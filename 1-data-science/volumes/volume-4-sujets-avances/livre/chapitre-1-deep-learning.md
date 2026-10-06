# Chapitre 1 : Deep learning

> « Un réseau de neurones n'est pas un cerveau. C'est une longue composition de fonctions très simples, dont on ajuste les paramètres par descente de gradient. Tout le reste est de l'ingénierie. »

Les volumes précédents ont construit des modèles à partir de **variables que nous avions choisies** : le nombre de commandes, la récence, le panier moyen. Le travail de l'analyste consistait à fabriquer les bonnes colonnes, puis à laisser un modèle (une régression, une forêt, un boosting) les combiner. Face à une image, un son ou une phrase, cette méthode se heurte à un mur : il n'y a pas de colonne « récence » dans une photographie. Il y a des **centaines de milliers de pixels**, et personne ne sait écrire à la main la formule qui transforme ces pixels en « ceci est un 7 ».

L'**apprentissage profond** (*deep learning*) répond à ce mur par une idée simple : **apprendre aussi les variables**. Un réseau empile des couches ; chacune transforme la sortie de la précédente ; les premières couches apprennent des motifs élémentaires (des contours), les suivantes les assemblent (des boucles, des angles), les dernières décident (« c'est un 7 »). Tout est appris **de bout en bout**, avec la même méthode d'optimisation que celle de la régression logistique : la descente de gradient (volume I, section 1.3.3).

## Le chemin de ce chapitre

- **1.1 Réseaux de neurones et rétropropagation** : le neurone, les couches, les fonctions d'activation, et surtout la **rétropropagation**, que nous calculerons **entièrement à la main** sur un petit réseau avant de la laisser à la machine. Optimiseurs, gradients qui disparaissent, régularisation.
- **1.2 Réseaux convolutifs** : comment exploiter la structure d'une image (voisinage, répétition) avec très peu de paramètres.
- **1.3 Réseaux récurrents et LSTM** : comment lire une suite (les ventes quotidiennes de la boutique) en gardant une mémoire.
- ➕ **1.4 Frameworks** : PyTorch en pratique, face à TensorFlow/Keras.
- ➕ **1.5 Apprentissage par transfert, vision par ordinateur, OCR de documents** : réutiliser un réseau déjà entraîné ; lire des factures.
- ➕ **1.6 Deep learning pour données tabulaires et séries temporelles** : quand il vaut mieux **ne pas** l'utiliser.

> 🧭 **Un fil rouge d'honnêteté.** Le deep learning est spectaculaire sur les images, le son et le texte, mais il n'est ni gratuit ni magique. Chaque comparaison de ce chapitre se fait **contre une référence** (régression logistique, boosting, méthode naïve) et avec les règles du volume III : jeu de test intact, plusieurs graines, incertitude. Vous verrez des cas où le réseau gagne nettement, des cas où il égale à peine une méthode simple, et des cas où il perd.

## Les données de ce chapitre

| Jeu | Contenu | Utilisé en |
|---|---|---|
| **MNIST** (réel) | images de chiffres manuscrits de 28 × 28 pixels ; nous en gardons 10 000 pour l'entraînement et 2 000 pour le test | 1.1, 1.2, 1.5 |
| `ventes_quotidiennes.csv` (simulé) | trois ans de ventes quotidiennes de la boutique | 1.3 |
| `clients_ml.csv` (simulé) | les clients du volume III, cible de résiliation | 1.6 |
| factures (générées) | images de factures fabriquées avec une bibliothèque de dessin | 1.5 |

MNIST est un jeu **réel** : une base publique de chiffres manuscrits (LeCun, Cortes et Burges), obtenue via OpenML, libre pour la recherche et l'enseignement. Les chiffres ont été écrits à la main par des centaines de personnes. Les autres jeux sont simulés avec des graines fixes, ce qui nous permet de connaître la vérité.


![Seize images de MNIST avec leur étiquette. Chaque image est un tableau de 28 × 28 niveaux de gris.](figures/ch01-chiffres.png)

Une image de MNIST n'est que cela : un tableau de $28\times28=784$ nombres entre 0 et 255. Pour un modèle des volumes précédents, ce sont 784 colonnes sans signification individuelle (le pixel (14, 9) ne veut rien dire en soi). La difficulté de la vision par ordinateur est là tout entière.


## 1.1 Réseaux de neurones et rétropropagation

> 💡 **Intuition.** Un réseau de neurones est une **chaîne de petites machines à calculer**. Chacune prend des nombres, les combine par une somme pondérée, puis les « tord » par une fonction simple. En enchaînant quelques dizaines de ces machines, on obtient une fonction capable de dessiner presque n'importe quelle frontière. La seule difficulté est de **régler les poids** : c'est le rôle de la **rétropropagation**, qui n'est rien d'autre que la règle de dérivation des fonctions composées, appliquée avec méthode.

### 1.1.1 Un neurone, c'est une régression logistique

Un **neurone** reçoit un vecteur $\mathbf x=(x_1,\dots,x_p)$, calcule une somme pondérée et lui applique une fonction d'**activation** $\varphi$ :

$$a=\varphi(z),\qquad z=\mathbf w^\top\mathbf x+b=w_1x_1+\dots+w_px_p+b.$$

Si $\varphi$ est la sigmoïde $\sigma(z)=\frac1{1+e^{-z}}$, ce neurone **est** une régression logistique (volume II, section 2.2 ; volume III, section 2.1) : $a$ est une probabilité. Un neurone seul trace donc une frontière **droite** dans l'espace des variables. Sa puissance vient de l'assemblage.

### 1.1.2 Les fonctions d'activation : pourquoi tordre ?

Pourquoi ne pas se contenter de sommes pondérées ? Parce qu'enchaîner des opérations linéaires donne… une opération linéaire : $W_2(W_1\mathbf x)=(W_2W_1)\mathbf x$. Dix couches sans activation valent **une seule couche**. C'est la non-linéarité de $\varphi$ qui donne de la profondeur au réseau.

Trois activations dominent :

