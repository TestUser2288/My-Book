# Chapitre 1 : Principes de visualisation

> « Un graphique n'est pas une illustration de l'analyse : c'est l'analyse, telle que l'autre va la lire. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch01 as O
F = O.faits()
print("CA 2023-2025 (k€) :", ", ".join(f"{v:,.0f}".replace(",", " ") for v in F["t"].values), "| conversion e-mail :", round(F["conv"]["email"], 1), "%")
```
<!--sortie-->
```text
CA 2023-2025 (k€) : 1 139, 1 189, 1 325 | conversion e-mail : 8.7 %
```

Un lundi, la gérante vous transmet un message d'une ligne, accompagné d'une capture d'écran : « **Je reçois ton graphique et je ne comprends pas ce qu'il faut en conclure.** » Le graphique en question est celui que vous avez envoyé vendredi, avec fierté : la conversion du site selon la source de trafic, six barres de six couleurs, une grille noire, une légende, un titre qui dit « Graphique 1 ». Tous les chiffres sont justes. Et pourtant, une lectrice attentive, qui connaît son métier mieux que vous, n'en tire rien.

Ce n'est pas un problème de données : c'est un problème de **traduction**. Entre le tableau de chiffres que vous avez sous les yeux et la décision que la gérante doit prendre, il y a une personne, et cette personne dispose de quelques secondes. Le graphique est ce qui franchit cet espace. S'il est mal choisi, mal ordonné, trop chargé, trompeur sans le vouloir, le travail d'analyse des trois volumes précédents est perdu à la dernière étape.

![Avant et après : le même tableau de six conversions par source, à gauche tel que l'outil le produit par défaut, à droite après quelques gestes simples (tri, une couleur, étiquettes directes, titre qui énonce la conclusion). Figure construite avec matplotlib à partir des sessions du site 2025 (données simulées).](figures/ch01-avant-apres.png)

```python hide
O.fig_redessin_avant_apres()
conv = F["conv"]
assert round(conv["email"], 1) == 8.7 and round(conv["reseaux"], 1) == 2.2 and round(conv["email"] / conv["reseaux"]) == 4
```
<!--sortie-->
```text
figure : ch01-avant-apres.png
```

La figure ci-dessus est le programme de ce chapitre. À gauche, les réglages par défaut ; à droite, les mêmes données après une demi-heure de travail. Rien n'a été ajouté qui ne figure déjà dans le tableau : on a **trié**, **retiré**, **nommé** et **énoncé**. Le message, lui, ne change pas : l'e-mail convertit environ **quatre fois** mieux que les réseaux sociaux (8,7 % contre 2,2 %). Mais à droite, la gérante le **lit** en trois secondes.

Ce chapitre fixe les principes qui rendent cela possible. Il ne parle encore d'aucun outil : les outils de tableaux de bord arrivent au chapitre 2, la programmation des graphiques au chapitre 3. Les principes, eux, valent pour tous.

## Le chemin de ce chapitre

- **1.1 Choisir le bon graphique.** On part de la **question** que pose la lectrice, pas du type de graphique que l'on sait faire. Un arbre de décision, la **hiérarchie des encodages visuels** (position, longueur, angle, aire, couleur), les mêmes données dites de quatre façons, le catalogue (barres, courbes, nuages, histogrammes, cascades, cartes thermiques) et ce qu'il vaut mieux éviter (camemberts chargés, doubles axes, radars, 3D).
- **1.2 Clarté, simplicité et mise en page.** Retirer ce qui ne dit rien, ordonner, étiqueter directement, écrire un **titre qui énonce la conclusion**, soigner axes et unités, comparer en **petits multiples**, penser à la salle de projection, et **redessiner** un graphique en cinq gestes, avant et après.
- **1.3 ➕ Théorie des couleurs, accessibilité, systèmes de design.** Trois familles de palettes, la couleur qui a un sens et un seul, le **daltonisme** simulé par le calcul, le **contraste** calculé selon une formule publique, et la **page de design** qui rend cohérents tous les tableaux de bord d'une entreprise.
- **1.4 ➕ Erreurs courantes et graphiques trompeurs.** Dix pièges, chacun avec le graphique qui trompe et sa version corrigée : axe tronqué, aires et 3D, échelles différentes, double axe, période choisie, pourcentages sans effectifs, corrélation suggérée, camembert à neuf parts, paradoxe de Simpson en image, échelle logarithmique non signalée. Pour chacun : **qui est trompé, par quoi, avec quelle conséquence**.

> 💡 **Intuition.** Un graphique est un **argument**. Comme tout argument, il a une thèse (ce qu'il faut conclure), des preuves (les données) et une forme (ce qui le rend convaincant, ou trompeur). Choisir un graphique, c'est choisir la forme la plus **honnête** et la plus **rapide à lire** pour une thèse que l'on peut défendre.

> ⚠️ **Piège.** « C'est mon outil qui l'a fait comme ça » n'est pas une justification. Les réglages par défaut d'un logiciel ne connaissent ni votre lectrice, ni votre question, ni la décision qui suit : ils produisent un graphique **possible**, pas un graphique **bon**.

## Les données du chapitre

Les exemples viennent de la **boutique** simulée des volumes précédents : commandes et lignes de commande 2023–2025 (chiffre d'affaires de 1 139, 1 189 puis 1 325 k€), jours d'exploitation (publicité, promotions, météo), sessions du site en 2025 (conversion par source), compte de résultat, retours de marchandises, **villes** (vingt villes fictives, de « Ville A » à « Ville T », dans un plan inventé), et la série « avec incidents » (une panne du site, une fermeture exceptionnelle) du volume III. Tout est **simulé** ; la vérité programmée sert ici de juge : un graphique est « fidèle » s'il laisse voir ce qui s'est réellement passé dans les données.

Les personnes sont désignées **par leur fonction** : la gérante, la responsable logistique, le financeur. Les nombres de la prose sont calculés par des blocs exécutés ; les figures sont toutes dessinées avec matplotlib (le code est rangé dans `build/outils_ch01.py` pour ne pas encombrer le texte). Aucune capture d'un produit commercial n'apparaît dans ce chapitre.
