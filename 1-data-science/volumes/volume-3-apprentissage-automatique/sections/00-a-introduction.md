# Introduction : statistique ou apprentissage automatique ?

> « Un bon modèle n'est pas celui qui explique le mieux le passé, mais celui qui se trompe le moins sur ce qu'il n'a pas encore vu. »

## Là où le volume II nous a laissés

Le volume II vous a appris à **construire et interpréter des modèles** : une droite de régression, un modèle logistique, un modèle de survie, une prévision. La question centrale était : *que disent les données du mécanisme qui les a produites ?* Un coefficient avait un sens, un intervalle de confiance en avait un autre, et les hypothèses du modèle se vérifiaient avec des diagnostics.

Ce volume change légèrement de question. Une gérante de boutique ne veut pas seulement savoir *pourquoi* certains clients s'en vont ; elle veut **repérer, ce mois-ci, ceux qui vont partir**, pour leur écrire avant qu'il ne soit trop tard. Elle ne demande pas un coefficient : elle demande une liste, et une raison de lui faire confiance.

> 💡 **Intuition.** Expliquer, c'est regarder **en arrière** : comprendre ce qui s'est passé. Prédire, c'est regarder **en avant** : annoncer ce qui n'a pas encore eu lieu. Le premier se juge à la qualité de la compréhension, le second à la qualité des annonces *vérifiées sur des cas que le modèle n'a jamais vus*. Les deux démarches utilisent les mêmes mathématiques ; elles ne posent pas la même exigence.

## Expliquer ou prédire ?

### Deux questions sur les mêmes données

Prenons les douze mille clients de la boutique (présentés dans la section suivante) et une question : *le client va-t-il partir dans les 90 jours ?* On peut y répondre de deux manières.

```python hide
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

c = pd.read_csv("donnees/clients_ml.csv")
y = c["churn_90j"]
X = c.drop(columns=["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"])
X = pd.get_dummies(X, columns=["ville", "canal_acquisition", "appareil", "categorie_preferee"], dummy_na=True, dtype=float)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
imp = Xtr.median()
sc = StandardScaler().fit(Xtr.fillna(imp))
lr = LogisticRegression(max_iter=3000).fit(sc.transform(Xtr.fillna(imp)), ytr)
p_lr = lr.predict_proba(sc.transform(Xte.fillna(imp)))[:, 1]
gb = HistGradientBoostingClassifier(random_state=0).fit(Xtr, ytr)
p_gb = gb.predict_proba(Xte)[:, 1]
j = list(X.columns).index("recence_jours")
sd_rec = Xtr["recence_jours"].std()
print("train / test :", len(Xtr), "/", len(Xte))
print("part de départs : train", round(ytr.mean(), 3), "; test", round(yte.mean(), 3))
print("coefficient standardisé de recence_jours :", round(lr.coef_[0][j], 3), "; rapport de cotes par +1 écart-type :", round(float(np.exp(lr.coef_[0][j])), 2),
      "(écart-type =", round(sd_rec, 1), "jours)")
print("rapport de cotes par +30 jours :", round(float(np.exp(lr.coef_[0][j] * 30 / sd_rec)), 2))
print("AUC test logistique :", round(roc_auc_score(yte, p_lr), 3), "; boosting :", round(roc_auc_score(yte, p_gb), 3))
print("AUC apprentissage logistique :", round(roc_auc_score(ytr, lr.predict_proba(sc.transform(Xtr.fillna(imp)))[:, 1]), 3),
      "; boosting :", round(roc_auc_score(ytr, gb.predict_proba(Xtr)[:, 1]), 3))
```
<!--sortie-->
```text
train / test : 9000 / 3000
part de départs : train 0.14 ; test 0.14
coefficient standardisé de recence_jours : 0.663 ; rapport de cotes par +1 écart-type : 1.94 (écart-type = 124.0 jours)
rapport de cotes par +30 jours : 1.17
AUC test logistique : 0.866 ; boosting : 0.898
AUC apprentissage logistique : 0.866 ; boosting : 0.991
```

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
