"""Figures du chapitre 3 (style commun build/style.py). Chaque fonction écrit un PNG dans figures/."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle  # noqa: E402
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET, GRILLE, AXE, SURFACE, setup, save as _save  # noqa: E402

setup()


def _fr_axes(fig):
    """Virgule décimale et espace fine pour les milliers sur les axes numériques (hors dates et étiquettes fixes)."""
    from matplotlib.ticker import ScalarFormatter, FuncFormatter
    def f(v, _):
        if abs(v - round(v)) < 1e-9:
            t = f"{int(round(v)):,}".replace(",", "\u202f")
        else:
            t = f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")
        return t.replace("-", "\u2212")
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_formatter(), ScalarFormatter):
                axis.set_major_formatter(FuncFormatter(f))


def save(fig, name):  # noqa: F811
    _fr_axes(fig)
    _save(fig, name)


def vir(x, n=0):
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _axe_mois(ax, pas=2, annee=True):
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13, pas)))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: MOIS[mdates.num2date(v).month - 1] + (f"\n{mdates.num2date(v).year}" if (mdates.num2date(v).month == 1 or not annee) else "")))


def _boite(ax, x, y, w, h, titre, texte, couleur, txt_col="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=couleur, ec="none"))
    ax.text(x + w / 2, y + h - 0.07, titre, ha="center", va="top", fontsize=11.5, color=txt_col, fontweight="bold")
    ax.text(x + w / 2, y + h - 0.2, texte, ha="center", va="top", fontsize=9, color=txt_col, linespacing=1.35)


def fig_quatre_questions():
    fig, ax = plt.subplots(figsize=(10.4, 3.7))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    noms = [("Descriptif", "Que s'est-il passé ?", "« 963 commandes\nen janvier 2025 »", BLEU),
            ("Diagnostic", "Pourquoi ?", "« la promotion explique\n+19 % de commandes »", "#256abf"),
            ("Prédictif", "Que va-t-il se passer ?", "« environ 1 014 commandes\nen janvier 2026 »", VIOLET),
            ("Prescriptif", "Que faire ?", "« contactez ces clients,\npas ceux-là »", "#c4430f")]
    w, gap = 0.21, 0.045
    for i, (t, q, ex, c) in enumerate(noms):
        x = 0.01 + i * (w + gap)
        _boite(ax, x, 0.30, w, 0.62, t, f"{q}\n\n{ex}", c)
        if i < 3:
            ax.add_patch(FancyArrowPatch((x + w + 0.004, 0.61), (x + w + gap - 0.004, 0.61), arrowstyle="-|>", mutation_scale=14, color=ENCRE2, lw=1.4))
    ax.annotate("", xy=(0.99, 0.15), xytext=(0.01, 0.15), arrowprops=dict(arrowstyle="-|>", color=MUET, lw=1.2))
    ax.text(0.01, 0.06, "le passé, connu", fontsize=9, color=MUET, ha="left")
    ax.text(0.99, 0.06, "l'action, à décider", fontsize=9, color=MUET, ha="right")
    ax.text(0.5, 0.06, "plus d'hypothèses, plus de valeur possible, plus de risque", fontsize=9, color=MUET, ha="center")
    ax.set_title("Un modèle prédictif répond à la troisième question, pas à la quatrième", loc="left", fontsize=11)
    save(fig, "ch03-quatre-questions.png")


def fig_references(R, M):
    r = R[R["h"] == 1].copy()
    r["date"] = pd.PeriodIndex(r["cible"], freq="M").to_timestamp()
    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    ax.plot(r["date"], r["reel"], color=ENCRE, lw=2.4, marker="o", ms=4)
    series = [("naïf (mois précédent)", ROUGE, "--"), ("saisonnier × croissance", ORANGE, "-"), ("régression de Poisson", BLEU, "-")]
    for nom, c, ls in series:
        ax.plot(r["date"], r[nom], color=c, lw=1.6, ls=ls)
    fin = r.iloc[-1]
    ax.text(fin["date"] + pd.Timedelta(days=12), fin["reel"], "réel", color=ENCRE, va="center", fontsize=9.5, fontweight="bold")
    ax.text(fin["date"] + pd.Timedelta(days=12), r.iloc[-1]["régression de Poisson"] - 55, "Poisson", color=BLEU, va="center", fontsize=9.5)
    ax.text(r["date"].iloc[0] + pd.Timedelta(days=40), 1480, "naïf : il recopie\nle mois d'avant", color=ROUGE, fontsize=9.5, ha="left")
    ax.annotate("saisonnier × croissance", xy=(r["date"].iloc[7], r["saisonnier × croissance"].iloc[7]), xytext=(r["date"].iloc[5], 620), color=ORANGE, fontsize=9.5, ha="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
    _axe_mois(ax, 2)
    ax.set_xlim(r["date"].iloc[0] - pd.Timedelta(days=15), fin["date"] + pd.Timedelta(days=75))
    ax.set_ylim(550, 1950)
    ax.set_ylabel("commandes par mois")
    ax.set_title("Prévues un mois à l'avance, les commandes 2025 sont bien suivies par un modèle qui connaît le calendrier", loc="left", fontsize=10.5)
    save(fig, "ch03-references.png")


def fig_janvier(d, f_promo, f_sans, bas, haut):
    M = d["M"]
    x = M.index.to_timestamp()
    fig, ax = plt.subplots(figsize=(10.2, 4.3))
    ax.plot(x, M.values, color=ENCRE, lw=2, marker="o", ms=3.5)
    t = pd.Timestamp("2026-01-01")
    ax.errorbar([t], [f_promo], yerr=[[f_promo - bas], [haut - f_promo]], color=VIOLET, capsize=5, lw=2, marker="o", ms=7, zorder=5)
    ax.plot([t], [f_sans], marker="D", color=ORANGE, ms=7, ls="none")
    ax.plot([x[-1], t], [M.values[-1], f_promo], color=VIOLET, lw=1.2, ls=":")
    ax.text(t + pd.Timedelta(days=20), f_promo, f"{vir(f_promo)} avec les soldes,\nfourchette {vir(bas)} à {vir(haut)}", color=VIOLET, va="center", fontsize=9.5)
    ax.text(t + pd.Timedelta(days=20), f_sans - 25, f"{vir(f_sans)} sans soldes", color=ORANGE, va="center", fontsize=9.5)
    ax.annotate("janvier 2025 : 963", xy=(pd.Timestamp("2025-01-01"), M.loc["2025-01"]), xytext=(pd.Timestamp("2024-08-01"), 540), color=ENCRE2, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUET))
    _axe_mois(ax, 3)
    ax.set_xlim(x[0] - pd.Timedelta(days=20), t + pd.Timedelta(days=250))
    ax.set_ylim(450, 1950)
    ax.set_ylabel("commandes par mois")
    ax.set_title("Janvier 2026 : environ 1 000 commandes, et la décision sur les soldes pèse une centaine", loc="left", fontsize=10.5)
    save(fig, "ch03-janvier-2026.png")


def fig_calendrier():
    fig, ax = plt.subplots(figsize=(10.4, 3.5))
    ax.set_xlim(2023.0, 2026.1); ax.set_ylim(0, 3.4); ax.axis("off")
    def ligne(y, coupure, etiquette, col_c):
        ax.add_patch(Rectangle((coupure - 1, y), 1, 0.55, fc="#cde2fb", ec="none"))
        ax.add_patch(Rectangle((coupure, y), 0.25, 0.55, fc=col_c, ec="none"))
        ax.plot([coupure, coupure], [y - 0.1, y + 0.65], color=ENCRE, lw=2)
        ax.text(coupure - 0.5, y + 0.275, "variables : les 12 mois\nqui précèdent", ha="center", va="center", fontsize=8.8, color=ENCRE)
        ax.text(coupure + 0.125, y + 0.275, "90 j", ha="center", va="center", fontsize=8.8, color="white", fontweight="bold")
        ax.text(coupure, y + 0.78, etiquette, ha="center", fontsize=9.3, color=ENCRE, fontweight="bold")
    ligne(2.0, 2024.5, "coupure du 30/06/2024 : ENTRAÎNEMENT", BLEU)
    ligne(0.75, 2025.5, "coupure du 30/06/2025 : TEST", ORANGE)
    ax.text(2023.05, 3.2, "Un modèle n'a le droit de connaître que ce qui existait à la date de coupure", fontsize=10.5, color=ENCRE, fontweight="bold")
    ax.annotate("à la coupure de test, ces 90 jours-là sont passés :\nles étiquettes d'entraînement sont connues", xy=(2024.63, 1.97), xytext=(2023.05, 1.3), fontsize=8.8, color=ENCRE2, va="center",
                arrowprops=dict(arrowstyle="->", color=MUET, relpos=(0.95, 0.75)))
    for a in range(2023, 2027):
        ax.plot([a, a], [0.2, 0.3], color=AXE); ax.text(a, 0.05, str(a), ha="center", fontsize=8.5, color=MUET)
    ax.plot([2023, 2026], [0.3, 0.3], color=AXE, lw=1)
    save(fig, "ch03-calendrier-coupure.png")


NOMS_VARS = {"nb_12m": "commandes sur 12 mois", "nb_3m": "commandes sur 3 mois", "recence": "jours depuis la dernière commande", "rythme": "commandes par mois\nd'ancienneté",
             "nb_cats": "catégories achetées", "montant_12m": "montant sur 12 mois (€)", "panier": "panier moyen (€)", "part_site": "part des achats sur le Site",
             "taux_retour": "taux de retour", "fidelite": "carte de fidélité"}


def fig_arbre(arbre, noms):
    t = arbre.tree_
    feuilles = []
    def ordre(n):
        if t.children_left[n] == -1:
            feuilles.append(n)
        else:
            ordre(t.children_left[n]); ordre(t.children_right[n])
    ordre(0)
    pos = {}
    def place(n, prof):
        if t.children_left[n] == -1:
            pos[n] = (feuilles.index(n), -prof)
        else:
            l, r = t.children_left[n], t.children_right[n]
            place(l, prof + 1); place(r, prof + 1)
            pos[n] = ((pos[l][0] + pos[r][0]) / 2, -prof)
    place(0, 0)
    nfe = len(feuilles)
    fig, ax = plt.subplots(figsize=(12.4, 5.0))
    ax.set_xlim(-0.6, nfe - 0.4); ax.set_ylim(-3.6, 0.5); ax.axis("off")
    n_tot = t.n_node_samples[0]
    def fmt(x):
        return f"{x:.1f}".replace(".", ",")
    for n, (x, y) in pos.items():
        part = t.value[n][0] / t.value[n][0].sum()
        if t.children_left[n] != -1:
            for c, lab in [(t.children_left[n], "oui"), (t.children_right[n], "non")]:
                xc, yc = pos[c]
                ax.plot([x, xc], [y - 0.16, yc + 0.2], color=AXE, lw=1.2, zorder=1)
                ax.text((x + xc) / 2 + (-0.08 if lab == "oui" else 0.08), (y + yc) / 2 + 0.08, lab, fontsize=8.5, color=MUET, ha="right" if lab == "oui" else "left")
            nom = noms[t.feature[n]]
            seuil = t.threshold[n]
            txt = f"{NOMS_VARS.get(nom, nom)}\n≤ {fmt(seuil)} ?"
            ax.text(x, y, txt, ha="center", va="center", fontsize=8.6, color=ENCRE, bbox=dict(boxstyle="round,pad=0.35", fc="#e8f0fb", ec=AXE), zorder=3)
        else:
            col = BLEU if part[1] >= 0.5 else MUET
            txt = f"{round(100 * t.n_node_samples[n] / n_tot)} % des clients\n{round(100 * part[1])} % rachètent"
            ax.text(x, y, txt, ha="center", va="center", fontsize=8.4, color=ENCRE, bbox=dict(boxstyle="round,pad=0.35", fc="#fcfcfb", ec=col, lw=1.6), zorder=3)
    ax.set_title("Un arbre de profondeur 3 : le nombre de commandes de l'année passe avant tout le reste", loc="left", fontsize=10.5)
    save(fig, "ch03-arbre.png")


def fig_calibration_gain(y, p, p_ref, tab_cal, parts=None):
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3))
    ax = axes[0]
    ax.plot([0, 1], [0, 1], color=MUET, lw=1, ls="--")
    ax.plot(tab_cal["prévu"], tab_cal["observé"], color=BLEU, marker="o", ms=5)
    ax.text(0.5, 0.2, "sur la diagonale :\nce qui est annoncé\narrive", color=MUET, fontsize=9, ha="left")
    ax.set_xlim(0, 0.9); ax.set_ylim(0, 0.9)
    ax.set_xlabel("probabilité annoncée (moyenne du décile)"); ax.set_ylabel("part observée de rachats")
    ax.set_title("Les probabilités annoncées se vérifient", loc="left", fontsize=10.5)
    ax = axes[1]
    n = len(y)
    for sc, c, lab in [(p, BLEU, "modèle"), (p_ref, ORANGE, "récence seule")]:
        o = np.argsort(-sc, kind="stable")
        cum = np.r_[0, np.cumsum(np.asarray(y)[o]) / np.sum(y)]
        ax.plot(np.arange(n + 1) / n, cum, color=c, lw=2)
    ax.plot([0, 1], [0, 1], color=MUET, lw=1, ls="--")
    o = np.argsort(-p, kind="stable"); k20 = int(0.2 * n); g20 = np.cumsum(np.asarray(y)[o])[k20 - 1] / np.sum(y)
    ax.plot([0.2, 0.2], [0, g20], color=ENCRE2, lw=0.9, ls=":"); ax.plot([0, 0.2], [g20, g20], color=ENCRE2, lw=0.9, ls=":")
    ax.text(0.23, 0.10, f"20 % contactés :\n{vir(g20 * 100)} % des acheteurs", fontsize=9, color=ENCRE)
    ax.text(0.62, 0.50, "modèle", color=BLEU, fontsize=9.5, fontweight="bold"); ax.text(0.62, 0.31, "récence seule", color=ORANGE, fontsize=9.5, fontweight="bold")
    ax.text(0.80, 0.66, "au hasard", color=MUET, fontsize=9, rotation=40)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.set_xlabel("part des clients contactés (scores décroissants)"); ax.set_ylabel("part des acheteurs captés")
    ax.set_title(f"Contacter 20 % des clients capte {vir(g20 * 100)} % des rachats", loc="left", fontsize=10.5)
    save(fig, "ch03-calibration-gain.png")


def fig_fuite(a_hon, a_fuite, a_ref):
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    noms = ["récence seule", "modèle honnête", "avec la variable\nde trop"]
    vals = [a_ref, a_hon, a_fuite]
    cols = [MUET, BLEU, ROUGE]
    ax.barh(noms[::-1], vals[::-1], color=cols[::-1], height=0.55)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 0.006, i, vir(v, 3), va="center", fontsize=10, color=ENCRE)
    ax.set_xlim(0.5, 0.86); ax.grid(axis="y", visible=False)
    ax.set_xlabel("AUC sur la coupure de test")
    ax.set_title("Une variable calculée après la coupure « améliore » l'AUC de 0,07", loc="left", fontsize=10.5)
    save(fig, "ch03-fuite.png")


def fig_seuil(p, marge, cout, effet_rel, effet_abs):
    o = np.sort(p)[::-1]
    k = np.arange(1, len(o) + 1)
    h1 = np.cumsum(effet_abs * marge - cout + 0 * o)
    h2 = np.cumsum(effet_rel * o * marge - cout)
    part = k / len(o)
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    ax.plot(part, h1, color=ROUGE, lw=2); ax.plot(part, h2, color=BLEU, lw=2)
    ax.axhline(0, color=MUET, lw=0.8)
    i2 = int(np.argmax(h2))
    ax.plot([part[i2]], [h2[i2]], marker="o", color=BLEU, ms=7)
    ax.text(part[i2] + 0.03, h2[i2] + 90, f"maximum : {vir(part[i2] * 100)} % contactés,\n{vir(h2[i2])} € de marge attendue", color=BLEU, fontsize=9.5, va="bottom")
    ax.annotate("hypothèse B : +10 % de la probabilité\n(la marge dépend du score)", xy=(0.72, h2[int(0.72 * len(o))]), xytext=(0.48, -1100), color=BLEU, fontsize=9.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=BLEU, lw=0.8))
    ax.annotate("hypothèse A : +3 points pour tout le monde\n(on perd de l'argent partout)", xy=(0.30, h1[int(0.30 * len(o))]), xytext=(0.40, -2350), color=ROUGE, fontsize=9.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=ROUGE, lw=0.8))
    ax.set_ylim(-2800, 1150)
    ax.set_xlim(0, 1)
    ax.set_xlabel("part des clients contactés (scores décroissants)"); ax.set_ylabel("marge cumulée attendue (€)")
    ax.set_title("Le meilleur seuil dépend de l'effet de la campagne, que le modèle ne donne pas", loc="left", fontsize=10.5)
    save(fig, "ch03-seuil-cout.png")


def fig_derive(tab):
    fig, ax = plt.subplots(figsize=(10.0, 4.3))
    x = np.arange(len(tab))
    ax.plot(x, tab["observé"] * 100, color=ENCRE, lw=2.4, marker="o")
    ax.plot(x, tab["prévu_fixe"] * 100, color=ROUGE, lw=1.8, marker="s", ms=5)
    ax.plot(x, tab["prévu_saison"] * 100, color=BLEU, lw=1.8, marker="^", ms=6)
    ax.set_xticks(x); ax.set_xticklabels(tab["etiquette"], fontsize=9)
    ax.text(x[-1] + 0.1, tab["observé"].iloc[-1] * 100 + 1.2, "observé", color=ENCRE, fontsize=9.5, fontweight="bold")
    ax.text(x[-1] + 0.1, tab["prévu_fixe"].iloc[-1] * 100 - 0.5, "modèle figé", color=ROUGE, fontsize=9.5, fontweight="bold")
    ax.text(x[-1] + 0.1, tab["prévu_saison"].iloc[-1] * 100 + 2.6, "avec la saison", color=BLEU, fontsize=9.5, fontweight="bold")
    for i, a in enumerate(tab["auc"]):
        ax.text(i, 31.5, f"AUC {vir(a, 2)}", ha="center", fontsize=8.8, color=MUET)
    ax.set_ylim(30, 57); ax.set_xlim(-0.3, len(tab) - 1 + 1.0)
    ax.set_ylabel("part des clients qui rachètent (%)")
    ax.set_title("L'AUC reste stable ; les probabilités, elles, décrochent quand la saison change", loc="left", fontsize=10.5)
    save(fig, "ch03-derive.png")


def fig_classement(R, opt):
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.3), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.42})
    ax = axes[0]
    top = R.sort_values("cv", ascending=False).head(8).reset_index(drop=True)
    y = np.arange(len(top))[::-1]
    lab = [f"{r.famille} #{int(r.id)}" for r in top.itertuples()]
    ax.errorbar(top["cv"], y, xerr=top["cv_sd"], fmt="o", color=BLEU, capsize=3, ms=6)
    ax.plot(top["test"], y, marker="D", color=ORANGE, ls="none", ms=6)
    ax.set_yticks(y); ax.set_yticklabels(lab, fontsize=9)
    ax.set_xlim(0.700, 0.745); ax.grid(axis="y", visible=False)
    ax.text(0.7005, y[1], "●  validation temporelle\n    (moyenne ± écart-type des plis)", color=BLEU, fontsize=8.5, va="center")
    ax.text(0.7005, y[3], "◆  test : coupure jamais vue", color=ORANGE, fontsize=8.5, va="center")
    ax.set_xlabel("AUC")
    ax.set_title("Les huit premiers sont à égalité", loc="left", fontsize=10.5)
    ax = axes[1]
    for m, c, lab in [(500, ROUGE, "validation de 500 clients"), (4000, BLEU, "validation de 4 000 clients")]:
        s = opt[opt["validation"] == m]
        ax.plot(s["candidats"], s["écart"] * 100, color=c, marker="o", lw=2)
    ax.set_xscale("log"); ax.set_xticks([1, 5, 20, 60, 200]); ax.set_xticklabels(["1", "5", "20", "60", "200"])
    ax.axhline(0, color=MUET, lw=0.8)
    ax.text(1.1, 0.95, "validation de 500 clients", color=ROUGE, fontsize=9.5, fontweight="bold")
    ax.text(1.1, -0.28, "validation de 4 000 clients", color=BLEU, fontsize=9.5, fontweight="bold")
    ax.set_ylim(-0.6, 1.5)
    ax.set_xlabel("nombre de modèles essayés"); ax.set_ylabel("score du gagnant sur la validation\nmoins son score sur le reste\n(points d'AUC)", fontsize=9)
    ax.set_title("Plus on essaie, plus le gagnant est flatté", loc="left", fontsize=10.5)
    save(fig, "ch03-classement.png")
