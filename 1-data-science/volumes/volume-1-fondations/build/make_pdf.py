#!/usr/bin/env python3
"""Construit le PDF du volume à partir de livre/volume-1-fondations-complet.md (pandoc + xelatex).

Usage : python3 build/make_pdf.py [source.md] [sortie.pdf]
Prérequis : pandoc, xelatex, texlive-lang-french, texlive-latex-extra, polices TeX Gyre + DejaVu.
Les emojis des callouts sont convertis en boîtes colorées par build/pdf/callouts.lua.
"""
import os, re, subprocess, sys, tempfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
src = sys.argv[1] if len(sys.argv) > 1 else "livre/volume-1-fondations-complet.md"
out = sys.argv[2] if len(sys.argv) > 2 else "livre/volume-1-fondations.pdf"

text = open(src, encoding="utf-8").read()
# 1. la page de titre est gérée par les métadonnées : on commence à l'avant-propos
i = text.find("# Avant-propos")
if i > 0:
    text = text[i:]
# 2. les commentaires HTML <!--sortie--> sont inutiles en PDF
text = text.replace("<!--sortie-->\n", "")
tmp = tempfile.mkdtemp(prefix="pdfbuild_")
md = os.path.join(tmp, "livre.md")
open(md, "w", encoding="utf-8").write(text)

meta = {
    "title": "DATA SCIENCE",
    "subtitle": "Volume I : Fondations — Mathématiques, probabilités, statistique, programmation, bases de données et outils",
    "author": "Série 1 : Data Science",
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
cmd = ["pandoc", md, "-f", "markdown+tex_math_dollars-smart", "-o", out, "--pdf-engine=xelatex",
       "--toc", "--top-level-division=chapter", "--resource-path=.",
       "--lua-filter=build/pdf/callouts.lua", "-H", "build/pdf/header.tex",
       "--highlight-style=tango"]
for k, v in meta.items():
    cmd += ["-V", f"{k}={v}"]
print(" ".join(cmd[:6]), "...")
r0 = None
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout[-2000:], r.stderr[-4000:])
sys.exit(r.returncode)
