"""Outils du chapitre 1 (principes de visualisation) : chargement des données et fonctions de figures, partagées par le livre et le cahier.

Chaque fonction `fig_*` produit un PNG dans `figures/` (style du livre : `build/style.py`). Le code des figures est ici pour ne pas encombrer le texte.
Les données sont celles de la boutique (volume III) ; tout est simulé."""
import os
import functools
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Wedge
from matplotlib.ticker import FuncFormatter

import style
from style import setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET, GRILLE, AXE, SURFACE, SEQ, DIV

D = os.environ.get("DONNEES") or "donnees"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
CATS = ["Jardin", "Maison", "Décoration", "Cuisine", "Bien-être", "Papeterie"]
PALETTE = [BLEU, ORANGE, AQUA, VIOLET, ROUGE]
GRIS = "#b9b8b0"
setup()


def fr(x, nd=0):
    """nombre à la française : espace pour les milliers, virgule décimale"""
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def _fk(x, _=None):
    return fr(x / 1000) + " k€" if abs(x) >= 1000 else fr(x)


def _titre(ax, t, sous=None):
    """titre à gauche, en gras, avec un sous-titre discret"""
    ax.set_title(t, loc="left", fontsize=10.5, fontweight="bold", color=ENCRE, pad=16 if sous else 8)
    if sous:
        ax.text(0, 1.015, sous, transform=ax.transAxes, fontsize=8.5, color=MUET, va="bottom")


@functools.lru_cache(maxsize=1)
def charger():
    j = pd.read_csv(f"{D}/jours_exploitation.csv", parse_dates=["date"])
    cmd = pd.read_csv(f"{D}/commandes.csv", parse_dates=["date_commande"])
    lig = pd.read_csv(f"{D}/lignes_commande.csv")
    prod = pd.read_csv(f"{D}/produits.csv")
    cli = pd.read_csv(f"{D}/clients.csv")
    x = lig.merge(cmd[["id_commande", "date_commande", "canal", "id_client", "code_promo"]], on="id_commande").merge(prod[["id_produit", "categorie", "nom_produit"]], on="id_produit")
    x["annee"], x["mois"] = x["date_commande"].dt.year, x["date_commande"].dt.month
    sess = pd.read_csv(f"{D}/sessions_web.csv")
    bud = pd.read_csv(f"{D}/budget_reel_2025.csv")
    cr = pd.read_csv(f"{D}/compte_resultat_mensuel.csv")
    liv = pd.read_csv(f"{D}/livraisons.csv")
    ret = pd.read_csv(f"{D}/retours.csv")
    vil = pd.read_csv(f"{D}/villes.csv")
    return dict(j=j, cmd=cmd, lig=lig, prod=prod, cli=cli, x=x, sess=sess, bud=bud, cr=cr, liv=liv, ret=ret, vil=vil)


def ca_mensuel(annee=2025, par=None):
    x = charger()["x"]
    x = x[x["annee"] == annee]
    if par is None:
        return x.groupby("mois")["montant"].sum()
    return x.pivot_table(index="mois", columns=par, values="montant", aggfunc="sum", fill_value=0)


def ca_categories(annee=2025):
    x = charger()["x"]
    return x[x["annee"] == annee].groupby("categorie")["montant"].sum().sort_values(ascending=False)


def conversion_sources():
    s = charger()["sess"]
    return (s.groupby("source")["commande"].mean() * 100).sort_values(ascending=False)


def ca_villes(annee=2025):
    c = charger()
    x = c["x"][c["x"]["annee"] == annee].merge(c["cli"][["id_client", "ville"]], on="id_client")
    return x.groupby("ville")["montant"].sum()


