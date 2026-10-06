"""Outils du chapitre 5 (ingénierie des données), partagés par les blocs cachés du livre et par le cahier.

Contenu : lecture des sources sales, nettoyage des commandes (pandas), règles de qualité, normalisation et rapprochement,
serveur HTTP LOCAL (page HTML + API JSON paginée avec limitation de débit) pour la collecte, journal de lignage.
Aucune connexion extérieure : tout tourne en local, avec des graines et des compteurs (pas d'horloge) pour rester déterministe.
"""
import io
import json
import os
import re
import threading
import unicodedata
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(RACINE, "donnees", "sources")


def lire(nom, **kw):
    """Lit un export brut TEL QUEL : tout en texte (dtype=str), pour ne rien perdre ni deviner."""
    return pd.read_csv(os.path.join(SOURCES, nom + ".csv"), dtype=str, keep_default_na=False, na_values=[""], **kw)


# ----------------------------------------------------------------------------- transformations des commandes
def parser_date(s):
    """Trois formats rencontrés : AAAA-MM-JJ, JJ/MM/AAAA (avec des /) et MM-JJ-AAAA (tiret, année à la fin)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return pd.NaT
    s = str(s).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
        return pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")
    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", s):
        return pd.to_datetime(s, format="%m-%d-%Y", errors="coerce")
    return pd.NaT


def typer_commandes(brut):
    """Typage : dates, prix à virgule décimale, quantités. Ne supprime AUCUNE ligne (c'est le rôle de l'étape suivante)."""
    d = brut.copy()
    d["date"] = d["date"].map(parser_date)
    d["prix_unitaire"] = pd.to_numeric(d["prix_unitaire"].str.replace(",", ".", regex=False), errors="coerce")
    d["quantite"] = pd.to_numeric(d["quantite"], errors="coerce")
    d["id_commande"] = d["id_commande"].astype(int)
    d["id_client"] = d["id_client"].astype(int)
    return d


def motif_rejet(d, clients_connus, produits_connus):
    """Motif de rejet d'une ligne typée (None si la ligne est acceptée). Règles de gestion, par ordre de gravité."""
    m = pd.Series([None] * len(d), index=d.index, dtype=object)
    m[d["quantite"].isna()] = "quantité manquante"
    m[d["quantite"] < 1] = "quantité négative ou nulle"
    m[d["prix_unitaire"].isna() | (d["prix_unitaire"] <= 0)] = "prix invalide"
    m[~d["id_produit"].isin(produits_connus)] = "produit inconnu"
    m[~d["id_client"].isin(clients_connus)] = "client inconnu"
    m[d["date"].isna()] = "date illisible"
    return m


def etl_commandes(brut, clients_connus, produits_connus):
    """Pipeline complet en mémoire : typage -> déduplication -> rejets. Retourne (propres, rejets, statistiques)."""
    typ = typer_commandes(brut)
    avant = len(typ)
    dedup = typ.drop_duplicates()
    cle_unique = dedup.drop_duplicates("id_commande")
    motif = motif_rejet(cle_unique, clients_connus, produits_connus)
    propres = cle_unique[motif.isna()].copy()
    propres["montant"] = (propres["quantite"] * propres["prix_unitaire"]).round(2)
    rejets = cle_unique[motif.notna()].assign(motif=motif[motif.notna()])
    stats = {"lignes_brutes": avant, "apres_doublons_exacts": len(dedup), "apres_cle_unique": len(cle_unique),
             "rejets": len(rejets), "propres": len(propres)}
    return propres, rejets, stats


# ----------------------------------------------------------------------------- normalisation de libellés
ABREVIATIONS = {"cér.": "céramique", "cot.": "coton", "arg.": "argent"}
MOTS_VIDES = {"en", "de", "du", "la", "le", "les", "lot", "(lot)"}


def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def normaliser(s, expand=True, trier=True):
    """Minuscules, sans accents, abréviations développées, mots vides retirés, jetons triés."""
    t = str(s).lower().strip()
    t = re.sub(r"\s+", " ", t)
    if expand:
        for a, b in ABREVIATIONS.items():
            t = t.replace(a, b)
    t = sans_accents(t)
    jetons = [w for w in re.findall(r"[a-z0-9]+", t) if w not in {sans_accents(x).strip("()") for x in MOTS_VIDES}]
    return " ".join(sorted(jetons) if trier else jetons)


