"""Outils du projet du volume V (cahier, chapitre 10) : « un pipeline de reporting automatisé alimentant un tableau de bord ».

Le projet ASSEMBLE les chapitres : l'entrepôt en étoile (chapitre 1), le pipeline de chargement et ses contrôles (chapitre 2, `outils_ch02`), une prévision (chapitre 3)
et une alerte de gestion (esprit du chapitre 4). Ce module ne contient que ce que les autres chapitres n'ont pas : une seconde table de faits (livraisons), l'historique
2023-2024, les indicateurs en SQL, la prévision de janvier 2026, le rendu de la page du tableau de bord et la diffusion par e-mail à un serveur de TEST local.
Tout est simulé (jeux du volume III + dépôt de fichiers du chapitre 2) ; rien n'est écrit dans le dépôt (tout va dans un dossier temporaire).
"""
import base64
import io
import os
import smtplib
import sys
from email.message import EmailMessage

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outils_ch02 as P  # noqa: E402

DONNEES = P.DONNEES
TVA = 1.2   # TVA fictive de 20 %

DDL_PLUS = """
CREATE TABLE dim_date(date DATE PRIMARY KEY, mois VARCHAR, annee INTEGER, num_mois INTEGER);
CREATE TABLE fait_livraison(id_commande INTEGER PRIMARY KEY, date_commande DATE, transporteur VARCHAR, mode_livraison VARCHAR,
                            date_expedition DATE, date_livraison DATE, delai_promis_j INTEGER, retard INTEGER);
"""

VUE_KPI = """
CREATE OR REPLACE VIEW v_kpi_mois AS
SELECT strftime(l.date_commande, '%Y-%m') AS mois,
       count(DISTINCT l.id_commande)                                   AS commandes,
       sum(l.montant) / 1.2                                            AS ca_ht,
       sum(l.montant) / 1.2 - sum(l.quantite * p.cout_achat)           AS marge,
       (sum(l.montant) / 1.2) / count(DISTINCT l.id_commande)          AS panier_ht,
       sum(CASE WHEN l.canal = 'Site' THEN l.montant ELSE 0 END) / sum(l.montant) AS part_site
FROM fait_ligne l JOIN dim_produit p USING (id_produit)
GROUP BY 1
"""

VUE_RETARD = """
CREATE OR REPLACE VIEW v_retard_mois AS
SELECT strftime(date_commande, '%Y-%m') AS mois, count(*) AS livraisons, avg(retard) AS taux_retard
FROM fait_livraison GROUP BY 1
"""


def ouvrir(donnees=DONNEES):
    """Entrepôt neuf : dimensions du chapitre 2, `dim_date`, `fait_livraison` et les deux vues d'indicateurs. Renvoie (connexion, ensemble des clients connus)."""
    con = P.nouvel_entrepot("projet")
    clients = P.charger_dimensions(con, donnees)
    con.execute(DDL_PLUS)
    con.execute("INSERT INTO dim_date SELECT CAST(d AS DATE), strftime(d, '%Y-%m'), year(d), month(d) "
                "FROM generate_series(DATE '2023-01-01', DATE '2026-12-31', INTERVAL 1 DAY) t(d)")
    con.execute(VUE_KPI)
    con.execute(VUE_RETARD)
    return con, clients


def charger_historique(con, donnees=DONNEES):
    """Charge une fois l'historique 2023-2024 (une seule livraison « historique ») ; relançable (fusion sur id_ligne)."""
    cmd = pd.read_csv(os.path.join(donnees, "commandes.csv"))
    lig = pd.read_csv(os.path.join(donnees, "lignes_commande.csv"))
    h = lig.merge(cmd, on="id_commande")
    h = h[h["date_commande"] < "2025-01-01"][P.COLS].assign(fichier="historique", date_commande=lambda x: pd.to_datetime(x["date_commande"]))
    con.register("hist", h)
    con.execute("INSERT OR REPLACE INTO fait_ligne SELECT id_ligne, id_commande, date_commande, id_client, canal, id_produit, quantite, montant, fichier FROM hist")
    con.unregister("hist")
    return len(h)


