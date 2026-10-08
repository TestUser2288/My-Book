"""Chapitre 4 (série 2, volume IV) : storytelling et rédaction de rapports.
Fonctions partagées par le livre et le cahier : chargement des données de la boutique, analyse des promotions (celle du volume III, refaite ici pour être racontée),
figures du récit (toutes dessinées avec matplotlib, style du livre), rapport hebdomadaire automatisé et ses contrôles, mesures de lisibilité."""
import os
import re
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import style as S  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch  # noqa: E402

TVA = 0.20


def fr(x, nd=1, signe=False):
    """nombre à la française : espace insécable pour les milliers, virgule décimale"""
    s = f"{x:+,.{nd}f}" if signe else f"{x:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")


# ----------------------------------------------------------------------------------------------- données
def charger(D):
    j = pd.read_csv(os.path.join(D, "jours_exploitation.csv"), parse_dates=["date"])
    cmd = pd.read_csv(os.path.join(D, "commandes.csv"), parse_dates=["date_commande"])
    lig = pd.read_csv(os.path.join(D, "lignes_commande.csv"))
    prod = pd.read_csv(os.path.join(D, "produits.csv"))
    liv = pd.read_csv(os.path.join(D, "livraisons.csv"), parse_dates=["date_commande", "date_livraison"])
    x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat", "categorie"]], on="id_produit")
    x["marge"] = x["montant"] / (1 + TVA) - x["quantite"] * x["cout_achat"]
    marge_j = x.groupby("date_commande")["marge"].sum().rename("marge").reset_index().rename(columns={"date_commande": "date"})
    j = j.merge(marge_j, on="date")
    j["mois"], j["annee"], j["t"] = j["date"].dt.month, j["date"].dt.year, np.arange(len(j)) / 365.25
    j["pub7"] = j["depense_pub"].rolling(7, min_periods=1).sum() / 1000
    j["pluie"] = (j["pluie_mm"] > 1).astype(int)
    return {"j": j, "cmd": cmd, "x": x, "liv": liv}


def analyse_promo(d):
    """l'analyse du volume III (chapitre 3 et projet) : effet de la promotion sur les commandes, contrefactuel de marge, seuil de bascule"""
    j = d["j"]
    mod = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie + pub7", data=j).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
    b, ic = mod.params["promo_active"], mod.conf_int().loc["promo_active"]
    e, e_bas, e_haut = np.exp(b) - 1, np.exp(ic[0]) - 1, np.exp(ic[1]) - 1
    pr, npr = j[j["promo_active"] == 1], j[j["promo_active"] == 0]
    mo_np, mo_p = npr["marge"].sum() / npr["nb_commandes"].sum(), pr["marge"].sum() / pr["nb_commandes"].sum()
    inc = lambda ee: pr["marge"].sum() - pr["nb_commandes"].sum() / (1 + ee) * mo_np
    pub_supp = pr["depense_pub"].sum() - len(pr) * npr["depense_pub"].mean()
    brut = j.groupby("promo_active")[["nb_commandes", "chiffre_affaires"]].mean()
    return dict(e=e, e_bas=e_bas, e_haut=e_haut, mo_np=mo_np, mo_p=mo_p, marge_reelle=pr["marge"].sum(), jours=len(pr), inc=inc(e), inc_bas=inc(e_haut), inc_haut=inc(e_bas),
                pub_supp=pub_supp, inc_pub=inc(e) - pub_supp, seuil=pr["nb_commandes"].sum() * mo_np / pr["marge"].sum() - 1, n_cmd=pr["nb_commandes"].sum(),
                brut_cmd=brut.loc[1, "nb_commandes"] / brut.loc[0, "nb_commandes"] - 1, brut_ca=brut.loc[1, "chiffre_affaires"] / brut.loc[0, "chiffre_affaires"] - 1, increment=inc)


# ----------------------------------------------------------------------------------------------- figures du récit
def _titre_fig(ax, titre, sous=None):
    ax.set_title(titre, loc="left", fontsize=11.5, color=S.ENCRE)
    if sous:
        ax.text(0, 1.015, sous, transform=ax.transAxes, fontsize=8.5, color=S.MUET, va="bottom")


