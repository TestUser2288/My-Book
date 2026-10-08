#!/usr/bin/env python3
"""Données SIMULÉES de la série 2 (Data Analyst), volume III « Analyse » — graines fixes, tout est fictif.

Même univers que les volumes I et II (la boutique : `donnees_a1.py`, copié ici sans modification) ; on ajoute des jeux propres à l'analyse.
Usage : python build/donnees_a3.py → écrit donnees/ (≈ 40 s).

VÉRITÉ PROGRAMMÉE
=================
Copies du volume I : clients, produits, commandes, lignes_commande, retours, jours_exploitation (vérité du volume I : promotion +18 % de commandes, publicité +1,5 % par 1 000 € hebdomadaires,
    pluie −8 % Boutique / +5 % Site, saison, tendance +6 %/an, jour de semaine ; voir `donnees_a1.py`).
jours_incidents.csv : version de `jours_exploitation` avec des INCIDENTS injectés, listés dans `verite_incidents.csv` : panne du site (3 jours, commandes Site à zéro), grosse commande « B2B » (+4 200 €),
    erreur de saisie (chiffre d'affaires ×10 un jour), fermeture exceptionnelle de la boutique (2 jours), doublon de journée.
ab_email.csv (12 000 contacts d'une liste de diffusion — la moitié sont des clients —, répartition aléatoire 50/50) : test d'objet d'e-mail ; taux d'ouverture A 22 % / B 25,5 % ; taux d'achat à 7 jours A 3,0 % / B 3,4 % (effet réel +0,4 point : NON significatif
    avec cette taille) ; panier ~ lognormal ; effet de nouveauté (l'écart d'ouverture décroît au fil des heures d'envoi).
ab_site.csv (≈ 40 000 sessions, 50/50 voulu) : refonte de la page de paiement ; conversion A 3,2 % / B 3,55 % ; l'effet vient entièrement du MOBILE (+0,75 point sur mobile, 0 sur ordinateur) ;
    ratio d'échantillon défectueux : B perd des sessions « ordinateur » (filtre de robots appliqué seulement à B) : répartition observée ≈ 52/48 (SRM).
sessions_web.csv (≈ 120 000 sessions 2025) : source (direct, organique, payant, email, reseaux, referent), appareil, pages vues, durée, entonnoir (ajout panier → début paiement → commande) ; les 6 078 commandes
    du canal Site de 2025 y sont rattachées (colonne `id_commande`) ; conversions par source : email 9 %, direct 7 %, organique 4 %, referent 3,5 %, payant 3 %, reseaux 2 %.
campagnes.csv : dépenses mensuelles 2025 par source payante (payant, email, reseaux) avec impressions et clics.
budget_reel_2025.csv : budget 2025 (année 2024 réelle × 1,08, avec quelques erreurs de plan par catégorie) et réalisé, par mois × catégorie × canal (CA, quantités, prix moyen, marge).
benchmark_secteur.csv : médiane et quartiles FICTIFS d'un secteur pour 12 indicateurs (à comparer à ceux de la boutique).
compte_resultat_mensuel.csv (36 mois) et bilan_annuel.csv (2023–2025) : comptes de la boutique ; CA HT = TTC / 1,2 (TVA fictive 20 %), achats = quantités × coût d'achat, loyers fixes, personnel fixe + variable,
    livraison par commande, frais bancaires 1,5 % du CA, marketing = campagnes, amortissements ; stocks, créances, dettes, trésorerie, emprunt.
livraisons.csv (commandes Site et Réseaux, 3 ans) : date d'expédition et de livraison, transporteur A/B/C (C : plus lent et plus de colis abîmés), retards en décembre ; reappro_fournisseur.csv (commandes d'achat) :
    délais promis et réels, quantités reçues (le fournisseur E est peu fiable) ; stock_quotidien.csv (20 produits × 2025) : niveau, ventes, rupture, point de commande.
employes.csv (64 collaborateurs du GROUPE auquel appartient la boutique — entrepôt et siège compris ; ce ne sont pas les seules personnes payées par le compte de résultat de la boutique) et employes_annees.csv (collaborateur × année 2021–2025) et departs.csv : poste, site, ancienneté, salaire, heures supplémentaires, absences, évaluation ; vérité : le risque de départ
    augmente avec les heures supplémentaires et un salaire inférieur à la médiane du poste, et baisse avec une promotion récente ; un écart salarial femmes/hommes de 3 % inexpliqué par le poste (à discuter avec précaution).
"""
import os
import numpy as np
import pandas as pd

