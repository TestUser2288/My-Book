#!/usr/bin/env python3
"""Rend le chapitre 7 : gabarits (tpl/) -> sections/ et cahier/, exécution (make fill-ch CH=07), puis remplacement des {{clé:format}} par les
valeurs imprimées par les blocs (lignes « NUM clé valeur »). Les fichiers du dépôt sont donc les versions REMPLIES ; pour changer un nombre
de la prose ou un bloc de code, modifier tpl/ puis relancer :  python build/gabarits/ch07/rendre.py   (depuis la racine du volume)."""
import glob, os, shutil, subprocess, sys
ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", "..", ".."))
os.chdir(RACINE)
for sous in ("sections", "cahier"):
    for f in sorted(glob.glob(f"{ICI}/tpl/{sous}/*.md")):
        shutil.copy(f, os.path.join(RACINE, sous, os.path.basename(f)))
r = subprocess.run(["make", "fill-ch", "CH=07"], capture_output=True, text=True)
print(r.stdout[-1500:], r.stderr[-1500:] if r.returncode else "")
if r.returncode:
    sys.exit(r.returncode)
for pattern in ("sections/07-*.md", "cahier/07-exercices.md"):
    fichiers = sorted(glob.glob(pattern))
    if fichiers:
        subprocess.run([sys.executable, f"{ICI}/subst.py"] + fichiers, check=True)
