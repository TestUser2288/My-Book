# Introduction : des modèles aux systèmes

> « Un modèle n'a de valeur que le jour où quelqu'un s'en sert, et il ne la garde que tant que quelqu'un s'en occupe. »

## Là où le volume III nous a laissés

Le volume III vous a appris à **construire un modèle prédictif honnête** : formuler le problème, séparer les données, éviter la fuite d'information, comparer à une référence, choisir une métrique, calibrer, expliquer. Son projet final, sur un jeu réel de défauts de crédit, aboutissait à un modèle d'AUC 0,78 sur des clients jamais vus, avec son intervalle de confiance, un seuil choisi par les coûts, une calibration vérifiée et une analyse d'équité (volume III, cahier, projet du volume).

C'est un vrai résultat, mais ce n'est pas encore un **service**. La gérante de la boutique ne veut pas un notebook : elle veut, **chaque lundi matin**, la liste des clients à rappeler, qui arrive toute seule, qui ne se trompe pas en silence quand quelque chose change en amont, qui coûte raisonnablement cher, et qu'on peut expliquer et reprendre si la personne qui l'a écrite part. Ce volume est consacré à ce qui sépare le modèle de ce service.

> 💡 **Intuition.** Un modèle est une **fonction** : des nombres en entrée, un nombre en sortie. Un système est une **organisation** autour de cette fonction : d'où viennent les entrées, qui vérifie qu'elles sont saines, où tourne le calcul, qui lit la sortie, comment on s'aperçoit que la fonction a cessé d'être juste, et comment on la remplace sans interrompre le service. Le volume III s'est occupé de la fonction ; celui-ci s'occupe de l'organisation.

Le volume élargit aussi la palette des modèles. Les **réseaux de neurones profonds** et les **modèles de langage** ouvrent des problèmes (reconnaître une image, lire un avis, répondre à une question) qu'un tableau de nombres ne sait pas exprimer ; le **calcul distribué** permet de traiter des volumes de données que pandas ne peut pas contenir. Ces modèles plus grands rendent l'organisation autour d'eux plus nécessaire encore.

## Un modèle dans un notebook n'est pas un produit

### Cinq écarts

Entre le notebook où le modèle a été mis au point et le service qui l'emploie, cinq écarts apparaissent presque toujours.

| Écart | Dans le notebook | En production |
|---|---|---|
| **Les données** | un fichier propre, figé, déjà nettoyé | des sources qui changent, arrivent en retard, contiennent des doublons, des unités différentes, des valeurs absentes (chapitre 5) |
| **L'échelle** | tout tient en mémoire, on relance quand on veut | des millions de lignes, des délais à tenir, des calculs répartis sur plusieurs machines (chapitre 3) |
| **La fiabilité** | si cela plante, on relance la cellule | le service doit répondre, ou échouer **proprement** ; un résultat faux sans erreur est pire qu'une erreur (chapitre 4) |
| **Le coût** | gratuit : c'est un ordinateur portable | du calcul, du stockage, des licences, du temps de personnes ; un très gros modèle n'est pas toujours rentable (chapitres 2 et 6) |
| **La maintenance** | le modèle est « terminé » | le monde change : le modèle vieillit, il faut le surveiller, le réentraîner, savoir quelle version a produit quelle prédiction (chapitre 4) |

### Une panne qui ne fait aucun bruit

Voici un exemple volontairement banal. Reprenons le modèle de départ des clients du volume III (un gradient boosting, entraîné sur 9 000 clients et évalué sur 3 000 autres). Il fonctionne bien. Puis, en amont, quelqu'un modifie une extraction : le montant dépensé sur douze mois n'est plus exprimé en **euros** mais en **centimes**. Le modèle reçoit donc des montants cent fois trop grands.


