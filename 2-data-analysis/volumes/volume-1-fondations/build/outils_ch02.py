"""Outils du chapitre 2 (Excel) : jeux de données de 2025, évaluation de formules par LibreOffice en un seul passage, TCD par pandas.

Principe : on écrit les formules avec les NOMS ANGLAIS (ce que stocke un fichier .xlsx) ; `evaluer` fabrique un classeur contenant les données et
une feuille `Calc` (une formule par ligne), LibreOffice le recalcule, et l'on lit les valeurs. Le livre affiche la formule convertie par `outils_xl.en_fr`.
"""
import os, sys, tempfile, shutil, datetime as dt
import numpy as np
import pandas as pd
import xlsxwriter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_xl as X

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


def charger_2025():
    """lignes de 2025 comme dans la feuille `Lignes` du classeur, produits et clients"""
    cmd = pd.read_csv(os.path.join(DONNEES, "commandes.csv"))
    lig = pd.read_csv(os.path.join(DONNEES, "lignes_commande.csv"))
    prod = pd.read_csv(os.path.join(DONNEES, "produits.csv"))
    cli = pd.read_csv(os.path.join(DONNEES, "clients.csv"))
    c25 = cmd[cmd["date_commande"] >= "2025-01-01"]
    l = lig[lig["id_commande"].isin(c25["id_commande"])].merge(c25[["id_commande", "date_commande", "id_client", "canal", "code_promo"]], on="id_commande")
    l = l.merge(prod[["id_produit", "nom_produit", "categorie"]], on="id_produit")
    l["date_commande"] = pd.to_datetime(l["date_commande"])
    cols = ["id_ligne", "id_commande", "date_commande", "id_client", "canal", "code_promo", "id_produit", "nom_produit", "categorie", "quantite", "prix_unitaire", "remise_pct", "montant"]
    l = l[cols].sort_values("id_ligne").reset_index(drop=True)
    return l, prod[["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat", "fournisseur"]], cli[["id_client", "ville", "annee_naissance", "canal_acquisition", "fidelite"]]


def _ecrire_df(wb, nom, df, formats):
    ws = wb.add_worksheet(nom)
    for j, c in enumerate(df.columns):
        ws.write(0, j, c, formats["h"])
    for j, c in enumerate(df.columns):
        s = df[c]
        for i, v in enumerate(s.tolist(), start=1):
            if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT or (not isinstance(v, (str, int, float, bool)) and pd.isna(v)):
                continue
            if isinstance(v, pd.Timestamp):
                ws.write_datetime(i, j, v.to_pydatetime(), formats["d"])
            elif isinstance(v, (np.integer,)):
                ws.write_number(i, j, int(v))
            elif isinstance(v, (np.floating, float)):
                ws.write_number(i, j, float(v))
            else:
                ws.write(i, j, v)
    return ws


