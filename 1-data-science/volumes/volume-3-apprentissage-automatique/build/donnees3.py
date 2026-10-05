"""Jeux de données simulés du volume III (apprentissage automatique) : la boutique, 2025.

    python3 build/donnees3.py   ->  écrit donnees/clients_ml.csv, transactions.csv, interactions.csv, produits_ml.csv

Tables
------
clients_ml.csv (12 000 clients, observés au 31/12/2025)
    Variables d'entrée : age, ville (Ville A…Ville T : 20 modalités), canal_acquisition (Boutique/Site/Réseaux),
    appareil (mobile/ordinateur/tablette, manquant pour ~15 %), anciennete_mois, nb_commandes_12m,
    panier_moyen (manquant si aucune commande), montant_12m, recence_jours (jours depuis la dernière commande, 365 si aucune),
    nb_retours_12m, satisfaction_moy (1 à 5, manquante ~15 %, plus souvent quand elle est basse),
    nb_tickets_support_12m, programme_fidelite (0/1), nb_promos_recues_12m, part_achats_promo (0 à 1),
    taux_ouverture_email (0 à 1), delai_livraison_moy (jours, manquant ~12 %), categorie_preferee (A à D), revenu_zone (indice).
    Cibles : churn_90j (0/1 : le client ne commande plus dans les 90 jours suivants ; ~14 %), depense_6m (€ sur les 6 mois suivants,
    beaucoup de zéros), segment_vrai (0 à 3 : classe latente utilisée pour générer les comportements ; sert à VALIDER les méthodes
    non supervisées ; ne jamais l'utiliser comme variable d'entrée).
    PIÈGE VOLONTAIRE (fuite d'information) : commandes_apres_cible = nombre de commandes dans les 3 mois suivants. Elle est
    quasi parfaitement liée à churn_90j parce qu'elle appartient à l'avenir : à exclure des variables d'entrée.
transactions.csv (60 000 commandes en ligne)
    id_commande, montant, heure (0-23), jour_semaine (0-6), canal, appareil_connu (0/1), distance_facturation_livraison_km,
    nb_commandes_24h, age_compte_jours, ip_pays_different (0/1), mode_paiement (carte/virement/portefeuille),
    delai_depuis_derniere_cmd_h, nb_articles, fraude (0/1 : ~0,8 %), type_fraude (0 = aucune, 1 = compte neuf, 2 = prise de contrôle).
interactions.csv (3 000 clients x 150 produits, format long, ~5 % de cases non vides)
    id_client, id_produit, nb_achats, note (1 à 5, renseignée pour ~25 % des lignes).
produits_ml.csv : id_produit, categorie (A à D), prix, nouveaute (0/1).
credit_defaut.csv : jeu RÉEL (UCI, « Default of Credit Card Clients », licence CC0) téléchargé par build/telecharger_credit.py.

Vérité terrain (ne pas révéler avant la fin des études)
    churn : logit = c + 0,002*recence + 3,0*[recence>150 et satisfaction<3,2] - 0,15*min(nb_commandes,6) + 2,5*[tickets>=3 et retours/commandes>0,2]
            + 2,0*[part_promo>0,6 et sans fidélité] - 0,5*(ouverture_email-0,3) - 0,3*fidelite + effet_ville(sd 0,5) + 0,004*(age-45)^2
            - 0,3*[Boutique] + 0,7*[segment 0] + 0,8*[aucune commande et ancienneté>24 mois] - 1,8*[recence<40 et nb_commandes>=6]
            - 1,2*[150<montant_12m<450]
    segments : 0 occasionnels, 1 fidèles, 2 chasseurs de promotions, 3 grands paniers (proportions 38/30/20/12 %).
    fraude : type 1 (compte neuf, montant élevé, adresses éloignées, nuit : indices partiels) et type 2 (compte ancien, appareil inconnu, IP étrangère, rafale de commandes).
"""
import os

import numpy as np
import pandas as pd


def _sigmoid(z):
    return 1 / (1 + np.exp(-z))


