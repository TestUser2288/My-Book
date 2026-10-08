"""Aides du chapitre 3 (« Visualisation avec Python ») partagées par le livre et le cahier : chargement, figures « de coulisses », captures réelles
d'outils libres exécutés ici (plotly, Dash, Streamlit, Shiny), extraction des applications écrites dans le livre, cartes en plan fictif.

Les captures (Chromium sans interface) sont coûteuses : elles ne sont refaites que si le PNG n'existe pas ou si REGENERER_CAPTURES=1.
Rien n'est téléchargé ; aucun logiciel commercial n'est photographié.
"""
import contextlib
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style as S  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
FIG = os.path.join(RACINE, "figures")
CANAUX = ["Boutique", "Site", "Réseaux"]
COUL = {"Boutique": S.BLEU, "Site": S.ORANGE, "Réseaux": S.AQUA}


def fr(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def lire(nom, **kw):
    return pd.read_csv(os.path.join(DONNEES, nom), **kw)


def ventes():
    """une ligne par ligne de commande : montant, date, canal, client, catégorie, année, mois"""
    c = lire("commandes.csv", parse_dates=["date_commande"])
    p = lire("produits.csv")[["id_produit", "categorie"]]
    x = lire("lignes_commande.csv").merge(c[["id_commande", "date_commande", "canal", "id_client"]], on="id_commande").merge(p, on="id_produit")
    x["annee"] = x["date_commande"].dt.year
    x["mois"] = x["date_commande"].dt.to_period("M")
    return x


def jours():
    j = lire("jours_exploitation.csv", parse_dates=["date"])
    j["annee"], j["mois"] = j["date"].dt.year, j["date"].dt.month
    return j


def sauver(fig, nom, dpi=200):
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, nom), dpi=dpi, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("figure :", nom)


def ca_canal(x, annee=2025):
    return x[x["annee"] == annee].groupby("canal")["montant"].sum().reindex(CANAUX)


def figure_ventes_canal(donnees, annee=2025):
    """la figure finale de la section 3.1 : une fonction qui reçoit les données et retourne la figure (testable)"""
    ca = ca_canal(donnees, annee) / 1000
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    barres = ax.bar(ca.index, ca.values, color=[COUL[c] for c in ca.index], width=0.62)
    ax.bar_label(barres, labels=[f"{fr(v)} k€" for v in ca.values], padding=3, color=S.ENCRE)
    ax.set(ylim=(0, ca.max() * 1.15), yticks=[])
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_title(f"Le Site et la Boutique font 89 % du chiffre d'affaires {annee}", loc="left", fontweight="bold", color=S.ENCRE)
    return fig


# --------------------------------------------------------------------------------------------- figures de coulisses
def anatomie():
    """schéma annoté d'une figure matplotlib : Figure, Axes, Axis, Artist (dessiné avec matplotlib)"""
    fig = plt.figure(figsize=(7.2, 4.2))
    fig.patch.set_edgecolor(S.MUET); fig.patch.set_linewidth(2)
    ax = fig.add_axes([0.11, 0.2, 0.46, 0.62])
    x = np.arange(12)
    ax.plot(x, [10, 11, 13, 14, 15, 14, 12, 11, 15, 17, 22, 28], color=S.BLEU, label="ligne")
    ax.set(xlabel="étiquette de l'axe des x", ylabel="axe des y", title="titre de l'Axes")
    ax.legend(loc="upper left")
    fl = dict(arrowstyle="->", color=S.ORANGE, lw=1.3)
    ax.annotate("Axes : la zone de dessin,\nses deux Axis et son titre", xy=(0.99, 0.80), xycoords="axes fraction", xytext=(0.62, 0.92), textcoords="figure fraction",
                fontsize=9, color=S.ENCRE, va="top", arrowprops=fl)
    ax.annotate("Artist : tout ce qui se dessine\n(ligne, légende, texte, barre)", xy=(10.5, 25), xycoords="data", xytext=(0.62, 0.70), textcoords="figure fraction",
                fontsize=9, color=S.ENCRE, va="top", arrowprops=fl)
    ax.annotate("Axis : l'axe, ses graduations\net son étiquette", xy=(0.99, 0.0), xycoords="axes fraction", xytext=(0.62, 0.48), textcoords="figure fraction",
                fontsize=9, color=S.ENCRE, va="top", arrowprops=fl)
    ax.annotate("Figure : toute l'image\n(taille, fond, enregistrement)", xy=(0.995, 0.02), xycoords="figure fraction", xytext=(0.62, 0.26), textcoords="figure fraction",
                fontsize=9, color=S.ENCRE, va="top", arrowprops=fl)
    return fig


