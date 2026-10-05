# Chapitre 2 : Probabilités

> « Le hasard n'est pas le désordre :
> c'est un ordre qui apparaît quand on regarde **assez de fois**. »

Dans le chapitre 1, tous nos nombres étaient connus avec certitude. Mais les données réelles ne le sont jamais : demain, la gérante vendra peut-être 12 articles, peut-être 25. Un client cliquera ou non sur la publicité. Un paiement sera légitime ou frauduleux. Les **probabilités** sont le langage mathématique de cette incertitude, et la **statistique** (chapitre 3) en est la réciproque : à partir de ce qu'on observe, remonter à ce qui se passe « derrière ».

## Le chemin de ce chapitre

- **2.1 Probabilités et formule de Bayes** : calculer des chances, mettre à jour ses croyances quand on apprend quelque chose. C'est le cœur du raisonnement en incertitude, et il est plus subtil qu'il n'y paraît.
- **2.2 Variables aléatoires et lois usuelles** : donner un « visage » au hasard avec les lois de Bernoulli, binomiale, de Poisson, uniforme, exponentielle et normale, et savoir laquelle choisir.
- **2.3 Espérance, variance, covariance** : résumer une loi par quelques nombres, et mesurer comment deux variables bougent ensemble.
- **2.4 Loi des grands nombres et théorème central limite** : les deux résultats qui rendent la statistique possible. Pourquoi une moyenne sur beaucoup d'observations devient fiable, et pourquoi la courbe en cloche est partout.
- ➕ **Pour aller plus loin** : la théorie de la mesure (ce que « probabilité » veut vraiment dire) et les processus stochastiques (le hasard qui évolue dans le temps).

> 💡 **Deux manières de voir une probabilité.**
> - **Fréquentiste** : $P(\text{pile})=0{,}5$ signifie que, sur un très grand nombre de lancers, environ la moitié donne pile.
> - **Bayésienne** : $P(\text{la livraison arrivera demain})=0{,}8$ exprime un **degré de confiance**, même pour un événement qui n'arrivera qu'une fois.
>
> Les règles de calcul sont les mêmes dans les deux cas. Nous utiliserons les deux interprétations selon les situations.

> 💡 **Voir pour croire : la simulation.** Beaucoup de résultats de ce chapitre se démontrent. Mais on peut aussi **les voir** en faisant « jouer » l'ordinateur des milliers de fois : la démonstration sert à *comprendre pourquoi*, la simulation à *y croire*. Les figures et les ordres de grandeur de ce chapitre viennent de telles simulations, tirées avec une **graine** (*seed*) fixe : avec la même graine, on obtient exactement les mêmes nombres. Le livre en montre les résultats ; le code correspondant est proposé dans le **cahier d'exercices et d'applications**, qui accompagne chaque chapitre.

> 📒 **Pour s'entraîner.** Le chapitre 2 du cahier contient six applications guidées (classer des avis avec Bayes, voir les paradoxes par simulation, dimensionner un échantillon, chaînes de Markov, diversification, dépenses « à zéros ») et dix exercices corrigés. Chaque section de ce chapitre indique en fin de page ce qui s'y rapporte.

```python hide
# Régénère les figures du chapitre (script build/fig_ch02.py) pour qu'elles restent synchronisées avec le texte.
import subprocess, sys
subprocess.run([sys.executable, "build/fig_ch02.py"], check=True)
```
