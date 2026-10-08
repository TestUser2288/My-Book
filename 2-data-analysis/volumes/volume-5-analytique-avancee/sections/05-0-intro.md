# Chapitre 5 : Utiliser les LLM pour l'analyse

> « Un assistant qui répond toujours avec aplomb est un excellent rédacteur et un témoin dangereux. »

```python hide
import os, sys, json, re, shutil, tempfile, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch05 as O
import fig_ch05 as F

REP = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))                 # dossier de travail du chapitre, supprimé dans le bilan
BASE = O.construire_entrepot(os.path.join(REP, "boutique.duckdb"))
con = O.ouvrir_lecture(BASE)                                         # connexion en lecture seule : celle du harnais
qs = O.questions_or()
refs = O.references(con, qs)
sorties = O.charger_json("ch05-sorties-modele.json")
prop = O.charger_json("ch05-propositions.json")
print("questions de référence :", len(qs), "| tables :", ", ".join(O.TABLES))
```
<!--sortie-->
```text
questions de référence : 20 | tables : commandes, lignes_commande, produits, clients, livraisons, retours
```
<!--sortie-->

## Un lundi matin, une bonne idée

Un collègue de l'équipe passe la tête dans la porte de votre bureau :

> « *Chaque lundi, on perd une heure à écrire les mêmes requêtes et le même commentaire pour la gérante. On pourrait demander à l'IA de les écrire à notre place, non ?* »

L'idée est excellente, et elle est dangereuse **pour la même raison** : un modèle de langage écrit très vite, très bien, et sans jamais dire « je ne sais pas ». Une requête qui compte les noms de produits au lieu des produits, un commentaire qui annonce « 1,8 M€ » quand le chiffre d'affaires du mois est de 184 k€ : ces erreurs ne se voient pas à la lecture, parce qu'elles sont écrites avec le même aplomb que les phrases justes. La gérante vous le dit avec son bon sens habituel :

> « *Si c'est plus rapide, tant mieux. Mais le jour où je donne un chiffre au comité, je veux savoir d'où il vient et qui l'a vérifié.* »

Ce chapitre répond à cette phrase. Vous n'y apprendrez pas à « bien parler à l'IA » : vous y apprendrez à **encadrer** un outil qui se trompe de manière imprévisible, c'est-à-dire à construire autour de lui ce que les chapitres 1 et 2 vous ont appris à construire autour d'une source de données : un **schéma connu**, des **contrôles automatiques**, un **journal** et une **relecture humaine** là où elle est indispensable. Le modèle est un **brouillon rapide** ; le harnais est ce qui permet de s'en servir sans y croire aveuglément.

> 💡 **Intuition.** Pensez à un stagiaire brillant, rapide, qui a tout lu et ne vérifie jamais rien. Vous lui confiez des brouillons, jamais une signature. Tout le chapitre tient dans la différence entre « il a écrit » et « nous avons vérifié ».

## Le chemin de ce chapitre

Le chapitre est complémentaire (➕) : il se lit après les quatre premiers, dont il emprunte les outils (SQL du volume I, tests de qualité et journal du chapitre 2, entrepôt du chapitre 1).

- **5.1 Ce qu'est un LLM pour un analyste.** Prédire le mot suivant, les jetons et la fenêtre de contexte, le hasard et la température, la confidentialité, modèle hébergé ou local, et l'anatomie d'un bon prompt.
- **5.2 Text-to-SQL.** Donner le schéma, voir les façons typiques de se tromper, puis construire **le harnais** : validation avec sqlglot, lecture seule, exécution bornée, comparaison à une référence, boucle de correction et journal.
- **5.3 Données synthétiques.** Produire des données de test sans toucher aux vraies, et mesurer à quel point elles ressemblent (ou trop) au réel.
- **5.4 Rédiger des rapports.** Donner au modèle des chiffres calculés plutôt que des données, et vérifier **chaque nombre** du texte produit.
- **5.5 Bonnes pratiques et limites.** Évaluation continue, journalisation, injection de prompt, biais, reproductibilité, coût, cadre éthique, et ce qu'un analyste ne délègue pas.

## Les données du chapitre

> 📦 **Les données.** La base de la boutique des volumes précédents, **simulée**, chargée dans un fichier DuckDB en **lecture seule** : `commandes` (avec une colonne `frais_port` ajoutée pour ce chapitre, une valeur par commande), `lignes_commande`, `produits`, `clients`, `livraisons`, `retours`. Un jeu de **vingt questions de référence** (`donnees/ch05-questions-or.csv`) associe à chaque question en français la requête SQL « or » dont nous avons contrôlé le résultat.

Un mot d'honnêteté sur les « sorties de modèle » de ce chapitre, parce que c'est le point le plus facile à mal comprendre. **Aucun service de modèle de langage n'est utilisé ici** : pas d'accès à Internet, pas de compte. Nous avons donc trois sources, toujours **étiquetées** :

| Source | Ce que c'est | Ce que cela prouve |
|---|---|---|
| **Petit modèle local** | un modèle de 135 millions de paramètres (SmolLM2-135M-Instruct), exécuté hors ligne ; ses sorties sont **enregistrées** dans `donnees/ch05-sorties-modele.json` | un vrai modèle, mais minuscule : ses erreurs sont nombreuses, et c'est utile pour étudier le harnais |
| **Réponses illustratives** | requêtes et textes **écrits par l'auteur** pour représenter des erreurs fréquentes | un catalogue d'erreurs réalistes, **pas** une mesure de la qualité d'un produit |
| **Imitations programmées** | un générateur de données qui reproduit exprès des défauts typiques | un moyen de tester les tests |

Aucune sortie n'est attribuée à un produit ou à une version précise, et **aucun taux de réussite de ce chapitre ne dit quoi que ce soit sur la qualité d'un modèle du commerce**. Ce qui, en revanche, est **réel et exécuté** de bout en bout : l'entrepôt, la validation, l'exécution bornée, la comparaison aux références, le vérificateur de nombres, les tests de données synthétiques. C'est cela que vous réutiliserez avec le modèle de votre choix.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.7 et exercices 5.1 à 5.12, section par section.
