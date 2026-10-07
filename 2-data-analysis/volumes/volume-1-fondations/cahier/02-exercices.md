# Chapitre 2 : Excel — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 2 du livre. Il contient **huit applications guidées** (de petites études sur le classeur de la gérante, à refaire pas à pas) et **douze exercices** de difficulté croissante (⭐ à la main, ⭐⭐ avec un peu de code, ⭐⭐⭐ à construire), tous **corrigés** à la fin. Rappel : Excel n'est pas installé sur la machine qui produit le livre ; **toutes les formules sont calculées avec LibreOffice** par `O.evaluer` (formules écrites avec les **noms anglais** du fichier `.xlsx`), puis **recoupées avec pandas**. Pour les voir comme dans votre Excel, `X.en_fr(formule)` les convertit en français. Les tableaux croisés dynamiques, Power Query, DAX, VBA, Google Sheets et Looker Studio ne sont pas exécutables ici : nous recalculons les résultats attendus en pandas ou en SQL.

```python
import os, sys, sqlite3, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_xl as X
import outils_ch02 as O

L, P, C = O.charger_2025()                      # lignes de 2025, catalogue, clients (identiques aux feuilles de ventes_2025.xlsx)
n = len(L) + 1                                  # dernière ligne de données de la feuille Lignes
R = lambda c: f"Lignes!{c}2:{c}{n}"              # plage d'une colonne de la feuille Lignes
print(len(L), "lignes de ventes en 2025 ;", len(P), "produits ;", len(C), "clients")
```
<!--sortie-->
```text
29827 lignes de ventes en 2025 ; 120 produits ; 6000 clients
```

## Applications

### Application 2.1 — Explorer et contrôler le classeur (introduction, section 2.4)

**Objectif.** Ouvrir un classeur inconnu comme le ferait un analyste : formes, types, valeurs manquantes, contrôles de base, recoupement avec la base de données.

**Étape 1 — ce que contient le fichier.** On lit les trois feuilles avec pandas et l'on regarde les types.

```python
x = pd.read_excel("donnees/ventes_2025.xlsx", sheet_name=None)
print({k: v.shape for k, v in x.items()})
print(dict(x["Lignes"].dtypes.astype(str)))
print("valeurs manquantes :", x["Lignes"].isna().sum()[lambda s: s > 0].to_dict())
```
<!--sortie-->
```text
{'Lignes': (29827, 13), 'Produits': (120, 6), 'Clients': (6000, 5)}
{'id_ligne': 'int64', 'id_commande': 'int64', 'date_commande': 'datetime64[us]', 'id_client': 'int64', 'canal': 'str', 'code_promo': 'str', 'id_produit': 'int64', 'nom_produit': 'str', 'categorie': 'str', 'quantite': 'int64', 'prix_unitaire': 'float64', 'remise_pct': 'int64', 'montant': 'float64'}
valeurs manquantes : {'code_promo': 25221}
```

**Étape 2 — des contrôles de cohérence.** Les identifiants sont-ils uniques ? Les montants positifs ? La période complète ? Le montant d'une ligne est-il bien `prix × quantité × (1 − remise)` ?

```python
lg = x["Lignes"]
print("identifiants de ligne uniques :", lg["id_ligne"].is_unique, "| montants ≤ 0 :", int((lg["montant"] <= 0).sum()))
print("période :", lg["date_commande"].min().date(), "→", lg["date_commande"].max().date())
ecart = (lg["quantite"] * lg["prix_unitaire"] * (1 - lg["remise_pct"] / 100) - lg["montant"]).abs()
print("écart maximal sur une ligne :", round(float(ecart.max()), 4), "€ (arrondi au centime) | lignes avec un écart > 1 centime :", int((ecart > 0.0101).sum()))
```
<!--sortie-->
```text
identifiants de ligne uniques : True | montants ≤ 0 : 0
période : 2025-01-01 → 2025-12-31
écart maximal sur une ligne : 0.005 € (arrondi au centime) | lignes avec un écart > 1 centime : 0
```

**Étape 3 — recoupement avec la base.** Le classeur est un extrait de la base `boutique.db` ; leurs totaux doivent être identiques.

```python
con = sqlite3.connect("donnees/boutique.db")
tot_bdd = con.execute("SELECT ROUND(SUM(l.montant), 2), COUNT(*) FROM lignes_commande l JOIN commandes c ON c.id_commande = l.id_commande WHERE c.date_commande >= '2025-01-01'").fetchone()
print("base :", tot_bdd, "| classeur :", (round(float(lg["montant"].sum()), 2), len(lg)))
```
<!--sortie-->
```text
base : (1324763.72, 29827) | classeur : (1324763.72, 29827)
```

**À vous.** Ajoutez un contrôle sur la colonne `canal` : quelles valeurs contient-elle, et combien de lignes par valeur ? Rédigez en trois lignes le « README » du classeur.

### Application 2.2 — Agréger sous conditions (section 2.1.4)

**Objectif.** Calculer par formules quelques indicateurs de la gérante et vérifier chacun avec pandas.

**Étape 1 — les formules (noms anglais), évaluées par LibreOffice.**

```python
F = {"CA Site": f'=SUMIFS({R("M")},{R("E")},"Site")',
     "lignes remisées": f'=COUNTIFS({R("L")},">0")',
     "CA Décoration en décembre": f'=SUMIFS({R("M")},{R("I")},"Décoration",{R("C")},">="&DATE(2025,12,1))',
     "montant moyen d'une ligne": f"=AVERAGE({R('M')})"}
res = O.evaluer(F, {"Lignes": L})
for k, f in F.items():
    print(f"{k:28s} → {O.fr(res[k]):>12s}")
print("exemple de formule :", X.en_fr(F["CA Site"]))
```
<!--sortie-->
```text
CA Site                      →   617 715,45
lignes remisées              →        4 606
CA Décoration en décembre    →    60 891,04
montant moyen d'une ligne    →        44,41
exemple de formule : =SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Site")
```

**Étape 2 — le recoupement avec pandas.**

