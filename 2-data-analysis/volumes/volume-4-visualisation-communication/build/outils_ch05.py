"""Outils du chapitre 5 (volume IV, série 2) : chiffres de la boutique à présenter, et figures du chapitre.

Les nombres cités dans la prose viennent de `faits(D)` ; les figures sont dessinées avec matplotlib (cartes d'acteurs, structure d'une présentation, etc.) :
ce sont des **schémas**, pas des captures d'écran.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import style as S

S.setup()


# ------------------------------------------------------------------------------------------------ chiffres
def faits(D):
    import statsmodels.formula.api as smf
    j = pd.read_csv(os.path.join(D, "jours_exploitation.csv"), parse_dates=["date"])
    cmd = pd.read_csv(os.path.join(D, "commandes.csv")); lig = pd.read_csv(os.path.join(D, "lignes_commande.csv")); prod = pd.read_csv(os.path.join(D, "produits.csv"))
    j["mois"], j["t"] = j["date"].dt.month, np.arange(len(j)) / 365.25
    j["pub7"] = j["depense_pub"].rolling(7, min_periods=1).sum() / 1000
    j["pluie"] = (j["pluie_mm"] > 1).astype(int)
    mod = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie + pub7", data=j).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
    b, ic = mod.params["promo_active"], mod.conf_int().loc["promo_active"]
    x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
    x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]
    mj = x.groupby("date_commande")["marge"].sum().rename("marge").reset_index().rename(columns={"date_commande": "date"})
    mj["date"] = pd.to_datetime(mj["date"])
    j = j.merge(mj, on="date")
    pr, npr = j[j["promo_active"] == 1], j[j["promo_active"] == 0]
    mo_np, mo_p = npr["marge"].sum() / npr["nb_commandes"].sum(), pr["marge"].sum() / pr["nb_commandes"].sum()

    def increment(e):
        return pr["marge"].sum() - pr["nb_commandes"].sum() / (1 + e) * mo_np

    e, e_bas, e_haut = np.exp(b) - 1, np.exp(ic[0]) - 1, np.exp(ic[1]) - 1
    liv = pd.read_csv(os.path.join(D, "livraisons.csv"))
    liv["mois"] = liv["date_commande"].str[5:7].astype(int)
    sess = pd.read_csv(os.path.join(D, "sessions_web.csv"))
    bud = pd.read_csv(os.path.join(D, "budget_reel_2025.csv"))
    conv = sess.groupby("source")["commande"].mean()
    return {
        "e": e, "e_bas": e_bas, "e_haut": e_haut, "mo_np": mo_np, "mo_p": mo_p, "marge_reelle": pr["marge"].sum(),
        "incr": increment(e), "incr_haut": increment(e_haut), "incr_bas": increment(e_bas), "seuil": pr["nb_commandes"].sum() * mo_np / pr["marge"].sum() - 1,
        "jours_promo": int(len(pr)), "pub_supp": pr["depense_pub"].sum() - len(pr) * npr["depense_pub"].mean(),
        "retard": liv["retard"].mean(), "retard_dec": liv.loc[liv["mois"] == 12, "retard"].mean(), "retard_hors_dec": liv.loc[liv["mois"] != 12, "retard"].mean(),
        "retard_transp": liv.groupby("transporteur")["retard"].mean().to_dict(), "abime_transp": liv.groupby("transporteur")["colis_abime"].mean().to_dict(),
        "conv": conv.to_dict(), "conv_globale": sess["commande"].mean(), "n_sessions": len(sess), "n_cmd_site": int(sess["commande"].sum()),
        "ca_bud": bud["ca_budget"].sum(), "ca_reel": bud["ca_reel"].sum(), "marge_bud": bud["marge_budget"].sum(), "marge_reelle_bud": bud["marge_reelle"].sum(),
        "mod": mod, "j": j,
    }


def fmt(v, nd=1):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")


# ------------------------------------------------------------------------------------------------ figures (schémas)
def _boite(ax, x, y, w, h, texte, couleur=S.BLEU, fc=None, fs=8.5, gras=False, alpha=0.12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc or couleur, ec=couleur, lw=1.2, alpha=alpha if fc is None else 1.0))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc="none", ec=couleur, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=fs, color=S.ENCRE, weight="bold" if gras else "normal", wrap=True)


def fig_salle(nom="ch05-salle.png"):
    fig, ax = plt.subplots(figsize=(7.2, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    roles = [("Le décideur", "veut une décision\net un ordre\nde grandeur", S.BLEU), ("L'expert", "veut la méthode\net les limites", S.VIOLET),
             ("L'utilisateur", "veut savoir ce qui\nchange dans\nson travail", S.AQUA), ("Le sceptique", "veut voir ce\nqui pourrait\nêtre faux", S.ROUGE)]
    for i, (t, s, c) in enumerate(roles):
        x = 0.3 + i * 2.4
        _boite(ax, x, 1.6, 2.2, 2.4, "", c)
        ax.text(x + 1.1, 3.55, t, ha="center", fontsize=10, weight="bold", color=c)
        ax.text(x + 1.1, 2.55, s, ha="center", va="center", fontsize=8, color=S.ENCRE)
    ax.text(5, 0.9, "La même analyse, quatre lectures : on prépare une phrase pour chacun.", ha="center", fontsize=9.5, color=S.ENCRE2)
    ax.text(5, 0.35, "Chacun a du temps, du vocabulaire et des craintes différents.", ha="center", fontsize=8.5, color=S.MUET)
    S.save(fig, nom)


def fig_pouvoir_interet(nom="ch05-pouvoir-interet.png"):
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axhline(5, color=S.AXE, lw=1); ax.axvline(5, color=S.AXE, lw=1); ax.grid(False)
    for (x, y, t) in [(1.4, 9.2, "À tenir informé"), (6.4, 9.2, "À associer étroitement"), (1.4, 0.5, "À surveiller"), (6.4, 0.5, "À informer régulièrement")]:
        ax.text(x, y, t, fontsize=8.5, color=S.MUET, style="italic")
    acteurs = [("La gérante\n(décide)", 8.7, 8.4, S.BLEU), ("Responsable\nlogistique", 7.3, 4.2, S.AQUA), ("Comptable", 3.2, 7.2, S.VIOLET),
               ("Vendeurs", 6.2, 2.2, S.ORANGE), ("Prestataire\nde livraison", 2.6, 3.0, S.MUET), ("Banque", 1.8, 6.4, S.ROUGE)]
    for t, x, y, c in acteurs:
        ax.scatter([x], [y], s=190, color=c, zorder=3); ax.text(x, y - 0.95, t, ha="center", va="top", fontsize=8, color=S.ENCRE)
    ax.set_xlabel("Intérêt pour le sujet →"); ax.set_ylabel("Pouvoir de décision →"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Cartographie des parties prenantes pour « faut-il reconduire les soldes ? »", loc="left", fontsize=9.5)
    S.save(fig, nom)


def fig_structure(nom="ch05-structure-10min.png"):
    fig, ax = plt.subplots(figsize=(7.4, 2.7)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    blocs = [("Réponse", 1, S.BLEU), ("Preuve 1", 2, S.AQUA), ("Preuve 2", 2, S.AQUA), ("Preuve 3", 2, S.AQUA), ("Action\nproposée", 1.2, S.ORANGE), ("Décision\ndemandée", 1, S.ROUGE), ("Suites", 0.8, S.VIOLET)]
    x = 0.1; tot = sum(b[1] for b in blocs); k = 9.8 / tot
    for t, m, c in blocs:
        _boite(ax, x, 1.0, m * k - 0.06, 1.2, t, c, fs=7.5, alpha=0.2)
        ax.text(x + (m * k - 0.06) / 2, 0.65, f"{m:g} min".replace(".", ","), ha="center", fontsize=8, color=S.ENCRE2)
        x += m * k
    ax.text(0.1, 2.65, "Dix minutes, sept blocs : la réponse en premier, jamais la méthode en premier.", fontsize=9, color=S.ENCRE2)
    ax.text(0.1, 0.15, "Les questions viennent après, pas pendant : annoncez-le au début.", fontsize=8.5, color=S.MUET)
    S.save(fig, nom)


def _sim(rgb, matrice):
    return np.clip(np.array(matrice) @ rgb, 0, 1)


def fig_daltonisme(nom="ch05-daltonisme.png"):
    cols = [S.BLEU, S.ORANGE, S.AQUA, S.VIOLET, S.ROUGE]
    noms = ["BLEU", "ORANGE", "AQUA", "VIOLET", "ROUGE"]
    def h2r(c):
        return np.array([int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    lin = lambda v: np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    gam = lambda v: np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.clip(v, 0, None) ** (1 / 2.4) - 0.055)
    M = {"Vision normale": np.eye(3),
         "Protanopie (rouge absent)": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
         "Deutéranopie (vert absent)": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
         "Tritanopie (bleu absent)": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}
    fig, ax = plt.subplots(figsize=(7.2, 3.3)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(-0.9, 4)
    for r, (k, m) in enumerate(M.items()):
        y = 3.1 - r * 0.9
        ax.text(0.0, y + 0.3, k, fontsize=8.5, va="center", color=S.ENCRE)
        for i, c in enumerate(cols):
            rgb = h2r(c) if k == "Vision normale" else gam(_sim(lin(h2r(c)), m))
            ax.add_patch(Rectangle((3.8 + i * 1.2, y), 1.05, 0.6, fc=rgb, ec="white"))
            if r == 0:
                ax.text(3.8 + i * 1.2 + 0.52, 3.85, noms[i].capitalize(), ha="center", fontsize=7.5, color=S.MUET)
    ax.text(0.0, -0.45, "Simulation (matrices de Machado et al., 2009). Orange, rouge et aqua se rapprochent en protanopie et deutéranopie :\ndoublez la couleur par une étiquette ou une forme.", fontsize=7.2, color=S.MUET)
    S.save(fig, nom)


def fig_trois_publics(nom="ch05-trois-publics.png", f=None):
    fig, ax = plt.subplots(figsize=(8.6, 4.0)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6)
    txt = [("La gérante", S.BLEU, "Les soldes font vendre\nplus, mais pas gagner\nplus : nous perdons\nenviron {p} € de marge\npar édition. À revoir."),
           ("La logistique", S.AQUA, "Les jours de soldes, les\ncommandes montent\nd'environ {e} % :\nprévoyez personnel\net colis."),
           ("Le financeur", S.VIOLET, "Effet des soldes sur la\nmarge : négatif dans\n{s} % des simulations ;\nil faudrait +{sd} %\nde commandes.")]
    for i, (t, c, s) in enumerate(txt):
        x = 0.2 + i * 3.95
        _boite(ax, x, 0.7, 3.7, 4.6, "", c)
        ax.text(x + 1.85, 4.85, t, ha="center", fontsize=9.5, weight="bold", color=c)
        ax.text(x + 1.85, 2.8, s.format(**f), ha="center", va="center", fontsize=8.6, color=S.ENCRE)
    ax.text(6, 0.25, "Même analyse, même incertitude : ce qui change, c'est la question que chacun se pose.", ha="center", fontsize=9, color=S.ENCRE2)
    S.save(fig, nom)


def fig_incertitude(f, nom="ch05-incertitude.png"):
    fig, axs = plt.subplots(1, 3, figsize=(8.2, 2.9), gridspec_kw={"width_ratios": [1, 1.2, 1.4]})
    e, lo, hi = f["e"] * 100, f["e_bas"] * 100, f["e_haut"] * 100
    ax = axs[0]; ax.bar([0], [e], color=S.BLEU, width=0.5); ax.set_xticks([0]); ax.set_xticklabels(["effet\nestimé"]); ax.set_ylim(0, 40); ax.set_ylabel("commandes en plus (%)")
    ax.text(0, e + 1, f"{e:.0f} %", ha="center", fontsize=9); ax.set_title("Un chiffre seul", loc="left", fontsize=9)
    ax = axs[1]; ax.errorbar([0], [e], yerr=[[e - lo], [hi - e]], fmt="o", color=S.BLEU, capsize=5, lw=2); ax.axhline(0, color=S.AXE); ax.set_xlim(-1, 1); ax.set_ylim(0, 40); ax.set_xticks([0]); ax.set_xticklabels(["effet estimé"])
    ax.text(0.15, e, f"{e:.0f} %\n({lo:.0f} à {hi:.0f})", fontsize=8.5, va="center"); ax.set_title("Une fourchette", loc="left", fontsize=9)
    ax = axs[2]; ax.set_xlim(-0.2, 1.2); ax.set_ylim(0, 40); ax.axis("off")
    x = np.linspace(0, 1, 100)
    ax.fill_between([0.15, 0.85], [lo, lo], [hi, hi], color=S.BLEU, alpha=0.15)
    ax.plot([0.1, 0.9], [e, e], color=S.BLEU, lw=2.5); ax.text(0.5, e + 1.5, f"{e:.0f} % : estimation", ha="center", fontsize=8.5, color=S.BLEU)
    ax.text(0.5, hi + 1.8, f"plausible jusqu'à {hi:.0f} %", ha="center", fontsize=8, color=S.MUET); ax.text(0.5, lo - 4, f"au moins {lo:.0f} %", ha="center", fontsize=8, color=S.MUET)
    s = f["seuil"] * 100; ax.plot([0.1, 0.9], [s, s], color=S.ROUGE, lw=2, ls="--"); ax.text(0.5, s + 1.2, f"seuil de rentabilité : {s:.0f} %", ha="center", fontsize=8.5, color=S.ROUGE)
    ax.set_title("Une fourchette et un seuil", loc="left", fontsize=9)
    S.save(fig, nom)


def fig_reco(f, nom="ch05-reco-graphique.png"):
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    reel, cf = f["marge_reelle"] / 1000, (f["marge_reelle"] - f["incr"]) / 1000
    ax.bar(["Sans soldes\n(estimé)", "Avec soldes\n(réel)"], [cf, reel], color=[S.MUET, S.BLEU], width=0.55)
    ax.set_ylim(0, cf * 1.25); ax.set_ylabel("Marge brute hors taxe (k€)")
    ax.plot([-0.27, 1.45], [cf, cf], color=S.MUET, lw=1, ls=":")
    ax.annotate("", xy=(1.45, reel), xytext=(1.45, cf), arrowprops=dict(arrowstyle="->", color=S.ROUGE, lw=2))
    ax.text(1.52, (cf + reel) / 2, f"− {abs(f['incr']) / 1000:.0f} k€", color=S.ROUGE, fontsize=11, weight="bold", va="center")
    for i, v in enumerate([cf, reel]):
        ax.text(i, v / 2, f"{v:.0f} k€", ha="center", fontsize=10, color="white", weight="bold")
    ax.set_xlim(-0.6, 2.1)
    ax.set_title("Les 153 jours de soldes ont fait perdre de la marge", loc="left")
    S.save(fig, nom)


def fig_demande_floue(nom="ch05-demande-floue.png"):
    fig, ax = plt.subplots(figsize=(7.6, 3.4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 5)
    etapes = [("Demande", "« Je veux un\ntableau de bord. »", S.MUET), ("Besoin", "Je dois décider\nquoi réapprovisionner\nchaque lundi.", S.ORANGE), ("Décision", "Commander ou non,\npar produit,\nchaque semaine.", S.AQUA),
              ("Question", "Quels produits\nrisquent la rupture\nsous 15 jours ?", S.BLEU)]
    for i, (t, s, c) in enumerate(etapes):
        x = 0.2 + i * 3.0
        _boite(ax, x, 1.3, 2.6, 2.6, "", c)
        ax.text(x + 1.3, 3.55, t, ha="center", fontsize=9.5, weight="bold", color=c); ax.text(x + 1.3, 2.4, s, ha="center", va="center", fontsize=8.3, color=S.ENCRE)
        if i < 3:
            ax.add_patch(FancyArrowPatch((x + 2.65, 2.6), (x + 2.95, 2.6), arrowstyle="->", mutation_scale=14, color=S.MUET))
    ax.text(6, 0.7, "Pourquoi ? → Qu'en ferez-vous ? → Comment saura-t-on que c'est réussi ?", ha="center", fontsize=9, color=S.ENCRE2)
    S.save(fig, nom)


def fig_triangle(nom="ch05-negociation.png"):
    fig, ax = plt.subplots(figsize=(5.2, 3.8)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 8)
    pts = np.array([[5, 7], [1, 1.2], [9, 1.2]]); ax.add_patch(plt.Polygon(pts, fc=S.BLEU, alpha=0.1, ec=S.BLEU, lw=1.5))
    ax.text(5, 7.4, "Périmètre", ha="center", weight="bold", color=S.BLEU); ax.text(0.7, 0.6, "Délai", ha="center", weight="bold", color=S.BLEU); ax.text(9.3, 0.6, "Fiabilité", ha="center", weight="bold", color=S.BLEU)
    ax.text(5, 3.3, "On peut en garder deux,\nrarement les trois.\nDire non, c'est proposer\nle compromis.", ha="center", va="center", fontsize=9, color=S.ENCRE)
    S.save(fig, nom)


def fig_boucle(nom="ch05-boucle.png"):
    fig, ax = plt.subplots(figsize=(6.4, 3.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    noms = [("Comprendre\nle besoin", S.BLEU), ("Montrer un\nbrouillon", S.AQUA), ("Recueillir\nles retours", S.ORANGE), ("Corriger,\nlivrer", S.VIOLET)]
    for i, (t, c) in enumerate(noms):
        x = 0.4 + i * 2.4
        _boite(ax, x, 1.6, 2.0, 1.4, t, c, fs=9, alpha=0.18)
        if i < 3:
            ax.add_patch(FancyArrowPatch((x + 2.02, 2.3), (x + 2.38, 2.3), arrowstyle="->", mutation_scale=13, color=S.MUET))
    ax.add_patch(FancyArrowPatch((8.7, 3.1), (1.4, 3.1), connectionstyle="arc3,rad=0.28", arrowstyle="->", mutation_scale=13, color=S.MUET))
    ax.text(5, 4.4, "On montre tôt, on montre souvent : une boucle de retour courte", ha="center", fontsize=9.5, color=S.ENCRE2)
    S.save(fig, nom)


# ------------------------------------------------------------------------------------------------ calculs complémentaires
def luminance(hexa):
    c = np.array([int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(c1, c2="#ffffff"):
    """rapport de contraste WCAG entre deux couleurs hexadécimales (1 à 21)"""
    l1, l2 = sorted([luminance(c1), luminance(c2)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def tableau_contrastes():
    cols = {"bleu": S.BLEU, "orange": S.ORANGE, "aqua": S.AQUA, "violet": S.VIOLET, "rouge": S.ROUGE, "gris du texte": S.ENCRE2, "gris muet": S.MUET}
    return pd.DataFrame({"couleur": list(cols), "sur blanc": [round(contraste(c), 1) for c in cols.values()]})


def simulation_incrementale(f, n=5000, seed=42):
    """incrément de marge simulé : effet tiré autour de l'estimation, marge par commande ordinaire à ±10 %"""
    rng = np.random.default_rng(seed)
    j = f["j"]; pr = j[j["promo_active"] == 1]
    b = np.log(1 + f["e"]); se = (np.log(1 + f["e_haut"]) - np.log(1 + f["e_bas"])) / (2 * 1.96)
    out = []
    for _ in range(n):
        e = np.exp(rng.normal(b, se)) - 1
        out.append(pr["marge"].sum() - pr["nb_commandes"].sum() / (1 + e) * f["mo_np"] * rng.uniform(0.9, 1.1))
    return np.array(out)