# ------------------------------------------------------------------------------------------------------------------ 1.1 choisir
def fig_arbre():
    """de la question au graphique : un arbre de décision"""
    lignes = [("Comparer des quantités (catégories, canaux)", "barres horizontales, triées"), ("Voir une évolution dans le temps", "courbe (ou barres si peu de points)"),
              ("Montrer une composition (parts d'un total)", "barres empilées à 100 %"), ("Voir la distribution d'une variable", "histogramme, boîte à moustaches"),
              ("Voir une relation entre deux variables", "nuage de points (+ courbe de tendance)"), ("Comparer au budget, à une cible", "barres d'écart ou barres + repère de cible"),
              ("Expliquer le passage d'un total à un autre", "cascade (waterfall)"), ("Suivre une conversion étape par étape", "barres d'entonnoir"),
              ("Croiser deux catégories (jour × mois)", "carte thermique (heatmap)"), ("Situer des lieux", "carte : cercles proportionnels, polygones")]
    fig, ax = plt.subplots(figsize=(9.2, 5.3))
    ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, len(lignes) + 1.2)
    ax.text(0, len(lignes) + 0.75, "Quelle est ma question ?", fontsize=11, fontweight="bold", color=ENCRE)
    ax.text(5.45, len(lignes) + 0.75, "Quel graphique ?", fontsize=11, fontweight="bold", color=ENCRE)
    for i, (q, g) in enumerate(lignes):
        y = len(lignes) - i - 0.3
        ax.add_patch(FancyBboxPatch((0, y - 0.32), 5.0, 0.64, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#e8f0fb", ec=BLEU, lw=0.8))
        ax.text(0.15, y, q, va="center", fontsize=8.8, color=ENCRE)
        ax.annotate("", xy=(5.4, y), xytext=(5.05, y), arrowprops=dict(arrowstyle="-|>", color=MUET, lw=1))
        ax.add_patch(FancyBboxPatch((5.45, y - 0.32), 4.5, 0.64, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#e6f6ef", ec=AQUA, lw=0.8))
        ax.text(5.6, y, g, va="center", fontsize=8.8, color=ENCRE)
    save(fig, "ch01-arbre.png")


def fig_encodages():
    """la même série de six valeurs, encodée par la position, la longueur, l'angle, l'aire et la couleur"""
    s = ca_categories()
    v = s.values / 1000
    n = len(v)
    fig, axs = plt.subplots(1, 5, figsize=(12.5, 3.0))
    for a in axs:
        a.set_xticks([]); a.set_yticks([]); a.grid(False)
        for sp in a.spines.values():
            sp.set_visible(False)
    a = axs[0]; a.set_xlim(-160, 400); a.set_ylim(-0.5, n - 0.5)
    for i, val in enumerate(v):
        a.plot([val], [n - 1 - i], "o", color=BLEU, ms=7)
    a.axhline(-0.5, color=AXE, lw=0.8); a.set_title("Position\n(le plus précis)", fontsize=9.5, color=ENCRE)
    for i, nom in enumerate(s.index):
        a.text(-155, n - 1 - i, nom, fontsize=7.5, va="center", color=MUET)
    a = axs[1]; a.set_xlim(0, 400); a.set_ylim(-0.5, n - 0.5)
    for i, val in enumerate(v):
        a.barh(n - 1 - i, val, height=0.6, color=BLEU)
    a.set_title("Longueur\n(très précis)", fontsize=9.5, color=ENCRE)
    a = axs[2]; a.set_aspect("equal"); a.set_xlim(-1.1, 1.1); a.set_ylim(-1.1, 1.1)
    ang = 90
    for i, val in enumerate(v):
        w = 360 * val / v.sum()
        a.add_patch(Wedge((0, 0), 1, ang - w, ang, fc=PALETTE[i % 5] if i < 5 else MUET, ec="white", lw=1))
        ang -= w
    a.set_title("Angle\n(moyennement précis)", fontsize=9.5, color=ENCRE)
    a = axs[3]; a.set_aspect("equal"); a.set_xlim(-0.6, 6.4); a.set_ylim(-0.7, 3.1)
    for i, val in enumerate(v):
        a.add_patch(Circle((0.55 + (i % 3) * 2.1, 2.1 - (i // 3) * 1.8), 0.9 * np.sqrt(val / v.max()), fc=BLEU, ec="white"))
    a.set_title("Aire\n(peu précis)", fontsize=9.5, color=ENCRE)
    a = axs[4]; a.set_xlim(0, 3); a.set_ylim(0, 2)
    for i, val in enumerate(v):
        a.add_patch(Rectangle(((i % 3) * 1.0, 1 - (i // 3) * 1.0), 0.95, 0.95, fc=SEQ(0.15 + 0.85 * val / v.max()), ec="white"))
    a.set_title("Couleur (intensité)\n(le moins précis)", fontsize=9.5, color=ENCRE)
    fig.suptitle("Les mêmes six chiffres d'affaires par catégorie, encodés de cinq façons : dans quel ordre se rangent-ils le plus facilement ?", fontsize=10, color=ENCRE2, x=0.01, ha="left", y=1.08)
    save(fig, "ch01-encodages.png")


def fig_quatre_facons():
    """le même jeu de données (CA mensuel 2025 par canal) dit de quatre façons"""
    p = ca_mensuel(2025, "canal") / 1000
    cols = {"Boutique": BLEU, "Site": ORANGE, "Réseaux": AQUA}
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 6.2))
    a = axs[0, 0]; w = 0.27
    for k, c in enumerate(cols):
        a.bar(p.index + (k - 1) * w, p[c], w, color=cols[c], label=c)
    a.set_title("Barres groupées : comparer les canaux mois par mois", loc="left", fontsize=9.5)
    a.legend(ncol=3, fontsize=8, loc="upper left")
    a = axs[0, 1]
    for c in cols:
        a.plot(p.index, p[c], color=cols[c], lw=2)
        a.text(12.15, p[c].iloc[-1], c, color=cols[c], fontsize=8.5, va="center")
    a.set_xlim(1, 13.6); a.set_title("Courbes : suivre l'évolution de chaque canal", loc="left", fontsize=9.5)
    a = axs[1, 0]
    a.stackplot(p.index, [p[c] for c in cols], colors=list(cols.values()), labels=list(cols))
    a.set_title("Aires empilées : voir le total et sa composition", loc="left", fontsize=9.5); a.legend(ncol=3, fontsize=8, loc="upper left")
    a = axs[1, 1]
    im = a.imshow(p[list(cols)].T.values, aspect="auto", cmap=SEQ)
    a.set_yticks(range(3)); a.set_yticklabels(list(cols)); a.set_xticks(range(12)); a.set_xticklabels([m[:1].upper() for m in MOIS]); a.grid(False)
    a.set_title("Carte thermique : repérer les mois forts de chaque canal", loc="left", fontsize=9.5)
    for ax in axs.ravel()[:3]:
        ax.set_xticks(range(1, 13)); ax.set_xticklabels([m[:1].upper() for m in MOIS]); ax.set_ylabel("k€")
    fig.tight_layout()
    save(fig, "ch01-quatre-facons.png")


def fig_galerie():
    """une question, un graphique : huit petits exemples sur les données de la boutique"""
    c = charger()
    fig, axs = plt.subplots(2, 4, figsize=(13, 6.4))
    a = axs[0, 0]; s = ca_categories().sort_values() / 1000
    a.barh(s.index, s.values, color=BLEU); a.set_title("Comparer\nCA 2025 par catégorie (k€)", loc="left", fontsize=9); a.grid(False)
    a = axs[0, 1]; m = ca_mensuel() / 1000
    a.plot(m.index, m.values, color=BLEU); a.set_xticks([1, 4, 7, 10]); a.set_xticklabels(["janv.", "avr.", "juil.", "oct."]); a.set_title("Évolution\nCA mensuel 2025 (k€)", loc="left", fontsize=9)
    a = axs[0, 2]; t = c["x"].groupby(["annee", "canal"])["montant"].sum().unstack(); t = t.div(t.sum(axis=1), axis=0) * 100
    bas = np.zeros(3)
    for k, cn in enumerate(["Boutique", "Site", "Réseaux"]):
        a.bar(t.index.astype(str), t[cn], bottom=bas, color=[BLEU, ORANGE, AQUA][k], label=cn); bas += t[cn].values
    a.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3); a.set_title("Composition\nPart des canaux dans le CA (%)", loc="left", fontsize=9); a.grid(False)
    a = axs[0, 3]; pan = c["lig"].groupby("id_commande")["montant"].sum()
    a.hist(pan, bins=40, color=BLEU); a.set_title("Distribution\nMontant d'une commande (€)", loc="left", fontsize=9)
    a = axs[1, 0]; w = c["j"].assign(sem=c["j"]["date"].dt.to_period("W")).groupby("sem").agg(pub=("depense_pub", "sum"), cmd=("nb_commandes", "sum")).iloc[1:-1]
    a.scatter(w["pub"] / 1000, w["cmd"], s=6, color=BLEU, alpha=0.5); a.set_title("Relation\nPublicité et commandes (par semaine)", loc="left", fontsize=9)
    a = axs[1, 1]; g = c["bud"].groupby("categorie")[["ca_budget", "ca_reel"]].sum(); e = ((g["ca_reel"] / g["ca_budget"] - 1) * 100).sort_values()
    a.barh(e.index, e.values, color=[ROUGE if v < 0 else AQUA for v in e.values]); a.axvline(0, color=ENCRE2, lw=0.8); a.set_title("Écart à une cible\nRéalisé / budget 2025 (%)", loc="left", fontsize=9); a.grid(False)
    a = axs[1, 2]; s = c["sess"]; et = [len(s), s["ajout_panier"].sum(), s["debut_paiement"].sum(), s["commande"].sum()]
    a.barh(["Sessions", "Panier", "Paiement", "Commande"][::-1], et[::-1], color=BLEU); a.set_title("Entonnoir\nSessions du site 2025", loc="left", fontsize=9); a.grid(False)
    a.xaxis.set_major_formatter(FuncFormatter(lambda x, _: fr(x / 1000) + " k"))
    a = axs[1, 3]; v = c["vil"].merge(ca_villes().rename("ca"), left_on="ville", right_index=True)
    a.scatter(v["x_km"], v["y_km"], s=v["ca"] / 1200, color=BLEU, alpha=0.55, edgecolor="white"); a.set_title("Géographie\nCA 2025 par ville (cercles)", loc="left", fontsize=9)
    a.set_xticks([]); a.set_yticks([]); a.grid(False); a.set_aspect("equal")
    fig.tight_layout()
    save(fig, "ch01-galerie.png")


def fig_camembert():
    """camembert à six parts contre barres triées"""
    s = ca_categories()
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw={"width_ratios": [1, 1.25]})
    cols = [BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET]
    axs[0].pie(s.values, labels=s.index, colors=cols, startangle=90, wedgeprops=dict(ec="white"), textprops=dict(fontsize=8.5))
    axs[0].set_title("Camembert : on devine l'ordre, pas les écarts", loc="left", fontsize=9.5)
    t = s.sort_values() / s.sum() * 100
    axs[1].barh(t.index, t.values, color=BLEU); axs[1].grid(False)
    for i, v in enumerate(t.values):
        axs[1].text(v + 0.5, i, fr(v, 1) + " %", va="center", fontsize=8.5, color=ENCRE)
    axs[1].set_xlim(0, 33); axs[1].set_title("Barres triées : l'ordre et les écarts se lisent", loc="left", fontsize=9.5)
    axs[1].set_xticks([])
    fig.tight_layout()
    save(fig, "ch01-camembert.png")


def fig_cascade():
    """cascade : du résultat de la marge brute au résultat d'exploitation 2025"""
    cr = charger()["cr"]
    d = cr[cr["mois"].str[:4] == "2025"].sum(numeric_only=True)
    etapes = [("Marge brute", d["marge_brute"]), ("Personnel", -d["frais_personnel"]), ("Loyers", -d["loyers_charges"]), ("Marketing", -d["marketing"]),
              ("Livraison", -d["livraison"]), ("Frais\nbancaires", -d["frais_bancaires"]), ("Amort.", -d["amortissements"]), ("Autres", -d["autres_charges"])]
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    cum = 0
    for i, (nom, v) in enumerate(etapes):
        if i == 0:
            ax.bar(i, v, color=BLEU); cum = v
            ax.text(i, v + 6000, fr(v / 1000) + " k€", ha="center", fontsize=8.5, color=ENCRE)
        else:
            ax.bar(i, v, bottom=cum, color=ROUGE)
            ax.text(i, cum + 6000, fr(v / 1000).replace("-", "−") + " k€", ha="center", fontsize=8.5, color=ENCRE); cum += v
    ax.bar(len(etapes), cum, color=AQUA); ax.text(len(etapes), cum + 6000, fr(cum / 1000) + " k€", ha="center", fontsize=8.5, color=ENCRE)
    ax.set_xticks(range(len(etapes) + 1)); ax.set_xticklabels([e[0] for e in etapes] + ["Résultat"], fontsize=8.5); ax.set_yticks([]); ax.grid(False); ax.set_ylim(0, etapes[0][1] * 1.12)
    ax.set_title("De la marge brute au résultat d'exploitation, 2025 : les charges font le trajet", loc="left", fontsize=10, fontweight="bold", color=ENCRE, pad=14)
    save(fig, "ch01-cascade.png")
    return cum


def fig_heatmap_semaine():
    x = charger()["x"]
    x = x[x["annee"] == 2025].copy()
    c = x.drop_duplicates("id_commande")
    c = c.assign(jour=c["date_commande"].dt.dayofweek)
    t = c.groupby(["jour", "mois"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8.8, 3.3))
    im = ax.imshow(t.values, cmap=SEQ, aspect="auto")
    ax.set_yticks(range(7)); ax.set_yticklabels(JOURS); ax.set_xticks(range(12)); ax.set_xticklabels(MOIS, fontsize=8.5); ax.grid(False)
    for i in range(7):
        for k in range(12):
            ax.text(k, i, int(t.values[i, k]), ha="center", va="center", fontsize=7, color="white" if t.values[i, k] > t.values.max() * 0.55 else ENCRE)
    ax.set_title("Commandes de 2025 : le samedi et la fin d'année dominent", loc="left", fontsize=10, fontweight="bold", color=ENCRE)
    save(fig, "ch01-heatmap.png")


def fig_camembert_neuf():
    """camembert à neuf parts contre barres"""
    s = ca_villes().sort_values(ascending=False)
    top = pd.concat([s.head(8), pd.Series({"Autres villes": s.iloc[8:].sum()})])
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1, 1.2]})
    cmap = plt.get_cmap("tab10")
    axs[0].pie(top.values, labels=top.index, colors=[cmap(i) for i in range(9)], startangle=90, wedgeprops=dict(ec="white"), textprops=dict(fontsize=7.5))
    axs[0].set_title("Neuf parts : légende illisible, parts voisines", loc="left", fontsize=9.5)
    t = pd.concat([top.iloc[[8]], top.iloc[:8].sort_values()]) / top.sum() * 100
    axs[1].barh(t.index, t.values, color=[GRIS if k == "Autres villes" else BLEU for k in t.index]); axs[1].grid(False); axs[1].set_xticks([])
    for i, v in enumerate(t.values):
        axs[1].text(v + 0.3, i, fr(v, 1) + " %", va="center", fontsize=8.5)
    axs[1].set_title("Barres triées : le classement se lit d'un coup d'œil", loc="left", fontsize=9.5); axs[1].set_xlim(0, t.max() * 1.18)
    fig.tight_layout()
    save(fig, "ch01-camembert-neuf.png")


# ------------------------------------------------------------------------------------------------------------------ 1.2 clarté
def _brouillon(ax):
    s = conversion_sources()
    ordre = ["reseaux", "direct", "payant", "email", "referent", "organique"]
    v = [s[k] for k in ordre]
    cols = ["#ff0000", "#00cc00", "#0000ff", "#ffcc00", "#ff00ff", "#00cccc"]
    b = ax.bar(ordre, v, color=cols, label=ordre)
    ax.grid(True, color="black", lw=0.5); ax.set_title("Graphique 1", fontsize=10); ax.set_ylabel("valeur"); ax.legend(fontsize=6, ncol=2)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    return s


def fig_redessin_avant_apres():
    """avant / après : la conversion du site selon la source"""
    s = conversion_sources().sort_values()
    noms = {"email": "E-mail", "direct": "Direct", "organique": "Recherche naturelle", "referent": "Sites partenaires", "payant": "Publicité payante", "reseaux": "Réseaux sociaux"}
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.4), gridspec_kw={"width_ratios": [1, 1.25]})
    with plt.rc_context({"axes.facecolor": "white", "figure.facecolor": "white", "axes.spines.right": True, "axes.spines.top": True}):
        _brouillon(axs[0])
    a = axs[1]
    cols = [BLEU if k == "email" else GRIS for k in s.index]
    a.barh([noms[k] for k in s.index], s.values, color=cols); a.grid(False); a.set_xticks([])
    for sp in ("bottom", "left"):
        a.spines[sp].set_visible(False)
    for i, (k, v) in enumerate(s.items()):
        a.text(v + 0.12, i, fr(v, 1) + " %", va="center", fontsize=9, color=ENCRE, fontweight="bold" if k == "email" else "normal")
    a.set_xlim(0, 10.3)
    a.set_title("Un visiteur venu d'un e-mail commande 4 fois plus souvent\nqu'un visiteur venu des réseaux sociaux", loc="left", fontsize=10.5, fontweight="bold", color=ENCRE)
    a.text(0, -0.9, "Part des sessions du site qui se terminent par une commande, 2025. Source : sessions web (127 022 sessions).", fontsize=8, color=MUET, transform=a.transData)
    fig.tight_layout(w_pad=3)
    save(fig, "ch01-avant-apres.png")


def fig_redessin_etapes():
    """cinq étapes de nettoyage du même graphique"""
    s = conversion_sources()
    noms = {"email": "E-mail", "direct": "Direct", "organique": "Recherche naturelle", "referent": "Sites partenaires", "payant": "Publicité payante", "reseaux": "Réseaux sociaux"}
    ordre = ["reseaux", "direct", "payant", "email", "referent", "organique"]
    fig, axs = plt.subplots(2, 3, figsize=(12.5, 6.4))
    # 0 brouillon
    a = axs[0, 0]
    with plt.rc_context({"axes.facecolor": "white"}):
        a.bar(ordre, [s[k] for k in ordre], color=["#ff0000", "#00cc00", "#0000ff", "#ffcc00", "#ff00ff", "#00cccc"], label=ordre); a.grid(True, color="black", lw=0.4)
    a.legend(fontsize=5, ncol=2); a.tick_params(axis="x", rotation=60, labelsize=6); a.set_title("0. Le brouillon (réglages par défaut)", loc="left", fontsize=9)
    # 1 trier
    t = s.sort_values()
    a = axs[0, 1]; a.barh([noms[k] for k in t.index], t.values, color=["#ff0000", "#00cc00", "#0000ff", "#ffcc00", "#ff00ff", "#00cccc"]); a.tick_params(labelsize=7)
    a.set_title("1. Ranger : barres horizontales, triées", loc="left", fontsize=9)
    # 2 couleur
    a = axs[0, 2]; a.barh([noms[k] for k in t.index], t.values, color=[BLEU if k == "email" else GRIS for k in t.index]); a.tick_params(labelsize=7)
    a.set_title("2. Une couleur, un accent sur le message", loc="left", fontsize=9)
    # 3 étiquettes directes, sans grille
    a = axs[1, 0]; a.barh([noms[k] for k in t.index], t.values, color=[BLEU if k == "email" else GRIS for k in t.index]); a.grid(False); a.set_xticks([]); a.tick_params(labelsize=7)
    for i, v in enumerate(t.values):
        a.text(v + 0.1, i, fr(v, 1) + " %", va="center", fontsize=7.5)
    a.set_xlim(0, 10); a.set_title("3. Étiqueter directement, retirer grille et axe", loc="left", fontsize=9)
    # 4 titre informatif
    a = axs[1, 1]; a.barh([noms[k] for k in t.index], t.values, color=[BLEU if k == "email" else GRIS for k in t.index]); a.grid(False); a.set_xticks([]); a.tick_params(labelsize=7)
    for i, v in enumerate(t.values):
        a.text(v + 0.1, i, fr(v, 1) + " %", va="center", fontsize=7.5)
    for sp in ("bottom", "left"):
        a.spines[sp].set_visible(False)
    a.set_xlim(0, 10)
    a.set_title("4. Un titre qui énonce la conclusion + la source\nL'e-mail convertit 4 fois mieux que les réseaux sociaux", loc="left", fontsize=8.5, color=ENCRE)
    a.text(0, -1.15, "Sessions se terminant par une commande, 2025. Source : sessions web.", fontsize=6.5, color=MUET, transform=a.transData)
    a2 = axs[1, 2]; a2.axis("off")
    a2.text(0, 0.95, "Liste de contrôle", fontsize=10, fontweight="bold", color=ENCRE, va="top")
    for i, l in enumerate(["Ai-je une seule idée ?", "Le titre dit-il la conclusion ?", "Les barres sont-elles triées ?", "Les couleurs ont-elles un sens ?", "Puis-je retirer quelque chose ?", "L'unité et la source sont-elles là ?"]):
        a2.text(0.02, 0.8 - i * 0.13, "–  " + l, fontsize=9, color=ENCRE2, va="top")
    fig.tight_layout()
    save(fig, "ch01-etapes.png")


def fig_titre():
    """titre descriptif contre titre informatif, même graphique"""
    m = ca_mensuel() / 1000
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for a in axs:
        a.plot(m.index, m.values, color=BLEU, lw=2.2); a.set_xticks(range(1, 13)); a.set_xticklabels([k[:1].upper() for k in MOIS]); a.set_ylim(0, 200)
    axs[0].set_title("Chiffre d'affaires mensuel 2025", loc="left", fontsize=10); axs[0].set_ylabel("k€")
    a = axs[1]
    part = (m[11] + m[12]) / m.sum() * 100
    a.set_title(f"Le CA mensuel est multiplié par {fr(m[12] / m[2], 1)} entre février et décembre :\nnovembre et décembre font {fr(part)} % de l'année", loc="left", fontsize=10, fontweight="bold", color=ENCRE, pad=10)
    a.annotate(f"Février : {fr(m[2])} k€", xy=(2, m[2]), xytext=(2.4, 25), arrowprops=dict(arrowstyle="-", color=MUET), fontsize=8.5, color=ENCRE2)
    a.annotate(f"Décembre : {fr(m[12])} k€", xy=(12, m[12]), xytext=(8.2, 192), arrowprops=dict(arrowstyle="-", color=MUET), fontsize=8.5, color=ENCRE2)
    a.axvspan(10.5, 12.5, color=ORANGE, alpha=0.12); a.text(11.5, 20, "novembre-\ndécembre", ha="center", fontsize=8, color=ORANGE)
    fig.tight_layout()
    save(fig, "ch01-titre.png")
    return m


def fig_petits_multiples():
    p = ca_mensuel(2025, "categorie") / 1000
    cols = [BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET]
    fig = plt.figure(figsize=(12.5, 4.3))
    gs = fig.add_gridspec(2, 5, width_ratios=[2.2, 1, 1, 1, 0.02])
    a = fig.add_subplot(gs[:, 0])
    for k, c in enumerate(CATS):
        a.plot(p.index, p[c], color=cols[k], lw=1.6, label=c)
    a.legend(fontsize=7, ncol=2, loc="upper left"); a.set_title("Six courbes sur un seul graphique :\nqui est qui ?", loc="left", fontsize=9.5); a.set_xticks([1, 4, 7, 10]); a.set_xticklabels(["janv.", "avr.", "juil.", "oct."])
    for k, c in enumerate(CATS):
        b = fig.add_subplot(gs[k // 3, 1 + k % 3])
        for c2 in CATS:
            b.plot(p.index, p[c2], color=GRILLE, lw=1)
        b.plot(p.index, p[c], color=BLEU, lw=2)
        b.set_title(c, loc="left", fontsize=9, color=ENCRE); b.set_xticks([]); b.set_ylim(0, p.values.max() * 1.05)
        if k % 3: b.set_yticklabels([])
    fig.suptitle("Petits multiples : la même échelle, une catégorie par case, les autres en gris", x=0.37, y=1.02, fontsize=10, fontweight="bold", color=ENCRE)
    save(fig, "ch01-petits-multiples.png")


def fig_projection():
    """le même graphique en petite et en grande police, vu en projection"""
    s = conversion_sources().sort_values()
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6))
    for a, fs, t in ((axs[0], 6.5, "Polices de 6,5 points : illisible au fond d'une salle"), (axs[1], 12, "Polices de 12 points : lisible à trois mètres")):
        a.barh([{"reseaux": "réseaux", "referent": "référent"}.get(k, k) for k in s.index], s.values, color=BLEU); a.tick_params(labelsize=fs); a.set_title(t, loc="left", fontsize=fs + 1.5)
        a.set_xlabel("taux de conversion (%)", fontsize=fs)
        a.grid(False)
        for i, v in enumerate(s.values):
            a.text(v + 0.1, i, fr(v, 1), va="center", fontsize=fs)
        a.set_xlim(0, 10.5); a.set_xticks([])
    fig.tight_layout()
    save(fig, "ch01-projection.png")


# ------------------------------------------------------------------------------------------------------------------ 1.3 couleurs
def fig_palettes():
    c = charger()
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.8), gridspec_kw={"width_ratios": [1, 1.35, 1.35]})
    s = ca_categories() / 1000
    axs[0].bar(range(6), s.values, color=[BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET]); axs[0].set_xticks(range(6)); axs[0].set_xticklabels(list(s.index), fontsize=7.5, rotation=30, ha="right")
    axs[0].set_title("Qualitative : des catégories sans ordre", loc="left", fontsize=9.5); axs[0].grid(False)
    x = c["x"][c["x"]["annee"] == 2025]
    t = x.pivot_table(index="categorie", columns="mois", values="montant", aggfunc="sum").reindex(CATS)
    im = axs[1].imshow(t.values / 1000, cmap=SEQ, aspect="auto"); axs[1].set_yticks(range(6)); axs[1].set_yticklabels(CATS, fontsize=8); axs[1].set_xticks(range(12)); axs[1].set_xticklabels([m[:1].upper() for m in MOIS], fontsize=8); axs[1].grid(False)
    axs[1].set_title("Séquentielle : du faible au fort (k€)", loc="left", fontsize=9.5); plt.colorbar(im, ax=axs[1], fraction=0.04, pad=0.02)
    b = c["bud"].pivot_table(index="categorie", columns="mois", values=["ca_budget", "ca_reel"], aggfunc="sum")
    e = ((b["ca_reel"] / b["ca_budget"] - 1) * 100).reindex(CATS)
    lim = 25
    im = axs[2].imshow(e.values, cmap=DIV.reversed(), vmin=-lim, vmax=lim, aspect="auto"); axs[2].set_yticks(range(6)); axs[2].set_yticklabels(CATS, fontsize=8); axs[2].set_xticks(range(12)); axs[2].set_xticklabels([m[:1].upper() for m in MOIS], fontsize=8); axs[2].grid(False)
    axs[2].set_title("Divergente : écart au budget, centré sur 0 (%)\nbleu : au-dessus du budget, rouge : en dessous", loc="left", fontsize=9.5); plt.colorbar(im, ax=axs[2], fraction=0.04, pad=0.02)
    fig.tight_layout()
    save(fig, "ch01-palettes.png")


# matrices de simulation de la vision des couleurs (Machado, Oliveira, Fernandes 2009, sévérité 1,0)
MATRICES = {"Protanopie": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
            "Deutéranopie": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
            "Tritanopie": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])}


