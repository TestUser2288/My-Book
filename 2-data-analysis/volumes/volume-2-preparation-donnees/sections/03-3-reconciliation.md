## 3.3 Réconciliation de sources

Les contrôles de la section précédente jugent **une** source contre ses propres règles. La **réconciliation** compare **deux** sources qui prétendent décrire la même réalité (les ventes de décembre, la liste des produits) et cherche à **expliquer chaque écart**. C'est le geste du comptable qui rapproche le relevé de banque du journal : on ne s'arrête pas à « les deux totaux sont proches », on s'arrête à « l'écart de 17 551,32 € est exactement ces 181 commandes annulées ».

### 3.3.1 Deux sources, une mesure

Réconcilier suppose de se mettre d'accord sur trois choses.

- **La mesure** : de quel chiffre parle-t-on ? (le chiffre d'affaires **toutes commandes** ou **hors annulations** ? **toutes taxes** comprises ? à quelle date : celle de la commande ou celle de l'encaissement ?)
- **Le périmètre** : quelles lignes sont concernées ? (le canal Site seulement ? l'année 2025 ? les commandes de test ?)
- **La source de référence** : si les deux disent des choses différentes, laquelle croit-on en premier ? On choisit la plus **proche de l'événement** (la caisse enregistre la vente au moment où elle a lieu) ou la plus **contrôlée** (la base alimente la comptabilité). Ce choix est une convention, à écrire.

Nous réconcilierons trois paires de sources de la boutique, de plus en plus difficiles.

| Paire | Mesure | Clé de rapprochement | Difficulté |
|---|---|---|---|
| **Site contre base** | chiffre d'affaires du canal Site en 2025 | numéro de commande | l'export est désordonné (unité, doublons, tests) |
| **Caisse contre base** | chiffre d'affaires du canal Boutique en 2025 | ticket + article + quantité + prix | douze fichiers, trois formats, des montants vides |
| **Catalogue contre produits** | liste des produits et de leur coût | **aucune** : un code étranger, une désignation réécrite | il faut fabriquer la clé |

### 3.3.2 La méthode en trois temps

Une réconciliation sérieuse suit toujours le même ordre, du plus grossier au plus fin.

1. **Compter.** Les deux sources ont-elles le même nombre de lignes (de commandes, de clients, de produits) ? Un écart d'effectif dit déjà si l'on perd, duplique ou invente des lignes.
2. **Sommer.** Les deux sources ont-elles le même total ? On compare les totaux de la mesure convenue, et l'on note l'écart (absolu et relatif).
3. **Expliquer.** On ventile l'écart en **causes** chiffrées, jusqu'à ce que la somme des causes égale l'écart. Seule cette étape transforme « c'est à peu près bon » en « c'est juste, et voici pourquoi ».

> 💡 **Intuition.** C'est un jeu de piste : la première étape dit *s'il y a* un problème, la deuxième *de quelle taille*, la troisième *où il se cache*. On n'a fini que lorsque l'écart restant vaut zéro (ou est inférieur à une tolérance décidée à l'avance, voir 3.4).

La cascade (en anglais *waterfall*) est l'outil qui rend la troisième étape lisible : une barre pour le total de départ, une barre par cause (vers le haut ou vers le bas), et une barre pour le total d'arrivée, qui doit tomber exactement sur la référence.

### 3.3.3 Le site contre la base : un écart de quarante fois

Commençons par les deux premiers temps sur l'export du site, pour le canal Site en 2025. On compte les lignes, puis on somme les montants **sans précaution** (le texte devient un nombre, c'est tout) :

```python
t_export = site["total"].map(O.montant_site_en_nombre)
base_site = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")]
ca_base = base_site["id_commande"].map(lig.groupby("id_commande")["montant"].sum()).sum()
print("compter :", len(site), "lignes d'export contre", len(base_site), "commandes en base")
print("sommer  :", f"{t_export.sum():,.2f}".replace(",", " "), "€ contre", f"{ca_base:,.2f}".replace(",", " "), "€")
```
<!--sortie-->
```text
compter : 6259 lignes d'export contre 6078 commandes en base
sommer  : 25 012 599.35 € contre 617 715.45 €
```

```python hide
num("n_base_site", len(base_site)); num("brut_site", round(float(t_export.sum()), 2)); num("ca_base_site", round(float(ca_base), 2)); num("ratio_site", round(float(t_export.sum() / ca_base), 1))
num("ecart_effectif_site", len(site) - len(base_site))
```
<!--sortie-->
```text
NUM n_base_site 6078
NUM brut_site 25012599.35
NUM ca_base_site 617715.45
NUM ratio_site 40.5
NUM ecart_effectif_site 181
```

L'export compte 181 lignes de plus que la base (6 259 contre 6 078), et son total vaut **40,5 fois** celui de la base. Cet écart n'est pas un arrondi : il se cache plusieurs causes, que la section 3.2 nous a appris à reconnaître. Allons-y dans l'ordre de leur poids.

**Première cause : l'unité.** À partir du 15 septembre, la date change de format (elle se termine par `Z`) et, en même temps, les montants sont exprimés en **centimes**. On le voit en comparant les montants moyens avant et après :

```python
apres = site["created_at"].str.endswith("Z")                       # format de date de la nouvelle plateforme
print(t_export.groupby(apres).mean().round(1).to_string())
```
<!--sortie-->
```text
created_at
False     102.5
True     9781.2
```

```python hide
t_eur = t_export.where(~apres, t_export / 100)
num("moy_avant", round(float(t_export[~apres].mean()), 1)); num("moy_apres", round(float(t_export[apres].mean()), 1)); num("n_apres", int(apres.sum()))
```
<!--sortie-->
```text
NUM moy_avant 102.5
NUM moy_apres 9781.2
NUM n_apres 2518
```

Le montant moyen vaut 102,5 € avant (la ligne `False`) et 9781,2 après (la ligne `True`) : cent fois plus, pour des commandes qui n'ont pas changé. On divise par cent les montants des 2 518 lignes du nouveau format. Notez que nous **déduisons** le changement d'unité de l'observation, nous ne l'avons lu nulle part : il faudra le **faire confirmer** par l'équipe du site.

**Deuxième et troisième causes : les tests et les copies.** Les commandes de test se reconnaissent à leur adresse, les copies à leur numéro répété (la plateforme a réexporté certaines commandes). On les met de côté et l'on construit la cascade :

```python
test = site["customer_email"].eq("test@example.com")
copie = site["order_ref"].duplicated(keep="first") & ~test
etapes = [("Somme brute de l'export", t_export.sum()), ("montants en centimes (÷ 100)", t_eur.sum() - t_export.sum()),
          ("commandes de test", -t_eur[test].sum()), ("copies d'export", -t_eur[copie].sum())]
tab = pd.DataFrame(etapes, columns=["étape", "montant"]); tab["cumul"] = tab["montant"].cumsum()
print(tab.round(2).to_string(index=False))
print("base :", round(ca_base, 2), "| écart restant :", abs(round(tab["cumul"].iloc[-1] - ca_base, 2)))
```
<!--sortie-->
```text
                       étape      montant       cumul
     Somme brute de l'export  25012599.35 25012599.35
montants en centimes (÷ 100) -24382796.13   629803.22
           commandes de test       -36.24   629766.98
             copies d'export    -12051.53   617715.45
base : 617715.45 | écart restant : 0.0
```

```python hide
propre = site[~test & ~copie].assign(eur=t_eur[~test & ~copie])
num("unite_site", round(abs(float(t_eur.sum() - t_export.sum())), 2)); num("tests_site", round(float(t_eur[test].sum()), 2)); num("copies_site", round(float(t_eur[copie].sum()), 2))
num("n_test_site", int(test.sum())); num("n_copie_site", int(copie.sum())); num("n_propre_site", len(propre)); num("restant_site", round(float(tab["cumul"].iloc[-1] - ca_base), 2) + 0.0)
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), gridspec_kw={"width_ratios": [1.1, 1.0]})
O.cascade(axes[0], [("Export\nbrut", t_export.sum() / 1e6, "total"), ("centimes", (t_eur.sum() - t_export.sum()) / 1e6, "delta"), ("tests +\ncopies", -(t_eur[test].sum() + t_eur[copie].sum()) / 1e6, "delta"), ("Base", ca_base / 1e6, "total")], fmt=lambda v: f"{v:,.3f}".replace(",", " ").replace(".", ","))
axes[0].set_ylabel("Millions d'euros"); axes[0].set_title("Vue d'ensemble", loc="left", fontsize=9)
O.cascade(axes[1], [("Après\ncentimes", t_eur.sum(), "total"), ("tests", -t_eur[test].sum(), "delta"), ("copies", -t_eur[copie].sum(), "delta"), ("Base", ca_base, "total")])
axes[1].set_ylim(605000, 635000); axes[1].set_title("Zoom (axe tronqué)", loc="left", fontsize=9); axes[1].set_ylabel("Euros")
fig.tight_layout(); fig.savefig("figures/ch03-cascade-site.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM unite_site 24382796.13
NUM tests_site 36.24
NUM copies_site 12051.53
NUM n_test_site 60
NUM n_copie_site 121
NUM n_propre_site 6078
NUM restant_site 0.0
```

![Cascade de réconciliation du canal Site : de la somme brute de l'export (25 millions d'euros) au chiffre d'affaires de la base (618 000 euros). À gauche, la vue d'ensemble ; à droite, un zoom sur les deux petites causes (axe tronqué : les barres de départ et d'arrivée sont coupées).](figures/ch03-cascade-site.png)

La cascade est exacte : **l'écart restant est de 0,0 €**. Le changement d'unité explique à lui seul 24 382 796 €, les 121 copies d'export 12 051,53 € et les 60 commandes de test 36,24 €. Ce qui reste, 6 078 commandes pour 617 715,45 €, **égale** la base, centime pour centime. Notez deux détails : les commandes de test pèsent presque rien en euros (1 € l'une) mais elles ne sont pas anodines dans un **comptage** (60 commandes qui n'existent pas), et si l'on n'avait corrigé que l'unité, on aurait gardé 12 000 € de copies.

> ⚠️ **Piège : corriger dans le mauvais ordre.** Si l'on retire les copies **avant** d'avoir converti l'unité, on retire des montants dont la taille dépend de la date : l'écart calculé pour chaque étape change, même si le total final reste juste. On décide d'un ordre, et l'on s'y tient : ici, d'abord les **formats** (unité), puis les **lignes parasites** (tests, copies).

Il reste à traiter trois points qui ne sont pas des écarts, mais des **définitions**.

**Les annulations.** L'export contient des commandes annulées. La base les contient aussi (elle ne porte pas de statut) : elles sont donc **dans les deux totaux**, et ne créent aucun écart. Mais elles comptent pour le chiffre d'affaires **encaissé** :

```python
annule = propre["status"].str.lower().eq("cancelled")
print("commandes annulées :", int(annule.sum()), "| montant :", round(propre.loc[annule, "eur"].sum(), 2), "€")
```
<!--sortie-->
```text
commandes annulées : 181 | montant : 17551.32 €
```

```python hide
num("n_annule", int(annule.sum())); num("montant_annule", round(float(propre.loc[annule, "eur"].sum()), 2)); num("pct_annule", round(100 * float(propre.loc[annule, "eur"].sum() / ca_base), 1))
num("ca_hors_annule", round(float(ca_base - propre.loc[annule, "eur"].sum()), 2))
```
<!--sortie-->
```text
NUM n_annule 181
NUM montant_annule 17551.32
NUM pct_annule 2.8
NUM ca_hors_annule 600164.13
```

181 commandes sont annulées, pour 17 551,32 € (2,8 % du chiffre d'affaires). Ce montant n'explique **aucun écart entre les sources**, mais il explique l'écart entre deux **définitions** du chiffre d'affaires : 617 715,45 € toutes commandes, 600 164,13 € hors annulations. Quand une direction dit « le site m'annonce un chiffre, la comptabilité un autre », la première chose à demander est : *avec ou sans annulations ?*

**Les arrondis.** Le total d'en-tête d'une commande est-il la somme de ses lignes ? Chaque ligne est arrondie au centime, et le total est arrondi lui aussi : de petits écarts apparaissent.

```python
somme_l = site_l.assign(m=site_l["qty"] * site_l["unit_price"] * (1 - site_l["discount_pct"] / 100)).groupby("order_ref")["m"].sum()
diff = propre["eur"].values - propre["order_ref"].map(somme_l).values
print("somme des écarts :", round(float(diff.sum()), 3), "€ | écart maximal :", round(float(np.abs(diff).max()), 3), "€ | commandes à plus d'un demi-centime :", int((np.abs(diff) > 0.005).sum()))
```
<!--sortie-->
```text
somme des écarts : 0.078 € | écart maximal : 0.016 € | commandes à plus d'un demi-centime : 172
```

```python hide
num("arrondi_somme", round(float(diff.sum()), 3)); num("arrondi_max", round(float(np.abs(diff).max()), 3)); num("arrondi_n", int((np.abs(diff) > 0.005).sum()))
```
<!--sortie-->
```text
NUM arrondi_somme 0.078
NUM arrondi_max 0.016
NUM arrondi_n 172
```

Les écarts d'arrondi sont bien réels (172 commandes), mais leur somme est de 0,078 € sur plus de six mille commandes : ils se compensent. On ne les **explique** pas un par un ; on fixe une **tolérance** (par exemple un centime par ligne) et l'on vérifie qu'ils restent en dessous (3.4.2).

**Le fuseau horaire.** Le nouveau format se termine par `Z`, qui veut dire « heure UTC ». Si c'était vrai, une commande passée à 23 h 30 à l'heure locale serait datée du lendemain, et les totaux **journaliers** du site ne tomberaient plus sur ceux de la base. Vérifions, commande par commande, ce que dit la base :

```python
cl = propre.assign(id_commande=propre["order_ref"].str.extract(r"WEB-(\d{6})")[0].astype(int)).merge(cmd[["id_commande", "date_commande", "heure"]], on="id_commande")
meme_jour = (pd.to_datetime(cl["created_at"].str.replace("Z", ""), format="ISO8601").dt.strftime("%Y-%m-%d") == cl["date_commande"])
meme_heure = (cl["created_at"].str[11:16] == cl["heure"])
print("même jour que la base :", round(100 * meme_jour.mean(), 1), "% | même heure que la base :", round(100 * meme_heure.mean(), 1), "%")
```
<!--sortie-->
```text
même jour que la base : 100.0 % | même heure que la base : 100.0 %
```

```python hide
num("pct_meme_jour", round(100 * float(meme_jour.mean()), 1)); num("pct_meme_heure", round(100 * float(meme_heure.mean()), 1)); num("heure_max_base", cmd["heure"].max())
```
<!--sortie-->
```text
NUM pct_meme_jour 100.0
NUM pct_meme_heure 100.0
NUM heure_max_base 21:59
```

Les dates et les heures sont **identiques** à celles de la base, y compris après le 15 septembre : le `Z` est une étiquette trompeuse (l'heure écrite est l'heure locale), ou la base est elle aussi en UTC ; dans les deux cas, **aucune commande ne change de jour**. La dernière commande de la base est à 21:59 : même avec un décalage de deux heures, personne ne passerait minuit. Le fuseau n'a donc rien changé à nos totaux journaliers ; il changerait une analyse **par heure**. Ce qui compte est de l'avoir **vérifié** au lieu de le supposer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.11.

### 3.3.4 La caisse contre la base : douze fichiers, trois formats

La caisse de la boutique envoie un fichier par mois. Au cours de l'année, le logiciel a changé deux fois de format. On le voit en regroupant les fichiers par leurs caractéristiques :

```python
print(fichiers.groupby(["encodage", "separateur", "decimale", "colonnes"]).agg(fichiers=("fichier", "count"), premier=("fichier", "min"), dernier=("fichier", "max")).to_string())
```
<!--sortie-->
```text
                                        fichiers             premier             dernier
encodage  separateur decimale colonnes                                                  
cp1252    ;          ,        8                6  caisse_2025-01.csv  caisse_2025-06.csv
utf-8-sig ,          .        9                3  caisse_2025-10.csv  caisse_2025-12.csv
          ;          ,        8                3  caisse_2025-07.csv  caisse_2025-09.csv
```

Trois formats : de janvier à juin, un fichier en `cp1252` avec `;` et virgule décimale ; de juillet à septembre, le même mais en UTF-8 (et l'en-tête de la colonne des quantités devient « Quantité », la date prend deux chiffres d'année) ; d'octobre à décembre, une virgule comme séparateur, un point décimal, des champs entre guillemets et une **neuvième colonne** (la remise). La fonction `lire_caisse` de `build/outils_ch03.py` absorbe ces différences ; l'écrire est un exercice de nettoyage du chapitre 1, ce qui nous intéresse ici est ce qu'elle rend : une table unique de 12 678 lignes.

Premier et deuxième temps :

```python
base_b = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande")
base_b = base_b[(base_b["canal"] == "Boutique") & (base_b["date_commande"] >= "2025-01-01")]
print("compter :", len(caisse), "lignes en caisse contre", len(base_b), "en base")
print("sommer  : lu", round(caisse["montant"].sum(), 2), "| total affiché", round(fichiers["total_affiche"].sum(), 2), "| base", round(base_b["montant"].sum(), 2))
```
<!--sortie-->
```text
compter : 12678 lignes en caisse contre 12611 en base
sommer  : lu 547896.42 | total affiché 560973.91 | base 560973.91
```

```python hide
num("n_base_b", len(base_b)); num("lu_caisse", round(float(caisse["montant"].sum()), 2)); num("aff_caisse", round(float(fichiers["total_affiche"].sum()), 2)); num("base_caisse", round(float(base_b["montant"].sum()), 2))
num("ecart_effectif_caisse", len(caisse) - len(base_b)); num("ecart_somme_caisse", round(abs(float(caisse["montant"].sum() - base_b["montant"].sum())), 2))
```
<!--sortie-->
```text
NUM n_base_b 12611
NUM lu_caisse 547896.42
NUM aff_caisse 560973.91
NUM base_caisse 560973.91
NUM ecart_effectif_caisse 67
NUM ecart_somme_caisse 13077.49
```

Deux enseignements. La caisse a 67 lignes **de plus** que la base, et la somme des montants lus est inférieure de 13077,49 € : deux défauts de sens opposé (des lignes en trop, des montants manquants). Et le **total affiché** par la caisse (560 973,91 €) est **égal** à celui de la base (560 973,91 €) : ce total est juste, ce sont les lignes que nous avons lues qui sont fautives.

Pour le troisième temps, il faut descendre à la **ligne**. Il n'y a pas d'identifiant de ligne dans la caisse ; on fabrique une clé avec le numéro de ticket, l'article (en minuscules), la quantité, le prix et un **rang** qui départage deux lignes identiques d'un même ticket (le rang vaut 0 pour la première, 1 pour la deuxième, etc.). Le rapprochement se fait par une **fusion externe**, qui garde les lignes des deux côtés et indique d'où elles viennent :

```python
r = O.rapprocher_caisse_base(caisse, cmd, lig, prod)
print(r["_merge"].value_counts().to_string())
```
<!--sortie-->
```text
_merge
both          12611
left_only        67
right_only        0
```

```python hide
vc = pd.read_csv(os.path.join(D, "verite_caisse.csv"))
seules = r[r["_merge"] == "left_only"]
par_fichier = seules.groupby("fichier").size().reindex(sorted(vc["fichier"].unique()), fill_value=0)
verite_par_fichier = vc.groupby("fichier")["est_doublon"].sum()
num("n_both", int((r["_merge"] == "both").sum())); num("n_left", int((r["_merge"] == "left_only").sum())); num("n_right", int((r["_merge"] == "right_only").sum()))
num("copies_retrouvees", "oui" if (par_fichier.values == verite_par_fichier.reindex(par_fichier.index).values).all() else "non")
```
<!--sortie-->
```text
NUM n_both 12611
NUM n_left 67
NUM n_right 0
NUM copies_retrouvees oui
```

12 611 lignes se retrouvent des deux côtés, **67** n'existent qu'en caisse et **0** qu'en base. Aucune ligne de la base ne manque à la caisse (rien n'est perdu), mais 67 lignes de la caisse n'ont pas d'équivalent : ce sont des **copies**, c'est-à-dire des lignes scannées deux fois. Le rang le montre : la copie a le rang 1 et la base n'a pas de ligne de rang 1 pour ce ticket.

> 💡 **Intuition.** Sans le rang, la fusion aurait associé les deux copies à la **même** ligne de la base, et nous n'aurions rien vu : les doublons auraient simplement doublé les lignes après jointure (le piège du volume I, section 3.2.6). La clé doit être **assez fine pour que chaque ligne n'ait qu'une correspondance possible**.

On peut maintenant expliquer l'écart de somme. On retire les copies, on complète les montants vides (une ligne de la caisse sans montant, mais qui existe en base), puis on tient compte des remises :

```python
copies = r[r["_merge"] == "left_only"]
vides = r[(r["_merge"] == "both") & r["montant"].isna()]
qp = vides["qte"] * vides["prix_unitaire"]
etapes = [("Somme des montants lus", caisse["montant"].sum()), ("copies de scan", -copies["montant"].sum()),
          ("montants vides complétés (qté × prix)", qp.sum()), ("remises des lignes vides", -(qp - vides["montant_base"]).sum())]
tab_c = pd.DataFrame(etapes, columns=["étape", "montant"]); tab_c["cumul"] = tab_c["montant"].cumsum()
print(tab_c.round(2).to_string(index=False))
```
<!--sortie-->
```text
                                étape   montant     cumul
               Somme des montants lus 547896.42 547896.42
                       copies de scan  -3126.29 544770.13
montants vides complétés (qté × prix)  16518.59 561288.72
             remises des lignes vides   -314.81 560973.91
```

```python hide
num("copies_caisse", round(float(copies["montant"].sum()), 2)); num("n_vides", int(len(vides))); num("complete_qp", round(float(qp.sum()), 2)); num("remises_vides", round(float((qp - vides["montant_base"]).sum()), 2))
num("restant_caisse", round(float(tab_c["cumul"].iloc[-1] - base_b["montant"].sum()), 2) + 0.0); num("n_vides_total", int(caisse["montant"].isna().sum()))
fig, ax = plt.subplots(figsize=(6.6, 3.3))
O.cascade(ax, [("Somme des\nmontants lus", tab_c["montant"].iloc[0], "total"), ("copies\nde scan", tab_c["montant"].iloc[1], "delta"), ("montants vides\n(qté × prix)", tab_c["montant"].iloc[2], "delta"), ("remises des\nlignes vides", tab_c["montant"].iloc[3], "delta"), ("Total affiché\n= base", float(base_b["montant"].sum()), "total")])
ax.set_ylim(540000, 566000); ax.set_ylabel("Euros (axe tronqué)")
fig.tight_layout(); fig.savefig("figures/ch03-cascade-caisse.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM copies_caisse 3126.29
NUM n_vides 398
NUM complete_qp 16518.59
NUM remises_vides 314.81
NUM restant_caisse 0.0
NUM n_vides_total 399
```

![Cascade de réconciliation de la caisse : de la somme des montants lus dans les douze fichiers au total affiché par la caisse, égal à celui de la base. Axe vertical tronqué.](figures/ch03-cascade-caisse.png)

L'écart restant est de 0,0 € : l'explication est **complète**. Les 398 montants vides retrouvés dans la base valent 16 518,59 € au prix catalogue ; les remises que la caisse n'imprime pas avant octobre les ramènent à leur valeur exacte, soit 314,81 € de moins. Retenez la mécanique : **chaque étape de la cascade est un nombre que l'on a calculé, pas un reste que l'on a « mis dans une case »**. Un écart qu'on ne sait expliquer que par un « divers » n'est pas expliqué.

Un dernier contrôle de la réconciliation : les copies que nous avons trouvées sont-elles bien les doublons du double scan ? La vérité programmée donne, pour chaque fichier, le nombre de lignes doublées : les douze comptes **coïncident** avec ceux de notre rapprochement (vérifié : oui). Dans une étude réelle, on ne dispose pas de cette vérité : on l'aurait remplacée par une question à l'équipe de la caisse (« avez-vous un double scan ? ») et par le fait que le total affiché retombe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.10.

### 3.3.5 Le catalogue contre les produits : fabriquer la clé

Le troisième cas est le plus fréquent en pratique et le plus délicat : deux listes **sans clé commune**. Le catalogue du fournisseur a ses propres codes (`F-1497`) et ses propres désignations ; la boutique a ses numéros de produit. Seule la **désignation** les rapproche, et elle est écrite autrement : majuscules, accents retirés, ordre des mots, abréviations, espaces parasites.

On commence par une **normalisation** qui supprime les écarts de pure forme (accents, casse, espaces), puis on joint sur le nom :

```python
def cle_nom(s):
    return s.map(lambda x: O.sans_accents(str(x)).lower().strip())
cat["cle"], prod["cle"] = cle_nom(cat["designation"]), cle_nom(prod["nom_produit"])
m = cat.merge(prod[["id_produit", "cle", "cout_achat"]], on="cle", how="left")
print("lignes après jointure sur le nom :", len(m), "pour", len(cat), "lignes de catalogue | sans correspondance :", int(m["id_produit"].isna().sum()))
```
<!--sortie-->
```text
lignes après jointure sur le nom : 196 pour 118 lignes de catalogue | sans correspondance : 40
```

```python hide
num("n_apres_jointure", len(m)); num("n_cat_sans", int(m["id_produit"].isna().sum())); num("n_noms_prod", int(prod["cle"].nunique())); num("n_prod", len(prod))
```
<!--sortie-->
```text
NUM n_apres_jointure 196
NUM n_cat_sans 40
NUM n_noms_prod 60
NUM n_prod 120
```

Deux surprises. D'abord la jointure a produit 196 lignes pour 118 lignes de catalogue : les produits de la boutique n'ont que 60 noms distincts pour 120 produits (deux produits portent chacun le même nom, à des prix différents), donc chaque ligne de catalogue se multiplie : c'est **le piège du volume I** (section 3.2.6). Ensuite 40 lignes de catalogue n'ont aucun correspondant.

Pour départager les homonymes, on ajoute une **seconde clé** : le **prix**. Le prix d'achat du catalogue doit être proche du coût d'achat de la boutique, à quelques pour cent près ; on retient les paires dont l'écart relatif est inférieur à 3,5 % :

```python
m["ecart_prix"] = (m["prix_achat_ht"] / m["cout_achat"] - 1).abs()
ok = m[m["ecart_prix"] <= 0.035]
print("codes appariés par nom + prix :", ok["code_fournisseur"].nunique(), "| codes qui désignent encore deux produits :", int(ok["code_fournisseur"].duplicated().sum()))
reste = cat[~cat["code_fournisseur"].isin(ok["code_fournisseur"])]
print(reste[["code_fournisseur", "designation", "prix_achat_ht"]].head(5).to_string(index=False))
```
<!--sortie-->
```text
codes appariés par nom + prix : 78 | codes qui désignent encore deux produits : 2
code_fournisseur          designation  prix_achat_ht
          F-1707        Diffu. design           4.86
          F-1798 Nouveauté 6 Brillant          31.38
          F-1553        Gants. design           9.77
          F-1147     compact Étagère           14.76
          F-1280    compact Guirlande          13.98
```

```python hide
g = ok.merge(vprod, on="code_fournisseur", suffixes=("", "_vrai"))
amb = ok["code_fournisseur"].duplicated(keep=False)
num("n_apparies", int(ok["code_fournisseur"].nunique())); num("n_ambigus", int(ok.loc[amb, "code_fournisseur"].nunique()))
sans_ambig = g[~g["code_fournisseur"].isin(ok.loc[amb, "code_fournisseur"])]
num("n_exacts", int((sans_ambig["id_produit"] == sans_ambig["id_produit_vrai"]).sum())); num("n_faux", int((sans_ambig["id_produit"] != sans_ambig["id_produit_vrai"]).sum()))
nr = reste.merge(vprod, on="code_fournisseur")
num("n_reste", len(reste)); num("n_reste_nouveaux", int((nr["id_produit"] == -1).sum())); num("n_reste_anciens", int((nr["id_produit"] != -1).sum()))
num("n_prod_sans_cat", int((~prod["id_produit"].isin(ok["id_produit"])).sum())); num("n_prod_absents", int((~prod["id_produit"].isin(vprod["id_produit"])).sum()))
```
<!--sortie-->
```text
NUM n_apparies 78
NUM n_ambigus 2
NUM n_exacts 76
NUM n_faux 0
NUM n_reste 40
NUM n_reste_nouveaux 10
NUM n_reste_anciens 30
NUM n_prod_sans_cat 41
NUM n_prod_absents 12
```

La clé « nom + prix » rapproche 78 codes du catalogue, dont 2 désignent encore **deux** produits (deux produits de même nom dont les coûts sont trop proches pour être départagés) ; ces cas sont des **exceptions**, à confier à quelqu'un, pas à deviner. Il reste 40 lignes sans correspondant : la liste de tête montre pourquoi (« Diffu. design » est une abréviation, « compact Étagère » a l'ordre des mots inversé).

Que dit la vérité programmée ? Parmi les codes appariés sans ambiguïté, **76** sont exacts et 0 faux : la clé est fiable quand elle tranche. Parmi les 40 lignes restantes, 10 sont de vrais produits nouveaux du fournisseur (qui n'existent pas à la boutique : ils ne **doivent pas** s'apparier), et 30 sont des produits que nous **avons** et que la normalisation simple n'a pas su reconnaître. Côté boutique, 41 produits n'ont pas de ligne de catalogue : 12 sont absents du catalogue du fournisseur, les autres font partie des lignes non reconnues. Les 30 cas difficiles relèvent de l'**appariement approximatif** (*fuzzy matching*, section 2.5 de ce volume) : des mesures de ressemblance entre textes plutôt qu'une égalité stricte.

> ⚠️ **Piège : une clé fabriquée n'est pas une clé.** Une clé fabriquée (nom normalisé + prix) apparie des choses qui se ressemblent, pas des choses identiques. Elle peut se tromper, et l'erreur est silencieuse : deux produits de même nom et de même coût seraient confondus sans alerte. On mesure donc **trois nombres** : combien d'appariements certains, combien d'ambigus, combien de non-appariés, et l'on traite chaque catégorie séparément.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7.

### 3.3.6 Un catalogue des causes d'écart

Les trois exemples ont montré les causes d'écart les plus fréquentes. Les connaître d'avance fait gagner du temps : on les passe en revue **dans cet ordre**, du plus fréquent au plus rare.

| Cause | Symptôme | Où nous l'avons vue |
|---|---|---|
| **Unité ou échelle** | rapport constant (×100, ×1 000) entre les deux totaux | export du site, centimes à partir du 15 septembre |
| **Doublons** | plus de lignes dans une source que dans l'autre | copies d'export du site ; double scan de la caisse |
| **Lignes parasites** | lignes sans équivalent : tests, orphelins | commandes de test du site |
| **Valeurs manquantes** | total inférieur au total affiché | montants vides de la caisse |
| **Périmètre et définition** | écart égal à un sous-ensemble connu | commandes annulées (avec ou sans) |
| **Calendrier et fuseau** | écarts qui se déplacent d'un jour à l'autre | vérifié : nul ici |
| **Arrondis** | écarts de quelques centimes, qui se compensent | total d'en-tête contre somme des lignes |
| **Remises, taxes, frais** | écart proportionnel aux lignes concernées | remises non imprimées avant octobre |
| **Clé mal fabriquée** | appariements faux ou multiples | homonymes du catalogue |

### 3.3.7 Quand s'arrêter ?

Une réconciliation s'arrête quand l'écart restant est **expliqué ou tolérable**, et pas avant. Trois critères de sortie.

- **Écart nul** : comme pour le site et la caisse, la cascade tombe exactement sur la référence. C'est le cas idéal.
- **Écart expliqué mais non nul** : une cause connue ne peut pas être chiffrée précisément (les remises avant octobre, si l'on n'avait pas eu la base). On l'écrit, avec une **fourchette**.
- **Écart tolérable** : sous un seuil fixé d'avance (3.4.2), et dont les causes sont de même nature que les arrondis.

Il y a aussi des raisons de **ne pas** s'arrêter : un écart qui change de signe d'un mois à l'autre, une cause dont le poids grandit, un « divers » qui dépasse le seuil. Dans tous ces cas, la réconciliation n'est pas finie.

Terminez toujours par une **note de réconciliation** d'une demi-page : les sources et leurs dates d'extraction, la mesure et le périmètre, les trois temps avec leurs chiffres, la cascade, les décisions prises (« les montants du site sont divisés par cent à partir du 15 septembre, à faire confirmer »), les exceptions restantes avec un responsable. C'est cette note, bien plus que le code, qui permet à quelqu'un d'autre de **refaire et de croire** votre résultat (le chapitre 4 de ce volume en fait un document type).

> ✅ **À retenir de la section 3.3.**
> - Réconcilier, c'est comparer deux sources sur **la même mesure, le même périmètre**, et **expliquer chaque écart** par des causes chiffrées.
> - La méthode : **compter, sommer, expliquer** ; la cascade rend la troisième étape lisible, et doit tomber **exactement** sur la référence.
> - Les causes fréquentes : unité, doublons, lignes parasites, valeurs manquantes, définitions, calendrier, arrondis, remises, clés mal fabriquées.
> - Sans clé commune, on **fabrique** une clé (normalisation, prix, rang) et l'on distingue appariements certains, ambigus et non appariés.
> - Une réconciliation se termine par une **note** : les chiffres, les décisions, les exceptions et leur responsable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 à 3.7, exercices 3.10 et 3.11.
