#!/usr/bin/env python3
"""Données SIMULÉES du volume V « Risque et assurance » (graines fixes ; tout est fictif).

Univers : un **établissement de crédit** et une **mutuelle d'assurance** fictifs (sans nom, sans pays) ; montants en €,
zones « Zone A … Zone F », pays « Pays P1 … P12 ». Aucune donnée réelle, sauf `credit_defaut.csv` (UCI, CC0), copié du volume III.

Usage : python build/donnees5.py   → écrit les CSV dans donnees/ (≈ 40 s). Les fonctions retournent des DataFrames (graine par défaut).

VÉRITÉ PROGRAMMÉE (à révéler dans les chapitres quand c'est instructif)
=======================================================================
credits_conso.csv  (40 000 prêts à la souscription, défaut à 12 mois ≈ 6 %)
    logit(PD) = c + 1,3·[0,0012·(âge−47)² − 0,12·min(ancienneté_emploi,10) + 1,5·dti + 3·max(0,dti−0,5) + 0,55·incidents
                + 0,35·[locataire] + 0,5·[hébergé] + 0,25·[objet=conso] − 0,10·[objet=travaux] + 0,012·durée
                − 0,5·(ln revenu − ln 32 000) − 0,04·min(ancienneté_relation,15)]        (c calé pour 6 %)
    Effets NON linéaires (âge en U, dti en coude) : un grille de score par classes les retrouve, une logistique linéaire non.
    Manquants INFORMATIFS : `anciennete_emploi` manque plus souvent quand le risque est élevé (≈ 8 %) ; `revenu_annuel` ≈ 5 %.
recouvrements.csv  (6 000 prêts en défaut ; LGD réalisée) : LGD ~ Beta(μk,(1−μ)k), k=2,2, μ = sigmoïde(−0,2+1,0·[sans garantie]−0,7·[caution]−0,2·[nantissement]
    +0,25·[objet=conso]) ; avec probabilité 0,12 la perte est nulle (récupération complète). Valeur moyenne ≈ 0,46.
revolving_defauts.csv (8 000 lignes de crédit renouvelable en défaut) : CCF vrai ~ Beta(2,3) décalé selon l'utilisation (moyenne ≈ 0,4, plus haut quand
    la ligne était peu utilisée) ; EAD = tirage_12m_avant + CCF·(limite − tirage_12m_avant).
portefeuille_ifrs9.csv (20 000 prêts) : pd_origine lognormale (médiane 2 %), pd_actuelle = pd_origine·exp(N(0,15 ; 0,6)) ; jours de retard (0 pour 91 %, 1–29 : 3 %,
    30–89 : 3,6 %, ≥ 90 : 2,4 %) ; LGD estimée 20–60 % ; taux d'intérêt effectif 3–8 %. Les « étapes » IFRS 9 sont à calculer par le lecteur.
notations_panel.csv (5 000 emprunteurs, 10 ans, 7 notes + défaut=8, 0 = sorti du portefeuille) : matrice de transition annuelle `matrice_vraie()` (7×8) déformée
    chaque année par un facteur macro z_t : les baisses de note sont multipliées par exp(0,6·z_t) (récession aux années 5 et 6). Retraits : 4 % par an.
taux_defaut_macro.csv (80 trimestres) : taux de défaut = sigmoïde(−3,6 − 0,30·croissance_z + 0,20·chômage_z − 0,12·immo_z + bruit) ; récession aux trimestres 48–54.
polices_auto.csv (100 000 lignes police-année 2022–2024) : fréquence annuelle moyenne ≈ 6,5 % ; log λ = c + 0,55·[âge<25] + 0,15·[âge>70] + 0,04·puissance + effet de zone
    (A −0,20, B −0,10, C 0, D 0,08, E 0,18, F 0,30) + 0,006·(bonus_malus−100) + 0,10·[usage pro] − 0,15·[hybride/électrique] − 0,02·min(âge_véhicule,10) ;
    hétérogénéité non observée : facteur Gamma de variance 0,4 (donc sur-dispersion, binomiale négative) ; nombre de sinistres ~ Poisson(exposition·λ·facteur).
sinistres_auto.csv : matériel (90 %) ~ Gamma(forme 2,5) de moyenne 1 900·exp(0,05·puissance + effet de zone/2) ; corporel (10 %) ~ lognormale(9,0 ; 1,6),
    dont 8 % remplacés par une queue de Pareto (alpha 1,8) au-delà de 100 000 € ; inflation de 4 % par an (année de survenance).
triangle_rc.csv / triangle_dommages.csv / triangle_choc.csv (10 années de survenance 2015–2024, évaluation fin 2024) : paiements incrémentaux = loi de Poisson sur-dispersée
    (φ = 20 000 € ; moyenne = prime·ratio de sinistralité·profil de paiement) ; RC à queue longue (profil sur 13 délais), dommages à queue courte (6 délais) ;
    inflation civile 2 %/an dans RC ; `triangle_choc.csv` ajoute un choc de +12 % sur toute la diagonale 2022 (viole l'hypothèse du chain ladder).
    Les `triangle_*_verite.csv` donnent les paiements FUTURS réels (carré complet) : on peut juger les provisions a posteriori.
sante_assures.csv (≈ 40 000 lignes assuré-année 2022–2024) : coûts par poste ; l'affection de longue durée (ALD) multiplie les consultations ×2,5 et les hospitalisations ×5 ;
    niveau de garantie : sélection adverse (les plus malades prennent « premium ») et aléa moral (+15 % / +35 % de consommation).
rendements_marche.csv (4 000 jours ouvrés depuis 2010-01-04, 5 actifs) : GARCH(1,1) à innovations t(5) ; deux régimes de Markov (calme/stress) : en stress, volatilité ×2
    et corrélations entre actions et immobilier ≈ 0,85 (≈ 0,45 en calme) ; `marche_verite.csv` donne le régime vrai.
courbe_taux.csv (120 mois, 9 maturités) : Nelson–Siegel dont niveau, pente et courbure suivent des AR(1) ; cycle de hausse des taux aux mois 60–90.
pertes_operationnelles.csv (10 ans, ≈ 1 800 événements) : fréquence de Poisson (150/an, +4 %/an) ; sévérité = lognormale(7,8 ; 1,3) + queue de Pareto généralisée (ξ=0,7) pour 3 % des événements.
sinistres_gros.csv (15 ans, ≈ 2 900 sinistres incendie) : lognormale(10,2 ; 1,5) + queue GPD (ξ=0,55) au-delà de 500 000 € pour 4 % ; `cat_annuel.csv` (40 ans) : 55 % d'années
    sans événement, sinon Pareto (ξ=0,9, minimum 2 M€).
mortalite_population.csv (sexe × âge 0–99 × années 1980–2019) : Lee–Carter exact : ln m(x,t) = a_x + b_x·k_t, b_x ∝ exp(−((x−35)/40)²)+0,2 (somme 1), k_t marche aléatoire de dérive −1,2
    (écart-type 1,0), choc +4 en 2018 ; vérité dans `mortalite_verite.csv`. portefeuille_vie.csv (20 000 contrats, fenêtre 2015–2019) : mortalité des assurés = 0,75 × population.
transactions_lab.csv (≈ 110 000 transactions, 3 000 comptes, 2024) : 2 % de comptes suspects : fractionnement (dépôts d'espèces de 9 000 à 9 900 € autour du seuil 10 000 €),
    relais (≥ 10 petits virements entrants puis sortie de ≈ 95 % vers Pays P11/P12 en 48 h), aller-retour circulaire entre 4 comptes, flux vers pays à risque ;
    + commerces légitimes à forts dépôts d'espèces (faux positifs difficiles). Étiquettes : `verite_lab.csv`.
takaful_fonds.csv (3 fonds × 15 ans) : cotisations, sinistres (ratio 72 / 80 / 76 %, bruit de 8 %), frais, rendement des placements (1–7 %), réserve d'ouverture.
"""
import os
import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def _caler(f, cible, lo=-12.0, hi=6.0):
    """cherche c tel que mean(f(c)) = cible (dichotomie)"""
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) < cible:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ----------------------------------------------------------------------------------------------- crédit
def credits_conso(n=40000, seed=5101):
    rng = np.random.default_rng(seed)
    age = np.clip(rng.normal(42, 12, n), 21, 75).round().astype(int)
    revenu = np.exp(rng.normal(np.log(32000), 0.45, n)).round(-1)
    emploi = np.minimum(rng.gamma(2.0, 4.0, n), age - 18).round(1)
    logement = rng.choice(["locataire", "proprietaire", "heberge"], n, p=[0.42, 0.38, 0.20])
    objet = rng.choice(["auto", "travaux", "conso"], n, p=[0.40, 0.25, 0.35])
    montant = np.clip(np.exp(rng.normal(9.0, 0.6, n)), 1000, 50000).round(-2)
    duree = rng.choice([12, 24, 36, 48, 60, 72], n, p=[0.08, 0.2, 0.3, 0.2, 0.14, 0.08])
    duree = np.where(montant > 20000, np.maximum(duree, 36), duree)
    mens_ratio = (montant / duree) / (revenu / 12)
    dti = np.clip(rng.beta(2, 6, n) * 0.7 + mens_ratio, 0.02, 1.2).round(3)
    incidents = rng.poisson(0.25 * (1 + (dti > 0.45)))
    relation = np.clip(rng.exponential(4.0, n), 0, 30).round(1)
    lin = (0.0012 * (age - 47) ** 2 - 0.12 * np.minimum(emploi, 10) + 1.5 * dti + 3 * np.maximum(0, dti - 0.5)
           + 0.55 * incidents + 0.35 * (logement == "locataire") + 0.5 * (logement == "heberge")
           + 0.25 * (objet == "conso") - 0.10 * (objet == "travaux") + 0.012 * duree
           - 0.5 * (np.log(revenu) - np.log(32000)) - 0.04 * np.minimum(relation, 15))
    lin = 1.3 * lin                                             # signal un peu plus net (AUC attendue ≈ 0,75)
    c = _caler(lambda c: _sig(c + lin).mean(), 0.06)
    pd_vraie = _sig(c + lin)
    defaut = (rng.random(n) < pd_vraie).astype(int)
    df = pd.DataFrame({"id_credit": np.arange(1, n + 1), "age": age, "revenu_annuel": revenu, "anciennete_emploi": emploi,
                       "logement": logement, "objet": objet, "montant": montant, "duree_mois": duree,
                       "taux_endettement": dti, "nb_incidents_12m": incidents, "anciennete_relation": relation})
    # manquants informatifs
    p_emp = np.clip(0.04 + 0.5 * pd_vraie, 0, 0.5)
    df.loc[rng.random(n) < p_emp, "anciennete_emploi"] = np.nan
    df.loc[rng.random(n) < 0.05, "revenu_annuel"] = np.nan
    df["defaut_12m"] = defaut
    return df


