"""Outils du chapitre 2 (tableaux de bord) — série 2, volume IV.

Chargement des données de la boutique, modèle en étoile, indicateurs hebdomadaires, équivalents « DAX » en pandas, sécurité par région, et toutes les figures du chapitre.
Les maquettes sont des DESSINS génériques faits avec matplotlib : aucune interface d'un produit commercial n'est reproduite.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

import style as S

TVA = 0.20
GRIS, GRIS2 = "#e8e7e1", "#c9c8bf"


# ------------------------------------------------------------------------------------------------------------------ données
def charger(dossier):
    """toutes les tables utiles + la table de faits `fv` (une ligne par ligne de commande)"""
    lire = lambda n, **k: pd.read_csv(os.path.join(dossier, n + ".csv"), **k)
    d = {"cmd": lire("commandes", parse_dates=["date_commande"]), "lig": lire("lignes_commande"), "prod": lire("produits"), "cli": lire("clients", parse_dates=["date_inscription"]),
         "ret": lire("retours"), "ses": lire("sessions_web", parse_dates=["date"]), "stk": lire("stock_quotidien", parse_dates=["date"]), "vil": lire("villes"),
         "bud": lire("budget_reel_2025"), "jours": lire("jours_exploitation", parse_dates=["date"]),
         "liv": lire("livraisons", parse_dates=["date_commande", "date_expedition", "date_livraison"]), "camp": lire("campagnes"), "bench": lire("benchmark_secteur")}
    fv = d["lig"].merge(d["cmd"][["id_commande", "date_commande", "canal", "id_client", "code_promo"]], on="id_commande").merge(d["prod"][["id_produit", "categorie", "cout_achat"]], on="id_produit")
    fv["marge_ht"] = fv["montant"] / (1 + TVA) - fv["quantite"] * fv["cout_achat"]
    fv["annee"], fv["mois"] = fv["date_commande"].dt.year, fv["date_commande"].dt.month
    d["fv"] = fv
    return d


def etoile(d):
    """le modèle en étoile de la boutique : une table de faits et quatre dimensions"""
    fv = d["fv"]
    dates = pd.DataFrame({"date": pd.date_range("2023-01-01", "2025-12-31")})
    dates["annee"], dates["trimestre"], dates["mois"] = dates["date"].dt.year, dates["date"].dt.quarter, dates["date"].dt.month
    dates["semaine_debut"] = dates["date"].dt.to_period("W-SUN").dt.start_time
    dates["jour_semaine"] = dates["date"].dt.dayofweek + 1
    dates = dates.merge(d["jours"][["date", "promo_active"]], on="date", how="left")
    dim_produit = d["prod"][["id_produit", "nom_produit", "categorie", "fournisseur", "prix_vente", "cout_achat"]].copy()
    dim_client = d["cli"][["id_client", "ville", "canal_acquisition", "fidelite", "annee_naissance"]].merge(d["vil"][["ville", "region"]], on="ville", how="left")
    dim_canal = pd.DataFrame({"canal": ["Boutique", "Site", "Réseaux"], "type": ["physique", "en ligne", "en ligne"]})
    fait = fv[["id_ligne", "id_commande", "date_commande", "canal", "id_client", "id_produit", "quantite", "prix_unitaire", "remise_pct", "montant", "marge_ht"]].rename(columns={"date_commande": "date"})
    return {"fait_ventes": fait, "dim_date": dates, "dim_produit": dim_produit, "dim_client": dim_client, "dim_canal": dim_canal}


def controle_etoile(star):
    """effectifs des tables, unicité des clés des dimensions, lignes de faits sans correspondance (orphelines)"""
    f = star["fait_ventes"]
    cles = {"dim_date": ("date", "date"), "dim_produit": ("id_produit", "id_produit"), "dim_client": ("id_client", "id_client"), "dim_canal": ("canal", "canal")}
    lignes = []
    for dim, (cf, cd) in cles.items():
        t = star[dim]
        lignes.append((dim, len(t), bool(t[cd].is_unique), int((~f[cf].isin(t[cd])).sum())))
    return pd.DataFrame(lignes, columns=["dimension", "lignes", "cle_unique", "faits_orphelins"])


# ------------------------------------------------------------------------------------------------------------------ indicateurs
def serie_hebdo(d):
    """indicateurs par semaine (lundi-dimanche) ; livraisons : semaine de LIVRAISON (on ne connaît que ce qui est livré) ; sessions et ruptures : 2025 seulement"""
    fv = d["fv"].copy()
    fv["sem"] = fv["date_commande"].dt.to_period("W-SUN").dt.start_time
    w = fv.groupby("sem").agg(ca=("montant", "sum"), marge=("marge_ht", "sum"), commandes=("id_commande", "nunique"))
    w["panier"] = w["ca"] / w["commandes"]
    w["taux_marge"] = w["marge"] / (w["ca"] / (1 + TVA))
    liv = d["liv"][d["liv"]["date_livraison"] <= "2025-12-31"].copy()
    liv["sem"] = liv["date_livraison"].dt.to_period("W-SUN").dt.start_time
    w["a_l_heure"] = 1 - liv.groupby("sem")["retard"].mean()
    ses = d["ses"].copy()
    ses["sem"] = ses["date"].dt.to_period("W-SUN").dt.start_time
    w["conversion"] = ses.groupby("sem")["commande"].mean()
    stk = d["stk"].copy()
    stk["sem"] = stk["date"].dt.to_period("W-SUN").dt.start_time
    w["rupture"] = stk.groupby("sem")["rupture"].mean()
    return w[w.index <= "2025-12-22"]


def limites(serie, semaine, n=26, k=3):
    """moyenne et limites ± k écarts-types calculées sur les n semaines qui PRÉCÈDENT `semaine`"""
    h = serie[serie.index < semaine].dropna().tail(n)
    return h.mean(), h.mean() - k * h.std(), h.mean() + k * h.std()


def kpi_semaine(d, debut):
    """les indicateurs de la page de la gérante pour la semaine commençant à `debut`, et la même semaine un an plus tôt (364 jours avant)"""
    debut = pd.Timestamp(debut)
    w = serie_hebdo(d)
    out = {}
    for nom, dt in (("cette_semaine", debut), ("an_dernier", debut - pd.Timedelta(days=364))):
        out[nom] = w.loc[dt] if dt in w.index else None
    return out, w


# ------------------------------------------------------------------------------------------------------------------ équivalents « DAX » (pandas)
def ca_par_mois(d):
    fv = d["fv"]
    t = fv.pivot_table(index="mois", columns="annee", values="montant", aggfunc="sum")
    return t


def cumul_annuel(d, annee):
    """chiffre d'affaires cumulé depuis le début de l'année (équivalent du « cumul annuel » d'une mesure de temps)"""
    t = ca_par_mois(d)[annee]
    return t.cumsum()


def region_par_canal(d):
    """chiffre d'affaires 2025 par région fictive (jointure faits -> clients -> villes)"""
    star = etoile(d)
    f = star["fait_ventes"].merge(star["dim_client"][["id_client", "region"]], on="id_client")
    return f[f["date"] >= "2025-01-01"].groupby("region")["montant"].sum()


# ------------------------------------------------------------------------------------------------------------------ dessins génériques
def _boite(ax, x, y, w, h, texte, fc="#eef4fc", ec=S.BLEU, fs=8.5, bold=False, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=fs, color=tc or S.ENCRE, weight="bold" if bold else "normal", linespacing=1.25)


def _fleche(ax, x1, y1, x2, y2, c=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.3, color=c or S.MUET))


