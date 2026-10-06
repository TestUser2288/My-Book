"""Outils du chapitre 4 (cadre réglementaire) : formules IRB, agrégation du SCR, partage de l'excédent Takaful, variables LAB.

Partagé par les blocs cachés du livre (sections/04-*.md) et par le cahier (cahier/04-exercices.md).
Tout est volontairement court et lisible : ce sont des **illustrations pédagogiques** des formules, pas des moteurs réglementaires.
"""
import os

import numpy as np
import pandas as pd
from scipy.stats import norm

DONNEES = os.environ.get("DONNEES", "donnees")
SEUIL_ESPECES = 10000.0          # seuil d'exemple (illustratif) pour les dépôts d'espèces


def charger(nom):
    return pd.read_csv(os.path.join(DONNEES, nom))


# ----------------------------------------------------------------------------------- Bâle : formule IRB
def rho_detail_autre(pd_):
    """Corrélation d'actifs « autres expositions de détail » (formule de principe : 3 % à 16 % selon la PD)."""
    w = (1 - np.exp(-35 * pd_)) / (1 - np.exp(-35))
    return 0.03 * w + 0.16 * (1 - w)


def rho_entreprise(pd_):
    """Corrélation d'actifs « entreprises » (12 % à 24 % selon la PD)."""
    w = (1 - np.exp(-50 * pd_)) / (1 - np.exp(-50))
    return 0.12 * w + 0.24 * (1 - w)


def k_vasicek(pd_, lgd, rho, q=0.999):
    """Capital par unité d'exposition : perte au quantile q (modèle à un facteur) moins perte attendue."""
    pd_ = np.asarray(pd_, float)
    pd_cond = norm.cdf((norm.ppf(pd_) + np.sqrt(rho) * norm.ppf(q)) / np.sqrt(1 - rho))
    return lgd * (pd_cond - pd_)


def k_detail(pd_, lgd, pd_plancher=0.0003):
    """Détail « autres expositions » : corrélation selon la PD, pas d'ajustement d'échéance."""
    p = np.maximum(np.asarray(pd_, float), pd_plancher)
    return k_vasicek(p, lgd, rho_detail_autre(p))


def k_entreprise(pd_, lgd, echeance=2.5, pd_plancher=0.0003):
    """Entreprises : même structure + ajustement d'échéance (b dépend de la PD)."""
    p = np.maximum(np.asarray(pd_, float), pd_plancher)
    b = (0.11852 - 0.05478 * np.log(p)) ** 2
    return k_vasicek(p, lgd, rho_entreprise(p)) * (1 + (echeance - 2.5) * b) / (1 - 1.5 * b)


def perte_portefeuille_vasicek(pd_, rho, n_prets, n_scenarios, seed=0):
    """Taux de perte (LGD=1) d'un portefeuille homogène : un facteur systématique Z, défauts conditionnellement binomiaux."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_scenarios)
    pd_cond = norm.cdf((norm.ppf(pd_) - np.sqrt(rho) * z) / np.sqrt(1 - rho))
    return rng.binomial(n_prets, pd_cond) / n_prets


# ----------------------------------------------------------------------------------- Solvabilité : agrégation
def agreger(charges, corr):
    """SCR de base = racine de la forme quadratique c' R c (diversification entre modules)."""
    c = np.asarray(charges, float)
    return float(np.sqrt(c @ np.asarray(corr, float) @ c))


