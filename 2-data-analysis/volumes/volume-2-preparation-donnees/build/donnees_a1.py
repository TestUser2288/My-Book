#!/usr/bin/env python3
"""Données SIMULÉES de la série 2 (Data Analyst), volume I « Fondations » — graines fixes, tout est fictif.

Univers : **la boutique** (une petite enseigne de maison et de décoration : 6 catégories, 120 produits), ses clients (« Ville A … Ville T »), ses trois canaux
(`Boutique`, `Site`, `Réseaux`), montants en €. Vous êtes l'analyste récemment embauchée ; la gérante vous pose des questions.

Usage : python build/donnees_a1.py → écrit donnees/ (≈ 40 s). Les fonctions retournent des DataFrames (graine par défaut).

VÉRITÉ PROGRAMMÉE (à révéler dans les chapitres quand c'est instructif)
=======================================================================
clients.csv (6 000 clients) : 4 000 clients déjà inscrits au 1er janvier 2023 (inscription 2018–2022) + 2 000 inscrits pendant 2023–2025 ; `annee_naissance` (âge moyen ≈ 43 ans),
    `ville` (20 villes, poids décroissants), `canal_acquisition`, `fidelite` (carte : 35 %), `email_valide` (92 %), `consentement_marketing` (60 %). Chaque client a une
    « propension » gamma (hétérogénéité) : quelques gros clients, beaucoup de petits.
produits.csv (120 produits) : 6 catégories × 20 ; `prix_vente` € TTC (Cuisine 8–60, Maison 12–150, Décoration 6–120, Papeterie 3–25, Jardin 8–180, Bien-être 7–70),
    `cout_achat` = 40–65 % du prix, 8 fournisseurs (« Fournisseur A… H ») ; hausse de prix de 3 % le 1er janvier 2025.
commandes.csv / lignes_commande.csv (2023-01-01 → 2025-12-31 ; ≈ 36 000 commandes, ≈ 83 000 lignes) : intensité quotidienne = base × tendance (+6 %/an) × saison
    (mensuelle : creux de janvier-février et d'été, pic de novembre-décembre) × jour de semaine (samedi +40 %, dimanche −35 %) × promotion (+18 % des commandes les jours de promotion :
    soldes d'hiver et d'été, « Vendredi noir ») × météo (la pluie : −8 % pour le canal Boutique, +5 % pour le Site). Part du canal Site : 35 % → 48 % en trois ans ;
    Réseaux ≈ 10–12 %. Codes promo : aucun ≈ 84 %, SOLDES ≈ 8 % (−20 %, pendant les périodes de promotion), BIENVENUE ≈ 1 % (−10 %, première commande dans les 30 jours de l'inscription), FIDELITE ≈ 7 % (−5 %, clients avec carte).
    Un panier compte 1 + Poisson(1,3) lignes (maximum 8) ; la catégorie « Jardin » pèse plus au printemps et en été (effet de la température sur le MIX, pas sur le volume total) et « Décoration »
    plus en décembre.
retours.csv : ≈ 6 % des lignes ; taux de retour : Site 9 %, Boutique 3 %, Réseaux 7 % ; motifs : défaut, mauvais choix de taille/modèle, livraison tardive, changement d'avis, autre.
jours_exploitation.csv (1 096 jours) : commandes et chiffre d'affaires du jour, `temperature_moy` (Ville A : sinusoïde de moyenne 13 °C, amplitude 9 °C, bruit 2,5 °C), `pluie_mm`,
    `promo_active`, `depense_pub` (dépense publicitaire quotidienne moyenne, plus forte en novembre-décembre et au printemps : elle est CORRÉLÉE à la saison, d'où une corrélation
    avec les ventes qui n'est pas causale à elle seule ; vrai effet programmé : +1,5 % de commandes pour +1 000 € de dépense hebdomadaire). La corrélation température–ventes de Jardin est forte
    mais passe par la saison.
enquete_satisfaction.csv (≈ 960 réponses sur ≈ 3 900 invitations : tous les clients ayant commandé en 2025) : satisfaction globale 1–5, livraison, prix, conseil (Boutique seulement), recommandation 0–10, commentaire court ;
    biais de réponse : répondent davantage les clients récents, les clients très satisfaits ou très mécontents, et les clients avec carte ; quelques doublons (3 %), de la ligne droite (« straight-lining », 4 %),
    20 % de réponses anonymes (`id_client` manquant).
ventes_2025.xlsx : classeur Excel (feuilles `Lignes`, `Produits`, `Clients`) de l'année 2025, pour le chapitre Excel.
export_caisse_brut.csv : export « à la française » désordonné (point-virgule, virgule décimale, dates jj/mm/aaaa, ligne de titre, ligne de total, en-tête répété, cellules vides, encodage cp1252)
    d'une semaine de caisse de la boutique physique, pour les chapitres de lecture de données et le projet.
boutique.db : base SQLite (tables clients, produits, commandes, lignes_commande, retours, jours_exploitation) pour le chapitre SQL.
"""
import os
import sqlite3
import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
VILLES = [f"Ville {chr(65 + i)}" for i in range(20)]
CANAUX = ["Boutique", "Site", "Réseaux"]
CATEGORIES = ["Cuisine", "Maison", "Décoration", "Papeterie", "Jardin", "Bien-être"]
PRIX = {"Cuisine": (8, 60), "Maison": (12, 150), "Décoration": (6, 120), "Papeterie": (3, 25), "Jardin": (8, 180), "Bien-être": (7, 70)}
MOTS = {"Cuisine": ["Casserole", "Poêle", "Bol", "Planche", "Théière", "Couteau", "Moule", "Carafe", "Tablier", "Set de table"],
        "Maison": ["Plaid", "Coussin", "Lampe", "Étagère", "Miroir", "Tapis", "Panier", "Rideau", "Cintre", "Boîte"],
        "Décoration": ["Bougie", "Vase", "Cadre", "Guirlande", "Statuette", "Horloge", "Photophore", "Affiche", "Suspension", "Bougeoir"],
        "Papeterie": ["Cahier", "Carnet", "Stylo", "Agenda", "Classeur", "Marque-page", "Trousse", "Calendrier", "Pochette", "Autocollants"],
        "Jardin": ["Arrosoir", "Pot", "Jardinière", "Sécateur", "Parasol", "Transat", "Lanterne", "Gants", "Bac", "Hamac"],
        "Bien-être": ["Savon", "Huile", "Diffuseur", "Encens", "Gommage", "Tisane", "Masque", "Peignoir", "Bougie parfumée", "Brume"]}
