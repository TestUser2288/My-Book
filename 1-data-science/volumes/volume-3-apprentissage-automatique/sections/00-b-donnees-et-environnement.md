# Les données et l'environnement du volume

## Les jeux de la boutique

Au volume II, nous avons suivi la boutique pendant dix ans, avec quelques milliers de clients. Pour apprendre à **prédire**, il faut davantage de données : dans ce volume, nous observons la boutique au **31 décembre 2025** à travers douze mille clients, soixante mille commandes en ligne et une matrice d'achats clients × produits. Tous ces jeux sont **simulés** (graines fixes, script `build/donnees3.py`) : vous obtiendrez exactement les mêmes chiffres que dans le livre. Un cinquième jeu est, lui, **réel**.

| Fichier | Contenu | Lignes | Utilisé surtout dans |
|---|---|---|---|
| `clients_ml.csv` | un client par ligne : comportement d'achat, satisfaction, support, trois cibles à prédire | 12 000 | chapitres 1 à 4, 5, 8 |
| `transactions.csv` | une commande en ligne par ligne, dont une très petite part de fraudes | 60 000 | chapitres 4 et 6 |
| `interactions.csv` | les achats « client × produit » (format long) | 27 687 | chapitre 7 |
| `produits_ml.csv` | catégorie, prix et nouveauté des 150 produits | 150 | chapitre 7 |
| `credit_defaut.csv` | **jeu réel** : clients d'une banque et défaut de paiement | 30 000 | chapitre 5 et projet du cahier |

Chargeons le premier, avec les trois gestes habituels (forme, types, valeurs manquantes) :

```python
import pandas as pd
clients = pd.read_csv("donnees/clients_ml.csv")
print(clients.shape)
```
<!--sortie-->
```text
(12000, 24)
```

```python hide
import numpy as np
transactions = pd.read_csv("donnees/transactions.csv")
interactions = pd.read_csv("donnees/interactions.csv")
produits = pd.read_csv("donnees/produits_ml.csv")
credit = pd.read_csv("donnees/credit_defaut.csv")
for nom, tab in [("clients_ml", clients), ("transactions", transactions), ("interactions", interactions),
                 ("produits_ml", produits), ("credit_defaut", credit)]:
    print(f"{nom:14s} {tab.shape[0]:6d} lignes, {tab.shape[1]:2d} colonnes, {int(tab.isna().sum().sum()):6d} valeur(s) manquante(s)")
```
<!--sortie-->
```text
clients_ml      12000 lignes, 24 colonnes,   6426 valeur(s) manquante(s)
transactions    60000 lignes, 15 colonnes,      0 valeur(s) manquante(s)
interactions    27687 lignes,  4 colonnes,  20804 valeur(s) manquante(s)
produits_ml       150 lignes,  4 colonnes,      0 valeur(s) manquante(s)
credit_defaut   30000 lignes, 24 colonnes,      0 valeur(s) manquante(s)
```

Les valeurs manquantes de `clients_ml.csv` et de `interactions.csv` ne sont pas des accidents : elles sont **voulues**, car la vraie vie en est pleine, et le chapitre 4 apprend à les traiter.

## Les clients : `clients_ml.csv`

Le fichier contient un identifiant, **19 variables d'entrée**, **trois cibles** (ce qu'on voudra prédire) et une colonne de plus dont nous parlerons à la fin de cette section.

| Variable | Type | Signification |
|---|---|---|
| `age` | quantitative | âge du client (18 à 78 ans) |
| `ville` | qualitative, **20 modalités** | « Ville A » à « Ville T » |
| `canal_acquisition` | qualitative | `Boutique` (magasin), `Site` (site web) ou `Réseaux` (réseaux sociaux) |
| `appareil` | qualitative, manquante | mobile, ordinateur ou tablette |
| `anciennete_mois` | quantitative | ancienneté du client, en mois |
| `nb_commandes_12m` | comptage | commandes sur les douze derniers mois |
| `panier_moyen` | quantitative, manquante | montant moyen d'une commande, en € (manquant si aucune commande) |
| `montant_12m` | quantitative ≥ 0 | dépense totale sur douze mois, en € |
| `recence_jours` | quantitative | jours écoulés depuis la dernière commande (365 si aucune) |
| `nb_retours_12m` | comptage | articles retournés sur douze mois |
| `satisfaction_moy` | quantitative (1 à 5), manquante | note de satisfaction moyenne |
| `nb_tickets_support_12m` | comptage | demandes au service client |
| `programme_fidelite` | binaire | 1 si le client est inscrit au programme de fidélité |
| `nb_promos_recues_12m` | comptage | promotions reçues |
| `part_achats_promo` | proportion | part des achats faits en promotion |
| `taux_ouverture_email` | proportion | part des courriels de la boutique ouverts |
| `delai_livraison_moy` | quantitative, manquante | délai moyen de livraison, en jours |
| `categorie_preferee` | qualitative | catégorie de produits la plus achetée (A à D) |
| `revenu_zone` | quantitative | indice de revenu de la zone de résidence |

