"""Figures du chapitre 3 (SQL) : schémas dessinés avec matplotlib (style commun de build/style.py) et graphiques tirés de la base.

Chaque fonction écrit un PNG dans figures/ ; les données des graphiques sont passées en argument (calculées par les requêtes SQL du chapitre).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET, GRILLE, AXE

style.setup()


def _boite(ax, x, y, w, h, titre, lignes, couleur=BLEU, cles=()):
    """une table : titre coloré + liste de colonnes (les clés en gras)"""
    ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.0,rounding_size=0.06", fc="white", ec=couleur, lw=1.4))
    ax.add_patch(Rectangle((x, y - 0.34), w, 0.34, fc=couleur, ec=couleur))
    ax.text(x + w / 2, y - 0.17, titre, ha="center", va="center", color="white", fontsize=9.5, weight="bold")
    for i, c in enumerate(lignes):
        ax.text(x + 0.1, y - 0.34 - 0.24 * (i + 0.8), c, fontsize=8, va="center", color=ENCRE, weight="bold" if c in cles else "normal")


def schema(png="figures/ch03-schema.png"):
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.5); ax.axis("off"); ax.grid(False)
    cl = ["id_client", "date_inscription", "annee_naissance", "ville", "canal_acquisition", "fidelite", "…"]
    cm = ["id_commande", "date_commande", "heure", "id_client", "canal", "mode_livraison", "code_promo"]
    li = ["id_ligne", "id_commande", "id_produit", "quantite", "prix_unitaire", "remise_pct", "montant"]
    pr = ["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat", "fournisseur", "…"]
    re_ = ["id_retour", "id_ligne", "date_retour", "motif", "montant_rembourse"]
    jo = ["date", "nb_commandes", "chiffre_affaires", "temperature_moy", "pluie_mm", "promo_active", "depense_pub"]
    _boite(ax, 0.1, 5.3, 2.1, 2.3, "clients", cl, AQUA, ("id_client",))
    _boite(ax, 3.0, 5.3, 2.1, 2.3, "commandes", cm, BLEU, ("id_commande", "id_client"))
    _boite(ax, 5.7, 5.3, 2.1, 2.3, "lignes_commande", li, VIOLET, ("id_ligne", "id_commande", "id_produit"))
    _boite(ax, 5.7, 2.4, 2.1, 1.9, "produits", pr, ORANGE, ("id_produit",))
    _boite(ax, 8.45, 5.3, 1.52, 1.9, "retours", re_, ROUGE, ("id_retour", "id_ligne"))
    _boite(ax, 3.0, 2.4, 2.1, 2.3, "jours_exploitation", jo, MUET, ("date",))
    def lien(a, b, txt_a, txt_b, ls="-", rad=0.0):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-", color=ENCRE2, lw=1.2, linestyle=ls, connectionstyle=f"arc3,rad={rad}"))
        ax.text(a[0] + (0.1 if a[0] < b[0] else -0.1), a[1] + 0.12, txt_a, fontsize=8.5, color=ROUGE, ha="center", weight="bold")
        ax.text(b[0] + (-0.1 if a[0] < b[0] else 0.1), b[1] + 0.12, txt_b, fontsize=8.5, color=ROUGE, ha="center", weight="bold")
    lien((2.2, 4.0), (3.0, 4.0), "1", "n")                       # clients - commandes
    lien((5.1, 4.0), (5.7, 4.0), "1", "n")                       # commandes - lignes
    ax.annotate("", xy=(6.75, 3.0), xytext=(6.75, 2.45), arrowprops=dict(arrowstyle="-", color=ENCRE2, lw=1.2))
    ax.text(6.85, 2.55, "1", fontsize=8.5, color=ROUGE, weight="bold"); ax.text(6.85, 2.88, "n", fontsize=8.5, color=ROUGE, weight="bold")
    lien((7.8, 4.0), (8.45, 4.0), "1", "0-1")                     # lignes - retours
    ax.annotate("", xy=(4.05, 3.15), xytext=(4.05, 2.55), arrowprops=dict(arrowstyle="-", color=ENCRE2, lw=1.2, linestyle=":"))
    ax.text(4.15, 2.72, "même date\n(pas de clé déclarée)", fontsize=7.5, color=ENCRE2, va="center")
    ax.set_title("Les six tables de la base boutique.db : un trait relie une clé à la colonne qui la référence (1 = un, n = plusieurs)", fontsize=9.5)
    style.save(fig, os.path.basename(png))


def ordre(png="figures/ch03-ordre-execution.png"):
    fig, ax = plt.subplots(figsize=(9.4, 3.1))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3.2); ax.axis("off"); ax.grid(False)
    ecrit = ["SELECT", "FROM / JOIN", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    exe = ["FROM / JOIN", "WHERE", "GROUP BY", "HAVING", "SELECT\n(+ fenêtres)", "ORDER BY", "LIMIT"]
    ax.text(0.0, 2.85, "Dans l'ordre où vous l'écrivez", fontsize=9.5, weight="bold", color=ENCRE)
    ax.text(0.0, 1.35, "Dans l'ordre où le moteur le calcule", fontsize=9.5, weight="bold", color=ENCRE)
    for i, t in enumerate(ecrit):
        ax.add_patch(FancyBboxPatch((0.05 + i * 1.4, 1.9), 1.25, 0.6, boxstyle="round,pad=0,rounding_size=0.08", fc="white", ec=AXE, lw=1.2))
        ax.text(0.05 + i * 1.4 + 0.625, 2.2, t, ha="center", va="center", fontsize=8.5)
    for i, t in enumerate(exe):
        c = ORANGE if t.startswith("SELECT") else BLEU
        ax.add_patch(FancyBboxPatch((0.05 + i * 1.4, 0.4), 1.25, 0.7, boxstyle="round,pad=0,rounding_size=0.08", fc=c, ec=c, lw=1.2, alpha=0.9))
        ax.text(0.05 + i * 1.4 + 0.625, 0.75, t, ha="center", va="center", fontsize=8.5, color="white", weight="bold")
        ax.text(0.05 + i * 1.4 + 0.625, 0.2, f"étape {i + 1}", ha="center", va="center", fontsize=7.5, color=MUET)
    style.save(fig, os.path.basename(png))


def _tableau(ax, x, y, titre, cols, lignes, largeurs, couleur=BLEU, surlignes=()):
    """petit tableau de valeurs, coin supérieur gauche en (x, y)"""
    w = sum(largeurs); h = 0.3
    ax.text(x, y + 0.1, titre, fontsize=8.5, weight="bold", color=couleur, va="bottom")
    cx = x
    for c, lw in zip(cols, largeurs):
        ax.add_patch(Rectangle((cx, y - h), lw, h, fc=couleur, ec="white", lw=0.8))
        ax.text(cx + lw / 2, y - h / 2, c, color="white", ha="center", va="center", fontsize=8, weight="bold")
        cx += lw
    for i, l in enumerate(lignes):
        cx = x
        for j, (v, lw) in enumerate(zip(l, largeurs)):
            fc = "#fde7e0" if i in surlignes else "white"
            ax.add_patch(Rectangle((cx, y - h * (i + 2)), lw, h, fc=fc, ec=AXE, lw=0.6))
            ax.text(cx + lw / 2, y - h * (i + 1.5), "" if v is None else str(v), ha="center", va="center", fontsize=8, color=ENCRE if v is not None else MUET)
            cx += lw
    return w


def jointures(png="figures/ch03-jointures.png"):
    fig, ax = plt.subplots(figsize=(9.6, 5.3))
    ax.set_xlim(0, 11); ax.set_ylim(0, 6); ax.axis("off"); ax.grid(False)
    _tableau(ax, 0.1, 5.6, "table a", ["k", "v"], [(1, "a"), (2, "b"), (3, "c")], [0.6, 0.6], AQUA)
    _tableau(ax, 1.8, 5.6, "table b", ["k", "w"], [(2, "x"), (3, "y"), (4, "z")], [0.6, 0.6], VIOLET)
    ax.text(3.6, 4.9, "Jointure sur a.k = b.k : les clés 2 et 3 existent des deux côtés,\nla clé 1 seulement dans a, la clé 4 seulement dans b.", fontsize=8.5, va="top", color=ENCRE2)
    _tableau(ax, 0.1, 3.7, "INNER JOIN", ["k", "v", "w"], [(2, "b", "x"), (3, "c", "y")], [0.6, 0.6, 0.6], BLEU)
    _tableau(ax, 2.5, 3.7, "LEFT JOIN", ["k", "v", "w"], [(1, "a", None), (2, "b", "x"), (3, "c", "y")], [0.6, 0.6, 0.6], BLEU, surlignes=(0,))
    _tableau(ax, 4.9, 3.7, "RIGHT JOIN", ["k", "v", "w"], [(2, "b", "x"), (3, "c", "y"), (4, None, "z")], [0.6, 0.6, 0.6], BLEU, surlignes=(2,))
    _tableau(ax, 7.3, 3.7, "FULL JOIN", ["k", "v", "w"], [(1, "a", None), (2, "b", "x"), (3, "c", "y"), (4, None, "z")], [0.6, 0.6, 0.6], BLEU, surlignes=(0, 3))
    ax.text(0.1, 1.55, "Lignes en rose : lignes sans correspondance, complétées par des valeurs absentes (NULL).\n"
                       "INNER ne garde que les correspondances ; LEFT garde toutes les lignes de a ; RIGHT toutes celles de b ; FULL les deux.\n"
                       "CROSS JOIN, lui, ne regarde aucune clé : il associe chaque ligne de a à chaque ligne de b (ici 3 × 3 = 9 lignes).", fontsize=8.5, va="top", color=ENCRE2)
    style.save(fig, os.path.basename(png))


def multiplication(png="figures/ch03-multiplication.png"):
    fig, ax = plt.subplots(figsize=(9.6, 3.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.7); ax.axis("off"); ax.grid(False)
    _tableau(ax, 0.1, 3.0, "jours_exploitation", ["date", "depense_pub"], [("03/01", 150)], [0.9, 1.4], ORANGE)
    _tableau(ax, 3.6, 3.0, "commandes (3 ce jour-là)", ["id_commande", "date"], [(101, "03/01"), (102, "03/01"), (103, "03/01")], [1.5, 0.9], BLEU)
    ax.annotate("", xy=(7.0, 2.35), xytext=(6.3, 2.35), arrowprops=dict(arrowstyle="->", color=ENCRE2, lw=1.4))
    ax.text(6.65, 2.55, "JOIN sur\nla date", fontsize=7.5, ha="center", color=ENCRE2)
    _tableau(ax, 7.3, 3.0, "résultat de la jointure", ["date", "depense_pub", "id_commande"], [("03/01", 150, 101), ("03/01", 150, 102), ("03/01", 150, 103)], [0.7, 1.35, 1.55], VIOLET, surlignes=(1, 2))
    ax.text(0.1, 0.95, "SUM(depense_pub) avant la jointure : 150 €.   SUM(depense_pub) après la jointure : 3 × 150 = 450 €.\n"
                       "Chaque ligne de la table « 1 » est recopiée autant de fois qu'elle a de correspondances dans la table « n » :\n"
                       "toute somme prise sur la table « 1 » est alors multipliée par le nombre de correspondances.", fontsize=9, va="top", color=ENCRE)
    style.save(fig, os.path.basename(png))


def cte(png="figures/ch03-cte.png"):
    fig, ax = plt.subplots(figsize=(9.6, 2.9))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3.1); ax.axis("off"); ax.grid(False)
    etapes = [("commandes +\nlignes_commande", "tables sources", MUET), ("ca_client", "WITH : chiffre d'affaires\n2025 de chaque client", BLEU),
              ("top10", "WITH : les 10 premiers\npar chiffre d'affaires", AQUA), ("résultat", "SELECT final : part du\ntop 10 dans le total", ORANGE)]
    for i, (t, d, c) in enumerate(etapes):
        x = 0.1 + i * 2.75
        ax.add_patch(FancyBboxPatch((x, 1.25), 2.2, 0.9, boxstyle="round,pad=0,rounding_size=0.1", fc=c, ec=c))
        ax.text(x + 1.1, 1.7, t, ha="center", va="center", color="white", fontsize=9.5, weight="bold")
        ax.text(x + 1.1, 0.75, d, ha="center", va="center", fontsize=8.3, color=ENCRE2)
        if i < len(etapes) - 1:
            ax.annotate("", xy=(x + 2.7, 1.7), xytext=(x + 2.25, 1.7), arrowprops=dict(arrowstyle="->", color=ENCRE2, lw=1.4))
    ax.text(0.1, 2.75, "Une requête avec CTE se lit de gauche à droite, comme une recette : chaque étape a un nom et ne dépend que des précédentes.", fontsize=9, color=ENCRE)
    style.save(fig, os.path.basename(png))


def deciles(parts, png="figures/ch03-deciles.png"):
    """parts : liste de 10 parts (en %) du CA par décile de clients (du plus dépensier au moins dépensier)"""
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = range(1, 11)
    ax.bar(x, parts, color=[BLEU if i > 1 else ORANGE for i in x], width=0.7)
    for i, p in zip(x, parts):
        ax.text(i, p + 0.7, f"{p:.1f} %".replace(".", ","), ha="center", fontsize=8.5, color=ENCRE)
    ax.set_xticks(list(x)); ax.set_xlabel("décile de clients (1 = les 10 % qui dépensent le plus en 2025)"); ax.set_ylabel("part du chiffre d'affaires (%)")
    ax.set_ylim(0, max(parts) * 1.18); ax.grid(axis="x", visible=False)
    style.save(fig, os.path.basename(png))


def fenetres(mois, ca, cumul, moy3, png="figures/ch03-fenetres.png"):
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.5))
    ax = axs[0]
    ax.bar(range(len(mois)), [c / 1000 for c in ca], color="#9fc3f0", width=0.7, label="CA du mois")
    ax.plot(range(len(mois)), [m / 1000 for m in moy3], color=ORANGE, marker="o", ms=3.5, label="moyenne mobile sur 3 mois")
    ax.set_xticks(range(len(mois))); ax.set_xticklabels([m[5:] for m in mois], fontsize=8)
    ax.set_xlabel("mois de 2025"); ax.set_ylabel("k€"); ax.legend(fontsize=8, loc="upper left"); ax.set_title("Mois par mois et lissé")
    ax = axs[1]
    ax.plot(range(len(mois)), [c / 1000 for c in cumul], color=BLEU, marker="o", ms=3.5)
    ax.set_xticks(range(len(mois))); ax.set_xticklabels([m[5:] for m in mois], fontsize=8)
    ax.set_xlabel("mois de 2025"); ax.set_ylabel("k€ cumulés"); ax.set_title("Cumul depuis janvier")
    fig.tight_layout()
    style.save(fig, os.path.basename(png))