```python
d = L[L["categorie"] == "Décoration"]
attendu = {"CA Site": L.loc[L["canal"] == "Site", "montant"].sum(), "lignes remisées": (L["remise_pct"] > 0).sum(),
           "CA Décoration en décembre": d.loc[d["date_commande"] >= "2025-12-01", "montant"].sum(), "montant moyen d'une ligne": L["montant"].mean()}
ecarts = {k: abs(float(res[k]) - float(v)) for k, v in attendu.items()}
print("écart maximal :", round(max(ecarts.values()), 6))
```
<!--sortie-->
```text
écart maximal : 0.0
```

**À vous.** Ajoutez la formule du nombre de lignes du canal `Réseaux` vendues en juillet, puis celle du montant moyen d'une ligne remisée. Vérifiez par pandas.

### Application 2.3 — Enrichir par recherche : le coût d'achat et la marge (section 2.1.6)

**Objectif.** Ajouter à chaque ligne le coût d'achat du produit par une recherche, puis calculer la marge par catégorie.

**Étape 1 — une colonne de recherche** (29 827 formules `XLOOKUP`) et la marge par catégorie.

```python
cats = sorted(L["categorie"].unique())
F = {f"marge {c}": f'=SUMPRODUCT(({R("I")}="{c}")*({R("M")}-{R("J")}*Lignes!N2:N{n}))' for c in cats}
F["marge totale"] = f"=SUM({R('M')})-SUMPRODUCT({R('J')},Lignes!N2:N{n})"
res = O.evaluer(F, {"Lignes": L, "Produits": P}, colonnes={"Lignes": {"cout_u": "=XLOOKUP(G{r},Produits!A:A,Produits!E:E)"}})
print(pd.Series({k: round(v, 2) for k, v in res.items()}).to_string())
```
<!--sortie-->
```text
marge Bien-être      53943.61
marge Cuisine       111442.65
marge Décoration    128773.48
marge Jardin        171875.43
marge Maison        146928.68
marge Papeterie      26847.03
marge totale        639810.88
```

**Étape 2 — recoupement par fusion pandas.**

```python
M = L.merge(P[["id_produit", "cout_achat"]], on="id_produit")
M["marge"] = M["montant"] - M["quantite"] * M["cout_achat"]
att = M.groupby("categorie")["marge"].sum()
print("écart maximal par catégorie :", round(max(abs(res[f"marge {c}"] - att[c]) for c in cats), 6), "| écart sur le total :", round(abs(res["marge totale"] - M["marge"].sum()), 6))
```
<!--sortie-->
```text
écart maximal par catégorie : 0.0 | écart sur le total : 0.0
```

**Étape 3 — le piège de la correspondance approchée.** Une table de produits non triée et une recherche avec `VRAI` (ou sans quatrième argument) :

```python
extra = {"Ref": [["id", "nom"], [7, "Moule mat"], [3, "Bol design"], [12, "Poêle mat"], [5, "Cadre design"]]}
r = O.evaluer({"exacte": "=VLOOKUP(5,Ref!A2:B5,2,FALSE)", "approchée": "=VLOOKUP(5,Ref!A2:B5,2,TRUE)"}, extra=extra)
print(r)
```
<!--sortie-->
```text
{'exacte': 'Cadre design', 'approchée': '#N/A'}
```