Le modèle de départ obtient une AUC de **0,900** sur le jeu de test, avec une probabilité moyenne prédite de 0,126 pour un taux réel de 0,14. Après le changement d'unité (le montant moyen passe de 181 € à 18 119 « € »), **le programme ne lève aucune erreur et ne produit aucune valeur manquante** : il continue de répondre. Mais sa probabilité moyenne prédite tombe à 0,085, l'AUC à 0,879, et la prédiction de **606 clients sur 3 000 (20,2 %)** bouge de plus de 0,05 ; pour un client, elle change de 0,77. Une liste de « clients à rappeler » construite sur ces prédictions serait **fausse sans que rien ne le signale**.

Un deuxième scénario, plus lent et plus réaliste, est la **dérive** : le comportement des clients change (ici, 40 jours de récence de plus et 0,4 point de satisfaction de moins). Le modèle n'est pas cassé, mais le monde n'est plus celui de son entraînement : la probabilité moyenne prédite monte de 0,126 à 0,168, et la part de clients au-dessus du seuil de 0,3 passe de 13,9 % à 19,8 %. Savoir **si c'est le monde qui a changé ou le modèle qui se trompe** demande de la supervision (chapitre 4).

> ⚠️ **Le pire échec est celui qu'on ne voit pas.** Un plantage se corrige le jour même ; une dégradation silencieuse peut durer des mois. Les outils de ce volume (contrôle des entrées, tests, supervision, détection de dérive) servent d'abord à transformer les échecs silencieux en échecs **bruyants**.

## Ce que les volumes précédents vous donnent

Ce volume suppose que vous avez lu les volumes I à III, ou que vous en avez le bagage. Chaque fois qu'un résultat est utilisé, nous le citons (« volume III, section 2.4 ») pour que vous puissiez aller le relire.

| Ce que vous devez maîtriser | Où le revoir |
|---|---|
| Descente de gradient (au cœur des réseaux de neurones) | volume I, section 1.3 (en particulier 1.3.3) |
| pandas, pour manipuler un tableau | volume I, section 4.4 |
| SQL : requêtes, jointures, agrégations | volume I, section 5.2 |
| Git, ligne de commande, environnements virtuels | volume I, sections 6.1 et 6.3 |
| Régression logistique | volume II, section 2.2 |
| Prévision d'une série temporelle | volume II, section 4.3 |
| Formulation d'un problème, découpage des données, fuite d'information | volume III, section 1.1 |
| Validation croisée | volume III, section 1.2 |
| Gradient boosting | volume III, section 2.4 |
| Classes déséquilibrées | volume III, section 4.3 |
| Métriques, calibration, interprétabilité | volume III, sections 5.1, 5.2 et 5.3 |

## La carte du volume

Le volume contient **cinq chapitres principaux** et **deux chapitres complémentaires** facultatifs. Chaque chapitre a son pendant dans le **cahier d'exercices et d'applications**.

```text
  1. DEEP LEARNING            2. LANGAGE
  réseaux, convolutions,      jetons, plongements,
  récurrence                  transformers, grands modèles
        └───────────┬───────────┘
                    ▼
  3. CALCUL DISTRIBUÉ    4. MLOPS               5. INGÉNIERIE DES DONNÉES
  quand les données      mettre en service,     fabriquer des données fiables
  ne tiennent plus       surveiller, remplacer  en amont de tout modèle
                    ▼
  ➕ 6. Plateformes cloud     ➕ 7. Applications de démonstration
  Cahier : projet du volume (déployer un modèle, avec pipeline et supervision)
```

