"""Outils du chapitre 12 (RH) : chargement du panel collaborateur-année, intervalles de Poisson, durées pour Kaplan-Meier."""
import os
import numpy as np
import pandas as pd
from scipy import stats

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


def charger():
    ea = pd.read_csv(os.path.join(D, "employes_annees.csv"))
    dep = pd.read_csv(os.path.join(D, "departs.csv"), parse_dates=["date_depart"])
    emp = pd.read_csv(os.path.join(D, "employes.csv"))
    med = ea.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    ea["compa_ratio"] = ea["salaire_brut_mensuel"] / med
    ea = ea.sort_values(["id_employe", "annee"]).reset_index(drop=True)
    ea["promo_3ans"] = ea.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max()).astype(int)
    return ea, dep, emp


def poisson_ic(k, exposition, alpha=0.05):
    """taux par unité d'exposition (k événements) et intervalle exact (Garwood)"""
    bas = stats.chi2.ppf(alpha / 2, 2 * k) / 2 if k > 0 else 0.0
    haut = stats.chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / 2
    return k / exposition, bas / exposition, haut / exposition


def durees(ea, dep):
    """une ligne par collaborateur : ancienneté à l'entrée dans l'observation, ancienneté à la sortie, événement (départ)"""
    g = ea.groupby("id_employe")
    entree = g["anciennete"].first()
    derniere = g["anciennete"].last()
    annee_der = g["annee"].last()
    ev = g["depart_dans_l_annee"].last()
    d = dep.set_index("id_employe")["date_depart"]
    fin = derniere + 1.0
    for i in ev[ev == 1].index:
        debut_annee = pd.Timestamp(f"{int(annee_der[i])}-01-01")
        fin[i] = derniere[i] + (d[i] - debut_annee).days / 365.25
    return pd.DataFrame({"entree": entree, "fin": fin, "depart": ev})