ADJ = ["classique", "nordique", "naturel", "compact", "XL", "mat", "brillant", "rustique", "pastel", "design"]
SAISON = np.array([0.80, 0.75, 0.85, 0.92, 0.97, 0.92, 0.80, 0.70, 1.00, 1.05, 1.30, 1.60])


def _fetes(dates):
    """jours de promotion : soldes d'hiver (début janvier, ~3 semaines), soldes d'été (fin juin, ~3 semaines), Vendredi noir (semaine du dernier vendredi de novembre)"""
    promo = np.zeros(len(dates), bool)
    for i, d in enumerate(dates):
        if (d.month == 1 and 8 <= d.day <= 28) or (d.month == 6 and d.day >= 24) or (d.month == 7 and d.day <= 14):
            promo[i] = True
        if d.month == 11 and d.day >= 22 and d.day <= 30:
            promo[i] = True
    return promo


def produits(seed=6101):
    rng = np.random.default_rng(seed)
    lignes = []
    k = 1
    for cat in CATEGORIES:
        lo, hi = PRIX[cat]
        for m in range(20):
            nom = MOTS[cat][m % 10] + " " + ADJ[(m * 3 + k) % 10]
            prix = float(np.round(np.exp(rng.uniform(np.log(lo), np.log(hi))), 0) - 0.1)
            cout = round(prix * rng.uniform(0.40, 0.65), 2)
            lignes.append((k, nom, cat, prix, cout, f"Fournisseur {chr(65 + int(rng.integers(0, 8)))}",
                           pd.Timestamp("2018-01-01") + pd.Timedelta(days=int(rng.integers(0, 2200)))))
            k += 1
    return pd.DataFrame(lignes, columns=["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat", "fournisseur", "date_lancement"])