def _rgb(c):
    return np.array(matplotlib.colors.to_rgb(c))


def simuler(c, nom):
    """couleur telle que la voit une personne atteinte d'une déficience de la vision des couleurs (ou en niveaux de gris)"""
    v = _rgb(c)
    if nom == "Niveaux de gris":
        g = 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
        return (g, g, g)
    lin = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    o = MATRICES[nom] @ lin
    o = np.clip(o, 0, 1)
    out = np.where(o <= 0.0031308, 12.92 * o, 1.055 * o ** (1 / 2.4) - 0.055)
    return tuple(np.clip(out, 0, 1))


def luminance(c):
    v = _rgb(c)
    lin = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(c1, c2):
    """rapport de contraste WCAG entre deux couleurs"""
    a, b = sorted([luminance(c1), luminance(c2)], reverse=True)
    return (a + 0.05) / (b + 0.05)


def fig_daltonisme():
    mauvais = ["#d62728", "#2ca02c", "#bcbd22", "#8c564b", "#1f77b4"]
    vues = ["Vision typique", "Protanopie", "Deutéranopie", "Tritanopie", "Niveaux de gris"]
    fig, axs = plt.subplots(2, 5, figsize=(13, 4.6))
    noms = ["Boutique", "Site", "Réseaux", "Marketplace", "Revendeurs"]
    val = [8, 6, 5, 4, 3]
    for r, (pal, tit) in enumerate(((mauvais, "Palette « rouge-vert » classique"), (PALETTE, "Palette du livre"))):
        for k, v in enumerate(vues):
            a = axs[r, k]
            cols = [pal[i] if v == "Vision typique" else simuler(pal[i], v) for i in range(5)]
            a.bar(range(5), val, color=cols); a.set_xticks([]); a.set_yticks([]); a.grid(False)
            for sp in a.spines.values():
                sp.set_visible(False)
            a.set_title(v if r == 0 else "", fontsize=9, color=ENCRE)
        axs[r, 0].set_ylabel(tit, fontsize=8.5, rotation=90, labelpad=6)
    fig.suptitle("Les mêmes barres vues par différentes personnes : on ne doit jamais compter sur la couleur seule", x=0.01, ha="left", y=1.0, fontsize=10, color=ENCRE2)
    fig.tight_layout()
    save(fig, "ch01-daltonisme.png")


