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

```python hide
import numpy as np

x = np.array([1, 2, 3, 4])
y = np.array([22, 41, 66, 79])
X = np.column_stack([np.ones(4), x])          # la colonne de 1, puis x

XtX = X.T @ X
Xty = X.T @ y
beta = np.linalg.solve(XtX, Xty)              # résout (X'X) beta = X'y

print("X'X =\n", XtX)
print("X'y =", Xty)
print("beta chapeau =", beta)

ajuste = X @ beta
residus = y - ajuste
print("valeurs ajustées :", ajuste)
print("résidus          :", residus.round(2))
print("somme des résidus        :", round(residus.sum(), 10))
print("somme des carrés (SCR)   :", round((residus**2).sum(), 2))
```
<!--sortie-->
```text
X'X =
 [[ 4. 10.]
 [10. 30.]]
X'y = [208. 618.]
beta chapeau = [ 3.  19.6]
valeurs ajustées : [22.6 42.2 61.8 81.4]
résidus          : [-0.6 -1.2  4.2 -2.4]
somme des résidus        : 0.0
somme des carrés (SCR)   : 25.2
```

En pratique, un logiciel ne calcule pas l'inverse de $\mathbf X^\top\mathbf X$ : il **résout** le système $\mathbf X^\top\mathbf X\,\boldsymbol\beta=\mathbf X^\top\mathbf y$, ce qui est plus rapide et surtout **plus précis** (c'est la leçon de la section 1.5.4 du volume I sur le conditionnement). Voyons le résultat en image.

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

fig, ax = plt.subplots(figsize=(6.4, 4.2))
xs = np.linspace(0.6, 4.4, 50)
ax.plot(xs, beta[0] + beta[1] * xs, color=BLEU, lw=2)
ax.scatter(x, y, color=ENCRE, zorder=3, s=40)
for xi, yi, ai in zip(x, y, ajuste):
    ax.plot([xi, xi], [yi, ai], color=ORANGE, lw=2)             # le résidu : un segment vertical
for xi, yi, nom in zip(x, y, "ABCD"):
    ax.annotate(nom, (xi, yi), textcoords="offset points", xytext=(-12, 4), color=ENCRE)