def evaluer(formules, feuilles=None, noms=None, extra=None, colonnes=None, tables=None):
    """Évalue des formules (noms anglais) avec LibreOffice.
    formules : dict {étiquette: '=SUM(Lignes!M:M)'} (une cellule chacune, feuille `Calc`, colonne B) ;
    feuilles : dict {nom_de_feuille: DataFrame} (en-têtes en ligne 1) ; noms : dict {nom: '=Lignes!$M:$M'} (plages nommées) ;
    extra : dict {nom_de_feuille: liste de lignes (valeurs ou formules)} pour de petites feuilles écrites à la main ;
    colonnes : dict {feuille: {nom_colonne: modèle de formule avec {r} = numéro de ligne}} (colonnes calculées ajoutées à droite des données) ;
    tables : dict {feuille: nom_de_tableau} (met la plage de données sous forme de tableau structuré Excel, pour les références Tableau[colonne]).
    Retourne dict {étiquette: valeur}. Un seul passage LibreOffice."""
    tmp = tempfile.mkdtemp(prefix="xl-", dir=os.environ.get("TMPDIR"))
    try:
        chemin = os.path.join(tmp, "calc.xlsx")
        wb = xlsxwriter.Workbook(chemin, {"use_future_functions": True})
        fm = {"h": wb.add_format({"bold": True, "bg_color": "#DDEBF7", "border": 1}), "d": wb.add_format({"num_format": "dd/mm/yyyy"})}
        for nom, df in (feuilles or {}).items():
            ws_ = _ecrire_df(wb, nom, df, fm)
            cc = (colonnes or {}).get(nom, {})
            for k, (cn, modele) in enumerate(cc.items()):
                j = len(df.columns) + k
                ws_.write(0, j, cn, fm["h"])
                for r in range(2, len(df) + 2):
                    ws_.write_formula(r - 1, j, modele.format(r=r))
            if tables and nom in tables:
                entetes = list(df.columns) + list(cc)
                ws_.add_table(0, 0, len(df), len(entetes) - 1, {"name": tables[nom], "columns": [{"header": c} for c in entetes], "style": None})
        for nom, lignes in (extra or {}).items():
            ws = wb.add_worksheet(nom)
            for i, lg in enumerate(lignes):
                for j, v in enumerate(lg):
                    if v is None:
                        continue
                    if isinstance(v, str) and v.startswith("="):
                        ws.write_formula(i, j, v)
                    elif isinstance(v, (dt.date, dt.datetime)):
                        ws.write_datetime(i, j, v if isinstance(v, dt.datetime) else dt.datetime.combine(v, dt.time()), fm["d"])
                    else:
                        ws.write(i, j, v)
        for n, ref in (noms or {}).items():
            wb.define_name(n, ref)
        ws = wb.add_worksheet("Calc")
        cles = list(formules)
        for i, k in enumerate(cles):
            ws.write(i, 0, k)
            f = formules[k]
            if isinstance(f, str) and f.startswith("="):
                ws.write_formula(i, 1, f)
            elif isinstance(f, (dt.date, dt.datetime)):
                ws.write_datetime(i, 1, f if isinstance(f, dt.datetime) else dt.datetime.combine(f, dt.time()), fm["d"])
            else:
                ws.write(i, 1, f)
        wb.close()
        rec = X.recalculer(chemin, tmp)
        val = X.valeurs(rec, "Calc")
        return {cles[i]: val[i][1] for i in range(len(cles))}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def resume(v, nd=2):
    """valeur LibreOffice -> nombre arrondi ou texte (pour l'affichage)"""
    if isinstance(v, float):
        return round(v, nd)
    return v


def fr(v, nd=2):
    """formatage français d'une valeur renvoyée par LibreOffice : 1 324 763,72 ; 03/11/2025 ; texte tel quel"""
    if isinstance(v, bool):
        return "VRAI" if v else "FAUX"
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}".replace(",", " ")
    if isinstance(v, (float, np.floating)):
        if abs(v - round(v)) < 1e-9 and abs(v) < 1e15:
            return f"{int(round(v)):,}".replace(",", " ")
        return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")
    return str(v)


def montrer(res, lignes, nd=2):
    """imprime « formule française  →  résultat » ; lignes = liste de (clé du dict `res`, formule anglaise)"""
    for cle, f in lignes:
        print(f"{X.en_fr(f).replace('_xlpm.', '')}  →  {fr(res[cle], nd)}")


def _fabrique_maquette():
    """copie de `outils_xl.maquette` avec un paramètre `lettres` : lettres de colonnes à afficher (colonnes masquées dans la feuille réelle),
    pour que les maquettes portent les VRAIES lettres du classeur (M = montant…)."""
    import inspect, re
    src = inspect.getsource(X.maquette)
    src = src.replace("def maquette(png, lignes,", "def maquette_l(png, lignes, lettres=None,")
    src = src.replace('        s = ""\n        j += 1', '        s = ""; jj = j\n        j += 1', 1)
    src = src.replace("        return s\n\n    def ref(a):", "        return s if not lettres else lettres[jj]\n\n    def ref(a):", 1)
    src = src.replace("        return int(m.group(2)) - 1, c - 1", "        return int(m.group(2)) - 1, (lettres.index(m.group(1)) if lettres else c - 1)", 1)
    src = src.replace('if abs(v - round(v)) > 1e-9 else f"{int(round(v)):,}".replace(",", " ")', '')   # un nombre décimal garde toujours ses deux décimales
    ns = {}
    exec(src, ns)
    return ns["maquette_l"]


maquette = _fabrique_maquette()
