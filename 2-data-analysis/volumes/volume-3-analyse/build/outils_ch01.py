"""Outils du chapitre 1 (analyse exploratoire) : chargement, détection d'incidents, rapport d'exploration automatique, figures.

Le livre et le cahier importent ce module (le code des figures est ici : il n'encombre pas le texte)."""
import os
import functools
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from style import setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2, GRILLE

D = os.environ.get("DONNEES") or "donnees"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]


@functools.lru_cache(maxsize=1)
def charger():
    """les données de la boutique, prêtes à explorer"""
    lig = pd.read_csv(f"{D}/lignes_commande.csv")
    cmd = pd.read_csv(f"{D}/commandes.csv")
    cmd = cmd.merge(lig.groupby("id_commande")["montant"].sum().rename("panier"), on="id_commande")
    cmd["date_commande"] = pd.to_datetime(cmd["date_commande"])
    cmd["code_promo"] = cmd["code_promo"].fillna("")
    prod = pd.read_csv(f"{D}/produits.csv")
    ret = pd.read_csv(f"{D}/retours.csv")
    j = pd.read_csv(f"{D}/jours_exploitation.csv", parse_dates=["date"])
    cli = pd.read_csv(f"{D}/clients.csv")
    liv = pd.read_csv(f"{D}/livraisons.csv")
    liv["delai"] = (pd.to_datetime(liv["date_livraison"]) - pd.to_datetime(liv["date_commande"])).dt.days
    ji = pd.read_csv(f"{D}/jours_incidents.csv", parse_dates=["date"])
    vi = pd.read_csv(f"{D}/verite_incidents.csv", parse_dates=["date"])
    return dict(cmd=cmd, lig=lig, prod=prod, ret=ret, j=j, cli=cli, liv=liv, ji=ji, vi=vi)


# ------------------------------------------------------------------ détection d'incidents
def reference_locale(serie, jour_semaine, k=4):
    """référence d'un jour = médiane des k jours semblables (même jour de la semaine) avant et après, le jour lui-même exclu"""
    ref = pd.Series(index=serie.index, dtype=float)
    for js in range(7):
        idx = serie.index[jour_semaine == js]
        v = serie.loc[idx].values
        for i, ix in enumerate(idx):
            lo, hi = max(0, i - k), min(len(v), i + k + 1)
            ref[ix] = np.median(np.r_[v[lo:i], v[i + 1:hi]])
    return ref


def z_robuste(serie, ref):
    """écart relatif au référentiel (en log), centré et réduit par le MAD (écart médian absolu) : un score z peu sensible aux extrêmes"""
    r = np.log(serie / ref)
    mad = 1.4826 * np.median(np.abs(r - np.median(r)))
    return (r - np.median(r)) / mad, mad


def incidents_jours(ji):
    """jours d'exploitation sans doublon, avec deux scores z robustes (commandes, panier du jour) ; renvoie aussi les dates en double"""
    doublons = set(ji.loc[ji["date"].duplicated(keep=False), "date"])
    j = ji.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    js = j["date"].dt.dayofweek.values
    j["panier_jour"] = j["chiffre_affaires"] / j["nb_commandes"]
    j["z_ca"], _ = z_robuste(j["chiffre_affaires"], reference_locale(j["chiffre_affaires"], js, 4))
    j["z_commandes"], _ = z_robuste(j["nb_commandes"].astype(float), reference_locale(j["nb_commandes"].astype(float), js, 2))
    j["z_panier"], _ = z_robuste(j["panier_jour"], reference_locale(j["panier_jour"], js, 4))
    return j, doublons


def signaler(j, doublons, seuil):
    """dates signalées : peu de commandes (z < -seuil), panier du jour inhabituel (|z| > seuil), ou date en double"""
    f = (j["z_commandes"] < -seuil) | (j["z_panier"].abs() > seuil)
    return set(j.loc[f, "date"]) | set(doublons)