import donnees_a1 as A1

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
TVA = 0.20


def jours_incidents(jours, seed=8001):
    rng = np.random.default_rng(seed)
    j = jours.copy()
    ver = []
    j["ca_site"] = np.nan
    j = j.assign(incident="")
    d = pd.to_datetime(j["date"])
    def idx(s): return int(np.where(j["date"] == s)[0][0])
    for s in ("2025-03-12", "2025-03-13", "2025-03-14"):
        i = idx(s); old = j.loc[i, "nb_commandes"]; j.loc[i, "nb_commandes"] = int(old * 0.45); j.loc[i, "chiffre_affaires"] = round(j.loc[i, "chiffre_affaires"] * 0.45, 2)
        ver.append((s, "panne_site", "commandes du Site à zéro : CA et commandes réduits à 45 % du niveau attendu"))
    i = idx("2025-06-18"); j.loc[i, "chiffre_affaires"] = round(j.loc[i, "chiffre_affaires"] + 4200, 2); ver.append(("2025-06-18", "commande_b2b", "+4 200 € (grosse commande d'un professionnel)"))
    i = idx("2025-09-09"); j.loc[i, "chiffre_affaires"] = round(j.loc[i, "chiffre_affaires"] * 10, 2); ver.append(("2025-09-09", "erreur_saisie", "chiffre d'affaires ×10"))
    for s in ("2025-04-28", "2025-04-29"):
        i = idx(s); j.loc[i, ["nb_commandes", "chiffre_affaires"]] = [int(j.loc[i, "nb_commandes"] * 0.55), round(j.loc[i, "chiffre_affaires"] * 0.55, 2)]
        ver.append((s, "fermeture_boutique", "fermeture exceptionnelle : environ 45 % de ventes en moins"))
    dup = j[j["date"] == "2025-10-20"].copy()
    j = pd.concat([j, dup], ignore_index=True).sort_values("date", kind="stable").reset_index(drop=True)
    ver.append(("2025-10-20", "doublon_journee", "la journée apparaît deux fois"))
    for s, k, _ in ver:
        j.loc[j["date"] == s, "incident"] = k
    j = j.drop(columns=["ca_site"])
    return j.drop(columns=["incident"]), pd.DataFrame(ver, columns=["date", "type", "description"])


