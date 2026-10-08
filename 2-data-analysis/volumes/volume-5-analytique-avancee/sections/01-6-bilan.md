## Bilan du chapitre 1

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

n = con.df("""SELECT (SELECT COUNT(*) FROM dwh.fait_ventes) AS lignes, (SELECT COUNT(*) FROM dwh.fait_commandes) AS commandes,
              (SELECT COUNT(*) FROM dwh.fait_retours) AS retours, (SELECT COUNT(*) FROM dwh.fait_livraisons) AS livraisons,
              (SELECT COUNT(*) FROM dwh.fait_stock) AS stock""").iloc[0]
assert [int(x) for x in n] == [83905, 36395, 5002, 19420, 7300]
```

Vous savez maintenant :

- **expliquer pourquoi on sépare l'analyse de l'exploitation** : charge, historique, intégration des sources, définitions communes, qualité, droits ; et **distinguer** OLTP et OLAP, **ETL** et **ELT**, entrepôt et lac ;
- **organiser un entrepôt en couches** (arrivée, entrepôt, marts, usages) et **ne jamais corriger à la main** : on corrige la règle et l'on rejoue ;
- **construire un schéma en étoile en SQL** : une table de **faits** au centre (une ligne par ligne de commande, 83 905 lignes), des **dimensions** autour (date, client, produit, canal, promotion), des **clés de substitution**, une ligne **« inconnu »** ;
- **vérifier** une construction : mêmes effectifs et mêmes totaux que la source, même résultat par un second outil, même chiffre que la **comptabilité** (écart maximal de 0,49 € sur trente-six mois, à condition de **ne pas arrondir au stockage**) ;
- **déclarer et tester le grain** de chaque table de faits, et **choisir** parmi les trois types : transaction, instantané périodique, cumulative ;
- **reconnaître les mesures additives, semi-additives et non additives** (un stock ne s'additionne pas dans le temps ; un taux ne se moyenne pas) et **stocker des composantes**, pas des rapports ;
- **traiter une mesure d'en-tête** : les frais de port comptés à chaque ligne donnent 75 458 € au lieu de 46 085 € (+ 64 %) ; la solution est une table de faits à son propre grain ;
- **ne jamais joindre deux tables de faits** (le chiffre d'affaires des jardins passe de 295 k€ à 18 millions) : on agrège d'abord, on joint ensuite (*drill-across*), grâce aux **dimensions conformes** ;
- **éviter de perdre des lignes** par une jointure interne (1 571 lignes et 66 521 € d'un coup) : clé 0 et jointure externe ;
- ➕ **choisir un traitement des attributs qui changent** (type 1, 2 ou 3) et le **charger** de façon idempotente ; mesurer ce que le type 1 fausse (jusqu'à 9,4 % par ville, 32 % pour une catégorie reclassée) ;
- ➕ **lire une matrice des processus** et **bâtir des data marts** qui stockent des sommes et des comptes ;
- ➕ **comprendre ce que changent les entrepôts infonuagiques** (stockage et calcul séparés, colonnes, partitions, facturation à l'usage), le démontrer en local avec Parquet, et **choisir à la bonne échelle**.

Le tableau suivant résume les chiffres que nous avons mesurés.

| Question | Résultat |
|---|---|
| Quatre « chiffres d'affaires 2025 » | 1 324 764 € (TTC), 1 103 970 € (hors taxe), 1 034 230 € (net des retours), 1 352 838 € (erreur de jointure) |
| Étoile contre comptabilité | écart maximal de 0,49 € par mois sur 36 mois (2,80 € si l'on arrondit chaque ligne) |
| Frais de port sur trois ans | 46 085 € contre 75 458 € comptés à la ligne |
| Livraisons par transporteur (A, B, C) | 16,0 %, 26,6 % et 51,0 % de retards ; moyenne simple des taux 31,2 %, taux global 26,6 % |
| Jointure interne avec dimension incomplète | 1 571 lignes et 66 521 € perdus |
| Commandes 2025 : somme par catégorie, distinctes | 25 163 contre 12 946 |
| Chiffre d'affaires 2024, Ville A, type 1 contre type 2 | + 5,8 % |
| Fichier Parquet contre CSV | 7,3 fois plus petit ; lire `montant_ttc` seul = 13,8 % du fichier ; un fichier sur trois ouvert pour 2025 |

Le fil conducteur du chapitre tient en une phrase : **un entrepôt est moins une technologie qu'un accord** sur ce que représente chaque ligne, sur ce que mesure chaque chiffre et sur la façon dont les tables se relient. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Écrire le grain avant de dessiner la table**, et le tester par une requête.
> 2. **Vérifier toute construction par un total** (source, second outil, comptabilité) : un entrepôt qui n'a pas été rapproché n'est qu'une opinion.
> 3. **Agréger d'abord, joindre ensuite** ; stocker des sommes, recalculer les rapports.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées** ; les frais de port sont **calculés** par une règle que nous avons choisie, faute de colonne dans la base d'origine ; l'historique des déménagements et des reclassements est **fabriqué** pour l'exemple. DuckDB joue le rôle de l'entrepôt : aucun service infonuagique n'a été exécuté, et le tableau comparatif de 1.5.4 repose sur des connaissances à vérifier dans la documentation de votre version.

Le chapitre 2 s'intéresse au **trajet** des données : comment les amener dans cet entrepôt **automatiquement, sans doublons et en sachant ce qui s'est passé** quand quelque chose casse. Les idées d'**idempotence**, de **rapprochement** et de **contrôle de chargement** qui ont affleuré ici y deviennent le sujet principal.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 (de la définition d'un chiffre d'affaires à un data mart et à un format en colonnes) et exercices 1.1 à 1.12.
