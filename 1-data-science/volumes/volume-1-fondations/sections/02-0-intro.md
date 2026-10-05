# Chapitre 2 : Probabilités

> « Le hasard n'est pas le désordre :
> c'est un ordre qui apparaît quand on regarde **assez de fois**. »

Dans le chapitre 1, tous nos nombres étaient connus avec certitude. Mais les données réelles ne le sont jamais : demain, Yasmine vendra peut-être 12 bols, peut-être 25. Un client cliquera ou non sur la publicité. Un paiement sera légitime ou frauduleux. Les **probabilités** sont le langage mathématique de cette incertitude, et la **statistique** (chapitre 3) en est la réciproque : à partir de ce qu'on observe, remonter à ce qui se passe « derrière ».

## Le chemin de ce chapitre

- **2.1 Probabilités et formule de Bayes** : calculer des chances, mettre à jour ses croyances quand on apprend quelque chose. C'est le cœur du raisonnement en incertitude, et il est plus subtil qu'il n'y paraît.
- **2.2 Variables aléatoires et lois usuelles** : donner un « visage » au hasard avec les lois de Bernoulli, binomiale, de Poisson, uniforme, exponentielle et normale, et savoir laquelle choisir.
- **2.3 Espérance, variance, covariance** : résumer une loi par quelques nombres, et mesurer comment deux variables bougent ensemble.
- **2.4 Loi des grands nombres et théorème central limite** : les deux résultats qui rendent la statistique possible. Pourquoi une moyenne sur beaucoup d'observations devient fiable, et pourquoi la courbe en cloche est partout.
- ➕ **Pour aller plus loin** : la théorie de la mesure (ce que « probabilité » veut vraiment dire) et les processus stochastiques (le hasard qui évolue dans le temps).
- **2.7 Exercices corrigés**.

> 💡 **Deux manières de voir une probabilité.**
> - **Fréquentiste** : $P(\text{pile})=0{,}5$ signifie que, sur un très grand nombre de lancers, environ la moitié donne pile.
> - **Bayésienne** : $P(\text{la livraison arrivera demain})=0{,}8$ exprime un **degré de confiance**, même pour un événement qui n'arrivera qu'une fois.
>
> Les règles de calcul sont les mêmes dans les deux cas. Nous utiliserons les deux interprétations selon les situations.

> 🛠️ **Notre outil : la simulation.** Beaucoup de résultats de ce chapitre se démontrent. Mais on peut aussi **les voir** en faisant « jouer » l'ordinateur des milliers de fois. Nous utiliserons systématiquement les deux : la démonstration pour *comprendre pourquoi*, la simulation pour *y croire*. Avec NumPy, le générateur aléatoire s'obtient par `rng = np.random.default_rng(graine)`. La **graine** (*seed*) fixe la suite de nombres tirés : avec la même graine, vous obtiendrez exactement les mêmes résultats que dans ce livre.
