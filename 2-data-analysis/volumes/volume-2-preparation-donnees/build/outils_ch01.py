"""Outils du chapitre 1 (nettoyage des données) — série 2, volume II. Partagé par le livre (blocs cachés : figures) et le cahier.

Contenu : lecture robuste des fichiers de caisse (`lire_caisse`), conversion de nombres écrits en texte (`nombre`), normalisation des noms de ville
(`normaliser_ville`), lecture d'une date de naissance à formats mixtes (`date_mixte`), et les figures du chapitre.
"""
import io
import os
import re
import unicodedata

import numpy as np
import pandas as pd

D = os.environ.get("DONNEES", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees"))


def chemin(nom):
    return os.path.join(D, nom)


# ------------------------------------------------------------------------------------------------ lecture
def lire_caisse(fichier):
    """Lit un export de caisse mensuel, quel que soit son format. Retourne (tableau typé, total affiché, description)."""
    brut = open(fichier, "rb").read()
    try:
        texte, enc = brut.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        texte, enc = brut.decode("cp1252"), "cp1252"
    lignes = texte.splitlines()
    est_entete = lambda l: re.match(r'^"?(N° ticket|Ticket)', l) is not None
    i0 = next(i for i, l in enumerate(lignes) if est_entete(l))
    sep = ";" if lignes[i0].count(";") > lignes[i0].count(",") else ","
    total = float(lignes[-1].split(sep)[-1].strip('"').replace(",", "."))
    corps = [l for l in lignes[i0 + 1:-1] if not est_entete(l)]
    t = pd.read_csv(io.StringIO("\n".join([lignes[i0]] + corps)), sep=sep, dtype=str)
    t.columns = [c.replace("N° ticket", "ticket").replace("Ticket", "ticket").replace("Quantité", "Qté") for c in t.columns]
    t = t.rename(columns={"ticket": "ticket", "Date": "date", "Heure": "heure", "Article": "article", "Catégorie": "categorie", "Qté": "quantite",
                          "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"})
    for c in ("prix_unitaire", "montant"):
        t[c] = pd.to_numeric(t[c].str.replace(",", "."), errors="coerce")
    t["quantite"] = t["quantite"].astype(int)
    fmt = "%d/%m/%y" if re.fullmatch(r"\d\d/\d\d/\d\d", t["date"].iloc[0]) else "%d/%m/%Y"
    t["date"] = pd.to_datetime(t["date"], format=fmt)
    t["id_commande"] = t["ticket"].str[1:].astype(int)
    return t, total, f"{enc}, séparateur « {sep} »"


def nombre(texte):
    """« 1 245,00 € » -> 1245.0 ; « 45.9 » -> 45.9"""
    s = str(texte).replace("€", "").replace(" ", "").replace(" ", "").strip().replace(",", ".")
    return float(s)


def normaliser_ville(s):
    """« VILLE A », « Vile A », « Ville A. », « ville a » -> « Ville A » ; l'arabe « المدينة أ » est traité à part."""
    s = str(s).strip().rstrip(".")
    m = re.fullmatch(r"(?i)vil{1,2}e\s+([a-t])", s)
    return f"Ville {m.group(1).upper()}" if m else s


AR = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف"]
MOIS = {m: i + 1 for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"])}


def date_mixte(s, americain=False):
    """Lit « 03/11/1966 », « 1966-11-03 », « 3 novembre 1966 ». Si americain=True, les dates avec « / » sont lues mm/jj/aaaa."""
    s = str(s).strip()
    try:
        if re.fullmatch(r"\d{4}-\d\d-\d\d", s):
            return pd.Timestamp(s)
        m = re.fullmatch(r"(\d{1,2}) (\w+) (\d{4})", s)
        if m:
            return pd.Timestamp(int(m.group(3)), MOIS[m.group(2)], int(m.group(1)))
        m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})", s)
        if m:
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return pd.Timestamp(y, a, b) if americain else pd.Timestamp(y, b, a)
    except (ValueError, KeyError):
        return pd.NaT
    return pd.NaT


# ------------------------------------------------------------------------------------------------ figures
def _style():
    import style
    style.setup()
    return style


