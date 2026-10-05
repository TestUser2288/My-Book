# Chapitre 2 : Apprentissage supervisé

> « Tous les modèles de ce chapitre font la même chose : ils apprennent une règle à partir d'exemples dont on connaît la réponse. Ils ne diffèrent que par la **forme** de la règle qu'ils savent écrire. »

Le chapitre 1 a installé la démarche : poser le problème, réserver des données pour juger, valider, se méfier du surapprentissage. Il est temps de rencontrer les **modèles** eux-mêmes. Nous allons les parcourir comme une échelle : chaque barreau corrige un défaut du précédent.


## Le chemin de ce chapitre

- **2.1 Modèles linéaires et logistiques** : le modèle le plus simple, revu avec les yeux de l'apprentissage automatique : une **fonction de perte**, un algorithme (la descente de gradient) et une **pénalité**.
- **2.2 Arbres de décision** : des règles « si… alors… » apprises automatiquement ; ils capturent les **seuils** et les **interactions** qu'un modèle linéaire ignore, mais ils sont instables.
- **2.3 Forêts aléatoires** : on moyenne beaucoup d'arbres différents ; la variance s'effondre.
- **2.4 Gradient boosting** : on construit les arbres l'un après l'autre, chacun corrigeant les erreurs des précédents. C'est, aujourd'hui, la famille la plus performante sur les données tabulaires. XGBoost et LightGBM en sont les deux implémentations vedettes.
- ➕ **2.5 SVM, k plus proches voisins, Bayes naïf** : trois idées classiques, utiles à connaître.
- ➕ **2.6 CatBoost, stacking et blending** : aller plus loin, et combiner des modèles sans tricher.

> 💡 **L'idée directrice : un seul problème, plusieurs règles.** Dans tout le chapitre, nous posons **la même question** aux **mêmes données**, avec le **même découpage** et la **même mesure de réussite**. Seul le modèle change. Cela permet de comparer honnêtement, et de voir ce que chaque famille apporte (ou n'apporte pas).

## Le problème qui nous accompagne

La gérante veut savoir, parmi ses clients, **lesquels vont cesser de commander** dans les 90 jours qui viennent, afin de leur proposer une attention particulière (un message, une offre). C'est le problème de **résiliation** (*churn*) : prédire une variable à deux issues, `churn_90j` ∈ {0, 1}, à partir de ce que l'on sait du client aujourd'hui.

