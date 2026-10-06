# Chapitre 5 : Ingénierie des données — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 5 du livre. Les **applications** refont pas à pas ce que le livre a résumé : un ETL complet, sa version en SQL, le chargement incrémental, les règles de qualité, le contrat de données, la réconciliation des produits et des clients, le lignage et la pseudonymisation, puis la collecte sur un site local. Les **exercices** (à la main d'abord, puis avec du code) sont corrigés à la fin. Données : les quatre exports bruts de `donnees/sources/` (commandes, CRM, catalogue, fournisseur) et leurs fichiers de vérité (`verite_*.csv`). Prérequis : les sections 5.1 à 5.5 du livre, selon l'exercice.

## Préparation

Une seule cellule charge les données brutes **comme du texte** (on ne laisse pas la bibliothèque deviner) et les fonctions du chapitre, rangées dans `build/outils_ch05.py` : lecture, typage des commandes, motifs de rejet, normalisation des libellés, serveur local de démonstration, journal de lignage. Les applications s'en servent.

```python
import os, sys, re, hashlib, hmac, time, tempfile, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import duckdb
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein, JaroWinkler
from outils_ch05 import *

brut = lire("commandes_export")
crm = lire("clients_crm"); crm["id_crm"] = crm["id_crm"].astype(int)
catalogue = lire("produits_catalogue"); catalogue["prix_catalogue"] = catalogue["prix_catalogue"].astype(float)
fournisseur = lire("produits_fournisseur"); fournisseur["prix_achat"] = fournisseur["prix_achat"].astype(float)
clients_connus, produits_connus = set(crm["id_crm"]), set(catalogue["id_produit"])
TMP = tempfile.mkdtemp(prefix="cah05_", dir=os.environ.get("TMPDIR"))        # fichiers intermédiaires, supprimés à la fin
print({"commandes": len(brut), "crm": len(crm), "catalogue": len(catalogue), "fournisseur": len(fournisseur)})
```
<!--sortie-->
```text
{'commandes': 19700, 'crm': 5000, 'catalogue': 48, 'fournisseur': 40}
```

## Applications

### Application 5.1 — Un ETL pas à pas (sections 5.1.2 à 5.1.5)

**Objectif.** Transformer les 19 700 lignes de commandes brutes en une table propre, en rendant compte de **chaque** ligne écartée.

**Étape 1 : extraire sans deviner, puis regarder ce qu'on a lu.** On garde tout en texte et l'on ajoute des métadonnées de chargement. Un premier profil montre les formats rencontrés.

```python
lu = brut.copy()
lu["_charge_le"] = "2025-12-31"
lu["_fichier"] = "commandes_export.csv"
format_date = lu["date"].map(lambda s: "AAAA-MM-JJ" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)
                             else "JJ/MM/AAAA" if "/" in s else "MM-JJ-AAAA")
print(format_date.value_counts().to_string())
print("prix avec virgule décimale :", int(lu["prix_unitaire"].str.contains(",").sum()))
```
<!--sortie-->
```text
date
AAAA-MM-JJ    11786
JJ/MM/AAAA     5897
MM-JJ-AAAA     2017
prix avec virgule décimale : 5824
```

Trois formats de date coexistent (59,8 % au format ISO, 29,9 % `JJ/MM/AAAA`, 10,2 % `MM-JJ-AAAA`) et près d'un prix sur trois (5 824 lignes) utilise la virgule décimale : une lecture « intelligente » aurait deviné autre chose pour chacun.

**Étape 2 : typer explicitement.** Le format `MM-JJ-AAAA` est ambigu (« 12-03-2025 » : 3 décembre ou 12 mars ?) : nous avons constaté, avec l'équipe de la caisse, qu'un tiret signale le format américain. Cette décision est **écrite** dans la fonction `parser_date`, pas dans la tête de quelqu'un.

```python
typ = typer_commandes(lu)
print(typ.dtypes.to_string())
print("dates illisibles :", int(typ["date"].isna().sum()), "| quantités manquantes :", int(typ["quantite"].isna().sum()))
```
<!--sortie-->
```text
id_commande               int64
date             datetime64[us]
id_client                 int64
id_produit                  str
quantite                float64
prix_unitaire           float64
_charge_le                  str
_fichier                    str
dates illisibles : 0 | quantités manquantes : 286
```

**Étape 3 : dédoublonner, puis rejeter avec un motif.** On compte à chaque étape pour pouvoir écrire l'équation de conservation.

```python
sans_doublon_exact = typ.drop_duplicates()
unique = sans_doublon_exact.drop_duplicates("id_commande")
motif = motif_rejet(unique, clients_connus, produits_connus)
propres_a = unique[motif.isna()]
rejets_a = unique[motif.notna()].assign(motif=motif[motif.notna()])
print("lignes lues", len(typ), "| doublons", len(typ) - len(unique), "| rejets", len(rejets_a), "| propres", len(propres_a))
print("conservation :", len(typ) - (len(typ) - len(unique)) - len(rejets_a) == len(propres_a))
print(rejets_a["motif"].value_counts().to_string())
```
<!--sortie-->
```text
lignes lues 19700 | doublons 1700 | rejets 782 | propres 17218
conservation : True
motif
client inconnu                334
quantité manquante            245
quantité négative ou nulle    203
```

L'équation est vérifiée : $19\,700-1\,700-782=17\,218$. Chacune des 782 lignes écartées a un **motif** : rien n'a disparu en silence.

**Étape 4 : tester.** Un test sur des cas écrits à la main, et deux garde-fous sur la table produite. Le dernier compare avec la fonction complète du chapitre.

```python
assert parser_date("03/12/2025") == pd.Timestamp("2025-12-03")
assert parser_date("12-03-2025") == pd.Timestamp("2025-12-03")
assert pd.isna(parser_date("3 décembre"))
assert propres_a["id_commande"].is_unique and (propres_a["quantite"] >= 1).all()
propres_b, rejets_b, stats = etl_commandes(brut, clients_connus, produits_connus)
assert propres_a.drop(columns=["_charge_le", "_fichier"]).reset_index(drop=True).equals(propres_b.drop(columns="montant").reset_index(drop=True))
print("tous les tests passent ;", stats)
```
<!--sortie-->
```text
tous les tests passent ; {'lignes_brutes': 19700, 'apres_doublons_exacts': 18000, 'apres_cle_unique': 18000, 'rejets': 782, 'propres': 17218}
```

