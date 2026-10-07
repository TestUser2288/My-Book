## 2.4 Bonnes pratiques de tableur

Un classeur n'est pas seulement un calcul : c'est un **document que quelqu'un d'autre ouvrira**, souvent des mois plus tard, souvent la personne qui l'a écrit et qui ne se souvient plus de rien. Les erreurs de tableur ne viennent presque jamais d'une formule mal comprise ; elles viennent d'une **structure** qui les cache. Cette section rassemble les pratiques qui rendent un classeur **lisible, vérifiable et durable**.

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
n = len(L) + 1
dup = pd.concat([L, L.sample(500, random_state=1)], ignore_index=True)
nd = len(dup) + 1
M = L.merge(P[["id_produit", "cout_achat"]], on="id_produit")
ca = float(L["montant"].sum()); cout = float((M["quantite"] * M["cout_achat"]).sum())

def controles(feuille, nlignes):
    r = lambda c: f"{feuille}!{c}2:{c}{nlignes}"
    return {f"{feuille}|lignes": f"=ROWS({r('A')})", f"{feuille}|doublons": f"=ROWS({r('A')})-COUNTA(UNIQUE({r('A')}))",
            f"{feuille}|vides_canal": f"=COUNTBLANK({r('E')})", f"{feuille}|dmin": f"=MIN({r('C')})", f"{feuille}|dmax": f"=MAX({r('C')})",
            f"{feuille}|negatifs": f'=COUNTIFS({r("M")},"<=0")', f"{feuille}|total": f"=SUM({r('M')})",
            f"{feuille}|verdict": f'=IF(AND(ROWS({r("A")})=29827,ABS(SUM({r("M")})-1324763.72)<0.005),"OK","ÉCART")'}
F = {}
F.update(controles("Lignes", n)); F.update(controles("Dup", nd))
F["prev_marge"] = "=Hyp!B2*(1+Hyp!B3)*(1+Hyp!B4)-Hyp!B5*(1+Hyp!B3)*(1+Hyp!B6)"
F["prev_marge_0"] = "=Hyp!B2*(1+0)*(1+Hyp!B4)-Hyp!B5*(1+0)*(1+Hyp!B6)"
F["prev_ca"] = "=Hyp!B2*(1+Hyp!B3)*(1+Hyp!B4)"
F["arrondi_275"] = "=ROUND(2.675,2)"
F["flottant"] = "=(0.1+0.2)-0.3"
F["gros_nombre"] = "=12345678901234567*1"
F["somme_arrondis"] = "=SUMPRODUCT(ROUND(Lignes!M2:M30,1))"
F["arrondi_somme"] = "=ROUND(SUM(Lignes!M2:M30),1)"
F["plage_courte"] = f"=SUM(Lignes!M2:M{n - 800})"
extra = {"Hyp": [["", "valeur"], ["CA 2025", ca], ["volume", 0.05], ["prix", 0.03], ["coût 2025", cout], ["inflation du coût", 0.02]]}
res = O.evaluer(F, {"Lignes": L, "Dup": dup}, extra=extra)
```

### 2.4.1 Une structure en trois étages

La règle d'or est de **séparer ce qui entre, ce qui se calcule et ce qui se montre**. Un bon classeur comporte au moins quatre types de feuilles :

| Feuille | Contenu | Règle |
|---|---|---|
| `README` | à quoi sert le classeur, qui l'a fait, quand, d'où viennent les données, comment l'actualiser | écrite **en premier**, lue en premier |
| `Données` (ou plusieurs) | une table par feuille, brute ou nettoyée | **aucune mise en forme, aucune formule de synthèse** |
| `Calculs` | les formules et tableaux croisés qui lisent les données | rien de saisi à la main, sauf les **hypothèses** |
| `Présentation` | les chiffres et graphiques destinés aux lecteurs | ne contient que des **renvois** aux calculs |

Cette séparation a trois avantages. Quand les données changent (nouvelle semaine, nouvel export), on **remplace la feuille de données** et tout se recalcule. Quand on se demande d'où vient un chiffre, on remonte de la présentation aux calculs puis aux données. Et quand on donne le classeur à quelqu'un d'autre, il sait **où il peut toucher** et où il ne le doit pas.

Le contraire est le classeur « tout-en-un » : un tableau de bord où se mélangent des données collées, des calculs intermédiaires dans des cellules dispersées, et des chiffres retapés. Il fonctionne le jour où on le fabrique, puis plus jamais.

### 2.4.2 Des données propres : une ligne, une observation

Les outils d'analyse (tableaux croisés, Power Query, pandas, SQL) attendent des données **ordonnées** (*tidy*) :

1. **une ligne = une observation** (ici, un article vendu) ;
2. **une colonne = une variable**, avec **un seul type** (que des dates, que des montants) ;
3. **une seule ligne d'en-tête**, avec des noms courts et **sans cellules fusionnées** ;
4. **pas de ligne ni de colonne de totaux, de titres ou de blancs** au milieu des données ;
5. **une information par cellule** (pas de « Boutique / Ville A » dans la même cellule) ;
6. **des catégories écrites toujours de la même façon** (une liste de valeurs autorisées).

Comparons deux manières de présenter les mêmes ventes. À gauche, la présentation « pour être lue », qu'un humain aime ; à droite, la présentation « pour être analysée ».

```python hide
mois_fr = ["Janvier", "Février", "Mars", "Avril"]
mp = L.assign(mois=L["date_commande"].dt.month).pivot_table(index="mois", columns="categorie", values="montant", aggfunc="sum")
mal = [["Ventes 2025 - Cuisine et Maison (en €)", None, None, None], [None, None, None, None], ["Mois", "Cuisine", "Maison", "Total"]]
tot_t1 = [0.0, 0.0]
for m in (1, 2, 3):
    c, h = float(mp.loc[m, "Cuisine"]), float(mp.loc[m, "Maison"]); tot_t1[0] += c; tot_t1[1] += h
    mal.append([mois_fr[m - 1], round(c), round(h), round(c + h)])