def recouvrements(n=6000, seed=5102):
    rng = np.random.default_rng(seed)
    garantie = rng.choice(["aucune", "caution", "nantissement"], n, p=[0.50, 0.30, 0.20])
    objet = rng.choice(["auto", "travaux", "conso"], n, p=[0.40, 0.25, 0.35])
    ead = np.clip(np.exp(rng.normal(8.9, 0.6, n)), 800, 45000).round(-1)
    mois = rng.integers(6, 60, n)
    mu = _sig(-0.2 + 1.0 * (garantie == "aucune") - 0.7 * (garantie == "caution") - 0.2 * (garantie == "nantissement")
              + 0.25 * (objet == "conso"))
    k = 2.2
    lgd = rng.beta(mu * k, (1 - mu) * k)
    lgd = np.where(rng.random(n) < 0.12, 0.0, lgd).round(4)
    delai = np.clip(rng.gamma(3.0, 6.0, n) + 6 * (garantie == "nantissement"), 1, 60).round().astype(int)
    return pd.DataFrame({"id_credit": np.arange(1, n + 1), "garantie": garantie, "objet": objet, "ead": ead,
                         "mois_depuis_origine": mois, "delai_recouvrement_mois": delai, "lgd_realisee": lgd})


def revolving_defauts(n=8000, seed=5103):
    rng = np.random.default_rng(seed)
    limite = np.clip(np.exp(rng.normal(8.3, 0.5, n)), 500, 20000).round(-2)
    util = rng.beta(2, 3, n)
    tirage = (util * limite).round(0)
    ccf = np.clip(rng.beta(2, 3, n) + 0.35 * (0.4 - util), 0, 1)
    ead = tirage + ccf * (limite - tirage)
    ccf_obs = np.where(limite - tirage > 1, (ead - tirage) / np.maximum(limite - tirage, 1), np.nan)
    return pd.DataFrame({"id_ligne": np.arange(1, n + 1), "limite": limite, "tirage_12m_avant": tirage,
                         "ead": ead.round(0), "ccf_observe": ccf_obs.round(4)})


