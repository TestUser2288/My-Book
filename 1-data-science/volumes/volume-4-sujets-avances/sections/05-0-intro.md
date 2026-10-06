# Chapitre 5 : Ingénierie des données

> « Un modèle sophistiqué sur des données douteuses est une erreur très bien calculée. »

Les chapitres précédents ont supposé que **la table d'entrée existait**, propre, typée, sans doublons, avec les bonnes colonnes. Dans une entreprise, ce n'est presque jamais le cas. Les données naissent dans des systèmes différents (la caisse du magasin, le site web, un tableur du service client, le fichier d'un fournisseur), chacun avec **ses formats, ses clés, ses habitudes et ses erreurs**. Quelqu'un doit les faire arriver, les contrôler, les réconcilier et les livrer, **tous les jours**, sans les abîmer. Ce travail s'appelle l'**ingénierie des données** (*data engineering*), et c'est lui qui décide en grande partie si les modèles du reste de ce volume serviront ou non.

La gérante de la boutique vous confie quatre fichiers « exportés tels quels » de ses outils : une liste de commandes, le carnet de clients de son logiciel de relation client (le CRM), le catalogue de ses produits, et la liste d'un fournisseur. Ce chapitre raconte, pas à pas, comment les transformer en **tables fiables**.

## Le chemin de ce chapitre

- **5.1 Conception d'ETL** : extraire, transformer, charger ; les couches (brut, nettoyé, mart) ; rejeter proprement ; **idempotence** et chargements incrémentaux ; ETL en pandas et ELT en SQL avec DuckDB.
- **5.2 Qualité des données** : les dimensions de la qualité, des règles écrites comme de petites fonctions, un score, des seuils, et le **coût concret** d'une donnée sale sur un chiffre d'affaires.
- **5.3 Réconciliation** : retrouver que « Bol  coton (lot) » et « Bol en coton » sont le même produit, et que deux lignes du CRM sont la même personne ; comparer des chaînes, **bloquer** pour passer à l'échelle, mesurer précision et rappel.
- ➕ **5.4 Gouvernance, lignage et protection des données** : qui est responsable de quoi, d'où vient chaque chiffre, et comment protéger les données personnelles (pseudonymisation).
- ➕ **5.5 Collecte par scraping et par API** : pages web et API paginées, limitation de débit, politesse et légalité, sur un **site de démonstration local**.

> 🧭 **Données de ce chapitre.** Quatre exports volontairement **sales**, dans `donnees/sources/` : `commandes_export.csv`, `clients_crm.csv`, `produits_catalogue.csv` et `produits_fournisseur.csv`. Ils sont **simulés**, avec une vérité connue (`verite_produits.csv`, `verite_clients.csv`) qui permet de **mesurer** la qualité d'une réconciliation, ce qui est impossible sur des données réelles où l'on ne connaît jamais la vérité. Aucun code de ce chapitre n'ouvre de connexion extérieure : les exemples de collecte interrogent un petit site fabriqué **sur votre machine**.

```python hide
import os, sys, shutil, tempfile, warnings, json, re, hashlib
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd, duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
style.setup()
from outils_ch05 import *

def NUM(nom, valeur):
    print("NUM", nom, valeur)

TMP = tempfile.mkdtemp(prefix="ch05_", dir=os.environ.get("TMPDIR"))      # tout fichier intermédiaire vit ici (supprimé en fin de chapitre)
brut = lire("commandes_export")
crm = lire("clients_crm")
crm["id_crm"] = crm["id_crm"].astype(int)
catalogue = lire("produits_catalogue")
catalogue["prix_catalogue"] = catalogue["prix_catalogue"].astype(float)
fournisseur = lire("produits_fournisseur")
fournisseur["prix_achat"] = fournisseur["prix_achat"].astype(float)
NUM("lignes", {"commandes": len(brut), "crm": len(crm), "catalogue": len(catalogue), "fournisseur": len(fournisseur)})
```
<!--sortie-->
```text
NUM lignes {'commandes': 19700, 'crm': 5000, 'catalogue': 48, 'fournisseur': 40}
```

Les quatre fichiers comptent respectivement **19 700**, **5 000**, **48** et **40** lignes. Les écarts sont déjà un indice : le catalogue décrit 48 produits, le fournisseur en livre 40 ; le CRM contient 5 000 lignes, mais combien de personnes ? C'est ce que le chapitre va établir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 et exercices 5.1 à 5.12, section par section.
