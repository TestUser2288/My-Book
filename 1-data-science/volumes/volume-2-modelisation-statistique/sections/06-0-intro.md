# Chapitre 6 : Statistique bayésienne et simulation

> « Toute connaissance est une croyance qu'on a promis de réviser à la lumière des faits. »

Dans le volume I, nous avons mesuré l'incertitude avec des **intervalles de confiance** et des **p-valeurs**. Cette façon de faire, dite *fréquentiste*, répond à la question : « *si je refaisais mon étude des milliers de fois, quelle serait la fréquence de telle ou telle erreur de ma méthode ?* » C'est une réponse rigoureuse… mais ce n'est pas celle que Yasmine attend. Yasmine demande plutôt : « *vu ce que j'ai observé, quelle est la probabilité que l'offre de bienvenue fonctionne ?* ». Une **probabilité sur le paramètre lui-même**.

La statistique **bayésienne** répond directement à cette question, en appliquant la formule de Bayes (volume I, section 2.1) non plus à des événements, mais à des **paramètres inconnus**. Elle y ajoute un ingrédient que le fréquentisme refuse : **ce que l'on sait avant de regarder les données** (la loi *a priori*). En contrepartie, elle exige souvent des calculs d'intégrales que personne ne sait faire à la main : c'est là qu'intervient la **simulation** (Monte-Carlo, MCMC), qui est devenue l'outil central de la modélisation moderne, bayésienne ou non.

## Le chemin de ce chapitre

- **6.1 Inférence bayésienne et lois a priori** : la formule de Bayes pour un paramètre, des exemples à la main, les lois conjuguées, le choix de l'a priori, la loi prédictive.
- **6.2 Méthodes de Monte-Carlo** : estimer une espérance ou une probabilité en **simulant**, vitesse de convergence en $1/\sqrt n$, échantillonnage préférentiel, réduction de variance.
- **6.3 MCMC** : quand on ne sait pas simuler directement, on fabrique une **chaîne de Markov** dont la loi limite est celle qu'on veut. Metropolis-Hastings et Gibbs, écrits en quelques lignes de NumPy.
- **6.4 Vérification des modèles bayésiens** : savoir si la chaîne a convergé, si le modèle est plausible, comment comparer deux modèles.
- ➕ **Pour aller plus loin** : la théorie des **valeurs extrêmes** (6.5) et les **copules** (6.6), qui modélisent les événements rares et la dépendance.
- **6.7 Exercices corrigés**.

> 🧭 **Comment lire ce chapitre.** Les sections 6.1 et 6.2 sont indépendantes l'une de l'autre et se lisent bien d'un trait. La section 6.3 suppose 6.1 (pour le sens de la loi *a posteriori*) et 6.2 (pour le sens d'« échantillon simulé »). La section 6.4 suppose 6.3. Les sections ➕ 6.5 et 6.6 demandent seulement le chapitre 2 du volume I (et, pour la simulation par inversion, la section 6.2.4) ; elles peuvent être lues à part.

> 📦 **Les données utilisées.** Principalement `donnees/clients.csv` (2 000 clients de Dar Jasmin, simulés ; voir l'introduction du volume). Nous nous intéressons surtout à `rachat_12m` (le client a-t-il recommandé dans les 12 mois ?), à `offre_bienvenue` (une offre attribuée **au hasard** à la moitié des clients), à `canal_acquisition` et à `nb_commandes_an`. Comme les données sont **simulées**, nous connaîtrons à la fin la vraie valeur de plusieurs paramètres : ce sera l'occasion de vérifier que la méthode les retrouve.

> ⚠️ **Honnêteté sur les outils.** Les bibliothèques bayésiennes professionnelles (PyMC, Stan) **ne sont pas installées** dans l'environnement qui a servi à produire ce livre. Leur code est montré dans la section 6.3.7, marqué « non exécuté ». Tous les algorithmes dont nous donnons les résultats sont **écrits à la main en NumPy** : c'est aussi la meilleure façon de comprendre ce que ces bibliothèques font à votre place.

> 🛠️ **Matériel.** Tout le code est en Python (NumPy, SciPy, pandas, matplotlib, statsmodels). Les graines sont fixées : vous retrouverez les mêmes nombres que dans le livre, à de très légères variations près selon les versions des bibliothèques.