def clients_ml(n=12000, seed=3001):
    rng = np.random.default_rng(seed)
    seg = rng.choice(4, n, p=[0.38, 0.30, 0.20, 0.12])
    freq = np.array([1.5, 7.0, 4.0, 3.0])[seg] * rng.gamma(4, 0.25, n)
    panier_mu = np.array([3.6, 3.7, 3.3, 4.7])[seg]
    promo_mu = np.array([0.15, 0.20, 0.75, 0.10])[seg]
    rec_scale = np.array([120, 35, 60, 70])[seg]
    sat_mu = np.array([3.4, 4.2, 3.6, 3.9])[seg]
    age = np.clip(np.round(rng.normal(np.array([34, 41, 29, 46])[seg], 11)), 18, 78).astype(int)
    probs_canal = np.array([[0.25, 0.35, 0.40], [0.40, 0.45, 0.15], [0.10, 0.35, 0.55], [0.45, 0.40, 0.15]])
    canal = np.array(["Boutique", "Site", "Réseaux"])[[rng.choice(3, p=probs_canal[s]) for s in seg]]
    villes = np.array([f"Ville {chr(65 + k)}" for k in range(20)])
    p_ville = rng.dirichlet(np.full(20, 2.0))
    ville_idx = rng.choice(20, n, p=p_ville)
    effet_ville = rng.normal(0, 0.5, 20)
    revenu_zone = np.round(rng.normal(40, 10, 20), 1)
    appareil = np.array(["mobile", "ordinateur", "tablette"])[rng.choice(3, n, p=[0.55, 0.35, 0.10])].astype(object)
    appareil[rng.random(n) < 0.15] = np.nan
    anciennete = np.clip(np.round(rng.gamma(2.2, 14, n)), 1, 96).astype(int)
    nb = rng.poisson(freq)
    panier = np.round(np.exp(rng.normal(panier_mu, 0.35)), 2)
    montant = np.where(nb > 0, np.round(nb * panier * rng.gamma(30, 1 / 30, n), 2), 0.0)
    recence = np.where(nb > 0, np.minimum(365, np.round(rng.exponential(rec_scale))), 365).astype(int)
    retours = rng.binomial(nb, 0.08 + 0.05 * (seg == 3))
    sat = np.clip(np.round(rng.normal(sat_mu, 0.7), 1), 1, 5)
    sat_obs = np.where(rng.random(n) < 0.10 + 0.15 * (sat < 3), np.nan, sat)
    tickets = rng.poisson(0.3 + 1.2 * np.maximum(0, 3.5 - sat))
    fidelite = rng.binomial(1, np.where(seg == 1, 0.65, 0.15))
    promos = rng.poisson(3 + 6 * (seg == 2))
    part_promo = np.clip(rng.normal(promo_mu, 0.12), 0, 1).round(3)
    ouverture = rng.beta(np.array([2, 5, 4, 3])[seg], np.array([6, 4, 3, 5])[seg]).round(3)
    livraison = np.where(rng.random(n) < 0.12, np.nan, np.round(rng.gamma(4, 0.9, n) + 1, 1))
    categorie = np.array(list("ABCD"))[[rng.choice(4, p=p) for p in np.array([[0.35, 0.30, 0.20, 0.15], [0.25, 0.25, 0.25, 0.25], [0.15, 0.20, 0.40, 0.25], [0.20, 0.15, 0.15, 0.50]])[seg]]]
    # cible : churn à 90 jours (seuils, interactions, effet ville, classe latente)
    s_eff = np.nan_to_num(sat_obs, nan=3.5)
    ratio_ret = np.where(nb > 0, retours / np.maximum(nb, 1), 0)
    z0 = (0.002 * recence + 3.0 * ((recence > 150) & (s_eff < 3.2)) - 0.15 * np.minimum(nb, 6)
          + 2.5 * ((tickets >= 3) & (ratio_ret > 0.2)) + 2.0 * ((part_promo > 0.6) & (fidelite == 0))
          - 0.5 * (ouverture - 0.3) - 0.3 * fidelite + effet_ville[ville_idx] + 0.004 * (age - 45) ** 2
          - 0.3 * (canal == "Boutique") + 0.7 * (seg == 0) + 0.8 * ((nb == 0) & (anciennete > 24))
          - 1.8 * ((recence < 40) & (nb >= 6)) - 1.2 * ((montant > 150) & (montant < 450)))
    lo, hi = -8.0, 4.0
    for _ in range(60):                                  # intercept pour une prévalence de ~14 %
        c = (lo + hi) / 2
        if _sigmoid(c + z0).mean() > 0.14: hi = c
        else: lo = c
    churn = rng.binomial(1, _sigmoid(c + z0))
    n6 = rng.poisson(freq * 0.5 * (1 - 0.8 * churn))
    depense = np.round(n6 * panier * rng.gamma(30, 1 / 30, n), 2)
    apres = rng.poisson(freq * 0.25 * (1 - 0.92 * churn))
    return pd.DataFrame({
        "id_client": np.arange(1, n + 1), "age": age, "ville": villes[ville_idx], "canal_acquisition": canal, "appareil": appareil,
        "anciennete_mois": anciennete, "nb_commandes_12m": nb, "panier_moyen": np.where(nb > 0, panier, np.nan), "montant_12m": montant,
        "recence_jours": recence, "nb_retours_12m": retours, "satisfaction_moy": sat_obs, "nb_tickets_support_12m": tickets,
        "programme_fidelite": fidelite, "nb_promos_recues_12m": promos, "part_achats_promo": part_promo, "taux_ouverture_email": ouverture,
        "delai_livraison_moy": livraison, "categorie_preferee": categorie, "revenu_zone": revenu_zone[ville_idx],
        "churn_90j": churn, "depense_6m": depense, "segment_vrai": seg, "commandes_apres_cible": apres})


