# Chapitre 7 : ➕ Systèmes de recommandation

> « Montrer à chacun les quelques produits, parmi des milliers, qu'il a une vraie chance d'aimer : voilà un problème de prédiction où la bonne réponse n'existe que dans l'avenir. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui veulent voir comment les idées du volume (validation honnête, modèles de référence, factorisation, évaluation) se déclinent dans un problème qui n'est ni une classification ni une régression : **classer des produits pour chaque client**.

Quand la gérante ouvre la page d'accueil de sa boutique en ligne, elle aimerait que chaque visiteur voie en premier les produits qu'il est le plus susceptible d'acheter. Elle n'a pas de variable « client à retenir » à prédire, comme au chapitre 2 : elle a un **historique d'achats** et une question plus délicate, « parmi les 150 produits du catalogue, lesquels montrer à *ce* client-là, dans quel ordre ? ».

C'est le problème de la **recommandation**. Il est plus ouvert qu'il n'y paraît : on ne dispose que d'achats (jamais de « non, ce produit ne m'intéresse pas »), la plupart des cases du tableau clients × produits sont vides, les produits populaires écrasent les autres, et les recommandations changent elles-mêmes les achats futurs. Le volume a donné les outils pour s'y prendre : une démarche d'évaluation rigoureuse (chapitre 1), des modèles de référence à battre (section 1.4), de la régularisation (section 2.1), une factorisation de matrice (la décomposition en valeurs singulières du volume I, section 1.1.4, et l'ACP du volume II, section 3.1).

## Le chemin de ce chapitre

- **7.1 Données d'interaction et références simples** : ce que l'on observe vraiment, la matrice d'interactions, et deux premières méthodes qui ne demandent aucun apprentissage sophistiqué : la **popularité** et le **filtrage par contenu**.
- **7.2 Filtrage collaboratif** : « ceux qui ont acheté comme vous ont aussi acheté… ». Les méthodes de **voisinage**, entre clients et entre produits.
- **7.3 Factorisation matricielle** : résumer chaque client et chaque produit par quelques **facteurs latents**, appris en minimisant une erreur régularisée ; le cas des achats **implicites**.
- **7.4 Évaluation et démarrage à froid** : comment mesurer un classement, pourquoi un découpage aléatoire peut tromper, ce que valent les recommandations pour un **nouveau client** ou un **nouveau produit**, et pourquoi les recommandations modifient les données qui serviront à les améliorer.

> 💡 **Le fil rouge du chapitre.** À chaque étape, la même question : *par rapport à quoi ?* Une recommandation « personnalisée » n'a d'intérêt que si elle fait mieux que montrer à tout le monde les produits les plus vendus. Nous verrons que, sur les données de la boutique, cette référence très simple est étonnamment difficile à battre.

## Les données et le protocole

Nous utilisons deux fichiers de la boutique (simulés, comme tous ceux du volume) : `donnees/interactions.csv` (qui a acheté quoi, et combien de fois) et `donnees/produits_ml.csv` (catégorie, prix et caractère « nouveau » de chaque produit).