> 💡 **À retenir.** Les 1 700 doublons exacts écartent **aussi** toutes les clés répétées : après typage, deux lignes de même `id_commande` sont identiques ligne à ligne (aucune ligne n'est en conflit avec elle-même). Si ce n'était pas le cas, il faudrait **choisir** laquelle garder, et le dire.

### Application 5.2 — La même transformation en SQL avec DuckDB (section 5.1.6)

**Objectif.** Écrire les règles du nettoyage en SQL, les exécuter là où se trouvent les données, et **vérifier** que le résultat est identique à celui de pandas.

**Étape 1 : charger le brut dans une table de staging.** DuckDB lit directement un DataFrame ; on déclare les trois tables dont les règles ont besoin.

```python
con = duckdb.connect()
con.register("staging_commandes", brut)
con.register("crm", crm[["id_crm"]])
con.register("catalogue", catalogue[["id_produit"]])
print(con.execute("SELECT count(*) AS lignes, count(DISTINCT id_commande) AS commandes FROM staging_commandes").df().to_string(index=False))
```
<!--sortie-->
```text
 lignes  commandes
  19700      18000
```

**Étape 2 : la requête de nettoyage.** Elle type, dédoublonne (`DISTINCT ON`), puis applique les règles de gestion. On y retrouve, ligne à ligne, les règles de la fonction Python.

```python
con.execute("""
CREATE TABLE propres_sql AS
WITH typees AS (
  SELECT CAST(id_commande AS INT) AS id_commande,
         CASE WHEN date LIKE '____-__-__' THEN strptime(date, '%Y-%m-%d')
              WHEN date LIKE '__/__/____' THEN strptime(date, '%d/%m/%Y')
              ELSE strptime(date, '%m-%d-%Y') END AS date,
         CAST(id_client AS INT) AS id_client, id_produit,
         CAST(quantite AS DOUBLE) AS quantite,
         CAST(replace(prix_unitaire, ',', '.') AS DOUBLE) AS prix_unitaire
  FROM staging_commandes),
uniques AS (SELECT DISTINCT ON (id_commande) * FROM typees)
SELECT *, round(quantite * prix_unitaire, 2) AS montant FROM uniques
WHERE quantite >= 1 AND prix_unitaire > 0
  AND id_client IN (SELECT id_crm FROM crm) AND id_produit IN (SELECT id_produit FROM catalogue)""")
print(con.execute("SELECT count(*) AS lignes, round(sum(montant), 2) AS ca FROM propres_sql").df().to_string(index=False))
```
<!--sortie-->
```text
 lignes        ca
  17218 893243.24
```

**Étape 3 : comparer les deux chemins.** Porter une transformation d'un outil à un autre se **teste** : on exige l'égalité, ligne à ligne, pas seulement sur le total.

```python
a = con.execute("SELECT * FROM propres_sql ORDER BY id_commande").df()
b = propres_b.sort_values("id_commande").reset_index(drop=True)
print("mêmes identifiants :", (a["id_commande"].to_numpy() == b["id_commande"].to_numpy()).all(),
      "| mêmes montants :", np.allclose(a["montant"].to_numpy(), b["montant"].to_numpy()))
```
<!--sortie-->
```text
mêmes identifiants : True | mêmes montants : True
```

**Étape 4 : un mart en SQL.** Le chiffre d'affaires mensuel par catégorie, que le tableau de bord de la gérante consomme.

```python
con.register("cat_complet", catalogue[["id_produit", "categorie"]])
mart = con.execute("""SELECT strftime(date_trunc('month', p.date), '%Y-%m') AS mois, c.categorie, round(sum(p.montant), 2) AS ca
                      FROM propres_sql p JOIN cat_complet c USING (id_produit)
                      GROUP BY 1, 2 ORDER BY 1, 2""").df()
print(mart.head(4).to_string(index=False)); print(len(mart), "lignes (12 mois × 4 catégories) ; total", round(mart["ca"].sum(), 2))
```
<!--sortie-->
```text
   mois categorie       ca
2025-01         A 18296.46
2025-01         B 18099.45
2025-01         C 20840.94
2025-01         D 18256.75
48 lignes (12 mois × 4 catégories) ; total 893243.24
```

### Application 5.3 — Un chargement incrémental idempotent (section 5.1.7)

**Objectif.** Charger les commandes propres **par lots**, rejouer un lot après un « incident », et comparer l'ajout naïf avec la fusion par clé.

**Étape 1 : trois lots par période.**

```python
propres_b["mois"] = propres_b["date"].dt.month
lots = {1: propres_b[propres_b["mois"] <= 4], 2: propres_b[propres_b["mois"].between(5, 8)], 3: propres_b[propres_b["mois"] >= 9]}
cols = ["id_commande", "date", "id_client", "id_produit", "quantite", "prix_unitaire", "montant"]
print({k: len(v) for k, v in lots.items()}, "total", sum(len(v) for v in lots.values()))
```
<!--sortie-->
```text
{1: 5611, 2: 5893, 3: 5714} total 17218
```

**Étape 2 : la fusion par clé (*upsert*).** La clé primaire déclare l'unicité ; `ON CONFLICT … DO UPDATE` met à jour au lieu de dupliquer.

```python
con.execute("CREATE TABLE cible (id_commande INT PRIMARY KEY, date TIMESTAMP, id_client INT, id_produit VARCHAR, quantite DOUBLE, prix_unitaire DOUBLE, montant DOUBLE)")
def charger(lot):
    con.register("lot", lot[cols])
    con.execute("""INSERT INTO cible SELECT * FROM lot ON CONFLICT (id_commande) DO UPDATE
                   SET quantite = excluded.quantite, prix_unitaire = excluded.prix_unitaire, montant = excluded.montant""")
    return con.execute("SELECT count(*) FROM cible").fetchone()[0]
print("après chaque lot :", [charger(lots[k]) for k in (1, 2, 3)])
print("après rejeu du lot 2, puis du lot 3 :", charger(lots[2]), charger(lots[3]))
```
<!--sortie-->
```text
après chaque lot : [5611, 11504, 17218]
après rejeu du lot 2, puis du lot 3 : 17218 17218
```

**Étape 3 : le même scénario avec l'ajout naïf.** Sans clé, `INSERT` ajoute tout ce qu'on lui donne.

```python
con.execute("CREATE TABLE naive AS SELECT * FROM (SELECT * FROM propres_sql LIMIT 0)")
for k in (1, 2, 2, 3):                                  # le lot 2 est rejoué
    con.register("lot", lots[k][cols]); con.execute("INSERT INTO naive (id_commande, date, id_client, id_produit, quantite, prix_unitaire, montant) SELECT * FROM lot")
print("ajout naïf avec rejeu :", con.execute("SELECT count(*) FROM naive").fetchone()[0], "lignes ; doublons de clé :",
      con.execute("SELECT count(*) - count(DISTINCT id_commande) FROM naive").fetchone()[0])
```
<!--sortie-->
```text
ajout naïf avec rejeu : 23111 lignes ; doublons de clé : 5893
```

**Étape 4 : une correction à la source.** Le lot 2 revient avec 50 prix corrigés (+3 %) ; la fusion doit **mettre à jour** ces lignes sans en ajouter.

```python
corrige = lots[2].copy()
idx = corrige.sample(50, random_state=1).index
corrige.loc[idx, "prix_unitaire"] = (corrige.loc[idx, "prix_unitaire"] * 1.03).round(2)
corrige["montant"] = (corrige["quantite"] * corrige["prix_unitaire"]).round(2)
avant = con.execute("SELECT sum(montant) FROM cible").fetchone()[0]
n = charger(corrige)
apres = con.execute("SELECT sum(montant) FROM cible").fetchone()[0]
attendu = corrige.loc[idx, "montant"].sum() - lots[2].loc[idx, "montant"].sum()
print("lignes :", n, "| variation du CA :", round(apres - avant, 2), "| attendue :", round(attendu, 2))
```
<!--sortie-->
```text
lignes : 17218 | variation du CA : 76.53 | attendue : 76.53
```

La table compte toujours **17 218** lignes, et son chiffre d'affaires varie de **76,53 €**, exactement la somme des écarts des 50 lignes corrigées. Le rejeu du lot 2 ne change rien (17 218 lignes) ; avec l'ajout naïf, le même scénario laisse 5 893 clés en double.

### Application 5.4 — Règles de qualité, score et seuils (sections 5.2.1 à 5.2.5)

**Objectif.** Écrire les règles comme des fonctions, calculer le taux de violation de chacune, un score par dimension, et décider selon une grille de seuils.

**Étape 1 : des règles qui renvoient « vrai si la ligne est fautive ».**

```python
def vide(d, col):                 return d[col].isna()
def hors_domaine(d, col, lo, hi): return d[col].notna() & ~d[col].between(lo, hi)
def repete(d, col):               return d.duplicated(col)
def orpheline(d, col, ref):       return ~d[col].isin(ref)

regles = [("complétude", "date renseignée", vide(typ, "date")), ("complétude", "quantité renseignée", vide(typ, "quantite")),
          ("complétude", "prix renseigné", vide(typ, "prix_unitaire")),
          ("validité", "quantité ≥ 1", hors_domaine(typ, "quantite", 1, 1e6)), ("validité", "prix dans ]0 ; 1 000]", hors_domaine(typ, "prix_unitaire", 0.01, 1000)),
          ("validité", "date dans 2025", hors_domaine(typ, "date", pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"))),
          ("unicité", "id_commande unique", repete(typ, "id_commande")),
          ("cohérence", "client connu", orpheline(typ, "id_client", clients_connus)), ("cohérence", "produit connu", orpheline(typ, "id_produit", produits_connus))]
bilan = pd.DataFrame([(d, r, int(m.sum()), round(100 * m.mean(), 2)) for d, r, m in regles], columns=["dimension", "règle", "violations", "taux (%)"])
print(bilan.to_string(index=False))
```
<!--sortie-->
```text
 dimension                 règle  violations  taux (%)
complétude       date renseignée           0      0.00
complétude   quantité renseignée         286      1.45
complétude        prix renseigné           0      0.00
  validité          quantité ≥ 1         226      1.15
  validité prix dans ]0 ; 1 000]           0      0.00
  validité        date dans 2025           0      0.00
   unicité    id_commande unique        1700      8.63
 cohérence          client connu         359      1.82
 cohérence         produit connu           0      0.00
```

**Étape 2 : un score global et un score par dimension.** Une ligne est conforme si elle ne viole **aucune** règle ; on cumule les violations avec un « ou » logique (ne pas additionner les taux : une ligne peut violer plusieurs règles).

```python
viol = np.column_stack([m.to_numpy() for _, _, m in regles]).any(axis=1)
par_dim = {d: round(float(100 * (1 - np.column_stack([m.to_numpy() for dd, _, m in regles if dd == d]).any(axis=1).mean())), 1) for d in dict.fromkeys(d for d, _, _ in regles)}
score = round(float(100 * (1 - viol.mean())), 1)
print("score global :", score, "|", par_dim)
print("somme des taux :", round(bilan["taux (%)"].sum(), 2), "% > taux de lignes touchées :", round(100 * viol.mean(), 2), "%")
```
<!--sortie-->
```text
score global : 87.4 | {'complétude': 98.5, 'validité': 98.9, 'unicité': 91.4, 'cohérence': 98.2}
somme des taux : 13.05 % > taux de lignes touchées : 12.6 %
```

**Étape 3 : la décision.**

```python
def decision(s):
    return "publier" if s >= 95 else "publier et alerter le propriétaire de la source" if s >= 85 else "arrêter le chargement"
print(score, "->", decision(score))
mois = typ["date"].dt.month
print("taux de lignes fautives par mois (%) :", (pd.Series(viol, index=typ.index).groupby(mois).mean() * 100).round(1).tolist())
```
<!--sortie-->
```text
87.4 -> publier et alerter le propriétaire de la source
taux de lignes fautives par mois (%) : [13.0, 13.6, 12.5, 11.7, 13.0, 11.9, 13.0, 13.6, 11.7, 13.4, 11.8, 12.1]
```

**Étape 4 : le profilage qui change la règle.** Quels identifiants se cachent derrière les « clients inconnus » ?

```python
inconnus = typ.loc[orpheline(typ, "id_client", clients_connus), "id_client"]
print(inconnus.value_counts().to_string())
sans_anonymes = orpheline(typ, "id_client", clients_connus | {999999})
print("violations de « client connu » en acceptant l'identifiant 999999 :", int(sans_anonymes.sum()))
```
<!--sortie-->
```text
id_client
999999    359
violations de « client connu » en acceptant l'identifiant 999999 : 0
```

Les 359 « clients inconnus » sont **un seul identifiant**, 999999, la valeur par défaut des ventes sans compte. Une fois ce cas reconnu comme légitime, la règle n'a plus aucune violation : la règle de qualité encodait une **décision métier** qu'il fallait expliciter.

### Application 5.5 — Un contrat de données exécutable (section 5.2.7)

**Objectif.** Écrire le contrat d'un export, le faire respecter à l'arrivée de chaque lot, et distinguer ce qui **bloque** de ce qui **alerte**.

**Étape 1 : le contrat et son contrôleur.** Le contrat dit quelles colonnes, lesquelles ne peuvent jamais être vides, et le taux de vides toléré ailleurs. Le contrôleur renvoie la liste des manquements, séparés en *erreurs* (on arrête) et *avertissements* (on prévient).

```python
contrat = {"colonnes": ["id_commande", "date", "id_client", "id_produit", "quantite", "prix_unitaire"],
           "non_nulles": ["id_commande", "date", "id_client", "id_produit"], "taux_vide_max": {"quantite": 0.02, "prix_unitaire": 0.0}}

def verifier(lot, contrat):
    erreurs, avertissements = [], []
    erreurs += [f"colonne manquante : {c}" for c in contrat["colonnes"] if c not in lot.columns]
    avertissements += [f"colonne inattendue : {c}" for c in lot.columns if c not in contrat["colonnes"]]
    erreurs += [f"vide interdit : {c}" for c in contrat["non_nulles"] if c in lot.columns and lot[c].isna().any()]
    erreurs += [f"trop de vides dans {c} : {lot[c].isna().mean():.1%}" for c, m in contrat["taux_vide_max"].items() if c in lot.columns and lot[c].isna().mean() > m]
    return erreurs, avertissements
```

**Étape 2 : quatre lots d'essai.** Le lot du jour, un lot où une colonne est renommée, un lot où une colonne est ajoutée, un lot où un champ obligatoire est vide en partie.

```python
essais = {"lot du jour": brut,
          "colonne renommée": brut.rename(columns={"quantite": "qte"}),
          "colonne ajoutée": brut.assign(canal="Site"),
          "identifiant client vide": brut.assign(id_client=brut["id_client"].where(brut.index % 500 != 0))}
for nom, lot in essais.items():
    e, a = verifier(lot, contrat)
    print(f"{nom:24s} erreurs={e} | avertissements={a}")
```
<!--sortie-->
```text
lot du jour              erreurs=[] | avertissements=[]
colonne renommée         erreurs=['colonne manquante : quantite'] | avertissements=['colonne inattendue : qte']
colonne ajoutée          erreurs=[] | avertissements=['colonne inattendue : canal']
identifiant client vide  erreurs=['vide interdit : id_client'] | avertissements=[]
```

**Étape 3 : le brancher sur le chargement.** Seules les **erreurs** arrêtent ; un avertissement est consigné et le chargement continue.

```python
def charger_si_conforme(lot):
    e, a = verifier(lot, contrat)
    if e:
        return f"REFUSÉ ({len(e)} erreur(s))"
    return f"chargé ({len(a)} avertissement(s))"
print({nom: charger_si_conforme(lot) for nom, lot in essais.items()})
```
<!--sortie-->
```text
{'lot du jour': 'chargé (0 avertissement(s))', 'colonne renommée': 'REFUSÉ (1 erreur(s))', 'colonne ajoutée': 'chargé (1 avertissement(s))', 'identifiant client vide': 'REFUSÉ (1 erreur(s))'}
```

Une colonne **ajoutée** n'empêche pas le chargement (elle est ignorée et consignée) ; une colonne **manquante** ou un champ obligatoire **vide** l'arrête. Le contrat distingue ce qui casse le pipeline de ce qui prévient seulement.

### Application 5.6 — Rapprocher les produits (sections 5.3.2 à 5.3.4)

**Objectif.** Retrouver, pour chacune des 40 désignations du fournisseur, le bon produit du catalogue, et mesurer ce que vaut **chaque niveau** de préparation du texte.

**Étape 1 : voir le problème.** Aucune clé commune, mais des libellés qui se ressemblent.

```python
verite_p = lire("verite_produits")
bonne = dict(zip(verite_p["ref_fournisseur"], verite_p["id_produit"]))
print(fournisseur.merge(verite_p, on="ref_fournisseur").merge(catalogue[["id_produit", "libelle"]], on="id_produit")
      [["designation", "libelle"]].head(6).to_string(index=False))
```
<!--sortie-->
```text
          designation           libelle
    Plat  coton (lot)     Plat en coton
           Verre plat     Plat en verre
Plat  céramique (lot) Plat en céramique
        Céramique bol  Bol en céramique
            BOL coton      Bol en coton
     Bol  laine (lot)      Bol en laine
```

**Étape 2 : une fonction de recherche, paramétrée par la préparation du texte.**

```python
def meilleur(designation, preparer, mesure=fuzz.ratio):
    scores = [mesure(preparer(designation), preparer(l)) for l in catalogue["libelle"]]
    k = int(np.argmax(scores))
    return catalogue["id_produit"][k], scores[k]

def exactitude(preparer, mesure=fuzz.ratio):
    return sum(meilleur(d, preparer, mesure)[0] == bonne[r] for r, d in zip(fournisseur["ref_fournisseur"], fournisseur["designation"]))
niveaux = {"textes bruts": str, "minuscules": lambda s: str(s).lower(), "normalisation partielle": lambda s: normaliser(s, expand=False, trier=False),
           "normalisation complète": normaliser}
print(pd.Series({n: exactitude(p) for n, p in niveaux.items()}, name="bonnes réponses sur 40").to_string())
```
<!--sortie-->
```text
textes bruts               29
minuscules                 36
normalisation partielle    37
normalisation complète     40
```

**Étape 3 : comparer les mesures sur textes bruts.** Une mesure plus « intelligente » remplace-t-elle la normalisation ?

```python
mesures = {"ratio (Levenshtein normalisé)": fuzz.ratio, "token_sort_ratio": fuzz.token_sort_ratio, "token_set_ratio": fuzz.token_set_ratio, "partial_ratio": fuzz.partial_ratio}
print(pd.Series({n: exactitude(str, m) for n, m in mesures.items()}, name="bonnes réponses sur 40 (textes bruts)").to_string())
```
<!--sortie-->
```text
ratio (Levenshtein normalisé)    29
token_sort_ratio                 29
token_set_ratio                  23
partial_ratio                    16
```

Aucune mesure ne passe de 29 à 40 sur textes bruts : `token_sort_ratio` ne dépasse pas `ratio`, parce que la **casse** différencie encore « BOL coton » de « Bol en coton ». La préparation du texte compte plus que la mesure : le gain vient de `normaliser`, pas d'une formule plus savante.

**Étape 4 : l'indice du prix.** Le prix d'achat vaut-il toujours entre 45 % et 65 % du prix catalogue ? Si oui, on peut écarter les candidats incompatibles.

```python
suivi = fournisseur.assign(id_produit=fournisseur["ref_fournisseur"].map(bonne)).merge(catalogue[["id_produit", "prix_catalogue"]], on="id_produit")
rapport = suivi["prix_achat"] / suivi["prix_catalogue"]
print("rapport prix d'achat / prix catalogue : min", round(rapport.min(), 3), "| max", round(rapport.max(), 3))
```
<!--sortie-->
```text
rapport prix d'achat / prix catalogue : min 0.45 | max 0.647
```

**Étape 5 : la jointure exacte sur le texte normalisé.** Si la normalisation suffit, aucune mesure floue n'est nécessaire.

```python
cle_cat = catalogue.assign(cle=catalogue["libelle"].map(normaliser))
cle_four = fournisseur.assign(cle=fournisseur["designation"].map(normaliser))
jointure = cle_four.merge(cle_cat[["cle", "id_produit"]], on="cle", how="left")
print("désignations sans correspondance :", int(jointure["id_produit"].isna().sum()), "| clés du catalogue en double :", int(cle_cat["cle"].duplicated().sum()),
      "| bonnes réponses :", int((jointure["id_produit"] == jointure["ref_fournisseur"].map(bonne)).sum()))
```
<!--sortie-->
```text
désignations sans correspondance : 0 | clés du catalogue en double : 0 | bonnes réponses : 40
```

Une simple **jointure exacte** sur le texte normalisé retrouve les 40 produits, sans doublon de clé côté catalogue : ici, la similarité floue est inutile. Le prix d'achat (45 % à 65 % du prix catalogue) reste un bon **garde-fou** quand deux libellés sont ambigus.

### Application 5.7 — Rapprocher les clients (sections 5.3.5 à 5.3.7)

**Objectif.** Retrouver les doublons du CRM par blocage, similarité de noms et recoupement, mesurer précision et rappel, router les cas douteux, puis fusionner.

**Étape 1 : préparer la table de travail.** `crm_avec_fautes` ajoute la vérité (`id_vrai`) et des fautes de frappe dans le nom de 35 % des doublons récents.

```python
cl, n_fautes = crm_avec_fautes(crm, lire("verite_clients"))
for c in ["prenom", "nom", "ville"]:
    cl[c + "_n"] = cl[c].map(lambda s: normaliser(s, expand=False, trier=False))
vraies = int(cl.groupby("id_vrai").size().pipe(lambda g: g * (g - 1) // 2).sum())
print(len(cl), "fiches |", cl["id_vrai"].nunique(), "personnes |", vraies, "paires de doublons |", n_fautes, "fautes ajoutées")
```
<!--sortie-->
```text
5000 fiches | 4200 personnes | 800 paires de doublons | 288 fautes ajoutées
```

**Étape 2 : le coût du blocage.** Combien de paires faudrait-il comparer avec chaque clé ?

```python
def paires_bloc(cols):
    g = cl.groupby(cols).size()
    return int((g * (g - 1) // 2).sum())
for nom, cols in {"même ville": ["ville_n"], "prénom + ville": ["prenom_n", "ville_n"], "prénom + ville + date": ["prenom_n", "ville_n", "date_inscription"]}.items():
    print(f"{nom:24s}{paires_bloc(cols):>10,}".replace(",", " "))
print("toutes les paires :", f"{len(cl) * (len(cl) - 1) // 2:,}".replace(",", " "))
```
<!--sortie-->
```text
même ville               1 041 310
prénom + ville              53 153
prénom + ville + date          828
toutes les paires : 12 497 500
```

**Étape 3 : comparer les noms dans les blocs, et évaluer.** Le blocage fin ne garde que 828 paires ; on score chacune avec Jaro-Winkler sur le nom, puis on mesure à plusieurs seuils.

```python
paires = paires_candidates(cl, ["prenom_n", "ville_n", "date_inscription"])
scores = np.array([JaroWinkler.similarity(cl["nom_n"][i], cl["nom_n"][j]) for i, j in paires])
juste = np.array([cl["id_vrai"][i] == cl["id_vrai"][j] for i, j in paires])
lignes = [(th, int((scores >= th).sum()), round(100 * juste[scores >= th].mean(), 1), round(100 * juste[scores >= th].sum() / vraies, 1)) for th in (0.7, 0.8, 0.9, 0.95, 1.0)]
print(pd.DataFrame(lignes, columns=["seuil", "paires fusionnées", "précision (%)", "rappel (%)"]).to_string(index=False))
```
<!--sortie-->
```text
 seuil  paires fusionnées  précision (%)  rappel (%)
  0.70                803           99.6       100.0
  0.80                803           99.6       100.0
  0.90                803           99.6       100.0
  0.95                720           99.7        89.8
  1.00                514           99.6        64.0
```

**Étape 4 : trois zones.** Fusion automatique au-dessus de 0,95, revue entre 0,80 et 0,95, rejet en dessous.

```python
zones = pd.cut(scores, [-1, 0.80, 0.95, 2], right=False, labels=["séparées", "revue", "fusion automatique"])
print(pd.DataFrame({"zone": zones, "vrai": juste}).groupby("zone", observed=True)["vrai"].agg(paires="size", vrais_doublons="sum").to_string())
```
<!--sortie-->
```text
                    paires  vrais_doublons
zone                                      
séparées                25               0
revue                   83              82
fusion automatique     720             718
```

Au seuil 0,95, la fusion automatique ne se trompe que deux fois sur 720 ; la revue concerne 83 paires. Les 25 paires les moins ressemblantes ne sont **aucune** un doublon. Les trois fusions à tort au seuil 0,80 sont des homonymes inscrits le même jour.

**Étape 5 : la fiche d'or.** On relie les paires fusionnées (composantes connexes d'un graphe), puis on garde la plus ancienne fiche de chaque groupe.