mal.append(["Sous-total T1", round(tot_t1[0]), round(tot_t1[1]), round(sum(tot_t1))])
mal.append(["Avril", round(float(mp.loc[4, "Cuisine"])), round(float(mp.loc[4, "Maison"])), round(float(mp.loc[4, "Cuisine"] + mp.loc[4, "Maison"]))])
O.maquette("figures/ch02-mal-range.png", mal, lettres=["A", "B", "C", "D"], largeurs=[22, 10, 10, 10], active="A1", onglets=("Synthèse",), surligne=["A4:D4"], formule="Ventes 2025 - Cuisine et Maison (en €)")
v = L.head(7)[["date_commande", "categorie", "canal", "montant"]]
bien = [["date", "categorie", "canal", "montant"]] + [[r.date_commande, r.categorie, r.canal, float(r.montant)] for r in v.itertuples(index=False)]
O.maquette("figures/ch02-bien-range.png", bien, lettres=["A", "B", "C", "D"], largeurs=[12, 12, 10, 10], active="A2", onglets=("Données",), surligne=["A1:D1"])
print("figures : ch02-mal-range.png, ch02-bien-range.png")
```
<!--sortie-->
```text
figures : ch02-mal-range.png, ch02-bien-range.png
```

![À éviter : un titre sur la première ligne, une ligne blanche, une colonne de total et, surtout, une ligne de sous-total au milieu des données. Agréable à lire, impossible à analyser. Maquette dessinée avec matplotlib.](figures/ch02-mal-range.png)

![À faire : une ligne d'en-tête, une ligne par article vendu, une colonne par variable, aucun total. Maquette dessinée avec matplotlib.](figures/ch02-bien-range.png)

Dans la première forme, un tableau croisé dynamique prendrait « Sous-total T1 » pour un mois, la ligne de titre pour un en-tête, et la colonne `Total` pour une catégorie. Dans la seconde, tout fonctionne : on regroupe par ce que l'on veut. Quand on **reçoit** des données sous la première forme (c'est fréquent), c'est précisément ce que Power Query (section 2.3) remet en forme.

⚠️ **Deux détails qui comptent.** D'abord les **identifiants** : un code comme `007` ou `00512` perd ses zéros si Excel le prend pour un nombre ; stockez-le comme **texte** (format texte *avant* la saisie). Ensuite les **cellules fusionnées** : elles cassent le tri, le filtre et les tableaux croisés ; pour centrer un titre au-dessus de plusieurs colonnes, utilisez l'alignement *Centré sur plusieurs colonnes*, qui ne fusionne rien.

### 2.4.3 Séparer les hypothèses des formules

Une formule qui contient un **nombre écrit en dur** est une bombe à retardement : `=B2*1,03` ne dit pas ce que représente 1,03, et personne ne pense à le changer quand le taux change. La règle est simple : **tout paramètre vit dans une cellule étiquetée**, et les formules y renvoient (par une référence absolue ou un nom, 2.1.2 et 2.1.3).

Illustrons-le avec une prévision simple pour 2026. Les hypothèses sont posées dans une feuille `Hyp` : volume +5 %, prix +3 %, inflation du coût d'achat +2 %. Le chiffre d'affaires 2026 est le chiffre de 2025 multiplié par `(1 + volume) × (1 + prix)` ; le coût d'achat est celui de 2025 multiplié par `(1 + volume) × (1 + inflation)` ; la marge est la différence.

```python hide-code
ca26 = ca * 1.05 * 1.03; cout26 = cout * 1.05 * 1.02
print("CA 2025 :", O.fr(ca), "| coûts d'achat 2025 :", O.fr(cout), "| marge 2025 :", O.fr(ca - cout))
print("marge 2026 (volume +5 %) :", O.fr(res["prev_marge"]), "| CA 2026 :", O.fr(res["prev_ca"]), "| recoupement en Python :", O.fr(ca26 - cout26))
print("marge 2026 si le volume reste stable :", O.fr(res["prev_marge_0"]))
print("marge 2026 par rapport à 2025 :", round((res["prev_marge"] / (ca - cout) - 1) * 100, 1), "% (volume +5 %) et", round((res["prev_marge_0"] / (ca - cout) - 1) * 100, 1), "% (volume stable)")
```
<!--sortie-->
```text
CA 2025 : 1 324 763,72 | coûts d'achat 2025 : 684 952,84 | marge 2025 : 639 810,88
marge 2026 (volume +5 %) : 699 147,47 | CA 2026 : 1 432 731,96 | recoupement en Python : 699 147,47
marge 2026 si le volume reste stable : 665 854,73
marge 2026 par rapport à 2025 : 9.3 % (volume +5 %) et 4.1 % (volume stable)
```

Avec ces hypothèses, la marge passe de **639 810,88 €** à **699 147,47 €** (+ 9,3 %) ; si le volume reste stable, elle s'élève à **665 854,73 €** (+ 4,1 %). Le **changement d'une seule cellule** (le volume) suffit à passer de l'un à l'autre : c'est ce qu'on appelle une **analyse de sensibilité**, et elle n'est possible que parce que l'hypothèse n'est écrite **qu'à un seul endroit**.

> 🧭 **En pratique.** Donnez une **couleur** aux cellules de saisie (par exemple un fond jaune pâle) et **une seule** couleur : tout le reste est calculé et ne se modifie pas. Ajoutez une colonne « source » ou « commentaire » à côté de chaque hypothèse : d'où vient ce 3 % ?

### 2.4.4 Se contrôler : validation, mise en forme conditionnelle, feuille de contrôles

On ne corrige bien que ce que l'on voit. Trois outils d'Excel aident à **rendre les erreurs visibles** :

- la **validation de données** (*Données → Validation*) restreint ce qu'une cellule accepte : une liste de valeurs (les trois canaux), un nombre entre deux bornes, une date dans la période. Une saisie `Sit` au lieu de `Site` est refusée à l'entrée plutôt que détectée dans un total faux ;
- la **mise en forme conditionnelle** colore les cellules qui remplissent une condition (valeurs négatives, doublons, écarts supérieurs à un seuil) ;
- une **feuille de contrôles** réunit des formules qui répondent à la question « ce classeur est-il intact ? ».

Voici notre feuille de contrôles, calculée par LibreOffice sur les données de la gérante, puis sur une copie où **500 lignes sont comptées deux fois** (un accident de copier-coller, l'erreur de la section 2.2.5). Les contrôles sont : nombre de lignes, nombre de doublons (lignes moins valeurs distinctes de l'identifiant), cellules vides dans une colonne clé, plage de dates, montants négatifs, total, et un verdict qui compare le nombre de lignes et le total à leurs **valeurs attendues**.

```python hide-code
lignes_c = [("lignes", "nombre de lignes"), ("doublons", "doublons d'identifiant"), ("vides_canal", "canaux vides"), ("dmin", "date minimale"), ("dmax", "date maximale"),
            ("negatifs", "montants ≤ 0"), ("total", "total des montants"), ("verdict", "verdict")]
