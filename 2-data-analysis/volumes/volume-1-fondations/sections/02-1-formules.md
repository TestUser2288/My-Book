## 2.1 Formules et fonctions

Une formule Excel est un **petit programme** que l'on écrit dans une cellule : elle commence par `=`, elle lit d'autres cellules et elle affiche un résultat qui se **met à jour tout seul** quand ces cellules changent. Cette section présente les familles de fonctions dont un analyste se sert tous les jours : agréger sous conditions, décider, chercher, nettoyer du texte, manipuler des dates, et comprendre les erreurs. Tous les résultats cités ont été calculés sur le classeur `ventes_2025.xlsx` et **recoupés par pandas** : le bloc suivant (caché dans le livre) le fait une fois pour toutes, et nous n'y reviendrons que pour citer les chiffres.

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
n = len(L) + 1                                   # dernière ligne de données dans la feuille Lignes
R = lambda c: f"Lignes!{c}2:{c}{n}"
F = {
 "total": f"=SUM({R('M')})",
 "recalc": f"=SUMPRODUCT({R('J')},{R('K')},1-{R('L')}/100)",
 "site": f'=SUMIFS({R("M")},{R("E")},"Site")',
 "boutique": f'=SUMIFS({R("M")},{R("E")},"Boutique")',
 "reseaux": f'=SUMIFS({R("M")},{R("E")},"Réseaux")',
 "nb_promo": f'=COUNTIFS({R("L")},">0")',
 "moy_jardin": f'=AVERAGEIFS({R("M")},{R("I")},"Jardin")',
 "jardin_mars": f'=SUMIFS({R("M")},{R("I")},"Jardin",{R("C")},">="&DATE(2025,3,1),{R("C")},"<"&DATE(2025,4,1))',
 "bougie": f'=SUMIF({R("H")},"Bougie*",{R("M")})',
 "site_deco_nov": f'=COUNTIFS({R("E")},"Site",{R("I")},"Décoration",{R("C")},">="&DATE(2025,11,1))',
 "sans_code": f'=COUNTBLANK({R("F")})',
 "plage_courte": f"=SUM(Lignes!M2:M{n-800})",
 "inegales": f'=SUMIFS({R("M")},Lignes!E2:E{n-10},"Site")',
 "gros": f'=COUNTIFS({R("M")},">=100")',
 "tab_total": "=SUM(Ventes[montant])",
 "tab_site": '=SUMIFS(Ventes[montant],Ventes[canal],"Site")',
 "nomme": "=SUM(Montant)",
 "marge": f"=SUM({R('M')})-SUMPRODUCT({R('J')},Lignes!N2:N{n})",
 "marge_jardin": f'=SUMPRODUCT(({R("I")}="Jardin")*({R("M")}-{R("J")}*Lignes!N2:N{n}))',
 "uniq": f"=COUNTA(UNIQUE({R('I')}))",
 "filt": f'=SUM(FILTER({R("M")},{R("E")}="Site"))',
 "let": f"=LET(_xlpm.a,SUM({R('M')}),_xlpm.b,COUNTA({R('A')}),ROUND(_xlpm.a/_xlpm.b,2))",
 "serial_n": "=DATE(2025,1,1)*1", "jsem": '=TEXT(DATE(2025,11,3),"dddd")', "mois_txt": '=TEXT(DATE(2025,3,15),"mmmm")',
 "fin_mois": "=EOMONTH(DATE(2025,2,10),0)", "decale": "=EDATE(DATE(2025,1,31),1)",
 "dif_m": '=DATEDIF(DATE(2025,1,15),DATE(2025,11,3),"M")', "dif_j": '=DATEDIF(DATE(2025,1,15),DATE(2025,11,3),"D")',
 "ouvres": "=NETWORKDAYS(DATE(2025,11,3),DATE(2025,11,9))", "wd": "=WEEKDAY(DATE(2025,11,3),2)", "datev": '=DATEVALUE("11/03/2025")',
 "texte_date_somme": "=SUM(Dates!A1:A2)", "texte_date_val": "=SUMPRODUCT(DATEVALUE(Dates!A1:A2))",
 "div0": "=1/0", "na": '=VLOOKUP("zz",Produits!A2:B121,2,FALSE)', "val": '="a"+1', "ref": "=INDEX(Produits!A:A,2000000)", "nom": "=NOMINCONNU(1)",
 "iferr": '=IFERROR(1/0,"n/a")',
 "vl_exact": "=VLOOKUP(7,Produits!A2:F121,2,FALSE)", "vl_faux_tri": "=VLOOKUP(5,Ref!A2:B5,2,TRUE)", "vl_exact_tri": "=VLOOKUP(5,Ref!A2:B5,2,FALSE)",
 "vl_espace": "=VLOOKUP(Ref!G2,Ref!E2:F5,2,FALSE)", "vl_trim": "=VLOOKUP(TRIM(Ref!G2),Ref!E2:F5,2,FALSE)",
 "idx": "=INDEX(Produits!B2:B121,MATCH(7,Produits!A2:A121,0))", "xl": '=XLOOKUP(7,Produits!A2:A121,Produits!B2:B121,"absent")',
 "xl_abs": '=XLOOKUP(999,Produits!A2:A121,Produits!B2:B121,"absent")', "xl_inv": '=XLOOKUP("Bol design",Produits!B2:B121,Produits!A2:A121,"absent")',
 "bareme": "=VLOOKUP(4,Bareme!A2:B4,2,TRUE)",
 "g_C3": "=Grille!C3", "g_D4": "=Grille!D4",
 "t_droite": "=VALUE(RIGHT(Texte!A2,LEN(Texte!A2)-1))", "t_prop": "=PROPER(TRIM(Texte!B2))", "t_gauche": "=LEFT(Texte!A2,1)", "t_stxt": "=MID(Texte!C2,1,3)",
 "t_len": "=LEN(Texte!B2)", "t_concat": '=CONCAT(Texte!A2,"-",Texte!D2)', "t_join": '=TEXTJOIN(" | ",TRUE,TRIM(Texte!B2),TRIM(Texte!B3),TRIM(Texte!B4))',
 "t_sub": '=SUBSTITUTE(Texte!E2,",",".")', "t_val": "=VALUE(Texte!E2)", "t_find": '=FIND("-",Texte!F2)',
 "si1": '=IF(Panier!A2>=100,"gros",IF(Panier!A2>=40,"moyen","petit"))', "si2": '=IF(Panier!A3>=100,"gros",IF(Panier!A3>=40,"moyen","petit"))',
 "si3": '=IF(Panier!A4>=100,"gros",IF(Panier!A4>=40,"moyen","petit"))', "si4": '=IF(Panier!A5>=100,"gros",IF(Panier!A5>=40,"moyen","petit"))',
 "ifs": '=IFS(Panier!A4>=100,"gros",Panier!A4>=40,"moyen",TRUE,"petit")', "et": "=AND(Panier!A4>=40,Panier!A4<100)", "ou": "=OR(Panier!A2>=100,Panier!A5>=100)",
 "sierr": "=IFERROR(Panier!A6/Panier!B6,0)", "div_b": "=Panier!A6/Panier!B6",
}
extra = {
 "Ref": [["id", "nom", "", "", "produit", "code", "clé tapée"], [7, "Moule mat", None, None, "Bol design", 3, "Bol design "], [3, "Bol design"], [12, "Poêle mat"], [5, "Cadre design"]],
 "Grille": [[None, 1, 2, 3], [1, "=B$1*$A2", "=C$1*$A2", "=D$1*$A2"], [2, "=B$1*$A3", "=C$1*$A3", "=D$1*$A3"], [3, "=B$1*$A4", "=C$1*$A4", "=D$1*$A4"]],
 "Dates": [["03/11/2025"], ["11/03/2025"]],
 "Bareme": [["quantité min", "remise"], [1, 0], [3, 0.05], [10, 0.1]],
 "Texte": [["ticket", "article", "code", "n", "valeur", "ref"], ["T33133", " bOÎTE rustique  ", "abcdef", "77", " 12,5", "a-b"], [None, "  moule MAT"], [None, "Plaid  NORDIQUE"]],
 "Panier": [["montant", "qte"], [12, 1], [45, 2], [99.9, 1], [150, 1], [320, 0], [None, 3]],
}
res = O.evaluer(F, {"Lignes": L, "Produits": P}, noms={"Montant": f"=Lignes!$M$2:$M${n}"}, extra=extra,
                colonnes={"Lignes": {"cout_u": "=XLOOKUP(G{r},Produits!A:A,Produits!E:E)"}}, tables={"Lignes": "Ventes"})
