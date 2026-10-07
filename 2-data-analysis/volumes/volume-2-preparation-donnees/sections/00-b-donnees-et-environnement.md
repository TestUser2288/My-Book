# Carte du volume, données et environnement

Cette section ouvre le volume par quatre choses : la **carte des chapitres**, le **catalogue des sources désordonnées** (avec, pour chacune, ce qui cloche), le mode d'emploi des **fichiers de vérité**, et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à une question de la gérante. Les chapitres se lisent dans l'ordre, mais on peut les prendre séparément ; les sections marquées ➕ sont facultatives, et le chapitre 5 tout entier est complémentaire.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Nettoyage des données** | Pourquoi ce fichier ne tombe-t-il pas juste ? | valeurs manquantes, valeurs aberrantes, doublons, incohérences de format ; ➕ texte, dates, encodage, données multilingues ; ➕ imputation et son impact |
| **2. Transformation et fusion** | Comment relier la caisse, le site, le fournisseur ? | variables dérivées, jointures, agrégation et restructuration ; ➕ pivot et dépivot ; ➕ rapprochement approximatif |
| **3. Qualité et réconciliation** | Les chiffres de deux sources disent-ils la même chose ? | dimensions de la qualité, contrôles de validation, réconciliation ; ➕ règles, seuils, rapports d'exceptions ; ➕ pandera et Great Expectations |
| **4. Documentation** | Qui comprendra ce travail dans six mois ? | documenter les jeux de données et les transformations, dictionnaire de données ; ➕ lignage et pistes d'audit |
| **➕ 5. Confidentialité et anonymisation** | Puis-je partager ce fichier ? | données personnelles, pseudonymisation, k-anonymat, bonnes pratiques |
| **Projet du volume (cahier)** | Je veux un fichier clients et un chiffre d'affaires fiables | nettoyer et réconcilier deux sources désordonnées |

## Les sources désordonnées du volume

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a2.py`. Il part de la base propre du volume I (la boutique, ses clients, ses commandes) et **fabrique des sources désordonnées**, comme celles que l'on reçoit dans la vie réelle, en y injectant des défauts connus. Les noms de personnes sont inventés, sans origine particulière, et les adresses de messagerie utilisent des domaines réservés aux exemples. Aucune donnée ne vient d'une entreprise réelle.

```python hide
import os, io, glob, re, sqlite3, subprocess
import numpy as np
import pandas as pd

def lire(nom, **kw):
    return pd.read_csv(f"donnees/{nom}", **kw)

crm = lire("crm_clients.csv", dtype=str)
site = lire("site_commandes.csv", dtype=str)
site_l = lire("site_lignes.csv")
cat = lire("catalogue_fournisseur.csv")
prod = lire("produits.csv")
prof = lire("profil_clients.csv")
mont = lire("montants_saisis.csv")
fichiers = sorted(glob.glob("donnees/caisse/*.csv"))
```

| Fichier | D'où il vient | Ce qui cloche | Lignes | Chapitres |
|---|---|---|---|---|
| `crm_clients.csv` | le fichier clients, alimenté par la caisse, le site et des imports | doublons flous, lignes de test, formats de date et de téléphone mêlés, codes postaux amputés, villes écrites de six façons, texte abîmé | 7 140 | 1, 2, 3, 5, projet |
| `site_commandes.csv`, `site_lignes.csv` | export de la plateforme web (Site, 2025) | commandes en double, de test, annulées ; montants en texte ; changement de format de date et **d'unité** | 6 259 ; 13 928 | 1, 2, 3, projet |
| `caisse/caisse_2025-01.csv` … `-12.csv` | export mensuel de la caisse de la boutique | **dérive de schéma** : encodage, séparateur, décimale, noms de colonnes, format de date ; titres, en-têtes répétés, total, montants vides, lignes doublées | 12 fichiers | 1, 2, 3, projet |
| `catalogue_fournisseur.csv` | catalogue d'un fournisseur | autres codes, désignations réécrites, produits en plus et en moins | 118 | 2, 3 |
| `stocks_tableur.xlsx` | tableur saisi à la main | titres, cellules fusionnées, sous-totaux, mois en colonnes, « ND », « rupture », nombres en texte | 1 feuille | 2 |
| `profil_clients.csv` | fichier de profils (âge, revenu estimé, dépenses, satisfaction) | valeurs **manquantes** de trois natures différentes | 6 000 | 1 |
| `montants_saisis.csv` | saisie de montants de lignes de commande | valeurs aberrantes : décimale décalée, signe, zéro, 9 999 | 6 000 | 1, 3 |
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv` | la base propre du volume I | (copies, pour recouper) | 6 000 ; 120 ; 36 395 ; 83 905 | tous |