def fig_titres(d):
    """le même graphique, deux titres : descriptif puis conclusion"""
    S.setup()
    j = d["j"]
    m = j[j["annee"] == 2025].groupby("mois")["chiffre_affaires"].sum() / 1000
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    part = (m.loc[11] + m.loc[12]) / m.sum() * 100
    for ax, titre in zip(axes, ["Chiffre d'affaires par mois en 2025", f"Novembre et décembre font {part:.0f} % du chiffre d'affaires de l'année"]):
        ax.bar(m.index, m.values, color=[S.ORANGE if k >= 11 else "#b9cdea" for k in m.index])
        ax.set_xticks(range(1, 13)); ax.set_xticklabels(list("JFMAMJJASOND"))
        ax.set_title(titre, loc="left", fontsize=10, color=S.ENCRE, wrap=True)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("k€")
    axes[0].text(0.02, 0.9, "avant : il décrit", transform=axes[0].transAxes, color=S.ROUGE, fontsize=9)
    axes[1].text(0.02, 0.9, "après : il conclut", transform=axes[1].transAxes, color=S.AQUA, fontsize=9)
    fig.tight_layout()
    S.save(fig, "ch04-titres.png")


def fig_arc():
    S.setup()
    fig, ax = plt.subplots(figsize=(9, 3.2)); ax.axis("off")
    x = np.linspace(0, 1, 200)
    y = 0.15 + 0.7 * np.exp(-((x - 0.55) ** 2) / 0.03) + 0.1 * x
    ax.plot(x, y, color=S.BLEU, lw=3)
    for xx, lab, c in [(0.07, "1. Contexte\nce que l'on sait", S.MUET), (0.35, "2. Tension\nla question qui gêne", S.ORANGE), (0.6, "3. Preuves\nles chiffres qui tranchent", S.BLEU), (0.92, "4. Résolution\nce que l'on fait", S.AQUA)]:
        ax.scatter([xx], [np.interp(xx, x, y)], s=120, color=c, zorder=3)
        if xx == 0.6:
            ax.text(xx + 0.04, np.interp(xx, x, y) + 0.03, lab, ha="left", fontsize=9, color=S.ENCRE)
        else:
            ax.text(xx, np.interp(xx, x, y) - 0.2, lab, ha="center", fontsize=9, color=S.ENCRE)
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.1, 1.2)
    ax.text(0.5, 1.12, "L'arc d'un récit de données : de ce qu'on sait à ce qu'on fait", ha="center", fontsize=11, color=S.ENCRE)
    S.save(fig, "ch04-arc.png")


