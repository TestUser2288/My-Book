"""Outils du chapitre 5 (confidentialité et anonymisation), partagés par le livre (blocs cachés) et le cahier.

Contenu : chargement des fichiers, hachage et hachage à clé, attaque par dictionnaire, table « à partager » (clients + profil), généralisation
(ville → région, année → tranche de dix ans), tailles de groupes et statistiques de k-anonymat, suppression pour atteindre k, bruit de Laplace.
Tout est déterministe (graines fixes). Les données sont simulées ; les noms de personnes sont inventés.
"""
import hashlib
import hmac
import os
import unicodedata

import numpy as np
import pandas as pd

D = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
DOMAINES = ["exemple.org", "courrier.test", "mail.example"]
OUI = ["oui", "Oui", "OUI", "O", "1", "TRUE"]


def charger():
    """dictionnaire des tables utiles au chapitre"""
    t = {}
    t["clients"] = pd.read_csv(os.path.join(D, "clients.csv"))
    t["profil"] = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))
    t["crm"] = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype={"telephone": str, "code_postal": str, "date_naissance": str})
    t["vcrm"] = pd.read_csv(os.path.join(D, "verite_crm.csv"))
    t["ident"] = pd.read_csv(os.path.join(D, "verite_identites.csv"))
    t["cmd"] = pd.read_csv(os.path.join(D, "commandes.csv"))
    t["lig"] = pd.read_csv(os.path.join(D, "lignes_commande.csv"))
    return t


def sha256(texte):
    return hashlib.sha256(str(texte).encode("utf-8")).hexdigest()


def hmac256(texte, cle):
    return hmac.new(cle, str(texte).encode("utf-8"), hashlib.sha256).hexdigest()


def sans_accent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def annuaire(ident):
    """dictionnaire {empreinte: e-mail} de tous les e-mails de la forme prenom.nom@domaine que l'on peut fabriquer avec un annuaire de noms"""
    d = {}
    for p, n in zip(ident["prenom"], ident["nom"]):
        for dom in DOMAINES:
            e = f"{sans_accent(p).lower()}.{sans_accent(n).lower()}@{dom}"
            d[sha256(e)] = e
    return d


def region(v):
    """regroupe les vingt villes (A à T) en quatre régions de cinq villes"""
    return f"Région {(ord(v[-1]) - 65) // 5 + 1}"


def partage(t):
    """table que l'on voudrait confier à un prestataire : quasi-identifiants et deux mesures (revenu, satisfaction), sans nom ni e-mail"""
    x = t["clients"][["id_client", "ville", "annee_naissance", "canal_acquisition", "fidelite"]].merge(
        t["profil"][["id_client", "revenu_annuel", "depense_2025", "satisfaction_moy"]], on="id_client")
    x["age"] = 2025 - x["annee_naissance"]
    return x


def generaliser(x):
    y = x.copy()
    y["region"] = y["ville"].map(region)
    y["tranche"] = pd.cut(y["annee_naissance"], range(1935, 2025, 10), right=False).astype(str).str.replace(r"\[(\d+), (\d+)\)", lambda m: f"{m.group(1)}-{int(m.group(2)) - 1}", regex=True)
    return y


def taille_groupes(x, cols):
    """pour chaque ligne, le nombre de lignes qui partagent les mêmes valeurs de `cols`"""
    return x.groupby(cols)[cols[0]].transform("size")


def stats_k(x, cols, k=5):
    """groupes, plus petit groupe, clients uniques, clients dans un groupe de moins de k"""
    n = taille_groupes(x, cols)
    return {"groupes": int(x.groupby(cols).ngroups), "k_min": int(n.min()), "uniques": int((n == 1).sum()), "sous_k": int((n < k).sum())}


def bruit_laplace(compte, eps, rng, n=1):
    """compte + bruit de Laplace d'échelle 1/eps (sensibilité 1 : une personne change un comptage d'au plus 1)"""
    return compte + rng.laplace(0.0, 1.0 / eps, n)


QI_ENVOI = ["region", "tranche", "canal_acquisition", "fidelite"]


def preparer_envoi(x, cle, k=5):
    """fichier à confier à un prestataire : identifiant remplacé par un pseudonyme à clé, quasi-identifiants généralisés, revenu arrondi au millier,
    lignes des groupes de moins de k personnes supprimées. Retourne (fichier, nombre de lignes supprimées)."""
    g = generaliser(x)
    g["pseudonyme"] = ["c_" + hmac256(i, cle)[:10] for i in g["id_client"]]
    g["revenu_arrondi"] = (g["revenu_annuel"] / 1000).round() * 1000
    garde = taille_groupes(g, QI_ENVOI) >= k
    sortie = g.loc[garde, ["pseudonyme", "region", "tranche", "canal_acquisition", "fidelite", "revenu_arrondi", "satisfaction_moy"]].reset_index(drop=True)
    return sortie, int((~garde).sum())


MOTIFS = {"email": r"[^@\s]+@[^@\s]+\.[a-z]{2,}", "téléphone": r"^\+?(?:\d[\s().-]?){9,}$"}
NOMS_SUSPECTS = ("nom", "prenom", "mail", "tel", "adresse", "date_naissance", "id_client", "id_crm")


def controle_avant_envoi(df, quasi_identifiants, k=5):
    """quelques contrôles automatiques avant d'envoyer un fichier : colonnes dont le nom ou le contenu évoque un identifiant direct,
    k du fichier pour les quasi-identifiants, nombre de lignes uniques. Ne remplace pas la relecture par une personne."""
    suspectes = []
    for c in df.columns:
        if any(m in c.lower() for m in NOMS_SUSPECTS):
            suspectes.append(c); continue
        if df[c].dtype == object or str(df[c].dtype).startswith("str"):
            echantillon = df[c].dropna().astype(str).head(200)
            if len(echantillon) and any(echantillon.str.contains(p, regex=True).mean() > 0.5 for p in MOTIFS.values()):
                suspectes.append(c)
    s = stats_k(df, quasi_identifiants, k)
    return {"colonnes_suspectes": suspectes, "k_min": s["k_min"], "uniques": s["uniques"], "lignes_sous_k": s["sous_k"], "ok": (not suspectes) and s["k_min"] >= k}
