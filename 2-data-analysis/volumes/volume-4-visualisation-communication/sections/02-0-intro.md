# Chapitre 2 : Tableaux de bord

> « Un tableau de bord ne sert pas à tout montrer : il sert à savoir quoi faire lundi matin. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch02 as O
D = os.environ["DONNEES"]
d = O.charger(D)
star = O.etoile(d)
ventes = d["fv"]
hebdo = O.serie_hebdo(d)
print(len(ventes), len(star["fait_ventes"]), len(hebdo))
```
<!--sortie-->
```text
83905 83905 157
```

Un lundi matin, la gérante s'arrête devant votre bureau. « Chaque semaine, tu m'envoies un fichier. Je l'ouvre, je cherche ce qui m'intéresse, je ne trouve pas, je te rappelle. **Je veux voir chaque lundi où nous en sommes, sans te demander un fichier.** Et que ça me dise tout seul quand quelque chose ne va pas. »

La demande semble technique (« fais-moi un tableau de bord »), mais elle contient trois exigences très différentes. La première est **technique** : il faut des données qui se mettent à jour seules, organisées pour que les chiffres soient toujours calculés de la même façon. La deuxième est **visuelle** : il faut que la page se lise en quelques secondes, sans mode d'emploi. La troisième est **humaine** : il faut que la gérante s'en serve vraiment, que le jour où le tableau de bord signale un problème, elle sache ce qu'elle décidera. Un tableau de bord réussi est un **outil de décision** ; un tableau de bord raté est un joli tableau que l'on ouvre deux semaines, puis plus jamais.

Le chapitre précédent vous a donné les principes : choisir le bon graphique, soigner la mise en page, ne pas tromper. Ce chapitre les met en œuvre dans des **outils de tableaux de bord**, ceux que l'on rencontre le plus en entreprise, et il montre surtout ce qu'ils ont en commun, parce que les menus changent d'une version à l'autre alors que les idées durent.

> ⚠️ **Ce que ce chapitre ne fait pas, et pourquoi.** Power BI, Tableau, Looker, Metabase, Superset et Qlik sont des produits que **nous n'avons pas exécutés** pour écrire ce livre. Nous ne montrons donc **aucune capture de leurs écrans** et nous ne prétendons pas décrire leurs menus : ils changent d'une version à l'autre, et ce que nous en disons est à **vérifier dans la documentation de votre version**. Les figures de ce chapitre sont des **maquettes dessinées** avec matplotlib (rectangles génériques, aucune identité d'un produit), ou des graphiques calculés sur les données de la boutique. Ce qui peut être **vérifié** l'est : le modèle de données, les mesures, les filtres de sécurité et les chiffres de la page finale sont recalculés ici avec pandas et SQL, et chaque nombre du texte vient d'un calcul exécuté.

## Le chemin de ce chapitre

Le chapitre suit la demande de la gérante, de la donnée à l'écran, puis du premier outil au choix d'un outil.

- **2.1 Power BI : modèle, visuels, publication.** Avant de dessiner quoi que ce soit, on organise les données en **étoile** (une table de faits, des dimensions), on définit des **mesures** qui se recalculent selon les filtres, on choisit des **visuels**, puis on **publie** et on planifie l'actualisation. Power BI sert d'exemple de l'approche « modèle d'abord ».
- **2.2 Tableau : feuilles, tableaux de bord, partage.** Tableau illustre l'approche inverse, plus **exploratoire** : on compose des *feuilles* en glissant des champs sur des **marques** (position, couleur, taille), on ajoute des **calculs de table** et des **niveaux de détail**, puis on assemble les feuilles en tableau de bord. Les deux approches se rejoignent.
- **2.3 Conception d'un tableau de bord selon les besoins des utilisateurs.** La section la plus importante : **partir de la décision**, choisir peu d'indicateurs, les ranger en trois niveaux (vue d'ensemble, analyse, détail), tester en cinq secondes, **valider les chiffres** et prévoir l'**adoption**. Nous construisons la page complète de la gérante.
- **2.4 ➕ Power BI avancé.** Le langage des mesures (DAX), la préparation des données (Power Query), la **sécurité au niveau des lignes** et le déploiement, avec des équivalents pandas qui permettent de **vérifier** chaque résultat.
- **2.5 ➕ Looker, Metabase, Superset, Qlik.** Quatre autres familles d'outils, ce qui les distingue, et une méthode pour **choisir** sans se laisser guider par la marque.

Le chapitre se termine par un bilan, et le **cahier** propose huit applications (modèle en étoile, mesures, calculs de table, critique de tableaux de bord, sécurité, choix d'outil…) et douze exercices.

> 💡 **Intuition.** Un outil de tableaux de bord est une **chaîne de montage** : les données brutes entrent à gauche, un chiffre juste et lisible sort à droite, et à chaque étape on peut se tromper. La qualité d'un tableau de bord se joue **en amont** (le modèle, les définitions) autant qu'en aval (les couleurs et la disposition).

## Les données du chapitre

Nous reprenons la boutique des volumes précédents : les commandes de 2023 à 2025, les clients, les produits, les livraisons, les sessions du site, les stocks. Toutes les données sont **simulées**. Nous utilisons un fichier supplémentaire, `villes.csv`, qui associe chaque ville fictive à une **région fictive** (quatre régions, dans un plan inventé) : elle sert à illustrer la sécurité par région, sans aucune géographie réelle.

> 📦 **Les données.** `commandes.csv`, `lignes_commande.csv` (83 905 lignes, 2023 à 2025), `produits.csv`, `clients.csv`, `villes.csv`, `livraisons.csv`, `sessions_web.csv`, `stock_quotidien.csv`, `jours_exploitation.csv`. Le script `build/outils_ch02.py` contient le chargement, le modèle en étoile et le dessin des maquettes ; les définitions des indicateurs sont celles du volume III, chapitre 6 (KPI).

Deux rappels des volumes précédents serviront souvent. D'abord, **les 120 produits portent seulement 60 noms** : on relie toujours les tables par l'**identifiant** du produit, jamais par son nom (volume II, section 2.2.5). Ensuite, les chiffres d'affaires de la boutique sont en **euros TTC** pour les ventes et la marge se calcule **hors taxes** avec une TVA fixée à 20 % **pour l'illustration** (volume III, chapitre 6).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 et exercices 2.1 à 2.12 ; chacun renvoie à la section du livre qui l'éclaire.