| Cible | Type | Signification |
|---|---|---|
| `churn_90j` | binaire | 1 si le client **n'a plus commandé dans les 90 jours suivants** (« départ ») |
| `depense_6m` | quantitative ≥ 0 | dépense, en €, sur les six mois suivants (souvent nulle) |
| `segment_vrai` | qualitative (0 à 3) | classe latente qui a servi à **fabriquer** les comportements : elle n'existe que parce que les données sont simulées ; nous ne l'utilisons que pour **vérifier** les méthodes non supervisées (chapitre 3) |

```python hide
print("clients :", len(clients))
manq = clients.isna().sum()
print("valeurs manquantes par colonne :")
print(manq[manq > 0].to_string())
print("taux de manquants (%) :", (100 * manq[manq > 0] / len(clients)).round(1).to_dict())
print()
print("churn_90j : part de 1 =", round(clients["churn_90j"].mean(), 3), "(", int(clients["churn_90j"].sum()), "clients )")
print("depense_6m : part de zéros =", round((clients["depense_6m"] == 0).mean(), 3), "; moyenne =", round(clients["depense_6m"].mean(), 1),
      "; médiane =", clients["depense_6m"].median(), "; maximum =", clients["depense_6m"].max())
print("segment_vrai :", clients["segment_vrai"].value_counts(normalize=True).sort_index().round(3).to_dict())
print("canal :", clients["canal_acquisition"].value_counts().to_dict())
print("nb de villes :", clients["ville"].nunique())
print("age min/max :", clients["age"].min(), clients["age"].max())
print("colonnes :", list(clients.columns[:2]), "...", len(clients.columns))
```
<!--sortie-->
```text
clients : 12000
valeurs manquantes par colonne :
appareil               1829
panier_moyen           1630
satisfaction_moy       1533
delai_livraison_moy    1434
taux de manquants (%) : {'appareil': 15.2, 'panier_moyen': 13.6, 'satisfaction_moy': 12.8, 'delai_livraison_moy': 12.0}

churn_90j : part de 1 = 0.14 ( 1685 clients )
depense_6m : part de zéros = 0.352 ; moyenne = 84.3 ; médiane = 42.135 ; maximum = 1473.57
segment_vrai : {0: 0.384, 1: 0.296, 2: 0.196, 3: 0.124}
canal : {'Site': 4614, 'Réseaux': 3850, 'Boutique': 3536}
nb de villes : 20
age min/max : 18 78
colonnes : ['id_client', 'age'] ... 24
```

Quelques constats guideront nos choix de méthodes :

- **Le départ est un événement minoritaire** : environ 14 % des clients (1 685 sur 12 000). Une prédiction qui répondrait toujours « il reste » aurait raison 86 fois sur 100 sans rien comprendre : c'est le problème des classes déséquilibrées (chapitres 4 et 5).
- **La dépense à six mois est asymétrique et pleine de zéros** (un peu plus d'un tiers des clients n'achètent rien) : sa moyenne (84,3 €) est le double de sa médiane (42,1 €).
- **Quatre variables ont des valeurs manquantes**, de 12,0 % (`delai_livraison_moy`) à 15,2 % (`appareil`). Le panier moyen manque pour les 13,6 % de clients qui n'ont passé aucune commande ; la satisfaction (12,8 % de manquants) manque plus souvent chez les clients peu satisfaits : une absence qui est elle-même une information, comme nous le verrons au chapitre 4.
- **La variable `ville` a vingt modalités** : un cas d'école pour l'encodage de variables qualitatives à nombreuses catégories (chapitre 4).