Le tableau contient **3 000 clients** et **150 produits** ; les clients ont passé en tout **27 687** achats distincts (une paire client-produit compte une fois, quel que soit le nombre d'exemplaires achetés). Sur les 450 000 cases possibles du tableau, seules **6,2 %** sont remplies : c'est ce que l'on appelle une matrice **creuse**.

Pour évaluer honnêtement les méthodes, nous appliquons dès maintenant la règle du chapitre 1 : trois jeux de données, séparés **avant** de regarder quoi que ce soit.

- On ne retient pour l'évaluation que les clients ayant au moins **5 achats** : ils sont **2 365**.
- Pour chacun, on met de côté au hasard environ **25 %** de ses achats : ce sont les achats du **jeu de test**, que personne ne regardera avant la fin (**6 523** achats au total).
- Parmi les achats restants, on met de côté environ **20 %** : c'est le **jeu de validation** (**3 987** achats), qui servira à choisir les hyperparamètres.
- Tout le reste, **17 177** achats, forme le **jeu d'entraînement**. Les clients qui ont moins de 5 achats restent dans l'entraînement, mais ne sont pas évalués.

Une méthode reçoit donc les achats d'entraînement, produit pour chaque client évalué un **classement** des produits qu'il n'a pas encore achetés, et on regarde dans quelle mesure les achats retirés apparaissent en tête de liste. Les métriques précises sont définies en 7.4.1 ; en attendant, retenez l'idée : plus les achats cachés remontent haut dans le classement, meilleur est le modèle.

> ⚠️ **Une limite à connaître dès le départ.** Ces données ne contiennent **pas de dates**. Nous ne pouvons donc pas découper « le passé » et « l'avenir », comme on le ferait dans un vrai projet, et nous retirons des achats au hasard, client par client. Nous verrons en 7.4.3, sur une simulation où le temps existe, à quel point ce choix peut flatter les résultats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : l'application 7.1 reconstruit la matrice d'interactions, la popularité et le filtrage par contenu pas à pas, et la préparation du cahier présente le protocole d'évaluation.


## 7.1 Données d'interaction et références simples

Avant de chercher à faire du « sur mesure », il faut comprendre ce que contiennent les données d'une boutique, et se donner des **références** : des méthodes si simples que tout modèle sophistiqué devra les battre pour justifier son existence. Cette section pose le vocabulaire, la matrice sur laquelle tout le chapitre repose, et deux premières méthodes : la popularité et le filtrage par contenu.

### 7.1.1 Ce que l'on recommande, et à qui

On appelle **utilisateurs** les clients à qui l'on recommande, et **articles** (*items*) ce que l'on recommande : ici, des produits. Un système de recommandation peut poursuivre deux tâches différentes, que l'on confond souvent.

- **Prédire une note** : « quelle note ce client donnerait-il à ce produit ? ». C'est un problème de régression sur une grandeur observée de temps en temps.
- **Classer** : « quels sont les dix produits à afficher en premier pour ce client ? ». Ce qui compte n'est pas la valeur précise d'un score, mais l'**ordre** : un produit placé en dixième position et un autre en première ne rapportent pas la même chose.

La seconde tâche est celle de la gérante. Une note de 3,9 plutôt que 4,1 n'a aucune importance si les deux produits sont bien classés l'un par rapport à l'autre, alors qu'une liste qui oublie le produit que le client aurait acheté est un échec. Le chapitre est donc organisé autour du **classement** ; la prédiction de notes n'apparaît qu'au cahier.

Le but commercial n'est jamais un score : c'est une conversion plus élevée, un panier plus grand, ou la **découverte** de produits que le client n'aurait pas trouvés seul. Nous verrons en 7.4 que ces objectifs ne se mesurent pas tous avec la même métrique.

### 7.1.2 Retours explicites et implicites

Les signaux dont on dispose sont de deux natures.

- Un retour **explicite** est une opinion exprimée : une note de 1 à 5, un « j'aime ». Il est précieux, mais rare : dans les données de la boutique, seulement un achat sur quatre est accompagné d'une note.
- Un retour **implicite** est un comportement : un achat, un clic, une page consultée. Il est abondant, mais ambigu : acheter un produit ne prouve pas qu'on l'a aimé (c'était peut-être un cadeau), et ne pas l'acheter ne prouve pas qu'on ne l'aimerait pas.

> ⚠️ **L'absence n'est pas un « non ».** Dans la matrice d'achats, une case vide signifie « le client n'a pas acheté ce produit », ce qui mélange trois situations : il ne l'a jamais vu, il l'a vu et n'en veut pas, ou il l'achètera demain. Traiter les cases vides comme des refus est l'erreur la plus fréquente. Elle a deux conséquences que nous retrouverons : en 7.3, on donne aux cases vides un **poids faible** plutôt qu'un poids égal à celui des achats ; en 7.4, on se rappelle qu'un produit recommandé que le client n'a pas acheté **n'est pas forcément une erreur** : l'évaluation sur achats cachés sous-estime la valeur réelle d'un bon classement.

Dans les données de la boutique, la colonne `nb_achats` compte les exemplaires achetés : **un achat sur trois environ** (33 %) concerne plus d'un exemplaire. Nous l'ignorerons dans la suite (un client « a acheté » ou « n'a pas acheté » le produit), ce qui revient à utiliser un signal binaire ; la fin de l'application 7.3 du cahier propose d'exploiter la quantité comme mesure de confiance.

### 7.1.3 La matrice d'interactions

Notons $R$ la matrice dont la ligne $u$ correspond au client $u$, la colonne $i$ au produit $i$, et dont l'entrée vaut $R_{ui}=1$ si le client a acheté le produit, $0$ sinon. Voici un exemple minuscule, que nous garderons pour tous les calculs à la main de la section : 5 clients et 6 produits.

| Client | P1 | P2 | P3 | P4 | P5 | P6 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| U1 | 1 | 1 | 0 | 1 | 0 | 0 |
| U2 | 1 | 0 | 1 | 1 | 0 | 0 |
| U3 | 0 | 1 | 1 | 1 | 1 | 0 |
| U4 | 1 | 1 | 0 | 0 | 0 | 1 |
| U5 | 1 | 0 | 1 | 1 | 1 | 0 |

Lisez la matrice par lignes (ce que chaque client a acheté) ou par colonnes (qui a acheté chaque produit). Le client U1 a acheté P1, P2 et P4. Le produit P4 a été acheté par U1, U2, U3 et U5. Ici plus de la moitié des cases sont remplies (17 sur 30) ; dans la réalité, ce n'est presque jamais le cas.


Sur les données de la boutique, la même matrice a 3 000 lignes et 150 colonnes. On ne la stocke jamais comme un grand tableau plein de zéros, mais en **format creux** : on ne garde que les positions des cases remplies. Le fichier d'achats est justement un tableau « une ligne par achat », que l'on convertit ainsi :

```python
from scipy.sparse import csr_matrix

R = csr_matrix((np.ones(len(inter)), (inter.id_client - 1, inter.id_produit - 1)), shape=(3000, 150))
print(R.shape, R.nnz)   # nombre de cases remplies
```
<!--sortie-->
```text
(3000, 150) 27687
```

Deux régularités frappent immédiatement quand on regarde les marges de la matrice.


![À gauche : nombre de clients ayant acheté chaque produit, du plus au moins acheté (le plus acheté l'a été par plus de mille clients, le moins acheté par une vingtaine). À droite : nombre de produits distincts achetés par client.](figures/ch07-longue-traine.png)

Le produit le plus acheté l'a été par **1 020** clients, le moins acheté par **20** : un rapport de plus de cinquante entre les deux. Les dix premiers produits concentrent à eux seuls **21 %** des achats. Du côté des clients, la médiane est de **8** produits achetés, avec une queue longue (au plus **43**). Cette asymétrie est typique : on parle de **longue traîne**. Elle a deux conséquences : un client a peu d'historique pour apprendre ses goûts, et un produit peu acheté a peu de données pour qu'on le recommande à bon escient.

### 7.1.4 La similarité cosinus

Presque toutes les méthodes de cette section et de la suivante reposent sur une même question : **à quel point deux vecteurs se ressemblent-ils ?** Deux clients sont proches s'ils ont acheté les mêmes produits ; deux produits sont proches s'ils ont été achetés par les mêmes clients. Il faut une mesure.

La **similarité cosinus** entre deux vecteurs $a$ et $b$ est le cosinus de l'angle qu'ils forment :
$$\cos(a,b)=\frac{a\cdot b}{\|a\|\,\|b\|}=\frac{\sum_k a_kb_k}{\sqrt{\sum_k a_k^2}\ \sqrt{\sum_k b_k^2}}.$$
Elle vaut 1 si les deux vecteurs pointent dans la même direction, 0 s'ils sont orthogonaux. Pour des vecteurs d'achats (des 0 et des 1), le calcul se simplifie : si $n_i$ et $n_j$ sont les nombres de clients ayant acheté les produits $i$ et $j$, et $n_{ij}$ le nombre de ceux qui ont acheté **les deux**,
$$\cos(i,j)=\frac{n_{ij}}{\sqrt{n_i\,n_j}}.$$

> 📐 **Pourquoi cette formule.** Le produit scalaire de deux vecteurs binaires compte les positions où les deux valent 1, soit $n_{ij}$. La norme au carré d'un vecteur binaire est son nombre de 1, soit $n_i$. Le numérateur mesure les achats communs ; le dénominateur, $\sqrt{n_in_j}$, est la moyenne géométrique des tailles : il **normalise** pour qu'un produit très vendu ne soit pas automatiquement « proche de tout ».

**À la main.** Reprenons le petit tableau. Les produits P3 et P5 ont été achetés respectivement par $n_3=3$ clients (U2, U3, U5) et $n_5=2$ clients (U3, U5), dont $n_{35}=2$ en commun. Donc
$$\cos(\text{P3},\text{P5})=\frac{2}{\sqrt{3\times2}}=\frac{2}{\sqrt6}\approx0{,}816.$$
À l'inverse, P5 et P6 n'ont aucun acheteur commun : $n_{56}=0$ et la similarité vaut 0.


> 💡 **Cosinus, Jaccard, corrélation.** On rencontre aussi l'indice de **Jaccard** $n_{ij}/(n_i+n_j-n_{ij})$, qui compte la part d'acheteurs communs parmi tous les acheteurs, et la **corrélation** de Pearson, qui centre les vecteurs. Pour des données binaires et creuses, le cosinus est le choix courant : il ignore les zéros communs (deux produits qu'aucun des deux clients n'a achetés ne se « ressemblent » pas), ce que la corrélation ne fait pas.

### 7.1.5 La référence : la popularité

La méthode la plus simple consiste à recommander à tout le monde **les produits les plus achetés**, en retirant à chaque client ceux qu'il a déjà. Elle n'est pas personnalisée (deux clients ayant acheté la même chose reçoivent la même liste) et ne demande aucun apprentissage : un simple comptage.

**À la main.** Dans le petit tableau, les nombres d'acheteurs sont $(4,3,3,4,2,1)$ pour P1 à P6. Le client U1 a acheté P1, P2 et P4 ; il reste P3 (3 acheteurs), P5 (2) et P6 (1). La popularité recommande donc P3, puis P5, puis P6, dans cet ordre.

Pourquoi parler de référence ? Parce que, dans presque tous les catalogues, les produits les plus vendus le sont **pour une raison** : ils plaisent à beaucoup de monde. Un modèle qui n'arrive pas à faire mieux que de montrer ces produits n'a rien appris de personnel sur le client.

Mesurons-la sur les données de la boutique, avec la méthode d'évaluation décrite plus haut : on recommande **10 produits** à chaque client évalué, et on regarde quelle part de ses achats cachés (jeu de validation) figure parmi ces 10. Cette part s'appelle le **rappel@10**. Comme point de repère, une liste **tirée au hasard** donne les résultats suivants.

```text
            précision@10  rappel@10  MAP@10  NDCG@10  au moins un achat retrouvé
au hasard          0.012      0.071   0.024    0.040                       0.119
popularité         0.039      0.241   0.094    0.143                       0.352
contenu            0.020      0.112   0.033    0.059                       0.184
```

Une liste tirée au hasard retrouve **7,1 %** des achats cachés dans ses dix produits ; la popularité en retrouve **24,1 %**, soit **plus de trois fois plus**. Autrement dit, sur ce catalogue, une grande partie de l'information utile tient dans un simple comptage. Ce que la personnalisation pourra apporter s'ajoute à ce socle.

### 7.1.6 Le filtrage par contenu

Le **filtrage par contenu** recommande à un client des produits qui **ressemblent à ceux qu'il a déjà achetés**, en s'appuyant sur les caractéristiques des produits (catégorie, prix, description…) et non sur le comportement des autres clients.

La construction se fait en trois temps. On décrit chaque produit par un vecteur de caractéristiques ; on résume chaque client par un **profil**, la moyenne des vecteurs de ses produits ; on classe les produits par ressemblance (cosinus) avec ce profil.

**À la main, avec une mise en garde.** Décrivons trois produits par un vecteur $(\text{catégorie A},\ \text{catégorie B},\ \text{prix})$, le prix étant exprimé en dizaines d'euros : P1 $=(1,0,2)$, P2 $=(1,0,3)$ et deux candidats, P3 $=(0,1,2{,}5)$ et P4 $=(1,0,2{,}5)$. Un client a acheté P1 et P2 ; son profil est la moyenne, $(1,0,2{,}5)$. Le candidat P4 (même catégorie, même prix moyen) a un cosinus de 1, ce qui est rassurant. Mais le candidat P3, d'une **autre catégorie**, obtient
$$\cos=\frac{0\times1+1\times0+2{,}5\times2{,}5}{\sqrt{1+6{,}25}\ \sqrt{1+6{,}25}}=\frac{6{,}25}{7{,}25}\approx0{,}862.$$
Le résultat est presque aussi élevé que pour le bon candidat : le prix, qui n'est pas à la même échelle que les indicatrices de catégorie, **domine le calcul**.

> ⚠️ **Les échelles comptent.** Le cosinus (comme toute distance) est sensible à l'échelle des variables. Avant de comparer des produits, il faut **mettre les caractéristiques à la même échelle** : ici, centrer et réduire le logarithme du prix. C'est la même idée que la standardisation du chapitre 4 (section 4.1) et de l'ACP (volume II, section 3.1).


Sur les données de la boutique, les caractéristiques disponibles sont pauvres : une catégorie parmi quatre, et un prix. Le résultat, **11,2 %** de rappel@10, se situe entre le hasard (7,1 %) et la popularité (24,1 %) : le contenu apporte un signal, mais bien moins que le comportement collectif. Le filtrage par contenu n'est pourtant pas inutile. Il fonctionne **sans historique d'autres clients**, ce qui en fait la méthode de choix pour un **produit tout neuf** (section 7.4.5), et ses recommandations sont faciles à expliquer (« parce que vous avez acheté un produit de la même catégorie »).

> ✅ **À retenir (7.1).**
> - Recommander, c'est **classer** des produits pour chaque client ; le résultat se juge sur l'ordre, pas sur un score.
> - Les achats sont un retour **implicite** : une case vide n'est pas un refus. La matrice clients × produits est **creuse** et sa « longue traîne » limite l'information disponible.
> - La **similarité cosinus** mesure la ressemblance de deux vecteurs ; pour des achats binaires, $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$. Les caractéristiques doivent être à la même échelle.
> - Deux références à battre : la **popularité** (très solide) et le **contenu** (utile surtout au démarrage à froid).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 (matrice d'interactions, popularité et contenu à la main), exercices 7.1 à 7.3.


## 7.2 Filtrage collaboratif : les méthodes de voisinage

Le filtrage par contenu regarde les **produits**. Le **filtrage collaboratif** regarde le **comportement collectif** : il recommande à un client ce qu'ont acheté des clients qui lui ressemblent, ou des produits qui ressemblent à ce qu'il a déjà acheté, sans jamais avoir besoin de savoir ce qu'est un produit. Cette section présente les méthodes les plus directes, dites de **voisinage**, qui n'ont pas de paramètres à ajuster au sens du chapitre 2 : tout le travail se joue dans la définition de la ressemblance et dans le nombre de voisins retenus.

### 7.2.1 L'intelligence collective

L'idée tient en une phrase : *les gens qui ont aimé les mêmes choses dans le passé aimeront probablement les mêmes choses dans l'avenir*. Elle se décline de deux façons symétriques.

- Les **voisins de clients** (*user-user*) : pour recommander au client $u$, on cherche les $k$ clients dont l'historique ressemble le plus au sien, et on lui propose ce qu'ils ont acheté et qu'il n'a pas encore acheté.
- Les **voisins de produits** (*item-item*) : pour chaque produit candidat, on mesure sa ressemblance avec les produits que $u$ a déjà achetés. Deux produits se ressemblent s'ils sont **achetés par les mêmes clients**.

Dans les deux cas, la ressemblance est la similarité cosinus de la section 7.1.4, appliquée soit aux lignes de la matrice $R$ (les clients), soit à ses colonnes (les produits).

### 7.2.2 Les voisins de clients

**Retours implicites.** Pour des achats binaires, on retient pour chaque client $u$ l'ensemble $N_k(u)$ de ses $k$ voisins les plus proches (au sens du cosinus), puis on attribue à chaque produit $i$ le score
$$\hat s_{ui}=\sum_{v\in N_k(u)}\operatorname{sim}(u,v)\,R_{vi}.$$
Un produit est bien classé s'il a été acheté par beaucoup de voisins, d'autant plus proches de $u$ que leur similarité est élevée. On ne classe que les produits que $u$ n'a pas déjà achetés.

**Retours explicites.** Avec des notes, une difficulté apparaît : certains clients notent toujours haut, d'autres toujours bas. On corrige ce biais en **centrant** les notes sur la moyenne de chaque client, $\bar r_u$, et on prédit
$$\hat r_{ui}=\bar r_u+\frac{\sum_{v\in N(u)}\operatorname{sim}(u,v)\,(r_{vi}-\bar r_v)}{\sum_{v\in N(u)}|\operatorname{sim}(u,v)|}.$$
La note prédite est la moyenne du client plus la moyenne **pondérée** des écarts que ses voisins ont à leur propre moyenne.

**À la main.** Quatre clients ont noté quatre produits (A à D) ; nous voulons prédire la note de $u_1$ pour le produit D.

| Client | A | B | C | D | Moyenne $\bar r$ |
|---|:-:|:-:|:-:|:-:|:-:|
| $u_1$ (cible) | 5 | 3 | 4 | ? | 4,00 |
| $u_2$ | 4 | 2 | 5 | 4 | 3,75 |
| $u_3$ | 2 | 5 | 1 | 2 | 2,50 |
| $u_4$ | 5 | 4 | 4 | 5 | 4,50 |

On mesure la ressemblance sur les produits notés par les deux clients (A, B, C), après centrage. Le vecteur centré de $u_1$ est $(1,-1,0)$, de norme $\sqrt2\approx1{,}414$. Pour $u_2$ : $(0{,}25,-1{,}75,1{,}25)$, de norme $\approx2{,}165$, et le produit scalaire avec $u_1$ vaut $0{,}25+1{,}75=2$, d'où $\operatorname{sim}(u_1,u_2)=\dfrac{2}{1{,}414\times2{,}165}\approx0{,}653$. De même $\operatorname{sim}(u_1,u_3)\approx-0{,}717$ (goûts opposés) et $\operatorname{sim}(u_1,u_4)\approx0{,}816$.

Chacun a noté le produit D ; l'écart de leur note à leur moyenne vaut $+0{,}25$ pour $u_2$, $-0{,}5$ pour $u_3$ et $+0{,}5$ pour $u_4$. La prédiction est donc
$$\hat r_{1D}=4+\frac{0{,}653\times0{,}25+(-0{,}717)\times(-0{,}5)+0{,}816\times0{,}5}{0{,}653+0{,}717+0{,}816}=4+\frac{0{,}930}{2{,}187}\approx4{,}43.$$


Remarquez le rôle de $u_3$ : ses goûts sont opposés à ceux de $u_1$ (similarité négative) et il a mal noté D ; le signe négatif de la similarité transforme cette mauvaise note en un argument **en faveur** de D. En pratique on écarte souvent les voisins de similarité négative, car cette inférence (« il n'aime pas ce que j'aime, donc ce qu'il déteste me plaira ») est fragile.

### 7.2.3 Les voisins de produits

L'approche symétrique raisonne sur les **colonnes**. Notons $I_u$ l'ensemble des produits achetés par $u$. Le score d'un produit candidat $j$ est la somme de ses ressemblances avec les produits de $I_u$ :
$$\hat s_{uj}=\sum_{i\in I_u}\operatorname{sim}(i,j).$$
On peut ne retenir, pour chaque produit $j$, que ses $k$ produits les plus proches (ses **voisins**) ; les autres similarités sont mises à zéro. Matriciellement, en notant $S$ la matrice des similarités entre produits (diagonale nulle), tout le calcul est un produit de matrices : $\hat S=R\,S$.

**À la main.** Reprenons le petit tableau de 7.1.3 (5 clients, 6 produits) et calculons les similarités nécessaires avec $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$. Les nombres d'acheteurs sont $(4,3,3,4,2,1)$. Le client U1, qui a acheté P1, P2 et P4, a trois produits candidats :

- **P3** : $\cos(\text{P3},\text{P1})=\dfrac{2}{\sqrt{12}}=0{,}577$, $\cos(\text{P3},\text{P2})=\dfrac{1}{\sqrt9}=0{,}333$, $\cos(\text{P3},\text{P4})=\dfrac{3}{\sqrt{12}}=0{,}866$. Score : $1{,}777$.
- **P5** : $\dfrac{1}{\sqrt8}=0{,}354$, $\dfrac{1}{\sqrt6}=0{,}408$, $\dfrac{2}{\sqrt8}=0{,}707$. Score : $1{,}469$.
- **P6** : $\dfrac{1}{\sqrt4}=0{,}5$, $\dfrac{1}{\sqrt3}=0{,}577$, $0$. Score : $1{,}077$.

Le classement est P3, P5, P6. Ici, il coïncide avec celui de la popularité ; la personnalisation ne devient visible que sur des historiques plus variés, comme ceux de la boutique.


> 💡 **Pourquoi on préfère souvent les voisins de produits.** Dans une boutique, le catalogue (150 produits) est bien plus petit et plus **stable** que la clientèle (3 000 clients, qui changent d'une semaine à l'autre) : la matrice de similarités entre produits est petite et évolue lentement, on peut donc la calculer à l'avance. Un client n'a de plus que quelques achats, ce qui rend la mesure de sa ressemblance avec les autres clients bruitée, alors que la ressemblance de deux produits s'appuie sur tous les clients qui les ont achetés. Enfin, les recommandations sont faciles à expliquer : « parce que vous avez acheté P1 ».

Voici ce calcul sur les données de la boutique. Une seule fonction de bibliothèque suffit pour la similarité, un produit de matrices pour les scores :


```python
from sklearn.metrics.pairwise import cosine_similarity

S = cosine_similarity(R_train.T)       # similarité entre produits (colonnes de R)
np.fill_diagonal(S, 0)
scores = R_train @ S                   # score du produit j pour le client u : somme des similarités
```


### 7.2.4 Rétrécissement et choix du voisinage

Une similarité calculée sur peu de données est peu fiable. Imaginez deux paires de produits : la paire $a$ a un cosinus de 0,8 obtenu sur seulement $n_{ij}=2$ clients communs ; la paire $b$ a un cosinus de 0,6 obtenu sur 40 clients communs. Laquelle croire ? Plutôt la seconde, malgré sa valeur plus faible, parce que 0,8 sur deux clients peut être une coïncidence.

Le **rétrécissement** (*shrinkage*) traduit cette intuition : on multiplie la similarité par un facteur qui tend vers 0 quand le nombre de co-achats est faible,
$$\operatorname{sim}'(i,j)=\operatorname{sim}(i,j)\times\frac{n_{ij}}{n_{ij}+\lambda},$$
où $\lambda>0$ est un paramètre de prudence. Avec $\lambda=10$, la paire $a$ devient $0{,}8\times\frac{2}{12}\approx0{,}133$ et la paire $b$ devient $0{,}6\times\frac{40}{50}=0{,}48$ : leur ordre s'**inverse**. C'est le même principe que la régularisation du chapitre 2 (section 2.1) : on tire vers zéro les estimations les moins fiables.

Il reste deux réglages : le **nombre de voisins** $k$ (trop petit, on gaspille de l'information ; trop grand, on dilue le signal avec des voisins peu ressemblants) et le coefficient $\lambda$. Ce sont des hyperparamètres : on les choisit sur le **jeu de validation**, jamais sur le jeu de test (chapitre 1, section 1.1 et section 1.5).


![NDCG@10 sur le jeu de validation selon le nombre de voisins retenus. À gauche, voisins de produits pour trois valeurs du rétrécissement ; à droite, voisins de clients. La ligne en tirets est la popularité.](figures/ch07-reglage-voisins.png)

### 7.2.5 Premiers résultats et limites

La figure et la grille donnent plusieurs enseignements.

- **La popularité est battue, mais de peu.** Elle obtient un NDCG@10 de 0,143 (rappel@10 de 24,1 %). Les voisins de produits, bien réglés, atteignent 0,158 (rappel de 25,8 %) et les voisins de clients 0,165 (rappel de 27,2 %).
- **Un voisinage trop étroit fait perdre.** Avec 5 produits voisins seulement, les voisins de produits tombent à 0,141 : **en dessous de la popularité**. Avec 10 voisins de clients, on tombe à 0,099. Le meilleur réglage garde tous les produits (149 voisins) ou 300 clients voisins : avec un catalogue de 150 produits, restreindre le voisinage jette presque toute l'information.
- **Le rétrécissement aide quand le voisinage est étroit, pas quand il est large.** Avec $k=5$ voisins de produits, passer de $\lambda=0$ à $\lambda=10$ fait passer le NDCG de 0,141 à 0,148 ; avec tous les voisins, il n'apporte plus rien (0,158 dans les deux cas). Les paires de produits ont en effet **peu de co-achats** sur l'entraînement (médiane de 3, et 84,5 % des paires en ont moins de 10) : chaque similarité est bruitée, mais le bruit se moyenne quand on additionne les similarités avec tous les produits du client.
- **Au-delà de 300 voisins de clients, on dilue** : le NDCG redescend à 0,157 pour 1 000 voisins.
- **L'écart entre les deux méthodes est petit** (0,006 de NDCG) : le jeu de validation compte 2 365 clients, ce qui ne permet pas de conclure laquelle est meilleure. Nous attendrons l'intervalle de confiance de 7.4.2.

> ⚠️ **Choisir un hyperparamètre sur la validation, puis le juger sur le test.** Les chiffres ci-dessus sont ceux de la **validation**, utilisée pour choisir $k$ et $\lambda$ : ils sont légèrement optimistes (on a gardé le meilleur de plusieurs essais). La comparaison honnête de toutes les méthodes se fera en 7.4.2, sur le jeu de test, avec des modèles réentraînés sur l'entraînement **et** la validation.

**Le coût de calcul.** Les voisins de produits demandent la matrice des similarités entre produits : pour $m$ produits, $m(m-1)/2$ paires, soit 11 175 ici, un calcul instantané. Les voisins de clients demandent les similarités entre clients : pour $n$ clients, $n(n-1)/2$ paires, soit environ 4,5 millions ici (3 000 clients). Pour un site de plusieurs millions de clients, cette matrice ne tient plus en mémoire : on passe à des méthodes de **voisins approchés** ou, plus souvent, à la factorisation de la section 7.3. Le nombre d'opérations pour une matrice creuse dépend de la somme des carrés des tailles d'historique, $\sum_u d_u^2$ pour les voisins de produits, où $d_u$ est le nombre d'achats du client $u$ : un client très actif pèse plus lourd que tous les autres.

**Les limites.** Les méthodes de voisinage sont simples, interprétables et difficiles à battre, mais elles ne **généralisent** pas : deux produits ne sont liés que s'ils ont des clients communs, de sorte qu'un produit peu acheté, ou un client sans historique, restent sans recommandation. Elles suivent aussi la popularité (les produits très achetés ont des voisins nombreux) : nous mesurerons ce biais en 7.4.4. La factorisation matricielle répond à une partie de ces limites en résumant chaque client et chaque produit par quelques facteurs latents.

> ✅ **À retenir (7.2).**
> - Le filtrage collaboratif recommande à partir du **comportement collectif** : voisins de clients (lignes de $R$) ou voisins de produits (colonnes de $R$), avec la similarité cosinus.
> - Pour les achats binaires, $\hat s_{uj}=\sum_{i\in I_u}\operatorname{sim}(i,j)$ ; avec des notes, on **centre** par la moyenne du client.
> - Le **rétrécissement** $n_{ij}/(n_{ij}+\lambda)$ protège des similarités calculées sur peu de co-achats ; $k$ et $\lambda$ se choisissent sur la **validation**.
> - Les voisins de produits sont plus stables et plus faciles à expliquer ; les deux approches ne recommandent rien sans co-achats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.2 (voisins écrits à la main, rétrécissement), exercices 7.4 à 7.6.


## 7.3 Factorisation matricielle

Les méthodes de voisinage ne relient deux produits que s'ils ont des clients **en commun**. La factorisation matricielle fait mieux : elle résume chaque client et chaque produit par un petit nombre de **facteurs latents**, des grandeurs cachées que l'on n'observe pas mais que l'on apprend à partir des achats. Deux produits qui n'ont aucun acheteur commun peuvent alors avoir des facteurs proches, et c'est cela qui permet de généraliser. Ce principe est celui qui a dominé les systèmes de recommandation pendant une décennie ; il s'appuie sur les idées de la décomposition en valeurs singulières (volume I, section 1.1.4) et de la régularisation (section 2.1).

### 7.3.1 L'idée : des facteurs latents

Associons à chaque client $u$ un vecteur $p_u\in\mathbb R^k$ et à chaque produit $i$ un vecteur $q_i\in\mathbb R^k$, avec $k$ petit (quelques unités à quelques dizaines). L'**affinité** prédite entre le client et le produit est leur produit scalaire :
$$\hat r_{ui}=p_u^\top q_i=\sum_{f=1}^kp_{uf}\,q_{if}.$$
On peut imaginer que chaque coordonnée $f$ est un « goût » : le produit $i$ possède plus ou moins ce trait (valeur $q_{if}$), le client y est plus ou moins sensible (valeur $p_{uf}$), et l'affinité additionne les rencontres entre les deux. Rien n'impose de nommer ces goûts : on les laisse émerger.

En notation matricielle, la matrice $R$ ($n$ clients $\times$ $m$ produits) est approchée par un produit de deux matrices plus petites, $R\approx P\,Q^\top$, où $P$ est $n\times k$ et $Q$ est $m\times k$.


![Factorisation matricielle : la grande matrice d'achats est approchée par le produit d'une matrice de facteurs de clients (une ligne par client) et d'une matrice de facteurs de produits (une colonne par produit).](figures/ch07-schema-factorisation.png)

Le gain d'économie est immédiat : au lieu des 450 000 cases de la matrice, on apprend $k(n+m)$ nombres, soit **18 900** pour $k=6$. Surtout, ces nombres sont **partagés** : un produit, quel que soit le client, a le même vecteur $q_i$, appris à partir de tous ses acheteurs.

### 7.3.2 L'objectif : des moindres carrés régularisés

Pour apprendre $P$ et $Q$ à partir de retours **explicites** (des notes), on minimise l'erreur de reconstruction sur les cases **observées** uniquement, notées $\Omega$, avec une pénalité qui retient les vecteurs de devenir démesurés :
$$\min_{P,Q}\ \sum_{(u,i)\in\Omega}\bigl(r_{ui}-p_u^\top q_i\bigr)^2+\lambda\Bigl(\sum_u\|p_u\|^2+\sum_i\|q_i\|^2\Bigr).$$
Les deux termes jouent les rôles que l'on connaît. Le premier mesure l'erreur sur ce que l'on a vu. Le second, la **régularisation de Ridge** du volume II (section 1.5), empêche le surapprentissage : sans lui, avec assez de facteurs, on reproduirait exactement les notes connues et on prédirait n'importe quoi ailleurs (nous en verrons un exemple en 7.3.4).

> 💡 **Pourquoi on n'utilise que les cases observées.** Dans une matrice de notes, une case vide n'est pas un zéro : c'est une note inconnue. Pénaliser l'écart à zéro sur ces cases forcerait le modèle à prédire des notes nulles. L'objectif ne somme donc que sur $\Omega$. Pour des achats (retours implicites), les cases vides ont un statut différent, que traite la section 7.3.5.

### 7.3.3 Deux algorithmes

Le problème n'est pas convexe en $(P,Q)$ simultanément (c'est un produit de deux inconnues), mais il l'est **en chacun des deux séparément**. Deux stratégies en découlent.

**La descente de gradient stochastique (SGD).** On parcourt les notes connues une à une. Pour la note $r_{ui}$ d'erreur $e_{ui}=r_{ui}-p_u^\top q_i$, on déplace les deux vecteurs un peu dans le sens qui réduit l'erreur, avec un pas $\gamma$ :
$$p_u\leftarrow p_u+\gamma\,(e_{ui}\,q_i-\lambda\,p_u),\qquad q_i\leftarrow q_i+\gamma\,(e_{ui}\,p_u-\lambda\,q_i).$$
C'est la descente de gradient du volume I (section 1.3.3), appliquée à un exemple à la fois.

**Les moindres carrés alternés (ALS).** On **fixe** $Q$ : l'objectif devient, pour chaque client $u$, une régression de Ridge de ses notes sur les vecteurs des produits qu'il a notés. Notons $Q_u$ la matrice dont les lignes sont les $q_i$ des produits notés par $u$, et $r_u$ le vecteur de ses notes ; l'annulation du gradient donne la solution **explicite**
$$p_u=\bigl(Q_u^\top Q_u+\lambda I\bigr)^{-1}Q_u^\top r_u.$$
Puis on fixe $P$ et on résout de même pour chaque produit. On **alterne** jusqu'à stabilisation. Chaque étape ne peut que faire baisser l'objectif, donc la suite converge, vers un minimum local (qui dépend de l'initialisation).

> 📐 **Pourquoi la formule.** Pour un client donné, l'objectif en $p_u$ est $\|r_u-Q_up_u\|^2+\lambda\|p_u\|^2$ : exactement une régression de Ridge, dont les équations normales sont $(Q_u^\top Q_u+\lambda I)p_u=Q_u^\top r_u$ (volume II, section 1.5.1). Les $n$ problèmes (un par client) sont **indépendants** : on peut les résoudre en parallèle, ce qui fait la force de l'ALS pour les grands catalogues.

### 7.3.4 Une itération à la main

Prenons quatre clients, quatre produits, onze notes connues et cinq cases vides (symbole « ? »).

| | P1 | P2 | P3 | P4 |
|---|:-:|:-:|:-:|:-:|
| Client 1 | 5 | 3 | ? | 1 |
| Client 2 | 4 | ? | ? | 1 |
| Client 3 | 1 | 1 | ? | 5 |
| Client 4 | ? | 1 | 5 | 4 |

Avec un seul facteur ($k=1$), chaque client et chaque produit est un simple nombre, et la formule d'ALS devient une division. Prenons $\lambda=1$ et initialisons tous les facteurs des produits à $q=(1,1,1,1)$.

**Étape 1 : les clients.** Pour le client 1, qui a noté P1, P2 et P4 (notes $5,3,1$) :
$$p_1=\frac{5\times1+3\times1+1\times1}{(1^2+1^2+1^2)+1}=\frac{9}{4}=2{,}25.$$
De même $p_2=\dfrac{4+1}{2+1}=1{,}667$, $p_3=\dfrac{1+1+5}{3+1}=1{,}75$ et $p_4=\dfrac{1+5+4}{3+1}=2{,}5$. Le terme $+1$ au dénominateur est la régularisation : il tire chaque facteur vers zéro.

**Étape 2 : les produits.** On fixe maintenant $p=(2{,}25;\ 1{,}667;\ 1{,}75;\ 2{,}5)$. Pour le produit P1, noté par les clients 1, 2 et 3 (notes $5,4,1$) :
$$q_1=\frac{5\times2{,}25+4\times1{,}667+1\times1{,}75}{2{,}25^2+1{,}667^2+1{,}75^2+1}=\frac{19{,}67}{11{,}90}\approx1{,}652.$$
On trouve de même $q_2\approx0{,}715$, $q_3\approx1{,}724$ (une seule note, celle du client 4) et $q_4\approx1{,}249$.

**L'objectif baisse.** Après l'étape 1, la somme des erreurs au carré sur les notes connues, plus la pénalité, vaut **59,17** ; après l'étape 2, **47,93**. Une seconde passe sur les clients donne $p\approx(2{,}01;\ 1{,}49;\ 1{,}48;\ 2{,}37)$ et un objectif de **46,91**. Après une centaine d'alternances, il se stabilise à **45,66**.


Un seul facteur ne suffit pas à représenter ce tableau (deux groupes de clients aux goûts opposés : les clients 1 et 2 notent P1 haut et P4 bas, les clients 3 et 4 l'inverse) ; que se passe-t-il avec deux facteurs et presque pas de régularisation ($\lambda=0{,}1$) ? L'erreur sur les notes connues tombe à **0,06**, contre 1,42 avec un seul facteur : le modèle a **recopié** les onze notes. Mais l'une de ses prédictions pour les cases vides est absurde : il prédit **5,87** pour le client 3 et le produit P3, une note supérieure au maximum possible de 5. C'est le surapprentissage en miniature : onze observations pour seize paramètres. Régulariser (et valider !) n'est pas facultatif.

### 7.3.5 Retours implicites : donner aux cases vides un poids faible

Pour des achats, la situation est différente : la matrice ne contient que des 1 (achats) et des cases vides. Si l'on ne somme que sur les achats observés, le modèle apprend à tout prédire à 1 et n'apprend rien. Si l'on traite toutes les cases vides comme des 0 avec le même poids que les achats, on enseigne au modèle que les produits non achetés sont rejetés, ce qui est faux (7.1.2). La solution de **Hu, Koren et Volinsky** (2008) est un compromis : on garde **toutes** les cases, mais on pondère par la **confiance** que l'on a dans chaque observation.

Pour chaque paire $(u,i)$, notons $x_{ui}=1$ si le client a acheté le produit et $0$ sinon, et donnons-lui la confiance
$$c_{ui}=1+\alpha\,R_{ui}.$$
Une case vide a la confiance minimale 1 ; un achat a la confiance $1+\alpha$, avec $\alpha$ de l'ordre de quelques unités. L'objectif devient
$$\min_{P,Q}\ \sum_{u,i}c_{ui}\bigl(x_{ui}-p_u^\top q_i\bigr)^2+\lambda\Bigl(\sum_u\|p_u\|^2+\sum_i\|q_i\|^2\Bigr),$$
avec, pour un client, la solution ALS $p_u=\bigl(Q^\top C_uQ+\lambda I\bigr)^{-1}Q^\top C_ux_u$, où $C_u$ est la matrice diagonale des confiances de $u$. Le calcul paraît lourd (il porte sur tous les produits), mais une astuce le rend rapide : $Q^\top C_uQ=Q^\top Q+\alpha\,Q_u^\top Q_u$, où $Q^\top Q$ est calculé une fois pour tous les clients et $Q_u$ ne contient que les produits **achetés** par $u$.

**À la main.** Un seul facteur ($k=1$), trois produits dont les facteurs sont $q=(1;\ 0{,}5;\ 2)$, un client qui a acheté P1 et P3, $\alpha=4$ (confiance 5 sur les achats) et $\lambda=1$. Le numérateur $\sum c\,x\,q=5\times1+5\times2=15$ ; le dénominateur $\sum c\,q^2+\lambda=5\times1+1\times0{,}25+5\times4+1=26{,}25$. Donc $p_u=15/26{,}25\approx0{,}571$ : les cases vides pèsent dans le dénominateur, mais faiblement.


### 7.3.6 La SVD tronquée comme référence

Il existe une version plus simple, et qui sert de **référence** : la décomposition en valeurs singulières tronquée (volume I, section 1.1.4) de la matrice d'achats. Le théorème d'**Eckart-Young** affirme que la meilleure approximation de rang $k$ de $R$ au sens des moindres carrés est obtenue en gardant les $k$ plus grandes valeurs singulières. Elle s'obtient en une ligne :

```python
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=4, random_state=0)
Z = svd.fit_transform(R_train)         # facteurs des clients
scores = Z @ svd.components_           # reconstruction : score de chaque produit pour chaque client
```

La différence avec l'ALS pondéré est instructive : la SVD traite **toutes les cases vides comme des zéros de même poids que les achats**, et ne régularise pas. Elle approche donc surtout la popularité et se met à surapprendre dès que $k$ grandit.

### 7.3.7 Choisir $k$ et $\lambda$, et ce que valent les facteurs

Il reste à régler le nombre de facteurs $k$, la régularisation $\lambda$ et la confiance $\alpha$ (fixée ici à 8). Comme pour les voisins, le choix se fait sur le jeu de **validation**.


![NDCG@10 sur le jeu de validation selon le nombre de facteurs, pour l'ALS implicite avec trois niveaux de régularisation et pour la SVD tronquée. La ligne en tirets est la popularité.](figures/ch07-reglage-factorisation.png)

Le tableau et la figure se lisent en quatre points.

- **Le meilleur réglage est $k=6$ facteurs et $\lambda=100$** : NDCG@10 de **0,168** (rappel@10 de 27,6 %), contre 0,165 pour les meilleurs voisins de clients, 0,158 pour les voisins de produits et 0,143 pour la popularité. Le gain sur la popularité est réel, mais modeste : 2,5 points de NDCG.
- **Plus de facteurs demandent plus de régularisation.** Avec $\lambda=20$, le NDCG atteint 0,155 pour $k=4$, puis baisse jusqu'à 0,125 pour $k=12$ : c'est le surapprentissage. Avec $\lambda=100$, il reste stable à 0,168 de $k=6$ à $k=12$ : la pénalité maintient en pratique la complexité effective du modèle, quel que soit $k$.
- **Une régularisation trop forte écrase tout.** Avec $\lambda=150$, le NDCG vaut 0,143 pour **toutes** les valeurs de $k$ : exactement celui de la popularité. Les facteurs de personnalisation sont réduits à zéro et il ne reste que la direction « produit populaire ». Le meilleur réglage se situe donc **près d'un précipice**, ce qui rappelle qu'on doit explorer une grille assez large pour voir l'autre côté de l'optimum (l'échelle de $\lambda$ dépend aussi de $\alpha$ et de la taille des données).
- **La SVD tronquée ne fait pas mieux que la popularité.** Son meilleur NDCG (0,143, avec $k=4$) est celui de la popularité, puis il baisse jusqu'à 0,090 pour $k=20$ : sans pondération ni régularisation, elle apprend surtout le bruit.

Que valent les facteurs eux-mêmes ? Projetons les vecteurs des produits appris par le meilleur modèle sur leurs deux directions principales (l'ACP du volume II, section 3.1).


![Les 150 produits projetés sur les deux premières directions de l'espace des facteurs appris par l'ALS, colorés par catégorie. Le modèle ne connaissait pas les catégories : elles se regroupent en partie.](figures/ch07-espace-latent.png)

La projection montre une structure : les produits de la catégorie C se regroupent en haut, ceux de la catégorie A en bas à gauche, ceux de la catégorie B à droite, la catégorie D étant plus diffuse. Les groupes se **recouvrent** pourtant : la dispersion moyenne à l'intérieur d'une catégorie (0,40) est proche de la distance moyenne entre les centres de deux catégories (0,45). Mais la projection en deux dimensions **écrase** l'information : dans l'espace complet des six facteurs, **86 %** des cinq plus proches voisins d'un produit (au sens du cosinus de leurs facteurs) appartiennent à sa catégorie, contre environ 26 % si les voisins étaient tirés au hasard. Les facteurs ne sont donc pas des catégories : ils capturent des goûts qui recoupent largement, mais pas exactement, le rangement du catalogue. (Les données ont été fabriquées avec six facteurs latents, dont les produits d'une même catégorie partagent une part ; le modèle retrouve cette trace sans connaître ni les catégories ni cette vérité.)

> ⚠️ **N'interprétez pas trop les axes.** Les facteurs latents ne sont définis qu'**à une rotation près** : si l'on remplace $P$ par $PA$ et $Q$ par $QA^{-\top}$ pour une matrice inversible $A$, le produit $PQ^\top$ est inchangé (et la pénalité l'est aussi pour une rotation orthogonale). Une direction de l'espace des facteurs n'a donc pas de sens propre ; seules comptent les **distances** et les **produits scalaires**. Nommer un axe « goût pour le traditionnel » est une histoire que l'on se raconte, pas un résultat.

> ✅ **À retenir (7.3).**
> - La factorisation approche $R\approx PQ^\top$ : chaque client et chaque produit reçoit un vecteur de $k$ **facteurs latents**, l'affinité étant leur produit scalaire. Elle **généralise** à des produits sans acheteurs communs.
> - On minimise une erreur de reconstruction **régularisée** (Ridge) par **SGD** ou par **moindres carrés alternés** (chaque étape est une régression de Ridge).
> - Pour des achats, on pondère par la **confiance** : cases vides à poids faible, achats à poids $1+\alpha$.
> - La SVD tronquée est une référence simple, qui traite les cases vides comme des zéros.
> - $k$ et $\lambda$ se règlent sur la validation ; trop de facteurs sans régularisation = surapprentissage.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.3 (ALS implicite écrit à la main) et 7.4 (factorisation sur les notes explicites par SGD), exercices 7.7 à 7.9.


## 7.4 Évaluation et démarrage à froid

Les trois sections précédentes ont comparé des méthodes sur le jeu de validation, avec des métriques annoncées mais pas encore définies. Cette dernière section fait le travail de rigueur qui, depuis le chapitre 1, est le fil rouge du volume : définir précisément ce que l'on mesure, comparer **honnêtement** les méthodes sur le jeu de test, s'interroger sur ce que ces chiffres ne disent pas, et regarder ce qui arrive quand le client ou le produit est **nouveau**.

### 7.4.1 Évaluer un classement

Pour un client donné, un système produit une liste ordonnée de $k$ produits (ici $k=10$). On dispose de l'ensemble des produits **pertinents** pour ce client : ceux qu'il a effectivement achetés et que l'on avait mis de côté (jeu de test). Cinq métriques complémentaires comparent la liste à cet ensemble.

- **Précision@k** : part des $k$ produits recommandés qui sont pertinents. Elle répond à : « combien de ma vitrine sert-elle ? ».
- **Rappel@k** : part des produits pertinents qui figurent dans la liste. Elle répond à : « quelle part de ce que le client voulait ai-je trouvée ? ».
- **Taux de succès@k** (*hit rate*) : part des clients pour lesquels **au moins un** produit pertinent figure dans la liste.
- **MAP@k** (*mean average precision*) : pour chaque client, on moyenne la précision aux rangs où apparaît un produit pertinent, puis on moyenne sur les clients. Elle récompense de **placer les bons produits haut**.
- **NDCG@k** (*normalised discounted cumulative gain*) : on attribue à chaque produit pertinent un gain $1/\log_2(\text{rang}+1)$, qui décroît avec le rang ; on somme (DCG), puis on divise par la valeur maximale possible (IDCG) pour obtenir un nombre entre 0 et 1.

**À la main.** Une liste de $k=5$ produits, dont les deuxième et quatrième sont pertinents ; le client avait en tout **3** produits pertinents dans le jeu de test (le troisième n'a pas été recommandé).

| Rang | 1 | 2 | 3 | 4 | 5 |
|---|:-:|:-:|:-:|:-:|:-:|
| Pertinent ? | non | **oui** | non | **oui** | non |

- Précision@5 $=2/5=0{,}4$ ; rappel@5 $=2/3\approx0{,}667$ ; succès@5 $=1$.
- Précision aux rangs des succès : $1/2$ au rang 2, $2/4$ au rang 4. La précision moyenne (AP) est la somme de ces précisions divisée par le nombre de produits pertinents (borné par $k$), soit $(0{,}5+0{,}5)/3\approx0{,}333$.
- DCG $=\dfrac1{\log_23}+\dfrac1{\log_25}=0{,}631+0{,}431=1{,}062$. Le meilleur classement possible placerait les 3 produits pertinents aux rangs 1, 2 et 3 : IDCG $=1+0{,}631+0{,}5=2{,}131$. Donc NDCG@5 $=1{,}062/2{,}131\approx0{,}498$.


> 💡 **Quelle métrique choisir ?** Cela dépend de l'usage. Si l'on affiche une longue liste que le client parcourt, le **rappel** compte. Si la vitrine ne montre que trois produits, la **précision** et la position (**NDCG**, **MAP**) comptent. Aucune ne remplace la mesure commerciale finale (panier, conversion) : elles ne sont que des indicateurs hors ligne. Dans la suite, nous retenons le **NDCG@10** comme métrique principale et le **rappel@10** comme métrique de lecture facile.

> ⚠️ **Le « faux négatif » de l'évaluation.** Un produit recommandé que le client n'a pas acheté compte comme une erreur, alors qu'il est peut-être un excellent choix qu'il n'avait pas vu. L'évaluation sur achats cachés **sous-estime** donc la qualité réelle de tout système, et pénalise davantage ceux qui recommandent des produits peu connus (7.4.4).

### 7.4.2 Un protocole honnête et des comparaisons avec incertitude

Voici la comparaison finale. Elle suit la discipline du chapitre 1 :

1. les hyperparamètres ont été choisis sur la **validation** (sections 7.2 et 7.3) ;
2. chaque méthode est maintenant **réentraînée sur l'entraînement et la validation réunis** (tout sauf le jeu de test) ;
3. elle est évaluée **une seule fois** sur le jeu de test, qui n'a servi à aucun choix ;
4. chaque métrique est accompagnée d'un **intervalle de confiance** obtenu par bootstrap sur les clients (volume I, section 3.3.5).


```text
            méthode  rappel@10       IC rappel  NDCG@10         IC NDCG
          Au hasard      0.070 [0.063 ; 0.077]    0.044 [0.039 ; 0.048]
         Popularité      0.244 [0.232 ; 0.256]    0.174 [0.165 ; 0.182]
            Contenu      0.122 [0.113 ; 0.130]    0.075 [0.069 ; 0.080]
Voisins de produits      0.270 [0.258 ; 0.282]    0.199 [0.189 ; 0.208]
 Voisins de clients      0.288 [0.275 ; 0.300]    0.209 [0.200 ; 0.218]
       SVD tronquée      0.255 [0.243 ; 0.267]    0.179 [0.171 ; 0.188]
      ALS implicite      0.295 [0.282 ; 0.307]    0.216 [0.206 ; 0.225]
```

```text
                        comparaison  écart NDCG@10          IC 95 %
         ALS implicite − Popularité         0.0420  [0.036 ; 0.048]
    Voisins de clients − Popularité         0.0352  [0.030 ; 0.041]
   Voisins de produits − Popularité         0.0250  [0.018 ; 0.031]
 ALS implicite − Voisins de clients         0.0068  [0.002 ; 0.011]
ALS implicite − Voisins de produits         0.0169  [0.011 ; 0.022]
          SVD tronquée − Popularité         0.0053 [-0.005 ; 0.015]
clients : ALS meilleur 0.391 | égalité 0.446 dont les deux à zéro 0.362 | ALS moins bon 0.163
```


![Performance des sept méthodes sur le jeu de test (2 365 clients) : NDCG@10 à gauche, rappel@10 à droite, avec l'intervalle de confiance à 95 % obtenu par bootstrap sur les clients.](figures/ch07-comparaison-modeles.png)

On y lit quatre choses.

- **Toutes les méthodes personnalisées battent le hasard et la popularité, sauf la SVD tronquée** (NDCG 0,179 contre 0,174 pour la popularité : écart non significatif, voir plus bas).
- **L'ALS implicite est la meilleure** : NDCG@10 de **0,216** (intervalle de confiance [0,206 ; 0,225]) et rappel@10 de **29,5 %**. En moyenne, 0,84 des dix produits recommandés correspond à un achat caché (précision@10 de 0,084), et près de trois achats cachés sur dix sont retrouvés. Les voisins de clients (0,209) et les voisins de produits (0,199) suivent ; la popularité atteint 0,174 (rappel de 24,4 %). Le gain de la meilleure méthode sur la référence est donc de **4 points de NDCG** et de **5 points de rappel** : réel, mais ce n'est pas une révolution.
- **Le contenu seul est loin derrière** (0,075), bien au-dessus du hasard (0,044) mais en dessous de la popularité.
- **Les niveaux du test ne se comparent pas à ceux de la validation** (0,216 contre 0,168 pour l'ALS) : le test cache davantage d'achats par client (6 523 au total contre 3 987), ce qui facilite la tâche, et les modèles sont réentraînés avec 23 % d'achats de plus. Seules les comparaisons entre méthodes **sur un même jeu** ont un sens.

Les intervalles de confiance de deux méthodes peuvent se chevaucher alors que leur **différence** est significative : les deux méthodes sont évaluées sur les **mêmes clients**, et la comparaison est **appariée** (chapitre 1, section 1.4). On calcule donc, client par client, la différence de leur NDCG, puis un intervalle de confiance de la moyenne de cette différence.

Les écarts se lisent ainsi :

- **L'ALS bat nettement la popularité** : $+0{,}042$ de NDCG, avec un intervalle de [0,036 ; 0,048] qui est loin de zéro.
- **L'ALS bat aussi les voisins de clients**, de peu : $+0{,}0068$, intervalle [0,002 ; 0,011]. L'intervalle exclut zéro, donc sur ces données la factorisation est très probablement un peu meilleure ; il faut toutefois nuancer, car ce résultat porte sur **un seul jeu de données** et **une seule initialisation** de l'ALS. En validation, nous n'avions pas pu départager les deux méthodes ; le jeu de test, plus gros, le permet de justesse.
- **La SVD tronquée ne se distingue pas de la popularité** : $+0{,}005$, intervalle [−0,005 ; 0,015] qui contient zéro.
- **L'avantage moyen cache des situations très inégales.** L'ALS fait mieux que la popularité pour **39,1 %** des clients, moins bien pour **16,3 %**, et fait **jeu égal** pour 44,6 %, dont 36,2 points où ni l'une ni l'autre ne retrouve aucun achat. Le gain moyen est le fruit d'un avantage net sur une minorité de clients.

### 7.4.3 Pourquoi un découpage aléatoire peut tromper

Nous avons évalué en retirant des achats **au hasard**, client par client. Dans un vrai projet, les achats ont des dates, et ce découpage pose un problème : le jeu d'entraînement contient des achats **postérieurs** à certains achats du jeu de test. Le modèle « voit l'avenir » : il connaît, par exemple, la popularité qu'aura un produit au moment où on lui demande de la prédire. Le chapitre 1 (section 1.1) l'a dit pour les modèles supervisés ; c'est encore plus net en recommandation, où les goûts et les catalogues changent.

Nos données n'ont pas de dates : nous ne pouvons pas mesurer l'écart. Simulons donc un monde où le temps existe. 2 000 clients et 100 produits, deux périodes ; entre les deux, la popularité de **30 produits** change nettement (certains montent, d'autres chutent). Le but est de prédire les achats de la **seconde** période de produits que le client n'avait pas achetés dans la première. Deux protocoles :

- **découpage aléatoire** : on mélange les deux périodes, on retire 25 % des achats de chaque client au hasard, on entraîne sur le reste ;
- **découpage temporel** : on entraîne sur la première période et on teste sur la seconde.


```text
                     découpage aléatoire  découpage temporel
méthode                                                     
Popularité                         0.328               0.221
Voisins de produits                0.397               0.259
ALS implicite                      0.398               0.260
```

![Rappel@10 de trois méthodes sur un monde simulé où la popularité de 30 produits change entre deux périodes, selon que l'on évalue avec un découpage aléatoire ou un découpage temporel.](figures/ch07-hasard-vs-temps.png)

Le découpage aléatoire **gonfle toutes les performances** : le rappel@10 de la popularité passe de 0,22 (temporel) à 0,33 (aléatoire), soit **48 % de plus** ; celui des voisins de produits de 0,26 à 0,40 (+53 %) et celui de l'ALS de 0,26 à 0,40 (+53 %). Le modèle entraîné sur un mélange des deux périodes connaît déjà les produits devenus populaires pendant la seconde, que le modèle « du passé » ne pouvait pas deviner. Et le découpage aléatoire **exagère aussi l'intérêt de la personnalisation** : l'ALS dépasse la popularité de 0,07 de rappel en évaluation aléatoire, de 0,04 seulement en évaluation temporelle. Le classement des méthodes reste le même (hyperparamètres fixés sans réglage dans cette simulation, une seule simulation).

> ⚠️ **Conséquence pratique.** Avec des données datées, on découpe **toujours dans le temps** : on entraîne sur le passé, on valide sur la période suivante, on teste sur la plus récente. C'est le même principe que la validation des séries temporelles (volume II, section 4.3). Notre évaluation par retrait aléatoire est donc, sur ce jeu sans dates, la meilleure option disponible, mais ses chiffres sont **optimistes en valeur absolue** ; les comparaisons entre méthodes y sont plus fiables que les niveaux.

### 7.4.4 Au-delà de la précision : couverture, nouveauté, biais de popularité

Une méthode qui recommande toujours les mêmes dix produits peut avoir un bon rappel et pourtant décevoir la gérante : le catalogue entier ne bénéficie pas de la vitrine, et les clients ne découvrent rien. Trois indicateurs complètent la précision.

- La **couverture** : part des 150 produits qui apparaissent au moins une fois dans une liste de dix.
- La **nouveauté** : le « degré de surprise » moyen des produits recommandés, mesuré par $-\log_2$ de leur part de popularité ; plus elle est élevée, plus on recommande des produits peu connus.
- La **diversité** d'une liste : part des paires de produits d'une même liste qui appartiennent à des catégories différentes.


```text
            méthode  NDCG@10  couverture  nouveauté (bits)  part des 10 plus populaires  diversité
          Au hasard    0.044       1.000             7.695                        0.058      0.748
         Popularité    0.174       0.160             5.711                        0.827      0.801
            Contenu    0.075       1.000             7.741                        0.048      0.115
Voisins de produits    0.199       0.480             6.016                        0.433      0.614
 Voisins de clients    0.209       0.433             5.909                        0.536      0.704
       SVD tronquée    0.179       0.380             6.176                        0.356      0.577
      ALS implicite    0.216       0.340             5.903                        0.517      0.686
```

Les chiffres appellent quelques remarques.

- **La popularité est la moins variée** : seuls **24 produits sur 150** (16 %) apparaissent dans les listes, **83 %** des emplacements sont occupés par les dix produits les plus vendus, et la nouveauté est la plus basse (5,7 bits).
- **Parmi les méthodes personnalisées, la couverture est de 48 %** pour les voisins de produits, 43 % pour les voisins de clients, 38 % pour la SVD et **34 % pour l'ALS**. Celle qui a la meilleure précision est donc la moins variée de ce groupe : 52 % de ses emplacements sont occupés par les dix produits les plus populaires, contre 43 % pour les voisins de produits.
- **Le contenu couvre tout le catalogue** (100 %) avec la nouveauté la plus élevée (7,7 bits, comparable au hasard), mais sa **diversité** est de 0,12 : ses listes sont presque entièrement de **la même catégorie**, le client est enfermé dans ce qu'il a déjà acheté. C'est la « bulle de filtre ».
- **Le hasard a une couverture parfaite et ne sert à rien** (NDCG de 0,044) : un indicateur de variété ne dit rien de la qualité s'il est lu seul.

> 💡 **Le compromis précision-découverte.** Ces indicateurs vont rarement dans le même sens que la précision. Un système qui améliore la couverture et la nouveauté aide les produits de la longue traîne, mais il prend plus de risques sur chaque recommandation individuelle. Le bon réglage dépend d'un choix commercial (vendre plus aujourd'hui ou élargir les achats de demain) que la donnée seule ne tranche pas.

### 7.4.5 Le démarrage à froid

Toutes les méthodes précédentes ont besoin d'**historique**. Que faire face à un client qui n'a encore rien acheté, ou à un produit qui n'a pas encore été acheté par personne ? C'est le problème du **démarrage à froid** (*cold start*).

**Un nouveau client.** Plaçons-nous du point de vue d'un client dont on ne connaît que $m$ achats. On prend les clients ayant au moins 11 achats, on en met un quart à l'écart comme « nouveaux », on entraîne les modèles sur les autres, et on révèle aux nouveaux clients seulement $m$ de leurs achats (0, 1, 2, 3, 5 ou 8) : le but est de retrouver tous les autres. Pour l'ALS, le facteur d'un nouveau client se calcule en **une seule étape** de la section 7.3 (le *fold-in*), sans réentraîner le modèle. À $m=0$, aucune méthode personnalisée n'a rien à utiliser : elles retombent toutes sur la popularité.


```text
               Popularité  Voisins de produits  ALS implicite
achats connus                                                
0                   0.198                0.198          0.198
1                   0.201                0.197          0.210
2                   0.208                0.237          0.240
3                   0.209                0.259          0.248
5                   0.216                0.269          0.274
8                   0.224                0.293          0.294
```

**Un nouveau produit.** Le problème est plus dur encore : un produit sans acheteur n'a **aucune colonne** utilisable par le filtrage collaboratif, ni par la popularité. Seul le **contenu** (catégorie, prix) peut parler. Pour le mesurer, on retire de l'entraînement les **26 produits récents** (`nouveaute = 1`) ; pour chaque client qui en a acheté, on classe les 26 produits récents à partir de ses **autres achats** et on regarde si ceux qu'il a réellement achetés arrivent en tête. Une liste au hasard retrouverait en moyenne 5/26 $\approx19{,}2$ % des achats parmi ses cinq premiers choix.


```text
                   rappel@5 parmi les 26 nouveaux  AUC par client
Au hasard                                   0.195           0.498
Catégorie seule                             0.296           0.617
Catégorie et prix                           0.290           0.592
```


![À gauche : rappel@10 en fonction du nombre d'achats connus d'un nouveau client, pour trois méthodes. À droite : rappel@5 parmi les 26 produits récents, avec la ligne du hasard.](figures/ch07-demarrage-froid.png)

**Pour un nouveau client**, la courbe de gauche se lit en trois temps.

- Sans aucun achat connu, **toutes les méthodes sont à égalité** (rappel@10 de 19,8 %) : ce sont, par construction, des recommandations de popularité.
- Avec **un seul achat**, l'ALS (21,0 %) dépasse à peine la popularité (20,1 %), et les voisins de produits (19,7 %) font un peu moins bien qu'elle ; sur 250 nouveaux clients, ces écarts ne sont pas mesurables.
- À partir de **deux achats**, l'écart devient net (24,0 % pour l'ALS et 23,7 % pour les voisins de produits, contre 20,8 %) et il atteint 7 points à huit achats (29,4 % et 29,3 % contre 22,4 %). La popularité progresse elle aussi un peu, car les produits déjà connus sont retirés de la liste, ce qui libère des places.

Pratiquement, deux ou trois achats suffisent pour que la personnalisation décolle : d'où l'intérêt d'un parcours d'accueil qui recueille rapidement quelques préférences.

**Pour un nouveau produit**, le contenu fait mieux que le hasard : en classant les 26 produits récents par ressemblance de catégorie avec les achats du client, on retrouve **29,6 %** de ses achats dans les cinq premiers choix (AUC de 0,62), contre 19,5 % pour une liste tirée au hasard (l'espérance est de 5/26, soit 19,2 %). Ajouter le prix **n'apporte rien** (29,0 % ; AUC de 0,59) : sur ces données simulées, le prix n'est en effet lié à aucun goût. Le gain est réel mais modeste : un produit sans historique reste difficile à recommander, et c'est une raison d'**organiser son lancement** (mise en avant volontaire, exploration) plutôt que d'attendre que les ventes le fassent remonter.

### 7.4.6 Les recommandations changent les données

Il reste la limite la plus profonde. Les achats que nous utilisons pour apprendre ne sont pas tombés du ciel : ils ont été **influencés par ce que le site affichait**. Un produit en vitrine est acheté plus souvent *parce qu'il est en vitrine*. Un modèle entraîné sur ces achats apprend, en partie, ce que le modèle précédent montrait. C'est une **boucle de rétroaction**.

Simulons-la. 1 500 clients, 60 produits dont l'attrait réel est connu (nous le programmons). À chaque tour, la vitrine montre 5 produits à chaque client ; il en achète un avec une probabilité qui dépend de son **goût réel** ; la vitrine du tour suivant est recalculée à partir des achats observés. Quatre politiques de vitrine :

1. **les produits les plus vendus** (le classement par popularité de 7.1.5) ;
2. les produits les plus vendus, avec **20 % d'exploration** (un emplacement sur cinq est tiré au hasard) ;
3. le classement par **taux d'achat** (achats divisés par expositions, lissé), avec 20 % d'exploration ;
4. le classement par taux d'achat, sans exploration.


```text
                               part des achats sur 5 produits  produits achetés (sur 60)  corrélation avec l'attrait réel  bons produits en vitrine (sur 5)
ventes seules                                            0.96                      47.25                             0.78                              0.50
ventes + 20 % de hasard                                  0.78                      59.62                             0.82                              0.50
taux d'achat + 20 % de hasard                            0.83                      59.62                             0.94                              4.62
taux d'achat seul                                        0.80                      45.88                             0.99                              4.88
```

![Boucle de rétroaction simulée sur 40 tours (moyenne de 8 simulations) pour quatre politiques de vitrine : corrélation entre les achats observés et l'attrait réel des produits (à gauche) et nombre des cinq meilleurs produits présents en vitrine (à droite).](figures/ch07-boucle-retroaction.png)

Le tableau et les courbes montrent un résultat net.

- **Avec le classement par ventes seules, la boucle se referme** : 96 % des achats se concentrent sur cinq produits, seuls 47 produits sur 60 sont achetés au moins une fois, et **la vitrine ne contient en moyenne que 0,5 des cinq meilleurs produits réels**. Les ventes mesurent ce qu'on a montré, pas ce que les clients aiment.
- **Ajouter 20 % d'exploration ne suffit pas** : on achète alors presque tous les produits (59,6 sur 60), la corrélation avec l'attrait réel passe de 0,78 à 0,82, mais la vitrine ne contient toujours que 0,5 des cinq meilleurs. Le problème n'est pas seulement de montrer plus de produits, c'est de **lire correctement** les ventes.
- **Le classement par taux d'achat** (achats par exposition) corrige cette lecture : la corrélation monte à 0,94 avec exploration et 0,99 sans, et la vitrine contient **4,6 à 4,9 des cinq meilleurs produits**.
- **Sans exploration explicite, la méthode découvre quand même**, mais lentement : le lissage donne à un produit jamais montré un taux optimiste, de sorte que les produits peu convaincants quittent la vitrine. La courbe bleue montre une dizaine de tours pendant lesquels la vitrine ne contient presque aucun bon produit, avant qu'elle ne bascule ; pendant ce temps, seuls 46 produits sur 60 sont achetés.

> ⚠️ **Ce que cela implique en pratique.**
> - Un modèle de recommandation évalué **hors ligne** (comme ici) mesure sa capacité à prédire des achats *influencés par le système précédent*. Seul un **test en conditions réelles** (A/B test, volume II, chapitre 7) mesure l'effet *causal* des recommandations sur les achats.
> - Il faut **réserver de l'exploration** : montrer de temps en temps des produits que le modèle n'aurait pas choisis, pour apprendre ce qu'on ignore.
> - Un produit recommandé n'est pas toujours un produit **en plus** : il peut simplement avoir été acheté à la place d'un autre (cannibalisation). Un bon indicateur est le chiffre d'affaires total, pas la part des ventes qui passent par les recommandations.

> ✅ **À retenir (7.4).**
> - On évalue un **classement** : précision@k, rappel@k, succès@k, MAP@k, NDCG@k ; aucune ne remplace la mesure commerciale.
> - Protocole : hyperparamètres choisis sur la validation, réentraînement sur tout sauf le test, **une seule** évaluation sur le test, **intervalles de confiance** et comparaisons **appariées**.
> - Avec des données datées, **on découpe dans le temps** : un découpage aléatoire fait voir l'avenir au modèle et gonfle les performances.
> - Couverture, nouveauté et diversité complètent la précision ; la popularité est un biais à surveiller.
> - **Démarrage à froid** : sans historique, tout retombe sur la popularité ; le contenu est le seul recours pour un produit nouveau.
> - Les recommandations modifient les achats futurs : prévoir de l'exploration et valider par des tests réels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 (métriques et intervalles de confiance), 7.6 (démarrage à froid), 7.7 (découpage aléatoire contre temporel), 7.8 (boucle de rétroaction) et 7.9 (mélange de méthodes et diversité), exercices 7.10 à 7.12.


## Bilan du chapitre 7

Vous savez maintenant :

- **formuler** un problème de recommandation comme un problème de **classement** (et non de prédiction de notes), distinguer retours **explicites** et **implicites**, et ne pas confondre une case vide avec un refus ;
- manier la **matrice d'interactions creuse** et la **similarité cosinus** (pour des achats binaires, $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$) ;
- construire deux **références** à battre, la **popularité** et le **filtrage par contenu**, et expliquer pourquoi la première est si difficile à dépasser ;
- écrire un **filtrage collaboratif de voisinage** (clients ou produits), le **centrer** quand on dispose de notes, le protéger par **rétrécissement** et en régler le voisinage sur la validation ;
- expliquer la **factorisation matricielle** $R\approx PQ^\top$, son objectif de moindres carrés **régularisés**, les algorithmes **SGD** et **ALS**, la **pondération par la confiance** des retours implicites et la place de la **SVD tronquée** comme référence ;
- **évaluer un classement** avec précision@k, rappel@k, succès@k, MAP@k et NDCG@k, comparer des méthodes avec des **intervalles de confiance appariés**, et regarder au-delà de la précision (**couverture**, **nouveauté**, **diversité**) ;
- reconnaître les pièges propres à la recommandation : le **découpage aléatoire** qui gonfle les résultats quand les données sont datées, le **démarrage à froid** (nouveau client, nouveau produit) et la **boucle de rétroaction** entre recommandations et achats.

Un message à retenir : **sur ce catalogue, une méthode très simple (la popularité) fait déjà presque tout, et la personnalisation n'ajoute que quelques points**, mesurables seulement avec un protocole rigoureux. Le plus souvent, l'essentiel du travail d'un système de recommandation n'est pas l'algorithme, mais la qualité de l'évaluation, la gestion du démarrage à froid et l'exploration qui entretient les données dont il se nourrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.9 et exercices 7.1 à 7.12.

Le chapitre suivant du volume (chapitre 8, également facultatif) retourne le problème : quand les **étiquettes** manquent ou coûtent cher à obtenir, comment apprendre avec peu d'exemples étiquetés, et lesquels demander en priorité ?
