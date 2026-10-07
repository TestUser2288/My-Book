## 2.1 Création et dérivation de variables

Les tables que l'on reçoit contiennent rarement **les colonnes dont on a besoin** : la caisse note un prix et une quantité, mais pas la marge ; la table des commandes porte une date, mais ni le trimestre ni le jour de la semaine ; le fichier clients a une année de naissance, mais pas la tranche d'âge. Une **variable dérivée** est une colonne que l'on **calcule** à partir des autres. Cette section apprend à en fabriquer de cinq sortes (des calculs, des morceaux de date, des classes, des indicateurs et des délais), à les **documenter**, et à éviter les trois pièges qui les abîment : la division par zéro, la valeur manquante qui se propage et la fuite d'information.

### 2.1.1 Une variable dérivée est une décision

Calculer « la marge d'une ligne de vente » paraît mécanique. Pourtant, avant d'écrire la première formule, **quatre décisions** sont déjà prises, et elles changent le chiffre :

1. **Quelle définition ?** La marge est-elle calculée avant ou après remise ? Sur le prix toutes taxes comprises, ou hors taxe ? Avec le coût d'achat seul, ou avec les frais de transport ?
2. **Quelle unité ?** Des euros, un pourcentage du prix de vente (le **taux de marge**) ou du coût d'achat (le **taux de marque**) ? Les trois se confondent souvent à l'oral, et ne valent pas la même chose (volume I, section 1.5.4).
3. **Quelle date de référence ?** Le coût d'achat d'aujourd'hui, ou celui de la date de la vente ?
4. **Que faire des cas limites ?** Une vente à zéro euro, un produit sans coût d'achat, un retour.

Chacune de ces décisions est un **choix de métier**, pas de technique. C'est pourquoi on **écrit** la définition de chaque variable créée (nous y reviendrons en 2.1.7), et pourquoi deux analystes qui calculent « la marge » sans s'être parlé obtiennent deux chiffres. Par convention, dans ce chapitre : la **marge brute** d'une ligne est son **chiffre d'affaires hors taxe** moins sa **quantité multipliée par le coût d'achat** ; la **TVA** est fixée à 20 % **pour l'illustration**, et le **taux de marge** est la marge divisée par le chiffre d'affaires hors taxe.

> 💡 **Intuition.** Une variable dérivée est une **phrase** qu'on a figée dans une colonne. Si la phrase est ambiguë (« la marge »), la colonne l'est aussi, et personne ne s'en apercevra avant qu'un chiffre ne soit contesté en réunion.

### 2.1.2 Calculs simples : marges, ratios, montants

Commençons par la demande de la gérante : une marge par ligne de vente. La table des lignes contient le **montant payé** (toutes taxes comprises, après remise) ; le coût d'achat est dans la table des produits. Il faut donc d'abord **relier** les deux tables (nous détaillerons la jointure en 2.2), puis calculer.

```python
lig = pd.read_csv("donnees/lignes_commande.csv")
prod = pd.read_csv("donnees/produits.csv")
x = lig.merge(prod[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
x["ca_ht"] = x["montant"] / 1.20
x["marge_ht"] = x["ca_ht"] - x["quantite"] * x["cout_achat"]
x["taux_marge"] = x["marge_ht"] / x["ca_ht"]
cols = ["id_ligne", "nom_produit", "quantite", "montant", "marge_ht", "taux_marge"]
print(x[cols].head(4).round(3).to_string(index=False))
```
<!--sortie-->

Vérifions la première ligne **à la main**, comme on le ferait avant de faire confiance à une colonne. Un article payé {{l1_montant:.2f}} € toutes taxes comprises vaut {{l1_montant:.2f}} / 1,20 = {{l1_ca_ht:.2f}} € hors taxe ; son coût d'achat est de {{l1_cout:.2f}} € ; la marge est donc {{l1_ca_ht:.2f}} − {{l1_cout:.2f}} = {{l1_marge:.2f}} €, soit {{l1_taux:.1f}} % du chiffre d'affaires hors taxe. Le code a donné la même valeur : on peut généraliser.