| Chapitre | Question centrale | Vous saurez… |
|---|---|---|
| **1. Deep learning** | Comment un réseau apprend-il, et pourquoi la convolution et la récurrence aident-elles ? | calculer une rétropropagation, entraîner un petit réseau, lire une image ou une séquence |
| **2. NLP et modèles de langage** | Comment transformer du texte en nombres, et que fait vraiment un grand modèle de langage ? | découper en jetons, utiliser des plongements, expliquer l'attention, juger un modèle de langage |
| **3. Big data et calcul distribué** | Que change le fait que les données ne tiennent plus sur une machine ? | raisonner en partitions, écrire une requête Spark, repérer les opérations coûteuses |
| **4. MLOps** | Comment passe-t-on d'un modèle à un service fiable et surveillé ? | construire un pipeline reproductible, exposer un modèle, le surveiller, détecter une dérive |
| **5. Ingénierie des données** | Comment fabriquer des données fiables à partir de sources qui ne le sont pas ? | concevoir un ETL, mesurer la qualité, réconcilier des sources |
| ➕ **6. Plateformes cloud** | Que change le cloud, et que coûte-t-il ? | situer les grandes familles de services et leurs risques |
| ➕ **7. Applications de démonstration** | Comment faire manipuler un modèle par quelqu'un qui ne code pas ? | construire un prototype d'application |
| **Cahier : projet** | Peut-on tout assembler ? | déployer un modèle avec un pipeline et une supervision |

> 🧭 **Les chapitres complémentaires.** Les chapitres 6 et 7, ainsi que toutes les sections marquées ➕, sont **facultatifs** : on peut lire les cinq premiers chapitres sans eux. Ils sont là pour celles et ceux qui veulent aller plus loin.

## Six idées qui reviennent dans tout le volume

1. **Un résultat doit pouvoir être refait.** Données versionnées, graines fixées, versions de bibliothèques notées, code exécuté de bout en bout : sans cela, on ne sait pas si un changement vient du modèle, des données ou du hasard (chapitre 4).
2. **Le code doit pouvoir être testé, et tourner sans réseau.** Un programme qui ne s'exécute que sur la machine de son auteur, ou qui télécharge quelque chose en silence au moment de s'exécuter, est fragile. Tous les exemples de ce livre tournent **hors ligne** après une installation unique.
3. **Dire honnêtement ce que font les outils.** Un outil à la mode n'est pas une réponse : nous disons à quoi il sert, ce qu'il coûte, ce qu'il ne fait pas, et quand une solution plus simple suffit.
4. **Commencer petit.** Un modèle simple, un seul fichier, une seule machine : tant que cela suffit, c'est ce qu'il faut. On change d'échelle quand une mesure le justifie, pas parce que c'est possible.
5. **La supervision fait partie du modèle.** Un modèle sans surveillance est un modèle dont on ignore quand il cesse de fonctionner (chapitre 4).
6. **Un modèle de langage s'évalue, il ne s'admire pas.** Il écrit avec aplomb, y compris des erreurs. Face à lui, la rigueur d'évaluation du volume III (jeu de test, référence simple, incertitude) s'applique **davantage**, pas moins (chapitre 2).

## Comment travailler avec ce volume

### Un livre, et son cahier

Ce volume est composé de **deux ouvrages complémentaires** :

- **le livre** (celui que vous lisez) explique les idées : intuition, exemple calculé à la main, démonstration quand elle éclaire, pièges, résumé ;
- **le cahier d'exercices et d'applications** contient tout ce qui se pratique : exercices corrigés, applications guidées, et le projet de fin de volume avec son auto-évaluation.

Le livre renvoie au cahier par une ligne qui termine les sections concernées :

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.

Lisez d'abord la section du livre, puis, pour fixer l'idée, passez au cahier. On peut aussi lire le livre seul : rien d'indispensable à la compréhension n'a été déplacé.

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

Ce n'est pas un livre de programmation : le code n'y apparaît que lorsqu'il aide à comprendre. Dans ce volume, il est un peu plus présent qu'au volume III, parce que, pour **mettre un modèle en service**, une requête Spark, une route d'API ou une commande de déploiement *sont* le sujet : nous les montrons alors en blocs courts, commentés, avec leurs résultats. Les formules, les démonstrations et les algorithmes restent expliqués en mathématiques et en français. Les figures, les simulations et les vérifications numériques sont produites par du code **caché** dans les sources, mais exécuté à chaque construction du livre : **chaque nombre cité est reproductible**. Les versions complètes se trouvent dans le cahier et dans le dépôt.

### Tout s'exécute hors ligne

