#!/usr/bin/env python3
"""Remplace les marqueurs @@cle:fmt@@ des fichiers .md par les valeurs NUM imprimées par les blocs exécutés.
Usage : patch.py fichier.md [...]   (les valeurs viennent des blocs <!--sortie--> de TOUS les fichiers chapitre 02 du livre et du cahier)
Formats : p0 p1 p2 (fraction -> « 94,2 % »), f0 f1 f2 f3 f4 (décimales avec virgule), i (entier, espace fin pour les milliers), s (texte brut)."""
import glob, re, sys
R = "/var/www/book/1-data-science/volumes/volume-4-sujets-avances/"
vals = {}
for f in sorted(glob.glob(R + "sections/02-*.md")) + sorted(glob.glob(R + "cahier/02-*.md")):
    for m in re.finditer(r"^NUM (\S+) (.*)$", open(f, encoding="utf-8").read(), re.M):
        vals[m.group(1)] = m.group(2).strip()
def fmt(v, f):
    if f == "s": return v
    x = float(v)
    if f == "e":
        import math
        e = max(-12, math.ceil(math.log10(x))) if x > 0 else -12
        return f"$10^{{{e}}}$"
    if f.startswith("p"): return f"{100*x:.{int(f[1:])}f}".replace(".", ",") + " %"
    if f.startswith("f"): return f"{x:.{int(f[1:])}f}".replace(".", ",")
    if f == "i": return f"{int(round(x)):,}".replace(",", " ")
    raise ValueError(f)
manq = set()
for p in sys.argv[1:]:
    t = open(p, encoding="utf-8").read()
    def rep(m):
        k, f = m.group(1), m.group(2)
        if k not in vals: manq.add(k); return m.group(0)
        return fmt(vals[k], f)
    t2 = re.sub(r"@@([A-Za-z0-9_]+):(\w+)@@", rep, t)
    open(p, "w", encoding="utf-8").write(t2)
print("clés disponibles :", len(vals), "| manquantes :", sorted(manq))
