#!/usr/bin/env python3
"""Outils du chapitre 6 (réassurance) : appelés depuis des blocs cachés du livre et du cahier.

Contenu : lecture des données (`sinistres_gros.csv`, `cat_annuel.csv`), prix de tranches (empirique, GPD, vérité programmée),
simulation de la charge annuelle, évaluation de programmes de réassurance, et figures du chapitre.
La « vérité » est celle de `donnees5.py` : sinistres = 96 % lognormale(10,2 ; 1,5) + 4 % GPD (ξ = 0,55, β = 300 000) au-delà de 500 000 € ;
fréquence 160·1,03^(année−2010) ; catastrophes : 45 % d'années avec événement, Pareto (minimum 2 M€, alpha = 1/0,9).
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import integrate, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style  # noqa: E402
from style import AQUA, BLEU, ENCRE, ENCRE2, MUET, ORANGE, ROUGE, VIOLET  # noqa: E402

style.setup()
DONNEES = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
ANNEES = np.arange(2010, 2025)
CROISSANCE = 0.03                                   # croissance annuelle de l'exposition (vérité programmée)
LAMBDA_2025 = 160 * (1 + CROISSANCE) ** 15          # nombre de sinistres attendu au niveau d'exposition de 2025
COUCHES = [(5e5, 5e5), (1e6, 1e6), (2e6, 2e6)]      # (priorité, portée) des trois tranches « par risque »


def charger():
    sg = pd.read_csv(os.path.join(DONNEES, "sinistres_gros.csv"))
    cat = pd.read_csv(os.path.join(DONNEES, "cat_annuel.csv"))
    return sg, cat


def tranche(x, a, L):
    """part du sinistre x à la charge de la tranche « L xs a » : min(max(x − a, 0), L)"""
    return np.minimum(np.maximum(np.asarray(x, dtype=float) - a, 0.0), L)


def _fr(x):
    """nombre de M€ avec virgule décimale : 0,5 ; 1 ; 2"""
    return f"{x / 1e6:g}".replace(".", ",")


def facteur_2025(annee):
    """coefficient qui ramène une année d'exposition passée au niveau de 2025"""
    return (1 + CROISSANCE) ** (2025 - np.asarray(annee))


# ------------------------------------------------------------------------------------------------ prix de tranches
def burning_cost(sg, a, L, ajuste=True):
    """moyenne annuelle (au niveau d'exposition 2025 si `ajuste`) de la charge de la tranche, par la méthode du « burning cost »"""
    par_an = sg.assign(c=tranche(sg["montant"], a, L)).groupby("annee_survenance")["c"].sum().reindex(ANNEES, fill_value=0.0)
    v = par_an.values * (facteur_2025(ANNEES) if ajuste else 1.0)
    return v.mean(), par_an.values


def taux_depassement(sg, u):
    """nombre annuel de sinistres au-delà de u, ramené à l'exposition 2025"""
    n = sg[sg["montant"] > u].groupby("annee_survenance").size().reindex(ANNEES, fill_value=0).values
    return (n * facteur_2025(ANNEES)).mean()


def ajuster_gpd(sg, u):
    e = sg["montant"].values[sg["montant"].values > u] - u
    xi, _, beta = stats.genpareto.fit(e, floc=0)
    return xi, beta, len(e)


def prix_gpd(a, L, u, xi, beta, lam_u):
    """E[min(max(X−a,0),L)] × λ_u pour une queue GPD au-delà de u (a ≥ u) : λ_u · ∫_a^{a+L} S(x) dx"""
    if abs(xi) < 1e-9:
        i = beta * (np.exp(-(a - u) / beta) - np.exp(-(a + L - u) / beta))
    else:
        i = beta / (1 - xi) * ((1 + xi * (a - u) / beta) ** (1 - 1 / xi) - (1 + xi * (a + L - u) / beta) ** (1 - 1 / xi))
    return lam_u * i


def _survie_vraie(x):
    corps = stats.norm.sf((np.log(x) - 10.2) / 1.5)
    q = np.where(x <= 5e5, 1.0, (1 + 0.55 * (x - 5e5) / 3e5) ** (-1 / 0.55))
    return 0.96 * corps + 0.04 * q