def fig_flux():
    S.setup()
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.06); ax.axis("off")
    etapes = [("1  Sources", "fichiers, bases,\nservices en ligne", "pd.read_csv, SQL"), ("2  Transformation", "nettoyer, typer,\nfusionner", "pandas, SQL"),
              ("3  Modèle", "faits, dimensions,\nrelations", "tables liées\npar des clés"), ("4  Mesures", "formules qui\nse recalculent", "fonctions\nd'agrégation"),
              ("5  Visuels", "graphiques, cartes,\ntableaux", "matplotlib,\nplotly"), ("6  Rapport", "une page, des\nfiltres", "figure + texte"),
              ("7  Publication", "partage et\naccès", "fichier, serveur,\ne-mail"), ("8  Actualisation", "recalcul\nplanifié", "script planifié")]
    for i, (t, bi, py) in enumerate(etapes):
        col, lig = i % 4, i // 4
        x, y = 0.02 + col * 0.245, 0.55 - lig * 0.52
        _boite(ax, x, y + 0.2, 0.21, 0.2, t, fc="#eef4fc", bold=True, fs=9.5)
        _boite(ax, x, y + 0.09, 0.21, 0.1, bi, fc="white", ec=S.GRIS2 if hasattr(S, "GRIS2") else GRIS2, fs=7.5)
        _boite(ax, x, y - 0.02, 0.21, 0.1, py, fc="#fdf1ec", ec=S.ORANGE, fs=7.5)
        if col < 3:
            _fleche(ax, x + 0.215, y + 0.3, x + 0.245, y + 0.3)
    ax.text(0.01, 1.045, "Le flux d'un outil de tableaux de bord (haut : étapes ; milieu : ce que fait l'outil ; bas : l'équivalent à la main)", fontsize=8.5, va="top", color=S.ENCRE2)
    S.save(fig, "ch02-flux-bi.png")


