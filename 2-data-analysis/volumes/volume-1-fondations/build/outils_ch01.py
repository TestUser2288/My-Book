"""Outils du chapitre 1 (statistique) : chargement des données de la boutique, résumés, intervalles de confiance, noms de fonctions Excel
supplémentaires pour l'affichage en français. Partagé par le livre (blocs cachés) et le cahier."""
import os
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_xl as X

DONNEES = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")

# fonctions utiles au chapitre, absentes de la table de outils_xl.FR
X.FR.update({"SKEW": "COEFFICIENT.ASYMETRIE", "KURT": "KURTOSIS", "TRIMMEAN": "MOYENNE.REDUITE", "MODE.SNGL": "MODE.SIMPLE",
             "STANDARDIZE": "CENTREE.REDUITE", "POISSON.DIST": "LOI.POISSON.N", "BINOM.DIST": "LOI.BINOMIALE.N", "T.INV.2T": "LOI.STUDENT.INVERSE.BILATERALE",
             "CONFIDENCE.T": "INTERVALLE.CONFIANCE.STUDENT", "CONFIDENCE.NORM": "INTERVALLE.CONFIANCE.NORMAL", "SQRT": "RACINE", "POWER": "PUISSANCE",
             "LN": "LN", "EXP": "EXP", "PERCENTRANK.INC": "RANG.POURCENTAGE.INCLURE", "COVARIANCE.S": "COVARIANCE.STANDARD",
             "RSQ": "COEFFICIENT.DETERMINATION", "CUMPRINC": "CUMUL.PRINCPER", "MROUND": "ARRONDI.AU.MULTIPLE", "INT": "ENT", "TRUNC": "TRONQUE"})


def charger(racine=None):
    """Retourne un espace de noms : commandes (avec `panier` et dates), lignes, produits, clients, retours, jours."""
    r = racine or DONNEES
    lire = lambda nom: pd.read_csv(os.path.join(r, nom))
    commandes, lignes, produits, clients, retours, jours = (lire(n) for n in (
        "commandes.csv", "lignes_commande.csv", "produits.csv", "clients.csv", "retours.csv", "jours_exploitation.csv"))
    panier = lignes.groupby("id_commande")["montant"].sum().rename("panier")
    commandes = commandes.merge(panier, on="id_commande")
    commandes["date_commande"] = pd.to_datetime(commandes["date_commande"])
    commandes["annee"] = commandes["date_commande"].dt.year
    commandes["mois"] = commandes["date_commande"].dt.month
    jours["date"] = pd.to_datetime(jours["date"])
    jours["annee"] = jours["date"].dt.year
    jours["mois"] = jours["date"].dt.month
    jours["jour_sem"] = jours["date"].dt.dayofweek
    lignes = lignes.merge(produits[["id_produit", "categorie", "cout_achat"]], on="id_produit").merge(
        commandes[["id_commande", "canal", "annee", "date_commande"]], on="id_commande")
    lignes["retournee"] = lignes["id_ligne"].isin(retours["id_ligne"]).astype(int)
    return SimpleNamespace(commandes=commandes, lignes=lignes, produits=produits, clients=clients, retours=retours, jours=jours)


def ic_moyenne(x, niveau=0.95):
    """intervalle de confiance (Student) de la moyenne : (borne basse, borne haute)"""
    from scipy import stats
    x = np.asarray(x, float)
    m, se = x.mean(), x.std(ddof=1) / np.sqrt(len(x))
    t = stats.t.ppf(0.5 + niveau / 2, len(x) - 1)
    return m - t * se, m + t * se


def ic_proportion(k, n, niveau=0.95, methode="wald"):
    """intervalle de confiance d'une proportion (Wald ou Wilson)"""
    from scipy import stats
    z = stats.norm.ppf(0.5 + niveau / 2)
    p = k / n
    if methode == "wald":
        h = z * np.sqrt(p * (1 - p) / n)
        return p - h, p + h
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def fmt(x, nd=2):
    """nombre à la française (virgule décimale, espace des milliers)"""
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
