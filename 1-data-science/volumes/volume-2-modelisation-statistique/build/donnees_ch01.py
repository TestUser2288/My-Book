"""Jeu de données hiérarchique du chapitre 1 (section 1.7) : les points relais de la boutique.
Le même code figure dans le livre (1.7.1). Usage : python3 build/donnees_ch01.py  -> donnees/ch01-relais.csv

30 points relais (urbain ou non) ; pour chaque commande retirée en relais : délai de livraison (jours) et note de
satisfaction sur 20. Vérité : note = 12 + 1,2*urbain + u0_j + (-0,7 + u1_j)*(délai - 5) + bruit(1,8),
avec u0_j ~ N(0, 1,6²) (intercept propre à chaque relais) et u1_j ~ N(0, 0,3²) (pente propre à chaque relais).
"""
import os

import numpy as np
import pandas as pd


def relais(graine=41):
    """Retourne le tableau des commandes et les vrais effets aléatoires (u0, u1), la taille et le type de chaque relais."""
    rng = np.random.default_rng(graine)
    J = 30
    tailles = np.clip(np.round(rng.lognormal(np.log(12), 0.8, J)), 3, 60).astype(int)    # commandes par relais (très inégal)
    urbain = (rng.random(J) < 0.5).astype(int)
    u0 = rng.normal(0, 1.6, J)
    u1 = rng.normal(0, 0.3, J)
    lignes = []
    for j in range(J):
        delai = rng.integers(1, 11, tailles[j])
        note = 12 + 1.2 * urbain[j] + u0[j] + (-0.7 + u1[j]) * (delai - 5) + rng.normal(0, 1.8, tailles[j])
        for d, y in zip(delai, note):
            lignes.append((f"R{j + 1:02d}", urbain[j], int(d), round(float(y), 2)))
    return pd.DataFrame(lignes, columns=["relais", "urbain", "delai", "note"]), u0, u1, tailles, urbain


if __name__ == "__main__":
    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    df = relais()[0]
    df.to_csv(os.path.join(dossier, "ch01-relais.csv"), index=False)
    print(df.shape, "| relais :", df["relais"].nunique())
