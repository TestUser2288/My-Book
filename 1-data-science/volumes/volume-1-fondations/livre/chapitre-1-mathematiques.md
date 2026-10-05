# Chapitre 1 : Mathématiques pour la data science

> « Un tableau de données, c'est une **matrice**.
> Un modèle, c'est une **fonction**.
> Apprendre, c'est **minimiser une erreur**. »

Ces trois phrases résument ce chapitre. Si elles vous paraissent mystérieuses, c'est normal : à la fin du chapitre, elles vous sembleront évidentes.

## Pourquoi des mathématiques ?

On entend parfois que « la data science, ce sont des bibliothèques Python : on appelle `fit()` et c'est fini ». C'est vrai… jusqu'au jour où le modèle donne un résultat absurde et où l'on doit comprendre pourquoi. Les mathématiques sont ce qui permet alors de **raisonner au lieu de deviner**.

Rassurez-vous : il ne s'agit pas de refaire un cursus de mathématiques. Il suffit de **quatre familles d'idées**, que nous construirons de zéro :

| Idée | Ce que c'est | À quoi ça sert en data science |
|---|---|---|
| **Vecteurs et matrices** | des listes et des tableaux de nombres, avec des règles de calcul | représenter les données, comparer des individus, réduire la dimension |
| **Dérivées et gradients** | la mesure de « à quelle vitesse ça change » | savoir dans quel sens améliorer un modèle |
| **Intégrales** | la mesure d'une « quantité accumulée » | calculer des probabilités (chapitre 2) |
| **Optimisation** | trouver le meilleur choix selon un critère | entraîner (presque) tous les modèles |

## Le chemin de ce chapitre

Nous allons suivre la boutique **Dar Jasmin** et ses questions concrètes :

- **1.1 Algèbre linéaire** : Yasmine veut savoir quels clients se ressemblent, calculer son chiffre d'affaires par mois sans boucle interminable, et résumer un tableau de ventes en quelques tendances.
- **1.2 Analyse** : comment son bénéfice change-t-il quand elle modifie un prix un tout petit peu ? Et quelle est la probabilité qu'une commande arrive dans les trois prochaines minutes ?
- **1.3 Optimisation** : quel prix maximise ses recettes ? Comment répartir son budget publicitaire ?
- **1.4 Fiche de notations** : toutes les notations du livre, au même endroit.
- ➕ **Pour aller plus loin** : pourquoi l'ordinateur se trompe parfois (analyse numérique), et comment compter et relier des objets (mathématiques discrètes et graphes).

> 💡 **Comment lire ce chapitre.** Chaque notion suit le même rythme : une intuition, un exemple chiffré à la main, puis (si nécessaire) une démonstration, puis le code. Si une démonstration vous décourage, sautez-la : l'exemple et le code suffisent pour avancer. Revenez-y plus tard.


## 1.1 Algèbre linéaire

L'algèbre linéaire est le langage des tableaux de nombres. Tout ce que fait un modèle de data science, de la régression la plus simple au réseau de neurones le plus profond, s'écrit avec elle. Nous allons en construire les quatre briques : **vecteurs**, **matrices**, **valeurs propres** et **décomposition en valeurs singulières**.

### 1.1.1 Vecteurs : décrire un client par une liste de nombres

> 💡 **Intuition.** Un **vecteur** est une liste ordonnée de nombres. On peut le voir de deux façons, qui sont les deux faces d'une même pièce :
>
> - comme une **flèche** partant de l'origine et pointant vers un point ;
> - comme la **fiche d'identité** d'un individu : une ligne de tableau où chaque case décrit une caractéristique.
>
> En data science, la seconde vision est la plus utile : *un individu = un vecteur*.

#### Un exemple concret

Dar Jasmin compte, pour chaque client, le nombre d'achats dans trois catégories : **poteries**, **huile d'olive**, **bijoux**. Chaque client devient un vecteur à trois composantes :

| Client | Poteries | Huile | Bijoux | Vecteur |
|---|---|---|---|---|
| Amel | 3 | 1 | 0 | $\mathbf{a} = (3, 1, 0)$ |
| Bilel | 6 | 2 | 0 | $\mathbf{b} = (6, 2, 0)$ |
| Chaima | 0 | 1 | 4 | $\mathbf{c} = (0, 1, 4)$ |

On note $\mathbf{a} = (a_1, a_2, \dots, a_p)$ un vecteur à $p$ composantes, et $\mathbb{R}^p$ l'ensemble de tous les vecteurs à $p$ composantes réelles. Ici $p = 3$ : nos clients vivent dans $\mathbb{R}^3$.

> ✅ **Convention du livre.** Un nombre seul (un *scalaire*) s'écrit en italique : $a$, $\lambda$. Un vecteur s'écrit en gras minuscule : $\mathbf{a}$. Une matrice s'écrit en gras majuscule : $\mathbf{A}$.

#### Les opérations de base

**Addition.** On additionne composante par composante. Si Amel et Chaima regroupent leurs achats :

$$\mathbf{a} + \mathbf{c} = (3+0,\; 1+1,\; 0+4) = (3, 2, 4).$$

**Multiplication par un scalaire.** On multiplie chaque composante :

$$2\,\mathbf{a} = (2 \times 3,\; 2 \times 1,\; 2 \times 0) = (6, 2, 0) = \mathbf{b}.$$

Regardez bien : **Bilel est exactement « deux fois Amel »**. Il achète les mêmes choses dans les mêmes proportions, simplement en plus grande quantité. Nous allons voir comment la mathématique capture cette idée.

**Combinaison linéaire.** Combiner les deux opérations donne une *combinaison linéaire* : $\lambda_1 \mathbf{u}_1 + \lambda_2 \mathbf{u}_2$. Par exemple, « la moitié d'Amel plus un tiers de Chaima » est $\tfrac12 \mathbf{a} + \tfrac13 \mathbf{c}$. Presque tout ce que nous ferons en modélisation est une combinaison linéaire de quelque chose.

En Python, la bibliothèque **NumPy** manipule les vecteurs comme des objets à part entière :

```python
import numpy as np

amel   = np.array([3, 1, 0])
bilel  = np.array([6, 2, 0])
chaima = np.array([0, 1, 4])

print("Amel + Chaima :", amel + chaima)
print("2 x Amel      :", 2 * amel)
print("Bilel == 2 x Amel ?", np.array_equal(bilel, 2 * amel))
```
<!--sortie-->
```text
Amel + Chaima : [3 2 4]
2 x Amel      : [6 2 0]
Bilel == 2 x Amel ? True
```

#### Le produit scalaire : mesurer l'accord entre deux vecteurs

Le **produit scalaire** de deux vecteurs de même taille est la somme des produits des composantes :

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{p} a_i b_i = a_1 b_1 + a_2 b_2 + \dots + a_p b_p.$$

> 🧪 **Exemple à la main.**
>
> $\mathbf{a} \cdot \mathbf{b} = 3 \times 6 + 1 \times 2 + 0 \times 0 = 18 + 2 + 0 = 20.$
>
> $\mathbf{a} \cdot \mathbf{c} = 3 \times 0 + 1 \times 1 + 0 \times 4 = 0 + 1 + 0 = 1.$

> 💡 **Intuition.** Le produit scalaire est grand quand les deux vecteurs « vont dans le même sens » (ils ont des composantes fortes aux mêmes endroits), proche de 0 quand ils n'ont rien en commun, et négatif quand ils s'opposent. Amel et Bilel s'entendent bien (20) ; Amel et Chaima presque pas (1) : le seul point commun est une unité d'huile.

La **norme** d'un vecteur est sa longueur, donnée par le théorème de Pythagore généralisé :

$$\|\mathbf{a}\| = \sqrt{\mathbf{a} \cdot \mathbf{a}} = \sqrt{a_1^2 + a_2^2 + \dots + a_p^2}.$$

Pour nos clients : $\|\mathbf{a}\| = \sqrt{9 + 1 + 0} = \sqrt{10} \approx 3{,}162$, $\|\mathbf{b}\| = \sqrt{36 + 4} = \sqrt{40} \approx 6{,}325$ et $\|\mathbf{c}\| = \sqrt{0 + 1 + 16} = \sqrt{17} \approx 4{,}123$. On remarque que $\|\mathbf{b}\| = 2\|\mathbf{a}\|$ : doubler un vecteur double sa longueur.

Le produit scalaire a aussi une **interprétation géométrique** qui est fondamentale :

$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\|\,\|\mathbf{b}\|\cos\theta,$$

où $\theta$ est l'angle entre les deux flèches. En isolant le cosinus, on obtient la **similarité cosinus** :

$$\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\|\,\|\mathbf{b}\|}.$$

> 🧪 **Exemple à la main.**
>
> - Amel et Bilel : $\cos\theta = \dfrac{20}{\sqrt{10}\,\sqrt{40}} = \dfrac{20}{\sqrt{400}} = \dfrac{20}{20} = 1$. Même direction : **mêmes goûts**.
> - Amel et Chaima : $\cos\theta = \dfrac{1}{\sqrt{10}\,\sqrt{17}} = \dfrac{1}{\sqrt{170}} \approx 0{,}077$. Presque perpendiculaires : **goûts très différents**.

La similarité cosinus ignore la *taille* des vecteurs et ne regarde que leur *direction*. C'est exactement ce que l'on veut pour comparer des profils d'achat : un gros acheteur et un petit acheteur qui ont les mêmes goûts doivent apparaître comme semblables.

```python
def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("cos(Amel, Bilel)  =", round(cosinus(amel, bilel), 4))
print("cos(Amel, Chaima) =", round(cosinus(amel, chaima), 4))
```
<!--sortie-->
```text
cos(Amel, Bilel)  = 1.0
cos(Amel, Chaima) = 0.0767
```

> 📐 **Démonstration : pourquoi le cosinus reste toujours entre −1 et 1.**
>
> Il faut montrer que $|\mathbf{a}\cdot\mathbf{b}| \le \|\mathbf{a}\|\,\|\mathbf{b}\|$. C'est l'**inégalité de Cauchy-Schwarz**. Supposons $\mathbf{b} \neq \mathbf{0}$ et considérons, pour un réel $t$ quelconque, la quantité
>
> $$q(t) = \|\mathbf{a} - t\,\mathbf{b}\|^2 = \|\mathbf{a}\|^2 - 2t\,(\mathbf{a}\cdot\mathbf{b}) + t^2 \|\mathbf{b}\|^2.$$
>
> Une norme au carré est toujours positive ou nulle, donc $q(t) \ge 0$ **pour tout** $t$. Or $q$ est un trinôme du second degré en $t$ ; pour qu'il ne prenne jamais de valeur négative, son discriminant doit être négatif ou nul :
>
> $$\Delta = 4(\mathbf{a}\cdot\mathbf{b})^2 - 4\|\mathbf{a}\|^2\|\mathbf{b}\|^2 \le 0 \;\Longleftrightarrow\; (\mathbf{a}\cdot\mathbf{b})^2 \le \|\mathbf{a}\|^2\|\mathbf{b}\|^2.$$
>
> En prenant la racine carrée, $|\mathbf{a}\cdot\mathbf{b}| \le \|\mathbf{a}\|\,\|\mathbf{b}\|$, donc $-1 \le \cos\theta \le 1$. $\blacksquare$
>
> L'égalité (cosinus égal à ±1) a lieu exactement quand le discriminant est nul, c'est-à-dire quand il existe un $t$ tel que $\mathbf{a} = t\,\mathbf{b}$ : les deux vecteurs sont alignés. C'est le cas d'Amel et Bilel.

#### La distance entre deux vecteurs

La **distance euclidienne** entre deux individus est la norme de leur différence :

$$d(\mathbf{a}, \mathbf{b}) = \|\mathbf{a} - \mathbf{b}\| = \sqrt{\sum_{i=1}^{p}(a_i - b_i)^2}.$$

> 🧪 **Exemple.**
>
> - $d(\mathbf{a}, \mathbf{b}) = \|(3-6,\, 1-2,\, 0-0)\| = \|(-3, -1, 0)\| = \sqrt{10} \approx 3{,}162.$
> - $d(\mathbf{a}, \mathbf{c}) = \|(3-0,\, 1-1,\, 0-4)\| = \|(3, 0, -4)\| = \sqrt{9 + 0 + 16} = 5.$

```python
print("distance(Amel, Bilel)  =", round(np.linalg.norm(amel - bilel), 3))
print("distance(Amel, Chaima) =", round(np.linalg.norm(amel - chaima), 3))
```
<!--sortie-->
```text
distance(Amel, Bilel)  = 3.162
distance(Amel, Chaima) = 5.0
```

Remarquez la nuance. Selon le **cosinus**, Amel et Bilel sont *identiques* (1) ; selon la **distance**, ils sont *à 3,16 unités l'un de l'autre*, parce que Bilel achète plus. Ni l'une ni l'autre mesure n'est « la bonne » : elles répondent à des questions différentes.

| Mesure | Elle répond à… | À utiliser quand… |
|---|---|---|
| **Cosinus** | « Ont-ils les mêmes goûts ? » | seule la *proportion* compte (profils, textes, recommandations) |
| **Distance** | « Sont-ils proches en valeur absolue ? » | la *quantité* compte (regroupement par niveau de dépense, par exemple) |

> ⚠️ **Piège : les unités.** La distance additionne des carrés de différences, donc une variable exprimée en grands nombres écrase les autres. Soit trois clients décrits par (âge, panier moyen en DT) : $P = (30,\; 100)$, $Q = (60,\; 102)$ et $R = (31,\; 160)$.
>
> - $d(P, Q) = \sqrt{30^2 + 2^2} = \sqrt{904} \approx 30{,}1$
> - $d(P, R) = \sqrt{1^2 + 60^2} = \sqrt{3601} \approx 60{,}0$
>
> Selon la distance, $P$ (30 ans) ressemble davantage à $Q$ (60 ans) qu'à $R$ (31 ans), simplement parce que 60 dinars « pèsent » plus que 30 ans dans le calcul ! La cause : les deux variables n'ont pas la même échelle. Le remède est de **standardiser** les variables avant de les comparer, ce que nous ferons au chapitre 3.

> ✅ **À retenir (vecteurs).**
>
> - Un individu est un vecteur ; ses composantes sont ses caractéristiques.
> - Le produit scalaire $\sum a_i b_i$ mesure l'accord entre deux vecteurs ; la norme mesure leur longueur.
> - Le cosinus compare les **directions**, la distance compare les **positions**. Toujours se demander laquelle des deux correspond à la question posée.
> - Avant de comparer des variables d'échelles différentes, on les standardise.


### 1.1.2 Matrices : le tableau de données devient un objet mathématique

> 💡 **Intuition.** Une **matrice** est un tableau rectangulaire de nombres, rangés en lignes et en colonnes. Si un vecteur est « un individu », une matrice est « **tous les individus à la fois** » : chaque ligne est un individu, chaque colonne est une variable. Un fichier de données, c'est une matrice.

On note $\mathbf{A} \in \mathbb{R}^{n \times p}$ une matrice à $n$ lignes et $p$ colonnes (on dit « $n$ par $p$ »), et $a_{ij}$ le nombre situé à la ligne $i$ et à la colonne $j$. Une matrice carrée a autant de lignes que de colonnes ($n = p$).

#### Un exemple concret

Yasmine a noté ses ventes des trois premiers mois pour trois produits (poteries, huile, bijoux). Chaque **ligne** est un mois, chaque **colonne** un produit :

$$\mathbf{V} = \begin{pmatrix} 10 & 40 & 20 \\ 12 & 35 & 25 \\ 15 & 50 & 18 \end{pmatrix} \begin{array}{l} \leftarrow \text{janvier} \\ \leftarrow \text{février} \\ \leftarrow \text{mars} \end{array}$$

Les prix unitaires sont $\mathbf{p} = (45,\; 12,\; 30)$ dinars. Question : quel est le chiffre d'affaires de chaque mois ?

#### Le produit matrice-vecteur

Pour janvier, c'est un produit scalaire : $10 \times 45 + 40 \times 12 + 20 \times 30 = 450 + 480 + 600 = 1\,530$ DT. On fait de même pour février et mars. Calculer ces trois produits scalaires d'un coup, c'est ce qu'on appelle le **produit matrice-vecteur** $\mathbf{V}\mathbf{p}$ :

$$\mathbf{V}\mathbf{p} = \begin{pmatrix} 10\cdot 45 + 40\cdot 12 + 20\cdot 30 \\ 12\cdot 45 + 35\cdot 12 + 25\cdot 30 \\ 15\cdot 45 + 50\cdot 12 + 18\cdot 30 \end{pmatrix} = \begin{pmatrix} 1530 \\ 1710 \\ 1815 \end{pmatrix}.$$

Formellement, $(\mathbf{V}\mathbf{p})_i = \sum_j v_{ij}\, p_j$ : la composante $i$ du résultat est le produit scalaire de la **ligne $i$** de $\mathbf{V}$ avec $\mathbf{p}$.

> 💡 **Une seconde lecture, tout aussi utile.** On peut aussi voir $\mathbf{V}\mathbf{p}$ comme une **combinaison linéaire des colonnes** de $\mathbf{V}$ :
>
> $$\mathbf{V}\mathbf{p} = 45 \begin{pmatrix}10\\12\\15\end{pmatrix} + 12 \begin{pmatrix}40\\35\\50\end{pmatrix} + 30 \begin{pmatrix}20\\25\\18\end{pmatrix}.$$
>
> Le chiffre d'affaires est « 45 fois les ventes de poteries, plus 12 fois les ventes d'huile, plus 30 fois les ventes de bijoux ». C'est exactement ce que fait une régression linéaire : un mélange pondéré de colonnes.

```python
import numpy as np

V = np.array([[10, 40, 20],    # janvier : poteries, huile, bijoux
              [12, 35, 25],    # février
              [15, 50, 18]])   # mars
prix = np.array([45, 12, 30])

print("Forme de V  :", V.shape)
print("CA par mois :", V @ prix)
```
<!--sortie-->
```text
Forme de V  : (3, 3)
CA par mois : [1530 1710 1815]
```

L'opérateur `@` est le produit matriciel de Python. Il évite d'écrire une boucle.

#### Le produit matrice-matrice

Et si Yasmine veut comparer deux grilles de prix : les prix actuels et les prix augmentés de 10 % ? On met les deux grilles côte à côte dans une matrice $\mathbf{P}$ (une colonne par scénario) et on calcule $\mathbf{V}\mathbf{P}$.

**Règle de calcul.** Le produit de $\mathbf{A} \in \mathbb{R}^{n\times p}$ par $\mathbf{B} \in \mathbb{R}^{p \times q}$ est la matrice $\mathbf{C} = \mathbf{A}\mathbf{B} \in \mathbb{R}^{n \times q}$ dont l'élément $(i, j)$ est le produit scalaire de la **ligne $i$** de $\mathbf{A}$ avec la **colonne $j$** de $\mathbf{B}$ :

$$c_{ij} = \sum_{k=1}^{p} a_{ik}\, b_{kj}.$$

> ⚠️ **Règle d'or des dimensions.** Pour multiplier, le **nombre de colonnes de $\mathbf{A}$ doit égaler le nombre de lignes de $\mathbf{B}$** : $(n \times \mathbf{p})(\mathbf{p} \times q) \to (n \times q)$. Les deux $p$ « du milieu » doivent être identiques et disparaissent ; il reste $n \times q$. Quand un code plante avec une erreur de « forme » (*shape*), c'est presque toujours cette règle qui est violée.

```python
P = np.array([[45, 49.5],      # poteries : prix actuel, prix +10 %
              [12, 13.2],      # huile
              [30, 33.0]])     # bijoux
print(V @ P)
```
<!--sortie-->
```text
[[1530.  1683. ]
 [1710.  1881. ]
 [1815.  1996.5]]
```

