# Chapitre 7 : ➕ Inférence causale

> « Les données vous disent ce qui *accompagne* quoi. Pour savoir ce qui *provoque* quoi, il faut en plus une idée de la façon dont les données ont été fabriquées. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 6 se lisent et se comprennent sans lui. Mais si vous ne devez retenir qu'un chapitre « de métier » de ce volume, c'est peut-être celui-ci : c'est lui qui transforme un modèle statistique correct en **décision correcte**.

Tout au long des chapitres précédents, nous avons posé des questions de **prédiction** et d'**association** : « les clients d'Réseaux dépensent-ils moins ? », « quel est le lien entre l'âge et le rachat ? ». Les modèles linéaires et généralisés y répondent très bien. Mais la question que se pose réellement la gérante, le plus souvent, est d'un autre genre :

- « Si j'envoie une offre de bienvenue à un client, **va-t-il** davantage racheter ? »
- « Si je lance une campagne publicitaire à Ville C, **les commandes vont-elles** augmenter ? »
- « Si mes clients suivent mon compte Réseaux, **dépensent-ils plus à cause de cela**, ou est-ce simplement que ce sont déjà mes meilleurs clients qui me suivent ? »

Ce sont des questions **causales** : elles portent sur ce qui se passerait si l'on **agissait**. Et la leçon la plus importante de ce chapitre est la suivante : **aucun modèle, même sophistiqué, ne répond à une question causale à partir des seules données. Il faut y ajouter des hypothèses sur la façon dont ces données ont été produites**. Le chapitre vous apprend à les formuler (avec des graphes), à les justifier (avec la randomisation, quand on le peut) et à les exploiter (quand on ne le peut pas).

## Le chemin de ce chapitre

- **7.1 Raisonner en causes** : les résultats potentiels (le « problème fondamental »), pourquoi la **randomisation** résout tout, une vraie expérience sur l'offre de bienvenue, puis les **graphes causaux** (DAG) et leurs trois structures de base (fourche, chaîne, collision), le paradoxe de Simpson, et le critère de la porte dérobée.
- **7.2 Scores de propension** : quand on ne peut pas randomiser mais que l'on observe les raisons du choix : appariement, pondération, estimateur doublement robuste.
- **7.3 Différences de différences** : une campagne lancée dans certaines villes seulement ; comparer l'évolution des villes traitées à celle des villes témoins.
- **7.4 Variables instrumentales** : quand la confusion n'est **pas observée**, un « coup de pouce » aléatoire peut sauver l'analyse ; avec un panorama honnête des limites de toutes ces méthodes.
- **7.5 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** Il repose sur un procédé très particulier : **nous simulons nous-mêmes les données**. Le gros avantage est que nous connaissons la **vraie** valeur de chaque effet, et nous pouvons donc vérifier honnêtement si chaque méthode la retrouve. Dans la vraie vie, ce ne sera jamais le cas : c'est précisément pour cela que le raisonnement causal est difficile. À chaque méthode, nous commencerons donc par faire comme si nous ne connaissions pas la vérité, puis nous la **révélerons**. Gardez bien en tête que cette simulation est une loupe pédagogique, pas une garantie : une méthode qui retrouve la vérité dans une simulation propre n'est pas pour autant infaillible sur des données réelles.

> 📦 **Les données de ce chapitre.**
>
> - `donnees/clients.csv` (2 000 clients, présenté dans l'introduction du volume) : on y trouve la variable `offre_bienvenue`, **attribuée au hasard**. C'est une vraie expérience randomisée (section 7.1.4).
> - `donnees/ch07-observationnel.csv` (4 000 clients) : une version **non randomisée** de la même histoire, où la gérante a choisi à qui envoyer l'offre (section 7.1.9 et 7.2). Le fichier `ch07-observationnel-verite.csv` contient les « résultats potentiels » que personne ne peut observer en pratique ; nous ne l'ouvrirons que pour vérifier.
> - `donnees/ch07-panel-villes.csv` : 20 villes suivies pendant 24 mois autour d'une campagne publicitaire (section 7.3).
> - `donnees/ch07-iv.csv` (5 000 clients) : une étude du lien entre le suivi du compte Réseaux et la dépense (section 7.4).
>
> Les fichiers `ch07-*` sont produits par `build/sim_ch07.py`. Le code de chaque simulation est imprimé dans la section correspondante (7.3 pour le panel de villes, 7.4 pour l'instrument) et exécuté pour vérifier qu'il redonne exactement le fichier ; celui de l'étude observationnelle se trouve dans `build/sim_ch07.py` (fonction `observationnel`).

> 💡 **Une convention de notation.** Dans tout le chapitre, $T$ désigne le **traitement** (ce que l'on décide : 1 = offre reçue, 0 = pas d'offre), $Y$ le **résultat observé** (ce que l'on mesure : dépense, rachat…) et $X$ les **covariables** (ce que l'on sait du client avant le traitement : âge, canal, engagement…). Dans le volume I, les sections 3.3 à 3.5 (intervalles de confiance, tests, tests multiples) sont les prérequis statistiques ; le chapitre 2 de ce volume (section 2.2, régression logistique) est utilisé pour les scores de propension.
