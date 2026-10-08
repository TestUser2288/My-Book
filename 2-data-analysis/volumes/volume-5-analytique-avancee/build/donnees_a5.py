#!/usr/bin/env python3
"""Données SIMULÉES de la série 2 (Data Analyst), volume V « Analytique avancée et automatisation » — graines fixes, tout est fictif.

On réutilise les données de la boutique du volume III (`donnees_a3.py`, copié sans modification ; voir sa docstring) et on ajoute, pour le chapitre 4
(« Analytique du risque et de l'assurance »), deux portefeuilles d'établissements FICTIFS (« l'assureur », « la banque » ; aucun nom, aucun pays, aucune loi réels) :

ASSURANCE AUTO — un petit assureur, 2021-2025, évaluation au 31/12/2025
  polices.csv        : une ligne par contrat (id_police, annee_debut, age_conducteur, classe_age, zone A-D, puissance 1-3, usage, bonus, canal).
  expositions.csv    : une ligne par police-année (exposition en années-police, prime_annuelle, prime_acquise = prime annuelle x exposition).
  sinistres.csv      : une ligne par sinistre (date de survenance, date de déclaration, nature, statut, montant payé à ce jour, réserve dossier-par-dossier).
  paiements.csv      : les règlements (id_sinistre, date, montant) ; sert à construire un triangle de développement.
  verite_sinistres.csv : coût ultime vrai de chaque sinistre (inconnu en pratique : sert à juger les provisions a posteriori).
  Vérité programmée :
    fréquence annuelle = 0,062 x f_âge x f_zone x f_puissance x f_usage x bonus^1,5 x f_année x frailty(Gamma, variance 0,3)
      f_âge : < 25 ans 2,3 ; 25-39 1,0 ; 40-59 0,8 ; 60+ 0,95 ; f_zone : A 0,75, B 0,95, C 1,15, D 1,45 ; f_puissance 1,0/1,1/1,3 ; f_usage pro 1,2.
      DÉRIVE RÉCENTE : en 2025 la fréquence de la zone C monte de +25 % (signal d'alerte précoce à repérer ; pas de changement ailleurs).
    sévérité : matériel (92 %) lognormale de moyenne ≈ 2 200 € ; corporel (8 %) lognormale (médiane ≈ 10 000 €) dont 4 % de queue de Pareto (> 50 000 €, plafonnée à 300 000 €) ;
      inflation de 4 % par an (année de survenance) ; zones C et D +5 %.
    tarif : prime = 428 x (facteurs âge tarifés : < 25 ans 1,6 seulement ; autres comme la vérité) x f_zone x f_puissance x f_usage x bonus^1,5, indexée de 2 % par an
      -> les jeunes conducteurs sont SOUS-TARIFÉS, et la dérive d'inflation (4 % contre 2 %) dégrade le ratio S/P année après année.
    déclaration : délai ~ exponentielle (moyenne 20 j) -> les sinistres des dernières semaines de 2025 ne sont pas encore tous déclarés (IBNR) ;
      règlement matériel en 1-2 paiements sous 6 mois ; corporel en 2-5 paiements sur 1-4 ans ; certains dossiers restent ouverts avec une réserve (= ultime x bruit).
    frais : 28 % de la prime acquise (frais généraux et d'acquisition), supposés constants.

CRÉDIT À LA CONSOMMATION ET AUX PROFESSIONNELS — une petite banque, prêts octroyés 2022-01 à 2025-06, suivi mensuel jusqu'à 2025-12
  prets.csv          : id_pret, date_octroi, montant, duree_mois, taux, segment (Particulier/Professionnel), secteur (pour les professionnels), region (Région 1-4), score_origine.
  suivi_mensuel.csv  : id_pret x mois : age_mois, encours, jours_retard, incidents_3m (incidents de paiement sur 3 mois), utilisation_decouvert (0-1).
  verite_prets.csv   : mois de défaut vrai (âge), défaut « brutal » (sans signal préalable) ou précédé d'un signal.
  Vérité programmée :
    risque mensuel de défaut = h0 x exp(-0,012 x (score-620)) x f_secteur x f_millésime x courbe_d'âge (pic entre 8 et 18 mois) x f_macro ; ≈ 6-7 % de défauts à l'échéance.
      f_secteur : Commerce 1,3 ; Restauration 1,2 ; Bâtiment 1,1 ; Services 0,9 ; Industrie 0,8 ; particuliers 1,0.
      MILLÉSIME FAIBLE : les prêts octroyés au 1er semestre 2024 ont un risque x1,5 (relâchement des critères) ; DÉRIVE 2025 : Commerce x1,6 et Restauration x1,4.
    défaut défini à 90 jours de retard. 70 % des défauts sont précédés d'un signal (à 6 mois : incidents et découvert qui montent ; 5 mois à 1 mois : retards 0, 10, 15, 40, 70 jours) ;
      30 % sont « brutaux » (fréquents chez les professionnels). Retards passagers sans défaut : 3,5 % des mois (1-29 jours), 0,4 % (30-59 jours).
    sortie du suivi : au défaut, à l'échéance, ou remboursement anticipé (1 % par mois).

Usage : python build/donnees_a5.py → écrit donnees/ (≈ 1 min).
"""
import os
import numpy as np
import pandas as pd