Chaque ligne est un mois, chaque colonne un scénario. La deuxième colonne vaut 1,1 fois la première, comme attendu.

> ⚠️ **Piège : le produit matriciel n'est pas commutatif.** En général, $\mathbf{A}\mathbf{B} \neq \mathbf{B}\mathbf{A}$. Un petit exemple suffit à s'en convaincre :
>
> $$\mathbf{A} = \begin{pmatrix}1&2\\3&4\end{pmatrix}, \quad \mathbf{B} = \begin{pmatrix}0&1\\1&0\end{pmatrix}.$$
>
> Calcul de $\mathbf{A}\mathbf{B}$ : première ligne $(1\cdot 0 + 2\cdot 1,\; 1\cdot 1 + 2\cdot 0) = (2, 1)$ ; seconde ligne $(3\cdot 0 + 4 \cdot 1,\; 3\cdot 1 + 4\cdot 0) = (4, 3)$. Donc $\mathbf{A}\mathbf{B} = \begin{pmatrix}2&1\\4&3\end{pmatrix}$ : multiplier à droite par $\mathbf{B}$ **échange les colonnes** de $\mathbf{A}$.
>
> Calcul de $\mathbf{B}\mathbf{A}$ : on trouve $\begin{pmatrix}3&4\\1&2\end{pmatrix}$ : multiplier à gauche par $\mathbf{B}$ **échange les lignes** de $\mathbf{A}$. Les deux résultats sont différents.

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[0, 1], [1, 0]])
print("A @ B =\n", A @ B)
print("B @ A =\n", B @ A)
```
<!--sortie-->
```text
A @ B =
 [[2 1]
 [4 3]]
B @ A =
 [[3 4]
 [1 2]]
```

Ce que l'on garde, en revanche : le produit est **associatif** ($(\mathbf{A}\mathbf{B})\mathbf{C} = \mathbf{A}(\mathbf{B}\mathbf{C})$) et **distributif** ($\mathbf{A}(\mathbf{B}+\mathbf{C}) = \mathbf{A}\mathbf{B} + \mathbf{A}\mathbf{C}$).

#### La transposée

La **transposée** $\mathbf{A}^\top$ d'une matrice échange ses lignes et ses colonnes : $(\mathbf{A}^\top)_{ij} = a_{ji}$. Une matrice $3 \times 2$ devient une matrice $2 \times 3$. On a la règle $(\mathbf{A}\mathbf{B})^\top = \mathbf{B}^\top \mathbf{A}^\top$ (l'ordre s'inverse).

Pour un vecteur colonne $\mathbf{x}$, le nombre $\mathbf{x}^\top \mathbf{x} = \sum x_i^2 = \|\mathbf{x}\|^2$ est son carré de norme : le produit scalaire s'écrit donc $\mathbf{a}\cdot\mathbf{b} = \mathbf{a}^\top\mathbf{b}$. Vous croiserez cette écriture partout.

#### La matrice identité et l'inverse

La **matrice identité** $\mathbf{I}$ (des 1 sur la diagonale, des 0 ailleurs) est le « 1 » des matrices : $\mathbf{I}\mathbf{A} = \mathbf{A}\mathbf{I} = \mathbf{A}$.

L'**inverse** d'une matrice carrée $\mathbf{A}$, quand il existe, est la matrice $\mathbf{A}^{-1}$ telle que

$$\mathbf{A}\mathbf{A}^{-1} = \mathbf{A}^{-1}\mathbf{A} = \mathbf{I}.$$

C'est l'analogue de $a \times \frac{1}{a} = 1$. Pour une matrice $2 \times 2$, il existe une formule simple. Si $\mathbf{A} = \begin{pmatrix}a&b\\c&d\end{pmatrix}$, son **déterminant** est $\det\mathbf{A} = ad - bc$, et lorsque $\det \mathbf{A} \neq 0$ :

$$\mathbf{A}^{-1} = \frac{1}{ad - bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.$$

> 🧪 **Exemple.** Soit $\mathbf{A} = \begin{pmatrix}2&1\\5&3\end{pmatrix}$. Son déterminant vaut $2\times 3 - 1\times 5 = 1$, donc
>
> $$\mathbf{A}^{-1} = \begin{pmatrix}3&-1\\-5&2\end{pmatrix}.$$
>
> **Vérification** : $\mathbf{A}\mathbf{A}^{-1} = \begin{pmatrix}2\cdot 3 + 1\cdot(-5) & 2\cdot(-1) + 1\cdot 2\\ 5\cdot 3 + 3\cdot(-5) & 5\cdot(-1) + 3\cdot 2\end{pmatrix} = \begin{pmatrix}1&0\\0&1\end{pmatrix}$. ✔

```python
A = np.array([[2, 1], [5, 3]])
A_inv = np.linalg.inv(A)
print(A_inv.round(6) + 0)          # le "+ 0" évite l'affichage de -0.
print((A @ A_inv).round(6) + 0)
```
<!--sortie-->
```text
[[ 3. -1.]
 [-5.  2.]]
[[1. 0.]
 [0. 1.]]
