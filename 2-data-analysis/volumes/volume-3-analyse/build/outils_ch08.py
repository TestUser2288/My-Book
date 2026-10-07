"""Outils du chapitre 8 (Pareto, ABC, benchmarking) : classement cumulé, classes ABC, courbe de Pareto, indicateurs de la boutique, partagés par le livre et le cahier."""
import numpy as np
import pandas as pd


def pareto(valeurs):
    """Trie une série de valeurs positives par ordre décroissant et ajoute rang, part et part cumulée (en %) ; l'index de la série est conservé."""
    s = valeurs.sort_values(ascending=False)
    d = pd.DataFrame({"valeur": s})
    d["rang"] = np.arange(1, len(d) + 1)
    d["part_cumulee"] = s.cumsum() / s.sum() * 100
    d["part_elements"] = d["rang"] / len(d) * 100
    return d


def classes_abc(valeurs, seuils=(80, 95)):
    """Classe A tant que la part cumulée AVANT l'élément est inférieure au premier seuil, B jusqu'au second, C ensuite. Retourne la série des classes."""
    d = pareto(valeurs)
    avant = d["part_cumulee"] - d["valeur"] / valeurs.sum() * 100
    cl = np.where(avant < seuils[0], "A", np.where(avant < seuils[1], "B", "C"))
    return pd.Series(cl, index=d.index)


def courbe_pareto(nom, series, titre, etiquettes):
    """Courbes de Pareto superposées : `series` = liste de DataFrame issus de `pareto`."""
    import matplotlib.pyplot as plt
    from style import setup, save, BLEU, ORANGE, AQUA, MUET
    setup()
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for d, c, e in zip(series, (BLEU, ORANGE, AQUA), etiquettes):
        ax.plot(np.r_[0, d["part_elements"]], np.r_[0, d["part_cumulee"]], color=c, label=e)
    ax.plot([0, 100], [0, 100], color=MUET, lw=1, ls="--")
    ax.axhline(80, color=MUET, lw=0.8); ax.axvline(20, color=MUET, lw=0.8)
    ax.set_xlabel("Part des éléments, classés du plus grand au plus petit (%)"); ax.set_ylabel("Part cumulée de la valeur (%)")
    ax.set_title(titre, loc="left"); ax.legend(loc="lower right")
    save(fig, nom)


def charger(D):
    """Charge les fichiers et prépare le tableau des lignes de commande enrichi (année, canal, client, catégorie, coût, marge hors taxe, TVA fictive de 20 %)."""
    import os
    lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
    cmd = lire("commandes.csv", parse_dates=["date_commande"])
    cmd["annee"] = cmd["date_commande"].dt.year
    cmd["mois"] = cmd["date_commande"].dt.month
    lig, prod, ret, cli = lire("lignes_commande.csv"), lire("produits.csv"), lire("retours.csv"), lire("clients.csv")
    lg = lig.merge(cmd[["id_commande", "annee", "mois", "canal", "id_client"]], on="id_commande").merge(prod[["id_produit", "nom_produit", "categorie", "cout_achat", "date_lancement"]], on="id_produit")
    lg["marge"] = lg["montant"] / 1.2 - lg["quantite"] * lg["cout_achat"]
    lg["retournee"] = lg["id_ligne"].isin(ret["id_ligne"])
    return cmd, lg, prod, ret, cli


