#!/usr/bin/env python3
"""Outils du chapitre 1 (volume V, série 2) : « Entrepôts de données et modélisation ».

- `Con` : mince enveloppe autour d'une connexion DuckDB, pour que les blocs ```sql du livre (exécutés par fill.py avec `pd.read_sql_query(…, con)`) fonctionnent
  sur DuckDB comme sur sqlite3 (`executescript`, `commit`, `cursor`).
- `ouvrir(D)` : une base DuckDB EN MÉMOIRE avec le schéma `src` (la « base opérationnelle » de la boutique ; les frais de port facturés, absents des volumes
  précédents, y sont calculés par une règle simple et déterministe : gratuits en retrait en magasin ou dès 80 € de commande, 5,90 € à domicile, 3,90 € en point relais).
- `construire_etoile(con)` : le script complet du schéma en étoile (schéma `dwh`) — c'est la version « de référence » du SQL montré dans le livre.
- `ecrire_historiques(D)` : écrit `donnees/ch01-historique-clients.csv` et `donnees/ch01-historique-produits.csv` (changements de ville de clients, reclassements de
  produits ; graine 8101). Usage : `python build/outils_ch01.py` (régénère ces deux fichiers).
- fonctions `fig_*` : les figures du chapitre (schémas dessinés avec matplotlib, aucun logo, aucune capture d'un produit).
Aucun fichier n'est écrit hors de `figures/`, `donnees/ch01-*` et d'un dossier temporaire (TMPDIR) supprimé après usage.
"""
import os
import sys
import warnings

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")


class _Curseur:
    """Curseur minimal attendu par pandas : execute / description / fetchall / close."""

    def __init__(self, d):
        self.d = d
        self.description = None

    def execute(self, sql, *a):
        self.d.execute(sql, *a)
        self.description = self.d.description
        return self

    def fetchall(self):
        return self.d.fetchall()

    def fetchone(self):
        return self.d.fetchone()

    def close(self):
        pass


class Con:
    def __init__(self, d=None):
        self.d = d or duckdb.connect(":memory:")

    def cursor(self):
        return _Curseur(self.d)

    def execute(self, sql, *a):
        return self.d.execute(sql, *a)

    def executescript(self, sql):
        self.d.execute(sql)

    def sql(self, sql):
        return self.d.sql(sql)

    def df(self, sql):
        return self.d.execute(sql).df()

    def commit(self):
        pass

    def close(self):
        self.d.close()


def ouvrir(D=DONNEES):
    """Base en mémoire avec le schéma `src` (copie de la base opérationnelle) ; retourne un `Con`."""
    con = Con()
    con.executescript("CREATE SCHEMA src")
    for t in ["clients", "produits", "lignes_commande", "retours", "livraisons", "stock_quotidien"]:
        con.executescript(f"CREATE TABLE src.{t} AS SELECT * FROM read_csv_auto('{D}/{t}.csv')")
    con.executescript(f"""CREATE TABLE src.commandes AS
        SELECT c.*, CASE WHEN c.mode_livraison = 'Retrait magasin' OR t.total >= 80 THEN 0.0
                         WHEN c.mode_livraison = 'Domicile' THEN 5.9 ELSE 3.9 END AS frais_port
        FROM read_csv_auto('{D}/commandes.csv') c
        JOIN (SELECT id_commande, SUM(montant) AS total FROM src.lignes_commande GROUP BY 1) t USING (id_commande)""")
    con.executescript(f"CREATE TABLE src.compte_resultat AS SELECT * FROM read_csv_auto('{D}/compte_resultat_mensuel.csv')")
    return con