def portefeuille_ifrs9(n=20000, seed=5104):
    rng = np.random.default_rng(seed)
    ead = np.clip(np.exp(rng.normal(9.3, 0.8, n)), 1000, 200000).round(-1)
    pd0 = np.clip(np.exp(rng.normal(np.log(0.02), 0.7, n)), 0.002, 0.35)
    pd1 = np.clip(pd0 * np.exp(rng.normal(0.15, 0.6, n)), 0.002, 0.95)
    u = rng.random(n)
    jr = np.zeros(n, dtype=int)
    m1 = (u > 0.91) & (u <= 0.94)
    m2 = (u > 0.94) & (u <= 0.976)
    m3 = u > 0.976
    jr[m1] = rng.integers(1, 30, m1.sum())
    jr[m2] = rng.integers(30, 90, m2.sum())
    jr[m3] = rng.integers(90, 400, m3.sum())
    mat = np.round(rng.uniform(0.5, 7.0, n), 1)
    lgd = np.round(rng.uniform(0.2, 0.6, n), 3)
    taux = np.round(rng.uniform(0.03, 0.08, n), 4)
    forb = (rng.random(n) < 0.02 + 0.05 * (jr > 0)).astype(int)
    return pd.DataFrame({"id_pret": np.arange(1, n + 1), "ead": ead, "pd_origine": pd0.round(5), "pd_actuelle": pd1.round(5),
                         "jours_retard": jr, "maturite_residuelle": mat, "lgd_estimee": lgd, "taux_effectif": taux,
                         "restructure": forb})


def matrice_vraie():
    """Matrice de transition annuelle vraie (7 notes + défaut) ; ligne = note de départ (1 = meilleure), colonne 8 = défaut. Lignes sommant à 1."""
    P = np.array([
        [0.915, 0.070, 0.010, 0.003, 0.001, 0.000, 0.000, 0.001],
        [0.040, 0.880, 0.060, 0.012, 0.004, 0.002, 0.001, 0.001],
        [0.005, 0.060, 0.860, 0.055, 0.012, 0.004, 0.002, 0.002],
        [0.002, 0.010, 0.070, 0.830, 0.062, 0.015, 0.006, 0.005],
        [0.001, 0.003, 0.012, 0.075, 0.800, 0.070, 0.022, 0.017],
        [0.000, 0.002, 0.004, 0.015, 0.080, 0.760, 0.080, 0.059],
        [0.000, 0.000, 0.002, 0.005, 0.020, 0.090, 0.600, 0.283]])
    return P / P.sum(axis=1, keepdims=True)


def notations_panel(n=5000, annees=10, seed=5105):
    rng = np.random.default_rng(seed)
    P = matrice_vraie()
    z = np.array([-0.3, -0.5, -0.3, 0.0, 0.4, 1.4, 1.3, 0.2, -0.4, -0.5])[:annees]
    init = np.array([0.05, 0.15, 0.28, 0.30, 0.14, 0.06, 0.02])
    note = rng.choice(np.arange(1, 8), n, p=init)
    actif = np.ones(n, bool)
    lignes = []
    for t in range(annees):
        fin = np.zeros(n, int)
        idx = np.where(actif)[0]
        for i_note in range(1, 8):
            m = idx[note[idx] == i_note]
            if len(m) == 0:
                continue
            p = P[i_note - 1].copy()
            # les baisses de note (colonnes > i_note) sont amplifiées par la macro
            for j in range(i_note, 8):
                p[j] *= np.exp(0.6 * z[t])
            for j in range(0, i_note - 1):
                p[j] *= np.exp(-0.3 * z[t])
            p = p / p.sum()
            fin[m] = rng.choice(np.arange(1, 9), len(m), p=p)
        sorti = actif & (fin < 8) & (rng.random(n) < 0.04)
        fin_obs = np.where(sorti, 0, fin)
        lignes.append(pd.DataFrame({"id_emprunteur": idx + 1, "annee": t, "note_debut": note[idx],
                                    "note_fin": fin_obs[idx]}))
        actif = actif & (fin_obs != 0) & (fin != 8)
        note = np.where(fin > 0, fin, note)
        note = np.where(note > 7, 7, note)
    return pd.concat(lignes, ignore_index=True)


