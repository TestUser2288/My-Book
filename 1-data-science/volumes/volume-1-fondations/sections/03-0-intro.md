# Chapitre 3 : Statistique

> « Les probabilités vont de la **cause** vers les **données**.
> La statistique fait le chemin inverse : des **données** vers la cause. »

Au chapitre 2, nous *connaissions* la loi (par exemple « le taux de conversion est 20,5 % ») et nous calculions la probabilité d'observer certaines données. Dans la vie réelle, c'est l'inverse : on **observe** des données (400 commandes) et on veut deviner la loi (« quel est le vrai panier moyen ? Le canal Réseaux est-il vraiment moins rentable que la boutique ? »). C'est le travail de la **statistique**.

## Le chemin de ce chapitre

- **3.1 Statistique descriptive** : résumer et regarder les données (moyenne, médiane, quantiles, graphiques) avant toute chose.
- **3.2 Estimation** : déduire un paramètre inconnu d'un échantillon (méthode des moments, maximum de vraisemblance), et juger la qualité d'un estimateur.
- **3.3 Intervalles de confiance** : ne pas donner un seul chiffre, mais une **fourchette** honnête.
- **3.4 Tests d'hypothèses** : décider, avec un risque maîtrisé, si un effet observé est réel ou dû au hasard (tests de moyenne, de proportion, du khi-deux, A/B).
- **3.5 p-valeurs, puissance et tests multiples** : bien interpréter les résultats, dimensionner une expérience, éviter les faux positifs.
- ➕ **Pour aller plus loin** : les sondages (comment échantillonner), et les méthodes non paramétriques (quand on ne veut pas supposer de loi).
- **Bilan du chapitre**, puis, dans le **cahier d'exercices**, des applications guidées et des exercices corrigés.

> 💡 **Le fil conducteur : un jeu de 400 commandes.** Tout au long du chapitre nous travaillons sur un même tableau de 400 commandes de la boutique (canal, montant, délai de livraison, satisfaction), fourni dans `donnees/commandes.csv`. Il est **simulé** (graine fixe) pour que vous puissiez reproduire chaque calcul, et vous verrez qu'on y retrouve des phénomènes tout à fait réalistes : montants asymétriques, différences entre canaux, lien entre délai et satisfaction.

> 🧭 **Peu de code dans ce chapitre.** Les formules, les démonstrations et les exemples calculés à la main portent le contenu ; les résultats chiffrés viennent de calculs réalisés sur le jeu de données (reproductibles, fournis avec le livre). Le code n'apparaît que lorsqu'un appel court est instructif : nous utilisons `pandas` pour les tableaux (étudié en détail à la section 4.4) et `scipy.stats` pour les tests. Les simulations complètes et les applications guidées sont dans le **cahier d'exercices**.
