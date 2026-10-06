"""Figures du chapitre 3 (calcul distribué) : schémas et courbes. Appelé depuis des blocs cachés du livre et du cahier.
Usage : python build/fig_ch03.py [nom ...]   (sans argument : toutes les figures sans données)"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style  # noqa: E402
from style import AQUA, BLEU, ENCRE, ENCRE2, MUET, ORANGE, ROUGE, VIOLET  # noqa: E402

style.setup()


def _boite(ax, x, y, w, h, texte, couleur=BLEU, fond=None, taille=8.5, poids="regular"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fond or (couleur + "22"), ec=couleur, lw=1.3))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=taille, color=ENCRE, fontweight=poids)


def _fleche(ax, p, q, couleur=ENCRE2, style_="-|>", lw=1.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style_, mutation_scale=10, color=couleur, lw=lw, connectionstyle=f"arc3,rad={rad}"))


def _vide(figsize, xlim, ylim):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis("off"); ax.grid(False)
    return fig, ax


def mapreduce():
    """Comptage de mots en trois phases : map, mélange (shuffle), reduce."""
    fig, ax = _vide((9.2, 4.3), (0, 9.2), (0, 4.3))
    lignes = ["« le colis est arrivé »", "« le colis est cassé »", "« le prix est bon »"]
    for i, t in enumerate(lignes):
        _boite(ax, 0.1, 3.1 - 1.15 * i, 2.1, 0.8, f"Machine {i + 1}\n{t}", BLEU)
    ax.text(1.15, 4.05, "Entrée découpée", ha="center", fontsize=9, color=ENCRE2)
    sorties = ["(le,1) (colis,1)\n(est,1) (arrivé,1)", "(le,1) (colis,1)\n(est,1) (cassé,1)", "(le,1) (prix,1)\n(est,1) (bon,1)"]
    for i, t in enumerate(sorties):
        _boite(ax, 3.05, 3.1 - 1.15 * i, 1.95, 0.8, t, ORANGE, taille=7.8)
        _fleche(ax, (2.2, 3.5 - 1.15 * i), (3.05, 3.5 - 1.15 * i))
    ax.text(4.0, 4.05, "1. map", ha="center", fontsize=9, color=ORANGE, fontweight="bold")
    ax.text(6.0, 4.05, "2. mélange (shuffle)", ha="center", fontsize=9, color=VIOLET, fontweight="bold")
    groupes = ["le → 1,1,1\nest → 1,1,1", "colis → 1,1\nprix → 1", "arrivé → 1\ncassé → 1\nbon → 1"]
    ys = [3.1, 1.95, 0.6]
    for i, t in enumerate(groupes):
        _boite(ax, 5.35, ys[i], 1.4, 0.8 if i < 2 else 1.1, t, VIOLET, taille=7.8)
    for i in range(3):
        for j in range(3):
            _fleche(ax, (5.0, 3.5 - 1.15 * i), (5.35, ys[j] + 0.4), couleur=MUET, lw=0.7)
    ax.text(8.1, 4.05, "3. reduce", ha="center", fontsize=9, color=AQUA, fontweight="bold")
    res = ["le : 3\nest : 3", "colis : 2\nprix : 1", "arrivé : 1\ncassé : 1\nbon : 1"]
    for i, t in enumerate(res):
        _boite(ax, 7.45, ys[i], 1.5, 0.8 if i < 2 else 1.1, t, AQUA, taille=7.8)
        _fleche(ax, (6.75, ys[i] + 0.4), (7.45, ys[i] + 0.4))
    ax.set_title("MapReduce : trois phases ; seul le mélange déplace des données entre machines", fontsize=10)
    style.save(fig, "ch03-mapreduce.png")


def ligne_colonne():
    """Stockage par lignes et par colonnes."""
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5))
    noms = ["id", "canal", "montant"]
    donnees = [[1, "Site", 42.5], [2, "Boutique", 18.0], [3, "Réseaux", 63.2], [4, "Site", 27.9]]
    for ax in axes:
        ax.set_xlim(0, 10); ax.set_ylim(-0.7, 6.2); ax.axis("off"); ax.grid(False)
    ax = axes[0]
    ax.set_title("Par lignes (CSV, bases transactionnelles)", fontsize=10)
    for j, n in enumerate(noms):
        ax.text(1.0 + 2.6 * j + 1.1, 5.4, n, ha="center", fontsize=9, color=ENCRE2, fontweight="bold")
    for i, lig in enumerate(donnees):
        for j, v in enumerate(lig):
            _boite(ax, 1.0 + 2.6 * j, 4.2 - 1.05 * i, 2.2, 0.8, str(v), BLEU, taille=8.5)
    ax.annotate("", xy=(9.2, 0.6), xytext=(9.2, 4.9), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4))
    ax.text(5.0, -0.45, "on lit une ligne entière, colonne après colonne", ha="center", fontsize=8.5, color=ORANGE)
    ax = axes[1]
    ax.set_title("Par colonnes (Parquet, entrepôts analytiques)", fontsize=10)
    couleurs = [BLEU, AQUA, VIOLET]
    for j, n in enumerate(noms):
        ax.text(1.0 + 2.6 * j + 1.1, 5.4, n, ha="center", fontsize=9, color=ENCRE2, fontweight="bold")
        for i, lig in enumerate(donnees):
            _boite(ax, 1.0 + 2.6 * j, 4.2 - 1.05 * i, 2.2, 0.8, str(lig[j]), couleurs[j], taille=8.5)
    ax.add_patch(plt.Rectangle((6.15, 0.35), 2.6, 4.9, fill=False, ec=ORANGE, lw=2, ls="--"))
    ax.text(5.0, -0.45, "on ne lit que la colonne demandée (ici : montant)", ha="center", fontsize=8.5, color=ORANGE)
    style.save(fig, "ch03-ligne-colonne.png")


def spark_architecture():
    """Pilote, gestionnaire de ressources et exécuteurs."""
    fig, ax = _vide((9.2, 4.6), (0, 9.2), (0, 4.6))
    _boite(ax, 0.2, 1.7, 2.3, 1.6, "Programme pilote\n(driver)\n\nplan, DAG,\nplanification", BLEU, taille=8.5)
    _boite(ax, 3.4, 3.65, 2.2, 0.7, "Gestionnaire de ressources", VIOLET, taille=8.5)
    for i in range(3):
        y = 2.65 - 1.2 * i
        _boite(ax, 6.2, y - 0.1, 2.8, 1.0, "", AQUA)
        ax.text(6.35, y + 0.7, f"Exécuteur {i + 1}", fontsize=8.5, color=ENCRE, fontweight="bold")
        for k in range(2):
            _boite(ax, 6.35 + 1.25 * k, y, 1.15, 0.45, f"tâche {2 * i + k + 1}", ORANGE, taille=7.6)
        _fleche(ax, (2.5, 2.5), (6.2, y + 0.35), couleur=MUET, lw=0.9)
    _fleche(ax, (1.8, 3.3), (3.4, 3.95), couleur=VIOLET)
    _fleche(ax, (5.6, 3.95), (7.6, 3.6), couleur=VIOLET)
    ax.text(3.7, 3.1, "demande des\nexécuteurs", fontsize=7.8, color=VIOLET, ha="center")
    ax.text(4.2, 1.1, "tâches envoyées,\nrésultats renvoyés", fontsize=7.8, color=ENCRE2, ha="center")
    ax.set_title("Architecture de Spark : un pilote, des exécuteurs, des tâches", fontsize=10)
    style.save(fig, "ch03-spark-architecture.png")


def fenetres():
    """Fenêtres fixes (tumbling), glissantes (sliding) et de session."""
    fig, axes = plt.subplots(3, 1, figsize=(9.0, 4.4), sharex=True)
    ev = [4, 11, 17, 26, 31, 34, 52, 58]
    titres = ["Fenêtres fixes de 20 s (chaque évènement dans une seule)", "Fenêtres glissantes de 20 s toutes les 10 s (un évènement dans deux)", "Fenêtres de session (silence de plus de 12 s)"]
    for ax, t in zip(axes, titres):
        ax.set_xlim(0, 62); ax.set_ylim(0, 1); ax.set_yticks([]); ax.grid(False)
        ax.set_title(t, fontsize=9, loc="left")
        ax.plot(ev, [0.16] * len(ev), "o", color=ENCRE, ms=5)
    for k, d in enumerate(range(0, 60, 20)):
        axes[0].add_patch(plt.Rectangle((d + 0.3, 0.38), 19.4, 0.4, fc=[BLEU, AQUA, VIOLET][k] + "55", ec=[BLEU, AQUA, VIOLET][k]))
    for k, d in enumerate(range(0, 50, 10)):
        axes[1].add_patch(plt.Rectangle((d + 0.3, 0.32 + 0.22 * (k % 2)), 19.4, 0.2, fc=[BLEU, ORANGE][k % 2] + "44", ec=[BLEU, ORANGE][k % 2]))
    for d0, d1 in [(4, 34 + 12), (52, 58 + 12)]:        # une session = du premier évènement jusqu'au dernier + le délai de silence
        axes[2].add_patch(plt.Rectangle((d0, 0.38), min(d1, 62) - d0, 0.4, fc=AQUA + "55", ec=AQUA))
    axes[2].set_xlabel("temps de l'évènement (secondes)")
    fig.tight_layout()
    style.save(fig, "ch03-fenetres.png")


def amdahl(courbes=None):
    """Accélération de la loi d'Amdahl pour plusieurs fractions parallélisables."""
    n = np.arange(1, 65)
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    for p, c in [(0.5, ROUGE), (0.9, ORANGE), (0.99, BLEU)]:
        s = 1 / ((1 - p) + p / n)
        ax.plot(n, s, color=c, lw=2)
        ax.axhline(1 / (1 - p), color=c, lw=0.8, ls=":")
        ax.text(64.5, s[-1], f"p = {str(p).replace('.', ',')}\nplafond {1 / (1 - p):g}", color=c, fontsize=8.5, va="center")
    ax.plot(n, n, color=MUET, lw=1, ls="--"); ax.text(9, 17, "accélération idéale", color=MUET, fontsize=8.5, rotation=40)
    ax.set_xlim(1, 82); ax.set_ylim(0, 40)
    ax.set_xlabel("nombre de machines (ou de cœurs) n"); ax.set_ylabel("accélération S(n)")
    ax.set_title("Loi d'Amdahl : la partie séquentielle fixe un plafond")
    style.save(fig, "ch03-amdahl.png")


