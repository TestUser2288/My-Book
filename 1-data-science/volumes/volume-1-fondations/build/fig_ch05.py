"""Figures du chapitre 5. Exécution : python build/fig_ch05.py [nom ...]
Lit donnees/dar_jasmin.db (créé par le code de la section 5.1.3)."""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle
from style import *  # noqa

setup()
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def schema_er():
    tables = {  # nom : (couleur, [(étiquette, colonne)])
        "categories": (AQUA, [("PK", "id_categorie"), ("", "nom")]),
        "produits": (AQUA, [("PK", "id_produit"), ("", "nom"), ("FK", "id_categorie"), ("", "prix_catalogue")]),
        "lignes_commande": (ORANGE, [("PK FK", "id_commande"), ("PK FK", "id_produit"), ("", "quantite"), ("", "prix_unitaire")]),
        "commandes": (BLEU, [("PK", "id_commande"), ("FK", "id_client"), ("", "date_commande"), ("", "canal"),
                             ("", "montant"), ("", "delai_livraison"), ("", "satisfaction")]),
        "clients": (VIOLET, [("PK", "id_client"), ("", "prenom"), ("", "nom"), ("", "ville"),
                             ("", "date_inscription"), ("", "telephone"), ("FK", "id_parrain")]),
    }
    ordre = ["categories", "produits", "lignes_commande", "commandes", "clients"]
    L, ECART, HT, HL = 2.85, 1.0, 0.5, 0.42          # largeur boîte, écart, hauteur titre, hauteur ligne
    fig, ax = plt.subplots(figsize=(15, 4.6))
    ax.set_xlim(-0.2, len(ordre) * (L + ECART) + 0.6)
    ax.set_ylim(-0.4, 3.7)
    ax.axis("off")
    ax.grid(False)
    pos = {}   # (table, colonne) -> (x_gauche, x_droite, y_centre)
    ytop = 3.5
    for i, nom in enumerate(ordre):
        coul, cols = tables[nom]
        x0 = i * (L + ECART)
        h = HT + HL * len(cols)
        ax.add_patch(Rectangle((x0, ytop - h), L, h, facecolor=SURFACE, edgecolor=coul, lw=1.4, zorder=2))
        ax.add_patch(Rectangle((x0, ytop - HT), L, HT, facecolor=coul, edgecolor=coul, lw=1.4, zorder=3, alpha=0.9))
        ax.text(x0 + L / 2, ytop - HT / 2, nom, color="white", ha="center", va="center", fontsize=10, fontweight="bold", zorder=4)
        for j, (etiq, col) in enumerate(cols):
            y = ytop - HT - HL * (j + 0.5)
            if etiq:
                ax.text(x0 + 0.1, y, etiq, color=ORANGE if "PK" in etiq else VIOLET, fontsize=7.5, fontweight="bold",
                        va="center", zorder=4)
            ax.text(x0 + 0.62 if "PK FK" not in etiq else x0 + 0.78, y, col, color=ENCRE, fontsize=8.8, va="center", zorder=4)
            pos[(nom, col)] = (x0, x0 + L, y)

    def lien(fk, pk, cote_fk, cote_pk):
        (a0, a1, ya), (b0, b1, yb) = pos[fk], pos[pk]
        xa = a0 if cote_fk == "g" else a1
        xb = b0 if cote_pk == "g" else b1
        ax.plot([xa, xb], [ya, yb], color=ENCRE2, lw=1.1, zorder=1)
        sgn = lambda x0, x1: 1 if x1 > x0 else -1
        ax.text(xa + 0.14 * sgn(xa, xb), ya + 0.1, "N", color=ENCRE2, fontsize=8.5, fontweight="bold", ha="center", va="bottom")
        ax.text(xb - 0.14 * sgn(xa, xb), yb + 0.1, "1", color=ENCRE2, fontsize=8.5, fontweight="bold", ha="center", va="bottom")

    lien(("produits", "id_categorie"), ("categories", "id_categorie"), "g", "d")
    lien(("lignes_commande", "id_produit"), ("produits", "id_produit"), "g", "d")
    lien(("lignes_commande", "id_commande"), ("commandes", "id_commande"), "d", "g")
    lien(("commandes", "id_client"), ("clients", "id_client"), "d", "g")
    # relation réflexive : parrainage (boucle à droite de la table clients)
    _, xr, y1 = pos[("clients", "id_parrain")]
    _, _, y2 = pos[("clients", "id_client")]
    xs = xr + 0.45
    ax.plot([xr, xs, xs, xr], [y1, y1, y2, y2], color=ENCRE2, lw=1.1, zorder=1)
    ax.text(xr + 0.12, y1 + 0.1, "N", color=ENCRE2, fontsize=8.5, fontweight="bold", ha="center", va="bottom")
    ax.text(xr + 0.12, y2 + 0.1, "1", color=ENCRE2, fontsize=8.5, fontweight="bold", ha="center", va="bottom")
    ax.text(xs + 0.07, (y1 + y2) / 2, "parrainage", color=ENCRE2, fontsize=8.5, rotation=90, va="center", ha="left")
    save(fig, "ch05-schema-er.png")


def ca_mensuel():
    con = sqlite3.connect(os.path.join(RACINE, "donnees", "dar_jasmin.db"))
    df = pd.read_sql_query(
        "SELECT substr(date_commande, 1, 7) AS mois, SUM(montant) AS ca FROM commandes GROUP BY mois ORDER BY mois", con)
    df["moy3"] = df.ca.rolling(3).mean()
    df["cumul"] = df.ca.cumsum()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.9), gridspec_kw={"wspace": 0.28})
    ax = axes[0]
    x = np.arange(12)
    ax.bar(x, df.ca, color=BLEU, alpha=0.55, width=0.7)
    ax.plot(x[2:], df.moy3[2:], color=ORANGE, marker="o", ms=4)
    ax.text(-0.3, 3250, "— moyenne mobile sur 3 mois", color=ORANGE, fontsize=9, ha="left", va="center")
    ax.set_xticks(x, [m[5:] for m in df.mois])
    ax.set_xlabel("mois de 2025")
    ax.set_ylabel("chiffre d'affaires (DT)")
    ax.set_title("Chiffre d'affaires mensuel")
    ax.grid(axis="x", visible=False)
    ax = axes[1]
    ax.plot(x, df.cumul, color=VIOLET, marker="o", ms=4)
    ax.fill_between(x, df.cumul, color=VIOLET, alpha=0.1)
    ax.text(0, 22500, f"total de l'année : {df.cumul.iloc[11]:,.0f} DT".replace(",", " "), color=VIOLET, fontsize=9.5, ha="left")
    ax.set_xticks(x, [m[5:] for m in df.mois])
    ax.set_xlabel("mois de 2025")
    ax.set_title("Chiffre d'affaires cumulé depuis janvier")
    ax.grid(axis="x", visible=False)
    save(fig, "ch05-ca-mensuel.png")


if __name__ == "__main__":
    noms = sys.argv[1:] or ["schema_er", "ca_mensuel"]
    for n in noms:
        globals()[n]()
