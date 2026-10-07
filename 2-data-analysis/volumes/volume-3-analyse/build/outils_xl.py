"""Outils Excel du volume (série 2, volume I) : écrire un classeur AVEC formules, le faire recalculer par LibreOffice (sans interface), lire les
valeurs calculées et produire une « capture » de la feuille (PDF -> PNG). Excel n'est pas installé sur la machine qui produit le livre :
les formules sont donc **vérifiées avec LibreOffice Calc**, qui lit les formules Excel (xlsx) ; quelques fonctions récentes peuvent différer.

    from outils_xl import classeur, recalculer, valeurs, capture

Pièges : `LET(x, …)` doit s'écrire `_xlpm.x` pour les noms de variables ; `TEXT(date, "mmmm yyyy")` suit la langue du profil LibreOffice (français ici).
"""
import os, shutil, subprocess, tempfile
import xlsxwriter
import openpyxl

SOFFICE = shutil.which("soffice") or "/usr/bin/soffice"


def classeur(chemin, feuilles, largeurs=None):
    """Écrit `chemin` (.xlsx). `feuilles` = {nom: liste de lignes} ; une cellule commençant par '=' est une formule, le reste une valeur.
    Les dates (datetime.date) sont écrites avec un format de date. Retourne le chemin."""
    import datetime as dt
    wb = xlsxwriter.Workbook(chemin, {"use_future_functions": True})   # préfixe _xlfn. des fonctions récentes (XLOOKUP, LET, TEXTJOIN…)
    fdate = wb.add_format({"num_format": "dd/mm/yyyy"})
    for nom, lignes in feuilles.items():
        ws = wb.add_worksheet(nom)
        for i, ligne in enumerate(lignes):
            for j, v in enumerate(ligne):
                if v is None:
                    continue
                if isinstance(v, str) and v.startswith("="):
                    ws.write_formula(i, j, v)
                elif isinstance(v, (dt.date, dt.datetime)):
                    ws.write_datetime(i, j, dt.datetime.combine(v, dt.time()) if not isinstance(v, dt.datetime) else v, fdate)
                else:
                    ws.write(i, j, v)
        if largeurs:
            for j, w in enumerate(largeurs):
                ws.set_column(j, j, w)
    wb.close()
    return chemin


XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Setup/L10N"><prop oor:name="ooSetupSystemLocale" oor:op="fuse"><value>fr-FR</value></prop></item>
<item oor:path="/org.openoffice.Setup/L10N"><prop oor:name="ooLocale" oor:op="fuse"><value>fr-FR</value></prop></item>
</oor:items>
"""


def _profil():
    """dossier temporaire servant de profil LibreOffice, avec « recalculer toujours à l'ouverture »"""
    d = tempfile.mkdtemp(prefix="lo-", dir=os.environ.get("TMPDIR"))
    os.makedirs(os.path.join(d, "profil", "user"), exist_ok=True)
    open(os.path.join(d, "profil", "user", "registrymodifications.xcu"), "w", encoding="utf-8").write(XCU)
    return d


def recalculer(chemin, sortie=None):
    """Fait ouvrir, recalculer et ré-enregistrer le classeur par LibreOffice ; retourne le chemin du classeur recalculé."""
    out = sortie or os.path.dirname(chemin)
    prof = _profil()
    try:
        env = dict(os.environ, HOME=prof)
        cmd = [SOFFICE, f"-env:UserInstallation=file://{prof}/profil", "--headless", "--norestore", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
               "--outdir", os.path.join(prof, "out"), chemin]
        subprocess.run(cmd, check=True, capture_output=True, timeout=180, env=env)
        res = os.path.join(prof, "out", os.path.basename(chemin))
        dest = os.path.join(out, "recalcule_" + os.path.basename(chemin))
        shutil.copy(res, dest)
        return dest
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def valeurs(chemin_recalcule, feuille=None):
    """Retourne les valeurs calculées sous forme de liste de lignes (openpyxl, data_only)."""
    wb = openpyxl.load_workbook(chemin_recalcule, data_only=True)
    ws = wb[feuille] if feuille else wb.worksheets[0]
    return [[c for c in row] for row in ws.iter_rows(values_only=True)]


