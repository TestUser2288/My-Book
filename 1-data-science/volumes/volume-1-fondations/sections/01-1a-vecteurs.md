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

La boutique compte, pour chaque client, le nombre d'achats dans trois catégories : **poteries**, **textiles**, **bijoux**. Chaque client devient un vecteur à trois composantes :

| Client | Poteries | Textiles | Bijoux | Vecteur |
|---|---|---|---|---|
| Alix | 3 | 1 | 0 | $\mathbf{a} = (3, 1, 0)$ |
| Basile | 6 | 2 | 0 | $\mathbf{b} = (6, 2, 0)$ |
| Camille | 0 | 1 | 4 | $\mathbf{c} = (0, 1, 4)$ |

On note $\mathbf{a} = (a_1, a_2, \dots, a_p)$ un vecteur à $p$ composantes, et $\mathbb{R}^p$ l'ensemble de tous les vecteurs à $p$ composantes réelles. Ici $p = 3$ : nos clients vivent dans $\mathbb{R}^3$.

> ✅ **Convention du livre.** Un nombre seul (un *scalaire*) s'écrit en italique : $a$, $\lambda$. Un vecteur s'écrit en gras minuscule : $\mathbf{a}$. Une matrice s'écrit en gras majuscule : $\mathbf{A}$.

#### Les opérations de base

**Addition.** On additionne composante par composante. Si Alix et Camille regroupent leurs achats :

$$\mathbf{a} + \mathbf{c} = (3+0,\; 1+1,\; 0+4) = (3, 2, 4).$$

**Multiplication par un scalaire.** On multiplie chaque composante :

$$2\,\mathbf{a} = (2 \times 3,\; 2 \times 1,\; 2 \times 0) = (6, 2, 0) = \mathbf{b}.$$

Regardez bien : **Basile est exactement « deux fois Alix »**. Il achète les mêmes choses dans les mêmes proportions, simplement en plus grande quantité. Nous allons voir comment la mathématique capture cette idée.

**Combinaison linéaire.** Combiner les deux opérations donne une *combinaison linéaire* : $\lambda_1 \mathbf{u}_1 + \lambda_2 \mathbf{u}_2$. Par exemple, « la moitié d'Alix plus un tiers de Camille » est $\tfrac12 \mathbf{a} + \tfrac13 \mathbf{c}$. Presque tout ce que nous ferons en modélisation est une combinaison linéaire de quelque chose.

Pour manipuler ces vecteurs sur un ordinateur, la bibliothèque Python **NumPy** les traite comme des objets à part entière (un tout petit aperçu, le chapitre 4 y reviendra en détail) :

```python
import numpy as np

alix   = np.array([3, 1, 0])
basile  = np.array([6, 2, 0])
camille = np.array([0, 1, 4])

print("Alix + Camille :", alix + camille)
print("2 x Alix      :", 2 * alix)
print("Basile == 2 x Alix ?", np.array_equal(basile, 2 * alix))
```
<!--sortie-->
```text
Alix + Camille : [3 2 4]
2 x Alix      : [6 2 0]
Basile == 2 x Alix ? True
```

#### Le produit scalaire : mesurer l'accord entre deux vecteurs

Le **produit scalaire** de deux vecteurs de même taille est la somme des produits des composantes :

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{p} a_i b_i = a_1 b_1 + a_2 b_2 + \dots + a_p b_p.$$

> 🧪 **Exemple à la main.**
>
> $\mathbf{a} \cdot \mathbf{b} = 3 \times 6 + 1 \times 2 + 0 \times 0 = 18 + 2 + 0 = 20.$
>
> $\mathbf{a} \cdot \mathbf{c} = 3 \times 0 + 1 \times 1 + 0 \times 4 = 0 + 1 + 0 = 1.$

> 💡 **Intuition.** Le produit scalaire est grand quand les deux vecteurs « vont dans le même sens » (ils ont des composantes fortes aux mêmes endroits), proche de 0 quand ils n'ont rien en commun, et négatif quand ils s'opposent. Alix et Basile s'entendent bien (20) ; Alix et Camille presque pas (1) : le seul point commun est un textile.

La **norme** d'un vecteur est sa longueur, donnée par le théorème de Pythagore généralisé :

$$\|\mathbf{a}\| = \sqrt{\mathbf{a} \cdot \mathbf{a}} = \sqrt{a_1^2 + a_2^2 + \dots + a_p^2}.$$

Pour nos clients : $\|\mathbf{a}\| = \sqrt{9 + 1 + 0} = \sqrt{10} \approx 3{,}162$, $\|\mathbf{b}\| = \sqrt{36 + 4} = \sqrt{40} \approx 6{,}325$ et $\|\mathbf{c}\| = \sqrt{0 + 1 + 16} = \sqrt{17} \approx 4{,}123$. On remarque que $\|\mathbf{b}\| = 2\|\mathbf{a}\|$ : doubler un vecteur double sa longueur.

