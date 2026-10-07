## 2.4 ➕ Pour aller plus loin : restructuration, pivot et dépivot

> 🧭 **Section complémentaire.** Elle traite d'un geste que l'on rencontre dès qu'un tableur « fait main » entre dans l'analyse : passer d'une table **large** (un mois par colonne) à une table **longue** (un mois par ligne) et inversement. La gérante tient le stock de la boutique dans un tableur de ce genre ; c'est notre terrain d'essai. Rien de ce qui suit n'est nécessaire à la suite du volume.

Une même information peut s'écrire de deux façons. Le **format large** place chaque valeur d'une variable dans une colonne différente (une colonne par mois) : c'est celui que l'on aime lire, parce que l'œil compare les colonnes, et celui que produisent les tableurs. Le **format long** a **une ligne par observation** et une colonne par variable (une colonne `mois`, une colonne `stock`) : c'est celui que veulent les outils d'analyse, de tracé et de jointure (volume I, section 5.1.4 sur le « tableau propre »). Passer de l'un à l'autre est un **changement de grain**, avec le même contenu.

```python hide
fig, ax = plt.subplots(figsize=(7.6, 2.8)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 40)
def tab(x, y, entetes, lignes, couleurs, w=9, h=4.2):
    for j, e in enumerate(entetes):
        ax.add_patch(plt.Rectangle((x + j * w, y), w, h, fc=couleurs, ec="white")); ax.text(x + j * w + w / 2, y + h / 2, e, ha="center", va="center", fontsize=7.5, weight="bold")
    for i, l in enumerate(lignes):
        for j, v in enumerate(l):
            ax.add_patch(plt.Rectangle((x + j * w, y - (i + 1) * h), w, h, fc="white", ec=GRILLE if False else "#cccccc")); ax.text(x + j * w + w / 2, y - (i + 1) * h + h / 2, str(v), ha="center", va="center", fontsize=7.5)
ax.text(1, 38, "Format large : une colonne par mois", fontsize=8.5, weight="bold", color=BLEU)
tab(1, 30, ["produit", "janv.", "févr.", "mars"], [["P001", 49, 41, 28], ["P002", 11, 0, 10]], "#cde2fb")
ax.text(52, 38, "Format long : une ligne par produit et par mois", fontsize=8.5, weight="bold", color=ORANGE)
tab(52, 30, ["produit", "mois", "stock"], [["P001", 1, 49], ["P001", 2, 41], ["P001", 3, 28], ["P002", 1, 11], ["P002", 2, 0], ["P002", 3, 10]], "#fbd9cc", w=11)
ax.annotate("", xy=(51, 22), xytext=(39, 22), arrowprops=dict(arrowstyle="->", color=MUET, lw=1.5)); ax.text(45, 24, "melt", ha="center", fontsize=8, color=MUET)
ax.annotate("", xy=(39, 18), xytext=(51, 18), arrowprops=dict(arrowstyle="->", color=MUET, lw=1.5)); ax.text(45, 14.5, "pivot", ha="center", fontsize=8, color=MUET)
save(fig, "ch02-large-long.png")
```

