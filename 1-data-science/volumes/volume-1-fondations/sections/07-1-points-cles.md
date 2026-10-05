# Points clés

> « On ne sait vraiment une chose que lorsqu'on peut l'expliquer à quelqu'un d'autre sans regarder ses notes. »

Ce dernier chapitre court **fixe l'essentiel** de chaque chapitre en quelques lignes, pour pouvoir y revenir. La vérification, elle, se fait dans le cahier : un projet de bout en bout et trente questions d'auto-évaluation avec leurs réponses.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|--|----------|
| **1. Mathématiques** | Un vecteur est une liste de nombres *et* une flèche ; une matrice **transforme** l'espace. Les valeurs propres disent de combien une direction est étirée, la SVD en donne la meilleure approximation. La dérivée mesure un taux de variation, le **gradient** pointe vers la plus forte montée : on **descend** dans l'opposé pour optimiser. Les ordinateurs calculent avec des approximations (`0,1 + 0,2 ≠ 0,3`) : on compare avec une tolérance. |
| **2. Probabilités** | Une probabilité mesure l'incertitude ; la **formule de Bayes** met à jour une croyance quand on observe un fait (et une alerte rare est souvent une fausse alerte). Les **lois** (Bernoulli, binomiale, Poisson, normale…) sont des modèles ; l'espérance et la variance les résument. La **loi des grands nombres** dit que la moyenne converge ; le **théorème central limite** dit comment elle fluctue (en $\sigma/\sqrt n$). |
| **3. Statistique** | **Dessiner avant de calculer.** Un estimateur se juge à son biais et à sa variance. Un **intervalle de confiance** quantifie l'incertitude ; une **p-valeur** n'est *pas* la probabilité que l'hypothèse soit vraie ; « significatif » n'est pas « important ». Tester plusieurs fois impose de **corriger** (Bonferroni, Holm, Benjamini-Hochberg). Le bootstrap et les tests de permutation fonctionnent sans hypothèse de loi. |
| **4. Programmation** | Python pour tout faire, R pour comparer. Une **bonne structure de données** (dictionnaire, ensemble) vaut mieux qu'un calcul plus rapide. **Vectorisez** avec NumPy et pandas au lieu de boucler. Un graphique répond à **une question** et ne ment pas (axes honnêtes). Un test automatique est un filet de sécurité. |
| **5. SQL** | Une base **relationnelle** sépare l'information en tables reliées par des clés. `WHERE` filtre les lignes, `HAVING` filtre les groupes. `LEFT JOIN` garde les lignes sans correspondance, `NULL` se teste avec `IS NULL`. Les **fonctions fenêtres** calculent sans écraser les lignes ; les **CTE** donnent un nom à chaque étape. Normaliser évite la redondance et les incohérences. |
| **6. Outils** | **Git** garde l'historique et permet d'essayer sans risque (branches). Un **notebook** mélange code et texte, mais cache un état : *Restart & Run All* avant de partager. La **ligne de commande** assemble de petits outils ; un **environnement virtuel** et un `requirements.txt` rendent l'analyse reproductible. |
| **Projet (cahier)** | Le cycle complet : **question → contrôle des données → description → comparaison ou liaison rigoureuse → conclusion prudente → reproductibilité**. |

## Trois idées qui traversent tout le volume

1. **Les données varient** : un chiffre calculé sur un échantillon est une estimation, jamais la vérité (chapitres 2 et 3).
2. **Un calcul juste n'est pas une conclusion juste** : il faut vérifier les hypothèses, dessiner, contrôler les données, distinguer association et causalité (chapitres 3 à 5 et projet).
3. **Ce qui n'est pas reproductible n'existe pas** : graines fixées, code versionné, environnement décrit (chapitres 4 à 6).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : le projet du volume (une étude complète de la boutique, de la question au rapport) et les trente questions d'auto-évaluation avec leur corrigé et leur grille.

## Et maintenant ?

Le volume I vous a donné le **socle**. Il ne contient volontairement aucun modèle « à la mode » : ceux-ci demandent justement les bases que vous venez d'acquérir. Dans le **volume II : Modélisation statistique**, vous apprendrez à **modéliser** : la régression linéaire (la droite des moindres carrés du projet du cahier, généralisée à plusieurs variables), les modèles linéaires généralisés, les séries temporelles (la saisonnalité des ventes, enfin traitée proprement), l'analyse de survie et la statistique bayésienne.

> 💡 **Un conseil pour la suite.** Ne passez pas au volume II en vous reprochant de ne pas tout retenir du volume I : personne ne retient tout. Retenez **où chercher**. Gardez ce livre à portée de main, et revenez-y chaque fois qu'une notion (une p-valeur, une jointure, un gradient) revient dans un contexte nouveau. C'est ainsi, en revenant, que les fondations deviennent solides.

> ✅ **À retenir, tout simplement.** La data science est un artisanat : des mathématiques simples, du code propre, beaucoup de bon sens, et la méthode. Vous avez désormais les gestes. Il ne reste qu'à les répéter.
