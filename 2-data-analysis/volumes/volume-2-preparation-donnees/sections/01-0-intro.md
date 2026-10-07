# Chapitre 1 : Nettoyage des données

> « Les données ne sont jamais sales en elles-mêmes : elles sont sales *pour une question donnée*. »

```python hide
import os, io, re, sys, glob, sqlite3
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
site_brut = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
site_total_brut = site_brut["total"].map(C.nombre).sum()
base = pd.read_csv(os.path.join(D, "lignes_commande.csv")).merge(pd.read_csv(os.path.join(D, "commandes.csv"))[["id_commande", "canal", "date_commande"]], on="id_commande")
ca_site_2025 = base[(base["canal"] == "Site") & (base["date_commande"] >= "2025-01-01")]["montant"].sum()
print(f"somme brute des totaux du site : {site_total_brut:,.0f} € ; chiffre d'affaires du site en 2025 dans la base : {ca_site_2025:,.0f} €")
```
<!--sortie-->
```text
somme brute des totaux du site : 25,012,599 € ; chiffre d'affaires du site en 2025 dans la base : 617,715 €
```

La gérante vous attend avec trois dossiers sous le bras. « Dans le fichier clients, **le revenu manque pour 17 % des personnes** : je les supprime, ou je mets la moyenne à la place ? Dans l'export du site, la somme des commandes de l'année donne **plus de 25 millions d'euros**, alors que le site n'en vend pas un million. Et le logiciel de caisse m'envoie douze fichiers par an qui ne se lisent pas tous de la même façon. Peux-tu me dire ce que je peux croire ? »

Ces trois questions sont le **nettoyage des données** : transformer des fichiers tels que la vie les produit (saisis à la main, exportés par des logiciels qui changent de version, fusionnés sans précaution) en un tableau sur lequel on peut calculer sans se tromper. Les chiffres ci-dessus donnent une idée de l'enjeu : une somme **quarante fois trop grande** n'a rien de subtil, mais d'autres erreurs sont discrètes (un doublon sur quarante, un revenu absent plus souvent chez les jeunes) et faussent un résultat de quelques pour cent **sans que rien ne le signale**.

## Pourquoi le nettoyage prend tant de temps

On répète souvent qu'une analyste passe la majeure partie de son temps à préparer les données. Ce n'est pas une corvée accessoire : **c'est là que se prennent les décisions qui déterminent le résultat**. Supprimer ou imputer, plafonner ou garder, fusionner deux écritures d'un même nom : chaque choix change la moyenne, le total ou la répartition que vous allez annoncer. Et ces choix ne se lisent nulle part dans le résultat final.

> 💡 **Intuition.** Une donnée est « propre » **par rapport à une question**. Une adresse sans code postal est parfaitement utilisable pour compter les clients par ville, et inutilisable pour calculer une distance de livraison. Il n'existe donc pas de nettoyage universel : on nettoie *pour* un usage, et l'on écrit ce que l'on a fait.

Quatre règles de méthode traversent tout le chapitre.

- **Ne jamais modifier le fichier d'origine.** On lit la source, on produit une copie nettoyée. Le brut sert à prouver, plus tard, ce que l'on a changé.
- **Compter avant et après.** Chaque correction a un effet que l'on mesure : « 121 doublons retirés », « 85 montants corrigés ». Une correction dont on ignore l'ampleur est un risque.
- **Écrire des scripts, pas des clics.** Un nettoyage fait dans le tableur ne se rejoue pas le mois suivant ; une fonction, si.
- **Vérifier par une source indépendante.** Un total affiché, une table de référence, un second fichier : la réconciliation (chapitre 3) est le contrôle qui transforme un nettoyage plausible en nettoyage prouvé.

## Le chemin de ce chapitre

Le parcours essentiel suit les quatre grandes familles de défauts.

- **1.1 Valeurs manquantes** : les repérer, distinguer l'absence d'un zéro ou d'un code spécial, comprendre **pourquoi** une valeur manque (hasard, dépendance à une autre variable, dépendance à la valeur elle-même) et ce que coûte une suppression.
- **1.2 Valeurs aberrantes** : séparer l'erreur de saisie, l'extrême réel et le cas rare ; comparer des méthodes statistiques et des règles métier.
- **1.3 Doublons** : exacts ou approchés, ce qu'est une clé, quel enregistrement garder, quel est l'effet sur les totaux.
- **1.4 Incohérences et erreurs de format** : types, unités mélangées, dates ambiguës, catégories écrites de six façons, schémas qui changent d'un fichier à l'autre.

Deux sections facultatives prolongent ce parcours : **➕ 1.5 Nettoyage de texte, dates et heures, encodage, données multilingues** et **➕ 1.6 Stratégies d'imputation et leur impact**, où l'on compare chaque méthode à la vérité.

## Les données du chapitre

Toutes les données sont **simulées** à partir de la base propre du volume I, puis salies de façon contrôlée : nous savons exactement ce qui a été abîmé, ce qui nous permet de **juger** chaque nettoyage (ce que l'on ne peut pas faire dans la vraie vie !). Les fichiers dont le nom commence par `verite_` ou se termine par `_verite` sont cette vérité : on ne s'en sert **qu'à la fin d'une étude**, pour mesurer l'erreur, comme un corrigé.

| Fichier | Contenu | Lignes | Sections |
|---|---|---|---|
| `profil_clients.csv` | profil de 6 000 clients, avec des **trous** (`revenu_annuel`, `depense_2025`, `satisfaction_moy`) | 6 000 | 1.1, 1.6 |
| `profil_clients_verite.csv` | les mêmes clients, **sans trou** | 6 000 | 1.1, 1.6 |
| `montants_saisis.csv` | montants de lignes de commande de 2024, avec des **anomalies** injectées | 6 000 | 1.2 |
| `site_commandes.csv` | export de la plateforme web (commandes du site en 2025) | 6 259 | 1.3, 1.4 |
| `crm_clients.csv` | le fichier clients du CRM, avec **doublons** et saisies disparates | 7 140 | 1.3, 1.4, 1.5 |
| `caisse/caisse_2025-MM.csv` | 12 exports mensuels de la caisse de la boutique | 12 678 | 1.3, 1.4 |

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rapport de manquants, mécanismes d'absence, détection d'aberrantes, doublons du site, changement d'unité, douze fichiers de caisse, nettoyage du CRM, imputations comparées à la vérité) et exercices 1.1 à 1.12.