def taux_defaut_macro(seed=5106, T=80):
    rng = np.random.default_rng(seed)
    g = np.zeros(T)
    for t in range(1, T):
        g[t] = 0.6 * g[t - 1] + rng.normal(0, 0.5)
    g[48:55] += np.array([-0.6, -1.5, -2.1, -1.8, -1.2, -0.6, -0.1])
    cho = np.zeros(T)
    for t in range(1, T):
        cho[t] = 0.85 * cho[t - 1] - 0.25 * g[t] + rng.normal(0, 0.15)
    immo = np.zeros(T)
    for t in range(1, T):
        immo[t] = 0.7 * immo[t - 1] + 0.3 * g[t - 1] + rng.normal(0, 0.5)
    immo[50:58] -= np.array([0.5, 1.5, 2.5, 3.0, 2.5, 1.5, 1.0, 0.5])
    z = lambda x: (x - x.mean()) / x.std()
    eta = -3.6 - 0.30 * z(g) + 0.20 * z(cho) - 0.12 * z(immo) + rng.normal(0, 0.06, T)
    taux = _sig(eta)
    annee = 2005 + np.arange(T) // 4
    trim = np.arange(T) % 4 + 1
    return pd.DataFrame({"trimestre": np.arange(1, T + 1), "annee": annee, "t": trim,
                         "croissance_pib": (1.5 + 0.8 * g).round(2), "chomage": (8.0 + 1.2 * cho).round(2),
                         "variation_immo": (1.0 + 1.5 * immo).round(2), "taux_defaut": taux.round(5)})


# ----------------------------------------------------------------------------------------------- assurance dommages
ZONES = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F"]
EFFET_ZONE = {"Zone A": -0.20, "Zone B": -0.10, "Zone C": 0.0, "Zone D": 0.08, "Zone E": 0.18, "Zone F": 0.30}


def polices_auto(n=100000, seed=5201):
    rng = np.random.default_rng(seed)
    annee = rng.choice([2022, 2023, 2024], n, p=[0.30, 0.33, 0.37])
    age = np.clip(rng.normal(46, 15, n), 18, 90).round().astype(int)
    av = np.clip(rng.gamma(2.2, 3.2, n), 0, 25).round(1)
    puiss = np.clip(rng.normal(5, 1.8, n), 1, 9).round().astype(int)
    zone = rng.choice(ZONES, n, p=[0.12, 0.20, 0.25, 0.20, 0.14, 0.09])
    bm = np.clip(np.where(age < 28, rng.normal(100, 12, n), rng.normal(78, 14, n)), 50, 150).round().astype(int)
    usage = rng.choice(["prive", "professionnel"], n, p=[0.86, 0.14])
    carb = rng.choice(["essence", "diesel", "hybride_electrique"], n, p=[0.48, 0.38, 0.14])
    expo = np.where(rng.random(n) < 0.72, 1.0, rng.uniform(0.05, 1.0, n)).round(3)
    permis = np.clip(age - 18 - rng.exponential(1.5, n), 0, None).round().astype(int)
    lin = (0.55 * (age < 25) + 0.15 * (age > 70) + 0.04 * puiss + np.array([EFFET_ZONE[z] for z in zone])
           + 0.006 * (bm - 100) + 0.10 * (usage == "professionnel") - 0.15 * (carb == "hybride_electrique")
           - 0.02 * np.minimum(av, 10))
    c = _caler(lambda c: (expo * np.exp(c + lin)).sum() / expo.sum(), 0.065)
    frail = rng.gamma(1 / 0.4, 0.4, n)                      # moyenne 1, variance 0,4
    lam = expo * np.exp(c + lin) * frail
    nb = rng.poisson(lam)
    df = pd.DataFrame({"id_police": np.arange(1, n + 1), "annee": annee, "exposition": expo, "age_conducteur": age,
                       "anciennete_permis": permis, "age_vehicule": av, "puissance": puiss, "zone": zone,
                       "bonus_malus": bm, "usage": usage, "carburant": carb, "nb_sinistres": nb})
    return df


def sinistres_auto(polices, seed=5202):
    rng = np.random.default_rng(seed)
    p = polices[polices["nb_sinistres"] > 0]
    rep = np.repeat(p.index.values, p["nb_sinistres"].values)
    q = polices.loc[rep].reset_index(drop=True)
    m = len(q)
    corporel = rng.random(m) < 0.10
    ez = np.array([EFFET_ZONE[z] for z in q["zone"]])
    moy_mat = 1900 * np.exp(0.05 * q["puissance"].values + ez / 2)
    mat = rng.gamma(2.5, moy_mat / 2.5)
    cor = np.exp(rng.normal(9.0, 1.6, m))
    queue = rng.random(m) < 0.08
    pareto = 100000 * (1 - rng.random(m)) ** (-1 / 1.8)
    cor = np.where(queue, pareto, cor)
    infl = 1.04 ** (q["annee"].values - 2022)
    montant = np.where(corporel, cor, mat) * infl
    return pd.DataFrame({"id_sinistre": np.arange(1, m + 1), "id_police": q["id_police"].values, "annee": q["annee"].values,
                         "type": np.where(corporel, "corporel", "materiel"), "montant": montant.round(0)})


PROFIL_RC = np.array([0.12, 0.30, 0.48, 0.62, 0.74, 0.83, 0.90, 0.94, 0.97, 0.985, 0.993, 0.997, 1.0])
PROFIL_DOM = np.array([0.55, 0.88, 0.96, 0.99, 0.998, 1.0])


def _triangle(profil, lr, infl, choc, seed, n_ay=10, phi=20000.0, prime0=60e6, croissance=0.04):
    rng = np.random.default_rng(seed)
    nd = len(profil)
    inc = np.diff(np.concatenate([[0], profil]))
    ay = 2015 + np.arange(n_ay)
    prime = prime0 * (1 + croissance) ** np.arange(n_ay)
    lr_ay = lr * np.exp(rng.normal(0, 0.05, n_ay))
    carre = np.zeros((n_ay, nd))
    for i in range(n_ay):
        for j in range(nd):
            cal = i + j
            moy = prime[i] * lr_ay[i] * inc[j] * (1 + infl) ** cal
            if choc and cal == 7:          # diagonale 2022
                moy *= 1 + choc
            carre[i, j] = phi * rng.poisson(moy / phi)
    return ay, prime, carre