def fig_contraste():
    couples = [("Texte principal", ENCRE, SURFACE), ("Texte secondaire", ENCRE2, SURFACE), ("Texte discret (graduations)", MUET, SURFACE), ("Bleu sur fond clair", BLEU, SURFACE),
               ("Orange sur fond clair", ORANGE, SURFACE), ("Aqua sur fond clair", AQUA, SURFACE), ("Blanc sur bleu", "#ffffff", BLEU), ("Gris clair sur blanc", "#c8c8c8", "#ffffff")]
    fig, ax = plt.subplots(figsize=(9.5, 4.0)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, len(couples) + 0.5)
    for i, (n, fg, bg) in enumerate(couples):
        y = len(couples) - i - 0.4
        r = contraste(fg, bg)
        ax.add_patch(Rectangle((0, y - 0.38), 4.6, 0.76, fc=bg, ec=AXE, lw=0.6)); ax.text(0.15, y, "Livraison en retard : 12 commandes", color=fg, fontsize=9, va="center")
        ax.text(4.8, y, n, fontsize=8.8, va="center", color=ENCRE)
        ax.text(8.0, y, f"{fr(r, 1)} : 1", fontsize=9, va="center", fontweight="bold", color=ENCRE)
        ax.text(9.0, y, "AA" if r >= 4.5 else ("grand texte" if r >= 3 else "insuffisant"), fontsize=8.5, va="center", color=AQUA if r >= 4.5 else (ORANGE if r >= 3 else ROUGE))
    ax.set_title("Rapport de contraste (seuil de lisibilité usuel : 4,5 : 1 pour un texte courant, 3 : 1 pour un grand texte)", loc="left", fontsize=9.5, color=ENCRE2)
    save(fig, "ch01-contraste.png")


