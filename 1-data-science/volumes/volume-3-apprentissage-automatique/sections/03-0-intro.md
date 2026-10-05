# Chapitre 3 : Apprentissage non supervisé et réduction de dimension

> « Un algorithme de classification rend toujours des groupes. La vraie question n'est pas *combien*, c'est *est-ce que ça existe* ? »

Jusqu'ici, dans ce volume, chaque observation portait une **étiquette** : le client est parti ou non, la commande est frauduleuse ou non. On pouvait donc **vérifier** un modèle en comparant ses réponses à la bonne réponse. Ce chapitre quitte ce confort. On dispose seulement de **variables** décrivant les clients, et on demande à la machine de **découvrir de la structure** : des groupes qui se ressemblent, des directions qui résument les données, des représentations plus courtes.

La difficulté change de nature. Quand il n'y a pas de bonne réponse à vérifier, comment savoir qu'un résultat est **bon** ? C'est la question qui traverse tout le chapitre, et la réponse tient en une idée : on ne vérifie pas un résultat non supervisé contre la vérité, on le **soumet à plusieurs épreuves** (cohérence interne, comparaison avec un hasard sans structure, stabilité quand on perturbe les données, utilité pour une décision) et on regarde si elles se rejoignent.

> 🧭 **Ce que le volume II a déjà couvert.** L'analyse en composantes principales (volume II, section 3.1), l'analyse factorielle (section 3.2), les k-means et la classification hiérarchique (section 3.3) y sont présentées avec leurs bases : distance, algorithme de Lloyd, choix du nombre de groupes par le coude et la silhouette, avertissement « une méthode rend toujours des groupes ». Nous **ne les refaisons pas** : nous allons plus loin, vers la **validation** rigoureuse des groupes, vers des méthodes de réduction qui ne sont pas linéaires, et vers des méthodes de classification qui ne cherchent pas des boules.

## Le chemin de ce chapitre

- **3.1 Classification non supervisée et validation** : critères internes (inertie, silhouette, Calinski–Harabasz, Davies–Bouldin, statistique de l'écart), stabilité par rééchantillonnage, validation externe contre une vérité cachée, rôle de l'échelle et du choix des variables, lecture des groupes pour une décision.
- **3.2 Réduction de dimension** : pourquoi réduire (la malédiction de la dimension), rappel de l'ACP et reconstruction, ACP à noyau, SVD tronquée, factorisation non négative, projections aléatoires et le lemme de Johnson–Lindenstrauss, combien de dimensions garder.
- ➕ **3.3 DBSCAN, classification hiérarchique, mélanges gaussiens** : des groupes qui ne sont pas des boules, des groupes « flous », l'algorithme EM.
- ➕ **3.4 t-SNE et UMAP** : dessiner des données en haute dimension, et ce que ces dessins n'ont pas le droit de dire.

> 📒 **Pour s'entraîner.** Le cahier de ce chapitre propose huit applications guidées (segmentation de bout en bout, statistique de l'écart, réduction des chiffres manuscrits, EM écrit à la main, t-SNE et UMAP…) et douze exercices corrigés.

## Les données de ce chapitre

Deux jeux de données, de natures opposées, servent de fil conducteur.

- **Les clients de la boutique** (`donnees/clients_ml.csv`, 12 000 clients, **simulés**). Nous retenons sept variables de comportement : `age`, `nb_commandes_12m`, `montant_12m` (en logarithme, car très asymétrique), `recence_jours`, `part_achats_promo`, `taux_ouverture_email` et `nb_promos_recues_12m`. Le fichier contient aussi une variable `segment_vrai` : la **classe latente** qui a servi à fabriquer les comportements (quatre types : occasionnels, fidèles, chasseurs de promotions, grands paniers). Nous la gardons **de côté**, comme un examinateur garde le corrigé : elle servira à juger les méthodes en 3.1.6, mais aucune méthode ne la voit. Dans la vie réelle, cette vérité n'existe pas ; ici, elle nous permet de mesurer ce que valent nos critères.
- **Les chiffres manuscrits** (`load_digits` de scikit-learn, **réel**, intégré à la bibliothèque : 1 797 images de 8 × 8 pixels, donc 64 variables, représentant les chiffres de 0 à 9 écrits à la main). C'est un jeu classique pour les méthodes de réduction, parce qu'on peut **voir** les observations et savoir à quel chiffre elles correspondent.

```python hide
import sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from style import setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
setup()
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_digits

c = pd.read_csv("donnees/clients_ml.csv")
cols = ["age", "nb_commandes_12m", "montant_12m", "recence_jours", "part_achats_promo", "taux_ouverture_email", "nb_promos_recues_12m"]
X = c[cols].copy()
X["montant_12m"] = np.log1p(X["montant_12m"])          # montant très asymétrique : on travaille en logarithme
Z = StandardScaler().fit_transform(X)                  # variables centrées et réduites
chiffres = load_digits()
print("clients :", c.shape, "| variables retenues :", len(cols), "| chiffres :", chiffres.data.shape)
print("segment_vrai (parts) :", (c["segment_vrai"].value_counts(normalize=True).sort_index().round(3)).to_dict())
```
<!--sortie-->
```text
clients : (12000, 24) | variables retenues : 7 | chiffres : (1797, 64)
segment_vrai (parts) : {0: 0.384, 1: 0.296, 2: 0.196, 3: 0.124}
```
