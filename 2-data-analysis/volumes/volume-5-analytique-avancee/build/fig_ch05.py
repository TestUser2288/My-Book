"""Figures du chapitre 5 (volume V) : schémas dessinés et graphiques de résultats. Style commun : build/style.py."""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import AQUA, BLEU, ENCRE, ENCRE2, MUET, ORANGE, ROUGE, VIOLET, save, setup  # noqa: E402

CLAIR = {BLEU: "#e8f1fc", ORANGE: "#fdeee7", AQUA: "#e3f6ee", VIOLET: "#ebe8f6", ROUGE: "#fbe6e6", MUET: "#efeeea"}


def boite(ax, x, y, w, h, titre, sous="", couleur=BLEU, taille=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=CLAIR[couleur], ec=couleur, lw=1.4))
    ax.text(x + w / 2, y + h * (0.64 if sous else 0.5), titre, ha="center", va="center", fontsize=taille, color=ENCRE, weight="bold")
    if sous:
        ax.text(x + w / 2, y + h * 0.28, sous, ha="center", va="center", fontsize=taille - 1.8, color=ENCRE2)


def fleche(ax, x0, y0, x1, y1, couleur=ENCRE2, style="-|>", lw=1.4, rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=12, color=couleur, lw=lw, connectionstyle=f"arc3,rad={rad}", linestyle=ls))


def fig_harnais(nom="ch05-harnais.png"):
    setup()
    fig, ax = plt.subplots(figsize=(11.6, 4.6))
    ax.set_xlim(0, 11.8)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    boite(ax, 0.1, 3.0, 1.9, 1.0, "Question", "« CA 2024 par canal ? »", MUET, 9.5)
    boite(ax, 2.35, 3.0, 2.2, 1.0, "Prompt", "schéma, règles, exemples", VIOLET, 9.5)
    boite(ax, 4.9, 3.0, 1.9, 1.0, "Modèle", "boîte noire, non fiable", ORANGE, 9.5)
    ax.text(7.05, 4.25, "tout ce qui suit est du code ordinaire", fontsize=9, color=BLEU, style="italic")
    boite(ax, 7.05, 3.0, 2.1, 1.0, "1. Validation", "SELECT seul, tables\net colonnes connues", BLEU, 9.5)
    boite(ax, 9.45, 3.0, 2.2, 1.0, "2. Exécution bornée", "lecture seule,\nlimites de lignes et de temps", BLEU, 9.5)
    for x0, x1 in ((2.0, 2.35), (4.55, 4.9), (6.8, 7.05), (9.15, 9.45)):
        fleche(ax, x0, 3.5, x1, 3.5)
    boite(ax, 7.05, 0.9, 2.1, 1.1, "3. Contrôle", "référence ou\nrelecture humaine", BLEU, 9.5)
    boite(ax, 9.45, 0.9, 2.2, 1.1, "Résultat", "+ journal de l'essai", AQUA, 9.5)
    fleche(ax, 10.5, 3.0, 8.6, 2.0)
    fleche(ax, 9.15, 1.45, 9.45, 1.45)
    boite(ax, 2.7, 0.9, 3.5, 1.1, "Message d'erreur", "syntaxe, colonne inconnue,\nerreur d'exécution", ROUGE, 9.5)
    fleche(ax, 7.8, 3.0, 6.2, 1.7, couleur=ROUGE, rad=-0.1)
    fleche(ax, 3.9, 2.0, 3.5, 3.0, couleur=ROUGE, rad=0.1, ls="--")
    ax.text(0.1, 2.3, "au plus 3 essais,\npuis on s'arrête\net une personne reprend", fontsize=8.8, color=ROUGE, va="top")
    ax.text(0.1, 0.25, "Une requête refusée n'est pas un échec du système : c'est le système qui fonctionne.", fontsize=9, color=ENCRE2)
    save(fig, nom)