def fig_etoile(star):
    S.setup()
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    f = star["fait_ventes"]
    _boite(ax, 0.33, 0.38, 0.34, 0.26, f"fait_ventes\n{len(f):,} lignes".replace(",", " ") + "\n\nid_ligne, id_commande\nquantité, prix, montant, marge", fc="#eef4fc", ec=S.BLEU, bold=False, fs=9)
    dims = {"dim_date": (0.02, 0.72, "date", star["dim_date"]), "dim_produit": (0.68, 0.72, "id_produit", star["dim_produit"]), "dim_client": (0.02, 0.06, "id_client", star["dim_client"]), "dim_canal": (0.68, 0.06, "canal", star["dim_canal"])}
    for nom, (x, y, cle, t) in dims.items():
        cols = ", ".join(t.columns[1:3])
        _boite(ax, x, y, 0.30, 0.22, f"{nom}\n{len(t):,} lignes".replace(",", " ") + f"\nclé : {cle}\n{cols}…", fc="#e9f7f1", ec=S.AQUA, fs=8.2)
    for (x1, y1, x2, y2, lab, haut) in [(0.17, 0.72, 0.40, 0.64, "date", True), (0.83, 0.72, 0.60, 0.64, "id_produit", True), (0.17, 0.28, 0.40, 0.38, "id_client", False), (0.83, 0.28, 0.60, 0.38, "canal", False)]:
        ax.plot([x1, x2], [y1, y2], color=S.MUET, lw=1.3)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + (0.02 if haut else -0.02), lab, fontsize=7.5, color=S.ENCRE2, ha="center", va="bottom" if haut else "top")
        ax.text(x1, y1 + (-0.03 if haut else 0.03), "1", fontsize=9, weight="bold", color=S.AQUA, ha="center", va="center")
        ax.text(x2, y2 + (0.03 if haut else -0.03), "n", fontsize=9, weight="bold", color=S.BLEU, ha="center", va="center")
    S.save(fig, "ch02-schema-etoile.png")


def fig_visuels(d):
    S.setup()
    fig, axs = plt.subplots(2, 3, figsize=(9.4, 5.6))
    fv = d["fv"]; f25 = fv[fv["annee"] == 2025]
    w = serie_hebdo(d)
    ax = axs[0, 0]; ax.axis("off")
    ax.text(0.5, 0.62, f"{f25['montant'].sum() / 1000:,.0f} k€".replace(",", " "), ha="center", fontsize=26, color=S.BLEU, weight="bold")
    ax.text(0.5, 0.28, "chiffre d'affaires 2025", ha="center", fontsize=9)
    ax.set_title("Carte : un chiffre à lire d'un coup", loc="left", fontsize=9)
    ax = axs[0, 1]; cat = f25.groupby("categorie")["montant"].sum().sort_values()
    ax.barh(cat.index, cat.values / 1000, color=S.BLEU); ax.set_title("Barres : comparer des catégories", loc="left", fontsize=9); ax.set_xlabel("k€", fontsize=8); ax.grid(axis="y", visible=False); ax.tick_params(labelsize=8)
    ax = axs[0, 2]; ax.plot(w.index[-52:], w["ca"].iloc[-52:] / 1000, color=S.BLEU, lw=1.6); ax.set_title("Courbe : suivre une évolution", loc="left", fontsize=9); ax.tick_params(labelsize=7); ax.set_ylabel("k€ / semaine", fontsize=8)
    ax.tick_params(axis="x", rotation=30)
    ax = axs[1, 0]; ax.axis("off")
    t = f25.groupby(["categorie", "canal"])["montant"].sum().unstack() / 1000
    cell = [[f"{v:,.0f}".replace(",", " ") for v in r] for r in t.values]
    tb = ax.table(cellText=cell, rowLabels=t.index, colLabels=t.columns, loc="center", cellLoc="right"); tb.auto_set_font_size(False); tb.set_fontsize(7.5); tb.scale(1, 1.25)
    for c in tb.get_celld().values():
        c.set_edgecolor(GRIS2)
    ax.set_title("Tableau : retrouver une valeur exacte (k€)", loc="left", fontsize=9)
    ax = axs[1, 1]; g = f25.groupby("id_commande").agg(n=("quantite", "sum"), m=("montant", "sum")); g = g.sample(1500, random_state=1)
    ax.scatter(g["n"] + np.random.default_rng(0).uniform(-0.2, 0.2, len(g)), g["m"], s=6, color=S.VIOLET, alpha=0.35); ax.set_title("Nuage : voir une relation", loc="left", fontsize=9); ax.set_xlabel("articles", fontsize=8); ax.set_ylabel("€", fontsize=8); ax.tick_params(labelsize=8)
    ax = axs[1, 2]; p = f25.groupby(["canal", "categorie"])["montant"].sum().unstack(); p = p.div(p.sum(axis=1), axis=0) * 100
    bottom = np.zeros(len(p)); cols = [S.BLEU, S.ORANGE, S.AQUA, S.VIOLET, S.ROUGE, S.MUET]
    for c, col in zip(p.columns, cols):
        ax.bar(p.index, p[c], bottom=bottom, color=col, label=c); bottom += p[c].values
    ax.set_title("Barres 100 % : comparer des parts", loc="left", fontsize=9); ax.legend(fontsize=6, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.12)); ax.tick_params(labelsize=8); ax.grid(axis="x", visible=False)
    fig.tight_layout()
    S.save(fig, "ch02-visuels.png")


