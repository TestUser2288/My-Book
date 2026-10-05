# Points clés et auto-évaluation

> « On ne sait vraiment une chose que lorsqu'on peut l'expliquer à quelqu'un d'autre sans regarder ses notes. »

Ce dernier chapitre court a deux rôles. Le premier : **fixer l'essentiel** de chaque chapitre en quelques lignes, pour pouvoir y revenir. Le second : vous donner un moyen **honnête** de savoir si le volume a fait son travail, avec trente questions, leurs réponses, et une grille d'auto-évaluation.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|--|----------|
| **1. Mathématiques** | Un vecteur est une liste de nombres *et* une flèche ; une matrice **transforme** l'espace. Les valeurs propres disent de combien une direction est étirée, la SVD en donne la meilleure approximation. La dérivée mesure un taux de variation, le **gradient** pointe vers la plus forte montée : on **descend** dans l'opposé pour optimiser. Les ordinateurs calculent avec des approximations (`0,1 + 0,2 ≠ 0,3`) : on compare avec une tolérance. |
| **2. Probabilités** | Une probabilité mesure l'incertitude ; la **formule de Bayes** met à jour une croyance quand on observe un fait (et une alerte rare est souvent une fausse alerte). Les **lois** (Bernoulli, binomiale, Poisson, normale…) sont des modèles ; l'espérance et la variance les résument. La **loi des grands nombres** dit que la moyenne converge ; le **théorème central limite** dit comment elle fluctue (en $\sigma/\sqrt n$). |
| **3. Statistique** | **Dessiner avant de calculer.** Un estimateur se juge à son biais et à sa variance. Un **intervalle de confiance** quantifie l'incertitude ; une **p-valeur** n'est *pas* la probabilité que l'hypothèse soit vraie ; « significatif » n'est pas « important ». Tester plusieurs fois impose de **corriger** (Bonferroni, Holm, Benjamini-Hochberg). Le bootstrap et les tests de permutation fonctionnent sans hypothèse de loi. |
| **4. Programmation** | Python pour tout faire, R pour comparer. Une **bonne structure de données** (dictionnaire, ensemble) vaut mieux qu'un calcul plus rapide. **Vectorisez** avec NumPy et pandas au lieu de boucler. Un graphique répond à **une question** et ne ment pas (axes honnêtes). Un test automatique est un filet de sécurité. |
| **5. SQL** | Une base **relationnelle** sépare l'information en tables reliées par des clés. `WHERE` filtre les lignes, `HAVING` filtre les groupes. `LEFT JOIN` garde les lignes sans correspondance, `NULL` se teste avec `IS NULL`. Les **fonctions fenêtres** calculent sans écraser les lignes ; les **CTE** donnent un nom à chaque étape. Normaliser évite la redondance et les incohérences. |
| **6. Outils** | **Git** garde l'historique et permet d'essayer sans risque (branches). Un **notebook** mélange code et texte, mais cache un état : *Restart & Run All* avant de partager. La **ligne de commande** assemble de petits outils ; un **environnement virtuel** et un `requirements.txt` rendent l'analyse reproductible. |
| **Projet** | Le cycle complet : **question → contrôle des données → description → comparaison ou liaison rigoureuse → conclusion prudente → reproductibilité**. |

> 💡 **Trois idées qui traversent tout le volume.**
>
> 1. **Les données varient** : un chiffre calculé sur un échantillon est une estimation, jamais la vérité (chapitres 2 et 3).
> 2. **Un calcul juste n'est pas une conclusion juste** : il faut vérifier les hypothèses, dessiner, contrôler les données, distinguer association et causalité (chapitres 3 à 5 et projet).
> 3. **Ce qui n'est pas reproductible n'existe pas** : graines fixées, code versionné, environnement décrit (chapitres 4 à 6).

## Trente questions pour s'auto-évaluer