def prix_vrai(a, L):
    """vérité programmée : λ_2025 · ∫_a^{a+L} S(x) dx (intégration numérique)"""
    val, _ = integrate.quad(_survie_vraie, a, a + L, limit=200)
    return LAMBDA_2025 * val


def prix_vrai_cat(a, L, p=0.45, xm=2e6, alpha=1 / 0.9):
    """vérité programmée des catastrophes : p · ∫_a^{a+L} (xm/x)^alpha dx (a ≥ xm)"""
    return p * xm ** alpha / (1 - alpha) * ((a + L) ** (1 - alpha) - a ** (1 - alpha))


def bootstrap_annees(sg, a, L, B=500, seed=7):
    """bootstrap par années entières : on retire 15 années avec remise ; renvoie B burning costs ajustés"""
    rng = np.random.default_rng(seed)
    par_an = [sg.loc[sg["annee_survenance"] == y, "montant"].values for y in ANNEES]
    c = np.array([tranche(v, a, L).sum() for v in par_an]) * facteur_2025(ANNEES)
    idx = rng.integers(0, len(ANNEES), (B, len(ANNEES)))
    return c[idx].mean(axis=1)


def pareto_cat(cat, xm=2e6):
    nz = cat["perte_cat"].values[cat["perte_cat"].values > 0]
    alpha = len(nz) / np.log(nz / xm).sum()
    return alpha, len(nz) / len(cat)


def prix_pareto(a, L, p, alpha, xm=2e6):
    if abs(alpha - 1) < 1e-9:
        return p * xm * np.log((a + L) / a)
    return p * xm ** alpha / (1 - alpha) * ((a + L) ** (1 - alpha) - a ** (1 - alpha))


# ------------------------------------------------------------------------------------------------ simulation de la charge annuelle
def simuler(N=20000, seed=2026, avec_cat=False):
    """charge annuelle brute au niveau d'exposition 2025 : Poisson(λ_2025) sinistres tirés avec remise dans les sinistres observés"""
    sg, cat = charger()
    rng = np.random.default_rng(seed)
    n = rng.poisson(LAMBDA_2025, N)
    idx = np.repeat(np.arange(N), n)
    cl = rng.choice(sg["montant"].values, n.sum())
    out = {"N": N, "idx": idx, "sinistres": cl, "brute": np.bincount(idx, weights=cl, minlength=N)}
    out["cat"] = rng.choice(cat["perte_cat"].values, N) if avec_cat else np.zeros(N)
    return out


def agreger(sim, v):
    return np.bincount(sim["idx"], weights=v, minlength=sim["N"])


def evaluer(res, res0):
    """indicateurs d'un résultat annuel `res` : moyenne, écart-type, quantile 0,5 %, K = E − q0,5 % (perte inattendue à 99,5 %), ruine"""
    q = np.percentile(res, 0.5)
    return {"moyenne": res.mean(), "ecart_type": res.std(), "q05pct": q, "K": res.mean() - q}


# ------------------------------------------------------------------------------------------------ simulations « sous la vérité »
def tirer_sinistres_vrais(rng, n):
    """n sinistres tirés dans la vérité programmée (mélange lognormale + GPD)"""
    corps = np.exp(rng.normal(10.2, 1.5, n))
    gpd = 500000 + 300000 / 0.55 * ((1 - rng.random(n)) ** (-0.55) - 1)
    return np.where(rng.random(n) < 0.04, gpd, corps)


def rejouer_experience(B=300, seed=99):
    """rejoue B fois « quinze années d'observation » sous la vérité et calcule les burning costs bruts et ajustés des trois tranches"""
    rng = np.random.default_rng(seed)
    ajuste = np.zeros((B, 3))
    brut = np.zeros((B, 3))
    for b in range(B):
        for i, y in enumerate(ANNEES):
            x = tirer_sinistres_vrais(rng, rng.poisson(160 * (1 + CROISSANCE) ** i))
            for j, (a, L) in enumerate(COUCHES):
                c = tranche(x, a, L).sum()
                ajuste[b, j] += c * facteur_2025(y) / len(ANNEES)
                brut[b, j] += c / len(ANNEES)
    return ajuste, brut


