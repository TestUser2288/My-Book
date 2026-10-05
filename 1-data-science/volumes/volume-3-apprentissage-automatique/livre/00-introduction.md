# Introduction : statistique ou apprentissage automatique ?

> « Un bon modèle n'est pas celui qui explique le mieux le passé, mais celui qui se trompe le moins sur ce qu'il n'a pas encore vu. »

## Là où le volume II nous a laissés

Le volume II vous a appris à **construire et interpréter des modèles** : une droite de régression, un modèle logistique, un modèle de survie, une prévision. La question centrale était : *que disent les données du mécanisme qui les a produites ?* Un coefficient avait un sens, un intervalle de confiance en avait un autre, et les hypothèses du modèle se vérifiaient avec des diagnostics.

Ce volume change légèrement de question. Une gérante de boutique ne veut pas seulement savoir *pourquoi* certains clients s'en vont ; elle veut **repérer, ce mois-ci, ceux qui vont partir**, pour leur écrire avant qu'il ne soit trop tard. Elle ne demande pas un coefficient : elle demande une liste, et une raison de lui faire confiance.

> 💡 **Intuition.** Expliquer, c'est regarder **en arrière** : comprendre ce qui s'est passé. Prédire, c'est regarder **en avant** : annoncer ce qui n'a pas encore eu lieu. Le premier se juge à la qualité de la compréhension, le second à la qualité des annonces *vérifiées sur des cas que le modèle n'a jamais vus*. Les deux démarches utilisent les mêmes mathématiques ; elles ne posent pas la même exigence.

## Expliquer ou prédire ?

### Deux questions sur les mêmes données

Prenons les douze mille clients de la boutique (présentés dans la section suivante) et une question : *le client va-t-il partir dans les 90 jours ?* On peut y répondre de deux manières.


- **La démarche d'explication** (volume II, section 2.2) : ajuster un modèle logistique et **lire ses coefficients**. Ici, 30 jours de plus sans commande multiplient les cotes de départ par 1,17 environ (par 1,94 pour un écart-type de récence, soit 124 jours), « toutes choses égales par ailleurs », avec un intervalle de confiance et des hypothèses que l'on vérifie. L'objet important est le coefficient.
- **La démarche de prédiction** : peu importe ce que valent les coefficients. On met de côté un quart des clients, on ajuste un modèle sur les trois autres quarts, puis on **mesure sa qualité sur les clients mis de côté**. L'objet important est le score sur des cas nouveaux (ici l'AUC, qui vaut 0,5 pour un modèle sans valeur et 1 pour un modèle parfait : section 5.1).

Le résultat de la seconde démarche est instructif. Sur les clients mis de côté, le modèle logistique atteint un AUC de **0,87** et un modèle d'arbres boostés (chapitre 2) **0,90** : les deux sont utiles, mais le second classe mieux les clients. Remarquez aussi ce que le même modèle fait sur les clients qui ont servi à l'ajuster : l'AUC du boosting y monte à 0,99, alors que celui de la logistique reste à 0,87. Le premier chiffre est un auto-compliment ; seul le second (0,90 sur des clients inédits) est une mesure honnête, et l'écart entre les deux est le signe qu'un modèle souple peut en partie **apprendre par cœur** (chapitre 1, section 1.3). Le boosting serait en outre incapable de nous donner « le » coefficient de la récence : ses prédictions sortent de centaines d'arbres, pas d'une formule. Voilà le compromis central de ce volume : **la précision de la prédiction se paie souvent d'une perte de lisibilité**, que nous apprendrons à compenser (chapitre 5, section 5.3).

### Deux cultures qui se rejoignent

Les deux démarches sont aussi anciennes l'une que l'autre, mais elles ont grandi dans des cultures différentes. Le tableau ci-dessous est une **caricature utile** : dans la pratique, les bons projets empruntent aux deux.