def fig_pyramide():
    S.setup()
    fig, ax = plt.subplots(figsize=(8.5, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 6)
    ax.add_patch(plt.Polygon([[5, 5.7], [3.4, 3.6], [6.6, 3.6]], color=S.BLEU, alpha=0.9))
    ax.text(5, 4.15, "Réponse", ha="center", color="white", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((1.7, 2.1), 6.6, 1.35, color="#86b6ef", alpha=0.9))
    ax.text(5, 2.78, "Trois arguments clés", ha="center", fontsize=10, color=S.ENCRE)
    ax.add_patch(Rectangle((0.2, 0.3), 9.6, 1.6, color="#cde2fb"))
    ax.text(5, 1.1, "Preuves : chiffres, figures, méthode, limites", ha="center", fontsize=10, color=S.ENCRE)
    ax.annotate("on lit de haut en bas :\nla réponse d'abord", xy=(8.6, 4.2), xytext=(8.0, 5.0), fontsize=8.5, color=S.ENCRE2, arrowprops=dict(arrowstyle="->", color=S.MUET))
    S.save(fig, "ch04-pyramide.png")


def _fig_effets(d, a):
    S.setup()
    fig, ax = plt.subplots(figsize=(8.2, 2.9))
    labels = ["Comparaison brute", "Avec contrôles (saison, jour, tendance, pluie, publicité)"]
    vals = [a["brut_cmd"] * 100, a["e"] * 100]
    ax.barh([1, 0], vals, color=["#b9cdea", S.BLEU], height=0.5)
    ax.errorbar([a["e"] * 100], [0], xerr=[[a["e"] * 100 - a["e_bas"] * 100], [a["e_haut"] * 100 - a["e"] * 100]], color=S.ENCRE, capsize=4, lw=1.4)
    ax.axvline(18, color=S.ORANGE, ls="--", lw=1.2); ax.text(18.5, 0.5, "vérité programmée : +18 %", color=S.ORANGE, fontsize=8, va="center", ha="left")
    ax.set_yticks([1, 0]); ax.set_yticklabels(["Comparaison\nbrute", "Avec\ncontrôles"])
    for v, y in zip(vals, [1, 0]):
        ax.text(v / 2, y, f"{v:+.1f} %".replace(".", ","), ha="center", va="center", color="white", fontsize=10, weight="bold")
    ax.set_xlim(0, 30); ax.set_xlabel("commandes en plus les jours de promotion (%)"); ax.grid(axis="y", visible=False)
    ax.set_title("La promotion ajoute environ 19 % de commandes, plus de deux fois ce que montre la comparaison brute", loc="left", fontsize=10, color=S.ENCRE)
    S.save(fig, "ch04-recit-2-effet.png")


def _fig_marge(a):
    S.setup()
    N, mo = a["n_cmd"], a["mo_np"]
    sans = N / (1 + a["e"]) * mo
    gain = (N - N / (1 + a["e"])) * mo
    remise = a["marge_reelle"] - sans - gain
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    etapes = [("Marge sans\npromotion", sans), ("Commandes en\nplus", gain), ("Remises sur\ntoutes les commandes", remise), ("Marge\nréelle", a["marge_reelle"])]
    base = 0
    for i, (lab, v) in enumerate(etapes):
        if i in (0, 3):
            ax.bar(i, v / 1000, color=S.BLEU); ax.text(i, v / 1000 + 2, fr(v / 1000, 0) + " k€", ha="center", fontsize=9)
            base = v
        else:
            ax.bar(i, v / 1000, bottom=base / 1000, color=S.AQUA if v > 0 else S.ROUGE)
            ax.text(i, (base + max(v, 0)) / 1000 + 2, fr(v / 1000, 0, True) + " k€", ha="center", fontsize=9)
            base += v
    ax.set_xticks(range(4)); ax.set_xticklabels([e[0] for e in etapes], fontsize=8.5); ax.set_ylabel("marge brute des jours de promotion (k€)")
    ax.set_ylim(0, 185); ax.grid(axis="x", visible=False)
    ax.set_title("Les promotions vendent plus mais rapportent moins : les remises mangent le gain de volume", loc="left", fontsize=10, color=S.ENCRE)
    S.save(fig, "ch04-recit-3-marge.png")
    return dict(sans=sans, gain=gain, remise=remise)


def _fig_seuil(a):
    S.setup()
    e = np.linspace(0, 0.5, 100)
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    ax.plot(e * 100, [a["increment"](v) / 1000 for v in e], color=S.BLEU)
    ax.axhline(0, color=S.ENCRE2, lw=0.8)
    ax.axvspan(a["e_bas"] * 100, a["e_haut"] * 100, color=S.BLEU, alpha=0.15)
    ax.text((a["e_bas"] + a["e_haut"]) * 50, 13, "intervalle de confiance\nde l'effet", ha="center", fontsize=8, color=S.BLEU, va="top")
    ax.scatter([a["e"] * 100], [a["inc"] / 1000], color=S.BLEU, zorder=3)
    ax.scatter([a["seuil"] * 100], [0], color=S.ORANGE, zorder=3)
    ax.annotate(f"effet estimé : {a['e'] * 100:+.0f} %".replace(".", ",") + f"\nincrément : {fr(a['inc'] / 1000, 0)} k€", (a["e"] * 100, a["inc"] / 1000), xytext=(a["e"] * 100 + 3, a["inc"] / 1000 - 12), fontsize=8.5)
    ax.annotate(f"seuil de bascule : +{a['seuil'] * 100:.0f} %", (a["seuil"] * 100, 0), xytext=(a["seuil"] * 100 + 1.5, -9), fontsize=8.5, color=S.ORANGE)
    ax.set_xlabel("effet de la promotion sur les commandes (%)"); ax.set_ylabel("incrément de marge (k€)")
    ax.set_title("Il faudrait plus de 35 % de commandes en plus pour ne pas perdre de marge", loc="left", fontsize=10, color=S.ENCRE)
    S.save(fig, "ch04-recit-4-seuil.png")


def _fig_brut(d):
    S.setup()
    j = d["j"]
    fig, ax = plt.subplots(figsize=(8.2, 2.9))
    g = j.groupby("promo_active")[["nb_commandes"]].mean()
    ax.bar([0, 1], [g.loc[0, "nb_commandes"], g.loc[1, "nb_commandes"]], color=["#b9cdea", S.ORANGE], width=0.5)
    for k, v in enumerate(g["nb_commandes"]):
        ax.text(k, v + 0.5, f"{v:.1f}".replace(".", ","), ha="center", fontsize=10)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["jours ordinaires", "jours de promotion"]); ax.set_ylabel("commandes par jour"); ax.set_ylim(0, 45); ax.grid(axis="x", visible=False)
    ax.set_title("Les jours de promotion, on vend un peu plus de commandes (mais ce chiffre trompe)", loc="left", fontsize=10, color=S.ENCRE)
    S.save(fig, "ch04-recit-1-brut.png")


