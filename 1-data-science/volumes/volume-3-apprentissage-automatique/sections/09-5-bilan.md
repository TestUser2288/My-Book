## Bilan du chapitre 9

Vous savez maintenant :

- **formuler** un problème de décision séquentielle comme un **processus de décision markovien** (états, actions, transitions, récompenses, facteur d'actualisation), et expliquer pourquoi la propriété de Markov est un choix de modélisation ;
- **démontrer** les **équations de Bellman** (d'espérance et d'optimalité), calculer à la main quelques itérations de l'**itération de la valeur** et justifier sa convergence par un argument de **contraction** ;
- lire une **politique optimale** dans $Q^*$, et comparer une politique apprise ou calculée à des règles simples avec un **gain moyen simulé** ;
- distinguer le **test A/B**, qui sert à **conclure**, des **bandits**, qui servent à **gagner en apprenant**, et mesurer un **regret** ; mettre en œuvre **ε-glouton**, **UCB** (et comprendre pourquoi ses constantes comptent) et l'**échantillonnage de Thompson** (lien avec l'inférence bayésienne du volume II) ;
- reconnaître l'intérêt d'un **contexte** (bandit contextuel) et les **biais** que crée une allocation adaptative ;
- écrire la règle du **Q-learning** et de **SARSA**, expliquer la différence entre **hors politique** et **sur la politique**, et énoncer les conditions de convergence de **Robbins et Monro** ;
- expliquer pourquoi la table ne suffit plus, ce que changent le **DQN** et les **gradients de politique**, et pourquoi l'apprentissage par renforcement profond est **fragile** ;
- poser les bonnes questions avant de déployer un agent : **la récompense mesure-t-elle ce que l'on veut ? Qui paie le coût de l'exploration ? Existe-t-il un simulateur ?**

Trois idées à emporter. **D'abord, agir et apprendre sont indissociables** : les données dépendent des décisions, donc l'évaluation doit se faire en conditions réelles de décision (le jeu de test mis de côté du chapitre 1 n'existe plus). **Ensuite, explorer a un prix** : c'est lui que mesurent le regret et l'écart entre les stratégies. **Enfin, la récompense est le cahier des charges** : l'algorithme optimise ce qu'on lui demande à la lettre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.6 et exercices 9.1 à 9.12.

Ce chapitre était le dernier des chapitres complémentaires. Le **projet du volume**, dans le cahier, rassemble les chapitres 1 à 5 en un pipeline complet sur un jeu de données réel, du modèle de référence à l'interprétation.
