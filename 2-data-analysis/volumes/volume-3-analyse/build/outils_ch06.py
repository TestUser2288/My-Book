"""Outils du chapitre 6 (KPI) — série 2, volume III : chargement, calcul des indicateurs de la boutique, limites de contrôle, figures.
Tout est déterministe (graines fixes). Les KPI sont calculés par UNE seule fonction (`kpis`) pour qu'aucun chiffre ne soit calculé de deux façons."""
import os
import numpy as np
import pandas as pd

TVA = 0.20


def charger(D=None):
    D = D or os.environ["DONNEES"]
    r = lambda f, **k: pd.read_csv(os.path.join(D, f), **k)
    d = dict(cmd=r("commandes.csv"), lig=r("lignes_commande.csv"), prod=r("produits.csv"), ret=r("retours.csv"), jours=r("jours_exploitation.csv"),
             liv=r("livraisons.csv"), sess=r("sessions_web.csv"), stock=r("stock_quotidien.csv"), bench=r("benchmark_secteur.csv"), budget=r("budget_reel_2025.csv"),
             cli=r("clients.csv"), cr=r("compte_resultat_mensuel.csv"), bil=r("bilan_annuel.csv"), camp=r("campagnes.csv"))
    x = d["lig"].merge(d["cmd"][["id_commande", "date_commande", "canal", "id_client", "code_promo"]], on="id_commande").merge(d["prod"][["id_produit", "categorie", "cout_achat"]], on="id_produit")
    x["annee"] = x["date_commande"].str[:4].astype(int)
    x["mois"] = x["date_commande"].str[:7]
    x["marge_ht"] = x["montant"] / (1 + TVA) - x["quantite"] * x["cout_achat"]
    x["retourne"] = x["id_ligne"].isin(d["ret"]["id_ligne"])
    d["x"] = x
    return d


def kpis(d, annee=2025):
    """Les indicateurs de la boutique pour une année (tous calculés ici, une seule fois)."""
    x = d["x"][d["x"]["annee"] == annee]
    ca = x["montant"].sum(); n = x["id_commande"].nunique()
    out = {"CA TTC (€)": ca, "Commandes": n, "Panier moyen (€)": ca / n,
           "Taux de marge brute (HT, %)": x["marge_ht"].sum() / (ca / (1 + TVA)) * 100,
           "Taux de retour (lignes, %)": x["retourne"].mean() * 100,
           "Part du site dans le CA (%)": x.loc[x["canal"] == "Site", "montant"].sum() / ca * 100}
    if annee == 2025:
        s = d["sess"]
        out["Taux de conversion du site (%)"] = s["commande"].mean() * 100
        l = d["liv"][d["liv"]["date_commande"].str[:4] == "2025"]
        out["Livraisons à l'heure (%)"] = (1 - l["retard"].mean()) * 100
        out["Taux de rupture de stock (%)"] = d["stock"]["rupture"].mean() * 100
        out["Clients actifs sur 12 mois (%)"] = x["id_client"].nunique() / len(d["cli"]) * 100
        premiers = d["cmd"].groupby("id_client")["date_commande"].min()
        nouveaux = int((premiers.str[:4] == "2025").sum())
        out["Coût d'acquisition d'un client (€)"] = d["cr"][d["cr"]["mois"].str[:4] == "2025"]["marketing"].sum() / nouveaux
        cr = d["cr"][d["cr"]["mois"].str[:4] == "2025"]
        out["Frais de personnel / CA HT (%)"] = cr["frais_personnel"].sum() / cr["ca_ht"].sum() * 100
        b = d["bil"][d["bil"]["annee"] == 2025].iloc[0]
        out["Rotation du stock (par an)"] = cr["achats"].sum() / b["stock"]
    return out


def limites_p(p_moy, n, k=3.0):
    """limites d'une carte de contrôle pour une proportion : p ± k racine(p(1-p)/n)"""
    s = np.sqrt(p_moy * (1 - p_moy) / np.asarray(n, float))
    return np.clip(p_moy - k * s, 0, 1), np.clip(p_moy + k * s, 0, 1)


def semaines(df, col_date, valeur, agg="mean"):
    s = pd.to_datetime(df[col_date]).dt.to_period("W-SUN")
    g = df.groupby(s)[valeur].agg(["mean", "size", "sum"])
    g.index = g.index.start_time
    return g