```python hide
l1 = x.iloc[0]
NUM("l1_montant", l1["montant"]); NUM("l1_ca_ht", l1["ca_ht"]); NUM("l1_cout", l1["quantite"] * l1["cout_achat"])
NUM("l1_marge", l1["marge_ht"]); NUM("l1_taux", l1["taux_marge"] * 100)
NUM("n_lignes_x", len(x)); NUM("n_lignes_lig", len(lig))
```

Le contrôle essentiel d'une jointure est visible dans ce que **le code vérifie lui-même** : `validate="m:1"` demande à pandas de s'arrêter si un produit apparaissait deux fois dans la table des produits, ce qui multiplierait les lignes. Ici la jointure est sans histoire : on part de {{n_lignes_lig:,.0f}} lignes et l'on en retrouve {{n_lignes_x:,.0f}}. Passons à ce que la gérante demande vraiment, une vue par catégorie.

```python
par_cat = x.groupby("categorie").agg(ca_ht=("ca_ht", "sum"), marge=("marge_ht", "sum"), taux_moyen_des_lignes=("taux_marge", "mean"))
par_cat["taux_marge"] = par_cat["marge"] / par_cat["ca_ht"]
print(par_cat.round(3).to_string())
```
<!--sortie-->

```python hide
dec = par_cat.loc["Décoration"]
NUM("dec_taux", dec["taux_marge"] * 100); NUM("dec_taux_moyen", dec["taux_moyen_des_lignes"] * 100)
NUM("taux_bien_etre", par_cat.loc["Bien-être", "taux_marge"] * 100); NUM("taux_deco", dec["taux_marge"] * 100)
NUM("taux_global", x["marge_ht"].sum() / x["ca_ht"].sum() * 100)
```

Deux colonnes se ressemblent mais ne disent pas la même chose. Le **taux de marge** d'un groupe est le rapport des **sommes** (la marge totale divisée par le chiffre d'affaires hors taxe total) ; la **moyenne des taux** des lignes donne à une ligne de 5 € le même poids qu'une ligne de 150 €. Pour la décoration, la première vaut {{dec_taux:.1f}} % et la seconde {{dec_taux_moyen:.1f}} %. **Un ratio d'agrégat se calcule toujours à partir des sommes**, jamais en faisant la moyenne de ratios ; c'est la même règle que pour le panier moyen du volume I. Sur l'ensemble des ventes, le taux de marge brute est de {{taux_global:.1f}} %, avec des écarts d'une catégorie à l'autre : de {{taux_bien_etre:.1f}} % pour le bien-être à {{taux_deco:.1f}} % pour la décoration.

> ⚠️ **Piège : la remise grignote la marge.** Une remise de 20 % ne coûte pas 20 % **de marge**, mais 20 % **du prix**, c'est-à-dire une part bien plus grande de la marge. Sur nos données, le taux de marge tombe de {{tm_0:.1f}} % pour les lignes sans remise à {{tm_20:.1f}} % pour celles qui bénéficient de 20 % de remise. Une variable `marge` calculée **avant** remise aurait caché cette érosion.

```python hide
t = x.groupby("remise_pct")["marge_ht"].sum() / x.groupby("remise_pct")["ca_ht"].sum()
NUM("tm_0", t.loc[0] * 100); NUM("tm_20", t.loc[20] * 100)
```

### 2.1.3 Les dates : en extraire des morceaux

Une date contient plusieurs informations utiles que l'on ne peut pas exploiter tant qu'elles ne sont pas **séparées** : l'année, le trimestre, le mois, la semaine, le jour de la semaine, le week-end. On les extrait avec l'accesseur `.dt`, après avoir **vérifié que la colonne est bien une date** (et non du texte : volume I, section 4.1.3).

```python
cmd = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
d = cmd["date_commande"].dt
cmd["annee"], cmd["trimestre"], cmd["mois"] = d.year, d.quarter, d.month
cmd["semaine_iso"], cmd["jour_semaine"] = d.isocalendar().week, d.dayofweek + 1
cmd["week_end"] = d.dayofweek >= 5
cols = ["id_commande", "date_commande", "annee", "trimestre", "semaine_iso", "jour_semaine", "week_end"]
print(cmd[cols].head(4).to_string(index=False))
```
<!--sortie-->