def triangles(seed=5203):
    out = {}
    for nom, profil, lr, infl, choc, s in [("rc", PROFIL_RC, 0.78, 0.02, 0.0, seed), ("dommages", PROFIL_DOM, 0.62, 0.0, 0.0, seed + 1),
                                           ("choc", PROFIL_RC, 0.78, 0.02, 0.12, seed + 2)]:
        ay, prime, carre = _triangle(profil, lr, infl, choc, s)
        n_ay, nd = carre.shape
        obs, ver = [], []
        for i in range(n_ay):
            for j in range(nd):
                ver.append((int(ay[i]), j, carre[i, j], prime[i]))
                if i + j <= n_ay - 1:
                    obs.append((int(ay[i]), j, carre[i, j], prime[i]))
        cols = ["annee_survenance", "delai", "paiement_incremental", "prime_acquise"]
        o = pd.DataFrame(obs, columns=cols)
        o["paiement_cumule"] = o.groupby("annee_survenance")["paiement_incremental"].cumsum()
        v = pd.DataFrame(ver, columns=cols)
        v["paiement_cumule"] = v.groupby("annee_survenance")["paiement_incremental"].cumsum()
        out[nom] = (o.round(0), v.round(0))
    return out


def sante_assures(n_membres=16000, seed=5204):
    rng = np.random.default_rng(seed)
    age0 = np.clip(rng.gamma(6, 7.5, n_membres), 0, 95)
    age0 = np.clip(age0, 0, 90).astype(int)
    sexe = rng.choice(["F", "M"], n_membres, p=[0.52, 0.48])
    ald = rng.random(n_membres) < np.clip(0.02 + 0.0035 * age0, 0, 0.35)
    p_niv = np.column_stack([np.where(ald, 0.25, 0.50), np.full(n_membres, 0.35), np.where(ald, 0.40, 0.15)])
    p_niv = p_niv / p_niv.sum(axis=1, keepdims=True)
    cum = p_niv.cumsum(axis=1)
    u = rng.random(n_membres)[:, None]
    niv = (u > cum).sum(axis=1)
    niveau = np.array(["basique", "confort", "premium"])[niv]
    zone = rng.choice(ZONES, n_membres)
    lignes = []
    for a in (2022, 2023, 2024):
        present = rng.random(n_membres) < (0.85 if a == 2022 else 0.8)
        idx = np.where(present)[0]
        k = len(idx)
        expo = np.where(rng.random(k) < 0.8, 1.0, rng.uniform(0.15, 1.0, k)).round(2)
        age = age0[idx] + (a - 2022)
        al = ald[idx].astype(float)
        mh = np.array([1.0, 1.15, 1.35])[niv[idx]]
        lam_c = expo * (2.2 + 0.07 * age + 7.0 * al) * mh
        nc = rng.poisson(lam_c)
        cout_c = rng.gamma(4.0, 40 * 1.03 ** (a - 2022) / 4.0, k) * nc
        lam_h = expo * (0.03 + 0.0014 * age + 0.30 * al) * mh * 1.0
        nh = rng.poisson(lam_h)
        cout_h = np.array([np.exp(rng.normal(8.1, 0.9, c)).sum() if c > 0 else 0.0 for c in nh]) * 1.03 ** (a - 2022)
        cout_ph = rng.gamma(0.8, 80 * (1 + 0.025 * age + 2.2 * al) * expo, k)
        dent = (rng.random(k) < 0.35 * np.array([0.6, 1.0, 1.5])[niv[idx]]) * rng.gamma(3.0, 90.0 * mh, k)
        tot = cout_c + cout_h + cout_ph + dent
        lignes.append(pd.DataFrame({"id_assure": idx + 1, "annee": a, "age": age, "sexe": sexe[idx], "niveau": niveau[idx],
                                    "ald": ald[idx].astype(int), "zone": zone[idx], "exposition": expo,
                                    "nb_consultations": nc, "nb_hospitalisations": nh, "cout_consultations": cout_c.round(2),
                                    "cout_hospitalisation": cout_h.round(2), "cout_pharmacie": cout_ph.round(2),
                                    "cout_dentaire": dent.round(2), "cout_total": tot.round(2)}))
    return pd.concat(lignes, ignore_index=True)


# ----------------------------------------------------------------------------------------------- marchés
ACTIFS = ["actions_A", "actions_B", "obligations", "immobilier", "matieres"]


