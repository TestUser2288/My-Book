## 2.2 Fusion et jointure de jeux de données

La demande de la gérante tient en une table, et les données arrivent en pièces détachées : douze fichiers de caisse, un export du site, une table de produits. Cette section apprend à **recoller** ces pièces sans en perdre ni en inventer : comprendre les types de jointure et la **cardinalité**, **contrôler** les effectifs avant et après chaque opération, **empiler** les fichiers de la caisse malgré leurs formats changeants, **lire** l'export du site et **harmoniser** les deux sources en une table de ventes unique, puis **chercher ce qui manque**. À la fin, on retrouve le même résultat avec trois outils (pandas, SQL, R), et l'on ouvre enfin le fichier de vérité pour juger le travail.

### 2.2.1 Quatre manières de recoller

Il existe deux familles d'opérations, qui ne répondent pas à la même question :

- **Joindre** (*merge*, *join*) relie deux tables **côte à côte** : chaque ligne de la première reçoit, de la seconde, les colonnes qui lui correspondent, selon une **clé**. On ajoute des **colonnes**.
- **Empiler** (*concat*, *union*) met deux tables **l'une sous l'autre** : elles doivent avoir la même structure. On ajoute des **lignes**.

Pour une jointure, la question qui change tout est : **que faire des lignes sans correspondance ?** Quatre réponses, que l'on retrouve sous le même nom en SQL, en R et dans Power Query.

| Type (`how=`) | Garde… | Lignes sans correspondance |
|---|---|---|
| `inner` | seulement les lignes présentes **des deux côtés** | perdues |
| `left` | **toutes** les lignes de la table de gauche | à droite : colonnes vides (`NaN`) |
| `right` | toutes celles de la table de droite | à gauche : colonnes vides |
| `outer` | **toutes** les lignes des deux tables | colonnes vides de l'un ou l'autre côté |

Sur trois lignes de produits et trois lignes de stocks, l'option `indicator=True` ajoute une colonne qui dit **d'où vient chaque ligne** : c'est le meilleur outil de diagnostic d'une jointure.

```python
a = pd.DataFrame({"id_produit": [1, 2, 3], "nom": ["Bol", "Vase", "Plaid"]})
b = pd.DataFrame({"id_produit": [2, 3, 4], "stock": [10, 0, 7]})
print(a.merge(b, on="id_produit", how="outer", indicator=True).to_string(index=False))
```
<!--sortie-->
```text
 id_produit   nom  stock     _merge
          1   Bol    NaN  left_only
          2  Vase   10.0       both
          3 Plaid    0.0       both
          4   NaN    7.0 right_only
```
<!--sortie-->

Le produit 1 n'a pas de stock (`left_only`), le produit 4 n'a pas de nom (`right_only`), les produits 2 et 3 sont présents des deux côtés (`both`). Une jointure `inner` n'aurait gardé que ces deux derniers ; une jointure `left`, les produits 1, 2 et 3. **Le choix du type de jointure est un choix d'analyse** : si l'on veut le chiffre d'affaires de **tous** les produits du catalogue, y compris ceux qui n'ont rien vendu, il faut un `left` depuis le catalogue ; un `inner` ferait **disparaître** ces produits sans le moindre message.

> ⚠️ **Piège : la jointure `inner` qui fait disparaître des lignes.** Par défaut, `merge` fait une jointure `inner`. Si la clé est mal écrite d'un côté (une majuscule, un espace), les lignes concernées **disparaissent** sans erreur. On vérifie donc toujours le nombre de lignes avant et après.

### 2.2.2 La cardinalité et le contrôle des effectifs

La **cardinalité** d'une jointure dit combien de lignes de droite correspondent à une ligne de gauche.