def precision_rappel(signalees, vraies):
    tp = len(signalees & vraies)
    return (tp / len(signalees) if signalees else float("nan")), tp / len(vraies)


# ------------------------------------------------------------------ rapport d'exploration automatique
def rapport_eda(df, cle=None, seuil_manquants=0.05, seuil_corr=0.8, seuil_modalites=0.01, seuil_dominante=0.8):
    """premier tour d'exploration d'un tableau : types, manquants, distributions, corrélations fortes et alertes (liste de textes).
    `cle` : colonne(s) qui devraient identifier une ligne (on signale alors les doublons de clé)."""
    alertes, n = [], len(df)
    types = pd.DataFrame({"type": df.dtypes.astype(str), "manquants_pct": (df.isna().mean() * 100).round(1), "distincts": df.nunique()})
    num = df.select_dtypes("number")
    binaires = [c for c in num.columns if num[c].nunique() <= 2]
    asym = {c: (float(stats.skew(num[c].dropna())) if num[c].nunique() > 2 else float("nan")) for c in num.columns}
    quant = pd.DataFrame({"min": num.min(), "mediane": num.median(), "moyenne": num.mean(), "max": num.max(), "asymetrie": pd.Series(asym)}).round(2)
    qual = df.select_dtypes(exclude="number")
    top = {}
    for c in qual.columns:
        if qual[c].nunique() <= 30:
            vc = qual[c].value_counts(normalize=True)
            top[c] = dict(modalite=vc.index[0] if vc.index[0] != "" else "(vide)", part=round(float(vc.iloc[0]) * 100, 1), rares=int((vc < seuil_modalites).sum()))
    corr = num.corr().abs().where(np.triu(np.ones((num.shape[1],) * 2), 1).astype(bool)).stack()
    fortes = corr[corr > seuil_corr].sort_values(ascending=False).round(2)
    for c, r in types.iterrows():
        if r["manquants_pct"] > seuil_manquants * 100:
            alertes.append(f"{c} : {r['manquants_pct']} % de valeurs manquantes")
        if r["distincts"] == 1:
            alertes.append(f"{c} : une seule valeur (colonne inutile)")
        if r["distincts"] == n and n > 1:
            alertes.append(f"{c} : une valeur différente par ligne (identifiant ?)")
        if r["type"] == "str" and df[c].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").mean() > 0.9:
            alertes.append(f"{c} : des dates stockées en texte (convertir)")
    for c, v in asym.items():
        if c not in binaires and abs(v) > 2:
            alertes.append(f"{c} : très asymétrique ({v:.2f}) : regarder la médiane et l'échelle logarithmique")
    for c, t in top.items():
        if t["rares"] > 0:
            alertes.append(f"{c} : {t['rares']} modalité(s) rare(s) (moins de {seuil_modalites * 100:.0f} %)")
        if t["part"] > seuil_dominante * 100:
            alertes.append(f"{c} : la modalité « {t['modalite']} » représente {t['part']} % des lignes")
    for (a, b2), r in fortes.items():
        alertes.append(f"{a} et {b2} : corrélation forte ({r})")
    if cle is not None:
        d = int(df.duplicated(subset=cle).sum())
        if d:
            alertes.append(f"{d} ligne(s) avec une clé {cle} déjà vue")
    return dict(lignes=n, colonnes=df.shape[1], types=types, quantitatives=quant, qualitatives=pd.DataFrame(top).T, correlations=fortes, alertes=alertes)


