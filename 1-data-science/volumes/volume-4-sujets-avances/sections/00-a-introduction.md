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

```python hide
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

d = pd.read_csv("donnees/clients_ml.csv")
exclus = ["id_client", "depense_6m", "segment_vrai", "commandes_apres_cible", "churn_90j"]
X, y = d.drop(columns=exclus), d["churn_90j"]
for c in ["ville", "canal_acquisition", "appareil", "categorie_preferee"]:
    X[c] = X[c].astype("category")
Xa, Xt, ya, yt = train_test_split(X, y, train_size=9000, test_size=3000, random_state=0, stratify=y)
m = HistGradientBoostingClassifier(random_state=0, categorical_features="from_dtype").fit(Xa, ya)
p0 = m.predict_proba(Xt)[:, 1]
print("base      AUC %.3f  proba moy %.3f  taux reel %.3f  montant moyen %.1f"
      % (roc_auc_score(yt, p0), p0.mean(), yt.mean(), Xt.montant_12m.mean()))

Xc = Xt.copy()
Xc[["montant_12m", "panier_moyen"]] *= 100            # euros -> centimes, sans erreur
p1 = m.predict_proba(Xc)[:, 1]
print("centimes  AUC %.3f  proba moy %.3f  montant moyen %.1f  valeurs manquantes ajoutees %d"
      % (roc_auc_score(yt, p1), p1.mean(), Xc.montant_12m.mean(),
         int(Xc.isna().sum().sum() - Xt.isna().sum().sum())))
ch = np.abs(p1 - p0)
print("changement > 0.05 : %d / %d (%.1f %%)  maximum %.3f" % ((ch > .05).sum(), len(ch), 100 * (ch > .05).mean(), ch.max()))

Xd = Xt.copy()
Xd["recence_jours"] += 40
Xd["satisfaction_moy"] -= 0.4
p2 = m.predict_proba(Xd)[:, 1]
print("derive    proba moy %.3f (base %.3f)  part > 0.3 : %.3f -> %.3f"
      % (p2.mean(), p0.mean(), (p0 > .3).mean(), (p2 > .3).mean()))
```
<!--sortie-->
```text
base      AUC 0.900  proba moy 0.126  taux reel 0.140  montant moyen 181.2
centimes  AUC 0.879  proba moy 0.085  montant moyen 18119.1  valeurs manquantes ajoutees 0
changement > 0.05 : 606 / 3000 (20.2 %)  maximum 0.771
derive    proba moy 0.168 (base 0.126)  part > 0.3 : 0.139 -> 0.198
```

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