- **1–1** : chaque clé apparaît au plus une fois des deux côtés (un client, sa fiche d'identité).
- **1–n** (ou **n–1** vu de l'autre côté) : une clé de la table « un » correspond à plusieurs lignes de l'autre (un produit, ses lignes de vente). C'est le cas le plus courant, et le plus sain : on **ajoute des colonnes** sans changer le nombre de lignes de la table « n ».
- **n–n** : la clé est répétée **des deux côtés**. Chaque ligne de gauche est associée à **toutes** les lignes de droite de même clé : le nombre de lignes **se multiplie**. C'est presque toujours un accident.

On teste la cardinalité avec le paramètre `validate` (`"1:1"`, `"1:m"`, `"m:1"`, `"m:m"`) : pandas lève une erreur si la réalité ne correspond pas à ce que l'on a **déclaré**. C'est la façon la plus simple de transformer une hypothèse tacite en vérification. Et quatre contrôles, à faire après **chaque** jointure, résument la méthode du chapitre :

1. le **nombre de lignes** avant et après (un 1–n ne doit rien changer) ;
2. la **somme** d'une colonne de la table « n » avant et après ;
3. le **nombre de lignes sans correspondance** (`indicator`) ;
4. l'**unicité** de la clé du côté « un ».

```python
def controler(gauche, droite, cle, how="left"):
    r = gauche.merge(droite, on=cle, how=how, indicator=True)
    return {"lignes avant": len(gauche), "lignes après": len(r),
            "clé dupliquée à droite": int(droite.duplicated(cle).sum()),
            "sans correspondance": int((r["_merge"] == "left_only").sum())}
print(controler(lig, prod[["id_produit", "cout_achat"]], "id_produit"))
```
<!--sortie-->
```text
{'lignes avant': 83905, 'lignes après': 83905, 'clé dupliquée à droite': 0, 'sans correspondance': 0}
```
<!--sortie-->

```python hide
c0 = controler(lig, prod[["id_produit", "cout_achat"]], "id_produit")
NUM("ctrl_avant", c0["lignes avant"]); NUM("ctrl_apres", c0["lignes après"]); NUM("ctrl_dup", c0["clé dupliquée à droite"]); NUM("ctrl_sans", c0["sans correspondance"])
```
<!--sortie-->
```text
NUM ctrl_avant 83905
NUM ctrl_apres 83905
NUM ctrl_dup 0
NUM ctrl_sans 0
```

Pour la jointure des lignes de vente avec les produits, les quatre contrôles passent : 83 905 lignes avant et 83 905 après, aucune clé dupliquée du côté des produits (0), aucune ligne sans correspondance (0). **On peut avancer.** Gardez cette petite fonction : vous allez voir, dans la suite, des jointures qui ne passent pas.

### 2.2.3 Empiler les douze fichiers de la caisse

La caisse de la boutique envoie **un fichier par mois**. Pour répondre à la gérante, il faut les mettre bout à bout, et c'est là que les ennuis commencent : **le format a changé en cours d'année**. Ce phénomène porte un nom, la **dérive de schéma** : la source a évolué (mise à jour du logiciel, changement de paramètres régionaux) et n'a prévenu personne.

| Mois | Codage du fichier | Séparateur | Décimale | Nom de la colonne des quantités | Date | Autres différences |
|---|---|---|---|---|---|---|
| janvier à juin | `cp1252` (ancien Windows) | `;` | `,` | « Qté » | `jj/mm/aaaa` | |
| juillet à septembre | UTF-8 avec « BOM » | `;` | `,` | « Quantité » | `jj/mm/aa` (année sur 2 chiffres) | |
| octobre à décembre | UTF-8 avec « BOM » | `,` | `.` | « Qté » | `jj/mm/aaaa` | colonne « Remise (%) » en plus, champs entre guillemets |

Chaque fichier commence par **trois lignes de titre** (dont une vide), répète son **en-tête** toutes les soixante lignes environ (comme à chaque « page » imprimée), et se termine par une **ligne de total**. Aucune de ces particularités n'est une erreur ; ce sont des **conventions d'édition** qu'un programme doit connaître. L'approche la plus robuste est de ne **rien deviner à la main** : on **détecte** le format de chaque fichier, puis on applique les mêmes étapes. D'abord, ouvrir le fichier en octets et choisir le codage : on essaie UTF-8, et l'on retombe sur `cp1252` si le décodage échoue.

```python
import io, glob, os
def lire_brut(chemin):
    brut = open(chemin, "rb").read()
    try:
        texte = brut.decode("utf-8-sig")        # « sig » : retire le BOM, marque d'ordre des octets
    except UnicodeDecodeError:
        texte = brut.decode("cp1252")
    lignes = texte.splitlines()
    sep = ";" if lignes[3].count(";") > lignes[3].count(",") else ","
    return lignes, sep
```

Le séparateur se devine sur la ligne d'en-tête (la quatrième) : il y en a plus de points-virgules que de virgules dans un fichier à points-virgules, et réciproquement (les décimales à virgule n'apparaissent pas dans l'en-tête). Ensuite, lire le corps en **texte** (jamais de conversion automatique : on convertit explicitement), retirer le total et les en-têtes répétés, et harmoniser le nom des colonnes.

```python
RENOM = {"N° ticket": "ticket", "Ticket": "ticket", "Qté": "quantite", "Quantité": "quantite", "Date": "date", "Heure": "heure",
         "Article": "article", "Catégorie": "categorie", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}
def ouvrir_caisse(chemin):
    lignes, sep = lire_brut(chemin)
    dec = "," if sep == ";" else "."
    total = float(lignes[-1].split(sep)[-1].replace(dec, "."))
    df = pd.read_csv(io.StringIO("\n".join(lignes[3:-1])), sep=sep, dtype=str, keep_default_na=False).rename(columns=RENOM)
    return df[~df["ticket"].isin(["N° ticket", "Ticket"])].copy(), total, dec
```

Reste à **typer** : nombres (en remplaçant la décimale locale par le point), quantité entière, date (le format dépend de la longueur du texte : dix caractères pour l'année sur quatre chiffres, huit pour l'année sur deux).

```python
def typer_caisse(df, dec, nom):
    for c in ["prix_unitaire", "montant", "remise_pct"]:
        df[c] = pd.to_numeric(df[c].str.replace(dec, "."), errors="coerce") if c in df else np.nan
    df["quantite"] = df["quantite"].astype(int)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y" if len(df["date"].iloc[0]) == 10 else "%d/%m/%y")
    df["fichier"] = nom
    df["id_commande"] = df["ticket"].str.lstrip("T").astype(int)
    return df
```

On applique alors la même fonction aux douze fichiers, on empile avec `pd.concat`, et l'on construit **en même temps** un tableau de contrôle : pour chaque fichier, le **total affiché en pied** et la **somme des montants lus**. C'est la ligne de total du fichier qui sert de **somme de contrôle**.

```python
morceaux, ctrl = [], []
for f in sorted(glob.glob("donnees/caisse/caisse_2025-*.csv")):
    df, total, dec = ouvrir_caisse(f)
    df = typer_caisse(df, dec, os.path.basename(f))
    morceaux.append(df)
    ctrl.append((os.path.basename(f), len(df), total, round(df["montant"].sum(), 2), int(df["montant"].isna().sum())))
caisse = pd.concat(morceaux, ignore_index=True)
ctrl = pd.DataFrame(ctrl, columns=["fichier", "lignes", "total_affiche", "somme_lue", "montants_vides"])
ctrl["ecart"] = (ctrl["total_affiche"] - ctrl["somme_lue"]).round(2)
print(len(caisse), "lignes |", caisse["fichier"].nunique(), "fichiers")
print(ctrl.iloc[[0, 3, 6, 9, 11]].to_string(index=False))
```
<!--sortie-->
```text
12678 lignes | 12 fichiers
           fichier  lignes  total_affiche  somme_lue  montants_vides   ecart
caisse_2025-01.csv     955       38882.41   37826.31              36 1056.10
caisse_2025-04.csv    1013       45832.57   45426.14              31  406.43
caisse_2025-07.csv     877       41595.82   41035.68              21  560.14
caisse_2025-10.csv    1138       51321.48   49839.95              38 1481.53
caisse_2025-12.csv    1694       73384.87   70924.34              63 2460.53
```
<!--sortie-->

```python hide
# le format décrit dans le tableau est bien celui des fichiers (la prose affirme, le code vérifie)
fmts = {os.path.basename(f): lire_brut(f)[1] for f in sorted(glob.glob("donnees/caisse/caisse_2025-*.csv"))}
assert all(fmts[f"caisse_2025-{m:02d}.csv"] == (";" if m <= 9 else ",") for m in range(1, 13))
enc = {}
for f in sorted(glob.glob("donnees/caisse/caisse_2025-*.csv")):
    try:
        open(f, "rb").read().decode("utf-8-sig"); enc[os.path.basename(f)] = "utf-8"
    except UnicodeDecodeError:
        enc[os.path.basename(f)] = "cp1252"
assert [enc[f"caisse_2025-{m:02d}.csv"] for m in range(1, 13)] == ["cp1252"] * 6 + ["utf-8"] * 6
for m in range(1, 13):
    entete = lire_brut(f"donnees/caisse/caisse_2025-{m:02d}.csv")[0][3]
    assert ("Quantité" in entete) == (7 <= m <= 9) and ("Qté" in entete) == (m <= 6 or m >= 10) and ("Remise (%)" in entete) == (m >= 10)
cai_ref, ctrl_ref = O.charger_caisse()
assert (caisse.loc[caisse["fichier"].str[11:13].astype(int).between(7, 9), "date"].dt.year == 2025).all()
assert len(cai_ref) == len(caisse) and abs(cai_ref["montant"].sum() - caisse["montant"].sum()) < 0.01
NUM("n_caisse", len(caisse)); NUM("vides_total", ctrl["montants_vides"].sum()); NUM("part_vides", ctrl["montants_vides"].sum() / len(caisse) * 100)
NUM("ecart_total", ctrl["ecart"].sum()); NUM("total_affiche_an", ctrl["total_affiche"].sum()); NUM("somme_lue_an", ctrl["somme_lue"].sum())
NUM("ecart_min", ctrl["ecart"].min()); NUM("ecart_max", ctrl["ecart"].max())
```
<!--sortie-->
```text
NUM n_caisse 12678
NUM vides_total 399
NUM part_vides 3.1471840984382395
NUM ecart_total 13077.49
NUM total_affiche_an 560973.91
NUM somme_lue_an 547896.4199999999
NUM ecart_min 406.43
NUM ecart_max 2460.53
```

Les douze fichiers, empilés, donnent 12 678 lignes de vente. Mais le tableau de contrôle est **net** : pour chaque fichier, la somme des montants lus est **inférieure** au total affiché par la caisse, d'un écart qui va de 406 € à 2 461 € selon les mois. Sur l'année, la caisse annonce 560 973,91 €, et notre table n'en contient que 547 896,42 €, soit **13 077,49 € de moins**. Une jointure ou une lecture qui « marche » sans erreur peut ainsi perdre de l'argent, et c'est la **ligne de total du fichier**, que l'on aurait pu jeter avec les titres, qui l'a révélé.

D'où vient l'écart ? La colonne `montants_vides` donne la piste : **399 lignes (3,1 %) n'ont pas de montant** (cellule vide dans l'export). Une ligne de caisse contient pourtant de quoi **reconstituer** son montant : quantité × prix unitaire, moins la remise. La remise n'est écrite que dans les fichiers d'octobre à décembre ; avant, on ne la connaît pas, et l'on suppose zéro (c'est une **hypothèse** à documenter, que nous testerons plus loin). Les montants reconstitués sont **marqués**, jamais mélangés en silence avec les montants lus.