def charger_livraisons(con, donnees=DONNEES):
    """Charge `livraisons.csv` avec ses contrôles : clé unique, dates cohérentes (commande <= expédition <= livraison). Renvoie (lignes chargées, rejetées)."""
    d = pd.read_csv(os.path.join(donnees, "livraisons.csv"), parse_dates=["date_commande", "date_expedition", "date_livraison"])
    cols = ["id_commande", "date_commande", "transporteur", "mode_livraison", "date_expedition", "date_livraison", "delai_promis_j", "retard"]
    ok = ~d["id_commande"].duplicated() & (d["date_expedition"] >= d["date_commande"]) & (d["date_livraison"] >= d["date_expedition"])
    con.register("liv", d[ok][cols])
    con.execute("INSERT OR REPLACE INTO fait_livraison SELECT * FROM liv")
    con.unregister("liv")
    return int(ok.sum()), int((~ok).sum())


def indicateurs(con):
    """Les indicateurs mensuels, calculés UNE fois, dans la vue SQL (jointure avec le retard de livraison)."""
    return con.execute("SELECT k.*, r.taux_retard FROM v_kpi_mois k LEFT JOIN v_retard_mois r USING (mois) ORDER BY mois").df()


def prevoir_mois_suivant(commandes, h=12):
    """Prévision du mois suivant : même mois de l'an dernier x croissance des 12 derniers mois, avec une fourchette tirée des erreurs passées (méthode simple du chapitre 3).

    `commandes` : série mensuelle (index = 'AAAA-MM', au moins 36 mois pour estimer l'erreur sur 12 mois). Renvoie (prévision, bas, haut, erreurs relatives passées)."""
    s = commandes.astype(float).reset_index(drop=True)

    def prevoir(o):
        g = s.iloc[o - 12:o].sum() / s.iloc[o - 24:o - 12].sum()
        return s.iloc[o - 12] * g

    n = len(s)
    erreurs = np.array([s.iloc[o] / prevoir(o) - 1 for o in range(max(24, n - h), n)])
    p = prevoir(n)
    bas, haut = np.quantile(erreurs, [0.1, 0.9])
    return p, p * (1 + bas), p * (1 + haut), erreurs


def fr(x, nd=1, signe=False):
    s = f"{x:+,.{nd}f}" if signe else f"{x:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")