def fig_recit(d, a):
    _fig_brut(d); _fig_effets(d, a); cascade = _fig_marge(a); _fig_seuil(a)
    return cascade


def fig_storyboard():
    S.setup()
    fig, axes = plt.subplots(1, 5, figsize=(11, 2.6))
    titres = ["1. Contexte", "2. Le chiffre\nqui trompe", "3. L'effet réel", "4. Le coût", "5. Que faire ?"]
    corps = ["Trois promotions\npar an, 153 jours,\nles ventes montent", "+8 % de commandes\nen comparaison brute,\nCA stable", "+19 % de commandes\nà saison égale", "Marge −18 k€ :\nremises sur toutes\nles commandes", "Réduire la remise,\ncibler, tester\nla prochaine édition"]
    cols = [S.MUET, S.ORANGE, S.BLEU, S.ROUGE, S.AQUA]
    for ax, t, c, col in zip(axes, titres, corps, cols):
        ax.axis("off"); ax.add_patch(FancyBboxPatch((0.03, 0.05), 0.94, 0.9, boxstyle="round,pad=0.01,rounding_size=0.04", fc="white", ec=col, lw=2, transform=ax.transAxes))
        ax.text(0.5, 0.8, t, ha="center", va="center", fontsize=9.5, color=col, weight="bold", transform=ax.transAxes)
        ax.text(0.5, 0.38, c, ha="center", va="center", fontsize=8.5, color=S.ENCRE, transform=ax.transAxes)
    fig.suptitle("Le storyboard : cinq pages, un message chacune, la recommandation à la fin ... et dans le résumé", fontsize=10, color=S.ENCRE, y=1.02)
    S.save(fig, "ch04-storyboard.png")


def fig_cerise(d):
    import matplotlib.dates as mdates
    S.setup()
    j = d["j"].set_index("date")["nb_commandes"].resample("W-SUN").sum().iloc[1:-1]       # semaines complètes seulement
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
    s = j["2024-10-01":"2025-01-31"]
    axes[0].plot(s.index, s.values, color=S.ROUGE); axes[0].set_title("« Nos commandes explosent ! »\n(octobre 2024 à janvier 2025)", loc="left", fontsize=9.5, color=S.ENCRE)
    axes[1].plot(j.index, j.values, color=S.BLEU); axes[1].axvspan(s.index[0], s.index[-1], color=S.ROUGE, alpha=0.12)
    axes[1].set_title("La même série sur trois ans :\nla hausse est la saison de fin d'année", loc="left", fontsize=9.5, color=S.ENCRE)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")); axes[0].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y")); axes[1].xaxis.set_major_locator(mdates.YearLocator())
    axes[0].set_ylabel("commandes par semaine"); axes[0].set_ylim(0, 480)
    fig.tight_layout(); S.save(fig, "ch04-cerise.png")


