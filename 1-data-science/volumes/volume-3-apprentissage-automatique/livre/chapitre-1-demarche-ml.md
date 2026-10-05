# Chapitre 1 : La démarche d'apprentissage automatique

> « Un modèle qui n'a jamais été testé sur des données neuves n'est pas un modèle : c'est une promesse. »

Les volumes I et II vous ont appris à **comprendre** des données : décrire, estimer, tester, modéliser pour expliquer. Ce volume change de question. On ne cherche plus d'abord *pourquoi* un client part, mais **lequel** partira, afin d'agir à temps : la gérante veut une liste de cent clients à contacter cette semaine. C'est le terrain de l'**apprentissage automatique** (*machine learning*, ML) : construire des modèles dont la qualité se juge à leur capacité de **prédire des cas qu'ils n'ont jamais vus**.

Ce premier chapitre est le plus important du volume, et pourtant il ne contient presque aucun « algorithme à la mode ». Il enseigne la **démarche**, c'est-à-dire la discipline qui sépare un modèle utile d'un modèle qui n'a l'air bon que sur le papier. Les chapitres suivants fourniront les modèles ; celui-ci fournit les règles du jeu. Si vous ne deviez lire qu'un chapitre de ce volume, ce serait celui-ci.

## Le chemin de ce chapitre

- **1.1 Formulation du problème et séparation des données** : qu'est-ce qu'on prédit, avec quelles informations, jugé comment ? Pourquoi on met des données de côté, et le piège numéro un : la **fuite d'information**.
- **1.2 Validation croisée** : exploiter les données au mieux sans tricher, et savoir à quel point l'estimation est incertaine.
- **1.3 Compromis biais-variance et surapprentissage** : pourquoi un modèle trop souple ou trop rigide échoue, démontré proprement.
- **1.4 Modèles de référence et rigueur expérimentale** : battre un modèle simple, comparer deux modèles avec un intervalle d'incertitude, rapporter honnêtement.
- ➕ **1.5 Réglage des hyperparamètres** : grille, recherche aléatoire, optimisation bayésienne avec Optuna, arrêt précoce, et le piège du réglage.

> 📒 **Pour s'entraîner.** Chaque section de ce chapitre renvoie à des applications et à des exercices du **cahier** (chapitre 1). Le livre explique ; le cahier fait pratiquer.

## Les données du chapitre

Presque tout le chapitre s'appuie sur un seul tableau : `clients_ml.csv`, **12 000 clients de la boutique observés au 31 décembre 2025**. Il est **simulé** (graine fixe), comme dans les volumes précédents : la vérité est connue de l'auteur, ce qui permettra à plusieurs reprises de vérifier qu'une méthode fait bien ce qu'elle prétend. La question posée est celle de la gérante : **ce client ne commandera-t-il plus dans les 90 jours qui viennent ?** Cette cible s'appelle `churn_90j` (1 : le client est parti ; 0 : il reste).

| Famille | Variables |
|---|---|
| Profil | `age`, `ville` (20 modalités), `canal_acquisition` (Boutique, Site, Réseaux), `appareil` (parfois manquant), `anciennete_mois` |
| Comportement d'achat | `nb_commandes_12m`, `panier_moyen` (manquant s'il n'y a aucune commande), `montant_12m`, `recence_jours` (jours depuis la dernière commande), `nb_retours_12m`, `part_achats_promo`, `categorie_preferee` |
| Relation | `satisfaction_moy` (manquante pour environ 13 % des clients), `nb_tickets_support_12m`, `programme_fidelite`, `nb_promos_recues_12m`, `taux_ouverture_email`, `delai_livraison_moy` |
| Contexte | `revenu_zone` (indice de la zone de résidence) |
| À prédire | `churn_90j` |

Le tableau contient aussi trois colonnes qui **ne sont pas des variables d'entrée** : `depense_6m` (la dépense future, utilisée dans d'autres chapitres), `segment_vrai` (une classe cachée, utilisée pour valider les méthodes non supervisées) et `commandes_apres_cible`, qui est un **piège volontaire**. Nous le désamorcerons à la section 1.1.6 : retenez seulement, pour l'instant, qu'on ne la donnera jamais au modèle.


