# Chapitre 4 : Storytelling et rédaction de rapports

> « Une analyse n'a de valeur que le jour où quelqu'un sait quoi en faire. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch04 as O
D = os.environ["DONNEES"]
d = O.charger(D)
a = O.analyse_promo(d)
print("jours :", len(d["j"]), "| lignes de commande :", len(d["x"]), "| livraisons :", len(d["liv"]))
print("effet de la promotion : %+.1f %% [%+.1f ; %+.1f] | incrément de marge %.0f € | seuil %+.1f %%" % (a["e"] * 100, a["e_bas"] * 100, a["e_haut"] * 100, a["inc"], a["seuil"] * 100))
assert round(a["e"] * 100, 1) == 19.2 and round(a["inc"]) == -17884 and a["jours"] == 153
```
<!--sortie-->
```text
jours : 1096 | lignes de commande : 83905 | livraisons : 19420
effet de la promotion : +19.2 % [+13.5 ; +25.1] | incrément de marge -17884 € | seuil +35.8 %
```

Un mardi matin, la gérante repose sur votre bureau le rapport que vous lui aviez remis la semaine précédente : douze pages, dix-sept figures, un tableau de régression en annexe. Elle l'a lu. Elle sourit poliment, puis elle pose la question que tout analyste finit par entendre : « C'est très complet. **Et alors, qu'est-ce que je fais ?** »

Vous avez fait, aux chapitres précédents, le plus dur : poser la question, nettoyer les données, estimer un effet, mesurer son incertitude. Vous savez que les promotions ajoutent environ 19 % de commandes et que, malgré cela, elles font perdre de la marge. Mais ce savoir est **dans votre tête et dans votre notebook**. Tant qu'il n'est pas **dans la tête de la gérante**, dans une forme qui lui permette de **décider**, il n'a produit aucune valeur. C'est le sujet de ce chapitre : transformer une analyse en **récit** (4.1), en **rapport** (4.2), en **synthèse d'une page** (4.3) et en **rapport qui se fabrique tout seul** chaque semaine (4.4).

> 💡 **Intuition.** Une analyse répond à une question ; un récit répond à une question **pour quelqu'un qui doit agir**. Le récit n'ajoute pas un chiffre : il **choisit**, **ordonne** et **conclut**. Il est donc une partie de l'analyse, pas son habillage.

Ce chapitre est surtout un chapitre d'**écriture**. Vous y verrez peu de code et beaucoup de textes : des paragraphes **avant** et **après** réécriture, commentés, parce que l'on apprend à écrire en comparant. Les chiffres cités viennent du calcul, comme partout dans ce livre : un récit honnête est un récit dont chaque nombre se retrouve.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de l'analyse brute à l'automatisation d'un rapport.

- **4.1 Structurer un récit de données.** Un récit a un **arc** (contexte, tension, preuves, résolution), commence par la **réponse** (la pyramide de Minto) et porte **un message par figure et par titre**. Nous bâtissons le storyboard de l'analyse des promotions en cinq pages, nous décidons ce qui va en **annexe**, et nous voyons comment un récit peut devenir **malhonnête** (cerises cueillies, causalité sous-entendue).
- **4.2 Rédiger des rapports d'analyse clairs.** La **structure** d'un rapport (résumé, question, données, méthode, résultats, limites, recommandations, annexes), l'art d'écrire pour un **lecteur pressé**, les **chiffres** (arrondis, comparés, avec leur unité), les **tableaux** et les **légendes**, une **liste de relecture**, et la **reproductibilité** du rapport lui-même.
- **4.3 ➕ Synthèses de direction, rapports d'une page, présentations.** Le résumé de cinq lignes, la page unique et la présentation de huit diapositives : ce qu'on garde et ce qu'on coupe.
- **4.4 ➕ Rapports récurrents automatisés.** Un script qui fabrique chaque lundi le rapport de la semaine, avec des **contrôles avant envoi** et un texte généré **qui n'ose pas conclure quand les données ne le permettent pas**.

## Les données du chapitre

> 📦 **Les données.** Les fichiers de la boutique des volumes précédents, **simulés**, propres : `jours_exploitation.csv` (1 096 jours : commandes, chiffre d'affaires, météo, promotion, publicité), `commandes.csv`, `lignes_commande.csv`, `produits.csv` et `livraisons.csv`. L'analyse racontée est celle du **projet du volume III** : l'effet des promotions sur les commandes et sur la marge. Les nombres de ce chapitre sont recalculés ici par `build/outils_ch04.py`, et l'on connaît la **vérité programmée** : la promotion augmente les commandes de **18 %**.

Un mot sur ce que nous ne faisons pas : aucun logiciel de présentation ni de traitement de texte n'est exécuté dans ce chapitre. Les maquettes de pages et de diapositives sont **dessinées avec matplotlib** ; les outils (PowerPoint, Keynote, Word, LibreOffice Impress…) sont cités sans que leurs écrans soient reproduits.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.6 et exercices 4.1 à 4.12 ; chacun renvoie à la section du livre qui l'éclaire.
