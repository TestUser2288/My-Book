"""Outils du chapitre 9 (analyse financière) : chargement, comptes annuels, ratios, coûts fixes/variables, point mort, rentabilité par canal.
Tout est SIMULÉ (voir la docstring de donnees_a3.py) : TVA fictive de 20 %, résultat net approché à 70 % du résultat d'exploitation."""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

TVA = 0.20
D = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
CHARGES = ["frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "amortissements", "autres_charges"]
PART_EMPRUNT_COURT = 15000          # remboursement annuel supposé : part de l'emprunt exigible à moins d'un an (hypothèse du chapitre)


def charger():
    lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
    cr = lire("compte_resultat_mensuel.csv")
    cr["annee"] = cr["mois"].str[:4].astype(int)
    return cr, lire("bilan_annuel.csv"), lire("commandes.csv"), lire("lignes_commande.csv"), lire("produits.csv"), lire("campagnes.csv"), lire("benchmark_secteur.csv")


def annuel(cr):
    """compte de résultat annuel (somme des 12 mois)"""
    cols = ["ca_ht", "achats", "variation_stock", "marge_brute"] + CHARGES + ["resultat_exploitation"]
    a = cr.groupby("annee")[cols].sum()
    a["charges_totales"] = a[CHARGES].sum(axis=1)
    return a


def ventes_mensuelles(cmd, lig):
    """chiffre d'affaires HT par mois reconstitué à partir des lignes de la base (montant TTC / 1,2)"""
    x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande")
    x["mois"] = x["date_commande"].str[:7]
    return (x.groupby("mois")["montant"].sum() / (1 + TVA)).rename("ca_base_ht")


def ratios(a, b, bm=None):
    """ratios annuels. a : compte de résultat annuel ; b : bilan annuel (index annee)"""
    r = pd.DataFrame(index=a.index)
    r["taux_marge_brute"] = a["marge_brute"] / a["ca_ht"]
    r["taux_marge_exploitation"] = a["resultat_exploitation"] / a["ca_ht"]
    r["resultat_net_approche"] = 0.7 * a["resultat_exploitation"]
    cp = b["capitaux_propres"]
    r["rentabilite_capitaux_propres"] = r["resultat_net_approche"] / cp
    r["rotation_stock"] = a["achats"] / b["stock"]
    r["jours_stock"] = 365 / r["rotation_stock"]
    r["delai_clients_j"] = b["creances_clients"] / a["ca_ht"] * 365
    r["delai_fournisseurs_j"] = b["dettes_fournisseurs"] / a["achats"] * 365
    r["bfr"] = b["stock"] + b["creances_clients"] - b["dettes_fournisseurs"]
    r["bfr_jours_ca"] = r["bfr"] / a["ca_ht"] * 365
    court = b["dettes_fournisseurs"] + b["autres_dettes"] + PART_EMPRUNT_COURT
    r["liquidite_generale"] = (b["stock"] + b["creances_clients"] + b["tresorerie"]) / court
    r["liquidite_immediate"] = b["tresorerie"] / court
    r["endettement"] = b["emprunt"] / cp
    r["autonomie_financiere"] = cp / (cp + b["emprunt"] + b["dettes_fournisseurs"] + b["autres_dettes"])
    r["part_personnel"] = a["frais_personnel"] / a["ca_ht"]
    return r


def couts_regression(cr):
    """pour chaque ligne de coût : coût mensuel ~ a + b x CA HT du mois ; retourne pente (part variable), constante, R²"""
    X = sm.add_constant(cr["ca_ht"])
    out = {}
    for c in ["achats", "frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "amortissements", "autres_charges"]:
        m = sm.OLS(cr[c], X).fit()
        out[c] = {"pente": m.params["ca_ht"], "constante": m.params["const"], "r2": m.rsquared, "ic_bas": m.conf_int().loc["ca_ht", 0], "ic_haut": m.conf_int().loc["ca_ht", 1]}
    return pd.DataFrame(out).T


def point_mort(ca, cv, cf):
    """seuil de rentabilité : CA* = CF / taux de marge sur coûts variables"""
    taux = 1 - cv / ca
    return {"taux_mcv": taux, "seuil": cf / taux, "marge_securite": (ca - cf / taux) / ca, "levier": (ca - cv) / (ca - cv - cf)}


def rentabilite_canal(cmd, lig, prod, cr, camp, annee=2025):
    """résultat par canal pour l'année, avec deux clés de répartition des charges communes"""
    x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
    x = x[x["date_commande"].str[:4] == str(annee)]
    x["ca_ht"] = x["montant"] / (1 + TVA)
    x["achats"] = x["quantite"] * x["cout_achat"]
    g = x.groupby("canal").agg(ca_ht=("ca_ht", "sum"), achats=("achats", "sum"), lignes=("id_ligne", "size"), ttc=("montant", "sum"))
    cc = cmd[cmd["date_commande"].str[:4] == str(annee)].groupby("canal").size().rename("commandes")
    g = g.join(cc)
    g["marge_brute"] = g["ca_ht"] - g["achats"]
    c = cr[cr["annee"] == annee]
    tot = {k: c[k].sum() for k in ["livraison", "marketing", "frais_bancaires", "frais_personnel", "loyers_charges", "amortissements", "autres_charges"]}
    g["frais_bancaires"] = g["ttc"] / g["ttc"].sum() * tot["frais_bancaires"]
    # livraison : seulement les commandes livrées (Site, Réseaux), au prorata du nombre de commandes
    liv = g["commandes"].where(g.index != "Boutique", 0.0)
    g["livraison"] = liv / liv.sum() * tot["livraison"]
    m = camp[camp["mois"].str[:4] == str(annee)].groupby("source")["depense"].sum()
    g["marketing_direct"] = 0.0
    g.loc["Site", "marketing_direct"] = m["payant"] + m["email"]
    g.loc["Réseaux", "marketing_direct"] = m["reseaux"]
    communes = tot["frais_personnel"] + tot["loyers_charges"] + tot["amortissements"] + tot["autres_charges"]
    g["communes_prorata_ca"] = g["ca_ht"] / g["ca_ht"].sum() * communes
    g["communes_prorata_commandes"] = g["commandes"] / g["commandes"].sum() * communes
    g["resultat_cle_ca"] = g["marge_brute"] - g["frais_bancaires"] - g["livraison"] - g["marketing_direct"] - g["communes_prorata_ca"]
    g["resultat_cle_commandes"] = g["marge_brute"] - g["frais_bancaires"] - g["livraison"] - g["marketing_direct"] - g["communes_prorata_commandes"]
    g["contribution"] = g["marge_brute"] - g["frais_bancaires"] - g["livraison"] - g["marketing_direct"]
    return g, tot


# ----------------------------------------------------------------------------------------------- figures
def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2
    setup()
    return plt, dict(BLEU=BLEU, ORANGE=ORANGE, AQUA=AQUA, VIOLET=VIOLET, ROUGE=ROUGE, MUET=MUET, ENCRE2=ENCRE2)


def fig_cascade(x, chemin):
    """cascade du compte de résultat d'une année : du chiffre d'affaires au résultat d'exploitation (k€)"""
    plt, C = _plt()
    etapes = [("Chiffre\nd'affaires", x["ca_ht"], "total"), ("Achats", -(x["achats"] - x["variation_stock"]), "cout"), ("Marge\nbrute", x["marge_brute"], "total"),
              ("Personnel", -x["frais_personnel"], "cout"), ("Loyers", -x["loyers_charges"], "cout"), ("Marketing", -x["marketing"], "cout"), ("Livraison", -x["livraison"], "cout"),
              ("Banque", -x["frais_bancaires"], "cout"), ("Amort.", -x["amortissements"], "cout"), ("Autres", -x["autres_charges"], "cout"), ("Résultat", x["resultat_exploitation"], "res")]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    niveau = 0.0
    for i, (nom, v, t) in enumerate(etapes):
        v = v / 1000
        if t == "cout":
            bas, h, col = niveau + v, -v, C["ROUGE"]
            niveau += v
        else:
            bas, h = 0, v
            col = C["BLEU"] if t == "total" else C["AQUA"]
            niveau = v
        ax.bar(i, h, bottom=bas, color=col, width=0.7)
        ax.text(i, bas + h + 12, f"{v:,.0f}".replace(",", " ").replace("-", "−"), ha="center", fontsize=8, color=C["ENCRE2"])
    ax.set_xticks(range(len(etapes))); ax.set_xticklabels([e[0] for e in etapes], fontsize=8)
    ax.set_ylabel("k€"); ax.set_ylim(0, 1240)
    ax.set_title("Du chiffre d'affaires au résultat, 2025 (k€ hors taxes)", loc="left")
    fig.savefig(chemin, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_point_mort(ca, cv, cf, pm, chemin):
    """droites de produits et de coûts totaux selon le chiffre d'affaires ; point mort et situation actuelle (k€)"""
    plt, C = _plt()
    xs = np.linspace(0, ca * 1.15, 50) / 1000
    v = cv / ca
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    ax.plot(xs, xs, color=C["BLEU"], lw=2); ax.plot(xs, cf / 1000 + v * xs, color=C["ROUGE"], lw=2); ax.axhline(cf / 1000, color=C["MUET"], lw=1, ls="--")
    s = pm["seuil"] / 1000
    ax.plot([s], [s], "o", color=C["VIOLET"], ms=7); ax.annotate(f"point mort\n{s:,.0f} k€".replace(",", " "), (s, s), xytext=(s - 330, s + 160), fontsize=8, arrowprops=dict(arrowstyle="-", color=C["MUET"]))
    ax.plot([ca / 1000], [ca / 1000], "o", color=C["AQUA"], ms=7); ax.annotate("2025", (ca / 1000, ca / 1000), xytext=(ca / 1000 + 25, ca / 1000 - 150), fontsize=8)
    ax.text(660, 660 - 150, "produits", color=C["BLEU"], ha="center", fontsize=8, rotation=33)
    ax.text(420, cf / 1000 + v * 420 + 55, "coûts totaux", color=C["ROUGE"], ha="center", fontsize=8, rotation=24)
    ax.text(10, cf / 1000 + 20, "coûts fixes", color=C["MUET"], fontsize=8)
    ax.set_xlabel("Chiffre d'affaires annuel (k€)"); ax.set_ylabel("k€"); ax.set_title("Seuil de rentabilité : où les produits rattrapent les coûts", loc="left")
    fig.savefig(chemin, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_canaux(g, chemin):
    """contribution et résultat par canal selon la clé de répartition des charges communes (k€)"""
    plt, C = _plt()
    canaux = list(g.index)
    x = np.arange(len(canaux)); w = 0.27
    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    ax.bar(x - w, g["contribution"] / 1000, w, color=C["BLEU"], label="contribution (avant charges communes)")
    ax.bar(x, g["resultat_cle_ca"] / 1000, w, color=C["ORANGE"], label="résultat, charges communes au prorata du CA")
    ax.bar(x + w, g["resultat_cle_commandes"] / 1000, w, color=C["VIOLET"], label="résultat, charges communes au prorata des commandes")
    ax.axhline(0, color=C["ENCRE2"], lw=0.8)
    for i in range(len(canaux)):
        for dx, col in ((-w, "contribution"), (0, "resultat_cle_ca"), (w, "resultat_cle_commandes")):
            v = g[col].iloc[i] / 1000
            ax.text(i + dx, v + (4 if v >= 0 else -14), f"{v:,.0f}".replace("-", "−"), ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(canaux); ax.set_ylabel("k€"); ax.set_ylim(-45, 205)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("Quel canal gagne de l'argent ? Cela dépend de la clé de répartition", loc="left")
    fig.savefig(chemin, dpi=200, bbox_inches="tight"); plt.close(fig)