def charge_annuelle_vraie(a, L, N=20000, seed=5):
    """charge annuelle d'une tranche sous la vérité, au niveau d'exposition 2025 (N années simulées)"""
    rng = np.random.default_rng(seed)
    n = rng.poisson(LAMBDA_2025, N)
    idx = np.repeat(np.arange(N), n)
    x = tirer_sinistres_vrais(rng, n.sum())
    return np.bincount(idx, weights=tranche(x, a, L), minlength=N)


def lev_empirique(x, d):
    """espérance limitée E[min(X, d)] des sinistres observés"""
    return np.minimum(x, d).mean()


def tirer_cat(rng, N, p=0.45, alpha=1 / 0.9, xm=2e6):
    """N années de pertes de catastrophe : événement avec probabilité p, puis Pareto(xm, alpha)"""
    return np.where(rng.random(N) < p, xm * (1 - rng.random(N)) ** (-1 / alpha), 0.0)


# ------------------------------------------------------------------------------------------------ figures
def fig_formes():
    X = np.array([30, 45, 80, 120, 250, 600, 900, 2000.])
    cap = np.array([200, 300, 500, 800, 1000, 2500, 3000, 5000.])
    qp = 0.3 * X
    taux = np.maximum(0, 1 - 1000 / cap)
    pl = taux * X
    xl = tranche(X, 500, 500)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)
    for ax, ced, titre in zip(axs, [qp, pl, xl], ["Quote-part 30 %", "Excédent de plénitude (1 000)", "Excédent de sinistre 500 xs 500"]):
        i = np.arange(8)
        ax.bar(i, X - ced, color=BLEU, label="gardé")
        ax.bar(i, ced, bottom=X - ced, color=ORANGE, label="cédé")
        ax.set_xticks(i)
        ax.set_xticklabels([f"{int(v)}" for v in X], fontsize=8)
        ax.set_title(f"{titre}\ncédé : {ced.sum():,.0f} k€".replace(",", " "), fontsize=9.5)
        ax.set_xlabel("sinistre (k€)")
        ax.grid(axis="x", visible=False)
    axs[0].set_ylabel("montant (k€)")
    axs[0].legend(loc="upper left")
    style.save(fig, "ch06-formes.png")


def fig_burning(sg):
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3), sharex=True)
    for ax, (a, L) in zip(axs, COUCHES):
        _, brut = burning_cost(sg, a, L, ajuste=False)
        adj = brut * facteur_2025(ANNEES)
        ax.bar(ANNEES - 0.2, brut / 1e6, width=0.4, color="#c3c2b7", label="brut")
        ax.bar(ANNEES + 0.2, adj / 1e6, width=0.4, color=BLEU, label="exposition 2025")
        ax.axhline(prix_vrai(a, L) / 1e6, color=ORANGE, ls="--", lw=1.6, label="vérité programmée")
        ax.set_title(f"{_fr(L)} M€ xs {_fr(a)} M€", fontsize=10)
        ax.set_xticks([2010, 2015, 2020, 2024])
        ax.grid(axis="x", visible=False)
    axs[0].set_ylabel("charge annuelle de la tranche (M€)")
    axs[0].set_ylim(0, 8.6)
    axs[0].legend(loc="upper left", fontsize=8, ncol=1)
    style.save(fig, "ch06-burning.png")


def fig_gpd(sg):
    x = sg["montant"].values
    us = np.linspace(2e5, 1.6e6, 29)
    me = np.array([(x[x > u] - u).mean() for u in us])
    xis, ses, ns = [], [], []
    for u in us:
        xi, _, n = ajuster_gpd(sg, u)
        xis.append(xi); ns.append(n); ses.append((1 + xi) / np.sqrt(n))
    xis, ses = np.array(xis), np.array(ses)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.5))
    axs[0].plot(us / 1e6, me / 1e6, color=BLEU)
    axs[0].set_xlabel("seuil u (M€)")
    axs[0].set_ylabel("excès moyen au-delà de u (M€)")
    axs[0].set_title("Excès moyen au-delà de u (pente croissante : queue lourde)", fontsize=9)
    axs[1].fill_between(us / 1e6, xis - 1.96 * ses, xis + 1.96 * ses, color=BLEU, alpha=0.18)
    axs[1].plot(us / 1e6, xis, color=BLEU)
    axs[1].axhline(0.55, color=ORANGE, ls="--", lw=1.6)
    axs[1].text(1.6, 0.57, "vérité de la queue : 0,55", color=ORANGE, ha="right", fontsize=8.5)
    axs[1].set_xlabel("seuil u (M€)")
    axs[1].set_ylabel("indice de queue estimé ξ")
    axs[1].set_title("Stabilité de ξ selon le seuil (bande : ± 1,96 écart-type)", fontsize=9)
    style.save(fig, "ch06-gpd.png")