def clients(seed=6102):
    rng = np.random.default_rng(seed)
    n_old, n_new = 4000, 2000
    n = n_old + n_new
    insc_old = pd.Timestamp("2018-01-01") + pd.to_timedelta(rng.integers(0, 1826, n_old), unit="D")
    insc_new = pd.Timestamp("2023-01-01") + pd.to_timedelta(np.sort(rng.integers(0, 1095, n_new)), unit="D")
    insc = np.concatenate([np.sort(insc_old.values), insc_new.values])
    w = np.exp(-np.arange(20) / 7.0); w /= w.sum()
    df = pd.DataFrame({"id_client": np.arange(1, n + 1), "date_inscription": pd.to_datetime(insc),
                       "annee_naissance": np.clip(np.round(rng.normal(1982, 14, n)), 1940, 2007).astype(int),
                       "ville": rng.choice(VILLES, n, p=w),
                       "canal_acquisition": rng.choice(CANAUX, n, p=[0.5, 0.38, 0.12]),
                       "fidelite": (rng.random(n) < 0.35).astype(int),
                       "email_valide": (rng.random(n) < 0.92).astype(int),
                       "consentement_marketing": (rng.random(n) < 0.6).astype(int)})
    return df


def _meteo(dates, rng):
    doy = dates.dayofyear.values
    temp = 13 + 9 * np.sin(2 * np.pi * (doy - 110) / 365.25) + rng.normal(0, 2.5, len(dates))
    pluie = np.where(rng.random(len(dates)) < 0.28, rng.gamma(1.5, 4.0, len(dates)), 0.0)
    return temp.round(1), pluie.round(1)


