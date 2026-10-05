# Chapitre 1 : Régression linéaire

> « Tous les modèles sont faux, mais certains sont utiles. »
> — George Box

Au volume I, vous avez appris à **décrire** des données (chapitre 3 : moyennes, corrélations) et à **comparer** des groupes (tests de Student, de Welch). Mais la gérante pose rarement des questions aussi simples. Elle demande plutôt :

- « **Combien** dépense un client de plus de 50 ans acquis par Réseaux, *par rapport à* un client de 30 ans acquis en boutique ? »
- « Quand je dis que les clients Réseaux dépensent moins, est-ce vraiment le **canal**, ou est-ce parce qu'ils sont plus jeunes ? »
- « Si je ne connais que l'âge et le canal d'un nouveau client, **quel panier** puis-je prévoir ? Avec quelle marge d'erreur ? »

Pour répondre, il faut un outil qui relie **une quantité à expliquer** à **plusieurs variables explicatives en même temps**, qui mesure l'effet de chacune *toutes choses égales par ailleurs*, et qui dit honnêtement quelle confiance accorder aux chiffres. Cet outil est la **régression linéaire**, le cheval de trait de la statistique appliquée : il sert tous les jours, il est au cœur de modèles plus sophistiqués (chapitres suivants et volume III), et le comprendre à fond rend tout le reste plus facile.

## Le chemin de ce chapitre

- **1.1 Le modèle linéaire et les moindres carrés** : écrire le modèle, calculer les coefficients (à la main, puis en code), comprendre pourquoi la solution est la bonne (projection, théorème de Gauss-Markov), interpréter les coefficients, y compris avec des variables qualitatives et des transformations logarithmiques.
- **1.2 Inférence sur les coefficients** : erreurs standard, tests $t$ et $F$, intervalles de confiance et intervalles de prédiction : que peut-on conclure, et avec quelle incertitude ?
- **1.3 Diagnostics** : vérifier que le modèle n'est pas faux de façon grave : résidus, effet de levier, observations influentes, multicolinéarité.
- **1.4 Sélection de variables et comparaison de modèles** : quelles variables garder ? Surapprentissage, critères AIC/BIC, validation croisée, et les pièges de la sélection automatique.
- ➕ **Pour aller plus loin** : la **régularisation** (Ridge, Lasso, Elastic Net, 1.5), la **régression robuste** (1.6), et les **modèles à effets mixtes** pour les données groupées (1.7).
- **Bilan du chapitre**, puis, dans le **cahier**, les applications guidées et les exercices corrigés du chapitre 1.