def calcul_tranches(sg):
    """tableau des estimations (M€) : brut, ajusté, intervalle bootstrap, GPD (seuil 500 000), vérité"""
    xi, beta, _ = ajuster_gpd(sg, 5e5)
    lam = taux_depassement(sg, 5e5)
    lignes = []
    for a, L in COUCHES:
        boot = bootstrap_annees(sg, a, L)
        lignes.append({"tranche": f"{_fr(L)} xs {_fr(a)}", "brut": burning_cost(sg, a, L, False)[0] / 1e6,
                       "ajuste": burning_cost(sg, a, L, True)[0] / 1e6, "ic_bas": np.percentile(boot, 2.5) / 1e6,
                       "ic_haut": np.percentile(boot, 97.5) / 1e6, "gpd": prix_gpd(a, L, 5e5, xi, beta, lam) / 1e6,
                       "vrai": prix_vrai(a, L) / 1e6})
    return pd.DataFrame(lignes)


def fig_tranches(sg):
    t = calcul_tranches(sg)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.4))
    for ax, (_, r) in zip(axs, t.iterrows()):
        ax.axhline(r["vrai"], color=ORANGE, ls="--", lw=1.6)
        ax.errorbar([1], [r["ajuste"]], yerr=[[r["ajuste"] - r["ic_bas"]], [r["ic_haut"] - r["ajuste"]]], fmt="o", color=BLEU, capsize=4)
        ax.plot([0], [r["brut"]], "o", color=MUET)
        ax.plot([2], [r["gpd"]], "s", color=VIOLET)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["brut", "ajusté\n(+ intervalle)", "GPD"], fontsize=8.5)
        ax.set_xlim(-0.6, 2.6)
        ax.set_ylim(0, max(r["ic_haut"], r["vrai"]) * 1.25)
        ax.set_title(f"{r['tranche']} (M€)", fontsize=10)
        ax.grid(axis="x", visible=False)
    axs[0].set_ylabel("charge annuelle attendue (M€)")
    axs[2].text(2.55, axs[2].get_ylim()[1] * 0.05, "ligne orange : vérité", color=ORANGE, ha="right", fontsize=8.5)
    style.save(fig, "ch06-tranches.png")


def calcul_cat(cat, B=2000, seed=11):
    c = cat["perte_cat"].values
    alpha, p = pareto_cat(cat)
    rng = np.random.default_rng(seed)
    lignes = []
    for a, L in [(5e6, 5e6), (1e7, 1e7), (2e7, 2e7)]:
        bs = np.array([tranche(rng.choice(c, len(c)), a, L).mean() for _ in range(B)])
        lignes.append({"tranche": f"{_fr(L)} xs {_fr(a)}", "empirique": tranche(c, a, L).mean() / 1e6,
                       "pareto": prix_pareto(a, L, p, alpha) / 1e6, "vrai": prix_vrai_cat(a, L) / 1e6,
                       "ic_bas": np.percentile(bs, 2.5) / 1e6, "ic_haut": np.percentile(bs, 97.5) / 1e6})
    return pd.DataFrame(lignes), alpha, p


