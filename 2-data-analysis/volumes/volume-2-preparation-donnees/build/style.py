"""Style commun des figures du livre (palette validée, traits fins, grilles discrètes)."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Palette catégorielle (ordre fixe) — bleu, orange, aqua, violet, rouge
BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
ENCRE, ENCRE2, MUET = "#0b0b0b", "#52514e", "#898781"
GRILLE, AXE, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"

# Rampe séquentielle bleue (clair -> foncé) et divergente bleu <-> rouge, milieu gris
SEQ = LinearSegmentedColormap.from_list(
    "seq_bleu", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
DIV = LinearSegmentedColormap.from_list(
    "div_bleu_rouge", ["#256abf", "#6da7ec", "#f0efec", "#ee8a85", "#c93a39"]
)

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")


def setup():
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 200,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.edgecolor": AXE,
            "axes.labelcolor": ENCRE2,
            "axes.titlecolor": ENCRE,
            "axes.titlesize": 11,
            "axes.titleweight": "regular",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRILLE,
            "grid.linewidth": 0.6,
            "xtick.color": MUET,
            "ytick.color": MUET,
            "text.color": ENCRE2,
            "lines.linewidth": 2.0,
            "legend.frameon": False,
        }
    )


def save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("figure :", name)