| Activation | Formule | Dérivée | Remarque |
|---|---|---|---|
| **Sigmoïde** | $\sigma(z)=\dfrac1{1+e^{-z}}$ | $\sigma(z)\,(1-\sigma(z))$ | sortie dans $]0,1[$ ; dérivée au plus égale à $0{,}25$ |
| **Tangente hyperbolique** | $\tanh(z)$ | $1-\tanh^2(z)$ | sortie dans $]-1,1[$, centrée ; dérivée au plus égale à $1$ |
| **ReLU** | $\max(0,z)$ | $1$ si $z>0$, $0$ sinon | très simple, ne « sature » pas pour $z>0$ |


![Les trois activations les plus courantes (à gauche) et leurs dérivées (à droite). La dérivée de la sigmoïde ne dépasse jamais 0,25 et s'écrase vers 0 loin de l'origine ; celle de la ReLU vaut 1 partout où le neurone est actif.](figures/ch01-activations.png)

La dérivée compte autant que la fonction : c'est elle qui transporte le signal d'apprentissage vers l'arrière du réseau. Nous verrons en 1.1.6 pourquoi la faible dérivée de la sigmoïde est un problème.

### 1.1.3 Un réseau, c'est des produits de matrices

Regroupons $m$ neurones en une **couche** : leurs poids forment une matrice $W$ de $m$ lignes (une par neurone) et $p$ colonnes, leurs biais un vecteur $\mathbf b$. La couche calcule d'un coup

$$\mathbf a=\varphi(W\mathbf x+\mathbf b).$$

Un réseau à deux couches cachées et une sortie s'écrit $\hat y=f_3\big(f_2(f_1(\mathbf x))\big)$ avec $f_k(\mathbf u)=\varphi_k(W_k\mathbf u+\mathbf b_k)$. Le **nombre de paramètres** se compte simplement : une couche de $p$ entrées et $m$ sorties en a $m\,(p+1)$. Pour un réseau qui lit une image aplatie de $784$ pixels, avec deux couches cachées de $128$ et $64$ neurones et $10$ sorties (un score par chiffre) :

$$128\times(784+1)+64\times(128+1)+10\times(64+1)=100\,480+8\,256+650=109\,386\ \text{paramètres}.$$

### 1.1.4 La perte : mesurer l'erreur

Entraîner, c'est **minimiser une perte** $L$ qui mesure l'écart entre la prédiction et la réalité.

- **Régression** : l'erreur quadratique $L=\frac12(\hat y-y)^2$.
- **Classification binaire** : l'entropie croisée $L=-\big[y\ln\hat y+(1-y)\ln(1-\hat y)\big]$ (c'est l'opposé de la log-vraisemblance de la régression logistique).
- **Classification à $K$ classes** : on transforme les $K$ scores $z_k$ en probabilités par la fonction **softmax**, $p_k=\dfrac{e^{z_k}}{\sum_j e^{z_j}}$, puis on prend $L=-\ln p_{y}$, l'opposé du logarithme de la probabilité attribuée à la bonne classe.

> 📐 **Un résultat utile : le gradient de softmax + entropie croisée.** Pour la perte $L=-\ln p_y$, on a $\dfrac{\partial L}{\partial z_k}=p_k-\mathbb 1_{k=y}$. Autrement dit : *probabilité prédite moins probabilité réelle (0 ou 1)*. *Preuve.* $L=-z_y+\ln\sum_je^{z_j}$ ; donc $\partial L/\partial z_k=-\mathbb 1_{k=y}+\dfrac{e^{z_k}}{\sum_je^{z_j}}$. $\blacksquare$ Pour la sigmoïde et l'entropie croisée binaire, le résultat est le même : $\partial L/\partial z=\hat y-y$. Cette simplicité explique que l'on associe presque toujours ces deux éléments.

### 1.1.5 La rétropropagation, entièrement à la main

L'entraînement par descente de gradient exige $\partial L/\partial w$ pour **chaque** poids du réseau. Le principe de la **rétropropagation** (*backpropagation*) est la règle de la chaîne : si $L$ dépend de $z_2$, qui dépend de $a_1$, qui dépend de $z_1$, qui dépend de $w$, alors

$$\frac{\partial L}{\partial w}=\frac{\partial L}{\partial z_2}\cdot\frac{\partial z_2}{\partial a_1}\cdot\frac{\partial a_1}{\partial z_1}\cdot\frac{\partial z_1}{\partial w}.$$

On calcule d'abord toutes les valeurs **en avançant** (passe avant), puis on remonte les dérivées **en reculant** (passe arrière), en réutilisant à chaque couche le résultat de la couche suivante. C'est ce qui rend le calcul efficace : un seul aller-retour donne **tous** les gradients.

Prenons le plus petit réseau intéressant : **deux entrées, deux neurones cachés (sigmoïde), un neurone de sortie (sigmoïde)**, avec l'entropie croisée binaire. Les valeurs sont choisies pour que les calculs restent lisibles.

- Entrée : $\mathbf x=(1,\ 2)$, étiquette $y=1$.
- Couche cachée : $W_1=\begin{pmatrix}0{,}1&0{,}3\\0{,}2&-0{,}1\end{pmatrix}$, $\mathbf b_1=(0,\ 0{,}1)$.
- Sortie : $W_2=(0{,}4,\ -0{,}2)$, $b_2=0{,}05$.


**Passe avant.** On avance, couche par couche :

| Étape | Calcul | Valeur |
|---|---|---|
| $z_1^{(1)}$ | $0{,}1\times1+0{,}3\times2+0$ | $0{,}7000$ |
| $z_1^{(2)}$ | $0{,}2\times1-0{,}1\times2+0{,}1$ | $0{,}1000$ |
| $a_1^{(1)}=\sigma(z_1^{(1)})$ | | $0{,}6682$ |
| $a_1^{(2)}=\sigma(z_1^{(2)})$ | | $0{,}5250$ |
| $z_2$ | $0{,}4\times0{,}6682-0{,}2\times0{,}5250+0{,}05$ | $0{,}2123$ |
| $\hat y=a_2=\sigma(z_2)$ | | $0{,}5529$ |
| Perte $L=-\ln\hat y$ | | $0{,}5926$ |

Le réseau donne une probabilité de 55,3 % à la classe 1, alors que la vérité est 1 : la perte vaut 0,593.

**Passe arrière.** On remonte. À la sortie, d'après le résultat du 1.1.4 (sigmoïde et entropie croisée), $\delta_2=\dfrac{\partial L}{\partial z_2}=\hat y-y=-0{,}4471$. Les gradients de la couche de sortie s'en déduisent immédiatement, car $z_2=\mathbf w_2^\top\mathbf a_1+b_2$ :

$$\frac{\partial L}{\partial W_2}=\delta_2\,\mathbf a_1=(-0{,}2988,\ -0{,}2347),\qquad\frac{\partial L}{\partial b_2}=\delta_2=-0{,}4471.$$

Pour la couche cachée, le signal $\delta_2$ **revient** vers chaque neurone caché, multiplié par le poids qui les relie, puis par la dérivée de la sigmoïde $a(1-a)$ (valant $0{,}2217$ et $0{,}2494$) :

$$\delta_1^{(j)}=\big(w_2^{(j)}\,\delta_2\big)\cdot a_1^{(j)}\big(1-a_1^{(j)}\big)\quad\Longrightarrow\quad\boldsymbol\delta_1=(-0{,}0397,\ 0{,}0223).$$

Les gradients de $W_1$ sont le produit extérieur $\boldsymbol\delta_1\mathbf x^\top$ :

$$\frac{\partial L}{\partial W_1}=\begin{pmatrix}-0{,}0397&-0{,}0793\\0{,}0223&0{,}0446\end{pmatrix},\qquad\frac{\partial L}{\partial\mathbf b_1}=\boldsymbol\delta_1.$$

**Un pas de descente de gradient** (pas $\eta=0{,}5$) : chaque paramètre est diminué de $\eta$ fois son gradient. On obtient $W_2=(0{,}5494,\ -0{,}0826)$, $b_2=0{,}2736$ et $W_1=\begin{pmatrix}0{,}1198&0{,}3397\\0{,}1888&-0{,}1223\end{pmatrix}$. Refaisons la passe avant avec ces nouveaux poids : la sortie passe de $0{,}5529$ à $0{,}6486$ et la **perte de $0{,}593$ à $0{,}433$**. Le réseau s'est rapproché de la bonne réponse.

> ✅ **Vérifié deux fois.** Ces gradients ont été recalculés par la **différentiation automatique** de PyTorch : les quatre tenseurs de gradients coïncident avec ceux de la main (`autograd_ok = True`), et une **différence finie** sur un poids (on calcule $\frac{L(w+\varepsilon)-L(w-\varepsilon)}{2\varepsilon}$) donne la même valeur (`True`). Cette dernière vérification, la **vérification de gradient**, est le réflexe à avoir quand on écrit une rétropropagation soi-même.

Les bibliothèques (PyTorch, TensorFlow) font exactement ce calcul, sur des millions de paramètres, en construisant automatiquement le graphe des opérations pendant la passe avant. Vous n'écrirez jamais la rétropropagation vous-même en pratique ; mais l'avoir faite une fois explique **tout ce qui suit** : pourquoi les gradients peuvent disparaître, pourquoi l'initialisation compte, pourquoi la ReLU a changé la donne.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1 (la même rétropropagation en `numpy`, avec vérification de gradient), exercices 1.1 à 1.4.

### 1.1.6 Quand les gradients disparaissent (ou explosent)

Dans la passe arrière, le signal d'erreur est **multiplié** à chaque couche par une dérivée d'activation et par un poids. Avec $L$ couches, il subit environ $L$ multiplications. Pour la sigmoïde, dont la dérivée vaut au plus $0{,}25$, le signal est au plus divisé par 4 à chaque couche : au bout de 10 couches, par plus d'un million. Les premières couches **n'apprennent presque plus** : c'est le problème des **gradients qui disparaissent** (*vanishing gradients*). À l'inverse, des poids trop grands les font **exploser**.


![Norme du gradient dans chacune des 10 couches d'un réseau profond (échelle logarithmique). Avec la sigmoïde, la première couche reçoit un signal environ un milliard de fois plus faible que la dernière.](figures/ch01-gradients-profondeur.png)

Mesurons-le : dans un réseau de 10 couches, le rapport entre le gradient de la première et celui de la dernière couche est de $1{,}4\times10^{-9}$ avec la sigmoïde, $2{,}3\times10^{-3}$ avec la tanh, $4{,}3\times10^{-4}$ avec la ReLU et l'initialisation par défaut, et seulement $0{,}09$ avec la ReLU et l'**initialisation de He**. Trois remèdes se sont imposés :

1. **La ReLU** : sa dérivée vaut 1 pour les neurones actifs, le signal n'est plus écrasé.
2. **Une bonne initialisation.** Si les poids sont tirés avec une variance trop faible, le signal s'éteint ; trop grande, il explose. L'initialisation de **Glorot** (variance $\frac{2}{n_{\text{ent}}+n_{\text{sor}}}$, adaptée à la tanh) et celle de **He** (variance $\frac2{n_{\text{ent}}}$, adaptée à la ReLU) maintiennent la variance du signal d'une couche à l'autre.
3. **Les connexions résiduelles** (*skip connections*) des réseaux profonds : on ajoute l'entrée de la couche à sa sortie, $\mathbf a=\mathbf x+f(\mathbf x)$, ce qui laisse au gradient un chemin direct vers l'arrière (voir ResNet, section 1.5).

### 1.1.7 Les optimiseurs : comment descendre

La descente de gradient du volume I (section 1.3.3) fait un pas dans la direction opposée au gradient. En pratique on ne calcule pas le gradient sur toutes les données, mais sur un petit **lot** (*mini-batch*) tiré au hasard : c'est la **descente de gradient stochastique** (SGD), plus rapide et mieux adaptée aux gros jeux de données. Trois variantes se rencontrent partout :

- **SGD** : $w\leftarrow w-\eta\,g$.
- **Avec moment** (*momentum*) : on garde une moyenne glissante des gradients, $v\leftarrow\beta v+g$ puis $w\leftarrow w-\eta v$ ; la « vitesse » lisse les oscillations et accélère dans les vallées étroites.
- **Adam** : il adapte le pas **paramètre par paramètre** en suivant la moyenne des gradients $m$ et celle de leurs carrés $v$ :
$$m\leftarrow\beta_1m+(1-\beta_1)g,\quad v\leftarrow\beta_2v+(1-\beta_2)g^2,\quad w\leftarrow w-\eta\,\frac{\hat m}{\sqrt{\hat v}+\varepsilon},$$
où $\hat m$ et $\hat v$ sont les moyennes corrigées de leur biais initial. Les valeurs usuelles sont $\beta_1=0{,}9$, $\beta_2=0{,}999$.


![Trois optimiseurs sur le même réseau (MNIST, 10 époques, mêmes données et même initialisation). À gauche, la perte d'entraînement ; à droite, l'exactitude en validation.](figures/ch01-optimiseurs.png)

Sur le même réseau, après 10 époques, le SGD simple atteint 88,4 % d'exactitude en validation, le SGD avec moment 93,5 % et Adam 91,9 %. La leçon n'est pas qu'« Adam est le meilleur » : le SGD avec moment gagne ici, parce que **le pas d'apprentissage a été réglé pour lui** ($0{,}05$) et non pour Adam ($0{,}001$, sa valeur usuelle). Le **pas d'apprentissage** est le réglage le plus influent d'un entraînement : trop petit, on n'avance pas ; trop grand, la perte oscille ou diverge. Adam est populaire parce qu'il est **peu sensible** à ce réglage, pas parce qu'il serait toujours meilleur.

### 1.1.8 La régularisation : empêcher le réseau d'apprendre par cœur

Un réseau a tant de paramètres qu'il peut **mémoriser** un jeu d'entraînement : l'erreur d'entraînement tombe à zéro, l'erreur sur des données nouvelles reste élevée (c'est le surapprentissage du volume III, section 1.3). Quatre moyens de le limiter :

- **La décroissance des poids** (*weight decay*) : on pénalise la taille des poids, comme la régression Ridge (volume II, section 1.5), pour des fonctions plus lisses.
- **Le dropout** : à chaque pas, on **éteint au hasard** une fraction $p$ des neurones. Le réseau ne peut plus compter sur un neurone précis : il doit répartir l'information. À la prédiction, on les rallume tous (avec une mise à l'échelle qui conserve l'espérance, voir l'exercice 1.5 du cahier).
- **L'arrêt précoce** : on suit l'erreur de validation et l'on conserve les poids de la meilleure époque (le même principe que l'arrêt précoce du boosting, volume III, section 2.4.5).
- **La normalisation par lots** (*batch normalization*) : on recentre et on réduit les activations de chaque lot ; cela stabilise l'entraînement et régularise légèrement.