# recoupements pandas (tous doivent être égaux à LibreOffice, au centime près)
M = L.merge(P[["id_produit", "cout_achat"]], on="id_produit")
M["marge"] = M["montant"] - M["quantite"] * M["cout_achat"]
d1, d2 = pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-01")
controles = {
 "total": L["montant"].sum(), "recalc": (L["quantite"] * L["prix_unitaire"] * (1 - L["remise_pct"] / 100)).sum(),
 "site": L.loc[L["canal"] == "Site", "montant"].sum(), "boutique": L.loc[L["canal"] == "Boutique", "montant"].sum(), "reseaux": L.loc[L["canal"] == "Réseaux", "montant"].sum(),
 "nb_promo": (L["remise_pct"] > 0).sum(), "moy_jardin": L.loc[L["categorie"] == "Jardin", "montant"].mean(),
 "jardin_mars": L.loc[(L["categorie"] == "Jardin") & (L["date_commande"] >= d1) & (L["date_commande"] < d2), "montant"].sum(),
 "bougie": L.loc[L["nom_produit"].str.startswith("Bougie"), "montant"].sum(),
 "site_deco_nov": ((L["canal"] == "Site") & (L["categorie"] == "Décoration") & (L["date_commande"] >= "2025-11-01")).sum(),
 "sans_code": L["code_promo"].isna().sum(), "plage_courte": L["montant"].iloc[:n - 800 - 1].sum(), "gros": (L["montant"] >= 100).sum(),
 "tab_total": L["montant"].sum(), "tab_site": L.loc[L["canal"] == "Site", "montant"].sum(), "nomme": L["montant"].sum(),
 "marge": M["marge"].sum(), "marge_jardin": M.loc[M["categorie"] == "Jardin", "marge"].sum(), "uniq": L["categorie"].nunique(),
 "filt": L.loc[L["canal"] == "Site", "montant"].sum(), "let": round(L["montant"].sum() / len(L), 2),
 "serial_n": (pd.Timestamp("2025-01-01") - pd.Timestamp("1899-12-30")).days,
 "fin_mois": (pd.Timestamp("2025-02-28") - pd.Timestamp("1899-12-30")).days, "dif_j": (pd.Timestamp("2025-11-03") - pd.Timestamp("2025-01-15")).days,
 "datev": (pd.Timestamp("2025-03-11") - pd.Timestamp("1899-12-30")).days,
}
ecarts = {k: abs(float(res[k]) - float(v)) for k, v in controles.items()}
print("recoupements Excel/LibreOffice contre pandas :", len(ecarts), "formules, écart maximal", round(max(ecarts.values()), 6))
print("rentabilité : marge", round(res["marge"], 2), "dont Jardin", round(res["marge_jardin"], 2))
print("tableau structuré = plage : ", bool(np.isclose(res["tab_total"], res["total"])), "| plage nommée = plage :", bool(np.isclose(res["nomme"], res["total"])))
print("écart du recalcul ligne par ligne :", round(res["total"] - res["recalc"], 4))
```
<!--sortie-->
```text
recoupements Excel/LibreOffice contre pandas : 25 formules, écart maximal 0.0
rentabilité : marge 639810.88 dont Jardin 171875.43
tableau structuré = plage :  True | plage nommée = plage : True
écart du recalcul ligne par ligne : 0.0805
```

### 2.1.1 Anatomie d'un classeur et d'une formule

Un **classeur** (le fichier `.xlsx`) contient des **feuilles** ; une feuille est une grille de **cellules** repérées par une lettre (la colonne) et un numéro (la ligne) : `M2` est la cellule de la colonne M, ligne 2. Une **plage** désigne un rectangle de cellules : `M2:M29828` est la colonne des montants, de la ligne 2 à la ligne 29828. Pour parler d'une cellule d'une autre feuille, on préfixe : `Lignes!M2`.

Une cellule contient soit une **valeur** (un nombre, un texte, une date), soit une **formule**. Pour calculer le montant d'une ligne de vente, la formule est `=J2*K2*(1-L2/100)` : le prix unitaire, multiplié par la quantité, multiplié par un moins la remise exprimée en pourcentage. Excel applique les règles de priorité de l'arithmétique : d'abord les parenthèses, puis les pourcentages et les puissances, puis les multiplications et divisions, puis les additions et soustractions, puis la concaténation de texte (`&`), enfin les comparaisons (`=`, `<>`, `<`, `>=`…). **Dans le doute, mettez des parenthèses** : elles ne coûtent rien et se lisent mieux.

Quand vous modifiez une cellule, Excel **recalcule** toutes les formules qui en dépendent (le mode par défaut est le calcul automatique ; la touche `F9` force un recalcul en mode manuel). C'est ce qui fait la force du tableur, et c'est aussi ce qui le rend dangereux : un changement oublié se propage sans bruit.

Faisons le calcul sur toute l'année. Si l'on recalcule chaque ligne par `prix × quantité × (1 − remise)` puis que l'on additionne, on trouve un total **légèrement différent** de la somme de la colonne `montant` :

```python hide-code
O.montrer(res, [("total", F["total"]), ("recalc", F["recalc"])], nd=4)
print("écart :", O.fr(res["total"] - res["recalc"], 4), "€ sur", O.fr(len(L)), "lignes")
```
<!--sortie-->
```text
=SOMME(Lignes!M2:M29828)  →  1 324 763,7200
=SOMMEPROD(Lignes!J2:J29828;Lignes!K2:K29828;1-Lignes!L2:L29828/100)  →  1 324 763,6395
écart : 0,0805 € sur 29 827 lignes
```

L'écart est de **8 centimes** pour 29 827 lignes : la colonne `montant` est arrondie au centime **ligne par ligne** (c'est ce que fait une caisse), alors que le recalcul additionne des produits non arrondis. Ce n'est pas une erreur, mais c'est la première leçon de rigueur : **une somme de valeurs arrondies n'est pas l'arrondi de la somme**. Nous retrouverons ce phénomène en section 2.4.5.

> 💡 **Intuition.** Une formule ne « contient » pas son résultat : elle contient une **recette**. Si vous copiez la recette sur une autre ligne, Excel adapte les ingrédients à la nouvelle ligne. C'est le sujet de la sous-section suivante.

### 2.1.2 Références relatives, absolues et mixtes

Quand on copie la formule `=J2*K2` de la ligne 2 vers la ligne 3, Excel écrit `=J3*K3` : la référence est **relative**, elle se décale avec la formule. Pour qu'une référence **ne bouge pas**, on la fige avec des dollars : `$A$1` est **absolue** (ni la colonne ni la ligne ne changent), `$A1` est **mixte** (la colonne est figée, la ligne se décale) et `A$1` est mixte dans l'autre sens. La touche `F4` fait défiler ces quatre variantes.

| Écriture | Copiée une ligne plus bas | Copiée une colonne plus à droite |
|---|---|---|
| `B2` (relative) | `B3` | `C2` |
| `$B$2` (absolue) | `$B$2` | `$B$2` |
| `$B2` (colonne figée) | `$B3` | `$B2` |
| `B$2` (ligne figée) | `B$2` | `C$2` |

Prenons un exemple où les références mixtes sont indispensables : une table de multiplication, avec les facteurs 1, 2, 3 en ligne 1 et en colonne A. La formule de la cellule `B2` est `=B$1*$A2`. Elle fige la **ligne** du facteur en haut (`B$1`) et la **colonne** du facteur à gauche (`$A2`) : copiée partout, elle fait toujours le produit de l'en-tête de colonne et de l'en-tête de ligne.

```python hide
grille = [[None, 1, 2, 3]] + [[i] + [i * j for j in (1, 2, 3)] for i in (1, 2, 3)]
assert res["g_C3"] == 4 and res["g_D4"] == 9         # valeurs calculées par LibreOffice : C3 = 2×2, D4 = 3×3
O.maquette("figures/ch02-references.png", grille, largeurs=[6, 6, 6, 6], active="C3", formule="=C$1*$A3", surligne=["B1:D1", "A2:A4"], onglets=("Feuil1",))
print("figure : ch02-references.png")
```
<!--sortie-->
```text
figure : ch02-references.png
```

![Une table de multiplication avec une seule formule recopiée : `=B$1*$A2`. En colonne et en ligne, les en-têtes (surlignés) restent figés. Maquette dessinée avec matplotlib, valeurs calculées par LibreOffice.](figures/ch02-references.png)

⚠️ **Piège.** La cause la plus fréquente de résultats faux dans un tableur est une **référence qui devait être figée et ne l'était pas** : par exemple une cellule de taux de remise `B1` utilisée dans `=J2*B1`, qui devient `=J3*B2` à la ligne suivante, et multiplie par une cellule vide. Règle : toute cellule de paramètre (un taux, un seuil) est référencée avec des **dollars** ou, mieux, par un **nom** (sous-section suivante).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : exercice 2.1.

### 2.1.3 Plages nommées et tableaux structurés

Écrire `Lignes!$M$2:$M$29828` est exact mais illisible, et fragile : si l'on ajoute une ligne en bas, la plage ne s'étend pas. Deux mécanismes règlent le problème.

La **plage nommée** donne un nom à une plage (menu *Formules → Gestionnaire de noms*, ou la zone de nom à gauche de la barre de formule) : après avoir nommé `Montant` la colonne M, la formule devient `=SOMME(Montant)`. Le nom se lit comme une phrase, et il est stable quand on copie la formule.

Le **tableau structuré** (*Insertion → Tableau*, ou `Ctrl+T`) transforme la plage de données en objet : il reçoit un nom (ici `Ventes`), ses colonnes se citent par leur en-tête (`Ventes[montant]`), et surtout **il grandit tout seul** quand on ajoute des lignes en dessous. Toutes les formules, les tableaux croisés et les requêtes qui s'y réfèrent suivent.

```python hide-code
O.montrer(res, [("total", F["total"]), ("nomme", F["nomme"]), ("tab_total", F["tab_total"])])
print("trois écritures, un même total :", bool(np.isclose(res["total"], res["nomme"]) and np.isclose(res["total"], res["tab_total"])))
```
<!--sortie-->
```text
=SOMME(Lignes!M2:M29828)  →  1 324 763,72
=SOMME(Montant)  →  1 324 763,72
=SOMME(Ventes[montant])  →  1 324 763,72
trois écritures, un même total : True
```

Les trois écritures donnent le même total, **1 324 763,72 €**. La différence est ailleurs : elle apparaît le jour où le classeur change. Les tableaux structurés sont la première des bonnes pratiques de la section 2.4.

### 2.1.4 Agréger sous conditions : SOMME.SI.ENS, NB.SI.ENS, MOYENNE.SI.ENS

La plupart des questions d'un analyste commencent par « combien … **pour** … ? ». Trois fonctions y répondent, dans leur version à conditions multiples (le suffixe `.ENS` signifie « ensemble de critères ») :

| Question | Fonction | Syntaxe |
|---|---|---|
| Combien d'euros ? | `SOMME.SI.ENS` | `(plage_à_sommer ; plage_critère1 ; critère1 ; …)` |
| Combien de lignes ? | `NB.SI.ENS` | `(plage_critère1 ; critère1 ; …)` |
| Quelle moyenne ? | `MOYENNE.SI.ENS` | `(plage_à_moyenner ; plage_critère1 ; critère1 ; …)` |

⚠️ La **plage à sommer vient en premier** dans `SOMME.SI.ENS`, alors qu'elle vient **en dernier** dans l'ancienne `SOMME.SI(plage_critère ; critère ; plage_à_sommer)`. Cette inversion est une source d'erreurs classique.

Les critères sont des textes ou des nombres, éventuellement précédés d'un opérateur écrit **entre guillemets** : `"Site"`, `">0"`, `"<>"` (non vide). Pour comparer à une date ou à une cellule, on **concatène** : `">="&DATE(2025;3;1)`. Les jokers `*` (une suite de caractères) et `?` (un caractère) fonctionnent dans les critères de texte.

Voici les réponses à quelques questions de la gérante, calculées par LibreOffice :

```python hide-code
O.montrer(res, [("site", F["site"]), ("boutique", F["boutique"]), ("reseaux", F["reseaux"]), ("nb_promo", F["nb_promo"]),
                ("moy_jardin", F["moy_jardin"]), ("jardin_mars", F["jardin_mars"]), ("bougie", F["bougie"]), ("site_deco_nov", F["site_deco_nov"]),
                ("gros", F["gros"])])