### Le fichier clients : un CRM alimenté par trois sources

Le CRM (*customer relationship management*, la base des contacts) compte 7 140 lignes pour 6 000 clients réels.

| Colonne | Contenu | Ce qu'on y trouve |
|---|---|---|
| `id_crm` | numéro de ligne du CRM | **pas** un identifiant de client : un client peut avoir plusieurs lignes |
| `prenom`, `nom` | identité | majuscules, accents retirés, fautes, initiales, inversions, espaces |
| `email` | adresse | absente, en majuscules, malformée |
| `telephone` | numéro | cinq présentations |
| `ville`, `code_postal` | adresse | variantes d'orthographe, ville en arabe, code sans son zéro initial, absent |
| `date_naissance`, `date_inscription` | dates | quatre formats de naissance, dont des dates impossibles ; inscription en `jj/mm/aaaa` |
| `consentement_marketing` | accord pour les messages commerciaux | sept façons de l'écrire |
| `source_saisie` | `caisse`, `site` ou `import` | peut expliquer la façon d'écrire |

```python hide-code
print("lignes :", len(crm), "| e-mails absents :", int(crm["email"].isna().sum()), f"({crm['email'].isna().mean():.1%})", "| codes postaux absents :", int(crm["code_postal"].isna().sum()), "| de moins de 5 chiffres :", int((crm["code_postal"].str.len() < 5).sum()))
def fmt(x):
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x):
        return "aaaa-mm-jj"
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", x):
        return "xx/xx/aaaa"
    return "texte"
print("formats de naissance :", crm["date_naissance"].map(fmt).value_counts().to_dict())
print("graphies de ville :", crm["ville"].nunique(), "pour 20 villes ;", int(crm["ville"].str.contains("[؀-ۿ]").sum()), "en arabe")
print("consentement :", crm["consentement_marketing"].fillna("(vide)").value_counts().to_dict())
print("présentations du téléphone :", crm["telephone"].map(lambda x: re.sub(r"\d", "9", x)).nunique(), "| noms abîmés (« Ã ») :", int(crm["nom"].str.contains("Ã").sum()))
print("source de saisie :", crm["source_saisie"].value_counts().to_dict())
```
<!--sortie-->
```text
lignes : 7140 | e-mails absents : 231 (3.2%) | codes postaux absents : 424 | de moins de 5 chiffres : 199
formats de naissance : {'xx/xx/aaaa': 4674, 'aaaa-mm-jj': 1749, 'texte': 717}
graphies de ville : 119 pour 20 villes ; 191 en arabe
consentement : {'oui': 2411, '(vide)': 2161, 'Oui': 703, '1': 687, 'O': 369, 'TRUE': 338, 'OUI': 331, 'non': 140}
présentations du téléphone : 5 | noms abîmés (« Ã ») : 213
source de saisie : {'caisse': 3507, 'site': 2965, 'import': 668}
```

