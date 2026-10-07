#!/usr/bin/env python3
"""Remplace les {{cle}} / {{cle:format}} de la prose par les valeurs imprimées par les blocs exécutés (lignes « NUM cle valeur »).
Usage : subst.py fichier1.md fichier2.md ...   (les valeurs sont collectées dans l'ordre des fichiers ; hors blocs de code)"""
import re, sys
files = sys.argv[1:]
vals = {}
def blocs(texte):
    """découpe en (est_code, ligne) pour ne toucher qu'à la prose"""
    inf = False
    for l in texte.split("\n"):
        if l.startswith("```"):
            inf = not inf
            yield True, l
        else:
            yield inf, l
for f in files:
    for code, l in blocs(open(f, encoding="utf-8").read()):
        m = re.match(r"NUM (\S+) (.*)$", l)
        if code and m:
            vals[m.group(1)] = m.group(2).strip()
PAT = re.compile(r"\{\{([A-Za-z0-9_]+)(?::([^}]+))?\}\}")
manque = set()
def rempl(m):
    k, fmt = m.group(1), m.group(2)
    if k not in vals:
        manque.add(k); return m.group(0)
    v = vals[k]
    if fmt == 'raw':
        return v
    if fmt:
        try: v = format(float(v) if not fmt.endswith("d") else int(float(v)), fmt)
        except ValueError: v = format(v, fmt)
    v = v.replace(",", " ") if fmt and "," in fmt else v
    return v.replace(".", ",")
for f in files:
    out = []
    for code, l in blocs(open(f, encoding="utf-8").read()):
        out.append(l if code else PAT.sub(rempl, l))
    open(f, "w", encoding="utf-8").write("\n".join(out))
reste = []
for f in files:
    for code, l in blocs(open(f, encoding="utf-8").read()):
        if not code and re.search(r"\{\{[^\W\d]", l):
            reste.append((f, l[:80]))
print("valeurs collectées :", len(vals), "| clés manquantes :", sorted(manque), "| gabarits non remplacés :", len(reste))
if reste or manque:
    for r in reste[:5]:
        print("  non remplacé :", r)
    sys.exit(1)