def univers(seed=6103):
    """génère commandes, lignes, retours, jours, à partir de clients et produits"""
    rng = np.random.default_rng(seed)
    cli = clients()
    prod = produits()
    dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    nd = len(dates)
    temp, pluie = _meteo(dates, rng)
    promo = _fetes(dates)
    t = np.arange(nd) / 365.25
    dow = dates.dayofweek.values
    wk = np.array([0.95, 0.9, 0.95, 1.0, 1.15, 1.4, 0.65])[dow]
    sais = SAISON[dates.month.values - 1]
    # dépense publicitaire quotidienne : liée à la saison (novembre-décembre, printemps), avec du bruit ; effet causal programmé : +1,5 % par 1 000 € hebdomadaires
    pub_base = 120 + 260 * (np.isin(dates.month.values, [11, 12])) + 110 * np.isin(dates.month.values, [3, 4, 5]) + 80 * promo
    pub = np.clip(pub_base * np.exp(rng.normal(0, 0.25, nd)), 20, None)
    pub_hebdo = pd.Series(pub).rolling(7, min_periods=1).sum().values
    effet_pub = 1 + 0.015 * pub_hebdo / 1000
    base = 30.0
    lam_tot = base * (1.06 ** t) * sais * wk * (1 + 0.18 * promo) * effet_pub
    # canaux
    part_site = 0.35 + 0.13 * (t / (nd / 365.25))
    part_res = 0.10 + 0.02 * (t / (nd / 365.25))
    part_boutique = 1 - part_site - part_res
    pluvieux = (pluie > 1.0)
    lam_b = lam_tot * part_boutique * np.where(pluvieux, 0.92, 1.0)
    lam_s = lam_tot * part_site * np.where(pluvieux, 1.05, 1.0)
    lam_r = lam_tot * part_res
    nb_b, nb_s, nb_r = rng.poisson(lam_b), rng.poisson(lam_s), rng.poisson(lam_r)
    # commandes
    jour_idx = np.repeat(np.arange(nd), nb_b + nb_s + nb_r)
    canal_idx = np.concatenate([np.repeat([0, 1, 2], [nb_b[i], nb_s[i], nb_r[i]]) for i in range(nd)])
    n_cmd = len(jour_idx)
    order = np.lexsort((rng.random(n_cmd), jour_idx))
    jour_idx, canal_idx = jour_idx[order], canal_idx[order]
    # clients : tirage pondéré parmi les inscrits à la date de la commande
    prop = rng.gamma(0.8, 1.0, len(cli))
    insc = cli["date_inscription"].values
    cl_cmd = np.empty(n_cmd, int)
    d_cmd = dates.values[jour_idx]
    for m in pd.period_range("2023-01", "2025-12", freq="M"):
        idx = np.where((dates[jour_idx].to_period("M") == m))[0]
        if len(idx) == 0:
            continue
        actifs = np.where(insc <= np.datetime64(m.end_time.date()))[0]
        p = prop[actifs] / prop[actifs].sum()
        cl_cmd[idx] = cli["id_client"].values[rng.choice(actifs, len(idx), p=p)]
    # on impose : un client ne commande pas avant son inscription (cas rares : on le décale au jour d'inscription)
    ins_c = cli.set_index("id_client")["date_inscription"]
    jours_cmd = pd.to_datetime(d_cmd)
    avant = ins_c.loc[cl_cmd].values > jours_cmd.values
    jours_cmd = pd.to_datetime(np.where(avant, ins_c.loc[cl_cmd].values, jours_cmd.values))
    # heure
    heures = np.clip(np.round(rng.normal(15.5, 3.2, n_cmd)), 8, 21).astype(int)
    minutes = rng.integers(0, 60, n_cmd)
    # code promo
    fid = cli.set_index("id_client")["fidelite"].loc[cl_cmd].values
    nouveau = (jours_cmd.values - ins_c.loc[cl_cmd].values) < np.timedelta64(30, "D")
    pr = promo[np.clip(((jours_cmd - pd.Timestamp("2023-01-01")).days).values, 0, nd - 1)]
    code = np.full(n_cmd, "", dtype=object)
    u = rng.random(n_cmd)
    code[(pr) & (u < 0.55)] = "SOLDES"
    code[(~pr) & nouveau & (u < 0.6)] = "BIENVENUE"
    code[(code == "") & (fid == 1) & (u < 0.22)] = "FIDELITE"
    remise_taux = {"": 0.0, "SOLDES": 0.20, "BIENVENUE": 0.10, "FIDELITE": 0.05}
    mode = np.where(canal_idx == 0, rng.choice(["Retrait magasin"], n_cmd), rng.choice(["Domicile", "Point relais", "Retrait magasin"], n_cmd, p=[0.55, 0.38, 0.07]))
    commandes = pd.DataFrame({"id_commande": np.arange(1, n_cmd + 1), "date_commande": jours_cmd.strftime("%Y-%m-%d"),
                              "heure": [f"{h:02d}:{m:02d}" for h, m in zip(heures, minutes)], "id_client": cl_cmd,
                              "canal": np.array(CANAUX)[canal_idx], "mode_livraison": mode, "code_promo": code})
    # lignes
    nb_l = np.minimum(1 + rng.poisson(1.3, n_cmd), 8)
    cmd_rep = np.repeat(np.arange(n_cmd), nb_l)
    mois_l = jours_cmd.month.values[cmd_rep]
    cat_poids = np.ones((12, 6))
    for mo in range(12):
        temp_m = 13 + 9 * np.sin(2 * np.pi * ((mo * 30.4 + 15) - 110) / 365.25)
        cat_poids[mo, 4] = np.exp(0.12 * (temp_m - 13))          # Jardin selon la température
        cat_poids[mo, 2] = 1.0 + (0.8 if mo == 11 else 0.0)      # Décoration en décembre
        cat_poids[mo, 3] = 1.0 + (0.5 if mo == 8 else 0.0)       # Papeterie : rentrée
    cat_poids = cat_poids * np.array([1.0, 1.0, 1.0, 0.8, 0.9, 0.7])
    cat_poids = cat_poids / cat_poids.sum(axis=1, keepdims=True)
    cats = np.empty(len(cmd_rep), int)
    for mo in range(12):
        ii = np.where(mois_l == mo + 1)[0]
        cats[ii] = rng.choice(6, len(ii), p=cat_poids[mo])
    id_prod = np.empty(len(cmd_rep), int)
    for c in range(6):
        ii = np.where(cats == c)[0]
        pw = np.exp(-np.arange(20) / 12.0); pw /= pw.sum()
        id_prod[ii] = 1 + c * 20 + rng.choice(20, len(ii), p=pw)
    qte = rng.choice([1, 2, 3, 4], len(cmd_rep), p=[0.85, 0.11, 0.03, 0.01])
    prix0 = prod.set_index("id_produit")["prix_vente"].loc[id_prod].values
    annee_l = jours_cmd.year.values[cmd_rep]
    prix_u = np.round(prix0 * np.where(annee_l == 2025, 1.03, 1.0), 2)
    rem = np.array([remise_taux[c] for c in code])[cmd_rep]
    lignes = pd.DataFrame({"id_ligne": np.arange(1, len(cmd_rep) + 1), "id_commande": commandes["id_commande"].values[cmd_rep],
                           "id_produit": id_prod, "quantite": qte, "prix_unitaire": prix_u, "remise_pct": (rem * 100).round(0).astype(int)})
    lignes["montant"] = (lignes["quantite"] * lignes["prix_unitaire"] * (1 - lignes["remise_pct"] / 100)).round(2)
    # retours
    canal_l = commandes["canal"].values[cmd_rep]
    p_ret = np.select([canal_l == "Site", canal_l == "Réseaux"], [0.09, 0.07], 0.03)
    ret = rng.random(len(lignes)) < p_ret
    ir = np.where(ret)[0]
    motifs = ["Défaut", "Mauvais choix", "Livraison tardive", "Changement d'avis", "Autre"]
    retours = pd.DataFrame({"id_retour": np.arange(1, len(ir) + 1), "id_ligne": lignes["id_ligne"].values[ir],
                            "date_retour": (jours_cmd[cmd_rep[ir]] + pd.to_timedelta(rng.integers(3, 21, len(ir)), unit="D")).strftime("%Y-%m-%d"),
                            "motif": rng.choice(motifs, len(ir), p=[0.18, 0.32, 0.12, 0.30, 0.08]),
                            "montant_rembourse": lignes["montant"].values[ir]})
    # jours d'exploitation
    ca_j = pd.Series(lignes["montant"].values).groupby(jours_cmd.values[cmd_rep]).sum()
    nc_j = pd.Series(1, index=jours_cmd.values).groupby(level=0).sum()
    jours = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "jour_semaine": dates.dayofweek.values + 1, "nb_commandes": nc_j.reindex(dates, fill_value=0).values,
                          "chiffre_affaires": ca_j.reindex(dates, fill_value=0.0).round(2).values, "temperature_moy": temp, "pluie_mm": pluie,
                          "promo_active": promo.astype(int), "depense_pub": pub.round(1)})
    return cli, prod, commandes, lignes, retours, jours