```

#### Résoudre un système d'équations linéaires

Voici l'utilité majeure de l'inverse. Yasmine a perdu sa liste de prix, mais retrouve deux factures :

- commande 1 : 2 poteries + 1 huile = 102 DT ;
- commande 2 : 1 poterie + 3 huiles = 81 DT.

Notons $x_1$ le prix d'une poterie et $x_2$ celui d'une huile. Le système s'écrit $\mathbf{M}\mathbf{x} = \mathbf{b}$ avec

$$\mathbf{M} = \begin{pmatrix}2&1\\1&3\end{pmatrix}, \quad \mathbf{x} = \begin{pmatrix}x_1\\x_2\end{pmatrix}, \quad \mathbf{b} = \begin{pmatrix}102\\81\end{pmatrix}.$$

> 🧪 **Résolution à la main.** $\det\mathbf{M} = 2\times 3 - 1 \times 1 = 5$ et $\mathbf{M}^{-1} = \frac15\begin{pmatrix}3&-1\\-1&2\end{pmatrix}$. Donc
>
> $$\mathbf{x} = \mathbf{M}^{-1}\mathbf{b} = \frac15\begin{pmatrix}3\cdot 102 - 81\\ -102 + 2\cdot 81\end{pmatrix} = \frac15\begin{pmatrix}225\\60\end{pmatrix} = \begin{pmatrix}45\\12\end{pmatrix}.$$
>
> Une poterie coûte **45 DT**, une huile **12 DT**. Vérifions : $2 \times 45 + 12 = 102$ ✔ et $45 + 3\times 12 = 81$ ✔.

```python
M = np.array([[2, 1], [1, 3]])
b = np.array([102, 81])
print("Prix retrouvés :", np.linalg.solve(M, b))
```
<!--sortie-->
```text
Prix retrouvés : [45. 12.]
```

> ⚠️ **Piège : en pratique, on évite d'inverser.** Pour résoudre $\mathbf{M}\mathbf{x} = \mathbf{b}$, on utilise `np.linalg.solve`, jamais `np.linalg.inv(M) @ b` : c'est plus rapide et plus précis (voir la section ➕ sur l'analyse numérique). L'inverse est un outil de **raisonnement** ; la machine, elle, résout directement.

#### Quand le système n'a pas de solution unique : déterminant et rang

Imaginons que la commande 2 soit en réalité « 4 poteries + 2 huiles = 204 DT » : c'est exactement le **double** de la commande 1. Elle n'apporte **aucune information nouvelle**. Il y a alors une infinité de couples de prix qui conviennent. Le déterminant le détecte : $\det\begin{pmatrix}2&1\\4&2\end{pmatrix} = 2\times 2 - 1\times 4 = 0$. On dit que la matrice est **singulière** (non inversible).

Une notion plus générale est le **rang** : le nombre de colonnes (ou de lignes) *linéairement indépendantes*, c'est-à-dire qui ne s'obtiennent pas comme combinaison des autres. Ici le rang vaut 1 au lieu de 2.

```python
S = np.array([[2, 1], [4, 2]])
print("déterminant :", np.linalg.det(S))
print("rang        :", np.linalg.matrix_rank(S))
```
<!--sortie-->
```text
déterminant : 0.0
rang        : 1
```

> 🛠️ **Application : des colonnes redondantes.** Cette situation est fréquente dans les vraies données. Supposons qu'un fichier contienne le prix hors taxes (HT) *et* le prix toutes taxes comprises (TTC = 1,19 × HT). La seconde colonne est un multiple de la première : elle ne dit rien de plus.

```python
ht = np.array([40.0, 25.0, 60.0, 15.0])
table = np.column_stack([ht, 1.19 * ht])    # deux colonnes : HT et TTC
print("rang de la table :", np.linalg.matrix_rank(table), "(alors qu'il y a 2 colonnes)")
```
<!--sortie-->
```text
rang de la table : 1 (alors qu'il y a 2 colonnes)
```

Un modèle de régression qui utiliserait ces deux colonnes serait incapable de départager leurs rôles. C'est le problème de la **multicolinéarité**, que nous retrouverons au volume II.

#### Application : la matrice des similarités entre clients

Revenons à nos clients et à la similarité cosinus. Ajoutons deux clients, Dorra et Elyes, et mettons les cinq profils dans une matrice $\mathbf{X}$ (une ligne par client, une colonne par catégorie).

L'astuce : si l'on **normalise** chaque ligne pour que sa norme vaille 1, on obtient une matrice $\mathbf{U}$ dont chaque ligne est un vecteur de longueur 1. Alors le produit scalaire de deux lignes de $\mathbf{U}$ est directement leur cosinus. Et **tous** les produits scalaires entre lignes sont rassemblés dans le produit $\mathbf{U}\mathbf{U}^\top$ :

$$(\mathbf{U}\mathbf{U}^\top)_{ij} = \mathbf{u}_i \cdot \mathbf{u}_j = \cos\theta_{ij}.$$

```python
clients = {"Amel": [3, 1, 0], "Bilel": [6, 2, 0], "Chaima": [0, 1, 4],
           "Dorra": [1, 0, 5], "Elyes": [2, 2, 2]}
noms = list(clients)
X = np.array(list(clients.values()), dtype=float)        # une ligne par client

U = X / np.linalg.norm(X, axis=1, keepdims=True)         # chaque ligne ramenée à la norme 1
S = U @ U.T                                              # toutes les similarités d'un coup

print(" " * 8 + "".join(f"{n:>8}" for n in noms))
for i, n in enumerate(noms):
    print(f"{n:<8}" + "".join(f"{S[i, j]:8.2f}" for j in range(len(noms))))
```
<!--sortie-->
```text
            Amel   Bilel  Chaima   Dorra   Elyes
Amel        1.00    1.00    0.08    0.19    0.73
Bilel       1.00    1.00    0.08    0.19    0.73
Chaima      0.08    0.08    1.00    0.95    0.70
Dorra       0.19    0.19    0.95    1.00    0.68
Elyes       0.73    0.73    0.70    0.68    1.00
```

Lecture : la diagonale vaut 1 (chacun ressemble parfaitement à lui-même), la matrice est symétrique (la ressemblance d'Amel à Bilel est celle de Bilel à Amel), Amel et Bilel valent 1,00, et Chaima et Dorra, tous deux fans de bijoux, sont très proches. Elyes, qui achète un peu de tout, est moyennement proche de chacun (entre 0,68 et 0,73) sans avoir de « jumeau » parmi eux.

Pour recommander un produit à Chaima, Yasmine pourrait regarder ce qu'achète son voisin le plus proche, ici Dorra. Avec une seule multiplication de matrices, nous avons comparé les cinq clients entre eux ; avec cinq mille clients, ce serait la même ligne de code.

> ✅ **À retenir (matrices).**
>
> - Une matrice est un tableau $n \times p$ : lignes = individus, colonnes = variables.
> - $(\mathbf{A}\mathbf{B})_{ij}$ = ligne $i$ de $\mathbf{A}$ $\cdot$ colonne $j$ de $\mathbf{B}$ ; les dimensions doivent s'emboîter : $(n\times p)(p \times q)$.
> - Le produit matriciel n'est **pas commutatif**.
> - Résoudre $\mathbf{M}\mathbf{x} = \mathbf{b}$ : on utilise `np.linalg.solve`. Si $\det\mathbf{M} = 0$ (rang insuffisant), il n'y a pas de solution unique.
> - Des colonnes redondantes font chuter le rang : c'est la source de la multicolinéarité.


### 1.1.3 Valeurs propres et vecteurs propres : les directions privilégiées

> 💡 **Intuition.** Une matrice carrée agit sur le plan comme une machine à déformer : elle étire, elle fait pivoter, elle cisaille. Si vous lui donnez un vecteur, elle en renvoie un autre, en général dans une **autre direction**.
>
> Mais il existe parfois des vecteurs « têtus » : la machine les **étire (ou les écrase) sans les faire tourner**. Ce sont les **vecteurs propres**. Le facteur d'étirement est la **valeur propre**.

Formellement, un vecteur $\mathbf{v} \neq \mathbf{0}$ est un **vecteur propre** de la matrice carrée $\mathbf{A}$ s'il existe un nombre $\lambda$ (la **valeur propre**) tel que

$$\mathbf{A}\mathbf{v} = \lambda\,\mathbf{v}.$$

#### Un exemple que l'on vérifie à la main

Prenons $\mathbf{A} = \begin{pmatrix}2&1\\1&2\end{pmatrix}$ et essayons trois vecteurs.

> 🧪 **Test 1.** $\mathbf{v} = (1, 1)$ : $\mathbf{A}\mathbf{v} = (2\cdot 1 + 1\cdot 1,\; 1\cdot 1 + 2\cdot 1) = (3, 3) = 3\,\mathbf{v}$. ✔ La direction est conservée, le vecteur est triplé : **vecteur propre, valeur propre 3**.
>
> **Test 2.** $\mathbf{w} = (1, -1)$ : $\mathbf{A}\mathbf{w} = (2 - 1,\; 1 - 2) = (1, -1) = 1\cdot\mathbf{w}$. ✔ **Vecteur propre, valeur propre 1.**
>
> **Test 3.** $\mathbf{u} = (1, 0)$ : $\mathbf{A}\mathbf{u} = (2, 1)$. Ce n'est pas un multiple de $(1, 0)$ : la direction a changé. ✘ **Pas un vecteur propre.**

La figure ci-dessous montre ce que fait $\mathbf{A}$ sur tous les vecteurs de longueur 1 (le cercle unité) : elle le transforme en une **ellipse**, allongée d'un facteur 3 dans la direction $(1,1)$ et conservée (facteur 1) dans la direction $(1,-1)$. Les axes de l'ellipse sont exactement les vecteurs propres.

![Action de la matrice A sur le cercle unité : l'ellipse est étirée d'un facteur 3 le long de (1,1) et inchangée le long de (1,−1).](figures/ch01-ellipse-propre.png)

#### Comment trouver les valeurs propres ?

On cherche les $\lambda$ pour lesquels l'équation $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ admet une solution non nulle. On la réécrit $(\mathbf{A} - \lambda\mathbf{I})\mathbf{v} = \mathbf{0}$. Un système homogène a une solution non nulle exactement lorsque sa matrice est **singulière**, c'est-à-dire lorsque son déterminant est nul :

$$\det(\mathbf{A} - \lambda\mathbf{I}) = 0.$$

C'est l'**équation caractéristique**. Pour notre matrice :

$$\det\begin{pmatrix}2-\lambda & 1\\ 1 & 2-\lambda\end{pmatrix} = (2-\lambda)^2 - 1 = \lambda^2 - 4\lambda + 3 = (\lambda - 1)(\lambda - 3).$$

Les valeurs propres sont donc $\lambda_1 = 3$ et $\lambda_2 = 1$. On trouve ensuite les vecteurs propres en résolvant $(\mathbf{A} - \lambda\mathbf{I})\mathbf{v} = \mathbf{0}$ :

- pour $\lambda = 3$ : $\begin{pmatrix}-1&1\\1&-1\end{pmatrix}\mathbf{v} = \mathbf{0}$ donne $v_1 = v_2$, soit $\mathbf{v} = (1, 1)$ (à un multiple près) ;
- pour $\lambda = 1$ : $\begin{pmatrix}1&1\\1&1\end{pmatrix}\mathbf{v} = \mathbf{0}$ donne $v_2 = -v_1$, soit $\mathbf{w} = (1, -1)$.

> ✅ **Deux contrôles rapides.** La **somme** des valeurs propres vaut la **trace** de la matrice (somme de la diagonale) : $3 + 1 = 4 = 2 + 2$. Le **produit** des valeurs propres vaut le **déterminant** : $3 \times 1 = 3 = 2\cdot 2 - 1\cdot 1$. Utile pour détecter une erreur de calcul.

```python
import numpy as np

A = np.array([[2, 1], [1, 2]])
valeurs, vecteurs = np.linalg.eigh(A)     # eigh : pour les matrices symétriques
print("valeurs propres :", valeurs)
print("vecteurs propres (en colonnes) :\n", vecteurs.round(4))
print("trace =", np.trace(A), " somme des valeurs propres =", valeurs.sum())
print("det   =", round(np.linalg.det(A), 4), " produit des valeurs propres =", valeurs.prod())
```
<!--sortie-->
```text
valeurs propres : [1. 3.]
vecteurs propres (en colonnes) :
 [[-0.7071  0.7071]
 [ 0.7071  0.7071]]
trace = 4  somme des valeurs propres = 4.0
det   = 3.0  produit des valeurs propres = 3.0
```

NumPy range les valeurs propres par ordre croissant et renvoie des vecteurs **de longueur 1** (le signe est arbitraire : si $\mathbf{v}$ est propre, $-\mathbf{v}$ l'est aussi).

#### Le cas des matrices symétriques

Une matrice est **symétrique** si $\mathbf{A}^\top = \mathbf{A}$ (la matrice de similarité de la section précédente en est une, et la matrice de covariance, que nous rencontrerons dans un instant, aussi). Ces matrices ont une propriété exceptionnelle :

> **Théorème spectral.** Une matrice symétrique réelle de taille $p\times p$ a $p$ valeurs propres **réelles** et on peut choisir pour elle $p$ vecteurs propres **orthogonaux** deux à deux (et de longueur 1). Si $\mathbf{V}$ est la matrice qui les contient en colonnes et $\boldsymbol{\Lambda}$ la matrice diagonale des valeurs propres, alors
>
> $$\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top.$$

Nous admettons l'existence (la preuve complète se trouve dans tout cours d'algèbre linéaire), mais voici pourquoi les vecteurs propres associés à des valeurs propres différentes sont orthogonaux :

> 📐 **Démonstration : orthogonalité.** Soient $\mathbf{A}\mathbf{v}_1 = \lambda_1\mathbf{v}_1$ et $\mathbf{A}\mathbf{v}_2 = \lambda_2\mathbf{v}_2$ avec $\lambda_1 \neq \lambda_2$ et $\mathbf{A}$ symétrique. Calculons de deux façons le nombre $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2$ :
>
> - directement : $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2 = \lambda_1\,(\mathbf{v}_1\cdot\mathbf{v}_2)$ ;
> - en déplaçant $\mathbf{A}$ : comme $\mathbf{A}$ est symétrique, $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2 = \mathbf{v}_1^\top\mathbf{A}^\top\mathbf{v}_2 = \mathbf{v}_1^\top\mathbf{A}\mathbf{v}_2 = \mathbf{v}_1\cdot(\mathbf{A}\mathbf{v}_2) = \lambda_2\,(\mathbf{v}_1\cdot\mathbf{v}_2)$.
>
> En soustrayant : $(\lambda_1 - \lambda_2)\,(\mathbf{v}_1\cdot\mathbf{v}_2) = 0$. Comme $\lambda_1 \neq \lambda_2$, on a $\mathbf{v}_1\cdot\mathbf{v}_2 = 0$ : les vecteurs sont orthogonaux. $\blacksquare$
>
> Dans notre exemple : $(1,1)\cdot(1,-1) = 1 - 1 = 0$. ✔

Une conséquence pratique de $\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top$ est que les **puissances** deviennent triviales : $\mathbf{A}^k = \mathbf{V}\boldsymbol{\Lambda}^k\mathbf{V}^\top$, et élever une matrice diagonale à la puissance $k$, c'est simplement élever ses éléments. (Nous nous en servirons pour les chaînes de Markov dans la section ➕ du chapitre 2.)

```python
k = 5
via_diagonalisation = vecteurs @ np.diag(valeurs**k) @ vecteurs.T
directement = np.linalg.matrix_power(A, k)
print("A^5 par diagonalisation :\n", via_diagonalisation.round(6))
print("A^5 directement :\n", directement)
```
<!--sortie-->
```text
A^5 par diagonalisation :
 [[122. 121.]
 [121. 122.]]
A^5 directement :
 [[122 121]
 [121 122]]
```

#### 🛠️ Application : la direction principale d'un nuage de clients

Yasmine mesure, pour 200 clients, le nombre de visites mensuelles sur son site et leur dépense mensuelle. Elle soupçonne que les deux sont liées. On **standardise** chaque variable (on retranche la moyenne et on divise par l'écart-type, pour qu'elles aient la même échelle, comme promis dans la section sur les vecteurs), puis on calcule la **matrice de covariance** des deux variables standardisées :

$$\mathbf{C} = \begin{pmatrix} 1 & r \\ r & 1 \end{pmatrix},$$

où $r$ est la corrélation entre les deux variables. C'est une matrice symétrique : le théorème spectral s'applique.

```python
rng = np.random.default_rng(42)
n = 200
visites = rng.normal(6, 2, n)                        # visites par mois
depense = 15 * visites + rng.normal(0, 12, n)        # dépense en DT, liée aux visites

def standardise(x):
    return (x - x.mean()) / x.std(ddof=1)

Z = np.column_stack([standardise(visites), standardise(depense)])
C = np.cov(Z.T)                                      # matrice de covariance 2 x 2
print("Matrice de covariance :\n", C.round(3))

valeurs, vecteurs = np.linalg.eigh(C)
print("Valeurs propres :", valeurs.round(3))
print("Part de la variance expliquée :", (valeurs / valeurs.sum()).round(3))
print("Direction principale :", np.abs(vecteurs[:, -1]).round(3))
```
<!--sortie-->
```text
Matrice de covariance :
 [[1.    0.903]
 [0.903 1.   ]]
Valeurs propres : [0.097 1.903]
Part de la variance expliquée : [0.049 0.951]
Direction principale : [0.707 0.707]
```

![Nuage des 200 clients (variables standardisées) et son axe principal : le long de la diagonale, le nuage est étiré ; perpendiculairement, il est mince.](figures/ch01-nuage-clients.png)

**Lecture.** La plus grande valeur propre (environ 1,90) correspond à la direction $(0{,}71;\; 0{,}71)$, la diagonale : c'est l'axe le long duquel le nuage de clients est le plus étiré, l'axe « client actif et dépensier ». Elle capte environ **95 %** de toute la variabilité. La seconde (0,10) correspond à la direction perpendiculaire, qui ne représente que les écarts « dépense inhabituelle pour ce nombre de visites ».

Autrement dit, on peut résumer ces deux variables par **une seule** (la position le long de l'axe principal), en ne perdant que 5 % de l'information. C'est le principe de l'**analyse en composantes principales** (ACP), que nous étudierons en détail au volume II : *trouver les directions de plus grande variance, ce sont les vecteurs propres de la matrice de covariance*.

> ✅ **À retenir (valeurs propres).**
>
> - $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ : un vecteur propre garde sa direction, la valeur propre dit de combien il est étiré.
> - On les trouve avec $\det(\mathbf{A} - \lambda\mathbf{I}) = 0$. Somme des valeurs propres = trace ; produit = déterminant.
> - Une matrice symétrique a des valeurs propres réelles et des vecteurs propres orthogonaux ; $\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top$.
> - Les vecteurs propres de la matrice de covariance sont les axes principaux d'un nuage de données.

### 1.1.4 La décomposition en valeurs singulières (SVD)

Les valeurs propres ne sont définies que pour des matrices **carrées**. Or un jeu de données est rarement carré : $n$ individus, $p$ variables, avec $n \neq p$. La **décomposition en valeurs singulières**, ou **SVD** (*Singular Value Decomposition*), étend la même idée à **n'importe quelle matrice**. C'est l'un des outils les plus puissants de toute la data science.

> 💡 **Intuition.** Toute matrice, même rectangulaire, agit en trois temps : **une rotation, un étirement le long des axes, puis une autre rotation**. On écrit :
>
> $$\mathbf{A} = \mathbf{U}\,\boldsymbol{\Sigma}\,\mathbf{V}^\top.$$
>
> Les matrices $\mathbf{U}$ et $\mathbf{V}$ sont des rotations (leurs colonnes sont des vecteurs de longueur 1, orthogonaux entre eux) ; $\boldsymbol{\Sigma}$ est « diagonale » et contient les facteurs d'étirement $\sigma_1 \ge \sigma_2 \ge \dots \ge 0$, appelés **valeurs singulières**.

On peut aussi lire la SVD comme une **somme de couches simples** (« de rang 1 »), classées de la plus importante à la moins importante :

$$\mathbf{A} = \sigma_1\,\mathbf{u}_1\mathbf{v}_1^\top + \sigma_2\,\mathbf{u}_2\mathbf{v}_2^\top + \dots + \sigma_r\,\mathbf{u}_r\mathbf{v}_r^\top.$$

Chaque couche $\mathbf{u}_i\mathbf{v}_i^\top$ est un tableau « produit » : (profil des lignes) × (profil des colonnes). La première couche, celle de plus grande valeur singulière, capture la structure dominante des données ; les suivantes en sont les raffinements.

#### Un exemple minuscule

> 🧪 **Exemple à la main.** Prenons $\mathbf{A} = \begin{pmatrix}1&1\\1&1\end{pmatrix}$ (rang 1 : les deux lignes sont identiques). Calculons $\mathbf{A}^\top\mathbf{A} = \begin{pmatrix}2&2\\2&2\end{pmatrix}$. Ses valeurs propres sont 4 et 0 (trace 4, déterminant 0). La plus grande valeur singulière est donc $\sigma_1 = \sqrt{4} = 2$ et la seconde est $\sigma_2 = 0$. Le vecteur propre associé à 4 est $\mathbf{v}_1 = \frac{1}{\sqrt2}(1, 1)$, et $\mathbf{u}_1 = \mathbf{A}\mathbf{v}_1/\sigma_1 = \frac{1}{\sqrt2}(1,1)$. On vérifie :
>
> $$\sigma_1\mathbf{u}_1\mathbf{v}_1^\top = 2\cdot\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix} = \begin{pmatrix}1&1\\1&1\end{pmatrix} = \mathbf{A}. \;\checkmark$$
>
> Une seule valeur singulière non nulle : la matrice n'a qu'**une** couche. Plus généralement, **le nombre de valeurs singulières non nulles est le rang** de la matrice.

> 📐 **Démonstration : d'où viennent les valeurs singulières ?** (l'idée de la construction)
>
> Soit $\mathbf{A} \in \mathbb{R}^{n\times p}$. La matrice $\mathbf{A}^\top\mathbf{A}$ est carrée ($p\times p$), **symétrique**, et **positive** : pour tout vecteur $\mathbf{x}$, $\mathbf{x}^\top\mathbf{A}^\top\mathbf{A}\mathbf{x} = \|\mathbf{A}\mathbf{x}\|^2 \ge 0$. Le théorème spectral nous donne donc des vecteurs propres orthonormés $\mathbf{v}_1, \dots, \mathbf{v}_p$ associés à des valeurs propres $\lambda_i \ge 0$ (elles sont positives car $\lambda_i = \mathbf{v}_i^\top\mathbf{A}^\top\mathbf{A}\mathbf{v}_i = \|\mathbf{A}\mathbf{v}_i\|^2$).
>
> On pose $\sigma_i = \sqrt{\lambda_i}$ et, pour $\sigma_i > 0$, $\mathbf{u}_i = \mathbf{A}\mathbf{v}_i/\sigma_i$. Ces vecteurs $\mathbf{u}_i$ sont **orthonormés** :
>
> $$\mathbf{u}_i\cdot\mathbf{u}_j = \frac{(\mathbf{A}\mathbf{v}_i)^\top(\mathbf{A}\mathbf{v}_j)}{\sigma_i\sigma_j} = \frac{\mathbf{v}_i^\top\mathbf{A}^\top\mathbf{A}\mathbf{v}_j}{\sigma_i\sigma_j} = \frac{\lambda_j\,\mathbf{v}_i\cdot\mathbf{v}_j}{\sigma_i\sigma_j} = \begin{cases}1 & i = j\\ 0 & i\neq j.\end{cases}$$
>
> Enfin, par construction $\mathbf{A}\mathbf{v}_i = \sigma_i\mathbf{u}_i$ : c'est exactement l'égalité $\mathbf{A}\mathbf{V} = \mathbf{U}\boldsymbol{\Sigma}$, qui donne $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$. $\blacksquare$

Autrement dit : **les valeurs singulières de $\mathbf{A}$ sont les racines carrées des valeurs propres de $\mathbf{A}^\top\mathbf{A}$**. Le lien avec la section précédente est direct.

#### Approximer une matrice par un nombre réduit de couches

Voici la propriété qui rend la SVD si utile en pratique.

> **Théorème (Eckart-Young).** Parmi toutes les matrices de rang $k$, la meilleure approximation de $\mathbf{A}$ (au sens de la somme des carrés des erreurs) est obtenue en **ne gardant que les $k$ premières couches** de la SVD :
> $$\mathbf{A}_k = \sigma_1\mathbf{u}_1\mathbf{v}_1^\top + \dots + \sigma_k\mathbf{u}_k\mathbf{v}_k^\top.$$
> L'erreur vaut alors $\|\mathbf{A} - \mathbf{A}_k\|_F = \sqrt{\sigma_{k+1}^2 + \dots + \sigma_r^2}$, où $\|\cdot\|_F$ est la racine de la somme des carrés de tous les éléments.

Autrement dit : si les premières valeurs singulières sont grandes et les suivantes minuscules, on peut **jeter** les dernières couches sans presque rien perdre. C'est de la **compression**.

#### 🛠️ Application : résumer un tableau de ventes

Yasmine a les ventes hebdomadaires de 6 produits sur 8 semaines. Les données sont simulées selon une règle simple : *ventes = popularité du produit × effet de la semaine + un peu de bruit*. Une telle structure « produit × saison » doit se retrouver dans la première couche de la SVD.

```python
rng = np.random.default_rng(7)
popularite = np.array([50, 30, 20, 12, 8, 5.0])                    # un niveau par produit
saison = np.array([1.0, 1.1, 0.9, 1.2, 1.5, 1.4, 1.0, 0.8])       # un effet par semaine
M = (np.outer(popularite, saison) + rng.normal(0, 1.0, (6, 8))).round(0)

print("Tableau des ventes (6 produits x 8 semaines) :")
print(M.astype(int))
```
<!--sortie-->
```text
Tableau des ventes (6 produits x 8 semaines) :
[[50 55 45 59 75 69 50 41]
 [30 32 27 36 45 41 30 25]
 [19 22 16 23 28 28 19 16]
 [12 13  8 14 18 17 10  9]
 [ 7  8  8  9 12 12  7  6]
 [ 5  6  3  6  9  5  6  4]]
```

```python
U, s, Vt = np.linalg.svd(M)
print("valeurs singulières :", s.round(2))
part = 100 * s**2 / (s**2).sum()
print("part de l'énergie par couche (%) :", " ".join(f"{x:.2f}" for x in part))

M1 = s[0] * np.outer(U[:, 0], Vt[0])          # approximation avec UNE seule couche
erreur_relative = np.linalg.norm(M - M1) / np.linalg.norm(M)
print("erreur relative de l'approximation de rang 1 :", round(erreur_relative, 4))
print("nombres à stocker : 48 (tableau) contre", 6 + 8 + 1, "(couche 1)")
```
<!--sortie-->
```text
valeurs singulières : [202.05   3.53   3.51   1.81   1.18   0.75]
part de l'énergie par couche (%) : 99.93 0.03 0.03 0.01 0.00 0.00
erreur relative de l'approximation de rang 1 : 0.0271
nombres à stocker : 48 (tableau) contre 15 (couche 1)
```

![Ventes observées (à gauche), approximation par une seule couche (au centre) et ce qui reste (à droite). L'échelle de couleur est la même pour les deux premiers panneaux.](figures/ch01-svd-ventes.png)

**Lecture.** La première valeur singulière (environ 202) est près de soixante fois plus grande que la deuxième (environ 3,5) : **99,9 %** de l'« énergie » du tableau est dans une seule couche. Une approximation de rang 1, qui ne stocke que 15 nombres au lieu de 48, reproduit le tableau avec une erreur relative d'environ 2,7 %. Le reste (les couches 2 à 6) est du bruit.

La SVD a donc **retrouvé toute seule** la structure « popularité × saison » que nous avions mise dans les données, sans qu'on lui dise de la chercher. Vous venez de voir le principe de la **réduction de dimension** et celui des **systèmes de recommandation** par factorisation de matrices, deux sujets que nous développerons aux volumes suivants.

> ✅ **À retenir (SVD).**
>
> - Toute matrice se décompose en $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$ : rotation, étirement, rotation.
> - Les valeurs singulières mesurent l'importance de chaque couche ; leur nombre non nul est le rang.
> - Garder les $k$ premières couches donne la meilleure approximation de rang $k$ (Eckart-Young) : c'est la base de la compression, du débruitage et de l'ACP.
> - L'ACP n'est rien d'autre que la SVD des données centrées.


## 1.2 Analyse : mesurer le changement

L'algèbre linéaire nous a appris à décrire des données. L'**analyse** nous apprend à décrire comment les choses **changent**. C'est ce qui permet de répondre à des questions comme : « si j'augmente mon prix d'un dinar, mes recettes montent-elles ou descendent-elles, et de combien ? ». Elle repose sur deux notions : la **dérivée** (le changement instantané) et l'**intégrale** (le changement accumulé).

### 1.2.1 La dérivée : la vitesse à laquelle une fonction change

> 💡 **Intuition.** Si une fonction décrit **où vous en êtes**, sa dérivée décrit **à quelle vitesse vous avancez**. Dans une voiture, la distance parcourue est la fonction ; le compteur de vitesse affiche sa dérivée. Graphiquement, la dérivée en un point est la **pente de la tangente** à la courbe en ce point.

#### Une fonction pour commencer

Une **fonction** associe à chaque valeur d'entrée $x$ une valeur de sortie $f(x)$. Voici celle que nous utiliserons dans cette section : le bénéfice hebdomadaire de Yasmine pour une poterie, en fonction du nombre $q$ de pièces vendues. Plus elle en vend, plus elle doit baisser le prix, et il y a 300 DT de frais fixes :

$$P(q) = -2q^2 + 80q - 300.$$

Par exemple, $P(20) = -2\cdot 400 + 1600 - 300 = 500$ DT.

#### D'abord, une idée de limite

Pour définir la dérivée, il faut la notion de **limite** : la valeur *vers laquelle tend* une quantité quand on s'approche d'un point, même si l'on ne peut pas l'atteindre.

> 🧪 **Exemple.** Considérons $f(x) = \dfrac{x^2 - 1}{x - 1}$. Elle n'est pas définie en $x = 1$ (division par zéro). Mais que se passe-t-il quand $x$ s'en approche ?

```python
import numpy as np

def f(x):
    return (x**2 - 1) / (x - 1)

for x in [0.9, 0.99, 0.999, 1.001, 1.01, 1.1]:
    print(f"x = {x:<6}  f(x) = {f(x):.4f}")
```
<!--sortie-->
```text
x = 0.9     f(x) = 1.9000
x = 0.99    f(x) = 1.9900
x = 0.999   f(x) = 1.9990
x = 1.001   f(x) = 2.0010
x = 1.01    f(x) = 2.0100
x = 1.1     f(x) = 2.1000
```

On voit que $f(x)$ se rapproche de **2**. On écrit $\lim_{x \to 1} f(x) = 2$. (Algébriquement, $x^2 - 1 = (x-1)(x+1)$, donc $f(x) = x + 1$ dès que $x \ne 1$.) Une limite décrit un comportement **au voisinage** d'un point, pas au point lui-même.

#### Définition de la dérivée

Comment mesurer la pente d'une courbe en un seul point ? Une pente se mesure entre deux points. L'idée est donc de prendre deux points très proches, $x$ et $x + h$, et de regarder la pente de la droite qui les relie : le **taux d'accroissement**

$$\frac{f(x + h) - f(x)}{h}.$$

Puis de faire tendre $h$ vers zéro. La **dérivée** est la limite, quand elle existe :

$$f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}.$$

> 🧪 **Exemple chiffré.** Prenons $f(x) = x^2$ au point $x = 3$ et rapprochons $h$ de zéro :

```python
def carre(x):
    return x**2

for h in [1, 0.1, 0.01, 0.001, 0.0001]:
    taux = (carre(3 + h) - carre(3)) / h
    print(f"h = {h:<7} taux d'accroissement = {taux:.4f}")
```
<!--sortie-->
```text
h = 1       taux d'accroissement = 7.0000
h = 0.1     taux d'accroissement = 6.1000
h = 0.01    taux d'accroissement = 6.0100
h = 0.001   taux d'accroissement = 6.0010
h = 0.0001  taux d'accroissement = 6.0001
```

Les valeurs se rapprochent de **6**. Et $2 \times 3 = 6$ : la dérivée de $x^2$ semble être $2x$. Prouvons-le.

> 📐 **Démonstration : la dérivée de $x^2$ est $2x$.**
>
> $$\frac{(x+h)^2 - x^2}{h} = \frac{x^2 + 2xh + h^2 - x^2}{h} = \frac{2xh + h^2}{h} = 2x + h.$$
>
> Quand $h \to 0$, cette quantité tend vers $2x$. Donc $(x^2)' = 2x$. $\blacksquare$
>
> Notez que les calculs numériques ci-dessus suivent exactement ce résultat : le taux vaut $2\cdot 3 + h = 6 + h$, soit 7, 6,1, 6,01, 6,001, 6,0001.

#### Les règles de calcul

On ne recalcule pas une limite à chaque fois. On utilise des règles, qu'il faut connaître par cœur :

| Fonction | Dérivée | Exemple |
|---|---|---|
| constante $c$ | $0$ | $(7)' = 0$ |
| $x^n$ | $n\,x^{n-1}$ | $(x^3)' = 3x^2$ ; $(\sqrt{x})' = \frac{1}{2\sqrt{x}}$ |
| $e^{x}$ | $e^{x}$ | |
| $\ln x$ | $\dfrac1x$ | |
| somme $f + g$ | $f' + g'$ | $(x^2 + 5x)' = 2x + 5$ |
| multiple $c\,f$ | $c\,f'$ | $(4x^3)' = 12x^2$ |
| produit $f\,g$ | $f'g + fg'$ | $(x\,e^x)' = e^x + x\,e^x$ |
| composée $f(g(x))$ | $f'(g(x))\cdot g'(x)$ | voir ci-dessous |

La dernière règle, celle de la **dérivée d'une composée** (ou « règle de la chaîne »), est la plus importante pour la suite : c'est elle qui fait fonctionner l'entraînement de tous les réseaux de neurones. Elle dit : *dérivez l'extérieur sans toucher à l'intérieur, puis multipliez par la dérivée de l'intérieur.*

> 🧪 **Exemple.** $h(x) = (3x + 1)^2$. L'extérieur est « carré », l'intérieur est $3x + 1$.
>
> $$h'(x) = \underbrace{2\,(3x+1)}_{\text{dérivée de l'extérieur}} \times \underbrace{3}_{\text{dérivée de l'intérieur}} = 6(3x+1) = 18x + 6.$$
>
> **Contrôle** : en développant, $h(x) = 9x^2 + 6x + 1$, dont la dérivée est $18x + 6$. ✔
>
> Autre exemple, qui servira bientôt : $\dfrac{d}{dx}\,e^{-0{,}5x} = -0{,}5\,e^{-0{,}5x}$ (l'intérieur est $-0{,}5x$, de dérivée $-0{,}5$).

Pour **vérifier** une dérivée calculée à la main (ou dénicher une erreur), on peut la comparer à une dérivée numérique : on calcule la pente entre $x - h$ et $x + h$ pour un très petit $h$ (la « différence centrée »).

```python
def derivee_numerique(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)

tests = [
    ("x^3 en x = 2",       lambda x: x**3,             2.0, 3 * 2.0**2),
    ("(3x+1)^2 en x = 1",  lambda x: (3 * x + 1)**2,   1.0, 6 * (3 * 1.0 + 1)),
    ("exp(-0.5x) en x = 2", lambda x: np.exp(-0.5 * x), 2.0, -0.5 * np.exp(-1.0)),
    ("ln(2x) en x = 4",    lambda x: np.log(2 * x),    4.0, 1 / 4.0),
]
for nom, fonction, x0, exacte in tests:
    print(f"{nom:<20} numérique = {derivee_numerique(fonction, x0):9.6f}   formule = {exacte:9.6f}")
```
<!--sortie-->
```text
x^3 en x = 2         numérique = 12.000000   formule = 12.000000
(3x+1)^2 en x = 1    numérique = 24.000000   formule = 24.000000
exp(-0.5x) en x = 2  numérique = -0.183940   formule = -0.183940
ln(2x) en x = 4      numérique =  0.250000   formule =  0.250000
```

> ✅ **Bonne habitude.** Chaque fois que vous dérivez une expression compliquée, comparez-la à une dérivée numérique. Les erreurs de signe et les oublis de « fois la dérivée de l'intérieur » sont les fautes les plus courantes.

#### 🛠️ Application : à quel niveau de ventes le bénéfice est-il maximal ?

Reprenons $P(q) = -2q^2 + 80q - 300$. Observons-la d'abord :

```python
def benefice(q):
    return -2 * q**2 + 80 * q - 300

for q in [10, 15, 20, 25, 30]:
    print(f"q = {q:>2}   bénéfice = {benefice(q):>4} DT")
```
<!--sortie-->
```text
q = 10   bénéfice =  300 DT
q = 15   bénéfice =  450 DT
q = 20   bénéfice =  500 DT
q = 25   bénéfice =  450 DT
q = 30   bénéfice =  300 DT
```

Le bénéfice monte, atteint un sommet, puis redescend : c'est une parabole « en cloche ». **Au sommet, la tangente est horizontale, donc la dérivée est nulle.** C'est la clé de l'optimisation. On dérive :

$$P'(q) = -4q + 80.$$

On résout $P'(q) = 0$ : $-4q + 80 = 0$, donc $q = 20$ pièces, pour un bénéfice $P(20) = 500$ DT.

La dérivée a aussi une lecture économique directe : c'est le **bénéfice marginal**, le gain approximatif que rapporte la pièce supplémentaire. En $q = 10$, $P'(10) = -40 + 80 = 40$ DT. Vérifions avec la vraie différence :

```python
print("gain réel de la 11e pièce : P(11) - P(10) =", benefice(11) - benefice(10), "DT")
print("pente en q = 10           : P'(10) = -4*10 + 80 =", -4 * 10 + 80, "DT")
```
<!--sortie-->
```text
gain réel de la 11e pièce : P(11) - P(10) = 38 DT
pente en q = 10           : P'(10) = -4*10 + 80 = 40 DT
```

La pente (40) est une bonne approximation du gain réel (38) : elle est exacte pour une variation infiniment petite, et approchée pour une variation d'une pièce. Enfin, confirmons le sommet par une recherche numérique, sans utiliser la dérivée :

```python
from scipy.optimize import minimize_scalar

res = minimize_scalar(lambda q: -benefice(q), bounds=(0, 40), method="bounded")
print(f"optimum numérique : q = {res.x:.3f}, bénéfice = {-res.fun:.2f} DT")
```
<!--sortie-->
```text
optimum numérique : q = 20.000, bénéfice = 500.00 DT
```

(On minimise $-P$ puisque la fonction cherche un minimum : maximiser $P$ revient à minimiser $-P$.)

![Bénéfice hebdomadaire en fonction du nombre de pièces vendues. En q = 10 la tangente monte avec une pente de 40 ; en q = 20 elle est horizontale : c'est le sommet.](figures/ch01-benefice-tangentes.png)

#### Comment savoir si c'est un maximum ou un minimum ?

Une dérivée nulle signale un point **candidat**, pas forcément un maximum. On regarde alors la **dérivée seconde** $f''$ (la dérivée de la dérivée, qui mesure comment la pente elle-même change) :

- $f''(x) < 0$ : la pente décroît, la courbe est une « bosse », c'est un **maximum local** ;
- $f''(x) > 0$ : la pente croît, la courbe est un « creux », c'est un **minimum local** ;
- $f''(x) = 0$ : on ne peut pas conclure.

Ici $P''(q) = -4 < 0$ : c'est bien un maximum. 

> ⚠️ **Piège.** « Dérivée nulle » ne veut pas dire « extremum ». Pour $f(x) = x^3$, on a $f'(0) = 3\cdot 0^2 = 0$, et pourtant la fonction ne fait que croître : en 0, la tangente est horizontale mais la courbe continue de monter (c'est un *point d'inflexion*). Vérifiez toujours avec la dérivée seconde ou en comparant les valeurs de part et d'autre.

> ✅ **À retenir (dérivée).**
>
> - $f'(x)$ est la pente de la tangente en $x$ : c'est le taux de variation instantané.
> - Les cinq règles à maîtriser : puissances, somme, multiple, produit, composée.
> - Pour optimiser : on cherche $f'(x) = 0$, puis on contrôle avec $f''$.
> - Comparer une dérivée à la main à une dérivée numérique permet de détecter les erreurs.


### 1.2.2 Dérivées partielles et gradient : plusieurs variables à la fois

Un modèle de data science a rarement un seul paramètre : il en a deux, dix, ou un milliard. Il nous faut donc dériver des fonctions de **plusieurs variables**.

> 💡 **Intuition.** Imaginez que vous êtes debout sur le flanc d'une colline brumeuse et que vous voulez monter le plus vite possible. À vos pieds, le sol penche plus dans une direction que dans les autres. Le **gradient** est la flèche qui indique **la direction de la plus forte montée**, et sa longueur dit à quel point c'est raide. Pour descendre, on marche dans la direction opposée.

#### Dérivée partielle

Pour une fonction $f(x, y)$, la **dérivée partielle par rapport à $x$**, notée $\dfrac{\partial f}{\partial x}$, s'obtient en dérivant par rapport à $x$ **en traitant $y$ comme une constante**. De même pour $y$.

> 🧪 **Exemple.** Soit $f(x, y) = x^2 + 3y^2$ (un « bol » plus raide dans la direction $y$).
>
> $$\frac{\partial f}{\partial x} = 2x, \qquad \frac{\partial f}{\partial y} = 6y.$$
>
> (Pour $\partial f/\partial x$, le terme $3y^2$ est une constante : sa dérivée est 0.)

Le **gradient** est le vecteur qui rassemble toutes les dérivées partielles :

$$\nabla f(x, y) = \begin{pmatrix} \partial f/\partial x \\ \partial f/\partial y \end{pmatrix} = \begin{pmatrix} 2x \\ 6y \end{pmatrix}.$$

En $(1, 1)$, on obtient $\nabla f(1,1) = (2, 6)$ : la pente est 3 fois plus forte dans la direction $y$ que dans la direction $x$.

#### Pourquoi le gradient indique-t-il la plus forte montée ?

Dans une direction donnée par un vecteur $\mathbf{u}$ de longueur 1, la pente de $f$ (la **dérivée directionnelle**) vaut

$$D_{\mathbf{u}} f = \nabla f \cdot \mathbf{u}.$$

Et ce produit scalaire, nous savons le majorer.

> 📐 **Démonstration.** Par la formule du produit scalaire vue en 1.1.1,
>
> $$D_{\mathbf{u}} f = \nabla f \cdot \mathbf{u} = \|\nabla f\|\,\|\mathbf{u}\|\cos\theta = \|\nabla f\|\cos\theta,$$
>
> où $\theta$ est l'angle entre $\mathbf{u}$ et le gradient. Cette quantité est maximale quand $\cos\theta = 1$, c'est-à-dire quand $\mathbf{u}$ pointe **dans la même direction que le gradient**, et alors la pente vaut $\|\nabla f\|$. Elle est minimale (la descente la plus forte, de pente $-\|\nabla f\|$) quand $\theta = 180^\circ$, c'est-à-dire dans la direction $-\nabla f$. $\blacksquare$
>
> (Au passage : on retrouve la même inégalité de Cauchy-Schwarz que dans la section 1.1.1.)

Vérifions numériquement en $(1, 1)$, en mesurant la pente de $f$ dans quatre directions :

```python
def f2(x, y):
    return x**2 + 3 * y**2

def gradient_f2(x, y):
    return np.array([2 * x, 6 * y])

g = gradient_f2(1, 1)
print("gradient en (1, 1) :", g, "   norme =", round(np.linalg.norm(g), 4))

h = 1e-6
directions = [("direction (1, 0)",        np.array([1.0, 0.0])),
              ("direction (0, 1)",        np.array([0.0, 1.0])),
              ("direction du gradient",   g / np.linalg.norm(g)),
              ("opposée au gradient",     -g / np.linalg.norm(g))]
for nom, u in directions:
    pente = (f2(1 + h * u[0], 1 + h * u[1]) - f2(1, 1)) / h
    print(f"{nom:<24} pente mesurée = {pente:8.3f}")
```
<!--sortie-->
```text
gradient en (1, 1) : [2 6]    norme = 6.3246
direction (1, 0)         pente mesurée =    2.000
direction (0, 1)         pente mesurée =    6.000
direction du gradient    pente mesurée =    6.325
opposée au gradient      pente mesurée =   -6.325
```

La pente mesurée est maximale (6,325, soit $\|\nabla f\| = \sqrt{40}$) dans la direction du gradient, et minimale (−6,325) dans la direction opposée. Aucune autre direction ne fait mieux.

![Courbes de niveau de f(x,y) = x² + 3y² (chaque ellipse est une « altitude » constante) et, en chaque point, la direction de la plus forte descente (−gradient). Les flèches sont perpendiculaires aux courbes de niveau et pointent vers le fond du bol.](figures/ch01-gradient-contours.png)

Deux faits à retenir sur cette figure : le gradient est **perpendiculaire aux courbes de niveau**, et **−gradient pointe vers le bas**. C'est exactement ce que nous utiliserons en 1.3 pour descendre vers le minimum.

#### 🛠️ Application : la pente de l'erreur d'une droite

Yasmine veut ajuster une droite $y = ax + b$ à trois mesures $(x_i, y_i)$ : $(1, 2)$, $(2, 3)$ et $(3, 5)$. Pour mesurer la qualité d'une droite candidate, on utilise la **somme des carrés des erreurs** :

$$L(a, b) = \sum_{i=1}^{3}\bigl(y_i - (a x_i + b)\bigr)^2.$$

C'est une fonction de **deux** variables, $a$ et $b$. Notons $r_i = y_i - (ax_i + b)$ l'erreur du point $i$. Par la règle de la composée :

$$\frac{\partial L}{\partial a} = -2\sum_i x_i\, r_i, \qquad \frac{\partial L}{\partial b} = -2\sum_i r_i.$$

> 🧪 **Calcul à la main en $(a, b) = (0, 0)$** (la droite $y = 0$). Les erreurs sont $r = (2, 3, 5)$.
>
> - $L(0,0) = 4 + 9 + 25 = 38$.
> - $\partial L/\partial a = -2\,(1\cdot 2 + 2\cdot 3 + 3\cdot 5) = -2 \times 23 = -46$.
> - $\partial L/\partial b = -2\,(2 + 3 + 5) = -20$.
>
> Le gradient $(-46, -20)$ est très négatif : en augmentant $a$ et $b$, l'erreur diminue fortement.

```python
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])