def fig_systeme_design():
    """une page de règles pour les tableaux de bord de la boutique (dessinée)"""
    fig = plt.figure(figsize=(11.5, 6.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 6.4)
    ax.text(0.3, 6.05, "Système de design — tableaux de bord de la boutique", fontsize=13, fontweight="bold", color=ENCRE)
    ax.text(0.3, 5.75, "Une page de règles, relue avant chaque nouveau tableau de bord", fontsize=9, color=MUET)
    ax.text(0.3, 5.3, "1. Palette", fontsize=10, fontweight="bold", color=ENCRE)
    for i, (n, c) in enumerate([("Bleu : principal", BLEU), ("Orange : à regarder", ORANGE), ("Aqua : favorable", AQUA), ("Violet : secondaire", VIOLET), ("Rouge : défavorable", ROUGE), ("Gris : contexte", GRIS)]):
        ax.add_patch(Rectangle((0.3 + i * 1.85, 4.55), 1.75, 0.55, fc=c, ec="none")); ax.text(0.3 + i * 1.85, 4.4, n, fontsize=7.5, color=ENCRE2, va="top")
    ax.text(0.3, 3.85, "2. Typographie", fontsize=10, fontweight="bold", color=ENCRE)
    for i, (t, fs) in enumerate([("Titre de page : 20 pt gras", 14), ("Titre de graphique : 14 pt gras, énonce la conclusion", 11), ("Texte et étiquettes : 11 pt", 9), ("Source et notes : 9 pt, gris", 7.5)]):
        ax.text(0.3, 3.55 - i * 0.3, t, fontsize=fs, color=ENCRE if i < 3 else MUET, va="center", fontweight="bold" if i < 2 else "normal")
    ax.text(6.0, 3.85, "3. Grille et espacements", fontsize=10, fontweight="bold", color=ENCRE)
    for i in range(4):
        ax.add_patch(Rectangle((6.0 + i * 1.3, 2.75), 1.2, 0.85, fc="#e8f0fb", ec=BLEU, lw=0.8))
    ax.text(6.0, 2.55, "Marge de 16 px · gouttière de 12 px · quatre colonnes · jamais plus de six visuels par page", fontsize=7.5, color=ENCRE2, va="top")
    ax.text(0.3, 2.15, "4. Composants", fontsize=10, fontweight="bold", color=ENCRE)
    ax.add_patch(FancyBboxPatch((0.3, 0.7), 2.4, 1.2, boxstyle="round,pad=0.02,rounding_size=0.1", fc="white", ec=AXE)); ax.text(0.45, 1.65, "Chiffre d'affaires, 2025", fontsize=8, color=MUET); ax.text(0.45, 1.2, "1 325 k€", fontsize=17, fontweight="bold", color=ENCRE); ax.text(0.45, 0.85, "+11,4 % sur 2024", fontsize=8.5, color=AQUA)
    ax.add_patch(FancyBboxPatch((3.0, 0.7), 3.2, 1.2, boxstyle="round,pad=0.02,rounding_size=0.1", fc="white", ec=AXE)); ax.text(3.15, 1.65, "Carte de graphique", fontsize=8, color=MUET)
    xs = np.linspace(3.2, 6.0, 12); ys = 0.95 + 0.5 * np.array([0.2, 0.1, 0.3, 0.4, 0.5, 0.5, 0.55, 0.3, 0.6, 0.7, 0.9, 1.0]) * 0.8
    ax.plot(xs, ys, color=BLEU, lw=2)
    ax.text(6.5, 1.8, "5. Conventions", fontsize=10, fontweight="bold", color=ENCRE)
    for i, t in enumerate(["Un titre = une conclusion", "Toujours : période, unité, source", "Écarts : vert = favorable, rouge = défavorable", "…et jamais la couleur seule : ajouter ▲ ▼ ou un mot", "Noms : « CA hors taxe », jamais « CA » seul", "Les chiffres : espace des milliers, virgule décimale"]):
        ax.text(6.5, 1.5 - i * 0.24, "• " + t, fontsize=8, color=ENCRE2, va="center")
    save(fig, "ch01-design.png")


# ------------------------------------------------------------------------------------------------------------------ 1.4 trompeurs
def fig_axe_tronque():
    x = charger()["x"]
    t = x.groupby("annee")["montant"].sum() / 1000
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.7))
    for a, tronque in zip(axs, (True, False)):
        a.bar(t.index.astype(str), t.values, color=[GRIS, GRIS, BLEU]); a.grid(False)
        for i, v in enumerate(t.values):
            a.text(i, v + (5 if tronque else 15), fr(v) + " k€", ha="center", fontsize=9, color=ENCRE)
        a.set_yticks([])
        for sp in ("left",):
            a.spines[sp].set_visible(False)
    rv = (t.iloc[-1] - 1100) / (t.iloc[0] - 1100)
    axs[0].set_ylim(1100, 1350); axs[0].set_title(f"Axe tronqué à 1 100 k€ : 2025 paraît {fr(rv, 1)} fois plus haut que 2023", loc="left", fontsize=9.5, color=ROUGE)
    axs[1].set_ylim(0, 1500); axs[1].set_title(f"Axe à zéro : {fr((t.iloc[-1] / t.iloc[0] - 1) * 100)} % en deux ans, pas {fr((rv - 1) * 100)} %", loc="left", fontsize=9.5, color=AQUA)
    fig.tight_layout()
    save(fig, "ch01-axe-tronque.png")
    return t


