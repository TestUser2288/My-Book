# Chapitre 7 : ➕ Applications de démonstration

> « Une démonstration vaut mille pages : elle laisse l'autre personne **essayer**. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : le volume se lit sans lui. Il s'adresse à celles et ceux qui veulent mettre un modèle **entre les mains de quelqu'un d'autre** (la gérante, un collègue, un client) sans écrire une application web complète.

Au volume III, nous avons construit un modèle de **résiliation** : pour chaque client, la probabilité qu'il ne commande plus dans les 90 jours. Ce modèle vit dans un notebook, et seule la personne qui l'a écrit peut l'interroger. Or la gérante a une question concrète : *« et pour cette cliente-là, qui n'a rien commandé depuis dix mois et qui s'est plainte deux fois, qu'est-ce que ça donne ? »*

Une **application de démonstration** répond à ce besoin : quelques curseurs, un résultat, une explication. En quelques dizaines de lignes de Python, on obtient une interface que l'on peut montrer, tester, critiquer. Ce chapitre explique comment la construire **proprement**, c'est-à-dire en pensant à ce que l'utilisateur comprendra de ce qu'il voit, pas seulement à ce que le code calcule.

## Le chemin de ce chapitre

- **7.1 Pourquoi une application ?** Ce qu'est une démonstration (et ce qu'elle n'est pas), les principes d'une interface honnête (entrées, valeurs par défaut, incertitude, explication, humain dans la boucle), et les deux manières de rendre une interface « vivante » : rejouer un script ou suivre un graphe de dépendances.
- **7.2 Streamlit.** Une application est un **script qui se rejoue** à chaque interaction ; widgets, état de session, mise en page, formulaires, cache, et surtout **comment tester** une application sans navigateur.
- **7.3 Shiny.** L'autre modèle : le **graphe réactif**. Nous le construisons en miniature, puis nous le comparons à Streamlit **par mesure**, en comptant les calculs réellement refaits.
- **7.4 Du prototype à l'usage réel.** Configuration, secrets, confidentialité, performance, journaux, conteneurs, accessibilité, licences, maintenance, et le moment où il faut remplacer l'application par une **API** (chapitre 4, sections 4.2 et 4.6).

> 📦 **Données et outils.** Le modèle est celui de la résiliation (`donnees/clients_ml.csv`, copie du jeu du volume III) : les colonnes qui fuient l'avenir (`commandes_apres_cible`) ou qui révèlent la vérité programmée (`segment_vrai`) en sont exclues, comme au volume III. La série des ventes quotidiennes (`donnees/ventes_quotidiennes.csv`) sert d'exemple de second écran. Les applications sont écrites dans un **dossier temporaire** et exécutées **sans navigateur** avec l'outil de test de Streamlit ; aucun accès au réseau n'est nécessaire. Les données sont **simulées**.

> ⚠️ **Aucune capture d'écran dans ce chapitre.** L'environnement de rédaction n'a pas de navigateur : les images qui représentent des écrans sont des **maquettes dessinées avec matplotlib**, et le livre le dit à chaque fois. Ce qui est mesuré (probabilités, nombres de calculs, résultats de tests) vient en revanche de l'exécution réelle des applications.

```python hide
import os, sys, tempfile, shutil, textwrap, warnings, logging, json
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
logging.getLogger("streamlit").setLevel(logging.CRITICAL)
RACINE = os.getcwd()
TMP = tempfile.mkdtemp(prefix="ch7_", dir=os.environ.get("TMPDIR"))
os.environ["APP_DONNEES"] = os.path.join(RACINE, "donnees", "clients_ml.csv")
os.environ["APP_VENTES"] = os.path.join(RACINE, "donnees", "ventes_quotidiennes.csv")
os.environ["CH7_TMP"] = TMP                       # lu par les blocs R de la section 7.3
sys.path.insert(0, os.path.join(RACINE, "build"))
sys.path.insert(0, TMP)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET
style.setup()

def fr(x, d=1):
    """Format français : virgule décimale, espace insécable pour les milliers."""
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")

NUMS = {}
def NUM(nom, valeur, d=1, suffixe=""):
    s = fr(valeur, d) + suffixe
    NUMS[nom] = s
    print("NUM", nom, s)

def ecrire(nom, contenu):
    """Écrit un fichier de l'application dans le dossier temporaire."""
    chemin = os.path.join(TMP, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(contenu).lstrip("\n"))
    return chemin
print("dossier temporaire prêt :", os.path.basename(TMP).startswith("ch7_"))
```
<!--sortie-->
```text
dossier temporaire prêt : True
```
