# Chapitre 5 : ➕ Confidentialité et anonymisation des données

> « Une donnée n'est pas anodine parce qu'elle est dans un tableau : elle parle encore de quelqu'un. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il est pourtant celui que l'on regrette le plus de ne pas avoir lu le jour où un fichier part par courriel. Il suppose le chapitre 1 (nettoyer), la section 2.5 (rapprocher des enregistrements) et un peu de pandas (volume I, chapitre 4).

La gérante de la boutique vous écrit un lundi matin. Un prestataire lui a proposé d'analyser sa clientèle : « Il veut un fichier avec nos clients, leur âge, leur ville, ce qu'ils ont acheté, s'ils sont contents. Je peux lui envoyer le CRM tel quel ? Ou si j'enlève les noms, c'est bon ? » Elle ajoute, un peu inquiète : « Un client m'a aussi demandé de supprimer toutes ses données. Combien de temps ça prend, au juste ? »

Ces deux questions n'ont rien de statistique, et pourtant ce sont des questions d'analyste. Vous êtes la personne qui **manipule** les fichiers : vous savez quelles colonnes existent, combien de lignes décrivent une même personne, ce qui se retrouve en croisant deux tableaux. Les juristes écrivent les règles ; c'est à vous de savoir **ce qu'un fichier contient vraiment** et ce que l'on peut en faire sortir. Ce chapitre vous donne les repères pour répondre à la gérante avec des chiffres plutôt qu'avec des impressions.

Deux idées le traversent. La première est que **retirer les noms ne suffit presque jamais** : une personne se reconnaît à son association de caractéristiques (une ville, une année de naissance, un canal, une carte de fidélité) bien avant son nom, et à plus forte raison à ses habitudes d'achat. La seconde est qu'il n'existe pas de procédé magique : chaque protection a un **prix** en information perdue, et l'on choisit un équilibre, que l'on documente.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un conseil juridique. Les règles de protection des données personnelles dépendent du pays, du secteur et de la date ; nous parlerons de principes **communs à la plupart des cadres** et nous citerons, à titre d'exemple seulement, le type de règles que l'on trouve dans les textes régionaux ou internationaux. Pour une décision réelle, consultez la personne qui, dans votre organisation, est chargée de la protection des données, ou un juriste.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 5.1 | Qu'est-ce qu'une donnée personnelle, et que doit-on en faire ? | Un identifiant direct n'est que la partie visible : les quasi-identifiants identifient aussi ; des principes simples guident l'analyste |
| 5.2 | Comment remplacer un identifiant sans le perdre ni le trahir ? | Pseudonymiser n'est pas anonymiser ; un hachage sans clé se retrouve par dictionnaire |
| 5.3 | Comment mesurer le risque de reconnaître une personne ? | Unicité, k-anonymat, recoupement, l-diversité ; la confidentialité différentielle en une page |
| 5.4 | Que faire concrètement, de lundi à vendredi ? | Minimiser, séparer, agréger, ne pas publier de petits groupes, vérifier avant d'envoyer |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateurs `build/donnees_a1.py` et `build/donnees_a2.py`) : la boutique est fictive, ses clients aussi, et leurs **noms sont inventés** à partir de syllabes, sans origine particulière. Nous connaissons donc la **vérité** (qui est qui) et nous nous en servons pour mesurer ce qu'un attaquant pourrait retrouver : en pratique, on ne la connaît pas, et c'est bien le problème.

- `crm_clients.csv` : le CRM de la boutique, **7 140 lignes** pour 6 000 clients (des doublons, 140 lignes de test), avec prénom, nom, e-mail, téléphone, ville, code postal, date de naissance, consentement (sections 5.1, 5.2).
- `verite_crm.csv` et `verite_identites.csv` : la vérité (à quel client correspond chaque ligne, quelle est la vraie identité), utilisée pour **juger** les attaques et les nettoyages, jamais comme une entrée de traitement.
- `clients.csv` et `profil_clients_verite.csv` : les 6 000 clients avec leur ville, leur année de naissance, leur canal d'acquisition, leur carte de fidélité, leur revenu estimé, leur dépense et leur satisfaction : c'est la table que l'on voudrait confier au prestataire (sections 5.3 et 5.4).
- `commandes.csv` et `lignes_commande.csv` : les commandes de 2023 à 2025, pour montrer qu'un **montant et une date** suffisent à reconnaître une commande (section 5.3).

```python hide
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2, GRILLE
import outils_ch05 as O
setup()
T = O.charger()
cli, pro, crm, vcrm, ident, cmd, lig = (T[k] for k in ["clients", "profil", "crm", "vcrm", "ident", "cmd", "lig"])
x = O.partage(T)
print("NUM n_crm", len(crm)); print("NUM n_clients", len(cli)); print("NUM n_tests", int((crm["prenom"] == "Test").sum()))
```
<!--sortie-->
```text
NUM n_crm 7140
NUM n_clients 6000
NUM n_tests 140
```