ax.text(2.45, 30, "droite des moindres carrés\nŷ = 3 + 19,6 x", color=BLEU)
ax.text(3.08, 60, "résidu", color=ORANGE)
ax.set_xlabel("nombre d'articles")
ax.set_ylabel("montant de la commande (€)")
ax.set_xlim(0.5, 4.6)
ax.set_ylim(10, 95)
plt.savefig("figures/ch01-droite-4-points.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Quatre commandes, la droite des moindres carrés et les résidus (segments verticaux). La droite est celle qui minimise la somme des carrés de ces segments.](figures/ch01-droite-4-points.png)

> 🧪 **Deux propriétés à remarquer.** (1) La somme des résidus est nulle (aux erreurs d'arrondi près). (2) Le produit $\mathbf X^\top\mathbf e$ est nul : les résidus sont *orthogonaux* à chaque colonne de $\mathbf X$. Nous les démontrons en 1.1.3 et 1.1.4, et elles joueront un rôle central.

```python hide
print("X' e =", (X.T @ residus).round(10))
```
<!--sortie-->
```text
X' e = [ 0. -0.]
```

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

```python hide
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.set_xlim(-0.3, 6.6); ax.set_ylim(-0.9, 3.9); ax.set_aspect("equal"); ax.axis("off")
ax.plot([0, 6.2], [0, 1.24], color=GRIS, lw=4, alpha=0.45, solid_capstyle="round")
ax.text(0.1, -0.5, "sous-espace engendré par les colonnes de X", color=GRIS)
yv = np.array([4.0, 3.2])
d = np.array([5.0, 1.0]) / np.linalg.norm([5.0, 1.0])                  # direction du sous-espace
pv = (yv @ d) * d                                                       # projeté orthogonal de y
ax.annotate("", xy=yv, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ENCRE, lw=2))
ax.annotate("", xy=pv, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLEU, lw=2))
ax.plot([yv[0], pv[0]], [yv[1], pv[1]], color=ORANGE, lw=2, ls="--")
n = np.array([-d[1], d[0]])                                             # petit carré : angle droit en ŷ
c = 0.22
ax.plot([pv[0] + c * d[0] * -1, pv[0] - c * d[0] + c * n[0], pv[0] + c * n[0]],
        [pv[1] + c * d[1] * -1, pv[1] - c * d[1] + c * n[1], pv[1] + c * n[1]], color=ORANGE, lw=1.2)
ax.text(yv[0] + 0.12, yv[1] + 0.05, "y  (les données)", color=ENCRE)
ax.text(pv[0] + 0.15, pv[1] - 0.55, "ŷ = Xβ̂\n(meilleur point du modèle)", color=BLEU)
ax.text(pv[0] + 0.25, 2.0, "résidu ε̂\n(perpendiculaire)", color=ORANGE)
plt.savefig("figures/ch01-projection.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

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

```python hide
H = X @ np.linalg.inv(X.T @ X) @ X.T
print("H (arrondie) =\n", H.round(2))
print("symétrique :", np.allclose(H, H.T), "| idempotente :", np.allclose(H @ H, H))
print("trace de H =", round(np.trace(H), 6), "(= p = 2)")
print("H y = valeurs ajustées :", np.allclose(H @ y, ajuste))
print("Pythagore : ||y||² =", int(y @ y), "= ||ŷ||² + ||ε̂||² =", round(ajuste @ ajuste + residus @ residus, 6))
```
<!--sortie-->
```text
H (arrondie) =
 [[ 0.7  0.4  0.1 -0.2]
 [ 0.4  0.3  0.2  0.1]
 [ 0.1  0.2  0.3  0.4]
 [-0.2  0.1  0.4  0.7]]
symétrique : True | idempotente : True
trace de H = 2.0 (= p = 2)
H y = valeurs ajustées : True
Pythagore : ||y||² = 12762 = ||ŷ||² + ||ε̂||² = 12762.0
```

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

```python hide
rng = np.random.default_rng(1)
beta_vrai, sigma = np.array([3.0, 20.0]), 3.0
R = 20000
Y = X @ beta_vrai + rng.normal(0, sigma, size=(R, 4))          # R échantillons de 4 montants (une ligne chacun)
Bhat = np.linalg.solve(X.T @ X, X.T @ Y.T).T                    # R estimations de beta
Res = Y - Bhat @ X.T
SCR = (Res**2).sum(axis=1)

print("moyenne des beta chapeau :", Bhat.mean(axis=0).round(3), "  (vrai :", beta_vrai, ")")
print("variances observées      :", Bhat.var(axis=0, ddof=1).round(3))
print("variances théoriques     :", (sigma**2 * np.diag(np.linalg.inv(X.T @ X))).round(3))
print("covariance observée      :", np.cov(Bhat.T)[0, 1].round(3), "| théorique :", (sigma**2 * np.linalg.inv(X.T @ X))[0, 1].round(3))
print()
print("sigma² vrai              :", sigma**2)
print("moyenne de SCR/(n-p)     :", (SCR / 2).mean().round(3), "  <- sans biais")
print("moyenne de SCR/n         :", (SCR / 4).mean().round(3), "  <- sous-estime, facteur (n-p)/n = 0,5")
```
<!--sortie-->
```text
moyenne des beta chapeau : [ 2.978 20.003]   (vrai : [ 3. 20.] )
variances observées      : [13.18   1.774]
variances théoriques     : [13.5  1.8]
covariance observée      : -4.414 | théorique : -4.5

sigma² vrai              : 9.0
moyenne de SCR/(n-p)     : 9.07   <- sans biais
moyenne de SCR/n         : 4.535   <- sous-estime, facteur (n-p)/n = 0,5
```

Les moyennes des $\hat\beta_j$ (2,978 et 20,003) sont proches des vraies valeurs (3 et 20 : absence de biais) ; les variances observées (13,18 et 1,77) et la covariance (−4,41) sont très proches de celles de $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ (13,5 ; 1,8 et −4,5) ; et la division par $n-p$ donne une estimation centrée de $\sigma^2$ (9,07 en moyenne, pour une vraie valeur de 9) alors que la division par $n$ la sous-estime d'un facteur $(n-p)/n=1/2$ (4,54). La théorie est confirmée par l'expérience.

### 1.1.6 Décomposition de la variance et coefficient de détermination $R^2$

Combien le modèle explique-t-il ? Mesurons la dispersion de $\mathbf y$ autour de sa moyenne par la **somme des carrés totale** $\text{SCT}=\sum_i(y_i-\bar y)^2$. La régression la décompose en une partie expliquée et une partie résiduelle.

> 📐 **Théorème (décomposition de la variance).** Si le modèle contient une constante, alors
> $$\underbrace{\sum_i(y_i-\bar y)^2}_{\text{SCT}}=\underbrace{\sum_i(\hat y_i-\bar y)^2}_{\text{SCE (expliquée)}}+\underbrace{\sum_i\hat\varepsilon_i^2}_{\text{SCR (résiduelle)}}.$$
> *Démonstration.* Écrivons $y_i-\bar y=(\hat y_i-\bar y)+\hat\varepsilon_i$ et élevons au carré : le double produit vaut $2\sum_i(\hat y_i-\bar y)\hat\varepsilon_i=2\sum_i\hat y_i\hat\varepsilon_i-2\bar y\sum_i\hat\varepsilon_i$. Le premier terme est nul car $\hat{\mathbf y}=\mathbf X\hat{\boldsymbol\beta}$ est orthogonal à $\hat{\boldsymbol\varepsilon}$ (1.1.3), le second car la somme des résidus est nulle (présence de la constante). $\square$

Le **coefficient de détermination** est la part de variance expliquée :

$$R^2=\frac{\text{SCE}}{\text{SCT}}=1-\frac{\text{SCR}}{\text{SCT}}\in[0,1].$$

On peut montrer que $R^2$ est le **carré de la corrélation** entre $\mathbf y$ et $\hat{\mathbf y}$ : en régression simple, c'est donc le carré du coefficient de corrélation de Pearson entre $x$ et $y$ (volume I, section 3.1.7). Pour nos quatre commandes : $\text{SCT}=900+121+196+729=1946$ (les écarts de $y$ à la moyenne 52 sont $-30,-11,14,27$) et $\text{SCR}=25{,}2$, donc $R^2=1-25{,}2/1946\approx0{,}987$.

```python hide
SCT = ((y - y.mean())**2).sum()
SCR_ = (residus**2).sum()
SCE = ((ajuste - y.mean())**2).sum()
print(f"SCT = {SCT:.1f} | SCE = {SCE:.1f} | SCR = {SCR_:.1f} | SCE + SCR = {SCE + SCR_:.1f}")
print("R² = 1 - SCR/SCT        :", round(1 - SCR_ / SCT, 4))
print("R² = corr(y, ŷ)²        :", round(np.corrcoef(y, ajuste)[0, 1]**2, 4))
print("R² = corr(x, y)² (simple):", round(np.corrcoef(x, y)[0, 1]**2, 4))
```
<!--sortie-->
```text
SCT = 1946.0 | SCE = 1920.8 | SCR = 25.2 | SCE + SCR = 1946.0
R² = 1 - SCR/SCT        : 0.9871
R² = corr(y, ŷ)²        : 0.9871
R² = corr(x, y)² (simple): 0.9871
```

> ⚠️ **Les limites du $R^2$.** (1) Il **ne peut qu'augmenter** quand on ajoute une variable, même une variable sans rapport : un $R^2$ élevé peut être le signe d'un surajustement. Le **$R^2$ ajusté**, $R^2_{\text{aj}}=1-\dfrac{\text{SCR}/(n-p)}{\text{SCT}/(n-1)}$, corrige ce défaut en comparant des variances *sans biais*. (2) Un $R^2$ faible n'est pas un échec : quand le phénomène est intrinsèquement bruité (le comportement d'achat d'un individu), un $R^2$ de 15 % peut déjà être très informatif sur les **effets moyens**. (3) Un $R^2$ élevé ne prouve ni que le modèle est correct, ni que la relation est causale. Rappelez-vous le quartet d'Anscombe (volume I, section 3.1.7) : quatre jeux très différents donnent la même droite et le même $R^2$. **Dessinez toujours.**

### 1.1.7 Première étude : le panier des clients de la boutique

Passons aux données de la boutique (simulées, rappelons-le) : 2 000 clients. La gérante s'intéresse au **panier moyen** (en €) des clients qui ont commandé au moins une fois dans l'année.

```python hide
import pandas as pd
import statsmodels.formula.api as smf

clients = pd.read_csv("donnees/clients.csv")
print(clients.shape)
print(clients.head(4).to_string(index=False))
print()
print("clients sans aucune commande :", int((clients["nb_commandes_an"] == 0).sum()),
      "sur", len(clients), "(", round(100 * (clients["nb_commandes_an"] == 0).mean(), 1), "%)")
```
<!--sortie-->
```text
(2000, 12)
 id_client  age   ville canal_acquisition date_inscription  offre_bienvenue  nb_commandes_an  panier_moyen  depense_annuelle  rachat_12m  duree_mois  churn
         1   19   Autre           Réseaux       2020-03-11                0                4         40.95            116.50           0       15.89      1
         2   43 Ville E              Site       2019-01-10                1                2         78.34            148.92           1       33.68      0
         3   35 Ville A          Boutique       2020-07-02                1                6         73.73            509.05           0       23.22      0
         4   42 Ville D           Réseaux       2024-08-01                0                0          0.00              0.00           0        0.96      0

clients sans aucune commande : 260 sur 2000 ( 13.0 %)
```

Sur les 2 000 clients, 260 (13 %) n'ont passé aucune commande. Leur panier moyen est égal à 0 par convention : ce 0 ne signifie pas « panier nul » mais « pas de panier ». Nous les **écartons** de cette étude (c'est une décision de périmètre, comme celle du projet du volume I) ; la section 2.6 du chapitre suivant apprendra à traiter ensemble les clients actifs et les autres.

```python hide
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36                       # âge centré sur 36 ans (l'âge moyen de la clientèle)
df["log_panier"] = np.log(df["panier_moyen"])
print(len(df), "clients actifs")
print(df["panier_moyen"].describe().round(1).to_string())
print("asymétrie du panier :", round(df["panier_moyen"].skew(), 2), "| du log du panier :", round(df["log_panier"].skew(), 2))
```
<!--sortie-->
```text
1740 clients actifs
count    1740.0
mean       61.2
std        26.4
min        17.4
25%        42.7
50%        56.0
75%        73.4
max       245.1
asymétrie du panier : 1.44 | du log du panier : 0.11
```

Il reste 1 740 clients actifs. Le panier est nettement **asymétrique** (queue vers les gros paniers ; coefficient d'asymétrie de 1,44), alors que son logarithme est presque symétrique (0,11). Comme au volume I (section 3.1.5), c'est le signe qu'il vaut mieux travailler sur le logarithme : les effets seront alors **multiplicatifs** (un client « 10 % plus dépensier » dépense 10 % de plus, quel que soit son niveau de départ), ce qui est bien plus naturel pour des montants.

```python hide
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
ax1.hist(df["panier_moyen"], bins=40, color=BLEU, alpha=0.85)
ax1.set_xlabel("panier moyen (€)"); ax1.set_ylabel("nombre de clients"); ax1.set_title("Panier : asymétrique")
ax2.hist(df["log_panier"], bins=40, color=AQUA, alpha=0.85)
ax2.set_xlabel("log du panier moyen"); ax2.set_title("Log du panier : presque symétrique")
plt.tight_layout()
plt.savefig("figures/ch01-panier-log.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Le panier moyen est asymétrique (à gauche) ; son logarithme est presque symétrique (à droite).](figures/ch01-panier-log.png)

**Régression simple.** Commençons par une seule variable : l'âge (centré, pour que la constante ait un sens : elle sera le log-panier d'un client de 36 ans).

```python hide
m1 = smf.ols("log_panier ~ a", data=df).fit()
print(m1.summary().tables[1])
print("R² =", round(m1.rsquared, 4), "| écart-type résiduel s =", round(np.sqrt(m1.scale), 4))
```
<!--sortie-->
```text
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept      4.0331      0.009    426.820      0.000       4.015       4.052
a              0.0090      0.001     10.050      0.000       0.007       0.011
==============================================================================
R² = 0.0549 | écart-type résiduel s = 0.3941
```

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

```python hide
print(m2.summary().tables[1])
print("R² =", round(m2.rsquared, 4), "| R² ajusté =", round(m2.rsquared_adj, 4), "| s =", round(np.sqrt(m2.scale), 4))
print("Début de la matrice X (les 6 premières lignes) :")
print(m2.model.exog[:6].round(0).astype(int), "  <- colonnes :", m2.model.exog_names)
```
<!--sortie-->
```text
=======================================================================================
                          coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------
Intercept               4.2206      0.017    241.369      0.000       4.186       4.255
C(canal)[T.Site]       -0.1571      0.023     -6.807      0.000      -0.202      -0.112
C(canal)[T.Réseaux]    -0.3368      0.022    -14.977      0.000      -0.381      -0.293
a                       0.0092      0.001     10.862      0.000       0.008       0.011
=======================================================================================
R² = 0.1657 | R² ajusté = 0.1643 | s = 0.3705
Début de la matrice X (les 6 premières lignes) :
[[  1   0   1 -17]
 [  1   1   0   7]
 [  1   0   0  -1]
 [  1   0   1 -15]
 [  1   1   0  -6]
 [  1   0   1 -10]]   <- colonnes : ['Intercept', 'C(canal)[T.Site]', 'C(canal)[T.Réseaux]', 'a']
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

```python hide
res_y = smf.ols("log_panier ~ C(canal)", data=df).fit().resid        # log-panier, une fois le canal « retiré »
res_a = smf.ols("a ~ C(canal)", data=df).fit().resid                  # âge, une fois le canal « retiré »
pente_fwl = (res_a @ res_y) / (res_a @ res_a)
print("coefficient de l'âge dans le modèle complet :", round(m2.params["a"], 6))
print("pente obtenue par Frisch-Waugh-Lovell        :", round(pente_fwl, 6))
```
<!--sortie-->
```text
coefficient de l'âge dans le modèle complet : 0.00917
pente obtenue par Frisch-Waugh-Lovell        : 0.00917
```

> 📐 **Pourquoi ça marche (esquisse).** Notons $\mathbf M$ le projecteur sur l'orthogonal des colonnes « canal » (et constante). Par la géométrie du 1.1.4, le coefficient d'une variable $\mathbf a$ dans le modèle $[\text{canal},\mathbf a]$ s'obtient en projetant $\mathbf y$ sur la partie de $\mathbf a$ qui n'est pas dans l'espace engendré par le canal, soit $\mathbf M\mathbf a$ : $\hat\beta_a=(\mathbf M\mathbf a)^\top\mathbf y/\|\mathbf M\mathbf a\|^2$. Comme $\mathbf M$ est symétrique et idempotente, $(\mathbf M\mathbf a)^\top\mathbf y=(\mathbf M\mathbf a)^\top(\mathbf M\mathbf y)$ : c'est la pente de la régression de $\mathbf M\mathbf y$ sur $\mathbf M\mathbf a$.

**Calculer à la main ce que fait `statsmodels`.** Pour boucler la boucle avec les sections précédentes, reconstruisons les coefficients de `m2` par les équations normales à partir de la matrice $\mathbf X$ construite par `statsmodels` :

```python hide
Xd = m2.model.exog                      # la matrice de plan d'expérience (n x p)
yd = m2.model.endog
beta_main = np.linalg.solve(Xd.T @ Xd, Xd.T @ yd)
print(pd.DataFrame({"à la main": beta_main, "statsmodels": m2.params.to_numpy()}, index=m2.params.index).round(6))
print("n =", Xd.shape[0], "| p =", Xd.shape[1])
print("nombre de conditionnement de X'X :", round(np.linalg.cond(Xd.T @ Xd), 1))
```
<!--sortie-->
```text
                     à la main  statsmodels
Intercept             4.220621     4.220621
C(canal)[T.Site]     -0.157139    -0.157139
C(canal)[T.Réseaux]  -0.336759    -0.336759
a                     0.009170     0.009170
n = 1740 | p = 4
nombre de conditionnement de X'X : 1501.8
```

Les deux colonnes sont identiques : `statsmodels` ne fait rien de magique, il résout les équations normales (en fait, via une factorisation plus stable). Le nombre de conditionnement de $\mathbf X^\top\mathbf X$ (volume I, section 1.5.4) est de l'ordre du millier : cela paraît grand, mais c'est surtout dû au fait que l'âge centré varie de $-18$ à $+37$ alors que les indicatrices valent 0 ou 1 (échelles très différentes). Ce n'est pas de la colinéarité entre variables ; nous apprendrons à la diagnostiquer proprement (VIF) en 1.3.5.

### 1.1.8 Logarithmes : interpréter et prédire

Le choix d'une transformation modifie l'**interprétation** des coefficients. Voici les trois cas les plus courants (où $\beta$ est le coefficient de $x$) :

| Modèle | Lecture du coefficient $\beta$ |
|---|---|
| $y=\beta_0+\beta x$ (niveau-niveau) | +1 unité de $x$ ⇒ $y$ varie de $\beta$ unités |
| $\log y=\beta_0+\beta x$ (log-niveau) | +1 unité de $x$ ⇒ $y$ est multiplié par $e^\beta$, soit une variation de **≈ $100\,\beta$ %** si $\beta$ est petit (exactement $100(e^\beta-1)$ %) |
| $\log y=\beta_0+\beta\log x$ (log-log) | +1 % de $x$ ⇒ $y$ varie d'environ $\beta$ % : $\beta$ est une **élasticité** |

> ⚠️ **« ≈ 100 β % » n'est vrai que pour les petits coefficients.** Pour $\beta=-0{,}34$ (Réseaux), l'approximation donne −34 %, alors que la variation exacte est $100(e^{-0{,}34}-1)\approx-28{,}8$ %. Au-delà de $|\beta|\approx0{,}1$, utilisez toujours $e^\beta-1$.

```python hide
for nom, coef in m2.params.items():
    if nom == "Intercept":
        continue
    print(f"{nom:22s} coefficient = {coef:+.3f} | approximation 100*beta = {100*coef:+.1f} % | exact 100*(exp(beta)-1) = {100*(np.exp(coef)-1):+.1f} %")
```
<!--sortie-->
```text
C(canal)[T.Site]       coefficient = -0.157 | approximation 100*beta = -15.7 % | exact 100*(exp(beta)-1) = -14.5 %
C(canal)[T.Réseaux]    coefficient = -0.337 | approximation 100*beta = -33.7 % | exact 100*(exp(beta)-1) = -28.6 %
a                      coefficient = +0.009 | approximation 100*beta = +0.9 % | exact 100*(exp(beta)-1) = +0.9 %
```

**Prédire en échelle d'origine : le piège de la rétro-transformation.** Le modèle prédit un **log**-panier. Pour revenir en euros, on pense à prendre l'exponentielle : $\hat y=e^{\hat\mu}$. Mais $e^{\hat\mu}$ est la prédiction de la **médiane** du panier, pas de sa **moyenne**, à cause de l'asymétrie de la loi log-normale.

> 📐 **Rétro-transformation.** Si $\log y\sim\mathcal N(\mu,\sigma^2)$, alors $\mathbb E[y]=e^{\mu+\sigma^2/2}$ (c'est la fonction génératrice des moments de la loi normale : $\mathbb E[e^{Z}]=e^{\mu+\sigma^2/2}$ pour $Z\sim\mathcal N(\mu,\sigma^2)$), alors que la médiane est $e^\mu$. Pour prédire la **moyenne** d'un panier, il faut donc multiplier $e^{\hat\mu}$ par un facteur correctif $e^{s^2/2}$ (ou, sans supposer la normalité, par le facteur « de Duan » $\frac1n\sum_ie^{\hat\varepsilon_i}$).

```python hide
cible = df[(df["canal"] == "Boutique") & (df["age"].between(33, 39))]            # clients de la boutique, 33-39 ans
mu_hat = m2.predict(pd.DataFrame({"a": [0], "canal": pd.Categorical(["Boutique"], categories=["Boutique", "Site", "Réseaux"])})).iloc[0]
s2 = m2.scale
duan = np.exp(m2.resid).mean()
print("panier moyen observé (clients boutique, 33-39 ans) :", round(cible["panier_moyen"].mean(), 2), "€   (n =", len(cible), ")")
print("exp(mu chapeau)                  [médiane prédite] :", round(np.exp(mu_hat), 2), "€")
print("exp(mu chapeau + s²/2)           [moyenne, normale]:", round(np.exp(mu_hat + s2 / 2), 2), "€")
print("exp(mu chapeau) x facteur de Duan[moyenne, libre]  :", round(np.exp(mu_hat) * duan, 2), "€")
```
<!--sortie-->
```text
panier moyen observé (clients boutique, 33-39 ans) : 74.33 €   (n = 110 )
exp(mu chapeau)                  [médiane prédite] : 68.08 €
exp(mu chapeau + s²/2)           [moyenne, normale]: 72.91 €
exp(mu chapeau) x facteur de Duan[moyenne, libre]  : 72.96 €
```

La moyenne observée est nettement plus proche des prédictions **corrigées** que de $e^{\hat\mu}$ : ignorer la correction conduit à sous-estimer systématiquement le panier moyen (ici de plusieurs euros), ce qui, multiplié par des milliers de clients, devient un manque à gagner dans un budget prévisionnel.

### 1.1.9 Interactions : quand un effet dépend d'un autre

Dans `m2`, l'effet de l'âge est supposé **le même** pour les trois canaux. Mais peut-être que l'âge compte plus chez les clients Réseaux que chez ceux de la boutique ? On le teste en ajoutant une **interaction** : le produit de l'âge par les indicatrices du canal.

```python hide-code
m3 = smf.ols("log_panier ~ a * C(canal)", data=df).fit()       # a + C(canal) + a:C(canal)
print(m3.summary().tables[1])
```
<!--sortie-->
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
