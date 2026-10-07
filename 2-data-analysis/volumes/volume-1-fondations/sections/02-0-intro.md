# Chapitre 2 : Excel

> « Le tableur est le premier outil de la plupart des analystes, et le dernier dont ils se méfient. »

La gérante de la boutique ouvre un classeur Excel tous les lundis matin. Elle y colle l'export des ventes de la semaine, recalcule à la main les totaux par catégorie, les compare à ceux du mois précédent, puis recopie les chiffres dans un tableau qu'elle envoie à son associé. Elle vous pose aujourd'hui la question que se posent tous les gens qui travaillent ainsi :

> « Peux-tu me dire, **par catégorie et par mois, ce que nous avons vendu en 2025**, sans que je refasse le calcul à la main chaque lundi ? Et peux-tu faire en sorte que je puisse **me fier** aux chiffres ? »

La seconde phrase compte autant que la première. Un tableur est un outil extraordinaire de rapidité : en quelques minutes, on obtient un tableau, un graphique, un chiffre. C'est aussi un outil sans garde-fou : une formule recopiée sur une plage trop courte, un nombre stocké comme du texte, une cellule fusionnée, un total qui ignore les dernières lignes, et personne ne le voit. Ce chapitre vous apprend à la fois **à aller vite** (formules, tableaux croisés dynamiques, Power Query) et **à vérifier** (contrôles, recoupements, bonnes pratiques de structure).

> ⚠️ **Honnêteté sur les outils.** Le livre a été produit sur une machine **sans Excel**. Voici ce que cela change pour vous :
> - **Les formules sont vérifiées**, mais avec **LibreOffice Calc**, un tableur libre qui lit les fichiers Excel (`.xlsx`) et calcule les mêmes fonctions. Chaque résultat chiffré du chapitre a été calculé ainsi, puis **recoupé par un second outil** (pandas ou SQL). LibreOffice et Excel peuvent différer sur des fonctions récentes ou des détails d'affichage : les cas connus sont signalés.
> - **Les formules sont écrites comme dans l'Excel en français** (`SOMME.SI.ENS`, séparateur `;`, virgule décimale). Un tableau de correspondance avec les noms anglais figure en section 2.1.10.
> - **Les « copies d'écran » sont des maquettes dessinées** avec un programme de dessin : elles montrent ce que vous verrez à l'écran, avec des valeurs réellement calculées, mais ce **ne sont pas des captures d'Excel**. Les menus, les libellés et les icônes varient selon la **version** d'Excel et la **langue** : traitez nos descriptions de menus comme des repères, **à vérifier** sur votre poste.
> - **Ce qui n'a pas pu être exécuté** : les tableaux croisés dynamiques réels, Power Query, Power Pivot et le langage DAX, VBA, Office Scripts, Google Sheets et Looker Studio. Ces blocs sont signalés « non exécuté » ; quand c'est possible, le même résultat est **recalculé en pandas ou en SQL** pour que vous puissiez vérifier ce que l'outil devrait donner.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 2.1 | Comment calculer, chercher et nettoyer avec des formules ? | Références, fonctions conditionnelles, recherches, dates, texte, erreurs |
| 2.2 | Comment résumer 30 000 lignes en un tableau ? | Le tableau croisé dynamique, et pourquoi il faut le recouper |
| 2.3 | Comment importer et nettoyer un export désordonné ? | Power Query : des étapes enregistrées et rejouables |
| 2.4 | Comment ne pas se tromper ? | Structure, données propres, contrôles, erreurs célèbres |
| ➕ 2.5 | Que fait Excel au-delà du tableur ? | Modèle de données, DAX, macros, et quand passer à SQL ou Python |
| ➕ 2.6 | Et dans le nuage ? | Google Sheets, Looker Studio, équivalences |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a1.py`) : la boutique, ses clients et ses ventes n'existent pas. La « vérité » du simulateur est documentée en tête du générateur ; nous n'en avons pas besoin ici, mais elle nous permet de savoir que les totaux sont exacts.

- **`ventes_2025.xlsx`**, le classeur de la gérante, contient trois feuilles : `Lignes` (une ligne par article vendu en 2025), `Produits` (le catalogue) et `Clients`.
- **`export_caisse_brut.csv`** est un export de caisse de la boutique physique, tel que la caisse le fournit : désordonné, avec un titre, un total et des formats « à la française ». Il sert à la section 2.3.
- Les autres fichiers du volume (`commandes.csv`, `boutique.db`…) servent dans les chapitres suivants ; nous les utilisons ici pour **recouper** les résultats.

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
xl = pd.read_excel("donnees/ventes_2025.xlsx", sheet_name=None)
print("feuilles :", {k: v.shape for k, v in xl.items()})
print("classeur identique au CSV :", bool(np.isclose(xl["Lignes"]["montant"].sum(), L["montant"].sum())) and bool((xl["Lignes"]["id_ligne"].values == L["id_ligne"].values).all()))
print("lignes", len(L), "| commandes", L["id_commande"].nunique(), "| clients", L["id_client"].nunique(), "| montant", round(L["montant"].sum(), 2))
print("période", L["date_commande"].min().date(), L["date_commande"].max().date(), "| produits", len(P), "| clients du fichier", len(C))
print("codes promo vides :", int(L["code_promo"].isna().sum()), "| taille du fichier (Mo) :", round(os.path.getsize("donnees/ventes_2025.xlsx") / 1e6, 2))
```
<!--sortie-->
```text
feuilles : {'Lignes': (29827, 13), 'Produits': (120, 6), 'Clients': (6000, 5)}
classeur identique au CSV : True
lignes 29827 | commandes 12946 | clients 3875 | montant 1324763.72
période 2025-01-01 2025-12-31 | produits 120 | clients du fichier 6000
codes promo vides : 25221 | taille du fichier (Mo) : 1.75
```

