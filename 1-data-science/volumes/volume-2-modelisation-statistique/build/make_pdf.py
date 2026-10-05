#!/usr/bin/env python3
"""Construit le PDF du volume à partir de livre/volume-1-fondations-complet.md (pandoc + xelatex).

Usage : python3 build/make_pdf.py [source.md] [sortie.pdf]
Prérequis : pandoc, xelatex, texlive-lang-french, texlive-latex-extra, polices TeX Gyre + DejaVu.
Les emojis des callouts sont convertis en boîtes colorées par build/pdf/callouts.lua.
"""
import json, os, re, subprocess, sys, tempfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
vol = json.load(open("build/pdf/volume.json", encoding="utf-8"))   # titre, source, sortie, page de titre
src = sys.argv[1] if len(sys.argv) > 1 else vol["source"]
out = sys.argv[2] if len(sys.argv) > 2 else vol["out"]

text = open(src, encoding="utf-8").read()
# 1. la page de titre est gérée par les métadonnées : on commence à l'avant-propos
i = text.find(vol["start_heading"])
if i > 0:
    text = text[i:]
# 2. les commentaires HTML <!--sortie--> sont inutiles en PDF
text = text.replace("<!--sortie-->\n", "")
tmp = tempfile.mkdtemp(prefix="pdfbuild_")
md = os.path.join(tmp, "livre.md")
macros = "".join("\\newcommand{\\Vol%s}{%s}\n" % (k, vol[v]) for k, v in
                 [("Serie", "serie"), ("Nom", "nom"), ("LigneA", "ligneA"), ("LigneB", "ligneB"), ("Pied", "pied")])
header = os.path.join(tmp, "header.tex")
open(header, "w", encoding="utf-8").write(macros + open("build/pdf/header.tex", encoding="utf-8").read())
open(md, "w", encoding="utf-8").write(text)

meta = {
    "title": vol["title"],
    "subtitle": vol["subtitle"],
    "author": vol["author"],
    "lang": "fr",
    "documentclass": "book",
    "classoption": "11pt,openany,a4paper",
    "geometry": "margin=2.4cm",
    "mainfont": "TeX Gyre Pagella",
    "mathfont": "TeX Gyre Pagella Math",
    "monofont": "DejaVu Sans Mono",
    "monofontoptions": "Scale=0.84",
    "linkcolor": "bleu",
    "urlcolor": "bleu",
    "colorlinks": "true",
    "toc-depth": "2",
}
cmd = ["pandoc", md, "-f", "markdown+tex_math_dollars-smart+lists_without_preceding_blankline", "-o", out, "--pdf-engine=xelatex",
       "--toc", "--top-level-division=chapter", "--resource-path=.",
       "--lua-filter=build/pdf/callouts.lua", "-H", header,
       "--highlight-style=tango"]
for k, v in meta.items():
    cmd += ["-V", f"{k}={v}"]
print(" ".join(cmd[:6]), "...")
r0 = None
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout[-2000:], r.stderr[-4000:])
sys.exit(r.returncode)