Regardez la première ligne du tableau ci-dessus : le 1er janvier 2023 est rangé dans la **semaine 52**, alors que l'année civile affiche 2023 (c'est la semaine 52 de l'année ISO 2022). Deux conventions méritent d'être **écrites** : `dayofweek` numérote les jours de 0 (lundi) à 6 (dimanche), d'où le `+ 1` pour obtenir 1 à 7 ; et la **semaine ISO** commence le lundi, la semaine 1 étant celle qui contient le premier jeudi de l'année. Cette dernière règle crée un piège redoutable : **les derniers jours de décembre peuvent appartenir à la semaine 1 de l'année suivante**. Le 29 décembre 2025 est un lundi ; il est dans la semaine {{iso_sem:.0f}} de l'année **{{iso_an:.0f}}**.

```python
jour = pd.Timestamp("2025-12-29")
print(jour.year, jour.isocalendar().year, jour.isocalendar().week)
```
<!--sortie-->

```python hide
j = pd.Timestamp("2025-12-29").isocalendar()
NUM("iso_an", j.year); NUM("iso_sem", j.week)
NUM("n_cmd_an_iso_diff", (d.isocalendar().year != d.year).sum()); NUM("n_cmd", len(cmd))
```

Sur nos {{n_cmd:,.0f}} commandes, {{n_cmd_an_iso_diff:,.0f}} ont une année ISO différente de leur année civile. Un tableau « chiffre d'affaires par année et par semaine » construit avec `semaine_iso` et `annee` mettrait donc les derniers jours de décembre dans la semaine 1 de **l'année précédente** si l'on n'y prend garde. **Règle** : quand on parle de semaines, on garde **l'année ISO avec la semaine ISO** (`isocalendar().year`), jamais l'année civile.

Les morceaux de date servent ensuite à regrouper. Voici le chiffre d'affaires par jour de la semaine : il suffit de relier les lignes à leur date, puis de regrouper.

```python
x = x.merge(cmd[["id_commande", "date_commande", "id_client", "canal", "jour_semaine"]], on="id_commande", validate="m:1")
ca_jour = x.groupby("jour_semaine")["montant"].sum().round(0)
print(ca_jour.to_string())
```
<!--sortie-->

```python hide
NUM("ca_samedi", ca_jour.loc[6] / 1000); NUM("ca_dimanche", ca_jour.loc[7] / 1000); NUM("ca_mardi", ca_jour.loc[2] / 1000)
NUM("rapport_sam_dim", ca_jour.loc[6] / ca_jour.loc[7])
```

Le samedi (jour 6) est le jour le plus fort ({{ca_samedi:,.0f}} k€ sur trois ans) et le dimanche (jour 7) le plus faible ({{ca_dimanche:,.0f}} k€) : un rapport de {{rapport_sam_dim:.1f}} entre les deux. Ce motif de semaine, invisible dans la colonne de dates, apparaît dès que l'on a dérivé le jour.

On obtient les mêmes morceaux de date en **SQL**, ce qui est utile quand les données restent dans une base. Voici le comptage des commandes par jour de la semaine avec **DuckDB**, un moteur SQL qui lit directement les fichiers CSV et qui parle un dialecte très proche de PostgreSQL ; on vérifie ensuite qu'il donne le même résultat que pandas.

```python
import duckdb
q = "select date_part('isodow', date_commande) as jour, count(*) as n from 'donnees/commandes.csv' group by 1 order by 1"
n_sql = duckdb.sql(q).df().set_index("jour")["n"]
n_pd = cmd["jour_semaine"].value_counts().sort_index()
print("même résultat que pandas :", (n_sql.values == n_pd.values).all())
```
<!--sortie-->

### 2.1.4 Les classes : découper une variable continue

Un montant de panier est une variable **continue** : il en existe des milliers de valeurs différentes. Pour un tableau de bord, une segmentation commerciale ou un tableau croisé, on le découpe en **classes** (volume I, section 5.1). Deux outils, deux philosophies :

