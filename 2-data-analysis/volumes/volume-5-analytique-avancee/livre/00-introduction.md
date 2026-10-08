# Introduction : des analyses ponctuelles aux systèmes reproductibles

> « Un chiffre que l'on ne sait pas refaire est un chiffre que l'on ne sait pas défendre. »

## Le lundi où vous n'êtes pas là

Depuis des mois, vous préparez chaque début de mois le même rapport pour la gérante : chiffre d'affaires, marge, retards de livraison, ruptures de stock. Vous exportez des fichiers, vous les nettoyez, vous recopiez des formules, vous collez des graphiques dans un document. Cela prend une demi-journée, et cela marche, **tant que c'est vous**.

Un lundi, vous êtes en congé. La responsable logistique lance le rapport à votre place, avec le fichier du mois **précédent** (elle s'est trompée de dossier). Le chiffre d'affaires est faux de 8 %. Personne ne le remarque : le document est bien mis en page, les graphiques sont jolis, et les chiffres ont l'air plausibles. Jeudi, la gérante décide un réapprovisionnement sur la foi de ce rapport.

Cette histoire n'est pas celle d'une erreur de calcul. C'est celle d'une **absence de système** : aucune étape n'a vérifié que le fichier était le bon, que le mois était complet, que le total ressemblait à celui du mois précédent, ni prévenu quelqu'un que quelque chose clochait. Les volumes précédents vous ont appris à **trouver** un résultat juste et à le **montrer**. Celui-ci vous apprend à le **produire de façon fiable, chaque fois, sans vous**.

> 🧭 **Le critère.** Une analyse est professionnelle quand une autre personne, ou vous-même dans six mois, peut la **refaire**, la **vérifier** et la **relancer sans risque**.

## Sept étapes à la main, sept occasions de se tromper

Reprenons le rapport mensuel tel qu'on le fait à la main.


| # | Étape manuelle | Comment elle casse (sans que personne ne le voie) |
|---|---|---|
| 1 | Télécharger les exports | mauvais fichier, mois incomplet, export lancé avant la fin de la journée |
| 2 | Les ouvrir dans le tableur | séparateur, encodage, dates lues à l'envers |
| 3 | Nettoyer à la main | une correction oubliée, une ligne supprimée par erreur |
| 4 | Recopier les formules du mois précédent | une plage décalée d'une ligne |
| 5 | Calculer les indicateurs | une définition qui change (hors taxe ou toutes taxes ?) |
| 6 | Construire les graphiques | un axe qui ne s'est pas mis à jour |
| 7 | Envoyer le rapport | la mauvaise version, la mauvaise liste de destinataires |

Il suffit d'une hypothèse simple pour mesurer le risque : supposons que chaque étape manuelle ait **2 %** de chances de contenir une erreur.

```python
p_etape, n_etapes = 0.02, 7
p_rapport = 1 - (1 - p_etape) ** n_etapes
p_annee = 1 - (1 - p_rapport) ** 12
print(f"un rapport : {p_rapport:.1%} | au moins une erreur dans l'année : {p_annee:.1%}")
```
<!--sortie-->
```text
un rapport : 13.2% | au moins une erreur dans l'année : 81.7%
```

Un rapport sur huit environ contiendrait une erreur, et **plus de quatre années sur cinq** en compteraient au moins une. Le chiffre de 2 % est une hypothèse, pas une mesure ; ce qu'il montre est un ordre de grandeur : **les erreurs d'un processus manuel s'accumulent**, et plus le processus est long, moins il est fiable. L'automatisation ne rend pas les étapes plus intelligentes ; elle les rend **identiques à chaque fois**, ce qui permet enfin de les **contrôler**.


![Le rapport mensuel fait à la main : sept étapes, et à chacune un point d'interrogation, c'est-à-dire un endroit où une erreur peut passer sans être vue.](figures/ch00-chaine-manuelle.png)

## Ce qui change quand l'analyse devient un système

Passer d'une analyse ponctuelle à un système, ce n'est pas écrire plus de code : c'est **ajouter des propriétés** que l'analyse ponctuelle n'a pas besoin d'avoir.

| Propriété | Analyse ponctuelle | Système reproductible |
|---|---|---|
| **Reproductible** | « ça marchait sur mon ordinateur » | mêmes entrées, mêmes sorties, sur n'importe quelle machine |
| **Idempotent** | relancer duplique ou corrompt | relancer **n'ajoute rien** : le résultat est le même |
| **Contrôlé** | on regarde si le chiffre « a l'air bon » | des vérifications écrites (comptage, rapprochement, plausibilité) échouent bruyamment |
| **Journalisé** | « je crois que ça a tourné » | chaque exécution laisse une trace : quand, quoi, combien, pourquoi |
| **Planifié** | on s'en souvient (ou pas) | une échéance, un rattrapage si elle est manquée |
| **Documenté** | dans la tête de l'auteur | définitions, schémas, responsable, procédure en cas de panne |
| **Défini une fois** | chaque rapport recalcule à sa façon | un indicateur est calculé **à un seul endroit** et réutilisé |

La dernière ligne est la plus importante, et c'est elle qui justifie le **premier chapitre** de ce volume : tant que chaque tableau de bord, chaque tableur et chaque rapport recalcule le chiffre d'affaires à sa manière, on aura trois chiffres d'affaires. La solution est de **modéliser les données une fois** (l'entrepôt), de les **charger de façon fiable** (l'ETL), puis d'en tirer les rapports.

> 💡 **Intuition.** Un système de reporting est une chaîne de production. On n'inspecte pas chaque pièce à la main : on installe des **contrôles** aux points où les défauts apparaissent, et l'on s'arrête quand un contrôle échoue.

## Trois idées qui tiennent le volume

1. **Une seule vérité, plusieurs usages.** Les données sont modélisées et nettoyées une fois ; les rapports, les tableaux de bord et les modèles lisent la même source.
2. **Échouer bruyamment.** Un pipeline qui se tait quand il se trompe est pire qu'un pipeline qui s'arrête : il distribue des erreurs avec l'autorité d'une machine.
3. **Prédire n'est pas décider, et générer n'est pas vérifier.** Les modèles prédictifs et les assistants fondés sur des modèles de langage sont des outils puissants **à encadrer** : par une référence simple à battre, par une validation hors échantillon, par des vérifications automatiques de ce qu'ils produisent.

## Carte des cinq chapitres

Les trois premiers chapitres forment le tronc ; le chapitre 4 applique la méthode à un domaine précis, celui du **risque** ; le chapitre 5, complémentaire, ouvre sur l'usage des modèles de langage.

| Chapitre | Question de fond | Ce que vous saurez faire |
|---|---|---|
| **1. Entrepôts de données et modélisation** | « Comment obtenir le même chiffre partout ? » | concevoir un schéma en étoile, déclarer un grain, séparer faits et dimensions ; ➕ dimensions à évolution lente, data marts, entrepôts infonuagiques |
| **2. ETL et automatisation** | « Comment faire tourner tout cela sans moi ? » | charger de façon incrémentale et idempotente, planifier, journaliser, gérer les erreurs ; ➕ outils d'orchestration, API, e-mail |
| **3. Analytique prédictive** | « Que va-t-il se passer, et que changer ? » | construire et évaluer un modèle simple, savoir quand passer la main ; ➕ AutoML |
| **4. Risque et assurance** | « Le portefeuille se dégrade-t-il, et à quelle vitesse ? » | sinistres, portefeuille, alertes, reporting de gestion et réglementaire |
| **➕ 5. LLM pour l'analyse** | « Peut-on déléguer les requêtes et les commentaires ? » | encadrer et vérifier un assistant : text-to-SQL, données synthétiques, rapports |
| **Projet du volume (cahier)** | « Le rapport du lundi, sans moi » | un pipeline de reporting automatisé qui alimente un tableau de bord |

> ✅ **À retenir.** Le travail d'un analyste ne s'arrête pas au résultat : il s'arrête quand le résultat peut être **reproduit, contrôlé et relancé** par quelqu'un d'autre. Automatiser, ce n'est pas aller plus vite : c'est devenir **fiable**.


# Carte du volume, données et environnement

Cette section sert de référence : le **catalogue des jeux de données**, les **fichiers de vérité**, l'**environnement** nécessaire pour refaire les exemples, ce que le volume **exécute** et ce qu'il se contente de **décrire**, et les **conventions** d'écriture. Elle se lit en dix minutes.

## Les jeux de données

Tout est **simulé**, avec des graines fixes. Le volume reprend **sans les modifier** les jeux du volume III (`build/donnees_a3.py`, construit sur la base de la boutique des volumes I et II) et y ajoute, pour le chapitre 4, deux portefeuilles d'établissements **fictifs** produits par `build/donnees_a5.py` : un petit **assureur automobile** et une petite **banque**. Chaque chapitre crée en outre, quand il en a besoin, ses propres petits jeux (historiques de prix, livraisons mensuelles de fichiers, jeu de questions), versionnés dans `donnees/` sous le préfixe `ch0N-`.


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

```bash
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
