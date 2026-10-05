#!/usr/bin/env python3
"""Aperçu du texte VISIBLE d'un ou plusieurs fichiers (code `hide` retiré) et statistiques de code.

Usage : python3 build/preview.py [--text] sections/03-*.md ...
  sans option : tableau par fichier : mots, lignes de code visibles, lignes cachées,
                plus long bloc visible, lignes de sortie visibles
  --text      : écrit le texte visible sur la sortie standard
Cible (voir HANDOFF.md §5) : aucun bloc visible de plus de 15 lignes ; sorties visibles <= 12 lignes.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import strip_hidden  # noqa: E402

args = sys.argv[1:]
show = "--text" in args
files = [a for a in args if not a.startswith("--")]
tot = [0, 0, 0, 0]
if not show:
    print(f"{'fichier':44s} {'mots':>6s} {'code vis.':>9s} {'code caché':>10s} {'bloc max':>8s} {'sortie vis.':>11s} {'blocs>15':>8s}")
for f in files:
    raw = open(f, encoding="utf-8").read()
    vis = strip_hidden(raw)
    if show:
        print(vis); continue
    def stats(text):
        code = out = longest = nlong = 0
        infence = False; lang = ""; cur = 0
        for l in text.split("\n"):
            m = re.match(r"^```(\S*)", l)
            if m:
                if not infence:
                    infence = True; lang = m.group(1); cur = 0
                else:
                    infence = False
                    if lang in ("python", "r", "bash", "sql"):
                        longest = max(longest, cur); nlong += cur > 15
                continue
            if infence:
                if lang in ("python", "r", "bash", "sql"): code += 1; cur += 1
                elif lang == "text": out += 1
        return code, out, longest, nlong
    cv, ov, lv, nl = stats(vis)
    cr, _, _, _ = stats(raw)
    words = len(re.sub(r"```.*?```", "", vis, flags=re.S).split())
    print(f"{os.path.basename(f):44s} {words:6d} {cv:9d} {cr - cv:10d} {lv:8d} {ov:11d} {nl:8d}")
    tot[0] += words; tot[1] += cv; tot[2] += cr - cv; tot[3] += ov
if not show and len(files) > 1:
    print(f"{'TOTAL':44s} {tot[0]:6d} {tot[1]:9d} {tot[2]:10d} {'':8s} {tot[3]:11d}")
