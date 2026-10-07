## 2.3 Agrégation et restructuration

La table des ventes compte plus de vingt-six mille lignes, et la gérante n'en lira aucune. Ce qu'elle veut, ce sont des chiffres **à un autre niveau de détail** : par mois, par canal, par catégorie, par client. **Agréger**, c'est passer d'un niveau fin à un niveau plus grossier en **résumant** : sommer, compter, moyenner. C'est le geste le plus fréquent de l'analyste, et celui qui cache le plus de pièges, parce que **chaque niveau de détail a sa propre définition du « nombre de… »**. Cette section apprend à raisonner sur le **grain** d'une table, à agréger sans compter deux fois, à calculer des parts, des rangs et des cumuls, à organiser les tables en **faits et dimensions**, et à vérifier par une **somme de contrôle** que rien n'a bougé.

### 2.3.1 Le grain d'une table et le changement de grain

Le **grain** d'une table est ce que représente **une ligne**. Dans notre table des ventes, une ligne est une **ligne de vente** (un article, dans une commande). Une commande compte plusieurs lignes ; un client passe plusieurs commandes. Trois niveaux, donc trois grains :

| Grain | Une ligne représente… | Exemple de colonnes | Nombre de lignes en 2025 (sources du chapitre) |
|---|---|---|---|
| **ligne** | un article vendu | produit, quantité, montant | 26 188 (caisse et site) |
| **commande** | un panier | date, canal, montant total, nombre d'articles | 11 339 |
| **client** | une personne | nombre de commandes, chiffre d'affaires, dernière date | 3 875 clients acheteurs (base) |

Passer d'un grain fin à un grain grossier est **l'agrégation** ; passer dans l'autre sens est impossible (on ne retrouve pas les lignes à partir des totaux). Il faut donc **garder la table la plus fine** et fabriquer les autres, jamais l'inverse. Et à chaque changement de grain, les mêmes mots ne désignent plus les mêmes choses : « nombre de commandes » est un **comptage de lignes distinctes** au grain ligne, et un simple **comptage de lignes** au grain commande.

```python hide
ventes["mois"] = ventes["date"].dt.strftime("%Y-%m")
cmd_b = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
v25 = lig.merge(cmd_b[["id_commande", "id_client", "date_commande", "canal"]], on="id_commande", validate="m:1")
v25 = v25[v25["date_commande"].dt.year == 2025].copy()
NUM("n_ventes_g", len(ventes)); NUM("n_cmd_g", ventes["id_commande"].nunique()); NUM("n_cli_g", v25["id_client"].nunique())
```
<!--sortie-->
```text
NUM n_ventes_g 26188
NUM n_cmd_g 11339
NUM n_cli_g 3875
```

Une remarque honnête : la table `ventes` (caisse et site) **ne contient pas le client**. La caisse n'enregistre pas qui achète, et le site fournit une adresse électronique que l'on peut relier au CRM, mais pas avec certitude (section 2.5). Pour le niveau « client », nous repartirons donc de la **base** du volume I, qui porte `id_client` sur chaque commande. C'est un exemple de la règle : **on ne peut agréger que selon ce que la table contient**.

### 2.3.2 `groupby` et `agg` : compter sans compter deux fois

L'outil est `groupby` suivi de `agg`, avec des **agrégats nommés** : `nom_de_la_colonne_résultat=("colonne_source", "fonction")`. Voici, par canal et par mois, le chiffre d'affaires, le nombre de lignes, le nombre de **commandes distinctes**, le panier moyen et le taux de marge.

```python
par_mois = ventes.groupby(["canal", "mois"]).agg(ca=("montant", "sum"), lignes=("montant", "size"),
                                                commandes=("id_commande", "nunique"), marge=("marge_ht", "sum"))
par_mois["panier_moyen"] = par_mois["ca"] / par_mois["commandes"]
par_mois["taux_marge"] = par_mois["marge"] / (par_mois["ca"] / 1.20)
print(par_mois.loc["Site"].tail(3).round(2).to_string())
```
<!--sortie-->
```text
               ca  lignes  commandes     marge  panier_moyen  taux_marge
mois                                                                    
2025-10  54999.72    1214        514  17848.28        107.00        0.39
2025-11  62884.28    1552        693  19364.05         90.74        0.37
2025-12  87496.07    1995        882  28616.09         99.20        0.39
```
<!--sortie-->

