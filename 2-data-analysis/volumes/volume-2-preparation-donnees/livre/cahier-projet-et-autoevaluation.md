# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume II. Il contient **le projet du volume** : **nettoyer et réconcilier deux sources désordonnées** (la caisse de la boutique et l'export du site web) en **un jeu de données fiable** des ventes de 2025, avec son journal de nettoyage, ses contrôles, son rapport d'écarts et son dictionnaire ; puis l'**auto-évaluation** (quarante questions). Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre.

## Projet du volume

### P.1 Le cahier des charges

La gérante vous écrit : « *La comptable m'annonce un chiffre d'affaires de 2025 que je n'arrive pas à retrouver avec la caisse et le site. Peux-tu me fabriquer une table unique des ventes de l'année, dont je puisse dire d'où vient chaque chiffre ? Et si quelque chose cloche dans les fichiers, dis-le-moi.* »

Vous traduisez en **six exigences** :

1. **Une table unique** des commandes de 2025 pour les deux canaux dont on a un export (Boutique par la caisse, Site par la plateforme), avec une ligne par commande. Le troisième canal, Réseaux, n'apparaît dans **aucun** des deux fichiers : on le signalera.
2. **Un nettoyage rejouable** : un script qui part des fichiers bruts, sans retouche manuelle.
3. **Un journal** : chaque étape consigne ses effectifs et ses totaux avant et après.
4. **Des contrôles** qui échouent bruyamment (types, plages, unicité, totaux).
5. **Une réconciliation** avec la base de données de l'entreprise : chaque écart est **expliqué**, ou signalé.
6. **Un dictionnaire de données** de la table finale.

La méthode suit dix étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Inventaire | Que contient chaque source ? Quel est son grain ? | 3.1, 4.1 |
| P.3 Lire la caisse | Comment lire douze fichiers qui n'ont pas le même format ? | 1.4, 2.2 |
| P.4 Nettoyer la caisse | Que faire des montants vides et des lignes en double ? | 1.1, 1.3 |
| P.5 Nettoyer le site | Doublons d'export, tests, annulations, unités : comment s'y retrouver ? | 1.3, 1.4 |
| P.6 Réconcilier | Les totaux s'accordent-ils avec la base ? Sinon, pourquoi ? | 3.3 |
| P.7 Assembler | Comment fabriquer la table unique ? | 2.2 |
| P.8 Contrôler | Les contrôles passent-ils ? | 3.2, 3.5 |
| P.9 Documenter | Quel journal, quel dictionnaire ? | 4.1, 4.2 |
| P.10 Juger | Peut-on livrer ? Que reste-t-il comme écart ? | 3.4 |

> 📦 **Les données.** `donnees/caisse/caisse_2025-01.csv` … `caisse_2025-12.csv`, `donnees/site_commandes.csv` et `donnees/site_lignes.csv`, plus la base de référence (`commandes.csv`, `lignes_commande.csv`). Elles sont **simulées** : des erreurs ont été **injectées** et leur vérité est dans les fichiers `verite_*.csv`, que nous n'ouvrirons qu'à la fin (P.10), comme on ouvre une correction.

### P.2 Étape 1 : l'inventaire des sources

Avant de nettoyer, on regarde ce que l'on a : combien de fichiers, de lignes, quelles colonnes, quel grain (livre, 3.1 et 4.1).

```python
import io, glob, os, re
import numpy as np, pandas as pd

fichiers = sorted(glob.glob("donnees/caisse/caisse_2025-*.csv"))
print("fichiers de caisse :", len(fichiers))
for f in (fichiers[0], fichiers[6], fichiers[10]):
    with open(f, "rb") as h:
        debut = h.read(160)
    print(os.path.basename(f), "| BOM :", debut.startswith(b"\xef\xbb\xbf"), "| séparateur détecté :", ";" if debut.count(b";") > debut.count(b",") else ",")
site = pd.read_csv("donnees/site_commandes.csv", dtype=str)
print("export du site :", len(site), "lignes,", site["order_ref"].nunique(), "références distinctes ;", list(site.columns))
```
<!--sortie-->
```text
fichiers de caisse : 12
caisse_2025-01.csv | BOM : False | séparateur détecté : ;
caisse_2025-07.csv | BOM : True | séparateur détecté : ;
caisse_2025-11.csv | BOM : True | séparateur détecté : ,
export du site : 6259 lignes, 6138 références distinctes ; ['order_ref', 'created_at', 'status', 'customer_email', 'customer_name', 'total', 'currency', 'promo_code', 'shipping_mode']
```

**Lecture.** Douze fichiers de caisse, dont le format change en juillet (BOM, nouveau format de date) et en octobre (séparateur `,`). L'export du site compte 6 259 lignes pour 6 138 références distinctes : 121 lignes sont des répétitions.

On constate déjà : la caisse change de **format** en cours d'année, et l'export du site contient **plus de lignes que de références** : il y a des répétitions à examiner.

### P.3 Étape 2 : lire la caisse, douze fichiers, trois formats

Une seule fonction de lecture, **paramétrée** par le mois, plutôt que douze lectures copiées : encodage, séparateur, décimale, date, noms de colonnes (livre, 1.4 et 2.2). On contrôle chaque fichier contre sa propre ligne de total.

```python
COLONNES = {"N° ticket": "ticket", "Ticket": "ticket", "Date": "date", "Heure": "heure", "Article": "article", "Catégorie": "categorie",
            "Qté": "qte", "Quantité": "qte", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}

def lire_caisse(chemin):
    mois = int(re.search(r"_2025-(\d\d)", chemin).group(1))
    enc, sep, dec = ("cp1252", ";", ",") if mois <= 6 else (("utf-8-sig", ";", ",") if mois <= 9 else ("utf-8-sig", ",", "."))
    with open(chemin, encoding=enc) as f:
        lignes = f.read().splitlines()
    total = float(lignes[-1].split(sep)[-1].replace(dec, "."))
    debut = next(i for i, l in enumerate(lignes) if re.match(r'"?(N° ticket|Ticket)"?' + re.escape(sep), l))
    df = pd.read_csv(io.StringIO("\n".join(lignes[debut:-1])), sep=sep, dtype=str)
    df["numero_ligne"] = df.index + debut + 2                    # numéro de ligne dans le fichier (pour retrouver une erreur)
    df = df[df.iloc[:, 0] != df.columns[0]].rename(columns=COLONNES)
    for c in ["prix_unitaire", "montant"]:
        df[c] = pd.to_numeric(df[c].str.replace(",", ".") if dec == "," else df[c], errors="coerce")
    df["qte"] = df["qte"].astype(int)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y" if 7 <= mois <= 9 else "%d/%m/%Y")
    df["remise_pct"] = pd.to_numeric(df.get("remise_pct"), errors="coerce")
    df["fichier"] = os.path.basename(chemin)
    return df, total
```

