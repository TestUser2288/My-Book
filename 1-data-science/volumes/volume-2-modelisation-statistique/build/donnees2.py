"""Jeux de données simulés du volume II : l'univers « Dar Jasmin 2016-2025 ».

Un seul générateur, des graines fixes : tous les chapitres lisent les mêmes fichiers de donnees/.
    python3 build/donnees2.py        -> écrit donnees/clients.csv, enquete_satisfaction.csv, ventes_mensuelles.csv

Tables
------
clients.csv (2000 lignes, un client par ligne)
    id_client, age, ville, canal_acquisition (Instagram/Site/Boutique), date_inscription,
    offre_bienvenue (0/1, ATTRIBUÉE AU HASARD : expérience randomisée),
    nb_commandes_an (entier, surdispersé), panier_moyen (DT, 0 si aucune commande),
    depense_annuelle (DT, 0 pour les clients sans commande : asymétrique, avec beaucoup de zéros),
    rachat_12m (0/1), duree_mois (durée observée de la relation), churn (1 = départ observé, 0 = censuré).
enquete_satisfaction.csv (≈1200 répondants : 60 % des clients, tirés au hasard)
    id_client, q1..q8 (notes 1 à 5), dont q1-q4 mesurent la qualité des produits
    et q5-q8 la qualité du service/livraison (deux facteurs latents corrélés).
ventes_mensuelles.csv (120 mois, janvier 2016 à décembre 2025)
    mois (AAAA-MM-01), ca (DT), nb_commandes, promo (0/1), covid (0/1 : mars-juin 2020).
    Tendance + saisonnalité annuelle (pic en décembre) + bruit autocorrélé + choc de 2020.

Vérité terrain (utile pour contrôler les modèles : ne PAS la révéler avant la fin de chaque étude)
    panier : log(panier) = 4.00 + 0.008*(age-36) + {Boutique:+0.22, Site:+0.05, Instagram:-0.12} + 0.12*F1 + bruit(0.35)
    nb_commandes_an ~ NegBin(moyenne exp(1.25 + 0.22*F1 + 0.10*F2 + {Site:+0.15, Boutique:+0.05} - 0.005*(age-36)), k=2)
    rachat_12m ~ Bernoulli(logit^-1(-0.35 + 0.45*F1 + 0.35*F2 - 0.015*(age-36) + 0.55*offre + {Boutique:+0.3}))
    duree ~ Weibull(forme 1.35), échelle exp(3.6 + 0.30*F2 + 0.35*offre + {Boutique:+0.30, Instagram:-0.15} + 0.008*(age-36))
"""
import os

import numpy as np
import pandas as pd

FIN = pd.Timestamp("2025-12-31")


