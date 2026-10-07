"""Outils du chapitre 7 (écarts, prix-volume-mix) : décomposition d'un écart de chiffre d'affaires ou de marge, partagée par le livre et le cahier."""
import numpy as np
import pandas as pd


def pvm_ca(df, cle, qb="quantite_budget", qr="quantite_reel", cab="ca_budget", car="ca_reel"):
    """Décompose l'écart de CA (réalisé - budget) en effets volume, mix et prix, au grain `cle` (liste de colonnes).
    volume = (Qr - Qb) x prix moyen budget global ; mix = sum (Qr_i - Qr x part_b_i) x Pb_i ; prix = sum Qr_i x (Pr_i - Pb_i).
    Retourne un dict avec les effets et leur somme (qui égale l'écart total à l'arrondi près)."""
    g = df.groupby(cle)[[qb, qr, cab, car]].sum()
    Qb, Qr = g[qb].sum(), g[qr].sum()
    Pb = g[cab] / g[qb]
    Pr = g[car] / g[qr]
    pbg = g[cab].sum() / Qb
    part_b = g[qb] / Qb
    volume = (Qr - Qb) * pbg
    mix = ((g[qr] - Qr * part_b) * Pb).sum()
    prix = (g[qr] * (Pr - Pb)).sum()
    return {"volume": float(volume), "mix": float(mix), "prix": float(prix), "total": float(volume + mix + prix), "ecart": float(g[car].sum() - g[cab].sum())}


def pvm_marge(df, cle, qb="quantite_budget", qr="quantite_reel", mb="marge_budget", mr="marge_reelle"):
    """Même logique pour la marge : volume, mix et marge unitaire (la marge unitaire regroupe prix et coût)."""
    g = df.groupby(cle)[[qb, qr, mb, mr]].sum()
    Qb, Qr = g[qb].sum(), g[qr].sum()
    ub = g[mb] / g[qb]
    ur = g[mr] / g[qr]
    ubg = g[mb].sum() / Qb
    part_b = g[qb] / Qb
    volume = (Qr - Qb) * ubg
    mix = ((g[qr] - Qr * part_b) * ub).sum()
    unit = (g[qr] * (ur - ub)).sum()
    return {"volume": float(volume), "mix": float(mix), "marge_unitaire": float(unit), "total": float(volume + mix + unit), "ecart": float(g[mr].sum() - g[mb].sum())}


# ----------------------------------------------------------------------------------------------- figures
def cascade(nom, etapes, titre, unite="€", ylabel=None):
    """Cascade (waterfall) : `etapes` = liste (libellé, valeur) ; la première et la dernière sont des totaux, les autres des effets."""
    import matplotlib.pyplot as plt
    from style import setup, save, BLEU, ORANGE, AQUA, ROUGE, MUET
    setup()
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    cum = 0.0
    n = len(etapes)
    for i, (lib, v) in enumerate(etapes):
        if i == 0 or i == n - 1:
            ax.bar(i, v if i == 0 else cum, color=MUET if i == 0 else BLEU, width=0.6)
            haut = v if i == 0 else cum
            ax.text(i, haut, f"{haut / 1000:,.1f} k{unite}".replace(",", " ").replace(".", ","), ha="center", va="bottom", fontsize=8)
            if i == 0:
                cum = v
        else:
            bas = cum if v >= 0 else cum + v
            ax.bar(i, abs(v), bottom=bas, color=AQUA if v >= 0 else ROUGE, width=0.6)
            ax.text(i, max(cum, cum + v), f"{v / 1000:+,.1f}".replace(",", " ").replace(".", ","), ha="center", va="bottom", fontsize=8)
            cum += v
    ax.set_xticks(range(n)); ax.set_xticklabels([e[0] for e in etapes], fontsize=8)
    lo = min(etapes[0][1], cum) * 0.9
    ax.set_ylim(lo, max(etapes[0][1], cum) * 1.05 + 1)
    ax.set_ylabel((ylabel or f"k{unite}") + " (axe tronqué)"); ax.set_title(titre, loc="left")
    ax.yaxis.set_major_formatter(lambda x, p: f"{x / 1000:,.0f}".replace(",", " "))
    save(fig, nom)


def ishikawa(nom, branches, effet, titre=None):
    """Diagramme d'Ishikawa (arête de poisson) dessiné : `branches` = {catégorie: [causes]} ; `effet` = texte de la tête."""
    import matplotlib.pyplot as plt
    from style import setup, save, BLEU, ORANGE, MUET, ENCRE2
    setup()
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.set_xlim(0, 11.6); ax.set_ylim(0, 6); ax.axis("off"); ax.grid(False)
    ax.annotate("", xy=(9.6, 3), xytext=(0.3, 3), arrowprops=dict(arrowstyle="-|>", color=ENCRE2, lw=2))
    ax.text(9.7, 3, effet, va="center", ha="left", fontsize=8.5, color="white", bbox=dict(boxstyle="round,pad=0.4", fc=BLEU, ec="none"), wrap=True)
    noms = list(branches)
    h = (len(noms) + 1) // 2
    for k, cat in enumerate(noms):
        haut = k % 2 == 0
        x0 = 2.6 + 2.9 * (k // 2)
        y1 = 5.3 if haut else 0.7
        ax.plot([x0, x0 + 0.9], [y1, 3], color=ORANGE, lw=1.6)
        ax.text(x0 - 0.05, y1 + (0.18 if haut else -0.18), cat, ha="center", va="bottom" if haut else "top", fontsize=8.5, color=ORANGE, fontweight="bold")
        for j, cause in enumerate(branches[cat]):
            f = (j + 1) / (len(branches[cat]) + 1)
            xc = x0 + 0.9 * (1 - (abs(3 - y1) * (1 - f)) / abs(3 - y1)) if False else x0 + 0.9 * f
            yc = y1 + (3 - y1) * f
            ax.plot([xc - 0.5, xc], [yc, yc], color=MUET, lw=0.9)
            ax.text(xc - 0.55, yc, cause, ha="right", va="center", fontsize=6.8)
    if titre:
        ax.set_title(titre, loc="left")
    save(fig, nom)