SQL_ETOILE = [
    "CREATE SCHEMA IF NOT EXISTS dwh",
    """CREATE TABLE dwh.dim_date AS
        SELECT CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key, CAST(d AS DATE) AS date,
               year(d) AS annee, quarter(d) AS trimestre, month(d) AS mois,
               strftime(d, '%Y-%m') AS annee_mois, isodow(d) AS jour_semaine, isodow(d) >= 6 AS est_weekend
        FROM generate_series(DATE '2023-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)""",
    """CREATE TABLE dwh.dim_produit AS
        SELECT 0 AS produit_key, -1 AS id_produit, 'inconnu' AS nom_produit, 'inconnu' AS categorie, 'inconnu' AS fournisseur, NULL AS prix_catalogue
        UNION ALL
        SELECT row_number() OVER (ORDER BY id_produit), id_produit, nom_produit, categorie, fournisseur, prix_vente FROM src.produits""",
    """CREATE TABLE dwh.dim_client AS
        SELECT 0 AS client_key, -1 AS id_client, 'inconnue' AS ville, 'inconnu' AS canal_acquisition, 'inconnu' AS carte_fidelite, NULL AS annee_inscription,
               'inconnue' AS tranche_age
        UNION ALL
        SELECT row_number() OVER (ORDER BY id_client), id_client, ville, canal_acquisition, CASE WHEN fidelite = 1 THEN 'Carte fidélité' ELSE 'Sans carte' END,
               year(date_inscription),
               CASE WHEN 2025 - annee_naissance < 30 THEN '< 30 ans' WHEN 2025 - annee_naissance < 45 THEN '30-44 ans'
                    WHEN 2025 - annee_naissance < 60 THEN '45-59 ans' ELSE '60 ans et +' END
        FROM src.clients""",
    """CREATE TABLE dwh.dim_canal AS
        SELECT row_number() OVER (ORDER BY canal, mode_livraison) AS canal_key, canal, mode_livraison
        FROM (SELECT DISTINCT canal, mode_livraison FROM src.commandes)""",
    """CREATE TABLE dwh.dim_promotion AS
        SELECT 1 AS promo_key, 'Aucune' AS code_promo, 'Sans promotion' AS famille_promo
        UNION ALL SELECT 2, 'SOLDES', 'Saisonnière' UNION ALL SELECT 3, 'FIDELITE', 'Fidélisation' UNION ALL SELECT 4, 'BIENVENUE', 'Acquisition'""",
    """CREATE TABLE dwh.dim_transporteur AS
        SELECT row_number() OVER (ORDER BY transporteur) AS transporteur_key, transporteur FROM (SELECT DISTINCT transporteur FROM src.livraisons)""",
    """CREATE TABLE dwh.fait_ventes AS
        SELECT l.id_ligne, l.id_commande,
               CAST(strftime(CAST(c.date_commande AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
               k.client_key, p.produit_key, ca.canal_key, pr.promo_key,
               l.quantite, l.prix_unitaire, l.remise_pct,
               l.montant AS montant_ttc, l.montant / 1.2 AS montant_ht, l.quantite * sp.cout_achat AS cout_achat
        FROM src.lignes_commande l
        JOIN src.commandes c USING (id_commande)
        JOIN src.produits sp USING (id_produit)
        JOIN dwh.dim_client k ON k.id_client = c.id_client
        JOIN dwh.dim_produit p ON p.id_produit = l.id_produit
        JOIN dwh.dim_canal ca ON ca.canal = c.canal AND ca.mode_livraison = c.mode_livraison
        JOIN dwh.dim_promotion pr ON pr.code_promo = COALESCE(c.code_promo, 'Aucune')""",
    """CREATE TABLE dwh.fait_commandes AS
        SELECT c.id_commande, CAST(strftime(CAST(c.date_commande AS DATE), '%Y%m%d') AS INTEGER) AS date_key, k.client_key, ca.canal_key, pr.promo_key,
               COUNT(*) AS nb_lignes, SUM(l.montant) AS montant_ttc, MAX(c.frais_port) AS frais_port
        FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
        JOIN dwh.dim_client k ON k.id_client = c.id_client
        JOIN dwh.dim_canal ca ON ca.canal = c.canal AND ca.mode_livraison = c.mode_livraison
        JOIN dwh.dim_promotion pr ON pr.code_promo = COALESCE(c.code_promo, 'Aucune')
        GROUP BY ALL""",
    """CREATE TABLE dwh.fait_retours AS
        SELECT r.id_retour, r.id_ligne, CAST(strftime(CAST(r.date_retour AS DATE), '%Y%m%d') AS INTEGER) AS date_key,
               v.date_key AS date_vente_key, v.client_key, v.produit_key, v.canal_key, r.motif, r.montant_rembourse
        FROM src.retours r JOIN dwh.fait_ventes v USING (id_ligne)""",
    """CREATE TABLE dwh.fait_livraisons AS
        SELECT l.id_commande, ca.canal_key, t.transporteur_key,
               CAST(strftime(CAST(l.date_commande AS DATE), '%Y%m%d') AS INTEGER) AS date_commande_key,
               CAST(strftime(CAST(l.date_expedition AS DATE), '%Y%m%d') AS INTEGER) AS date_expedition_key,
               CAST(strftime(CAST(l.date_livraison AS DATE), '%Y%m%d') AS INTEGER) AS date_livraison_key,
               date_diff('day', CAST(l.date_commande AS DATE), CAST(l.date_expedition AS DATE)) AS delai_preparation_j,
               date_diff('day', CAST(l.date_expedition AS DATE), CAST(l.date_livraison AS DATE)) AS delai_transport_j,
               date_diff('day', CAST(l.date_commande AS DATE), CAST(l.date_livraison AS DATE)) AS delai_total_j,
               l.delai_promis_j, l.retard, l.colis_abime
        FROM src.livraisons l JOIN dwh.dim_canal ca ON ca.canal = l.canal AND ca.mode_livraison = l.mode_livraison
        JOIN dwh.dim_transporteur t ON t.transporteur = l.transporteur""",
    """CREATE TABLE dwh.fait_stock AS
        SELECT CAST(strftime(CAST(s.date AS DATE), '%Y%m%d') AS INTEGER) AS date_key, p.produit_key, s.stock_fin_jour, s.demande, s.rupture, s.point_de_commande
        FROM src.stock_quotidien s JOIN dwh.dim_produit p USING (id_produit)""",
]