- **`pd.cut`** découpe selon des **bornes que l'on choisit** (0, 50, 100, 200…) : les classes ont un sens **métier** (« petit panier », « gros panier »), mais des effectifs inégaux ;
- **`pd.qcut`** découpe selon des **quantiles** : chaque classe contient autant de lignes (dix déciles de {{taille_decile:,.0f}} commandes environ), mais les bornes sont des nombres peu parlants.

```python
paniers = x.groupby("id_commande", as_index=False).agg(panier=("montant", "sum"), id_client=("id_client", "first"), date=("date_commande", "first"))
bornes = [0, 50, 100, 200, np.inf]
paniers["classe"] = pd.cut(paniers["panier"], bornes, right=False, labels=["< 50", "50 à 100", "100 à 200", "200 et +"])
paniers["decile"] = pd.qcut(paniers["panier"], 10, labels=False) + 1
print(paniers["classe"].value_counts().sort_index().to_string())
print(paniers.groupby("decile")["panier"].agg(["min", "max"]).round(0).head(3).to_string())
```
<!--sortie-->

```python hide
NUM("taille_decile", len(paniers) / 10)
vc = paniers["classe"].value_counts().sort_index()
NUM("n_moins50", vc.iloc[0]); NUM("n_200plus", vc.iloc[3]); NUM("part_200plus", vc.iloc[3] / len(paniers) * 100)
NUM("borne_d1", paniers["panier"].quantile(0.1)); NUM("borne_d5", paniers["panier"].quantile(0.5))
```

Le paramètre `right=False` mérite attention : il rend chaque classe **fermée à gauche et ouverte à droite** (`[50 ; 100[`). Sans lui, un panier de **exactement** 100 € irait dans la classe « 50 à 100 » ; avec lui, dans « 100 à 200 ». Les deux conventions sont défendables ; l'important est **d'en choisir une et de l'écrire**, sinon deux tableaux du même fichier ne tombent pas d'accord pour quelques lignes. Les classes obtenues donnent {{n_moins50:,.0f}} paniers de moins de 50 € et {{n_200plus:,.0f}} de 200 € et plus, soit {{part_200plus:.0f}} % des commandes. Quant aux déciles, le premier décile s'arrête à {{borne_d1:.0f}} € et le cinquième à {{borne_d5:.0f}} € : la médiane des paniers.

L'équivalent en SQL s'écrit avec `CASE`, qui évalue les conditions **dans l'ordre** et s'arrête à la première vraie. On vérifie que les deux méthodes classent les paniers de la même façon.

```python
con = duckdb.connect(); con.register("paniers", paniers)
q = "select case when panier < 50 then '< 50' when panier < 100 then '50 à 100' when panier < 200 then '100 à 200' else '200 et +' end as classe, count(*) as n from paniers group by 1"
n_case = con.sql(q).df().set_index("classe")["n"]
print("CASE = cut :", (n_case.reindex(vc.index.astype(str)).values == vc.values).all())
```
<!--sortie-->

> 🧭 **En pratique : choisir les bornes.** Partez de l'usage : si les classes servent à une décision (« remise à partir de 200 € »), les bornes viennent du métier. Si elles servent à comparer des groupes de taille comparable, prenez des quantiles. Dans les deux cas, **gardez la variable continue d'origine** à côté de la classe : on peut toujours reclasser, on ne peut pas « déclasser ».

### 2.1.5 Indicateurs, rangs et variables retardées

Un **indicateur** (ou variable binaire) vaut vrai ou faux : « la commande a eu lieu un week-end », « le panier dépasse 200 € », « la ligne a bénéficié d'une remise ». C'est la variable dérivée la plus simple, et l'une des plus utiles, parce qu'une moyenne d'indicateur **est une proportion** : la moyenne de `week_end` est la part des commandes passées le week-end.

