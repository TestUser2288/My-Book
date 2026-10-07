# Chapitre 3 : Qualité des données et réconciliation — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 3 du livre. Les **applications** sont de petites études guidées sur les fichiers désordonnés de la boutique (le CRM, l'export du site, les fichiers de la caisse, le catalogue du fournisseur, les montants saisis) ; vous les refaites pas à pas, puis vous prolongez dans les rubriques « À vous ». Les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ plus long) renvoient chacun à une section du livre ; leurs **corrigés** sont à la fin. Les données sont **simulées**, et la « vérité » est conservée dans les fichiers `verite_*` : **n'ouvrez la vérité qu'à la fin d'une étude**, pour juger votre travail, comme on ouvrirait le corrigé d'un problème.

Une première cellule charge les bibliothèques et les fichiers ; les autres reprennent les noms ainsi définis.

```python
import os, sys, io, sqlite3, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O          # lecture de la caisse, rapprochements, fonctions utiles du chapitre

D = os.environ["DONNEES"]
lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
crm, site = lire("crm_clients.csv", dtype=str), lire("site_commandes.csv", dtype=str)
site_l, cmd, lig, prod = lire("site_lignes.csv"), lire("commandes.csv"), lire("lignes_commande.csv"), lire("produits.csv")
cat, mont = lire("catalogue_fournisseur.csv"), lire("montants_saisis.csv")
caisse, fichiers = O.lire_caisse()
print(len(crm), "lignes de CRM |", len(site), "lignes d'export du site |", len(caisse), "lignes de caisse |", len(cat), "lignes de catalogue")
```

```python hide
def num(cle, valeur):
    print("NUM", cle, valeur)
REF = pd.Timestamp("2026-01-05")
```

## Applications

### Application 3.1 — Mesurer la qualité du CRM (section 3.1)

**Objectif.** Calculer, pour le CRM, un indicateur par dimension, puis les lire comme un tableau de bord.

**Étape 1 — La complétude.** On compte, colonne par colonne, la part des cellules renseignées, puis la part des fiches « complètes » (e-mail, code postal et consentement présents) :

```python
completude = (crm.notna().mean() * 100).round(1)
print(completude[completude < 100].to_string())
complet = crm[["email", "code_postal", "consentement_marketing"]].notna().all(axis=1)
print("fiches complètes :", int(complet.sum()), "sur", len(crm), f"({100 * complet.mean():.1f} %)")
```

**Étape 2 — La validité.** On applique six règles de forme et l'on garde, pour chacune, le nombre de lignes en échec. Les colonnes absentes ne comptent pas comme échec de forme (elles relèvent de la complétude) :

```python
def echecs_format(serie, motif):
    return serie.notna() & ~serie.str.fullmatch(motif, na=False)

regles = {
    "e-mail mal formé": echecs_format(crm["email"], O.RE_EMAIL),
    "code postal ≠ 5 chiffres": echecs_format(crm["code_postal"], O.RE_CP),
    "consentement hors {oui, non}": crm["consentement_marketing"].notna() & ~crm["consentement_marketing"].isin(["oui", "non"]),
    "ville non reconnue": O.canonique_ville(crm["ville"]).isna(),
    "naissance illisible": O.parse_naissance(crm["date_naissance"]).isna(),
    "ligne de test": crm["email"].eq("test@example.com"),
}
print(O.resume_controles(regles, len(crm)).to_string(index=False))
```

**Étape 3 — L'unicité.** Une ligne est redondante si son e-mail normalisé (espaces retirés, minuscules) est déjà apparu plus haut :

```python
cle = crm["email"].str.strip().str.lower()
redondante = cle.notna() & cle.ne("test@example.com") & cle.duplicated(keep="first")
print("lignes redondantes par e-mail :", int(redondante.sum()), "(", round(100 * redondante.mean(), 1), "% du fichier )")
```

**Lecture.** La complétude est tirée vers le bas par le consentement, la validité par le champ consentement et par la ville (des écritures différentes mais acceptables : un contrôle trop strict qui appelle une **normalisation**), l'unicité mesurée est partielle (corrigé 3.3).

**À vous.** Ajoutez un septième indicateur de validité : « le téléphone se normalise en dix chiffres » (utilisez `O.telephone_normalise`). Combien de lignes échouent ? Que vous apprend ce résultat sur la **sensibilité** de l'indicateur ?

### Application 3.2 — Écrire les contrôles du CRM et les rejouer en SQL (section 3.2)

**Objectif.** Passer des mesures aux **contrôles** : une gravité, un rapport trié, puis la même règle en SQL.

**Étape 1 — Le rapport.** On associe à chaque règle de l'application précédente une gravité décidée **avant** de regarder les résultats :

```python
gravite = {"e-mail mal formé": "erreur", "code postal ≠ 5 chiffres": "erreur", "consentement hors {oui, non}": "avertissement",
           "ville non reconnue": "avertissement", "naissance illisible": "erreur", "ligne de test": "erreur"}
rapport = O.resume_controles(regles, len(crm))
rapport["gravite"] = rapport["controle"].map(gravite)
print(rapport.sort_values(["gravite", "echecs"], ascending=[True, False]).to_string(index=False))
```

