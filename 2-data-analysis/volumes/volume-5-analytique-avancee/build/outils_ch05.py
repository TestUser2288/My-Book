"""Chapitre 5 (volume V) : utiliser les LLM pour l'analyse — le HARNAIS de vérification, exécuté pour de vrai.

Aucun service de LLM n'est utilisé ici. Trois sources de « sorties de modèle » :
  1. un TOUT PETIT modèle local (SmolLM2-135M-Instruct, 135 millions de paramètres), dont les sorties sont ENREGISTRÉES dans `donnees/ch05-sorties-modele.json`
     (régénération : `REGENERER_SORTIES=1 python build/outils_ch05.py` ; le dossier des poids n'est pas versionné) ;
  2. des RÉPONSES ILLUSTRATIVES écrites par l'auteur (`donnees/ch05-propositions.json`) : elles représentent des erreurs fréquentes des LLM, elles ne sont
     la sortie d'aucun produit ;
  3. des imitations PROGRAMMÉES de défauts typiques (données synthétiques « naïves »), clairement présentées comme telles.
Ce qui est réel : l'entrepôt DuckDB en lecture seule, la validation sqlglot, l'exécution bornée, la comparaison à une référence, le vérificateur de nombres,
les tests de données synthétiques.

Ports réservés au chapitre : 20180-20189 (non utilisés ici).
"""
import hashlib
import html
import json
import os
import re
import tempfile
import threading
import warnings

import duckdb
import numpy as np
import pandas as pd
import sqlglot
from sqlglot import exp
from sqlglot.optimizer.qualify import qualify

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
TMP = os.environ.get("TMPDIR") or tempfile.gettempdir()

# ------------------------------------------------------------------------------------------------ le schéma présenté au modèle
# (table -> [(colonne, type, description)])
SCHEMA = {
    "commandes": [("id_commande", "INTEGER", "identifiant de la commande"), ("date_commande", "DATE", "jour de la commande"),
                  ("heure", "TIME", "heure de la commande"), ("id_client", "INTEGER", "client (clients.id_client)"),
                  ("canal", "VARCHAR", "Boutique, Site ou Réseaux"), ("mode_livraison", "VARCHAR", "Domicile, Point relais ou Retrait magasin"),
                  ("code_promo", "VARCHAR", "code utilisé ; NULL si aucun"),
                  ("frais_port", "DOUBLE", "frais de port facturés, UNE valeur par COMMANDE (pas par ligne)")],
    "lignes_commande": [("id_ligne", "INTEGER", "identifiant de la ligne"), ("id_commande", "INTEGER", "commandes.id_commande"),
                        ("id_produit", "INTEGER", "produits.id_produit"), ("quantite", "INTEGER", "quantité"),
                        ("prix_unitaire", "DOUBLE", "prix unitaire TTC"), ("remise_pct", "DOUBLE", "remise en %"),
                        ("montant", "DOUBLE", "montant TTC de la ligne après remise ; chiffre d'affaires = somme des montants")],
    "produits": [("id_produit", "INTEGER", "identifiant du produit (120)"), ("nom_produit", "VARCHAR", "nom : ATTENTION, 60 noms pour 120 produits"),
                 ("categorie", "VARCHAR", "6 catégories"), ("prix_vente", "DOUBLE", "prix de vente TTC"), ("cout_achat", "DOUBLE", "coût d'achat HT"),
                 ("fournisseur", "VARCHAR", "fournisseur"), ("date_lancement", "DATE", "date de lancement")],
    "clients": [("id_client", "INTEGER", "identifiant"), ("date_inscription", "DATE", "inscription"), ("annee_naissance", "INTEGER", "année de naissance"),
                ("ville", "VARCHAR", "Ville A … Ville T"), ("canal_acquisition", "VARCHAR", "canal d'acquisition"),
                ("fidelite", "INTEGER", "1 si carte de fidélité, sinon 0"), ("email_valide", "INTEGER", "0/1"), ("consentement_marketing", "INTEGER", "0/1")],
    "livraisons": [("id_commande", "INTEGER", "commandes.id_commande (uniquement les commandes Site et Réseaux)"), ("date_commande", "DATE", "jour de la commande"),
                   ("canal", "VARCHAR", "canal"), ("mode_livraison", "VARCHAR", "mode"), ("transporteur", "VARCHAR", "Transporteur A, B ou C"),
                   ("date_expedition", "DATE", "expédition"), ("date_livraison", "DATE", "livraison"), ("delai_promis_j", "INTEGER", "délai promis en jours"),
                   ("colis_abime", "INTEGER", "0/1"), ("retard", "INTEGER", "1 si livré après le délai promis")],
    "retours": [("id_retour", "INTEGER", "identifiant"), ("id_ligne", "INTEGER", "lignes_commande.id_ligne"), ("date_retour", "DATE", "date"),
                ("motif", "VARCHAR", "motif du retour"), ("montant_rembourse", "DOUBLE", "montant remboursé")],
}
TABLES = list(SCHEMA)
REGLES = [
    "Le chiffre d'affaires est la somme de lignes_commande.montant (montants TTC, TVA fictive de 20 %).",
    "Les noms de produits ne sont pas uniques (60 noms pour 120 produits) : regrouper par id_produit.",
    "frais_port est une valeur par commande : ne la sommez pas après une jointure avec lignes_commande.",
    "Les données vont du 2023-01-01 au 2025-12-31 : « le dernier trimestre » veut dire le 4e trimestre 2025.",
    "Écrivez UNE requête SELECT en dialecte DuckDB, sans commentaire.",
]