```
<!--sortie-->
```text
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Site")  →  617 715,45
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Boutique")  →  560 973,91
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Réseaux")  →  146 074,36
=NB.SI.ENS(Lignes!L2:L29828;">0")  →  4 606
=MOYENNE.SI.ENS(Lignes!M2:M29828;Lignes!I2:I29828;"Jardin")  →  65,63
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!I2:I29828;"Jardin";Lignes!C2:C29828;">="&DATE(2025;3;1);Lignes!C2:C29828;"<"&DATE(2025;4;1))  →  14 788,58
=SOMME.SI(Lignes!H2:H29828;"Bougie*";Lignes!M2:M29828)  →  36 833,11
=NB.SI.ENS(Lignes!E2:E29828;"Site";Lignes!I2:I29828;"Décoration";Lignes!C2:C29828;">="&DATE(2025;11;1))  →  971
=NB.SI.ENS(Lignes!M2:M29828;">=100")  →  2 482
```

Lisons-les : le canal **Site** a rapporté 617 715,45 €, la **Boutique** 560 973,91 € et les **Réseaux** 146 074,36 € (ces trois montants s'additionnent bien en 1 324 763,72 € : c'est le premier **contrôle de cohérence** à toujours faire). Sur 29 827 lignes, 4 606 portent une remise ; une ligne de la catégorie Jardin pèse en moyenne 65,63 € ; les ventes de Jardin de mars 2025 valent 14 788,58 € ; les produits dont le nom commence par « Bougie » 36 833,11 € ; le Site a vendu 971 articles de décoration depuis le 1ᵉʳ novembre ; et 2 482 lignes valent 100 € ou plus.

Chacun de ces chiffres a été recoupé par pandas (`groupby`, `sum`, `mean`) : les écarts maximaux sont nuls au centime près. C'est l'habitude à prendre : **un chiffre obtenu par deux chemins indépendants est un chiffre auquel on peut se fier**.

#### Les pièges de l'agrégation conditionnelle

- **Les plages doivent avoir exactement la même taille.** Si l'on écrit `=SOMME.SI.ENS(M2:M29828 ; E2:E29818 ; "Site")` (dix lignes de moins pour le critère), Excel renvoie `#VALEUR!` : ici, LibreOffice l'a confirmé (`#VALEUR!`). C'est un bon signe : l'erreur est **visible**.
- **Une plage trop courte, au contraire, ne dit rien.** `=SOMME(M2:M29028)` oublie les 800 dernières lignes et renvoie 1 291 124,89 € au lieu de 1 324 763,72 € : **33 638,83 € disparus** sans le moindre message. C'est l'erreur la plus courante des classeurs réels, et la raison pour laquelle on préfère les tableaux structurés.
- **Les critères sont sensibles aux détails** : `"Site"` ne trouve pas `"site "` (avec une espace à la fin). Nous verrons comment nettoyer en 2.1.7.
- **Les dates doivent être de vraies dates** : une date stockée comme du texte (`"03/11/2025"`) n'est pas comparée comme une date (2.1.8).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.2, exercice 2.2.

