"""Figures du chapitre 4 (celles qui demandent un dessin soigné).
Les autres figures du chapitre sont produites par le code même du livre (section 4.5) via fill.py.
Exécution : python build/fig_ch04.py [nom ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle
from style import *  # noqa
from donnees import commandes

setup()


def _grille(ax, x0, y0, valeurs, couleur, texte_couleur=ENCRE, alpha=0.35, fantome=None, taille=0.9, fmt="{:.0f}"):
    """Dessine une grille de cases (lignes de haut en bas) à partir du coin haut-gauche (x0, y0)."""
    v = np.atleast_2d(valeurs)
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            x, y = x0 + j, y0 - i - 1
            fant = fantome is not None and fantome[i, j]
            ax.add_patch(Rectangle((x + 0.04, y + 0.04), 0.92, 0.92, facecolor=couleur, alpha=0.12 if fant else alpha,
                                   edgecolor=couleur, lw=1.0, ls="--" if fant else "-"))
            ax.text(x + 0.5, y + 0.5, fmt.format(v[i, j]).replace("-", "−"), ha="center", va="center",
                    fontsize=10 * taille, color=MUET if fant else texte_couleur)


def broadcasting():
    A = np.array([[120, 150, 90, 140], [90, 100, 120, 70], [60, 50, 90, 105]])
    m = A.mean(axis=0)
    R = A - m
    fig, ax = plt.subplots(figsize=(11, 3.7))
    ax.set_xlim(-0.3, 22.3)
    ax.set_ylim(-1.4, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.grid(False)
    # A
    _grille(ax, 0, 3, A, BLEU)
    ax.text(2, 3.4, "A : ventes\n(3 canaux × 4 semaines)", ha="center", va="bottom", color=ENCRE, fontsize=9.5)
    ax.text(5.1, 1.5, "−", fontsize=22, ha="center", va="center", color=ENCRE2)
    # m étiré
    fant = np.array([[False] * 4, [True] * 4, [True] * 4])
    _grille(ax, 6.2, 3, np.tile(m, (3, 1)), ORANGE, fantome=fant)
    ax.text(8.2, 3.4, "m : moyennes par semaine\n(1 ligne × 4 colonnes)", ha="center", va="bottom", color=ENCRE, fontsize=9.5)
    ax.text(8.2, -0.45, "lignes pâles : copies virtuelles\nfabriquées par le broadcasting", ha="center",
            fontsize=8.5, color=MUET, va="top")
    ax.text(11.3, 1.5, "=", fontsize=22, ha="center", va="center", color=ENCRE2)
    _grille(ax, 12.4, 3, R, AQUA)
    ax.text(14.4, 3.4, "A − m : écart à la\nmoyenne de la semaine", ha="center", va="bottom", color=ENCRE, fontsize=9.5)
    ax.text(14.4, -0.45, "positif : mieux que la moyenne ;\nnégatif : moins bien", ha="center", fontsize=8.5,
            color=MUET, va="top")
    # petit rappel des formes
    ax.text(20.5, 2.5, "formes\n(3, 4) − (4,)\n→ (3, 4)", ha="center", va="center", fontsize=10, color=VIOLET,
            bbox=dict(boxstyle="round,pad=0.5", fc="none", ec=VIOLET, lw=1))
    save(fig, "ch04-broadcasting.png")


def anatomie():
    from matplotlib.patches import Rectangle as R
    rng = np.random.default_rng(4)
    semaines = np.arange(1, 13)
    insta = 100 + 4 * semaines + rng.normal(0, 8, 12)
    site = 80 + 3 * semaines + rng.normal(0, 8, 12)
    fig = plt.figure(figsize=(10.5, 5.4))
    fig.patch.set_edgecolor(ORANGE)
    fig.patch.set_linewidth(3)
    ax = fig.add_axes([0.25, 0.2, 0.5, 0.58])
    ax.plot(semaines, insta, color=BLEU, marker="o", ms=4, label="Réseaux")
    ax.plot(semaines, site, color=VIOLET, marker="s", ms=4, label="Site")
    ax.set_title("Ventes hebdomadaires (€)")
    ax.set_xlabel("semaine")
    ax.set_ylabel("ventes")
    ax.legend(loc="upper left")
    ax.set_xticks([1, 4, 8, 12])
    # cadre pointillé = zone Axes (au sens matplotlib : tout ce qui est dessiné dans le repère)
    ax.add_patch(R((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=ORANGE, lw=1.2, ls=(0, (4, 3)), clip_on=False))
    kw = dict(fontsize=9.5, color=ENCRE, va="center", arrowprops=dict(arrowstyle="->", color=MUET, lw=0.9, shrinkA=2, shrinkB=2))

    def note(texte, cible, pos):
        ax.annotate(texte, xy=cible, xycoords="axes fraction", xytext=pos, textcoords="axes fraction", **kw)

    # droite
    note("ax.set_title(…)", (0.78, 1.04), (1.08, 1.12))
    note("ax.plot(…) : une ligne\n(objet Line2D)", (0.97, 0.9), (1.08, 0.82))
    note("cadre pointillé : l'Axes,\nla zone de dessin (une figure\npeut en contenir plusieurs)", (1.0, 0.45), (1.08, 0.45))
    note("ax.grid(…) : la grille", (0.8, 0.15), (1.08, 0.12))
    # gauche
    note("ax.legend()", (0.02, 0.91), (-0.58, 0.95))
    note("ax.set_ylabel(…)", (-0.1, 0.5), (-0.58, 0.55))
    note("graduations (ticks)\net leurs étiquettes", (-0.02, 0.2), (-0.58, 0.18))
    # bas
    note("ax.set_xlabel(…)", (0.5, -0.19), (0.5, -0.33))
    fig.text(0.015, 0.96, "Figure : toute la page (bord orange plein)", fontsize=10.5, color=ORANGE, weight="bold", va="top")
    save(fig, "ch04-anatomie.png")


def axe_tronque():
    df = commandes()
    ordre = ["Réseaux", "Site"]
    moy = df.groupby("canal")["satisfaction"].mean().reindex(ordre)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), gridspec_kw={"wspace": 0.3})
    for ax, (ymin, ymax, titre, col) in zip(axes, [(3.70, 3.80, "Axe tronqué : l'écart paraît énorme", ROUGE),
                                                   (0, 5, "Axe complet : l'écart est minuscule", BLEU)]):
        ax.bar(ordre, moy.values, color=col, alpha=0.65, width=0.5)
        ax.set_ylim(ymin, ymax)
        ax.set_title(titre, color=ENCRE)
        ax.set_ylabel("satisfaction moyenne (1 à 5)")
        ax.grid(axis="x", visible=False)
        for i, v in enumerate(moy.values):
            ax.text(i, v + (ymax - ymin) * 0.02, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9.5, color=ENCRE)
    save(fig, "ch04-axe-tronque.png")


if __name__ == "__main__":
    noms = sys.argv[1:] or ["broadcasting", "anatomie", "axe_tronque"]
    for n in noms:
        globals()[n]()