```python
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
fusion = [(i, j) for (i, j), s in zip(paires, scores) if s >= 0.80]
m = coo_matrix(([1] * len(fusion), ([i for i, _ in fusion], [j for _, j in fusion])), shape=(len(cl), len(cl)))
cl["groupe"] = connected_components(m, directed=False)[1]
fiche_or = cl.sort_values("id_crm").groupby("groupe").first()
print("fiches :", len(cl), "-> fiches d'or :", len(fiche_or), "| personnes réelles :", cl["id_vrai"].nunique())
```
<!--sortie-->
```text
fiches : 5000 -> fiches d'or : 4198 | personnes réelles : 4200
```

Cinq mille fiches deviennent 4 198 personnes pour 4 200 en réalité : les deux fiches d'écart viennent des homonymes fusionnés à tort.

### Application 5.8 — Lignage et pseudonymisation (sections 5.4.2 à 5.4.5)

**Objectif.** Faire enregistrer ses étapes au pipeline, interroger le graphe qui en résulte, puis pseudonymiser une colonne et mesurer ce qu'un attaquant en retrouve.

**Étape 1 : un journal de lignage.**

```python
journal = Journal()
journal.enregistrer("chargement", ["commandes_export"], ["stg_commandes"], len(brut), len(brut))
journal.enregistrer("typage et dédoublonnage", ["stg_commandes"], ["commandes_typees"], len(brut), len(unique))
journal.enregistrer("validation", ["commandes_typees", "clients_crm", "produits_catalogue"], ["commandes_propres", "commandes_rejets"], len(unique), len(propres_a))
journal.enregistrer("mart par catégorie", ["commandes_propres", "produits_catalogue"], ["mart_ca_categorie"], len(propres_a), 4)
print(journal.table().assign(entrees=lambda d: d["entrees"].map(", ".join), sorties=lambda d: d["sorties"].map(", ".join)).to_string(index=False))
```
<!--sortie-->
```text
                  etape                                           entrees                             sorties  lignes_in  lignes_out
             chargement                                  commandes_export                       stg_commandes      19700       19700
typage et dédoublonnage                                     stg_commandes                    commandes_typees      19700       18000
             validation commandes_typees, clients_crm, produits_catalogue commandes_propres, commandes_rejets      18000       17218
     mart par catégorie             commandes_propres, produits_catalogue                   mart_ca_categorie      17218           4
```

