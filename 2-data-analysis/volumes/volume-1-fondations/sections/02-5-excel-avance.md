## 2.5 ➕ Pour aller plus loin : Excel avancé

> 🧭 **Section complémentaire.** Elle présente ce qu'Excel sait faire au-delà de la feuille de calcul : un **modèle de données** relié (Power Pivot), un langage de **mesures** (DAX), l'**automatisation** (macros VBA, scripts Office), puis elle répond à la question qui conclut toute formation sur Excel : **quand faut-il le quitter ?** Aucun des composants de cette section n'a pu être exécuté sur la machine qui a produit le livre : les scripts DAX, VBA et Office Scripts sont **non exécutés** et leur syntaxe est **à vérifier** ; nous donnons à chaque fois le **résultat attendu**, calculé en pandas ou en SQL.

```python hide
import os, sys, sqlite3, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style as S
import outils_ch02 as O

S.setup()
L, P, C = O.charger_2025()
cmd = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
lig = pd.read_csv("donnees/lignes_commande.csv")
tout = lig.merge(cmd[["id_commande", "date_commande", "id_client", "canal"]], on="id_commande")
tout["annee"] = tout["date_commande"].dt.year
```

### 2.5.1 Power Pivot et le modèle de données

Un tableau croisé classique travaille sur **une seule table**. Or les données d'une entreprise sont réparties en plusieurs tables : les lignes de vente (les **faits**, des événements nombreux), le catalogue des produits et la liste des clients (les **dimensions**, des objets décrits une fois). Plutôt que d'ajouter des colonnes à la table des ventes par `RECHERCHEX` (2.1.6), Excel permet de **déclarer des relations** entre tables dans un **modèle de données** (le composant s'appelle *Power Pivot*), puis de construire un tableau croisé qui s'appuie sur plusieurs tables à la fois.

Une relation relie une colonne de la table des faits à la **clé** d'une dimension : `Lignes[id_produit]` vers `Produits[id_produit]`. Elle est de type **plusieurs à un** (plusieurs lignes de vente pour un produit). Pour qu'elle fonctionne, la clé du côté « un » doit être **unique** : c'est ce que la section 2.3.5 nous a appris à vérifier (le nom d'un produit ne l'est pas, son identifiant l'est).

```python hide-code
print("relation Lignes → Produits : identifiants du catalogue uniques :", bool(P["id_produit"].is_unique), "| lignes sans produit connu :", int((~L["id_produit"].isin(P["id_produit"])).sum()))
print("relation Lignes → Clients  : identifiants clients uniques :", bool(C["id_client"].is_unique), "| lignes sans client connu :", int((~L["id_client"].isin(C["id_client"])).sum()))
print("lignes de ventes :", O.fr(len(L)), "| produits :", len(P), "| clients :", O.fr(len(C)))
```
<!--sortie-->
```text
relation Lignes → Produits : identifiants du catalogue uniques : True | lignes sans produit connu : 0
relation Lignes → Clients  : identifiants clients uniques : True | lignes sans client connu : 0
lignes de ventes : 29 827 | produits : 120 | clients : 6 000
```

Les deux relations sont **saines** : les identifiants du côté « un » sont uniques, et aucune ligne de vente ne renvoie à un produit ou à un client inconnu (pas de ligne « orpheline »). C'est le **contrôle d'intégrité** que l'on fait avant de déclarer une relation : une clé en double ou une ligne orpheline faussent tous les résultats sans message.