def ddl(avec_descriptions=False):
    """Le schéma sous forme d'instructions CREATE TABLE (avec ou sans commentaires de colonnes)."""
    out = []
    for t, cols in SCHEMA.items():
        lignes = [f"  {c} {typ}" + (f",  -- {d}" if avec_descriptions else ",") for c, typ, d in cols]
        lignes[-1] = lignes[-1].replace(",  --", "  --").rstrip(",")
        out.append(f"CREATE TABLE {t} (\n" + "\n".join(lignes) + "\n);")
    return "\n".join(out)


def schema_sqlglot():
    return {t: {c: typ for c, typ, _ in cols} for t, cols in SCHEMA.items()}


def prompt_texte(question, version="v3"):
    """Le prompt en 3 versions : v1 question seule ; v2 + schéma ; v3 + descriptions, règles et deux exemples."""
    amorce = f"-- Question : {question}\nSELECT"
    if version == "v1":
        return "-- Écrivez une requête DuckDB.\n" + amorce
    if version == "v2":
        return "-- Schéma DuckDB\n" + ddl() + "\n" + amorce
    exemples = ("-- Question : combien de commandes en 2023 ?\nSELECT COUNT(*) FROM commandes WHERE date_commande >= DATE '2023-01-01' AND date_commande < DATE '2024-01-01';\n"
                "-- Question : nombre de lignes par catégorie de produit\nSELECT p.categorie, COUNT(*) AS n FROM lignes_commande l JOIN produits p USING (id_produit) GROUP BY p.categorie;\n")
    regles = "\n".join("-- " + r for r in REGLES)
    return "-- Schéma DuckDB\n" + ddl(True) + "\n" + regles + "\n" + exemples + amorce


# ------------------------------------------------------------------------------------------------ l'entrepôt local (DuckDB, lecture seule)
def construire_entrepot(chemin):
    """Charge les CSV de la boutique dans un fichier DuckDB. `commandes` reçoit `frais_port` (règle fictive : domicile 4,90 ; point relais 2,90 ; sinon 0)."""
    if os.path.exists(chemin):
        os.remove(chemin)
    con = duckdb.connect(chemin)
    for t in TABLES:
        f = os.path.join(DONNEES, f"{t}.csv")
        if t == "commandes":
            con.execute(f"CREATE TABLE commandes AS SELECT *, CASE mode_livraison WHEN 'Domicile' THEN 4.9 WHEN 'Point relais' THEN 2.9 ELSE 0.0 END AS frais_port "
                        f"FROM read_csv_auto('{f}')")
        else:
            con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{f}')")
    con.close()
    return chemin


