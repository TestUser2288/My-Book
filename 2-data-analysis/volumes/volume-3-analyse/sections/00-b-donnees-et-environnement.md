# Carte du volume, données et environnement

Cette section ouvre le volume par quatre choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce que l'on y sait d'avance), le mode d'emploi des **fichiers de vérité**, et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à une question de la gérante. Les chapitres 1 à 6 forment le parcours essentiel et se lisent dans l'ordre ; les sections marquées ➕ sont facultatives, et les chapitres 7 à 13 sont **entièrement complémentaires** : on les lit selon ses besoins.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Analyse exploratoire** | « Que contiennent vraiment ces données ? » | analyse univariée, bivariée et multivariée, motifs et anomalies ; ➕ liste de contrôle EDA |
| **2. Tests, tests A/B, corrélation** | « Le nouvel e-mail marche-t-il mieux ? » | tests essentiels, conception et lecture d'un test A/B, corrélation ; ➕ catalogue des tests ; ➕ puissance et taille d'échantillon |
| **3. Régression** | « Qu'est-ce qui fait varier mes ventes ? » | régression linéaire, lire les coefficients, ➕ régression logistique |
| **4. Segmentation et cohortes** | « Quels sont mes types de clients, et restent-ils ? » | segmentation, cohortes ; ➕ RFM, valeur vie client, churn ; ➕ entonnoirs |
| **5. Séries temporelles** | « Combien vendrons-nous en décembre ? » | tendance, saisonnalité, moyennes mobiles, prévisions simples ; ➕ planification |
| **6. KPI** | « Quels chiffres dois-je suivre chaque semaine ? » | bon indicateur, arbres d'indicateurs, cibles et seuils |
| **➕ 7. Écarts et causes racines** | « Pourquoi n'avons-nous pas atteint le budget ? » | budget contre réalisé, prix-volume-mix, causes |
| **➕ 8. Pareto, ABC, benchmarking** | « Sur quoi concentrer mes efforts ? » | Pareto, analyse ABC, comparaison interne et externe |
| **➕ 9. Analyse financière** | « La boutique est-elle rentable ? » | compte de résultat, bilan, ratios, seuil de rentabilité |
| **➕ 10. Marketing et web** | « D'où viennent mes clients, et ce que je dépense en publicité rapporte-t-il ? » | sessions, entonnoir, coût d'acquisition, attribution |
| **➕ 11. Opérations et logistique** | « Pourquoi les livraisons sont-elles en retard ? » | niveau de service, stocks, fournisseurs |
| **➕ 12. Ressources humaines** | « Pourquoi les gens partent-ils ? » | turnover, rémunération et équité, prévision des départs |
| **➕ 13. Sensibilité et scénarios** | « Et si le prix des achats montait de 5 % ? » | tornade, Monte-Carlo, scénarios |
| **Projet du volume (cahier)** | « Répondez à une vraie question, de bout en bout » | une question, des données, une méthode, une recommandation |

## Les jeux de données

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a3.py` : vos résultats seront identiques à ceux du livre. Le script part de la base de la boutique des volumes I et II (clients, commandes, lignes, retours, jours d'exploitation), reprise **sans modification**, et y ajoute des jeux propres à l'analyse : tests A/B, sessions web, budget, comptes, logistique, ressources humaines. Ces jeux sont **déjà propres** : le nettoyage est le sujet du volume II, ici on analyse. Aucune donnée ne vient d'une entreprise réelle.

```python hide
import os, glob
import numpy as np
import pandas as pd

def lire(nom, **kw):
    return pd.read_csv(f"donnees/{nom}", **kw)