Les variables les plus délicates sont celles qui **regardent une autre ligne** : « le délai depuis la commande précédente du même client », « le rang de la commande dans la vie du client ». Elles demandent deux gestes : **trier** (le « précédent » n'a de sens que dans un ordre) et **regrouper** (le précédent d'une commande est une commande **du même client**). En pandas, `groupby` puis `shift` décale chaque groupe d'une ligne ; `cumcount` numérote les lignes d'un groupe.

```python
paniers = paniers.sort_values(["id_client", "date", "id_commande"]).reset_index(drop=True)
g = paniers.groupby("id_client")
paniers["rang_commande"] = g.cumcount() + 1
paniers["delai_jours"] = (paniers["date"] - g["date"].shift()).dt.days
paniers["dormant_180"] = paniers["delai_jours"] > 180
un = paniers[paniers["id_client"] == 2]
print(un[["id_commande", "date", "panier", "rang_commande", "delai_jours", "dormant_180"]].to_string(index=False))
```
<!--sortie-->

```python hide
NUM("n_clients_cmd", paniers["id_client"].nunique()); NUM("n_delai_nan", paniers["delai_jours"].isna().sum())
NUM("delai_median", paniers["delai_jours"].median()); NUM("part_dormant", paniers["dormant_180"].mean() * 100)
NUM("part_dormant_hors_premiere", (paniers["delai_jours"] > 180).sum() / paniers["delai_jours"].notna().sum() * 100)
NUM("d2_a", un.iloc[1]["delai_jours"]); NUM("d2_b", un.iloc[2]["delai_jours"]); NUM("d2_c", un.iloc[3]["delai_jours"])
```

La première commande du client n°2 a un délai **vide** (`NaN`), et c'est exact : elle n'a pas de précédente. Une erreur fréquente consisterait à remplacer ce vide par zéro, ce qui dirait « ce client a recommandé le jour même ». Sur nos {{n_clients_cmd:,.0f}} clients, {{n_delai_nan:,.0f}} commandes n'ont pas de précédente (une par client), et le délai **médian** entre deux commandes consécutives d'un même client est de {{delai_median:.0f}} jours. L'indicateur `dormant_180` marque les commandes passées plus de six mois après la précédente : {{part_dormant_hors_premiere:.1f}} % des commandes qui **ont** une précédente. Notez que `NaN > 180` vaut `False` : l'indicateur, calculé sur toutes les lignes, dilue cette proportion à {{part_dormant:.1f}} %. **Le choix du dénominateur est une décision** : on documente « sur les commandes qui ont une précédente ».

Le décalage fait aussi apparaître la forme du comportement d'achat. Un client qui revient {{d2_a:.0f}} jours, puis {{d2_b:.0f}} jours, puis {{d2_c:.0f}} jours après sa commande précédente s'éloigne ; la variable `delai_jours`, que la colonne `date` ne contenait pas, le rend **visible** et **mesurable**.

> 🧪 **Expérience : le même délai en SQL.** En SQL, la fonction fenêtre `LAG(date) OVER (PARTITION BY id_client ORDER BY date)` joue le rôle de `groupby` + `shift` (volume I, section 3.3.4). Retenez l'équivalence : `partition by` ↔ `groupby`, `order by` ↔ `sort_values`, `lag` ↔ `shift`.

### 2.1.6 Du texte à la clé

Pour relier deux sources, il faut une **clé** qui s'écrive de la même façon des deux côtés. Or le texte est la matière la moins fiable : la caisse écrit « BOÎTE RUSTIQUE », le catalogue « Boîte rustique », le CRM « boite rustique ». Trois écritures, un seul objet. La première transformation, avant toute jointure sur du texte, est de **normaliser** : tout passer en minuscules, retirer les accents, remplacer la ponctuation par des espaces, compresser les espaces multiples.

```python
import unicodedata, re
def cle_texte(s):
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()
exemples = ["BOÎTE RUSTIQUE", "Boîte rustique", " boite  rustique ", "Boîte-rustique."]
print([cle_texte(e) for e in exemples])
```
<!--sortie-->

```python hide
NUM("n_cles_distinctes", len({cle_texte(e) for e in exemples}))
NUM("n_noms_bruts", prod["nom_produit"].nunique()); NUM("n_produits", len(prod))
NUM("n_noms_cles", prod["nom_produit"].map(cle_texte).nunique())
```

