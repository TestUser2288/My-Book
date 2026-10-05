"""Figures du chapitre 1. Exécution : python build/fig_ch01.py [nom ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from style import *  # noqa

setup()


def ellipse_propre():
    A = np.array([[2, 1], [1, 2]])
    t = np.linspace(0, 2 * np.pi, 400)
    cercle = np.vstack([np.cos(t), np.sin(t)])
    ell = A @ cercle
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.plot(cercle[0], cercle[1], color=MUET, lw=1.2, ls="--")
    ax.plot(ell[0], ell[1], color=BLEU, lw=2.2)
    s = 1 / np.sqrt(2)
    # vecteurs propres : (1,1)/√2 étiré x3 ; (1,-1)/√2 étiré x1
    ax.annotate("", xy=(3 * s, 3 * s), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2))
    ax.annotate("", xy=(s, -s), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2))
    ax.text(3 * s + 0.08, 3 * s + 0.05, "direction (1, 1)\nétirée ×3", color=ENCRE2, fontsize=9)
    ax.annotate("direction (1, −1)\nconservée ×1", xy=(s * 0.9, -s * 0.9), xytext=(1.35, -1.85),
                color=ENCRE2, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], color=MUET, lw=1.2, ls="--", label="cercle unité (avant)"),
                       Line2D([0], [0], color=BLEU, lw=2.2, label="ellipse (après A)")],
              loc="upper left", fontsize=9)
    ax.set_aspect("equal")
    ax.set_xlim(-3.2, 3.6)
    ax.set_ylim(-2.4, 3.2)
    ax.axhline(0, color=AXE, lw=0.8)
    ax.axvline(0, color=AXE, lw=0.8)
    save(fig, "ch01-ellipse-propre.png")


def nuage_clients():
    rng = np.random.default_rng(42)
    n = 200
    visites = rng.normal(6, 2, n)
    depense = 15 * visites + rng.normal(0, 12, n)
    z = lambda x: (x - x.mean()) / x.std(ddof=1)
    Z = np.column_stack([z(visites), z(depense)])
    C = np.cov(Z.T)
    w, v = np.linalg.eigh(C)
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.scatter(Z[:, 0], Z[:, 1], s=16, color=BLEU, alpha=0.55, edgecolor="none")
    for k, col in [(1, ORANGE), (0, VIOLET)]:
        d = v[:, k] * np.sqrt(w[k]) * 2
        if k == 1 and d[0] < 0:
            d = -d
        ax.annotate("", xy=d, xytext=-d if k == 1 else (0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2))
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], color=ORANGE, lw=2.2, label="axe principal (95 % de la variance)"),
                       Line2D([0], [0], color=VIOLET, lw=2.2, label="axe secondaire (5 %)")],
              loc="upper left", fontsize=9)
    ax.set_xlabel("visites par mois (standardisées)")
    ax.set_ylabel("dépense mensuelle (standardisée)")
    ax.set_aspect("equal")
    ax.set_xlim(-3.3, 3.8)
    ax.set_ylim(-3.3, 3.8)
    save(fig, "ch01-nuage-clients.png")


def svd_ventes():
    rng = np.random.default_rng(7)
    popularite = np.array([50, 30, 20, 12, 8, 5.0])
    saison = np.array([1.0, 1.1, 0.9, 1.2, 1.5, 1.4, 1.0, 0.8])
    M = (np.outer(popularite, saison) + rng.normal(0, 1.0, (6, 8))).round(0)
    U, s, Vt = np.linalg.svd(M)
    M1 = s[0] * np.outer(U[:, 0], Vt[0])
    R = M - M1
    produits = ["Huile", "Dattes", "Poteries", "Savons", "Bijoux", "Tapis"]
    semaines = [f"S{i}" for i in range(1, 9)]
    vmax = M.max()
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.6), constrained_layout=True)
    titres = ["ventes observées", "approximation de rang 1", "ce qui reste (différence)"]
    ims = []
    for ax, data, titre, cmap, lim in zip(
        axes, [M, M1, R], titres, [SEQ, SEQ, DIV], [(0, vmax), (0, vmax), (-vmax * 0.1, vmax * 0.1)]
    ):
        ims.append(ax.imshow(data, cmap=cmap, vmin=lim[0], vmax=lim[1], aspect="auto"))
        ax.set_title(titre)
        ax.set_xticks(range(8), semaines, fontsize=8)
        ax.set_yticks(range(6), produits if ax is axes[0] else [""] * 6, fontsize=8)
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
    cb = fig.colorbar(ims[0], ax=axes[:2], orientation="horizontal", shrink=0.5, aspect=30, pad=0.04)
    cb.set_label("ventes (unités)", fontsize=8)
    cb.outline.set_visible(False)
    cb2 = fig.colorbar(ims[2], ax=axes[2], orientation="horizontal", shrink=0.8, aspect=20, pad=0.04)
    cb2.set_label("écart (unités)", fontsize=8)
    cb2.outline.set_visible(False)
    save(fig, "ch01-svd-ventes.png")


def benefice_tangentes():
    P = lambda q: -2 * q**2 + 80 * q - 300
    q = np.linspace(0, 40, 400)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(q, P(q), color=BLEU, lw=2.4)
    # tangente en q=10 (pente 40) et en q=20 (pente 0)
    q1 = np.linspace(4, 17, 10)
    ax.plot(q1, P(10) + 40 * (q1 - 10), color=ORANGE, lw=1.6)
    q2 = np.linspace(14, 27, 10)
    ax.plot(q2, P(20) + 0 * (q2 - 20), color=ORANGE, lw=1.6)
    ax.scatter([10, 20], [P(10), P(20)], color=ORANGE, zorder=5, s=36)
    ax.annotate("tangente en q = 10\npente = +40 € par pièce", xy=(10, 300), xytext=(15.5, 110), color=ENCRE2,
                fontsize=9, va="center", arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    ax.text(21.5, 523, "sommet en q = 20 : pente = 0", color=ENCRE2, fontsize=9, va="bottom")
    ax.axhline(0, color=AXE, lw=0.8)
    ax.set_xlabel("pièces vendues par semaine, q")
    ax.set_ylabel("bénéfice P(q) en €")
    ax.set_ylim(-320, 640)
    save(fig, "ch01-benefice-tangentes.png")


def gradient_contours():
    f = lambda x, y: x**2 + 3 * y**2
    xs = np.linspace(-3.2, 3.2, 300)
    ys = np.linspace(-2.2, 2.2, 300)
    X, Y = np.meshgrid(xs, ys)
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    cs = ax.contour(X, Y, f(X, Y), levels=[0.5, 1, 2, 4, 6, 9, 12, 16], colors=MUET, linewidths=0.9)
    ax.clabel(cs, fmt=lambda v: f"{v:g}", fontsize=7, colors=MUET)
    pts = np.array([[2.4, 0.9], [-2.2, 1.0], [1.0, -1.6], [-1.4, -0.8], [2.6, -0.6], [0.4, 1.6], [-0.6, 0.4]])
    G = np.column_stack([2 * pts[:, 0], 6 * pts[:, 1]])
    D = -G / np.linalg.norm(G, axis=1, keepdims=True)
    ax.scatter(pts[:, 0], pts[:, 1], color=BLEU, s=22, zorder=4)
    ax.quiver(pts[:, 0], pts[:, 1], D[:, 0], D[:, 1], color=ORANGE, angles="xy", scale_units="xy", scale=2.4,
              width=0.006, zorder=5)
    ax.scatter([0], [0], color=ENCRE, s=26, zorder=6)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor=ENCRE, markersize=6, label="minimum (0, 0)"),
                       Line2D([0], [0], marker="o", color="none", markerfacecolor=BLEU, markersize=6, label="points de départ"),
                       Line2D([0], [0], color=ORANGE, lw=2, label="plus forte descente (−gradient)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=8.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    ax.grid(False)
    save(fig, "ch01-gradient-contours.png")


def attente_densite():
    lam = 0.5
    t = np.linspace(0, 10, 500)
    f = lam * np.exp(-lam * t)
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(t, f, color=BLEU, lw=2.4)
    m = t <= 3
    ax.fill_between(t[m], f[m], color=BLEU, alpha=0.25, lw=0)
    ax.text(1.2, 0.03, "aire = 0,777\n(77,7 %)", color=ENCRE2, fontsize=10, ha="center", va="bottom")
    ax.axvline(3, color=MUET, lw=0.9, ls="--")
    ax.set_xlabel("temps d'attente t avant la prochaine commande (minutes)")
    ax.set_ylabel("densité f(t)")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 0.55)
    save(fig, "ch01-attente-densite.png")


def _gd(grad, theta0, eta, n_iter=1000, tol=1e-8):
    theta = np.array(theta0, dtype=float)
    chemin = [theta.copy()]
    for _ in range(n_iter):
        g = grad(theta)
        if np.linalg.norm(g) < tol:
            break
        theta = theta - eta * g
        chemin.append(theta.copy())
    return theta, np.array(chemin)


def descente_1d():
    f = lambda x: (x - 3) ** 2
    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.2), constrained_layout=True)
    cas = [(0.1, "η = 0,1 : prudent (lent)", 8), (0.4, "η = 0,4 : bien choisi", 8), (1.1, "η = 1,1 : trop grand (diverge)", 6)]
    for ax, (eta, titre, n) in zip(axes, cas):
        xs = [0.0]
        for _ in range(n):
            xs.append(xs[-1] - eta * 2 * (xs[-1] - 3))
        xs = np.array(xs)
        lim = max(abs(xs - 3).max() * 1.15, 3.6)
        grid = np.linspace(3 - lim, 3 + lim, 300)
        ax.plot(grid, f(grid), color=MUET, lw=1.4)
        ax.plot(xs, f(xs), color=ORANGE, lw=1.0, marker="o", ms=4.5)
        ax.scatter([xs[0]], [f(xs[0])], color=BLEU, s=40, zorder=5)
        ax.set_title(titre, fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylim(-0.05 * f(grid).max(), f(grid).max() * 1.05 if f(xs).max() < f(grid).max() else f(xs).max() * 1.05)
    axes[0].set_ylabel("f(x)")
    axes[0].text(0.1, 9.3, "départ", color=BLEU, fontsize=8.5)
    save(fig, "ch01-descente-1d.png")


def descente_2d():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 3.0, 5.0])
    gL = lambda t, X: -2 * X.T @ (y - X @ t)
    LL = lambda t, X: np.sum((y - X @ t) ** 2)
    X = np.column_stack([x, np.ones_like(x)])
    xc = x - x.mean()
    Xc = np.column_stack([xc, np.ones_like(xc)])
    _, ch1 = _gd(lambda t: gL(t, X), [0, 0], 0.05, 5000, 1e-6)
    _, ch2 = _gd(lambda t: gL(t, Xc), [0, 0], 0.15, 5000, 1e-6)
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.0), constrained_layout=True)
    for ax, XX, ch, titre, xr, yr, eta in [
        (axes[0], X, ch1, f"variable brute : {len(ch1) - 1} itérations", (-0.3, 2.3), (-1.0, 3.4), 0.05),
        (axes[1], Xc, ch2, f"variable centrée : {len(ch2) - 1} itérations", (-0.3, 2.3), (-0.5, 4.2), 0.15),
    ]:
        A, B = np.meshgrid(np.linspace(*xr, 250), np.linspace(*yr, 250))
        Lg = np.array([[LL(np.array([a, b]), XX) for a in A[0]] for b in B[:, 0]])
        ax.contour(A, B, Lg, levels=[0.2, 0.5, 1, 2, 4, 8, 16, 32], colors=MUET, linewidths=0.8)
        ax.plot(ch[:, 0], ch[:, 1], color=ORANGE, lw=1.2, marker="o", ms=2.2 if len(ch) > 40 else 4)
        ax.scatter([ch[0, 0]], [ch[0, 1]], color=BLEU, s=40, zorder=5)
        ax.set_title(titre, fontsize=10)
        ax.set_xlabel("a (pente)")
        ax.grid(False)
    axes[0].set_ylabel("b (ordonnée à l'origine)")
    axes[1].set_ylabel("b' (ordonnée en x centré)")
    save(fig, "ch01-descente-2d.png")


def demande_recettes():
    prix = np.array([25, 28, 31, 34, 37, 40, 43, 46], dtype=float)
    ventes = np.array([93, 82, 82, 69, 67, 56, 56, 47], dtype=float)
    beta, alpha = np.polyfit(prix, ventes, 1)
    R = lambda p: p * (alpha + beta * p)
    p_opt = -alpha / (2 * beta)
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.6), constrained_layout=True)
    ax = axes[0]
    pp = np.linspace(22, 49, 100)
    ax.plot(pp, alpha + beta * pp, color=BLEU, lw=2)
    ax.scatter(prix, ventes, color=ORANGE, s=34, zorder=5)
    ax.set_xlabel("prix p (€)")
    ax.set_ylabel("ventes hebdomadaires q")
    ax.text(31.5, 91, "q ≈ 143,9 − 2,11 p", color=ENCRE2, fontsize=9.5)
    ax = axes[1]
    ax.plot(pp, R(pp), color=BLEU, lw=2)
    ax.scatter([p_opt], [R(p_opt)], color=ORANGE, s=40, zorder=5)
    ax.scatter([40], [R(40)], color=MUET, s=40, zorder=5)
    ax.annotate(f"optimum : p* ≈ {p_opt:.1f} €\n{R(p_opt):,.0f} €".replace(",", " ").replace(".", ","), xy=(p_opt, R(p_opt)), xytext=(23, 2560),
                fontsize=9, color=ENCRE2, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    ax.annotate(f"prix actuel : 40 €\n{R(40):,.0f} €".replace(",", " "), xy=(40, R(40)), xytext=(41.5, 2480),
                fontsize=9, color=ENCRE2, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    ax.set_xlabel("prix p (€)")
    ax.set_ylabel("recettes hebdomadaires R(p) (€)")
    ax.set_ylim(1800, 2750)
    save(fig, "ch01-demande-recettes.png")


ALL = {f.__name__: f for f in [ellipse_propre, nuage_clients, svd_ventes, benefice_tangentes, gradient_contours, attente_densite, descente_1d, descente_2d, demande_recettes]}

if __name__ == "__main__":
    names = sys.argv[1:] or list(ALL)
    for n in names:
        ALL[n]()
