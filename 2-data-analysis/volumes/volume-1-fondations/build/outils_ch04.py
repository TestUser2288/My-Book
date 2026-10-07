"""Outils du chapitre 4 (série 2, volume I) : vérification croisée Python <-> R, exécution de notebooks.

Le « pont » est un dossier temporaire (variable d'environnement CH4_TMP) dans lequel Python écrit ses résultats en CSV ; un bloc R caché les relit et
vérifie qu'il obtient les mêmes nombres. Il est créé au début du chapitre, avant le premier bloc R (la session R hérite alors de la variable)."""
import atexit, os, re, shutil, tempfile

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def ouvrir_pont():
    d = tempfile.mkdtemp(prefix="ch4_", dir=os.environ.get("TMPDIR"))
    os.environ["CH4_TMP"] = d
    atexit.register(shutil.rmtree, d, ignore_errors=True)
    return d


def pont_ecrire(df, nom):
    """écrit un DataFrame pandas dans le pont (index ignoré) pour que R puisse le relire"""
    df.to_csv(os.path.join(os.environ["CH4_TMP"], nom + ".csv"), index=False)


def sans_couleurs(texte):
    return re.sub(r"\x1b\[[0-9;]*m", "", texte)


def executer_notebook(cellules, dossier_travail):
    """construit un notebook à partir d'une liste de (type, source) puis l'exécute DANS L'ORDRE dans un noyau Python neuf.
    Retourne (notebook, message d'erreur ou None)."""
    nb = new_notebook(cells=[new_markdown_cell(s) if t == "md" else new_code_cell(s) for t, s in cellules])
    try:
        NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": dossier_travail}}).execute()
        return nb, None
    except CellExecutionError as e:
        return nb, sans_couleurs(str(e)).strip().splitlines()[-1]


def sorties_texte(nb):
    """texte des sorties (stdout et résultats) de chaque cellule de code d'un notebook exécuté"""
    res = []
    for c in nb.cells:
        if c.cell_type != "code":
            continue
        t = ""
        for o in c.get("outputs", []):
            if o.output_type == "stream":
                t += o.text
            elif o.output_type == "execute_result":
                t += o.data.get("text/plain", "")
        res.append(t.strip())
    return res