**À vous.** Calculez le **taux de marge** (marge / chiffre d'affaires) de chaque catégorie par formules, puis comparez à celui du TCD de la section 2.2.4 (ratio de sommes).

### Application 2.4 — Nettoyer du texte et des dates (sections 2.1.7 et 2.1.8)

**Objectif.** Nettoyer les premières lignes de l'export de caisse avec des formules, et comparer avec pandas.

**Étape 1 — lire l'export en texte** (sans interpréter) et extraire douze lignes de vente.

```python
brut = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", header=None, dtype=str, skip_blank_lines=False)
ech = brut.iloc[4:16, [0, 1, 3]].reset_index(drop=True)
ech.columns = ["ticket", "date", "article"]
print(ech.head(4).to_string())
```
<!--sortie-->
```text
   ticket        date             article
0  T33133  03/11/2025      BOÎTE RUSTIQUE
1  T33137  03/11/2025      Tapis nordique
2  T33137  03/11/2025  Statuette rustique
3  T33137  03/11/2025     Étagère compact
```

**Étape 2 — les formules, ligne par ligne.** Numéro de ticket, date, article en « majuscule initiale » (la fonction `NOMPROPRE` mettrait une majuscule à chaque mot : nous utiliserons plutôt `MAJUSCULE(GAUCHE(…))` et `MINUSCULE(STXT(…))`).

```python
lignes = [["ticket", "date", "article"]] + ech.values.tolist()
F = {}
for i in range(len(ech)):
    r = i + 2
    F[f"num{i}"] = f"=VALUE(RIGHT(Export!A{r},LEN(Export!A{r})-1))"
    F[f"date{i}"] = f"=DATEVALUE(Export!B{r})"
    F[f"art{i}"] = f"=UPPER(LEFT(TRIM(Export!C{r}),1))&LOWER(MID(TRIM(Export!C{r}),2,100))"
res = O.evaluer(F, extra={"Export": lignes})
nums = [int(res[f"num{i}"]) for i in range(len(ech))]; arts = [res[f"art{i}"] for i in range(len(ech))]
dates = [pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(res[f"date{i}"])) for i in range(len(ech))]
print(nums[:4], arts[:4], [d.strftime("%d/%m/%Y") for d in dates[:3]])
```
<!--sortie-->
```text
[33133, 33137, 33137, 33137] ['Boîte rustique', 'Tapis nordique', 'Statuette rustique', 'Étagère compact'] ['03/11/2025', '03/11/2025', '03/11/2025']
```

**Étape 3 — recoupement.**

```python
att_num = ech["ticket"].str[1:].astype(int).tolist()
att_art = ech["article"].str.strip().str.capitalize().tolist()
att_dat = pd.to_datetime(ech["date"], format="%d/%m/%Y").tolist()
print("numéros identiques :", nums == att_num, "| articles identiques :", arts == att_art, "| dates identiques :", dates == att_dat)
```
<!--sortie-->
```text
numéros identiques : True | articles identiques : True | dates identiques : True
```

**À vous.** Que donnerait `NOMPROPRE` sur `bien-être` ? Et sur `BOÎTE RUSTIQUE` ? Dans quel cas la différence compte-t-elle (indice : une jointure avec le catalogue) ?

### Application 2.5 — Recouper un tableau croisé dynamique (section 2.2)

**Objectif.** Construire le tableau croisé « catégorie × trimestre » comme le ferait Excel (avec pandas), puis le recouper avec des `SOMME.SI.ENS`.

**Étape 1 — le tableau attendu.**

```python
pt = L.assign(trimestre=L["date_commande"].dt.quarter).pivot_table(index="categorie", columns="trimestre", values="montant", aggfunc="sum", margins=True, margins_name="Total")
print(pt.round(2).to_string())
```
<!--sortie-->
```text
trimestre           1          2          3          4       Total
categorie                                                         
Bien-être    27442.93   26028.04   20767.18   43272.69   117510.84
Cuisine      53688.76   52530.23   42320.21   84773.38   233312.58
Décoration   55146.61   51061.80   43924.15  108609.77   258742.33
Jardin       29892.76  102809.91  143416.32   77835.65   353954.64
Maison       73190.94   65747.55   52308.41  113367.10   304614.00
Papeterie    12246.69   12605.15   11835.70   19941.79    56629.33
Total       251608.69  310782.68  314571.97  447800.38  1324763.72
```

**Étape 2 — 24 formules `SOMME.SI.ENS`** (6 catégories × 4 trimestres), avec des bornes de dates.

```python
bornes = {1: (1, 4), 2: (4, 7), 3: (7, 10), 4: (10, 13)}
F = {}
for c in cats:
    for q, (m1, m2) in bornes.items():
        fin = "DATE(2026,1,1)" if m2 == 13 else f"DATE(2025,{m2},1)"
        F[(c, q)] = f'=SUMIFS({R("M")},{R("I")},"{c}",{R("C")},">="&DATE(2025,{m1},1),{R("C")},"<"&{fin})'
res = O.evaluer({f"{c}|{q}": f for (c, q), f in F.items()}, {"Lignes": L})
```

**Étape 3 — comparer, et lire les proportions.**

```python
grille = pd.DataFrame({q: [res[f"{c}|{q}"] for c in cats] for q in bornes}, index=cats)
print("écart maximal :", round(float((grille - pt.loc[cats, [1, 2, 3, 4]]).abs().max().max()), 6))
print("part de chaque trimestre dans l'année (%) :", (pt.loc["Total", [1, 2, 3, 4]] / pt.loc["Total", "Total"] * 100).round(1).to_dict())
```
<!--sortie-->
```text
écart maximal : 0.0
part de chaque trimestre dans l'année (%) : {1: 19.0, 2: 23.5, 3: 23.7, 4: 33.8}
```

**À vous.** Quelle catégorie est la plus saisonnière ? Proposez une mesure (rapport du meilleur trimestre au moins bon) et calculez-la.

### Application 2.6 — Rejouer une chaîne Power Query sur plusieurs fichiers (section 2.3)

**Objectif.** Écrire une fonction qui reproduit les étapes de la requête de la section 2.3, l'appliquer à l'export de caisse, puis « empiler le dossier » avec un second fichier.

**Étape 1 — la fonction de nettoyage** (une étape de Power Query par ligne).

```python
def nettoyer(chemin):
    b = pd.read_csv(chemin, sep=";", encoding="cp1252", header=None, dtype=str, skip_blank_lines=False)
    total = float(b.iloc[-1, 7].replace(",", "."))                          # ligne de total, gardée pour le contrôle
    t = b.iloc[3:].reset_index(drop=True); t.columns = t.iloc[0]; t = t.iloc[1:]
    t = t[t["N° ticket"] != "N° ticket"]; t = t[t["Qté"].notna()].copy()
    for c in ["Prix unitaire", "Montant"]:
        t[c] = t[c].str.replace(",", ".").astype(float)
    t["Qté"] = t["Qté"].astype(int); t["Date"] = pd.to_datetime(t["Date"], format="%d/%m/%Y")
    t["Article"] = t["Article"].str.strip().str.capitalize(); t["Catégorie"] = t["Catégorie"].str.strip().str.capitalize()
    t["Montant corrigé"] = t["Montant"].fillna((t["Qté"] * t["Prix unitaire"]).round(2))
    return t.reset_index(drop=True), total

s1, total1 = nettoyer("donnees/export_caisse_brut.csv")
print(len(s1), "lignes | total de contrôle", O.fr(total1), "| somme corrigée", O.fr(s1["Montant corrigé"].sum()))
```
<!--sortie-->
```text
280 lignes | total de contrôle 11 561,47 | somme corrigée 11 564,09
```

**Étape 2 — un second fichier.** Nous fabriquons un « fichier de la semaine suivante » en décalant les dates de sept jours (ce n'est qu'une simulation).

```python
import tempfile, shutil
txt1 = open("donnees/export_caisse_brut.csv", encoding="cp1252").read()
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
open(f"{dossier}/semaine_1.csv", "w", encoding="cp1252").write(txt1)
txt2 = txt1
for jj in range(3, 10):                               # 03/11 → 10/11, …, 09/11 → 16/11 (aucune collision)
    txt2 = txt2.replace(f";{jj:02d}/11/2025;", f";{jj + 7:02d}/11/2025;")
open(f"{dossier}/semaine_2.csv", "w", encoding="cp1252").write(txt2)
```

**Étape 3 — empiler le dossier et contrôler.**

```python
parts = [nettoyer(f"{dossier}/{f}") for f in sorted(os.listdir(dossier))]
tout = pd.concat([p[0] for p in parts], ignore_index=True)
print(len(tout), "lignes | du", tout["Date"].min().date(), "au", tout["Date"].max().date(), "| total de contrôle cumulé", O.fr(sum(p[1] for p in parts)))
shutil.rmtree(dossier)
```
<!--sortie-->
```text
560 lignes | du 2025-11-03 au 2025-11-16 | total de contrôle cumulé 23 122,94
```

**À vous.** Que se passe-t-il si un fichier du dossier a une colonne de plus ? Quelle étape échoue, et pourquoi est-ce « un bon signe » ?

### Application 2.7 — Auditer un classeur abîmé (section 2.4)

**Objectif.** Injecter des défauts dans les données et vérifier qu'une feuille de contrôles les détecte.

**Étape 1 — abîmer une copie** (40 doublons, 25 canaux mal écrits, 10 montants vides, 5 montants négatifs).

```python
ab = pd.concat([L, L.sample(40, random_state=1)], ignore_index=True)
ab.loc[ab.sample(25, random_state=2).index, "canal"] = "site "
ab.loc[ab.sample(10, random_state=3).index, "montant"] = np.nan
idx_neg = ab[ab["montant"].notna()].sample(5, random_state=4).index
ab.loc[idx_neg, "montant"] = -ab.loc[idx_neg, "montant"]
na = len(ab) + 1
print(len(ab), "lignes dans la copie abîmée")
```
<!--sortie-->
```text
29867 lignes dans la copie abîmée
```

**Étape 2 — la feuille de contrôles.**

```python
r = lambda c: f"Ab!{c}2:{c}{na}"
F = {"lignes": f"=ROWS({r('A')})", "doublons d'identifiant": f"=ROWS({r('A')})-COUNTA(UNIQUE({r('A')}))",
     "canaux non reconnus": f'=ROWS({r("E")})-COUNTIFS({r("E")},"Site")-COUNTIFS({r("E")},"Boutique")-COUNTIFS({r("E")},"Réseaux")',
     "montants vides": f"=COUNTBLANK({r('M')})", "montants négatifs": f'=COUNTIFS({r("M")},"<0")', "total": f"=SUM({r('M')})"}
res = O.evaluer(F, {"Ab": ab})
for k, v in res.items():
    print(f"{k:24s} {O.fr(v)}")
```
<!--sortie-->
```text
lignes                   29 867
doublons d'identifiant   40
canaux non reconnus      25
montants vides           10
montants négatifs        5
total                    1 326 154,16
```

**Étape 3 — recouper avec pandas.**

```python
print("pandas : doublons", int(ab["id_ligne"].duplicated().sum()), "| canaux non reconnus", int((~ab["canal"].isin(["Site", "Boutique", "Réseaux"])).sum()),
      "| vides", int(ab["montant"].isna().sum()), "| négatifs", int((ab["montant"] < 0).sum()))
```
<!--sortie-->
```text
pandas : doublons 40 | canaux non reconnus 25 | vides 10 | négatifs 5
```

**À vous.** Quels défauts un contrôle de total seul n'aurait-il **pas** détectés ? Ajoutez un contrôle sur les dates hors période.

### Application 2.8 — Trianguler : formules, SQL et pandas (sections 2.5 et 2.6)

**Objectif.** Calculer le chiffre d'affaires du Site **par mois** avec trois outils indépendants, et vérifier qu'ils s'accordent ; écrire l'équivalent d'une mesure DAX et d'une requête `QUERY`.

**Étape 1 — douze formules `SOMME.SI.ENS`.**

```python
F = {}
for m in range(1, 13):
    fin = "DATE(2026,1,1)" if m == 12 else f"DATE(2025,{m + 1},1)"
    F[m] = f'=SUMIFS({R("M")},{R("E")},"Site",{R("C")},">="&DATE(2025,{m},1),{R("C")},"<"&{fin})'
res = O.evaluer(F, {"Lignes": L})
excel = pd.Series({m: res[m] for m in F})
```

**Étape 2 — SQL et pandas.**

```python
con = sqlite3.connect("donnees/boutique.db")
sql = pd.read_sql("""SELECT CAST(strftime('%m', c.date_commande) AS INTEGER) AS mois, SUM(l.montant) AS ca FROM lignes_commande l
                     JOIN commandes c ON c.id_commande = l.id_commande WHERE c.canal = 'Site' AND c.date_commande >= '2025-01-01' GROUP BY mois""", con).set_index("mois")["ca"]
pdp = L[L["canal"] == "Site"].groupby(L["date_commande"].dt.month)["montant"].sum()
print("écart Excel–SQL :", round(float((excel - sql).abs().max()), 6), "| écart Excel–pandas :", round(float((excel - pdp).abs().max()), 6))
print("meilleur mois :", int(excel.idxmax()), "→", O.fr(excel.max()), "€ | total :", O.fr(excel.sum()), "€")
```
<!--sortie-->
```text
écart Excel–SQL : 0.0 | écart Excel–pandas : 0.0
meilleur mois : 12 → 90 048,47 € | total : 617 715,45 €
```

**Étape 3 — une mesure DAX en pandas.** `CA N-1` et `Croissance` pour le Site, 2025 contre 2024 : pandas sur toutes les années.

```python
cmd = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"]); lig = pd.read_csv("donnees/lignes_commande.csv")
tt = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande"); tt = tt[tt["canal"] == "Site"]
ca_an = tt.groupby(tt["date_commande"].dt.year)["montant"].sum()
print({int(k): O.fr(v) for k, v in ca_an.items()}, "| croissance du Site 2025/2024 :", O.fr((ca_an[2025] / ca_an[2024] - 1) * 100), "%")
```
<!--sortie-->
```text
{2023: '422\u202f440,34', 2024: '502\u202f531', 2025: '617\u202f715,45'} | croissance du Site 2025/2024 : 22,92 %
```

**À vous.** Écrivez la formule `QUERY` de Google Sheets qui donnerait le CA du Site par mois, et la requête SQL équivalente.

## Exercices

### Exercice 2.1 ⭐ — Que devient une formule recopiée ? (section 2.1.2)

La cellule `D5` contient `=$B2*C$1`. Écrivez le contenu de la cellule obtenue en recopiant `D5` (a) vers `F8`, (b) vers `H5`, (c) vers `D9`. Vérifiez avec une petite fonction qui applique la règle de décalage.

### Exercice 2.2 ⭐ — SOMME.SI.ENS à la main (section 2.1.4)

Voici huit lignes de ventes :

| Ligne | Catégorie | Canal | Montant |
|---|---|---|---|
| 1 | Cuisine | Boutique | 40 |
| 2 | Cuisine | Site | 25 |
| 3 | Jardin | Boutique | 80 |
| 4 | Jardin | Site | 60 |
| 5 | Cuisine | Boutique | 10 |
| 6 | Jardin | Site | 30 |
| 7 | Cuisine | Site | 15 |
| 8 | Jardin | Boutique | 20 |

Sans ordinateur, calculez : (a) la somme des montants du Jardin en Boutique ; (b) le nombre de lignes du Site avec un montant d'au moins 30 ; (c) le montant moyen de la Cuisine. Écrivez les trois formules, puis vérifiez avec `O.evaluer`.

### Exercice 2.3 ⭐⭐ — Trois tailles de ligne (section 2.1.5)

On range une ligne de vente de 2025 en « petit » (moins de 40 €), « moyen » (de 40 € inclus à 100 € exclus) ou « gros » (100 € et plus). Écrivez les 9 formules `NB.SI.ENS` qui comptent les lignes de chaque taille pour chaque canal, puis recoupez avec `pd.crosstab` et `pd.cut`. Quel canal a la plus grande **part de gros** ?

### Exercice 2.4 ⭐⭐ — Un barème de remise par palier (section 2.1.6)

Une remise de fidélité dépend de la quantité : 0 % pour 1 article, 3 % pour 2, 5 % pour 3 ou 4, 8 % à partir de 5 (barème `1 → 0 ; 2 → 0,03 ; 3 → 0,05 ; 5 → 0,08`). (a) Appliquez-le à chaque ligne de 2025 par `RECHERCHEV` en correspondance approchée et calculez la **remise moyenne** ; recoupez avec pandas. (b) Que se passe-t-il si le barème n'est plus trié (5, 1, 3, 2) ? Testez la quantité 3.

### Exercice 2.5 ⭐ — Dates (section 2.1.8)

Calculez par formules, puis par Python : (a) le jour de la semaine du 25/12/2025 ; (b) le dernier jour de février 2024 ; (c) le nombre de jours ouvrés de décembre 2025 ; (d) l'âge en années entières, au 31/12/2025, d'une personne née le 12/05/1990.

### Exercice 2.6 ⭐⭐ — Un tableau croisé à la main (section 2.2)

Avec les huit lignes de l'exercice 2.2 : construisez à la main le tableau croisé « catégorie en lignes, canal en colonnes, somme du montant », avec les totaux ; puis le même tableau en **% du total de la ligne**. Vérifiez avec `pivot_table`.

### Exercice 2.7 ⭐⭐ — Moyenne des ratios ou ratio des sommes ? (section 2.2.4)

Trois lignes de vente ont pour (montant, marge) : (10 ; 5), (100 ; 30), (200 ; 60). Calculez le taux de marge **moyen des lignes** et le taux de marge **global** (somme des marges sur somme des montants). Lequel donnerait un champ calculé de tableau croisé ? Faites ensuite le même calcul par canal sur les ventes de 2025.

### Exercice 2.8 ⭐⭐ — L'ordre des étapes compte (section 2.3)

Dans la requête de la section 2.3, on change le type de `Qté` en entier **après** avoir retiré les en-têtes répétés et la ligne de total. Montrez ce qui se passe si l'on change le type **avant**. Quelle erreur obtient-on, et pourquoi est-ce « un bon signe » ?

### Exercice 2.9 ⭐⭐⭐ — Dépivoter et repivoter (section 2.3.4)

Construisez le tableau **large** du chiffre d'affaires 2025 par canal (en lignes) et par mois (en colonnes). Dépivotez-le en un tableau **long**, puis repivotez-le. Vérifiez que vous retrouvez le tableau de départ et que le total est conservé.

### Exercice 2.10 ⭐⭐ — Remettre un tableau en forme (section 2.4.2)

Le tableau ci-dessous (construit dans le corrigé) est présenté « pour être lu » : un titre, un blanc, des mois en lignes, des catégories en colonnes, des lignes de sous-total par trimestre. Écrivez le code qui le transforme en tableau ordonné (une ligne par mois et catégorie, sans total), puis vérifiez que le total général est conservé.

### Exercice 2.11 ⭐⭐⭐ — Cinq contrôles (section 2.4.4)

Sur un extrait de 2 000 lignes de la feuille `Lignes`, on a injecté : 7 identifiants clients qui n'existent pas dans la feuille `Clients`, 4 dates de 2024, 3 lignes en double et 5 canaux mal écrits. Écrivez **cinq contrôles** sous forme de formules (clients inconnus, dates hors période, doublons, canaux hors liste, total comparé à une valeur de référence), appliquez-les et construisez le tableau « défaut injecté → contrôle qui le détecte ».

### Exercice 2.12 ⭐⭐⭐ — Le panier moyen par canal, dans cinq outils (sections 2.5 et 2.6)

Le **panier moyen** d'un canal est son chiffre d'affaires divisé par son nombre de commandes **distinctes**. Calculez-le pour chaque canal en 2025 : par formules (`SOMME.SI.ENS` et `NBVAL(UNIQUE(FILTRE(…)))`), en SQL (SQLite), en pandas. Écrivez (sans l'exécuter) la mesure DAX et la formule `QUERY` de Google Sheets équivalentes.

## Corrigés

### Corrigé 2.1

Règle : une référence **relative** se décale du même nombre de lignes et de colonnes que la formule ; la partie précédée de `$` ne bouge pas. (a) `D5 → F8` : deux colonnes et trois lignes plus loin : `$B2` devient `$B5` (colonne figée, ligne relative +3), `C$1` devient `E$1` (colonne relative +2, ligne figée) : **`=$B5*E$1`**. (b) `D5 → H5` : quatre colonnes plus loin, même ligne : **`=$B2*G$1`**. (c) `D5 → D9` : quatre lignes plus bas : **`=$B6*C$1`**.

```python
import re
def decaler(formule, dl, dc):
    num = lambda s: sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(s)))
    nom = lambda k: (nom((k - 1) // 26) if k > 26 else "") + chr(65 + (k - 1) % 26)
    def f(m):
        ca, c, la, l = m.groups()
        return f"{ca}{c if ca else nom(num(c) + dc)}{la}{l if la else int(l) + dl}"
    return re.sub(r"(\$?)([A-Z]+)(\$?)(\d+)", f, formule)
print(decaler("=$B2*C$1", 3, 2), decaler("=$B2*C$1", 0, 4), decaler("=$B2*C$1", 4, 0))
```
<!--sortie-->
```text
=$B5*E$1 =$B2*G$1 =$B6*C$1
```

### Corrigé 2.2

(a) Jardin en Boutique : 80 + 20 = **100**. (b) Lignes du Site avec un montant ≥ 30 : les montants du Site sont 25, 60, 30, 15 ; deux sont ≥ 30 : **2**. (c) Montant moyen de la Cuisine : (40 + 25 + 10 + 15) / 4 = **22,5**. Formules (avec les colonnes A à D et les lignes 2 à 9) : `=SOMME.SI.ENS(D2:D9;B2:B9;"Jardin";C2:C9;"Boutique")`, `=NB.SI.ENS(C2:C9;"Site";D2:D9;">=30")`, `=MOYENNE.SI.ENS(D2:D9;B2:B9;"Cuisine")`.

```python
lg8 = [["ligne", "catégorie", "canal", "montant"], [1, "Cuisine", "Boutique", 40], [2, "Cuisine", "Site", 25], [3, "Jardin", "Boutique", 80], [4, "Jardin", "Site", 60],
       [5, "Cuisine", "Boutique", 10], [6, "Jardin", "Site", 30], [7, "Cuisine", "Site", 15], [8, "Jardin", "Boutique", 20]]
F = {"a": '=SUMIFS(H!D2:D9,H!B2:B9,"Jardin",H!C2:C9,"Boutique")', "b": '=COUNTIFS(H!C2:C9,"Site",H!D2:D9,">=30")', "c": '=AVERAGEIFS(H!D2:D9,H!B2:B9,"Cuisine")'}
print(O.evaluer(F, extra={"H": lg8}))
```
<!--sortie-->
```text
{'a': 100, 'b': 2, 'c': 22.5}
```

### Corrigé 2.3

```python
canaux = ["Boutique", "Site", "Réseaux"]; tailles = ["petit", "moyen", "gros"]
F = {}
for c in canaux:
    F[f"petit|{c}"] = f'=COUNTIFS({R("E")},"{c}",{R("M")},"<40")'
    F[f"moyen|{c}"] = f'=COUNTIFS({R("E")},"{c}",{R("M")},">=40",{R("M")},"<100")'
    F[f"gros|{c}"] = f'=COUNTIFS({R("E")},"{c}",{R("M")},">=100")'
res = O.evaluer(F, {"Lignes": L})
tab = pd.DataFrame({c: [int(res[f"{t}|{c}"]) for t in tailles] for c in canaux}, index=tailles)
att = pd.crosstab(pd.cut(L["montant"], [-np.inf, 40, 100, np.inf], right=False, labels=tailles), L["canal"])[canaux]
print(tab.to_string()); print("identique à pandas :", bool((tab.values == att.values).all()))
print("part de gros (%) :", (tab.loc["gros"] / tab.sum() * 100).round(1).to_dict())
```
<!--sortie-->
```text
       Boutique  Site  Réseaux
petit      7425  8278     1938
moyen      4122  4488     1094
gros       1064  1162      256
identique à pandas : True
part de gros (%) : {'Boutique': 8.4, 'Site': 8.3, 'Réseaux': 7.8}
```

Les neuf formules et `pd.crosstab` donnent le même tableau. La part de lignes « grosses » est de **8,4 %** en Boutique, **8,3 %** sur le Site et **7,8 %** pour les Réseaux : la Boutique est en tête, mais l'écart est minime ; sur ces données simulées, la taille d'une ligne ne dépend guère du canal.

### Corrigé 2.4

(a) Le barème approché lit « la plus grande quantité inférieure ou égale » : 4 articles tombent donc dans la tranche de 3 (5 %). La remise moyenne est de **0,53 %** : la grande majorité des lignes (25 366 sur 29 827) ne comptent qu'un article.

```python
bar = [["q", "r"], [1, 0.0], [2, 0.03], [3, 0.05], [5, 0.08]]
res = O.evaluer({"moyenne": f"=AVERAGE(Lignes!N2:N{n})"}, {"Lignes": L}, extra={"Ba": bar}, colonnes={"Lignes": {"rem": "=VLOOKUP(J{r},Ba!A2:B5,2,TRUE)"}})
att = np.array([0.0, 0.03, 0.05, 0.08])[np.searchsorted([1, 2, 3, 5], L["quantite"], side="right") - 1]
print("remise moyenne : feuille de calcul", round(res["moyenne"], 6), "| pandas", round(float(att.mean()), 6), "| répartition des quantités :", L["quantite"].value_counts().sort_index().to_dict())
```
<!--sortie-->
```text
remise moyenne : feuille de calcul 0.00529 | pandas 0.00529 | répartition des quantités : {1: 25366, 2: 3264, 3: 881, 4: 316}
```

(b) Avec le barème **non trié** (5, 1, 3, 2), la correspondance approchée n'a plus de sens :

```python
ba_n = [["q", "r"], [5, 0.08], [1, 0.0], [3, 0.05], [2, 0.03]]
r = O.evaluer({"q3": "=VLOOKUP(3,Ba!A2:B5,2,TRUE)", "q4": "=VLOOKUP(4,Ba!A2:B5,2,TRUE)"}, extra={"Ba": ba_n})
print(r)
```
<!--sortie-->
```text
{'q3': '#N/A', 'q4': '#N/A'}
```

Ici le tableur renvoie `#N/A` ; dans Excel, le résultat sur une table non triée peut être faux **sans erreur**, ce qui est pire. Règle : la correspondance approchée exige une première colonne **triée par ordre croissant**.

### Corrigé 2.5

(a) Le 25 décembre 2025 est un **jeudi**. (b) Le dernier jour de février 2024 est le **29 février** (année bissextile), numéro de série 45 351. (c) Décembre 2025 compte **23 jours ouvrés** (31 jours moins 8 jours de week-end). (d) **35 ans** (le 12 mai 1990 est antérieur au 31 décembre 2025 de 35 ans, 7 mois et 19 jours).

```python
F = {"jour": '=TEXT(DATE(2025,12,25),"dddd")', "fin_fev": "=EOMONTH(DATE(2024,2,15),0)", "ouvres": "=NETWORKDAYS(DATE(2025,12,1),DATE(2025,12,31))",
     "age": '=DATEDIF(DATE(1990,5,12),DATE(2025,12,31),"Y")'}
r = O.evaluer(F)
print(r["jour"], "|", (pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(r["fin_fev"]))).date(), "|", int(r["ouvres"]), "|", int(r["age"]))
print(pd.Timestamp("2025-12-25").day_name(), "|", np.busday_count("2025-12-01", "2026-01-01"), "|", (pd.Timestamp("2025-12-31") - pd.Timestamp("1990-05-12")).days // 365.25)
```
<!--sortie-->
```text
jeudi | 2024-02-29 | 23 | 35
Thursday | 23 | 35.0
```

### Corrigé 2.6

Sommes : Cuisine × Boutique = 50, Cuisine × Site = 40, Jardin × Boutique = 100, Jardin × Site = 90 ; totaux : Cuisine 90, Jardin 190, Boutique 150, Site 130 ; total général **280**. En % du total de la ligne : Cuisine 55,6 % Boutique / 44,4 % Site ; Jardin 52,6 % / 47,4 % ; ensemble 53,6 % / 46,4 %.

```python
t8 = pd.DataFrame(lg8[1:], columns=lg8[0])
pt8 = t8.pivot_table(index="catégorie", columns="canal", values="montant", aggfunc="sum", margins=True, margins_name="Total")
print(pt8.to_string()); print((pt8.div(pt8["Total"], axis=0) * 100).round(1).to_string())
```
<!--sortie-->
```text
canal      Boutique  Site  Total
catégorie                       
Cuisine          50    40     90
Jardin          100    90    190
Total           150   130    280
canal      Boutique  Site  Total
catégorie                       
Cuisine        55.6  44.4  100.0
Jardin         52.6  47.4  100.0
Total          53.6  46.4  100.0
```

### Corrigé 2.7

Taux par ligne : 50 %, 30 % et 30 % ; **moyenne** des taux = (50 + 30 + 30) / 3 = **36,7 %**. Taux **global** = (5 + 30 + 60) / (10 + 100 + 200) = 95 / 310 = **30,6 %**. Les deux diffèrent parce que la ligne à 10 € (taux élevé) compte autant que les lignes à 100 et 200 € dans la moyenne, et presque rien dans le ratio des sommes. Un champ calculé de tableau croisé donne le **ratio des sommes** (30,6 %). Sur les ventes 2025, les deux mesures sont presque identiques par canal (de 48,1 % à 48,4 %), car les lignes ont des taux de marge voisins : l'écart de l'exemple à la main est pédagogique, il est plus faible sur nos données.

```python
print("moyenne des taux :", round(np.mean([5 / 10, 30 / 100, 60 / 200]) * 100, 1), "% | ratio des sommes :", round(95 / 310 * 100, 1), "%")
M = L.merge(P[["id_produit", "cout_achat"]], on="id_produit"); M["marge"] = M["montant"] - M["quantite"] * M["cout_achat"]
par = M.groupby("canal").apply(lambda g: pd.Series({"moyenne des taux (%)": (g["marge"] / g["montant"]).mean() * 100, "ratio des sommes (%)": g["marge"].sum() / g["montant"].sum() * 100}), include_groups=False)
print(par.round(2).to_string())
```
<!--sortie-->
```text
moyenne des taux : 36.7 % | ratio des sommes : 30.6 %
          moyenne des taux (%)  ratio des sommes (%)
canal                                               
Boutique                 48.26                 48.33
Réseaux                  48.20                 48.43
Site                     48.08                 48.24
```

### Corrigé 2.8

Si l'on convertit `Qté` en entier avant d'avoir retiré les en-têtes répétés et la ligne de total, la colonne contient encore du texte (« Qté ») et du vide :

```python
b = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", header=None, dtype=str, skip_blank_lines=False)
t = b.iloc[3:].reset_index(drop=True); t.columns = t.iloc[0]; t = t.iloc[1:]
try:
    t["Qté"].astype(int)
except Exception as e:
    print("avant le nettoyage :", type(e).__name__, "—", str(e)[:60])
t2 = t[t["N° ticket"] != "N° ticket"]; t2 = t2[t2["Qté"].notna()]
print("après le nettoyage :", int(t2["Qté"].astype(int).sum()), "articles")
```
<!--sortie-->
```text
avant le nettoyage : ValueError — cannot convert float NaN to integer
après le nettoyage : 338 articles
```

L'erreur est **visible** : la requête s'arrête au lieu de produire un résultat faux. C'est un bon signe : une conversion de type qui échoue est le moyen le plus simple de découvrir qu'une ligne parasite traîne dans les données. Dans Power Query, l'étape « Type modifié » afficherait des cellules `Error` ; il ne faut pas les remplacer mécaniquement par des valeurs vides.

### Corrigé 2.9

```python
mois = L["date_commande"].dt.month
large = L.pivot_table(index="canal", columns=mois, values="montant", aggfunc="sum")
long = large.reset_index().melt(id_vars="canal", var_name="mois", value_name="montant")
retour = long.pivot(index="canal", columns="mois", values="montant")
print(large.shape, "→", long.shape, "| identique après repivot :", bool(np.allclose(retour.values, large.values)), "| total :", round(long["montant"].sum(), 2))
```
<!--sortie-->
```text
(3, 12) → (36, 3) | identique après repivot : True | total : 1324763.72
```

Les 3 × 12 cases deviennent 36 lignes ; le repivot redonne le tableau de départ, et le total (1 324 763,72 €) est conservé.

### Corrigé 2.10

```python
mp = L.assign(mois=L["date_commande"].dt.month).pivot_table(index="mois", columns="categorie", values="montant", aggfunc="sum").round(0)
cats = ["Cuisine", "Maison"]; noms = ["Janvier", "Février", "Mars", "Avril"]
lignes = [["Ventes 2025 (en €)", None, None], [None, None, None], ["Mois", *cats]]
for m in (1, 2, 3):
    lignes.append([noms[m - 1], *[float(mp.loc[m, c]) for c in cats]])
lignes.append(["Sous-total T1", *[float(sum(mp.loc[m, c] for m in (1, 2, 3))) for c in cats]])
lignes.append([noms[3], *[float(mp.loc[4, c]) for c in cats]])
sale = pd.DataFrame(lignes)
```

```python
t = sale.iloc[3:].copy(); t.columns = sale.iloc[2]; t = t.rename(columns={"Mois": "mois"})
t = t[~t["mois"].str.startswith("Sous-total")]
propre = t.melt(id_vars="mois", var_name="categorie", value_name="montant")
total_attendu = float(sale.iloc[3:, 1:].astype(float).sum().sum() - sale.iloc[6, 1:].astype(float).sum())
print(propre.shape, "| total conservé :", float(propre["montant"].sum()) == total_attendu)
```
<!--sortie-->
```text
(8, 3) | total conservé : True
```

Les étapes sont celles que fait Power Query : sauter les trois premières lignes, promouvoir l'en-tête, **supprimer les lignes de sous-total** (sinon le total est compté deux fois), dépivoter. Le contrôle compare le total du tableau ordonné au total des lignes de détail.

### Corrigé 2.11

```python
S = L.head(2000).copy()
S.loc[S.index[:7], "id_client"] = 999999                       # clients inconnus
S.loc[S.index[10:14], "date_commande"] = pd.Timestamp("2024-12-30")  # dates hors période
S = pd.concat([S, S.iloc[20:23]], ignore_index=True)           # doublons
S.loc[S.index[40:45], "canal"] = "Boutique "                   # canaux mal écrits
ns = len(S) + 1; ref_total = float(L.head(2000)["montant"].sum())
r = lambda c: f"S!{c}2:{c}{ns}"
F = {"clients inconnus": f"=SUMPRODUCT(--ISNA(MATCH({r('D')},Clients!A2:A6001,0)))",
     "dates hors période": f'=COUNTIFS({r("C")},"<"&DATE(2025,1,1))+COUNTIFS({r("C")},">"&DATE(2025,12,31))',
     "doublons": f"=ROWS({r('A')})-COUNTA(UNIQUE({r('A')}))",
     "canaux hors liste": f'=ROWS({r("E")})-COUNTIFS({r("E")},"Site")-COUNTIFS({r("E")},"Boutique")-COUNTIFS({r("E")},"Réseaux")',
     "total (écart à la référence)": f"=SUM({r('M')})-{ref_total}"}
res = O.evaluer(F, {"S": S, "Clients": C})
for k, v in res.items():
    print(f"{k:30s}{O.fr(v)}")
```
<!--sortie-->
```text
clients inconnus              7
dates hors période            4
doublons                      3
canaux hors liste             5
total (écart à la référence)  84,16
```

Le tableau « défaut → contrôle » : **clients inconnus** → contrôle 1 (7) ; **dates de 2024** → contrôle 2 (4) ; **doublons** → contrôle 3 (3 lignes ; ils font aussi monter le total de 84,16 €, donc le contrôle 5 les voit) ; **canaux mal écrits** → contrôle 4 (5). Le contrôle du **total** ne voit que les défauts qui changent la somme (ici, les doublons) : il est nécessaire, mais **insuffisant** à lui seul.

### Corrigé 2.12

```python
canaux = ["Boutique", "Site", "Réseaux"]
F = {}
for c in canaux:
    F[f"ca|{c}"] = f'=SUMIFS({R("M")},{R("E")},"{c}")'
    F[f"nb|{c}"] = f'=COUNTA(UNIQUE(FILTER({R("B")},{R("E")}="{c}")))'
res = O.evaluer(F, {"Lignes": L})
exc = {c: res[f"ca|{c}"] / res[f"nb|{c}"] for c in canaux}
con = sqlite3.connect("donnees/boutique.db")
sql = pd.read_sql("""SELECT c.canal, ROUND(SUM(l.montant) / COUNT(DISTINCT c.id_commande), 4) AS panier FROM lignes_commande l JOIN commandes c ON c.id_commande = l.id_commande
                     WHERE c.date_commande >= '2025-01-01' GROUP BY c.canal""", con).set_index("canal")["panier"]
pdp = L.groupby("canal").apply(lambda g: g["montant"].sum() / g["id_commande"].nunique(), include_groups=False)
print({c: round(exc[c], 2) for c in canaux}); print("écarts maximaux : SQL", round(max(abs(exc[c] - sql[c]) for c in canaux), 4), "| pandas", round(max(abs(exc[c] - pdp[c]) for c in canaux), 4))
```
<!--sortie-->
```text
{'Boutique': 103.08, 'Site': 101.63, 'Réseaux': 102.44}
écarts maximaux : SQL 0.0 | pandas 0.0
```

Les trois outils donnent les mêmes paniers moyens : **103,08 €** en Boutique, **101,63 €** sur le Site, **102,44 €** pour les Réseaux. La mesure DAX équivalente est `Panier moyen := DIVIDE ( SUM ( Lignes[montant] ), DISTINCTCOUNT ( Lignes[id_commande] ) )` : placée dans un tableau croisé par canal, elle s'évalue canal par canal (non exécuté). La formule `QUERY` de Google Sheets est `=QUERY(Lignes!A1:M ; "select E, sum(M) group by E" ; 1)` pour le chiffre d'affaires, à diviser par le nombre de commandes distinctes (par exemple `=COUNTUNIQUE(FILTER(Lignes!B:B ; Lignes!E:E = "Site"))`) : non exécuté, syntaxe à vérifier.
