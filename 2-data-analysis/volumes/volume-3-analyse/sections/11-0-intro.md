# Chapitre 11 : ➕ Analytique des opérations et de la chaîne logistique

> « Un client ne juge pas votre entrepôt : il juge le jour où le colis arrive. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 et 2 (distributions, intervalles de confiance, comparaison de proportions) à des questions d'**opérations** : livrer à l'heure, ne pas manquer de stock, choisir des fournisseurs fiables.

La gérante de la boutique vous écrit un mardi, d'un ton un peu las : « *Plusieurs clients se plaignent de livraisons tardives, et de mon côté je tombe en rupture sur des produits qui se vendent bien. Je ne sais pas si le problème vient des transporteurs, de mes fournisseurs ou de ma façon de commander. Peux-tu regarder ?* »

C'est une question d'analyste, et elle a une particularité : **trois problèmes se cachent derrière une seule plainte**. Un colis en retard peut venir de la préparation (la boutique), du transport (le transporteur) ou d'une période de forte demande (décembre). Une rupture peut venir d'un fournisseur lent, d'un point de commande trop bas ou d'une demande qui a monté. Ces causes se confondent dans une moyenne, et c'est précisément le travail de l'analyste de les **séparer**.

Le chapitre suit la chaîne dans l'ordre où le client la vit, mais en sens inverse de la cause : d'abord ce que le client a vu (la livraison, section 11.1), ensuite ce que la boutique contrôle le plus (ses stocks, section 11.2), enfin ce qu'elle contrôle le moins (ses fournisseurs, section 11.3). Trois idées l'organisent. La première est qu'**un délai se décrit par sa distribution, pas par sa moyenne** : le client qui attend huit jours ne se console pas parce que la moyenne est de six. La deuxième est qu'un stock est un **compromis chiffrable** entre le service rendu et l'argent immobilisé : on peut mettre un prix sur chaque point de rupture évité. La troisième est qu'une comparaison entre fournisseurs ou entre transporteurs n'a de sens qu'avec son **incertitude** : sur quelques dizaines de commandes, tout le monde a l'air bon ou mauvais selon la semaine.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de logistique : nous n'optimisons pas de tournées, ne dimensionnons pas d'entrepôt et ne modélisons pas de réseaux. Nous mesurons ce que les données de la boutique permettent de mesurer, avec des formules simples et une honnêteté sur leurs limites.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 11.1 | Les livraisons sont-elles tardives, et à cause de qui ? | Délais par étape, centiles plutôt que moyenne, comparaison de transporteurs avec intervalles, effet de décembre |
| 11.2 | Pourquoi des ruptures, et comment les réduire ? | Rotation et couverture, point de commande et stock de sécurité, quantité économique, compromis service/stock rejoué sur les données |
| 11.3 | Quels fournisseurs sont fiables ? | Délai promis contre réel, taux de service, carte de performance avec intervalles, impact sur les ruptures |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique est fictive. Nous connaissons donc la **vérité programmée** et nous la révélerons à la fin de chaque étude, pour que vous voyiez ce que l'analyse retrouve et ce qu'elle manque.

- `livraisons.csv` : une ligne par commande envoyée (canaux Site et Réseaux, 2023 à 2025), avec le transporteur, les dates d'expédition et de livraison, le délai promis au client (six jours), un indicateur de retard et un indicateur de colis abîmé (section 11.1).
- `stock_quotidien.csv` : le niveau de stock, la demande et l'éventuelle rupture de **vingt produits**, **chaque jour de 2025**, avec le point de commande en vigueur (section 11.2).
- `reappro_fournisseur.csv` : **1 500 commandes d'achat** de 2023 à 2025, avec le fournisseur, le délai promis et le délai réel, la quantité commandée et la quantité reçue (section 11.3).
- `produits.csv`, `commandes.csv`, `retours.csv` : le prix et le coût des produits, les commandes et les retours, pour relier un retard à un coût (sections 11.1 et 11.2).

Le fichier des livraisons contient aussi des commandes en « retrait en magasin » : le client vient chercher son colis, et un transporteur figure pourtant dans le fichier (un transfert entre entrepôt et magasin, ou une saisie par défaut). Un retrait n'est pas une livraison au sens du client : nous les écartons dès le départ, et c'est notre premier choix d'analyste à documenter.

```python hide
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2
import outils_ch11 as O
setup()

def NUM(k, v, nd=None):
    if nd is not None:
        v = f"{v:,.{nd}f}".replace(",", " ")
    elif isinstance(v, (int, np.integer)):
        v = f"{int(v):,}".replace(",", " ")
    print("NUM", k, v)

liv, rea, stk, prod = O.charger()
liv_brut = pd.read_csv("donnees/livraisons.csv")
NUM("n_liv_brut", len(liv_brut))
NUM("n_retrait", int((liv_brut["mode_livraison"] == "Retrait magasin").sum()))
NUM("n_liv", len(liv))
NUM("n_stock_lignes", len(stk))
NUM("n_produits_stock", stk["id_produit"].nunique())
NUM("n_achats", len(rea))
```
<!--sortie-->
```text
NUM n_liv_brut 19 420
NUM n_retrait 1 373
NUM n_liv 18 047
NUM n_stock_lignes 7 300
NUM n_produits_stock 20
NUM n_achats 1 500
```

Dans le fichier brut, 1 373 des 19 420 lignes sont des retraits en magasin ; il reste **18 047 livraisons** à analyser.
