"""Figures du chapitre 3. Exécution : python build/fig_ch03.py [nom ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from style import *  # noqa
from donnees import commandes

setup()


def distribution_montants():
    df = commandes()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.25})
    ax = axes[0]
    ax.hist(df.montant, bins=32, color=BLEU, alpha=0.6, edgecolor=SURFACE)
    ax.set_ylim(0, 66)
    m, med = df.montant.mean(), df.montant.median()
    ax.axvline(m, color=ORANGE, lw=2)
    ax.axvline(med, color=VIOLET, lw=2, ls="--")
    ax.text(m + 4, ax.get_ylim()[1] * 0.92, f"moyenne\n{m:.1f}".replace(".", ","), color=ORANGE, fontsize=9)
    ax.text(med - 4, ax.get_ylim()[1] * 0.92, f"médiane\n{med:.1f}".replace(".", ","), color=VIOLET, fontsize=9, ha="right")
    ax.set_xlabel("montant de la commande (€)")
    ax.set_ylabel("nombre de commandes")
    ax.set_title("Distribution des 400 commandes")
    ax = axes[1]
    ordre = ["Réseaux", "Site", "Boutique"]
    data = [df.montant[df.canal == c] for c in ordre]
    bp = ax.boxplot(data, tick_labels=ordre, patch_artist=True, widths=0.55,
                    medianprops=dict(color=ENCRE, lw=1.6), flierprops=dict(marker="o", markersize=3, markerfacecolor=MUET, markeredgecolor="none"))
    for patch, c in zip(bp["boxes"], [BLEU, ORANGE, AQUA]):
        patch.set_facecolor(c); patch.set_alpha(0.45); patch.set_edgecolor(ENCRE2)
    ax.set_ylabel("montant (€)")
    ax.set_title("Montant selon le canal")
    ax.grid(axis="x", visible=False)
    save(fig, "ch03-distribution-montants.png")


def anscombe():
    x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
    ys = [[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
          [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
          [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
          [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]]
    xs = [x, x, x, [8] * 7 + [19] + [8] * 3]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.0), sharex=True, sharey=True, gridspec_kw={"wspace": 0.1})
    for ax, a, b, t in zip(axes, xs, ys, "IIIIIIIV".replace("III", "III").split() or ["I", "II", "III", "IV"]):
        pass
    for ax, a, b, t in zip(axes, xs, ys, ["I", "II", "III", "IV"]):
        ax.scatter(a, b, color=BLEU, s=22)
        pente, ord_ = np.polyfit(a, b, 1)
        xx = np.array([3, 20])
        ax.plot(xx, pente * xx + ord_, color=ORANGE, lw=1.6)
        ax.set_title(f"jeu {t}")
        ax.set_xlim(2, 20); ax.set_ylim(2, 14)
    save(fig, "ch03-anscombe.png")


def vraisemblance():
    p = np.linspace(0.01, 0.99, 400)
    k, n = 7, 20
    L = p**k * (1 - p) ** (n - k)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), gridspec_kw={"wspace": 0.28})
    for ax, y, titre, yl in [(axes[0], L, "Vraisemblance L(p)", "L(p)"),
                             (axes[1], np.log(L), "Log-vraisemblance ln L(p)", "ln L(p)")]:
        ax.plot(p, y, color=BLEU)
        ax.axvline(k / n, color=ORANGE, ls="--", lw=1.4)
        ax.plot([k / n], [y[np.argmin(abs(p - k / n))]], "o", color=ORANGE)
        ax.set_xlabel("valeur candidate de p")
        ax.set_ylabel(yl)
        ax.set_title(titre)
    axes[1].set_ylim(-40, -10)
    axes[0].text(0.52, L.max() * 0.6, "maximum en p̂ = 7/20 = 0,35", color=ENCRE2, fontsize=9)
    save(fig, "ch03-vraisemblance.png")


def biais_variance():
    rng = np.random.default_rng(3)
    x = rng.normal(0, 1, size=(100000, 5))
    v_n = x.var(axis=1, ddof=0)
    v_n1 = x.var(axis=1, ddof=1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3), sharey=True, gridspec_kw={"wspace": 0.08})
    bins = np.linspace(0, 6, 60)
    for ax, v, t, c in [(axes[0], v_n, "diviser par n", ORANGE), (axes[1], v_n1, "diviser par n − 1", BLEU)]:
        ax.hist(v, bins=bins, density=True, color=c, alpha=0.55, edgecolor="none")
        ax.axvline(1, color=ENCRE, lw=1.4, ls="--")
        ax.axvline(v.mean(), color=c, lw=2)
        ax.set_title(f"{t} : moyenne = {v.mean():.2f}".replace(".", ","))
        ax.set_xlabel("estimation de la variance (vraie valeur = 1)")
        ax.set_yticks([])
        ax.grid(False)
    save(fig, "ch03-biais-variance.png")


def couverture():
    from donnees import commandes
    rng = np.random.default_rng(21)
    pop = commandes().montant.to_numpy()
    mu = pop.mean()
    n, N = 40, 60
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    rates = 0
    for i in range(N):
        e = rng.choice(pop, size=n, replace=False)
        m = e.mean(); se = e.std(ddof=1) / np.sqrt(n)
        t = stats.t.ppf(0.975, n - 1)
        lo, hi = m - t * se, m + t * se
        ok = lo <= mu <= hi
        rates += ok
        ax.plot([lo, hi], [i, i], color=BLEU if ok else ROUGE, lw=1.8 if ok else 2.4)
        ax.plot([m], [i], "o", color=BLEU if ok else ROUGE, ms=3)
    ax.axvline(mu, color=ENCRE, lw=1.4, ls="--")
    ax.text(mu + 0.8, N + 0.5, "vraie moyenne 60,25", color=ENCRE2, fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel("montant moyen (€)")
    ax.set_ylim(-1, N + 3)
    ax.set_title(f"{N} intervalles à 95 % : {N - rates} ratent la vraie valeur (en rouge)")
    ax.grid(axis="y", visible=False)
    save(fig, "ch03-couverture.png")


def test_rejet():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.5), gridspec_kw={"wspace": 0.2})
    x = np.linspace(-4.5, 4.5, 600)
    d = stats.t(399)
    for ax, tobs, titre in [(axes[0], 2.76, "t observé = 2,76 : on rejette H₀"), (axes[1], 1.1, "t observé = 1,10 : on ne rejette pas H₀")]:
        ax.plot(x, d.pdf(x), color=ENCRE2, lw=1.6)
        crit = d.ppf(0.975)
        for lo, hi in [(-4.5, -crit), (crit, 4.5)]:
            m = (x >= lo) & (x <= hi)
            ax.fill_between(x[m], d.pdf(x[m]), color=ORANGE, alpha=0.55)
        ax.axvline(tobs, color=BLEU, lw=2)
        ax.text(tobs + 0.12, 0.30, "valeur\nobservée", color=BLEU, fontsize=9)
        ax.text(0, 0.17, "zone de non-rejet\n95 %", ha="center", color=ENCRE2, fontsize=9)
        ax.text(3.3, 0.07, "rejet\n2,5 %", ha="center", color=ENCRE2, fontsize=9)
        ax.text(-3.3, 0.07, "rejet\n2,5 %", ha="center", color=ENCRE2, fontsize=9)
        ax.set_title(titre)
        ax.set_xlabel("statistique de test t (si H₀ est vraie)")
        ax.set_yticks([])
        ax.set_ylim(0, 0.45)
        ax.grid(False)
    save(fig, "ch03-test-rejet.png")


def puissance():
    n = np.arange(50, 6001, 25)
    za = stats.norm.ppf(0.975)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), gridspec_kw={"wspace": 0.25})
    ax = axes[0]
    for delta, c in [(0.02, VIOLET), (0.03, BLEU), (0.05, ORANGE)]:
        p1, p2 = 0.12, 0.12 + delta
        se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
        pw = stats.norm.cdf(delta / se - za)
        ax.plot(n, pw, color=c, label=f"+{int(delta*100)} points (12 % → {int(round((0.12+delta)*100))} %)")
    ax.axhline(0.8, color=MUET, ls="--", lw=1)
    ax.text(5900, 0.82, "80 %", ha="right", color=ENCRE2, fontsize=9)
    ax.set_xlabel("visiteurs par version (n)")
    ax.set_ylabel("puissance")
    ax.set_title("Puissance d'un test A/B (α = 5 %)")
    ax.legend(loc="lower right", fontsize=9)
    ax.set_ylim(0, 1.02)
    ax = axes[1]
    rng = np.random.default_rng(8)
    n_pk, n_sim = 20, 4000
    x = rng.normal(size=(n_sim, n_pk * 50))
    # peeking : on regarde le test t (moyenne = 0) tous les 50 obs
    ks = np.arange(1, n_pk + 1) * 50
    cs = np.cumsum(x, axis=1)
    z = np.stack([cs[:, k - 1] / np.sqrt(k) for k in ks], axis=1)
    ever = np.maximum.accumulate((np.abs(z) > 1.96), axis=1).mean(axis=0)
    ax.plot(np.arange(1, n_pk + 1), ever, color=ROUGE)
    ax.axhline(0.05, color=MUET, ls="--", lw=1)
    ax.text(n_pk, 0.07, "seuil nominal 5 %", ha="right", color=ENCRE2, fontsize=9)
    ax.set_xlabel("nombre de « coups d'œil » aux résultats")
    ax.set_ylabel("proportion de faux positifs")
    ax.set_title("Regarder trop souvent gonfle les faux positifs")
    ax.set_ylim(0, 0.5)
    save(fig, "ch03-puissance.png")


if __name__ == "__main__":
    noms = sys.argv[1:] or [n for n, f in list(globals().items()) if callable(f) and getattr(f, "__module__", None) == "__main__"]
    for n in noms:
        globals()[n]()
