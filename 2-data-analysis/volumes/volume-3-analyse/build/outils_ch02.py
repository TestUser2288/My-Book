"""Outils du chapitre 2 (volume III, série 2) : chargement des données et petites fonctions de test, partagées par le livre (blocs cachés) et le cahier.

    import outils_ch02 as O
    d = O.charger()          # ab_email, ab_site, jours, commandes (avec panier), lignes, retours, produits
"""
import os
import types
import numpy as np
import pandas as pd
from scipy import stats

DONNEES = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")


def lire(nom, **kw):
    return pd.read_csv(os.path.join(DONNEES, nom), **kw)


def charger():
    """Retourne un espace de noms avec les tables du chapitre."""
    d = types.SimpleNamespace()
    d.email = lire("ab_email.csv")
    d.site = lire("ab_site.csv")
    d.jours = lire("jours_exploitation.csv", parse_dates=["date"])
    d.jours["mois"] = d.jours["date"].dt.strftime("%Y-%m")
    d.commandes = lire("commandes.csv")
    d.lignes = lire("lignes_commande.csv")
    d.retours = lire("retours.csv")
    d.produits = lire("produits.csv")
    d.commandes["panier"] = d.commandes["id_commande"].map(d.lignes.groupby("id_commande")["montant"].sum())
    return d


def deux_proportions(x_a, n_a, x_b, n_b):
    """Compare deux proportions (B contre A) : écart, intervalle de confiance à 95 % (Wald), z et p-valeur (z poolé, bilatéral)."""
    pa, pb = x_a / n_a, x_b / n_b
    p = (x_a + x_b) / (n_a + n_b)
    se0 = np.sqrt(p * (1 - p) * (1 / n_a + 1 / n_b))
    z = (pb - pa) / se0
    se = np.sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)
    return {"pa": pa, "pb": pb, "ecart": pb - pa, "ic_bas": pb - pa - 1.96 * se, "ic_haut": pb - pa + 1.96 * se, "z": z, "p": 2 * (1 - stats.norm.cdf(abs(z)))}


def holm(pvals):
    """Correction de Holm : p-valeurs ajustées, dans l'ordre d'entrée."""
    p = np.asarray(pvals, float)
    ordre = np.argsort(p)
    m = len(p)
    aj = np.empty(m)
    courant = 0.0
    for rang, i in enumerate(ordre):
        courant = max(courant, (m - rang) * p[i])
        aj[i] = min(1.0, courant)
    return aj


def p_aa(rng, n_jours=21, par_jour=900, taux=0.035):
    """Un test A/A (aucun effet) suivi jour après jour : retourne la p-valeur (bilatérale) de chaque jour, calculée sur les données cumulées."""
    a = np.cumsum(rng.binomial(par_jour, taux, n_jours))
    b = np.cumsum(rng.binomial(par_jour, taux, n_jours))
    n = np.arange(1, n_jours + 1) * par_jour
    p = (a + b) / (2 * n)
    se = np.sqrt(p * (1 - p) * 2 / n)
    z = (b - a) / n / se
    return 2 * (1 - stats.norm.cdf(np.abs(z)))


def puissance_simulee(rng, p_a, p_b, n, essais=4000, alpha=0.05):
    """Part des expériences simulées qui détectent l'écart (test z bilatéral)."""
    xa = rng.binomial(n, p_a, essais)
    xb = rng.binomial(n, p_b, essais)
    p = (xa + xb) / (2 * n)
    z = (xb - xa) / n / np.sqrt(p * (1 - p) * 2 / n)
    return float((2 * (1 - stats.norm.cdf(np.abs(z))) < alpha).mean())


def taille_deux_proportions(p_a, p_b, alpha=0.05, puissance=0.8):
    """Effectif par groupe pour détecter p_a contre p_b (formule classique, test bilatéral)."""
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(puissance)
    return (za + zb) ** 2 * (p_a * (1 - p_a) + p_b * (1 - p_b)) / (p_b - p_a) ** 2


def taille_deux_moyennes(ecart, sigma, alpha=0.05, puissance=0.8):
    """Effectif par groupe pour détecter un écart de moyennes (même écart-type sigma dans les deux groupes)."""
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(puissance)
    return 2 * (za + zb) ** 2 * sigma ** 2 / ecart ** 2
