```python hide
import os, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

## 1.3 Doublons

Un doublon est un même fait enregistré deux fois : une commande exportée en double, un ticket scanné deux fois, un client saisi sous deux écritures. Il gonfle les totaux (le chiffre d'affaires, le nombre de clients), et il passe inaperçu, puisqu'une ligne en double ressemble à une ligne ordinaire. Cette section apprend à les **définir**, à les **repérer** même quand ils ne sont pas identiques, et à décider **lequel garder**.

### 1.3.1 Exact ou approché, clé naturelle ou clé technique

Un doublon **exact** est une ligne identique, caractère pour caractère, à une autre. Un doublon **approché** (ou « flou ») désigne la même réalité écrite autrement : « Mirela Dorvane » et « MIRELA DORVANE », « Mirela » et « M. ». Pour savoir si deux lignes se ressemblent *assez*, il faut d'abord décider **ce qui identifie** un enregistrement : sa **clé**.

- Une **clé technique** est un numéro attribué par le système (`id_crm`, `order_ref`). Elle est unique **par construction**… et donc inutile pour détecter un doublon : deux saisies du même client reçoivent deux numéros différents.
- Une **clé naturelle** est une propriété du monde réel qui identifie la chose : l'e-mail d'un client, le couple (ticket, produit) d'une ligne de caisse. Elle n'est unique que **si le monde le veut bien**.

pandas offre `duplicated()` (qui marque les lignes répétées) et `drop_duplicates()` (qui les retire). Leurs deux arguments à connaître sont `subset` (les colonnes qui forment la clé) et `keep` (garder la première occurrence, la dernière, ou aucune). Appliquons-les au fichier clients du CRM : 7 140 lignes pour 6 000 clients.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
sans_id = crm.drop(columns="id_crm")
print("lignes :", len(crm), "| doublons exacts (hors identifiant technique) :", int(sans_id.duplicated().sum()))
print(crm[sans_id.duplicated(keep=False)][["prenom", "nom", "email"]].drop_duplicates().to_string(index=False))
```
<!--sortie-->
```text
lignes : 7140 | doublons exacts (hors identifiant technique) : 139
prenom  nom            email
  Test TEST test@example.com
```

Il y a 139 doublons exacts, et ce sont tous des **lignes de test** (« Test TEST », adresse `test@example.com`) : 140 lignes identiques qu'il faut écarter, mais qui ne sont pas des clients. Les vrais doublons du CRM sont **approchés** : les chercher avec `duplicated()` sur l'ensemble des colonnes ne trouve rien. Prenons une clé naturelle, l'e-mail, normalisée (sans espaces ni majuscules).

```python
crm["email_cle"] = crm["email"].str.strip().str.lower()
reel = crm[crm["email_cle"].notna() & (crm["email_cle"] != "test@example.com")].copy()
doublons_email = reel.duplicated("email_cle", keep="first")
print("lignes avec un e-mail utilisable :", len(reel), "| marquées doublon par l'e-mail normalisé :", int(doublons_email.sum()))
```
<!--sortie-->
```text
lignes avec un e-mail utilisable : 6769 | marquées doublon par l'e-mail normalisé : 677
```

L'e-mail normalisé désigne 677 lignes comme des doublons. Combien le sont **vraiment** ? C'est ici que la vérité, que nous n'avons pas dans la vie réelle, permet de juger la clé.

```python
vrai_crm = pd.read_csv(os.path.join(D, "verite_crm.csv"))
reel["id_crm"] = reel["id_crm"].astype(int)
reel = reel.merge(vrai_crm[["id_crm", "id_client"]], on="id_crm")
premier = reel.groupby("email_cle")["id_client"].transform("first")
a_tort = doublons_email.values & (reel["id_client"] != premier).values
print("marquées à tort (deux clients différents, même e-mail) :", int(a_tort.sum()))
reels = vrai_crm.loc[vrai_crm["id_client"] > 0, "id_client"]
print("doublons réels dans le fichier (hors test) :", int(reels.duplicated().sum()), "| retrouvés par l'e-mail :", int(doublons_email.sum() - a_tort.sum()))
```
<!--sortie-->
```text
marquées à tort (deux clients différents, même e-mail) : 3
doublons réels dans le fichier (hors test) : 1000 | retrouvés par l'e-mail : 674
```

