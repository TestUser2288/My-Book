#!/usr/bin/env python3
"""Assemble les fichiers de sections en chapitres puis en volume complet.
Usage : assemble.py   (lit sections/*.md triés par nom)"""
import glob, os, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
files = sorted(glob.glob("sections/*.md"))
groups = {}
for f in files:
    name = os.path.basename(f)
    m = re.match(r"(\d\d)-", name)
    groups.setdefault(m.group(1), []).append(f)
titles = {
    "00": "00-avant-propos",
    "01": "chapitre-1-mathematiques",
    "02": "chapitre-2-probabilites",
    "03": "chapitre-3-statistique",
    "04": "chapitre-4-programmation",
    "05": "chapitre-5-sql",
    "06": "chapitre-6-outils",
    "07": "cloture-projet-et-autoevaluation",
}
os.makedirs("livre", exist_ok=True)
full = []
for k in sorted(groups):
    parts = [open(f, encoding="utf-8").read().rstrip() + "\n" for f in groups[k]]
    text = "\n\n".join(parts)
    out = f"livre/{titles.get(k, k)}.md"
    open(out, "w", encoding="utf-8").write(text)
    full.append(text)
    print("écrit", out, len(text.split()), "mots")
open("livre/volume-1-fondations-complet.md", "w", encoding="utf-8").write("\n\n---\n\n".join(full))
print("total", sum(len(t.split()) for t in full), "mots")
