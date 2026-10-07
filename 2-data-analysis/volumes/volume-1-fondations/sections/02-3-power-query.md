## 2.3 Power Query pour l'import et la transformation

Chaque lundi, la gérante reçoit l'export de la caisse, l'ouvre, supprime à la main les lignes de titre, retire la ligne de total, corrige les majuscules, convertit les virgules en points… puis recommence la semaine suivante. **Power Query** est l'outil d'Excel qui remplace ces gestes par une **recette enregistrée** : on la construit une fois, on la rejoue en un clic sur chaque nouvel export. Cette section en explique le principe, montre la recette sur l'export de caisse, et vérifie chaque étape avec pandas.

> ⚠️ **Ce qui est vérifié, et ce qui ne l'est pas.** Power Query est un composant d'Excel (et de Power BI) que nous n'avons pas pu exécuter. Les **scripts en langage M** de cette section sont donc **non exécutés** et leur syntaxe est **à vérifier** dans votre version. En revanche, **chaque étape est reproduite en pandas** sur le vrai fichier `export_caisse_brut.csv`, avec le nombre de lignes à chaque étape et un contrôle final : ce sont les résultats que votre requête doit donner.

### 2.3.1 L'idée : une recette d'étapes enregistrées

Power Query (*Données → Obtenir des données*) ouvre un éditeur dans lequel chaque transformation (supprimer des lignes, changer un type, scinder une colonne, fusionner deux tables…) devient une **étape appliquée**, listée dans un volet à droite. L'ensemble des étapes est la **requête**. Trois propriétés la distinguent d'un nettoyage à la main :

- **elle est rejouable** : sur le prochain fichier, un clic sur *Actualiser* refait toutes les étapes dans le même ordre ;
- **elle est lisible** : les étapes portent un nom, on voit où une donnée a changé ; la requête est aussi un **document** du traitement (section 2.4) ;
- **elle ne touche pas à la source** : le fichier d'origine reste intact, le résultat est chargé dans une feuille ou dans le modèle de données.

Derrière l'interface, chaque étape est une ligne de code dans un langage fonctionnel appelé **M**. On peut l'ignorer au début (on clique), et le lire ensuite pour comprendre ou corriger une requête.

```python hide
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style as S
import outils_xl as X
import outils_ch02 as O

S.setup()
L, P, C = O.charger_2025()
```

### 2.3.2 Importer : formats, encodage, paramètres régionaux