def indicateurs_boutique(D, annee=2025):
    """Les indicateurs de la boutique, calculés comme le fichier `benchmark_secteur.csv` les nomme. Retourne un DataFrame (indicateur, valeur, sens) ;
    `sens` vaut +1 si une valeur plus haute est meilleure, −1 si plus basse est meilleure, 0 si le sens dépend de la stratégie. Le désabonnement e-mail n'est pas mesurable avec ces données."""
    import os
    lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
    cmd, lg, prod, ret, cli = charger(D)
    a = lg[lg["annee"] == annee]
    ca = a["montant"].sum()
    sess, cr, bil, liv, stk = lire("sessions_web.csv"), lire("compte_resultat_mensuel.csv"), lire("bilan_annuel.csv"), lire("livraisons.csv"), lire("stock_quotidien.csv")
    cr = cr[cr["mois"].str[:4] == str(annee)]
    nouveaux = int((pd.to_datetime(cli["date_inscription"]).dt.year == annee).sum())
    c_an = cmd[cmd["annee"] == annee]
    livr = liv[liv["date_commande"].str[:4] == str(annee)]
    v = [("Taux de marge brute (HT)", a["marge"].sum() / (ca / 1.2) * 100, 1),
         ("Taux de retour (lignes)", a["retournee"].mean() * 100, -1),
         ("Panier moyen", ca / len(c_an), 1),
         ("Taux de conversion du site", sess["commande"].mean() * 100 if annee == 2025 else np.nan, 1),
         ("Part du site dans le CA", a.loc[a["canal"] == "Site", "montant"].sum() / ca * 100, 0),
         ("Rotation du stock (par an)", cr["achats"].sum() / bil.loc[bil["annee"] == annee, "stock"].iloc[0], 1),
         ("Taux de rupture de stock", stk["rupture"].mean() * 100 if annee == 2025 else np.nan, -1),
         ("Livraisons à l'heure", (1 - livr["retard"].mean()) * 100, 1),
         ("Coût d'acquisition d'un client", cr["marketing"].sum() / nouveaux, -1),
         ("Clients actifs à 12 mois", c_an["id_client"].nunique() / len(cli) * 100, 1),
         ("Part des frais de personnel dans le CA", cr["frais_personnel"].sum() / cr["ca_ht"].sum() * 100, -1)]
    return pd.DataFrame(v, columns=["indicateur", "valeur", "sens"])


def positionner(ind, sect):
    """Compare chaque indicateur de la boutique à la médiane et aux quartiles du secteur : position, écart standardisé robuste (écart à la médiane
    divisé par l'écart interquartile / 1,349) et verdict tenant compte du sens (favorable, défavorable, neutre)."""
    d = ind.merge(sect, on="indicateur")
    d["ecart_std"] = (d["valeur"] - d["mediane_secteur"]) / ((d["quartile_3"] - d["quartile_1"]) / 1.349)
    d["position"] = np.where(d["valeur"] < d["quartile_1"], "sous le 1er quartile", np.where(d["valeur"] > d["quartile_3"], "au-dessus du 3e quartile", "dans l'intervalle interquartile"))
    ok = (np.sign(d["ecart_std"]) * d["sens"]).where(d["sens"] != 0, 0)
    d["verdict"] = np.where(d["sens"] == 0, "neutre", np.where(d["ecart_std"].abs() < 0.25, "proche de la médiane", np.where(ok > 0, "favorable", "défavorable")))
    return d


def figure_positionnement(nom, d):
    """Positionnement : pour chaque indicateur, bande interquartile du secteur ramenée à [0, 1] et valeur de la boutique (point)."""
    import matplotlib.pyplot as plt
    from style import setup, save, BLEU, ORANGE, AQUA, MUET, ROUGE
    setup()
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    n = len(d)
    for i, r in enumerate(d.itertuples()):
        y = n - i
        etendue = r.quartile_3 - r.quartile_1
        x = (r.valeur - r.quartile_1) / etendue
        ax.barh(y, 1, left=0, height=0.5, color="#dde7f5", zorder=1)
        ax.plot([(r.mediane_secteur - r.quartile_1) / etendue] * 2, [y - 0.25, y + 0.25], color=MUET, lw=1.4, zorder=2)
        couleur = {"favorable": AQUA, "défavorable": ROUGE}.get(r.verdict, ORANGE if r.verdict == "neutre" else BLEU)
        ax.scatter([max(min(x, 2.6), -1.6)], [y], color=couleur, s=42, zorder=3)
    ax.set_yticks(range(n, 0, -1)); ax.set_yticklabels(d["indicateur"], fontsize=8)
    ax.set_xlim(-1.8, 2.8); ax.set_xticks([0, 1]); ax.set_xticklabels(["1er quartile\ndu secteur", "3e quartile\ndu secteur"], fontsize=8)
    ax.grid(False); ax.axvline(0, color=MUET, lw=0.5); ax.axvline(1, color=MUET, lw=0.5)
    ax.set_title("La boutique par rapport au secteur (données fictives)", loc="left")
    save(fig, nom)


def gini(valeurs):
    """Coefficient de Gini (0 = répartition égale, proche de 1 = tout chez un seul élément) d'une série de valeurs positives."""
    x = np.sort(np.asarray(valeurs, float))
    n = len(x)
    return float(2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum()) - (n + 1) / n)
