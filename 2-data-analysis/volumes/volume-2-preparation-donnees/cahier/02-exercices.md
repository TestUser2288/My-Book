# Chapitre 2 : Transformation et fusion des données — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 2 du livre. Les **applications** sont de petites études guidées sur les données de la boutique : chacune annonce un objectif, avance par étapes courtes (au plus vingt-cinq lignes par bloc) et se termine par un « **À vous** » corrigé en fin de chapitre. Les **exercices** sont notés ⭐ (direct), ⭐⭐ (demande un peu de méthode), ⭐⭐⭐ (demande de combiner plusieurs sections). Les corrigés suivent : cherchez avant de les ouvrir. Les lectures de la caisse et du site, les jointures et le rapprochement du fichier clients **reposent sur le module `build/outils_ch02.py`**, qui regroupe les fonctions que le livre construit pas à pas : le cahier peut ainsi se concentrer sur les questions plutôt que sur la recopie du code de lecture.

Une seule cellule charge les bibliothèques et les tables de base (lignes de commande, commandes, produits). Les autres cellules en dépendent ; relancez-la si vous repartez de zéro.

```python
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch02 as O          # les fonctions de lecture du livre, regroupées (voir build/outils_ch02.py)
lig = pd.read_csv("donnees/lignes_commande.csv")
cmd = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
prod = pd.read_csv("donnees/produits.csv")
print(len(lig), "lignes |", len(cmd), "commandes |", len(prod), "produits")
```
<!--sortie-->
```text
83905 lignes | 36395 commandes | 120 produits
```

```python hide
NUM = O.NUM
```

## Applications

### Application 2.1 — La marge par canal et par trimestre (section 2.1)

**Objectif.** Calculer la marge brute hors taxe de chaque ligne, puis son taux par canal et par trimestre en 2025, en respectant la règle « un ratio d'agrégat est un rapport de sommes ».