# ----------------------------------------------------------------------------- serveur HTTP local (chapitre 5.5)
class _Gestionnaire(BaseHTTPRequestHandler):
    """Petit site fictif : /robots.txt, /catalogue (HTML), /api/avis?page=&taille= (JSON paginé, limité en débit)."""

    compteur = 0                       # nombre de requêtes reçues sur /api (limitation DÉTERMINISTE : 1 requête sur 7 est refusée)

    def log_message(self, *a, **k):    # silence
        pass

    def _envoyer(self, code, corps, type_="application/json", entetes=None):
        octets = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_ + "; charset=utf-8")
        self.send_header("Content-Length", str(len(octets)))
        for k, v in (entetes or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(octets)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        srv = self.server
        if u.path == "/robots.txt":
            return self._envoyer(200, "User-agent: *\nDisallow: /prive/\nCrawl-delay: 1\n", "text/plain")
        if u.path == "/prive/clients":
            return self._envoyer(403, json.dumps({"erreur": "interdit"}))
        if u.path in ("/catalogue", "/catalogue-v2"):
            lignes = []
            for _, r in srv.catalogue.iterrows():
                if u.path == "/catalogue":
                    lignes.append(f'<div class="produit" data-id="{r.id_produit}"><h3 class="nom">{r.libelle}</h3>'
                                  f'<span class="prix">{r.prix_catalogue:.2f} €</span><span class="cat">Catégorie {r.categorie}</span></div>')
                else:                      # nouvelle mise en page : les classes changent, la structure aussi
                    lignes.append(f'<article id="{r.id_produit}"><a>{r.libelle}</a><p><b>{r.prix_catalogue:.2f}</b> EUR</p></article>')
            return self._envoyer(200, "<html><body>" + "".join(lignes) + "</body></html>", "text/html")
        if u.path == "/api/avis":
            type(self).compteur += 1
            if type(self).compteur % 7 == 0:
                return self._envoyer(429, json.dumps({"erreur": "trop de requêtes"}), entetes={"Retry-After": "0"})
            page, taille = int(q.get("page", ["1"])[0]), int(q.get("taille", ["50"])[0])
            av = srv.avis
            morceau = av.iloc[(page - 1) * taille: page * taille]
            corps = {"page": page, "total": len(av), "suivante": page + 1 if page * taille < len(av) else None,
                     "resultats": morceau.to_dict(orient="records")}
            return self._envoyer(200, json.dumps(corps, ensure_ascii=False))
        return self._envoyer(404, json.dumps({"erreur": "introuvable"}))


@contextmanager
def serveur_local(catalogue, avis):
    """Démarre le faux site dans un fil d'exécution (port libre choisi par le système) et rend son URL de base."""
    _Gestionnaire.compteur = 0
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Gestionnaire)
    srv.catalogue, srv.avis = catalogue, avis
    fil = threading.Thread(target=srv.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}"
    finally:
        srv.shutdown()
        srv.server_close()


# ----------------------------------------------------------------------------- journal de lignage
class Journal:
    """Enregistre chaque étape d'un pipeline : entrées, sorties, lignes avant/après (métadonnées de lignage)."""

    def __init__(self):
        self.etapes = []

    def enregistrer(self, nom, entrees, sorties, lignes_in, lignes_out):
        self.etapes.append({"etape": nom, "entrees": list(entrees), "sorties": list(sorties), "lignes_in": int(lignes_in), "lignes_out": int(lignes_out)})
        return sorties

    def table(self):
        return pd.DataFrame(self.etapes)


# ----------------------------------------------------------------------------- réconciliation des clients (chapitre 5.3)
def crm_avec_fautes(crm, verite, graine=5, part=0.35):
    """CRM + vérité terrain (id_vrai) ; on ajoute des fautes de frappe (inversion de deux lettres) dans le nom
    de `part` des doublons récents (id_crm > 4200), pour rendre le problème réaliste. Retourne (table, nombre de fautes)."""
    d = crm.merge(verite.astype(int), on="id_crm")
    rng = np.random.default_rng(graine)
    idx = d.index[d["id_crm"] > 4200]
    touche = rng.random(len(idx)) < part

    def faute(s):
        j = int(rng.integers(0, len(s) - 1))
        return s[:j] + s[j + 1] + s[j] + s[j + 2:]
    d.loc[idx[touche], "nom"] = [faute(n) for n in d.loc[idx[touche], "nom"]]
    return d, int(touche.sum())


def paires_candidates(d, cles):
    """Paires (i, j) d'index qui partagent les mêmes valeurs sur les colonnes `cles` : le BLOCAGE."""
    from itertools import combinations
    sortie = []
    for _, g in d.groupby(cles):
        if len(g) > 1:
            sortie += list(combinations(g.index.tolist(), 2))
    return sortie