def ouvrir_lecture(chemin):
    """Connexion en LECTURE SEULE : le moteur lui-même refuse toute écriture, même si la validation avait laissé passer une requête."""
    con = duckdb.connect(chemin, read_only=True)
    con.execute("SET enable_external_access = false")
    return con


# ------------------------------------------------------------------------------------------------ le harnais : validation
INTERDITS = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.Command, exp.Copy, exp.Pragma, exp.Set, exp.Use, exp.Merge, exp.TruncateTable)


def valider(sql, tables_ok=None):
    """(ok, raison). Une SEULE instruction, de type SELECT, sur des tables connues, avec des colonnes qui existent, sans fonction de lecture de fichiers."""
    tables_ok = set(tables_ok or TABLES)
    try:
        arbres = sqlglot.parse(sql, dialect="duckdb")
    except sqlglot.errors.SqlglotError as e:
        return False, "syntaxe : " + str(e).split("\n")[0][:90]
    arbres = [a for a in arbres if a is not None]
    if len(arbres) != 1:
        return False, f"{len(arbres)} instructions (une seule autorisée)"
    a = arbres[0]
    for n in a.walk():
        if isinstance(n, INTERDITS):
            return False, "instruction interdite : " + type(n).__name__.upper()
    if not isinstance(a, exp.Query):
        return False, "ce n'est pas une requête SELECT (" + type(a).__name__ + ")"
    cte = {c.alias for c in a.find_all(exp.CTE)}
    for t in a.find_all(exp.Table):
        if not isinstance(t.this, exp.Identifier):
            return False, "fonction de table interdite : " + t.sql(dialect="duckdb")[:40]
        if t.name not in tables_ok and t.name not in cte:
            return False, f"table inconnue : {t.name}"
    try:
        qualify(a.copy(), schema=schema_sqlglot(), dialect="duckdb", validate_qualify_columns=True)
    except sqlglot.errors.SqlglotError as e:
        return False, "colonne inconnue : " + str(e).split(".")[0][:80]
    return True, "ok"


def executer(con, sql, limite=1000, delai=10.0):
    """Exécution bornée : au plus `limite` lignes, interrompue après `delai` secondes. Retourne (DataFrame | None, message)."""
    minuteur = threading.Timer(delai, con.interrupt)
    minuteur.start()
    try:
        cur = con.execute(f"SELECT * FROM ({sql.rstrip().rstrip(';')}) AS _q LIMIT {int(limite)}")
        return cur.fetchdf(), "ok"
    except duckdb.InterruptException:
        return None, f"interrompue après {delai:g} s"
    except duckdb.Error as e:
        return None, str(e).split("\n")[0][:110]
    finally:
        minuteur.cancel()


# ------------------------------------------------------------------------------------------------ comparaison à la référence
def _normaliser(df, ordonne):
    lignes = []
    for t in df.itertuples(index=False):
        lignes.append(tuple(round(float(v), 2) if isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool) and np.isfinite(v) else str(v) for v in t))
    return lignes if ordonne else sorted(lignes, key=lambda r: tuple(str(x) for x in r))


def egal(obtenu, ref, ordonne=False, tol=0.011):
    """Mêmes lignes (les noms de colonnes importent peu), mêmes valeurs à 0,01 près ; l'ordre ne compte que si `ordonne`."""
    if obtenu is None or obtenu.shape != ref.shape:
        return False
    a, b = _normaliser(obtenu, ordonne), _normaliser(ref, ordonne)
    for x, y in zip(a, b):
        for u, v in zip(x, y):
            if isinstance(u, float) and isinstance(v, float):
                if abs(u - v) > tol:
                    return False
            elif u != v:
                return False
    return True


def questions_or():
    return pd.read_csv(os.path.join(DONNEES, "ch05-questions-or.csv"))