```python
lectures = [lire_caisse(f) for f in fichiers]
caisse = pd.concat([d for d, _ in lectures], ignore_index=True)
controle = pd.DataFrame({"fichier": [os.path.basename(f) for f in fichiers], "lignes": [len(d) for d, _ in lectures],
                         "somme_lue": [round(d["montant"].sum(), 2) for d, _ in lectures], "total_affiche": [t for _, t in lectures]})
controle["ecart"] = (controle["total_affiche"] - controle["somme_lue"]).round(2)
print(controle.head(3).to_string(index=False))
print("lignes lues :", len(caisse), "| montants vides :", int(caisse["montant"].isna().sum()), "| total affiché des douze fichiers :", round(controle["total_affiche"].sum(), 2))
print("somme des montants présents :", round(caisse["montant"].sum(), 2))
```
<!--sortie-->
```text
           fichier  lignes  somme_lue  total_affiche   ecart
caisse_2025-01.csv     955   37826.31       38882.41 1056.10
caisse_2025-02.csv     770   32273.46       33079.41  805.95
caisse_2025-03.csv     916   37863.67       39038.90 1175.23
lignes lues : 12678 | montants vides : 399 | total affiché des douze fichiers : 560973.91
somme des montants présents : 547896.42
```

**Lecture.** 12 678 lignes lues, dont 399 sans montant. La somme des montants présents (547 896,42 €) est inférieure de 13 077,49 € au total affiché par la caisse (560 973,91 €) : l'écart est dominé par les montants vides, mais les lignes en double, elles, **gonflent** la somme en sens inverse.

Les douze fichiers se lisent avec la **même** fonction, et **aucun** ne retombe sur son total : l'écart a deux sources possibles, les **montants vides** (qui font baisser la somme) et les **lignes en double** (qui la font monter).

### P.4 Étape 3 : nettoyer la caisse

On traite les deux problèmes **l'un après l'autre**, en mesurant chaque fois l'effet (livre, 1.1 et 1.3). D'abord les montants vides : ils se reconstituent par quantité × prix unitaire (en retirant la remise quand le fichier la donne, à partir d'octobre).

```python
journal = []
def noter(etape, df, note=""):
    journal.append({"etape": etape, "lignes": len(df), "somme": round(float(df["montant_net"].sum()), 2) if "montant_net" in df else None, "note": note})

caisse["remise_pct"] = caisse["remise_pct"].fillna(0)
caisse["montant_calcule"] = (caisse["qte"] * caisse["prix_unitaire"] * (1 - caisse["remise_pct"] / 100)).round(2)
caisse["montant_net"] = caisse["montant"].fillna(caisse["montant_calcule"])
caisse["montant_reconstitue"] = caisse["montant"].isna()
noter("caisse lue", caisse, "douze fichiers, montants vides reconstitués par quantité x prix")
print("montants reconstitués :", int(caisse["montant_reconstitue"].sum()), "| somme après reconstitution :", round(caisse["montant_net"].sum(), 2))
print("écart avec le total affiché :", round(caisse["montant_net"].sum() - controle["total_affiche"].sum(), 2))
```
<!--sortie-->
```text
montants reconstitués : 399 | somme après reconstitution : 564472.59
écart avec le total affiché : 3498.68
```

**Lecture.** Après reconstitution des 399 montants, la somme dépasse le total affiché de 3 498,68 € : la reconstitution a bien comblé le vide, et il reste un **excédent** à expliquer.

Il reste un écart **positif** : il vient des lignes en double. Mais attention : une ligne identique à une autre dans un même ticket peut être un **vrai double achat** (deux articles identiques) ou un **double scan**. Le fichier seul ne permet pas de trancher ; on s'appuie sur la **base de référence**, qui contient le total de chaque commande (livre, 3.3).

```python
cmd = pd.read_csv("donnees/commandes.csv"); lig = pd.read_csv("donnees/lignes_commande.csv")
base = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
base = base[base["date_commande"] >= "2025-01-01"]
base_boutique = base[base["canal"] == "Boutique"].groupby("id_commande")["montant"].sum().round(2)
caisse["id_commande"] = caisse["ticket"].str[1:].astype(int)
tk = caisse.groupby("id_commande")["montant_net"].sum().round(2)
cmp_ = pd.concat([tk.rename("caisse"), base_boutique.rename("base")], axis=1)
cmp_["ecart"] = (cmp_["caisse"] - cmp_["base"]).round(2)
print("tickets en caisse :", len(tk), "| commandes Boutique en base :", len(base_boutique))
print("tickets dont le total diffère de la base :", int((cmp_["ecart"].abs() > 0.005).sum()), "| tous positifs :", bool((cmp_["ecart"] > -0.005).all()))
```
<!--sortie-->
```text
tickets en caisse : 5442 | commandes Boutique en base : 5442
tickets dont le total diffère de la base : 102 | tous positifs : True
```

**Lecture.** La caisse et la base contiennent les **mêmes** 5 442 commandes ; 102 tickets ont un total supérieur à celui de la base, aucun n'est inférieur. Un écart toujours positif évoque des lignes en trop, pas des lignes manquantes.

```python
suspects = cmp_[cmp_["ecart"] > 0.005].index
caisse["rang"] = caisse.groupby(["id_commande", "article", "qte", "prix_unitaire"]).cumcount()
cand = caisse[caisse["id_commande"].isin(suspects) & (caisse["rang"] > 0)]
retire = cand[cand["montant_net"].round(2).values == cmp_.loc[cand["id_commande"], "ecart"].round(2).values]
caisse["doublon_scan"] = caisse.index.isin(retire.index)
propre = caisse[~caisse["doublon_scan"]].copy()
noter("doublons de scan retirés", propre, f"{int(caisse['doublon_scan'].sum())} lignes dont le montant égale exactement l'écart du ticket")
print("lignes retirées :", int(caisse["doublon_scan"].sum()), "| écart restant avec le total affiché :", round(propre["montant_net"].sum() - controle["total_affiche"].sum(), 2))
```
<!--sortie-->
```text
lignes retirées : 68 | écart restant avec le total affiché : 180.78
```

**Lecture.** 68 lignes sont retirées, et l'écart avec le total affiché tombe de 3 498,68 € à 180,78 €. Le reliquat n'est pas encore expliqué : nous y reviendrons à l'étape de jugement (P.10).

> ⚠️ **Attention.** La règle « supprimer la ligne dont le montant égale l'écart du ticket » est **prudente** : elle ne retire que ce que l'on peut **prouver** avec la base. Un `drop_duplicates` aveugle aurait supprimé aussi des vrais doubles achats. Le reliquat qui subsiste est documenté, pas caché.

### P.5 Étape 4 : nettoyer l'export du site

L'export du site cumule cinq problèmes : doublons d'export, commandes de test, annulations, statuts écrits de trois façons, montants en texte et **unité qui change en cours d'année** (livre, 1.3 et 1.4). On les traite un par un, en notant chaque effectif.

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str)
n0 = len(site)
site = site.drop_duplicates("order_ref")
n1 = len(site)
test = site["customer_email"].str.strip().str.lower().eq("test@example.com")
site = site[~test].copy()
site["statut"] = site["status"].str.lower()
print("lignes brutes :", n0, "| après doublons :", n1, "| après commandes de test :", len(site))
print("statuts normalisés :", site["statut"].value_counts().to_dict())
```
<!--sortie-->
```text
lignes brutes : 6259 | après doublons : 6138 | après commandes de test : 6078
statuts normalisés : {'paid': 5897, 'cancelled': 181}
```

**Lecture.** 6 259 lignes brutes, 6 138 après suppression des 121 répétitions, 6 078 après retrait des 60 commandes de test. Les trois écritures du statut (`paid`, `PAID`, `Paid`) se ramènent à un seul statut `paid` ; il reste 181 commandes annulées.

```python
def en_nombre(t):
    return float(t.replace("€", "").replace(" ", "").strip().replace(" ", "").replace(",", "."))