**Étape 2 — La quarantaine.** Les lignes de gravité « erreur » sont écartées vers une table à part ; le reste continue son chemin :

```python
masque_erreur = np.zeros(len(crm), bool)
for nom, m in regles.items():
    if gravite[nom] == "erreur":
        masque_erreur |= m.values
quarantaine, propres = crm[masque_erreur], crm[~masque_erreur]
print("en quarantaine :", len(quarantaine), "| conservées :", len(propres))
```

**Étape 3 — Les contraintes et les requêtes de contrôle.** On charge le CRM dans une base en mémoire. Une table avec des contraintes refuse l'insertion d'une ligne invalide :

```python
con = sqlite3.connect(":memory:")
crm.to_sql("crm", con, index=False)
con.execute("CREATE TABLE clients_propres (id_crm INTEGER PRIMARY KEY, code_postal TEXT CHECK (code_postal IS NULL OR length(code_postal) = 5))")
for cp in ["75012", "1234"]:
    try:
        con.execute("INSERT INTO clients_propres VALUES (NULL, ?)", (cp,)); print(cp, "accepté")
    except sqlite3.IntegrityError as e:
        print(cp, "refusé :", e)
```

```sql
SELECT COUNT(*) AS codes_postaux_invalides FROM crm WHERE code_postal IS NOT NULL AND length(code_postal) <> 5;
```

**À vous.** Écrivez la requête SQL qui compte les lignes dont le consentement est présent mais hors de la liste `oui`/`non`, puis vérifiez qu'elle redonne le chiffre de pandas.

### Application 3.3 — Plage ou dépendance ? (section 3.2.3)

**Objectif.** Comparer trois règles pour repérer les erreurs de saisie des 6 000 lignes de `montants_saisis.csv`, en s'aidant de la vérité pour **juger** chaque règle.

**Étape 1 — Les trois règles.** Une borne fixe, la règle statistique des 1,5 écart interquartile, et la règle de dépendance entre colonnes :

```python
q1, q3 = mont["montant"].quantile([0.25, 0.75])
r_fixe = mont["montant"] > 1000
r_iqr = mont["montant"] > q3 + 1.5 * (q3 - q1)
r_dep = (mont["montant"] <= 0) | (mont["montant"] > mont["quantite"] * mont["prix_unitaire"] + 0.01)
verite = lire("verite_montants.csv")
vrai = mont.merge(verite, on="id_ligne")["anomalie"].notna()
for nom, r in {"borne fixe > 1000 €": r_fixe, "1,5 écart interquartile": r_iqr, "dépendance": r_dep}.items():
    print(f"{nom:26s} signalées {int(r.sum()):4d} | vraies {int((r & vrai).sum()):3d} | fausses alertes {int((r & ~vrai).sum()):3d}")
```

**Étape 2 — Qui trouve quoi ?** On regarde, par **type** d'anomalie, la part trouvée par chaque règle :

```python
tab = mont.merge(verite, on="id_ligne")
tab["fixe"], tab["iqr"], tab["dep"] = r_fixe.values, r_iqr.values, r_dep.values
res = tab[tab["anomalie"].notna()].groupby("anomalie")[["fixe", "iqr", "dep"]].mean().mul(100).round(0)
print(res.to_string())
```

**Lecture.** La règle de dépendance retrouve **tous** les types d'anomalie, sans fausse alerte, parce qu'elle compare le montant à la quantité et au prix. La règle statistique ne voit jamais les montants négatifs ni nuls (elle regarde vers le haut) et noie ses vraies alertes dans des centaines de grosses commandes légitimes. La borne fixe n'a aucune fausse alerte, mais elle ne trouve que les valeurs énormes : presque aucune décimale décalée de ×10 (le tableau donne la part trouvée par type), et rien du côté des signes et des zéros. Une règle de plage **ne voit que le haut de la distribution**.

**À vous.** Quelle valeur de borne fixe donnerait autant de vraies alertes que la règle des 1,5 écart interquartile ? Combien de fausses alertes de plus ?

### Application 3.4 — Détecter une rupture dans une série (section 3.2.5)

**Objectif.** Repérer le jour où l'export du site change d'unité, sans connaître la date, et vérifier que la caisse n'a pas de rupture comparable.

**Étape 1 — Le montant médian par jour.**

```python
site["date"] = pd.to_datetime(site["created_at"].str.replace("Z", ""), format="ISO8601").dt.normalize()
site["t"] = site["total"].map(O.montant_site_en_nombre)
jour = site.groupby("date")["t"].median()
rapport_jour = jour / jour.rolling(7).median().shift(1)
print(rapport_jour[rapport_jour > 10].head(3).round(0).to_string())
```

**Étape 2 — Un seuil, plusieurs fenêtres.** On vérifie que la date trouvée ne dépend pas de la fenêtre glissante :

```python
for fen in (3, 7, 14):
    r_ = jour / jour.rolling(fen).median().shift(1)
    print("fenêtre", fen, "jours : premier jour détecté", r_[r_ > 10].index[0].date())
```

**Étape 3 — La même question sur la caisse.** On compare le montant médian par ticket d'un mois à l'autre :