def fig_structure():
    S.setup()
    fig, ax = plt.subplots(figsize=(9, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    blocs = [("Résumé", "la réponse et la recommandation", 1.0, S.AQUA), ("Question", "ce qu'on voulait savoir, et pourquoi", 0.9, S.BLEU), ("Données", "d'où, quand, quoi, limites", 0.9, S.BLEU),
             ("Méthode", "en quelques lignes", 0.9, S.BLEU), ("Résultats", "figures et tableaux, un message chacun", 1.2, S.BLEU), ("Limites", "ce que l'analyse ne dit pas", 0.9, S.ORANGE),
             ("Recommandations", "action, responsable, date, indicateur", 1.0, S.AQUA), ("Annexes", "détails, code, données", 0.7, S.MUET)]
    y = 4.7
    for t, c, h, col in blocs:
        ax.add_patch(Rectangle((0.2, y - h * 0.5), 2.2, h * 0.5, color=col)); ax.text(1.3, y - h * 0.25, t, ha="center", va="center", color="white", fontsize=9.5, weight="bold")
        ax.text(2.6, y - h * 0.25, c, va="center", fontsize=9, color=S.ENCRE)
        y -= h * 0.5 + 0.08
    ax.text(7.2, 4.2, "Ce que lit\nun décideur pressé :", fontsize=9, color=S.ENCRE2); ax.add_patch(Rectangle((7.1, 3.0), 2.6, 0.1, color=S.AQUA)); 
    ax.text(7.2, 2.5, "résumé + recommandations\n(une page)", fontsize=9, color=S.AQUA)
    ax.text(7.2, 1.3, "Ce que lit\nun collègue qui refait :", fontsize=9, color=S.ENCRE2); ax.text(7.2, 0.5, "données + méthode + annexes", fontsize=9, color=S.BLEU)
    S.save(fig, "ch04-structure.png")


def fig_une_page(a):
    S.setup()
    fig = plt.figure(figsize=(6.2, 8.2)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 13)
    ax.add_patch(Rectangle((0.2, 0.2), 9.6, 12.6, fc="white", ec=S.AXE, lw=1.2))
    ax.text(0.7, 12.2, "Les promotions : vendre plus, gagner moins", fontsize=13, weight="bold", color=S.ENCRE)
    ax.text(0.7, 11.7, "Note à la gérante : décision demandée avant le 15 novembre", fontsize=8.5, color=S.MUET)
    ax.add_patch(Rectangle((0.7, 10.0), 8.6, 1.35, fc="#e8f6f0", ec="none"))
    ax.text(0.9, 11.15, "Recommandation : ne pas reconduire la promotion telle quelle.", fontsize=9.3, weight="bold", color=S.AQUA, va="top")
    ax.text(0.9, 10.7, "Baisser la remise, la limiter aux produits à forte marge,\ntester l'édition d'hiver sur une partie des jours.", fontsize=8.3, color=S.ENCRE, va="top")
    ax.text(0.7, 9.6, "Trois chiffres à retenir", fontsize=10, weight="bold", color=S.ENCRE)
    puces = [f"+{a['e'] * 100:.0f} % de commandes à saison égale (intervalle {a['e_bas'] * 100:.0f} à {a['e_haut'] * 100:.0f} %)".replace(".", ","),
             f"marge par commande : {fr(a['mo_np'], 0)} € hors promotion, {fr(a['mo_p'], 0)} € en promotion",
             f"perte de marge estimée : {fr(-a['inc'] / 1000, 0)} k€ ; seuil de bascule : +{a['seuil'] * 100:.0f} % de commandes"]
    for i, t in enumerate(puces):
        ax.text(0.9, 9.1 - 0.45 * i, "•  " + t, fontsize=8.3, color=S.ENCRE)
    ax2 = fig.add_axes([0.12, 0.17, 0.78, 0.37])
    vals = [(a["marge_reelle"] - a["inc"]) / 1000, a["marge_reelle"] / 1000]
    ax2.bar(["Marge sans\npromotion", "Marge\nréelle"], vals, color=["#b9cdea", S.ROUGE], width=0.5)
    ax2.set_ylabel("k€"); ax2.grid(axis="x", visible=False); ax2.set_ylim(0, 175)
    ax2.set_title("Marge brute des 153 jours de promotion", loc="left", fontsize=9, color=S.ENCRE)
    for k, v in enumerate(vals):
        ax2.text(k, v + 3, fr(v, 0) + " k€", ha="center", fontsize=9)
    ax.text(0.7, 0.85, "Limites : effet estimé, non mesuré par expérience ;\nvaleur à long terme des clients acquis non comptée.", fontsize=7.5, color=S.MUET, style="italic")
    S.save(fig, "ch04-une-page.png")


def fig_diapos():
    S.setup()
    fig, axes = plt.subplots(2, 4, figsize=(10, 4.8))
    titres = ["Les promotions :\nvendre plus, gagner moins", "Ce que l'on a vu :\n+8 % de commandes", "À saison égale :\n+19 % de commandes", "Chaque commande\nrapporte 8 € de moins",
              "Résultat :\n−18 k€ de marge", "Même dans le meilleur\ncas, la marge baisse", "Recommandation :\nréduire la remise, tester", "Annexe :\nméthode et limites"]
    cols = [S.BLEU, S.MUET, S.BLEU, S.ORANGE, S.ROUGE, S.ROUGE, S.AQUA, S.MUET]
    contenus = ["titre", "figure", "figure", "figure", "figure", "figure", "3 puces", "texte court"]
    for k, (ax, t, c, ct) in enumerate(zip(axes.ravel(), titres, cols, contenus)):
        ax.axis("off"); ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=S.AXE, transform=ax.transAxes))
        ax.add_patch(Rectangle((0, 0.72), 1, 0.28, fc=c, transform=ax.transAxes))
        ax.text(0.05, 0.86, t, color="white", fontsize=7.5, va="center", weight="bold", transform=ax.transAxes)
        ax.add_patch(Rectangle((0.08, 0.1), 0.84, 0.52, fc="#f3f2ee", ec="none", transform=ax.transAxes))
        ax.text(0.5, 0.36, ct, ha="center", va="center", fontsize=8, color=S.MUET, transform=ax.transAxes)
        ax.text(0.97, 0.02, str(k + 1), ha="right", fontsize=7, color=S.MUET, transform=ax.transAxes)
    fig.suptitle("Huit diapositives pour dix minutes : le titre de chacune est sa conclusion", fontsize=10, color=S.ENCRE)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.03, wspace=0.08, hspace=0.12)
    S.save(fig, "ch04-diapositives.png")