![Le même contenu en format large (une colonne par mois) et en format long (une ligne par produit et par mois) ; `melt` passe du premier au second, `pivot` fait l'inverse.](figures/ch02-large-long.png)

### 2.4.1 Trois fonctions à connaître

- **`melt`** (en R : `pivot_longer`) **dépivote** : il garde quelques colonnes d'identifiant et transforme **toutes les autres colonnes** en deux colonnes, `variable` et `valeur`. Il ne **calcule** rien.
- **`pivot`** (en R : `pivot_wider`) fait l'inverse, mais **ne sait pas agréger** : si deux lignes ont la même combinaison d'identifiants, il s'arrête.
- **`pivot_table`** pivote **et** agrège (`aggfunc`) : c'est l'équivalent d'un tableau croisé dynamique de tableur, avec des totaux optionnels (`margins=True`).

Reprenons la table des ventes. Un `pivot_table` donne le chiffre d'affaires par canal (en lignes) et par mois (en colonnes), avec les totaux.

```python
large = ventes.pivot_table(index="canal", columns="mois", values="montant", aggfunc="sum", margins=True, margins_name="Total").round(0)
print(large.iloc[:, [0, 1, -2, -1]].to_string())
```
<!--sortie-->

On le **redresse** en format long avec `melt` (après avoir retiré la ligne et la colonne de totaux, qui sont des **résumés**, pas des observations), puis on retourne au format large avec `pivot` : si tout va bien, on retombe sur le tableau de départ.

```python
corps = large.drop(columns="Total").drop(index="Total")
long = corps.reset_index().melt(id_vars="canal", var_name="mois", value_name="ca")
retour = long.pivot(index="canal", columns="mois", values="ca")
print(len(long), "lignes en format long | aller-retour identique :", bool(retour.equals(corps)))
print(long.head(3).to_string(index=False))
```
<!--sortie-->

```python hide
NUM("n_long", len(long)); NUM("ca_bout_janv", corps.loc["Boutique", "2025-01"]); NUM("ca_total_large", large.loc["Total", "Total"])
```

Deux canaux et douze mois donnent {{n_long:.0f}} lignes en format long : le **nombre de cellules** est conservé, c'est le contrôle de base. Le total du tableau large ({{ca_total_large:,.0f}} €) est celui de la table des ventes, et le passage au format long n'a rien changé. Voyons maintenant ce qui se passe quand `pivot` rencontre deux lignes pour la même case.

```python
try:
    ventes.pivot(index="canal", columns="mois", values="montant")
except ValueError as e:
    print(e)
```
<!--sortie-->

Le message est clair : la table des ventes compte des milliers de lignes par couple (canal, mois) ; `pivot` ne sait pas **choisir** laquelle garder, donc il refuse. C'est une **protection** : `pivot_table` accepte, mais **à condition de dire comment agréger** (`aggfunc="sum"`), et l'on est obligé d'y penser. Dans un tableur, un tableau croisé dynamique fait la même chose sans prévenir : il somme par défaut, ce qui est faux si la colonne contient des prix unitaires ou des moyennes.

> 💡 **Intuition.** `melt` et `pivot` **déplacent** de l'information sans la changer (comme tourner un tableau d'un quart de tour) ; `pivot_table` **résume**. Un aller-retour qui ne retombe pas sur ses pieds trahit une clé en double ou une perte de lignes.

### 2.4.2 Le tableur de stocks : lire, nettoyer, dépivoter

Le fichier `stocks_tableur.xlsx` ressemble à ce que l'on trouve dans toutes les entreprises : saisi à la main, lisible pour un humain, **hostile à une machine**. Ouvrons-le sans rien présumer, en lisant les cellules telles quelles avec `openpyxl` (la lecture d'un tableur avec pandas est vue au volume I, chapitre 4).

```python
import openpyxl
ws = openpyxl.load_workbook("donnees/stocks_tableur.xlsx")["Stock 2025"]
brut = pd.DataFrame(list(ws.iter_rows(min_row=5, values_only=True))).iloc[:, :14]
brut.columns = ["ref", "designation"] + list(range(1, 13))
print(brut.iloc[[0, 1, 2, 21, 22]].iloc[:, :6].to_string(index=False))
```
<!--sortie-->