print(f"{'contrôle':26s}{'données saines':>18s}{'avec 500 doublons':>20s}")
for k, lab in lignes_c:
    print(f"{lab:26s}{O.fr(res['Lignes|' + k]):>18s}{O.fr(res['Dup|' + k]):>20s}")
```
<!--sortie-->
```text
contrôle                      données saines   avec 500 doublons
nombre de lignes                      29 827              30 327
doublons d'identifiant                     0                 500
canaux vides                               0                   0
date minimale                     01/01/2025          01/01/2025
date maximale                     31/12/2025          31/12/2025
montants ≤ 0                               0                   0
total des montants              1 324 763,72        1 345 630,05
verdict                                   OK               ÉCART
```

Le classeur sain passe tous les contrôles (29 827 lignes, aucun doublon, aucune valeur manquante, dates du 01/01/2025 au 31/12/2025, aucun montant négatif, verdict **OK**). La copie abîmée est détectée immédiatement : 30 327 lignes, **500 doublons**, un total de 1 345 630,05 € au lieu de 1 324 763,72 €, et un verdict **ÉCART**. **Les valeurs attendues** (29 827 lignes, 1 324 763,72 €) viennent d'une **autre source** que le classeur (par exemple la compta, ou la base de données) : c'est ce qui rend le contrôle utile, car un contrôle qui compare le classeur à lui-même ne prouve rien.

### 2.4.5 Les erreurs de tableur que tout le monde commet

Les erreurs spectaculaires de tableur ont des **mécanismes** simples et récurrents. Les reconnaître vaut mieux que mémoriser des anecdotes.

**1. La conversion automatique.** Excel interprète ce que l'on saisit ou importe : `1-2` devient une date, `007` devient 7, un nom qui ressemble à une date devient une date. Les chercheurs en génétique en ont fait l'amère expérience : des noms de gènes comme `SEPT2` ou `MARCH1` étaient convertis en dates dans des listes publiées, au point que les organismes de nomenclature ont fini par **renommer** des gènes (à vérifier, mais le cas est documenté). Pour éviter la conversion, importez en **texte** (Power Query, section 2.3) ou mettez la colonne au format texte **avant** de coller.

**2. L'arrondi et la précision.** Un tableur affiche un nombre arrondi mais calcule avec le nombre complet, et inversement. Deux illustrations sur nos données :

```python hide-code
print("somme des montants arrondis au dixième, 29 premières lignes :", O.fr(res["somme_arrondis"]), "| arrondi de la somme :", O.fr(res["arrondi_somme"]))
print("ARRONDI(2,675 ; 2) dans le tableur :", O.fr(res["arrondi_275"]), "| round(2.675, 2) en Python :", round(2.675, 2))
print("(0,1 + 0,2) − 0,3 dans le tableur :", O.fr(res["flottant"]), "| en Python :", 0.1 + 0.2 - 0.3)
print("12345678901234567 dans le tableur :", O.fr(res["gros_nombre"]))
```
<!--sortie-->
```text
somme des montants arrondis au dixième, 29 premières lignes : 1 281,90 | arrondi de la somme : 1 281,70
ARRONDI(2,675 ; 2) dans le tableur : 2,68 | round(2.675, 2) en Python : 2.67
(0,1 + 0,2) − 0,3 dans le tableur : 0 | en Python : 5.551115123125783e-17
12345678901234567 dans le tableur : 12 345 678 901 234 600
```

- **La somme des arrondis n'est pas l'arrondi de la somme** : 1 281,90 € contre 1 281,70 € sur seulement 29 lignes.
- **Outils différents, arrondis différents** : le tableur arrondit 2,675 à 2,68 (convention « 5 vers le haut » appliquée au nombre décimal), alors que Python donne 2,67, parce que 2,675 n'est **pas représentable exactement** en binaire (il est stocké un peu en dessous) ; de même, `(0,1 + 0,2) − 0,3` vaut 0 dans le tableur et 5,55 × 10⁻¹⁷ en Python : le tableur « nettoie » certains petits résidus, ce qui peut masquer un problème de précision.
- **La précision est limitée à 15 chiffres significatifs** : un identifiant de 17 chiffres (`12345678901234567`) perd ses derniers chiffres (LibreOffice affiche ici 12 345 678 901 234 600). **Les identifiants longs (numéros de carte, de compte) doivent être stockés comme du texte.**

Pour des montants, la règle est de **choisir où l'on arrondit** (à la ligne ? au total ?) et de s'y tenir : un écart de quelques centimes entre deux documents est presque toujours une affaire d'arrondi, pas d'erreur de calcul.

**3. La plage oubliée.** `=SOMME(M2:M29028)` oublie les 800 dernières lignes (33 638,83 € de moins, section 2.1.4). Un grand article d'économie très cité a, dit-on, subi une erreur de ce type (une plage qui omettait quelques pays) ; le détail est à vérifier, le mécanisme est certain. Contre cela : tableaux structurés, contrôle de total.

**4. Les limites du format.** Un fichier `.xlsx` est limité à **1 048 576 lignes** et 16 384 colonnes ; l'ancien format `.xls` s'arrêtait à **65 536 lignes**. Un service de santé publique a, en 2020, perdu plusieurs milliers de cas déclarés parce qu'un fichier de résultats était enregistré dans l'ancien format (à vérifier : l'incident est largement rapporté). Des données au-delà du million de lignes **n'ont rien à faire dans un tableur** : base de données, SQL, Python.

**5. Les liens et les valeurs figées.** Un classeur qui lit un autre classeur par un lien externe affiche l'ancienne valeur si le fichier source a bougé ; un « copier / collage spécial valeurs » fige un chiffre qui ne se mettra plus jamais à jour. Les deux sont légitimes, **à condition de les documenter**.

### 2.4.6 Documenter, protéger, versionner, partager

**Documenter.** La feuille `README` répond en dix lignes à : *à quoi sert ce classeur ? qui l'a produit, quand, pour qui ? quelles sont les sources des données et leurs dates ? comment l'actualiser ? quelles sont les hypothèses ? quelles sont les limites connues ?* Les commentaires de cellules servent aux exceptions (« valeur corrigée à la main le 12/03, voir le mail du fournisseur »).

**Nommer et versionner.** Un fichier s'appelle `ventes_2025_v03_2025-12-31.xlsx` plutôt que `ventes_final_vraiment_final.xlsx` : un numéro de version, une date ISO (année-mois-jour, qui se range correctement par ordre alphabétique). Si le classeur est partagé dans un espace en ligne, l'**historique des versions** permet de revenir en arrière ; si le travail est important, un **journal des modifications** (une feuille de plus) note qui a changé quoi.

**Protéger.** La protection d'une feuille ou de cellules verrouille les formules et laisse libres les cellules de saisie : c'est un **garde-fou contre les fausses manœuvres**, pas une mesure de sécurité (les mots de passe de protection d'un classeur sont faciles à contourner). Pour des données confidentielles, le contrôle d'accès se fait au niveau du **dossier ou du fichier**, pas de la feuille. Les classeurs qui contiennent des **données personnelles** (noms, adresses, téléphones de clients) sont soumis à des règles de confidentialité, et circulent mal par courrier électronique : le volume II y consacre un chapitre complémentaire.

**Partager.** Pour diffuser un chiffre, mieux vaut un **PDF** ou une feuille de présentation en lecture seule que le classeur de travail ; pour échanger des données, un **CSV** (simple, universel) plutôt qu'un classeur plein de formules et de liens.

> 🧭 **Liste de contrôle d'un classeur fiable.**
> 1. Une feuille `README` : objet, auteur, date, sources, hypothèses.
> 2. Données et calculs **séparés** ; données en **tableau structuré**, une ligne par observation.
> 3. **Aucun nombre en dur** dans une formule : des cellules d'hypothèses étiquetées.
> 4. Une **feuille de contrôles** comparant à une source indépendante.
> 5. **Aucune erreur** affichée (`#N/A`, `#REF!`…), aucune cellule fusionnée.
> 6. Un nom de fichier **versionné** et daté.

> ✅ **À retenir.**
> - Séparez ce qui **entre** (données, hypothèses), ce qui se **calcule** et ce qui se **montre**.
> - Des données **ordonnées** (une ligne, une observation) font fonctionner tous les outils ; un tableau « pour l'œil » les met en échec.
> - Un paramètre écrit en dur est une erreur future : une cellule, un nom, une analyse de sensibilité (ici : marge 2026 de 699 147,47 € ou 665 854,73 € selon le volume).
> - **Contrôlez** : lignes, doublons, vides, dates, total comparé à une **source indépendante** (500 doublons détectés, verdict ÉCART).
> - Les erreurs célèbres ont des mécanismes simples : conversion automatique, arrondis, plage oubliée, limites du format, liens et valeurs figées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercices 2.10 et 2.11.
