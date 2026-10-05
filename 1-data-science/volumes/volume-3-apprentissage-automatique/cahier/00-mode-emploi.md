# Mode d'emploi

> « On comprend en lisant, on retient en pratiquant. »

Ce cahier est le **compagnon du livre** du volume III (*Apprentissage automatique*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées** sur données, des **exercices** et leurs **corrigés**, puis le **projet du volume** (un pipeline complet sur un jeu réel) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.
2. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre : on peut ainsi chercher sans voir la réponse.
3. **Tapez le code vous-même** plutôt que de le copier : modifiez-le, cassez-le, lisez les messages d'erreur. En apprentissage automatique, on apprend surtout en changeant un réglage et en regardant ce que devient le score.
4. **Faites les applications dans l'ordre** : chacune raconte une petite étude, avec une question, des étapes, du code et une lecture des résultats.
5. **Gardez le jeu de test pour la fin.** C'est la règle de tout le volume : dans les applications, quand on vous demande de régler quelque chose, on le fait avec la validation croisée sur le jeu d'entraînement, jamais en regardant le jeu de test.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 2.1 : première application du chapitre 2 |
| Exercice | `Exercice N.k` | Exercice 2.3 : troisième exercice du chapitre 2 |
| Corrigé | `Corrigé N.k` | Corrigé 2.3 : correction de l'exercice 2.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une formule ou d'une idée vue dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, une démonstration ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/`. Toutes celles de la boutique sont **simulées** avec des graines fixes ; vos résultats seront identiques à ceux du livre.

| Fichier | Contenu |
|---|---|
| `clients_ml.csv` | 12 000 clients : 19 variables d'entrée et 3 cibles (`churn_90j`, `depense_6m`, `segment_vrai`) |
| `transactions.csv` | 60 000 commandes en ligne, dont 0,81 % de fraudes |
| `interactions.csv`, `produits_ml.csv` | achats « client × produit » et description des 150 produits |
| `credit_defaut.csv` | **jeu réel** : 30 000 clients d'une banque (UCI, licence CC0) ; cible `default` |

Certains chapitres ajoutent leurs propres jeux (`ch0N-*.csv`) : ils sont fournis, et le script qui les produit se trouve dans `build/`. Chaque chapitre du cahier est **autonome** : il commence par recharger ses données et refaire ses imports.

### Dictionnaire des données de `clients_ml.csv`

Le statut d'une colonne décide de ce qu'on a le droit d'en faire. Le voici pour les 24 colonnes du fichier :

| Colonne | Statut | Remarque |
|---|---|---|
| `id_client` | identifiant | à ne jamais utiliser comme variable d'entrée |
| `age`, `ville`, `canal_acquisition`, `appareil`, `anciennete_mois`, `nb_commandes_12m`, `panier_moyen`, `montant_12m`, `recence_jours`, `nb_retours_12m`, `satisfaction_moy`, `nb_tickets_support_12m`, `programme_fidelite`, `nb_promos_recues_12m`, `part_achats_promo`, `taux_ouverture_email`, `delai_livraison_moy`, `categorie_preferee`, `revenu_zone` | **entrée** (19 variables) | observées au 31/12/2025 ; certaines ont des valeurs manquantes |
| `churn_90j` | **cible** (classification) | 1 si le client ne commande plus dans les 90 jours suivants |
| `depense_6m` | **cible** (régression) | dépense, en €, sur les 6 mois suivants |
| `segment_vrai` | vérité de simulation | classe latente ayant servi à générer les données ; sert uniquement à **valider** les méthodes non supervisées (chapitre 3) ; n'existe pas dans la vie réelle |
| `commandes_apres_cible` | **⚠️ à ne pas utiliser en entrée** | nombre de commandes dans les 3 mois **suivant** la date d'observation : une information qu'on n'a pas encore au moment de prédire. Elle sert à étudier la **fuite d'information** (chapitre 1) |

Le dictionnaire de `transactions.csv`, de `interactions.csv` et de `credit_defaut.csv` figure dans la section « Les données et l'environnement du volume » du livre ; celui de `credit_defaut.csv` est repris dans le projet.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/clients_ml.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, ou dans un terminal interactif.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Le temps de calcul.** Les modèles de ce volume sont plus lents que ceux du volume II (forêts, boosting, validations croisées). Les applications sont dimensionnées pour tourner en quelques dizaines de secondes sur un ordinateur ordinaire ; si l'une d'elles est trop lente chez vous, réduisez `n_estimators` ou travaillez sur un sous-échantillon des clients.

## Vérifier son installation

Avant de commencer, ce court bloc vérifie que les données sont trouvées, que les bibliothèques sont installées et qu'un modèle à graine fixe donne le résultat attendu.

```python
from importlib import import_module
from importlib.metadata import version
paquets = [("numpy", "numpy"), ("pandas", "pandas"), ("scipy", "scipy"), ("scikit-learn", "sklearn"), ("xgboost", "xgboost"),
           ("lightgbm", "lightgbm"), ("catboost", "catboost"), ("shap", "shap"), ("lime", "lime"), ("optuna", "optuna"),
           ("imbalanced-learn", "imblearn"), ("umap-learn", "umap")]
for paquet, module in paquets:
    import_module(module)                       # échoue si la bibliothèque n'est pas installée
    print(f"{paquet:17s}", version(paquet))
import pandas as pd
print(pd.read_csv("donnees/clients_ml.csv").shape)
```
<!--sortie-->
```text
numpy             2.5.3
pandas            3.0.6
scipy             1.18.1
scikit-learn      1.9.1
xgboost           3.4.1
lightgbm          4.7.0
catboost          1.2.10
shap              0.52.0
lime              0.2.0.1
optuna            5.0.0
imbalanced-learn  0.14.2
umap-learn        0.5.12
(12000, 24)
```

Vous devez lire une version pour chaque bibliothèque (le livre utilise celles de la section « L'environnement de travail »), puis `(12000, 24)`. Si une bibliothèque manque, installez-la avec `pip` (voir le livre).

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
X, y = load_breast_cancer(return_X_y=True)
print(round(LogisticRegression(max_iter=5000).fit(X, y).score(X, y), 4))
```
<!--sortie-->
```text
0.9578
```

Cette seconde vérification doit afficher une exactitude de 0,9578 (à la dernière décimale près selon la version de la bibliothèque) : c'est le signe que le calcul numérique se comporte comme prévu.

## Plan du cahier

| Chapitre | Contenu |
|---|---|
| 1. La démarche | séparation des données, validation croisée, biais-variance, modèles de référence, fuite d'information ; ➕ réglage des hyperparamètres |
| 2. Apprentissage supervisé | modèles linéaires et logistiques, arbres, forêts, gradient boosting ; ➕ SVM, k plus proches voisins, Bayes naïf, stacking |
| 3. Sans étiquettes | validation d'un regroupement, réduction de dimension ; ➕ DBSCAN, mélanges gaussiens, t-SNE et UMAP |
| 4. Variables et déséquilibre | encodage, transformations, création de variables, classes rares ; ➕ sélection de variables, SMOTE |
| 5. Évaluation et interprétabilité | métriques, calibration, SHAP et LIME ; ➕ équité, prédiction conforme |
| 6 à 9 (facultatifs) | anomalies et fraude, recommandation, semi-supervisé et actif, renforcement |
| Projet et auto-évaluation | un pipeline complet sur le jeu réel de défaut de crédit, puis des questions pour vérifier ses acquis |
