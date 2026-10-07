"""Outils du chapitre 5 (types de données, collecte, enquêtes) : chargement typé, population invitée à l'enquête, vérité programmée de la satisfaction,
mini-serveur HTTP local (API, pages HTML, données ouvertes) pour les sections 5.5, et fonctions de figures.

Tout est local et reproductible : le serveur écoute sur 127.0.0.1 (port libre choisi par le système), aucun accès réseau externe."""
import json
import os
import threading
import time
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
FIN_ENQUETE = pd.Timestamp("2025-12-31")
CLE_API = "cle-demo-123"


# ------------------------------------------------------------------------------------------------ données
def charger():
    """Les tables de la boutique avec leurs types (dates en datetime, identifiants en entiers). Retourne un dictionnaire de DataFrames."""
    d = DONNEES
    t = {"clients": pd.read_csv(os.path.join(d, "clients.csv"), parse_dates=["date_inscription"]),
         "commandes": pd.read_csv(os.path.join(d, "commandes.csv"), parse_dates=["date_commande"]),
         "lignes": pd.read_csv(os.path.join(d, "lignes_commande.csv")),
         "produits": pd.read_csv(os.path.join(d, "produits.csv"), parse_dates=["date_lancement"]),
         "retours": pd.read_csv(os.path.join(d, "retours.csv"), parse_dates=["date_retour"]),
         "jours": pd.read_csv(os.path.join(d, "jours_exploitation.csv"), parse_dates=["date"]),
         "enquete": pd.read_csv(os.path.join(d, "enquete_satisfaction.csv"), parse_dates=["date_reponse"])}
    return t


def invites(commandes, clients):
    """La population invitée à l'enquête : un client par ligne (tous ceux qui ont commandé en 2025), avec sa dernière commande de 2025, son ancienneté
    de dernière commande (`jours`), sa carte de fidélité et sa tranche d'âge. C'est ce que l'on SAIT des invités, répondants ou non."""
    c25 = commandes[commandes["date_commande"] >= "2025-01-01"].sort_values(["date_commande", "id_commande"])
    inv = c25.drop_duplicates("id_client", keep="last").merge(clients[["id_client", "fidelite", "annee_naissance", "email_valide", "ville"]], on="id_client")
    inv["jours"] = (FIN_ENQUETE - inv["date_commande"]).dt.days
    inv["tranche_age"] = tranche_age(2025 - inv["annee_naissance"])
    return inv.reset_index(drop=True)


def tranche_age(age):
    return pd.cut(age, [0, 24, 34, 44, 54, 64, 120], labels=["moins de 25 ans", "25-34 ans", "35-44 ans", "45-54 ans", "55-64 ans", "65 ans et plus"]).astype(str)


def nettoyer_enquete(e, seuil_rapide=25):
    """Retire les doublons exacts (hors `id_reponse`), marque la « ligne droite rapide » (5-5-5 en moins de `seuil_rapide` secondes).
    Retourne (enquête sans doublons, masque de la ligne droite rapide sur cette enquête)."""
    cols = [c for c in e.columns if c != "id_reponse"]
    u = e.drop_duplicates(subset=cols).reset_index(drop=True)
    sl = (u["satisfaction_globale"] == 5) & (u["satisfaction_livraison"] == 5) & (u["satisfaction_prix"] == 5) & (u["duree_reponse_s"] < seuil_rapide)
    return u, sl


def nps(x, z=1.96):
    """Net Promoter Score (en points) et demi-largeur de l'intervalle de confiance à 95 % (formule de la variance d'une différence de proportions)."""
    x = np.asarray(x)
    n = len(x)
    p, d = (x >= 9).mean(), (x <= 6).mean()
    var = (p + d - (p - d) ** 2) / n
    return 100 * (p - d), 100 * z * np.sqrt(var)