```python hide
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.set_xlim(0, 10); ax.set_ylim(5.4, 0); ax.axis("off")
def table(x, y, w, titre, cols, couleur, cle=0):
    h = 0.5 + 0.34 * len(cols)
    ax.add_patch(plt.Rectangle((x, y), w, h, fc="white", ec=S.AXE, lw=1))
    ax.add_patch(plt.Rectangle((x, y), w, 0.42, fc=couleur, ec="none", alpha=0.25))
    ax.text(x + w / 2, y + 0.21, titre, ha="center", va="center", fontsize=9, weight="bold", color=S.ENCRE)
    for i, c in enumerate(cols):
        ax.text(x + 0.12, y + 0.65 + 0.34 * i, ("🔑 " if i == cle and False else "") + c, va="center", fontsize=7.6, color=S.ENCRE, weight="bold" if i == cle else "normal")
    return (x, y, w, h)
f = table(3.55, 0.3, 2.9, "Lignes (faits)", ["id_ligne", "id_produit", "id_client", "date_commande", "quantite", "montant"], S.BLEU)
p = table(0.15, 0.3, 2.7, "Produits", ["id_produit", "nom_produit", "categorie", "prix_vente", "cout_achat"], S.AQUA)
c = table(7.15, 0.3, 2.7, "Clients", ["id_client", "ville", "annee_naissance", "canal_acquisition", "fidelite"], S.ORANGE)
d = table(3.55, 3.45, 2.9, "Calendrier", ["date", "mois", "trimestre", "annee"], S.VIOLET)
for (x1, y1), (x2, y2) in [((2.85, 1.35), (3.55, 1.35)), ((7.15, 1.35), (6.45, 1.35)), ((5.0, 3.45), (5.0, 2.88))]:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=S.ENCRE2, lw=1.3))
for (x, y, t) in [(2.97, 1.15, "1"), (3.43, 1.15, "∞"), (7.03, 1.15, "1"), (6.57, 1.15, "∞"), (5.2, 3.3, "1"), (5.2, 3.0, "∞")]:
    ax.text(x, y, t, fontsize=8, color=S.ENCRE2, ha="center", va="center")
S.save(fig, "ch02-modele.png")
```
<!--sortie-->
```text
figure : ch02-modele.png
```

![Un modèle de données en étoile : au centre la table des faits (`Lignes`), autour d'elle les dimensions (`Produits`, `Clients`, `Calendrier`). Chaque flèche est une relation « plusieurs à un » (∞ côté faits, 1 côté dimension). Schéma dessiné avec matplotlib.](figures/ch02-modele.png)

Ce dessin s'appelle un **schéma en étoile**. Il a quatre avantages décisifs sur la table unique avec colonnes collées : le **catalogue n'est stocké qu'une fois** (on change un prix à un seul endroit) ; le modèle gère **bien plus de lignes** que la grille d'Excel, car il les stocke en mémoire de façon compressée ; il permet de **compter des valeurs distinctes** (le nombre de clients différents), ce qu'un champ calculé de tableau croisé ne sait pas faire (2.2.4) ; et il prépare le terrain aux **mesures** de la sous-section suivante. La table `Calendrier` est une dimension particulière : une ligne par jour, avec le mois, le trimestre et l'année, indispensable pour comparer des périodes.

### 2.5.2 Les mesures DAX

**DAX** (*Data Analysis Expressions*) est le langage des formules du modèle de données. Il ressemble aux formules d'Excel, mais fonctionne différemment : au lieu de calculer une cellule, on définit une **mesure**, un calcul qui se **réévalue dans chaque case du tableau croisé**, selon les filtres de cette case. La même mesure donne le chiffre d'affaires de toute l'année dans le total général et celui d'une catégorie dans la ligne de cette catégorie.

C'est la différence avec la **colonne calculée**, évaluée **ligne par ligne** à la création (comme une colonne de formules) et stockée. Règle simple : une colonne calculée sert à **décrire** une ligne (le coût unitaire d'une vente) ; une mesure sert à **agréger** (une somme, un ratio, une comparaison).

Voici les mesures dont la gérante a besoin, en DAX (non exécuté, syntaxe à vérifier selon votre version) :

```text
CA := SUM ( Lignes[montant] )
CA Site := CALCULATE ( [CA], Lignes[canal] = "Site" )
Marge := SUMX ( Lignes, Lignes[montant] - Lignes[quantite] * RELATED ( Produits[cout_achat] ) )
Marge % := DIVIDE ( [Marge], [CA] )
Clients distincts := DISTINCTCOUNT ( Lignes[id_client] )
Panier moyen := DIVIDE ( [CA], DISTINCTCOUNT ( Lignes[id_commande] ) )
CA N-1 := CALCULATE ( [CA], SAMEPERIODLASTYEAR ( Calendrier[date] ) )
Croissance := DIVIDE ( [CA] - [CA N-1], [CA N-1] )
```

