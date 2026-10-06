# Chapitre 9 : ➕ Bases de l'apprentissage par renforcement

> « Personne n'apprend à faire du vélo en lisant un manuel : on tombe, on ajuste, on recommence. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : on peut lire le volume sans lui. Il suppose le chapitre 1 (démarche d'évaluation) et s'appuie sur trois résultats des volumes précédents : les chaînes de Markov (volume I, section 2.6.2), le test A/B (volume I, section 3.4.5) et la mise à jour bayésienne d'une probabilité (volume II, section 6.1). Il est indépendant des chapitres 2 à 8.

Jusqu'ici, dans ce volume, un modèle recevait un **tableau de données déjà constitué** et apprenait à prédire une colonne. Personne ne se demandait *comment* ces données avaient été produites. Dans la vie d'une boutique, pourtant, beaucoup de questions sont d'une autre nature :

- **Quelle bannière afficher** sur la page d'accueil, sachant que l'on ne connaît pas à l'avance celle qui convertit le mieux, et que chaque affichage « gaspillé » sur une mauvaise bannière coûte des ventes ?
- **Quand et combien commander** pour ne pas tomber en rupture, sans immobiliser de la marchandise qui ne se vendra pas ?
- **Quelle offre envoyer** à quel client, et à quel moment du cycle de vie, pour qu'il devienne fidèle ?

Dans chaque cas, on **agit**, le monde **répond** (une vente, une rupture, un abandon), et la réponse dépend de ce que l'on a fait. Les données que l'on recueillera demain dépendent des décisions d'aujourd'hui. C'est le terrain de l'**apprentissage par renforcement** (*reinforcement learning*, RL) : apprendre, par essais et erreurs, **une façon d'agir** qui maximise une récompense cumulée.

## Le chemin de ce chapitre

- **9.1 Processus de décision markoviens** : le vocabulaire (agent, état, action, récompense), la notion de **retour actualisé**, les **équations de Bellman** démontrées, et un premier algorithme, l'**itération de la valeur**, calculé à la main sur un exemple à trois états.
- **9.2 Bandits manchots** : le cas le plus simple, sans état, où le seul enjeu est le dilemme **explorer ou exploiter**. On compare le test A/B, ε-glouton, UCB et l'échantillonnage de Thompson sur quatre bannières.
- **9.3 Q-learning** : apprendre sans connaître les règles du jeu. On démontre la règle de mise à jour, on oppose **Q-learning et SARSA**, et on apprend à gérer un petit stock.
- **9.4 Du Q-learning à l'apprentissage profond** : pourquoi la table ne suffit plus, ce que changent les réseaux de neurones, et les précautions (récompenses mal posées, sécurité, éthique). Section de lecture, sans exécution.

## Ce qui change par rapport à l'apprentissage supervisé

| | Apprentissage supervisé (chapitres 1 à 5) | Apprentissage par renforcement |
|---|---|---|
| **Ce qu'on reçoit** | des exemples étiquetés : l'entrée **et** la bonne réponse | une **récompense** après l'action, souvent différée et partielle |
| **D'où viennent les données** | elles préexistent (le tableau est donné) | elles dépendent des **décisions prises** : l'agent influence ce qu'il observe |
| **Ce qu'on apprend** | une fonction qui prédit | une **politique** : quelle action prendre dans quel état |
| **Difficulté propre** | le surapprentissage | l'**attribution du crédit** (quelle action passée explique ce gain ?) et l'**exploration** |
| **Évaluation** | un jeu de test mis de côté | la récompense cumulée obtenue **en agissant** |

Le point de départ est donc le même (des données, un objectif), mais deux difficultés nouvelles apparaissent : **le feedback est retardé** (la commande passée aujourd'hui ne montre son effet que dans trois jours) et **les données sont biaisées par nos propres choix** (on n'observe pas ce qui serait arrivé avec l'autre bannière).

## Trois petits mondes pour tout le chapitre

Les chapitres précédents travaillaient sur des tableaux de clients. Ici, l'apprentissage par renforcement a besoin d'un **environnement** avec lequel interagir. Aucune bibliothèque dédiée n'est nécessaire : nous écrivons à la main trois environnements simples. Ils sont **simulés** (graines fixes, déclarées à chaque fois), et nous connaissons donc les vrais paramètres, ce qui permet de vérifier ce que l'algorithme apprend.

| Environnement | Section | Question | Graine(s) |
|---|---|---|---|
| **Quatre bannières** | 9.2 | laquelle afficher, sachant que les taux de conversion (4,0 ; 5,2 ; 5,8 et 7,0 %) sont inconnus ? | 900 (200 répétitions), 4, 1 et 77 |
| **Le cycle de vie d'un client** (3 états) et **le stock** (5 états) | 9.1, 9.3 | quelle action dans quel état ? | 1 (évaluation), 5 et 100 à 109 (apprentissage) |
| **Un couloir d'entrepôt** (grille 4 × 10) | 9.1, 9.3 | comment traverser sans entrer dans la zone dangereuse ? | 0 à 9 et 3 |

> 📦 **Pas de données à charger.** Ce chapitre n'utilise aucun fichier : tout est simulé dans le texte et dans les blocs de calcul. Les mêmes environnements, avec leur code complet, sont reconstruits pas à pas dans le cahier.

> ⚠️ **Un chapitre d'introduction, pas un manuel d'ingénierie.** L'apprentissage par renforcement « pour de vrai » (robotique, jeux, recommandation en ligne à grande échelle) demande des simulateurs, beaucoup de calcul et une grande prudence. Nous voulons ici comprendre **les idées** et leurs limites, sur des problèmes assez petits pour être résolus **exactement** et ainsi comparés à ce que l'apprentissage trouve.


## 9.1 Processus de décision markoviens

Cette section pose le langage de tout le chapitre. Nous partons d'une boucle très simple (l'agent agit, le monde répond), nous définissons ce que l'agent cherche à maximiser, puis nous démontrons les deux équations qui permettent de le calculer : les équations de **Bellman**. Elles servent de fil conducteur jusqu'au Q-learning.

### 9.1.1 Apprendre en agissant : la boucle agent-environnement

Un problème d'apprentissage par renforcement se décrit par deux acteurs et un échange répété :

- l'**agent** (celui qui décide : la gérante, ou le programme qui l'assiste) ;
- l'**environnement** (tout le reste : les clients, les fournisseurs, le hasard).

À chaque instant $t = 0, 1, 2, \dots$ :

1. l'agent observe l'**état** $S_t$ de la situation (le niveau de stock, le type de client) ;
2. il choisit une **action** $A_t$ (commander 3 unités, envoyer une offre) ;
3. l'environnement répond par une **récompense** $R_{t+1}$ (le gain de la journée, en €) et un **nouvel état** $S_{t+1}$.

On obtient ainsi une trajectoire $S_0, A_0, R_1, S_1, A_1, R_2, S_2, \dots$. Le but de l'agent n'est pas de maximiser la prochaine récompense : c'est de maximiser **le cumul des récompenses futures**. Commander beaucoup aujourd'hui coûte cher tout de suite et ne rapporte qu'au fil des jours suivants ; une bonne politique accepte ce compromis.

> 💡 **Intuition.** Un joueur d'échecs ne regarde pas seulement la prise de pion immédiate : il sacrifie parfois une pièce pour une position gagnante dix coups plus loin. L'apprentissage par renforcement formalise exactement cette idée : **une récompense immédiate faible peut valoir mieux qu'un gain immédiat qui conduit à une impasse**.

### 9.1.2 Récompense, retour et actualisation

Pour comparer des séquences de décisions, on résume l'avenir par un seul nombre, le **retour** (*return*) à partir de l'instant $t$ :

$$G_t \;=\; R_{t+1} + \gamma\,R_{t+2} + \gamma^2 R_{t+3} + \cdots \;=\; \sum_{k=0}^{\infty} \gamma^{k}\,R_{t+k+1}, \qquad 0\le\gamma<1.$$

Le **facteur d'actualisation** $\gamma$ pondère l'avenir : un euro reçu dans $k$ jours ne compte que $\gamma^k$ euro aujourd'hui. Il a deux rôles :

- un rôle **économique** : un euro tout de suite vaut mieux qu'un euro dans un an (on l'a rencontré, sous forme de taux d'actualisation, dans le projet du volume II) ;
- un rôle **mathématique** : il garantit que la somme infinie est finie, tant que les récompenses restent bornées.

Si la récompense vaut toujours $r$, la série est géométrique, et

