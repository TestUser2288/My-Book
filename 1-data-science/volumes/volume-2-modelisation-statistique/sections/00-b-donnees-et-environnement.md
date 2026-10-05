# Les données et l'environnement du volume

## Une boutique, dix ans d'activité

Au volume I, la boutique était observée sur une année. Ici, nous suivons **dix ans d'activité** : un magasin ouvert en 2016, un site web, puis une présence sur les réseaux sociaux. La gérante a fait croître son affaire, a vécu un arrêt brutal au printemps 2020, et a lancé une **offre de bienvenue** tirée au sort pour les nouveaux clients.

Trois jeux de données, fournis dans le dossier `donnees/`, servent à presque tous les chapitres. Ils sont produits par le script `build/donnees2.py` avec des graines fixes : vous obtiendrez exactement les mêmes chiffres que dans le livre.

| Fichier | Contenu | Lignes | Utilisé surtout dans |
|---|---|---|---|
| `clients.csv` | un client par ligne : âge, ville, canal d'acquisition, offre de bienvenue, commandes, panier, dépense, rachat, durée de la relation | 2 000 | chapitres 1, 2, 5, 6, 7 |
| `enquete_satisfaction.csv` | huit questions de satisfaction (notes de 1 à 5) pour les clients qui ont répondu | 1 212 | chapitre 3 |
| `ventes_mensuelles.csv` | chiffre d'affaires et nombre de commandes par mois, 2016 à 2025 | 120 | chapitre 4 |

Aucune valeur n'est manquante dans les trois fichiers. Pour les charger avec pandas (volume I, section 4.4), une ligne suffit :

```python
import pandas as pd
clients = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
print(clients.shape)
```
<!--sortie-->
```text
(2000, 12)
```

```python hide
import numpy as np
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
ventes = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
for nom, tab in [("clients", clients), ("enquete", enquete), ("ventes", ventes)]:
    print(f"{nom:8s} {tab.shape[0]:5d} lignes, {tab.shape[1]:2d} colonnes, {int(tab.isna().sum().sum())} valeur(s) manquante(s)")
```
<!--sortie-->
```text
clients   2000 lignes, 12 colonnes, 0 valeur(s) manquante(s)
enquete   1212 lignes,  9 colonnes, 0 valeur(s) manquante(s)
ventes     120 lignes,  5 colonnes, 0 valeur(s) manquante(s)
```

### Le tableau des clients

Voici les variables de `clients.csv`, avec leur type statistique, car c'est lui qui décidera du modèle (chapitres 1 et 2) :

| Variable | Type | Signification |
|---|---|---|
| `age` | quantitative | âge à l'inscription (18 à 75 ans) |
| `ville` | qualitative nominale | « Ville A » à « Ville E », ou « Autre » |
| `canal_acquisition` | qualitative nominale | canal par lequel le client est arrivé : `Boutique` (le magasin), `Site` (le site web) ou `Réseaux` (les réseaux sociaux) |
| `date_inscription` | date | entre janvier 2019 et juin 2025 |
| `offre_bienvenue` | binaire (0/1) | 1 si le client a reçu une offre de bienvenue ; **attribuée au hasard** |
| `nb_commandes_an` | comptage (0, 1, 2…) | nombre de commandes sur l'année |
| `panier_moyen` | quantitative positive | montant moyen d'une commande en € (0 si aucune commande) |
| `depense_annuelle` | quantitative ≥ 0 | dépense totale de l'année en € : beaucoup de zéros, très asymétrique |
| `rachat_12m` | binaire (0/1) | le client a-t-il racheté dans les douze mois ? |
| `duree_mois` | quantitative positive | durée de la relation, en mois, **jusqu'au départ ou jusqu'à la fin de l'observation** |
| `churn` | binaire (0/1) | 1 : le départ a été observé ; 0 : le client est encore là au 31/12/2025, donc sa durée est **censurée** |

Cette dernière paire de colonnes, `duree_mois` et `churn`, mérite un instant. Un client inscrit en 2024 et toujours actif fin 2025 a une durée de relation d'*au moins* dix-huit mois, mais nous ne connaissons pas sa durée finale. Ignorer ces clients, ou les traiter comme s'ils étaient partis, fausserait toute analyse : c'est le sujet du chapitre 5.

