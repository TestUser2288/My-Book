#!/usr/bin/env python3
"""Assemble les sources du volume en livres lisibles : le LIVRE (sections/) et le CAHIER (cahier/).

Usage : assemble.py [livre|cahier|tout]      (par défaut : tout)

Les noms des fichiers de sortie et les titres des chapitres sont dans build/pdf/volume.json.

Drapeaux de blocs de code (dans la ligne d'ouverture du bloc, après le langage) :
    ```python            code visible + sortie visible          (comportement normal)
    ```python noexec     code visible, jamais exécuté
    ```python hide       EXÉCUTÉ (donc vérifié par `make check`) mais ABSENT du livre assemblé :
                         ni le code ni sa sortie n'apparaissent. À utiliser pour les figures, les
                         simulations, les vérifications numériques de la prose.
    ```python hide-code  exécuté ; seule la SORTIE apparaît dans le livre (le code est caché).
Les sources de sections/ et cahier/ ne sont jamais modifiées par l'assemblage.
"""
import glob, json, os, re, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
vol = json.load(open("build/pdf/volume.json", encoding="utf-8"))


def strip_hidden(text):
    """Retire les blocs `hide` (et leur sortie) ; pour `hide-code`, ne garde que la sortie."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^```(\S*)\s*(.*)$", lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        flags = (m.group(2) or "").split()
        # fin du bloc
        j = i + 1
        while j < len(lines) and not lines[j].startswith("```"):
            j += 1
        block = lines[i:j + 1]
        # sortie injectée par fill.py : "<!--sortie-->" puis un bloc ```text
        k = j + 1
        sortie = []
        if k < len(lines) and lines[k].strip() == "<!--sortie-->" and k + 1 < len(lines) and lines[k + 1].startswith("```"):
            e = k + 2
            while e < len(lines) and not lines[e].startswith("```"):
                e += 1
            sortie = lines[k:e + 1]
            nxt = e + 1
        else:
            nxt = j + 1
        if "hide" in flags:
            pass                                   # tout disparaît
        elif "hide-code" in flags:
            out.extend(sortie[1:] if sortie else [])   # on garde le bloc ```text de la sortie, sans le marqueur
        else:
            out.extend(block)
            out.extend(sortie)
        i = nxt
    text = "\n".join(out)
    return re.sub(r"\n{4,}", "\n\n\n", text)


def assemble(nom):
    cfg = vol[nom]
    files = sorted(glob.glob(cfg["dossier"] + "/*.md"))
    groups = {}
    for f in files:
        m = re.match(r"(\d\d)-", os.path.basename(f))
        if m:
            groups.setdefault(m.group(1), []).append(f)
    os.makedirs("livre", exist_ok=True)
    full, total = [], 0
    for k in sorted(groups):
        parts = [open(f, encoding="utf-8").read().rstrip() + "\n" for f in groups[k]]
        text = strip_hidden("\n\n".join(parts))
        out = f"livre/{cfg['titres'].get(k, k)}.md"
        open(out, "w", encoding="utf-8").write(text)
        full.append(text)
        total += len(text.split())
        print("écrit", out, len(text.split()), "mots")
    complet = cfg["source"]
    open(complet, "w", encoding="utf-8").write("\n\n---\n\n".join(full))
    print(f"[{nom}] total", total, "mots (code caché exclu) ->", complet)


if __name__ == "__main__":
    cible = sys.argv[1] if len(sys.argv) > 1 else "tout"
    for nom in (["livre", "cahier"] if cible == "tout" else [cible]):
        if nom in vol and os.path.isdir(vol[nom]["dossier"]):
            assemble(nom)