def clients(n=2000, seed=2016):
    rng = np.random.default_rng(seed)
    age = np.clip(np.round(rng.normal(36, 11, n)), 18, 75).astype(int)
    ville = rng.choice(["Tunis", "Sousse", "Sfax", "Nabeul", "Bizerte", "Autre"], n, p=[0.30, 0.18, 0.15, 0.12, 0.10, 0.15])
    canal = rng.choice(["Instagram", "Site", "Boutique"], n, p=[0.40, 0.35, 0.25])
    jours = rng.integers(0, (pd.Timestamp("2025-06-30") - pd.Timestamp("2019-01-01")).days + 1, n)
    inscription = pd.Timestamp("2019-01-01") + pd.to_timedelta(jours, unit="D")
    offre = rng.integers(0, 2, n)
    # deux facteurs latents corrélés : F1 = goût pour les produits, F2 = sensibilité au service
    corr = 0.3
    z = rng.normal(size=(n, 2))
    F1 = z[:, 0]
    F2 = corr * z[:, 0] + np.sqrt(1 - corr**2) * z[:, 1]
    a = age - 36
    eff_canal_panier = pd.Series(canal).map({"Boutique": 0.22, "Site": 0.05, "Instagram": -0.12}).to_numpy()
    mu = 1.25 + 0.22 * F1 + 0.10 * F2 + pd.Series(canal).map({"Site": 0.15, "Boutique": 0.05, "Instagram": 0.0}).to_numpy() - 0.005 * a
    k = 2.0
    lam = rng.gamma(k, np.exp(mu) / k)
    nb = rng.poisson(lam)
    log_panier = 4.0 + 0.008 * a + eff_canal_panier + 0.12 * F1 + rng.normal(0, 0.35, n)
    panier = np.where(nb > 0, np.round(np.exp(log_panier), 2), 0.0)
    depense = np.where(nb > 0, np.round(nb * np.exp(log_panier) * rng.gamma(40, 1 / 40, n), 2), 0.0)
    eta = -0.35 + 0.45 * F1 + 0.35 * F2 - 0.015 * a + 0.55 * offre + pd.Series(canal).map({"Boutique": 0.3}).fillna(0).to_numpy()
    rachat = rng.binomial(1, 1 / (1 + np.exp(-eta)))
    # survie : durée Weibull (mois), censure administrative au 31/12/2025 + quelques pertes de vue
    echelle = np.exp(3.6 + 0.30 * F2 + 0.35 * offre + pd.Series(canal).map({"Boutique": 0.30, "Instagram": -0.15, "Site": 0.0}).to_numpy() + 0.008 * a)
    t = echelle * rng.weibull(1.35, n)
    max_obs = (FIN - inscription).days / 30.4375
    perdu = rng.exponential(120, n)               # perte de vue très rare
    duree = np.minimum.reduce([t, max_obs, perdu])
    churn = (t <= np.minimum(max_obs, perdu)).astype(int)
    df = pd.DataFrame({
        "id_client": np.arange(1, n + 1), "age": age, "ville": ville, "canal_acquisition": canal,
        "date_inscription": inscription.strftime("%Y-%m-%d"), "offre_bienvenue": offre,
        "nb_commandes_an": nb, "panier_moyen": panier, "depense_annuelle": depense,
        "rachat_12m": rachat, "duree_mois": np.round(duree, 2), "churn": churn})
    return df, F1, F2


def enquete(F1, F2, seed=2017):
    rng = np.random.default_rng(seed)
    n = len(F1)
    repond = rng.random(n) < 0.60
    charges = [(0.80, 0), (0.70, 0), (0.75, 0), (0.60, 0), (0.80, 1), (0.70, 1), (0.75, 1), (0.65, 1)]
    cols = {}
    for j, (l, f) in enumerate(charges, start=1):
        F = F1 if f == 0 else F2
        brut = l * F + np.sqrt(1 - l**2) * rng.normal(size=n)
        cols[f"q{j}"] = np.clip(np.round(3.6 + 0.95 * brut), 1, 5).astype(int)
    q = pd.DataFrame(cols)
    q.insert(0, "id_client", np.arange(1, n + 1))
    return q[repond].reset_index(drop=True)


def ventes(seed=2018):
    rng = np.random.default_rng(seed)
    mois = pd.date_range("2016-01-01", "2025-12-01", freq="MS")
    t = np.arange(len(mois))
    saison = np.array([0.62, 0.72, 0.95, 1.00, 1.12, 1.18, 1.22, 1.15, 0.90, 0.78, 1.05, 1.55])
    s = saison[mois.month - 1]
    # AR(1) sur le log
    e = np.zeros(len(mois))
    for i in range(1, len(mois)):
        e[i] = 0.5 * e[i - 1] + rng.normal(0, 0.07)
    promo = (rng.random(len(mois)) < 0.15).astype(int)
    covid = ((mois >= "2020-03-01") & (mois <= "2020-06-01")).astype(int)
    log_ca = np.log(1000) + 0.0075 * t + np.log(s) + e + 0.10 * promo - 0.55 * covid
    ca = np.round(np.exp(log_ca), 1)
    nb = rng.poisson(ca / 58.0)
    return pd.DataFrame({"mois": mois.strftime("%Y-%m-%d"), "ca": ca, "nb_commandes": nb, "promo": promo, "covid": covid})


def generer(dossier=None):
    dossier = dossier or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    os.makedirs(dossier, exist_ok=True)
    c, F1, F2 = clients()
    c.to_csv(os.path.join(dossier, "clients.csv"), index=False)
    enquete(F1, F2).to_csv(os.path.join(dossier, "enquete_satisfaction.csv"), index=False)
    ventes().to_csv(os.path.join(dossier, "ventes_mensuelles.csv"), index=False)
    return c


if __name__ == "__main__":
    c = generer()
    print(c.describe().round(2).T)