```python hide
print(clients[["age", "nb_commandes_an", "panier_moyen", "depense_annuelle", "duree_mois"]].describe().round(1).to_string())
print()
print("part des clients sans commande   :", round((clients["nb_commandes_an"] == 0).mean(), 3))
print("part des clients qui ont racheté :", round(clients["rachat_12m"].mean(), 3))
print("départs observés / censurés      :", int(clients["churn"].sum()), "/", int((1 - clients["churn"]).sum()))
print("dépense annuelle : moyenne", round(clients["depense_annuelle"].mean(), 1), "; médiane", round(clients["depense_annuelle"].median(), 1))
print()
print(clients["canal_acquisition"].value_counts().to_string())
```
<!--sortie-->
```text
          age  nb_commandes_an  panier_moyen  depense_annuelle  duree_mois
count  2000.0           2000.0        2000.0            2000.0      2000.0
mean     35.8              3.9          53.3             247.0        23.4
std      10.5              3.6          32.1             297.2        17.2
min      18.0              0.0           0.0               0.0         0.0
25%      28.0              1.0          36.2              62.0        10.0
50%      35.0              3.0          52.0             156.5        19.5
75%      43.0              5.0          70.2             326.8        32.8
max      73.0             29.0         245.1            2576.3        82.7

part des clients sans commande   : 0.13
part des clients qui ont racheté : 0.509
départs observés / censurés      : 977 / 1023
dépense annuelle : moyenne 247.0 ; médiane 156.5

canal_acquisition
Réseaux     816
Site        680
Boutique    504
```

Quelques constats guideront les choix de modèles :

- **13 % des clients n'ont passé aucune commande** : la dépense annuelle contient donc beaucoup de zéros exacts ;
- la dépense annuelle est très asymétrique : sa moyenne (247 €) dépasse nettement sa médiane (156,5 €), comme les montants du volume I ;
- **un peu plus de la moitié des durées de relation (1 023 sur 2 000) sont censurées** : ces clients sont encore là, leur durée finale est inconnue ; 977 départs ont été observés ;
- environ un client sur deux (50,9 %) a racheté dans les douze mois ;
- 816 clients sont arrivés par les réseaux sociaux, 680 par le site et 504 par le magasin.

L'offre de bienvenue est la variable la plus précieuse du jeu pour la **causalité** : elle a été attribuée par tirage au sort (une pièce lancée pour chaque nouveau client), donc elle est, par construction, indépendante de l'âge, de la ville et de tout le reste. Le tirage a bien équilibré les groupes :

```python hide
equilibre = clients.groupby("offre_bienvenue").agg(
    clients=("id_client", "count"),
    age_moyen=("age", "mean"),
    part_reseaux=("canal_acquisition", lambda s: (s == "Réseaux").mean()),
    part_ville_e=("ville", lambda s: (s == "Ville E").mean()),
).round(3)
print(equilibre.to_string())
```
<!--sortie-->
```text
                 clients  age_moyen  part_reseaux  part_ville_e
offre_bienvenue                                                
0                    985     36.114         0.403         0.303
1                   1015     35.397         0.413         0.317
```

| `offre_bienvenue` | clients | âge moyen | part « Réseaux » | part « Ville E » |
|---|---:|---:|---:|---:|
| 0 | 985 | 36,1 | 40,3 % | 30,3 % |
| 1 | 1 015 | 35,4 | 41,3 % | 31,7 % |

Les deux groupes se ressemblent : c'est exactement ce que la randomisation promet (nous y reviendrons au chapitre 7).

### L'enquête de satisfaction

Six clients sur dix (1 212 sur 2 000) ont répondu à huit questions, notées de 1 (très insatisfait) à 5 (très satisfait). Les quatre premières portent sur les **produits** (qualité, finition, authenticité, rapport qualité/prix) ; les quatre suivantes sur le **service** (délais de livraison, emballage, relation client, facilité de retour). Cette structure est cachée dans les données ; l'analyse factorielle du chapitre 3 la retrouvera.

```python hide
print(enquete.drop(columns="id_client").describe().loc[["count", "mean", "std", "min", "max"]].round(2).to_string())
print()
print("corrélation moyenne entre q1..q4 :", round(enquete[["q1","q2","q3","q4"]].corr().values[np.triu_indices(4, 1)].mean(), 2))
print("corrélation moyenne entre q5..q8 :", round(enquete[["q5","q6","q7","q8"]].corr().values[np.triu_indices(4, 1)].mean(), 2))
print("corrélation moyenne entre (q1..q4) et q5 :", round(enquete[[f"q{i}" for i in range(1, 5)]].corrwith(enquete["q5"]).mean(), 2))
```
<!--sortie-->
```text
            q1       q2       q3       q4       q5       q6       q7       q8
count  1212.00  1212.00  1212.00  1212.00  1212.00  1212.00  1212.00  1212.00
mean      3.63     3.64     3.59     3.60     3.56     3.54     3.51     3.54
std       0.92     0.90     0.93     0.91     0.94     0.93     0.94     0.94
min       1.00     1.00     1.00     1.00     1.00     1.00     1.00     1.00
max       5.00     5.00     5.00     5.00     5.00     5.00     5.00     5.00

corrélation moyenne entre q1..q4 : 0.42
corrélation moyenne entre q5..q8 : 0.48
corrélation moyenne entre (q1..q4) et q5 : 0.12
```