Le classeur de la gérante compte **29 827 lignes** de ventes, réparties en 12 946 commandes passées par 3 875 clients, du 1ᵉʳ janvier au 31 décembre 2025, pour un montant total de **1 324 763,72 €**. La figure suivante montre ce que la gérante voit en ouvrant la feuille `Lignes`.

```python hide
cols = ["id_ligne", "id_commande", "date_commande", "canal", "code_promo", "nom_produit", "categorie", "quantite", "montant"]
lettres = ["A", "B", "C", "E", "F", "H", "I", "J", "M"]           # colonnes D, G, K et L masquées dans la maquette
v = L.head(8)[cols].copy()
lignes_maq = [cols] + [[(None if (isinstance(x, float) and np.isnan(x)) else x) for x in r] for r in v.itertuples(index=False)]
O.maquette("figures/ch02-classeur.png", lignes_maq, lettres=lettres, largeurs=[8, 11, 14, 9, 10, 18, 11, 8, 8], active="M2", formule="24,62",
           onglets=("Lignes", "Produits", "Clients"), surligne=["A1:M1"])
print("figure : ch02-classeur.png")
```
<!--sortie-->
```text
figure : ch02-classeur.png
```

![La feuille `Lignes` de `ventes_2025.xlsx` : une ligne par article vendu, une colonne par caractéristique (les colonnes D, G, K et L sont masquées pour que la figure reste lisible). Maquette dessinée avec matplotlib, pas une capture d'Excel.](figures/ch02-classeur.png)

Remarquez déjà trois choses, que tout analyste vérifie en ouvrant un classeur inconnu. **Une ligne d'en-tête** unique, sans cellule fusionnée. **Une ligne = une observation** (ici, un article vendu). **Des colonnes homogènes** : une colonne de dates ne contient que des dates, une colonne de montants que des montants. C'est la forme que les outils d'analyse attendent, et nous y reviendrons en section 2.4.2. Les cellules vides de la colonne `code_promo` ne sont pas une erreur : elles signifient « pas de code promo » (25 221 lignes sur 29 827).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1 (explorer et contrôler le classeur).