```python
caisse["montant_vide"] = caisse["montant"].isna()
remise = caisse["remise_pct"].fillna(0)
caisse["montant_corrige"] = caisse["montant"].fillna((caisse["quantite"] * caisse["prix_unitaire"] * (1 - remise / 100)).round(2))
caisse["identique_precedente"] = caisse.duplicated(["ticket", "date", "heure", "article", "categorie", "quantite", "prix_unitaire", "montant"])
par_fichier = caisse.groupby("fichier")["montant_corrige"].sum().round(2).values
print("écart restant sur l'année :", round(par_fichier.sum() - ctrl["total_affiche"].sum(), 2), "€")
print("lignes strictement identiques à une ligne précédente :", int(caisse["identique_precedente"].sum()))
```
<!--sortie-->
```text
écart restant sur l'année : 3498.68 €
lignes strictement identiques à une ligne précédente : 154
```
<!--sortie-->

```python hide
ecart_restant = par_fichier.sum() - ctrl["total_affiche"].sum()
NUM("ecart_restant", ecart_restant); NUM("ecart_restant_pct", ecart_restant / ctrl["total_affiche"].sum() * 100)
NUM("n_identiques", caisse["identique_precedente"].sum()); NUM("montant_identiques", caisse.loc[caisse["identique_precedente"], "montant_corrige"].sum())
sans_ident = caisse.loc[~caisse["identique_precedente"], "montant_corrige"].sum() - ctrl["total_affiche"].sum()
NUM("ecart_sans_ident", sans_ident); NUM("ecart_sans_ident_pct", sans_ident / ctrl["total_affiche"].sum() * 100)
```
<!--sortie-->
```text
NUM ecart_restant 3498.679999999935
NUM ecart_restant_pct 0.6236796288796986
NUM n_identiques 154
NUM montant_identiques 7009.279999999999
NUM ecart_sans_ident -3510.5999999999767
NUM ecart_sans_ident_pct -0.6258045048832978
```

Après reconstitution, l'écart ne disparaît pas : il **change de signe**. Au lieu de 13 077 € **manquants**, il y a maintenant 3 499 € **en trop** (0,62 % du total). La cause est la seconde anomalie du fichier : des lignes **strictement identiques** à une ligne précédente, au nombre de 154, pour 7 009 € : probablement des **doubles scans** à la caisse.

Faut-il les supprimer ? Le total de contrôle dit **combien** d'euros sont en trop, pas **lesquelles** des lignes le sont, car deux lignes identiques peuvent aussi être **légitimes** : un client qui achète deux fois le même article, enregistré en deux passages. Voici l'arithmétique des deux décisions possibles.

| Décision | Écart au total de la caisse |
|---|---|
| garder toutes les lignes (et les signaler) | +3 499 € (+0,62 %) |
| supprimer toutes les lignes identiques | -3 511 € (-0,63 %) |

Les deux erreurs sont du même ordre de grandeur et de signe opposé : aucune décision n'est exacte, et la bonne réponse est de **ne rien supprimer sans preuve** : on **garde** les lignes, on les **marque** (`identique_precedente`), et l'on **écrit** l'incertitude résiduelle (de l'ordre de 0,6 % du chiffre d'affaires de la caisse). En fin de section, nous ouvrirons le fichier de vérité pour savoir ce qu'il en était vraiment.

```python hide
from style import setup, BLEU, ORANGE, ROUGE, MUET, AQUA, VIOLET, save
import matplotlib.pyplot as plt
setup()
fig, ax = plt.subplots(figsize=(7.2, 3.2))
mois = np.arange(12)
ax.bar(mois - 0.2, ctrl["ecart"].values, 0.4, color=ORANGE, label="avant : total affiché − somme des montants lus")
ax.bar(mois + 0.2, ctrl["total_affiche"].values - par_fichier, 0.4, color=BLEU, label="après reconstitution des montants vides")
ax.axhline(0, color=MUET, lw=0.8)
ax.set_xticks(mois); ax.set_xticklabels(["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."], fontsize=8)
ax.set_ylabel("euros"); ax.set_ylim(-900, 3300); ax.legend(loc="upper left", fontsize=8)
ax.set_title("Écart entre le total affiché par la caisse et la somme des lignes", loc="left")
save(fig, "ch02-ecarts-caisse.png")
```
<!--sortie-->
```text
figure : ch02-ecarts-caisse.png
```

![Écart mensuel entre le total affiché en pied de chaque fichier de la caisse et la somme des montants lus : avant correction, les montants vides font « manquer » de l'argent (barres orange, positives) ; après reconstitution, les lignes doublées en font apparaître en trop (barres bleues, négatives).](figures/ch02-ecarts-caisse.png)

### 2.2.4 Lire l'export du site

L'export du site est d'une autre nature : un seul fichier d'en-têtes de commande (`site_commandes.csv`), un fichier de lignes (`site_lignes.csv`), liés par la référence `order_ref`. Tout est écrit **en texte**, et la méthode est la même : ne rien convertir automatiquement, **regarder** d'abord.

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str, keep_default_na=False)
lignes_site = pd.read_csv("donnees/site_lignes.csv")
print(site[["order_ref", "created_at", "status", "total", "currency"]].head(4).to_string(index=False))
print(site["status"].value_counts().to_dict())
print(site["currency"].value_counts().to_dict())
```
<!--sortie-->
```text
 order_ref          created_at status    total currency