def trois_couches():
    """schéma des trois couches : données, esthétiques, géométries (dessiné)"""
    fig, ax = plt.subplots(figsize=(7.2, 2.3))
    ax.axis("off"); ax.set_xlim(0, 10.4); ax.set_ylim(0, 3)
    cases = [("1. Les données", "canal  ca_2025\nBoutique  561\nSite  618\nRéseaux  146", S.BLEU), ("2. Les esthétiques", "x = canal\nhauteur = chiffre d'affaires\ncouleur = canal", S.ORANGE),
             ("3. La géométrie", "des barres\n(une barre par ligne)", S.AQUA)]
    for i, (t, corps, col) in enumerate(cases):
        x0 = 0.2 + i * 3.4
        ax.add_patch(FancyBboxPatch((x0, 0.3), 3.0, 2.4, boxstyle="round,pad=0.05", fc="white", ec=col, lw=2))
        ax.text(x0 + 1.5, 2.35, t, ha="center", va="center", fontweight="bold", color=col)
        ax.text(x0 + 1.5, 1.25, corps, ha="center", va="center", fontsize=9, color=S.ENCRE)
        if i < 2:
            ax.annotate("", xy=(x0 + 3.35, 1.5), xytext=(x0 + 3.05, 1.5), arrowprops=dict(arrowstyle="->", color=S.MUET, lw=1.5))
    return fig


def barres_defaut(x):
    ca = ca_canal(x) / 1000
    fig, ax = plt.subplots()
    ax.bar(ca.index, ca.values)
    return fig


def serie_mensuelle(x):
    m = x.groupby(["mois", "canal"])["montant"].sum().unstack()[CANAUX] / 1000
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    idx = m.index.to_timestamp()
    for c in CANAUX:
        ax.plot(idx, m[c], color=COUL[c], lw=2)
        ax.text(idx[-1] + pd.Timedelta(days=12), m[c].iloc[-1], c, color=COUL[c], va="center", fontweight="bold")
    ax.set_ylabel("k€ par mois")
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m/%Y"))
    ax.set_xlim(idx[0], idx[-1] + pd.Timedelta(days=95))
    pic = m.sum(axis=1).idxmax().to_timestamp()
    ax.annotate("décembre 2025 :\nle pic de trois ans", xy=(pic, m.loc[m.sum(axis=1).idxmax(), "Site"]), xytext=(pic - pd.Timedelta(days=60), 84), ha="right",
                arrowprops=dict(arrowstyle="->", color=S.MUET), color=S.ENCRE2, fontsize=9)
    ax.set_title("Chiffre d'affaires mensuel par canal, 2023-2025", loc="left", color=S.ENCRE, fontweight="bold")
    return fig


# --------------------------------------------------------------------------------------------- captures réelles
def doit_capturer(png):
    return os.environ.get("REGENERER_CAPTURES") == "1" or not os.path.exists(png)


def _point(page, x, y):
    """(x, y) en pixels ; ou, si les deux valent au plus 1, en fractions de la zone de tracé plotly (0, 0 = haut gauche)"""
    if 0 <= x <= 1 and 0 <= y <= 1:
        b = page.locator(".nsewdrag").first.bounding_box()
        return b["x"] + x * b["width"], b["y"] + y * b["height"]
    return x, y


def capturer_html(html_chemin, png, largeur=1000, hauteur=520, survol=None, clic=None, glisser=None, attente_ms=700):
    """photographie une page HTML locale avec Chromium sans interface.
    `survol` : sélecteur CSS (texte) ou (x, y) ; `clic` : liste de sélecteurs CSS ou de (x, y) ;
    `glisser` : liste de (x1, y1, x2, y2). Les coordonnées sont en pixels, ou en fractions de la zone de tracé si elles valent au plus 1."""
    if not doit_capturer(png):
        print("capture existante :", os.path.basename(png))
        return png
    from playwright.sync_api import sync_playwright
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={"width": largeur, "height": hauteur}, device_scale_factor=2)
        page.goto("file://" + html_chemin)
        page.wait_for_timeout(attente_ms)
        page.add_style_tag(content=".notifier-note {display: none !important}")      # cache l'astuce « double-clic pour revenir » qui masque la légende
        for cible in (clic or []):
            if isinstance(cible, str):
                page.locator(cible).first.click(force=True)
            else:
                page.mouse.click(*_point(page, *cible))
            page.wait_for_timeout(700)
        for x1, y1, x2, y2 in (glisser or []):
            a, b = _point(page, x1, y1), _point(page, x2, y2)
            page.mouse.move(*a); page.mouse.down(); page.mouse.move(*b, steps=8); page.mouse.up()
            page.wait_for_timeout(500)
        if survol:
            if isinstance(survol, str):
                page.locator(survol).first.hover(force=True)
            else:
                page.mouse.move(*_point(page, *survol))
            page.wait_for_timeout(400)
        page.screenshot(path=png)
        nav.close()
    print("capture :", os.path.basename(png))
    return png