Les 119 graphies de ville pour 20 villes, les cinq formats de téléphone et les sept écritures du consentement donnent une idée de ce qu'est un champ saisi par plusieurs mains. Notez le nombre de dates écrites `xx/xx/aaaa` : pour la plupart, on lit « jour/mois », mais **pas pour toutes** (certaines lignes saisies sur le site écrivent « mois/jour »), et c'est un piège que nous rencontrerons à la section 1.4.

### L'export du site web

La plateforme exporte une ligne par commande (`site_commandes.csv`) et une ligne par article (`site_lignes.csv`), avec des noms de colonnes en anglais.

| Colonne | Contenu | Ce qu'on y trouve |
|---|---|---|
| `order_ref` | référence de la commande (`WEB-023450`) | répétée quand l'export est relancé |
| `created_at` | date et heure | `2025-03-04 14:22:05` (sans fuseau) jusqu'au 14 septembre, `2025-09-16T14:22:05Z` (en UTC) ensuite |
| `status` | statut | `paid`, `PAID`, `Paid`, `cancelled` |
| `customer_email`, `customer_name` | client | en majuscules, avec espaces, ou `test@example.com` |
| `total`, `currency` | montant et devise | texte (`34,92 €`, `195.40`, `1 245,00`), **en centimes** depuis le 15 septembre ; `EUR`, `eur`, `€` |
| `promo_code`, `shipping_mode` | code promotionnel, livraison | vides pour « aucun » |
| (lignes) `sku`, `qty`, `unit_price`, `discount_pct` | article, quantité, prix, remise | le `sku` s'écrit `P043` : le code produit de la boutique, sans le zéro de gauche |

```python hide-code
print("commandes (lignes d'export) :", len(site), "| références distinctes :", site["order_ref"].nunique(), "| lignes d'articles :", len(site_l))
print("statuts :", site["status"].value_counts().to_dict(), "| devises :", site["currency"].value_counts().to_dict())
form = site["total"].map(lambda x: "euro" if "€" in x else ("espace" if " " in x else ("point" if "." in x else ("virgule" if "," in x else "entier"))))
print("présentations du total :", form.value_counts().to_dict(), "| promo absente :", f"{site['promo_code'].isna().mean():.1%}")
```
<!--sortie-->
```text
commandes (lignes d'export) : 6259 | références distinctes : 6138 | lignes d'articles : 13928
statuts : {'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186} | devises : {'EUR': 4987, 'eur': 643, '€': 629}
présentations du total : {'entier': 2494, 'point': 1510, 'euro': 1476, 'virgule': 779} | promo absente : 84.2%
```

### Les exports de caisse : douze fichiers, trois réglages

L'export de la caisse est produit chaque mois, mais **le logiciel a changé de réglages deux fois dans l'année**. Concaténer les douze fichiers sans précaution échoue ou donne des colonnes mélangées.

| Mois | Encodage | Séparateur | Décimale | Colonne des quantités | Date | Colonnes |
|---|---|---|---|---|---|---|
| janvier à juin | `cp1252` (Windows) | `;` | virgule | `Qté` | `jj/mm/aaaa` | 8 |
| juillet à septembre | UTF-8 avec marque BOM | `;` | virgule | `Quantité` | `jj/mm/aa` | 8 |
| octobre à décembre | UTF-8 avec marque BOM | `,` | point | `Qté` | `jj/mm/aaaa` | 9 (une colonne `Remise (%)` en plus) |

Chaque fichier commence par trois lignes de titre, répète son en-tête toutes les soixante lignes (le « changement de page »), se termine par une ligne de total, comporte quelques montants vides et, parfois, une ligne répétée par un double passage en caisse.