def references(con, qs):
    """Résultat de la requête de référence de chaque question."""
    res = {}
    for r in qs.itertuples():
        df, msg = executer(con, r.sql_reference)
        assert df is not None, (r.id, msg)
        res[r.id] = df
    return res


def evaluer(con, qs, refs, propositions, source="", version=""):
    """Passe chaque proposition (dict id -> SQL) dans le harnais : validation, exécution, comparaison. Retourne un DataFrame, une ligne par question."""
    lignes = []
    for r in qs.itertuples():
        sql = propositions.get(r.id, "")
        ok, raison = valider(sql)
        if not ok:
            statut, detail = "refusée", raison
        else:
            df, msg = executer(con, sql)
            if df is None:
                statut, detail = "erreur d'exécution", msg
            elif egal(df, refs[r.id], ordonne=bool(r.ordre)):
                statut, detail = "juste", ""
            else:
                statut, detail = "exécutée mais fausse", f"{df.shape[0]} ligne(s) × {df.shape[1]} col. au lieu de {refs[r.id].shape[0]} × {refs[r.id].shape[1]}" \
                    if df.shape != refs[r.id].shape else "valeurs différentes"
        lignes.append({"id": r.id, "source": source, "version": version, "statut": statut, "detail": detail, "sql": sql})
    return pd.DataFrame(lignes)