# ----------------------------------------------------------------------------------------------- lisibilité
JARGON = ["contrefactuel", "hétéroscédasticité", "autocorrélation", "coefficient", "intervalle de confiance", "p-valeur", "régression", "logarithme", "écart-type", "significatif", "estimateur", "résidus"]


def phrases(texte):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", texte.strip()) if p.strip()]


def lisibilite(texte):
    p = phrases(texte)
    mots = re.findall(r"\w+(?:['’-]\w+)*", texte)
    jarg = sum(texte.lower().count(j) for j in JARGON)
    return {"phrases": len(p), "mots": len(mots), "mots_par_phrase": round(len(mots) / max(len(p), 1), 1), "termes_techniques": jarg, "chiffres": len(re.findall(r"\d+(?:[.,]\d+)?", texte))}


# ----------------------------------------------------------------------------------------------- rapport hebdomadaire automatisé
def semaine_kpis(d, debut):
    """indicateurs de la semaine commençant à `debut` (lundi), comparés à la semaine précédente et à la même semaine un an avant"""
    j = d["j"].set_index("date"); cmd = d["cmd"]; x = d["x"]; liv = d["liv"]
    debut = pd.Timestamp(debut)
    def agr(a):
        fin = a + pd.Timedelta(days=6)
        js = j.loc[a:fin]
        xs = x[(x["date_commande"] >= a) & (x["date_commande"] <= fin)]
        cs = cmd[(cmd["date_commande"] >= a) & (cmd["date_commande"] <= fin)]
        ls = liv[(liv["date_commande"] >= a) & (liv["date_commande"] <= fin)]
        retard = ls.assign(delai=(ls["date_livraison"] - ls["date_commande"]).dt.days).eval("delai > delai_promis_j")
        return dict(ca=js["chiffre_affaires"].sum(), commandes=int(js["nb_commandes"].sum()), panier=xs["montant"].sum() / max(len(cs), 1), marge=xs["marge"].sum(),
                    a_l_heure=1 - retard.mean() if len(ls) else np.nan, jours=len(js))
    cur, prec, an = agr(debut), agr(debut - pd.Timedelta(days=7)), agr(debut - pd.Timedelta(days=364))
    return {"debut": debut, "fin": debut + pd.Timedelta(days=6), "cur": cur, "prec": prec, "an": an}


