# Carte du volume, données et environnement

Cette section sert de référence : le **catalogue des jeux de données**, les **fichiers de vérité**, l'**environnement** nécessaire pour refaire les exemples, ce que le volume **exécute** et ce qu'il se contente de **décrire**, et les **conventions** d'écriture. Elle se lit en dix minutes.

## Les jeux de données

Tout est **simulé**, avec des graines fixes. Le volume reprend **sans les modifier** les jeux du volume III (`build/donnees_a3.py`, construit sur la base de la boutique des volumes I et II) et y ajoute, pour le chapitre 4, deux portefeuilles d'établissements **fictifs** produits par `build/donnees_a5.py` : un petit **assureur automobile** et une petite **banque**. Chaque chapitre crée en outre, quand il en a besoin, ses propres petits jeux (historiques de prix, livraisons mensuelles de fichiers, jeu de questions), versionnés dans `donnees/` sous le préfixe `ch0N-`.

```python hide
import os
import numpy as np
import pandas as pd

tables = {f[:-4]: pd.read_csv(f"donnees/{f}") for f in sorted(os.listdir("donnees")) if f.endswith(".csv") and not f.startswith("ch0")}
```

| Fichier | Contenu | Lignes | Usage principal |
|---|---|---|---|
| `clients.csv` | clients (inscription, naissance, ville, canal d'acquisition, carte de fidélité) | 6 000 | chapitres 1 et 3 |
| `produits.csv` | catalogue (catégorie, prix, coût d'achat, fournisseur) ; **60 noms pour 120 produits** | 120 | chapitres 1, 3 et 5 |
| `commandes.csv` | une ligne par commande (date, client, canal, livraison, code promo) | 36 395 | chapitres 1 à 3 et 5 |
| `lignes_commande.csv` | une ligne par article de commande | 83 905 | chapitres 1, 2 et 5 |
| `retours.csv` | lignes retournées | 5 002 | chapitres 1 et 3 |
| `jours_exploitation.csv` | une ligne par jour : commandes, chiffre d'affaires, météo, promotion, publicité | 1 096 | chapitre 3 (prévision) |
| `sessions_web.csv`, `campagnes.csv` | trafic du site (2025), dépenses publicitaires | 127 022 ; 36 | chapitre 2 |
| `budget_reel_2025.csv`, `compte_resultat_mensuel.csv`, `bilan_annuel.csv`, `benchmark_secteur.csv` | pilotage et comptes de la boutique | 216 ; 36 ; 3 ; 12 | chapitres 2 et 5 |
| `livraisons.csv`, `reappro_fournisseur.csv`, `stock_quotidien.csv` | logistique | 19 420 ; 1 500 ; 7 300 | chapitre 1 (types de faits) |
| `ab_email.csv`, `ab_site.csv`, `jours_incidents.csv`, `employes*.csv`, `departs.csv` | autres jeux du volume III (non utilisés ici, présents par continuité) | — | — |
| `polices.csv` | **nouveau** : 30 000 contrats d'assurance automobile (âge du conducteur, zone, puissance, usage, bonus, canal) | 30 000 | chapitre 4 |
| `expositions.csv` | police-années : exposition, prime annuelle, prime acquise | 84 875 | chapitre 4 |
| `sinistres.csv`, `paiements.csv` | sinistres déclarés au 31/12/2025 et leurs règlements | 5 113 ; 7 093 | chapitre 4 |
| `prets.csv` | **nouveau** : 12 000 prêts octroyés de janvier 2022 à juin 2025 | 12 000 | chapitre 4 |
| `suivi_mensuel.csv` | une ligne par prêt et par mois : encours, jours de retard, incidents, découvert | 229 747 | chapitre 4 |

```python hide
attendu = {"clients": 6000, "produits": 120, "commandes": 36395, "lignes_commande": 83905, "retours": 5002, "jours_exploitation": 1096, "sessions_web": 127022, "campagnes": 36,
           "budget_reel_2025": 216, "compte_resultat_mensuel": 36, "bilan_annuel": 3, "benchmark_secteur": 12, "livraisons": 19420, "reappro_fournisseur": 1500, "stock_quotidien": 7300,
           "polices": 30000, "expositions": 84875, "sinistres": 5113, "paiements": 7093, "prets": 12000, "suivi_mensuel": 229747}
for nom, n in attendu.items():
    assert len(tables[nom]) == n, (nom, len(tables[nom]))
print("tous les effectifs du tableau sont exacts")
```
<!--sortie-->
```text
tous les effectifs du tableau sont exacts
```

### Les deux établissements fictifs du chapitre 4

L'**assureur** vend des contrats d'assurance automobile ; ses tables couvrent 2021 à 2025, évaluées au **31 décembre 2025**. Une ligne de `sinistres.csv` est un sinistre **déclaré** à cette date : ceux qui sont survenus à la fin de 2025 mais ne sont pas encore connus n'y figurent pas, comme dans la réalité. La **banque** accorde des prêts à des particuliers et à des professionnels ; `suivi_mensuel.csv` suit chaque prêt jusqu'à son défaut (90 jours de retard), son remboursement ou la fin du suivi. Aucun nom, aucun pays, aucune autorité de contrôle n'existe dans ces données : les « seuils » des exemples de reporting sont **inventés** et dits tels.

```python
print(tables["sinistres"].head(3).to_string(index=False))
```
<!--sortie-->
```text
id_sinistre id_police date_survenance date_declaration   nature statut  montant_paye  reserve_dossier
    S000001    P00001      2024-01-16       2024-02-08 Matériel   Clos       3621.78             0.00
    S000002    P00008      2024-08-28       2024-09-14 Matériel   Clos       2313.84             0.00
    S000003    P00012      2025-04-26       2025-04-28 Corporel Ouvert          0.00          8841.08
```

## Les fichiers de vérité

Comme dans les volumes précédents, les données **simulées** embarquent leur **vérité programmée**, décrite dans la docstring du générateur (`donnees_a5.py` pour le chapitre 4). Trois fichiers la donnent sous forme de tables, ce qui n'existe **jamais** dans la réalité : `verite_sinistres.csv` (le coût final vrai de chaque sinistre), `verite_prets.csv` (l'âge auquel un prêt fera défaut, et si le défaut est brutal) et `verite_incidents.csv` (volume III). On s'en sert **après** l'analyse pour juger une méthode (« la provision calculée était-elle juste ? », « l'alerte aurait-elle prévenu ? »), jamais pendant.

## Régénérer les données

```bash noexec
python build/donnees_a5.py        # réécrit donnees/*.csv (jeux du volume III + assureur + banque)
```

Les données sont identiques à chaque génération (graines fixes). La commande se lance depuis le dossier du volume.

## L'environnement

| Besoin | Outil | Chapitres |
|---|---|---|
| Manipuler les données | **pandas**, **SQL** | tous |
| Entrepôt local | **DuckDB** (base en colonnes, dans un fichier ou en mémoire), Parquet | 1, 2, 5 |
| Planification | **cron** (la syntaxe), **APScheduler** | 2 |
| Journalisation et contrôles | `logging`, **pandera** | 2 |
| E-mail et API | `smtplib` avec un serveur de test **aiosmtpd** ; **FastAPI**/`requests` | 2 |
| Modèles | **scikit-learn**, **statsmodels**, LightGBM (pour comparer) | 3, 4 |
| Validation de SQL | **sqlglot** | 5 |
| Figures | **matplotlib** (style du livre) | tous |

```python
from importlib.metadata import version
print({p: version(p) for p in ["pandas", "duckdb", "scikit-learn", "statsmodels", "APScheduler", "sqlglot"]})
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'duckdb': '1.5.6', 'scikit-learn': '1.9.1', 'statsmodels': '0.15.0', 'APScheduler': '3.11.3', 'sqlglot': '30.21.0'}
```

### Ce que le volume exécute, et ce qu'il décrit

- **Exécuté** : tout ce qui tourne sur une machine ordinaire sans compte ni service payant : DuckDB, Parquet, planification locale, serveur de messagerie de test, API locale, modèles de scikit-learn et de statsmodels, vérification de requêtes SQL.
- **Décrit, non exécuté** : les entrepôts infonuagiques (BigQuery, Snowflake, Redshift, Azure Synapse), les orchestrateurs et outils de transformation (Airflow, dbt, Power Automate), l'automatisation robotisée (UiPath), les outils d'apprentissage automatique sans code, et tout service de modèle de langage hébergé. Pour comprendre le principe, le livre écrit parfois un **jouet pédagogique** (un mini-exécuteur de graphe de tâches, des « modèles SQL » à la dbt) : il est présenté comme tel, et ne prétend pas reproduire le produit. Les menus et les noms de paramètres de ces outils changent : *à vérifier dans la documentation de votre version*.
- **Aucune capture d'un produit commercial** : le volume montre des schémas dessinés et des captures de pages produites par ses propres programmes.

> ⚠️ **Piège.** Un exemple de configuration d'un outil non exécuté (un fichier de graphe de tâches, une requête dans un dialecte) est **non vérifié** ici. Il illustre un principe ; avant de le copier, essayez-le dans votre environnement.

## Conventions

- **Monnaie et noms** : montants en euros ; villes « Ville A » à « Ville T » ; régions « Région 1 » à « Région 4 » ; aucune personne nommée (« la gérante », « la direction des risques », « le comité de crédit ») ; TVA fictive de 20 %.
- **Dates** : la boutique est photographiée au 31 décembre 2025, comme l'assureur et la banque.
- **Graines** : toute simulation fixe sa graine.
- **Vérités** : quand elles existent, elles sont révélées **après** l'analyse.
- **Cadres de règles** : quand un chapitre évoque des règles internationales (prudentielles, comptables), c'est **comme exemple d'une famille de règles** ; aucun seuil officiel n'est reproduit, aucun format réglementaire n'est imité.

> ✅ **À retenir.** Les données sont fictives et leur vérité est connue : elles servent à apprendre à **construire des systèmes fiables**, pas à mesurer un vrai portefeuille. Le livre n'affirme rien sur un produit qu'il n'exécute pas.