site["total_num"] = site["total"].map(en_nombre)
site["date"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False).str.replace("T", " "))
avant = site.loc[site["date"] < "2025-09-15", "total_num"]
apres = site.loc[site["date"] >= "2025-09-15", "total_num"]
print("total moyen avant le 15/09 :", round(avant.mean(), 2), "| après :", round(apres.mean(), 2), "| rapport :", round(apres.mean() / avant.mean(), 1))
```
<!--sortie-->
```text
total moyen avant le 15/09 : 103.3 | après : 9913.89 | rapport : 96.0
```


Le montant moyen **est multiplié par cent** à partir du 15 septembre : ce n'est pas un miracle commercial, c'est un **changement d'unité** (centimes) non annoncé. On le corrige **à partir de la date de rupture**, puis on vérifie que la distribution redevient continue.

```python
site.loc[site["date"] >= "2025-09-15", "total_num"] /= 100
print("total moyen avant :", round(site.loc[site["date"] < "2025-09-15", "total_num"].mean(), 2), "| après correction :", round(site.loc[site["date"] >= "2025-09-15", "total_num"].mean(), 2))
site["id_commande"] = site["order_ref"].str[4:].astype(int)
site["annulee"] = site["statut"].eq("cancelled")
print("commandes du site après nettoyage :", len(site), "| dont annulées :", int(site["annulee"].sum()), "| somme :", round(site["total_num"].sum(), 2))
```
<!--sortie-->
```text
total moyen avant : 103.3 | après correction : 99.14
commandes du site après nettoyage : 6078 | dont annulées : 181 | somme : 617715.45
```

**Lecture.** Le montant moyen d'une commande est de 103,30 € avant le 15 septembre et de 9 913,89 € après : un rapport de 96. Divisé par cent à partir de cette date, il devient 99,14 €, cohérent avec les mois précédents. Il reste 6 078 commandes, dont 181 annulées, pour 617 715,45 € avant exclusion des annulations.

### P.6 Étape 5 : réconcilier avec la base

Avec la base, on construit l'« escalier des écarts » : on part du chiffre d'affaires de la base pour le canal Site et l'on retrouve celui de l'export, étape par étape (livre, 3.3).

```python
base_site = base[base["canal"] == "Site"].groupby("id_commande")["montant"].sum().round(2)
ca_base_site = base_site.sum()
m = site.set_index("id_commande")["total_num"].round(2)
joint = pd.concat([m.rename("export"), base_site.rename("base")], axis=1)
print("commandes en base :", len(base_site), "| dans l'export nettoyé :", len(m), "| clés communes :", int(joint.dropna().shape[0]))
print("écart maximal par commande :", round((joint["export"] - joint["base"]).abs().max(), 2))
annule = site.loc[site["annulee"], "total_num"].sum()
print("CA base :", round(ca_base_site, 2), "| export nettoyé :", round(m.sum(), 2), "| dont annulations :", round(annule, 2), "| export hors annulations :", round(m.sum() - annule, 2))
```
<!--sortie-->
```text
commandes en base : 6078 | dans l'export nettoyé : 6078 | clés communes : 6078
écart maximal par commande : 0.0
CA base : 617715.45 | export nettoyé : 617715.45 | dont annulations : 17551.32 | export hors annulations : 600164.13
```

**Lecture.** Les 6 078 commandes du site se retrouvent dans la base, **à l'euro près** (écart maximal par commande nul). La différence de 17 551,32 € entre la base et le chiffre d'affaires « hors annulations » (600 164,13 €) n'est pas une erreur : c'est la valeur des 181 commandes annulées, que la base compte et que la plateforme exclut.

```python
ca_canal = base.groupby("canal")["montant"].sum()
print("part du chiffre d'affaires 2025 de la base, par canal (%) :", (ca_canal / ca_canal.sum() * 100).round(1).to_dict())
```
<!--sortie-->
```text
part du chiffre d'affaires 2025 de la base, par canal (%) : {'Boutique': 42.3, 'Réseaux': 11.0, 'Site': 46.6}
```

Un contrôle de **couverture** : les deux exports ne couvrent que deux canaux sur trois. Le canal Réseaux, qui pèse environ un neuvième du chiffre d'affaires, n'est dans aucun fichier : on ne peut donc **pas** retrouver le chiffre d'affaires total de la comptable avec ces sources, et il faudra le dire.

Les deux sources **concordent commande par commande** une fois les doublons, les tests et l'unité traités. Reste une **décision**, pas un écart : la base compte les commandes annulées comme des ventes, la plateforme les marque « annulées ». Quel est le chiffre d'affaires de la gérante ? La réponse dépend de la définition, qu'il faut **écrire** (livre, 4.2) ; ici, une commande annulée n'est pas une vente.

### P.7 Étape 6 : assembler la table unique

On met les deux canaux au **même grain** (une ligne par commande) et aux **mêmes colonnes** (livre, 2.2 et 2.3).

```python
c_caisse = propre.groupby("id_commande").agg(date=("date", "first"), montant=("montant_net", "sum"), lignes=("article", "size"),
                                              reconstitue=("montant_reconstitue", "max")).reset_index()
c_caisse["canal"], c_caisse["source"] = "Boutique", "caisse"
c_site = site[~site["annulee"]][["id_commande", "date", "total_num"]].rename(columns={"total_num": "montant"})
c_site["date"] = c_site["date"].dt.normalize()
c_site["canal"], c_site["source"], c_site["reconstitue"] = "Site", "site", False
ventes = pd.concat([c_caisse, c_site[c_caisse.columns.drop("lignes")]], ignore_index=True)
ventes["montant"] = ventes["montant"].round(2)
ventes["mois"] = ventes["date"].dt.to_period("M").astype(str)
print(ventes.groupby("canal").agg(commandes=("id_commande", "nunique"), ca=("montant", "sum")).round(2))
print("clés uniques :", ventes["id_commande"].is_unique, "| lignes :", len(ventes))
```
<!--sortie-->
```text
          commandes         ca