### 2.1.5 Décider : SI, SI.CONDITIONS, ET, OU, SIERREUR

La fonction `SI(test ; valeur_si_vrai ; valeur_si_faux)` renvoie une valeur ou une autre selon un test. Pour ranger un panier dans une taille — « petit » en dessous de 40 €, « moyen » de 40 à 100 €, « gros » à partir de 100 € — on imbrique deux `SI` :

```text
=SI(A2>=100 ; "gros" ; SI(A2>=40 ; "moyen" ; "petit"))
```

La fonction `SI.CONDITIONS` (Excel 2019 et suivants, **à vérifier** selon votre version) évite l'imbrication : `=SI.CONDITIONS(A2>=100 ; "gros" ; A2>=40 ; "moyen" ; VRAI ; "petit")`. Le dernier couple `VRAI ; "petit"` joue le rôle de la valeur par défaut : sans lui, un montant qui ne remplit aucune condition produit `#N/A`.

```python hide-code
for lab, cle in [("12 €", "si1"), ("45 €", "si2"), ("99,90 €", "si3"), ("150 €", "si4")]:
    print(f"panier de {lab:8s} → {res[cle]}")
print("SI.CONDITIONS sur 99,90 € →", res["ifs"], "| ET(99,90 ≥ 40 ; 99,90 < 100) →", O.fr(res["et"]), "| OU(12 ≥ 100 ; 150 ≥ 100) →", O.fr(res["ou"]))
```
<!--sortie-->
```text
panier de 12 €     → petit
panier de 45 €     → moyen
panier de 99,90 €  → moyen
panier de 150 €    → gros
SI.CONDITIONS sur 99,90 € → moyen | ET(99,90 ≥ 40 ; 99,90 < 100) → VRAI | OU(12 ≥ 100 ; 150 ≥ 100) → VRAI
```

Les fonctions `ET(…)`, `OU(…)` et `NON(…)` combinent des tests : elles renvoient `VRAI` ou `FAUX`, et se placent à l'intérieur d'un `SI`. L'erreur classique est d'écrire `=SI(40<=A2<100 ; …)`, qui n'est **pas** un test d'intervalle en Excel : il faut `=SI(ET(A2>=40 ; A2<100) ; …)`.