```python hide
dec_s = par_mois.loc[("Site", "2025-12")]
NUM("ca_site_dec", dec_s["ca"]); NUM("cmd_site_dec", dec_s["commandes"]); NUM("lignes_site_dec", dec_s["lignes"]); NUM("pm_site_dec", dec_s["panier_moyen"]); NUM("tm_site_dec", dec_s["taux_marge"] * 100)
NUM("ca_site_oct", par_mois.loc[("Site", "2025-10"), "ca"]); NUM("pm_site_nov", par_mois.loc[("Site", "2025-11"), "panier_moyen"])
```
<!--sortie-->
```text
NUM ca_site_dec 87496.06999999999
NUM cmd_site_dec 882.0
NUM lignes_site_dec 1995.0
NUM pm_site_dec 99.20189342403627
NUM tm_site_dec 39.24668845126416
NUM ca_site_oct 54999.72
NUM pm_site_nov 90.74210678210677
```

Trois définitions à ne pas confondre. Le **nombre de lignes** (`size`) est un comptage d'articles : 1 995 en décembre pour le site. Le **nombre de commandes** (`nunique` sur `id_commande`) est un comptage de paniers : 882. Le **panier moyen** est le **chiffre d'affaires divisé par le nombre de commandes** (87 496 € / 882 = 99,20 €), et **non** le montant moyen d'une ligne, qui serait environ deux fois plus petit. Le taux de marge de décembre (39,2 %) est, comme en 2.1.2, un rapport de sommes.

Il y a pourtant un piège plus subtil que le choix de la fonction : certains comptages **ne s'additionnent pas**. Une commande appartient à **un seul** mois, donc le nombre de commandes distinctes d'une année est bien la somme des nombres mensuels. Un client, lui, peut acheter plusieurs mois. Comparons, avec la base, la somme des clients distincts mois par mois et le nombre de clients distincts de l'année.

```python
v25["mois"] = v25["date_commande"].dt.month
mensuel = v25.groupby("mois")["id_client"].nunique()
print("somme des clients distincts de chaque mois :", int(mensuel.sum()))
print("clients distincts de l'année :", v25["id_client"].nunique())
print("somme des commandes distinctes par mois :", int(v25.groupby("mois")["id_commande"].nunique().sum()), "| commandes distinctes de l'année :", v25["id_commande"].nunique())
```
<!--sortie-->
```text
somme des clients distincts de chaque mois : 10621
clients distincts de l'année : 3875
somme des commandes distinctes par mois : 12946 | commandes distinctes de l'année : 12946
```
<!--sortie-->

```python hide
NUM("cli_somme_mois", mensuel.sum()); NUM("cli_annee", v25["id_client"].nunique()); NUM("cli_ratio", mensuel.sum() / v25["id_client"].nunique())
```
<!--sortie-->
```text
NUM cli_somme_mois 10621
NUM cli_annee 3875
NUM cli_ratio 2.7409032258064516
```

La somme des clients mensuels (10 621) est **2,7 fois** le nombre réel de clients (3 875) : les clients qui reviennent sont comptés autant de fois qu'ils achètent de mois différents. **Un comptage distinct n'est additif que si les groupes ne se recouvrent pas.** Règle pratique : un total « tous mois » d'un nombre de clients se recalcule **sur les données**, il ne se déduit **jamais** d'une colonne de totaux mensuels.

> ⚠️ **Piège : additionner des moyennes, des taux, des comptages distincts.** Les **sommes** s'additionnent ; les **moyennes**, les **ratios** et les **comptages distincts** non. Pour recomposer un niveau supérieur à partir d'un niveau inférieur, on garde les **composantes** (somme et effectif, numérateur et dénominateur) et l'on refait le ratio.

