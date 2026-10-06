# Chapitre 1 : Deep learning

> « Un réseau de neurones n'est pas un cerveau. C'est une longue composition de fonctions très simples, dont on ajuste les paramètres par descente de gradient. Tout le reste est de l'ingénierie. »

Les volumes précédents ont construit des modèles à partir de **variables que nous avions choisies** : le nombre de commandes, la récence, le panier moyen. Le travail de l'analyste consistait à fabriquer les bonnes colonnes, puis à laisser un modèle (une régression, une forêt, un boosting) les combiner. Face à une image, un son ou une phrase, cette méthode se heurte à un mur : il n'y a pas de colonne « récence » dans une photographie. Il y a des **centaines de milliers de pixels**, et personne ne sait écrire à la main la formule qui transforme ces pixels en « ceci est un 7 ».

L'**apprentissage profond** (*deep learning*) répond à ce mur par une idée simple : **apprendre aussi les variables**. Un réseau empile des couches ; chacune transforme la sortie de la précédente ; les premières couches apprennent des motifs élémentaires (des contours), les suivantes les assemblent (des boucles, des angles), les dernières décident (« c'est un 7 »). Tout est appris **de bout en bout**, avec la même méthode d'optimisation que celle de la régression logistique : la descente de gradient (volume I, section 1.3.3).

## Le chemin de ce chapitre

- **1.1 Réseaux de neurones et rétropropagation** : le neurone, les couches, les fonctions d'activation, et surtout la **rétropropagation**, que nous calculerons **entièrement à la main** sur un petit réseau avant de la laisser à la machine. Optimiseurs, gradients qui disparaissent, régularisation.
- **1.2 Réseaux convolutifs** : comment exploiter la structure d'une image (voisinage, répétition) avec très peu de paramètres.
- **1.3 Réseaux récurrents et LSTM** : comment lire une suite (les ventes quotidiennes de la boutique) en gardant une mémoire.
- ➕ **1.4 Frameworks** : PyTorch en pratique, face à TensorFlow/Keras.
- ➕ **1.5 Apprentissage par transfert, vision par ordinateur, OCR de documents** : réutiliser un réseau déjà entraîné ; lire des factures.
- ➕ **1.6 Deep learning pour données tabulaires et séries temporelles** : quand il vaut mieux **ne pas** l'utiliser.

> 🧭 **Un fil rouge d'honnêteté.** Le deep learning est spectaculaire sur les images, le son et le texte, mais il n'est ni gratuit ni magique. Chaque comparaison de ce chapitre se fait **contre une référence** (régression logistique, boosting, méthode naïve) et avec les règles du volume III : jeu de test intact, plusieurs graines, incertitude. Vous verrez des cas où le réseau gagne nettement, des cas où il égale à peine une méthode simple, et des cas où il perd.

## Les données de ce chapitre

| Jeu | Contenu | Utilisé en |
|---|---|---|
| **MNIST** (réel) | images de chiffres manuscrits de 28 × 28 pixels ; nous en gardons {{n_train|int}} pour l'entraînement et {{n_test|int}} pour le test | 1.1, 1.2, 1.5 |
| `ventes_quotidiennes.csv` (simulé) | trois ans de ventes quotidiennes de la boutique | 1.3 |
| `clients_ml.csv` (simulé) | les clients du volume III, cible de résiliation | 1.6 |
| factures (générées) | images de factures fabriquées avec une bibliothèque de dessin | 1.5 |

MNIST est un jeu **réel** : une base publique de chiffres manuscrits (LeCun, Cortes et Burges), obtenue via OpenML, libre pour la recherche et l'enseignement. Les chiffres ont été écrits à la main par des centaines de personnes. Les autres jeux sont simulés avec des graines fixes, ce qui nous permet de connaître la vérité.

```python hide
import sys, warnings, time
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, torch, torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "build")
import style
from style import AQUA, BLEU, ENCRE2, MUET, ORANGE, ROUGE, VIOLET
from outils_ch01 import *
style.setup()


def NUM(cle, valeur):
    """Imprime un nombre cité dans la prose : le gabarit du livre le relit dans cette sortie."""
    print("NUM", cle, valeur)


graine(0)
xi, yi, xte, yte = charger_mnist()                       # images (N, 1, 28, 28)
xt, yt, xv, yv = xi[:8000], yi[:8000], xi[8000:], yi[8000:]
NUM("n_train", len(xt) + len(xv)); NUM("n_test", len(xte))
fig, axs = plt.subplots(2, 8, figsize=(9.6, 2.9))
for k, ax in enumerate(axs.ravel()):
    ax.imshow(xt[k, 0], cmap="gray_r"); ax.set_title(str(int(yt[k])), fontsize=10, color=ENCRE2); ax.axis("off")
style.save(fig, "ch01-chiffres.png")
```

![Seize images de MNIST avec leur étiquette. Chaque image est un tableau de 28 × 28 niveaux de gris.](figures/ch01-chiffres.png)

Une image de MNIST n'est que cela : un tableau de $28\times28=784$ nombres entre 0 et 255. Pour un modèle des volumes précédents, ce sont 784 colonnes sans signification individuelle (le pixel (14, 9) ne veut rien dire en soi). La difficulté de la vision par ordinateur est là tout entière.
