"""Outils du chapitre 3 (régression) : chargement des données et petites fonctions partagées par le livre et le cahier."""
import numpy as np
import pandas as pd

FORMULE = "np.log(nb_commandes) ~ promo_active + pub_hebdo + pluie_jour + C(jour_semaine) + C(mois) + t"


def charger_jours(dossier="donnees"):
    """un jour par ligne, avec la dépense publicitaire des sept derniers jours (en k€), la pluie en 0/1, le mois et le temps en années"""
    j = pd.read_csv(f"{dossier}/jours_exploitation.csv", parse_dates=["date"])
    j["pub_hebdo"] = j["depense_pub"].rolling(7, min_periods=7).sum() / 1000
    j["mois"] = j["date"].dt.month
    j["annee"] = j["date"].dt.year
    j["t"] = (j["date"] - j["date"].min()).dt.days / 365.25
    j["pluie_jour"] = (j["pluie_mm"] > 1).astype(int)
    return j.dropna(subset=["pub_hebdo"]).reset_index(drop=True)


def charger_lignes(dossier="donnees"):
    """une ligne de commande par ligne, avec le canal, la catégorie, et un indicateur de retour"""
    c = pd.read_csv(f"{dossier}/commandes.csv", usecols=["id_commande", "canal"])
    l = pd.read_csv(f"{dossier}/lignes_commande.csv")
    r = pd.read_csv(f"{dossier}/retours.csv", usecols=["id_ligne"])
    p = pd.read_csv(f"{dossier}/produits.csv", usecols=["id_produit", "categorie"])
    x = l.merge(c, on="id_commande").merge(p, on="id_produit")
    x["retour"] = x["id_ligne"].isin(r["id_ligne"]).astype(int)
    x["promo"] = (x["remise_pct"] > 0).astype(int)
    return x


def pct(beta):
    """effet en pourcentage d'un coefficient d'un modèle sur le logarithme"""
    return (np.exp(beta) - 1) * 100