`SIERREUR(formule ; valeur_de_remplacement)` remplace n'importe quelle erreur par une valeur : `=SIERREUR(A6/B6 ; 0)` renvoie 0 quand le dénominateur est nul. Utilisez-la **avec parcimonie** : elle **masque toutes les erreurs**, y compris celles qui révèlent un vrai problème (une référence cassée, un nom mal écrit). Si seule l'erreur « non trouvé » vous intéresse, préférez `SI.NON.DISP(…)`, qui ne traite que `#N/A`.

> ⚠️ **Piège.** Un `SIERREUR` qui renvoie 0 transforme une donnée **manquante** en donnée **égale à zéro**. Sur une moyenne ou une somme, cela fausse silencieusement le résultat. Préférez un message explicite (`"à vérifier"`) ou une cellule vide, et comptez ensuite les erreurs.

### 2.1.6 Chercher : RECHERCHEV, INDEX+EQUIV, RECHERCHEX

Presque toutes les analyses croisent deux tables : ici, les lignes de vente ne contiennent que l'identifiant du produit, et le prix d'achat est dans la feuille `Produits`. Retrouver une information d'une table à partir d'une clé s'appelle une **recherche** (en base de données, une **jointure**, chapitre 3).

**`RECHERCHEV(clé ; table ; n° de colonne ; FAUX)`** cherche la clé dans la **première colonne** de la table et renvoie la valeur de la colonne numéro n. Son quatrième argument est le piège principal : `FAUX` (ou 0) demande la correspondance **exacte** ; `VRAI` (ou omis !) demande la correspondance **approchée**, qui suppose la première colonne **triée** et renvoie la plus grande valeur inférieure ou égale à la clé.

```python hide-code
O.montrer(res, [("vl_exact", F["vl_exact"]), ("vl_exact_tri", F["vl_exact_tri"]), ("vl_faux_tri", F["vl_faux_tri"]),
                ("vl_espace", F["vl_espace"]), ("vl_trim", F["vl_trim"]), ("bareme", F["bareme"])])
```
<!--sortie-->
```text
=RECHERCHEV(7;Produits!A2:F121;2;FAUX)  →  Moule mat
=RECHERCHEV(5;Ref!A2:B5;2;FAUX)  →  Cadre design
=RECHERCHEV(5;Ref!A2:B5;2;VRAI)  →  #N/A
=RECHERCHEV(Ref!G2;Ref!E2:F5;2;FAUX)  →  #N/A
=RECHERCHEV(SUPPRESPACE(Ref!G2);Ref!E2:F5;2;FAUX)  →  3
=RECHERCHEV(4;Bareme!A2:B4;2;VRAI)  →  0,05
```

Lisons ces résultats. La clé 7 est trouvée exactement (`Moule mat`). Avec une table **non triée** (identifiants 7, 3, 12, 5), chercher la clé 5 en correspondance exacte donne bien `Cadre design`, mais **la même recherche en mode approché échoue** (`#N/A`) ; dans Excel, selon l'ordre des données, le résultat peut même être **faux sans erreur** : c'est pourquoi il ne faut **jamais oublier le `FAUX`**. Une clé tapée avec une espace de trop (`"Bol design "`) ne se trouve pas (`#N/A`) tant qu'on ne la nettoie pas avec `SUPPRESPACE`. Enfin, la correspondance approchée a un **bon usage** : lire un **barème** trié, comme une remise par palier de quantité (1 → 0 %, 3 → 5 %, 10 → 10 %) ; ici, une quantité de 4 donne 5 %.

Trois autres limites de `RECHERCHEV` : elle **ne regarde qu'à droite** de la colonne clé ; le **numéro de colonne** est écrit en dur, donc **insérer une colonne casse la formule sans prévenir** ; et une clé numérique (`7`) ne correspond pas à la même clé écrite comme du texte (`"7"`) dans Excel (l'erreur est `#N/A` ; LibreOffice, plus indulgent, convertit silencieusement : **le comportement diffère**, nous ne pouvons donc pas le montrer ici et il est à tester dans votre Excel).

**`INDEX` et `EQUIV`** se combinent pour faire mieux : `EQUIV(clé ; colonne_clés ; 0)` renvoie la **position** de la clé, et `INDEX(colonne_résultat ; position)` renvoie la valeur à cette position. La colonne résultat peut être **n'importe où** (à gauche aussi), et rien ne casse si l'on insère une colonne.

**`RECHERCHEX(clé ; colonne_clés ; colonne_résultat ; si_non_trouvé)`** (Excel 2021 et Microsoft 365, **à vérifier** pour les versions antérieures) cumule les avantages : correspondance exacte par défaut, valeur de remplacement intégrée, recherche dans les deux sens.

```python hide-code
O.montrer(res, [("idx", F["idx"]), ("xl", F["xl"]), ("xl_abs", F["xl_abs"]), ("xl_inv", F["xl_inv"])])
```
<!--sortie-->
```text
=INDEX(Produits!B2:B121;EQUIV(7;Produits!A2:A121;0))  →  Moule mat
=RECHERCHEX(7;Produits!A2:A121;Produits!B2:B121;"absent")  →  Moule mat
=RECHERCHEX(999;Produits!A2:A121;Produits!B2:B121;"absent")  →  absent
=RECHERCHEX("Bol design";Produits!B2:B121;Produits!A2:A121;"absent")  →  3
```

La dernière ligne illustre la recherche « à l'envers » : retrouver l'identifiant (3) d'un produit à partir de son nom, ce que `RECHERCHEV` ne sait pas faire.

⚠️ **Mais attention : un nom n'est pas une clé.** La recherche précédente renvoie l'identifiant **3**, la **première** correspondance, sans prévenir qu'il y en a d'autres. Vérifions l'unicité des noms dans le catalogue :

```python hide-code
print("catalogue :", len(P), "produits,", P["nom_produit"].nunique(), "noms distincts,", int(P["nom_produit"].duplicated(keep=False).sum()), "produits dont le nom est partagé")
```
<!--sortie-->
```text
catalogue : 120 produits, 60 noms distincts, 120 produits dont le nom est partagé
```

Le catalogue compte **120 produits mais seulement 60 noms distincts** : chaque nom est porté par deux produits (de prix différents). Une recherche par nom renvoie donc l'un des deux, silencieusement. Une **clé de recherche doit être unique** : ici l'identifiant du produit. Nous retrouverons cette anomalie, avec ses conséquences sur une jointure, en section 2.3.5.