def rendements_marche(T=4000, seed=5301):
    rng = np.random.default_rng(seed)
    sig_inc = np.array([0.011, 0.013, 0.0025, 0.007, 0.015])
    corr_calme = np.array([[1, .60, -.15, .45, .25], [.60, 1, -.15, .45, .25], [-.15, -.15, 1, -.05, -.05],
                           [.45, .45, -.05, 1, .20], [.25, .25, -.05, .20, 1]])
    corr_stress = np.array([[1, .90, .00, .85, .50], [.90, 1, .00, .85, .50], [.00, .00, 1, .00, .00],
                            [.85, .85, .00, 1, .45], [.50, .50, .00, .45, 1]])
    Lc, Ls = np.linalg.cholesky(corr_calme), np.linalg.cholesky(corr_stress)
    alpha, beta = 0.08, 0.90
    omega = 1 - alpha - beta                                   # variance relative moyenne = 1
    regime = np.zeros(T, int)
    for t in range(1, T):
        sortie = 0.03 if regime[t - 1] == 1 else 0.004         # stress : durée moyenne ≈ 33 jours
        regime[t] = 1 - regime[t - 1] if rng.random() < sortie else regime[t - 1]
    h = np.ones(5)
    z_prev = np.zeros(5)
    nu = 5
    R = np.zeros((T, 5))
    for t in range(T):
        h = omega + alpha * h * z_prev ** 2 + beta * h
        z = rng.standard_t(nu, 5) / np.sqrt(nu / (nu - 2))
        zc = (Ls if regime[t] else Lc) @ z
        z_prev = zc
        vol_mult = 2.0 if regime[t] else 1.0
        R[t] = sig_inc * vol_mult * np.sqrt(h) * zc + np.array([0.0004, 0.0004, 0.0001, 0.0002, 0.0001])
    dates = pd.bdate_range("2010-01-04", periods=T)
    df = pd.DataFrame(R.round(6), columns=ACTIFS)
    df.insert(0, "date", dates.strftime("%Y-%m-%d"))
    ver = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "regime": np.where(regime == 1, "stress", "calme")})
    return df, ver


def courbe_taux(T=120, seed=5302):
    rng = np.random.default_rng(seed)
    mats = np.array([0.25, 1, 2, 3, 5, 7, 10, 20, 30])
    niv = np.zeros(T); pen = np.zeros(T); cou = np.zeros(T)
    niv[0], pen[0], cou[0] = 0.025, -0.012, 0.005
    for t in range(1, T):
        cible = 0.025 + (0.025 if 60 <= t < 90 else 0.0)
        niv[t] = niv[t - 1] + 0.05 * (cible - niv[t - 1]) + rng.normal(0, 0.0012)
        pen[t] = 0.92 * pen[t - 1] + rng.normal(0, 0.0015) + (-0.0006 if 60 <= t < 90 else 0.0)
        cou[t] = 0.9 * cou[t - 1] + rng.normal(0, 0.002)
    lam = 0.45
    f1 = (1 - np.exp(-lam * mats)) / (lam * mats)
    f2 = f1 - np.exp(-lam * mats)
    Y = niv[:, None] + pen[:, None] * f1[None, :] + cou[:, None] * f2[None, :]
    cols = [f"taux_{str(m).replace('.', '_')}a" for m in mats]
    df = pd.DataFrame(Y.round(5), columns=cols)
    df.insert(0, "mois", np.arange(1, T + 1))
    return df


def pertes_operationnelles(seed=5303):
    rng = np.random.default_rng(seed)
    lignes = []
    cats = ["fraude_interne", "fraude_externe", "erreur_traitement", "panne_systeme", "pratiques_commerciales"]
    pc = np.array([0.04, 0.22, 0.46, 0.18, 0.10])
    mu = {"fraude_interne": 8.6, "fraude_externe": 7.9, "erreur_traitement": 7.4, "panne_systeme": 7.9, "pratiques_commerciales": 8.4}
    lm = ["banque_detail", "assurance", "gestion_actifs", "paiements"]
    for a in range(2015, 2025):
        lam = 150 * 1.04 ** (a - 2015)
        n = rng.poisson(lam)
        cat = rng.choice(cats, n, p=pc)
        corps = np.exp(rng.normal([mu[c] for c in cat], 1.3))
        xi, sc = 0.7, 80000.0
        queue = rng.random(n) < 0.03
        gpd = 100000 + sc / xi * ((1 - rng.random(n)) ** (-xi) - 1)
        perte = np.where(queue, gpd, corps)
        recup = np.where(rng.random(n) < 0.25, perte * rng.uniform(0.1, 0.6, n), 0.0)
        jours = rng.integers(0, 365, n)
        date = pd.to_datetime(f"{a}-01-01") + pd.to_timedelta(jours, unit="D")
        lignes.append(pd.DataFrame({"date_evenement": date.strftime("%Y-%m-%d"), "categorie": cat,
                                    "ligne_metier": rng.choice(lm, n), "perte_brute": perte.round(0),
                                    "recuperation": recup.round(0), "perte_nette": (perte - recup).round(0)}))
    return pd.concat(lignes, ignore_index=True).sort_values("date_evenement").reset_index(drop=True)


def sinistres_gros(seed=5304):
    rng = np.random.default_rng(seed)
    lignes = []
    for a in range(2010, 2025):
        n = rng.poisson(160 * 1.03 ** (a - 2010))
        corps = np.exp(rng.normal(10.2, 1.5, n))
        xi, sc = 0.55, 300000.0
        queue = rng.random(n) < 0.04
        gpd = 500000 + sc / xi * ((1 - rng.random(n)) ** (-xi) - 1)
        lignes.append(pd.DataFrame({"annee_survenance": a, "montant": np.where(queue, gpd, corps).round(0)}))
    return pd.concat(lignes, ignore_index=True)


def cat_annuel(seed=5305, n=40):
    rng = np.random.default_rng(seed)
    ev = rng.random(n) >= 0.55
    m = 2e6 * (1 - rng.random(n)) ** (-0.9)
    return pd.DataFrame({"annee": 1985 + np.arange(n), "perte_cat": np.where(ev, m, 0.0).round(0)})


# ----------------------------------------------------------------------------------------------- vie
def _ax_bx_kt(seed=5401):
    rng = np.random.default_rng(seed)
    ages = np.arange(100)
    years = np.arange(1980, 2020)
    ax = {}
    for s, k in (("F", 1.0), ("M", 1.35)):
        m = k * (0.0035 * np.exp(-1.2 * ages) + 0.0003 + 0.00004 * np.exp(0.1 * ages))
        m = np.minimum(m, 0.6)
        ax[s] = np.log(m)
    bx = np.exp(-(((ages - 35) / 40.0) ** 2)) + 0.2
    bx = bx / bx.sum()
    kt = np.zeros(len(years))
    for t in range(1, len(years)):
        kt[t] = kt[t - 1] - 1.2 + rng.normal(0, 1.0)
    kt[years == 2018] += 4.0
    kt = kt - kt.mean()
    return ages, years, ax, bx, kt


