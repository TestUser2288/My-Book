# Chapitre 2 : Transformation et fusion des données

> « Une analyse commence le jour où toutes les données tiennent dans une seule table, et où l'on sait ce que chaque ligne représente. »

```python hide
import os, sys, tempfile, shutil
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch02 as O
NUM = O.NUM
TMP2 = tempfile.mkdtemp(prefix="ch02_", dir=os.environ.get("TMPDIR"))
```

Un matin, la gérante de la boutique vous apporte une demande qui a l'air simple : « **Je voudrais une seule table de toutes les ventes de l'année, la caisse et le site ensemble, avec le nom du produit et la marge sur chaque ligne.** Ensuite, je pourrai répondre moi-même à mes questions avec un tableau croisé. » Elle ajoute, un peu gênée, que la caisse lui envoie un fichier par mois, que le site web fournit « un export », et qu'elle ne sait plus très bien quand le format a changé.

Vous ouvrez les fichiers. Les douze exports de la caisse n'ont pas tous les mêmes colonnes ni le même codage ; l'export du site exprime ses montants en texte, avec un symbole monétaire, et, à partir de la mi-septembre, **en centimes** ; aucun des deux ne contient le coût d'achat des produits, qui est dans une autre table, ni de numéro de produit utilisable pour la caisse. Tout est là pour répondre à la gérante, mais **rien n'est prêt** : avant l'analyse, il faut **transformer** (créer des variables), **fusionner** (relier des tables), **empiler** (mettre des fichiers bout à bout) et **agréger** (changer le niveau de détail).

Ce chapitre vous apprend ces quatre gestes, et surtout **comment s'assurer qu'on ne s'est pas trompé**. Car chacun de ces gestes peut faire perdre des lignes, en inventer, ou fausser un total **sans qu'aucune erreur ne s'affiche**. Une jointure qui double les lignes donne un chiffre d'affaires deux fois trop grand ; un fichier lu avec la mauvaise décimale divise les montants par cent ; une agrégation faite au mauvais niveau compte deux fois la même commande. La méthode qui traverse tout le chapitre tient en une phrase : **à chaque étape, comparer les effectifs et les totaux avant et après, et expliquer chaque écart**.

> 💡 **Intuition.** Préparer des données, c'est comme **monter un meuble** à partir de plusieurs cartons : chaque pièce est correcte, mais l'ensemble n'est utilisable qu'une fois les pièces assemblées dans le bon ordre. Et, comme pour un meuble, il vaut mieux **vérifier à chaque vissage** que la pièce est bien droite plutôt que de s'en apercevoir à la fin, quand l'étagère penche.

## Quatre gestes, un vocabulaire

Pour que la suite soit lisible, fixons le vocabulaire. Les quatre gestes se distinguent par ce qu'ils font du **nombre de lignes** et du **nombre de colonnes**.

| Geste | Ce qu'il fait | Lignes | Colonnes | Exemple de la boutique |
|---|---|---|---|---|
| **Dériver** | calculer de nouvelles variables à partir des colonnes existantes | inchangées | augmentent | la marge d'une ligne de vente, le trimestre d'une date |
| **Joindre** | relier deux tables par une clé commune | ne devraient pas changer (en cas de 1–n) | augmentent | ajouter le coût d'achat à chaque ligne de vente |
| **Empiler** | mettre bout à bout des tables de même structure | s'additionnent | inchangées | les douze fichiers mensuels de la caisse |
| **Agréger** | résumer par groupes, en changeant le niveau de détail | diminuent | changent | le chiffre d'affaires par mois et par canal |