**Mode d'emploi.** Répondez **à voix haute ou par écrit** avant de regarder le corrigé, en une ou deux phrases. Si vous ne savez pas, notez la section indiquée et allez la relire : ce n'est pas un échec, c'est le but de l'exercice. Vingt-cinq bonnes réponses sur trente signalent un volume bien assimilé.

### Mathématiques (chapitre 1)

1. Que signifie l'égalité $A\mathbf v=\lambda\mathbf v$ ?
2. Dans quelle direction faut-il se déplacer pour **faire diminuer** le plus vite possible une fonction ?
3. Pourquoi `0.1 + 0.2 == 0.3` vaut-il `False` en Python, et comment comparer proprement deux nombres décimaux ?
4. La gérante veut présenter 3 produits choisis parmi 8 dans une vitrine, sans tenir compte de l'ordre. Combien de vitrines possibles ?

### Probabilités (chapitre 2)

5. Une maladie touche 1 % de la population. Un test la détecte dans 90 % des cas, mais donne un faux positif chez 5 % des personnes saines. Vous êtes positif : quelle est la probabilité d'être malade ?
6. Quelle différence entre la loi des grands nombres et le théorème central limite ?
7. Les montants de commandes ont un écart-type de 38 €. Quel est l'écart-type de la **moyenne** de 400 commandes ?
8. Quelle loi pour (a) le nombre de commandes reçues en une heure ; (b) le fait qu'une commande soit retournée ou non ?

### Statistique (chapitre 3)

9. Pourquoi divise-t-on par $n-1$ et non par $n$ pour estimer une variance ?
10. Que signifie « intervalle de confiance à 95 % » ? Que ne signifie-t-il **pas** ?
11. Qu'est-ce qu'une p-valeur ? Citez une mauvaise interprétation fréquente.
12. On réalise 20 tests indépendants au seuil de 5 %, alors qu'**aucun** effet n'existe. Combien de faux positifs attend-on, et quelle est la probabilité d'en obtenir **au moins un** ?
13. Quand préférer la médiane à la moyenne ?
14. Un test donne $p = 10^{-9}$ pour une différence de 0,3 € entre deux paniers moyens. Doit-on s'en réjouir ?

### Programmation (chapitre 4)

15. Pourquoi tester l'appartenance d'un élément est-il bien plus rapide dans un `set` ou un `dict` que dans une `list` de grande taille ?
16. Pourquoi `df["montant"].sum()` est-il préférable à une boucle `for` sur les lignes ?
17. Que renvoie `df.groupby("canal")["montant"].mean()` : quel type, et quel index ?
18. Citez deux manières de rendre un graphique en barres trompeur.
19. Combien de comparaisons, au maximum, la recherche dichotomique effectue-t-elle sur une liste triée d'un million d'éléments ?
20. À quoi sert un test unitaire, et pourquoi vaut-il mieux que « j'ai regardé, ça avait l'air bon » ?

### SQL (chapitre 5)