#### Enrichir les lignes : le coût d'achat et la marge

Ajoutons à chaque ligne de vente le **coût d'achat unitaire** du produit, par `=RECHERCHEX(G2 ; Produits!A:A ; Produits!E:E)` (l'identifiant du produit est en colonne G) recopiée sur les 29 827 lignes dans une nouvelle colonne N. On obtient alors la **marge** de l'année : le chiffre d'affaires moins la somme des quantités multipliées par le coût unitaire.

```python hide
cols_m = ["id_ligne", "id_produit", "nom_produit", "quantite", "prix_unitaire", "montant"]
mm = M.head(7)
rows = [cols_m + ["cout_u"]] + [[getattr(r, c) for c in cols_m] + [r.cout_achat] for r in mm.itertuples(index=False)]
O.maquette("figures/ch02-recherche.png", rows, lettres=["A", "G", "H", "J", "K", "M", "N"], largeurs=[8, 10, 18, 8, 12, 9, 8], active="N2",
           formule="=RECHERCHEX(G2;Produits!A:A;Produits!E:E)", surligne=["N1:N8"], onglets=("Lignes", "Produits", "Clients"))
print("figure : ch02-recherche.png")
```
<!--sortie-->
```text
figure : ch02-recherche.png
```

![Une colonne ajoutée par recherche : le coût d'achat unitaire de chaque ligne, retrouvé dans la feuille `Produits` à partir de l'identifiant du produit. Extrait : seules quelques colonnes de la feuille sont affichées. Maquette dessinée avec matplotlib, valeurs issues du classeur.](figures/ch02-recherche.png)

```python hide-code
print(f"marge de l'année : {O.fr(res['marge'])} € (CA {O.fr(res['total'])} €)")
print(f"dont catégorie Jardin : {O.fr(res['marge_jardin'])} €")
```
<!--sortie-->
```text
marge de l'année : 639 810,88 € (CA 1 324 763,72 €)
dont catégorie Jardin : 171 875,43 €
```

La **marge de 2025** s'élève à **639 810,88 €**, dont **171 875,43 €** pour la seule catégorie Jardin ; les deux chiffres sont recoupés par pandas (fusion des tables, puis somme). La marge est ici calculée sur le prix de vente tel quel : nous ignorons la TVA, simplification que nous reprendrons en section 2.2.4.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3, exercices 2.3 et 2.4.

### 2.1.7 Nettoyer du texte

Les données réelles sont sales : espaces en trop, majuscules incohérentes, nombres écrits comme du texte. Quelques fonctions de texte suffisent à corriger l'essentiel.

| Besoin | Fonction | Exemple (cellule `B2` = `" bOÎTE rustique  "`) |
|---|---|---|
| Enlever les espaces superflus | `SUPPRESPACE` | `SUPPRESPACE(B2)` |
| Normaliser la casse | `MAJUSCULE`, `MINUSCULE`, `NOMPROPRE` | `NOMPROPRE(SUPPRESPACE(B2))` |
| Extraire un morceau | `GAUCHE`, `DROITE`, `STXT` | `GAUCHE(A2 ; 1)` |
| Mesurer, repérer | `NBCAR`, `TROUVE`, `CHERCHE` | `TROUVE("-" ; F2)` |
| Remplacer | `SUBSTITUE` | `SUBSTITUE(E2 ; "," ; ".")` |
| Assembler | `CONCAT`, `JOINDRE.TEXTE`, opérateur `&` | `CONCAT(A2 ; "-" ; D2)` |
| Convertir en nombre | `CNUM` | `CNUM(E2)` |

```python hide-code
O.montrer(res, [("t_prop", F["t_prop"]), ("t_gauche", F["t_gauche"]), ("t_droite", F["t_droite"]), ("t_len", F["t_len"]), ("t_stxt", F["t_stxt"]),
                ("t_concat", F["t_concat"]), ("t_join", F["t_join"]), ("t_find", F["t_find"]), ("t_val", F["t_val"])])
```
<!--sortie-->
```text
=NOMPROPRE(SUPPRESPACE(Texte!B2))  →  Boîte Rustique
=GAUCHE(Texte!A2;1)  →  T
=CNUM(DROITE(Texte!A2;NBCAR(Texte!A2)-1))  →  33 133
=NBCAR(Texte!B2)  →  17
=STXT(Texte!C2;1;3)  →  abc
=CONCAT(Texte!A2;"-";Texte!D2)  →  T33133-77
=JOINDRE.TEXTE(" | ";VRAI;SUPPRESPACE(Texte!B2);SUPPRESPACE(Texte!B3);SUPPRESPACE(Texte!B4))  →  bOÎTE rustique | moule MAT | Plaid NORDIQUE
=TROUVE("-";Texte!F2)  →  2
=CNUM(Texte!E2)  →  12,50
```

L'exemple le plus courant est le **numéro de ticket** de l'export de caisse : `T33133`, un code qui commence par une lettre. Pour obtenir le numéro seul, on enlève le premier caractère et on convertit : `=CNUM(DROITE(A2 ; NBCAR(A2)-1))` donne 33 133. De même, le nom d'article ` bOÎTE rustique  ` devient `Boîte Rustique` avec `NOMPROPRE(SUPPRESPACE(…))` : l'espace en tête et les doubles espaces disparaissent, et la casse est homogène. `TROUVE` est sensible à la casse et renvoie `#VALEUR!` si le texte n'existe pas ; `CHERCHE` ne l'est pas et accepte des jokers.

⚠️ **Piège.** `SUPPRESPACE` ne supprime pas l'**espace insécable** (code 160) que l'on obtient en copiant des données depuis une page web ou un PDF. Il faut alors `SUBSTITUE(A2 ; CAR(160) ; " ")` avant. Les décimales posent un autre piège : `"12,5"` est un nombre en Excel français, mais un texte qui **ne se convertit pas** en Excel anglais, où le séparateur décimal est le point. Quand vous échangez des fichiers entre langues, **testez**.

### 2.1.8 Manipuler des dates

Pour Excel, une date est un **numéro de série** : le nombre de jours écoulés depuis le 1ᵉʳ janvier 1900 (système par défaut de Windows, dans lequel le 1ᵉʳ janvier 1900 vaut 1). Le 1ᵉʳ janvier 2025 vaut **45 658** ; la cellule n'affiche une date que grâce à son **format**. Ce choix rend les calculs triviaux (la différence de deux dates est un nombre de jours) mais cache deux pièges : on peut afficher un nombre à la place d'une date (si le format est « Standard »), et inversement un nombre peut s'afficher comme une date.