def fig_marques(d):
    S.setup()
    f25 = d["fv"][d["fv"]["annee"] == 2025]
    t = (f25.groupby(["categorie", "canal"])["montant"].sum().unstack() / 1000)[["Boutique", "Site", "Réseaux"]]
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.8))
    ax = axs[0]; x = np.arange(len(t)); w = 0.27
    for i, (c, col) in enumerate(zip(t.columns, [S.BLEU, S.ORANGE, S.AQUA])):
        ax.bar(x + (i - 1) * w, t[c], w, color=col, label=c)
    ax.set_xticks(x); ax.set_xticklabels(t.index, rotation=35, ha="right", fontsize=8); ax.legend(fontsize=7); ax.set_title("Position (longueur de barre)", loc="left", fontsize=9); ax.set_ylabel("k€", fontsize=8); ax.grid(axis="x", visible=False)
    ax = axs[1]; im = ax.imshow(t.values, cmap=S.SEQ, aspect="auto")
    ax.set_xticks(range(3)); ax.set_xticklabels(t.columns, fontsize=8); ax.set_yticks(range(len(t))); ax.set_yticklabels(t.index, fontsize=8); ax.grid(False)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            ax.text(j, i, f"{t.values[i, j]:.0f}", ha="center", va="center", fontsize=7.5, color="white" if t.values[i, j] > t.values.max() * 0.55 else S.ENCRE)
    ax.set_title("Couleur (intensité)", loc="left", fontsize=9)
    ax = axs[2]
    for j, c in enumerate(t.columns):
        ax.scatter([j] * len(t), range(len(t)), s=t[c] * 9, color=[S.BLEU, S.ORANGE, S.AQUA][j], alpha=0.7)
    ax.set_xticks(range(3)); ax.set_xticklabels(t.columns, fontsize=8); ax.set_yticks(range(len(t))); ax.set_yticklabels(t.index, fontsize=8); ax.set_xlim(-0.6, 2.6); ax.set_ylim(-0.7, len(t) - 0.3); ax.invert_yaxis()
    ax.set_title("Taille (aire du cercle)", loc="left", fontsize=9)
    fig.tight_layout()
    S.save(fig, "ch02-marques.png")


def _carte_kpi(ax, x, y, w, h, titre, valeur, delta, ok=None, note=None):
    col = S.ENCRE2 if ok is None else (S.AQUA if ok else S.ROUGE)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.003,rounding_size=0.01", fc="white", ec=GRIS2, lw=1))
    ax.text(x + 0.012, y + h - 0.02, titre, fontsize=7.2, va="top", color=S.ENCRE2)
    ax.text(x + 0.012, y + h * 0.52, valeur, fontsize=13.5, va="center", color=S.ENCRE, weight="bold")
    ax.text(x + 0.012, y + 0.012, delta, fontsize=6.6, va="bottom", color=col, linespacing=1.25)