Après une **installation unique** (le bloc de commandes de la section suivante, qui télécharge aussi quelques petits modèles pré-entraînés), tous les exemples exécutés du livre et du cahier tournent **sans accès au réseau**. Ce n'est pas un détail : c'est la condition pour qu'un résultat reste reproductible dans le temps, quand un site disparaît ou qu'un modèle change de version.

### Des données simulées, un jeu réel, des modèles petits

Les données de la boutique sont **simulées**, comme aux volumes précédents (graines fixes, vérité programmée) : cela permet de savoir ce qu'on aurait dû trouver. Un seul jeu est réel : des chiffres manuscrits (MNIST). Quant aux modèles pré-entraînés, nous n'utilisons que de **petits** modèles, capables de tourner sur un ordinateur ordinaire : cela limite ce qu'on peut leur faire dire, et nous le disons chaque fois.

> ⚠️ **Simulé ne veut pas dire facile.** Un jeu simulé est plus *propre* que la réalité. Les avis de clients du chapitre 2, par exemple, sont assemblés à partir de phrases-types : une méthode très simple les lit presque parfaitement, ce qui serait faux sur de vrais avis.

### Ce qui n'a pas pu être exécuté

Certains outils du volume (Docker, Kubernetes, Airflow, Prefect, dbt, Kafka, Hadoop, TensorFlow, les plateformes cloud) ne peuvent pas tourner dans l'environnement qui a servi à écrire le livre. Nous ne les passons pas sous silence, car un lecteur les rencontrera : leur code est montré dans des blocs explicitement marqués **non exécuté**, et nous l'accompagnons, quand c'est possible, d'un **équivalent minimal exécutable** (par exemple un petit orchestrateur écrit en Python pur, ou un mini-MapReduce) qui montre la même idée. Ce qui n'a pas été vérifié ici est dit comme tel.


# Les données, les modèles et l'environnement du volume

## Les jeux du volume

Dans ce volume, la boutique change d'échelle. Le volume III observait douze mille clients ; ici il faut des **images** à reconnaître, des **avis** à lire, des **millions de lignes** à traiter, des **exports sales** à nettoyer, et un modèle à **mettre en service**. Les jeux sont donc de natures très différentes : un seul est **réel** (des chiffres manuscrits), les autres sont **simulés** avec des graines fixes (script `build/donnees4.py`) : vous obtiendrez exactement les mêmes chiffres que dans le livre.

| Fichier ou source | Contenu | Utilisé surtout dans |
|---|---|---|
| `mnist_sous_ensemble.npz` | **jeu réel** : 12 000 images de chiffres manuscrits (28 × 28 pixels) | chapitre 1 (réseaux, convolutions) |
| `ventes_quotidiennes.csv` | les ventes journalières de la boutique sur trois ans | chapitre 1 (réseaux récurrents) |
| `avis_clients.csv` | des avis de clients en français, avec une note de 1 à 5 | chapitre 2 (langage) |
| `clients_ml.csv` | les 12 000 clients du volume III, avec leur départ à 90 jours | chapitre 4 et projet (mise en production) |
| `sources/*.csv` | des exports « bruts » volontairement sales (commandes, clients, produits) | chapitre 5 (ingénierie des données) |
| générateur `gros_volume` | des millions de transactions, écrites à la demande en format Parquet | chapitre 3 (calcul distribué) |

Chargeons-les et regardons, comme toujours, leur forme et leurs valeurs manquantes :

```text
mnist (apprentissage)   10000 images 28x28
mnist (test)             2000 images
ventes_quotidiennes      1096 lignes,  5 colonnes,     0 valeur(s) manquante(s)
avis_clients             8000 lignes,  6 colonnes,     0 valeur(s) manquante(s)
clients_ml              12000 lignes, 24 colonnes,  6426 valeur(s) manquante(s)
sources/commandes_export        19700 lignes,  6 colonnes
sources/clients_crm              5000 lignes,  6 colonnes
sources/produits_catalogue         48 lignes,  4 colonnes
sources/produits_fournisseur       40 lignes,  3 colonnes
sources/verite_clients           5000 lignes,  2 colonnes
sources/verite_produits            40 lignes,  2 colonnes
```

