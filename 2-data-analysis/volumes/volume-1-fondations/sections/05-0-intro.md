# Chapitre 5 : Types de données, collecte et conception d'enquêtes

> « Avant de demander ce que disent les données, demandez ce qu'elles mesurent, d'où elles viennent, et qui a décidé qu'elles existeraient. »

La gérante de la boutique vous tend une feuille. En 2025, l'équipe a invité par courriel les clients qui avaient commandé dans l'année à répondre à une enquête de satisfaction. Environ un client sur quatre a répondu, et la note moyenne est de **3,64 sur 5**. « C'est un beau chiffre, dit-elle. Est-ce que je peux le croire ? Est-ce que je peux le montrer à mon banquier ? »

Cette question n'est pas une question de statistique au sens des chapitres précédents : il ne s'agit ni de calculer une moyenne ni de tracer une courbe, mais de savoir **ce que ce chiffre représente**. Que veut dire « satisfait » quand on répond en cochant une case de 1 à 5 ? Peut-on calculer une moyenne de cases cochées ? Les clients qui ont répondu ressemblent-ils à ceux qui n'ont pas répondu ? Qui a rempli deux fois le formulaire, et qui a coché cinq fois « 5 » en huit secondes pour en finir ? Comment aurait-on dû poser les questions, et à qui ?

Tout le reste du volume suppose que l'on sache répondre à ces questions. Les chapitres de statistique, d'Excel, de SQL et de programmation vous donnent des outils pour **calculer** ; ce chapitre vous apprend à **regarder ce que l'on calcule**. Il est volontairement le dernier du volume : vous avez désormais assez de pratique pour que des exemples chiffrés, tirés des tables de la boutique, éclairent chaque idée.

> 🧭 **Ce que le chapitre suppose.** Les notions de moyenne, de médiane, d'écart-type et d'échantillon (chapitre 1) et l'usage de pandas (chapitre 4). Aucune autre notion n'est nécessaire ; les sections complémentaires (➕) utilisent un peu plus de code.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 5.1 | Que contient une colonne, et que peut-on calculer dessus ? | Un type statistique n'est pas un type informatique ; un tableau a un **grain** |
| 5.2 | D'où viennent les données, et que valent-elles ? | Chaque source a une population, une fraîcheur, un propriétaire, des droits… et un biais |
| 5.3 | Peut-on croire une enquête ? | Le chiffre dépend de qui répond : la non-réponse se mesure, se corrige un peu, se borne |
| ➕ 5.4 | Comment poser les questions, choisir les personnes, éviter les biais ? | Formulation, plans de sondage, taille d'échantillon, biais d'enquête |
| ➕ 5.5 | Comment collecter par API et par moissonnage de pages ? | Données ouvertes, API paginées et limitées, *scraping* poli et fragile |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a1.py`) : la boutique est fictive, ses clients aussi. Comme nous avons écrit le simulateur, nous connaissons la **vérité programmée** et la révélons quand elle éclaire une analyse : c'est un luxe que la vie réelle n'offre jamais.

- `clients.csv` : 6 000 clients, avec leur ville, leur année de naissance, leur canal d'acquisition, leur carte de fidélité (sections 5.1, 5.2, 5.4).
- `commandes.csv` et `lignes_commande.csv` : 36 395 commandes et 83 905 lignes de commande de 2023 à 2025 (sections 5.1 à 5.4).
- `produits.csv` : le catalogue de 120 produits (section 5.5).
- `retours.csv` : les lignes de commande retournées (section 5.4).
- `enquete_satisfaction.csv` : les **958 réponses** reçues à l'enquête de 2025 (sections 5.1 et 5.3). L'enquête a été envoyée à **3 875 clients invités**, soit tous ceux qui avaient commandé en 2025.
- Pour la section 5.5, un **mini-serveur local** (écrit dans `build/outils_ch05.py`) joue le rôle d'un site et d'une API : aucun accès réseau externe n'est nécessaire, et rien de ce qui est collecté ne sort de votre machine.

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
cli, cmd, lig, prod, ret, jr, enq = (T[k] for k in ["clients", "commandes", "lignes", "produits", "retours", "jours", "enquete"])
inv = O.invites(cmd, cli)
enq_u, ligne_droite = O.nettoyer_enquete(enq)
print("NUM n_clients", len(cli)); print("NUM n_cmd", len(cmd)); print("NUM n_lignes", len(lig)); print("NUM n_prod", len(prod))
print("NUM n_inv", len(inv)); print("NUM n_rep_brut", len(enq)); print("NUM n_rep_unique", len(enq_u))
print("NUM moy_brute", round(float(enq["satisfaction_globale"].mean()), 4))
print("NUM taux_rep", round(len(enq_u) / len(inv), 4))
```
<!--sortie-->
```text
NUM n_clients 6000
NUM n_cmd 36395
NUM n_lignes 83905
NUM n_prod 120
NUM n_inv 3875
NUM n_rep_brut 958
NUM n_rep_unique 931
NUM moy_brute 3.6388
NUM taux_rep 0.2403
```