def perte(a, b):
    return np.sum((y - (a * x + b))**2)

def grad_perte(a, b):
    r = y - (a * x + b)
    return np.array([-2 * np.sum(x * r), -2 * np.sum(r)])

print("perte en (0, 0)     :", perte(0, 0))
print("gradient en (0, 0)  :", grad_perte(0, 0))

# la droite des moindres carrés (calculée en 1.3) : a = 1,5 et b = 1/3
a_opt, b_opt = 1.5, 1 / 3
print("perte en (1,5 ; 1/3) :", round(perte(a_opt, b_opt), 4))
print("gradient en (1,5 ; 1/3) :", (grad_perte(a_opt, b_opt).round(10) + 0))
```
<!--sortie-->
```text
perte en (0, 0)     : 38.0
gradient en (0, 0)  : [-46. -20.]
perte en (1,5 ; 1/3) : 0.1667
gradient en (1,5 ; 1/3) : [0. 0.]
```

Au point $(1{,}5\;;\;1/3)$, le gradient est **nul** : on est au fond du bol. Nous montrerons en 1.3 comment y arriver automatiquement.

> ✅ **À retenir (gradient).**
>
> - Le gradient $\nabla f$ rassemble les dérivées partielles ; il pointe vers la **plus forte montée** et sa norme mesure la pente.
> - $-\nabla f$ pointe vers la plus forte **descente**.
> - Au minimum (ou au maximum, ou au col), le gradient est nul.
> - La règle de la composée rend le calcul du gradient d'une « somme de carrés d'erreurs » mécanique : c'est le cœur de l'entraînement des modèles.

### 1.2.3 Intégrales : accumuler les petits changements

> 💡 **Intuition.** L'intégrale est l'opération inverse de la dérivée. Si la dérivée donne « la vitesse à chaque instant », l'**intégrale** donne « la distance parcourue sur un intervalle » : elle **additionne une infinité de petits morceaux**. Graphiquement, c'est l'**aire sous la courbe**.
>
> En data science, l'intégrale sert surtout à une chose : calculer des **probabilités**. Quand une quantité est décrite par une courbe de densité, la probabilité d'un événement est l'aire sous la courbe sur la zone concernée.

#### Calculer une aire avec des rectangles

L'aire sous une courbe $f$ entre $a$ et $b$ se note $\displaystyle\int_a^b f(x)\,dx$. L'idée de **Riemann** : découper l'intervalle en $n$ bandes étroites, approcher chaque bande par un rectangle de hauteur $f(x)$, et additionner. Plus $n$ est grand, meilleure est l'approximation.

> 🧪 **Exemple à la main.** Aire sous $f(x) = x^2$ entre 0 et 3, avec $n = 3$ rectangles de largeur 1 (hauteur mesurée au bord droit) : $1\cdot 1^2 + 1 \cdot 2^2 + 1\cdot 3^2 = 1 + 4 + 9 = 14$. C'est une approximation grossière (les rectangles dépassent la courbe). Avec $n = 6$ rectangles de largeur $0{,}5$ : $0{,}5\,(0{,}5^2 + 1^2 + 1{,}5^2 + 2^2 + 2{,}5^2 + 3^2) = 0{,}5 \times 22{,}75 = 11{,}375$. Mieux !

```python
def riemann(f, a, b, n):
    largeur = (b - a) / n
    xs = a + largeur * np.arange(1, n + 1)        # extrémités droites des bandes
    return np.sum(f(xs)) * largeur

for n in [3, 6, 30, 300, 3000]:
    print(f"n = {n:>4} rectangles : aire ≈ {riemann(lambda t: t**2, 0, 3, n):.4f}")
print("valeur exacte : 3^3 / 3 =", 3**3 / 3)
```
<!--sortie-->
```text
n =    3 rectangles : aire ≈ 14.0000
n =    6 rectangles : aire ≈ 11.3750
n =   30 rectangles : aire ≈ 9.4550
n =  300 rectangles : aire ≈ 9.0451
n = 3000 rectangles : aire ≈ 9.0045
valeur exacte : 3^3 / 3 = 9.0
```

Les approximations convergent vers **9**. L'intégrale *est* cette limite.

#### Le théorème fondamental : la dérivée à l'envers

Faut-il toujours découper en rectangles ? Heureusement non. Le **théorème fondamental de l'analyse** relie intégrale et dérivée :

> Si $F$ est une **primitive** de $f$ (c'est-à-dire $F' = f$), alors
> $$\int_a^b f(x)\,dx = F(b) - F(a).$$

> 🧪 **Exemple.** Pour $f(x) = x^2$, une primitive est $F(x) = x^3/3$ (car $(x^3/3)' = x^2$). Donc $\int_0^3 x^2\,dx = F(3) - F(0) = 9 - 0 = 9$. ✔ C'est la valeur vers laquelle convergeaient nos rectangles.

Quelques primitives à connaître :

| $f(x)$ | une primitive $F(x)$ |
|---|---|
| $x^n$ ($n \ne -1$) | $\dfrac{x^{n+1}}{n+1}$ |
| $e^{kx}$ | $\dfrac{e^{kx}}{k}$ |
| $\dfrac{1}{x}$ | $\ln\lvert x\rvert$ |

> 📐 **Pourquoi ça marche : l'idée de la preuve.** Notons $A(x) = \int_a^x f(t)\,dt$ l'aire accumulée jusqu'en $x$. Quand $x$ avance de $h$, l'aire gagne une fine bande de largeur $h$ et de hauteur à peu près $f(x)$ : $A(x+h) - A(x) \approx f(x)\,h$. En divisant par $h$ et en faisant tendre $h$ vers 0, on obtient $A'(x) = f(x)$. L'aire accumulée est donc **une** primitive de $f$ ; deux primitives ne diffèrent que d'une constante, qui disparaît dans la différence $F(b) - F(a)$. $\blacksquare$ (Preuve simplifiée, suffisante pour l'intuition.)

#### 🛠️ Application : une commande dans les trois prochaines minutes ?

Sur le site de Dar Jasmin, en heure de pointe, une commande arrive en moyenne toutes les 2 minutes. On montrera au chapitre 2 que le temps d'attente $T$ (en minutes) avant la prochaine commande suit une **loi exponentielle** de taux $\lambda = 0{,}5$ par minute, dont la densité est

$$f(t) = \lambda\,e^{-\lambda t} = 0{,}5\,e^{-0{,}5\,t}, \qquad t \ge 0.$$

La probabilité qu'une commande arrive dans les 3 prochaines minutes est l'aire sous cette courbe entre 0 et 3.

> 🧪 **À la main.** Une primitive de $0{,}5\,e^{-0{,}5t}$ est $-e^{-0{,}5t}$ (on dérive : $-(-0{,}5)e^{-0{,}5t} = 0{,}5\,e^{-0{,}5t}$ ✔). Donc
>
> $$P(T \le 3) = \bigl[-e^{-0{,}5\,t}\bigr]_0^3 = -e^{-1{,}5} - (-e^{0}) = 1 - e^{-1{,}5} \approx 0{,}777.$$

```python
from scipy.integrate import quad

lam = 0.5
densite = lambda t: lam * np.exp(-lam * t)