> ⚠️ **Une colonne ne doit pas servir de variable d'entrée.** Le fichier contient une vingt-quatrième colonne, qui n'est ni un identifiant, ni une entrée, ni l'une des trois cibles. Le **dictionnaire des données** du cahier (« Mode d'emploi ») précise le statut de chaque colonne, y compris celle-ci. Comprendre pourquoi on ne peut pas l'utiliser pour prédire est l'une des leçons du chapitre 1. Elle n'a rien d'une rareté : c'est l'une des erreurs les plus fréquentes, et les plus coûteuses, des projets réels.

## Les commandes en ligne : `transactions.csv`

Chaque ligne est une commande passée en ligne ; la colonne `fraude` indique si elle était frauduleuse.

| Variable | Signification |
|---|---|
| `montant` | montant de la commande, en € |
| `heure`, `jour_semaine` | heure (0 à 23) et jour (0 à 6) de la commande |
| `canal` | `Site` ou `Réseaux` |
| `appareil_connu` | 1 si le client a déjà utilisé cet appareil |
| `distance_facturation_livraison_km` | écart entre l'adresse de facturation et celle de livraison |
| `nb_commandes_24h` | commandes du même compte dans les 24 dernières heures |
| `age_compte_jours` | ancienneté du compte, en jours |
| `ip_pays_different` | 1 si l'adresse IP ne correspond pas au pays du client |
| `mode_paiement` | carte, virement ou portefeuille |
| `delai_depuis_derniere_cmd_h` | heures écoulées depuis la commande précédente du compte |
| `nb_articles` | nombre d'articles |
| `fraude` | **cible** : 1 si la commande est frauduleuse |
| `type_fraude` | 0 (aucune), 1 ou 2 : **deux façons différentes** de frauder (utile pour comprendre les détecteurs d'anomalies, chapitre 6) |

```python hide
fr = transactions["fraude"]
print("commandes :", len(transactions), "; fraudes :", int(fr.sum()), "; taux :", round(100 * fr.mean(), 2), "%")
print("types de fraude :", transactions["type_fraude"].value_counts().sort_index().to_dict())
print("une règle « jamais de fraude » a raison dans", round(100 * (1 - fr.mean()), 1), "% des cas")
print("montant médian : légitimes", transactions.loc[fr == 0, "montant"].median(), "; fraudes", transactions.loc[fr == 1, "montant"].median())
```
<!--sortie-->
```text
commandes : 60000 ; fraudes : 486 ; taux : 0.81 %
types de fraude : {0: 59514, 1: 287, 2: 199}
une règle « jamais de fraude » a raison dans 99.2 % des cas
montant médian : légitimes 44.785 ; fraudes 76.09
```

Sur 60 000 commandes, 486 sont frauduleuses (0,81 %), réparties en 287 fraudes de type 1 et 199 de type 2. Ici, la règle « aucune commande n'est frauduleuse » a raison dans 99,2 % des cas : l'**exactitude** (la proportion de bonnes réponses) est une mesure trompeuse, ce qui motive une partie du chapitre 5.

## Les achats : `interactions.csv` et `produits_ml.csv`

`interactions.csv` est au **format long** : une ligne par couple (client, produit) pour lequel il y a eu au moins un achat. Les colonnes sont `id_client`, `id_produit`, `nb_achats` et `note` (une note de 1 à 5, renseignée pour environ un achat sur quatre seulement). `produits_ml.csv` décrit les 150 produits : `categorie` (A à D), `prix` en € et `nouveaute` (1 pour les produits récents).

```python hide
n_cli, n_pro = 3000, 150
print("lignes :", len(interactions), "; clients ayant acheté :", interactions["id_client"].nunique(), "sur", n_cli, "; produits :", interactions["id_produit"].nunique())
print("densité de la matrice clients x produits :", round(len(interactions) / (n_cli * n_pro), 3))
print("achats par client : moyenne", round(len(interactions) / n_cli, 1), "; médiane", int(interactions.groupby("id_client").size().median()))
print("part des lignes notées :", round(interactions["note"].notna().mean(), 3))
print("produits par catégorie :", produits["categorie"].value_counts().sort_index().to_dict(), "; nouveaux :", int(produits["nouveaute"].sum()))
```
<!--sortie-->
```text
lignes : 27687 ; clients ayant acheté : 2981 sur 3000 ; produits : 150
densité de la matrice clients x produits : 0.062
achats par client : moyenne 9.2 ; médiane 8
part des lignes notées : 0.249
produits par catégorie : {'A': 44, 'B': 44, 'C': 31, 'D': 31} ; nouveaux : 26
```

Sur 3 000 clients et 150 produits, seules **6,2 %** des cases de la matrice sont remplies (9,2 achats par client en moyenne) : c'est une matrice très **creuse**, caractéristique des systèmes de recommandation (chapitre 7).

## Un jeu réel : `credit_defaut.csv`

Les données de la boutique sont simulées, ce qui nous permet de connaître la vérité. Pour ne pas oublier à quoi ressemble la réalité, le chapitre 5 et le projet du cahier utilisent un **jeu réel et public** : « *Default of Credit Card Clients* ».

> 📦 **Source et licence.** Jeu publié par le dépôt de données de l'université de Californie à Irvine (UCI) et disponible sur OpenML, **licence CC0** (domaine public). Référence : I-C. Yeh et C-H. Lien, « The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients », *Expert Systems with Applications*, 36(2), 2009. Il décrit 30 000 titulaires de cartes de crédit d'une banque de Taïwan en 2005. Les montants sont en dollars taïwanais (NT$). Le fichier a été téléchargé une fois (script `build/telecharger_credit.py`) et est fourni dans `donnees/` : rien n'est téléchargé à l'exécution.

| Variable | Signification |
|---|---|
| `limit_bal` | montant du crédit accordé, en NT$ |
| `sex` | 1 = homme, 2 = femme |
| `education` | 1 = études supérieures, 2 = université, 3 = lycée, 4 = autre |
| `marriage` | 1 = marié(e), 2 = célibataire, 3 = autre |
| `age` | âge, en années |
| `pay_1` à `pay_6` | statut de remboursement, de septembre (`pay_1`) à avril (`pay_6`) : −1 = payé à temps, 1 à 9 = nombre de mois de retard |
| `bill_amt1` à `bill_amt6` | montant de la facture, de septembre à avril |
| `pay_amt1` à `pay_amt6` | montant payé, de septembre à avril |
| `default` | **cible** : 1 si le client est en défaut de paiement le mois suivant |

```python hide
print("clients :", len(credit), "; taux de défaut :", round(credit["default"].mean(), 4), "(", int(credit["default"].sum()), "défauts )")
print("age :", credit["age"].min(), "à", credit["age"].max(), "; médiane", credit["age"].median())
print("limite médiane :", credit["limit_bal"].median(), "NT$ ; maximum", credit["limit_bal"].max())
print("part de femmes :", round((credit["sex"] == 2).mean(), 3))
print("défaut selon pay_1 >= 1 :", round(credit.loc[credit["pay_1"] >= 1, "default"].mean(), 3), "contre", round(credit.loc[credit["pay_1"] < 1, "default"].mean(), 3))
```
<!--sortie-->
```text
clients : 30000 ; taux de défaut : 0.2212 ( 6636 défauts )
age : 21 à 79 ; médiane 34.0
limite médiane : 140000.0 NT$ ; maximum 1000000
part de femmes : 0.604
défaut selon pay_1 >= 1 : 0.503 contre 0.138
```

Sur 30 000 clients, 6 636 (22,1 %) sont en défaut. Le statut du dernier remboursement est très informatif : 50,3 % des clients qui étaient déjà en retard en septembre font défaut, contre 13,8 % des autres. Ce jeu contient aussi des **attributs sensibles** (le sexe, l'état civil, l'âge, le niveau d'études) : c'est pourquoi nous l'utiliserons pour la section facultative sur l'équité (section 5.4), avec toutes les précautions que le sujet demande.

## Les jeux embarqués de scikit-learn

Pour quelques illustrations, nous utilisons aussi des jeux **réels et classiques**, fournis avec la bibliothèque scikit-learn (donc disponibles hors ligne) :

| Jeu | Contenu | Utilisé dans |
|---|---|---|
| `load_digits` | 1 797 images 8 × 8 de chiffres manuscrits | réduction de dimension (chapitre 3), apprentissage semi-supervisé (chapitre 8) |
| `load_breast_cancer` | 569 tumeurs, 30 mesures, bénigne ou maligne | exemples de classification |
| `load_wine` | 178 vins, 13 mesures chimiques, 3 cépages | exemples de classification |
| `load_diabetes` | 442 patients, 10 variables, progression de la maladie | exemples de régression |

```python hide
from sklearn import datasets as D
for nom in ["load_digits", "load_breast_cancer", "load_wine", "load_diabetes"]:
    d = getattr(D, nom)()
    print(f"{nom:20s} {d.data.shape[0]:5d} lignes, {d.data.shape[1]:3d} variables")
```
<!--sortie-->
```text
load_digits           1797 lignes,  64 variables
load_breast_cancer     569 lignes,  30 variables
load_wine              178 lignes,  13 variables
load_diabetes          442 lignes,  10 variables
```

## L'environnement de travail

Ce volume utilise les outils des volumes précédents, avec des bibliothèques d'apprentissage automatique en plus. Voici les commandes d'installation (non exécutées ici : elles installent des paquets sur *votre* machine). Les quatre premiers paquets sont **figés** à la version qui a produit les sorties du livre.

```bash noexec
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy==2.5.3 pandas==3.0.6 scipy==1.18.1 scikit-learn==1.9.1
pip install matplotlib seaborn statsmodels xgboost lightgbm catboost shap lime optuna imbalanced-learn umap-learn
```

| Bibliothèque | Pour quoi faire | Chapitres |
|---|---|---|
| `scikit-learn` | l'outil central : pipelines, validation croisée, modèles, métriques | tous |
| `xgboost`, `lightgbm` | gradient boosting (arbres boostés) | 2 |
| `catboost` | boosting avec traitement natif des variables qualitatives | 2 (facultatif) |
| `optuna` | réglage des hyperparamètres | 1 (facultatif) |
| `imbalanced-learn` (`imblearn`) | rééchantillonnage, SMOTE | 4 |
| `shap`, `lime` | explication des prédictions | 5 |
| `umap-learn` | réduction de dimension non linéaire | 3 (facultatif) |
| `statsmodels` | comparaisons avec le volume II | quelques sections |

Une absence mérite d'être signalée : ce volume **n'utilise pas PyTorch ni TensorFlow**. Les réseaux de neurones apparaissent seulement dans les chapitres facultatifs (autoencodeurs du chapitre 6, aperçu du chapitre 9) : nous les écrivons avec le `MLPRegressor` de scikit-learn ou à la main, et le code PyTorch équivalent est montré sans être exécuté (« non exécuté »).

Les sorties de ce livre ont été produites avec les versions suivantes :

```python hide-code
import platform, importlib
print("Python       :", platform.python_version())
for nom, mod in [("numpy", "numpy"), ("pandas", "pandas"), ("scipy", "scipy"), ("scikit-learn", "sklearn"), ("xgboost", "xgboost"),
                 ("lightgbm", "lightgbm"), ("catboost", "catboost"), ("shap", "shap"), ("optuna", "optuna"),
                 ("imbalanced-learn", "imblearn"), ("umap-learn", "umap")]:
    print(f"{nom:17s}:", importlib.import_module(mod).__version__)
```
<!--sortie-->
```text
Python       : 3.13.3
numpy            : 2.5.3
pandas           : 3.0.6
scipy            : 1.18.1
scikit-learn     : 1.9.1
xgboost          : 3.4.1
lightgbm         : 4.7.0
catboost         : 1.2.10
shap             : 0.52.0
optuna           : 5.0.0
imbalanced-learn : 0.14.2
umap-learn       : 0.5.12
```

> ⚠️ **Les résultats d'apprentissage automatique varient plus légèrement que ceux de la statistique classique.** Un modèle de boosting ou une forêt aléatoire repose sur des tirages aléatoires (nous fixons toujours la graine) et sur des calculs en parallèle dont l'ordre peut changer d'une version à l'autre. Avec d'autres versions, il est normal que vos chiffres s'écartent dans la dernière décimale (un AUC de 0,899 au lieu de 0,900) ; si l'écart dépasse un point, c'est un signal à examiner. Dans ce volume, aucune conclusion ne dépend de la dernière décimale.

> 🧭 **Prêt ?** Au chapitre 1, nous commençons par la démarche qui rend toutes les suivantes possibles : formuler un problème de prédiction, séparer les données, et comprendre pourquoi un modèle ne se juge jamais sur ce qu'il a déjà vu.