def bruit_hebdo(d, debut, n=26, annuel=False):
    """écart-type (en proportion) de la variation du CA hebdomadaire sur n semaines avant `debut` : d'une semaine à la suivante, ou d'une année à l'autre (même semaine N-1)"""
    j = d["j"].set_index("date")["chiffre_affaires"]
    s = j.resample("W-SUN").sum()
    s = s[s.index < pd.Timestamp(debut)]
    v = (s / s.shift(52) - 1).dropna().tail(n) if annuel else s.pct_change().dropna().tail(n)
    return float(v.std())


def phrase_variation(cur, ref, bruit, ref_nom):
    """texte généré avec garde-fou : on ne commente une variation que si elle dépasse 1,5 fois la variation ordinaire"""
    v = cur / ref - 1
    if abs(v) < 1.5 * bruit:
        return f"stable par rapport à {ref_nom} ({fr(v * 100, 1, True)} %, dans la variation ordinaire)"
    sens = "en hausse" if v > 0 else "en baisse"
    return f"{sens} de {fr(abs(v) * 100, 1)} % par rapport à {ref_nom} (au-delà de la variation ordinaire de ±{fr(1.5 * bruit * 100, 0)} %)"


def controles_avant_envoi(d, debut):
    """les contrôles qui bloquent l'envoi : données complètes, fraîcheur, totaux concordants"""
    j = d["j"]; cmd = d["cmd"]; x = d["x"]
    debut = pd.Timestamp(debut); fin = debut + pd.Timedelta(days=6)
    js = j[(j["date"] >= debut) & (j["date"] <= fin)]
    xs = x[(x["date_commande"] >= debut) & (x["date_commande"] <= fin)]
    cs = cmd[(cmd["date_commande"] >= debut) & (cmd["date_commande"] <= fin)]
    return {"sept jours présents": len(js) == 7,
            "dernière date des données couvre la semaine": j["date"].max() >= fin,
            "CA du fichier journalier = CA des lignes (à 1 €)": bool(abs(js["chiffre_affaires"].sum() - xs["montant"].sum()) < 1),
            "commandes du fichier journalier = commandes distinctes": int(js["nb_commandes"].sum()) == cs["id_commande"].nunique(),
            "aucune valeur manquante dans la semaine": not js.isna().any().any()}


def rapport_md(d, debut):
    k = semaine_kpis(d, debut); b = bruit_hebdo(d, debut); ba = bruit_hebdo(d, debut, annuel=True)
    c, p, a = k["cur"], k["prec"], k["an"]
    lignes = [f"# Rapport hebdomadaire : semaine du {k['debut']:%d/%m/%Y} au {k['fin']:%d/%m/%Y}", "",
              f"**En une phrase.** Chiffre d'affaires de {fr(c['ca'], 0)} €, " + phrase_variation(c["ca"], a["ca"], ba, "la même semaine de l'an dernier") + ".", "",
              "| Indicateur | Cette semaine | Semaine précédente | Même semaine N−1 |", "|---|---:|---:|---:|",
              f"| Chiffre d'affaires (€) | {fr(c['ca'], 0)} | {fr(p['ca'], 0)} | {fr(a['ca'], 0)} |",
              f"| Commandes | {c['commandes']} | {p['commandes']} | {a['commandes']} |",
              f"| Panier moyen (€) | {fr(c['panier'], 1)} | {fr(p['panier'], 1)} | {fr(a['panier'], 1)} |",
              f"| Marge brute HT (€) | {fr(c['marge'], 0)} | {fr(p['marge'], 0)} | {fr(a['marge'], 0)} |",
              f"| Livraisons à l'heure (%) | {fr(c['a_l_heure'] * 100, 1)} | {fr(p['a_l_heure'] * 100, 1)} | {fr(a['a_l_heure'] * 100, 1)} |", "",
              "**Lecture.** D'une semaine à l'autre, le chiffre d'affaires est " + phrase_variation(c["ca"], p["ca"], b, "la semaine précédente") + ".", "",
              f"*Variation ordinaire (écart-type sur 26 semaines) : {fr(b * 100, 1)} % d'une semaine à l'autre, {fr(ba * 100, 1)} % d'une année à l'autre.*"]
    return "\n".join(lignes), k, b