def fig_noye_vs_ordonne():
    S.setup()
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
    rng = np.random.default_rng(3)
    ax = axs[0]; ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.set_title("Un tableau de bord qui noie (14 éléments, 9 couleurs)", loc="left", fontsize=9)
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=GRIS2))
    cols = ["#e34948", "#eb6834", "#e0a100", "#1baf7a", "#2a78d6", "#4a3aa7", "#d63384", "#17a2b8", "#6f42c1"]
    noms = ["camembert 3D", "jauge", "courbe", "barres", "tableau 40 lignes", "carte", "jauge", "camembert", "courbe", "barres", "nuage", "tableau", "jauge", "barres"]
    k = 0
    for r in range(4):
        for c in range(4):
            if k >= 14:
                break
            ax.add_patch(Rectangle((0.02 + c * 0.24, 0.76 - r * 0.24), 0.22, 0.2, fc=cols[k % 9], alpha=0.35, ec=cols[k % 9]))
            ax.text(0.13 + c * 0.24, 0.86 - r * 0.24, noms[k], ha="center", va="center", fontsize=6.5)
            k += 1
    ax = axs[1]; ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.set_title("Le même contenu rangé (6 chiffres, 3 graphiques, 1 couleur d'alerte)", loc="left", fontsize=9)
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=GRIS2))
    for i in range(6):
        ax.add_patch(Rectangle((0.02 + i * 0.16, 0.72), 0.14, 0.24, fc="#eef4fc", ec=S.BLEU)); ax.text(0.09 + i * 0.16, 0.84, "chiffre", ha="center", fontsize=7)
    ax.add_patch(Rectangle((0.02, 0.1), 0.58, 0.55, fc="#f5f5f2", ec=GRIS2)); ax.text(0.31, 0.38, "tendance 52 semaines", ha="center", fontsize=8)
    ax.add_patch(Rectangle((0.63, 0.38), 0.35, 0.27, fc="#f5f5f2", ec=GRIS2)); ax.text(0.805, 0.51, "par canal", ha="center", fontsize=8)
    ax.add_patch(Rectangle((0.63, 0.1), 0.35, 0.25, fc="#fdecec", ec=S.ROUGE)); ax.text(0.805, 0.225, "alertes", ha="center", fontsize=8, color=S.ROUGE)
    fig.tight_layout()
    S.save(fig, "ch02-noye-ordonne.png")


def fig_disposition():
    S.setup()
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.06); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=GRIS2))
    zones = [(0.02, 0.76, 0.96, 0.2, "1  Les chiffres clés (le plus important, en haut à gauche)", "#eef4fc", S.BLEU), (0.02, 0.28, 0.6, 0.44, "2  La tendance (où va-t-on ?)", "#f5f5f2", GRIS2),
             (0.64, 0.28, 0.34, 0.44, "3  La répartition (où ?)", "#f5f5f2", GRIS2), (0.02, 0.03, 0.96, 0.21, "4  Les alertes et le détail (que faire ?)", "#fdecec", S.ROUGE)]
    for x, y, w, h, t, fc, ec in zones:
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.2)); ax.text(x + 0.012, y + h - 0.025, t, fontsize=9, va="top", color=S.ENCRE)
    for (x1, y1, x2, y2) in [(0.1, 0.8, 0.92, 0.8), (0.92, 0.79, 0.12, 0.47), (0.12, 0.45, 0.9, 0.12)]:
        _fleche(ax, x1, y1, x2, y2, c=S.ORANGE)
    ax.text(0.5, 1.02, "sens de lecture « en Z »", ha="center", va="center", fontsize=9, color=S.ORANGE)
    S.save(fig, "ch02-disposition.png")