# ------------------------------------------------------------------ figures
def _fmt_k(ax, axis="y"):
    f = matplotlib.ticker.FuncFormatter(lambda v, p: f"{v:,.0f}".replace(",", " "))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def fig_panier():
    setup(); c = charger()["cmd"]; x = c["panier"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2), gridspec_kw={"width_ratios": [1.2, 1.2, 0.9]})
    ax[0].hist(x, bins=40, color=BLEU, alpha=0.85)
    ax[0].axvline(x.mean(), color=ORANGE, lw=1.6, label=f"moyenne {x.mean():.0f} €".replace(".", ","))
    ax[0].axvline(x.median(), color=VIOLET, lw=1.6, ls="--", label=f"médiane {x.median():.0f} €".replace(".", ","))
    ax[0].legend(fontsize=8, loc="upper right")
    ax[0].set_title("Panier (échelle ordinaire)"); ax[0].set_xlabel("€"); ax[0].set_ylabel("commandes"); _fmt_k(ax[0])
    ax[1].hist(x, bins=np.logspace(np.log10(x.min()), np.log10(x.max()), 40), color=AQUA, alpha=0.85); ax[1].set_xscale("log")
    ax[1].set_title("Même panier, échelle logarithmique"); ax[1].set_xlabel("€ (échelle log)"); ax[1].grid(True, which="major")
    ax[1].set_xticks([5, 10, 25, 50, 100, 250, 500]); ax[1].set_xticklabels(["5", "10", "25", "50", "100", "250", "500"])
    ax[2].boxplot(x, vert=True, widths=0.5, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#cde2fb", edgecolor=BLEU), medianprops=dict(color=ORANGE), whiskerprops=dict(color=BLEU), capprops=dict(color=BLEU))
    ax[2].set_title("Boîte à moustaches"); ax[2].set_xticks([]); ax[2].set_ylabel("€")
    save(fig, "ch01-panier.png")


def fig_classes():
    setup(); x = charger()["cmd"]["panier"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 2.9), sharey=False)
    for a, (b, t) in zip(ax, [(5, "5 classes : trop grossier"), (17, "17 classes (règle de Sturges)"), (177, "177 classes : trop fin")]):
        a.hist(x, bins=b, color=BLEU, alpha=0.85); a.set_title(t); a.set_xlabel("€"); _fmt_k(a)
    ax[0].set_ylabel("commandes")
    save(fig, "ch01-classes.png")


def fig_barres():
    setup(); c = charger(); cmd, ret = c["cmd"], c["ret"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.1))
    p = cmd["code_promo"].replace("", "aucun").value_counts(normalize=True) * 100
    p = p.sort_values(); ax[0].barh(p.index, p.values, color=BLEU); ax[0].set_title("Code promo des commandes (%)")
    for i, v in enumerate(p.values): ax[0].text(v + 1, i, f"{v:.1f}".replace(".", ",") + " %", va="center", fontsize=8)
    m = ret["motif"].value_counts(normalize=True).sort_values() * 100; ax[1].barh(m.index, m.values, color=ORANGE); ax[1].set_title("Motif des retours (%)")
    for i, v in enumerate(m.values): ax[1].text(v + 1, i, f"{v:.1f}".replace(".", ",") + " %", va="center", fontsize=8)
    l = c["lig"].merge(c["prod"][["id_produit", "categorie"]], on="id_produit")["categorie"].value_counts(normalize=True).sort_values() * 100
    ax[2].barh(l.index, l.values, color=AQUA); ax[2].set_title("Catégorie des lignes vendues (%)")
    for i, v in enumerate(l.values): ax[2].text(v + 0.5, i, f"{v:.1f}".replace(".", ",") + " %", va="center", fontsize=8)
    for a in ax: a.set_xlim(0, a.get_xlim()[1] * 1.3); a.grid(False); a.grid(True, axis="x")
    fig.subplots_adjust(wspace=0.75)
    save(fig, "ch01-barres.png")


def fig_serie_mensuelle():
    setup(); c = charger(); m = c["cmd"].merge(c["lig"].groupby("id_commande")["montant"].sum().rename("m2"), on="id_commande")
    s = m.groupby(m["date_commande"].dt.to_period("M"))["panier"].sum() / 1000
    fig, ax = plt.subplots(figsize=(9, 3.1))
    ax.plot(range(36), s.values, color=BLEU, marker="o", ms=3)
    for a in range(3): ax.axvspan(a * 12 - 0.5, a * 12 + 11.5, color=GRILLE if a % 2 == 0 else "white", alpha=0.35, lw=0)
    ax.set_xticks(range(0, 36, 6)); ax.set_xticklabels([f"{MOIS[i % 12]}\n{2023 + i // 12}" for i in range(0, 36, 6)], fontsize=8)
    ax.set_ylabel("chiffre d'affaires TTC (k€)"); ax.set_title("Chiffre d'affaires mensuel : le creux de février, le pic de décembre, la hausse d'une année à l'autre")
    save(fig, "ch01-serie-mensuelle.png")