def fig_echelles():
    p = ca_mensuel(2025, "canal") / 1000
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 5.2), sharex=True)
    for k, c in enumerate(["Boutique", "Réseaux"]):
        a = axs[0, k]; a.plot(p.index, p[c], color=[BLEU, AQUA][k]); a.set_title(c + " : axe propre à chaque graphique", loc="left", fontsize=9.5); a.set_ylabel("k€")
        b = axs[1, k]; b.plot(p.index, p[c], color=[BLEU, AQUA][k]); b.set_ylim(0, 85); b.set_title(c + " : même axe (0 à 85 k€)", loc="left", fontsize=9.5); b.set_ylabel("k€")
    for a in axs[1]:
        a.set_xticks(range(1, 13)); a.set_xticklabels([m[:1].upper() for m in MOIS])
    fig.tight_layout()
    save(fig, "ch01-echelles.png")
    return p


def fig_double_axe():
    c = charger()
    m = c["j"].assign(mois=c["j"]["date"].dt.to_period("M")).groupby("mois").agg(pub=("depense_pub", "sum"), cmd=("nb_commandes", "sum"))
    m = m[m.index.year == 2025]
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    a = axs[0]; a2 = a.twinx()
    a.plot(range(12), m["pub"] / 1000, color=BLEU); a2.plot(range(12), m["cmd"], color=ORANGE); a2.grid(False)
    a.set_ylim(0, 14); a2.set_ylim(0, 2000); a.set_xticks(range(12)); a.set_xticklabels([k[:1].upper() for k in MOIS])
    a.set_ylabel("publicité (k€)", color=BLEU); a2.set_ylabel("commandes", color=ORANGE); a.set_title("Double axe : deux échelles choisies pour que les courbes coïncident", loc="left", fontsize=9.5, color=ROUGE)
    b = axs[1]
    b.scatter(m["pub"] / 1000, m["cmd"], color=BLEU); b.set_xlabel("publicité du mois (k€)"); b.set_ylabel("commandes du mois")
    r = np.corrcoef(m["pub"], m["cmd"])[0, 1]
    b.set_title("Un nuage : la relation se voit, et se calcule", loc="left", fontsize=9.5, color=AQUA)
    fig.tight_layout()
    save(fig, "ch01-double-axe.png")
    return r


