# Chapitre 4 : Documentation et dictionnaires de données

> « Un chiffre que personne ne peut refaire est un chiffre que personne ne peut défendre. »

```python hide
import os, sys, shutil, tempfile, json
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch04 as O
import fig_ch04 as F4
TMP4 = tempfile.mkdtemp(prefix="doc4_", dir=os.environ.get("TMPDIR"))
cmd = O.charger("commandes")
lig = O.charger("lignes_commande")
x = lig.merge(cmd, on="id_commande")
```

La gérante vous arrête devant la machine à café, un dossier à la main. « Ma collègue de la comptabilité a repris ton analyse du quatrième trimestre pour le bilan. **Elle ne retrouve pas ton chiffre.** Tu m'avais dit 211 434 € pour le Site, elle m'en annonce un autre. Qu'est-ce qui manque ? »

Vous reprenez la question avec calme, parce que vous savez qu'il y a deux réponses possibles. Ou bien l'un de vous deux s'est trompé, ou bien — c'est le cas le plus fréquent — **vous avez tous deux raison**, mais vous ne parlez pas du même chiffre. Faisons l'expérience sur les données de la boutique : quatre calculs honnêtes du « chiffre d'affaires du quatrième trimestre pour le canal Site », qui ne diffèrent que par un choix que personne n'a écrit.

```python
site_t4 = x[(x["canal"] == "Site") & (x["date_commande"] >= "2025-10-01")]
variantes = {
    "TTC, remises déduites, jusqu'au 31/12": site_t4["montant"].sum(),
    "hors taxe (TVA fictive de 20 %)": site_t4["montant"].sum() / 1.2,
    "avant remises": (site_t4["quantite"] * site_t4["prix_unitaire"]).sum(),
    "extraction arrêtée au 15/12": site_t4[site_t4["date_commande"] <= "2025-12-15"]["montant"].sum(),
}
for nom, v in variantes.items():
    print(f"{O.eur(v):>14}  {nom}")
```
<!--sortie-->
```text
  211 433,79 €  TTC, remises déduites, jusqu'au 31/12
  176 194,83 €  hors taxe (TVA fictive de 20 %)
  214 992,95 €  avant remises
  166 108,12 €  extraction arrêtée au 15/12
```

Quatre chiffres, tous **exacts**, séparés de près de 49 000 € entre le plus bas et le plus haut : la **taxe**, les **remises**, la **date** de l'extraction. Aucune erreur de calcul là-dedans ; ce qui manque, c'est la **phrase** qui dit lequel on a calculé. Voici ce que votre collègue aurait voulu trouver à côté du chiffre.

```python hide
F4.manque()
```
<!--sortie-->
```text
figure : ch04-ce-qui-manque.png
```

![Le chiffre de 211 434 € et les six questions que se pose quelqu'un qui doit le refaire : de quelle source, extraite quand, TTC ou HT, quelles lignes écartées, quelle définition du trimestre, avec quelle version du code.](figures/ch04-ce-qui-manque.png)

Ce chapitre vous apprend à répondre à ces six questions **avant** qu'on vous les pose : en **documentant** ce que l'on a reçu (les jeux de données), ce que l'on en a fait (les transformations), ce que veulent dire les colonnes (le dictionnaire) et, pour aller plus loin, **d'où vient chaque chiffre** (le lignage).

## Pourquoi un analyste documente

Documenter n'est pas de la bureaucratie ; c'est la partie du travail qui **rend le reste réutilisable**. Quatre raisons, que vous rencontrerez dès la première année.

- **Refaire.** Dans trois mois, la gérante vous demandera la même analyse sur le trimestre suivant. Si le travail est écrit, il se **rejoue** en dix minutes ; sinon, il se **refait** en trois jours, avec des résultats légèrement différents sans que l'on sache pourquoi.
- **Comprendre.** Une colonne `statut` qui contient `PAID`, `paid` et `Paid` ne se comprend pas toute seule. Une colonne `total` qui change d'unité en septembre non plus. La documentation rend ces pièges **visibles pour la personne suivante**, y compris vous dans six mois.
- **Auditer.** Un chiffre qui va dans un bilan, dans un dossier de banque ou dans une décision de prix peut être contesté. Pouvoir montrer la **chaîne** — la source, les règles, les contrôles — transforme une opinion en démonstration.
- **Transmettre.** Un jour, quelqu'un reprendra votre poste. La documentation est la différence entre une passation de dix minutes et une enquête de dix jours.

> 💡 **Intuition.** Documenter, c'est écrire pour **quelqu'un d'intelligent qui n'a pas assisté à la réunion**. Cette personne sait lire du Python, du SQL et des tableaux ; elle ne sait pas ce que **vous** saviez en le faisant. Presque toujours, cette personne, c'est vous dans six mois.

## Le chemin de ce chapitre

Le parcours essentiel suit deux étapes, qui correspondent aux deux choses que l'on documente.

- **4.1 Documenter les jeux de données et les transformations** : la fiche d'un jeu de données (d'où vient-il, que représente une ligne, que sait-on de ses défauts), puis le **journal** d'un nettoyage (une règle, une justification, des effectifs avant et après), écrit par le code lui-même.
- **4.2 Construire un dictionnaire de données** : que veut dire chaque colonne (libellé, type, unité, valeurs permises, codage des manquants, sensibilité), comment en fabriquer un squelette automatiquement, comment **vérifier qu'il reste vrai**, et comment s'accorder sur une définition unique de « client actif », de « commande annulée » ou de « panier moyen ».

Une section facultative prolonge ce parcours : **➕ 4.3 Lignage des données et pistes d'audit**, pour savoir **d'où vient** un chiffre, prouver qu'une entrée n'a pas changé (les empreintes), tenir un journal d'audit et rejouer un résultat depuis le brut grâce à sa documentation.

## Les données du chapitre

> 📦 **Quatre jeux de la boutique.** Le chapitre documente des fichiers que vous connaissez déjà ou que vous allez retrouver : `crm_clients.csv` (le CRM, 7 140 lignes, désordonné : il sert à l'exemple de la fiche et du journal), `clients.csv` et `produits.csv` (les référentiels propres du volume I), et `profil_clients.csv` (le profil de 6 000 clients, avec des valeurs manquantes : il sert à l'exemple du dictionnaire). Les commandes (`commandes.csv`, `lignes_commande.csv`) servent à calculer les chiffres que l'on documente. Tous sont **simulés** ; les fichiers `verite_*.csv` ne servent qu'à **juger** nos choix à la fin d'une étude : on ne les ouvre pas pour nettoyer.

Tout le code de ce chapitre est **réellement exécuté** : ce que vous lirez sous un bloc est ce que le code a produit, pas une illustration.

> 📒 **Pour s'entraîner.** Le chapitre 4 du cahier propose huit applications (fiches, journaux, dictionnaires, lignage, empreintes) et douze exercices corrigés ; chaque section du livre indique ceux qui la prolongent.
