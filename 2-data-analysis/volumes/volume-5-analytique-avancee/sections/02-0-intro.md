# Chapitre 2 : ETL et automatisation des flux de travail

> « Un chiffre fabriqué à la main n'est juste que les lundis où personne n'est en congé. »

```python hide
import os, sys, io, re, json, time, shutil, warnings, logging
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
logging.getLogger("apscheduler").setLevel(logging.CRITICAL)      # les refus d'exécution sont comptés, pas affichés
sys.path.insert(0, "build")
import outils_ch02 as P
from outils_ch02 import fr
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE
setup()
DEPOT = os.path.join(os.environ["DONNEES"], "ch02-depot")
VERITE = P.verite(DEPOT)
```

## Le lundi où vous n'étiez pas là

Chaque lundi matin, la gérante reçoit le point de la semaine : le chiffre d'affaires du mois en cours, par canal, avec les commandes et le panier moyen. Depuis le début de l'année, c'est vous qui le fabriquez. Le système de commandes dépose un fichier par mois ; vous l'ouvrez, vous corrigez ce qui doit l'être (une date mal écrite, une colonne renommée, quelques lignes en double), vous collez le résultat dans le classeur de suivi, vous actualisez les tableaux croisés, puis vous envoyez le message. Quarante-cinq minutes, quand tout va bien.

Un lundi de novembre, vous êtes en congé. Un collègue prend le relais, de bonne foi. Il ouvre le fichier du mois d'octobre, livré le 3 novembre, il le colle, il envoie. Personne ne voit rien. Voici ce que le fichier contenait vraiment.

```python
chemin = os.path.join(DEPOT, "commandes_2025-10.csv")
recu = pd.read_csv(chemin)
print("lignes dans le fichier livré :", len(recu))
print("chiffre d'affaires du fichier :", fr(recu["montant"].sum(), 0), "€")
print("chiffre d'affaires réel d'octobre :", fr(VERITE["par_mois"]["2025-10"]["total_original"], 0), "€")
print("écart :", fr((recu["montant"].sum() / VERITE["par_mois"]["2025-10"]["total_original"] - 1) * 100, 1, True), "%")
```
<!--sortie-->
```text
lignes dans le fichier livré : 2249
chiffre d'affaires du fichier : 102 601 €
chiffre d'affaires réel d'octobre : 120 064 €
écart : −14,5 %
```

Le fichier s'est **interrompu en route** : il manque environ une ligne sur sept, donc près de quinze pour cent du chiffre d'affaires. L'exportateur annonçait pourtant 2 645 lignes, mais personne ne l'a comparé à ce qu'il a reçu. La gérante a décidé, pendant trois semaines, avec un chiffre d'octobre trop faible de près de 17 500 €. Aucune faute de calcul : un **processus** qui ne contrôle rien et qui dépend d'une personne.

> 💡 **Intuition.** Ce n'est pas la personne en congé qui a failli, c'est la chaîne. Une chaîne manuelle repose sur le regard de quelqu'un qui « sent » que quelque chose cloche ; un programme n'a que les contrôles qu'on lui a écrits. L'automatisation n'est donc pas « faire plus vite » : c'est **écrire ce que le regard faisait sans le dire**.

Ce chapitre construit, pas à pas, la chaîne qui aurait évité cela. Elle lit les fichiers qui arrivent, les contrôle, met de côté ce qui est douteux, charge le reste dans un entrepôt sans jamais le charger deux fois, s'exécute à heure fixe, raconte ce qu'elle fait dans un journal, prévient quand elle échoue, et envoie le rapport. Chaque pièce est simple. Le travail est de les faire tenir ensemble.

## Le chemin de ce chapitre

| Section | La question de départ | Ce que vous saurez faire |
|---|---|---|
| **2.1 Principes de l'ETL** | « Comment passe-t-on d'un fichier livré à une table fiable ? » | extraire, transformer, charger ; chargement complet ou incrémental ; **idempotence** (relancer sans doubler) |
| **2.2 Scripts planifiés et pipelines** | « Et si cela se lançait tout seul, le 3 de chaque mois ? » | découper en étapes, paramétrer, lancer en ligne de commande, planifier (cron, APScheduler), rattraper des mois manqués, éviter deux exécutions simultanées |
| **2.3 Erreurs et journalisation** | « Comment sait-on que ça a marché, et pourquoi ça n'a pas marché ? » | journal, table des exécutions, quarantaine, contrôles avant et après, reprises, **alertes utiles** |
| **➕ 2.4 Outils d'orchestration** | « Existe-t-il quelque chose de plus solide que mon script ? » | ce que font dbt, Airflow et les outils bas-code (décrits, non exécutés) ; deux jouets exécutés pour comprendre le principe |
| **➕ 2.5 Automatisation robotisée** | « Et quand il n'y a ni fichier ni API ? » | quand un robot qui manipule un écran se justifie, et pourquoi il reste le dernier recours |
| **➕ 2.6 API et diffusion** | « Comment lire un service en ligne, et envoyer le rapport ? » | lire une API paginée avec reprises, gérer ses secrets, envoyer un e-mail avec pièce jointe, penser à la diffusion |