def capture(chemin, png, dpi=130):
    """Convertit la première feuille du classeur en PNG (aspect de LibreOffice, pas d'Excel), rogné sur le contenu."""
    prof = _profil()
    try:
        env = dict(os.environ, HOME=prof)
        subprocess.run([SOFFICE, f"-env:UserInstallation=file://{prof}/profil", "--headless", "--norestore", "--convert-to", "pdf",
                        "--outdir", prof, chemin], check=True, capture_output=True, timeout=180, env=env)
        pdf = os.path.join(prof, os.path.splitext(os.path.basename(chemin))[0] + ".pdf")
        base = os.path.join(prof, "p")
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", "1", "-l", "1", "-png", pdf, base], check=True)
        src = [f for f in os.listdir(prof) if f.startswith("p-") and f.endswith(".png")][0]
        from PIL import Image, ImageChops
        im = Image.open(os.path.join(prof, src)).convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        box = ImageChops.difference(im, bg).getbbox()
        if box:
            m = 12
            im = im.crop((max(0, box[0] - m), max(0, box[1] - m), min(im.width, box[2] + m), min(im.height, box[3] + m)))
        im.save(png)
        return png
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def maquette(png, lignes, largeurs=None, active=None, formule=None, onglets=("Feuil1",), onglet_actif=0, surligne=None, titre=None, hauteur_ligne=0.26):
    """Dessine une MAQUETTE de tableur (barre de formule, lettres de colonnes, numéros de lignes, grille) avec matplotlib, à partir de valeurs
    déjà calculées (par exemple par `valeurs(recalculer(...))`). Ce n'est pas une capture d'écran d'Excel : la légende doit le dire.
    `lignes` : liste de lignes (valeurs affichables) ; `active` : 'B3' (cellule sélectionnée) ; `formule` : texte de la barre de formule ;
    `surligne` : liste de plages 'A2:C5' colorées en bleu clair ; `largeurs` : largeur de chaque colonne (en caractères)."""
    import re
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    nl = len(lignes)
    nc = max(len(r) for r in lignes)
    larg = list(largeurs or [12] * nc) + [12] * (nc - len(largeurs or []))
    wpx = [0.085 * w + 0.15 for w in larg]
    x0, hdr = 0.45, 0.30
    W = x0 + sum(wpx) + 0.1
    H = 0.32 + 0.04 + hdr + nl * hauteur_ligne + 0.38
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

    def col(j):
        s = ""
        j += 1
        while j:
            j, r = divmod(j - 1, 26)
            s = chr(65 + r) + s
        return s

    def ref(a):
        m = re.fullmatch(r"([A-Z]+)(\d+)", a)
        c = 0
        for ch in m.group(1):
            c = c * 26 + ord(ch) - 64
        return int(m.group(2)) - 1, c - 1

    xs = [x0]
    for w in wpx:
        xs.append(xs[-1] + w)
    top = 0.32                                         # sous la barre de formule
    ax.add_patch(Rectangle((0, 0), W, 0.32, color="#f3f2ee"))
    ax.add_patch(Rectangle((0.08, 0.05), 0.7, 0.22, fc="white", ec="#c3c2b7", lw=0.6))
    ax.text(0.16, 0.16, active or "", fontsize=7.5, va="center", family="DejaVu Sans")
    ax.text(0.9, 0.16, "fx", fontsize=8, va="center", style="italic", color="#52514e")
    ax.add_patch(Rectangle((1.2, 0.05), W - 1.3, 0.22, fc="white", ec="#c3c2b7", lw=0.6))
    if formule is not None:
        ax.text(1.28, 0.16, formule, fontsize=7.5, va="center", family="DejaVu Sans Mono")
    ytop = top + 0.04
    ax.add_patch(Rectangle((0, ytop), W, hdr, color="#f3f2ee"))
    for j in range(nc):
        ax.text((xs[j] + xs[j + 1]) / 2, ytop + hdr / 2, col(j), ha="center", va="center", fontsize=7.5, color="#52514e")
    y0 = ytop + hdr
    ys = [y0 + i * hauteur_ligne for i in range(nl + 1)]
    for rng in (surligne or []):
        a, b = rng.split(":") if ":" in rng else (rng, rng)
        (r1, c1), (r2, c2) = ref(a), ref(b)
        ax.add_patch(Rectangle((xs[c1], ys[r1]), xs[c2 + 1] - xs[c1], ys[r2 + 1] - ys[r1], fc="#cde2fb", ec="none", alpha=0.8))
    for i in range(nl + 1):
        ax.plot([x0, xs[-1]], [ys[i], ys[i]], color="#dcdbd3", lw=0.5)
    for j in range(nc + 1):
        ax.plot([xs[j], xs[j]], [y0, ys[-1]], color="#dcdbd3", lw=0.5)
    ax.add_patch(Rectangle((0, y0), x0, ys[-1] - y0, color="#f3f2ee"))
    for i in range(nl):
        ax.text(x0 / 2, (ys[i] + ys[i + 1]) / 2, str(i + 1), ha="center", va="center", fontsize=7.5, color="#52514e")
        for j, v in enumerate(lignes[i]):
            if v is None or v == "":
                continue
            if isinstance(v, float):
                t = f"{v:,.2f}".replace(",", " ").replace(".", ",") if abs(v - round(v)) > 1e-9 else f"{int(round(v)):,}".replace(",", " ")
            elif hasattr(v, "strftime"):
                t = v.strftime("%d/%m/%Y")
            else:
                t = str(v)
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            if num:
                ax.text(xs[j + 1] - 0.06, (ys[i] + ys[i + 1]) / 2, t, ha="right", va="center", fontsize=8)
            else:
                ax.text(xs[j] + 0.06, (ys[i] + ys[i + 1]) / 2, t, ha="left", va="center", fontsize=8)
    if active:
        r, c = ref(active)
        ax.add_patch(Rectangle((xs[c], ys[r]), xs[c + 1] - xs[c], ys[r + 1] - ys[r], fc="none", ec="#1f7a4d", lw=1.8))
    yb = ys[-1] + 0.06
    ax.add_patch(Rectangle((0, yb), W, 0.28, color="#f3f2ee"))
    xo = 0.1
    for k, nom in enumerate(onglets):
        w = 0.1 + 0.075 * len(nom)
        ax.add_patch(Rectangle((xo, yb + 0.03), w, 0.22, fc="white" if k == onglet_actif else "#e7e6e0", ec="#c3c2b7", lw=0.5))
        ax.text(xo + w / 2, yb + 0.14, nom, ha="center", va="center", fontsize=7.5, weight="bold" if k == onglet_actif else "normal")
        xo += w + 0.05
    if titre:
        fig.suptitle(titre, fontsize=8, y=0.995)
    fig.savefig(png, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png


# --- noms de fonctions : anglais (fichier .xlsx) -> français (Excel en français) ; séparateur d'arguments « ; » ---------------------------------
FR = {"SUM": "SOMME", "SUMIF": "SOMME.SI", "SUMIFS": "SOMME.SI.ENS", "SUMPRODUCT": "SOMMEPROD", "AVERAGE": "MOYENNE", "AVERAGEIF": "MOYENNE.SI",
      "AVERAGEIFS": "MOYENNE.SI.ENS", "COUNT": "NB", "COUNTA": "NBVAL", "COUNTIF": "NB.SI", "COUNTIFS": "NB.SI.ENS", "COUNTBLANK": "NB.VIDE",
      "IF": "SI", "IFS": "SI.CONDITIONS", "IFERROR": "SIERREUR", "IFNA": "SI.NON.DISP", "AND": "ET", "OR": "OU", "NOT": "NON",
      "VLOOKUP": "RECHERCHEV", "HLOOKUP": "RECHERCHEH", "XLOOKUP": "RECHERCHEX", "XMATCH": "EQUIVX", "INDEX": "INDEX", "MATCH": "EQUIV",
      "LEFT": "GAUCHE", "RIGHT": "DROITE", "MID": "STXT", "LEN": "NBCAR", "TRIM": "SUPPRESPACE", "UPPER": "MAJUSCULE", "LOWER": "MINUSCULE",
      "PROPER": "NOMPROPRE", "SUBSTITUTE": "SUBSTITUE", "CONCAT": "CONCAT", "TEXTJOIN": "JOINDRE.TEXTE", "TEXT": "TEXTE", "VALUE": "CNUM",
      "FIND": "TROUVE", "SEARCH": "CHERCHE", "TODAY": "AUJOURDHUI", "NOW": "MAINTENANT", "DATE": "DATE", "YEAR": "ANNEE", "MONTH": "MOIS",
      "DAY": "JOUR", "WEEKDAY": "JOURSEM", "EOMONTH": "FIN.MOIS", "EDATE": "MOIS.DECALER", "DATEDIF": "DATEDIF", "NETWORKDAYS": "NB.JOURS.OUVRES",
      "ROUND": "ARRONDI", "ROUNDUP": "ARRONDI.SUP", "ROUNDDOWN": "ARRONDI.INF", "ABS": "ABS", "MAX": "MAX", "MIN": "MIN", "MEDIAN": "MEDIANE",
      "MODE": "MODE", "STDEV.S": "ECARTYPE.STANDARD", "STDEV.P": "ECARTYPE.PEARSON", "VAR.S": "VAR.S", "PERCENTILE.INC": "CENTILE.INCLURE",
      "QUARTILE.INC": "QUARTILE.INCLURE", "CORREL": "COEFFICIENT.CORRELATION", "RANK.EQ": "RANG.EGALITE", "FILTER": "FILTRE", "SORT": "TRIER",
      "SORTBY": "TRIERPAR", "UNIQUE": "UNIQUE", "SEQUENCE": "SEQUENCE", "LET": "LET", "ISNUMBER": "ESTNUM", "ISBLANK": "ESTVIDE",
      "ISERROR": "ESTERREUR", "ISTEXT": "ESTTEXTE", "CHOOSE": "CHOISIR", "OFFSET": "DECALER", "INDIRECT": "INDIRECT", "ROW": "LIGNE", "COLUMN": "COLONNE",
      "TRANSPOSE": "TRANSPOSE", "NORM.DIST": "LOI.NORMALE.N", "NORM.S.INV": "LOI.NORMALE.STANDARD.INVERSE.N", "SUBTOTAL": "SOUS.TOTAL",
      "AGGREGATE": "AGREGAT", "TEXTSPLIT": "FRACTIONNER.TEXTE", "FORECAST.LINEAR": "PREVISION.LINEAIRE", "SLOPE": "PENTE", "INTERCEPT": "ORDONNEE.ORIGINE"}


def en_fr(formule):
    """Convertit une formule écrite avec les noms anglais (fichier xlsx) en formule « Excel en français » (noms français, séparateur « ; »,
    virgule décimale), pour l'AFFICHAGE dans le livre. Les chaînes entre guillemets ne sont pas modifiées. Conversion lexicale simple : à relire."""
    import re
    out, i, n = [], 0, len(formule)
    while i < n:
        ch = formule[i]
        if ch == '"':
            j = formule.index('"', i + 1) if '"' in formule[i + 1:] else n - 1
            out.append(formule[i:j + 1]); i = j + 1
            continue
        mb = re.match(r"(TRUE|FALSE)\b(?!\()", formule[i:])
        if mb and not re.search(r"[A-Za-z0-9_.]$", "".join(out)):
            out.append("VRAI" if mb.group(1) == "TRUE" else "FAUX"); i += len(mb.group(1))
            continue
        m = re.match(r"[A-Z][A-Z0-9.]*(?=\()", formule[i:])
        if m:
            nom = m.group(0)
            out.append(FR.get(nom, nom)); i += len(nom)
            continue
        if ch == ",":
            out.append(";")
        elif ch == "." and re.match(r"\d", formule[i + 1:i + 2] or "") and re.search(r"\d$", "".join(out)):
            out.append(",")
        else:
            out.append(ch)
        i += 1
    return "".join(out)