tables = {f[:-4]: lire(f) for f in sorted(os.listdir("donnees")) if f.endswith(".csv")}
```

| Fichier | Contenu | Lignes | Chapitres | Vérité connue ? |
|---|---|---|---|---|
| `clients.csv` | clients (inscription, naissance, ville, canal d'acquisition, carte de fidélité) | 6 000 | 1, 4 | oui (volume I) |
| `produits.csv` | catalogue (catégorie, prix, coût d'achat, fournisseur) | 120 | 1, 7, 8, 11 | oui |
| `commandes.csv` | une ligne par commande (date, client, canal, livraison, code promo) | 36 395 | 1, 3, 4, 8 | oui |
| `lignes_commande.csv` | une ligne par article de commande | 83 905 | 1, 4, 7, 8 | oui |
| `retours.csv` | lignes retournées | 5 002 | 1, 3 | oui |
| `jours_exploitation.csv` | une ligne par jour : commandes, chiffre d'affaires, météo, promotion, publicité | 1 096 | 1, 3, 5 | oui (effets programmés) |
| `jours_incidents.csv` | la même série avec des **incidents injectés** | 1 097 | 1, 5 | oui (`verite_incidents.csv`) |
| `ab_email.csv` | test d'objet d'e-mail (A contre B) | 12 000 | 2 | oui (effet réel connu) |
| `ab_site.csv` | test d'une nouvelle page de paiement | 38 622 | 2 | oui (effet réel connu) |
| `sessions_web.csv` | sessions du site en 2025 : source, appareil, entonnoir | 127 022 | 4, 6, 10 | partiellement |
| `campagnes.csv` | dépenses publicitaires mensuelles par source | 36 | 10 | oui |
| `budget_reel_2025.csv` | budget et réalisé par mois, catégorie et canal | 216 | 7 | oui |
| `benchmark_secteur.csv` | médiane et quartiles **fictifs** d'un secteur | 12 | 6, 8 | par construction |
| `compte_resultat_mensuel.csv` | compte de résultat mensuel (36 mois) | 36 | 9, 13 | oui |
| `bilan_annuel.csv` | bilan 2023–2025 | 3 | 9 | oui |
| `livraisons.csv` | livraisons des commandes Site et Réseaux | 19 420 | 11 | oui (transporteurs) |
| `reappro_fournisseur.csv` | commandes d'achat et délais | 1 500 | 11 | oui (fournisseur E) |
| `stock_quotidien.csv` | niveau de stock de 20 produits en 2025 | 7 300 | 11 | oui |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | collaborateurs, collaborateur-année, départs | 64 ; 245 ; 20 | 12 | oui (facteurs de départ) |

```python hide
attendu = {"clients": 6000, "produits": 120, "commandes": 36395, "lignes_commande": 83905, "retours": 5002, "jours_exploitation": 1096, "jours_incidents": 1097, "ab_email": 12000,
           "ab_site": 38622, "sessions_web": 127022, "campagnes": 36, "budget_reel_2025": 216, "benchmark_secteur": 12, "compte_resultat_mensuel": 36, "bilan_annuel": 3,
           "livraisons": 19420, "reappro_fournisseur": 1500, "stock_quotidien": 7300, "employes": 64, "employes_annees": 245, "departs": 20}
for nom, n in attendu.items():
    assert len(tables[nom]) == n, (nom, len(tables[nom]))