21. Quelle est la différence entre une clé primaire et une clé étrangère ?
22. Quelle différence entre `WHERE` et `HAVING` ?
23. Vous voulez la liste de **tous** les clients avec leur nombre de commandes, y compris ceux qui n'ont jamais commandé. Quelle jointure ?
24. Pourquoi `WHERE telephone = NULL` ne renvoie-t-il jamais rien, et que faut-il écrire ?
25. En quoi une fonction fenêtre (`OVER`) diffère-t-elle d'un `GROUP BY` ?
26. Pourquoi normaliser une base (jusqu'à la 3FN) ?

### Outils (chapitre 6)

27. Quelle différence entre `git add` et `git commit` ?
28. Pourquoi un notebook peut-il donner des résultats différents selon qui l'exécute, et comment s'en protéger ?
29. À quoi sert un fichier `requirements.txt` ?
30. Quelle commande compte rapidement le nombre de lignes d'un fichier CSV, et pourquoi faut-il en retrancher une ?

## Vérifier les réponses chiffrées

Pour les questions numériques, plutôt que de se fier à sa mémoire, **calculons**. Le code ci-dessous vérifie les réponses des questions 3, 4, 5, 7, 12 et 19.

```python
import math

# Q3 : arithmétique des flottants
print("Q3  0.1 + 0.2 == 0.3 :", 0.1 + 0.2 == 0.3, "| avec tolérance :", math.isclose(0.1 + 0.2, 0.3))

# Q4 : combinaisons
print("Q4  C(8,3) =", math.comb(8, 3))

# Q5 : formule de Bayes
prevalence, sensibilite, faux_positifs = 0.01, 0.90, 0.05
p_positif = sensibilite * prevalence + faux_positifs * (1 - prevalence)
print(f"Q5  P(malade | test positif) = {sensibilite * prevalence / p_positif:.4f}")

# Q7 : écart-type d'une moyenne
print(f"Q7  38 / sqrt(400) = {38 / math.sqrt(400):.2f} €")

# Q12 : tests multiples
print(f"Q12 faux positifs attendus : {20 * 0.05:.0f} ; P(au moins un) = {1 - 0.95 ** 20:.4f}")

# Q19 : recherche dichotomique
print("Q19 comparaisons max pour 1 000 000 éléments :", math.ceil(math.log2(1_000_000 + 1)))
```
<!--sortie-->
```text
Q3  0.1 + 0.2 == 0.3 : False | avec tolérance : True
Q4  C(8,3) = 56
Q5  P(malade | test positif) = 0.1538
Q7  38 / sqrt(400) = 1.90 €
Q12 faux positifs attendus : 1 ; P(au moins un) = 0.6415
Q19 comparaisons max pour 1 000 000 éléments : 20
```

## Corrigé

**1.** $\mathbf v$ est un **vecteur propre** de $A$ : la matrice ne change pas sa direction, elle l'étire (ou le comprime) d'un facteur $\lambda$, la **valeur propre**. (1.1.3)

**2.** Dans la direction **opposée au gradient**, qui pointe vers la plus forte montée. C'est le principe de la descente de gradient. (1.2 et 1.3)

**3.** Les nombres décimaux sont stockés en binaire, et $0{,}1$ n'a pas d'écriture binaire finie : on ne stocke qu'une **approximation**. On compare avec une tolérance (`math.isclose`, `np.isclose`), jamais avec `==`. (1.5)

**4.** $\binom{8}{3}=\dfrac{8!}{3!\,5!}=56$ vitrines. L'ordre ne comptant pas, on divise les $8\times7\times6=336$ arrangements par les $3!=6$ façons de les ranger. (1.6)

**5.** Environ **15,4 %**, loin des 90 % que l'on devine. Sur 1 000 personnes, 10 sont malades (9 détectées) et 990 sont saines (environ 49,5 faux positifs) : seulement $9$ positifs sur $58{,}5$ environ sont vraiment malades. C'est ce qui arrive quand la maladie est rare. (2.1)

**6.** La loi des grands nombres dit que la **moyenne d'échantillon converge** vers l'espérance quand $n$ grandit ; le théorème central limite décrit **comment elle fluctue** autour de celle-ci : approximativement selon une loi normale d'écart-type $\sigma/\sqrt n$, quelle que soit la loi d'origine. (2.4)

**7.** $38/\sqrt{400}=38/20=1{,}9$ € : la moyenne est bien plus stable que chaque commande. C'est la raison pour laquelle on moyenne. (2.4)

**8.** (a) Une loi de **Poisson** (événements rares et indépendants dans un intervalle de temps) ; (b) une loi de **Bernoulli** (deux issues), ou binomiale si l'on compte le nombre de retours sur $n$ commandes. (2.2)

**9.** Parce que l'on mesure les écarts à la moyenne **de l'échantillon**, qui est elle-même ajustée aux données : les écarts sont un peu trop petits. Diviser par $n-1$ corrige ce biais et rend l'estimateur **sans biais**. (3.2)

**10.** La **méthode** produit un intervalle qui contient la vraie valeur dans 95 % des échantillons possibles. Ce n'est **pas** « 95 % de chances que la vraie valeur soit dans cet intervalle-ci » : une fois calculé, l'intervalle contient la vraie valeur ou ne la contient pas. (3.3.2)

**11.** La probabilité d'observer un résultat **au moins aussi extrême** que le nôtre, *si l'hypothèse nulle était vraie*. Mauvaise interprétation fréquente : « c'est la probabilité que l'hypothèse nulle soit vraie ». (3.5.1 et 3.5.2)

**12.** On attend $20\times0{,}05=1$ faux positif, et la probabilité d'au moins un est $1-0{,}95^{20}\approx64\,\%$ : d'où la nécessité de corriger les tests multiples. (3.5.5)

**13.** Quand la distribution est **asymétrique** ou contient des **valeurs extrêmes** (montants, revenus, durées) : la médiane est robuste, la moyenne est tirée par la queue. (3.1.3)

**14.** Pas vraiment : avec assez de données, même une différence minuscule devient « significative ». 0,3 € sur un panier de 60 € n'a **aucune importance pratique**. Il faut toujours regarder la **taille de l'effet** et l'intervalle de confiance, pas seulement la p-valeur. (3.5.3)

**15.** Un `set` ou un `dict` utilise une **table de hachage** : il calcule directement où se trouve l'élément (coût quasi constant). Une liste doit être **parcourue** élément par élément (coût proportionnel à sa taille). (4.3.2 et 4.8)

**16.** La somme vectorisée s'exécute en **code compilé** sur un tableau contigu, sans le surcoût de l'interpréteur Python à chaque ligne : elle est en général beaucoup plus rapide (au moins plusieurs fois, souvent bien davantage selon la taille du tableau), et plus courte à écrire. (4.4 et 4.8)

**17.** Une **Series** pandas dont l'index est le canal (Boutique, Réseaux, Site) et dont les valeurs sont les montants moyens. (4.4)

**18.** Par exemple : **tronquer l'axe vertical** (un écart réel de 2 % peut sembler un rapport de 5 à 1), utiliser un **camembert en 3D** (la perspective déforme les aires) ou un **double axe vertical** (on rend « visible » n'importe quelle corrélation en choisissant les échelles). Une barre doit toujours partir de zéro. (4.5.6)

