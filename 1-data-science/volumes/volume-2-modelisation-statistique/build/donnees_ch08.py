"""Jeux de données simulés du chapitre 8 (plans d'expériences), graines fixes.

    python3 build/donnees_ch08.py     -> écrit donnees/ch08-*.csv

Vérité terrain (à ne révéler qu'APRÈS chaque analyse dans le livre)
-------------------------------------------------------------------
ch08-vitrines.csv        (4 agencements de vitrine × 12 jours, ordre des jours tiré au hasard ; ventes en €)
    moyennes vraies : Classique 200, Par couleur 215, Par thème 240, Vedette 205 ; écart-type résiduel 30.
ch08-vitrines-blocs.csv  (8 semaines = blocs × 4 agencements, une fois chacun par semaine, ordre aléatoire dans la semaine)
    ventes = 200 + effet semaine (écart-type 45) + effet agencement {Classique 0, Par couleur +15, Par thème +40, Vedette +5} + bruit (écart-type 14).
    (graine 811 : les graines 802 et 803 donnaient des échantillons atypiques, l'une avec un carré moyen résiduel anormalement bas (63 au lieu
    de ~196), l'autre avec des semaines presque identiques. On a retenu la première graine donnant un échantillon représentatif sur ces trois points
    (résidu, variabilité entre semaines, effets estimés). Le générateur est correct : carré moyen résiduel moyen de 195 sur 400 graines.)
ch08-emballage-canal.csv (3 emballages × 2 canaux × 10 commandes ; panier en €, écart-type 9)
    panier = 50 + {Kraft 0, Tissu +3, Coffret +10 (Site) ou +22 (Réseaux)} + {Site 0, Réseaux -4} ; il y a donc une INTERACTION.
ch08-factoriel-2p3.csv   (plan 2^3 répliqué 2 fois : 16 essais, ordre aléatoire ; réponse = commandes de la semaine)
    A = emballage cadeau (-1 standard, +1 cadeau), B = prix (-1 normal, +1 promo de 10 %), C = relance (-1 e-mail, +1 stories Réseaux)
    modèle en unités codées : 60 + 4A + 6B + 2C - 2.5AB + 1.5BC ; bruit : écart-type 3.5  (effets = 2 x coefficients).
ch08-factoriel-2p4.csv   (plan 2^4 NON répliqué : 16 essais ; réponse = commandes de la semaine)
    facteurs A, B, C comme ci-dessus + D = message personnalisé (-1 non, +1 oui)
    modèle codé : 60 + 4A + 6B - 3AB + 2.5D ; bruit : écart-type 1.5.
ch08-ccd-cuisson.csv     (plan composite centré à 2 facteurs, 13 essais ; réponse = % de pièces sans défaut)
    x1 = (température - 1000)/40 en °C ; x2 = (durée - 6) en heures ; α = sqrt(2) ; 5 essais au centre
    y = 84 + 3 x1 + 1 x2 - 4 x1^2 - 6 x2^2 + 2.5 x1 x2 + bruit (écart-type 0.9) ;  optimum vrai en (x1, x2) = (0.429, 0.173).
"""
import itertools
import os

import numpy as np
import pandas as pd

DOSSIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
AGENCEMENTS = ["Classique", "Par couleur", "Par thème", "Vedette"]


def vitrines(seed=801):
    rng = np.random.default_rng(seed)
    vrai = {"Classique": 200, "Par couleur": 215, "Par thème": 240, "Vedette": 205}
    etiq = np.repeat(AGENCEMENTS, 12)
    etiq = rng.permutation(etiq)                       # affectation aléatoire des 48 jours
    ventes = np.array([vrai[a] for a in etiq]) + rng.normal(0, 30, 48)
    return pd.DataFrame({"jour": np.arange(1, 49), "agencement": etiq, "ventes": np.round(ventes, 1)})


