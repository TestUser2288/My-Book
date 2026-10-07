# Chapitre 3 : Régression pour les questions métier

> « Toutes choses égales par ailleurs : la plus belle expression de la statistique, et la plus facile à mal employer. »

Un mardi matin de décembre, la gérante pose une feuille sur votre bureau : le planning des soldes de janvier. Elle hésite entre trois semaines de promotion et deux.

— Quand on lance une promotion, on vend plus de commandes, ça se voit. Mais en janvier on vend toujours peu, et en décembre toujours beaucoup. **Combien de commandes la promotion nous fait-elle gagner par jour, vraiment ?** Et la publicité : je dépense plus de 1 000 € par semaine, est-ce que ça rapporte ?

Vous connaissez déjà la moitié de la réponse. Au volume I (section 1.4), vous avez appris à mesurer une **corrélation** et à vous méfier : la publicité et les ventes montent ensemble parce que **la saison** les fait monter ensemble. Mais « se méfier » ne répond pas à la question de la gérante. Il faut un outil qui **sépare les effets** : la part due à la promotion, la part due au jour de la semaine, la part due à la saison, la part due à la publicité. Cet outil, c'est la **régression**.

La régression est probablement la méthode statistique la plus utilisée en entreprise, pour deux raisons très différentes. On peut s'en servir pour **expliquer** (« la promotion augmente les commandes de 19 % ») ou pour **estimer** et prédire (« combien de commandes demain ? »). Ces deux usages ne demandent pas les mêmes précautions, et ce chapitre vous apprend à ne pas les confondre.

## Le chemin de ce chapitre

Le **parcours essentiel** compte deux sections :

- **3.1 Régression linéaire pour expliquer et estimer** : *comment une droite, puis un plan, puis un modèle à plusieurs variables résume-t-il une relation ?* Les moindres carrés à la main, la lecture d'un tableau de résultats, les variables qualitatives (jours, mois, canaux), les logarithmes, les interactions, les vérifications (résidus, colinéarité, valeurs influentes), et la différence entre expliquer et prédire.
- **3.2 Interpréter les coefficients pour des non-spécialistes** : *comment dire ce que le modèle dit, sans trahir ce qu'il dit ?* Les phrases types, les effets en pourcentage, les graphiques d'effets, ce que l'on peut comparer et ce que l'on ne doit pas comparer, et les erreurs de formulation qui font le plus de dégâts.

Une section facultative (➕) complète le tout : **3.3 Régression logistique pour les résultats métier**, quand la grandeur à expliquer n'est plus un nombre mais un oui ou un non (une ligne est-elle retournée ?), avec les cotes, les rapports de cotes et le choix d'un seuil de décision.

> 🧭 **Comment lire ce chapitre.** Le fil conducteur est la question de la gérante. À chaque étape, nous comparons ce que le modèle trouve à ce que nous savons, puisque les données de la boutique sont **simulées** : nous connaissons l'effet **programmé** de la promotion, de la publicité, de la pluie, des jours de la semaine. Cette « vérité » est le moyen de voir quand une régression tient sa promesse, et quand elle ne peut pas la tenir (par exemple quand l'effet est trop petit pour être mesuré).

## Les données du chapitre

> 📦 **Les données.** Deux jeux de la boutique, que vous connaissez depuis le volume I.
>
> - `jours_exploitation.csv` : une ligne par jour entre janvier 2023 et décembre 2025 (1 096 jours, dont 1 090 utilisables ici : la dépense des sept derniers jours n'existe pas pour les six premiers), avec le nombre de commandes et le chiffre d'affaires du jour, la température, la pluie, un indicateur de **promotion** (soldes d'hiver et d'été, semaine du « Vendredi noir ») et la **dépense publicitaire** du jour. Nous y ajouterons la dépense des **sept derniers jours**, plus parlante que celle d'un seul jour.
> - `lignes_commande.csv`, `commandes.csv`, `retours.csv` et `produits.csv` : les 83 905 lignes de commande, leur canal, leur catégorie et le fait d'avoir été retournées ou non (section 3.3).
>
> Les données sont déjà propres (le nettoyage est l'objet du volume II). Elles sont **simulées** par `build/donnees_a1.py`.

```python
import pandas as pd
import statsmodels.formula.api as smf
import outils_ch03 as O

jr = O.charger_jours()                  # un jour par ligne, avec la dépense des sept derniers jours en k€
print(len(jr), "jours ;", jr["date"].min().date(), "->", jr["date"].max().date())
print("commandes par jour : moyenne", round(jr["nb_commandes"].mean(), 1), "| jours de promotion :", int(jr["promo_active"].sum()))
```

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2
setup()
def NUM(cle, valeur):
    print("NUM", cle, valeur)
NUM("n_jours", len(jr)); NUM("n_jours_modele", len(jr))
NUM("moy_commandes", round(jr["nb_commandes"].mean(), 1)); NUM("n_promo", int(jr["promo_active"].sum()))
NUM("pub_hebdo_moy", round(jr["pub_hebdo"].mean(), 2))
```