**19.** **20** comparaisons au plus ($2^{20}=1\,048\,576>10^6$) : chaque comparaison divise l'intervalle de recherche par deux. Chercher dans une liste non triée en demanderait jusqu'à un million. (4.3.5)

**20.** Un test unitaire **vérifie automatiquement** qu'une fonction renvoie le résultat attendu sur des cas connus. Rejoué à chaque modification, il détecte immédiatement une régression ; un coup d'œil, lui, oublie les cas limites et ne se rejoue pas. (4.6)

**21.** La **clé primaire** identifie de façon unique chaque ligne d'une table. Une **clé étrangère** est une colonne qui référence la clé primaire d'une autre table : c'est elle qui crée le lien entre les tables. (5.1)

**22.** `WHERE` filtre les **lignes** avant le regroupement ; `HAVING` filtre les **groupes** après l'agrégation (par exemple « les clients avec plus de 5 commandes »). (5.2.4)

**23.** Un **`LEFT JOIN`** de `clients` vers `commandes` : il garde tous les clients, avec `NULL` (ou 0 après `COUNT` sur la colonne de droite) pour ceux qui n'ont pas de commande. Un `INNER JOIN` les ferait disparaître. (5.2.5)

**24.** Parce que `NULL` signifie « inconnu » : comparer quoi que ce soit à `NULL` donne « inconnu », jamais « vrai ». Il faut écrire `WHERE telephone IS NULL`. (5.2.7)

**25.** `GROUP BY` **réduit** plusieurs lignes à une seule par groupe ; une fonction fenêtre **conserve toutes les lignes** et ajoute une colonne calculée sur une « fenêtre » de lignes voisines (classement, cumul, ligne précédente). (5.3.1)