def verite_satisfaction(inv, repetitions=400, seed=0):
    """VÉRITÉ PROGRAMMÉE. Rejoue le modèle de satisfaction de `build/donnees_a1.py` sur TOUS les invités (répondants ou non) et retourne les
    moyennes attendues si tout le monde avait répondu, ainsi que celles que l'on observerait chez les seuls répondants. Les graines diffèrent de celles du
    fichier : on compare des moyennes sur `repetitions` tirages, pas des tirages."""
    rng = np.random.default_rng(seed)
    n = len(inv)
    boutique = (inv["canal"] == "Boutique").values
    relais = (inv["mode_livraison"] == "Point relais").values
    fid = inv["fidelite"].values
    jours = inv["jours"].values
    sat_pop, sat_rep, nps_pop, nps_rep, taux = [], [], [], [], []
    for _ in range(repetitions):
        lat = rng.normal(3.6, 0.9, n) + 0.3 * boutique - 0.25 * relais
        sat = np.clip(np.round(lat + rng.normal(0, 0.7, n)), 1, 5)
        rec = np.clip(np.round(2 * lat + rng.normal(0, 1.6, n) - 0.5), 0, 10)
        p_rep = np.clip(0.17 + 0.10 * np.exp(-jours / 60) + 0.05 * fid + 0.06 * (np.abs(lat - 3.5) > 1.2), 0, 0.8)
        rp = rng.random(n) < p_rep
        sat_pop.append(sat.mean()); sat_rep.append(sat[rp].mean())
        nps_pop.append(nps(rec)[0]); nps_rep.append(nps(rec[rp])[0]); taux.append(rp.mean())
    return {"sat_population": float(np.mean(sat_pop)), "sat_repondants": float(np.mean(sat_rep)), "nps_population": float(np.mean(nps_pop)),
            "nps_repondants": float(np.mean(nps_rep)), "taux_reponse": float(np.mean(taux))}


def villes_ouvertes(seed=5):
    """Une table de « données ouvertes » fictive sur les 20 villes (population, revenu médian) : servie par le mini-serveur, jointe aux clients."""
    rng = np.random.default_rng(seed)
    noms = [f"Ville {chr(65 + i)}" for i in range(20)]
    pop = (np.round(rng.lognormal(10.2, 0.7, 20), -2)).astype(int)
    pop = np.sort(pop)[::-1]
    rev = np.round(rng.normal(21500, 2800, 20), -2).astype(int)
    return pd.DataFrame({"ville": noms, "population": pop, "revenu_median": rev})