Pour **voir** le surapprentissage, il faut peu de données. Entraînons un réseau large (512-512) sur seulement 1 000 images, et comparons les quatre variantes, **sur trois graines** pour ne pas confondre effet réel et hasard.


![Sans régularisation, l'exactitude d'entraînement atteint 100 % en quelques époques alors que l'exactitude en validation plafonne : l'écart entre les deux courbes mesure le surapprentissage.](figures/ch01-surapprentissage.png)

| Variante (1 000 images, 3 graines) | Exactitude d'entraînement | Exactitude de validation (moyenne ± écart-type) |
|---|---|---|
| sans régularisation | 100,0 % | 89,1 % ± 0,1 |
| décroissance des poids (0,01) | 99,6 % | 88,3 % ± 0,2 |
| dropout (0,5) | 100,0 % | 90,1 % ± 0,3 |
| arrêt précoce | 100,0 % | 89,0 % ± 0,2 |

Le réseau sans régularisation apprend les 1 000 images par cœur (100,0 % en entraînement) mais n'en généralise que 89,1 %. Le **dropout** est ici la variante la plus utile : il gagne 1,0 point(s) de validation, soit nettement plus que l'écart-type entre graines (de l'ordre de 0,1 à 0,3 point). La décroissance des poids avec ce coefficient (0,01) **fait perdre** 0,8 point : un coefficient trop fort bride le réseau, et il faudrait le régler. L'arrêt précoce ne change rien de mesurable ici. Retenez deux choses : l'effet d'une régularisation dépend de son **réglage** et du problème, et il faut le **mesurer sur plusieurs graines** avant de proclamer qu'une astuce « marche ».

### 1.1.9 Ce que savent faire les réseaux, et ce qu'ils coûtent

Un résultat théorique explique la polyvalence des réseaux : le **théorème d'approximation universelle** (Cybenko, 1989 ; Hornik, 1991) affirme qu'un réseau à **une seule couche cachée** suffisamment large peut approcher n'importe quelle fonction continue sur un domaine borné, avec la précision voulue. Attention à ce qu'il **ne dit pas** : il ne dit pas combien de neurones il faut (possiblement un nombre énorme), ni que la descente de gradient **trouvera** les bons poids, ni que le réseau **généralisera**. C'est un théorème d'existence, pas une recette.

Voyons ce que cela donne sur MNIST, face aux références du volume III. Le réseau 784-128-64-10 de la section 1.1.3 se définit et s'entraîne ainsi :

```python
modele = nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
histo = entrainer(modele, xt_p, yt, xv_p, yv, epoques=25, lr=3e-3)
print(nb_parametres(modele), "paramètres | exactitude sur le test :", round(exactitude(modele, xte_p, yte), 4))
```
<!--sortie-->
```text
109386 paramètres | exactitude sur le test : 0.9445
```

La fonction `entrainer` contient la boucle d'entraînement ; nous la détaillerons en 1.4.


| Modèle (entraîné sur 8 000 images) | Exactitude sur le test |
|---|---|
| Régression logistique (sur les pixels) | 89,1 % |
| Boosting (LightGBM, 100 arbres) | 95,0 % |
| Réseau dense 784-128-64-10 (109 386 paramètres) | 94,5 % |

> ⚠️ **Le réseau ne « bat » pas le boosting ici.** Un perceptron multicouche entraîné sur 8 000 images obtient à peu près le score d'un boosting bien réglé. L'avantage du deep learning sur les images ne vient pas des couches *denses*, mais des couches **convolutives** de la section suivante, qui exploitent la structure de l'image. Un réseau dense traite les 784 pixels comme 784 colonnes indépendantes, comme le ferait un boosting.

> ✅ **À retenir.**
> - Un **neurone** = somme pondérée + activation ; une **couche** = un produit de matrices ; un réseau = des couches enchaînées ; son nombre de paramètres se compte à la main.
> - La **non-linéarité** des activations est indispensable ; la **ReLU** et une bonne **initialisation** combattent les gradients qui disparaissent.
> - La **rétropropagation** est la règle de la chaîne appliquée de l'arrière vers l'avant ; avec sigmoïde (ou softmax) et entropie croisée, le gradient de sortie vaut simplement « prédiction moins vérité ».
> - **Adam** est peu sensible au pas d'apprentissage ; le **pas** reste le réglage décisif.
> - La régularisation (poids, dropout, arrêt précoce) limite le surapprentissage ; on la juge sur **plusieurs graines**.
> - Le théorème d'approximation universelle est un théorème d'existence : il ne garantit ni l'apprentissage ni la généralisation.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 et 1.3, exercice 1.5.


## 1.2 Réseaux convolutifs

> 💡 **Intuition.** Pour reconnaître un « 7 », il ne faut pas regarder les 784 pixels un par un : il faut repérer **un trait horizontal en haut, puis un trait oblique**, où qu'ils se trouvent dans l'image. Un réseau convolutif encode exactement cette idée : il fait glisser sur l'image un **petit détecteur** (un filtre de $3\times3$ pixels) et note **où** il se déclenche. Le même détecteur sert partout, ce qui réduit le nombre de paramètres de façon spectaculaire.

### 1.2.1 Pourquoi un réseau dense convient mal aux images

Le réseau de la section 1.1 traite l'image comme une liste de 784 nombres. Deux défauts en découlent.

- **Trop de paramètres.** Une seule couche dense de 128 neurones sur une image de $28\times28$ en a $100\,480$. Sur une photographie de $1\,000\times1\,000$ pixels, ce serait **plus de 128 millions** de poids pour la seule première couche.
- **Aucune notion de voisinage.** Pour un réseau dense, mélanger au hasard les 784 pixels (avec la même permutation pour toutes les images) ne change rien à ce qu'il peut apprendre : il ne sait pas que deux pixels voisins se ressemblent. De plus, un chiffre **décalé** de deux pixels devient, pour lui, une image entièrement différente.

Une image a pourtant deux propriétés évidentes : ce qui compte est **local** (un contour est fait de pixels voisins) et **répété** (un contour peut apparaître n'importe où).

### 1.2.2 La convolution, entièrement à la main

Une **convolution** (en réalité une *corrélation croisée*, mais tout le monde dit convolution) fait glisser un **filtre** $K$ de taille $k\times k$ sur l'image. À chaque position, on multiplie terme à terme le filtre et la zone qu'il recouvre, puis on somme.

Prenons une image de $5\times5$ pixels avec un **bord vertical** (sombre à gauche, clair à droite), et un filtre qui répond aux transitions « sombre → clair » :

$$\text{image}=\begin{pmatrix}0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\end{pmatrix},\qquad K=\begin{pmatrix}-1&0&1\\-1&0&1\\-1&0&1\end{pmatrix}.$$

En haut à gauche, le filtre recouvre les colonnes 1 à 3 de l'image, c'est-à-dire les valeurs $(0,0,1)$ sur chaque ligne :
$$(-1\times0+0\times0+1\times1)\times3\ \text{lignes}=3.$$
Une position plus à droite (colonnes 2 à 4, valeurs $(0,1,1)$) donne $(0+0+1)\times3=3$ ; encore une plus à droite (colonnes 3 à 5, valeurs $(1,1,1)$), $(-1+0+1)\times3=0$. En répétant sur les trois lignes de positions, on obtient une **carte de caractéristiques** (*feature map*) de $3\times3$ :

$$\text{sortie}=\begin{pmatrix}3&3&0\\3&3&0\\3&3&0\end{pmatrix}.$$

Le filtre « s'allume » (valeur 3) là où la fenêtre contient le bord, et reste éteint (0) là où l'image est uniforme. Il a **détecté un contour vertical**.


La taille de la sortie se calcule avec une formule à connaître : pour une entrée de largeur $n$, un filtre de largeur $k$, un **rembourrage** (*padding*) de $p$ pixels de zéros de chaque côté et un **pas** (*stride*) $s$,

$$\text{largeur de sortie}=\left\lfloor\frac{n+2p-k}{s}\right\rfloor+1.$$

Sur notre exemple : $n=5,\ k=3$. Sans rembourrage ($p=0,s=1$) : $\frac{5-3}{1}+1=3$. Avec $p=1$ : $\frac{5+2-3}{1}+1=5$, la sortie garde la taille de l'entrée (c'est le rôle du rembourrage). Avec un pas de 2 : $\frac{5-3}{2}+1=2$ (calculs vérifiés par PyTorch : 5 et 2 de largeur).

Un filtre est un **petit détecteur de motif** ; un réseau convolutif en apprend **plusieurs** par couche (8, 16, 64…), dont les poids sont appris par rétropropagation exactement comme ceux d'un réseau dense. Ils découvrent seuls des détecteurs de contours, de coins, de textures.

### 1.2.3 Le pooling : résumer, tolérer les petits décalages

Après la convolution et la ReLU, on réduit souvent la carte par **pooling** : on découpe la carte en fenêtres de $2\times2$ et l'on ne garde que **le maximum** (*max pooling*) de chaque fenêtre. Sur une carte de $4\times4$ :

$$\begin{pmatrix}1&3&2&0\\4&2&1&1\\0&1&5&2\\2&0&3&6\end{pmatrix}\ \longrightarrow\ \begin{pmatrix}\max(1,3,4,2)&\max(2,0,1,1)\\\max(0,1,2,0)&\max(5,2,3,6)\end{pmatrix}=\begin{pmatrix}4&2\\2&6\end{pmatrix}.$$

La carte est quatre fois plus petite, et la valeur gardée est « le détecteur s'est-il déclenché *quelque part* dans cette zone ? » : un motif décalé d'un pixel donne souvent le même résultat. C'est la première source de **tolérance aux décalages**.

### 1.2.4 Partage des paramètres et champ réceptif

Deux idées font l'efficacité des réseaux convolutifs.

1. **Le partage des paramètres.** Un filtre de $3\times3$ n'a que $9+1=10$ paramètres (9 poids et un biais), quelle que soit la taille de l'image : le **même** filtre est appliqué à toutes les positions.
2. **Le champ réceptif.** Un neurone de la première couche voit une zone de $3\times3$ pixels. Un neurone de la deuxième couche voit $3\times3$ neurones de la première, c'est-à-dire une zone de $5\times5$ pixels. Chaque couche supplémentaire de filtres $3\times3$ élargit le champ de 2 pixels ; un pooling $2\times2$ **double l'écart entre neurones voisins** : les couches suivantes élargissent alors le champ deux fois plus vite. En **empilant** des couches, les neurones profonds voient de grandes zones : les premières couches détectent des contours, les suivantes des formes, les dernières des objets.

### 1.2.5 Un petit réseau convolutif, pas à pas

Construisons un réseau minuscule pour MNIST : une convolution à 8 filtres $3\times3$, une ReLU, un pooling ; une convolution à 16 filtres, une ReLU, un pooling ; puis une couche dense qui produit les 10 scores.

```python
cnn = nn.Sequential(
    nn.Conv2d(1, 8, kernel_size=3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, kernel_size=3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(16 * 5 * 5, 10))
histo_cnn = entrainer(cnn, xt, yt, xv, yv, epoques=6, lr=3e-3)
x = xte[:1]
for couche in cnn:
    x = couche(x); print(f"{type(couche).__name__:10s} -> {tuple(x.shape)}")
```
<!--sortie-->
```text
Conv2d     -> (1, 8, 26, 26)
ReLU       -> (1, 8, 26, 26)
MaxPool2d  -> (1, 8, 13, 13)
Conv2d     -> (1, 16, 11, 11)
ReLU       -> (1, 16, 11, 11)
MaxPool2d  -> (1, 16, 5, 5)
Flatten    -> (1, 400)
Linear     -> (1, 10)
```

Le suivi des **formes** (*shape bookkeeping*) est le premier outil de débogage d'un réseau : à chaque couche, on vérifie que ce qui sort est ce que l'on attendait. Ici, $28\to26$ (filtre $3\times3$ sans rembourrage : $28-3+1$), puis $26\to13$ (pooling), $13\to11$, $11\to5$ (pooling, avec arrondi vers le bas), et enfin $16\times5\times5=400$ valeurs aplaties.

Le nombre de paramètres se compte à la main : la première convolution a $8\times(1\times3\times3+1)=80$ paramètres, la seconde $16\times(8\times3\times3+1)=1\,168$, la couche dense $400\times10+10=4\,010$ : en tout **5 258**. À comparer aux **109 386** du réseau dense de la section 1.1.


![Les 8 filtres de la première couche (rouge : poids positifs, bleu : négatifs), et les cartes de caractéristiques qu'ils produisent pour un chiffre de test. Chaque filtre réagit à une orientation ou à une zone différente.](figures/ch01-filtres-cartes.png)

Après 6 époques, ce réseau de 5 258 paramètres atteint **96,2 %** d'exactitude sur le test, contre **94,5 %** pour le réseau dense de 109 386 paramètres : **environ 21 fois moins de paramètres pour un résultat équivalent ou meilleur**. Les filtres de la figure sont lisibles : certains répondent à des contours obliques, d'autres à des zones sombres ou claires.

### 1.2.6 Robustesse aux décalages et augmentation de données

L'avantage réel du convolutif apparaît quand les images **changent un peu**. Décalons horizontalement les images de test de 0 à 4 pixels, sans réentraîner, et mesurons l'exactitude des deux réseaux.


![Exactitude des deux réseaux quand on décale les images de test (sans réentraînement). L'exactitude des deux s'effondre, mais celle du réseau dense s'effondre plus vite.](figures/ch01-decalages.png)

Sans décalage, les deux réseaux sont proches (96,2 % et 94,5 %). Avec un décalage de 3 pixels, le réseau convolutif conserve 72,2 % d'exactitude, le réseau dense seulement 49,0 %. Ni l'un ni l'autre n'est **invariant** aux décalages (la convolution est *équivariante* : décaler l'entrée décale la carte, mais le pooling et la couche dense finale ne rétablissent qu'une invariance partielle) ; le convolutif y est simplement plus tolérant.

Le remède le plus répandu est l'**augmentation de données** : on fabrique des exemples d'entraînement supplémentaires en appliquant à chaque image des transformations qui **ne changent pas l'étiquette** (décalages, petites rotations, retournements si le sujet s'y prête, changements de luminosité). Ici, nous ajoutons à chaque image deux copies décalées au hasard de $-3$ à $+3$ pixels. Le réseau convolutif passe à **97,0 %** sur le test (et 93,0 % sur les images décalées de 3 pixels) ; le réseau dense à 94,5 % (89,8 % décalé).

> ⚠️ **L'augmentation doit respecter l'étiquette.** Retourner un « 6 » à l'envers en fait un « 9 » ; décaler un chiffre de quelques pixels n'en change pas le sens. Les transformations d'augmentation se choisissent avec la connaissance du métier, et ne s'appliquent qu'au jeu d'**entraînement**.

### 1.2.7 Les grandes architectures

Les réseaux convolutifs ont connu une succession d'architectures de plus en plus profondes. **LeNet** (1998), pour la reconnaissance de chiffres, ressemble beaucoup au réseau de cette section. **AlexNet** (2012) a remporté une compétition de reconnaissance d'images avec une marge si large qu'elle a lancé la vague actuelle : plus de couches, des ReLU, du dropout et des cartes graphiques. **VGG** (2014) a montré qu'empiler des filtres $3\times3$ suffit. **ResNet** (2015) a introduit les **connexions résiduelles** qui permettent d'entraîner des réseaux de plus de cent couches (nous le réutiliserons en 1.5). Les noms changent ; le principe reste celui de cette section : **des filtres locaux et partagés, empilés**.

> ✅ **À retenir.**
> - Un réseau dense ignore le voisinage des pixels et compte des centaines de milliers de poids ; un **réseau convolutif** exploite le caractère **local** et **répété** des motifs.
> - Une convolution fait glisser un filtre ; la taille de sortie vaut $\lfloor(n+2p-k)/s\rfloor+1$ ; le **pooling** résume et apporte une tolérance aux petits décalages.
> - Le **partage des paramètres** réduit drastiquement leur nombre ; empiler les couches élargit le **champ réceptif**.
> - Le suivi des **formes** à chaque couche est le premier outil de débogage.
> - L'**augmentation de données** (transformations qui préservent l'étiquette) améliore la généralisation, sur l'entraînement seulement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4 et 1.5, exercices 1.6 et 1.7.


## 1.3 Réseaux récurrents et LSTM

> 💡 **Intuition.** Pour prédire les ventes de demain, on ne regarde pas un seul chiffre : on lit **la suite** des jours précédents (le rythme de la semaine, la tendance, la dernière promotion). Un réseau récurrent lit cette suite **un élément à la fois** en gardant dans un **vecteur d'état** (sa « mémoire ») un résumé de ce qu'il a déjà lu. À chaque pas, il combine la nouvelle entrée et l'ancienne mémoire pour produire la nouvelle mémoire.

### 1.3.1 Le réseau récurrent simple et la rétropropagation dans le temps

Un **réseau récurrent** (*RNN*) applique **la même transformation** à chaque pas de temps $t$ :

$$h_t=\tanh\!\big(W_x\,x_t+W_h\,h_{t-1}+b\big).$$

L'état $h_t$ dépend de l'entrée $x_t$ et de l'état précédent $h_{t-1}$, lui-même fonction de $x_{t-1}$ et de $h_{t-2}$, et ainsi de suite : le réseau a une **mémoire** de toute la suite. Les mêmes poids $W_x$, $W_h$ servent à tous les pas, comme le filtre d'une convolution sert à toutes les positions de l'image.

On **déroule** le réseau dans le temps : il devient un réseau très profond (une couche par pas de temps) dont toutes les couches partagent leurs poids. La rétropropagation de la section 1.1 s'y applique telle quelle ; on l'appelle **rétropropagation dans le temps** (*backpropagation through time*, BPTT). Le gradient de la perte à l'instant $T$ par rapport à un état ancien $h_t$ s'écrit comme un **produit** de $T-t$ facteurs :

$$\frac{\partial h_T}{\partial h_t}=\prod_{s=t+1}^{T}\operatorname{diag}\!\big(1-h_s^2\big)\,W_h.$$

C'est exactement la situation des gradients qui disparaissent de la section 1.1.6, mais avec le **même** facteur $W_h$ répété : si ses valeurs propres sont plus petites que 1, le produit s'écrase vers zéro ; si elles sont plus grandes, il explose.

### 1.3.2 Mesurer la disparition du gradient dans le temps

Mesurons-le. Nous construisons un RNN et lui présentons une suite de 60 pas ; nous calculons l'influence de **chaque entrée** $x_t$ sur la dernière sortie (la norme du gradient de la dernière sortie par rapport à $x_t$), puis nous faisons la moyenne géométrique sur 10 initialisations aléatoires.


![Influence d'une entrée sur la dernière sortie, selon son ancienneté (échelle logarithmique). Le RNN simple « oublie » en quelques dizaines de pas ; le LSTM dont la porte d'oubli est initialisée à 1 conserve beaucoup mieux la trace.](figures/ch01-gradient-temps.png)

Lisons la figure. Pour le RNN simple, l'influence d'une entrée vieille de 10 pas est déjà de $3{,}9\times10^{-4}$, et de $1{,}3\times10^{-17}$ à 59 pas : au-delà d'une vingtaine de pas, le réseau est **aveugle** au passé. Le LSTM n'est pas magique non plus : avec l'initialisation par défaut, il décroît presque aussi vite ($5{,}9\times10^{-14}$ à 59 pas). Sa force vient de sa **conception** (section suivante) combinée à une bonne initialisation : avec un biais de porte d'oubli égal à 1, l'influence à 59 pas est de $8{,}2\times10^{-7}$, soit environ **$6{,}3\times10^{10}$ fois** celle du RNN.

### 1.3.3 Le LSTM : une mémoire protégée par des portes

Le **LSTM** (*long short-term memory*, Hochreiter et Schmidhuber, 1997) sépare deux choses : une **cellule mémoire** $c_t$, qui voyage d'un pas à l'autre presque sans transformation, et un **état de sortie** $h_t$. Trois **portes**, des sigmoïdes qui produisent des nombres entre 0 et 1, décident de ce qui entre, de ce qui reste et de ce qui sort :

| Porte | Formule | Rôle |
|---|---|---|
| **Oubli** $f_t$ | $\sigma(W_f[x_t,h_{t-1}]+b_f)$ | quelle fraction de l'ancienne mémoire garder |
| **Entrée** $i_t$ | $\sigma(W_i[x_t,h_{t-1}]+b_i)$ | quelle fraction du nouveau candidat écrire |
| **Candidat** $g_t$ | $\tanh(W_g[x_t,h_{t-1}]+b_g)$ | la nouvelle information proposée |
| **Sortie** $o_t$ | $\sigma(W_o[x_t,h_{t-1}]+b_o)$ | quelle partie de la mémoire exposer |

$$c_t=f_t\odot c_{t-1}+i_t\odot g_t,\qquad h_t=o_t\odot\tanh(c_t).$$

La mise à jour de la mémoire est **additive** ($c_t=f_t c_{t-1}+\dots$) : tant que la porte d'oubli reste proche de 1, l'information (et le gradient) traverse de nombreux pas sans s'écraser. C'est tout le secret.

**Un pas à la main.** Prenons un LSTM d'**une seule unité** (tous les nombres sont des scalaires), avec l'entrée $x_t=1$, l'état précédent $h_{t-1}=0{,}5$ et la mémoire précédente $c_{t-1}=0{,}2$. Les poids (entrée, état, biais) sont $(0{,}5;\,0{,}3;\,0{,}1)$ pour la porte d'entrée, $(0{,}4;\,0{,}2;\,0{,}5)$ pour l'oubli, $(0{,}9;\,-0{,}4;\,0)$ pour le candidat et $(0{,}7;\,0{,}6;\,-0{,}1)$ pour la sortie.


| Étape | Calcul | Valeur |
|---|---|---|
| Entrée $i$ | $\sigma(0{,}5\cdot1+0{,}3\cdot0{,}5+0{,}1)=\sigma(0{,}75)$ | 0,679 |
| Oubli $f$ | $\sigma(0{,}4+0{,}1+0{,}5)=\sigma(1)$ | 0,731 |
| Candidat $g$ | $\tanh(0{,}9-0{,}2+0)=\tanh(0{,}7)$ | 0,604 |
| Sortie $o$ | $\sigma(0{,}7+0{,}3-0{,}1)=\sigma(0{,}9)$ | 0,711 |
| Mémoire $c_t$ | $f\cdot0{,}2+i\cdot g$ | 0,557 |
| État $h_t$ | $o\cdot\tanh(c_t)$ | 0,359 |

Le calcul, refait avec la cellule `LSTMCell` de PyTorch dont on a imposé les mêmes poids, donne la même mémoire et le même état (vérification : `True`). Remarquez la porte d'oubli : à 0,73, elle garde les trois quarts de la mémoire précédente.

> 💡 **Le GRU.** Le *gated recurrent unit* (Cho et al., 2014) est une variante plus légère : il fusionne la cellule et l'état, et n'a que deux portes (mise à jour et réinitialisation). Il a moins de paramètres que le LSTM et donne souvent des résultats comparables ; c'est un bon premier essai quand les données sont peu nombreuses.

### 1.3.4 Prévoir les ventes quotidiennes de la boutique

Retour au concret. Le fichier `ventes_quotidiennes.csv` contient trois ans de ventes quotidiennes de la boutique (1 096 jours, 2024 étant bissextile), avec l'indicateur de **promotion** du jour. Les ventes suivent un rythme hebdomadaire (le samedi est le jour fort), un pic de fin d'année, une légère tendance et un bruit multiplicatif. La tâche : **prédire les ventes de demain** connaissant les jours précédents, le calendrier de demain et sa promotion.

**Le découpage est temporel**, comme au volume II (section 4.3.3) : on s'entraîne sur 2023-2024 (703 jours exploitables) et l'on teste sur 2025 (365 jours). Jamais d'aléatoire sur une série temporelle : le futur ne doit pas fuiter dans l'entraînement.

Avant tout réseau, il faut des **références** :

- le **naïf saisonnier** : prédire la valeur du même jour de la semaine précédente ;
- le **boosting sur retards** : un `LightGBM` qui reçoit les 14 derniers jours, ceux d'il y a 21 et 28 jours, le jour de la semaine, le mois et la promotion (nous avons écarté le retard de 364 jours, qui aurait privé le boosting de la moitié de ses données d'entraînement) ;
- un plafond théorique, que seule la simulation autorise : la **prévision parfaite**, qui connaît la structure exacte (rythme, saison, tendance, promotion) et ne se trompe que du bruit irréductible.

