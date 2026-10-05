"""Figures de la section 4.8 (complexité). Exécution : python build/fig_ch04c.py [nom ...]"""
import os
import sys
from timeit import repeat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
from style import *  # noqa

setup()


def temps(f, nombre):
    return min(repeat(f, number=nombre, repeat=5)) / nombre


def complexite():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw={"wspace": 0.32})

    # (a) croissance théorique
    ax = axes[0]
    n = np.linspace(1, 30, 300)
    courbes = [("log n", np.log2(n), AQUA, 29.5), ("n", n, BLEU, 29.5),
               ("n log n", n * np.log2(n), VIOLET, 29.5), ("n²", n**2, ORANGE, 29.5),
               ("2ⁿ", 2.0**n, ROUGE, 29.5)]
    for nom, y, c, _ in courbes:
        ax.plot(n, y, color=c, lw=1.8)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 3e9)
    ax.set_xlim(1, 33)
    # étiquettes directes (à droite des courbes, décalées pour éviter les collisions)
    pos = {"log n": 1.6, "n": 38, "n log n": 150, "n²": 1500, "2ⁿ": 1e9}
    for nom, y, c, _ in courbes:
        ax.text(30.6, pos[nom], nom, color=c, va="center", fontsize=10)
    ax.set_title("(a) Opérations selon la taille n (axe vertical logarithmique)")
    ax.set_xlabel("taille des données n")
    ax.set_ylabel("nombre d'opérations")

    # (b) mesure : liste contre ensemble
    ax = axes[1]
    tailles = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000]
    t_liste, t_set = [], []
    for taille in tailles:
        liste = list(range(taille))
        ensemble = set(liste)
        t_liste.append(temps(lambda: -1 in liste, 100))
        t_set.append(temps(lambda: -1 in ensemble, 100_000))
    ax.loglog(tailles, np.array(t_liste) * 1e6, color=ORANGE, marker="o", ms=4)
    ax.loglog(tailles, np.array(t_set) * 1e6, color=BLEU, marker="o", ms=4)
    ax.set_xlim(7e2, 1.2e6)
    ax.text(tailles[-1] * 1.25, t_liste[-1] * 1e6, "liste\n(linéaire)", color=ORANGE, va="center", fontsize=10)
    ax.text(tailles[-1] * 1.25, t_set[-1] * 1e6 * 1.0, "ensemble\n(constant)", color=BLEU, va="center", fontsize=10)
    ax.set_title("(b) Temps mesuré : chercher un élément absent")
    ax.set_xlabel("taille n")
    ax.set_ylabel("microsecondes (échelles log-log)")
    save(fig, "ch04-complexite.png")


if __name__ == "__main__":
    noms = sys.argv[1:] or [n for n, f in list(globals().items()) if callable(f) and f.__module__ == "__main__" and n not in ("setup", "save", "temps")]
    for n in noms:
        globals()[n]()