def fig_cerises():
    m = ca_mensuel(2025) / 1000
    x = charger()["x"]
    tot = x.groupby(["annee", "mois"])["montant"].sum() / 1000
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7))
    a = axs[0]; sel = m.loc[[10, 11, 12]]
    a.plot(sel.index, sel.values, color=BLEU, marker="o"); a.set_xticks([10, 11, 12]); a.set_xticklabels(["oct.", "nov.", "déc."]); a.set_title(f"« Les ventes ont progressé de {fr((m.loc[12] / m.loc[10] - 1) * 100)} % en trois mois »", loc="left", fontsize=9.5, color=ROUGE)
    a.set_ylabel("k€")
    b = axs[1]
    for an, c in zip([2023, 2024, 2025], [GRIS, MUET, BLEU]):
        s = tot.loc[an]; b.plot(s.index, s.values, color=c, label=str(an), lw=2.2 if an == 2025 else 1.5)
    b.axvspan(9.5, 12.5, color=ORANGE, alpha=0.1); b.legend(fontsize=8, ncol=3, loc="upper left"); b.set_xticks(range(1, 13)); b.set_xticklabels([k[:1].upper() for k in MOIS])
    b.set_title("Trois années entières : une saison, chaque fin d'année", loc="left", fontsize=9.5, color=AQUA)
    fig.tight_layout()
    save(fig, "ch01-cerises.png")
    return m


def fig_effectifs():
    """taux de retour par produit sur le canal Réseaux : sans effectifs, de petits échantillons dominent le classement"""
    c = charger()
    x = c["x"][c["x"]["canal"] == "Réseaux"]
    lig = x[["id_ligne", "id_produit"]].merge(c["ret"][["id_ligne"]].assign(r=1), on="id_ligne", how="left").fillna({"r": 0})
    g = lig.groupby("id_produit").agg(n=("id_ligne", "size"), r=("r", "sum"))
    g["taux"] = g["r"] / g["n"] * 100
    petit = g[g["n"] >= 5].sort_values("taux", ascending=False).head(6)
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    a = axs[0]; a.barh([f"produit {i}" for i in petit.index][::-1], petit["taux"].values[::-1], color=ROUGE); a.grid(False)
    for i, v in enumerate(petit["taux"].values[::-1]):
        a.text(v + 0.3, i, fr(v, 0) + " %", va="center", fontsize=8.5)
    a.set_title("« Les produits les plus retournés » : sans les effectifs", loc="left", fontsize=9.5, color=ROUGE); a.set_xlim(0, petit["taux"].max() * 1.2)
    b = axs[1]
    b.scatter(g["n"], g["taux"], s=14, color=BLEU, alpha=0.7)
    moy = g["r"].sum() / g["n"].sum() * 100
    n = np.linspace(max(g["n"].min(), 3), g["n"].max(), 200)
    se = np.sqrt(moy / 100 * (1 - moy / 100) / n) * 100
    b.plot(n, moy + 1.96 * se, color=MUET, lw=1, ls="--"); b.plot(n, np.maximum(moy - 1.96 * se, 0), color=MUET, lw=1, ls="--"); b.axhline(moy, color=ENCRE2, lw=0.8)
    b.set_xlabel("lignes vendues par les Réseaux"); b.set_ylabel("taux de retour (%)"); b.set_title("Avec les effectifs : les petits échantillons étalent les taux", loc="left", fontsize=9.5, color=AQUA)
    fig.tight_layout()
    save(fig, "ch01-effectifs.png")
    return petit, moy, g


def fig_simpson():
    c = charger()
    j = c["j"].copy(); j["mois"] = j["date"].dt.month
    glob = j.groupby("promo_active")["chiffre_affaires"].mean()
    mm = j[j["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack()
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1, 1.5]})
    a = axs[0]; a.bar(["Jours sans\npromotion", "Jours de\npromotion"], glob.values, color=[GRIS, BLEU]); a.grid(False); a.set_yticks([])
    for i, v in enumerate(glob.values):
        a.text(i, v + 40, fr(v) + " €", ha="center", fontsize=9)
    a.set_ylim(0, 4000); a.set_title("En moyenne : la promotion « rapporte moins »", loc="left", fontsize=9.5, color=ROUGE)
    b = axs[1]; w = 0.35; ix = np.arange(len(mm))
    b.bar(ix - w / 2, mm[0], w, color=GRIS, label="sans promotion"); b.bar(ix + w / 2, mm[1], w, color=BLEU, label="promotion")
    b.set_xticks(ix); b.set_xticklabels([MOIS[m - 1] for m in mm.index]); b.legend(fontsize=8); b.set_ylabel("CA moyen par jour (€)")
    b.set_title("Mois par mois : la promotion rapporte plus, chaque fois", loc="left", fontsize=9.5, color=AQUA)
    fig.tight_layout()
    save(fig, "ch01-simpson.png")
    return glob, mm


def fig_log():
    c = charger()
    p = c["x"][c["x"]["annee"] == 2025].groupby("id_produit")["montant"].sum().sort_values(ascending=False).values / 1000
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7))
    a = axs[0]; a.bar(range(len(p)), p, color=BLEU, width=1.0); a.set_title("Échelle linéaire : quelques produits dominent", loc="left", fontsize=9.5)
    a.set_ylabel("CA 2025 du produit (k€)"); a.set_xlabel("produits, du plus au moins vendu")
    b = axs[1]; b.bar(range(len(p)), p, color=BLEU, width=1.0); b.set_yscale("log"); b.set_title("Échelle logarithmique, non signalée : tout semble proche", loc="left", fontsize=9.5, color=ROUGE)
    b.set_ylabel("CA 2025 du produit (k€, échelle log)"); b.set_xlabel("produits, du plus au moins vendu")
    fig.tight_layout()
    save(fig, "ch01-log.png")
    return p


def fig_aire_rayon():
    v = np.array([1, 2, 3])
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
    for a, mode in zip(axs, ("rayon", "aire")):
        a.set_xlim(0, 9.4); a.set_ylim(-0.3, 3.0); a.set_aspect("equal"); a.axis("off")
        for i, val in enumerate(v):
            r = val * 0.42 if mode == "rayon" else 0.42 * np.sqrt(val) * 1.45
            a.add_patch(Circle((1.4 + i * 3.1, 1.6), r, fc=BLEU if mode == "aire" else ROUGE, ec="white")); a.text(1.4 + i * 3.1, -0.2, f"valeur {val}", ha="center", fontsize=9, color=ENCRE2)
        a.set_title("Rayon proportionnel à la valeur : 3 paraît 9 fois plus grand que 1" if mode == "rayon" else "Aire proportionnelle à la valeur : 3 paraît 3 fois plus grand", loc="left", fontsize=9.5, color=ROUGE if mode == "rayon" else AQUA)
    fig.tight_layout()
    save(fig, "ch01-aire-rayon.png")


