# Chapitre 3 : SQL

> « Une question bien posée à une base de données vaut mieux que dix tableaux copiés à la main. »

```python hide
import os, shutil, sqlite3, sys, tempfile
import pandas as pd
sys.path.insert(0, "build")
TMP3 = tempfile.mkdtemp(prefix="sql3_", dir=os.environ.get("TMPDIR"))
shutil.copy(os.path.join(os.environ["DONNEES"], "boutique.db"), os.path.join(TMP3, "boutique.db"))
con = sqlite3.connect(os.path.join(TMP3, "boutique.db"))     # copie jetable : on peut créer des index et des vues sans toucher au fichier du dépôt
```

La gérante de la boutique vous arrête dans le couloir : « Je prépare mon bilan de l'année. **Quels sont nos dix meilleurs clients de 2025, et que représentent-ils dans notre chiffre d'affaires ?** » La question tient en une phrase. La réponse, elle, se cache dans deux tables de plusieurs dizaines de milliers de lignes : la liste des commandes, et le détail de chacune. Vous pourriez ouvrir un classeur, copier, trier, additionner à la main ; vous y passeriez la matinée, et personne ne saurait demain comment vous avez obtenu votre chiffre.

Ce chapitre vous apprend à poser cette question **à la base de données elle-même**, dans le langage prévu pour cela : le **SQL** (*Structured Query Language*, que l'on prononce « esse-ku-elle » ou « sicouèle »). À la fin du chapitre, vous répondrez à la question de la gérante en une requête de quelques lignes, **vous la vérifierez par un autre outil**, et vous pourrez la relancer l'an prochain en changeant une date.

## Pourquoi un analyste a besoin du SQL

Une grande partie des données d'une entreprise ne vit pas dans des fichiers, mais dans des **bases de données relationnelles** : la caisse, le site, la comptabilité, la logistique y écrivent en continu. Pour les lire, on ne copie pas les tables dans un tableur : on **interroge** la base. Trois raisons rendent cette compétence centrale pour une analyste.

- **L'échelle.** Un tableur se traîne à partir de quelques centaines de milliers de lignes ; une base répond en quelques instants à des questions sur des millions de lignes, parce qu'elle sait **filtrer, joindre et agréger près des données**, sans les déplacer.
- **La source unique.** Quand tout le monde interroge la même base, tout le monde parle du même chiffre d'affaires. Un classeur recopié, lui, devient vite un chiffre de plus.
- **La reproductibilité.** Une requête est un texte : on la relit, on la fait relire, on la rejoue le mois suivant, on la met sous contrôle de version. Un clic dans un tableur ne laisse aucune trace.

> 💡 **Intuition.** Une requête SQL ne dit pas **comment** calculer (quelles boucles, dans quel ordre), mais **ce que l'on veut** : quelles colonnes, de quelles tables, avec quelles conditions, regroupées comment. C'est le moteur de la base qui choisit la méthode. On parle d'un langage **déclaratif**. C'est ce qui rend le SQL à la fois court et exigeant : il faut savoir **décrire précisément le résultat attendu**, y compris la ligne qui, sur le tableau final, représente « une commande », « un client » ou « un mois ».

## Le chemin de ce chapitre

Le parcours essentiel suit les quatre idées qui font 90 % du travail quotidien d'une analyste.

- **3.1 SELECT, filtrage, tri, agrégation** : lire une table, garder les lignes qui comptent, les trier, les regrouper et les résumer ; comprendre l'ordre dans lequel le moteur exécute une requête, et la valeur absente (`NULL`).
- **3.2 Jointures** : recoller les tables entre elles (clients, commandes, produits), garder ou non les lignes sans correspondance, et éviter le piège le plus coûteux du métier : **la multiplication silencieuse des lignes**.
- **3.3 Fonctions fenêtres** : calculer un classement, un cumul, une moyenne mobile ou une évolution d'un mois sur l'autre **sans perdre le détail** des lignes.
- **3.4 CTE et structuration de requêtes complexes** : découper une longue requête en étapes nommées, la construire avec méthode, et la **vérifier** par un second outil.

Deux sections facultatives prolongent ce parcours : **➕ 3.5 SQL avancé** (sous-requêtes, index, vues, transactions, déclencheurs, sécurité) et **➕ 3.6 Différences entre PostgreSQL, MySQL, SQL Server et Oracle** (les dialectes que vous rencontrerez en entreprise).

## Les données du chapitre

> 📦 **La base `boutique.db`.** Tout le chapitre travaille sur une petite base **SQLite** (un fichier unique, sans serveur à installer) qui décrit **trois ans d'activité de la boutique** (2023 à 2025) : les clients, les produits, les commandes et leurs lignes, les retours, et un tableau de bord journalier. **Les données sont simulées**, avec des graines fixes : aucun client, aucun produit réel. La section 3.1.1 en dessine le schéma.

Les requêtes de ce chapitre sont **réellement exécutées** : les tableaux que vous verrez sous chaque bloc sont les résultats produits par SQLite (version 3.46) au moment où le livre a été fabriqué, pas des résultats imaginés. Deux précautions de lecture :

- le chapitre travaille sur une **copie jetable** de la base, ce qui nous autorise à créer des index ou des vues sans rien abîmer ;
- le SQL est un langage normalisé, mais **chaque produit a son dialecte**. Ce que vous lirez ici est du SQL courant, qui fonctionne tel quel sur la plupart des bases ; ce qui est propre à SQLite est signalé, et la section 3.6 dresse la liste des différences.

> 🧭 **En pratique : lire les résultats avec un œil d'analyste.** Après chaque requête, posez-vous toujours trois questions : *combien de lignes attendais-je ? quelle est la signification d'une ligne du résultat ? ce chiffre est-il plausible ?* Le chapitre vous y entraîne en comparant systématiquement les résultats à des ordres de grandeur connus (36 395 commandes, un chiffre d'affaires annuel de l'ordre du million d'euros…) et, quand c'est possible, à un second outil.

Les applications guidées et les exercices de ce chapitre sont dans le cahier : vous y trouverez une base prête à l'emploi et une trentaine de requêtes à écrire, corrigées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 et exercices 3.1 à 3.14 (chacun renvoie à la section du livre qu'il met en pratique).