Les 6 426 valeurs manquantes de `clients_ml.csv` sont **voulues** (nous y revenons plus bas) ; tous les autres jeux sont complets.

## Des chiffres manuscrits : `mnist_sous_ensemble.npz`

Le chapitre 1 a besoin d'**images** : c'est pour elles qu'ont été inventés les réseaux convolutifs. Nous utilisons **MNIST**, un classique réel : des chiffres de 0 à 9 écrits à la main, numérisés en 28 × 28 pixels en niveaux de gris (chaque pixel est un entier de 0, le fond, à 255, l'encre). Il a été constitué par Yann LeCun, Corinna Cortes et Christopher Burges ; nous le récupérons via OpenML, qui l'indique sous la licence « Public » (à vérifier avant tout usage commercial). Pour que les entraînements tiennent dans le temps d'un exemple de livre, nous n'en gardons qu'un **sous-ensemble** tiré au hasard, de façon stratifiée et à graine fixe : 10 000 images pour l'apprentissage et 2 000 pour le test. Le fichier, d'environ 2 Mo, est fourni ; le script `build/telecharger_mnist.py` montre comment il a été fabriqué.


![Deux exemples de chaque chiffre de MNIST, pris dans le jeu d'apprentissage. Chaque image fait 28 × 28 pixels ; les écritures varient beaucoup d'une personne à l'autre.](figures/ch00-mnist.png)

Les dix classes sont à peu près équilibrées : de 902 images pour le 5 à 1 125 pour le 1 dans le jeu d'apprentissage (de 180 à 225 dans le jeu de test). Seulement **19,2 % des pixels sont non nuls** : une image est surtout du fond, avec un pixel moyen de 33,4 sur 255. Cette régularité sera utile au chapitre 1.

## Les ventes quotidiennes : `ventes_quotidiennes.csv`

Pour parler de **séquences**, le chapitre 1 reprend les ventes de la boutique, cette fois **jour par jour**, du 1er janvier 2023 au 31 décembre 2025 (1 096 jours : 2024 est bissextile). La série mélange les effets qu'on s'attend à trouver : une croissance régulière, un rythme **hebdomadaire**, un renforcement en fin d'année, des **promotions** ponctuelles et du bruit.

| Colonne | Signification |
|---|---|
| `date` | jour, au format `AAAA-MM-JJ` |
| `ventes` | chiffre d'affaires du jour, en € |
| `promo` | 1 s'il y avait une promotion ce jour-là |
| `jour_semaine` | 0 pour lundi, 6 pour dimanche |
| `mois` | numéro du mois |


Les ventes valent en moyenne 154,1 € par jour (de 67,2 € à 356,2 €). Le samedi (jour 5) est le jour fort, avec 224,0 € en moyenne, contre 115,8 € le lundi. La moyenne annuelle passe de 135,3 € en 2023 à 153,4 € en 2024 puis 173,5 € en 2025. Décembre est environ un cinquième plus fort que les autres mois (182,6 € contre 151,4 €), et les 7 % de jours en promotion vendent en moyenne 187,4 € contre 151,5 €. Ce sont ces structures qu'un réseau récurrent devra apprendre.

## Les avis des clients : `avis_clients.csv`

Le chapitre 2 travaille sur du **texte** : huit mille avis de clients, en français, chacun avec une note de 1 à 5, le sujet principal (livraison, qualité, prix, service, emballage), la catégorie du produit (A à D) et le canal d'achat. Ces avis sont **simulés** : le texte a été fabriqué en assemblant des phrases-types, avec des fautes de frappe, quelques emojis, des avis très courts (« RAS », « Top !! »), des avis en anglais, des phrases à **négation** (« Rapide, la livraison ? Pas vraiment. ») et environ 8 % de désaccords entre le ton du texte et la note.


Les notes sont majoritairement bonnes (5 498 notes de 4 ou 5 sur 8 000) ; 433 avis (5,4 %) sont en anglais, 319 comptent moins de trois mots, et 2 353 contiennent une phrase à négation. Un avis fait 11 mots en médiane (32 au maximum).

> ⚠️ **Ce corpus est plus facile qu'un vrai corpus, et il faut le dire.** Parce que le texte est assemblé à partir d'un petit nombre de phrases-types, des méthodes très simples le lisent presque parfaitement. Une régression logistique sur des fréquences de mots et de paires de mots (TF-IDF, section 2.1) distingue les avis positifs (note 4 ou 5) des négatifs (note 1 ou 2) avec une exactitude de **0,942** sur des avis mis de côté. Ce chiffre sera la **référence** du chapitre 2 : un modèle plus sophistiqué doit la battre pour justifier son coût. Contre-intuitivement, la référence ne fait pas moins bien sur les phrases niées (0,955 sur 582 avis) ou sur les avis en anglais (0,957 sur 94 avis) : ces phrases sont elles aussi répétées d'un avis à l'autre, donc mémorisables. Sur de vrais avis, l'écart serait bien plus grand ; le chapitre 2 le rappellera.

## Les clients : `clients_ml.csv`

Pour la mise en production (chapitre 4 et projet du cahier), nous reprenons **tels quels** les 12 000 clients du volume III : le fichier est une copie de celui de ce volume (même graine, mêmes colonnes), pour que ce livre se lise sans lui. Il contient 24 colonnes : un identifiant, **19 variables d'entrée** (comportement d'achat, satisfaction, support, âge, ville, canal…), trois colonnes de résultat et une colonne piégée. La cible à prédire est `churn_90j` (1 si le client ne commande plus dans les 90 jours suivants), qui vaut 1 pour 14 % des clients.