Sur les 12 000 clients, **14,0 %** sont partis (environ 1 685) : le problème est **déséquilibré** (nous y reviendrons au chapitre 4), et quatre variables ont des valeurs manquantes, de 12 % à 15 % des clients selon la variable (le panier moyen manque pour 1 630 clients, qui n'ont passé aucune commande). Dans tout le chapitre, deux modèles servent de fil conducteur, volontairement très différents : une **régression logistique** (le modèle du volume II, section 2.2) et un **gradient boosting** (un ensemble d'arbres, étudié en détail à la section 2.4 : ici, on l'utilise comme une boîte performante). Ils jouent le rôle de deux « candidats » à comparer avec rigueur.

> 🧭 **Comment lire ce chapitre.** Le code qui produit les figures et les chiffres cités est **exécuté mais masqué** : le livre ne montre que de courts extraits quand ils aident à comprendre. Les applications complètes, avec tout leur code, sont dans le **cahier**.


## 1.1 Formulation du problème et séparation des données

Avant de choisir un algorithme, un projet d'apprentissage automatique commence par trois décisions qui pèsent plus lourd que n'importe quel hyperparamètre : **ce que l'on prédit** (et pour quelle ligne du tableau), **avec quelles informations** (et à quel moment), et **comment on jugera le résultat**. Cette section pose le cadre mathématique, puis montre pourquoi on met des données de côté et comment une erreur de formulation, la **fuite d'information**, peut faire passer un modèle inutilisable pour un excellent modèle.

### 1.1.1 Un exemple minuscule, entièrement à la main

Huit clients de la boutique, une variable (le nombre de jours depuis la dernière commande), et un modèle qui, pour chaque client, donne une **probabilité de départ** $\hat p$ :

| Client | Récence (jours) | Parti ? ($y$) | Probabilité prédite $\hat p$ |
|---|---:|---:|---:|
| A | 20 | 0 | 0,05 |
| B | 35 | 0 | 0,10 |
| C | 60 | 0 | 0,20 |
| D | 90 | 1 | 0,30 |
| E | 120 | 0 | 0,40 |
| F | 150 | 1 | 0,60 |
| G | 200 | 1 | 0,80 |
| H | 300 | 1 | 0,90 |

Comment dire si ce modèle est bon ? Cela dépend de **ce qu'on appelle « bon »**. Voici trois mesures, calculées à la main.

**Le taux d'erreur.** Prédisons « parti » quand $\hat p>0{,}5$. Le modèle prédit F, G, H comme partis, les autres comme restants. Il se trompe sur D (parti, prédit restant) seulement : 7 bonnes réponses sur 8, soit une **exactitude** de $7/8=0{,}875$.

**La perte logarithmique** (*log-loss*). Elle punit une probabilité confiante et fausse bien plus qu'une probabilité prudente et fausse :
$$\mathrm{LL}=-\frac18\sum_{i=1}^8\bigl[y_i\ln\hat p_i+(1-y_i)\ln(1-\hat p_i)\bigr].$$
Les huit termes $-\ln(\text{probabilité attribuée à ce qui s'est réellement passé})$ valent : A $-\ln0{,}95=0{,}051$ ; B $0{,}105$ ; C $0{,}223$ ; D $-\ln0{,}3=1{,}204$ ; E $-\ln0{,}6=0{,}511$ ; F $-\ln0{,}6=0{,}511$ ; G $0{,}223$ ; H $0{,}105$. Leur somme est $2{,}934$, d'où $\mathrm{LL}=2{,}934/8\approx0{,}367$. Remarquez que **D à lui seul pèse 41 %** du total : le modèle était assez sûr que D resterait (il lui donnait 30 % de risque) et il est parti.

**L'AUC.** C'est la probabilité qu'un client parti, tiré au hasard, ait reçu une probabilité **plus élevée** qu'un client resté tiré au hasard. Il y a $4\times4=16$ paires (parti, resté). Le client D (0,30) bat A, B, C mais pas E : 3 paires gagnées sur 4. F, G et H (0,60 ; 0,80 ; 0,90) battent les quatre clients restés : 12 paires sur 12. Total : $15/16=0{,}9375$.


Trois mesures, trois lectures : 87,5 % de bonnes réponses, une perte de 0,367, une capacité à classer les clients de 0,94. Aucune n'est « la » vérité : elles répondent à des questions différentes (*combien de décisions justes ? les probabilités sont-elles bien dosées ? l'ordre est-il bon ?*). Garder cette idée en tête évite bien des malentendus.

### 1.1.2 Le cadre : prédire, perte, risque

Formalisons. Chaque observation est une paire $(x,y)$ : $x$ regroupe les **variables d'entrée** (les *features*) et $y$ la **cible**. On suppose que ces paires sont tirées indépendamment d'une même loi inconnue $P$. Un **prédicteur** est une fonction $f$ qui associe à $x$ une prédiction $f(x)$. Une **fonction de perte** $\ell(y,f(x))\ge0$ mesure le coût d'une prédiction (erreur au carré, perte logarithmique, erreur 0-1…).

Le **risque** de $f$ est sa perte moyenne **sur la population entière**, c'est-à-dire sur les clients à venir :
$$R(f)=\mathbb E_{(x,y)\sim P}\bigl[\ell(y,f(x))\bigr].$$
On ne peut pas le calculer, puisque $P$ est inconnue. On dispose seulement d'un échantillon $S=\{(x_i,y_i)\}_{i=1}^n$ et du **risque empirique**
$$\widehat R_S(f)=\frac1n\sum_{i=1}^n\ell\bigl(y_i,f(x_i)\bigr).$$
Apprendre, c'est choisir $\hat f$ dans une famille $\mathcal F$ de prédicteurs possibles (les droites, les arbres de profondeur 5, etc.) en minimisant $\widehat R_S$ : c'est la **minimisation du risque empirique**. Ce qui nous intéresse, cependant, est $R(\hat f)$, le risque **sur des clients que le modèle n'a pas vus**. L'écart $R(\hat f)-\widehat R_S(\hat f)$ s'appelle l'**erreur de généralisation**.

> 📐 **Pourquoi l'erreur d'entraînement est optimiste.** Deux faits, faciles à démontrer.
>
> **(1) Si $f$ ne dépend pas de l'échantillon $S$**, alors $\widehat R_S(f)$ est un estimateur **sans biais** de $R(f)$. En effet, par linéarité de l'espérance et parce que chaque $(x_i,y_i)$ suit la loi $P$ :
> $$\mathbb E\bigl[\widehat R_S(f)\bigr]=\frac1n\sum_i\mathbb E\bigl[\ell(y_i,f(x_i))\bigr]=R(f).$$
> C'est la situation d'un **jeu de test** : un prédicteur déjà figé, évalué sur des données qui ne l'ont pas influencé.
>
> **(2) Si $\hat f$ est choisi *en minimisant* $\widehat R_S$**, l'estimateur devient optimiste. Soit $f^\star$ le meilleur prédicteur de la famille au sens du vrai risque ($R(f^\star)\le R(f)$ pour tout $f\in\mathcal F$). Par construction $\widehat R_S(\hat f)\le\widehat R_S(f^\star)$ ; en prenant l'espérance et en utilisant le fait (1) pour le prédicteur **fixe** $f^\star$ :
> $$\mathbb E\bigl[\widehat R_S(\hat f)\bigr]\ \le\ \mathbb E\bigl[\widehat R_S(f^\star)\bigr]=R(f^\star)\ \le\ \mathbb E\bigl[R(\hat f)\bigr].$$
> Donc **en moyenne, l'erreur d'entraînement est inférieure à l'erreur réelle** de $\hat f$. Plus la famille $\mathcal F$ est riche, plus l'écart peut être grand. $\blacksquare$

Voilà la raison d'être de tout ce chapitre : **on ne peut pas juger un modèle sur les données qui ont servi à le construire.** Il faut des données *neuves*, ou des méthodes qui simulent la nouveauté (section 1.2).

### 1.1.3 La perte n'est pas la métrique

Deux notions voisines sont à distinguer, parce qu'on les confond tout le temps :

- La **perte** est ce que l'algorithme **minimise** pendant l'apprentissage. Elle doit être commode : dérivable, convexe si possible (la perte logarithmique pour une régression logistique, l'erreur quadratique pour une régression).
- La **métrique** est ce que l'**utilisateur** veut maximiser dans la vie réelle. Elle peut être discontinue, difficile à optimiser, et dépend du métier : « parmi les cent clients que la gérante appellera cette semaine, combien sont vraiment sur le point de partir ? »

| Question du métier | Perte typique pour l'apprentissage | Métrique de décision |
|---|---|---|
| Quels clients appeler ? | perte logarithmique | précision sur les 100 meilleurs scores |
| Combien de ventes le mois prochain ? | erreur quadratique | erreur moyenne en € (MAE) |
| Cette transaction est-elle frauduleuse ? | perte logarithmique pondérée | coût total des fraudes manquées et des fausses alertes |

Le chapitre 5 détaille les métriques. Retenons ici un **piège élémentaire** : l'exactitude (*accuracy*) trompe quand les classes sont déséquilibrées. Dans notre tableau, 14,0 % des clients partent ; un « modèle » qui répond toujours « il reste » obtient donc **86,0 % d'exactitude** sans rien avoir appris. Un score de 88 % n'a de sens que comparé à ce repère (section 1.4).

### 1.1.4 L'unité d'analyse et le moment de la prédiction

Un projet bien posé répond d'abord à quatre questions simples, que l'on s'oblige à écrire :

1. **Que représente une ligne ?** Ici : *un client, vu à une date donnée*. Ce n'est pas « le client » en général, mais son état au 31 décembre 2025.
2. **À quel moment prédit-on ?** Le modèle sera utilisé le 31 décembre pour décider qui appeler en janvier. La date de prédiction $t_0$ est donc le 31 décembre.
3. **Qu'est-ce qui est connu à $t_0$ ?** Tout ce qui s'est passé **jusqu'à** $t_0$ : l'historique de commandes, les tickets, la satisfaction déclarée. Rien de ce qui se passera après.
4. **Quand la cible est-elle connue ?** Le départ à 90 jours ne se saura que **le 31 mars** : il y a un **délai d'étiquetage**. Pour construire le jeu d'entraînement, on a dû se placer dans le passé, à une date $t_0$ assez ancienne pour que les 90 jours suivants soient écoulés.


![Chronologie d'un problème de prédiction : les variables d'entrée appartiennent au passé de la date de prédiction, la cible est observée pendant les 90 jours suivants et n'est connue que le 31 mars.](figures/ch01-chronologie.png)

> ⚠️ **La question qui évite les catastrophes.** Pour chaque variable d'entrée, demandez-vous : *« à la date où j'utiliserai le modèle, cette valeur existe-t-elle déjà ? »* Si la réponse est « non » ou « pas sûr », la variable est interdite. Cette seule question aurait suffi à éviter la plupart des projets de ML qui échouent au moment du déploiement.

### 1.1.5 Séparer les données : entraînement, validation, test

Comme l'erreur d'entraînement est optimiste (section 1.1.2), on garde de côté des données que le modèle ne verra pas pendant sa construction. On distingue **trois rôles**, qui correspondent à trois questions différentes :

| Jeu | Rôle | Question | Qui l'utilise |
|---|---|---|---|
| **Entraînement** (*train*) | ajuster les paramètres du modèle | « quels coefficients, quels arbres ? » | l'algorithme |
| **Validation** | comparer des modèles, régler les hyperparamètres | « lequel choisir ? » | **vous**, de nombreuses fois |
| **Test** | estimer la performance finale du modèle choisi | « que vaudra-t-il en production ? » | **vous, une seule fois** |

L'analogie qui aide : l'entraînement, ce sont les **exercices** que l'on fait en révisant ; la validation, ce sont les **examens blancs**, que l'on peut passer plusieurs fois pour ajuster sa méthode ; le test est **l'examen final**. Si on regarde le sujet de l'examen final pour adapter sa révision, la note ne mesure plus rien. Dès que le jeu de test a influencé une décision (choisir un modèle, régler un seuil, supprimer une variable), il devient un jeu de validation, et il n'y a plus de jeu de test.

**Comment découper ?** Plusieurs façons, qui ne sont pas interchangeables :

- **Aléatoire**, quand les lignes sont indépendantes : on tire au hasard, par exemple 75 % pour l'entraînement et 25 % pour le test.
- **Stratifié**, quand la cible est rare : on garde la même proportion de clients partis (14 %) dans chaque jeu. Sans cela, un petit jeu de test pourrait n'en contenir que 10 % ou 18 % par hasard.
- **Temporel**, quand le futur doit être prédit à partir du passé : on entraîne sur les périodes anciennes, on teste sur les récentes. Un tirage aléatoire mélangerait passé et futur et serait trop favorable (section 1.2.3).
- **Groupé**, quand plusieurs lignes concernent la même entité (plusieurs commandes d'un même client, plusieurs photos d'un même objet) : toutes les lignes d'une entité vont du même côté, sinon le modèle « reconnaît » l'entité au lieu de généraliser.

Dans tout le chapitre, nous mettons de côté **25 % des clients** (3 000) pour le test final, en conservant la proportion de départs. Le jeu d'entraînement (9 000 clients) sert à toutes les expériences ; le jeu de test ne sera ouvert qu'**une fois**, à la section 1.4.

```python
from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
print(X_tr.shape, X_te.shape, y_tr.mean().round(4), y_te.mean().round(4))
```
<!--sortie-->
```text
(9000, 19) (3000, 19) 0.1404 0.1403
```

Le résultat est : 9 000 clients d'entraînement (14,04 % de départs) et 3 000 clients de test (14,03 %). L'argument `random_state=0` fixe la graine : le même découpage sera obtenu à chaque exécution, condition indispensable pour qu'une expérience soit **reproductible**.

> 💡 **Quelle taille pour le jeu de test ?** Plus il est petit, plus la note finale est incertaine. Pour une exactitude voisine de 0,9 mesurée sur $n$ clients, l'erreur-type est environ $\sqrt{0{,}9\times0{,}1/n}$ : 0,5 point pour $n=3\,000$ mais 1,7 point pour $n=300$ (un intervalle à 95 % est environ deux fois plus large de chaque côté). Sur un problème rare (14 % de positifs), c'est le nombre de **positifs** dans le test qui compte : ici environ 420. Nous mesurerons précisément cette incertitude à la section 1.4.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.3.

### 1.1.6 La fuite d'information

La **fuite d'information** (*data leakage*) désigne toute situation où le modèle, pendant sa construction, a accès à une information qu'il n'aura pas au moment de l'utilisation réelle. C'est la cause la plus fréquente de projets dont les résultats brillants s'effondrent en production. Elle se présente sous plusieurs formes :

- **La fuite par la cible** : une variable d'entrée contient, directement ou indirectement, la réponse (un « motif de résiliation » enregistré *après* le départ).
- **La contamination du jeu de test** : un traitement qui *apprend* des données (calcul d'une moyenne, choix de variables, normalisation) est appliqué **avant** le découpage, sur l'ensemble des données.
- **La fuite temporelle** : on prédit le passé avec le futur (section 1.2.3).
- **Les doublons et les entités partagées** : le même client apparaît des deux côtés du découpage.

**Un cas concret : la colonne `commandes_apres_cible`.** Notre tableau contient le nombre de commandes passées dans les **trois mois suivant** la date de prédiction. Elle semble anodine : c'est un nombre de commandes comme un autre. Ajoutons-la aux variables d'entrée et mesurons la performance par validation croisée (la méthode de la section 1.2).


![À gauche : l'AUC en validation croisée passe de 0,89 à 0,92 quand on ajoute la colonne des commandes futures. À droite : cette colonne devient la variable la plus « importante » du modèle.](figures/ch01-fuite.png)

L'AUC passe de 0,890 à 0,922 : un gain de trois points, qui ferait la joie de n'importe quelle équipe. Et la colonne piège devient la variable la plus importante du modèle (figure de droite). **C'est un mirage.** Le nombre de commandes des trois mois suivants est précisément ce que l'on cherche à prédire : un client qui ne commande plus a, par définition, zéro commande après. Au 31 décembre, cette colonne **n'existe pas encore**. Le modèle « avec » ne peut donc pas être utilisé : appliqué en production, il recevrait des valeurs manquantes ou inventées, et sa performance réelle s'effondrerait à celle du modèle « sans », voire pire (il s'est appuyé sur une information qui n'arrive jamais).

> ⚠️ **Un détecteur de fuite imparfait.** On entend souvent qu'une variable « trop belle » trahit la fuite. Ici, elle est discrète : prise seule, la colonne piège a une AUC de 0,76, au **deuxième rang** sur 16 variables, juste derrière le montant des commandes (0,77) ; rien d'aberrant, et un tri des variables par pouvoir prédictif individuel ne l'aurait pas signalée. Ce qui la trahit, c'est (1) **l'audit du calendrier** (« quand cette valeur est-elle connue ? ») et (2) le **bond** de performance quand on l'ajoute, combiné à son importance démesurée. La fuite par la cible est une faute de **raisonnement**, rarement visible dans les chiffres seuls.

**Un second cas : la contamination par le choix des variables.** Voici une expérience classique. On génère 100 clients fictifs avec 2 000 variables de **pur bruit** et une cible tirée à pile ou face : aucune information à trouver. On retient les 10 variables les mieux corrélées à la cible, puis on estime la performance par validation croisée.


En sélectionnant les variables **sur toutes les données avant** de valider, on obtient une AUC de **0,88** sur un jeu qui ne contient que du bruit. En refaisant la sélection **à l'intérieur de chaque pli** (dans un *pipeline*), on tombe à 0,60, ce qui est, sur 100 observations, la dispersion normale autour du hasard (0,5). La différence entre 0,88 et 0,60 est la mesure de la contamination : les données de validation avaient « voté » pour le choix des variables.

> ✅ **À retenir.**
> - Un modèle se juge sur des données **qu'il n'a pas vues**, parce que l'erreur d'entraînement est en moyenne **optimiste** (démonstration 1.1.2).
> - Une ligne = une unité d'analyse à une **date de prédiction** ; chaque variable doit être **connue à cette date**. L'audit du calendrier est la meilleure défense contre la fuite.
> - Trois rôles : **entraînement** (ajuster), **validation** (choisir, souvent), **test** (évaluer, **une seule fois**).
> - Tout traitement qui *apprend* des données (imputation, normalisation, sélection, encodage cible) fait partie du modèle : il doit être **entraîné sur le jeu d'entraînement seulement**, dans un pipeline.
> - La perte guide l'algorithme, la **métrique** guide la décision ; l'exactitude seule trompe sur les classes déséquilibrées.


## 1.2 Validation croisée

Mettre de côté un jeu de test (section 1.1) protège de l'optimisme, mais coûte cher : ces clients ne participent pas à l'apprentissage, et la note obtenue dépend du **hasard du découpage**. Quand il s'agit de **choisir** entre modèles ou de les régler, on a besoin de nombreuses évaluations fiables. La **validation croisée** est la réponse standard : elle fait servir chaque observation tantôt à l'entraînement, tantôt à la validation, sans jamais mélanger les deux rôles pour une même évaluation.

### 1.2.1 Un seul découpage ne suffit pas

Prenons un petit échantillon de 2 000 clients, et mesurons l'AUC d'une régression logistique sur un jeu de validation de 20 % (400 clients, dont 56 partis). Recommençons **200 fois**, avec 200 découpages aléatoires différents. Le modèle, les données et la métrique sont les mêmes ; seul le hasard du découpage change.


![Distribution de l'AUC d'une même régression logistique sur 200 découpages aléatoires différents d'un échantillon de 2 000 clients.](figures/ch01-decoupage-variabilite.png)

Selon le découpage, l'AUC varie de **0,79 à 0,91**, avec un intervalle central à 95 % de 0,82 à 0,91. Deux analystes qui utilisent des graines différentes pourraient publier des conclusions opposées sur le même modèle, et choisir, entre deux modèles proches, celui que le hasard a favorisé. Un découpage unique est un instrument de mesure **bruité**. Avec 56 clients partis dans le jeu de validation, rien d'étonnant : la mesure s'appuie sur un petit nombre d'événements.

### 1.2.2 La validation croisée à $k$ plis

L'idée : au lieu d'un découpage, on en fait $k$, **de façon systématique**, pour que chaque client serve exactement une fois à la validation.

1. On mélange les données et on les coupe en $k$ parties de taille égale, les **plis** (*folds*).
2. Pour chaque pli $j=1,\dots,k$ : on **entraîne** le modèle sur les $k-1$ autres plis, et on mesure sa perte sur le pli $j$, qui n'a pas servi à l'entraînement.
3. On **moyenne** les $k$ mesures :
$$\mathrm{CV}_k=\frac1k\sum_{j=1}^k\ \frac1{|F_j|}\sum_{i\in F_j}\ell\bigl(y_i,\ \hat f^{(-j)}(x_i)\bigr),$$
où $\hat f^{(-j)}$ est le modèle entraîné **sans** le pli $F_j$.


![Validation croisée à 5 plis : à chaque essai, un pli (orange) sert à la validation et les quatre autres (bleu) à l'entraînement.](figures/ch01-schema-kplis.png)

**Un exemple à la main.** Le cas extrême $k=n$ (chaque observation forme un pli) s'appelle la validation croisée **« un seul laissé de côté »** (*leave-one-out*, LOO). Prenons trois montants de commandes $y=(2;\ 4;\ 9)$ et un « modèle » très simple : prédire la **moyenne des données d'entraînement**. L'erreur sur les données d'entraînement vaut, avec $\bar y=5$ : $\frac{(2-5)^2+(4-5)^2+(9-5)^2}{3}=\frac{26}{3}\approx8{,}67$. Voyons maintenant la validation LOO :

- on retire 2, on prédit avec la moyenne de (4 ; 9), soit 6,5 : erreur $-4{,}5$ ;
- on retire 4, on prédit avec la moyenne de (2 ; 9), soit 5,5 : erreur $-1{,}5$ ;
- on retire 9, on prédit avec la moyenne de (2 ; 4), soit 3 : erreur $6$.

L'erreur quadratique LOO vaut $\frac{20{,}25+2{,}25+36}{3}=19{,}5$, soit **plus du double** de l'erreur d'entraînement (8,67). On voit à l'œuvre l'optimisme de la section 1.1.2. Et il existe ici une jolie formule : si l'on retire $y_i$, la moyenne des autres vaut $\frac{n\bar y-y_i}{n-1}$, donc l'erreur est $y_i-\frac{n\bar y-y_i}{n-1}=\frac{n}{n-1}(y_i-\bar y)$ ; l'erreur LOO est ainsi l'erreur d'entraînement multipliée par $\left(\frac n{n-1}\right)^2=2{,}25$, et $2{,}25\times8{,}67=19{,}5$. (Pour la régression linéaire, il existe de même une formule exacte qui évite de réentraîner $n$ fois : le **PRESS**, vu dans le volume II, section 1.4.)


En pratique, sur les données de la boutique, une validation croisée à 5 plis de la régression logistique tient en trois lignes :

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(modele_logit(), X_tr, y_tr, cv=5, scoring="roc_auc")
print(scores.round(3), scores.mean().round(3))
```
<!--sortie-->
```text
[0.873 0.858 0.87  0.836 0.862] 0.86
```

Les cinq plis donnent des AUC de 0,84 à 0,87 ; l'estimation retenue est leur moyenne, **0,860**. Ici, `cv=5` découpe en cinq plis *stratifiés* (même proportion de départs dans chacun), comportement par défaut pour un classifieur.

> 💡 **Ce que la validation croisée estime vraiment.** Chacun des $k$ modèles est entraîné sur $\frac{k-1}k$ des données ; la moyenne estime donc la performance d'un modèle entraîné sur **un peu moins** de données que le jeu complet. C'est une estimation de la *procédure* d'apprentissage (« entraîner ce type de modèle sur ce volume de données »), pas du modèle final particulier que l'on livrera en réentraînant sur tout.

**Combien de plis ?** Il y a un compromis. Avec peu de plis ($k=2$), chaque modèle voit la moitié des données : il est moins bon que le modèle final, et la validation est **pessimiste** (biais). Avec beaucoup de plis, le biais disparaît, mais les modèles entraînés sont presque identiques, donc les erreurs sont très corrélées, et le calcul coûte $k$ entraînements. Vérifions sur nos données : on tire 10 sous-échantillons de 1 000 clients ; pour chacun, on compare l'estimation par validation croisée à la **vraie performance** du modèle entraîné sur ces 1 000 clients, mesurée sur les 8 000 clients restants.


Avec $k=2$, l'estimation est **pessimiste** de 1 point d'AUC et plus dispersée (écart-type 0,021). À partir de $k=5$, le biais est de l'ordre du millième, plus petit que la dispersion, et augmenter encore $k$ n'apporte rien de mesurable. D'où la règle pratique : **$k=5$ ou $k=10$**. Le « un seul laissé de côté » est surtout réservé aux très petits jeux de données ou aux modèles pour lesquels une formule évite les réentraînements.

### 1.2.3 Les variantes : stratifiée, répétée, groupée, temporelle

Le découpage en plis n'est pas anodin : il doit **reproduire la situation de l'utilisation réelle**. Les variantes suivantes répondent à quatre situations différentes.

| Variante | Quand l'utiliser | Idée |
|---|---|---|
| **Stratifiée** | cible rare ou classes déséquilibrées | même proportion de chaque classe dans chaque pli |
| **Répétée** | jeu de données petit, mesure instable | on refait la validation $m$ fois avec des découpages différents |
| **Groupée** | plusieurs lignes par entité (client, magasin, patient) | toutes les lignes d'une entité sont dans le même pli |
| **Temporelle** | prédire l'avenir à partir du passé | on entraîne sur le passé, on valide sur le futur proche |

**Répétée.** Refaire 5 plis 20 fois (avec 20 découpages différents) réduit le bruit dû au découpage lui-même. Sur nos 9 000 clients, il est déjà minuscule : l'écart-type des moyennes entre répétitions vaut seulement 0,0007 d'AUC. La répétition est utile pour de **petits** jeux de données.


**Groupée.** Supposons qu'on veuille savoir comment le modèle se comportera dans une **ville qu'il n'a jamais vue**. On place alors chaque ville tout entière dans un seul pli.

```python
from sklearn.model_selection import GroupKFold

villes = df.loc[X_tr.index, "ville"]
cv_ville = cross_val_score(modele_logit(), X_tr, y_tr, groups=villes, cv=GroupKFold(5), scoring="roc_auc")
print(cv_ville.mean().round(4))
```
<!--sortie-->
```text
0.8577
```

L'AUC « par ville » (0,858) est à peine inférieure à celle de la validation stratifiée (0,860) : dans nos données, l'effet de la ville est modeste. Dans un jeu où le même **client** apparaît sur plusieurs lignes (plusieurs commandes), la différence serait énorme, car le modèle reconnaîtrait le client plutôt que de généraliser.

**Temporelle.** C'est la variante où l'erreur est la plus courante, et la plus coûteuse. Prenons une série mensuelle simulée sur 11 ans (tendance, saisonnalité, bruit corrélé) et un modèle qui prédit chaque mois à partir des valeurs de 1, 2, 3 et 12 mois plus tôt. Trois estimations de l'erreur (RMSE) :


![Deux façons de découper une série temporelle : plis aléatoires (à gauche, le modèle voit des mois situés après ceux qu'il doit prédire) et plis temporels (à droite, l'entraînement précède toujours la validation).](figures/ch01-schemas-cv.png)

La validation croisée **aléatoire** annonce une erreur de **3,5** : elle est presque deux fois trop optimiste. La validation **temporelle** annonce 7,3, proche de l'erreur réellement observée sur les 24 derniers mois (6,75). La raison est simple : en mélangeant les mois, le modèle s'entraîne sur des mois **voisins** du mois à prédire (le mois d'avant et le mois d'après se ressemblent), ce qu'il ne pourra jamais faire en production, où l'avenir est inconnu. C'est une **fuite temporelle**.

> ⚠️ **Règle de décision.** Avant de choisir une validation croisée, posez la question : *« en production, qu'est-ce qui sera connu de ce qui m'entoure ? »* Si le futur n'est pas connu, la validation doit respecter l'ordre du temps ; si les lignes d'une même entité arrivent ensemble, elles doivent rester ensemble.

### 1.2.4 Quelle confiance accorder à l'estimation ?

La validation croisée donne un **nombre**, pas une certitude. Deux sources de bruit s'y mélangent : le découpage (que la répétition réduit) et, surtout, **l'échantillon lui-même**, c'est-à-dire le fait qu'on ait observé ces 9 000 clients et pas d'autres. La seconde source est la plus importante, et on ne peut pas la réduire par des calculs.

On est tenté de calculer une erreur-type avec les $k$ scores des plis : $\hat\sigma/\sqrt k$. **Ce n'est pas valable.** Les $k$ modèles sont entraînés sur des données qui se recouvrent presque entièrement : les $k$ mesures ne sont pas indépendantes, et la formule suppose qu'elles le sont. Un résultat théorique (Bengio et Grandvalet, 2004) montre même qu'**il n'existe pas d'estimateur sans biais universel** de la variance de la validation croisée. Vérifions numériquement. On découpe nos 9 000 clients en 12 blocs disjoints de 750 ; sur chacun, on fait une validation à 5 plis. Les 12 estimations sont indépendantes : leur dispersion est la **vraie** incertitude d'une validation croisée sur 750 clients.


L'incertitude réelle (écart-type 0,0145) diffère de l'erreur-type « naïve » tirée des plis (0,0215) : ici, cette dernière est trop **pessimiste** ; dans d'autres situations, elle est trop optimiste. Le message est clair : **ne présentez jamais $\hat\sigma/\sqrt k$ comme une barre d'erreur.** Pour comparer deux modèles ou rapporter un intervalle, la section 1.4 présente des outils adaptés (test t corrigé, bootstrap du jeu de test). Retenez surtout un ordre de grandeur : avec quelques centaines à quelques milliers de clients, **des écarts de moins d'un point d'AUC ne sont pas interprétables**.

### 1.2.5 La validation croisée imbriquée : un aperçu

Un dernier piège guette dès qu'on se sert de la validation croisée pour **choisir** : un modèle parmi dix, un hyperparamètre parmi cent. Le meilleur score obtenu est alors lui-même le résultat d'une **sélection**, donc optimiste (c'est exactement l'argument de la démonstration 1.1.2, appliqué à la validation). La parade est la **validation croisée imbriquée** (*nested cross-validation*) :

1. une **boucle externe** découpe les données en plis ; chaque pli externe est un jeu de test provisoire ;
2. pour chaque pli externe, une **boucle interne** (une autre validation croisée sur les données d'entraînement externes seulement) choisit le meilleur modèle ou réglage ;
3. le modèle ainsi choisi est évalué **sur le pli externe**, que la sélection n'a jamais vu ;
4. la moyenne des évaluations externes estime la performance de **toute la procédure** « choisir puis entraîner ».

Le coût est multiplicatif ($k_{\text{ext}}\times k_{\text{int}}\times$ le nombre de candidats), mais c'est le prix d'une estimation honnête. Nous la mettrons en œuvre à la section 1.5, où nous verrons sur un jeu de pur bruit à quel point le réglage peut s'auto-persuader.

> ✅ **À retenir.**
> - Un seul découpage est un instrument **bruité** : sur 400 clients de validation, l'AUC varie de 0,79 à 0,91 selon la graine.
> - La **validation croisée à $k$ plis** utilise chaque observation pour valider exactement une fois ; **$k=5$ ou $10$** est un bon compromis (biais de l'ordre du millième pour $k\ge5$, pessimiste pour $k=2$).
> - Le découpage doit **imiter l'usage réel** : stratifié (classes rares), groupé (entités répétées), **temporel** (prédire l'avenir). Une validation aléatoire sur une série temporelle annonce 3,5 d'erreur au lieu de 7.
> - L'**écart-type entre plis n'est pas une barre d'erreur** : les plis ne sont pas indépendants.
> - Quand la validation croisée sert à **choisir**, son meilleur score est optimiste : on utilise la validation **imbriquée**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 à 1.4, exercices 1.4 à 1.6.


## 1.3 Compromis biais-variance et surapprentissage

Pourquoi un modèle très souple, capable d'épouser les moindres détails des données d'entraînement, prédit-il souvent **moins bien** qu'un modèle plus simple ? Et pourquoi un modèle trop simple échoue-t-il aussi ? Cette section répond par un résultat mathématique d'une grande élégance, la **décomposition biais-variance**, puis le montre à l'œuvre sur un exemple chiffré, sur des polynômes, et sur les données de la boutique.

### 1.3.1 Deux façons de se tromper

Imaginez un tireur à l'arc. Il peut mal viser **systématiquement** du même côté de la cible : ses flèches sont groupées, mais loin du centre. C'est un défaut de **biais**. Il peut aussi avoir la main qui tremble : ses flèches sont réparties autour du centre, sans direction privilégiée, mais très dispersées. C'est un défaut de **variance**. Un bon tireur a peu des deux ; entre deux tireurs mauvais, on ne peut pas dire lequel est « moins mauvais » sans savoir ce qu'on veut.

En apprentissage, la « cible » est la vraie relation $f(x)$ entre les variables d'entrée et ce qu'on prédit. Le « tireur » est **l'algorithme**, qui reçoit un jeu de données d'entraînement $D$ tiré au sort et produit un prédicteur $\hat f_D$. Si on lui donnait un autre jeu de données (d'autres clients, mêmes caractéristiques générales), il produirait un autre prédicteur. Deux questions se posent alors :

- **En moyenne** sur tous les jeux d'entraînement possibles, le prédicteur vise-t-il juste ? Sinon, il a un **biais**.
- D'un jeu à l'autre, le prédicteur change-t-il beaucoup ? Si oui, il a une grande **variance**.

### 1.3.2 Un exemple à la main : estimer une moyenne

Le plus petit exemple possible n'a pas de variables d'entrée. On veut estimer une grandeur inconnue $\mu=2$ (un panier moyen, en dizaines d'euros) à partir de $n=4$ observations de variance $\sigma^2=4$. L'estimateur habituel est la moyenne $\bar y$ : il est **sans biais** (en moyenne il vaut $\mu$) et sa variance est $\sigma^2/n=4/4=1$. Son erreur quadratique moyenne vaut donc $\mathrm{EQM}=\text{biais}^2+\text{variance}=0+1=1$.

Essayons maintenant un estimateur **volontairement biaisé** : $0{,}8\,\bar y$, qui « tire » la moyenne vers zéro.

- Son espérance vaut $0{,}8\mu=1{,}6$ : le **biais** est $1{,}6-2=-0{,}4$, donc $\text{biais}^2=0{,}16$.
- Sa variance vaut $0{,}8^2\times1=0{,}64$.
- Son erreur quadratique moyenne vaut $0{,}16+0{,}64=\mathbf{0{,}80}$.

**L'estimateur biaisé est meilleur que l'estimateur sans biais** (0,80 contre 1). On a accepté un petit biais en échange d'une forte baisse de variance. En général, l'estimateur $c\,\bar y$ a pour erreur $(c-1)^2\mu^2+c^2\sigma^2/n$, minimale pour
$$c^\star=\frac{\mu^2}{\mu^2+\sigma^2/n}=\frac{4}{4+1}=0{,}8.$$
Plus les données sont bruitées ($\sigma^2/n$ grand), plus il faut rétrécir. C'est exactement le principe de la **régularisation** (volume II, section 1.5) : on « tire » les coefficients vers zéro pour réduire la variance.


Une simulation de 400 000 tirages confirme : l'erreur quadratique moyenne vaut 1,00 pour la moyenne et 0,80 pour l'estimateur rétréci.

### 1.3.3 La décomposition biais-variance

Passons au cas général. On observe $y=f(x)+\varepsilon$, où $f$ est la vraie fonction, et $\varepsilon$ un bruit d'espérance nulle et de variance $\sigma^2$, indépendant du jeu d'entraînement $D$. Fixons un point $x$ et considérons la prédiction $\hat f(x)=\hat f_D(x)$, qui est aléatoire parce que $D$ l'est. L'erreur quadratique d'une nouvelle observation $y$ en ce point, **moyennée sur le bruit et sur le choix de $D$**, se décompose ainsi.

> 📐 **Théorème (décomposition biais-variance).**
> $$\mathbb E\bigl[(y-\hat f(x))^2\bigr]\;=\;\underbrace{\sigma^2}_{\text{bruit irréductible}}\;+\;\underbrace{\bigl(\mathbb E[\hat f(x)]-f(x)\bigr)^2}_{\text{biais}^2}\;+\;\underbrace{\mathbb E\bigl[(\hat f(x)-\mathbb E[\hat f(x)])^2\bigr]}_{\text{variance}}.$$
>
> *Démonstration.* Écrivons $y-\hat f=\varepsilon+(f-\hat f)$ et développons le carré :
> $$\mathbb E\bigl[(y-\hat f)^2\bigr]=\mathbb E[\varepsilon^2]+\mathbb E\bigl[(f-\hat f)^2\bigr]+2\,\mathbb E\bigl[\varepsilon\,(f-\hat f)\bigr].$$
> Le premier terme vaut $\sigma^2$. Le dernier est nul : $\varepsilon$ est indépendant de $\hat f$ (qui ne dépend que de $D$) et d'espérance nulle, donc $\mathbb E[\varepsilon(f-\hat f)]=\mathbb E[\varepsilon]\,\mathbb E[f-\hat f]=0$. Pour le terme central, ajoutons et retranchons $\mathbb E[\hat f]$ :
> $$f-\hat f=\bigl(f-\mathbb E[\hat f]\bigr)+\bigl(\mathbb E[\hat f]-\hat f\bigr).$$
> En développant, le double produit contient le facteur $\mathbb E\bigl[\mathbb E[\hat f]-\hat f\bigr]=0$ et disparaît, d'où
> $$\mathbb E\bigl[(f-\hat f)^2\bigr]=\bigl(f-\mathbb E[\hat f]\bigr)^2+\mathbb E\bigl[(\hat f-\mathbb E[\hat f])^2\bigr]=\text{biais}^2+\text{variance}.\quad\blacksquare$$

Trois lectures de cette formule :

1. Le terme $\sigma^2$ est un **plancher** : aucun modèle ne peut faire mieux que le bruit des données (on l'appelle l'erreur de Bayes dans le cas de la classification). Si une équipe annonce une erreur *inférieure* au bruit connu, elle s'est trompée ou a triché (fuite d'information, section 1.1.6).
2. Le biais mesure l'**écart systématique** entre ce que l'algorithme sait représenter et la réalité ; il baisse quand le modèle devient **plus souple**.
3. La variance mesure la **sensibilité** à l'échantillon ; elle augmente quand le modèle devient **plus souple** (plus de paramètres que de données pour les contraindre).

La conséquence est le **compromis biais-variance** : on ne peut pas minimiser les deux en même temps, et le meilleur modèle est un équilibre.

> ⚠️ **Deux précisions.** La décomposition ci-dessus est exacte pour l'**erreur quadratique**. Pour la classification (perte 0-1) il existe des décompositions analogues, mais plus délicates ; l'intuition reste valable. Et dans les modèles modernes très surdimensionnés (grands réseaux de neurones), on observe parfois que l'erreur de test **rebaisse** quand la complexité continue de croître (phénomène de « double descente ») : le compromis classique est un cadre précieux, pas une loi universelle.

### 1.3.4 Voir le compromis : un polynôme de degré croissant

Rendons cela visible. La vraie fonction est $f(x)=\sin(1{,}5\pi x)$ sur $[0;1]$ et le bruit a un écart-type $\sigma=0{,}3$ (donc $\sigma^2=0{,}09$). Un « jeu d'entraînement » contient 30 points tirés au hasard. Pour chaque degré de polynôme de 1 à 7, on **simule 500 jeux d'entraînement**, on ajuste un polynôme à chacun, et on mesure, en 200 points de $[0;1]$, le biais carré moyen et la variance moyenne de la prédiction.


![Biais et variance d'un polynôme de degré croissant. À gauche : 12 ajustements (bleu) de degré 1, 3 et 7 sur des jeux d'entraînement différents, et la vraie fonction (orange). À droite : biais carré, variance et erreur attendue en fonction du degré.](figures/ch01-biais-variance.png)

Les trois panneaux de gauche montrent des **paquets de flèches** : le degré 1 donne toujours à peu près la même droite, mais elle est loin de la courbe (biais fort, variance faible) ; le degré 7 donne des courbes très différentes d'un jeu à l'autre (variance forte) ; le degré 3 épouse bien la courbe, et d'un jeu à l'autre varie peu. À droite, le compromis : le biais s'effondre dès le degré 3, la variance croît, et l'erreur attendue est minimale au **degré 3** (0,111, à comparer au plancher de 0,09). Plus loin, la situation se dégrade vite : la variance dépasse 5 dès le degré 8 et 1 000 dès le degré 9, parce que, avec 30 points, un polynôme de degré 9 peut osciller sauvagement dans les zones sans donnée.

### 1.3.5 Sous-apprentissage, surapprentissage

Le vocabulaire courant désigne les deux extrémités :

- Le **sous-apprentissage** (*underfitting*) : le modèle est **trop rigide** pour représenter la structure des données ; le biais domine. Les erreurs d'entraînement **et** de validation sont élevées.
- Le **surapprentissage** (*overfitting*) : le modèle est **trop souple** ; il a appris le bruit de l'échantillon d'entraînement ; la variance domine. L'erreur d'entraînement est faible, l'erreur de validation beaucoup plus élevée.

Reproduisons cela sur les données de la boutique, avec un arbre de décision dont on fait croître la profondeur (un arbre plus profond pose plus de questions successives : c'est un modèle plus souple ; le chapitre 2 le détaille). Pour chaque profondeur de 1 à 20, on mesure l'AUC sur les données d'entraînement et par validation croisée.


![AUC d'un arbre de décision sur les données d'entraînement (bleu) et en validation croisée (orange) selon sa profondeur : sous-apprentissage à gauche, surapprentissage à droite.](figures/ch01-complexite.png)

C'est la signature classique : l'AUC d'entraînement ne fait que **monter** avec la complexité (elle atteint 1,00 : l'arbre profond a mémorisé tous les clients) ; l'AUC en validation monte, atteint un maximum à la profondeur **4** (0,864), puis **s'effondre** (0,68 à la profondeur 20). Un arbre de profondeur 20 est « parfait » sur ce qu'il a vu et à peine meilleur que le hasard sur ce qu'il n'a pas vu. Le choix de la complexité se lit **sur la courbe de validation**, jamais sur celle d'entraînement.

### 1.3.6 Les courbes d'apprentissage : diagnostiquer son modèle

La courbe précédente fait varier la complexité. Une **courbe d'apprentissage** fait varier la **quantité de données** d'entraînement, et répond à une question de gestionnaire : *« si on collectait deux fois plus de données, cela servirait-il ? »* On entraîne le modèle sur 200, 500, 1 000, 2 000, 4 000 puis 6 000 clients, et on trace l'AUC d'entraînement et de validation.

```python
from sklearn.model_selection import learning_curve

tailles, train, val = learning_curve(modele_logit(), X_tr, y_tr, train_sizes=[200, 1000, 6000], cv=3, scoring="roc_auc")[:3]
print(tailles, train.mean(1).round(3), val.mean(1).round(3))
```
<!--sortie-->
```text
[ 200 1000 6000] [0.935 0.887 0.868] [0.831 0.851 0.86 ]
```


![Courbes d'apprentissage de trois modèles sur les données de la boutique : AUC d'entraînement (bleu) et de validation (orange) selon le nombre de clients utilisés pour l'entraînement.](figures/ch01-courbes-apprentissage.png)

Chaque forme se lit comme un diagnostic :

- **Régression logistique** : les deux courbes **se rejoignent** à un niveau modeste (0,87 et 0,86 avec 6 000 clients). Écart faible, performance plafonnée : le modèle est **trop rigide** (biais). Ajouter des clients n'aidera presque pas ; il faut un modèle plus expressif ou de meilleures variables.
- **Arbre profond** : l'AUC d'entraînement vaut 1,00 dès le départ, celle de validation reste autour de 0,65 à 0,69, même avec beaucoup de données : l'écart est immense (variance). Il faut **contraindre** le modèle (limiter la profondeur, section 1.3.5) ou le moyenner (forêts, chapitre 2).
- **Gradient boosting** : l'AUC d'entraînement est parfaite (1,00) mais **l'AUC de validation continue de monter** avec les données (de 0,83 à 0,89), signe que **plus de données aideraient**. L'écart entre les deux courbes est grand, mais ce n'est pas un défaut ici : ce qui compte est le niveau de la courbe de validation, que le boosting domine nettement.

> 💡 **Le piège de l'écart.** Un grand écart entre entraînement et validation n'est pas, à lui seul, la preuve d'un mauvais modèle : un modèle puissant peut mémoriser l'entraînement et très bien généraliser (c'est le cas du boosting ci-dessus). Ce qu'on regarde, c'est **la validation**, et si elle **progresse** quand on ajoute des données.

### 1.3.7 Que faire quand le modèle ne généralise pas ?

| Diagnostic | Symptôme | Remèdes |
|---|---|---|
| **Biais élevé** (sous-apprentissage) | entraînement et validation tous deux mauvais, courbes qui se rejoignent | modèle plus souple, **meilleures variables** (chapitre 4), moins de régularisation |
| **Variance élevée** (surapprentissage) | entraînement excellent, validation nettement inférieure | **plus de données**, modèle plus simple, **régularisation**, arrêt précoce (section 1.5), **moyenne de modèles** (bagging, chapitre 2) |
| **Bruit irréductible** | tous les modèles plafonnent au même niveau | accepter la limite ; chercher de **nouvelles informations** plutôt qu'un meilleur algorithme |

> ✅ **À retenir.**
> - $\mathbb E[(y-\hat f)^2]=\sigma^2+\text{biais}^2+\text{variance}$ : un plancher de bruit, une erreur systématique, une sensibilité à l'échantillon.
> - Rendre un modèle plus souple **réduit le biais et augmente la variance** ; le meilleur modèle est un **compromis**. Un estimateur légèrement biaisé peut battre un estimateur sans biais (exemple : $0{,}8\bar y$).
> - **Sous-apprentissage** : tout est mauvais. **Surapprentissage** : l'entraînement est excellent, la validation médiocre. On choisit la complexité sur la **courbe de validation**.
> - Une **courbe d'apprentissage** dit si l'on manque de données (la validation monte encore) ou de souplesse (les courbes se rejoignent à un niveau bas).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.7 et 1.8.


## 1.4 Modèles de référence et rigueur expérimentale

Un score n'a de sens que **comparé** à autre chose. « Notre modèle atteint 0,89 d'AUC » ne dit pas si c'est remarquable ou médiocre, et encore moins si l'écart avec le modèle précédent est réel ou imputable au hasard. Cette section donne trois outils de rigueur : les **modèles de référence** (ce qu'il faut battre), les **comparaisons avec incertitude** (de combien bat-on, et est-ce réel ?), et le **protocole de rapport** (comment présenter honnêtement un résultat).

### 1.4.1 Le modèle de référence : l'adversaire à battre

Avant d'entraîner quoi que ce soit de sophistiqué, on construit des **modèles de référence** (*baselines*) très simples, qui fixent le niveau « gratuit ». Un modèle complexe qui ne les bat pas n'a aucune raison d'exister.

| Référence | Principe | Ce qu'elle apprend |
|---|---|---|
| **Naïve** | toujours la classe majoritaire, ou toujours la probabilité moyenne (14 % de départs) | le niveau « sans information » |
| **Règle métier** | un score à partir d'une seule variable évidente (ici : plus la dernière commande est ancienne, plus le client est jugé risqué) | ce qu'un expert obtient sans modèle |
| **Modèle simple** | une régression logistique | ce qu'apporte un modèle linéaire standard, interprétable |
| **Modèle actuel** | ce qui est déjà en production, s'il y en a un | le seuil à franchir pour que le projet serve |

Mesurons-les sur les données d'entraînement par validation croisée à 5 plis, avec quatre métriques : l'AUC, la précision moyenne (aire sous la courbe précision-rappel, qui vaut la prévalence de 14 % pour un modèle sans information), la perte logarithmique et l'exactitude.

```python
from sklearn.dummy import DummyClassifier

naif = cross_val_score(DummyClassifier(strategy="most_frequent"), X_tr, y_tr, cv=5, scoring="accuracy")
print("exactitude du modèle naïf :", naif.mean().round(3))
```
<!--sortie-->
```text
exactitude du modèle naïf : 0.86
```


```text
                         AUC  précision moyenne  perte log.  exactitude
naïf (prévalence)      0.500              0.140       0.406       0.860
règle : récence seule  0.742              0.329         NaN         NaN
régression logistique  0.860              0.564       0.288       0.883
gradient boosting      0.888              0.617       0.270       0.892
```

Trois lectures :

1. Le modèle naïf obtient une exactitude de **0,860** et une AUC de **0,500** : il n'a rien appris et pourtant « se trompe » seulement dans 14 % des cas. Sa perte logarithmique (0,406) est celle d'une pièce biaisée à 14 % : $-[0{,}14\ln0{,}14+0{,}86\ln0{,}86]\approx0{,}406$, ce que l'on peut vérifier à la main.
2. La **règle métier** (la récence seule) donne déjà une AUC de 0,74 : elle capte une partie réelle du signal. C'est le niveau « un analyste avec un tableur ».
3. La régression logistique grimpe à 0,860, le gradient boosting à 0,888. L'exactitude, elle, n'évolue presque pas (0,860 → 0,883 → 0,892) : on voit à nouveau pourquoi **elle est un mauvais juge** sur un problème déséquilibré.

> 💡 **Le bon réflexe.** Présentez toujours un résultat sous la forme « *X, contre Y pour la référence* ». Un gain de 0,03 d'AUC sur une régression logistique peut valoir des milliers d'euros ou rien du tout selon le métier : c'est à la gérante, pas à l'algorithme, de le dire. Mais sans la référence, la question ne peut même pas être posée.

### 1.4.2 Comparer deux modèles : l'écart est-il réel ?

Le gradient boosting bat la régression logistique de 0,03 d'AUC. Mais nous avons vu (section 1.2.4) qu'une validation croisée est bruitée : cet écart est-il **réel**, ou aurait-il pu apparaître par hasard ? Quatre outils, qui répondent à des questions un peu différentes.

**Principe commun : la comparaison appariée.** On évalue les **deux modèles sur les mêmes découpages** et on étudie la **différence** des scores, découpage par découpage. Cela élimine la variabilité commune (un découpage « facile » est facile pour les deux) et ne garde que ce qui sépare réellement les modèles.

**(1) Le test $t$ corrigé (Nadeau et Bengio, 2003).** On répète $J=15$ découpages aléatoires 75 % / 25 % du jeu d'entraînement ($n_1=6\,750$ clients pour entraîner, $n_2=2\,250$ pour valider) et on note l'écart d'AUC $d_j$ à chaque découpage. Le test $t$ habituel traite les $J$ écarts comme **indépendants** : $t=\bar d\big/\sqrt{s_d^2/J}$. C'est faux, parce que les jeux d'entraînement des différents découpages se recouvrent beaucoup : les écarts sont corrélés, la variance de leur moyenne est **sous-estimée**, et les tests concluent trop souvent à une différence. Nadeau et Bengio corrigent la variance en la multipliant par un facteur lié au rapport des tailles :
$$t=\frac{\bar d}{\sqrt{\left(\dfrac1J+\dfrac{n_2}{n_1}\right)s_d^2}},\qquad\text{à comparer à une loi de Student à }J-1\text{ degrés de liberté.}$$
Ici $\frac1J+\frac{n_2}{n_1}=\frac1{15}+\frac{2\,250}{6\,750}=0{,}067+0{,}333=0{,}4$ : la correction multiplie la variance par 6 environ par rapport à la formule naïve ($0{,}4$ au lieu de $1/15=0{,}067$).


Sur nos données : écart moyen d'AUC $\bar d=0{,}030$, écart-type des écarts $s_d=0{,}0065$. Le test naïf donne $t=17{,}7$ (absurdement significatif). Le test corrigé donne **$t=7{,}2$**, encore très significatif, avec un **intervalle de confiance à 95 % de 0,021 à 0,038** pour l'écart d'AUC. Conclusion honnête : le boosting est meilleur que la régression logistique, de **deux à quatre points d'AUC** sur ces données ; ce n'est pas un hasard.

**(2) Le test de McNemar.** Il compare deux **classifieurs** (des décisions, pas des scores) sur le **même** jeu de données. On ne regarde que les clients où les deux modèles **divergent** : $b$ clients où le modèle A est juste et B faux, $c$ clients où A est faux et B juste. Sous l'hypothèse « les deux modèles ont la même précision », ces désaccords se répartissent à pile ou face, et
$$\chi^2=\frac{(|b-c|-1)^2}{b+c}\quad\text{suit approximativement une loi du }\chi^2\text{ à 1 degré de liberté.}$$
Sur un jeu de validation de 2 700 clients, avec la règle « contacter le client si le risque estimé dépasse 25 % » :


Les deux modèles divergent sur $b+c=331$ clients : la régression logistique a raison et le boosting tort pour 120 d'entre eux ; c'est l'inverse pour 211. Si les deux modèles étaient équivalents, on s'attendrait à environ 165 de chaque côté. Le calcul donne $\chi^2=\dfrac{(|120-211|-1)^2}{331}=\dfrac{90^2}{331}=24{,}5$, soit une probabilité critique de l'ordre de $10^{-6}$ : la différence est réelle. (L'exactitude passe de 83,8 % à 87,2 %.)

**(3) Le bootstrap du jeu de validation.** On tire 1 000 jeux de validation « de même taille » **avec remise** parmi les 2 700 clients, et pour chacun on recalcule l'écart d'AUC entre les deux modèles, **sur le même tirage** (appariement). La dispersion de ces 1 000 écarts donne un intervalle de confiance. Ici, l'écart observé est de 0,0235, et l'intervalle à 95 % va de **0,011 à 0,036** : il exclut zéro.

**Quel outil pour quelle question ?**

| Outil | Question | Ce qu'il capture | Limite |
|---|---|---|---|
| Test $t$ corrigé | la **méthode** A est-elle meilleure que B sur ce type de données ? | variabilité due à l'entraînement **et** à l'évaluation | suppose beaucoup de découpages ; approximatif |
| McNemar | deux **décisions** diffèrent-elles ? | variabilité de l'évaluation, à seuil fixé | un seul seuil, ne mesure pas la qualité des scores |
| Bootstrap du jeu d'évaluation | de combien diffèrent les **scores** (AUC, perte…) ? | variabilité due à la **taille** du jeu d'évaluation | **ignore** la variabilité due à l'entraînement |

Aucun n'est « le bon » : on choisit selon la question, et mieux vaut en présenter deux qui concordent. Retenez surtout le geste : **toujours accompagner un écart de performance d'un intervalle**, et ne conclure que si celui-ci exclut une valeur négligeable.

### 1.4.3 Graines, reproductibilité et variabilité

Beaucoup d'algorithmes utilisent le hasard : initialisation, sous-échantillonnage de lignes ou de variables, découpage interne pour l'arrêt précoce. Leur résultat dépend d'une **graine** aléatoire. Mesurons ce que cela change : on entraîne 10 fois le même gradient boosting (avec arrêt précoce, qui tire au sort une partie de validation interne) sur le même jeu d'entraînement, avec 10 graines différentes, et on évalue chaque fois sur le même jeu de validation.


L'AUC varie de 0,881 à 0,890 selon la graine (écart-type 0,0025) : **neuf millièmes d'écart pour un même modèle**. Deux conséquences pratiques :

- Un écart de performance **inférieur à environ 0,005 d'AUC** entre deux modèles aléatoires est dans le bruit des graines : il ne faut pas en tirer de conclusion.
- Pour un résultat publié, on **fixe la graine** (reproductibilité : tout le monde retrouve le même nombre) **et** on rapporte la moyenne et l'écart-type sur plusieurs graines (honnêteté : le nombre n'est pas une constante de la nature).

La reproductibilité demande aussi de **tout consigner** : versions des bibliothèques, découpages (enregistrés, pas retirés au vol), paramètres, et un **pipeline** qui enchaîne le prétraitement et le modèle pour qu'aucune étape ne soit oubliée ou appliquée dans le mauvais ordre.

### 1.4.4 Le jeu de test, une seule fois

Après tout ce travail sur le jeu d'entraînement (comparaisons, validation croisée, graines), il reste à mettre le modèle à l'épreuve du **jeu de test** de 3 000 clients mis de côté à la section 1.1, **une fois**. Le protocole est strict :

1. toutes les décisions (modèle, variables, réglages, seuil) sont prises **avant**, sur l'entraînement et la validation ;
2. on entraîne le modèle final sur **tout le jeu d'entraînement** ;
3. on l'évalue **une seule fois** sur le jeu de test, et on rapporte le résultat **avec son intervalle** (bootstrap du jeu de test) ;
4. on ne modifie plus rien en fonction de ce résultat.


![AUC finale des deux modèles sur le jeu de test (points colorés, avec intervalle de confiance à 95 % par bootstrap), et estimation par validation croisée (losanges gris).](figures/ch01-test-final.png)

Résultat final, sur des clients que personne n'avait regardés : **régression logistique 0,866** (intervalle à 95 % : 0,848 à 0,883) ; **gradient boosting 0,900** (0,883 à 0,914) ; écart de **0,034** (0,022 à 0,046). Les estimations par validation croisée (0,860 et 0,888, losanges gris) tombent bien dans ces intervalles : la démarche a tenu sa promesse. Remarquez la **largeur** des intervalles : malgré 3 000 clients de test, l'AUC n'est connue qu'à ±0,016 près (environ 420 clients partis seulement). Un modèle dont on annonce « 0,8996 » est annoncé avec deux chiffres de trop : « 0,90 ± 0,015 » est la bonne présentation.

> ⚠️ **Si le résultat sur le test vous déçoit.** La tentation est de « retoucher » le modèle et de re-tester. Mais dès qu'un résultat sur le test guide une décision, le test est consommé : on n'a plus d'estimation honnête. Dans une vraie étude, on documente le résultat décevant tel quel, ou bien on met de côté un **nouveau** jeu de test frais.

### 1.4.5 Rapporter honnêtement : une liste de contrôle

Résumons la rigueur du chapitre en une liste, à parcourir avant de présenter un résultat à un collègue ou à la direction.

| Point | Question à se poser | Exemple dans ce chapitre |
|---|---|---|
| **Problème** | quelle est la ligne ? la date de prédiction ? la cible, et quand est-elle connue ? | client au 31/12, départ à 90 jours |
| **Fuite** | chaque variable est-elle connue à la date de prédiction ? le prétraitement est-il dans le pipeline ? | `commandes_apres_cible` exclue |
| **Découpage** | imite-t-il l'usage réel (temps, groupes, strates) ? | 75 % / 25 % stratifié |
| **Référence** | contre quoi se compare-t-on ? | naïf, règle de récence, régression logistique |
| **Métrique** | adaptée au métier ? complétée au-delà de l'exactitude ? | AUC, précision moyenne, perte logarithmique |
| **Incertitude** | intervalle ? écarts testés ? graines multiples ? | bootstrap, test $t$ corrigé, 10 graines |
| **Test** | ouvert une seule fois ? | oui, section 1.4.4 |
| **Limites** | ce que le modèle ne sait pas faire ? | données simulées ; 420 départs dans le test |

> ✅ **À retenir.**
> - Un score se juge contre une **référence** : naïve, règle métier, modèle simple. L'exactitude d'un modèle naïf (0,860) rend ses 0,89 d'AUC éclairants.
> - Comparer deux modèles, c'est comparer **des différences appariées** et leur associer un **intervalle** : test $t$ **corrigé** (le $t$ naïf est trop optimiste : 17,7 au lieu de 7,2), McNemar pour des décisions, bootstrap du jeu d'évaluation pour des scores.
> - Un modèle aléatoire varie avec sa **graine** (écart-type 0,0025 d'AUC ici) : fixez-la, mais rapportez aussi la variabilité.
> - Le **jeu de test** s'ouvre **une fois**, avec son intervalle ; l'AUC d'un jeu de 3 000 clients est connue à ±0,016 près.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.9 et 1.10.


## 1.5 ➕ Pour aller plus loin : le réglage des hyperparamètres

> 🧭 **Section optionnelle.** Elle approfondit un geste que les chapitres suivants pratiquent sans cesse : choisir les réglages d'un modèle. On peut la sauter à la première lecture ; le piège de la section 1.5.5 mérite cependant d'être lu.

Un modèle d'apprentissage automatique a deux sortes de « boutons ». Les premiers sont **appris** à partir des données ; les seconds sont **fixés par vous avant l'apprentissage**. Bien régler les seconds change souvent beaucoup la performance, mais cela se fait avec une méthode, et un piège.

### 1.5.1 Paramètres et hyperparamètres

- Les **paramètres** sont les nombres que l'algorithme **apprend** : les coefficients d'une régression logistique, les questions posées dans les nœuds d'un arbre.
- Les **hyperparamètres** sont les réglages que **vous choisissez** avant l'entraînement et qui gouvernent la souplesse du modèle : la force de la régularisation, la profondeur maximale d'un arbre, la vitesse d'apprentissage d'un boosting. Ils contrôlent le compromis biais-variance de la section 1.3.

| Modèle | Exemples d'hyperparamètres | Effet |
|---|---|---|
| Régression logistique | force de régularisation $C$ | $C$ petit : modèle rigide (biais), $C$ grand : souple (variance) |
| Arbre de décision | profondeur maximale, taille minimale des feuilles | profond : souple |
| Gradient boosting | nombre d'itérations, vitesse d'apprentissage, nombre de feuilles par arbre, régularisation $\ell_2$ | plus d'itérations ou de feuilles : plus souple |

Régler, c'est chercher la combinaison qui **maximise le score de validation** : une fonction coûteuse (chaque évaluation est une validation croisée), sans formule, qu'on ne sait évaluer qu'en l'essayant. C'est de l'**optimisation par boîte noire**.

### 1.5.2 La grille et la recherche aléatoire

La première idée est la **recherche sur grille** (*grid search*) : on liste quelques valeurs pour chaque hyperparamètre et on essaie **toutes les combinaisons**. Trois valeurs pour quatre hyperparamètres, c'est déjà $3^4=81$ combinaisons, multipliées par le nombre de plis : le coût croît **exponentiellement** avec le nombre d'hyperparamètres.

La **recherche aléatoire** (*random search*) tire les combinaisons au hasard dans des intervalles, pour un budget fixé. Bergstra et Bengio (2012) ont montré pourquoi elle est souvent plus efficace : **en pratique, peu d'hyperparamètres comptent vraiment** pour un problème donné, et on ne sait pas lesquels à l'avance. Avec une grille de $3\times3=9$ essais, chaque hyperparamètre n'est testé qu'à **trois valeurs** distinctes ; avec 9 tirages aléatoires, il est testé à **neuf valeurs** distinctes. Si seul l'un des deux compte, la recherche aléatoire a exploré trois fois plus de valeurs de celui-ci.

**Un calcul à la main.** Supposons que 5 % de l'espace des réglages soient « excellents ». Chaque tirage aléatoire tombe dans cette zone avec probabilité $0{,}05$, donc $n$ tirages indépendants **manquent** la zone avec probabilité $0{,}95^n$. La probabilité d'en toucher au moins un est $1-0{,}95^n$ : $0{,}37$ pour $n=9$, et il faut $n=59$ tirages pour atteindre 95 % (car $0{,}95^{59}\approx0{,}05$). **Le budget nécessaire ne dépend pas du nombre d'hyperparamètres** : c'est l'avantage décisif sur la grille.


Essayons sur la prédiction de départ, avec un gradient boosting, sur un sous-échantillon de 5 000 clients (pour rester rapide) et une validation croisée à 3 plis. La grille : trois vitesses d'apprentissage × trois tailles d'arbre = 9 essais.

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

cv = StratifiedKFold(3, shuffle=True, random_state=0)
grille = {"learning_rate": [0.03, 0.1, 0.3], "max_leaf_nodes": [8, 31, 63]}
gs = GridSearchCV(modele_hgb(), grille, cv=cv, scoring="roc_auc").fit(X5, y5)
print(gs.best_params_, round(gs.best_score_, 4))
```
<!--sortie-->
```text
{'learning_rate': 0.03, 'max_leaf_nodes': 8} 0.8975
```


Sur ces données, la grille trouve un réglage à **0,8975** d'AUC (vitesse 0,03, arbres de 8 feuilles) ; les 9 combinaisons s'échelonnent de 0,874 à 0,8975, ce qui montre que **le réglage compte** (jusqu'à 2,3 points). Cinq recherches aléatoires de 9 essais, avec des graines différentes, trouvent entre 0,892 et 0,897 (moyenne 0,895), **sans faire mieux** que la grille. Ce n'est pas un échec de la méthode : avec 9 essais et un espace réduit, la grille s'est trouvée bien placée. L'avantage de l'aléatoire apparaît quand l'espace compte **beaucoup** d'hyperparamètres ou quand on ne sait pas où chercher.

> 💡 **Où se trouve le bon réglage ?** Ici, le meilleur modèle est **simple** (8 feuilles par arbre, apprentissage lent). Rien d'étonnant : le signal se résume à quelques seuils (section 1.3), et un modèle trop souple ajusterait le bruit. Cette observation rejoint la leçon du compromis biais-variance : le bon réglage est celui que la **validation** désigne, pas le plus puissant en apparence.

### 1.5.3 L'optimisation bayésienne : apprendre des essais précédents

La grille et le hasard **n'apprennent rien** de leurs essais : le vingtième tirage ignore que les dix-neuf premiers étaient mauvais dans telle région. L'**optimisation bayésienne** utilise l'historique pour décider où essayer ensuite : on construit un **modèle de substitution** du score de validation en fonction des hyperparamètres (un processus gaussien, ou, dans Optuna, des estimateurs de densité), et on essaie ensuite le point qui semble **le plus prometteur**, en équilibrant *exploitation* (près des bons points connus) et *exploration* (là où l'on ne sait rien).

Le plus répandu dans les bibliothèques actuelles est le **TPE** (*Tree-structured Parzen Estimator*). Son idée tient en trois phrases : on sépare les essais déjà faits en deux groupes, les **bons** (les 25 % meilleurs scores) et les **autres** ; on estime la densité $\ell(x)$ des réglages parmi les bons et la densité $g(x)$ parmi les autres ; on essaie ensuite le réglage $x$ qui **maximise le rapport $\ell(x)/g(x)$**, c'est-à-dire un réglage « typique des bons essais et rare parmi les mauvais ».

```python
import optuna

def objectif(essai):
    p = {"learning_rate": essai.suggest_float("learning_rate", 0.01, 0.5, log=True),
         "max_leaf_nodes": essai.suggest_int("max_leaf_nodes", 4, 128),
         "l2_regularization": essai.suggest_float("l2_regularization", 1e-3, 10, log=True),
         "min_samples_leaf": essai.suggest_int("min_samples_leaf", 5, 100)}
    return cross_val_score(modele_hgb(**p), X5, y5, cv=cv, scoring="roc_auc").mean()

etude = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0))
etude.optimize(objectif, n_trials=30)
print(round(etude.best_value, 4))
```
<!--sortie-->
```text
0.8951
```


![Optimisation de 4 hyperparamètres d'un gradient boosting en 30 essais : meilleur score atteint après chaque essai (traits) et score de chaque essai (points), pour le TPE d'Optuna (bleu) et pour la recherche aléatoire (orange).](figures/ch01-recherche.png)

(Le TPE démarre par 10 essais **aléatoires**, identiques ici à ceux de la recherche aléatoire puisque la graine est la même : c'est pourquoi les dix premiers points de la figure sont confondus.) Les deux méthodes finissent au même niveau : **0,895** pour le TPE, **0,898** pour la recherche aléatoire, un écart de 0,003, dans le bruit de la mesure (section 1.4.3). Dans cette expérience, **le TPE n'a pas fait mieux que le hasard** ; les dix premiers essais des deux méthodes valent la même moyenne (0,886), mais les **dix derniers** du TPE ont une moyenne de 0,893, contre 0,888 pour le hasard : il a bien appris à se concentrer sur les bonnes régions, sans que cela ait suffi, ici, à battre le meilleur tirage du hasard. Ce résultat est un bon exemple d'**honnêteté expérimentale** : on ne peut pas conclure qu'une méthode « plus intelligente » gagne toujours, surtout avec un budget de 30 essais sur 4 hyperparamètres. L'optimisation bayésienne tient surtout ses promesses quand **chaque essai coûte très cher** (réseaux de neurones, grands jeux de données) et que le budget est de l'ordre de quelques dizaines d'essais.

### 1.5.4 L'arrêt précoce

Pour les modèles construits **itération après itération** (boosting, réseaux de neurones), le **nombre d'itérations** est lui-même un hyperparamètre, et un régulateur très efficace : trop peu, le modèle sous-apprend ; trop, il surapprend. L'**arrêt précoce** (*early stopping*) évite d'avoir à le deviner : on met de côté une petite partie des données (15 % ici), on suit la perte sur cette partie à chaque itération, et on **s'arrête quand elle cesse de baisser** pendant un nombre fixé d'itérations (la « patience », ici 10).


![Perte logarithmique d'un gradient boosting sur les données d'entraînement (bleu) et sur la partie de validation interne (orange) selon le nombre d'itérations ; l'arrêt précoce interrompt l'entraînement peu après le minimum de la validation.](figures/ch01-arret-precoce.png)

La perte d'entraînement baisse sans cesse, celle de la validation interne atteint son minimum à l'itération 45 puis cesse de baisser ; l'algorithme s'arrête à l'itération 55 (45 plus la patience de 10), bien avant le maximum de 500. **On a évité de choisir le nombre d'arbres à la main.** Attention cependant : la partie de validation interne est tirée **au hasard**, ce qui rend le nombre d'itérations dépendant de la graine (c'est le phénomène de la section 1.4.3).

### 1.5.5 Le piège du réglage et la validation imbriquée

Voici le piège central de cette section. Chaque fois que l'on essaie une combinaison et qu'on lit son score de validation, on **apprend quelque chose du jeu de validation**. Après des centaines d'essais, le meilleur score est celui d'une combinaison **sélectionnée pour avoir bien marché sur cette validation**, en partie par chance : c'est le biais d'optimisme de la démonstration 1.1.2, appliqué à la sélection d'un réglage.

Mesurons-le dans un cas où l'on connaît la vérité : **il n'y a rien à apprendre**. On prend 150 clients dont on remplace les étiquettes par un tirage à pile ou face, et on règle un arbre de décision (profondeur, taille des feuilles, nombre de variables considérées) par 300 essais aléatoires évalués par validation croisée à 5 plis. On évalue ensuite le réglage retenu sur 1 000 clients « neufs », eux aussi à étiquettes aléatoires.


Le réglage sélectionné annonce une AUC de **0,66** en validation croisée, alors qu'il n'y a **aucun signal** ; sur des données neuves, il tombe à **0,53**, le hasard. Les 0,13 de différence mesurent l'auto-persuasion de la recherche : avec 300 essais, l'un d'eux a forcément eu de la chance. La parade est la **validation croisée imbriquée** (section 1.2.5) : la recherche d'hyperparamètres est refaite **à l'intérieur** de chaque pli d'une validation externe, et le score est mesuré sur le pli externe, que la recherche n'a jamais vu.

Le même calcul, **imbriqué**, pour 30 essais par recherche interne (`Xa` et `ya_` désignent les 150 clients aux étiquettes aléatoires) :

```python
recherche = RandomizedSearchCV(DecisionTreeClassifier(random_state=0), dist_arbre, n_iter=30, cv=3, scoring="roc_auc", random_state=0)
imbrique = cross_val_score(recherche, Xa, ya_, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc")
print("validation imbriquée :", imbrique.mean().round(3))
```
<!--sortie-->
```text
validation imbriquée : 0.483
```

La validation imbriquée donne **0,48** : elle voit juste (pas de signal, donc le hasard). Elle estime la performance de la **procédure complète** « régler, puis entraîner », et c'est cette procédure qu'il faut évaluer.

> ⚠️ **Règles pour un réglage honnête.**
> - Le **jeu de test** (section 1.1) ne sert **jamais** au réglage.
> - Limitez la **taille de la recherche** : plus on essaie de combinaisons sur peu de données, plus l'optimisme grandit. Ici, 300 essais sur 150 clients ; sur 9 000 clients et 30 essais, l'effet est bien plus faible.
> - Quand l'estimation honnête de la performance compte (publication, décision d'investissement), utilisez la validation **imbriquée**.
> - Après le réglage, **réentraînez** le modèle final avec les meilleurs hyperparamètres sur toutes les données d'entraînement.

> ✅ **À retenir.**
> - Les **hyperparamètres** sont fixés avant l'apprentissage et pilotent le compromis biais-variance ; on les règle par le score de **validation**.
> - La **recherche aléatoire** coûte un budget fixe, quel que soit le nombre d'hyperparamètres ($1-0{,}95^n$ chances de toucher une zone excellente de 5 %) ; la grille croît exponentiellement.
> - L'**optimisation bayésienne** (TPE, Optuna) exploite l'historique des essais : utile quand chaque essai coûte cher, **sans garantie** de gagner (ici : 0,895 contre 0,898 pour le hasard).
> - L'**arrêt précoce** choisit le nombre d'itérations d'un modèle itératif en surveillant une validation interne.
> - Le meilleur score d'une recherche est **optimiste** : sur du bruit pur, 0,66 annoncé pour 0,53 réel. Seule la validation **imbriquée** estime honnêtement la procédure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.8 et 1.9, exercices 1.11 et 1.12.


## Bilan du chapitre 1

Vous savez maintenant :

- **formuler** un problème d'apprentissage : la ligne du tableau, la **date de prédiction**, la cible et le moment où elle est connue ; distinguer la **perte** que l'algorithme minimise de la **métrique** qui guide la décision ;
- **démontrer** pourquoi l'erreur d'entraînement est optimiste, et **séparer les données** en trois rôles (entraînement, validation, test) selon un schéma adapté (aléatoire, stratifié, groupé, temporel) ;
- **repérer et éviter la fuite d'information** : variable connue après la date de prédiction (le mirage de 0,89 à 0,92 d'AUC), prétraitement ou sélection de variables hors du pipeline (0,88 d'AUC sur du pur bruit) ;
- **estimer** une performance par **validation croisée** : choisir $k$ (5 ou 10), la stratifier, la grouper ou la rendre temporelle, et savoir que l'**écart-type entre plis n'est pas une barre d'erreur** ;
- **décomposer** l'erreur en bruit, biais carré et variance, **diagnostiquer** sous-apprentissage et surapprentissage sur une courbe de complexité et une **courbe d'apprentissage**, et en tirer les remèdes ;
- **se comparer à une référence** (naïve, règle métier, modèle simple), **comparer deux modèles avec un intervalle** (test $t$ corrigé, McNemar, bootstrap), tenir compte de la variabilité des graines, et n'ouvrir le jeu de test qu'**une fois** ;
- (en option) **régler des hyperparamètres** (grille, recherche aléatoire, TPE avec Optuna, arrêt précoce) **sans s'auto-persuader**, grâce à la validation croisée imbriquée.

Le fil conducteur du chapitre tient en une phrase : **un modèle vaut ce que vaut la façon dont on l'a évalué**. Sur un même jeu de données, on peut annoncer 0,92 ou 0,89 d'AUC (fuite ou pas), 3,5 ou 7 d'erreur (validation aléatoire ou temporelle), 0,66 ou 0,53 (réglage optimiste ou honnête) : la différence n'est pas dans le modèle, mais dans la **discipline**.

Le chapitre 2 apporte les modèles : de la régression logistique revue comme un problème d'optimisation aux **arbres**, aux **forêts aléatoires** et au **gradient boosting**, qui s'est imposé comme la référence sur les tableaux de données. Chacun sera évalué avec les règles de ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.9 (fuite d'information, loterie du découpage, choix de $k$, série temporelle, biais-variance, courbes d'apprentissage, comparaison rigoureuse, recherche d'hyperparamètres, validation imbriquée) et exercices 1.1 à 1.12.
