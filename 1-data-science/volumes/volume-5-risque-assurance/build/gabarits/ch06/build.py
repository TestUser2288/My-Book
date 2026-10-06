#!/usr/bin/env python3
"""Gabarits -> fichiers du chapitre 6. Les nombres cités dans la prose sont lus dans les lignes « NUM clé valeur » imprimées par des blocs cachés.
Usage : build.py [lire|rendre|tout]   (tout : rend, remplit, relit ; répète jusqu'à stabilité)
Format d'un nombre dans un gabarit : {{clé}} (tel quel) ou {{clé|spec}} avec spec = [pc|M|k]N[m] ou « int » :
  N chiffres après la virgule décimale française ; pc = ×100 ; M = ÷10^6 ; k = ÷10^3 ; m = virgule de mode mathématique {,} ; int = entier avec espaces."""
import glob, json, os, re, subprocess, sys
TMP = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(TMP, "..", "..", ".."))
NUMS = os.path.join(TMP, "nums.json")
def lire():
    d = json.load(open(NUMS)) if os.path.exists(NUMS) else {}
    for f in glob.glob(RACINE + "/sections/06-*.md") + glob.glob(RACINE + "/cahier/06-*.md"):
        for l in open(f, encoding="utf-8"):
            m = re.match(r"^NUM (\S+) (.+)$", l.rstrip("\n"))
            if m: d[m.group(1)] = m.group(2).strip()
    json.dump(d, open(NUMS, "w"), indent=0, sort_keys=True); return d
def fmt(v, spec):
    if not spec: return v
    if spec == "int": return f"{int(round(float(v))):,}".replace(",", " ")
    m = re.fullmatch(r"(pc|M|k)?(\d+)(m)?", spec)
    if not m: raise ValueError(spec)
    x = float(v); x = x * 100 if m.group(1) == "pc" else x / 1e6 if m.group(1) == "M" else x / 1e3 if m.group(1) == "k" else x
    s = f"{x:.{int(m.group(2))}f}"
    return s.replace(".", "{,}" if m.group(3) else ",")
def rendre(d):
    manques = set()
    for sous in ("sections", "cahier"):
        for f in glob.glob(f"{TMP}/tpl/{sous}/*.md"):
            t = open(f, encoding="utf-8").read()
            def rep(m):
                k, spec = m.group(1), m.group(2)
                if k not in d: manques.add(k); return "⟦" + k + "⟧"
                return fmt(d[k], spec)
            t = re.sub(r"\{\{([A-Za-z0-9_]+)(?:\|([^}]*))?\}\}", rep, t)
            open(os.path.join(RACINE, sous, os.path.basename(f)), "w", encoding="utf-8").write(t)
    return manques
def remplir():
    return subprocess.run(["make", "fill-ch", "CH=06"], cwd=RACINE, capture_output=True, text=True)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tout"
    if mode == "lire": print(len(lire()), "nombres"); sys.exit()
    if mode == "rendre": d = lire(); print("manquants :", sorted(rendre(d))); sys.exit()
    for tour in range(4):
        d = lire(); avant = dict(d); man = rendre(d); print(f"tour {tour}: manquants {len(man)}", sorted(man)[:12], flush=True)
        r = remplir(); print((r.stdout + r.stderr)[-900:], flush=True)
        d = lire()
        if d == avant and not man: print("stable"); break
