# Chapitre 1 : Entrepôts de données et modélisation

> « Une donnée ne sert que si tout le monde, en la lisant, comprend la même chose. »

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

D = os.environ["DONNEES"]
con = O.ouvrir(D)                      # base DuckDB en mémoire : schéma src = la base opérationnelle de la boutique
ca = con.df("""SELECT SUM(l.montant) AS ttc, SUM(l.montant) / 1.2 AS ht
               FROM src.lignes_commande l JOIN src.commandes c USING (id_commande) WHERE year(c.date_commande) = 2025""").iloc[0]
rb = con.df("SELECT SUM(montant_rembourse) AS r FROM src.retours WHERE year(date_retour) = 2025")["r"][0]
fp_naif = con.df("SELECT SUM(c.frais_port) AS f FROM src.commandes c JOIN src.lignes_commande l USING (id_commande) WHERE year(c.date_commande) = 2025")["f"][0]
fp_vrai = con.df("SELECT SUM(frais_port) AS f FROM src.commandes WHERE year(date_commande) = 2025")["f"][0]
quatre = {"Classeur Excel (export des ventes)": ca["ttc"], "Tableau de bord (hors taxe)": ca["ht"],
          "Rapport (hors taxe, net des retours)": ca["ht"] - rb / 1.2, "Requête d'un collègue (ventes + frais de port)": ca["ttc"] + fp_naif}
assert [round(v) for v in quatre.values()] == [1324764, 1103970, 1034230, 1352838]
assert round(fp_vrai, 1) == 17415.5 and round(fp_naif) == 28074
O.fig_trois_chiffres(quatre)
```
<!--sortie-->
```text
figure : ch01-trois-chiffres.png
```

## Un chiffre d'affaires, quatre réponses

Un mercredi, la gérante pose devant vous trois documents. Le classeur Excel que lui envoie chaque mois la personne qui prépare la comptabilité dit : **1 324 764 €** de chiffre d'affaires en 2025. Le tableau de bord de la boutique dit : **1 103 970 €**. Le rapport trimestriel, rédigé par un ancien stagiaire, dit : **1 034 230 €**. Elle ne demande pas lequel est faux. Elle demande : « **Je voudrais le même chiffre partout. Pourquoi est-ce si difficile ?** »

Vous cherchez, et vous trouvez que **personne ne s'est trompé en calculant**. Les trois documents partent de la même base, mais chacun a, sans le dire, **sa propre définition** du chiffre d'affaires :

- le classeur additionne les montants des lignes de commande **toutes taxes comprises** (TTC) ;
- le tableau de bord les divise par 1,2 pour obtenir le chiffre **hors taxe** (la TVA de la boutique fictive est de 20 %) ;
- le rapport retranche en plus les **remboursements** de l'année, calculés à la date du retour, et non à la date de la vente.

Et ce n'est pas tout. Un collègue du service informatique a écrit une requête qui donne **1 352 838 €**, plus que le classeur. Il a joint les lignes de commande aux commandes pour récupérer les **frais de port**, qui sont enregistrés une seule fois par commande, et il les a donc **additionnés autant de fois que la commande a de lignes**. Ce quatrième chiffre n'est pas une définition différente : c'est une **erreur**, et elle est silencieuse, parce que le résultat a l'air raisonnable.

![Quatre « chiffres d'affaires 2025 » calculés à partir de la même base : trois définitions (TTC, hors taxe, net des retours) et une erreur de jointure (frais de port comptés plusieurs fois, en orange).](figures/ch01-trois-chiffres.png)

Voilà le problème que résout un **entrepôt de données**. Ce n'est pas un logiciel plus rapide. C'est un **lieu**, avec des **règles**, où l'on décide une fois pour toutes :

1. ce que **représente une ligne** de chaque table (une ligne de commande, une commande, un retour, un jour de stock) ;
2. ce que **signifie chaque chiffre** (hors taxe, brut des retours, sans les frais de port) et à partir de **quelle colonne** on l'obtient ;
3. comment **ces tables se relient** entre elles, de façon que personne n'ait à deviner une jointure.

> 💡 **Intuition.** Une base opérationnelle est organisée pour **enregistrer** correctement (une commande, une fois). Un entrepôt est organisé pour **comparer et additionner** correctement (le chiffre d'affaires, toujours le même, quelle que soit la personne qui le demande). Ce sont deux métiers différents, donc deux organisations différentes.

Dans ce volume, vous passez des **analyses ponctuelles** (un chiffre, un jour, un notebook) aux **systèmes reproductibles** (un chiffre qui se recalcule seul, se contrôle et s'explique). Ce chapitre pose la première pierre : **où et comment ranger les données** pour qu'elles se laissent additionner sans pièges. Le chapitre 2 apprendra à **les y amener** automatiquement.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de la source de la confusion à la conception d'un entrepôt.

- **1.1 Concepts d'entrepôt de données.** Deux manières d'utiliser les données (enregistrer ou analyser), les **couches** (arrivée, entrepôt, marts), **ETL ou ELT**, entrepôt ou lac de données, et ce qu'un entrepôt ne fait pas.
- **1.2 Schéma en étoile.** Une table de **faits** au centre, des **dimensions** autour. Nous construisons l'étoile de la boutique **en SQL**, nous l'interrogeons, et nous **vérifions** qu'elle retrouve à l'euro près le chiffre d'affaires de la comptabilité.
- **1.3 Faits, dimensions et granularité.** **Déclarer le grain**, distinguer les mesures **additives**, **semi-additives** et **non additives**, traiter les frais de port, choisir entre trois types de tables de faits, et éviter le piège de la jointure entre deux faits.
- **1.4 ➕ Modélisation dimensionnelle.** Quand les attributs **changent** (un client déménage, un produit change de catégorie) : les dimensions à évolution lente, la **matrice des processus** et les **data marts**.
- **1.5 ➕ BigQuery, Snowflake, Redshift, Azure Synapse.** Ce que les entrepôts infonuagiques changent et ne changent pas ; le stockage **en colonnes** et le **partitionnement**, démontrés **en local** avec Parquet.

## Les données du chapitre

> 📦 **Les données.** La base de la boutique des volumes précédents, **simulée** : `clients`, `produits`, `commandes`, `lignes_commande`, `retours`, `livraisons`, `stock_quotidien` et `compte_resultat_mensuel`. Comme le jeu du volume III ne contient pas de **frais de port**, nous en ajoutons une version **calculée par une règle simple** (gratuits en retrait en magasin ou à partir de 80 € de commande, 5,90 € à domicile, 3,90 € en point relais) : c'est ce qui nous permet d'illustrer les mesures d'en-tête. Deux petits fichiers **simulés** (`donnees/ch01-historique-clients.csv` et `ch01-historique-produits.csv`, générés par `build/outils_ch01.py`) donnent l'historique des changements de ville et de catégorie utilisé en 1.4.

L'« entrepôt » de ce chapitre est une base **DuckDB** en mémoire : un moteur SQL gratuit, installé en une ligne, qui lit directement les fichiers CSV et Parquet. Il joue le même rôle que les entrepôts infonuagiques de la section 1.5 pour ce qui est du **modèle** (les tables, les clés, les jointures), à une échelle que votre ordinateur supporte. **Aucun service infonuagique n'est exécuté ici.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 et exercices 1.1 à 1.12 ; chacun renvoie à la section du livre qui l'éclaire.
