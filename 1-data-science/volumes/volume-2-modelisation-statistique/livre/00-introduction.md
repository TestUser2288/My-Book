# Introduction : de la description à la modélisation

> « Tous les modèles sont faux, mais certains sont utiles. »
> *George Box*

## Là où le volume I nous a laissés

Le volume I vous a donné les gestes de base : **calculer** (mathématiques), **raisonner sous incertitude** (probabilités), **tirer des conclusions honnêtes d'un échantillon** (statistique), **coder** (Python, R), **interroger des données** (SQL) et **travailler proprement** (Git, notebooks, projet reproductible).

À la fin de ce volume, vous saviez répondre à des questions du type : « Les paniers des clients venus des réseaux sociaux sont-ils plus petits que ceux du magasin ? » (un test de Welch), ou « Chaque jour de retard fait-il baisser la satisfaction, et de combien ? » (une pente, avec son intervalle de confiance). Ce sont des questions à **une ou deux variables**.

La vraie vie en pose d'autres :

- « **Toutes choses égales par ailleurs**, combien le canal d'acquisition change-t-il le panier d'un client, une fois qu'on tient compte de son âge ? »
- « Quelle est la **probabilité** qu'un client rachète dans les douze mois, selon son profil ? »
- « Quelles seront mes **ventes** des douze prochains mois ? »
- « **Combien de temps** un client reste-t-il, sachant que certains sont encore là aujourd'hui, donc que leur durée est inconnue ? »

Pour répondre, il ne suffit plus de comparer des moyennes. Il faut un **modèle** : une description mathématique simplifiée du mécanisme qui a produit les données, assez simple pour être comprise, assez riche pour être utile. Ce volume est consacré à la construction, à l'évaluation et à l'interprétation honnête de tels modèles.

> 💡 **Intuition.** Un modèle est une **carte**. Une carte est utile *parce qu'elle simplifie* : une carte à l'échelle 1:1 serait inutilisable. Mais une carte qui oublie un fleuve vous fait tomber à l'eau. Tout le métier du modélisateur tient en deux questions : *qu'a-t-on le droit de simplifier ?* et *comment vérifier qu'on n'a pas oublié le fleuve ?*

## À qui s'adresse ce volume ?

Aux lecteurs qui ont lu le volume I, ou qui ont un bagage équivalent : algèbre linéaire de base (produit de matrices, valeurs propres), dérivées, probabilités usuelles, intervalles de confiance et tests, et un peu de Python. Chaque fois qu'un résultat du volume I est utilisé, nous le disons (« volume I, section 3.4 »), pour que vous puissiez aller le relire.

| Ce que vous devez maîtriser | Où le revoir dans le volume I |
|---|---|
| Produit matriciel, inverse, valeurs et vecteurs propres, SVD | section 1.1 |
| Dérivées, gradient, descente de gradient | sections 1.2 et 1.3 |
| Lois usuelles, espérance, variance, covariance | sections 2.2 et 2.3 |
| Loi des grands nombres, théorème central limite | section 2.4 |
| Estimation, maximum de vraisemblance | section 3.2 |
| Intervalle de confiance, bootstrap | section 3.3 |
| Tests, p-valeurs, tests multiples | sections 3.4 et 3.5 |
| pandas, graphiques | sections 4.4 et 4.5 |