**Étape 2 : remonter et descendre le graphe.**

```python
def voisins(table, etapes, sens):
    de, vers = ("sorties", "entrees") if sens == "amont" else ("entrees", "sorties")
    trouves = set()
    for e in etapes:
        if table in e[de]:
            for t in e[vers]:
                trouves |= {t} | voisins(t, etapes, sens)
    return trouves
print("amont de mart_ca_categorie :", sorted(voisins("mart_ca_categorie", journal.etapes, "amont")))
print("aval de produits_catalogue :", sorted(voisins("produits_catalogue", journal.etapes, "aval")))
```
<!--sortie-->
```text
amont de mart_ca_categorie : ['clients_crm', 'commandes_export', 'commandes_propres', 'commandes_typees', 'produits_catalogue', 'stg_commandes']
aval de produits_catalogue : ['commandes_propres', 'commandes_rejets', 'mart_ca_categorie']
```

**Étape 3 : l'empreinte nue contre la clé secrète.** L'attaquant connaît le format des adresses (`prénom.nomN@exemple.test`) et dispose des listes de prénoms et de noms : 1,6 million de candidats.

```python
def empreinte(v):             return hashlib.sha256(v.lower().encode()).hexdigest()
def pseudonyme(v, cle):       return hmac.new(cle, v.lower().encode(), hashlib.sha256).hexdigest()
emails = crm["email"].str.lower().unique()
prenoms, noms = sorted(set(crm["prenom"].str.lower())), sorted(set(crm["nom"].str.lower()))
dico = {empreinte(f"{p}.{n}{i}@exemple.test") for p in prenoms for n in noms for i in range(1, 5001)}
nu = [empreinte(e) for e in emails]
protege = [pseudonyme(e, b"cle-secrete-de-la-boutique") for e in emails]
print("candidats :", len(dico), "| adresses :", len(emails))
print("retrouvées avec l'empreinte nue :", sum(x in dico for x in nu), "| avec la clé secrète :", sum(x in dico for x in protege))
```
<!--sortie-->
```text
candidats : 1600000 | adresses : 4200
retrouvées avec l'empreinte nue : 4200 | avec la clé secrète : 0
```

