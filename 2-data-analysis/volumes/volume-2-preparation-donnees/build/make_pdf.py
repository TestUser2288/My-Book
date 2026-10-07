#!/usr/bin/env python3
"""Construit le PDF du LIVRE ou du CAHIER du volume (pandoc + xelatex).

Usage : python3 build/make_pdf.py [livre|cahier]      (défaut : livre)
Lit build/pdf/volume.json (sources, sorties, texte de la page de titre).
Prérequis : pandoc, xelatex, texlive-lang-french, texlive-latex-extra, polices TeX Gyre + DejaVu.
Les emojis des callouts sont convertis en boîtes colorées par build/pdf/callouts.lua ;
le style des titres (chapitres, sections, sous-sections) est dans build/pdf/header.tex.
"""
import json, os, subprocess, sys, tempfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
vol = json.load(open("build/pdf/volume.json", encoding="utf-8"))
nom = sys.argv[1] if len(sys.argv) > 1 else "livre"
cfg = {**{k: v for k, v in vol.items() if not isinstance(v, dict)}, **vol[nom]}   # le livre/cahier surcharge
src, out = cfg["source"], cfg["out"]

text = open(src, encoding="utf-8").read()
# la page de titre est générée par les métadonnées : on commence au premier titre voulu
i = text.find(cfg["start_heading"])
if i > 0:
    text = text[i:]
text = text.replace("<!--sortie-->\n", "")           # commentaires HTML inutiles en PDF
tmp = tempfile.mkdtemp(prefix="pdfbuild_")
md = os.path.join(tmp, "livre.md")
macros = "".join("\\newcommand{\\Vol%s}{%s}\n" % (k, cfg[v]) for k, v in
                 [("Serie", "serie"), ("Nom", "nom"), ("LigneA", "ligneA"), ("LigneB", "ligneB"), ("Pied", "pied")])
header = os.path.join(tmp, "header.tex")
open(header, "w", encoding="utf-8").write(macros + open("build/pdf/header.tex", encoding="utf-8").read())
open(md, "w", encoding="utf-8").write(text)

meta = {
    "title": cfg["title"], "subtitle": cfg["subtitle"], "author": cfg["author"], "lang": "fr",
    "documentclass": "book", "classoption": "11pt,openany,a4paper", "geometry": "margin=2.4cm",
    "mainfont": "TeX Gyre Pagella", "mathfont": "TeX Gyre Pagella Math",
    "monofont": "DejaVu Sans Mono", "monofontoptions": "Scale=0.84",
    "linkcolor": "bleu", "urlcolor": "bleu", "colorlinks": "true", "toc-depth": "2",
}
cmd = ["pandoc", md, "-f", "markdown+tex_math_dollars-smart+lists_without_preceding_blankline", "-o", out,
       "--pdf-engine=xelatex", "--toc", "--top-level-division=chapter", "--resource-path=.",
       "--lua-filter=build/pdf/callouts.lua", "-H", header, "--highlight-style=tango"]
for k, v in meta.items():
    cmd += ["-V", f"{k}={v}"]
print(f"[{nom}]", src, "->", out)
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout[-2000:], r.stderr[-4000:])
sys.exit(r.returncode)
