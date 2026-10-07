"""Outils du chapitre 11 (opérations et chaîne logistique) : chargement, intervalles, délais reconstitués, rejeu de la politique de stock, figures."""
import os
import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


def charger():
    liv = pd.read_csv(os.path.join(D, "livraisons.csv"), parse_dates=["date_commande", "date_expedition", "date_livraison"])
    liv = liv[liv["mode_livraison"] != "Retrait magasin"].copy()
    liv["preparation"] = (liv["date_expedition"] - liv["date_commande"]).dt.days
    liv["transport"] = (liv["date_livraison"] - liv["date_expedition"]).dt.days
    liv["total"] = (liv["date_livraison"] - liv["date_commande"]).dt.days
    liv["mois"] = liv["date_commande"].dt.month
    liv["annee"] = liv["date_commande"].dt.year
    rea = pd.read_csv(os.path.join(D, "reappro_fournisseur.csv"), parse_dates=["date_commande"])
    rea["ecart_j"] = rea["delai_reel_j"] - rea["delai_promis_j"]
    rea["en_retard"] = (rea["ecart_j"] > 0).astype(int)
    rea["taux_service"] = rea["quantite_recue"] / rea["quantite_commandee"]
    stk = pd.read_csv(os.path.join(D, "stock_quotidien.csv"), parse_dates=["date"])
    prod = pd.read_csv(os.path.join(D, "produits.csv"))
    return liv, rea, stk, prod


def wilson(k, n, z=1.96):
    """intervalle de Wilson d'une proportion k/n"""
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, c - h, c + h


def delais_reconstitues(stk):
    """délai de réapprovisionnement : jours entre le franchissement du point de commande et l'arrivée (hausse brutale du stock)"""
    L = []
    for _, g in stk.groupby("id_produit"):
        s, pc = g["stock_fin_jour"].values, g["point_de_commande"].iloc[0]
        arr = np.where(np.diff(s) > 5)[0] + 1
        prev = 0
        for a in arr:
            seg = np.where(s[prev:a] <= pc)[0]
            if len(seg):
                L.append(a - (prev + seg[0]))
            prev = a
    return np.array(L)


def rejouer(stk, rop_par_produit, qte_par_produit, delais, graine=7, n_rep=20):
    """rejoue la demande de chaque produit avec une politique (point de commande, quantité) ; délais tirés dans `delais`.
    Retourne (taux de jours en rupture, stock moyen en jours de demande, nombre de commandes par an)."""
    rng = np.random.default_rng(graine)
    rupt = jours = stock_somme = demande_somme = cmd = 0
    for rep in range(n_rep):
        for p, g in stk.groupby("id_produit"):
            v = g["demande"].values
            rop, q = rop_par_produit[p], qte_par_produit[p]
            stock = int(v.mean() * 25)
            arr = {}
            en_route = False
            for i in range(len(v)):
                if i in arr:
                    stock += arr.pop(i); en_route = False
                vendu = min(int(v[i]), stock)
                stock -= vendu
                rupt += int(v[i] > vendu); jours += 1; stock_somme += stock; demande_somme += v[i]
                if stock <= rop and not en_route:
                    arr[i + int(rng.choice(delais))] = q; en_route = True; cmd += 1
    return rupt / jours, stock_somme / demande_somme, cmd / (n_rep * stk["id_produit"].nunique())