# ------------------------------------------------------------------------------------------------ mini-serveur local
CATALOGUE_V1 = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Catalogue de la boutique (démonstration)</title></head><body>
<h1>Catalogue</h1>
{cartes}
<p class="pagination"><a rel="next" href="{suivant}">Page suivante</a></p></body></html>"""
CARTE_V1 = ('<div class="produit" data-id="{id}"><h2 class="nom">{nom}</h2><span class="categorie">{cat}</span>'
            '<span class="prix">{prix} €</span></div>')
CARTE_V2 = ('<article class="item" id="p{id}"><header><h3>{nom}</h3></header><p class="meta">{cat}</p>'
            '<p class="tarif"><strong>{prix}</strong> EUR</p></article>')


class MiniServeur:
    """Serveur HTTP de démonstration, local (127.0.0.1), lancé dans un fil d'exécution.

    Routes : `/api/v1/produits` (JSON paginé ; clé d'API `X-API-Key` ; limite de débit : 3 requêtes par fenêtre de `fenetre` secondes, sinon 429 avec
    `Retry-After`), `/catalogue?page=n` et `/catalogue-v2?page=n` (pages HTML), `/robots.txt`, `/prive/stock` (interdit par robots.txt),
    `/ouvert/villes.csv|json|xml` et `/ouvert/villes.meta.json` (données ouvertes fictives). Compteurs : `serveur.journal` (liste de (chemin, statut))."""

    def __init__(self, produits, villes, fenetre=1.0, limite=3, par_page_defaut=25):
        self.produits, self.villes = produits.reset_index(drop=True), villes
        self.fenetre, self.limite, self.par_page_defaut = fenetre, limite, par_page_defaut
        self.journal = []
        self._appels = []
        self._verrou = threading.Lock()
        outer = self

        class Gestionnaire(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _envoyer(self, statut, corps, type_="application/json; charset=utf-8", entetes=None):
                b = corps.encode("utf-8") if isinstance(corps, str) else corps
                with outer._verrou:                       # journal écrit AVANT la réponse : le client ne peut pas dépasser le serveur
                    outer.journal.append((self.path.split("?")[0], statut))
                self.send_response(statut)
                self.send_header("Content-Type", type_)
                self.send_header("Content-Length", str(len(b)))
                for k, v in (entetes or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(b)

            def do_GET(self):
                u = urlparse(self.path)
                q = {k: v[0] for k, v in parse_qs(u.query).items()}
                if u.path == "/api/v1/produits":
                    return self._api(q)
                if u.path in ("/catalogue", "/catalogue-v2"):
                    return self._catalogue(u.path, q)
                if u.path == "/robots.txt":
                    return self._envoyer(200, "User-agent: *\nDisallow: /prive/\nCrawl-delay: 1\n", "text/plain; charset=utf-8")
                if u.path == "/prive/stock":
                    return self._envoyer(200, "<html><body>Stock interne : ne pas collecter.</body></html>", "text/html; charset=utf-8")
                if u.path.startswith("/ouvert/"):
                    return self._ouvert(u.path)
                return self._envoyer(404, json.dumps({"erreur": "introuvable", "chemin": u.path}))

            def _api(self, q):
                if self.headers.get("X-API-Key") != CLE_API:
                    return self._envoyer(401, json.dumps({"erreur": "clé d'API absente ou invalide"}))
                with outer._verrou:
                    t = time.monotonic()
                    outer._appels = [a for a in outer._appels if t - a < outer.fenetre]
                    depasse = len(outer._appels) >= outer.limite
                    if not depasse:
                        outer._appels.append(t)
                if depasse:
                    return self._envoyer(429, json.dumps({"erreur": "trop de requêtes"}), entetes={"Retry-After": str(int(np.ceil(outer.fenetre)))})
                try:
                    page = int(q.get("page", 1)); par_page = min(int(q.get("per_page", outer.par_page_defaut)), 50)
                    assert page >= 1 and par_page >= 1
                except (ValueError, AssertionError):
                    return self._envoyer(400, json.dumps({"erreur": "paramètres invalides"}))
                n = len(outer.produits)
                pages = -(-n // par_page)
                bloc = outer.produits.iloc[(page - 1) * par_page: page * par_page]
                data = [{"id_produit": int(r.id_produit), "nom": r.nom_produit, "categorie": r.categorie, "prix_vente": float(r.prix_vente)} for r in bloc.itertuples()]
                suivant = f"/api/v1/produits?page={page + 1}&per_page={par_page}" if page < pages else None
                return self._envoyer(200, json.dumps({"page": page, "par_page": par_page, "total": n, "pages": pages, "data": data, "suivant": suivant}, ensure_ascii=False))

            def _catalogue(self, chemin, q):
                page = int(q.get("page", 1))
                bloc = outer.produits.iloc[(page - 1) * 10: page * 10]
                modele = CARTE_V1 if chemin == "/catalogue" else CARTE_V2
                cartes = "\n".join(modele.format(id=int(r.id_produit), nom=r.nom_produit, cat=r.categorie, prix=f"{r.prix_vente:.2f}".replace(".", ",")) for r in bloc.itertuples())
                suivant = f"{chemin}?page={page + 1}" if page * 10 < len(outer.produits) else ""
                return self._envoyer(200, CATALOGUE_V1.format(cartes=cartes, suivant=suivant), "text/html; charset=utf-8")

            def _ouvert(self, chemin):
                v = outer.villes
                if chemin.endswith("villes.csv"):
                    return self._envoyer(200, v.to_csv(index=False), "text/csv; charset=utf-8")
                if chemin.endswith("villes.json"):
                    return self._envoyer(200, v.to_json(orient="records", force_ascii=False))
                if chemin.endswith("villes.xml"):
                    racine = ET.Element("villes")
                    for r in v.itertuples():
                        e = ET.SubElement(racine, "ville", nom=r.ville)
                        ET.SubElement(e, "population").text = str(r.population)
                        ET.SubElement(e, "revenu_median").text = str(r.revenu_median)
                    return self._envoyer(200, ET.tostring(racine, encoding="unicode"), "application/xml; charset=utf-8")
                if chemin.endswith("villes.meta.json"):
                    return self._envoyer(200, json.dumps({"titre": "Villes de la région (démonstration)", "licence": "Licence ouverte fictive v1",
                                                          "source": "Service statistique fictif", "mise_a_jour": "2025-06-30"}, ensure_ascii=False))
                return self._envoyer(404, json.dumps({"erreur": "introuvable"}))

        self._srv = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
        self.url = f"http://127.0.0.1:{self._srv.server_address[1]}"
        self._fil = None

    def demarrer(self):
        self._fil = threading.Thread(target=self._srv.serve_forever, daemon=True)
        self._fil.start()
        return self

    def arreter(self):
        self._srv.shutdown()
        self._srv.server_close()


# ------------------------------------------------------------------------------------------------ plans de sondage (simulation)
def depense_2025(commandes, lignes, clients, produits=None):
    """Dépense 2025 et 2024 de chaque client ayant commandé en 2025 (la « population » des simulations de sondage)."""
    m = lignes.merge(commandes[["id_commande", "id_client", "date_commande"]], on="id_commande")
    m["an"] = m["date_commande"].dt.year
    pv = m.pivot_table(index="id_client", columns="an", values="montant", aggfunc="sum", fill_value=0.0)
    pv.columns = [f"depense_{a}" for a in pv.columns]
    pop = pv[pv["depense_2025"] > 0].reset_index().merge(clients[["id_client", "canal_acquisition", "ville", "fidelite", "email_valide", "consentement_marketing"]], on="id_client")
    return pop


def simuler_plans(pop, n=300, repetitions=500, seed=1):
    """Compare quatre plans de sondage pour estimer la dépense moyenne 2025 par client. Retourne un DataFrame (une ligne par répétition)."""
    rng = np.random.default_rng(seed)
    y = pop["depense_2025"].values
    N = len(pop)
    strates = pd.qcut(pop["depense_2024"].rank(method="first"), 3, labels=False).values       # strates connues AVANT l'enquête : dépense 2024
    villes = pop["ville"].values
    liste_villes = np.unique(villes)
    contact = ((pop["email_valide"] == 1) & (pop["consentement_marketing"] == 1)).values
    sorties = []
    for _ in range(repetitions):
        i = rng.choice(N, n, replace=False)
        srs = y[i].mean()
        # stratifié proportionnel
        est = 0.0
        for s in range(3):
            idx = np.where(strates == s)[0]
            k = int(round(n * len(idx) / N))
            est += len(idx) / N * y[rng.choice(idx, k, replace=False)].mean()
        # grappes : 4 villes tirées au hasard, tous leurs clients (puis sous-échantillon de n)
        v = rng.choice(liste_villes, 4, replace=False)
        idx = np.where(np.isin(villes, v))[0]
        cl = y[rng.choice(idx, min(n, len(idx)), replace=False)].mean()
        # commodité : clients joignables par courriel (consentement) ET ayant acheté le plus récemment (ici : plus forte dépense 2024, proxy d'activité)
        cand = np.where(contact)[0]
        cand = cand[np.argsort(-pop["depense_2024"].values[cand], kind="stable")][: 3 * n]
        com = y[rng.choice(cand, n, replace=False)].mean()
        sorties.append((srs, est, cl, com))
    return pd.DataFrame(sorties, columns=["aleatoire_simple", "stratifie", "grappes", "commodite"])


def n_corr(e, N=None, p=0.5, z=1.96):
    """Effectif nécessaire pour estimer une proportion avec une marge d'erreur `e` (demi-largeur de l'IC à 95 %) ; correction de population finie si N est donné."""
    n0 = z * z * p * (1 - p) / e ** 2
    return n0 if N is None else n0 / (1 + (n0 - 1) / N)