def fig_delais():
    setup(); d = charger()["liv"]["delai"]
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    v = d.value_counts().sort_index(); ax.bar(v.index, v.values, color=BLEU)
    ax.axvline(d.median(), color=ORANGE, ls="--"); ax.text(d.median() + 0.15, v.max() * 0.95, f"médiane {d.median():.0f} j", color=ORANGE, fontsize=8)
    p90 = d.quantile(0.9); ax.axvline(p90, color=VIOLET, ls=":"); ax.text(p90 + 0.15, v.max() * 0.8, f"90 % livrées en {p90:.0f} j ou moins", color=VIOLET, fontsize=8)
    ax.set_xlabel("délai de livraison (jours)"); ax.set_ylabel("commandes"); ax.set_title("Délais de livraison : une variable discrète, une queue à droite"); _fmt_k(ax)
    save(fig, "ch01-delais.png")


def fig_axe_tronque():
    setup(); c = charger()["cmd"]; m = c.groupby(c["date_commande"].dt.year)["panier"].mean()
    fig, ax = plt.subplots(1, 2, figsize=(8, 2.9))
    for a, (y0, t) in zip(ax, [(97, "Axe tronqué à 97 € : une envolée ?"), (0, "Axe à zéro : une hausse modeste")]):
        a.bar([str(i) for i in m.index], m.values, color=[MUET, MUET, BLEU]); a.set_ylim(y0, 106 if y0 else 115); a.set_title(t)
        for i, v in enumerate(m.values): a.text(i, v + (0.3 if y0 else 1.5), f"{v:.1f}".replace(".", ",") + " €", ha="center", fontsize=8)
        a.grid(False); a.set_yticks([])
    save(fig, "ch01-axe-tronque.png")


def fig_nuages():
    setup(); j = charger()["j"]
    from statsmodels.nonparametric.smoothers_lowess import lowess
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
    for a, (col, xl) in zip(ax, [("depense_pub", "dépense publicitaire du jour (€)"), ("temperature_moy", "température moyenne (°C)")]):
        a.scatter(j[col], j["nb_commandes"], s=7, color=BLEU, alpha=0.35)
        l = lowess(j["nb_commandes"], j[col], frac=0.4); a.plot(l[:, 0], l[:, 1], color=ORANGE, lw=2)
        a.set_xlabel(xl); a.set_ylabel("commandes du jour"); a.set_title(f"r = {j[col].corr(j['nb_commandes']):.2f}".replace(".", ","))
    save(fig, "ch01-nuages.png")


def fig_groupes():
    setup(); c = charger(); cmd, liv = c["cmd"], c["liv"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2))
    g = [cmd.loc[cmd["canal"] == k, "panier"] for k in ["Boutique", "Site", "Réseaux"]]
    b = ax[0].boxplot(g, tick_labels=["Boutique", "Site", "Réseaux"], showfliers=False, patch_artist=True, medianprops=dict(color=ORANGE))
    for p in b["boxes"]: p.set(facecolor="#cde2fb", edgecolor=BLEU)
    ax[0].set_title("Panier par canal : trois boîtes presque identiques"); ax[0].set_ylabel("€")
    t = [liv.loc[liv["transporteur"] == k, "delai"] for k in ["Transporteur A", "Transporteur B", "Transporteur C"]]
    b = ax[1].boxplot(t, tick_labels=["A", "B", "C"], showfliers=False, patch_artist=True, medianprops=dict(color=ORANGE))
    for p, col in zip(b["boxes"], ["#cde2fb", "#cde2fb", "#f7c9b8"]): p.set(facecolor=col, edgecolor=BLEU)
    ax[1].set_title("Délai de livraison par transporteur : le C est plus lent"); ax[1].set_ylabel("jours"); ax[1].set_xlabel("transporteur")
    save(fig, "ch01-groupes.png")