def page_tableau_de_bord(kpi, prevision, alertes, statuts, titre="Reporting mensuel de la boutique", mois_edition=None):
    """HTML d'UNE page (cartes + trois graphiques + alertes + statut du pipeline). `kpi` : indicateurs mensuels ; `prevision` : (p, bas, haut) pour le mois suivant ;
    `alertes` : liste de (gravité, message) ; `statuts` : dict mois -> statut du dernier chargement. Les graphiques sont incorporés (image encodée) : un seul fichier."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from style import setup, BLEU, ORANGE, MUET, ENCRE, ENCRE2
    setup()
    k = kpi.copy()
    k["annee"], k["m"] = k["mois"].str[:4].astype(int), k["mois"].str[5:].astype(int)
    a25, a24 = k[k["annee"] == 2025].set_index("m"), k[k["annee"] == 2024].set_index("m")
    mois_edition = mois_edition or a25.index.max()
    cur = a25.loc[mois_edition]
    prec = a24.loc[mois_edition]
    fig, ax = plt.subplots(1, 3, figsize=(11.2, 3.1), gridspec_kw={"width_ratios": [1.5, 1.2, 0.9]})
    x = np.arange(1, 13)
    ax[0].plot(x, a24["ca_ht"].reindex(x) / 1000, color=MUET, lw=1.6, label="2024")
    ax[0].plot(a25.index, a25["ca_ht"] / 1000, color=BLEU, lw=2.2, label="2025")
    ax[0].set_xticks(x)
    ax[0].set_title("CA hors taxe par mois (k€)", loc="left", fontsize=10)
    ax[0].legend(frameon=False, fontsize=8, loc="upper left")
    ax[1].plot(a25.index, a25["taux_retard"] * 100, color=ORANGE, lw=2.2, marker="o", ms=3.5)
    ax[1].set_xticks(x)
    ax[1].set_ylim(0, None)
    ax[1].set_title("Livraisons en retard (%)", loc="left", fontsize=10)
    p, bas, haut = prevision
    ax[2].bar(["janv. 2025\n(réel)", "janv. 2026\n(prévu)"], [a25.loc[1, "commandes"], p], color=[MUET, BLEU], width=0.55)
    ax[2].errorbar([1], [p], yerr=[[p - bas], [haut - p]], color=ENCRE, capsize=4, lw=1.4)
    ax[2].set_title("Commandes : janvier", loc="left", fontsize=10)
    ax[2].tick_params(axis="x", labelsize=8)
    for a in ax:
        a.grid(axis="x", visible=False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130)
    plt.close(fig)
    img = base64.b64encode(buf.getvalue()).decode()

    def carte(libelle, valeur, delta=None):
        d = f"<div class='d'>{delta}</div>" if delta else ""
        return f"<div class='c'><div class='l'>{libelle}</div><div class='v'>{valeur}</div>{d}</div>"

    ev = lambda a, b: fr((a / b - 1) * 100, 0, signe=True) + " % sur un an"
    cartes = "".join([carte("CA hors taxe", fr(cur["ca_ht"] / 1000, 1) + " k€", ev(cur["ca_ht"], prec["ca_ht"])),
                      carte("Marge brute", fr(cur["marge"] / 1000, 1) + " k€", ev(cur["marge"], prec["marge"])),
                      carte("Commandes", fr(cur["commandes"], 0), ev(cur["commandes"], prec["commandes"])),
                      carte("Panier moyen HT", fr(cur["panier_ht"], 1) + " €"),
                      carte("Livraisons en retard", fr(cur["taux_retard"] * 100, 1) + " %")])
    al = "".join(f"<li><b class='{g.lower()}'>{g}</b> {m}</li>" for g, m in alertes) or "<li>Aucune alerte.</li>"
    st = "".join(f"<span class='s {'ok' if v == 'SUCCES' else 'ko'}'>{m[5:]} {'✔' if v == 'SUCCES' else '✘'}</span>" for m, v in statuts.items())
    return f"""<!doctype html><html lang="fr"><meta charset="utf-8"><title>{titre}</title><style>
body{{font-family:DejaVu Sans,sans-serif;margin:0;padding:16px 20px;color:#0b0b0b;background:#fcfcfb;width:1060px}}
h1{{font-size:19px;margin:0}} .sous{{color:#52514e;font-size:12px;margin:2px 0 12px}}
.k{{display:flex;gap:10px}} .c{{border:1px solid #c3c2b7;border-radius:6px;padding:8px 12px;width:178px;background:#fff}}
.l{{font-size:11px;color:#52514e}} .v{{font-size:22px;font-weight:bold;margin-top:2px}} .d{{font-size:11px;color:#52514e}}
img{{width:1060px;margin-top:10px}} ul{{font-size:12px;margin:6px 0 8px 18px;padding:0}} .critique,.attention{{margin-right:6px}} .critique{{color:#b3261e}} .attention{{color:#9a5b00}}
.s{{display:inline-block;font-size:11px;border:1px solid #c3c2b7;border-radius:4px;padding:1px 6px;margin-right:4px}} .ok{{color:#1a6b2f}} .ko{{color:#b3261e;font-weight:bold}}
h2{{font-size:13px;margin:8px 0 0}}</style>
<h1>{titre}</h1><div class="sous">Mois : {mois_edition:02d}/2025 · données simulées · produit par le pipeline, sans intervention manuelle</div>
<div class="k">{cartes}</div><img src="data:image/png;base64,{img}">
<h2>Alertes</h2><ul>{al}</ul><h2>Chargements 2025</h2><div>{st}</div></html>"""


def diffuser(html, hote, port, objet, corps, destinataires=("gerante@boutique.example",), expediteur="rapports@boutique.example"):
    """Envoie la page en pièce jointe à un serveur SMTP LOCAL de test (jamais à un vrai serveur). Renvoie le nombre d'octets envoyés."""
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = objet, expediteur, ", ".join(destinataires)
    msg.set_content(corps)
    msg.add_attachment(html, subtype="html", filename="tableau_de_bord.html")   # texte : encodé en UTF-8 par la bibliothèque
    with smtplib.SMTP(hote, port, timeout=10) as s:
        s.send_message(msg)
    return len(msg.as_bytes())
