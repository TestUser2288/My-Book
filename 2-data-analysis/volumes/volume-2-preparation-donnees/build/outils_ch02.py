"""Outils du chapitre 2 (série 2, volume II) : lire et harmoniser les sources désordonnées de la boutique, puis les empiler.

Le LIVRE montre ces étapes pas à pas dans de petits blocs ; ce module les regroupe pour que le CAHIER (et les sections qui repartent d'une table déjà
construite) n'aient pas à les réécrire. Rien ici ne lit les fichiers `verite_*` : la vérité sert seulement à juger, dans le texte.

    import sys; sys.path.insert(0, "build")
    import outils_ch02 as O
"""
import glob
import io
import os
import re
import unicodedata

import numpy as np
import pandas as pd

DONNEES = os.environ.get("DONNEES", "donnees")
TVA = 0.20            # taux de TVA fictif, pour l'illustration
HAUSSE_2025 = 1.03    # hausse de prix de la boutique au 1er janvier 2025


def NUM(cle, val):
    """imprime « NUM clé valeur » : les nombres cités dans la prose sont lus dans ces lignes par le gabarit (build/gabarits/ch02)"""
    print(f"NUM {cle} {val}")


# ------------------------------------------------------------------------------------------------ texte
def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def norm_texte(s):
    """minuscules, sans accents, ponctuation remplacée par des espaces, espaces simplifiés"""
    s = sans_accents(s).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9@ ]", " ", s)).strip()


# ------------------------------------------------------------------------------------------------ caisse
RENOMMAGE_CAISSE = {"N° ticket": "ticket", "Ticket": "ticket", "Date": "date", "Heure": "heure", "Article": "article", "Catégorie": "categorie",
                    "Qté": "quantite", "Quantité": "quantite", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}


def lire_caisse_fichier(chemin):
    """lit un export de caisse, quel que soit son format (encodage, séparateur, décimale, noms de colonnes, format de date) ;
    retourne (DataFrame harmonisé, total affiché en pied de fichier)"""
    brut = open(chemin, "rb").read()
    try:
        texte, enc = brut.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        texte, enc = brut.decode("cp1252"), "cp1252"
    lignes = texte.splitlines()
    sep = ";" if lignes[3].count(";") > lignes[3].count(",") else ","
    dec = "," if sep == ";" else "."
    total = float(lignes[-1].split(sep)[-1].replace(dec, "."))
    df = pd.read_csv(io.StringIO("\n".join(lignes[3:-1])), sep=sep, dtype=str, keep_default_na=False).rename(columns=RENOMMAGE_CAISSE)
    df = df[~df["ticket"].isin(["N° ticket", "Ticket"])].copy()          # en-têtes répétés à chaque « page »
    for c in ["prix_unitaire", "montant"] + (["remise_pct"] if "remise_pct" in df else []):
        df[c] = pd.to_numeric(df[c].str.replace(dec, "."), errors="coerce")
    df["quantite"] = df["quantite"].astype(int)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y" if len(df["date"].iloc[0]) == 10 else "%d/%m/%y")
    df["fichier"] = os.path.basename(chemin)
    df["rang"] = np.arange(len(df))
    df["id_commande"] = df["ticket"].str.lstrip("T").astype(int)
    if "remise_pct" not in df:
        df["remise_pct"] = np.nan
    return df, total


def charger_caisse(dossier=None):
    """empile les 12 fichiers ; retourne (table, tableau de contrôle par fichier)"""
    dossier = dossier or os.path.join(DONNEES, "caisse")
    morceaux, ctrl = [], []
    for f in sorted(glob.glob(os.path.join(dossier, "caisse_2025-*.csv"))):
        df, total = lire_caisse_fichier(f)
        morceaux.append(df)
        ctrl.append((os.path.basename(f), len(df), total, round(df["montant"].sum(), 2), int(df["montant"].isna().sum())))
    ctrl = pd.DataFrame(ctrl, columns=["fichier", "lignes", "total_affiche", "somme_lue", "montants_vides"])
    ctrl["ecart"] = (ctrl["total_affiche"] - ctrl["somme_lue"]).round(2)
    return pd.concat(morceaux, ignore_index=True), ctrl


# ------------------------------------------------------------------------------------------------ site
def montant_site(texte, en_centimes):
    s = texte.replace("€", "").strip()
    if en_centimes:
        return int(s) / 100
    return float(s.replace(" ", "").replace(",", "."))


def lire_site(dossier=None):
    """retourne (commandes brutes typées, lignes) du site ; ne supprime rien : les doublons, tests et annulations sont signalés par des colonnes"""
    dossier = dossier or DONNEES
    so = pd.read_csv(os.path.join(dossier, "site_commandes.csv"), dtype=str, keep_default_na=False)
    sl = pd.read_csv(os.path.join(dossier, "site_lignes.csv"))
    so["en_utc"] = so["created_at"].str.endswith("Z")
    so["date_heure"] = pd.to_datetime(so["created_at"].str.replace("Z", "", regex=False), format="ISO8601")
    so["email_norm"] = so["customer_email"].str.strip().str.lower()
    so["est_test"] = so["email_norm"] == "test@example.com"
    so["statut"] = so["status"].str.lower()
    so["est_double"] = so.duplicated("order_ref", keep="first")
    so["total_num"] = [np.nan if t else montant_site(m, u) for m, u, t in zip(so["total"], so["en_utc"], so["est_test"])]
    so["id_commande"] = pd.to_numeric(so["order_ref"].str[4:], errors="coerce")        # « WEB-023473 » -> 23473 ; les références de test donnent NaN
    return so, sl