def transactions(n=60000, seed=3002):
    rng = np.random.default_rng(seed)
    fraude = (rng.random(n) < 0.008).astype(int)
    typ = np.where(fraude == 1, rng.choice([1, 2], n, p=[0.55, 0.45]), 0)
    poids_h = np.array([1, 1, 1, 1, 1, 2, 3, 5, 6, 7, 7, 8, 8, 7, 7, 7, 7, 8, 9, 9, 8, 6, 3, 2], float)
    heure_l = rng.choice(24, n, p=poids_h / poids_h.sum())
    heure = np.where((typ == 1) & (rng.random(n) < 0.5), rng.choice([0, 1, 2, 3, 4, 23], n), heure_l)
    montant = np.round(np.exp(np.where(typ == 1, rng.normal(4.5, 0.8, n), np.where(typ == 2, rng.normal(4.0, 0.8, n), rng.normal(3.8, 0.8, n)))), 2)
    appareil_connu = np.where((typ == 2) & (rng.random(n) < 0.65), 0, rng.binomial(1, 0.90, n))
    distance = np.where((typ == 1) & (rng.random(n) < 0.7), rng.gamma(2.5, 60, n), np.where(rng.random(n) < 0.06, rng.gamma(3, 60, n), rng.exponential(12, n))).round(1)
    nb24 = np.where(typ == 2, rng.poisson(2.2, n), rng.poisson(0.3, n))
    age_compte = np.where((typ == 1) & (rng.random(n) < 0.6), rng.integers(0, 15, n), np.where(typ == 2, rng.gamma(3, 300, n), rng.gamma(1.6, 250, n))).astype(int)
    ip_diff = np.where(typ == 2, rng.binomial(1, 0.55, n), rng.binomial(1, 0.04, n))
    paiement = np.array(["carte", "virement", "portefeuille"])[rng.choice(3, n, p=[0.70, 0.12, 0.18])]
    delai = np.where((typ == 2) & (rng.random(n) < 0.6), rng.exponential(1.5, n), rng.exponential(150, n)).round(1)
    nb_art = 1 + rng.poisson(np.where(typ == 1, 3.0, 1.0))
    return pd.DataFrame({"id_commande": np.arange(1, n + 1), "montant": montant, "heure": heure, "jour_semaine": rng.integers(0, 7, n),
                         "canal": np.array(["Site", "Réseaux"])[rng.choice(2, n, p=[0.7, 0.3])], "appareil_connu": appareil_connu,
                         "distance_facturation_livraison_km": distance, "nb_commandes_24h": nb24, "age_compte_jours": age_compte,
                         "ip_pays_different": ip_diff, "mode_paiement": paiement, "delai_depuis_derniere_cmd_h": delai, "nb_articles": nb_art,
                         "fraude": fraude, "type_fraude": typ})


def interactions(n_users=3000, n_items=150, k=6, seed=3003):
    rng = np.random.default_rng(seed)
    cat = rng.choice(4, n_items, p=[0.3, 0.3, 0.2, 0.2])
    centres = rng.normal(0, 1.0, (4, k))
    V = centres[cat] + rng.normal(0, 0.5, (n_items, k))
    U = rng.normal(0, 1, (n_users, k))
    pop = rng.normal(0, 0.8, n_items)
    prix = np.round(np.exp(rng.normal(3.3, 0.6, n_items)), 2)
    p = _sigmoid(-3.6 + pop[None, :] + 0.55 * U @ V.T)
    achats = rng.random((n_users, n_items)) < p
    ui, ii = np.where(achats)
    nb = 1 + rng.poisson(0.4, len(ui))
    aff = (U @ V.T)[ui, ii]
    note = np.clip(np.round(3.2 + 0.5 * aff + rng.normal(0, 0.8, len(ui))), 1, 5)
    note = np.where(rng.random(len(ui)) < 0.25, note, np.nan)
    inter = pd.DataFrame({"id_client": ui + 1, "id_produit": ii + 1, "nb_achats": nb, "note": note})
    prod = pd.DataFrame({"id_produit": np.arange(1, n_items + 1), "categorie": np.array(list("ABCD"))[cat], "prix": prix,
                         "nouveaute": (rng.random(n_items) < 0.12).astype(int)})
    return inter, prod


def generer(dossier=None):
    dossier = dossier or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    os.makedirs(dossier, exist_ok=True)
    c = clients_ml(); c.to_csv(os.path.join(dossier, "clients_ml.csv"), index=False)
    t = transactions(); t.to_csv(os.path.join(dossier, "transactions.csv"), index=False)
    inter, prod = interactions()
    inter.to_csv(os.path.join(dossier, "interactions.csv"), index=False); prod.to_csv(os.path.join(dossier, "produits_ml.csv"), index=False)
    return c, t, inter, prod


if __name__ == "__main__":
    c, t, inter, prod = generer()
    print(c.shape, "churn", c.churn_90j.mean().round(3), "| transactions", t.shape, "fraude", t.fraude.mean().round(4),
          "| interactions", inter.shape, "densité", round(len(inter) / (3000 * 150), 3))