**Étape 4 : les quasi-identifiants.** Même sans e-mail, combien de personnes sont **uniques** selon les attributs conservés ?

```python
personnes = cl.drop_duplicates("id_vrai").assign(annee=lambda d: d["date_inscription"].str[:4])
def uniques(cols):
    return round(float(100 * (personnes.groupby(cols)["id_vrai"].transform("size") == 1).mean()), 1)
print({"ville + prénom": uniques(["ville", "prenom"]), "+ année d'inscription": uniques(["ville", "prenom", "annee"]),
       "+ date d'inscription": uniques(["ville", "prenom", "date_inscription"])})
```
<!--sortie-->
```text
{'ville + prénom': 0.0, "+ année d'inscription": 1.5, "+ date d'inscription": 99.1}
```

Avec la ville et le prénom, personne n'est unique ; avec l'année d'inscription, 1,5 % le sont ; avec la **date précise**, 99,1 %. Une pseudonymisation de l'e-mail seule ne protège donc pas : la **combinaison** d'attributs réidentifie.

### Application 5.9 — Collecter sur le site local (sections 5.5.3 à 5.5.6)

**Objectif.** Lire `robots.txt`, extraire le catalogue d'une page HTML, parcourir une API paginée qui refuse une requête sur sept, et se défendre contre un changement de mise en page. Tout se passe sur votre machine.

**Étape 1 : démarrer le site de démonstration.** `serveur_local` lance le serveur dans un fil d'exécution et le ferme à la sortie du bloc `with`.

```python
import requests
from bs4 import BeautifulSoup
from urllib import robotparser
avis_demo = pd.read_csv("donnees/avis_clients.csv").head(400).fillna("")
with serveur_local(catalogue, avis_demo) as base:
    robots = robotparser.RobotFileParser(base + "/robots.txt"); robots.read()
    print("catalogue autorisé :", robots.can_fetch("*", base + "/catalogue"), "| /prive/ autorisé :", robots.can_fetch("*", base + "/prive/clients"),
          "| délai demandé :", robots.crawl_delay("*"), "s")
    print("accès forcé à /prive/clients : code", requests.get(base + "/prive/clients", timeout=5).status_code)
```
<!--sortie-->
```text
catalogue autorisé : True | /prive/ autorisé : False | délai demandé : 1 s
accès forcé à /prive/clients : code 403
```

**Étape 2 : scraper la page du catalogue.**

```python
def extraire(html):
    soupe = BeautifulSoup(html, "html.parser")
    return pd.DataFrame([{"id_produit": d["data-id"], "libelle": d.select_one(".nom").text, "prix": float(d.select_one(".prix").text.replace("€", ""))}
                         for d in soupe.select("div.produit")])
with serveur_local(catalogue, avis_demo) as base:
    page = extraire(requests.get(base + "/catalogue", timeout=5).text)
print(page.shape, "| identique au catalogue :", bool((page["id_produit"] == catalogue["id_produit"]).all() and np.allclose(page["prix"], catalogue["prix_catalogue"])))
```
<!--sortie-->
```text
(48, 3) | identique au catalogue : True
```

**Étape 3 : l'API paginée, d'abord sans précaution.** Le serveur refuse une requête sur sept (code 429). Combien d'avis le collecteur naïf perd-il, et le sait-il ?

```python
with serveur_local(catalogue, avis_demo) as base:
    reponses = [requests.get(f"{base}/api/avis?page={p}&taille=25", timeout=5) for p in range(1, 17)]
recus = sum(len(r.json()["resultats"]) for r in reponses if r.status_code == 200)
print("codes :", [r.status_code for r in reponses])
print("avis reçus :", recus, "sur", len(avis_demo))
```
<!--sortie-->
```text
codes : [200, 200, 200, 200, 200, 200, 429, 200, 200, 200, 200, 200, 200, 429, 200, 200]
avis reçus : 350 sur 400
```

**Étape 4 : le collecteur robuste.** Il réessaie sur 429, avec une attente croissante, et s'arrête après un nombre d'essais borné.

```python
def lire_page(session, url, essais=5):
    for k in range(essais):
        r = session.get(url, timeout=5)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 0)) + 0.01 * 2 ** k); continue
        r.raise_for_status(); return r.json()
    raise RuntimeError(f"abandon après {essais} essais : {url}")

with serveur_local(catalogue, avis_demo) as base:
    s, collectes, page_no = requests.Session(), [], 1
    while page_no:
        rep = lire_page(s, f"{base}/api/avis?page={page_no}&taille=25")
        collectes += rep["resultats"]; page_no = rep["suivante"]
c = pd.DataFrame(collectes)
print(len(c), "avis | identifiants uniques :", c["id_avis"].nunique(), "| identiques à la source :", c["texte"].tolist() == avis_demo["texte"].tolist())
```
<!--sortie-->
```text
400 avis | identifiants uniques : 400 | identiques à la source : True
```

**Étape 5 : la mise en page change.** Le sélecteur `div.produit` ne trouve plus rien dans `/catalogue-v2` ; un contrôle de volume le détecte.