# ----------------------------------------------------------------------------------------------- cerises, relecture des chiffres, rapport en HTML
def cerise_chiffres(d):
    """commandes hebdomadaires moyennes en octobre puis fin novembre à fin décembre, pour chaque année : la « hausse » de l'automne et la vraie comparaison (décembre contre décembre)"""
    s = d["j"].set_index("date")["nb_commandes"].resample("W-SUN").sum().iloc[1:-1]
    r = {}
    for y in (2023, 2024, 2025):
        a, b = s[f"{y}-10-01":f"{y}-10-28"].mean(), s[f"{y}-11-25":f"{y}-12-22"].mean()
        r[y] = {"octobre": a, "decembre": b, "hausse": b / a - 1}
    r["dec_sur_dec_2024"] = r[2024]["decembre"] / r[2023]["decembre"] - 1
    r["dec_sur_dec_2025"] = r[2025]["decembre"] / r[2024]["decembre"] - 1
    return r


def nombres_du_texte(texte):
    """les nombres écrits dans un texte français (virgule décimale, espaces fines ou insécables comme séparateurs de milliers), en valeur absolue"""
    t = texte.replace(" ", "").replace(" ", "").replace("−", "-")
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", "", t)
    return [float(m.replace(",", ".")) for m in re.findall(r"\d+(?:,\d+)?", t)]


def _arrondis(p):
    """les écritures acceptables d'un nombre calculé : lui-même, arrondi à 0, 1 ou 2 décimales, ou à 1 à 4 chiffres significatifs"""
    p = abs(float(p))
    out = {round(p, k) for k in (0, 1, 2)} | {p}
    if p > 0:
        out |= {round(p, k - 1 - int(np.floor(np.log10(p)))) for k in range(1, 5)}
    return out


def verifier_nombres(texte, permis):
    """les nombres du texte qui ne correspondent à aucune valeur calculée, arrondis compris : des erreurs de recopie probables"""
    ok = set().union(*[_arrondis(p) for p in permis]) if len(permis) else set()
    return [n for n in nombres_du_texte(texte) if not any(abs(n - r) < 1e-9 for r in ok)]


def rapport_html(md):
    """le rapport en Markdown devient une page HTML (pandoc s'il est installé), avec une feuille de style sobre"""
    import shutil, subprocess
    css = ("body{font-family:Helvetica,Arial,sans-serif;max-width:760px;margin:24px auto;color:#1f2937;line-height:1.45;font-size:15px}"
           "h1{font-size:22px;border-bottom:3px solid #1d4f9f;padding-bottom:6px}table{border-collapse:collapse;width:100%;margin:14px 0}"
           "th,td{padding:6px 10px;border-bottom:1px solid #d9dce3}th{text-align:left;background:#eef3fb}td:not(:first-child),th:not(:first-child){text-align:right}em{color:#667085}")
    if shutil.which("pandoc"):
        corps = subprocess.run(["pandoc", "-f", "gfm", "-t", "html"], input=md, capture_output=True, text=True, check=True).stdout
    else:
        corps = "<pre>" + md + "</pre>"
    return f"<!doctype html><html lang='fr'><meta charset='utf-8'><style>{css}</style><body>{corps}</body></html>"
