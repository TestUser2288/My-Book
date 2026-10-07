"""Outils du chapitre 10 (analytique marketing et web) : chargement, intervalles de confiance, marge par commande, simulations FABRIQUÉES (parcours multi-contacts, groupe témoin, consentement)."""
import os
import numpy as np
import pandas as pd

D = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
TVA = 0.20
SOURCES = ["direct", "organique", "payant", "email", "reseaux", "referent"]


def charger():
    s = pd.read_csv(os.path.join(D, "sessions_web.csv"), parse_dates=["date"])
    c = pd.read_csv(os.path.join(D, "campagnes.csv"))
    cmd = pd.read_csv(os.path.join(D, "commandes.csv"), parse_dates=["date_commande"])
    lig = pd.read_csv(os.path.join(D, "lignes_commande.csv"))
    prod = pd.read_csv(os.path.join(D, "produits.csv"))
    return s, c, cmd, lig, prod


def wilson(k, n, z=1.96):
    """intervalle de Wilson d'une proportion (k succès sur n)"""
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - demi, centre + demi


def marge_commandes(cmd, lig, prod):
    """une ligne par commande : CA TTC, CA HT, marge brute HT, client, première commande du client ?"""
    x = lig.merge(prod[["id_produit", "cout_achat"]], on="id_produit")
    x["marge"] = x["montant"] / (1 + TVA) - x["quantite"] * x["cout_achat"]
    o = x.groupby("id_commande").agg(ca_ttc=("montant", "sum"), marge=("marge", "sum")).reset_index()
    o["ca_ht"] = o["ca_ttc"] / (1 + TVA)
    m = cmd[["id_commande", "id_client", "date_commande", "canal"]].merge(o, on="id_commande")
    m = m.sort_values(["date_commande", "id_commande"])
    m["premiere_commande"] = ~m.duplicated("id_client")
    return m


def parcours_fabriques(n=4000, seed=10):
    """parcours multi-contacts FABRIQUÉS (les vraies sessions n'ont qu'une source) : liste de sources par parcours, tous convertis"""
    rng = np.random.default_rng(seed)
    debut = {"reseaux": 0.30, "payant": 0.25, "organique": 0.30, "referent": 0.05, "direct": 0.05, "email": 0.05}
    milieu = {"organique": 0.30, "reseaux": 0.20, "payant": 0.15, "email": 0.20, "direct": 0.10, "referent": 0.05}
    fin = {"direct": 0.40, "email": 0.25, "organique": 0.18, "payant": 0.10, "reseaux": 0.04, "referent": 0.03}
    tirer = lambda d: str(rng.choice(list(d), p=list(d.values())))
    parcours = []
    for _ in range(n):
        k = int(rng.choice([1, 2, 3, 4, 5], p=[0.35, 0.25, 0.20, 0.12, 0.08]))
        if k == 1:
            parcours.append([tirer(fin)])
        else:
            parcours.append([tirer(debut)] + [tirer(milieu) for _ in range(k - 2)] + [tirer(fin)])
    return parcours


def attribution(parcours, modele):
    credit = dict.fromkeys(SOURCES, 0.0)
    for p in parcours:
        k = len(p)
        if modele == "dernier clic":
            w = [0] * (k - 1) + [1]
        elif modele == "premier clic":
            w = [1] + [0] * (k - 1)
        elif modele == "linéaire":
            w = [1 / k] * k
        elif modele == "en U":
            w = [1.0] if k == 1 else ([0.5, 0.5] if k == 2 else [0.4] + [0.2 / (k - 2)] * (k - 2) + [0.4])
        for s, x in zip(p, w):
            credit[s] += x
    tot = sum(credit.values())
    return {s: v / tot for s, v in credit.items()}


def test_temoin(n=60000, part_temoin=0.2, seed=11):
    """groupe témoin FABRIQUÉ : une audience voit la publicité (exposée) ou non (témoin, tirage aléatoire) ; 3 % d'achats de base, +0,3 point causé par la publicité ;
    le « dernier clic » attribue à la publicité tous les achats des exposés qui ont cliqué avant d'acheter, y compris ceux qui auraient acheté de toute façon"""
    rng = np.random.default_rng(seed)
    expose = rng.random(n) >= part_temoin
    base = rng.random(n) < 0.030
    extra = (rng.random(n) < 0.0031) & expose
    achat = base | extra
    clique = expose & (rng.random(n) < np.where(achat, 0.42, 0.04))
    return pd.DataFrame({"expose": expose.astype(int), "achat": achat.astype(int), "clique": clique.astype(int)})


CONSENTEMENT = {"direct": 0.85, "email": 0.95, "organique": 0.75, "payant": 0.65, "reseaux": 0.55, "referent": 0.70}


def vue_outil(s, seed=12):
    """VUE D'OUTIL FABRIQUÉE : seules les sessions dont le visiteur a accepté le suivi (ou n'a pas de bloqueur) sont mesurées ; le taux dépend de la source"""
    rng = np.random.default_rng(seed)
    garde = rng.random(len(s)) < s["source"].map(CONSENTEMENT).values
    return s[garde].copy()


def evenements_doublons(s, taux=0.03, seed=13):
    """ÉVÉNEMENTS FABRIQUÉS : sur 3 % des commandes, l'événement « achat » se déclenche deux fois (rechargement de la page de confirmation)"""
    rng = np.random.default_rng(seed)
    ev = s.loc[s["commande"] == 1, ["id_session", "id_commande"]].copy()
    dup = ev[rng.random(len(ev)) < taux]
    return pd.concat([ev, dup], ignore_index=True).sample(frac=1, random_state=3).reset_index(drop=True)