print("tous les effectifs du tableau sont exacts")
```
<!--sortie-->
```text
tous les effectifs du tableau sont exacts
```

### La base de la boutique

C'est la base des volumes précédents. Rappelons ses colonnes.

| Table | Colonnes principales |
|---|---|
| `clients` | `id_client`, `date_inscription`, `annee_naissance`, `ville`, `canal_acquisition`, `fidelite` (0/1), `email_valide`, `consentement_marketing` |
| `produits` | `id_produit`, `nom_produit`, `categorie`, `prix_vente`, `cout_achat`, `fournisseur`, `date_lancement` |
| `commandes` | `id_commande`, `date_commande`, `heure`, `id_client`, `canal` (Boutique, Site, Réseaux), `mode_livraison`, `code_promo` |
| `lignes_commande` | `id_ligne`, `id_commande`, `id_produit`, `quantite`, `prix_unitaire`, `remise_pct`, `montant` |
| `retours` | `id_retour`, `id_ligne`, `date_retour`, `motif`, `montant_rembourse` |
| `jours_exploitation` | `date`, `jour_semaine`, `nb_commandes`, `chiffre_affaires`, `temperature_moy`, `pluie_mm`, `promo_active`, `depense_pub` |

> ⚠️ **Un piège hérité du volume I.** Le catalogue compte 120 produits mais seulement **60 noms distincts** : chaque nom est porté par deux produits à des prix différents. Dans ce volume, **on identifie toujours un produit par `id_produit`**, jamais par son nom.

La vérité programmée de cette base (docstring de `donnees_a1.py`) est utile dès le chapitre 1 : les **commandes** augmentent de 18 % les jours de promotion, de 1,5 % pour 1 000 € de dépense publicitaire hebdomadaire, baissent de 8 % les jours de pluie dans le canal Boutique et montent de 5 % dans le canal Site ; la tendance est de +6 % par an, la saison creuse janvier-février et l'été et culmine en novembre-décembre, le samedi pèse +40 % et le dimanche −35 %. Vous pourrez ainsi mesurer ce que vos analyses retrouvent.

```python hide-code
cmd, lig, cli, ret = tables["commandes"], tables["lignes_commande"], tables["clients"], tables["retours"]
print("période des commandes :", cmd["date_commande"].min(), "à", cmd["date_commande"].max(), "| canaux :", cmd["canal"].value_counts().to_dict())
print("lignes par commande :", round(len(lig) / len(cmd), 2), "| taux de retour (lignes) :", round(len(ret) / len(lig) * 100, 1), "%")
print("produits :", tables["produits"]["id_produit"].nunique(), "| noms distincts :", tables["produits"]["nom_produit"].nunique())
```
<!--sortie-->
```text
période des commandes : 2023-01-01 à 2025-12-31 | canaux : {'Boutique': 16975, 'Site': 15463, 'Réseaux': 3957}
lignes par commande : 2.31 | taux de retour (lignes) : 6.0 %
produits : 120 | noms distincts : 60
```

### Les jeux propres à l'analyse

| Jeu | Colonnes principales | Ce qu'on y a programmé |
|---|---|---|
| `jours_incidents` | comme `jours_exploitation` | une panne du site (3 jours), une grosse commande d'un professionnel (+4 200 €), une erreur de saisie (×10), une fermeture (2 jours), une journée en double ; `verite_incidents.csv` les liste |
| `ab_email` | `id_contact`, `groupe` (A/B), `heure_envoi`, `est_client`, `ouvert`, `clique`, `achat_7j`, `montant_7j` | B ouvre plus souvent ; l'effet réel sur l'achat est de +0,4 point, **trop petit pour être détecté** avec cette taille |
| `ab_site` | `id_session`, `date`, `groupe`, `appareil`, `nouveau_visiteur`, `commande`, `montant` | l'effet existe **sur mobile seulement** ; les groupes ne sont pas équilibrés (**SRM**) |
| `sessions_web` | `id_session`, `date`, `source`, `appareil`, `nouveau_visiteur`, `pages_vues`, `duree_s`, `ajout_panier`, `debut_paiement`, `commande`, `id_commande` | conversion par source : e-mail ≈ 9 %, direct ≈ 7 %, organique ≈ 4 %, référent ≈ 3,5 %, payant ≈ 3 %, réseaux ≈ 2 % |
| `campagnes` | `mois`, `source`, `depense`, `impressions`, `clics` | trois sources payantes (payant, e-mail, réseaux), plus fortes en novembre-décembre |
| `budget_reel_2025` | `mois`, `categorie`, `canal`, `ca_budget`, `ca_reel`, `quantite_*`, `prix_moyen_*`, `marge_*` | budget = 2024 réel × 1,08, avec des erreurs de plan par catégorie |
| `benchmark_secteur` | `indicateur`, `unite`, `mediane_secteur`, `quartile_1`, `quartile_3` | valeurs **fictives** d'un « secteur » |
| `compte_resultat_mensuel` | `mois`, `ca_ht`, `achats`, `marge_brute`, `frais_personnel`, `loyers_charges`, `marketing`, `livraison`, … , `resultat_exploitation` | TVA fictive de 20 % ; coûts fixes et variables |
| `bilan_annuel` | `annee`, `immobilisations_nettes`, `stock`, `creances_clients`, `tresorerie`, `dettes_fournisseurs`, `autres_dettes`, `capitaux_propres`, `emprunt`, … | un bilan équilibré, trois exercices |
| `livraisons` | `id_commande`, `transporteur`, `date_expedition`, `date_livraison`, `delai_promis_j`, `colis_abime`, `retard` | le transporteur C est plus lent et abîme plus de colis ; décembre est un mois de retards |
| `reappro_fournisseur` | `fournisseur`, `id_produit`, `delai_promis_j`, `delai_reel_j`, `quantite_commandee`, `quantite_recue` | le fournisseur E est peu fiable |
| `stock_quotidien` | `id_produit`, `date`, `stock_fin_jour`, `demande`, `rupture`, `point_de_commande` | une politique de réapprovisionnement à point de commande, avec des aléas de délai |
| `employes_annees` | `id_employe`, `annee`, `poste`, `site`, `genre`, `anciennete`, `salaire_brut_mensuel`, `heures_sup_mensuelles`, `jours_absence`, `evaluation`, `promotion`, `depart_dans_l_annee` | le départ croît avec les heures supplémentaires et un salaire sous la médiane du poste, et baisse après une promotion ; un écart salarial de 3 % entre femmes et hommes |

```python hide-code
em, es, sw = tables["ab_email"], tables["ab_site"], tables["sessions_web"]
print("ab_email :", em.groupby("groupe").size().to_dict(), "| taux d'achat A et B :", em.groupby("groupe")["achat_7j"].mean().round(4).to_dict())
print("ab_site : sessions par groupe", es.groupby("groupe").size().to_dict(), "| part de B :", round((es["groupe"] == "B").mean(), 3))
print("sessions_web : commandes", int(sw["commande"].sum()), "| conversion globale :", round(sw["commande"].mean() * 100, 2), "%")
liv = tables["livraisons"]
print("livraisons : part en retard", round(liv["retard"].mean() * 100, 1), "% | par transporteur :", (liv.groupby("transporteur")["retard"].mean() * 100).round(1).to_dict())
ea = tables["employes_annees"]
print("RH : collaborateurs", ea["id_employe"].nunique(), "| collaborateur-années", len(ea), "| départs", int(ea["depart_dans_l_annee"].sum()))
```
<!--sortie-->
```text
ab_email : {'A': 6000, 'B': 6000} | taux d'achat A et B : {'A': 0.0292, 'B': 0.0338}
ab_site : sessions par groupe {'A': 20048, 'B': 18574} | part de B : 0.481
sessions_web : commandes 6078 | conversion globale : 4.78 %
livraisons : part en retard 26.6 % | par transporteur : {'Transporteur A': 16.0, 'Transporteur B': 26.6, 'Transporteur C': 51.0}
RH : collaborateurs 64 | collaborateur-années 245 | départs 20
```

Les chiffres montrent déjà ce que les chapitres exploreront : une liste de diffusion de 12 000 contacts coupée en deux groupes égaux, une répartition 52/48 du test du site (qui n'a pas l'air d'une répartition au hasard), 6 078 commandes du Site rattachées à des sessions, et un jeu RH de seulement 20 départs, dont il faudra se méfier.

> ⚠️ **Les petits effectifs.** `employes_annees` ne compte que 20 départs, `bilan_annuel` que 3 lignes, `campagnes` que 36 : les conclusions tirées de si peu de lignes sont fragiles, et les chapitres concernés le disent. Savoir **quand les données ne permettent pas de conclure** fait partie de l'analyse.

> ⚠️ **Des données de groupe.** Les collaborateurs du jeu RH sont ceux d'un **groupe** auquel appartient la boutique (entrepôt et siège compris) : ils ne sont pas tous payés par le compte de résultat de la boutique. Les deux jeux ne se recoupent donc pas, et on ne cherchera pas à les rapprocher.

## Les fichiers de vérité

Deux fichiers jouent le rôle de **corrigé** : `verite_incidents.csv` (les 8 incidents injectés dans `jours_incidents.csv`, avec leur date, leur type et leur description) et, pour les autres jeux, la **docstring de `build/donnees_a3.py`**, qui consigne la loi programmée de chaque jeu. On les consulte **après** avoir mené son analyse, pour mesurer ce que l'on a retrouvé et ce qu'on a raté : jamais pour décider ce que l'analyse doit contenir.

```python hide-code
v = tables["verite_incidents"]
print(v[["date", "type"]].to_string(index=False))
```
<!--sortie-->
```text
      date               type