Les sections 2.1 à 2.3 forment le parcours essentiel et se lisent dans l'ordre. Les trois suivantes sont facultatives et indépendantes l'une de l'autre.

## Les données du chapitre

> 📦 **Données du chapitre.** Un **dépôt** de fichiers livrés par le système de commandes de la boutique, dans `donnees/ch02-depot/`, et deux référentiels du volume III (`clients.csv`, `produits.csv`). Tout est **simulé**, avec une graine fixe (script `build/outils_ch02.py`).

Le dépôt contient un fichier par mois de 2025 (`commandes_2025-01.csv` à `commandes_2025-12.csv`), une ligne par **ligne de commande** (identifiant de ligne et de commande, date, client, canal, produit, quantité, montant TTC), et un **manifeste** qui indique, pour chaque fichier, sa date de livraison et le nombre de lignes que l'exportateur dit avoir écrites. Le total des lignes d'origine est celui du volume III : 29 827 lignes, 12 946 commandes, 1 324 764 € de chiffre d'affaires TTC en 2025.

Trois mois ont été livrés **deux fois** : un premier fichier défectueux, puis un renvoi avec le suffixe `_v2`.

```python
man = P.manifeste(DEPOT)
print("fichiers :", len(man), "| mois :", man["mois"].nunique(), "| lignes annoncées au total :", int(man["lignes_annoncees"].sum()))
print(man.groupby("mois").size().loc[lambda s: s > 1].rename("fichiers").to_string())
```
<!--sortie-->
```text
fichiers : 15 | mois : 12 | lignes annoncées au total : 37074
mois
2025-03    2
2025-09    2
2025-10    2
```

Les fichiers ne sont pas tous propres, et c'est voulu : un format qui change en cours d'année, un encodage différent, un fichier vide, des lignes en double, des clients inconnus. Vous les découvrirez en chemin, comme dans la vraie vie, et leur liste complète (la « vérité programmée ») sera donnée dans le bilan du chapitre pour que vous puissiez juger ce que votre pipeline a trouvé.

> ⚠️ **Piège : un exemple à taille réelle, pas un jouet.** Les fichiers sont petits (moins de 200 Ko), mais les défauts sont de ceux que l'on rencontre vraiment. Un pipeline qui ne traite que le cas propre n'a pas été testé.

## Ce que ce chapitre suppose

- **SQL et Python** : volume I, chapitres 3 et 4 (nous utilisons **DuckDB**, une base de données qui tient dans un fichier et s'interroge en SQL, comme entrepôt local ; volume I, section 3.6.4).
- **Nettoyage et contrôles de qualité** : volume II, chapitre 1 (formats, dates, doublons), section 3.2 (contrôles de validation) et section 3.5 (pandera). Ici, on ne refait pas ces contrôles : on les **branche dans une chaîne qui se déclenche seule**.
- **Rapport automatisé simple** : volume IV, section 4.4 (un programme qui produit le rapport de la semaine). Ce chapitre en est le prolongement industriel : ce qu'il faut autour pour qu'on puisse **lui faire confiance un lundi de congé**.
- **Entrepôt de données** : chapitre 1 de ce volume. Nous y renvoyons pour le schéma en étoile (section 1.2) et la granularité (section 1.3). La cible de ce chapitre en est une version minimale, expliquée au fil du texte.

## Ce qui est exécuté, et ce qui ne l'est pas

Tout le code de ce chapitre tourne sur une machine ordinaire, hors ligne : l'entrepôt est un fichier DuckDB créé dans un dossier temporaire, la « planification » utilise la bibliothèque APScheduler sur des échéances de quelques secondes, l'API est un petit service lancé localement sur le port 20120 puis arrêté, le serveur d'e-mail est un serveur de **test** local sur le port 20130 : aucun message ne quitte la machine. Les produits qui ne sont pas installés ici (dbt, Airflow, Power Automate, UiPath, les entrepôts infonuagiques) sont **décrits, jamais exécutés**, et chaque extrait de code qui les concerne porte la mention « non exécuté ». Les menus et les noms de paramètres de ces produits changent d'une version à l'autre : vérifiez-les dans la documentation de votre version.