def fig_profils():
    setup(); cmd = charger()["cmd"]
    t = pd.crosstab(cmd["canal"], cmd["mode_livraison"], normalize="index") * 100
    fig, ax = plt.subplots(figsize=(7, 2.6)); left = np.zeros(len(t))
    for col, color in zip(t.columns, [BLEU, ORANGE, AQUA]):
        ax.barh(t.index, t[col], left=left, color=color, label=col)
        for i, v in enumerate(t[col]):
            if v > 6: ax.text(left[i] + v / 2, i, f"{v:.0f} %", ha="center", va="center", color="white", fontsize=8)
        left += t[col].values
    ax.set_xlim(0, 100); ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.02), fontsize=8); ax.set_xlabel("part des commandes du canal (%)"); ax.grid(False)
    save(fig, "ch01-profils.png")


def fig_correlations():
    setup(); j = charger()["j"]
    cols = ["nb_commandes", "chiffre_affaires", "temperature_moy", "pluie_mm", "promo_active", "depense_pub"]
    lab = ["commandes", "CA", "température", "pluie", "promotion", "publicité"]
    r = j[cols].corr().values
    fig, ax = plt.subplots(figsize=(4.8, 4.2)); im = ax.imshow(r, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(6)); ax.set_xticklabels(lab, rotation=40, ha="right", fontsize=8); ax.set_yticks(range(6)); ax.set_yticklabels(lab, fontsize=8); ax.grid(False)
    for i in range(6):
        for k in range(6): ax.text(k, i, f"{r[i, k]:.2f}".replace(".", ","), ha="center", va="center", fontsize=7, color="white" if abs(r[i, k]) > 0.6 else "black")
    fig.colorbar(im, shrink=0.8); ax.set_title("Corrélations entre indicateurs journaliers")
    save(fig, "ch01-correlations.png")