p_riemann = riemann(densite, 0, 3, 3000)
p_quad, _ = quad(densite, 0, 3)
print("rectangles de Riemann (3000) :", round(p_riemann, 5))
print("intégration numérique (quad)  :", round(p_quad, 5))
print("formule  1 - exp(-1,5)        :", round(1 - np.exp(-1.5), 5))

total, _ = quad(densite, 0, np.inf)
print("aire totale sous la courbe    :", round(total, 5))
```
<!--sortie-->
```text
rectangles de Riemann (3000) : 0.77668
intégration numérique (quad)  : 0.77687
formule  1 - exp(-1,5)        : 0.77687
aire totale sous la courbe    : 1.0
```

![Densité du temps d'attente avant la prochaine commande. L'aire grisée entre 0 et 3 minutes vaut 0,777 : il y a environ 78 % de chances qu'une commande arrive dans les trois prochaines minutes.](figures/ch01-attente-densite.png)

**Lecture.** Les trois méthodes concordent : environ **77,7 %** de chances. Et l'aire **totale** sous la courbe vaut 1 : c'est une exigence de toute densité de probabilité (la probabilité que *quelque chose* arrive est de 100 %). Nous reverrons ces idées en détail au chapitre 2.

> ⚠️ **Piège : les aires sous l'axe comptent négativement.** Si $f$ est négative sur une partie de l'intervalle, l'intégrale en tient compte avec un signe moins. L'intégrale mesure une quantité **algébrique** accumulée, pas toujours une surface géométrique.

> ✅ **À retenir (intégrale).**
>
> - $\int_a^b f(x)\,dx$ est l'aire (algébrique) sous la courbe entre $a$ et $b$ : une limite de sommes de rectangles.
> - Théorème fondamental : $\int_a^b f = F(b) - F(a)$ où $F' = f$.
> - Pour une densité de probabilité, l'aire sous la courbe sur une zone **est** la probabilité de cette zone ; l'aire totale vaut 1.


## 1.3 Optimisation : trouver le meilleur choix

Presque tout problème de data science se ramène à la même question : **parmi toutes les valeurs possibles des paramètres de mon modèle, laquelle est la meilleure ?** Et « meilleure » veut dire : celle qui **minimise une erreur** (ou maximise un gain). C'est la troisième phrase de notre épigraphe : *apprendre, c'est minimiser une erreur*. Tout ce que nous avons vu dans ce chapitre (vecteurs, matrices, dérivées, gradients) converge ici.

### 1.3.1 Le problème d'optimisation

Un **problème d'optimisation** consiste à trouver les paramètres $\boldsymbol{\theta}$ qui minimisent une **fonction objectif** $f(\boldsymbol{\theta})$ (on dit aussi *fonction de coût* ou *fonction de perte*) :

$$\boldsymbol{\theta}^\star = \underset{\boldsymbol{\theta}}{\arg\min}\; f(\boldsymbol{\theta}).$$

La notation $\arg\min$ se lit « l'argument qui minimise » : on cherche **où** le minimum est atteint, pas seulement sa valeur. Maximiser $f$ revient à minimiser $-f$ : on peut donc toujours se ramener à une minimisation.

Nous avons déjà rencontré deux problèmes de ce type :

- le bénéfice $P(q)$ de la section 1.2 (une variable, maximisation) ;
- la perte $L(a, b)$ d'une droite ajustée à des points (deux variables, minimisation).

> 💡 **Rappel utile.** Aux points qui annulent le gradient ($\nabla f = \mathbf{0}$), la fonction est « à plat ». Ces points sont des **candidats** : minimum local, maximum local, ou col. La question est de savoir lequel, et surtout de savoir si c'est le **meilleur de tous** (minimum *global*) ou seulement le meilleur dans son voisinage (minimum *local*).

### 1.3.2 La convexité : quand il n'y a qu'une vallée

> 💡 **Intuition.** Imaginez un bol : où que vous posiez une bille, elle roule vers l'unique point le plus bas. Maintenant imaginez un paysage de montagnes avec plusieurs vallées : la bille peut se retrouver coincée dans une petite vallée alors qu'une plus profonde existe ailleurs. Une fonction **convexe** est un bol : **pas de piège possible**.

Formellement, $f$ est **convexe** si, pour deux points quelconques $\mathbf{x}$ et $\mathbf{y}$ et pour tout $t \in [0, 1]$,

$$f\bigl(t\,\mathbf{x} + (1-t)\,\mathbf{y}\bigr) \;\le\; t\,f(\mathbf{x}) + (1-t)\,f(\mathbf{y}).$$

Graphiquement : **la corde qui relie deux points de la courbe est toujours au-dessus de la courbe**. Pour une fonction d'une variable deux fois dérivable, c'est équivalent à $f''(x) \ge 0$ partout.

| Fonction | $f''$ | Convexe ? |
|---|---|---|
| $x^2$ | $2$ | oui |
| $\lvert x\rvert$ | (pas dérivable en 0, mais la corde est au-dessus) | oui |
| $e^x$ | $e^x > 0$ | oui |
| $x^3$ | $6x$ (change de signe) | **non** |
| $\sin x$ | $-\sin x$ (change de signe) | **non** |

La propriété qui rend la convexité précieuse :

> **Théorème.** Si $f$ est convexe, **tout minimum local est un minimum global**.

> 📐 **Démonstration.** Raisonnons par l'absurde. Soit $\mathbf{x}^\star$ un minimum local de $f$, et supposons qu'il existe un point $\mathbf{y}$ avec $f(\mathbf{y}) < f(\mathbf{x}^\star)$. Pour $t \in (0, 1)$, considérons le point $\mathbf{z}_t = (1-t)\,\mathbf{x}^\star + t\,\mathbf{y}$, sur le segment qui joint $\mathbf{x}^\star$ à $\mathbf{y}$. Par convexité,
>
> $$f(\mathbf{z}_t) \le (1-t)\,f(\mathbf{x}^\star) + t\,f(\mathbf{y}) < (1-t)\,f(\mathbf{x}^\star) + t\,f(\mathbf{x}^\star) = f(\mathbf{x}^\star).$$
>
> Or, quand $t \to 0$, le point $\mathbf{z}_t$ se rapproche de $\mathbf{x}^\star$ tout en gardant $f(\mathbf{z}_t) < f(\mathbf{x}^\star)$ : il existe donc des points arbitrairement proches de $\mathbf{x}^\star$ où $f$ est plus petite. Cela contredit le fait que $\mathbf{x}^\star$ est un minimum local. $\blacksquare$

#### La perte des moindres carrés est convexe

Voici le résultat qui justifie pourquoi la régression linéaire est « facile » à optimiser. Pour un modèle linéaire, la perte s'écrit avec une matrice de données $\mathbf{X}$ (une ligne par individu), un vecteur de paramètres $\boldsymbol{\theta}$ et un vecteur de cibles $\mathbf{y}$ :

$$L(\boldsymbol{\theta}) = \|\mathbf{y} - \mathbf{X}\boldsymbol{\theta}\|^2.$$

Son gradient est $\nabla L(\boldsymbol{\theta}) = -2\,\mathbf{X}^\top(\mathbf{y} - \mathbf{X}\boldsymbol{\theta})$ (c'est la forme matricielle de ce que nous avions calculé à la main en 1.2.2), et sa dérivée seconde, la **matrice hessienne**, est $\mathbf{H} = 2\,\mathbf{X}^\top\mathbf{X}$.

> 📐 **Démonstration : la hessienne est « positive », donc $L$ est convexe.** Pour tout vecteur $\mathbf{v}$,
>
> $$\mathbf{v}^\top\mathbf{H}\,\mathbf{v} = 2\,\mathbf{v}^\top\mathbf{X}^\top\mathbf{X}\,\mathbf{v} = 2\,\|\mathbf{X}\mathbf{v}\|^2 \;\ge\; 0.$$
>
> Une hessienne dont toutes les valeurs propres sont positives ou nulles correspond à une fonction convexe (c'est l'analogue en plusieurs variables de $f'' \ge 0$). $\blacksquare$
>
> De plus, si les colonnes de $\mathbf{X}$ sont **indépendantes** (rang plein), alors $\mathbf{X}\mathbf{v} = \mathbf{0}$ n'est possible que pour $\mathbf{v} = \mathbf{0}$ : la hessienne est strictement positive, le bol a un **unique** fond.

On retrouve ici le rang de la section 1.1. Reprenons nos colonnes redondantes (prix HT et prix TTC) : si $\mathbf{X}$ contient les deux, alors $\boldsymbol{\theta} = (1, 0)$ (« on utilise le HT ») et $\boldsymbol{\theta} = (0, 1/1{,}19)$ (« on utilise le TTC divisé par 1,19 ») produisent **exactement les mêmes prédictions** et donc la même perte : le fond du bol est une *rigole*, pas un point. Le minimum existe mais n'est pas unique.

```python
import numpy as np

ht = np.array([40.0, 25.0, 60.0, 15.0])
X_redondant = np.column_stack([ht, 1.19 * ht])
for theta in [(1.0, 0.0), (0.0, 1 / 1.19)]:
    print("theta =", np.round(theta, 4), "-> prédictions :", np.round(X_redondant @ np.array(theta), 4))
```
<!--sortie-->
```text
theta = [1. 0.] -> prédictions : [40. 25. 60. 15.]
theta = [0.     0.8403] -> prédictions : [40. 25. 60. 15.]
```

Pour notre petit exemple de trois points, la hessienne est $2\mathbf{X}^\top\mathbf{X}$ avec $\mathbf{X}$ constituée de la colonne $x = (1,2,3)$ et d'une colonne de 1 :

```python
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])
X = np.column_stack([x, np.ones_like(x)])          # colonnes : x et 1  ->  theta = (a, b)

H = 2 * X.T @ X
print("Hessienne :\n", H)
print("valeurs propres :", np.linalg.eigvalsh(H).round(3))
```
<!--sortie-->
```text
Hessienne :
 [[28. 12.]
 [12.  6.]]
valeurs propres : [ 0.721 33.279]
```

Les deux valeurs propres (0,72 et 33,28) sont positives : $L$ est convexe, avec un unique minimum. Remarquez toutefois qu'elles sont **très inégales** (un rapport de 46). Cela signifie que le bol est très allongé : raide dans une direction, presque plat dans l'autre. Nous allons voir que cela a des conséquences concrètes.

### 1.3.3 La descente de gradient

> 💡 **Intuition.** Vous êtes un randonneur dans le brouillard ; vous ne voyez pas la vallée, mais vous sentez la pente sous vos pieds. La stratégie : **faire un pas dans la direction où le sol descend le plus, puis recommencer**. Nous savons déjà que cette direction est $-\nabla f$.

#### L'algorithme

On part d'un point initial $\boldsymbol{\theta}_0$ et on répète :

$$\boxed{\;\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k - \eta\,\nabla f(\boldsymbol{\theta}_k)\;}$$

Le nombre $\eta > 0$ est le **pas d'apprentissage** (*learning rate*) : la taille de nos enjambées. On s'arrête quand le gradient est presque nul, ou après un nombre fixé d'itérations.

#### Un exemple à une variable, calculé à la main

Minimisons $f(x) = (x - 3)^2$. Sa dérivée est $f'(x) = 2(x - 3)$ et son minimum est évidemment en $x = 3$. Partons de $x_0 = 0$ avec $\eta = 0{,}1$.

> 🧪 **Pas à pas.**
>
> - $x_1 = 0 - 0{,}1 \times 2(0 - 3) = 0 + 0{,}6 = 0{,}6$
> - $x_2 = 0{,}6 - 0{,}1 \times 2(0{,}6 - 3) = 0{,}6 + 0{,}48 = 1{,}08$
> - $x_3 = 1{,}08 - 0{,}1 \times 2(1{,}08 - 3) = 1{,}08 + 0{,}384 = 1{,}464$
>
> On avance vers 3, avec des pas qui raccourcissent (la pente s'adoucit à mesure qu'on approche du fond).

Peut-on prévoir ce comportement ? Oui, et c'est instructif :

> 📐 **Démonstration : quand la descente converge-t-elle ?** Écrivons l'itération : $x_{k+1} = x_k - 2\eta(x_k - 3)$. Soustrayons 3 des deux côtés :
>
> $$x_{k+1} - 3 = (x_k - 3) - 2\eta(x_k - 3) = (1 - 2\eta)\,(x_k - 3).$$
>
> L'écart au minimum est donc **multiplié à chaque pas par le même facteur** $(1 - 2\eta)$. Par récurrence, $x_k - 3 = (1 - 2\eta)^k\,(x_0 - 3)$. Cet écart tend vers zéro si et seulement si $|1 - 2\eta| < 1$, c'est-à-dire
>
> $$0 < \eta < 1.$$
>
> Avec $\eta = 0{,}1$, le facteur vaut $0{,}8$ : on réduit l'erreur de 20 % à chaque pas ($x_1 - 3 = 0{,}8 \times (-3) = -2{,}4$, soit $x_1 = 0{,}6$ ✔). Le cas $\eta = 0{,}5$ donne un facteur 0 : convergence **en un seul pas** (c'est le pas idéal, égal à l'inverse de la courbure $f'' = 2$). Pour $\eta > 1$, le facteur dépasse 1 en valeur absolue : l'erreur **grandit** à chaque pas. $\blacksquare$

Observons les cinq comportements possibles :

```python
grad_1d = lambda x: 2 * (x - 3)

for eta in [0.1, 0.5, 0.9, 1.0, 1.1]:
    x_k = 0.0
    suite = [x_k]
    for _ in range(6):
        x_k = x_k - eta * grad_1d(x_k)
        suite.append(round(x_k, 3))
    print(f"eta = {eta:<4}", suite)