# ---------------------------------------------------------------------------------------------------- séries mensuelles et position sectorielle
DIRECTION = {"Taux de marge brute (HT, %)": 1, "Taux de retour (lignes, %)": -1, "Panier moyen (€)": 1, "Taux de conversion du site (%)": 1, "Part du site dans le CA (%)": 1,
             "Rotation du stock (par an)": 1, "Taux de rupture de stock (%)": -1, "Livraisons à l'heure (%)": 1, "Coût d'acquisition d'un client (€)": -1,
             "Clients actifs sur 12 mois (%)": 1, "Frais de personnel / CA HT (%)": 0}
ASSOC = {"Taux de marge brute (HT, %)": "Taux de marge brute (HT)", "Taux de retour (lignes, %)": "Taux de retour (lignes)", "Panier moyen (€)": "Panier moyen",
         "Taux de conversion du site (%)": "Taux de conversion du site", "Part du site dans le CA (%)": "Part du site dans le CA", "Rotation du stock (par an)": "Rotation du stock (par an)",
         "Taux de rupture de stock (%)": "Taux de rupture de stock", "Livraisons à l'heure (%)": "Livraisons à l'heure", "Coût d'acquisition d'un client (€)": "Coût d'acquisition d'un client",
         "Clients actifs sur 12 mois (%)": "Clients actifs à 12 mois", "Frais de personnel / CA HT (%)": "Part des frais de personnel dans le CA"}


def position_secteur(d, annee=2025):
    """pour chaque KPI comparable : valeur, médiane, quartiles du secteur (fictif) et position (meilleur / dans la norme / moins bon / à interpréter)"""
    k = kpis(d, annee)
    b = d["bench"].set_index("indicateur")
    lignes = []
    for nom, ref in ASSOC.items():
        v = k[nom]; q1, med, q3 = b.loc[ref, "quartile_1"], b.loc[ref, "mediane_secteur"], b.loc[ref, "quartile_3"]
        s = DIRECTION[nom]
        if s == 0:
            pos = "à interpréter"
        else:
            bon, mauvais = (q3, q1) if s > 0 else (q1, q3)
            pos = "meilleur" if (v - bon) * s > 0 else ("moins bon" if (v - mauvais) * s < 0 else "dans la norme")
        lignes.append((nom, round(v, 2), q1, med, q3, pos))
    return pd.DataFrame(lignes, columns=["indicateur", "boutique", "quartile_1", "mediane", "quartile_3", "position"])


def mensuel(d):
    x = d["x"][d["x"]["annee"] == 2025]
    g = x.groupby("mois").agg(ca=("montant", "sum"), commandes=("id_commande", "nunique"), marge=("marge_ht", "sum"), retour=("retourne", "mean")).reset_index()
    g["panier"] = g["ca"] / g["commandes"]
    g["taux_marge"] = g["marge"] / (g["ca"] / (1 + TVA)) * 100
    g["retour"] *= 100
    s = d["sess"].assign(mois=d["sess"]["date"].str[:7]).groupby("mois")["commande"].mean() * 100
    l = d["liv"][d["liv"]["date_commande"].str[:4] == "2025"].assign(mois=lambda t: t["date_commande"].str[:7]).groupby("mois")["retard"].mean()
    st = d["stock"].assign(mois=d["stock"]["date"].str[:7]).groupby("mois")["rupture"].mean() * 100
    g = g.merge(s.rename("conversion").reset_index(), on="mois").merge((100 * (1 - l)).rename("a_l_heure").reset_index(), on="mois").merge(st.rename("rupture").reset_index(), on="mois")
    return g


# ---------------------------------------------------------------------------------------------------- figures
def _style():
    from style import setup
    setup()