> 🧪 **Un héritage historique.** Excel traite par erreur 1900 comme une année bissextile (pour rester compatible avec un ancien tableur) : les numéros de série d'avant le 1ᵉʳ mars 1900 sont décalés d'un jour. Sans conséquence pour des données récentes ; sachez-le si vous travaillez sur des dates anciennes. Les Mac utilisaient autrefois un système différent (point de départ en 1904) : une option du classeur le permet encore.

| Besoin | Fonction | Résultat |
|---|---|---|
| Extraire l'année, le mois, le jour | `ANNEE`, `MOIS`, `JOUR` | `ANNEE(3/11/2025)` = 2025 |
| Fabriquer une date | `DATE(année ; mois ; jour)` | `DATE(2025 ; 1 ; 1)` = 45 658 |
| Dernier jour du mois | `FIN.MOIS(date ; 0)` | `FIN.MOIS(10/02/2025 ; 0)` = 28/02/2025 |
| Décaler de n mois | `MOIS.DECALER(date ; n)` | `MOIS.DECALER(31/01/2025 ; 1)` = 28/02/2025 |
| Jour de la semaine | `JOURSEM(date ; 2)` | lundi = 1 |
| Écart | `DATEDIF(début ; fin ; "M")` | mois entiers écoulés |
| Jours ouvrés | `NB.JOURS.OUVRES(début ; fin)` | exclut samedis et dimanches |
| Afficher | `TEXTE(date ; "mmmm")` | « mars » |

```python hide-code
O.montrer(res, [("serial_n", F["serial_n"]), ("fin_mois", F["fin_mois"]), ("decale", F["decale"]), ("wd", F["wd"]), ("jsem", F["jsem"]),
                ("dif_m", F["dif_m"]), ("dif_j", F["dif_j"]), ("ouvres", F["ouvres"]), ("mois_txt", F["mois_txt"])])
```
<!--sortie-->
```text
=DATE(2025;1;1)*1  →  45 658
=FIN.MOIS(DATE(2025;2;10);0)  →  45 716
=MOIS.DECALER(DATE(2025;1;31);1)  →  45 716
=JOURSEM(DATE(2025;11;3);2)  →  1
=TEXTE(DATE(2025;11;3);"dddd")  →  lundi
=DATEDIF(DATE(2025;1;15);DATE(2025;11;3);"M")  →  9
=DATEDIF(DATE(2025;1;15);DATE(2025;11;3);"D")  →  292
=NB.JOURS.OUVRES(DATE(2025;11;3);DATE(2025;11;9))  →  5
=TEXTE(DATE(2025;3;15);"mmmm")  →  mars
```

Les résultats sont des numéros de série, que l'on met en forme de date pour les lire (`FIN.MOIS` donne 45 716, c'est-à-dire le 28 février 2025) ; le 3 novembre 2025 est un **lundi** (`JOURSEM(…;2)` renvoie 1), il y a **9 mois entiers** et **292 jours** entre le 15 janvier et le 3 novembre, et la semaine du 3 au 9 novembre compte **5 jours ouvrés**. Les numéros de série sont recoupés par pandas (écart de dates).

`DATEDIF` est une fonction **non documentée dans l'aide** d'Excel mais qui fonctionne ; évitez son argument `"MD"`, dont les résultats sont réputés incohérents.

#### Dates en texte : le piège du format régional

Quand un export écrit les dates comme `03/11/2025`, Excel les reconnaît comme des dates **si** le format correspond à la langue du poste : en français, jour/mois/année ; en anglais américain, mois/jour/année. La chaîne `11/03/2025` est donc le **11 mars** dans un Excel français et le **3 novembre** dans un Excel américain. Si Excel ne la reconnaît pas, elle reste du **texte** : une `SOMME` de ces cellules vaut 0, mais `DATEVALUE` les convertit.

```python hide-code
print("somme de deux dates stockées en texte :", O.fr(res["texte_date_somme"]))
print("somme après DATEVALUE (03/11/2025 + 11/03/2025) :", O.fr(res["texte_date_val"]), "= 45 964 + 45 727")
print("11/03/2025 lu par un Excel français :", O.fr(res["datev"]), "(le 11 mars 2025)")
```
<!--sortie-->
```text
somme de deux dates stockées en texte : 0
somme après DATEVALUE (03/11/2025 + 11/03/2025) : 91 691 = 45 964 + 45 727
11/03/2025 lu par un Excel français : 45 727 (le 11 mars 2025)
```

Notre classeur est en français : `11/03/2025` donne 45 727, le 11 mars. **Vérifiez toujours** quelques dates connues (un 25, un 31 : ceux-là ne peuvent pas être des mois) après un import : c'est le test le plus rapide pour détecter une inversion jour/mois.

⚠️ **Piège.** Les codes de format dans `TEXTE` dépendent de la **langue** : en français, l'année s'écrit `aaaa` et le jour `jjjj` ; en anglais `yyyy` et `dddd`. Un classeur partagé entre un poste français et un poste anglais peut donc afficher `#VALEUR!` ou un format inattendu. Dans ce livre, nous utilisons les codes valables dans les deux langues (`mmmm` pour le mois).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.4, exercice 2.5.

### 2.1.9 Les formules à résultats multiples : FILTRE, TRIER, UNIQUE, LET

Dans Excel 2021 et Microsoft 365, certaines fonctions renvoient **plusieurs valeurs** qui « débordent » (*spill*) dans les cellules voisines : `UNIQUE(plage)` liste les valeurs distinctes, `TRIER(plage)` les range, `FILTRE(plage ; condition)` extrait les lignes qui vérifient une condition, `SEQUENCE(n)` génère une suite de nombres. Avant ces fonctions, il fallait des astuces (formules matricielles, `Ctrl+Maj+Entrée`).

La fonction `LET` donne un **nom** à un résultat intermédiaire à l'intérieur d'une formule, ce qui la rend lisible et évite de recalculer deux fois la même chose : `=LET(somme ; SOMME(Montant) ; nb ; NBVAL(A:A)-1 ; somme/nb)` calcule le montant moyen par ligne.

```python hide-code
O.montrer(res, [("uniq", F["uniq"]), ("filt", F["filt"]), ("let", F["let"])])
```
<!--sortie-->
```text
=NBVAL(UNIQUE(Lignes!I2:I29828))  →  6
=SOMME(FILTRE(Lignes!M2:M29828;Lignes!E2:E29828="Site"))  →  617 715,45
=LET(a;SOMME(Lignes!M2:M29828);b;NBVAL(Lignes!A2:A29828);ARRONDI(a/b;2))  →  44,41
```