def fig_cat(cat):
    c = cat["perte_cat"].values
    nz = np.sort(c[c > 0])[::-1]
    t, alpha, p = calcul_cat(cat)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.5))
    rang = np.arange(1, len(nz) + 1) / len(nz)
    axs[0].loglog(nz / 1e6, rang, "o", color=BLEU, ms=5, label="observé (17 événements)")
    xs = np.linspace(2, 40, 100)
    axs[0].loglog(xs, (2 / xs) ** alpha, color=VIOLET, label=f"Pareto ajusté (alpha = {alpha:.2f})".replace(".", ","))
    axs[0].loglog(xs, (2 / xs) ** (1 / 0.9), color=ORANGE, ls="--", label="vérité (alpha = 1,11)")
    axs[0].set_xticks([2, 5, 10, 20, 40]); axs[0].set_xticklabels(["2", "5", "10", "20", "40"]); axs[0].minorticks_off()
    axs[0].set_yticks([0.05, 0.1, 0.2, 0.5, 1]); axs[0].set_yticklabels(["5 %", "10 %", "20 %", "50 %", "100 %"])
    axs[0].set_xlabel("perte d'un événement (M€, échelle log)")
    axs[0].set_ylabel("part des événements au-delà")
    axs[0].legend(fontsize=8, loc="lower left")
    axs[0].set_title("Queue des événements : peu de points, beaucoup d'incertitude", fontsize=9)
    ypos = np.arange(3)
    for i, r in t.iterrows():
        axs[1].plot([r["ic_bas"], r["ic_haut"]], [i, i], color=BLEU, lw=3, alpha=0.35)
        axs[1].plot(r["empirique"], i, "o", color=BLEU)
        axs[1].plot(r["pareto"], i, "s", color=VIOLET)
        axs[1].plot(r["vrai"], i, "D", color=ORANGE)
    axs[1].set_yticks(ypos)
    axs[1].set_yticklabels(list(t["tranche"]))
    axs[1].set_xlabel("charge annuelle attendue (M€) ; tranches « portée xs priorité » en M€")
    axs[1].set_title("Bleu : observé (bande : bootstrap) · violet : Pareto · orange : vérité", fontsize=9)
    axs[1].grid(axis="y", visible=False)
    style.save(fig, "ch06-cat.png")


def fig_programmes(res0, programmes):
    """programmes : dict nom -> (résultat annuel net, coût, ΔK)"""
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.7))
    bins = np.linspace(-16e6, 12e6, 70)
    couleurs = {"aucune": MUET, "XL 1 M xs 1 M": BLEU, "quote-part 20 %": AQUA, "stop-loss": ORANGE}
    for nom, col in couleurs.items():
        r = res0 if nom == "aucune" else programmes[nom][0]
        h, e = np.histogram(r, bins=bins, density=True)
        axs[0].plot(0.5 * (e[1:] + e[:-1]) / 1e6, h * 1e6, color=col, label=nom, lw=1.7)
    axs[0].set_xlabel("résultat annuel (M€)")
    axs[0].set_ylabel("densité")
    axs[0].legend(fontsize=8, loc="upper left")
    axs[0].set_title("Distribution du résultat annuel selon le programme", fontsize=9.5)
    xs = np.linspace(0, 1.6, 10)
    axs[1].plot(xs, xs / 0.08, color=MUET, ls="--", lw=1)
    axs[1].text(0.62, 7.4, "au-dessus de la droite : la protection\nvaut son coût au taux de 8 % sur le capital", color=MUET, fontsize=8, ha="left", va="top")
    decal = {"XL 1 M xs 1 M": (6, 9), "XL 0,5 M xs 0,5 M": (6, -16), "quote-part 20 %": (6, 7), "XL 2 M xs 2 M": (6, -12)}
    for nom, (_, cout, dk) in programmes.items():
        axs[1].plot(cout / 1e6, dk / 1e6, "o", color=BLEU)
        dx, dy = decal.get(nom, (6, 5))
        axs[1].annotate(nom, (cout / 1e6, dk / 1e6), xytext=(dx, dy), textcoords="offset points", fontsize=8.5, ha="right" if dx < 0 else "left")
    axs[1].set_xlim(0, 1.6)
    axs[1].set_ylim(0, 8)
    axs[1].set_xlabel("coût de la protection (M€ par an)")
    axs[1].set_ylabel("capital économisé (M€)")
    axs[1].set_title("Que coûte un euro de capital économisé ?", fontsize=9.5)
    style.save(fig, "ch06-programmes.png")


if __name__ == "__main__":
    sg, cat = charger()
    fig_formes(); fig_burning(sg); fig_gpd(sg); fig_tranches(sg); fig_cat(cat)