def sql_de(table):
    """L'instruction de référence qui crée `dwh.<table>`."""
    return next(s for s in SQL_ETOILE if f"CREATE TABLE dwh.{table} AS" in s)


def construire_etoile(con):
    for s in SQL_ETOILE:
        con.executescript(s)
    return con


# ----------------------------------------------------------------------------------------------------- historiques simulés (dimensions à évolution lente)
def ecrire_historiques(D=DONNEES, seed=8101):
    """Versions d'adresse des clients (10 % ont déménagé) et reclassements de produits (8 produits au 1er juillet 2024). Graine fixe."""
    rng = np.random.default_rng(seed)
    cl = pd.read_csv(os.path.join(D, "clients.csv"), parse_dates=["date_inscription"])
    villes = sorted(cl["ville"].unique())
    poids = cl["ville"].value_counts().reindex(villes).to_numpy() / len(cl)
    lignes = []
    demenage = rng.random(len(cl)) < 0.10
    for i, r in enumerate(cl.itertuples()):
        deb = r.date_inscription
        debut_possible = max(deb, pd.Timestamp("2023-01-01")) + pd.Timedelta(days=60)
        jours = (pd.Timestamp("2025-10-01") - debut_possible).days
        if demenage[i] and jours > 30:
            quand = debut_possible + pd.Timedelta(days=int(rng.integers(0, jours)))
            p = poids.copy()
            p[villes.index(r.ville)] = 0
            ancienne = villes[rng.choice(len(villes), p=p / p.sum())]
            lignes.append((r.id_client, ancienne, deb, quand - pd.Timedelta(days=1), 0))
            lignes.append((r.id_client, r.ville, quand, pd.Timestamp("9999-12-31"), 1))
        else:
            lignes.append((r.id_client, r.ville, deb, pd.Timestamp("9999-12-31"), 1))
    h = pd.DataFrame(lignes, columns=["id_client", "ville", "date_debut", "date_fin", "courant"])
    for c in ["date_debut", "date_fin"]:
        h[c] = h[c].dt.strftime("%Y-%m-%d")
    h.to_csv(os.path.join(D, "ch01-historique-clients.csv"), index=False)

    pr = pd.read_csv(os.path.join(D, "produits.csv"))
    cats = sorted(pr["categorie"].unique())
    choisis = rng.choice(pr["id_produit"].to_numpy(), 8, replace=False)
    lignes = []
    for r in pr.itertuples():
        if r.id_produit in choisis:
            autres = [c for c in cats if c != r.categorie]
            ancienne = autres[int(rng.integers(0, len(autres)))]
            lignes.append((r.id_produit, ancienne, "2023-01-01", "2024-06-30", 0))
            lignes.append((r.id_produit, r.categorie, "2024-07-01", "9999-12-31", 1))
        else:
            lignes.append((r.id_produit, r.categorie, "2023-01-01", "9999-12-31", 1))
    pd.DataFrame(lignes, columns=["id_produit", "categorie", "date_debut", "date_fin", "courant"]).to_csv(os.path.join(D, "ch01-historique-produits.csv"), index=False)
    return h



