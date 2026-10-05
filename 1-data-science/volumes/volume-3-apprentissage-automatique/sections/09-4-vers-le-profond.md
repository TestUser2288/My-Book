## 9.4 Du Q-learning à l'apprentissage profond

Cette section est une **lecture** : elle explique ce qui change quand on quitte la table, sans rien exécuter (ni PyTorch ni TensorFlow n'est installé pour ce livre). Les méthodes décrites ici sont celles des grandes réussites médiatiques (jeux vidéo, Go, robots) ; elles sont aussi celles dont il faut le plus se méfier, et nous en profitons pour discuter les précautions d'emploi.

### 9.4.1 Quand la table explose

Le Q-learning stocke une valeur par couple (état, action). Pour le stock d'un seul article, cela représente 15 valeurs. Imaginons maintenant que la gérante gère **dix articles**, chacun avec un stock de 0 à 20 unités : l'état est la liste des dix stocks, et il y a $21^{10}=16\,679\,880\,978\,201$ états, soit près de **17 000 milliards**. Ajoutons le jour de la semaine (7 valeurs) : un nombre de l'ordre de $10^{14}$. Aucune table ne tient en mémoire, et surtout **aucun agent ne peut visiter chaque état** : la plupart des situations ne se rencontreront jamais deux fois.

```python hide
print("états pour dix articles, stocks de 0 à 20 :", 21 ** 10)
print("avec le jour de la semaine :", 7 * 21 ** 10)
```
<!--sortie-->
```text
états pour dix articles, stocks de 0 à 20 : 16679880978201
avec le jour de la semaine : 116759166847407
```

Il faut **généraliser** : estimer la valeur d'une situation jamais vue à partir de situations voisines déjà vues. C'est exactement ce que fait l'apprentissage supervisé (chapitres 1 et 2). On remplace donc la table par une **fonction paramétrée** $Q_\theta(s,a)$ (une régression, un arbre, un réseau de neurones), que l'on ajuste pour qu'elle respecte l'équation de Bellman.

### 9.4.2 Approximer la fonction de valeur : le principe du DQN

L'idée du **DQN** (*deep Q-network*, Mnih et al., 2015) est d'entraîner un réseau de neurones $Q_\theta$ avec la même cible que le Q-learning. Après une transition $(s,a,r,s')$, on cherche à réduire l'erreur
$$L(\theta)=\Big(r+\gamma\max_{a'}Q_{\theta^-}(s',a')-Q_\theta(s,a)\Big)^2.$$
Deux ingrédients rendent l'entraînement praticable :

- le **tampon de rejeu** (*replay buffer*) : on stocke les transitions passées et on entraîne sur des **mini-lots tirés au hasard** dans ce tampon. Sans cela, les exemples successifs sont très corrélés (la journée $t+1$ ressemble à la journée $t$), ce qui viole l'hypothèse « exemples indépendants » de l'apprentissage supervisé (chapitre 1) ;
- le **réseau cible** $\theta^-$ : une copie *figée* du réseau, mise à jour rarement, qui sert à calculer la cible. Sans lui, la cible bouge à chaque pas puisqu'elle dépend des paramètres que l'on est en train de modifier.

```python noexec
# Non exécuté : PyTorch n'est pas installé dans l'environnement de ce livre.
q_reseau, q_cible = ReseauQ(), ReseauQ()                      # deux réseaux de même architecture
for etape in range(n_etapes):
    a = epsilon_glouton(q_reseau, s)                           # on explore parfois
    s2, r, fin = env.pas(a)                                    # l'environnement répond
    tampon.ajouter((s, a, r, s2, fin))                         # on garde la transition en mémoire
    s_b, a_b, r_b, s2_b, fin_b = tampon.echantillon(64)        # mini-lot tiré au hasard
    cible = r_b + gamma * (1 - fin_b) * q_cible(s2_b).max(dim=1).values
    perte = ((q_reseau(s_b).gather(1, a_b) - cible.detach()) ** 2).mean()
    optimiseur.zero_grad(); perte.backward(); optimiseur.step()
    if etape % 1000 == 0: q_cible.load_state_dict(q_reseau.state_dict())   # copie périodique
```

### 9.4.3 Optimiser directement la politique

Une autre famille ne passe pas par $Q$ : elle **paramètre la politique** $\pi_\theta(a\mid s)$ elle-même (par exemple un réseau qui renvoie des probabilités d'actions) et monte le long du gradient de la récompense espérée $J(\theta)$. Le **théorème du gradient de politique** donne l'expression de ce gradient :
$$\nabla_\theta J(\theta)=\mathbb E_{\pi_\theta}\!\Big[\nabla_\theta\ln\pi_\theta(a\mid s)\;Q^{\pi_\theta}(s,a)\Big].$$
L'intuition est simple : **augmenter la probabilité des actions qui ont mené à un bon retour, diminuer celle des autres**. L'algorithme **REINFORCE** estime cette espérance avec des retours observés, au prix d'une variance élevée ; on la réduit en soustrayant une **valeur de référence** (*baseline*) à $Q$. Quand cette référence est elle-même une fonction de valeur apprise, on obtient les méthodes **acteur-critique** : un « acteur » (la politique) et un « critique » (la valeur) apprennent ensemble. Les algorithmes modernes les plus répandus (PPO, SAC) en sont des variantes.

### 9.4.4 Pourquoi l'apprentissage devient instable

Avec une table, la convergence du Q-learning est garantie (9.3.6). Avec une fonction approchée, elle ne l'est plus. Sutton et Barto parlent de la **triade mortelle** (*deadly triad*) : trois ingrédients dont **la combinaison** peut faire diverger l'apprentissage, alors que chacun, isolément, est inoffensif.

1. l'**approximation de fonction** (le réseau), qui fait que mettre à jour un état modifie la valeur d'états voisins ;
2. l'**amorçage** (*bootstrapping*) : la cible dépend de l'estimation elle-même ;
3. l'apprentissage **hors politique** (*off-policy*) : on apprend sur des données produites par une autre politique.

Le tampon de rejeu et le réseau cible du DQN sont des **rustines** destinées à contenir ce risque, pas des garanties. En pratique, l'apprentissage par renforcement profond est connu pour être **sensible** : de petits changements d'hyperparamètres, ou de graine, produisent des résultats très différents, et les comparaisons d'algorithmes nécessitent de nombreuses répétitions (la rigueur expérimentale de la section 1.4 s'applique ici avec une force particulière).

### 9.4.5 Apprendre à partir de données déjà collectées

Une boutique a des **années d'historique** : quelles offres ont été envoyées à quels clients, avec quels résultats. Peut-on apprendre une politique à partir de ce journal, **sans** expérimenter sur de vrais clients ? C'est l'**apprentissage par renforcement hors ligne** (*offline RL*). C'est séduisant et difficile, pour une raison de fond : le journal ne contient que les décisions qui **ont été prises**. Pour une action jamais tentée dans un état donné, aucune donnée ne dit ce qui serait arrivé, et un algorithme naïf aura tendance à **surestimer** précisément ces actions inconnues (il en choisit alors de fausses « bonnes » idées).

Les remèdes sont de deux types : **rester proche de la politique historique** (méthodes dites conservatrices), et **évaluer d'abord, déployer ensuite** : on estime la valeur d'une nouvelle politique à partir des données de l'ancienne par **pondération par l'inverse des probabilités** (volume II, section 7.2), à condition d'avoir enregistré les probabilités avec lesquelles les actions ont été choisies. C'est le même problème que celui de l'inférence causale en données observationnelles (volume II, chapitre 7) : on veut connaître l'effet d'une action que l'on n'a pas toujours faite.

### 9.4.6 La récompense, ou ce que l'on demande vraiment

L'agent ne maximise pas ce que nous **voulons**, mais ce que nous **mesurons**. Si la récompense est mal spécifiée, l'agent trouvera la faille. C'est un phénomène bien documenté, sous des noms divers (*reward hacking*, loi de Goodhart : « quand une mesure devient un objectif, elle cesse d'être une bonne mesure »).

Dans notre petit monde, il suffirait que la récompense du problème de stock compte seulement **le nombre d'articles vendus**, en oubliant les coûts : l'agent apprendrait à **réapprovisionner chaque jour** pour ne jamais manquer une vente, quel qu'en soit le prix, et la boutique perdrait de l'argent (1,45 € par jour au lieu d'en gagner 0,27). Le cahier le vérifie par le calcul (application 9.6). Quelques situations réelles du même type :

- une recommandation récompensée par le **clic** apprend à fabriquer des titres racoleurs ;
- une politique de remises récompensée par le **chiffre d'affaires** brade les marges ;
- un agent récompensé par la **satisfaction déclarée** apprend à ne solliciter que les clients satisfaits.

### 9.4.7 Sécurité, éthique et responsabilité

Un agent qui **apprend en agissant** agit sur de vraies personnes pendant qu'il apprend. Trois points à garder en tête :

- **Explorer a un coût humain.** Tester une mauvaise offre sur un client est un coût réel, parfois irréversible (un client perdu). L'exploration doit être bornée, supervisée, et limitée à des actions dont les pires conséquences sont acceptables. C'est la même prudence que celle de SARSA en 9.3.4.
- **L'équité ne vient pas gratuitement.** Un agent qui maximise le profit peut proposer des prix ou des offres **différents selon des groupes** de clients, sans que personne ne l'ait demandé. Les outils d'audit de la section 5.4 s'appliquent aussi aux politiques apprises.
- **Manipulation.** Une politique optimisée sur l'attention ou les achats impulsifs peut exploiter les biais cognitifs des clients. Qu'un algorithme y parvienne ne signifie pas qu'on doive l'autoriser.

### 9.4.8 Quand utiliser l'apprentissage par renforcement ?

La plupart des problèmes de boutique **n'ont pas besoin** d'apprentissage par renforcement. Voici un guide de décision :

| Votre situation | Outil adapté |
|---|---|
| Prédire une réponse à partir de données déjà collectées (churn, dépense) | **apprentissage supervisé** (chapitres 1 à 5) |
| Choisir parmi quelques options **sans** effet à long terme (bannière, objet d'un courriel) | **bandit** (9.2) ou test A/B |
| Même chose, avec des **contextes** (profil du visiteur) | **bandit contextuel** |
| Enchaîner des décisions dont **l'effet se prolonge** (stock, cycle de vie, tarification dynamique), avec un **simulateur** ou un modèle fiable | **apprentissage par renforcement** (9.1 à 9.3 ; profond si l'état est riche) |
| Mêmes décisions, **sans simulateur**, avec seulement un journal | **RL hors ligne** : avec une extrême prudence (9.4.5) |
| Problème de petite taille et modèle connu | **programmation dynamique** exacte (9.1), souvent suffisante |

> ✅ **À retenir.**
> - Quand l'espace d'états explose, on remplace la table par une **fonction approchée** (réseau de neurones) : c'est l'idée du **DQN**, qui ajoute un tampon de rejeu et un réseau cible. Les **gradients de politique** et les méthodes **acteur-critique** optimisent directement la politique.
> - Fonction approchée + amorçage + hors politique = **instabilité** possible ; l'apprentissage par renforcement profond est sensible aux hyperparamètres et aux graines.
> - L'**apprentissage hors ligne** apprend d'un journal, mais ne peut pas juger les actions jamais essayées.
> - **La récompense est le cahier des charges** : une récompense mal posée est exploitée à la lettre ; apprendre en agissant engage une **responsabilité** envers les personnes concernées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.6 (une récompense mal posée).