def fig_arbre(d, nom="ch06-arbre-ca.png"):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from style import BLEU, ORANGE, AQUA, VIOLET, MUET, ENCRE, save
    _style()
    x = d["x"][(d["x"]["annee"] == 2025) & (d["x"]["canal"] == "Site")]
    s = d["sess"]; N = len(s); n = x["id_commande"].nunique(); ca = x["montant"].sum()
    fig, ax = plt.subplots(figsize=(8.4, 4.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    def boite(cx, cy, w, h, titre, val, couleur):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.04,rounding_size=0.12", fc="white", ec=couleur, lw=2))
        ax.text(cx, cy + 0.17, val, ha="center", va="center", fontsize=11.5, color=ENCRE, weight="bold")
        ax.text(cx, cy - 0.27, titre, ha="center", va="center", fontsize=8.5, color=MUET)
    boite(5, 5.2, 3.2, 1.0, "chiffre d'affaires du site, 2025", f"{ca:,.0f} €".replace(",", " "), BLEU)
    xs = [1.7, 5.0, 8.3]
    for cx, (t, v, c) in zip(xs, [("sessions", f"{N:,}".replace(",", " "), ORANGE), ("taux de conversion", f"{n / N * 100:.2f} %".replace(".", ","), AQUA), ("panier moyen", f"{ca / n:.2f} €".replace(".", ","), VIOLET)]):
        ax.plot([5, cx], [4.65, 3.55], color=MUET, lw=1); boite(cx, 3.0, 2.8, 1.0, t, v, c)
    ax.text(3.35, 3.0, "×", fontsize=18, ha="center", va="center", color=MUET); ax.text(6.65, 3.0, "×", fontsize=18, ha="center", va="center", color=MUET)
    par = s.groupby("source").size().sort_values(ascending=False)
    ax.text(1.7, 1.75, "trafic par source (somme)", ha="center", fontsize=8.5, color=MUET)
    for i, (src, k) in enumerate(par.items()):
        ax.text(0.35 + (i % 3) * 1.35, 1.25 - (i // 3) * 0.55, f"{ {'reseaux': 'réseaux', 'referent': 'référent'}.get(src, src)}\n{k / N * 100:.0f} %", fontsize=7.8, ha="left", va="center", color=ENCRE)
    ax.text(5.0, 1.75, "commandes ÷ sessions", ha="center", fontsize=8.5, color=MUET); ax.text(8.3, 1.75, "CA ÷ commandes", ha="center", fontsize=8.5, color=MUET)
    save(fig, nom)


def indices_goodhart(d):
    """trois « victoires » d'un KPI et leur contrepartie, en indice (situation de départ = 100)"""
    x = d["x"]; j = d["jours"].set_index("date")
    dm = x.groupby("date_commande").agg(marge=("marge_ht", "sum"), n=("id_commande", "nunique"))
    g = j.join(dm).groupby("promo_active")[["n", "marge"]].mean()
    x25 = x[x["annee"] == 2025]; op = x25.groupby("id_commande")["montant"].sum(); k = op[op >= 40]
    s = d["sess"]; C = s["commande"].sum(); N = len(s); cr = s.loc[s["source"] == "reseaux", "commande"].mean(); ajout = 20000
    return {"promo": (g.loc[1, "n"] / g.loc[0, "n"] * 100, g.loc[1, "marge"] / g.loc[0, "marge"] * 100),
            "seuil": (k.mean() / op.mean() * 100, k.sum() / op.sum() * 100),
            "trafic": ((C + ajout * cr) / C * 100, (C + ajout * cr) / (N + ajout) / (C / N) * 100)}


def fig_goodhart(d, nom="ch06-goodhart.png"):
    import matplotlib.pyplot as plt
    from style import BLEU, ORANGE, ROUGE, MUET, save
    _style()
    ind = indices_goodhart(d)
    cas = [("Promotion : jours de promotion\ncontre autres jours", "promo", ("commandes\npar jour", "marge HT\npar jour")),
           ("Seuil de panier à 40 € :\npaniers retenus contre tous", "seuil", ("panier\nmoyen", "chiffre\nd'affaires")),
           ("+20 000 sessions « réseaux » :\navant contre après", "trafic", ("commandes", "taux de\nconversion"))]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.5), sharey=True)
    for ax, (titre, cle, (l1, l2)) in zip(axes, cas):
        a, b = ind[cle]
        ax.bar([0, 1], [a, b], color=[BLEU, ORANGE], width=0.6); ax.axhline(100, color=MUET, lw=1, ls="--")
        for i, v in enumerate([a, b]):
            ax.text(i, v + 2, f"{v:.0f}", ha="center", fontsize=10)
        ax.set_xticks([0, 1]); ax.set_xticklabels([l1, l2], fontsize=8.5); ax.set_title(titre, loc="left", fontsize=9); ax.grid(False)
    axes[0].set_ylim(60, 135); axes[0].set_ylabel("indice (100 = référence)", fontsize=8.5)
    save(fig, nom)


def fig_pcharts(d, nom="ch06-cartes-controle.png"):
    import matplotlib.pyplot as plt
    from style import BLEU, ROUGE, MUET, save
    _style()
    x = d["x"][d["x"]["annee"] == 2025]
    w = semaines(x, "date_commande", "retourne"); w = w[w["size"] >= 300]
    pb = w["sum"].sum() / w["size"].sum(); lo, hi = limites_p(pb, w["size"])
    l = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"])
    wl = semaines(l, "date_commande", "ok"); wl = wl[wl["size"] >= 100]
    base = wl[wl.index < "2025-11-24"]; pl = base["sum"].sum() / base["size"].sum(); lo2, hi2 = limites_p(pl, wl["size"])
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.3))
    for ax, ww, p, a, b, titre in [(axes[0], w, pb, lo, hi, "Taux de retour hebdomadaire (lignes, %)"), (axes[1], wl, pl, lo2, hi2, "Livraisons à l'heure, par semaine (%)")]:
        v = ww["mean"].values * 100; hors = (ww["mean"].values < a) | (ww["mean"].values > b)
        ax.fill_between(ww.index, a * 100, b * 100, color=BLEU, alpha=0.10, lw=0); ax.axhline(p * 100, color=MUET, lw=1, ls="--")
        ax.plot(ww.index, v, color=BLEU, lw=1.4); ax.scatter(ww.index[hors], v[hors], color=ROUGE, zorder=3, s=26)
        ax.set_title(titre, loc="left", fontsize=9.5); ax.tick_params(axis="x", labelsize=8); ax.tick_params(axis="y", labelsize=8)
    axes[0].set_ylim(3, 10); axes[1].axvline(pd.Timestamp("2025-11-24"), color=MUET, lw=0.8)
    axes[1].text(pd.Timestamp("2025-11-20"), 52, "limites calculées\navant le 24/11", ha="right", fontsize=8, color=MUET)
    save(fig, nom)