WEB-023473 2025-01-01 09:27:00   PAID  34,92 €      EUR
WEB-023450 2025-01-01 11:44:00   paid  63,66 €      eur
WEB-023464 2025-01-01 13:14:00   paid 195,40 €      EUR
WEB-023465 2025-01-01 14:22:00   paid  81,07 €      EUR
{'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186}
{'EUR': 4987, 'eur': 643, '€': 629}
```
<!--sortie-->

Trois remarques s'imposent. Le **statut** est écrit de trois façons (`paid`, `PAID`, `Paid`) : une comparaison avec `== "paid"` laisserait de côté 40 % des commandes payées. La **devise** est écrite de trois façons aussi (`EUR`, `eur`, `€`) : une seule devise en réalité, mais un `groupby` sur la colonne brute en ferait trois groupes. Et le **montant** est un texte, avec un symbole, une virgule ou un point selon la ligne : `"34,92 €"`, `"158.42"`. Le plus sournois est ailleurs : regardons l'ordre de grandeur du montant mois par mois, après une conversion qui ignore pour l'instant tout format exotique.

```python
site["brut"] = pd.to_numeric(site["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", "."), errors="coerce")
site["date_heure"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="ISO8601")
site["mois"] = site["date_heure"].dt.month
mediane = site[site["customer_email"].str.lower() != "test@example.com"].groupby("mois")["brut"].median().round(0)
print(mediane.loc[7:11].to_string())
```
<!--sortie-->
```text
mois
7       91.0
8       87.0
9     1741.0
10    8426.0
11    7190.0
```
<!--sortie-->

```python hide
st = site["status"].value_counts(); payees = st[st.index.str.lower() == "paid"]
NUM("part_paid_hors", (1 - st["paid"] / payees.sum()) * 100)
NUM("med_aout", mediane.loc[8]); NUM("med_sept", mediane.loc[9]); NUM("med_oct", mediane.loc[10])
sp = site[site["customer_email"].str.lower() != "test@example.com"]
sp = sp.assign(utc=sp["created_at"].str.endswith("Z"))
NUM("med_non_utc", sp.loc[~sp["utc"], "brut"].median()); NUM("med_utc", sp.loc[sp["utc"], "brut"].median())
NUM("premier_utc", sp.loc[sp["utc"], "date_heure"].min().day)
```
<!--sortie-->
```text
NUM part_paid_hors 40.243701630166306
NUM med_aout 87.0
NUM med_sept 1741.0
NUM med_oct 8426.0
NUM med_non_utc 83.23
NUM med_utc 7901.0
NUM premier_utc 15
```

Voilà une anomalie que **seul un contrôle d'ordre de grandeur** détecte : la **médiane du montant** vaut 87 € en août, 1 741 € en septembre et 8 426 € en octobre. Personne n'a vendu pour 8 000 € de bougies : à partir d'une certaine date, la plateforme exporte les montants **en centimes**. La rupture coïncide avec un autre changement, discret : à partir du 15 septembre, le texte de la date se termine par un `Z` (ISO 8601, heure UTC), alors qu'il n'en avait pas auparavant. Une mise à jour du site a changé **deux choses à la fois**, et n'en a annoncé aucune. L'hypothèse à tester : *les montants sont en centimes exactement quand la date porte le `Z`*. La médiane brute vaut 83 € sans `Z` et 7 901 € avec `Z`.

On **teste l'hypothèse** de la seule manière convaincante : on corrige, puis on **compare avec une autre source**, ici la somme des lignes de détail de chaque commande, qui est indépendante du montant total de l'en-tête.

```python
site["en_utc"] = site["created_at"].str.endswith("Z")
site["total_num"] = np.where(site["en_utc"], site["brut"] / 100, site["brut"])
lignes_site["montant"] = (lignes_site["qty"] * lignes_site["unit_price"] * (1 - lignes_site["discount_pct"] / 100)).round(2)
somme_lignes = lignes_site.groupby("order_ref")["montant"].sum().rename("somme_lignes")
test = site[site["customer_email"].str.lower() != "test@example.com"].drop_duplicates("order_ref").merge(somme_lignes, on="order_ref", how="left")
print("commandes dont le total égale la somme des lignes :", round(((test["total_num"] - test["somme_lignes"]).abs() < 0.011).mean() * 100, 1), "%")
```
<!--sortie-->
```text
commandes dont le total égale la somme des lignes : 100.0 %
```
<!--sortie-->

```python hide
NUM("part_total_egal", ((test["total_num"] - test["somme_lignes"]).abs() < 0.011).mean() * 100); NUM("n_test_ctrl", len(test))
```
<!--sortie-->
```text
NUM part_total_egal 100.0
NUM n_test_ctrl 6078
```

Sur 6 078 commandes, **100 %** ont un total égal à la somme de leurs lignes : l'hypothèse « centimes si et seulement si `Z` » est confirmée, au centime près. Reste à regarder la **date** elle-même. Un `Z` signifie « heure UTC » : si elle l'était vraiment, les heures de commande devraient se décaler d'une ou deux heures par rapport à celles d'avant la mise à jour, puisque la boutique n'est pas à l'heure UTC. Comparons l'heure moyenne de commande avant et après.

```python
heure_moyenne = site.assign(h=site["date_heure"].dt.hour).groupby("en_utc")["h"].mean().round(2)
print(heure_moyenne.to_dict())
```
<!--sortie-->
```text
{False: 15.45, True: 15.37}
```
<!--sortie-->

```python hide
NUM("h_avant", heure_moyenne.loc[False]); NUM("h_apres", heure_moyenne.loc[True])
```
<!--sortie-->
```text
NUM h_avant 15.45
NUM h_apres 15.37
```

L'heure moyenne est de 15,45 avant et de 15,37 après : **aucun décalage**. Le `Z` est donc une étiquette sans effet sur les heures, ou les horodatages sont restés locaux malgré l'étiquette : nous les traiterons comme des heures locales, en **documentant** l'hypothèse (et en la signalant au responsable du site). Ce raisonnement, tester une hypothèse sur la distribution plutôt que de la croire, vaut mieux que n'importe quelle conversion de fuseau faite « au cas où ».

Il reste à **filtrer**. Trois catégories de lignes ne sont pas des ventes : les **commandes de test** (adresse `test@example.com`), les **doublons d'export** (même référence deux fois : l'export a été relancé) et les **commandes annulées**. On les retire **dans cet ordre, en comptant ce que l'on retire**, pour pouvoir en rendre compte.

```python
site["email_norm"] = site["customer_email"].str.strip().str.lower()
n0 = len(site)
s1 = site[site["email_norm"] != "test@example.com"]
s2 = s1.drop_duplicates("order_ref")
s3 = s2[s2["status"].str.lower() != "cancelled"]
print("export brut :", n0, "| sans tests :", len(s1), "| sans doublons :", len(s2), "| sans annulées :", len(s3))
cmd_site = site.assign(est_test=site["email_norm"] == "test@example.com", est_double=site.duplicated("order_ref"), statut=site["status"].str.lower())
```
<!--sortie-->
```text
export brut : 6259 | sans tests : 6199 | sans doublons : 6078 | sans annulées : 5897
```
<!--sortie-->

```python hide
NUM("site_brut", n0); NUM("site_tests", n0 - len(s1)); NUM("site_doubles", len(s1) - len(s2)); NUM("site_annulees", len(s2) - len(s3)); NUM("site_net", len(s3))
NUM("ca_annulees", s2.loc[s2["status"].str.lower() == "cancelled", "total_num"].sum()); NUM("ca_site_net", s3["total_num"].sum())
cmd_ref, lignes_ref = O.lire_site()
assert abs(cmd_ref.loc[~cmd_ref.est_test & ~cmd_ref.est_double & (cmd_ref.statut != "cancelled"), "total_num"].sum() - s3["total_num"].sum()) < 0.01
```
<!--sortie-->
```text
NUM site_brut 6259
NUM site_tests 60
NUM site_doubles 121
NUM site_annulees 181
NUM site_net 5897
NUM ca_annulees 17551.32
NUM ca_site_net 600164.1299999999
```

L'export contient 6 259 lignes ; on en retire 60 de test, 121 doublons et 181 annulées, pour **5 897 commandes** (600 164,13 € de chiffre d'affaires). Les commandes annulées pesaient 17 551,32 € : elles n'ont pas été vendues, et les compter gonflerait le chiffre d'affaires.

> 💡 **Intuition.** Un export n'est pas un fait, c'est un **document** produit par un logiciel, avec ses conventions et ses accidents. Avant de calculer avec lui, on le **lit comme on lirait un rapport** : que contient-il, que signifie chaque ligne, qu'est-ce qui a changé ? Les deux accidents de cet export (les centimes, les doublons) se détectent par **l'ordre de grandeur** et par le **comptage**, pas par la lecture ligne à ligne.

### 2.2.5 Relier les ventes aux produits : la jointure qui multiplie

La caisse ne note ni numéro de produit ni coût d'achat, seulement le **nom de l'article** et son prix unitaire. Pour calculer une marge, il faut retrouver le produit dans la table des produits. La première idée est de joindre **sur le nom**, normalisé avec la fonction `cle_texte` de la section 2.1.6.

```python
produits = pd.read_csv("donnees/produits.csv")
caisse["nom_cle"] = caisse["article"].map(cle_texte)
produits["nom_cle"] = produits["nom_produit"].map(cle_texte)
par_nom = caisse.merge(produits[["nom_cle", "id_produit", "cout_achat"]], on="nom_cle", how="left")
print("lignes avant :", len(caisse), "| après la jointure sur le nom :", len(par_nom))
try:
    caisse.merge(produits[["nom_cle", "id_produit"]], on="nom_cle", validate="m:1")
except Exception as e:
    print(type(e).__name__, ":", str(e).splitlines()[0])
```
<!--sortie-->
```text
lignes avant : 12678 | après la jointure sur le nom : 25356
MergeError : Merge keys are not unique in right dataset; not a many-to-one merge
```
<!--sortie-->

```python hide
NUM("n_avant_nom", len(caisse)); NUM("n_apres_nom", len(par_nom)); NUM("ca_par_nom", par_nom["montant"].fillna(0).sum()); NUM("ca_sans_nom", caisse["montant"].fillna(0).sum())
```
<!--sortie-->
```text
NUM n_avant_nom 12678
NUM n_apres_nom 25356
NUM ca_par_nom 1095792.8399999999
NUM ca_sans_nom 547896.4199999999
```

Le nombre de lignes **double** : de 12 678 à 25 356. La cause, vue en 2.1.6 : **chaque nom de produit est porté par deux produits**, donc chaque ligne de caisse se retrouve associée aux deux. Le chiffre d'affaires, recalculé sur cette table, passerait de 547 896 € à 1 095 793 €. C'est le piège classique de la jointure **n–n** : aucune erreur, un résultat **doublement faux**. Le paramètre `validate="m:1"` l'attrape, avec un message clair (le dernier affichage ci-dessus) ; c'est pourquoi il faut **toujours** le déclarer.

Que faire ? Chercher un **second élément de clé**. Les deux produits qui partagent un nom ont des **prix différents** (sauf exception, voir ci-dessous) : le prix de la ligne de caisse doit égaler le prix du catalogue majoré de la hausse de 3 % du 1er janvier 2025, ce qui permet de départager. Joindre sur un **prix** pose un problème technique : des nombres décimaux ne s'égalent pas toujours exactement (arrondis). On joint donc sur le nom, puis l'on **filtre** les candidats dont le prix est « assez proche » (à un demi-centime près).

```python
produits["prix_2025"] = (produits["prix_vente"] * 1.03).round(2)
c = caisse.reset_index().merge(produits[["nom_cle", "id_produit", "prix_2025", "cout_achat"]], on="nom_cle")
c = c[(c["prix_unitaire"] - c["prix_2025"]).abs() < 0.011]
n = c.groupby("index").size()
print("lignes appariées de façon unique :", int((n == 1).sum()), "| ambiguës :", int((n > 1).sum()), "| sans candidat :", len(caisse) - len(n))
```
<!--sortie-->
```text
lignes appariées de façon unique : 12452 | ambiguës : 226 | sans candidat : 0
```
<!--sortie-->

```python hide
NUM("n_unique", (n == 1).sum()); NUM("n_ambigu", (n > 1).sum()); NUM("n_sans_cand", len(caisse) - len(n))
jum = produits[produits["nom_cle"].map(produits.groupby("nom_cle")["prix_2025"].nunique()) == 1]
NUM("n_jumeaux_produits", len(jum)); NUM("id_j1", jum["id_produit"].iloc[0]); NUM("id_j2", jum["id_produit"].iloc[1])
NUM("prix_jumeaux", jum["prix_vente"].iloc[0]); NUM("cout_jumeaux", jum["cout_achat"].iloc[0]); NUM("cout_jumeaux_2", jum["cout_achat"].iloc[1])
```
<!--sortie-->
```text
NUM n_unique 12452
NUM n_ambigu 226
NUM n_sans_cand 0
NUM n_jumeaux_produits 2
NUM id_j1 62
NUM id_j2 72
NUM prix_jumeaux 2.9
NUM cout_jumeaux 1.53
NUM cout_jumeaux_2 1.53
```

Avec le prix, **12 452 lignes** trouvent un produit **unique**, aucune n'est sans candidat, et 226 restent **ambiguës**. Ces dernières correspondent à une seule paire de produits, les numéros 62 et 72 (le même nom), qui ont **exactement le même prix** (2,90 €) **et le même coût d'achat** (1,53 € et 1,53 €) : **aucun** élément de la ligne de caisse ne permet de dire de quel produit il s'agit. Deux conséquences :

- l'identité du produit reste **inconnue** pour ces 226 lignes : on laisse `id_produit` **vide** plutôt que de tirer au sort ;
- mais la **marge n'est pas affectée**, puisque les deux produits ont le même coût : on peut y mettre la moyenne des coûts candidats. C'est une **ambiguïté sans conséquence pour la question posée**, et c'est ce qu'il faut écrire (elle en aurait pour une question sur le stock par produit).

On range ce résultat dans la table de caisse : l'identifiant du produit quand il est unique, le coût d'achat dans tous les cas.

```python
unique = n[n == 1].index
caisse["id_produit"] = np.nan
caisse.loc[unique, "id_produit"] = c[c["index"].isin(unique)].set_index("index")["id_produit"]
caisse["cout_achat"] = c.groupby("index")["cout_achat"].mean()
print(caisse[["article", "prix_unitaire", "id_produit", "cout_achat"]].head(3).to_string(index=False))
print("lignes sans id_produit :", int(caisse["id_produit"].isna().sum()), "| sans coût :", int(caisse["cout_achat"].isna().sum()))
```
<!--sortie-->
```text
         article  prix_unitaire  id_produit  cout_achat
       Poêle mat          40.07         2.0       21.47
  Tapis nordique          64.79        26.0       28.56
Théière rustique          52.43         5.0       24.65
lignes sans id_produit : 226 | sans coût : 0
```
<!--sortie-->

```python hide
ref_prod = O.apparier_produit_caisse(cai_ref, O.charger_produits())
assert (ref_prod["id_produit"].fillna(-1).values == caisse["id_produit"].fillna(-1).values).all()
```

Pour le site, la question ne se pose pas : les lignes portent une **référence produit** (`sku`, comme `P043`) qui contient directement le numéro du produit. Une vraie clé vaut mieux que la meilleure reconstitution : si l'on peut obtenir de la source un identifiant plutôt qu'un libellé, **on le demande**.

> ⚠️ **Piège : les homonymes.** Dans nos données, c'est un artefact de fabrication ; dans la vie réelle, c'est courant (deux clients nommés « Martin », deux articles « Coussin bleu » de tailles différentes). **Un nom n'est jamais une clé.** Quand on est forcé de joindre sur un libellé, on teste l'unicité de la clé (`validate=`), on lui adjoint un second critère, et l'on **compte** ce qui reste ambigu.

```python hide
fig, ax = plt.subplots(figsize=(7.2, 2.6))
etiq = ["lignes de caisse", "après jointure\nsur le nom seul", "après jointure sur\nnom + prix (unique)", "ambiguës (même nom,\nmême prix)"]
vals = [len(caisse), len(par_nom), int((n == 1).sum()), int((n > 1).sum())]
ax.barh(etiq[::-1], vals[::-1], color=[MUET, ORANGE, ROUGE, BLEU])
for i, v in enumerate(vals[::-1]):
    ax.text(v + 300, i, f"{v:,.0f}".replace(",", " "), va="center", fontsize=8)
ax.set_xlim(0, 30000); ax.set_xlabel("nombre de lignes"); ax.grid(axis="y", visible=False)
ax.set_title("Une jointure sur le nom seul double le nombre de lignes", loc="left")
save(fig, "ch02-jointure-effectifs.png")
```
<!--sortie-->
```text
figure : ch02-jointure-effectifs.png
```

![Nombre de lignes de la caisse avant et après jointure avec les produits : la jointure sur le nom seul double les lignes ; ajouter le prix à la clé rétablit un produit unique, sauf pour une paire de produits indiscernables.](figures/ch02-jointure-effectifs.png)

### 2.2.6 Harmoniser et empiler : la table des ventes

Les deux sources sont maintenant propres. Pour les empiler, il faut qu'elles aient le **même schéma** : mêmes noms de colonnes, mêmes types, mêmes unités. On le **conçoit d'abord**, comme un contrat.

| Colonne commune | Définition | Caisse | Site |
|---|---|---|---|
| `source`, `canal` | d'où vient la ligne | `caisse`, `Boutique` | `site`, `Site` |
| `id_commande` | numéro de commande | numéro du ticket sans le `T` | référence sans `WEB-` |
| `date` | jour de la vente | date du ticket | date de l'horodatage |
| `id_produit`, `nom_produit`, `categorie` | produit, en écriture normalisée | reconstitués (2.2.5) ; nom et catégorie pris dans le catalogue | `sku` converti ; nom et catégorie pris dans le catalogue |
| `quantite`, `prix_unitaire`, `remise_pct` | comme dans la source | remise connue seulement au dernier trimestre | `qty`, `unit_price`, `discount_pct` |
| `montant` | montant TTC payé, **en euros** | lu, ou reconstitué | quantité × prix × (1 − remise) |
| `cout_achat` | coût d'achat unitaire | du catalogue | du catalogue |
| `montant_reconstitue`, `identique_precedente` | **indicateurs de qualité** | oui / ligne identique à la précédente | non |

Le schéma est le **contrat** entre les sources et l'analyse : si une colonne ne peut pas être alimentée honnêtement, on la laisse **vide** plutôt que de lui donner une valeur plausible. Construisons d'abord la partie caisse. Le nom et la catégorie viennent du **catalogue** (une seule écriture normalisée au lieu des cinq de la caisse).

```python
ref_nom = produits.drop_duplicates("nom_cle").set_index("nom_cle")[["nom_produit", "categorie"]]
v_caisse = caisse.drop(columns=["categorie"]).join(ref_nom, on="nom_cle")
v_caisse = v_caisse.assign(source="caisse", canal="Boutique", montant=v_caisse["montant_corrige"], montant_reconstitue=v_caisse["montant_vide"])
print(v_caisse[["id_commande", "nom_produit", "categorie", "quantite", "montant", "montant_reconstitue"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
 id_commande      nom_produit categorie  quantite  montant  montant_reconstitue
       23468        Poêle mat   Cuisine         1    40.07                False
       23468   Tapis nordique    Maison         1    64.79                False
       23458 Théière rustique   Cuisine         1    52.43                False
```
<!--sortie-->

Puis la partie site : on ne garde que les commandes valides, on relie les lignes à leur commande, on convertit la référence produit, on calcule le montant, et l'on ajoute le nom, la catégorie et le coût du catalogue par une jointure **m:1** (vérifiée).

```python
ok = cmd_site[~cmd_site["est_test"] & ~cmd_site["est_double"] & (cmd_site["statut"] != "cancelled")]
ls = lignes_site.merge(ok[["order_ref", "date_heure"]].assign(id_commande=ok["order_ref"].str[4:].astype(int)), on="order_ref", validate="m:1")
ls = ls.assign(id_produit=ls["sku"].str[1:].astype(int), quantite=ls["qty"], prix_unitaire=ls["unit_price"], remise_pct=ls["discount_pct"])
v_site = ls.merge(produits[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
v_site = v_site.assign(source="site", canal="Site", date=v_site["date_heure"].dt.normalize(), montant_reconstitue=False, identique_precedente=False)
print("lignes de commandes valides :", len(ls), "| lignes après jointure produits :", len(v_site))
```
<!--sortie-->
```text
lignes de commandes valides : 13510 | lignes après jointure produits : 13510
```
<!--sortie-->

Il ne reste qu'à **empiler** les deux parties, en ne gardant que les colonnes du contrat et dans le même ordre, puis à calculer la marge (2.1.2).

```python
cols = ["source", "canal", "id_commande", "date", "id_produit", "nom_produit", "categorie", "quantite", "prix_unitaire", "remise_pct", "montant",
        "cout_achat", "montant_reconstitue", "identique_precedente"]
ventes = pd.concat([v_caisse[cols], v_site[cols]], ignore_index=True)
ventes["marge_ht"] = ventes["montant"] / 1.20 - ventes["quantite"] * ventes["cout_achat"]
resume = ventes.groupby("canal").agg(lignes=("montant", "size"), commandes=("id_commande", "nunique"), ca=("montant", "sum"), marge=("marge_ht", "sum"))
print(resume.round(0).to_string())
```
<!--sortie-->
```text
          lignes  commandes        ca     marge
canal                                          
Boutique   12678       5442  564473.0  178813.0
Site       13510       5897  600164.0  189431.0
```
<!--sortie-->

```python hide
ref_v, _ = O.ventes_2025()
assert len(ref_v) == len(ventes) and abs(ref_v["montant"].sum() - ventes["montant"].sum()) < 0.01 and abs(ref_v["marge_ht"].sum() - ventes["marge_ht"].sum()) < 0.01
NUM("n_ventes", len(ventes)); NUM("n_cmd_boutique", resume.loc["Boutique", "commandes"]); NUM("n_cmd_site", resume.loc["Site", "commandes"])
NUM("ca_boutique", resume.loc["Boutique", "ca"]); NUM("ca_site", resume.loc["Site", "ca"]); NUM("marge_boutique", resume.loc["Boutique", "marge"]); NUM("marge_site", resume.loc["Site", "marge"])
NUM("taux_marge_ventes", ventes["marge_ht"].sum() / (ventes["montant"].sum() / 1.2) * 100)
NUM("n_lignes_site", len(v_site)); NUM("n_lignes_caisse_v", len(v_caisse))
```
<!--sortie-->
```text
NUM n_ventes 26188
NUM n_cmd_boutique 5442
NUM n_cmd_site 5897
NUM ca_boutique 564472.59
NUM ca_site 600164.13
NUM marge_boutique 178813.49500000002
NUM marge_site 189431.14500000002
NUM taux_marge_ventes 37.94260994965023
NUM n_lignes_site 13510
NUM n_lignes_caisse_v 12678
```

**La table demandée par la gérante existe** : 26 188 lignes de vente pour l'année 2025, avec le produit, la catégorie, le montant, le coût d'achat et la marge (37,9 % du chiffre d'affaires hors taxe sur l'ensemble). La caisse a 5 442 commandes pour 564 473 € et le site 5 897 commandes pour 600 164 €. Mais **une table n'est pas fiable parce qu'elle a été construite sans erreur** : il faut maintenant la contrôler.

![Chaîne de préparation des ventes de 2025.](figures/ch02-chaine.png)

```python hide
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(8.4, 3.4)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 40)
def boite(x, y, w, h, txt, c=BLEU, fs=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc="white", ec=c, lw=1.6))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)
def fleche(x1, y1, x2, y2, c=MUET):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=c, lw=1.4))
boite(1, 27, 20, 9, "12 fichiers\nde la caisse\n(formats changeants)")
boite(1, 14, 20, 9, "export du site\n(montants en texte,\ncentimes dès sept.)", ORANGE)
boite(1, 1, 20, 9, "catalogue produits\n(coût d'achat)", MUET)
boite(30, 20, 17, 12, "lire, typer,\nharmoniser\n(2.2.3 à 2.2.5)")
boite(58, 20, 17, 12, "table des ventes\nau schéma commun\n(2.2.6)")
boite(84, 20, 15, 12, "agrégats,\nanalyses\n(2.3)", AQUA)
for y in (31.5, 18.5):
    fleche(21.8, y, 29.3, 26 + (y - 25) * 0.3)
fleche(21.8, 5.5, 29.3, 22)
fleche(47.8, 26, 57.3, 26); fleche(75.8, 26, 83.3, 26)
ax.text(52.5, 14, "contrôles : total des fichiers, somme des lignes,\ncomptage avant/après, comparaison à la base", ha="center", fontsize=8, color=ROUGE)
fleche(52.5, 16.5, 52.5, 19.4, ROUGE)
save(fig, "ch02-chaine.png")
```
<!--sortie-->
```text
figure : ch02-chaine.png
```

### 2.2.7 Contrôler : comparer à la base, puis ouvrir la vérité

Pour contrôler la table des ventes, il faut un **point de comparaison indépendant**. Ici, nous en avons un : la base du volume I (`commandes` et `lignes_commande`), qui contient les mêmes ventes telles que le système de gestion les a enregistrées. On compare, **canal par canal**, le chiffre d'affaires de notre table avec celui de la base.

```python
cmd_b = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
base = lig.merge(cmd_b[["id_commande", "date_commande", "canal"]], on="id_commande", validate="m:1")
base = base[base["date_commande"].dt.year == 2025]
comp = pd.DataFrame({"table_ventes": ventes.groupby("canal")["montant"].sum(), "base": base.groupby("canal")["montant"].sum()}).dropna()
comp["ecart"] = comp["table_ventes"] - comp["base"]
comp["ecart_pct"] = comp["ecart"] / comp["base"] * 100
print(comp.round(2).to_string())
```
<!--sortie-->
```text
          table_ventes       base     ecart  ecart_pct
canal                                                 
Boutique     564472.59  560973.91   3498.68       0.62
Site         600164.13  617715.45 -17551.32      -2.84
```
<!--sortie-->

```python hide
NUM("ecart_b", comp.loc["Boutique", "ecart"]); NUM("ecart_b_pct", comp.loc["Boutique", "ecart_pct"])
NUM("ecart_s", comp.loc["Site", "ecart"]); NUM("ecart_s_pct", comp.loc["Site", "ecart_pct"]); NUM("ecart_s_abs", -comp.loc["Site", "ecart"]); NUM("ecart_s_pct_abs", -comp.loc["Site", "ecart_pct"])
NUM("base_boutique", comp.loc["Boutique", "base"]); NUM("base_site", comp.loc["Site", "base"])
```
<!--sortie-->
```text
NUM ecart_b 3498.679999999935
NUM ecart_b_pct 0.6236796288796986
NUM ecart_s -17551.31999999995
NUM ecart_s_pct -2.841327669560467
NUM ecart_s_abs 17551.31999999995
NUM ecart_s_pct_abs 2.841327669560467
NUM base_boutique 560973.91
NUM base_site 617715.45
```

Deux écarts, **deux explications** à produire. Pour la **Boutique**, la table dépasse la base de 3 498,68 € (+0,62 %) : on retrouve exactement l'écart du total de contrôle de 2.2.3, c'est-à-dire les lignes identiques **et** la reconstitution approximative des montants. Pour le **Site**, la table est **inférieure** à la base de 17 551,32 € (2,8 %) : c'est la somme des commandes annulées retirées en 2.2.4 (17 551,32 €), qui existent dans la base mais ne sont pas des ventes. Un écart n'est « bon » ou « mauvais » que **s'il est expliqué**.

Ouvrons maintenant la **vérité**. Le fichier `verite_caisse.csv` indique, pour chaque ligne de chaque fichier, le numéro de la ligne de commande d'origine et si c'est un vrai double scan. Cela permet de savoir **ce que valaient nos décisions**, une chose impossible dans la vie réelle.

```python
verite = pd.read_csv("donnees/verite_caisse.csv")
caisse["rang"] = caisse.groupby("fichier").cumcount(); verite["rang"] = verite.groupby("fichier").cumcount()
cv = caisse.merge(verite[["fichier", "rang", "id_ligne", "est_doublon"]], on=["fichier", "rang"], validate="1:1")
cv["montant_vrai"] = cv["id_ligne"].map(lig.set_index("id_ligne")["montant"])
ident = cv[cv["identique_precedente"]]
print("lignes identiques :", len(ident), "| vrais doubles scans :", int(ident["est_doublon"].sum()), "| répétitions légitimes :", int((ident["est_doublon"] == 0).sum()))
vides = cv[cv["montant_vide"] & (cv["est_doublon"] == 0)]
print("montants vides : reconstitués", round(vides["montant_corrige"].sum(), 2), "€ | vrais", round(vides["montant_vrai"].sum(), 2), "€")
```
<!--sortie-->
```text
lignes identiques : 154 | vrais doubles scans : 67 | répétitions légitimes : 87
montants vides : reconstitués 16445.46 € | vrais 16203.78 €
```
<!--sortie-->

```python hide
NUM("ident_total", len(ident)); NUM("ident_vrais", ident["est_doublon"].sum()); NUM("ident_legit", (ident["est_doublon"] == 0).sum())
NUM("vides_rec", vides["montant_corrige"].sum()); NUM("vides_vrai", vides["montant_vrai"].sum())
NUM("dup_euros", cv.loc[cv["est_doublon"] == 1, "montant_corrige"].sum()); NUM("rec_err", vides["montant_corrige"].sum() - vides["montant_vrai"].sum())
NUM("n_doublons_vrais", cv["est_doublon"].sum())
assert abs(cv.loc[cv["est_doublon"] == 1, "montant_corrige"].sum() + (vides["montant_corrige"].sum() - vides["montant_vrai"].sum()) - comp.loc["Boutique", "ecart"]) < 0.01
```
<!--sortie-->
```text
NUM ident_total 154
NUM ident_vrais 67
NUM ident_legit 87
NUM vides_rec 16445.46
NUM vides_vrai 16203.779999999999
NUM dup_euros 3257.0
NUM rec_err 241.6800000000003
NUM n_doublons_vrais 67
```

La vérité éclaire notre choix. Sur les 154 lignes identiques, **67** seulement sont de vrais doubles scans ; **87** sont des répétitions légitimes. Supprimer toutes les lignes identiques aurait donc retiré 87 ventes réelles. En ne supprimant rien, nous avons conservé 67 lignes en trop, pour 3 257 € : c'est le gros de l'écart de 3 499 € de la Boutique. Le reste, 242 €, vient de la reconstitution des montants vides : nous avons supposé une remise nulle avant octobre, et le montant reconstitué (16 445,46 €) dépasse un peu le vrai (16 203,78 €), parce que des remises existaient. **Aucune de nos deux hypothèses n'était parfaite, et l'erreur totale reste à 0,62 %** : c'est ce que l'on écrit dans la note de méthode, et c'est suffisant pour la question de la gérante (la marge par catégorie), mais ce ne serait pas acceptable pour un rapprochement comptable au centime (chapitre 3).

### 2.2.8 Chercher ce qui manque : les anti-jointures

Une jointure ne dit pas seulement ce qui se **retrouve**, mais aussi ce qui **ne se retrouve pas**. L'**anti-jointure** (les lignes d'une table qui n'ont **aucune** correspondance dans l'autre) est l'outil de recherche des manques. On l'obtient avec `indicator=True` puis un filtre sur `left_only`. Quatre questions, quatre anti-jointures.

**Les références du site existent-elles toutes dans la base ?** On joint les références de l'export à celles de la base (qui s'écrivent `WEB-` suivi du numéro sur six chiffres).

```python
refs_base = "WEB-" + cmd_b["id_commande"].astype(str).str.zfill(6)
anti = site[["order_ref"]].drop_duplicates().merge(refs_base.rename("order_ref"), on="order_ref", how="left", indicator=True)
print("références de l'export absentes de la base :", int((anti["_merge"] == "left_only").sum()), "| exemples :", anti.loc[anti["_merge"] == "left_only", "order_ref"].head(3).tolist())
sens_inverse = cmd_b[(cmd_b["canal"] == "Site") & (cmd_b["date_commande"].dt.year == 2025)]
print("commandes Site 2025 de la base absentes de l'export :", int((~("WEB-" + sens_inverse["id_commande"].astype(str).str.zfill(6)).isin(site["order_ref"])).sum()))
```
<!--sortie-->
```text
références de l'export absentes de la base : 60 | exemples : ['WEB-T0011', 'WEB-T0015', 'WEB-T0014']
commandes Site 2025 de la base absentes de l'export : 0
```
<!--sortie-->

```python hide
NUM("n_refs_absentes", (anti["_merge"] == "left_only").sum())
```
<!--sortie-->
```text
NUM n_refs_absentes 60
```

Les 60 références absentes de la base sont des **commandes de test** (leur numéro commence par `WEB-T`) : l'anti-jointure les aurait retrouvées même sans l'adresse électronique. Dans l'autre sens, **aucune** commande de la base n'est absente de l'export : rien n'a été perdu à l'extraction.

**Quelle part de l'activité n'est dans aucun des deux fichiers ?** La gérante a demandé « la caisse et le site ». Or la boutique vend aussi par un troisième canal, les réseaux : la base le montre.

```python
ca_canaux = base.groupby("canal")["montant"].sum()
couvert = ca_canaux[["Boutique", "Site"]].sum()
print("part du chiffre d'affaires 2025 couverte par la caisse et le site :", round(couvert / ca_canaux.sum() * 100, 1), "%")
print("chiffre d'affaires du canal Réseaux, absent des deux sources :", round(ca_canaux["Réseaux"], 0), "€")
```
<!--sortie-->
```text
part du chiffre d'affaires 2025 couverte par la caisse et le site : 89.0 %
chiffre d'affaires du canal Réseaux, absent des deux sources : 146074.0 €
```
<!--sortie-->

```python hide
NUM("part_couverte", couvert / ca_canaux.sum() * 100); NUM("ca_reseaux", ca_canaux["Réseaux"]); NUM("part_reseaux", ca_canaux["Réseaux"] / ca_canaux.sum() * 100)
```
<!--sortie-->
```text
NUM part_couverte 88.97355371416722
NUM ca_reseaux 146074.36
NUM part_reseaux 11.026446285832767
```

La table construite couvre **89 %** du chiffre d'affaires de 2025 : le canal Réseaux, soit 146 074 € (11 %), n'a **aucune source** dans les fichiers que l'on nous a remis. C'est une information à **rendre à la gérante** avant qu'elle ne présente la table comme « toutes les ventes ».

**Les adresses électroniques du site retrouvent-elles les clients du CRM ?** Joindre les commandes du site aux clients du CRM se fait par l'adresse électronique. Essayons d'abord sur l'écriture **brute**, puis sur une écriture **normalisée** (espaces retirés, minuscules).

```python
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str, keep_default_na=False)
valides = site[site["email_norm"] != "test@example.com"].drop_duplicates("order_ref")
brut_ok = valides["customer_email"].isin(set(crm["email"]))
norm_ok = valides["email_norm"].isin(set(crm["email"].str.strip().str.lower()))
print("e-mails retrouvés dans le CRM : brut", round(brut_ok.mean() * 100, 1), "% | normalisé", round(norm_ok.mean() * 100, 1), "%")
```
<!--sortie-->
```text
e-mails retrouvés dans le CRM : brut 87.7 % | normalisé 100.0 %
```
<!--sortie-->

```python hide
NUM("part_brut_ok", brut_ok.mean() * 100); NUM("n_brut_ko", (~brut_ok).sum()); NUM("part_norm_ok", norm_ok.mean() * 100); NUM("n_valides", len(valides))
```
<!--sortie-->
```text
NUM part_brut_ok 87.6604146100691
NUM n_brut_ko 750
NUM part_norm_ok 100.0
NUM n_valides 6078
```

Sur l'écriture brute, **750 commandes** sur 6 078 ne retrouvent pas leur client (87,7 % de succès) : des majuscules, des espaces superflus. Après une normalisation de deux lignes, tout se retrouve (100 %). Cette différence illustre le principe de toute jointure sur du texte : **normaliser avant de joindre**, puis mesurer le taux de correspondance.

> ✅ **À retenir.** Une **anti-jointure** n'est pas un accessoire : c'est le moyen de répondre à « *qu'est-ce qui manque ?* », celui que la gérante n'a pas pensé à poser (le canal Réseaux), et à « *qu'est-ce qui ne devrait pas être là ?* » (les commandes de test).

### 2.2.9 Le même résultat avec trois outils

Une table de ventes de cette importance se recoupe avec **un autre outil**, pas avec le même code relancé. On écrit la table dans un fichier, puis on calcule le même résumé (lignes et chiffre d'affaires par canal et par mois) avec **DuckDB** (SQL) et avec **R**, et l'on compare à pandas.

```python
ventes["mois"] = ventes["date"].dt.strftime("%Y-%m")
ventes.to_csv(os.path.join(TMP2, "ventes.csv"), index=False)
os.environ["TMP2"] = TMP2
q = f"select canal, strftime(date, '%Y-%m') as mois, count(*) as lignes, round(sum(montant), 2) as ca from '{TMP2}/ventes.csv' group by 1, 2 order by 1, 2"
sql = duckdb.sql(q).df()
pdm = ventes.groupby(["canal", "mois"]).agg(lignes=("montant", "size"), ca=("montant", "sum")).round(2).reset_index()
print("DuckDB = pandas :", bool((sql["lignes"].values == pdm["lignes"].values).all() and np.allclose(sql["ca"].values, pdm["ca"].values)))
```
<!--sortie-->
```text
DuckDB = pandas : True
```
<!--sortie-->

Et le même calcul en **R**, avec `dplyr` (la jointure ou le regroupement s'écrivent à peu près comme en pandas : volume I, section 4.2) ; R écrit son résultat dans un fichier, que Python relit pour le comparer.

```r
library(dplyr, warn.conflicts = FALSE)
v <- read.csv(file.path(Sys.getenv("TMP2"), "ventes.csv"))
r <- v |> group_by(canal, mois) |> summarise(lignes = n(), ca = round(sum(montant), 2), .groups = "drop")
write.csv(r, file.path(Sys.getenv("TMP2"), "ventes_r.csv"), row.names = FALSE)
print(as.data.frame(r |> group_by(canal) |> summarise(lignes = sum(lignes), ca = round(sum(ca), 0))))
```
<!--sortie-->
```text
     canal lignes     ca
