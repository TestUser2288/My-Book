"""Outils du chapitre 3 (qualité des données et réconciliation) — volume II de la série 2.

Fonctions partagées par le livre (blocs cachés) et le cahier : lecture robuste des fichiers de caisse (dérive de schéma), lecture des montants du site,
petits contrôles, figure en cascade (« waterfall »). Aucune dépendance vers un autre chapitre.
"""
import csv
import io
import os
import re
import unicodedata

import numpy as np
import pandas as pd

DONNEES = os.environ.get("DONNEES", "donnees")


# ------------------------------------------------------------------------------------------------ lecture
def lire_texte(chemin):
    """lit un fichier texte en essayant UTF-8 (avec ou sans BOM) puis cp1252 ; retourne (texte, encodage)"""
    brut = open(chemin, "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return brut.decode(enc), enc
        except UnicodeDecodeError:
            continue
    raise ValueError("encodage inconnu")


def lire_caisse_fichier(chemin):
    """Lit UN fichier de caisse, quel que soit son format (séparateur, encodage, décimale, date, colonnes) ; retourne (lignes, total_affiche, meta).
    `lignes` : DataFrame typé ; `total_affiche` : le total imprimé en bas du fichier ; `meta` : dict (encodage, séparateur, décimale, colonnes)."""
    texte, enc = lire_texte(chemin)
    lignes = texte.splitlines()
    i0 = next(i for i, l in enumerate(lignes) if l.startswith(("N° ticket", "Ticket")))
    sep = ";" if lignes[i0].count(";") > lignes[i0].count(",") else ","
    lecteur = list(csv.reader(lignes[i0:], delimiter=sep))
    entete = lecteur[0]
    corps = [r for r in lecteur[1:] if r and r != entete]
    total = None
    if corps and "Total" in corps[-1]:
        total = corps.pop()
        total = float([x for x in total if x and x != "Total"][-1].replace(",", "."))
    df = pd.DataFrame(corps, columns=entete)
    df = df.rename(columns={"N° ticket": "ticket", "Ticket": "ticket", "Date": "date", "Heure": "heure", "Article": "article", "Catégorie": "categorie",
                            "Qté": "qte", "Quantité": "qte", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"})
    for c in ("prix_unitaire", "montant"):
        df[c] = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")
    df["qte"] = df["qte"].astype(int)
    if "remise_pct" in df:
        df["remise_pct"] = df["remise_pct"].astype(float)
    fmt = "%d/%m/%y" if df["date"].str.len().iloc[0] == 8 else "%d/%m/%Y"
    df["date"] = pd.to_datetime(df["date"], format=fmt)
    df["id_commande"] = df["ticket"].str[1:].astype(int)
    meta = {"encodage": enc, "separateur": sep, "decimale": "," if sep == ";" else ".", "colonnes": len(entete)}
    return df, total, meta


def lire_caisse(dossier=None):
    """Lit les 12 fichiers de l'année ; retourne (lignes de toute l'année avec colonne `fichier`, tableau des fichiers)"""
    dossier = dossier or os.path.join(DONNEES, "caisse")
    parts, infos = [], []
    for nom in sorted(os.listdir(dossier)):
        df, total, meta = lire_caisse_fichier(os.path.join(dossier, nom))
        df.insert(0, "fichier", nom)
        df["numero_ligne"] = np.arange(len(df))
        parts.append(df)
        infos.append({"fichier": nom, "lignes": len(df), "total_affiche": total, **meta})
    return pd.concat(parts, ignore_index=True), pd.DataFrame(infos)


def montant_site_en_nombre(texte):
    """« 1 245,00 € », « 45.9 », « 4590 » -> nombre (SANS deviner l'unité : le texte « 4590 » devient 4590.0)"""
    t = str(texte).replace("€", "").replace(" ", "").replace(" ", "").strip().replace(",", ".")
    return float(t)


# ------------------------------------------------------------------------------------------------ contrôles
def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def resume_controles(resultats, n):
    """`resultats` : dict nom -> masque booléen des lignes EN ÉCHEC ; retourne un tableau (nombre d'échecs, taux)"""
    t = pd.DataFrame({"controle": list(resultats), "echecs": [int(m.sum()) for m in resultats.values()]})
    t["taux_pct"] = (100 * t["echecs"] / n).round(1)
    return t


# ------------------------------------------------------------------------------------------------ figure en cascade
def cascade(ax, etapes, couleur_pos="#1baf7a", couleur_neg="#e34948", couleur_tot="#2a78d6", fmt=lambda v: f"{v:,.0f}".replace(",", " ")):
    """Dessine une cascade. `etapes` : liste de (libellé, valeur, type) avec type 'total' (barre pleine depuis 0) ou 'delta' (variation)."""
    cum = 0.0
    xs = range(len(etapes))
    for i, (lib, v, typ) in enumerate(etapes):
        if typ == "total":
            ax.bar(i, v, color=couleur_tot, width=0.6)
            cum = v
            ax.text(i, v, fmt(v), ha="center", va="bottom", fontsize=8)
        else:
            bas = min(cum, cum + v)
            ax.bar(i, abs(v), bottom=bas, color=couleur_pos if v >= 0 else couleur_neg, width=0.6)
            ax.text(i, max(cum, cum + v), ("+" if v >= 0 else "−") + fmt(abs(v)), ha="center", va="bottom", fontsize=8)
            cum += v
    ax.set_xticks(list(xs))
    ax.set_xticklabels([e[0] for e in etapes], fontsize=8)
    return ax


# ------------------------------------------------------------------------------------------------ contrôles du CRM
RE_EMAIL = r"[^@\s.]+(\.[^@\s.]+)*@[^@\s.]+(\.[^@\s.]+)+"
RE_CP = r"\d{5}"
MOIS = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}
AR_LETTRES = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف"]
VILLES = [f"Ville {chr(65 + i)}" for i in range(20)]


def parse_naissance(s):
    """Dates de naissance de formats mêlés -> Timestamp ou NaT. Lecture JOUR D'ABORD pour jj/mm/aaaa (le format américain mm/jj/aaaa n'est pas détectable en général)."""
    s = pd.Series(s, dtype="string")
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[us]")
    iso = s.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)
    out[iso] = pd.to_datetime(s[iso], format="%Y-%m-%d", errors="coerce")
    fr = s.str.fullmatch(r"\d{2}/\d{2}/\d{4}", na=False)
    out[fr] = pd.to_datetime(s[fr], format="%d/%m/%Y", errors="coerce")
    txt = s.str.extract(r"^(\d{1,2}) ([a-zéûô]+) (\d{4})$")
    ok = txt[0].notna() & txt[1].isin(MOIS.keys())
    if ok.any():
        out[ok] = pd.to_datetime(dict(year=txt.loc[ok, 2].astype(int), month=txt.loc[ok, 1].map(MOIS).astype(int), day=txt.loc[ok, 0].astype(int)), errors="coerce")
    return out


def telephone_normalise(s):
    """chiffres seuls ; +99 devient 0 ; retourne None si la forme n'est pas celle d'un numéro à 10 chiffres"""
    d = s.str.replace(r"\D", "", regex=True)
    d = d.where(~d.str.startswith("99") | (d.str.len() != 11), "0" + d.str[2:])
    return d.where(d.str.fullmatch(r"0\d{9}", na=False))


def canonique_ville(s):
    """« VILLE A », « ville a. », « Ville A » -> « Ville A » ; les fautes (« Vile A ») et l'arabe restent NON reconnus (None)"""
    t = s.str.lower().str.replace(".", "", regex=False).str.strip()
    m = t.str.extract(r"^ville ([a-t])$")[0]
    return ("Ville " + m.str.upper()).where(m.notna())


def consentement_normalise(s):
    t = s.str.strip().str.lower()
    oui = t.isin(["oui", "o", "1", "true"])
    return pd.Series(np.where(oui, "oui", np.where(t == "non", "non", None)), index=s.index, dtype="object")


# ------------------------------------------------------------------------------------------------ tableau de bord de qualité
def cle_ligne(df, col_art, col_prix="prix_unitaire", col_qte="qte"):
    """clé de rapprochement ligne à ligne : ticket, article (minuscules), quantité, prix, rang (pour départager des lignes identiques)"""
    d = pd.DataFrame({"id_commande": df["id_commande"].values, "art": df[col_art].str.lower().values, "qte": df[col_qte].values, "prix_unitaire": df[col_prix].values})
    d["rang"] = d.groupby(["id_commande", "art", "qte", "prix_unitaire"]).cumcount()
    return d


def rapprocher_caisse_base(caisse, cmd, lig, prod):
    """Rapproche chaque ligne de la caisse d'une ligne de la base (canal Boutique, 2025) par la clé ticket + article + quantité + prix + rang.
    Retourne le résultat de la fusion externe avec la colonne `_merge` (both / left_only = en caisse seulement / right_only = en base seulement)."""
    b = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande").merge(prod[["id_produit", "nom_produit"]], on="id_produit")
    b = b[(b["canal"] == "Boutique") & (b["date_commande"] >= "2025-01-01")].rename(columns={"quantite": "qte"})
    kc, kb = cle_ligne(caisse, "article"), cle_ligne(b, "nom_produit")
    c2 = pd.concat([caisse.reset_index(drop=True), kc[["art", "rang"]]], axis=1)
    b2 = pd.concat([b.reset_index(drop=True)[["id_ligne", "montant", "remise_pct"]], kb], axis=1)
    cles = ["id_commande", "art", "qte", "prix_unitaire", "rang"]
    return c2.merge(b2, on=cles, how="outer", suffixes=("", "_base"), indicator=True)


def indicateurs_qualite(crm, site, site_l, caisse, fichiers, cmd, lig, prod, ref):
    """Tableau (source, dimension, indicateur, valeur) : valeur = pourcentage de conformité, sauf pour l'actualité (retard en jours)."""
    L = []

    def ajoute(src, dim, ind, v):
        L.append((src, dim, ind, float(v)))

    # --- CRM
    nn = crm["email"].ne("test@example.com")
    ajoute("CRM", "Complétude", "e-mail renseigné", 100 * crm["email"].notna().mean())
    ajoute("CRM", "Complétude", "code postal renseigné", 100 * crm["code_postal"].notna().mean())
    ajoute("CRM", "Complétude", "consentement renseigné", 100 * crm["consentement_marketing"].notna().mean())
    ajoute("CRM", "Validité", "e-mail bien formé", 100 * (1 - (crm["email"].notna() & ~crm["email"].str.fullmatch(RE_EMAIL, na=False)).sum() / crm["email"].notna().sum()))
    ajoute("CRM", "Validité", "code postal à 5 chiffres", 100 * (1 - (crm["code_postal"].notna() & ~crm["code_postal"].str.fullmatch(RE_CP, na=False)).sum() / crm["code_postal"].notna().sum()))
    nais = parse_naissance(crm["date_naissance"])
    ajoute("CRM", "Validité", "date de naissance plausible", 100 * ((nais.dt.year >= 1925) & (nais <= pd.Timestamp("2009-12-31"))).mean())
    ajoute("CRM", "Validité", "ville reconnue", 100 * canonique_ville(crm["ville"]).notna().mean())
    ajoute("CRM", "Validité", "pas une ligne de test", 100 * nn.mean())
    cle = crm["email"].str.strip().str.lower()
    dup = cle.notna() & nn & cle.duplicated(keep="first")
    ajoute("CRM", "Unicité", "ligne non redondante (même e-mail)", 100 * (1 - dup.sum() / nn.sum()))
    insc = pd.to_datetime(crm["date_inscription"], format="%d/%m/%Y")
    age_insc = (insc - nais).dt.days / 365.25
    ok_age = age_insc.dropna()
    ajoute("CRM", "Cohérence", "âgé d'au moins 16 ans à l'inscription", 100 * (ok_age >= 16).mean())
    vc = canonique_ville(crm["ville"])
    cp_ok = crm["code_postal"].where(crm["code_postal"].str.fullmatch(RE_CP, na=False))
    mode = cp_ok.groupby(vc).agg(lambda s: s.mode().iloc[0] if s.notna().any() else None)
    dd = pd.DataFrame({"v": vc, "cp": crm["code_postal"]}).dropna()
    ajoute("CRM", "Cohérence", "code postal conforme à la ville", 100 * (dd["cp"] == dd["v"].map(mode)).mean())
    ajoute("CRM", "Actualité", "retard de la dernière inscription (jours)", (ref - insc.max()).days)
    # --- Site
    ajoute("Site", "Complétude", "champs obligatoires renseignés", 100 * site[["order_ref", "created_at", "status", "customer_email", "total"]].notna().all(axis=1).mean())
    ajoute("Site", "Validité", "statut en minuscules (liste stricte)", 100 * site["status"].isin(["paid", "cancelled"]).mean())
    ajoute("Site", "Validité", "devise = EUR", 100 * site["currency"].eq("EUR").mean())
    ajoute("Site", "Validité", "pas une commande de test", 100 * site["customer_email"].ne("test@example.com").mean())
    ajoute("Site", "Unicité", "numéro de commande unique", 100 * (1 - site["order_ref"].duplicated().sum() / len(site)))
    t = site["total"].map(montant_site_en_nombre)
    somme = site_l.assign(m=site_l["qty"] * site_l["unit_price"] * (1 - site_l["discount_pct"] / 100)).groupby("order_ref")["m"].sum()
    ecart = (t - site["order_ref"].map(somme)).abs()
    ajoute("Site", "Cohérence", "total d'en-tête = somme des lignes (lecture brute)", 100 * (ecart.dropna() <= 0.05).mean())
    tot_base = lig.groupby("id_commande")["montant"].sum()
    idc = site["order_ref"].str.extract(r"WEB-(\d{6})")[0].astype(float)
    vrai = idc.map(tot_base)
    ajoute("Site", "Exactitude", "total conforme à la base (lecture brute)", 100 * ((t - vrai).abs().dropna() <= 0.01).mean())
    ajoute("Site", "Actualité", "retard de la dernière commande (jours)", (ref - pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="ISO8601").max().normalize()).days)
    # --- Caisse
    ajoute("Caisse", "Complétude", "montant renseigné", 100 * caisse["montant"].notna().mean())
    dupl = caisse.duplicated(subset=["fichier", "ticket", "date", "heure", "article", "qte", "prix_unitaire", "montant"], keep="first")
    ajoute("Caisse", "Unicité", "ligne non doublée (copie exacte)", 100 * (1 - dupl.mean()))
    ajoute("Caisse", "Cohérence", "fichiers au format du premier fichier", 100 * (fichiers[["encodage", "separateur", "decimale", "colonnes"]].eq(fichiers.iloc[0][["encodage", "separateur", "decimale", "colonnes"]]).all(axis=1)).mean())
    lu = caisse.groupby("fichier")["montant"].sum()
    aff = fichiers.set_index("fichier")["total_affiche"]
    ajoute("Caisse", "Cohérence", "mois dont le total de contrôle est respecté (±0,5 %)", 100 * ((lu - aff).abs() / aff <= 0.005).mean())
    r = rapprocher_caisse_base(caisse, cmd, lig, prod)
    ajoute("Caisse", "Exactitude", "ligne retrouvée dans la base", 100 * (r["_merge"] == "both").sum() / (r["_merge"] != "right_only").sum())
    ajoute("Caisse", "Actualité", "retard de la dernière vente (jours)", (ref - caisse["date"].max()).days)
    return pd.DataFrame(L, columns=["source", "dimension", "indicateur", "valeur"])


