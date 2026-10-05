# Chapitre 5 : Analyse de survie

> « La question n'est pas seulement *si* l'événement arrivera, mais *quand*, et ce que l'on peut dire des personnes qu'on n'a pas encore vues partir. »

La gérante a une inquiétude que tous les commerçants connaissent : **combien de temps un client reste-t-il fidèle ?** Elle sait que 49 % de ses 2 000 clients ont cessé d'acheter à la fin de 2025. Mais les autres ? Certains sont arrivés en 2019 et sont toujours là ; d'autres se sont inscrits il y a trois mois et n'ont tout simplement pas eu le temps de partir. Peut-on dire qu'ils « ne partiront jamais » ? Bien sûr que non : on ne sait pas encore. C'est un problème très particulier : **une partie de l'information est incomplète, et pourtant elle n'est pas sans valeur**, puisque savoir qu'un client est resté au moins 40 mois est un renseignement précieux.

L'**analyse de survie** (on dit aussi *analyse des durées*) est la branche de la statistique qui traite ce problème. Son nom vient de la médecine (durée de survie d'un patient), mais ses applications dépassent largement l'hôpital : durée de vie d'un client, d'un abonnement, d'une machine, délai avant un remboursement anticipé de crédit, durée d'un chômage, temps avant le premier sinistre d'une assurance…

> 🧭 **Ce que ce chapitre suppose.** Les chapitres 1 à 3 du volume I (surtout : lois de probabilité et loi exponentielle, estimation par maximum de vraisemblance, intervalles de confiance, tests, bootstrap) et le chapitre 2 de ce volume (modèles linéaires généralisés) pour l'idée de « modèle de régression avec une fonction de lien ». Aucune connaissance préalable en analyse de survie n'est nécessaire.

## Le chemin de ce chapitre

- **5.1 Censure et fonctions de survie** : pourquoi la moyenne ne marche pas, ce qu'est la censure, et les trois fonctions (survie, risque instantané, risque cumulé) qui décrivent une durée.
- **5.2 L'estimateur de Kaplan-Meier** : estimer la courbe de survie **sans hypothèse de forme**, avec son intervalle de confiance, et comparer des groupes (test du log-rank).
- **5.3 Le modèle de Cox à risques proportionnels** : une régression pour les durées, le modèle le plus utilisé de la discipline. Comment l'ajuster, l'interpréter, le vérifier.
- **5.4 Modèles de durée paramétriques** : exponentiel, Weibull, log-normal ; extrapoler au-delà des données et calculer la **valeur vie client**.
- ➕ **5.5 Pour aller plus loin : les risques concurrents** : quand plusieurs événements peuvent interrompre la durée et s'excluent mutuellement.
- **Bilan du chapitre.** Les applications guidées et les exercices corrigés sont dans le **cahier** (chapitre 5), auquel renvoient les encadrés 📒 de chaque section.

## Les données de ce chapitre

Nous utilisons le fichier `donnees/clients.csv`, déjà présenté en début de volume : 2 000 clients de la boutique inscrits entre janvier 2019 et juin 2025, observés jusqu'au **31 décembre 2025**. Quatre colonnes comptent ici :

| Colonne | Signification |
|---|---|
| `duree_mois` | durée pendant laquelle le client a été **observé** (en mois) |
| `churn` | **1** si le départ a été observé, **0** si le client était encore là à la fin de l'observation (durée *censurée*) |
| `offre_bienvenue` | 1 si le client a reçu une offre de bienvenue, 0 sinon, **attribuée au hasard** |
| `canal_acquisition`, `age` | canal par lequel le client est arrivé, âge à l'inscription |

> 📦 **Des données simulées.** Comme dans tout le volume, ces données sont **simulées** avec une graine fixe : nous connaissons donc la loi qui les a engendrées. Nous ne la révélerons qu'à la fin du chapitre (section 5.4.7), pour pouvoir vérifier ce que les méthodes retrouvent, et ce qu'elles retrouvent mal. Faites comme si la gérante ne la connaissait pas.

> 🧭 **Les outils.** Les estimateurs importants (Kaplan-Meier, log-rank, vraisemblance de Cox, maximum de vraisemblance paramétrique, incidences cumulées) ont été **écrits à la main** pour s'assurer de comprendre ce qu'ils calculent, puis comparés aux bibliothèques : `statsmodels` (`SurvfuncRight`, `survdiff`, `PHReg`), `lifelines` et le paquet R `survival`, qui est la référence de la discipline. Ces comparaisons ont été exécutées et leurs résultats sont cités dans le texte ; le code complet est dans le **cahier** (applications 5.1 à 5.6) et dans le fichier `build/outils_ch05.py`.
