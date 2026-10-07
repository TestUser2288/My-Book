"""Figures du chapitre 4 (série 2, volume I) : format large et long (schéma), ventes hebdomadaires."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import style as S

CAN = {"Boutique": S.BLEU, "Réseaux": S.VIOLET, "Site": S.ORANGE}


def _table(ax, x0, y0, entetes, lignes, largeurs, couleurs_col=None, h=0.34, taille=8.5):
    x = x0
    for j, (e, w) in enumerate(zip(entetes, largeurs)):
        ax.add_patch(Rectangle((x, y0), w, h, fc="#e7e6e0", ec=S.AXE, lw=0.6))
        c = (couleurs_col or {}).get(e, S.ENCRE)
        ax.text(x + w / 2, y0 + h / 2, e, ha="center", va="center", fontsize=taille, weight="bold", color=c)
        x += w
    for i, lg in enumerate(lignes):
        x = x0
        for j, (v, w) in enumerate(zip(lg, largeurs)):
            ax.add_patch(Rectangle((x, y0 - (i + 1) * h), w, h, fc="white", ec=S.AXE, lw=0.6))
            c = CAN.get(v, S.ENCRE) if isinstance(v, str) and v in CAN else S.ENCRE
            ax.text(x + w / 2, y0 - (i + 0.5) * h, v, ha="center", va="center", fontsize=taille, color=c)
            x += w


def fig_large_long(nom="ch04-large-long.png"):
    S.setup()
    fig, ax = plt.subplots(figsize=(8.4, 2.9))
    ax.set_xlim(0, 10.6); ax.set_ylim(0.3, 3.5); ax.axis("off"); ax.grid(False)
    ax.text(0.1, 3.3, "Format large : une colonne par canal", fontsize=9, color=S.ENCRE, weight="bold")
    _table(ax, 0.1, 2.85, ["annee", "Boutique", "Réseaux", "Site"],
           [["2023", "594", "123", "422"], ["2024", "558", "129", "503"], ["2025", "561", "146", "618"]],
           [0.8, 1.0, 1.0, 1.0], couleurs_col=CAN)
    ax.text(6.0, 3.3, "Format long : une ligne par observation", fontsize=9, color=S.ENCRE, weight="bold")
    lignes = [[a, c, v] for c, vs in [("Boutique", ["594", "558", "561"]), ("Réseaux", ["123", "129", "146"]), ("Site", ["422", "503", "618"])]
              for a, v in zip(["2023", "2024", "2025"], vs)]
    _table(ax, 6.0, 2.85, ["annee", "canal", "ca"], lignes[:7], [0.8, 1.2, 0.8], h=0.3, taille=8)
    ax.text(8.0, 0.5, "… (9 lignes en tout)", fontsize=7.5, ha="center", color=S.MUET)
    for (xa, xb, y, txt, ytxt) in [(4.1, 5.8, 2.0, "pivot_longer / melt", 2.2), (5.8, 4.1, 1.2, "pivot_wider / pivot", 0.82)]:
        ax.add_patch(FancyArrowPatch((xa, y), (xb, y), arrowstyle="-|>", mutation_scale=14, color=S.ENCRE2, lw=1.4))
        ax.text((xa + xb) / 2, ytxt, txt, ha="center", fontsize=8, color=S.ENCRE2)
    S.save(fig, nom)


def fig_semaines(sem, annee=2025, semaine_cible=45, nom="ch04-semaines.png"):
    """chiffre d'affaires hebdomadaire total, année N contre année N-1 (semaines ISO), avec la semaine du tableau du lundi marquée"""
    S.setup()
    tot = sem.groupby(["annee_iso", "semaine"], as_index=False)["montant"].sum()
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    for a, c, lab, lw in [(annee - 1, S.MUET, str(annee - 1), 1.6), (annee, S.BLEU, str(annee), 2.2)]:
        d = tot[(tot.annee_iso == a) & (tot.semaine <= 52)].sort_values("semaine")
        ax.plot(d["semaine"], d["montant"] / 1000, color=c, lw=lw)
        ax.text(d["semaine"].iloc[-1] + 0.6, d["montant"].iloc[-1] / 1000, lab, color=c, va="center", fontsize=9)
    v = tot[(tot.annee_iso == annee) & (tot.semaine == semaine_cible)]["montant"].iloc[0] / 1000
    ax.scatter([semaine_cible], [v], color=S.ORANGE, zorder=5, s=36)
    ax.annotate(f"semaine {semaine_cible} : tableau du lundi", (semaine_cible, v), xytext=(semaine_cible - 17, v + 12), fontsize=8.5, color=S.ORANGE,
                arrowprops=dict(arrowstyle="-", color=S.ORANGE, lw=0.8))
    ax.set_xlabel("semaine ISO"); ax.set_ylabel("chiffre d'affaires hebdomadaire (milliers d'€)")
    ax.set_xlim(1, 57)
    S.save(fig, nom)