def fig_simpson():
    setup(); j = charger()["j"]; j = j.assign(mois=j["date"].dt.month)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2), gridspec_kw={"width_ratios": [0.6, 1.4]})
    g = j.groupby("promo_active")["chiffre_affaires"].mean()
    ax[0].bar(["sans", "avec"], g.values, color=[MUET, ORANGE]); ax[0].set_xlabel("promotion"); ax[0].set_ylim(0, 4200); ax[0].set_title("Tous les jours confondus")
    for i, v in enumerate(g.values): ax[0].text(i, v + 60, f"{v:,.0f} €".replace(",", " "), ha="center", fontsize=8)
    ax[0].set_ylabel("CA moyen par jour (€)"); ax[0].grid(False)
    m = j[j["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack()
    x = np.arange(4); ax[1].bar(x - 0.18, m[0], 0.36, color=MUET, label="sans promotion"); ax[1].bar(x + 0.18, m[1], 0.36, color=ORANGE, label="avec promotion")
    ax[1].set_xticks(x); ax[1].set_xticklabels(["janvier", "juin", "juillet", "novembre"]); ax[1].set_title("À mois égal : la promotion gagne dans les quatre mois"); ax[1].legend(fontsize=8); ax[1].grid(False)
    save(fig, "ch01-simpson.png")


def fig_saisonnalite():
    setup(); j = charger()["j"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.0))
    s = j.groupby(j["date"].dt.dayofweek)["nb_commandes"].mean(); ax[0].bar(JOURS, s.values, color=BLEU); ax[0].set_title("Commandes par jour de la semaine"); ax[0].set_ylabel("moyenne par jour")
    s = j.groupby(j["date"].dt.month)["nb_commandes"].mean(); ax[1].bar(MOIS, s.values, color=AQUA); ax[1].set_title("Commandes par mois de l'année"); ax[1].tick_params(axis="x", labelsize=8)
    save(fig, "ch01-saisonnalite.png")


def fig_rupture_prix():
    setup(); c = charger(); cmd = c["cmd"]; m = cmd.groupby(cmd["date_commande"].dt.to_period("M"))["panier"].mean()
    l = c["lig"].merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(c["prod"][["id_produit", "prix_vente"]], on="id_produit")
    idx = (l["prix_unitaire"] / l["prix_vente"]).groupby(l["date_commande"].dt.to_period("M")).mean()
    fig, ax = plt.subplots(1, 2, figsize=(10, 2.9))
    lab = [f"{MOIS[i % 12]}\n{2023 + i // 12}" for i in range(0, 36, 6)]
    ax[0].plot(range(36), m.values, color=BLEU, marker="o", ms=3); ax[0].axvline(23.5, color=ORANGE, ls="--")
    ax[0].set_xticks(range(0, 36, 6)); ax[0].set_xticklabels(lab, fontsize=8); ax[0].set_ylabel("panier moyen (€)"); ax[0].set_title("Panier moyen : la saison masque la hausse")
    ax[1].plot(range(36), idx.values, color=AQUA, marker="o", ms=3); ax[1].axvline(23.5, color=ORANGE, ls="--")
    ax[1].set_xticks(range(0, 36, 6)); ax[1].set_xticklabels(lab, fontsize=8); ax[1].set_ylabel("prix payé / prix catalogue 2023-2024"); ax[1].set_title("Prix à produits constants : une marche de 3 %")
    save(fig, "ch01-rupture-prix.png")


def fig_incidents():
    setup(); c = charger(); j, doub = incidents_jours(c["ji"]); vrai = set(c["vi"]["date"]); sig = signaler(j, doub, 4)
    j25 = j[j["date"].dt.year == 2025]
    fig, ax = plt.subplots(figsize=(10, 3.3)); ax.plot(j25["date"], j25["chiffre_affaires"], color=MUET, lw=0.9)
    v = j25[j25["date"].isin(vrai)]; ax.scatter(v["date"], v["chiffre_affaires"], s=60, facecolors="none", edgecolors=ORANGE, lw=1.6, label="incident réel (vérité)", zorder=3)
    s = j25[j25["date"].isin(sig)]; ax.scatter(s["date"], s["chiffre_affaires"], s=14, color=BLEU, label="jour signalé (seuil 4)", zorder=4)
    ax.set_yscale("log"); ax.set_ylabel("CA du jour (€, échelle log)"); ax.legend(fontsize=8, loc="upper left"); ax.set_title("2025 : jours signalés par la méthode et incidents réellement injectés")
    save(fig, "ch01-incidents.png")


def fig_seuils():
    setup(); c = charger(); j, doub = incidents_jours(c["ji"]); vrai = set(c["vi"]["date"])
    seuils = np.arange(2.5, 6.01, 0.25); pr = []; ra = []
    for s in seuils:
        p, r = precision_rappel(signaler(j, doub, s), vrai); pr.append(p); ra.append(r)
    fig, ax = plt.subplots(figsize=(6, 3.0)); ax.plot(seuils, np.array(pr) * 100, color=BLEU, label="précision"); ax.plot(seuils, np.array(ra) * 100, color=ORANGE, label="rappel")
    ax.set_xlabel("seuil du score z"); ax.set_ylabel("%"); ax.set_ylim(0, 105); ax.legend(); ax.set_title("Plus le seuil monte, plus on rate d'incidents")
    save(fig, "ch01-seuils.png")


def toutes_les_figures():
    for f in (fig_panier, fig_classes, fig_barres, fig_serie_mensuelle, fig_delais, fig_axe_tronque, fig_nuages, fig_groupes, fig_profils, fig_correlations, fig_simpson,
              fig_saisonnalite, fig_rupture_prix, fig_incidents, fig_seuils):
        f()


if __name__ == "__main__":
    toutes_les_figures()
