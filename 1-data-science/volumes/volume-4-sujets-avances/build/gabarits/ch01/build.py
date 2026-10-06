#!/usr/bin/env python3
"""Gabarits -> fichiers du chapitre. Les nombres cités dans la prose sont lus dans les sorties « NUM cle valeur » des blocs exécutés.
Usage : build.py [rendre|lire|tout]   (tout : lire, rendre, remplir, relire ; répète jusqu'à stabilité)"""
import json, os, re, subprocess, sys, glob
TMP = os.path.dirname(os.path.abspath(__file__)); RACINE = "/var/www/book/1-data-science/volumes/volume-4-sujets-avances"
NUMS = os.path.join(TMP, "nums.json")
def lire():
    d = json.load(open(NUMS)) if os.path.exists(NUMS) else {}
    for f in glob.glob(RACINE + "/sections/01-*.md") + glob.glob(RACINE + "/cahier/01-*.md"):
        for l in open(f, encoding="utf-8"):
            m = re.match(r"^NUM (\S+) (.+)$", l.rstrip("\n"))
            if m: d[m.group(1)] = m.group(2).strip()
    json.dump(d, open(NUMS, "w"), indent=0, sort_keys=True); return d
def fmt(v, spec):
    if spec is None or spec == "": return v
    if spec == "int":
        return f"{int(round(float(v))):,}".replace(",", " ")
    x = float(v)
    m = re.fullmatch(r"(pc)?(\d+)(m)?", spec)
    if m:
        s = f"{x*100 if m.group(1) else x:.{int(m.group(2))}f}".replace(".", "{,}" if m.group(3) else ",")
        return s
    if spec in ("sci", "scim"):
        mant, ex = f"{x:.1e}".split("e"); return mant.replace(".", "{,}") + r"\times10^{" + str(int(ex)) + "}"
    raise ValueError(spec)
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
def remplir(cible):
    env = dict(os.environ)
    cmd = f"cd {RACINE} && source {TMP}/env.sh && python build/fill.py {cible}"
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tout"
    if mode == "lire": print(len(lire()), "nombres"); sys.exit()
    if mode == "rendre":
        d = lire(); print("manquants :", sorted(rendre(d))); sys.exit()
    for tour in range(4):
        d = lire(); avant = dict(d); man = rendre(d); print(f"tour {tour}: manquants {len(man)}")
        for cible in ("sections/01-*.md", "cahier/01-*.md"):
            r = remplir(cible); print(r.stdout[-600:], r.stderr[-800:] if r.returncode else "")
        d = lire()
        if d == avant and not man: print("stable"); break