def fig_corr_suggeree():
    c = charger()
    j = c["j"].copy()
    m = j.assign(mois=j["date"].dt.to_period("M")).groupby("mois").agg(pub=("depense_pub", "sum"), cmd=("nb_commandes", "sum"), temp=("temperature_moy", "mean")).reset_index()
    m["annee"] = m["mois"].dt.year; m["mois_n"] = m["mois"].dt.month
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    a = axs[0]; a.scatter(m["pub"] / 1000, m["cmd"], color=BLEU, s=26)
    r = np.corrcoef(m["pub"], m["cmd"])[0, 1]
    a.set_title(f"Publicité et commandes (36 mois) : corrélation {fr(r, 2)}", loc="left", fontsize=9.5, color=ROUGE); a.set_xlabel("publicité du mois (k€)"); a.set_ylabel("commandes du mois")
    b = axs[1]
    for k in range(1, 13):
        s = m[m["mois_n"] == k]
        b.scatter(s["pub"] / 1000, s["cmd"], s=20, color=ORANGE if k in (11, 12) else (BLEU if k in (3, 4, 5) else GRIS))
    b.set_title("Même nuage, coloré par saison : la saison pilote les deux", loc="left", fontsize=9.5, color=AQUA); b.set_xlabel("publicité du mois (k€)")
    b.text(0.05, 0.93, "orange : nov.-déc.   bleu : mars-mai   gris : autres mois", transform=b.transAxes, fontsize=8, color=MUET)
    fig.tight_layout()
    save(fig, "ch01-correlation.png")
    return r


def fig_annotation():
    """CA quotidien de mars-mai 2025 (série avec incidents) : sans, puis avec annotations de ce que l'on sait des creux"""
    j = pd.read_csv(f"{D}/jours_incidents.csv", parse_dates=["date"])
    w = j[(j["date"] >= "2025-03-01") & (j["date"] <= "2025-05-15")].set_index("date")["chiffre_affaires"] / 1000
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.7), sharey=True)
    for a in axs:
        a.plot(w.index, w.values, color=BLEU, lw=1.6)
        a.set_ylim(0, w.max() * 1.15); a.set_xticks(pd.to_datetime(["2025-03-01", "2025-04-01", "2025-05-01"])); a.set_xticklabels(["1er mars", "1er avril", "1er mai"])
    axs[0].set_ylabel("CA quotidien (k€)"); axs[0].set_title("Sans annotation : des creux inexpliqués", loc="left", fontsize=9.5, color=ROUGE)
    a = axs[1]
    a.set_title("Avec annotation : chaque creux a son explication", loc="left", fontsize=9.5, color=AQUA)
    for d0, d1, txt, dy in (("2025-03-12", "2025-03-14", "Panne du site\n(3 jours)", 0.85), ("2025-04-28", "2025-04-29", "Fermeture\nexceptionnelle", 0.85)):
        a.axvspan(pd.Timestamp(d0) - pd.Timedelta(hours=12), pd.Timestamp(d1) + pd.Timedelta(hours=12), color=ORANGE, alpha=0.18)
        a.text(pd.Timestamp(d0) + (pd.Timestamp(d1) - pd.Timestamp(d0)) / 2, w.max() * 1.12 * dy + 0.05, txt, ha="center", va="top", fontsize=8.5, color=ENCRE2)
    fig.tight_layout()
    save(fig, "ch01-annotation.png")
    sel = w.loc["2025-03-12":"2025-03-14"].mean(), w.loc["2025-04-28":"2025-04-29"].mean(), w.drop(pd.to_datetime(["2025-03-12", "2025-03-13", "2025-03-14", "2025-04-28", "2025-04-29"])).median()
    return sel


@functools.lru_cache(maxsize=1)
def faits():
    """tous les nombres cités dans la prose du chapitre (calculés ici, vérifiés par des assert dans le texte)"""
    c = charger()
    x = c["x"]
    F = {}
    t = x.groupby("annee")["montant"].sum() / 1000
    F["t"] = t
    F["cat"] = ca_categories() / 1000
    F["part_cat"] = F["cat"] / F["cat"].sum() * 100
    m = ca_mensuel(2025) / 1000
    F["m"] = m
    F["canal_dec"] = (ca_mensuel(2025, "canal") / 1000).loc[12]
    F["canal_an"] = (ca_mensuel(2025, "canal") / 1000).sum()
    F["conv"] = conversion_sources()
    v = ca_villes().sort_values(ascending=False)
    F["villes"] = v / v.sum() * 100
    F["autres_villes"] = v.iloc[8:].sum() / v.sum() * 100
    cmd = x[x["annee"] == 2025].drop_duplicates("id_commande")
    cmd = cmd.assign(jour=cmd["date_commande"].dt.dayofweek)
    F["sem"] = cmd.groupby(["jour", "mois"]).size().unstack(fill_value=0)
    cr = c["cr"]
    F["cr"] = cr[cr["mois"].str[:4] == "2025"].sum(numeric_only=True) / 1000
    j = c["j"].copy(); j["mois"] = j["date"].dt.to_period("M")
    mo = j.groupby("mois").agg(pub=("depense_pub", "sum"), cmd=("nb_commandes", "sum")).reset_index()
    mo["mn"] = mo["mois"].dt.month
    F["r_tout"] = np.corrcoef(mo["pub"], mo["cmd"])[0, 1]
    hors = mo[~mo["mn"].isin([11, 12])]
    F["r_hors"] = np.corrcoef(hors["pub"], hors["cmd"])[0, 1]
    F["pub_nd"], F["pub_hors"] = mo[mo["mn"].isin([11, 12])]["pub"].mean(), hors["pub"].mean()
    F["cmd_nd"], F["cmd_hors"] = mo[mo["mn"].isin([11, 12])]["cmd"].mean(), hors["cmd"].mean()
    F["oct_dec"] = {an: (ca_mensuel(an) / 1000).loc[[10, 12]].values for an in (2023, 2024, 2025)}
    jj = c["j"].copy(); jj["mois"] = jj["date"].dt.month
    F["promo_glob"] = jj.groupby("promo_active")["chiffre_affaires"].mean()
    F["promo_mois"] = jj[jj["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack()
    F["produits"] = np.sort(x[x["annee"] == 2025].groupby("id_produit")["montant"].sum().values)[::-1] / 1000
    ret = c["ret"]
    xs = x[x["canal"] == "Réseaux"]
    lig = xs[["id_ligne", "id_produit"]].merge(ret[["id_ligne"]].assign(r=1), on="id_ligne", how="left").fillna({"r": 0})
    g = lig.groupby("id_produit").agg(n=("id_ligne", "size"), r=("r", "sum"))
    g["taux"] = g["r"] / g["n"] * 100
    F["ret_g"] = g
    F["ret_moy"] = g["r"].sum() / g["n"].sum() * 100
    ji = pd.read_csv(f"{D}/jours_incidents.csv", parse_dates=["date"]).set_index("date")["chiffre_affaires"] / 1000
    w = ji.loc["2025-03-01":"2025-05-15"]
    F["panne"] = w.loc["2025-03-12":"2025-03-14"].mean()
    F["fermeture"] = w.loc["2025-04-28":"2025-04-29"].mean()
    F["normal"] = w.drop(pd.to_datetime(["2025-03-12", "2025-03-13", "2025-03-14", "2025-04-28", "2025-04-29"])).median()
    return F