Quelques lignes méritent une explication. `CALCULATE` **modifie le contexte de filtre** avant d'évaluer sa première expression : `CALCULATE([CA]; canal = "Site")` calcule le chiffre d'affaires **comme si** le tableau était filtré sur le Site, quelle que soit la case où on le place. `SUMX` **itère** sur chaque ligne de la table, calcule une expression (`RELATED` va chercher le coût dans la table `Produits` grâce à la relation), puis additionne : c'est le même calcul que le `SOMMEPROD` de la section 2.1.6. `DIVIDE` renvoie un résultat vide, au lieu d'une erreur, quand le dénominateur est nul. `SAMEPERIODLASTYEAR` décale le contexte de dates d'un an : c'est l'une des fonctions d'**intelligence temporelle**, qui exigent une table `Calendrier` complète, sans trou.

Les résultats attendus, calculés en pandas sur le même classeur (et sur toutes les années pour la comparaison avec 2024) :

```python hide-code
ca = L["montant"].sum()
mm = L.merge(P[["id_produit", "cout_achat"]], on="id_produit")
marge = (mm["montant"] - mm["quantite"] * mm["cout_achat"]).sum()
ca24 = tout.loc[tout["annee"] == 2024, "montant"].sum(); ca25 = tout.loc[tout["annee"] == 2025, "montant"].sum()
print("CA                :", O.fr(ca))
print("CA Site           :", O.fr(L.loc[L["canal"] == "Site", "montant"].sum()))
print("Marge             :", O.fr(marge))
print("Marge %           :", O.fr(marge / ca * 100), "%")
print("Clients distincts :", O.fr(L["id_client"].nunique()))
print("Panier moyen      :", O.fr(ca / L["id_commande"].nunique()), "€ (", O.fr(L["id_commande"].nunique()), "commandes)")
print("CA N-1 (2024)     :", O.fr(ca24))
print("Croissance        :", O.fr((ca25 / ca24 - 1) * 100), "%")
```
<!--sortie-->
```text
CA                : 1 324 763,72
CA Site           : 617 715,45
Marge             : 639 810,88
Marge %           : 48,30 %
Clients distincts : 3 875
Panier moyen      : 102,33 € ( 12 946 commandes)
CA N-1 (2024)     : 1 189 461,17
Croissance        : 11,38 %
```

On lit : un chiffre d'affaires de 1 324 763,72 €, dont 617 715,45 € sur le Site ; une marge de 639 810,88 €, soit **48,30 %** du chiffre d'affaires ; **3 875** clients distincts ; un **panier moyen de 102,33 €** sur 12 946 commandes ; et une **croissance de 11,4 %** par rapport à 2024 (1 189 461,17 €). Remarquez que `Marge %` est un **ratio de sommes**, par construction (2.2.4) : c'est le comportement voulu d'une mesure, et c'est ce qui la distingue d'une moyenne de ratios. Chaque mesure s'adapte ensuite **au contexte du tableau** : placée dans un tableau croisé par catégorie, `Marge %` donne le taux de chaque catégorie, avec une seule définition.

> ⚠️ **Piège.** Le contexte de filtre est la notion la plus difficile de DAX, et la source des erreurs : une mesure qui donne un bon résultat dans le total peut en donner un faux dans une case, parce qu'un filtre d'une autre table s'y propage (ou ne s'y propage pas). **Testez chaque mesure sur un cas que vous savez calculer à la main**, comme nous l'avons fait ici avec pandas.

### 2.5.3 Macros VBA et scripts Office

Une **macro** enregistre une suite de gestes (mise en forme, copie, tri…) et la rejoue sur demande. Excel peut l'enregistrer pendant que vous travaillez, et la traduit en code **VBA** (*Visual Basic for Applications*). Un classeur qui contient des macros doit être enregistré au format `.xlsm`, que les messageries et les politiques de sécurité accueillent avec méfiance, à juste titre : les macros peuvent faire n'importe quoi sur votre poste.