Le produit scalaire a aussi une **interprétation géométrique** qui est fondamentale :

$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\|\,\|\mathbf{b}\|\cos\theta,$$

où $\theta$ est l'angle entre les deux flèches. En isolant le cosinus, on obtient la **similarité cosinus** :

$$\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\|\,\|\mathbf{b}\|}.$$

> 🧪 **Exemple à la main.**
>
> - Alix et Basile : $\cos\theta = \dfrac{20}{\sqrt{10}\,\sqrt{40}} = \dfrac{20}{\sqrt{400}} = \dfrac{20}{20} = 1$. Même direction : **mêmes goûts**.
> - Alix et Camille : $\cos\theta = \dfrac{1}{\sqrt{10}\,\sqrt{17}} = \dfrac{1}{\sqrt{170}} \approx 0{,}077$. Presque perpendiculaires : **goûts très différents**.

La similarité cosinus ignore la *taille* des vecteurs et ne regarde que leur *direction*. C'est exactement ce que l'on veut pour comparer des profils d'achat : un gros acheteur et un petit acheteur qui ont les mêmes goûts doivent apparaître comme semblables.

```python hide
def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("cos(Alix, Basile)  =", round(cosinus(alix, basile), 4))
print("cos(Alix, Camille) =", round(cosinus(alix, camille), 4))
```
<!--sortie-->
```text
cos(Alix, Basile)  = 1.0
cos(Alix, Camille) = 0.0767
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
> L'égalité (cosinus égal à ±1) a lieu exactement quand le discriminant est nul, c'est-à-dire quand il existe un $t$ tel que $\mathbf{a} = t\,\mathbf{b}$ : les deux vecteurs sont alignés. C'est le cas d'Alix et Basile.

#### La distance entre deux vecteurs

La **distance euclidienne** entre deux individus est la norme de leur différence :

$$d(\mathbf{a}, \mathbf{b}) = \|\mathbf{a} - \mathbf{b}\| = \sqrt{\sum_{i=1}^{p}(a_i - b_i)^2}.$$

> 🧪 **Exemple.**
>
> - $d(\mathbf{a}, \mathbf{b}) = \|(3-6,\, 1-2,\, 0-0)\| = \|(-3, -1, 0)\| = \sqrt{10} \approx 3{,}162.$
> - $d(\mathbf{a}, \mathbf{c}) = \|(3-0,\, 1-1,\, 0-4)\| = \|(3, 0, -4)\| = \sqrt{9 + 0 + 16} = 5.$

```python hide
print("distance(Alix, Basile)  =", round(np.linalg.norm(alix - basile), 3))
print("distance(Alix, Camille) =", round(np.linalg.norm(alix - camille), 3))
```
<!--sortie-->
```text
distance(Alix, Basile)  = 3.162
distance(Alix, Camille) = 5.0
```

Remarquez la nuance. Selon le **cosinus**, Alix et Basile sont *identiques* (1) ; selon la **distance**, ils sont *à 3,16 unités l'un de l'autre*, parce que Basile achète plus. Ni l'une ni l'autre mesure n'est « la bonne » : elles répondent à des questions différentes.

| Mesure | Elle répond à… | À utiliser quand… |
|---|---|---|
| **Cosinus** | « Ont-ils les mêmes goûts ? » | seule la *proportion* compte (profils, textes, recommandations) |
| **Distance** | « Sont-ils proches en valeur absolue ? » | la *quantité* compte (regroupement par niveau de dépense, par exemple) |

> ⚠️ **Piège : les unités.** La distance additionne des carrés de différences, donc une variable exprimée en grands nombres écrase les autres. Soit trois clients décrits par (âge, panier moyen en €) : $P = (30,\; 100)$, $Q = (60,\; 102)$ et $R = (31,\; 160)$.
>
> - $d(P, Q) = \sqrt{30^2 + 2^2} = \sqrt{904} \approx 30{,}1$
> - $d(P, R) = \sqrt{1^2 + 60^2} = \sqrt{3601} \approx 60{,}0$
>
> Selon la distance, $P$ (30 ans) ressemble davantage à $Q$ (60 ans) qu'à $R$ (31 ans), simplement parce que 60 euros « pèsent » plus que 30 ans dans le calcul ! La cause : les deux variables n'ont pas la même échelle. Le remède est de **standardiser** les variables avant de les comparer, ce que nous ferons au chapitre 3.

> ✅ **À retenir (vecteurs).**
>
> - Un individu est un vecteur ; ses composantes sont ses caractéristiques.
> - Le produit scalaire $\sum a_i b_i$ mesure l'accord entre deux vecteurs ; la norme mesure leur longueur.
> - Le cosinus compare les **directions**, la distance compare les **positions**. Toujours se demander laquelle des deux correspond à la question posée.
> - Avant de comparer des variables d'échelles différentes, on les standardise.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.1.
