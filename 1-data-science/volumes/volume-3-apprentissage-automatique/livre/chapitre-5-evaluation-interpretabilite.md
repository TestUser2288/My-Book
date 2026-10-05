# Chapitre 5 : Évaluation, calibration et interprétabilité

> « Un modèle qui prédit bien ne vaut rien tant qu'on ne sait pas dire *à quel point*, *pour quelle décision* et *pourquoi*. »

Les quatre chapitres précédents ont appris à **construire** des modèles : séparer les données, valider, comparer des familles d'algorithmes, préparer les variables. Il reste l'essentiel : savoir ce que valent ces modèles une fois qu'on les a. Trois questions, qui reviennent à chaque projet, structurent ce chapitre.

1. **Est-il bon ?** Mais bon *pour quoi faire* ? Une exactitude de 90 % peut cacher un modèle inutile ; une AUC de 0,90 peut cacher un modèle mal réglé. Choisir la bonne mesure, et le bon seuil de décision, est un acte de métier avant d'être un acte statistique.
2. **Peut-on se fier à ses probabilités ?** Quand le modèle annonce « 30 % de risque de départ », se passe-t-il vraiment quelque chose environ trois fois sur dix ? C'est la **calibration**, condition de toute décision fondée sur un coût attendu.
3. **Pourquoi dit-il cela ?** Un modèle qui prédit sans que personne ne puisse l'expliquer est un modèle difficile à corriger, à défendre, ou à débusquer quand il triche. C'est l'**interprétabilité**.

## Le chemin de ce chapitre

- **5.1 Métriques** : de la matrice de confusion à la courbe ROC, à la courbe précision-rappel, aux coûts, au lift ; les métriques de régression.
- **5.2 Calibration** : le diagramme de fiabilité, pourquoi certains modèles mentent sur leurs probabilités, Platt, la régression isotonique, et l'effet des poids de classes.
- **5.3 Interprétabilité** : importance par permutation, effets partiels, LIME, et les valeurs de Shapley avec SHAP.
- ➕ **5.4 Équité, biais et éthique** : mesurer les écarts entre groupes sur un jeu **réel** de crédit, et ce que l'on ne peut pas avoir en même temps.
- ➕ **5.5 Prédiction conforme** : transformer n'importe quel modèle en un modèle qui annonce des *ensembles* ou des *intervalles* avec une garantie de couverture.

> 🧭 **Comment lire ce chapitre.** Les sections 5.1 à 5.3 forment le socle. Les sections 5.4 et 5.5 sont facultatives. Le livre démontre et explique ; le code qui produit chaque nombre cité est exécuté en coulisses (voir l'introduction du volume), et les exercices et applications sont dans le cahier.

## Le fil rouge : un même problème, trois modèles

Tout le chapitre s'appuie sur le même problème, celui du volume : **prédire, pour chacun des 12 000 clients de la boutique, s'il aura cessé de commander dans les 90 jours** (la variable `churn_90j`, qui vaut 1 pour 14 % des clients). Les données sont **simulées** (`clients_ml.csv`), ce qui permet de savoir ce qui a été programmé.

Conformément à la règle du chapitre 1 (section 1.1), les clients sont répartis une fois pour toutes en trois jeux, **stratifiés** sur la cible (chacun garde 14 % de partants) :

| Jeu | Clients | Rôle |
|---|---|---|
| Entraînement | 7 200 | ajuster les modèles |
| Calibration (ou validation) | 2 400 | régler les seuils, calibrer les probabilités, calibrer la prédiction conforme |
| Test | 2 400 | **évaluer une seule fois**, à la fin, sans jamais s'en servir pour décider |

Trois modèles sont ajustés sur le jeu d'entraînement, avec leurs réglages par défaut (le réglage fin est l'objet de la section 1.5) : une **régression logistique** sur variables centrées-réduites, une **forêt aléatoire** (150 arbres) et un **gradient boosting**. Voici leurs scores sur le jeu de test, mesurés avec les outils de la section suivante :

| Modèle | AUC | Précision moyenne (AP) | Log-loss | Brier |
|---|---:|---:|---:|---:|
| Régression logistique | 0,859 | 0,560 | 0,289 | 0,0872 |
| Forêt aléatoire | 0,888 | 0,624 | 0,269 | 0,0808 |
| Gradient boosting | 0,897 | 0,650 | 0,255 | 0,0758 |

Dans ce tableau, le boosting domine sur toutes les colonnes. Dans la pratique, on voudrait savoir **de combien** il domine, si la différence est due au hasard, ce qu'elle change pour la décision et si ses probabilités sont crédibles : c'est précisément ce que ce chapitre apprend à faire.