Le bilan de cette clé : **674 vrais doublons retrouvés sur 1 000** (rappel de 67 %), **3 fausses alertes** (précision de 99,6 %). Deux enseignements. D'abord, une clé naturelle n'est jamais parfaite : ici, deux personnes différentes ont reçu la même adresse (des homonymes), et un tiers des doublons échappe à l'e-mail parce que leur e-mail est absent ou mal écrit. Ensuite, aucune clé unique ne suffit : on en **combine plusieurs** (e-mail, puis nom et date de naissance, puis téléphone) ou l'on passe à un **rapprochement approché**, objet de la section 2.5 du chapitre suivant.

> ⚠️ **Piège.** Retirer les doublons sur **toutes** les colonnes ne retire que les copies parfaites. Retirer sur une clé **trop large** (le nom de famille seul) fusionne des personnes différentes. Dans les deux cas, on se trompe sans le voir : mesurez toujours le nombre de lignes retirées, et regardez-en un échantillon.

### 1.3.2 Les doublons d'export de la plateforme web

Le site de la boutique exporte ses commandes dans `site_commandes.csv`. Un export qu'on relance après un incident réécrit parfois les mêmes commandes : voici ce que cela donne, et ce que cela coûte. Nous ne regardons que la période de janvier à août, avant le changement d'unité de septembre (section 1.4.2), pour que les montants soient comparables.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
print("lignes :", len(site), "| commandes distinctes :", site["order_ref"].nunique(), "| lignes strictement identiques :", int(site.duplicated().sum()))
av = site[site["created_at"] < "2025-09-01"].copy()
av["total_n"] = av["total"].str.replace("€", "", regex=False).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False).astype(float)
```
<!--sortie-->
```text
lignes : 6259 | commandes distinctes : 6138 | lignes strictement identiques : 121
```

On compte 121 lignes de trop : toutes les lignes en double sont des **copies exactes**, faciles à retirer. Mais il y a **deux autres types de lignes qui ne doivent pas compter** dans le chiffre d'affaires : les commandes de test (adresse `test@example.com`) et les commandes annulées (statut `cancelled`, écrit aussi `paid` ou `PAID` pour les autres, en trois casses différentes, ce qu'il faudra normaliser). On enchaîne les trois filtres, en comptant à chaque étape.

```python
a = av.drop_duplicates("order_ref")
b = a[~a["customer_email"].str.strip().str.lower().eq("test@example.com")]
c = b[b["status"].str.lower() != "cancelled"]
for nom, t in [("lignes brutes", av), ("sans doublons d'export", a), ("sans commandes de test", b), ("sans commandes annulées", c)]:
    print(f"{nom:26s} {len(t):5d} commandes {t['total_n'].sum():12,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
lignes brutes               3493 commandes   358 029.54 €
sans doublons d'export      3431 commandes   350 778.16 €
sans commandes de test      3397 commandes   350 744.16 €
sans commandes annulées     3295 commandes   340 260.31 €
```

De janvier à août, le total brut est de 358 029,54 € pour 3 493 lignes. Les doublons en gonflent le nombre de 62 (1,8 %) et le montant de 7 251,38 € (2,1 %), les commandes de test de 34 €, et les commandes annulées de 10 484 € supplémentaires (3,1 %). Au total, **le chiffre d'affaires brut surestime le vrai de 5,2 %**. Le contrôle ultime, c'est la vérité : les commandes valides sont exactement 3 295, pour 340 260,31 €, comme l'enchaînement des trois filtres.

```python
vs = pd.read_csv(os.path.join(D, "verite_site.csv"))
dates = site.drop_duplicates("order_ref").set_index("order_ref")["created_at"]
vs = vs[vs["defaut"].isna() & (vs["order_ref"].map(dates) < "2025-09-01")]
print("vérité : ", len(vs), "commandes valides,", f"{vs['total_vrai'].sum():,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
vérité :  3295 commandes valides, 340 260.31 €
```

Retenez la **méthode** : trois filtres, appliqués dans un ordre explicite, chacun accompagné de son compte. C'est ce qui permet de répondre à la question « d'où vient la différence entre mon chiffre et celui du site ? ».

### 1.3.3 Les doublons de scan en caisse : quand la copie est peut-être légitime

La caisse de la boutique pose un problème plus subtil. Quand une caissière scanne deux fois le même article par erreur, on obtient deux lignes identiques dans le même ticket. Mais **un client peut aussi acheter deux fois le même article** : deux lignes identiques légitimes. Rien, dans le fichier, ne distingue les deux cas. Lisons les douze fichiers (la fonction `lire_caisse`, qui absorbe leurs formats différents, est écrite en 1.4.6) et cherchons les lignes identiques.

```python
cais = pd.concat([C.lire_caisse(f)[0] for f in sorted(glob.glob(os.path.join(D, "caisse", "*.csv")))], ignore_index=True)
cais["article"] = cais["article"].str.lower()
identiques = cais.duplicated(["ticket", "article", "quantite", "prix_unitaire", "montant"], keep="first")
print("lignes dans les fichiers :", len(cais), "| lignes identiques à une précédente :", int(identiques.sum()))
```
<!--sortie-->
```text
lignes dans les fichiers : 12678 | lignes identiques à une précédente : 163
```

163 lignes sont identiques à une ligne précédente du même ticket. Faut-il toutes les retirer ? Pour trancher, il faut une **référence** : la base de données de la boutique sait, elle, ce que contient chaque ticket. On rapproche chaque ligne de la caisse d'une ligne de la base, avec une clé (ticket, article, quantité, prix) complétée d'un **rang** : la première ligne « Plaid, 1, 22,56 € » d'un ticket correspond à la première de la base, la deuxième à la deuxième, et ainsi de suite. Une ligne de la caisse **sans correspondance** est une ligne en trop.

```python
produits = pd.read_csv(os.path.join(D, "produits.csv"))[["id_produit", "nom_produit"]]
base = pd.read_csv(os.path.join(D, "lignes_commande.csv")).merge(pd.read_csv(os.path.join(D, "commandes.csv"))[["id_commande", "canal", "date_commande"]], on="id_commande").merge(produits, on="id_produit")
base = base[(base["canal"] == "Boutique") & (base["date_commande"] >= "2025-01-01")].copy()
base["article"] = base["nom_produit"].str.lower()
cle = ["id_commande", "article", "quantite", "prix_unitaire"]
for t in (cais, base):
    t["rang"] = t.groupby(cle).cumcount()
rapproche = cais.merge(base[cle + ["rang", "montant"]].rename(columns={"montant": "montant_base"}), on=cle + ["rang"], how="left", indicator=True)
en_trop = rapproche["_merge"] == "left_only"
print("lignes dans la base :", len(base), "| lignes de la caisse sans correspondance :", int(en_trop.sum()))
```
<!--sortie-->
```text
lignes dans la base : 12611 | lignes de la caisse sans correspondance : 67
```

La base compte 12 611 lignes pour les mêmes tickets : il y a **67 lignes en trop**, et non 163. Les **96 autres lignes « identiques »** sont de vraies ventes de deux exemplaires d'un même article. Mesurons ce que serait l'erreur d'un dédoublonnage sans référence.

```python
fr = lambda x: f"{x:,.2f} €".replace(",", " ")
print("avec la référence : ", int(en_trop.sum()), "lignes retirées, montant", fr(rapproche.loc[en_trop, "montant"].sum()))
print("sans la référence :", int(identiques.sum()), "lignes retirées, montant", fr(cais.loc[identiques, "montant"].sum()))
```
<!--sortie-->
```text
avec la référence :  67 lignes retirées, montant 3 126.29 €
sans la référence : 163 lignes retirées, montant 7 576.01 €
```

Avec la référence, on retire exactement 67 lignes (3 126,29 €). Sans elle, on en retire 163 (7 576,01 €) : **4 449,72 € de vraies ventes** auraient disparu. La réconciliation (chapitre 3) est la généralisation de cette idée : un doublon se prouve contre une **source indépendante**.

> 🧪 **Remarque.** Le fichier de caisse contient, à la dernière ligne de chaque mois, un **total**. La somme de ces douze totaux (560 973,91 €) est **exactement** le chiffre d'affaires de la base pour ces tickets : la caisse avait raison, c'est l'export qui a perdu des montants et ajouté des doublons (section 1.4.6). Un total affiché est un excellent point de contrôle à conserver.

### 1.3.4 Quel enregistrement garder ?

Une fois les doublons identifiés, il faut en garder **un**. Quatre critères sont courants.

| Critère | Principe | Convient quand |
|---|---|---|
| **Le plus récent** | on garde la dernière saisie | les données changent (adresse, téléphone) |
| **Le plus complet** | on garde la ligne avec le moins de trous | les copies diffèrent par ce qu'elles contiennent |
| **La source la plus fiable** | on garde l'enregistrement du système de référence | une source fait autorité (le logiciel de caisse plutôt que le tableur) |
| **La fusion** | on garde, colonne par colonne, la première valeur renseignée | chaque copie a des morceaux utiles |

Regardons une paire du CRM, retrouvée par l'e-mail normalisé : les clients 3921 et 3922.

```python
paire = reel[reel["id_crm"].isin([3921, 3922])].sort_values("id_crm")[["id_crm", "prenom", "nom", "ville", "code_postal", "date_naissance"]]
print(paire.to_string(index=False))
```
<!--sortie-->
```text
 id_crm prenom      nom   ville code_postal date_naissance
   3921 Ardare Brentier  Vile A         NaN     05/02/1960
   3922 ARDARE BRENTIER Ville A       01601     1960-05-02
```

Les deux lignes décrivent la même personne. La première a une faute dans la ville (« Vile A ») et pas de code postal ; la seconde a tout, mais le nom en majuscules ; les dates de naissance ne sont pas écrites de la même façon (jour/mois/année et année-mois-jour). Garder **la plus complète** et combler ses trous avec l'autre est ce qui donne le meilleur enregistrement. En pandas, `groupby(...).first()` fait exactement cela : il prend, colonne par colonne, la première valeur **non vide**.

```python
reel["manquants"] = reel.isna().sum(axis=1)
fusion = reel.sort_values(["email_cle", "manquants"]).groupby("email_cle", as_index=False).first()
print("lignes avant :", len(reel), "| après fusion par e-mail :", len(fusion))
print("codes postaux manquants avant :", int(reel["code_postal"].isna().sum()), "| après :", int(fusion["code_postal"].isna().sum()))
```
<!--sortie-->
```text
lignes avant : 6769 | après fusion par e-mail : 6092
codes postaux manquants avant : 408 | après : 328
```

On passe de 6 769 lignes à 6 092 fiches, et le nombre de codes postaux manquants de 408 à 328 : la fusion a **comblé 80 trous** que chaque copie, prise seule, ne comblait pas. Les 231 lignes sans e-mail ne sont pas fusionnées (elles échappent à cette clé) : elles seront rapprochées autrement, au chapitre suivant (section 2.5).

> ✅ **À retenir.** Un traitement de doublons comprend **quatre actes** : (1) définir la clé, (2) repérer, **en mesurant** ce qui est retrouvé et ce qui est faussement signalé, (3) choisir l'enregistrement à garder, (4) **journaliser** ce que l'on a retiré (garder une table des lignes écartées avec la raison). Un total qui change après dédoublonnage doit pouvoir s'expliquer ligne à ligne.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.4, exercices 1.6 et 1.7.
