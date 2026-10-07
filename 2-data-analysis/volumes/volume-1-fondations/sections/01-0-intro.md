# Chapitre 1 : Les essentiels de la statistique

> « Un chiffre sans contexte est une opinion qui se fait passer pour un fait. »

C'est votre deuxième semaine à la boutique. La gérante passe la tête dans la porte de votre bureau, un tableau imprimé à la main :

— Notre panier moyen est de **100 €**. C'est un bon chiffre ?

Vous ouvrez la bouche pour répondre « oui » ou « non », et vous vous arrêtez. Bon **par rapport à quoi** ? À l'an dernier, à ce que fait la concurrence, à ce qu'il faudrait pour couvrir les frais ? Et surtout : ce « 100 € » est-il un montant que **beaucoup de clients dépensent vraiment**, ou le résultat de quelques grosses commandes qui tirent la moyenne vers le haut ? Les deux situations donnent le même chiffre, et pourtant elles appellent des décisions très différentes.

Ce chapitre vous donne le **vocabulaire** pour répondre à ce genre de question. La statistique que vous allez y rencontrer n'est pas de la « grosse mathématique » : c'est un petit nombre d'idées, que l'on retrouve à chaque analyse, et qu'il faut avoir **dans les doigts** avant d'ouvrir Excel, d'écrire une requête SQL ou de lancer un notebook.

## Le chemin de ce chapitre

Le **parcours essentiel** compte quatre sections, qui répondent chacune à une question de la gérante :

- **1.1 Statistique descriptive** : *comment résumer des milliers de commandes en quelques nombres honnêtes ?* Le centre (moyenne, médiane), la dispersion (écart-type, quartiles), la forme (asymétrie, valeurs aberrantes), et les moyennes qui trompent.
- **1.2 Distributions et courbe normale** : *quelle forme prennent les phénomènes que nous observons ?* Compter des retours, des commandes, mesurer des âges, des montants : quelques « lois » suffisent pour décrire la plupart des situations.
- **1.3 Échantillonnage et erreur d'échantillonnage** : *si je n'observe qu'une partie des clients, de combien mon chiffre peut-il se tromper ?* L'intervalle de confiance, la taille d'échantillon, et les biais qu'aucune taille d'échantillon ne corrige.
- **1.4 Corrélation et causalité** : *les ventes montent quand la publicité monte : est-ce la publicité qui les fait monter ?* Mesurer une liaison, puis apprendre à ne pas en tirer de conclusion hâtive.

Une section facultative (➕) complète le tout : **1.5 Mathématiques du quotidien en entreprise**, avec les pourcentages, les taux de croissance, les moyennes pondérées, les marges et les arrondis, c'est-à-dire les calculs que vous ferez **tous les jours**.

> 🧭 **Comment lire ce chapitre.** Chaque notion suit le même rythme : une **question** concrète, un **petit exemple calculé à la main** (sur quelques lignes, pour que vous voyiez ce qui se passe), la **formule** expliquée, puis l'**application aux données de la boutique**. Le code est réduit au strict nécessaire : l'essentiel est de comprendre ce que l'on calcule. Les exercices et les applications à refaire se trouvent dans le **cahier**, signalé par le symbole 📒 à la fin de chaque section.

## Les données du chapitre

> 📦 **Les données.** Tout le volume s'appuie sur les données **simulées** de la boutique (le générateur est dans `build/donnees_a1.py`) : une petite enseigne de maison et de décoration, avec **6 catégories** et **120 produits**, trois canaux de vente (`Boutique`, `Site`, `Réseaux`) et des clients répartis dans vingt villes fictives (« Ville A » à « Ville T »). Dans ce chapitre, nous utilisons :
>
> - `commandes.csv` et `lignes_commande.csv` : environ 36 395 commandes et 83 905 lignes de commande entre janvier 2023 et décembre 2025 ;
> - `clients.csv` : 6 000 clients inscrits ;
> - `retours.csv` : les lignes que les clients ont renvoyées ;
> - `jours_exploitation.csv` : une ligne par jour (commandes, chiffre d'affaires, météo, promotion, dépense publicitaire).
>
> Comme les données sont fabriquées, nous connaissons la **vérité** qui les a générées, et nous la révélerons au fil du chapitre : c'est le seul moyen de **vérifier** qu'une méthode statistique répond bien à la question posée, ce que la réalité ne permet presque jamais.

Une commande est composée d'une ou de plusieurs **lignes** (un produit, une quantité, un prix). Le **panier** d'une commande est la somme des montants de ses lignes : c'est la grandeur que la gérante appelle « panier moyen » quand elle fait la moyenne sur toutes les commandes. Chargeons les données et calculons ce premier chiffre.

```python
import pandas as pd
commandes = pd.read_csv("donnees/commandes.csv")
lignes = pd.read_csv("donnees/lignes_commande.csv")
panier = lignes.groupby("id_commande")["montant"].sum()     # une commande = une ou plusieurs lignes
print(len(commandes), "commandes,", len(lignes), "lignes")
print("panier moyen :", round(panier.mean(), 2), "€")
```
<!--sortie-->
```text
36395 commandes, 83905 lignes
panier moyen : 100.38 €
```

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET, GRILLE
style.setup()
import outils_ch01 as O
X = O.X
def NUM(cle, valeur):
    print("NUM", cle, valeur)
d = O.charger()
cmd, lig, jours, cli = d.commandes, d.lignes, d.jours, d.clients
NUM("panier_moyen", panier.mean())
NUM("n_commandes", len(commandes))
NUM("n_lignes", len(lignes))
NUM("n_clients", len(cli))
assert abs(cmd["panier"].mean() - panier.mean()) < 1e-9
```
<!--sortie-->
```text
NUM panier_moyen 100.37525154554197
NUM n_commandes 36395
NUM n_lignes 83905
NUM n_clients 6000
```

Cette moyenne est exacte, mais elle ne répond pas encore à la question de la gérante. Les quatre sections qui suivent expliquent pourquoi, et ce qu'il faut calculer **en plus**.