def vitrines_blocs(seed=811):
    rng = np.random.default_rng(seed)
    eff = {"Classique": 0, "Par couleur": 15, "Par thème": 40, "Vedette": 5}
    sem = rng.normal(0, 45, 8)
    lignes = []
    for s in range(8):
        for a in rng.permutation(AGENCEMENTS):        # ordre aléatoire dans le bloc
            lignes.append((s + 1, a, round(200 + sem[s] + eff[a] + rng.normal(0, 14), 1)))
    return pd.DataFrame(lignes, columns=["semaine", "agencement", "ventes"])


def emballage_canal(seed=803):
    rng = np.random.default_rng(seed)
    lignes = []
    for emb, can in itertools.product(["Kraft", "Tissu", "Coffret"], ["Site", "Réseaux"]):
        mu = 50 + {"Kraft": 0, "Tissu": 3, "Coffret": 10 if can == "Site" else 22}[emb] + (0 if can == "Site" else -4)
        for _ in range(10):
            lignes.append((emb, can, round(mu + rng.normal(0, 9), 1)))
    df = pd.DataFrame(lignes, columns=["emballage", "canal", "panier"])
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def plan_2k(k):
    """Plan factoriel complet 2^k en ordre standard (A varie le plus vite), unités codées -1/+1."""
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2**k)])


def factoriel_2p3(seed=804):
    rng = np.random.default_rng(seed)
    X = np.vstack([plan_2k(3)] * 2)
    A, B, C = X.T
    y = 60 + 4 * A + 6 * B + 2 * C - 2.5 * A * B + 1.5 * B * C + rng.normal(0, 3.5, len(X))
    df = pd.DataFrame({"A": A, "B": B, "C": C, "commandes": np.round(y, 1), "replicat": np.repeat([1, 2], 8)})
    df.insert(0, "ordre", rng.permutation(len(df)) + 1)  # ordre d'exécution tiré au hasard
    return df.sort_values("ordre").reset_index(drop=True)


def factoriel_2p4(seed=805):
    rng = np.random.default_rng(seed)
    X = plan_2k(4)
    A, B, C, D = X.T
    y = 60 + 4 * A + 6 * B - 3 * A * B + 2.5 * D + rng.normal(0, 1.5, len(X))
    df = pd.DataFrame({"A": A, "B": B, "C": C, "D": D, "commandes": np.round(y, 1)})
    df.insert(0, "ordre", rng.permutation(len(df)) + 1)
    return df.sort_values("ordre").reset_index(drop=True)


def ccd_cuisson(seed=806):
    rng = np.random.default_rng(seed)
    a = np.sqrt(2)
    pts = [(-1, -1), (1, -1), (-1, 1), (1, 1), (-a, 0), (a, 0), (0, -a), (0, a)] + [(0, 0)] * 5
    x1, x2 = np.array(pts).T
    y = 84 + 3 * x1 + 1 * x2 - 4 * x1**2 - 6 * x2**2 + 2.5 * x1 * x2 + rng.normal(0, 0.9, len(x1))
    df = pd.DataFrame({"x1": np.round(x1, 4), "x2": np.round(x2, 4),
                       "temperature_C": np.round(1000 + 40 * x1, 1), "duree_h": np.round(6 + x2, 2),
                       "reussite": np.round(y, 1)})
    df.insert(0, "ordre", rng.permutation(len(df)) + 1)
    return df.sort_values("ordre").reset_index(drop=True)


def generer():
    os.makedirs(DOSSIER, exist_ok=True)
    for nom, f in [("vitrines", vitrines), ("vitrines-blocs", vitrines_blocs), ("emballage-canal", emballage_canal),
                   ("factoriel-2p3", factoriel_2p3), ("factoriel-2p4", factoriel_2p4), ("ccd-cuisson", ccd_cuisson)]:
        f().to_csv(os.path.join(DOSSIER, f"ch08-{nom}.csv"), index=False)


if __name__ == "__main__":
    generer()
    for f in sorted(os.listdir(DOSSIER)):
        if f.startswith("ch08-"):
            print(f, pd.read_csv(os.path.join(DOSSIER, f)).shape)