def fig_bruit(nom="ch06-bruit.png"):
    import matplotlib.pyplot as plt
    from scipy.stats import binom
    from style import BLEU, ORANGE, MUET, save
    _style()
    n, p = 530, 0.059
    k = np.arange(int(n * p) - 22, int(n * p) + 23)
    ecart = (k / n - p) * 100; proba = binom.pmf(k, n, p)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(ecart, proba, width=0.17, color=[ORANGE if abs(e) >= 1 else BLEU for e in ecart])
    ax.set_xlabel("écart du taux hebdomadaire à sa vraie valeur (points de pourcentage)"); ax.set_yticks([])
    ax.text(2.4, proba.max() * 0.55, f"écarts ≥ 1 point :\n{proba[np.abs(ecart) >= 1].sum() * 100:.0f} % des semaines".replace(".", ","), ha="center", color=ORANGE, fontsize=9)
    ax.grid(False); save(fig, nom)


def fig_benchmark(d, nom="ch06-benchmark.png"):
    import matplotlib.pyplot as plt
    from style import BLEU, ORANGE, AQUA, ROUGE, MUET, ENCRE, save
    _style()
    t = position_secteur(d)
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    y = np.arange(len(t))[::-1]
    for yy, r in zip(y, t.itertuples()):
        ax.barh(yy, 1, left=0, height=0.55, color="#dbe7f7")
        z = (r.boutique - r.quartile_1) / (r.quartile_3 - r.quartile_1)
        z = np.clip(z, -0.6, 1.6)
        c = {"meilleur": AQUA, "dans la norme": BLEU, "moins bon": ROUGE, "à interpréter": MUET}[r.position]
        ax.scatter([z], [yy], color=c, s=55, zorder=3)
        ax.text(1.75, yy, r.position, va="center", fontsize=8.3, color=c)
    ax.set_yticks(y); ax.set_yticklabels([s.replace(" (HT, %)", "").replace(" (%)", "").replace(" (€)", "").replace(" (par an)", "") for s in t["indicateur"]], fontsize=8.3)
    ax.set_xticks([0, 0.5, 1]); ax.set_xticklabels(["1er quartile", "médiane", "3e quartile"], fontsize=8); ax.set_xlim(-0.7, 2.2); ax.grid(False)
    ax.set_title("La boutique (point) par rapport à la zone centrale du secteur (bande bleue ; valeurs fictives)", loc="left", fontsize=9.3)
    save(fig, nom)