```python
tickets = caisse.dropna(subset=["montant"]).groupby(["fichier", "ticket"])["montant"].sum()
med = tickets.groupby("fichier").median()
print((med / med.shift(1)).round(2).describe()[["min", "max"]].to_string())
```

**À vous.** Que se passerait-il si la rupture était une division par dix (des euros devenus des dizaines d'euros) ? Votre seuil de 10 la détecterait-il ? Comment le choisir ?

### Application 3.5 — Réconcilier le site avec la base (section 3.3.3)

**Objectif.** Refaire la cascade du chiffre d'affaires du site, dans l'ordre : format, lignes parasites, définitions.

**Étape 1 — Compter et sommer.**

```python
t_export = site["total"].map(O.montant_site_en_nombre)
base_site = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")]
ca_base = base_site["id_commande"].map(lig.groupby("id_commande")["montant"].sum()).sum()
print("lignes :", len(site), "contre", len(base_site), "| somme :", round(t_export.sum(), 2), "contre", round(ca_base, 2))
```

**Étape 2 — Les unités, les tests, les copies.**

```python
apres = site["created_at"].str.endswith("Z")
t_eur = t_export.where(~apres, t_export / 100)
test = site["customer_email"].eq("test@example.com")
copie = site["order_ref"].duplicated(keep="first") & ~test
etapes = {"unité": t_eur.sum() - t_export.sum(), "tests": -t_eur[test].sum(), "copies": -t_eur[copie].sum()}
print({k: round(float(v), 2) for k, v in etapes.items()})
print("écart restant :", abs(round(t_export.sum() + sum(etapes.values()) - ca_base, 2)))
```

**Étape 3 — Les totaux journaliers.** On vérifie que, jour par jour, l'export nettoyé et la base donnent la même chose (et pas seulement l'année) :

```python
propre = site[~test & ~copie].assign(eur=t_eur[~test & ~copie])
par_jour_site = propre.groupby("date")["eur"].sum()
base_j = base_site.assign(m=base_site["id_commande"].map(lig.groupby("id_commande")["montant"].sum())).groupby(pd.to_datetime(base_site["date_commande"]))["m"].sum()
print("jours comparés :", len(base_j), "| écart journalier maximal :", round(float((par_jour_site - base_j).abs().max()), 4), "€")
```

**À vous.** Retirez de l'export les commandes annulées et dites quel chiffre vous annonceriez à la gérante, avec quelle phrase de définition.

### Application 3.6 — Réconcilier la caisse avec la base (section 3.3.4)

**Objectif.** Lire douze fichiers de formats différents, puis expliquer l'écart entre la somme des lignes et le total que la caisse imprime.

**Étape 1 — Les formats.** La fonction `O.lire_caisse_fichier` renvoie, pour un fichier, les lignes, le total affiché et les caractéristiques du format :

```python
for nom in ["caisse_2025-03.csv", "caisse_2025-08.csv", "caisse_2025-11.csv"]:
    df, total, meta = O.lire_caisse_fichier(os.path.join(D, "caisse", nom))
    print(nom, "|", meta["encodage"], "| séparateur", repr(meta["separateur"]), "|", meta["colonnes"], "colonnes |", len(df), "lignes | total", total)
```

**Étape 2 — Les trois temps.**

```python
base_b = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande")
base_b = base_b[(base_b["canal"] == "Boutique") & (base_b["date_commande"] >= "2025-01-01")]
print("compter :", len(caisse), "contre", len(base_b))
print("sommer  :", round(caisse["montant"].sum(), 2), "(lu) |", round(fichiers["total_affiche"].sum(), 2), "(affiché) |", round(base_b["montant"].sum(), 2), "(base)")
```

**Étape 3 — Le rapprochement ligne à ligne.** La clé est ticket + article + quantité + prix + rang :

```python
prod_nom = prod[["id_produit", "nom_produit"]]
r = O.rapprocher_caisse_base(caisse, cmd, lig, prod_nom)
print(r["_merge"].value_counts().to_string())
copies = r[r["_merge"] == "left_only"]
vides = r[(r["_merge"] == "both") & r["montant"].isna()]
print("copies :", len(copies), "| montants vides retrouvés en base :", len(vides))
```

**Étape 4 — La cascade.**

```python
qp = vides["qte"] * vides["prix_unitaire"]
etapes = [caisse["montant"].sum(), -copies["montant"].sum(), qp.sum(), -(qp - vides["montant_base"]).sum()]
print([round(float(e), 2) for e in etapes], "| total obtenu :", round(sum(etapes), 2), "| base :", round(base_b["montant"].sum(), 2))
```

**À vous.** Refaites la cascade **mois par mois** (utilisez la colonne `fichier`) et construisez un tableau de douze lignes où l'écart restant vaut zéro partout.

### Application 3.7 — Réconcilier le catalogue du fournisseur (section 3.3.5)

**Objectif.** Rapprocher deux listes sans clé commune, et mesurer l'effet de la **tolérance de prix**.

**Étape 1 — La clé « nom normalisé ».**