Deux jeux de données interviendront en plus : le **jeu réel** `credit_defaut.csv` (30 000 clients d'une banque, 22 % de défauts ; source : Yeh et Lien, 2009, licence CC0) pour l'équité en 5.4, et les mêmes clients de la boutique pour la prédiction conforme en 5.5.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : le chapitre tout entier est accompagné d'applications et d'exercices ; chaque section ci-dessous indique les siens.


## 5.1 Métriques

Une métrique répond à une question précise. Choisir celle qui répond à la **bonne** question, avant de comparer des modèles, évite des semaines de travail dans la mauvaise direction. Cette section suit un fil : on part d'un modèle qui sort un **score** par client, on en fait une **décision** (contacter ou non) en choisissant un seuil, puis on mesure la **valeur** de cette décision.

### 5.1.1 Ce que l'on mesure : un score, une décision, une valeur

Trois objets se confondent souvent, et chacun a ses mesures.

- Le **score** (ou la probabilité) que le modèle attribue à chaque client. On le juge avec des mesures indépendantes de tout seuil : l'**AUC**, la **précision moyenne**, la **log-loss**, le **score de Brier**.
- La **décision** obtenue en comparant le score à un **seuil** : « contacter si le risque dépasse $t$ ». On la juge avec des mesures qui dépendent du seuil : exactitude, précision, rappel, $F_1$…
- La **valeur** de cette décision, en euros : ce que rapporte la campagne, une fois déduits ses coûts. C'est la seule mesure qui compte pour la gérante, et celle qui permet de choisir le seuil.

> 💡 **Intuition.** Un thermomètre (le score) n'est pas un diagnostic (la décision), et un diagnostic n'est pas un traitement réussi (la valeur). Un bon thermomètre est nécessaire ; il n'est jamais suffisant.

Dans toute la suite, **le cas positif est le départ** (`churn_90j` = 1). On appelle *positif* un client qui part et *alerte* un client que le modèle signale comme risqué.


### 5.1.2 La matrice de confusion et ses dérivés

Fixons un seuil. Chaque client tombe dans l'une des quatre cases du tableau croisant la réalité et la prédiction :

| | Prédit : fidèle | Prédit : partant |
|---|---|---|
| **Réel : fidèle** | vrais négatifs (VN) | faux positifs (FP), les *fausses alertes* |
| **Réel : partant** | faux négatifs (FN), les *départs manqués* | vrais positifs (VP) |

**Un exemple entièrement à la main.** Sur 1 000 clients, 140 vont partir. Le modèle émet 120 alertes, dont 84 sont justes. Il y a donc VP = 84, FP = 120 − 84 = 36, FN = 140 − 84 = 56 et VN = 1 000 − 84 − 36 − 56 = 824. À partir de ces quatre nombres :

- l'**exactitude** (*accuracy*) est la part de bonnes réponses : $\dfrac{VP+VN}{n}=\dfrac{84+824}{1000}=0{,}908$ ;
- la **précision** est la part d'alertes justes : $\dfrac{VP}{VP+FP}=\dfrac{84}{120}=0{,}70$ ;
- le **rappel** (*recall*, ou *sensibilité*, ou taux de vrais positifs) est la part des départs détectés : $\dfrac{VP}{VP+FN}=\dfrac{84}{140}=0{,}60$ ;
- la **spécificité** est la part des fidèles correctement laissés en paix : $\dfrac{VN}{VN+FP}=\dfrac{824}{860}\approx0{,}958$ ; son complément, $1-$ spécificité, est le **taux de fausses alertes** (FPR) ;
- le **$F_1$** est la moyenne **harmonique** de la précision et du rappel : $F_1=\dfrac{2PR}{P+R}=\dfrac{2\times0{,}7\times0{,}6}{1{,}3}\approx0{,}646$.

Le $F_1$ pondère précision et rappel également. Si manquer un départ coûte plus cher qu'une fausse alerte, on utilise sa généralisation, le **$F_\beta$** : $F_\beta=\dfrac{(1+\beta^2)\,PR}{\beta^2P+R}$. Avec $\beta=2$, le rappel compte deux fois plus que la précision ($F_2\approx0{,}618$ ici) ; avec $\beta=0{,}5$, c'est l'inverse ($F_{0,5}\approx0{,}677$).

Enfin, le **coefficient de corrélation de Matthews** (MCC) résume les quatre cases d'un seul nombre entre $-1$ et $1$ : $\text{MCC}=\dfrac{VP\cdot VN-FP\cdot FN}{\sqrt{(VP+FP)(VP+FN)(VN+FP)(VN+FN)}}$, soit $\dfrac{69\,216-2\,016}{\sqrt{120\cdot140\cdot860\cdot880}}\approx0{,}596$. C'est la corrélation entre prédiction et réalité ; elle reste informative même quand les classes sont très déséquilibrées.

> ⚠️ **Le piège de l'exactitude.** Ici, un modèle qui répondrait « personne ne part » aurait une exactitude de $860/1000=86\ \%$. Notre modèle à 90,8 % ne fait donc que quatre points de mieux, alors qu'il a détecté 60 % des départs. Quand une classe est rare, l'exactitude récompense surtout la prudence. Comparez-la toujours à celle du modèle « toujours la classe majoritaire ».

Voyons maintenant ces mesures sur le **vrai** jeu de test (2 400 clients dont 337 partants), avec le boosting et le seuil habituel de 0,5.


Voici les quatre cases :

| | Prédit : fidèle | Prédit : partant |
|---|---:|---:|
| **Réel : fidèle** (2 063) | 1 996 | 67 |
| **Réel : partant** (337) | 174 | 163 |

On en tire : exactitude 0,900 (contre 0,860 pour « personne ne part »), précision 0,709, rappel 0,484, spécificité 0,968, $F_1=0{,}575$, $F_2=0{,}517$, $F_{0,5}=0{,}648$ et MCC = 0,533. La lecture est limpide : quand le modèle alerte, il a raison sept fois sur dix, mais il laisse passer plus de la moitié des départs.

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score

yhat = (p >= 0.5).astype(int)                     # p : probabilités prédites du boosting sur le jeu de test
print(confusion_matrix(yt, yhat))                 # lignes : réalité ; colonnes : prédiction
print(round(precision_score(yt, yhat), 3), round(recall_score(yt, yhat), 3), round(roc_auc_score(yt, p), 3))
```
<!--sortie-->
```text
[[1996   67]
 [ 174  163]]
0.709 0.484 0.897
```

Ces mesures sont disponibles en une ligne dans `scikit-learn`. Le plus difficile est de les **lire**.

### 5.1.3 Le seuil change tout

Le seuil de 0,5 n'a rien de sacré : il n'est « naturel » que si fausses alertes et départs manqués coûtent pareil. Voyons ce que devient la même sortie du modèle pour d'autres seuils :

| Seuil | Alertes | Précision | Rappel | $F_1$ |
|---:|---:|---:|---:|---:|
| 0,1 | 692 | 0,399 | 0,819 | 0,536 |
| 0,2 | 460 | 0,517 | 0,706 | 0,597 |
| 0,3 | 350 | 0,603 | 0,626 | 0,614 |
| 0,5 | 230 | 0,709 | 0,484 | 0,575 |

En abaissant le seuil, on signale plus de clients : le **rappel monte** (on détecte plus de départs) mais la **précision baisse** (plus de fausses alertes). C'est un **compromis**, pas un réglage à optimiser une fois pour toutes. Le $F_1$ est maximal autour de 0,3, mais ce « maximum » ne dit rien de ce qui compte vraiment pour la boutique ; nous y reviendrons en 5.1.7 en passant aux coûts.

> 💡 **Ce qu'il faut retenir du seuil.** Le même modèle peut être un détecteur prudent (précision 71 %, rappel 48 %) ou un détecteur large (précision 40 %, rappel 82 %). Comparer deux modèles à un seuil fixé arbitrairement mélange la qualité du score et le choix du seuil. Pour juger le **score** seul, il faut des mesures qui balaient tous les seuils.

### 5.1.4 La courbe ROC et l'AUC

La **courbe ROC** (*Receiver Operating Characteristic*) balaie tous les seuils possibles. Pour chaque seuil $t$, elle place un point d'abscisse le taux de fausses alertes $\mathrm{FPR}(t)$ et d'ordonnée le rappel $\mathrm{TPR}(t)$. Un seuil très élevé ne signale personne : on est en $(0,0)$. Un seuil nul signale tout le monde : on est en $(1,1)$. Entre les deux, plus la courbe se rapproche du coin supérieur gauche $(0,1)$, meilleur est le score ; la diagonale correspond au hasard.


![Courbes ROC (à gauche) et précision-rappel (à droite) des trois modèles sur le jeu de test. Le boosting domine, mais l'écart est bien plus lisible sur la courbe précision-rappel.](figures/ch05-roc-pr.png)

**L'aire sous la courbe ROC** (AUC, *Area Under the Curve*) résume la courbe en un nombre entre 0,5 (hasard) et 1 (classement parfait). Elle a une interprétation probabiliste remarquable.

> 📐 **Démonstration : l'AUC est une probabilité.** Notons $S^+$ le score d'un client qui part tiré au hasard et $S^-$ celui d'un client fidèle tiré au hasard, indépendamment. Pour un seuil $t$, $\mathrm{TPR}(t)=P(S^+>t)$ et $\mathrm{FPR}(t)=P(S^->t)$. Quand $t$ parcourt les valeurs de la plus grande à la plus petite, $\mathrm{FPR}$ augmente de $0$ à $1$, et sa « vitesse » est la densité $f^-$ de $S^-$ : $d\,\mathrm{FPR}=-f^-(t)\,dt$. Donc
> $$\mathrm{AUC}=\int \mathrm{TPR}\;d\mathrm{FPR}=\int_{-\infty}^{+\infty}P(S^+>t)\,f^-(t)\,dt=P(S^+>S^-),$$
> la dernière égalité venant de la formule des probabilités totales en conditionnant par la valeur $S^-=t$. (En cas d'égalité de scores, on compte une demi-paire.) $\blacksquare$

**L'AUC est donc la probabilité qu'un client qui part ait un score plus élevé qu'un client qui reste.** Une AUC de 0,90 signifie : si l'on prend un partant et un fidèle au hasard, le modèle les classe dans le bon ordre neuf fois sur dix. Sur notre jeu de test, il y a $337\times2\,063=695\,231$ paires (partant, fidèle) ; en les comparant une à une, on trouve exactement la même valeur que le calcul de l'AUC : **0,8971**.

Ce résultat est la même chose que la **statistique $U$ du test de Mann-Whitney** (volume I, section 3.7.2) : $\mathrm{AUC}=U/(n^+n^-)$. Tester si deux modèles ont la même AUC, c'est comparer des rangs.

> ⚠️ **L'AUC ne dit rien de la calibration ni du seuil.** Deux scores qui rangent les clients dans le même ordre ont exactement la même AUC, même si l'un annonce 1 % et l'autre 90 % pour le même client. L'AUC mesure le **classement**, pas la justesse des probabilités (voir 5.2).

### 5.1.5 Précision-rappel : ce que la ROC ne voit pas

Sur la courbe de droite de la figure, on trace la **précision en fonction du rappel**. Son résumé est la **précision moyenne** (*average precision*, AP) : $\mathrm{AP}=\sum_n(R_n-R_{n-1})P_n$, la moyenne des précisions obtenues à chaque nouveau départ détecté. Le « hasard » n'est pas une diagonale : c'est une droite horizontale à hauteur de la **prévalence** (14 % ici).

Pourquoi deux courbes ? Parce qu'elles ne réagissent pas de la même façon quand les positifs sont rares. La ROC compare des **taux** calculés séparément parmi les positifs et parmi les négatifs ; la précision, elle, mélange les deux populations : sa valeur dépend du **nombre de négatifs**. Une expérience le montre bien. Multiplions (par un poids) le nombre de clients fidèles par 10, sans changer les scores : la prévalence tombe de 14 % à 1,6 %.

| | Avant | Après (négatifs × 10) |
|---|---:|---:|
| Prévalence | 0,140 | 0,016 |
| **AUC** | 0,8971 | **0,8971** |
| **Précision moyenne** | 0,6496 | **0,2343** |

L'AUC n'a pas bougé d'un millième ; la précision moyenne s'est effondrée. Elle a raison : avec 10 fois plus de fidèles, une alerte a beaucoup plus de chances d'être une fausse alerte. La ROC rend ce modèle « aussi bon qu'avant » parce qu'elle regarde le classement ; la courbe précision-rappel rend compte de ce que l'on vivra en réalité, à savoir une montagne de fausses alertes.

> 💡 **Règle pratique.** Quand les positifs sont rares (fraude à 1 %, départ à 5 %…) et que ce sont eux qui intéressent, **regardez la courbe précision-rappel**. L'AUC reste pratique pour comparer des classements, mais elle peut rester élevée (0,95 !) pour un modèle dont 90 % des alertes sont fausses.

### 5.1.6 Juger les probabilités : log-loss et score de Brier

Les mesures précédentes ne regardent que l'**ordre** des scores. Si l'on veut utiliser la probabilité elle-même (pour calculer un coût attendu, par exemple), il faut une mesure qui juge sa **justesse**. Deux sont standard. Pour $n$ clients de probabilités prédites $\hat p_i$ et de résultats $y_i\in\{0,1\}$ :

$$\text{log-loss}=-\frac1n\sum_i\bigl[y_i\ln\hat p_i+(1-y_i)\ln(1-\hat p_i)\bigr],\qquad \text{Brier}=\frac1n\sum_i(\hat p_i-y_i)^2.$$

La log-loss est la **vraisemblance négative** : c'est ce que minimise la régression logistique (volume II, section 2.2). Elle punit très fort un modèle qui annonce « 1 % » pour un événement qui arrive. Le Brier est l'erreur quadratique moyenne des probabilités : plus doux, mais plus robuste.

Ces deux mesures sont des **règles de score propres** : en espérance, elles sont minimisées en annonçant la **vraie** probabilité. Pour le Brier, c'est immédiat. Si la vraie probabilité d'un départ, pour un type de client, est $q$, et que l'on annonce $p$, alors $E[(p-Y)^2]=(p-q)^2+q(1-q)$ : le premier terme s'annule exactement pour $p=q$, et le second est la part d'incertitude irréductible. Impossible de « tricher » en exagérant ou en minimisant.

Il faut un point de repère. Le modèle constant, qui annonce 14 % à tout le monde, a un Brier de $0{,}14\times0{,}86\approx0{,}1207$ et une log-loss de 0,4057. Notre boosting obtient 0,0758 et 0,2548, soit un **gain de 37 % sur le Brier** (le « score de compétence » $1-0{,}0758/0{,}1207$). La régression logistique est à 0,0872 et 0,2886 : meilleure que le hasard, moins bonne que la forêt (0,0808 ; 0,2687) et que le boosting. L'ordre est le même qu'avec l'AUC, mais ce n'est pas une règle : on verra en 5.2 des modèles dont l'AUC est bonne et le Brier mauvais.

### 5.1.7 Choisir le seuil par les coûts

Voici enfin la manière de choisir un seuil qui ait un sens. La gérante veut proposer une offre de rétention aux clients à risque. Chaque contact coûte 5 €. Un client contacté qui allait partir est « sauvé » avec une probabilité de 40 %, et un client sauvé vaut 60 € de marge future. Pour un client dont la probabilité de départ est $p$, le **gain net attendu** d'un contact est

$$g(p)=p\times0{,}4\times60-5=24\,p-5.$$

> 📐 **Le seuil optimal.** Il faut contacter si et seulement si $g(p)>0$, c'est-à-dire si $p>\dfrac{5}{24}\approx0{,}208$. Plus généralement, avec un coût de contact $c$, une probabilité de succès $s$ et une valeur $V$, le seuil optimal est $t^\star=\dfrac{c}{sV}$. Il ne dépend que de l'économie du problème, pas du modèle. (Sous la forme classique des « coûts de mauvaise classification », $t^\star=\dfrac{C_{FP}}{C_{FP}+C_{FN}}$.)

Cette formule suppose que $p$ est une **vraie** probabilité : il faut donc un modèle calibré (section 5.2). Vérifions-la sur le jeu de test, en comptant pour chaque seuil le gain net réalisé :


| Seuil | Clients contactés | Gain net |
|---:|---:|---:|
| 0,10 | 692 | 3 164 € |
| 0,20 | 460 | 3 412 € |
| 0,208 (théorique) | 446 | 3 386 € |
| 0,30 | 350 | 3 314 € |
| 0,50 (habituel) | 230 | 2 762 € |
| contacter tout le monde | 2 400 | −3 912 € |

![Gain net de la campagne selon le seuil. Le maximum observé est atteint vers 0,18 ; la courbe est plate entre 0,15 et 0,30.](figures/ch05-seuil-cout.png)

Le message est triple. D'abord, **le seuil de 0,5 laisse environ 700 € sur la table** (2 762 € contre 3 473 € au meilleur seuil de la grille, 0,18). Ensuite, le seuil théorique (0,208) donne 3 386 €, soit 87 € de moins que le maximum observé : la courbe est plate autour de l'optimum, et l'optimum exact sur un jeu de 2 400 clients est bruité. Enfin, **contacter tout le monde perd de l'argent** : c'est ce que fait, en pratique, une campagne sans modèle.

> ⚠️ **Le gain mesuré sur le jeu de test sert à illustrer, pas à choisir.** Pour choisir le seuil dans un vrai projet, on utilise le jeu de **calibration** (ou la validation croisée), puis on mesure une dernière fois sur le jeu de test.

### 5.1.8 Gain et lift : la lecture du marketing

Une campagne n'a souvent pas de seuil : elle a un **budget** (« nous pouvons contacter 20 % des clients »). On classe alors les clients par score décroissant, on les découpe en déciles, et on regarde où se trouvent les partants.


| Décile | Clients | Partants | Taux de départ | Lift | Part cumulée des partants |
|---:|---:|---:|---:|---:|---:|
| 1 | 240 | 168 | 70,0 % | 4,99 | 49,9 % |
| 2 | 240 | 76 | 31,7 % | 2,26 | 72,4 % |
| 3 | 240 | 36 | 15,0 % | 1,07 | 83,1 % |
| 4 | 240 | 27 | 11,2 % | 0,80 | 91,1 % |
| 5 | 240 | 10 | 4,2 % | 0,30 | 94,1 % |
| 6 | 240 | 11 | 4,6 % | 0,33 | 97,3 % |
| 7 | 240 | 6 | 2,5 % | 0,18 | 99,1 % |
| 8 | 240 | 1 | 0,4 % | 0,03 | 99,4 % |
| 9 | 240 | 2 | 0,8 % | 0,06 | 100,0 % |
| 10 | 240 | 0 | 0,0 % | 0,00 | 100,0 % |

Le **lift** d'un décile est son taux de départ divisé par le taux moyen (14 %) : le premier décile « vaut » 4,99 fois un tirage au hasard. La dernière colonne donne la **courbe de gain** : **en contactant 20 % des clients seulement, on atteint 72 % des partants**. Aucun partant dans le dernier décile : le modèle repère bien les clients qui ne partiront pas, ce qui permet de ne pas les déranger.

![Courbe de gain : part des partants atteinte en fonction de la part de clients contactés, classés par score. La diagonale est le ciblage au hasard.](figures/ch05-gain.png)

> 💡 **À quoi sert cette lecture ?** Elle parle le langage du budget : « pour 20 % de l'effort, 72 % du résultat ». Elle ne demande aucun seuil, et elle se compare directement à un tirage au hasard, ce qui la rend lisible par des non-spécialistes.

### 5.1.9 Plus de deux classes

Quand la cible a plus de deux modalités, on garde la matrice de confusion (une ligne par classe réelle), et on **moyenne** les métriques par classe de trois façons :

- la moyenne **macro** calcule la métrique par classe, puis moyenne sans pondération : chaque classe pèse autant ;
- la moyenne **micro** additionne tous les VP, FP, FN avant de calculer : chaque *client* pèse autant (pour un problème à une seule étiquette par client, le $F_1$ micro est égal à l'exactitude) ;
- la moyenne **pondérée** moyenne par classe, avec des poids proportionnels aux effectifs.

Pour illustrer, tentons de reconnaître à quel **segment** appartient un client (4 segments latents simulés, dont les proportions sont 39, 29, 20 et 12 %) à partir de ses comportements. Ce n'est qu'une démonstration : ailleurs, ce segment ne sert jamais d'entrée.

| Segment réel \ prédit | 0 | 1 | 2 | 3 | Rappel |
|---|---:|---:|---:|---:|---:|
| 0 (936 clients) | 873 | 44 | 0 | 19 | 0,933 |
| 1 (703) | 30 | 655 | 5 | 13 | 0,932 |
| 2 (479) | 0 | 1 | 478 | 0 | 0,998 |
| 3 (282) | 31 | 7 | 0 | 244 | 0,865 |

L'exactitude est de 0,9375, le $F_1$ micro lui est égal (0,9375), le $F_1$ pondéré vaut 0,9374 et le $F_1$ **macro** 0,9328. Le macro est le plus bas parce qu'il donne autant de poids à la plus petite classe (les « grands paniers », 12 % des clients, rappel 0,865) qu'à la plus grande. **Si une classe rare est précisément celle qui vous importe, c'est le macro, ou le rappel par classe, qu'il faut regarder.**

### 5.1.10 Régression : choisir sa perte

Pour une cible numérique, les métriques mesurent l'écart entre la valeur prédite $\hat y_i$ et la valeur réelle $y_i$. Prenons la **dépense des six mois suivants** (en euros). Elle est difficile à prédire : 36 % des clients du jeu de test ne dépensent rien, et le reste a une distribution très étalée (moyenne 83,2 €, écart-type 125,7 €).

| Mesure | Formule | Remarque |
|---|---|---|
| **MAE** (erreur absolue moyenne) | $\frac1n\sum\lvert y_i-\hat y_i\rvert$ | en euros ; robuste aux valeurs extrêmes ; cible la **médiane** |
| **RMSE** (racine de l'erreur quadratique) | $\sqrt{\frac1n\sum(y_i-\hat y_i)^2}$ | en euros ; punit les gros écarts ; cible la **moyenne** |
| **$R^2$** | $1-\frac{\sum(y_i-\hat y_i)^2}{\sum(y_i-\bar y)^2}$ | part de variance expliquée par rapport à la moyenne |
| **MAPE** | $\frac1n\sum\frac{\lvert y_i-\hat y_i\rvert}{\lvert y_i\rvert}$ | erreur relative ; **indéfinie si $y_i=0$**, asymétrique |
| **Perte pinball** | $\max\bigl(\tau(y-q),\,(\tau-1)(y-q)\bigr)$ | juge un **quantile** $q$ de niveau $\tau$ |

Un gradient boosting entraîné pour minimiser l'erreur quadratique obtient sur le jeu de test **MAE = 59,2 €, RMSE = 98,6 € et $R^2=0{,}385$**. Pour savoir si c'est bien, il faut des références : prédire la moyenne d'entraînement à tout le monde donne MAE = 83,5 € et RMSE = 125,7 € ; prédire la médiane (41,9 €) donne MAE = 75,1 €. Le modèle réduit donc l'erreur absolue de 29 % par rapport à la moyenne. On vérifie la cohérence du $R^2$ : $1-(98{,}6/125{,}7)^2\approx0{,}385$.

> 💡 **MAE et RMSE ne mesurent pas la même chose.** Le RMSE est toujours supérieur ou égal au MAE, et l'écart entre les deux dit si les erreurs sont régulières ou concentrées. Ici, les 1 % de plus grosses erreurs représentent **35 %** de l'erreur quadratique mais seulement **10 %** de l'erreur absolue. Si quelques gros clients mal prédits sont l'enjeu, le RMSE est le bon juge ; si l'on veut juger le client « typique », c'est le MAE.

**Le piège du MAPE.** Il est calculé en divisant par la valeur réelle : impossible pour les 860 clients du jeu de test dont la dépense est nulle. En se limitant aux dépenses positives, on trouve 60 %, un nombre qui dépend beaucoup de la façon dont on traite les petits montants. Quant au sMAPE (qui divise par la moyenne de $\lvert y\rvert$ et $\lvert\hat y\rvert$), il vaut ici 1,07, car chaque prédiction positive d'une dépense nulle donne une erreur de 200 %. **Sur une cible qui contient des zéros, évitez les erreurs relatives.**

**Prédire un quantile.** Parfois, on ne veut pas la valeur la plus probable mais une valeur « haute » : *quelle dépense sera dépassée dans seulement 10 % des cas ?* (pour dimensionner un stock, par exemple). On entraîne alors le modèle avec la **perte pinball** de niveau $\tau=0{,}9$, qui pénalise davantage de sous-estimer que de surestimer. Le modèle quantile obtient une perte pinball de 17,2, contre 29,0 pour le modèle de la moyenne utilisé comme prédicteur de quantile. Mais il faut vérifier sa **couverture** : seuls 85,8 % des clients ont une dépense inférieure au quantile annoncé, et non 90 %. (Le modèle de la moyenne, lui, en couvre 61,2 %.) Un quantile estimé n'est pas garanti : en 5.5, on le réparera.

> ✅ **À retenir.**
> - L'exactitude se compare toujours au modèle « classe majoritaire » ; avec des classes rares, préférez rappel, précision, $F_\beta$, MCC.
> - L'**AUC** est la probabilité qu'un positif ait un score supérieur à celui d'un négatif (statistique de Mann-Whitney) : elle mesure le classement, pas la justesse des probabilités, et elle ne voit pas la prévalence.
> - Avec des positifs rares, la **courbe précision-rappel** et l'AP disent ce que l'AUC cache.
> - La **log-loss** et le **Brier** jugent les probabilités ; ce sont des règles de score propres.
> - Le seuil se déduit des **coûts** : $t^\star=c/(sV)$ pour une campagne, à condition que les probabilités soient calibrées.
> - Le **lift** et la courbe de gain parlent le langage du budget.
> - En régression, **MAE** (médiane) et **RMSE** (moyenne) répondent à des questions différentes ; évitez le MAPE avec des zéros ; la perte **pinball** juge un quantile.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.4, exercices 5.1 à 5.6.


## 5.2 Calibration

Une probabilité n'est utile que si on peut la prendre au mot. Quand la gérante lit « 30 % » sur la fiche d'un client, elle en déduit un coût attendu, un seuil, une priorité. Si ce « 30 % » est en réalité « 55 % », tout ce qui en découle est faux, même si le classement des clients est parfait. Cette section apprend à **vérifier** que les probabilités sont justes, à comprendre pourquoi elles ne le sont pas toujours, et à les **réparer**.

### 5.2.1 Qu'est-ce qu'une probabilité « juste » ?

Un modèle est **calibré** si, parmi tous les clients à qui il attribue une probabilité $p$, une proportion $p$ d'entre eux subit effectivement l'événement :
$$P(Y=1\mid \hat p=p)=p\quad\text{pour tout } p.$$
Il s'agit d'une propriété distincte de la **discrimination** (la capacité à bien classer, mesurée par l'AUC). Un score peut classer parfaitement et être très mal calibré : si l'on divise toutes les probabilités d'un modèle parfaitement calibré par deux, l'ordre reste identique (l'AUC ne bouge pas), mais plus aucune probabilité n'est juste.

**Un exemple à la main.** Vingt clients : dix reçoivent la probabilité $0{,}10$ et deux d'entre eux partent (taux observé $0{,}20$) ; les dix autres reçoivent $0{,}60$ et cinq partent (taux observé $0{,}50$). Le modèle est trop optimiste dans le premier groupe (il annonce 10 %, la réalité est de 20 %) et trop pessimiste dans le second (60 % annoncés, 50 % observés).

On le résume avec le **diagramme de fiabilité** (*reliability diagram*) : on regroupe les clients en classes de probabilités voisines (ici, par classes de même effectif), et l'on trace, pour chaque classe, le **taux observé** en fonction de la **probabilité moyenne prédite**. Un modèle calibré suit la diagonale. L'**erreur de calibration attendue** (ECE) est l'écart moyen à la diagonale, pondéré par l'effectif $n_b$ de chaque classe $b$ :
$$\mathrm{ECE}=\sum_{b}\frac{n_b}{n}\,\bigl|\,\bar p_b-\bar y_b\,\bigr|.$$
Sur notre exemple, $\mathrm{ECE}=\tfrac12\times0{,}10+\tfrac12\times0{,}10=0{,}10$.

> ⚠️ **L'ECE est bruitée.** Avec 10 classes de 240 clients, le taux observé d'une classe où le risque est de 14 % fluctue naturellement de $\sqrt{0{,}14\times0{,}86/240}\approx0{,}022$. Une ECE de 0,01 ou 0,02 est donc **indiscernable d'une calibration parfaite** sur ce jeu. L'ECE dépend aussi du découpage en classes. Elle se lit avec le diagramme, jamais seule.


### 5.2.2 Qui est bien calibré, qui ne l'est pas ?

Comparons cinq modèles sur le jeu de test : les trois du chapitre, plus deux modèles « abîmés » à dessein : un **boosting surajusté** (300 itérations, taux d'apprentissage 0,3, arbres de 63 feuilles) et une **régression logistique avec poids de classes** (`class_weight="balanced"`, qui donne autant de poids aux 14 % de partants qu'aux 86 % de fidèles).

| Modèle | AUC | Brier | Log-loss | ECE | Probabilité moyenne |
|---|---:|---:|---:|---:|---:|
| Régression logistique | 0,859 | 0,0872 | 0,2886 | 0,012 | 0,136 |
| Forêt aléatoire | 0,888 | 0,0808 | 0,2687 | 0,031 | 0,139 |
| Boosting (réglages par défaut) | 0,897 | 0,0758 | 0,2548 | 0,014 | 0,128 |
| Boosting surajusté | 0,876 | 0,1010 | 0,7143 | 0,098 | 0,094 |
| Logistique pondérée | 0,857 | 0,1542 | 0,4588 | 0,209 | 0,349 |

(La prévalence observée sur le jeu de test est de 0,140.)


![Diagrammes de fiabilité des cinq modèles sur le jeu de test (classes de même effectif), et distribution des probabilités de deux d'entre eux. Un modèle calibré suit la diagonale.](figures/ch05-fiabilite.png)

Chaque modèle raconte une histoire différente.

**La régression logistique est calibrée par construction.** Elle maximise la vraisemblance, donc annule la dérivée de la log-vraisemblance par rapport à l'ordonnée à l'origine : $\sum_i(y_i-\hat p_i)=0$. La somme des probabilités prédites sur le jeu d'entraînement est égale au nombre de partants : en moyenne, le modèle est juste (probabilité moyenne 0,136 pour une prévalence de 0,140). Quand le modèle est correctement spécifié, cette justesse vaut aussi à tous les niveaux. Et même s'il ne l'est pas, la calibration reste en général très honorable.

**La forêt est trop prudente aux extrêmes.** Elle moyenne les proportions observées dans les feuilles de ses arbres, avec au moins 5 clients par feuille : ses probabilités sont tirées vers le milieu. Dans la classe des clients les plus à risque, elle annonce **54 %** pour un taux observé de **68 %** ; dans la classe la moins à risque, elle annonce 0,3 % pour 0,4 %. C'est un modèle *sous-confiant* (ECE 0,031, la plus mauvaise des trois modèles « sains »).

**Le boosting par défaut est bien calibré** (ECE 0,014, log-loss 0,255) : il optimise la log-loss, avec un petit pas d'apprentissage, et s'arrête avant de surajuster. Mais le **boosting surajusté** est le contraire de la forêt : il est *sur-confiant*. Ses probabilités se collent à 0 ou à 1 (huit classes sur dix ont une probabilité moyenne prédite inférieure à 0,001), et la classe des plus à risque reçoit **89 %** pour un taux observé de **63 %**. Sa log-loss est de 0,714, près de trois fois celle du boosting réglé. Retenez qu'un boosting n'est bien calibré que si on le laisse peu s'entraîner.

**La logistique pondérée classe aussi bien que la logistique ordinaire (AUC 0,857 contre 0,859) mais ses probabilités sont fausses :** elle annonce en moyenne 35 % de départs alors qu'ils sont 14 %. Les poids de classes déplacent la prévalence apparente. On y revient en 5.2.6.

> 💡 **Ce que montre ce tableau.** L'AUC et la calibration sont indépendantes. La logistique pondérée a une AUC quasi identique à celle de la logistique ordinaire et un Brier presque deux fois plus mauvais (0,154 contre 0,087). Ne choisissez pas un modèle sur la seule AUC si vous comptez utiliser ses probabilités.

> 🧭 **Et les autres modèles ?** Les SVM produisent des scores qui sont des distances à une frontière, pas des probabilités (section 2.5) ; les k plus proches voisins annoncent des proportions de voisins, tirées vers les extrêmes quand $k$ est petit ; le Bayes naïf est souvent sur-confiant, car l'indépendance supposée entre variables compte plusieurs fois la même information. Dans tous les cas, **vérifiez**.

### 5.2.3 Réparer : la méthode de Platt

Si le défaut de calibration est une déformation régulière des probabilités, on peut la corriger après coup par une **recalibration** : on apprend une fonction $g$ telle que $g(\hat s)$ soit calibré, où $\hat s$ est le score du modèle. La première méthode est celle de **Platt** : on suppose que le log-odds de la probabilité vraie est une fonction affine du log-odds du score,
$$P(Y=1\mid \hat s)=\sigma\bigl(a\cdot\operatorname{logit}(\hat s)+b\bigr),\qquad \sigma(z)=\frac1{1+e^{-z}}.$$
Deux paramètres $(a,b)$, estimés par maximum de vraisemblance : c'est une **régression logistique à une variable** (le logit du score), ajustée sur le jeu de **calibration**, qui n'a pas servi à entraîner le modèle.

Les paramètres s'interprètent. Une **pente $a>1$** étire les probabilités vers les extrêmes (corrige un modèle sous-confiant) ; une pente **$a<1$** les écrase vers le centre (corrige un modèle sur-confiant) ; l'**ordonnée $b$** déplace le niveau global. Sur nos trois modèles abîmés :

| Modèle | Pente $a$ | Ordonnée $b$ | Lecture |
|---|---:|---:|---|
| Forêt | 1,42 | 0,55 | étire : le modèle était sous-confiant |
| Boosting surajusté | 0,28 | −0,19 | écrase fortement : il était sur-confiant |
| Logistique pondérée | 1,06 | −1,79 | quasi pas de changement de forme, mais un grand décalage de niveau |

### 5.2.4 Réparer : la régression isotonique

Platt suppose une forme précise (une sigmoïde). La **régression isotonique** n'en suppose aucune, sauf que la probabilité vraie est une fonction **croissante** du score. Elle ajuste, par moindres carrés, la fonction en escalier croissante la plus proche des résultats observés sur le jeu de calibration (par l'algorithme classique « pool adjacent violators » : on fusionne les marches voisines qui violent l'ordre). Elle est donc plus flexible, mais elle demande **plus de données** (compter au moins quelques milliers d'exemples), et elle produit des paliers : plusieurs clients reçoivent exactement la même probabilité.

Voici, pour les trois modèles abîmés, l'effet des deux méthodes, ajustées sur les 2 400 clients du jeu de calibration et évaluées sur le jeu de test :


| Modèle | Méthode | Brier | Log-loss | ECE |
|---|---|---:|---:|---:|
| Forêt | brut | 0,0808 | 0,2687 | 0,031 |
| | Platt | 0,0785 | 0,2629 | 0,009 |
| | isotonique | 0,0780 | 0,2741 | 0,014 |
| Boosting surajusté | brut | 0,1010 | 0,7143 | 0,098 |
| | Platt | 0,0842 | 0,2911 | 0,042 |
| | isotonique | 0,0821 | 0,2734 | 0,012 |
| Logistique pondérée | brut | 0,1542 | 0,4588 | 0,209 |
| | Platt | 0,0881 | 0,2906 | 0,015 |
| | isotonique | 0,0887 | 0,3129 | 0,019 |

![Diagrammes de fiabilité avant (rouge) et après recalibration par Platt (bleu) ou régression isotonique (vert), sur le jeu de test.](figures/ch05-recalibrage.png)

La recalibration est spectaculaire pour les deux modèles les plus abîmés : le Brier de la logistique pondérée passe de 0,154 à 0,088, soit quasiment celui de la logistique ordinaire (0,087), et celui du boosting surajusté de 0,101 à 0,082. Pour la forêt, qui était déjà presque calibrée, le gain est modeste mais réel.

Deux nuances. **Platt est plus stable avec peu de données** (deux paramètres seulement) mais ne peut corriger que des déformations en S ; ici, sur le boosting surajusté, il laisse une ECE de 0,042 que la méthode isotonique ramène à 0,012. **L'isotonique, plus souple, peut perdre en log-loss** : sur la forêt, elle passe de 0,2687 à 0,2741, car ses paliers produisent des probabilités proches de 0 pour des clients dont le risque n'est pas nul. Le Brier, plus tolérant, s'améliore dans les deux cas.

### 5.2.5 Calibrer sans tricher

La recalibration est un **modèle de plus**, qui peut lui aussi surajuster. Trois règles.

1. **Calibrez sur des données que ni le modèle ni vous-même n'avez utilisées pour l'entraîner.** Calibrer sur le jeu d'entraînement revient à corriger un modèle pour les données qu'il connaît déjà par cœur, et donc à ne rien corriger.
2. **Ne touchez pas au jeu de test avant la fin.** Il sert à *mesurer* la calibration, pas à l'obtenir.
3. **Si les données sont comptées**, utilisez la **validation croisée** : à chaque pli, on ajuste le modèle sur les autres et on calibre sur le pli. `CalibratedClassifierCV` fait cela automatiquement.

```python
from sklearn.calibration import CalibratedClassifierCV

foret = RandomForestClassifier(150, min_samples_leaf=5, random_state=0)
foret_calibree = CalibratedClassifierCV(foret, method="isotonic", cv=3).fit(Xtr, ytr)   # 3 plis : chaque pli sert à calibrer le modèle ajusté sur les deux autres
p_cal = foret_calibree.predict_proba(Xte)[:, 1]
print("Brier :", round(M.brier_score_loss(yte, p_cal), 4), "| ECE :", round(ece(yte.to_numpy(), p_cal), 4), "| AUC :", round(M.roc_auc_score(yte, p_cal), 4))
```
<!--sortie-->
```text
Brier : 0.0782 | ECE : 0.0089 | AUC : 0.8888
```

Sur la forêt, la calibration croisée donne un Brier de 0,0782 et une ECE de 0,009, contre 0,0808 et 0,031 avant. L'AUC est quasiment inchangée (0,8888 contre 0,8881) : la recalibration est une fonction croissante des scores, donc elle conserve l'ordre, sauf les égalités que peut créer une fonction en escalier.

> ⚠️ **Recalibrez après tout changement.** Une calibration dépend de la population : si les clients de demain diffèrent de ceux d'hier (nouvelle campagne, nouveau canal), les probabilités dérivent. Un tableau de bord de production doit contenir un diagramme de fiabilité calculé sur les données récentes.

### 5.2.6 Poids de classes et rééchantillonnage : un décalage de prévalence

Le chapitre 4 (section 4.3) présente des remèdes au déséquilibre de classes : **pondérer** les exemples rares, ou **rééchantillonner** (suréchantillonner les rares, sous-échantillonner les fréquents). Ils améliorent souvent le rappel, mais ils déplacent la prévalence que « voit » le modèle, donc ses probabilités. Heureusement, le décalage est **exactement corrigible**.

> 📐 **Correction d'un décalage de prévalence.** D'après la formule de Bayes (volume I, section 2.1.6), la cote *a posteriori* est la cote *a priori* multipliée par un rapport de vraisemblance qui ne dépend que des variables : $\dfrac{P(Y=1\mid x)}{P(Y=0\mid x)}=\dfrac{\pi}{1-\pi}\times\mathrm{LR}(x)$, où $\pi$ est la prévalence. Un modèle entraîné comme si la prévalence valait $\pi'$ (avec `class_weight="balanced"`, on a $\pi'=\tfrac12$) apprend $\dfrac{\pi'}{1-\pi'}\times\mathrm{LR}(x)$ : le même $\mathrm{LR}(x)$, mais un autre a priori. On retrouve donc la vraie cote en la multipliant par $\dfrac{\pi/(1-\pi)}{\pi'/(1-\pi')}$.

Avec $\pi=0{,}1404$ (prévalence d'entraînement) et $\pi'=\tfrac12$, le facteur est $0{,}1404/0{,}8596\approx0{,}163$. Appliquée à la logistique pondérée, la correction ramène la probabilité moyenne de **0,349 à 0,135** (la prévalence du test est 0,140), le Brier de **0,1542 à 0,0881** et l'ECE de **0,209 à 0,015**, **sans aucun jeu de calibration** et sans changer l'AUC. Cela explique l'ordonnée trouvée par Platt en 5.2.3 : $b=-1{,}79$, très proche de $\ln(0{,}163)=-1{,}81$. **Platt retrouve le décalage de prévalence tout seul.**

> 💡 **Quand faut-il corriger ?** Si vous n'utilisez que le **classement** (cibler les 20 % les plus à risque, ou calculer une AUC), le décalage est sans importance : l'ordre est conservé. Si vous utilisez la **probabilité** (calculer un seuil par les coûts comme en 5.1.7, estimer un nombre attendu de départs), il faut corriger ou recalibrer. Le même raisonnement vaut après un suréchantillonnage ou un sous-échantillonnage (section 4.3 et ➕ 4.5) : la prévalence apparente est celle de l'échantillon rééquilibré.

> ✅ **À retenir.**
> - Un modèle est **calibré** si $P(Y=1\mid\hat p=p)=p$. La calibration est indépendante de la discrimination (AUC).
> - Le **diagramme de fiabilité** la révèle ; l'**ECE** la résume mais est bruitée (≈ ±0,02 avec 240 clients par classe).
> - La régression logistique est calibrée par construction ; les forêts sont sous-confiantes ; un boosting trop entraîné est sur-confiant ; les poids de classes décalent la prévalence.
> - **Platt** (deux paramètres, sigmoïde) et la **régression isotonique** (escalier croissant, plus de données) recalibrent sur un jeu **séparé**.
> - Un décalage de prévalence se corrige exactement : cote × $\frac{\pi/(1-\pi)}{\pi'/(1-\pi')}$.
> - Une recalibration doit être **surveillée** : elle dépend de la population.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercices 5.7 et 5.8.


## 5.3 Interprétabilité

Un modèle de boosting de 150 arbres n'a pas de « formule » que l'on puisse lire. Pourtant, il faut pouvoir répondre à des questions simples : *quelles variables comptent ? Pourquoi ce client est-il signalé ? Le modèle a-t-il appris quelque chose de raisonnable, ou une erreur ?* Cette section présente les outils standard, du plus simple au plus fondé, et surtout leurs **limites**.

### 5.3.1 Expliquer quoi, et à qui ?

Une « explication » peut répondre à plusieurs questions, qu'il faut distinguer.

- **Globale ou locale.** Une explication *globale* décrit le comportement général du modèle (« la récence est la variable la plus déterminante »). Une explication *locale* décrit **une** prédiction (« ce client est signalé à 92 % surtout parce que sa dernière commande date de plus d'un an »).
- **Intrinsèque ou post hoc.** Certains modèles sont *interprétables par construction* : une régression logistique (chaque coefficient est un effet sur la cote, volume II, section 2.2), un arbre peu profond (section 2.2). Pour les autres, on applique après coup des méthodes qui interrogent le modèle comme une boîte noire.
- **Pour qui ?** La gérante veut une phrase ; le data scientist veut un diagnostic ; l'auditeur veut une traçabilité. L'explication utile dépend de l'usage.

Dans toute la section, le modèle expliqué est un **gradient boosting LightGBM** de 150 arbres (AUC de 0,902 et Brier de 0,0744 sur le jeu de test), entraîné sur les 7 200 clients d'entraînement.

> ⚠️ **Une explication explique le modèle, pas le monde.** Si le modèle dit « les clients de moins de 28 ans partent plus », l'explication le montrera fidèlement. Elle ne dit pas que *l'âge cause le départ* : elle dit que *le modèle utilise l'âge*. La confusion entre les deux est l'erreur la plus fréquente (voir 5.3.7).


### 5.3.2 L'importance par permutation

L'idée est d'une simplicité désarmante : **si une variable est utile, détruire son information doit dégrader le modèle**. On mesure la performance sur le jeu de test (ici l'AUC), puis on **mélange au hasard** les valeurs d'une seule variable (on casse son lien avec la cible et avec les autres variables) et l'on mesure à nouveau. La **baisse de performance** est l'importance de cette variable. On répète le mélange plusieurs fois (ici 5) pour obtenir un écart-type.

| Variable | Baisse d'AUC | Écart-type |
|---|---:|---:|
| `age` | 0,0655 | 0,0049 |
| `recence_jours` | 0,0612 | 0,0073 |
| `satisfaction_moy` | 0,0409 | 0,0029 |
| `montant_12m` | 0,0403 | 0,0047 |
| `part_achats_promo` | 0,0200 | 0,0022 |
| `programme_fidelite` | 0,0088 | 0,0034 |
| `nb_commandes_12m` | 0,0072 | 0,0013 |

Sept variables dominent ; les 40 autres (dont les 20 villes) pèsent chacune moins de 0,003. C'est cohérent avec ce qui a été programmé : l'âge (par un effet en U), la récence, la satisfaction, le montant et la part d'achats en promotion jouent un rôle central dans le départ.

La méthode a deux avantages : elle marche avec **n'importe quel modèle**, et elle mesure l'effet sur la **performance** (ce qui compte), pas sur la structure interne. Elle a aussi deux limites sérieuses.

> ⚠️ **Les variables corrélées se partagent l'importance.** Si deux variables portent la même information, mélanger l'une laisse l'autre compenser : aucune n'apparaît importante, alors que leur information l'est. Expérience : on ajoute au jeu une copie *bruitée* de `recence_jours` (corrélation de l'ordre de 0,99, écart-type du bruit de 15 jours). La récence valait seule 0,0612 d'AUC ; avec la copie, l'importance se répartit entre les deux variables (0,0189 pour l'originale et 0,0126 pour la copie, soit 0,0315 au total, la moitié de l'importance initiale), alors que l'AUC du modèle est pratiquement inchangée. Aucune des deux ne semble cruciale, et pourtant leur information l'est. **Ne concluez jamais « cette variable est inutile » d'une importance faible quand des variables voisines existent.**

> ⚠️ **L'importance n'est pas un effet.** L'importance dit « le modèle perd 0,06 d'AUC sans la récence », pas « la récence augmente (ou diminue) le risque ». Pour la *direction* de l'effet, il faut les outils suivants.

### 5.3.3 Effets moyens et individuels : PDP et ICE

Le **graphique de dépendance partielle** (PDP, *partial dependence plot*) répond à la question « *que fait le modèle quand je fais varier cette variable ?* ». On fixe la variable $x_j$ à une valeur $v$ pour **tous** les clients, on fait prédire le modèle, et l'on prend la moyenne des probabilités ; on répète pour une grille de valeurs $v$ :
$$\mathrm{PDP}_j(v)=\frac1n\sum_{i=1}^n\hat f\bigl(x_{ij}\!:=v,\ x_{i,-j}\bigr).$$
Si l'on ne moyenne pas, on obtient une courbe par client : ce sont les courbes **ICE** (*individual conditional expectation*). Le PDP est leur moyenne.


![À gauche : courbes ICE (40 clients, en bleu) et leur moyenne, le PDP (en orange), pour la récence. À droite : le même PDP calculé séparément pour les clients peu satisfaits et les autres.](figures/ch05-pdp-ice.png)

Le PDP de la récence est presque plat jusqu'à 100 jours (probabilité moyenne de 0,079 à 10 jours et de 0,087 à 100 jours), puis monte brutalement : 0,137 à 150 jours, 0,189 à 200 jours, 0,203 à 300 jours. Une lecture sans nuance conclurait que « le risque augmente avec la récence, surtout entre 100 et 200 jours ».

Les courbes ICE disent qu'**il y a quelque chose de plus**. Elles ne sont pas parallèles : le PDP moyenne des comportements très différents. Coupons les clients en deux groupes selon leur satisfaction. Pour les clients à satisfaction inférieure à 3,2 (17 % de l'échantillon), la probabilité moyenne passe de **0,135 à 100 jours à 0,549 à 200 jours** ; pour les autres, de **0,078 à 0,116**. C'est exactement ce qui avait été programmé : la récence ne devient dangereuse que combinée à une faible satisfaction. Un effet qui dépend d'une autre variable est une **interaction** ; le PDP seul l'aurait masquée, les ICE l'ont révélée.

> ⚠️ **Limite du PDP.** Fixer la récence à 365 jours *pour tous* les clients crée des clients irréalistes (un client qui a passé dix commandes le mois dernier et dont la dernière commande date d'un an). Le PDP suppose les variables indépendantes ; quand elles ne le sont pas, il évalue le modèle là où il n'a pas de données.

### 5.3.4 LIME : un modèle simple autour d'un client

**LIME** (*Local Interpretable Model-agnostic Explanations*) explique une prédiction individuelle en la **remplaçant localement par un modèle simple**. Pour un client $x_0$ :

1. on fabrique des milliers de clients fictifs *autour* de $x_0$ (en perturbant ses variables) ;
2. on fait prédire le modèle complexe sur ces clients fictifs ;
3. on ajuste une **régression linéaire pondérée** (les clients proches de $x_0$ comptent plus) pour approcher ces prédictions ;
4. les coefficients de cette régression sont l'explication.

Autrement dit, LIME minimise $\sum_k w_k\,\bigl(\hat f(z_k)-g(z_k)\bigr)^2$ sur des points $z_k$ voisins de $x_0$, avec $g$ linéaire (et parcimonieuse).


Prenons un client du jeu de test dont la probabilité de départ est de 0,548 (il est finalement resté). Avec la graine 0, LIME répond que ce risque s'explique par : récence supérieure à 148 jours (+0,147), âge inférieur à 28 ans (+0,133), part d'achats en promotion supérieure à 0,34 (+0,051), montant annuel inférieur à 40 € (+0,048), absence de programme de fidélité (+0,035). C'est une explication lisible, en phrases.

Mais relançons LIME avec d'autres graines, sur **le même client et le même modèle**. Les poids changent (avec la graine 1, l'âge passe de +0,133 à +0,115) et les variables retenues parmi les cinq premières ne sont pas toujours les mêmes : le recouvrement moyen (indice de Jaccard) entre les ensembles de cinq variables de deux graines est de 0,80, et il descend à 0,67 pour certaines paires. **Une explication qui varie avec la graine aléatoire n'est pas une explication stable.** LIME est utile pour *se faire une idée* d'un cas, pas pour le *justifier* devant un tiers sans vérification.

### 5.3.5 Les valeurs de Shapley

On aimerait une méthode qui répartisse la prédiction entre les variables de façon **équitable et sans ambiguïté**. La théorie des jeux coopératifs en a une, inventée par Lloyd Shapley en 1953.

**Le problème du partage.** Trois joueurs coopèrent et gagnent ensemble une somme. Comment partager le gain équitablement, sachant que chaque joueur contribue différemment, et que certains ne servent qu'en présence d'autres ? Ici, les « joueurs » sont des *variables* (la récence R, la satisfaction S et le nombre de tickets de support T), et le « gain » est la *probabilité de départ* prédite pour un client. On note $v(S)$ le gain qu'obtient la coalition $S$ de variables connues. Imaginons, pour un client donné, les valeurs suivantes :

| Coalition | $\varnothing$ | R | S | T | R, S | R, T | S, T | R, S, T |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $v$ | 0,14 | 0,30 | 0,20 | 0,15 | 0,62 | 0,34 | 0,22 | 0,66 |

($v(\varnothing)=0{,}14$ est la prévalence : le risque sans aucune information ; $v(R,S,T)=0{,}66$ est la prédiction du modèle quand on connaît tout.) La récence et la satisfaction ont un effet conjoint fort : $v(R,S)=0{,}62$, bien plus que $0{,}30+0{,}20-0{,}14=0{,}36$. Comment attribuer les $0{,}66-0{,}14=0{,}52$ de risque ?

**L'idée de Shapley.** Faisons arriver les variables **dans un ordre**, et comptons ce que chacune apporte en arrivant. Pour que l'ordre n'avantage personne, on prend la moyenne sur **tous les ordres possibles** (ici $3!=6$). Voici les apports marginaux de chaque variable :

| Ordre d'arrivée | Apport de R | Apport de S | Apport de T |
|---|---:|---:|---:|
| R, S, T | $0{,}30-0{,}14=0{,}16$ | $0{,}62-0{,}30=0{,}32$ | $0{,}66-0{,}62=0{,}04$ |
| R, T, S | $0{,}16$ | $0{,}66-0{,}34=0{,}32$ | $0{,}34-0{,}30=0{,}04$ |
| S, R, T | $0{,}62-0{,}20=0{,}42$ | $0{,}20-0{,}14=0{,}06$ | $0{,}04$ |
| S, T, R | $0{,}66-0{,}22=0{,}44$ | $0{,}06$ | $0{,}22-0{,}20=0{,}02$ |
| T, R, S | $0{,}34-0{,}15=0{,}19$ | $0{,}66-0{,}34=0{,}32$ | $0{,}15-0{,}14=0{,}01$ |
| T, S, R | $0{,}66-0{,}22=0{,}44$ | $0{,}22-0{,}15=0{,}07$ | $0{,}01$ |
| **Moyenne** | $\mathbf{1{,}81/6\approx0{,}302}$ | $\mathbf{1{,}15/6\approx0{,}192}$ | $\mathbf{0{,}16/6\approx0{,}027}$ |

La récence est responsable de 0,302 du risque, la satisfaction de 0,192 et les tickets de 0,027. Leur somme est $0{,}302+0{,}192+0{,}027=0{,}52=v(R,S,T)-v(\varnothing)$ : **le gain est exactement réparti, sans reste.**

> 📐 **Définition générale.** Pour un jeu à $p$ joueurs, la valeur de Shapley du joueur $j$ est
> $$\varphi_j=\sum_{S\subseteq N\setminus\{j\}}\frac{|S|!\,(p-|S|-1)!}{p!}\Bigl[v(S\cup\{j\})-v(S)\Bigr],$$
> la moyenne de son apport marginal sur tous les ordres d'arrivée. C'est **la seule** attribution qui vérifie quatre propriétés raisonnables : (1) **efficacité** : $\sum_j\varphi_j=v(N)-v(\varnothing)$ ; (2) **symétrie** : deux joueurs qui apportent la même chose à toutes les coalitions reçoivent la même valeur ; (3) **joueur nul** : un joueur qui n'apporte jamais rien reçoit zéro ; (4) **additivité** : si l'on additionne deux jeux, les valeurs s'additionnent.

Le calcul exact demande d'évaluer $2^p$ coalitions : impraticable pour 47 variables (plus de $10^{14}$ coalitions). C'est le rôle de SHAP.

### 5.3.6 SHAP : Shapley appliqué à un modèle

**SHAP** (*SHapley Additive exPlanations*) applique cette idée à un modèle : les « joueurs » sont les variables, et $v(S)$ est la **prédiction moyenne du modèle quand seules les variables de $S$ sont connues** (les autres étant intégrées sur leur distribution). On obtient, pour **chaque client et chaque variable**, une valeur $\varphi_{ij}$, avec la propriété d'efficacité :
$$\hat f(x_i)=\varphi_0+\sum_{j=1}^p\varphi_{ij},$$
où $\varphi_0$ est la **valeur de base** (la prédiction moyenne du modèle). Pour un classifieur à arbres, la prédiction est exprimée en *log-cote* ; une valeur positive augmente le risque, une valeur négative le diminue.

L'ingénieux **TreeSHAP** calcule ces valeurs **exactement** pour des arbres, en un temps polynomial, au lieu des $2^p$ coalitions. En pratique, deux lignes suffisent :

```python
import shap

explicateur = shap.TreeExplainer(mg)                 # mg : le modèle LightGBM entraîné plus haut
valeurs = explicateur.shap_values(Xte.iloc[:500])    # une valeur de Shapley par client et par variable
print(np.shape(valeurs), "| valeur de base (log-cote) :", round(float(np.ravel(explicateur.expected_value)[-1]), 3))
```
<!--sortie-->
```text
(500, 47) | valeur de base (log-cote) : -2.993
```


On obtient une matrice de 500 clients par 47 variables, et la valeur de base vaut $-2{,}993$ en log-cote, soit une probabilité de $0{,}048$. (Elle est très inférieure à la prévalence de 14 % : la valeur de base est la *moyenne des log-cotes*, et non la log-cote de la moyenne. Quelques clients très risqués tirent la moyenne des probabilités vers le haut sans déplacer beaucoup celle des log-cotes.) Vérifions l'efficacité : pour chaque client, la valeur de base plus la somme de ses 47 valeurs SHAP doit redonner exactement la sortie brute du modèle. L'écart maximal sur les 500 clients est de $10^{-14}$ : c'est de l'arrondi informatique. Rien n'est « approximatif » : l'explication est une **décomposition exacte** de la prédiction.

**Lecture globale.** La moyenne des valeurs absolues de SHAP par variable donne une importance globale, cette fois dans l'unité du modèle (la log-cote). En tête : l'âge (0,683), le montant annuel (0,648), la récence (0,558), la part d'achats en promotion (0,278), la satisfaction (0,267), le nombre de commandes (0,218) et le programme de fidélité (0,204). Le classement est proche de celui de la permutation, mais pas identique :

| Variable | Rang SHAP | Rang permutation |
|---|---:|---:|
| `age` | 1 | 1 |
| `montant_12m` | 2 | 4 |
| `recence_jours` | 3 | 2 |
| `part_achats_promo` | 4 | 5 |
| `satisfaction_moy` | 5 | 3 |
| `nb_commandes_12m` | 6 | 7 |
| `programme_fidelite` | 7 | 6 |
| `taux_ouverture_email` | 8 | 47 |
| `panier_moyen` | 10 | 45 |

L'écart le plus net concerne `taux_ouverture_email` (8ᵉ en SHAP, 47ᵉ en permutation) : cette variable a un effet **réel mais faible** sur chaque client, que SHAP restitue, mais qui ne se traduit que par une dégradation négligeable de l'AUC quand on la mélange. Ce sont deux questions différentes : SHAP répond à « *combien cette variable déplace-t-elle les prédictions ?* », la permutation à « *combien le modèle perd-il à l'ignorer ?* ».

![Résumé SHAP : un point par client (500 clients) et par variable ; position horizontale = effet sur la log-cote ; couleur = valeur de la variable (rouge : élevée).](figures/ch05-shap-resume.png)

![Dépendance de la valeur SHAP de la récence à la récence elle-même, colorée par la satisfaction.](figures/ch05-shap-dependance.png)

**Comment lire le résumé.** Chaque ligne est une variable, chaque point un client ; la position horizontale est l'effet du client sur la log-cote du départ (à droite : le risque augmente) et la couleur est la valeur de la variable pour ce client (rouge : élevée). On y retrouve ce qui a été programmé. La **récence** : les points rouges (longue absence) sont à droite, jusqu'à $+1{,}9$ ; les points bleus (achat récent) à gauche. La **satisfaction** : les clients peu satisfaits (points bleus) poussent le risque de $+0{,}3$ à $+1{,}5$, les clients satisfaits le diminuent légèrement. Le **montant annuel** : un montant élevé protège (jusqu'à $-1{,}1$), un montant nul ou faible expose. Le **programme de fidélité** : les membres (rouge) sont du côté protecteur. Enfin l'**âge** montre l'effet **en U** : les clients les plus jeunes (points bleus) ont des contributions fortement positives, qui atteignent $+2{,}2$, la zone centrale est négative, et quelques clients plus âgés (points rouges, à droite) retrouvent des contributions positives. Une courbe moyenne, ou une seule importance, n'aurait pas montré cette forme.

**Comment lire la dépendance.** Pour la récence, la contribution passe d'environ $-1$ (achat très récent) à $0$ vers 100 jours, puis grimpe nettement après 150 jours. Au-delà de 150 jours, les points se séparent verticalement selon leur couleur : les clients **peu satisfaits** (bleus) atteignent $+1{,}3$ à $+1{,}9$, les clients **satisfaits** (rouges ou violets) restent entre $+0{,}8$ et $+1{,}2$. C'est l'interaction repérée en 5.3.3, cette fois mesurée sur chaque client. L'empilement vertical à 365 jours correspond aux clients qui n'ont passé aucune commande dans l'année.

**Lecture locale.** Prenons, parmi les 500, le client le plus à risque. Sa sortie brute est de $2{,}398$ en log-cote (probabilité $0{,}917$), contre $-2{,}993$ pour la valeur de base (probabilité $0{,}048$). La différence, $5{,}39$, est répartie entre les variables : **récence** (365 jours, c'est-à-dire aucune commande depuis un an) $+1{,}78$, **satisfaction** (2,4) $+1{,}21$, **âge** (24 ans) $+0{,}77$, **montant annuel** (0 €) $+0{,}76$, **nombre de commandes** (0) $+0{,}28$, **ancienneté** (38 mois) $+0{,}22$, et d'autres plus petites. Chaque contribution est lisible par un non-spécialiste : « ce client est signalé parce qu'il n'a rien acheté depuis un an, qu'il est peu satisfait et qu'il est jeune ».

![Décomposition de la prédiction du client le plus à risque parmi les 500 : de la valeur de base aux 8 plus grandes contributions.](figures/ch05-shap-cas.png)

### 5.3.7 Les pièges de l'interprétation

**SHAP n'est pas de la causalité.** Les valeurs SHAP décrivent comment le *modèle* utilise les variables. Elles ne disent pas ce qui arriverait si l'on *intervenait* sur la variable. Que la satisfaction ait une forte contribution ne dit pas qu'augmenter la satisfaction fera baisser le départ ; cela relève de l'inférence causale (volume II, chapitre 7, facultatif).

**Les variables corrélées brouillent la lecture.** Comme en 5.3.2, quand deux variables portent la même information, SHAP la partage entre elles de façon dépendante du modèle. Lire « la variable A pèse deux fois plus que B » n'a de sens que si A et B sont à peu près indépendantes.

**Une explication peut être fausse sans que le modèle le soit.** Les explications dépendent d'hypothèses (la distribution de fond utilisée pour « supprimer » les variables, le nombre de perturbations de LIME…). Deux outils peuvent donner deux récits différents pour la même prédiction ; il faut le savoir.

**Mais l'interprétabilité sert aussi à débusquer les erreurs.** Rappelez-vous le piège du chapitre 1 : la colonne `commandes_apres_cible`, qui contient les commandes des trois mois *suivants*, donc l'avenir. Entraînons le même modèle en la laissant parmi les variables. L'AUC sur le jeu de test monte de 0,902 à **0,933**, ce qui est tentant. Mais SHAP trahit immédiatement le modèle : la première variable est `commandes_apres_cible` (importance moyenne 1,394), bien devant l'âge (0,531) et le montant annuel (0,452). Un modèle de prévision dont la variable la plus importante est une information du futur est un modèle qui triche. **Regardez toujours les variables que votre modèle juge les plus importantes : si l'une est suspecte, vous avez probablement une fuite d'information.**

> ✅ **À retenir.**
> - Distinguez l'explication **globale** et **locale**, et ce que l'on explique : le **modèle**, pas le monde.
> - L'**importance par permutation** mesure la perte de performance sans une variable ; elle est trompée par les variables corrélées.
> - **PDP** et **ICE** montrent *comment* une variable agit ; les ICE révèlent les interactions que le PDP moyenne.
> - **LIME** ajuste un modèle linéaire local : lisible, mais **instable** (varie avec la graine).
> - Les **valeurs de Shapley** répartissent la prédiction de façon unique (efficacité, symétrie, joueur nul, additivité) ; **TreeSHAP** les calcule exactement pour les arbres. Leur somme redonne la prédiction.
> - Utilisez l'interprétabilité comme **outil de diagnostic** : elle débusque les fuites d'information.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 et 5.7, exercices 5.9 et 5.10.


## 5.4 ➕ Pour aller plus loin : équité, biais et éthique

> 🧭 **Section optionnelle.** Elle suppose acquises les sections 5.1 (métriques) et 5.2 (calibration).

Un modèle peut être excellent « en moyenne » et traiter très différemment deux groupes de personnes. Quand ses décisions touchent des personnes (accorder un crédit, repérer des clients à relancer, trier des candidatures), cette différence n'est plus seulement un défaut technique : c'est une question de justice, et parfois de droit. Cette section ne prétend pas la résoudre. Elle apprend à la **mesurer**, à comprendre pourquoi **aucune mesure ne suffit seule**, et à discuter des remèdes avec honnêteté.

### 5.4.1 Un jeu de données réel, et un avertissement

Pour une fois, nous quittons la boutique : le sujet exige des données **réelles**, avec des attributs sensibles. Nous utilisons le jeu public « Default of Credit Card Clients » (Yeh et Lien, 2009 ; licence CC0) : **30 000 clients d'une banque de Taïwan en 2005**, dont 22,1 % ont fait défaut le mois suivant. Pour chaque client : le montant du crédit, le **sexe**, le niveau d'études, la situation matrimoniale, l'**âge**, six mois d'historique de remboursement (retards, factures, paiements) et la cible (le défaut). On entraîne un gradient boosting sur 70 % des clients, et l'on évalue sur les 9 000 autres.

> ⚠️ **Ce que cette étude est, et n'est pas.** C'est une illustration méthodologique sur un échantillon ancien et particulier. Les résultats décrivent *ce modèle sur ces données*. Ils ne disent rien sur les pratiques d'un établissement réel, ni sur ce qu'il faudrait faire ailleurs. Dans plusieurs pays, utiliser le sexe ou l'âge dans une décision de crédit est restreint ou interdit : le cadre juridique varie selon les lieux et les domaines, et ceci n'est pas un conseil juridique.

Le modèle atteint une AUC de **0,777** sur le jeu de test. Pour passer de scores à des décisions, on fixe un seuil qui **signale 25 % des dossiers** (les plus risqués), soit un score supérieur à 0,271 : par exemple, des dossiers à examiner de plus près.


### 5.4.2 Mesurer : les critères d'équité

Découpons le jeu de test par groupes. Voici ce que donne le modèle selon le **sexe** (1 = hommes, 2 = femmes dans les données d'origine) :

| Groupe | Effectif | Taux de défaut | Taux d'alerte | Rappel | Fausses alertes | Précision | Probabilité moyenne prédite | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Femmes | 5 353 | 0,206 | 0,234 | 0,571 | 0,147 | 0,502 | 0,213 | 0,780 |
| Hommes | 3 647 | 0,244 | 0,273 | 0,574 | 0,176 | 0,513 | 0,230 | 0,771 |


```python
alerte = s_avec >= t_alerte                                  # les 25 % de dossiers jugés les plus risqués
audit = pd.DataFrame({"sexe": g_sexe, "défaut": y5, "alerte": alerte})
print(audit.groupby("sexe").mean().round(3))                 # taux de défaut et taux d'alerte, par groupe
```
<!--sortie-->
```text
        défaut  alerte
sexe                  
femmes   0.206   0.234
hommes   0.244   0.273
```

Et selon l'**âge** (trois classes) :

| Groupe | Effectif | Taux de défaut | Taux d'alerte | Rappel | Fausses alertes | Précision | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Moins de 30 ans | 2 885 | 0,216 | 0,258 | 0,608 | 0,162 | 0,509 | 0,785 |
| 30 à 44 ans | 4 497 | 0,212 | 0,234 | 0,533 | 0,154 | 0,483 | 0,770 |
| 45 ans et plus | 1 618 | 0,255 | 0,279 | 0,610 | 0,165 | 0,559 | 0,781 |

Plusieurs définitions de l'équité circulent. Chacune compare une grandeur entre les groupes :

- **Parité démographique** : le **taux d'alerte** est le même dans tous les groupes. Elle ne regarde pas la réalité : elle compare seulement les décisions.
- **Égalité des chances** : le **rappel** (taux de vrais positifs) est le même. Parmi les clients qui feront défaut, chaque groupe est détecté dans la même proportion.
- **Cotes égalisées** (*equalized odds*) : le rappel **et** le taux de fausses alertes sont les mêmes. Parmi ceux qui ne feront pas défaut, chaque groupe est signalé à tort dans la même proportion.
- **Parité prédictive** : la **précision** est la même. Une alerte a la même probabilité d'être justifiée dans tous les groupes.
- **Calibration par groupe** : $P(Y=1\mid \hat p=p,\text{groupe})=p$ pour chaque groupe.

Mesurons les écarts maximaux entre groupes. Selon le **sexe**, le rappel est quasiment identique (0,571 contre 0,574 : écart de **0,003**), l'égalité des chances est donc presque réalisée ; mais le taux d'alerte diffère de **0,039** (23,4 % contre 27,3 %), et le taux de fausses alertes de **0,030** (14,7 % contre 17,6 %). Selon l'**âge**, le tableau est différent : l'écart de **rappel** est de **0,077** (les 30 à 44 ans sont moins bien détectés : 53,3 % contre 61 % pour les autres), et l'écart de précision de **0,076**.

> 💡 **Le même modèle paraît équitable ou non selon le critère.** Pour le sexe, il passe presque l'égalité des chances et échoue à la parité démographique ; pour l'âge, il échoue à l'égalité des chances. Aucun critère ne dit à lui seul si « le modèle est équitable ». Choisir le critère est un choix **de valeurs**, pas de statistique.

Une partie de l'écart de taux d'alerte entre hommes et femmes s'explique simplement : **les taux de défaut diffèrent dans les données** (24,4 % contre 20,6 %). Un modèle bien calibré signale davantage le groupe où le défaut est plus fréquent ; l'écart de taux d'alerte (0,039) est du même ordre que l'écart de taux de défaut (0,038). La calibration par groupe est d'ailleurs bonne : l'ECE vaut 0,0205 pour les hommes et 0,0144 pour les femmes ; elle est un peu moins bonne pour les 45 ans et plus (0,039, sur seulement 1 618 clients), alors qu'elle est de 0,016 et 0,020 pour les deux autres classes d'âge.

### 5.4.3 Supprimer la variable sensible ne suffit pas

La réaction la plus courante est : « *retirons le sexe des variables, le modèle ne pourra plus discriminer* ». C'est l'**équité par ignorance** (*fairness through unawareness*). Essayons.

L'AUC passe de 0,777 à 0,774 : le sexe apporte presque rien au pouvoir prédictif. Les écarts entre groupes diminuent un peu, sans disparaître : l'écart de taux d'alerte selon le sexe passe de 0,039 à **0,030**, celui de fausses alertes de 0,030 à 0,019, mais l'écart de **précision** *augmente*, de 0,011 à 0,025. Et surtout, l'information sexe **n'a pas disparu des autres variables** : un modèle entraîné à retrouver le sexe à partir des variables restantes (le niveau d'études, la situation matrimoniale, le montant du crédit, les habitudes de paiement…) atteint une AUC de **0,644**, nettement supérieure à 0,5. Les variables qui restent sont des **proxys** (substituts) du sexe.

> ⚠️ **Retirer une variable sensible n'efface ni le biais ni l'information.** Cela empêche seulement de la mesurer : sans la colonne « sexe », on ne peut plus auditer les écarts entre groupes. Il faut en général **garder** l'attribut pour l'audit, même si le modèle ne l'utilise pas pour décider.

### 5.4.4 Pourquoi on ne peut pas tout avoir

Peut-on exiger **à la fois** l'égalité des chances (même rappel), la parité prédictive (même précision) et l'égalité des fausses alertes ? En général, **non**, dès que les taux de défaut diffèrent entre les groupes. C'est un résultat mathématique, pas un défaut de modèle.

> 📐 **L'identité qui interdit de tout égaliser.** Pour un groupe de taux de défaut $p$, de précision $\mathrm{PPV}$, de rappel $1-\mathrm{FNR}$ et de taux de fausses alertes $\mathrm{FPR}$, on a, puisque ces quatre grandeurs sont des fonctions des mêmes quatre effectifs (VP, FP, FN, VN) :
> $$\mathrm{FPR}=\frac{p}{1-p}\cdot\frac{1-\mathrm{PPV}}{\mathrm{PPV}}\cdot(1-\mathrm{FNR}).$$
> En effet, $\mathrm{PPV}=\dfrac{VP}{VP+FP}$ donne $FP=VP\cdot\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}$ ; avec $VP=(1-\mathrm{FNR})\cdot pn$ et $\mathrm{FPR}=FP/((1-p)n)$, on retrouve la formule. **Si deux groupes ont la même précision et le même rappel mais des taux de défaut $p$ différents, ils ne peuvent pas avoir le même taux de fausses alertes.**

Vérifions sur nos données : pour les femmes ($p=0{,}2057$, précision 0,502, taux de faux négatifs 0,4287), la formule donne un taux de fausses alertes de 0,1468, exactement la valeur observée ; pour les hommes ($p=0{,}244$, précision 0,5125, taux de faux négatifs 0,4258), 0,1763, là aussi exactement la valeur observée. Imaginons maintenant les deux groupes avec la **même précision** (0,507) et le **même rappel** (0,573), moyennes des valeurs observées : la formule impose des fausses alertes de 0,144 pour les femmes et de 0,180 pour les hommes. L'écart de 0,036 est exigé par l'écart entre les taux de défaut.

> 💡 **Ce que cela signifie.** Il n'existe pas de modèle imparfait qui soit « équitable » pour tous les critères quand les taux de base diffèrent (c'est le résultat connu sous le nom de *théorème d'impossibilité* d'Alexandra Chouldechova et de Jon Kleinberg et ses coauteurs, 2016-2017). Il faut **choisir** quel type d'erreur doit être égalisé, et assumer ce choix.

### 5.4.5 Corriger : des seuils par groupe

L'une des corrections les plus simples est un **post-traitement** : utiliser un seuil **différent par groupe**. Comparons trois politiques pour le sexe, puis pour l'âge, dans un cadre de coûts où manquer un défaut coûte 5 unités et signaler à tort 1 unité :

| Politique | Variable | Seuils par groupe | Alertes | Coût pour 1 000 dossiers | Écart d'alerte | Écart de rappel | Écart de précision | Écart de fausses alertes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Seuil unique | sexe | 0,271 / 0,271 | 25,0 % | 596,1 | 0,039 | 0,003 | 0,011 | 0,030 |
| Égalité des chances | sexe | 0,267 (F) / 0,272 (H) | 25,1 % | 597,0 | 0,036 | 0,001 | 0,016 | 0,025 |
| Parité démographique | sexe | 0,256 (F) / 0,291 (H) | 25,0 % | 594,9 | 0,000 | 0,040 | 0,052 | 0,009 |
| Seuil unique | âge | 0,271 pour tous | 25,0 % | 596,1 | 0,044 | 0,077 | 0,076 | 0,011 |
| Égalité des chances | âge | 0,235 / 0,294 / 0,307 | 25,5 % | 601,1 | 0,036 | 0,002 | 0,143 | 0,054 |
| Parité démographique | âge | 0,255 / 0,277 / 0,302 | 25,0 % | 598,3 | 0,000 | 0,051 | 0,121 | 0,031 |

(Pour l'âge, les seuils sont dans l'ordre 30-44 ans, moins de 30 ans, 45 ans et plus.)

On lit trois choses. **Chaque politique égalise ce qu'elle vise** : la parité démographique annule l'écart de taux d'alerte, l'égalité des chances ramène l'écart de rappel de 0,077 à 0,002 pour l'âge. **Chaque politique dégrade autre chose** : en égalisant le rappel entre classes d'âge, l'écart de *précision* grimpe de 0,076 à 0,143 et l'écart de fausses alertes de 0,011 à 0,054 : c'est l'identité de 5.4.4 en action. Enfin, **le coût moyen varie peu** (entre 595 et 601 unités pour 1 000 dossiers) : ici, corriger les écarts ne coûte presque rien en performance globale. Ce n'est pas une règle générale.

![À gauche : courbes ROC par sexe sur le jeu réel ; à droite : calibration par classe d'âge. Les écarts sont faibles mais pas nuls.](figures/ch05-equite.png)

### 5.4.6 L'éthique commence où le calcul s'arrête

Les chiffres ci-dessus ne répondent pas aux questions qui comptent le plus.

- **La cible est-elle neutre ?** Ici, la cible est « a fait défaut ». Mais le défaut dépend des décisions de crédit passées (qui a obtenu un crédit, à quel montant), qui ont elles-mêmes pu être biaisées. Un modèle entraîné sur l'historique reproduit parfois ce qu'il a hérité, avec une apparence d'objectivité.
- **Qui est dans les données ?** Les clients refusés par le passé n'y figurent pas : on ne sait pas s'ils auraient remboursé. Le modèle est évalué sur les seuls dossiers qu'il a vus.
- **Quel critère, et qui le choisit ?** Les critères de 5.4.2 correspondent à des idées différentes de la justice, incompatibles dès que les taux de base diffèrent. Les arbitrer n'est pas une décision que le data scientist doit prendre seul.
- **Que fait-on des personnes concernées ?** Explication de la décision, droit de contestation, intervention humaine, suivi dans le temps : ce sont des éléments de la **gouvernance** du modèle, pas de ses statistiques.
- **Les boucles de rétroaction.** Un modèle qui refuse des crédits modifie les données de demain. Surveillez les écarts entre groupes **après** le déploiement, pas seulement avant.

> ✅ **À retenir.**
> - Auditez le modèle **par groupe** : taux d'alerte, rappel, fausses alertes, précision, calibration. Gardez l'attribut sensible pour l'audit.
> - Les critères (parité démographique, égalité des chances, cotes égalisées, parité prédictive) mesurent des choses **différentes** ; un même modèle peut en satisfaire un et pas l'autre.
> - Quand les taux de base diffèrent, on **ne peut pas** tout égaliser : $\mathrm{FPR}=\frac{p}{1-p}\cdot\frac{1-\mathrm{PPV}}{\mathrm{PPV}}\cdot(1-\mathrm{FNR})$.
> - **Retirer** la variable sensible ne suffit pas : des proxys subsistent.
> - Des **seuils par groupe** égalisent une grandeur au prix d'une autre. Le choix du critère est un choix de valeurs, à discuter avec toutes les parties concernées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.8 et 5.9, exercices 5.11 et 5.12.


## 5.5 ➕ Pour aller plus loin : quantifier l'incertitude, la prédiction conforme

> 🧭 **Section optionnelle.** Elle prolonge 5.2 (calibration) et 5.1.10 (prédire un quantile).

Un modèle de classification annonce « 62 % de risque de départ ». Un modèle de régression annonce « 83 € de dépense ». Dans les deux cas, **le modèle ne dit pas à quel point il peut se tromper**. La calibration (5.2) répare les probabilités, mais seulement approximativement, et sous l'hypothèse que la recalibration est bonne. La **prédiction conforme** (*conformal prediction*) propose autre chose : transformer *n'importe quel* modèle déjà ajusté en un modèle qui annonce non pas une valeur, mais un **ensemble** (en classification) ou un **intervalle** (en régression), avec une **garantie** de couverture valable à distance finie, sans hypothèse sur la loi des données.

### 5.5.1 L'objectif : une garantie de couverture

On se donne un niveau d'erreur $\alpha$ (par exemple $0{,}10$). On veut, pour un nouveau client, un ensemble $C(x)$ de réponses plausibles tel que
$$P\bigl(Y\in C(X)\bigr)\ \ge\ 1-\alpha.$$
En classification, $C(x)$ est un sous-ensemble des classes ({fidèle}, {partant}, ou les deux). En régression, c'est un intervalle $[\ell(x),u(x)]$. Cette probabilité porte sur le tirage du client *et* du jeu de calibration : on parle de **couverture marginale**.

### 5.5.2 La recette : la prédiction conforme « séparée »

La version la plus simple, dite **split conformal**, utilise trois jeux (ceux du fil rouge) : l'entraînement (pour ajuster le modèle), la **calibration** (pour mesurer ses erreurs), et le test (pour vérifier).

1. On ajuste le modèle sur le jeu d'entraînement.
2. On définit un **score de non-conformité** $s(x,y)$, qui est grand quand le couple $(x,y)$ est « surprenant » pour le modèle. En classification, on prend $s(x,y)=1-\hat p_y(x)$ : un moins la probabilité que le modèle attribuait à la **vraie** classe.
3. On calcule ce score pour chacun des $n$ clients du jeu de calibration, et l'on prend son **quantile** d'ordre $\lceil(n+1)(1-\alpha)\rceil/n$ : le $k$-ième plus petit score, avec $k=\lceil(n+1)(1-\alpha)\rceil$. Notons-le $\hat q$.
4. Pour un nouveau client, l'ensemble prédit est $C(x)=\{y:\ s(x,y)\le\hat q\}$ : toutes les classes dont le score ne dépasse pas $\hat q$.

**Un exemple à la main.** Neuf clients de calibration ($n=9$), $\alpha=0{,}20$. Leurs scores, triés : 0,05 ; 0,10 ; 0,14 ; 0,22 ; 0,31 ; 0,38 ; 0,47 ; 0,55 ; 0,71. On a $k=\lceil10\times0{,}8\rceil=8$ : $\hat q$ est le 8ᵉ score, **0,55**. Un client dont le modèle annonce $\hat p_{\text{partant}}=0{,}62$ donne le score $0{,}38$ pour la classe « partant » et $0{,}62$ pour « fidèle ». L'ensemble est $\{y:s\le0{,}55\}=\{\text{partant}\}$. Un autre client avec $\hat p_{\text{partant}}=0{,}48$ donne $0{,}52$ et $0{,}48$ : les deux sont $\le0{,}55$, l'ensemble est {fidèle, partant} : le modèle **avoue son hésitation**.

Appliquons cela aux 2 400 clients de calibration et au gradient boosting du chapitre, avec $\alpha=0{,}10$ :


```python
scores_cal = 1 - pcal[np.arange(len(ycal)), ycal]       # non-conformité : 1 - probabilité de la VRAIE classe, sur le jeu de calibration
k = int(np.ceil((len(scores_cal) + 1) * (1 - alpha)))   # rang du quantile : ⌈(n + 1)(1 - α)⌉
q = np.sort(scores_cal)[k - 1]                          # le k-ième plus petit score
ensembles = (1 - ptest) <= q                            # pour chaque client de test : les classes dont le score est <= q
couvert = ensembles[np.arange(len(y5c)), y5c]           # la vraie classe est-elle dans l'ensemble ?
print("k =", k, "sur", len(scores_cal), "| q =", round(q, 4), "| couverture :", round(couvert.mean(), 4))
```
<!--sortie-->
```text
k = 2161 sur 2400 | q = 0.5221 | couverture : 0.9025
```

C'est le 2 161ᵉ plus petit des 2 400 scores ($k=\lceil2401\times0{,}9\rceil=2\,161$) : $\hat q=0{,}5221$. Un client reçoit la classe $k$ dans son ensemble si la probabilité de cette classe est au moins $1-0{,}5221=0{,}4779$. En classification binaire, cela revient à dire : **si la probabilité de départ est comprise entre 0,478 et 0,522, on répond « les deux » ; sinon, on répond une seule classe**. Sur le jeu de test, 99,4 % des clients reçoivent une réponse unique, et 0,6 % reçoivent les deux ; la **couverture globale vaut 0,9025**, conforme à l'objectif de 90 %.

### 5.5.3 Pourquoi cela marche

La garantie est étonnamment simple à démontrer. Elle ne suppose **ni** que le modèle est bon, **ni** que les probabilités sont calibrées, **ni** une loi particulière : seulement que les données de calibration et le nouveau client sont **échangeables** (par exemple, tirés indépendamment de la même population).

> 📐 **Théorème (couverture du « split conformal »).** Soient $(X_i,Y_i)$, $i=1,\dots,n+1$, échangeables, et $s_i=s(X_i,Y_i)$ les scores calculés avec un modèle fixé indépendamment d'eux. Soit $\hat q$ le $k$-ième plus petit des $n$ scores de calibration, $k=\lceil(n+1)(1-\alpha)\rceil$ (par convention $\hat q=+\infty$ si $k>n$). Alors
> $$1-\alpha\ \le\ P\bigl(s_{n+1}\le\hat q\bigr)\ \le\ 1-\alpha+\frac1{n+1}\quad\text{(borne supérieure : si les scores sont presque sûrement distincts).}$$
>
> *Démonstration.* L'événement $\{s_{n+1}\le\hat q\}$ signifie que $s_{n+1}$ est au plus égal au $k$-ième plus petit des $n$ scores de calibration, c'est-à-dire que le **rang** de $s_{n+1}$ parmi les $n+1$ scores est au plus $k$. Par échangeabilité, les $n+1$ scores jouent des rôles symétriques : si les scores sont tous distincts, le rang de $s_{n+1}$ est **uniforme** sur $\{1,\dots,n+1\}$. La probabilité vaut donc $\dfrac{k}{n+1}=\dfrac{\lceil(n+1)(1-\alpha)\rceil}{n+1}\in\Bigl[1-\alpha,\ 1-\alpha+\dfrac1{n+1}\Bigr)$. S'il y a des égalités, le rang n'est plus uniforme mais $P(\text{rang}\le k)\ge\dfrac{k}{n+1}$, et la borne inférieure subsiste. $\blacksquare$

Remarquez ce que la démonstration n'utilise pas : le modèle, la calibration, la loi des données. Plus le modèle est bon, plus les ensembles sont **petits** ; mais la couverture, elle, est garantie quel que soit le modèle.

**La garantie, vue par simulation.** La couverture garantie est une moyenne sur le tirage du jeu de calibration : pour *un* jeu de calibration donné, la couverture réelle fluctue. On peut même dire comment : elle suit une **loi Bêta**$(k,\,n+1-k)$. Pour le voir, on mélange 1 000 fois les 4 800 clients des jeux de calibration et de test, on prend à chaque fois 300 clients pour calibrer et l'on mesure la couverture sur les 4 500 autres.


![Couverture sur le jeu de test pour 1 000 découpages aléatoires (300 clients de calibration à chaque fois), et densité de la loi Bêta théorique. La couverture fluctue, mais autour de 90 %.](figures/ch05-conforme-couverture.png)

Ici $n=300$ et $k=\lceil301\times0{,}9\rceil=271$ : la théorie donne une loi Bêta(271 ; 30), de moyenne $0{,}9003$ et d'écart-type $0{,}0172$. La simulation donne une moyenne de **0,9003** et un écart-type de **0,0177**, avec des couvertures allant de 0,841 à 0,945. La moyenne coïncide avec la théorie (0,9003, dans l'intervalle garanti $[0{,}9\,;\,0{,}9033]$) et l'écart-type est proche de 0,0172. La théorie décrit fidèlement l'expérience.

> 💡 **Combien de clients de calibration ?** Avec $n=300$, la couverture réelle d'un jeu de calibration donné peut tomber à 85 % ou monter à 94 % (± deux écarts-types : ±3,5 points). Avec $n=2\,400$, l'écart-type est de l'ordre de $0{,}006$. La garantie est valide pour tout $n$, mais plus $n$ est grand, plus la couverture *réelle* se rapproche de la couverture *annoncée*.

### 5.5.4 Garantie marginale, pas conditionnelle

Voici la nuance qui se perd le plus souvent. Calculons la couverture **séparément** pour chaque classe réelle :

| | Couverture | Taille moyenne de l'ensemble |
|---|---:|---:|
| **Globale** | 0,9025 | 1,006 |
| Parmi les clients qui **partent** | **0,4955** | |
| Parmi les clients qui restent | 0,969 | |

La couverture globale est de 90 %, mais elle est de **49,6 % seulement pour les clients qui partent**, ceux qui nous intéressent. Comment est-ce possible ? La garantie est *marginale* : elle moyenne sur tous les clients. Or 86 % des clients restent, et le modèle les couvre à 97 % ; cela suffit à atteindre 90 % en moyenne, même en laissant à découvert un partant sur deux. C'est l'analogue, en prédiction d'ensembles, du piège de l'exactitude de 5.1.2.

**Le remède : la prédiction conforme de Mondrian (conditionnelle à la classe).** On calcule un quantile **par classe** (en n'utilisant que les clients de calibration de cette classe). La garantie devient valable *dans chaque classe* :

| | LAC (global) | Mondrian |
|---|---:|---:|
| Couverture parmi les partants | 0,4955 | **0,9021** |
| Couverture parmi les fidèles | 0,969 | 0,9157 |
| Taille moyenne des ensembles | 1,006 | 1,213 |

Le prix : des ensembles plus gros (en moyenne 1,21 classe au lieu de 1,01), c'est-à-dire plus d'hésitations affichées. C'est normal : on ne peut pas être à la fois sûr de couvrir les partants à 90 % et de rester précis, avec un modèle dont l'AUC est de 0,90.

Il existe d'autres scores de non-conformité. Le score **APS** (*adaptive prediction sets*) cumule les probabilités des classes par ordre décroissant ; avec une petite part d'aléa, il donne ici une couverture de 0,900 et une taille moyenne de 1,107, avec 4,5 % d'ensembles vides. On note que le choix du score est un compromis entre taille des ensembles et homogénéité de la couverture.

### 5.5.5 En régression : des intervalles avec garantie

Le même principe s'applique à une cible numérique, ici la dépense à six mois. Le score est l'**erreur absolue** $s(x,y)=\lvert y-\hat f(x)\rvert$, et l'intervalle est $[\hat f(x)-\hat q,\ \hat f(x)+\hat q]$ (borné par zéro, une dépense ne pouvant être négative).


Avec $\alpha=0{,}10$, la demi-largeur est de $\hat q=142{,}4$ €. La couverture sur le jeu de test vaut **0,910**, conforme à la garantie. Mais le défaut est immédiat : **la largeur est la même pour tous les clients**, qu'ils soient de petits ou de gros dépensiers. Séparons les clients en trois tiers selon la dépense prévue :

| Tiers de la dépense prévue | Couverture (intervalle de largeur constante) | Couverture (CQR) | Largeur moyenne CQR |
|---|---:|---:|---:|
| Prévision basse | 0,994 | 0,922 | 74 € |
| Prévision moyenne | 0,975 | 0,916 | 138 € |
| Prévision haute | **0,760** | 0,892 | 344 € |

Les intervalles de largeur constante sont **trop larges** pour les petits clients (couverture de 99 %, soit un gaspillage de précision) et **trop étroits** pour les gros (76 %, bien en dessous de l'objectif). On préfère des intervalles qui s'adaptent. La **régression quantile conformalisée** (CQR) en offre un moyen : on entraîne d'abord deux modèles de régression quantile (aux niveaux 5 % et 95 %, avec la perte pinball de 5.1.10), qui fournissent un intervalle $[\hat\ell(x),\hat u(x)]$ de largeur variable. Mais, on l'a vu en 5.1.10, un quantile estimé n'a aucune garantie. On corrige donc par conformalisation : le score est $s(x,y)=\max\bigl(\hat\ell(x)-y,\ y-\hat u(x)\bigr)$ (négatif quand $y$ est dans l'intervalle), et l'intervalle final est $[\hat\ell(x)-\hat q,\ \hat u(x)+\hat q]$.

Ici, la correction est **exactement nulle** ($\hat q=0$) : les deux modèles quantiles couvraient déjà 90 % des clients de calibration. (Avec 36 % de clients à dépense nulle, le modèle du quantile à 5 % prédit exactement 0 pour beaucoup d'entre eux, et leur score de non-conformité est exactement 0.) La couverture est de **0,910**, la largeur moyenne de **185 €** (contre 210 € pour l'intervalle constant : des intervalles *plus courts* à couverture égale), et les couvertures par tiers sont beaucoup plus homogènes (0,92 ; 0,92 ; 0,89). La largeur s'adapte : 74 € pour les clients peu dépensiers, 344 € pour les gros.

![Intervalles à 90 % pour un client sur 24 trié par dépense prévue : largeur constante (à gauche) et CQR (à droite). Les points orange sont les dépenses réelles.](figures/ch05-conforme-regression.png)

### 5.5.6 Limites et bonnes pratiques

- **La couverture reste marginale.** Même avec CQR, la couverture parmi les clients dont la dépense est strictement positive n'est que de 0,860 (les 36 % de clients qui ne dépensent rien sont couverts à 100 % et relèvent la moyenne). Une garantie *conditionnelle* à un sous-groupe demande de calibrer sur ce sous-groupe (comme Mondrian) ou des méthodes plus avancées.
- **L'échangeabilité est une vraie hypothèse.** Si les clients de demain ne ressemblent pas à ceux de la calibration (changement de saison, de population), la garantie tombe. Surveillez la couverture empirique en production, et recalibrez.
- **La garantie ne remplace pas un bon modèle.** Un mauvais modèle donne des ensembles énormes ou des intervalles très larges : ils sont valides, mais inutiles. La largeur moyenne est donc, en soi, une mesure de qualité.
- **Il faut des données de calibration** (quelques centaines au minimum) que l'on ne peut pas réutiliser pour l'entraînement. La variante *cross-conformal* ou *jackknife+* évite de sacrifier des données, au prix d'un calcul plus lourd.

> ✅ **À retenir.**
> - La prédiction conforme transforme **n'importe quel modèle** en un modèle qui annonce un **ensemble** ou un **intervalle** avec une couverture garantie $\ge1-\alpha$.
> - Recette : un score de non-conformité, son quantile d'ordre $\lceil(n+1)(1-\alpha)\rceil/n$ sur un jeu de calibration séparé, puis l'ensemble $\{y:s(x,y)\le\hat q\}$.
> - La preuve ne demande que l'**échangeabilité** : le rang d'un score parmi $n+1$ est uniforme.
> - La garantie est **marginale** : elle peut cacher une couverture très faible pour une classe rare (49,6 % pour les partants !) ; la version de **Mondrian** la rend valable par classe.
> - En régression, des intervalles de largeur constante sont inadaptés ; **CQR** les rend adaptatifs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.10, exercices 5.13 et 5.14.


## Bilan du chapitre 5

Vous savez maintenant :

- **choisir la bonne mesure** : exactitude comparée au modèle « classe majoritaire », précision, rappel, $F_\beta$ et MCC pour une décision à seuil ; **AUC** (probabilité qu'un positif soit mieux classé qu'un négatif) et **précision moyenne** pour juger un score, la seconde étant la seule à voir la prévalence ; **log-loss** et **Brier** pour juger des probabilités ; MAE, RMSE, $R^2$ et perte pinball en régression, en évitant le MAPE quand la cible contient des zéros ;
- **transformer un score en décision** par les coûts, avec le seuil $t^\star=c/(sV)$, et lire le **gain** et le **lift** quand on raisonne en budget ;
- **vérifier la calibration** d'un modèle par un diagramme de fiabilité, comprendre pourquoi les forêts sont sous-confiantes, le boosting surajusté sur-confiant et les poids de classes décalent la prévalence, et **réparer** par la méthode de Platt, la régression isotonique ou la correction exacte d'un décalage de prévalence, sur un jeu séparé ;
- **expliquer un modèle** : importance par permutation (et son piège avec les variables corrélées), PDP et ICE, LIME (et son instabilité), **valeurs de Shapley** et SHAP, avec la propriété d'efficacité qui décompose exactement chaque prédiction ; et utiliser l'interprétabilité pour **débusquer une fuite d'information** ;
- (en option) **auditer l'équité** d'un modèle par groupe, comprendre qu'on ne peut pas égaliser à la fois rappel, précision et fausses alertes quand les taux de base diffèrent, et ne pas confondre retirer une variable sensible et supprimer le biais ;
- (en option) **quantifier l'incertitude** par la prédiction conforme : une garantie de couverture valable à distance finie pour n'importe quel modèle, mais marginale, et non conditionnelle.

Un fil conducteur traverse le chapitre : **une métrique, un seuil ou une explication ne valent que par la question à laquelle on les rattache**. L'AUC qui satisfait le data scientist, l'exactitude qui rassure le client et le seuil de 0,5 que l'on a toujours utilisé répondent à trois questions différentes ; aucune n'est « la » question de la gérante, qui est en euros.

Les chapitres complémentaires qui suivent appliquent ces outils à des problèmes particuliers : la détection d'anomalies et de fraude (chapitre 6, où la classe positive est extrêmement rare, donc où la courbe précision-rappel est reine), les systèmes de recommandation (chapitre 7), l'apprentissage semi-supervisé et actif (chapitre 8) et l'apprentissage par renforcement (chapitre 9).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.10 et exercices 5.1 à 5.14.
