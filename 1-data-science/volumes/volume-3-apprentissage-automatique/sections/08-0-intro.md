# Chapitre 8 : ➕ Apprentissage semi-supervisé et actif

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui se heurtent, en pratique, à un problème très courant : **on a beaucoup de données, mais très peu d'étiquettes**.

> « Les données coulent à flots ; les étiquettes, elles, se paient au compte-gouttes. »

Tout au long du volume, nous avons supposé que chaque ligne du tableau venait avec sa **réponse** : ce client a-t-il résilié ou non, cette image représente-t-elle un 3 ou un 8, cette commande est-elle une fraude. Dans la vie réelle, cette réponse a souvent un **prix** :

- pour savoir si un client a résilié, il faut **attendre** trois mois, ou l'appeler (quelques euros par appel) ;
- pour savoir si une image montre tel chiffre ou tel défaut sur un produit, il faut qu'un **humain** la regarde ;
- pour savoir si une commande est frauduleuse, il faut une **enquête**.

La boutique, elle, possède des dizaines de milliers de lignes de données *brutes* (clients, images, commandes) mais seulement quelques dizaines de lignes *étiquetées*. Deux familles de méthodes répondent à cette situation, avec deux questions différentes :

| | **Question posée** | **Le lecteur retiendra** |
|---|---|---|
| **Apprentissage semi-supervisé** | « Les données **non étiquetées** que j'ai déjà peuvent-elles m'aider à mieux apprendre avec peu d'étiquettes ? » | exploiter ce qu'on a **gratuitement** |
| **Apprentissage actif** | « Si je ne peux payer que $b$ étiquettes, **lesquelles** dois-je demander ? » | choisir ce qu'on **achète** |

> 💡 **Intuition.** Imaginez que vous apprenez à reconnaître des champignons. Un expert est disponible une heure. Vous pouvez (1) *regarder des milliers de photos sans légende* en vous disant « ces deux-là se ressemblent donc sont sans doute de la même espèce » : c'est le **semi-supervisé** ; ou (2) *choisir avec soin les dix champignons que vous montrerez à l'expert*, en lui apportant ceux qui vous font le plus hésiter : c'est l'**actif**. Les deux se combinent.

## Le chemin de ce chapitre

- **8.1 Pourquoi et hypothèses** : ce que les données non étiquetées *peuvent* apporter, les quatre hypothèses qui le permettent, les cas où elles **nuisent**, et le seul outil d'évaluation honnête de ce chapitre, la **courbe d'apprentissage selon le budget d'étiquettes**.
- **8.2 Auto-apprentissage et propagation d'étiquettes** : deux méthodes concrètes, l'une qui étiquette elle-même les cas faciles, l'autre qui fait « couler » les étiquettes le long d'un graphe de similarité.
- **8.3 Apprentissage actif** : la boucle « entraîner, choisir, demander, recommencer », les critères de choix (incertitude, marge, entropie, comité, densité), le **piège du biais d'échantillonnage**, le **démarrage à froid** et un petit calcul de coût.

> 📒 **Pour s'entraîner.** Le cahier de ce chapitre contient huit applications guidées (courbes d'apprentissage, auto-apprentissage, propagation, co-apprentissage, boucle active écrite à la main, comité, biais d'échantillonnage, calcul de coût) et douze exercices corrigés. Chaque section du livre indique celles qui la prolongent.

## Les données du chapitre

Deux jeux de données serviront d'un bout à l'autre, **sans aucun téléchargement** :

| Jeu | Nature | Taille | Rôle |
|---|---|---|---|
| **Chiffres manuscrits** (`load_digits` de scikit-learn) | **réel** : images 8 × 8 pixels de chiffres écrits à la main, 10 classes | 1 797 images ; nous en gardons 1 347 comme **réservoir** (*pool*) à étiqueter et 450 comme **jeu de test** | des classes bien groupées : le cas où les méthodes de ce chapitre brillent |
| **Clients de la boutique** (`donnees/clients_ml.csv`, volume III) | **simulé** : 12 000 clients, résiliation à 90 jours (14 %) | 9 000 en réservoir, 3 000 en test | des variables mélangées (nombres, catégories) et des classes qui se chevauchent : le cas où ces méthodes **déçoivent** |

Les étiquettes de ces deux jeux sont en réalité toutes connues : c'est ce qui permet de **simuler** un budget d'étiquettes limité (on « cache » presque toutes les étiquettes, puis on mesure ce que les méthodes savent en faire) et de vérifier, à la fin, si elles ont deviné juste. Les clients, eux, sont plus difficiles : des variables de natures différentes et des classes qui se chevauchent, comme dans la vraie vie.

> ⚠️ **Une convention à connaître.** Dans scikit-learn, une observation **sans étiquette** se marque par la valeur `-1` dans le vecteur des étiquettes. Les méthodes semi-supervisées reçoivent *tout* le tableau de variables $X$, et un vecteur $y$ où seules quelques entrées sont renseignées.

```python noexec
y_partiel = np.full(len(y), -1)              # -1 = « pas d'étiquette »
y_partiel[indices_etiquetes] = y[indices_etiquetes]
```

```python hide
import sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import outils_ch08 as o
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
from sklearn.linear_model import LogisticRegression
from sklearn.semi_supervised import LabelSpreading, SelfTrainingClassifier

style.setup()
Xp, Xt, yp, yt = o.charger_digits()                 # chiffres : réservoir et test
Xc, Xct, yc, yct = o.charger_churn()                # clients : réservoir et test
print("chiffres : réservoir", Xp.shape, "test", Xt.shape, "| clients : réservoir", Xc.shape, "test", Xct.shape,
      "| churn", round(yc.mean(), 3), round(yct.mean(), 3))
```
<!--sortie-->
```text
chiffres : réservoir (1347, 64) test (450, 64) | clients : réservoir (9000, 49) test (3000, 49) | churn 0.14 0.14
```
