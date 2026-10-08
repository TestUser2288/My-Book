#!/usr/bin/env python3
"""Outils du chapitre 2 (volume V) « ETL et automatisation des flux de travail » — tout est SIMULÉ, graines fixes.

Ce module contient :
  1. le générateur du DÉPÔT de fichiers livrés chaque mois par le système de commandes de la boutique (12 fichiers 2025 + renvois), avec des défauts réalistes
     (vérité programmée ci-dessous) ;
  2. les briques du pipeline (extraire, transformer, charger, contrôler, exécuter) dans leur version FINALE — le livre les construit pas à pas dans le texte ;
     le cahier, qui doit être autonome, les importe d'ici ;
  3. de petits outils : horloge déterministe, journalisation, alertes, planification (cron), jouets (exécuteur de graphe, modèles SQL à la dbt) ;
  4. les serveurs locaux de démonstration (API, SMTP de test) et les figures.

Usage : python build/outils_ch02.py generer   -> réécrit donnees/ch02-depot/ (déterministe) ; python build/outils_ch02.py pipeline --help

VÉRITÉ PROGRAMMÉE DU DÉPÔT (donnees/ch02-depot/, graine 20250)
===============================================================
Source : les lignes de commande 2025 de la boutique (29 827 lignes, 12 946 commandes, 1 324 763,72 € TTC, ce sont exactement les chiffres du volume III).
Un fichier par mois, `commandes_2025-MM.csv` (colonnes id_ligne, id_commande, date_commande, id_client, canal, id_produit, quantite, montant ; séparateur « , », UTF-8) et un
manifeste `manifeste.csv` (fichier, date de livraison, nombre de lignes ANNONCÉ par l'exportateur). Défauts injectés :
  - mars    : première livraison avec 12 montants multipliés par 10 (erreur de saisie) ; `commandes_2025-03_v2.csv` renvoyé le 14 avril avec les bons montants ;
  - mai     : la colonne `montant` s'appelle `total_ligne` (dérive de schéma) ;
  - juillet : dates au format jj/mm/aaaa ;
  - août    : fichier encodé en cp1252 (latin-1) et non en UTF-8 ;
  - septembre : fichier VIDE (0 octet) ; `_v2` complet livré le 9 octobre ;
  - octobre : fichier TRONQUÉ (85 % des lignes, dernière ligne coupée) ; `_v2` complet livré le 6 novembre ;
  - novembre : 25 lignes en double exact ;
  - 18 lignes « orphelines » (client 90001-90018 absent du référentiel) et 9 montants négatifs (avoirs), répartis sur l'année, ajoutés AUX lignes d'origine.
  Les lignes injectées portent des id_ligne ≥ 900001 : le total des lignes valides est exactement 1 324 763,72 €.
"""
import atexit
import contextlib
import io
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from graphlib import TopologicalSorter

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
DEPOT = os.path.join(DONNEES, "ch02-depot")
COLS = ["id_ligne", "id_commande", "date_commande", "id_client", "canal", "id_produit", "quantite", "montant"]
ALIAS = {"total_ligne": "montant"}
CANAUX = {"Boutique", "Site", "Réseaux"}
TVA = 0.20      # TVA fictive de la boutique (volume III)


def fr(x, nd=1, signe=False):
    """Nombre à la française : espace fine insécable pour les milliers, virgule décimale, vrai signe moins."""
    s = f"{x:+,.{nd}f}" if signe else f"{x:,.{nd}f}"
    return s.replace(",", "\u202f").replace(".", ",").replace("-", "\u2212")