**26.** Pour **éviter la redondance** (la même information écrite à plusieurs endroits) et donc les **anomalies** de mise à jour, d'insertion et de suppression : chaque fait est stocké **une seule fois**. (5.4)

**27.** `git add` **prépare** les modifications (zone d'index) ; `git commit` **enregistre** ce qui a été préparé dans l'historique, avec un message. Cela permet de composer des commits cohérents. (6.1.3)

**28.** Parce que l'on peut exécuter les cellules **dans le désordre** et que le noyau garde en mémoire des variables qui n'existent plus dans le fichier : c'est l'**état caché**. Protection : *Restart & Run All* avant de partager ou d'en tirer un résultat. (6.2.3)

**29.** Il **liste les bibliothèques et leurs versions** nécessaires, pour que n'importe qui puisse recréer le même environnement (`pip install -r requirements.txt`). (6.3.6)

**30.** `wc -l fichier.csv`. Il faut retrancher **1** : la première ligne est l'en-tête (les noms de colonnes), pas une observation. (6.3)

## Votre grille d'auto-évaluation

Pour chaque ligne, cochez mentalement : **je sais l'expliquer** / **je sais le faire** / **à revoir**. Les sections à relire sont indiquées.

| Compétence | Où la retravailler |
|---|---|
| Manipuler des vecteurs et des matrices, interpréter valeurs propres et SVD | 1.1 |
| Dériver, calculer un gradient, faire une descente de gradient | 1.2, 1.3 |
| Calculer avec des probabilités conditionnelles et appliquer Bayes | 2.1 |
| Choisir une loi et en calculer espérance et variance | 2.2, 2.3 |
| Expliquer la loi des grands nombres et le théorème central limite | 2.4 |
| Décrire un jeu de données (position, dispersion, forme) et le tracer | 3.1 |
| Estimer un paramètre, construire et interpréter un intervalle de confiance | 3.2, 3.3 |
| Mener un test, lire une p-valeur, corriger les tests multiples | 3.4, 3.5 |
| Écrire un programme Python avec fonctions, boucles, dictionnaires | 4.1, 4.3 |
| Manipuler un tableau avec pandas (filtrer, regrouper, joindre) | 4.4 |
| Produire un graphique honnête et lisible | 4.5 |
| Écrire des requêtes SQL avec jointures et agrégations | 5.2 |
| Utiliser fonctions fenêtres et CTE | 5.3 |
| Concevoir un schéma normalisé | 5.1, 5.4 |
| Versionner un projet avec Git | 6.1 |
| Utiliser notebooks, ligne de commande et environnements virtuels | 6.2, 6.3 |
| Mener un petit projet de bout en bout | Projet du volume |

## Et maintenant ?

Le volume I vous a donné le **socle**. Il ne contient volontairement aucun modèle « à la mode » : ceux-ci demandent justement les bases que vous venez d'acquérir. Dans le **volume II : Modélisation statistique**, vous apprendrez à **modéliser** : la régression linéaire (la droite des moindres carrés de ce projet, généralisée à plusieurs variables), les modèles linéaires généralisés, les séries temporelles (la saisonnalité de la boutique, enfin traitée proprement), l'analyse de survie et la statistique bayésienne.

> 💡 **Un conseil pour la suite.** Ne passez pas au volume II en vous reprochant de ne pas tout retenir du volume I : personne ne retient tout. Retenez **où chercher**. Gardez ce livre à portée de main, et revenez-y chaque fois qu'une notion (une p-valeur, une jointure, un gradient) revient dans un contexte nouveau. C'est ainsi, en revenant, que les fondations deviennent solides.

> ✅ **À retenir, tout simplement.** La data science est un artisanat : des mathématiques simples, du code propre, beaucoup de bon sens, et la méthode. Vous avez désormais les gestes. Il ne reste qu'à les répéter.
