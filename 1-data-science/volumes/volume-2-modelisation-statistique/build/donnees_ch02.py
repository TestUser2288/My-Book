"""Jeu de données du chapitre 2 (section 2.5, GAM) : sessions de navigation sur le site de la boutique.

    python3 build/donnees_ch02.py   -> écrit donnees/ch02-sessions.csv

1 500 sessions : `duree_min` (durée de la session, minutes) et `achat` (0/1).
Vérité terrain : logit P(achat) = -1.8 + 3.0*exp(-((duree-10)/5)^2) - 0.04*duree
(une « bosse » autour de 10 minutes : trop court = pas assez regardé, trop long = visiteur perdu).
"""
import os

import numpy as np
import pandas as pd


def sessions(n=1500, seed=252):
    rng = np.random.default_rng(seed)
    d = np.round(rng.gamma(4.0, 2.8, n).clip(0.5, 35), 1)
    eta = -1.8 + 3.0 * np.exp(-((d - 10) / 5) ** 2) - 0.04 * d
    achat = rng.binomial(1, 1 / (1 + np.exp(-eta)))
    return pd.DataFrame({"duree_min": d, "achat": achat})


if __name__ == "__main__":
    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    sessions().to_csv(os.path.join(dossier, "ch02-sessions.csv"), index=False)
    print(sessions().describe().round(2))
