"""Figures du chapitre 4 (documentation et dictionnaires) ; appelées par des blocs cachés du livre et du cahier."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style as S
import outils_ch04 as O

S.setup()


def manque(valeur="211 434 €"):
    """le chiffre au centre, les questions que la collègue se pose autour"""
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.axis("off"); ax.set_xlim(-5.6, 5.6); ax.set_ylim(-2.4, 2.4)
    ax.add_patch(FancyBboxPatch((-1.3, -0.5), 2.6, 1.0, boxstyle="round,pad=0.02,rounding_size=0.12", fc=S.BLEU, ec="none"))
    ax.text(0, 0.12, valeur, ha="center", va="center", fontsize=15, color="white", weight="bold")
    ax.text(0, -0.25, "chiffre d'affaires, T4, Site", ha="center", va="center", fontsize=8.5, color="white")
    q = [("De quelle source ?", -3.6, 1.7), ("Extraite quand ?", 0.0, 2.0), ("TTC ou HT ?", 3.6, 1.7), ("Quelles lignes écartées ?", -3.6, -1.7),
         ("Quelle définition du « T4 » ?", 0.0, -2.0), ("Avec quelle version du code ?", 3.6, -1.7)]
    for t, x, y in q:
        ax.add_patch(FancyBboxPatch((x - 1.6, y - 0.25), 3.2, 0.5, boxstyle="round,pad=0.02,rounding_size=0.1", fc="white", ec=S.AXE, lw=1.0))
        ax.text(x, y, t, ha="center", va="center", fontsize=8.6, color=S.ENCRE)
        ax.annotate("", xy=(0.0 + (x * 0.2), 0.55 * (1 if y > 0 else -1)), xytext=(x * 0.78, y - 0.28 * (1 if y > 0 else -1)),
                    arrowprops=dict(arrowstyle="-", color=S.AXE, lw=0.9, ls="--"))
    S.save(fig, "ch04-ce-qui-manque.png")


def cascade(table, nom="ch04-journal-crm.png"):
    """effectif après chaque étape du journal"""
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    etapes = ["lecture", "1. lignes\nde test", "2. e-mails", "3. téléphones", "4. doublons\nd'e-mail"]
    apres = list(table["apres"])
    couleurs = [S.MUET] + [S.ORANGE if r > 0 else S.BLEU for r in table["retirees"].iloc[1:]]
    b = ax.bar(range(len(apres)), apres, color=couleurs, width=0.62)
    for i, v in enumerate(apres):
        ax.text(i, v + 60, f"{v:,}".replace(",", " "), ha="center", fontsize=9, color=S.ENCRE)
        if i > 0 and table["retirees"].iloc[i] > 0:
            ax.text(i, v / 2, f"−{int(table['retirees'].iloc[i])}", ha="center", color="white", fontsize=10, weight="bold")
        if i > 0 and table["modifiees"].iloc[i] > 0:
            ax.text(i, v / 2, f"{int(table['modifiees'].iloc[i]):,}".replace(",", " ") + "\nmodifiées", ha="center", color="white", fontsize=8.5)
    ax.set_xticks(range(len(apres))); ax.set_xticklabels(etapes, fontsize=8.5)
    ax.set_ylabel("lignes"); ax.set_ylim(0, max(apres) * 1.14); ax.grid(axis="x", visible=False)
    ax.set_title("Effectif du CRM après chaque étape du nettoyage", loc="left")
    S.save(fig, nom)


def capture_dico(dico, nom="ch04-dictionnaire-capture.png"):
    """page HTML du dictionnaire, rendue par Chromium : vraie capture d'une page produite localement"""
    import html
    import outils_capture as C
    cols = ["colonne", "libelle", "unite", "type", "manquants_pct", "sensibilite"]
    ent = ["Colonne", "Libellé", "Unité", "Type", "Manquants (%)", "Sensibilité"]
    corps = "".join("<tr>" + "".join(f"<td>{html.escape('' if x is None or x != x else str(x))}</td>" for x in r) + "</tr>" for r in dico[cols].itertuples(index=False))
    page = f"""<html><body style="font-family:DejaVu Sans,sans-serif;margin:16px;color:#0b0b0b;background:#fcfcfb">
<h3 style="margin:0 0 4px 0">Dictionnaire de données : profil_clients</h3><div style="color:#52514e;font-size:12px;margin-bottom:10px">Version 1 · 6 000 lignes · propriétaire : analyse</div>
<table style="border-collapse:collapse;font-size:12.5px;width:100%"><thead><tr style="background:#2a78d6;color:white">{''.join(f'<th style="text-align:left;padding:5px 8px">{e}</th>' for e in ent)}</tr></thead>
<tbody>{corps.replace('<td>', '<td style="padding:4px 8px;border-bottom:1px solid #e1e0d9">')}</tbody></table></body></html>"""
    out = os.path.join(S.FIG_DIR, nom)
    C.capturer(page, out, largeur=980, hauteur=300, html=True)
    print("figure :", nom)


def lignage_tables(L, surligne=None):
    L.dessiner("ch04-lignage-tables.png", titre="D'où vient le message à la gérante ?", surligne=surligne, largeur=10.4, hauteur=4.0)


def lignage_colonnes(L, surligne=None):
    L.dessiner("ch04-lignage-colonnes.png", titre="D'où vient le panier moyen ? Lignage au niveau des colonnes", surligne=surligne, largeur=10.4, hauteur=4.2)