2025-03-12         panne_site
2025-03-13         panne_site
2025-03-14         panne_site
2025-06-18       commande_b2b
2025-09-09      erreur_saisie
2025-04-28 fermeture_boutique
2025-04-29 fermeture_boutique
2025-10-20    doublon_journee
```

## Régénérer les données

Le script s'exécute en quelques secondes et reproduit **exactement** les mêmes fichiers (graines fixes). Il faut le lancer depuis le dossier du volume :

```bash noexec
python build/donnees_a3.py        # réécrit donnees/*.csv
```

Si vous modifiez les données, relancez aussi le calcul du chapitre : plusieurs résultats cités (par exemple, la taille d'un effet détecté ou non dans un test A/B) dépendent de la **graine** et du **tirage**, et un autre tirage donnerait d'autres chiffres, parfois une autre conclusion.

## L'environnement

Le volume utilise les outils des deux volumes précédents ; voici ce qui sert à quoi.

| Besoin | Outil | Chapitres |
|---|---|---|
| Manipuler les données | **pandas**, `polars` (mentionné), SQL (SQLite, DuckDB) | tous |
| Tests statistiques | **scipy.stats**, **statsmodels** | 2 |
| Régressions et séries temporelles | **statsmodels** (OLS, logit, décomposition, lissage exponentiel) | 3, 5, 9 |
| Segmentation et classification | **scikit-learn** (k-moyennes) | 4, 12 |
| Graphiques | **matplotlib** (style du livre) | tous |
| Calculs équivalents en R | **tidyverse** (blocs `r`, quand utile) | 1, 3 |
| Tableur | Excel (non installé ici), **LibreOffice Calc** pour vérifier des formules | 6, 9, 13 |
| Outils d'analyse web et de BI | Google Analytics et outils de tableau de bord : **non exécutés** | 10 |

Le volume ne dépend d'**aucune** nouvelle bibliothèque par rapport aux volumes précédents. Versions utilisées pour ce livre :

```python
from importlib.metadata import version
print({p: version(p) for p in ["pandas", "numpy", "scipy", "statsmodels", "scikit-learn", "matplotlib"]})
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'numpy': '2.5.3', 'scipy': '1.18.1', 'statsmodels': '0.15.0', 'scikit-learn': '1.9.1', 'matplotlib': '3.11.2'}
```

> 🧭 **Excel, LibreOffice et les captures d'écran.** Excel n'est pas installé sur la machine qui produit ce livre. Quand une section montre une formule de tableur, son résultat a été **recalculé avec LibreOffice Calc** et recoupé par pandas ; les « copies d'écran » de tableur sont des **maquettes dessinées**, légendées comme telles. Les vraies captures d'écran ne portent que sur des outils libres exécutés ici ; les outils commerciaux (tableurs en ligne, Google Analytics) sont décrits, jamais reproduits.

## Conventions

- **Monnaie et noms** : les montants sont en euros, les villes s'appellent « Ville A » à « Ville T », les noms de personnes n'existent pas ; la TVA est fictive (20 %).
- **Dates** : on analyse l'année 2025 (et 2023–2024 pour les tendances), la photographie étant prise au 31 décembre 2025.
- **Graines** : toute simulation fixe sa graine, pour que les résultats se reproduisent.
- **Ordre de lecture d'un résultat** : estimation, incertitude, ce que cela permet de conclure, ce que cela ne permet pas de conclure (voir l'introduction).
- **Vérité programmée** : quand elle existe, elle est révélée **après** l'analyse.

> ✅ **À retenir.** Les données sont fictives, propres, et leur vérité est connue : elles servent à apprendre à **choisir une méthode** et à **mesurer ce qu'elle retrouve**. Le volume suit treize chapitres, dont six essentiels ; chaque chapitre répond à une question de la gérante, et chaque jeu de données dit d'avance ce qu'on pourra y retrouver.