```
<!--sortie-->
```text
eta = 0.1  [0.0, 0.6, 1.08, 1.464, 1.771, 2.017, 2.214]
eta = 0.5  [0.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
eta = 0.9  [0.0, 5.4, 1.08, 4.536, 1.771, 3.983, 2.214]
eta = 1.0  [0.0, 6.0, 0.0, 6.0, 0.0, 6.0, 0.0]
eta = 1.1  [0.0, 6.6, -1.32, 8.184, -3.221, 10.465, -5.958]
```

On y voit : $\eta = 0{,}1$ converge doucement ; $\eta = 0{,}5$ tombe sur 3 dès le premier pas ; $\eta = 0{,}9$ converge **en oscillant** de part et d'autre du minimum ; $\eta = 1$ oscille éternellement entre 0 et 6 sans jamais converger ; $\eta = 1{,}1$ **diverge** (les valeurs s'éloignent de plus en plus).

![Descente de gradient sur f(x) = (x−3)² pour trois pas d'apprentissage : prudent (lent), bien choisi (rapide), trop grand (divergence).](figures/ch01-descente-1d.png)

> ⚠️ **Piège : le choix du pas.** Un pas trop petit donne un calcul lent ; un pas trop grand fait diverger l'algorithme. En pratique, le pas se règle à l'essai, ou avec des méthodes adaptatives (que nous verrons au volume III).

#### Descente de gradient en deux dimensions : ajuster une droite

Passons au problème de la droite ajustée aux points $(1,2)$, $(2,3)$, $(3,5)$. Écrivons l'algorithme une fois pour toutes sous une forme réutilisable :

```python
def descente_de_gradient(grad, theta0, eta, n_iter=1000, tol=1e-8):
    """Descente de gradient : renvoie le point final et le chemin parcouru."""
    theta = np.array(theta0, dtype=float)
    chemin = [theta.copy()]
    for _ in range(n_iter):
        g = grad(theta)
        if np.linalg.norm(g) < tol:          # presque à plat : on s'arrête
            break
        theta = theta - eta * g
        chemin.append(theta.copy())
    return theta, np.array(chemin)

def grad_L(theta, X, y):
    return -2 * X.T @ (y - X @ theta)

def perte_L(theta, X, y):
    return np.sum((y - X @ theta)**2)
```

On a vu que la hessienne a pour valeurs propres 0,72 et 33,28. Pour que la descente converge, le pas doit être inférieur à $2/\lambda_{\max} = 2/33{,}28 \approx 0{,}060$ (même raisonnement que $0 < \eta < 1$ en une dimension, où la courbure était 2). Essayons un pas de $0{,}05$ (acceptable), puis de $0{,}07$ (trop grand) :

```python
theta, chemin = descente_de_gradient(lambda t: grad_L(t, X, y), [0, 0], eta=0.05, n_iter=5000, tol=1e-6)
print("eta = 0,05 : itérations =", len(chemin) - 1, "   theta =", theta.round(4))

_, chemin = descente_de_gradient(lambda t: grad_L(t, X, y), [0, 0], eta=0.07, n_iter=15, tol=1e-6)
print("eta = 0,07 : pertes aux étapes 0, 5, 10, 15 :", [float(round(perte_L(chemin[k], X, y), 1)) for k in (0, 5, 10, 15)])
```
<!--sortie-->
```text
eta = 0,05 : itérations = 335    theta = [1.5    0.3333]
eta = 0,07 : pertes aux étapes 0, 5, 10, 15 : [38.0, 652.5, 11256.2, 194234.4]
```

Avec $\eta = 0{,}05$, l'algorithme converge vers $(1{,}5\;;\;0{,}3333)$, la droite $y = 1{,}5x + 1/3$, mais il lui faut **335 itérations** pour un problème à trois points. Avec $\eta = 0{,}07$ (juste au-dessus de la limite 0,060), la perte **explose**.

Pourquoi tant d'itérations ? À cause du bol allongé : le pas est limité par la direction raide (valeur propre 33), mais la progression dans la direction presque plate (valeur propre 0,72) est minuscule. Il existe un remède classique et très simple : **centrer** la variable. Au lieu de $x = (1, 2, 3)$, on utilise $x - \bar{x} = (-1, 0, 1)$.

> 🧪 **Pourquoi ça aide ?** Avec la colonne centrée, le produit $\mathbf{X}^\top\mathbf{X}$ devient **diagonal** : $\begin{pmatrix}2&0\\0&3\end{pmatrix}$. Les deux directions deviennent indépendantes et de courbures comparables (4 et 6 pour la hessienne). Le bol est presque rond.

```python
xc = x - x.mean()
Xc = np.column_stack([xc, np.ones_like(xc)])
print("valeurs propres (variable centrée) :", np.linalg.eigvalsh(2 * Xc.T @ Xc).round(3))

theta_c, chemin_c = descente_de_gradient(lambda t: grad_L(t, Xc, y), [0, 0], eta=0.15, n_iter=5000, tol=1e-6)
a, b_centre = theta_c
print("variable centrée : itérations =", len(chemin_c) - 1, "   (a, b') =", theta_c.round(4))
print("retour à la droite d'origine : a =", round(a, 4), "  b =", round(b_centre - a * x.mean(), 4))
```
<!--sortie-->
```text
valeurs propres (variable centrée) : [4. 6.]
variable centrée : itérations = 18    (a, b') = [1.5    3.3333]
retour à la droite d'origine : a = 1.5   b = 0.3333
```

**18 itérations au lieu de 335**, pour exactement le même résultat. (On retrouve la droite d'origine par $b = b' - a\,\bar{x}$.) C'est la raison pour laquelle on **centre et standardise** presque toujours les variables avant d'entraîner un modèle par descente de gradient.

Enfin, pour ce problème précis, une solution **exacte** existe, sans itérer. Le gradient s'annule quand $-2\mathbf{X}^\top(\mathbf{y} - \mathbf{X}\boldsymbol{\theta}) = \mathbf{0}$, c'est-à-dire pour

$$\mathbf{X}^\top\mathbf{X}\,\boldsymbol{\theta} = \mathbf{X}^\top\mathbf{y},$$

un système linéaire (les « équations normales ») que l'on sait résoudre avec ce que nous avons vu en 1.1.2 :

```python
theta_exact = np.linalg.solve(X.T @ X, X.T @ y)
print("équations normales :", theta_exact.round(4))
```
<!--sortie-->
```text
équations normales : [1.5    0.3333]
```

Pourquoi alors se servir de la descente de gradient ? Parce que **la plupart des modèles n'ont pas de solution exacte** : réseaux de neurones, régression logistique, etc. La descente de gradient fonctionne partout où l'on sait calculer un gradient. La régression linéaire est notre terrain d'entraînement, car on connaît la bonne réponse.

![Chemin de la descente de gradient sur les courbes de niveau de la perte, avec la variable brute (à gauche) et la variable centrée (à droite). Le bol allongé force à zigzaguer ; le bol presque rond permet d'aller droit au but.](figures/ch01-descente-2d.png)

### 1.3.4 🛠️ Application : le prix qui maximise les recettes

Voici un vrai petit problème de décision, qui combine tout le chapitre. Yasmine a testé huit prix pour un même bol en céramique, chacun pendant une semaine :

| Prix $p$ (DT) | 25 | 28 | 31 | 34 | 37 | 40 | 43 | 46 |
|---|---|---|---|---|---|---|---|---|
| Ventes $q$ (pièces) | 93 | 82 | 82 | 69 | 67 | 56 | 56 | 47 |

**Étape 1 : modéliser la demande.** On suppose une relation linéaire $q = \alpha + \beta\,p$ et on cherche $\alpha$ et $\beta$ par descente de gradient. Ici les prix valent environ 35 et les ventes environ 70 : les variables n'ont pas la même échelle. Nous appliquons donc ce que nous venons d'apprendre : **standardiser le prix** avant de descendre.

```python
prix = np.array([25, 28, 31, 34, 37, 40, 43, 46], dtype=float)
ventes = np.array([93, 82, 82, 69, 67, 56, 56, 47], dtype=float)

z = (prix - prix.mean()) / prix.std()                 # prix standardisé
Z = np.column_stack([z, np.ones_like(z)])

theta, chemin = descente_de_gradient(lambda t: grad_L(t, Z, ventes), [0, 0], eta=0.05, n_iter=1000, tol=1e-6)
print("itérations :", len(chemin) - 1)

# retour aux unités d'origine : q = alpha + beta * p
beta = theta[0] / prix.std()
alpha = theta[1] - theta[0] * prix.mean() / prix.std()
print(f"alpha = {alpha:.3f}   beta = {beta:.3f}")
print("contrôle avec np.polyfit :", np.polyfit(prix, ventes, 1).round(3)[::-1])
```
<!--sortie-->
```text
itérations : 13
alpha = 143.944   beta = -2.111
contrôle avec np.polyfit : [143.944  -2.111]
```

Treize itérations seulement. Le modèle trouvé est $q \approx 143{,}9 - 2{,}11\,p$ : **chaque dinar de hausse fait perdre environ 2,1 ventes par semaine**. (La ligne `polyfit` vérifie notre résultat avec la fonction toute faite de NumPy.)

**Étape 2 : exprimer les recettes.** Les recettes sont le prix multiplié par les quantités vendues :

$$R(p) = p \cdot q(p) = p\,(\alpha + \beta\,p) = \alpha\,p + \beta\,p^2.$$

**Étape 3 : maximiser.** On dérive et on annule : $R'(p) = \alpha + 2\beta\,p = 0$, d'où

$$p^\star = -\frac{\alpha}{2\beta}.$$

Comme $\beta < 0$, on a $R'' = 2\beta < 0$ : c'est bien un maximum.

```python
p_opt = -alpha / (2 * beta)
R = lambda p: p * (alpha + beta * p)
print(f"prix optimal p* = {p_opt:.2f} DT")
print(f"recettes prévues à p* : {R(p_opt):8.1f} DT par semaine")
print(f"recettes prévues à 40 DT : {R(40):8.1f} DT par semaine")
print(f"recettes prévues à 46 DT : {R(46):8.1f} DT par semaine")
```
<!--sortie-->
```text
prix optimal p* = 34.09 DT
recettes prévues à p* :   2453.7 DT par semaine
recettes prévues à 40 DT :   2380.0 DT par semaine
recettes prévues à 46 DT :   2154.3 DT par semaine
```

![À gauche : les huit mesures et la droite de demande ajustée. À droite : les recettes prévues selon le prix, avec leur maximum vers 34 DT.](figures/ch01-demande-recettes.png)

**Résultat.** Le prix qui maximise les recettes est d'environ **34 DT**, avec 2 454 DT de recettes hebdomadaires prévues. Au prix actuel de 40 DT, elles seraient de 2 380 DT : baisser le prix de 6 dinars rapporterait un peu plus de **70 DT par semaine**, soit environ 3 % de mieux.

> ⚠️ **Prudence.** Ce résultat est obtenu avec **huit** points et un modèle très simple. Il ne dit rien de l'incertitude (de combien $p^\star$ pourrait-il se tromper ?), ni du bénéfice (ici nous avons maximisé les *recettes*, sans tenir compte des coûts), ni de l'extrapolation hors de la plage de prix testée. Ces questions sont l'objet du chapitre 3 (statistique) et du volume II (régression). Retenez la démarche : **modéliser, écrire la fonction objectif, la dériver, l'annuler.**

### 1.3.5 Optimisation sous contraintes : les multiplicateurs de Lagrange

Dans la vraie vie, on n'optimise presque jamais librement : on a un **budget**, une capacité, un poids maximal. On cherche alors le meilleur choix **parmi ceux qui respectent une contrainte**.

> 💡 **Intuition.** Vous voulez atteindre le point le plus haut d'une colline, mais vous devez rester sur un sentier. Au meilleur point du sentier, vous ne pouvez plus monter en suivant le sentier : celui-ci est **tangent à une courbe de niveau** de la colline. À cet endroit, la direction de plus forte montée de la colline (le gradient de $f$) est **perpendiculaire au sentier**, donc **parallèle au gradient de la contrainte** (qui, lui aussi, est perpendiculaire au sentier).

#### Un exemple concret

Yasmine dispose de 1 000 DT de budget publicitaire à répartir entre Facebook ($x$ dinars) et Instagram ($y$ dinars). Elle estime les recettes générées par :

$$R(x, y) = 80\sqrt{x} + 120\sqrt{y}.$$

(La racine carrée traduit des **rendements décroissants** : les premiers dinars investis rapportent plus que les derniers.) Elle veut maximiser $R$ sous la contrainte $x + y = 1000$.

**La méthode de Lagrange.** On introduit un nombre $\lambda$ (le *multiplicateur*) et on forme le **lagrangien** :

$$\mathcal{L}(x, y, \lambda) = 80\sqrt{x} + 120\sqrt{y} - \lambda\,(x + y - 1000).$$

On annule toutes ses dérivées partielles :

- $\dfrac{\partial\mathcal{L}}{\partial x} = \dfrac{40}{\sqrt{x}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial y} = \dfrac{60}{\sqrt{y}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial \lambda} = -(x + y - 1000) = 0$ (qui redonne la contrainte).

> 🧪 **Résolution à la main.** Les deux premières équations donnent $\dfrac{40}{\sqrt{x}} = \dfrac{60}{\sqrt{y}}$, donc $\sqrt{y} = 1{,}5\sqrt{x}$, soit $y = 2{,}25\,x$. En reportant dans la contrainte : $x + 2{,}25\,x = 1000$, donc
>
> $$x = \frac{1000}{3{,}25} \approx 307{,}7\ \text{DT}, \qquad y = 2{,}25\,x \approx 692{,}3\ \text{DT}.$$
>
> Recettes : $80\sqrt{307{,}7} + 120\sqrt{692{,}3} \approx 1\,403{,}3 + 3\,157{,}4 = 4\,560{,}7$ DT.

> 📐 **Pourquoi cette méthode marche.** Le long de la contrainte, on peut paramétrer $y = 1000 - x$ et regarder $R$ comme fonction d'une seule variable. Au maximum, sa dérivée s'annule, ce qui s'écrit $\nabla R \cdot \mathbf{t} = 0$ où $\mathbf{t}$ est la direction du sentier : $\nabla R$ est perpendiculaire au sentier. Or le gradient de $g(x,y) = x + y - 1000$ l'est aussi. Deux vecteurs perpendiculaires à la même direction (en dimension 2) sont parallèles : $\nabla R = \lambda\,\nabla g$. C'est exactement ce que disent les équations $\partial\mathcal{L}/\partial x = \partial\mathcal{L}/\partial y = 0$. $\blacksquare$

Vérifions par trois chemins différents : un solveur numérique, une recherche exhaustive le long de la contrainte, et la formule.

```python
from scipy.optimize import minimize

R2 = lambda v: 80 * np.sqrt(v[0]) + 120 * np.sqrt(v[1])

res = minimize(lambda v: -R2(v), x0=[500, 500], method="SLSQP",
               bounds=[(1e-6, None), (1e-6, None)],
               constraints=[{"type": "eq", "fun": lambda v: v[0] + v[1] - 1000}])
print("solveur SLSQP        : x = %.1f, y = %.1f, recettes = %.2f" % (res.x[0], res.x[1], -res.fun))

grille = np.linspace(1, 999, 9981)
valeurs = [R2([g, 1000 - g]) for g in grille]
i = int(np.argmax(valeurs))
print("recherche exhaustive : x = %.1f, y = %.1f, recettes = %.2f" % (grille[i], 1000 - grille[i], valeurs[i]))

x_th = 1000 / 3.25
print("formule              : x = %.1f, y = %.1f, recettes = %.2f" % (x_th, 1000 - x_th, R2([x_th, 1000 - x_th])))
```
<!--sortie-->
```text
solveur SLSQP        : x = 307.7, y = 692.3, recettes = 4560.70
recherche exhaustive : x = 307.7, y = 692.3, recettes = 4560.70
formule              : x = 307.7, y = 692.3, recettes = 4560.70
```

**Le multiplicateur $\lambda$ a une signification concrète.** Au point optimal, $\lambda = 40/\sqrt{x} \approx 40/17{,}54 \approx 2{,}28$. C'est le **prix de l'ombre** (*shadow price*) de la contrainte : **un dinar de budget supplémentaire rapporterait environ 2,28 DT de recettes en plus**, si l'on réoptimise la répartition. Vérifions :

```python
meilleur = lambda B: R2([B / 3.25, B - B / 3.25])       # répartition optimale pour un budget B
print("gain réel avec 1 DT de plus :", round(meilleur(1001) - meilleur(1000), 4))
print("multiplicateur lambda       :", round(40 / np.sqrt(x_th), 4))
```
<!--sortie-->
```text
gain réel avec 1 DT de plus : 2.2798
multiplicateur lambda       : 2.2804
```

C'est une information précieuse pour fixer un budget : 1 DT de publicité en plus rapporte environ 2,28 DT de recettes. Il n'est donc rentable d'augmenter le budget que si la marge brute de Yasmine dépasse $1/2{,}28 \approx 44\,\%$ (sinon la dépense supplémentaire coûte plus qu'elle ne rapporte).

> ✅ **À retenir (optimisation).**
>
> - Apprendre = minimiser une fonction de perte. $\arg\min$ désigne le point où le minimum est atteint.
> - Si la fonction est **convexe**, tout minimum local est global. La perte des moindres carrés est convexe (hessienne $2\mathbf{X}^\top\mathbf{X}$ positive) ; elle a un fond unique si les colonnes de $\mathbf{X}$ sont indépendantes.
> - Descente de gradient : $\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k - \eta\,\nabla f(\boldsymbol{\theta}_k)$. Le pas $\eta$ ne doit être ni trop petit (lent) ni trop grand (divergence : $\eta < 2/\lambda_{\max}$ pour une fonction quadratique).
> - **Centrer et standardiser** les variables arrondit le bol et accélère considérablement la descente.
> - Sous contrainte, on annule les dérivées du lagrangien ; $\lambda$ mesure la valeur marginale de la contrainte.


## 1.4 La fiche de notations

> 💡 **À quoi sert cette fiche ?** Les livres de data science sont pleins de symboles. Le but n'est pas de les apprendre par cœur, mais de **savoir où regarder** quand l'un d'eux vous bloque. Gardez cette page ouverte pendant la lecture de tous les volumes.

### 1.4.1 Conventions typographiques

| Ce que vous voyez | Ce que cela désigne | Exemple |
|---|---|---|
| Lettre minuscule italique : $x$, $a$, $\eta$ | un **nombre** (scalaire) | $x = 3{,}5$ |
| Minuscule grasse : $\mathbf{x}$, $\mathbf{y}$, $\boldsymbol{\theta}$ | un **vecteur** (colonne par défaut) | $\mathbf{x} = (1, 2, 3)^\top$ |
| Majuscule grasse : $\mathbf{A}$, $\mathbf{X}$ | une **matrice** | $\mathbf{X} \in \mathbb{R}^{n\times p}$ |
| Majuscule italique : $X$, $Y$ | (au chapitre 2) une **variable aléatoire** | $X$ = montant d'un panier |
| Chapeau : $\hat{y}$, $\hat{\theta}$ | une valeur **estimée** ou **prédite** | $\hat{y}_i$ = prédiction pour $i$ |
| Barre : $\bar{x}$ | la **moyenne** | $\bar{x} = \frac1n\sum x_i$ |
| Étoile : $p^\star$, $\theta^\star$ | la valeur **optimale** | $p^\star = 34{,}09$ |
| Exposant $\top$ : $\mathbf{A}^\top$ | la **transposée** (lignes ↔ colonnes) | |
| Exposant $-1$ : $\mathbf{A}^{-1}$ | l'**inverse** d'une matrice | $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$ |

> ⚠️ **Attention aux indices.** $x_i$ est le $i$-ème **élément** d'un vecteur, ou la $i$-ème **observation**. $x_{ij}$ est l'élément de la ligne $i$, colonne $j$ d'une matrice. Mathématiquement on compte à partir de **1** ; en Python, à partir de **0** : $x_1$ s'écrit `x[0]`. C'est la source d'erreur n°1 quand on traduit une formule en code.

### 1.4.2 Ensembles et logique

| Symbole | Se lit | Exemple et sens |
|---|---|---|
| $\mathbb{N}, \mathbb{Z}, \mathbb{Q}, \mathbb{R}$ | entiers naturels, relatifs, rationnels, réels | $\mathbb{R}$ = tous les nombres de la droite |
| $\mathbb{R}^n$ | vecteurs de $n$ nombres réels | $\mathbb{R}^3$ : l'espace usuel |
| $\mathbb{R}^{n\times p}$ | matrices à $n$ lignes et $p$ colonnes | un tableau de données |
| $\in$ | « appartient à » | $3 \in \mathbb{N}$ |
| $\subset$ | « est inclus dans » | $\mathbb{N} \subset \mathbb{R}$ |
| $\cup$, $\cap$ | union, intersection | $A \cup B$ : dans $A$ **ou** $B$ |
| $\emptyset$ | ensemble vide | |
| $\forall$ | « pour tout » | $\forall x \in \mathbb{R},\; x^2 \ge 0$ |
| $\exists$ | « il existe » | $\exists x,\; x^2 = 2$ |
| $\Rightarrow$ | « implique » | $x > 2 \Rightarrow x > 1$ |
| $\Leftrightarrow$ | « si et seulement si » | |
| $:=$ | « est défini comme » | $f(x) := x^2$ |
| $\approx$, $\propto$ | environ égal ; proportionnel à | |

### 1.4.3 Sommes, produits, fonctions

| Symbole | Sens | Équivalent NumPy |
|---|---|---|
| $\sum_{i=1}^n x_i$ | $x_1 + x_2 + \dots + x_n$ | `x.sum()` |
| $\prod_{i=1}^n x_i$ | $x_1 \times x_2 \times \dots \times x_n$ | `x.prod()` |
| $\bar{x} = \frac1n\sum x_i$ | moyenne | `x.mean()` |
| $\max$, $\min$ | plus grande, plus petite valeur | `x.max()`, `x.min()` |
| $\arg\min_\theta f(\theta)$ | **l'argument** $\theta$ qui rend $f$ minimale | `np.argmin(f_values)` |
| $\arg\max$ | idem pour le maximum | `np.argmax` |
| $\lvert x\rvert$ | valeur absolue | `np.abs(x)` |
| $\lfloor x\rfloor$, $\lceil x\rceil$ | partie entière inférieure, supérieure | `np.floor`, `np.ceil` |
| $\exp(x) = e^x$, $\ln x$ | exponentielle, log népérien | `np.exp`, `np.log` |
| $\mathbb{1}[\text{cond}]$ | vaut 1 si la condition est vraie, 0 sinon | `(cond).astype(int)` |
| $f: A\to B$ | $f$ prend ses valeurs de $A$ vers $B$ | |
| $f\circ g$ | composition : $(f\circ g)(x) = f(g(x))$ | |
| $\lim_{x\to a} f(x)$ | limite | |
| $\binom{n}{k}$ | « $k$ parmi $n$ » | `math.comb(n, k)` |
| $n!$ | factorielle | `math.factorial(n)` |

### 1.4.4 Algèbre linéaire et analyse

| Symbole | Sens | Équivalent NumPy |
|---|---|---|
| $\mathbf{u}\cdot\mathbf{v} = \mathbf{u}^\top\mathbf{v}$ | produit scalaire | `u @ v` |
| $\lVert\mathbf{v}\rVert$ ou $\lVert\mathbf{v}\rVert_2$ | norme euclidienne $\sqrt{\sum v_i^2}$ | `np.linalg.norm(v)` |
| $\lVert\mathbf{v}\rVert_1$ | norme 1 : $\sum\lvert v_i\rvert$ | `np.linalg.norm(v, 1)` |
| $\mathbf{A}\mathbf{B}$ | produit matriciel | `A @ B` |
| $\mathbf{A}^\top$ | transposée | `A.T` |
| $\mathbf{A}^{-1}$ | inverse | `np.linalg.inv(A)` (ou mieux : `solve`) |
| $\mathbf{I}$ | matrice identité | `np.eye(n)` |
| $\det\mathbf{A}$ | déterminant | `np.linalg.det(A)` |
| $\operatorname{rang}\mathbf{A}$ | nombre de colonnes indépendantes | `np.linalg.matrix_rank(A)` |
| $\operatorname{tr}\mathbf{A}$ | trace (somme de la diagonale) | `np.trace(A)` |
| $\lambda$, $\mathbf{v}$ | valeur propre, vecteur propre : $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ | `np.linalg.eig(A)` |
| $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$ | décomposition en valeurs singulières | `np.linalg.svd(A)` |
| $f'(x)$ ou $\dfrac{df}{dx}$ | dérivée | |
| $\dfrac{\partial f}{\partial x_j}$ | dérivée partielle | |
| $\nabla f$ | gradient (vecteur des dérivées partielles) | |
| $\nabla^2 f$ ou $\mathbf{H}$ | hessienne (matrice des dérivées secondes) | |
| $\int_a^b f(x)\,dx$ | intégrale (aire sous la courbe) | `scipy.integrate.quad` |

### 1.4.5 L'alphabet grec en data science

Les lettres grecques reviennent partout. Voici celles que vous rencontrerez, avec leur usage **habituel** (pas une règle absolue).

| Lettre | Nom | Usage courant |
|---|---|---|
| $\alpha$ | alpha | niveau de risque d'un test ; ordonnée à l'origine ; paramètre de régularisation |
| $\beta$ | bêta | coefficients d'une régression |
| $\gamma$ | gamma | pas d'apprentissage (parfois) ; fonction Gamma |
| $\delta$, $\Delta$ | delta | une petite variation ; $\Delta x$ = écart |
| $\varepsilon$ | epsilon | une très petite quantité ; l'**erreur** (bruit) d'un modèle |
| $\eta$ | êta | **pas d'apprentissage** (learning rate) |
| $\theta$ | thêta | **paramètres** d'un modèle (ce que l'on apprend) |
| $\lambda$ | lambda | valeur propre ; multiplicateur de Lagrange ; taux d'une loi exponentielle ; force de la régularisation |
| $\mu$ | mu | **moyenne** d'une loi (théorique) |
| $\nu$ | nu | degrés de liberté |
| $\pi$ | pi | 3,14159… ; ou une probabilité |
| $\rho$ | rhô | coefficient de **corrélation** |
| $\sigma$, $\Sigma$ | sigma | **écart-type** ($\sigma$) ; matrice de covariance ($\boldsymbol\Sigma$) ; ⚠️ $\sum$ est la somme, pas la même lettre |
| $\tau$ | tau | un seuil |
| $\phi$, $\varphi$ | phi | densité de la loi normale ($\varphi$) ; une fonction de transformation |
| $\Phi$ | Phi majuscule | fonction de répartition de la loi normale |
| $\chi^2$ | khi-deux | loi et test du khi-deux |
| $\omega$, $\Omega$ | oméga | l'ensemble des issues possibles ($\Omega$) |

> 🧪 **Astuce pour lire une formule inconnue.** (1) Repérez d'abord ce qui est un nombre, un vecteur, une matrice (grâce à la typographie). (2) Cherchez ce qui est *sommé* ou *minimisé*. (3) Remplacez les symboles par un exemple chiffré minuscule ($n = 3$). Une formule devient presque toujours claire sur un exemple à trois éléments.

### 1.4.6 Exemple : lire une formule du début à la fin

Voici la fonction de perte des moindres carrés, que vous connaissez maintenant :

$$\hat{\boldsymbol\theta} = \arg\min_{\boldsymbol\theta}\; \sum_{i=1}^{n}\bigl(y_i - \mathbf{x}_i^\top\boldsymbol\theta\bigr)^2 .$$

Lecture mot à mot : « le vecteur de paramètres estimé $\hat{\boldsymbol\theta}$ est **l'argument $\boldsymbol\theta$ qui minimise** la somme, sur les $n$ observations, du **carré de l'écart** entre la valeur observée $y_i$ et la prédiction $\mathbf{x}_i^\top\boldsymbol\theta$ ». Et en Python :

```python
import numpy as np
x = np.array([1.0, 2.0, 3.0]); y = np.array([2.0, 3.0, 5.0])
X = np.column_stack([x, np.ones_like(x)])
theta_chapeau = np.linalg.solve(X.T @ X, X.T @ y)
print("theta chapeau =", theta_chapeau.round(4))
print("somme des carrés =", round(((y - X @ theta_chapeau) ** 2).sum(), 4))
```
<!--sortie-->
```text
theta chapeau = [1.5    0.3333]
somme des carrés = 0.1667
```

Une formule, une phrase, trois lignes de code : c'est cette triple lecture qui vous rendra autonome.


## 1.5 ➕ Pour aller plus loin : analyse numérique

> 🧭 **Section optionnelle.** Vous pouvez la sauter sans perdre le fil du livre. Mais si un jour votre code donne un résultat « presque juste » et que vous ne comprenez pas pourquoi, c'est ici qu'est la réponse.

Les mathématiques des sections précédentes travaillent avec des nombres **exacts**. Un ordinateur, lui, n'en a pas : il stocke des nombres avec un nombre **fini** de chiffres. L'**analyse numérique** étudie ce que cela change. Bonne nouvelle : on peut tout comprendre avec quelques expériences.

### 1.5.1 Pourquoi 0,1 + 0,2 n'est pas égal à 0,3

> 💡 **Intuition.** En base 10, le nombre $1/3 = 0{,}3333\ldots$ ne s'écrit pas avec un nombre fini de chiffres. Il en va de même en base 2 pour $0{,}1$ : l'ordinateur en garde une **approximation**, très bonne mais pas exacte.

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(f"{0.1:.25f}")
print(f"{0.3:.25f}")
```
<!--sortie-->
```text
0.30000000000000004
False
0.1000000000000000055511151
0.2999999999999999888977698
```

Les nombres décimaux de Python (type `float`) suivent la norme IEEE 754 en **double précision** : 64 bits, soit environ **16 chiffres significatifs**. L'erreur relative maximale d'un arrondi est appelée **epsilon machine** :

```python
import numpy as np
print("epsilon machine :", np.finfo(float).eps)
```
<!--sortie-->
```text
epsilon machine : 2.220446049250313e-16
```

> ✅ **Règle d'or.** On ne compare **jamais** deux flottants avec `==`. On teste s'ils sont *proches* :

```python
import math
print(math.isclose(0.1 + 0.2, 0.3))
print(np.isclose(0.1 + 0.2, 0.3))
```
<!--sortie-->
```text
True
True
```

Autre piège du même type, que nous avons rencontré en préparant ce livre : demander le logarithme de 1000 en base 10.

```python
print(math.log(1000, 10))      # calcule log(1000)/log(10) : deux arrondis
print(math.log10(1000))        # fonction dédiée : exacte ici
```
<!--sortie-->
```text
2.9999999999999996
3.0
```

Morale : quand une fonction **dédiée** existe (`log10`, `expm1`, `hypot`…), elle est plus précise que la formule naïve.

### 1.5.2 Les grands nombres avalent les petits

Additionner un très petit nombre à un très grand peut ne **rien changer** :

```python
print(1e16 + 1 == 1e16)
print(1e15 + 1 == 1e15)
```
<!--sortie-->
```text
True
False
```

Conséquence pratique : l'**ordre** des additions compte. Additionner un million de fois $0{,}1$ ne donne pas exactement 100 000.

```python
s = 0.0
for _ in range(1_000_000):
    s += 0.1
print(s)
print(math.fsum([0.1] * 1_000_000))     # somme compensée : exacte à l'arrondi final
```
<!--sortie-->
```text
100000.00000133288
100000.0
```

### 1.5.3 L'annulation catastrophique

C'est le piège le plus important pour un data scientist. Quand on **soustrait deux nombres presque égaux**, les premiers chiffres s'annulent et il ne reste que… du bruit d'arrondi.

> 💡 **Intuition.** Vous mesurez deux immeubles de 300,00 m et 300,01 m, avec une règle précise au mètre près. Leur différence (0,01 m) est noyée dans l'imprécision.

Exemple réel : le calcul de la **variance**. Il existe deux formules équivalentes en mathématiques :

- formule stable : $\displaystyle \operatorname{Var} = \frac1n\sum (x_i - \bar{x})^2$ ;
- formule « du calcul à la main » : $\displaystyle \operatorname{Var} = \overline{x^2} - \bar{x}^2$ (moyenne des carrés moins carré de la moyenne).

Appliquons les deux à des chiffres d'affaires de l'ordre du milliard, avec une petite dispersion :

```python
rng = np.random.default_rng(0)
x = 1e9 + rng.normal(0, 1, size=1000)          # moyenne ~ 1 milliard, écart-type ~ 1

var_stable = np.mean((x - x.mean()) ** 2)
var_naive  = np.mean(x ** 2) - x.mean() ** 2

print("formule stable :", round(var_stable, 6))
print("formule naive  :", var_naive)
```
<!--sortie-->
```text
formule stable : 0.954046
formule naive  : -128.0
```

La vraie variance vaut environ 1. La formule stable la retrouve (0,95) ; la naïve donne **−128**, une variance *négative*, ce qui est impossible ! Elle est fausse, car $\overline{x^2}\approx 10^{18}$ et $\bar{x}^2\approx 10^{18}$ sont deux nombres presque égaux dont la différence est de l'ordre de 1 : on soustrait des nombres de 18 chiffres avec seulement 16 chiffres de précision.

> ⚠️ **Conséquence.** NumPy et pandas utilisent des algorithmes stables, pas la formule naïve. Moralité : **faites confiance aux fonctions des bibliothèques** plutôt que de recoder des formules vues en cours.

> 📐 **Pourquoi mathématiquement ?** Si $a$ et $b$ sont connus avec une erreur relative $\varepsilon$, leur différence $a-b$ a une erreur **absolue** d'environ $\varepsilon(|a|+|b|)$, donc une erreur **relative** de $\varepsilon\,\dfrac{|a|+|b|}{|a-b|}$. Quand $a \approx b$, le quotient est gigantesque : l'erreur relative explose.

### 1.5.4 Le conditionnement : quand un problème est « fragile »

Certains problèmes sont intrinsèquement sensibles : un minuscule changement des données change beaucoup la réponse. On mesure cette sensibilité par le **nombre de conditionnement** d'une matrice,

$$\kappa(\mathbf{A}) = \frac{\sigma_{\max}}{\sigma_{\min}},$$

le rapport entre sa plus grande et sa plus petite valeur singulière (section 1.1.4). Si $\kappa$ est grand, la matrice est « presque singulière » : c'est exactement le cas de la **multicollinéarité** vue au 1.1.

Voici un système $\mathbf{A}\mathbf{x}=\mathbf{b}$ dont les deux équations sont presque identiques :

```python
A = np.array([[1.0, 1.0],
              [1.0, 1.0001]])
b = np.array([2.0, 2.0001])
print("solution :", np.linalg.solve(A, b))
print("conditionnement :", round(np.linalg.cond(A)))
```
<!--sortie-->
```text
solution : [1. 1.]
conditionnement : 40002
```

Perturbons légèrement le second membre (changement de $10^{-4}$) :

```python
b2 = np.array([2.0, 2.0002])
print("solution perturbée :", np.linalg.solve(A, b2))
```
<!--sortie-->
```text
solution perturbée : [0. 2.]
```

Un changement de $0{,}0001$ sur les données a **complètement changé la solution** : de $(1, 1)$ à $(0, 2)$. Le conditionnement est de l'ordre de 40 000 : on peut perdre jusqu'à 4 à 5 chiffres de précision.

> ✅ **Règle empirique.** Avec $\kappa \approx 10^k$, on perd environ $k$ chiffres significatifs sur les 16 disponibles.

Deux conséquences pratiques :

1. Pour résoudre $\mathbf{A}\mathbf{x}=\mathbf{b}$, on utilise `np.linalg.solve(A, b)`, **pas** `np.linalg.inv(A) @ b` : c'est plus rapide **et** plus précis.
2. Centrer et standardiser les variables (1.3.3) diminue le conditionnement, ce qui explique en partie le gain de 335 à 18 itérations.

```python
x = np.array([1.0, 2.0, 3.0])
X_brut = np.column_stack([x, np.ones(3)])
X_centre = np.column_stack([x - x.mean(), np.ones(3)])
print("kappa(X^T X) brut   :", round(np.linalg.cond(X_brut.T @ X_brut), 1))
print("kappa(X^T X) centré :", round(np.linalg.cond(X_centre.T @ X_centre), 1))
```
<!--sortie-->
```text
kappa(X^T X) brut   : 46.1
kappa(X^T X) centré : 1.5
```

### 1.5.5 Deux algorithmes classiques

**La méthode de Newton pour résoudre $f(x)=0$.** Idée : on remplace la courbe par sa **tangente** (1.2.1) et on prend l'endroit où la tangente coupe l'axe des abscisses :

$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}.$$

Pour calculer $\sqrt{2}$, on cherche le zéro de $f(x) = x^2 - 2$, avec $f'(x) = 2x$ :

```python
x = 1.0
for k in range(6):
    print(f"étape {k} : x = {x:.15f}   erreur = {abs(x - 2**0.5):.2e}")
    x = x - (x**2 - 2) / (2 * x)
```
<!--sortie-->
```text
étape 0 : x = 1.000000000000000   erreur = 4.14e-01
étape 1 : x = 1.500000000000000   erreur = 8.58e-02
étape 2 : x = 1.416666666666667   erreur = 2.45e-03
étape 3 : x = 1.414215686274510   erreur = 2.12e-06
étape 4 : x = 1.414213562374690   erreur = 1.59e-12
étape 5 : x = 1.414213562373095   erreur = 0.00e+00
```

Le nombre de chiffres justes **double** à chaque étape (on parle de convergence quadratique). C'est ainsi que votre calculatrice calcule vraiment les racines carrées.

**La dichotomie.** Plus lente mais beaucoup plus robuste : si $f$ est continue et change de signe entre $a$ et $b$, il existe un zéro entre les deux. On coupe l'intervalle en deux, on garde la moitié qui change de signe, et on recommence. L'erreur est divisée par 2 à chaque tour.

```python
def dichotomie(f, a, b, tol=1e-10):
    n = 0
    while b - a > tol:
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
        n += 1
    return (a + b) / 2, n

racine, n = dichotomie(lambda x: x**2 - 2, 0, 2)
print(f"racine = {racine:.10f} en {n} étapes")
```
<!--sortie-->
```text
racine = 1.4142135624 en 35 étapes
```

Il faut 35 étapes à la dichotomie, contre 5 à Newton, pour une précision comparable. Newton est rapide mais peut diverger si on part mal ; la dichotomie est lente mais ne rate jamais. Les bibliothèques (`scipy.optimize.brentq`) combinent les deux.

> ✅ **À retenir (analyse numérique).**
>
> - Un flottant a ~16 chiffres significatifs ; on compare avec `isclose`, jamais avec `==`.
> - Soustraire deux nombres proches détruit la précision (annulation) : préférez les fonctions de bibliothèque.
> - Le conditionnement $\kappa$ mesure la fragilité d'un problème ; on perd environ $\log_{10}\kappa$ chiffres.
> - `solve` plutôt que `inv`. Centrer et standardiser améliore le conditionnement.
> - Newton : rapide mais capricieux ; dichotomie : lente mais sûre.


## 1.6 ➕ Pour aller plus loin : mathématiques discrètes et graphes

> 🧭 **Section optionnelle.** Tout ce qui précède traitait de quantités qui varient de façon *continue* (prix, temps, pentes). Ici, on compte et on relie : des objets distincts, des choix, des liens. Ces outils servent pour les probabilités (chapitre 2), les algorithmes (chapitre 4), les bases de données (chapitre 5) et les systèmes de recommandation.

### 1.6.1 Ensembles : le langage de base

Un **ensemble** est une collection d'objets distincts, sans ordre. Yasmine propose quatre produits : $P = \{\text{bol}, \text{tapis}, \text{lampe}, \text{plateau}\}$. Ses clients de la semaine ont acheté des sous-ensembles de $P$.

Les opérations de la fiche de notations (1.4.2) se testent directement en Python avec le type `set` :

```python
panier_amel = {"bol", "tapis", "lampe"}
panier_karim = {"bol", "plateau"}

print("union          :", sorted(panier_amel | panier_karim))
print("intersection   :", sorted(panier_amel & panier_karim))
print("amel sans karim:", sorted(panier_amel - panier_karim))
print("taille         :", len(panier_amel))
```
<!--sortie-->
```text
union          : ['bol', 'lampe', 'plateau', 'tapis']
intersection   : ['bol']
amel sans karim: ['lampe', 'tapis']
taille         : 3
```

> 💡 **Application : similarité de Jaccard.** Comment mesurer à quel point deux paniers se ressemblent ? On divise la taille de ce qu'ils ont **en commun** par la taille de ce qu'ils ont **au total** :
>
> $$J(A, B) = \frac{|A\cap B|}{|A\cup B|}.$$
>
> Elle vaut 1 si les paniers sont identiques, 0 s'ils n'ont rien en commun. C'est l'équivalent « ensembliste » de la similarité cosinus du 1.1.1.

```python
def jaccard(a, b):
    return len(a & b) / len(a | b)

print("Jaccard(Amel, Karim) =", round(jaccard(panier_amel, panier_karim), 3))
```
<!--sortie-->
```text
Jaccard(Amel, Karim) = 0.25
```

Un seul produit en commun (le bol), sur quatre produits au total : $1/4 = 0{,}25$.

### 1.6.2 Compter : le principe multiplicatif

> 💡 **Intuition.** Si vous avez 3 pulls et 4 pantalons, vous avez $3\times 4 = 12$ tenues. Quand on enchaîne des choix indépendants, on **multiplie** le nombre d'options.

Yasmine veut proposer un **coffret cadeau** : un produit principal (4 choix), un emballage (3 choix), une carte message (2 choix). Le nombre de coffrets différents est $4\times3\times2 = 24$.

**Permutations.** De combien de façons peut-on **ranger** $n$ objets distincts dans l'ordre ? $n$ choix pour la première place, $n-1$ pour la suivante, etc. :

$$n! = n\times(n-1)\times\dots\times 2\times 1.$$

Les 4 produits peuvent être alignés en vitrine de $4! = 24$ façons.

**Arrangements et combinaisons.** Choisir $k$ objets parmi $n$ :

- *quand l'ordre compte* (podium : 1er, 2e, 3e) : $\dfrac{n!}{(n-k)!}$ ;
- *quand l'ordre ne compte pas* (un panier de 3 produits) :

$$\binom{n}{k} = \frac{n!}{k!\,(n-k)!}.$$

> 📐 **Pourquoi cette formule ?** Il y a $\frac{n!}{(n-k)!}$ façons de choisir $k$ objets *dans l'ordre*. Mais chaque groupe de $k$ objets a été compté $k!$ fois (une fois par ordre possible). On divise donc par $k!$.

```python
import math
print("tenues             :", 3 * 4)
print("coffrets           :", 4 * 3 * 2)
print("ordres de vitrine  :", math.factorial(4))
print("paniers de 2 parmi 4:", math.comb(4, 2))
print("podium 3 parmi 10  :", math.perm(10, 3))
print("paniers de 3 parmi 40:", math.comb(40, 3))
```
<!--sortie-->
```text
tenues             : 12
coffrets           : 24
ordres de vitrine  : 24
paniers de 2 parmi 4: 6
podium 3 parmi 10  : 720
paniers de 3 parmi 40: 9880
```

> 🧪 **Attention à l'explosion.** Si le catalogue contient 40 produits, il y a déjà 9 880 paniers de trois produits. Pour des paniers de dix produits parmi 40, on dépasse les 847 millions :

```python
print(math.comb(40, 10))
```
<!--sortie-->
```text
847660528
```

C'est pourquoi les algorithmes de recommandation ne peuvent pas **énumérer** tous les cas : on y reviendra avec la complexité (section ➕ du chapitre 4).

**Le triangle de Pascal et le binôme.** Les nombres $\binom{n}{k}$ se calculent par la règle $\binom{n}{k}=\binom{n-1}{k-1}+\binom{n-1}{k}$ et vérifient $(a+b)^n=\sum_k\binom{n}{k}a^k b^{n-k}$. Nous les retrouverons au chapitre 2 dans la **loi binomiale**.

### 1.6.3 Les graphes : modéliser des relations

Un **graphe** est un ensemble de **sommets** (des objets) et d'**arêtes** (des liens entre eux). Tout ce qui est « réseau » est un graphe : amis sur un réseau social, routes entre villes, produits souvent achetés ensemble, pages web reliées par des liens.

Voici le graphe des produits **achetés ensemble** dans la boutique : deux produits sont reliés si au moins un client les a pris dans le même panier.

```python
produits = ["bol", "tapis", "lampe", "plateau", "coussin"]
aretes = [("bol", "plateau"), ("bol", "tapis"), ("tapis", "lampe"),
          ("tapis", "coussin"), ("lampe", "coussin")]

# liste d'adjacence : pour chaque sommet, la liste de ses voisins
voisins = {p: [] for p in produits}
for a, b in aretes:
    voisins[a].append(b)
    voisins[b].append(a)

for p in produits:
    print(f"{p:8s} -> {voisins[p]}")
print("degrés :", {p: len(v) for p, v in voisins.items()})
```
<!--sortie-->
```text
bol      -> ['plateau', 'tapis']
tapis    -> ['bol', 'lampe', 'coussin']
lampe    -> ['tapis', 'coussin']
plateau  -> ['bol']
coussin  -> ['tapis', 'lampe']
degrés : {'bol': 2, 'tapis': 3, 'lampe': 2, 'plateau': 1, 'coussin': 2}
```

Le **degré** d'un sommet est son nombre de voisins : le tapis (degré 3) est le produit le plus « connecté », donc un bon candidat pour une promotion croisée.

**La matrice d'adjacence.** On peut ranger le graphe dans une matrice $\mathbf{A}$ : $A_{ij}=1$ si $i$ et $j$ sont reliés, 0 sinon.

```python
import numpy as np
idx = {p: i for i, p in enumerate(produits)}
A = np.zeros((5, 5), dtype=int)
for a, b in aretes:
    A[idx[a], idx[b]] = A[idx[b], idx[a]] = 1
print(A)
print("symétrique :", (A == A.T).all())
```
<!--sortie-->
```text
[[0 1 0 1 0]
 [1 0 1 0 1]
 [0 1 0 0 1]
 [1 0 0 0 0]
 [0 1 1 0 0]]
symétrique : True
```

> 📐 **Propriété remarquable : les puissances de $\mathbf{A}$ comptent les chemins.** L'élément $(\mathbf{A}^k)_{ij}$ est le **nombre de chemins de longueur $k$** entre $i$ et $j$.
>
> *Preuve pour $k=2$.* Par définition du produit matriciel, $(\mathbf{A}^2)_{ij}=\sum_{m} A_{im}A_{mj}$. Le terme $A_{im}A_{mj}$ vaut 1 exactement quand $i$—$m$ et $m$—$j$ sont deux arêtes, c'est-à-dire quand $m$ est un intermédiaire possible. La somme compte donc les intermédiaires, c'est-à-dire les chemins en deux pas. Le cas général se démontre par récurrence sur $k$ avec le même argument. $\blacksquare$

```python
A2 = A @ A
print("chemins de longueur 2 entre bol et lampe :", A2[idx["bol"], idx["lampe"]])
print("chemins de longueur 2 entre tapis et tapis :", A2[idx["tapis"], idx["tapis"]])
A3 = np.linalg.matrix_power(A, 3)
print("trace de A^3 / 6 = nombre de triangles :", np.trace(A3) // 6)
```
<!--sortie-->
```text
chemins de longueur 2 entre bol et lampe : 1
chemins de longueur 2 entre tapis et tapis : 3
trace de A^3 / 6 = nombre de triangles : 1
```

Entre le bol et la lampe, il y a un seul chemin en deux pas (bol → tapis → lampe). Le tapis a trois chemins de longueur 2 vers lui-même : c'est son degré (il part vers un voisin et revient). Et la trace de $\mathbf{A}^3$ compte les triangles (chaque triangle est compté 6 fois : 3 sommets de départ × 2 sens) ; ici on trouve 1 triangle : tapis–lampe–coussin. Un triangle dans un graphe de co-achat signale un trio de produits qui se vendent bien ensemble.

### 1.6.4 Parcourir un graphe : la recherche en largeur

> 💡 **Intuition.** Vous lancez une pierre dans l'eau : les ondes atteignent d'abord les voisins directs, puis les voisins des voisins, etc. La **recherche en largeur** (*BFS*, *breadth-first search*) explore un graphe de la même manière, « cercle par cercle ». Elle trouve le **plus court chemin** (en nombre d'arêtes) entre deux sommets.

L'algorithme utilise une **file** (premier arrivé, premier servi) :

1. Mettre le sommet de départ dans la file, avec la distance 0.
2. Tant que la file n'est pas vide : retirer le premier sommet ; pour chacun de ses voisins non encore vus, noter sa distance (celle du sommet + 1) et le mettre en fin de file.

```python
from collections import deque

def distances_depuis(depart, voisins):
    dist = {depart: 0}
    file = deque([depart])
    while file:
        courant = file.popleft()
        for v in voisins[courant]:
            if v not in dist:
                dist[v] = dist[courant] + 1
                file.append(v)
    return dist

print(distances_depuis("plateau", voisins))
```
<!--sortie-->
```text
{'plateau': 0, 'bol': 1, 'tapis': 2, 'lampe': 3, 'coussin': 3}
```

Depuis le plateau : le bol est à distance 1, le tapis à 2, la lampe et le coussin à 3. Si un client achète un plateau, la « chaîne de recommandations » la plus courte vers une lampe passe par le bol puis le tapis.

> ✅ **À retenir (discret et graphes).**
>
> - Ensembles : $\cup$, $\cap$, $\setminus$ ; Jaccard $=|A\cap B|/|A\cup B|$.
> - Principe multiplicatif ; $n!$ ordres ; $\binom{n}{k}$ choix sans ordre ; ça explose très vite.
> - Un graphe = sommets + arêtes ; le stocker en **liste d'adjacence** ou en **matrice d'adjacence**.
> - $(\mathbf{A}^k)_{ij}$ = nombre de chemins de longueur $k$ de $i$ à $j$.
> - BFS : exploration par cercles, plus courts chemins sur graphe non pondéré.


## 1.7 Exercices du chapitre 1

> 🧭 **Mode d'emploi.** Essayez chaque exercice **sur papier ou dans un notebook avant** de lire le corrigé. Les exercices sont rangés par difficulté croissante : ⭐ (application directe), ⭐⭐ (demande un raisonnement), ⭐⭐⭐ (synthèse). Les corrigés sont juste après l'énoncé de la série, avec le calcul à la main **et** la vérification par code.

### Énoncés

**Exercice 1 ⭐ (cosinus).** Deux clientes sont décrites par leurs achats (bols, tapis, lampes) : $\mathbf{u}=(1,2,2)$ et $\mathbf{v}=(2,0,1)$. Calculez leur similarité cosinus. Sont-elles plutôt semblables ?

**Exercice 2 ⭐ (produit matriciel et système).** Soit $\mathbf{A}=\begin{pmatrix}2&1\\1&3\end{pmatrix}$ et $\mathbf{b}=\begin{pmatrix}5\\10\end{pmatrix}$. (a) Calculez $\mathbf{A}^2$. (b) Résolvez $\mathbf{A}\mathbf{x}=\mathbf{b}$ à la main (par substitution), puis vérifiez avec NumPy.

**Exercice 3 ⭐⭐ (valeurs propres).** Trouvez les valeurs propres et des vecteurs propres de $\mathbf{M}=\begin{pmatrix}4&1\\2&3\end{pmatrix}$. Vérifiez que la trace est la somme et le déterminant le produit des valeurs propres.

**Exercice 4 ⭐ (dérivées).** Pour $f(x)=x^3-6x^2+9x$, calculez $f'$, trouvez les points où la pente est nulle, et déterminez s'il s'agit de minima ou de maxima grâce à $f''$.

**Exercice 5 ⭐⭐ (gradient).** Pour $f(x,y)=x^2+3y^2$, calculez le gradient en $(1,1)$ puis effectuez **un pas** de descente de gradient avec $\eta=0{,}1$. La valeur de $f$ a-t-elle diminué ?

**Exercice 6 ⭐⭐ (pas d'apprentissage).** Soit $f(x)=2(x-1)^2$. (a) Écrivez la récurrence de la descente de gradient. (b) Pour quelles valeurs de $\eta$ converge-t-elle ? (c) Quelle valeur de $\eta$ converge en un seul pas ?

**Exercice 7 ⭐⭐ (Lagrange).** Yasmine dispose de 10 mètres de ruban pour entourer un rectangle de tissu. Quel rectangle d'aire maximale peut-on former ? Utilisez un multiplicateur de Lagrange, c'est-à-dire maximisez $xy$ sous la contrainte $x+y=5$ (demi-périmètre), et interprétez $\lambda$.

**Exercice 8 ⭐⭐⭐ (Python : régression à la main).** Les ventes de bougies en fonction de la température sont : $x=(10,15,20,25)$ et $y=(40,35,28,22)$. (a) Ajustez la droite $y=ax+b$ avec les équations normales. (b) Retrouvez le résultat par descente de gradient sur la variable **centrée**. (c) Prédisez les ventes à 18 °C.

**Exercice 9 ⭐⭐ (analyse numérique).** Expliquez pourquoi `0.1 * 3 == 0.3` est faux en Python et écrivez le test correct. Puis donnez la formule du nombre de chiffres perdus pour un conditionnement $\kappa=10^6$.

**Exercice 10 ⭐⭐ (graphes).** Dans le graphe de co-achat du 1.6, calculez avec $\mathbf{A}^2$ le nombre de chemins de longueur 2 entre « plateau » et « tapis », puis entre « bol » et « coussin ». Vérifiez en les énumérant à la main.

### Corrigés

**Corrigé 1.** $\mathbf{u}\cdot\mathbf{v}=1\cdot2+2\cdot0+2\cdot1=4$. $\lVert\mathbf{u}\rVert=\sqrt{1+4+4}=3$, $\lVert\mathbf{v}\rVert=\sqrt{4+0+1}=\sqrt5$. Donc $\cos\theta=\dfrac{4}{3\sqrt5}\approx0{,}596$.

```python
import numpy as np
u = np.array([1, 2, 2]); v = np.array([2, 0, 1])
cos = u @ v / (np.linalg.norm(u) * np.linalg.norm(v))
print("cosinus =", round(cos, 3), "  angle =", round(np.degrees(np.arccos(cos)), 1), "degrés")
```
<!--sortie-->
```text
cosinus = 0.596   angle = 53.4 degrés
```

Un cosinus de 0,6 correspond à un angle d'environ 53° : **moyennement semblables** (1 = identiques, 0 = rien en commun). Elles aiment toutes deux les bols mais diffèrent sur les tapis.

**Corrigé 2.** (a) $\mathbf{A}^2=\begin{pmatrix}2\cdot2+1\cdot1&2\cdot1+1\cdot3\\1\cdot2+3\cdot1&1\cdot1+3\cdot3\end{pmatrix}=\begin{pmatrix}5&5\\5&10\end{pmatrix}$. (b) Les équations sont $2x+y=5$ et $x+3y=10$. De la première : $y=5-2x$. En remplaçant : $x+15-6x=10$, donc $-5x=-5$, $x=1$ et $y=3$.

```python
A = np.array([[2, 1], [1, 3]]); b = np.array([5, 10])
print(A @ A)
print("solution :", np.linalg.solve(A, b))
```
<!--sortie-->
```text
[[ 5  5]
 [ 5 10]]
solution : [1. 3.]
```

**Corrigé 3.** Le polynôme caractéristique est $\det(\mathbf{M}-\lambda\mathbf{I})=(4-\lambda)(3-\lambda)-2=\lambda^2-7\lambda+10=(\lambda-5)(\lambda-2)$. Les valeurs propres sont $5$ et $2$. Pour $\lambda=5$ : $(\mathbf{M}-5\mathbf{I})\mathbf{v}=\begin{pmatrix}-1&1\\2&-2\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,1)$. Pour $\lambda=2$ : $\begin{pmatrix}2&1\\2&1\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,-2)$. Trace : $4+3=7=5+2$ ✓. Déterminant : $4\cdot3-1\cdot2=10=5\times2$ ✓.

```python
M = np.array([[4, 1], [2, 3]])
valeurs, vecteurs = np.linalg.eig(M)
print("valeurs propres :", np.sort(valeurs.real))
print("trace =", np.trace(M), "  det =", round(np.linalg.det(M), 6))
print("M @ (1,1) =", M @ np.array([1, 1]), " = 5 * (1,1)")
```
<!--sortie-->
```text
valeurs propres : [2. 5.]
trace = 7   det = 10.0
M @ (1,1) = [5 5]  = 5 * (1,1)
```

**Corrigé 4.** $f'(x)=3x^2-12x+9=3(x-1)(x-3)$, nulle en $x=1$ et $x=3$. $f''(x)=6x-12$. En $x=1$ : $f''=-6<0$, c'est un **maximum local** ($f(1)=4$). En $x=3$ : $f''=6>0$, c'est un **minimum local** ($f(3)=0$).

```python
f = lambda x: x**3 - 6*x**2 + 9*x
print("f(1) =", f(1), " f(3) =", f(3))
```
<!--sortie-->
```text
f(1) = 4  f(3) = 0
```

**Corrigé 5.** $\nabla f=(2x,\,6y)$, donc $\nabla f(1,1)=(2,6)$. Le pas : $(1,1)-0{,}1\,(2,6)=(0{,}8;\,0{,}4)$. Avant : $f(1,1)=1+3=4$. Après : $f(0{,}8;0{,}4)=0{,}64+3\cdot0{,}16=1{,}12$. La valeur a bien diminué (de 4 à 1,12).

```python
grad = lambda p: np.array([2 * p[0], 6 * p[1]])
f2 = lambda p: p[0]**2 + 3 * p[1]**2
p = np.array([1.0, 1.0])
p_nouveau = p - 0.1 * grad(p)
print(p_nouveau, f2(p), round(f2(p_nouveau), 2))
```
<!--sortie-->
```text
[0.8 0.4] 4.0 1.12
```

**Corrigé 6.** (a) $f'(x)=4(x-1)$, donc $x_{k+1}=x_k-4\eta(x_k-1)$, soit $x_{k+1}-1=(1-4\eta)(x_k-1)$. (b) L'écart à 1 est multiplié par $(1-4\eta)$ à chaque pas ; il tend vers 0 si $|1-4\eta|<1$, c'est-à-dire $0<\eta<\tfrac12$. (On retrouve $\eta<2/\lambda_{\max}$ avec $f''=4$.) (c) Le facteur est nul si $\eta=\tfrac14$ : on tombe sur le minimum en un seul pas.

```python
for eta in (0.1, 0.25, 0.45, 0.5, 0.55):
    x = 5.0
    for _ in range(20):
        x = x - eta * 4 * (x - 1)
    print(f"eta = {eta:<5} -> x après 20 pas = {x:.6g}")
```
<!--sortie-->
```text
eta = 0.1   -> x après 20 pas = 1.00015
eta = 0.25  -> x après 20 pas = 1
eta = 0.45  -> x après 20 pas = 1.04612
eta = 0.5   -> x après 20 pas = 5
eta = 0.55  -> x après 20 pas = 154.35
```

**Corrigé 7.** On maximise $g(x,y)=xy$ sous $x+y=5$. Lagrangien : $\mathcal{L}=xy-\lambda(x+y-5)$. Les conditions $\partial_x\mathcal{L}=y-\lambda=0$ et $\partial_y\mathcal{L}=x-\lambda=0$ donnent $x=y=\lambda$. La contrainte donne $2\lambda=5$, donc $x=y=2{,}5$ m : le **carré** de 2,5 m de côté, d'aire $6{,}25\ \text{m}^2$. Le multiplicateur $\lambda=2{,}5$ s'interprète comme le prix de l'ombre : un mètre de demi-périmètre en plus rapporte environ 2,5 m² d'aire en plus (l'aire optimale est $(c/2)^2$ et sa dérivée par rapport à $c$ est $c/2=2{,}5$).

```python
from scipy.optimize import minimize
res = minimize(lambda v: -v[0] * v[1], x0=[1, 1],
               constraints={"type": "eq", "fun": lambda v: v[0] + v[1] - 5})
print(res.x.round(3), "aire =", round(-res.fun, 3))
```
<!--sortie-->
```text
[2.5 2.5] aire = 6.25
```

**Corrigé 8.** (a) On construit $\mathbf{X}$ avec une colonne $x$ et une colonne de 1, puis on résout $\mathbf{X}^\top\mathbf{X}\boldsymbol\theta=\mathbf{X}^\top\mathbf{y}$. (b) On centre $x$ (moyenne 17,5), on descend le gradient, puis on revient à l'ordonnée d'origine par $b=b'-a\bar{x}$. (c) On évalue la droite en 18. Attention au pas : la hessienne vaut ici $2\mathbf{X}_c^\top\mathbf{X}_c=\operatorname{diag}(250,\,8)$, donc il faut $\eta<2/250=0{,}008$ ; nous prendrons $\eta=0{,}003$.

```python
x = np.array([10, 15, 20, 25.0]); y = np.array([40, 35, 28, 22.0])
X = np.column_stack([x, np.ones_like(x)])
a, b = np.linalg.solve(X.T @ X, X.T @ y)
print(f"(a) a = {a:.3f}  b = {b:.3f}")

xc = x - x.mean()
Xc = np.column_stack([xc, np.ones_like(xc)])
theta = np.zeros(2)
for _ in range(500):
    theta = theta - 0.003 * (-2 * Xc.T @ (y - Xc @ theta))
a2, b2 = theta[0], theta[1] - theta[0] * x.mean()
print(f"(b) a = {a2:.3f}  b = {b2:.3f}")
print("(c) ventes à 18 °C :", round(a * 18 + b, 1))
```
<!--sortie-->
```text
(a) a = -1.220  b = 52.600
(b) a = -1.220  b = 52.600
(c) ventes à 18 °C : 30.6
```

Lecture : chaque degré de plus fait perdre environ 1,2 ventes de bougies ; à 18 °C on prévoit environ 31 bougies.

**Corrigé 9.** Le nombre $0{,}1$ n'a pas d'écriture finie en base 2 ; `0.1 * 3` vaut `0.30000000000000004`, un flottant différent de celui de `0.3`. Le bon test est `math.isclose(0.1 * 3, 0.3)`. Pour $\kappa=10^6$ on perd environ $\log_{10}\kappa=6$ chiffres significatifs sur les 16 disponibles : il en reste environ 10.

```python
import math
print(0.1 * 3, 0.1 * 3 == 0.3, math.isclose(0.1 * 3, 0.3))
```
<!--sortie-->
```text
0.30000000000000004 False True
```

**Corrigé 10.** Avec l'ordre des produits `["bol","tapis","lampe","plateau","coussin"]` (indices 0 à 4), on lit $(\mathbf{A}^2)_{\text{plateau},\text{tapis}}$ et $(\mathbf{A}^2)_{\text{bol},\text{coussin}}$. À la main : plateau—bol—tapis est le seul chemin en deux pas du plateau au tapis (le plateau n'a qu'un voisin, le bol), donc 1. Bol—tapis—coussin est le seul chemin en deux pas du bol au coussin (les voisins du bol sont plateau et tapis ; seul le tapis touche le coussin), donc 1.

```python
produits = ["bol", "tapis", "lampe", "plateau", "coussin"]
aretes = [("bol", "plateau"), ("bol", "tapis"), ("tapis", "lampe"),
          ("tapis", "coussin"), ("lampe", "coussin")]
idx = {p: i for i, p in enumerate(produits)}
A = np.zeros((5, 5), dtype=int)
for a_, b_ in aretes:
    A[idx[a_], idx[b_]] = A[idx[b_], idx[a_]] = 1
A2 = A @ A
print("plateau-tapis :", A2[idx["plateau"], idx["tapis"]])
print("bol-coussin   :", A2[idx["bol"], idx["coussin"]])
```
<!--sortie-->
```text
plateau-tapis : 1
bol-coussin   : 1
```

---

## Bilan du chapitre 1

Vous savez maintenant :

- **représenter** des données comme des vecteurs et des matrices, mesurer des ressemblances (produit scalaire, cosinus), résoudre des systèmes et comprendre le rang ;
- **décomposer** une matrice (valeurs propres, SVD) pour en extraire la structure — l'idée derrière l'ACP ;
- **dériver** et calculer un gradient pour savoir comment une quantité réagit à ses paramètres ;
- **optimiser** : écrire une fonction de perte, la minimiser par descente de gradient, gérer les contraintes avec Lagrange ;
- **lire** une formule grâce à la fiche de notations, et **se méfier** des arrondis de l'ordinateur.

Le chapitre 2 change de point de vue : jusqu'ici, nos nombres étaient certains. Désormais ils seront **aléatoires**, et il faudra apprendre à raisonner dans l'incertitude.