# ----------------------------------------------------------------------------------------------------- figures (schémas dessinés, aucun logo)
def _plt():
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    import style
    style.setup()
    return plt, FancyBboxPatch, style


def _toile(plt, w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w * 10)
    ax.set_ylim(0, h * 10)
    ax.axis("off")
    ax.grid(False)
    return fig, ax


def _boite(ax, FBP, x, y, w, h, titre, corps=(), fc="#ffffff", ec="#52514e", tc="#0b0b0b", fs=9.5, lw=1.2, haut=True, ital=False):
    ax.add_patch(FBP((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.2", fc=fc, ec=ec, lw=lw))
    if titre:
        ax.text(x + w / 2, y + h - 2.2, titre, ha="center", va="top", fontsize=fs, fontweight="bold", color=tc)
    for i, l in enumerate(corps):
        ax.text(x + 1.6, y + h - 6.6 - i * 3.5, l, ha="left", va="top", fontsize=fs - 1.6, color="#2b2a28", style="italic" if ital else "normal")


def _fleche(ax, x0, y0, x1, y1, col="#52514e", txt=None, ls="-", lw=1.4, fs=8.2, dy=1.6, style="-|>"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle=style, color=col, lw=lw, ls=ls, shrinkA=0, shrinkB=0))
    if txt:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + dy, txt, ha="center", va="bottom", fontsize=fs, color=col)


def fig_couches(nom="ch01-couches.png"):
    plt, FBP, st = _plt()
    fig, ax = _toile(plt, 11.0, 4.6)
    cols = [("#e9e8e2", "Sources", ["base opérationnelle", "fichiers, API", "(hors de l'entrepôt)"]),
            ("#dbe9fb", "Zone d'arrivée", ["copie brute, datée", "aucune règle métier", "(src)"]),
            ("#cde2fb", "Entrepôt", ["nettoyé, modélisé", "schéma en étoile", "(dwh)"]),
            ("#fbe3d6", "Data marts", ["un sujet, un public", "agrégats et vues", "(mart)"]),
            ("#e1f3ea", "Usages", ["tableau de bord", "classeur Excel", "rapport, API"])]
    w, g, x = 19.0, 2.8, 2.0
    for i, (fc, t, l) in enumerate(cols):
        _boite(ax, FBP, x, 14, w, 21, t, l, fc=fc, fs=10.5)
        if i < 4:
            _fleche(ax, x + w + 0.2, 24.5, x + w + g - 0.2, 24.5)
        x += w + g
    ax.text(2, 41.5, "Chaque flèche est un traitement écrit, testé et rejouable (ETL ou ELT) : chapitre 2.", fontsize=9.2, color="#52514e", ha="left")
    ax.text(2, 7, "Plus on avance vers la droite : plus les données sont propres et décrites, moins elles sont détaillées par source, plus elles sont proches d'une décision.",
            fontsize=8.8, color="#52514e", ha="left")
    ax.text(2, 3.2, "On ne corrige jamais une donnée à la main dans l'entrepôt : on corrige la règle qui la fabrique.", fontsize=8.8, color="#52514e", ha="left")
    st.save(fig, nom)


def fig_etoile(nom="ch01-etoile.png"):
    plt, FBP, st = _plt()
    fig, ax = _toile(plt, 11.0, 7.4)
    centre = (34, 25, 32, 24)
    _boite(ax, FBP, *centre, "fait_ventes", ["une ligne de commande", "quantite, prix_unitaire", "montant_ttc, montant_ht", "cout_achat", "id_commande (dégénérée)"], fc="#fbe3d6", ec="#eb6834", lw=1.8, fs=10.5)
    dims = [("dim_date", ["date_key", "annee, trimestre, mois", "annee_mois, jour_semaine", "est_weekend"], 2, 52),
            ("dim_client", ["client_key", "ville, tranche_age", "canal_acquisition", "carte_fidelite"], 36, 52),
            ("dim_produit", ["produit_key", "nom_produit, categorie", "fournisseur", "prix_catalogue"], 70, 52),
            ("dim_canal", ["canal_key", "canal", "mode_livraison"], 2, 4),
            ("dim_promotion", ["promo_key", "code_promo", "famille_promo"], 70, 4)]
    for t, l, x, y in dims:
        _boite(ax, FBP, x, y, 28, 20, t, l, fc="#cde2fb", ec="#2a78d6", fs=10)
    cx, cy = 50, 37
    for (t, l, x, y) in dims:
        bx, by = x + 14, y + (0 if y > 40 else 20)
        tx = np.clip(bx, 38, 62)
        ty = 49 if y > 40 else 25
        ax.annotate("", xy=(tx, ty), xytext=(bx, by + (0 if y > 40 else 0)), arrowprops=dict(arrowstyle="-", color="#2a78d6", lw=1.3))
    ax.text(50, 73.5 + 0, "", fontsize=1)
    ax.text(50, 21.5, "5 clés étrangères (substituts) :\ndate_key, client_key, produit_key,\ncanal_key, promo_key", fontsize=8.3, color="#52514e", ha="center", va="top")
    ax.set_ylim(0, 76)
    st.save(fig, nom)


def fig_flocon(nom="ch01-flocon.png"):
    plt, FBP, st = _plt()
    fig, ax = _toile(plt, 11.0, 4.3)
    ax.text(12, 41, "Étoile : la dimension est à plat", fontsize=10.5, fontweight="bold", ha="left")
    _boite(ax, FBP, 2, 18, 20, 18, "fait_ventes", ["produit_key", "montant_ht"], fc="#fbe3d6", ec="#eb6834")
    _boite(ax, FBP, 30, 14, 24, 24, "dim_produit", ["produit_key", "nom_produit", "categorie", "famille", "fournisseur"], fc="#cde2fb", ec="#2a78d6")
    _fleche(ax, 22.2, 27, 29.8, 27, style="-")
    ax.text(66, 41, "Flocon : la dimension est normalisée", fontsize=10.5, fontweight="bold", ha="left")
    _boite(ax, FBP, 58, 18, 16, 18, "fait_ventes", ["produit_key", "montant_ht"], fc="#fbe3d6", ec="#eb6834", fs=9)
    _boite(ax, FBP, 79, 22, 17, 18, "dim_produit", ["produit_key", "nom_produit", "categorie_key"], fc="#cde2fb", ec="#2a78d6", fs=9)
    _boite(ax, FBP, 79, 0.5, 17, 16, "dim_categorie", ["categorie_key", "categorie", "famille"], fc="#cde2fb", ec="#2a78d6", fs=9)
    _fleche(ax, 74.2, 27, 78.8, 30, style="-")
    _fleche(ax, 87.5, 21.8, 87.5, 16.2, style="-")
    ax.text(100, 28, "une jointure\nde plus\npour chaque\nrequête", fontsize=8.6, color="#52514e", ha="left", va="center")
    ax.set_xlim(0, 118)
    st.save(fig, nom)


def fig_trois_chiffres(vals, nom="ch01-trois-chiffres.png"):
    plt, FBP, st = _plt()
    fig, ax = plt.subplots(figsize=(10.4, 3.8))
    noms = list(vals)[::-1]
    v = [vals[k] for k in noms]
    cols = [st.ORANGE if k.startswith("Requête") else st.BLEU for k in noms]
    ax.barh(noms, [x / 1000 for x in v], color=cols, height=0.6)
    for i, x in enumerate(v):
        ax.text(x / 1000 + 8, i, f"{x / 1000:,.0f} k€".replace(",", " "), va="center", fontsize=9.5, color=st.ENCRE)
    ax.set_xlim(0, max(v) / 1000 * 1.18)
    ax.set_xlabel("Chiffre d'affaires 2025 (k€)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Quatre « chiffres d'affaires 2025 » pour la même boutique, trois définitions et une erreur", loc="left", fontsize=10.5)
    st.save(fig, nom)


def fig_ca_categorie(df, nom="ch01-ca-categorie.png"):
    plt, FBP, st = _plt()
    fig, ax = plt.subplots(figsize=(10.4, 4.0))
    cols = [st.BLEU, st.ORANGE, st.AQUA, st.VIOLET, st.ROUGE, st.MUET]
    fin = {c: df[c].iloc[-1] / 1000 for c in df.columns}
    pos, dernier = {}, -99
    for c in sorted(fin, key=fin.get):
        pos[c] = max(fin[c], dernier + 2.6)
        dernier = pos[c]
    for c, couleur in zip(df.columns, cols):
        ax.plot(df.index, df[c] / 1000, color=couleur, lw=1.8, label=c)
        ax.text(len(df) - 0.6, pos[c], " " + c, va="center", fontsize=8.6, color=couleur)
    ax.set_xticks(range(0, len(df), 3))
    ax.set_xticklabels([df.index[i] for i in range(0, len(df), 3)], rotation=0, fontsize=8.4)
    ax.set_xlim(-0.5, len(df) + 3.2)
    ax.set_ylabel("CA HT mensuel (k€)")
    ax.set_title("Chiffre d'affaires hors taxe par catégorie et par mois, lu dans l'étoile", loc="left", fontsize=10.5)
    st.save(fig, nom)


def fig_types_faits(nom="ch01-types-faits.png"):
    plt, FBP, st = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.9))
    rng = np.random.default_rng(3)
    ax = axes[0]
    t = np.sort(rng.uniform(0, 30, 16))
    ax.vlines(t, 0, rng.uniform(0.4, 1.0, 16), color=st.BLEU, lw=2)
    ax.set_title("Transaction\n« une ligne par événement »", fontsize=9.6)
    ax.set_xlabel("temps (irrégulier)")
    ax.set_yticks([])
    ax = axes[1]
    t = np.arange(0, 30, 3)
    ax.vlines(t, 0, [0.8, 0.7, 0.9, 0.6, 0.55, 0.65, 0.4, 0.5, 0.45, 0.7], color=st.AQUA, lw=3)
    ax.set_title("Instantané périodique\n« une ligne par entité et par jour »", fontsize=9.6)
    ax.set_xlabel("temps (régulier)")
    ax.set_yticks([])
    ax = axes[2]
    ax.set_xlim(-1.2, 10)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.grid(False)
    jal = ["commande", "expédition", "livraison"]
    for ligne, n in enumerate([3, 2, 1]):
        y = 3.2 - ligne * 1.25
        for k in range(3):
            plein = k < n
            ax.add_patch(plt.Rectangle((0.2 + k * 3.2, y), 3.0, 0.8, fc=st.ORANGE if plein else "#ffffff", ec=st.ORANGE, lw=1.2, alpha=0.9 if plein else 1))
            if k == 0:
                ax.text(-0.1, y + 0.4, ["jour 3", "jour 2", "jour 1"][ligne], ha="right", va="center", fontsize=8, color=st.MUET)
            ax.text(1.7 + k * 3.2, y + 0.4, jal[k] if plein else "(vide)", ha="center", va="center", fontsize=8.2, color="#ffffff" if plein else st.MUET)
    ax.text(5, 0.25, "la même ligne se complète\nau fil des jalons", ha="center", fontsize=8.6, color=st.ENCRE2)
    ax.set_title("Cumulative (jalons)\n« une ligne par processus »", fontsize=9.6)
    fig.tight_layout()
    st.save(fig, nom)