def asymetrie(avant, apres, k_avant, k_apres):
    """Lignes par partition avant et après salage."""
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
    for ax, v, c, t in [(axes[0], avant, ROUGE, f"Clé brute : la plus grosse partition = {k_avant:.2f} × la moyenne".replace(".", ",")),
                        (axes[1], apres, AQUA, f"Clé salée : la plus grosse partition = {k_apres:.2f} × la moyenne".replace(".", ","))]:
        ax.bar(range(len(v)), np.asarray(v) / 1e3, color=c, width=0.7)
        ax.axhline(np.mean(v) / 1e3, color=ENCRE2, lw=1, ls="--")
        ax.set_xlabel("numéro de partition"); ax.set_title(t, fontsize=9)
        ax.grid(axis="x", visible=False); ax.set_xticks(range(len(v)))
    axes[0].set_ylabel("lignes (milliers)")
    axes[0].text(len(avant) - 0.5, np.mean(avant) / 1e3, "moyenne", ha="right", va="bottom", fontsize=8, color=ENCRE2)
    fig.tight_layout()
    style.save(fig, "ch03-asymetrie.png")


if __name__ == "__main__":
    for f in sys.argv[1:] or ["mapreduce", "ligne_colonne", "spark_architecture", "fenetres", "amdahl"]:
        globals()[f]()