Le LSTM reçoit, lui, une **fenêtre** des 28 derniers jours (ventes en logarithme, standardisées, et indicateur de promotion) et, en plus, le calendrier du jour à prédire. Voici le modèle.

```python
class PrevisionLSTM(nn.Module):
    def __init__(self, cache=16):
        super().__init__()
        self.lstm = nn.LSTM(2, cache, batch_first=True)      # entrée : (ventes, promo) par jour
        self.tete = nn.Sequential(nn.Linear(cache + 10, 16), nn.ReLU(), nn.Linear(16, 1))
    def forward(self, fenetre, calendrier):
        sorties, _ = self.lstm(fenetre)                      # (lot, 28, cache)
        return self.tete(torch.cat([sorties[:, -1], calendrier], dim=1)).squeeze(1)
```

L'état de la **dernière** position résume la fenêtre ; il est concaténé au calendrier (promo, jour de la semaine, saison) et passé à une petite couche dense. L'entraînement (40 époques d'Adam, trois graines différentes) est celui de la section 1.4.


![Les 70 premiers jours de 2025 : ventes réelles et prévisions à un jour. Le naïf saisonnier recopie la semaine précédente, y compris un pic de promotion qui n'a plus lieu (mi-février) ; le LSTM, qui connaît la promotion du jour et le calendrier, ne le recopie pas.](figures/ch01-previsions-ventes.png)

L'erreur est mesurée par l'**erreur absolue moyenne** (MAE, en euros par jour ; le niveau moyen des ventes en 2025 est de 173 €) :

| Méthode | MAE (€/jour) | Erreur relative moyenne |
|---|---|---|
| Naïf saisonnier (même jour, semaine précédente) | 27,86 | 16,2 % |
| Boosting sur retards | 21,76 | 12,2 % |
| **LSTM** (moyenne de 3 graines) | **20,50** (écart-type 0,39) | 11,3 % |
| Prévision parfaite (plafond de la simulation) | 17,55 | 10,1 % |

Le LSTM fait mieux que les deux références : nettement mieux que le naïf, **bien plus modestement** que le boosting. La lecture doit rester prudente, pour trois raisons.

1. **L'écart au plafond.** La prévision parfaite se trompe encore de 17,55 € par jour : c'est le bruit pur, impossible à prédire. Le LSTM reste au-dessus de ce plancher (écart apparié de 2,88 €, intervalle à 95 % de 1,73 à 4,15) : il récupère une bonne part de l'écart entre le naïf et le plafond, pas la totalité.
2. **L'incertitude.** Les graines du LSTM donnent des MAE de 20,15 à 20,93. Un **bootstrap par blocs de 7 jours** (sur la moyenne des prévisions des trois graines, de MAE 20,43 € ; on rééchantillonne des semaines entières pour respecter l'autocorrélation) sur la différence des erreurs absolues, jour par jour, donne : boosting moins LSTM = 1,32 € par jour, intervalle à 95 % de 0,34 à 2,50 ; naïf moins LSTM = 7,43 €, de 5,25 à 9,57. Les deux intervalles **excluent zéro** : l'avantage du LSTM est visible sur l'année de test, très net face au naïf, mais **mince** face au boosting (la borne basse est proche de zéro). Il ne garantit pas qu'il en serait de même une autre année, ni avec un boosting mieux réglé.
3. **La nature des données.** Les ventes sont **simulées** avec une structure régulière (rythme hebdomadaire stable, pic annuel net). Sur des données réelles, plus désordonnées, l'écart entre un bon boosting à retards et un LSTM est souvent bien plus mince ; le boosting, lui, est plus rapide, plus simple à régler et plus facile à expliquer.

> 💡 **Le bon réflexe.** Pour une série temporelle, **commencez par le naïf saisonnier, puis un boosting à retards**. N'adoptez un LSTM que si, sur un découpage temporel rigoureux et plusieurs graines, il bat ces références **de façon convaincante** et que le surcoût (entraînement, surveillance, explication) en vaut la peine. La section 1.6 revient sur les séries temporelles et sur les alternatives modernes.

> ✅ **À retenir.**
> - Un RNN lit une suite en gardant un état ; la **rétropropagation dans le temps** déroule le réseau et multiplie des facteurs qui font **disparaître** (ou exploser) le gradient.
> - Le **LSTM** protège une cellule mémoire par des **portes** (oubli, entrée, sortie) et une mise à jour **additive** ; le GRU en est une version légère.
> - L'initialisation compte : un biais d'oubli proche de 1 prolonge la mémoire.
> - En prévision, comparez toujours à un **naïf saisonnier** et à un **boosting sur retards**, avec un découpage **temporel**, plusieurs graines, et un plafond de bruit quand il est connu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.6, exercices 1.8 et 1.9.


## 1.4 ➕ Pour aller plus loin : les frameworks de deep learning

> 🧭 Section optionnelle. Elle est utile dès que vous écrivez vos propres réseaux ; vous pouvez la sauter si vous voulez seulement comprendre les principes.

Jusqu'ici, nous avons utilisé la fonction `entrainer` (fournie avec le livre) pour ne pas encombrer les explications. Cette section ouvre la boîte : ce qu'un **framework** fournit, à quoi ressemble une boucle d'entraînement, et comment PyTorch se compare à TensorFlow/Keras.

### 1.4.1 Ce que fournit un framework

Un framework de deep learning apporte quatre choses que nous avons faites à la main dans la section 1.1, et qu'il fait **pour vous** :

1. des **tenseurs** (tableaux à plusieurs dimensions), utilisables sur processeur comme sur carte graphique ;
2. la **différentiation automatique** : il enregistre les opérations effectuées et calcule tous les gradients (c'est le `backward()` que nous avons comparé à notre rétropropagation manuelle) ;
3. des **couches et optimiseurs** prêts à l'emploi (`Linear`, `Conv2d`, `LSTM`, `Adam`…) ;
4. de quoi **sauvegarder, charger et déployer** les modèles.

### 1.4.2 PyTorch et TensorFlow/Keras

Les deux frameworks dominants sont **PyTorch** (Meta) et **TensorFlow** avec son interface **Keras** (Google). Ce livre utilise PyTorch, qui s'est imposé dans la recherche et dans la plupart des projets récents.

| | PyTorch | TensorFlow / Keras |
|---|---|---|
| Style | on écrit la boucle d'entraînement ; le graphe est construit **à l'exécution** | `model.fit(...)` fait tout ; le graphe peut être compilé |
| Débogage | comme du Python ordinaire (`print`, point d'arrêt) | plus indirect en mode compilé |
| Souplesse | très grande (architectures inhabituelles, recherche) | grande, mais l'API de haut niveau cadre davantage |
| Déploiement | export ONNX, TorchScript, serveurs dédiés | écosystème de déploiement très complet (mobile, navigateur) |
| Usage typique | recherche, modèles de langage, la plupart des nouveaux projets | systèmes existants en production, déploiement embarqué |

Le même petit réseau s'écrit ainsi en Keras (code **non exécuté** ici : TensorFlow n'est pas installé dans l'environnement du livre) :

```python
import keras
modele = keras.Sequential([keras.layers.Input((784,)), keras.layers.Dense(64, activation="relu"), keras.layers.Dense(10)])
modele.compile(optimizer="adam", loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=["accuracy"])
modele.fit(x_train, y_train, epochs=5, batch_size=128, validation_data=(x_val, y_val))
```

> 💡 **Lequel choisir ?** Le choix compte moins que l'on croit : les concepts (tenseurs, gradients, couches, optimiseurs) sont les mêmes, et un réseau écrit dans l'un se traduit dans l'autre en une heure. Choisissez celui que votre équipe maîtrise, ou celui de l'écosystème dont vous avez besoin (modèles pré-entraînés, déploiement).

### 1.4.3 Une boucle d'entraînement lisible

Voici la boucle que `entrainer` exécute, réduite à l'essentiel : à chaque **époque** (un passage sur toutes les données), on mélange les exemples, on les découpe en **lots**, et pour chaque lot on enchaîne quatre gestes : remettre les gradients à zéro, calculer la perte, rétropropager, mettre à jour.

```python
modele = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))
optimiseur = torch.optim.Adam(modele.parameters(), lr=3e-3)
graine(0)
for epoque in range(3):
    ordre = torch.randperm(len(xt_p))                        # on mélange les exemples
    for debut in range(0, len(ordre), 128):
        lot = ordre[debut:debut + 128]
        optimiseur.zero_grad()                               # 1. gradients à zéro
        perte = nn.functional.cross_entropy(modele(xt_p[lot]), yt[lot])   # 2. perte
        perte.backward()                                     # 3. rétropropagation
        optimiseur.step()                                    # 4. mise à jour des poids
    print(f"époque {epoque + 1} : perte du dernier lot = {perte.item():.3f}")
```
<!--sortie-->
```text
époque 1 : perte du dernier lot = 0.557
époque 2 : perte du dernier lot = 0.212
époque 3 : perte du dernier lot = 0.195
```

Les quatre gestes se retrouvent dans **tous** les programmes d'entraînement PyTorch. Deux oublis classiques : omettre `zero_grad()` (les gradients s'**accumulent** d'un lot à l'autre, et l'entraînement diverge) et évaluer le modèle sans `modele.eval()` ni `torch.no_grad()` (le dropout reste actif, et l'on gaspille de la mémoire à mémoriser un graphe inutile).

### 1.4.4 Processeur, carte graphique et reproductibilité

PyTorch place les tenseurs sur un **périphérique** : `cpu` ou `cuda` (une carte graphique NVIDIA). Le code de la section précédente s'exécute sur l'un ou l'autre en déplaçant le modèle et les données avec `.to(périphérique)`. Les cartes graphiques accélèrent massivement les grands réseaux (multiplications de matrices), mais pas les petits : pour les exemples de ce chapitre, un processeur suffit.

```python
print("carte graphique disponible sur cette machine :", torch.cuda.is_available())
peripherique = "cuda" if torch.cuda.is_available() else "cpu"
modele = modele.to(peripherique)           # les données se déplacent de la même façon : x.to(peripherique)
```
<!--sortie-->
```text
carte graphique disponible sur cette machine : False
```

La **reproductibilité** demande de fixer les graines des générateurs aléatoires (`torch.manual_seed`, `np.random.seed`) **avant** de créer le modèle et de mélanger les lots. Vérifions que deux entraînements avec la même graine donnent exactement la même perte, et qu'une autre graine donne un résultat légèrement différent :


| Entraînement | Perte de validation |
|---|---|
| graine 0, première exécution | 0.319800 |
| graine 0, deuxième exécution | 0.319800 |
| graine 1 | 0.315035 |

Les deux premières lignes sont identiques (égalité exacte : `True`). Sur carte graphique, certaines opérations restent non déterministes (l'ordre des additions varie), et l'égalité n'est alors qu'approchée ; `torch.use_deterministic_algorithms(True)` force le déterminisme, au prix de la vitesse. Dans tous les cas, **le résultat d'un réseau dépend de la graine** : pour comparer deux modèles, il faut plusieurs graines (nous l'avons fait en 1.1.8).

### 1.4.5 Sauvegarder et recharger

Un modèle entraîné se sauvegarde sous la forme de son **dictionnaire d'état** (`state_dict`) : les valeurs de tous ses paramètres. Pour le recharger, on recrée **la même architecture**, puis on y charge les valeurs.

```python
chemin = "modele_ch01.pt"
torch.save(modele.state_dict(), chemin)
copie = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))   # même architecture
copie.load_state_dict(torch.load(chemin)); copie.eval()
print("mêmes sorties après rechargement :", torch.allclose(modele.cpu()(xte_p[:50]), copie(xte_p[:50])))
```
<!--sortie-->
```text
mêmes sorties après rechargement : True
```


Pour **déployer** un modèle hors de Python (serveur de production, navigateur, mobile), on l'exporte dans un format neutre comme **ONNX**, lisible par des moteurs d'inférence rapides. Le chapitre 4 de ce volume y revient avec la mise en production.

> ✅ **À retenir.**
> - Un framework fournit **tenseurs, différentiation automatique, couches, optimiseurs** et outils de sauvegarde.
> - La boucle d'entraînement PyTorch tient en quatre gestes : `zero_grad`, perte, `backward`, `step`.
> - Fixer les **graines** rend un entraînement reproductible sur processeur ; comparer des modèles exige plusieurs graines.
> - On sauvegarde le `state_dict`, et on recharge dans la même architecture.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.10.


## 1.5 ➕ Pour aller plus loin : apprentissage par transfert, vision par ordinateur et OCR

> 🧭 Section optionnelle. Elle montre comment réutiliser un réseau déjà entraîné, panorama les tâches de vision, puis traite un cas concret : lire des factures.

### 1.5.1 Réutiliser un réseau entraîné : le transfert

Entraîner un réseau convolutif profond demande des millions d'images et des jours de calcul. Heureusement, ce qu'il apprend est en grande partie **réutilisable** : les premières couches détectent des contours et des textures utiles pour presque toute image. L'**apprentissage par transfert** (*transfer learning*) consiste à prendre un réseau **pré-entraîné** sur un grand jeu (ici **ResNet-18**, entraîné sur ImageNet, un million d'images de 1 000 catégories), à retirer sa dernière couche (celle qui produit les 1 000 catégories d'ImageNet) et à utiliser ce qui reste comme **extracteur de caractéristiques** : chaque image devient un vecteur de 512 nombres, sur lequel on entraîne un modèle simple.

Deux variantes existent. L'**extraction de caractéristiques** (celle que nous faisons) gèle tout le réseau. Le **réglage fin** (*fine-tuning*) continue l'entraînement de tout ou partie des couches avec un très petit pas d'apprentissage.

```python
import torchvision
resnet = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).eval()
resnet.fc = nn.Identity()                                   # on retire la classification : il reste 512 caractéristiques
moy, ect = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

def caracteristiques(x, lot=250):
    sortie = []
    with torch.no_grad():
        for i in range(0, len(x), lot):
            b = nn.functional.interpolate(x[i:i + lot], size=64, mode="bilinear").repeat(1, 3, 1, 1)   # 28×28 gris -> 64×64 couleur
            sortie.append(resnet((b - moy) / ect))                                                    # mêmes statistiques qu'ImageNet
    return torch.cat(sortie).numpy()
```

Les images de MNIST sont en niveaux de gris de $28\times28$ ; ResNet attend des images en couleurs de grande taille, normalisées comme ImageNet. Nous agrandissons donc les chiffres à $64\times64$ et répétons le canal gris trois fois.

> ⚠️ **Un test honnête.** ImageNet ne contient **aucun chiffre manuscrit** : ses caractéristiques ont été apprises sur des chats, des voitures, des outils. Le transfert marche d'autant mieux que la nouvelle tâche **ressemble** à la tâche d'origine. MNIST est donc un cas défavorable, ce qui en fait un test instructif : nous comparons, selon le nombre d'images d'entraînement, trois approches : une régression logistique sur les pixels, un petit réseau convolutif entraîné **de zéro** (celui de la section 1.2) et une régression logistique sur les **caractéristiques de ResNet**.


![Exactitude sur 1 000 images de test selon le nombre d'images d'entraînement, pour trois approches.](figures/ch01-transfert.png)

| Images d'entraînement | Régression logistique (pixels) | Petit CNN de zéro | ResNet-18 gelé + régression |
|---|---|---|---|
| 50 | 65,2 % | 69,3 % | 63,6 % |
| 200 | 80,0 % | 84,0 % | 82,3 % |
| 1 000 | 86,8 % | 91,9 % | 91,3 % |
| 2 000 | 87,2 % | 94,3 % | 92,5 % |

Trois constats, qu'il faut lire avec la prudence d'un seul jeu de 1 000 images de test (une exactitude vaut à environ ±1 point près) :

1. **Avec très peu d'images (50), aucune approche n'est bonne**, et les caractéristiques d'ImageNet ne sont pas meilleures que les pixels bruts (63,6 % contre 65,2 %).
2. **Avec plus d'images, ResNet gelé devance la régression sur les pixels** : de 82,3 % contre 80,0 % à 200 images (un écart encore à peine plus grand que l'incertitude), à 91,3 % contre 86,8 % à 1 000 images. Ses 512 caractéristiques (contours, courbes) sont plus informatives que les pixels isolés, **même sans avoir jamais vu un chiffre**.
3. **Sur ce problème, le petit CNN entraîné de zéro fait aussi bien, voire mieux** (94,3 % contre 92,5 % à 2 000 images). Le transfert n'est pas un gain automatique : sur une tâche simple et éloignée d'ImageNet, un petit réseau bien adapté suffit.

Le transfert est surtout précieux quand la tâche **ressemble** aux données d'origine (photos de produits, de plantes, de documents), que les images sont **peu nombreuses** et que l'on ne peut pas entraîner un grand réseau. Dans ce cas, c'est souvent la meilleure première approche, avant d'envisager le réglage fin. Le temps d'extraction des caractéristiques de ces 3 000 images est de quelques secondes sur un processeur ordinaire.

### 1.5.2 Les tâches de la vision par ordinateur

La classification d'images n'est qu'une tâche parmi d'autres. Chacune a ses architectures et sa mesure d'erreur.

| Tâche | Question | Exemples de modèles | Mesure usuelle |
|---|---|---|---|
| **Classification** | « Que contient l'image ? » | ResNet, EfficientNet, Vision Transformer | exactitude, AUC |
| **Détection** | « Quels objets, et où ? » (boîtes) | YOLO, Faster R-CNN | $\mathrm{IoU}$, précision moyenne (mAP) |
| **Segmentation** | « Quels pixels appartiennent à quoi ? » | U-Net, Mask R-CNN | $\mathrm{IoU}$ moyen par classe |
| **Reconnaissance de texte (OCR)** | « Quels caractères sont écrits ? » | Tesseract, modèles de lecture de documents | taux d'erreur par caractère |
| **Génération** | « Produire une image » | modèles de diffusion | évaluation humaine, métriques de distribution |

La mesure $\mathrm{IoU}$ (*intersection over union*) compare une boîte prédite $P$ à la boîte vraie $V$ : $\mathrm{IoU}=\dfrac{\text{aire}(P\cap V)}{\text{aire}(P\cup V)}$ ; elle vaut 1 pour une boîte parfaite et 0 pour deux boîtes disjointes ; on compte souvent une détection comme correcte à partir de 0,5. Deux boîtes de $10\times10$ décalées de 5 pixels se recouvrent sur $5\times10=50$, leur union est de $100+100-50=150$ : $\mathrm{IoU}=1/3$, une détection **ratée** malgré une position qui paraît proche.

Les **Vision Transformers** (2020), qui découpent l'image en petits carrés traités comme les mots d'une phrase, rivalisent aujourd'hui avec les réseaux convolutifs sur les grands jeux de données ; le mécanisme d'attention qu'ils utilisent est présenté au chapitre 2.

### 1.5.3 Cas concret : lire des factures (OCR)

La boutique reçoit des factures de ses fournisseurs sous forme d'images, et voudrait en extraire le texte. L'**OCR** (*optical character recognition*, reconnaissance optique de caractères) transforme une image de texte en texte. Nous utilisons **Tesseract**, un moteur libre, par l'intermédiaire de la bibliothèque `pytesseract`, sur des factures **fabriquées** avec la bibliothèque de dessin Pillow (texte noir sur fond blanc, cinq lignes : numéro, date, client, article, total). Fabriquer les images nous donne la **vérité** (le texte exact) pour mesurer l'erreur.


```python
import pytesseract
texte = pytesseract.image_to_string(image, lang="fra")      # image : un objet PIL ; le résultat est une chaîne de caractères
```

**Mesurer la qualité de lecture.** On compare le texte lu au texte vrai par la **distance d'édition de Levenshtein** : le plus petit nombre d'insertions, de suppressions et de substitutions de caractères pour passer d'un texte à l'autre. Divisée par la longueur du texte vrai, elle donne le **taux d'erreur par caractère** (*character error rate*, CER) : 0 pour une lecture parfaite, 0,10 si environ un caractère sur dix est faux.

```python
def levenshtein(a, b):
    ligne = list(range(len(b) + 1))                              # distances de "" à chaque préfixe de b
    for i, ca in enumerate(a, 1):
        precedent, ligne[0] = ligne[0], i
        for j, cb in enumerate(b, 1):
            precedent, ligne[j] = ligne[j], min(ligne[j] + 1, ligne[j - 1] + 1, precedent + (ca != cb))
    return ligne[-1]

cer = lambda lu, vrai: levenshtein(lu, vrai) / len(vrai)
print(levenshtein("FACTURE", "FACTURF"), "erreur sur 7 caractères ->", round(cer("FACTURF", "FACTURE"), 3))
```
<!--sortie-->
```text
1 erreur sur 7 caractères -> 0.143
```

Un exemple de lecture, sur une facture propre (on ignore les lignes vides que le moteur insère entre les blocs de texte, et l'on n'affiche que les lignes qui diffèrent du texte vrai) :


```text
lu   : Article C8 x3 67.52€
vrai : Article C8 x3   67.52 €
lu   : TOTAL TIC : 375.33 €
vrai : TOTAL TTC : 375.33 €
```

Sur cette facture, la distance d'édition est de 4 pour 100 caractères vrais : un CER de **0,040**. Le calcul à la main est identique à celui de la bibliothèque `rapidfuzz` sur les quatre paires de contrôle (vérification : `True`).

**Le prétraitement : aide ou piège ?** Une règle de bon sens veut que l'on **nettoie** l'image avant la lecture. Voici le prétraitement classique : un filtre médian (qui efface le bruit isolé), une **binarisation** (chaque pixel devient noir ou blanc selon un seuil) et un agrandissement ×2.

```python
def pretraiter(image):
    adouci = image.filter(ImageFilter.MedianFilter(3))                       # efface le bruit isolé
    gris = np.array(adouci)
    noir_blanc = ((gris > gris.mean() * 0.8) * 255).astype(np.uint8)         # binarisation par seuil
    return Image.fromarray(noir_blanc).resize((image.width * 2, image.height * 2))
```

Nous le testons sur 8 factures, dans cinq conditions : image propre, avec bruit, inclinée de 4°, en basse résolution (réduite puis agrandie) et floue.


![En haut : la même facture propre, inclinée et floue. En bas : taux d'erreur par caractère moyen de Tesseract sur 8 factures, avec et sans prétraitement.](figures/ch01-ocr.png)

| Condition | CER, image brute | CER, après prétraitement | Factures améliorées (sur 8) |
|---|---|---|---|
| Propre | 0,032 | 0,024 | 6 |
| Bruit | 0,051 | 0,046 | 3 |
| Inclinée de 4° | 0,066 | 0,058 | 4 |
| Basse résolution | 0,152 | 0,246 | 0 |
| Floue | 0,229 | 0,360 | 1 |

La leçon est contrintuitive : **le prétraitement n'est pas une recette universelle**. Il aide un peu sur l'image propre et inclinée, mais **dégrade** la lecture quand l'image est floue ou de basse résolution (0,229 → 0,360 et 0,152 → 0,246) : la binarisation par seuil détruit les niveaux de gris dont le moteur avait besoin pour deviner les caractères flous. Avec seulement 8 factures, les écarts fins sont fragiles ; ce qui est solide est le **sens** des grandes différences (le flou et la basse résolution coûtent bien plus cher que le bruit modéré ou l'inclinaison).

> 💡 **Le bon réflexe en OCR.** (1) Mesurez le CER sur des **documents représentatifs** avant et après chaque étape ; (2) corrigez d'abord la **qualité de capture** (résolution, éclairage, cadrage) plutôt que de réparer ensuite ; (3) ajoutez des **contrôles métier** (un total doit être la somme des lignes ; une date doit exister) ; (4) gardez un humain pour les cas douteux. Les erreurs de lecture les plus coûteuses (un `0` lu `O` dans un montant) ne sont pas celles que le CER pénalise le plus.

> ✅ **À retenir.**
> - Le **transfert** réutilise un réseau pré-entraîné comme extracteur de caractéristiques (gelé) ou le **règle finement** ; il est précieux quand les données sont peu nombreuses **et** proches de la tâche d'origine.
> - Il n'est pas gratuit : sur une tâche éloignée et simple (ici, des chiffres), un petit réseau entraîné de zéro peut faire aussi bien.
> - Les tâches de vision (classification, détection, segmentation, OCR) ont chacune leurs modèles et leurs mesures (exactitude, $\mathrm{IoU}$, CER).
> - L'OCR se mesure par le **CER** (distance de Levenshtein) ; le prétraitement doit être **testé**, car il peut dégrader la lecture.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercice 1.11.


## 1.6 ➕ Pour aller plus loin : deep learning pour données tabulaires et séries temporelles

> 🧭 Section optionnelle. Elle répond à une question que vous vous poserez : « puisque le deep learning est si puissant, pourquoi garder le boosting pour mes tableaux ? »

### 1.6.1 Pourquoi les tableaux sont un terrain difficile pour les réseaux

Les images, les sons et les textes ont une **structure** que les réseaux exploitent : voisinage des pixels, ordre des mots. Un tableau de clients n'en a pas : la colonne « âge » n'a pas de voisinage avec la colonne « ville », les colonnes sont de natures différentes (des montants, des comptes, des catégories), souvent **asymétriques** (quelques clients dépensent énormément) avec des valeurs manquantes. Les arbres de décision s'en accommodent naturellement (volume III, section 2.4.6) : un seuil sur une variable asymétrique ne dépend pas de son échelle, une catégorie se coupe en groupes. Un réseau demande de **préparer** chaque colonne (standardiser, imputer, encoder), et il est sensible aux variables inutiles.

Cela ne signifie pas que le réseau soit inutilisable : on sait lui donner des **plongements** (*embeddings*) pour les variables catégorielles.

### 1.6.2 Les plongements pour les catégories

Encoder une ville par des colonnes 0/1 (*one-hot*) crée autant de colonnes que de villes. Un **plongement** associe à chaque modalité un **petit vecteur de nombres appris** (par exemple 4 valeurs), exactement comme les poids d'une couche : deux villes aux comportements proches finissent avec des vecteurs proches. C'est l'idée qui, appliquée aux mots, sera au cœur du chapitre 2.

Le modèle ci-dessous combine un plongement par colonne catégorielle et les variables numériques standardisées, puis deux couches denses :

```python
class ReseauTabulaire(nn.Module):
    def __init__(self, nb_modalites, nb_num):
        super().__init__()
        self.plong = nn.ModuleList([nn.Embedding(n, min(8, n)) for n in nb_modalites])   # un vecteur par modalité
        entree = sum(min(8, n) for n in nb_modalites) + nb_num
        self.dense = nn.Sequential(nn.Linear(entree, 64), nn.ReLU(), nn.Dropout(0.2), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x_num, x_cat):
        vecteurs = [e(x_cat[:, i]) for i, e in enumerate(self.plong)]
        return self.dense(torch.cat(vecteurs + [x_num], dim=1)).squeeze(1)       # score de résiliation (logit)
```

### 1.6.3 Le match : régression logistique, réseau, boosting

Nous reprenons le jeu `clients_ml.csv` du volume III : prédire la **résiliation à 90 jours** de 12 000 clients. Trois colonnes sont **écartées** : `commandes_apres_cible` et `depense_6m` contiennent l'avenir (une fuite de cible : volume III, section 1.1.6), et `segment_vrai` est la vérité cachée de la simulation. Les valeurs manquantes sont remplacées par la médiane de l'**entraînement** (avec un indicateur « manquant »), les variables numériques standardisées, et les quatre variables catégorielles reçoivent un plongement (ou, pour la régression logistique, un encodage 0/1).

La comparaison utilise la **validation croisée à 5 plis répétée 2 fois** (10 évaluations, mêmes plis pour les trois modèles) et l'**AUC**, la mesure du volume III (section 5.1.4). Le boosting est le `HistGradientBoosting` de scikit-learn, avec ses réglages par défaut : on compare un réseau **raisonnable** à un boosting **non réglé**, pas un réseau au meilleur de ses concurrents.


| Modèle | AUC moyenne (10 évaluations) | Écart-type entre évaluations |
|---|---|---|
| Régression logistique | 0,8627 | 0,0119 |
| Réseau à plongements | 0,8694 | 0,0095 |
| Boosting (`HistGradientBoosting`, réglages par défaut) | 0,8959 | 0,0083 |

La comparaison est **appariée** : les trois modèles voient les mêmes plis, et l'on compare leurs écarts pli par pli. Comme les jeux d'entraînement de la validation croisée se recouvrent, le test $t$ ordinaire serait trop optimiste ; nous utilisons la correction de Nadeau et Bengio (volume III, section 1.4.2), dans sa forme approchée pour la validation croisée répétée (rapport des tailles test/entraînement égal à $1/4$).

| Écart d'AUC | Écart moyen | $p$ (test $t$ corrigé) |
|---|---|---|
| Boosting − réseau | 0,0265 | $2{,}0\times10^{-5}$ |
| Boosting − régression logistique | 0,0332 | $1{,}5\times10^{-5}$ |
| Réseau − régression logistique | 0,0067 | 0,10 |

Le boosting fait mieux que le réseau dans 10 des 10 évaluations, et l'écart d'AUC (0,027) est très supérieur à ce que le hasard des plis explique. En revanche, le réseau ne se distingue pas nettement de la régression logistique ($p\approx0{,}10$) : le plongement et les deux couches n'apportent presque rien sur ces données. Ce n'est pas un hasard de l'exemple : sur des tableaux de taille moyenne, avec des variables hétérogènes et une structure faite surtout de seuils et d'interactions simples, les **arbres boostés restent, en pratique, difficiles à battre**, et ils s'entraînent plus vite et se règlent plus facilement. Le résultat dépend du jeu : sur des jeux immenses, avec beaucoup de catégories à haute cardinalité, ou quand le réseau doit être entraîné **conjointement** avec du texte ou des images, il devient compétitif.

> 💡 **La règle pratique.** Pour un tableau : régression logistique, puis boosting. N'ajoutez un réseau que (a) si le boosting plafonne et que vous avez de grands volumes, (b) si vous combinez le tableau avec d'autres types de données (texte, image), ou (c) si une architecture spécifique le justifie. Et dans tous les cas, **comparez avec la même rigueur** qu'ici.

### 1.6.4 Séries temporelles : au-delà du LSTM

Nous avons vu en 1.3 un LSTM prévoir les ventes. Le champ est plus large, et le message reste le même : **les méthodes classiques sont des adversaires sérieux** (volume II, chapitre 4).

- Des réseaux **conçus pour la prévision** existent : N-BEATS (2019), réseaux **convolutifs temporels**, *Temporal Fusion Transformer*, PatchTST (2023). Ils brillent surtout quand on prévoit **beaucoup de séries à la fois** (des milliers de produits), le modèle partageant ce qu'il apprend entre séries.
- Des **modèles de fondation** pour les séries temporelles, pré-entraînés sur de très grandes collections (par exemple Chronos, TimesFM, 2024), prévoient une série **sans entraînement** sur vos données. Leur apport réel dépend des données et doit être mesuré.
- Plusieurs travaux de comparaison ont montré que de simples modèles linéaires sur la fenêtre des retards égalent ou dépassent des architectures de type *transformer* sur des jeux de référence : la complexité n'achète pas toujours de la précision.

Dans tous les cas, la procédure d'évaluation est celle du volume II (section 4.3.3 : découpage temporel ; section 4.3.4 : références simples), plus une validation à origine glissante quand la série est assez longue (section 4.3.6). **Aucun résultat de cette sous-section n'est exécuté** : ce sont des repères, pas des mesures du livre.

> ✅ **À retenir.**
> - Sur des **tableaux**, la régression logistique et le **boosting** restent les références ; un réseau avec **plongements** peut les égaler, rarement les surpasser, sur des données de taille moyenne.
> - La comparaison se fait **par plis appariés**, avec le test $t$ **corrigé** de Nadeau et Bengio.
> - Un **plongement** est un vecteur de nombres appris pour chaque modalité d'une catégorie.
> - En séries temporelles, commencez par les références classiques ; le deep learning se justifie surtout pour **beaucoup de séries** ou des **données multimodales**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercice 1.12.


## Bilan du chapitre 1

Vous savez maintenant :

- **calculer à la main** un neurone, une couche et une **rétropropagation** complète sur un petit réseau (et vérifier le résultat par la différentiation automatique et par différences finies) ; **compter** les paramètres d'un réseau ;
- **choisir** une activation et une perte selon la sortie voulue (sigmoïde, softmax, linéaire), **reconnaître** les gradients qui disparaissent et y remédier (ReLU, initialisation de He), **régler** un optimiseur (le pas d'apprentissage reste décisif) et **régulariser** (poids, dropout, arrêt précoce) en jugeant sur plusieurs graines ;
- **expliquer** pourquoi un réseau **convolutif** convient aux images (filtres locaux et partagés, pooling, champ réceptif), **suivre les formes** couche par couche, et **augmenter** les données en respectant l'étiquette ;
- **expliquer** un réseau **récurrent**, la disparition du gradient dans le temps, les **portes** d'un LSTM (avec un pas calculé à la main), et **prévoir** une série en la comparant à un naïf saisonnier et à un boosting à retards, avec un découpage temporel ;
- (en option) **écrire** une boucle d'entraînement PyTorch, fixer les graines, sauvegarder un modèle ; **réutiliser** un réseau pré-entraîné ; **mesurer** une lecture OCR par le taux d'erreur par caractère ; **comparer** un réseau à un boosting sur un tableau avec un test apparié corrigé.

Le tableau suivant résume **ce que nous avons mesuré**, et pas ce que l'on lit dans les articles enthousiastes :

| Problème | Référence simple | Réseau | Verdict mesuré |
|---|---|---|---|
| Chiffres MNIST (8 000 images) | boosting : 95,0 % | réseau dense : 94,5 % ; **réseau convolutif : 96,2 %** | le convolutif fait un peu mieux, avec 5 258 paramètres contre 109 386 |
| Chiffres décalés de 3 pixels | — | convolutif : 72,2 % ; dense : 49,0 % | le convolutif est plus tolérant, sans être invariant |
| Ventes quotidiennes | naïf saisonnier : 27,86 € ; boosting : 21,76 € | LSTM : 20,50 € | le LSTM gagne, sur des données simulées régulières ; plancher de bruit : 17,55 € |
| Résiliation de clients (AUC) | boosting : 0,8959 | réseau : 0,8694 | le boosting fait mieux |
| Chiffres, 2 000 images | régression sur pixels : 87,2 % | ResNet gelé : 92,5 % ; petit CNN : 94,3 % | le transfert aide, mais n'égale pas un petit CNN adapté |

Le fil conducteur du chapitre tient en une phrase : **le deep learning est la bonne réponse quand les données ont une structure** (pixels voisins, suites ordonnées) que l'architecture sait exploiter, et pas nécessairement ailleurs. Dans tous les cas, **la discipline du volume III reste la même** : une référence à battre, un découpage honnête, plusieurs graines, une incertitude annoncée.

Le chapitre 2 aborde le **texte** : comment un réseau représente les mots par des plongements (l'idée vue en 1.6), le mécanisme d'**attention** et les modèles de langage ; le chapitre 4 reprend l'**export** et la **mise en production** d'un modèle comme ceux de ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rétropropagation en `numpy`, optimiseurs, régularisation, convolution à la main, augmentation de données, LSTM contre GRU, OCR de factures inclinées, réseau contre boosting selon la taille des données) et exercices 1.1 à 1.12.