| | Statistique (volume II) | Apprentissage automatique (volume III) |
|---|---|---|
| **Question typique** | Quel est l'effet de cette variable ? Cet écart est-il dû au hasard ? | Quelle valeur ce client aura-t-il demain ? Cette commande est-elle frauduleuse ? |
| **Objectif** | comprendre un mécanisme, quantifier une incertitude | prédire de nouveaux cas, le plus justement possible |
| **Hypothèses** | un modèle probabiliste explicite (normalité, indépendance, linéarité…) | peu d'hypothèses sur la forme ; on ne suppose que des cas **tirés de la même source** |
| **Évaluation** | tests, intervalles de confiance, diagnostics sur les résidus | **score sur des données jamais vues** (jeu de test, validation croisée) |
| **Interprétabilité** | native : un coefficient a un sens | à reconstruire : importances, explications locales |
| **Données** | quelques centaines à milliers de lignes, quelques variables choisies | de milliers à millions de lignes, des dizaines de variables parfois sans sens évident |
| **Risque principal** | un modèle mal spécifié, des hypothèses fausses | le **surapprentissage** et la **fuite d'information** |

Ces deux mondes se rejoignent plus qu'on ne le dit. La régularisation (volume II, section 1.5), la validation croisée (volume II, section 1.4.3) et la régression logistique (volume II, section 2.2) sont déjà des outils d'apprentissage automatique. Réciproquement, un modèle prédictif qu'on n'ose pas expliquer ne sera pas utilisé : l'interprétabilité et l'équité sont une part de l'évaluation, pas un luxe (chapitre 5).

> ⚠️ **Prédire n'est pas expliquer, et encore moins causer.** Un modèle qui prédit bien le départ des clients ne dit pas que *changer* la récence ferait changer le départ. Savoir quelle action déclencherait l'effet voulu est une question causale, traitée au volume II (chapitre 7, facultatif). Nous le rappellerons chaque fois que la tentation sera grande.

## À qui s'adresse ce volume ?

Aux lecteurs des volumes I et II, ou à ceux qui en ont le bagage : statistique de base (intervalles de confiance, tests, bootstrap), régression linéaire et logistique, un peu d'algèbre et de dérivées, et de la pratique de Python. Chaque fois qu'un résultat des volumes précédents est utilisé, nous le citons (« volume II, section 2.2 ») pour que vous puissiez aller le relire.

| Ce que vous devez maîtriser | Où le revoir |
|---|---|
| Gradient, descente de gradient | volume I, section 1.3 (en particulier 1.3.3) |
| Loi des grands nombres, théorème central limite | volume I, section 2.4 |
| Intervalles de confiance, bootstrap | volume I, section 3.3 (en particulier 3.3.5) |
| Tests d'hypothèses, p-valeurs, tests multiples | volume I, sections 3.4 et 3.5 |
| pandas, graphiques | volume I, sections 4.4 et 4.5 |
| Régression linéaire, surajustement, critères d'information, validation croisée | volume II, sections 1.1 et 1.4 |
| Régularisation (Ridge, Lasso) | volume II, section 1.5 |
| Régression logistique, ROC et AUC | volume II, section 2.2 |
| ACP, classification non supervisée (k-means) | volume II, sections 3.1 et 3.3 |

## La carte du volume

Le volume contient **cinq chapitres principaux**, qui suivent le cycle de vie d'un projet, et **quatre chapitres complémentaires** facultatifs. Chaque chapitre a son pendant dans le **cahier d'exercices et d'applications** du volume.

```text
   1. DÉMARCHE            2. MODÈLES               3. SANS ÉTIQUETTES
   formuler, séparer,     des modèles linéaires     regrouper, résumer,
   valider, comparer      aux arbres boostés        réduire la dimension
          │                      │                         │
          └──────────┬───────────┴─────────────────────────┘
                     ▼
   4. VARIABLES ET DÉSÉQUILIBRE            5. ÉVALUATION, CALIBRATION, INTERPRÉTABILITÉ
   préparer les données, créer des         mesurer juste, probabilités fiables,
   variables, traiter les classes rares    expliquer, rester équitable

   ➕ 6. Anomalies et fraude   ➕ 7. Recommandation   ➕ 8. Semi-supervisé et actif   ➕ 9. Renforcement

               Cahier : projet du volume (un pipeline complet sur un jeu réel) et auto-évaluation
```