```python
cle_nom = lambda s: s.map(lambda x: O.sans_accents(str(x)).lower().strip())
cat["cle"], prod["cle"] = cle_nom(cat["designation"]), cle_nom(prod["nom_produit"])
m = cat.merge(prod[["id_produit", "cle", "cout_achat"]], on="cle", how="left")
m["ecart_prix"] = (m["prix_achat_ht"] / m["cout_achat"] - 1).abs()
print(len(m), "lignes après jointure pour", len(cat), "lignes de catalogue ;", int(m["id_produit"].isna().sum()), "sans correspondance")
```

**Étape 2 — La tolérance de prix.** On fait varier le seuil et l'on compte appariés, ambigus et non appariés :

```python
for tol in (0.01, 0.035, 0.10):
    ok = m[m["ecart_prix"] <= tol]
    amb = ok["code_fournisseur"].duplicated(keep=False)
    print(f"tolérance {tol:5.1%} : appariés {ok['code_fournisseur'].nunique():3d} | codes ambigus {ok.loc[amb, 'code_fournisseur'].nunique():2d} | non appariés {len(cat) - ok['code_fournisseur'].nunique():3d}")
```

**Étape 3 — La vérité.** Avec la vérité, on mesure la **justesse** des appariements sans ambiguïté :

```python
vprod = lire("verite_produits.csv")
ok = m[m["ecart_prix"] <= 0.035]
sans_amb = ok[~ok["code_fournisseur"].duplicated(keep=False)].merge(vprod, on="code_fournisseur", suffixes=("", "_vrai"))
print("appariements sans ambiguïté :", len(sans_amb), "| exacts :", int((sans_amb["id_produit"] == sans_amb["id_produit_vrai"]).sum()))
```

**À vous.** À 10 % de tolérance, y a-t-il des appariements **faux** parmi ceux que vous croyez certains ? Qu'en concluez-vous sur le choix d'un seuil trop large ?

### Application 3.8 — Tolérances, règles et rapport d'exceptions (section 3.4)

**Objectif.** Évaluer cinq règles de réconciliation avant et après nettoyage, puis construire le rapport d'exceptions par propriétaire.

**Étape 1 — Les règles.** On reprend les objets des applications précédentes (`t_export`, `ca_base`, `propre`, `caisse`, `base_b`, `copies`, `vides`) :

```python
def dans_la_tolerance(a, b, abs_tol=0.01, rel_tol=0.0):
    return abs(a - b) <= max(abs_tol, rel_tol * abs(b))

regles_r = [("R1", "CA du site", t_export.sum(), ca_base, propre["eur"].sum()), ("R2", "Commandes du site", len(site), len(base_site), len(propre)),
            ("R3", "CA de la caisse", caisse["montant"].sum(), base_b["montant"].sum(), sum(etapes)), ("R4", "Lignes de la caisse", len(caisse), len(base_b), len(caisse) - len(copies))]
for i, n, a, b, ap in regles_r:
    print(i, f"{n:20s}", "avant :", "OK " if dans_la_tolerance(a, b, 1.0) else "ÉCART", "| après :", "OK" if dans_la_tolerance(ap, b, 1.0) else "ÉCART")
```

**Étape 2 — Les exceptions.** On rassemble les exceptions avec leur propriétaire et on les compte :

```python
def exceptions(source, nature, ref, montant, proprietaire):
    return pd.DataFrame({"source": source, "nature": nature, "reference": ref, "montant": montant, "proprietaire": proprietaire, "statut": "à traiter"})

exc = pd.concat([exceptions("Caisse", "copie de scan", copies["fichier"] + " / " + copies["ticket"], copies["montant"], "équipe caisse"),
                 exceptions("Caisse", "montant vide", vides["fichier"] + " / " + vides["ticket"], vides["montant_base"], "équipe caisse"),
                 exceptions("Site", "copie d'export", site.loc[copie, "order_ref"], t_eur[copie], "équipe web"),
                 exceptions("Site", "commande de test", site.loc[test, "order_ref"], t_eur[test], "équipe web")], ignore_index=True)
print(exc.groupby("proprietaire").agg(exceptions=("reference", "count"), montant=("montant", "sum")).round(2).to_string())
```

**À vous.** Ajoutez la règle R5 « taux d'appariement du catalogue ≥ 90 % » et les exceptions du catalogue (propriétaire : « achats »). Quelle équipe a le plus d'exceptions à traiter ? Laquelle en a pour le plus d'argent ?

### Application 3.9 — pandera et Great Expectations sur l'export du site (section 3.5)

**Objectif.** Déclarer les contrôles de l'export du site avec pandera, puis les rejouer avec Great Expectations, et comparer les comptes aux vôtres.

**Étape 1 — Le schéma pandera.**

```python
import pandera.pandas as pa
schema_site = pa.DataFrameSchema({
    "order_ref": pa.Column(str, unique=True),
    "status": pa.Column(str, pa.Check.isin(["paid", "cancelled"])),
    "currency": pa.Column(str, pa.Check.isin(["EUR"])),
    "customer_email": pa.Column(str, pa.Check(lambda s: s != "test@example.com", name="pas un e-mail de test")),
})
try:
    schema_site.validate(site[["order_ref", "status", "currency", "customer_email"]], lazy=True)
except pa.errors.SchemaErrors as e:
    echecs = e.failure_cases
print(echecs.groupby(["column", "check"])["index"].nunique().to_string())
```

**Étape 2 — La même chose avec Great Expectations.**