canal                         
Boutique       5442  561154.69
Site           5897  600164.13
clés uniques : True | lignes : 11339
```

**Lecture.** La table compte 11 339 commandes : 5 442 pour la Boutique (561 154,69 €) et 5 897 pour le Site (600 164,13 €), avec des clés uniques.

### P.8 Étape 7 : les contrôles

Une table livrée sans contrôle est une table **qu'on espère** juste. On écrit des contrôles qui **échouent bruyamment** : `pandera` pour le schéma (type, plage, unicité), et des contrôles de totaux contre les sources (livre, 3.2 et 3.5).

```python
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "id_commande": pa.Column(int, unique=True),
    "date": pa.Column("datetime64[us]", pa.Check.in_range(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"))),
    "montant": pa.Column(float, pa.Check.in_range(0.01, 5000)),
    "canal": pa.Column(str, pa.Check.isin(["Boutique", "Site"])),
}, coerce=True)
try:
    schema.validate(ventes[["id_commande", "date", "montant", "canal"]], lazy=True)
    print("schéma pandera : OK")
except pa.errors.SchemaErrors as e:
    print("échecs de schéma :", len(e.failure_cases))
```
<!--sortie-->
```text
schéma pandera : OK
```

```python
ca_attendu_site = base_site.sum() - annule
ca_attendu_boutique = base_boutique.sum()
verif = {"clés uniques": ventes["id_commande"].is_unique,
         "Site = base hors annulations (à 1 centime)": abs(ventes.loc[ventes["canal"] == "Site", "montant"].sum() - ca_attendu_site) < 0.01,
         "Boutique = total affiché par la caisse (à 0,1 %)": abs(ventes.loc[ventes["canal"] == "Boutique", "montant"].sum() - controle["total_affiche"].sum()) < 0.001 * controle["total_affiche"].sum(),
         "aucune vente de plus de 5 000 €": bool((ventes["montant"] < 5000).all()),
         "douze mois présents": ventes["mois"].nunique() == 12}
for k, v in verif.items():
    print("OK  " if v else "KO  ", k)
```
<!--sortie-->
```text
OK   clés uniques
OK   Site = base hors annulations (à 1 centime)
OK   Boutique = total affiché par la caisse (à 0,1 %)
OK   aucune vente de plus de 5 000 €
OK   douze mois présents
```

### P.9 Étape 8 : le journal et le dictionnaire

Le journal est **déjà écrit** pendant le nettoyage ; on le complète et on le range en tableau. Le dictionnaire se **génère** à partir de la table, puis on y ajoute à la main ce que la machine ne sait pas (définitions, unités, règles) (livre, 4.1 et 4.2).

```python
noter("export du site lu", pd.DataFrame({"montant_net": site["total_num"]}), "doublons, tests retirés ; montants en euros (unité corrigée après le 15/09)")
noter("table des ventes", ventes.rename(columns={"montant": "montant_net"}), "caisse + site hors annulations, une ligne par commande")
print(pd.DataFrame(journal).to_string(index=False))
```
<!--sortie-->
```text
                   etape  lignes      somme                                                                        note
              caisse lue   12678  564472.59             douze fichiers, montants vides reconstitués par quantité x prix
doublons de scan retirés   12610  561154.69                68 lignes dont le montant égale exactement l'écart du ticket
       export du site lu    6078  617715.45 doublons, tests retirés ; montants en euros (unité corrigée après le 15/09)
        table des ventes   11339 1161318.82                      caisse + site hors annulations, une ligne par commande
```

```python
descriptions = {"id_commande": "Numéro de commande (clé unique, commun à la caisse, au site et à la base)", "date": "Date de la commande (jour)",
                "montant": "Montant TTC en euros, remises déduites", "lignes": "Nombre de lignes d'achat (caisse seulement)",
                "reconstitue": "Vrai si un montant de ligne a été reconstitué par quantité x prix", "canal": "Boutique ou Site", "source": "Fichier d'origine : caisse ou site",
                "mois": "Mois de la commande (AAAA-MM)"}
dico = pd.DataFrame({"colonne": ventes.columns, "type": [str(t) for t in ventes.dtypes], "manquants": ventes.isna().sum().values,
                     "distincts": ventes.nunique().values, "description": [descriptions[c] for c in ventes.columns]})
print(dico.to_string(index=False))
```
<!--sortie-->
```text
    colonne           type  manquants  distincts                                                               description
id_commande          int64          0      11339 Numéro de commande (clé unique, commun à la caisse, au site et à la base)
       date datetime64[us]          0        365                                                Date de la commande (jour)
    montant        float64          0       2606                                    Montant TTC en euros, remises déduites
     lignes        float64       5897          8                               Nombre de lignes d'achat (caisse seulement)
reconstitue           bool          0          2         Vrai si un montant de ligne a été reconstitué par quantité x prix
      canal            str          0          2                                                          Boutique ou Site
     source            str          0          2                                        Fichier d'origine : caisse ou site
       mois            str          0         12                                             Mois de la commande (AAAA-MM)
```

### P.10 Étape 9 : juger, puis ouvrir la correction

On fixe les critères de livraison **avant** d'ouvrir les fichiers de vérité, puis on mesure ce qui reste (livre, 3.4).

```python
vs = pd.read_csv("donnees/verite_site.csv"); vc = pd.read_csv("donnees/verite_caisse.csv")
vrai_site = vs[vs["defaut"].fillna("") == ""].drop_duplicates("order_ref")
ca_vrai_boutique = base_boutique.sum()
ca_boutique = ventes.loc[ventes["canal"] == "Boutique", "montant"].sum()
retirees = caisse.loc[caisse["doublon_scan"], ["fichier", "numero_ligne"]].merge(vc, left_on=["fichier", "numero_ligne"], right_on=["fichier", "numero_ligne_fichier"], how="left")
print("doublons de scan réels :", int(vc["est_doublon"].sum()), "| lignes retirées :", len(retirees), "| dont vraies doublons :", int(retirees["est_doublon"].sum()))
print("CA Boutique : table", round(ca_boutique, 2), "| vérité", round(ca_vrai_boutique, 2), "| écart", round(ca_boutique - ca_vrai_boutique, 2))
print("CA Site : table", round(ventes.loc[ventes["canal"] == "Site", "montant"].sum(), 2), "| vérité hors annulations", round(vrai_site["total_vrai"].sum(), 2))
```
<!--sortie-->
```text
doublons de scan réels : 67 | lignes retirées : 68 | dont vraies doublons : 67
CA Boutique : table 561154.69 | vérité 560973.91 | écart 180.78
CA Site : table 600164.13 | vérité hors annulations 600164.13
```

**Lecture.** Le chiffre d'affaires du Site est **exact** (écart nul). Celui de la Boutique est supérieur de 180,78 € (0,03 %) à la vérité. Deux causes, que l'on peut chiffrer : les 398 montants reconstitués par quantité × prix ignorent les remises de janvier à septembre (+241,68 € au total), et une ligne de 60,90 € (une « Jardinière design » du ticket 34537) a été retirée à tort, car elle ressemblait à un doublon (−60,90 €) : $241{,}68-60{,}90=180{,}78$. Sur 67 doublons de scan réels, la règle en a retiré 67 (et une de trop).

```python
criteres = {"clés uniques": verif["clés uniques"], "Site égal à la base hors annulations": verif["Site = base hors annulations (à 1 centime)"],
            "écart Boutique inférieur à 0,1 % du chiffre d'affaires": abs(ca_boutique - ca_vrai_boutique) < 0.001 * ca_vrai_boutique,
            "au moins 95 % des lignes retirées sont de vrais doublons": retirees["est_doublon"].sum() >= 0.95 * len(retirees),
            "journal et dictionnaire produits": len(journal) >= 3 and len(dico) == len(ventes.columns)}