def fig_prompt(nom="ch05-anatomie-prompt.png"):
    setup()
    fig, ax = plt.subplots(figsize=(10.4, 3.6))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    couches = [("Rôle\net tâche", "« Écrivez UNE\nrequête SELECT\nen dialecte\nDuckDB »", VIOLET), ("Contexte", "qui lit,\nquel usage,\nquelle période", MUET),
               ("Schéma", "tables, colonnes,\ntypes,\ndescriptions,\nexemples de\nvaleurs", BLEU), ("Règles\nmétier", "définition du CA,\n« 60 noms pour\n120 produits »", AQUA),
               ("Exemples", "2 ou 3 paires\nquestion\n→ requête", ORANGE), ("Format\nde sortie", "« une requête,\nrien d'autre »", ROUGE)]
    w = 1.58
    for i, (t, s_, c) in enumerate(couches):
        ax.add_patch(FancyBboxPatch((0.1 + i * 1.7, 1.0), w, 1.95, boxstyle="round,pad=0.02,rounding_size=0.12", fc=CLAIR[c], ec=c, lw=1.4))
        ax.text(0.1 + i * 1.7 + w / 2, 2.62, t, ha="center", va="center", fontsize=9.5, color=ENCRE, weight="bold")
        ax.text(0.1 + i * 1.7 + w / 2, 1.78, s_, ha="center", va="center", fontsize=8.2, color=ENCRE2, linespacing=1.3)
    ax.text(5.2, 3.3, "Un prompt est un document : on y met ce qu'un nouveau collègue devrait savoir pour répondre juste", ha="center", fontsize=10, color=ENCRE)
    ax.annotate("", xy=(10.2, 0.8), xytext=(0.1, 0.8), arrowprops=dict(arrowstyle="-|>", color=ENCRE2))
    ax.text(5.2, 0.4, "plus de contexte utile = meilleures réponses, mais plus de jetons à payer, et une limite de fenêtre", ha="center", fontsize=9, color=ENCRE2)
    save(fig, nom)


def fig_temperature(logits, nom="ch05-temperature.png"):
    """Probabilités du jeton suivant pour trois températures, à partir des scores réels du petit modèle (enregistrés)."""
    setup()
    jetons = [j.replace("\n", "⏎") for j in logits["jetons"]][:8]
    s = np.array(logits["scores"][:8])
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.5), sharey=True)
    for ax, T, c in zip(axes, (0.3, 1.0, 2.0), (BLEU, VIOLET, ORANGE)):
        p = np.exp((s - s.max()) / T)
        p = p / p.sum()
        ax.barh(range(len(p))[::-1], p * 100, color=c, height=0.65)
        ax.set_yticks(range(len(p))[::-1])
        ax.set_yticklabels([f"« {j.strip() or j} »" for j in jetons], fontsize=9)
        ax.set_title(f"température {str(T).replace('.', ',')}", fontsize=10, loc="left")
        for yi, v in zip(range(len(p))[::-1], p * 100):
            ax.text(v + 1, yi, f"{v:.0f}".replace(".", ","), va="center", fontsize=8.5, color=ENCRE2)
        ax.set_xlim(0, 105)
        ax.grid(False)
    fig.subplots_adjust(bottom=0.2)
    fig.supxlabel("probabilité du jeton suivant (%, parmi les 8 plus probables ; même échelle sur les trois graphiques)", fontsize=9, color=ENCRE2)
    save(fig, nom)


def fig_jetons(lignes, nom="ch05-jetons.png"):
    """lignes : liste de (libellé, nombre de jetons) ; échelle logarithmique."""
    setup()
    fig, ax = plt.subplots(figsize=(10.2, 3.5))
    lab = [l for l, _ in lignes][::-1]
    val = [v for _, v in lignes][::-1]
    cols = [BLEU if v < 8000 else (ORANGE if v < 200000 else ROUGE) for v in val]
    ax.barh(lab, val, color=cols, height=0.6)
    ax.set_xscale("log")
    ax.axvline(8000, color=MUET, lw=1, ls="--")
    ax.text(8000 * 1.1, len(lab) - 0.45, "ordre de grandeur d'une fenêtre de\ncontexte modeste (8 000 jetons)", fontsize=8.5, color=ENCRE2, va="top")
    for y, v in enumerate(val):
        ax.text(v * 1.12, y, f"{v:,.0f}".replace(",", " ") + " jetons", va="center", fontsize=9, color=ENCRE)
    ax.set_xlim(20, 4e8)
    ax.set_xlabel("jetons (échelle logarithmique)")
    ax.grid(False)
    save(fig, nom)