```python
import great_expectations as gx
E = gx.expectations
with O.silencieux():
    ctx = gx.get_context(mode="ephemeral")
    lot_def = ctx.data_sources.add_pandas("boutique").add_dataframe_asset("site").add_batch_definition_whole_dataframe("tout")
    suite = ctx.suites.add(gx.ExpectationSuite(name="site"))
    for e in [E.ExpectColumnValuesToBeUnique(column="order_ref"), E.ExpectColumnValuesToBeInSet(column="status", value_set=["paid", "cancelled"]),
              E.ExpectColumnValuesToBeInSet(column="currency", value_set=["EUR"])]:
        suite.add_expectation(e)
    res = ctx.validation_definitions.add(gx.ValidationDefinition(name="site", data=lot_def, suite=suite)).run(batch_parameters={"dataframe": site})
for x in res.results:
    print(f"{x.expectation_config.type:40s} {'OK' if x.success else 'KO'} | anormales : {x.result['unexpected_count']}")
```

```python hide
num("a9_uniq_pa", int(echecs[echecs["column"] == "order_ref"]["index"].nunique())); num("a9_uniq_maison", int(site["order_ref"].duplicated().sum()))
num("a9_statut", int(echecs[echecs["column"] == "status"]["index"].nunique())); num("a9_devise", int(echecs[echecs["column"] == "currency"]["index"].nunique())); num("a9_test", int(echecs[echecs["column"] == "customer_email"]["index"].nunique()))
```

