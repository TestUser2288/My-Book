# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume I. Il contient **le projet du volume** : une **première analyse complète**, du fichier brut au tableau de synthèse, que vous remettrez à la gérante ; puis l'**auto-évaluation** (quarante questions). Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre, et chaque chiffre est **recoupé par au moins deux outils** (SQL, Python, R, tableur).

## Projet du volume

### P.1 Le cahier des charges

La gérante vous écrit : « *Pour la réunion de janvier, j'aimerais une page qui compare le dernier trimestre 2025 au même trimestre de 2024, par canal : ce que l'on a vendu, combien de commandes, le panier moyen, ce que l'on rembourse en retours et ce que l'on gagne vraiment. Et je voudrais être sûre que les chiffres sont bons : le logiciel de caisse et le site ne donnent pas toujours les mêmes totaux.* »

Vous traduisez en **cinq exigences** :

1. **Un tableau de synthèse** par canal (Boutique, Site, Réseaux) : chiffre d'affaires, commandes, panier moyen, taux de retour, marge brute, avec l'évolution en pourcentage.
2. **Des chiffres vérifiés** : chaque total obtenu par au moins deux outils différents, et un écart expliqué ou nul.
3. **Un fichier brut maîtrisé** : l'export de la caisse de la boutique (une semaine) est lu, nettoyé, puis **réconcilié** avec la base de données.
4. **Un classeur lisible** que la gérante peut ouvrir et dont les formules sont visibles.
5. **Un message** de cinq lignes, un graphique, et la liste de ce que l'analyse **ne dit pas**.

La méthode suit neuf étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Comprendre | Que contient chaque table ? Quel est son grain ? | 5.1, 3.1 |
| P.3 Lire le fichier brut | Comment passer d'un export désordonné à un tableau propre ? | 4.3, 2.3 |
| P.4 Réconcilier | La caisse et la base disent-elles la même chose ? | 3.2, 4.1 |
| P.5 Calculer la synthèse | Quel est le chiffre d'affaires par canal et par trimestre ? | 3.1, 3.4, 4.1, 4.2 |
| P.6 Les indicateurs | Panier moyen, retours, marge : comment les calculer sans se tromper ? | 1.5, 1.1 |
| P.7 Le classeur | Comment livrer un tableau à formules vérifiables ? | 2.1, 2.4 |
| P.8 Le graphique | Que montrer ? | 1.1 |
| P.9 Le message | Qu'est-ce qu'on dit, et qu'est-ce qu'on ne peut pas dire ? | 1.4, 5.3 |

> 📦 **Les données.** `donnees/boutique.db` (base SQLite), `donnees/export_caisse_brut.csv` (une semaine de caisse de la boutique, désordonnée) et les fichiers CSV associés. Elles sont **simulées** : la vérité est programmée (docstring de `build/donnees_a1.py`). Les taux et les montants sont fictifs ; la TVA est fixée à 20 % **pour l'illustration**.

### P.2 Étape 1 : comprendre les données

Avant tout calcul, on vérifie le **grain** de chaque table (qu'est-ce qu'une ligne ?) et les clés qui les relient (livre, 3.1 et 5.1). Un comptage simple suffit.

```python
import sqlite3, io
import numpy as np, pandas as pd

con = sqlite3.connect("donnees/boutique.db")
for t in ["clients", "produits", "commandes", "lignes_commande", "retours", "jours_exploitation"]:
    n = con.execute(f"select count(*) from {t}").fetchone()[0]
    print(f"{t:20s} {n:>7,d} lignes".replace(",", " "))
print("commandes distinctes dans les lignes :", con.execute("select count(distinct id_commande) from lignes_commande").fetchone()[0])
print("lignes par commande en moyenne :", round(con.execute("select count(*)*1.0/count(distinct id_commande) from lignes_commande").fetchone()[0], 2))
```
<!--sortie-->
```text
clients                6 000 lignes
produits                 120 lignes
commandes             36 395 lignes
lignes_commande       83 905 lignes
retours                5 002 lignes
jours_exploitation     1 096 lignes
commandes distinctes dans les lignes : 36395
lignes par commande en moyenne : 2.31
```

Le **grain** est la ligne de commande : une commande contient plusieurs lignes, et un retour porte sur une ligne. Retenez-le : tout calcul de « nombre de commandes » doit compter des commandes **distinctes**, pas des lignes.

### P.3 Étape 2 : lire le fichier brut de la caisse

L'export de la caisse est un fichier **à la française** : encodage `cp1252`, séparateur `;`, virgule décimale, dates `jj/mm/aaaa`, trois lignes de titre, un en-tête répété à chaque « page », une ligne de total, des cellules vides. On l'ouvre sans rien deviner (livre, 4.3 et 2.3).

```python
with open("donnees/export_caisse_brut.csv", encoding="cp1252") as f:
    lignes = f.read().splitlines()
print("lignes du fichier :", len(lignes))
print(*lignes[:5], sep="\n")
print("...")
print(lignes[-1])
```
<!--sortie-->
```text
lignes du fichier : 289
Export caisse - Boutique;;;;;;;
Période du 03/11/2025 au 09/11/2025;;;;;;;
;;;;;;;
N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant
T33133;03/11/2025;09:00;BOÎTE RUSTIQUE;Maison;2;52,43;104,86
...
;;;;;;Total;11561,47
```

