"""Jeu de données la boutique du chapitre 3 (identique au code du livre)."""
import numpy as np
import pandas as pd


def commandes():
    rng = np.random.default_rng(100)
    n = 400
    canal = rng.choice(["Réseaux", "Site", "Boutique"], size=n, p=[0.4, 0.35, 0.25])
    base = {"Réseaux": 3.7, "Site": 3.9, "Boutique": 4.1}
    montant = np.round(np.exp(rng.normal([base[c] for c in canal], 0.55)), 1)
    livraison = np.where(canal == "Boutique", 0, np.round(rng.gamma(4, 0.9, size=n)) + 1).astype(int)
    satisfaction = np.clip(np.round(4.6 - 0.18 * livraison + rng.normal(0, 0.7, size=n)), 1, 5).astype(int)
    return pd.DataFrame({"canal": canal, "montant": montant, "livraison": livraison, "satisfaction": satisfaction})