# ----------------------------------------------------------------------------------- Takaful : partage de l'excédent
def exercice_takaful(f, modele, dette=0.0, wakala=0.20, part_mudaraba=0.30, part_participants=0.70):
    """Une année du fonds des participants (cotisations, sinistres, rendement, réserve d'ouverture, frais de gestion réels).

    modele : 'wakala' (l'opérateur reçoit un % des cotisations et supporte ses frais),
             'moudaraba' (il reçoit une part du profit des placements, rien d'autre),
             'hybride' (frais d'agence + part du profit des placements).
    Le déficit est couvert par un prêt sans intérêt de l'opérateur (qard hassan), remboursé sur les excédents suivants ;
    l'excédent restant est distribué pour une part aux participants, le reste va en réserve.
    """
    cot, sin, rend, res = f["cotisations"], f["sinistres"], f["rendement"], f["reserve_ouverture"]
    placements = max(res, 0.0) * rend
    frais = wakala * cot if modele in ("wakala", "hybride") else 0.0
    part_op = part_mudaraba * placements if modele in ("moudaraba", "hybride") else 0.0
    excedent = cot - sin - frais + placements - part_op
    avant = res + excedent
    qard_nouveau = max(-avant, 0.0)                    # la réserve ne peut pas être négative : l'opérateur prête la différence
    remb = min(max(excedent, 0.0), dette)              # un excédent rembourse d'abord le prêt
    distribuable = max(excedent, 0.0) - remb
    distribue = part_participants * distribuable
    reserve_fin = max(avant, 0.0) - remb - distribue
    return {"frais_agence": frais, "placements": placements, "part_op_placements": part_op, "excedent": excedent,
            "qard_nouveau": qard_nouveau, "remboursement": remb, "distribue": distribue, "reserve_fin": reserve_fin,
            "dette_fin": dette + qard_nouveau - remb,
            "resultat_operateur": frais + part_op - f["frais_gestion"]}


def simuler_fonds(df, modele, **kw):
    """Fait tourner les années d'un fonds dans l'ordre : la réserve et la dette d'ouverture viennent de l'année précédente."""
    res, dette, lignes = 0.0, 0.0, []
    for _, f in df.sort_values("annee").iterrows():
        g = f.copy()
        g["reserve_ouverture"] = res
        r = exercice_takaful(g, modele, dette=dette, **kw)
        res, dette = r["reserve_fin"], r["dette_fin"]
        lignes.append({"annee": int(f["annee"]), **r})
    return pd.DataFrame(lignes)


# ----------------------------------------------------------------------------------- LAB : variables par compte
def variables_comptes(tx, comptes):
    """Une ligne par compte : volumes, dépôts d'espèces juste sous le seuil, rafales de virements entrants, flux vers pays à risque."""
    t = tx.copy()
    t["date"] = pd.to_datetime(t["date"])
    t["jour"] = (t["date"] - t["date"].min()).dt.days
    t["credit"] = (t["sens"] == "credit")
    g = t.groupby("id_compte")
    F = pd.DataFrame({"n_tx": g.size(), "montant_total": g["montant"].sum()})
    esp_c = t[(t["type"] == "especes") & t["credit"]]
    sous = esp_c[(esp_c["montant"] >= 0.9 * SEUIL_ESPECES) & (esp_c["montant"] < SEUIL_ESPECES)]
    F["n_depots_sous_seuil"] = sous.groupby("id_compte").size()
    # nombre maximal de dépôts sous le seuil dans une fenêtre glissante de 14 jours
    F["max_depots_sous_seuil_14j"] = sous.groupby("id_compte")["jour"].apply(lambda s: max_fenetre(np.sort(s.values), 14))
    vin = t[(t["type"] == "virement") & t["credit"]]
    F["max_virements_entrants_3j"] = vin.groupby("id_compte")["jour"].apply(lambda s: max_fenetre(np.sort(s.values), 3))
    risque = t[t["pays_contrepartie"].isin(["Pays P11", "Pays P12"]) & (t["sens"] == "debit")]
    F["n_sorties_pays_risque"] = risque.groupby("id_compte").size()
    F["montant_pays_risque"] = risque.groupby("id_compte")["montant"].sum()
    F = F.fillna(0.0)
    entrants = t[t["credit"]].groupby("id_compte")["montant"].sum().reindex(F.index).fillna(0.0)
    F["part_sortie_risque"] = np.where(entrants > 0, F["montant_pays_risque"] / entrants.replace(0, np.nan), 0.0)
    F["part_sortie_risque"] = F["part_sortie_risque"].fillna(0.0).clip(0, 5)
    F = F.reset_index().merge(comptes[["id_compte", "profil"]], on="id_compte", how="right").fillna(0.0)
    return F


def max_fenetre(jours, largeur):
    """plus grand nombre de dates (triées) tenant dans une fenêtre de `largeur` jours"""
    if len(jours) == 0:
        return 0
    j, best = 0, 0
    for i in range(len(jours)):
        while jours[i] - jours[j] > largeur:
            j += 1
        best = max(best, i - j + 1)
    return best
