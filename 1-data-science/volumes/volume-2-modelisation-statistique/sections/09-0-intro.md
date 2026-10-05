# Chapitre 9 : ➕ Statistique spatiale

> « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. »
> — Waldo Tobler, *première loi de la géographie* (1970)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement facultatif** : rien dans les chapitres 1 à 6 ni dans le projet du volume n'en dépend. Il s'adresse à ceux dont les données ont une **position** : des adresses de clients, des points de livraison, des zones géographiques, des capteurs. Si c'est votre cas, vous verrez que presque tout ce que nous avons appris repose sur une hypothèse que l'espace met à mal : l'**indépendance** des observations.

La boutique livre maintenant dans toute une région. La gérante remarque des choses que les tableaux des chapitres précédents ne savent pas dire :

- *« Les délais de livraison longs sont groupés : quand un client d'un quartier attend longtemps, ses voisins aussi. »* Un point isolé ne serait pas un problème ; un **paquet** de retards, c'est un problème de tournée ou de route.
- *« Mes ventes par zone ont l'air de former des îlots : des zones où l'on vend beaucoup, entourées de zones où l'on vend beaucoup. »* Est-ce réel, ou est-ce l'œil qui voit des formes dans le hasard ?
- *« Je voudrais promettre un délai au client avant même d'avoir livré dans son quartier. »* Comment **prédire** une valeur en un endroit où l'on n'a rien mesuré ?
- *« Mes clients du quartier se regroupent-ils vraiment autour de la boutique, ou sont-ils répartis au hasard ? »*

Quatre questions, quatre outils : l'**autocorrélation spatiale**, le **variogramme** et le **krigeage**, les **processus ponctuels**. Les voici, dans l'ordre.

## Le chemin de ce chapitre

- **9.1 Données spatiales et cartes** : les trois grands types de données spatiales, la façon de repérer un point sur la Terre, de calculer une distance **sans se tromper**, et de dessiner une carte honnête sans fond de carte.
- **9.2 Autocorrélation spatiale** : définir « voisin » avec une **matrice de poids**, mesurer la ressemblance entre voisins avec l'**indice de Moran** (démontré, calculé à la main, puis testé par permutations), l'indice de **Geary**, et repérer *où* se trouvent les îlots avec les indices **locaux** (LISA).
- **9.3 Variogramme et krigeage** : décrire comment la ressemblance **décroît avec la distance**, ajuster un modèle (pépite, palier, portée), et **prédire** en un point non mesuré avec une **variance d'erreur** (le krigeage, dérivé avec des multiplicateurs de Lagrange).
- **9.4 Processus ponctuels** : quand ce sont les **positions** qui sont aléatoires ; hasard complet, agrégat ou répulsion ? Test des quadrats, plus proche voisin, fonction K de Ripley, enveloppes de Monte-Carlo.
- **Bilan du chapitre**, puis le **cahier** : applications guidées (le code complet de ce chapitre, pas à pas) et douze exercices corrigés.

> 🧭 **Comment travailler avec ce chapitre.** Aucune bibliothèque de cartographie n'est nécessaire (ni `geopandas`, ni `pykrige`) : tout est écrit avec NumPy, SciPy et matplotlib. C'est volontaire. Calculer soi-même un indice de Moran ou résoudre soi-même un système de krigeage est la meilleure garantie de comprendre ce que font ensuite les bibliothèques spécialisées. En contrepartie, les cartes n'ont **pas de fond de carte** (il faudrait télécharger des tuiles) : ce sont des graphiques de coordonnées, sobres mais honnêtes. Pour garder le livre lisible, les simulations et les tracés sont exécutés « en coulisses » : on y lit les résultats et les figures, et le code complet se trouve dans le cahier, chapitre 9 (applications 9.1 à 9.7).

> 📦 **Les données de ce chapitre.** Les données sont **simulées**, avec des graines fixes, de façon que nous connaissions la vérité et puissions vérifier que les méthodes la retrouvent. Le décor est une **région fictive** : les villes, les zones et les coordonnées sont inventées.
>
> - Une **grille de 12 × 12 zones** fictives (144 zones de 5 km de côté) avec des ventes par habitant qui présentent une autocorrélation spatiale *connue* (fichier `donnees/ch09-zones.csv`), plus une variable de contrôle sans aucune structure spatiale.
> - **200 livraisons** dans un carré de 100 km de côté, avec un délai en jours qui varie de façon continue dans l'espace (fichier `donnees/ch09-livraisons.csv`).
> - Des **semis de points** (adresses de clients), simulés directement dans les sections qui les utilisent.
> - Les **coordonnées de dix villes fictives** (A à J), écrites à la main, et le tableau `donnees/clients.csv` du volume pour les effectifs par ville.
>
> Le générateur du chapitre est dans `build/donnees_ch09.py` ; il est reconstruit pas à pas dans le cahier.