def enquete(commandes, lignes, clients_df, seed=6104):
    rng = np.random.default_rng(seed)
    montants = lignes.groupby("id_commande")["montant"].sum()
    dern = commandes[commandes["date_commande"] >= "2025-01-01"].copy()
    dern["montant"] = dern["id_commande"].map(montants)
    inv = dern.drop_duplicates("id_client", keep="last")          # invitation : tous les clients ayant commandé en 2025 (dernière commande)
    inv = inv.merge(clients_df[["id_client", "fidelite", "annee_naissance"]], on="id_client")
    jours_depuis = (pd.Timestamp("2025-12-31") - pd.to_datetime(inv["date_commande"])).dt.days.values
    # satisfaction latente
    lat = rng.normal(3.6, 0.9, len(inv)) + 0.3 * (inv["canal"] == "Boutique").values - 0.25 * (inv["mode_livraison"] == "Point relais").values
    p_rep = 0.17 + 0.10 * np.exp(-jours_depuis / 60) + 0.05 * inv["fidelite"].values + 0.06 * (np.abs(lat - 3.5) > 1.2)
    rep = rng.random(len(inv)) < np.clip(p_rep, 0, 0.8)
    r = inv[rep].reset_index(drop=True)
    lat = lat[rep]
    n = len(r)
    lik = lambda x: np.clip(np.round(x + rng.normal(0, 0.7, n)), 1, 5).astype(int)
    sat = lik(lat)
    liv = lik(lat + rng.normal(0, 0.3, n) - 0.2)
    prix = lik(lat - 0.3)
    conseil = lik(lat + 0.2).astype(float)
    conseil[r["canal"].values != "Boutique"] = np.nan
    reco = np.clip(np.round(2 * lat + rng.normal(0, 1.6, n) - 0.5), 0, 10).astype(int)
    tr = pd.cut(2025 - r["annee_naissance"].values, [0, 24, 34, 44, 54, 64, 120], labels=["moins de 25 ans", "25-34 ans", "35-44 ans", "45-54 ans", "55-64 ans", "65 ans et plus"]).astype(str)
    pos = ["Livraison rapide, produits conformes.", "Très bon accueil, merci.", "Joli choix, je reviendrai.", "Colis soigné.", "Bon rapport qualité-prix."]
    neu = ["Correct sans plus.", "RAS.", "Livraison un peu longue.", "Choix limité dans ma ville."]
    neg = ["Produit abîmé à la réception.", "Livraison trop tardive.", "Prix trop élevé pour la qualité.", "Service client difficile à joindre."]
    com = np.where(sat >= 4, rng.choice(pos, n), np.where(sat == 3, rng.choice(neu, n), rng.choice(neg, n)))
    com = np.where(rng.random(n) < 0.55, "", com)
    df = pd.DataFrame({"id_reponse": np.arange(1, n + 1), "date_reponse": (pd.to_datetime(r["date_commande"]) + pd.to_timedelta(rng.integers(1, 15, n), unit="D")).dt.strftime("%Y-%m-%d"),
                       "id_client": r["id_client"].values, "canal": r["canal"].values, "tranche_age": tr, "satisfaction_globale": sat, "satisfaction_livraison": liv,
                       "satisfaction_prix": prix, "satisfaction_conseil": conseil, "recommandation_0_10": reco, "commentaire": com,
                       "duree_reponse_s": np.clip(rng.lognormal(4.3, 0.55, n), 25, 1200).round(0).astype(int)})
    ano = rng.random(n) < 0.20
    df.loc[ano, "id_client"] = np.nan
    # ligne droite (straight-lining) : 4 % répondent 5-5-5-5 rapidement
    sl = rng.random(n) < 0.04
    for c in ["satisfaction_globale", "satisfaction_livraison", "satisfaction_prix"]:
        df.loc[sl, c] = 5
    df.loc[sl, "duree_reponse_s"] = rng.integers(8, 20, sl.sum())
    # doublons (3 %)
    dup = df.sample(int(0.03 * n), random_state=3).copy()
    df = pd.concat([df, dup], ignore_index=True).sort_values("date_reponse", kind="stable").reset_index(drop=True)
    df["id_reponse"] = np.arange(1, len(df) + 1)
    df.attrs["invites"] = len(inv)
    return df