**Étape 1 : relier les trois tables.** On joint les lignes aux produits (coût d'achat) et aux commandes (canal, date), en déclarant la cardinalité de chaque jointure.

```python
x = lig.merge(prod[["id_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
x = x.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande", validate="m:1")
x["ca_ht"] = x["montant"] / (1 + O.TVA)
x["marge_ht"] = x["ca_ht"] - x["quantite"] * x["cout_achat"]
x["annee"], x["trimestre"] = x["date_commande"].dt.year, x["date_commande"].dt.quarter
print(len(lig), "->", len(x), "lignes | TVA fictive :", O.TVA)
```
<!--sortie-->
```text
83905 -> 83905 lignes | TVA fictive : 0.2
```
<!--sortie-->

**Étape 2 : le tableau.** Taux de marge par canal (en lignes) et par trimestre (en colonnes), pour 2025.

```python
tab_marge = x[x["annee"] == 2025].groupby(["canal", "trimestre"]).agg(ca_ht=("ca_ht", "sum"), marge=("marge_ht", "sum"))
tab_marge["taux"] = tab_marge["marge"] / tab_marge["ca_ht"]
print(tab_marge["taux"].unstack("trimestre").round(3).to_string())
```
<!--sortie-->
```text
trimestre      1      2      3      4
canal                                
Boutique   0.370  0.384  0.382  0.381
Réseaux    0.369  0.389  0.378  0.383
Site       0.366  0.383  0.377  0.384
```
<!--sortie-->

**Étape 3 : le contrôle.** La somme des marges des groupes doit retrouver la marge totale de 2025.

```python
total_2025 = x.loc[x["annee"] == 2025, "marge_ht"].sum()
print("somme des groupes :", round(tab_marge["marge"].sum(), 2), "| marge totale :", round(total_2025, 2), "| égalité :", bool(np.isclose(tab_marge["marge"].sum(), total_2025)))
```
<!--sortie-->
```text
somme des groupes : 419016.93 | marge totale : 419016.93 | égalité : True
```
<!--sortie-->

> **À vous.** Quel couple (canal, trimestre) a le taux de marge le plus bas ? Calculez aussi, pour ce couple, la moyenne **des taux des lignes** : est-elle égale au taux de marge ? Pourquoi ? *(Piste en fin de chapitre.)*

### Application 2.2 — Délais, clients dormants et fuite d'information (sections 2.1.5 et 2.1.7)

**Objectif.** Mesurer le délai entre les commandes d'un client, ranger les clients dans des classes, puis constater qu'une variable qui regarde le futur **triche**.

**Étape 1 : un délai par commande.** On fabrique la table des paniers (une ligne par commande), on la trie par client et par date, et l'on décale d'une ligne **au sein de chaque client**.

```python
paniers = lig.groupby("id_commande", as_index=False)["montant"].sum().rename(columns={"montant": "panier"})
paniers = paniers.merge(cmd[["id_commande", "id_client", "date_commande"]], on="id_commande", validate="1:1")
paniers = paniers.sort_values(["id_client", "date_commande", "id_commande"]).reset_index(drop=True)
g = paniers.groupby("id_client")["date_commande"]
paniers["delai_jours"] = (paniers["date_commande"] - g.shift()).dt.days
print(paniers["delai_jours"].describe().round(1).to_string())
```
<!--sortie-->
```text
count    31589.0
mean        86.4
std        111.1
min          0.0
25%         17.0
50%         47.0
75%        110.0
max       1014.0
```
<!--sortie-->

**Étape 2 : des classes de clients.** Le délai **moyen** de chaque client, découpé avec des bornes que l'on écrit : moins de 30 jours, 30 à 90, 90 à 180, 180 et plus. Les clients à une seule commande n'ont **pas** de délai : ils restent à part.

```python
moyen = paniers.groupby("id_client")["delai_jours"].mean()
classes = pd.cut(moyen, [0, 30, 90, 180, np.inf], right=False, labels=["< 30 j", "30-90 j", "90-180 j", "180 j et +"])
print(classes.value_counts(dropna=False).sort_index().to_string())
print("clients sans délai (une seule commande) :", int(moyen.isna().sum()))
```
<!--sortie-->
```text
delai_jours
< 30 j         180
30-90 j       1404
90-180 j      1319
180 j et +    1070
NaN            833
clients sans délai (une seule commande) : 833
```
<!--sortie-->

**Étape 3 : la fuite.** Au 31 mars 2025, on veut prévoir qui commandera **encore en 2025**. Deux versions du nombre de commandes : avant la coupure, et au total.

```python
from sklearn.metrics import roc_auc_score
def auc_fuite(coupure):
    c = pd.Timestamp(coupure)
    avant = paniers[paniers["date_commande"] <= c].groupby("id_client").size().rename("avant")
    total = paniers.groupby("id_client").size().rename("total")
    futur = paniers[(paniers["date_commande"] > c) & (paniers["date_commande"].dt.year == 2025)].groupby("id_client").size().rename("futur")
    t = pd.concat([avant, total, futur], axis=1).dropna(subset=["avant"]).fillna(0)
    y = (t["futur"] > 0).astype(int)
    return round(roc_auc_score(y, t["avant"]), 3), round(roc_auc_score(y, t["total"]), 3), len(t)
print("coupure au 31 mars : AUC 'avant', AUC 'total', clients ->", auc_fuite("2025-03-31"))
```
<!--sortie-->
```text
coupure au 31 mars : AUC 'avant', AUC 'total', clients -> (0.787, 0.902, 4225)
```
<!--sortie-->

> **À vous.** Relancez `auc_fuite("2025-09-30")`. L'écart entre les deux AUC augmente-t-il ou diminue-t-il ? Pourquoi ? *(Piste en fin de chapitre.)*

### Application 2.3 — Contrôler une jointure (sections 2.2.2 et 2.2.5)

**Objectif.** Écrire la fonction de contrôle d'une jointure, l'appliquer à deux jointures dont l'une est **saine** et l'autre **n–n**, et réparer la seconde.

**Étape 1 : la fonction.**

```python
def controler(gauche, droite, cle, how="left"):
    r = gauche.merge(droite, on=cle, how=how, indicator=True)
    return {"avant": len(gauche), "après": len(r), "clé dupliquée à droite": int(droite.duplicated(cle).sum()),
            "sans correspondance": int((r["_merge"] == "left_only").sum())}
print("lignes x produits, sur l'identifiant :", controler(lig, prod[["id_produit", "cout_achat"]], "id_produit"))
```
<!--sortie-->
```text
lignes x produits, sur l'identifiant : {'avant': 83905, 'après': 83905, 'clé dupliquée à droite': 0, 'sans correspondance': 0}
```
<!--sortie-->

**Étape 2 : la jointure fautive.** Les lignes de la caisse, jointes aux produits sur le **nom** normalisé.

```python
caisse, ctrl = O.charger_caisse()
produits = O.charger_produits()
caisse["nom_norm"] = caisse["article"].map(O.norm_texte)
print("caisse x produits, sur le nom :", controler(caisse, produits[["nom_norm", "cout_achat"]], "nom_norm"))
```
<!--sortie-->
```text
caisse x produits, sur le nom : {'avant': 12678, 'après': 25356, 'clé dupliquée à droite': 60, 'sans correspondance': 0}
```
<!--sortie-->

**Étape 3 : la réparation.** On ajoute le prix de 2025 à la clé, avec une tolérance d'un demi-centime, et l'on compte les lignes uniques, ambiguës et sans candidat.

```python
c = caisse.reset_index().merge(produits[["nom_norm", "id_produit", "prix_2025"]], on="nom_norm")
c = c[(c["prix_unitaire"] - c["prix_2025"]).abs() < 0.011]
n = c.groupby("index").size()
print("uniques :", int((n == 1).sum()), "| ambiguës :", int((n > 1).sum()), "| sans candidat :", len(caisse) - len(n))
```
<!--sortie-->
```text
uniques : 12452 | ambiguës : 226 | sans candidat : 0
```
<!--sortie-->

> **À vous.** Pourquoi la clé `(nom, prix)` ne départage-t-elle pas toutes les lignes ? Que faut-il faire des lignes restantes ? *(Piste en fin de chapitre.)*

### Application 2.4 — Lire un fichier de janvier et un fichier de décembre (section 2.2.3)

**Objectif.** Constater la dérive de schéma entre deux fichiers de la caisse, les lire avec la même fonction et appliquer la somme de contrôle.

**Étape 1 : regarder les octets.** Le codage et la première ligne d'en-tête diffèrent.

```python
for f in ["caisse_2025-01.csv", "caisse_2025-12.csv"]:
    brut = open(os.path.join("donnees/caisse", f), "rb").read()
    entete = brut.decode("utf-8-sig" if brut.startswith(b"\xef\xbb\xbf") else "cp1252").splitlines()[3]
    print(f, "| BOM UTF-8 :", brut.startswith(b"\xef\xbb\xbf"), "| en-tête :", entete[:70])
```
<!--sortie-->
```text
caisse_2025-01.csv | BOM UTF-8 : False | en-tête : N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant
caisse_2025-12.csv | BOM UTF-8 : True | en-tête : Ticket,Date,Heure,Article,Catégorie,Qté,Prix unitaire,Remise (%),Monta
```
<!--sortie-->

**Étape 2 : lire les deux avec la même fonction.** `O.lire_caisse_fichier` détecte le codage, le séparateur, la décimale et le format de date.

```python
d1, t1 = O.lire_caisse_fichier("donnees/caisse/caisse_2025-01.csv")
d12, t12 = O.lire_caisse_fichier("donnees/caisse/caisse_2025-12.csv")
for nom, d, t in [("janvier", d1, t1), ("décembre", d12, t12)]:
    print(f"{nom:9s} lignes : {len(d):5d} | total affiché : {t:10.2f} | somme lue : {d['montant'].sum():10.2f} | vides : {int(d['montant'].isna().sum())}")
print("remise renseignée en janvier :", bool(d1["remise_pct"].notna().any()), "| en décembre :", bool(d12["remise_pct"].notna().any()))
```
<!--sortie-->
```text
janvier   lignes :   955 | total affiché :   38882.41 | somme lue :   37826.31 | vides : 36
décembre  lignes :  1694 | total affiché :   73384.87 | somme lue :   70924.34 | vides : 63
remise renseignée en janvier : False | en décembre : True
```
<!--sortie-->

**Étape 3 : reconstituer.** Quantité × prix × (1 − remise), la remise étant supposée nulle quand elle n'est pas écrite. Quel écart reste-t-il ?

```python
for nom, d, t in [("janvier", d1, t1), ("décembre", d12, t12)]:
    rec = d["montant"].fillna((d["quantite"] * d["prix_unitaire"] * (1 - d["remise_pct"].fillna(0) / 100)).round(2))
    print(nom, "écart au total affiché après reconstitution :", round(rec.sum() - t, 2))
```
<!--sortie-->
```text
janvier écart au total affiché après reconstitution : 351.63
décembre écart au total affiché après reconstitution : 303.48
```
<!--sortie-->

> **À vous.** Pourquoi l'écart de décembre est-il plus petit que celui de janvier, proportionnellement ? Qu'est-ce qui reste, dans chaque cas ? *(Piste en fin de chapitre.)*

### Application 2.5 — Nettoyer l'export du site (section 2.2.4)

**Objectif.** Appliquer les filtres du livre à l'export du site, comparer le chiffre d'affaires mensuel avec la base et expliquer l'écart.

**Étape 1 : lire et marquer.** `O.lire_site` ne supprime rien : il ajoute des colonnes qui disent si la ligne est un test, un doublon d'export, une commande annulée.

```python
site, lignes_site = O.lire_site()
print("lignes :", len(site), "| tests :", int(site["est_test"].sum()), "| doublons :", int(site["est_double"].sum()), "| annulées :", int((site["statut"] == "cancelled").sum()))
valides = site[~site["est_test"] & ~site["est_double"]]
print("commandes valides (annulées comprises) :", len(valides))
```
<!--sortie-->
```text
lignes : 6259 | tests : 60 | doublons : 121 | annulées : 186
commandes valides (annulées comprises) : 6078
```
<!--sortie-->

**Étape 2 : le chiffre d'affaires mensuel.** Avec et sans les commandes annulées.

```python
valides = valides.assign(mois=valides["date_heure"].dt.month)
ca_avec = valides.groupby("mois")["total_num"].sum()
ca_sans = valides[valides["statut"] != "cancelled"].groupby("mois")["total_num"].sum()
print(pd.DataFrame({"avec annulées": ca_avec, "sans annulées": ca_sans}).round(0).T.to_string())
```
<!--sortie-->
```text
mois                1        2        3        4        5        6        7        8        9        10       11       12
avec annulées  41358.0  34084.0  42308.0  43392.0  48614.0  50044.0  53634.0  37311.0  55538.0  56535.0  64851.0  90048.0
sans annulées  40221.0  32746.0  40821.0  41828.0  47471.0  48555.0  52340.0  36278.0  54524.0  55000.0  62884.0  87496.0
```
<!--sortie-->

**Étape 3 : la comparaison avec la base.**

```python
mt = lig.groupby("id_commande")["montant"].sum()
b = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"].dt.year == 2025)].assign(ca=lambda d: d["id_commande"].map(mt))
base_mois = b.groupby(b["date_commande"].dt.month)["ca"].sum()
print("écart max entre la base et « avec annulées » :", round((base_mois - ca_avec).abs().max(), 2), "| écart max avec « sans annulées » :", round((base_mois - ca_sans).abs().max(), 2))
```
<!--sortie-->
```text
écart max entre la base et « avec annulées » : 0.0 | écart max avec « sans annulées » : 2552.4
```
<!--sortie-->

> **À vous.** Que valent exactement, chaque mois, les écarts entre la base et « sans annulées » ? À quoi correspondent-ils ? *(Piste en fin de chapitre.)*

### Application 2.6 — La table des ventes et son contrôle (sections 2.2.6 à 2.2.8)

**Objectif.** Construire la table des ventes (caisse et site) avec `O.ventes_2025`, la contrôler mois par mois contre la base et chercher ce qui manque.

**Étape 1 : la table.**

```python
ventes, ctrl_caisse = O.ventes_2025()
ventes["mois"] = ventes["date"].dt.month
print(len(ventes), "lignes |", ventes.groupby("canal")["montant"].sum().round(2).to_dict())
```
<!--sortie-->
```text
26188 lignes | {'Boutique': 564472.59, 'Site': 600164.13}
```
<!--sortie-->

**Étape 2 : le contrôle par canal et par mois.**

```python
v25 = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande", validate="m:1")
v25 = v25[v25["date_commande"].dt.year == 2025].assign(mois=lambda d: d["date_commande"].dt.month)
comp = pd.DataFrame({"table": ventes.groupby(["canal", "mois"])["montant"].sum(), "base": v25.groupby(["canal", "mois"])["montant"].sum()}).dropna()
comp["ecart_pct"] = (comp["table"] / comp["base"] - 1) * 100
print(comp["ecart_pct"].unstack("canal").round(2).to_string())
```
<!--sortie-->
```text
canal  Boutique  Site
mois                 
1          0.90 -2.75
2          0.00 -3.93
3          0.37 -3.51
4          1.48 -3.60
5          0.95 -2.35
6          0.67 -2.98
7          0.47 -2.41
8          1.05 -2.77
9          0.72 -1.83
10         0.16 -2.72
11         0.40 -3.03
12         0.41 -2.83
```
<!--sortie-->

**Étape 3 : anti-jointures dans les deux sens.**

```python
base_bs = set(v25.loc[v25["canal"].isin(["Boutique", "Site"]), "id_commande"])
ids = set(ventes["id_commande"])
print("commandes de la base absentes de la table :", len(base_bs - ids), "| de la table absentes de la base :", len(ids - base_bs))
```
<!--sortie-->
```text
commandes de la base absentes de la table : 181 | de la table absentes de la base : 0
```
<!--sortie-->

> **À vous.** Quels mois ont l'écart le plus grand pour chaque canal, et pourquoi ? Que sont les commandes de la base absentes de la table ? Pourquoi, pour la Boutique, aucune commande ne manque-t-elle alors que les totaux diffèrent ? *(Piste en fin de chapitre.)*

### Application 2.7 — Agréger et contrôler (section 2.3)

**Objectif.** Passer de la ligne à la commande, calculer des parts avec `transform`, puis voir quels contrôles détectent une erreur.

**Étape 1 : la table des commandes.**

```python
cmd_v = ventes.groupby(["canal", "id_commande"], as_index=False).agg(ca=("montant", "sum"), lignes=("montant", "size"), mois=("mois", "first"))
print(len(ventes), "lignes ->", len(cmd_v), "commandes | CA :", round(ventes["montant"].sum(), 2), "=", round(cmd_v["ca"].sum(), 2))
print("panier moyen par canal :", cmd_v.groupby("canal")["ca"].mean().round(2).to_dict())
```
<!--sortie-->
```text
26188 lignes -> 11339 commandes | CA : 1164636.72 = 1164636.72
panier moyen par canal : {'Boutique': 103.73, 'Site': 101.77}
```
<!--sortie-->

**Étape 2 : la part de chaque catégorie dans son mois.**

```python
cat_mois = ventes.groupby(["mois", "categorie"], as_index=False)["montant"].sum()
cat_mois["part"] = cat_mois["montant"] / cat_mois.groupby("mois")["montant"].transform("sum")
print(cat_mois[cat_mois["mois"] == 12].sort_values("part", ascending=False).round(3).head(3).to_string(index=False))
print("somme des parts par mois (min, max) :", round(cat_mois.groupby("mois")["part"].sum().min(), 6), round(cat_mois.groupby("mois")["part"].sum().max(), 6))
```
<!--sortie-->
```text
 mois  categorie  montant  part
   12 Décoration 52982.84 0.329
   12     Maison 39492.40 0.245
   12    Cuisine 29751.27 0.185
somme des parts par mois (min, max) : 1.0 1.0
```
<!--sortie-->

**Étape 3 : quel contrôle voit quoi ?** On fabrique deux erreurs : 100 lignes dupliquées, et 100 montants multipliés par dix.

```python
total_ref = ventes["montant"].sum()
fautes = {"100 lignes dupliquées": pd.concat([ventes, ventes.head(100)]), "100 montants x10": ventes.assign(montant=np.where(ventes.index < 100, ventes["montant"] * 10, ventes["montant"]))}
for nom, t in fautes.items():
    interne = np.isclose(t.groupby("canal")["montant"].sum().sum(), t.groupby("mois")["montant"].sum().sum())
    print(f"{nom:24s} | contrôle interne (canal = mois) : {bool(interne)} | contrôle externe (= total de référence) : {bool(np.isclose(t['montant'].sum(), total_ref))}")
```
<!--sortie-->
```text
100 lignes dupliquées    | contrôle interne (canal = mois) : True | contrôle externe (= total de référence) : False
100 montants x10         | contrôle interne (canal = mois) : True | contrôle externe (= total de référence) : False
```
<!--sortie-->

> **À vous.** Quel type d'erreur le contrôle **externe** voit-il, et pas l'interne ? Que ferait-il falloir pour détecter une erreur qui laisse le total inchangé (deux lignes échangées) ? *(Piste en fin de chapitre.)*

### Application 2.8 — Le tableur de stocks (section 2.4)

**Objectif.** Lire le tableur désordonné, le passer au format long, compter les ruptures par catégorie et vérifier un aller-retour large → long → large.

**Étape 1 : lire et filtrer.**

```python
import openpyxl
ws = openpyxl.load_workbook("donnees/stocks_tableur.xlsx")["Stock 2025"]
brut = pd.DataFrame(list(ws.iter_rows(min_row=5, values_only=True))).iloc[:, :14]
brut.columns = ["ref", "designation"] + list(range(1, 13))
est_produit = brut["ref"].astype(str).str.fullmatch(r"P\d{3}")
print(len(brut), "lignes lues |", int(est_produit.sum()), "lignes de produits")
```
<!--sortie-->
```text
137 lignes lues | 120 lignes de produits
```
<!--sortie-->

**Étape 2 : convertir et dépivoter.** « rupture » vaut 0, « ND » et « — » sont des inconnus.

```python
def vers_nombre(v):
    if isinstance(v, (int, float)): return v
    s = str(v).strip()
    return 0 if s == "rupture" else (int(s) if s.isdigit() else np.nan)
stock_large = brut[est_produit].copy()
stock_large[list(range(1, 13))] = stock_large[list(range(1, 13))].apply(lambda col: col.map(vers_nombre))
stock = stock_large.melt(id_vars=["ref", "designation"], var_name="mois", value_name="stock")
stock["id_produit"] = stock["ref"].str[1:].astype(int)
stock = stock.merge(prod[["id_produit", "categorie"]], on="id_produit", validate="m:1")
print(len(stock), "lignes |", int(stock["stock"].isna().sum()), "inconnus |", int((stock["stock"] == 0).sum()), "ruptures")
```
<!--sortie-->
```text
1440 lignes | 71 inconnus | 120 ruptures
```
<!--sortie-->

**Étape 3 : analyse et aller-retour.**

```python
rupt = stock.assign(rupture=stock["stock"] == 0).pivot_table(index="categorie", columns="mois", values="rupture", aggfunc="sum")
print("ruptures par catégorie sur l'année :", rupt.sum(axis=1).astype(int).to_dict())
large2 = stock.pivot(index="id_produit", columns="mois", values="stock")
ref = stock_large.assign(id_produit=stock_large["ref"].str[1:].astype(int)).set_index("id_produit")[list(range(1, 13))].astype(float)
print("aller-retour identique :", bool(large2.astype(float).equals(ref.astype(float))))
```
<!--sortie-->
```text
ruptures par catégorie sur l'année : {'Bien-être': 13, 'Cuisine': 25, 'Décoration': 27, 'Jardin': 24, 'Maison': 22, 'Papeterie': 9}
aller-retour identique : True
```
<!--sortie-->

> **À vous.** Quelle catégorie compte le plus de ruptures, et quelle part de ses cellules cela représente-t-il ? Que se passerait-il sur la moyenne du stock si l'on remplaçait « ND » et « — » par zéro ? *(Piste en fin de chapitre.)*

### Application 2.9 — Dédoublonner le CRM sans téléphone (section 2.5)

**Objectif.** Comparer trois clés de blocage, puis régler les seuils d'un score de ressemblance et mesurer précision et rappel.

**Étape 1 : charger le CRM normalisé et les paires vraies.**

```python
crm, vraies = O.charger_crm()
print(len(crm), "lignes |", len(vraies), "paires vraies |", crm["ville_norm"].nunique(), "villes normalisées")
```
<!--sortie-->
```text
7000 lignes | 1050 paires vraies | 20 villes normalisées
```
<!--sortie-->

**Étape 2 : trois blocages.** Le rappel du blocage borne celui de tout ce qui suit.

```python
crm["debut_nom"] = crm["nom_tri"].str[:3]
for cles in (["ville_norm"], ["ville_norm", "annee_naiss"], ["annee_naiss", "debut_nom"]):
    b = O.paires(crm, cles, taille_max=10_000)       # on accepte aussi les gros groupes, pour voir le vrai nombre de paires
    print(f"{' + '.join(cles):26s}", O.juger(b, vraies))
```
<!--sortie-->
```text
ville_norm                 {'paires': 1979607, 'précision': 0.001, 'rappel': 1.0}
ville_norm + annee_naiss   {'paires': 42538, 'précision': 0.024, 'rappel': 0.984}
annee_naiss + debut_nom    {'paires': 10690, 'précision': 0.085, 'rappel': 0.864}
```
<!--sortie-->

**Étape 3 : le score sur le blocage retenu, et trois seuils.**

```python
bloc = O.paires(crm, ["ville_norm", "annee_naiss"])
S = O.scorer_paires(crm, bloc, vraies)
for seuil in (70, 80, 90):
    sel = S["score"] >= seuil
    print(f"seuil {seuil} | paires : {int(sel.sum()):5d} | précision : {S.loc[sel, 'vrai'].mean():.3f} | rappel : {S.loc[sel, 'vrai'].sum() / len(vraies):.3f}")
```
<!--sortie-->
```text
seuil 70 | paires :  1111 | précision : 0.924 | rappel : 0.978
seuil 80 | paires :  1003 | précision : 0.991 | rappel : 0.947
seuil 90 | paires :   921 | précision : 0.999 | rappel : 0.876
```
<!--sortie-->

> **À vous.** Quel blocage a le meilleur compromis entre nombre de paires et rappel ? Pourquoi la clé « début du nom » est-elle fragile ici ? *(Piste en fin de chapitre.)*

### Application 2.10 — Rapprocher le catalogue du fournisseur (section 2.5.7)

**Objectif.** Voir l'effet de la tolérance de prix sur le rapprochement du catalogue.

**Étape 1 : le rapprochement de référence.** `O.rapprocher_catalogue` reprend la méthode du livre (nom ressemblant, pénalisé par l'écart de prix).

```python
R = O.rapprocher_catalogue()
vp = pd.read_csv("donnees/verite_produits.csv").rename(columns={"id_produit": "id_vrai"})
J = R.merge(vp, on="code_fournisseur", validate="1:1")
print("lignes :", len(J), "| acceptées :", int(J["accepte"].sum()), "| nouveautés (sans équivalent) :", int((J["id_vrai"] == -1).sum()))
```
<!--sortie-->
```text
lignes : 118 | acceptées : 108 | nouveautés (sans équivalent) : 10
```
<!--sortie-->

**Étape 2 : varier la tolérance de prix.**

```python
for tol in (0.01, 0.035, 0.10, 0.50):
    A = O.rapprocher_catalogue(seuil_prix=tol).merge(vp, on="code_fournisseur")
    acc = A[A["accepte"]]
    print(f"tolérance {tol:.3f} | acceptées : {len(acc):3d} | nouveautés acceptées à tort : {int((acc['id_vrai'] == -1).sum())} | bons produits manqués : {int((~A['accepte'] & (A['id_vrai'] != -1)).sum())}")
```
<!--sortie-->
```text
tolérance 0.010 | acceptées :  34 | nouveautés acceptées à tort : 0 | bons produits manqués : 74
tolérance 0.035 | acceptées : 108 | nouveautés acceptées à tort : 0 | bons produits manqués : 0
tolérance 0.100 | acceptées : 108 | nouveautés acceptées à tort : 0 | bons produits manqués : 0
tolérance 0.500 | acceptées : 108 | nouveautés acceptées à tort : 0 | bons produits manqués : 0
```
<!--sortie-->

> **À vous.** Quelle tolérance choisiriez-vous pour la boutique, et à quelle condition accepterait-on une tolérance plus large ? *(Piste en fin de chapitre.)*

## Exercices

### Exercice 2.1 ⭐ — La marge à la main (section 2.1.2)

Trois lignes de vente toutes taxes comprises, TVA à 20 % : (1) 59,90 € pour 2 articles, coût d'achat unitaire 18,40 € ; (2) 24,00 € pour 1 article, coût 14,50 € ; (3) 120,00 € pour 4 articles avec 20 % de remise **déjà déduits** du montant, coût unitaire 18,00 €. Calculez à la main la marge hors taxe de chaque ligne et son taux, puis le taux de marge **global** des trois lignes. Est-ce la moyenne des trois taux ?

### Exercice 2.2 ⭐ — Les semaines ISO (section 2.1.3)

Donnez l'année ISO et la semaine ISO des dates suivantes : 30 décembre 2024, 1er janvier 2025, 29 décembre 2025, 1er janvier 2026. Vérifiez avec pandas.

### Exercice 2.3 ⭐⭐ — Les bornes d'une classe (section 2.1.4)

Avec `pd.cut(paniers, [0, 50, 100, 200, np.inf], right=False)`, dans quelle classe tombent des paniers de 50,00 €, 99,99 €, 100,00 € et 200,00 € ? Même question avec `right=True`. Combien de commandes de la base ont un panier **exactement** égal à une borne ?

### Exercice 2.4 ⭐⭐ — Zéro ou vide ? (section 2.1.7)

Calculez, pour chacun des 6 000 clients, la **part de ses commandes de 2025 passées un week-end**. Que valent cette part et son dénominateur pour un client sans commande en 2025 ? Donnez la moyenne de la part en laissant les vides, puis en les remplaçant par zéro : laquelle répond à « *quelle part des commandes se passe le week-end ?* » ?

### Exercice 2.5 ⭐ — Le type de jointure (section 2.2.1)

Soient `a` (produits 1, 2, 3, 5) et `b` (stocks pour les produits 2, 3, 4, 5, 6). Prévoyez, **sans exécuter**, le nombre de lignes et la liste des produits pour une jointure `inner`, `left`, `right` et `outer` sur l'identifiant. Vérifiez.

### Exercice 2.6 ⭐⭐ — Prévoir le nombre de lignes (section 2.2.2)

Sans l'exécuter, prévoyez le nombre de lignes de : (a) `lig` joint à `cmd` sur `id_commande` ; (b) la table `ventes` de l'application 2.6 jointe à `prod` sur `nom_produit` (rappel : chaque nom est porté par deux produits) ; (c) `cmd` joint à `clients` sur `id_client`. Vérifiez avec `validate=`.

### Exercice 2.7 ⭐⭐ — Le mojibake et le codage (section 2.2.3)

Le texte « Théière » encodé en UTF-8 puis lu à tort en `cp1252` donne « ThÃ©iÃ¨re ». Écrivez les deux lignes de Python qui fabriquent ce texte abîmé, puis celles qui le réparent. Pourquoi la réparation inverse ne marche-t-elle pas toujours ?

### Exercice 2.8 ⭐⭐⭐ — Chercher une rupture d'unité (section 2.2.4)

Dans l'export du site, trouvez le **premier jour** où le montant brut change d'ordre de grandeur, en comparant la médiane des montants **par jour**, pour les commandes qui ne sont pas des tests. Montrez que la rupture coïncide exactement avec l'apparition du `Z` dans la date, puis expliquez pourquoi cette coïncidence ne **prouve** pas que la plateforme exporte en centimes.

### Exercice 2.9 ⭐ — Le panier moyen par canal (section 2.3.2)

Calculez le panier moyen de chaque canal en 2025 (base) de deux façons : (a) chiffre d'affaires divisé par le nombre de commandes ; (b) moyenne des montants de **lignes**. Pourquoi (b) est-elle fausse comme panier moyen ?

### Exercice 2.10 ⭐⭐ — La moyenne mobile (section 2.3.6)

Calculez la moyenne mobile sur sept jours du chiffre d'affaires quotidien de la table des ventes (a) avec `min_periods=7`, (b) avec `min_periods=1`, (c) **centrée** (`center=True`). Combien de valeurs vides pour chacune ? Laquelle utiliseriez-vous pour décrire le niveau du 15 juin, et laquelle pour prévoir le 16 ?

### Exercice 2.11 ⭐⭐ — L'aller-retour pivot (section 2.4.1)

À partir de la table des ventes, fabriquez le tableau « chiffre d'affaires par catégorie (lignes) et par mois (colonnes) » avec `pivot_table`, repassez-le au format long avec `melt`, puis rebâtissez-le avec `pivot`. Vérifiez l'égalité des deux tableaux larges et celle des totaux. Que se passe-t-il si vous utilisez `pivot` directement sur la table des ventes ?

### Exercice 2.12 ⭐⭐ — Inconnu n'est pas zéro (section 2.4.2)

Dans le tableur de stocks, comptez les cellules « ND » et « — ». Calculez le stock moyen d'octobre (a) en ignorant les inconnus, (b) en les remplaçant par zéro. De combien la seconde moyenne sous-estime-t-elle la première ? Le raisonnement change-t-il pour « rupture » ?

### Exercice 2.13 ⭐⭐ — Levenshtein à la main (section 2.5.3)

Calculez à la main la distance de Levenshtein entre `bougie` et `bougeoir`, en remplissant la table. Vérifiez avec `rapidfuzz`. Calculez ensuite la similarité (100 × (1 − distance / longueur maximale)) et comparez-la au `token_set_ratio` de « bougie nordique » et « nordique bougie ».

### Exercice 2.14 ⭐⭐⭐ — Choisir un seuil par les coûts (section 2.5.6)

Dans l'application 2.9, une **fusion erronée** coûte 5 unités et un **doublon raté** 1 unité. Pour chaque seuil de 50 à 100 (de un en un), calculez le coût total (faux positifs et faux négatifs, ces derniers comptés par rapport à **toutes** les paires vraies, blocage compris). Quel seuil minimise le coût ? Comparez avec le seuil obtenu pour un coût de 1 pour 1, et expliquez la différence.

## Pistes pour les « À vous » des applications

### Piste de l'application 2.1

```python
ct = tab_marge["taux"].dropna()
pire = ct.idxmin()
sel = x[(x["annee"] == 2025) & (x["canal"] == pire[0]) & (x["trimestre"] == pire[1])]
print("taux le plus bas :", (pire[0], int(pire[1])), round(ct.min(), 4), "| moyenne des taux des lignes de ce couple :", round((sel["marge_ht"] / sel["ca_ht"]).mean(), 4))
```
<!--sortie-->
```text
taux le plus bas : ('Site', 1) 0.3656 | moyenne des taux des lignes de ce couple : 0.3623
```
<!--sortie-->

```python hide
NUM("pire_taux", ct.min() * 100); NUM("pire_moy", (sel["marge_ht"] / sel["ca_ht"]).mean() * 100); NUM("pire_trim", pire[1]); NUM("pire_canal", pire[0])
```
<!--sortie-->
```text
NUM pire_taux 36.56356616106222
NUM pire_moy 36.233453706656434
NUM pire_trim 1
NUM pire_canal Site
```

Le couple (**Site**, trimestre 1) a le taux le plus bas, 36,6 % ; la moyenne des taux de ses lignes est de 36,2 %. Les deux ne sont pas égales : la moyenne donne le même poids à une ligne de 5 € et à une ligne de 150 €, alors que le **rapport des sommes** pèse chaque ligne par son chiffre d'affaires. On prend toujours le rapport des sommes pour un ratio d'agrégat.

### Piste de l'application 2.2

```python
for coupure in ("2025-03-31", "2025-09-30"):
    a_, t_, n_cl = auc_fuite(coupure)
    print(coupure, "| AUC honnête :", a_, "| AUC avec fuite :", t_, "| écart :", round(t_ - a_, 3), "| clients :", n_cl)
```
<!--sortie-->
```text
2025-03-31 | AUC honnête : 0.787 | AUC avec fuite : 0.902 | écart : 0.115 | clients : 4225
2025-09-30 | AUC honnête : 0.756 | AUC avec fuite : 0.833 | écart : 0.077 | clients : 4573
```
<!--sortie-->

```python hide
a1, t1_, _ = auc_fuite("2025-03-31"); a2, t2_, _ = auc_fuite("2025-09-30")
NUM("ecart_mars", t1_ - a1); NUM("ecart_sept", t2_ - a2); NUM("auc_h_mars", a1); NUM("auc_h_sept", a2)
```
<!--sortie-->
```text
NUM ecart_mars 0.11499999999999999
NUM ecart_sept 0.07699999999999996
NUM auc_h_mars 0.787
NUM auc_h_sept 0.756
```

L'écart entre les deux AUC passe de 0,115 (coupure de mars) à 0,077 (coupure de septembre), et l'AUC « honnête » de 0,787 à 0,756. La variable qui regarde le futur **paraît** toujours meilleure que la variable honnête ; ce que l'on peut dire de l'évolution des écarts vient des chiffres, pas d'une règle générale, et la bonne conclusion ne change pas : **un prédicteur se calcule avec les seules données antérieures à la date de prévision**.

### Piste de l'application 2.3

```python
amb = c[c["index"].isin(n[n > 1].index)]
print("noms concernés :", sorted(amb["nom_norm"].unique()), "| produits candidats :", sorted(amb["id_produit"].astype(int).unique().tolist()), "| prix de 2025 :", sorted(amb["prix_2025"].unique().tolist()))
```
<!--sortie-->
```text
noms concernés : ['carnet mat'] | produits candidats : [62, 72] | prix de 2025 : [2.99]
```
<!--sortie-->

```python hide
NUM("n_amb_c", (n > 1).sum()); NUM("n_noms_amb", amb["nom_norm"].nunique())
```
<!--sortie-->
```text
NUM n_amb_c 226
NUM n_noms_amb 1
```

La clé `(nom, prix)` laisse **226 lignes** ambiguës, qui concernent 1 nom de produit : **deux produits distincts ont le même nom et le même prix** (et le même coût d'achat). Aucune information de la ligne de caisse ne les distingue. On laisse leur `id_produit` **vide**, on garde le coût d'achat (identique) pour la marge, et l'on **écrit** l'ambiguïté dans la note de méthode.

### Piste de l'application 2.4

```python
resume = {}
for nom, d, t_ in [("janvier", d1, t1), ("décembre", d12, t12)]:
    rec = d["montant"].fillna((d["quantite"] * d["prix_unitaire"] * (1 - d["remise_pct"].fillna(0) / 100)).round(2))
    ident = d.duplicated(["ticket", "date", "heure", "article", "categorie", "quantite", "prix_unitaire", "montant"])
    resume[nom] = (rec.sum() - t_, rec[ident].sum())
    print(nom, "| écart restant :", round(rec.sum() - t_, 2), "€ (", round((rec.sum() - t_) / t_ * 100, 2), "%) | montant des lignes identiques :", round(rec[ident].sum(), 2), "€ | nombre :", int(ident.sum()))
```
<!--sortie-->
```text
janvier | écart restant : 351.63 € ( 0.9 %) | montant des lignes identiques : 377.4 € | nombre : 8
décembre | écart restant : 303.48 € ( 0.41 %) | montant des lignes identiques : 775.88 € | nombre : 20
```
<!--sortie-->

```python hide
NUM("ecart_jan", resume["janvier"][0]); NUM("ident_jan", resume["janvier"][1]); NUM("ecart_dec", resume["décembre"][0]); NUM("ident_dec", resume["décembre"][1])
```
<!--sortie-->
```text
NUM ecart_jan 351.6299999999901
NUM ident_jan 377.4
NUM ecart_dec 303.4800000000105
NUM ident_dec 775.8800000000001
```

En décembre, la remise est **écrite** dans le fichier : la reconstitution des montants vides est exacte, et l'écart restant (303,48 €) ne peut venir que des lignes en trop. Il est **inférieur** au montant de toutes les lignes identiques (775,88 €) : certaines de ces lignes sont des répétitions **légitimes** (section 2.2.3), seules les autres sont de vrais doubles scans. En janvier, la remise n'est pas écrite : la reconstitution suppose une remise nulle (faux pour les lignes remisées pendant les soldes), et l'écart (351,63 €) combine cette hypothèse **et** les lignes en trop. Les deux fichiers portent le même nom de colonne « Montant » mais n'ont pas **la même qualité d'information**.

### Piste de l'application 2.5

```python
ecarts = (base_mois - ca_sans).round(2)
annul = valides[valides["statut"] == "cancelled"].groupby("mois")["total_num"].sum().round(2)
print(pd.DataFrame({"base - sans annulées": ecarts, "annulées du mois": annul}).T.to_string())
```
<!--sortie-->
```text
                           1        2        3       4        5        6        7        8        9        10       11      12
base - sans annulées  1136.98  1338.09  1486.97  1563.7  1142.18  1489.61  1293.75  1032.57  1013.75  1535.08  1966.24  2552.4
annulées du mois      1136.98  1338.09  1486.97  1563.7  1142.18  1489.61  1293.75  1032.57  1013.75  1535.08  1966.24  2552.4
```
<!--sortie-->

```python hide
assert np.allclose(ecarts.values, annul.reindex(ecarts.index).fillna(0).values)
```

L'écart mensuel entre la base et « sans annulées » est **exactement** le montant des commandes annulées du mois : la base enregistre les commandes annulées parmi les ventes, alors que l'export du site, avec son statut, permet de les écarter. L'écart avec « avec annulées » est **nul** (étape 3). Une réconciliation réussie se reconnaît à ceci : chaque écart restant est **expliqué** par une cause identifiée et chiffrée.

### Piste de l'application 2.6

```python
ecart_mois = comp["ecart_pct"].unstack("canal")
print("mois d'écart absolu maximal :", ecart_mois.abs().idxmax().to_dict(), "| écart :", ecart_mois.abs().max().round(2).to_dict())
print("mois d'écart absolu minimal :", ecart_mois.abs().idxmin().to_dict(), "| écart :", ecart_mois.abs().min().round(2).to_dict())
site_, _ = O.lire_site()
annulees = set(site_.loc[site_["statut"] == "cancelled", "id_commande"].dropna().astype(int))
print("commandes de la base absentes de la table = commandes annulées du site :", (base_bs - ids) == annulees)
```
<!--sortie-->
```text
mois d'écart absolu maximal : {'Boutique': 4, 'Site': 2} | écart : {'Boutique': 1.48, 'Site': 3.93}
mois d'écart absolu minimal : {'Boutique': 2, 'Site': 9} | écart : {'Boutique': 0.0, 'Site': 1.83}
commandes de la base absentes de la table = commandes annulées du site : True
```
<!--sortie-->

Pour le **Site**, l'écart de chaque mois est le montant des commandes annulées (la base les compte, la table des ventes les écarte) : l'anti-jointure le confirme, car les 181 commandes de la base absentes de la table sont **exactement** les commandes annulées du site. Pour la **Boutique**, l'écart vient des lignes identiques conservées et de la reconstitution des montants vides ; aucune commande ne manque ni n'est inventée, et pourtant le total diffère : les **identifiants** concordent, les **montants** non. Il faut donc **les deux** contrôles.

### Piste de l'application 2.7

La duplication de lignes et la multiplication de montants changent toutes deux le total par rapport à la référence, que seul le contrôle **externe** voit ; le contrôle **interne** (somme par canal égale à somme par mois) reste vrai dans les deux cas, puisque la table fautive est cohérente avec elle-même. Une erreur qui **laisse le total inchangé** (deux montants échangés entre deux lignes) n'est détectée ni par l'un ni par l'autre : il faut un contrôle **plus fin**, au niveau d'un sous-total (par catégorie, par jour) comparé à une référence indépendante, ou une vérification de **plausibilité** ligne à ligne.

```python
attendu = ventes["quantite"] * ventes["prix_unitaire"] * (1 - ventes["remise_pct"].fillna(0) / 100)
ecart_ligne = (ventes["montant"] - attendu).abs()
print("lignes où montant ≠ quantité × prix × (1 − remise) :", int((ecart_ligne > 0.011).sum()), "sur", len(ventes), "| dont lignes de la caisse :", int(((ecart_ligne > 0.011) & (ventes["source"] == "caisse")).sum()))
```
<!--sortie-->
```text
lignes où montant ≠ quantité × prix × (1 − remise) : 1302 sur 26188 | dont lignes de la caisse : 1302
```
<!--sortie-->

```python hide
NUM("n_incoh", (ecart_ligne > 0.011).sum()); NUM("n_ventes_c", len(ventes)); NUM("n_incoh_caisse", ((ecart_ligne > 0.011) & (ventes["source"] == "caisse")).sum())
```
<!--sortie-->
```text
NUM n_incoh 1302
NUM n_ventes_c 26188
NUM n_incoh_caisse 1302
```

Ce test de plausibilité signale 1 302 lignes sur 26 188, dont 1 302 de la caisse : ce sont celles dont le montant lu inclut une remise que le calcul ignore (la remise n'est écrite que de façon partielle). Un contrôle qui signale quelque chose n'est utile que si l'on **sait expliquer** ce qu'il signale.

### Piste de l'application 2.8

```python
cat_rupt = stock.assign(rupture=stock["stock"] == 0).groupby("categorie")["rupture"].agg(["sum", "mean"]).round(3)
print(cat_rupt.sort_values("sum", ascending=False).head(3).to_string())
m_ignore = stock.loc[stock["mois"] == 10, "stock"].mean()
m_zero = stock.loc[stock["mois"] == 10, "stock"].fillna(0).mean()
print("stock moyen d'octobre : inconnus ignorés", round(m_ignore, 2), "| inconnus à zéro", round(m_zero, 2))
```
<!--sortie-->
```text
            sum   mean
categorie             
Décoration   27  0.112
Cuisine      25  0.104
Jardin       24  0.100
stock moyen d'octobre : inconnus ignorés 47.59 | inconnus à zéro 44.82
```
<!--sortie-->

```python hide
NUM("sous_est", (m_ignore - m_zero) / m_ignore * 100); NUM("n_inconnus_oct", stock.loc[stock["mois"] == 10, "stock"].isna().sum())
```
<!--sortie-->
```text
NUM sous_est 5.833333333333326
NUM n_inconnus_oct 7
```

Remplacer les inconnus par zéro **sous-estime** le stock moyen d'octobre de 5,8 % (il y a 7 inconnus ce mois-là) : on traite comme « vide » ce que l'on ne sait pas. Pour « rupture », au contraire, le zéro est la **vraie** valeur : le stock est nul, ce qui est une information.

### Piste de l'application 2.9

```python
for cles in (["ville_norm"], ["ville_norm", "annee_naiss"], ["annee_naiss", "debut_nom"]):
    r = O.juger(O.paires(crm, cles, taille_max=10_000), vraies)
    print(f"{' + '.join(cles):26s} | paires {r['paires']:>9,d} | rappel {r['rappel']}".replace(",", " "))
```
<!--sortie-->
```text
ville_norm                 | paires 1 979 607 | rappel 1.0
ville_norm + annee_naiss   | paires    42 538 | rappel 0.984
annee_naiss + debut_nom    | paires    10 690 | rappel 0.864
```
<!--sortie-->

Le meilleur compromis entre nombre de paires et rappel est donné par les chiffres ci-dessus : la **ville seule** compare beaucoup plus de paires ; la clé `année + début du nom` compare peu de paires mais son rappel est le plus faible, parce que le **début du nom** est justement ce que les fautes de frappe, les initiales et les inversions abîment. Une clé de blocage doit être **fiable** (peu abîmée) et **grossière** (assez large pour ne pas séparer les vrais doublons).

### Piste de l'application 2.10

```python
for tol in (0.01, 0.035, 0.10, 0.50):
    A = O.rapprocher_catalogue(seuil_prix=tol).merge(vp, on="code_fournisseur")
    acc = A[A["accepte"]]
    print(f"{tol:.3f} acceptées {len(acc):3d} | à tort {int((acc['id_vrai'] == -1).sum())} | manquées {int((~A['accepte'] & (A['id_vrai'] != -1)).sum())}")
```
<!--sortie-->
```text
0.010 acceptées  34 | à tort 0 | manquées 74
0.035 acceptées 108 | à tort 0 | manquées 0
0.100 acceptées 108 | à tort 0 | manquées 0
0.500 acceptées 108 | à tort 0 | manquées 0
```
<!--sortie-->

La tolérance de **1 %** manque des produits légitimes (le catalogue a ±3 % d'écart sur les coûts) ; à 3,5 % tous les bons produits sont acceptés et toutes les nouveautés rejetées. Au-delà, la tolérance devient inutile ici, car les nouveautés se rejettent déjà par leur **nom** (similarité trop basse). On n'élargirait la tolérance que si l'on **savait** les écarts de prix plus grands (variation de tarif), en gardant un seuil de nom exigeant : la tolérance doit refléter ce que l'on sait du **fournisseur**, pas être choisie sur les résultats.

## Corrigés des exercices

### Corrigé 2.1

Ligne 1 : 59,90 / 1,20 = 49,92 € hors taxe ; coût 2 × 18,40 = 36,80 € ; marge 13,12 € ; taux 26,3 %. Ligne 2 : 24,00 / 1,20 = 20,00 € ; coût 14,50 € ; marge 5,50 € ; taux 27,5 %. Ligne 3 : 120,00 / 1,20 = 100,00 € ; coût 4 × 18,00 = 72,00 € ; marge 28,00 € ; taux 28,0 % (la remise de 20 % est **déjà** dans le montant : on ne la retire pas une seconde fois). Global : marge 46,62 € sur 169,92 € de chiffre d'affaires hors taxe, soit 27,4 % ; la moyenne des trois taux vaut 27,3 %, légèrement différente, parce que les trois lignes n'ont pas le même poids.

```python
l3 = pd.DataFrame({"ttc": [59.90, 24.00, 120.00], "cout": [2 * 18.40, 14.50, 4 * 18.00]})
l3["ht"] = l3["ttc"] / 1.2; l3["marge"] = l3["ht"] - l3["cout"]; l3["taux"] = l3["marge"] / l3["ht"]
print(l3.round(3).to_string(index=False)); print("global :", round(l3["marge"].sum() / l3["ht"].sum(), 4), "| moyenne des taux :", round(l3["taux"].mean(), 4))
```
<!--sortie-->
```text
  ttc  cout      ht  marge  taux
 59.9  36.8  49.917 13.117 0.263
 24.0  14.5  20.000  5.500 0.275
120.0  72.0 100.000 28.000 0.280
global : 0.2744 | moyenne des taux : 0.2726
```
<!--sortie-->

### Corrigé 2.2

30 décembre 2024 : année ISO 2025, semaine 1. 1er janvier 2025 : année ISO 2025, semaine 1. 29 décembre 2025 : année ISO 2026, semaine 1. 1er janvier 2026 : année ISO 2026, semaine 1. Les derniers jours de décembre peuvent appartenir à la semaine 1 de l'année **suivante**.

```python
for j in ["2024-12-30", "2025-01-01", "2025-12-29", "2026-01-01"]:
    i = pd.Timestamp(j).isocalendar(); print(j, "-> année ISO", i.year, "semaine", i.week)
```
<!--sortie-->
```text
2024-12-30 -> année ISO 2025 semaine 1
2025-01-01 -> année ISO 2025 semaine 1
2025-12-29 -> année ISO 2026 semaine 1
2026-01-01 -> année ISO 2026 semaine 1
```
<!--sortie-->

### Corrigé 2.3

Avec `right=False` (intervalles `[a ; b[`) : 50,00 → « 50 à 100 » ; 99,99 → « 50 à 100 » ; 100,00 → « 100 à 200 » ; 200,00 → « 200 et + ». Avec `right=True` (`]a ; b]`) : 50,00 → « < 50 » ; 99,99 → « 50 à 100 » ; 100,00 → « 50 à 100 » ; 200,00 → « 100 à 200 ».

```python
pan = lig.groupby("id_commande")["montant"].sum()
bornes = [0, 50, 100, 200, np.inf]; lab = ["< 50", "50 à 100", "100 à 200", "200 et +"]
test = pd.Series([50.00, 99.99, 100.00, 200.00])
print(pd.cut(test, bornes, right=False, labels=lab).tolist()); print(pd.cut(test, bornes, right=True, labels=lab).tolist())
print("paniers exactement égaux à une borne :", int(pan.round(2).isin([50, 100, 200]).sum()), "sur", len(pan))
```
<!--sortie-->
```text
['50 à 100', '50 à 100', '100 à 200', '200 et +']
['< 50', '50 à 100', '50 à 100', '100 à 200']
paniers exactement égaux à une borne : 0 sur 36395
```
<!--sortie-->

### Corrigé 2.4

```python
w = cmd[cmd["date_commande"].dt.year == 2025].assign(we=lambda d: d["date_commande"].dt.dayofweek >= 5)
cl_we = w.groupby("id_client")["we"].agg(part="mean", n="size")
tous = pd.read_csv("donnees/clients.csv")[["id_client"]].merge(cl_we, on="id_client", how="left")
print("clients sans commande en 2025 :", int(tous["n"].isna().sum()), "| moyenne en laissant les vides :", round(tous["part"].mean(), 3), "| avec des zéros :", round(tous["part"].fillna(0).mean(), 3))
print("part des commandes passées le week-end (toutes les commandes) :", round(w["we"].mean(), 3))
```
<!--sortie-->
```text
clients sans commande en 2025 : 2125 | moyenne en laissant les vides : 0.296 | avec des zéros : 0.191
part des commandes passées le week-end (toutes les commandes) : 0.295
```
<!--sortie-->

Pour un client sans commande, la part est **indéfinie** (zéro divisé par zéro) : elle n'est pas nulle. Laisser les vides donne une moyenne **par client** ; remplacer par zéro l'écrase. Aucune des deux ne répond à « quelle part des commandes se passe le week-end ? » : cette question se pose **au niveau des commandes** (dernière ligne affichée), pas des clients. Le niveau d'agrégation doit correspondre à la question.

### Corrigé 2.5

`a` contient les produits 1, 2, 3, 5 ; `b` les produits 2, 3, 4, 5, 6. `inner` : produits 2, 3, 5 (3 lignes) ; `left` : 1, 2, 3, 5 (4 lignes) ; `right` : 2, 3, 4, 5, 6 (5 lignes) ; `outer` : 1, 2, 3, 4, 5, 6 (6 lignes).

```python
a = pd.DataFrame({"id": [1, 2, 3, 5], "nom": list("wxyz")}); b = pd.DataFrame({"id": [2, 3, 4, 5, 6], "stock": [10, 0, 7, 3, 9]})
print({how: len(a.merge(b, on="id", how=how)) for how in ["inner", "left", "right", "outer"]})
```
<!--sortie-->
```text
{'inner': 3, 'left': 4, 'right': 5, 'outer': 6}
```
<!--sortie-->

### Corrigé 2.6

(a) autant de lignes que `lig` : jointure m:1, chaque ligne a une seule commande ; (b) **le double** : n–n, chaque nom a deux produits ; (c) autant que `cmd` : m:1.

```python
cli = pd.read_csv("donnees/clients.csv")
print("(a)", len(lig), "->", len(lig.merge(cmd, on="id_commande", validate="m:1")))
print("(b)", len(ventes), "->", len(ventes.merge(prod[["nom_produit", "prix_vente"]], on="nom_produit")))
print("(c)", len(cmd), "->", len(cmd.merge(cli[["id_client"]], on="id_client", validate="m:1")))
```
<!--sortie-->
```text
(a) 83905 -> 83905
(b) 26188 -> 52376
(c) 36395 -> 36395
```
<!--sortie-->

### Corrigé 2.7

```python
abime = "Théière".encode("utf-8").decode("cp1252")
repare = abime.encode("cp1252").decode("utf-8")
import ftfy
print(abime, "->", repare, "| ftfy :", ftfy.fix_text(abime))
```
<!--sortie-->
```text
ThÃ©iÃ¨re -> Théière | ftfy : Théière
```
<!--sortie-->

La réparation inverse (réencoder en `cp1252` puis décoder en UTF-8) ne marche que si **tous** les caractères abîmés existent dans `cp1252` : certaines séquences UTF-8 produisent des octets que `cp1252` ne sait pas représenter, et l'information est alors **perdue**. `ftfy` essaie plusieurs réparations et retient celle qui donne du texte plausible.

### Corrigé 2.8

```python
s = site[~site["est_test"]].assign(jour=lambda d: d["date_heure"].dt.date)
s["brut"] = pd.to_numeric(s["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", "."))
med = s.groupby("jour")["brut"].median()
premier = med[med > 500].index.min()
print("premier jour dont la médiane dépasse 500 :", premier, "| premier jour avec Z :", s.loc[s["en_utc"], "jour"].min())
print("lignes avec Z et montant < 500 :", int((s["en_utc"] & (s["brut"] < 500)).sum()), "| lignes sans Z et montant ≥ 500 :", int((~s["en_utc"] & (s["brut"] >= 500)).sum()))
```
<!--sortie-->
```text
premier jour dont la médiane dépasse 500 : 2025-09-15 | premier jour avec Z : 2025-09-15
lignes avec Z et montant < 500 : 23 | lignes sans Z et montant ≥ 500 : 7
```
<!--sortie-->

```python hide
NUM("n_z_petit", (s["en_utc"] & (s["brut"] < 500)).sum()); NUM("n_noz_gros", (~s["en_utc"] & (s["brut"] >= 500)).sum()); NUM("n_z", s["en_utc"].sum())
```
<!--sortie-->
```text
NUM n_z_petit 23
NUM n_noz_gros 7
NUM n_z 2494
```

La rupture de la médiane **commence le jour** de l'apparition du `Z` (affichage ci-dessus). Les deux conditions ne coïncident pas ligne à ligne : 23 lignes à `Z` ont un montant brut inférieur à 500 (de **petites** commandes : 5 € en centimes font 500) et 7 lignes sans `Z` dépassent 500 (de **grosses** commandes en euros) : un seuil sur le montant n'est **pas** un test de format. Et la coïncidence des dates ne **prouve** pas que les montants sont en centimes : elle montre que **deux changements arrivent le même jour**. Ce qui le prouve, c'est l'**autre source** : le total de chaque commande égale la somme de ses lignes (en euros) après division par cent (section 2.2.4), pour les 2 494 lignes à `Z` comme pour les autres.

### Corrigé 2.9

```python
m = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande", validate="m:1")
m = m[m["date_commande"].dt.year == 2025]
pan_c = m.groupby(["canal", "id_commande"])["montant"].sum().groupby("canal").mean()
lg = m.groupby("canal")["montant"].mean()
print(pd.DataFrame({"panier moyen (a)": pan_c, "montant moyen d'une ligne (b)": lg}).round(2).to_string())
```
<!--sortie-->
```text
          panier moyen (a)  montant moyen d'une ligne (b)
canal                                                    
Boutique            103.08                          44.48
Réseaux             102.44                          44.43
Site                101.63                          44.35
```
<!--sortie-->

La moyenne des **lignes** (b) mesure le prix moyen d'un article vendu ; le **panier moyen** (a) est le chiffre d'affaires par commande. Une commande compte plusieurs lignes : (b) est plus petit, d'un facteur proche du nombre moyen de lignes par commande.

### Corrigé 2.10

```python
ca_j = ventes.groupby("date")["montant"].sum()
v7 = ca_j.rolling(7, min_periods=7).mean(); v1 = ca_j.rolling(7, min_periods=1).mean(); vc = ca_j.rolling(7, center=True, min_periods=7).mean()
print("valeurs vides :", int(v7.isna().sum()), int(v1.isna().sum()), int(vc.isna().sum()))
d15 = pd.Timestamp("2025-06-15")
print("15 juin :", round(v7[d15]), round(v1[d15]), round(vc[d15]))
```
<!--sortie-->
```text
valeurs vides : 6 0 6
15 juin : 3208 3208 2971
```
<!--sortie-->

`min_periods=7` : 6 vides au début ; `min_periods=1` : aucun vide, mais les six premières valeurs reposent sur **moins** de sept jours (donc plus bruitées) ; centrée : 3 vides au début **et** 3 à la fin. Pour **décrire** le niveau du 15 juin, la moyenne **centrée** est la plus juste (elle regarde autant avant qu'après) ; pour **prévoir** le 16, on ne peut utiliser que la moyenne **arrière** (`min_periods=7`) : la centrée utiliserait des jours futurs, c'est une fuite d'information.

### Corrigé 2.11

```python
ventes["mois"] = ventes["date"].dt.strftime("%Y-%m")
large = ventes.pivot_table(index="categorie", columns="mois", values="montant", aggfunc="sum")
long = large.reset_index().melt(id_vars="categorie", var_name="mois", value_name="ca")
retour = long.pivot(index="categorie", columns="mois", values="ca")
print("aller-retour identique :", bool(retour.equals(large)), "| total large :", round(large.sum().sum(), 2), "| total long :", round(long["ca"].sum(), 2))
try:
    ventes.pivot(index="categorie", columns="mois", values="montant")
except ValueError as e:
    print("pivot direct :", e)
```
<!--sortie-->
```text
aller-retour identique : True | total large : 1164636.72 | total long : 1164636.72
pivot direct : Index contains duplicate entries, cannot reshape
```
<!--sortie-->

`pivot` refuse parce que la table des ventes a **plusieurs lignes** par couple (catégorie, mois) : il ne sait pas **agréger**. `pivot_table` exige de dire comment (`aggfunc`), ce que fait aussi un tableau croisé dynamique de tableur, mais sans le dire.

### Corrigé 2.12

```python
n_nd = int(brut.loc[est_produit].iloc[:, 2:].map(lambda v: str(v).strip() in ("ND", "—")).sum().sum())
print("cellules ND ou — :", n_nd, "| stock moyen d'octobre, inconnus ignorés / à zéro :", round(m_ignore, 2), "/", round(m_zero, 2))
```
<!--sortie-->
```text
cellules ND ou — : 71 | stock moyen d'octobre, inconnus ignorés / à zéro : 47.59 / 44.82
```
<!--sortie-->

Le remplacement par zéro **sous-estime** le stock moyen (voir la piste de l'application 2.8) : un inconnu n'est pas un zéro. Pour « rupture », le zéro est exact : on sait que le stock est nul, ce que la mention signifie.

### Corrigé 2.13

La distance entre `bougie` et `bougeoir` est **3** : on garde `boug`, on insère `e` et `o` avant le `i` (2 insertions), le `i` est conservé, puis on remplace le `e` final de `bougie` par un `r` (1 remplacement). La table de programmation dynamique de la section 2.5.3 donne ce minimum dans sa dernière case.

```python
from rapidfuzz.distance import Levenshtein
from rapidfuzz import fuzz
dist = Levenshtein.distance("bougie", "bougeoir")
print("distance :", dist, "| similarité :", round(100 * (1 - dist / max(len("bougie"), len("bougeoir"))), 1), "| ratio rapidfuzz :", round(fuzz.ratio("bougie", "bougeoir"), 1))
print("token_set_ratio « bougie nordique » / « nordique bougie » :", round(fuzz.token_set_ratio("bougie nordique", "nordique bougie")), "| ratio simple :", round(fuzz.ratio("bougie nordique", "nordique bougie"), 1))
```
<!--sortie-->
```text
distance : 3 | similarité : 62.5 | ratio rapidfuzz : 71.4
token_set_ratio « bougie nordique » / « nordique bougie » : 100 | ratio simple : 53.3
```
<!--sortie-->

### Corrigé 2.14

```python
def cout_total(seuil, c_fp, c_fn):
    sel = S["score"] >= seuil
    fp = int((sel & ~S["vrai"]).sum()); fn = len(vraies) - int((sel & S["vrai"]).sum())
    return c_fp * fp + c_fn * fn
hypotheses = {"5 pour 1": (5, 1), "1 pour 1": (1, 1)}
opt = {nom: min(range(50, 101), key=lambda t: cout_total(t, *h)) for nom, h in hypotheses.items()}
print("seuil optimal :", opt, "| coûts :", {nom: cout_total(t, *hypotheses[nom]) for nom, t in opt.items()})
```
<!--sortie-->
```text
seuil optimal : {'5 pour 1': 83, '1 pour 1': 77} | coûts : {'5 pour 1': 76, '1 pour 1': 37}
```
<!--sortie-->

```python hide
NUM("seuil_5", opt["5 pour 1"]); NUM("seuil_1", opt["1 pour 1"])
```
<!--sortie-->
```text
NUM seuil_5 83
NUM seuil_1 77
```

Quand une **fusion erronée coûte cinq fois plus** qu'un doublon raté, le seuil optimal est **83** ; quand les deux coûts sont égaux, il est de **77**. Un coût plus élevé pour les fusions fautives pousse le seuil vers le haut : on accepte moins de paires et l'on tolère plus de doublons pour éviter de fusionner deux personnes. Un seuil est un **choix de coût**, pas un fait statistique.