def fig_niveaux():
    S.setup()
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.5))
    for i, (ax, t, sous) in enumerate(zip(axs, ["Vue d'ensemble", "Analyse", "Détail"], ["6 chiffres, 3 graphiques : « où en sommes-nous ? »", "filtres et comparaisons : « d'où vient l'écart ? »", "la liste des lignes : « quelles commandes ? »"])):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=GRIS2))
        ax.set_title(f"{i + 1}  {t}", loc="left", fontsize=10)
        if i == 0:
            for j in range(6):
                ax.add_patch(Rectangle((0.04 + j * 0.155, 0.74), 0.14, 0.2, fc="#eef4fc", ec=S.BLEU))
            ax.add_patch(Rectangle((0.04, 0.1), 0.6, 0.55, fc="#f5f5f2", ec=GRIS2)); ax.add_patch(Rectangle((0.67, 0.1), 0.29, 0.55, fc="#f5f5f2", ec=GRIS2))
        elif i == 1:
            ax.add_patch(Rectangle((0.04, 0.82), 0.92, 0.12, fc="#fff7e0", ec="#e0a100")); ax.text(0.5, 0.88, "filtres : période, canal, catégorie", ha="center", fontsize=7.5)
            ax.add_patch(Rectangle((0.04, 0.1), 0.44, 0.65, fc="#f5f5f2", ec=GRIS2)); ax.add_patch(Rectangle((0.52, 0.1), 0.44, 0.65, fc="#f5f5f2", ec=GRIS2))
        else:
            for j in range(9):
                ax.add_patch(Rectangle((0.04, 0.82 - j * 0.085), 0.92, 0.07, fc="#f5f5f2" if j % 2 else "white", ec=GRIS2))
        ax.text(0.5, -0.06, sous, ha="center", fontsize=7.8, va="top", color=S.ENCRE2)
    for a, b in [(0, 1), (1, 2)]:
        fig.text((a + 1) / 3 - 0.006, 0.52, "▶", fontsize=16, color=S.ORANGE, ha="center")
    fig.tight_layout()
    S.save(fig, "ch02-niveaux.png")


def fig_processus():
    S.setup()
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    etapes = ["Entretien", "Croquis\npapier", "Maquette", "Prototype", "Test\nutilisateur", "Livraison", "Maintenance"]
    for i, t in enumerate(etapes):
        x = 0.01 + i * 0.141
        _boite(ax, x, 0.5, 0.12, 0.28, t, fc="#eef4fc", fs=8)
        if i < len(etapes) - 1:
            _fleche(ax, x + 0.121, 0.64, x + 0.141, 0.64)
    ax.add_patch(FancyArrowPatch((0.66, 0.48), (0.30, 0.48), connectionstyle="arc3,rad=-0.35", arrowstyle="-|>", mutation_scale=12, lw=1.4, color=S.ORANGE))
    ax.text(0.48, 0.17, "on revient en arrière tant que l'utilisateur ne comprend pas en 5 secondes", ha="center", fontsize=8.5, color=S.ORANGE)
    S.save(fig, "ch02-processus.png")