def mortalite():
    ages, years, ax, bx, kt = _ax_bx_kt()
    rng = np.random.default_rng(5402)
    lignes = []
    verite = []
    for s in ("F", "M"):
        k = kt * (1.0 if s == "F" else 1.1)
        for ti, a in enumerate(years):
            m = np.exp(ax[s] + bx * k[ti])
            m = np.minimum(m, 0.9)
            expo = 100000 * np.exp(-0.022 * ages) * (1 + 0.1 * np.sin(ages / 10.0)) * (0.5 + 0.5 * (a - 1980) / 40)
            expo = np.where(ages > 90, expo * 0.6, expo)
            d = rng.poisson(expo * m)
            lignes.append(pd.DataFrame({"annee": a, "age": ages, "sexe": s, "exposition": expo.round(1), "deces": d}))
        verite.append(pd.DataFrame({"sexe": s, "age": ages, "ax": ax[s].round(5), "bx": bx.round(6)}))
    kt_df = pd.DataFrame({"annee": years, "kt_F": kt.round(4), "kt_M": (kt * 1.1).round(4)})
    return pd.concat(lignes, ignore_index=True), pd.concat(verite, ignore_index=True), kt_df


def portefeuille_vie(n=20000, seed=5403):
    ages, years, ax, bx, kt = _ax_bx_kt()
    rng = np.random.default_rng(seed)
    sexe = rng.choice(["F", "M"], n, p=[0.45, 0.55])
    age_em = rng.integers(25, 66, n)
    annee_em = rng.integers(2005, 2020, n)
    contrat = rng.choice(["temporaire_10", "temporaire_20", "vie_entiere"], n, p=[0.30, 0.35, 0.35])
    capital = (np.round(np.exp(rng.normal(11.3, 0.6, n)), -3)).clip(20000, 400000)
    vivant = np.ones(n, bool)
    expo = np.zeros(n)
    deces = np.zeros(n, int)
    for yi, a in enumerate(range(2015, 2020)):
        tk = np.where(years == a)[0][0]
        en_vigueur = vivant & (annee_em <= a)
        age = np.clip(age_em + (a - annee_em), 0, 99)
        m = np.empty(n)
        for s, k in (("F", 1.0), ("M", 1.1)):
            mm = np.exp(ax[s] + bx * kt[tk] * k)
            m[sexe == s] = mm[age[sexe == s]]
        q = 1 - np.exp(-0.75 * m)
        d = en_vigueur & (rng.random(n) < q)
        expo += np.where(en_vigueur, np.where(d, 0.5, 1.0), 0.0)
        deces += d.astype(int)
        vivant = vivant & ~d
    df = pd.DataFrame({"id_contrat": np.arange(1, n + 1), "sexe": sexe, "age_emission": age_em, "annee_emission": annee_em,
                       "contrat": contrat, "capital": capital, "exposition_2015_2019": expo, "deces": deces})
    return df[df["exposition_2015_2019"] > 0].reset_index(drop=True)


