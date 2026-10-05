"""Simulations du chapitre 7 (inférence causale). Le code est identique à celui imprimé dans le livre.

    python3 build/sim_ch07.py   -> écrit donnees/ch07-observationnel.csv, ch07-observationnel-verite.csv,
                                           ch07-panel-villes.csv, ch07-iv.csv
"""
import os

import numpy as np
import pandas as pd


def observationnel(n=4000, seed=7001):
    """Offre de bienvenue ciblée (non aléatoire) : Yasmine l'envoie surtout aux clients engagés, jeunes, d'Instagram."""
    rng = np.random.default_rng(seed)
    age = np.clip(np.round(rng.normal(36, 11, n)), 18, 75).astype(int)
    canal = rng.choice(["Instagram", "Site", "Boutique"], n, p=[0.40, 0.35, 0.25])
    insta = (canal == "Instagram").astype(float)
    z_eng = rng.normal(0, 1, n) + 0.3 * insta - 0.01 * (age - 36)
    engagement = np.clip(np.round(50 + 15 * z_eng), 0, 100)
    ze = (engagement - 50) / 15
    p = 1 / (1 + np.exp(-(-0.5 + 0.9 * ze - 0.03 * (age - 36) + 0.6 * insta)))
    offre = rng.binomial(1, p)
    eff_canal = pd.Series(canal).map({"Boutique": 25.0, "Site": 0.0, "Instagram": -10.0}).to_numpy()
    y0 = 220 + 40 * ze - 1.2 * (age - 36) + eff_canal + rng.normal(0, 55, n)
    tau = 10 + 14 * insta                      # effet individuel : plus fort sur Instagram
    y1 = y0 + tau
    depense = np.where(offre == 1, y1, y0)
    obs = pd.DataFrame({"id_client": np.arange(1, n + 1), "age": age, "canal": canal, "engagement": engagement.astype(int),
                        "offre": offre, "depense": np.round(depense, 2)})
    verite = pd.DataFrame({"id_client": np.arange(1, n + 1), "y0": np.round(y0, 2), "y1": np.round(y1, 2)})
    return obs, verite


def panel_villes(seed=7002, tendance_diff=0.0):
    """20 villes x 24 mois (2024-2025). Campagne publicitaire Instagram lancée en juillet 2025 dans 8 grandes villes."""
    rng = np.random.default_rng(seed)
    villes = ["Tunis", "Ariana", "Ben Arous", "Manouba", "Bizerte", "Nabeul", "Hammamet", "Sousse", "Monastir", "Mahdia",
              "Sfax", "Kairouan", "Gabès", "Gafsa", "Tozeur", "Kasserine", "Le Kef", "Béja", "Jendouba", "Médenine"]
    traitees = {"Tunis", "Ariana", "Ben Arous", "Sousse", "Sfax", "Nabeul", "Monastir", "Bizerte"}
    mois = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    saison = np.log(np.array([0.70, 0.78, 0.95, 1.00, 1.10, 1.15, 1.20, 1.12, 0.90, 0.80, 1.05, 1.50]))
    effet_commun = saison[mois.month - 1] + 0.004 * np.arange(len(mois))
    lignes = []
    for v in villes:
        T = v in traitees
        niveau = rng.normal(3.3, 0.25) + (0.55 if T else 0.0)
        for t, m in enumerate(mois):
            D = int(T and m >= pd.Timestamp("2025-07-01"))
            log_mu = niveau + effet_commun[t] + 0.15 * D + (tendance_diff * t if T else 0.0)
            lignes.append({"ville": v, "mois": m.strftime("%Y-%m-%d"), "t": t, "groupe_traite": int(T), "campagne": D,
                           "commandes": int(rng.poisson(np.exp(log_mu)))})
    return pd.DataFrame(lignes)


def iv(n=5000, seed=7003, force=2.0):
    """Suivre le compte Instagram (choix libre, influencé par la passion non observée) ; instrument : rappel e-mail aléatoire."""
    rng = np.random.default_rng(seed)
    age = np.clip(np.round(rng.normal(36, 11, n)), 18, 75).astype(int)
    passion = rng.normal(0, 1, n)                    # NON OBSERVÉE
    rappel = rng.integers(0, 2, n)                   # instrument : tiré au hasard
    eta = -0.3 + force * rappel + 0.8 * passion + 0.01 * (age - 36)
    suit = rng.binomial(1, 1 / (1 + np.exp(-eta)))
    depense = 80 + 25 * suit + 30 * passion - 0.8 * (age - 36) + rng.normal(0, 40, n)
    return pd.DataFrame({"id_client": np.arange(1, n + 1), "age": age, "rappel": rappel, "suit_instagram": suit,
                         "depense": np.round(depense, 2)})


def generer(dossier=None):
    dossier = dossier or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    os.makedirs(dossier, exist_ok=True)
    obs, verite = observationnel()
    obs.to_csv(os.path.join(dossier, "ch07-observationnel.csv"), index=False)
    verite.to_csv(os.path.join(dossier, "ch07-observationnel-verite.csv"), index=False)
    panel_villes().to_csv(os.path.join(dossier, "ch07-panel-villes.csv"), index=False)
    iv().to_csv(os.path.join(dossier, "ch07-iv.csv"), index=False)


if __name__ == "__main__":
    generer()