On y voit, en quelques lignes, les obstacles : une ligne **de catégorie** (`CUISINE`, cellule fusionnée, seule la première cellule porte la valeur), des lignes **de produits**, une ligne de **sous-total** (dont les cellules contiennent des **formules** ; le fichier n'ayant jamais été recalculé, `openpyxl` donne le texte de la formule et non son résultat), des lignes **vides**, et des **valeurs en texte**. Les lignes de produits se repèrent par un critère **sûr** : la référence suit le motif `P` suivi de trois chiffres. Les autres lignes (catégories, sous-totaux, vides) ne sont pas des observations et sont **écartées** (un sous-total lu comme une donnée ferait compter deux fois le stock). Regardons maintenant ce que contiennent les cellules textuelles.

```python
est_produit = brut["ref"].astype(str).str.fullmatch(r"P\d{3}")
cellules = brut.loc[est_produit].iloc[:, 2:].stack()
textes = cellules[cellules.map(lambda v: isinstance(v, str))].str.strip().str.replace(r"^\d+$", "<nombre>", regex=True)
print(textes.value_counts().to_string())
```
<!--sortie-->

```python hide
vc_t = textes.value_counts()
NUM("n_rupture", vc_t["rupture"]); NUM("n_nd", vc_t["ND"]); NUM("n_tiret", vc_t["—"]); NUM("n_nombre_texte", vc_t["<nombre>"]); NUM("n_cellules", cellules.size)
NUM("n_produits_stock", est_produit.sum())
```

Sur {{n_cellules:,.0f}} cellules de stock, quatre catégories de **texte** : **{{n_nombre_texte:.0f}}** nombres écrits comme du texte avec un espace en fin (`"28 "`) ; **{{n_rupture:.0f}}** mentions « rupture » ; **{{n_nd:.0f}}** « ND » (non disponible) ; **{{n_tiret:.0f}}** tirets « — ». Il faut une **décision par catégorie**, et elle est de métier :

- un nombre écrit en texte **est** un nombre : on retire l'espace et l'on convertit ;
- « rupture » signifie **zéro** en stock : c'est une information (on peut compter les ruptures), pas un manquant ;
- « ND » et « — » signifient **inconnu** : on met un **vide** (`NaN`), jamais zéro. Le zéro dirait « en rupture », ce qui est faux et ferait croire à des ruptures qui n'existent pas.

```python
def vers_nombre(v):
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    if s == "rupture":
        return 0
    return int(s) if s.isdigit() else np.nan
produits_stock = brut[est_produit].copy()
mois_cols = list(range(1, 13))
produits_stock[mois_cols] = produits_stock[mois_cols].apply(lambda col: col.map(vers_nombre))
stock = produits_stock.melt(id_vars=["ref", "designation"], var_name="mois", value_name="stock")
stock["id_produit"] = stock["ref"].str[1:].astype(int)
print(len(stock), "lignes | vides :", int(stock["stock"].isna().sum()), "| ruptures :", int((stock["stock"] == 0).sum()))
```
<!--sortie-->

Cent vingt produits et douze mois font **1 440 lignes** en format long, ce que l'on attendait : le nombre de cellules est conservé, aucune n'a été perdue. Comme pour la caisse, on peut maintenant **juger le travail** avec le fichier de vérité, ce qui n'est possible qu'ici.

```python
verite_stock = pd.read_csv("donnees/verite_stocks.csv")
m = stock.merge(verite_stock, on=["id_produit", "mois"], suffixes=("", "_vrai"), validate="1:1")
egal = (m["stock"] == m["stock_vrai"]) | (m["stock"].isna() & m["stock_vrai"].isna())
print("cellules identiques à la vérité :", int(egal.sum()), "sur", len(m))
```
<!--sortie-->

```python hide
NUM("n_egal_stock", egal.sum()); NUM("n_m_stock", len(m)); NUM("n_stock_vides", stock["stock"].isna().sum()); NUM("n_stock_ruptures", (stock["stock"] == 0).sum())
```

Toutes les {{n_egal_stock:,.0f}} cellules coïncident avec la vérité, valeurs manquantes comprises. Ce n'est pas un exploit : les règles de lecture étaient simples et **chaque catégorie de cellule avait été examinée avant de convertir**. Le contrôle de fond reste le même que pour la caisse : **compter** (1 440 cellules avant et après), **classer** ce qui est inhabituel, **décider** par catégorie et **documenter**.

> ⚠️ **Piège : `read_excel` qui « devine ».** Avec `pandas.read_excel`, la colonne qui contient des nombres **et** des mentions comme « rupture » serait lue en texte, ou convertie avec des surprises. Lire les cellules **brutes**, puis décider, est plus long mais ne laisse rien au hasard.

### 2.4.3 Joindre deux tables du même grain

Les stocks sont mensuels, par produit. Pour savoir **combien de mois de ventes** couvre un stock, il faut les rapprocher des ventes, qui sont au grain de la ligne de vente. Si l'on joignait telles quelles, chaque ligne de stock serait associée à **toutes** les lignes de vente du produit et du mois : une jointure 1–n qui multiplierait le stock. La bonne méthode est de **ramener d'abord les ventes au grain du stock** (produit × mois), puis de joindre deux tables dont la clé est unique des deux côtés.

```python
q = ventes.dropna(subset=["id_produit"]).assign(mois=lambda d: d["date"].dt.month, id_produit=lambda d: d["id_produit"].astype(int))
unites = q.groupby(["id_produit", "mois"], as_index=False)["quantite"].sum().rename(columns={"quantite": "vendu"})
couv = stock.dropna(subset=["stock"]).merge(unites, on=["id_produit", "mois"], how="left", validate="1:1")
couv["vendu"] = couv["vendu"].fillna(0)
couv["stock_inferieur_aux_ventes"] = couv["stock"] < couv["vendu"]
print(len(couv), "lignes produit-mois | stock < ventes du mois :", int(couv["stock_inferieur_aux_ventes"].sum()))
```
<!--sortie-->

```python hide
NUM("n_couv", len(couv)); NUM("n_stock_lt", couv["stock_inferieur_aux_ventes"].sum()); NUM("part_stock_lt", couv["stock_inferieur_aux_ventes"].mean() * 100)
rup = couv[couv["stock"] == 0]; NUM("n_rupt_couv", len(rup)); NUM("part_rupt_vendu", (rup["vendu"] > 0).mean() * 100)
```

Sur {{n_couv:,.0f}} couples (produit, mois) dont le stock est connu, **{{part_stock_lt:.0f}} %** ({{n_stock_lt:,.0f}}) ont un stock de fin de mois **inférieur** aux ventes du mois : c'est la couverture inférieure à un mois, un signal de réassort à surveiller. Remarquez aussi que, parmi les {{n_rupt_couv:.0f}} couples en rupture, {{part_rupt_vendu:.0f}} % ont **des ventes dans le mois** : une rupture de **fin** de mois n'interdit pas d'avoir vendu avant, et il ne faut pas confondre les deux.

> ⚠️ **Ce que ce calcul ne prouve pas.** Dans nos données, les stocks et les ventes ont été **simulés indépendamment l'un de l'autre** : la couverture calculée ici montre la **mécanique** de la jointure (même grain, clé unique, vides conservés), pas une réalité de la boutique. Dans de vraies données, on s'attendrait à ce qu'un produit en rupture vende moins le mois suivant : on le **vérifierait**, on ne le supposerait pas.

Deux précautions de méthode s'imposent : les ventes de la caisse dont le produit est ambigu (la paire de produits indiscernables de 2.2.5) ont été **écartées** de ce calcul, donc les ventes de ces deux produits sont **sous-estimées** ; et les stocks « inconnus » sont **exclus** plutôt que traités comme zéro.

### 2.4.4 Le même geste dans les autres outils

Dans **DuckDB**, `UNPIVOT` fait ce que fait `melt` ; on vérifie qu'il donne le même nombre de lignes.

```python
con2 = duckdb.connect(); con2.register("stock_large", produits_stock.rename(columns=str))
n_sql = con2.sql("select count(*) from (unpivot stock_large on columns(* exclude (ref, designation)) into name mois value stock)").fetchone()[0]
print("lignes après UNPIVOT en SQL :", n_sql)
```
<!--sortie-->

Dans **Power Query** (Excel), la même opération s'appelle « dépivoter les autres colonnes » ; on la lit dans le langage M de l'éditeur avancé. Ce qui suit n'est **pas exécuté** ici (Power Query n'est pas disponible sur la machine qui a produit ce livre) ; le résultat attendu est celui que pandas vient de donner : 1 440 lignes. Les noms des étapes et des fonctions sont à vérifier dans la documentation de votre version.