def fig_grain(n, nom="ch01-grain.png"):
    plt, FBP, st = _plt()
    fig, ax = _toile(plt, 11.0, 3.2)
    lab = [("ligne de commande", n[0], "#fbe3d6", "#eb6834", 22), ("commande", n[1], "#cde2fb", "#2a78d6", 18), ("jour", n[2], "#e1f3ea", "#1baf7a", 14)]
    x = 3
    for i, (t, c, fc, ec, h) in enumerate(lab):
        y = 15 - h / 2
        ax.add_patch(FBP((x, y), 28, h, boxstyle="round,pad=0.0,rounding_size=1.2", fc=fc, ec=ec, lw=1.4))
        ax.text(x + 14, 15 + 2.2, t, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#0b0b0b")
        ax.text(x + 14, 15 - 2.6, f"{c:,} lignes".replace(",", " "), ha="center", va="center", fontsize=10, color="#2b2a28")
        if i < 2:
            _fleche(ax, x + 28.6, 15, x + 36.4, 15, col="#52514e")
            ax.text(x + 32.5, 18.2, "on agrège", ha="center", va="bottom", fontsize=8.6, color="#52514e")
        x += 36.5
    ax.text(3, 1.0, "Passer du grain fin au grain grossier est toujours possible ; l'inverse est impossible : le détail est perdu.", fontsize=9, color="#52514e")
    ax.set_ylim(0, 28)
    st.save(fig, nom)


def fig_scd2(nom="ch01-scd2.png"):
    plt, FBP, st = _plt()
    import matplotlib.dates as md
    fig, axes = plt.subplots(2, 1, figsize=(10.4, 4.6), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    d = lambda s: pd.Timestamp(s)
    debut, fin_obs = d("2023-01-01"), d("2025-12-31")
    achats = [d(x) for x in ["2023-03-12", "2023-09-30", "2024-02-18", "2024-05-02", "2024-11-21", "2025-04-09", "2025-10-14"]]
    dem = d("2024-08-15")
    ax = axes[0]
    ax.barh([0], [(fin_obs - debut).days], left=[md.date2num(debut)], height=0.5, color=st.ORANGE, alpha=0.9)
    ax.text(md.date2num(d("2024-03-01")), 0, "Type 1 : « Ville C » pour tout l'historique (l'ancienne valeur est écrasée)", ha="center", va="center", color="white", fontsize=9)
    ax.set_yticks([])
    ax.set_title("Un client qui change de ville le 15 août 2024 : ses sept achats sont-ils tous « de la Ville C » ?", loc="left", fontsize=10)
    ax = axes[1]
    ax.barh([0], [(dem - debut).days], left=[md.date2num(debut)], height=0.5, color=st.BLEU)
    ax.barh([0], [(fin_obs - dem).days], left=[md.date2num(dem)], height=0.5, color=st.AQUA)
    ax.text(md.date2num(d("2023-11-01")), 0, "version 1 : Ville A", ha="center", va="center", color="white", fontsize=9)
    ax.text(md.date2num(d("2025-03-01")), 0, "version 2 : Ville C", ha="center", va="center", color="white", fontsize=9)
    ax.axvline(md.date2num(dem), color=st.ENCRE, lw=1)
    ax.text(md.date2num(dem) + 6, 0.42, "déménagement (15 août 2024)", fontsize=8.4, va="bottom", ha="left")
    ax.set_yticks([])
    for a in axes:
        a.plot([md.date2num(x) for x in achats], [-0.42] * len(achats), "v", color=st.ENCRE, ms=6)
        a.set_ylim(-0.6, 0.8)
        a.grid(False)
    axes[1].text(md.date2num(d("2023-01-10")), -0.5, "▼ achats", fontsize=8.4, va="top")
    axes[1].xaxis_date()
    ticks = ["2023-01-01", "2023-07-01", "2024-01-01", "2024-07-01", "2025-01-01", "2025-07-01"]
    axes[1].set_xticks([md.date2num(d(x)) for x in ticks])
    axes[1].set_xticklabels(["janv. 2023", "juil. 2023", "janv. 2024", "juil. 2024", "janv. 2025", "juil. 2025"])
    axes[1].text(md.date2num(d("2023-11-01")), -1.0, "Type 2 : une ligne par version, avec sa période de validité ; chaque achat rejoint la version valide ce jour-là", fontsize=9, ha="left", va="top", clip_on=False)
    fig.tight_layout()
    st.save(fig, nom)


def fig_scd_effet(df, nom="ch01-scd-effet.png"):
    plt, FBP, st = _plt()
    fig, ax = plt.subplots(figsize=(10.4, 3.8))
    x = np.arange(len(df))
    ax.bar(x - 0.2, df["type1"] / 1000, 0.4, color=st.ORANGE, label="type 1 : ville actuelle")
    ax.bar(x + 0.2, df["type2"] / 1000, 0.4, color=st.BLEU, label="type 2 : ville au moment de l'achat")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index)
    ax.set_ylabel("CA TTC 2024 (k€)")
    ax.legend(loc="upper right")
    ax.grid(axis="x", visible=False)
    ax.set_title("Le même chiffre d'affaires 2024 par ville, selon le traitement de l'historique", loc="left", fontsize=10.5)
    st.save(fig, nom)


def fig_bus(nom="ch01-bus.png"):
    plt, FBP, st = _plt()
    procs = ["Ventes (lignes)", "Commandes (en-têtes)", "Retours", "Livraisons", "Stock quotidien", "Réapprovisionnements"]
    dims = ["Date", "Client", "Produit", "Canal", "Promotion", "Transporteur", "Fournisseur"]
    m = [[1, 1, 1, 1, 1, 0, 0], [1, 1, 0, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0, 0], [1, 0, 0, 1, 0, 1, 0], [1, 0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 1]]
    fig, ax = plt.subplots(figsize=(10.4, 3.9))
    ax.grid(False)
    for i, ligne in enumerate(m):
        for j, v in enumerate(ligne):
            ax.add_patch(plt.Rectangle((j, len(m) - 1 - i), 0.94, 0.88, fc=st.BLEU if v else "#f0efec", ec="white"))
            if v:
                ax.text(j + 0.47, len(m) - 1 - i + 0.44, "●", ha="center", va="center", color="white", fontsize=12)
    ax.set_xlim(0, len(dims))
    ax.set_ylim(0, len(m))
    ax.set_xticks([j + 0.47 for j in range(len(dims))])
    ax.set_xticklabels(dims, fontsize=9.2)
    ax.xaxis.tick_top()
    ax.set_yticks([len(m) - 1 - i + 0.44 for i in range(len(m))])
    ax.set_yticklabels(procs, fontsize=9.2)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.text(0.01, -0.02, "Colonnes : dimensions conformes (définies une fois, partagées). Lignes : processus mesurés (un fait chacun). « Réapprovisionnements » : décrit, non construit ici.", fontsize=8.4, color=st.ENCRE2)
    st.save(fig, nom)


def fig_parquet(taille, nom="ch01-parquet.png"):
    plt, FBP, st = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.8), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    s = taille.sort_values()
    couleurs = [st.ORANGE if i == "montant_ttc" else st.BLEU for i in s.index]
    ax.barh(s.index, s.values / 1024, color=couleurs, height=0.62)
    for i, v in enumerate(s.values):
        ax.text(v / 1024 + 4, i, f"{v / 1024:,.0f} ko".replace(",", " ") if v >= 1024 else "< 1 ko", va="center", fontsize=8.6)
    ax.set_xlim(0, s.max() / 1024 * 1.25)
    ax.set_xlabel("octets stockés par colonne dans le fichier Parquet (ko)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Lire une colonne : ne lire que sa part", loc="left", fontsize=10)
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.grid(False)
    for k, an in enumerate([2023, 2024, 2025]):
        pl = an == 2025
        ax.add_patch(plt.Rectangle((0.3 + k * 3.2, 2.2), 2.9, 2.6, fc=st.AQUA if pl else "#f0efec", ec=st.AQUA if pl else st.AXE, lw=1.5))
        ax.text(1.75 + k * 3.2, 3.5, f"annee={an}\n/…parquet", ha="center", va="center", fontsize=9, color="white" if pl else st.MUET)
    ax.text(5, 1.2, "WHERE annee = 2025 :\nseul le dossier annee=2025 est ouvert\n(élagage des partitions)", ha="center", va="center", fontsize=9, color=st.ENCRE2)
    ax.set_title("Partitionner : ne pas ouvrir les autres années", loc="left", fontsize=10)
    fig.tight_layout()
    st.save(fig, nom)