def fig_page_gerante(d, debut="2025-12-22"):
    """LA page de tableau de bord de la gérante (figure du livre) ; retourne le dictionnaire des valeurs affichées"""
    S.setup()
    debut = pd.Timestamp(debut)
    kp, w = kpi_semaine(d, debut)
    cur, prev = kp["cette_semaine"], kp["an_dernier"]
    fig = plt.figure(figsize=(11, 7.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#f6f6f3"))
    ax.text(0.02, 0.965, "La boutique : où en sommes-nous ?", fontsize=15, weight="bold", color=S.ENCRE, va="center")
    fin = debut + pd.Timedelta(days=6)
    ax.text(0.02, 0.93, f"Semaine du {debut.day} au {fin.day} décembre 2025 · données simulées, actualisées le 31/12/2025 · définitions : voir le dictionnaire des indicateurs", fontsize=7.6, color=S.ENCRE2, va="center")
    # cartes
    def delta(a, b, fmt="%", inverse=False):
        if b is None or pd.isna(b):
            return "pas d'historique", None
        v = (a / b - 1) * 100 if fmt == "%" else (a - b) * 100
        ok = (v >= 0) != inverse
        return (f"{v:+.1f} % vs an dernier".replace(".", ",") if fmt == "%" else f"{v:+.1f} pts vs an dernier".replace(".", ",")), ok
    cartes = []
    dd, ok = delta(cur["ca"], prev["ca"]); cartes.append(("Chiffre d'affaires", f"{cur['ca'] / 1000:.1f} k€".replace(".", ","), dd, ok))
    dd, ok = delta(cur["commandes"], prev["commandes"]); cartes.append(("Commandes", f"{cur['commandes']:.0f}", dd, ok))
    dd, ok = delta(cur["panier"], prev["panier"]); cartes.append(("Panier moyen", f"{cur['panier']:.1f} €".replace(".", ","), dd, ok))
    dd, ok = delta(cur["taux_marge"], prev["taux_marge"], "pts"); cartes.append(("Taux de marge brute (HT)", f"{cur['taux_marge'] * 100:.1f} %".replace(".", ","), dd, ok))
    dd, ok = delta(cur["a_l_heure"], prev["a_l_heure"], "pts")
    mh, loh, _ = limites(w["a_l_heure"], debut)
    if cur["a_l_heure"] < loh:                       # sous ses limites habituelles : la carte passe au rouge, quelle que soit la comparaison à l'an dernier
        ok, dd = False, f"habituel : {mh * 100:.0f} %\n{dd}"
    cartes.append(("Livraisons à l'heure", f"{cur['a_l_heure'] * 100:.0f} %", dd, ok))
    m, lo, hi = limites(w["conversion"], debut)
    cartes.append(("Conversion du site", f"{cur['conversion'] * 100:.1f} %".replace(".", ","), "pas d'historique\navant 2025", None))
    for i, (t, v, dl, ok) in enumerate(cartes):
        _carte_kpi(ax, 0.02 + i * 0.1625, 0.77, 0.152, 0.13, t, v, dl, ok)
    # tendance 52 semaines
    a1 = fig.add_axes([0.05, 0.38, 0.52, 0.30]); ws = w[["ca"]].copy(); cur52 = ws.loc[debut - pd.Timedelta(weeks=51):debut, "ca"] / 1000
    ant = ws["ca"].shift(52).loc[cur52.index] / 1000
    a1.plot(cur52.index, ant.values, color=S.MUET, lw=1.4, label="même semaine, an dernier"); a1.plot(cur52.index, cur52.values, color=S.BLEU, lw=2, label="2025")
    a1.set_title("Chiffre d'affaires par semaine (k€)", loc="left", fontsize=9.5); a1.legend(fontsize=7.5, loc="upper left"); a1.tick_params(labelsize=7.5)
    # par canal
    a2 = fig.add_axes([0.65, 0.37, 0.31, 0.31]); fv = d["fv"]
    def canal(a, b):
        return fv[(fv["date_commande"] >= a) & (fv["date_commande"] <= b)].groupby("canal")["montant"].sum().reindex(["Boutique", "Site", "Réseaux"]) / 1000
    c1, c0 = canal(debut, debut + pd.Timedelta(days=6)), canal(debut - pd.Timedelta(days=364), debut - pd.Timedelta(days=358))
    x = np.arange(3); a2.bar(x - 0.2, c0.values, 0.38, color=S.MUET, label="an dernier"); a2.bar(x + 0.2, c1.values, 0.38, color=S.BLEU, label="cette semaine")
    a2.set_xticks(x); a2.set_xticklabels(c1.index, fontsize=8); a2.set_title("Par canal (k€)", loc="left", fontsize=9.5); a2.legend(fontsize=7.5); a2.grid(axis="x", visible=False); a2.tick_params(labelsize=7.5)
    # livraisons à l'heure avec limites
    a3 = fig.add_axes([0.05, 0.06, 0.38, 0.22]); lh = w["a_l_heure"].dropna().iloc[-26:] * 100; m, lo, hi = limites(w["a_l_heure"], debut)
    a3.plot(lh.index, lh.values, color=S.BLEU, marker="o", ms=3); a3.axhline(m * 100, color=S.MUET, lw=1); a3.axhline(lo * 100, color=S.ROUGE, lw=1, ls="--")
    a3.set_title("Livraisons à l'heure (%) et limites sur 26 semaines", loc="left", fontsize=9.5); a3.tick_params(labelsize=7.5)
    # alertes
    ax.add_patch(Rectangle((0.5, 0.06), 0.46, 0.22, fc="#fdecec", ec=S.ROUGE, lw=1.1)); ax.text(0.51, 0.265, "À regarder cette semaine", fontsize=9.5, weight="bold", color=S.ROUGE, va="top")
    alertes = []
    for nom, col, fmt, bas in (("Livraisons à l'heure", "a_l_heure", "{:.0f} %", True), ("Conversion du site", "conversion", "{:.1f} %", True), ("Rupture sur les 20 produits suivis", "rupture", "{:.0f} %", False)):
        m, lo, hi = limites(w[col], debut); v = cur[col]
        if (bas and v < lo) or ((not bas) and v > hi):
            alertes.append(f"• {nom} : {fmt.format(v * 100).replace('.', ',')} (habituel : {fmt.format(m * 100).replace('.', ',')})")
    if not alertes:
        alertes = ["• aucun indicateur hors de ses limites"]
    for i, t in enumerate(alertes):
        ax.text(0.51, 0.225 - i * 0.045, t, fontsize=8.6, color=S.ENCRE, va="top")
    ax.text(0.51, 0.09, "Seuil d'alerte : moyenne des 26 semaines précédentes ± 3 écarts-types.", fontsize=7, color=S.ENCRE2, va="bottom")
    S.save(fig, "ch02-tableau-de-bord.png")
    return {"cartes": cartes, "alertes": alertes}


def fig_comparaison_bi():
    S.setup()
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.axhline(5, color=GRIS2, lw=1); ax.axvline(5, color=GRIS2, lw=1)
    pts = {"Power BI": (7.6, 7.3), "Tableau": (8.2, 6.2), "Qlik": (6.2, 7.8), "Looker": (3.0, 8.0), "Metabase": (6.5, 2.6), "Superset": (3.4, 3.4)}
    for k, (x, y) in pts.items():
        ax.scatter(x, y, s=260, color=S.BLEU, alpha=0.75, zorder=3); ax.text(x, y - 0.75, k, ha="center", fontsize=9)
    ax.set_xlabel("← travail surtout par le code et la modélisation · travail surtout par clics et glisser-déposer →", fontsize=8.5)
    ax.set_ylabel("← usage libre, pour des analystes · usage cadré, pour toute une entreprise →", fontsize=8.5)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.set_title("Positionnement indicatif (d'après la documentation publique : à vérifier ; position = tendance, pas mesure)", fontsize=8.5, loc="left")
    S.save(fig, "ch02-positionnement-bi.png")


def fig_dax(d):
    S.setup()
    t = ca_par_mois(d)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    ax = axs[0]; mois = np.arange(1, 13)
    ax.plot(mois, t[2024] / 1000, color=S.MUET, label="2024 (même période de l'an dernier)"); ax.plot(mois, t[2025] / 1000, color=S.BLEU, lw=2.2, label="2025")
    ax.set_xticks(mois); ax.set_title("Chiffre d'affaires mensuel (k€)", loc="left", fontsize=9.5); ax.legend(fontsize=7.5)
    ax = axs[1]
    ax.plot(mois, t[2024].cumsum() / 1000, color=S.MUET); ax.plot(mois, t[2025].cumsum() / 1000, color=S.BLEU, lw=2.2); ax.set_xticks(mois); ax.set_title("Cumul depuis le début de l'année (k€)", loc="left", fontsize=9.5)
    fig.tight_layout()
    S.save(fig, "ch02-dax-an-dernier.png")


def fig_rls(d):
    S.setup()
    r = region_par_canal(d) / 1000
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    axs[0].bar(r.index, r.values, color=S.BLEU); axs[0].set_title("Vue de la direction : toutes les régions", loc="left", fontsize=9)
    axs[1].bar(r.index, [r.values[0] if i == 0 else 0 for i in range(len(r))], color=S.BLEU); axs[1].set_title("Vue du responsable de la Région 1 (filtre de ligne)", loc="left", fontsize=9)
    for ax in axs:
        ax.set_ylabel("k€ (2025)", fontsize=8); ax.grid(axis="x", visible=False)
    fig.tight_layout()
    S.save(fig, "ch02-securite-lignes.png")


def fig_autres_outils():
    S.setup()
    fig, ax = plt.subplots(figsize=(9.2, 3.4))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    etapes = [("Modèle sémantique", "définitions\ncentralisées"), ("Requêtes SQL", "sur l'entrepôt"), ("Visuels et\ntableaux de bord", "navigateur"), ("Gouvernance", "droits, versions,\naudit")]
    for i, (t, s) in enumerate(etapes):
        x = 0.02 + i * 0.245
        _boite(ax, x, 0.35, 0.21, 0.35, f"{t}", fc="#eef4fc", bold=True, fs=9)
        ax.text(x + 0.105, 0.28, s, ha="center", va="top", fontsize=8, color=S.ENCRE2)
        if i < 3:
            _fleche(ax, x + 0.215, 0.52, x + 0.245, 0.52)
    ax.text(0.5, 0.92, "Les quatre briques que l'on retrouve, dans des proportions différentes, dans tous les outils de tableaux de bord", ha="center", fontsize=9)
    S.save(fig, "ch02-briques-bi.png")


def toutes_les_figures(d):
    star = etoile(d)
    fig_flux(); fig_etoile(star); fig_visuels(d); fig_marques(d); fig_noye_vs_ordonne(); fig_disposition(); fig_niveaux(); fig_processus()
    res = fig_page_gerante(d); fig_comparaison_bi(); fig_dax(d); fig_rls(d); fig_autres_outils()
    return res
