#!/usr/bin/env python3
"""Données SIMULÉES de la série 2 (Data Analyst), volume II « Préparation des données » — graines fixes, tout est fictif.

Même univers que le volume I (la boutique : `donnees_a1.py`, copié ici sans modification) ; on en tire des **sources désordonnées**, avec une
**vérité** (fichiers `verite_*.csv`) qui permet de juger un nettoyage. Les noms de personnes sont **inventés** (syllabes), sans origine particulière.

Usage : python build/donnees_a2.py → écrit donnees/ (≈ 40 s).

VÉRITÉ PROGRAMMÉE
=================
crm_clients.csv (7 140 lignes pour 6 000 clients (+ 140 lignes de test)) : le CRM de la boutique ; 900 clients apparaissent 2 fois et 50 clients 3 fois (doublons « flous » : casse, accents retirés,
    espaces, fautes de frappe, prénom abrégé, nom et prénom inversés, e-mail différent ou absent) ; 2 % de lignes de test ; téléphones en 5 formats ; codes postaux sans zéro initial (≈ 9 %)
    ou absents (6 %) ; dates de naissance en 4 formats (jj/mm/aaaa, aaaa-mm-jj, « 12 mars 1985 », mm/jj/aaaa pour une partie des lignes issues de la saisie « site »), dont ≈ 1 % impossibles
    (31/02, année 1900 ou 2030) ; ville écrite de 6 façons (« Ville A », « VILLE A », « ville a », « Vile A » (faute), « Ville A. », et en arabe « المدينة أ » pour 2 %) ; consentement écrit en 7 façons ;
    ≈ 3 % des textes en « mojibake » (UTF-8 lu en cp1252). Vérité : `verite_crm.csv` (id_crm → id_client, indicateur de doublon, défauts injectés).
site_commandes.csv / site_lignes.csv (commandes du canal Site en 2025, ≈ 6 000) : export de la plateforme web ; 2 % de commandes en double (nouvelle tentative d'export), 1 % de commandes de test
    (e-mail `test@example.com`), 3 % annulées, statut écrit de 3 façons, montants texte (« 45,90 € », « 45.9 », « 1 245,00 »), dates ISO sans fuseau jusqu'au 14 septembre 2025 puis en UTC (`Z`) à partir du 15 septembre,
    et à partir du 15 septembre `total` exprimé **en centimes** (changement d'unité de la plateforme, non annoncé). Vérité : `verite_site.csv`.
caisse/caisse_2025-MM.csv (12 fichiers, canal Boutique, ≈ 12 500 lignes) : dérive de schéma : janvier–juin en `cp1252`, `;`, virgule décimale, en-tête « Qté », dates jj/mm/aaaa ; juillet–septembre
    en UTF-8 avec BOM, en-tête « Quantité », dates jj/mm/aa ; octobre–décembre séparateur `,`, point décimal, champs entre guillemets, colonne supplémentaire « Remise (%) » ; 3 lignes de titre, en-têtes répétés,
    ligne de total, ≈ 3 % de montants vides, 0,5 % de lignes doublées (double scan). Vérité : `verite_caisse.csv`.
catalogue_fournisseur.csv (118 lignes) : catalogue d'un fournisseur ; codes `F-xxxx`, désignations réécrites (casse, accents, abréviations, ordre des mots, 5 % en anglais), prix d'achat HT = coût d'achat ± 3 %,
    12 produits de la boutique absents, 10 produits qui ne sont pas à la boutique ; NB : 60 noms de produits de la boutique sont portés par DEUX produits à prix différents (voir volume I). Vérité : `verite_produits.csv`.
stocks_tableur.xlsx : stock mensuel 2025 saisi dans un tableur « à la main » (titres, cellules fusionnées pour les catégories, sous-totaux, mois en colonnes, « ND », « — », « rupture », nombres en texte avec espace).
    Vérité : `verite_stocks.csv` (id_produit, mois, stock).
profil_clients.csv / profil_clients_verite.csv (6 000 clients) : âge, revenu annuel estimé, nombre de commandes et dépense 2025, satisfaction moyenne, minutes sur le site. Valeurs manquantes :
    `depense_2025` MCAR (5 % au hasard) ; `revenu_annuel` MAR (la probabilité de manquer vaut 35 % avant 30 ans, 12 % ensuite, plus 10 points pour le canal Réseaux) ; `satisfaction_moy` MNAR (manque d'autant plus que
    la vraie satisfaction est basse : 40 % de manquants pour une satisfaction ≤ 2,5, 8 % au-delà). La vérité complète est dans `profil_clients_verite.csv`.
montants_saisis.csv / verite_montants.csv (6 000 lignes de commande de 2024) : montants avec ≈ 1,5 % d'anomalies injectées : décimale décalée (×10, ×100), signe inversé, zéro, placeholder 9999. Vérité : type d'anomalie et montant réel.
"""
import os
import re
import unicodedata
import numpy as np
import pandas as pd

