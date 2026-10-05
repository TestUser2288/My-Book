"""Figures du chapitre 2. Exécution : python build/fig_ch02.py [nom ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from style import *  # noqa

setup()


def lois_discretes():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={"wspace": 0.3})
    ax = axes[0]
    k = np.arange(0, 13)
    ax.bar(k, stats.binom(20, 0.2).pmf(k), color=BLEU, width=0.7)
    ax.set_title("Binomiale(20 ; 0,2) : acheteurs sur 20 visiteurs")
    ax.set_xlabel("nombre d'acheteurs k")
    ax.set_ylabel("P(X = k)")
    ax.annotate("le plus probable :\n4 acheteurs (21,8 %)", xy=(4, 0.218), xytext=(7, 0.19),
                color=ENCRE2, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    ax = axes[1]
    k = np.arange(0, 13)
    ax.bar(k, stats.poisson(3).pmf(k), color=ORANGE, width=0.7)
    ax.set_title("Poisson(3) : commandes en une heure")
    ax.set_xlabel("nombre de commandes k")
    ax.set_ylabel("P(X = k)")
    save(fig, "ch02-lois-discretes.png")


def lois_continues():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.4), gridspec_kw={"wspace": 0.4})
    x = np.linspace(-0.5, 10.5, 400)
    ax = axes[0]
    xs = np.linspace(-1, 11, 400)
    ax.plot(xs, stats.uniform(0, 10).pdf(xs), color=BLEU)
    ax.fill_between(xs, stats.uniform(0, 10).pdf(xs), color=BLEU, alpha=0.15)
    ax.set_title("Uniforme sur [0 ; 10]")
    ax.set_ylim(0, 0.3)
    ax.set_xlabel("x")
    ax.set_ylabel("densité")
    ax = axes[1]
    xe = np.linspace(0, 10, 400)
    ax.plot(xe, stats.expon(scale=2).pdf(xe), color=ORANGE)
    ax.fill_between(xe, stats.expon(scale=2).pdf(xe), color=ORANGE, alpha=0.15)
    ax.set_title("Exponentielle (λ = 0,5)")
    ax.set_xlabel("temps d'attente (min)")
    ax = axes[2]
    xn = np.linspace(60, 180, 400)
    ax.plot(xn, stats.norm(120, 15).pdf(xn), color=AQUA)
    ax.fill_between(xn, stats.norm(120, 15).pdf(xn), color=AQUA, alpha=0.15)
    ax.set_title("Normale (μ = 120, σ = 15)")
    ax.set_xlabel("ventes du jour")
    save(fig, "ch02-lois-continues.png")


def normale_zones():
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    x = np.linspace(60, 180, 600)
    d = stats.norm(120, 15)
    ax.plot(x, d.pdf(x), color=ENCRE2, lw=1.6)
    m = (x >= 105) & (x <= 135)
    ax.fill_between(x[m], d.pdf(x[m]), color=BLEU, alpha=0.35)
    t = x >= 150
    ax.fill_between(x[t], d.pdf(x[t]), color=ORANGE, alpha=0.7)
    ax.text(120, 0.012, "68,3 %\n(μ ± σ)", ha="center", color=ENCRE, fontsize=10)
    ax.annotate("P(X > 150) ≈ 2,3 %", xy=(155, 0.0012), xytext=(150, 0.014), color=ENCRE2,
                fontsize=10, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
    ax.set_xlabel("ventes du jour")
    ax.set_ylabel("densité")
    ax.set_xticks([75, 90, 105, 120, 135, 150, 165])
    save(fig, "ch02-normale-zones.png")


def correlations():
    rng = np.random.default_rng(5)
    n = 250
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.0), gridspec_kw={"wspace": 0.25})
    def corr(rho):
        z = rng.normal(size=(n, 2))
        return z[:, 0], rho * z[:, 0] + np.sqrt(1 - rho**2) * z[:, 1]
    cas = [("ρ = 0,9", corr(0.9)), ("ρ = 0,5", corr(0.5)), ("ρ = 0", corr(0.0)), ("ρ = −0,9", corr(-0.9))]
    x = rng.uniform(-2, 2, n)
    cas[2] = ("ρ ≈ 0, mais dépendants", (x, x**2 + rng.normal(0, 0.15, n)))
    cas = [cas[0], cas[1], cas[3], cas[2]]
    for ax, (titre, (a, b)) in zip(axes, cas):
        ax.scatter(a, b, s=9, color=BLEU, alpha=0.7, linewidths=0)
        ax.set_title(titre if "≈" not in titre else "ρ ≈ 0 et pourtant dépendants")
        ax.set_xticks([]); ax.set_yticks([])
        ax.grid(False)
        if "≈" not in titre:
            ax.set_title(f"ρ mesuré = {np.corrcoef(a, b)[0, 1]:+.2f}".replace(".", ","))
        else:
            ax.set_title(f"ρ mesuré = {np.corrcoef(a, b)[0, 1]:+.2f} (dépendance en U)".replace(".", ","))
    save(fig, "ch02-correlations.png")


def lgn():
    rng = np.random.default_rng(12)
    n = 5000
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw={"wspace": 0.25})
    ax = axes[0]
    k = np.arange(1, n + 1)
    cols = [BLEU, ORANGE, AQUA, VIOLET]
    for i, c in enumerate(cols):
        x = rng.random(n) < 0.205
        ax.plot(k, np.cumsum(x) / k, color=c, lw=1.2, alpha=0.9)
    ax.axhline(0.205, color=ENCRE2, lw=1, ls="--")
    ax.text(n * 0.98, 0.08, "pointillés : vraie valeur 0,205", ha="right", color=ENCRE2, fontsize=9)
    ax.set_xscale("log")
    ax.set_ylim(0, 0.6)
    ax.set_xlabel("nombre de visiteurs observés (échelle log)")
    ax.set_ylabel("proportion d'acheteurs")
    ax.set_title("Loi des grands nombres : 4 expériences")
    ax = axes[1]
    for i, c in enumerate([BLEU, ORANGE, AQUA]):
        x = rng.standard_cauchy(n)
        ax.plot(k, np.cumsum(x) / k, color=c, lw=1.2)
    ax.set_xscale("log")
    ax.set_ylim(-12, 12)
    ax.set_xlabel("nombre d'observations (échelle log)")
    ax.set_ylabel("moyenne cumulée")
    ax.set_title("Quand ça ne marche pas : loi de Cauchy")
    save(fig, "ch02-lgn.png")


def tcl():
    rng = np.random.default_rng(4)
    fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.0), gridspec_kw={"wspace": 0.18}, sharey=False)
    for ax, n in zip(axes, (1, 2, 10, 50)):
        m = rng.exponential(1.0, size=(20000, n)).mean(axis=1)
        ax.hist(m, bins=45, density=True, color=BLEU, alpha=0.55, edgecolor="none")
        xs = np.linspace(max(0, m.min()), m.max(), 300)
        ax.plot(xs, stats.norm(1, 1 / np.sqrt(n)).pdf(xs), color=ORANGE, lw=1.8)
        ax.set_title(f"moyenne de n = {n}")
        ax.set_yticks([])
        ax.grid(False)
    save(fig, "ch02-tcl.png")


if __name__ == "__main__":
    noms = sys.argv[1:] or [n for n, f in list(globals().items()) if callable(f) and f.__module__ == "__main__" and n not in ("setup", "save")]
    for n in noms:
        globals()[n]()