# ------------------------------------------------------------------------------------------------ catalogue et ventes
def charger_produits(dossier=None):
    p = pd.read_csv(os.path.join(dossier or DONNEES, "produits.csv"))
    p["nom_norm"] = p["nom_produit"].map(norm_texte)
    p["prix_2025"] = (p["prix_vente"] * HAUSSE_2025).round(2)
    return p


def apparier_produit_caisse(caisse, produits):
    """retrouve id_produit pour les lignes de caisse (nom + prix de 2025 ; deux produits portent le même nom) ;
    retourne caisse avec id_produit (NaN si ambigu), produit_ambigu, cout_achat (moyenne des candidats si ambigu)"""
    c = caisse.reset_index(drop=True).copy()
    c["nom_norm"] = c["article"].map(norm_texte)
    cand = c[["nom_norm", "prix_unitaire"]].reset_index().merge(produits[["id_produit", "nom_norm", "prix_2025", "cout_achat"]], on="nom_norm")
    cand = cand[(cand["prix_unitaire"] - cand["prix_2025"]).abs() < 0.011]
    g = cand.groupby("index").agg(n=("id_produit", "size"), id_produit=("id_produit", "first"), cout_achat=("cout_achat", "mean"))
    c["id_produit"] = g["id_produit"].where(g["n"] == 1)
    c["produit_ambigu"] = (g["n"] > 1).reindex(c.index, fill_value=False)
    c["cout_achat"] = g["cout_achat"].reindex(c.index)
    return c