Power Query sait lire des classeurs Excel, des fichiers texte et CSV, des **dossiers entiers** (tous les fichiers d'un répertoire, empilés), des bases de données, des pages web. Pour un fichier texte, **trois réglages** décident de tout, et c'est là que naissent la plupart des erreurs d'import :

- le **délimiteur** (point-virgule, virgule, tabulation) : l'export français utilise le point-virgule parce que la virgule sert de séparateur décimal ;
- l'**encodage** : les anciens exports de Windows sont en `cp1252` (ANSI), les fichiers modernes en UTF-8 ;
- les **paramètres régionaux** (*culture*) : ils définissent la virgule décimale (`52,43`) et l'ordre des dates (`03/11/2025` = jour/mois/année).

Regardons le fichier tel que la caisse le fournit. Nous le lisons **sans rien interpréter** : tout en texte, sans en-tête, en conservant les lignes vides.

```python
brut = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", header=None, dtype=str, skip_blank_lines=False)
print(brut.shape)
print(brut.iloc[:6, :4].fillna("").to_string(header=False))
```
<!--sortie-->
```text
(289, 8)
0             Export caisse - Boutique                                   
1  Période du 03/11/2025 au 09/11/2025                                   
2                                                                        
3                            N° ticket        Date  Heure         Article
4                               T33133  03/11/2025  09:00  BOÎTE RUSTIQUE
5                               T33137  03/11/2025  10:35  Tapis nordique
```

Le fichier compte **289 lignes** et 8 colonnes. On y voit un **titre**, une ligne de **période**, une ligne **vide**, puis l'en-tête réel (`N° ticket`, `Date`, …) à la quatrième ligne. Un import automatique, qui supposerait un en-tête en première ligne, rangerait ce titre dans les noms de colonnes et ferait de toutes les colonnes du **texte**.

```python hide-code
octets = open("donnees/export_caisse_brut.csv", "rb").read()
print("caractères illisibles si l'on décode en UTF-8 au lieu de cp1252 :", octets.decode("utf-8", errors="replace").count("�"))
mal = pd.to_datetime(brut.iloc[4:, 1].dropna().iloc[:3])
print("dates 03/11/2025 lues « à l'américaine » :", [d.strftime("%d/%m/%Y") for d in mal.tolist()])
```
<!--sortie-->
```text
caractères illisibles si l'on décode en UTF-8 au lieu de cp1252 : 169
dates 03/11/2025 lues « à l'américaine » : ['11/03/2025', '11/03/2025', '11/03/2025']
```

Deux erreurs d'import illustrent les réglages. Avec le **mauvais encodage**, 169 caractères accentués sont illisibles (`é` devient `�`) : un `Boîte` ne correspond plus à rien. Avec les **mauvais paramètres régionaux**, le 3 novembre (`03/11/2025`) est lu comme le **11 mars** : les trois premières dates se retrouvent au 11/03/2025. Comme toutes les dates de cette semaine ont un jour inférieur à 10 et le mois 11, **toutes** les lignes seraient décalées de plusieurs mois, sans le moindre message d'erreur.

### 2.3.3 Les étapes de nettoyage, une à une

Voici la recette pour l'export de caisse. Pour chaque étape, nous donnons l'opération de Power Query (son nom français dans l'interface, **à vérifier** selon la version) et l'équivalent pandas, avec le **nombre de lignes** après l'étape.

| # | Étape Power Query | Équivalent pandas | Lignes après |
|---|---|---|---|
| 1 | Supprimer les premières lignes (3) | `.iloc[3:]` | 286 |
| 2 | Utiliser la première ligne comme en-têtes | `.columns = …` | 285 |
| 3 | Supprimer les lignes d'en-tête répétées (filtrer `N° ticket` ≠ `N° ticket`) | `[t["N° ticket"] != "N° ticket"]` | 281 |
| 4 | Supprimer la ligne de total (filtrer les `Qté` vides) | `[t["Qté"].notna()]` | 280 |
| 5 | Changer les types (avec les paramètres régionaux `fr-FR`) | `to_datetime(format=…)`, `astype` | 280 |
| 6 | Nettoyer le texte (espaces, majuscules) | `.str.strip().str.capitalize()` | 280 |
| 7 | Ajouter une colonne : montant corrigé | `fillna(Qté × Prix)` | 280 |

```python
t = brut.iloc[3:].reset_index(drop=True)
t.columns = t.iloc[0]; t = t.iloc[1:].reset_index(drop=True)
n_apres_entete = len(t)
t = t[t["N° ticket"] != "N° ticket"]; n_sans_repetes = len(t)
t = t[t["Qté"].notna()].copy(); n_sans_total = len(t)
print(len(brut), "→", n_apres_entete, "→", n_sans_repetes, "→", n_sans_total, "lignes")
```
<!--sortie-->
```text
289 → 285 → 281 → 280 lignes
```

On passe de 289 lignes à **280 lignes de vente** : trois lignes de titre, l'en-tête réel, quatre en-têtes répétés (l'export les a reproduits à chaque « page ») et une ligne de total. La ligne de total est précieuse : nous la conservons de côté, elle servira de **total de contrôle**.

Viennent les types et le texte :

```python
for c in ["Prix unitaire", "Montant"]:
    t[c] = t[c].str.replace(",", ".").astype(float)          # virgule décimale -> point
t["Qté"] = t["Qté"].astype(int)
t["Date"] = pd.to_datetime(t["Date"], format="%d/%m/%Y")
t["Article"] = t["Article"].str.strip().str.capitalize()      # « BOÎTE RUSTIQUE » -> « Boîte rustique »
t["Catégorie"] = t["Catégorie"].str.strip().str.capitalize()  # « maison » -> « Maison »
print(t["Catégorie"].value_counts().to_dict())
print("montants manquants :", int(t["Montant"].isna().sum()))
```
<!--sortie-->
```text
{'Décoration': 68, 'Maison': 52, 'Cuisine': 50, 'Papeterie': 40, 'Bien-être': 38, 'Jardin': 32}
montants manquants : 8
```

Deux choix méritent l'attention. D'abord la **casse** : la fonction « Première lettre de chaque mot en majuscule » de Power Query (`Text.Proper`) donnerait `Bien-Être` et `Bol Design`, qui ne correspondent plus au catalogue (`Bien-être`, `Bol design`) ; la bonne transformation est **une majuscule initiale, le reste en minuscules** (`Text.Upper` du premier caractère, `Text.Lower` du reste). Ensuite les **8 montants manquants** : que mettre ?

#### Combler les montants manquants, et se contrôler

Une solution naturelle est de recalculer `Qté × Prix unitaire`. Mais la ligne de total du fichier permet de **vérifier** cette réparation : elle annonce 11 561,47 €.

```python hide-code
total_fichier = float(brut.iloc[-1, 7].replace(",", "."))
t["Montant corrigé"] = t["Montant"].fillna((t["Qté"] * t["Prix unitaire"]).round(2))
print("total annoncé par l'export :", O.fr(total_fichier), "| somme après réparation :", O.fr(t["Montant corrigé"].sum()), "| écart :", O.fr(t["Montant corrigé"].sum() - total_fichier))
```
<!--sortie-->
```text
total annoncé par l'export : 11 561,47 | somme après réparation : 11 564,09 | écart : 2,62
```

La somme réparée vaut **11 564,09 €** contre **11 561,47 €** : un écart de **2,62 €**. La réparation est donc **un peu trop généreuse** : les huit lignes concernées appartiennent à des tickets qui avaient une **remise** (code promo), et `Qté × Prix` l'ignore. Le contrôle ne dit pas *quelle* ligne est fausse, mais il **prouve** qu'il y a un écart, ce qu'une réparation silencieuse n'aurait jamais révélé. Deux attitudes sont défendables : signaler l'écart et laisser un indicateur « montant estimé » dans une colonne, ou aller chercher la remise dans la source (ici la table des commandes). **Ne jamais réparer sans contrôler.**

Voici la requête complète en langage M (non exécutée) ; les étapes portent les noms de l'éditeur.

```text
let
    Source = Csv.Document(File.Contents("export_caisse_brut.csv"), [Delimiter=";", Columns=8, Encoding=1252]),
    SansTitre = Table.Skip(Source, 3),
    EnTetes = Table.PromoteHeaders(SansTitre, [PromoteAllScalars=true]),
    SansRepetes = Table.SelectRows(EnTetes, each [#"N° ticket"] <> "N° ticket"),
    SansTotal = Table.SelectRows(SansRepetes, each [Qté] <> null and [Qté] <> ""),
    Types = Table.TransformColumnTypes(SansTotal, {{"Date", type date}, {"Qté", Int64.Type},
             {"Prix unitaire", type number}, {"Montant", type number}}, "fr-FR"),
    Texte = Table.TransformColumns(Types, {{"Article", each Text.Upper(Text.Start(Text.Trim(_), 1)) & Text.Lower(Text.Middle(Text.Trim(_), 1))},
             {"Catégorie", each Text.Upper(Text.Start(Text.Trim(_), 1)) & Text.Lower(Text.Middle(Text.Trim(_), 1))}}),
    Corrige = Table.AddColumn(Texte, "Montant corrigé", each if [Montant] = null then [Qté] * [Prix unitaire] else [Montant], type number)
in
    Corrige
```

*Syntaxe à vérifier dans votre version de Power Query, en particulier les noms de colonnes entre `#"…"` et le traitement de la colonne `Qté` vide.*

```python hide
fig, ax = plt.subplots(figsize=(7.6, 3.1))
ax.set_xlim(0, 12); ax.set_ylim(4.4, 0); ax.axis("off")
ax.add_patch(plt.Rectangle((0, 0), 3.7, 4.3, fc="white", ec=S.AXE, lw=1))
ax.text(0.15, 0.3, "Étapes appliquées", fontsize=9, weight="bold", va="center", color=S.ENCRE)
etapes = ["Source", "Lignes du haut supprimées", "En-têtes promus", "Doublons d'en-tête filtrés", "Total supprimé", "Types modifiés", "Texte nettoyé", "Montant corrigé"]
for i, e in enumerate(etapes):
    y = 0.65 + 0.46 * i
    ax.add_patch(plt.Rectangle((0.12, y), 3.45, 0.38, fc="#e8f1fc" if i == len(etapes) - 1 else "#f3f2ee", ec=S.AXE, lw=0.6))
    ax.text(0.28, y + 0.19, f"✓ {e}" if i < len(etapes) - 1 else f"▶ {e}", fontsize=7.2, va="center", color=S.ENCRE)
ax.add_patch(plt.Rectangle((3.95, 0), 7.95, 4.3, fc="white", ec=S.AXE, lw=1))
ax.text(4.1, 0.3, "Aperçu du résultat (280 lignes)", fontsize=9, weight="bold", va="center", color=S.ENCRE)
cols = ["N° ticket", "Date", "Article", "Catégorie", "Qté", "Montant corrigé"]
xs = [4.1, 5.4, 6.8, 8.7, 9.95, 10.4]
for x, c in zip(xs, cols):
    ax.text(x, 0.8, c, fontsize=6.6, weight="bold", va="center", color=S.ENCRE2)
ax.plot([4.05, 11.85], [1.0, 1.0], color=S.AXE, lw=0.8)
for i, r in enumerate(t.head(7).itertuples(index=False)):
    vals = [r[0], r[1].strftime("%d/%m/%Y"), r[3], r[4], str(r[5]), O.fr(r[8])]
    for x, v in zip(xs, vals):
        ax.text(x, 1.3 + 0.4 * i, v, fontsize=6.6, va="center", color=S.ENCRE)
S.save(fig, "ch02-power-query.png")
```
<!--sortie-->
```text
figure : ch02-power-query.png
```

![L'éditeur de Power Query : à gauche, les étapes appliquées (chacune rejouable) ; à droite, l'aperçu du résultat. Schéma dessiné avec matplotlib, avec les vraies valeurs de l'export, pas une capture d'écran.](figures/ch02-power-query.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercice 2.8.

### 2.3.4 Scinder, fusionner des colonnes, dépivoter

Trois transformations de forme reviennent sans cesse.

**Scinder une colonne.** Le numéro de ticket `T33133` mélange une lettre et un nombre. *Fractionner la colonne → par nombre de caractères* donne `T` et `33133`, ce que fait en pandas `t["N° ticket"].str[0]` et `.str[1:]`. On peut aussi scinder `Nom Prénom` par délimiteur (l'espace), une adresse par virgule.

**Fusionner des colonnes.** L'inverse : `Date` et `Heure` (deux colonnes de texte) deviennent un seul horodatage utilisable pour trier ou regrouper.

**Dépivoter.** Beaucoup de tableaux de reporting sont **larges** : une ligne par catégorie, une colonne par mois. Pour un TCD, un graphique ou une jointure, il faut le format **long** : une ligne par couple (catégorie, mois). L'opération *Dépivoter les colonnes* (*unpivot*) fait ce passage ; l'inverse est *Pivoter*. Prenons le tableau large du chiffre d'affaires par catégorie et par mois de 2025 : 6 lignes et 12 colonnes de mois.

```python
large = L.assign(mois=L["date_commande"].dt.to_period("M").astype(str)).pivot_table(index="categorie", columns="mois", values="montant", aggfunc="sum")
long = large.reset_index().melt(id_vars="categorie", var_name="mois", value_name="montant")
print(large.shape, "→", long.shape, "| total conservé :", round(long["montant"].sum(), 2))
```
<!--sortie-->
```text
(6, 12) → (72, 3) | total conservé : 1324763.72
```

Les 6 × 12 cases deviennent **72 lignes**, et le total (1 324 763,72 €) est **conservé** : c'est le contrôle de toute restructuration. Le format long est celui que les outils d'analyse attendent (chapitre 4 du volume) : une colonne par variable, une ligne par observation.

### 2.3.5 Fusionner et ajouter des requêtes

**Ajouter** des requêtes (*Append*) empile des tables de même structure : les exports de chaque semaine de l'année, par exemple. Avec l'option **Dossier**, Power Query lit tous les fichiers d'un répertoire et les empile : déposer le fichier de la semaine suivante dans le dossier suffit, un clic sur *Actualiser* met tout à jour. Notez que les fichiers doivent avoir **la même structure** (mêmes colonnes, même ordre) : un export dont une colonne a changé de nom fait échouer toute la requête, ce qui est **un bon signe** (l'erreur est visible).

**Fusionner** des requêtes (*Merge*) est une **jointure** : on rattache à chaque ligne d'une table des colonnes d'une autre, à partir d'une clé commune. Les types de jointure de Power Query ont leur équivalent pandas et SQL (chapitre 3) :

| Power Query | pandas | Ce que l'on garde |
|---|---|---|
| Externe gauche | `how="left"` | toutes les lignes de la table de gauche |
| Interne | `how="inner"` | seulement les lignes qui ont une correspondance |
| Anti gauche | `how="left"` puis filtre sur le manque | les lignes **sans** correspondance |

Rattachons à l'export de caisse le **coût d'achat** du catalogue, pour calculer la marge de la semaine. L'export ne contient pas l'identifiant du produit, seulement le **nom de l'article** : la clé de jointure sera le nom.

```python
cle = lambda s: s.str.lower()
prod = P.assign(cle=cle(P["nom_produit"]))
t["cle"] = cle(t["Article"])
m1 = t.merge(prod[["cle", "cout_achat"]], on="cle", how="left")
print(len(t), "lignes avant,", len(m1), "après la jointure sur le seul nom | total", O.fr(m1["Montant corrigé"].sum()))
```
<!--sortie-->
```text
280 lignes avant, 560 après la jointure sur le seul nom | total 23 128,18
```

**Le nombre de lignes a doublé** (280 → 560) et le total aussi (23 128,18 € au lieu de 11 564,09 €) : le nom d'article **n'est pas une clé**. Le catalogue compte 120 produits mais seulement **60 noms distincts** : chaque nom désigne deux produits, à des prix différents. La jointure rattache chaque ligne de vente à **chacun** des deux produits, et personne ne reçoit de message d'erreur. C'est l'erreur de fusion la plus coûteuse : **toujours vérifier le nombre de lignes avant et après une jointure**.

Pour lever l'ambiguïté, ajoutons le **prix** à la clé : le prix de caisse de novembre 2025 est le prix du catalogue majoré de 3 % (hausse du 1ᵉʳ janvier 2025, arrondie au centime).

```python
prod["prix_caisse"] = (prod["prix_vente"] * 1.03).round(2)
m2 = t.merge(prod[["cle", "prix_caisse", "cout_achat"]], left_on=["cle", "Prix unitaire"], right_on=["cle", "prix_caisse"], how="left")
print(len(t), "→", len(m2), "lignes | sans correspondance :", int(m2["prix_caisse"].isna().sum()))
doublons_cat = prod[prod.duplicated(["cle", "prix_caisse"], keep=False)][["id_produit", "nom_produit", "prix_vente", "cout_achat"]]
print(doublons_cat.to_string(index=False))
```
<!--sortie-->
```text
280 → 285 lignes | sans correspondance : 0
 id_produit nom_produit  prix_vente  cout_achat
         62  Carnet mat         2.9        1.53
         72  Carnet mat         2.9        1.53
```

Le résultat compte 285 lignes pour 280 attendues : **cinq lignes sont encore doublées**, parce que le catalogue lui-même contient **deux produits identiques** (`Carnet mat`, identifiants 62 et 72, même prix, même coût). C'est une anomalie du **catalogue** à signaler à son propriétaire ; en attendant, on **supprime les doublons du catalogue** avant de fusionner (l'étape *Supprimer les doublons* de Power Query).

```python hide-code
prod_u = prod.drop_duplicates(["cle", "prix_caisse"])
m3 = t.merge(prod_u[["cle", "prix_caisse", "cout_achat"]], left_on=["cle", "Prix unitaire"], right_on=["cle", "prix_caisse"], how="left")
m3["marge"] = m3["Montant corrigé"] - m3["Qté"] * m3["cout_achat"]
src = L[L["id_commande"].isin(t["N° ticket"].str[1:].astype(int))]
print("après dédoublonnage du catalogue :", len(m3), "lignes | sans correspondance :", int(m3["cout_achat"].isna().sum()))
print("marge de la semaine :", O.fr(m3["marge"].sum()), "€ sur", O.fr(m3["Montant corrigé"].sum()), "€ de ventes")
print("recoupement avec la base : lignes", len(src), "| montant", O.fr(src["montant"].sum()), "| total de contrôle du fichier", O.fr(total_fichier))
```
<!--sortie-->
```text
après dédoublonnage du catalogue : 280 lignes | sans correspondance : 0
marge de la semaine : 5 715,57 € sur 11 564,09 € de ventes
recoupement avec la base : lignes 280 | montant 11 561,47 | total de contrôle du fichier 11 561,47
```

Après dédoublonnage, la jointure rend bien **280 lignes**, toutes appariées. La marge de la semaine est de **5 715,57 €** sur 11 564,09 € de ventes (avec le montant réparé) ; et le recoupement avec la base des ventes confirme le **total de contrôle** : 280 lignes, 11 561,47 €, exactement la valeur de la ligne de total de l'export. Les 2,62 € de l'écart de réparation sont donc bien des remises que `Qté × Prix` ignorait.

Voici la fusion en langage M (non exécutée) :

```text
Fusion = Table.NestedJoin(Corrige, {"Article", "Prix unitaire"}, Catalogue, {"Nom", "PrixCaisse"}, "Cat", JoinKind.LeftOuter),
Colonnes = Table.ExpandTableColumn(Fusion, "Cat", {"cout_achat"})
```

### 2.3.6 Power Query, formules ou Python ?

| | Formules Excel | Power Query | Python / SQL |
|---|---|---|---|
| Point fort | immédiat, visible | rejouable sans code | très gros volumes, reproductible, versionnable |
| Point faible | difficile à rejouer proprement | outil propre à l'écosystème Microsoft | demande d'apprendre un langage |
| À choisir pour | calculs ponctuels, petits tableaux | **import et nettoyage récurrents de fichiers** | traitements lourds ou à partager en équipe |

> 🧭 **En pratique.** Si vous faites deux fois la même manipulation de fichier, **faites-en une requête**. Si le fichier dépasse le million de lignes, ou si le traitement doit tourner sans personne, passez à SQL ou à Python (chapitres 3 et 4).

> ✅ **À retenir.**
> - Une requête Power Query est une **liste d'étapes rejouables** ; elle ne modifie pas la source.
> - Trois réglages d'import décident de tout : **délimiteur, encodage, paramètres régionaux** (sur notre export : 169 caractères illisibles avec le mauvais encodage ; toutes les dates décalées avec les mauvais paramètres).
> - **Compter les lignes à chaque étape** (289 → 280 sur l'export) et **contrôler un total** (11 561,47 €) : l'écart de 2,62 € a révélé que la réparation ignorait des remises.
> - Une jointure sur une clé **non unique** multiplie les lignes (280 → 560) sans erreur : vérifiez l'unicité des clés et le nombre de lignes avant/après.
> - Dépivoter conserve le total (72 lignes, 1 324 763,72 €) : la restructuration se contrôle comme le reste.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercices 2.8 et 2.9.