1 Boutique  12678 564473
2     Site  13510 600164
```
<!--sortie-->

```python
r = pd.read_csv(os.path.join(TMP2, "ventes_r.csv"))
print("R = pandas :", bool((r["lignes"].values == pdm["lignes"].values).all() and np.allclose(r["ca"].values, pdm["ca"].values)))
```
<!--sortie-->
```text
R = pandas : True
```
<!--sortie-->

```python hide
assert (sql["lignes"].values == pdm["lignes"].values).all() and (r["lignes"].values == pdm["lignes"].values).all()
```

Trois outils, un même résultat à l'euro près. Si DuckDB ou R avaient donné un écart, la première hypothèse n'aurait pas été « l'outil se trompe », mais « *je n'ai pas demandé la même chose aux deux* » : un filtre de dates différent, une jointure qui duplique, un arrondi. C'est cette recherche de la **différence de question** qui fait la valeur de la vérification croisée.

> ✅ **À retenir.**
> - **Joindre** ajoute des colonnes, **empiler** ajoute des lignes ; le **type** de jointure est un choix d'analyse, et `indicator=True` en est le diagnostic.
> - À chaque jointure, **quatre contrôles** : lignes avant et après, somme avant et après, lignes sans correspondance, unicité de la clé. `validate=` transforme l'hypothèse de cardinalité en **vérification**.
> - Une jointure **n–n** multiplie les lignes **sans erreur** : un nom n'est jamais une clé ; on ajoute un critère et l'on **compte** les ambiguïtés restantes.
> - Une source qui **dérive** (codage, séparateur, décimale, unité) se lit en **détectant** son format, pas en le devinant ; la **ligne de total** d'un fichier est une somme de contrôle gratuite.
> - On **ne supprime rien sans preuve** : on garde, on marque, on documente l'incertitude résiduelle (ici moins de 1 %).
> - Un écart n'est acceptable que **expliqué** ; une **anti-jointure** cherche ce qui manque (un canal entier, des commandes de test).
> - Deux outils valent mieux qu'un : DuckDB et R ont retrouvé les chiffres de pandas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.3 à 2.6, exercices 2.5 à 2.8.