import donnees_a1 as A1

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
CP = {}  # code postal par ville
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
AR_LETTRES = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف"]
SYL1 = ["Mi", "Ta", "Lo", "Ka", "Ve", "Na", "So", "Ri", "Du", "Ba", "Fe", "Ju", "Ma", "Pi", "Zo", "El", "Or", "Ar", "Yu", "Se"]
SYL2 = ["rel", "vin", "dar", "lon", "sen", "tel", "mar", "nor", "val", "bor", "ken", "ris", "dan", "sol", "ven", "tar", "mon", "lis", "gar", "nel"]
SYL3 = ["a", "o", "e", "i", "u", "ia", "ea", "an", "in", "el"]
NOM1 = ["Dor", "Kel", "Mon", "Tar", "Val", "Bren", "Sor", "Lan", "Per", "Gal", "Hav", "Ros", "Tor", "Wen", "Fal", "Cor", "Nev", "Ost", "Rav", "Dun"]
NOM2 = ["vane", "mar", "tier", "lin", "gren", "dis", "ver", "sac", "ner", "mont", "lais", "bert", "net", "rand", "sen", "bel", "dal", "mer", "voir", "kan"]


def _nettoyer(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def identites(cli, seed=7001):
    rng = np.random.default_rng(seed)
    n = len(cli)
    pren = [SYL1[rng.integers(20)] + SYL2[rng.integers(20)] + SYL3[rng.integers(10)] for _ in range(n)]
    nom = [NOM1[rng.integers(20)] + NOM2[rng.integers(20)] for _ in range(n)]
    villes = sorted(cli["ville"].unique())
    cp = {v: f"{(i * 4 + 1) :02d}{rng.integers(100, 999)}" for i, v in enumerate(villes)}   # 5 chiffres, certains commencent par 0
    cp_cli = [cp[v] for v in cli["ville"]]
    tel = [f"0{rng.integers(1, 9)}{rng.integers(10000000, 99999999)}" for _ in range(n)]
    naiss = []
    for a in cli["annee_naissance"].values:
        d = pd.Timestamp(int(a), 1, 1) + pd.Timedelta(days=int(rng.integers(0, 365)))
        naiss.append(d)
    ident = pd.DataFrame({"id_client": cli["id_client"].values, "prenom": pren, "nom": nom, "ville": cli["ville"].values,
                          "code_postal": cp_cli, "telephone": tel, "date_naissance": naiss})
    base = (ident["prenom"].map(_nettoyer).str.lower() + "." + ident["nom"].map(_nettoyer).str.lower())
    dom = rng.choice(["exemple.org", "courrier.test", "mail.example"], n, p=[0.5, 0.3, 0.2])
    num = rng.integers(1, 99, n)
    ident["email"] = [f"{b}{x if (i % 7 == 0) else ''}@{d}" for i, (b, d, x) in enumerate(zip(base, dom, num))]
    return ident


def _typo(s, rng):
    if len(s) < 4:
        return s
    i = int(rng.integers(1, len(s) - 1))
    k = rng.integers(0, 3)
    if k == 0:
        return s[:i] + s[i + 1:]                  # lettre oubliée
    if k == 1:
        return s[:i] + s[i] + s[i:]               # lettre doublée
    return s[:i - 1] + s[i] + s[i - 1] + s[i + 1:]  # lettres permutées


def _mojibake(s):
    try:
        return s.encode("utf-8").decode("cp1252", errors="replace")
    except Exception:
        return s


def _ville_variante(v, rng, idx):
    lettre = v[-1]
    k = rng.random()
    if k < 0.60:
        return v
    if k < 0.74:
        return v.upper()
    if k < 0.84:
        return v.lower()
    if k < 0.90:
        return "Vile " + lettre
    if k < 0.97:
        return v + "."
    return "المدينة " + AR_LETTRES[idx]


def crm(cli, ident, seed=7002):
    rng = np.random.default_rng(seed)
    villes = sorted(cli["ville"].unique())
    idx_v = {v: i for i, v in enumerate(villes)}
    n = len(ident)
    nb = np.ones(n, int)
    dup1 = rng.choice(n, 950, replace=False)
    nb[dup1] = 2
    nb[dup1[:50]] = 3
    lignes, verite = [], []
    k = 1
    ins = cli.set_index("id_client")["date_inscription"]
    for i in range(n):
        r = ident.iloc[i]
        for c in range(nb[i]):
            prenom, nom = r["prenom"], r["nom"]
            email, tel, ville, cp, dn = r["email"], r["telephone"], r["ville"], r["code_postal"], r["date_naissance"]
            defauts = []
            if c > 0:                               # ligne en double : on dégrade
                m = rng.random()
                if m < 0.25:
                    nom, prenom = nom.upper(), prenom.upper(); defauts.append("casse")
                elif m < 0.45:
                    nom, prenom = _nettoyer(nom), _nettoyer(prenom); defauts.append("accents")
                elif m < 0.65:
                    nom = _typo(nom, rng); defauts.append("faute")
                elif m < 0.80:
                    prenom = prenom[0] + "."; defauts.append("initiale")
                elif m < 0.90:
                    prenom, nom = nom, prenom; defauts.append("inversion")
                else:
                    prenom = " " + prenom + "  "; defauts.append("espaces")
                m2 = rng.random()
                if m2 < 0.25:
                    email = None; defauts.append("email_absent")
                elif m2 < 0.5:
                    email = email.upper(); defauts.append("email_majuscules")
                elif m2 < 0.6:
                    email = email.replace("@", "@@") if rng.random() < 0.5 else email.replace(".", "..", 1); defauts.append("email_invalide")
            # téléphone
            f = rng.integers(0, 5)
            if tel is not None:
                d = tel
                tel = [d, f"{d[:2]} {d[2:4]} {d[4:6]} {d[6:8]} {d[8:]}" if len(d) >= 10 else d, f"{d[:2]}.{d[2:4]}.{d[4:6]}.{d[6:8]}.{d[8:]}" if len(d) >= 10 else d,
                       f"+99 {d[1:2]} {d[2:4]} {d[4:6]} {d[6:8]} {d[8:]}" if len(d) >= 10 else d, f"({d[:1]}){d[1:2]} {d[2:]}"][f]
            # code postal
            u = rng.random()
            if u < 0.06:
                cp = None; defauts.append("cp_absent")
            elif u < 0.15 and str(cp).startswith("0"):
                cp = str(int(cp)); defauts.append("cp_zero_perdu")
            # ville
            v2 = _ville_variante(ville, rng, idx_v[ville])
            if v2 != ville:
                defauts.append("ville_variante")
            # date de naissance
            u = rng.random()
            if u < 0.01:
                dnt = rng.choice(["31/02/1980", "00/00/0000", "15/13/1990", "01/01/1900", "01/01/2030"]); defauts.append("naissance_impossible")
            else:
                fmt = rng.choice(["jma", "iso", "texte", "mja"], p=[0.5, 0.25, 0.1, 0.15])
                dnt = {"jma": dn.strftime("%d/%m/%Y"), "iso": dn.strftime("%Y-%m-%d"), "texte": f"{dn.day} {MOIS_FR[dn.month - 1]} {dn.year}", "mja": dn.strftime("%m/%d/%Y")}[fmt]
                if fmt == "mja":
                    defauts.append("naissance_format_americain")
            consent = rng.choice(["oui", "Oui", "OUI", "O", "1", "TRUE", ""], p=[0.35, 0.1, 0.05, 0.05, 0.1, 0.05, 0.3])
            if rng.random() < 0.03:
                nom = _mojibake(nom + "é"); defauts.append("mojibake")
            lignes.append((k, prenom, nom, email, tel, v2, cp, dnt, ins.loc[r["id_client"]].strftime("%d/%m/%Y"), consent,
                           rng.choice(["caisse", "site", "import"], p=[0.5, 0.4, 0.1])))
            verite.append((k, int(r["id_client"]), int(c > 0), ";".join(defauts)))
            k += 1
    df = pd.DataFrame(lignes, columns=["id_crm", "prenom", "nom", "email", "telephone", "ville", "code_postal", "date_naissance", "date_inscription", "consentement_marketing", "source_saisie"])
    # lignes de test
    test = pd.DataFrame({"id_crm": np.arange(len(df) + 1, len(df) + 1 + 140), "prenom": "Test", "nom": "TEST", "email": "test@example.com", "telephone": "0000000000",
                         "ville": "Ville A", "code_postal": "01000", "date_naissance": "01/01/2000", "date_inscription": "01/06/2025", "consentement_marketing": "non", "source_saisie": "site"})
    ver_t = pd.DataFrame({"id_crm": test["id_crm"], "id_client": -1, "est_doublon": 0, "defauts": "test"})
    df = pd.concat([df, test], ignore_index=True).sample(frac=1, random_state=3).reset_index(drop=True)
    vdf = pd.concat([pd.DataFrame(verite, columns=["id_crm", "id_client", "est_doublon", "defauts"]), ver_t], ignore_index=True)
    return df, vdf


def site(commandes, lignes, ident, seed=7003):
    rng = np.random.default_rng(seed)
    c = commandes[(commandes["canal"] == "Site") & (commandes["date_commande"] >= "2025-01-01")].copy()
    montant = lignes.groupby("id_commande")["montant"].sum().round(2)
    c["total"] = c["id_commande"].map(montant)
    ident_i = ident.set_index("id_client")
    n = len(c)
    ref = [f"WEB-{i:06d}" for i in c["id_commande"].values]
    dates = pd.to_datetime(c["date_commande"] + " " + c["heure"])
    apres = dates >= pd.Timestamp("2025-09-15")
    created = np.where(apres, dates.dt.strftime("%Y-%m-%dT%H:%M:%SZ"), dates.dt.strftime("%Y-%m-%d %H:%M:%S"))
    statut = rng.choice(["paid", "PAID", "Paid"], n, p=[0.6, 0.25, 0.15]).astype(object)
    defaut = np.array([""] * n, dtype=object)
    annule = rng.random(n) < 0.03
    statut[annule] = "cancelled"; defaut[annule] = "annulee"
    total_txt = np.empty(n, dtype=object)
    for i, (t, ap) in enumerate(zip(c["total"].values, apres.values)):
        if ap:
            total_txt[i] = str(int(round(t * 100)))
        else:
            m = rng.random()
            total_txt[i] = (f"{t:,.2f}".replace(",", " ").replace(".", ",") + " €") if m < 0.4 else (f"{t:.2f}" if m < 0.8 else f"{t:,.2f}".replace(",", " ").replace(".", ","))
    email = [ident_i.loc[x, "email"] for x in c["id_client"].values]
    email = [e.upper() if rng.random() < 0.1 else (" " + e if rng.random() < 0.03 else e) for e in email]
    nom = [f"{ident_i.loc[x, 'prenom']} {ident_i.loc[x, 'nom']}" for x in c["id_client"].values]
    out = pd.DataFrame({"order_ref": ref, "created_at": created, "status": statut, "customer_email": email, "customer_name": nom,
                        "total": total_txt, "currency": rng.choice(["EUR", "eur", "€"], n, p=[0.8, 0.1, 0.1]), "promo_code": c["code_promo"].replace("", np.nan).values,
                        "shipping_mode": c["mode_livraison"].values})
    ver = pd.DataFrame({"order_ref": ref, "id_commande": c["id_commande"].values, "id_client": c["id_client"].values, "total_vrai": c["total"].values, "defaut": defaut})
    # commandes de test
    nt = int(0.01 * n)
    tst = out.sample(nt, random_state=5).copy()
    tst["order_ref"] = [f"WEB-T{i:04d}" for i in range(nt)]
    tst["customer_email"] = "test@example.com"; tst["customer_name"] = "Test Test"; tst["total"] = "1,00"
    vt = pd.DataFrame({"order_ref": tst["order_ref"], "id_commande": -1, "id_client": -1, "total_vrai": 0.0, "defaut": "test"})
    # doublons d'export
    nd = int(0.02 * n)
    dup = out.sample(nd, random_state=6).copy()
    vd = ver[ver["order_ref"].isin(dup["order_ref"])].copy(); vd["defaut"] = "doublon_export"
    out = pd.concat([out, tst, dup], ignore_index=True).sort_values("created_at", kind="stable").reset_index(drop=True)
    ver = pd.concat([ver, vt, vd], ignore_index=True)
    # lignes
    lg = lignes[lignes["id_commande"].isin(c["id_commande"])].merge(c[["id_commande"]], on="id_commande")
    prod = lg["id_produit"].map(lambda p: f"P{p:03d}")
    lout = pd.DataFrame({"order_ref": [f"WEB-{i:06d}" for i in lg["id_commande"].values], "sku": prod, "qty": lg["quantite"].values, "unit_price": lg["prix_unitaire"].values,
                         "discount_pct": lg["remise_pct"].values})
    return out, lout, ver


def _entetes(mois):
    if mois <= 6:
        return ["N° ticket", "Date", "Heure", "Article", "Catégorie", "Qté", "Prix unitaire", "Montant"]
    if mois <= 9:
        return ["N° ticket", "Date", "Heure", "Article", "Catégorie", "Quantité", "Prix unitaire", "Montant"]
    return ["Ticket", "Date", "Heure", "Article", "Catégorie", "Qté", "Prix unitaire", "Remise (%)", "Montant"]


def caisse(commandes, lignes, produits, dossier, seed=7004):
    rng = np.random.default_rng(seed)
    c = commandes[(commandes["canal"] == "Boutique") & (commandes["date_commande"] >= "2025-01-01")]
    l = lignes[lignes["id_commande"].isin(c["id_commande"])].merge(c[["id_commande", "date_commande", "heure"]], on="id_commande").merge(
        produits[["id_produit", "nom_produit", "categorie"]], on="id_produit").sort_values(["date_commande", "heure", "id_ligne"])
    os.makedirs(os.path.join(dossier, "caisse"), exist_ok=True)
    ver = []
    for mois in range(1, 13):
        m = l[l["date_commande"].str[5:7] == f"{mois:02d}"]
        dec = "," if mois <= 9 else "."
        sep = ";" if mois <= 9 else ","
        fmt = lambda x: f"{x:.2f}".replace(".", dec)
        enc = "cp1252" if mois <= 6 else "utf-8-sig"
        lignes_txt = [f"Export caisse - Boutique{sep * (len(_entetes(mois)) - 1)}", f"Période : mois {mois:02d} de 2025{sep * (len(_entetes(mois)) - 1)}", sep * (len(_entetes(mois)) - 1)]
        ent = _entetes(mois)
        lignes_txt.append(sep.join(ent))
        k = 0
        for r in m.itertuples():
            d = pd.Timestamp(r.date_commande)
            ds = d.strftime("%d/%m/%Y") if mois <= 6 else (d.strftime("%d/%m/%y") if mois <= 9 else d.strftime("%d/%m/%Y"))
            art = r.nom_produit if rng.random() > 0.05 else r.nom_produit.upper()
            montant = fmt(r.montant) if rng.random() > 0.03 else ""
            ligne = [f"T{r.id_commande}", ds, r.heure, art, r.categorie, str(r.quantite), fmt(r.prix_unitaire)]
            if mois >= 10:
                ligne.append(str(r.remise_pct))
            ligne.append(montant)
            rep = 2 if rng.random() < 0.005 else 1
            for j in range(rep):
                txt = sep.join(f'"{x}"' if (mois >= 10 and x) else x for x in ligne)
                lignes_txt.append(txt)
                k += 1
                ver.append((f"caisse_2025-{mois:02d}.csv", len(lignes_txt), int(r.id_ligne), int(j > 0)))
                if k % 60 == 0:
                    lignes_txt.append(sep.join(ent))
        lignes_txt.append(sep * (len(ent) - 2) + f"Total{sep}{fmt(m['montant'].sum())}")
        with open(os.path.join(dossier, "caisse", f"caisse_2025-{mois:02d}.csv"), "w", encoding=enc, newline="") as f:
            f.write("\n".join(lignes_txt) + "\n")
    return pd.DataFrame(ver, columns=["fichier", "numero_ligne_fichier", "id_ligne", "est_doublon"])


def catalogue(produits, seed=7005):
    rng = np.random.default_rng(seed)
    p = produits.copy()
    absents = set(rng.choice(p["id_produit"].values, 12, replace=False))
    abbr = {"Casserole": "Cass.", "Suspension": "Susp.", "Jardinière": "Jard.", "Photophore": "Photoph.", "Bougeoir": "Bgr", "Classeur": "Classr"}
    en = {"Bol": "Bowl", "Plaid": "Throw", "Vase": "Vase", "Cadre": "Frame", "Carnet": "Notebook"}
    lignes, ver = [], []
    k = 1
    for r in p.itertuples():
        if r.id_produit in absents:
            continue
        mots = r.nom_produit.split()
        m = rng.random()
        if m < 0.30:
            des = r.nom_produit.upper()
        elif m < 0.50:
            des = _nettoyer(r.nom_produit)
        elif m < 0.65 and len(mots) == 2:
            des = f"{mots[1]} {mots[0]}"
        elif m < 0.80:
            des = abbr.get(mots[0], mots[0][:5] + ".") + " " + " ".join(mots[1:])
        elif m < 0.85:
            des = en.get(mots[0], mots[0]) + " " + " ".join(mots[1:])
        else:
            des = r.nom_produit
        if rng.random() < 0.15:
            des = " " + des + " "
        prix = round(r.cout_achat * rng.uniform(0.97, 1.03), 2)
        lignes.append((f"F-{1000 + k * 7}", des, r.categorie.upper() if rng.random() < 0.3 else r.categorie, prix, r.fournisseur))
        ver.append((f"F-{1000 + k * 7}", int(r.id_produit)))
        k += 1
    for j in range(10):
        lignes.append((f"F-{1000 + k * 7}", f"Nouveauté {j + 1} {rng.choice(['Mat', 'Brillant', 'XL'])}", "Maison", round(float(rng.uniform(3, 40)), 2), f"Fournisseur {chr(65 + j % 8)}"))
        ver.append((f"F-{1000 + k * 7}", -1))
        k += 1
    df = pd.DataFrame(lignes, columns=["code_fournisseur", "designation", "famille", "prix_achat_ht", "fournisseur"]).sample(frac=1, random_state=9).reset_index(drop=True)
    return df, pd.DataFrame(ver, columns=["code_fournisseur", "id_produit"])


def stocks(produits, chemin, seed=7006):
    import xlsxwriter
    rng = np.random.default_rng(seed)
    cats = list(produits["categorie"].unique())
    wb = xlsxwriter.Workbook(chemin)
    ws = wb.add_worksheet("Stock 2025")
    fm = wb.add_format({"bold": True, "align": "center", "bg_color": "#DDEBF7", "border": 1})
    ft = wb.add_format({"bold": True, "font_size": 14})
    fc = wb.add_format({"bold": True, "bg_color": "#F2F2F2"})
    ws.write(0, 0, "Stock de fin de mois - boutique", ft)
    ws.write(1, 0, "Saisie manuelle, à ne pas modifier sans prévenir")
    ws.write(3, 0, "Réf.", fm); ws.write(3, 1, "Désignation", fm)
    for j, m in enumerate(MOIS_FR):
        ws.write(3, 2 + j, m[:4].capitalize() + ".", fm)
    r = 4
    ver = []
    for cat in cats:
        ws.merge_range(r, 0, r, 13, cat.upper(), fc); r += 1
        sub = produits[produits["categorie"] == cat]
        deb = r
        for p in sub.itertuples():
            ws.write(r, 0, f"P{p.id_produit:03d}"); ws.write(r, 1, p.nom_produit)
            s = int(rng.integers(5, 120))
            for j in range(12):
                s = max(0, s + int(rng.integers(-15, 12)))
                x = rng.random()
                if x < 0.03:
                    ws.write(r, 2 + j, "ND"); ver.append((int(p.id_produit), j + 1, np.nan))
                elif x < 0.05:
                    ws.write(r, 2 + j, "—"); ver.append((int(p.id_produit), j + 1, np.nan))
                elif s == 0 or x < 0.07:
                    ws.write(r, 2 + j, "rupture"); ver.append((int(p.id_produit), j + 1, 0))
                elif x < 0.17:
                    ws.write(r, 2 + j, f"{s:,}".replace(",", " ") if s >= 1000 else (str(s) + " ")); ver.append((int(p.id_produit), j + 1, s))
                else:
                    ws.write_number(r, 2 + j, s); ver.append((int(p.id_produit), j + 1, s))
            r += 1
        ws.write(r, 1, "Sous-total " + cat, fc)
        for j in range(12):
            col = chr(ord("C") + j)
            ws.write_formula(r, 2 + j, f"=SUM({col}{deb + 1}:{col}{r})", fc)
        r += 2
    ws.set_column(0, 0, 8); ws.set_column(1, 1, 28); ws.set_column(2, 13, 7)
    wb.close()
    return pd.DataFrame(ver, columns=["id_produit", "mois", "stock"])


def profils(cli, commandes, lignes, seed=7007):
    rng = np.random.default_rng(seed)
    n = len(cli)
    age = (2025 - cli["annee_naissance"].values)
    c25 = commandes[commandes["date_commande"] >= "2025-01-01"]
    montant = lignes.groupby("id_commande")["montant"].sum()
    c25 = c25.assign(m=c25["id_commande"].map(montant))
    dep = c25.groupby("id_client")["m"].sum().reindex(cli["id_client"]).fillna(0.0).values
    nb = c25.groupby("id_client").size().reindex(cli["id_client"]).fillna(0).astype(int).values
    ville_idx = cli["ville"].map(lambda v: ord(v[-1]) - 65).values
    revenu = np.exp(rng.normal(10.2 + 0.012 * (np.clip(age, 18, 60) - 40) - 0.01 * ville_idx, 0.35, n)).round(-2)
    sat = np.clip(rng.normal(3.7 + 0.15 * (cli["canal_acquisition"] == "Boutique").values - 0.1 * (nb == 0), 0.7, n), 1, 5).round(2)
    minutes = np.clip(rng.gamma(2.0, 6.0, n) * (1 + 0.5 * (cli["canal_acquisition"] == "Site").values), 0, 120).round(1)
    ver = pd.DataFrame({"id_client": cli["id_client"].values, "age": age, "canal_acquisition": cli["canal_acquisition"].values, "revenu_annuel": revenu,
                        "nb_commandes_2025": nb, "depense_2025": dep.round(2), "satisfaction_moy": sat, "minutes_site": minutes})
    t = ver.copy()
    t.loc[rng.random(n) < 0.05, "depense_2025"] = np.nan                                              # MCAR
    p_rev = np.where(age < 30, 0.35, 0.12) + 0.10 * (cli["canal_acquisition"] == "Réseaux").values     # MAR
    t.loc[rng.random(n) < p_rev, "revenu_annuel"] = np.nan
    p_sat = np.where(sat <= 2.5, 0.40, 0.08)                                                           # MNAR
    t.loc[rng.random(n) < p_sat, "satisfaction_moy"] = np.nan
    return t, ver


def montants(lignes, seed=7008):
    rng = np.random.default_rng(seed)
    s = lignes[lignes["id_ligne"] % 5 == 0].head(6000).copy()
    vrai = s["montant"].values.copy()
    m = vrai.copy()
    typ = np.array([""] * len(s), dtype=object)
    u = rng.random(len(s))
    m[u < 0.005] *= 10; typ[u < 0.005] = "decimale_x10"
    sel = (u >= 0.005) & (u < 0.008); m[sel] *= 100; typ[sel] = "decimale_x100"
    sel = (u >= 0.008) & (u < 0.011); m[sel] = -m[sel]; typ[sel] = "signe_inverse"
    sel = (u >= 0.011) & (u < 0.013); m[sel] = 0; typ[sel] = "zero"
    sel = (u >= 0.013) & (u < 0.015); m[sel] = 9999; typ[sel] = "placeholder_9999"
    out = pd.DataFrame({"id_ligne": s["id_ligne"].values, "id_commande": s["id_commande"].values, "id_produit": s["id_produit"].values, "quantite": s["quantite"].values,
                        "prix_unitaire": s["prix_unitaire"].values, "montant": np.round(m, 2)})
    ver = pd.DataFrame({"id_ligne": s["id_ligne"].values, "anomalie": typ, "montant_vrai": vrai})
    return out, ver


def generer(dossier=DONNEES):
    os.makedirs(dossier, exist_ok=True)

    def ecrire(df, nom, **kw):
        df.to_csv(os.path.join(dossier, nom), index=False, **kw)
        print(f"{nom:34s} {len(df):>8d} lignes")

    cli, prod, cmd, lig, ret, jours = A1.univers()
    cmd = cmd.fillna({"code_promo": ""})
    ident = identites(cli)
    crmdf, vcrm = crm(cli, ident)
    ecrire(crmdf, "crm_clients.csv"); ecrire(vcrm, "verite_crm.csv")
    so, sl, vs = site(cmd, lig, ident)
    ecrire(so, "site_commandes.csv"); ecrire(sl, "site_lignes.csv"); ecrire(vs, "verite_site.csv")
    vc = caisse(cmd, lig, prod, dossier)
    ecrire(vc, "verite_caisse.csv")
    cat, vcat = catalogue(prod)
    ecrire(cat, "catalogue_fournisseur.csv"); ecrire(vcat, "verite_produits.csv")
    vst = stocks(prod, os.path.join(dossier, "stocks_tableur.xlsx"))
    ecrire(vst, "verite_stocks.csv")
    t, ver = profils(cli, cmd, lig)
    ecrire(t, "profil_clients.csv"); ecrire(ver, "profil_clients_verite.csv")
    mo, vm = montants(lig)
    ecrire(mo, "montants_saisis.csv"); ecrire(vm, "verite_montants.csv")
    # copies utiles du volume I (mêmes données de base)
    for nom, df in [("clients.csv", cli), ("produits.csv", prod), ("commandes.csv", cmd), ("lignes_commande.csv", lig)]:
        ecrire(df, nom)
    ecrire(ident[["id_client", "prenom", "nom", "email"]], "verite_identites.csv")


if __name__ == "__main__":
    generer()