def charger_json(nom):
    with open(os.path.join(DONNEES, nom), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------ boucle de correction avec journal
def boucle(con, question, generer, max_essais=3):
    """Appelle `generer(question, erreur_precedente)` jusqu'à une requête acceptée par le harnais, au plus `max_essais` fois. Retourne (sql, journal).
    Attention : la boucle corrige les ERREURS (syntaxe, colonne, exécution), pas les réponses plausibles mais fausses."""
    journal, erreur = [], None
    for essai in range(1, max_essais + 1):
        sql = generer(question, erreur)
        ok, raison = valider(sql)
        if ok:
            df, msg = executer(con, sql)
            if df is not None:
                journal.append({"essai": essai, "resultat": "acceptée", "message": f"{df.shape[0]} ligne(s)"})
                return sql, journal
            raison = msg
        journal.append({"essai": essai, "resultat": "rejetée", "message": raison})
        erreur = raison
    return None, journal


# ------------------------------------------------------------------------------------------------ chiffres d'un rapport et vérificateur de nombres
def faits_mensuels(con, annee=2025, mois=12):
    """Les chiffres calculés (pas les données brutes) qu'on transmet au modèle pour rédiger le commentaire d'un mois."""
    q = f"""WITH m AS (SELECT year(c.date_commande) a, month(c.date_commande) mo, SUM(l.montant) ca, COUNT(DISTINCT c.id_commande) n
                 FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY ALL)
            SELECT * FROM m WHERE (a, mo) IN (({annee}, {mois}), ({annee}, {mois - 1}), ({annee - 1}, {mois}))"""
    m = con.execute(q).fetchdf().set_index(["a", "mo"])
    ca, n = float(m.loc[(annee, mois), "ca"]), int(m.loc[(annee, mois), "n"])
    ca_p, n_p = float(m.loc[(annee, mois - 1), "ca"]), int(m.loc[(annee, mois - 1), "n"])
    ca_a, n_a = float(m.loc[(annee - 1, mois), "ca"]), int(m.loc[(annee - 1, mois), "n"])
    cat = con.execute(f"""SELECT p.categorie, SUM(l.montant) ca FROM commandes c JOIN lignes_commande l USING (id_commande) JOIN produits p USING (id_produit)
                         WHERE year(c.date_commande) = {annee} AND month(c.date_commande) = {mois} GROUP BY ALL ORDER BY ca DESC LIMIT 1""").fetchdf()
    ret = con.execute(f"""SELECT 100.0 * AVG(retard) FROM livraisons WHERE year(date_commande) = {annee} AND month(date_commande) = {mois}""").fetchone()[0]
    return {"mois": f"{MOIS[mois - 1]} {annee}", "ca": round(ca), "commandes": n, "panier_moyen": round(ca / n, 1),
            "ca_vs_mois_precedent_pct": round(100 * (ca / ca_p - 1), 1), "ca_vs_annee_precedente_pct": round(100 * (ca / ca_a - 1), 1),
            "commandes_vs_annee_precedente_pct": round(100 * (n / n_a - 1), 1), "categorie_leader": cat.iloc[0, 0],
            "part_categorie_leader_pct": round(100 * float(cat.iloc[0, 1]) / ca, 1), "livraisons_en_retard_pct": round(float(ret), 1)}


NOMBRE = re.compile(r"(?<![\w.])([+\-−–]?)(\d{1,3}(?:[  ]\d{3})+|\d+)(?:,(\d+))?\s*(%|k€|M€|€|points?)?")


def extraire_nombres(texte):
    """Tous les nombres d'un texte français (« 1 325 k€ », « −3,4 % », « 12 »), avec leur unité, leur position et leur précision (décimales écrites)."""
    out = []
    for m in NOMBRE.finditer(texte):
        signe, ent, dec, unite = m.groups()
        v = float(ent.replace(" ", "").replace(" ", "") + ("." + dec if dec else ""))
        if signe in ("-", "−", "–"):
            v = -v
        out.append({"texte": m.group(0).strip(), "valeur": v, "unite": unite or "", "decimales": len(dec) if dec else 0, "debut": m.start(), "fin": m.end(), "signe": bool(signe)})
    return out


def valeurs_autorisees(faits):
    """Les valeurs qu'un texte a le droit de citer, avec leur unité : les faits, leurs conversions évidentes (€ → k€ → M€) et leurs valeurs absolues."""
    ok = []
    for cle, v in faits.items():
        if isinstance(v, (int, float)):
            u = "%" if cle.endswith("pct") else ("€" if cle in ("ca", "panier_moyen") else "")
            ok.append((cle, float(v), u))
            if u == "€" and cle == "ca":
                ok.append((cle, v / 1000, "k€"))
                ok.append((cle, v / 1e6, "M€"))
            if u == "%":
                ok.append((cle, abs(float(v)), "%"))
    return ok


def verifier_nombres(texte, faits, annees=(2024, 2025, 2026)):
    """Compare chaque nombre du texte aux faits. Retourne un DataFrame : nombre, unité, statut (« confirmé » / « introuvable » / « unité douteuse »), fait correspondant.
    Tolérance : l'arrondi implicite du nombre écrit (nombre de décimales). Les années, jours et mois cités (« décembre », « 2025 ») sont ignorés."""
    ok = valeurs_autorisees(faits)
    lignes = []
    for n in extraire_nombres(texte):
        suite = texte[n["fin"]:n["fin"] + 12].lower().strip()
        if n["unite"] == "" and (n["valeur"] in annees or suite.startswith(MOIS)):
            continue
        tol = 0.5 * 10 ** (-n["decimales"])
        trouve = None
        autres_unites = None
        for cle, v, u in ok:
            valeur = n["valeur"]
            if abs(abs(valeur) - abs(v)) <= tol + 1e-9:
                if u == n["unite"] or (u == "" and n["unite"] == ""):
                    trouve = cle
                    break
                autres_unites = cle
        statut = "confirmé" if trouve else ("unité douteuse" if autres_unites else "introuvable")
        lignes.append({"nombre": n["texte"], "unité": n["unite"], "statut": statut, "fait": trouve or autres_unites or "", "debut": n["debut"], "fin": n["fin"]})
    return pd.DataFrame(lignes)


MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre")
MOTS_HAUSSE = ("hausse", "augment", "progress", "croît", "croit", "gagne", "monte", "mieux")
MOTS_BAISSE = ("baisse", "recul", "diminu", "perd", "chute", "repli", "moins bien")


def verifier_directions(texte, faits):
    """Contrôle les phrases qui citent une évolution : le sens écrit (hausse/baisse) doit être celui du fait. Une phrase par fait, repérée par un mot-clé."""
    cles = {"ca_vs_mois_precedent_pct": ("novembre", "mois précédent"), "ca_vs_annee_precedente_pct": ("décembre 2024", "an dernier", "année précédente", "2024"),
            "commandes_vs_annee_precedente_pct": ("commandes",)}
    res = []
    for ph in re.split(r"(?<=[.!?])\s+", texte):
        bas = ph.lower()
        sens = "hausse" if any(m in bas for m in MOTS_HAUSSE) else ("baisse" if any(m in bas for m in MOTS_BAISSE) else None)
        if sens is None:
            continue
        for cle, mots in cles.items():
            if cle in faits and any(m in bas for m in mots) and (cle != "commandes_vs_annee_precedente_pct" or "commandes" in bas):
                reel = "hausse" if faits[cle] > 0 else "baisse"
                res.append({"phrase": ph[:80], "écrit": sens, "réel": reel, "statut": "confirmé" if sens == reel else "sens contradictoire", "fait": cle})
                break
    return pd.DataFrame(res, columns=["phrase", "écrit", "réel", "statut", "fait"])


def annoter_html(texte, verif):
    """Le texte avec chaque nombre surligné : vert (confirmé), orange (unité douteuse), rouge (introuvable)."""
    couleurs = {"confirmé": "#d6f0e3", "unité douteuse": "#fde4c8", "introuvable": "#f9c9c8"}
    out, pos = "", 0
    for r in verif.sort_values("debut").itertuples():
        out += html.escape(texte[pos:r.debut]) + f'<mark style="background:{couleurs[r.statut]};padding:1px 3px;border-radius:3px;white-space:nowrap" title="{r.statut}">' + html.escape(texte[r.debut:r.fin]) + "</mark>"
        pos = r.fin
    return out + html.escape(texte[pos:])


# ------------------------------------------------------------------------------------------------ données synthétiques : générateurs et batterie de tests
def charger_reel(con):
    """Table de lignes « à plat » du réel (une ligne = une ligne de commande) pour comparer aux jeux synthétiques."""
    return con.execute("""SELECT c.id_commande, c.id_client, c.date_commande, c.canal, l.id_produit, l.quantite, l.prix_unitaire, l.montant
                          FROM commandes c JOIN lignes_commande l USING (id_commande) WHERE year(c.date_commande) = 2024""").fetchdf()


def synthetique_regles(reel, produits, n_commandes=6000, seed=2024):
    """Générateur À RÈGLES : le catalogue (non personnel), la saisonnalité mensuelle, la répartition des canaux, le nombre d'articles et les quantités sont
    estimés sur l'agrégat réel, puis tirés ; chaque ligne référence une commande et un produit qui existent."""
    rng = np.random.default_rng(seed)
    cmd = reel.drop_duplicates("id_commande")
    p_mois = cmd["date_commande"].dt.month.value_counts(normalize=True).sort_index()
    p_canal = cmd["canal"].value_counts(normalize=True)
    nb_art = reel.groupby("id_commande").size().value_counts(normalize=True).sort_index()
    p_qte = reel["quantite"].value_counts(normalize=True).sort_index()
    mois = rng.choice(p_mois.index, n_commandes, p=p_mois.values)
    jour = rng.integers(1, 29, n_commandes)
    dates = pd.to_datetime({"year": 2024, "month": mois, "day": jour})
    canaux = rng.choice(p_canal.index, n_commandes, p=p_canal.values)
    clients = rng.zipf(1.6, n_commandes) % 1500 + 1                      # quelques clients très actifs, beaucoup de clients occasionnels
    ids = np.arange(1, n_commandes + 1)
    cmds = pd.DataFrame({"id_commande": ids, "id_client": clients, "date_commande": dates, "canal": canaux})
    k = rng.choice(nb_art.index, n_commandes, p=nb_art.values)
    l = cmds.loc[cmds.index.repeat(k)].reset_index(drop=True)
    prod = produits.sample(len(l), replace=True, random_state=seed, weights=None).reset_index(drop=True)
    l["id_produit"] = prod["id_produit"].to_numpy()
    l["quantite"] = rng.choice(p_qte.index, len(l), p=p_qte.values)
    l["prix_unitaire"] = prod["prix_vente"].to_numpy()
    l["montant"] = (l["quantite"] * l["prix_unitaire"]).round(2)
    return l[reel.columns]


def synthetique_naif(reel, produits, n_commandes=6000, seed=7):
    """IMITATION PROGRAMMÉE des défauts typiques d'un jeu « écrit à la main » ou produit sans mesure : dates régulières, prix ronds, quantités uniformes,
    clients répartis également, montants tirés sur quelques valeurs. Ce n'est pas la sortie d'un modèle : c'est une caricature pour tester les tests."""
    rng = np.random.default_rng(seed)
    n = n_commandes * 2
    ids = np.repeat(np.arange(1, n_commandes + 1), 2)
    jours = pd.date_range("2024-01-01", "2024-12-31")
    dates = jours[np.repeat(np.arange(n_commandes), 2) % len(jours)]
    q = rng.integers(1, 6, n)
    prix = rng.choice([9.99, 14.99, 19.99, 24.99, 29.99, 49.99, 99.99], n)
    return pd.DataFrame({"id_commande": ids, "id_client": (np.repeat(np.arange(n_commandes), 2) % 1500) + 1, "date_commande": dates,
                         "canal": rng.choice(["Boutique", "Site", "Réseaux"], n), "id_produit": rng.integers(1, 121, n), "quantite": q,
                         "prix_unitaire": prix, "montant": (q * prix).round(2)})


def synthetique_copie_bruitee(reel, seed=11, part=0.3):
    """Un « jeu synthétique » obtenu en recopiant des lignes réelles avec un petit bruit (dates ±2 jours, montants ±1 %) : fuite de vie privée."""
    rng = np.random.default_rng(seed)
    s = reel.sample(frac=part, random_state=seed).copy().reset_index(drop=True)
    s["date_commande"] = s["date_commande"] + pd.to_timedelta(rng.integers(-2, 3, len(s)), unit="D")
    s["montant"] = (s["montant"] * (1 + rng.normal(0, 0.01, len(s)))).round(2)
    return s


def batterie(synth, reel, produits_ids):
    """Cinq contrôles de qualité d'un jeu synthétique ; retourne un DataFrame (contrôle, mesure, seuil, résultat)."""
    from scipy.stats import ks_2samp
    res = []
    # 1. intégrité référentielle
    manque = (~synth["id_produit"].isin(produits_ids)).mean()
    res.append(("intégrité référentielle", f"{100 * manque:.1f} %".replace(".", ","), "0 %", manque == 0))
    # 2. distribution des montants (Kolmogorov-Smirnov)
    ks = ks_2samp(synth["montant"], reel["montant"]).statistic
    res.append(("montants (écart KS)", f"{ks:.3f}".replace(".", ","), "< 0,05", ks < 0.05))
    # 3. saisonnalité mensuelle
    a = synth.drop_duplicates("id_commande")["date_commande"].dt.month.value_counts(normalize=True).sort_index()
    b = reel.drop_duplicates("id_commande")["date_commande"].dt.month.value_counts(normalize=True).sort_index()
    corr = float(np.corrcoef(a.reindex(range(1, 13), fill_value=0), b.reindex(range(1, 13), fill_value=0))[0, 1])
    res.append(("saisonnalité (corrélation)", f"{corr:.2f}".replace(".", ","), "> 0,80", corr > 0.8))
    # 4. diversité des prix
    d_s, d_r = synth["prix_unitaire"].nunique(), reel["prix_unitaire"].nunique()
    res.append(("prix distincts (réel : %d)" % d_r, f"{d_s}", f"≥ {int(0.5 * d_r)}", d_s >= 0.5 * d_r))
    # 5. fuite : part de lignes quasi identiques à une ligne réelle (même client, produit, canal, montant à 2 % près, date à 3 jours près)
    cle = ["id_client", "id_produit", "canal"]
    m = synth.merge(reel[cle + ["montant", "date_commande"]], on=cle, suffixes=("", "_r"))
    proche = m[(abs(m["montant"] / m["montant_r"] - 1) < 0.02) & ((m["date_commande"] - m["date_commande_r"]).abs() <= pd.Timedelta(days=3))]
    part = proche.drop_duplicates(["id_commande", "id_produit"]).shape[0] / len(synth)
    res.append(("fuite vers le réel", f"{100 * part:.1f} %".replace(".", ","), "< 1 %", part < 0.01))
    return pd.DataFrame(res, columns=["contrôle", "mesure", "seuil", "réussi"])


# ------------------------------------------------------------------------------------------------ enregistrement des sorties du petit modèle local (facultatif)
def regenerer_sorties():
    """Régénère `donnees/ch05-sorties-modele.json` avec SmolLM2-135M-Instruct (hors ligne, glouton, déterministe). Demande `HF_HOME` vers le cache local des modèles."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    nom = "HuggingFaceTB/SmolLM2-135M-Instruct"
    tok, mod = AutoTokenizer.from_pretrained(nom), AutoModelForCausalLM.from_pretrained(nom)
    mod.eval()

    def completer(prompt, n=100):
        ids = tok(prompt, return_tensors="pt").input_ids
        with torch.no_grad():
            out = mod.generate(ids, max_new_tokens=n, do_sample=False, pad_token_id=tok.eos_token_id)
        return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)

    def coupe_sql(brut):
        s = "SELECT" + brut
        s = re.split(r"\n--|;\s*\n", s)[0].strip()
        return s if s.endswith(";") else s.rstrip(";") + ";"

    qs = questions_or()
    sortie = {"modele": nom, "parametres": "135 millions", "decodage": "glouton (déterministe)", "sql": {}, "tokens": [], "logits": {}}
    for v in ("v1", "v2", "v3"):
        sortie["sql"][v] = {r.id: coupe_sql(completer(prompt_texte(r.question, v))) for r in qs.itertuples()}
    # comptages de jetons
    textes = {"schema_ddl": ddl(), "schema_descriptions": ddl(True), "ligne_csv": "1,1,24,1,33.9,0,33.9\n2,1,10,1,49.9,0,49.9\n3,2,87,2,12.5,10,22.5\n",
              "phrase": "Le chiffre d'affaires de décembre progresse de 12,4 % par rapport à décembre 2024.", "requete": "SELECT canal, SUM(montant) FROM lignes_commande GROUP BY canal;"}
    for k, t in textes.items():
        sortie["tokens"].append({"nom": k, "texte": t, "caracteres": len(t), "jetons": len(tok(t).input_ids)})
    # probabilités du jeton suivant à plusieurs températures
    amorce = "Le chiffre d'affaires de décembre a"
    ids = tok(amorce, return_tensors="pt").input_ids
    with torch.no_grad():
        lg = mod(ids).logits[0, -1].float()
    top = torch.topk(lg, 12)
    sortie["logits"] = {"amorce": amorce, "jetons": [tok.decode([int(i)]) for i in top.indices], "scores": [round(float(x), 3) for x in top.values]}
    # un commentaire et des lignes
    f = faits_mensuels(ouvrir_lecture(construire_entrepot(os.path.join(TMP, "ch05_regen.duckdb"))))
    p = ("Faits (JSON) : " + json.dumps(f, ensure_ascii=False) + "\nRédigez en trois phrases un commentaire du mois pour la gérante, sans inventer de chiffre.\nCommentaire :")
    sortie["commentaire"] = {"faits": f, "texte": completer(p, 90).strip()}
    p = "client,date_commande,canal,montant\n12,2024-03-02,Site,38.50\n"
    sortie["lignes_csv"] = {"prompt": p, "texte": completer(p, 80)}
    with open(os.path.join(DONNEES, "ch05-sorties-modele.json"), "w", encoding="utf-8") as fh:
        json.dump(sortie, fh, ensure_ascii=False, indent=1)
    print("sorties enregistrées")


if __name__ == "__main__":
    if os.environ.get("REGENERER_SORTIES") == "1":
        regenerer_sorties()
    else:
        print(__doc__)