| Chapitre | Question centrale | Vous saurez… |
|---|---|---|
| **1. La démarche** | Comment savoir qu'un modèle fonctionnera sur des cas nouveaux ? | formuler un problème, séparer les données, valider sans tricher, comparer à un modèle de référence |
| **2. Apprentissage supervisé** | Quelle famille de modèles choisir, et pourquoi ? | utiliser modèles linéaires, arbres, forêts et gradient boosting, et comprendre leurs forces et leurs limites |
| **3. Sans étiquettes** | Que faire quand il n'y a rien à prédire ? | valider un regroupement, réduire la dimension, visualiser |
| **4. Variables et déséquilibre** | Comment préparer les données, et que faire quand l'événement est rare ? | encoder, transformer, créer des variables, pondérer ou rééchantillonner |
| **5. Évaluation et interprétabilité** | Mon modèle est-il bon, fiable, compréhensible, équitable ? | choisir la bonne métrique, calibrer, expliquer (SHAP, LIME), détecter les biais |
| ➕ **6. Anomalies et fraude** | Comment repérer le très rare, sans toujours savoir à quoi il ressemble ? | utiliser forêt d'isolement, densités, autoencodeurs |
| ➕ **7. Recommandation** | Quel produit proposer à quel client ? | construire et évaluer un système de recommandation |
| ➕ **8. Semi-supervisé et actif** | Comment apprendre quand les étiquettes coûtent cher ? | exploiter des données non étiquetées et choisir quoi étiqueter |
| ➕ **9. Renforcement** | Comment apprendre en agissant ? | raisonner en bandits manchots et en Q-learning |
| **Cahier : projet** | Peut-on tout assembler sur un vrai jeu ? | mener un pipeline complet de bout en bout |

> 🧭 **Les chapitres complémentaires.** Les chapitres 6 à 9, ainsi que toutes les sections marquées ➕, sont **facultatifs** : on peut lire les cinq premiers chapitres sans eux. Ils sont là pour celles et ceux qui veulent aller plus loin.

## Six idées qui reviennent dans tout le volume

Avant de commencer, voici six idées qui traversent chaque chapitre. Elles valent mieux que n'importe quelle formule.

1. **La généralisation est le seul but.** Un modèle n'a de valeur que sur des cas qu'il n'a jamais vus. Ajuster parfaitement les données d'apprentissage ne prouve rien, et peut même être un mauvais signe (chapitre 1).
2. **Le jeu de test est sacré.** On le met de côté dès le début, on n'y touche qu'une fois à la fin, et on ne règle rien avec lui. Chaque fois qu'on le regarde avant d'avoir terminé, il devient un peu moins fiable.
3. **La fuite d'information est le piège numéro un.** Un modèle peut obtenir un score magnifique parce qu'il a eu accès, directement ou non, à ce qu'il doit prédire. Le piège est discret et ses effets sont spectaculaires : il se détecte par la méthode, pas par le flair.
4. **Un modèle de référence avant la sophistication.** Avant d'essayer un modèle complexe, on mesure ce que fait une règle bête (toujours prédire la classe majoritaire) et un modèle simple. Un modèle complexe qui ne fait pas mieux n'a pas sa place.
5. **La métrique doit épouser la décision.** Il n'existe pas de « bonne métrique » dans l'absolu : si une fraude manquée coûte cent fois plus qu'une fausse alerte, la mesure doit le refléter (chapitre 5).
6. **Interprétabilité et équité font partie de l'évaluation.** Un modèle précis qu'on ne peut ni expliquer ni contrôler, ou qui traite différemment des groupes de clients sans raison valable, n'est pas un bon modèle (chapitre 5).

## Comment travailler avec ce volume

### Un livre, et son cahier

Ce volume est composé de **deux ouvrages complémentaires** :

- **le livre** (celui que vous lisez) explique les idées : intuition, exemple calculé à la main, démonstration quand elle éclaire, pièges, résumé ;
- **le cahier d'exercices et d'applications** contient tout ce qui se pratique : exercices corrigés, applications guidées sur données, et le projet de fin de volume avec son auto-évaluation.

Le livre renvoie au cahier par une ligne qui termine les sections concernées :

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.

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