import donnees_a3 as A3

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
FIN = pd.Timestamp("2025-12-31")

# ----------------------------------------------------------------------------------------------- assurance
F_AGE = {"< 25 ans": 2.3, "25-39 ans": 1.0, "40-59 ans": 0.8, "60 ans et +": 0.95}
F_AGE_TARIF = {"< 25 ans": 1.6, "25-39 ans": 1.0, "40-59 ans": 0.8, "60 ans et +": 0.95}
F_ZONE = {"A": 0.75, "B": 0.95, "C": 1.15, "D": 1.45}
F_PUIS = {1: 1.0, 2: 1.1, 3: 1.3}


def _classe_age(a):
    return np.select([a < 25, a < 40, a < 60], ["< 25 ans", "25-39 ans", "40-59 ans"], "60 ans et +")


def assurance(seed=5001):
    rng = np.random.default_rng(seed)
    n = 30000
    debut = rng.choice([2021, 2022, 2023, 2024, 2025], n, p=[0.30, 0.20, 0.18, 0.17, 0.15])
    age = np.clip(rng.normal(46, 15, n), 18, 85).round().astype(int)
    classe = _classe_age(age)
    zone = rng.choice(list("ABCD"), n, p=[0.30, 0.30, 0.25, 0.15])
    puis = rng.choice([1, 2, 3], n, p=[0.40, 0.40, 0.20])
    usage = rng.choice(["Privé", "Professionnel"], n, p=[0.88, 0.12])
    bonus = np.clip(np.exp(rng.normal(0, 0.18, n)) * np.where(age < 25, 1.25, 1.0) * np.where(age >= 40, 0.9, 1.0), 0.5, 1.5).round(2)
    canal = rng.choice(["Agence", "Courtier", "Web"], n, p=[0.45, 0.30, 0.25])
    pol = pd.DataFrame({"id_police": [f"P{i + 1:05d}" for i in range(n)], "annee_debut": debut, "age_conducteur": age, "classe_age": classe, "zone": zone,
                        "puissance": puis, "usage": usage, "bonus": bonus, "canal": canal})
    frailty = rng.gamma(1 / 0.3, 0.3, n)
    pol["_frailty"] = frailty

    # police-année
    lignes = []
    for i in range(n):
        a0 = int(debut[i])
        for an in range(a0, 2026):
            expo = 1.0
            fin = False
            if an == a0:
                expo = rng.uniform(0.2, 1.0)
            if rng.random() < 0.11 and an < 2025:
                expo = rng.uniform(0.3, 1.0) if an != a0 else expo
                fin = True
            lignes.append((i, an, expo))
            if fin:
                break
    ex = pd.DataFrame(lignes, columns=["i", "annee", "exposition"])
    p = pol.iloc[ex["i"]].reset_index(drop=True)
    f_pol = (p["classe_age"].map(F_AGE) * p["zone"].map(F_ZONE) * p["puissance"].map(F_PUIS) * np.where(p["usage"] == "Professionnel", 1.2, 1.0) * p["bonus"] ** 1.5).to_numpy()
    f_an = np.where(ex["annee"].to_numpy() == 2021, 0.95, 1.0) * np.where((ex["annee"].to_numpy() == 2025) & (p["zone"].to_numpy() == "C"), 1.25, 1.0)
    lam = 0.062 * f_pol * f_an * p["_frailty"].to_numpy()
    nb = rng.poisson(lam * ex["exposition"].to_numpy())
    # tarif
    f_tar = (p["classe_age"].map(F_AGE_TARIF) * p["zone"].map(F_ZONE) * p["puissance"].map(F_PUIS) * np.where(p["usage"] == "Professionnel", 1.2, 1.0) * p["bonus"] ** 1.5).to_numpy()
    prime = (428 * f_tar * 1.02 ** (ex["annee"].to_numpy() - 2021)).round(2)
    expo_df = pd.DataFrame({"id_police": p["id_police"], "annee": ex["annee"], "exposition": ex["exposition"].round(3), "prime_annuelle": prime,
                            "prime_acquise": (prime * ex["exposition"].to_numpy()).round(2)})

    # sinistres
    idx = np.repeat(np.arange(len(ex)), nb)
    m = len(idx)
    an = ex["annee"].to_numpy()[idx]
    expo_i = ex["exposition"].to_numpy()[idx]
    # date de survenance : uniforme dans la période d'exposition (début d'année + décalage d'entrée)
    jour = np.floor(rng.uniform(0, 365 * np.minimum(expo_i + 0.0, 1.0))).astype(int)
    debut_an = pd.to_datetime(an.astype(str) + "-01-01")
    # si 1re année, l'exposition commence plus tard : on décale la fenêtre à la fin de l'année
    premiere = (an == debut[ex["i"].to_numpy()[idx]])
    decal = np.where(premiere, np.floor(365 * (1 - expo_i)).astype(int), 0)
    surv = debut_an + pd.to_timedelta(np.minimum(jour + decal, 364), unit="D")
    delai = np.round(rng.exponential(20, m)).astype(int)
    decl = surv + pd.to_timedelta(delai, unit="D")
    corporel = rng.random(m) < 0.08
    infl = 1.04 ** (an - 2021)
    zone_i = p["zone"].to_numpy()[idx]
    fz = np.where(np.isin(zone_i, ["C", "D"]), 1.05, 1.0)
    mat = rng.lognormal(np.log(2200) - 0.32, 0.8, m)
    cor = rng.lognormal(np.log(10000), 1.3, m)
    queue = corporel & (rng.random(m) < 0.04)
    cor = np.where(queue, np.minimum(50000 * (1 - rng.random(m)) ** (-1 / 1.6), 300000), cor)
    ultime = (np.where(corporel, cor, mat) * infl * fz).round(2)

    # paiements
    paie = []
    statut = np.empty(m, dtype=object)
    paye = np.zeros(m)
    reserve = np.zeros(m)
    for k in range(m):
        nbp = rng.integers(2, 6) if corporel[k] else rng.integers(1, 3)
        duree_j = rng.integers(365, 365 * 4) if corporel[k] else rng.integers(30, 180)
        parts = rng.dirichlet(np.ones(nbp) * 2) if nbp > 1 else np.array([1.0])
        t0 = decl[k] + pd.Timedelta(days=int(rng.integers(5, 40)))
        dates = [t0 + pd.Timedelta(days=int(duree_j * (j + 1) / nbp)) for j in range(nbp)]
        tot = 0.0
        for d, w in zip(dates, parts):
            if d <= FIN and decl[k] <= FIN:
                paie.append((k, d, round(float(ultime[k] * w), 2)))
                tot += round(float(ultime[k] * w), 2)
        paye[k] = tot
        if decl[k] > FIN:
            statut[k] = "Non déclaré"
        elif dates[-1] <= FIN:
            statut[k] = "Clos"
        else:
            statut[k] = "Ouvert"
            reserve[k] = round(max(ultime[k] - tot, 0) * rng.lognormal(0, 0.25), 2)
    ids = np.array([f"S{k + 1:06d}" for k in range(m)])
    sin_all = pd.DataFrame({"id_sinistre": ids, "id_police": p["id_police"].to_numpy()[idx], "date_survenance": surv.strftime("%Y-%m-%d"),
                            "date_declaration": decl.strftime("%Y-%m-%d"), "nature": np.where(corporel, "Corporel", "Matériel"), "statut": statut,
                            "montant_paye": paye.round(2), "reserve_dossier": reserve})
    verite = pd.DataFrame({"id_sinistre": ids, "cout_ultime": ultime, "declare_au_31_12_2025": decl <= FIN})
    visibles = sin_all["statut"] != "Non déclaré"
    sin = sin_all[visibles].reset_index(drop=True)
    pay = pd.DataFrame(paie, columns=["k", "date_paiement", "montant"])
    pay["id_sinistre"] = ids[pay["k"].to_numpy()]
    pay["date_paiement"] = pay["date_paiement"].dt.strftime("%Y-%m-%d")
    pay = pay[["id_sinistre", "date_paiement", "montant"]]
    pol = pol.drop(columns="_frailty")
    return pol, expo_df, sin, pay, verite