La décomposition en Unicode « NFD » sépare chaque lettre accentuée en une lettre et un **accent combinant** ; on supprime ensuite les accents. Les quatre écritures donnent {{n_cles_distinctes:.0f}} seule clé. Mais attention : **normaliser n'est pas dédoublonner**. Dans notre catalogue de {{n_produits:.0f}} produits, il n'y a que {{n_noms_bruts:.0f}} noms distincts, et la normalisation n'en retire aucun ({{n_noms_cles:.0f}} clés) : **chaque nom est porté par deux produits** différents. Une clé de texte rend deux écritures comparables ; elle ne dit pas si deux objets distincts portent le même nom. Cette ambiguïté est l'un des fils de la section suivante.

### 2.1.7 Trois pièges, et comment documenter

**Piège 1 : la division par zéro.** Un ratio dont le dénominateur peut valoir zéro doit prévoir ce cas. En pandas, `x / 0` donne `inf` (l'infini) et `0 / 0` donne `NaN`, sans erreur : un `inf` dans une moyenne la rend infinie, et personne n'est prévenu. Calculons le panier moyen par client sur 2025. Les clients qui n'ont pas commandé cette année-là n'ont ni chiffre d'affaires ni commande : leur panier moyen n'est **pas défini**.

```python
x25 = x[x["date_commande"].dt.year == 2025]
cl = pd.read_csv("donnees/clients.csv")[["id_client"]]
cl = cl.merge(x25.groupby("id_client").agg(ca=("montant", "sum"), nb=("id_commande", "nunique")), on="id_client", how="left")
cl["panier_moyen"] = cl["ca"] / cl["nb"]
print("clients sans commande en 2025 :", int(cl["nb"].isna().sum()), "| paniers moyens indéfinis :", int(cl["panier_moyen"].isna().sum()))
print("moyenne des paniers moyens (acheteurs) :", round(cl["panier_moyen"].mean(), 2), "| avec des zéros :", round(cl["panier_moyen"].fillna(0).mean(), 2))
```
<!--sortie-->

```python hide
NUM("n_sans_cmd", cl["nb"].isna().sum()); NUM("pm_acheteurs", cl["panier_moyen"].mean()); NUM("pm_zeros", cl["panier_moyen"].fillna(0).mean())
NUM("n_clients_total", len(cl))
```

Sur {{n_clients_total:,.0f}} clients, {{n_sans_cmd:,.0f}} n'ont rien acheté en 2025. Les laisser en `NaN` donne un panier moyen de **{{pm_acheteurs:.2f}} €** (celui des acheteurs) ; les remplacer par zéro l'écrase à {{pm_zeros:.2f}} €. Aucun des deux calculs n'est « faux » : ils répondent à deux questions différentes. Ce qui serait faux serait de **ne pas savoir lequel on a fait**.

**Piège 2 : la valeur manquante qui se propage.** Une opération arithmétique avec un `NaN` donne un `NaN`. Si l'on calcule le chiffre d'affaires total d'un client en **additionnant** ses chiffres par canal, tous ceux qui n'ont pas acheté dans l'un des trois canaux ont un total vide.

```python
par_canal = x25.pivot_table(index="id_client", columns="canal", values="montant", aggfunc="sum")
mauvais = par_canal["Boutique"] + par_canal["Site"] + par_canal["Réseaux"]
bon = par_canal.sum(axis=1)
print("totaux vides avec + :", int(mauvais.isna().sum()), "sur", len(par_canal), "| avec sum(axis=1) :", int(bon.isna().sum()))
```
<!--sortie-->

```python hide
NUM("tot_vides_plus", mauvais.isna().sum()); NUM("n_acheteurs", len(par_canal)); NUM("part_vides_plus", mauvais.isna().mean() * 100)
```

Avec l'opérateur `+`, {{tot_vides_plus:,.0f}} totaux sur {{n_acheteurs:,.0f}} (soit {{part_vides_plus:.0f}} %) sont perdus, alors qu'`axis=1` avec `sum` **ignore** les vides. Retenez la règle : **`sum` ignore les manquants, `+` les propage**. L'une n'est pas meilleure que l'autre, mais il faut choisir en connaissance de cause.

**Piège 3 : la fuite d'information.** Une variable dérivée **fuit** quand elle utilise une information qui n'était pas connue à la date où l'on veut s'en servir. Imaginons que la gérante veuille repérer, au 30 juin 2025, les clients qui commanderont encore au second semestre. Parmi les clients qui avaient déjà commandé, nous calculons deux versions de « nombre de commandes » : l'une **avant** le 30 juin, l'autre **au total**, futur compris.

```python
coupure = pd.Timestamp("2025-06-30")
avant = paniers[paniers["date"] <= coupure].groupby("id_client").size().rename("avant")
total = paniers.groupby("id_client").size().rename("total")
cible = paniers[(paniers["date"] > coupure) & (paniers["date"].dt.year == 2025)].groupby("id_client").size().rename("s2")
t = pd.concat([avant, total, cible], axis=1).dropna(subset=["avant"]).fillna(0)
from sklearn.metrics import roc_auc_score
y = (t["s2"] > 0).astype(int)
print("AUC avec 'avant' :", round(roc_auc_score(y, t["avant"]), 3), "| avec 'total' :", round(roc_auc_score(y, t["total"]), 3))
```
<!--sortie-->

```python hide
NUM("auc_avant", roc_auc_score(y, t["avant"])); NUM("auc_total", roc_auc_score(y, t["total"])); NUM("n_t", len(t)); NUM("part_y", y.mean() * 100)
```

Sur {{n_t:,.0f}} clients ayant déjà commandé au 30 juin, {{part_y:.0f}} % commandent au second semestre. La variable honnête (`avant`) a un pouvoir de classement modeste (une AUC de {{auc_avant:.2f}} : 0,5 correspondrait au hasard, 1 à un classement parfait), alors que la version qui regarde le futur (`total`, qui **contient** les commandes du second semestre) paraît bien meilleure : {{auc_total:.2f}}. Cette différence n'a aucune valeur : c'est la **cible** qui se glisse dans la prédiction. Règle : **toute variable qui sert à prévoir doit être calculée avec les seules données antérieures à la date de prévision**. Quand on dérive une variable, on se demande donc : « *à quelle date aurais-je pu la calculer ?* ». (Le volume III revient en détail sur la fuite d'information et l'évaluation des modèles.)

**Documenter chaque variable créée.** Une variable dérivée sans définition est une dette. Une **fiche** de quelques lignes suffit ; le chapitre 4 de ce volume en fait un dictionnaire de données complet.

| Champ | Exemple pour `marge_ht` |
|---|---|
| Nom | `marge_ht` |
| Définition | chiffre d'affaires hors taxe de la ligne moins quantité × coût d'achat |
| Unité | euros |
| Formule | `montant / 1,20 − quantite × cout_achat` |
| Hypothèses | TVA de 20 % (fictive) ; coût d'achat actuel du catalogue, sans frais de transport |
| Cas particuliers | un produit sans coût d'achat donne une marge vide (jamais zéro) |
| Auteur, date | l'analyste, date de création |

> ✅ **À retenir.**
> - Une variable dérivée est une **décision de définition** : unité, base de calcul, cas limites. On l'**écrit**.
> - Un **ratio d'agrégat** se calcule à partir des **sommes**, jamais en faisant la moyenne de ratios.
> - Pour les dates : on extrait année, trimestre, mois, jour ; on garde **l'année ISO avec la semaine ISO**.
> - Les classes se choisissent (`cut`, bornes du métier) ou se calculent (`qcut`, quantiles) ; on **écrit la convention des bornes** et l'on garde la variable d'origine.
> - Un délai ou un rang demande de **trier** puis de **regrouper** ; le vide d'un premier délai n'est **pas** un zéro.
> - Trois pièges : la division par zéro, le `NaN` qui se propage (`sum` ≠ `+`), la **fuite d'information**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 et 2.2, exercices 2.1 à 2.4.