def capturer_url(url, png, largeur=1100, hauteur=700, attendre_texte=None, attente_ms=1500, interactions=None):
    """photographie une application locale en cours d'exécution ; `attendre_texte` : texte à voir avant de photographier ; `interactions` : fonction(page)"""
    if not doit_capturer(png):
        print("capture existante :", os.path.basename(png))
        return png
    from playwright.sync_api import sync_playwright
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={"width": largeur, "height": hauteur}, device_scale_factor=2)
        page.goto(url)
        if attendre_texte:
            page.get_by_text(attendre_texte).first.wait_for(timeout=30000)
        page.wait_for_timeout(attente_ms)
        if interactions:
            interactions(page)
            page.wait_for_timeout(attente_ms)
        page.screenshot(path=png)
        nav.close()
    print("capture :", os.path.basename(png))
    return png


def port_libre():
    with contextlib.closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def serveur(commande, port, env=None, delai=60):
    """lance une application en sous-processus local, attend l'ouverture du port, puis l'arrête proprement (aucun processus orphelin)"""
    proc = subprocess.Popen(commande, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, **(env or {})}, start_new_session=True)
    try:
        debut = time.time()
        while time.time() - debut < delai:
            with contextlib.closing(socket.socket()) as s:
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    break
            if proc.poll() is not None:
                raise RuntimeError("l'application s'est arrêtée au démarrage")
            time.sleep(0.5)
        else:
            raise RuntimeError("délai dépassé")
        yield proc
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, 15)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, 9)


# --------------------------------------------------------------------------------------------- applications écrites dans le livre
def extraire_apps(md, dossier):
    """lit le fichier Markdown du livre, rassemble les blocs `noexec` dont la première ligne est « # app_xxx.ext (k/n) » et écrit les fichiers dans `dossier`.
    Le code montré au lecteur est donc exactement le code testé."""
    texte = open(md, encoding="utf-8").read()
    parties = {}
    for m in re.finditer(r"```(?:python|r) noexec\n(# app_[a-z_]+\.(?:py|R)) ?(?:\((\d+)/(\d+)\))?\n(.*?)```", texte, flags=re.S):
        nom = m.group(1)[2:]
        parties.setdefault(nom, []).append((int(m.group(2) or 1), m.group(4)))
    os.makedirs(dossier, exist_ok=True)
    for nom, liste in parties.items():
        with open(os.path.join(dossier, nom), "w", encoding="utf-8") as f:
            f.write("".join(corps for _, corps in sorted(liste)))
    return sorted(parties)


def photographier_appli(commande, png, texte, env=None, largeur=1100, hauteur=760, interactions=None):
    """lance l'application (`{port}` est remplacé par un port libre), la photographie quand `texte` est affiché, l'arrête ; ne fait rien si le PNG existe déjà"""
    if not doit_capturer(png):
        print("capture existante :", os.path.basename(png))
        return png
    port = port_libre()
    cmd = [c.replace("{port}", str(port)) for c in commande]
    env = {k: v.replace("{port}", str(port)) for k, v in (env or {}).items()}
    with serveur(cmd, port, env):
        capturer_url(f"http://127.0.0.1:{port}", png, largeur=largeur, hauteur=hauteur, attendre_texte=texte, interactions=interactions)
    return png


def dossier_apps():
    """dossier fixe (sous TMPDIR) où sont écrites les applications extraites du livre ; lisible aussi par R"""
    d = os.path.join(os.environ.get("TMPDIR", tempfile.gettempdir()), "ch03-apps")
    os.makedirs(d, exist_ok=True)
    return d


def supprimer_dossier(chemin):
    """suppression d'un dossier temporaire sous TMPDIR, seulement s'il porte le préfixe de ce chapitre"""
    chemin = os.path.abspath(chemin)
    if os.path.basename(chemin).startswith("ch03-") and os.path.isdir(chemin):
        shutil.rmtree(chemin, ignore_errors=True)


def dossier_temp():
    return tempfile.mkdtemp(prefix="ch03-", dir=os.environ.get("TMPDIR"))


# --------------------------------------------------------------------------------------------- cartes en plan fictif
def ventes_villes(x, annee=2025):
    cl = lire("clients.csv")[["id_client", "ville"]]
    v = lire("villes.csv").set_index("ville")
    ca = x[x["annee"] == annee].merge(cl, on="id_client").groupby("ville")["montant"].sum().rename("ca")
    d = v.join(ca)
    d["par_habitant"] = d["ca"] / d["habitants"]
    return d


def voronoi_polygones(pts, borne=(-10, 130, -10, 100)):
    """polygones de Voronoï bornés (méthode des demi-plans) pour des points d'un plan fictif : renvoie une liste de tableaux (n, 2)"""
    x0, x1, y0, y1 = borne
    polys = []
    for i, p in enumerate(pts):
        poly = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], float)
        for j, q in enumerate(pts):
            if i == j:
                continue
            n = q - p
            c = (q @ q - p @ p) / 2
            nouveau = []
            for k in range(len(poly)):
                a, b = poly[k], poly[(k + 1) % len(poly)]
                da, db = a @ n - c, b @ n - c
                if da <= 0:
                    nouveau.append(a)
                if da * db < 0:
                    t = da / (da - db)
                    nouveau.append(a + t * (b - a))
            poly = np.array(nouveau)
            if len(poly) == 0:
                break
        polys.append(poly)
    return polys