def fig_stockage_calcul(nom="ch01-stockage-calcul.png"):
    plt, FBP, st = _plt()
    fig, ax = _toile(plt, 11.0, 4.3)
    _boite(ax, FBP, 3, 28, 24, 12, "Utilisateurs", ["tableaux de bord,", "notebooks, API"], fc="#e9e8e2")
    for i, (t, c, u) in enumerate([("Calcul A", "#cde2fb", "équipe finance"), ("Calcul B", "#cde2fb", "équipe marketing"), ("Calcul C", "#cde2fb", "chargement de nuit")]):
        _boite(ax, FBP, 36, 32 - i * 10.5 + 5, 22, 8.5, t, [u], fc=c, ec="#2a78d6", fs=9.2)
        _fleche(ax, 27.2, 34, 35.8, 41.5 - i * 10.5 + 0.2, style="-|>", lw=1.0)
        _fleche(ax, 58.2, 41.2 - i * 10.5, 66.8, 25 + 2.0, style="-|>", lw=1.0)
    _boite(ax, FBP, 67, 10, 28, 24, "Stockage partagé", ["fichiers en colonnes,", "compressés, partitionnés", "(stockage d'objets)"], fc="#fbe3d6", ec="#eb6834")
    ax.text(3, 13, "Les calculs se démarrent, s'arrêtent\net se dimensionnent indépendamment :\non paie ce que l'on utilise.", fontsize=8.8, color="#52514e", va="top")
    ax.set_ylim(0, 46)
    st.save(fig, nom)


if __name__ == "__main__":
    h = ecrire_historiques()
    print(len(h), "versions de clients ;", int((h["courant"] == 0).sum()), "anciennes adresses")