```python noexec
// Power Query (langage M), non exécuté
let
    Source   = Excel.Workbook(File.Contents("stocks_tableur.xlsx"), null, true),
    Feuille  = Source{[Item = "Stock 2025", Kind = "Sheet"]}[Data],
    Entetes  = Table.PromoteHeaders(Table.Skip(Feuille, 3)),
    Produits = Table.SelectRows(Entetes, each Text.StartsWith([#"Réf."], "P")),
    Long     = Table.UnpivotOtherColumns(Produits, {"Réf.", "Désignation"}, "Mois", "Stock")
in
    Long
```

En R, ce serait `pivot_longer(cols = -c(ref, designation), names_to = "mois", values_to = "stock")`, après `filter(grepl("^P[0-9]{3}$", ref))`.

> ✅ **À retenir.**
> - **Large** pour lire, **long** pour calculer, tracer et joindre ; `melt` et `pivot` déplacent sans modifier, `pivot_table` **résume**.
> - Un **aller-retour** large → long → large qui ne retombe pas sur ses pieds trahit un doublon ou une perte ; le **nombre de cellules** est conservé.
> - Un tableur « fait main » se lit en **cellules brutes** : repérer les lignes utiles par un motif sûr, écarter titres et sous-totaux, **classer** les valeurs textuelles et décider **par catégorie** (nombre, zéro, inconnu).
> - **« Inconnu » n'est pas zéro** : un `NaN` dit « on ne sait pas », un zéro dit « rupture ».
> - Avant de joindre, on ramène les deux tables au **même grain** (produit × mois), clé unique des deux côtés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.11 à 2.12.