$$G_t = r\,(1+\gamma+\gamma^2+\cdots) = \frac{r}{1-\gamma}.$$

Cette formule donne l'**horizon effectif** : avec $\gamma=0{,}9$ on « voit » environ $1/(1-\gamma)=10$ pas devant soi ; avec $\gamma=0{,}95$, environ 20. Au bout de cet horizon, le poids d'une récompense a été divisé par près de trois (le calcul exact est donné ci-dessous : $0{,}9^{10}\approx0{,}35$ et $0{,}95^{20}\approx0{,}36$).

> ⚠️ **Choisir $\gamma$ n'est pas neutre.** Un $\gamma$ proche de 0 produit un agent **myope** (il ne regarde que le jour même et ne commandera jamais pour demain) ; un $\gamma$ proche de 1 produit un agent **patient**, mais dont l'apprentissage est plus lent et plus instable. En pratique, $\gamma$ traduit la valeur que l'entreprise accorde au futur : ce n'est pas un réglage technique.

### 9.1.3 États, actions, transitions : le processus de décision markovien

Pour calculer, il faut un cadre précis. Un **processus de décision markovien** (MDP, *Markov decision process*) est la donnée de :

- un ensemble d'**états** $\mathcal S$ et d'**actions** $\mathcal A$ ;
- des **probabilités de transition** $P(s'\mid s,a)$ : la probabilité d'arriver en $s'$ quand on agit avec $a$ depuis $s$ ;
- une **récompense** $r(s,a)$ (ou son espérance) ;
- un facteur d'actualisation $\gamma$.

Le mot « markovien » porte l'hypothèse essentielle : **le futur ne dépend du passé qu'à travers l'état présent**. C'est la propriété des chaînes de Markov du volume I (section 2.6.2), à laquelle on a simplement ajouté des décisions : pour chaque action, une chaîne de Markov différente. Cette hypothèse est un choix de modélisation : si l'état « stock = 2 » ne contient pas l'information « un jour férié approche », la propriété est violée, et il faut enrichir l'état.

Notre premier MDP est volontairement minuscule, pour que tous les calculs se fassent à la main. Il représente le **cycle de vie d'un client** :

- trois **états** : client *occasionnel*, *régulier*, *fidèle* ;
- deux **actions** à chaque période : *attendre*, ou *envoyer une offre* ;
- les transitions sont **déterministes** : une offre fait passer d'occasionnel à régulier (en coûtant 1 € de remise), puis de régulier à fidèle ; attendre laisse l'état inchangé ; un client fidèle le reste ;
- les récompenses (marge nette par période) sont : 0 € (occasionnel qui attend), +1 € (régulier qui attend), +4 € (fidèle qui attend) ; l'offre coûte 1 € à un occasionnel (récompense −1 €), rapporte 0 € à un régulier, et fait perdre 1 € de marge à un fidèle (+3 € au lieu de +4 €) ;
- le facteur d'actualisation vaut $\gamma=0{,}9$.

La figure résume ce MDP ; elle montre aussi, à droite, le résultat de l'algorithme que nous allons dérouler.

### 9.1.4 Politiques et fonctions de valeur

Une **politique** $\pi$ est une règle de décision : $\pi(a\mid s)$ est la probabilité de choisir l'action $a$ dans l'état $s$ (une politique **déterministe** associe une action à chaque état). Pour juger une politique, on définit deux fonctions.

La **valeur d'un état** sous la politique $\pi$ est le retour moyen quand on part de $s$ et que l'on suit $\pi$ :
$$V^{\pi}(s) \;=\; \mathbb E_\pi\!\left[\,G_t \mid S_t=s\,\right].$$

La **valeur d'une action** (fonction $Q$) est le retour moyen quand on part de $s$, qu'on **commence** par l'action $a$ puis qu'on suit $\pi$ :
$$Q^{\pi}(s,a) \;=\; \mathbb E_\pi\!\left[\,G_t \mid S_t=s,\,A_t=a\,\right].$$

$V^\pi(s)$ répond à la question « combien vaut la situation $s$ si je continue comme ça ? » ; $Q^\pi(s,a)$ à « combien vaudrait la situation si je faisais d'abord $a$ ? ». L'objectif est de trouver la **meilleure** politique : celle dont la valeur est maximale en tout état.

### 9.1.5 Les équations de Bellman : démonstration

Le retour obéit à une relation **récursive** évidente : le retour d'aujourd'hui est la prochaine récompense, plus le retour de demain actualisé,
$$G_t = R_{t+1} + \gamma\,(R_{t+2}+\gamma R_{t+3}+\cdots) = R_{t+1} + \gamma\,G_{t+1}.$$

> 📐 **Équation de Bellman d'espérance.** Pour toute politique $\pi$ et tout état $s$,
> $$V^\pi(s)=\sum_{a}\pi(a\mid s)\Big[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)\,V^\pi(s')\Big].$$
>
> *Démonstration.* On part de la définition et on applique la relation récursive :
> $$V^\pi(s)=\mathbb E_\pi[G_t\mid S_t=s]=\mathbb E_\pi[R_{t+1}+\gamma G_{t+1}\mid S_t=s]=\mathbb E_\pi[R_{t+1}\mid S_t=s]+\gamma\,\mathbb E_\pi[G_{t+1}\mid S_t=s].$$
> Le premier terme vaut $\sum_a\pi(a\mid s)\,r(s,a)$. Pour le second, on conditionne sur l'état suivant (loi de l'espérance totale) :
> $$\mathbb E_\pi[G_{t+1}\mid S_t=s]=\sum_a\pi(a\mid s)\sum_{s'}P(s'\mid s,a)\;\mathbb E_\pi[G_{t+1}\mid S_{t+1}=s'].$$
> Or, par la **propriété de Markov**, l'espérance de $G_{t+1}$ sachant $S_{t+1}=s'$ ne dépend pas de ce qui s'est passé avant : elle vaut exactement $V^\pi(s')$. En regroupant, on obtient l'équation. $\blacksquare$

En mots : *la valeur d'un état est la récompense moyenne immédiate, plus la valeur actualisée de l'état où l'on atterrit.* Si l'on connaît la valeur de demain, on connaît celle d'aujourd'hui. Pour une politique fixée, c'est un **système linéaire** (une équation par état) : on peut le résoudre directement ou par itérations.

### 9.1.6 L'équation d'optimalité

Parmi toutes les politiques, il existe (pour un MDP fini avec $\gamma<1$) une politique **optimale** $\pi^*$ dont la valeur $V^*(s)=\max_\pi V^\pi(s)$ est au moins aussi bonne que toute autre, **dans tous les états à la fois**. Sa valeur obéit à la version « avec un max » de l'équation de Bellman :

$$V^*(s)=\max_{a}\Big[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)\,V^*(s')\Big],\qquad Q^*(s,a)=r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)\,\max_{a'}Q^*(s',a').$$

L'argument est le **principe d'optimalité** de Bellman : une politique optimale, à partir d'un état donné, doit choisir l'action qui maximise « récompense immédiate + valeur optimale de la suite » ; elle ne peut pas faire mieux en gâchant la suite. Et dès que l'on connaît $Q^*$, la politique optimale est immédiate : **dans chaque état, choisir l'action de $Q^*$ la plus élevée**,
$$\pi^*(s)=\arg\max_a Q^*(s,a).$$

C'est ce qui rend la fonction $Q$ si commode : on y lit directement la décision à prendre, sans avoir besoin de connaître les probabilités de transition.

### 9.1.7 L'itération de la valeur : un exemple calculé à la main

L'équation d'optimalité est une équation de **point fixe** : $V^*$ est la fonction qui ne change plus quand on lui applique le membre de droite. L'idée la plus simple pour la trouver : partir d'une valeur quelconque (par exemple $V_0=0$) et appliquer l'équation **encore et encore**,
$$V_{k+1}(s)=\max_a\Big[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)\,V_k(s')\Big].$$
C'est l'**itération de la valeur** (*value iteration*). Faisons-la à la main sur le cycle de vie du client. Dans ce MDP déterministe, la somme sur $s'$ se réduit à un seul terme, donc $V_{k+1}(s)=\max_a[r(s,a)+0{,}9\,V_k(\text{état suivant})]$.

**Itération 1** (à partir de $V_0=(0,0,0)$ pour occasionnel, régulier, fidèle).
- Fidèle : attendre donne $4+0{,}9\times0=4$ ; l'offre donne $3$. Le max vaut **4**.
- Régulier : attendre $1+0=1$ ; offre $0+0=0$. Le max vaut **1**.
- Occasionnel : attendre $0$ ; offre $-1$. Le max vaut **0**.

**Itération 2** (à partir de $V_1=(0,1,4)$).
- Fidèle : attendre $4+0{,}9\times4=7{,}6$. Régulier : attendre $1+0{,}9\times1=1{,}9$ ; **offre** $0+0{,}9\times4=3{,}6$ : le max vaut **3,6**. Occasionnel : attendre $0+0{,}9\times0=0$ ; offre $-1+0{,}9\times1=-0{,}1$ : le max vaut **0**.

**Itération 3** (à partir de $V_2=(0;\,3{,}6;\,7{,}6)$).
- Fidèle : $4+0{,}9\times7{,}6=10{,}84$. Régulier : offre $0+0{,}9\times7{,}6=6{,}84$ (contre $1+0{,}9\times3{,}6=4{,}24$ en attendant). Occasionnel : **offre** $-1+0{,}9\times3{,}6=2{,}24$, qui l'emporte enfin sur attendre ($0$).

Voici les premières itérations, avec la politique **gloutonne vis-à-vis de $V_k$** : celle qui, dans chaque état, choisit l'action au meilleur rendement d'après $V_k$ (c'est justement elle qui sert à calculer $V_{k+1}$) :

| itération $k$ | $V_k$(occasionnel) | $V_k$(régulier) | $V_k$(fidèle) | politique gloutonne (occasionnel, régulier, fidèle) |
|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | attendre, attendre, attendre |
| 1 | 0 | 1 | 4 | attendre, offre, attendre |
| 2 | 0 | 3,6 | 7,6 | offre, offre, attendre |
| 3 | 2,24 | 6,84 | 10,84 | offre, offre, attendre |
| 4 | 5,156 | 9,756 | 13,756 | offre, offre, attendre |


Deux enseignements, que la figure confirme. **D'abord**, la politique gloutonne est correcte dès $V_2$ : l'ordre « offre, offre, attendre » ne change plus ensuite, alors que les valeurs sont encore très loin de leur limite. **Ensuite**, les valeurs montent régulièrement vers un plafond. On peut le calculer exactement : un client fidèle qui attend rapporte 4 € par période pour toujours, donc $V^*(\text{fidèle})=4/(1-0{,}9)=40$ ; un régulier qui envoie l'offre gagne 0 € puis devient fidèle : $V^*(\text{régulier})=0+0{,}9\times40=36$ (c'est mieux que d'attendre pour toujours, qui rapporterait $1/(1-0{,}9)=10$) ; un occasionnel qui envoie l'offre : $V^*(\text{occasionnel})=-1+0{,}9\times36=31{,}4$. La valeur optimale vaut donc $(31{,}4\;;\;36\;;\;40)$, ce que l'algorithme retrouve.

![À gauche : le MDP du cycle de vie d'un client (trois états, deux actions). À droite : l'itération de la valeur, qui monte vers les valeurs optimales 31,4 ; 36 et 40.](figures/ch09-mdp-trois-etats.png)

> 💡 **La valeur d'un état, c'est son avenir.** Un client « fidèle » vaut 40 €, un « occasionnel » 31,4 €, bien qu'il ne rapporte rien tout de suite : sa valeur vient de ce qu'il peut devenir. L'offre, qui coûte 1 € aujourd'hui, est un **investissement** que l'algorithme sait justifier. C'est le calcul de la valeur d'un client du projet du volume II, vu comme un problème de décision.

### 9.1.8 Pourquoi l'itération converge : un argument de contraction

L'itération de la valeur ne converge pas par chance. Notons $T$ l'opérateur qui transforme une fonction de valeur $V$ en la fonction $TV$ donnée par le membre de droite de l'équation d'optimalité. On mesure la distance entre deux fonctions de valeur par leur écart maximal $\|V-W\|_\infty=\max_s|V(s)-W(s)|$.

> 📐 **Théorème.** Pour tout $V,W$ : $\;\|TV-TW\|_\infty\le\gamma\,\|V-W\|_\infty$. On dit que $T$ est une **contraction** de rapport $\gamma$.
>
> *Démonstration.* On utilise l'inégalité $\big|\max_a x_a-\max_a y_a\big|\le\max_a|x_a-y_a|$ (si le maximum de $x$ est atteint en $a_0$, alors $\max y\ge y_{a_0}\ge x_{a_0}-\max|x-y|$, et symétriquement). Pour chaque état $s$,
> $$|(TV)(s)-(TW)(s)|\le\max_a\Big|\gamma\sum_{s'}P(s'\mid s,a)\big(V(s')-W(s')\big)\Big|\le\gamma\,\|V-W\|_\infty,$$
> car une moyenne pondérée de nombres de valeur absolue au plus $\|V-W\|_\infty$ ne dépasse pas ce maximum. $\blacksquare$

Le **théorème du point fixe de Banach** en découle : $T$ a un unique point fixe, c'est $V^*$, et l'itération converge vers lui **quelle que soit la valeur de départ**, avec la garantie
$$\|V_k-V^*\|_\infty\le\gamma^{\,k}\,\|V_0-V^*\|_\infty.$$
Dans notre exemple, l'erreur est dominée par l'état fidèle, dont la valeur de départ est 0 pour une limite de 40, soit $40\times0{,}9^k$ : 36 après 1 itération, 32,4 après 2, 29,16 après 3, environ 23,6 après 5, 13,9 après 10 et 4,9 après 20. La convergence est **géométrique**, mais **lente quand $\gamma$ est proche de 1** : c'est la rançon de la patience.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1, exercices 9.1 à 9.4.

### 9.1.9 Le problème de stock

Passons à un problème plus réaliste, que nous retrouverons en 9.3. Chaque matin, la gérante observe le **stock** d'un article, entre 0 et 4 unités (l'étagère en contient 4 au plus), et décide **combien en commander** (de 0 à ce qui reste de place) ; la livraison est immédiate. Dans la journée, la **demande** est aléatoire : 0, 1, 2 ou 3 clients souhaitent l'article, avec les probabilités $0{,}2\,;\,0{,}4\,;\,0{,}3\,;\,0{,}1$ (soit 1,3 client par jour en moyenne). La récompense de la journée est :

- $+3$ € par article vendu ;
- $-1$ € par article commandé (son prix d'achat) ;
- $-4$ € de **frais de livraison fixes**, dès que l'on passe commande, quelle que soit la quantité ;
- $-0{,}5$ € par article invendu en fin de journée (coût de stockage) ;
- $-1$ € par client servi en rupture (un client déçu coûte de la fidélité).

L'état est le stock du matin (5 valeurs), l'action la quantité commandée, et nous prenons $\gamma=0{,}95$. Les transitions sont aléatoires (la demande), mais **connues** ici, ce qui permet de résoudre le problème exactement par itération de la valeur. Pour comparer, nous évaluons aussi trois règles simples, en les simulant sur 100 000 jours (graine 1).


Les valeurs optimales sont $V^*=(2{,}05\,;\,4{,}14\,;\,6{,}73\,;\,8{,}62\,;\,10{,}05)$ € pour un stock de 0, 1, 2, 3 ou 4 en début de journée ; 372 itérations suffisent pour que deux itérations successives diffèrent de moins d'un milliardième d'euro. La politique optimale est :

> **Attendre que l'étagère soit vide, puis la remplir entièrement** (commander 4 si le stock vaut 0, rien sinon).

Cette règle peut surprendre : elle accepte des ruptures. Elle s'explique par les **frais de livraison fixes** : en commandant rarement mais en grande quantité, on les partage entre beaucoup d'articles. Voyons ce que les quatre politiques rapportent en moyenne par jour :

| Politique | Gain moyen par jour |
|---|---:|
| Ne jamais commander | −1,30 € |
| Remplir l'étagère chaque jour | −1,95 € |
| Si le stock vaut 0 ou 1, remonter à 3 | −0,33 € |
| **Politique optimale** (attendre la rupture, remplir à 4) | **+0,27 €** |

Le premier chiffre se vérifie à la main : sans jamais commander, on ne vend rien et on subit la pénalité de rupture pour chaque client, soit $1{,}3\times1=1{,}3$ € de perte par jour. Le second montre que « remplir tous les jours » est ruineux : on paie chaque jour les frais fixes. La règle de bon sens de la ligne trois (« dès que ça baisse, on remonte à 3 ») perd encore de l'argent : le calcul exact trouve mieux.

![À gauche : valeur optimale selon le stock de départ. À droite : gain moyen par jour de quatre politiques (100 000 jours simulés).](figures/ch09-stock-valeurs-regles.png)

> ⚠️ **Valeur actualisée et gain moyen ne sont pas la même chose.** Les barres de gauche sont des valeurs **actualisées** (avec $\gamma=0{,}95$) ; celles de droite sont des gains moyens **par jour**, sans actualisation. Rien ne garantit que deux politiques soient classées dans le même ordre par les deux mesures : un $\gamma$ trop petit pourrait même faire préférer une politique myope. Quand on évalue une politique, on dit toujours **quelle** mesure on utilise.

### 9.1.10 Un couloir d'entrepôt : la valeur comme distance au but

Un dernier exemple, en grille, rend la notion de valeur très visuelle. Un préparateur de commandes traverse un couloir de $4\times10$ cases, du point de départ **S** (coin bas gauche) au quai d'expédition **G** (coin bas droit). La rangée du bas, entre les deux, est une **zone de chargement de chariots** : y mettre le pied coûte $-100$ € (incident évité de justesse) et ramène au départ. Chaque pas coûte $-1$ €, il n'y a pas d'actualisation, et les mouvements sont déterministes (haut, droite, bas, gauche).

L'itération de la valeur donne, pour chaque case, la valeur optimale : c'est tout simplement **moins le nombre de pas** du meilleur chemin jusqu'à G. Depuis le départ, il faut 11 pas (monter d'une case, avancer de 9 cases, redescendre d'une case), donc $V^*(\text{S})=-11$. La figure montre les valeurs par la couleur et la politique optimale par les flèches : **longer la zone dangereuse**, d'aussi près que possible, est optimal puisque le mouvement est sans aléa.


![Le couloir d'entrepôt : valeur optimale de chaque case (plus la case est sombre, plus elle est loin du quai G) et politique optimale (flèches). La zone noire est la zone de chargement dangereuse.](figures/ch09-couloir-valeurs.png)

En 9.3, nous réutiliserons ce couloir pour une raison précise : lorsque l'agent doit **apprendre** sa route en se trompant parfois, longer le précipice n'est plus aussi innocent.

> ✅ **À retenir.**
> - Un **MDP** est un état, des actions, des transitions et des récompenses, avec la propriété de Markov ; l'objectif est de maximiser le **retour actualisé** $G_t=\sum_k\gamma^kR_{t+k+1}$.
> - La **valeur** $V^\pi(s)$ et la valeur d'action $Q^\pi(s,a)$ résument l'avenir ; les **équations de Bellman** les relient à la valeur de l'état suivant.
> - La **politique optimale** choisit $\arg\max_aQ^*(s,a)$ ; l'**itération de la valeur** converge vers $V^*$ à vitesse $\gamma^k$ parce que l'opérateur de Bellman est une contraction.
> - Avec un MDP **connu** et petit, on résout exactement. Tout le reste du chapitre répond à la question suivante : *que faire quand on ne connaît pas les probabilités de transition ?*

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1 (résoudre le problème de stock et mesurer l'effet des frais fixes), exercices 9.1 à 9.4.


## 9.2 Bandits manchots

Cette section isole la difficulté la plus célèbre de l'apprentissage par renforcement : le **dilemme entre explorer et exploiter**. Pour la voir à l'état pur, on retire tout le reste : pas d'état, pas d'avenir qui dépende de l'action, une décision répétée, un résultat immédiat. On l'appelle un problème de **bandit manchot à plusieurs bras** (*multi-armed bandit*), du nom des machines à sous.

Notre terrain d'expérience : la page d'accueil de la boutique peut afficher **quatre bannières** (A, B, C, D). Chaque visiteur voit une bannière et convertit (achète) ou non. Les vrais taux de conversion, **que l'algorithme ignore**, sont :

| Bannière | A | B | C | D |
|---|---:|---:|---:|---:|
| Taux de conversion | 4,0 % | 5,2 % | 5,8 % | 7,0 % |

La meilleure bannière est D. Sur 10 000 visiteurs, la connaître d'avance rapporterait en moyenne $0{,}07\times10\,000=700$ conversions. Mais la gérante ne la connaît pas : elle doit la découvrir **en affichant** les bannières, et chaque affichage sur une mauvaise bannière est une conversion probablement perdue.


### 9.2.1 Le dilemme exploration-exploitation

À chaque visiteur, deux tentations s'opposent :

- **exploiter** : afficher la bannière qui a le mieux marché jusqu'ici, pour gagner maintenant ;
- **explorer** : afficher une autre bannière, pour savoir si elle ne serait pas meilleure, au risque de perdre maintenant.

Aucune des deux attitudes pures ne marche. Un agent qui n'exploite jamais gaspille ses visiteurs en tentatives. Un agent qui n'explore jamais peut s'enfermer sur une mauvaise bannière : si, par malchance, D convertit mal sur ses dix premiers affichages, un exploiteur pur ne lui donnera plus jamais sa chance. Toute la théorie des bandits consiste à **doser** l'exploration, et à la faire décroître à mesure que l'on en sait davantage.

### 9.2.2 Mesurer le coût de l'ignorance : le regret

Pour comparer des stratégies, on définit le **regret** : ce que l'on perd, en moyenne, par rapport à quelqu'un qui connaîtrait la meilleure bannière. Si $\mu^*$ est le taux de la meilleure bannière et $\mu_{a_t}$ celui de la bannière affichée au $t$-ième visiteur, le **regret cumulé** après $T$ visiteurs est

$$R_T \;=\; \sum_{t=1}^{T}\big(\mu^*-\mu_{a_t}\big) \;=\; T\mu^*-\sum_{t=1}^T\mu_{a_t}.$$

C'est un nombre de **conversions perdues** (en espérance). Une stratégie qui n'apprend rien (affichage au hasard) a un regret qui croît **linéairement** : chaque visiteur coûte en moyenne $0{,}07-0{,}055=0{,}015$ conversion, soit 150 conversions perdues sur 10 000 visiteurs. Une bonne stratégie a un regret qui croît **de plus en plus lentement**, parce qu'elle finit par afficher presque toujours la bonne bannière. On sait même démontrer qu'aucune stratégie ne peut faire mieux, en général, qu'un regret qui croît comme $\ln T$ (résultat de Lai et Robbins, 1985).

Le regret ne se mesure que dans une simulation (il suppose de connaître $\mu^*$). Nous le calculerons donc sur **200 répétitions** de 10 000 visiteurs (graine 900), pour chaque stratégie.

### 9.2.3 Le test A/B, vu comme une stratégie

La méthode classique est le **test A/B** (volume I, section 3.4.5) : répartir les visiteurs **à égalité** entre les bannières pendant une période de test, puis adopter la gagnante. Combien de visiteurs faut-il ? Pour distinguer D (7,0 %) de C (5,8 %) avec un risque de 5 % et une puissance de 80 %, la formule du volume I donne environ **6 530 visiteurs par bannière**, donc **26 121 visiteurs au total** pour les quatre. C'est plus de deux fois notre budget de 10 000 visiteurs : un test rigoureux à quatre bannières **n'est pas possible** dans ce cadre, et l'on aurait payé très cher son exploration, puisque trois visiteurs sur quatre auraient vu une bannière moins bonne.

On peut quand même transformer le test A/B en stratégie, avec un budget d'exploration réduit : **tester 2 000 visiteurs** (500 par bannière), puis **s'engager** sur la bannière qui a le mieux converti (on dit *explore-then-commit*). Le regret moyen est alors d'environ 48 conversions, mais le résultat est très inégal : dans 14,5 % des répétitions, **la mauvaise bannière est choisie**, et dans 10 % des répétitions le regret dépasse 125. Le test est trop court pour distinguer des bannières aussi proches.

> ⚠️ **Le test A/B n'est pas « mauvais », il répond à une autre question.** Il est conçu pour **conclure** (« D est meilleure que C, avec telle confiance »), pas pour **gagner pendant qu'on apprend**. Si le but est une décision définitive appuyée sur des preuves, c'est l'outil adapté ; si le but est de maximiser les ventes pendant que l'on cherche, les bandits sont plus efficaces. Les deux objectifs ne sont pas compatibles à 100 %, comme nous le verrons en 9.2.9.

### 9.2.4 La stratégie ε-glouton

La règle la plus simple pour mélanger exploration et exploitation : avec une probabilité $\varepsilon$ (ici $0{,}1$), afficher une bannière **au hasard** ; sinon, afficher celle dont le taux observé est le meilleur. L'idée est séduisante, mais elle a deux défauts. D'abord, l'exploration est **constante** : même quand D est évidemment la meilleure, 10 % des visiteurs voient une bannière tirée au hasard, ce qui coûte, par visiteur, $0{,}1\times0{,}015=0{,}0015$ conversion, soit 15 conversions perdues sur 10 000, **pour toujours**. Ensuite, elle est **aveugle** : elle explore autant les bannières qui semblent mauvaises que celles qui sont prometteuses.

Résultat : un regret moyen d'environ 65 conversions, avec une grande dispersion (écart-type 51), et dans 28 % des répétitions la bannière la plus affichée **n'est pas** D : le glouton s'est enfermé sur une mauvaise bannière après un démarrage malchanceux.

### 9.2.5 UCB : l'optimisme face à l'incertitude

L'idée d'**UCB** (*upper confidence bound*) est de choisir **la bannière qui pourrait être la meilleure**, en lui accordant le bénéfice du doute proportionnellement à notre incertitude. À chaque visiteur $t$, on calcule pour chaque bannière un **indice** :

$$\text{indice}_a \;=\; \underbrace{\hat\mu_a}_{\text{taux observé}} \;+\; \underbrace{\sqrt{\frac{2\ln t}{n_a}}}_{\text{bonus d'incertitude}},$$

où $n_a$ est le nombre d'affichages de $a$. On affiche la bannière d'indice maximal. Une bannière rarement affichée a un grand bonus et sera donc essayée ; au fur et à mesure qu'on la connaît mieux, le bonus s'effondre et seul le taux observé compte. L'exploration **se règle toute seule**, bannière par bannière.

> 📐 **D'où vient le bonus ?** Il vient de l'inégalité de **Hoeffding** : pour un taux observé sur $n$ essais, $P(\mu\ge\hat\mu+\varepsilon)\le e^{-2n\varepsilon^2}$ (valable pour des résultats compris entre 0 et 1). Le bonus est la valeur de $\varepsilon$ pour laquelle cette probabilité d'erreur vaut $t^{-4}$, c'est-à-dire $e^{-2n\varepsilon^2}=t^{-4}$, soit $\varepsilon=\sqrt{2\ln t/n}$. L'indice est donc une **borne supérieure plausible** du vrai taux : la probabilité qu'on le sous-estime est minuscule. Auer, Cesa-Bianchi et Fischer (2002) ont démontré que cette stratégie, appelée UCB1, a un regret qui croît comme $\ln T$, avec la borne $\sum_{a\neq a^*}\big(8\ln T/\Delta_a+(1+\pi^2/3)\Delta_a\big)$, où $\Delta_a=\mu^*-\mu_a$ est l'écart avec la meilleure bannière.

**Un exemple à la main.** Au visiteur numéro $t=1\,000$, la bannière A a été affichée 400 fois pour 20 conversions (5,0 %), la bannière B 100 fois pour 6 conversions (6,0 %). Les bonus valent
$$\sqrt{\tfrac{2\ln1000}{400}}\approx0{,}186\quad(\text{A}),\qquad\sqrt{\tfrac{2\ln1000}{100}}\approx0{,}372\quad(\text{B}),$$
donc les indices valent $0{,}050+0{,}186=0{,}236$ pour A et $0{,}060+0{,}372=0{,}432$ pour B. On affiche **B** : peu connue, elle bénéficie d'un grand doute.

Mais remarquez l'**ordre de grandeur** : le bonus (0,19 à 0,37) est **plusieurs fois supérieur** aux taux eux-mêmes (5 à 6 %). La formule suppose des résultats répartis sur tout l'intervalle $[0,1]$, alors que nos conversions sont rares. Le résultat est un **excès d'exploration** : UCB1 affiche D seulement 35 % du temps, et son regret moyen (**123 conversions**) est le **pire** de toutes les stratégies, bien qu'il soit très régulier (écart-type 5). La borne théorique de 12 690 est vraie, mais très pessimiste.

Le remède classique est de **réduire le bonus** : remplacer le 2 par une constante $c$ à régler. Le regret moyen vaut 123,4 pour $c=2$, 99,2 pour $c=0{,}5$, **56,6 pour $c=0{,}1$** et 38,8 pour $c=0{,}05$. Dans le tableau qui suit, nous retenons $c=0{,}1$. Attention toutefois : choisir $c$ en regardant le regret sur *la même simulation* est une forme de triche (on sait déjà que D gagne). En pratique, $c$ est un **hyperparamètre**, à régler avec la rigueur du chapitre 1 (section 1.5).

### 9.2.6 L'échantillonnage de Thompson

L'autre grande idée est bayésienne, et elle est plus élégante. Pour chaque bannière, on entretient une **croyance** sur son taux de conversion, sous forme d'une loi de probabilité. Avec une loi *a priori* uniforme et des résultats « conversion / pas de conversion », cette croyance est une **loi Bêta** (volume II, section 6.1.3) : après $s$ conversions en $n$ affichages, le taux suit une loi $\mathrm{Bêta}(1+s,\,1+n-s)$. L'**échantillonnage de Thompson** (1933) procède ainsi, à chaque visiteur :

1. pour chaque bannière, **tirer un taux au hasard** dans sa loi Bêta ;
2. afficher la bannière dont le taux tiré est le plus élevé ;
3. observer le résultat et mettre à jour la loi de cette bannière.

```python
# Un tour de Thompson (succes et essais : tableaux de taille 4 ; taux_vrais : inconnus de l'algorithme)
theta = rng.beta(1 + succes, 1 + essais - succes)    # un taux tiré dans chaque loi Bêta
a = int(np.argmax(theta))                            # on affiche la bannière au taux tiré le plus haut
x = rng.random() < taux_vrais[a]                     # le visiteur convertit-il ?
essais[a] += 1                                       # mise à jour : une conversion de plus ou non
succes[a] += x
```

L'astuce est que **la probabilité d'afficher une bannière égale la probabilité qu'elle soit la meilleure**, d'après nos croyances (c'est le *probability matching*). **Exemple à la main** : à $t=1\,000$, A (20 conversions sur 400) suit une loi $\mathrm{Bêta}(21,\,381)$ et B (6 sur 100) une loi $\mathrm{Bêta}(7,\,95)$. En tirant de nombreux couples de taux, on trouve que le taux de B dépasse celui de A dans **71 % des cas** : B sera donc affichée 71 % du temps, et A 29 %. Contrairement à UCB, la décision est **aléatoire**, et l'exploration est naturellement concentrée sur les bannières encore plausibles.

La figure montre l'évolution des croyances pour une répétition (graine 4). Après 100 visiteurs, tout est flou ; après 1 000, D émerge ; après 10 000, la croyance sur D est étroite (8 816 affichages) alors que celles sur les trois autres sont larges : on **ne les a plus regardées**, et c'est parfaitement raisonnable, puisqu'on a compris qu'elles étaient moins bonnes.

![Croyances de l'algorithme de Thompson sur le taux de chaque bannière, après 100, 1 000 et 10 000 visiteurs (une seule répétition). Les traits pointillés verticaux marquent les vrais taux, inconnus de l'algorithme.](figures/ch09-thompson-croyances.png)

### 9.2.7 Comparaison des stratégies

Voici les cinq stratégies sur les mêmes 200 répétitions (graine 900) :

| Stratégie | Regret moyen | Écart-type | 90e centile | Part des affichages sur D | Répétitions où la bannière la plus affichée n'est pas D |
|---|---:|---:|---:|---:|---:|
| A/B test (2 000 visiteurs, puis la meilleure) | 47,9 | 36,6 | 125,0 | 71,8 % | 14,5 % |
| ε-glouton ($\varepsilon=0{,}1$) | 64,6 | 50,9 | 138,6 | 61,8 % | 28,0 % |
| UCB1 (bonus classique) | 123,4 | 5,3 | 130,3 | 34,7 % | 1,0 % |
| UCB à bonus réduit ($c=0{,}1$) | 56,6 | 14,6 | 74,9 | 66,6 % | 1,0 % |
| **Thompson** | **46,2** | 23,2 | **74,1** | 71,5 % | 7,0 % |

![Regret cumulé moyen (conversions perdues) de cinq stratégies d'affichage sur 10 000 visiteurs, moyenne de 200 répétitions.](figures/ch09-regret-bandits.png)

Ce qu'il faut lire dans ce tableau :

- **Thompson** a le meilleur regret moyen (46,2), **mais le test A/B est tout près** (47,9). Sur le total de conversions, la différence est négligeable : 652 pour le A/B contre 654 pour Thompson, sur les 700 qu'une connaissance parfaite aurait données.
- La vraie différence est dans la **queue de la distribution** : le A/B a 14,5 % de chances de se tromper de bannière et un 90e centile de regret de 125, contre 74 pour Thompson. Le premier est un **pari** ; le second est **robuste**.
- **UCB1** est très régulier (écart-type 5) mais cher : son exploration est trop prudente pour des taux aussi petits. Réduit, il devient compétitif.
- **ε-glouton** est dominé par les trois meilleures stratégies (Thompson, A/B, UCB réduit) : regret moyen plus élevé, plus forte dispersion, et 28 % de répétitions enfermées sur une mauvaise bannière. Il cumule exploration constante *et* risque d'enfermement.

> 🧪 **Ne généralisez pas ce classement.** Il dépend de l'écart entre les bannières, de leur nombre, du nombre de visiteurs et de la valeur de $c$. Dans cette expérience précise (peu de visiteurs, taux faibles), Thompson et A/B sont proches en moyenne ; avec 100 000 visiteurs, l'avantage des méthodes adaptatives serait bien plus net. Le message n'est pas « Thompson gagne », mais **« une stratégie adaptative réduit le coût et la variance de l'exploration »**.

### 9.2.8 Quand le meilleur choix dépend du contexte

Jusqu'ici, la même bannière était la meilleure pour tous les visiteurs. En réalité, le meilleur choix dépend souvent de **qui est le visiteur**. Un **bandit contextuel** observe, avant de choisir, un **contexte** (le canal d'arrivée, l'appareil, la ville) et apprend une politique par contexte. Imaginons que trois canaux d'arrivée (Boutique, Site, Réseaux ; 30, 40 et 30 % des visiteurs) préfèrent des bannières différentes :

| Canal d'arrivée | A | B | C | D | Meilleure |
|---|---:|---:|---:|---:|:---:|
| Boutique | 6,0 % | 4,0 % | 3,0 % | 4,5 % | A |
| Site | 4,0 % | 4,5 % | 7,0 % | 5,0 % | C |
| Réseaux | 3,5 % | 4,0 % | 4,5 % | 7,5 % | D |

Si l'on ignore le canal, la meilleure bannière **unique** est D, avec un taux moyen de 5,6 % ; en choisissant la bonne bannière **par canal**, on atteindrait 6,85 %. En simulant Thompson (graine 77, 200 répétitions de 10 000 visiteurs), l'algorithme **aveugle au contexte** accumule un regret moyen de 164,5 conversions (par rapport à la politique idéale par canal), tandis que l'algorithme qui entretient **une croyance par canal** n'en accumule que 80,1. Savoir à qui l'on s'adresse divise le regret par deux.

La version complète des bandits contextuels remplace la table « un canal = une ligne » par un **modèle** (régression logistique, arbre) qui prédit la probabilité de conversion à partir de variables nombreuses ; les méthodes les plus connues (LinUCB, Thompson avec régression) en dérivent. Elles ne sont pas exécutées ici.

### 9.2.9 Précautions

Les bandits sont puissants, et dangereux quand on oublie leurs hypothèses.

- **Les taux changent.** Un taux de conversion varie avec la saison, les promotions, la météo (volume II, chapitre 4). Un bandit qui a « fini d'explorer » ne s'adapte plus ; il faut oublier le passé (fenêtre glissante, facteur d'oubli) ou garder une exploration résiduelle.
- **Les résultats arrivent en retard.** Si l'on ne sait qu'au bout de 10 jours qu'une commande est retournée, le bandit apprend sur des signaux incomplets.
- **On optimise ce qu'on mesure.** Si la récompense est le clic, la bannière « pièges à clics » gagnera, même si elle déçoit ensuite le client.
- **L'allocation adaptative biaise les estimations.** Une bannière peu affichée l'a été **parce qu'elle a mal débuté** : son taux observé est donc, en moyenne, **sous-estimé**. Dans nos 200 répétitions de Thompson, le taux estimé moyen des bannières A, B, C et D vaut 3,43 %, 4,64 %, 5,31 % et 6,92 %, contre des vrais taux de 4,0 ; 5,2 ; 5,8 et 7,0 %. Les trois bannières abandonnées sont toutes **sous-estimées**.
- **La randomisation devient un choix algorithmique.** Un test A/B randomisé donne une comparaison **causale** propre (volume II, chapitre 7, section 7.1). Les probabilités d'un bandit changent avec le temps, ce qui complique l'inférence : on peut la rétablir en gardant les probabilités d'affichage et en pondérant (volume II, section 7.2), mais ce n'est plus un simple calcul de moyennes.

| | **Test A/B** | **Bandit** |
|---|---|---|
| Objectif | **conclure** avec confiance | **gagner** en apprenant |
| Allocation | fixe, à égalité | adaptative |
| Coût de l'exploration | élevé et connu d'avance | faible, mais variable |
| Qualité de l'inférence | excellente | dégradée (biais d'estimation) |
| À utiliser quand | la décision est définitive et doit être justifiée | le contexte change vite et chaque affichage compte |

> ✅ **À retenir.**
> - Un **bandit** est le problème de décision le plus simple : pas d'état, un résultat immédiat, et un dilemme **explorer / exploiter**.
> - Le **regret** mesure les conversions perdues par rapport à une connaissance parfaite ; une bonne stratégie a un regret qui croît lentement (en $\ln T$).
> - **ε-glouton** explore à taux constant ; **UCB** explore là où l'incertitude est grande (attention aux constantes) ; **Thompson** tire au sort selon ses croyances bayésiennes. Les deux derniers explorent de façon **dirigée**.
> - Le **contexte** divise le regret quand le meilleur choix dépend du visiteur ; un **test A/B** reste préférable pour **conclure**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.2 et 9.3, exercices 9.5 à 9.8.


## 9.3 Q-learning : apprendre sans connaître les règles

En 9.1, nous avons **résolu** le problème de stock parce que nous connaissions les probabilités de demande. Dans une vraie boutique, personne ne les connaît : on observe seulement ce qui se passe quand on agit. Cette section montre comment apprendre une bonne politique **à partir de l'expérience seule**, c'est-à-dire de suites $(s,a,r,s')$ : « j'étais dans l'état $s$, j'ai fait $a$, j'ai gagné $r$, et je me suis retrouvé en $s'$ ».

### 9.3.1 Apprendre sans modèle

Deux familles de méthodes se distinguent :

- les méthodes **avec modèle** (*model-based*) estiment d'abord les transitions et les récompenses à partir de l'expérience, puis résolvent le MDP estimé (comme en 9.1). Elles demandent beaucoup d'observations pour bien estimer le modèle entier ;
- les méthodes **sans modèle** (*model-free*) apprennent directement la valeur des actions, sans jamais écrire le modèle. C'est le cas du Q-learning.

Une première idée sans modèle serait de jouer des journées entières, de calculer le retour de chaque épisode, puis de **moyenner** les retours observés depuis chaque état (méthode de Monte-Carlo). Elle est correcte, mais lente : il faut attendre la fin de l'épisode, et la variance des retours est grande. La **différence temporelle** fait mieux, en s'appuyant sur l'équation de Bellman.

### 9.3.2 La différence temporelle

L'équation de Bellman (9.1.5) dit que $V^\pi(s)=\mathbb E\big[R_{t+1}+\gamma V^\pi(S_{t+1})\mid S_t=s\big]$. À chaque transition observée, la quantité $R_{t+1}+\gamma V(S_{t+1})$ est donc **un tirage aléatoire dont l'espérance est la bonne valeur**. L'idée consiste à rapprocher notre estimation actuelle $V(S_t)$ de ce tirage, d'un petit pas $\alpha$ :

$$V(S_t)\;\leftarrow\;V(S_t)+\alpha\,\underbrace{\big[R_{t+1}+\gamma V(S_{t+1})-V(S_t)\big]}_{\delta_t\ :\ \text{erreur de différence temporelle}}.$$

L'**erreur de différence temporelle** $\delta_t$ est la **surprise** : la différence entre ce que l'on pensait (la valeur de $S_t$) et ce que l'on vient d'observer (la récompense, plus la valeur de la suite *telle qu'on l'estime*). Si $\delta_t>0$, l'état était meilleur que prévu : on relève sa valeur. On dit que la méthode **amorce** (*bootstrap*) : elle corrige une estimation à partir d'une autre estimation, sans attendre la fin de l'histoire.

> 💡 **Pourquoi ça marche.** C'est une **moyenne mobile** : si l'on remplaçait $\alpha$ par $1/n$ et la cible par un tirage indépendant, on retrouverait exactement la moyenne arithmétique des tirages. La cible $R+\gamma V(S')$ n'est pas tout à fait un tirage indépendant (elle contient notre estimation $V$), mais la contraction de Bellman (9.1.8) garantit que cette boucle de rétroaction s'améliore au lieu de s'emballer.

### 9.3.3 Le Q-learning

Pour *choisir* une action, on a besoin de la valeur des **actions**, pas seulement des états. Le **Q-learning** (Watkins, 1989) applique la différence temporelle à l'équation d'**optimalité** (9.1.6) : après avoir observé $(s,a,r,s')$,

$$Q(s,a)\;\leftarrow\;Q(s,a)+\alpha\Big[\,r+\gamma\max_{a'}Q(s',a')-Q(s,a)\Big].$$

C'est la même idée, avec un max : la cible est « la récompense observée, plus la valeur de la **meilleure** action possible dans l'état suivant ». Comme la cible est un tirage dont l'espérance est $(TQ)(s,a)$, où $T$ est l'opérateur de Bellman d'optimalité, et que $Q^*$ est son point fixe, la règle pousse $Q$ vers $Q^*$.

```python
# Une mise à jour de Q-learning après l'observation (s, a, r, s2)
cible = r + gamma * Q[s2].max()           # ce que l'on croit valoir cette action, d'après la suite
Q[s, a] += alpha * (cible - Q[s, a])      # on rapproche l'estimation de la cible, d'un pas alpha
```

**Un calcul à la main.** Dans le problème de stock, supposons que l'on soit en $s=0$ (étagère vide), que l'on commande 4 articles, et que la demande du jour soit de 2 clients. La récompense vaut $2\times3$ (ventes) $-4\times1$ (achats) $-4$ (frais fixes) $-0{,}5\times2$ (deux articles invendus) $-0=-3$ €, et le stock suivant vaut $4-2=2$. Admettons que l'estimation courante soit $Q(0,4)=3{,}0$ et que la meilleure valeur connue en $s'=2$ soit $\max_{a'}Q(2,a')=6{,}0$ (valeurs choisies pour l'illustration). Avec $\gamma=0{,}95$ et $\alpha=0{,}1$ :

$$\text{cible}=-3+0{,}95\times6{,}0=2{,}7,\qquad\delta=2{,}7-3{,}0=-0{,}3,\qquad Q(0,4)\leftarrow3{,}0+0{,}1\times(-0{,}3)=2{,}97.$$

La surprise est légèrement négative (la journée a été un peu moins bonne que prévu), et l'estimation baisse d'un dixième de cet écart.

> 💡 **Le Q-learning est « hors politique » (*off-policy*).** Il apprend la valeur de la politique **gloutonne** (à cause du max), alors que les actions *jouées* pendant l'apprentissage sont choisies par une autre politique, qui explore. Cette séparation est précieuse : on peut apprendre la politique optimale en agissant différemment, ou même à partir de données collectées par quelqu'un d'autre.

### 9.3.4 SARSA, ou apprendre en tenant compte de ses propres erreurs

Une variante remplace le max par **l'action effectivement choisie** ensuite, $a'$ :

$$Q(s,a)\leftarrow Q(s,a)+\alpha\big[r+\gamma\,Q(s',a')-Q(s,a)\big].$$

Le nom vient de la suite $(S,A,R,S',A')$ qu'elle utilise. SARSA est **sur la politique** (*on-policy*) : elle évalue la politique qu'elle suit réellement, **exploration comprise**. La différence, qui paraît minuscule, a des conséquences visibles sur le couloir d'entrepôt de 9.1.10. Cette fois, **l'agent ne connaît pas la carte** : il l'apprend par essais, avec $\alpha=0{,}5$ et une exploration $\varepsilon=0{,}1$ (10 % des pas sont tirés au hasard), pendant 500 épisodes. On répète l'expérience pour 10 graines.


Deux observations :

- **Pendant l'apprentissage**, SARSA obtient un retour moyen de $-26{,}6$ par épisode (sur les 100 derniers), contre $-39{,}5$ pour le Q-learning : le Q-learning tombe plus souvent dans la zone dangereuse.
- **Les chemins appris**, si l'on suit ensuite la politique gloutonne, sont différents : le Q-learning trouve le chemin **le plus court**, qui longe la zone dangereuse (11 pas, rangée 2) ; SARSA trouve un chemin **plus long mais plus sûr**, qui passe par la rangée du haut (15 pas).

![À gauche : retour par épisode pendant l'apprentissage (moyenne de 10 graines, lissée sur 10 épisodes). À droite : chemins gloutons appris par SARSA et par le Q-learning ; la zone noire est dangereuse.](figures/ch09-sarsa-q-couloir.png)

L'explication tient à ce que chacune **estime**. Le Q-learning suppose qu'à partir de la case suivante, il jouera au mieux : le bord du précipice lui semble donc sans danger. Mais **pendant l'apprentissage**, il joue avec $\varepsilon=0{,}1$ : sur le bord, un pas tiré au hasard sur dix peut le précipiter. SARSA, lui, apprend la valeur de la politique **réellement suivie**, dérapages compris ; il en déduit que le bord est risqué, et s'en écarte. Quand $\varepsilon$ tend vers zéro, les deux méthodes convergent vers le même chemin optimal.

> ⚠️ **On-policy ou off-policy : une question de sécurité.** Si les erreurs d'exploration sont **coûteuses ou irréversibles** (un robot près d'un escalier, une promotion qui fâche un client pour toujours), la prudence de SARSA est souhaitable : l'agent apprend en tenant compte du fait qu'il se trompera. Si l'on apprend dans un **simulateur** où les erreurs ne coûtent rien, le Q-learning, qui vise directement la politique optimale, est préférable.

### 9.3.5 Explorer pendant l'apprentissage

Nous avons déjà rencontré le dilemme en 9.2 ; il revient ici, état par état. Dans nos expériences, l'exploration est de type **ε-glouton à décroissance** : avec la probabilité $\varepsilon_t$, l'agent choisit une action légale au hasard, sinon il choisit l'action de plus grand $Q$. Pour le stock, $\varepsilon$ décroît linéairement de 1 à 0,05 pendant la première moitié de l'apprentissage, puis reste à 0,05. Au début, l'agent explore donc presque toujours ; à la fin, il exploite presque toujours.

D'autres techniques existent : l'**initialisation optimiste** (on part de valeurs $Q$ très élevées, de sorte que toute action essayée « déçoit » et que les autres paraissent plus attrayantes) ; les **bonus d'exploration** inspirés d'UCB (9.2.5), qui valorisent les couples $(s,a)$ peu visités ; l'exploration par **bruit** sur les paramètres, dans les méthodes profondes (9.4).

### 9.3.6 Quand le Q-learning converge

Le Q-learning ne converge pas toujours. Un théorème de **Watkins et Dayan (1992)** donne des conditions suffisantes : si chaque couple $(s,a)$ est visité **une infinité de fois**, et si le pas d'apprentissage $\alpha_n$ utilisé à la $n$-ième mise à jour de ce couple vérifie les conditions de **Robbins et Monro**,
$$\sum_{n}\alpha_n=\infty\qquad\text{et}\qquad\sum_n\alpha_n^2<\infty,$$
alors $Q$ converge vers $Q^*$ avec probabilité 1. La première condition garantit que l'on peut **aller aussi loin** que nécessaire ; la seconde que le **bruit finit par s'éteindre**. Un pas $\alpha_n=1/n$ les satisfait (la série harmonique diverge, la série des carrés converge) ; un pas **constant** ne satisfait pas la seconde : la table continue de bouger au gré du hasard et ne se fixe jamais.

Mesurons-le sur le problème de stock (graine 5, 300 000 jours), en comparant un pas constant $\alpha=0{,}1$ à un pas décroissant $\alpha=1/(1+N/50)$, où $N$ est le nombre de fois que le couple a été visité. L'erreur maximale entre la table apprise et la vraie fonction $Q^*$ (calculée en 9.1) vaut, après 10 000, 50 000, 150 000 et 300 000 jours :

| Pas d'apprentissage | 10 000 | 50 000 | 150 000 | 300 000 |
|---|---:|---:|---:|---:|
| Constant ($\alpha=0{,}1$) | 0,55 € | 0,71 € | 1,22 € | 0,79 € |
| Décroissant | 1,02 € | 0,24 € | 0,16 € | 0,25 € |

Le pas constant **n'améliore plus rien** : l'erreur oscille autour de 1 €. Le pas décroissant, lent au départ, **descend** ensuite d'un facteur 4 environ. Sur 10 graines, le pas décroissant retrouve la politique optimale **10 fois sur 10** avec une erreur maximale moyenne de 0,20 €, contre **8 fois sur 10** et 1,22 € pour le pas constant.

![Erreur maximale entre la table Q apprise et la vraie fonction Q* au fil de l'apprentissage, pour un pas constant et un pas décroissant (échelle logarithmique).](figures/ch09-q-learning-stock.png)

> ⚠️ **Dans la pratique, on utilise souvent un pas constant.** Il s'adapte si le monde change (un pas décroissant « s'endort »). C'est le bon choix quand les données évoluent, au prix d'une table qui reste bruitée : comme toujours, le réglage dépend de la situation.

### 9.3.7 Sur le problème de stock

Le Q-learning, sans connaître les probabilités de demande, retrouve ici la politique optimale : **attendre la rupture, puis remplir** (commander 4 si le stock vaut 0, rien sinon). Son gain moyen simulé vaut $0{,}27$ € par jour, identique à celui de la solution exacte, alors que la règle de bon sens de 9.1.9 (« remonter à 3 si le stock vaut 0 ou 1 ») perd 0,33 € par jour. L'apprentissage a donc découvert, **par l'expérience seule**, qu'il fallait accepter des ruptures pour amortir les frais de livraison, ce qu'aucune règle intuitive n'aurait suggéré.

### 9.3.8 Les limites de la table

Ce succès est trompeur, pour trois raisons.

- **L'expérience coûte cher.** Nos 300 000 jours simulés représentent environ **822 ans** de vie de la boutique. L'apprentissage ne fonctionne que dans un **simulateur** (ou avec d'énormes volumes de données historiques) : on ne peut pas laisser une vraie boutique faire 300 000 essais.
- **La table est minuscule** : 15 couples $(s,a)$ ici. Dès que l'état contient plusieurs variables (le stock de dix produits, le jour de la semaine, la météo), le nombre d'états explose : c'est le sujet de la section suivante.
- **Le Q-learning est instable en dehors de la table.** Les garanties de convergence ci-dessus supposent une table exacte ; elles disparaissent quand on approxime $Q$ par une fonction (9.4).

> ✅ **À retenir.**
> - L'apprentissage **par différence temporelle** corrige une estimation à partir d'une autre : $\delta=r+\gamma V(s')-V(s)$ mesure la surprise.
> - Le **Q-learning** vise $Q^*$ avec la cible $r+\gamma\max_{a'}Q(s',a')$ ; il est **hors politique**. **SARSA** utilise l'action réellement jouée ; elle est **sur la politique** et plus prudente quand l'exploration est risquée.
> - Il converge si tous les couples sont visités infiniment et si le pas vérifie $\sum\alpha=\infty$, $\sum\alpha^2<\infty$ ; un pas constant laisse un bruit résiduel.
> - Sur un petit problème, il retrouve la solution exacte, mais au prix de **beaucoup d'expérience** : c'est la raison d'être des simulateurs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.4 et 9.5, exercices 9.9 à 9.12.


## 9.4 Du Q-learning à l'apprentissage profond

Cette section est une **lecture** : elle explique ce qui change quand on quitte la table, sans rien exécuter (ni PyTorch ni TensorFlow n'est installé pour ce livre). Les méthodes décrites ici sont celles des grandes réussites médiatiques (jeux vidéo, Go, robots) ; elles sont aussi celles dont il faut le plus se méfier, et nous en profitons pour discuter les précautions d'emploi.

### 9.4.1 Quand la table explose

Le Q-learning stocke une valeur par couple (état, action). Pour le stock d'un seul article, cela représente 15 valeurs. Imaginons maintenant que la gérante gère **dix articles**, chacun avec un stock de 0 à 20 unités : l'état est la liste des dix stocks, et il y a $21^{10}=16\,679\,880\,978\,201$ états, soit près de **17 000 milliards**. Ajoutons le jour de la semaine (7 valeurs) : un nombre de l'ordre de $10^{14}$. Aucune table ne tient en mémoire, et surtout **aucun agent ne peut visiter chaque état** : la plupart des situations ne se rencontreront jamais deux fois.


Il faut **généraliser** : estimer la valeur d'une situation jamais vue à partir de situations voisines déjà vues. C'est exactement ce que fait l'apprentissage supervisé (chapitres 1 et 2). On remplace donc la table par une **fonction paramétrée** $Q_\theta(s,a)$ (une régression, un arbre, un réseau de neurones), que l'on ajuste pour qu'elle respecte l'équation de Bellman.

### 9.4.2 Approximer la fonction de valeur : le principe du DQN

L'idée du **DQN** (*deep Q-network*, Mnih et al., 2015) est d'entraîner un réseau de neurones $Q_\theta$ avec la même cible que le Q-learning. Après une transition $(s,a,r,s')$, on cherche à réduire l'erreur
$$L(\theta)=\Big(r+\gamma\max_{a'}Q_{\theta^-}(s',a')-Q_\theta(s,a)\Big)^2.$$
Deux ingrédients rendent l'entraînement praticable :

- le **tampon de rejeu** (*replay buffer*) : on stocke les transitions passées et on entraîne sur des **mini-lots tirés au hasard** dans ce tampon. Sans cela, les exemples successifs sont très corrélés (la journée $t+1$ ressemble à la journée $t$), ce qui viole l'hypothèse « exemples indépendants » de l'apprentissage supervisé (chapitre 1) ;
- le **réseau cible** $\theta^-$ : une copie *figée* du réseau, mise à jour rarement, qui sert à calculer la cible. Sans lui, la cible bouge à chaque pas puisqu'elle dépend des paramètres que l'on est en train de modifier.

```python
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


## Bilan du chapitre 9

Vous savez maintenant :

- **formuler** un problème de décision séquentielle comme un **processus de décision markovien** (états, actions, transitions, récompenses, facteur d'actualisation), et expliquer pourquoi la propriété de Markov est un choix de modélisation ;
- **démontrer** les **équations de Bellman** (d'espérance et d'optimalité), calculer à la main quelques itérations de l'**itération de la valeur** et justifier sa convergence par un argument de **contraction** ;
- lire une **politique optimale** dans $Q^*$, et comparer une politique apprise ou calculée à des règles simples avec un **gain moyen simulé** ;
- distinguer le **test A/B**, qui sert à **conclure**, des **bandits**, qui servent à **gagner en apprenant**, et mesurer un **regret** ; mettre en œuvre **ε-glouton**, **UCB** (et comprendre pourquoi ses constantes comptent) et l'**échantillonnage de Thompson** (lien avec l'inférence bayésienne du volume II) ;
- reconnaître l'intérêt d'un **contexte** (bandit contextuel) et les **biais** que crée une allocation adaptative ;
- écrire la règle du **Q-learning** et de **SARSA**, expliquer la différence entre **hors politique** et **sur la politique**, et énoncer les conditions de convergence de **Robbins et Monro** ;
- expliquer pourquoi la table ne suffit plus, ce que changent le **DQN** et les **gradients de politique**, et pourquoi l'apprentissage par renforcement profond est **fragile** ;
- poser les bonnes questions avant de déployer un agent : **la récompense mesure-t-elle ce que l'on veut ? Qui paie le coût de l'exploration ? Existe-t-il un simulateur ?**

Trois idées à emporter. **D'abord, agir et apprendre sont indissociables** : les données dépendent des décisions, donc l'évaluation doit se faire en conditions réelles de décision (le jeu de test mis de côté du chapitre 1 n'existe plus). **Ensuite, explorer a un prix** : c'est lui que mesurent le regret et l'écart entre les stratégies. **Enfin, la récompense est le cahier des charges** : l'algorithme optimise ce qu'on lui demande à la lettre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.6 et exercices 9.1 à 9.12.

Ce chapitre était le dernier des chapitres complémentaires. Le **projet du volume**, dans le cahier, rassemble les chapitres 1 à 5 en un pipeline complet sur un jeu de données réel, du modèle de référence à l'interprétation.