Les données (décrites dans l'introduction du volume) sont un tableau `clients_ml.csv` de 12 000 clients, avec 19 variables d'entrée : âge, ville (20 modalités), canal d'acquisition, ancienneté, nombre de commandes et montant des 12 derniers mois, récence (jours depuis la dernière commande), retours, satisfaction, tickets au support, programme de fidélité, promotions reçues, ouverture des courriels, délai de livraison… Certaines valeurs sont **manquantes** (13 % des satisfactions, par exemple). Environ 14 % des clients partent : le problème est **déséquilibré** sans l'être extrêmement (le chapitre 4 traitera les cas plus durs).

Conformément au chapitre 1, nous avons mis de côté un **jeu de test** (3 000 clients, un quart des données, tiré au hasard en conservant la proportion de départs) que nous n'utiliserons qu'à la fin, pour juger. Le **jeu d'entraînement** compte 9 000 clients ; quand il faut choisir un réglage, nous le faisons par validation croisée **à l'intérieur** de ce jeu (volume III, section 1.2).

> ⚠️ **Une colonne à ne pas toucher.** Le fichier contient aussi `commandes_apres_cible`, le nombre de commandes des trois mois **suivants**. Elle contient la réponse en filigrane : un modèle qui l'utilise paraît parfait et ne servira à rien le jour où l'on prédit réellement l'avenir. C'est la **fuite d'information** (volume III, section 1.1). Nous l'excluons, avec les autres cibles, de toutes les variables d'entrée.

## Ce qu'« apprendre » veut dire

Un modèle supervisé est, au fond, **une fonction** $f$ qui associe à un client $x$ (le vecteur de ses caractéristiques) une prédiction $f(x)$. Pour choisir $f$, on dispose de $n$ exemples $(x_i,y_i)$ et de trois ingrédients :

1. une **famille de fonctions** $\mathcal F$ (les droites, les arbres, les sommes d'arbres…) : c'est ce que le modèle *sait écrire* ;
2. une **perte** $\ell\bigl(y,f(x)\bigr)$, qui mesure le coût d'une erreur ;
3. un **algorithme** qui cherche, dans $\mathcal F$, la fonction de perte moyenne minimale sur les exemples (la minimisation du **risque empirique**) : $\hat f=\arg\min_{f\in\mathcal F}\frac1n\sum_i\ell\bigl(y_i,f(x_i)\bigr)$, souvent additionnée d'une pénalité qui limite la complexité.

Les sections suivantes varient ces trois ingrédients. Retenons dès maintenant la leçon du chapitre 1 : plus la famille $\mathcal F$ est riche, mieux elle ajuste les données d'entraînement, et plus elle risque d'apprendre le bruit. **Le bon modèle n'est pas le plus riche : c'est celui dont la richesse est adaptée à la quantité de données et à la structure du phénomène.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : les applications 2.1 à 2.10 et les exercices 2.1 à 2.12 accompagnent les sections de ce chapitre ; chaque section renvoie aux siens.


## 2.1 Modèles linéaires et logistiques vus sous l'angle du ML

> 💡 **Intuition.** Le modèle linéaire est le **point de départ obligé** : simple, rapide, lisible, souvent étonnamment bon. Mais l'apprentissage automatique ne le regarde pas comme la statistique : il y voit une **famille de fonctions**, une **perte** à minimiser et un **algorithme** (la descente de gradient) qui fait descendre cette perte pas à pas. Ces trois mots reviendront dans tout le chapitre.

Le volume II a déjà présenté la régression logistique (volume II, section 2.2) et la régularisation (volume II, section 1.5) avec les yeux du statisticien : un modèle probabiliste, des coefficients, des tests. Nous ne le refaisons pas. Nous posons une autre question : **que se passe-t-il quand le but est de prédire, et pas d'expliquer ?**

### 2.1.1 Une perte pour chaque philosophie

Un modèle linéaire calcule un **score** $f(x)=w^\top x+b$ : une somme pondérée des caractéristiques du client. Pour un problème à deux classes, on note $y\in\{-1,+1\}$ et on regarde la **marge**

$$m=y\,f(x).$$

Une marge positive signifie « bien classé » (le score et la réalité ont le même signe) ; plus elle est grande, plus le modèle est sûr de lui à raison ; une marge négative est une erreur, d'autant plus grave qu'elle est grande en valeur absolue.

Une **fonction de perte** attribue un coût à chaque marge. Le coût qui nous intéresse vraiment est le **0-1** : 1 si l'on se trompe, 0 sinon. Hélas, il est plat presque partout (sa pente est nulle) et il saute en $m=0$ : on ne sait pas le minimiser avec une descente de gradient. On le remplace donc par un **substitut convexe** qui le majore :

| Perte | Formule en fonction de la marge $m$ | Usage typique |
|---|---|---|
| 0-1 | $\mathbf 1[m\le 0]$ | ce que l'on voudrait minimiser |
| Charnière (*hinge*) | $\max(0,\,1-m)$ | SVM (section 2.5) |
| Logistique | $\ln\bigl(1+e^{-m}\bigr)$ | régression logistique, boosting |
| Quadratique | $(1-m)^2$ | moindres carrés appliqués à la classification |


![Quatre fonctions de perte en fonction de la marge. La perte 0-1 est un escalier ; les trois autres la majorent et sont convexes, donc minimisables par descente de gradient.](figures/ch02-pertes.png)

```text
 marge  0-1  charnière  logistique  quadratique
  -2.0    1        3.0       2.127          9.0
  -1.0    1        2.0       1.313          4.0
   0.0    1        1.0       0.693          1.0
   1.0    0        0.0       0.313          0.0
   2.0    0        0.0       0.127          1.0
```

Lisez les lignes du tableau : pour une marge de $-2$ (une erreur franche), la perte logistique vaut environ 2,13 et la charnière 3 ; pour une marge de $+2$ (bien classé avec assurance), la charnière tombe à **0** (elle ne se soucie plus de cet exemple) tandis que la logistique reste faiblement positive (0,127) : elle continue à *pousser* un peu pour augmenter la confiance. La perte quadratique, elle, punit aussi les marges **très positives** ($(1-3)^2=4$) : elle déteste les clients « trop bien classés », ce qui n'a aucun sens pour la classification.

> 💡 **Le choix de la perte est un choix de modèle.** Charnière + pénalité $\ell_2$ = SVM. Logistique = régression logistique = maximum de vraisemblance d'un modèle de Bernoulli (volume II, section 2.2). Exponentielle $e^{-m}$ = AdaBoost. Même famille de fonctions (le score linéaire), algorithmes et comportements différents.

### 2.1.2 La régression logistique, une perte et un gradient

Pour la régression logistique, on code plutôt $y\in\{0,1\}$ et l'on note $p_i=\sigma(f(x_i))=1/(1+e^{-f(x_i)})$ la probabilité prédite. La perte moyenne est l'opposé de la log-vraisemblance :

$$L(w,b)=-\frac1n\sum_{i=1}^n\Bigl[y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr].$$

> 📐 **Le gradient, en deux lignes.** Posons $\ell(f)=-y\ln\sigma(f)-(1-y)\ln\bigl(1-\sigma(f)\bigr)$. Comme $\sigma'(f)=\sigma(f)\bigl(1-\sigma(f)\bigr)$, on obtient
> $$\frac{\partial\ell}{\partial f}=-\frac{y}{\sigma}\,\sigma(1-\sigma)+\frac{1-y}{1-\sigma}\,\sigma(1-\sigma)=-y(1-\sigma)+(1-y)\sigma=\sigma(f)-y=p-y.$$
> Par la règle de la chaîne, $f=w^\top x+b$ donne
> $$\nabla_wL=\frac1n\sum_i(p_i-y_i)\,x_i,\qquad \frac{\partial L}{\partial b}=\frac1n\sum_i(p_i-y_i).$$
> L'**erreur de prédiction** $p_i-y_i$ pondère chaque client : un client que l'on prédit à 0,9 alors qu'il n'est pas parti ($y=0$) tire fort le modèle vers le bas ; un client bien prédit ($p_i\approx y_i$) ne le tire presque pas. Le Hessien, $\frac1nX^\top\operatorname{diag}\bigl(p_i(1-p_i)\bigr)X$, est semi-défini positif : la perte est **convexe**, elle n'a **qu'un seul** minimum, et la descente de gradient le trouve. (On retrouve ici les équations du maximum de vraisemblance du volume II ; la différence est que l'on cherche maintenant à les *résoudre par un algorithme*, sans formule fermée.)

### 2.1.3 La descente de gradient : un pas à la main

La descente de gradient répète : $w\leftarrow w-\eta\,\nabla_wL$, où $\eta>0$ est le **pas** d'apprentissage (volume I, section 1.3.3). Voyons un pas, sur un jeu de données minuscule : quatre clients, une seule variable $x$ (une « note de risque ») et la réponse $y$ (1 = parti).

| Client | $x$ | $y$ |
|---|---|---|
| 1 | −2 | 0 |
| 2 | −1 | 0 |
| 3 | 1 | 1 |
| 4 | 3 | 1 |

On part de $w=0$, $b=0$. Alors $f=0$ partout et $p_i=\sigma(0)=0{,}5$ pour les quatre clients. Les erreurs de prédiction valent $p_i-y_i=(0{,}5,\ 0{,}5,\ -0{,}5,\ -0{,}5)$. Donc

$$\nabla_wL=\frac14\bigl[0{,}5(-2)+0{,}5(-1)-0{,}5(1)-0{,}5(3)\bigr]=\frac{-3{,}5}{4}=-0{,}875,\qquad \frac{\partial L}{\partial b}=\frac14(0{,}5+0{,}5-0{,}5-0{,}5)=0.$$

Avec un pas $\eta=0{,}5$, le nouveau coefficient est $w=0-0{,}5\times(-0{,}875)=0{,}4375$ (et $b$ ne bouge pas). La perte initiale vaut $\ln2\approx0{,}693$ ; après le pas, elle baisse.


La perte passe de 0,693 à 0,396 : un seul pas a déjà nettement amélioré le modèle. Répétés des centaines de fois, ces pas convergent vers le minimum. Dans la **descente de gradient stochastique** (SGD), on ne calcule pas le gradient sur tous les clients mais sur un petit paquet tiré au hasard (un *mini-lot*) : chaque pas est bruité, mais il est $n/\text{taille du lot}$ fois moins cher, ce qui rend l'apprentissage possible sur des millions de lignes. C'est la méthode d'entraînement de presque tous les modèles à grande échelle, des modèles linéaires aux réseaux de neurones.

### 2.1.4 Pourquoi il faut mettre les variables à l'échelle

Sur nos données, la **récence** s'exprime en jours (de 0 à 365), le **nombre de commandes** est de l'ordre de la dizaine, le taux d'ouverture des courriels est entre 0 et 1. Une descente de gradient sur de telles variables brutes est un cauchemar : le gradient est dominé par la variable aux grandes valeurs, et le pas $\eta$ qui évite l'explosion pour celle-là est ridiculement petit pour les autres.

Formellement, la vitesse de convergence dépend du **conditionnement** $\kappa$, le rapport entre la plus grande et la plus petite valeur propre du Hessien de la perte au voisinage du minimum : pour une perte quadratique, l'erreur est multipliée par $\frac{\kappa-1}{\kappa+1}$ à chaque pas au mieux. Plus $\kappa$ est grand, plus la descente zigzague.


Sur un modèle à deux variables seulement (la récence et le nombre de commandes), le conditionnement du Hessien est d'environ 377 486 avec les variables brutes, et de 13,6 une fois les variables **standardisées** (moyenne 0, écart-type 1). Le graphique montre la conséquence : avec le plus grand pas de la grille pour lequel la perte décroît sans osciller (0,000), la perte vaut encore 0,50 après 400 itérations (le minimum est 0,342), tandis que la descente sur variables standardisées atteint 0,342, soit le minimum à quelques millièmes près.

![Écart à la perte minimale au fil des itérations, pour la même descente de gradient. Orange : variables brutes (le pas doit rester minuscule). Bleu : variables standardisées.](figures/ch02-gradient-echelle.png)

> ⚠️ **Standardiser n'est pas facultatif… pour certains modèles.** Les modèles entraînés par descente de gradient (linéaire, logistique, réseaux de neurones), à pénalité (Ridge, Lasso) ou fondés sur des **distances** (k plus proches voisins, SVM) exigent des variables à des échelles comparables. Les **arbres** et leurs dérivés (forêts, boosting) n'en ont pas besoin : ils ne comparent une variable qu'à des seuils, et une transformation croissante (changer l'unité, passer au logarithme) ne change ni l'ordre ni donc les découpages. Le chapitre 4 reviendra sur ces règles en détail (section 4.1).

### 2.1.5 La pénalité : une contrainte déguisée

Quand les variables sont nombreuses ou corrélées, les coefficients de la régression logistique peuvent devenir grands, instables, et le modèle sur-apprend. On ajoute à la perte une **pénalité** :

$$\min_{w,b}\ L(w,b)+\lambda\,\Omega(w),\qquad \Omega(w)=\|w\|_2^2\ \text{(Ridge)}\quad\text{ou}\quad\|w\|_1=\sum_j|w_j|\ \text{(Lasso)}.$$

> 📐 **Pénalité et contrainte, deux visages du même problème.** Par la théorie des multiplicateurs de Lagrange (volume I, section 1.3.5), minimiser $L+\lambda\Omega$ revient à minimiser $L$ **sous la contrainte** $\Omega(w)\le t$, avec $t$ qui décroît quand $\lambda$ croît. Choisir un $\lambda$ plus grand, c'est se limiter à un plus **petit domaine** de coefficients possibles : le modèle est moins riche, donc moins sujet au surapprentissage. Le domaine $\|w\|_2\le t$ est un **disque** ; le domaine $\|w\|_1\le t$ est un **losange** dont les sommets sont sur les axes. La solution est le point où les courbes de niveau de la perte touchent le domaine. Sur un disque, ce point est « n'importe où » ; sur un losange, il est très souvent **à un sommet**, c'est-à-dire avec **un coefficient exactement nul**. D'où la propriété du Lasso : il **sélectionne** des variables.


![Courbes de niveau d'une perte (bleu) et domaine autorisé (orange) pour une pénalité l2 (disque) et l1 (losange). La solution du Lasso tombe sur un sommet du losange, où un coefficient est nul.](figures/ch02-ridge-lasso-geometrie.png)

Un cas simple permet de voir le mécanisme sans algorithme : si les variables sont orthonormées et la perte quadratique, le Lasso **seuille** les coefficients estimés $z_j$ : $\hat w_j=\operatorname{signe}(z_j)\,(|z_j|-\lambda)_+$, alors que Ridge les **rétrécit** : $\hat w_j=z_j/(1+\lambda)$. Avec $z=(3;\,0{,}8;\,-0{,}3)$ et $\lambda=0{,}5$, le Lasso donne $(2{,}5;\ 0{,}3;\ 0)$ (la petite variable disparaît) et Ridge donne $(2;\ 0{,}533;\ -0{,}2)$ (toutes survivent, rétrécies).

Sur la résiliation, voyons ce que fait le Lasso quand on fait varier la force de la pénalité. En `scikit-learn`, le réglage se nomme `C` et vaut l'**inverse** de la force : un petit `C` donne une forte pénalité.


```text
           AUC l1  AUC l2  nb coef. l1  nb coef. l2
C                                                  
0.001000   0.5000  0.8465          1.0         49.0
0.003162   0.8244  0.8512          5.0         49.0
0.010000   0.8487  0.8557          9.0         49.0
0.031623   0.8561  0.8587         12.0         49.0
0.100000   0.8587  0.8602         25.0         49.0
0.316228   0.8604  0.8605         40.0         49.0
1.000000   0.8604  0.8603         42.0         49.0
3.162278   0.8602  0.8602         43.0         49.0
10.000000  0.8602  0.8602         44.0         49.0
```

Lisez le tableau : avec une pénalité $\ell_1$ très forte ($C=0{,}001$), **un seul** coefficient sur 49 reste non nul et l'AUC en validation croisée tombe au hasard (0,5) ; en relâchant la pénalité, le nombre de coefficients non nuls remonte (44 sur 49 pour le $C$ le plus grand testé), et l'AUC en validation croisée grimpe jusqu'à un plateau. Le meilleur réglage ici est une pénalité **l2** avec $C=$ 0,316 (AUC de validation croisée 0,861). L'écart avec le modèle presque non pénalisé est minuscule : avec 9 000 clients et un nombre raisonnable de variables, la régularisation ne change pas grand-chose à la **précision** ; elle sert surtout à **stabiliser** les coefficients et, pour $\ell_1$, à **réduire** le modèle.

Voici le modèle de référence que nous garderons pour tout le chapitre : une régression logistique avec imputation médiane (et indicateurs de valeur manquante), standardisation et encodage des catégories, évaluée sur le jeu de test.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

logistique = make_pipeline(pre_lin, LogisticRegression(C=1.0, max_iter=1000))
logistique.fit(Xtr, ytr)
print(round(roc_auc_score(yte, logistique.predict_proba(Xte)[:, 1]), 4))
```
<!--sortie-->
```text
0.8656
```

(Ici, `pre_lin` est le prétraitement décrit ci-dessus : imputation, standardisation, encodage.)


Avec une **AUC** de 0,866 sur le jeu de test (l'aire sous la courbe ROC : la probabilité qu'un client parti ait un score plus élevé qu'un client resté ; 0,5 = hasard, 1 = parfait ; chapitre 5, section 5.1), ce modèle de référence est déjà solide. Voyons maintenant ce qu'il **ne sait pas** faire.

### 2.1.6 Ce qu'un score linéaire ne sait pas écrire

Un score linéaire est une **somme** : chaque variable pousse le résultat dans un sens, indépendamment des autres, et proportionnellement à sa valeur. Il ne peut donc exprimer ni une **interaction** (« le risque explose quand *à la fois* la récence est grande *et* la satisfaction est basse ») ni un **seuil** (« rien ne se passe avant 150 jours, puis tout change »).

L'exemple d'école est le « ou exclusif » (XOR) : la classe dépend du **signe du produit** de deux variables.


![Deux classes disposées en damier : la classe dépend du signe du produit des deux variables. Aucune droite ne les sépare.](figures/ch02-xor.png)

Une régression logistique sur ces deux variables obtient une AUC de 0,503 : **le hasard**. Aucune droite ne sépare un damier. Pourtant, si l'on **ajoute à la main** la variable « produit » $x_1x_2$, l'AUC passe à 0,936. L'information était là ; c'est la **forme** de la règle qui manquait. Il existe deux réponses : fabriquer à la main les bonnes variables (les interactions, les seuils : c'est l'*ingénierie des variables* du chapitre 4), ou utiliser un modèle capable d'écrire des règles non linéaires **tout seul**. Les arbres sont le premier de ces modèles.

> ✅ **À retenir.**
> - Un modèle supervisé = **famille de fonctions + perte + algorithme**. Le modèle linéaire calcule un score $w^\top x+b$ ; la perte logistique (ou charnière) remplace le coût 0-1, non minimisable.
> - Le gradient de la perte logistique est $\frac1n\sum(p_i-y_i)x_i$ ; la **descente de gradient** (et sa version stochastique, la SGD) le suit pas à pas. Elle exige des variables **à l'échelle** : le conditionnement du problème en dépend.
> - **Pénalité = contrainte** : Ridge (disque) rétrécit, Lasso (losange) met des coefficients à zéro. `C` est l'inverse de la force de pénalisation.
> - Un score linéaire **ne peut exprimer ni interaction ni seuil** ; sur la résiliation, il fournit pourtant une référence honorable (AUC 0,866).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1 (descente de gradient écrite à la main) et application 2.2 (chemins de régularisation), exercices 2.1 à 2.3.


## 2.2 Arbres de décision

> 💡 **Intuition.** Un arbre de décision, c'est le **questionnaire** que ferait un conseiller expérimenté : « Le client a-t-il commandé il y a plus de 140 jours ? Si oui, est-il satisfait ? Si non, rien à craindre. » Chaque question coupe l'ensemble des clients en deux groupes plus homogènes, et l'on recommence dans chaque groupe. L'arbre **apprend lui-même** les questions à poser, leur ordre et les seuils.

Les arbres ont trois qualités qui expliquent leur succès : ils sont **lisibles** (on peut tracer l'arbre et le raconter), ils n'exigent **ni mise à l'échelle ni imputation** pour fonctionner, et surtout ils écrivent des **règles non linéaires** : seuils, interactions, effets qui changent de sens selon la zone. Leur défaut, nous le verrons, est l'**instabilité**. C'est ce défaut que corrigeront les forêts (section 2.3) et le boosting (section 2.4).

### 2.2.1 Un arbre minuscule, entièrement à la main

Voici dix clients, décrits par la récence (jours depuis la dernière commande), la satisfaction (de 1 à 5) et le fait d'être partis dans les 90 jours.

| Client | Récence | Satisfaction | Parti |
|---|---|---|---|
| 1 | 15 | 4,5 | 0 |
| 2 | 30 | 3,0 | 0 |
| 3 | 45 | 4,0 | 0 |
| 4 | 70 | 4,1 | 0 |
| 5 | 95 | 3,1 | 0 |
| 6 | 120 | 4,4 | 0 |
| 7 | 160 | 3,0 | 1 |
| 8 | 200 | 4,3 | 0 |
| 9 | 260 | 2,9 | 1 |
| 10 | 320 | 3,8 | 1 |

Trois clients sur dix sont partis. Nous cherchons **la meilleure première question**, de la forme « la variable $j$ est-elle inférieure ou égale au seuil $s$ ? ». Pour la comparer à d'autres, il nous faut une mesure de l'**homogénéité** d'un groupe.

### 2.2.2 Mesurer l'impureté

Dans un groupe où une proportion $p$ de clients sont partis, on veut une mesure qui vaut 0 quand le groupe est **pur** ($p=0$ ou $p=1$) et qui est maximale quand il est le plus mélangé ($p=\frac12$). Les trois mesures usuelles, pour deux classes, sont :

| Mesure | Formule | Valeur maximale (en $p=\frac12$) |
|---|---|---|
| Impureté de **Gini** | $G=1-p^2-(1-p)^2=2p(1-p)$ | 0,5 |
| **Entropie** (en bits) | $H=-p\log_2p-(1-p)\log_2(1-p)$ | 1 |
| Taux d'erreur | $E=\min(p,1-p)$ | 0,5 |

L'impureté de Gini est celle qu'utilise `scikit-learn` par défaut. Elle s'interprète ainsi : c'est la probabilité de se tromper si l'on attribue au hasard à un client une étiquette tirée dans le groupe. L'entropie mesure l'information (en bits) qui manque pour connaître l'issue. En pratique, Gini et entropie donnent presque toujours des arbres très voisins ; le taux d'erreur, lui, est trop « plat » pour guider la construction.


![Impureté d'un groupe en fonction de la proportion de clients partis. Gini et entropie (divisée par deux pour tenir à l'échelle) ont la même allure en cloche ; le taux d'erreur est une tente à pointe.](figures/ch02-impuretes.png)

Pour notre groupe de dix clients ($p=0{,}3$), l'impureté de Gini vaut $1-0{,}3^2-0{,}7^2=1-0{,}09-0{,}49=0{,}42$ et l'entropie $-0{,}3\log_20{,}3-0{,}7\log_20{,}7\approx0{,}881$ bit.

### 2.2.3 Le meilleur découpage : un par un

Une question « récence $\le s$ ? » coupe les clients en un groupe de gauche (de taille $n_G$) et un groupe de droite ($n_D$). Sa qualité est la **diminution d'impureté** :

$$\text{gain}(s)=G(\text{parent})-\frac{n_G}{n}\,G(\text{gauche})-\frac{n_D}{n}\,G(\text{droite}).$$

Il suffit d'essayer, comme seuils candidats, les **milieux** entre deux valeurs consécutives de la variable triée (au-dessus et au-dessous d'un tel seuil, les groupes sont les mêmes, quel que soit le seuil exact choisi dans l'intervalle). Faisons-le à la main pour le seuil $s=140$ (entre 120 et 160) :

- groupe de gauche : les clients 1 à 6, tous restés ($p=0$) : $G=0$ ;
- groupe de droite : les clients 7 à 10, dont trois partis ($p=\frac34$) : $G=1-\frac9{16}-\frac1{16}=0{,}375$ ;
- impureté après découpage : $\frac6{10}\times0+\frac4{10}\times0{,}375=0{,}15$ ; gain $=0{,}42-0{,}15=0{,}27$.


```text
 seuil gauche (n, partis) droite (n, partis)  impureté après   gain
  22.5               1, 0               9, 3          0.4000 0.0200
  37.5               2, 0               8, 3          0.3750 0.0450
  57.5               3, 0               7, 3          0.3429 0.0771
  82.5               4, 0               6, 3          0.3000 0.1200
 107.5               5, 0               5, 3          0.2400 0.1800
 140.0               6, 0               4, 3          0.1500 0.2700
 180.0               7, 1               3, 2          0.3048 0.1152
 230.0               8, 1               2, 2          0.1750 0.2450
 290.0               9, 2               1, 1          0.3111 0.1089
```

Le tableau reprend ce calcul pour tous les seuils de récence. Le meilleur est bien $s=$ 140, avec un gain de 0,27. Le meilleur seuil de satisfaction ne donne que 0,180 : la première question est donc « **récence ≤ 140 jours ?** ». À gauche, le groupe est pur : on s'arrête, la prédiction est « reste ». À droite, il reste quatre clients (7, 8, 9, 10) dont un est resté (le 8, très satisfait : 4,3) ; on recommence avec la satisfaction : le seuil $s=4{,}05$ sépare les clients 7, 9 et 10 (satisfaction $\le4{,}05$, tous partis) du client 8 (resté). Les deux feuilles sont pures : l'arbre est terminé.


![À gauche : les dix clients dans le plan (récence, satisfaction) et les deux coupes de l'arbre. À droite : l'arbre appris par scikit-learn, qui retrouve exactement les seuils du calcul à la main.](figures/ch02-arbre-main.png)

`scikit-learn` retrouve exactement ce calcul : première coupe à 140 jours, seconde à 4,05, 3 feuilles pures. L'arbre peut se lire comme deux règles : « **si la récence dépasse 140 jours *et* la satisfaction est inférieure à 4,05, alors le client part** ; sinon il reste ». Remarquez que cette règle est une **interaction** : ni la récence seule ni la satisfaction seule ne suffit à prédire. Un score linéaire n'aurait pas pu l'écrire.

> 📐 **L'algorithme, en toutes lettres (CART).** Pour construire un arbre à partir d'un jeu d'exemples : (1) pour **chaque variable** et **chaque seuil candidat**, calculer le gain d'impureté ; (2) retenir la coupe de **gain maximal** ; (3) recommencer **séparément** dans chacun des deux groupes ; (4) s'arrêter quand un critère d'arrêt est atteint (groupe pur, profondeur maximale, trop peu de clients). C'est un algorithme **glouton** : il choisit la meilleure coupe *maintenant*, sans se demander si une coupe moins bonne aujourd'hui permettrait de meilleures coupes demain. Il ne trouve donc pas forcément **le** meilleur arbre, mais il en trouve un bon très vite : en triant une fois chaque variable, évaluer tous les seuils d'une variable coûte de l'ordre de $n\log n$.
>
> La **prédiction** d'une feuille est la classe majoritaire (ou la proportion de clients partis, utilisée comme probabilité) des exemples d'entraînement qui y tombent. Les variables catégorielles se traitent par des questions « la modalité est-elle dans cet ensemble ? » ou, dans `scikit-learn`, après encodage en indicatrices ; les valeurs manquantes sont gérées nativement par les versions récentes.

### 2.2.4 Les arbres de régression

Pour prédire une **quantité** (la dépense des six prochains mois, par exemple), la prédiction d'une feuille est la **moyenne** des valeurs de ses exemples, et le critère de coupe est la **réduction de la somme des carrés des écarts** (les écarts à la moyenne du groupe). Un exemple minuscule : six clients, $x$ = nombre de commandes et $y$ = dépense (en €).

| $x$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| $y$ | 10 | 14 | 12 | 40 | 44 | 42 |

La moyenne générale vaut 27, et la somme des carrés des écarts $(10-27)^2+(14-27)^2+\dots=$ 1366. La coupe « $x\le3$ » donne deux feuilles : à gauche la moyenne est 12 (écarts : −2, +2, 0 : somme des carrés 8), à droite la moyenne est 42 (écarts −2, +2, 0 : somme des carrés 8). Après la coupe, la somme des carrés tombe de 1366 à 16 : le modèle prédit 12 pour les petits acheteurs et 42 pour les gros. C'est une fonction **en escalier**.


### 2.2.5 Jusqu'où laisser pousser l'arbre ?

Un arbre qu'on laisse pousser sans limite finit par isoler **chaque client** dans sa propre feuille : l'erreur d'entraînement tombe à zéro, mais l'arbre a appris le bruit. C'est l'exemple le plus pur de **surapprentissage** (volume III, section 1.3). On contrôle la complexité par des **hyperparamètres** : la profondeur maximale, le nombre minimal de clients par feuille, ou le nombre maximal de feuilles.

Voyons-le sur la résiliation : pour des profondeurs croissantes, on mesure l'AUC sur l'entraînement et, par validation croisée à cinq plis **à l'intérieur** de l'entraînement, sur des clients que l'arbre n'a pas vus.


![AUC d'un arbre de décision selon sa profondeur maximale : sur l'entraînement elle monte sans cesse, en validation croisée elle atteint un sommet puis redescend.](figures/ch02-arbre-profondeur.png)

La courbe d'entraînement (orange) monte sans cesse, jusqu'à 0,981 pour une profondeur de 14. La courbe de validation (bleue) monte jusqu'à une profondeur de **5** (AUC 0,863), puis **redescend** : au-delà, l'arbre mémorise. C'est la signature classique de l'arbitrage biais-variance. Un arbre trop court (profondeur 2) est trop simple (AUC 0,793 en validation) ; un arbre trop profond (14) a trop de liberté (0,749). Sur le jeu de test, l'arbre de profondeur 5 obtient une AUC de **0,885**, contre 0,866 pour la régression logistique.

```python
from sklearn.tree import DecisionTreeClassifier

arbre = DecisionTreeClassifier(max_depth=d_opt, min_samples_leaf=5, random_state=0)
arbre.fit(Xtr_o, ytr)
print(round(roc_auc_score(yte, arbre.predict_proba(Xte_o)[:, 1]), 4))
```
<!--sortie-->
```text
0.8847
```

(Ici, `Xtr_o` est le tableau d'entraînement dont les catégories ont été transformées en indicatrices, et `d_opt` la profondeur retenue par la validation croisée.)

**Une autre façon de limiter : élaguer.** Plutôt que d'interdire à l'arbre de grandir, on le laisse pousser puis on **coupe les branches** qui apportent trop peu. L'élagage par **coût-complexité** minimise
$$R_\alpha(T)=R(T)+\alpha\,|T|,$$
où $R(T)$ est l'erreur de l'arbre $T$ sur l'entraînement, $|T|$ son nombre de feuilles et $\alpha\ge0$ le prix d'une feuille supplémentaire. Pour $\alpha=0$, on garde tout ; quand $\alpha$ augmente, on supprime d'abord la branche dont la suppression coûte le moins par feuille retirée, et ainsi de suite jusqu'à la racine. On obtient une **suite d'arbres emboîtés**, et la validation croisée choisit $\alpha$.


![Élagage par coût-complexité : l'AUC en validation croisée (courbe bleue, axe de gauche) selon le prix α d'une feuille, et le nombre de feuilles de l'arbre (tirets gris, axe de droite). Le maximum (pointillé orange) correspond à un petit arbre d'une vingtaine de feuilles ; un arbre complet de 458 feuilles généralise moins bien.](figures/ch02-arbre-elagage.png)

Ici, l'élagage retient $\alpha\approx$ 0,0006 : un arbre de 20 feuilles (au lieu de 458 pour l'arbre complet), d'AUC de validation 0,861 et d'AUC de test 0,873. Les deux méthodes (limiter la profondeur, élaguer) conduisent à des arbres comparables : retenons que **la complexité d'un arbre est un réglage à choisir par validation**, jamais à laisser au maximum.

### 2.2.6 Ce que les arbres savent écrire : effets non linéaires et interactions

Sur les données de résiliation, la régression logistique atteint 0,866 et l'arbre de profondeur 5 0,885 : un arbre **seul** dépasse déjà un peu le modèle linéaire. D'où vient l'écart ? Il ne vient pas d'une grande découverte, mais de **plusieurs petites formes** que le score linéaire ne sait pas écrire. Voyons les deux plus parlantes.

**Un effet qui sature : le nombre de commandes.** Un score linéaire attribue à une variable un effet qui va **toujours dans le même sens et au même rythme** : chaque commande supplémentaire retranche la même quantité de log-cote, que l'on passe de 0 à 1 commande ou de 11 à 12. Or le risque de départ ne se comporte pas ainsi : il est très élevé pour les clients qui n'ont **rien commandé** en douze mois, il chute dès les premières commandes, puis **se stabilise** : au-delà d'une demi-douzaine de commandes, une de plus ne change plus rien.


![À gauche : le taux de départ observé selon le nombre de commandes (points gris), la prédiction d'une régression logistique (une courbe lisse qui ne sature pas) et celle d'un arbre (un escalier qui épouse le saut à 0 commande et le plateau). Au centre et à droite : probabilité de départ prédite en fonction de l'âge et du nombre de commandes, par une régression logistique (bandes obliques) et par un arbre (rectangles).](figures/ch02-regions-lineaire-arbre.png)

Le taux de départ observé est de 42 % pour les clients sans commande, de 15 % pour ceux qui en ont une ou deux, de 2 % à partir de six. Avec cette seule variable, la régression logistique atteint une AUC de test de 0,766 et l'arbre de profondeur 3 de 0,762 : la différence est faible, mais l'arbre dessine ce que montrent les données (un saut, puis un plateau), alors que la courbe logistique continue à descendre. Avec **deux** variables (le nombre de commandes et l'âge), les cartes de droite montrent la différence de **forme** : la régression logistique ne sait tracer que des bandes obliques, l'arbre découpe des rectangles, et isole notamment la bande horizontale des clients sans commande. L'AUC passe à 0,814 pour la première et à 0,831 pour le second.

**Une interaction : deux conditions à la fois.** La récence et la satisfaction illustrent l'autre limite. Regardons le taux de départ observé selon que la récence dépasse 150 jours et que la satisfaction est inférieure à 3,2 (en laissant de côté les clients dont la satisfaction manque), puis comparons-le à ce que prédit un modèle **additif** (logistique) sur ces deux variables.


```text
    récence satisfaction  clients  observé  additif
> 150 jours        < 3,2      562    0.717    0.507
> 150 jours        ≥ 3,2     1350    0.217    0.291
≤ 150 jours        < 3,2     1063    0.121    0.159
≤ 150 jours        ≥ 3,2     4888    0.064    0.060
```

Dans le coin « récence > 150 jours *et* satisfaction < 3,2 » (562 clients d'entraînement), le taux de départ observé est de **72 %**. Pour les clients qui ne remplissent aucune des deux conditions, il est de 6 % ; chaque condition **seule** le fait monter à 12 % (satisfaction basse) ou 22 % (récence élevée) ; les deux **ensemble** le multiplient par 11. Or un modèle additif ne peut qu'**ajouter** les deux effets (sur l'échelle de la log-cote) : il prédit 51 % pour le coin, soit vingt points de moins que la réalité, et surestime les deux cases voisines (29 % et 16 % prédits, contre 22 % et 12 % observés). Un arbre écrit cela avec deux questions.

> 💡 **La vérité programmée.** Ces données sont simulées : nous pouvons donc révéler ce qui les produit. Le risque de départ contient bien une forte hausse quand la récence dépasse **150 jours** *et* la satisfaction est inférieure à **3,2** (un terme d'interaction), un effet du nombre de commandes qui **sature** à six, un surcroît de risque pour les clients anciens sans aucune commande, et d'autres interactions (trois tickets au support et beaucoup de retours ; beaucoup de promotions sans programme de fidélité). Le modèle linéaire en capte la part régulière ; les arbres captent aussi ces formes irrégulières, et la somme de ces petits gains explique l'écart global entre 0,866 et 0,885.

### 2.2.7 Le point faible : l'instabilité

Si les arbres sont aussi pratiques, pourquoi ne s'arrête-t-on pas là ? Parce qu'un arbre est **instable** : une petite modification des données peut changer complètement la première question, donc tout ce qui suit. L'algorithme étant glouton, une coupe presque aussi bonne que la meilleure, mais portant sur une autre variable, change toute la suite de l'arbre.

Mesurons-le sur un jeu modeste : on tire 30 sous-échantillons de **2 000 clients** dans le jeu d'entraînement, on ajuste sur chacun un arbre de profondeur 4 et l'on regarde **quelle variable ouvre l'arbre**. (Avec les 9 000 clients complets, la première variable serait presque toujours la même ; c'est le **seuil** et la **suite** qui bougent, comme on le voit plus bas.)


Sur 30 sous-échantillons de 2 000 clients, 4 variables différentes ouvrent l'arbre : `recence_jours` dans 19 cas, `age` dans 5 cas, et les autres variables dans les cas restants. Et même quand la variable est la même, le seuil change : avec les 9 000 clients, 1 seule variable ouvre les 30 arbres bootstrap, mais le seuil de la première coupe va de 156 à 312 jours. Les prédictions de deux arbres de ce type ne sont corrélées qu'à 0,78 en moyenne sur le jeu de test : **chaque arbre raconte une histoire différente**. En termes du chapitre 1, un arbre profond a un **biais** faible et une **variance** élevée. Or il existe un remède universel contre la variance : **moyenner**. C'est le sujet de la section suivante.

> ✅ **À retenir.**
> - Un arbre pose une suite de questions « variable ≤ seuil ? » ; il est construit **gloutonnement**, en maximisant à chaque étape la **diminution d'impureté** (Gini ou entropie en classification, somme des carrés en régression).
> - Il capture **seuils et interactions** et n'exige ni standardisation ni modèle de la loi des données ; ses règles sont lisibles.
> - Sa complexité (profondeur, taille minimale des feuilles, élagage par coût-complexité $R(T)+\alpha|T|$) est un **hyperparamètre à régler par validation croisée**.
> - Il est **instable** : forte variance, d'où les forêts (2.3) et le boosting (2.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3 (construire un arbre à la main puis avec `scikit-learn`, élaguer), exercices 2.4 à 2.6.


## 2.3 Forêts aléatoires

> 💡 **Intuition.** Demandez à un seul expert d'estimer le poids d'un bœuf : il se trompera, dans un sens ou dans l'autre. Demandez à cent experts **indépendants** et faites la moyenne : les erreurs de signes opposés se compensent, et l'on tombe très près de la vérité. Une forêt aléatoire est cette foule : des centaines d'arbres, chacun entraîné sur une version un peu différente des données, dont on moyenne les prédictions. Chaque arbre est instable (section 2.2.7) ; **la moyenne ne l'est presque plus**.

### 2.3.1 Le bagging : moyenner des arbres entraînés sur des échantillons bootstrap

L'idée porte le nom de **bagging** (*bootstrap aggregating*, Breiman, 1996). Pour construire $B$ arbres, on répète $B$ fois : (1) tirer un **échantillon bootstrap** : $n$ clients tirés **avec remise** dans le jeu d'entraînement (certains clients apparaissent plusieurs fois, d'autres jamais) ; (2) ajuster un arbre profond sur cet échantillon. Pour prédire, on moyenne les $B$ probabilités prédites (ou on prend le vote majoritaire).

Combien de clients distincts un échantillon bootstrap contient-il ? Un client donné n'est **pas** tiré à un tirage donné avec la probabilité $1-\frac1n$, donc il n'est tiré **jamais** sur les $n$ tirages avec la probabilité $\bigl(1-\frac1n\bigr)^n\to e^{-1}\approx0{,}368$. Un échantillon bootstrap contient donc, en moyenne, **63,2 %** des clients distincts, et environ **36,8 %** des clients sont laissés de côté. Ces clients « hors sac » nous serviront en 2.3.4.


Vérification sur notre jeu d'entraînement : un échantillon bootstrap contient 63,4 % de clients distincts, pour une valeur théorique de 63,2 %.

### 2.3.2 Pourquoi moyenner réduit la variance : la formule

Soient $B$ prédictions $T_1,\dots,T_B$ (celles de $B$ arbres, en un point $x$ fixé), de même variance $\sigma^2$ et de **corrélation** deux à deux $\rho$. Leur moyenne a pour variance

$$\operatorname{Var}\Bigl(\frac1B\sum_{b=1}^BT_b\Bigr)=\frac1{B^2}\Bigl[\underbrace{B\sigma^2}_{\text{variances}}+\underbrace{B(B-1)\rho\sigma^2}_{\text{covariances}}\Bigr]=\rho\,\sigma^2+\frac{1-\rho}{B}\,\sigma^2.$$

> 📐 **Lecture de la formule.** Le second terme, $\frac{1-\rho}B\sigma^2$, **disparaît quand $B$ augmente** : c'est la part de variance que la moyenne élimine. Le premier, $\rho\sigma^2$, **reste** : si les arbres sont corrélés, moyenner à l'infini n'enlève pas leur erreur commune. Deux cas extrêmes : si les arbres étaient **indépendants** ($\rho=0$), la variance serait divisée par $B$ ; s'ils étaient **identiques** ($\rho=1$), la moyenne ne servirait à rien, la variance resterait $\sigma^2$. Un autre point mérite d'être noté : la moyenne ne change pas le **biais** (c'est la moyenne des biais), c'est pourquoi on moyenne des arbres **profonds**, au biais faible et à la variance forte.

Un exemple chiffré avec $\sigma^2=1$ et $\rho=0{,}3$ : pour $B=1$ la variance vaut 1 ; pour $B=10$, $0{,}3+0{,}07=0{,}37$ ; pour $B=100$, $0{,}3+0{,}007=0{,}307$ ; pour $B\to\infty$, $0{,}3$. On a éliminé presque toute la variance « évitable » avec une centaine d'arbres, mais jamais les 30 % dus à la corrélation.

Voyons ce que cela donne avec de vrais arbres. On tire 12 sous-échantillons de 4 500 clients dans le jeu d'entraînement (12 « jeux de données » différents) ; sur chacun on ajuste 30 arbres bootstrap. Pour 800 clients du jeu de test, on mesure la variance de la prédiction d'un seul arbre, puis de la moyenne de 5, 15, 30 arbres, **d'un jeu de données à l'autre**.


```text
 arbres moyennés  variance mesurée  formule ρσ² + (1−ρ)σ²/B
               1           0.03060                  0.03271
               5           0.00709                  0.00774
              15           0.00340                  0.00358
              30           0.00253                  0.00254
```

La variance d'un seul arbre est 0,0327 ; la corrélation estimée entre deux arbres du même jeu de données est 0,05, ce qui fixe un plancher $\rho\sigma^2\approx$ 0,0015. La corrélation est modeste en valeur absolue parce qu'une grande part de la variance d'un arbre profond vient de l'aléa du bootstrap lui-même, que la moyenne élimine ; mais c'est la part restante qui compte quand $B$ est grand. En moyennant 30 arbres, la variance mesurée tombe à 0,0025, soit une division par environ 12,9 ; la colonne de droite montre que la formule, alimentée par ces deux estimations, retrouve les variances mesurées (à l'échantillonnage près : seulement 12 jeux de données).


### 2.3.3 La forêt aléatoire : décorréler les arbres

Le bagging a un défaut : si une variable est très prédictive (la récence, ici), **tous** les arbres l'utilisent en première coupe, donc se ressemblent : $\rho$ reste élevé. Les **forêts aléatoires** (*random forests*, Breiman, 2001) ajoutent une idée simple : à **chaque coupe**, l'arbre ne considère qu'un **sous-ensemble tiré au hasard** de $m$ variables parmi $p$ (par défaut $m=\sqrt p$ en classification). Une variable dominante n'est plus disponible à toutes les coupes ; les arbres sont forcés d'explorer d'autres pistes, donc de se **décorréler**. Chaque arbre individuel est un peu moins bon (il a moins de choix), mais la moyenne l'est davantage, parce que $\rho$ a baissé.


Sur la même expérience, mais avec $m=\sqrt p$ variables tirées à chaque coupe, la corrélation entre deux arbres passe de 0,046 à 0,039 (plancher : de 0,0015 à 0,0011), et la variance de la moyenne de 30 arbres tombe de 0,0025 à 0,0011, soit une division par plus de deux, alors que chaque arbre pris seul a une variance comparable (0,0273 contre 0,0327). Décorréler fait gagner plus que ce que fait perdre l'appauvrissement de chaque arbre.

### 2.3.4 L'erreur « hors sac » : une validation gratuite

Chaque arbre n'a vu que 63,2 % des clients. Pour chaque client $i$, on peut donc faire voter **uniquement les arbres qui ne l'ont jamais vu**, soit environ 37 % de la forêt : on obtient une prédiction **honnête** pour ce client, comme en validation croisée, mais sans entraîner un seul modèle supplémentaire. C'est l'estimation **hors sac** (*out-of-bag*, OOB). On s'en sert pour régler les hyperparamètres d'une forêt à coût nul.


```python
from sklearn.ensemble import RandomForestClassifier

foret = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, max_features="sqrt",
                               oob_score=True, n_jobs=1, random_state=0)
foret.fit(Xtr_o, ytr)
print(round(roc_auc_score(yte, foret.predict_proba(Xte_o)[:, 1]), 4))
```
<!--sortie-->
```text
0.8964
```

Une forêt de 300 arbres obtient une AUC de **0,896** sur le jeu de test, contre 0,885 pour l'arbre unique de profondeur 5 et 0,866 pour la régression logistique. L'estimation hors sac, calculée **sans utiliser le jeu de test**, donne 0,888 : elle est proche de la valeur de test, avec un léger pessimisme (chaque client n'est évalué que par environ 37 % des arbres, donc par une sous-forêt plus petite).

### 2.3.5 Combien d'arbres ? Quels réglages ?

Une particularité des forêts : **ajouter des arbres ne fait pas surapprendre**. La performance monte puis se stabilise, parce que l'erreur de la moyenne converge vers une limite quand $B\to\infty$ (c'est la loi des grands nombres appliquée aux arbres ; le terme $\rho\sigma^2$ de la formule est un plancher, pas un risque). Il suffit donc de prendre « assez » d'arbres : plus, c'est seulement plus lent.


![AUC d'une forêt sur le jeu de test selon le nombre d'arbres : elle monte vite puis forme un plateau.](figures/ch02-foret-nb-arbres.png)

Avec un seul arbre de la forêt, l'AUC est de 0,752 ; avec 25 arbres, de 0,891 ; avec 300, de 0,896. Au-delà de quelques dizaines d'arbres, le gain devient marginal.

Les réglages qui comptent vraiment sont ailleurs : la **profondeur** ou la **taille minimale des feuilles** (le compromis biais-variance de chaque arbre), et surtout `max_features`, la fraction de variables examinées à chaque coupe. En voici l'effet, mesuré par l'erreur hors sac (donc sans toucher au jeu de test) :

```text
 max_features (fraction)  AUC hors sac  AUC test
                    0.05        0.8701    0.8814
                    0.10        0.8821    0.8925
                    0.20        0.8848    0.8967
                    0.40        0.8852    0.8948
                    0.70        0.8854    0.8945
                    1.00        0.8826    0.8942
```

L'AUC hors sac est maximale pour une fraction de 0,70 des variables (0,885), contre 0,883 quand on les examine toutes (c'est du bagging pur) et 0,870 quand on n'en examine presque aucune. Trop peu de variables : chaque arbre est trop pauvre ; trop : les arbres se ressemblent. Le sommet est entre les deux, et il est peu marqué : les forêts sont, parmi tous les modèles, **les plus tolérantes aux mauvais réglages**.

### 2.3.6 Quelles variables comptent ? Importance et ses pièges

Une forêt ne se lit pas comme un arbre, mais on peut lui demander **quelles variables elle utilise le plus**. Deux mesures s'opposent.

- L'**importance par impureté** (*mean decrease in impurity*, MDI) additionne, pour chaque variable, les diminutions d'impureté de toutes les coupes où elle intervient. Elle est gratuite (calculée pendant l'entraînement), mais elle est **biaisée** : elle favorise les variables à **beaucoup de valeurs distinctes** (une variable continue offre beaucoup plus de seuils possibles, donc beaucoup plus d'occasions de trouver une coupe qui améliore *par hasard* l'impureté de l'entraînement) et elle est calculée **sur l'entraînement**, donc elle récompense aussi ce que la forêt a mémorisé.
- L'**importance par permutation** mélange au hasard les valeurs d'**une** variable sur des données **non vues** (le jeu de test) et mesure la **baisse de performance** : si le modèle s'effondre, la variable compte ; si rien ne change, elle ne compte pas.

Pour voir le biais, on ajoute au jeu deux variables **de pur bruit** : l'une continue (tirée dans une loi normale), l'autre un « identifiant » à 2 000 valeurs entières. Elles ne contiennent aucune information sur le départ.


![Les huit variables les plus importantes selon l'impureté et les deux variables de pur bruit (en orange) ajoutées au tableau, avec deux mesures d'importance. L'importance par impureté (à gauche) accorde de l'importance au bruit ; l'importance par permutation sur le jeu de test (à droite) la ramène à zéro.](figures/ch02-foret-importances.png)

Parmi les 47 colonnes, l'importance par impureté classe la variable de bruit continue au rang **11** et l'identifiant aléatoire au rang **12**, c'est-à-dire parmi les premières colonnes, devant des variables qui portent une vraie information : l'identifiant, sans aucune information, reçoit une importance de 0,0358. L'importance par permutation, elle, donne −0,0005 et 0,0001 aux deux variables de bruit : **zéro, ou à peu près**, ce qui est la bonne réponse.

> ⚠️ **Deux précautions.** (1) Ne vous fiez jamais à l'importance par impureté pour comparer des variables de types différents (continues contre catégories à peu de modalités) : préférez l'importance par permutation, calculée sur des données de test. (2) Quand deux variables sont **fortement corrélées**, la forêt répartit l'importance entre elles (et la permutation en sous-estime chacune, car l'autre « compense ») : l'importance dit *ce que le modèle utilise*, pas *ce qui cause le phénomène*. La section 5.3 reprendra l'interprétation de façon plus complète (valeurs de Shapley, PDP).

> ✅ **À retenir.**
> - Le **bagging** moyenne des arbres profonds entraînés sur des échantillons bootstrap ; la variance de la moyenne vaut $\rho\sigma^2+\frac{1-\rho}B\sigma^2$ : elle baisse avec $B$ mais plafonne à $\rho\sigma^2$.
> - La **forêt aléatoire** diminue $\rho$ en ne laissant, à chaque coupe, qu'un sous-ensemble de variables : les arbres se ressemblent moins, la moyenne est meilleure.
> - L'**erreur hors sac** (63,2 % / 36,8 % des clients) est une validation gratuite. **Ajouter des arbres ne fait pas surapprendre.**
> - Les réglages qui comptent : profondeur ou taille des feuilles, `max_features`. Une forêt est robuste et exige peu de réglages.
> - L'importance par **impureté** est biaisée (variables à nombreuses valeurs) ; préférez celle **par permutation**, mesurée sur des données non vues.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 (bagging écrit à la main) et 2.5 (importances et variables de bruit), exercices 2.7 à 2.8.


## 2.4 Gradient boosting : XGBoost et LightGBM

> 💡 **Intuition.** Une forêt réunit des arbres **indépendants** et les moyenne. Le **boosting** fait l'inverse : il construit les arbres **un par un**, chacun étant chargé de **corriger les erreurs** de l'ensemble construit jusque-là. On commence par une prédiction grossière (la moyenne), on regarde où l'on se trompe, on entraîne un petit arbre à prédire *ces erreurs*, on l'ajoute (en le pondérant prudemment), et l'on recommence. Les forêts réduisent la **variance** ; le boosting réduit surtout le **biais**. Sur les données tabulaires, c'est aujourd'hui la famille de modèles la plus efficace.

### 2.4.1 Un exemple à la main : deux tours de boosting

Six clients, une variable $x$ (le nombre de commandes) et une dépense $y$ (en €).

| $x$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| $y$ | 3 | 5 | 4 | 12 | 20 | 13 |

**Tour 0.** Le modèle le plus simple prédit la **moyenne** : $F_0(x)=\frac{3+5+4+12+20+13}6=9{,}5$. Les **résidus** (réalité moins prédiction) sont $r^{(1)}=y-F_0=(-6{,}5;\ -4{,}5;\ -5{,}5;\ 2{,}5;\ 10{,}5;\ 3{,}5)$.

**Tour 1.** On ajuste un tout petit arbre (une seule coupe, une « souche ») pour **prédire les résidus**. La meilleure coupe est « $x\le3$ » : la moyenne des résidus à gauche vaut $-5{,}5$, à droite $+5{,}5$. Au lieu d'ajouter toute la correction, on n'ajoute que la moitié (le **pas d'apprentissage** vaut $\nu=0{,}5$) : $F_1=F_0+0{,}5\times\text{souche}_1$. À gauche, $F_1=9{,}5-2{,}75=6{,}75$ ; à droite, $F_1=9{,}5+2{,}75=12{,}25$.

**Tour 2.** On recalcule les résidus $r^{(2)}=y-F_1$ et l'on ajuste une nouvelle souche. Cette fois, la meilleure coupe est « $x\le4$ » : elle isole les grosses dépenses des clients 5 et 6. Après ces deux tours, la prédiction vaut 5,6875 pour les clients 1 à 3, 11,1875 pour le client 4 et 14,375 pour les clients 5 et 6. Et ainsi de suite.


```text
 x    y  F0  résidu 1    F1  résidu 2     F2
 1  3.0 9.5      -6.5  6.75     -3.75  5.688
 2  5.0 9.5      -4.5  6.75     -1.75  5.688
 3  4.0 9.5      -5.5  6.75     -2.75  5.688
 4 12.0 9.5       2.5 12.25     -0.25 11.188
 5 20.0 9.5      10.5 12.25      7.75 14.375
 6 13.0 9.5       3.5 12.25      0.75 14.375
```

![Les six clients (points orange) et la prédiction du modèle de boosting (courbe bleue) après 0, 1, 2 et 100 tours. À chaque tour, la fonction en escalier se rapproche des données.](figures/ch02-boosting-main.png)

Le tableau et la figure montrent le mécanisme : la somme des carrés des erreurs passe de 221,5 (tour 0) à 85,4 (tour 1), puis à 44,7 (tour 2). Chaque tour réduit ce qui reste d'erreur, et le « pas » $\nu$ empêche de corriger d'un coup, ce qui évite de s'ajuster au bruit. Après 100 tours, le modèle reproduit les données de façon quasi exacte : le boosting a un biais qui tend vers zéro, et c'est précisément pourquoi il faut **l'arrêter à temps**.

### 2.4.2 Le gradient boosting : une descente de gradient dans l'espace des fonctions

L'exemple semble un truc de bricoleur : « ajuster les résidus ». Friedman (2001) a montré qu'il s'agit en réalité d'une **descente de gradient**, non sur des paramètres, mais **sur la fonction elle-même**. Cela permet de traiter n'importe quelle perte, pas seulement le carré.

> 📐 **La dérivation.** On cherche une fonction $F$ qui minimise la perte totale $L(F)=\sum_{i=1}^n\ell\bigl(y_i,F(x_i)\bigr)$. Considérons les valeurs $F(x_1),\dots,F(x_n)$ comme $n$ paramètres. Une descente de gradient consisterait à les déplacer dans la direction opposée au gradient :
> $$F(x_i)\leftarrow F(x_i)-\nu\,\frac{\partial\ell\bigl(y_i,F(x_i)\bigr)}{\partial F(x_i)}.$$
> Le problème : on ne veut pas modifier seulement les $n$ valeurs observées, mais obtenir une fonction qui **généralise**. On ajuste donc un petit arbre $h$ pour **approcher** les $n$ valeurs $r_i=-\partial\ell/\partial F(x_i)$ (les « pseudo-résidus »), puis on ajoute $\nu\,h$ à $F$. L'algorithme est donc :
> 1. $F_0=\arg\min_c\sum_i\ell(y_i,c)$ (une constante) ;
> 2. pour $m=1,\dots,M$ : calculer les pseudo-résidus $r_i^{(m)}=-\Bigl[\dfrac{\partial\ell(y_i,F)}{\partial F}\Bigr]_{F=F_{m-1}(x_i)}$ ; ajuster un arbre $h_m$ aux $r_i^{(m)}$ ; poser $F_m=F_{m-1}+\nu\,h_m$.
>
> **Perte quadratique** $\ell=\frac12(y-F)^2$ : $r_i=y_i-F(x_i)$ : le pseudo-résidu est le **résidu ordinaire**. C'est le cas de l'exemple. **Perte logistique** (classification), avec $F$ la **log-cote** et $p=\sigma(F)$ : on a montré (section 2.1.2) que $\partial\ell/\partial F=p-y$, donc $r_i=y_i-p_i$ : chaque arbre apprend l'écart entre la réalité et la probabilité actuellement prédite. Changer la perte (valeur absolue, perte de quantile, perte de Poisson…) ne change **rien** à l'algorithme.

Quelques réglages découlent de cette vision. Le pas $\nu$ (*learning rate*) joue le rôle du pas de la descente de gradient : petit, il est prudent mais exige beaucoup d'arbres. La **profondeur** des arbres $h_m$ fixe l'**ordre des interactions** que le modèle peut représenter : avec des souches (profondeur 1), le modèle final est une somme de fonctions d'**une seule variable** ; avec une profondeur 3, il peut combiner jusqu'à trois variables dans un même terme. Enfin, comme pour les forêts, on peut n'utiliser qu'une **fraction aléatoire** des clients (*subsample*) et des variables (*colsample*) à chaque tour : le **boosting stochastique** réduit la variance et accélère le calcul.

### 2.4.3 XGBoost : un objectif régularisé et une formule fermée

**XGBoost** (Chen et Guestrin, 2016) reprend ce schéma en lui apportant trois améliorations de fond. D'abord un objectif **régularisé** : la perte plus une pénalité sur la complexité de l'arbre, $\Omega(h)=\gamma\,T+\frac12\lambda\sum_jw_j^2$ ($T$ feuilles, $w_j$ valeur de la feuille $j$). Ensuite un développement **au second ordre** de la perte : avec $g_i=\partial\ell/\partial F$ et $h_i=\partial^2\ell/\partial F^2$ calculés au tour précédent, le coût d'un arbre se réécrit

$$\widetilde{\mathcal L}=\sum_{j=1}^T\Bigl[G_jw_j+\tfrac12\,(H_j+\lambda)\,w_j^2\Bigr]+\gamma\,T,\qquad G_j=\sum_{i\in\text{feuille }j}g_i,\quad H_j=\sum_{i\in\text{feuille }j}h_i.$$

> 📐 **Les formules à retenir.** C'est un trinôme en $w_j$, minimal en
> $$w_j^*=-\frac{G_j}{H_j+\lambda},\qquad\text{de valeur}\qquad-\frac12\,\frac{G_j^2}{H_j+\lambda}.$$
> La **qualité d'une coupe** (qui sépare un nœud en gauche et droite) est donc la diminution de coût obtenue :
> $$\text{gain}=\frac12\Bigl[\frac{G_G^2}{H_G+\lambda}+\frac{G_D^2}{H_D+\lambda}-\frac{(G_G+G_D)^2}{H_G+H_D+\lambda}\Bigr]-\gamma.$$
> Une coupe n'est faite que si son gain est **positif** : $\gamma$ est un seuil d'élagage intégré. Pour la perte logistique, $g_i=p_i-y_i$ et $h_i=p_i(1-p_i)$.

Un exemple chiffré. Au tour 1 d'un modèle logistique, on part de $F_0=0$, donc $p_i=0{,}5$ pour tous. Quatre clients tombent dans un nœud, avec $y=(1,0,1,1)$ : $g_i=(-0{,}5;\ +0{,}5;\ -0{,}5;\ -0{,}5)$ et $h_i=0{,}25$ partout. Si le nœud reste une feuille : $G=-1$, $H=1$ et, avec $\lambda=1$, $w^*=\frac{1}{1+1}=0{,}5$ (on relève la log-cote de 0,5 ; sans régularisation, ce serait $1$). Si une coupe sépare les clients $\{1,2\}$ de $\{3,4\}$ : $G_G=0$, $H_G=0{,}5$ ; $G_D=-1$, $H_D=0{,}5$, donc

$$\text{gain}=\tfrac12\Bigl[\tfrac{0}{1{,}5}+\tfrac{1}{1{,}5}-\tfrac{1}{2}\Bigr]=\tfrac12\bigl(0{,}667-0{,}5\bigr)\approx0{,}083\ \ (\gamma=0).$$


Le calcul est confirmé : la valeur de feuille est 0,50 (1,00 sans régularisation) et le gain de la coupe 0,083. Le régulariseur $\lambda$ **rétrécit** les valeurs de feuilles, surtout pour celles qui reposent sur peu de clients (petit $H_j$) : c'est une protection contre le surapprentissage, intégrée à l'algorithme.

Troisième apport : XGBoost est **rapide**. Il regroupe les valeurs des variables en **histogrammes** (au plus 256 intervalles) : au lieu d'essayer chaque seuil, on n'en essaie que 255, ce qui rend le calcul presque indépendant de $n$.

### 2.4.4 LightGBM et le choix d'une stratégie de croissance

**LightGBM** (Ke et coll., 2017) va plus loin dans la vitesse. Il utilise lui aussi des histogrammes, et ajoute deux idées : la **croissance par feuille** (*leaf-wise*) et l'économie de calcul sur les données. XGBoost (par défaut) fait grandir l'arbre **niveau par niveau** : toutes les feuilles du niveau courant sont coupées, puis celles du niveau suivant. LightGBM coupe à chaque étape **la feuille dont le gain est le plus grand**, où qu'elle soit : l'arbre devient asymétrique, avec parfois une longue branche profonde, et réduit plus vite l'erreur pour un même nombre de feuilles. Le réglage principal n'est donc plus la profondeur mais le **nombre de feuilles** (`num_leaves`), avec un garde-fou sur la taille minimale des feuilles (`min_child_samples`). La version de `scikit-learn`, `HistGradientBoostingClassifier`, reprend cette philosophie et n'exige aucune installation supplémentaire.

Trois précautions communes : (1) le boosting **surapprend si on le laisse tourner**, d'où l'**arrêt précoce** (section suivante) ; (2) il est **sensible au bruit des étiquettes** (il insiste sur les clients mal prédits, même quand c'est du hasard) ; (3) il **n'extrapole pas** : comme tout modèle à base d'arbres, il prédit une valeur constante en dehors du domaine des données d'entraînement.

### 2.4.5 Régler le boosting : pas, nombre d'arbres et arrêt précoce

Le pas $\nu$ et le nombre d'arbres $M$ sont liés : diviser $\nu$ par deux oblige à doubler $M$ pour atteindre un niveau de performance comparable. Plutôt que de choisir $M$ à la main, on prend un $\nu$ petit et l'on **arrête quand la perte de validation cesse de baisser** : c'est l'**arrêt précoce** (*early stopping*). On réserve pour cela une partie de l'entraînement (ici 20 %) comme **jeu de validation**, distinct du jeu de test.


![Perte logistique sur le jeu de validation selon le nombre d'arbres, pour trois pas d'apprentissage. Chaque courbe passe par un minimum puis remonte : le modèle se met à surapprendre. Plus le pas est petit, plus le minimum est atteint tard.](figures/ch02-boosting-pas-arbres.png)

Les trois courbes ont la même forme : la perte de validation baisse, passe par un **minimum**, puis **remonte** (le modèle commence à s'ajuster au bruit de l'entraînement). Avec un pas de 0,3, le minimum est atteint après 16 arbres (perte 0,2612) ; avec 0,1, après 57 (0,2490) ; avec 0,03, après 246 (0,2500). Les pas de 0,1 et de 0,03 atteignent des minima équivalents, nettement meilleurs que celui du pas de 0,3 qui, trop gros, dépasse le fond : un petit pas atteint un minimum au moins aussi bon, au prix de plus d'arbres. La règle d'usage est de prendre un pas de 0,02 à 0,1 et de laisser l'arrêt précoce décider du nombre d'arbres.

Voici l'usage de XGBoost et de LightGBM, avec arrêt précoce (les catégories sont passées sous forme de type `category` de `pandas`) :

```python
import xgboost as xgb

xg = xgb.XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8,
                       enable_categorical=True, early_stopping_rounds=30, eval_metric="logloss", n_jobs=1, random_state=0)
xg.fit(Xa, ya, eval_set=[(Xv, yv)], verbose=False)
print(xg.best_iteration, round(roc_auc_score(yte, xg.predict_proba(Xte_c)[:, 1]), 4))
```
<!--sortie-->
```text
227 0.8982
```

```python
import lightgbm as lgb

lg = lgb.LGBMClassifier(n_estimators=1000, learning_rate=0.05, num_leaves=15, subsample=0.8, subsample_freq=1,
                        colsample_bytree=0.8, n_jobs=1, random_state=0, verbose=-1)
lg.fit(Xa, ya, eval_set=[(Xv, yv)], callbacks=[lgb.early_stopping(30, verbose=False)])
print(lg.best_iteration_, round(roc_auc_score(yte, lg.predict_proba(Xte_c)[:, 1]), 4))
```
<!--sortie-->
```text
198 0.9026
```

(Ici, `Xa`/`ya` désignent 80 % de l'entraînement et `Xv`/`yv` les 20 % réservés à la validation ; `Xte_c` est le jeu de test, catégories en type `category`.)


Les deux bibliothèques s'arrêtent après 227 (XGBoost) et 198 (LightGBM) arbres et obtiennent respectivement des AUC de test de 0,898 et 0,903 : des valeurs voisines (la différence de 0,004 vient des détails d'implémentation : croissance par niveau ou par feuille, histogrammes, traitement des catégories), car l'algorithme de fond est le même. Les autres réglages usuels, avec leurs ordres de grandeur : profondeur 3 à 8 (XGBoost) ou 15 à 63 feuilles (LightGBM) ; taille minimale des feuilles ; `subsample` et `colsample_bytree` de 0,5 à 1 ; régularisation $\lambda$ de 0 à 10. Le chapitre 1 (section 1.5, ➕) présente les méthodes pour les chercher de façon systématique.

### 2.4.6 Valeurs manquantes et catégories : sans artifice

Les modèles à base d'arbres modernes traitent **nativement** deux difficultés qui occupent un modèle linéaire : les valeurs manquantes et les catégories à nombreuses modalités.

- **Valeurs manquantes.** À chaque coupe, XGBoost, LightGBM et `HistGradientBoostingClassifier` **apprennent** vers quel côté envoyer les clients dont la valeur manque, en choisissant la direction qui réduit le plus la perte. Pas d'imputation : et le **fait d'être manquant**, souvent informatif (ici la satisfaction manque plus souvent quand elle est basse), est exploité directement.
- **Catégories.** Une variable comme `ville` (20 modalités) donnerait 20 colonnes en encodage par indicatrices. LightGBM et `HistGradientBoostingClassifier` cherchent directement, pour une variable catégorielle, **le meilleur partage des modalités en deux ensembles**.


```text
                                            traitement  AUC test
                natif (NaN gardés, catégories natives)    0.9025
                NaN gardés, catégories en indicatrices    0.9018
               NaN gardés, catégories en codes entiers    0.9013
médiane à la place des NaN, catégories en indicatrices    0.9019
```

Sur la résiliation, le traitement natif (valeurs manquantes conservées, catégories natives) donne une AUC de 0,903 ; les mêmes catégories passées en indicatrices 0,902 ; en codes entiers arbitraires (un « 3 » pour la ville D, ce qui n'a aucun sens) 0,901 ; et, si l'on **impute** d'abord les valeurs manquantes par la médiane (et que l'on perd donc l'information « manquant »), 0,902. Les écarts sont minuscules (au plus 0,001 d'AUC), de l'ordre du bruit d'échantillonnage : sur ces données, les variables importantes sont numériques et presque toutes renseignées, et la seule catégorie à nombreuses modalités (la ville) a un effet modeste. Ne tirez donc pas de ces chiffres qu'un traitement « bat » un autre ; retenez que le traitement natif **ne coûte rien** et simplifie le code. Sur des données plus riches en catégories ou en valeurs manquantes informatives, l'écart se creuse.

### 2.4.7 Le match : régression logistique, arbre, forêt, boosting

Comparons maintenant les quatre familles sur **le même découpage** et **la même mesure**. Nous mesurons l'AUC de deux façons : par **validation croisée à cinq plis** à l'intérieur de l'entraînement (qui donne aussi une dispersion), et sur le **jeu de test**, que nous n'ouvrons qu'une fois.


```text
                    modèle  AUC validation croisée (moyenne)  écart-type entre plis  AUC test  perte logistique test
     régression logistique                            0.8605                 0.0098    0.8659                 0.2816
arbre (profondeur choisie)                            0.8630                 0.0066    0.8847                 0.2584
           forêt aléatoire                            0.8856                 0.0085    0.8963                 0.2608
         gradient boosting                            0.8900                 0.0077    0.9025                 0.2437
```

![AUC de quatre familles de modèles sur la résiliation : moyenne et écart-type sur cinq plis de validation croisée (cercles bleus) et valeur sur le jeu de test (losanges orange).](figures/ch02-comparaison-modeles.png)

Lecture, en trois temps.

1. **La hiérarchie.** Sur le jeu de test, la régression logistique obtient 0,866, l'arbre 0,885, la forêt 0,896 et le boosting 0,903. En validation croisée, l'ordre est le même pour la forêt et le boosting (0,886 et 0,890, contre 0,860 pour la régression logistique, avec des écarts-types entre plis de l'ordre de 0,008) : leur avance dépasse nettement cette dispersion. L'arbre, lui, est **indiscernable** de la régression logistique en validation croisée (0,863, écart-type 0,007) alors qu'il la dépasse sur le jeu de test : ne tirez pas de conclusion d'un seul chiffre. Remarquez aussi que, pour tous les modèles, l'AUC de test est un peu supérieure à celle de validation croisée : en validation croisée, chaque modèle n'apprend que sur 80 % de l'entraînement (7 200 clients) ; le modèle final voit les 9 000, et les modèles flexibles profitent davantage de données supplémentaires (courbes d'apprentissage, section 1.3).
2. **La comparaison appariée.** Pour savoir si l'avantage du boosting sur la régression logistique est **réel**, on ne compare pas deux intervalles de confiance isolés : on compare les deux modèles **sur les mêmes clients**. Pli par pli, le boosting gagne en moyenne 0,030 d'AUC (de 0,020 à 0,035 selon le pli). Sur le jeu de test, un **bootstrap apparié** (on rééchantillonne 400 fois les mêmes 3 000 clients et l'on recalcule la différence) donne un écart d'AUC de 0,037 avec un intervalle à 95 % de [0,025 ; 0,049]. Entre boosting et forêt, l'écart moyen est de 0,006 avec un intervalle [−0,001 ; 0,014]. Entre forêt et régression logistique, 0,030 [0,021 ; 0,042]. Un intervalle qui contient zéro signale une différence qu'on ne peut pas distinguer du hasard d'échantillonnage.
3. **La perte logistique** (dernière colonne) juge les **probabilités** et non plus seulement le classement. Elle va ici dans le même sens que l'AUC : 0,244 pour le boosting, 0,258 pour l'arbre, 0,261 pour la forêt et 0,282 pour la régression logistique (plus c'est bas, mieux c'est). Un modèle peut cependant très bien **ordonner** les clients et mal **estimer** leur probabilité ; la perte seule ne dit pas si les probabilités annoncées sont fiables. Vérifier cela, et le corriger, est le sujet de la section 5.2.

> 💡 **Pourquoi les arbres l'emportent ici.** L'écart d'AUC n'est pas une loi de la nature : il dépend des données. Dans la simulation, le risque de départ dépend de **seuils** et d'**interactions** (récence supérieure à 150 jours *et* satisfaction inférieure à 3,2 ; trois tickets au support *et* beaucoup de retours ; beaucoup de promotions *sans* programme de fidélité…) que la régression logistique ne sait pas écrire. Sur des données où les effets sont réguliers et sans interactions marquées, la régression logistique, bien réglée, aurait **égalé** le boosting. C'est pourquoi on la garde toujours comme **modèle de référence** (chapitre 1, section 1.4) : si le boosting ne la bat pas nettement, il ne vaut pas sa complexité.

> ⚠️ **Le jeu de test est ouvert une fois.** Nous avons regardé le jeu de test pour chaque famille afin de les comparer ici : c'est une démonstration. En situation réelle, on choisirait le modèle **par validation croisée sur l'entraînement**, et l'on n'ouvrirait le jeu de test qu'**une seule fois**, pour le modèle retenu.

> ✅ **À retenir.**
> - Le **gradient boosting** construit des arbres **séquentiellement** : chaque arbre ajuste le **pseudo-résidu** $-\partial\ell/\partial F$ du modèle courant (le résidu pour la perte quadratique, $y-p$ pour la perte logistique), pondéré par un petit pas $\nu$. C'est une descente de gradient **dans l'espace des fonctions**.
> - **XGBoost** ajoute un objectif régularisé et un développement au second ordre : valeur de feuille $-G/(H+\lambda)$, gain de coupe explicite. **LightGBM** et `HistGradientBoostingClassifier` ajoutent histogrammes et croissance par feuille.
> - On règle surtout : **pas** $\nu$ (petit), **nombre d'arbres par arrêt précoce**, profondeur/feuilles, sous-échantillonnage, régularisation.
> - Les modèles à arbres gèrent **valeurs manquantes** et **catégories** sans artifice ; ils n'ont pas besoin de standardisation ; ils n'extrapolent pas.
> - Comparez **sur les mêmes données et les mêmes plis**, avec un écart **apparié** et son incertitude ; gardez un **modèle de référence** simple.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.6 (boosting écrit à la main), 2.7 (XGBoost et LightGBM : réglages, valeurs manquantes, catégories) et 2.8 (le match des modèles, avec comparaison appariée), exercices 2.9 et 2.10.


## 2.5 ➕ Pour aller plus loin : SVM et noyaux, k plus proches voisins, Bayes naïf

> 🧭 **Section optionnelle.** Trois familles classiques, que l'on rencontre encore souvent et qui illustrent chacune une idée utile : la **marge** et l'astuce du **noyau** (SVM), la **ressemblance** (k plus proches voisins), l'**hypothèse d'indépendance** (Bayes naïf). Sur des données tabulaires de taille moyenne, le boosting les devance généralement ; elles gardent leur intérêt pédagogique et, pour certains problèmes (peu de données, texte, images, données très structurées), leur intérêt pratique.

### 2.5.1 Les machines à vecteurs de support (SVM)

**L'idée de la marge.** Parmi toutes les droites qui séparent deux classes, laquelle choisir ? Celle qui laisse **le plus de place** de part et d'autre : la droite qui maximise la **marge**, la distance entre elle et les clients les plus proches. Une droite collée à des clients est fragile ; une droite au milieu d'une zone vide l'est moins. Les clients qui touchent la marge sont les **vecteurs de support** : ce sont les **seuls** qui déterminent la solution (déplacer un client loin de la marge ne change rien).

Quand les classes se chevauchent (c'est le cas de presque toutes les vraies données), on autorise des violations de la marge, pénalisées. Le problème, pour un score $f(x)=w^\top x+b$, s'écrit exactement dans le cadre de la section 2.1 :

$$\min_{w,b}\ \frac12\|w\|^2+C\sum_{i=1}^n\max\bigl(0,\,1-y_if(x_i)\bigr),$$

soit la **perte charnière** (section 2.1.1) plus une pénalité $\ell_2$. Le paramètre $C$ règle le compromis : grand $C$, on punit fort les violations (marge étroite, risque de surapprentissage) ; petit $C$, on tolère (marge large, modèle plus simple).

**L'astuce du noyau.** Un score linéaire ne sépare pas toujours les classes. L'astuce est de **transformer les variables** pour les rendre séparables, puis d'y chercher une frontière linéaire. Exemple minuscule, en dimension 1 : sept clients repérés par une variable $x$, la classe 1 étant celle des clients proches de zéro.

| $x$ | −3 | −2 | −1 | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|---|---|
| classe | 0 | 0 | 1 | 1 | 1 | 0 | 0 |

Sur la droite des réels, aucun seuil ne sépare les 1 des 0 (les 1 sont au milieu). Mais si l'on associe à chaque $x$ le point $\varphi(x)=(x,\,x^2)$, les clients de la classe 1 ont $x^2\le1$ et ceux de la classe 0 ont $x^2\ge4$ : la droite horizontale $x^2=2{,}5$ les sépare. Une **frontière linéaire dans l'espace transformé** correspond à une frontière **non linéaire** dans l'espace d'origine.

Le miracle est que l'on n'a jamais besoin de calculer $\varphi$ : l'algorithme n'utilise les clients que par leurs **produits scalaires** $\varphi(x)^\top\varphi(x')$, et un **noyau** $k(x,x')$ les calcule directement. Par exemple, le noyau polynomial de degré 2, $k(x,x')=(xx'+1)^2$, correspond à $\varphi(x)=(x^2,\sqrt2\,x,\,1)$ : pour $x=2$ et $x'=3$, $k=(6+1)^2=49$ et $\varphi(x)^\top\varphi(x')=36+12+1=49$. Le noyau le plus utilisé, le noyau **gaussien** (RBF), $k(x,x')=\exp\bigl(-\gamma\|x-x'\|^2\bigr)$, correspond à un espace de dimension *infinie* ; il mesure la **ressemblance** de deux clients, proche de 1 s'ils sont voisins et de 0 s'ils sont éloignés. Le paramètre $\gamma$ règle la portée : grand, chaque client n'influence que son voisinage immédiat (frontière très tourmentée) ; petit, la frontière est lisse.


![Deux SVM sur des données en forme de deux croissants. À gauche, une droite et ses marges (pointillés) : elle sépare mal. À droite, avec un noyau gaussien, la frontière épouse la forme des données. Les points cerclés sont les vecteurs de support.](figures/ch02-svm-noyaux.png)

Sur ces données en deux croissants entremêlés, le SVM linéaire classe correctement 76 % des clients de test, le SVM à noyau gaussien 90 %. Le premier s'appuie sur 61 vecteurs de support, le second sur 54 (sur 180 points d'entraînement).

Sur la résiliation, le SVM exige une chose que le boosting ignore : des variables **à l'échelle** (le noyau gaussien repose sur des distances). Il ne fournit pas directement de probabilités (seulement un score : la distance signée à la frontière, que l'on peut calibrer, section 5.2), et son coût d'entraînement croît environ comme le **carré** du nombre de clients : au-delà de quelques dizaines de milliers de lignes, il devient lent.

```python
from sklearn.svm import SVC

svm = make_pipeline(pre_lin, SVC(kernel="rbf", C=1.0, gamma="scale"))
svm.fit(Xtr, ytr)
print(round(roc_auc_score(yte, svm.decision_function(Xte)), 4))
```
<!--sortie-->
```text
0.8492
```


Sur nos clients, le SVM à noyau gaussien atteint une AUC de test de 0,849 et le SVM linéaire 0,862 (à comparer à 0,866 pour la régression logistique : même famille de fonctions, perte différente, résultats voisins). Sans mise à l'échelle des variables, le même SVM à noyau gaussien tombe à 0,757 : la récence en jours écrase tout le reste dans le calcul des distances.

### 2.5.2 Les k plus proches voisins (k-NN)

Le modèle le plus intuitif qui soit : pour prédire un nouveau client, on cherche, dans les données d'entraînement, les **$k$ clients qui lui ressemblent le plus** et l'on prend le vote de leurs classes. Il n'y a pas d'« entraînement » : le modèle **est** les données. Tout repose sur deux choix : la **distance** (en général euclidienne, sur des variables standardisées) et $k$, qui règle le compromis biais-variance du chapitre 1 : $k=1$ colle aux données (variance maximale, frontière en confettis), $k$ très grand lisse tout (biais fort).

**Le fléau de la dimension.** Le k-NN suppose qu'**être proche** a un sens. Or, quand le nombre de variables $d$ grandit, les distances **se concentrent** : tous les points deviennent à peu près aussi éloignés les uns des autres. Pour des points tirés uniformément dans un cube, le rapport entre la distance au voisin le plus proche et la distance au voisin le plus lointain tend vers 1 quand $d$ grandit : la notion de « plus proche voisin » perd son sens.


![Rapport entre la distance au plus proche voisin et la distance au plus lointain pour des points tirés au hasard, en fonction du nombre de variables : il tend vers 1.](figures/ch02-fleau-dimension.png)

Le rapport moyen est de 0,02 en dimension 2, de 0,28 en dimension 10 et de 0,86 en dimension 500 : dans ce dernier cas, le voisin « le plus proche » est presque aussi loin que le plus lointain. Pour un k-NN, ajouter des variables **inutiles** noie les variables utiles.

Sur la résiliation (45 colonnes après encodage), la validation croisée retient $k=$ 150 (AUC 0,849 ; avec $k=1$, seulement 0,643 : la variance). Sur le jeu de test, l'AUC est de 0,858, et de 0,839 sans mise à l'échelle. Le k-NN fait moins bien que les modèles précédents ici : trop de variables peu informatives, et une prédiction lente (il faut comparer le client à *tous* les autres).

### 2.5.3 Bayes naïf

Le classifieur de **Bayes naïf** applique la règle de Bayes (volume I, section 2.1) en faisant une hypothèse brutale : **les variables sont indépendantes entre elles, une fois la classe connue**. Pour une classe $k$ (parti, resté) et des variables $x_1,\dots,x_p$ :

$$P(k\mid x)\ \propto\ P(k)\prod_{j=1}^pP(x_j\mid k).$$

On n'a donc besoin d'estimer que des lois **à une variable**, ce qui est facile, même avec peu de données. Un exemple chiffré : douze clients, dont 4 sont partis. Parmi les 4 partis, 1 avait ouvert le dernier courriel et 3 avaient ouvert un ticket au support ; parmi les 8 restés, 6 avaient ouvert le courriel et 2 un ticket. Un nouveau client **n'a pas ouvert** le courriel et **a ouvert** un ticket :

- score « parti » : $\frac4{12}\times\frac34\times\frac34=0{,}1875$ ;
- score « resté » : $\frac8{12}\times\frac28\times\frac28=0{,}0417$ ;
- probabilité de départ : $\dfrac{0{,}1875}{0{,}1875+0{,}0417}\approx\mathbf{0{,}818}$.


L'hypothèse d'indépendance est presque toujours **fausse** (la récence et le nombre de commandes sont liés) mais, pour **classer**, elle est souvent tolérable : le classement reste raisonnable même quand les probabilités sont fausses. Sur nos données, un Bayes naïf gaussien (sur les variables numériques seules) obtient une AUC de 0,840. En revanche, ses **probabilités** sont mauvaises : en comptant plusieurs fois la même information, il devient **sûr de lui à tort**. Quand il annonce plus de 90 % de risque de départ (570 clients du jeu de test), il prédit en moyenne 97 % alors que 43 % seulement de ces clients partent. À titre de comparaison, la régression logistique annonce plus de 90 % pour 3 clients, avec 91 % prédits et 100 % observés. La perte logistique du Bayes naïf vaut 0,74 (contre 0,28 pour la régression logistique). C'est un exemple parfait de modèle **bien classant mais mal calibré** (section 5.2).

### 2.5.4 Comment choisir entre elles ?

```text
               modèle  AUC test
régression logistique    0.8659
         SVM linéaire    0.8617
         SVM gaussien    0.8492
                 k-NN    0.8579
  Bayes naïf gaussien    0.8395
    gradient boosting    0.9025
```

| Modèle | Hypothèse implicite | Atouts | Faiblesses |
|---|---|---|---|
| SVM à noyau | la ressemblance (le noyau) est bien choisie | peu de données, grande dimension, bonne frontière | exige des variables à l'échelle ; lent au-delà de quelques dizaines de milliers de lignes ; pas de probabilités directes |
| k-NN | les voisins se ressemblent | aucun entraînement, très simple, naturellement non linéaire | fléau de la dimension ; prédiction lente ; sensible à l'échelle |
| Bayes naïf | variables indépendantes entre elles à classe donnée | rapide, peu de données, texte | probabilités mal calibrées ; ignore les interactions |

Le tableau du dessus récapitule les AUC de test : sur ces données, le boosting reste devant. Mais ces trois modèles ont une vertu : ils obligent à penser en termes de **distance**, de **marge** et d'**indépendance**, trois idées qui reviennent partout en apprentissage automatique.

> ✅ **À retenir.**
> - Le **SVM** cherche la droite de **marge maximale** ; il minimise la perte charnière plus une pénalité $\ell_2$. Avec un **noyau** (gaussien, polynomial), il fait des frontières non linéaires sans calculer les variables transformées. Mise à l'échelle obligatoire.
> - Le **k-NN** prédit par vote des $k$ plus proches voisins : $k$ règle le compromis biais-variance ; le **fléau de la dimension** le rend fragile quand les variables sont nombreuses.
> - Le **Bayes naïf** suppose l'indépendance des variables à classe donnée : rapide et robuste pour classer, **mal calibré** pour estimer des probabilités.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.9 (SVM, k-NN, Bayes naïf face au boosting, et le fléau de la dimension), exercice 2.11 (Bayes naïf à la main).


## 2.6 ➕ Pour aller plus loin : CatBoost, stacking et blending

> 🧭 **Section optionnelle.** Deux idées pour aller au-delà d'un modèle unique : un boosting conçu pour les **variables catégorielles** (CatBoost), et la **combinaison** de plusieurs modèles différents (blending, stacking). Dans les deux cas, le danger principal est le même, et il est discret : la **fuite d'information** de la cible vers les variables.

### 2.6.1 CatBoost et le piège de l'encodage par la cible

Comment donner une variable à beaucoup de modalités (la ville, le code d'un produit) à un modèle ? L'encodage par indicatrices crée autant de colonnes que de modalités. Une idée tentante : remplacer la modalité par la **moyenne de la cible** dans cette modalité (l'**encodage par la cible**, *target encoding*). La ville D devient « 0,17 », parce que 17 % des clients de la ville D sont partis.

L'idée est excellente, **mais elle fuit** si on la calcule naïvement. La moyenne de la ville D contient la réponse du client lui-même : pour un client dont la ville ne compte que quelques clients, la valeur encodée *est* sa propre étiquette, à peine diluée. Le modèle apprend « une valeur élevée signifie parti » sur l'entraînement, où c'est vrai par construction, puis échoue sur de nouvelles données.

Pour le voir, fabriquons une variable **sans aucune information** : un identifiant de zone à 1 500 modalités, tiré au hasard, indépendant de la résiliation. Encodons-la naïvement par la moyenne de la cible, et ajustons un modèle logistique sur cette seule colonne.


Avec environ 6 clients par zone, le modèle ajusté sur l'encodage naïf atteint une AUC de **0,801** sur l'entraînement, sur une variable qui ne contient *rien*. Sur le jeu de test, l'AUC retombe à 0,505 : le hasard. C'est de la fuite pure : l'étiquette du client est passée dans la variable.

**La solution de CatBoost : l'encodage ordonné.** On met les clients dans un **ordre aléatoire** et l'on encode chaque client par la moyenne de la cible des **seuls clients qui le précèdent** dans cet ordre, avec un petit a priori pour lisser :

$$\text{enc}_i=\frac{\sum_{j<i,\ x_j=x_i}y_j+a\,p}{\#\{j<i:\ x_j=x_i\}+a},$$

où $p$ est la moyenne générale de la cible et $a$ un poids d'a priori. L'étiquette d'un client n'intervient donc **jamais** dans sa propre valeur. Un exemple à la main : six clients de deux villes, $a=1$ et $p=0{,}5$.

```text
ville  y  encodage_ordonne  encodage_naif
    A  1             0.500          0.667
    A  0             0.750          0.667
    A  1             0.500          0.667
    B  0             0.500          0.333
    B  0             0.250          0.333
    B  1             0.167          0.333
```

Pour la ville A, le premier client n'a pas d'historique : $\frac{0+0{,}5}{0+1}=0{,}5$ ; le deuxième voit un seul prédécesseur, parti ($y=1$) : $\frac{1+0{,}5}{1+1}=0{,}75$ ; le troisième voit deux prédécesseurs, un parti et un resté : $\frac{1+0{,}5}{2+1}=0{,}5$. L'encodage naïf aurait donné $0{,}667$ à tous les clients de la ville A, y compris ceux qui ont contribué à ce 0,667. Sur notre variable de bruit, l'encodage ordonné ramène l'AUC d'entraînement à 0,528 : le modèle n'a plus rien à mémoriser, ce qui est la bonne réponse.

**CatBoost** (Prokhorenkova et coll., 2018) fait de cette idée un principe : encodage ordonné des catégories, mais aussi **boosting ordonné** (les pseudo-résidus d'un client sont calculés avec un modèle qui ne l'a pas vu), et des arbres **symétriques** (*oblivious trees*, la même question à tous les nœuds d'un niveau), plus rapides et moins sujets au surapprentissage. En pratique, on lui passe les colonnes catégorielles telles quelles :

```python
from catboost import CatBoostClassifier

Xtr_cb, Xte_cb = Xtr.copy(), Xte.copy()
Xtr_cb[cat], Xte_cb[cat] = Xtr_cb[cat].fillna("manquant"), Xte_cb[cat].fillna("manquant")
catb = CatBoostClassifier(iterations=300, learning_rate=0.08, depth=6, cat_features=cat, random_seed=0, verbose=False, thread_count=1)
catb.fit(Xtr_cb, ytr)
print(round(roc_auc_score(yte, catb.predict_proba(Xte_cb)[:, 1]), 4))
```
<!--sortie-->
```text
0.9046
```


CatBoost obtient une AUC de test de 0,905, à comparer à 0,903 pour le boosting de la section 2.4 : sur ces données, avec peu de catégories, les deux sont équivalents. CatBoost brille surtout quand les variables catégorielles sont nombreuses ou à très grand nombre de modalités, et sa configuration par défaut est réputée robuste.

### 2.6.2 Combiner des modèles : le blending

Les modèles de la section 2.4 ne se trompent pas tous sur les mêmes clients. **Combiner** leurs prédictions peut donc faire mieux que le meilleur. Le plus simple est le **blending** (mélange) : une **moyenne** des probabilités prédites, éventuellement pondérée.

Pourquoi cela marche-t-il ? Par la même formule qu'en 2.3.2 : la variance de la moyenne de prédictions $\rho\sigma^2+\frac{1-\rho}B\sigma^2$ ne diminue que si les prédictions sont **peu corrélées**. Moyenner trois modèles quasi identiques ne sert à rien ; moyenner trois modèles de **familles différentes** (un linéaire, une forêt, un boosting) apporte quelque chose.

Une règle essentielle : les prédictions utilisées pour **choisir** les poids ne doivent pas être des prédictions **faites sur les données d'entraînement** du modèle, qui sont trop belles. On utilise des prédictions **hors pli** (*out-of-fold*, OOF) : pour chaque client, la prédiction d'un modèle entraîné sans lui, par validation croisée.


Les corrélations entre les prédictions hors pli sont de 0,88 (régression logistique et forêt), 0,83 (régression logistique et boosting) et 0,92 (forêt et boosting). La moyenne simple des trois modèles obtient une AUC de test de **0,900**, contre 0,903 pour le boosting seul : **le mélange est un peu moins bon que son meilleur membre**, parce que le modèle linéaire, nettement plus faible, dilue les autres. La moyenne forêt + boosting seulement obtient 0,904, un peu au-dessus. Moyennez des modèles de **niveau comparable**, ou pondérez-les (c'est ce que fait le stacking). Ces corrélations, toutes élevées, expliquent aussi la modestie du gain : ces modèles se trompent largement sur les mêmes clients.

### 2.6.3 Le stacking : laisser un modèle apprendre à combiner

Le **stacking** (empilement) pousse l'idée plus loin : au lieu de fixer les poids du mélange, on les **apprend** avec un **méta-modèle** (souvent une régression logistique), dont les variables d'entrée sont les prédictions des modèles de base. On passe de « moyenne égale » à « donne trois fois plus de poids au boosting qu'à la forêt, et un petit poids au modèle linéaire ». La condition de validité est celle du blending, et le piège est sournois : **le méta-modèle doit être entraîné sur des prédictions hors pli.**

```python
# oof : une colonne par modèle de base, prédictions HORS PLI (calculées plus haut avec cross_val_predict)
meta = LogisticRegression().fit(logit_(np.clip(oof, 1e-4, 1 - 1e-4)), ytr)
print(meta.coef_.round(2))
```
<!--sortie-->
```text
[[0.09 0.47 0.57]]
```

(`oof` a été calculé plus haut : pour chaque client, la prédiction de chaque modèle de base entraîné **sans lui**, par validation croisée à cinq plis. Les prédictions de test s'obtiennent en réentraînant chaque modèle sur tout l'entraînement.)


Les coefficients appris sur des prédictions hors pli sont 0,09 (régression logistique), 0,47 (forêt) et 0,57 (boosting) ; l'AUC de test de l'empilement est **0,904**. Que se passe-t-il si l'on commet la faute et que l'on entraîne le méta-modèle sur les prédictions que chaque modèle fait **sur ses propres données d'entraînement** ? La forêt, qui a vu ces clients, y est presque parfaite (AUC 0,986 sur l'entraînement) ; le méta-modèle conclut que la forêt est un oracle et lui donne un poids énorme (coefficients −1,67, 5,64, −0,12). Résultat sur le jeu de test : 0,883 au lieu de 0,904. Le coût d'un méta-modèle fautif n'est pas toujours spectaculaire, mais il va toujours dans le mauvais sens, et il **fausse l'évaluation** si on l'évalue lui aussi sur des données déjà vues.

### 2.6.4 Quand cela vaut-il la peine ?

Le gain de l'empilement sur le meilleur modèle seul est ici de 0,002 d'AUC, avec un intervalle à 95 % de [−0,001 ; 0,005] (bootstrap apparié sur le jeu de test). Aucune de ces combinaisons n'apporte plus qu'un gain marginal, et c'est typique : sur des données tabulaires de cette taille, **le boosting bien réglé capte l'essentiel**. Dans les compétitions de prédiction, où l'on se bat pour le troisième chiffre après la virgule, on empile systématiquement. Dans une entreprise, chaque modèle supplémentaire est un **coût** : plus de code, plus de dépendances, plus de pannes, plus de difficulté à expliquer. La question honnête n'est pas « peut-on gagner 0,002 ? » mais « ce gain justifie-t-il la complexité, au regard de la décision que l'on prend avec la prédiction ? »

> ✅ **À retenir.**
> - L'**encodage par la cible** naïf **fuit** : l'étiquette du client entre dans sa propre variable (sur du bruit pur, il « apprend » l'étiquette). **CatBoost** l'évite par l'**encodage ordonné** (on n'utilise que les clients qui précèdent).
> - Le **blending** moyenne des modèles ; il ne marche que si leurs erreurs sont **peu corrélées**.
> - Le **stacking** apprend la combinaison avec un méta-modèle, qui doit être entraîné sur des prédictions **hors pli**, jamais sur des prédictions faites sur les données d'entraînement.
> - Les gains sont souvent minces ; comparez-les à leur **coût de complexité**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.10 (encodage ordonné, CatBoost et empilement sans fuite), exercice 2.12 (blending et corrélation des erreurs).


## Bilan du chapitre 2

Vous savez maintenant :

- **décrire** un modèle supervisé par ses trois ingrédients (famille de fonctions, perte, algorithme), comprendre pourquoi on remplace le coût 0-1 par un substitut convexe (logistique, charnière), et **calculer à la main** un pas de descente de gradient ;
- expliquer pourquoi la descente de gradient et les pénalités exigent des variables **à l'échelle**, et voir la pénalité $\ell_2$ ou $\ell_1$ comme une **contrainte** (disque ou losange) ;
- **construire un arbre** à la main (impureté de Gini ou entropie, meilleur seuil, gain), le régler (profondeur, taille des feuilles, élagage par coût-complexité) et dire **ce qu'il sait écrire** (seuils, interactions) et **ce qui le fragilise** (l'instabilité) ;
- démontrer que la **variance d'une moyenne** de prédictions corrélées vaut $\rho\sigma^2+\frac{1-\rho}B\sigma^2$, en déduire le **bagging** et les **forêts aléatoires**, utiliser l'erreur **hors sac**, et **se méfier de l'importance par impureté** ;
- voir le **gradient boosting** comme une descente de gradient dans l'espace des fonctions (pseudo-résidu $-\partial\ell/\partial F$), calculer à la main une valeur de feuille et un gain de coupe **XGBoost**, régler le pas et le nombre d'arbres par **arrêt précoce**, et profiter des valeurs manquantes et des catégories natives de **LightGBM** ;
- **comparer** plusieurs familles sur les mêmes données avec une **différence appariée** et son incertitude, en gardant un modèle de référence simple ;
- (en option) comprendre la **marge** et l'astuce du **noyau** des SVM, le **fléau de la dimension** des k-NN, l'indépendance du **Bayes naïf**, l'**encodage ordonné** de CatBoost et le **stacking sans fuite**.

Sur la résiliation, la hiérarchie obtenue est la suivante, en AUC sur le jeu de test :

| Modèle | AUC |
|---|---|
| Régression logistique (référence) | 0,866 |
| Arbre de décision réglé | 0,885 |
| Forêt aléatoire | 0,896 |
| Gradient boosting | 0,903 |

Trois leçons dépassent ce chapitre. **Un modèle plus riche n'est pas toujours meilleur** : l'avantage des arbres ici vient des seuils et des interactions du problème, et ne serait pas apparu sur des données lisses. **L'évaluation prime sur l'algorithme** : jeu de test intact, validation croisée dans l'entraînement, comparaisons appariées, modèle de référence. Enfin, **chaque fois que l'on réutilise des étiquettes** (encodage par la cible, empilement), la fuite d'information guette.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.10 et exercices 2.1 à 2.12.

Le chapitre 3 quitte le monde des étiquettes : que peut-on apprendre des clients quand on ne sait pas ce que l'on cherche ? Le chapitre 4 reviendra sur la préparation des variables (encodage, échelle, déséquilibre), et le chapitre 5 sur l'évaluation fine des modèles (calibration, interprétabilité) que nous avons ici seulement effleurée.