def fig_tableau_bord(d, nom="ch06-tableau-bord.png"):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from style import BLEU, AQUA, ROUGE, ORANGE, MUET, ENCRE, save
    _style()
    m = mensuel(d); k = kpis(d, 2025); k24 = kpis(d, 2024)
    pos = position_secteur(d).set_index("indicateur")["position"]
    tuiles = [("Chiffre d'affaires", "ca", "CA TTC (€)", lambda v: f"{v / 1000:,.0f} k€".replace(",", " "), None, k24["CA TTC (€)"]),
              ("Panier moyen", "panier", "Panier moyen (€)", lambda v: f"{v:.1f} €".replace(".", ","), "Panier moyen (€)", k24["Panier moyen (€)"]),
              ("Taux de marge brute", "taux_marge", "Taux de marge brute (HT, %)", lambda v: f"{v:.1f} %".replace(".", ","), "Taux de marge brute (HT, %)", k24["Taux de marge brute (HT, %)"]),
              ("Taux de retour", "retour", "Taux de retour (lignes, %)", lambda v: f"{v:.1f} %".replace(".", ","), "Taux de retour (lignes, %)", k24["Taux de retour (lignes, %)"]),
              ("Conversion du site", "conversion", "Taux de conversion du site (%)", lambda v: f"{v:.2f} %".replace(".", ","), "Taux de conversion du site (%)", None),
              ("Livraisons à l'heure", "a_l_heure", "Livraisons à l'heure (%)", lambda v: f"{v:.0f} %", "Livraisons à l'heure (%)", None),
              ("Ruptures de stock", "rupture", "Taux de rupture de stock (%)", lambda v: f"{v:.1f} %".replace(".", ","), "Taux de rupture de stock (%)", None),
              ("Commandes", "commandes", "Commandes", lambda v: f"{v:,.0f}".replace(",", " "), None, k24["Commandes"])]
    couleur = {"meilleur": AQUA, "dans la norme": BLEU, "moins bon": ROUGE, "à interpréter": MUET}
    fig, axes = plt.subplots(2, 4, figsize=(9.8, 4.6))
    for ax, (titre, col, cle, fmt, ref, v24) in zip(axes.ravel(), tuiles):
        ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        c = couleur[pos[ref]] if ref else MUET
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.0,rounding_size=0.06", fc="white", ec=c, lw=2.2, transform=ax.transAxes))
        ax.text(0.08, 0.86, titre, fontsize=8.8, color=MUET, va="center")
        ax.text(0.08, 0.66, fmt(k[cle]), fontsize=15, color=ENCRE, weight="bold", va="center")
        if v24 is not None:
            dlt = (k[cle] / v24 - 1) * 100 if "%" not in cle else k[cle] - v24
            unite = " pt" if "%" in cle else " %"
            ax.text(0.08, 0.50, f"{dlt:+.1f}{unite} vs 2024".replace(".", ","), fontsize=8, color=MUET, va="center")
        elif ref:
            ax.text(0.08, 0.50, pos[ref] + " (secteur)", fontsize=8, color=c, va="center")
        sp = ax.inset_axes([0.08, 0.08, 0.84, 0.30]); sp.plot(range(len(m)), m[col], color=c, lw=1.4); sp.axis("off")
        sp.scatter([len(m) - 1], [m[col].iloc[-1]], color=c, s=10)
    fig.suptitle("Tableau de bord de la boutique, 2025 : valeur annuelle, variation et tendance mensuelle", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); save(fig, nom)


def seuils_hebdo(d):
    """seuils d'alerte (orange à 2 écarts-types, rouge à 3) du côté défavorable, pour quatre indicateurs hebdomadaires, d'après la variabilité de l'échantillonnage (carte p)"""
    x = d["x"][d["x"]["annee"] == 2025]
    liv = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"])
    stock = d["stock"].assign(date=pd.to_datetime(d["stock"]["date"]).dt.strftime("%Y-%m-%d"))
    series = {"Taux de retour (lignes)": (semaines(x, "date_commande", "retourne"), -1, 300, None),
              "Livraisons à l'heure": (semaines(liv, "date_commande", "ok"), 1, 100, "2025-11-24"),
              "Conversion du site": (semaines(d["sess"], "date", "commande"), 1, 500, None),
              "Rupture de stock": (semaines(stock, "date", "rupture"), -1, 100, None)}
    out = {}
    for nom, (w, sens, nmin, fin_base) in series.items():
        w = w[w["size"] >= nmin]
        base = w if fin_base is None else w[w.index < fin_base]
        p = base["sum"].sum() / base["size"].sum(); n = base["size"].mean(); sd = np.sqrt(p * (1 - p) / n)
        out[nom] = dict(p=p * 100, n=n, orange=(p - sens * 2 * sd) * 100, rouge=(p - sens * 3 * sd) * 100, sens=sens)
    return out