for k, v in criteres.items():
    print("OK  " if v else "KO  ", k)
print("\nDécision :", "LIVRER la table, avec le rapport d'écarts" if all(criteres.values()) else "NE PAS LIVRER : revoir le nettoyage")
```
<!--sortie-->
```text
OK   clés uniques
OK   Site égal à la base hors annulations
OK   écart Boutique inférieur à 0,1 % du chiffre d'affaires
OK   au moins 95 % des lignes retirées sont de vrais doublons
OK   journal et dictionnaire produits

Décision : LIVRER la table, avec le rapport d'écarts
```

> ✅ **À retenir.** Une table propre n'est pas une table « corrigée » : c'est une table dont on connaît **chaque transformation**, dont les **totaux** s'accordent avec une source de référence, et dont les **écarts résiduels** sont écrits. Le nettoyage est fini quand on peut **expliquer** les chiffres, pas quand ils « ont l'air bons ».

### P.11 Les limites de l'étude

- **Une base de référence qui est elle-même une source.** Ici, la base concorde avec les deux exports une fois nettoyés ; dans la réalité, c'est la **réconciliation** qui décide laquelle des sources est la plus fiable.
- **Remises avant octobre.** Les fichiers de caisse de janvier à septembre ne contiennent pas la remise : un montant reconstitué par quantité × prix **ignore** une éventuelle remise.
- **Un canal absent.** Le canal Réseaux (environ 11 % du chiffre d'affaires de 2025 dans la base) n'est exporté par aucun des deux fichiers : la table unique ne couvre que deux canaux sur trois, et le chiffre d'affaires qu'elle donne **ne peut pas** être comparé tel quel à celui de la comptable. Un contrôle de couverture (quels canaux, quelle part du total de la base) fait partie de toute réconciliation.
- **Annulations.** La décision « une annulation n'est pas une vente » dépend de la définition comptable de la boutique, pas d'une règle de nettoyage.
- **Pas de rapprochement des clients.** La table est au grain de la commande ; relier les commandes au CRM suppose le rapprochement flou du chapitre 2 (section 2.5).
- **Données simulées.** Les erreurs injectées sont plus propres que celles de la réalité (typographies, fichiers corrompus, changements non documentés).

### P.12 Variante : dédoublonner le CRM

La même démarche s'applique au CRM (`donnees/crm_clients.csv`, 140 lignes de test, 1 000 doublons) : **normaliser**, **rapprocher**, **juger** par précision et rappel. Version courte avec `rapidfuzz` (livre, 2.5).

```python
from unidecode import unidecode

crm = pd.read_csv("donnees/crm_clients.csv", dtype=str)
crm = crm[crm["email"].fillna("") != "test@example.com"].copy()
simple = lambda s: re.sub(r"[^a-z]", "", unidecode(str(s)).lower())
valide = crm["email"].str.contains(r"^[^@\s]+@[^@\s]+\.[a-z]+$", na=False, case=False)
cles = {"e-mail": crm["email"].str.strip().str.lower().where(valide),
        "nom + initiale + année": crm["nom"].map(simple) + "|" + crm["prenom"].map(lambda s: simple(s)[:1]) + "|" + crm["date_naissance"].fillna("").str[-4:]}
def paires(cle):
    g = crm.assign(k=cle).dropna(subset=["k"]).groupby("k")["id_crm"].apply(list)
    return {(a, b) for liste in g if len(liste) > 1 for i, a in enumerate(liste) for b in liste[i + 1:]}
vcrm = pd.read_csv("donnees/verite_crm.csv", dtype={"id_crm": str}); vcrm = vcrm[vcrm["id_client"] >= 0]
vrai = vcrm.set_index("id_crm")["id_client"]
n_vraies = int(vcrm.groupby("id_client").size().pipe(lambda s: (s * (s - 1) / 2).sum()))
resultats = {nom: paires(c) for nom, c in cles.items()}
resultats["union"] = resultats["e-mail"] | resultats["nom + initiale + année"]
for nom, p in resultats.items():
    bons = sum(vrai[a] == vrai[b] for a, b in p)
    print(f"{nom:24s} paires {len(p):4d} | précision {bons / len(p):.3f} | rappel {bons / n_vraies:.3f}")