# =========================================================================================== 1. le dépôt
def generer_depot(donnees=DONNEES, seed=20250):
    rng = np.random.default_rng(seed)
    depot = os.path.join(donnees, "ch02-depot")
    os.makedirs(depot, exist_ok=True)
    c = pd.read_csv(os.path.join(donnees, "commandes.csv"))
    c = c[c["date_commande"].str[:4] == "2025"]
    li = pd.read_csv(os.path.join(donnees, "lignes_commande.csv"))
    x = li.merge(c[["id_commande", "date_commande", "id_client", "canal"]], on="id_commande").sort_values("id_ligne")
    x = x[COLS].reset_index(drop=True)
    x["mois"] = x["date_commande"].str[:7]
    x["montant"] = x["montant"].round(2)
    clients = pd.read_csv(os.path.join(donnees, "clients.csv"))["id_client"]
    # lignes injectées
    mois_liste = sorted(x["mois"].unique())
    extras = {m: [] for m in mois_liste}
    nid = 900001
    for k in range(18):
        m = mois_liste[int(rng.integers(0, 12))]
        base = x[x["mois"] == m].iloc[int(rng.integers(0, 200))]
        extras[m].append({**base[COLS].to_dict(), "id_ligne": nid, "id_client": 90001 + k})
        nid += 1
    for k in range(9):
        m = mois_liste[int(rng.integers(0, 12))]
        base = x[x["mois"] == m].iloc[int(rng.integers(0, 200))]
        extras[m].append({**base[COLS].to_dict(), "id_ligne": nid, "id_client": int(rng.choice(clients)), "montant": -round(float(rng.uniform(20, 120)), 2)})
        nid += 1
    manifeste, verite = [], {"total_original": round(float(x["montant"].sum()), 2), "lignes_originales": int(len(x)), "commandes": int(x["id_commande"].nunique()),
                             "par_mois": {}, "orphelins": 18, "negatifs": 9, "doublons_novembre": 25, "mars_lignes_erronees": 12}
    for i, m in enumerate(mois_liste):
        d = x[x["mois"] == m][COLS].copy()
        ex = pd.DataFrame(extras[m], columns=COLS) if extras[m] else pd.DataFrame(columns=COLS)
        d = pd.concat([d, ex], ignore_index=True)
        if len(ex):
            # on glisse les lignes injectées à des positions aléatoires sans toucher à l'ordre relatif des autres
            base_idx = list(range(len(d) - len(ex)))
            for j in range(len(ex)):
                base_idx.insert(int(rng.integers(0, len(base_idx) + 1)), len(d) - len(ex) + j)
            d = d.iloc[base_idx].reset_index(drop=True)
        if m == "2025-11":
            dup = d.sample(25, random_state=7)
            d = pd.concat([d, dup], ignore_index=True)
        verite["par_mois"][m] = {"lignes_originales": int((x["mois"] == m).sum()), "lignes_fichier": int(len(d)), "total_original": round(float(x[x["mois"] == m]["montant"].sum()), 2)}
        livraison = (datetime(2025, i + 2, 3) if i < 11 else datetime(2026, 1, 3)).strftime("%Y-%m-%d")
        nom = f"commandes_{m}.csv"
        annonce = len(d)
        entete = ",".join(COLS)
        if m == "2025-05":
            entete = entete.replace("montant", "total_ligne")
        sortie = d.copy()
        if m == "2025-07":
            sortie["date_commande"] = pd.to_datetime(sortie["date_commande"]).dt.strftime("%d/%m/%Y")
        corps = sortie.to_csv(index=False, header=False, lineterminator="\n")
        texte = entete + "\n" + corps
        if m == "2025-03":                                      # v1 : montants erronés ; v2 : corrects
            fautes = d[d["id_ligne"] < 900000].sample(12, random_state=3).index
            v1 = sortie.copy()
            v1.loc[fautes, "montant"] = (v1.loc[fautes, "montant"] * 10).round(2)
            texte_v1 = entete + "\n" + v1.to_csv(index=False, header=False, lineterminator="\n")
            ecrire(depot, nom, texte_v1)
            ecrire(depot, "commandes_2025-03_v2.csv", texte)
            manifeste += [(nom, livraison, annonce), ("commandes_2025-03_v2.csv", "2025-04-14", annonce)]
            continue
        if m == "2025-09":
            ecrire(depot, nom, "")
            ecrire(depot, "commandes_2025-09_v2.csv", texte)
            manifeste += [(nom, livraison, annonce), ("commandes_2025-09_v2.csv", "2025-10-09", annonce)]
            continue
        if m == "2025-10":
            coupe = int(len(texte) * 0.85)
            ecrire(depot, nom, texte[:coupe])
            ecrire(depot, "commandes_2025-10_v2.csv", texte)
            manifeste += [(nom, livraison, annonce), ("commandes_2025-10_v2.csv", "2025-11-06", annonce)]
            continue
        ecrire(depot, nom, texte, encodage="cp1252" if m == "2025-08" else "utf-8")
        manifeste.append((nom, livraison, annonce))
    pd.DataFrame(manifeste, columns=["fichier", "date_livraison", "lignes_annoncees"]).sort_values(["date_livraison", "fichier"]).to_csv(os.path.join(depot, "manifeste.csv"), index=False)
    json.dump(verite, open(os.path.join(depot, "verite.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return verite


def ecrire(dossier, nom, texte, encodage="utf-8"):
    with open(os.path.join(dossier, nom), "wb") as f:
        f.write(texte.encode(encodage))


def manifeste(depot=DEPOT):
    m = pd.read_csv(os.path.join(depot, "manifeste.csv"))
    m["mois"] = m["fichier"].str.extract(r"(\d{4}-\d{2})")[0]
    return m


def verite(depot=DEPOT):
    return json.load(open(os.path.join(depot, "verite.json"), encoding="utf-8"))


# =========================================================================================== 2. les briques du pipeline
class ContratViole(Exception):
    """Le fichier ne respecte pas le contrat de données (colonnes absentes, par exemple)."""


class SourceVide(Exception):
    """Le fichier livré est vide."""


class ControleEchoue(Exception):
    """Un contrôle de qualité a échoué : on n'écrit rien."""


def lire_texte(chemin):
    brut = open(chemin, "rb").read()
    try:
        return brut.decode("utf-8")
    except UnicodeDecodeError:
        return brut.decode("cp1252")


def extraire(chemin):
    texte = lire_texte(chemin)
    if not texte.strip():
        raise SourceVide(os.path.basename(chemin) + " est vide")
    df = pd.read_csv(io.StringIO(texte), dtype=str, keep_default_na=False).rename(columns=ALIAS)
    manque = [c for c in COLS if c not in df.columns]
    if manque:
        raise ContratViole("colonnes absentes : " + ", ".join(manque))
    return df[COLS]


def transformer(df, clients):
    d = pd.to_datetime(df["date_commande"], format="%Y-%m-%d", errors="coerce")
    d = d.fillna(pd.to_datetime(df["date_commande"], format="%d/%m/%Y", errors="coerce"))
    nombres = ["id_ligne", "id_commande", "id_client", "id_produit", "quantite", "montant"]
    t = df.assign(date_commande=d, **{c: pd.to_numeric(df[c], errors="coerce") for c in nombres})
    motif = np.select([df.duplicated(), t.isna().any(axis=1), ~df["canal"].isin(CANAUX), t["montant"] < 0, ~t["id_client"].isin(clients)],
                      ["doublon exact", "valeur illisible ou manquante", "canal inconnu", "montant négatif", "client inconnu"], default="")
    ok = motif == ""
    v = t[ok].astype({c: "int64" for c in nombres[:5]}).reset_index(drop=True)
    return v, df[~ok].assign(motif=motif[~ok], ligne=np.flatnonzero(~ok) + 2).reset_index(drop=True)


DDL = """
CREATE TABLE dim_client(id_client INTEGER PRIMARY KEY, ville VARCHAR, canal_acquisition VARCHAR);
CREATE TABLE dim_produit(id_produit INTEGER PRIMARY KEY, nom_produit VARCHAR, categorie VARCHAR, prix_vente DOUBLE, cout_achat DOUBLE);
CREATE TABLE fait_ligne(id_ligne INTEGER PRIMARY KEY, id_commande INTEGER, date_commande DATE, id_client INTEGER, canal VARCHAR,
                        id_produit INTEGER, quantite INTEGER, montant DOUBLE, fichier VARCHAR);
CREATE TABLE rejets(fichier VARCHAR, ligne INTEGER, motif VARCHAR, contenu VARCHAR);
CREATE TABLE executions(id_execution INTEGER, mois VARCHAR, fichier VARCHAR, debut TIMESTAMP, fin TIMESTAMP, statut VARCHAR,
                        lignes_lues INTEGER, lignes_chargees INTEGER, lignes_rejetees INTEGER, message VARCHAR);
"""


def dossier_de(con):
    """Dossier temporaire qui contient la base DuckDB de la connexion (pour y poser un verrou, un journal…)."""
    return os.path.dirname(con.execute("PRAGMA database_list").fetchone()[2])


def nouvel_entrepot(nom="entrepot"):
    """Un entrepôt DuckDB neuf dans un dossier temporaire (supprimé à la sortie) : renvoie la connexion."""
    import duckdb
    dossier = tempfile.mkdtemp(prefix="ch02_", dir=os.environ.get("TMPDIR"))
    atexit.register(shutil.rmtree, dossier, ignore_errors=True)
    con = duckdb.connect(os.path.join(dossier, nom + ".duckdb"))
    con.execute(DDL)
    return con


def charger_dimensions(con, donnees=DONNEES):
    cl = pd.read_csv(os.path.join(donnees, "clients.csv"))[["id_client", "ville", "canal_acquisition"]]
    pr = pd.read_csv(os.path.join(donnees, "produits.csv"))[["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat"]]
    for nom, df in (("dim_client", cl), ("dim_produit", pr)):
        con.execute(f"DELETE FROM {nom}")
        con.register("tmp_dim", df)
        con.execute(f"INSERT INTO {nom} SELECT * FROM tmp_dim")
        con.unregister("tmp_dim")
    return set(cl["id_client"])


def charger(con, v, fichier):
    """Fusion (upsert) sur la clé naturelle id_ligne : relancer donne le même état. Renvoie (insérées, mises à jour)."""
    con.register("lot", v.assign(fichier=fichier)[COLS + ["fichier"]])
    deja = con.execute("SELECT count(*) FROM lot WHERE id_ligne IN (SELECT id_ligne FROM fait_ligne)").fetchone()[0]
    con.execute("INSERT OR REPLACE INTO fait_ligne SELECT * FROM lot")
    con.unregister("lot")
    return len(v) - deja, deja


# ----- horloge et journal déterministes (pour que le livre donne toujours les mêmes sorties)
class Horloge:
    """Horloge factice : chaque appel avance de `pas` secondes. `aller_a` saute à une date (la livraison d'un fichier)."""

    def __init__(self, debut="2025-02-03 06:00:00", pas=3):
        self.t = datetime.fromisoformat(debut).replace(tzinfo=timezone.utc)
        self.pas = pas

    def __call__(self):
        self.t += timedelta(seconds=self.pas)
        return self.t

    def aller_a(self, jour, heure="06:00:00"):
        self.t = datetime.fromisoformat(f"{jour} {heure}").replace(tzinfo=timezone.utc)


class FormatteurHorloge(logging.Formatter):
    def __init__(self, horloge, fmt, json_=False):
        super().__init__(fmt)
        self.horloge, self.json_ = horloge, json_

    def format(self, record):
        record.horodatage = self.horloge().strftime("%Y-%m-%d %H:%M:%S")
        if self.json_:
            return json.dumps({"t": record.horodatage, "niveau": record.levelname, "etape": getattr(record, "etape", ""), "mois": getattr(record, "mois", ""),
                               "message": record.getMessage()}, ensure_ascii=False)
        return super().format(record)


def journal(horloge, nom="pipeline", json_=False, niveau=logging.INFO, fichier=None):
    """Renvoie (logger, tampon) : le journal écrit dans un tampon mémoire (et dans `fichier` si demandé)."""
    log = logging.getLogger(f"{nom}.{id(horloge)}")
    log.handlers.clear()
    log.propagate = False
    log.setLevel(niveau)
    tampon = io.StringIO()
    fmt = "%(horodatage)s %(levelname)-7s %(message)s"
    for h in [logging.StreamHandler(tampon)] + ([logging.FileHandler(fichier, encoding="utf-8")] if fichier else []):
        h.setFormatter(FormatteurHorloge(horloge, fmt, json_))
        log.addHandler(h)
    return log, tampon


_MUET = logging.getLogger("pipeline.muet")
_MUET.addHandler(logging.NullHandler())
_MUET.propagate = False


def executer(con, chemin, annonce, clients, horloge, log=None, seuil_rejets=0.02, mois=None):
    """Une exécution complète pour un fichier : tout ou rien, trace dans `executions`, rejets en quarantaine."""
    nom = os.path.basename(chemin)
    mois = mois or re.search(r"(\d{4}-\d{2})", nom).group(1)
    debut, lues, chargees, rejetees, message, statut = horloge(), 0, 0, 0, "", "SUCCES"
    log = log or _MUET
    log.info("début %s", nom, extra={"etape": "début", "mois": mois})
    try:
        df = extraire(chemin)
        lues = len(df)
        if lues != annonce:
            raise ControleEchoue(f"{lues} lignes lues pour {annonce} annoncées")
        v, r = transformer(df, clients)
        rejetees = len(r)
        if rejetees / max(lues, 1) > seuil_rejets:
            raise ControleEchoue(f"{rejetees} lignes rejetées sur {lues} (seuil {fr(seuil_rejets * 100, 2)} %)")
        con.execute("BEGIN")
        try:
            ins, maj = charger(con, v, nom)
            hors = con.execute("SELECT count(*) FROM fait_ligne WHERE fichier = ? AND strftime(date_commande, '%Y-%m') <> ?", [nom, mois]).fetchone()[0]
            if hors:
                raise ControleEchoue(f"{hors} lignes hors du mois {mois}")
            ecart = con.execute("SELECT sum(montant) FROM fait_ligne WHERE fichier = ?", [nom]).fetchone()[0] - float(v["montant"].sum())
            if abs(ecart) > 0.005:
                raise ControleEchoue(f"écart de {ecart:.2f} € entre la source et l'entrepôt")
            con.execute("DELETE FROM rejets WHERE fichier = ?", [nom])          # relancer le même fichier ne double pas la quarantaine
            if len(r):
                rr = r.assign(fichier=nom)[["fichier", "ligne", "motif"]].assign(contenu=r[COLS].astype(str).agg(",".join, axis=1))
                con.register("rr", rr)
                con.execute("INSERT INTO rejets SELECT * FROM rr")
                con.unregister("rr")
            con.execute("COMMIT")
        except BaseException:
            con.execute("ROLLBACK")
            raise
        chargees = len(v)
        message = f"{ins} insérées, {maj} mises à jour"
        log.info("fin %s : %s, %d rejetées", nom, message, rejetees, extra={"etape": "fin", "mois": mois})
    except Exception as e:
        statut, message = "ECHEC", f"{type(e).__name__} : {e}"
        log.error("%s : %s", nom, message, extra={"etape": "erreur", "mois": mois})
    fin = horloge()
    nid = con.execute("SELECT coalesce(max(id_execution), 0) + 1 FROM executions").fetchone()[0]
    con.execute("INSERT INTO executions VALUES (?,?,?,?,?,?,?,?,?,?)", [nid, mois, nom, debut.replace(tzinfo=None), fin.replace(tzinfo=None), statut, lues, chargees, rejetees, message])
    return statut


def rejouer(con, depot, clients, horloge, log=None, a_partir_de=None, seuil_rejets=0.02):
    """Rejoue les livraisons dans l'ordre où elles sont arrivées (le manifeste donne l'ordre et les nombres de lignes annoncés)."""
    m = manifeste(depot)
    for _, ligne in m.iterrows():
        horloge.aller_a(ligne["date_livraison"])
        executer(con, os.path.join(depot, ligne["fichier"]), int(ligne["lignes_annoncees"]), clients, horloge, log, seuil_rejets)


def empreinte(con):
    """Compte, total et signature des lignes de l'entrepôt : deux états identiques ont la même empreinte."""
    return con.execute("""SELECT count(*), round(sum(montant), 2),
           md5(string_agg(id_ligne || ':' || montant, ',' ORDER BY id_ligne)) FROM fait_ligne""").fetchone()


def a_rattraper(con, depot):
    """Mois dont la dernière livraison n'a pas été chargée avec succès."""
    m = manifeste(depot).sort_values("date_livraison").groupby("mois").tail(1)
    ok = con.execute("SELECT DISTINCT fichier FROM executions WHERE statut = 'SUCCES'").df()["fichier"].tolist()
    return m[~m["fichier"].isin(ok)]


# ----- reprises, alertes
def avec_reprises(fonction, essais=4, base=1.0, dormir=time.sleep, graine=0, transitoires=(ConnectionError, TimeoutError)):
    """Réessaie `fonction` en cas d'erreur transitoire, avec attente exponentielle (1, 2, 4 s…) et un peu d'aléa (jitter)."""
    rng = np.random.default_rng(graine)
    for k in range(essais):
        try:
            return fonction()
        except transitoires:
            if k == essais - 1:
                raise
            dormir(base * 2 ** k * (1 + 0.25 * rng.random()))


def evaluer_alertes(con, aujourdhui, depot=DEPOT, jours_sans_succes=35, seuil_rejets=0.005):
    """Règles d'alerte : seulement ce qui appelle une action. Renvoie une liste de (gravité, message)."""
    ex = con.execute("SELECT * FROM executions ORDER BY id_execution").df()
    ex = ex[ex["debut"] < pd.Timestamp(aujourdhui) + pd.Timedelta(days=1)]          # on ne voit que ce qui s'est déjà passé
    al = []
    for _, e in ex[ex["statut"] == "ECHEC"].iterrows():
        suite = ex[(ex["mois"] == e["mois"]) & (ex["id_execution"] > e["id_execution"]) & (ex["statut"] == "SUCCES")]
        if suite.empty:
            al.append(("CRITIQUE", f"{e['mois']} : échec non résolu ({e['message']})"))
    for _, e in ex[ex["statut"] == "SUCCES"].iterrows():
        if e["lignes_lues"] and e["lignes_rejetees"] / e["lignes_lues"] > seuil_rejets:
            al.append(("ATTENTION", f"{e['mois']} : {e['lignes_rejetees']} lignes en quarantaine sur {e['lignes_lues']}"))
    dernier = ex[ex["statut"] == "SUCCES"]["fin"].max()
    if pd.isna(dernier) or (pd.Timestamp(aujourdhui) - dernier).days > jours_sans_succes:
        al.append(("CRITIQUE", f"aucun chargement réussi depuis plus de {jours_sans_succes} jours"))
    return al


# =========================================================================================== 3. cron
def champ_cron(txt, bas, haut):
    """Valeurs permises d'un champ de cron : *, listes, plages a-b, pas */n ou a-b/n."""
    valeurs = set()
    for part in txt.split(","):
        plage, _, pas = part.partition("/")
        if plage == "*":
            a, b = bas, haut
        elif "-" in plage:
            a, b = map(int, plage.split("-"))
        else:
            a = b = int(plage)
        valeurs |= set(range(a, b + 1, int(pas or 1)))
    return valeurs


def prochaine_echeance(expr, depuis):
    """Première date strictement après `depuis` qui satisfait l'expression cron à cinq champs (heure locale, sans fuseau)."""
    m, h, jm, mo, js = expr.split()
    minutes, heures = champ_cron(m, 0, 59), champ_cron(h, 0, 23)
    jours_mois, mois, jours_sem = champ_cron(jm, 1, 31), champ_cron(mo, 1, 12), champ_cron(js, 0, 7)
    jours_sem = {d % 7 for d in jours_sem}                                    # 0 et 7 = dimanche
    jour = depuis.replace(hour=0, minute=0, second=0, microsecond=0)
    for _ in range(3660):
        dow = (jour.weekday() + 1) % 7                                         # lundi=1 … dimanche=0
        ok_jour = (jour.day in jours_mois and dow in jours_sem) if (jm.startswith("*") or js.startswith("*")) else (jour.day in jours_mois or dow in jours_sem)
        if jour.month in mois and ok_jour:
            for hh in sorted(heures):
                for mm in sorted(minutes):
                    t = jour.replace(hour=hh, minute=mm)
                    if t > depuis:
                        return t
        jour += timedelta(days=1)
    return None


# =========================================================================================== 4. jouets
def lancer_graphe(graphe, actions, etat=None):
    """Exécuteur de graphe minimal : ordre topologique, tâches suivantes ignorées si une précédente échoue, reprise possible via `etat`."""
    etat = dict(etat or {})
    for tache in TopologicalSorter(graphe).static_order():
        if etat.get(tache) == "ok":
            continue
        if any(etat.get(p) != "ok" for p in graphe.get(tache, ())):
            etat[tache] = "ignorée"
            continue
        try:
            actions[tache]()
            etat[tache] = "ok"
        except Exception as e:
            etat[tache] = "échec"
    return etat


def construire_modeles(con, modeles):
    """Mini-dbt : lit les `{{ ref('x') }}`, ordonne les modèles et les crée en vues. Renvoie l'ordre de construction et le SQL compilé."""
    refs = {n: set(re.findall(r"ref\('(\w+)'\)", s)) for n, s in modeles.items()}
    ordre, compile_ = [], {}
    for n in TopologicalSorter(refs).static_order():
        compile_[n] = re.sub(r"\{\{\s*ref\('(\w+)'\)\s*\}\}", r"\1", modeles[n])
        con.execute(f"CREATE OR REPLACE VIEW {n} AS {compile_[n]}")
        ordre.append(n)
    return ordre, compile_


def tester_modele(con, modele, test):
    """Tests à la dbt : 'unique:col1,col2' (aucune clé en double), 'non_nul:col' (aucune valeur manquante). Renvoie le nombre de lignes en défaut."""
    genre, _, cols = test.partition(":")
    cols = cols.split(",")
    if genre == "unique":
        return con.execute(f"SELECT count(*) FROM (SELECT {', '.join(cols)} FROM {modele} GROUP BY ALL HAVING count(*) > 1)").fetchone()[0]
    return con.execute(f"SELECT count(*) FROM {modele} WHERE {cols[0]} IS NULL").fetchone()[0]


def lire_api(url, cle, taille=500, dormir=time.sleep, trace=None):
    """Lit toutes les pages de /colis (curseurs), réessaie 429 et 500, s'arrête sur les autres erreurs. Renvoie (DataFrame, total annoncé)."""
    import requests
    trace = [] if trace is None else trace
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + cle
    lignes, curseur = [], "c0"
    while curseur:
        for essai in range(5):
            r = session.get(url + "/colis", params={"curseur": curseur, "taille": taille}, timeout=10)
            trace.append((curseur, r.status_code))
            if r.status_code not in (429, 500, 502, 503):
                r.raise_for_status()
                break
            dormir(float(r.headers.get("Retry-After", 2 ** essai)))
        else:
            raise RuntimeError("trop d'échecs sur la page " + curseur)
        page = r.json()
        lignes += page["donnees"]
        curseur = page["suivant"]
    return pd.DataFrame(lignes), page["total"]


# =========================================================================================== 5. e-mail et API de démonstration
@contextlib.contextmanager
def serveur_smtp(port=20130):
    """Serveur SMTP LOCAL de test (aiosmtpd) : garde les messages reçus dans une liste. Rien ne sort de la machine."""
    from aiosmtpd.controller import Controller
    recus = []

    class Capture:
        async def handle_DATA(self, server, session, envelope):
            recus.append({"de": envelope.mail_from, "a": list(envelope.rcpt_tos), "octets": envelope.content})
            return "250 Message accepté"

    ctl = Controller(Capture(), hostname="127.0.0.1", port=port)
    ctl.start()
    try:
        yield recus
    finally:
        ctl.stop()


@contextlib.contextmanager
def serveur_api(port=20120, cle="cle-de-demonstration-0000"):
    """Lance l'API locale `ch02_api` (uvicorn) en sous-processus, attend qu'elle réponde, et l'arrête proprement."""
    import subprocess
    import requests
    env = dict(os.environ, API_COLIS_CLE=cle, DONNEES=DONNEES)
    p = subprocess.Popen([sys.executable, "-m", "uvicorn", "ch02_api:app", "--app-dir", os.path.dirname(os.path.abspath(__file__)), "--host", "127.0.0.1",
                          "--port", str(port), "--log-level", "error"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                if requests.get(f"http://127.0.0.1:{port}/sante", timeout=1).status_code == 200:
                    break
            except requests.exceptions.RequestException:
                time.sleep(0.2)
        yield f"http://127.0.0.1:{port}"
    finally:
        p.terminate()
        try:
            p.wait(timeout=10)
        except Exception:
            p.kill()


# =========================================================================================== 6. figures (appelées par des blocs cachés)
def _style():
    from style import setup
    setup()
    import matplotlib.pyplot as plt
    return plt


def boite(ax, x, y, w, h, texte, couleur="#cde2fb", bord="#2a78d6", fs=9, gras=False):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=couleur, ec=bord, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=fs, color="#0b0b0b", fontweight="bold" if gras else "normal", linespacing=1.25)


def fleche(ax, x1, y1, x2, y2, style="-|>", couleur="#52514e", lw=1.4, ls="-", rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle=style, color=couleur, lw=lw, ls=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def fig_chaine(png="ch02-chaine-etl.png"):
    from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, save
    plt = _style()
    fig, ax = plt.subplots(figsize=(10.4, 3.9))
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.grid(False)
    boite(ax, 0.1, 3.0, 2.0, 1.2, "Sources\nfichiers livrés,\nAPI, base", "#f0efec", "#898781")
    boite(ax, 2.9, 3.0, 2.0, 1.2, "Dépôt (staging)\ncopie brute,\njamais modifiée", "#cde2fb", BLEU)
    boite(ax, 5.7, 3.0, 2.2, 1.2, "Transformer\ncontrat, types,\nrègles, contrôles", "#fde2d6", ORANGE)
    boite(ax, 8.7, 3.0, 2.0, 1.2, "Entrepôt\nfaits et\ndimensions", "#d3f1e5", AQUA)
    boite(ax, 11.4, 3.0, 1.9, 1.2, "Marts, rapports,\ntableau de bord,\ne-mail", "#e4e0f5", VIOLET)
    for a, b in ((2.1, 2.9), (4.9, 5.7), (7.9, 8.7), (10.7, 11.4)):
        fleche(ax, a, 3.6, b, 3.6)
    boite(ax, 5.7, 0.55, 2.2, 1.2, "Quarantaine\nlignes rejetées\n+ motif", "#fbdcdb", ROUGE)
    fleche(ax, 6.8, 3.0, 6.8, 1.75, couleur=ROUGE)
    boite(ax, 8.7, 0.55, 4.6, 1.2, "Journal et table des exécutions\nqui, quand, combien de lignes, quel statut", "#f0efec", "#898781")
    fleche(ax, 9.7, 3.0, 9.7, 1.75, style="-|>", ls="--")
    fleche(ax, 7.9, 3.2, 8.7, 1.5, ls="--", rad=-0.1)
    ax.text(3.9, 4.6, "E : extraire", ha="center", fontsize=10, color=BLEU, fontweight="bold")
    ax.text(6.8, 4.6, "T : transformer", ha="center", fontsize=10, color=ORANGE, fontweight="bold")
    ax.text(9.7, 4.6, "L : charger", ha="center", fontsize=10, color="#117a54", fontweight="bold")
    boite(ax, 0.1, 0.55, 2.4, 1.2, "Planificateur\nlance la chaîne\nà heure fixe", "#f0efec", "#898781")
    fleche(ax, 1.3, 1.75, 3.2, 3.0, ls="--")
    save(fig, png)


def fig_cron(png="ch02-cron.png"):
    from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, save
    plt = _style()
    fig, ax = plt.subplots(figsize=(9.4, 3.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.grid(False)
    champs = [("minute", "0-59", "0", BLEU, "#cde2fb"), ("heure", "0-23", "6", ORANGE, "#fde2d6"), ("jour du mois", "1-31", "3", AQUA, "#d3f1e5"),
              ("mois", "1-12", "*", VIOLET, "#e4e0f5"), ("jour de la semaine", "0-6 ou 0-7\n(dimanche = 0)", "*", ROUGE, "#fbdcdb")]
    for i, (nom, plage, val, c, f) in enumerate(champs):
        x = 0.2 + i * 1.95
        boite(ax, x, 1.55, 1.7, 1.0, val, f, c, fs=20, gras=True)
        ax.text(x + 0.85, 3.05, nom, ha="center", fontsize=9.5, color=c, fontweight="bold")
        ax.text(x + 0.85, 1.0, plage, ha="center", va="center", fontsize=8.5, color="#52514e")
    ax.text(5, 3.7, "0 6 3 * *", ha="center", fontsize=13, color="#0b0b0b", family="monospace")
    ax.text(5, 0.25, "= le 3 de chaque mois, à 6 h 00 (le jour de livraison des fichiers de la boutique)", ha="center", fontsize=9.5, color="#0b0b0b")
    save(fig, png)


def fig_cout_automatisation(heures, png="ch02-cout-automatisation.png"):
    """`heures` : {nom: (construction, entretien par an, couleur)} ; courbes du temps cumulé sur quatre ans."""
    from style import save
    plt = _style()
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    t = np.linspace(0, 4, 81)
    for nom, (cons, ent, c) in heures.items():
        y = cons + ent * t
        ax.plot(t, y, color=c, lw=2.2)
        ax.text(4.04, y[-1], nom, va="center", fontsize=9, color=c)
    ax.set_xlim(0, 4)
    ax.set_xticks(range(5))
    ax.set_xlabel("années après le début du projet")
    ax.set_ylabel("heures cumulées (construction + entretien)")
    ax.set_title("Le robot d'interface ne rembourse jamais ici ; le chargement par fichier rembourse en un peu plus d'un an", loc="left", fontsize=10)
    fig.subplots_adjust(right=0.74)
    save(fig, png)


def fig_idempotence(etapes, naif, idem, vrai, png="ch02-idempotence.png"):
    from style import BLEU, ORANGE, MUET, save
    plt = _style()
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    x = np.arange(len(etapes))
    ax.bar(x - 0.2, naif, 0.38, color=ORANGE, label="chargement par ajout simple")
    ax.bar(x + 0.2, idem, 0.38, color=BLEU, label="chargement par fusion sur la clé")
    for i, (a, b) in enumerate(zip(naif, idem)):
        ax.text(i - 0.2, a + 12000, f"{a / 1000:,.0f}".replace(",", " ").replace(".", ","), ha="center", fontsize=8.5, color="#0b0b0b")
        ax.text(i + 0.2, b + 12000, f"{b / 1000:,.0f}".replace(",", " ").replace(".", ","), ha="center", fontsize=8.5, color="#0b0b0b")
    ax.axhline(vrai, color="#0b0b0b", lw=1.1, ls="--")
    ax.text(-0.45, vrai + 10000, "vrai total du trimestre", ha="left", fontsize=8.5, color="#0b0b0b")
    ax.set_xticks(x)
    ax.set_xticklabels(etapes, fontsize=9)
    ax.set_ylabel("chiffre d'affaires TTC chargé (k€)")
    ax.set_yticks([0, 200000, 400000])
    ax.set_yticklabels(["0", "200", "400"])
    ax.set_ylim(0, 520000)
    ax.legend(loc="upper left", fontsize=9)
    ax.set_title("Charger deux fois : le total double, ou il reste juste", loc="left", fontsize=10.5)
    save(fig, png)


def fig_graphe(graphe, etat, png, positions, titre=None, largeur=9.6, hauteur=3.2):
    """Dessine un graphe de tâches (colonnes = niveaux) ; l'état est montré par la couleur ET par un symbole."""
    from style import BLEU, ORANGE, AQUA, ROUGE, MUET, save
    plt = _style()
    fig, ax = plt.subplots(figsize=(largeur, hauteur))
    ax.axis("off")
    ax.grid(False)
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    ax.set_xlim(min(xs) - 1.1, max(xs) + 1.3)
    ax.set_ylim(min(ys) - 0.8, max(ys) + 0.8)
    coul = {"ok": ("#d3f1e5", AQUA, "✓"), "échec": ("#fbdcdb", ROUGE, "✗"), "ignorée": ("#f0efec", MUET, "–"), None: ("#cde2fb", BLEU, "")}
    for t, preds in graphe.items():
        for p in preds:
            (x1, y1), (x2, y2) = positions[p], positions[t]
            fleche(ax, x1 + 0.78, y1, x2 - 0.78, y2)
    for t, (x, y) in positions.items():
        fc, ec, sym = coul.get(etat.get(t) if etat else None, coul[None])
        boite(ax, x - 0.78, y - 0.28, 1.56, 0.56, f"{t} {sym}".strip(), fc, ec, fs=8.5)
    if titre:
        ax.set_title(titre, loc="left", fontsize=10.5)
    save(fig, png)


def fig_calendrier(ex, png="ch02-calendrier-executions.png"):
    """Chaque exécution = un marqueur à sa date, sur la ligne du mois traité ; la forme dit le statut (pas seulement la couleur)."""
    from style import BLEU, ROUGE, AQUA, ORANGE, save
    plt = _style()
    mois = sorted(ex["mois"].unique())
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    for _, e in ex.iterrows():
        y = mois.index(e["mois"])
        ok = e["statut"] == "SUCCES"
        ax.scatter(pd.Timestamp(e["debut"]).normalize(), y, s=50, marker="o" if ok else "X", color=AQUA if ok else ROUGE, zorder=3 if ok else 4, edgecolor="#0b0b0b", linewidth=0.5)
    ax.set_yticks(range(len(mois)))
    ax.set_yticklabels(mois, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("date de l'exécution")
    ax.grid(axis="x", alpha=0.5)
    ax.scatter([], [], s=50, marker="o", color=AQUA, edgecolor="#0b0b0b", linewidth=0.5, label="succès")
    ax.scatter([], [], s=50, marker="X", color=ROUGE, edgecolor="#0b0b0b", linewidth=0.5, label="échec")
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("Une ligne par mois traité : trois mois ont demandé une seconde livraison", loc="left", fontsize=10.5)
    import matplotlib.dates as md
    ax.xaxis.set_major_formatter(md.DateFormatter("%d/%m"))
    save(fig, png)


def fig_rejets(rej, png="ch02-rejets.png"):
    from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, save
    plt = _style()
    t = rej.pivot_table(index="mois", columns="motif", values="n", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    bas = np.zeros(len(t))
    for col, c in zip(t.columns, (ORANGE, BLEU, VIOLET, ROUGE, AQUA)):
        ax.bar(t.index.str[5:], t[col], bottom=bas, color=c, label=col, width=0.7)
        bas += t[col].to_numpy()
    for i, v in enumerate(bas):
        ax.text(i, v + 0.5, str(int(v)), ha="center", fontsize=8.5, color="#0b0b0b")
    ax.set_xlabel("mois 2025")
    ax.set_ylabel("lignes en quarantaine")
    ax.set_ylim(0, 29)
    ax.legend(fontsize=8.5, loc="upper left")
    ax.set_title("Ce que retient la quarantaine : surtout novembre (doublons)", loc="left", fontsize=10.5)
    save(fig, png)


def fig_api_trace(trace, png="ch02-api-trace.png"):
    """Les requêtes dans l'ordre : page demandée (ordonnée), forme et couleur = résultat (200 réussi, 429 trop de demandes, 500 erreur serveur)."""
    from style import BLEU, ORANGE, ROUGE, save
    plt = _style()
    fig, ax = plt.subplots(figsize=(8.8, 3.9))
    pages = sorted({c for c, _ in trace}, key=lambda c: int(c[1:]))
    style = {200: ("o", BLEU, "200 : page reçue"), 429: ("^", ORANGE, "429 : trop de demandes"), 500: ("X", ROUGE, "500 : erreur du serveur")}
    vus = set()
    for i, (c, code) in enumerate(trace, start=1):
        m, col, lab = style.get(code, ("s", "#898781", str(code)))
        ax.scatter(i, pages.index(c), marker=m, color=col, s=60, edgecolor="#0b0b0b", linewidth=0.5, label=None if code in vus else lab, zorder=3)
        vus.add(code)
    ax.set_yticks(range(len(pages)))
    ax.set_yticklabels([f"page {k + 1}" for k in range(len(pages))], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel("numéro de la requête")
    ax.set_xticks(range(1, len(trace) + 1))
    ax.tick_params(axis="x", labelsize=8)
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("Seize pages, dix-huit requêtes : deux pannes passagères, deux reprises", loc="left", fontsize=10.5)
    save(fig, png)


def rapport_html(df, titre, note):
    """Petit rapport HTML pour le corps d'un e-mail (styles en ligne : les messageries ignorent les feuilles de style)."""
    th = "".join(f"<th style='text-align:{'left' if i == 0 else 'right'};padding:4px 10px;border-bottom:2px solid #c3c2b7'>{c}</th>" for i, c in enumerate(df.columns))
    lignes = "".join("<tr>" + "".join(f"<td style='text-align:{'left' if i == 0 else 'right'};padding:4px 10px;border-bottom:1px solid #e1e0d9'>{v}</td>" for i, v in enumerate(r)) + "</tr>" for r in df.itertuples(index=False))
    return (f"<div style='font:14px DejaVu Sans,sans-serif;color:#0b0b0b'><h3 style='margin:0 0 8px'>{titre}</h3>"
            f"<table style='border-collapse:collapse'><tr>{th}</tr>{lignes}</table><p style='color:#52514e;font-size:12px'>{note}</p></div>")


def page_journal(lignes, titre="journal du pipeline"):
    """HTML d'un journal (niveau en couleur ET en toutes lettres) : sert à une vraie capture avec Chromium."""
    coul = {"INFO": "#256abf", "WARNING": "#9a5b00", "ERROR": "#b3261e"}
    corps = []
    for l in lignes:
        m = re.match(r"(\S+ \S+) (\w+)\s+(.*)", l)
        if m:
            corps.append(f"<div><span class='t'>{m.group(1)}</span> <b style='color:{coul.get(m.group(2), '#222')}'>{m.group(2):<7}</b> {m.group(3)}</div>")
        else:
            corps.append(f"<div>{l}</div>")
    return ("<html><body style='margin:0;background:#fcfcfb'><div style='font:13px DejaVu Sans Mono,monospace;padding:14px 18px;color:#0b0b0b;line-height:1.55'>"
            f"<div style='font:600 13px DejaVu Sans,sans-serif;color:#52514e;margin-bottom:8px'>{titre}</div>" + "".join(corps) +
            "</div><style>.t{color:#6b6a65}</style></body></html>")


def page_courriel(de, a, objet, pieces, corps_html):
    """Rendu générique d'un message reçu (pas un client de messagerie réel) : sert à une capture avec Chromium."""
    pj = "".join(f"<span style='border:1px solid #c3c2b7;border-radius:4px;padding:2px 8px;margin-right:6px;font-size:12px'>📎 {p}</span>" for p in pieces)
    return ("<html><body style='margin:0;background:#fcfcfb;font:14px DejaVu Sans,sans-serif;color:#0b0b0b'>"
            "<div style='border-bottom:1px solid #e1e0d9;padding:12px 18px;background:#f4f3ef'>"
            f"<div style='font-weight:600;font-size:15px;margin-bottom:6px'>{objet}</div>"
            f"<div style='font-size:12px;color:#52514e'>De : {de}<br>À : {a}</div><div style='margin-top:8px'>{pj}</div></div>"
            f"<div style='padding:14px 18px'>{corps_html}</div></body></html>")


# =========================================================================================== 7. ligne de commande
def construire_parser():
    import argparse
    p = argparse.ArgumentParser(prog="pipeline", description="Charge les commandes livrées par mois dans l'entrepôt.")
    p.add_argument("--depot", default=DEPOT, help="dossier des fichiers livrés")
    p.add_argument("--mois", help="un seul mois (AAAA-MM) ; sinon tous les mois à rattraper")
    p.add_argument("--simuler", action="store_true", help="n'écrit rien : liste ce qui serait fait")
    p.add_argument("--seuil-rejets", type=float, default=0.02, help="part maximale de lignes rejetées (0,02 = 2 %%)")
    return p


def main(argv=None):
    a = construire_parser().parse_args(argv)
    con = nouvel_entrepot()
    clients = charger_dimensions(con)
    m = manifeste(a.depot).sort_values("date_livraison").groupby("mois").tail(1)       # dernière version livrée de chaque mois
    if a.mois:
        m = m[m["mois"] == a.mois]
    if a.simuler:
        for _, ligne in m.iterrows():
            print(f"[simulation] chargerait {ligne['fichier']} ({ligne['lignes_annoncees']} lignes annoncées)")
        return 0
    h = Horloge()
    log, tampon = journal(h)
    statuts = []
    for _, ligne in m.iterrows():
        h.aller_a(ligne["date_livraison"])
        statuts.append(executer(con, os.path.join(a.depot, ligne["fichier"]), int(ligne["lignes_annoncees"]), clients, h, log, a.seuil_rejets))
    print(tampon.getvalue().rstrip())
    return 1 if "ECHEC" in statuts else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generer":
        v = generer_depot()
        print("dépôt écrit :", v["lignes_originales"], "lignes d'origine,", v["total_original"], "€")
    elif len(sys.argv) > 1 and sys.argv[1] == "pipeline":
        sys.exit(main(sys.argv[2:]))
    else:
        print(__doc__)