### 2.3.3 `transform` : un agrégat sans perdre les lignes

`agg` **réduit** : une ligne par groupe. `transform` calcule le même agrégat, mais le **recopie sur chaque ligne** du groupe : le nombre de lignes ne change pas. C'est l'outil de tout ce qui compare une ligne à son groupe : une **part du total**, un **écart à la moyenne**, un **rang**.

```python
n_avant = len(ventes)
ventes["ca_mois"] = ventes.groupby("mois")["montant"].transform("sum")
ventes["part_du_mois"] = ventes["montant"] / ventes["ca_mois"]
ventes["rang_dans_categorie"] = ventes.groupby("categorie")["montant"].rank(method="dense", ascending=False)
t = ventes.groupby(["mois", "canal"])["part_du_mois"].sum().unstack()
print(t.tail(3).round(3).to_string())
print("lignes avant / après transform :", n_avant, len(ventes))
```
<!--sortie-->
```text
canal    Boutique   Site
mois                    
2025-10     0.483  0.517
2025-11     0.492  0.508
2025-12     0.457  0.543
lignes avant / après transform : 26188 26188
```
<!--sortie-->

```python hide
NUM("part_site_dec", t.loc["2025-12", "Site"] * 100); NUM("part_bout_dec", t.loc["2025-12", "Boutique"] * 100)
NUM("somme_parts_dec", t.loc["2025-12"].sum()); NUM("n_rang1", (ventes["rang_dans_categorie"] == 1).sum())
```
<!--sortie-->
```text
NUM part_site_dec 54.28320553562186
NUM part_bout_dec 45.71679446437813
NUM somme_parts_dec 0.9999999999999999
NUM n_rang1 17
```

Chaque ligne porte désormais la part qu'elle représente dans son mois ; en les resommant par canal, on retrouve la part de chacun : en décembre, la Boutique pèse 45,7 % et le Site 54,3 % du chiffre d'affaires des deux sources (la somme des parts fait 1, ce qui est **un contrôle**). La dernière ligne affichée montre, avant et après, que `transform` **conserve toutes les lignes**, contrairement à `agg`.

Le **rang** (`rank`) réclame une décision de présentation : `method="dense"` donne 1, 2, 2, 3 en cas d'égalité (pas de « trou »), alors que `method="min"` donnerait 1, 2, 2, 4. On choisit selon l'usage et l'on **l'écrit**.

### 2.3.4 Du grain ligne au grain commande, puis au grain client

Fabriquer la table des commandes, puis celle des clients, se fait par deux agrégations successives. Chaque ligne de la table des clients **résume** ce que le client a fait : combien de commandes, quel chiffre d'affaires, quand pour la dernière fois (la **récence**), dans quel canal il achète le plus souvent.

```python
fin = pd.Timestamp("2025-12-31")
clients_2025 = v25.groupby("id_client").agg(nb_commandes=("id_commande", "nunique"), ca=("montant", "sum"),
                                            premiere=("date_commande", "min"), derniere=("date_commande", "max"))
clients_2025["recence_jours"] = (fin - clients_2025["derniere"]).dt.days
clients_2025["canal_principal"] = v25.groupby("id_client")["canal"].agg(lambda s: s.mode().iloc[0])
print(clients_2025.describe().loc[["mean", "50%", "max"], ["nb_commandes", "ca", "recence_jours"]].round(1).to_string())
```
<!--sortie-->
```text
      nb_commandes      ca  recence_jours
mean           3.3   341.9           91.5
50%            2.0   233.2           53.0
max           25.0  3382.3          364.0
```
<!--sortie-->