```
<!--sortie-->
```text
e-mail                   paires  698 | précision 0.994 | rappel 0.661
nom + initiale + année   paires  462 | précision 0.916 | rappel 0.403
union                    paires  878 | précision 0.951 | rappel 0.795
```

**Lecture.** Il existe 1 050 paires réelles de doublons. L'**e-mail** est très précis (99,4 %) mais ne retrouve que 66 % des paires, car l'adresse est parfois absente ou modifiée ; la clé « nom + initiale + année » en retrouve 40 % avec 92 % de précision. Leur **union** gagne en rappel (79,5 %) en perdant un peu de précision (95,1 %). Pour aller plus loin (fautes de frappe, inversion du nom et du prénom), il faut une mesure de similarité et des seuils : c'est le sujet de la section 2.5.


## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des sections facultatives (➕ 1.5, 1.6, 2.4, 2.5, 3.4, 3.5, 4.3 et chapitre 5) comptent si vous les avez lues.

### Nettoyage des données (chapitre 1)

1. Le revenu manque plus souvent chez les moins de 30 ans ; la satisfaction manque plus souvent quand elle est basse ; la dépense manque au hasard pour 5 % des clients. Nommez le mécanisme de chaque absence (MCAR, MAR, MNAR) et dites ce que cela change à une suppression des lignes incomplètes.
2. Un montant vaut 9999 dans trois lignes sur 6 000. Que représente probablement ce nombre, et quel est l'effet sur la moyenne de trois valeurs 20, 30 et 9999 ?
3. Pourquoi une valeur aberrante n'est-elle pas toujours une erreur ? Citez trois façons de la repérer.
4. Une caisse contient 154 lignes identiques à une autre ligne du même ticket. Peut-on les supprimer d'un `drop_duplicates` ? Que faire ?
5. Le montant moyen d'une commande du site passe de 103,30 € à 9 913,89 € au 15 septembre. Quelle est l'explication la plus probable, comment la confirmer et comment corriger ?
6. Une date s'écrit `03/04/2025`. Est-ce le 3 avril ou le 4 mars ? Comment lever le doute ?
7. La colonne « ville » contient `Ville A`, `VILLE A`, `ville a`, `Vile A`, `Ville A.` et `المدينة أ`. Quelles écritures une normalisation simple (casse, espaces, point) corrige-t-elle, et lesquelles demandent une table de correspondance ?
8. Le texte `Ã©tÃ©` apparaît dans un fichier. D'où vient cette erreur et comment la corriger ?
9. On remplace tous les revenus manquants par la moyenne. Quel est l'effet sur la moyenne et sur la dispersion ? Cette méthode répare-t-elle une absence de type MNAR ?

### Transformation et fusion (chapitre 2)

10. Joindre 12 678 lignes de caisse à un catalogue de produits **sur le nom** donne 25 356 lignes. Que s'est-il passé, comment le détecter avant de sommer, et comment corriger ?
11. Citez deux contrôles à faire **avant** et **après** une jointure.
12. Douze fichiers de caisse n'ont pas le même format. Comment les empiler sans erreur ?
13. Un article à 50 € TTC (TVA à 20 %) coûte 22 € à l'achat. Quelle est sa marge brute hors taxe, et le taux de marge ?
14. Quelle est la différence entre `cut` et `qcut` ?
15. On passe du grain « ligne de commande » au grain « commande ». Quelle vérification garantit que rien n'a été perdu ?
16. Dans le tableur de stocks, les cellules contiennent `ND`, `—`, `rupture` et `28 ` (avec un espace). Comment passer à un tableau propre (une ligne, un produit, un mois) ?
17. Le nom `Dormar` est saisi `Dorrmar`. Quelle est la distance de Levenshtein, et quel score de ressemblance (0 à 100) donne `fuzz.ratio` ? Pourquoi ne pas fusionner automatiquement au-dessus d'un seuil unique ?

### Qualité et réconciliation (chapitre 3)

18. Donnez un indicateur chiffré pour chacune des quatre dimensions : exactitude, complétude, cohérence, actualité.
19. Qu'est-ce qu'un contrôle « qui renvoie ses échecs », et pourquoi est-ce plus utile qu'un simple oui/non ?
20. Expliquez la méthode de réconciliation en trois temps.
21. La base compte 181 commandes de plus que la plateforme (17 551,32 €). Est-ce une erreur ? Que faut-il décider ?
22. Une tolérance de 0,1 % s'applique à un total de 560 973,91 €. À partir de quel écart absolu un contrôle échoue-t-il ? Un écart de 180,78 € est-il toléré ?
23. Comment trie-t-on un rapport d'exceptions pour agir d'abord là où il y a le plus à gagner ?
24. Quand choisir pandera, Great Expectations ou de simples fonctions ?
25. Une colonne est « complète à 100 % » : toutes ses cellules sont remplies de `N/A`. Que montre cet exemple sur les indicateurs de qualité ?

### Documentation (chapitre 4)

26. Que doit contenir la fiche d'un jeu de données ? Citez six éléments.
27. Un journal de nettoyage indique : 7 140 lignes lues, 140 tests retirés, 677 doublons retirés, 6 323 lignes restantes. Pourquoi y consigner les effectifs avant et après chaque étape ?
28. Le chiffre d'affaires du Site au quatrième trimestre donne 211 434 € d'un côté et 176 195 € de l'autre. Quelle est l'explication la plus simple, et que faut-il écrire pour éviter la confusion ?
29. Que contient un dictionnaire de données, et comment vérifie-t-on automatiquement qu'il n'est pas périmé ?
30. « Client actif » donne 2 654, 3 148 ou 3 875 selon la définition. Que faire ?
31. Une empreinte (hachage) de fichier prouve-t-elle que les données sont **correctes** ?
32. Que signifie « refaire depuis le brut », et pourquoi est-ce la meilleure documentation ?

### Confidentialité (chapitre 5)

33. Classez en identifiant direct, quasi-identifiant ou donnée sensible : adresse électronique, année de naissance, ville, état de santé, numéro de client.
34. Citez trois principes communs aux cadres de protection des données.
35. Un hachage sans clé des adresses électroniques protège-t-il les personnes ? Que fait une clé secrète en plus ?
36. Une donnée pseudonymisée est-elle anonyme ?
37. Un tableau compte quatre groupes de 3, 2, 5 et 4 personnes sur les quasi-identifiants. Quel est son k-anonymat, et que faire pour atteindre k = 5 ?
38. Pourquoi 26 % de clients « uniques » sur ville, année de naissance, canal et carte posent-ils problème ?
39. Peut-on publier un tableau où l'on masque les petits effectifs, mais avec les totaux de ligne et de colonne ?
40. En confidentialité différentielle, avec un bruit de Laplace d'échelle $1/\varepsilon$, quelle est l'erreur médiane pour $\varepsilon=0{,}1$ et pour $\varepsilon=1$ ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np, pandas as pd
from unidecode import unidecode
import ftfy
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

print("Q2  moyenne de 20, 30, 9999 :", round(np.mean([20, 30, 9999]), 1), "| sans le placeholder :", np.mean([20, 30]))
print("Q8  réparation du mojibake :", ftfy.fix_text("Ã©tÃ©"), "|", "été".encode("utf-8").decode("cp1252"))
print("Q13 marge hors taxe :", round(50 / 1.2 - 22, 2), "| taux de marge :", round((50 / 1.2 - 22) / (50 / 1.2) * 100, 1), "%")
print("Q17 Levenshtein :", Levenshtein.distance("Dormar", "Dorrmar"), "| fuzz.ratio :", round(fuzz.ratio("Dormar", "Dorrmar"), 1))
print("Q22 seuil de tolérance :", round(0.001 * 560973.91, 2), "€ | 180,78 € toléré :", 180.78 < 0.001 * 560973.91)
print("Q28 TTC -> HT :", round(211433.79 / 1.2, 2))
groupes = pd.Series([3, 2, 5, 4], index=list("ABCD"))
print("Q37 k-anonymat :", groupes.min(), "| groupes à supprimer ou fusionner pour k = 5 :", list(groupes[groupes < 5].index))
print("Q40 erreur médiane de Laplace : eps = 0,1 ->", round(np.log(2) / 0.1, 2), "| eps = 1 ->", round(np.log(2) / 1, 2))
```
<!--sortie-->
```text
Q2  moyenne de 20, 30, 9999 : 3349.7 | sans le placeholder : 25.0
Q8  réparation du mojibake : été | Ã©tÃ©
Q13 marge hors taxe : 19.67 | taux de marge : 47.2 %
Q17 Levenshtein : 1 | fuzz.ratio : 92.3
Q22 seuil de tolérance : 560.97 € | 180,78 € toléré : True
Q28 TTC -> HT : 176194.83
Q37 k-anonymat : 2 | groupes à supprimer ou fusionner pour k = 5 : ['A', 'B', 'D']
Q40 erreur médiane de Laplace : eps = 0,1 -> 6.93 | eps = 1 -> 0.69
```

