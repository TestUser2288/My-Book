# Chapitre 2 : Apprentissage supervisé

> « Tous les modèles de ce chapitre font la même chose : ils apprennent une règle à partir d'exemples dont on connaît la réponse. Ils ne diffèrent que par la **forme** de la règle qu'ils savent écrire. »

Le chapitre 1 a installé la démarche : poser le problème, réserver des données pour juger, valider, se méfier du surapprentissage. Il est temps de rencontrer les **modèles** eux-mêmes. Nous allons les parcourir comme une échelle : chaque barreau corrige un défaut du précédent.

```python hide
import sys
import warnings

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import style
from style import AQUA, BLEU, ORANGE, ROUGE, VIOLET

style.setup()


def NUM(cle, valeur):
    """Imprime un nombre cité dans la prose : le gabarit du livre le relit dans cette sortie."""
    print("NUM", cle, valeur)


from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

clients = pd.read_csv("donnees/clients_ml.csv")
y = clients["churn_90j"]
X = clients.drop(columns=["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"])
cat = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
num = [c for c in X.columns if c not in cat]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)

# Trois « vues » des mêmes données : brutes, catégories pandas (boosting), indicatrices (arbres, forêts)
def en_categories(df, ref):
    out = df.copy()
    for c in cat:
        out[c] = pd.Categorical(df[c], categories=sorted(ref[c].dropna().unique()))
    return out

Xtr_c, Xte_c = en_categories(Xtr, Xtr), en_categories(Xte, Xtr)
Xtr_o = pd.get_dummies(Xtr, columns=cat, dtype=float)
Xte_o = pd.get_dummies(Xte, columns=cat, dtype=float).reindex(columns=Xtr_o.columns, fill_value=0.0)

NUM("n_total", len(clients))
NUM("n_train", len(Xtr))
NUM("n_test", len(Xte))
NUM("taux_churn", y.mean())
NUM("taux_churn_train", ytr.mean())
NUM("n_vars", X.shape[1])
NUM("n_vars_one_hot", Xtr_o.shape[1])
NUM("pct_manquant_sat", clients["satisfaction_moy"].isna().mean())
```
<!--sortie-->
```text
NUM n_total 12000
NUM n_train 9000
NUM n_test 3000
NUM taux_churn 0.14041666666666666
NUM taux_churn_train 0.14044444444444446
NUM n_vars 19
NUM n_vars_one_hot 45
NUM pct_manquant_sat 0.12775
```

## Le chemin de ce chapitre

- **2.1 Modèles linéaires et logistiques** : le modèle le plus simple, revu avec les yeux de l'apprentissage automatique : une **fonction de perte**, un algorithme (la descente de gradient) et une **pénalité**.
- **2.2 Arbres de décision** : des règles « si… alors… » apprises automatiquement ; ils capturent les **seuils** et les **interactions** qu'un modèle linéaire ignore, mais ils sont instables.
- **2.3 Forêts aléatoires** : on moyenne beaucoup d'arbres différents ; la variance s'effondre.
- **2.4 Gradient boosting** : on construit les arbres l'un après l'autre, chacun corrigeant les erreurs des précédents. C'est, aujourd'hui, la famille la plus performante sur les données tabulaires. XGBoost et LightGBM en sont les deux implémentations vedettes.
- ➕ **2.5 SVM, k plus proches voisins, Bayes naïf** : trois idées classiques, utiles à connaître.
- ➕ **2.6 CatBoost, stacking et blending** : aller plus loin, et combiner des modèles sans tricher.

> 💡 **L'idée directrice : un seul problème, plusieurs règles.** Dans tout le chapitre, nous posons **la même question** aux **mêmes données**, avec le **même découpage** et la **même mesure de réussite**. Seul le modèle change. Cela permet de comparer honnêtement, et de voir ce que chaque famille apporte (ou n'apporte pas).

## Le problème qui nous accompagne

La gérante veut savoir, parmi ses clients, **lesquels vont cesser de commander** dans les 90 jours qui viennent, afin de leur proposer une attention particulière (un message, une offre). C'est le problème de **résiliation** (*churn*) : prédire une variable à deux issues, `churn_90j` ∈ {0, 1}, à partir de ce que l'on sait du client aujourd'hui.

Les données (décrites dans l'introduction du volume) sont un tableau `clients_ml.csv` de 12 000 clients, avec 19 variables d'entrée : âge, ville (20 modalités), canal d'acquisition, ancienneté, nombre de commandes et montant des 12 derniers mois, récence (jours depuis la dernière commande), retours, satisfaction, tickets au support, programme de fidélité, promotions reçues, ouverture des courriels, délai de livraison… Certaines valeurs sont **manquantes** (13 % des satisfactions, par exemple). Environ 14 % des clients partent : le problème est **déséquilibré** sans l'être extrêmement (le chapitre 4 traitera les cas plus durs).

Conformément au chapitre 1, nous avons mis de côté un **jeu de test** (3 000 clients, un quart des données, tiré au hasard en conservant la proportion de départs) que nous n'utiliserons qu'à la fin, pour juger. Le **jeu d'entraînement** compte 9 000 clients ; quand il faut choisir un réglage, nous le faisons par validation croisée **à l'intérieur** de ce jeu (volume III, section 1.2).

> ⚠️ **Une colonne à ne pas toucher.** Le fichier contient aussi `commandes_apres_cible`, le nombre de commandes des trois mois **suivants**. Elle contient la réponse en filigrane : un modèle qui l'utilise paraît parfait et ne servira à rien le jour où l'on prédit réellement l'avenir. C'est la **fuite d'information** (volume III, section 1.1). Nous l'excluons, avec les autres cibles, de toutes les variables d'entrée.

## Ce qu'« apprendre » veut dire

Un modèle supervisé est, au fond, **une fonction** $f$ qui associe à un client $x$ (le vecteur de ses caractéristiques) une prédiction $f(x)$. Pour choisir $f$, on dispose de $n$ exemples $(x_i,y_i)$ et de trois ingrédients :

1. une **famille de fonctions** $\mathcal F$ (les droites, les arbres, les sommes d'arbres…) : c'est ce que le modèle *sait écrire* ;
2. une **perte** $\ell\bigl(y,f(x)\bigr)$, qui mesure le coût d'une erreur ;
3. un **algorithme** qui cherche, dans $\mathcal F$, la fonction de perte moyenne minimale sur les exemples (la minimisation du **risque empirique**) : $\hat f=\arg\min_{f\in\mathcal F}\frac1n\sum_i\ell\bigl(y_i,f(x_i)\bigr)$, souvent additionnée d'une pénalité qui limite la complexité.

Les sections suivantes varient ces trois ingrédients. Retenons dès maintenant la leçon du chapitre 1 : plus la famille $\mathcal F$ est riche, mieux elle ajuste les données d'entraînement, et plus elle risque d'apprendre le bruit. **Le bon modèle n'est pas le plus riche : c'est celui dont la richesse est adaptée à la quantité de données et à la structure du phénomène.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : les applications 2.1 à 2.10 et les exercices 2.1 à 2.12 accompagnent les sections de ce chapitre ; chaque section renvoie aux siens.