def fig_statuts(tab, nom="ch05-statuts.png"):
    """tab : DataFrame indexé par la source, colonnes = statuts (comptes)."""
    setup()
    ordre = ["juste", "exécutée mais fausse", "erreur d'exécution", "refusée"]
    couleurs = {"juste": AQUA, "exécutée mais fausse": ROUGE, "erreur d'exécution": ORANGE, "refusée": BLEU}
    tab = tab.reindex(columns=ordre, fill_value=0)
    fig, ax = plt.subplots(figsize=(10.4, 0.75 * len(tab) + 1.9))
    gauche = np.zeros(len(tab))
    for st in ordre:
        v = tab[st].to_numpy()
        ax.barh(range(len(tab))[::-1], v, left=gauche, color=couleurs[st], height=0.55, label=st)
        for y, (g, x) in enumerate(zip(gauche, v)):
            if x > 0:
                ax.text(g + x / 2, len(tab) - 1 - y, str(int(x)), ha="center", va="center", color="white", fontsize=10, weight="bold")
        gauche = gauche + v
    ax.set_yticks(range(len(tab))[::-1])
    ax.set_yticklabels(tab.index, fontsize=9.5)
    ax.set_xlabel("nombre de questions (sur 20)")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.12), fontsize=9)
    ax.set_xticks(range(0, 21, 4))
    ax.grid(False)
    save(fig, nom)


def fig_synth(reel, jeux, nom="ch05-synthetique.png"):
    """Compare réel et jeux synthétiques : montants, prix unitaires, saisonnalité."""
    setup()
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.6))
    ax = axes[0]
    bins = np.linspace(0, 400, 41)
    ax.hist(reel["montant"].clip(upper=400), bins=bins, density=True, color=MUET, alpha=0.55, label="réel")
    for (nom_j, df), c in zip(jeux.items(), (BLEU, ORANGE)):
        ax.hist(df["montant"].clip(upper=400), bins=bins, density=True, histtype="step", color=c, lw=1.8, label=nom_j)
    ax.set_title("montant d'une ligne (€)", fontsize=10, loc="left")
    ax.legend(fontsize=8)
    ax.set_yticks([])
    ax = axes[1]
    pr = reel["prix_unitaire"].round(2)
    ax.hist(pr, bins=np.linspace(0, 150, 61), density=True, color=MUET, alpha=0.55)
    for (nom_j, df), c in zip(jeux.items(), (BLEU, ORANGE)):
        ax.hist(df["prix_unitaire"], bins=np.linspace(0, 150, 61), density=True, histtype="step", color=c, lw=1.8)
    ax.set_title("prix unitaire (€)", fontsize=10, loc="left")
    ax.set_yticks([])
    ax = axes[2]
    m = np.arange(1, 13)
    ax.plot(m, [100 * (reel.drop_duplicates("id_commande")["date_commande"].dt.month == k).mean() for k in m], color=MUET, lw=3, label="réel")
    for (nom_j, df), c in zip(jeux.items(), (BLEU, ORANGE)):
        ax.plot(m, [100 * (df.drop_duplicates("id_commande")["date_commande"].dt.month == k).mean() for k in m], color=c, lw=1.8, marker="o", ms=3)
    ax.set_xticks(m)
    ax.set_title("part des commandes par mois (%)", fontsize=10, loc="left")
    ax.set_ylim(0, None)
    save(fig, nom)