def export_caisse_brut(commandes, lignes, produits_df, seed=6105):
    """une semaine de caisse de la boutique physique, désordonnée, encodée en cp1252"""
    rng = np.random.default_rng(seed)
    c = commandes[(commandes["canal"] == "Boutique") & (commandes["date_commande"] >= "2025-11-03") & (commandes["date_commande"] <= "2025-11-09")]
    l = lignes[lignes["id_commande"].isin(c["id_commande"])].merge(c[["id_commande", "date_commande", "heure"]], on="id_commande").merge(
        produits_df[["id_produit", "nom_produit", "categorie"]], on="id_produit")
    l = l.sort_values(["date_commande", "heure", "id_ligne"])
    fr = lambda x: f"{x:.2f}".replace(".", ",")
    lignes_txt = ["Export caisse - Boutique;;;;;;;", "Période du 03/11/2025 au 09/11/2025;;;;;;;", ";;;;;;;",
                  "N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant"]
    k = 0
    for r in l.itertuples():
        d = pd.Timestamp(r.date_commande).strftime("%d/%m/%Y")
        art = r.nom_produit if rng.random() > 0.05 else r.nom_produit.upper()
        cat = r.categorie if rng.random() > 0.04 else r.categorie.lower()
        qte = r.quantite
        montant = fr(r.montant) if rng.random() > 0.03 else ""
        lignes_txt.append(f"T{r.id_commande};{d};{r.heure};{art};{cat};{qte};{fr(r.prix_unitaire)};{montant}")
        k += 1
        if k % 60 == 0:
            lignes_txt.append("N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant")      # en-tête répété à chaque « page »
    tot = l["montant"].sum()
    lignes_txt.append(f";;;;;;Total;{fr(tot)}")
    return "\n".join(lignes_txt) + "\n"