```python hide-code
regimes = {}
for f in fichiers:
    brut = open(f, "rb").read()
    try:
        texte = brut.decode("utf-8-sig"); enc = "utf-8"
    except UnicodeDecodeError:
        texte = brut.decode("cp1252"); enc = "cp1252"
    lignes = texte.splitlines()
    entete = lignes[3]
    sep = ";" if entete.count(";") > entete.count(",") else ","
    regimes.setdefault((enc, sep, len(entete.split(sep))), []).append(os.path.basename(f)[-6:-4])
print("réglages distincts :", len(regimes))
for k, v in regimes.items():
    print(k, "→ mois", ", ".join(v))
print("lignes de fichier au total :", sum(len(open(f, "rb").read().splitlines()) for f in fichiers))
```
<!--sortie-->
```text
réglages distincts : 3
('cp1252', ';', 8) → mois 01, 02, 03, 04, 05, 06
('utf-8', ';', 8) → mois 07, 08, 09
('utf-8', ',', 9) → mois 10, 11, 12
lignes de fichier au total : 12943
```

### Le catalogue du fournisseur et le tableur de stocks

Le **catalogue du fournisseur** décrit les articles par un code `F-xxxx` et une désignation réécrite (casse, accents, abréviations, ordre des mots, quelques mots anglais). Il manque 12 produits de la boutique, et 10 articles du fournisseur ne sont pas à la boutique. Attention à un détail hérité du volume I : **la boutique compte 120 produits mais seulement 60 noms distincts**, parce que chaque nom est porté par deux produits à prix différents. La désignation seule ne suffit donc pas à rapprocher les deux listes : il faudra s'aider du prix (sections 2.2 et 2.5).

Le **tableur de stocks** est une feuille « à la main » : un titre, une phrase de consigne, une ligne d'en-têtes, puis les catégories en cellules fusionnées, les produits (un par ligne, les douze mois en colonnes), un sous-total par catégorie avec une formule, et des cellules qui contiennent « ND », un tiret, « rupture » ou un nombre écrit avec une espace.

```python hide-code
print("catalogue : lignes", len(cat), "| familles écrites :", cat["famille"].nunique(), "pour 6 catégories | désignations avec espaces autour :", int((cat["designation"] != cat["designation"].str.strip()).sum()))
print("boutique : produits", len(prod), "| noms distincts :", prod["nom_produit"].nunique(), "| noms portés par deux produits :", int((prod["nom_produit"].value_counts() == 2).sum()))
import openpyxl
ws = openpyxl.load_workbook("donnees/stocks_tableur.xlsx")["Stock 2025"]
valeurs = [v for r in ws.iter_rows(min_row=6, min_col=3, max_col=14, values_only=True) for v in r if v is not None]
texte = [v for v in valeurs if isinstance(v, str) and not v.startswith("=")]
print("feuille :", ws.dimensions, "| cellules fusionnées :", len(ws.merged_cells.ranges), "| cellules de données :", len(valeurs))
print("  « ND » :", texte.count("ND"), "| tirets :", texte.count("—"), "| « rupture » :", texte.count("rupture"), "| nombres écrits en texte avec espace :", len([v for v in texte if v not in ("ND", "—", "rupture")]))
```
<!--sortie-->
```text
catalogue : lignes 118 | familles écrites : 12 pour 6 catégories | désignations avec espaces autour : 19
boutique : produits 120 | noms distincts : 60 | noms portés par deux produits : 60
feuille : A1:N141 | cellules fusionnées : 6 | cellules de données : 1512
  « ND » : 49 | tirets : 22 | « rupture » : 120 | nombres écrits en texte avec espace : 131
```

### Les profils clients et les montants saisis

Deux petits jeux servent aux chapitres de nettoyage proprement dit. **`profil_clients.csv`** donne, pour 6 000 clients, l'âge, le revenu annuel estimé, le nombre de commandes et la dépense de 2025, la satisfaction moyenne et le temps passé sur le site ; trois colonnes ont des **trous**, et ils n'ont pas la même origine, ce qui change tout (section 1.1). **`montants_saisis.csv`** reprend 6 000 lignes de commande de 2024 dans lesquelles ont été glissées des anomalies de saisie, que le chapitre 1 apprend à repérer (section 1.2).

