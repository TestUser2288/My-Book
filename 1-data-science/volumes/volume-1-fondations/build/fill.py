#!/usr/bin/env python3
"""
Exécute les blocs ```python et ```sql des fichiers Markdown (dans l'ordre, avec un espace
de noms partagé) et insère la sortie réelle juste après chaque bloc.

Convention :
  - ```python        -> exécuté, sortie insérée dans <!--sortie--> ```text ... ```
  - ```python noexec -> affiché seulement (jamais exécuté)
  - ```r             -> exécuté dans une session R persistante (R --slave)
  - ```bash          -> exécuté dans une session bash persistante (répertoire de travail jetable)
  - ```sql           -> exécuté sur la connexion `con` (sqlite3) si elle existe
  - ```sql noexec    -> affiché seulement
  - toute sortie existante (bloc <!--sortie-->) est remplacée.

Usage : fill.py [--check] fichier1.md fichier2.md ...
"""
import contextlib
import io
import os
import re
import sys
import traceback

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib  # noqa: E402

matplotlib.use("Agg")

FENCE = re.compile(r"^```(\S*)\s*(.*)$")
MAX_LINES = 70


def split_blocks(text):
    """Retourne une liste de segments ('text', '', [lignes], n) ou ('code', info, [lignes], n)."""
    lines = text.split("\n")
    segs, buf, i = [], [], 0
    while i < len(lines):
        if lines[i].startswith("```"):
            if buf:
                segs.append(["text", "", buf, i - len(buf) + 1])
                buf = []
            info = lines[i][3:].strip()
            j = i + 1
            code = []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j])
                j += 1
            segs.append(["code", info, code, i + 1])
            i = j + 1
        else:
            buf.append(lines[i])
            i += 1
    if buf:
        segs.append(["text", "", buf, len(lines) - len(buf) + 1])
    return segs


def run_python(code, ns):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, "<bloc>", "exec"), ns)
    return out.getvalue()


def run_sql(code, ns):
    import pandas as pd

    con = ns.get("con")
    if con is None:
        raise RuntimeError("bloc ```sql sans connexion `con` définie avant")
    out = []
    # on découpe sur les ';' de fin d'instruction
    stmts = [s.strip() for s in re.split(r";\s*(?:\n|$)", code) if s.strip()]
    for s in stmts:
        first = re.sub(r"--.*", "", s).strip().split()
        kw = first[0].upper() if first else ""
        if kw in ("SELECT", "WITH"):
            df = pd.read_sql_query(s, con)
            with pd.option_context("display.width", 200, "display.max_columns", 50, "display.max_rows", 200):
                out.append(df.to_string(index=False) if len(df) else "(aucune ligne)")
        else:
            con.executescript(s + ";")
            con.commit()
    return "\n\n".join(out)


class Session:
    """Processus persistant (R ou bash) alimenté bloc par bloc, avec un marqueur de fin."""

    FIN = "@@FIN@@"

    def __init__(self, lang):
        import subprocess, tempfile
        self.lang = lang
        self.tmp = tempfile.mkdtemp(prefix=f"fill_{lang}_")
        env = dict(os.environ, HOME=self.tmp, LANG="C.UTF-8", LC_ALL="C.UTF-8")
        if lang == "r":
            cmd = ["R", "--vanilla", "--slave", "--no-save"]
            self.cwd = os.getcwd()
        else:
            cmd = ["bash", "--noprofile", "--norc"]
            self.cwd = os.path.join(self.tmp, "atelier")
            os.makedirs(self.cwd, exist_ok=True)
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, cwd=self.cwd, env=env, bufsize=1)
        if lang == "bash":
            self.p.stdin.write("export PS1=''; export GIT_CONFIG_NOSYSTEM=1\n")

    def run(self, code):
        if self.lang == "r":
            f = os.path.join(self.tmp, "bloc.R")
            open(f, "w", encoding="utf-8").write(code + "\n")
            self.p.stdin.write(
                f'tryCatch(source("{f}", print.eval=TRUE, echo=FALSE), error=function(e) cat("ERREUR R :", conditionMessage(e), "\\n"))\n'
                f'cat("\\n{self.FIN}\\n")\n')
        else:
            self.p.stdin.write(code + "\n")
            self.p.stdin.write(f"echo; echo {self.FIN}\n")
        self.p.stdin.flush()
        out = []
        for line in self.p.stdout:
            if line.strip() == self.FIN:
                break
            out.append(line)
        res = "".join(out)
        if "ERREUR R :" in res:
            raise RuntimeError(res.strip())
        return res


SESSIONS = {}


def run_other(lang, code):
    if lang not in SESSIONS:
        SESSIONS[lang] = Session(lang)
    return SESSIONS[lang].run(code)


def process(path, ns, check):
    text = open(path, encoding="utf-8").read()
    segs = split_blocks(text)
    # retirer les anciens blocs de sortie
    cleaned = []
    k = 0
    while k < len(segs):
        kind, info, lines, ln = segs[k]
        if kind == "text" and lines and lines[-1].strip() == "<!--sortie-->" and k + 1 < len(segs) and segs[k + 1][0] == "code":
            lines = lines[:-1]
            if lines:
                cleaned.append(["text", info, lines, ln])
            k += 2
            continue
        cleaned.append([kind, info, lines, ln])
        k += 1
    segs = cleaned

    out_lines = []
    errors = 0
    for kind, info, lines, ln in segs:
        if kind == "text":
            out_lines.extend(lines)
            continue
        out_lines.append("```" + info)
        out_lines.extend(lines)
        out_lines.append("```")
        lang = info.split()[0] if info else ""
        noexec = "noexec" in info.split()
        if lang not in ("python", "sql", "r", "bash") or noexec:
            continue
        code = "\n".join(lines)
        try:
            if lang == "python":
                output = run_python(code, ns)
            elif lang == "sql":
                output = run_sql(code, ns)
            else:
                output = run_other(lang, code)
        except Exception:
            errors += 1
            print(f"\n!!! ERREUR dans {path}, bloc {lang} ligne {ln}:")
            tb = traceback.format_exc().strip().split("\n")
            print("\n".join(tb[-6:]))
            continue
        output = output.rstrip("\n")
        if output:
            olines = output.split("\n")
            if len(olines) > MAX_LINES:
                print(f"  (attention) {path} ligne {ln}: sortie de {len(olines)} lignes tronquée")
                olines = olines[:MAX_LINES] + ["…"]
            out_lines.append("<!--sortie-->")
            out_lines.append("```text")
            out_lines.extend(olines)
            out_lines.append("```")
    new_text = "\n".join(out_lines)
    changed = new_text != text
    if changed and not check:
        open(path, "w", encoding="utf-8").write(new_text)
    return errors, changed


def main():
    args = sys.argv[1:]
    check = False
    if args and args[0] == "--check":
        check = True
        args = args[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)  # figures/ relatif à la racine du volume
    ns = {"__name__": "__book__"}
    total_err = 0
    for p in args:
        err, changed = process(p, ns, check)
        total_err += err
        print(f"{'[vérif]' if check else '[écrit]'} {p}: {err} erreur(s), {'modifié' if changed else 'inchangé'}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