Les moyennes des huit notes sont toutes voisines de 3,5 (entre 3,51 et 3,64). Mais les questions d'un même thème sont nettement plus corrélées entre elles (0,42 en moyenne pour les produits, 0,48 pour le service) qu'avec une question de l'autre thème (0,12 en moyenne entre les questions de produits et la question 5, sur le service) : deux « blocs » se dessinent, sans que nous ayons eu à le dire.

### Les ventes mensuelles

`ventes_mensuelles.csv` donne, pour chacun des 120 mois de janvier 2016 à décembre 2025, le chiffre d'affaires (`ca`, en €), le nombre de commandes, un indicateur de promotion (`promo`) et un indicateur d'arrêt d'activité (`covid`, mars à juin 2020).

```python hide
print(ventes.head(3).to_string(index=False))
print("...")
print(ventes.tail(2).to_string(index=False))
annuel = ventes.groupby(ventes["mois"].dt.year)["ca"].sum().round(0).astype(int)
print()
print(annuel.to_string())
```
<!--sortie-->
```text
      mois     ca  nb_commandes  promo  covid
2016-01-01  620.0            14      0      0
2016-02-01  757.5            11      0      0
2016-03-01 1007.0            13      0      0
...
      mois     ca  nb_commandes  promo  covid
2025-11-01 2608.5            47      0      0
2025-12-01 4175.0            63      1      0

mois
2016    12658
2017    13846
2018    15280
2019    16828
2020    15680
2021    20847
2022    22934
2023    22884
2024    25249
2025    27630
```

Le chiffre d'affaires annuel passe de 12 658 € en 2016 à 27 630 € en 2025 : une croissance régulière, interrompue en 2020 (15 680 € cette année-là, contre 16 828 € en 2019). Nous décomposerons cette série (tendance, saisonnalité, bruit) au chapitre 4.

> 📦 **Les chiffres du volume I et ceux-ci ne sont pas les mêmes, et c'est normal.** Au volume I, nous avions un échantillon de 400 commandes de l'année 2025. Ici, `ventes_mensuelles.csv` donne le chiffre d'affaires sur dix ans : l'année 2025 y est du même ordre de grandeur que les 24 098 € observés au volume I, mais les deux jeux sont indépendants. Ne cherchez pas à les rapprocher ligne à ligne.

## L'environnement de travail

Ce volume utilise les mêmes outils que le volume I (Python, R, un terminal), avec quelques bibliothèques de plus. Si vous avez suivi le chapitre 6 du volume I, vous savez créer un environnement virtuel ; voici les commandes (non exécutées ici : elles installent des paquets sur *votre* machine).

```bash noexec
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn statsmodels scikit-learn lifelines arch
```

Rôle de chaque nouvelle bibliothèque :

| Bibliothèque | Pour quoi faire | Chapitres |
|---|---|---|
| `statsmodels` | régression, GLM, séries temporelles, survie, tests : la bibliothèque statistique de référence en Python | 1 à 5 |
| `scikit-learn` | réduction de dimension, classification, régularisation, validation croisée | 1, 3 |
| `lifelines` | analyse de survie (certaines fonctions seulement dans ce livre) | 5 |
| `arch` | modèles GARCH | 4 |

Pour les lecteurs de R, les paquets `MASS`, `lme4`, `mgcv`, `survival` et `forecast` sont utilisés pour **comparer** certains résultats avec ceux de Python : c'est une excellente façon de vérifier qu'on a bien compris le modèle, puisque deux logiciels indépendants doivent donner les mêmes nombres.

Les sorties de ce livre ont été produites avec les versions suivantes :

```python hide-code
import platform
import scipy, statsmodels, sklearn
print("Python      :", platform.python_version())
print("numpy       :", np.__version__)
print("pandas      :", pd.__version__)
print("scipy       :", scipy.__version__)
print("statsmodels :", statsmodels.__version__)
print("scikit-learn:", sklearn.__version__)
```
<!--sortie-->
```text
Python      : 3.13.3
numpy       : 2.5.3
pandas      : 3.0.6
scipy       : 1.18.1
statsmodels : 0.15.0
scikit-learn: 1.9.1
```

> ⚠️ **Des versions différentes donnent parfois de très légères différences** dans la dernière décimale des estimations (algorithmes d'optimisation, arrondis), jamais dans les conclusions. Si vos chiffres s'écartent d'un ou deux chiffres significatifs, c'est un signal ; s'ils s'écartent de la dernière décimale, c'est normal.

> 🧭 **Prêt ?** Au chapitre 1, nous commençons par le modèle le plus simple et le plus important de toute la statistique : la droite des moindres carrés, que vous avez déjà croisée plusieurs fois au volume I, enfin généralisée à plusieurs variables.