```python
with serveur_local(catalogue, avis_demo) as base:
    v2 = requests.get(base + "/catalogue-v2", timeout=5).text
trouves = len(extraire(v2))
print("produits trouvés dans la nouvelle page :", trouves, "| article[id] en trouve :", len(BeautifulSoup(v2, "html.parser").select("article[id]")))
print("contrôle de volume :", "OK" if trouves >= 40 else "ALERTE : résultat vide ou tronqué, chargement arrêté")
```
<!--sortie-->
```text
produits trouvés dans la nouvelle page : 0 | article[id] en trouve : 48
contrôle de volume : ALERTE : résultat vide ou tronqué, chargement arrêté
```

## Exercices

Les exercices sont rangés par difficulté (⭐ calcul direct, ⭐⭐ raisonnement, ⭐⭐⭐ synthèse ou expérience). Essayez-les **à la main d'abord** ; les corrigés suivent.

### Exercice 5.1 ⭐ — L'équation de conservation (section 5.1.4)

Un pipeline lit **12 400** lignes. Il écarte **1 100** doublons, rejette **4 %** des lignes restantes, et charge le reste.

(a) Combien de lignes sont rejetées ? Combien sont chargées ?
(b) Écrivez l'équation de conservation et vérifiez-la.
(c) Le lendemain, il lit 12 600 lignes, écarte 1 150 doublons, rejette 600 lignes et en charge 10 850. Le seuil d'alerte est un taux de rejet de 5 % **des lignes restantes**. Que doit faire le pipeline ?

### Exercice 5.2 ⭐⭐ — Idempotent ou pas ? (section 5.1.7)

Pour chaque opération, dites si elle est **idempotente** (la relancer donne le même résultat qu'une seule exécution) et, sinon, comment la corriger.

(a) `INSERT INTO ventes SELECT * FROM lot` dans une table sans clé.
(b) `INSERT … ON CONFLICT (id) DO UPDATE SET montant = excluded.montant`.
(c) `DELETE FROM ventes WHERE lot = 7` suivi de l'insertion du lot 7.
(d) `UPDATE stock SET quantite = quantite - 3`.
(e) Écrire le fichier `ventes_2025-12-31.parquet`, en écrasant le précédent s'il existe.
(f) Ajouter une ligne « chargement terminé » à la fin d'un fichier de journal.

### Exercice 5.3 ⭐⭐⭐ — Le filigrane qui perd des lignes (section 5.1.7)

Chaque commande des trois premiers mois de 2025 arrive à l'entrepôt avec un **retard** : 90 % arrivent le jour même, 10 % entre 1 et 30 jours plus tard (graine 0). Chaque nuit, un pipeline charge les nouvelles lignes, du 1ᵉʳ janvier au 30 avril. Comparez deux méthodes : **A**, charger les lignes dont la date de commande dépasse la plus grande date déjà chargée (le filigrane) ; **B**, charger les lignes arrivées depuis la veille. Combien de lignes chaque méthode perd-elle ?

### Exercice 5.4 ⭐ — Quelle dimension ? (section 5.2.2)

Classez chaque défaut dans une dimension de la qualité (complétude, validité, unicité, cohérence, exactitude, fraîcheur).

(a) Le champ « téléphone » est vide pour 18 % des clientes.
(b) Une commande porte la date du 31 février.
(c) La même cliente apparaît sous deux numéros.
(d) Le tableau de ventes affiche, le lundi, les chiffres de jeudi dernier.
(e) Une commande référence un produit qui n'existe pas au catalogue.
(f) Un produit est vendu 12 € alors que son prix d'achat est de 15 €.

### Exercice 5.5 ⭐⭐ — Un score sans se tromper de formule (section 5.2.4)

Sur 10 000 lignes, on mesure : 300 valeurs vides (complétude), 150 valeurs hors domaine (validité), 500 doublons (unicité) et 50 références orphelines (cohérence). Cent lignes cumulent un doublon **et** une valeur vide.

(a) Combien de lignes sont fautives ? Quel est le score global ?
(b) Que décide la grille du livre (≥ 95 % publier ; 85 à 95 % publier et alerter ; < 85 % arrêter) ?
(c) Si l'on ignorait le chevauchement, entre quelles bornes le score pourrait-il se trouver ?

### Exercice 5.6 ⭐⭐ — Une règle statistique et son seuil (section 5.2.6)

On veut signaler en avertissement les prix « improbables pour leur produit » : ceux qui dépassent **k fois la médiane** des prix de ce produit. (a) Combien de lignes sont signalées pour k = 3, 4, 5 et 8 ? (b) Comment choisir k ? (c) Les lignes signalées se répartissent-elles uniformément entre les catégories de produits ?

### Exercice 5.7 ⭐ — Levenshtein à la main (section 5.3.3)

(a) Quelle est la distance de Levenshtein entre « kitten » et « sitting » ? Donnez une suite d'opérations.
(b) Quelle est la similarité normalisée $1-d/\max(|a|,|b|)$ entre « sophie » et « sofie » ?
(c) « Jean Dupont » et « Dupont Jean » désignent la même personne, mais leur distance de Levenshtein est élevée. Quel traitement du livre règle le problème ?

### Exercice 5.8 ⭐⭐ — Précision, rappel, coûts (section 5.3.6)

Une base contient **100** vraies paires de doublons. Selon le seuil de similarité :

| Seuil | Paires fusionnées | Dont vraies |
|---|---|---|
| 0,95 | 60 | 59 |
| 0,80 | 130 | 95 |
| 0,60 | 400 | 100 |

(a) Calculez précision, rappel et F1 pour chaque seuil.
(b) Une fusion à tort coûte **10** (deux personnes fondues en une, difficile à défaire) et un doublon laissé coûte **1**. Quel seuil minimise le coût total ?
(c) Et si les deux erreurs coûtent 1 ?

### Exercice 5.9 ⭐⭐⭐ — Choisir une clé de blocage (section 5.3.5)

Une clé de blocage doit être **économique** (peu de paires) et **sûre** (elle ne sépare pas de vrais doublons). Sur la table `cl` de l'application 5.7 (avec ses fautes de frappe), évaluez cinq clés : la ville ; le prénom et la ville ; le prénom et la date d'inscription ; les trois premières lettres du nom et la ville ; la date d'inscription seule. Pour chacune, donnez le nombre de paires à comparer et la part des 800 vraies paires qu'elle conserve (la **complétude des paires**). Ajoutez ensuite des fautes de frappe dans le **prénom** (une lettre manquante au début, pour 35 % des doublons récents) : que devient la complétude de la clé « prénom + date d'inscription » ? Proposez un **blocage multiple** (union de deux clés) et évaluez-le.

### Exercice 5.10 ⭐ — Le k-anonymat à la main (section 5.4.5)

Huit personnes, avec leur ville et leur année de naissance : 1 (A, 1990), 2 (A, 1990), 3 (A, 1991), 4 (B, 1990), 5 (B, 1991), 6 (B, 1991), 7 (B, 1992), 8 (C, 1990). Les villes A et C sont dans la région Nord, B dans la région Sud.

(a) Quel est le *k* de la table si l'on ne conserve que la ville ?
(b) Avec la ville et l'année de naissance : quel est le *k*, et quelle part des personnes est unique ?
(c) Proposez une généralisation qui donne **k ≥ 4**.

### Exercice 5.11 ⭐⭐ — Un sel public protège-t-il ? (section 5.4.5)

On remplace l'e-mail par `sha256(sel + e-mail)`, avec un sel **identique pour toutes les lignes et publié** dans la documentation du jeu de données. Un attaquant dispose du même dictionnaire de 1,6 million de candidats qu'à l'application 5.8. (a) Combien d'adresses retrouve-t-il ? (b) Qu'est-ce qui distingue ce sel d'une clé secrète ? (c) Que faudrait-il changer pour que l'attaque échoue ?

### Exercice 5.12 ⭐⭐ — Un extracteur qui survit au changement de page (sections 5.5.4 à 5.5.6)

(a) À la main : un collecteur essaie une requête au plus 5 fois, avec une attente de 1, 2, 4, puis 8 secondes entre deux essais. Quelle attente cumulée dans le pire cas ?
(b) Le serveur refuse une requête sur sept. Pour collecter 16 pages, combien de requêtes sont envoyées au total ?
(c) Écrivez une fonction `extraire_tout(html)` qui renvoie la même table pour les deux mises en page (`/catalogue` et `/catalogue-v2`), et vérifiez qu'elle retrouve les 48 produits avec leurs prix.

## Corrigés

### Corrigé 5.1

(a) Lignes restantes : $12\,400-1\,100=11\,300$. Rejets : $0{,}04\times11\,300=452$. Lignes chargées : $11\,300-452=10\,848$.

(b) Entrées − doublons − rejets = sorties : $12\,400-1\,100-452=10\,848$. ✔

(c) Lignes restantes : $12\,600-1\,150=11\,450$. Taux de rejet : $600/11\,450\approx5{,}24\,\%$, au-dessus du seuil de 5 %. Le pipeline **arrête le chargement** et prévient un humain : la veille, le taux était de 4 %, et ce saut est le signe d'un incident à la source. (L'équation reste juste : $12\,600-1\,150-600=10\,850$ ; une équation de conservation vérifiée n'est **pas** une preuve de qualité, seulement de non-perte.)

### Corrigé 5.2

(a) **Non idempotente** : chaque relance ajoute les lignes une nouvelle fois. Correction : déclarer une clé et fusionner (*upsert*).
(b) **Idempotente** : une seconde exécution écrit les mêmes valeurs sur les mêmes clés.
(c) **Idempotente** : on remplace le lot entier par lui-même. À condition que la suppression et l'insertion se fassent dans **une seule transaction** : sinon une panne entre les deux perd le lot.
(d) **Non idempotente** : chaque relance retire 3 unités. Correction : écrire une **valeur absolue** (`SET quantite = <valeur calculée à partir du lot>`), pas un incrément.
(e) **Idempotente** : le nom dépend de la date métier, et l'écrasement donne le même fichier.
(f) **Non idempotente** : la ligne est ajoutée à chaque exécution. Pour un journal c'est voulu (on garde l'historique), mais il faut alors **ne pas le lire comme un état**.