**Lecture.** Les deux outils donnent les **mêmes** comptes pour le statut ({{a9_statut}}) et la devise ({{a9_devise}}) ; le test de l'e-mail ({{a9_test}} lignes) n'existe que dans pandera (la règle de Great Expectations n'a pas été écrite). Pour l'unicité, ils comptent {{a9_uniq_pa}} lignes : les **deux** membres de chaque paire de numéros identiques, alors que `duplicated(keep="first")` n'en compte que {{a9_uniq_maison}} (la copie). Même règle, autre **convention de comptage** : avant de comparer un nombre d'échecs entre deux outils, on vérifie ce qu'il compte.

**À vous.** Les « statuts » en échec sont-ils de vraies erreurs ou des écritures différentes (casse) d'une même valeur ? Modifiez la règle (ou normalisez avant) pour ne signaler que ce qui est réellement erroné.

## Exercices

### Exercice 3.1 ⭐ — La complétude du CRM (section 3.1.2)

Calculez la complétude de chaque colonne du CRM, puis la part des fiches où l'e-mail, le téléphone et la ville sont **tous** renseignés. Pourquoi ce taux est-il égal à celui de l'e-mail seul ?

### Exercice 3.2 ⭐ — Valider un téléphone (section 3.1.3)

Après suppression de tous les séparateurs, un téléphone est valide s'il se compose de dix chiffres et commence par `0` (les numéros écrits `+33` sont ramenés à `0`). Combien de téléphones sont invalides ? Que dit ce chiffre sur l'intérêt de cet indicateur ? Quelle règle supplémentaire détecterait les lignes de test ?

### Exercice 3.3 ⭐⭐ — Choisir une clé d'unicité (section 3.1.3 et 3.1.8)

On veut mesurer la redondance du CRM. Comparez trois clés : l'e-mail normalisé, le téléphone normalisé, et « e-mail **ou** téléphone ». Pour chacune, combien de lignes sont redondantes ? Ouvrez ensuite la vérité (`verite_crm.csv`) : combien de lignes redondantes la vérité compte-t-elle, et combien de groupes de lignes mélangent des **clients différents** pour chaque clé ?

### Exercice 3.4 ⭐⭐ — Le tableau de bord avant et après correction (section 3.1.7)

Dans le tableau de bord du livre, l'exactitude et la cohérence de l'export du site sont à 59,8 %. Recalculez l'indicateur « total conforme à la base » après avoir corrigé l'unité (division par cent après le 15 septembre) et retiré les commandes de test et les copies. Que devient-il ?

### Exercice 3.5 ⭐ — La moyenne qui cache (section 3.1.8)

Pour chaque source, comparez la **moyenne** des indicateurs de validité et le **plus mauvais** indicateur de validité (utilisez `O.indicateurs_qualite`). Dans quel cas la moyenne rassure-t-elle à tort ?

### Exercice 3.6 ⭐ — Trop strict ou normalisable ? (section 3.2.2)

La règle « la devise du site vaut `EUR` » échoue pour une partie des lignes. Combien ? Montrez que ces échecs sont de simples écritures différentes (`eur`, `€`) en normalisant avant de contrôler, et dites quel contrôle vous garderiez en production.

### Exercice 3.7 ⭐⭐ — Un contrôle de dépendance (section 3.2.3)

Pour les fichiers d'octobre à décembre de la caisse (qui contiennent la colonne de remise), vérifiez que le montant égale `quantité × prix × (1 − remise / 100)` à un centime près, sur les lignes où le montant est présent. Pourquoi ce contrôle est-il impossible pour les fichiers de janvier à septembre ?

### Exercice 3.8 ⭐⭐ — La caisse a-t-elle une rupture ? (section 3.2.5)

Calculez le panier moyen (par ticket) par mois dans la caisse. Quel est le plus grand rapport entre deux mois consécutifs ? Ce rapport ressemble-t-il à celui du site, le 15 septembre ? Comment l'expliquez-vous ?

### Exercice 3.9 ⭐⭐ — Des contraintes SQL (section 3.2.7)

Chargez le CRM dans une base SQLite en mémoire. Écrivez (1) une table avec des contraintes `CHECK` sur le code postal et le consentement ; (2) la requête qui renvoie les e-mails présents plus d'une fois (après `lower(trim(...))`), avec leur nombre d'occurrences ; (3) la requête qui compte les commandes du site sans aucune ligne.

### Exercice 3.10 ⭐⭐ — La cascade de la caisse en décembre (section 3.3.4)

Reprenez la cascade de la section 3.3.4, mais pour le seul mois de **décembre**. Quels sont le nombre de copies, le nombre de montants vides et l'écart restant ?

### Exercice 3.11 ⭐⭐⭐ — La cascade du site en septembre (section 3.3.3)

Le mois de septembre est coupé en deux par le changement d'unité. Faites la cascade du chiffre d'affaires du site pour **septembre seul** : combien de commandes avant et après le 15 ? Quel montant l'erreur d'unité ajoute-t-elle à la somme brute du mois ? L'écart restant est-il nul ?

### Exercice 3.12 ⭐⭐⭐ — Tolérance et exceptions par mois (section 3.4)

Pour la caisse, calculez par mois l'écart relatif entre la somme des montants lus et le total affiché. Avec une tolérance relative de 0,5 %, combien de mois passent **avant** nettoyage ? Après nettoyage (copies retirées, vides complétés) ? Construisez enfin le tableau d'exceptions par fichier (copies et montants vides) et dites quel mois est le plus chargé.

## Corrigés

### Corrigé 3.1

```python
print((crm.notna().mean() * 100).round(1)[lambda s: s < 100].to_string())
f = crm[["email", "telephone", "ville"]].notna().all(axis=1)
print("e-mail, téléphone et ville renseignés :", round(100 * f.mean(), 1), "% | e-mail seul :", round(100 * crm["email"].notna().mean(), 1), "%")
```

Le téléphone et la ville sont renseignés à 100 % : la fiche « complète » sur ces trois colonnes ne dépend donc que de l'e-mail, et les deux taux sont égaux. Un indicateur composé n'est jamais plus fin que sa colonne la plus lacunaire.

### Corrigé 3.2

```python
tel = O.telephone_normalise(crm["telephone"])
print("téléphones invalides :", int(tel.isna().sum()), "| numéros nuls :", int((tel == "0000000000").sum()))
```

Aucun téléphone n'est invalide : **toutes** les écritures se normalisent, y compris `0000000000`, la valeur bidon des lignes de test. Un indicateur de validité de forme ne détecte pas les valeurs absurdes mais bien formées. Pour détecter les lignes de test, il faut une **règle de contenu** (« le téléphone n'est pas une suite de zéros », « l'e-mail n'est pas celui de l'équipe »), ce qui relève de la validité **métier**, au-delà de la forme.

### Corrigé 3.3

```python
v = lire("verite_crm.csv").assign(id_crm=lambda d: d["id_crm"].astype(str))
reel = crm[crm["email"].ne("test@example.com")].copy()
reel["tel"] = O.telephone_normalise(reel["telephone"]); reel["cle"] = reel["email"].str.strip().str.lower()
reel = reel.merge(v[["id_crm", "id_client"]], on="id_crm")
print("lignes redondantes selon la vérité :", int(v["est_doublon"].sum()))
for nom, col in {"e-mail": "cle", "téléphone": "tel"}.items():
    k = reel[col].dropna()
    melanges = int((reel.loc[k.index].groupby(col)["id_client"].nunique() > 1).sum())
    print(f"{nom:10s} redondantes {int(k.duplicated().sum()):4d} | groupes qui mélangent des clients : {melanges}")
ou = (reel["cle"].notna() & reel["cle"].duplicated()) | (reel["tel"].notna() & reel["tel"].duplicated())
print("e-mail ou téléphone : redondantes", int(ou.sum()))
```

```python hide
num("c3_vrai", int(v["est_doublon"].sum())); num("c3_mail", int((reel["cle"].notna() & reel["cle"].duplicated()).sum())); num("c3_tel", int((reel["tel"].notna() & reel["tel"].duplicated()).sum())); num("c3_ou", int(ou.sum()))
num("c3_extra", int(ou.sum()) - int(v["est_doublon"].sum()))
num("c3_melange_mail", int((reel[reel["cle"].notna()].groupby("cle")["id_client"].nunique() > 1).sum()))
```

La vérité compte {{c3_vrai:,d}} lignes redondantes. Le **téléphone** en trouve {{c3_tel:,d}}, soit le compte exact, sans aucun groupe qui mélange des clients ; l'**e-mail** n'en trouve que {{c3_mail}}, et {{c3_melange_mail}} de ses groupes mélangent des clients différents (des homonymes dont l'adresse coïncide) ; « e-mail ou téléphone » en trouve {{c3_ou:,d}}, soit {{c3_extra}} de plus que la vérité : ce sont ces homonymes. Le meilleur indicateur est celui dont la clé est **la plus stable d'une copie à l'autre** : ici le numéro de téléphone (les copies le conservent, à la mise en forme près), pas l'e-mail (absent ou abîmé dans environ une copie sur trois). Notez qu'un **compte** égal à la vérité ne prouve pas que chaque ligne est la bonne ; ici le contrôle par groupe (aucun mélange de clients) le confirme.

### Corrigé 3.4

```python
t_export = site["total"].map(O.montant_site_en_nombre)
apres = site["created_at"].str.endswith("Z")
t_eur = t_export.where(~apres, t_export / 100)
idc = site["order_ref"].str.extract(r"WEB-(\d{6})")[0].astype(float)
base_t = idc.map(lig.groupby("id_commande")["montant"].sum())
garde = ~site["customer_email"].eq("test@example.com") & ~site["order_ref"].duplicated()
for nom, serie in {"lecture brute": t_export, "unité corrigée": t_eur}.items():
    ok = ((serie - base_t).abs() <= 0.01)[garde & base_t.notna()]
    print(f"{nom:16s} commandes exactes : {100 * ok.mean():.1f} %")
```

Une fois l'unité corrigée, **toutes** les commandes sont exactes (100 %). Le tableau de bord à 59,8 % ne mesurait pas un défaut diffus mais **un seul défaut de lot** : un changement d'unité sur 40 % des lignes.

### Corrigé 3.5

```python
ind = O.indicateurs_qualite(crm, site, lire("site_lignes.csv"), caisse, fichiers, cmd, lig, prod, REF)
val = ind[ind["dimension"] == "Validité"].groupby("source")["valeur"].agg(["mean", "min"]).round(1)
print(val.to_string())
```

Pour le site, la moyenne des indicateurs de validité (autour de 80 %) cache un indicateur à 61 % (le statut en minuscules) et un autre à 99 % (les commandes de test) : la moyenne rassure à tort sur une colonne qui échoue pour **quatre lignes sur dix**. On regarde donc **chaque indicateur**, en particulier le plus mauvais.

### Corrigé 3.6

```python
ecart = ~site["currency"].eq("EUR")
norm = site["currency"].str.upper().replace({"€": "EUR"})
print("devises ≠ EUR :", int(ecart.sum()), "| après normalisation :", int((~norm.eq("EUR")).sum()))
```

La règle stricte échoue pour environ un cinquième des lignes, mais **aucune** n'est une vraie erreur : `eur` et `€` sont deux écritures d'euros. En production, on garde le contrôle **après** normalisation (« la devise normalisée vaut EUR »), ce qui échoue seulement si une autre devise apparaît.

### Corrigé 3.7

```python
trim4 = caisse[caisse["fichier"] >= "caisse_2025-10.csv"].dropna(subset=["montant"])
attendu = (trim4["qte"] * trim4["prix_unitaire"] * (1 - trim4["remise_pct"] / 100)).round(2)
echec = (trim4["montant"] - attendu).abs() > 0.011
print("lignes testées :", len(trim4), "| en échec :", int(echec.sum()))
```

Aucune ligne n'échoue : le montant est cohérent avec la quantité, le prix et la remise. Pour janvier à septembre, la colonne de remise **n'existe pas** dans le fichier : on ne peut contrôler que l'inégalité `montant ≤ quantité × prix`, pas l'égalité. Un contrôle dépend de l'**information disponible** dans la source.

### Corrigé 3.8

```python
pm = caisse.dropna(subset=["montant"]).groupby(["fichier", "ticket"])["montant"].sum().groupby("fichier").mean()
r_ = (pm / pm.shift(1)).dropna()
print("panier moyen par mois :", pm.round(1).tolist())
print("rapport maximal entre deux mois :", round(float(max(r_.max(), 1 / r_.min())), 2))
```

```python hide
num("rmax_caisse", round(float(max(r_.max(), 1 / r_.min())), 2))
```

Le rapport maximal est de {{rmax_caisse}} (de l'ordre de vingt pour cent, les variations de saison et de mix de produits) : **aucune rupture** comparable à celle du site (un rapport de l'ordre de 100). C'est cohérent avec ce que nous avons vu : les trois formats de la caisse changent la **forme** (séparateur, décimale) mais pas le **sens** des montants, qui restent en euros.

### Corrigé 3.9

```python
con = sqlite3.connect(":memory:")
crm.to_sql("crm", con, index=False); site.to_sql("site", con, index=False); site_l.to_sql("site_lignes", con, index=False)
con.execute("CREATE TABLE propres (id INTEGER PRIMARY KEY, code_postal TEXT CHECK (code_postal IS NULL OR length(code_postal) = 5), consentement TEXT CHECK (consentement IN ('oui', 'non')))")
print(con.execute("SELECT lower(trim(email)), COUNT(*) FROM crm WHERE email IS NOT NULL AND email <> 'test@example.com' GROUP BY 1 HAVING COUNT(*) > 1 ORDER BY 2 DESC LIMIT 3").fetchall())
print(con.execute("SELECT COUNT(*) FROM site s LEFT JOIN site_lignes l ON l.order_ref = s.order_ref WHERE l.order_ref IS NULL").fetchone())
```

La première requête renvoie les adresses les plus répétées (trois fois chacune) ; la seconde compte les commandes sans ligne : ce sont les commandes de test, que l'on a trouvées en 3.2.4. La table `propres` refuserait toute insertion avec un code postal à quatre chiffres ou un consentement hors liste.

### Corrigé 3.10

```python
r = O.rapprocher_caisse_base(caisse, cmd, lig, prod[["id_produit", "nom_produit"]])
dec = r[r["fichier"] == "caisse_2025-12.csv"]
copies = dec[dec["_merge"] == "left_only"]
vides = dec[(dec["_merge"] == "both") & dec["montant"].isna()]
qp = vides["qte"] * vides["prix_unitaire"]
lu = caisse.loc[caisse["fichier"] == "caisse_2025-12.csv", "montant"].sum()
total = fichiers.set_index("fichier").loc["caisse_2025-12.csv", "total_affiche"]
fin = lu - copies["montant"].sum() + qp.sum() - (qp - vides["montant_base"]).sum()
print("copies :", len(copies), "| vides :", len(vides), "| lu :", round(lu, 2), "| total affiché :", total, "| après cascade :", round(fin, 2), "| écart restant :", abs(round(fin - total, 2)))
```

L'écart restant est nul : le mois de décembre se réconcilie comme l'année entière, avec ses propres copies et ses montants vides (le nombre de copies de décembre, comme celui des vides, est proportionnel au nombre de lignes du mois, le plus élevé de l'année).

### Corrigé 3.11

```python
t_export = site["total"].map(O.montant_site_en_nombre)
apres = site["created_at"].str.endswith("Z")
t_eur = t_export.where(~apres, t_export / 100)
mois = pd.to_datetime(site["created_at"].str.replace("Z", ""), format="ISO8601").dt.month
sept = mois.eq(9)
test = site["customer_email"].eq("test@example.com"); copie = site["order_ref"].duplicated() & ~test
base_s = cmd[(cmd["canal"] == "Site") & cmd["date_commande"].str.startswith("2025-09")]
ca_base = base_s["id_commande"].map(lig.groupby("id_commande")["montant"].sum()).sum()
print("commandes avant/après le 15 :", int((sept & ~apres).sum()), "/", int((sept & apres).sum()))
print("somme brute :", round(t_export[sept].sum(), 2), "| erreur d'unité :", round((t_export[sept] - t_eur[sept]).sum(), 2), "| base :", round(ca_base, 2))
print("écart restant :", abs(round(t_eur[sept & ~test & ~copie].sum() - ca_base, 2)))
```

```python hide
num("s_avant", int((sept & ~apres).sum())); num("s_apres", int((sept & apres).sum())); num("s_brut", round(float(t_export[sept].sum()), 0)); num("s_unite", round(float((t_export[sept] - t_eur[sept]).sum()), 0)); num("s_base", round(float(ca_base), 0))
num("s_ratio", round(float(t_export[sept].sum() / ca_base), 0))
```

Septembre compte {{s_avant}} commandes en euros (avant le 15) et {{s_apres}} en centimes (à partir du 15). La somme brute du mois vaut {{s_brut:,.0f}} € alors que la base en donne {{s_base:,.0f}} € : **{{s_ratio:.0f}} fois** trop, parce que l'erreur d'unité ajoute {{s_unite:,.0f}} € à la somme. Une fois l'unité, les tests et les copies traités, l'écart restant est **nul**.

### Corrigé 3.12

```python
lu = caisse.groupby("fichier")["montant"].sum()
aff = fichiers.set_index("fichier")["total_affiche"]
r = O.rapprocher_caisse_base(caisse, cmd, lig, prod[["id_produit", "nom_produit"]])
copies = r[r["_merge"] == "left_only"].groupby("fichier")["montant"].sum()
vides = r[(r["_merge"] == "both") & r["montant"].isna()].groupby("fichier")["montant_base"].sum()
apres = lu - copies.reindex(lu.index, fill_value=0) + vides.reindex(lu.index, fill_value=0)
t = pd.DataFrame({"ecart_avant_pct": (100 * (lu - aff) / aff).round(2), "ecart_apres_pct": (100 * (apres - aff) / aff).round(3)})
print("mois dans la tolérance de 0,5 % : avant", int((t["ecart_avant_pct"].abs() <= 0.5).sum()), "| après", int((t["ecart_apres_pct"].abs() <= 0.5).sum()))
exc = pd.DataFrame({"copies": r[r["_merge"] == "left_only"].groupby("fichier").size(), "vides": r[(r["_merge"] == "both") & r["montant"].isna()].groupby("fichier").size()}).fillna(0).astype(int)
print(exc.assign(total=exc.sum(axis=1)).sort_values("total", ascending=False).head(3).to_string())
```

Avant nettoyage, aucun des douze mois n'est dans la tolérance de 0,5 % ; après, **tous** le sont, avec un écart de l'ordre du centime. Le fichier le plus chargé est celui de **décembre** (le plus grand nombre de lignes) : le nombre d'exceptions suit l'activité, un taux par ligne (3 % de vides, 0,5 % de copies) serait plus parlant qu'un compte brut.
