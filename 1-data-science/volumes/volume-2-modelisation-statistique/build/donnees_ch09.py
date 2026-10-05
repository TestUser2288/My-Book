"""Données simulées du chapitre 9 (statistique spatiale). Le code est identique à celui imprimé dans le livre.
    python3 build/donnees_ch09.py  -> écrit donnees/ch09-delegations.csv et donnees/ch09-livraisons.csv

Vérité terrain
  délégations : grille 12 x 12, ventes_hab = 50 + 8*z avec (I - 0.9*W) z = e, W = contiguïté « reine » standardisée par ligne, e ~ N(0,1) ;
                ventes_bruit : N(50, 8^2) indépendant (aucune structure spatiale).
  livraisons  : 200 adresses dans un carré de 100 km x 100 km ; champ gaussien stationnaire de covariance exponentielle
                C(h) = 1.0 * exp(-h/12) (portée pratique 36 km), moyenne 4 jours, bruit de mesure (pépite) de variance 0.4.
"""
import os

import numpy as np
import pandas as pd


def contiguite_reine(n_lig, n_col):
    """Matrice de voisinage binaire (n x n) de la grille n_lig x n_col, voisins « reine » (8 directions)."""
    n = n_lig * n_col
    W = np.zeros((n, n))
    for i in range(n_lig):
        for j in range(n_col):
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di, dj) != (0, 0) and 0 <= i + di < n_lig and 0 <= j + dj < n_col:
                        W[i * n_col + j, (i + di) * n_col + (j + dj)] = 1
    return W


def delegations(seed=9, n_lig=12, n_col=12, rho=0.9):
    rng = np.random.default_rng(seed)
    W = contiguite_reine(n_lig, n_col)
    W = W / W.sum(axis=1, keepdims=True)                      # standardisation par ligne
    n = n_lig * n_col
    e = rng.normal(size=n)
    z = np.linalg.solve(np.eye(n) - rho * W, e)               # z = (I - rho W)^-1 e
    pop = np.round(rng.lognormal(8.5, 0.5, n)).astype(int)
    lig, col = np.divmod(np.arange(n), n_col)
    return pd.DataFrame({"id": np.arange(n), "lig": lig, "col": col, "x": col * 5.0 + 2.5, "y": lig * 5.0 + 2.5,
                         "population": pop, "ventes_hab": np.round(50 + 8 * z, 2),
                         "ventes_bruit": np.round(rng.normal(50, 8, n), 2)})


def livraisons(seed=27, n=200, cote=100.0, sill=1.0, a=12.0, pepite=0.4, moyenne=4.0):
    rng = np.random.default_rng(seed)
    g = np.linspace(2, cote - 2, 25)                          # grille de prédiction 25 x 25
    gx, gy = np.meshgrid(g, g)
    grille = np.column_stack([gx.ravel(), gy.ravel()])
    obs = rng.uniform(0, cote, size=(n, 2))
    pts = np.vstack([obs, grille])
    D = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(axis=2))
    C = sill * np.exp(-D / a)
    champ = moyenne + np.linalg.cholesky(C + 1e-8 * np.eye(len(pts))) @ rng.normal(size=len(pts))
    z = champ[:n] + rng.normal(0, np.sqrt(pepite), n)
    df = pd.DataFrame({"x": np.round(obs[:, 0], 2), "y": np.round(obs[:, 1], 2), "delai_jours": np.round(z, 3)})
    df["pli"] = rng.permutation(np.arange(n) % 5)             # 5 plis pour la validation croisée
    verite = pd.DataFrame({"x": grille[:, 0], "y": grille[:, 1], "champ": champ[n:]})
    return df, verite


def generer(dossier=None):
    dossier = dossier or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    os.makedirs(dossier, exist_ok=True)
    delegations().to_csv(os.path.join(dossier, "ch09-delegations.csv"), index=False)
    liv, _ = livraisons()
    liv.to_csv(os.path.join(dossier, "ch09-livraisons.csv"), index=False)


if __name__ == "__main__":
    generer()