On saute les trois lignes de titre, on lit tout en **texte**, on retire la ligne de total (que l'on garde de côté pour le recoupement) et les en-têtes répétés, puis on convertit les types explicitement.

```python
total_affiche = float(lignes[-1].split(";")[-1].replace(",", "."))
corps = "\n".join(lignes[3:-1])
brut = pd.read_csv(io.StringIO(corps), sep=";", dtype=str)
brut = brut[brut["N° ticket"] != "N° ticket"].copy()
brut.columns = ["ticket", "date", "heure", "article", "categorie", "qte", "prix_unitaire", "montant"]
brut["date"] = pd.to_datetime(brut["date"], format="%d/%m/%Y")
brut["qte"] = brut["qte"].astype(int)
for c in ["prix_unitaire", "montant"]:
    brut[c] = brut[c].str.replace(",", ".").astype(float)
brut["article"] = brut["article"].str.capitalize()
brut["categorie"] = brut["categorie"].str.capitalize()
print(brut.shape, "| montants manquants :", int(brut["montant"].isna().sum()))
print("somme des montants présents :", round(brut["montant"].sum(), 2), "| total affiché par la caisse :", total_affiche)
```
<!--sortie-->
```text
(280, 8) | montants manquants : 8
somme des montants présents : 11250.01 | total affiché par la caisse : 11561.47
```

**Lecture.** Le fichier compte 280 lignes d'achats, dont 8 sans montant. La somme des montants présents est de 11 250,01 €, alors que la caisse affiche 11 561,47 € : il manque **311,46 €**, soit 2,7 % du total.

La somme des montants lus **ne retombe pas** sur le total affiché : l'écart vient des cellules vides. On ne comble pas à l'aveugle : on cherche la cause, puis on **réconcilie** avec une source fiable.

### P.4 Étape 3 : réconcilier la caisse et la base

La même semaine existe dans la base de données (canal « Boutique », commandes du 3 au 9 novembre 2025). On recalcule le total par SQL, ligne par ligne, et on compare (livre, 3.2 et 3.4).

```python
sql_semaine = """
select c.id_commande, c.date_commande, l.id_ligne, p.nom_produit, p.categorie, l.quantite, l.prix_unitaire, l.remise_pct, l.montant
from commandes c join lignes_commande l using (id_commande) join produits p using (id_produit)
where c.canal = 'Boutique' and c.date_commande between '2025-11-03' and '2025-11-09'
"""
base = pd.read_sql(sql_semaine, con)
print("lignes dans la base :", len(base), "| lignes dans l'export :", len(brut))
print("CA de la base :", round(base["montant"].sum(), 2), "| total affiché par la caisse :", total_affiche)
brut["id_commande"] = brut["ticket"].str[1:].astype(int)
manquants = brut[brut["montant"].isna()]
print("tickets concernés par un montant manquant :", manquants["id_commande"].nunique())
```
<!--sortie-->
```text
lignes dans la base : 280 | lignes dans l'export : 280
CA de la base : 11561.47 | total affiché par la caisse : 11561.47
tickets concernés par un montant manquant : 8
```

**Lecture.** La base contient exactement les mêmes 280 lignes que l'export, et son chiffre d'affaires (11 561,47 €) est **égal au total affiché par la caisse**. Les 8 montants vides concernent 8 tickets différents.

Le total affiché par la caisse est **identique** à celui de la base : la caisse avait raison, c'est l'**export** qui a perdu des montants. On peut alors reconstituer les montants manquants à partir de la base et vérifier que la somme complète retombe exactement.

```python
cle = ["id_commande", "nom_produit", "quantite", "prix_unitaire"]
brut2 = brut.rename(columns={"article": "nom_produit", "qte": "quantite"}).copy()
b = base.copy()
for d in (brut2, b):
    d["nom_produit"] = d["nom_produit"].str.capitalize()
    d["rang"] = d.groupby(cle).cumcount()          # distingue deux lignes identiques d'un même ticket
fusion = brut2.merge(b[cle + ["rang", "montant"]], on=cle + ["rang"], how="left", suffixes=("", "_base"))
print("lignes de l'export sans correspondance dans la base :", int(fusion["montant_base"].isna().sum()), "| lignes après fusion :", len(fusion))
fusion["montant_complet"] = fusion["montant"].fillna(fusion["montant_base"])
print("somme complète :", round(fusion["montant_complet"].sum(), 2), "| total de la caisse :", total_affiche)
print("écart :", round(fusion["montant_complet"].sum() - total_affiche, 2))
```
<!--sortie-->
```text
lignes de l'export sans correspondance dans la base : 0 | lignes après fusion : 280
somme complète : 11561.47 | total de la caisse : 11561.47
écart : 0.0
```

**Lecture.** Aucune ligne de l'export n'est sans correspondance, et la somme complète retombe **exactement** sur le total de la caisse (écart nul). La clé de rapprochement comprend un **rang** parce que deux lignes d'un même ticket peuvent être identiques (même article, même quantité, même prix) : sans lui, la fusion dupliquerait des lignes et le total serait faux.

> ✅ **À retenir.** Une réconciliation se fait en trois temps : **compter** (mêmes lignes ?), **sommer** (même total ?), **expliquer** (d'où vient l'écart ?). Ici l'écart venait de cellules vides dans l'export ; la base, source de vérité, a permis de les reconstituer.

### P.5 Étape 4 : la synthèse du dernier trimestre, par trois outils

On calcule le chiffre d'affaires et le nombre de commandes du **quatrième trimestre** (octobre à décembre) de 2024 et de 2025, par canal. La même question, posée à **SQL**, à **pandas** et à **R**, doit donner les mêmes chiffres (livre, 3.4, 4.1 et 4.2).

```python
sql_t4 = """
select strftime('%Y', c.date_commande) as annee, c.canal, count(distinct c.id_commande) as commandes, round(sum(l.montant), 2) as ca
from commandes c join lignes_commande l using (id_commande)
where strftime('%m', c.date_commande) in ('10', '11', '12') and strftime('%Y', c.date_commande) in ('2024', '2025')
group by annee, c.canal order by c.canal, annee
"""
t4_sql = pd.read_sql(sql_t4, con)
print(t4_sql.to_string(index=False))
```
<!--sortie-->
```text
annee    canal  commandes        ca
 2024 Boutique       1834 175280.54
 2025 Boutique       1846 185292.97
 2024  Réseaux        433  39807.02
 2025  Réseaux        511  51073.62
 2024     Site       1846 175635.46
 2025     Site       2155 211433.79
```

```python
cmd = pd.read_sql("select * from commandes", con, parse_dates=["date_commande"])
lig = pd.read_sql("select * from lignes_commande", con)
x = lig.merge(cmd[["id_commande", "date_commande", "canal", "id_client", "code_promo"]], on="id_commande")
x["annee"], x["mois"] = x["date_commande"].dt.year, x["date_commande"].dt.month
t4 = x[(x["mois"] >= 10) & x["annee"].isin([2024, 2025])]
t4_pd = t4.groupby(["canal", "annee"]).agg(commandes=("id_commande", "nunique"), ca=("montant", "sum")).round(2).reset_index()
print("pandas = SQL :", np.allclose(t4_pd["ca"].values, t4_sql["ca"].values) and (t4_pd["commandes"].values == t4_sql["commandes"].values).all())
```
<!--sortie-->
```text
pandas = SQL : True
```

**Lecture.** SQL et pandas donnent les mêmes six lignes : au quatrième trimestre 2025, le chiffre d'affaires est de 185 293 € pour la Boutique, 51 074 € pour les Réseaux et 211 434 € pour le Site.

```r
library(dplyr, warn.conflicts = FALSE)
dossier <- Sys.getenv("DONNEES")
lig <- read.csv(file.path(dossier, "lignes_commande.csv")); cmd <- read.csv(file.path(dossier, "commandes.csv"))
x <- lig |> inner_join(cmd, by = "id_commande") |>
  mutate(annee = as.integer(substr(date_commande, 1, 4)), mois = as.integer(substr(date_commande, 6, 7))) |>
  filter(mois >= 10, annee %in% c(2024, 2025))
r <- x |> group_by(canal, annee) |> summarise(commandes = n_distinct(id_commande), ca = round(sum(montant), 2), .groups = "drop") |> arrange(canal, annee)
print(as.data.frame(r))
```
<!--sortie-->
```text
     canal annee commandes        ca
1 Boutique  2024      1834 175280.54
2 Boutique  2025      1846 185292.97
3  Réseaux  2024       433  39807.02
4  Réseaux  2025       511  51073.62
5     Site  2024      1846 175635.46
6     Site  2025      2155 211433.79
```

**Lecture.** R retrouve les mêmes totaux (le nom des colonnes et l'ordre des lignes diffèrent à peine). Trois langages, un seul résultat : on peut passer à la suite.

Les trois outils donnent les mêmes totaux. Ce n'est pas un détail : si deux outils divergent, **l'un des deux calcule autre chose** (un filtre de dates différent, une jointure qui duplique des lignes, un arrondi).

### P.6 Étape 5 : les indicateurs de la synthèse

On complète avec le **panier moyen** (CA divisé par le nombre de commandes), le **taux de retour** (lignes retournées sur lignes vendues), la **marge brute** et l'évolution en pourcentage. Deux pièges : le panier moyen d'un total n'est pas la moyenne des paniers moyens des canaux, et une marge se calcule **hors taxe** (livre, 1.1 et 1.5).

```python
TVA = 0.20      # taux de TVA fictif, pour l'illustration
prod = pd.read_sql("select id_produit, cout_achat from produits", con)
ret = pd.read_sql("select id_ligne, montant_rembourse from retours", con)
t4 = t4.merge(prod, on="id_produit").merge(ret, on="id_ligne", how="left")
t4["retourne"] = t4["montant_rembourse"].notna()
t4["marge_ht"] = t4["montant"] / (1 + TVA) - t4["quantite"] * t4["cout_achat"]
syn = t4.groupby(["canal", "annee"]).agg(ca=("montant", "sum"), commandes=("id_commande", "nunique"), lignes=("id_ligne", "size"),
                                         retours=("retourne", "sum"), marge=("marge_ht", "sum")).reset_index()
syn["panier_moyen"] = syn["ca"] / syn["commandes"]
syn["taux_retour"] = syn["retours"] / syn["lignes"]
syn["taux_marge"] = syn["marge"] / (syn["ca"] / (1 + TVA))
print(syn.round(3).to_string(index=False))
```
<!--sortie-->
```text
   canal  annee        ca  commandes  lignes  retours     marge  panier_moyen  taux_retour  taux_marge
Boutique   2024 175280.54       1834    4154      107 53517.907        95.573        0.026       0.366
Boutique   2025 185292.97       1846    4266      150 58902.348       100.375        0.035       0.381
 Réseaux   2024  39807.02        433    1003       81 11998.227        91.933        0.081       0.362
 Réseaux   2025  51073.62        511    1185       90 16315.470        99.948        0.076       0.383
    Site   2024 175635.46       1846    4261      371 53514.863        95.144        0.087       0.366
    Site   2025 211433.79       2155    4911      419 67718.105        98.113        0.085       0.384
```

**Lecture.** Le Site a le taux de retour le plus élevé (8,5 % des lignes en 2025, contre 3,5 % pour la Boutique et 7,6 % pour les Réseaux). Le taux de marge brute, hors taxe, est voisin de 38 % pour les trois canaux en 2025, et de 36–37 % en 2024.

```python
tot = t4.groupby("annee").agg(ca=("montant", "sum"), commandes=("id_commande", "nunique"), retours=("retourne", "sum"), lignes=("id_ligne", "size"))
tot["panier_moyen"] = tot["ca"] / tot["commandes"]
moyenne_des_moyennes = syn[syn["annee"] == 2025]["panier_moyen"].mean()
print("panier moyen 2025 (total) :", round(tot.loc[2025, "panier_moyen"], 2), "| moyenne des paniers moyens des canaux :", round(moyenne_des_moyennes, 2))
evo = syn.pivot(index="canal", columns="annee", values="ca")
print("évolution du CA 2025 / 2024 :", ((evo[2025] / evo[2024] - 1) * 100).round(1).to_dict(), "| total :", round((tot.loc[2025, "ca"] / tot.loc[2024, "ca"] - 1) * 100, 1))
```
<!--sortie-->
```text
panier moyen 2025 (total) : 99.25 | moyenne des paniers moyens des canaux : 99.48
évolution du CA 2025 / 2024 : {'Boutique': 5.7, 'Réseaux': 28.3, 'Site': 20.4} | total : 14.6
```

**Lecture.** Le panier moyen du total (99,25 €) diffère de la moyenne des paniers moyens des canaux (99,48 €) : c'est le **poids des commandes** de chaque canal qui explique l'écart, d'où la règle de calculer le panier moyen sur les totaux. Le chiffre d'affaires du trimestre progresse de 14,6 % ; la progression est de 5,7 % pour la Boutique, 20,4 % pour le Site et 28,3 % pour les Réseaux. En euros, le Site contribue le plus (+35 798 €).

### P.7 Étape 6 : le classeur de synthèse

La gérante veut un **classeur**, avec des formules qu'elle peut inspecter. On y met les données agrégées (canal × année) sur une feuille et la synthèse sur une autre, avec de vraies formules ; on les **fait recalculer** par LibreOffice pour vérifier que le classeur affiche les mêmes chiffres que Python (livre, 2.1 et 2.4). Excel lui-même n'est pas installé : la vérification est faite avec LibreOffice Calc.

```python
import sys, os, tempfile
sys.path.insert(0, "build")
import outils_xl as X
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
donnees = [["canal", "annee", "ca", "commandes", "retours", "lignes"]] + [
    [r.canal, int(r.annee), round(float(r.ca), 2), int(r.commandes), int(r.retours), int(r.lignes)] for r in syn.itertuples()]
synthese = [["Canal", "CA 2024", "CA 2025", "Évolution", "Panier moyen 2025", "Taux de retour 2025"]]
for i, canal in enumerate(["Boutique", "Réseaux", "Site"], start=2):
    synthese.append([canal, f'=SUMIFS(Donnees!C:C,Donnees!A:A,A{i},Donnees!B:B,2024)', f'=SUMIFS(Donnees!C:C,Donnees!A:A,A{i},Donnees!B:B,2025)',
                     f"=C{i}/B{i}-1", f'=C{i}/SUMIFS(Donnees!D:D,Donnees!A:A,A{i},Donnees!B:B,2025)',
                     f'=SUMIFS(Donnees!E:E,Donnees!A:A,A{i},Donnees!B:B,2025)/SUMIFS(Donnees!F:F,Donnees!A:A,A{i},Donnees!B:B,2025)'])
synthese.append(["Total", "=SUM(B2:B4)", "=SUM(C2:C4)", "=C5/B5-1", None, None])
chemin = X.classeur(os.path.join(dossier, "synthese_T4.xlsx"), {"Synthese": synthese, "Donnees": donnees})
val = X.valeurs(X.recalculer(chemin), "Synthese")
for ligne in val:
    print([round(v, 3) if isinstance(v, float) else v for v in ligne])
```
<!--sortie-->
```text
['Canal', 'CA 2024', 'CA 2025', 'Évolution', 'Panier moyen 2025', 'Taux de retour 2025']
['Boutique', 175280.54, 185292.97, 0.057, 100.375, 0.035]
['Réseaux', 39807.02, 51073.62, 0.283, 99.948, 0.076]
['Site', 175635.46, 211433.79, 0.204, 98.113, 0.085]
['Total', 390723.02, 447800.38, 0.146, None, None]
```

```python
ca25 = syn[syn["annee"] == 2025].set_index("canal")["ca"]
ok = all(abs(val[i][2] - ca25[val[i][0]]) < 0.01 for i in range(1, 4))
print("formules du classeur = résultats de pandas :", ok, "| formule de l'évolution (affichage français) :", X.en_fr("=C2/B2-1"))
print("formule du CA 2025 (affichage français) :", X.en_fr(synthese[1][2]))
```
<!--sortie-->
```text
formules du classeur = résultats de pandas : True | formule de l'évolution (affichage français) : =C2/B2-1
formule du CA 2025 (affichage français) : =SOMME.SI.ENS(Donnees!C:C;Donnees!A:A;A2;Donnees!B:B;2025)
```

**Lecture.** Les formules du classeur donnent les mêmes valeurs que pandas. La seconde ligne montre la formule telle qu'elle s'afficherait dans un Excel en français : `SOMME.SI.ENS` avec le séparateur `;`.


![Maquette du classeur de synthèse : la cellule active contient la formule du chiffre d'affaires 2025 de la Boutique. Maquette dessinée avec matplotlib à partir des valeurs recalculées par LibreOffice, pas une capture d'Excel.](figures/ch10-classeur-synthese.png)

> ⚠️ **Attention.** Un classeur n'est fiable que si les **entrées** sont séparées des **calculs** et si le résultat est recoupé. Ici, les chiffres affichés par les formules sont comparés à ceux de pandas : sans cette comparaison, une erreur de plage ou un `2024` en dur passe inaperçu.

### P.8 Étape 7 : le graphique

Un seul graphique, qui répond à la question de la gérante : **qu'est-ce qui a changé, et où ?** On montre le chiffre d'affaires par canal pour les deux trimestres, avec l'évolution écrite sur les barres (livre, 1.1).

```python
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, MUET
setup()
canaux = ["Boutique", "Réseaux", "Site"]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
l = np.arange(3); w = 0.36
a24 = [evo.loc[c, 2024] / 1000 for c in canaux]; a25 = [evo.loc[c, 2025] / 1000 for c in canaux]
ax.bar(l - w / 2, a24, w, color=MUET, label="T4 2024"); ax.bar(l + w / 2, a25, w, color=BLEU, label="T4 2025")
for i, c in enumerate(canaux):
    ax.text(i + w / 2, a25[i] + 3, f"{(a25[i] / a24[i] - 1) * 100:+.0f} %".replace(".", ","), ha="center", fontsize=9, color=BLEU)
ax.set_xticks(l); ax.set_xticklabels(canaux); ax.set_ylabel("Chiffre d'affaires (k€)"); ax.set_ylim(0, 250); ax.legend(frameon=False, loc="upper center", ncol=2)
ax.set_title("Quatrième trimestre : 2025 contre 2024, par canal", loc="left")
fig.savefig("figures/ch10-synthese-t4.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("figure écrite")
```
<!--sortie-->
```text
figure écrite
```

![Chiffre d'affaires du quatrième trimestre par canal, 2024 et 2025, avec l'évolution en pourcentage.](figures/ch10-synthese-t4.png)

### P.9 Étape 8 : le message à la gérante

Le message tient en cinq lignes, chacune avec **un chiffre et sa base de comparaison**, plus ce que l'analyse ne dit pas. Voici la trame.

> **Objet : synthèse du quatrième trimestre 2025.**
> 1. Le chiffre d'affaires du trimestre est de *X* €, en hausse de *a* % sur le même trimestre de 2024 ; la plus forte hausse en euros vient du canal *Y*.
> 2. Le nombre de commandes progresse de *b* % ; le panier moyen est de *Z* € (calculé sur le total, pas sur la moyenne des canaux).
> 3. Le taux de retour est de *r* % ; il est plus élevé sur le Site.
> 4. La marge brute (hors taxe) représente *m* % du chiffre d'affaires hors taxe.
> 5. Les totaux ont été recoupés par SQL, pandas et R, et le classeur par LibreOffice : aucun écart.
>
> **Ce que cette analyse ne dit pas :** *pourquoi* les ventes ont évolué (promotions, saison, publicité : voir le volume III) ; si les clients reviendront ; la marge après frais de personnel et de livraison.

On remplit la trame **par le calcul**, pas à la main, pour éviter toute faute de recopie.

```python
t25, t24 = tot.loc[2025], tot.loc[2024]
site = syn[(syn["annee"] == 2025)].set_index("canal")
fr = lambda x, nd=1: f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
gain = (evo[2025] - evo[2024])
print(f"1) CA : {fr(t25['ca'], 0)} € ({fr((t25['ca'] / t24['ca'] - 1) * 100)} %) ; plus forte hausse en euros : {gain.idxmax()} (+{fr(gain.max(), 0)} €)")
print(f"2) Commandes : {fr((t25['commandes'] / t24['commandes'] - 1) * 100)} % ; panier moyen : {fr(t25['panier_moyen'], 2)} €")
print(f"3) Taux de retour : {fr(t25['retours'] / t25['lignes'] * 100)} % ; le plus élevé : {site['taux_retour'].idxmax()} ({fr(site['taux_retour'].max() * 100)} %)")
print(f"4) Taux de marge brute (HT) : {fr(syn[syn['annee'] == 2025]['marge'].sum() / (t25['ca'] / (1 + TVA)) * 100)} %")
```
<!--sortie-->
```text
1) CA : 447 800 € (14,6 %) ; plus forte hausse en euros : Site (+35 798 €)
2) Commandes : 9,7 % ; panier moyen : 99,25 €
3) Taux de retour : 6,4 % ; le plus élevé : Site (8,5 %)
4) Taux de marge brute (HT) : 38,3 %
```

### P.10 Les limites de l'étude

- **Une description, pas une explication.** Le tableau dit *ce qui s'est passé*, pas *pourquoi* ; la promotion, la saison et la publicité jouent ensemble (volume III).
- **Deux trimestres seulement.** Une évolution de quelques pour cent sur un trimestre peut être de la variation ordinaire ; on ne la compare pas à une tendance sur plusieurs années.
- **Hypothèses de marge.** La TVA est fictive et le coût d'achat est supposé constant ; les frais de livraison et de personnel ne sont pas comptés.
- **Taux de retour mesuré sur les lignes vendues** dans le trimestre, retours **comptés à la date de vente** ; les retours de décembre arrivent en janvier et sont **sous-estimés** pour les dernières semaines.
- **Données simulées.** La réalité apporte des cas que ce jeu ne contient pas (remboursements partiels, annulations, doublons de commandes).

### P.11 Variante : l'enquête de satisfaction

La même démarche s'applique à `donnees/enquete_satisfaction.csv` : **lire**, **nettoyer** (doublons, réponses trop rapides), **calculer** une satisfaction moyenne et un indicateur de recommandation (*Net Promoter Score*), puis **douter** (qui a répondu ?). Voici la version courte.

```python
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
n0 = len(enq)
enq = enq.drop_duplicates(subset=[c for c in enq.columns if c != "id_reponse"])
n1 = len(enq)
enq = enq[enq["duree_reponse_s"] >= 20]
print("réponses brutes :", n0, "| après doublons :", n1, "| après réponses trop rapides :", len(enq))
reco = enq["recommandation_0_10"]
nps = ((reco >= 9).mean() - (reco <= 6).mean()) * 100
print("satisfaction moyenne :", round(enq["satisfaction_globale"].mean(), 2), "| NPS :", round(nps, 1))
inv = pd.read_sql("select distinct id_client from commandes where date_commande >= '2025-01-01'", con)
print("clients invités :", len(inv), "| taux de réponse :", round(len(enq) / len(inv) * 100, 1), "%")
```
<!--sortie-->
```text
réponses brutes : 958 | après doublons : 931 | après réponses trop rapides : 897
satisfaction moyenne : 3.58 | NPS : -21.1
clients invités : 3875 | taux de réponse : 23.1 %
```

**Lecture.** Sur 958 lignes brutes, on retire 27 doublons puis 34 réponses remplies en moins de 20 secondes : il reste 897 réponses, pour 3 875 clients invités, soit un taux de réponse de 23,1 %. La satisfaction moyenne est de 3,58 sur 5 et le NPS de −21 points. **Attention** : ces chiffres décrivent les **répondants**, et rien ne garantit qu'ils ressemblent aux clients (chapitre 5, section 5.3) ; on ne les annonce pas comme « la satisfaction des clients ».

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des sections facultatives (➕ 1.5, 2.5, 2.6, 3.5, 3.6, 4.5, 4.6, 5.4, 5.5) comptent si vous les avez lues.

### Les essentiels de la statistique (chapitre 1)

1. Neuf commandes valent 20, 25, 30, 35, 40, 45, 50, 60 et 260 €. Calculez la moyenne et la médiane. Laquelle annoncez-vous à la gérante pour décrire « une commande typique », et pourquoi ?
2. Le premier quartile des paniers est de 20 € et le troisième de 40 €. Quels sont les seuils de la règle des 1,5 écart interquartile ? Une commande de 95 € est-elle « aberrante » ? Doit-on la supprimer ?
3. Le panier moyen vaut 100 € avec un écart-type de 40 €. Quel est le score z d'une commande de 180 € ? Si les paniers suivaient une loi normale, quelle proportion dépasserait 180 € ? Pourquoi cette réponse est-elle probablement fausse pour nos paniers ?
4. Le taux de retour est de 6 %. Sur 200 lignes vendues, combien de retours attend-on, avec quel écart-type ?
5. Un échantillon de 400 commandes donne un panier moyen de 100,4 € et un écart-type de 85 €. Donnez l'erreur type et un intervalle de confiance à 95 % de la moyenne.
6. Combien de personnes faut-il interroger pour estimer une proportion à plus ou moins 3 points, avec 95 % de confiance, dans le pire cas ?
7. La dépense publicitaire et le chiffre d'affaires sont corrélés (0,42), mais la corrélation tombe à presque rien à mois égal. Que s'est-il passé, et que conclure ?
8. Un prix augmente de 20 % puis baisse de 20 %. Le résultat est-il le prix initial ? Un taux de retour passe de 6 % à 8 % : de combien en points, et en pourcentage ? Quelle croissance annuelle moyenne mène de 100 à 121 en deux ans ?

### Excel (chapitre 2)

9. En `C2`, la formule `=B2*$F$1` est copiée vers le bas jusqu'en `C3`. Que devient-elle, et pourquoi le `$` ?
10. Écrivez la formule qui donne le chiffre d'affaires du canal « Site » depuis le 1er octobre 2025 à partir de la feuille `Lignes` (canal en colonne E, date en C, montant en M).
11. Citez deux pièges de `RECHERCHEV` et la fonction qui les évite.
12. La colonne `A` contient des numéros de ticket comme `T33133`. Comment extraire le nombre `33133` (en nombre, pas en texte) ?
13. Que renvoie `=FIN.MOIS(DATE(2025;11;15);0)` ? Et `=DATE(2025;11;15)+30` ?
14. Un tableau croisé dynamique n'affiche pas les ventes d'hier. Quelles sont les deux causes les plus fréquentes ?
15. Quelle structure de classeur sépare données, calculs et présentation ? Pourquoi éviter les cellules fusionnées dans une table de données ?
16. Qu'apportent les « étapes appliquées » de Power Query par rapport à un nettoyage fait à la main dans une feuille ?

### SQL (chapitre 3)

17. Pourquoi ne peut-on pas écrire `WHERE SUM(montant) > 1000` ? Quelle clause utiliser ?
18. Une colonne contient cinq valeurs : 10, 20, NULL, 30, NULL. Que valent `COUNT(*)`, `COUNT(colonne)` et `AVG(colonne)` ?
19. Combien de clients de la base n'ont **jamais** commandé ? Écrivez la requête.
20. On joint la table des jours (une ligne par jour, avec la dépense publicitaire) à la table des commandes (plusieurs par jour) puis on somme la dépense. Quel est le problème, et quelle est l'ampleur de l'erreur sur 2025 ?
21. Quatre produits ont des ventes de 90, 80, 80 et 70. Donnez `ROW_NUMBER`, `RANK` et `DENSE_RANK`.
22. Le chiffre d'affaires de trois mois vaut 100, 110 et 99. Quelle fonction fenêtre donne la variation par rapport au mois précédent ? Quelles valeurs ?
23. À quoi sert une CTE (`WITH`), et pourquoi vérifie-t-on un résultat SQL par un second outil ?
24. Pourquoi ne faut-il jamais construire une requête en collant du texte saisi par un utilisateur, et que faire à la place ?

### Python et R (chapitre 4)

25. Quelle est la différence entre `loc` et `iloc` ? Pourquoi les conditions combinées s'écrivent-elles `(a) & (b)` entre parenthèses ?
26. Quels arguments de lecture faut-il pour un fichier CSV français (point-virgule, virgule décimale, accents Windows) ?
27. En 2025, combien y a-t-il de lignes de commande et combien de commandes distinctes ? Quelle fonction pandas compte les commandes distinctes ?
28. Comment détecter, au moment de la jointure de deux tables avec pandas, qu'une clé est en double dans la table que l'on croit sans doublon ?
29. Traduisez en tidyverse : « garder les commandes du Site, ajouter le montant hors taxe, grouper par mois, sommer ».
30. Quand préfère-t-on le format large et quand le format long ? Quelles fonctions passent de l'un à l'autre en pandas et en R ?
31. Pourquoi un notebook qui « marche chez moi » peut-il ne pas se rejouer chez un collègue, et quelle habitude évite le problème ?
32. Pourquoi la vectorisation (NumPy, pandas, polars) est-elle préférable à une boucle Python sur les lignes ?

### Types de données, collecte et enquêtes (chapitre 5)

33. Classez par niveau de mesure : la note de satisfaction de 1 à 5, la ville, la température en °C, le chiffre d'affaires. Quelles opérations a-t-on le droit de faire sur chacune ?
34. Quel est le grain de la table `commandes` ? De la table `lignes_commande` ? Quel risque court-on en joignant les deux et en sommant une colonne de la première ?
35. Pourquoi lire un identifiant comme `007421` en texte ?
36. Seuls 24 % des clients invités ont répondu, avec une moyenne de 3,64. Entre quelles valeurs la moyenne de **tous** les clients peut-elle se situer, sans autre hypothèse ?
37. Sur 50 réponses de recommandation (0 à 10), 20 sont des 9 ou 10, 15 des 7 ou 8, et 15 des 0 à 6. Quel est le NPS ?
38. Combien de répondants pour une marge d'erreur de 3 points, et pour 2 points ?
39. Citez quatre biais d'enquête et un remède pour chacun.
40. Une API répond « 429 » : que signifie ce code et comment se comporter ? Pourquoi consulter `robots.txt` avant de collecter une page ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire. Les formules Excel sont vérifiées avec LibreOffice (Excel n'est pas installé) et recoupées par pandas.

```python
import numpy as np, pandas as pd, sqlite3, datetime as dt
from scipy.stats import norm

paniers = [20, 25, 30, 35, 40, 45, 50, 60, 260]
print("Q1  moyenne :", round(np.mean(paniers), 1), "| médiane :", np.median(paniers))
print("Q2  seuils :", 20 - 1.5 * 20, "et", 40 + 1.5 * 20)
print("Q3  z =", (180 - 100) / 40, "| P(> 180) si normal :", round(1 - norm.cdf(2), 4))
print("Q4  retours attendus :", 200 * 0.06, "| écart-type :", round(np.sqrt(200 * 0.06 * 0.94), 2))
se = 85 / np.sqrt(400)
print("Q5  erreur type :", round(se, 2), "| IC 95 % :", round(100.4 - 1.96 * se, 1), "à", round(100.4 + 1.96 * se, 1))
print("Q6  n =", round(1.96 ** 2 * 0.25 / 0.03 ** 2))
print("Q8  1,2 x 0,8 =", round(1.2 * 0.8, 2), "| 6 % -> 8 % :", 2, "points,", round((8 / 6 - 1) * 100, 1), "% | croissance annuelle :", round((1.21 ** 0.5 - 1) * 100, 1), "%")
print("Q36 bornes :", round(0.24 * 3.64 + 0.76 * 1, 2), "à", round(0.24 * 3.64 + 0.76 * 5, 2))
print("Q37 NPS :", (20 - 15) / 50 * 100, "points | Q38 n pour 3 points :", round(1.96 ** 2 * 0.25 / 0.03 ** 2), ", pour 2 points :", round(1.96 ** 2 * 0.25 / 0.02 ** 2))
```
<!--sortie-->
```text
Q1  moyenne : 62.8 | médiane : 40.0
Q2  seuils : -10.0 et 70.0
Q3  z = 2.0 | P(> 180) si normal : 0.0228
Q4  retours attendus : 12.0 | écart-type : 3.36
Q5  erreur type : 4.25 | IC 95 % : 92.1 à 108.7
Q6  n = 1067
Q8  1,2 x 0,8 = 0.96 | 6 % -> 8 % : 2 points, 33.3 % | croissance annuelle : 10.0 %
Q36 bornes : 1.63 à 4.67
Q37 NPS : 10.0 points | Q38 n pour 3 points : 1067 , pour 2 points : 2401
```

```python
con = sqlite3.connect("donnees/boutique.db")
print("Q18 COUNT(*), COUNT(col), AVG :", con.execute("with t(v) as (values (10),(20),(NULL),(30),(NULL)) select count(*), count(v), avg(v) from t").fetchone())
print("Q19 clients sans commande :", con.execute("select count(*) from clients c left join commandes o on o.id_client = c.id_client where o.id_commande is null").fetchone()[0])
juste = con.execute("select round(sum(depense_pub)) from jours_exploitation where date >= '2025-01-01'").fetchone()[0]
faux = con.execute("select round(sum(j.depense_pub)) from jours_exploitation j join commandes c on c.date_commande = j.date where j.date >= '2025-01-01'").fetchone()[0]
print("Q20 dépense 2025 :", juste, "€ | après jointure :", faux, "€ | rapport :", round(faux / juste, 1))
print("Q21", con.execute("with t(p, v) as (values ('a',90),('b',80),('c',80),('d',70)) select p, row_number() over (order by v desc), rank() over (order by v desc), dense_rank() over (order by v desc) from t").fetchall())
print("Q22", con.execute("with t(m, v) as (values (1,100.0),(2,110.0),(3,99.0)) select m, round(v / lag(v) over (order by m) - 1, 3) from t").fetchall())
print("Q27 lignes, commandes distinctes (2025) :", con.execute("select count(*), count(distinct c.id_commande) from commandes c join lignes_commande l using (id_commande) where c.date_commande >= '2025-01-01'").fetchone())
```
<!--sortie-->
```text
Q18 COUNT(*), COUNT(col), AVG : (5, 3, 20.0)
Q19 clients sans commande : 1194
Q20 dépense 2025 : 75995.0 € | après jointure : 2991731.0 € | rapport : 39.4
Q21 [('a', 1, 1, 1), ('b', 2, 2, 2), ('c', 3, 2, 2), ('d', 4, 4, 3)]
Q22 [(1, None), (2, 0.1), (3, -0.1)]
Q27 lignes, commandes distinctes (2025) : (29827, 12946)
```

```python
import sys, os, tempfile
sys.path.insert(0, "build")
import outils_xl as X
lignes = pd.read_excel("donnees/ventes_2025.xlsx", sheet_name="Lignes")
rows = [list(lignes.columns)] + [[(v.date() if isinstance(v, pd.Timestamp) else (None if pd.isna(v) else (v.item() if hasattr(v, "item") else v))) for v in r] for r in lignes.itertuples(index=False)]
f10 = '=SUMIFS(Lignes!M:M,Lignes!E:E,"Site",Lignes!C:C,">="&DATE(2025,10,1))'
calc = [[f10, "=EOMONTH(DATE(2025,11,15),0)", "=DATE(2025,11,15)+30", '=VALUE(MID("T33133",2,10))']]
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
res = X.valeurs(X.recalculer(X.classeur(os.path.join(dossier, "q.xlsx"), {"Calcul": calc, "Lignes": rows})), "Calcul")[0]
attendu = lignes[(lignes["canal"] == "Site") & (lignes["date_commande"] >= "2025-10-01")]["montant"].sum()
print("Q10 formule :", X.en_fr(f10))
print("Q10 LibreOffice :", round(res[0], 2), "| pandas :", round(attendu, 2))
serie = lambda n: n.date() if hasattr(n, 'date') else dt.date(1899, 12, 30) + dt.timedelta(days=int(n))      # numéro de série Excel -> date
print("Q12 STXT(...) :", res[3], "| Q13 FIN.MOIS :", serie(res[1]), "| +30 jours :", serie(res[2]))
```
<!--sortie-->
```text
Q10 formule : =SOMME.SI.ENS(Lignes!M:M;Lignes!E:E;"Site";Lignes!C:C;">="&DATE(2025;10;1))
Q10 LibreOffice : 211433.79 | pandas : 211433.79
Q12 STXT(...) : 33133 | Q13 FIN.MOIS : 2025-11-30 | +30 jours : 2025-12-15
```

**1.** Moyenne $62{,}8$ €, médiane **40 €** (code ci-dessus). On annonce la **médiane** : la commande de 260 € tire la moyenne vers le haut, alors que huit commandes sur neuf sont de 60 € ou moins. Une distribution asymétrique se décrit par la médiane, accompagnée des quartiles (1.1.1, 1.1.4).

**2.** Écart interquartile $=40-20=20$ ; seuils $20-1{,}5\times20=-10$ et $40+1{,}5\times20=70$. La commande de 95 € dépasse 70 € : elle est **signalée**, pas supprimée. On cherche d'abord si c'est une erreur de saisie ou un vrai gros achat ; une vraie valeur reste dans l'analyse (et se discute à part) (1.1.3).

**3.** $z=(180-100)/40=2$ : la commande est à deux écarts-types au-dessus de la moyenne. Pour une loi normale, la proportion au-dessus de $z=2$ vaut environ 2,3 %. Mais les paniers sont **asymétriques**, pas normaux : la règle ne s'applique pas, et il faut lire la distribution réelle (1.2.3, 1.2.4).

**4.** On attend $200\times0{,}06=12$ retours, avec un écart-type de $\sqrt{200\times0{,}06\times0{,}94}\approx3{,}4$ : trois ou quatre retours de plus ou de moins ne sont pas surprenants (1.2.2).

**5.** Erreur type $=85/\sqrt{400}=4{,}25$ € ; intervalle à 95 % $\approx100{,}4\pm1{,}96\times4{,}25$, soit de **92,1 à 108,7 €** (1.3.3).

**6.** $n=1{,}96^2\times0{,}25/0{,}03^2\approx1\,067$ répondants (le pire cas est $p=0{,}5$) (1.3.5).

**7.** La dépense publicitaire et les ventes montent **ensemble en novembre-décembre** : la **saison** est une variable de confusion. À mois égal, la corrélation devient presque nulle : le chiffre brut ne prouve pas que la publicité augmente les ventes, et il ne prouve pas non plus qu'elle n'a aucun effet. Pour le savoir, il faut une comparaison contrôlée ou une expérience (1.4.3, 1.4.6).

**8.** $1{,}2\times0{,}8=0{,}96$ : on perd **4 %**, le prix initial n'est pas retrouvé. Un taux de 6 % à 8 % est une hausse de **2 points**, soit **33 %** en valeur relative. De 100 à 121 en deux ans, le taux annuel moyen est de $\sqrt{1{,}21}-1=10\ \%$ (1.5.1, 1.5.2).

**9.** Elle devient `=B3*$F$1` : la référence `B2` est **relative** (elle suit la copie), `$F$1` est **absolue** (le taux reste ancré sur la même cellule) (2.1.2).

**10.** En français : `=SOMME.SI.ENS(Lignes!M:M;Lignes!E:E;"Site";Lignes!C:C;">="&DATE(2025;10;1))`. Résultat recalculé par LibreOffice : 211 433,79 €, identique à pandas (code ci-dessus) (2.1.4).

**11.** (1) La colonne cherchée doit être la **première à gauche** de la table ; (2) le numéro de colonne est écrit en dur et **casse** quand on insère une colonne ; (3) si l'on oublie le dernier argument, la correspondance est **approchée** et le résultat peut être faux sans erreur. `RECHERCHEX` (ou `INDEX` + `EQUIV`) évite ces pièges (2.1.6).

**12.** `=CNUM(STXT(A2;2;10))` : `STXT` extrait le texte à partir du deuxième caractère, `CNUM` le convertit en nombre. Résultat : 33133 (code ci-dessus) (2.1.7).

**13.** `FIN.MOIS` renvoie le **30/11/2025** ; ajouter 30 à une date donne le **15/12/2025** : une date est un nombre de jours (2.1.8).

**14.** (1) Le tableau croisé **n'a pas été actualisé** (il garde une copie des données) ; (2) sa **source** est une plage fixe qui n'inclut pas les nouvelles lignes, alors qu'un tableau structuré s'étendrait seul (2.2.5).

**15.** Trois étages : **données** brutes, **calculs**, **présentation**. Les cellules fusionnées cassent le tri, les filtres, les tableaux croisés et la copie de formules : dans une table de données, une ligne est une observation et une colonne une variable (2.4.1, 2.4.2).

**16.** Les étapes sont **enregistrées et rejouables** : on peut les relancer sur le fichier du mois suivant, les relire, les corriger et les expliquer. Un nettoyage manuel dans une feuille n'est ni reproductible ni traçable (2.3.1).

**17.** `WHERE` s'applique **avant** l'agrégation, à des lignes ; la somme n'existe pas encore. On filtre un agrégat avec **`HAVING`** (3.1.7).

**18.** `COUNT(*)` $=5$, `COUNT(colonne)` $=3$ (les `NULL` ne sont pas comptés) et `AVG(colonne)` $=20$ (moyenne de 10, 20 et 30 ; les `NULL` sont ignorés, pas traités comme des zéros) (3.1.8).

**19.** **1 194** clients. `SELECT COUNT(*) FROM clients c LEFT JOIN commandes o ON o.id_client = c.id_client WHERE o.id_commande IS NULL` : le `LEFT JOIN` garde tous les clients, le `IS NULL` retient ceux qui n'ont aucune commande (3.2.3).

**20.** La jointure de « un jour » avec « plusieurs commandes » **répète** la ligne du jour autant de fois qu'il y a de commandes ce jour-là ; la somme de la dépense est donc multipliée. Sur 2025 : 75 995 € devient 2 991 731 €, soit près de **39 fois** trop. On agrège **avant** de joindre, ou l'on joint des tables de même grain (3.2.6).

**21.** `ROW_NUMBER` : 1, 2, 3, 4 ; `RANK` : 1, 2, 2, 4 ; `DENSE_RANK` : 1, 2, 2, 3 (3.3.3).

**22.** `LAG` : $v/\text{LAG}(v)-1$ donne **+10 %** pour le deuxième mois et **−10 %** pour le troisième (code ci-dessus) (3.3.4).

**23.** Une CTE **nomme une étape** : la requête se lit de haut en bas, chaque étape se vérifie seule. On recoupe par un second outil parce qu'une jointure qui duplique, un filtre de dates décalé ou un arrondi fausse un total **sans erreur visible** (3.4.1, 3.4.2).

**24.** Du texte saisi peut contenir du SQL (**injection**) et modifier la requête, voire détruire des données. On utilise des **requêtes paramétrées** : la requête et les valeurs sont transmises séparément (3.5.7).

**25.** `loc` sélectionne par **étiquettes** (bornes incluses), `iloc` par **positions**. Les opérateurs `&`, `|` ont une priorité supérieure aux comparaisons : sans parenthèses, `a > 1 & b < 2` n'a pas le sens voulu, et `and`/`or` ne fonctionnent pas sur des colonnes entières (4.1.4, 4.1.5).

**26.** `sep=";"`, `decimal=","` et `encoding="cp1252"`, avec éventuellement `dtype` (identifiants en texte) et `parse_dates` (ou une conversion explicite avec le format `jj/mm/aaaa`) (4.1.3, 4.3.1).

**27.** **29 827** lignes de commande pour **12 946** commandes distinctes (code ci-dessus). En pandas : `nunique()` (ou `.drop_duplicates()` puis `len`) (4.3.2).

**28.** Avec `merge(..., validate="m:1")` : pandas lève une erreur si la clé de droite n'est pas unique. On peut aussi contrôler avant : `table["cle"].is_unique` ou `table.duplicated("cle").sum()` (4.3.3).

**29.** `cmd |> filter(canal == "Site") |> mutate(ca_ht = montant / 1.2) |> group_by(mois) |> summarise(ca = sum(ca_ht))` (4.2.3).

**30.** Le format **large** se lit bien (une colonne par mois) et convient aux tableaux de présentation ; le format **long** (une ligne par observation) convient au calcul, au filtrage et aux graphiques. En pandas : `melt` (large vers long), `pivot` ou `pivot_table` (long vers large) ; en R : `pivot_longer`, `pivot_wider` (4.3.4).

**31.** Un notebook garde un **état caché** : on peut exécuter les cellules dans le désordre, ou supprimer une cellule dont dépendent d'autres. L'habitude qui protège : **redémarrer et tout exécuter** de haut en bas avant de partager, avec des chemins relatifs et des données en entrée (4.4.2, 4.4.3).

**32.** La vectorisation applique l'opération **à toute la colonne** dans du code compilé ; une boucle Python répète l'interprétation ligne par ligne, ce qui est beaucoup plus lent sur des dizaines de milliers de lignes (4.6.1).

**33.** **Satisfaction de 1 à 5** : ordinal (compter, ordonner, médiane ; la moyenne est discutable). **Ville** : nominal (compter, mode). **Température en °C** : intervalle (différences et moyenne, mais 20 °C n'est pas « deux fois plus chaud » que 10 °C). **Chiffre d'affaires** : rapport (toutes les opérations, y compris les ratios) (5.1.2).

**34.** Le grain de `commandes` est **une commande** ; celui de `lignes_commande`, **une ligne de commande**. Joindre les deux puis sommer une colonne de `commandes` la **multiplie** par le nombre de lignes de chaque commande : c'est le double comptage (5.1.4, 3.2.6).

**35.** Un identifiant n'est pas une quantité : lu comme un nombre, `007421` devient `7421` et les zéros de tête sont perdus (et deux identifiants distincts peuvent se confondre). On lit les identifiants en **texte** (5.1.3).

**36.** Sans aucune hypothèse, la moyenne de tous les clients est entre $0{,}24\times3{,}64+0{,}76\times1\approx1{,}63$ (si tous les non-répondants étaient au plus bas) et $0{,}24\times3{,}64+0{,}76\times5\approx4{,}67$ : l'intervalle est très large, et c'est pourquoi on étudie **qui** a répondu (5.3.4).

**37.** Promoteurs (9–10) : $20/50=40\ \%$ ; détracteurs (0–6) : $15/50=30\ \%$ ; **NPS $=+10$ points** (les 7–8 sont « passifs » et ne comptent pas) (5.3.6).

**38.** **1 067** répondants pour ±3 points et **2 401** pour ±2 points, dans le pire cas : diviser la marge d'erreur par 1,5 coûte 2,25 fois plus de réponses (5.4.3).

**39.** Par exemple : **biais de sélection** (tirer au hasard dans la population) ; **non-réponse** (relancer, comparer répondants et invités, pondérer) ; **désirabilité sociale** (anonymat, formulation neutre) ; **formulation et ordre des questions** (test pilote, rotation de l'ordre). Aucune de ces corrections n'est parfaite (5.4.4).

**40.** Le code **429** signifie « trop de requêtes » : on a dépassé la **limite de débit**. On attend (en suivant l'en-tête `Retry-After` s'il existe), on espace les appels, et l'on réessaie avec un délai croissant. `robots.txt` indique ce que l'éditeur autorise aux programmes ; le consulter est une règle de **politesse** et de prudence juridique, à compléter par les conditions d'utilisation du site (5.5.2 à 5.5.4).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Résumer une variable : centre, dispersion, forme, valeurs aberrantes | 1.1 |
| Choisir une loi simple et lire une courbe normale | 1.2 |
| Mesurer l'erreur d'échantillonnage, calculer un intervalle de confiance | 1.3 |
| Lire une corrélation et la distinguer d'une causalité | 1.4 |
| Calculer pourcentages, croissances, moyennes pondérées, marges | 1.5 |
| Écrire des formules Excel (conditionnelles, recherche, texte, dates) | 2.1 |
| Construire un tableau croisé dynamique | 2.2 |
| Importer et transformer avec Power Query | 2.3 |
| Organiser un classeur fiable et le contrôler | 2.4 |
| Interroger une base : SELECT, WHERE, GROUP BY, HAVING | 3.1 |
| Joindre des tables sans doubler les lignes | 3.2 |
| Utiliser les fonctions fenêtres | 3.3 |
| Structurer une requête avec des CTE et la vérifier | 3.4 |
| Manipuler un DataFrame pandas | 4.1 |
| Faire la même chose avec le tidyverse | 4.2 |
| Lire, regrouper, joindre, restructurer des données | 4.3 |
| Livrer un notebook reproductible | 4.4 |
| Reconnaître les types et les niveaux de mesure, le grain d'une table | 5.1 |
| Choisir et évaluer une source de données | 5.2 |
| Concevoir une enquête et en corriger les biais | 5.3, 5.4 |
| Mener une première analyse de bout en bout | Projet du volume |
