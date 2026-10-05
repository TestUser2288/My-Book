"""Figures du chapitre 8 produites par script (palette de build/style.py).
Usage : python3 build/fig_ch08.py [cube] [rsm]      (sans argument : tout)
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cube():
    """Cube des 8 moyennes du plan 2^3 répliqué (A : emballage, B : prix, C : relance)."""
    style.setup()
    f3 = pd.read_csv(os.path.join(RACINE, "donnees", "ch08-factoriel-2p3.csv"))
    m = f3.groupby(["A", "B", "C"])["commandes"].mean()
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    ax.set_axis_off()
    dx, dy = 0.9, 0.7                                   # décalage oblique pour le facteur C

    def pos(a, b, c):
        return (a + dx * (c + 1) / 2 * 1.0, b + dy * (c + 1) / 2 * 1.0)

    # arêtes
    for a in (-1, 1):
        for b in (-1, 1):
            ax.plot(*zip(pos(a, b, -1), pos(a, b, 1)), color=style.AXE, lw=1.2, zorder=1)
    for c in (-1, 1):
        for a, b, a2, b2 in [(-1, -1, 1, -1), (-1, 1, 1, 1), (-1, -1, -1, 1), (1, -1, 1, 1)]:
            ax.plot(*zip(pos(a, b, c), pos(a2, b2, c)), color=style.AXE, lw=1.2, zorder=1)
    vmin, vmax = m.min(), m.max()
    for (a, b, c), val in m.items():
        x, y = pos(a, b, c)
        t = (val - vmin) / (vmax - vmin)
        ax.scatter([x], [y], s=1900, color=style.SEQ(0.15 + 0.8 * t), zorder=3, edgecolor="white", linewidth=1.5)
        ax.text(x, y, f"{val:.1f}", ha="center", va="center", fontsize=11, zorder=4,
                color="white" if t > 0.45 else style.ENCRE, fontweight="bold")
    # étiquettes des facteurs
    ax.annotate("", xy=(1.55, -1.55), xytext=(-1.0, -1.55), arrowprops=dict(arrowstyle="->", color=style.ENCRE2))
    ax.text(0.3, -1.85, "A : emballage  standard (−) → cadeau (+)", ha="center", color=style.ENCRE2, fontsize=9)
    ax.annotate("", xy=(-1.75, 1.15), xytext=(-1.75, -1.0), arrowprops=dict(arrowstyle="->", color=style.ENCRE2))
    ax.text(-1.95, 0.1, "B : prix  normal (−) → promo (+)", rotation=90, va="center", ha="right", color=style.ENCRE2, fontsize=9)
    ax.annotate("", xy=(3.0, -0.62), xytext=(2.45, -1.04), arrowprops=dict(arrowstyle="->", color=style.ENCRE2))
    ax.text(2.45, -1.35, "C : relance\ne-mail (−) → réseaux\nsociaux (+)", ha="left", va="top", color=style.ENCRE2, fontsize=9)
    ax.set_xlim(-2.6, 4.2)
    ax.set_ylim(-2.1, 2.4)
    ax.set_title("Commandes hebdomadaires moyennes aux 8 sommets du plan 2³", color=style.ENCRE, pad=10)
    style.save(fig, "ch08-cube-2p3.png")


def rsm():
    """Surface de réponse du réglage du four : courbes de niveau, plan composite centré, optimum."""
    style.setup()
    import statsmodels.formula.api as smf
    d = pd.read_csv(os.path.join(RACINE, "donnees", "ch08-ccd-cuisson.csv"))
    mod = smf.ols("reussite ~ x1 + x2 + I(x1**2) + I(x2**2) + x1:x2", d).fit()
    p = mod.params
    b = np.array([p["x1"], p["x2"]])
    B = np.array([[p["I(x1 ** 2)"], p["x1:x2"] / 2], [p["x1:x2"] / 2, p["I(x2 ** 2)"]]])
    xs = -0.5 * np.linalg.solve(B, b)
    g1, g2 = np.meshgrid(np.linspace(-1.8, 1.8, 200), np.linspace(-1.8, 1.8, 200))
    z = p["Intercept"] + p["x1"] * g1 + p["x2"] * g2 + p["I(x1 ** 2)"] * g1**2 + p["I(x2 ** 2)"] * g2**2 + p["x1:x2"] * g1 * g2
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    cs = ax.contourf(g1, g2, z, levels=np.arange(60, 90, 2.5), cmap=style.SEQ, alpha=0.9)
    lines = ax.contour(g1, g2, z, levels=np.arange(65, 85, 5), colors="white", linewidths=0.8)
    ax.clabel(lines, fmt="%d", fontsize=8)
    cen = d[(d.x1 == 0) & (d.x2 == 0)]
    fact = d[(d.x1.abs() == 1) & (d.x2.abs() == 1)]
    axial = d[(d.x1.abs() > 1.2) | (d.x2.abs() > 1.2)]
    ax.scatter(fact.x1, fact.x2, s=45, color=style.ORANGE, zorder=4, label="points factoriels (4)")
    ax.scatter(axial.x1, axial.x2, s=45, marker="s", color=style.VIOLET, zorder=4, label="points axiaux (4)")
    ax.scatter(cen.x1, cen.x2, s=45, marker="D", color="white", edgecolor=style.ENCRE, zorder=4, label="centre (5 répétitions)")
    ax.scatter([xs[0]], [xs[1]], s=140, marker="*", color=style.ROUGE, edgecolor="white", zorder=5, label="optimum estimé")
    ax.set_xlabel("x₁ : température codée (1000 °C + 40 °C × x₁)")
    ax.set_ylabel("x₂ : durée codée (6 h + 1 h × x₂)")
    ax.set_title("Surface ajustée du taux de pièces sans défaut (%)")
    ax.grid(False)
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=8)
    fig.colorbar(cs, ax=ax, label="% de pièces sans défaut", shrink=0.85)
    style.save(fig, "ch08-rsm-contours.png")


if __name__ == "__main__":
    cibles = sys.argv[1:] or ["cube", "rsm"]
    if "cube" in cibles:
        cube()
    if "rsm" in cibles:
        rsm()