> 💡 **Le fil conducteur : le panier des clients de la boutique.** Nous travaillons sur **2 000 clients** de la boutique, observés sur une année (âge, canal d'acquisition, ville, dépenses, etc.) et, pour certains, leur réponse à un petit questionnaire de satisfaction. Ces données sont **simulées** (graine fixe) : ainsi, nous connaissons la vérité, et nous pourrons à la fin de l'étude **vérifier** que la méthode la retrouve. C'est un luxe que la vie réelle n'offre jamais, et il rend très instructif l'examen de ce que la régression fait bien… ou moins bien.

> 📦 **Les fichiers de données.** Ce chapitre lit `donnees/clients.csv` (un client par ligne) et, à partir de 1.4, `donnees/enquete_satisfaction.csv` (réponses à huit questions de satisfaction). Au 1.7, un petit jeu supplémentaire (`donnees/ch01-relais.csv`, 30 points relais) est simulé avec une graine fixe : le fichier est fourni.

> 💡 **Outils, et place du code.** Nous utilisons `statsmodels` (le module de référence pour les modèles statistiques en Python : tableaux de résultats, tests, diagnostics), `numpy` (pour recalculer à la main), `scikit-learn` (pour la régularisation) et `matplotlib`. Quelques calculs en R (`lm`, `lme4`) ont servi à vérifier que l'on obtient exactement les mêmes nombres dans l'autre grand langage de la statistique (section 4.2 du volume I). Dans ce livre, le code n'apparaît que lorsqu'il montre **comment utiliser un outil** : les vérifications numériques, les simulations et les figures sont produites par du code caché (mais exécuté, donc reproductible : il est dans les sources du dépôt) et leurs résultats sont cités dans le texte. Les applications complètes, pas à pas, sont dans le **cahier** du volume.

> 🧭 **Notations.** Nous écrivons les vecteurs en gras minuscule ($\mathbf y$, $\boldsymbol\beta$), les matrices en gras majuscule ($\mathbf X$), $n$ pour le nombre d'observations et $p$ pour le nombre de **colonnes** de $\mathbf X$ (constante comprise). Si l'algèbre linéaire vous semble lointaine, relisez les sections 1.1.2 (matrices) et 1.1.3 (valeurs propres) du volume I ; pour la minimisation d'une fonction, le chapitre 1.3 du même volume.


## 1.1 Le modèle linéaire et les moindres carrés

> 💡 **Intuition.** Vous avez un nuage de points et vous voulez y poser **la droite qui colle le mieux**. Mais « le mieux » est vague : on peut passer par certains points et en rater d'autres. Le critère des **moindres carrés** tranche : on mesure l'écart vertical entre chaque point et la droite, on **élève chaque écart au carré** (pour que les écarts positifs et négatifs ne s'annulent pas, et pour punir plus sévèrement les gros écarts), on additionne, et on choisit la droite qui rend cette somme **la plus petite possible**. Tout ce chapitre est l'étude de cette idée, avec une ou plusieurs variables explicatives.

### 1.1.1 Un exemple minuscule, entièrement à la main

La gérante a noté, pour quatre commandes, le **nombre d'articles** et le **montant total** en € :

| Commande | Articles $x$ | Montant $y$ (€) |
|---|---|---|
| A | 1 | 22 |
| B | 2 | 41 |
| C | 3 | 66 |
| D | 4 | 79 |

Elle cherche une droite $y=\beta_0+\beta_1x$ : $\beta_0$ serait un coût fixe (emballage, livraison) et $\beta_1$ le prix moyen d'un article supplémentaire. Chaque commande donne une équation, que l'on empile en **écriture matricielle** (volume I, section 1.1.2) :

$$\underbrace{\begin{pmatrix}22\\41\\66\\79\end{pmatrix}}_{\mathbf y}\;\approx\;\underbrace{\begin{pmatrix}1&1\\1&2\\1&3\\1&4\end{pmatrix}}_{\mathbf X}\underbrace{\begin{pmatrix}\beta_0\\\beta_1\end{pmatrix}}_{\boldsymbol\beta}$$

La première colonne de $\mathbf X$ ne contient que des 1 : elle sert à porter la constante $\beta_0$. Nous démontrerons plus loin (1.1.3) que la meilleure droite au sens des moindres carrés est donnée par la formule

$$\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y .$$

Calculons-la à la main. D'abord les deux produits matriciels :

$$\mathbf X^\top\mathbf X=\begin{pmatrix}4&10\\10&30\end{pmatrix},\qquad \mathbf X^\top\mathbf y=\begin{pmatrix}22+41+66+79\\ 22\cdot1+41\cdot2+66\cdot3+79\cdot4\end{pmatrix}=\begin{pmatrix}208\\618\end{pmatrix}.$$

Le déterminant de $\mathbf X^\top\mathbf X$ vaut $4\times30-10\times10=20$, donc l'inverse d'une matrice $2\times2$ s'obtient en échangeant les termes de la diagonale, en changeant le signe des deux autres et en divisant par le déterminant :

$$(\mathbf X^\top\mathbf X)^{-1}=\frac1{20}\begin{pmatrix}30&-10\\-10&4\end{pmatrix},\qquad
\hat{\boldsymbol\beta}=\frac1{20}\begin{pmatrix}30\cdot208-10\cdot618\\-10\cdot208+4\cdot618\end{pmatrix}=\frac1{20}\begin{pmatrix}60\\392\end{pmatrix}=\begin{pmatrix}3\\19{,}6\end{pmatrix}.$$

La meilleure droite est donc $\hat y=3+19{,}6\,x$ : un coût fixe de 3 € et 19,60 € par article. Les valeurs ajustées sont $22{,}6;\ 42{,}2;\ 61{,}8;\ 81{,}4$, et les **résidus** (écarts entre le réel et l'ajusté) valent $-0{,}6;\ -1{,}2;\ +4{,}2;\ -2{,}4$. Leur somme est nulle, et la somme de leurs carrés vaut $0{,}36+1{,}44+17{,}64+5{,}76=25{,}2$. Un calcul sur ordinateur confirme ces valeurs.


En pratique, un logiciel ne calcule pas l'inverse de $\mathbf X^\top\mathbf X$ : il **résout** le système $\mathbf X^\top\mathbf X\,\boldsymbol\beta=\mathbf X^\top\mathbf y$, ce qui est plus rapide et surtout **plus précis** (c'est la leçon de la section 1.5.4 du volume I sur le conditionnement). Voyons le résultat en image.


![Quatre commandes, la droite des moindres carrés et les résidus (segments verticaux). La droite est celle qui minimise la somme des carrés de ces segments.](figures/ch01-droite-4-points.png)

> 🧪 **Deux propriétés à remarquer.** (1) La somme des résidus est nulle (aux erreurs d'arrondi près). (2) Le produit $\mathbf X^\top\mathbf e$ est nul : les résidus sont *orthogonaux* à chaque colonne de $\mathbf X$. Nous les démontrons en 1.1.3 et 1.1.4, et elles joueront un rôle central.


### 1.1.2 Le modèle linéaire : ce que l'on suppose

Passons de quatre points à un vrai modèle statistique. On observe $n$ individus. Pour l'individu $i$, une variable à expliquer $y_i$ (la **réponse**) et $p-1$ variables explicatives $x_{i1},\dots,x_{i,p-1}$ (les **prédicteurs**, ou *covariables*). Le **modèle de régression linéaire** postule

$$y_i=\beta_0+\beta_1x_{i1}+\dots+\beta_{p-1}x_{i,p-1}+\varepsilon_i,\qquad\text{soit}\qquad \mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon .$$

Ici $\mathbf X$ est la **matrice de plan d'expérience** (en anglais *design matrix*), de taille $n\times p$ (première colonne de 1), $\boldsymbol\beta$ le vecteur des $p$ coefficients inconnus, et $\boldsymbol\varepsilon$ le vecteur des **erreurs** : tout ce que le modèle n'explique pas (variables oubliées, hasard, erreurs de mesure). Les erreurs ne sont jamais observées ; ce que l'on calcule, ce sont des **résidus** $\hat\varepsilon_i=y_i-\hat y_i$, qui en sont une approximation.

Pour que les formules qui suivent aient un sens statistique, on fait des **hypothèses**. Nous les numérotons, car nous y reviendrons tout le chapitre :

| | Hypothèse | Ce qu'elle dit | Ce dont elle sert |
|---|---|---|---|
| **H1** | **Linéarité** | $\mathbb E[y_i\mid x_i]$ est une combinaison linéaire des **paramètres** $\beta_j$ | l'espérance de $\mathbf y$ est $\mathbf X\boldsymbol\beta$ |
| **H2** | **Rang plein** | les colonnes de $\mathbf X$ sont linéairement indépendantes ($\operatorname{rang}\mathbf X=p$, donc $n\ge p$) | $\mathbf X^\top\mathbf X$ est inversible : $\hat{\boldsymbol\beta}$ existe et est unique |
| **H3** | **Exogénéité** | $\mathbb E[\boldsymbol\varepsilon\mid\mathbf X]=\mathbf 0$ : les erreurs sont « neutres » vis-à-vis des prédicteurs | $\hat{\boldsymbol\beta}$ est **sans biais** |
| **H4** | **Erreurs sphériques** | $\operatorname{Var}(\boldsymbol\varepsilon\mid\mathbf X)=\sigma^2\mathbf I_n$ : variance **constante** (homoscédasticité) et erreurs **non corrélées** | formule de la variance de $\hat{\boldsymbol\beta}$, théorème de Gauss-Markov |
| **H5** | **Normalité** | $\boldsymbol\varepsilon\sim\mathcal N(\mathbf 0,\sigma^2\mathbf I_n)$ | tests $t$ et $F$ **exacts**, intervalles de confiance |

> ⚠️ **« Linéaire » veut dire linéaire dans les paramètres, pas dans les variables.** Le modèle $y=\beta_0+\beta_1x+\beta_2x^2+\varepsilon$ est un modèle linéaire (c'est une combinaison linéaire de $\beta_0,\beta_1,\beta_2$ ; la colonne $x^2$ est simplement une colonne de plus dans $\mathbf X$). De même $\log y=\beta_0+\beta_1\log x+\varepsilon$. En revanche, $y=\beta_0e^{\beta_1x}+\varepsilon$ n'est pas linéaire : $\beta_1$ apparaît dans l'exponentielle. C'est ce qui permet à la régression linéaire d'ajuster des courbes, et pas seulement des droites.

> 💡 **Le rôle de chaque hypothèse.** On ne les exige pas toutes pour toutes les conclusions. H1 à H3 suffisent à garantir que les coefficients visent juste en moyenne (absence de biais). Il faut H4 en plus pour savoir **quelle précision** on atteint et pour comparer les estimateurs (Gauss-Markov). Il faut H5 pour obtenir des tests et des intervalles de confiance exacts avec $n$ petit (pour $n$ grand, le théorème central limite, volume I section 2.4.3, atténue l'importance de H5). La section 1.3 apprendra à **vérifier** ces hypothèses.

### 1.1.3 Les équations normales : démonstration

**Objectif.** Trouver le vecteur $\boldsymbol\beta$ qui minimise la somme des carrés des résidus

$$S(\boldsymbol\beta)=\|\mathbf y-\mathbf X\boldsymbol\beta\|^2=(\mathbf y-\mathbf X\boldsymbol\beta)^\top(\mathbf y-\mathbf X\boldsymbol\beta).$$

> 📐 **Démonstration.** Développons le produit (en rappelant que $\boldsymbol\beta^\top\mathbf X^\top\mathbf y$ est un nombre, donc égal à sa transposée $\mathbf y^\top\mathbf X\boldsymbol\beta$) :
> $$S(\boldsymbol\beta)=\mathbf y^\top\mathbf y-2\,\boldsymbol\beta^\top\mathbf X^\top\mathbf y+\boldsymbol\beta^\top\mathbf X^\top\mathbf X\boldsymbol\beta .$$
> **Gradient** (volume I, section 1.2.2) : les règles $\nabla_{\boldsymbol\beta}(\mathbf a^\top\boldsymbol\beta)=\mathbf a$ et $\nabla_{\boldsymbol\beta}(\boldsymbol\beta^\top\mathbf A\boldsymbol\beta)=2\mathbf A\boldsymbol\beta$ (pour $\mathbf A$ symétrique) donnent
> $$\nabla S(\boldsymbol\beta)=-2\,\mathbf X^\top\mathbf y+2\,\mathbf X^\top\mathbf X\,\boldsymbol\beta .$$
> En un minimum, le gradient s'annule, d'où les **équations normales** :
> $$\boxed{\;\mathbf X^\top\mathbf X\,\hat{\boldsymbol\beta}=\mathbf X^\top\mathbf y\;}$$
> **C'est bien un minimum, et il est unique.** La matrice hessienne de $S$ est $2\mathbf X^\top\mathbf X$. Pour tout vecteur $\mathbf v\neq\mathbf 0$, $\mathbf v^\top\mathbf X^\top\mathbf X\mathbf v=\|\mathbf X\mathbf v\|^2\ge0$, et cette quantité est **strictement positive** si $\mathbf X\mathbf v\neq\mathbf 0$, ce qui est garanti par H2 (colonnes indépendantes). Donc le hessien est définie positive : $S$ est **strictement convexe** (volume I, section 1.3.2), elle possède un unique point critique, et c'est son minimum global. Sous H2, $\mathbf X^\top\mathbf X$ est inversible et $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y$. $\square$

Deux conséquences immédiates. La $j$-ième équation normale s'écrit $\mathbf x_j^\top(\mathbf y-\mathbf X\hat{\boldsymbol\beta})=0$, soit

$$\mathbf X^\top\hat{\boldsymbol\varepsilon}=\mathbf 0 :$$

**les résidus sont orthogonaux à chaque colonne de $\mathbf X$**. En particulier, comme la première colonne est faite de 1, $\sum_i\hat\varepsilon_i=0$ : *tant que le modèle contient une constante*, les résidus sont de somme nulle. Nous avions constaté ces deux faits au 1.1.1.

**Une autre route vers la même solution : la descente de gradient.** Au volume I (section 1.3.3), nous avons appris à descendre une pente pas à pas. La fonction à minimiser ici est $S$, de gradient $-2\mathbf X^\top(\mathbf y-\mathbf X\boldsymbol\beta)$ : en la descendant (après avoir **centré** $x$, ce qui accélère la convergence), on retrouve la même solution, $(3\,;\,19{,}6)$ pour nos quatre commandes, en quelques dizaines de pas (cahier, application 1.1).


En pratique, les logiciels n'utilisent ni l'inverse ni la descente de gradient pour la régression linéaire classique, mais une **factorisation QR** de $\mathbf X$ (ou une SVD, volume I section 1.1.4), numériquement bien plus stable. La descente de gradient reprend tout son intérêt avec les très grands jeux de données et avec les modèles qui n'ont pas de formule fermée : la régression logistique du chapitre 2, par exemple, s'ajuste par un algorithme itératif de la même famille.

### 1.1.4 La géométrie des moindres carrés : une projection

Les équations normales cachent une image géométrique très puissante. Voyons les $n$ observations $\mathbf y$ comme **un seul point** (un vecteur) de l'espace $\mathbb R^n$. Les colonnes de $\mathbf X$ engendrent un sous-espace de dimension $p$ (ici, un plan si $p=2$). Les valeurs $\mathbf X\boldsymbol\beta$ que le modèle peut produire sont exactement les points de ce sous-espace. Chercher $\boldsymbol\beta$ qui minimise $\|\mathbf y-\mathbf X\boldsymbol\beta\|$, c'est **chercher le point du sous-espace le plus proche de $\mathbf y$**, et la géométrie nous dit que c'est le **projeté orthogonal** de $\mathbf y$ sur ce sous-espace.


![Les moindres carrés comme projection : ŷ est le point du sous-espace le plus proche de y, et le résidu est perpendiculaire au sous-espace.](figures/ch01-projection.png)

> 📐 **La matrice chapeau.** Comme $\hat{\mathbf y}=\mathbf X\hat{\boldsymbol\beta}=\mathbf X(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y$, on a $\hat{\mathbf y}=\mathbf H\mathbf y$ avec
> $$\mathbf H=\mathbf X(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\qquad(\text{« la matrice chapeau »}, \text{ car elle met un chapeau sur }\mathbf y).$$
> Elle est **symétrique** ($\mathbf H^\top=\mathbf H$, car $(\mathbf X^\top\mathbf X)^{-1}$ est symétrique) et **idempotente** :
> $$\mathbf H^2=\mathbf X(\mathbf X^\top\mathbf X)^{-1}\underbrace{\mathbf X^\top\mathbf X(\mathbf X^\top\mathbf X)^{-1}}_{=\mathbf I}\mathbf X^\top=\mathbf H .$$
> Cela caractérise un **projecteur orthogonal** : projeter deux fois revient à projeter une fois. Le résidu est $\hat{\boldsymbol\varepsilon}=\mathbf y-\mathbf H\mathbf y=(\mathbf I-\mathbf H)\mathbf y$, et $\mathbf I-\mathbf H$ est le projecteur sur le sous-espace **orthogonal**. Enfin, la trace d'un projecteur est la dimension de son image :
> $$\operatorname{tr}(\mathbf H)=p,\qquad\operatorname{tr}(\mathbf I-\mathbf H)=n-p .$$
> (En effet $\operatorname{tr}(\mathbf X(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top)=\operatorname{tr}((\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf X)=\operatorname{tr}(\mathbf I_p)=p$, car la trace est invariante par permutation circulaire.)
> **Pythagore** s'applique alors : $\|\mathbf y\|^2=\|\hat{\mathbf y}\|^2+\|\hat{\boldsymbol\varepsilon}\|^2$.

Sur nos quatre commandes, un calcul sur ordinateur donne la matrice

$$\mathbf H\approx\begin{pmatrix}0{,}7&0{,}4&0{,}1&-0{,}2\\0{,}4&0{,}3&0{,}2&0{,}1\\0{,}1&0{,}2&0{,}3&0{,}4\\-0{,}2&0{,}1&0{,}4&0{,}7\end{pmatrix},$$

qui est bien symétrique, idempotente, de trace $2=p$, et qui vérifie $\mathbf H\mathbf y=\hat{\mathbf y}$ ainsi que Pythagore : $\|\mathbf y\|^2=12\,762=\|\hat{\mathbf y}\|^2+\|\hat{\boldsymbol\varepsilon}\|^2$.


Les éléments diagonaux de $\mathbf H$, notés $h_{ii}$ (ici $0{,}7;\,0{,}3;\,0{,}3;\,0{,}7$, de somme $2=p$), mesurent « l'influence » de chaque observation sur sa propre valeur ajustée : nous les retrouverons en 1.3 sous le nom d'**effet de levier**. On voit déjà que les commandes extrêmes (A et D, avec 1 et 4 articles) ont plus de levier que celles du milieu.

### 1.1.5 Propriétés statistiques : sans biais, variance, et le théorème de Gauss-Markov

Les données sont un échantillon : un autre échantillon donnerait d'autres résidus, donc un autre $\hat{\boldsymbol\beta}$. L'estimateur $\hat{\boldsymbol\beta}$ est donc une **variable aléatoire** (volume I, section 3.2.1). Quelles sont ses propriétés ?

> 📐 **Théorème 1 (espérance et variance de $\hat{\boldsymbol\beta}$).** Sous H1 à H4,
> $$\mathbb E[\hat{\boldsymbol\beta}]=\boldsymbol\beta,\qquad\operatorname{Var}(\hat{\boldsymbol\beta})=\sigma^2(\mathbf X^\top\mathbf X)^{-1}.$$
> *Démonstration.* En posant $\mathbf A=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top$, on a $\hat{\boldsymbol\beta}=\mathbf A\mathbf y=\mathbf A(\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon)=\boldsymbol\beta+\mathbf A\boldsymbol\varepsilon$, car $\mathbf A\mathbf X=\mathbf I_p$. Donc $\mathbb E[\hat{\boldsymbol\beta}]=\boldsymbol\beta+\mathbf A\,\mathbb E[\boldsymbol\varepsilon]=\boldsymbol\beta$ (H3). Et $\operatorname{Var}(\hat{\boldsymbol\beta})=\mathbf A\operatorname{Var}(\boldsymbol\varepsilon)\mathbf A^\top=\sigma^2\mathbf A\mathbf A^\top=\sigma^2(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf X(\mathbf X^\top\mathbf X)^{-1}=\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ (H4). $\square$

Regardons ce que dit la formule de variance : la précision de $\hat\beta_j$ s'améliore quand $\sigma^2$ est petit (peu de bruit), quand $n$ est grand ($\mathbf X^\top\mathbf X$ croît avec $n$) et quand les valeurs de $x_j$ sont **bien étalées** (si tous les clients avaient le même âge, on ne pourrait pas estimer l'effet de l'âge). C'est une information précieuse pour **concevoir** une étude.

> 📐 **Théorème 2 (Gauss-Markov).** Sous H1 à H4, $\hat{\boldsymbol\beta}$ est le **meilleur estimateur linéaire sans biais** (en anglais **BLUE**, *Best Linear Unbiased Estimator*) : pour tout autre estimateur $\tilde{\boldsymbol\beta}=\mathbf C\mathbf y$ linéaire en $\mathbf y$ et sans biais, $\operatorname{Var}(\tilde{\boldsymbol\beta})-\operatorname{Var}(\hat{\boldsymbol\beta})$ est une matrice semi-définie positive. En particulier, pour toute combinaison $\mathbf c^\top\boldsymbol\beta$, la variance de $\mathbf c^\top\hat{\boldsymbol\beta}$ est la plus petite possible.
> *Démonstration.* Écrivons $\mathbf C=\mathbf A+\mathbf D$, où $\mathbf A=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top$ et $\mathbf D$ est une matrice $p\times n$. L'absence de biais exige $\mathbb E[\mathbf C\mathbf y]=\mathbf C\mathbf X\boldsymbol\beta=\boldsymbol\beta$ pour tout $\boldsymbol\beta$, donc $\mathbf C\mathbf X=\mathbf I$, c'est-à-dire $\mathbf D\mathbf X=\mathbf 0$ (puisque $\mathbf A\mathbf X=\mathbf I$). Alors
> $$\operatorname{Var}(\tilde{\boldsymbol\beta})=\sigma^2\mathbf C\mathbf C^\top=\sigma^2(\mathbf A+\mathbf D)(\mathbf A+\mathbf D)^\top=\sigma^2\big(\mathbf A\mathbf A^\top+\mathbf A\mathbf D^\top+\mathbf D\mathbf A^\top+\mathbf D\mathbf D^\top\big).$$
> Or $\mathbf D\mathbf A^\top=\mathbf D\mathbf X(\mathbf X^\top\mathbf X)^{-1}=\mathbf 0$, et sa transposée $\mathbf A\mathbf D^\top$ aussi. Il reste $\operatorname{Var}(\tilde{\boldsymbol\beta})=\sigma^2(\mathbf X^\top\mathbf X)^{-1}+\sigma^2\mathbf D\mathbf D^\top$, et $\mathbf D\mathbf D^\top$ est semi-définie positive (pour tout $\mathbf v$, $\mathbf v^\top\mathbf D\mathbf D^\top\mathbf v=\|\mathbf D^\top\mathbf v\|^2\ge0$). $\square$

Ce théorème est remarquable par ce qu'il **ne demande pas** : aucune hypothèse de normalité. Mais il a aussi des limites, qu'il faut garder en tête : il ne compare que des estimateurs **linéaires et sans biais**. Un estimateur *biaisé* (comme la régression Ridge, section 1.5) peut avoir une erreur quadratique moyenne plus petite. Et si H4 est fausse (variance non constante), $\hat{\boldsymbol\beta}$ reste sans biais mais n'est plus le meilleur.

**Estimer la variance du bruit.** La formule de $\operatorname{Var}(\hat{\boldsymbol\beta})$ contient $\sigma^2$, inconnue. On l'estime par

$$s^2=\frac{\text{SCR}}{n-p}=\frac{\sum_i\hat\varepsilon_i^2}{n-p}.$$

> 📐 **Pourquoi $n-p$ ?** (c'est la généralisation de la division par $n-1$ du volume I, section 3.2.3). Le résidu s'écrit $\hat{\boldsymbol\varepsilon}=(\mathbf I-\mathbf H)\mathbf y=(\mathbf I-\mathbf H)(\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon)=(\mathbf I-\mathbf H)\boldsymbol\varepsilon$, car $(\mathbf I-\mathbf H)\mathbf X=\mathbf 0$. Donc $\text{SCR}=\boldsymbol\varepsilon^\top(\mathbf I-\mathbf H)\boldsymbol\varepsilon$ (projecteur symétrique idempotent) et
> $$\mathbb E[\text{SCR}]=\mathbb E\big[\operatorname{tr}\big(\boldsymbol\varepsilon^\top(\mathbf I-\mathbf H)\boldsymbol\varepsilon\big)\big]=\operatorname{tr}\big((\mathbf I-\mathbf H)\,\mathbb E[\boldsymbol\varepsilon\boldsymbol\varepsilon^\top]\big)=\sigma^2\operatorname{tr}(\mathbf I-\mathbf H)=\sigma^2(n-p).$$
> Intuitivement : les résidus sont plus petits que les vraies erreurs, parce que le modèle a *utilisé* $p$ degrés de liberté pour s'ajuster aux données. Diviser par $n-p$ compense exactement ce « trop bon ajustement ».

**Voyons-le en simulation.** Nous connaissons la vérité dans une simulation : prenons les quatre valeurs de $x$ ci-dessus, $\boldsymbol\beta=(3,\,20)$ et $\sigma=3$, fabriquons 20 000 échantillons de quatre montants, et ajustons la droite à chacun. On compare les moyennes et la variance **observées** des estimateurs aux formules du théorème :


Les moyennes des $\hat\beta_j$ (2,978 et 20,003) sont proches des vraies valeurs (3 et 20 : absence de biais) ; les variances observées (13,18 et 1,77) et la covariance (−4,41) sont très proches de celles de $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ (13,5 ; 1,8 et −4,5) ; et la division par $n-p$ donne une estimation centrée de $\sigma^2$ (9,07 en moyenne, pour une vraie valeur de 9) alors que la division par $n$ la sous-estime d'un facteur $(n-p)/n=1/2$ (4,54). La théorie est confirmée par l'expérience.

### 1.1.6 Décomposition de la variance et coefficient de détermination $R^2$

Combien le modèle explique-t-il ? Mesurons la dispersion de $\mathbf y$ autour de sa moyenne par la **somme des carrés totale** $\text{SCT}=\sum_i(y_i-\bar y)^2$. La régression la décompose en une partie expliquée et une partie résiduelle.

> 📐 **Théorème (décomposition de la variance).** Si le modèle contient une constante, alors
> $$\underbrace{\sum_i(y_i-\bar y)^2}_{\text{SCT}}=\underbrace{\sum_i(\hat y_i-\bar y)^2}_{\text{SCE (expliquée)}}+\underbrace{\sum_i\hat\varepsilon_i^2}_{\text{SCR (résiduelle)}}.$$
> *Démonstration.* Écrivons $y_i-\bar y=(\hat y_i-\bar y)+\hat\varepsilon_i$ et élevons au carré : le double produit vaut $2\sum_i(\hat y_i-\bar y)\hat\varepsilon_i=2\sum_i\hat y_i\hat\varepsilon_i-2\bar y\sum_i\hat\varepsilon_i$. Le premier terme est nul car $\hat{\mathbf y}=\mathbf X\hat{\boldsymbol\beta}$ est orthogonal à $\hat{\boldsymbol\varepsilon}$ (1.1.3), le second car la somme des résidus est nulle (présence de la constante). $\square$

Le **coefficient de détermination** est la part de variance expliquée :

$$R^2=\frac{\text{SCE}}{\text{SCT}}=1-\frac{\text{SCR}}{\text{SCT}}\in[0,1].$$

On peut montrer que $R^2$ est le **carré de la corrélation** entre $\mathbf y$ et $\hat{\mathbf y}$ : en régression simple, c'est donc le carré du coefficient de corrélation de Pearson entre $x$ et $y$ (volume I, section 3.1.7). Pour nos quatre commandes : $\text{SCT}=900+121+196+729=1946$ (les écarts de $y$ à la moyenne 52 sont $-30,-11,14,27$) et $\text{SCR}=25{,}2$, donc $R^2=1-25{,}2/1946\approx0{,}987$.


> ⚠️ **Les limites du $R^2$.** (1) Il **ne peut qu'augmenter** quand on ajoute une variable, même une variable sans rapport : un $R^2$ élevé peut être le signe d'un surajustement. Le **$R^2$ ajusté**, $R^2_{\text{aj}}=1-\dfrac{\text{SCR}/(n-p)}{\text{SCT}/(n-1)}$, corrige ce défaut en comparant des variances *sans biais*. (2) Un $R^2$ faible n'est pas un échec : quand le phénomène est intrinsèquement bruité (le comportement d'achat d'un individu), un $R^2$ de 15 % peut déjà être très informatif sur les **effets moyens**. (3) Un $R^2$ élevé ne prouve ni que le modèle est correct, ni que la relation est causale. Rappelez-vous le quartet d'Anscombe (volume I, section 3.1.7) : quatre jeux très différents donnent la même droite et le même $R^2$. **Dessinez toujours.**

### 1.1.7 Première étude : le panier des clients de la boutique

Passons aux données de la boutique (simulées, rappelons-le) : 2 000 clients. La gérante s'intéresse au **panier moyen** (en €) des clients qui ont commandé au moins une fois dans l'année.


Sur les 2 000 clients, 260 (13 %) n'ont passé aucune commande. Leur panier moyen est égal à 0 par convention : ce 0 ne signifie pas « panier nul » mais « pas de panier ». Nous les **écartons** de cette étude (c'est une décision de périmètre, comme celle du projet du volume I) ; la section 2.6 du chapitre suivant apprendra à traiter ensemble les clients actifs et les autres.


Il reste 1 740 clients actifs. Le panier est nettement **asymétrique** (queue vers les gros paniers ; coefficient d'asymétrie de 1,44), alors que son logarithme est presque symétrique (0,11). Comme au volume I (section 3.1.5), c'est le signe qu'il vaut mieux travailler sur le logarithme : les effets seront alors **multiplicatifs** (un client « 10 % plus dépensier » dépense 10 % de plus, quel que soit son niveau de départ), ce qui est bien plus naturel pour des montants.


![Le panier moyen est asymétrique (à gauche) ; son logarithme est presque symétrique (à droite).](figures/ch01-panier-log.png)

**Régression simple.** Commençons par une seule variable : l'âge (centré, pour que la constante ait un sens : elle sera le log-panier d'un client de 36 ans).


Avec `statsmodels`, le modèle s'écrit en une ligne : la formule `log_panier ~ a` se lit « log-panier expliqué par `a` », et la constante est ajoutée automatiquement. Le tableau de résultats donne, pour chaque coefficient, l'estimation, son erreur standard, une statistique $t$, une p-valeur et un intervalle de confiance à 95 % : nous en comprendrons chaque colonne au 1.2. Retenons pour l'instant l'**interprétation** :

- La **constante** vaut environ 4,03 : un client de 36 ans a un log-panier de 4,03, soit un panier typique de $e^{4{,}03}\approx56$ €.
- Le coefficient de **`a`** vaut environ 0,009 : chaque année d'âge supplémentaire est associée à une hausse de **0,9 %** du panier ($\log$ y augmente de 0,009, donc $y$ est multiplié par $e^{0{,}009}\approx1{,}009$).
- Le $R^2$ est faible (environ 5,5 %) : l'âge à lui seul explique peu de choses, ce qui n'a rien de surprenant.

**Variable qualitative : le codage par indicatrices.** Comment faire entrer le **canal** (Boutique/Site/Réseaux), qui n'est pas un nombre ? On le remplace par des **variables indicatrices** (ou *dummies*) : une colonne par modalité *sauf une*, la **modalité de référence**, qui est absorbée par la constante. Avec Boutique pour référence :

| canal | `Site` | `Réseaux` |
|---|---|---|
| Boutique | 0 | 0 |
| Site | 1 | 0 |
| Réseaux | 0 | 1 |

> ⚠️ **Pourquoi pas une colonne par modalité ?** Parce que les trois colonnes s'additionnent exactement à la colonne de 1 de la constante : $\mathbf X$ ne serait plus de rang plein, et $(\mathbf X^\top\mathbf X)^{-1}$ n'existerait pas (violation de H2 : c'est le « piège de la variable indicatrice »). Retirer une colonne règle le problème.

Ajustons maintenant le modèle à l'âge **et** au canal. En code, une seule ligne suffit ; l'écriture `C(canal)` demande à `statsmodels` de traiter `canal` comme qualitative et de fabriquer les indicatrices :

```python
import statsmodels.formula.api as smf

m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()     # df : clients actifs ; a : âge centré
print(m2.params.round(3))
```
<!--sortie-->
```text
Intercept              4.221
C(canal)[T.Site]      -0.157
C(canal)[T.Réseaux]   -0.337
a                      0.009
dtype: float64
```


Voici comment lire chaque coefficient (le tableau complet donne en plus erreurs standard et intervalles ; le $R^2$ est de 16,6 %) :

- **Constante** (≈ 4,22) : le log-panier d'un client de **36 ans acquis en boutique** (modalité de référence, âge à 0 après centrage), soit $e^{4{,}22}\approx68$ €.
- **`C(canal)[T.Site]`** (≈ −0,16) : à âge égal, un client acquis par le site a un log-panier inférieur de 0,16 à celui d'un client de la boutique. En pourcentage : $e^{-0{,}157}\approx0{,}855$, soit un panier **environ 14,5 % plus petit**.
- **`C(canal)[T.Réseaux]`** (≈ −0,34) : $e^{-0{,}34}\approx0{,}71$ : à âge égal, un panier **29 % plus petit** qu'en boutique.
- **`a`** (≈ 0,009) : à canal égal, +0,9 % de panier par année d'âge.

Et le $R^2$ a presque triplé par rapport au modèle précédent (de 5,5 % à 16,6 %). C'est la réponse à la première question de la gérante : *à âge égal*, un client Réseaux dépense environ 29 % de moins qu'un client de la boutique.

> 🧪 **Un détail d'interprétation fréquemment raté.** Les coefficients se lisent **à l'intérieur du modèle**. Le coefficient de l'âge ne dit pas « l'effet de l'âge sur le panier » dans l'absolu, mais « l'effet de l'âge **quand on compare des clients de même canal** ». C'est le sens de l'expression **« toutes choses égales par ailleurs »**. Ici, le coefficient de l'âge change à peine entre `m1` et `m2` car l'âge et le canal sont presque indépendants dans nos données ; s'ils étaient liés (par exemple si Réseaux attirait surtout les jeunes), le coefficient de l'âge dans `m1` mélangerait l'effet de l'âge et l'effet du canal, et il changerait nettement. Ce mélange, c'est la **confusion**.

**Le théorème de Frisch-Waugh-Lovell : « toutes choses égales par ailleurs » rendu concret.** Il existe une manière explicite de retrouver le coefficient de l'âge dans `m2`, qui montre ce que veut dire « tenir compte du canal » :

1. régresser le log-panier sur le **canal** seul et garder les résidus (la partie du log-panier *que le canal n'explique pas*) ;
2. régresser l'âge sur le **canal** seul et garder les résidus (la partie de l'âge *indépendante du canal*) ;
3. régresser les premiers résidus sur les seconds : la pente obtenue est **exactement** le coefficient de l'âge dans le modèle complet.


> 📐 **Pourquoi ça marche (esquisse).** Notons $\mathbf M$ le projecteur sur l'orthogonal des colonnes « canal » (et constante). Par la géométrie du 1.1.4, le coefficient d'une variable $\mathbf a$ dans le modèle $[\text{canal},\mathbf a]$ s'obtient en projetant $\mathbf y$ sur la partie de $\mathbf a$ qui n'est pas dans l'espace engendré par le canal, soit $\mathbf M\mathbf a$ : $\hat\beta_a=(\mathbf M\mathbf a)^\top\mathbf y/\|\mathbf M\mathbf a\|^2$. Comme $\mathbf M$ est symétrique et idempotente, $(\mathbf M\mathbf a)^\top\mathbf y=(\mathbf M\mathbf a)^\top(\mathbf M\mathbf y)$ : c'est la pente de la régression de $\mathbf M\mathbf y$ sur $\mathbf M\mathbf a$.

**Calculer à la main ce que fait `statsmodels`.** Pour boucler la boucle avec les sections précédentes, reconstruisons les coefficients de `m2` par les équations normales à partir de la matrice $\mathbf X$ construite par `statsmodels` :


Les deux colonnes sont identiques : `statsmodels` ne fait rien de magique, il résout les équations normales (en fait, via une factorisation plus stable). Le nombre de conditionnement de $\mathbf X^\top\mathbf X$ (volume I, section 1.5.4) est de l'ordre du millier : cela paraît grand, mais c'est surtout dû au fait que l'âge centré varie de $-18$ à $+37$ alors que les indicatrices valent 0 ou 1 (échelles très différentes). Ce n'est pas de la colinéarité entre variables ; nous apprendrons à la diagnostiquer proprement (VIF) en 1.3.5.

### 1.1.8 Logarithmes : interpréter et prédire

Le choix d'une transformation modifie l'**interprétation** des coefficients. Voici les trois cas les plus courants (où $\beta$ est le coefficient de $x$) :

| Modèle | Lecture du coefficient $\beta$ |
|---|---|
| $y=\beta_0+\beta x$ (niveau-niveau) | +1 unité de $x$ ⇒ $y$ varie de $\beta$ unités |
| $\log y=\beta_0+\beta x$ (log-niveau) | +1 unité de $x$ ⇒ $y$ est multiplié par $e^\beta$, soit une variation de **≈ $100\,\beta$ %** si $\beta$ est petit (exactement $100(e^\beta-1)$ %) |
| $\log y=\beta_0+\beta\log x$ (log-log) | +1 % de $x$ ⇒ $y$ varie d'environ $\beta$ % : $\beta$ est une **élasticité** |

> ⚠️ **« ≈ 100 β % » n'est vrai que pour les petits coefficients.** Pour $\beta=-0{,}34$ (Réseaux), l'approximation donne −34 %, alors que la variation exacte est $100(e^{-0{,}34}-1)\approx-28{,}8$ %. Au-delà de $|\beta|\approx0{,}1$, utilisez toujours $e^\beta-1$.


**Prédire en échelle d'origine : le piège de la rétro-transformation.** Le modèle prédit un **log**-panier. Pour revenir en euros, on pense à prendre l'exponentielle : $\hat y=e^{\hat\mu}$. Mais $e^{\hat\mu}$ est la prédiction de la **médiane** du panier, pas de sa **moyenne**, à cause de l'asymétrie de la loi log-normale.

> 📐 **Rétro-transformation.** Si $\log y\sim\mathcal N(\mu,\sigma^2)$, alors $\mathbb E[y]=e^{\mu+\sigma^2/2}$ (c'est la fonction génératrice des moments de la loi normale : $\mathbb E[e^{Z}]=e^{\mu+\sigma^2/2}$ pour $Z\sim\mathcal N(\mu,\sigma^2)$), alors que la médiane est $e^\mu$. Pour prédire la **moyenne** d'un panier, il faut donc multiplier $e^{\hat\mu}$ par un facteur correctif $e^{s^2/2}$ (ou, sans supposer la normalité, par le facteur « de Duan » $\frac1n\sum_ie^{\hat\varepsilon_i}$).


La moyenne observée est nettement plus proche des prédictions **corrigées** que de $e^{\hat\mu}$ : ignorer la correction conduit à sous-estimer systématiquement le panier moyen (ici de plusieurs euros), ce qui, multiplié par des milliers de clients, devient un manque à gagner dans un budget prévisionnel.

### 1.1.9 Interactions : quand un effet dépend d'un autre

Dans `m2`, l'effet de l'âge est supposé **le même** pour les trois canaux. Mais peut-être que l'âge compte plus chez les clients Réseaux que chez ceux de la boutique ? On le teste en ajoutant une **interaction** : le produit de l'âge par les indicatrices du canal.

```text
=========================================================================================
                            coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                 4.2205      0.017    241.183      0.000       4.186       4.255
C(canal)[T.Site]         -0.1568      0.023     -6.788      0.000      -0.202      -0.112
C(canal)[T.Réseaux]      -0.3366      0.022    -14.961      0.000      -0.381      -0.292
a                         0.0086      0.002      5.115      0.000       0.005       0.012
a:C(canal)[T.Site]        0.0010      0.002      0.463      0.643      -0.003       0.005
a:C(canal)[T.Réseaux]     0.0005      0.002      0.235      0.814      -0.004       0.005
=========================================================================================
```

L'écriture `a * C(canal)` signifie `a + C(canal) + a:C(canal)`. Les deux lignes `a:C(canal)[T.…]` mesurent la **différence de pente** de l'âge entre le canal considéré et la boutique. Si ces coefficients sont proches de zéro (et statistiquement indiscernables de zéro, ce que nous formaliserons par un test $F$ au 1.2.4), le modèle sans interaction suffit. Nous verrons au 1.4 comment choisir objectivement entre `m2` et `m3`.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3 et 1.9.

> ✅ **À retenir (1.1).**
> - Le modèle linéaire s'écrit $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ ; il est linéaire **dans les paramètres**. Les hypothèses H1 à H5 servent chacune à quelque chose de précis.
> - Les **équations normales** $\mathbf X^\top\mathbf X\hat{\boldsymbol\beta}=\mathbf X^\top\mathbf y$ donnent $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y$, unique grâce à la convexité ; en pratique on résout, on n'inverse pas.
> - Géométriquement, $\hat{\mathbf y}=\mathbf H\mathbf y$ est la **projection orthogonale** de $\mathbf y$ ; les résidus sont orthogonaux aux colonnes de $\mathbf X$ ; $\operatorname{tr}\mathbf H=p$.
> - Sous H1-H4 : $\hat{\boldsymbol\beta}$ est sans biais, de variance $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$, et **le meilleur estimateur linéaire sans biais** (Gauss-Markov). On estime $\sigma^2$ par $\text{SCR}/(n-p)$.
> - $R^2=1-\text{SCR}/\text{SCT}$ mesure la part de variance expliquée ; il ne peut qu'augmenter avec le nombre de variables (préférer $R^2$ ajusté pour comparer).
> - Une variable qualitative entre par des **indicatrices** (une modalité de référence) ; un coefficient se lit « toutes choses égales par ailleurs » (Frisch-Waugh-Lovell).
> - Avec $\log y$, un coefficient $\beta$ correspond à un effet multiplicatif $e^\beta$ ; pour prédire la **moyenne** en euros, corrigez la rétro-transformation.


## 1.2 Inférence sur les coefficients

> 💡 **Intuition.** Les coefficients de `m2` (−0,34 pour Réseaux, +0,009 par année d'âge…) sont calculés sur **un** échantillon de 1 740 clients. Avec un autre échantillon, on aurait obtenu d'autres valeurs. La question de l'inférence est : *de combien ces chiffres peuvent-ils bouger ?* et donc *que peut-on affirmer sur la vraie valeur ?* C'est exactement l'esprit du chapitre 3 du volume I (intervalles de confiance, tests), appliqué maintenant à chaque coefficient d'un modèle.

On part des mêmes données qu'en 1.1 : les 1 740 clients actifs, et les modèles `m1` (âge), `m2` (âge et canal) et `m3` (avec interaction) déjà ajustés.


### 1.2.1 La loi des estimateurs sous l'hypothèse de normalité

Au 1.1.5, nous avons établi l'espérance et la variance de $\hat{\boldsymbol\beta}$. Pour fabriquer des tests et des intervalles exacts, il faut sa **loi** entière : c'est le rôle de l'hypothèse H5 (erreurs normales).

> 📐 **Théorème 3.** Sous H1 à H5 :
> 1. $\hat{\boldsymbol\beta}\sim\mathcal N\big(\boldsymbol\beta,\ \sigma^2(\mathbf X^\top\mathbf X)^{-1}\big)$ ;
> 2. $\dfrac{(n-p)\,s^2}{\sigma^2}=\dfrac{\text{SCR}}{\sigma^2}\sim\chi^2_{n-p}$ ;
> 3. $\hat{\boldsymbol\beta}$ et $s^2$ sont **indépendants**.
>
> *Démonstration.* (1) On a vu que $\hat{\boldsymbol\beta}=\boldsymbol\beta+\mathbf A\boldsymbol\varepsilon$ avec $\mathbf A=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top$ : c'est une transformation linéaire d'un vecteur gaussien, donc un vecteur gaussien, d'espérance $\boldsymbol\beta$ et de variance $\sigma^2\mathbf A\mathbf A^\top=\sigma^2(\mathbf X^\top\mathbf X)^{-1}$.
> (3) Le résidu est $\hat{\boldsymbol\varepsilon}=(\mathbf I-\mathbf H)\boldsymbol\varepsilon$. Le couple $(\hat{\boldsymbol\beta},\hat{\boldsymbol\varepsilon})$ est gaussien (transformation linéaire de $\boldsymbol\varepsilon$), et sa covariance croisée vaut $\operatorname{Cov}(\mathbf A\boldsymbol\varepsilon,(\mathbf I-\mathbf H)\boldsymbol\varepsilon)=\sigma^2\mathbf A(\mathbf I-\mathbf H)^\top=\sigma^2(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top(\mathbf I-\mathbf H)=\mathbf 0$, car $\mathbf X^\top(\mathbf I-\mathbf H)=\mathbf 0$ (1.1.4). Pour des vecteurs gaussiens **conjoints**, covariance nulle ⇔ indépendance. Comme $s^2$ ne dépend que de $\hat{\boldsymbol\varepsilon}$, on obtient (3).
> (2) $\text{SCR}/\sigma^2=(\boldsymbol\varepsilon/\sigma)^\top(\mathbf I-\mathbf H)(\boldsymbol\varepsilon/\sigma)$, où $\boldsymbol\varepsilon/\sigma\sim\mathcal N(\mathbf 0,\mathbf I_n)$ et $\mathbf I-\mathbf H$ est un projecteur orthogonal de rang $n-p$. Dans une base orthonormée adaptée au projecteur, c'est la somme de $n-p$ carrés de lois $\mathcal N(0,1)$ indépendantes : une loi $\chi^2_{n-p}$ (théorème de Cochran). $\square$

Pour un coefficient $\beta_j$, la formule (1) donne $\hat\beta_j\sim\mathcal N(\beta_j,\ \sigma^2c_{jj})$ où $c_{jj}$ est le $j$-ième élément diagonal de $(\mathbf X^\top\mathbf X)^{-1}$. Comme $\sigma$ est inconnu, on le remplace par $s$ : l'**erreur standard** de $\hat\beta_j$ est $\operatorname{se}(\hat\beta_j)=s\sqrt{c_{jj}}$. Et le rapport d'une normale à la racine d'un $\chi^2$ indépendant, divisé par ses degrés de liberté, est une loi de Student (volume I, section 3.3.3) :

$$\boxed{\;T_j=\frac{\hat\beta_j-\beta_j}{\operatorname{se}(\hat\beta_j)}\;\sim\;t_{n-p}\;}$$

Reconstruire à la main le tableau de `statsmodels` pour `m2`, colonne par colonne, est un excellent exercice (cahier, application 1.3). Avec $s=0{,}3705$ et le quantile de Student $t_{1736,\,0{,}975}=1{,}961$ (presque 1,96 : $n-p=1\,736$ est grand), on obtient exactement le tableau du logiciel :

```text
                       coef  std err         t  P>|t|  IC bas  IC haut
Intercept            4.2206   0.0175  241.3693    0.0  4.1863   4.2549
C(canal)[T.Site]    -0.1571   0.0231   -6.8065    0.0 -0.2024  -0.1119
C(canal)[T.Réseaux] -0.3368   0.0225  -14.9770    0.0 -0.3809  -0.2927
a                    0.0092   0.0008   10.8618    0.0  0.0075   0.0108

identique à statsmodels : True True True
s = 0.3705 | quantile t(n-p, 97,5 %) = 1.9613  (presque 1,96 : n - p = 1736 est grand)
```

Chaque colonne a ainsi une origine claire : l'erreur standard vient de $s\sqrt{c_{jj}}$, la statistique $t$ est le rapport coefficient / erreur standard, la p-valeur est la probabilité qu'un Student à $n-p$ degrés de liberté dépasse $|t|$ en valeur absolue, et l'intervalle de confiance est $\hat\beta_j\pm t_{n-p,\,0{,}975}\operatorname{se}(\hat\beta_j)$ (c'est la construction du volume I, section 3.3.3, appliquée à chaque coefficient).

### 1.2.2 Tester un coefficient, lire un intervalle

Le **test de Student** d'un coefficient teste $H_0:\beta_j=0$ contre $H_1:\beta_j\neq0$ : « une fois les autres variables prises en compte, cette variable apporte-t-elle une information ? ». La statistique est $t_j=\hat\beta_j/\operatorname{se}(\hat\beta_j)$, et on rejette $H_0$ au niveau 5 % si $|t_j|>t_{n-p,\,0{,}975}\approx1{,}96$.

Dans le tableau précédent, les trois coefficients du canal et de l'âge ont des $|t|$ très supérieurs à 1,96 (la plus petite valeur, pour l'âge, est de l'ordre de 11) : les p-valeurs sont minuscules : elles s'affichent `0.000` dans le tableau de `statsmodels` (ce qui signifie « inférieur à 0,0005 », et non « exactement nul »), et `0.0` dans notre tableau arrondi à quatre décimales.

> ⚠️ **Rappels du volume I, appliqués ici.** (1) Une p-valeur n'est **pas** la probabilité que $H_0$ soit vraie (3.5.2). (2) « Significatif » n'est pas « important » (3.5.3) : avec 1 740 clients, même un très petit effet serait détecté. Il faut donc toujours lire **l'estimation et son intervalle**, pas seulement le test. (3) Si l'on teste beaucoup de coefficients, il faut se méfier des faux positifs (3.5.5) : nous y reviendrons au 1.4.

L'**intervalle de confiance** est bien plus informatif que la p-valeur. Pour Réseaux, l'intervalle sur le log-panier est environ $[-0{,}381\,;-0{,}293]$ ; en passant à l'exponentielle (une fonction croissante conserve les bornes), on obtient une **fourchette sur l'effet multiplicatif** : pour le Site, −14,5 % (intervalle à 95 % : de −18,3 % à −10,6 %) ; pour Réseaux, −28,6 % (de −31,7 % à −25,4 %) ; et pour dix ans d'âge de plus, +9,6 % (de +7,8 % à +11,4 %).


La phrase honnête à transmettre à la gérante est donc : « *à âge égal, un client acquis par Réseaux dépense environ 29 % de moins qu'un client de la boutique ; avec 95 % de confiance, la vraie différence se situe entre 25 % et 32 % de moins* ». Et pour l'âge : « *dix ans de plus sont associés à un panier de 8 à 11 % plus élevé* ».

**Un test peut aussi porter sur une combinaison de coefficients.** Par exemple : « le Site et Réseaux ont-ils le même panier (à âge égal) ? ». L'hypothèse est $H_0:\beta_{\text{Site}}-\beta_{\text{Réseaux}}=0$, c'est-à-dire $H_0:\mathbf c^\top\boldsymbol\beta=0$ avec $\mathbf c=(0,1,-1,0)^\top$. La variance de $\mathbf c^\top\hat{\boldsymbol\beta}$ est $\sigma^2\mathbf c^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf c$ : les covariances entre coefficients **comptent** (on ne peut pas se contenter de lire les deux erreurs standard du tableau). Ici, l'écart estimé vaut 0,180 (erreur standard 0,021), soit $t\approx8{,}7$ : à âge égal, le Site dépense significativement plus que Réseaux.


### 1.2.3 Le test $F$ : tester plusieurs coefficients à la fois

Comment tester que le **canal** compte, quand il se traduit par *deux* coefficients (`Site` et `Réseaux`) ? Faire deux tests $t$ séparés ne répond pas à la question (et multiplie les risques de faux positif). On utilise un **test $F$ de modèles emboîtés** : on compare le modèle complet $M_1$ (avec $p_1$ paramètres) au modèle réduit $M_0$ (avec $p_0<p_1$ paramètres, obtenu en imposant $q=p_1-p_0$ contraintes, par exemple « les deux coefficients du canal sont nuls »).

> 📐 **Statistique de Fisher.** En notant $\text{SCR}_0$ et $\text{SCR}_1$ les sommes de carrés résiduelles des deux modèles (le modèle réduit ajuste toujours moins bien : $\text{SCR}_0\ge\text{SCR}_1$),
> $$F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}\ \sim\ F_{q,\;n-p_1}\quad\text{sous }H_0 .$$
> *Pourquoi cette loi ?* Notons $\mathbf H_0$ et $\mathbf H_1$ les matrices chapeau des deux modèles (l'image de $\mathbf H_0$ est contenue dans celle de $\mathbf H_1$). Sous $H_0$, la vraie moyenne $\mathbf X\boldsymbol\beta$ appartient au petit sous-espace, donc $\text{SCR}_0-\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf H_1-\mathbf H_0)\boldsymbol\varepsilon$ et $\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf I-\mathbf H_1)\boldsymbol\varepsilon$. Les matrices $\mathbf H_1-\mathbf H_0$ et $\mathbf I-\mathbf H_1$ sont des projecteurs orthogonaux entre eux, de rangs $q$ et $n-p_1$ : par le théorème de Cochran, ce sont deux variables **indépendantes** de lois $\sigma^2\chi^2_q$ et $\sigma^2\chi^2_{n-p_1}$. Leur rapport, une fois divisé par les degrés de liberté, est par définition une loi de Fisher. $\square$
>
> L'intuition est limpide : le numérateur mesure **combien l'ajustement se dégrade** (par contrainte) quand on retire les variables ; le dénominateur est l'échelle de bruit du modèle complet. Si retirer les variables ne dégrade pas plus que du bruit, $F$ est proche de 1.


On trouve $\text{SCR}_0=269{,}94$, $\text{SCR}_1=238{,}30$ et $q=2$, donc $F\approx115{,}3$ (p-valeur de l'ordre de $10^{-47}$) : le calcul à la main coïncide avec la fonction `anova_lm` de `statsmodels`. Le canal est donc **très significatif** dans son ensemble.

Le même outil teste d'autres questions :

- **Le test global** du tableau de résultats (`F-statistic` dans `summary()`) compare le modèle complet au modèle réduit à la **seule constante** : « au moins une variable explicative est-elle utile ? ».
- **L'interaction âge × canal** (1.1.9) : `m3` contre `m2`, avec $q=2$ contraintes (« les deux différences de pente sont nulles »).
- **Un cas particulier** : quand $q=1$, $F=t^2$ (le test $F$ d'un seul coefficient est le carré du test $t$).


Pour l'interaction, $F\approx0{,}11$ et la p-valeur vaut 0,90 : rien n'indique que l'effet de l'âge diffère selon le canal, le modèle plus simple `m2` suffit. Les deux autres vérifications se passent bien : pour $q=1$, le carré de la statistique $t$ de l'âge (117,98) est exactement le $F$ de sa suppression, et le test global de `m2` donne $F\approx114{,}9$.

> 🧪 **Que se passe-t-il si les erreurs ne sont pas normales ?** Pour un grand échantillon, le théorème central limite (volume I, section 2.4.3) assure que $\hat{\boldsymbol\beta}$ est approximativement normal même si les erreurs ne le sont pas, de sorte que les tests $t$ et $F$ restent *approximativement* valides (avec les lois asymptotiques). Pour un petit échantillon avec des erreurs très asymétriques, il vaut mieux recourir au **bootstrap** (voir plus bas).

### 1.2.4 Intervalle de confiance et intervalle de prédiction

Deux questions très différentes se cachent derrière « prédire » :

1. **Quel est le panier moyen** des clients Réseaux de 25 ans ? Il s'agit d'estimer une **espérance** $\mathbf x_0^\top\boldsymbol\beta$ : on veut un **intervalle de confiance de la moyenne**.
2. **Quel sera le panier** d'*un* nouveau client Réseaux de 25 ans ? Il s'agit de prévoir une **observation** $y_0=\mathbf x_0^\top\boldsymbol\beta+\varepsilon_0$ : on veut un **intervalle de prédiction**, plus large, car il faut ajouter le bruit individuel $\varepsilon_0$.

> 📐 **Les deux formules.** La valeur prédite est $\hat y_0=\mathbf x_0^\top\hat{\boldsymbol\beta}$, de variance $\sigma^2\,\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$. Posons $h_0=\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$ (le « levier » du point $\mathbf x_0$). Alors
> $$\text{IC de la moyenne :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{h_0},\qquad\text{intervalle de prédiction :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{1+h_0}.$$
> Dans le second cas, l'erreur de prévision est $y_0-\hat y_0=\varepsilon_0-\mathbf x_0^\top(\hat{\boldsymbol\beta}-\boldsymbol\beta)$ : somme de deux termes **indépendants** ($\varepsilon_0$ est un nouveau bruit, indépendant de l'échantillon), d'où la variance $\sigma^2(1+h_0)$.

**À la main, sur les quatre commandes du 1.1.1.** Quel montant prévoir pour une commande de **5 articles** ? On a $\hat y_0=3+19{,}6\times5=101$ €, $s^2=\text{SCR}/(n-p)=25{,}2/2=12{,}6$, et $\mathbf x_0=(1,5)^\top$ donne $h_0=\frac1{20}(30-2\cdot10\cdot5+4\cdot25)=\frac{30}{20}=1{,}5$ (calcul avec $(\mathbf X^\top\mathbf X)^{-1}=\frac1{20}\begin{pmatrix}30&-10\\-10&4\end{pmatrix}$). Avec $n-p=2$ degrés de liberté, $t_{2,\,0{,}975}\approx4{,}303$ : IC de la moyenne $101\pm4{,}303\sqrt{12{,}6\times1{,}5}\approx101\pm18{,}7$ ; intervalle de prédiction $101\pm4{,}303\sqrt{12{,}6\times2{,}5}\approx101\pm24{,}2$. Le logiciel donne les mêmes bornes : de 82,3 à 119,7 pour la moyenne, de 76,9 à 125,2 pour une observation.


Ces intervalles sont énormes parce que $n=4$ et que $x_0=5$ est **hors de la plage** des données ($1$ à $4$) : $h_0=1{,}5$ est grand. C'est une propriété générale : $h_0$ **croît quand $\mathbf x_0$ s'éloigne du centre des données**, si bien que l'incertitude explose en **extrapolation**.

**Sur les clients de la boutique.** Dessinons, pour les clients acquis par Réseaux, le nuage log-panier contre âge avec la droite ajustée par `m2`, la bande de confiance de la moyenne et la bande de prédiction.


![Clients Réseaux : log du panier selon l'âge. La bande bleue (intervalle de confiance de la moyenne) est étroite ; la bande orange (prédiction pour un client) est beaucoup plus large et contient environ 95 % des points.](figures/ch01-bandes-prediction.png)

Deux observations. La bande de **confiance** est étroite et se resserre autour de l'âge moyen (là où $h_0$ est minimal), tout en s'évasant aux âges extrêmes. La bande de **prédiction** est quasi parallèle à la droite et très large : elle est dominée par le terme « $1$ » (le bruit individuel), que **rien** ne peut réduire, même avec un échantillon infini. Retenons : *on peut connaître très précisément le panier moyen d'un groupe, et pourtant prévoir très mal le panier d'un individu*.

En euros, il suffit d'appliquer l'exponentielle aux bornes (la transformation est croissante). Voici, pour un client Réseaux de 25 ans, l'appel de `statsmodels` qui fournit tout :

```python
profil = pd.DataFrame({"a": [25 - 36], "canal": pd.Categorical(["Réseaux"], categories=["Boutique", "Site", "Réseaux"])})
pred = m2.get_prediction(profil).summary_frame(alpha=0.05)
print(pred.round(3).T)      # mean_ci_* : confiance sur la moyenne ; obs_ci_* : prédiction pour un client
```
<!--sortie-->
```text
                   0
mean           3.783
mean_se        0.017
mean_ci_lower  3.750
mean_ci_upper  3.816
obs_ci_lower   3.056
obs_ci_upper   4.510
```


Le log-panier prédit vaut 3,783, soit un panier **médian** de 43,9 € (intervalle de confiance à 95 % : de 42,5 à 45,4 €) ; un nouveau client Réseaux de 25 ans aura, avec 95 % de confiance, un panier entre 21,2 et 91,0 €. Remarquez le vocabulaire : l'exponentielle des bornes de l'IC de $\mathbb E[\log y]$ donne un intervalle pour la **médiane** de $y$ (et non pour sa moyenne, cf. 1.1.8). L'intervalle de prédiction, lui, se transforme sans difficulté, car il concerne une observation.

### 1.2.5 Vérifier la théorie par simulation : la couverture des intervalles

Tout ceci repose sur H1-H5. Que vaut vraiment « 95 % de confiance » ? Vérifions-le comme on vérifie un théorème : en **répétant l'expérience** un grand nombre de fois quand on connaît la vérité. Utilisons le plan d'expérience réel $\mathbf X$ de `m2` (mêmes 1 740 clients), des coefficients vrais $\boldsymbol\beta^\star$ choisis par nous, un bruit normal d'écart-type 0,37, et générons 4 000 jeux de données. Pour chacun, nous construisons l'intervalle à 95 % du coefficient de Réseaux et vérifions s'il contient la vraie valeur.


Les intervalles à 95 % couvrent la vraie valeur dans environ 95 % des jeux de données (94,4 %, 95,1 %, 94,8 % et 95,0 % pour les quatre coefficients), et la statistique $t$ centrée sur la vérité se comporte comme une loi de Student (moyenne nulle, écart-type voisin de 1). Quand l'hypothèse nulle est vraie, le test $t$ à 5 % se trompe dans environ 5 % des cas : c'est exactement ce que promet la théorie. **Mais** n'oublions pas que cette simulation **respecte** H1 à H5 par construction. Dans la vraie vie, la couverture dépend de la qualité du modèle : c'est tout l'objet de la section 1.3.

### 1.2.6 Quand on ne veut pas supposer la normalité : le bootstrap des couples

Le bootstrap du volume I (section 3.3.5) s'étend à la régression : on tire au hasard, **avec remise**, des **clients entiers** (le vecteur $(y_i,\mathbf x_i)$, d'où le nom de « bootstrap des couples »), on réajuste le modèle sur chaque rééchantillon, et on observe la variabilité des coefficients. Aucune formule, aucune hypothèse de normalité.


Les deux approches donnent des intervalles quasi identiques (pour Réseaux : erreur standard de 0,0225 par la formule contre 0,0216 par bootstrap ; intervalle de −0,381 à −0,293 contre −0,379 à −0,293) : ici, la formule théorique est fiable. Le bootstrap devient précieux quand les hypothèses sont douteuses (erreurs très asymétriques, petit échantillon, quantité d'intérêt compliquée comme un rapport de coefficients).

### 1.2.7 Retour aux questions de la gérante

Nous pouvons maintenant répondre honnêtement aux trois questions de l'introduction du chapitre :

1. **« Combien dépense un client Réseaux de 50 ans par rapport à un client de la boutique de 30 ans ? »** C'est une combinaison linéaire de coefficients : effet du canal (−0,34) plus 20 ans d'âge (+20 × 0,009). Son intervalle de confiance s'obtient par la formule de variance d'une combinaison (1.2.2).
2. **« Est-ce le canal ou l'âge ? »** Le test $F$ du canal est très significatif **à âge égal** (1.2.3) : ce n'est pas l'âge. Et réciproquement.
3. **« Quel panier prévoir pour un nouveau client ? »** Un intervalle de prédiction, large (1.2.4).


Un client Réseaux de 50 ans dépense donc, en moyenne géométrique, environ **14 % de moins** qu'un client de la boutique de 30 ans : les 20 ans d'âge de plus compensent un peu plus de la moitié de l'écart de canal. Cette comparaison de deux profils précis, avec son intervalle (de −19 % à −9 %), est typiquement ce qu'une simple comparaison de moyennes de groupes ne peut pas donner.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 et 1.4, exercices 1.4 et 1.5.

> ✅ **À retenir (1.2).**
> - Sous H1-H5, $\hat{\boldsymbol\beta}\sim\mathcal N(\boldsymbol\beta,\sigma^2(\mathbf X^\top\mathbf X)^{-1})$, $\text{SCR}/\sigma^2\sim\chi^2_{n-p}$, et les deux sont indépendants : d'où $T_j=(\hat\beta_j-\beta_j)/\operatorname{se}(\hat\beta_j)\sim t_{n-p}$ avec $\operatorname{se}(\hat\beta_j)=s\sqrt{c_{jj}}$.
> - Le **test $t$** teste un coefficient ; le **test $F$** de modèles emboîtés, $F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}$, teste $q$ contraintes à la fois (par exemple tout un facteur qualitatif, ou une interaction). Pour $q=1$, $F=t^2$.
> - Préférez les **intervalles de confiance** aux seules p-valeurs ; en échelle logarithmique, transformez les bornes par $e^{(\cdot)}$ pour parler en pourcentage.
> - **Intervalle de confiance de la moyenne** ($\hat y_0\pm t\,s\sqrt{h_0}$) et **intervalle de prédiction** ($\hat y_0\pm t\,s\sqrt{1+h_0}$) répondent à deux questions différentes ; le second ne peut pas rétrécir en dessous du bruit individuel, et les deux **s'élargissent en extrapolation**.
> - Une simulation confirme que « 95 % » signifie bien 95 % de couverture… **quand le modèle est correct** ; le bootstrap des couples est une alternative sans hypothèse de normalité.


## 1.3 Diagnostics : le modèle est-il fiable ?

> 💡 **Intuition.** Un logiciel produit un tableau de coefficients quoi qu'on lui donne, même si le modèle est absurde. Les p-valeurs et les intervalles du 1.2 ne valent **que si les hypothèses H1 à H5 sont à peu près vraies**. Faire des diagnostics, c'est la visite médicale du modèle : on regarde ce qui reste *après* l'ajustement (les résidus), parce que les erreurs d'un modèle bien spécifié ne doivent contenir **aucune structure**. Si l'on voit une courbe, un entonnoir ou un point isolé dans les résidus, c'est que le modèle a raté quelque chose.

Nous reprenons les données des sections précédentes (modèles `m2` sur le log du panier et `m_niv` sur le panier en euros) et nous chargeons en plus les **ventes mensuelles** de la boutique (120 mois), qui nous serviront de deuxième terrain d'observation.


### 1.3.1 Les résidus : brut, standardisé, studentisé

Le résidu brut $\hat\varepsilon_i=y_i-\hat y_i$ approche l'erreur $\varepsilon_i$. Mais attention : les résidus **n'ont pas tous la même variance**, même si les erreurs vraies, elles, l'ont.

> 📐 **Variance d'un résidu.** On a vu (1.1.5) que $\hat{\boldsymbol\varepsilon}=(\mathbf I-\mathbf H)\boldsymbol\varepsilon$. Donc
> $$\operatorname{Var}(\hat{\boldsymbol\varepsilon})=(\mathbf I-\mathbf H)\,\sigma^2\mathbf I\,(\mathbf I-\mathbf H)^\top=\sigma^2(\mathbf I-\mathbf H),\qquad\text{soit}\qquad\operatorname{Var}(\hat\varepsilon_i)=\sigma^2(1-h_{ii}),$$
> où $h_{ii}$ est le $i$-ième élément diagonal de la matrice chapeau (le **levier** de l'observation $i$, étudié plus loin).

Un point à fort levier « attire » la droite vers lui : son résidu est mécaniquement plus petit. Pour comparer les résidus entre eux, on les **standardise** :

| Résidu | Formule | Usage |
|---|---|---|
| brut | $\hat\varepsilon_i=y_i-\hat y_i$ | calcul de base |
| **standardisé** (*studentisé en interne*) | $r_i=\dfrac{\hat\varepsilon_i}{s\sqrt{1-h_{ii}}}$ | variance ≈ 1 pour tous : comparable |
| **studentisé externe** | $t_i=\dfrac{\hat\varepsilon_i}{s_{(i)}\sqrt{1-h_{ii}}}$ | $s_{(i)}$ = écart-type estimé **sans** l'observation $i$ ; suit exactement une loi $t_{n-p-1}$ si le modèle est correct : sert à **tester** si $i$ est aberrante |

Sur les quatre commandes du 1.1.1 (leviers 0,7 ; 0,3 ; 0,3 ; 0,7, résidus bruts −0,6 ; −1,2 ; +4,2 ; −2,4, écart-type résiduel $s=\sqrt{12{,}6}\approx3{,}55$), la formule donne les résidus standardisés hmtBc0{,}309$ ; hmtBc0{,}404$ ; {,}414$ ; hmtBc1{,}234$ ; `statsmodels` retrouve exactement les mêmes valeurs. On voit que le dernier point (levier 0,7) a un résidu brut de −2,4 qui, une fois standardisé, pèse presque autant que celui du point C.


Pour le résidu studentisé externe, on n'a pas besoin de refaire $n$ régressions : $s_{(i)}^2=\big(\text{SCR}-\hat\varepsilon_i^2/(1-h_{ii})\big)/(n-p-1)$ (résultat classique, que `statsmodels` utilise aussi). Nous le vérifierons en 1.3.4 sur un exemple plus fourni. Sur ces *quatre* points, il est d'ailleurs dégénéré pour la commande C : les trois autres points $(1,22),(2,41),(4,79)$ sont **exactement alignés** (pente 19), donc $s_{(C)}=0$ et la statistique serait infinie. C'est une bonne illustration de ce qu'un test d'aberrance demande plus de points que cela.

### 1.3.2 Les graphiques de résidus : voir avant de tester

Trois graphiques suffisent à repérer l'essentiel :

1. **Résidus contre valeurs ajustées** : doit ressembler à un **nuage sans structure** centré sur 0. Une **courbe** signale une non-linéarité (H1) ; un **entonnoir** (dispersion qui augmente), une variance non constante (H4).
2. **Diagramme quantile-quantile (Q-Q) des résidus standardisés** : les points doivent suivre la diagonale si les erreurs sont normales (H5). Une queue relevée indique une asymétrie ou des valeurs extrêmes.
3. **Échelle-position** ($\sqrt{|r_i|}$ contre valeurs ajustées) : une tendance croissante confirme une variance non constante.

Mettons en concurrence **deux modèles pour le même phénomène** : le panier en euros (`m_niv`) et son logarithme (`m2`). Le premier est celui que l'on écrirait « naturellement » ; le second celui que nous avons choisi en 1.1.7 parce que le panier est asymétrique. Les diagnostics vont nous dire si ce choix était justifié.


![Diagnostics comparés. Ligne du haut : modèle sur le panier en € (résidus asymétriques, dispersion croissante, queue lourde à droite). Ligne du bas : modèle sur le log du panier (nuage homogène, points alignés sur la diagonale). La courbe orange est un lissage local.](figures/ch01-diagnostics-niveau-log.png)

La différence est nette. Pour le panier en euros (ligne du haut), les résidus sont très **asymétriques** : une nuée de points très hauts (jusqu'à 7 écarts-types), mais aucun point aussi bas, et le diagramme Q-Q montre une **queue droite très relevée** et une queue gauche trop courte. La dispersion augmente aussi avec la valeur ajustée : le lissage de l'échelle-position monte de 0,6 à 0,85 environ (l'entonnoir est modeste à l'œil, mais le test de Breusch-Pagan, ci-dessous, ne s'y trompe pas). Pour le log du panier (ligne du bas), le nuage est homogène, le lissage orange reste plat, et les points suivent la diagonale. La transformation logarithmique n'était donc pas un détail esthétique : elle rend le modèle **valide**.

> 💡 **Pourquoi le log résout le problème.** Quand les effets sont **multiplicatifs** ($y=\mu\cdot\eta$ avec $\eta$ un facteur aléatoire autour de 1), l'écart-type de $y$ est proportionnel à sa moyenne $\mu$ : les gros paniers fluctuent plus que les petits, exactement l'entonnoir observé. En passant au logarithme, $\log y=\log\mu+\log\eta$ : le bruit devient **additif** et de variance constante.

### 1.3.3 Les tests de diagnostic (et pourquoi ils ne remplacent pas les graphiques)

Des tests formalisent ce que l'œil voit.

**Variance non constante : le test de Breusch-Pagan.** Idée : si la variance dépend des variables explicatives, alors les carrés des résidus $\hat\varepsilon_i^2$ (estimations grossières de la variance) doivent être **prévisibles** à partir de $\mathbf X$. On régresse donc $\hat\varepsilon_i^2$ sur les mêmes variables ; si cette régression a un $R^2$ non négligeable, on rejette l'homoscédasticité. La statistique est $\text{LM}=n\,R^2_{\text{aux}}\sim\chi^2_{p-1}$ sous $H_0$ (variance constante). Calculons-la à la main pour les deux modèles et comparons à `statsmodels` :


Pour le modèle en euros, `LM` vaut 35,9 (p-valeur de $8\times10^{-8}$) : l'homoscédasticité est nettement rejetée ; pour le modèle en logarithme, `LM` vaut 1,92 (p-valeur de 0,59) : on ne la rejette pas. Le calcul à la main coïncide avec celui de `statsmodels`.

**Normalité des erreurs.** Le test de Shapiro-Wilk et celui de Jarque-Bera (fondé sur l'asymétrie et l'aplatissement, volume I, section 3.7.5) comparent les résidus à une loi normale. Avec un grand $n$, ils détectent des écarts minuscules sans importance pratique : le diagramme Q-Q reste l'outil principal. Ici, l'asymétrie des résidus vaut 1,40 en euros (excès d'aplatissement de 3,84) contre 0,11 (−0,06) en logarithme ; les deux tests rejettent très nettement la normalité pour le modèle en euros (p-valeurs inférieures à $10^{-28}$) et ne la rejettent pas pour le modèle en logarithme (0,23 et 0,16).


**Autocorrélation des erreurs (H4 : erreurs non corrélées).** Quand les observations sont ordonnées dans le temps, les erreurs successives peuvent se ressembler. Le test de **Durbin-Watson** mesure cela : $\text{DW}=\dfrac{\sum_{i\ge2}(\hat\varepsilon_i-\hat\varepsilon_{i-1})^2}{\sum_i\hat\varepsilon_i^2}\approx2(1-\hat\rho)$, où $\hat\rho$ est l'autocorrélation d'ordre 1 des résidus. Une valeur proche de 2 indique l'absence d'autocorrélation ; **inférieure à 2**, une autocorrélation positive. Les clients n'ont pas d'ordre naturel, donc ce test n'a pas de sens pour eux : utilisons plutôt les ventes mensuelles, avec le modèle d'une **tendance simple** $\text{ventes}_t=\beta_0+\beta_1 t+\varepsilon_t$, en niveau puis en logarithme.


![À gauche : les résidus du modèle de tendance sur le log des ventes forment des vagues saisonnières (ils ne sont pas du bruit pur). À droite : leur autocorrélation, avec des pics très nets aux décalages 12, 24 et 36 mois.](figures/ch01-residus-ventes.png)

Le $R^2$ du modèle en log est un peu meilleur, et c'est le seul des deux dont la variance est constante (Breusch-Pagan : $p=0{,}889$, contre $0{,}004$ en niveau). La valeur de Durbin-Watson, identique pour les deux modèles à deux décimales près (ce n'est pas une erreur de copie : la même structure temporelle persiste dans les deux jeux de résidus), est nettement inférieure à 2 : les erreurs sont **positivement autocorrélées** ($\hat\rho\approx0{,}22$ d'un mois sur le suivant). Mais la figure raconte une histoire bien plus riche que ce seul nombre. Le test de Durbin-Watson ne regarde que le **décalage d'un mois** ; or le graphique d'autocorrélation (à droite) montre trois pics très nets aux décalages **12, 24 et 36 mois** (autour de 0,6), et des creux négatifs vers 10 et 22 mois. La cause est identifiable : la **saisonnalité annuelle** (le pic de décembre revient chaque année), absente du modèle de tendance, se retrouve intégralement dans les résidus. Un seul test peut donc passer à côté d'une structure massive : *regardez toujours l'autocorrélation complète*.

Quand H4 (erreurs non corrélées) est violée, les estimations restent sans biais, mais **les erreurs standard sont fausses** (en général trop optimistes) : les p-valeurs du 1.2 ne sont plus fiables. La remédiation n'est pas un bricolage de régression ordinaire, mais les **modèles de séries temporelles** du chapitre 4 (section 4.1 : autocorrélation et décomposition saisonnière ; section 4.2 : ARIMA saisonniers).

> ⚠️ **Un test n'est pas un diagnostic.** (1) Avec un grand échantillon, un test rejette pour un écart minuscule et sans conséquence ; avec un petit échantillon, il laisse passer des défauts graves. (2) Un test ne dit pas **comment réparer**. (3) Les tests eux-mêmes supposent des hypothèses. Le bon réflexe : **graphique d'abord**, test ensuite pour *confirmer ce qu'on voit*, jugement enfin sur l'ampleur de l'écart.

### 1.3.4 Effet de levier et observations influentes

Certaines observations pèsent beaucoup plus que d'autres dans l'ajustement. Il faut distinguer trois notions, qu'on confond souvent :

- Un **point aberrant** (*outlier*) a un résidu **grand** : il est mal expliqué par le modèle.
- Un point à **fort levier** (*leverage*) a des valeurs de $\mathbf x$ **inhabituelles** (loin du centre des données) : il *peut* tirer la droite vers lui.
- Un point **influent** change **beaucoup** les résultats quand on le retire. Il est typiquement à la fois aberrant *et* à fort levier.

> 📐 **Le levier.** $h_{ii}=\mathbf x_i^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i$ est le $i$-ième élément diagonal de $\mathbf H$. Comme $\hat y_i=\sum_jh_{ij}y_j$, on a $\partial\hat y_i/\partial y_i=h_{ii}$ : c'est **le poids de $y_i$ dans sa propre prédiction**. Propriétés : $\tfrac1n\le h_{ii}\le1$ (avec constante) et $\sum_ih_{ii}=\operatorname{tr}\mathbf H=p$, donc le levier moyen vaut $p/n$. Règle empirique : un levier supérieur à $2p/n$ est « élevé ».
>
> **La distance de Cook** combine résidu et levier :
> $$D_i=\frac{(\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)})^\top\mathbf X^\top\mathbf X\,(\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)})}{p\,s^2}=\frac{r_i^2}{p}\cdot\frac{h_{ii}}{1-h_{ii}},$$
> où $\hat{\boldsymbol\beta}_{(i)}$ est l'estimateur calculé **sans** l'observation $i$ et $r_i$ le résidu standardisé. La première expression est la définition (« de combien l'ajustement bouge si j'enlève $i$, en unités d'erreur standard ») ; la seconde, un raccourci de calcul qui évite $n$ régressions. Il découle de l'identité $\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)}=(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i\,\hat\varepsilon_i/(1-h_{ii})$ (formule de Sherman-Morrison pour la mise à jour d'un inverse de matrice).

**Un petit exemple pour voir.** Six points : cinq bien alignés sur une droite de pente environ 2, et un sixième, **très à droite** ($x=12$), qui s'écarte de la tendance.


Sur ces six points, la pente vaut 1,03 avec les six points et 1,99 sans le sixième ; le levier du sixième point est de 0,89 (levier moyen $p/n=0{,}33$), son résidu standardisé de seulement −1,99, et sa distance de Cook de 16,4 (contre 0,36 au plus pour les cinq autres) ; sans lui, la tendance prévoyait 23,9 en $x=12$, alors qu'on a observé 14,0. Le calcul du résidu studentisé externe sans réajustement coïncide avec `statsmodels`.

![Un point à fort levier (rouge, x = 12) tire la droite orange vers lui. Sans ce point, la droite bleue suit le reste du nuage, et prévoit environ 24 en x = 12.](figures/ch01-levier.png)

Remarquez la leçon, qui surprend toujours : **le point influent a un résidu petit**. Comme la droite est tirée vers lui, son résidu brut est modeste (voyez la ligne des résidus), alors qu'il est très loin de ce que la tendance des cinq autres points prévoyait. C'est son **levier** (proche de 0,9, très au-dessus de la moyenne $p/n\approx0{,}33$) et sa **distance de Cook** qui le trahissent. Un diagnostic fondé sur les seuls résidus l'aurait laissé passer. Et la formule de Cook, retrouvée ici par réajustement sans chaque point, confirme le raccourci.

**Sur les clients de la boutique.** Appliquons ces outils au modèle `m2`. Avec 1 740 clients, un seul client ne pèse presque rien :

```python
infl = m2.get_influence()
h, cook = infl.hat_matrix_diag, infl.cooks_distance[0]
print(f"levier max = {h.max():.4f} | Cook max = {cook.max():.4f} | clients avec Cook > 4/n : {(cook > 4 / len(h)).sum()}")
```
<!--sortie-->
```text
levier max = 0.0089 | Cook max = 0.0067 | clients avec Cook > 4/n : 84
```


Aucun client n'a un levier ou une distance de Cook préoccupants : le plus grand levier (0,0089) est certes environ quatre fois le levier moyen (0,0023), mais il reste inférieur à 1 % (aucun client ne pèse même 1 % dans sa propre prédiction), et la distance de Cook maximale (0,0067) est plus de cent fois sous le seuil d'alerte de 1. Deux remarques de méthode :

- Le seuil « $D_i>4/n$ » est une **règle de dépistage**, pas un test : avec $n$ grand elle signale toujours quelques points (ici environ 5 % des clients), simplement parce que certains points sont toujours un peu plus éloignés que d'autres. Ce qui compte est qu'**aucun** ne soit isolé du lot. Regardez les valeurs, pas seulement le seuil.
- Le test des résidus studentisés externes, ajusté pour le nombre de tests (correction de **Bonferroni**, volume I, section 3.5.5), est un vrai test de « valeur aberrante » : la plus grande valeur absolue (environ 3,73) a une p-valeur brute de 0,0002, mais parmi 1 740 observations on s'attend à de telles valeurs : une fois la correction de Bonferroni appliquée, la p-valeur ajustée est de 0,35, rien de significatif.

> 💡 **Que faire d'une observation influente ?** Ne la supprimez **pas** automatiquement. (1) Vérifiez qu'il ne s'agit pas d'une **erreur de saisie** (un panier de 5 000 € au lieu de 50). (2) Si elle est authentique, regardez comment les conclusions changent **avec et sans** elle, et rapportez les deux. (3) Si elle représente un phénomène réel mais rare, envisagez une méthode **robuste** (section 1.6). Retirer un point « parce qu'il gêne » est l'une des formes les plus courantes de falsification involontaire.

### 1.3.5 La multicolinéarité : quand deux variables disent la même chose

Si deux variables explicatives sont presque redondantes, le modèle ne peut pas **départager** leurs effets. Les prédictions restent bonnes, mais les coefficients individuels deviennent **instables** et leurs erreurs standard explosent.

> 📐 **Pourquoi les erreurs standard explosent.** Par le théorème de Frisch-Waugh-Lovell (1.1.7), le coefficient de la variable $\mathbf x_j$ est la pente de la régression sur la partie de $\mathbf x_j$ qui n'est pas expliquée par les autres variables, soit $\tilde{\mathbf x}_j=\mathbf M_{-j}\mathbf x_j$ (les résidus de la régression de $\mathbf x_j$ sur les autres colonnes). Donc
> $$\operatorname{Var}(\hat\beta_j)=\frac{\sigma^2}{\|\tilde{\mathbf x}_j\|^2}=\frac{\sigma^2}{\text{SCT}_j\,(1-R_j^2)},$$
> où $\text{SCT}_j=\sum_i(x_{ij}-\bar x_j)^2$ et $R_j^2$ est le $R^2$ de la régression de $\mathbf x_j$ sur les autres variables explicatives. Quand $R_j^2\to1$ (colinéarité), la partie « propre » de $\mathbf x_j$ disparaît et la variance explose. Le **facteur d'inflation de la variance** est
> $$\text{VIF}_j=\frac{1}{1-R_j^2}.$$
> Règles empiriques : $\text{VIF}>5$ : à surveiller ; $\text{VIF}>10$ : problématique.

**Provoquons le problème.** Ajoutons au modèle `m2` l'âge **exprimé en mois**, mesuré avec un petit bruit (le client indique son âge « à peu près » ; l'âge en mois est quasiment $12\times$ l'âge en années) :


Les prédictions sont aussi bonnes (le $R^2$ ne bouge pas), mais regardez les coefficients de l'âge : l'erreur standard de `a` est multipliée par plus de quarante, et le coefficient lui-même est devenu **négatif** et non significatif : pourtant, nous savons que l'effet de l'âge est positif. Les deux variables se « disputent » le même effet. Les VIF, de l'ordre de 1 800, le disent sans ambiguïté, alors que ceux des variables de canal restent bas (1,5). Les coefficients du **canal** sont, eux, intacts, car ils ne sont pas corrélés avec ce couple : la multicolinéarité n'abîme que les coefficients des variables concernées.

**Une colinéarité plus sournoise : les termes polynomiaux non centrés.** Si l'on ajoute le carré de l'âge pour tester une courbure, $\text{âge}$ et $\text{âge}^2$ sont très corrélés (les deux croissent ensemble). Le **centrage** règle le problème :


Le terme quadratique n'est pas significatif dans les deux cas (la p-valeur du terme du second degré est identique avec ou sans centrage, comme il se doit : on décrit le *même* modèle), mais les VIF passent de plus de 30 à 1 après centrage, ce qui rend les coefficients lisibles. L'âge n'a pas de courbure détectable : la relation avec le log-panier est bien linéaire (H1 est plausible).

> 💡 **Que faire en cas de multicolinéarité ?** (1) **Retirer** une des variables redondantes, ou les **combiner** en une seule (moyenne, indice). (2) **Centrer** les variables avant de créer des puissances ou des interactions. (3) Si l'on tient à garder toutes les variables et que l'objectif est la **prédiction**, la **régularisation** (Ridge, section 1.5) stabilise les coefficients. (4) Si l'objectif est d'**interpréter** un effet précis, il faut accepter qu'on ne peut pas séparer l'effet de deux variables quasi identiques : il est plus honnête de le dire.

### 1.3.6 Variance non constante : que faire ?

Pour `m_niv`, nous avons vu que le défaut est net. Trois remèdes :

1. **Transformer la réponse** (le logarithme, ici : c'est la solution privilégiée, car elle rend le modèle plus naturel).
2. **Changer de famille de lois** (modèles linéaires généralisés, chapitre 2 : par exemple une régression Gamma, qui suppose précisément que l'écart-type est proportionnel à la moyenne).
3. **Garder le modèle en niveau et corriger les erreurs standard** par la méthode « robuste à l'hétéroscédasticité ». C'est utile quand on tient à l'échelle d'origine.

> 📐 **Erreurs standard de White (« sandwich »).** Si $\operatorname{Var}(\boldsymbol\varepsilon)=\boldsymbol\Omega$ est diagonale mais avec des $\sigma_i^2$ différents, alors $\hat{\boldsymbol\beta}$ reste sans biais, mais sa variance devient
> $$\operatorname{Var}(\hat{\boldsymbol\beta})=(\mathbf X^\top\mathbf X)^{-1}\Big(\sum_i\sigma_i^2\,\mathbf x_i\mathbf x_i^\top\Big)(\mathbf X^\top\mathbf X)^{-1}$$
> (le « sandwich » : deux tranches de pain $(\mathbf X^\top\mathbf X)^{-1}$ autour de la garniture). On remplace $\sigma_i^2$ par un estimateur : $\hat\varepsilon_i^2$ (version **HC0**), ou, plus prudent pour les échantillons de taille modérée, $\hat\varepsilon_i^2/(1-h_{ii})^2$ (version **HC3**). La formule classique $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ n'en est qu'un cas particulier (variances égales).

Comparons, pour `m_niv`, les erreurs standard classiques, robustes (HC3), et celles d'un bootstrap des couples (qui ne fait aucune hypothèse sur la variance) :


Les erreurs standard robustes sont plus proches du bootstrap que les erreurs classiques pour la constante, le coefficient du Site et celui de Réseaux : la formule classique **sous-estimait** l'incertitude de ces coefficients (de 12 % environ pour la constante et le Site : pour le Site, 1,52 par la formule classique, 1,69 en robuste et 1,66 par bootstrap). Pour le coefficient de l'âge, tout concorde. L'écart n'est pas énorme, mais il va dans le sens qu'annonce la théorie. Dans les modèles où l'hétéroscédasticité est plus forte, il peut être considérable.

### 1.3.7 Courbure et variables manquantes : lire les graphiques de résidus partiels

Pour déceler une relation **non linéaire** avec une variable précise $x_j$, on trace les **résidus partiels** : $\hat\varepsilon_i+\hat\beta_jx_{ij}$ contre $x_{ij}$. Si la relation est linéaire, le nuage suit la droite de pente $\hat\beta_j$ ; une courbure systématique suggère d'ajouter un terme (carré, logarithme, ou une transformation plus flexible, cf. les GAM de la section 2.5).


![Résidus partiels pour l'âge : le lissage local (orange) suit la droite du modèle (bleu pointillé) : pas de courbure détectable.](figures/ch01-residus-partiels.png)

Le lissage orange épouse la droite bleue : la linéarité en l'âge est acceptable (ce que le test du terme quadratique, plus haut, confirmait). Notez que le lissage s'écarte un peu aux âges extrêmes, où il y a peu de clients : c'est du bruit d'échantillonnage, pas de la structure.

**Verdict sur `m2`.** Le modèle `log_panier ~ a + C(canal)` passe les contrôles : linéarité plausible, variance constante (Breusch-Pagan non significatif), résidus proches de la normale, aucune observation influente, pas de colinéarité entre ses variables. Les intervalles du 1.2 sont donc fiables. Ce n'est **pas** une preuve que le modèle est « vrai » (des variables importantes peuvent manquer), seulement que ses hypothèses ne sont pas manifestement violées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercices 1.6, 1.8 et 1.10.

> ✅ **À retenir (1.3).**
> - Les résidus d'un bon modèle ne contiennent **aucune structure**. Regardez : résidus contre ajustées (courbure, entonnoir), Q-Q (normalité), échelle-position (variance).
> - $\operatorname{Var}(\hat\varepsilon_i)=\sigma^2(1-h_{ii})$ : on **standardise** (ou studentise) les résidus avant de les comparer. Un point à fort levier a un résidu brut **petit** : ne vous fiez pas aux seuls résidus.
> - **Levier** $h_{ii}$ (valeurs inhabituelles de $\mathbf x$), **résidu** (écart à la prédiction) et **influence** (changement des résultats si on retire le point, **distance de Cook**) sont trois notions distinctes. Ne supprimez jamais un point sans enquêter.
> - **VIF** $=1/(1-R_j^2)$ mesure l'inflation de variance due à la colinéarité ; **centrer** avant de créer des puissances.
> - Si la variance n'est pas constante : transformer (log), changer de famille (GLM), ou corriger les erreurs standard (**sandwich**, HC3). Si les erreurs sont **autocorrélées** (séries temporelles) : chapitre 4.
> - Un test (Breusch-Pagan, Shapiro, Durbin-Watson) **complète** un graphique, il ne le remplace pas.


## 1.4 Sélection de variables et comparaison de modèles

> 💡 **Intuition.** Face à dix variables possibles, laquelle garder ? Tout garder semble prudent, mais chaque variable inutile ajoute du **bruit** à l'estimation (les erreurs standard grossissent) et peut conduire à des prédictions pires que celles d'un modèle plus simple. À l'inverse, oublier une variable utile introduit un **biais**. Choisir un modèle, c'est trouver le bon compromis entre **trop simple** (qui rate des effets réels) et **trop complexe** (qui s'ajuste au hasard de l'échantillon, c'est le *surajustement*). Il existe pour cela des outils objectifs : des critères d'information (AIC, BIC), la validation croisée, des tests emboîtés.

Pour avoir plus de variables à départager, nous ajoutons aux données précédentes les **notes de l'enquête de satisfaction** (`donnees/enquete_satisfaction.csv`) : 60 % des clients y ont répondu (au hasard), avec huit questions notées de 1 à 5. Les questions q1 à q4 portent sur les **produits**, q5 à q8 sur le **service et la livraison** ; nous en tirons deux scores moyens.


Nous travaillerons sur ces clients (tableau **`bq`**) : les clients actifs qui ont répondu à l'enquête (1 212 répondants à l'enquête, dont 1 076 clients actifs). La question est : quelles variables (âge, canal, ville, offre de bienvenue, scores produit et service, courbure de l'âge…) méritent de figurer dans le modèle du log-panier ?

### 1.4.1 Le surajustement : mieux s'ajuster n'est pas mieux prédire

Rappelons l'enjeu (volume I, chapitre 3 : biais et variance d'un estimateur). Un modèle très flexible épouse les données d'entraînement, y compris leur bruit. Pour le **voir**, faisons une expérience : on tire au hasard **40 clients** pour entraîner un modèle polynomial en l'âge de degré 0, 1, 2…, 8, et on mesure l'erreur sur les clients **non utilisés** pour l'entraînement. On répète 300 fois, et on moyenne.


![Erreur d'apprentissage (bleu) et erreur sur de nouveaux clients (orange) selon le degré du polynôme, avec 40 clients d'entraînement. L'erreur d'apprentissage ne fait que baisser ; l'erreur de prédiction est minimale au degré 1 puis explose (axe coupé).](figures/ch01-surajustement.png)

C'est le dessin classique du **surajustement** : l'erreur sur les données d'entraînement (bleu) **ne peut que baisser** quand on ajoute des paramètres, alors que l'erreur sur de nouvelles données (orange) atteint son minimum pour un modèle **simple** (le **degré 1**, avec une erreur de 0,163 : l'âge n'explique qu'une faible partie de la variation, et la vraie relation est linéaire) puis **remonte**, d'abord doucement, puis **vertigineusement** : 1,44 au degré 5 et plus de 12 000 au degré 8. Cette explosion vient de ce que les polynômes de haut degré, ajustés sur 40 clients, oscillent violemment dès qu'on sort de la zone dense des données (certains clients de test ont des âges bien plus extrêmes que ceux de l'entraînement) : c'est le surajustement dans sa forme la plus spectaculaire. L'écart entre les deux courbes mesure l'**optimisme** de l'erreur d'apprentissage. Retenez : *on ne peut jamais juger un modèle sur les données qui ont servi à l'ajuster* ; il faut une mesure corrigée de l'optimisme (critères d'information) ou une mesure sur des données mises de côté (validation).

### 1.4.2 Les critères d'information : AIC et BIC

On cherche une note qui récompense l'ajustement mais **pénalise la complexité**. Le $R^2$ ajusté (1.1.6) en est une, mais la statistique propose mieux : des critères fondés sur la **vraisemblance**.

> 📐 **La vraisemblance du modèle linéaire gaussien.** Sous H5, les $y_i$ sont indépendants de loi $\mathcal N(\mathbf x_i^\top\boldsymbol\beta,\sigma^2)$. La log-vraisemblance est
> $$\ell(\boldsymbol\beta,\sigma^2)=-\frac n2\log(2\pi\sigma^2)-\frac{1}{2\sigma^2}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2 .$$
> La maximiser en $\boldsymbol\beta$ revient à **minimiser les moindres carrés** : l'estimateur du maximum de vraisemblance est $\hat{\boldsymbol\beta}$ (volume I, section 3.2.5). En $\sigma^2$, on obtient $\hat\sigma^2_{\text{MV}}=\text{SCR}/n$ (le facteur $1/n$ et non $1/(n-p)$ : l'estimateur du maximum de vraisemblance est biaisé, comme nous l'avons vu en 1.1.5). En reportant, la valeur maximale de la log-vraisemblance est
> $$\hat\ell=-\frac n2\Big(\log(2\pi)+\log\frac{\text{SCR}}n+1\Big).$$

On pénalise ensuite par le **nombre de paramètres estimés** $k$. Par convention (celle de `statsmodels`), on compte les $p$ coefficients : $k=p$. (Certains logiciels comptent aussi $\sigma^2$, donc $k=p+1$ : cela ajoute la **même constante** à tous les modèles — 2 à l'AIC, $\log n$ au BIC — sans changer le moindre classement ; mais deux logiciels peuvent afficher des valeurs différentes pour le même modèle.)

$$\boxed{\text{AIC}=-2\hat\ell+2k},\qquad\boxed{\text{BIC}=-2\hat\ell+k\log n}.$$

**Plus petit = meilleur.** Les deux critères ont la même forme (ajustement + pénalité), avec une pénalité par paramètre de **2** pour l'AIC et de $\log n$ pour le BIC. Dès que $n\ge8$, $\log n>2$ : le BIC est **plus sévère**, et choisit donc des modèles plus petits.

> 💡 **D'où viennent-ils ?** (1) L'**AIC** (Akaike) estime, à une constante près, la **qualité prédictive** attendue du modèle sur de nouvelles données : $-2\hat\ell$ est trop optimiste (c'est l'erreur d'apprentissage), et on montre (asymptotiquement) que l'optimisme moyen vaut environ $2k$, d'où la correction. Il vise la **prédiction**. (2) Le **BIC** (Schwarz) approche la probabilité *a posteriori* d'un modèle dans une approche bayésienne (chapitre 6) ; il est **consistant** : si le vrai modèle fait partie des candidats, il le retrouve avec une probabilité qui tend vers 1 quand $n$ grandit, ce que l'AIC ne garantit pas (il a tendance à garder quelques variables en trop). Les deux peuvent être en désaccord : c'est normal, ils ne visent pas la même chose.

Sur le modèle âge + canal ajusté sur `bq`, le calcul à la main donne une log-vraisemblance de −431,47, un AIC de 870,94 et un BIC de 890,87 : exactement les valeurs de `statsmodels`.


> ⚠️ **Deux précautions.** (1) On ne peut comparer les AIC/BIC de deux modèles que s'ils sont ajustés **sur exactement les mêmes données et la même variable réponse** (comparer l'AIC d'un modèle sur $y$ à celui d'un modèle sur $\log y$ n'a aucun sens, sans correction). (2) La valeur absolue d'un AIC ne signifie rien ; seules les **différences** comptent. Une différence de moins de 2 est négligeable ; de plus de 10, très forte.

### 1.4.3 La validation croisée

Les critères d'information reposent sur des hypothèses (modèle bien spécifié, grand échantillon). La **validation croisée** est plus directe : on **simule** la prédiction sur des données nouvelles en réservant une partie des données.

**$K$-fold.** On découpe l'échantillon en $K$ paquets (*folds*) de taille égale (typiquement $K=10$). Pour chaque paquet, on ajuste le modèle sur les $K-1$ autres et on mesure l'erreur de prédiction sur le paquet laissé de côté. La moyenne des erreurs estime l'erreur de généralisation.

**Leave-one-out et la formule de PRESS.** Si $K=n$ (un client par paquet), on parle de *leave-one-out*. Pour la régression linéaire, il n'est pas nécessaire de refaire $n$ ajustements :

> 📐 **Théorème (PRESS).** L'erreur de prédiction de l'observation $i$ par le modèle ajusté **sans elle** est $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\dfrac{\hat\varepsilon_i}{1-h_{ii}}$. La somme des carrés $\text{PRESS}=\sum_i\big(\hat\varepsilon_i/(1-h_{ii})\big)^2$ s'obtient donc **avec un seul ajustement**.
> *Démonstration.* On a vu (1.3.4) que $\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)}=(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i\,\hat\varepsilon_i/(1-h_{ii})$. Multiplions à gauche par $\mathbf x_i^\top$ : $\mathbf x_i^\top\hat{\boldsymbol\beta}-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=h_{ii}\hat\varepsilon_i/(1-h_{ii})$. Donc $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\hat\varepsilon_i+h_{ii}\hat\varepsilon_i/(1-h_{ii})=\hat\varepsilon_i/(1-h_{ii})$. $\square$

Un client à fort levier est mal prédit quand on le retire, d'où le diviseur $1-h_{ii}$ : l'erreur « honnête » est supérieure au résidu brut. Une boucle explicite de $n=1\,076$ ajustements (un par client écarté) donne le même résultat que la formule : PRESS = 141,52, à comparer à la somme des carrés résiduelle, plus optimiste, de 140,49.


Pour la validation croisée $K$-fold, on écrit une petite fonction (10 paquets). **Règle importante : utiliser les mêmes paquets pour tous les modèles comparés** (comparaison appariée). Pour le modèle âge + canal, le RMSE de validation croisée vaut 0,3629, contre 0,3613 sur les données d'apprentissage.


### 1.4.4 Comparer plusieurs modèles sur les données de l'enquête

Mettons les outils à l'épreuve. Voici huit modèles candidats, du plus simple au plus chargé :

| | Variables |
|---|---|
| **M0** | constante seule |
| **M1** | âge |
| **M2** | âge + canal |
| **M3** | âge + canal + score produit |
| **M4** | M3 + score service |
| **M5** | M3 + ville + offre de bienvenue |
| **M6** | M3 + âge² + interaction âge × canal |
| **M7** | tout : âge, âge², canal, ville, offre, scores, interactions |


```python
print(tab[["paramètres p", "R² ajusté", "AIC", "BIC", "RMSE CV10"]].round(3))
```
<!--sortie-->
```text
        paramètres p  R² ajusté       AIC       BIC  RMSE CV10
modèle                                                        
M0                 1      0.000  1082.344  1087.325      0.400
M1                 2      0.065  1010.513  1020.475      0.387
M2                 4      0.181   870.944   890.868      0.363
M3                 5      0.251   774.786   799.691      0.348
M4                 6      0.253   773.161   803.047      0.347
M5                11      0.248   785.882   840.673      0.350
M6                 8      0.250   779.784   819.632      0.349
M7                15      0.248   788.987   863.702      0.351
```

Lisons ce tableau avec méthode.

- Le **$R^2$ et le RMSE d'apprentissage** s'améliorent (ou restent égaux) à chaque ajout de variables : ils recommandent toujours le modèle le plus gros (M7). Pas un critère de sélection.
- Les **critères corrigés** (AIC, BIC, $R^2$ ajusté, validation croisée) arrêtent leur progression bien avant. Retenez l'ordre de grandeur : l'ajout du **score produit** (M2 → M3) est un gain énorme, l'ajout du **score service** (M3 → M4) est marginal, et tout ce qui vient après (ville, offre, âge², interactions) n'apporte **rien** (voire détériore).
- Le **BIC**, plus sévère, désigne le modèle **M3**. Les autres critères (AIC, $R^2$ ajusté, PRESS, validation croisée) désignent **M4**, qui ajoute le score service, mais **de justesse** : l'AIC de M4 est inférieur de 1,6 point à celui de M3 (différence inférieure à 2 : négligeable, selon la règle du 1.4.2), et le RMSE de validation croisée passe de 0,3478 à 0,3474. M3 et M4 prédisent donc pratiquement aussi bien ; à prédiction égale, on **préfère le plus simple** (principe de parcimonie), ce que fait le BIC. Les trois mesures hors échantillon (PRESS, CV10) sont très proches l'une de l'autre, ce qui rassure sur la fiabilité du classement.

**Les tests emboîtés** (1.2.3) répondent à des questions précises sur des modèles qui se contiennent :


Le score produit est hautement significatif ($F\approx102$) ; le score service est **à la limite** ($F\approx3{,}6$, p-valeur de 0,058) ; la ville et l'offre de bienvenue (p-valeur de 0,99), la courbure de l'âge et les interactions (0,80) n'ont **aucun** effet décelable. C'est cohérent avec les critères d'information : *deux méthodes différentes, la même conclusion*. Le cas du score service illustre bien la tension entre AIC et BIC : sa $t$-statistique, voisine de 1,9, dépasse le seuil $\sqrt2\approx1{,}41$ que l'AIC applique implicitement (un paramètre en plus est conservé si $t^2>2$) mais pas le seuil $\sqrt{\log n}\approx2{,}6$ du BIC pour $n\approx1000$.

### 1.4.5 La sélection automatique, et pourquoi il faut s'en méfier

Avec beaucoup de variables, comparer à la main devient impossible, d'où la tentation des procédures automatiques : sélection **ascendante** (*forward* : on part de rien et on ajoute à chaque étape la variable qui améliore le plus), **descendante** (*backward*), **pas à pas** (*stepwise*), ou **tous les sous-ensembles**. Elles sont commodes, mais elles posent un problème **statistique profond** : *le modèle final est choisi sur les données, puis ses p-valeurs sont lues comme si on l'avait choisi à l'avance.* Les p-valeurs et les intervalles du modèle final sont donc **trop optimistes**.

Une simulation le montre. On génère $n=100$ observations d'une variable réponse $y$ qui **n'a aucun lien** avec 20 variables explicatives (toutes du pur bruit). On applique la sélection ascendante par p-valeur (on ajoute la variable la plus significative tant que sa p-valeur est inférieure à 0,05). Combien de « découvertes » la méthode va-t-elle faire ? On répète 500 fois.


Dans près des deux tiers des jeux de données, la procédure « découvre » au moins une variable explicative, alors qu'il n'y en a **aucune** ; le $R^2$ du modèle final est nettement positif (environ 0,09 en moyenne, alors que la vraie valeur est 0) ; et, dans le modèle final, les coefficients retenus apparaissent **tous** significatifs, ce qui est trompeur : ils n'ont été retenus que parce qu'ils l'étaient. La procédure « honnête », qui **sépare** les données utilisées pour choisir des données utilisées pour tester, retrouve le taux d'erreur attendu de 5 %.

> ⚠️ **Les défauts de la sélection automatique.** (1) Les **p-valeurs et intervalles** du modèle final sont **trop optimistes** (biais de sélection). (2) Les coefficients retenus sont **gonflés** en valeur absolue (on garde ceux qui, par chance, sont grands). (3) Le résultat est **instable** : un autre échantillon donne un autre modèle. (4) Les procédures ne connaissent pas **le sens** des variables : on risque de retirer une variable de confusion essentielle. (5) Plus on essaie de modèles, plus on a de chances d'en trouver un « bon » par hasard (c'est le problème des tests multiples du volume I, section 3.5.5).

> 💡 **Bonnes pratiques.** (1) **Commencez par la connaissance du domaine** : quelles variables ont un sens ? (2) Fixez les modèles candidats **à l'avance**, en petit nombre, et comparez-les par AIC/BIC et validation croisée. (3) Si vous devez explorer beaucoup de variables, **mettez de côté un échantillon de test** *avant* de commencer, et ne l'utilisez qu'**une fois**, à la fin. (4) Pour la prédiction avec beaucoup de variables, préférez la **régularisation** (section 1.5), qui fait une sélection plus stable. (5) Décrivez honnêtement tout ce qui a été essayé.

### 1.4.6 Verdict : retrouver la vérité

Nous avons un luxe : les données sont simulées, nous connaissons donc le vrai modèle (détails dans la documentation de `build/donnees2.py`). Les clients actifs ont été produits par

$$\log(\text{panier})=4{,}00+0{,}008\,(\text{âge}-36)+\delta_{\text{canal}}+0{,}12\,F_1+\varepsilon,\qquad\varepsilon\sim\mathcal N(0,\,0{,}35^2),$$

avec $\delta=+0{,}22$ pour la Boutique, $+0{,}05$ pour le Site, $-0{,}12$ pour Réseaux. Ici $F_1$ est un **« goût pour les produits »** non observé (de moyenne 0 et d'écart-type 1) ; ni la ville, ni l'offre de bienvenue, ni le score de service **n'interviennent** dans le panier. Comparons au modèle M3 retenu par le BIC :

```text
                     estimation (M3)  IC95 bas  IC95 haut  vérité IC contient la vérité ?
Intercept                     3.6543    3.5385     3.7701     NaN                       —
C(canal)[T.Site]             -0.1573   -0.2114    -0.1032  -0.170                     oui
C(canal)[T.Réseaux]          -0.3519   -0.4045    -0.2993  -0.340                     oui
a                             0.0097    0.0078     0.0117   0.008                     oui
score_produit                 0.1557    0.1255     0.1859     NaN                       —
```


Les effets du **canal** et de l'**âge** sont retrouvés : les intervalles à 95 % contiennent les vraies valeurs (−0,17 pour le Site, −0,34 pour Réseaux, +0,008 par année d'âge). La méthode a bien écarté les variables **sans effet réel** (ville, offre, courbure, interactions : dans le modèle « tout » M7, leurs p-valeurs vont de 0,30 à 0,93). L'intercept ne se compare pas directement, car dans M3 il correspond à un score produit de 0 (une valeur impossible sur une échelle de 1 à 5) : un bon exemple de la nécessité de **centrer** les variables pour interpréter la constante.

Reste le cas du **score service** : il n'a aucun effet direct dans le vrai modèle du panier, et pourtant l'AIC et la validation croisée le **gardent**, de justesse, avec une $t$-statistique voisine de 1,9. C'est la **conséquence mécanique** de la corrélation entre les facteurs « produit » et « service » dans la population (corrélation de 0,3 entre $F_1$ et $F_2$) : le score de service est un peu informatif sur $F_1$, donc sur le panier. Et c'est un rappel qu'**une association n'est pas un effet**.

**Un dernier point, sur le score produit.** Le vrai effet est de **0,12 par écart-type de $F_1$**. Or le coefficient estimé (0,15 environ) est un effet **par point de note**, ce qui est autre chose : la note moyenne est un reflet **imparfait** de $F_1$ (chaque question est bruitée). Un calcul direct à partir de la façon dont les notes ont été simulées (générateur `build/donnees2.py` : $q_j\approx3{,}6+0{,}95\,(\lambda_jF_1+\sqrt{1-\lambda_j^2}\,\eta_j)$, avec des poids $\lambda_j=0{,}8;\,0{,}7;\,0{,}75;\,0{,}6$) permet de prédire le coefficient attendu **par point de note** :


La valeur attendue tombe **à l'intérieur** de l'intervalle de confiance. La **fiabilité** (la part de la variance de la note qui provient du vrai facteur, environ 0,8) est une notion générale : quand une variable explicative est mesurée avec du bruit, son coefficient est **atténué** par rapport à l'effet de la grandeur « vraie » (*erreur de mesure*) ; ici, la conversion d'échelle (par point de note plutôt que par écart-type de $F_1$) cache cet effet, mais il est bien là.

> 🧪 **Une dernière subtilité (hors programme, mais honnête).** Nous n'observons le panier que pour les clients **actifs** (ayant commandé), et l'activité dépend elle-même de $F_1$ dans la simulation (le goût pour les produits augmente le nombre de commandes). En ne gardant que les clients actifs, nous opérons une **sélection** qui peut biaiser légèrement la relation entre les notes et le panier. Le biais est ici faible et invisible dans les intervalles ; mais en pratique, restreindre un échantillon sur une variable liée à la réponse est une source classique de biais, que la section 2.6 (modèles à zéros excédentaires) permettra de traiter proprement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercice 1.7.

> ✅ **À retenir (1.4).**
> - Un modèle plus complexe s'ajuste toujours mieux aux données d'**entraînement** ($R^2$ croissant) mais pas forcément aux **nouvelles** données : c'est le **surajustement**.
> - **AIC** $=-2\hat\ell+2k$ vise la prédiction ; **BIC** $=-2\hat\ell+k\log n$ est plus sévère et consistant. Comparez les modèles sur les mêmes données et la même réponse ; seules les **différences** comptent.
> - La **validation croisée** estime l'erreur sur de nouvelles données ; pour la régression linéaire, le leave-one-out s'obtient d'un seul ajustement : $\text{PRESS}=\sum_i(\hat\varepsilon_i/(1-h_{ii}))^2$.
> - Les **tests $F$ emboîtés** comparent deux modèles qui se contiennent.
> - La **sélection automatique** fabrique des « découvertes » dans le bruit, gonfle les coefficients et rend les p-valeurs trompeuses : fixez des modèles candidats à l'avance, séparez choix et test, expliquez ce qui a été essayé.
> - Sur nos données, les critères retrouvent la vérité : âge, canal et score produit comptent ; ville, offre de bienvenue et courbure n'ont aucun effet.


## 1.5 ➕ Pour aller plus loin : la régularisation (Ridge, Lasso, Elastic Net)

> 🧭 **Section optionnelle.** Elle prolonge directement 1.3 (multicolinéarité) et 1.4 (surajustement) et sert de pont vers l'apprentissage automatique (volume III). On peut la sauter sans perdre le fil du chapitre.

> 💡 **Intuition.** Quand un modèle a beaucoup de variables pour peu de données, les moindres carrés ont **trop de liberté** : ils utilisent chaque coefficient pour coller au bruit, d'où des coefficients énormes et instables. La **régularisation** consiste à leur mettre une **laisse** : on minimise l'erreur *plus* une pénalité qui grandit avec la taille des coefficients. On accepte un petit biais volontaire (les coefficients sont « rétrécis » vers 0) en échange d'une **forte baisse de variance**. C'est une application directe du dilemme biais-variance, et la preuve que le théorème de Gauss-Markov (1.1.5) a des limites : il ne dit rien des estimateurs **biaisés**.


### 1.5.1 La régression Ridge

**Le principe.** On ajoute à la somme des carrés une pénalité sur la **norme au carré** des coefficients (sans la constante) :

$$\hat{\boldsymbol\beta}_{\text{ridge}}(\lambda)=\arg\min_{\boldsymbol\beta}\ \|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\lambda\|\boldsymbol\beta\|^2,\qquad\lambda\ge0 .$$

Le **paramètre de régularisation** $\lambda$ règle la sévérité de la laisse : $\lambda=0$ redonne les moindres carrés, $\lambda\to\infty$ écrase tous les coefficients vers 0.

> 📐 **Solution explicite.** Le gradient de la fonction objectif est $-2\mathbf X^\top(\mathbf y-\mathbf X\boldsymbol\beta)+2\lambda\boldsymbol\beta$. En l'annulant :
> $$(\mathbf X^\top\mathbf X+\lambda\mathbf I)\,\hat{\boldsymbol\beta}_{\text{ridge}}=\mathbf X^\top\mathbf y\quad\Longrightarrow\quad\hat{\boldsymbol\beta}_{\text{ridge}}=(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y .$$
> Pour $\lambda>0$, $\mathbf X^\top\mathbf X+\lambda\mathbf I$ est **toujours inversible** (ses valeurs propres sont $\ge\lambda>0$), même si $\mathbf X$ n'est pas de rang plein ou si $p>n$ : la régularisation résout aussi le problème de la colinéarité parfaite.

Deux règles pratiques, essentielles : (1) **la constante n'est pas pénalisée** (on centre simplement $\mathbf y$ et les colonnes de $\mathbf X$) ; (2) **il faut standardiser les variables** (moyenne 0, écart-type 1) : sinon la pénalité frappe plus les variables exprimées dans de petites unités (un âge en années contre un revenu en milliers d'euros) et le résultat dépend des unités choisies.

**Voir ce que fait la pénalité : la SVD.** Écrivons la décomposition en valeurs singulières de $\mathbf X$ centrée : $\mathbf X=\mathbf U\mathbf D\mathbf V^\top$ (volume I, section 1.1.4), où les $d_j$ sont les valeurs singulières. Alors

$$\mathbf X\hat{\boldsymbol\beta}_{\text{ridge}}=\sum_{j=1}^p\mathbf u_j\,\frac{d_j^2}{d_j^2+\lambda}\,\mathbf u_j^\top\mathbf y .$$

> 📐 **Démonstration.** $(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}=\mathbf V(\mathbf D^2+\lambda\mathbf I)^{-1}\mathbf V^\top$ et $\mathbf X^\top\mathbf y=\mathbf V\mathbf D\mathbf U^\top\mathbf y$, donc $\mathbf X\hat{\boldsymbol\beta}_{\text{ridge}}=\mathbf U\mathbf D(\mathbf D^2+\lambda\mathbf I)^{-1}\mathbf D\mathbf U^\top\mathbf y$, matrice diagonale $d_j^2/(d_j^2+\lambda)$. $\square$

Les moindres carrés correspondent à $\lambda=0$ : tous les facteurs valent 1. Ridge **rétrécit** chaque direction principale $\mathbf u_j$ d'un facteur $d_j^2/(d_j^2+\lambda)\in(0,1)$ : **très peu** pour les directions où les données varient beaucoup ($d_j$ grand), **beaucoup** pour celles où elles varient peu ($d_j$ petit), c'est-à-dire précisément les directions de **quasi-colinéarité**, où l'estimation par moindres carrés est la plus instable.

**Pourquoi un estimateur biaisé peut être meilleur.** L'erreur quadratique moyenne (EQM) d'un estimateur se décompose en $\text{biais}^2+\text{variance}$ (volume I, section 3.2.2). Prenons le cas le plus simple, où les colonnes de $\mathbf X$ sont orthonormales ($\mathbf X^\top\mathbf X=\mathbf I$) : alors $\hat\beta_j^{\text{MCO}}=\beta_j+\eta_j$ avec $\operatorname{Var}\eta_j=\sigma^2$, et $\hat\beta_j^{\text{ridge}}=\hat\beta_j^{\text{MCO}}/(1+\lambda)$.

> 📐 **L'EQM de Ridge est inférieure à celle des MCO pour un $\lambda$ petit.** Pour Ridge, biais $=-\dfrac{\lambda}{1+\lambda}\beta_j$ et variance $=\dfrac{\sigma^2}{(1+\lambda)^2}$, donc
> $$\text{EQM}(\lambda)=\frac{\lambda^2\beta_j^2+\sigma^2}{(1+\lambda)^2}.$$
> Sa dérivée en $\lambda=0$ vaut $-2\sigma^2<0$ : **l'EQM décroît dès qu'on s'écarte de $\lambda=0$**, quel que soit $\beta_j$. Le minimum est atteint en $\lambda^\star=\sigma^2/\beta_j^2$ : la bonne régularisation est d'autant plus forte que le bruit est grand et le signal faible. Le gain n'est pas un accident : *il existe toujours un $\lambda>0$ pour lequel Ridge bat les moindres carrés en EQM*.

**Voyons-le par simulation.** Deux variables explicatives très corrélées (corrélation 0,98), $n=30$, des vrais coefficients $(1,\,1)$ et $\sigma=1$. On répète 4 000 fois l'expérience et on mesure l'EQM des estimateurs pour plusieurs $\lambda$ (le code est dans le cahier, application 1.8) :

```text
corrélation entre les deux variables : 0.984
        EQM totale  biais² total  variance totale
lambda                                           
0.0         2.0874        0.0002           2.0872
0.5         0.5132        0.0001           0.5131
1.0         0.2281        0.0003           0.2278
2.0         0.0899        0.0007           0.0892
5.0         0.0332        0.0038           0.0294
10.0        0.0292        0.0128           0.0164
20.0        0.0487        0.0378           0.0109
50.0        0.1310        0.1259           0.0052
corrélation entre les deux estimations MCO du même échantillon : -0.984
```

Pour $\lambda=0$ (les moindres carrés), la **variance** domine : les deux estimations sont fortement corrélées négativement entre elles (si l'une surestime, l'autre sous-estime : voir la corrélation affichée), ce qui rend chacune très instable. Quand $\lambda$ augmente, le **biais²** augmente et la **variance** chute ; l'EQM totale passe par un **minimum** vers $\lambda=10$ (0,029, contre 2,09 pour les moindres carrés : soixante-dix fois moins), avant de remonter quand le biais devient excessif ($\lambda=50$ : 0,13). Le meilleur estimateur au sens de l'EQM est donc **biaisé** : ce n'est pas en contradiction avec Gauss-Markov, qui ne parlait que des estimateurs **sans biais**.

**À la main contre `scikit-learn`.** Sur les données de la boutique (âge, canal, notes de l'enquête), la formule explicite et la fonction `Ridge` de `scikit-learn` donnent exactement les mêmes coefficients (à cinq décimales) ; ceux des moindres carrés ($\lambda=0$) sont un peu plus grands :


Les deux colonnes de Ridge coïncident : `scikit-learn` fait exactement le calcul de la formule. Les coefficients de Ridge sont **rétrécis** par rapport aux moindres carrés, modestement ici ($\lambda=50$ est petit devant $n\approx1\,000$) : environ 4 % pour l'âge, 15 % pour le Site, 8 % pour Réseaux. Le rétrécissement est le plus marqué pour les indicatrices du canal, qui sont **corrélées entre elles** (les clients Site ne sont pas Réseaux) : leurs directions ont de petites valeurs singulières, exactement celles que le facteur $d_j^2/(d_j^2+\lambda)$ pénalise le plus.

### 1.5.2 Le Lasso : la pénalité qui élimine des variables

Ridge rétrécit tous les coefficients, mais **n'en met jamais aucun exactement à 0**. Le **Lasso** (*Least Absolute Shrinkage and Selection Operator*) remplace le carré par la **valeur absolue** :

$$\hat{\boldsymbol\beta}_{\text{lasso}}(\alpha)=\arg\min_{\boldsymbol\beta}\ \frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\sum_j|\beta_j| .$$

(La normalisation $1/(2n)$ est celle de `scikit-learn`.) Ce changement apparemment minuscule a une conséquence majeure : le Lasso produit des solutions **creuses**, où beaucoup de coefficients sont **exactement nuls**. C'est une régression qui **sélectionne** ses variables tout en les ajustant.

> 💡 **Pourquoi des zéros ? La géométrie.** Minimiser la somme des carrés sous la contrainte $\sum_j\beta_j^2\le r^2$ (Ridge) ou $\sum_j|\beta_j|\le r$ (Lasso) donne le même résultat que les versions pénalisées. Les courbes de niveau de la somme des carrés sont des **ellipses** centrées sur la solution des moindres carrés ; la solution contrainte est le **premier point de contact** entre une ellipse qui grandit et la région admissible. Pour Ridge, la région est un **disque** : le contact est un point lisse, quelconque, où aucun coefficient n'est nul. Pour le Lasso, la région est un **losange** dont les **sommets sont sur les axes** : une ellipse qui grandit touche très souvent un sommet, où un coefficient est exactement nul.


![La géométrie de la régularisation. Les ellipses sont les courbes de niveau de la somme des carrés, centrées sur la solution des moindres carrés. À gauche (Ridge), la région admissible est un disque et le point de contact a ses deux coordonnées non nulles. À droite (Lasso), la région est un losange : le contact se fait au sommet, sur l'axe, avec β₂ = 0 exactement.](figures/ch01-geometrie-ridge-lasso.png)

**Comment calcule-t-on le Lasso ?** Il n'a pas de formule fermée (la valeur absolue n'est pas dérivable en 0), mais un algorithme très simple : la **descente par coordonnées**. On optimise un coefficient à la fois, les autres étant fixés, et on recommence jusqu'à stabilisation. Pour des variables standardisées ($\tfrac1n\mathbf x_j^\top\mathbf x_j=1$), la mise à jour du coefficient $j$ est donnée par un **seuillage doux** :

$$\beta_j\leftarrow S\big(\rho_j,\alpha\big),\qquad\rho_j=\frac1n\mathbf x_j^\top\big(\mathbf y-\textstyle\sum_{k\ne j}\mathbf x_k\beta_k\big),\qquad S(\rho,\alpha)=\operatorname{signe}(\rho)\,\max(|\rho|-\alpha,\,0).$$

> 📐 **Pourquoi le seuillage doux ?** Fixons les autres coefficients : on minimise en $\beta_j$ la fonction $\tfrac12(\beta_j-\rho_j)^2+\alpha|\beta_j|$ (en développant et en utilisant $\tfrac1n\mathbf x_j^\top\mathbf x_j=1$). Pour $\beta_j>0$, la dérivée est $\beta_j-\rho_j+\alpha$, nulle en $\beta_j=\rho_j-\alpha$, valable si $\rho_j>\alpha$ ; symétriquement pour $\beta_j<0$. Si $|\rho_j|\le\alpha$, la dérivée à droite en 0 ($-\rho_j+\alpha$) est $\ge0$ et la dérivée à gauche ($-\rho_j-\alpha$) est $\le0$ : le minimum est exactement en **0**. Le Lasso **ramène à 0** toute variable dont la corrélation (partielle) avec le résidu est inférieure au seuil $\alpha$, et **rétrécit de $\alpha$** les autres.

Écrite à la main, cette descente par coordonnées donne exactement les coefficients de `scikit-learn`. Avec $\alpha=0{,}05$, on trouve 0,053 pour l'âge, −0,075 pour Réseaux, 0,055 pour le score produit, et **exactement zéro** pour `Site` et `score_service` (les moindres carrés donnaient 0,103 ; −0,172 ; 0,103 ; −0,075 et 0,020).


Cette coïncidence valide l'algorithme. Mais regardez ce que fait ce seuil $\alpha=0{,}05$, choisi arbitrairement : le Lasso met à zéro `score_service`, qui (dans le vrai modèle) n'a pas d'effet direct sur le panier, mais aussi `Site`, qui **a** un vrai effet (−15 % environ, 1.2.2), et il **divise par deux** à peu près les autres coefficients. Cette pénalité est donc **trop forte** : un $\alpha$ mal choisi supprime de vraies variables et sous-estime les effets. D'où l'importance de choisir $\alpha$ par validation croisée, ce que nous faisons maintenant.

### 1.5.3 L'Elastic Net : un compromis

Le Lasso a un défaut : face à un **groupe de variables très corrélées**, il en choisit une presque au hasard et élimine les autres, de façon instable. Ridge, au contraire, répartit le poids entre elles. L'**Elastic Net** combine les deux pénalités :

$$\frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\Big(\rho\sum_j|\beta_j|+\frac{1-\rho}2\sum_j\beta_j^2\Big),\qquad\rho\in[0,1].$$

Pour $\rho=1$ c'est le Lasso, pour $\rho\to0$, Ridge. Il fournit des solutions **creuses** tout en étant **stables** en présence de variables corrélées. On choisit $\alpha$ et $\rho$ par validation croisée.

### 1.5.4 Beaucoup de variables, peu de clients : l'expérience

Mettons les trois méthodes à l'épreuve (code pas à pas dans le cahier, application 1.9) dans un scénario réaliste d'**analyse exploratoire** : on dispose de **35 variables candidates** pour prévoir le log-panier d'un client, et de seulement **120 clients** pour apprendre le modèle. Parmi ces 35 variables : 4 portent un vrai signal (l'âge, deux indicatrices de canal, le score produit), quelques-unes sont des **variables pertinentes mais inutiles** (ville, offre de bienvenue, score service, courbure de l'âge, interactions), et **20 sont du pur bruit** que nous ajoutons (nombres tirés au hasard : des « variables » sans aucun rapport avec les clients). On teste sur les 956 autres clients de l'enquête.


Entraînons cinq modèles : les **moindres carrés avec les 35 variables**, un modèle de **référence** qui ne contient que les vraies variables (inaccessible en pratique, puisqu'on ne sait pas lesquelles sont vraies), puis **Ridge**, **Lasso** et **Elastic Net** avec $\lambda$ choisi par validation croisée à 10 paquets sur l'échantillon d'entraînement.

```text
                                RMSE apprentissage  RMSE test  variables non nulles  dont bruit
modèle                                                                                         
constante seule                             0.3803     0.4039                     0           0
référence : 4 vraies variables              0.3093     0.3612                     4           0
MCO, 35 variables                           0.2728     0.4152                    35          20
Ridge (λ par CV)                            0.3200     0.3765                    35          20
Lasso (α par CV)                            0.3032     0.3609                    15           7
Elastic Net (CV)                            0.3038     0.3608                    15           7

Ridge : lambda choisi = 134.0 | Lasso : alpha choisi = 0.0250 | Elastic Net : alpha = 0.0266, rho = 0.95
```

Lisons ce tableau, qui contient presque toute la leçon :

- Les **moindres carrés avec 35 variables** ont l'erreur d'apprentissage la plus faible (0,273 : ils s'ajustent au bruit) mais l'erreur de test **la pire** (0,415), **plus mauvaise que celle de la simple constante** (0,404) : avec 35 variables pour 120 clients, le modèle prédit moins bien que si l'on n'avait pas de modèle du tout. C'est le surajustement dans toute sa gloire.
- **Ridge** corrige une grande partie du problème en rétrécissant (erreur de test 0,377), mais il garde les 35 variables avec un coefficient non nul (y compris les 20 de bruit).
- Le **Lasso** et l'**Elastic Net** font mieux encore : ils ne gardent que 15 variables, et leur erreur de test (0,361) **égale** celle de la **référence** (0,361), un modèle qui connaît à l'avance les vraies variables, ce qu'on ne sait jamais faire en pratique. (La très légère avance du Lasso sur la référence, 0,3609 contre 0,3612, est dans le bruit d'échantillonnage : il ne faut pas en tirer de conclusion.)
- Ces méthodes ne font pas une sélection parfaite : sur les 15 variables conservées, **7 sont du bruit**. Mais elles les gardent avec des coefficients **petits**.

Les coefficients retenus par le Lasso, comparés à ceux des moindres carrés, racontent la même histoire.


Le Lasso retient **les quatre vraies variables** (âge, Site, Réseaux, score produit), avec des coefficients de 0,05 à 0,13 en valeur absolue, et laisse passer 7 variables de bruit dont les coefficients sont **au plus 0,025**, c'est-à-dire plus de deux fois plus petits que le plus petit coefficient d'une vraie variable : l'ordre de grandeur permet de les distinguer. Avec les moindres carrés, au contraire, les variables de bruit atteignent 0,073, un coefficient du même ordre que celui du score produit (0,106) : on ne peut plus faire la différence. Remarquez aussi que les coefficients MCO des vraies variables sont **gonflés** par rapport à ceux du Lasso (l'âge : 0,165 contre 0,050) : c'est le **biais de sélection** vu au 1.4.5, qui joue ici à l'envers, puisque la régularisation le contrôle.

**Les chemins de régularisation.** Pour voir la régularisation à l'œuvre, on trace comment chaque coefficient évolue quand la pénalité varie, de très forte (tous les coefficients à 0) à très faible (on retrouve les moindres carrés).


![Chemins de régularisation (à gauche : Ridge ; à droite : Lasso). Les coefficients des quatre vraies variables sont en couleur, ceux des 31 autres variables en gris. Plus on va vers la droite (pénalité faible), plus les coefficients grossissent. Le Lasso met à zéro les coefficients un par un ; Ridge les rétrécit tous ensemble sans jamais les annuler. La ligne pointillée marque la pénalité choisie par validation croisée.](figures/ch01-chemins-regularisation.png)

Sur la gauche de chaque graphique, la pénalité est énorme et tous les coefficients valent 0 ; en allant vers la droite, la pénalité se relâche et les coefficients se déploient. Avec le Lasso, les variables **entrent une par une** dans le modèle, à peu près dans l'ordre de leur pouvoir prédictif : le score produit, l'âge et Réseaux apparaissent en premier ; le Site, dont l'effet est pourtant réel, n'apparaît qu'à peu près en même temps que les premières variables de bruit (il est partiellement redondant avec Réseaux, comme on l'a vu avec Ridge) ; les variables de bruit entrent avec de petits coefficients. À la valeur choisie par validation croisée (pointillés), on est dans la zone où le signal est capté et où la plus grande partie du bruit est encore écartée. Avec Ridge, tous les coefficients se rétrécissent **ensemble** : le bruit n'est pas éliminé, seulement atténué.

### 1.5.5 Précautions

- **Standardisez toujours** les variables (et estimez la moyenne et l'écart-type sur l'échantillon d'**entraînement** seulement, jamais sur les données de test : sinon on laisse fuir de l'information du test dans le modèle).
- Choisissez $\lambda$ **par validation croisée** sur l'entraînement ; ne regardez l'échantillon de test qu'à la fin.
- Les coefficients régularisés sont **biaisés** par construction : on ne les interprète pas comme des effets (« à toutes choses égales par ailleurs ») avec la même confiance. Il n'y a pas de p-valeurs ni d'intervalles de confiance « standard » : les formules du 1.2 ne s'appliquent plus, et la sélection par le Lasso soulève précisément le problème de l'inférence **après sélection** discuté au 1.4.5.
- La régularisation vise la **prédiction**. Pour estimer un effet précis et le décrire à la gérante, on revient en général à un modèle plus simple et interprétable, éventuellement **choisi** avec l'aide du Lasso, mais **réajusté** sur de nouvelles données.
- **Lien avec le bayésien (chapitre 6).** Ridge équivaut à une approche bayésienne où chaque coefficient a une loi *a priori* **normale** centrée en 0 (le coefficient est « probablement petit »), et le Lasso à une loi *a priori* de **Laplace** (plus piquée en 0, d'où les zéros). La section 6.1 reprendra cette interprétation : $\lambda$ y correspond au rapport entre la variance du bruit et celle de l'*a priori*.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.8 et 1.9, exercice 1.11.

> ✅ **À retenir (1.5).**
> - Ridge : $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y$ ; il **rétrécit** les directions peu variables ($d_j^2/(d_j^2+\lambda)$), est toujours défini et réduit la variance au prix d'un **biais** : l'EQM s'améliore pour un $\lambda$ petit (et optimal en $\sigma^2/\beta^2$ dans le cas orthonormal).
> - Lasso : pénalité $\sum|\beta_j|$ ; il produit des solutions **creuses** (seuillage doux, descente par coordonnées) et sert de **sélection de variables**. Elastic Net : mélange des deux, stable pour les variables corrélées.
> - Standardiser, ne pas pénaliser la constante, choisir $\lambda$ par validation croisée, évaluer sur des données de test non utilisées.
> - Beaucoup de variables pour peu de données : les moindres carrés surajustent (ici, pire que la simple constante) ; la régularisation rejoint la prédiction du meilleur modèle possible. Mais ses coefficients ne s'interprètent pas comme ceux d'un modèle ordinaire.


## 1.6 ➕ Pour aller plus loin : la régression robuste

> 🧭 **Section optionnelle.** Elle prolonge la discussion des observations aberrantes et influentes de 1.3.4 et s'appuie sur l'idée, vue au volume I (section 3.1.3), que la médiane est plus robuste que la moyenne.

> 💡 **Intuition.** Les moindres carrés élèvent chaque écart **au carré** : un client dont le panier est dix fois trop grand (une virgule mal placée dans un export) pèse **cent fois** plus qu'un client ordinaire. Quelques erreurs de saisie peuvent suffire à fausser tout le modèle. La régression **robuste** limite l'influence des points extrêmes : elle cherche la droite qui colle à **la majorité** des données, sans se laisser tirer par quelques cas isolés. Elle fait pour la régression ce que la médiane fait pour la moyenne.

Nous reprenons les données propres des sections précédentes : 1 740 clients actifs et le modèle `m_propre` (`log_panier ~ a + C(canal)`, de coefficients 4,221 ; −0,157 ; −0,337 et 0,0092).


### 1.6.1 La fragilité des moindres carrés

Reprenons l'exemple du volume I (3.1.3) : cinq commandes de 20, 25, 30, 35 et 400 €. La **moyenne** (102 €) est entraînée par la dernière valeur ; la **médiane** (30 €) ne bouge pas. On dit que la médiane a un **point de rupture** de 50 % (il faut corrompre la moitié des données pour la faire dériver à l'infini) alors que celui de la moyenne est de **0 %** (une seule valeur suffit). Les moindres carrés, qui généralisent la moyenne, héritent de cette fragilité.

> 📐 **Pourquoi ? La fonction d'influence.** Un estimateur $\hat\theta$ minimise $\sum_i\rho(e_i)$. Son équation d'estimation est $\sum_i\psi(e_i)\,\mathbf x_i=\mathbf 0$ où $\psi=\rho'$ (comme les équations normales du 1.1.3, qui correspondent à $\rho(e)=e^2/2$ et $\psi(e)=e$). La fonction $\psi$ mesure **l'influence** d'un résidu sur l'estimation. Pour les moindres carrés, $\psi(e)=e$ n'est **pas bornée** : plus un point est extrême, plus il tire. Un estimateur robuste choisit un $\rho$ dont la dérivée $\psi$ est **bornée** : au-delà d'un seuil, un résidu de plus en plus grand n'a pas plus d'influence.

### 1.6.2 Les M-estimateurs et la fonction de Huber

La fonction de **Huber** est quadratique pour les petits résidus (comme les moindres carrés : efficace quand tout va bien) et **linéaire** pour les grands (comme la valeur absolue : l'influence est plafonnée). Avec un seuil $c$ (en unités d'écart-type du résidu) :

$$\rho_c(u)=\begin{cases}\tfrac12u^2&\text{si }|u|\le c\\ c|u|-\tfrac12c^2&\text{si }|u|>c\end{cases}\qquad\psi_c(u)=\begin{cases}u&\text{si }|u|\le c\\ c\,\operatorname{signe}(u)&\text{si }|u|>c\end{cases}\qquad u=\frac{e}{s}$$

où $s$ est une estimation **robuste** de l'échelle des résidus : on prend le **MAD** (écart absolu médian) : $s=\operatorname{médiane}(|e_i-\operatorname{médiane}(e)|)/0{,}6745$ (le facteur 0,6745 rend $s$ cohérent avec l'écart-type pour des erreurs normales). Le seuil usuel $c=1{,}345$ garantit que, **si les erreurs sont réellement normales**, l'estimateur de Huber conserve **95 % de l'efficacité** des moindres carrés : on perd très peu quand tout va bien, et on gagne beaucoup quand il y a des aberrations.

**L'algorithme : les moindres carrés repondérés (IRLS).** Les équations d'estimation $\sum_i\psi(u_i)\mathbf x_i=\mathbf 0$ s'écrivent $\sum_iw_iu_i\mathbf x_i=\mathbf 0$ avec les **poids** $w_i=\psi(u_i)/u_i$ : une régression **pondérée**. Pour Huber, $w_i=1$ si $|u_i|\le c$ et $w_i=c/|u_i|$ sinon : chaque point reçoit un poids d'autant plus petit qu'il est loin de la droite. Comme les poids dépendent des résidus qui dépendent de $\boldsymbol\beta$, on **itère** : (1) calculer les résidus, (2) en déduire les poids, (3) refaire une régression pondérée, jusqu'à stabilisation.

Dessinons les fonctions de perte et de poids de trois méthodes : les moindres carrés, Huber, et la fonction « bisquare » de Tukey (plus radicale : les points très éloignés reçoivent un poids **nul**).


![Fonctions de perte (à gauche) et poids (à droite). Les moindres carrés (gris) pénalisent quadratiquement et donnent le même poids à tous. Huber (bleu) devient linéaire au-delà de 1,345 écart-type. Tukey (orange) plafonne la perte et annule le poids des points très éloignés.](figures/ch01-fonctions-robustes.png)

Écrit à la main (cahier, application 1.10), l'algorithme IRLS donne les mêmes coefficients que la fonction `RLM` de `statsmodels` sur les données propres, à $10^{-4}$ près.


Sur des données **propres**, Huber et les moindres carrés donnent presque les mêmes coefficients (pour Réseaux : −0,333 pour Huber contre −0,337 pour les moindres carrés) : c'est l'efficacité de 95 % en action : on ne paie quasiment rien pour la robustesse. (L'écart minime, de l'ordre de $10^{-4}$, entre notre version et `RLM` tient à des choix de détail sur l'estimation de l'échelle.) Remarquez aussi que **18 % des clients reçoivent un poids inférieur à 1 même sur ces données propres** : ce n'est pas un signe d'anomalie, c'est exactement la proportion attendue pour des erreurs normales, puisque $\mathbb P(|Z|>1{,}345)\approx17{,}9\,\%$. Huber n'écarte pas 18 % des données : il en réduit un peu le poids.

### 1.6.3 Une contamination : les erreurs de saisie

Corrompons maintenant les données, comme le ferait un export mal formaté. Dans **6 %** des clients tirés au hasard, la virgule du panier est mal placée : le panier est **multiplié par 10** (54 € devient 540 €). Nous gardons la version propre (`df`) et fabriquons une copie contaminée (`dfc`).


Avec `statsmodels`, le modèle de Huber s'ajuste en une ligne (`rlm`, pour *robust linear model*) ; comparons ses coefficients à ceux des moindres carrés sur les mêmes données contaminées :

```python
rlm_c = smf.rlm("log_panier ~ a + C(canal)", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO propre": m_propre.params, "MCO contaminé": m_mco_c.params, "Huber contaminé": rlm_c.params}).round(3))
```
<!--sortie-->
```text
                     MCO propre  MCO contaminé  Huber contaminé
Intercept                 4.221          4.390            4.263
C(canal)[T.Site]         -0.157         -0.185           -0.157
C(canal)[T.Réseaux]      -0.337         -0.392           -0.353
a                         0.009          0.009            0.009
```

Les conséquences pour les moindres carrés sont de deux types. (1) Un **biais** : la constante est tirée vers le haut (de 4,22 à 4,39, soit +18 % sur le panier médian prédit : 80,6 € au lieu de 68,1 € ; en moyenne on attendrait $0{,}06\times\ln10\approx0{,}14$, le reste vient de la répartition aléatoire des erreurs entre les canaux), les effets du Site et de Réseaux sont gonflés, et les erreurs standard grossissent ; (2) surtout, l'**écart-type résiduel** passe de 0,37 à 0,665 : les moindres carrés *attribuent à tort un bruit énorme* à tout le modèle, donc des intervalles de confiance beaucoup trop larges, des prévisions moins précises, et des effets réels (le canal, l'âge) qui deviennent plus difficiles à détecter. Huber, lui, **donne un poids faible aux clients corrompus** (0,24 en moyenne, contre 0,97 aux clients intacts) : sa constante (4,26) et son effet pour Réseaux (−0,353) restent proches de ceux des données propres (4,22 et −0,337), alors que ceux des moindres carrés dérivent (4,39 et −0,392) ; son échelle (0,40) est proche de l'écart-type propre (0,37) alors que celui des moindres carrés double (0,665). Ses erreurs standard (0,020 pour la constante) sont proches de celles des données propres (0,017) et loin de celles des moindres carrés contaminés (0,031).

Visualisons-le sur un modèle simple (le log-panier selon l'âge seul, pour pouvoir tracer les droites).


![Nuage du log-panier selon l'âge, avec 6 % de paniers corrompus (rouge, environ 2,3 plus haut). La droite des moindres carrés sur les données contaminées (orange) est décalée vers le haut par rapport à la droite sur données propres (noire) ; la droite de Huber sur les mêmes données contaminées (bleu pointillé) reste beaucoup plus proche de la droite propre.](figures/ch01-robuste-contamination.png)

Les points rouges forment une bande décalée d'environ $\ln10\approx2{,}3$ au-dessus du nuage principal. La droite des moindres carrés (orange) est visiblement tirée vers le haut ; celle de Huber (bleu pointillé) reste beaucoup plus proche de la droite que l'on obtiendrait sans contamination (noire) : la constante passe de 4,03 (données propres) à 4,17 pour les moindres carrés mais seulement à 4,07 pour Huber, et la pente est presque intacte (0,0092 pour Huber, 0,0086 pour les moindres carrés, 0,0090 sans contamination). Huber n'est pas totalement insensible (les points corrompus gardent un petit poids, 0,24 en moyenne), mais l'essentiel du dégât est évité.

### 1.6.4 La limite : les points à fort levier

Les M-estimateurs de Huber protègent contre les **valeurs aberrantes de la réponse** $y$ (les « aberrations verticales »), mais **pas contre les points à fort levier** (valeurs aberrantes des *variables explicatives*, 1.3.4). Leur fonction $\psi$ borne l'influence du résidu, mais pas celle de la position $\mathbf x_i$ : un point très éloigné en $x$ attire la droite, et se retrouve avec un résidu qui n'a pas l'air grand. Faisons une seconde contamination : cette fois, ce sont des **âges** mal saisis. Pour 1 % des clients, l'âge est écrit avec un chiffre de trop (35 devient 350).


Les deux méthodes sont mises en échec : le coefficient de l'âge est **écrasé vers 0** (par les moindres carrés comme par Huber), parce que ces 17 clients, supposés avoir jusqu'à 640 ans, ont un panier ordinaire : sur ces points, la droite « âge ↗, panier ↗ » est contredite, et leur très fort levier leur donne le pouvoir de l'aplatir. Les estimateurs robustes **à fort levier** (MM-estimateurs, moindres carrés tronqués) existent, mais dans ce cas la bonne réponse est plus simple : **vérifier les données**. Un âge de 350 ans est **impossible** : une règle de validation élémentaire (`age <= 100`) l'élimine.

> ⚠️ **Robuste ne veut pas dire infaillible.** (1) Une méthode robuste ne remplace pas la **vérification des données** : un âge de 350 ans doit être détecté et corrigé, pas « absorbé » par un estimateur. (2) Les méthodes robustes protègent contre un certain **type** d'anomalie (ici, les erreurs sur $y$) et pas contre tous. (3) Elles sont moins efficaces que les moindres carrés si les données sont parfaitement propres (un peu : 5 % pour Huber). (4) Leurs erreurs standard demandent des formules spécifiques ; `RLM` les fournit, mais leurs propriétés sont asymptotiques. (5) Si les « aberrations » sont **réelles** (quelques très gros clients), il ne faut pas les cacher : il faut **les étudier**, car elles peuvent être ce qu'il y a de plus important commercialement.

### 1.6.5 Une autre voie : la régression quantile

Une approche voisine consiste à modéliser non plus la **moyenne** conditionnelle mais la **médiane** conditionnelle, en minimisant la **somme des valeurs absolues** des résidus (perte $\rho(e)=|e|$, dont l'influence $\psi=\operatorname{signe}(e)$ est bornée) : c'est la **régression médiane** (LAD, *least absolute deviations*), robuste aux aberrations verticales. Elle se généralise à un **quantile** quelconque $\tau\in(0,1)$ avec la perte asymétrique $\rho_\tau(e)=e\,(\tau-\mathbb 1_{e<0})$ : on modélise alors le $\tau$-ième quantile de la réponse, ce qui décrit **toute la distribution** et non son seul centre.

Voyons-le sur les paniers (code dans le cahier, application 1.11). Dans le modèle en **euros**, que dit le canal Réseaux sur les paniers faibles, moyens et élevés ? Et dans le modèle en **log** ?


![Effet du canal Réseaux selon le quantile du panier. À gauche (en euros) : l'effet est faible pour les petits paniers et de plus en plus négatif pour les grands. À droite (en log) : l'effet est à peu près constant, autour de −0,34, avec une bande de confiance qui contient la valeur des moindres carrés. Les bandes bleues sont les intervalles de confiance à 95 %.](figures/ch01-regression-quantile.png)

Lisons la figure. En **euros** (à gauche), l'effet de Réseaux n'est pas le même sur les petits et les grands paniers : le déficit est de 13,5 € pour les petits paniers (quantile 10 %) et de 33,9 € pour les gros (quantile 90 %), à comparer aux 20,8 € de l'effet moyen des moindres carrés. La moyenne (moindres carrés) ne voit qu'un effet moyen. En **log** (à droite), l'effet varie peu le long de la distribution (de −0,31 à −0,37, des intervalles de confiance qui se chevauchent largement et contiennent la valeur des moindres carrés, −0,337) : on peut le considérer comme **constant**. Les deux lectures sont **cohérentes** : un effet **multiplicatif** constant ($-29$ % du panier, quel que soit son niveau) se traduit en euros par un effet **proportionnel** au niveau (un gros panier perd plus d'euros qu'un petit). C'est exactement ce que le modèle simulé a programmé, et c'est une raison de plus de préférer le log : l'effet s'y résume par un **seul nombre**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.10 et 1.11, exercice 1.13.

> ✅ **À retenir (1.6).**
> - Les moindres carrés ont un **point de rupture de 0 %** : une seule aberration peut les fausser, car leur fonction d'influence $\psi(e)=e$ n'est pas bornée.
> - Les **M-estimateurs** (Huber, Tukey) minimisent $\sum\rho(e_i/s)$ avec un $\rho$ à influence bornée ; on les calcule par **moindres carrés repondérés** (IRLS), avec une échelle robuste (MAD). Huber avec $c=1{,}345$ garde 95 % d'efficacité si les erreurs sont normales.
> - Sur nos données contaminées, Huber **ignore presque** les paniers corrompus ; les moindres carrés sont biaisés et croient à un bruit énorme.
> - Les M-estimateurs ne protègent **pas** contre les points à **fort levier** : il faut vérifier les données d'abord.
> - La **régression quantile** (médiane ou autres quantiles) est robuste elle aussi, et décrit l'effet d'une variable sur **toute la distribution**.


## 1.7 ➕ Pour aller plus loin : les modèles à effets mixtes et hiérarchiques

> 🧭 **Section optionnelle.** Elle s'adresse à qui travaille sur des données **groupées** (clients dans des villes, élèves dans des classes, mesures répétées sur les mêmes personnes). Elle prépare les modèles hiérarchiques bayésiens du chapitre 6.

> 💡 **Intuition.** La régression ordinaire suppose que les observations sont **indépendantes** (hypothèse H4 du 1.1.2). Mais les 20 commandes retirées dans le **même point relais** se ressemblent : elles partagent la même équipe, le même emplacement, la même ambiance. Les traiter comme 20 observations indépendantes revient à compter vingt fois une information qui n'existe qu'une fois : on se croit plus sûr de soi qu'on ne l'est. Le **modèle mixte** reconnaît explicitement que chaque groupe a sa propre « personnalité » (un niveau de base propre) et la modélise comme un **effet aléatoire**, tiré d'une loi commune. Chaque groupe est ainsi à la fois **différent** des autres et **lié** à eux.

### 1.7.1 Un jeu de données groupé : les points relais

La boutique livre en partie via **30 points relais** (commerces partenaires où les clients viennent retirer leur colis). Pour chaque commande retirée, on dispose du **délai de livraison** (de 1 à 10 jours) et de la **note de satisfaction** (sur 20). Les relais sont de tailles très inégales (certains ont reçu 4 commandes, d'autres près de 60), et certains sont en zone **urbaine**. Les données sont simulées (graine fixe) selon un modèle que nous connaîtrons, comme d'habitude :

$$\text{note}_{ij}=12+1{,}2\,\text{urbain}_j+u_{0j}+(-0{,}7+u_{1j})(\text{délai}_{ij}-5)+\varepsilon_{ij},$$

où $i$ numérote les commandes du relais $j$, $u_{0j}\sim\mathcal N(0,1{,}6^2)$ est le **niveau de base propre au relais** (« certains relais notent plus généreusement »), $u_{1j}\sim\mathcal N(0,0{,}3^2)$ la **sensibilité propre au retard** de ce relais, et $\varepsilon_{ij}\sim\mathcal N(0,1{,}8^2)$ le bruit.


Notons déjà un fait important. Les 30 niveaux de base $u_{0j}$ ont été **tirés** d'une loi d'écart-type 1,6, mais avec seulement 30 relais, leur écart-type **réalisé** n'est que de 1,31. Avec peu de groupes, les composantes de variance sont **mal connues** : nous y reviendrons.

### 1.7.2 Trois façons de traiter les groupes

Pour estimer le niveau de base de chaque relais, trois stratégies s'offrent à nous :

1. **Mise en commun totale** (*complete pooling*) : on ignore les groupes (régression ordinaire sur les 484 commandes). On suppose que tous les relais sont identiques.
2. **Pas de mise en commun** (*no pooling*) : on estime chaque relais **séparément** (une indicatrice par relais). On suppose qu'ils n'ont rien en commun.
3. **Mise en commun partielle** (*partial pooling*) : le **modèle mixte**. Chaque relais a son propre niveau, mais ces niveaux sont supposés tirés d'une même loi : l'information d'un relais **aide** à estimer les autres.

Commençons par les deux premières, et regardons les conséquences sur les erreurs standard. La régression ordinaire (groupes ignorés) donne un coefficient du délai de −0,721 (erreur standard 0,039) et un effet « urbain » de 0,482, avec une erreur standard de 0,224 (intervalle de 0,04 à 0,92). Avec une indicatrice par relais, le coefficient du délai vaut −0,703 (erreur standard 0,034), mais l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).


> ⚠️ **Le problème de la mise en commun totale.** Les p-valeurs et intervalles de ce premier modèle supposent 484 observations **indépendantes**. Or elles sont groupées en 30 relais. Pour une variable qui ne varie **qu'entre** relais (comme `urbain`), l'information ne vient que de 30 unités, pas de 484 : la mise en commun totale **sous-estime fortement** son incertitude. Nous le démontrons par simulation plus bas (1.7.6).

Le **pas de mise en commun** a l'inconvénient inverse : il ne peut pas estimer l'effet d'une variable de niveau groupe (`urbain`), et il estime très mal le niveau d'un petit relais (4 commandes) : l'estimation est trop bruitée.

### 1.7.3 Le modèle à intercept aléatoire

Le **modèle mixte à intercept aléatoire** s'écrit

$$y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_{j}+\varepsilon_{ij},\qquad u_j\sim\mathcal N(0,\tau^2),\quad\varepsilon_{ij}\sim\mathcal N(0,\sigma^2),$$

les $u_j$ et les $\varepsilon_{ij}$ étant indépendants. Les $\boldsymbol\beta$ sont les **effets fixes** (communs à tous), les $u_j$ des **effets aléatoires**. Deux paramètres de variance : $\tau^2$ (variance **entre** relais) et $\sigma^2$ (variance **à l'intérieur** d'un relais).

> 📐 **Ce que cela implique pour les observations.** Pour deux commandes $i\ne i'$ du **même** relais, $\operatorname{Cov}(y_{ij},y_{i'j})=\operatorname{Var}(u_j)=\tau^2$ : elles sont **corrélées**, avec une corrélation
> $$\rho=\frac{\tau^2}{\tau^2+\sigma^2}\qquad\text{(coefficient de corrélation intraclasse, ICC).}$$
> Pour deux commandes de relais différents, la covariance est nulle. Le vecteur des commandes d'un relais de $n_j$ commandes a donc pour matrice de variance $\mathbf V_j=\sigma^2\mathbf I+\tau^2\mathbf 1\mathbf 1^\top$ (« symétrie composée »). Par conséquent, la **variance de la moyenne** de $n_j$ commandes est $\tau^2+\sigma^2/n_j$, et non $\sigma^2/n_j$ : *il y a un plancher*, $\tau^2$, que l'on ne peut jamais dépasser en ajoutant des commandes dans un même relais. L'**effectif effectif** d'un échantillon de $m$ commandes par groupe est $m/(1+(m-1)\rho)$ (« effet de plan »).

**L'ICC répond à la question « les groupes comptent-ils ? ».** Comparons deux situations. D'abord un cas où la réponse est **non** : les clients de la boutique sont répartis en six **villes**. Le panier dépend-il de la ville, au-delà de l'âge et du canal ?


L'ICC est estimé à **0** (la variance entre villes est estimée au bord de l'espace des paramètres : exactement 0) : une fois l'âge et le canal pris en compte, la ville n'explique rien du panier. Le modèle mixte aurait ici été superflu, et nos analyses des sections précédentes (sans effet de ville) étaient légitimes. Retenons que **regrouper n'implique pas toujours une dépendance** : le modèle mixte est un outil à utiliser quand l'ICC est notable.

Pour les points relais, la situation est tout autre. Un modèle mixte à intercept aléatoire s'ajuste en une ligne avec `statsmodels` (`groups` désigne la variable de regroupement) :

```python
m_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=True)
print(m_ri.summary().tables[1])
```
<!--sortie-->
```text
            Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept  12.489    0.364   34.284  0.000  11.775  13.202
dc         -0.710    0.034  -21.047  0.000  -0.776  -0.644
urbain      0.377    0.534    0.705  0.481  -0.671   1.424
Group Var   1.711    0.280                                
```


La dernière ligne de la sortie (cachée) donne l'ICC : 0,282. Plus du quart (28 %) de la variance résiduelle des notes est **entre relais** : deux commandes du même relais sont corrélées (corrélation ≈ 0,28). Avec 16 commandes par relais en moyenne, l'**effet de plan** est considérable : $1+(m-1)\rho\approx1+15\times0{,}28\approx5{,}2$ : pour une variable qui ne varie qu'entre relais, les 484 commandes **valent environ 484/5 ≈ 93 observations indépendantes**. Remarquez le résultat sur `urbain` : sa erreur standard est de 0,534 avec le modèle mixte, contre 0,224 pour la régression ordinaire du 1.7.2, soit **2,4 fois plus**. L'intervalle de confiance ordinaire (de 0,04 à 0,92) **exclut** zéro et laisse croire à un effet « significatif » ; l'intervalle mixte (de −0,67 à 1,42) **ne l'exclut pas**. C'est l'effet de plan en action : les 484 commandes n'apportent, sur le type de relais, que l'information de 30 relais.

**Comment estime-t-on ce modèle ? La méthode REML.** La variance de $\hat{\boldsymbol\beta}$ dépend de $\mathbf V=\operatorname{diag}(\mathbf V_j)$, qui dépend de $\tau^2$ et $\sigma^2$, inconnus. Étant donné $\mathbf V$, l'estimateur des effets fixes est celui des **moindres carrés généralisés** (qui pondère selon la fiabilité de chaque observation)

$$\hat{\boldsymbol\beta}=\big(\mathbf X^\top\mathbf V^{-1}\mathbf X\big)^{-1}\mathbf X^\top\mathbf V^{-1}\mathbf y .$$

Les paramètres de variance sont estimés par maximum de vraisemblance, mais la version « classique » **sous-estime** les variances (comme la division par $n$ au lieu de $n-p$, 1.1.5) : on lui préfère la **vraisemblance restreinte (REML)**, qui maximise la vraisemblance des **résidus** (les combinaisons des données indépendantes des effets fixes) et corrige ce biais. `statsmodels` (`reml=True`, par défaut) et R (`lme4`) utilisent la REML.

### 1.7.4 La mise en commun partielle : le rétrécissement

Le grand intérêt du modèle mixte est ce qu'il fait des **niveaux des groupes**. Une fois les effets fixes estimés, on prédit l'effet aléatoire $u_j$ de chaque relais par le **meilleur prédicteur linéaire sans biais (BLUP)**.

> 📐 **Le BLUP est une moyenne rétrécie.** Soit $\bar r_j$ la moyenne, pour le relais $j$, des résidus « fixes » $r_{ij}=y_{ij}-\mathbf x_{ij}^\top\hat{\boldsymbol\beta}$ (c'est l'estimation « sans mise en commun » du niveau de base du relais). Le BLUP est
> $$\hat u_j=\underbrace{\frac{\tau^2}{\tau^2+\sigma^2/n_j}}_{B_j\in(0,1)}\ \bar r_j .$$
> *Démonstration.* Pour un groupe de $n_j$ observations, $\mathbf V_j=\sigma^2\mathbf I+\tau^2\mathbf 1\mathbf 1^\top$ vérifie $\mathbf V_j\mathbf 1=(\sigma^2+n_j\tau^2)\mathbf 1$, donc $\mathbf V_j^{-1}\mathbf 1=\mathbf 1/(\sigma^2+n_j\tau^2)$. Le BLUP est $\hat u_j=\tau^2\,\mathbf 1^\top\mathbf V_j^{-1}\mathbf r_j=\tau^2\,\dfrac{n_j\bar r_j}{\sigma^2+n_j\tau^2}=\dfrac{\tau^2}{\tau^2+\sigma^2/n_j}\,\bar r_j$. $\square$
>
> Le facteur $B_j$ est la **fiabilité** de la moyenne du groupe. Pour un **grand** groupe ($n_j\to\infty$), $B_j\to1$ : on fait confiance à sa moyenne. Pour un **petit** groupe, $B_j$ est petit : sa moyenne est bruitée, on la **rapproche de la moyenne générale** (0). C'est un compromis entre « ce relais est unique » ($B_j=1$, pas de mise en commun) et « tous les relais sont pareils » ($B_j=0$, mise en commun totale).

La formule reproduit exactement les prédictions de `statsmodels`. Comparons maintenant les deux estimations à la **vérité**, que nous connaissons ici (les vrais $u_{0j}$) : l'erreur quadratique moyenne vaut 0,900 sans mise en commun et 0,765 avec mise en commun partielle ; pour les dix relais de 8 commandes ou moins, 1,273 contre 1,031.


L'erreur par rapport aux **vrais** niveaux est donc plus faible avec la mise en commun partielle, et le gain est **le plus net pour les petits relais**, dont l'estimation individuelle était la plus bruitée. Voyons le mécanisme sur un graphique : pour chaque relais (classés par taille), on relie son estimation « sans mise en commun » à son estimation rétrécie.


![Niveau de base de chacun des 30 relais, classés par nombre de commandes. Les cercles orange sont les moyennes de chaque relais, les points bleus leurs versions rétrécies par le modèle mixte, les traits noirs la vérité. Les segments gris relient les deux estimations. Le rétrécissement est fort pour les petits relais (à gauche) et faible pour les grands (à droite).](figures/ch01-retrecissement.png)

Le dessin raconte l'idée centrale. À gauche, les **petits** relais (4 à 8 commandes) : leur moyenne brute (cercle orange) est très variable, parfois extrême ; le modèle la **ramène nettement vers 0** (point bleu), ce qui la rapproche souvent de la vérité (trait noir). À droite, les **grands** relais : l'estimation brute est déjà fiable et le rétrécissement est faible. Ce principe, **« emprunter de la force aux autres groupes »**, est l'un des plus puissants de la statistique moderne : on le retrouvera dans le cadre bayésien (chapitre 6, avec la loi *a priori* $u_j\sim\mathcal N(0,\tau^2)$).

### 1.7.5 Pente aléatoire : chaque relais a sa propre sensibilité au retard

Jusqu'ici, tous les relais partagent la même pente (−0,7 point par jour de retard, en moyenne). Mais les vraies données ont été produites avec une **pente propre à chaque relais** ($u_{1j}$). On l'inclut par une **pente aléatoire** : $y_{ij}=\beta_0+\beta_1x_{ij}+\dots+u_{0j}+u_{1j}x_{ij}+\varepsilon_{ij}$, où le couple $(u_{0j},u_{1j})$ est tiré d'une loi normale bidimensionnelle de matrice de covariance $\mathbf G$.


Les composantes de variance sont raisonnablement proches des vraies valeurs, compte tenu du petit nombre de relais : l'écart-type des niveaux de base est estimé à 1,19 (vrai : 1,6, mais **réalisé** : 1,31 : l'estimation colle à ce qui a effectivement été tiré), celui des pentes à 0,28 (vrai : 0,3), l'écart-type résiduel à 1,93 (vrai : 1,8). La corrélation estimée niveau/pente (0,21), alors que la vraie est nulle, est du bruit d'échantillonnage (son erreur est large avec 30 relais). Les **effets fixes** sont bien retrouvés pour le délai : −0,76 point par jour (vrai : −0,7, intervalle [−0,89 ; −0,63]) ; en revanche l'effet « urbain » est estimé à 0,28 avec une erreur standard de 0,50 : **positif mais très imprécis** (la vraie valeur, 1,2, est à moins de deux erreurs standard). Avec 30 relais, on ne peut tout simplement pas mesurer un effet de niveau groupe de cette taille avec précision.

**Comparer les deux modèles par un test du rapport de vraisemblance.** Les modèles à intercept aléatoire seul et à intercept + pente aléatoire sont emboîtés. On compare leurs vraisemblances. Comme les deux modèles ont les **mêmes effets fixes**, la REML conviendrait aussi ; l'usage prudent, que nous suivons, est de comparer les modèles ajustés par **maximum de vraisemblance** (ML), car la vraisemblance REML ne se compare pas entre modèles d'effets fixes différents.


On trouve des log-vraisemblances de −1 067,99 (intercept aléatoire) et −1 047,41 (intercept et pente aléatoires), donc $\text{LR}=41{,}15$ et une p-valeur de $6{,}5\times10^{-10}$ (mélange de $\chi^2$) : la pente aléatoire est très nettement justifiée ; l'AIC (2 108,8 contre 2 146,0) conclut de même.

> ⚠️ **Un piège de l'optimisation.** En préparant ce bloc, la même ligne ajustée avec `method="lbfgs"` (l'optimiseur que nous avions utilisé pour la pente aléatoire) a renvoyé une log-vraisemblance **infinie** pour le modèle à intercept aléatoire, sans la moindre erreur : l'optimiseur avait convergé vers une solution dégénérée (variance entre groupes égale à 0). Avec l'optimiseur par défaut, ou avec `bfgs`, on obtient −1067,99, la valeur que donne aussi `lme4`. **Un optimiseur peut échouer en silence.** Vérifiez toujours qu'un ajustement est plausible (log-vraisemblance finie, variances raisonnables) et, dans le doute, comparez deux optimiseurs ou le résultat de `lme4`.

> ⚠️ **Un piège du test.** Tester qu'une **variance** est nulle ($H_0:\tau_1^2=0$) place l'hypothèse nulle **au bord** de l'espace des paramètres (une variance est $\ge0$) : la loi du rapport de vraisemblance n'est pas un simple $\chi^2$ mais un **mélange** de $\chi^2$ (ici 50/50 entre $\chi^2_1$ et $\chi^2_2$). Utiliser un $\chi^2_2$ naïf est **conservateur** (p-valeur trop grande).

Visualisons maintenant le résultat : les droites de **chaque relais** (prédites avec leurs effets aléatoires), autour de la droite moyenne.


![Droites de régression propres à chaque relais (orange : urbains, vert : non urbains) autour de l'effet moyen (noir). Les relais diffèrent par leur niveau de base (décalage vertical) et par leur sensibilité au retard (pente).](figures/ch01-droites-par-relais.png)

**Les mêmes résultats en R avec `lme4`.** Le paquet `lme4` est la référence pour ces modèles. Un bloc R (visible dans les sources du chapitre) relit le fichier `donnees/ch01-relais.csv` et ajuste le même modèle ; il donne exactement les mêmes nombres que `statsmodels` : effets fixes 12,596 ; −0,760 ; 0,277, écarts-types 1,195 (niveau de base) et 0,281 (pente), corrélation 0,21 et écart-type résiduel 1,930.


### 1.7.6 Pourquoi ignorer les groupes est dangereux : une simulation

Terminons par la démonstration promise : l'effet d'ignorer la structure de groupes sur la fiabilité des tests. Prenons les **mêmes** tailles de relais et la même variance entre relais, mais supposons que le type de relais (urbain ou non) n'a **aucun effet** réel. Un bon test doit alors rejeter l'hypothèse « aucun effet » dans **5 %** des cas. Combien rejettent-ils réellement ? On répète 300 fois.


La régression ordinaire, qui ignore le groupage, déclare un effet « significatif » dans **plus de la moitié** des simulations alors qu'il n'y a **aucun effet** : plus de dix fois le taux nominal de 5 %. C'est la conséquence directe de l'effet de plan : des **faux positifs en rafale**. Le modèle mixte, lui, se tient près du niveau nominal (un peu au-dessus de 5 %, ce qui est attendu : l'approximation de Wald est légèrement optimiste avec seulement 30 groupes) ; sa statistique $z$ a un écart-type voisin de 1, et sa variance entre relais est estimée sans biais notable. Voilà pourquoi, dès que les données sont groupées, **les erreurs standard ordinaires ne sont pas fiables pour les variables de niveau groupe**.

La dernière ligne de la sortie confirme l'avertissement du 1.7.5 : avec l'optimiseur `lbfgs`, la plupart des ajustements de ce modèle pourtant simple dégénèrent (43 sur 60 : la variance entre relais est estimée à 0, ce qui fausse tout), alors que l'optimiseur par défaut ne dégénère jamais (0 sur 60). Un résultat qui paraît plausible peut être faux : c'est pourquoi nous avons systématiquement comparé aux valeurs de `lme4`.

> ⚠️ **Précautions.**
> - **Peu de groupes** (moins de 5 à 10) : les variances entre groupes sont très mal estimées, et les approximations de Wald des effets fixes sont trop optimistes. Dans ce cas, envisagez de traiter le groupe comme un effet **fixe** (une indicatrice par groupe) ou une approche bayésienne.
> - **Effets fixes ou aléatoires ?** Traiter les groupes comme **aléatoires** est pertinent si l'on veut généraliser à d'autres groupes de la même population (les 30 relais sont un échantillon des relais possibles) et si les groupes sont nombreux. Si les groupes sont **tous** ceux qui existent (les 6 villes) et peu nombreux, des effets fixes suffisent.
> - **Convergence** : l'optimisation de ces modèles est parfois délicate (variances proches de 0, corrélations proches de ±1). Essayez un autre optimiseur (`method="bfgs"`, `"powell"`…), simplifiez la structure aléatoire, ou comparez à `lme4`.
> - **Interprétation** : les effets fixes sont des effets **moyens** dans la population de groupes ; les effets aléatoires sont des **écarts** propres à chaque groupe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.12, exercice 1.12.

> ✅ **À retenir (1.7).**
> - Des observations **groupées** (clients d'une même ville, commandes d'un même relais) ne sont pas indépendantes ; l'ignorer rend les **erreurs standard trop petites**, surtout pour les variables de niveau groupe.
> - Le **modèle mixte** ajoute des **effets aléatoires** : $y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_j+\varepsilon_{ij}$, $u_j\sim\mathcal N(0,\tau^2)$. L'**ICC** $=\tau^2/(\tau^2+\sigma^2)$ mesure la part de variance due aux groupes (elle était nulle pour les villes, notable pour les relais).
> - Les effets aléatoires sont prédits par **rétrécissement** : $\hat u_j=\frac{\tau^2}{\tau^2+\sigma^2/n_j}\bar r_j$. Les petits groupes sont davantage ramenés vers la moyenne : c'est la **mise en commun partielle**, qui bat à la fois « tous pareils » et « tous différents ».
> - On peut ajouter des **pentes aléatoires**. Les paramètres se comparent par un test du rapport de vraisemblance (**attention** à la loi limite au bord de l'espace des paramètres) ; l'estimation se fait par **REML**.
> - `statsmodels.MixedLM` et `lme4` en R donnent les mêmes résultats.


## Bilan du chapitre 1

Vous savez maintenant :

- **écrire et résoudre** un modèle linéaire $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ par les équations normales, comprendre pourquoi la solution est une **projection orthogonale** et démontrer le théorème de **Gauss-Markov** ;
- **interpréter** les coefficients (variables qualitatives par indicatrices, « toutes choses égales par ailleurs », modèles en logarithmes, rétro-transformation pour prédire une moyenne) ;
- **faire de l'inférence** : erreurs standard, tests $t$ et $F$ de modèles emboîtés, intervalles de confiance et de **prédiction**, bootstrap des couples, en sachant sous quelles hypothèses ils sont valables ;
- **poser un diagnostic** : graphiques de résidus, tests de Breusch-Pagan et de Durbin-Watson, **levier** et **distance de Cook**, **VIF**, erreurs standard robustes, et savoir remédier aux défauts (transformer, centrer, changer de modèle) ;
- **choisir un modèle** sans tricher : AIC, BIC, validation croisée (PRESS), tests emboîtés, et se méfier de la sélection automatique ;
- (en option) **régulariser** (Ridge, Lasso, Elastic Net) quand les variables sont nombreuses, **résister** aux aberrations (Huber, régression quantile) et **modéliser des données groupées** (effets mixtes, rétrécissement).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : les applications 1.1 à 1.12 et les exercices corrigés 1.1 à 1.13 reprennent, dans l'ordre du chapitre, tout ce qui est à pratiquer.

Le chapitre 2 généralise la régression à des réponses qui ne sont **ni continues ni normales** : un client rachète-t-il (oui/non) ? combien de commandes passe-t-il (un entier) ? C'est le cadre des **modèles linéaires généralisés**, dont la régression linéaire de ce chapitre est le cas particulier le plus simple.