> 🧭 **Les chapitres complémentaires.** Les chapitres 7 (inférence causale), 8 (plans d'expériences) et 9 (statistique spatiale), ainsi que toutes les sections marquées ➕, sont **facultatifs**. On peut lire le volume sans eux. Ils sont là pour celles et ceux qui veulent aller plus loin.

## La carte du volume

Le volume contient six chapitres principaux, qui forment trois blocs, et trois chapitres complémentaires facultatifs. Chaque chapitre a son pendant dans le **cahier d'exercices et d'applications** du volume (voir plus bas).

```text
 BLOC A : relier des variables                  BLOC B : structures des données        BLOC C : incertitude
 ─────────────────────────────                  ──────────────────────────────         ────────────────────
 Chapitre 1 : Régression linéaire               Chapitre 3 : Analyse multivariée       Chapitre 6 : Statistique
      │  (réponse continue)                           (beaucoup de variables,                  bayésienne et simulation
      ▼                                                sans réponse à prédire)
 Chapitre 2 : Modèles linéaires généralisés
      (réponse binaire, comptage, positive)         Chapitre 4 : Séries temporelles
                                                        (observations ordonnées dans le temps)
                                                    Chapitre 5 : Analyse de survie
                                                        (durées, avec censure)

 ➕ Chapitre 7 : Inférence causale   ➕ Chapitre 8 : Plans d'expériences   ➕ Chapitre 9 : Statistique spatiale

                        Cahier : projet du volume (une étude de modélisation complète) et auto-évaluation
```

| Chapitre | Question centrale | Vous saurez… |
|---|---|---|
| **1. Régression linéaire** | Comment expliquer une quantité continue par d'autres variables ? | estimer, interpréter, tester et vérifier un modèle linéaire |
| **2. Modèles linéaires généralisés** | Et si la réponse est un oui/non, un comptage, un montant strictement positif ? | choisir une loi et un lien, ajuster et diagnostiquer un GLM |
| **3. Analyse multivariée** | Comment résumer et regrouper des dizaines de variables ? | réduire la dimension (ACP, analyse factorielle) et segmenter (classification) |
| **4. Séries temporelles** | Comment modéliser et prévoir ce qui évolue dans le temps ? | décomposer, ajuster un ARIMA saisonnier et évaluer des prévisions |
| **5. Analyse de survie** | Comment traiter des durées dont certaines ne sont pas terminées ? | estimer des courbes de survie et mesurer l'effet de variables sur le risque |
| **6. Statistique bayésienne** | Comment exprimer l'incertitude sur un paramètre par une loi de probabilité ? | raisonner à la Bayes et écrire un MCMC |
| **Cahier : projet** | Peut-on tout assembler ? | mener une étude complète : GLM, séries temporelles, survie |

## Cinq idées qui reviennent dans tout le volume

Avant de commencer, voici cinq idées qui traversent chaque chapitre. Elles valent mieux que n'importe quelle formule.

1. **Un modèle = une partie « signal » + une partie « bruit ».** Chaque chapitre propose une façon différente, mais toujours explicite, de dire quelle part est le signal et à quoi ressemble le bruit.
2. **Estimer, c'est choisir les paramètres qui rendent les données les plus plausibles.** Presque tous les modèles de ce volume (régression, GLM, ARIMA, survie) sont ajustés par **maximum de vraisemblance** (volume I, section 3.2) ; la régression linéaire en est le cas particulier le plus simple, et le bayésien en est le prolongement.
3. **Un modèle s'évalue sur des données qu'il n'a pas vues.** Mesurer la qualité d'un modèle sur les données qui ont servi à l'ajuster est un auto-compliment. Validation hors échantillon, validation croisée, rétro-test pour les séries : le même principe sous trois formes.
4. **Les hypothèses se vérifient.** Chaque modèle suppose quelque chose (linéarité, indépendance, stationnarité, risques proportionnels…). Chaque chapitre contient des **diagnostics**, c'est-à-dire des moyens de regarder si l'hypothèse tient.
5. **Association n'est pas causalité.** Un modèle prédictif décrit comment les variables varient ensemble ; il ne dit pas ce qui arriverait si on intervenait. La différence est subtile et essentielle : elle fait l'objet du chapitre 7, et elle est signalée chaque fois qu'elle compte.

## Comment travailler avec ce volume

### Un livre, et son cahier

Ce volume est composé de **deux ouvrages complémentaires** :

- **le livre** (celui que vous lisez) explique les idées : intuition, exemple calculé à la main, démonstration quand elle éclaire, pièges, résumé ;
- **le cahier d'exercices et d'applications** contient tout ce qui se pratique : exercices corrigés, applications guidées sur données, et le projet de fin de volume avec son auto-évaluation.

Le livre renvoie au cahier par une ligne qui termine les sections concernées :

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.

Lisez d'abord la section dans le livre, puis, si vous voulez fixer l'idée, passez au cahier. On peut aussi lire le livre seul : rien d'indispensable à la compréhension n'a été déplacé.

### Le rythme d'une section

Pour chaque notion : une **intuition**, un **exemple minuscule calculé à la main**, la **démonstration** quand elle éclaire, les **pièges**, puis un **résumé**. Les encadrés ont des pictogrammes fixes :

| Encadré | Rôle |
|---|---|
| 💡 **Intuition** | l'idée en langage courant |
| 📐 **Démonstration** | le raisonnement rigoureux (on peut le sauter à la première lecture) |
| ⚠️ **Piège** | l'erreur classique et comment l'éviter |
| 🧪 **Expérience / remarque** | une simulation ou un commentaire |
| ✅ **À retenir** | le résumé de la section |
| 🧭 **Repère** | un guide de lecture, ou une section optionnelle |
| 📒 **Pour s'entraîner** | le renvoi vers les exercices et applications du cahier |

### Le code dans ce livre

Ce n'est pas un livre de programmation : le code n'y apparaît que lorsqu'il aide à comprendre, par exemple un appel court qui montre comment demander un modèle à une bibliothèque. Les formules, les démonstrations et les algorithmes sont expliqués en mathématiques et en français. Les figures, les simulations et les vérifications numériques sont bien produites par du code, mais ce code est **caché** dans les sources : il est exécuté à chaque construction du livre, de sorte que **chaque nombre cité est reproductible**. Les versions complètes se trouvent dans le cahier et dans le dépôt du livre.

### Des données simulées

Une particularité importante de ce volume : **les données sont simulées**. C'est un choix délibéré. Quand on simule, on connaît la **vérité** (les vrais coefficients, la vraie forme de la saisonnalité…), ce qui permet de vérifier que la méthode la retrouve, ou de comprendre pourquoi elle la retrouve mal. À la fin de chaque étude importante, nous dévoilons ce qui avait été programmé. Dans la vie réelle, on n'a jamais cette chance : c'est précisément pourquoi il faut s'entraîner ici. Quand nous utilisons des données réelles (certains jeux embarqués dans les bibliothèques), nous le disons.

> ⚠️ **Simulé ne veut pas dire facile.** Un jeu simulé est plus *propre* que la réalité : pas de valeurs saisies de travers, pas de variables oubliées par le service de collecte. Lorsque vous appliquerez ces méthodes à de vrais jeux, comptez sur une part de travail supplémentaire pour le nettoyage et la vérification (volume I, cahier, projet du volume, étape 1).


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


Quelques constats guideront les choix de modèles :

- **13 % des clients n'ont passé aucune commande** : la dépense annuelle contient donc beaucoup de zéros exacts ;
- la dépense annuelle est très asymétrique : sa moyenne (247 €) dépasse nettement sa médiane (156,5 €), comme les montants du volume I ;
- **un peu plus de la moitié des durées de relation (1 023 sur 2 000) sont censurées** : ces clients sont encore là, leur durée finale est inconnue ; 977 départs ont été observés ;
- environ un client sur deux (50,9 %) a racheté dans les douze mois ;
- 816 clients sont arrivés par les réseaux sociaux, 680 par le site et 504 par le magasin.

L'offre de bienvenue est la variable la plus précieuse du jeu pour la **causalité** : elle a été attribuée par tirage au sort (une pièce lancée pour chaque nouveau client), donc elle est, par construction, indépendante de l'âge, de la ville et de tout le reste. Le tirage a bien équilibré les groupes :


| `offre_bienvenue` | clients | âge moyen | part « Réseaux » | part « Ville E » |
|---|---:|---:|---:|---:|
| 0 | 985 | 36,1 | 40,3 % | 30,3 % |
| 1 | 1 015 | 35,4 | 41,3 % | 31,7 % |

Les deux groupes se ressemblent : c'est exactement ce que la randomisation promet (nous y reviendrons au chapitre 7).

### L'enquête de satisfaction

Six clients sur dix (1 212 sur 2 000) ont répondu à huit questions, notées de 1 (très insatisfait) à 5 (très satisfait). Les quatre premières portent sur les **produits** (qualité, finition, authenticité, rapport qualité/prix) ; les quatre suivantes sur le **service** (délais de livraison, emballage, relation client, facilité de retour). Cette structure est cachée dans les données ; l'analyse factorielle du chapitre 3 la retrouvera.


Les moyennes des huit notes sont toutes voisines de 3,5 (entre 3,51 et 3,64). Mais les questions d'un même thème sont nettement plus corrélées entre elles (0,42 en moyenne pour les produits, 0,48 pour le service) qu'avec une question de l'autre thème (0,12 en moyenne entre les questions de produits et la question 5, sur le service) : deux « blocs » se dessinent, sans que nous ayons eu à le dire.

### Les ventes mensuelles

`ventes_mensuelles.csv` donne, pour chacun des 120 mois de janvier 2016 à décembre 2025, le chiffre d'affaires (`ca`, en €), le nombre de commandes, un indicateur de promotion (`promo`) et un indicateur d'arrêt d'activité (`covid`, mars à juin 2020).


Le chiffre d'affaires annuel passe de 12 658 € en 2016 à 27 630 € en 2025 : une croissance régulière, interrompue en 2020 (15 680 € cette année-là, contre 16 828 € en 2019). Nous décomposerons cette série (tendance, saisonnalité, bruit) au chapitre 4.

> 📦 **Les chiffres du volume I et ceux-ci ne sont pas les mêmes, et c'est normal.** Au volume I, nous avions un échantillon de 400 commandes de l'année 2025. Ici, `ventes_mensuelles.csv` donne le chiffre d'affaires sur dix ans : l'année 2025 y est du même ordre de grandeur que les 24 098 € observés au volume I, mais les deux jeux sont indépendants. Ne cherchez pas à les rapprocher ligne à ligne.

## L'environnement de travail

Ce volume utilise les mêmes outils que le volume I (Python, R, un terminal), avec quelques bibliothèques de plus. Si vous avez suivi le chapitre 6 du volume I, vous savez créer un environnement virtuel ; voici les commandes (non exécutées ici : elles installent des paquets sur *votre* machine).

```bash
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