Voici une macro minimale (non exécutée) qui actualise toutes les connexions de données puis exporte la feuille de présentation en PDF :

```text
Sub PublierRapport()
    ThisWorkbook.RefreshAll                         ' actualise requêtes et tableaux croisés
    Application.CalculateUntilAsyncQueriesDone      ' attend la fin des requêtes
    Sheets("Présentation").ExportAsFixedFormat Type:=xlTypePDF, _
        Filename:=ThisWorkbook.Path & "\rapport_" & Format(Date, "yyyy-mm-dd") & ".pdf"
End Sub
```

Les **Office Scripts** (Excel pour le web, scénarios automatisés par Power Automate) jouent le même rôle avec un langage différent, TypeScript :

```text
function main(workbook: ExcelScript.Workbook) {
    const feuille = workbook.getWorksheet("Données");
    const plage = feuille.getUsedRange();
    console.log("lignes :", plage.getRowCount());
}
```

Le premier script (VBA) tourne sur le poste, le second dans le nuage. Retenez trois principes. **Une macro ne remplace pas une formule** : tout ce qu'une formule fait, elle le fait de façon visible et recalculable, une macro non. **Toute macro doit être documentée**, car personne ne peut la relire dans l'interface d'Excel. Et **ne faites pas confiance aux macros reçues** : désactivez-les par défaut.

### 2.5.4 Quand quitter Excel : SQL ou Python ?

Excel est le bon outil dans beaucoup de situations, et le mauvais dans d'autres. Les signaux qui disent « il faut changer d'outil » sont assez nets :

| Signal | Pourquoi Excel peine | Alternative |
|---|---|---|
| Plus d'un million de lignes (ou plus de quelques centaines de milliers avec des formules) | limite de la grille, lenteur, fichier énorme | base de données et SQL (chapitre 3) |
| La même opération chaque semaine, avec plusieurs étapes | gestes à la main, erreurs | Power Query, ou un script Python |
| Plusieurs personnes modifient en même temps | conflits de versions | base partagée, dépôt de code |
| Il faut pouvoir **prouver** et **rejouer** l'analyse | formules dispersées, pas d'historique | script versionné, notebook (chapitre 4) |
| Calculs statistiques évolués (modèles, simulations) | fonctions limitées | Python ou R |

Une dernière illustration, pour **trianguler** : le chiffre d'affaires du Site en 2025, calculé trois fois, avec trois outils indépendants (la formule du tableur, une requête SQL sur la base, pandas).

```python
con = sqlite3.connect("donnees/boutique.db")
sql = """SELECT ROUND(SUM(l.montant), 2) FROM lignes_commande l JOIN commandes c ON c.id_commande = l.id_commande
         WHERE c.canal = 'Site' AND c.date_commande >= '2025-01-01'"""
print("SQL :", con.execute(sql).fetchone()[0])
print("pandas :", round(L.loc[L["canal"] == "Site", "montant"].sum(), 2))
```
<!--sortie-->
```text
SQL : 617715.45
pandas : 617715.45
```

Les deux donnent **617 715,45 €**, exactement le résultat de `SOMME.SI.ENS` de la section 2.1.4. Trois outils, un seul chiffre : c'est ce qui permet de s'y fier. Le chapitre suivant apprend à écrire cette requête SQL de zéro.

> ✅ **À retenir.**
> - Un **modèle de données** relie des tables par des clés **uniques** côté « un » ; contrôlez l'intégrité (clés uniques, pas de lignes orphelines) avant de déclarer une relation.
> - Une **mesure DAX** s'évalue dans chaque case selon son contexte de filtre ; une colonne calculée est évaluée ligne par ligne. `CALCULATE` modifie le contexte ; un ratio de mesures est un **ratio de sommes**.
> - Une **macro** automatise mais ne se lit pas comme une formule : documentez-la, méfiez-vous de celles qu'on vous envoie.
> - **Changez d'outil** quand les données dépassent la grille, quand le traitement doit être rejoué sans personne, ou quand il faut le prouver : SQL, Python, Power Query.
> - **Triangulez** : un même chiffre obtenu par trois outils (ici 617 715,45 €) est un chiffre fiable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.