**1.** Revenu manquant selon l'âge : **MAR** (l'absence dépend d'une variable observée). Satisfaction manquante quand elle est basse : **MNAR** (l'absence dépend de la valeur elle-même). Dépense manquante au hasard : **MCAR**. Supprimer les lignes incomplètes ne biaise que dans le cas MCAR ; en MAR et MNAR, la suppression **déforme** la population (par exemple moins de jeunes, moins de clients mécontents) (1.1.3, 1.1.4).

**2.** 9999 est un **code spécial** (un « placeholder » de saisie), pas un montant. La moyenne de 20, 30 et 9999 vaut 3 349,7 contre 25 sans le code : un seul placeholder ruine la moyenne. On le remplace par une valeur manquante avant tout calcul (1.1.2).

**3.** Une valeur extrême peut être **réelle** (un très gros achat) : l'erreur se juge par la **règle métier** (un montant doit valoir quantité × prix), pas seulement par la distance à la moyenne. Trois façons de la repérer : la règle des **1,5 écart interquartile**, le **score z robuste** (médiane et MAD), et une **règle métier** ou un contrôle croisé avec une table de référence (1.2.1 à 1.2.3).

**4.** Non. Parmi ces 154 lignes identiques, la vérité en désigne 67 comme de vrais doubles scans et 87 comme des répétitions **légitimes** (deux articles identiques achetés ensemble). Un `drop_duplicates` aveugle supprimerait 87 vraies ventes. On compare avec une source de référence (le total du ticket) et l'on ne retire que ce que l'on peut prouver (1.3.3).

**5.** Un montant moyen multiplié par 96 d'un jour à l'autre n'est pas un miracle commercial : c'est un **changement d'unité** (centimes). On le confirme par la **rupture temporelle** (le saut est net au 15 septembre) et par le contrôle contre une source de référence ; on corrige en divisant par cent **à partir de la date de rupture**, ce qui ramène la moyenne à 99,14 € (1.4.2).

**6.** Sans autre information, c'est ambigu. On lève le doute avec la **source** (la plateforme écrit-elle jour/mois ?), avec les **autres valeurs de la colonne** (un `13/04/2025` ne peut pas être un mois), et en documentant le format retenu. Le mois et le jour ne se devinent jamais ligne par ligne sans règle (1.4.3).

**7.** La normalisation (casse, espaces, point final) ramène `VILLE A`, `ville a` et `Ville A.` à `Ville A`. La **faute** (`Vile A`) et l'écriture **arabe** ne se corrigent pas par une règle générale : il faut une **table de correspondance** vérifiée, qui est aussi une décision à documenter (1.4.4, 1.5.6).

**8.** Le texte a été écrit en **UTF-8** puis lu comme du **cp1252** : chaque caractère accentué devient deux caractères (c'est le « mojibake »). On le répare en relisant avec le bon encodage, ou avec une bibliothèque comme `ftfy` (code ci-dessus : `ftfy.fix_text("Ã©tÃ©")` rend « été ») (1.5.2, 1.5.5).

**9.** La moyenne reste inchangée, mais la **dispersion diminue** (on ajoute des valeurs toutes égales) et les corrélations sont atténuées. Une imputation ne répare pas un MNAR : si l'absence dépend de la valeur, aucune information des autres colonnes ne la contient. Dans nos données, après imputation, la part de clients très insatisfaits reste à 2,55 % contre 4,08 % en vérité (1.6.1, 1.6.4).

**10.** Deux produits portent le même nom : la jointure sur le nom **multiplie** les lignes (12 678 devient 25 356). On le détecte **avant de sommer** par le contrôle des effectifs (lignes avant et après) et par `validate="m:1"` ; on corrige en ajoutant une clé qui distingue les homonymes (ici le prix), puis en vérifiant les effectifs (2.2.2, 2.2.5).

**11.** **Avant** : la clé est-elle unique dans la table de droite, et quelle est la cardinalité attendue ? **Après** : le nombre de lignes est-il celui que l'on attend (inchangé pour une jointure n–1), et le total d'une colonne numérique est-il conservé ? (2.2.2).

**12.** Avec **une fonction de lecture paramétrée** par fichier (encodage, séparateur, décimale, noms de colonnes, format de date), appliquée aux douze fichiers, puis un `concat` ; chaque fichier est contrôlé contre sa propre ligne de total (2.2.3).

**13.** Prix hors taxe $=50/1{,}2\approx41{,}67$ € ; marge brute $=41{,}67-22=19{,}67$ € ; taux de marge $=19{,}67/41{,}67\approx47{,}2\ \%$ (code ci-dessus). On compare des montants hors taxe aux coûts hors taxe (2.1.2).

**14.** `cut` découpe selon des **bornes fixées** (classes de largeur choisie, par exemple des tranches d'âge) ; `qcut` découpe selon des **quantiles** (classes d'effectifs à peu près égaux) (2.1.4).

**15.** Une **somme de contrôle** : le total du montant au grain commande doit être égal au total au grain ligne, et le nombre de commandes distinctes doit rester le même (2.3.7).

**16.** On lit les cellules en texte, on convertit `ND` et `—` en valeurs **manquantes**, `rupture` en **zéro**, on retire les espaces avant de convertir, on supprime titres et sous-totaux, puis on **dépivote** les colonnes de mois en lignes (`melt`) (2.4.2).

**17.** La distance de Levenshtein vaut **1** (un caractère à ajouter) et `fuzz.ratio` donne 92,3 (code ci-dessus). Un seuil unique mélange deux erreurs de coût différent : fusionner deux personnes distinctes ne se rattrape pas, rater un doublon se corrige plus tard. On utilise donc **trois zones** : accepter, revoir à la main, rejeter (2.5.3, 2.5.5, 2.5.6).

**18.** Par exemple : **exactitude** : écart entre le total de la source et celui d'une référence ; **complétude** : part de cellules renseignées ; **cohérence** : part des lignes qui respectent une règle entre colonnes (inscription avant naissance) ; **actualité** : âge de la dernière donnée (jours depuis l'extraction) (3.1.2 à 3.1.6).

**19.** C'est une règle qui **renvoie les lignes en échec** (et non un simple booléen) : on voit **quoi** corriger et combien, on peut trier, compter et joindre les exceptions à un rapport (3.2.1, 3.2.6).

**20.** (1) **Comparer les effectifs** (mêmes lignes, mêmes clés ?) ; (2) **comparer les totaux** (même somme ?) ; (3) **expliquer l'écart ligne à ligne** jusqu'à zéro (doublons, unités, annulations, arrondis) (3.3.2).

**21.** Ce n'est pas une erreur de données : la base compte les commandes annulées comme des commandes, la plateforme les marque « annulées ». Il faut **décider** de la définition du chiffre d'affaires (commandé ou encaissé), puis l'**écrire** dans le dictionnaire (3.3.6).

