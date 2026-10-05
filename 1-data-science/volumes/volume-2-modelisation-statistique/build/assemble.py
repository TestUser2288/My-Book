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
    "00": "00-introduction",
    "01": "chapitre-1-regression-lineaire",
    "02": "chapitre-2-modeles-lineaires-generalises",
    "03": "chapitre-3-analyse-multivariee",
    "04": "chapitre-4-series-temporelles",
    "05": "chapitre-5-analyse-de-survie",
    "06": "chapitre-6-statistique-bayesienne",
    "07": "chapitre-7-inference-causale",
    "08": "chapitre-8-plans-experiences",
    "09": "chapitre-9-statistique-spatiale",
    "10": "cloture-projet-et-autoevaluation",
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
open("livre/volume-2-modelisation-statistique-complet.md", "w", encoding="utf-8").write("\n\n---\n\n".join(full))
print("total", sum(len(t.split()) for t in full), "mots")
