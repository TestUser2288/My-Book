#!/usr/bin/env python3
"""Données SIMULÉES de la série 2 (Data Analyst), volume IV « Visualisation et communication » — graines fixes, tout est fictif.

On réutilise les données de la boutique du volume III (`donnees_a3.py`, copié sans modification : clients, commandes, lignes, retours, jours, sessions web, campagnes, budget,
livraisons, comptes, etc. ; voir sa docstring pour la vérité programmée) et on ajoute :
villes.csv : les 20 villes fictives (« Ville A … Ville T ») avec des coordonnées dans un PLAN FICTIF (x, y en km, pas de vraie géographie), une région fictive (« Région 1 … 4 ») et un nombre
    d'habitants fictif ; sert aux cartes (aucune donnée géographique réelle n'est utilisée ni téléchargée).
Usage : python build/donnees_a4.py → écrit donnees/ (≈ 10 s).
"""
import os
import numpy as np
import pandas as pd

import donnees_a3 as A3

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


def villes(seed=9001):
    rng = np.random.default_rng(seed)
    n = 20
    # une grille irrégulière 5 x 4 dans un plan de 120 x 90 km, avec du bruit
    gx, gy = np.meshgrid(np.linspace(10, 110, 5), np.linspace(10, 80, 4))
    xy = np.column_stack([gx.ravel(), gy.ravel()]) + rng.normal(0, 4.5, (n, 2))
    pop = np.round(np.exp(-np.arange(n) / 7.0) * 180000 * rng.uniform(0.8, 1.2, n), -2).astype(int)
    rng.shuffle(pop)
    reg = np.where(xy[:, 0] < 45, np.where(xy[:, 1] < 45, "Région 1", "Région 2"), np.where(xy[:, 1] < 45, "Région 3", "Région 4"))
    return pd.DataFrame({"ville": [f"Ville {chr(65 + i)}" for i in range(n)], "x_km": xy[:, 0].round(1), "y_km": xy[:, 1].round(1), "region": reg, "habitants": pop})


def generer(dossier=DONNEES):
    A3.generer(dossier)
    v = villes()
    v.to_csv(os.path.join(dossier, "villes.csv"), index=False)
    print(f"{'villes.csv':34s} {len(v):>8d} lignes")


if __name__ == "__main__":
    generer()