Un cinquième geste, le **pivot** (passer d'un tableau « large » à un tableau « long » et inversement), est traité dans une section facultative, ainsi que le **rapprochement approximatif** (relier deux enregistrements qui désignent la même chose sans être écrits de la même façon).

## Le chemin de ce chapitre

Le parcours essentiel suit les trois premiers gestes, dans l'ordre où la gérante en a besoin.

- **2.1 Création et dérivation de variables** : calculer une marge, extraire des morceaux de date, fabriquer des classes et des indicateurs, mesurer un délai entre deux commandes, normaliser du texte pour en faire une clé ; et repérer les pièges (division par zéro, valeurs manquantes qui se propagent, fuite d'information).
- **2.2 Fusion et jointure de jeux de données** : comprendre les types de jointure et la **cardinalité**, contrôler les effectifs avant et après, empiler les douze fichiers de la caisse, lire l'export du site, **harmoniser** les deux sources en une table de ventes unique, et chercher ce qui manque.
- **2.3 Agrégation et restructuration** : changer de niveau de détail (ligne, commande, client), distinguer table de faits et dimensions, calculer des parts, des cumuls et des fenêtres, et vérifier par une **somme de contrôle** que rien n'a été perdu.

Deux sections facultatives prolongent ce parcours : **➕ 2.4 Restructuration : pivot et dépivot** (le tableur de stocks de la boutique, saisi à la main) et **➕ 2.5 Appariement approximatif et rapprochement d'enregistrements** (dédoublonner le fichier clients, rapprocher le catalogue du fournisseur).

## Les données du chapitre

Les fichiers de ce chapitre sont **simulés** : ils ont été fabriqués à partir de la base propre du volume I, puis abîmés de façon contrôlée. Des fichiers de **vérité** (`verite_*.csv`) disent ce qui a été injecté : nous ne les ouvrirons qu'en fin d'étude, pour **juger** notre travail, comme on corrige un exercice. Dans la vie réelle, on ne dispose jamais de cette vérité : c'est précisément pourquoi les contrôles de ce chapitre sont indispensables.

| Fichier | Contenu | Particularités |
|---|---|---|
| `caisse/caisse_2025-01.csv` … `caisse_2025-12.csv` | ventes du canal **Boutique** en 2025, un fichier par mois | le format change trois fois dans l'année (codage, séparateur, décimale, noms de colonnes, format des dates) ; lignes de titre, en-têtes répétés, ligne de total, montants vides, lignes doublées |
| `site_commandes.csv`, `site_lignes.csv` | commandes du canal **Site** en 2025 (en-têtes puis lignes) | montants en texte, statuts écrits de plusieurs façons, doublons d'export, commandes de test, commandes annulées, changement de format et d'unité à la mi-septembre |
| `catalogue_fournisseur.csv` | catalogue d'un fournisseur : code, désignation, prix d'achat | désignations réécrites ; certains produits manquent ; d'autres n'existent pas à la boutique |
| `crm_clients.csv` | le fichier clients du CRM | plusieurs lignes pour un même client, noms et e-mails mal écrits |
| `stocks_tableur.xlsx` | stock mensuel saisi à la main dans un tableur | cellules fusionnées, sous-totaux, valeurs textuelles |
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv` | la base propre du volume I | servent de référence (produits, coût d'achat) et de contrôle |

```python hide
lig0 = pd.read_csv("donnees/lignes_commande.csv"); cmd0 = pd.read_csv("donnees/commandes.csv")
cai0, ctrl0 = O.charger_caisse()
NUM("n_fichiers_caisse", len(ctrl0)); NUM("n_lignes_caisse", len(cai0))
so0, sl0 = O.lire_site(); NUM("n_lignes_site_brut", len(so0)); NUM("n_lignes_site_detail", len(sl0))
NUM("n_commandes_base", len(cmd0)); NUM("n_lignes_base", len(lig0))
```

Pour fixer les idées : les douze fichiers de la caisse contiennent {{n_lignes_caisse:,.0f}} lignes de vente (une fois retirés les titres et les en-têtes répétés), l'export du site compte {{n_lignes_site_brut:,.0f}} lignes d'en-têtes de commande et {{n_lignes_site_detail:,.0f}} lignes de détail, et la base propre du volume I contient {{n_commandes_base:,.0f}} commandes et {{n_lignes_base:,.0f}} lignes de commande sur trois ans. Retenez ces ordres de grandeur : vous les retrouverez en fil de chapitre, sous forme de **contrôles**.

> 📦 **Ce que ce chapitre suppose.** Vous savez lire un fichier CSV avec pandas, filtrer, regrouper et faire une jointure simple (volume I, chapitres 3 et 4). Nous reprendrons ces notions en les mettant à l'épreuve de données réelles dans leur désordre. Les tables sont reliées par des clés (`id_commande`, `id_produit`, `id_client`) : le schéma de la base est rappelé dans le volume I, section 3.1.1.