> ⚠️ **Colonnes à exclure des variables d'entrée.** Quatre colonnes ne sont **pas** des variables d'entrée : `id_client` (un identifiant), `depense_6m` (une autre cible), `segment_vrai` (la classe latente qui a servi à fabriquer les données : elle n'existe pas dans la vie réelle) et `commandes_apres_cible` (le nombre de commandes **après** la date de prédiction : c'est la fuite d'information étudiée au volume III, section 1.1, qui rendrait un modèle impossible à utiliser en production, puisque cette information n'existe pas encore au moment de prédire). Les quatre colonnes manquantes (`appareil`, `panier_moyen`, `satisfaction_moy`, `delai_livraison_moy`) comptent de 1 434 à 1 829 valeurs absentes : un service de production doit savoir les traiter.

## Les exports sales : `sources/`

Le chapitre 5 apprend à **fabriquer un jeu propre à partir de sources qui ne le sont pas**. Nous fournissons donc, dans `donnees/sources/`, trois exports « bruts » (les commandes, le fichier client d'un CRM, et les produits vus par le catalogue interne et par un fournisseur) et deux fichiers de **vérité** qui permettent d'évaluer une réconciliation. Les défauts sont **programmés**, pour qu'on puisse vérifier qu'on les a tous trouvés :

| Fichier | Lignes | Défauts programmés |
|---|---|---|
| `commandes_export.csv` | 19 700 | doublons, trois formats de date, prix avec virgule décimale, quantités manquantes ou négatives, clients inconnus |
| `clients_crm.csv` | 5 000 | une même personne saisie plusieurs fois (courriel en majuscules, ville mal écrite) |
| `produits_catalogue.csv` | 48 | produits de référence, avec leur identifiant interne |
| `produits_fournisseur.csv` | 40 | les mêmes produits, avec une autre référence et un autre libellé |
| `verite_clients.csv`, `verite_produits.csv` | 5 000 ; 40 | la correspondance exacte, **à ne consulter que pour évaluer** |


Concrètement : sur 19 700 lignes de commandes, il n'y a que 18 000 identifiants distincts (1 700 lignes en trop), dont 1 524 lignes strictement identiques à une autre ; 286 quantités manquent et 226 sont négatives ; 359 commandes portent sur un client inconnu ; 5 824 prix s'écrivent avec une virgule ; 5 897 dates sont au format `jj/mm/aaaa` et 2 017 au format `mm-jj-aaaa`. Dans le CRM, 5 000 lignes décrivent en réalité 4 200 personnes ; la même ville s'y écrit de 36 façons, qui se réduisent à 12 une fois la casse et les espaces normalisés. Et le fournisseur ne connaît que 40 des 48 produits du catalogue, avec des libellés qui n'ont pas la même forme (« Céramique bol » pour « Bol en céramique »).

## Un grand volume de transactions : `gros_volume`

Le chapitre 3 a besoin de données qui **ne tiennent pas confortablement** dans une session pandas. Plutôt que de stocker des centaines de mégaoctets dans le dépôt, le script fournit une fonction, `donnees4.gros_volume(n)`, qui **écrit à la demande** `n` transactions (client, produit, magasin, canal, montant, date) en plusieurs fichiers au format **Parquet**, avec une graine fixe : les mêmes chiffres à chaque exécution, et rien de volumineux dans le dépôt. Pour 5 millions de lignes :


Les 5 millions de lignes se répartissent en 8 fichiers de 625 000 lignes et occupent 71 Mo sur disque (le Parquet est un format colonnaire compressé) ; un seul de ces fichiers, chargé dans pandas, occupe déjà 41 Mo en mémoire. Les chiffres du chapitre 3 sont modestes à l'échelle d'une entreprise réelle : ils suffisent à montrer les mécanismes, pas à reproduire les difficultés d'un cluster.

## Les modèles pré-entraînés

Trois exemples de ce volume utilisent des modèles **déjà entraînés** par d'autres. Ils sont téléchargés **une seule fois**, avec une **révision figée**, par le script `build/telecharger_modeles.py`, dans un dossier `modeles/` qui n'est pas versionné ; ensuite, le livre s'exécute **hors ligne**.

| Modèle | Rôle | Paramètres | Disque | Licence | Chapitre |
|---|---|---|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | plongements de phrases (vecteurs de dimension 384), langues multiples dont le français | 117,7 M | 500 Mo | Apache-2.0 | 2 |
| `SmolLM2-135M-Instruct` | petit modèle de langage conversationnel (anglais) | 134,5 M | 272 Mo | Apache-2.0 | 2 |
| ResNet-18 (poids ImageNet) | reconnaissance d'images, pour l'apprentissage par transfert | 11,7 M | 47 Mo | code BSD-3 ; poids entraînés sur ImageNet (conditions d'usage à vérifier pour un emploi commercial) | 1 (facultatif) |


> ⚠️ **Pourquoi des modèles si petits, et ce que cela change.** Les modèles de langage « de pointe » ont des centaines de milliards de paramètres et ne tournent pas sur un ordinateur ordinaire. Le seul modèle de langage génératif que nous pouvons exécuter ici, SmolLM2, en a 134,5 millions, soit des milliers de fois moins que les plus grands, et il a été entraîné pour l'**anglais** : il répond souvent en anglais à une consigne en français, et ses réponses sont approximatives. Nous l'utilisons pour montrer des **mécanismes** (découpage en jetons, génération pas à pas, effet des réglages), jamais pour juger de ce que savent faire les grands modèles. Une phrase comme « La livraison a été très rapide. » se découpe en 13 jetons avec son vocabulaire de 49 152 entrées.

L'exécution hors ligne est imposée par quatre variables d'environnement (`HF_HOME` et `TORCH_HOME` pour l'emplacement des modèles, `HF_HUB_OFFLINE=1` et `TRANSFORMERS_OFFLINE=1` pour interdire tout accès au réseau) que le `Makefile` du volume pose pour vous : si un modèle manque, le programme s'arrête avec une erreur claire au lieu de le télécharger en silence.

## L'environnement de travail

Ce volume utilise les outils des volumes précédents, plus quelques outils lourds. Voici les commandes d'installation (non exécutées ici : elles installent des paquets et des programmes sur *votre* machine). La version **CPU** de PyTorch est choisie exprès : la version par défaut de PyPI tire plusieurs gigaoctets de bibliothèques pour cartes graphiques, inutiles ici. Les paquets numériques de base sont **figés** aux versions qui ont produit les sorties du livre.

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy==2.5.3 pandas==3.0.6 scipy scikit-learn==1.9.1 matplotlib
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
pip install transformers sentence-transformers pyspark duckdb pyarrow fastapi uvicorn httpx mlflow streamlit
pip install onnx onnxruntime beautifulsoup4 requests rapidfuzz pytesseract
sudo apt-get install default-jre-headless tesseract-ocr tesseract-ocr-fra    # Java pour Spark, OCR avec le français
python build/telecharger_modeles.py     # une fois : environ 780 Mo ; ensuite, tout s'exécute hors ligne
```


| Bibliothèque | Version utilisée | Pour quoi faire | Chapitres |
|---|---|---|---|
| `torch`, `torchvision` | 2.14.1 (CPU), 0.29.1 | réseaux de neurones, dérivation automatique | 1, 2 |
| `transformers` | 5.18.0 | modèles de langage, découpage en jetons | 2 |
| `sentence-transformers` | 6.1.0 | plongements de phrases | 2 |
| `pyspark` (+ Java) | 4.2.0 | calcul distribué, en mode local | 3 |
| `duckdb`, `pyarrow` | 1.5.6, 25.0.1 | requêtes SQL sur fichiers, format Parquet | 3, 5 |
| `fastapi` | 0.142.2 | mise à disposition d'un modèle par une API | 4 |
| `mlflow` | 3.16.1 | suivi d'expériences | 4 (facultatif) |
| `onnxruntime` | 1.30.0 | exécuter un modèle exporté | 4 |
| `rapidfuzz`, `beautifulsoup4` (et `requests`) | 3.14.6, 4.15.0 | réconciliation, collecte de données | 5 |
| `streamlit` | 1.65.0 | applications de démonstration | 7 (facultatif) |
| `pytesseract` (+ Tesseract) | 0.3.13 | reconnaissance de caractères (OCR) | 1 (facultatif) |
| `scikit-learn`, `pandas`, `numpy` | 1.9.1, 3.0.6, 2.5.3 | les bases des volumes précédents | tous |

Python 3.13 a produit les sorties de ce livre.

> 🧭 **Ce qui ne tourne pas ici.** Certains outils du volume ne peuvent pas s'exécuter dans l'environnement qui a servi à écrire le livre : **Docker** et **Kubernetes** (pas de conteneurs), **Airflow**, **Prefect** et **dbt** (serveurs et orchestrateurs lourds), **DVC**, **Kafka** et **Hadoop** (services à installer), **TensorFlow/Keras**, et les **plateformes cloud** (AWS, Azure, GCP : pas de compte). Leur code est montré dans des blocs marqués *non exécuté* ; chaque fois que c'est possible, nous l'accompagnons d'un **équivalent minimal exécutable** (un mini-orchestrateur en Python, un mini-MapReduce, un serveur HTTP local) qui montre la même idée.

> ⚠️ **Les résultats d'un réseau de neurones varient légèrement.** L'entraînement d'un réseau repose sur des initialisations aléatoires et sur des calculs parallèles dont l'ordre peut changer d'une version de bibliothèque à l'autre. Nous fixons toujours les graines, mais votre dernière décimale peut différer de celle du livre ; une conclusion qui changerait avec une version ne serait pas une conclusion. Nous ne citons jamais de durée en secondes : elles dépendent de la machine.

> 🧭 **Prêt ?** Au chapitre 1, nous commençons par les réseaux de neurones : une idée simple (composer des fonctions et corriger leurs erreurs par la règle de la chaîne), qui devient puissante parce qu'on peut la répéter des millions de fois.