**22.** Une tolérance de 0,1 % vaut 560,97 € ; **180,78 € est toléré** (code ci-dessus), mais l'écart reste consigné au rapport : une tolérance accepte un écart, elle ne l'efface pas (3.4.2).

**23.** On **trie par montant** (ou par effet sur le total) et l'on regroupe par **cause** : 5 exceptions qui représentent 80 % de l'écart passent avant 100 exceptions de quelques centimes (3.4.5).

**24.** Des **fonctions maison** suffisent pour une analyse ponctuelle ; **pandera** convient pour valider le schéma d'un DataFrame de façon déclarative dans le code ; **Great Expectations** vaut son poids pour un **pipeline récurrent** avec rapports partagés (3.5.5).

**25.** Un indicateur de complétude ne regarde que le **vide** : `N/A` est un texte rempli. Un indicateur ne remplace pas la **validité** et le regard sur les valeurs ; il se lit toujours avec les autres dimensions (3.1.8).

**26.** Par exemple : la **source** et le propriétaire, la **date d'extraction**, le **périmètre**, le **grain**, la **clé**, la **description des colonnes**, les **limites connues**, la **version** et la **licence ou les droits** (4.1.1).

**27.** Parce qu'un journal avec les effectifs permet de **vérifier chaque étape** (le nombre de lignes retirées est-il celui qu'on attend ?) et de **retrouver** une perte inexpliquée. Ici : $7\,140-140-677=6\,323$ ; on peut ensuite comparer à la vérité et voir que 674 des 677 retraits étaient de vrais doublons (4.1.3 à 4.1.5).

**28.** Le premier chiffre est **TTC**, le second **hors taxe** : $211\,433{,}79/1{,}2\approx176\,194{,}83$ (code ci-dessus). Il faut écrire dans le dictionnaire et sur le rapport la **définition** du montant (TTC ou HT, remises déduites ou non, période exacte) (4.2.6).

**29.** Pour chaque colonne : nom, libellé, type, unité, valeurs permises, caractère obligatoire, codage des manquants, exemple, règle de calcul, source et sensibilité. On le teste automatiquement en comparant ses colonnes, ses types et ses domaines à ceux du fichier réel : tout écart fait échouer le test (4.2.1, 4.2.5).

**30.** On ne choisit pas au hasard : on **écrit une définition unique** (par exemple « au moins une commande dans les 12 derniers mois ») dans le glossaire métier, on l'utilise partout, et l'on indique quelle définition correspond à quel chiffre publié (4.2.6).

**31.** Non : une empreinte prouve que le fichier est **identique** à celui que l'on a documenté, pas qu'il est **correct**. Elle protège contre les modifications silencieuses, pas contre les erreurs d'origine (4.3.4).

**32.** C'est disposer d'un script qui, à partir des **fichiers bruts** et d'une configuration, reproduit **sans retouche manuelle** les tables et les chiffres. Elle documente mieux que n'importe quelle description : si le script donne le même chiffre, la documentation est exacte (4.1.7, 4.3.8).

**33.** **Adresse électronique** : identifiant direct ; **numéro de client** : identifiant direct (indirect si la table de correspondance est séparée) ; **année de naissance** et **ville** : quasi-identifiants ; **état de santé** : donnée sensible (5.1.2).

**34.** Par exemple : la **finalité** (on collecte pour un usage déclaré), la **minimisation** (seulement ce qui sert), la **limitation de conservation**, la **sécurité**, le **consentement ou une autre base légale**, et les **droits des personnes** (5.1.3).

**35.** Non : les adresses se retrouvent par **dictionnaire** (on hache les adresses plausibles et l'on compare : 85,7 % retrouvées dans notre jeu). Une **clé secrète** (HMAC) conservée à part rend cette attaque impossible sans la clé, tout en gardant le même identifiant pour joindre des fichiers (5.2.2, 5.2.3).

**36.** Non : une donnée **pseudonymisée** reste personnelle puisque l'on peut en principe retrouver la personne (table de correspondance, recoupement). Seule une anonymisation irréversible sort du champ des données personnelles, et elle est difficile à garantir (5.2.5).

**37.** Le k-anonymat est la **plus petite taille de groupe** : **2** (le groupe B). Pour atteindre $k=5$, il faut **généraliser** (tranches d'âge, régions) ou **supprimer** les lignes des groupes A (3), B (2) et D (4), jusqu'à ce que chaque groupe compte au moins cinq personnes (code ci-dessus) (5.3.2, 5.3.3).

**38.** Une personne **unique** sur ces quatre colonnes est identifiable par quiconque connaît ces quatre informations (par recoupement avec une autre source). Un quart de clients uniques signifie que la table, malgré l'absence de nom, **n'est pas anonyme** (5.3.1, 5.3.5).

**39.** Non, pas sans précaution : si l'on publie aussi les totaux de lignes et de colonnes, on peut **retrouver les cases masquées par soustraction** (dans notre exemple, toutes les valeurs masquées sont retrouvées). Il faut un masquage complémentaire ou ne pas publier les totaux détaillés (5.4.2).

**40.** L'erreur médiane vaut $\ln 2/\varepsilon$ : environ **6,93** pour $\varepsilon=0{,}1$ et **0,69** pour $\varepsilon=1$ (code ci-dessus) : plus la protection est forte (ε petit), plus le comptage est bruité (5.3.7).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Repérer et traiter des valeurs manquantes selon leur mécanisme | 1.1 |
| Distinguer valeur aberrante et erreur, choisir une règle | 1.2 |
| Détecter et traiter doublons exacts et flous | 1.3 |
| Corriger formats, unités, dates, catégories, schémas | 1.4 |
| Nettoyer texte, encodage et dates (➕) | 1.5 |
| Imputer et en mesurer l'impact (➕) | 1.6 |
| Dériver des variables et les documenter | 2.1 |
| Joindre sans multiplier les lignes, empiler des fichiers | 2.2 |
| Agréger et changer de grain avec contrôle | 2.3 |
| Passer du large au long, lire un tableur désordonné (➕) | 2.4 |
| Rapprocher des enregistrements approximativement (➕) | 2.5 |
| Mesurer la qualité selon plusieurs dimensions | 3.1 |
| Écrire des contrôles de validation | 3.2 |
| Réconcilier deux sources et expliquer les écarts | 3.3 |
| Régler des tolérances et un rapport d'exceptions (➕) | 3.4 |
| Utiliser pandera ou Great Expectations (➕) | 3.5 |
| Documenter un jeu de données et ses transformations | 4.1 |
| Construire et tester un dictionnaire de données | 4.2 |
| Tracer le lignage et rejouer un chiffre (➕) | 4.3 |
| Pseudonymiser, anonymiser, mesurer un risque de réidentification | 5.1 à 5.4 |
| Mener un nettoyage et une réconciliation de bout en bout | Projet du volume |