### Corrigé 5.3

On simule les retards, puis on joue 120 nuits avec chaque méthode.

```python
typ_q1 = propres_b[propres_b["mois"] <= 3].copy()
rng = np.random.default_rng(0)
retard = np.where(rng.random(len(typ_q1)) < 0.10, rng.integers(1, 31, len(typ_q1)), 0)
typ_q1["arrivee"] = typ_q1["date"] + pd.to_timedelta(retard, unit="D")

filigrane, charge_a, charge_b = pd.Timestamp("2024-12-31"), set(), set()
for nuit in pd.date_range("2025-01-01", "2025-04-30"):
    dispo = typ_q1[typ_q1["arrivee"] <= nuit]                                       # ce qui est arrivé à l'entrepôt
    neuf_a = dispo[dispo["date"] > filigrane]                                       # A : filtre sur la date métier
    neuf_b = dispo[dispo["arrivee"] > nuit - pd.Timedelta(days=1)]                  # B : filtre sur la date d'arrivée
    charge_a |= set(neuf_a["id_commande"]); charge_b |= set(neuf_b["id_commande"])
    filigrane = max(filigrane, neuf_a["date"].max() if len(neuf_a) else filigrane)
print("lignes à charger :", len(typ_q1), "| perdues par A :", len(typ_q1) - len(charge_a), "| perdues par B :", len(typ_q1) - len(charge_b))
```
<!--sortie-->
```text
lignes à charger : 4210 | perdues par A : 438 | perdues par B : 0
```
<!--sortie-->

La méthode A **perd 438 lignes sur 4 210** (10,4 %, soit à peu près la part des lignes en retard) : toutes celles qui arrivent après que le filigrane a dépassé leur date, et plus le retard est long, plus le risque est grand. La méthode B ne perd rien, parce que la date d'arrivée **croît toujours** : une ligne ne peut pas arriver « avant » la veille. Le prix à payer est de stocker cette date technique, mais on la reçoit gratuitement avec la métadonnée de chargement (`_charge_le`).

### Corrigé 5.4