def ab_email(clients, seed=8022):
    rng = np.random.default_rng(seed)
    n = 12000
    est_client = np.r_[np.ones(6000, int), np.zeros(n - 6000, int)][rng.permutation(n)]     # liste de diffusion : 6 000 clients + 6 000 contacts qui n'ont jamais acheté
    grp = rng.permutation(np.r_[np.zeros(n // 2, int), np.ones(n // 2, int)])
    heure = rng.integers(0, 24, n)                       # tranche horaire d'envoi (0..23)
    ouvre = rng.random(n) < np.where(grp == 1, 0.22 + 0.035 + 0.02 * np.exp(-heure / 6.0) - 0.01, 0.22)
    clic = ouvre & (rng.random(n) < 0.18)
    achat = rng.random(n) < np.where(grp == 1, 0.034, 0.030)
    montant = np.where(achat, np.exp(rng.normal(4.3, 0.7, n)), 0.0)
    return pd.DataFrame({"id_contact": np.arange(1, n + 1), "groupe": np.where(grp == 1, "B", "A"), "heure_envoi": heure, "est_client": est_client,
                         "ouvert": ouvre.astype(int), "clique": clic.astype(int), "achat_7j": achat.astype(int), "montant_7j": montant.round(2)})


def ab_site(seed=8003):
    rng = np.random.default_rng(seed)
    n = 40000
    jour = pd.Timestamp("2025-06-02") + pd.to_timedelta(rng.integers(0, 21, n), unit="D")
    grp = rng.integers(0, 2, n)
    app = rng.choice(["mobile", "ordinateur", "tablette"], n, p=[0.58, 0.36, 0.06])
    # le filtre de robots n'est appliqué qu'à B : B perd 8 % de ses sessions « ordinateur »
    perdu = (grp == 1) & (app == "ordinateur") & (rng.random(n) < 0.20)
    nouveau = rng.random(n) < 0.55
    p = 0.032 + (grp == 1) * np.where(app == "mobile", 0.0075, 0.0) + 0.006 * (~nouveau)
    conv = rng.random(n) < p
    montant = np.where(conv, np.exp(rng.normal(4.4, 0.6, n)), 0.0)
    df = pd.DataFrame({"id_session": np.arange(1, n + 1), "date": jour.strftime("%Y-%m-%d"), "groupe": np.where(grp == 1, "B", "A"), "appareil": app,
                       "nouveau_visiteur": nouveau.astype(int), "commande": conv.astype(int), "montant": montant.round(2)})
    return df[~perdu].reset_index(drop=True)


SOURCES = ["direct", "organique", "payant", "email", "reseaux", "referent"]
CONV = {"direct": 0.07, "organique": 0.04, "payant": 0.03, "email": 0.09, "reseaux": 0.02, "referent": 0.035}
PART = {"direct": 0.28, "organique": 0.34, "payant": 0.14, "email": 0.07, "reseaux": 0.12, "referent": 0.05}


def sessions(commandes, seed=8004):
    rng = np.random.default_rng(seed)
    c = commandes[(commandes["canal"] == "Site") & (commandes["date_commande"] >= "2025-01-01")].reset_index(drop=True)
    n_cmd = len(c)
    N = n_cmd / sum(PART[s] * CONV[s] for s in SOURCES)
    ns = {s: int(round(N * PART[s])) for s in SOURCES}
    cmd_src = rng.choice(SOURCES, n_cmd, p=np.array([PART[s] * CONV[s] for s in SOURCES]) / sum(PART[s] * CONV[s] for s in SOURCES))
    lignes = []
    jours = pd.date_range("2025-01-01", "2025-12-31")
    poids_j = pd.Series(1.0 + 0.5 * np.isin(jours.month, [11, 12]) + 0.2 * (jours.dayofweek >= 5), index=jours)
    poids_j = (poids_j / poids_j.sum()).values
    ordre_cmd = {s: list(np.where(cmd_src == s)[0]) for s in SOURCES}
    for s in SOURCES:
        non = max(ns[s] - len(ordre_cmd[s]), 0)
        dates = rng.choice(jours, non, p=poids_j)
        for d in dates:
            lignes.append((s, pd.Timestamp(d), -1))
        for k in ordre_cmd[s]:
            lignes.append((s, pd.Timestamp(c.loc[k, "date_commande"]), int(c.loc[k, "id_commande"])))
    df = pd.DataFrame(lignes, columns=["source", "date", "id_commande"]).sample(frac=1, random_state=5).reset_index(drop=True)
    n = len(df)
    df["id_session"] = np.arange(1, n + 1)
    df["appareil"] = rng.choice(["mobile", "ordinateur", "tablette"], n, p=[0.58, 0.36, 0.06])
    conv = df["id_commande"] > 0
    df["pages_vues"] = np.where(conv, 6 + rng.poisson(4, n), 1 + rng.poisson(2.2, n))
    df["duree_s"] = np.where(conv, rng.gamma(4, 90, n), rng.gamma(1.6, 60, n)).round(0).astype(int)
    df["nouveau_visiteur"] = (rng.random(n) < np.where(df["source"] == "email", 0.15, 0.55)).astype(int)
    panier = conv | (rng.random(n) < 0.10)
    paiement = conv | (panier & (rng.random(n) < 0.35))
    df["ajout_panier"] = panier.astype(int)
    df["debut_paiement"] = paiement.astype(int)
    df["commande"] = conv.astype(int)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df = df.sort_values(["date", "id_session"]).reset_index(drop=True)
    df["id_session"] = np.arange(1, n + 1)
    df["id_commande"] = df["id_commande"].where(df["id_commande"] > 0, np.nan)
    return df[["id_session", "date", "source", "appareil", "nouveau_visiteur", "pages_vues", "duree_s", "ajout_panier", "debut_paiement", "commande", "id_commande"]]


def campagnes(sess, seed=8005):
    rng = np.random.default_rng(seed)
    mois = pd.period_range("2025-01", "2025-12", freq="M")
    lignes = []
    for s, base, cpc in (("payant", 3100, 0.62), ("email", 600, 0.15), ("reseaux", 1600, 0.45)):
        for m in mois:
            sais = 1.0 + 0.5 * (m.month in (11, 12)) + 0.2 * (m.month in (3, 4, 5))
            dep = base * sais * np.exp(rng.normal(0, 0.08))
            clics = dep / cpc * np.exp(rng.normal(0, 0.06))
            lignes.append((str(m), s, round(dep, 2), int(clics * rng.uniform(25, 40)), int(clics)))
    return pd.DataFrame(lignes, columns=["mois", "source", "depense", "impressions", "clics"])


def budget_reel(cmd, lig, prod, seed=8006):
    rng = np.random.default_rng(seed)
    x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande").merge(prod[["id_produit", "categorie", "cout_achat"]], on="id_produit")
    x["annee"] = x["date_commande"].str[:4].astype(int); x["mois"] = x["date_commande"].str[5:7].astype(int)
    x["marge"] = x["montant"] / (1 + TVA) - x["quantite"] * x["cout_achat"]
    g = x.groupby(["annee", "mois", "categorie", "canal"]).agg(ca=("montant", "sum"), quantite=("quantite", "sum"), marge=("marge", "sum")).reset_index()
    r25 = g[g["annee"] == 2025].drop(columns="annee").rename(columns={"ca": "ca_reel", "quantite": "quantite_reel", "marge": "marge_reelle"})
    r24 = g[g["annee"] == 2024].drop(columns="annee").rename(columns={"ca": "ca_24", "quantite": "q_24", "marge": "m_24"})
    b = r25.merge(r24, on=["mois", "categorie", "canal"], how="left")
    plan = {c: rng.uniform(0.95, 1.08) for c in b["categorie"].unique()}
    b["ca_budget"] = (b["ca_24"] * 1.08 * b["categorie"].map(plan)).round(2)
    b["quantite_budget"] = (b["q_24"] * 1.05 * b["categorie"].map(plan)).round(0)
    b["marge_budget"] = (b["m_24"] * 1.08 * b["categorie"].map(plan)).round(2)
    b["prix_moyen_budget"] = (b["ca_budget"] / b["quantite_budget"]).round(2)
    b["prix_moyen_reel"] = (b["ca_reel"] / b["quantite_reel"]).round(2)
    out = b[["mois", "categorie", "canal", "ca_budget", "ca_reel", "quantite_budget", "quantite_reel", "prix_moyen_budget", "prix_moyen_reel", "marge_budget", "marge_reelle"]].copy()
    for c in ["ca_reel", "marge_reelle"]:
        out[c] = out[c].round(2)
    return out.sort_values(["mois", "categorie", "canal"]).reset_index(drop=True)


def benchmark():
    lignes = [("Taux de marge brute (HT)", "%", 38.0, 33.0, 42.0), ("Taux de retour (lignes)", "%", 5.5, 3.5, 8.5), ("Panier moyen", "€", 92.0, 70.0, 118.0), ("Taux de conversion du site", "%", 2.6, 1.8, 3.8),
              ("Part du site dans le CA", "%", 35.0, 20.0, 50.0), ("Rotation du stock (par an)", "fois", 4.2, 3.0, 5.8), ("Taux de rupture de stock", "%", 4.0, 2.0, 7.0),
              ("Livraisons à l'heure", "%", 92.0, 86.0, 96.0), ("Coût d'acquisition d'un client", "€", 18.0, 11.0, 27.0), ("Clients actifs à 12 mois", "%", 42.0, 30.0, 55.0),
              ("Part des frais de personnel dans le CA", "%", 24.0, 19.0, 29.0), ("Taux de désabonnement e-mail annuel", "%", 18.0, 12.0, 25.0)]
    return pd.DataFrame(lignes, columns=["indicateur", "unite", "mediane_secteur", "quartile_1", "quartile_3"])


def comptes(cmd, lig, prod, camp, seed=8007):
    rng = np.random.default_rng(seed)
    x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
    x["mois"] = x["date_commande"].str[:7]
    g = x.groupby("mois").agg(ca_ttc=("montant", "sum"), achats=("cout_achat", lambda s: 0.0)).reset_index()
    g["achats"] = x.assign(a=x["quantite"] * x["cout_achat"]).groupby("mois")["a"].sum().values
    g["ca_ht"] = g["ca_ttc"] / (1 + TVA)
    nb = cmd.assign(mois=cmd["date_commande"].str[:7]).groupby("mois").size().values
    nbs = cmd[cmd["canal"] != "Boutique"].assign(mois=cmd["date_commande"].str[:7]).groupby("mois").size().values
    cm = camp.groupby("mois")["depense"].sum()
    g["marketing"] = [cm.get(m, 0.0) if m.startswith("2025") else cm.get("2025" + m[4:], 0.0) * (0.82 if m.startswith("2024") else 0.7) for m in g["mois"]]
    n = len(g)
    g["variation_stock"] = rng.normal(0, 600, n).round(0)
    g["frais_personnel"] = (7500 + 0.04 * g["ca_ht"] + rng.normal(0, 300, n) + np.where(g["mois"].str[:4] == "2025", 700, 0)).round(0)
    g["loyers_charges"] = np.where(g["mois"].str[:4] == "2025", 5400, 5100).astype(float)
    g["livraison"] = (nbs * 4.2 + 0.0).round(0)
    g["frais_bancaires"] = (0.015 * g["ca_ttc"]).round(0)
    g["amortissements"] = 1900.0
    g["autres_charges"] = (2000 + rng.normal(0, 200, n)).round(0)
    g["marge_brute"] = (g["ca_ht"] - g["achats"] + g["variation_stock"]).round(0)
    g["resultat_exploitation"] = (g["marge_brute"] - g[["frais_personnel", "loyers_charges", "livraison", "frais_bancaires", "amortissements", "autres_charges", "marketing"]].sum(axis=1)).round(0)
    out = g[["mois", "ca_ht", "achats", "variation_stock", "marge_brute", "frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "amortissements", "autres_charges", "resultat_exploitation"]].copy()
    for c in ["ca_ht", "achats", "marketing"]:
        out[c] = out[c].round(0)
    bil = []
    cumul = 0.0
    for an in (2023, 2024, 2025):
        d = g[g["mois"].str[:4] == str(an)]
        ca = d["ca_ht"].sum(); ach = d["achats"].sum()
        res = d["resultat_exploitation"].sum(); cumul += res * 0.7           # résultat net approché : 70 % du résultat d'exploitation (impôt et intérêts)
        stock = ach / 4.4 * (1 + 0.02 * (an - 2023)); creances = ca / 12 * 0.35; dettes_f = ach / 12 * 1.4
        immo = 95000 - 7800 * (an - 2023)
        emprunt = 90000 - 15000 * (an - 2023)
        capitaux = 150000 + cumul
        autres = ca * 0.06
        tres = capitaux + emprunt + dettes_f + autres - immo - stock - creances
        bil.append((an, round(immo), round(stock), round(creances), round(tres), round(dettes_f), round(autres), round(capitaux), round(emprunt), round(ca), round(res)))
    bil = pd.DataFrame(bil, columns=["annee", "immobilisations_nettes", "stock", "creances_clients", "tresorerie", "dettes_fournisseurs", "autres_dettes", "capitaux_propres", "emprunt", "ca_ht", "resultat_exploitation"])
    return out, bil


def logistique(cmd, prod, lig, seed=8008):
    rng = np.random.default_rng(seed)
    e = cmd[cmd["canal"] != "Boutique"].copy().reset_index(drop=True)
    n = len(e)
    dc = pd.to_datetime(e["date_commande"])
    transp = rng.choice(["Transporteur A", "Transporteur B", "Transporteur C"], n, p=[0.45, 0.35, 0.20])
    base = np.select([transp == "Transporteur A", transp == "Transporteur B"], [2.0, 2.6], 3.4)
    dec = (dc.dt.month == 12).values.astype(float)
    delai_exp = np.clip(np.round(rng.gamma(2.0, 0.5, n) + 0.3 + 0.5 * dec + 0.5 * (dc.dt.dayofweek.values >= 4)), 0, 8).astype(int)
    delai_liv = np.clip(np.round(base + rng.gamma(2.0, 0.6, n) + 0.8 * dec + 0.8 * (e["mode_livraison"].values == "Point relais")), 1, 20).astype(int)
    prom = 6
    tot = delai_exp + delai_liv
    abime = rng.random(n) < np.select([transp == "Transporteur A", transp == "Transporteur B"], [0.010, 0.014], 0.035)
    liv = pd.DataFrame({"id_commande": e["id_commande"], "date_commande": e["date_commande"], "canal": e["canal"], "mode_livraison": e["mode_livraison"], "transporteur": transp,
                        "date_expedition": (dc + pd.to_timedelta(delai_exp, unit="D")).dt.strftime("%Y-%m-%d"), "date_livraison": (dc + pd.to_timedelta(tot, unit="D")).dt.strftime("%Y-%m-%d"),
                        "delai_promis_j": prom, "colis_abime": abime.astype(int)})
    liv["retard"] = (tot > prom).astype(int)
    # réapprovisionnement
    m = 1500
    four = rng.choice([f"Fournisseur {c}" for c in "ABCDEFGH"], m)
    promis = rng.choice([7, 10, 14, 21], m)
    inf = np.where(four == "Fournisseur E", 0.45, 0.10)
    reel = np.maximum(1, np.round(promis * (1 + rng.normal(0.0, 0.1, m)) + np.where(rng.random(m) < inf, rng.integers(3, 15, m), 0))).astype(int)
    qc = rng.choice([50, 100, 200, 400], m)
    qr = np.minimum(qc, np.round(qc * np.where(four == "Fournisseur E", rng.uniform(0.7, 1.0, m), rng.uniform(0.96, 1.0, m)))).astype(int)
    d0 = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 1095, m), unit="D")
    rea = pd.DataFrame({"id_achat": np.arange(1, m + 1), "fournisseur": four, "id_produit": rng.integers(1, 121, m), "date_commande": d0.strftime("%Y-%m-%d"), "delai_promis_j": promis,
                        "delai_reel_j": reel, "quantite_commandee": qc, "quantite_recue": qr}).sort_values("date_commande").reset_index(drop=True)
    # stock quotidien : 20 produits, politique de point de commande
    ventes_j = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande")
    ventes_j = ventes_j[ventes_j["date_commande"] >= "2025-01-01"]
    top = ventes_j.groupby("id_produit")["quantite"].sum().sort_values(ascending=False).head(20).index
    jours = pd.date_range("2025-01-01", "2025-12-31")
    lignes = []
    for p in top:
        v = ventes_j[ventes_j["id_produit"] == p].groupby("date_commande")["quantite"].sum().reindex(jours.strftime("%Y-%m-%d"), fill_value=0).values
        moy = v.mean()
        stock = int(moy * 25); pc = int(moy * 9); qcmd = int(moy * 30) + 5
        arrivees = {}
        for i, d in enumerate(jours):
            stock += arrivees.pop(i, 0)
            vendu = min(int(v[i]), stock)
            stock -= vendu
            rupt = int(v[i] > vendu)
            lignes.append((int(p), d.strftime("%Y-%m-%d"), stock, int(v[i]), rupt, pc))
            if stock <= pc and not any(k > i for k in arrivees):
                arrivees[i + int(rng.choice([7, 10, 14])) + (0 if rng.random() > 0.15 else int(rng.integers(3, 10)))] = qcmd
    stk = pd.DataFrame(lignes, columns=["id_produit", "date", "stock_fin_jour", "demande", "rupture", "point_de_commande"])
    return liv, rea, stk


def rh(seed=8009):
    rng = np.random.default_rng(seed)
    postes = {"Vendeur": (1950, 0.35, "Boutique"), "Caissier": (1850, 0.25, "Boutique"), "Logistique": (2000, 0.20, "Entrepôt"), "Service client": (2100, 0.10, "Siège"), "Responsable": (3300, 0.07, "Boutique"), "Administratif": (2600, 0.03, "Siège")}
    n = 64
    po = rng.choice(list(postes), n, p=[v[1] for v in postes.values()])
    genre = rng.choice(["F", "H"], n, p=[0.55, 0.45])
    entree = pd.Timestamp("2015-01-01") + pd.to_timedelta(rng.integers(0, 365 * 10, n), unit="D")
    rows, departs = [], []
    for i in range(n):
        base = postes[po[i]][0]
        for an in range(2021, 2026):
            deb = pd.Timestamp(f"{an}-01-01")
            if entree[i] > pd.Timestamp(f"{an}-12-31"):
                continue
            anc = max((deb - entree[i]).days / 365.25, 0)
            sal = base * (1 + 0.012 * min(anc, 15)) * (1 - 0.03 * (genre[i] == "F")) * (1.02 ** (an - 2021)) * np.exp(rng.normal(0, 0.03))
            hs = max(0.0, rng.normal(6 if po[i] in ("Logistique", "Responsable") else 3, 3))
            promo = rng.random() < 0.08
            rows.append([i + 1, an, po[i], postes[po[i]][2], genre[i], round(anc, 1), round(sal, 0), round(hs, 1), int(rng.poisson(6 + 0.5 * hs)), round(float(np.clip(rng.normal(3.4, 0.7), 1, 5)), 1), int(promo)])
    df = pd.DataFrame(rows, columns=["id_employe", "annee", "poste", "site", "genre", "anciennete", "salaire_brut_mensuel", "heures_sup_mensuelles", "jours_absence", "evaluation", "promotion"])
    med = df.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    ratio = df["salaire_brut_mensuel"] / med
    prom3 = df.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    lin = -2.6 + 0.07 * df["heures_sup_mensuelles"] - 3.0 * (ratio - 1) - 0.8 * prom3 - 0.3 * (df["evaluation"] - 3.4) - 0.03 * np.minimum(df["anciennete"], 10)
    p = 1 / (1 + np.exp(-lin))
    depart = rng.random(len(df)) < p
    df["depart_dans_l_annee"] = depart.astype(int)
    # on retire les années après le départ
    out, vus = [], set()
    for r in df.itertuples(index=False):
        if r.id_employe in vus:
            continue
        out.append(r)
        if r.depart_dans_l_annee:
            vus.add(r.id_employe)
            mot = rng.choice(["démission", "fin de contrat", "licenciement", "retraite"], p=[0.62, 0.18, 0.12, 0.08])
            departs.append((r.id_employe, f"{r.annee}-{int(rng.integers(1, 13)):02d}-15", mot))
    df2 = pd.DataFrame(out, columns=df.columns).reset_index(drop=True)
    emp = df2.sort_values("annee").groupby("id_employe").last().reset_index()[["id_employe", "poste", "site", "genre"]]
    return emp, df2, pd.DataFrame(departs, columns=["id_employe", "date_depart", "motif"])


def generer(dossier=DONNEES):
    os.makedirs(dossier, exist_ok=True)

    def ecrire(df, nom):
        df.to_csv(os.path.join(dossier, nom), index=False)
        print(f"{nom:34s} {len(df):>8d} lignes")

    cli, prod, cmd, lig, ret, jours = A1.univers()
    cmd = cmd.fillna({"code_promo": ""})
    for nom, df in [("clients.csv", cli), ("produits.csv", prod), ("commandes.csv", cmd), ("lignes_commande.csv", lig), ("retours.csv", ret), ("jours_exploitation.csv", jours)]:
        ecrire(df, nom)
    j, v = jours_incidents(jours)
    ecrire(j, "jours_incidents.csv"); ecrire(v, "verite_incidents.csv")
    ecrire(ab_email(cli), "ab_email.csv"); ecrire(ab_site(), "ab_site.csv")
    s = sessions(cmd)
    ecrire(s, "sessions_web.csv")
    camp = campagnes(s)
    ecrire(camp, "campagnes.csv")
    ecrire(budget_reel(cmd, lig, prod), "budget_reel_2025.csv")
    ecrire(benchmark(), "benchmark_secteur.csv")
    cr, bil = comptes(cmd, lig, prod, camp)
    ecrire(cr, "compte_resultat_mensuel.csv"); ecrire(bil, "bilan_annuel.csv")
    liv, rea, stk = logistique(cmd, prod, lig)
    ecrire(liv, "livraisons.csv"); ecrire(rea, "reappro_fournisseur.csv"); ecrire(stk, "stock_quotidien.csv")
    emp, ea, dep = rh()
    ecrire(emp, "employes.csv"); ecrire(ea, "employes_annees.csv"); ecrire(dep, "departs.csv")


if __name__ == "__main__":
    generer()