def fig_manquants(profil, png):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.2), gridspec_kw={"width_ratios": [1, 1.25]})
    cols = ["revenu_annuel", "depense_2025", "satisfaction_moy"]
    pc = profil[cols].isna().mean() * 100
    ax[0].barh(cols, pc.values, color=st.BLEU)
    for i, v in enumerate(pc.values):
        ax[0].text(v + 0.4, i, f"{v:.1f} %".replace(".", ","), va="center", fontsize=9)
    ax[0].set_xlim(0, 22); ax[0].invert_yaxis(); ax[0].set_xlabel("Part de valeurs manquantes (%)")
    ax[0].set_title("Par colonne", loc="left")
    motif = profil[cols].isna()
    noms = {(0, 0, 0): "aucun manquant", (1, 0, 0): "revenu seul", (0, 0, 1): "satisfaction seule", (0, 1, 0): "dépense seule", (1, 0, 1): "revenu + satisfaction",
            (1, 1, 0): "revenu + dépense"}
    cnt = motif.astype(int).apply(tuple, axis=1).value_counts()
    lab, val = [], []
    for k, n in cnt.items():
        lab.append(noms.get(k, "autres")); val.append(n)
    s = pd.Series(val, index=lab).groupby(level=0, sort=False).sum().sort_values(ascending=True)
    ax[1].barh(s.index, s.values, color=[st.MUET if i == "aucun manquant" else st.ORANGE for i in s.index])
    for i, v in enumerate(s.values):
        ax[1].text(v + 40, i, f"{int(v):,}".replace(",", " "), va="center", fontsize=9)
    ax[1].set_xlim(0, 5200); ax[1].set_xlabel("Nombre de clients"); ax[1].set_title("Par combinaison de colonnes manquantes", loc="left")
    fig.tight_layout(); fig.savefig(png, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_mecanismes(profil, verite, png):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.1), sharey=True)
    can = profil.groupby("canal_acquisition")["depense_2025"].apply(lambda s: s.isna().mean() * 100)
    ax[0].bar(can.index, can.values, color=st.BLEU); ax[0].set_title("Dépense selon le canal\n(au hasard)", loc="left", fontsize=10)
    cl = pd.cut(profil["age"], [0, 29, 44, 59, 200], labels=["< 30", "30-44", "45-59", "60+"])
    ra = profil.groupby(cl, observed=True)["revenu_annuel"].apply(lambda s: s.isna().mean() * 100)
    ax[1].bar(ra.index.astype(str), ra.values, color=st.ORANGE); ax[1].set_title("Revenu selon l'âge\n(dépend d'une variable connue)", loc="left", fontsize=10)
    b = pd.cut(verite["satisfaction_moy"], [0, 2.5, 3.5, 4.5, 5.01], labels=["≤ 2,5", "2,5-3,5", "3,5-4,5", "> 4,5"])
    rs = profil["satisfaction_moy"].isna().groupby(b, observed=True).mean() * 100
    ax[2].bar(rs.index.astype(str), rs.values, color=st.ROUGE); ax[2].set_title("Satisfaction selon sa vraie valeur\n(dépend de la valeur manquante)", loc="left", fontsize=10)
    for a in ax:
        for p in a.patches:
            a.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.8, f"{p.get_height():.0f} %", ha="center", fontsize=9)
    ax[0].set_ylabel("Part de manquants (%)"); ax[0].set_ylim(0, 48)
    fig.tight_layout(); fig.savefig(png, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_aberrantes(m, png):
    """m : montants saisis avec colonnes quantite, prix_unitaire, montant, anomalie (vide si aucune)."""
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    att = m["quantite"] * m["prix_unitaire"]
    bon = m["anomalie"].isna()
    ax.scatter(att[bon], m.loc[bon, "montant"], s=6, color=st.MUET, alpha=0.5, label="montants corrects")
    coul = {"decimale_x10": st.ORANGE, "decimale_x100": st.ROUGE, "signe_inverse": st.VIOLET, "zero": st.AQUA, "placeholder_9999": st.BLEU}
    noms = {"decimale_x10": "décimale ×10", "decimale_x100": "décimale ×100", "signe_inverse": "signe inversé", "zero": "zéro", "placeholder_9999": "9999"}
    for k, c in coul.items():
        s = m["anomalie"] == k
        ax.scatter(att[s], m.loc[s, "montant"], s=22, color=c, label=noms[k], edgecolor="white", linewidth=0.4)
    xs = np.linspace(att.min(), att.max(), 50)
    ax.fill_between(xs, 0.8 * xs, xs, color=st.BLEU, alpha=0.10, label="montant plausible : de 80 % à 100 % de qté × prix")
    ax.set_xscale("log"); ax.set_yscale("symlog", linthresh=10)
    ax.set_xlabel("Quantité × prix unitaire (€)"); ax.set_ylabel("Montant saisi (€)")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    fig.tight_layout(); fig.savefig(png, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_unite(site, png):
    """site : DataFrame avec 'mois' (période) et 'total_brut' (nombre lu tel quel) et 'total_corrige'."""
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    g = site.groupby("mois")[["total_brut", "total_corrige"]].median()
    x = np.arange(len(g)); lab = [str(p)[5:] for p in g.index]
    ax.plot(x, g["total_brut"], marker="o", color=st.ROUGE, label="montant lu tel quel")
    ax.plot(x, g["total_corrige"], marker="o", color=st.BLEU, label="après correction (centimes -> euros)")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(lab)
    ax.set_xlabel("Mois de 2025"); ax.set_ylabel("Montant médian d'une commande (€, échelle log)")
    ax.axvline(7.5, color=st.MUET, lw=0.8, ls="--"); ax.text(7.6, 2000, "15 septembre :\nchangement d'unité", fontsize=8, color=st.ENCRE2)
    ax.legend(frameon=False, fontsize=8, loc="center left")
    fig.tight_layout(); fig.savefig(png, dpi=200, bbox_inches="tight"); plt.close(fig)


def fig_imputation(vrai, mean_imp, reg_imp, png):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.9), sharex=True, sharey=True)
    bins = np.linspace(0, 70000, 36)
    for a, (s, titre, c) in zip(ax, [(vrai, "Vérité (jamais connue)", st.MUET), (mean_imp, "Imputation par la moyenne", st.ORANGE), (reg_imp, "Imputation par régression", st.BLEU)]):
        a.hist(s, bins=bins, color=c)
        a.set_title(f"{titre}\nécart-type : {s.std():,.0f} €".replace(",", " "), loc="left", fontsize=9.5)
        a.set_xlabel("Revenu annuel (€)")
    ax[0].set_ylabel("Nombre de clients")
    fig.tight_layout(); fig.savefig(png, dpi=200, bbox_inches="tight"); plt.close(fig)