# ------------------------------------------------------------------------------------------------ cadres de validation
import contextlib


@contextlib.contextmanager
def silencieux():
    """masque la sortie d'erreur (barres de progression de Great Expectations) pendant un bloc"""
    import contextlib
    with contextlib.redirect_stderr(io.StringIO()):
        yield


def generer_data_docs(df, png, largeur=1200, hauteur=780):
    """Valide `df` (CRM) avec Great Expectations dans un projet temporaire, construit les Data Docs et photographie la page du résultat de validation
    avec Chromium sans interface. Capture RÉELLE d'un logiciel libre exécuté ici ; lancée seulement si la variable REGENERER_CAPTURES est posée."""
    import shutil
    import tempfile
    import warnings
    warnings.filterwarnings("ignore")
    import great_expectations as gx
    from great_expectations.checkpoint import UpdateDataDocsAction
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix="gx_", dir=os.environ.get("TMPDIR"))
    try:
        with silencieux():
            ctx = gx.get_context(mode="file", project_root_dir=tmp)
            bd = ctx.data_sources.add_pandas("boutique").add_dataframe_asset("crm").add_batch_definition_whole_dataframe("tout")
            E = gx.expectations
            suite = ctx.suites.add(gx.ExpectationSuite(name="crm"))
            for e in [E.ExpectColumnValuesToNotBeNull(column="email", mostly=0.95), E.ExpectColumnValuesToMatchRegex(column="code_postal", regex=r"^\d{5}$", mostly=0.99),
                      E.ExpectColumnValuesToBeInSet(column="consentement_marketing", value_set=["oui", "non"], mostly=0.9), E.ExpectColumnValuesToBeUnique(column="id_crm")]:
                suite.add_expectation(e)
            vd = ctx.validation_definitions.add(gx.ValidationDefinition(name="crm_def", data=bd, suite=suite))
            cp = ctx.checkpoints.add(gx.Checkpoint(name="cp", validation_definitions=[vd], actions=[UpdateDataDocsAction(name="docs")]))
            cp.run(batch_parameters={"dataframe": df})
        page = [os.path.join(r, x) for r, d, f in os.walk(tmp) for x in f if x == "boutique-crm.html" or (x.endswith(".html") and "validations" in r)][0]
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
        with sync_playwright() as p:
            nav = p.chromium.launch()
            pg = nav.new_page(viewport={"width": largeur, "height": hauteur + 120}, device_scale_factor=2)
            pg.goto("file://" + page)
            pg.add_style_tag(content="img{display:none !important}")
            pg.wait_for_timeout(400)
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": largeur, "height": hauteur})
            nav.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return png
