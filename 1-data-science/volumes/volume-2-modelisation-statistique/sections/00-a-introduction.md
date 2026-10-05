# Introduction : de la description à la modélisation

> « Tous les modèles sont faux, mais certains sont utiles. »
> *George Box*

## Là où le volume I nous a laissés

Le volume I vous a donné les gestes de base : **calculer** (mathématiques), **raisonner sous incertitude** (probabilités), **tirer des conclusions honnêtes d'un échantillon** (statistique), **coder** (Python, R), **interroger des données** (SQL) et **travailler proprement** (Git, notebooks, projet reproductible).

À la fin de ce volume, vous saviez répondre à des questions du type : « Les paniers Réseaux sont-ils plus petits que ceux de la boutique ? » (un test de Welch), ou « Chaque jour de retard fait-il baisser la satisfaction, et de combien ? » (une pente, avec son intervalle de confiance). Ce sont des questions à **une ou deux variables**.

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

Le volume contient six chapitres principaux, qui forment trois blocs, et trois chapitres complémentaires.

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

                        Projet du volume : une étude de modélisation complète pour la boutique
```

| Chapitre | Question centrale | Vous saurez… |
|---|---|---|
| **1. Régression linéaire** | Comment expliquer une quantité continue par d'autres variables ? | estimer, interpréter, tester et vérifier un modèle linéaire |
| **2. Modèles linéaires généralisés** | Et si la réponse est un oui/non, un comptage, un montant strictement positif ? | choisir une loi et un lien, ajuster et diagnostiquer un GLM |
| **3. Analyse multivariée** | Comment résumer et regrouper des dizaines de variables ? | réduire la dimension (ACP, analyse factorielle) et segmenter (classification) |
| **4. Séries temporelles** | Comment modéliser et prévoir ce qui évolue dans le temps ? | décomposer, ajuster un ARIMA saisonnier et évaluer des prévisions |
| **5. Analyse de survie** | Comment traiter des durées dont certaines ne sont pas terminées ? | estimer des courbes de survie et mesurer l'effet de variables sur le risque |
| **6. Statistique bayésienne** | Comment exprimer l'incertitude sur un paramètre par une loi de probabilité ? | raisonner à la Bayes et écrire un MCMC |
| **Projet** | Peut-on tout assembler ? | mener une étude complète : GLM, séries temporelles, survie |

## Cinq idées qui reviennent dans tout le volume

Avant de commencer, voici cinq idées qui traversent chaque chapitre. Elles valent mieux que n'importe quelle formule.

1. **Un modèle = une partie « signal » + une partie « bruit ».** Chaque chapitre propose une façon différente, mais toujours explicite, de dire quelle part est le signal et à quoi ressemble le bruit.
2. **Estimer, c'est choisir les paramètres qui rendent les données les plus plausibles.** Presque tous les modèles de ce volume (régression, GLM, ARIMA, survie) sont ajustés par **maximum de vraisemblance** (volume I, section 3.2) ; la régression linéaire en est le cas particulier le plus simple, et le bayésien en est le prolongement.
3. **Un modèle s'évalue sur des données qu'il n'a pas vues.** Mesurer la qualité d'un modèle sur les données qui ont servi à l'ajuster est un auto-compliment. Validation hors échantillon, validation croisée, rétro-test pour les séries : le même principe sous trois formes.
4. **Les hypothèses se vérifient.** Chaque modèle suppose quelque chose (linéarité, indépendance, stationnarité, risques proportionnels…). Chaque chapitre contient des **diagnostics**, c'est-à-dire des moyens de regarder si l'hypothèse tient.
5. **Association n'est pas causalité.** Un modèle prédictif décrit comment les variables varient ensemble ; il ne dit pas ce qui arriverait si on intervenait. La différence est subtile et essentielle : elle fait l'objet du chapitre 7, et elle est signalée chaque fois qu'elle compte.

## Comment travailler avec ce volume

Le rythme est celui du volume I : pour chaque notion, une **intuition**, un **exemple minuscule calculé à la main**, la **démonstration** quand elle éclaire, puis l'**application en code** sur des données, suivie de sa sortie réelle. Les encadrés gardent les mêmes pictogrammes :

| Encadré | Rôle |
|---|---|
| 💡 **Intuition** | l'idée en langage courant |
| 📐 **Démonstration** | le raisonnement rigoureux (on peut le sauter à la première lecture) |
| 🛠️ **Application** | une petite étude réelle avec du code |
| ⚠️ **Piège** | l'erreur classique et comment l'éviter |
| 🧪 **Expérience / remarque** | une simulation ou un commentaire |
| ✅ **À retenir** | le résumé de la section |
| 🧭 **Repère** | un guide de lecture, ou une section optionnelle |

Une particularité importante de ce volume : **les données sont simulées**. C'est un choix délibéré. Quand on simule, on connaît la **vérité** (les vrais coefficients, la vraie forme de la saisonnalité…), ce qui permet de vérifier que la méthode la retrouve, ou de comprendre pourquoi elle la retrouve mal. À la fin de chaque étude importante, nous dévoilons ce qui avait été programmé. Dans la vie réelle, on n'a jamais cette chance : c'est précisément pourquoi il faut s'entraîner ici. Quand nous utilisons des données réelles (certains jeux embarqués dans les bibliothèques), nous le disons.

> ⚠️ **Simulé ne veut pas dire facile.** Un jeu simulé est plus *propre* que la réalité : pas de valeurs saisies de travers, pas de variables oubliées par le service de collecte. Lorsque vous appliquerez ces méthodes à de vrais jeux, comptez sur une part de travail supplémentaire pour le nettoyage et la vérification (volume I, projet de clôture, étape 1).