```python hide-code
print("profils : manquants par colonne :", {c: int(n) for c, n in prof.isna().sum().items() if n})
print("part des manquants :", {c: round(float(prof[c].isna().mean()), 3) for c in ["revenu_annuel", "depense_2025", "satisfaction_moy"]})
print("montants saisis : lignes", len(mont), "| médiane", round(float(mont["montant"].median()), 2), "| minimum", float(mont["montant"].min()), "| maximum", float(mont["montant"].max()))
```
<!--sortie-->
```text
profils : manquants par colonne : {'revenu_annuel': 1039, 'depense_2025': 297, 'satisfaction_moy': 562}
part des manquants : {'revenu_annuel': 0.173, 'depense_2025': 0.05, 'satisfaction_moy': 0.094}
montants saisis : lignes 6000 | médiane 31.43 | minimum -153.8 | maximum 26070.0
```

## Les fichiers de vérité

Pour chaque source désordonnée, le script écrit un fichier `verite_*.csv` qui dit **ce qui a été injecté** et ce que la valeur propre aurait dû être.

| Fichier | Ce qu'il contient |
|---|---|
| `verite_crm.csv` | pour chaque ligne du CRM, le vrai client, l'indicateur de doublon et les défauts injectés |
| `verite_identites.csv` | l'identité propre de chaque client (prénom, nom, e-mail) |
| `verite_site.csv` | pour chaque référence de l'export du site, la vraie commande, le vrai total et le défaut |
| `verite_caisse.csv` | pour chaque ligne des fichiers de caisse, la vraie ligne de la base et l'indicateur de doublon |
| `verite_produits.csv` | pour chaque code du fournisseur, le vrai produit de la boutique (ou -1) |
| `verite_stocks.csv` | le vrai stock de chaque produit et de chaque mois |
| `profil_clients_verite.csv` | les valeurs complètes, sans trous |
| `verite_montants.csv` | le type d'anomalie et le vrai montant |

> ⚠️ **Piège.** Ces fichiers sont des **corrigés**, pas des données : dans la vie réelle, il n'y a pas de fichier de vérité, et c'est tout l'intérêt de ce volume d'apprendre à **contrôler sans lui** (chapitre 3). On les ouvre à la fin d'une étude pour mesurer ce qu'on a bien et mal fait, comme on regarde le corrigé d'un exercice après l'avoir cherché. Un nettoyage qui s'appuie sur eux pour décider n'a rien démontré.

## L'environnement de travail

### Python, R et SQL

Les calculs du livre sont faits en **Python** (pandas), en **R** (tidyverse) et en **SQL** (SQLite et DuckDB), comme au volume I. Ce volume ajoute des bibliothèques propres à la préparation des données.