(a) **Complétude** : une valeur attendue est absente.
(b) **Validité** : la date n'appartient pas au domaine des dates possibles.
(c) **Unicité** : une même réalité est représentée deux fois (une cliente, deux numéros).
(d) **Fraîcheur** : la donnée est trop ancienne par rapport à l'usage.
(e) **Cohérence** : une référence ne trouve pas sa cible entre deux sources.
(f) **Exactitude** (ou cohérence métier) : la valeur contredit un recoupement de confiance (le prix d'achat dépasse le prix de vente). On ne peut la déceler qu'en la comparant à une **référence**.

### Corrigé 5.5

(a) Lignes fautives distinctes : $300+150+500+50-100=900$ (on retire les 100 lignes comptées deux fois). Score : $1-900/10\,000=91\,\%$.

(b) 91 % est entre 85 % et 95 % : on **publie et l'on alerte** le propriétaire de la source.

(c) Sans connaître le chevauchement, le nombre de lignes fautives est au moins $\max(300,150,500,50)=500$ (si toutes les autres violations recoupent les doublons) et au plus $300+150+500+50=1\,000$ (aucun recoupement). Le score est donc **entre 90 % et 95 %** : la décision reste « publier et alerter », sauf si le résultat tombe pile à 95 %. D'où l'intérêt de calculer le « ou » logique ligne à ligne, au lieu d'additionner les taux.

### Corrigé 5.6

```python
mediane = typ.groupby("id_produit")["prix_unitaire"].transform("median")
for k in (3, 4, 5, 8):
    print(f"k = {k} : {int((typ['prix_unitaire'] > k * mediane).sum())} lignes signalées")
par_cat = typ[typ["prix_unitaire"] > 5 * mediane].merge(catalogue[["id_produit", "categorie"]], on="id_produit")["categorie"].value_counts()
print("répartition par catégorie pour k = 5 :", par_cat.to_dict())
```
<!--sortie-->
```text
k = 3 : 660 lignes signalées
k = 4 : 186 lignes signalées
k = 5 : 57 lignes signalées
k = 8 : 7 lignes signalées
répartition par catégorie pour k = 5 : {'D': 16, 'A': 15, 'B': 14, 'C': 12}
```
<!--sortie-->

(a) Le nombre de lignes signalées s'effondre quand k augmente : 660 pour k = 3, 186 pour k = 4, 57 pour k = 5, 7 pour k = 8.
(b) Le bon k est celui qui signale un **nombre de lignes qu'un humain peut relire** tout en laissant passer les variations normales : avec k = 3, 660 lignes (3,4 %) noient la relecture ; avec k = 8, sept lignes laissent passer des prix douteux. **k = 5** (57 lignes, 0,3 %) est un bon compromis ; un échantillon relu à la main (20 lignes signalées) dit si l'on cible des erreurs ou de simples promotions.
(c) Les lignes signalées pour k = 5 se répartissent presque également entre les catégories (D : 16, A : 15, B : 14, C : 12) : la règle ne vise pas une catégorie en particulier. Si elles s'étaient concentrées sur l'une d'elles, on aurait suspecté une dispersion naturelle de ses prix, et affiné la règle **par catégorie**.

### Corrigé 5.7

(a) La distance vaut **3** : *kitten* → *sitten* (remplacer k par s) → *sittin* (remplacer e par i) → *sitting* (insérer g).
(b) *sophie* → *sofie* demande 2 opérations (remplacer p par f, supprimer h) : $d=2$, longueur maximale 6, similarité $1-2/6\approx0{,}667$.
(c) Les **comparaisons par jetons** (*token sort*), ou la normalisation qui **trie les mots**, rendent l'ordre indifférent.

```python
print(Levenshtein.distance("kitten", "sitting"), Levenshtein.distance("sophie", "sofie"),
      round(Levenshtein.normalized_similarity("sophie", "sofie"), 3), "|", round(fuzz.ratio("Jean Dupont", "Dupont Jean")),
      round(fuzz.token_sort_ratio("Jean Dupont", "Dupont Jean")))
```
<!--sortie-->
```text
3 2 0.667 | 55 100
```

Les deux premiers nombres retrouvent les distances (3 et 2), puis la similarité 0,667. À droite de la barre, le rapport de similarité (en pourcentage) vaut **55** pour « Jean Dupont » contre « Dupont Jean » et **100** une fois les mots triés.
<!--sortie-->

### Corrigé 5.8

(a)

| Seuil | Précision | Rappel | F1 |
|---|---|---|---|
| 0,95 | $59/60=0{,}983$ | $59/100=0{,}59$ | $0{,}738$ |
| 0,80 | $95/130=0{,}731$ | $95/100=0{,}95$ | $0{,}826$ |
| 0,60 | $100/400=0{,}25$ | $100/100=1$ | $0{,}4$ |

(b) Coût = $10\times$ fusions à tort + $1\times$ doublons laissés. Seuil 0,95 : $10\times1+41=51$. Seuil 0,80 : $10\times35+5=355$. Seuil 0,60 : $10\times300+0=3\,000$. **Le seuil 0,95** gagne nettement : quand une erreur de fusion coûte cher, on exige une grande précision et l'on envoie le reste à la **file de revue**.

(c) Avec des coûts égaux : 0,95 → $1+41=42$ ; 0,80 → $35+5=40$ ; 0,60 → $300$. **Le seuil 0,80** devient le meilleur, de peu. Le seuil se choisit toujours par les coûts, pas par la seule précision ou le seul F1.

### Corrigé 5.9

```python
vraies_paires = {frozenset(p) for p in paires_candidates(cl, ["id_vrai"])}
cl["nom3"] = cl["nom_n"].str[:3]
def evaluer(d, cols):
    P = {frozenset(p) for p in paires_candidates(d, cols)}
    return len(P), round(100 * len(P & vraies_paires) / len(vraies_paires), 1)
cles = {"ville": ["ville_n"], "prénom + ville": ["prenom_n", "ville_n"], "prénom + date": ["prenom_n", "date_inscription"],
        "3 lettres du nom + ville": ["nom3", "ville_n"], "date seule": ["date_inscription"]}
print(pd.DataFrame([(n, *evaluer(cl, c)) for n, c in cles.items()], columns=["clé", "paires", "complétude des paires (%)"]).to_string(index=False))
```
<!--sortie-->
```text
                     clé  paires  complétude des paires (%)
                   ville 1041310                      100.0
          prénom + ville   53153                      100.0
           prénom + date    1227                      100.0
3 lettres du nom + ville   68548                       79.4
              date seule    9595                      100.0
```
<!--sortie-->

La **complétude des paires** est le rappel du blocage : une paire qui n'est pas dans le même bloc ne sera **jamais comparée**, quel que soit le soin du score. Quatre clés conservent les 800 vraies paires, mais à des coûts très différents : « prénom + date » en demande 1 227, « date seule » près de 9 600, « ville » plus d'un million. La clé « trois lettres du nom + ville » est **peu sûre** : elle perd 20,6 % des vraies paires, car la faute de frappe sur le nom touche souvent l'une des trois premières lettres.

Ajoutons maintenant des fautes dans le prénom des doublons récents, et comparons deux clés seules avec leur union.

```python
rng = np.random.default_rng(7)
cl2 = cl.copy()
touches = cl2.index[(cl2["id_crm"] > 4200) & (rng.random(len(cl2)) < 0.35)]
cl2.loc[touches, "prenom_n"] = cl2.loc[touches, "prenom_n"].str[1:]                     # première lettre manquante
seul_a, seul_b = ["prenom_n", "date_inscription"], ["nom3", "date_inscription"]
union = {frozenset(p) for c in (seul_a, seul_b) for p in paires_candidates(cl2, c)}
print("prénom + date :", evaluer(cl2, seul_a), "| 3 lettres du nom + date :", evaluer(cl2, seul_b))
print("union des deux clés :", len(union), "paires,", round(100 * len(union & vraies_paires) / len(vraies_paires), 1), "% des vraies paires")
```
<!--sortie-->
```text
prénom + date : (882, 61.5) | 3 lettres du nom + date : (1248, 79.4)
union des deux clés : 1706 paires, 92.6 % des vraies paires
```
<!--sortie-->

« Prénom + date », sûre jusque-là, ne conserve plus que **61,5 %** des vraies paires ; « 3 lettres du nom + date » en conserve **79,4 %**. Chaque clé échoue sur des fautes **différentes** (le prénom pour l'une, le nom pour l'autre), si bien que leur **union** monte à **92,6 %** avec 1 706 paires à comparer. Elle ne retrouve pas les doublons dont le prénom **et** le nom portent une faute : un blocage multiple réduit le risque, il ne l'annule pas.

### Corrigé 5.10

(a) Groupes : A = {1, 2, 3} (3 personnes), B = {4, 5, 6, 7} (4), C = {8} (1). Le plus petit groupe compte 1 personne : **k = 1** (la personne 8 est unique).

(b) Groupes (ville, année) : (A, 1990) = 2, (A, 1991) = 1, (B, 1990) = 1, (B, 1991) = 2, (B, 1992) = 1, (C, 1990) = 1. **k = 1**, et les personnes 3, 4, 7 et 8 sont uniques : **4 sur 8, soit 50 %**.

(c) On généralise : la ville devient la **région**, l'année la **décennie** (toutes les années 1990 se confondent). Groupes : Nord = {1, 2, 3, 8} (4 personnes), Sud = {4, 5, 6, 7} (4). Donc **k = 4**. Le prix est une perte de précision : on ne sait plus ni la ville ni l'année exacte.

### Corrigé 5.11

```python
sel_public = "sel-publie-dans-la-documentation:"
sale = {hashlib.sha256((sel_public + e).encode()).hexdigest() for e in emails}
dico_sale = {hashlib.sha256((sel_public + f"{p}.{n}{i}@exemple.test").encode()).hexdigest() for p in prenoms for n in noms for i in range(1, 5001)}
print("adresses retrouvées avec le sel public :", len(sale & dico_sale), "sur", len(sale))
```
<!--sortie-->
```text
adresses retrouvées avec le sel public : 4200 sur 4200
```
<!--sortie-->

(a) L'attaquant **retrouve toutes les adresses** : il lui suffit de recalculer son dictionnaire avec le sel connu. Un sel public a un seul mérite, empêcher les tables précalculées **génériques** (celles que l'on trouve en ligne) ; il n'arrête pas une attaque ciblée.
(b) Une **clé secrète** n'est connue que de l'organisation : sans elle, l'attaquant ne peut rien précalculer, et chaque essai demanderait un accès au système. C'est le **secret** qui protège, pas la fonction.
(c) Utiliser un **HMAC avec une clé secrète** (comme à l'application 5.8), conservée **hors du jeu de données** et renouvelée si elle fuit. Et, pour les données à partager, se demander d'abord si l'identifiant est **nécessaire** (minimisation).

### Corrigé 5.12

(a) Les attentes se produisent **entre** deux essais : 1 + 2 + 4 + 8 = **15 secondes** dans le pire cas (5 essais, 4 pauses).

(b) Une requête sur sept est refusée : les requêtes numéro 7 et 14 le sont, et la requête 21 n'est pas atteinte. Pour obtenir 16 pages, il faut **16 + 2 = 18 requêtes**.

(c)

```python
def extraire_tout(html):
    soupe = BeautifulSoup(html, "html.parser")
    if soupe.select("div.produit"):                                                 # mise en page d'origine
        lignes = [(d["data-id"], float(d.select_one(".prix").text.replace("€", ""))) for d in soupe.select("div.produit")]
    else:                                                                           # nouvelle mise en page
        lignes = [(a["id"], float(a.select_one("b").text)) for a in soupe.select("article[id]")]
    return pd.DataFrame(lignes, columns=["id_produit", "prix"])

with serveur_local(catalogue, avis_demo) as base:
    v1, v2 = (extraire_tout(requests.get(base + p, timeout=5).text) for p in ("/catalogue", "/catalogue-v2"))
for nom, t in (("v1", v1), ("v2", v2)):
    print(nom, len(t), "produits | prix identiques au catalogue :", bool((t["id_produit"] == catalogue["id_produit"]).all() and np.allclose(t["prix"], catalogue["prix_catalogue"])))
```
<!--sortie-->
```text
v1 48 produits | prix identiques au catalogue : True
v2 48 produits | prix identiques au catalogue : True
```
<!--sortie-->

Deux mises en page, une seule fonction : les **identifiants** (`data-id`, `id`) sont les mêmes dans les deux, et c'est eux qu'on exploite, plutôt que des classes de style, plus volatiles. Et le contrôle de volume (au moins 40 produits) reste indispensable : le jour où une **troisième** mise en page arrive, la fonction renvoie un tableau vide, et c'est le contrôle qui donne l'alerte.

```python
import shutil
shutil.rmtree(TMP, ignore_errors=True)
```