Les résultats scalaires ont été vérifiés : il y a **6 catégories** distinctes, le total des lignes du **Site** est de 617 715,45 € (le même que `SOMME.SI.ENS`, trouvé par un autre chemin), et le **montant moyen d'une ligne** est de **44,41 €**. En revanche, **le débordement lui-même** (la liste affichée sur plusieurs cellules) n'est pas vérifiable avec notre outil : nous l'avons recoupé par pandas (`unique`, `sort_values`, filtre booléen), qui donne les mêmes lignes. Ces fonctions sont absentes des versions anciennes d'Excel : un classeur qui les utilise **ne se recalcule pas** chez un collègue qui en possède une (⚠️ à vérifier avant de partager).

### 2.1.10 Les erreurs, et la correspondance anglais–français

Excel signale une formule impossible par un code d'erreur commençant par `#`. Les reconnaître vous fait gagner un temps considérable.

```python hide-code
O.montrer(res, [("div0", F["div0"]), ("na", F["na"]), ("val", F["val"]), ("ref", F["ref"]), ("nom", F["nom"]), ("iferr", F["iferr"])])
```
<!--sortie-->
```text
=1/0  →  #DIV/0!
=RECHERCHEV("zz";Produits!A2:B121;2;FAUX)  →  #N/A
="a"+1  →  #VALUE!
=INDEX(Produits!A:A;2000000)  →  #REF!
=NOMINCONNU(1)  →  #NAME?
=SIERREUR(1/0;"n/a")  →  n/a
```

| Code (Excel français) | Signification | Cause typique |
|---|---|---|
| `#DIV/0!` | division par zéro | dénominateur vide ou nul |
| `#N/A` | valeur non disponible | recherche sans résultat |
| `#VALEUR!` | mauvais type d'argument | texte à la place d'un nombre, plages de tailles différentes |
| `#REF!` | référence invalide | ligne ou colonne supprimée, `INDEX` hors plage |
| `#NOM?` | nom inconnu | faute de frappe dans une fonction ou un nom |
| `#NOMBRE!` | valeur numérique impossible | racine carrée d'un négatif |
| `#NUL!` | intersection vide | espace utilisé à la place de `;` ou `:` |
| `#DÉBORDEMENT!` | résultat qui déborde sur des cellules occupées | formule à résultats multiples bloquée |
| `#####` | colonne trop étroite | pas une erreur de calcul : élargir la colonne |

Le bloc précédent a produit cinq de ces erreurs avec LibreOffice (division par zéro, recherche sans résultat, texte plus un nombre, référence hors plage, nom inconnu) : `#DIV/0!`, `#N/A`, `#VALEUR!`, `#REF!` et `#NAME?` (le nom anglais de `#NOM?`). Une **différence** connue : la racine carrée d'un nombre négatif renvoie `#NOMBRE!` dans Excel et `#VALEUR!` dans LibreOffice ; la liste ci-dessus suit Excel et n'a pas pu être entièrement vérifiée.

Pour **chercher** les erreurs dans un classeur : `ESTERREUR(cellule)` renvoie `VRAI` ou `FAUX` ; le compte `=SOMMEPROD(--ESTERREUR(plage))` dénombre les erreurs d'une plage ; l'outil *Audit de formules* (onglet *Formules*) trace les antécédents d'une cellule. Un classeur propre n'affiche **aucune erreur** : un `#N/A` laissé en place est une alarme qu'on a éteinte.

#### Correspondance anglais–français

Un fichier `.xlsx` stocke les **noms anglais** des fonctions et le séparateur `,` ; Excel les affiche dans la langue de l'utilisateur. Quand vous lisez un tutoriel en anglais, voici les équivalents des fonctions de ce chapitre.

| Anglais | Français | Anglais | Français |
|---|---|---|---|
| `SUM`, `SUMIFS`, `SUMIF` | `SOMME`, `SOMME.SI.ENS`, `SOMME.SI` | `LEFT`, `RIGHT`, `MID` | `GAUCHE`, `DROITE`, `STXT` |
| `COUNTIFS`, `COUNTBLANK` | `NB.SI.ENS`, `NB.VIDE` | `TRIM`, `PROPER`, `LEN` | `SUPPRESPACE`, `NOMPROPRE`, `NBCAR` |
| `AVERAGEIFS` | `MOYENNE.SI.ENS` | `FIND`, `SUBSTITUTE`, `VALUE` | `TROUVE`, `SUBSTITUE`, `CNUM` |
| `IF`, `IFS`, `IFERROR` | `SI`, `SI.CONDITIONS`, `SIERREUR` | `CONCAT`, `TEXTJOIN`, `TEXT` | `CONCAT`, `JOINDRE.TEXTE`, `TEXTE` |
| `AND`, `OR`, `NOT` | `ET`, `OU`, `NON` | `YEAR`, `MONTH`, `EOMONTH` | `ANNEE`, `MOIS`, `FIN.MOIS` |
| `VLOOKUP`, `XLOOKUP` | `RECHERCHEV`, `RECHERCHEX` | `EDATE`, `WEEKDAY`, `NETWORKDAYS` | `MOIS.DECALER`, `JOURSEM`, `NB.JOURS.OUVRES` |
| `INDEX`, `MATCH` | `INDEX`, `EQUIV` | `FILTER`, `SORT`, `UNIQUE` | `FILTRE`, `TRIER`, `UNIQUE` |
| `SUMPRODUCT`, `LET` | `SOMMEPROD`, `LET` | `TRUE`, `FALSE` | `VRAI`, `FAUX` |

> ✅ **À retenir.**
> - Une formule est une **recette** : les références relatives se décalent, les références absolues (`$`) et les **noms** ne bougent pas ; un tableau structuré **grandit** tout seul.
> - `SOMME.SI.ENS` : la plage à sommer **vient d'abord** ; les plages doivent avoir **la même taille** ; une plage trop courte ne signale **rien**.
> - `RECHERCHEV` : toujours `FAUX` pour l'exacte ; elle regarde à droite et casse si l'on insère une colonne ; préférez `INDEX+EQUIV` ou `RECHERCHEX`.
> - `SIERREUR` masque **toutes** les erreurs : utilisez-la avec parcimonie.
> - Une date est un **numéro de série** ; vérifiez le format jour/mois après un import.
> - **Chaque chiffre important se recoupe par un second chemin** (ici pandas) : sur le classeur, 29 827 lignes, 1 324 763,72 €, un écart nul sur toutes les formules vérifiées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 à 2.4, exercices 2.1 à 2.5.