def ventes_2025(dossier=None):
    """la table des ventes 2025 (caisse + site) au schéma commun, telle que le chapitre la construit pas à pas ;
    retourne (ventes, contrôle de la caisse)"""
    produits = charger_produits(dossier)
    caisse, ctrl = charger_caisse(os.path.join(dossier, "caisse") if dossier else None)
    caisse = apparier_produit_caisse(caisse, produits)
    caisse["montant_vide"] = caisse["montant"].isna()
    remise = caisse["remise_pct"].fillna(0)
    caisse["montant_corrige"] = caisse["montant"].fillna((caisse["quantite"] * caisse["prix_unitaire"] * (1 - remise / 100)).round(2))
    caisse["identique_precedente"] = caisse.duplicated(["ticket", "date", "heure", "article", "categorie", "quantite", "prix_unitaire", "montant"])
    ref_nom = produits.drop_duplicates("nom_norm").set_index("nom_norm")[["nom_produit", "categorie"]]
    v_caisse = caisse.drop(columns=["categorie"]).join(ref_nom, on="nom_norm")
    v_caisse = v_caisse.assign(source="caisse", canal="Boutique", montant=v_caisse["montant_corrige"], montant_reconstitue=v_caisse["montant_vide"])
    cmd, lignes = lire_site(dossier)
    ok = cmd[~cmd["est_test"] & ~cmd["est_double"] & (cmd["statut"] != "cancelled")]
    ls = lignes.merge(ok[["order_ref", "id_commande", "date_heure"]], on="order_ref", validate="m:1")
    ls["id_commande"] = ls["id_commande"].astype(int)
    ls = ls.assign(id_produit=ls["sku"].str[1:].astype(int), quantite=ls["qty"], prix_unitaire=ls["unit_price"], remise_pct=ls["discount_pct"])
    ls["montant"] = (ls["quantite"] * ls["prix_unitaire"] * (1 - ls["remise_pct"] / 100)).round(2)
    v_site = ls.merge(produits[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
    v_site = v_site.assign(source="site", canal="Site", date=v_site["date_heure"].dt.normalize(), montant_reconstitue=False, identique_precedente=False)
    cols = ["source", "canal", "id_commande", "date", "id_produit", "nom_produit", "categorie", "quantite", "prix_unitaire", "remise_pct", "montant",
            "cout_achat", "montant_reconstitue", "identique_precedente"]
    ventes = pd.concat([v_caisse[cols], v_site[cols]], ignore_index=True)
    ventes["marge_ht"] = ventes["montant"] / (1 + TVA) - ventes["quantite"] * ventes["cout_achat"]
    return ventes, ctrl


# ------------------------------------------------------------------------------------------------ CRM et catalogue (section 2.5)
LETTRES_AR = "أبتثجحخدذرزسشصضطظعغف"


def ville_cle(s):
    """clé de ville : « المدينة أ » -> « ville a » ; « Vile A. » -> « ville a »"""
    s = s.strip()
    if s.startswith("المدينة"):
        return "ville " + chr(97 + LETTRES_AR.index(s.split()[-1]))
    return re.sub(r"^vile", "ville", norm_texte(s))


def charger_crm(dossier=None):
    """le CRM sans les lignes de test, avec les champs normalisés ; retourne (crm, paires vraies d'après verite_crm.csv)"""
    import itertools
    import ftfy
    dossier = dossier or DONNEES
    crm = pd.read_csv(os.path.join(dossier, "crm_clients.csv"), dtype=str, keep_default_na=False)
    crm = crm[crm["email"] != "test@example.com"].copy()
    crm["id_crm"] = crm["id_crm"].astype(int)
    crm["mail_norm"] = crm["email"].str.strip().str.lower().replace("", np.nan)
    crm["tel_norm"] = crm["telephone"].str.replace(r"\D", "", regex=True).str[-9:]
    crm["nom_complet"] = (crm["prenom"] + " " + crm["nom"]).map(lambda s: norm_texte(ftfy.fix_text(s)))
    crm["nom_tri"] = crm["nom_complet"].str.split().map(lambda t: " ".join(sorted(t)))
    crm["ville_norm"] = crm["ville"].map(ville_cle)
    crm["annee_naiss"] = pd.to_numeric(crm["date_naissance"].str.extract(r"(\d{4})")[0]).where(lambda a: a.between(1920, 2010))
    verite = pd.read_csv(os.path.join(dossier, "verite_crm.csv"))
    groupes = crm.merge(verite[["id_crm", "id_client"]], on="id_crm").groupby("id_client")["id_crm"].apply(sorted)
    vraies = {p for g in groupes for p in itertools.combinations(g, 2)}
    return crm, vraies


def paires(df, cles, taille_max=100):
    """toutes les paires de lignes qui partagent la même valeur de clé (les groupes de `taille_max` lignes ou plus sont ignorés : trop gros pour être un blocage utile)"""
    import itertools
    sortie = set()
    for _, g in df.dropna(subset=cles).groupby(cles)["id_crm"]:
        ids = sorted(g)
        if 1 < len(ids) < taille_max:
            sortie.update(itertools.combinations(ids, 2))
    return sortie


def juger(trouvees, vraies):
    ok = len(trouvees & vraies)
    return {"paires": len(trouvees), "précision": round(ok / max(1, len(trouvees)), 3), "rappel": round(ok / len(vraies), 3)}


def scorer_paires(crm, bloc, vraies=None):
    """score de ressemblance (nom 60 %, partie locale de l'e-mail 40 % ; nom seul × 0,9 si un e-mail manque) pour chaque paire du blocage"""
    from rapidfuzz import fuzz
    rec = crm.set_index("id_crm")[["nom_tri", "mail_norm"]].to_dict("index")
    local = lambda m: m.split("@")[0] if isinstance(m, str) else None
    lignes = []
    for a, b in sorted(bloc):
        nom = fuzz.token_set_ratio(rec[a]["nom_tri"], rec[b]["nom_tri"])
        lx, ly = local(rec[a]["mail_norm"]), local(rec[b]["mail_norm"])
        if lx is None or ly is None:
            lignes.append((a, b, nom, np.nan, 0.9 * nom))
        else:
            mail = fuzz.ratio(lx, ly)
            lignes.append((a, b, nom, mail, 0.6 * nom + 0.4 * mail))
    S = pd.DataFrame(lignes, columns=["a", "b", "nom", "mail", "score"])
    if vraies is not None:
        S["vrai"] = [(a, b) in vraies for a, b in zip(S["a"], S["b"])]
    return S


def rapprocher_catalogue(seuil_nom=70, seuil_prix=0.035, dossier=None):
    """relie le catalogue du fournisseur aux produits (nom ressemblant dans la même famille, pénalisé par l'écart de prix d'achat) ;
    retourne une ligne par code fournisseur : produit choisi, similarité, écart de prix, décision, produit choisi par le nom seul"""
    from rapidfuzz import fuzz
    dossier = dossier or DONNEES
    cat = pd.read_csv(os.path.join(dossier, "catalogue_fournisseur.csv"))
    produits = pd.read_csv(os.path.join(dossier, "produits.csv"))
    cat["cle"] = cat["designation"].map(norm_texte); cat["fam"] = cat["famille"].map(norm_texte)
    produits["nom_cle"] = produits["nom_produit"].map(norm_texte); produits["fam"] = produits["categorie"].map(norm_texte)
    res = []
    for r in cat.itertuples():
        cand = produits[produits["fam"] == r.fam]
        nom = cand["nom_cle"].map(lambda x: max(fuzz.token_sort_ratio(r.cle, x), fuzz.ratio(r.cle, x)))
        ecart = (r.prix_achat_ht / cand["cout_achat"] - 1).abs()
        i = (nom - 100 * ecart).idxmax()
        res.append((r.code_fournisseur, cand.loc[i, "id_produit"], nom[i], ecart[i], cand.loc[nom.idxmax(), "id_produit"]))
    R = pd.DataFrame(res, columns=["code_fournisseur", "id_produit", "similarite", "ecart_prix", "id_nom_seul"])
    R["accepte"] = (R["similarite"] >= seuil_nom) & (R["ecart_prix"] <= seuil_prix)
    return R