```python hide
NUM("nb_cmd_moy", clients_2025["nb_commandes"].mean()); NUM("nb_cmd_med", clients_2025["nb_commandes"].median()); NUM("nb_cmd_max", clients_2025["nb_commandes"].max())
NUM("ca_cli_med", clients_2025["ca"].median()); NUM("rec_med", clients_2025["recence_jours"].median())
NUM("part_unique", (clients_2025["nb_commandes"] == 1).mean() * 100)
cp = clients_2025["canal_principal"].value_counts(); NUM("cp_boutique", cp["Boutique"]); NUM("cp_site", cp["Site"]); NUM("cp_reseaux", cp["Réseaux"])
```
<!--sortie-->
```text
NUM nb_cmd_moy 3.3409032258064517
NUM nb_cmd_med 2.0
NUM nb_cmd_max 25
NUM ca_cli_med 233.21
NUM rec_med 53.0
NUM part_unique 31.509677419354837
NUM cp_boutique 1793
NUM cp_site 1756
NUM cp_reseaux 326
```

La moyenne du nombre de commandes (3,3) est supérieure à la médiane (2) : quelques gros clients (jusqu'à 25 commandes) tirent la moyenne, et 32 % des clients n'ont acheté **qu'une fois** en 2025. Le client médian a dépensé 233 € et sa dernière commande date de 53 jours : tout ce qu'une **segmentation** de clientèle (volume III de cette série) saura exploiter.

Chaque changement de grain se **contrôle**. Les trois tables doivent porter le **même chiffre d'affaires** et le **même nombre de commandes**.

```python
v25_cmd = v25.groupby("id_commande", as_index=False).agg(ca=("montant", "sum"), id_client=("id_client", "first"))
print("CA des lignes :", round(v25["montant"].sum(), 2), "| des commandes :", round(v25_cmd["ca"].sum(), 2), "| des clients :", round(clients_2025["ca"].sum(), 2))
print("commandes :", v25["id_commande"].nunique(), "=", len(v25_cmd), "=", int(clients_2025["nb_commandes"].sum()))
```
<!--sortie-->
```text
CA des lignes : 1324763.72 | des commandes : 1324763.72 | des clients : 1324763.72
commandes : 12946 = 12946 = 12946
```
<!--sortie-->

Un dernier point : la table des clients ne contient que les **acheteurs de 2025**. Si l'on veut parler **de tous** les clients (par exemple « quelle part est inactive ? »), il faut partir de la table complète des clients et faire une jointure **à gauche** : les clients sans achat auront des vides, qu'il faudra **remplacer par zéro pour les compteurs** (nombre de commandes, chiffre d'affaires), mais **pas** pour la récence (un client qui n'a jamais acheté n'a pas une récence de zéro jour). Cela rejoint le piège de 2.1.7 : le sens d'un vide dépend de la colonne.

### 2.3.5 Table de faits et dimensions

Une organisation des tables, très répandue en analyse, évite de tout recopier partout : le **schéma en étoile**. Au centre, une **table de faits** : ce qui se produit et se mesure (une ligne de vente, avec ses montants et ses quantités). Autour, des **dimensions** : les « axes » selon lesquels on regarde les faits (le produit, la date, le canal, le client). Chaque fait porte, pour chaque dimension, une **clé** qui renvoie à une ligne de la dimension.

```python hide
fig, ax = plt.subplots(figsize=(7.4, 3.8)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 50)
def bte(x, y, w, h, titre, lignes, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc="white", ec=c, lw=1.8))
    ax.text(x + w / 2, y + h - 2.8, titre, ha="center", va="center", fontsize=9, weight="bold", color=c)
    ax.text(x + w / 2, y + (h - 5.5) / 2, "\n".join(lignes), ha="center", va="center", fontsize=7.5)
bte(36, 14, 28, 22, "FAITS : ventes", ["id_commande", "date  →  dim_date", "id_produit  →  dim_produit", "canal  →  dim_canal", "quantité, montant, marge"], BLEU)
bte(2, 32, 24, 14, "dim_date", ["jour, mois, trimestre", "semaine ISO, week-end"], AQUA)
bte(74, 32, 24, 14, "dim_produit", ["nom, catégorie", "prix, coût d'achat"], ORANGE)
bte(2, 3, 24, 12, "dim_canal", ["Boutique, Site, Réseaux"], VIOLET)
bte(74, 3, 24, 12, "dim_client", ["ville, âge, fidélité", "(non reliée à la caisse)"], MUET)
for (x1, y1, x2, y2) in [(26.5, 39, 36, 31), (73.5, 39, 64, 31), (26.5, 9, 36, 19), (73.5, 9, 64, 19)]:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="<-", color=MUET, lw=1.3))
save(fig, "ch02-etoile.png")
```
<!--sortie-->
```text
figure : ch02-etoile.png
```

![Schéma en étoile : une table de faits (les lignes de vente) entourée de dimensions (date, produit, canal, client), reliées par des clés.](figures/ch02-etoile.png)

Pourquoi cette organisation ? Parce qu'elle **sépare ce qui change souvent** (les ventes, qui s'ajoutent chaque jour) de **ce qui change rarement** (le catalogue, le calendrier), et parce qu'elle règle la question du grain : la table de faits a **un** grain, les dimensions ont **le leur**. Une jointure entre faits et dimension est par construction **n–1** : la clé de la dimension est unique, donc le nombre de lignes de faits ne change pas, et l'on peut le **vérifier**. Voici la dimension de date de 2025, un calendrier avec une ligne par jour, joint à la table de faits.

```python
dim_date = pd.DataFrame({"date": pd.date_range("2025-01-01", "2025-12-31")})
dim_date["trimestre"] = dim_date["date"].dt.quarter
dim_date["semaine_iso"] = dim_date["date"].dt.isocalendar().week
dim_date["week_end"] = dim_date["date"].dt.dayofweek >= 5
f = ventes.merge(dim_date, on="date", how="left", validate="m:1")
print("lignes avant / après :", len(ventes), len(f), "| dates sans correspondance :", int(f["trimestre"].isna().sum()))
print(f.groupby("trimestre")["montant"].sum().round(0).to_dict())
```
<!--sortie-->
```text
lignes avant / après : 26188 26188 | dates sans correspondance : 0
{1: 225285.0, 2: 273107.0, 3: 274942.0, 4: 391302.0}
```
<!--sortie-->

```python hide
NUM("n_dates_sans", f["trimestre"].isna().sum()); NUM("n_jours", len(dim_date))
NUM("ca_t4", f.groupby("trimestre")["montant"].sum().loc[4]); NUM("ca_t1", f.groupby("trimestre")["montant"].sum().loc[1])
NUM("jours_vente_boutique", ventes.loc[ventes["canal"] == "Boutique", "date"].nunique()); NUM("jours_vente_site", ventes.loc[ventes["canal"] == "Site", "date"].nunique())
```
<!--sortie-->
```text
NUM n_dates_sans 0
NUM n_jours 365
NUM ca_t4 391302.06
NUM ca_t1 225285.38
NUM jours_vente_boutique 365
NUM jours_vente_site 365
```

La jointure conserve les 26 188 lignes, sans date orpheline : le trimestre est ajouté à chaque ligne en un seul geste (le quatrième trimestre pèse 391 302 € contre 225 285 € pour le premier). Le **calendrier** offre autre chose : il liste **tous** les jours, y compris ceux où rien ne s'est vendu. Ici la Boutique a des ventes sur 365 jours sur 365, et le Site sur 365 : aucune journée creuse. Mais dans une série où un jour manquerait, c'est **la dimension de date qui le ferait voir**, alors qu'un `groupby` sur la table de faits ne produirait simplement **pas de ligne** pour ce jour (et un graphique le raccorderait sans rien dire).

> 💡 **Intuition.** Une table de faits répond à « *combien ?* », une dimension à « *selon quoi ?* ». Quand une question commence par « par… » (par mois, par catégorie, par canal), elle désigne une dimension.

### 2.3.6 Cumuls, moyennes mobiles et comparaisons dans le temps

Une série quotidienne est bruitée (les samedis sont forts, les dimanches faibles) ; deux outils la lissent ou la **cumulent**. Le **cumul** (`cumsum`) donne le chiffre d'affaires depuis le début de l'année, utile pour comparer à un objectif. La **moyenne mobile** (`rolling`) remplace chaque jour par la moyenne des sept derniers jours : une fenêtre de **sept** jours contient exactement un exemplaire de chaque jour de la semaine, ce qui efface l'effet de la semaine.

```python
jour = ventes.groupby(["canal", "date"])["montant"].sum().unstack("canal").fillna(0)
jour["total"] = jour.sum(axis=1)
jour["cumul"] = jour["total"].cumsum()
jour["moy7"] = jour["total"].rolling(7, min_periods=7).mean()
print(jour[["total", "cumul", "moy7"]].iloc[[0, 6, 7, -1]].round(0).to_string())
```
<!--sortie-->
```text
canal        total      cumul    moy7
date                                 
2025-01-01  2086.0     2086.0     NaN
2025-01-07  1969.0    17511.0  2502.0
2025-01-08  2552.0    20063.0  2568.0
2025-12-31  2838.0  1164637.0  4778.0
```
<!--sortie-->

```python hide
NUM("cumul_fin", jour["cumul"].iloc[-1]); NUM("moy7_juin", jour.loc["2025-06-15", "moy7"]); NUM("moy7_dec", jour.loc["2025-12-15", "moy7"])
NUM("moy7_vide", jour["moy7"].isna().sum()); NUM("jour_max", jour["total"].max()); NUM("moy7_max", jour["moy7"].max())
q = "select date, sum(sum(montant)) over (order by date) as cumul from (select date, montant from read_csv_auto('" + os.path.join(TMP2, "ventes.csv") + "')) group by date order by date"
cum_sql = duckdb.sql(q).df()
assert np.allclose(cum_sql["cumul"].values, jour["cumul"].values)
```
<!--sortie-->
```text
NUM cumul_fin 1164636.7200000002
NUM moy7_juin 3207.712857142857
NUM moy7_dec 4860.071428571428
NUM moy7_vide 6
NUM jour_max 9268.52
NUM moy7_max 5860.795714285715
```

Le chiffre d'affaires cumulé atteint 1 164 637 € au 31 décembre (c'est exactement la somme de la table : un cumul **se termine par le total**, autre contrôle). La moyenne mobile ne commence qu'au septième jour : les six premières valeurs sont **vides** (6 jours), parce que `min_periods=7` refuse de calculer sur une fenêtre incomplète ; on préfère un vide à une valeur trompeuse. Elle vaut 3 208 € par jour à la mi-juin et 4 860 € à la mi-décembre. Le même cumul s'écrit en SQL par une **fonction fenêtre** (`sum(...) over (order by date)`, volume I, section 3.3.5) ; calculé avec DuckDB sur le fichier écrit en 2.2.9, il donne la même série.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.0))
ax[0].plot(jour.index, jour["cumul"] / 1000, color=BLEU); ax[0].set_title("Chiffre d'affaires cumulé (k€)", loc="left"); ax[0].tick_params(axis="x", labelsize=7)
ax[1].plot(jour.index, jour["total"] / 1000, color=MUET, lw=0.8, label="par jour"); ax[1].plot(jour.index, jour["moy7"] / 1000, color=ORANGE, label="moyenne sur 7 jours")
ax[1].set_title("CA quotidien (k€)", loc="left"); ax[1].legend(fontsize=7); ax[1].tick_params(axis="x", labelsize=7)
save(fig, "ch02-cumul.png")
```
<!--sortie-->
```text
figure : ch02-cumul.png
```

![À gauche, chiffre d'affaires cumulé de 2025 (caisse et site) ; à droite, chiffre d'affaires quotidien et sa moyenne mobile sur sept jours, qui efface l'effet du jour de la semaine.](figures/ch02-cumul.png)

### 2.3.7 La somme de contrôle : rien n'a bougé

Agréger, c'est résumer, donc **perdre** du détail ; mais il ne faut perdre **ni argent ni lignes**. Un jeu de **contrôles d'invariants** vérifie que les quantités qui doivent se conserver se conservent : le chiffre d'affaires est le même à tous les niveaux (ligne, mois, canal, commande), le nombre de commandes aussi, et les cumuls finissent sur le total. On en fait une petite fonction, que l'on **relance à chaque modification** de la chaîne.

```python
def controles(table):
    total = table["montant"].sum()
    return {"CA par canal = CA total": np.isclose(table.groupby("canal")["montant"].sum().sum(), total),
            "CA par mois = CA total": np.isclose(table.groupby("mois")["montant"].sum().sum(), total),
            "CA par commande = CA total": np.isclose(table.groupby(["canal", "id_commande"])["montant"].sum().sum(), total),
            "aucun montant vide": table["montant"].notna().all(),
            "aucune commande sans date": table["date"].notna().all()}