def classeur_2025(commandes, lignes, produits_df, clients_df, chemin):
    import xlsxwriter
    c25 = commandes[commandes["date_commande"] >= "2025-01-01"]
    l25 = lignes[lignes["id_commande"].isin(c25["id_commande"])].merge(c25[["id_commande", "date_commande", "id_client", "canal", "code_promo"]], on="id_commande")
    l25 = l25.merge(produits_df[["id_produit", "nom_produit", "categorie"]], on="id_produit")
    l25["date_commande"] = pd.to_datetime(l25["date_commande"])
    cols = ["id_ligne", "id_commande", "date_commande", "id_client", "canal", "code_promo", "id_produit", "nom_produit", "categorie", "quantite", "prix_unitaire", "remise_pct", "montant"]
    l25 = l25[cols].sort_values("id_ligne")
    wb = xlsxwriter.Workbook(chemin)
    fd = wb.add_format({"num_format": "dd/mm/yyyy"}); fe = wb.add_format({"num_format": "#,##0.00"}); fh = wb.add_format({"bold": True, "bg_color": "#DDEBF7", "border": 1})
    ws = wb.add_worksheet("Lignes")
    for j, c in enumerate(cols):
        ws.write(0, j, c, fh)
    for i, row in enumerate(l25.itertuples(index=False), start=1):
        for j, v in enumerate(row):
            if j == 2:
                ws.write_datetime(i, j, v.to_pydatetime(), fd)
            elif j in (10, 12):
                ws.write_number(i, j, float(v), fe)
            elif isinstance(v, (int, np.integer)):
                ws.write_number(i, j, int(v))
            else:
                ws.write(i, j, "" if (isinstance(v, float) and np.isnan(v)) else v)
    ws.freeze_panes(1, 0); ws.set_column(0, 12, 14); ws.set_column(7, 8, 22)
    wp = wb.add_worksheet("Produits")
    pc = ["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat", "fournisseur"]
    for j, c in enumerate(pc):
        wp.write(0, j, c, fh)
    for i, row in enumerate(produits_df[pc].itertuples(index=False), start=1):
        for j, v in enumerate(row):
            wp.write(i, j, v if not isinstance(v, np.generic) else v.item())
    wp.set_column(0, 5, 16)
    wc = wb.add_worksheet("Clients")
    cc = ["id_client", "ville", "annee_naissance", "canal_acquisition", "fidelite"]
    for j, c in enumerate(cc):
        wc.write(0, j, c, fh)
    for i, row in enumerate(clients_df[cc].itertuples(index=False), start=1):
        for j, v in enumerate(row):
            wc.write(i, j, v if not isinstance(v, np.generic) else v.item())
    wc.set_column(0, 4, 16)
    wb.close()


def generer(dossier=DONNEES):
    os.makedirs(dossier, exist_ok=True)

    def ecrire(df, nom):
        df.to_csv(os.path.join(dossier, nom), index=False)
        print(f"{nom:30s} {len(df):>8d} lignes")

    cli, prod, cmd, lig, ret, jours = univers()
    ecrire(cli, "clients.csv"); ecrire(prod, "produits.csv"); ecrire(cmd, "commandes.csv"); ecrire(lig, "lignes_commande.csv")
    ecrire(ret, "retours.csv"); ecrire(jours, "jours_exploitation.csv")
    enq = enquete(cmd, lig, cli)
    ecrire(enq, "enquete_satisfaction.csv")
    print("invitations :", enq.attrs.get("invites"))
    txt = export_caisse_brut(cmd, lig, prod)
    with open(os.path.join(dossier, "export_caisse_brut.csv"), "w", encoding="cp1252", newline="") as f:
        f.write(txt)
    classeur_2025(cmd, lig, prod, cli, os.path.join(dossier, "ventes_2025.xlsx"))
    db = os.path.join(dossier, "boutique.db")
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db)
    for nom, df in [("clients", cli), ("produits", prod), ("commandes", cmd), ("lignes_commande", lig), ("retours", ret), ("jours_exploitation", jours)]:
        d = df.copy()
        for c in d.columns:
            if str(d[c].dtype).startswith("datetime"):
                d[c] = d[c].dt.strftime("%Y-%m-%d")
        d.to_sql(nom, con, index=False)
    con.execute("create index idx_cmd_client on commandes(id_client)"); con.execute("create index idx_cmd_date on commandes(date_commande)")
    con.execute("create index idx_lig_cmd on lignes_commande(id_commande)"); con.execute("create index idx_lig_prod on lignes_commande(id_produit)")
    con.commit(); con.close()
    print("boutique.db écrite")


if __name__ == "__main__":
    generer()