# ----------------------------------------------------------------------------------------------- crédit
F_SECT = {"Commerce": 1.3, "Restauration": 1.2, "Bâtiment": 1.1, "Services": 0.9, "Industrie": 0.8, "": 1.0}


def credit(seed=5002):
    rng = np.random.default_rng(seed)
    n = 12000
    mois_oct = pd.period_range("2022-01", "2025-06", freq="M")
    poids = np.linspace(0.8, 1.4, len(mois_oct))
    poids = poids / poids.sum()
    m0 = rng.choice(len(mois_oct), n, p=poids)
    octroi = mois_oct[m0].to_timestamp() + pd.to_timedelta(rng.integers(0, 28, n), unit="D")
    seg = rng.choice(["Particulier", "Professionnel"], n, p=[0.75, 0.25])
    secteur = np.where(seg == "Professionnel", rng.choice(["Commerce", "Services", "Bâtiment", "Restauration", "Industrie"], n, p=[0.30, 0.25, 0.20, 0.15, 0.10]), "")
    montant = np.round(np.where(seg == "Professionnel", rng.lognormal(np.log(25000), 0.7, n), rng.lognormal(np.log(8000), 0.6, n)), -2)
    duree = rng.choice([24, 36, 48, 60], n, p=[0.2, 0.35, 0.3, 0.15])
    score = np.clip(rng.normal(620, 70, n), 350, 850).round().astype(int)
    taux = np.clip(0.035 + (700 - score) * 0.00018 + rng.normal(0, 0.004, n), 0.025, 0.12).round(4)
    region = rng.choice(["Région 1", "Région 2", "Région 3", "Région 4"], n, p=[0.3, 0.3, 0.2, 0.2])
    prets = pd.DataFrame({"id_pret": [f"L{i + 1:05d}" for i in range(n)], "date_octroi": octroi.strftime("%Y-%m-%d"), "montant": montant.astype(int), "duree_mois": duree,
                          "taux": taux, "segment": seg, "secteur": secteur, "region": region, "score_origine": score})
    f_sect = pd.Series(secteur).map(F_SECT).to_numpy()
    mill = np.where((octroi >= "2024-01-01") & (octroi < "2024-07-01"), 1.5, 1.0)
    f_sc = np.exp(-0.012 * (score - 620))
    base = 0.0007
    brutal = rng.random(n) < np.where(seg == "Professionnel", 0.42, 0.22)
    age_def = np.full(n, np.nan)
    sortie = np.zeros(n, dtype=int)
    idx0 = (octroi.year * 12 + octroi.month - 1).to_numpy()   # indice de mois entier (année x 12 + mois - 1)
    tmax = 2025 * 12 + 11 - idx0
    for k in range(n):
        h = 0
        tm = min(duree[k], tmax[k])
        if tm < 1:
            sortie[k] = max(tm, 0)
            continue
        ag = np.arange(1, tm + 1)
        courbe = 0.4 + 1.6 * np.exp(-0.5 * ((ag - 12) / 6.0) ** 2)
        didx = idx0[k] + ag
        macro = np.ones(len(ag))
        if secteur[k] == "Commerce":
            macro = np.where(didx >= 2025 * 12, 1.6, 1.0)
        elif secteur[k] == "Restauration":
            macro = np.where(didx >= 2025 * 12, 1.4, 1.0)
        haz = np.clip(base * f_sc[k] * f_sect[k] * mill[k] * courbe * macro * 3.0, 0, 0.5)
        tirage = rng.random(len(ag))
        remb = rng.random(len(ag)) < 0.01
        d = np.where(tirage < haz)[0]
        r = np.where(remb)[0]
        d0 = d[0] + 1 if len(d) else None
        r0 = r[0] + 1 if len(r) else None
        if d0 is not None and (r0 is None or d0 <= r0):
            age_def[k] = d0
            sortie[k] = d0
        elif r0 is not None:
            sortie[k] = r0
        else:
            sortie[k] = tm
    # lignes mensuelles
    rep = np.repeat(np.arange(n), sortie)
    age = np.concatenate([np.arange(1, s + 1) for s in sortie]) if sortie.sum() else np.array([], dtype=int)
    midx = idx0[rep] + age
    mois = pd.to_datetime(pd.DataFrame({"year": midx // 12, "month": midx % 12 + 1, "day": 1}))
    j_avant = np.where(np.isnan(age_def[rep]), 99, age_def[rep] - age)  # mois restant avant le défaut
    signal = (~brutal[rep]) & (j_avant <= 5)
    jr = np.zeros(len(rep))
    pas = {5: 0, 4: 10, 3: 15, 2: 40, 1: 70}
    for j, v in pas.items():
        jr = np.where(signal & (j_avant == j), v + rng.integers(0, 6, len(rep)) * (v > 0), jr)
    jr = np.where(j_avant == 0, 90 + rng.integers(0, 20, len(rep)), jr)
    bruit = (jr == 0) & (j_avant > 5)
    u = rng.random(len(rep))
    jr = np.where(bruit & (u < 0.035), rng.integers(1, 30, len(rep)), jr)
    jr = np.where(bruit & (u > 0.996), rng.integers(30, 60, len(rep)), jr)
    prox = (~brutal[rep]) & (j_avant <= 6) & (j_avant >= 1)
    proche = np.clip(6 - j_avant, 0, 6)
    inc = np.where(prox, rng.poisson(0.9 + 0.2 * proche, len(rep)), rng.poisson(0.10, len(rep)))
    dec = np.clip(np.where(prox, rng.beta(2.5, 3.5, len(rep)) * (1 + 0.1 * proche), rng.beta(1.2, 8, len(rep))), 0, 1)
    enc = montant[rep] * np.clip(1 - age / duree[rep], 0, 1)
    suivi = pd.DataFrame({"id_pret": prets["id_pret"].to_numpy()[rep], "mois": mois.dt.strftime("%Y-%m-%d"), "age_mois": age, "encours": enc.round(0).astype(int),
                          "jours_retard": jr.astype(int), "incidents_3m": inc, "utilisation_decouvert": dec.round(3)})
    verite = pd.DataFrame({"id_pret": prets["id_pret"], "age_defaut": age_def, "defaut_brutal": brutal & ~np.isnan(age_def)})
    return prets, suivi, verite


def generer(dossier=DONNEES):
    A3.generer(dossier)
    pol, ex, sin, pay, ver = assurance()
    for nom, df in [("polices", pol), ("expositions", ex), ("sinistres", sin), ("paiements", pay), ("verite_sinistres", ver)]:
        df.to_csv(os.path.join(dossier, f"{nom}.csv"), index=False)
        print(f"{nom + '.csv':34s} {len(df):>8d} lignes")
    pr, su, vr = credit()
    for nom, df in [("prets", pr), ("suivi_mensuel", su), ("verite_prets", vr)]:
        df.to_csv(os.path.join(dossier, f"{nom}.csv"), index=False)
        print(f"{nom + '.csv':34s} {len(df):>8d} lignes")


if __name__ == "__main__":
    generer()