| Bibliothèque | À quoi elle sert | Chapitres |
|---|---|---|
| `pandas`, `polars` | lire, nettoyer, transformer | tous |
| `rapidfuzz`, `jellyfish` | mesurer la ressemblance entre deux textes (distance d'édition, Jaro-Winkler) | 2.5 |
| `unidecode`, `ftfy` | retirer les accents ; réparer un texte abîmé par un mauvais encodage | 1.5 |
| `pandera`, `great-expectations` | écrire des contrôles de qualité exécutables | 3.5 |
| `openpyxl`, `XlsxWriter` | lire et écrire des classeurs Excel | 1, 2, 3 |

```python hide-code
import platform, subprocess
import importlib.metadata as M
print("python", platform.python_version(), "|", ", ".join(f"{p} {M.version(p)}" for p in ["pandas", "numpy", "polars", "openpyxl"]))
print("préparation :", ", ".join(f"{p} {M.version(p)}" for p in ["rapidfuzz", "jellyfish", "Unidecode", "ftfy", "pandera", "great_expectations"]))
print("SQLite", sqlite3.sqlite_version)
print(subprocess.run(["Rscript", "-e", "cat(R.version.string)"], capture_output=True, text=True).stdout.strip())
```
<!--sortie-->
```text
python 3.13.3 | pandas 3.0.6, numpy 2.5.3, polars 2.0.0, openpyxl 3.1.5
préparation : rapidfuzz 3.14.6, jellyfish 1.2.1, Unidecode 1.4.0, ftfy 6.3.1, pandera 0.34.1, great_expectations 1.24.0
SQLite 3.46.1
R version 4.4.3 (2025-02-28)
```

### Le tableur : Excel, LibreOffice et nos maquettes

Même précision d'honnêteté qu'au volume I. **Excel n'est pas installé** sur la machine qui produit ce livre, mais **LibreOffice Calc** l'est : les formules du livre sont **écrites dans des classeurs, recalculées par LibreOffice et comparées aux résultats de pandas**. Les noms de menus et de fonctions varient avec la version et la langue d'Excel : à vérifier dans la vôtre. Ce qui n'est pas exécutable ici (Power Query et son langage M, tableaux croisés dynamiques réels, macros) est signalé **« non exécuté »**, avec un équivalent calculé en pandas quand c'est possible.

### Les captures d'écran

Les copies d'écran ne sont pas toutes de la même nature, et le livre le dit chaque fois dans la légende :

- les **maquettes** sont dessinées avec matplotlib (comme celles de Power Query ou d'un classeur) ;
- les **captures réelles** sont faites sur des outils libres que l'on exécute ici, avec un navigateur sans interface (par exemple un rapport HTML de Great Expectations) ;
- les **images empruntées** à Internet ne le sont que si leur licence autorise la réutilisation ; elles sont alors créditées dans la légende et dans le fichier `figures/credits.md`. Nous n'utilisons pas de captures prises dans la documentation ou le site d'un éditeur de logiciel commercial.

### Régénérer les données et refaire les calculs

Tout le dossier `donnees/` se régénère à l'identique par un script, et les calculs du livre se rejouent par `make check` (qui vérifie que chaque sortie est inchangée).

```bash noexec
python build/donnees_a2.py        # régénère donnees/ (une dizaine de secondes, graines fixes)
make check                        # rejoue tous les blocs de code et signale toute différence
make pdf                          # reconstruit le livre et le cahier en PDF
```

## Conventions du volume

- **Monnaie, villes, canaux** : montants en **€** ; villes « Ville A » à « Ville T » ; canaux `Boutique`, `Site`, `Réseaux`.
- **Personnes** : tous les noms sont **inventés** ; les adresses de messagerie utilisent des domaines réservés aux exemples (`exemple.org`, `courrier.test`, `mail.example`).
- **Nombres** : à la française dans le texte (espace pour les milliers, virgule décimale), à l'anglaise dans les sorties de programme.
- **Dates** : `aaaa-mm-jj` dans les programmes ; les formats `jj/mm/aaaa` ou `mm/jj/aaaa` sont ceux des fichiers reçus.
- **Aléatoire** : toute simulation fixe sa **graine**.
- **Encadrés** : 💡 intuition · 📐 formule · 🧪 expérience · ⚠️ piège · ✅ à retenir · 🧭 repère ou section facultative · 📒 pour s'entraîner · 📦 données.

> ✅ **À retenir.** Les sources du volume sont **simulées et volontairement désordonnées** : un CRM de 7 140 lignes pour 6 000 clients, un export web qui change d'unité en septembre, douze exports de caisse sous trois réglages, un catalogue fournisseur, un tableur saisi à la main, des profils à trous et des montants à anomalies. Les fichiers `verite_*` sont des **corrigés** à n'ouvrir qu'à la fin. Les formules Excel sont vérifiées avec LibreOffice ; les captures d'écran sont des maquettes, des captures d'outils libres ou des images sous licence libre créditées.