Ce n'est pas un livre de programmation : le code n'y apparaît que lorsqu'il aide à comprendre, typiquement un appel court qui montre comment demander un modèle à une bibliothèque. Les formules, les démonstrations et les algorithmes sont expliqués en mathématiques et en français. Les figures, les simulations et les vérifications numériques sont bien produites par du code, mais ce code est **caché** dans les sources : il est exécuté à chaque construction du livre, de sorte que **chaque nombre cité est reproductible**. Les versions complètes se trouvent dans le cahier et dans le dépôt du livre.

### Des données simulées, et un jeu réel

Les données de la boutique sont **simulées**, comme aux volumes précédents. C'est un choix délibéré : quand on simule, on connaît la **vérité** (quelles variables comptent, comment elles interagissent), ce qui permet de vérifier qu'une méthode la retrouve, ou de comprendre pourquoi elle la retrouve mal. À la fin des études importantes, nous dévoilons ce qui avait été programmé. Mais la réalité est plus rugueuse : c'est pourquoi nous utilisons aussi un **jeu réel et public** (30 000 clients d'une banque, section suivante), sur lequel on ne connaît aucune vérité.

> ⚠️ **Simulé ne veut pas dire facile.** Un jeu simulé est plus *propre* que la réalité. Lorsque vous appliquerez ces méthodes à de vrais jeux, comptez sur davantage de nettoyage et de vérification (volume I, cahier, projet du volume, étape 1).

### Reproductibilité d'un résultat d'apprentissage automatique

Les modèles de ce volume font intervenir le hasard (division des données, arbres tirés au sort, initialisations). Nous fixons **toujours** les graines (`random_state=0`) : le livre est ainsi reproductible. Mais deux choses échappent à ce contrôle : les **versions des bibliothèques** (un algorithme d'optimisation qui change, un arrondi) et le **calcul en parallèle**. Il est donc normal que vos résultats diffèrent de quelques unités de la dernière décimale ; une conclusion qui changerait d'une version à l'autre ne serait pas une conclusion. Dans votre propre travail, notez toujours les versions, la graine et la division des données avec les résultats : c'est la condition pour qu'un résultat soit refaisable.


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


Sur 60 000 commandes, 486 sont frauduleuses (0,81 %), réparties en 287 fraudes de type 1 et 199 de type 2. Ici, la règle « aucune commande n'est frauduleuse » a raison dans 99,2 % des cas : l'**exactitude** (la proportion de bonnes réponses) est une mesure trompeuse, ce qui motive une partie du chapitre 5.

## Les achats : `interactions.csv` et `produits_ml.csv`

`interactions.csv` est au **format long** : une ligne par couple (client, produit) pour lequel il y a eu au moins un achat. Les colonnes sont `id_client`, `id_produit`, `nb_achats` et `note` (une note de 1 à 5, renseignée pour environ un achat sur quatre seulement). `produits_ml.csv` décrit les 150 produits : `categorie` (A à D), `prix` en € et `nouveaute` (1 pour les produits récents).


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


Sur 30 000 clients, 6 636 (22,1 %) sont en défaut. Le statut du dernier remboursement est très informatif : 50,3 % des clients qui étaient déjà en retard en septembre font défaut, contre 13,8 % des autres. Ce jeu contient aussi des **attributs sensibles** (le sexe, l'état civil, l'âge, le niveau d'études) : c'est pourquoi nous l'utiliserons pour la section facultative sur l'équité (section 5.4), avec toutes les précautions que le sujet demande.

## Les jeux embarqués de scikit-learn

Pour quelques illustrations, nous utilisons aussi des jeux **réels et classiques**, fournis avec la bibliothèque scikit-learn (donc disponibles hors ligne) :

| Jeu | Contenu | Utilisé dans |
|---|---|---|
| `load_digits` | 1 797 images 8 × 8 de chiffres manuscrits | réduction de dimension (chapitre 3), apprentissage semi-supervisé (chapitre 8) |
| `load_breast_cancer` | 569 tumeurs, 30 mesures, bénigne ou maligne | exemples de classification |
| `load_wine` | 178 vins, 13 mesures chimiques, 3 cépages | exemples de classification |
| `load_diabetes` | 442 patients, 10 variables, progression de la maladie | exemples de régression |


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