print(pd.Series(controles(ventes)).to_string())
```
<!--sortie-->
```text
CA par canal = CA total       True
CA par mois = CA total        True
CA par commande = CA total    True
aucun montant vide            True
aucune commande sans date     True
```
<!--sortie-->

Tous les contrôles passent. Leur valeur apparaît quand quelque chose **casse**. Refaisons, volontairement, la faute de 2.2.5 : joindre les ventes aux produits **sur le nom seul**, puis relancer les contrôles sur la table obtenue.

```python
fautive = ventes.merge(prod[["nom_produit", "cout_achat"]], on="nom_produit", suffixes=("", "_cat"))
print("lignes :", len(ventes), "->", len(fautive), "| CA :", round(ventes["montant"].sum()), "->", round(fautive["montant"].sum()))
print("contrôle « CA par canal = CA total » sur la table fautive : ", bool(controles(fautive)["CA par canal = CA total"]))
```
<!--sortie-->
```text
lignes : 26188 -> 52376 | CA : 1164637 -> 2329273
contrôle « CA par canal = CA total » sur la table fautive :  True
```
<!--sortie-->

```python hide
NUM("n_faute", len(fautive)); NUM("ca_faute", fautive["montant"].sum()); NUM("ca_juste", ventes["montant"].sum()); NUM("ratio_faute_ca", fautive["montant"].sum() / ventes["montant"].sum())
assert controles(ventes)["CA par mois = CA total"]
```
<!--sortie-->
```text
NUM n_faute 52376
NUM ca_faute 2329273.4399999995
NUM ca_juste 1164636.72
NUM ratio_faute_ca 1.9999999999999996
```

Les contrôles de **cohérence interne** (ligne, mois, canal) passent même sur la table fautive : ils comparent la table **à elle-même**, et une jointure qui duplique des lignes duplique aussi ses totaux. Ce que la faute change, c'est la **comparaison à l'extérieur** : le chiffre d'affaires est multiplié par 2,0 (2 329 273 € au lieu de 1 164 637 €), ce que révélerait la comparaison avec la base ou avec le total des fichiers de la caisse. **Il faut donc les deux** : des contrôles internes (les invariants entre niveaux de détail) et des contrôles **externes** (un total qui vient d'ailleurs). C'est ce que le chapitre 3 systématise.

> ✅ **À retenir.**
> - Le **grain** dit ce que représente une ligne ; on **garde la table la plus fine** et l'on en dérive les autres, jamais l'inverse.
> - Un **ratio d'agrégat** se refait à partir des **sommes** ; un **comptage distinct** n'est additif que si les groupes ne se recouvrent pas (clients par mois).
> - `agg` réduit, **`transform`** conserve les lignes : parts, écarts à la moyenne, rangs.
> - Une jointure entre faits et dimension est **n–1** par construction : le nombre de lignes de faits ne doit pas changer ; un calendrier fait voir les **jours manquants**.
> - Un cumul se termine par le **total** ; une moyenne mobile a des vides au début (`min_periods`).
> - On contrôle par **invariants internes** (mêmes totaux à chaque niveau) **et** par une comparaison **externe** : les premiers ne voient pas une jointure qui duplique tout.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercices 2.9 à 2.10.