# ----------------------------------------------------------------------------------------------- LAB
def lab(n_comptes=3000, seed=5501):
    rng = np.random.default_rng(seed)
    pays = [f"Pays P{i}" for i in range(1, 13)]
    risque_pays = {p: (p in ("Pays P11", "Pays P12")) for p in pays}
    profil = rng.choice(["particulier", "commerce", "association"], n_comptes, p=[0.80, 0.17, 0.03])
    comptes = pd.DataFrame({"id_compte": np.arange(1, n_comptes + 1), "profil": profil,
                            "anciennete_ans": np.round(rng.exponential(5.0, n_comptes), 1),
                            "pays_residence": rng.choice(pays[:10], n_comptes, p=np.r_[[0.7], np.full(9, 0.3 / 9)])})
    rows = []
    jour0 = pd.Timestamp("2024-01-01")
    tid = 0

    def ajoute(compte, jour, sens, typ, montant, contre, pays_c):
        rows.append((compte, jour, sens, typ, round(float(montant), 2), contre, pays_c))

    for c in range(1, n_comptes + 1):
        p = profil[c - 1]
        k = rng.poisson({"particulier": 24, "commerce": 90, "association": 40}[p])
        jours = rng.integers(0, 366, k)
        for j in jours:
            typ = rng.choice(["virement", "especes", "carte"], p=[0.30, 0.10, 0.60] if p != "commerce" else [0.25, 0.30, 0.45])
            sens = "debit" if rng.random() < (0.7 if p == "particulier" else 0.45) else "credit"
            mu = {"particulier": 4.6, "commerce": 6.0, "association": 5.3}[p]
            m = float(np.clip(np.exp(rng.normal(mu, 0.9)), 3, 9000 if typ != "especes" or p == "commerce" else 3000))
            contre = int(rng.integers(1, n_comptes + 1)) if typ == "virement" else -1
            ajoute(c, int(j), sens, typ, m, contre, "Pays P1" if rng.random() < 0.9 else rng.choice(pays[:10]))
    # commerces à forts dépôts d'espèces (faux positifs difficiles)
    comm = np.where(profil == "commerce")[0] + 1
    for c in rng.choice(comm, 40, replace=False):
        for j in rng.integers(0, 366, 60):
            ajoute(c, j, "credit", "especes", rng.uniform(5000, 9990), -1, "Pays P1")
    # schémas suspects
    n_susp = int(0.02 * n_comptes)
    susp = rng.choice(np.setdiff1d(np.arange(1, n_comptes + 1), comm[:0]), n_susp, replace=False)
    schema = {}
    groupes = np.array_split(susp, 4)
    for c in groupes[0]:                      # fractionnement
        schema[c] = "fractionnement"
        j0 = int(rng.integers(0, 340))
        for _ in range(rng.integers(8, 16)):
            ajoute(c, j0 + int(rng.integers(0, 14)), "credit", "especes", rng.uniform(9000, 9900), -1, "Pays P1")
    for c in groupes[1]:                      # relais
        schema[c] = "relais"
        j0 = int(rng.integers(0, 340))
        tot = 0.0
        for _ in range(rng.integers(10, 20)):
            m = rng.uniform(300, 1500)
            tot += m
            ajoute(c, j0 + int(rng.integers(0, 3)), "credit", "virement", m, int(rng.integers(1, n_comptes + 1)), "Pays P1")
        ajoute(c, j0 + 3, "debit", "virement", 0.95 * tot, -2, str(rng.choice(["Pays P11", "Pays P12"])))
    anneau = groupes[2]
    for i0 in range(0, len(anneau) - len(anneau) % 4, 4):  # aller-retour circulaire
        g = anneau[i0:i0 + 4]
        for c in g:
            schema[c] = "aller_retour"
        m0 = rng.uniform(4000, 8000)
        j0 = int(rng.integers(0, 330))
        for r in range(rng.integers(3, 6)):
            for a, b in zip(g, np.roll(g, -1)):
                m = m0 * rng.uniform(0.97, 1.0)
                ajoute(a, j0 + r * 2, "debit", "virement", m, int(b), "Pays P1")
                ajoute(b, j0 + r * 2, "credit", "virement", m, int(a), "Pays P1")
    for c in groupes[3]:                      # pays à risque
        schema[c] = "pays_a_risque"
        for _ in range(rng.integers(6, 14)):
            ajoute(c, int(rng.integers(0, 366)), "debit", "virement", rng.uniform(2000, 9000), -2,
                   str(rng.choice(["Pays P11", "Pays P12"])))
    tx = pd.DataFrame(rows, columns=["id_compte", "jour", "sens", "type", "montant", "contrepartie", "pays_contrepartie"])
    tx["date"] = (jour0 + pd.to_timedelta(tx["jour"], unit="D")).dt.strftime("%Y-%m-%d")
    tx = tx.sort_values(["date", "id_compte"]).reset_index(drop=True)
    tx.insert(0, "id_transaction", np.arange(1, len(tx) + 1))
    tx = tx[["id_transaction", "date", "id_compte", "sens", "type", "montant", "contrepartie", "pays_contrepartie"]]
    verite = pd.DataFrame({"id_compte": comptes["id_compte"],
                           "schema": [schema.get(c, "aucun") for c in comptes["id_compte"]]})
    verite["suspect"] = (verite["schema"] != "aucun").astype(int)
    return comptes, tx, verite


def takaful_fonds(seed=5601):
    rng = np.random.default_rng(seed)
    lignes = []
    for fonds, prime0, lr in (("famille", 20e6, 0.72), ("auto", 35e6, 0.80), ("sante", 28e6, 0.76)):
        reserve = 0.0
        for a in range(2010, 2025):
            cot = prime0 * 1.05 ** (a - 2010)
            sin = cot * lr * np.exp(rng.normal(0, 0.08))
            frais = cot * 0.10
            rend = rng.uniform(0.01, 0.07)
            lignes.append((fonds, a, round(cot), round(sin), round(frais), round(rend, 4), round(reserve)))
            reserve += (cot - sin - frais) + reserve * rend      # avant toute distribution d'excédent
    return pd.DataFrame(lignes, columns=["fonds", "annee", "cotisations", "sinistres", "frais_gestion", "rendement", "reserve_ouverture"])


# ----------------------------------------------------------------------------------------------- écriture
def generer(dossier=DONNEES):
    os.makedirs(dossier, exist_ok=True)

    def ecrire(df, nom):
        df.to_csv(os.path.join(dossier, nom), index=False)
        print(f"{nom:34s} {len(df):>8d} lignes")

    ecrire(credits_conso(), "credits_conso.csv")
    ecrire(recouvrements(), "recouvrements.csv")
    ecrire(revolving_defauts(), "revolving_defauts.csv")
    ecrire(portefeuille_ifrs9(), "portefeuille_ifrs9.csv")
    ecrire(notations_panel(), "notations_panel.csv")
    ecrire(taux_defaut_macro(), "taux_defaut_macro.csv")
    pol = polices_auto()
    ecrire(pol, "polices_auto.csv")
    ecrire(sinistres_auto(pol), "sinistres_auto.csv")
    for nom, (o, v) in triangles().items():
        ecrire(o, f"triangle_{nom}.csv")
        ecrire(v, f"triangle_{nom}_verite.csv")
    ecrire(sante_assures(), "sante_assures.csv")
    r, ver = rendements_marche()
    ecrire(r, "rendements_marche.csv")
    ecrire(ver, "marche_verite.csv")
    ecrire(courbe_taux(), "courbe_taux.csv")
    ecrire(pertes_operationnelles(), "pertes_operationnelles.csv")
    ecrire(sinistres_gros(), "sinistres_gros.csv")
    ecrire(cat_annuel(), "cat_annuel.csv")
    mort, ver_m, kt = mortalite()
    ecrire(mort, "mortalite_population.csv")
    ecrire(ver_m, "mortalite_verite.csv")
    ecrire(kt, "mortalite_kt_vrai.csv")
    ecrire(portefeuille_vie(), "portefeuille_vie.csv")
    c, t, v = lab()
    ecrire(c, "comptes_lab.csv")
    ecrire(t, "transactions_lab.csv")
    ecrire(v, "verite_lab.csv")
    ecrire(takaful_fonds(), "takaful_fonds.csv")


if __name__ == "__main__":
    generer()
