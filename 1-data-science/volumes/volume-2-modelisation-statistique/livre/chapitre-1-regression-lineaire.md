# Chapitre 1 : Régression linéaire

> « Tous les modèles sont faux, mais certains sont utiles. »
> — George Box

Au volume I, vous avez appris à **décrire** des données (chapitre 3 : moyennes, corrélations) et à **comparer** des groupes (tests de Student, de Welch). Mais Yasmine pose rarement des questions aussi simples. Elle demande plutôt :

- « **Combien** dépense un client de plus de 50 ans acquis par Instagram, *par rapport à* un client de 30 ans acquis en boutique ? »
- « Quand je dis que les clients Instagram dépensent moins, est-ce vraiment le **canal**, ou est-ce parce qu'ils sont plus jeunes ? »
- « Si je ne connais que l'âge et le canal d'un nouveau client, **quel panier** puis-je prévoir ? Avec quelle marge d'erreur ? »

Pour répondre, il faut un outil qui relie **une quantité à expliquer** à **plusieurs variables explicatives en même temps**, qui mesure l'effet de chacune *toutes choses égales par ailleurs*, et qui dit honnêtement quelle confiance accorder aux chiffres. Cet outil est la **régression linéaire**, le cheval de trait de la statistique appliquée : il sert tous les jours, il est au cœur de modèles plus sophistiqués (chapitres suivants et volume III), et le comprendre à fond rend tout le reste plus facile.

## Le chemin de ce chapitre

- **1.1 Le modèle linéaire et les moindres carrés** : écrire le modèle, calculer les coefficients (à la main, puis en code), comprendre pourquoi la solution est la bonne (projection, théorème de Gauss-Markov), interpréter les coefficients, y compris avec des variables qualitatives et des transformations logarithmiques.
- **1.2 Inférence sur les coefficients** : erreurs standard, tests $t$ et $F$, intervalles de confiance et intervalles de prédiction : que peut-on conclure, et avec quelle incertitude ?
- **1.3 Diagnostics** : vérifier que le modèle n'est pas faux de façon grave : résidus, effet de levier, observations influentes, multicolinéarité.
- **1.4 Sélection de variables et comparaison de modèles** : quelles variables garder ? Surapprentissage, critères AIC/BIC, validation croisée, et les pièges de la sélection automatique.
- ➕ **Pour aller plus loin** : la **régularisation** (Ridge, Lasso, Elastic Net, 1.5), la **régression robuste** (1.6), et les **modèles à effets mixtes** pour les données groupées (1.7).
- **1.8 Exercices corrigés**.

> 💡 **Le fil conducteur : le panier des clients de Dar Jasmin.** Nous travaillons sur **2 000 clients** de Dar Jasmin, observés sur une année (âge, canal d'acquisition, ville, dépenses, etc.) et, pour certains, leur réponse à un petit questionnaire de satisfaction. Ces données sont **simulées** (graine fixe) : ainsi, nous connaissons la vérité, et nous pourrons à la fin de l'étude **vérifier** que la méthode la retrouve. C'est un luxe que la vie réelle n'offre jamais, et il rend très instructif l'examen de ce que la régression fait bien… ou moins bien.

> 📦 **Les fichiers de données.** Ce chapitre lit `donnees/clients.csv` (un client par ligne) et, à partir de 1.4, `donnees/enquete_satisfaction.csv` (réponses à huit questions de satisfaction). Au 1.7, un petit jeu supplémentaire (`donnees/ch01-relais.csv`) est simulé sous vos yeux. Le code est exécuté depuis la racine du volume, d'où les chemins `donnees/…`.

> 🛠️ **Outils.** Nous utilisons `statsmodels` (le module de référence pour les modèles statistiques en Python : tableaux de résultats, tests, diagnostics), `numpy` (pour tout recalculer à la main afin de bien comprendre), `scikit-learn` (pour la régularisation) et `matplotlib`. Quelques blocs R (`lm`, `lme4`) montrent que l'on obtient exactement les mêmes nombres dans l'autre grand langage de la statistique (section 4.2 du volume I).

> 🧭 **Notations.** Nous écrivons les vecteurs en gras minuscule ($\mathbf y$, $\boldsymbol\beta$), les matrices en gras majuscule ($\mathbf X$), $n$ pour le nombre d'observations et $p$ pour le nombre de **colonnes** de $\mathbf X$ (constante comprise). Si l'algèbre linéaire vous semble lointaine, relisez les sections 1.1.2 (matrices) et 1.1.3 (valeurs propres) du volume I ; pour la minimisation d'une fonction, le chapitre 1.3 du même volume.


## 1.1 Le modèle linéaire et les moindres carrés

> 💡 **Intuition.** Vous avez un nuage de points et vous voulez y poser **la droite qui colle le mieux**. Mais « le mieux » est vague : on peut passer par certains points et en rater d'autres. Le critère des **moindres carrés** tranche : on mesure l'écart vertical entre chaque point et la droite, on **élève chaque écart au carré** (pour que les écarts positifs et négatifs ne s'annulent pas, et pour punir plus sévèrement les gros écarts), on additionne, et on choisit la droite qui rend cette somme **la plus petite possible**. Tout ce chapitre est l'étude de cette idée, avec une ou plusieurs variables explicatives.

### 1.1.1 Un exemple minuscule, entièrement à la main

Yasmine a noté, pour quatre commandes, le **nombre d'articles** et le **montant total** en DT :

| Commande | Articles $x$ | Montant $y$ (DT) |
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

La meilleure droite est donc $\hat y=3+19{,}6\,x$ : un coût fixe de 3 DT et 19,60 DT par article. Les valeurs ajustées sont $22{,}6;\ 42{,}2;\ 61{,}8;\ 81{,}4$, et les **résidus** (écarts entre le réel et l'ajusté) valent $-0{,}6;\ -1{,}2;\ +4{,}2;\ -2{,}4$. Leur somme est nulle, et la somme de leurs carrés vaut $0{,}36+1{,}44+17{,}64+5{,}76=25{,}2$. Vérifions tout cela par le code.

```python
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

Nous avons utilisé `np.linalg.solve(XtX, Xty)` plutôt que d'inverser explicitement la matrice : résoudre un système est plus rapide et surtout **plus précis** que calculer un inverse (c'est la leçon de la section 1.5.4 du volume I sur le conditionnement). Voyons le résultat en image.

```python
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
ax.set_ylabel("montant de la commande (DT)")
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

```python
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

> 🛠️ **Une autre route vers la même solution : la descente de gradient.** Au volume I (section 1.3.3), nous avons appris à descendre une pente pas à pas. La fonction à minimiser ici est $S$, de gradient $-2\mathbf X^\top(\mathbf y-\mathbf X\boldsymbol\beta)$. Pour que la descente converge vite, on **centre** la variable $x$ (on lui soustrait sa moyenne), ce qui rend les deux directions de $\mathbf X^\top\mathbf X$ orthogonales entre elles. Vérifions que l'on retrouve $(3\,;\,19{,}6)$ (après recentrage : constante $52$ et pente $19{,}6$).

```python
xc = x - x.mean()                                  # x centré : -1,5 ; -0,5 ; 0,5 ; 1,5
Xc = np.column_stack([np.ones(4), xc])
b = np.zeros(2)
pas = 0.1                                          # taux d'apprentissage
for it in range(200):
    gradient = -2 / len(y) * Xc.T @ (y - Xc @ b)   # gradient de la moyenne des carrés
    b = b - pas * gradient
print("descente de gradient (x centré) :", b.round(4))
print("solution exacte                 :", np.linalg.solve(Xc.T @ Xc, Xc.T @ y).round(4))
print("retour à l'échelle d'origine    : constante =", round(b[0] - b[1] * x.mean(), 3), "| pente =", round(b[1], 3))
```
<!--sortie-->
```text
descente de gradient (x centré) : [52.  19.6]
solution exacte                 : [52.  19.6]
retour à l'échelle d'origine    : constante = 3.0 | pente = 19.6
```

La descente de gradient retrouve la solution exacte (à la précision près) : il s'agit bien du même problème, résolu autrement. En pratique, les logiciels n'utilisent ni l'inverse ni la descente de gradient pour la régression linéaire classique, mais une **factorisation QR** de $\mathbf X$ (ou une SVD, volume I section 1.1.4), numériquement bien plus stable. La descente de gradient reprend tout son intérêt avec les très grands jeux de données et avec les modèles qui n'ont pas de formule fermée : la régression logistique du chapitre 2, par exemple, s'ajuste par un algorithme itératif de la même famille.

### 1.1.4 La géométrie des moindres carrés : une projection

Les équations normales cachent une image géométrique très puissante. Voyons les $n$ observations $\mathbf y$ comme **un seul point** (un vecteur) de l'espace $\mathbb R^n$. Les colonnes de $\mathbf X$ engendrent un sous-espace de dimension $p$ (ici, un plan si $p=2$). Les valeurs $\mathbf X\boldsymbol\beta$ que le modèle peut produire sont exactement les points de ce sous-espace. Chercher $\boldsymbol\beta$ qui minimise $\|\mathbf y-\mathbf X\boldsymbol\beta\|$, c'est **chercher le point du sous-espace le plus proche de $\mathbf y$**, et la géométrie nous dit que c'est le **projeté orthogonal** de $\mathbf y$ sur ce sous-espace.

```python
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

Vérifions ces propriétés sur nos quatre commandes :

```python
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

**Voyons-le en simulation.** Nous connaissons la vérité dans une simulation : prenons les quatre valeurs de $x$ ci-dessus, $\boldsymbol\beta=(3,\,20)$ et $\sigma=3$, fabriquons 20 000 échantillons de quatre montants, et ajustons la droite à chacun. On comparera les moyennes et la variance **observées** des estimateurs aux formules du théorème.

```python
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

Les moyennes des $\hat\beta_j$ sont proches des vraies valeurs (absence de biais), les variances et covariances observées sont très proches de celles de $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$, et la division par $n-p$ donne une estimation centrée de $\sigma^2$ alors que la division par $n$ la sous-estime d'un facteur $(n-p)/n=1/2$. La théorie est confirmée par l'expérience.

### 1.1.6 Décomposition de la variance et coefficient de détermination $R^2$

Combien le modèle explique-t-il ? Mesurons la dispersion de $\mathbf y$ autour de sa moyenne par la **somme des carrés totale** $\text{SCT}=\sum_i(y_i-\bar y)^2$. La régression la décompose en une partie expliquée et une partie résiduelle.

> 📐 **Théorème (décomposition de la variance).** Si le modèle contient une constante, alors
> $$\underbrace{\sum_i(y_i-\bar y)^2}_{\text{SCT}}=\underbrace{\sum_i(\hat y_i-\bar y)^2}_{\text{SCE (expliquée)}}+\underbrace{\sum_i\hat\varepsilon_i^2}_{\text{SCR (résiduelle)}}.$$
> *Démonstration.* Écrivons $y_i-\bar y=(\hat y_i-\bar y)+\hat\varepsilon_i$ et élevons au carré : le double produit vaut $2\sum_i(\hat y_i-\bar y)\hat\varepsilon_i=2\sum_i\hat y_i\hat\varepsilon_i-2\bar y\sum_i\hat\varepsilon_i$. Le premier terme est nul car $\hat{\mathbf y}=\mathbf X\hat{\boldsymbol\beta}$ est orthogonal à $\hat{\boldsymbol\varepsilon}$ (1.1.3), le second car la somme des résidus est nulle (présence de la constante). $\square$

Le **coefficient de détermination** est la part de variance expliquée :

$$R^2=\frac{\text{SCE}}{\text{SCT}}=1-\frac{\text{SCR}}{\text{SCT}}\in[0,1].$$

On peut montrer que $R^2$ est le **carré de la corrélation** entre $\mathbf y$ et $\hat{\mathbf y}$ : en régression simple, c'est donc le carré du coefficient de corrélation de Pearson entre $x$ et $y$ (volume I, section 3.1.7). Pour nos quatre commandes : $\text{SCT}=900+121+196+729=1946$ (les écarts de $y$ à la moyenne 52 sont $-30,-11,14,27$) et $\text{SCR}=25{,}2$, donc $R^2=1-25{,}2/1946\approx0{,}987$.

```python
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

### 1.1.7 Première étude : le panier des clients de Dar Jasmin

Passons aux données de Dar Jasmin (simulées, rappelons-le) : 2 000 clients. Yasmine s'intéresse au **panier moyen** (en DT) des clients qui ont commandé au moins une fois dans l'année.

```python
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
         1   19   Autre         Instagram       2020-03-11                0                4         40.95            116.50           0       15.89      1
         2   43   Tunis              Site       2019-01-10                1                2         78.34            148.92           1       33.68      0
         3   35 Bizerte          Boutique       2020-07-02                1                6         73.73            509.05           0       23.22      0
         4   42  Sousse         Instagram       2024-08-01                0                0          0.00              0.00           0        0.96      0

clients sans aucune commande : 260 sur 2000 ( 13.0 %)
```

Les clients sans commande ont un panier moyen égal à 0 par convention : ce 0 ne signifie pas « panier nul » mais « pas de panier ». Nous les **écartons** de cette étude (c'est une décision de périmètre, comme celle du projet du volume I) ; la section 2.6 du chapitre suivant apprendra à traiter ensemble les clients actifs et les autres.

```python
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
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

Le panier est nettement **asymétrique** (queue vers les gros paniers), alors que son logarithme est presque symétrique. Comme au volume I (section 3.1.5), c'est le signe qu'il vaut mieux travailler sur le logarithme : les effets seront alors **multiplicatifs** (un client « 10 % plus dépensier » dépense 10 % de plus, quel que soit son niveau de départ), ce qui est bien plus naturel pour des montants.

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
ax1.hist(df["panier_moyen"], bins=40, color=BLEU, alpha=0.85)
ax1.set_xlabel("panier moyen (DT)"); ax1.set_ylabel("nombre de clients"); ax1.set_title("Panier : asymétrique")
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

```python
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

La formule `log_panier ~ a` se lit « log-panier expliqué par `a` » ; `statsmodels` ajoute la constante tout seul. Le tableau donne, pour chaque coefficient, l'estimation (`coef`), son erreur standard (`std err`), une statistique $t$, une p-valeur et un intervalle de confiance à 95 % : nous en comprendrons chaque colonne au 1.2. Retenons pour l'instant l'**interprétation** :

- La **constante** vaut environ 4,03 : un client de 36 ans a un log-panier de 4,03, soit un panier typique de $e^{4{,}03}\approx56$ DT.
- Le coefficient de **`a`** vaut environ 0,009 : chaque année d'âge supplémentaire est associée à une hausse de **0,9 %** du panier ($\log$ y augmente de 0,009, donc $y$ est multiplié par $e^{0{,}009}\approx1{,}009$).
- Le $R^2$ est faible (environ 5,5 %) : l'âge à lui seul explique peu de choses, ce qui n'a rien de surprenant.

**Variable qualitative : le codage par indicatrices.** Comment faire entrer le **canal** (Boutique/Site/Instagram), qui n'est pas un nombre ? On le remplace par des **variables indicatrices** (ou *dummies*) : une colonne par modalité *sauf une*, la **modalité de référence**, qui est absorbée par la constante. Avec Boutique pour référence :

| canal | `Site` | `Instagram` |
|---|---|---|
| Boutique | 0 | 0 |
| Site | 1 | 0 |
| Instagram | 0 | 1 |

> ⚠️ **Pourquoi pas une colonne par modalité ?** Parce que les trois colonnes s'additionnent exactement à la colonne de 1 de la constante : $\mathbf X$ ne serait plus de rang plein, et $(\mathbf X^\top\mathbf X)^{-1}$ n'existerait pas (violation de H2 : c'est le « piège de la variable indicatrice »). Retirer une colonne règle le problème.

Ajustons maintenant le modèle à l'âge **et** au canal :

```python
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
print(m2.summary().tables[1])
print("R² =", round(m2.rsquared, 4), "| R² ajusté =", round(m2.rsquared_adj, 4), "| s =", round(np.sqrt(m2.scale), 4))
print()
print("Début de la matrice X (les 6 premières lignes) :")
print(m2.model.exog[:6].round(0).astype(int), "  <- colonnes :", m2.model.exog_names)
```
<!--sortie-->
```text
=========================================================================================
                            coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                 4.2206      0.017    241.369      0.000       4.186       4.255
C(canal)[T.Site]         -0.1571      0.023     -6.807      0.000      -0.202      -0.112
C(canal)[T.Instagram]    -0.3368      0.022    -14.977      0.000      -0.381      -0.293
a                         0.0092      0.001     10.862      0.000       0.008       0.011
=========================================================================================
R² = 0.1657 | R² ajusté = 0.1643 | s = 0.3705

Début de la matrice X (les 6 premières lignes) :
[[  1   0   1 -17]
 [  1   1   0   7]
 [  1   0   0  -1]
 [  1   0   1 -15]
 [  1   1   0  -6]
 [  1   0   1 -10]]   <- colonnes : ['Intercept', 'C(canal)[T.Site]', 'C(canal)[T.Instagram]', 'a']
```

L'écriture `C(canal)` demande à `statsmodels` de traiter `canal` comme qualitative. Voici comment lire chaque ligne :

- **Constante** (≈ 4,22) : le log-panier d'un client de **36 ans acquis en boutique** (modalité de référence, âge à 0 après centrage), soit $e^{4{,}22}\approx68$ DT.
- **`C(canal)[T.Site]`** (≈ −0,16) : à âge égal, un client acquis par le site a un log-panier inférieur de 0,16 à celui d'un client de la boutique. En pourcentage : $e^{-0{,}157}\approx0{,}855$, soit un panier **environ 14,5 % plus petit**.
- **`C(canal)[T.Instagram]`** (≈ −0,34) : $e^{-0{,}34}\approx0{,}71$ : à âge égal, un panier **29 % plus petit** qu'en boutique.
- **`a`** (≈ 0,009) : à canal égal, +0,9 % de panier par année d'âge.

Et le $R^2$ a presque triplé par rapport au modèle précédent (de 5,5 % à 16,6 %). C'est la réponse à la première question de Yasmine : *à âge égal*, un client Instagram dépense environ 29 % de moins qu'un client de la boutique.

> 🧪 **Un détail d'interprétation fréquemment raté.** Les coefficients se lisent **à l'intérieur du modèle**. Le coefficient de l'âge ne dit pas « l'effet de l'âge sur le panier » dans l'absolu, mais « l'effet de l'âge **quand on compare des clients de même canal** ». C'est le sens de l'expression **« toutes choses égales par ailleurs »**. Ici, le coefficient de l'âge change à peine entre `m1` et `m2` car l'âge et le canal sont presque indépendants dans nos données ; s'ils étaient liés (par exemple si Instagram attirait surtout les jeunes), le coefficient de l'âge dans `m1` mélangerait l'effet de l'âge et l'effet du canal, et il changerait nettement. Ce mélange, c'est la **confusion**.

**Le théorème de Frisch-Waugh-Lovell : « toutes choses égales par ailleurs » rendu concret.** Il existe une manière explicite de retrouver le coefficient de l'âge dans `m2`, qui montre ce que veut dire « tenir compte du canal » :

1. régresser le log-panier sur le **canal** seul et garder les résidus (la partie du log-panier *que le canal n'explique pas*) ;
2. régresser l'âge sur le **canal** seul et garder les résidus (la partie de l'âge *indépendante du canal*) ;
3. régresser les premiers résidus sur les seconds : la pente obtenue est **exactement** le coefficient de l'âge dans le modèle complet.

```python
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

```python
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
Intercept               4.220621     4.220621
C(canal)[T.Site]       -0.157139    -0.157139
C(canal)[T.Instagram]  -0.336759    -0.336759
a                       0.009170     0.009170
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

> ⚠️ **« ≈ 100 β % » n'est vrai que pour les petits coefficients.** Pour $\beta=-0{,}34$ (Instagram), l'approximation donne −34 %, alors que la variation exacte est $100(e^{-0{,}34}-1)\approx-28{,}8$ %. Au-delà de $|\beta|\approx0{,}1$, utilisez toujours $e^\beta-1$.

```python
for nom, coef in m2.params.items():
    if nom == "Intercept":
        continue
    print(f"{nom:22s} coefficient = {coef:+.3f} | approximation 100*beta = {100*coef:+.1f} % | exact 100*(exp(beta)-1) = {100*(np.exp(coef)-1):+.1f} %")
```
<!--sortie-->
```text
C(canal)[T.Site]       coefficient = -0.157 | approximation 100*beta = -15.7 % | exact 100*(exp(beta)-1) = -14.5 %
C(canal)[T.Instagram]  coefficient = -0.337 | approximation 100*beta = -33.7 % | exact 100*(exp(beta)-1) = -28.6 %
a                      coefficient = +0.009 | approximation 100*beta = +0.9 % | exact 100*(exp(beta)-1) = +0.9 %
```

**Prédire en échelle d'origine : le piège de la rétro-transformation.** Le modèle prédit un **log**-panier. Pour revenir en dinars, on pense à prendre l'exponentielle : $\hat y=e^{\hat\mu}$. Mais $e^{\hat\mu}$ est la prédiction de la **médiane** du panier, pas de sa **moyenne**, à cause de l'asymétrie de la loi log-normale.

> 📐 **Rétro-transformation.** Si $\log y\sim\mathcal N(\mu,\sigma^2)$, alors $\mathbb E[y]=e^{\mu+\sigma^2/2}$ (c'est la fonction génératrice des moments de la loi normale : $\mathbb E[e^{Z}]=e^{\mu+\sigma^2/2}$ pour $Z\sim\mathcal N(\mu,\sigma^2)$), alors que la médiane est $e^\mu$. Pour prédire la **moyenne** d'un panier, il faut donc multiplier $e^{\hat\mu}$ par un facteur correctif $e^{s^2/2}$ (ou, sans supposer la normalité, par le facteur « de Duan » $\frac1n\sum_ie^{\hat\varepsilon_i}$).

```python
cible = df[(df["canal"] == "Boutique") & (df["age"].between(33, 39))]            # clients de la boutique, 33-39 ans
mu_hat = m2.predict(pd.DataFrame({"a": [0], "canal": pd.Categorical(["Boutique"], categories=["Boutique", "Site", "Instagram"])})).iloc[0]
s2 = m2.scale
duan = np.exp(m2.resid).mean()
print("panier moyen observé (clients boutique, 33-39 ans) :", round(cible["panier_moyen"].mean(), 2), "DT   (n =", len(cible), ")")
print("exp(mu chapeau)                  [médiane prédite] :", round(np.exp(mu_hat), 2), "DT")
print("exp(mu chapeau + s²/2)           [moyenne, normale]:", round(np.exp(mu_hat + s2 / 2), 2), "DT")
print("exp(mu chapeau) x facteur de Duan[moyenne, libre]  :", round(np.exp(mu_hat) * duan, 2), "DT")
```
<!--sortie-->
```text
panier moyen observé (clients boutique, 33-39 ans) : 74.33 DT   (n = 110 )
exp(mu chapeau)                  [médiane prédite] : 68.08 DT
exp(mu chapeau + s²/2)           [moyenne, normale]: 72.91 DT
exp(mu chapeau) x facteur de Duan[moyenne, libre]  : 72.96 DT
```

La moyenne observée est nettement plus proche des prédictions **corrigées** que de $e^{\hat\mu}$ : ignorer la correction conduit à sous-estimer systématiquement le panier moyen (ici de plusieurs dinars), ce qui, multiplié par des milliers de clients, devient un manque à gagner dans un budget prévisionnel.

### 1.1.9 Interactions : quand un effet dépend d'un autre

Dans `m2`, l'effet de l'âge est supposé **le même** pour les trois canaux. Mais peut-être que l'âge compte plus chez les clients Instagram que chez ceux de la boutique ? On le teste en ajoutant une **interaction** : le produit de l'âge par les indicatrices du canal.

```python
m3 = smf.ols("log_panier ~ a * C(canal)", data=df).fit()       # a + C(canal) + a:C(canal)
print(m3.summary().tables[1])
```
<!--sortie-->
```text
===========================================================================================
                              coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------------
Intercept                   4.2205      0.017    241.183      0.000       4.186       4.255
C(canal)[T.Site]           -0.1568      0.023     -6.788      0.000      -0.202      -0.112
C(canal)[T.Instagram]      -0.3366      0.022    -14.961      0.000      -0.381      -0.292
a                           0.0086      0.002      5.115      0.000       0.005       0.012
a:C(canal)[T.Site]          0.0010      0.002      0.463      0.643      -0.003       0.005
a:C(canal)[T.Instagram]     0.0005      0.002      0.235      0.814      -0.004       0.005
===========================================================================================
```

L'écriture `a * C(canal)` signifie `a + C(canal) + a:C(canal)`. Les deux lignes `a:C(canal)[T.…]` mesurent la **différence de pente** de l'âge entre le canal considéré et la boutique. Si ces coefficients sont proches de zéro (et statistiquement indiscernables de zéro, ce que nous formaliserons par un test $F$ au 1.2.4), le modèle sans interaction suffit. Nous verrons au 1.4 comment choisir objectivement entre `m2` et `m3`.

> ✅ **À retenir (1.1).**
> - Le modèle linéaire s'écrit $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ ; il est linéaire **dans les paramètres**. Les hypothèses H1 à H5 servent chacune à quelque chose de précis.
> - Les **équations normales** $\mathbf X^\top\mathbf X\hat{\boldsymbol\beta}=\mathbf X^\top\mathbf y$ donnent $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y$, unique grâce à la convexité ; en pratique on résout, on n'inverse pas.
> - Géométriquement, $\hat{\mathbf y}=\mathbf H\mathbf y$ est la **projection orthogonale** de $\mathbf y$ ; les résidus sont orthogonaux aux colonnes de $\mathbf X$ ; $\operatorname{tr}\mathbf H=p$.
> - Sous H1-H4 : $\hat{\boldsymbol\beta}$ est sans biais, de variance $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$, et **le meilleur estimateur linéaire sans biais** (Gauss-Markov). On estime $\sigma^2$ par $\text{SCR}/(n-p)$.
> - $R^2=1-\text{SCR}/\text{SCT}$ mesure la part de variance expliquée ; il ne peut qu'augmenter avec le nombre de variables (préférer $R^2$ ajusté pour comparer).
> - Une variable qualitative entre par des **indicatrices** (une modalité de référence) ; un coefficient se lit « toutes choses égales par ailleurs » (Frisch-Waugh-Lovell).
> - Avec $\log y$, un coefficient $\beta$ correspond à un effet multiplicatif $e^\beta$ ; pour prédire la **moyenne** en dinars, corrigez la rétro-transformation.


## 1.2 Inférence sur les coefficients

> 💡 **Intuition.** Les coefficients de `m2` (−0,34 pour Instagram, +0,009 par année d'âge…) sont calculés sur **un** échantillon de 1 740 clients. Avec un autre échantillon, on aurait obtenu d'autres valeurs. La question de l'inférence est : *de combien ces chiffres peuvent-ils bouger ?* et donc *que peut-on affirmer sur la vraie valeur ?* C'est exactement l'esprit du chapitre 3 du volume I (intervalles de confiance, tests), appliqué maintenant à chaque coefficient d'un modèle.

On part des mêmes données qu'en 1.1. Voici la préparation (identique), que nous ne détaillerons plus :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

m1 = smf.ols("log_panier ~ a", data=df).fit()
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
m3 = smf.ols("log_panier ~ a * C(canal)", data=df).fit()
print(len(df), "clients | n - p pour m2 =", int(m2.df_resid))
```
<!--sortie-->
```text
1740 clients | n - p pour m2 = 1736
```

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

Reconstruisons à la main le tableau de `statsmodels` pour `m2`, colonne par colonne :

```python
X = m2.model.exog
y = m2.model.endog
n, p = X.shape
XtX_inv = np.linalg.inv(X.T @ X)
beta = XtX_inv @ X.T @ y
residus = y - X @ beta
s2 = residus @ residus / (n - p)                       # estimation de sigma²
se = np.sqrt(s2 * np.diag(XtX_inv))                     # erreurs standard
t = beta / se                                           # statistiques t pour H0 : beta_j = 0
pval = 2 * stats.t.sf(np.abs(t), df=n - p)              # p-valeur bilatérale
crit = stats.t.ppf(0.975, df=n - p)                     # quantile de Student à 97,5 %
tab = pd.DataFrame({"coef": beta, "std err": se, "t": t, "P>|t|": pval,
                    "IC bas": beta - crit * se, "IC haut": beta + crit * se}, index=m2.params.index)
print(tab.round(4))
print()
print("identique à statsmodels :", np.allclose(tab["std err"], m2.bse), np.allclose(tab["t"], m2.tvalues),
      np.allclose(tab[["IC bas", "IC haut"]].to_numpy(), m2.conf_int().to_numpy()))
print(f"s = {np.sqrt(s2):.4f} | quantile t(n-p, 97,5 %) = {crit:.4f}  (presque 1,96 : n - p = {n - p} est grand)")
```
<!--sortie-->
```text
                         coef  std err         t  P>|t|  IC bas  IC haut
Intercept              4.2206   0.0175  241.3693    0.0  4.1863   4.2549
C(canal)[T.Site]      -0.1571   0.0231   -6.8065    0.0 -0.2024  -0.1119
C(canal)[T.Instagram] -0.3368   0.0225  -14.9770    0.0 -0.3809  -0.2927
a                      0.0092   0.0008   10.8618    0.0  0.0075   0.0108

identique à statsmodels : True True True
s = 0.3705 | quantile t(n-p, 97,5 %) = 1.9613  (presque 1,96 : n - p = 1736 est grand)
```

Chaque colonne a désormais une origine claire : l'erreur standard vient de $s\sqrt{c_{jj}}$, la statistique $t$ est le rapport coefficient / erreur standard, la p-valeur est la probabilité qu'un Student à $n-p$ degrés de liberté dépasse $|t|$ en valeur absolue, et l'intervalle de confiance est $\hat\beta_j\pm t_{n-p,\,0{,}975}\operatorname{se}(\hat\beta_j)$ (c'est la construction du volume I, section 3.3.3, appliquée à chaque coefficient).

### 1.2.2 Tester un coefficient, lire un intervalle

Le **test de Student** d'un coefficient teste $H_0:\beta_j=0$ contre $H_1:\beta_j\neq0$ : « une fois les autres variables prises en compte, cette variable apporte-t-elle une information ? ». La statistique est $t_j=\hat\beta_j/\operatorname{se}(\hat\beta_j)$, et on rejette $H_0$ au niveau 5 % si $|t_j|>t_{n-p,\,0{,}975}\approx1{,}96$.

Dans le tableau précédent, les trois coefficients du canal et de l'âge ont des $|t|$ très supérieurs à 1,96 (la plus petite valeur, pour l'âge, est de l'ordre de 11) : les p-valeurs sont minuscules : elles s'affichent `0.000` dans le tableau de `statsmodels` (ce qui signifie « inférieur à 0,0005 », et non « exactement nul »), et `0.0` dans notre tableau arrondi à quatre décimales.

> ⚠️ **Rappels du volume I, appliqués ici.** (1) Une p-valeur n'est **pas** la probabilité que $H_0$ soit vraie (3.5.2). (2) « Significatif » n'est pas « important » (3.5.3) : avec 1 740 clients, même un très petit effet serait détecté. Il faut donc toujours lire **l'estimation et son intervalle**, pas seulement le test. (3) Si l'on teste beaucoup de coefficients, il faut se méfier des faux positifs (3.5.5) : nous y reviendrons au 1.4.

L'**intervalle de confiance** est bien plus informatif que la p-valeur. Pour Instagram, l'intervalle sur le log-panier est environ $[-0{,}381\,;-0{,}293]$ ; en passant à l'exponentielle (une fonction croissante conserve les bornes), on obtient une **fourchette sur l'effet multiplicatif** :

```python
ic = m2.conf_int()
for nom in ["C(canal)[T.Site]", "C(canal)[T.Instagram]"]:
    bas, haut = ic.loc[nom]
    print(f"{nom:24s} effet sur le panier : {100*(np.exp(m2.params[nom])-1):+.1f} %   IC95 % : [{100*(np.exp(bas)-1):+.1f} % ; {100*(np.exp(haut)-1):+.1f} %]")
bas, haut = ic.loc["a"]
print(f"{'a (10 ans de plus)':24s} effet sur le panier : {100*(np.exp(10*m2.params['a'])-1):+.1f} %   IC95 % : [{100*(np.exp(10*bas)-1):+.1f} % ; {100*(np.exp(10*haut)-1):+.1f} %]")
```
<!--sortie-->
```text
C(canal)[T.Site]         effet sur le panier : -14.5 %   IC95 % : [-18.3 % ; -10.6 %]
C(canal)[T.Instagram]    effet sur le panier : -28.6 %   IC95 % : [-31.7 % ; -25.4 %]
a (10 ans de plus)       effet sur le panier : +9.6 %   IC95 % : [+7.8 % ; +11.4 %]
```

La phrase honnête à transmettre à Yasmine est donc : « *à âge égal, un client acquis par Instagram dépense environ 29 % de moins qu'un client de la boutique ; avec 95 % de confiance, la vraie différence se situe entre 25 % et 32 % de moins* ». Et pour l'âge : « *dix ans de plus sont associés à un panier de 8 à 11 % plus élevé* ».

**Un test peut aussi porter sur une combinaison de coefficients.** Par exemple : « le Site et Instagram ont-ils le même panier (à âge égal) ? ». L'hypothèse est $H_0:\beta_{\text{Site}}-\beta_{\text{Instagram}}=0$, c'est-à-dire $H_0:\mathbf c^\top\boldsymbol\beta=0$ avec $\mathbf c=(0,1,-1,0)^\top$. La variance de $\mathbf c^\top\hat{\boldsymbol\beta}$ est $\sigma^2\mathbf c^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf c$ : les covariances entre coefficients **comptent** (on ne peut pas se contenter de lire les deux erreurs standard du tableau).

```python
c = np.array([0, 1, -1, 0])
diff = c @ beta
se_diff = np.sqrt(s2 * c @ XtX_inv @ c)
print(f"beta_Site - beta_Instagram = {diff:.4f} | erreur standard = {se_diff:.4f} | t = {diff/se_diff:.2f} | p = {2*stats.t.sf(abs(diff/se_diff), n-p):.2e}")
print(m2.t_test("C(canal)[T.Site] - C(canal)[T.Instagram] = 0"))
```
<!--sortie-->
```text
beta_Site - beta_Instagram = 0.1796 | erreur standard = 0.0207 | t = 8.69 | p = 8.16e-18
                             Test for Constraints                             
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
c0             0.1796      0.021      8.691      0.000       0.139       0.220
==============================================================================
```

### 1.2.3 Le test $F$ : tester plusieurs coefficients à la fois

Comment tester que le **canal** compte, quand il se traduit par *deux* coefficients (`Site` et `Instagram`) ? Faire deux tests $t$ séparés ne répond pas à la question (et multiplie les risques de faux positif). On utilise un **test $F$ de modèles emboîtés** : on compare le modèle complet $M_1$ (avec $p_1$ paramètres) au modèle réduit $M_0$ (avec $p_0<p_1$ paramètres, obtenu en imposant $q=p_1-p_0$ contraintes, par exemple « les deux coefficients du canal sont nuls »).

> 📐 **Statistique de Fisher.** En notant $\text{SCR}_0$ et $\text{SCR}_1$ les sommes de carrés résiduelles des deux modèles (le modèle réduit ajuste toujours moins bien : $\text{SCR}_0\ge\text{SCR}_1$),
> $$F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}\ \sim\ F_{q,\;n-p_1}\quad\text{sous }H_0 .$$
> *Pourquoi cette loi ?* Notons $\mathbf H_0$ et $\mathbf H_1$ les matrices chapeau des deux modèles (l'image de $\mathbf H_0$ est contenue dans celle de $\mathbf H_1$). Sous $H_0$, la vraie moyenne $\mathbf X\boldsymbol\beta$ appartient au petit sous-espace, donc $\text{SCR}_0-\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf H_1-\mathbf H_0)\boldsymbol\varepsilon$ et $\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf I-\mathbf H_1)\boldsymbol\varepsilon$. Les matrices $\mathbf H_1-\mathbf H_0$ et $\mathbf I-\mathbf H_1$ sont des projecteurs orthogonaux entre eux, de rangs $q$ et $n-p_1$ : par le théorème de Cochran, ce sont deux variables **indépendantes** de lois $\sigma^2\chi^2_q$ et $\sigma^2\chi^2_{n-p_1}$. Leur rapport, une fois divisé par les degrés de liberté, est par définition une loi de Fisher. $\square$
>
> L'intuition est limpide : le numérateur mesure **combien l'ajustement se dégrade** (par contrainte) quand on retire les variables ; le dénominateur est l'échelle de bruit du modèle complet. Si retirer les variables ne dégrade pas plus que du bruit, $F$ est proche de 1.

```python
# Le canal compte-t-il ?  M0 : log_panier ~ a   (m1)    contre   M1 : log_panier ~ a + canal   (m2)
scr0, scr1 = m1.ssr, m2.ssr
q = int(m2.df_model - m1.df_model)
F = ((scr0 - scr1) / q) / (scr1 / m2.df_resid)
pF = stats.f.sf(F, q, m2.df_resid)
print(f"SCR0 = {scr0:.2f} | SCR1 = {scr1:.2f} | q = {q} | F = {F:.2f} | p = {pF:.2e}")
print()
print(sm.stats.anova_lm(m1, m2).round(4))
```
<!--sortie-->
```text
SCR0 = 269.94 | SCR1 = 238.30 | q = 2 | F = 115.26 | p = 9.98e-48

   df_resid       ssr  df_diff  ss_diff       F  Pr(>F)
0    1738.0  269.9406      0.0      NaN     NaN     NaN
1    1736.0  238.2975      2.0  31.6431  115.26     0.0
```

La statistique $F$ calculée à la main coïncide avec celle de `anova_lm`. Le canal est donc **très significatif** dans son ensemble.

Le même outil teste d'autres questions :

- **Le test global** du tableau de résultats (`F-statistic` dans `summary()`) compare le modèle complet au modèle réduit à la **seule constante** : « au moins une variable explicative est-elle utile ? ».
- **L'interaction âge × canal** (1.1.9) : `m3` contre `m2`, avec $q=2$ contraintes (« les deux différences de pente sont nulles »).
- **Un cas particulier** : quand $q=1$, $F=t^2$ (le test $F$ d'un seul coefficient est le carré du test $t$).

```python
print("Interaction âge x canal (m2 contre m3) :")
print(sm.stats.anova_lm(m2, m3).round(4))
print()
a_t = m2.tvalues["a"]
print("cas q = 1 : t² de l'âge =", round(a_t**2, 3), "| F de la suppression de l'âge =", round(sm.stats.anova_lm(smf.ols("log_panier ~ C(canal)", df).fit(), m2).loc[1, "F"], 3))
print()
print("test global (m2) : F =", round(m2.fvalue, 2), "| p =", f"{m2.f_pvalue:.2e}")
```
<!--sortie-->
```text
Interaction âge x canal (m2 contre m3) :
   df_resid       ssr  df_diff  ss_diff       F  Pr(>F)
0    1736.0  238.2975      0.0      NaN     NaN     NaN
1    1734.0  238.2677      2.0   0.0299  0.1087   0.897

cas q = 1 : t² de l'âge = 117.979 | F de la suppression de l'âge = 117.979

test global (m2) : F = 114.93 | p = 6.88e-68
```

Pour l'interaction, la p-valeur est grande : rien n'indique que l'effet de l'âge diffère selon le canal. Le modèle plus simple `m2` suffit.

> 🧪 **Que se passe-t-il si les erreurs ne sont pas normales ?** Pour un grand échantillon, le théorème central limite (volume I, section 2.4.3) assure que $\hat{\boldsymbol\beta}$ est approximativement normal même si les erreurs ne le sont pas, de sorte que les tests $t$ et $F$ restent *approximativement* valides (avec les lois asymptotiques). Pour un petit échantillon avec des erreurs très asymétriques, il vaut mieux recourir au **bootstrap** (voir plus bas).

### 1.2.4 Intervalle de confiance et intervalle de prédiction

Deux questions très différentes se cachent derrière « prédire » :

1. **Quel est le panier moyen** des clients Instagram de 25 ans ? Il s'agit d'estimer une **espérance** $\mathbf x_0^\top\boldsymbol\beta$ : on veut un **intervalle de confiance de la moyenne**.
2. **Quel sera le panier** d'*un* nouveau client Instagram de 25 ans ? Il s'agit de prévoir une **observation** $y_0=\mathbf x_0^\top\boldsymbol\beta+\varepsilon_0$ : on veut un **intervalle de prédiction**, plus large, car il faut ajouter le bruit individuel $\varepsilon_0$.

> 📐 **Les deux formules.** La valeur prédite est $\hat y_0=\mathbf x_0^\top\hat{\boldsymbol\beta}$, de variance $\sigma^2\,\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$. Posons $h_0=\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$ (le « levier » du point $\mathbf x_0$). Alors
> $$\text{IC de la moyenne :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{h_0},\qquad\text{intervalle de prédiction :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{1+h_0}.$$
> Dans le second cas, l'erreur de prévision est $y_0-\hat y_0=\varepsilon_0-\mathbf x_0^\top(\hat{\boldsymbol\beta}-\boldsymbol\beta)$ : somme de deux termes **indépendants** ($\varepsilon_0$ est un nouveau bruit, indépendant de l'échantillon), d'où la variance $\sigma^2(1+h_0)$.

**À la main, sur les quatre commandes du 1.1.1.** Quel montant prévoir pour une commande de **5 articles** ? On a $\hat y_0=3+19{,}6\times5=101$ DT, $s^2=\text{SCR}/(n-p)=25{,}2/2=12{,}6$, et $\mathbf x_0=(1,5)^\top$ donne $h_0=\frac1{20}(30-2\cdot10\cdot5+4\cdot25)=\frac{30}{20}=1{,}5$ (calcul avec $(\mathbf X^\top\mathbf X)^{-1}=\frac1{20}\begin{pmatrix}30&-10\\-10&4\end{pmatrix}$). Avec $n-p=2$ degrés de liberté, $t_{2,\,0{,}975}\approx4{,}303$ : IC de la moyenne $101\pm4{,}303\sqrt{12{,}6\times1{,}5}\approx101\pm18{,}7$ ; intervalle de prédiction $101\pm4{,}303\sqrt{12{,}6\times2{,}5}\approx101\pm24{,}2$. Vérifions :

```python
x4 = np.array([1, 2, 3, 4]); y4 = np.array([22, 41, 66, 79])
d4 = pd.DataFrame({"x": x4, "y": y4})
mp = smf.ols("y ~ x", d4).fit()
nouveau = pd.DataFrame({"x": [5]})
pred = mp.get_prediction(nouveau).summary_frame(alpha=0.05)
print(pred.round(2).to_string())
x0 = np.array([1, 5]); X4 = np.column_stack([np.ones(4), x4])
h0 = x0 @ np.linalg.inv(X4.T @ X4) @ x0
s2_4 = mp.scale; tq = stats.t.ppf(0.975, 2)
print("à la main : h0 =", round(h0, 3), "| IC moyenne ±", round(tq*np.sqrt(s2_4*h0), 2), "| IC prédiction ±", round(tq*np.sqrt(s2_4*(1+h0)), 2))
```
<!--sortie-->
```text
    mean  mean_se  mean_ci_lower  mean_ci_upper  obs_ci_lower  obs_ci_upper
0  101.0     4.35          82.29         119.71         76.85        125.15
à la main : h0 = 1.5 | IC moyenne ± 18.71 | IC prédiction ± 24.15
```

Ces intervalles sont énormes parce que $n=4$ et que $x_0=5$ est **hors de la plage** des données ($1$ à $4$) : $h_0=1{,}5$ est grand. C'est une propriété générale : $h_0$ **croît quand $\mathbf x_0$ s'éloigne du centre des données**, si bien que l'incertitude explose en **extrapolation**.

**Sur les clients de Dar Jasmin.** Dessinons, pour les clients acquis par Instagram, le nuage log-panier contre âge avec la droite ajustée par `m2`, la bande de confiance de la moyenne et la bande de prédiction.

```python
grille = pd.DataFrame({"age": np.arange(18, 76)})
grille["a"] = grille["age"] - 36
grille["canal"] = pd.Categorical(["Instagram"] * len(grille), categories=["Boutique", "Site", "Instagram"])
pf = m2.get_prediction(grille).summary_frame(alpha=0.05)

insta = df[df["canal"] == "Instagram"]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(insta["age"], insta["log_panier"], s=9, color=GRIS, alpha=0.55, label="clients Instagram")
ax.fill_between(grille["age"], pf["obs_ci_lower"], pf["obs_ci_upper"], color=ORANGE, alpha=0.15, label="intervalle de prédiction à 95 % (un client)")
ax.fill_between(grille["age"], pf["mean_ci_lower"], pf["mean_ci_upper"], color=BLEU, alpha=0.45, label="intervalle de confiance à 95 % (le panier moyen)")
ax.plot(grille["age"], pf["mean"], color=BLEU, lw=2)
ax.set_xlabel("âge (ans)")
ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
ax.set_ylim(2.3, 5.9)
plt.savefig("figures/ch01-bandes-prediction.png", dpi=200, bbox_inches="tight")
dans = ((insta["log_panier"] >= np.interp(insta["age"], grille["age"], pf["obs_ci_lower"])) &
        (insta["log_panier"] <= np.interp(insta["age"], grille["age"], pf["obs_ci_upper"]))).mean()
print(f"part des {len(insta)} clients Instagram situés dans l'intervalle de prédiction à 95 % : {100*dans:.1f} %")
```
<!--sortie-->
```text
part des 687 clients Instagram situés dans l'intervalle de prédiction à 95 % : 94.8 %
```

![Clients Instagram : log du panier selon l'âge. La bande bleue (intervalle de confiance de la moyenne) est étroite ; la bande orange (prédiction pour un client) est beaucoup plus large et contient environ 95 % des points.](figures/ch01-bandes-prediction.png)

Deux observations. La bande de **confiance** est étroite et se resserre autour de l'âge moyen (là où $h_0$ est minimal), tout en s'évasant aux âges extrêmes. La bande de **prédiction** est quasi parallèle à la droite et très large : elle est dominée par le terme « $1$ » (le bruit individuel), que **rien** ne peut réduire, même avec un échantillon infini. Retenons : *on peut connaître très précisément le panier moyen d'un groupe, et pourtant prévoir très mal le panier d'un individu*.

En dinars, il suffit d'appliquer l'exponentielle aux bornes (la transformation est croissante) :

```python
nouveau = pd.DataFrame({"a": [25 - 36], "canal": pd.Categorical(["Instagram"], categories=["Boutique", "Site", "Instagram"])})
r = m2.get_prediction(nouveau).summary_frame(alpha=0.05).iloc[0]
print(f"log-panier prédit : {r['mean']:.3f}")
print(f"panier médian prédit : {np.exp(r['mean']):.1f} DT | IC95 % de la médiane : [{np.exp(r['mean_ci_lower']):.1f} ; {np.exp(r['mean_ci_upper']):.1f}] DT")
print(f"un nouveau client Instagram de 25 ans : panier entre {np.exp(r['obs_ci_lower']):.1f} et {np.exp(r['obs_ci_upper']):.1f} DT avec 95 % de confiance")
```
<!--sortie-->
```text
log-panier prédit : 3.783
panier médian prédit : 43.9 DT | IC95 % de la médiane : [42.5 ; 45.4] DT
un nouveau client Instagram de 25 ans : panier entre 21.2 et 91.0 DT avec 95 % de confiance
```

Remarquez le vocabulaire : l'exponentielle des bornes de l'IC de $\mathbb E[\log y]$ donne un intervalle pour la **médiane** de $y$ (et non pour sa moyenne, cf. 1.1.8). L'intervalle de prédiction, lui, se transforme sans difficulté, car il concerne une observation.

### 1.2.5 Vérifier la théorie par simulation : la couverture des intervalles

Tout ceci repose sur H1-H5. Que vaut vraiment « 95 % de confiance » ? Vérifions-le comme on vérifie un théorème : en **répétant l'expérience** un grand nombre de fois quand on connaît la vérité. Utilisons le plan d'expérience réel $\mathbf X$ de `m2` (mêmes 1 740 clients), des coefficients vrais $\boldsymbol\beta^\star$ choisis par nous, un bruit normal d'écart-type 0,37, et générons 4 000 jeux de données. Pour chacun, nous construisons l'intervalle à 95 % du coefficient d'Instagram et vérifions s'il contient la vraie valeur.

```python
rng = np.random.default_rng(12)
beta_etoile = np.array([4.22, -0.17, -0.34, 0.009])               # nos « vrais » coefficients
sigma_v = 0.37
R = 4000
Ysim = X @ beta_etoile + rng.normal(0, sigma_v, size=(R, n))       # R jeux de données de n clients (lignes)
B = Ysim @ (XtX_inv @ X.T).T                                       # R estimations de beta (chaque ligne = un jeu)
E = Ysim - B @ X.T
S2 = (E**2).sum(axis=1) / (n - p)
SE = np.sqrt(S2[:, None] * np.diag(XtX_inv)[None, :])
Tst = (B - beta_etoile) / SE                                       # R x p statistiques t « vraies » (centrées sur la vérité)
low, high = B - crit * SE, B + crit * SE
couverture = ((low <= beta_etoile) & (beta_etoile <= high)).mean(axis=0)
print("couverture empirique de l'IC à 95 % :")
print(pd.Series(couverture, index=m2.params.index).round(3).to_string())
print("statistique t pour Instagram : moyenne =", Tst[:, 2].mean().round(3), "| écart-type =", Tst[:, 2].std().round(3),
      "| écart-type théorique de t(n-p) =", round(np.sqrt((n - p) / (n - p - 2)), 3))
print("part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge :", (np.abs(Tst[:, 3]) > 1.96).mean().round(3))
```
<!--sortie-->
```text
couverture empirique de l'IC à 95 % :
Intercept                0.944
C(canal)[T.Site]         0.951
C(canal)[T.Instagram]    0.948
a                        0.950
statistique t pour Instagram : moyenne = 0.008 | écart-type = 1.01 | écart-type théorique de t(n-p) = 1.001
part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge : 0.05
```

Les intervalles à 95 % couvrent la vraie valeur dans environ 95 % des jeux de données, pour chacun des quatre coefficients, et la statistique $t$ centrée sur la vérité se comporte comme une loi de Student (moyenne nulle, écart-type voisin de 1). Quand l'hypothèse nulle est vraie, le test $t$ à 5 % se trompe dans environ 5 % des cas : c'est exactement ce que promet la théorie. **Mais** n'oublions pas que cette simulation **respecte** H1 à H5 par construction. Dans la vraie vie, la couverture dépend de la qualité du modèle : c'est tout l'objet de la section 1.3.

### 1.2.6 Quand on ne veut pas supposer la normalité : le bootstrap des couples

Le bootstrap du volume I (section 3.3.5) s'étend à la régression : on tire au hasard, **avec remise**, des **clients entiers** (le vecteur $(y_i,\mathbf x_i)$, d'où le nom de « bootstrap des couples »), on réajuste le modèle sur chaque rééchantillon, et on observe la variabilité des coefficients. Aucune formule, aucune hypothèse de normalité.

```python
rng = np.random.default_rng(5)
B_boot = 2000
coefs = np.empty((B_boot, p))
for b in range(B_boot):
    idx = rng.integers(0, n, n)
    coefs[b] = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
ic_boot = np.percentile(coefs, [2.5, 97.5], axis=0)
comp = pd.DataFrame({"IC t (bas)": m2.conf_int()[0].to_numpy(), "IC t (haut)": m2.conf_int()[1].to_numpy(),
                     "IC bootstrap (bas)": ic_boot[0], "IC bootstrap (haut)": ic_boot[1],
                     "se (formule)": m2.bse.to_numpy(), "se (bootstrap)": coefs.std(axis=0, ddof=1)}, index=m2.params.index)
print(comp.round(4).to_string())
```
<!--sortie-->
```text
                       IC t (bas)  IC t (haut)  IC bootstrap (bas)  IC bootstrap (haut)  se (formule)  se (bootstrap)
Intercept                  4.1863       4.2549              4.1868               4.2545        0.0175          0.0172
C(canal)[T.Site]          -0.2024      -0.1119             -0.2021              -0.1131        0.0231          0.0227
C(canal)[T.Instagram]     -0.3809      -0.2927             -0.3794              -0.2931        0.0225          0.0216
a                          0.0075       0.0108              0.0075               0.0108        0.0008          0.0008
```

Les deux approches donnent des intervalles quasi identiques : ici, la formule théorique est fiable. Le bootstrap devient précieux quand les hypothèses sont douteuses (erreurs très asymétriques, petit échantillon, quantité d'intérêt compliquée comme un rapport de coefficients).

### 1.2.7 Retour aux questions de Yasmine

Nous pouvons maintenant répondre honnêtement aux trois questions de l'introduction du chapitre :

1. **« Combien dépense un client Instagram de 50 ans par rapport à un client de la boutique de 30 ans ? »** C'est une combinaison linéaire de coefficients : effet du canal (−0,34) plus 20 ans d'âge (+20 × 0,009). Son intervalle de confiance s'obtient par la formule de variance d'une combinaison (1.2.2).
2. **« Est-ce le canal ou l'âge ? »** Le test $F$ du canal est très significatif **à âge égal** (1.2.3) : ce n'est pas l'âge. Et réciproquement.
3. **« Quel panier prévoir pour un nouveau client ? »** Un intervalle de prédiction, large (1.2.4).

```python
c1 = np.array([0, 0, 1, 20.0])              # coef_Instagram + 20 * coef_age  (par rapport à la référence « Boutique, 30 ans »)
est = c1 @ beta
se_c = np.sqrt(s2 * c1 @ XtX_inv @ c1)
bas, haut = est - crit * se_c, est + crit * se_c
print(f"effet estimé : {est:+.3f} (log) -> panier {100*(np.exp(est)-1):+.1f} %   IC95 % : [{100*(np.exp(bas)-1):+.1f} % ; {100*(np.exp(haut)-1):+.1f} %]")
print(m2.t_test("C(canal)[T.Instagram] + 20*a = 0").summary_frame().round(4).to_string())
```
<!--sortie-->
```text
effet estimé : -0.153 (log) -> panier -14.2 %   IC95 % : [-18.8 % ; -9.4 %]
      coef  std err       t  P>|t|  Conf. Int. Low  Conf. Int. Upp.
c0 -0.1534    0.028 -5.4802    0.0         -0.2083          -0.0985
```

Un client Instagram de 50 ans dépense donc, en moyenne géométrique, environ **14 % de moins** qu'un client de la boutique de 30 ans : les 20 ans d'âge de plus compensent un peu plus de la moitié de l'écart de canal. Cette comparaison de deux profils précis, avec son intervalle (de −19 % à −9 %), est typiquement ce qu'une simple comparaison de moyennes de groupes ne peut pas donner.

> ✅ **À retenir (1.2).**
> - Sous H1-H5, $\hat{\boldsymbol\beta}\sim\mathcal N(\boldsymbol\beta,\sigma^2(\mathbf X^\top\mathbf X)^{-1})$, $\text{SCR}/\sigma^2\sim\chi^2_{n-p}$, et les deux sont indépendants : d'où $T_j=(\hat\beta_j-\beta_j)/\operatorname{se}(\hat\beta_j)\sim t_{n-p}$ avec $\operatorname{se}(\hat\beta_j)=s\sqrt{c_{jj}}$.
> - Le **test $t$** teste un coefficient ; le **test $F$** de modèles emboîtés, $F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}$, teste $q$ contraintes à la fois (par exemple tout un facteur qualitatif, ou une interaction). Pour $q=1$, $F=t^2$.
> - Préférez les **intervalles de confiance** aux seules p-valeurs ; en échelle logarithmique, transformez les bornes par $e^{(\cdot)}$ pour parler en pourcentage.
> - **Intervalle de confiance de la moyenne** ($\hat y_0\pm t\,s\sqrt{h_0}$) et **intervalle de prédiction** ($\hat y_0\pm t\,s\sqrt{1+h_0}$) répondent à deux questions différentes ; le second ne peut pas rétrécir en dessous du bruit individuel, et les deux **s'élargissent en extrapolation**.
> - Une simulation confirme que « 95 % » signifie bien 95 % de couverture… **quand le modèle est correct** ; le bootstrap des couples est une alternative sans hypothèse de normalité.


## 1.3 Diagnostics : le modèle est-il fiable ?

> 💡 **Intuition.** Un logiciel produit un tableau de coefficients quoi qu'on lui donne, même si le modèle est absurde. Les p-valeurs et les intervalles du 1.2 ne valent **que si les hypothèses H1 à H5 sont à peu près vraies**. Faire des diagnostics, c'est la visite médicale du modèle : on regarde ce qui reste *après* l'ajustement (les résidus), parce que les erreurs d'un modèle bien spécifié ne doivent contenir **aucune structure**. Si l'on voit une courbe, un entonnoir ou un point isolé dans les résidus, c'est que le modèle a raté quelque chose.

Voici la préparation (mêmes données qu'en 1.1 et 1.2). Nous chargeons en plus les **ventes mensuelles** de Dar Jasmin, qui nous serviront de deuxième terrain d'observation :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

m_niv = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()      # panier en DT : modèle « niveau »
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()           # log du panier : le modèle de 1.1 et 1.2

ventes = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
ventes["t"] = np.arange(len(ventes))                               # numéro du mois : 0, 1, ..., 119
print(len(df), "clients actifs |", len(ventes), "mois de ventes")
```
<!--sortie-->
```text
1740 clients actifs | 120 mois de ventes
```

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

Vérifions la formule du résidu standardisé à la main, puis avec `statsmodels`, en reprenant les quatre commandes du 1.1.1 (où les leviers valaient 0,7 ; 0,3 ; 0,3 ; 0,7) :

```python
x4 = np.array([1, 2, 3, 4]); y4 = np.array([22, 41, 66, 79])
X4 = np.column_stack([np.ones(4), x4])
H4 = X4 @ np.linalg.inv(X4.T @ X4) @ X4.T
h4 = np.diag(H4)
e4 = y4 - H4 @ y4
n4, p4 = X4.shape
s4 = np.sqrt(e4 @ e4 / (n4 - p4))
r4 = e4 / (s4 * np.sqrt(1 - h4))                                         # standardisés
infl4 = sm.OLS(y4, X4).fit().get_influence()
print("leviers h_ii             :", h4.round(2))
print("résidus bruts            :", e4.round(2))
print("standardisés (main)      :", r4.round(3), "| statsmodels :", infl4.resid_studentized_internal.round(3))
```
<!--sortie-->
```text
leviers h_ii             : [0.7 0.3 0.3 0.7]
résidus bruts            : [-0.6 -1.2  4.2 -2.4]
standardisés (main)      : [-0.309 -0.404  1.414 -1.234] | statsmodels : [-0.309 -0.404  1.414 -1.234]
```

Pour le résidu studentisé externe, on n'a pas besoin de refaire $n$ régressions : $s_{(i)}^2=\big(\text{SCR}-\hat\varepsilon_i^2/(1-h_{ii})\big)/(n-p-1)$ (résultat classique, que `statsmodels` utilise aussi). Nous le vérifierons en 1.3.4 sur un exemple plus fourni. Sur ces *quatre* points, il est d'ailleurs dégénéré pour la commande C : les trois autres points $(1,22),(2,41),(4,79)$ sont **exactement alignés** (pente 19), donc $s_{(C)}=0$ et la statistique serait infinie. C'est une bonne illustration de ce qu'un test d'aberrance demande plus de points que cela.

### 1.3.2 Les graphiques de résidus : voir avant de tester

Trois graphiques suffisent à repérer l'essentiel :

1. **Résidus contre valeurs ajustées** : doit ressembler à un **nuage sans structure** centré sur 0. Une **courbe** signale une non-linéarité (H1) ; un **entonnoir** (dispersion qui augmente), une variance non constante (H4).
2. **Diagramme quantile-quantile (Q-Q) des résidus standardisés** : les points doivent suivre la diagonale si les erreurs sont normales (H5). Une queue relevée indique une asymétrie ou des valeurs extrêmes.
3. **Échelle-position** ($\sqrt{|r_i|}$ contre valeurs ajustées) : une tendance croissante confirme une variance non constante.

Mettons en concurrence **deux modèles pour le même phénomène** : le panier en dinars (`m_niv`) et son logarithme (`m2`). Le premier est celui que l'on écrirait « naturellement » ; le second celui que nous avons choisi en 1.1.7 parce que le panier est asymétrique. Les diagnostics vont nous dire si ce choix était justifié.

```python
def diagnostics(modele, axes, titre):
    ajuste = modele.fittedvalues
    r = modele.get_influence().resid_studentized_internal
    ax1, ax2, ax3 = axes
    ax1.scatter(ajuste, r, s=7, color=BLEU, alpha=0.45)
    lis = sm.nonparametric.lowess(r, ajuste, frac=0.4)
    ax1.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2)
    ax1.axhline(0, color=GRIS, lw=1)
    ax1.set_xlabel("valeurs ajustées"); ax1.set_ylabel("résidu standardisé"); ax1.set_title(titre + " : résidus / ajustées", fontsize=10)
    th, emp = stats.probplot(r, dist="norm")[0]               # quantiles théoriques, quantiles observés
    ax2.scatter(th, emp, s=7, color=BLEU, alpha=0.45)
    lim = [min(th.min(), emp.min()), max(th.max(), emp.max())]
    ax2.plot(lim, lim, color=ORANGE, lw=2)
    ax2.set_xlabel("quantiles théoriques (loi normale)"); ax2.set_ylabel("quantiles observés"); ax2.set_title(titre + " : Q-Q", fontsize=10)
    ax3.scatter(ajuste, np.sqrt(np.abs(r)), s=7, color=BLEU, alpha=0.45)
    lis = sm.nonparametric.lowess(np.sqrt(np.abs(r)), ajuste, frac=0.4)
    ax3.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2)
    ax3.set_xlabel("valeurs ajustées"); ax3.set_ylabel("racine de |résidu standardisé|"); ax3.set_title(titre + " : échelle-position", fontsize=10)

fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.2))
diagnostics(m_niv, axes[0], "panier en DT")
diagnostics(m2, axes[1], "log du panier")
plt.tight_layout()
plt.savefig("figures/ch01-diagnostics-niveau-log.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Diagnostics comparés. Ligne du haut : modèle sur le panier en DT (résidus asymétriques, dispersion croissante, queue lourde à droite). Ligne du bas : modèle sur le log du panier (nuage homogène, points alignés sur la diagonale). La courbe orange est un lissage local.](figures/ch01-diagnostics-niveau-log.png)

La différence est nette. Pour le panier en dinars (ligne du haut), les résidus sont très **asymétriques** : une nuée de points très hauts (jusqu'à 7 écarts-types), mais aucun point aussi bas, et le diagramme Q-Q montre une **queue droite très relevée** et une queue gauche trop courte. La dispersion augmente aussi avec la valeur ajustée : le lissage de l'échelle-position monte de 0,6 à 0,85 environ (l'entonnoir est modeste à l'œil, mais le test de Breusch-Pagan, ci-dessous, ne s'y trompe pas). Pour le log du panier (ligne du bas), le nuage est homogène, le lissage orange reste plat, et les points suivent la diagonale. La transformation logarithmique n'était donc pas un détail esthétique : elle rend le modèle **valide**.

> 💡 **Pourquoi le log résout le problème.** Quand les effets sont **multiplicatifs** ($y=\mu\cdot\eta$ avec $\eta$ un facteur aléatoire autour de 1), l'écart-type de $y$ est proportionnel à sa moyenne $\mu$ : les gros paniers fluctuent plus que les petits, exactement l'entonnoir observé. En passant au logarithme, $\log y=\log\mu+\log\eta$ : le bruit devient **additif** et de variance constante.

### 1.3.3 Les tests de diagnostic (et pourquoi ils ne remplacent pas les graphiques)

Des tests formalisent ce que l'œil voit.

**Variance non constante : le test de Breusch-Pagan.** Idée : si la variance dépend des variables explicatives, alors les carrés des résidus $\hat\varepsilon_i^2$ (estimations grossières de la variance) doivent être **prévisibles** à partir de $\mathbf X$. On régresse donc $\hat\varepsilon_i^2$ sur les mêmes variables ; si cette régression a un $R^2$ non négligeable, on rejette l'homoscédasticité. La statistique est $\text{LM}=n\,R^2_{\text{aux}}\sim\chi^2_{p-1}$ sous $H_0$ (variance constante). Calculons-la à la main pour les deux modèles et comparons à `statsmodels` :

```python
def breusch_pagan_main(modele):
    e2 = modele.resid.to_numpy() ** 2
    Xm = modele.model.exog
    aux = sm.OLS(e2, Xm).fit()                       # régression des carrés des résidus sur X
    LM = len(e2) * aux.rsquared
    return LM, stats.chi2.sf(LM, Xm.shape[1] - 1)

for nom, m in [("panier en DT", m_niv), ("log du panier", m2)]:
    LM, p = breusch_pagan_main(m)
    LM_sm, p_sm = sm.stats.diagnostic.het_breuschpagan(m.resid, m.model.exog)[:2]
    print(f"{nom:14s} LM (main) = {LM:6.2f}  p = {p:.2e} | statsmodels : LM = {LM_sm:6.2f}  p = {p_sm:.2e}")
```
<!--sortie-->
```text
panier en DT   LM (main) =  35.90  p = 7.86e-08 | statsmodels : LM =  35.90  p = 7.86e-08
log du panier  LM (main) =   1.92  p = 5.90e-01 | statsmodels : LM =   1.92  p = 5.90e-01
```

**Normalité des erreurs.** Le test de Shapiro-Wilk et celui de Jarque-Bera (fondé sur l'asymétrie et l'aplatissement, volume I, section 3.7.5) comparent les résidus à une loi normale. Avec un grand $n$, ils détectent des écarts minuscules sans importance pratique : le diagramme Q-Q reste l'outil principal.

```python
for nom, m in [("panier en DT", m_niv), ("log du panier", m2)]:
    r = m.resid
    jb, pjb, sk, ku = sm.stats.jarque_bera(r)
    print(f"{nom:14s} asymétrie = {sk:5.2f} | aplatissement (excès) = {ku-3:5.2f} | Shapiro p = {stats.shapiro(r).pvalue:.2e} | Jarque-Bera p = {pjb:.2e}")
```
<!--sortie-->
```text
panier en DT   asymétrie =  1.40 | aplatissement (excès) =  3.84 | Shapiro p = 1.25e-29 | Jarque-Bera p = 0.00e+00
log du panier  asymétrie =  0.11 | aplatissement (excès) = -0.06 | Shapiro p = 2.34e-01 | Jarque-Bera p = 1.63e-01
```

**Autocorrélation des erreurs (H4 : erreurs non corrélées).** Quand les observations sont ordonnées dans le temps, les erreurs successives peuvent se ressembler. Le test de **Durbin-Watson** mesure cela : $\text{DW}=\dfrac{\sum_{i\ge2}(\hat\varepsilon_i-\hat\varepsilon_{i-1})^2}{\sum_i\hat\varepsilon_i^2}\approx2(1-\hat\rho)$, où $\hat\rho$ est l'autocorrélation d'ordre 1 des résidus. Une valeur proche de 2 indique l'absence d'autocorrélation ; **inférieure à 2**, une autocorrélation positive. Les clients n'ont pas d'ordre naturel, donc ce test n'a pas de sens pour eux : utilisons plutôt les ventes mensuelles, avec le modèle d'une **tendance simple** $\text{ventes}_t=\beta_0+\beta_1 t+\varepsilon_t$, en niveau puis en logarithme.

```python
mv_niv = smf.ols("ca ~ t", data=ventes).fit()
mv_log = smf.ols("np.log(ca) ~ t", data=ventes).fit()
for nom, m in [("ca ~ t", mv_niv), ("log(ca) ~ t", mv_log)]:
    dw = sm.stats.durbin_watson(m.resid)
    print(f"{nom:12s} R² = {m.rsquared:.3f} | Durbin-Watson = {dw:.2f} (rho ≈ {1 - dw/2:.2f}) | Breusch-Pagan p = {sm.stats.diagnostic.het_breuschpagan(m.resid, m.model.exog)[1]:.3f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
ax1.plot(ventes["mois"], mv_log.resid, color=BLEU, lw=1.2)
ax1.axhline(0, color=GRIS, lw=1)
ax1.set_ylabel("résidu de log(ca) ~ t"); ax1.set_title("Résidus dans le temps : une saisonnalité subsiste", fontsize=10)
pd.plotting.autocorrelation_plot(pd.Series(mv_log.resid.to_numpy()), ax=ax2, color=BLEU)
ax2.set_xlim(0, 36); ax2.set_title("Autocorrélation des résidus (décalages en mois)", fontsize=10)
plt.tight_layout()
plt.savefig("figures/ch01-residus-ventes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
ca ~ t       R² = 0.464 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.004
log(ca) ~ t  R² = 0.493 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.889
figure enregistrée
```

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

```python
xs = np.array([1, 2, 3, 4, 5, 12.0])
ys = np.array([2.1, 3.9, 6.2, 7.8, 10.1, 14.0])          # le dernier point devrait être vers 24 si la tendance se poursuivait
Xs = np.column_stack([np.ones(6), xs])
ms = sm.OLS(ys, Xs).fit()
m5 = sm.OLS(ys[:5], Xs[:5]).fit()                         # sans le sixième point
infl = ms.get_influence()
print("pente avec les 6 points :", round(ms.params[1], 3), "| sans le sixième point :", round(m5.params[1], 3))
print("leviers h_ii :", infl.hat_matrix_diag.round(3), "(moyenne p/n =", round(2/6, 3), ")")
print("résidus bruts :", ms.resid.round(2))
print("résidus standardisés :", infl.resid_studentized_internal.round(2))
print("distances de Cook :", infl.cooks_distance[0].round(2))
print("prévision en x = 12 sans le sixième point :", round(m5.params[0] + m5.params[1] * 12, 1), "| observé :", ys[5])
# vérification de la formule de Cook par réajustement sans l'observation i
# résidu studentisé externe : formule sans réajustement, comparée à statsmodels
h6, e6 = infl.hat_matrix_diag, ms.resid
s_sans = np.sqrt((e6 @ e6 - e6**2 / (1 - h6)) / (6 - 2 - 1))
print("studentisés externes (main)  :", (e6 / (s_sans * np.sqrt(1 - h6))).round(2))
print("studentisés externes (statsm.):", infl.resid_studentized_external.round(2))
cook_main = []
for i in range(6):
    mi = sm.OLS(np.delete(ys, i), np.delete(Xs, i, axis=0)).fit()
    d = ms.params - mi.params
    cook_main.append(d @ Xs.T @ Xs @ d / (2 * ms.scale))
print("Cook par réajustement :", np.round(cook_main, 2))

fig, ax = plt.subplots(figsize=(6.6, 4.2))
xx = np.linspace(0, 13, 50)
ax.plot(xx, ms.params[0] + ms.params[1] * xx, color=ORANGE, lw=2, label="droite avec les 6 points")
ax.plot(xx, m5.params[0] + m5.params[1] * xx, color=BLEU, lw=2, label="droite sans le sixième point")
ax.scatter(xs[:5], ys[:5], color=ENCRE, s=36, zorder=3)
ax.scatter(xs[5:], ys[5:], color=ROUGE, s=60, zorder=3)
ax.annotate("point à fort levier", (12, 14.0), textcoords="offset points", xytext=(-95, -35), color=ROUGE,
            arrowprops=dict(arrowstyle="->", color=ROUGE))
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(frameon=False, loc="upper left")
ax.set_xlim(0, 13); ax.set_ylim(0, 27)
plt.savefig("figures/ch01-levier.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
pente avec les 6 points : 1.029 | sans le sixième point : 1.99
leviers h_ii : [0.325 0.247 0.196 0.17  0.17  0.892] (moyenne p/n = 0.333 )
résidus bruts : [-1.65 -0.88  0.39  0.96  2.24 -1.07]
résidus standardisés : [-1.23 -0.62  0.27  0.65  1.5  -1.99]
distances de Cook : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
prévision en x = 12 sans le sixième point : 23.9 | observé : 14.0
studentisés externes (main)  : [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
studentisés externes (statsm.): [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
Cook par réajustement : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
figure enregistrée
```

![Un point à fort levier (rouge, x = 12) tire la droite orange vers lui. Sans ce point, la droite bleue suit le reste du nuage, et prévoit environ 24 en x = 12.](figures/ch01-levier.png)

Remarquez la leçon, qui surprend toujours : **le point influent a un résidu petit**. Comme la droite est tirée vers lui, son résidu brut est modeste (voyez la ligne des résidus), alors qu'il est très loin de ce que la tendance des cinq autres points prévoyait. C'est son **levier** (proche de 0,9, très au-dessus de la moyenne $p/n\approx0{,}33$) et sa **distance de Cook** qui le trahissent. Un diagnostic fondé sur les seuls résidus l'aurait laissé passer. Et la formule de Cook, retrouvée ici par réajustement sans chaque point, confirme le raccourci.

**Sur les clients de Dar Jasmin.** Appliquons ces outils au modèle `m2`. Avec 1 740 clients, un seul client ne pèse presque rien :

```python
infl = m2.get_influence()
h = infl.hat_matrix_diag
cook = infl.cooks_distance[0]
n, p = m2.model.exog.shape
print(f"n = {n}, p = {p} | levier moyen p/n = {p/n:.4f} | levier maximal = {h.max():.4f} | seuil 2p/n = {2*p/n:.4f}")
print(f"distance de Cook maximale = {cook.max():.4f} | seuil usuel 4/n = {4/n:.4f} | seuil d'alerte forte : 1")
print(f"nombre de clients au-dessus de 4/n : {(cook > 4/n).sum()} sur {n} ({100*(cook > 4/n).mean():.1f} %)")
print()
top = pd.DataFrame({"age": df["age"].to_numpy(), "canal": df["canal"].to_numpy(), "panier": df["panier_moyen"].to_numpy(),
                    "résidu stud. ext.": infl.resid_studentized_external, "levier": h, "Cook": cook}).sort_values("Cook", ascending=False).head(5)
print(top.round(4).to_string())
print()
print(m2.outlier_test().sort_values("unadj_p").head(3).round(4))
```
<!--sortie-->
```text
n = 1740, p = 4 | levier moyen p/n = 0.0023 | levier maximal = 0.0089 | seuil 2p/n = 0.0046
distance de Cook maximale = 0.0067 | seuil usuel 4/n = 0.0023 | seuil d'alerte forte : 1
nombre de clients au-dessus de 4/n : 84 sur 1740 (4.8 %)

      age      canal  panier  résidu stud. ext.  levier    Cook
864    43       Site  245.06             3.7254  0.0019  0.0067
747    48   Boutique   25.53            -2.9552  0.0030  0.0066
1060   66  Instagram  131.04             1.9415  0.0061  0.0058
140    50       Site  189.89             2.8562  0.0027  0.0055
439    22  Instagram  124.39             2.8921  0.0025  0.0052

      student_resid  unadj_p  bonf(p)
1001         3.7254   0.0002   0.3502
180          3.3254   0.0009   1.0000
1741         3.2648   0.0011   1.0000
```

Aucun client n'a un levier ou une distance de Cook préoccupants : le plus grand levier (0,0089) est certes environ quatre fois le levier moyen (0,0023), mais il reste inférieur à 1 % (aucun client ne pèse même 1 % dans sa propre prédiction), et la distance de Cook maximale (0,0067) est plus de cent fois sous le seuil d'alerte de 1. Deux remarques de méthode :

- Le seuil « $D_i>4/n$ » est une **règle de dépistage**, pas un test : avec $n$ grand elle signale toujours quelques points (ici environ 5 % des clients), simplement parce que certains points sont toujours un peu plus éloignés que d'autres. Ce qui compte est qu'**aucun** ne soit isolé du lot. Regardez les valeurs, pas seulement le seuil.
- Le test des résidus studentisés externes, ajusté pour le nombre de tests (correction de **Bonferroni**, volume I, section 3.5.5), est un vrai test de « valeur aberrante » : la plus grande valeur absolue (environ 3,73) a une p-valeur brute de 0,0002, mais parmi 1 740 observations on s'attend à de telles valeurs : une fois la correction de Bonferroni appliquée, la p-valeur ajustée est de 0,35, rien de significatif.

> 🛠️ **Que faire d'une observation influente ?** Ne la supprimez **pas** automatiquement. (1) Vérifiez qu'il ne s'agit pas d'une **erreur de saisie** (un panier de 5 000 DT au lieu de 50). (2) Si elle est authentique, regardez comment les conclusions changent **avec et sans** elle, et rapportez les deux. (3) Si elle représente un phénomène réel mais rare, envisagez une méthode **robuste** (section 1.6). Retirer un point « parce qu'il gêne » est l'une des formes les plus courantes de falsification involontaire.

### 1.3.5 La multicolinéarité : quand deux variables disent la même chose

Si deux variables explicatives sont presque redondantes, le modèle ne peut pas **départager** leurs effets. Les prédictions restent bonnes, mais les coefficients individuels deviennent **instables** et leurs erreurs standard explosent.

> 📐 **Pourquoi les erreurs standard explosent.** Par le théorème de Frisch-Waugh-Lovell (1.1.7), le coefficient de la variable $\mathbf x_j$ est la pente de la régression sur la partie de $\mathbf x_j$ qui n'est pas expliquée par les autres variables, soit $\tilde{\mathbf x}_j=\mathbf M_{-j}\mathbf x_j$ (les résidus de la régression de $\mathbf x_j$ sur les autres colonnes). Donc
> $$\operatorname{Var}(\hat\beta_j)=\frac{\sigma^2}{\|\tilde{\mathbf x}_j\|^2}=\frac{\sigma^2}{\text{SCT}_j\,(1-R_j^2)},$$
> où $\text{SCT}_j=\sum_i(x_{ij}-\bar x_j)^2$ et $R_j^2$ est le $R^2$ de la régression de $\mathbf x_j$ sur les autres variables explicatives. Quand $R_j^2\to1$ (colinéarité), la partie « propre » de $\mathbf x_j$ disparaît et la variance explose. Le **facteur d'inflation de la variance** est
> $$\text{VIF}_j=\frac{1}{1-R_j^2}.$$
> Règles empiriques : $\text{VIF}>5$ : à surveiller ; $\text{VIF}>10$ : problématique.

**Provoquons le problème.** Ajoutons au modèle `m2` l'âge **exprimé en mois**, mesuré avec un petit bruit (le client indique son âge « à peu près » ; l'âge en mois est quasiment $12\times$ l'âge en années) :

```python
rng = np.random.default_rng(3)
df["age_mois"] = 12 * df["age"] + rng.normal(0, 3, len(df))         # presque redondant avec l'âge en années
print("corrélation âge (années) / âge (mois) :", round(np.corrcoef(df["age"], df["age_mois"])[0, 1], 4))

mc = smf.ols("log_panier ~ a + C(canal) + age_mois", data=df).fit()
print(pd.DataFrame({"m2 : coef": m2.params, "m2 : se": m2.bse, "avec age_mois : coef": mc.params, "avec age_mois : se": mc.bse}).round(4).to_string())
Xc = mc.model.exog
vif = pd.Series([variance_inflation_factor(Xc, i) for i in range(Xc.shape[1])], index=mc.params.index)
print()
print("VIF :", vif.round(1).to_dict())
print("R² de m2 :", round(m2.rsquared, 4), "| R² avec age_mois :", round(mc.rsquared, 4), " (prédictions aussi bonnes)")
```
<!--sortie-->
```text
corrélation âge (années) / âge (mois) : 0.9997
                       m2 : coef  m2 : se  avec age_mois : coef  avec age_mois : se
C(canal)[T.Instagram]    -0.3368   0.0225               -0.3377              0.0225
C(canal)[T.Site]         -0.1571   0.0231               -0.1580              0.0231
Intercept                 4.2206   0.0175                3.2552              1.2998
a                         0.0092   0.0008               -0.0176              0.0361
age_mois                     NaN      NaN                0.0022              0.0030

VIF : {'Intercept': 1.0, 'C(canal)[T.Site]': 1.5, 'C(canal)[T.Instagram]': 1.5, 'a': 1828.5, 'age_mois': 1828.6}
R² de m2 : 0.1657 | R² avec age_mois : 0.166  (prédictions aussi bonnes)
```

Les prédictions sont aussi bonnes (le $R^2$ ne bouge pas), mais regardez les coefficients de l'âge : l'erreur standard de `a` est multipliée par plus de quarante, et le coefficient lui-même est devenu **négatif** et non significatif : pourtant, nous savons que l'effet de l'âge est positif. Les deux variables se « disputent » le même effet. Les VIF, de l'ordre de 1 800, le disent sans ambiguïté, alors que ceux des variables de canal restent bas (1,5). Les coefficients du **canal** sont, eux, intacts, car ils ne sont pas corrélés avec ce couple : la multicolinéarité n'abîme que les coefficients des variables concernées.

**Une colinéarité plus sournoise : les termes polynomiaux non centrés.** Si l'on ajoute le carré de l'âge pour tester une courbure, $\text{âge}$ et $\text{âge}^2$ sont très corrélés (les deux croissent ensemble). Le **centrage** règle le problème :

```python
df["age2_brut"] = df["age"] ** 2
df["a2"] = df["a"] ** 2
mq_brut = smf.ols("log_panier ~ age + age2_brut + C(canal)", data=df).fit()
mq_centre = smf.ols("log_panier ~ a + a2 + C(canal)", data=df).fit()
for nom, m in [("non centré (âge, âge²)", mq_brut), ("centré (a, a²)", mq_centre)]:
    Xq = m.model.exog
    v = [round(float(variance_inflation_factor(Xq, i)), 1) for i in range(Xq.shape[1])]
    print(f"{nom:24s} VIF = {v} | p-valeur du terme quadratique = {m.pvalues.iloc[-1]:.3f}")
```
<!--sortie-->
```text
non centré (âge, âge²)   VIF = [1.0, 1.5, 1.5, 33.9, 33.9] | p-valeur du terme quadratique = 0.580
centré (a, a²)           VIF = [1.0, 1.5, 1.5, 1.0, 1.0] | p-valeur du terme quadratique = 0.580
```

Le terme quadratique n'est pas significatif dans les deux cas (la p-valeur du terme du second degré est identique avec ou sans centrage, comme il se doit : on décrit le *même* modèle), mais les VIF passent de plus de 30 à 1 après centrage, ce qui rend les coefficients lisibles. L'âge n'a pas de courbure détectable : la relation avec le log-panier est bien linéaire (H1 est plausible).

> 🛠️ **Que faire en cas de multicolinéarité ?** (1) **Retirer** une des variables redondantes, ou les **combiner** en une seule (moyenne, indice). (2) **Centrer** les variables avant de créer des puissances ou des interactions. (3) Si l'on tient à garder toutes les variables et que l'objectif est la **prédiction**, la **régularisation** (Ridge, section 1.5) stabilise les coefficients. (4) Si l'objectif est d'**interpréter** un effet précis, il faut accepter qu'on ne peut pas séparer l'effet de deux variables quasi identiques : il est plus honnête de le dire.

### 1.3.6 Variance non constante : que faire ?

Pour `m_niv`, nous avons vu que le défaut est net. Trois remèdes :

1. **Transformer la réponse** (le logarithme, ici : c'est la solution privilégiée, car elle rend le modèle plus naturel).
2. **Changer de famille de lois** (modèles linéaires généralisés, chapitre 2 : par exemple une régression Gamma, qui suppose précisément que l'écart-type est proportionnel à la moyenne).
3. **Garder le modèle en niveau et corriger les erreurs standard** par la méthode « robuste à l'hétéroscédasticité ». C'est utile quand on tient à l'échelle d'origine.

> 📐 **Erreurs standard de White (« sandwich »).** Si $\operatorname{Var}(\boldsymbol\varepsilon)=\boldsymbol\Omega$ est diagonale mais avec des $\sigma_i^2$ différents, alors $\hat{\boldsymbol\beta}$ reste sans biais, mais sa variance devient
> $$\operatorname{Var}(\hat{\boldsymbol\beta})=(\mathbf X^\top\mathbf X)^{-1}\Big(\sum_i\sigma_i^2\,\mathbf x_i\mathbf x_i^\top\Big)(\mathbf X^\top\mathbf X)^{-1}$$
> (le « sandwich » : deux tranches de pain $(\mathbf X^\top\mathbf X)^{-1}$ autour de la garniture). On remplace $\sigma_i^2$ par un estimateur : $\hat\varepsilon_i^2$ (version **HC0**), ou, plus prudent pour les échantillons de taille modérée, $\hat\varepsilon_i^2/(1-h_{ii})^2$ (version **HC3**). La formule classique $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ n'en est qu'un cas particulier (variances égales).

Comparons, pour `m_niv`, les erreurs standard classiques, robustes (HC3), et celles d'un bootstrap des couples (qui ne fait aucune hypothèse sur la variance) :

```python
m_hc3 = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit(cov_type="HC3")
Xn, yn = m_niv.model.exog, m_niv.model.endog
rng = np.random.default_rng(8)
cb = np.array([np.linalg.lstsq(Xn[idx], yn[idx], rcond=None)[0] for idx in (rng.integers(0, len(yn), len(yn)) for _ in range(2000))])
print(pd.DataFrame({"se classique": m_niv.bse, "se robuste (HC3)": m_hc3.bse, "se bootstrap": cb.std(axis=0, ddof=1)}).round(3).to_string())
```
<!--sortie-->
```text
                       se classique  se robuste (HC3)  se bootstrap
Intercept                     1.149             1.306         1.274
C(canal)[T.Site]              1.518             1.688         1.659
C(canal)[T.Instagram]         1.478             1.511         1.522
a                             0.055             0.055         0.055
```

Les erreurs standard robustes sont plus proches du bootstrap que les erreurs classiques pour la constante, le coefficient du Site et celui d'Instagram : la formule classique **sous-estimait** l'incertitude de ces coefficients (de 12 % environ pour la constante et le Site). Pour le coefficient de l'âge, tout concorde. L'écart n'est pas énorme, mais il va dans le sens qu'annonce la théorie. Dans les modèles où l'hétéroscédasticité est plus forte, il peut être considérable.

### 1.3.7 Courbure et variables manquantes : lire les graphiques de résidus partiels

Pour déceler une relation **non linéaire** avec une variable précise $x_j$, on trace les **résidus partiels** : $\hat\varepsilon_i+\hat\beta_jx_{ij}$ contre $x_{ij}$. Si la relation est linéaire, le nuage suit la droite de pente $\hat\beta_j$ ; une courbure systématique suggère d'ajouter un terme (carré, logarithme, ou une transformation plus flexible, cf. les GAM de la section 2.5).

```python
fig, ax = plt.subplots(figsize=(6.6, 4.0))
partiel = m2.resid + m2.params["a"] * df["a"]
ax.scatter(df["age"], partiel, s=7, color=GRIS, alpha=0.45)
lis = sm.nonparametric.lowess(partiel, df["age"], frac=0.5)
ax.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2.2, label="lissage local")
xa = np.linspace(18, 75, 50)
ax.plot(xa, m2.params["a"] * (xa - 36), color=BLEU, lw=2, ls="--", label="droite du modèle")
ax.set_xlabel("âge (ans)"); ax.set_ylabel("résidu partiel (effet de l'âge)")
ax.legend(frameon=False, loc="upper left")
plt.savefig("figures/ch01-residus-partiels.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Résidus partiels pour l'âge : le lissage local (orange) suit la droite du modèle (bleu pointillé) : pas de courbure détectable.](figures/ch01-residus-partiels.png)

Le lissage orange épouse la droite bleue : la linéarité en l'âge est acceptable (ce que le test du terme quadratique, plus haut, confirmait). Notez que le lissage s'écarte un peu aux âges extrêmes, où il y a peu de clients : c'est du bruit d'échantillonnage, pas de la structure.

**Verdict sur `m2`.** Le modèle `log_panier ~ a + C(canal)` passe les contrôles : linéarité plausible, variance constante (Breusch-Pagan non significatif), résidus proches de la normale, aucune observation influente, pas de colinéarité entre ses variables. Les intervalles du 1.2 sont donc fiables. Ce n'est **pas** une preuve que le modèle est « vrai » (des variables importantes peuvent manquer), seulement que ses hypothèses ne sont pas manifestement violées.

> ✅ **À retenir (1.3).**
> - Les résidus d'un bon modèle ne contiennent **aucune structure**. Regardez : résidus contre ajustées (courbure, entonnoir), Q-Q (normalité), échelle-position (variance).
> - $\operatorname{Var}(\hat\varepsilon_i)=\sigma^2(1-h_{ii})$ : on **standardise** (ou studentise) les résidus avant de les comparer. Un point à fort levier a un résidu brut **petit** : ne vous fiez pas aux seuls résidus.
> - **Levier** $h_{ii}$ (valeurs inhabituelles de $\mathbf x$), **résidu** (écart à la prédiction) et **influence** (changement des résultats si on retire le point, **distance de Cook**) sont trois notions distinctes. Ne supprimez jamais un point sans enquêter.
> - **VIF** $=1/(1-R_j^2)$ mesure l'inflation de variance due à la colinéarité ; **centrer** avant de créer des puissances.
> - Si la variance n'est pas constante : transformer (log), changer de famille (GLM), ou corriger les erreurs standard (**sandwich**, HC3). Si les erreurs sont **autocorrélées** (séries temporelles) : chapitre 4.
> - Un test (Breusch-Pagan, Shapiro, Durbin-Watson) **complète** un graphique, il ne le remplace pas.


## 1.4 Sélection de variables et comparaison de modèles

> 💡 **Intuition.** Face à dix variables possibles, laquelle garder ? Tout garder semble prudent, mais chaque variable inutile ajoute du **bruit** à l'estimation (les erreurs standard grossissent) et peut conduire à des prédictions pires que celles d'un modèle plus simple. À l'inverse, oublier une variable utile introduit un **biais**. Choisir un modèle, c'est trouver le bon compromis entre **trop simple** (qui rate des effets réels) et **trop complexe** (qui s'ajuste au hasard de l'échantillon, c'est le *surajustement*). Il existe pour cela des outils objectifs : des critères d'information (AIC, BIC), la validation croisée, des tests emboîtés.

Nous gardons la même préparation. Pour avoir plus de variables à départager, nous ajoutons les **notes de l'enquête de satisfaction** (volume II, `donnees/enquete_satisfaction.csv`) : 60 % des clients y ont répondu (au hasard), avec huit questions notées de 1 à 5. Les questions q1 à q4 portent sur les **produits**, q5 à q8 sur le **service et la livraison** ; nous en tirons deux scores moyens.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.model_selection import KFold
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client")   # clients actifs ayant répondu
print(len(enq), "répondants à l'enquête |", len(df), "clients actifs |", len(bq), "clients actifs répondants")
print(bq[["score_produit", "score_service", "a"]].describe().round(2).loc[["mean", "std", "min", "max"]].to_string())
```
<!--sortie-->
```text
1212 répondants à l'enquête | 1740 clients actifs | 1076 clients actifs répondants
      score_produit  score_service      a
mean           3.64           3.55   0.17
std            0.69           0.74  10.51
min            1.25           1.25 -18.00
max            5.00           5.00  37.00
```

Nous travaillerons sur ces **`bq`** : les clients actifs qui ont répondu à l'enquête. La question est : quelles variables (âge, canal, ville, offre de bienvenue, scores produit et service, courbure de l'âge…) méritent de figurer dans le modèle du log-panier ?

### 1.4.1 Le surajustement : mieux s'ajuster n'est pas mieux prédire

Rappelons l'enjeu (volume I, chapitre 3 : biais et variance d'un estimateur). Un modèle très flexible épouse les données d'entraînement, y compris leur bruit. Pour le **voir**, faisons une expérience : on tire au hasard **40 clients** pour entraîner un modèle polynomial en l'âge de degré 0, 1, 2…, 8, et on mesure l'erreur sur les clients **non utilisés** pour l'entraînement. On répète 300 fois, et on moyenne.

```python
z = ((df["age"] - 36) / 10).to_numpy()                 # âge centré et réduit (évite les problèmes numériques des puissances)
yy = df["log_panier"].to_numpy()
rng = np.random.default_rng(21)
degres = np.arange(0, 9)
err_app, err_test = np.zeros((300, len(degres))), np.zeros((300, len(degres)))
for r in range(300):
    idx = rng.permutation(len(z))
    tr, te = idx[:40], idx[40:]
    for j, d in enumerate(degres):
        coef = np.polyfit(z[tr], yy[tr], d)
        err_app[r, j] = np.mean((yy[tr] - np.polyval(coef, z[tr])) ** 2)
        err_test[r, j] = np.mean((yy[te] - np.polyval(coef, z[te])) ** 2)
res = pd.DataFrame({"degré": degres, "erreur d'apprentissage": err_app.mean(axis=0), "erreur sur nouveaux clients": err_test.mean(axis=0)})
print(res.round(4).to_string(index=False))

fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(degres, err_app.mean(axis=0), "o-", color=BLEU, lw=2)
ax.plot(degres, err_test.mean(axis=0), "o-", color=ORANGE, lw=2)
ax.text(3.0, 0.108, "erreur sur les clients d'entraînement", color=BLEU, ha="left", va="center")
ax.text(0.1, 0.228, "erreur sur de\nnouveaux clients", color=ORANGE, ha="left", va="center")
ax.text(4.5, 0.33, "au-delà du degré 4, l'erreur\nexplose (axe coupé) :\n1,44 au degré 5,\nplus de 12 000 au degré 8", color=ORANGE, ha="left", va="center")
ax.set_xlabel("degré du polynôme en l'âge (complexité du modèle)")
ax.set_ylabel("erreur quadratique moyenne")
ax.set_xlim(-0.3, 8.5)
ax.set_ylim(0.10, 0.42)
plt.savefig("figures/ch01-surajustement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
 degré  erreur d'apprentissage  erreur sur nouveaux clients
     0                  0.1610                       0.1684
     1                  0.1490                       0.1629
     2                  0.1454                       0.1696
     3                  0.1423                       0.1853
     4                  0.1389                       0.2958
     5                  0.1353                       1.4399
     6                  0.1311                      50.3002
     7                  0.1261                     612.0571
     8                  0.1220                   12583.0488
figure enregistrée
```

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

Vérifions la formule à la main sur un modèle de `bq` :

```python
m_ex = smf.ols("log_panier ~ a + C(canal)", data=bq).fit()
n, p = m_ex.model.exog.shape
scr = m_ex.ssr
ll = -n / 2 * (np.log(2 * np.pi) + np.log(scr / n) + 1)
k = p                                                   # convention de statsmodels : on ne compte pas sigma²
print(f"log-vraisemblance : à la main = {ll:.3f} | statsmodels = {m_ex.llf:.3f}")
print(f"AIC : à la main = {-2*ll + 2*k:.3f} | statsmodels = {m_ex.aic:.3f}")
print(f"BIC : à la main = {-2*ll + k*np.log(n):.3f} | statsmodels = {m_ex.bic:.3f}")
```
<!--sortie-->
```text
log-vraisemblance : à la main = -431.472 | statsmodels = -431.472
AIC : à la main = 870.944 | statsmodels = 870.944
BIC : à la main = 890.868 | statsmodels = 890.868
```

> ⚠️ **Deux précautions.** (1) On ne peut comparer les AIC/BIC de deux modèles que s'ils sont ajustés **sur exactement les mêmes données et la même variable réponse** (comparer l'AIC d'un modèle sur $y$ à celui d'un modèle sur $\log y$ n'a aucun sens, sans correction). (2) La valeur absolue d'un AIC ne signifie rien ; seules les **différences** comptent. Une différence de moins de 2 est négligeable ; de plus de 10, très forte.

### 1.4.3 La validation croisée

Les critères d'information reposent sur des hypothèses (modèle bien spécifié, grand échantillon). La **validation croisée** est plus directe : on **simule** la prédiction sur des données nouvelles en réservant une partie des données.

**$K$-fold.** On découpe l'échantillon en $K$ paquets (*folds*) de taille égale (typiquement $K=10$). Pour chaque paquet, on ajuste le modèle sur les $K-1$ autres et on mesure l'erreur de prédiction sur le paquet laissé de côté. La moyenne des erreurs estime l'erreur de généralisation.

**Leave-one-out et la formule de PRESS.** Si $K=n$ (un client par paquet), on parle de *leave-one-out*. Pour la régression linéaire, il n'est pas nécessaire de refaire $n$ ajustements :

> 📐 **Théorème (PRESS).** L'erreur de prédiction de l'observation $i$ par le modèle ajusté **sans elle** est $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\dfrac{\hat\varepsilon_i}{1-h_{ii}}$. La somme des carrés $\text{PRESS}=\sum_i\big(\hat\varepsilon_i/(1-h_{ii})\big)^2$ s'obtient donc **avec un seul ajustement**.
> *Démonstration.* On a vu (1.3.4) que $\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)}=(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i\,\hat\varepsilon_i/(1-h_{ii})$. Multiplions à gauche par $\mathbf x_i^\top$ : $\mathbf x_i^\top\hat{\boldsymbol\beta}-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=h_{ii}\hat\varepsilon_i/(1-h_{ii})$. Donc $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\hat\varepsilon_i+h_{ii}\hat\varepsilon_i/(1-h_{ii})=\hat\varepsilon_i/(1-h_{ii})$. $\square$

Un client à fort levier est mal prédit quand on le retire, d'où le diviseur $1-h_{ii}$ : l'erreur « honnête » est supérieure au résidu brut. Vérifions par une boucle explicite de $n$ ajustements :

```python
Xb, yb = m_ex.model.exog, m_ex.model.endog
h = m_ex.get_influence().hat_matrix_diag
press_formule = np.sum((m_ex.resid / (1 - h)) ** 2)
loo = np.empty(len(yb))
for i in range(len(yb)):                                           # n ajustements, un par client écarté
    mask = np.arange(len(yb)) != i
    b_i = np.linalg.lstsq(Xb[mask], yb[mask], rcond=None)[0]
    loo[i] = yb[i] - Xb[i] @ b_i
print(f"PRESS (formule, 1 ajustement)       = {press_formule:.4f}")
print(f"PRESS (boucle, {len(yb)} ajustements) = {np.sum(loo**2):.4f}")
print(f"erreur quadratique d'apprentissage (SCR) = {scr:.4f}  <- plus optimiste")
```
<!--sortie-->
```text
PRESS (formule, 1 ajustement)       = 141.5167
PRESS (boucle, 1076 ajustements) = 141.5167
erreur quadratique d'apprentissage (SCR) = 140.4879  <- plus optimiste
```

Écrivons maintenant une fonction de validation croisée $K$-fold. **Règle importante : utiliser les mêmes paquets pour tous les modèles comparés** (comparaison appariée).

```python
def cv_rmse(formule, data, K=10, graine=0):
    """RMSE de validation croisée K-fold (sur l'échelle du log-panier), mêmes paquets pour tous les modèles."""
    kf = KFold(n_splits=K, shuffle=True, random_state=graine)
    erreurs = []
    for tr, te in kf.split(data):
        m = smf.ols(formule, data=data.iloc[tr]).fit()
        pred = np.asarray(m.predict(data.iloc[te]))
        if pred.size == 1:                                       # modèle à constante seule : predict renvoie un seul nombre
            pred = np.repeat(pred, len(te))
        erreurs.append(data.iloc[te]["log_panier"].to_numpy() - pred)
    e = np.concatenate(erreurs)
    return np.sqrt(np.mean(e ** 2))

print("RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) :", round(cv_rmse("log_panier ~ a + C(canal)", bq), 4))
print("RMSE d'apprentissage                                                   :", round(np.sqrt(scr / n), 4))
```
<!--sortie-->
```text
RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) : 0.3629
RMSE d'apprentissage                                                   : 0.3613
```

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
bq = bq.copy()
bq["a2"] = bq["a"] ** 2
candidats = {
    "M0": "log_panier ~ 1",
    "M1": "log_panier ~ a",
    "M2": "log_panier ~ a + C(canal)",
    "M3": "log_panier ~ a + C(canal) + score_produit",
    "M4": "log_panier ~ a + C(canal) + score_produit + score_service",
    "M5": "log_panier ~ a + C(canal) + score_produit + C(ville) + offre_bienvenue",
    "M6": "log_panier ~ a * C(canal) + a2 + score_produit",
    "M7": "log_panier ~ a * C(canal) + a2 + C(ville) + offre_bienvenue + score_produit + score_service",
}
lignes, fits = [], {}
for nom, f in candidats.items():
    m = smf.ols(f, data=bq).fit()
    fits[nom] = m
    h = m.get_influence().hat_matrix_diag
    lignes.append({"modèle": nom, "paramètres p": int(m.df_model) + 1, "R²": m.rsquared, "R² ajusté": m.rsquared_adj,
                   "AIC": m.aic, "BIC": m.bic, "RMSE appr.": np.sqrt(m.mse_resid * m.df_resid / m.nobs),
                   "RMSE LOO (PRESS)": np.sqrt(np.mean((m.resid / (1 - h)) ** 2)), "RMSE CV10": cv_rmse(f, bq)})
tab = pd.DataFrame(lignes).set_index("modèle")
with pd.option_context("display.width", 200):
    print(tab.round(4).to_string())
print()
for crit in ["R² ajusté", "AIC", "BIC", "RMSE LOO (PRESS)", "RMSE CV10"]:
    meilleur = tab[crit].idxmax() if crit == "R² ajusté" else tab[crit].idxmin()
    print(f"meilleur modèle selon {crit:18s} : {meilleur}")
```
<!--sortie-->
```text
        paramètres p      R²  R² ajusté        AIC        BIC  RMSE appr.  RMSE LOO (PRESS)  RMSE CV10
modèle                                                                                                
M0                 1  0.0000     0.0000  1082.3441  1087.3251      0.3997            0.4001     0.4005
M1                 2  0.0663     0.0654  1010.5132  1020.4752      0.3863            0.3870     0.3872
M2                 4  0.1829     0.1807   870.9438   890.8679      0.3613            0.3627     0.3629
M3                 5  0.2542     0.2514   774.7862   799.6912      0.3452            0.3469     0.3478
M4                 6  0.2567     0.2532   773.1610   803.0470      0.3446            0.3466     0.3474
M5                11  0.2548     0.2478   785.8815   840.6726      0.3451            0.3487     0.3503
M6                 8  0.2549     0.2500   779.7843   819.6323      0.3451            0.3476     0.3485
M7                15  0.2582     0.2484   788.9871   863.7021      0.3443            0.3491     0.3506

meilleur modèle selon R² ajusté          : M4
meilleur modèle selon AIC                : M4
meilleur modèle selon BIC                : M3
meilleur modèle selon RMSE LOO (PRESS)   : M4
meilleur modèle selon RMSE CV10          : M4
```

Lisons ce tableau avec méthode.

- Le **$R^2$ et le RMSE d'apprentissage** s'améliorent (ou restent égaux) à chaque ajout de variables : ils recommandent toujours le modèle le plus gros (M7). Pas un critère de sélection.
- Les **critères corrigés** (AIC, BIC, $R^2$ ajusté, validation croisée) arrêtent leur progression bien avant. Retenez l'ordre de grandeur : l'ajout du **score produit** (M2 → M3) est un gain énorme, l'ajout du **score service** (M3 → M4) est marginal, et tout ce qui vient après (ville, offre, âge², interactions) n'apporte **rien** (voire détériore).
- Le **BIC**, plus sévère, désigne le modèle **M3**. Les autres critères (AIC, $R^2$ ajusté, PRESS, validation croisée) désignent **M4**, qui ajoute le score service, mais **de justesse** : l'AIC de M4 est inférieur de 1,6 point à celui de M3 (différence inférieure à 2 : négligeable, selon la règle du 1.4.2), et le RMSE de validation croisée passe de 0,3478 à 0,3474. M3 et M4 prédisent donc pratiquement aussi bien ; à prédiction égale, on **préfère le plus simple** (principe de parcimonie), ce que fait le BIC. Les trois mesures hors échantillon (PRESS, CV10) sont très proches l'une de l'autre, ce qui rassure sur la fiabilité du classement.

**Les tests emboîtés** (1.2.3) répondent à des questions précises sur des modèles qui se contiennent :

```python
print("M2 -> M3 (ajout du score produit) :")
print(sm.stats.anova_lm(fits["M2"], fits["M3"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M4 (ajout du score service) :")
print(sm.stats.anova_lm(fits["M3"], fits["M4"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M5"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M6 (âge² et interactions, 3 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M6"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
```
<!--sortie-->
```text
M2 -> M3 (ajout du score produit) :
   df_resid  df_diff         F  Pr(>F)
0    1072.0      0.0       NaN     NaN
1    1071.0      1.0  102.2966     0.0

M3 -> M4 (ajout du score service) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1070.0      1.0  3.6111  0.0577

M3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1065.0      6.0  0.1493  0.9892

M3 -> M6 (âge² et interactions, 3 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1068.0      3.0  0.3316  0.8025
```

Le score produit est hautement significatif ; le score service est **à la limite** (p-valeur autour de 0,05) ; la ville, l'offre de bienvenue, la courbure de l'âge et les interactions n'ont **aucun** effet décelable. C'est cohérent avec les critères d'information : *deux méthodes différentes, la même conclusion*. Le cas du score service illustre bien la tension entre AIC et BIC : sa $t$-statistique, voisine de 1,9, dépasse le seuil $\sqrt2\approx1{,}41$ que l'AIC applique implicitement (un paramètre en plus est conservé si $t^2>2$) mais pas le seuil $\sqrt{\log n}\approx2{,}6$ du BIC pour $n\approx1000$.

### 1.4.5 La sélection automatique, et pourquoi il faut s'en méfier

Avec beaucoup de variables, comparer à la main devient impossible, d'où la tentation des procédures automatiques : sélection **ascendante** (*forward* : on part de rien et on ajoute à chaque étape la variable qui améliore le plus), **descendante** (*backward*), **pas à pas** (*stepwise*), ou **tous les sous-ensembles**. Elles sont commodes, mais elles posent un problème **statistique profond** : *le modèle final est choisi sur les données, puis ses p-valeurs sont lues comme si on l'avait choisi à l'avance.* Les p-valeurs et les intervalles du modèle final sont donc **trop optimistes**.

Une simulation le montre. On génère $n=100$ observations d'une variable réponse $y$ qui **n'a aucun lien** avec 20 variables explicatives (toutes du pur bruit). On applique la sélection ascendante par p-valeur (on ajoute la variable la plus significative tant que sa p-valeur est inférieure à 0,05). Combien de « découvertes » la méthode va-t-elle faire ? On répète 500 fois.

```python
def selection_ascendante(X, y, alpha=0.05):
    """Sélection ascendante par p-valeur. X : matrice n x q sans constante. Retourne la liste des colonnes retenues."""
    n, q = X.shape
    retenues = []
    while len(retenues) < q:
        meilleur, p_min = None, 1.0
        for j in range(q):
            if j in retenues:
                continue
            Z = np.column_stack([np.ones(n), X[:, retenues + [j]]])
            b, _, _, _ = np.linalg.lstsq(Z, y, rcond=None)
            e = y - Z @ b
            s2 = e @ e / (n - Z.shape[1])
            se = np.sqrt(s2 * np.linalg.inv(Z.T @ Z)[-1, -1])
            pj = 2 * stats.t.sf(abs(b[-1] / se), n - Z.shape[1])
            if pj < p_min:
                meilleur, p_min = j, pj
        if meilleur is None or p_min >= alpha:
            break
        retenues.append(meilleur)
    return retenues

def ols_pvaleurs(X, y):
    Z = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    e = y - Z @ b
    s2 = e @ e / (len(y) - Z.shape[1])
    se = np.sqrt(s2 * np.diag(np.linalg.inv(Z.T @ Z)))
    return 2 * stats.t.sf(np.abs(b / se), len(y) - Z.shape[1])[1:], 1 - (e @ e) / np.sum((y - y.mean()) ** 2)

rng = np.random.default_rng(99)
R, n_obs, q = 500, 100, 20
nb_retenues, r2_final, sig_final, sig_honnete, nb_honnete = [], [], [], [], []
for _ in range(R):
    X = rng.normal(size=(n_obs, q)); y = rng.normal(size=n_obs)            # y est indépendant de tout X
    ret = selection_ascendante(X, y)
    nb_retenues.append(len(ret))
    if ret:
        pv, r2 = ols_pvaleurs(X[:, ret], y)
        r2_final.append(r2); sig_final.append(np.mean(pv < 0.05))
    # procédure honnête : on choisit sur les 50 premiers, on teste sur les 50 autres
    ret_h = selection_ascendante(X[:50], y[:50])
    if ret_h:
        pv_h, _ = ols_pvaleurs(X[50:][:, ret_h], y[50:])
        sig_honnete.append(np.sum(pv_h < 0.05)); nb_honnete.append(len(ret_h))
nb_retenues = np.array(nb_retenues)
print(f"y est du pur bruit, indépendant des {q} variables explicatives (n = {n_obs}).")
print(f"part des jeux de données où au moins une variable est « découverte » : {np.mean(nb_retenues > 0):.1%}  (théorie pour une seule étape : 1 - 0,95^20 = {1 - 0.95**20:.1%})")
print(f"nombre moyen de variables retenues : {nb_retenues.mean():.2f}")
print(f"R² moyen du modèle final (quand il est non vide) : {np.mean(r2_final):.3f}  alors que le vrai R² est 0")
print(f"part de coefficients « significatifs à 5 % » dans le modèle final : {np.mean(sig_final):.1%}  (c'est trompeur : ils ont été choisis POUR l'être)")
print(f"procédure honnête (choix sur la moitié A, test sur la moitié B) : {np.sum(sig_honnete) / np.sum(nb_honnete):.1%} de significatifs parmi les variables retenues (≈ 5 % attendu)")
```
<!--sortie-->
```text
y est du pur bruit, indépendant des 20 variables explicatives (n = 100).
part des jeux de données où au moins une variable est « découverte » : 63.4%  (théorie pour une seule étape : 1 - 0,95^20 = 64.2%)
nombre moyen de variables retenues : 1.09
R² moyen du modèle final (quand il est non vide) : 0.093  alors que le vrai R² est 0
part de coefficients « significatifs à 5 % » dans le modèle final : 100.0%  (c'est trompeur : ils ont été choisis POUR l'être)
procédure honnête (choix sur la moitié A, test sur la moitié B) : 5.6% de significatifs parmi les variables retenues (≈ 5 % attendu)
```

Dans près des deux tiers des jeux de données, la procédure « découvre » au moins une variable explicative, alors qu'il n'y en a **aucune** ; le $R^2$ du modèle final est nettement positif (environ 0,09 en moyenne, alors que la vraie valeur est 0) ; et, dans le modèle final, les coefficients retenus apparaissent **tous** significatifs, ce qui est trompeur : ils n'ont été retenus que parce qu'ils l'étaient. La procédure « honnête », qui **sépare** les données utilisées pour choisir des données utilisées pour tester, retrouve le taux d'erreur attendu de 5 %.

> ⚠️ **Les défauts de la sélection automatique.** (1) Les **p-valeurs et intervalles** du modèle final sont **trop optimistes** (biais de sélection). (2) Les coefficients retenus sont **gonflés** en valeur absolue (on garde ceux qui, par chance, sont grands). (3) Le résultat est **instable** : un autre échantillon donne un autre modèle. (4) Les procédures ne connaissent pas **le sens** des variables : on risque de retirer une variable de confusion essentielle. (5) Plus on essaie de modèles, plus on a de chances d'en trouver un « bon » par hasard (c'est le problème des tests multiples du volume I, section 3.5.5).

> 🛠️ **Bonnes pratiques.** (1) **Commencez par la connaissance du domaine** : quelles variables ont un sens ? (2) Fixez les modèles candidats **à l'avance**, en petit nombre, et comparez-les par AIC/BIC et validation croisée. (3) Si vous devez explorer beaucoup de variables, **mettez de côté un échantillon de test** *avant* de commencer, et ne l'utilisez qu'**une fois**, à la fin. (4) Pour la prédiction avec beaucoup de variables, préférez la **régularisation** (section 1.5), qui fait une sélection plus stable. (5) Décrivez honnêtement tout ce qui a été essayé.

### 1.4.6 Verdict : retrouver la vérité

Nous avons un luxe : les données sont simulées, nous connaissons donc le vrai modèle (détails dans la documentation de `build/donnees2.py`). Les clients actifs ont été produits par

$$\log(\text{panier})=4{,}00+0{,}008\,(\text{âge}-36)+\delta_{\text{canal}}+0{,}12\,F_1+\varepsilon,\qquad\varepsilon\sim\mathcal N(0,\,0{,}35^2),$$

avec $\delta=+0{,}22$ pour la Boutique, $+0{,}05$ pour le Site, $-0{,}12$ pour Instagram. Ici $F_1$ est un **« goût pour les produits »** non observé (de moyenne 0 et d'écart-type 1) ; ni la ville, ni l'offre de bienvenue, ni le score de service **n'interviennent** dans le panier. Comparons au modèle M3 retenu par le BIC :

```python
m3 = fits["M3"]
ic = m3.conf_int()
vrai_site, vrai_insta = 0.05 - 0.22, -0.12 - 0.22              # effets du Site et d'Instagram RELATIVEMENT à la Boutique
vrai = {"Intercept": np.nan, "C(canal)[T.Site]": vrai_site, "C(canal)[T.Instagram]": vrai_insta, "a": 0.008}
comp = pd.DataFrame({"estimation (M3)": m3.params, "IC95 bas": ic[0], "IC95 haut": ic[1]})
comp["vérité"] = pd.Series(vrai)
comp["IC contient la vérité ?"] = [("oui" if (lo <= v <= hi) else "non") if not np.isnan(v) else "—" for lo, hi, v in zip(comp["IC95 bas"], comp["IC95 haut"], comp["vérité"])]
print(comp.round(4).to_string())
print()
print("Variables retenues dans M3 : âge, canal, score produit. Écartées par les critères : ville, offre, score service, âge², interactions.")
print("Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :")
print(fits["M7"].pvalues[["C(ville)[T.Bizerte]", "C(ville)[T.Nabeul]", "C(ville)[T.Sfax]", "C(ville)[T.Sousse]", "C(ville)[T.Tunis]", "offre_bienvenue", "a2", "score_service"]].round(3).to_string())
```
<!--sortie-->
```text
                       estimation (M3)  IC95 bas  IC95 haut  vérité IC contient la vérité ?
Intercept                       3.6543    3.5385     3.7701     NaN                       —
C(canal)[T.Site]               -0.1573   -0.2114    -0.1032  -0.170                     oui
C(canal)[T.Instagram]          -0.3519   -0.4045    -0.2993  -0.340                     oui
a                               0.0097    0.0078     0.0117   0.008                     oui
score_produit                   0.1557    0.1255     0.1859     NaN                       —

Variables retenues dans M3 : âge, canal, score produit. Écartées par les critères : ville, offre, score service, âge², interactions.
Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :
C(ville)[T.Bizerte]    0.901
C(ville)[T.Nabeul]     0.934
C(ville)[T.Sfax]       0.526
C(ville)[T.Sousse]     0.808
C(ville)[T.Tunis]      0.883
offre_bienvenue        0.788
a2                     0.300
score_service          0.051
```

Les effets du **canal** et de l'**âge** sont retrouvés : les intervalles à 95 % contiennent les vraies valeurs (−0,17 pour le Site, −0,34 pour Instagram, +0,008 par année d'âge). La méthode a bien écarté les variables **sans effet réel** (ville, offre, courbure, interactions). L'intercept ne se compare pas directement, car dans M3 il correspond à un score produit de 0 (une valeur impossible sur une échelle de 1 à 5) : un bon exemple de la nécessité de **centrer** les variables pour interpréter la constante.

Reste le cas du **score service** : il n'a aucun effet direct dans le vrai modèle du panier, et pourtant l'AIC et la validation croisée le **gardent**, de justesse, avec une $t$-statistique voisine de 1,9. C'est la **conséquence mécanique** de la corrélation entre les facteurs « produit » et « service » dans la population (corrélation de 0,3 entre $F_1$ et $F_2$) : le score de service est un peu informatif sur $F_1$, donc sur le panier. Et c'est un rappel qu'**une association n'est pas un effet**.

**Un dernier point, sur le score produit.** Le vrai effet est de **0,12 par écart-type de $F_1$**. Or le coefficient estimé (0,15 environ) est un effet **par point de note**, ce qui est autre chose : la note moyenne est un reflet **imparfait** de $F_1$ (chaque question est bruitée). Un calcul direct à partir de la façon dont les notes ont été simulées (volume II, `donnees2.py` : $q_j\approx3{,}6+0{,}95\,(\lambda_jF_1+\sqrt{1-\lambda_j^2}\,\eta_j)$, avec des poids $\lambda_j=0{,}8;\,0{,}7;\,0{,}75;\,0{,}6$) permet de prédire le coefficient attendu **par point de note** :

```python
lam = np.array([0.80, 0.70, 0.75, 0.60])
var_bruit = np.mean(1 - lam**2) / 4                       # variance du bruit de la moyenne de 4 questions (en unités de F1)
charge = lam.mean()                                        # poids moyen de F1 dans la moyenne des questions
fiabilite = charge**2 / (charge**2 + var_bruit)            # part de la variance de la note qui provient de F1
cov_F_score = 0.95 * charge
var_score = 0.95**2 * (charge**2 + var_bruit)
pente_F_sur_score = cov_F_score / var_score                # E[F1 | score] = pente * (score - moyenne)
print(f"fiabilité du score produit : {fiabilite:.2f}")
print(f"effet attendu par point de note : 0,12 x {pente_F_sur_score:.3f} = {0.12 * pente_F_sur_score:.3f}   | estimé dans M3 : {m3.params['score_produit']:.3f}  (IC95 % : [{ic.loc['score_produit', 0]:.3f} ; {ic.loc['score_produit', 1]:.3f}])")
```
<!--sortie-->
```text
fiabilité du score produit : 0.81
effet attendu par point de note : 0,12 x 1.192 = 0.143   | estimé dans M3 : 0.156  (IC95 % : [0.125 ; 0.186])
```

La valeur attendue tombe **à l'intérieur** de l'intervalle de confiance. La **fiabilité** (la part de la variance de la note qui provient du vrai facteur, environ 0,8) est une notion générale : quand une variable explicative est mesurée avec du bruit, son coefficient est **atténué** par rapport à l'effet de la grandeur « vraie » (*erreur de mesure*) ; ici, la conversion d'échelle (par point de note plutôt que par écart-type de $F_1$) cache cet effet, mais il est bien là.

> 🧪 **Une dernière subtilité (hors programme, mais honnête).** Nous n'observons le panier que pour les clients **actifs** (ayant commandé), et l'activité dépend elle-même de $F_1$ dans la simulation (le goût pour les produits augmente le nombre de commandes). En ne gardant que les clients actifs, nous opérons une **sélection** qui peut biaiser légèrement la relation entre les notes et le panier. Le biais est ici faible et invisible dans les intervalles ; mais en pratique, restreindre un échantillon sur une variable liée à la réponse est une source classique de biais, que la section 2.6 (modèles à zéros excédentaires) permettra de traiter proprement.

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

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.linear_model import Ridge, RidgeCV, Lasso, LassoCV, ElasticNetCV, lasso_path, LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)
```

### 1.5.1 La régression Ridge

**Le principe.** On ajoute à la somme des carrés une pénalité sur la **norme au carré** des coefficients (sans la constante) :

$$\hat{\boldsymbol\beta}_{\text{ridge}}(\lambda)=\arg\min_{\boldsymbol\beta}\ \|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\lambda\|\boldsymbol\beta\|^2,\qquad\lambda\ge0 .$$

Le **paramètre de régularisation** $\lambda$ règle la sévérité de la laisse : $\lambda=0$ redonne les moindres carrés, $\lambda\to\infty$ écrase tous les coefficients vers 0.

> 📐 **Solution explicite.** Le gradient de la fonction objectif est $-2\mathbf X^\top(\mathbf y-\mathbf X\boldsymbol\beta)+2\lambda\boldsymbol\beta$. En l'annulant :
> $$(\mathbf X^\top\mathbf X+\lambda\mathbf I)\,\hat{\boldsymbol\beta}_{\text{ridge}}=\mathbf X^\top\mathbf y\quad\Longrightarrow\quad\hat{\boldsymbol\beta}_{\text{ridge}}=(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y .$$
> Pour $\lambda>0$, $\mathbf X^\top\mathbf X+\lambda\mathbf I$ est **toujours inversible** (ses valeurs propres sont $\ge\lambda>0$), même si $\mathbf X$ n'est pas de rang plein ou si $p>n$ : la régularisation résout aussi le problème de la colinéarité parfaite.

Deux règles pratiques, essentielles : (1) **la constante n'est pas pénalisée** (on centre simplement $\mathbf y$ et les colonnes de $\mathbf X$) ; (2) **il faut standardiser les variables** (moyenne 0, écart-type 1) : sinon la pénalité frappe plus les variables exprimées dans de petites unités (un âge en années contre un revenu en milliers de dinars) et le résultat dépend des unités choisies.

**Voir ce que fait la pénalité : la SVD.** Écrivons la décomposition en valeurs singulières de $\mathbf X$ centrée : $\mathbf X=\mathbf U\mathbf D\mathbf V^\top$ (volume I, section 1.1.4), où les $d_j$ sont les valeurs singulières. Alors

$$\mathbf X\hat{\boldsymbol\beta}_{\text{ridge}}=\sum_{j=1}^p\mathbf u_j\,\frac{d_j^2}{d_j^2+\lambda}\,\mathbf u_j^\top\mathbf y .$$

> 📐 **Démonstration.** $(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}=\mathbf V(\mathbf D^2+\lambda\mathbf I)^{-1}\mathbf V^\top$ et $\mathbf X^\top\mathbf y=\mathbf V\mathbf D\mathbf U^\top\mathbf y$, donc $\mathbf X\hat{\boldsymbol\beta}_{\text{ridge}}=\mathbf U\mathbf D(\mathbf D^2+\lambda\mathbf I)^{-1}\mathbf D\mathbf U^\top\mathbf y$, matrice diagonale $d_j^2/(d_j^2+\lambda)$. $\square$

Les moindres carrés correspondent à $\lambda=0$ : tous les facteurs valent 1. Ridge **rétrécit** chaque direction principale $\mathbf u_j$ d'un facteur $d_j^2/(d_j^2+\lambda)\in(0,1)$ : **très peu** pour les directions où les données varient beaucoup ($d_j$ grand), **beaucoup** pour celles où elles varient peu ($d_j$ petit), c'est-à-dire précisément les directions de **quasi-colinéarité**, où l'estimation par moindres carrés est la plus instable.

**Pourquoi un estimateur biaisé peut être meilleur.** L'erreur quadratique moyenne (EQM) d'un estimateur se décompose en $\text{biais}^2+\text{variance}$ (volume I, section 3.2.2). Prenons le cas le plus simple, où les colonnes de $\mathbf X$ sont orthonormales ($\mathbf X^\top\mathbf X=\mathbf I$) : alors $\hat\beta_j^{\text{MCO}}=\beta_j+\eta_j$ avec $\operatorname{Var}\eta_j=\sigma^2$, et $\hat\beta_j^{\text{ridge}}=\hat\beta_j^{\text{MCO}}/(1+\lambda)$.

> 📐 **L'EQM de Ridge est inférieure à celle des MCO pour un $\lambda$ petit.** Pour Ridge, biais $=-\dfrac{\lambda}{1+\lambda}\beta_j$ et variance $=\dfrac{\sigma^2}{(1+\lambda)^2}$, donc
> $$\text{EQM}(\lambda)=\frac{\lambda^2\beta_j^2+\sigma^2}{(1+\lambda)^2}.$$
> Sa dérivée en $\lambda=0$ vaut $-2\sigma^2<0$ : **l'EQM décroît dès qu'on s'écarte de $\lambda=0$**, quel que soit $\beta_j$. Le minimum est atteint en $\lambda^\star=\sigma^2/\beta_j^2$ : la bonne régularisation est d'autant plus forte que le bruit est grand et le signal faible. Le gain n'est pas un accident : *il existe toujours un $\lambda>0$ pour lequel Ridge bat les moindres carrés en EQM*.

**Voyons-le par simulation.** Deux variables explicatives très corrélées (corrélation 0,98), $n=30$, des vrais coefficients $(1,\,1)$ et $\sigma=1$. On répète 4 000 fois l'expérience et on mesure l'EQM des estimateurs pour plusieurs $\lambda$ :

```python
rng = np.random.default_rng(4)
n_s, rho = 30, 0.98
cov = np.array([[1, rho], [rho, 1]])
Xs = rng.multivariate_normal([0, 0], cov, size=n_s)
Xs = (Xs - Xs.mean(axis=0)) / Xs.std(axis=0)                     # variables centrées et standardisées, FIXES pour toute l'expérience
beta_vrai = np.array([1.0, 1.0]) / np.sqrt(n_s) * 3              # vrais coefficients (de petite taille relative au bruit)
R = 4000
resultats = {}
for lam in [0, 0.5, 1, 2, 5, 10, 20, 50]:
    M = np.linalg.solve(Xs.T @ Xs + lam * np.eye(2), Xs.T)       # (X'X + lambda I)^-1 X'
    erreurs = np.empty((R, 2))
    for r in range(R):
        y_s = Xs @ beta_vrai + rng.normal(0, 1, n_s)
        erreurs[r] = M @ y_s - beta_vrai
    if lam == 0:
        erreurs_mco = erreurs.copy()
    resultats[lam] = (np.mean(np.sum(erreurs**2, axis=1)), np.sum(erreurs.mean(axis=0)**2), np.sum(erreurs.var(axis=0)))
tab = pd.DataFrame(resultats, index=["EQM totale", "biais² total", "variance totale"]).T
tab.index.name = "lambda"
print("corrélation entre les deux variables :", round(np.corrcoef(Xs.T)[0, 1], 3))
print(tab.round(4).to_string())
print("corrélation entre les deux estimations MCO du même échantillon :", round(np.corrcoef(erreurs_mco.T)[0, 1], 3))
```
<!--sortie-->
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

**À la main contre `scikit-learn`.** Vérifions notre formule sur les données de Dar Jasmin, avec les notes de l'enquête (nous introduisons ici le jeu de variables de la section suivante) :

```python
clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client").reset_index(drop=True)

# Un petit jeu de variables : l'âge, le canal, les scores
Xp = pd.DataFrame({"age": bq["a"], "Site": (bq["canal"] == "Site").astype(float), "Instagram": (bq["canal"] == "Instagram").astype(float),
                   "score_produit": bq["score_produit"], "score_service": bq["score_service"]})
yv = bq["log_panier"].to_numpy()
sc = StandardScaler().fit(Xp)
Z = sc.transform(Xp)
yc = yv - yv.mean()
lam = 50.0
beta_main = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ yc)
sk = Ridge(alpha=lam).fit(Z, yv)
print(pd.DataFrame({"à la main": beta_main, "scikit-learn": sk.coef_, "MCO (λ = 0)": LinearRegression().fit(Z, yv).coef_}, index=Xp.columns).round(5).to_string())
```
<!--sortie-->
```text
               à la main  scikit-learn  MCO (λ = 0)
age              0.09800       0.09800      0.10255
Site            -0.06342      -0.06342     -0.07490
Instagram       -0.15797      -0.15797     -0.17241
score_produit    0.09827       0.09827      0.10322
score_service    0.02016       0.02016      0.02035
```

Les deux colonnes de Ridge coïncident : `scikit-learn` fait exactement le calcul de la formule. Les coefficients de Ridge sont **rétrécis** par rapport aux moindres carrés, modestement ici ($\lambda=50$ est petit devant $n\approx1\,000$) : environ 4 % pour l'âge, 15 % pour le Site, 8 % pour Instagram. Le rétrécissement est le plus marqué pour les indicatrices du canal, qui sont **corrélées entre elles** (les clients Site ne sont pas Instagram) : leurs directions ont de petites valeurs singulières, exactement celles que le facteur $d_j^2/(d_j^2+\lambda)$ pénalise le plus.

### 1.5.2 Le Lasso : la pénalité qui élimine des variables

Ridge rétrécit tous les coefficients, mais **n'en met jamais aucun exactement à 0**. Le **Lasso** (*Least Absolute Shrinkage and Selection Operator*) remplace le carré par la **valeur absolue** :

$$\hat{\boldsymbol\beta}_{\text{lasso}}(\alpha)=\arg\min_{\boldsymbol\beta}\ \frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\sum_j|\beta_j| .$$

(La normalisation $1/(2n)$ est celle de `scikit-learn`.) Ce changement apparemment minuscule a une conséquence majeure : le Lasso produit des solutions **creuses**, où beaucoup de coefficients sont **exactement nuls**. C'est une régression qui **sélectionne** ses variables tout en les ajustant.

> 💡 **Pourquoi des zéros ? La géométrie.** Minimiser la somme des carrés sous la contrainte $\sum_j\beta_j^2\le r^2$ (Ridge) ou $\sum_j|\beta_j|\le r$ (Lasso) donne le même résultat que les versions pénalisées. Les courbes de niveau de la somme des carrés sont des **ellipses** centrées sur la solution des moindres carrés ; la solution contrainte est le **premier point de contact** entre une ellipse qui grandit et la région admissible. Pour Ridge, la région est un **disque** : le contact est un point lisse, quelconque, où aucun coefficient n'est nul. Pour le Lasso, la région est un **losange** dont les **sommets sont sur les axes** : une ellipse qui grandit touche très souvent un sommet, où un coefficient est exactement nul.

```python
def solution_contrainte(centre, A, region, r, n_pts=4000):
    """Point de la frontière de la région (norme p = 1 ou 2, rayon r) qui minimise (b-c)'A(b-c)."""
    t = np.linspace(0, 2 * np.pi, n_pts)
    if region == 2:
        pts = r * np.column_stack([np.cos(t), np.sin(t)])
    else:
        c, s_ = np.cos(t), np.sin(t)
        pts = r * np.column_stack([c, s_]) / (np.abs(c) + np.abs(s_))[:, None]
    d = pts - centre
    val = np.einsum("ij,jk,ik->i", d, A, d)
    k = np.argmin(val)
    return pts[k], val[k]

centre = np.array([2.0, 0.30])                                  # solution des moindres carrés
theta = np.deg2rad(-30)
Rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
A = Rot @ np.diag([1.0, 3.0]) @ Rot.T                           # ellipses allongées
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
for ax, region, titre in zip(axes, [2, 1], ["Ridge : contrainte en disque", "Lasso : contrainte en losange"]):
    r = 1.15
    t = np.linspace(0, 2 * np.pi, 400)
    if region == 2:
        ax.fill(r * np.cos(t), r * np.sin(t), color=BLEU, alpha=0.18)
        ax.plot(r * np.cos(t), r * np.sin(t), color=BLEU, lw=1.8)
    else:
        sommets = np.array([[r, 0], [0, r], [-r, 0], [0, -r], [r, 0]])
        ax.fill(sommets[:, 0], sommets[:, 1], color=BLEU, alpha=0.18)
        ax.plot(sommets[:, 0], sommets[:, 1], color=BLEU, lw=1.8)
    sol, val = solution_contrainte(centre, A, region, r)
    for niveau in [val * 0.25, val * 0.6, val, val * 2.4, val * 5]:           # ellipses de niveau
        u = np.linspace(0, 2 * np.pi, 400)
        w, V = np.linalg.eigh(A)
        el = np.sqrt(niveau) * (V @ np.diag(1 / np.sqrt(w)) @ np.vstack([np.cos(u), np.sin(u)])).T + centre
        ax.plot(el[:, 0], el[:, 1], color=ORANGE if np.isclose(niveau, val) else GRIS, lw=1.6 if np.isclose(niveau, val) else 0.9)
    ax.scatter(*centre, color=ENCRE, zorder=5, s=30); ax.annotate("moindres carrés", centre, textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.scatter(*sol, color=ROUGE, zorder=6, s=45); ax.annotate("solution\npénalisée", sol, textcoords="offset points", xytext=(14, -40) if region == 2 else (16, -42), color=ROUGE, fontsize=9)
    ax.axhline(0, color=GRIS, lw=0.8); ax.axvline(0, color=GRIS, lw=0.8)
    ax.set_xlim(-1.6, 3.1); ax.set_ylim(-1.6, 1.9); ax.set_aspect("equal")
    ax.set_xlabel("coefficient β₁"); ax.set_ylabel("coefficient β₂"); ax.set_title(titre, fontsize=10.5)
    print(f"{titre}: solution = ({sol[0]:.3f}, {sol[1]:.3f})")
plt.tight_layout()
plt.savefig("figures/ch01-geometrie-ridge-lasso.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Ridge : contrainte en disque: solution = (1.071, 0.420)
Lasso : contrainte en losange: solution = (1.150, 0.000)
figure enregistrée
```

![La géométrie de la régularisation. Les ellipses sont les courbes de niveau de la somme des carrés, centrées sur la solution des moindres carrés. À gauche (Ridge), la région admissible est un disque et le point de contact a ses deux coordonnées non nulles. À droite (Lasso), la région est un losange : le contact se fait au sommet, sur l'axe, avec β₂ = 0 exactement.](figures/ch01-geometrie-ridge-lasso.png)

**Comment calcule-t-on le Lasso ?** Il n'a pas de formule fermée (la valeur absolue n'est pas dérivable en 0), mais un algorithme très simple : la **descente par coordonnées**. On optimise un coefficient à la fois, les autres étant fixés, et on recommence jusqu'à stabilisation. Pour des variables standardisées ($\tfrac1n\mathbf x_j^\top\mathbf x_j=1$), la mise à jour du coefficient $j$ est donnée par un **seuillage doux** :

$$\beta_j\leftarrow S\big(\rho_j,\alpha\big),\qquad\rho_j=\frac1n\mathbf x_j^\top\big(\mathbf y-\textstyle\sum_{k\ne j}\mathbf x_k\beta_k\big),\qquad S(\rho,\alpha)=\operatorname{signe}(\rho)\,\max(|\rho|-\alpha,\,0).$$

> 📐 **Pourquoi le seuillage doux ?** Fixons les autres coefficients : on minimise en $\beta_j$ la fonction $\tfrac12(\beta_j-\rho_j)^2+\alpha|\beta_j|$ (en développant et en utilisant $\tfrac1n\mathbf x_j^\top\mathbf x_j=1$). Pour $\beta_j>0$, la dérivée est $\beta_j-\rho_j+\alpha$, nulle en $\beta_j=\rho_j-\alpha$, valable si $\rho_j>\alpha$ ; symétriquement pour $\beta_j<0$. Si $|\rho_j|\le\alpha$, la dérivée à droite en 0 ($-\rho_j+\alpha$) est $\ge0$ et la dérivée à gauche ($-\rho_j-\alpha$) est $\le0$ : le minimum est exactement en **0**. Le Lasso **ramène à 0** toute variable dont la corrélation (partielle) avec le résidu est inférieure au seuil $\alpha$, et **rétrécit de $\alpha$** les autres.

Écrivons-la à la main et comparons à `scikit-learn` :

```python
def lasso_coordonnees(Z, y, alpha, n_iter=500):
    n_, p_ = Z.shape
    beta = np.zeros(p_)
    for _ in range(n_iter):
        for j in range(p_):
            r_partiel = y - Z @ beta + Z[:, j] * beta[j]              # résidu en retirant l'effet de toutes les variables sauf j
            rho = Z[:, j] @ r_partiel / n_
            beta[j] = np.sign(rho) * max(abs(rho) - alpha, 0.0)        # seuillage doux
    return beta

alpha = 0.05
b_main = lasso_coordonnees(Z, yc, alpha)
b_sk = Lasso(alpha=alpha, max_iter=100000, tol=1e-12).fit(Z, yv).coef_
print(pd.DataFrame({"à la main": b_main, "scikit-learn": b_sk, "MCO": LinearRegression().fit(Z, yv).coef_}, index=Xp.columns).round(5).to_string())
print("coefficients exactement nuls (à la main) :", list(Xp.columns[b_main == 0]))
```
<!--sortie-->
```text
               à la main  scikit-learn      MCO
age              0.05297       0.05297  0.10255
Site            -0.00000      -0.00000 -0.07490
Instagram       -0.07486      -0.07486 -0.17241
score_produit    0.05465       0.05465  0.10322
score_service    0.00000       0.00000  0.02035
coefficients exactement nuls (à la main) : ['Site', 'score_service']
```

Les deux versions coïncident, ce qui valide notre algorithme. Mais regardez ce que fait ce seuil $\alpha=0{,}05$, choisi arbitrairement : le Lasso met à zéro `score_service`, qui (dans le vrai modèle) n'a pas d'effet direct sur le panier, mais aussi `Site`, qui **a** un vrai effet (−15 % environ, 1.2.2), et il **divise par deux** à peu près les autres coefficients. Cette pénalité est donc **trop forte** : un $\alpha$ mal choisi supprime de vraies variables et sous-estime les effets. D'où l'importance de choisir $\alpha$ par validation croisée, ce que nous faisons maintenant.

### 1.5.3 L'Elastic Net : un compromis

Le Lasso a un défaut : face à un **groupe de variables très corrélées**, il en choisit une presque au hasard et élimine les autres, de façon instable. Ridge, au contraire, répartit le poids entre elles. L'**Elastic Net** combine les deux pénalités :

$$\frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\Big(\rho\sum_j|\beta_j|+\frac{1-\rho}2\sum_j\beta_j^2\Big),\qquad\rho\in[0,1].$$

Pour $\rho=1$ c'est le Lasso, pour $\rho\to0$, Ridge. Il fournit des solutions **creuses** tout en étant **stables** en présence de variables corrélées. On choisit $\alpha$ et $\rho$ par validation croisée.

### 1.5.4 Application : beaucoup de variables, peu de clients

Mettons les trois méthodes à l'épreuve dans un scénario réaliste d'**analyse exploratoire** : on dispose de **35 variables candidates** pour prévoir le log-panier d'un client, et de seulement **120 clients** pour apprendre le modèle. Parmi ces 35 variables : 4 portent un vrai signal (l'âge, deux indicatrices de canal, le score produit), quelques-unes sont des **variables pertinentes mais inutiles** (ville, offre de bienvenue, score service, courbure de l'âge, interactions), et **20 sont du pur bruit** que nous ajoutons (nombres tirés au hasard : des « variables » sans aucun rapport avec les clients). On teste sur les 956 autres clients de l'enquête.

```python
rng = np.random.default_rng(31)
ville = bq["id_client"].map(clients.set_index("id_client")["ville"])
villes = pd.get_dummies(ville, prefix="ville", drop_first=True, dtype=float)       # 5 indicatrices (Autre = référence)
F = pd.DataFrame({
    "age": bq["a"].astype(float), "age_carre": bq["a"].astype(float) ** 2, "age_cube": bq["a"].astype(float) ** 3,
    "canal_Site": (bq["canal"] == "Site").astype(float), "canal_Instagram": (bq["canal"] == "Instagram").astype(float),
    "offre_bienvenue": bq["id_client"].map(clients.set_index("id_client")["offre_bienvenue"]).astype(float),
    "score_produit": bq["score_produit"], "score_service": bq["score_service"],
    "age_x_Site": bq["a"] * (bq["canal"] == "Site").astype(float), "age_x_Instagram": bq["a"] * (bq["canal"] == "Instagram").astype(float),
})
F = pd.concat([F, villes], axis=1)
bruit = pd.DataFrame(rng.normal(size=(len(F), 20)), columns=[f"bruit_{i+1:02d}" for i in range(20)])
F = pd.concat([F, bruit], axis=1)
signal = ["age", "canal_Site", "canal_Instagram", "score_produit"]               # les variables qui ont un VRAI effet dans la simulation
print("nombre de variables candidates :", F.shape[1], "| dont du pur bruit :", 20, "| clients :", len(F))

ordre = rng.permutation(len(F))
tr, te = ordre[:120], ordre[120:]
sc = StandardScaler().fit(F.iloc[tr])
Ztr, Zte = sc.transform(F.iloc[tr]), sc.transform(F.iloc[te])
ytr, yte = yv[tr], yv[te]
print("entraînement :", len(tr), "clients | test :", len(te), "clients")
```
<!--sortie-->
```text
nombre de variables candidates : 35 | dont du pur bruit : 20 | clients : 1076
entraînement : 120 clients | test : 956 clients
```

Entraînons cinq modèles : les **moindres carrés avec les 35 variables**, un modèle de **référence** qui ne contient que les vraies variables (inaccessible en pratique, puisqu'on ne sait pas lesquelles sont vraies), puis **Ridge**, **Lasso** et **Elastic Net** avec $\lambda$ choisi par validation croisée à 10 paquets sur l'échantillon d'entraînement.

```python
def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))

noms = list(F.columns)
idx_signal = [noms.index(v) for v in signal]
modeles = {}
modeles["MCO, 35 variables"] = LinearRegression().fit(Ztr, ytr)
ref = LinearRegression().fit(Ztr[:, idx_signal], ytr)
ridge = RidgeCV(alphas=np.logspace(-1, 3.5, 60), cv=10).fit(Ztr, ytr)
lasso = LassoCV(alphas=100, cv=10, random_state=0, max_iter=100000).fit(Ztr, ytr)
enet = ElasticNetCV(l1_ratio=[0.2, 0.5, 0.8, 0.95], alphas=60, cv=10, random_state=0, max_iter=100000).fit(Ztr, ytr)
modeles.update({"Ridge (λ par CV)": ridge, "Lasso (α par CV)": lasso, "Elastic Net (CV)": enet})

lignes = [{"modèle": "constante seule", "RMSE apprentissage": rmse(ytr, np.full(len(ytr), ytr.mean())), "RMSE test": rmse(yte, np.full(len(yte), ytr.mean())),
           "variables non nulles": 0, "dont bruit": 0}]
lignes.append({"modèle": "référence : 4 vraies variables", "RMSE apprentissage": rmse(ytr, ref.predict(Ztr[:, idx_signal])),
               "RMSE test": rmse(yte, ref.predict(Zte[:, idx_signal])), "variables non nulles": 4, "dont bruit": 0})
for nom, m in modeles.items():
    coef = m.coef_
    non_nuls = np.abs(coef) > 1e-10
    lignes.append({"modèle": nom, "RMSE apprentissage": rmse(ytr, m.predict(Ztr)), "RMSE test": rmse(yte, m.predict(Zte)),
                   "variables non nulles": int(non_nuls.sum()), "dont bruit": int(sum(non_nuls[i] for i, n in enumerate(noms) if n.startswith("bruit")))})
res = pd.DataFrame(lignes).set_index("modèle")
print(res.round(4).to_string())
print()
print(f"Ridge : lambda choisi = {ridge.alpha_:.1f} | Lasso : alpha choisi = {lasso.alpha_:.4f} | Elastic Net : alpha = {enet.alpha_:.4f}, rho = {enet.l1_ratio_}")
```
<!--sortie-->
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

Regardons les coefficients retenus par le Lasso, comparés à ceux des moindres carrés :

```python
coef = pd.DataFrame({"MCO": modeles["MCO, 35 variables"].coef_, "Ridge": ridge.coef_, "Lasso": lasso.coef_, "Elastic Net": enet.coef_}, index=noms)
vus = coef[(coef["Lasso"].abs() > 1e-10) | coef.index.isin(signal)]
print("coefficients (variables standardisées) pour les variables retenues par le Lasso ou vraiment utiles :")
print(vus.round(3).to_string())
print()
print("variables de bruit : plus grand |coefficient| MCO =", round(coef.loc[coef.index.str.startswith("bruit"), "MCO"].abs().max(), 3),
      "| Ridge =", round(coef.loc[coef.index.str.startswith("bruit"), "Ridge"].abs().max(), 3),
      "| Lasso =", round(coef.loc[coef.index.str.startswith("bruit"), "Lasso"].abs().max(), 3))
```
<!--sortie-->
```text
coefficients (variables standardisées) pour les variables retenues par le Lasso ou vraiment utiles :
                   MCO  Ridge  Lasso  Elastic Net
age              0.165  0.033  0.050        0.050
age_carre        0.052  0.015  0.011        0.010
canal_Site      -0.174 -0.033 -0.091       -0.090
canal_Instagram -0.218 -0.056 -0.132       -0.131
score_produit    0.106  0.053  0.096        0.095
age_x_Instagram -0.005  0.022  0.026        0.026
ville_Sousse    -0.067 -0.021 -0.013       -0.013
ville_Tunis     -0.037  0.013  0.004        0.003
bruit_01         0.073  0.024  0.025        0.024
bruit_02         0.060  0.012  0.013        0.012
bruit_11        -0.034 -0.016 -0.005       -0.004
bruit_13        -0.052 -0.013 -0.004       -0.003
bruit_14         0.020  0.020  0.021        0.021
bruit_19         0.013  0.015  0.004        0.003
bruit_20        -0.054 -0.021 -0.014       -0.014

variables de bruit : plus grand |coefficient| MCO = 0.073 | Ridge = 0.024 | Lasso = 0.025
```

Le Lasso retient **les quatre vraies variables** (âge, Site, Instagram, score produit), avec des coefficients de 0,05 à 0,13 en valeur absolue, et laisse passer 7 variables de bruit dont les coefficients sont **au plus 0,025**, c'est-à-dire plus de deux fois plus petits que le plus petit coefficient d'une vraie variable : l'ordre de grandeur permet de les distinguer. Avec les moindres carrés, au contraire, les variables de bruit atteignent 0,073, un coefficient du même ordre que celui du score produit (0,106) : on ne peut plus faire la différence. Remarquez aussi que les coefficients MCO des vraies variables sont **gonflés** par rapport à ceux du Lasso (l'âge : 0,165 contre 0,050) : c'est le **biais de sélection** vu au 1.4.5, qui joue ici à l'envers, puisque la régularisation le contrôle.

**Les chemins de régularisation.** Pour voir la régularisation à l'œuvre, on trace comment chaque coefficient évolue quand la pénalité varie, de très forte (tous les coefficients à 0) à très faible (on retrouve les moindres carrés).

```python
alphas_l, coefs_l, _ = lasso_path(Ztr, ytr - ytr.mean(), alphas=80)
alphas_r = np.logspace(-1, 4, 80)
coefs_r = np.array([np.linalg.solve(Ztr.T @ Ztr + a * np.eye(Ztr.shape[1]), Ztr.T @ (ytr - ytr.mean())) for a in alphas_r]).T
couleurs = {"age": VIOLET, "canal_Site": AQUA, "canal_Instagram": ORANGE, "score_produit": BLEU}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
for ax, al, cf, titre, choisi in [(ax1, alphas_r, coefs_r, "Ridge", ridge.alpha_), (ax2, alphas_l, coefs_l, "Lasso", lasso.alpha_)]:
    for i, nom in enumerate(noms):
        if nom in couleurs:
            continue
        ax.plot(np.log10(al), cf[i], color=GRIS, lw=0.7, alpha=0.55)
    for i, nom in enumerate(noms):
        if nom in couleurs:
            ax.plot(np.log10(al), cf[i], color=couleurs[nom], lw=2.2, label=nom)
    ax.axvline(np.log10(choisi), color=ENCRE, ls="--", lw=1)
    ax.text(np.log10(choisi), ax.get_ylim()[1] * 0.92, " choisi par\n validation croisée", fontsize=8.5, va="top")
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.set_xlabel("pénalité : log10(λ)" if titre == "Ridge" else "pénalité : log10(α)")
    ax.set_title(titre + " : coefficients (variables standardisées)", fontsize=10.5)
ax1.set_ylabel("valeur du coefficient")
ax1.legend(frameon=False, fontsize=8.5, loc="lower left")
ax1.invert_xaxis(); ax2.invert_xaxis()
plt.tight_layout()
plt.savefig("figures/ch01-chemins-regularisation.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Chemins de régularisation (à gauche : Ridge ; à droite : Lasso). Les coefficients des quatre vraies variables sont en couleur, ceux des 31 autres variables en gris. Plus on va vers la droite (pénalité faible), plus les coefficients grossissent. Le Lasso met à zéro les coefficients un par un ; Ridge les rétrécit tous ensemble sans jamais les annuler. La ligne pointillée marque la pénalité choisie par validation croisée.](figures/ch01-chemins-regularisation.png)

Sur la gauche de chaque graphique, la pénalité est énorme et tous les coefficients valent 0 ; en allant vers la droite, la pénalité se relâche et les coefficients se déploient. Avec le Lasso, les variables **entrent une par une** dans le modèle, à peu près dans l'ordre de leur pouvoir prédictif : le score produit, l'âge et Instagram apparaissent en premier ; le Site, dont l'effet est pourtant réel, n'apparaît qu'à peu près en même temps que les premières variables de bruit (il est partiellement redondant avec Instagram, comme on l'a vu avec Ridge) ; les variables de bruit entrent avec de petits coefficients. À la valeur choisie par validation croisée (pointillés), on est dans la zone où le signal est capté et où la plus grande partie du bruit est encore écartée. Avec Ridge, tous les coefficients se rétrécissent **ensemble** : le bruit n'est pas éliminé, seulement atténué.

### 1.5.5 Précautions

- **Standardisez toujours** les variables (et estimez la moyenne et l'écart-type sur l'échantillon d'**entraînement** seulement, jamais sur les données de test : sinon on laisse fuir de l'information du test dans le modèle).
- Choisissez $\lambda$ **par validation croisée** sur l'entraînement ; ne regardez l'échantillon de test qu'à la fin.
- Les coefficients régularisés sont **biaisés** par construction : on ne les interprète pas comme des effets (« à toutes choses égales par ailleurs ») avec la même confiance. Il n'y a pas de p-valeurs ni d'intervalles de confiance « standard » : les formules du 1.2 ne s'appliquent plus, et la sélection par le Lasso soulève précisément le problème de l'inférence **après sélection** discuté au 1.4.5.
- La régularisation vise la **prédiction**. Pour estimer un effet précis et le décrire à Yasmine, on revient en général à un modèle plus simple et interprétable, éventuellement **choisi** avec l'aide du Lasso, mais **réajusté** sur de nouvelles données.
- **Lien avec le bayésien (chapitre 6).** Ridge équivaut à une approche bayésienne où chaque coefficient a une loi *a priori* **normale** centrée en 0 (le coefficient est « probablement petit »), et le Lasso à une loi *a priori* de **Laplace** (plus piquée en 0, d'où les zéros). La section 6.1 reprendra cette interprétation : $\lambda$ y correspond au rapport entre la variance du bruit et celle de l'*a priori*.

> ✅ **À retenir (1.5).**
> - Ridge : $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y$ ; il **rétrécit** les directions peu variables ($d_j^2/(d_j^2+\lambda)$), est toujours défini et réduit la variance au prix d'un **biais** : l'EQM s'améliore pour un $\lambda$ petit (et optimal en $\sigma^2/\beta^2$ dans le cas orthonormal).
> - Lasso : pénalité $\sum|\beta_j|$ ; il produit des solutions **creuses** (seuillage doux, descente par coordonnées) et sert de **sélection de variables**. Elastic Net : mélange des deux, stable pour les variables corrélées.
> - Standardiser, ne pas pénaliser la constante, choisir $\lambda$ par validation croisée, évaluer sur des données de test non utilisées.
> - Beaucoup de variables pour peu de données : les moindres carrés surajustent (ici, pire que la simple constante) ; la régularisation rejoint la prédiction du meilleur modèle possible. Mais ses coefficients ne s'interprètent pas comme ceux d'un modèle ordinaire.


## 1.6 ➕ Pour aller plus loin : la régression robuste

> 🧭 **Section optionnelle.** Elle prolonge la discussion des observations aberrantes et influentes de 1.3.4 et s'appuie sur l'idée, vue au volume I (section 3.1.3), que la médiane est plus robuste que la moyenne.

> 💡 **Intuition.** Les moindres carrés élèvent chaque écart **au carré** : un client dont le panier est dix fois trop grand (une virgule mal placée dans un export) pèse **cent fois** plus qu'un client ordinaire. Quelques erreurs de saisie peuvent suffire à fausser tout le modèle. La régression **robuste** limite l'influence des points extrêmes : elle cherche la droite qui colle à **la majorité** des données, sans se laisser tirer par quelques cas isolés. Elle fait pour la régression ce que la médiane fait pour la moyenne.

Voici la préparation habituelle :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
m_propre = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
print(len(df), "clients | coefficients du modèle sur les données propres :")
print(m_propre.params.round(4).to_string())
```
<!--sortie-->
```text
1740 clients | coefficients du modèle sur les données propres :
Intercept                4.2206
C(canal)[T.Site]        -0.1571
C(canal)[T.Instagram]   -0.3368
a                        0.0092
```

### 1.6.1 La fragilité des moindres carrés

Reprenons l'exemple du volume I (3.1.3) : cinq commandes de 20, 25, 30, 35 et 400 DT. La **moyenne** (102 DT) est entraînée par la dernière valeur ; la **médiane** (30 DT) ne bouge pas. On dit que la médiane a un **point de rupture** de 50 % (il faut corrompre la moitié des données pour la faire dériver à l'infini) alors que celui de la moyenne est de **0 %** (une seule valeur suffit). Les moindres carrés, qui généralisent la moyenne, héritent de cette fragilité.

> 📐 **Pourquoi ? La fonction d'influence.** Un estimateur $\hat\theta$ minimise $\sum_i\rho(e_i)$. Son équation d'estimation est $\sum_i\psi(e_i)\,\mathbf x_i=\mathbf 0$ où $\psi=\rho'$ (comme les équations normales du 1.1.3, qui correspondent à $\rho(e)=e^2/2$ et $\psi(e)=e$). La fonction $\psi$ mesure **l'influence** d'un résidu sur l'estimation. Pour les moindres carrés, $\psi(e)=e$ n'est **pas bornée** : plus un point est extrême, plus il tire. Un estimateur robuste choisit un $\rho$ dont la dérivée $\psi$ est **bornée** : au-delà d'un seuil, un résidu de plus en plus grand n'a pas plus d'influence.

### 1.6.2 Les M-estimateurs et la fonction de Huber

La fonction de **Huber** est quadratique pour les petits résidus (comme les moindres carrés : efficace quand tout va bien) et **linéaire** pour les grands (comme la valeur absolue : l'influence est plafonnée). Avec un seuil $c$ (en unités d'écart-type du résidu) :

$$\rho_c(u)=\begin{cases}\tfrac12u^2&\text{si }|u|\le c\\ c|u|-\tfrac12c^2&\text{si }|u|>c\end{cases}\qquad\psi_c(u)=\begin{cases}u&\text{si }|u|\le c\\ c\,\operatorname{signe}(u)&\text{si }|u|>c\end{cases}\qquad u=\frac{e}{s}$$

où $s$ est une estimation **robuste** de l'échelle des résidus : on prend le **MAD** (écart absolu médian) : $s=\operatorname{médiane}(|e_i-\operatorname{médiane}(e)|)/0{,}6745$ (le facteur 0,6745 rend $s$ cohérent avec l'écart-type pour des erreurs normales). Le seuil usuel $c=1{,}345$ garantit que, **si les erreurs sont réellement normales**, l'estimateur de Huber conserve **95 % de l'efficacité** des moindres carrés : on perd très peu quand tout va bien, et on gagne beaucoup quand il y a des aberrations.

**L'algorithme : les moindres carrés repondérés (IRLS).** Les équations d'estimation $\sum_i\psi(u_i)\mathbf x_i=\mathbf 0$ s'écrivent $\sum_iw_iu_i\mathbf x_i=\mathbf 0$ avec les **poids** $w_i=\psi(u_i)/u_i$ : une régression **pondérée**. Pour Huber, $w_i=1$ si $|u_i|\le c$ et $w_i=c/|u_i|$ sinon : chaque point reçoit un poids d'autant plus petit qu'il est loin de la droite. Comme les poids dépendent des résidus qui dépendent de $\boldsymbol\beta$, on **itère** : (1) calculer les résidus, (2) en déduire les poids, (3) refaire une régression pondérée, jusqu'à stabilisation.

Dessinons les fonctions de perte et de poids de trois méthodes : les moindres carrés, Huber, et la fonction « bisquare » de Tukey (plus radicale : les points très éloignés reçoivent un poids **nul**).

```python
u = np.linspace(-6, 6, 400)
c_h, c_t = 1.345, 4.685
rho_mco = u**2 / 2
rho_huber = np.where(np.abs(u) <= c_h, u**2 / 2, c_h * np.abs(u) - c_h**2 / 2)
rho_tukey = np.where(np.abs(u) <= c_t, c_t**2 / 6 * (1 - (1 - (u / c_t)**2)**3), c_t**2 / 6)
w_mco = np.ones_like(u)
w_huber = np.where(np.abs(u) <= c_h, 1.0, c_h / np.abs(u))
w_tukey = np.where(np.abs(u) <= c_t, (1 - (u / c_t)**2)**2, 0.0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for rho, nom, col in [(rho_mco, "moindres carrés", GRIS), (rho_huber, "Huber (c = 1,345)", BLEU), (rho_tukey, "Tukey bisquare (c = 4,685)", ORANGE)]:
    ax1.plot(u, rho, color=col, lw=2.2, label=nom)
ax1.set_ylim(0, 9); ax1.set_xlabel("résidu standardisé u"); ax1.set_ylabel("perte ρ(u)"); ax1.set_title("Perte attribuée à un résidu", fontsize=10.5)
ax1.legend(frameon=False, loc="upper center", fontsize=9)
for w, col, nom in [(w_mco, GRIS, "moindres carrés : poids constant égal à 1"), (w_huber, BLEU, "Huber : poids c/|u| au-delà de 1,345"), (w_tukey, ORANGE, "Tukey : poids nul au-delà de 4,685")]:
    ax2.plot(u, w, color=col, lw=2.2, label=nom)
ax2.set_ylim(-0.05, 1.15); ax2.set_xlabel("résidu standardisé u"); ax2.set_ylabel("poids w(u)"); ax2.set_title("Poids donné à l'observation", fontsize=10.5)
ax2.legend(frameon=False, loc="lower center", fontsize=8.5, bbox_to_anchor=(0.5, 0.08))
plt.tight_layout()
plt.savefig("figures/ch01-fonctions-robustes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Fonctions de perte (à gauche) et poids (à droite). Les moindres carrés (gris) pénalisent quadratiquement et donnent le même poids à tous. Huber (bleu) devient linéaire au-delà de 1,345 écart-type. Tukey (orange) plafonne la perte et annule le poids des points très éloignés.](figures/ch01-fonctions-robustes.png)

Écrivons l'algorithme IRLS à la main et comparons à `statsmodels` (`RLM`, *robust linear model*) sur les données propres :

```python
def huber_irls(X, y, c=1.345, n_iter=100, tol=1e-10):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]                  # départ : les moindres carrés
    for _ in range(n_iter):
        e = y - X @ beta
        s = np.median(np.abs(e - np.median(e))) / 0.6745        # échelle robuste (MAD)
        u = e / s
        w = np.where(np.abs(u) <= c, 1.0, c / np.abs(u))        # poids de Huber
        W = X.T * w                                              # X' diag(w)
        beta_new = np.linalg.solve(W @ X, W @ y)                 # régression pondérée
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta, w, s

Xp, yp = m_propre.model.exog, m_propre.model.endog
b_main, w_main, s_main = huber_irls(Xp, yp)
rlm = sm.RLM(yp, Xp, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO": m_propre.params, "Huber (à la main)": b_main, "RLM statsmodels": rlm.params}).round(4).to_string())
print(f"échelle robuste s : {s_main:.4f} | écart-type résiduel des MCO : {np.sqrt(m_propre.scale):.4f}")
print(f"part des clients dont le poids est inférieur à 1 : {np.mean(w_main < 1):.1%}")
```
<!--sortie-->
```text
                          MCO  Huber (à la main)  RLM statsmodels
Intercept              4.2206             4.2171           4.2172
C(canal)[T.Site]      -0.1571            -0.1602          -0.1602
C(canal)[T.Instagram] -0.3368            -0.3331          -0.3332
a                      0.0092             0.0090           0.0090
échelle robuste s : 0.3667 | écart-type résiduel des MCO : 0.3705
part des clients dont le poids est inférieur à 1 : 18.1%
```

Sur des données **propres**, Huber et les moindres carrés donnent presque les mêmes coefficients : c'est l'efficacité de 95 % en action : on ne paie quasiment rien pour la robustesse. (L'écart minime, de l'ordre de $10^{-4}$, entre notre version et `RLM` tient à des choix de détail sur l'estimation de l'échelle.) Remarquez aussi que **18 % des clients reçoivent un poids inférieur à 1 même sur ces données propres** : ce n'est pas un signe d'anomalie, c'est exactement la proportion attendue pour des erreurs normales, puisque $\mathbb P(|Z|>1{,}345)\approx17{,}9\,\%$. Huber n'écarte pas 18 % des données : il en réduit un peu le poids.

### 1.6.3 Une contamination : les erreurs de saisie

Corrompons maintenant les données, comme le ferait un export mal formaté. Dans **6 %** des clients tirés au hasard, la virgule du panier est mal placée : le panier est **multiplié par 10** (54 DT devient 540 DT). Nous gardons la version propre (`df`) et fabriquons une copie contaminée (`dfc`).

```python
rng = np.random.default_rng(77)
dfc = df.copy()
cible = rng.choice(len(df), size=int(0.06 * len(df)), replace=False)       # 6 % de clients touchés
dfc.loc[cible, "panier_moyen"] = dfc.loc[cible, "panier_moyen"] * 10
dfc["log_panier"] = np.log(dfc["panier_moyen"])
contamine = np.zeros(len(df), dtype=bool); contamine[cible] = True
print(len(cible), "paniers corrompus sur", len(df), f"({contamine.mean():.1%})")

m_mco_c = smf.ols("log_panier ~ a + C(canal)", data=dfc).fit()
rlm_c = smf.rlm("log_panier ~ a + C(canal)", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
tab = pd.DataFrame({"MCO données propres": m_propre.params, "MCO contaminé": m_mco_c.params, "Huber contaminé": rlm_c.params})
tab_se = pd.DataFrame({"MCO données propres": m_propre.bse, "MCO contaminé": m_mco_c.bse, "Huber contaminé": rlm_c.bse})
print("Coefficients :"); print(tab.round(4).to_string())
print("\nErreurs standard :"); print(tab_se.round(4).to_string())
print(f"\nécart-type résiduel : MCO propre = {np.sqrt(m_propre.scale):.3f} | MCO contaminé = {np.sqrt(m_mco_c.scale):.3f} | échelle robuste de Huber = {rlm_c.scale:.3f}")
print(f"panier médian prédit pour un client Boutique de 36 ans : propre = {np.exp(m_propre.params['Intercept']):.1f} DT | MCO contaminé = {np.exp(m_mco_c.params['Intercept']):.1f} DT | Huber contaminé = {np.exp(rlm_c.params['Intercept']):.1f} DT")
poids = rlm_c.weights
print(f"poids de Huber moyen : clients corrompus = {poids[contamine].mean():.2f} | clients intacts = {poids[~contamine].mean():.2f}")
```
<!--sortie-->
```text
104 paniers corrompus sur 1740 (6.0%)
Coefficients :
                       MCO données propres  MCO contaminé  Huber contaminé
Intercept                           4.2206         4.3898           4.2628
C(canal)[T.Site]                   -0.1571        -0.1853          -0.1573
C(canal)[T.Instagram]              -0.3368        -0.3919          -0.3527
a                                   0.0092         0.0088           0.0091

Erreurs standard :
                       MCO données propres  MCO contaminé  Huber contaminé
Intercept                           0.0175         0.0314           0.0201
C(canal)[T.Site]                    0.0231         0.0414           0.0265
C(canal)[T.Instagram]               0.0225         0.0403           0.0258
a                                   0.0008         0.0015           0.0010

écart-type résiduel : MCO propre = 0.370 | MCO contaminé = 0.665 | échelle robuste de Huber = 0.402
panier médian prédit pour un client Boutique de 36 ans : propre = 68.1 DT | MCO contaminé = 80.6 DT | Huber contaminé = 71.0 DT
poids de Huber moyen : clients corrompus = 0.24 | clients intacts = 0.97
```

Les conséquences pour les moindres carrés sont de deux types. (1) Un **biais** : la constante est tirée vers le haut (de 4,22 à 4,39, soit +18 % sur le panier médian prédit : 80,6 DT au lieu de 68,1 DT ; en moyenne on attendrait $0{,}06\times\ln10\approx0{,}14$, le reste vient de la répartition aléatoire des erreurs entre les canaux), les effets du Site et d'Instagram sont gonflés, et les erreurs standard grossissent ; (2) surtout, l'**écart-type résiduel** passe de 0,37 à 0,665 : les moindres carrés *attribuent à tort un bruit énorme* à tout le modèle, donc des intervalles de confiance beaucoup trop larges, des prévisions moins précises, et des effets réels (le canal, l'âge) qui deviennent plus difficiles à détecter. Huber, lui, **donne un poids faible aux clients corrompus** (0,24 en moyenne, contre 0,97 aux clients intacts) : sa constante (4,26) et son effet d'Instagram (−0,353) restent proches de ceux des données propres (4,22 et −0,337), alors que ceux des moindres carrés dérivent (4,39 et −0,392) ; son échelle (0,40) est proche de l'écart-type propre (0,37) alors que celui des moindres carrés double (0,665). Ses erreurs standard (0,020 pour la constante) sont proches de celles des données propres (0,017) et loin de celles des moindres carrés contaminés (0,031).

Visualisons-le sur un modèle simple (le log-panier selon l'âge seul, pour pouvoir tracer les droites) :

```python
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(dfc.loc[~contamine, "age"], dfc.loc[~contamine, "log_panier"], s=7, color=GRIS, alpha=0.5, label="paniers corrects")
ax.scatter(dfc.loc[contamine, "age"], dfc.loc[contamine, "log_panier"], s=14, color=ROUGE, alpha=0.8, label="paniers corrompus (× 10)")
s1 = smf.ols("log_panier ~ a", data=df).fit()
s2 = smf.ols("log_panier ~ a", data=dfc).fit()
s3 = smf.rlm("log_panier ~ a", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
xa = np.linspace(18, 75, 50)
for m, col, nom, ls in [(s1, ENCRE, "MCO, données propres", "-"), (s2, ORANGE, "MCO, données contaminées", "-"), (s3, BLEU, "Huber, données contaminées", "--")]:
    ax.plot(xa, m.params["Intercept"] + m.params["a"] * (xa - 36), color=col, lw=2.2, ls=ls, label=nom)
ax.set_xlabel("âge (ans)"); ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, fontsize=8.5, loc="lower right", ncol=2)
ax.set_ylim(1.5, 7.6)
plt.savefig("figures/ch01-robuste-contamination.png", dpi=200, bbox_inches="tight")
print("pente (MCO propre) =", round(s1.params["a"], 4), "| (MCO contaminé) =", round(s2.params["a"], 4), "| (Huber contaminé) =", round(s3.params["a"], 4))
print("constante (MCO propre) =", round(s1.params["Intercept"], 3), "| (MCO contaminé) =", round(s2.params["Intercept"], 3), "| (Huber contaminé) =", round(s3.params["Intercept"], 3))
```
<!--sortie-->
```text
pente (MCO propre) = 0.009 | (MCO contaminé) = 0.0086 | (Huber contaminé) = 0.0092
constante (MCO propre) = 4.033 | (MCO contaminé) = 4.171 | (Huber contaminé) = 4.07
```

![Nuage du log-panier selon l'âge, avec 6 % de paniers corrompus (rouge, environ 2,3 plus haut). La droite des moindres carrés sur les données contaminées (orange) est décalée vers le haut par rapport à la droite sur données propres (noire) ; la droite de Huber sur les mêmes données contaminées (bleu pointillé) reste beaucoup plus proche de la droite propre.](figures/ch01-robuste-contamination.png)

Les points rouges forment une bande décalée d'environ $\ln10\approx2{,}3$ au-dessus du nuage principal. La droite des moindres carrés (orange) est visiblement tirée vers le haut ; celle de Huber (bleu pointillé) reste beaucoup plus proche de la droite que l'on obtiendrait sans contamination (noire) : la constante passe de 4,03 (données propres) à 4,17 pour les moindres carrés mais seulement à 4,07 pour Huber, et la pente est presque intacte (0,0092 pour Huber, 0,0086 pour les moindres carrés, 0,0090 sans contamination). Huber n'est pas totalement insensible (les points corrompus gardent un petit poids, 0,24 en moyenne), mais l'essentiel du dégât est évité.

### 1.6.4 La limite : les points à fort levier

Les M-estimateurs de Huber protègent contre les **valeurs aberrantes de la réponse** $y$ (les « aberrations verticales »), mais **pas contre les points à fort levier** (valeurs aberrantes des *variables explicatives*, 1.3.4). Leur fonction $\psi$ borne l'influence du résidu, mais pas celle de la position $\mathbf x_i$ : un point très éloigné en $x$ attire la droite, et se retrouve avec un résidu qui n'a pas l'air grand. Faisons une seconde contamination : cette fois, ce sont des **âges** mal saisis. Pour 1 % des clients, l'âge est écrit avec un chiffre de trop (35 devient 350).

```python
rng = np.random.default_rng(78)
dfl = df.copy()
cible_l = rng.choice(len(df), size=int(0.01 * len(df)), replace=False)
dfl.loc[cible_l, "age"] = dfl.loc[cible_l, "age"] * 10
dfl["a"] = dfl["age"] - 36
print(len(cible_l), "âges corrompus ; âge maximal après contamination :", int(dfl["age"].max()), "ans")
m_mco_l = smf.ols("log_panier ~ a + C(canal)", data=dfl).fit()
rlm_l = smf.rlm("log_panier ~ a + C(canal)", data=dfl, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO propre": m_propre.params, "MCO âges corrompus": m_mco_l.params, "Huber âges corrompus": rlm_l.params}).round(4).to_string())
print(f"coefficient de l'âge : propre = {m_propre.params['a']:.4f} | MCO corrompu = {m_mco_l.params['a']:.4f} | Huber corrompu = {rlm_l.params['a']:.4f}")
print(f"levier maximal : {m_mco_l.get_influence().hat_matrix_diag.max():.3f} (levier moyen = {4/len(dfl):.4f})")
```
<!--sortie-->
```text
17 âges corrompus ; âge maximal après contamination : 640 ans
                       MCO propre  MCO âges corrompus  Huber âges corrompus
Intercept                  4.2206              4.2156                4.2126
C(canal)[T.Site]          -0.1571             -0.1575               -0.1603
C(canal)[T.Instagram]     -0.3368             -0.3349               -0.3338
a                          0.0092              0.0008                0.0009
coefficient de l'âge : propre = 0.0092 | MCO corrompu = 0.0008 | Huber corrompu = 0.0009
levier maximal : 0.126 (levier moyen = 0.0023)
```

Les deux méthodes sont mises en échec : le coefficient de l'âge est **écrasé vers 0** (par les moindres carrés comme par Huber), parce que ces 17 clients, supposés avoir jusqu'à 640 ans, ont un panier ordinaire : sur ces points, la droite « âge ↗, panier ↗ » est contredite, et leur très fort levier leur donne le pouvoir de l'aplatir. Les estimateurs robustes **à fort levier** (MM-estimateurs, moindres carrés tronqués) existent, mais dans ce cas la bonne réponse est plus simple : **vérifier les données**. Un âge de 350 ans est **impossible** : une règle de validation élémentaire (`age <= 100`) l'élimine.

> ⚠️ **Robuste ne veut pas dire infaillible.** (1) Une méthode robuste ne remplace pas la **vérification des données** : un âge de 350 ans doit être détecté et corrigé, pas « absorbé » par un estimateur. (2) Les méthodes robustes protègent contre un certain **type** d'anomalie (ici, les erreurs sur $y$) et pas contre tous. (3) Elles sont moins efficaces que les moindres carrés si les données sont parfaitement propres (un peu : 5 % pour Huber). (4) Leurs erreurs standard demandent des formules spécifiques ; `RLM` les fournit, mais leurs propriétés sont asymptotiques. (5) Si les « aberrations » sont **réelles** (quelques très gros clients), il ne faut pas les cacher : il faut **les étudier**, car elles peuvent être ce qu'il y a de plus important commercialement.

### 1.6.5 Une autre voie : la régression quantile

Une approche voisine consiste à modéliser non plus la **moyenne** conditionnelle mais la **médiane** conditionnelle, en minimisant la **somme des valeurs absolues** des résidus (perte $\rho(e)=|e|$, dont l'influence $\psi=\operatorname{signe}(e)$ est bornée) : c'est la **régression médiane** (LAD, *least absolute deviations*), robuste aux aberrations verticales. Elle se généralise à un **quantile** quelconque $\tau\in(0,1)$ avec la perte asymétrique $\rho_\tau(e)=e\,(\tau-\mathbb 1_{e<0})$ : on modélise alors le $\tau$-ième quantile de la réponse, ce qui décrit **toute la distribution** et non son seul centre.

Voyons-le sur les paniers. Dans le modèle en **dinars**, que dit le canal Instagram sur les paniers faibles, moyens et élevés ? Et dans le modèle en **log** ?

```python
taus = [0.1, 0.25, 0.5, 0.75, 0.9]
res_niveau, res_log = [], []
for tau in taus:
    qn = smf.quantreg("panier_moyen ~ a + C(canal)", data=df).fit(q=tau)
    ql = smf.quantreg("log_panier ~ a + C(canal)", data=df).fit(q=tau)
    res_niveau.append((tau, qn.params["C(canal)[T.Instagram]"], *qn.conf_int().loc["C(canal)[T.Instagram]"]))
    res_log.append((tau, ql.params["C(canal)[T.Instagram]"], *ql.conf_int().loc["C(canal)[T.Instagram]"]))
rn = pd.DataFrame(res_niveau, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
rl = pd.DataFrame(res_log, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
mco_n = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()
print("Effet d'Instagram (par rapport à la Boutique) sur le panier en DT, par quantile :")
print(rn.round(2).to_string())
print(f"(MCO, effet sur la moyenne : {mco_n.params['C(canal)[T.Instagram]']:.2f} DT)")
print("\nEffet d'Instagram sur le log du panier, par quantile :")
print(rl.round(3).to_string())
print(f"(MCO, effet sur la moyenne du log : {m_propre.params['C(canal)[T.Instagram]']:.3f})")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for ax, r, ref, titre, yl in [(ax1, rn, mco_n.params["C(canal)[T.Instagram]"], "Panier en DT", "effet d'Instagram (DT)"),
                              (ax2, rl, m_propre.params["C(canal)[T.Instagram]"], "Log du panier", "effet d'Instagram (log)")]:
    ax.fill_between(r.index, r["bas"], r["haut"], color=BLEU, alpha=0.2)
    ax.plot(r.index, r["coef"], "o-", color=BLEU, lw=2, label="régression quantile")
    ax.axhline(ref, color=ORANGE, lw=1.8, ls="--", label="moindres carrés (moyenne)")
    ax.set_xlabel("quantile τ du panier (0,1 = petits paniers ; 0,9 = grands paniers)"); ax.set_ylabel(yl); ax.set_title(titre, fontsize=10.5)
ax1.legend(frameon=False, fontsize=8.5, loc="lower left")
plt.tight_layout()
plt.savefig("figures/ch01-regression-quantile.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Effet d'Instagram (par rapport à la Boutique) sur le panier en DT, par quantile :
       coef    bas   haut
tau                      
0.10 -13.50 -16.18 -10.82
0.25 -14.40 -16.92 -11.89
0.50 -18.27 -21.44 -15.09
0.75 -24.22 -28.42 -20.02
0.90 -33.87 -40.70 -27.04
(MCO, effet sur la moyenne : -20.81 DT)

Effet d'Instagram sur le log du panier, par quantile :
       coef    bas   haut
tau                      
0.10 -0.373 -0.448 -0.298
0.25 -0.331 -0.387 -0.275
0.50 -0.310 -0.369 -0.252
0.75 -0.339 -0.400 -0.278
0.90 -0.372 -0.446 -0.299
(MCO, effet sur la moyenne du log : -0.337)
figure enregistrée
```

![Effet du canal Instagram selon le quantile du panier. À gauche (en dinars) : l'effet est faible pour les petits paniers et de plus en plus négatif pour les grands. À droite (en log) : l'effet est à peu près constant, autour de −0,34, avec une bande de confiance qui contient la valeur des moindres carrés. Les bandes bleues sont les intervalles de confiance à 95 %.](figures/ch01-regression-quantile.png)

Lisons la figure. En **dinars** (à gauche), l'effet d'Instagram n'est pas le même sur les petits et les grands paniers : le déficit est de 13,5 DT pour les petits paniers (quantile 10 %) et de 33,9 DT pour les gros (quantile 90 %), à comparer aux 20,8 DT de l'effet moyen des moindres carrés. La moyenne (moindres carrés) ne voit qu'un effet moyen. En **log** (à droite), l'effet varie peu le long de la distribution (de −0,31 à −0,37, des intervalles de confiance qui se chevauchent largement et contiennent la valeur des moindres carrés, −0,337) : on peut le considérer comme **constant**. Les deux lectures sont **cohérentes** : un effet **multiplicatif** constant ($-29$ % du panier, quel que soit son niveau) se traduit en dinars par un effet **proportionnel** au niveau (un gros panier perd plus de dinars qu'un petit). C'est exactement ce que le modèle simulé a programmé, et c'est une raison de plus de préférer le log : l'effet s'y résume par un **seul nombre**.

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

Dar Jasmin livre en partie via **30 points relais** (commerces partenaires où les clients viennent retirer leur colis). Pour chaque commande retirée, on dispose du **délai de livraison** (de 1 à 10 jours) et de la **note de satisfaction** (sur 20). Les relais sont de tailles très inégales (certains ont reçu 4 commandes, d'autres près de 60), et certains sont en zone **urbaine**. Les données sont simulées (graine fixe) selon un modèle que nous connaîtrons, comme d'habitude :

$$\text{note}_{ij}=12+1{,}2\,\text{urbain}_j+u_{0j}+(-0{,}7+u_{1j})(\text{délai}_{ij}-5)+\varepsilon_{ij},$$

où $i$ numérote les commandes du relais $j$, $u_{0j}\sim\mathcal N(0,1{,}6^2)$ est le **niveau de base propre au relais** (« certains relais notent plus généreusement »), $u_{1j}\sim\mathcal N(0,0{,}3^2)$ la **sensibilité propre au retard** de ce relais, et $\varepsilon_{ij}\sim\mathcal N(0,1{,}8^2)$ le bruit.

```python
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

# Simulation des 30 points relais (graine fixe)
rng = np.random.default_rng(41)
J = 30
tailles = np.clip(np.round(rng.lognormal(np.log(12), 0.8, J)), 3, 60).astype(int)    # commandes par relais (très inégal)
urbain = (rng.random(J) < 0.5).astype(int)
u0 = rng.normal(0, 1.6, J)                                                           # vrai niveau de base de chaque relais
u1 = rng.normal(0, 0.3, J)                                                           # vraie sensibilité au retard de chaque relais
lignes = []
for j in range(J):
    delai = rng.integers(1, 11, tailles[j])
    note = 12 + 1.2 * urbain[j] + u0[j] + (-0.7 + u1[j]) * (delai - 5) + rng.normal(0, 1.8, tailles[j])
    for d, y in zip(delai, note):
        lignes.append((f"R{j + 1:02d}", urbain[j], int(d), round(float(y), 2)))
rel = pd.DataFrame(lignes, columns=["relais", "urbain", "delai", "note"])
rel.to_csv("donnees/ch01-relais.csv", index=False)         # fichier fourni avec le livre (lu aussi par R plus bas)
rel["dc"] = rel["delai"] - 5                                # délai centré : 0 = délai de 5 jours
print(rel.shape, "| relais :", rel["relais"].nunique(), "| relais urbains :", int(urbain.sum()))
print("commandes par relais : min =", tailles.min(), "| médiane =", int(np.median(tailles)), "| max =", tailles.max())
print("écart-type RÉALISÉ des 30 vrais niveaux de base u0 :", round(u0.std(ddof=1), 2), "(la loi dont ils sont tirés a un écart-type de 1,6)")
print(rel.head(5).to_string(index=False))
```
<!--sortie-->
```text
(484, 5) | relais : 30 | relais urbains : 14
commandes par relais : min = 4 | médiane = 11 | max = 58
écart-type RÉALISÉ des 30 vrais niveaux de base u0 : 1.31 (la loi dont ils sont tirés a un écart-type de 1,6)
relais  urbain  delai  note  dc
   R01       0      6 12.57   1
   R01       0      4 11.23  -1
   R01       0      8  4.98   3
   R01       0     10  7.56   5
   R02       1      6  9.91   1
```

Notons déjà un fait important. Les 30 niveaux de base $u_{0j}$ ont été **tirés** d'une loi d'écart-type 1,6, mais avec seulement 30 relais, leur écart-type **réalisé** n'est que de 1,31. Avec peu de groupes, les composantes de variance sont **mal connues** : nous y reviendrons.

### 1.7.2 Trois façons de traiter les groupes

Pour estimer le niveau de base de chaque relais, trois stratégies s'offrent à nous :

1. **Mise en commun totale** (*complete pooling*) : on ignore les groupes (régression ordinaire sur les 484 commandes). On suppose que tous les relais sont identiques.
2. **Pas de mise en commun** (*no pooling*) : on estime chaque relais **séparément** (une indicatrice par relais). On suppose qu'ils n'ont rien en commun.
3. **Mise en commun partielle** (*partial pooling*) : le **modèle mixte**. Chaque relais a son propre niveau, mais ces niveaux sont supposés tirés d'une même loi : l'information d'un relais **aide** à estimer les autres.

Commençons par les deux premières, et regardons les conséquences sur les erreurs standard :

```python
m_commun = smf.ols("note ~ dc + urbain", data=rel).fit()                           # ignore les groupes
m_separe = smf.ols("note ~ dc + C(relais)", data=rel).fit()                         # une indicatrice par relais (urbain y est absorbé)
print("Mise en commun totale (MCO, groupes ignorés) :")
print(pd.DataFrame({"coef": m_commun.params, "erreur standard": m_commun.bse, "IC bas": m_commun.conf_int()[0], "IC haut": m_commun.conf_int()[1]}).round(3).to_string())
print(f"\nrésidu : s = {np.sqrt(m_commun.scale):.2f}")
print("\nPas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).")
print(f"coefficient du délai avec indicatrices de relais : {m_separe.params['dc']:.3f} (erreur standard {m_separe.bse['dc']:.3f})")
```
<!--sortie-->
```text
Mise en commun totale (MCO, groupes ignorés) :
             coef  erreur standard  IC bas  IC haut
Intercept  12.644            0.152  12.345   12.943
dc         -0.721            0.039  -0.796   -0.645
urbain      0.482            0.224   0.043    0.922

résidu : s = 2.44

Pas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).
coefficient du délai avec indicatrices de relais : -0.703 (erreur standard 0.034)
```

> ⚠️ **Le problème de la mise en commun totale.** Les p-valeurs et intervalles de ce premier modèle supposent 484 observations **indépendantes**. Or elles sont groupées en 30 relais. Pour une variable qui ne varie **qu'entre** relais (comme `urbain`), l'information ne vient que de 30 unités, pas de 484 : la mise en commun totale **sous-estime fortement** son incertitude. Nous le démontrons par simulation plus bas (1.7.6).

Le **pas de mise en commun** a l'inconvénient inverse : il ne peut pas estimer l'effet d'une variable de niveau groupe (`urbain`), et il estime très mal le niveau d'un petit relais (4 commandes) : l'estimation est trop bruitée.

### 1.7.3 Le modèle à intercept aléatoire

Le **modèle mixte à intercept aléatoire** s'écrit

$$y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_{j}+\varepsilon_{ij},\qquad u_j\sim\mathcal N(0,\tau^2),\quad\varepsilon_{ij}\sim\mathcal N(0,\sigma^2),$$

les $u_j$ et les $\varepsilon_{ij}$ étant indépendants. Les $\boldsymbol\beta$ sont les **effets fixes** (communs à tous), les $u_j$ des **effets aléatoires**. Deux paramètres de variance : $\tau^2$ (variance **entre** relais) et $\sigma^2$ (variance **à l'intérieur** d'un relais).

> 📐 **Ce que cela implique pour les observations.** Pour deux commandes $i\ne i'$ du **même** relais, $\operatorname{Cov}(y_{ij},y_{i'j})=\operatorname{Var}(u_j)=\tau^2$ : elles sont **corrélées**, avec une corrélation
> $$\rho=\frac{\tau^2}{\tau^2+\sigma^2}\qquad\text{(coefficient de corrélation intraclasse, ICC).}$$
> Pour deux commandes de relais différents, la covariance est nulle. Le vecteur des commandes d'un relais de $n_j$ commandes a donc pour matrice de variance $\mathbf V_j=\sigma^2\mathbf I+\tau^2\mathbf 1\mathbf 1^\top$ (« symétrie composée »). Par conséquent, la **variance de la moyenne** de $n_j$ commandes est $\tau^2+\sigma^2/n_j$, et non $\sigma^2/n_j$ : *il y a un plancher*, $\tau^2$, que l'on ne peut jamais dépasser en ajoutant des commandes dans un même relais. L'**effectif effectif** d'un échantillon de $m$ commandes par groupe est $m/(1+(m-1)\rho)$ (« effet de plan »).

**L'ICC répond à la question « les groupes comptent-ils ? ».** Comparons deux situations. D'abord un cas où la réponse est **non** : les clients de Dar Jasmin sont répartis en six **villes**. Le panier dépend-il de la ville, au-delà de l'âge et du canal ?

```python
clients = pd.read_csv("donnees/clients.csv")
cl = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
cl["canal"] = pd.Categorical(cl["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
cl["a"] = cl["age"] - 36
cl["log_panier"] = np.log(cl["panier_moyen"])
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_ville = smf.mixedlm("log_panier ~ a + C(canal)", cl, groups=cl["ville"]).fit(reml=True)
tau2_v, sigma2_v = m_ville.cov_re.iloc[0, 0], m_ville.scale
print(f"clients groupés par ville : variance entre villes tau² = {tau2_v:.5f} | variance résiduelle sigma² = {sigma2_v:.4f}")
print(f"ICC = tau²/(tau² + sigma²) = {tau2_v / (tau2_v + sigma2_v):.4f}")
```
<!--sortie-->
```text
clients groupés par ville : variance entre villes tau² = 0.00000 | variance résiduelle sigma² = 0.1373
ICC = tau²/(tau² + sigma²) = 0.0000
```

L'ICC est estimé à **0** (la variance entre villes est estimée au bord de l'espace des paramètres : exactement 0) : une fois l'âge et le canal pris en compte, la ville n'explique rien du panier. Le modèle mixte aurait ici été superflu, et nos analyses des sections précédentes (sans effet de ville) étaient légitimes. Retenons que **regrouper n'implique pas toujours une dépendance** : le modèle mixte est un outil à utiliser quand l'ICC est notable.

Pour les points relais, la situation est tout autre :

```python
m_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=True)
tau2, sigma2 = m_ri.cov_re.iloc[0, 0], m_ri.scale
print(m_ri.summary().tables[1])
print(f"\nvariance entre relais tau² = {tau2:.3f} (écart-type {np.sqrt(tau2):.2f}) | variance résiduelle sigma² = {sigma2:.3f} (écart-type {np.sqrt(sigma2):.2f})")
print(f"ICC = {tau2 / (tau2 + sigma2):.3f} : environ {100 * tau2 / (tau2 + sigma2):.0f} % de la variance des notes (après effet du délai et du type de relais) est due au relais")
```
<!--sortie-->
```text
            Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept  12.489    0.364   34.284  0.000  11.775  13.202
dc         -0.710    0.034  -21.047  0.000  -0.776  -0.644
urbain      0.377    0.534    0.705  0.481  -0.671   1.424
Group Var   1.711    0.280                                

variance entre relais tau² = 1.711 (écart-type 1.31) | variance résiduelle sigma² = 4.350 (écart-type 2.09)
ICC = 0.282 : environ 28 % de la variance des notes (après effet du délai et du type de relais) est due au relais
```

Plus du quart (28 %) de la variance résiduelle des notes est **entre relais** : deux commandes du même relais sont corrélées (corrélation ≈ 0,28). Avec 16 commandes par relais en moyenne, l'**effet de plan** est considérable : $1+(m-1)\rho\approx1+15\times0{,}28\approx5{,}2$ : pour une variable qui ne varie qu'entre relais, les 484 commandes **valent environ 484/5 ≈ 93 observations indépendantes**. Remarquez le résultat sur `urbain` : sa erreur standard est de 0,534 avec le modèle mixte, contre 0,224 pour la régression ordinaire du 1.7.2, soit **2,4 fois plus**. L'intervalle de confiance ordinaire (de 0,04 à 0,92) **exclut** zéro et laisse croire à un effet « significatif » ; l'intervalle mixte (de −0,67 à 1,42) **ne l'exclut pas**. C'est l'effet de plan en action : les 484 commandes n'apportent, sur le type de relais, que l'information de 30 relais.

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

Vérifions la formule, puis comparons les deux estimations à la **vérité**, que nous connaissons ici (les vrais $u_{0j}$) :

```python
beta_ri = m_ri.fe_params
rel["r"] = rel["note"] - (beta_ri["Intercept"] + beta_ri["dc"] * rel["dc"] + beta_ri["urbain"] * rel["urbain"])      # résidus « fixes »
groupes = rel.groupby("relais")["r"].agg(["mean", "size"]).rename(columns={"mean": "r_bar", "size": "n_j"})
groupes["B"] = tau2 / (tau2 + sigma2 / groupes["n_j"])
groupes["u_formule"] = groupes["B"] * groupes["r_bar"]
groupes["u_statsmodels"] = [m_ri.random_effects[g]["Group"] for g in groupes.index]
groupes["u_vrai"] = u0
print("formule du BLUP = statsmodels :", np.allclose(groupes["u_formule"], groupes["u_statsmodels"]))
print(groupes.sort_values("n_j").iloc[[0, 1, 2, 14, 27, 28, 29]].round(3).to_string())
erreur_sans = np.sqrt(np.mean((groupes["r_bar"] - groupes["u_vrai"])**2))
erreur_part = np.sqrt(np.mean((groupes["u_statsmodels"] - groupes["u_vrai"])**2))
print(f"\nerreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = {erreur_sans:.3f} | mise en commun partielle = {erreur_part:.3f}")
petits = groupes["n_j"] <= 8
print(f"  pour les {petits.sum()} petits relais (8 commandes ou moins) :   sans = {np.sqrt(np.mean((groupes.loc[petits, 'r_bar'] - groupes.loc[petits, 'u_vrai'])**2)):.3f} | partielle = {np.sqrt(np.mean((groupes.loc[petits, 'u_statsmodels'] - groupes.loc[petits, 'u_vrai'])**2)):.3f}")
```
<!--sortie-->
```text
formule du BLUP = statsmodels : True
        r_bar  n_j      B  u_formule  u_statsmodels  u_vrai
relais                                                     
R01    -1.983    4  0.611     -1.213         -1.213  -0.937
R05     0.997    4  0.611      0.610          0.610  -0.683
R10    -2.442    4  0.611     -1.493         -1.493   0.413
R19    -0.426   11  0.812     -0.346         -0.346   0.624
R12    -0.644   31  0.924     -0.595         -0.595  -0.548
R16     1.386   56  0.957      1.326          1.326   1.867
R29     1.257   58  0.958      1.204          1.204   0.725

erreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = 0.900 | mise en commun partielle = 0.765
  pour les 10 petits relais (8 commandes ou moins) :   sans = 1.273 | partielle = 1.031
```

La formule reproduit exactement les prédictions de `statsmodels`. Surtout, l'erreur par rapport aux **vrais** niveaux est plus faible avec la mise en commun partielle, et le gain est **le plus net pour les petits relais**, dont l'estimation individuelle était la plus bruitée. Voyons le mécanisme sur un graphique : pour chaque relais (classés par taille), on relie son estimation « sans mise en commun » à son estimation rétrécie.

```python
ordre = groupes.sort_values("n_j").reset_index()
fig, ax = plt.subplots(figsize=(8.8, 4.8))
x = np.arange(len(ordre))
for i, ligne in ordre.iterrows():
    ax.plot([i, i], [ligne["r_bar"], ligne["u_statsmodels"]], color=GRIS, lw=1.2, zorder=1)
ax.scatter(x, ordre["r_bar"], facecolors="none", edgecolors=ORANGE, s=45, lw=1.6, zorder=3, label="sans mise en commun (moyenne du relais)")
ax.scatter(x, ordre["u_statsmodels"], color=BLEU, s=32, zorder=4, label="mise en commun partielle (BLUP)")
ax.scatter(x, ordre["u_vrai"], marker="_", color=ENCRE, s=130, lw=2, zorder=5, label="vérité (connue car simulée)")
ax.axhline(0, color=GRIS, lw=1)
ax.set_xticks(x); ax.set_xticklabels(ordre["n_j"], fontsize=7.5)
ax.set_xlabel("nombre de commandes du relais (relais classés du plus petit au plus grand)")
ax.set_ylabel("niveau de base du relais (écart à la moyenne, en points)")
ax.set_ylim(-3.3, 3.8)                                    # marge en haut pour la légende
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
plt.savefig("figures/ch01-retrecissement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Niveau de base de chacun des 30 relais, classés par nombre de commandes. Les cercles orange sont les moyennes de chaque relais, les points bleus leurs versions rétrécies par le modèle mixte, les traits noirs la vérité. Les segments gris relient les deux estimations. Le rétrécissement est fort pour les petits relais (à gauche) et faible pour les grands (à droite).](figures/ch01-retrecissement.png)

Le dessin raconte l'idée centrale. À gauche, les **petits** relais (4 à 8 commandes) : leur moyenne brute (cercle orange) est très variable, parfois extrême ; le modèle la **ramène nettement vers 0** (point bleu), ce qui la rapproche souvent de la vérité (trait noir). À droite, les **grands** relais : l'estimation brute est déjà fiable et le rétrécissement est faible. Ce principe, **« emprunter de la force aux autres groupes »**, est l'un des plus puissants de la statistique moderne : on le retrouvera dans le cadre bayésien (chapitre 6, avec la loi *a priori* $u_j\sim\mathcal N(0,\tau^2)$).

### 1.7.5 Pente aléatoire : chaque relais a sa propre sensibilité au retard

Jusqu'ici, tous les relais partagent la même pente (−0,7 point par jour de retard, en moyenne). Mais les vraies données ont été produites avec une **pente propre à chaque relais** ($u_{1j}$). On l'inclut par une **pente aléatoire** : $y_{ij}=\beta_0+\beta_1x_{ij}+\dots+u_{0j}+u_{1j}x_{ij}+\varepsilon_{ij}$, où le couple $(u_{0j},u_{1j})$ est tiré d'une loi normale bidimensionnelle de matrice de covariance $\mathbf G$.

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=True, method="lbfgs")
print("Converge :", m_rs.converged)
print(m_rs.summary().tables[1])
G = m_rs.cov_re
print(f"\nécart-type des niveaux de base : {np.sqrt(G.iloc[0, 0]):.3f} (vrai : 1,6) | écart-type des pentes : {np.sqrt(G.iloc[1, 1]):.3f} (vrai : 0,3)")
print(f"corrélation niveau de base / pente : {G.iloc[0, 1] / np.sqrt(G.iloc[0, 0] * G.iloc[1, 1]):.2f} (vraie : 0) | écart-type résiduel : {np.sqrt(m_rs.scale):.3f} (vrai : 1,8)")
```
<!--sortie-->
```text
Converge : True
                 Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept       12.596    0.339   37.166  0.000  11.932  13.260
dc              -0.760    0.064  -11.806  0.000  -0.886  -0.634
urbain           0.277    0.501    0.553  0.581  -0.705   1.259
Group Var        1.427    0.252                                
Group x dc Cov   0.072    0.044                                
dc Var           0.079    0.017                                

écart-type des niveaux de base : 1.195 (vrai : 1,6) | écart-type des pentes : 0.281 (vrai : 0,3)
corrélation niveau de base / pente : 0.21 (vraie : 0) | écart-type résiduel : 1.930 (vrai : 1,8)
```

Les composantes de variance sont raisonnablement proches des vraies valeurs, compte tenu du petit nombre de relais : l'écart-type des niveaux de base est estimé à 1,19 (vrai : 1,6, mais **réalisé** : 1,31 : l'estimation colle à ce qui a effectivement été tiré), celui des pentes à 0,28 (vrai : 0,3), l'écart-type résiduel à 1,93 (vrai : 1,8). La corrélation estimée niveau/pente (0,21), alors que la vraie est nulle, est du bruit d'échantillonnage (son erreur est large avec 30 relais). Les **effets fixes** sont bien retrouvés pour le délai : −0,76 point par jour (vrai : −0,7, intervalle [−0,89 ; −0,63]) ; en revanche l'effet « urbain » est estimé à 0,28 avec une erreur standard de 0,50 : **positif mais très imprécis** (la vraie valeur, 1,2, est à moins de deux erreurs standard). Avec 30 relais, on ne peut tout simplement pas mesurer un effet de niveau groupe de cette taille avec précision.

**Comparer les deux modèles par un test du rapport de vraisemblance.** Les modèles à intercept aléatoire seul et à intercept + pente aléatoire sont emboîtés. On compare leurs vraisemblances. Comme les deux modèles ont les **mêmes effets fixes**, la REML conviendrait aussi ; l'usage prudent, que nous suivons, est de comparer les modèles ajustés par **maximum de vraisemblance** (ML), car la vraisemblance REML ne se compare pas entre modèles d'effets fixes différents.

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ml_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=False)      # optimiseur par défaut (voir la remarque ci-dessous)
    ml_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=False, method="lbfgs")
LR = 2 * (ml_rs.llf - ml_ri.llf)
# Sous H0, la variance de la pente est sur le bord de l'espace des paramètres (>= 0) : loi limite = mélange 50/50 de chi²(1) et chi²(2)
p_val = 0.5 * stats.chi2.sf(LR, 1) + 0.5 * stats.chi2.sf(LR, 2)
print(f"log-vraisemblance (ML) : intercept aléatoire = {ml_ri.llf:.2f} | intercept + pente aléatoires = {ml_rs.llf:.2f}")
print(f"LR = {LR:.2f} | p-valeur (mélange de chi²) = {p_val:.2e}")
print(f"AIC : {-2 * ml_ri.llf + 2 * 5:.1f} (intercept aléatoire, 5 paramètres) contre {-2 * ml_rs.llf + 2 * 7:.1f} (intercept + pente, 7 paramètres)")
```
<!--sortie-->
```text
log-vraisemblance (ML) : intercept aléatoire = -1067.99 | intercept + pente aléatoires = -1047.41
LR = 41.15 | p-valeur (mélange de chi²) = 6.50e-10
AIC : 2146.0 (intercept aléatoire, 5 paramètres) contre 2108.8 (intercept + pente, 7 paramètres)
```

> ⚠️ **Un piège de l'optimisation.** En préparant ce bloc, la même ligne ajustée avec `method="lbfgs"` (l'optimiseur que nous avions utilisé pour la pente aléatoire) a renvoyé une log-vraisemblance **infinie** pour le modèle à intercept aléatoire, sans la moindre erreur : l'optimiseur avait convergé vers une solution dégénérée (variance entre groupes égale à 0). Avec l'optimiseur par défaut, ou avec `bfgs`, on obtient −1067,99, la valeur que donne aussi `lme4`. **Un optimiseur peut échouer en silence.** Vérifiez toujours qu'un ajustement est plausible (log-vraisemblance finie, variances raisonnables) et, dans le doute, comparez deux optimiseurs ou le résultat de `lme4`.

> ⚠️ **Un piège du test.** Tester qu'une **variance** est nulle ($H_0:\tau_1^2=0$) place l'hypothèse nulle **au bord** de l'espace des paramètres (une variance est $\ge0$) : la loi du rapport de vraisemblance n'est pas un simple $\chi^2$ mais un **mélange** de $\chi^2$ (ici 50/50 entre $\chi^2_1$ et $\chi^2_2$). Utiliser un $\chi^2_2$ naïf est **conservateur** (p-valeur trop grande).

Visualisons maintenant le résultat : les droites de **chaque relais** (prédites avec leurs effets aléatoires), autour de la droite moyenne :

```python
fig, ax = plt.subplots(figsize=(8.0, 4.8))
dd = np.arange(-4, 5.01, 1.0)
for j, g in enumerate(sorted(rel["relais"].unique())):
    re = m_rs.random_effects[g]
    u_urb = urbain[j]
    y_g = m_rs.fe_params["Intercept"] + m_rs.fe_params["urbain"] * u_urb + re["Group"] + (m_rs.fe_params["dc"] + re["dc"]) * dd
    ax.plot(dd + 5, y_g, color=ORANGE if u_urb else AQUA, lw=0.9, alpha=0.55)
ax.plot(dd + 5, m_rs.fe_params["Intercept"] + m_rs.fe_params["dc"] * dd, color=ENCRE, lw=3, label="effet moyen (effets fixes), relais non urbain")
ax.scatter(rel["delai"], rel["note"], s=6, color=GRIS, alpha=0.35)
ax.plot([], [], color=ORANGE, lw=1.4, label="relais urbains"); ax.plot([], [], color=AQUA, lw=1.4, label="relais non urbains")
ax.set_xlabel("délai de livraison (jours)"); ax.set_ylabel("note de satisfaction (sur 20)")
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
ax.set_xlim(0.7, 10.3)
plt.savefig("figures/ch01-droites-par-relais.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Droites de régression propres à chaque relais (orange : urbains, vert : non urbains) autour de l'effet moyen (noir). Les relais diffèrent par leur niveau de base (décalage vertical) et par leur sensibilité au retard (pente).](figures/ch01-droites-par-relais.png)

**Les mêmes résultats en R avec `lme4`.** Le paquet `lme4` est la référence pour ces modèles. Les nombres doivent coïncider avec ceux de `statsmodels` (le fichier `donnees/ch01-relais.csv` vient d'être écrit par notre bloc Python) :

```r
suppressMessages(library(lme4))
d <- read.csv("donnees/ch01-relais.csv")
d$dc <- d$delai - 5
m <- lmer(note ~ dc + urbain + (1 + dc | relais), data = d)
print(round(fixef(m), 4))
print(VarCorr(m), digits = 4)
cat("log-vraisemblance REML :", round(as.numeric(logLik(m)), 3), "\n")
```
<!--sortie-->
```text
(Intercept)          dc      urbain 
    12.5960     -0.7598      0.2769 
 Groups   Name        Std.Dev. Corr
 relais   (Intercept) 1.1948       
          dc          0.2812   0.21
 Residual             1.9299       
log-vraisemblance REML : -1049.555 
```

### 1.7.6 Pourquoi ignorer les groupes est dangereux : une simulation

Terminons par la démonstration promise : l'effet d'ignorer la structure de groupes sur la fiabilité des tests. Prenons les **mêmes** tailles de relais et la même variance entre relais, mais supposons que le type de relais (urbain ou non) n'a **aucun effet** réel. Un bon test doit alors rejeter l'hypothèse « aucun effet » dans **5 %** des cas. Combien rejettent-ils réellement ? On répète 300 fois.

```python
rng2 = np.random.default_rng(2024)
R = 300
rej_mco, rej_mixte, z_mixte, tau2_est = 0, 0, [], []
degenere_lbfgs, degenere_defaut = 0, 0
groupe = np.repeat(np.arange(J), tailles)
urb_obs = urbain[groupe]
dc_obs = rel["dc"].to_numpy()
for r in range(R):
    u = rng2.normal(0, 1.6, J)
    y = 12 + u[groupe] - 0.7 * dc_obs + rng2.normal(0, 1.8, len(groupe))                   # AUCUN effet du type de relais
    d_sim = pd.DataFrame({"note": y, "dc": dc_obs, "urbain": urb_obs, "g": groupe})
    p_mco = sm.OLS(y, sm.add_constant(d_sim[["dc", "urbain"]])).fit().pvalues["urbain"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True)                # optimiseur par défaut
        if r < 60:                                                                                   # même ajustement avec lbfgs, sur 60 répétitions
            f2 = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True, method="lbfgs")
            degenere_lbfgs += f2.cov_re.iloc[0, 0] < 1e-6
            degenere_defaut += f.cov_re.iloc[0, 0] < 1e-6
    rej_mco += p_mco < 0.05
    rej_mixte += f.pvalues["urbain"] < 0.05
    z_mixte.append(f.params["urbain"] / f.bse["urbain"])
    tau2_est.append(f.cov_re.iloc[0, 0])
print(f"quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur {R} simulations :")
print(f"  régression ordinaire (groupes ignorés) : {rej_mco / R:.1%}")
print(f"  modèle mixte (intercept aléatoire)     : {rej_mixte / R:.1%}   | écart-type de la statistique z : {np.std(z_mixte):.2f} (théorie : 1)")
print(f"variance entre relais estimée en moyenne : {np.mean(tau2_est):.2f} (vraie valeur : {1.6**2:.2f})")
print(f"sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = {degenere_defaut}/60 | lbfgs = {degenere_lbfgs}/60")
```
<!--sortie-->
```text
quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur 300 simulations :
  régression ordinaire (groupes ignorés) : 55.3%
  modèle mixte (intercept aléatoire)     : 6.7%   | écart-type de la statistique z : 1.04 (théorie : 1)
variance entre relais estimée en moyenne : 2.54 (vraie valeur : 2.56)
sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = 0/60 | lbfgs = 43/60
```

La régression ordinaire, qui ignore le groupage, déclare un effet « significatif » dans **plus de la moitié** des simulations alors qu'il n'y a **aucun effet** : plus de dix fois le taux nominal de 5 %. C'est la conséquence directe de l'effet de plan : des **faux positifs en rafale**. Le modèle mixte, lui, se tient près du niveau nominal (un peu au-dessus de 5 %, ce qui est attendu : l'approximation de Wald est légèrement optimiste avec seulement 30 groupes) ; sa statistique $z$ a un écart-type voisin de 1, et sa variance entre relais est estimée sans biais notable. Voilà pourquoi, dès que les données sont groupées, **les erreurs standard ordinaires ne sont pas fiables pour les variables de niveau groupe**.

La dernière ligne de la sortie confirme l'avertissement du 1.7.5 : avec l'optimiseur `lbfgs`, la plupart des ajustements de ce modèle pourtant simple dégénèrent (43 sur 60 : la variance entre relais est estimée à 0, ce qui fausse tout), alors que l'optimiseur par défaut ne dégénère jamais (0 sur 60). Un résultat qui paraît plausible peut être faux : c'est pourquoi nous avons systématiquement comparé aux valeurs de `lme4`.

> ⚠️ **Précautions.**
> - **Peu de groupes** (moins de 5 à 10) : les variances entre groupes sont très mal estimées, et les approximations de Wald des effets fixes sont trop optimistes. Dans ce cas, envisagez de traiter le groupe comme un effet **fixe** (une indicatrice par groupe) ou une approche bayésienne.
> - **Effets fixes ou aléatoires ?** Traiter les groupes comme **aléatoires** est pertinent si l'on veut généraliser à d'autres groupes de la même population (les 30 relais sont un échantillon des relais possibles) et si les groupes sont nombreux. Si les groupes sont **tous** ceux qui existent (les 6 villes) et peu nombreux, des effets fixes suffisent.
> - **Convergence** : l'optimisation de ces modèles est parfois délicate (variances proches de 0, corrélations proches de ±1). Essayez un autre optimiseur (`method="bfgs"`, `"powell"`…), simplifiez la structure aléatoire, ou comparez à `lme4`.
> - **Interprétation** : les effets fixes sont des effets **moyens** dans la population de groupes ; les effets aléatoires sont des **écarts** propres à chaque groupe.

> ✅ **À retenir (1.7).**
> - Des observations **groupées** (clients d'une même ville, commandes d'un même relais) ne sont pas indépendantes ; l'ignorer rend les **erreurs standard trop petites**, surtout pour les variables de niveau groupe.
> - Le **modèle mixte** ajoute des **effets aléatoires** : $y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_j+\varepsilon_{ij}$, $u_j\sim\mathcal N(0,\tau^2)$. L'**ICC** $=\tau^2/(\tau^2+\sigma^2)$ mesure la part de variance due aux groupes (elle était nulle pour les villes, notable pour les relais).
> - Les effets aléatoires sont prédits par **rétrécissement** : $\hat u_j=\frac{\tau^2}{\tau^2+\sigma^2/n_j}\bar r_j$. Les petits groupes sont davantage ramenés vers la moyenne : c'est la **mise en commun partielle**, qui bat à la fois « tous pareils » et « tous différents ».
> - On peut ajouter des **pentes aléatoires**. Les paramètres se comparent par un test du rapport de vraisemblance (**attention** à la loi limite au bord de l'espace des paramètres) ; l'estimation se fait par **REML**.
> - `statsmodels.MixedLM` et `lme4` en R donnent les mêmes résultats.


## 1.8 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 1 à 8 et 11 à 12 se résolvent surtout à la main ; les exercices 9, 10 et 13 demandent le code.

### Énoncés

**Exercice 1 ⭐ (moindres carrés à la main).** Trois commandes ont $x$ articles et un montant $y$ en DT : $(1,\,2),\ (2,\,3),\ (4,\,7)$. (a) Écrivez $\mathbf X$ et $\mathbf y$, calculez $\mathbf X^\top\mathbf X$ et $\mathbf X^\top\mathbf y$, puis $\hat{\boldsymbol\beta}=(\hat\beta_0,\hat\beta_1)$. (b) Calculez les valeurs ajustées et les résidus, et vérifiez que $\mathbf X^\top\hat{\boldsymbol\varepsilon}=\mathbf 0$. (c) Calculez le $R^2$. (d) Quel montant prévoit-on pour 3 articles ?

**Exercice 2 ⭐ (lire un modèle en log).** Le modèle `log_panier ~ a + C(canal)` du 1.1.7 donne : constante $4{,}2206$, Site $-0{,}1571$, Instagram $-0{,}3368$, âge centré $0{,}0092$ par année. (a) Exprimez **exactement** (en pourcentage) l'effet du Site et d'Instagram par rapport à la boutique. (b) Quel effet pour 10 années d'âge de plus ? (c) Quel est le panier **médian** prédit d'une cliente de 46 ans acquise par le Site ? (d) Pourquoi dit-on « médian » et non « moyen » ?

**Exercice 3 ⭐⭐ (régression simple).** Dans la régression simple $y=\beta_0+\beta_1x+\varepsilon$, démontrez que $\hat\beta_1=r\,\dfrac{s_y}{s_x}$ et que $R^2=r^2$, où $r$ est le coefficient de corrélation de Pearson entre $x$ et $y$. Vérifiez-le sur les quatre commandes du 1.1.1 ($x=1,2,3,4$ ; $y=22,41,66,79$).

**Exercice 4 ⭐⭐ (test et intervalle à la main).** Pour Instagram, `statsmodels` donne le coefficient $-0{,}3368$ et son erreur standard $0{,}0225$, avec $n-p=1736$ degrés de liberté (quantile de Student à 97,5 % : $1{,}961$). (a) Calculez la statistique $t$ et dites si l'on rejette $H_0:\beta=0$ à 5 %. (b) Donnez l'intervalle de confiance à 95 % de $\beta$, puis de l'effet multiplicatif $e^\beta$ exprimé en pourcentage. (c) Pour l'âge : coefficient $0{,}0092$, erreur standard $0{,}00085$ : quelle est la statistique $t$ ?

**Exercice 5 ⭐⭐ (test $F$).** Le modèle réduit `log_panier ~ a` a une somme des carrés résiduelle $\text{SCR}_0=269{,}94$ ; le modèle complet `log_panier ~ a + C(canal)` a $\text{SCR}_1=238{,}30$, avec $n-p_1=1736$. (a) Calculez la statistique $F$ du test « le canal est inutile ». Combien y a-t-il de contraintes $q$ ? (b) La valeur critique de $F_{2,\,1736}$ à 5 % est environ 3,0 : concluez. (c) Si $\text{SCR}_1$ valait 269,70 au lieu de 238,30 (le canal améliorait à peine l'ajustement), que vaudrait $F$ ? Que concluriez-vous ?

**Exercice 6 ⭐⭐ (levier).** Quatre clients ont pour âge centré $x=(1,\,2,\,3,\,10)$. (a) Calculez le levier $h_{ii}=\frac1n+\frac{(x_i-\bar x)^2}{\sum_k(x_k-\bar x)^2}$ de chacun. Vérifiez que leur somme vaut $p=2$. (b) Quel client a le plus d'influence potentielle ? (c) Si $y_4$ augmente de 1, de combien augmente la valeur ajustée $\hat y_4$ ?

**Exercice 7 ⭐⭐ (PRESS).** Reprenez les trois points de l'exercice 1. (a) Calculez les leviers $h_{ii}$. (b) Calculez les erreurs de prédiction « sans le point » $\hat\varepsilon_i/(1-h_{ii})$ et la somme PRESS. (c) Vérifiez l'une d'elles en réajustant la droite sur les deux autres points. (d) Comparez PRESS à la somme des carrés résiduelle : que constatez-vous ?

**Exercice 8 ⭐⭐ (multicolinéarité).** (a) Une variable explicative $x_j$ est expliquée à 99,5 % par les autres ($R_j^2=0{,}995$) : donnez son VIF et le facteur par lequel son erreur standard est multipliée. (b) Avec deux variables explicatives de corrélation 0,9, que vaut leur VIF ? (c) **Code.** Les huit questions de l'enquête de satisfaction (`q1` à `q8`) sont-elles gravement colinéaires entre elles ? Calculez leurs VIF.

**Exercice 9 ⭐⭐ (prédire une moyenne en dinars).** Avec le modèle `log_panier ~ a + C(canal)` : (a) donnez, pour un client **Instagram de 25 ans**, le panier médian prédit ; (b) calculez une prédiction du panier **moyen** avec la correction de Duan ; (c) comparez à la moyenne observée des clients Instagram âgés de 23 à 27 ans. Laquelle des deux prédictions est la plus proche, et pourquoi ?

**Exercice 10 ⭐⭐⭐ (régression sur les ventes mensuelles).** Avec `donnees/ventes_mensuelles.csv` (120 mois), ajustez `log(ca) ~ t + C(mois) + promo + covid`, où `t` est le numéro du mois (0 à 119), `mois` le mois civil (1 à 12), `promo` indique un mois de promotion et `covid` les mois de mars à juin 2020. (a) Quelle est la croissance annuelle estimée ? (b) Quel est l'effet estimé de décembre par rapport à janvier (en facteur multiplicatif) ? (c) Quel est l'effet du confinement de 2020 sur les ventes, en pourcentage ? (d) Que disent le $R^2$ et le test de Durbin-Watson sur ce modèle ? Reste-t-il de la structure dans les résidus ?

**Exercice 11 ⭐⭐⭐ (Ridge, cas orthonormal).** Les colonnes de $\mathbf X$ sont orthonormales ($\mathbf X^\top\mathbf X=\mathbf I$). (a) Montrez que $\hat\beta_j^{\text{ridge}}=\hat\beta_j^{\text{MCO}}/(1+\lambda)$. (b) Pour un coefficient vrai $\beta=2$ et $\sigma=1$, calculez l'erreur quadratique moyenne $\text{EQM}(\lambda)=\dfrac{\lambda^2\beta^2+\sigma^2}{(1+\lambda)^2}$ pour $\lambda=0$, $0{,}25$ et $1$. (c) Quel $\lambda$ la minimise ? Vérifiez par le code sur une grille.

**Exercice 12 ⭐⭐ (modèle mixte, calcul à la main).** Dans un modèle à intercept aléatoire, $\tau^2=2{,}0$ (variance entre groupes) et $\sigma^2=6{,}0$ (variance résiduelle). (a) Calculez l'ICC. (b) Un relais a $n_j=9$ commandes et une moyenne de résidus « fixes » $\bar r_j=3{,}2$ : calculez le facteur de rétrécissement $B_j$ et le BLUP $\hat u_j$. (c) Même question pour un relais de $n_j=2$ commandes avec la même moyenne de résidus. (d) Avec $J=20$ relais de 9 commandes chacun, quel est l'effectif effectif pour estimer une variable qui ne varie qu'entre relais ?

**Exercice 13 ⭐⭐ (robustesse, simulation).** Simulez $n=100$ points $y=2+1{,}5x+\varepsilon$ ($x$ uniforme sur $[0,10]$, $\varepsilon\sim\mathcal N(0,1)$, graine 5), puis ajoutez 25 à $y$ pour 5 points tirés au hasard. Comparez les coefficients des moindres carrés, de Huber et de la régression médiane sur les données propres et corrompues. Que constatez-vous ?

### Corrigés

**Corrigé 1.** (a) $\mathbf X=\begin{pmatrix}1&1\\1&2\\1&4\end{pmatrix}$, $\mathbf y=(2,3,7)^\top$. $\mathbf X^\top\mathbf X=\begin{pmatrix}3&7\\7&21\end{pmatrix}$ (déterminant $63-49=14$), $\mathbf X^\top\mathbf y=(12,\ 2+6+28)^\top=(12,\,36)^\top$. Donc $\hat{\boldsymbol\beta}=\frac1{14}\begin{pmatrix}21&-7\\-7&3\end{pmatrix}\begin{pmatrix}12\\36\end{pmatrix}=\frac1{14}\begin{pmatrix}252-252\\-84+108\end{pmatrix}=\begin{pmatrix}0\\12/7\end{pmatrix}$ : la droite passe **exactement par l'origine** : $\hat y=\frac{12}7x\approx1{,}714\,x$. (b) Ajustées : $\frac{12}7,\ \frac{24}7,\ \frac{48}7$ ; résidus : $\frac27,\ -\frac37,\ \frac17$ (soit $0{,}286;\ -0{,}429;\ 0{,}143$). Somme : $0$ ✓. $\sum x_i\hat\varepsilon_i=\frac27-\frac67+\frac47=0$ ✓. (c) $\text{SCR}=\frac{4+9+1}{49}=\frac27$ ; $\bar y=4$, $\text{SCT}=4+1+9=14$ ; $R^2=1-\frac{2/7}{14}=\frac{48}{49}\approx0{,}980$. (d) $\hat y(3)=\frac{36}7\approx5{,}14$ DT.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")

x = np.array([1.0, 2, 4]); y = np.array([2.0, 3, 7])
X = np.column_stack([np.ones(3), x])
beta = np.linalg.solve(X.T @ X, X.T @ y)
res = y - X @ beta
print("beta =", beta.round(4), "| 12/7 =", round(12 / 7, 4))
print("résidus =", res.round(4), "| X'e =", (X.T @ res).round(10))
print("SCR =", round(res @ res, 4), "| R² =", round(1 - res @ res / ((y - y.mean())**2).sum(), 4), "| prévision en x = 3 :", round(beta[0] + 3 * beta[1], 4))
```
<!--sortie-->
```text
beta = [0.     1.7143] | 12/7 = 1.7143
résidus = [ 0.2857 -0.4286  0.1429] | X'e = [-0.  0.]
SCR = 0.2857 | R² = 0.9796 | prévision en x = 3 : 5.1429
```

**Corrigé 2.** (a) Site : $e^{-0{,}1571}-1=-14{,}5\,\%$ ; Instagram : $e^{-0{,}3368}-1=-28{,}6\,\%$ (et non −15,7 % et −33,7 % : l'approximation $100\beta$ est mauvaise pour de grands coefficients, 1.1.8). (b) $e^{10\times0{,}0092}-1=+9{,}6\,\%$. (c) Pour 46 ans, $a=10$ : $\hat\mu=4{,}2206-0{,}1571+10\times0{,}0092=4{,}1555$, donc $e^{4{,}1555}\approx63{,}8$ DT. (d) Parce que $e^{\hat\mu}$ est la prédiction de la **médiane** de $y$ : pour la moyenne il faudrait la correction $e^{s^2/2}$ ou celle de Duan (1.1.8, et exercice 9).

```python
for nom, b in [("Site", -0.1571), ("Instagram", -0.3368)]:
    print(f"{nom:10s}: {100 * (np.exp(b) - 1):+.1f} %")
print(f"10 ans d'âge : {100 * (np.exp(10 * 0.0092) - 1):+.1f} %")
print(f"panier médian prédit, 46 ans, Site : {np.exp(4.2206 - 0.1571 + 10 * 0.0092):.1f} DT")
```
<!--sortie-->
```text
Site      : -14.5 %
Instagram : -28.6 %
10 ans d'âge : +9.6 %
panier médian prédit, 46 ans, Site : 63.8 DT
```

**Corrigé 3.** On sait (1.1.1, équations normales) que $\hat\beta_1=\dfrac{S_{xy}}{S_{xx}}$ avec $S_{xy}=\sum(x_i-\bar x)(y_i-\bar y)$ et $S_{xx}=\sum(x_i-\bar x)^2$. Or $r=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}$ et $\dfrac{s_y}{s_x}=\sqrt{S_{yy}/S_{xx}}$, donc $r\dfrac{s_y}{s_x}=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}\sqrt{\dfrac{S_{yy}}{S_{xx}}}=\dfrac{S_{xy}}{S_{xx}}=\hat\beta_1$. Pour le $R^2$ : $\hat y_i-\bar y=\hat\beta_1(x_i-\bar x)$, donc $\text{SCE}=\hat\beta_1^2S_{xx}=\dfrac{S_{xy}^2}{S_{xx}}$ et $R^2=\dfrac{\text{SCE}}{\text{SCT}}=\dfrac{S_{xy}^2}{S_{xx}S_{yy}}=r^2$. $\square$

```python
x4 = np.array([1.0, 2, 3, 4]); y4 = np.array([22.0, 41, 66, 79])
r = np.corrcoef(x4, y4)[0, 1]
b1 = np.polyfit(x4, y4, 1)[0]
print(f"r = {r:.5f} | r·sy/sx = {r * y4.std(ddof=1) / x4.std(ddof=1):.4f} | pente MCO = {b1:.4f}")
print(f"r² = {r**2:.5f} | R² du modèle = {sm.OLS(y4, sm.add_constant(x4)).fit().rsquared:.5f}")
```
<!--sortie-->
```text
r = 0.99350 | r·sy/sx = 19.6000 | pente MCO = 19.6000
r² = 0.98705 | R² du modèle = 0.98705
```

**Corrigé 4.** (a) $t=-0{,}3368/0{,}0225=-14{,}97$ ; $|t|\gg1{,}961$ : on rejette $H_0$ (p-valeur de l'ordre de $10^{-48}$). (b) $-0{,}3368\pm1{,}961\times0{,}0225=[-0{,}381\,;\,-0{,}293]$ ; en pourcentage : $e^{-0{,}381}-1=-31{,}7\,\%$ et $e^{-0{,}293}-1=-25{,}4\,\%$ : un effet de **−25 % à −32 %**. (c) $t=0{,}0092/0{,}00085\approx10{,}8$.

```python
b, se, crit = -0.3368, 0.0225, stats.t.ppf(0.975, 1736)
print(f"t = {b / se:.2f} | p = {2 * stats.t.sf(abs(b / se), 1736):.1e} | quantile = {crit:.3f}")
lo, hi = b - crit * se, b + crit * se
print(f"IC de beta : [{lo:.3f} ; {hi:.3f}] | IC de l'effet : [{100 * (np.exp(lo) - 1):.1f} % ; {100 * (np.exp(hi) - 1):.1f} %]")
print(f"t de l'âge = {0.0092 / 0.00085:.2f}")
```
<!--sortie-->
```text
t = -14.97 | p = 9.8e-48 | quantile = 1.961
IC de beta : [-0.381 ; -0.293] | IC de l'effet : [-31.7 % ; -25.4 %]
t de l'âge = 10.82
```

**Corrigé 5.** (a) $q=2$ (les deux coefficients du canal). $F=\dfrac{(269{,}94-238{,}30)/2}{238{,}30/1736}=\dfrac{15{,}82}{0{,}1373}\approx115{,}3$. (b) $115\gg3{,}0$ : on rejette l'hypothèse « le canal est inutile » (p-valeur de l'ordre de $10^{-47}$). (c) $F=\dfrac{(269{,}94-269{,}70)/2}{269{,}70/1736}=\dfrac{0{,}12}{0{,}1554}\approx0{,}77$, inférieur à 3,0 (et même à 1) : le canal n'apporte pas plus que du bruit, on ne rejette pas $H_0$.

```python
def F_stat(scr0, scr1, q, ddl):
    F = ((scr0 - scr1) / q) / (scr1 / ddl)
    return F, stats.f.sf(F, q, ddl)
print("cas observé  : F = %.2f, p = %.1e" % F_stat(269.94, 238.30, 2, 1736))
print("cas (c)      : F = %.2f, p = %.2f" % F_stat(269.94, 269.70, 2, 1736))
print("valeur critique F(2, 1736) à 5 % :", round(stats.f.ppf(0.95, 2, 1736), 3))
```
<!--sortie-->
```text
cas observé  : F = 115.25, p = 1.0e-47
cas (c)      : F = 0.77, p = 0.46
valeur critique F(2, 1736) à 5 % : 3.001
```

**Corrigé 6.** (a) $\bar x=4$, $\sum(x_k-\bar x)^2=9+4+1+36=50$. $h_{11}=\frac14+\frac9{50}=0{,}43$ ; $h_{22}=\frac14+\frac4{50}=0{,}33$ ; $h_{33}=\frac14+\frac1{50}=0{,}27$ ; $h_{44}=\frac14+\frac{36}{50}=0{,}97$. Somme : $2{,}00=p$ ✓. (b) Le client d'âge 10, éloigné des autres : levier de 0,97 (presque 1). (c) $\partial\hat y_4/\partial y_4=h_{44}=0{,}97$ : la droite est presque **forcée** de passer par ce point ; $\hat y_4$ augmente de 0,97.

```python
x6 = np.array([1.0, 2, 3, 10]); X6 = np.column_stack([np.ones(4), x6])
h6 = np.diag(X6 @ np.linalg.inv(X6.T @ X6) @ X6.T)
print("leviers :", h6.round(3), "| somme =", h6.sum().round(3))
y6 = np.array([2.1, 3.9, 6.2, 20.0]); y6b = y6 + np.array([0, 0, 0, 1.0])
f1, f2 = sm.OLS(y6, X6).fit(), sm.OLS(y6b, X6).fit()
print("variation de la valeur ajustée du 4e point quand y4 augmente de 1 :", round(f2.fittedvalues[3] - f1.fittedvalues[3], 3))
```
<!--sortie-->
```text
leviers : [0.43 0.33 0.27 0.97] | somme = 2.0
variation de la valeur ajustée du 4e point quand y4 augmente de 1 : 0.97
```

**Corrigé 7.** (a) $\bar x=7/3$, $S_{xx}=\frac{16}9+\frac19+\frac{25}9=\frac{42}9=\frac{14}3$ : $h_{11}=\frac13+\frac{16/9}{14/3}=\frac5{7}\approx0{,}714$ ; $h_{22}=\frac13+\frac{1/9}{14/3}=\frac5{14}\approx0{,}357$ ; $h_{33}=\frac13+\frac{25/9}{14/3}=\frac{13}{14}\approx0{,}929$ (somme $=2$ ✓). (b) Erreurs sans le point : $\frac{2/7}{2/7}=1$ ; $\frac{-3/7}{9/14}=-\frac23$ ; $\frac{1/7}{1/14}=2$. $\text{PRESS}=1+\frac49+4=\frac{49}9\approx5{,}44$. (c) Sans le point $(1,2)$ : la droite passe par $(2,3)$ et $(4,7)$, d'équation $y=2x-1$, et prévoit $1$ en $x=1$ : l'erreur est $2-1=1$ ✓. (d) PRESS ($5{,}44$) est près de **vingt fois** plus grand que la somme des carrés résiduelle ($2/7\approx0{,}286$) : avec 3 points seulement, l'ajustement « d'apprentissage » est trompeusement optimiste, surtout pour le point $x=4$ à fort levier (0,93), dont l'erreur sans lui est de 2 contre un résidu de 0,14.

```python
Xa = np.column_stack([np.ones(3), np.array([1.0, 2, 4])]); ya = np.array([2.0, 3, 7])
H = Xa @ np.linalg.inv(Xa.T @ Xa) @ Xa.T
e = ya - H @ ya; h = np.diag(H)
print("leviers :", h.round(3))
print("erreurs sans le point (formule) :", (e / (1 - h)).round(4), "| PRESS =", round(np.sum((e / (1 - h))**2), 4), "| 49/9 =", round(49 / 9, 4))
loo = []
for i in range(3):
    m = np.arange(3) != i
    b = np.linalg.lstsq(Xa[m], ya[m], rcond=None)[0]
    loo.append(ya[i] - Xa[i] @ b)
print("erreurs sans le point (réajustement) :", np.round(loo, 4), "| SCR =", round(e @ e, 4))
```
<!--sortie-->
```text
leviers : [0.714 0.357 0.929]
erreurs sans le point (formule) : [ 1.     -0.6667  2.    ] | PRESS = 5.4444 | 49/9 = 5.4444
erreurs sans le point (réajustement) : [ 1.     -0.6667  2.    ] | SCR = 0.2857
```

**Corrigé 8.** (a) $\text{VIF}=\frac1{1-0{,}995}=200$ ; l'erreur standard est multipliée par $\sqrt{200}\approx14$. (b) Avec deux variables, $R_j^2=r^2=0{,}81$, donc $\text{VIF}=\frac1{0{,}19}\approx5{,}3$ : à surveiller (règle empirique : > 5). (c) Voir le code ci-dessous.

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
print("VIF (a) :", 1 / (1 - 0.995), "| racine :", round(np.sqrt(200), 1), "| VIF (b) :", round(1 / (1 - 0.9**2), 2))
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
Q = sm.add_constant(enq[[f"q{i}" for i in range(1, 9)]])
vif = pd.Series([variance_inflation_factor(Q.to_numpy(), i) for i in range(1, Q.shape[1])], index=Q.columns[1:])
print(vif.round(2).to_string())
```
<!--sortie-->
```text
VIF (a) : 199.99999999999983 | racine : 14.1 | VIF (b) : 5.26
q1    1.60
q2    1.42
q3    1.47
q4    1.27
q5    1.71
q6    1.47
q7    1.63
q8    1.46
```

Les VIF des huit questions restent **modestes** (inférieurs à 2) : les questions d'un même bloc (produits d'un côté, service de l'autre) sont corrélées, mais pas au point de rendre un modèle instable. On peut donc les utiliser ensemble, ou les résumer par un score moyen comme au 1.4 (ce que l'analyse factorielle du chapitre 3 formalisera : section 3.2).

**Corrigé 9.** (a) Panier médian prédit : $e^{\hat\mu}$ avec $\hat\mu$ la prédiction du modèle. (b) La prédiction de la moyenne s'obtient en multipliant par le facteur de Duan $\frac1n\sum_ie^{\hat\varepsilon_i}$. (c) On compare à la moyenne observée.

```python
clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
m = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
profil = pd.DataFrame({"a": [25 - 36], "canal": pd.Categorical(["Instagram"], categories=["Boutique", "Site", "Instagram"])})
mu = float(m.predict(profil).iloc[0])
duan = float(np.exp(m.resid).mean())
obs = df[(df["canal"] == "Instagram") & (df["age"].between(23, 27))]["panier_moyen"]
print(f"(a) panier médian prédit      : {np.exp(mu):.2f} DT")
print(f"(b) panier moyen prédit (Duan) : {np.exp(mu) * duan:.2f} DT   [facteur de Duan = {duan:.4f} ; facteur exp(s²/2) = {np.exp(m.scale / 2):.4f}]")
print(f"(c) moyenne observée (Instagram, 23-27 ans, n = {len(obs)}) : {obs.mean():.2f} DT (erreur standard de cette moyenne : {obs.std() / np.sqrt(len(obs)):.2f}) | médiane observée : {obs.median():.2f} DT")
# Test décisif : sur TOUS les clients, quelle prédiction reproduit la moyenne observée ?
mediane_pred = np.exp(m.fittedvalues)
print(f"tous les clients (n = {len(df)}) : moyenne observée = {df['panier_moyen'].mean():.2f} | moyenne de exp(mu) = {mediane_pred.mean():.2f} | moyenne de exp(mu) x Duan = {(mediane_pred * duan).mean():.2f}")
```
<!--sortie-->
```text
(a) panier médian prédit      : 43.95 DT
(b) panier moyen prédit (Duan) : 47.10 DT   [facteur de Duan = 1.0718 ; facteur exp(s²/2) = 1.0710]
(c) moyenne observée (Instagram, 23-27 ans, n = 86) : 44.49 DT (erreur standard de cette moyenne : 1.40) | médiane observée : 42.69 DT
tous les clients (n = 1740) : moyenne observée = 61.23 | moyenne de exp(mu) = 57.12 | moyenne de exp(mu) x Duan = 61.22
```

Sur ce petit groupe (86 clients), **la moyenne observée (44,49) tombe plus près de la prédiction médiane (43,95) que de la prédiction corrigée (47,10)** : ce n'est pas une contradiction de la théorie, mais du bruit d'échantillonnage. L'erreur standard de cette moyenne observée est de 1,40 DT (écart-type des paniers d'environ 13 DT, divisé par $\sqrt{86}$) : la prédiction corrigée (47,10) est à 1,9 erreur standard de la moyenne observée, la prédiction médiane à 0,4 : sur un groupe aussi petit, ces deux écarts sont tous deux plausibles par hasard. Pour **départager** vraiment, il faut un grand échantillon : sur les 1 740 clients, la moyenne observée est de 61,23 DT ; la moyenne des prédictions $e^{\hat\mu}$ (la médiane de chacun) n'en donne que 57,12 DT, soit un défaut de 7 %, alors que les prédictions corrigées $e^{\hat\mu}\times$Duan redonnent 61,22 DT. C'est la confirmation de la théorie du 1.1.8 : la rétro-transformation **naïve vise la médiane, pas la moyenne**, et sous-estime systématiquement le panier moyen ; la correction de Duan la rétablit. (En attendant, retenez qu'une comparaison sur 86 observations ne départage pas des écarts de 7 %.)

**Corrigé 10.**

```python
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
v["t"] = np.arange(len(v))
v["m"] = v["mois"].dt.month
mv = smf.ols("np.log(ca) ~ t + C(m) + promo + covid", data=v).fit()
ic = mv.conf_int()
print(f"(a) croissance annuelle : exp(12 x {mv.params['t']:.4f}) - 1 = {100 * (np.exp(12 * mv.params['t']) - 1):.1f} % par an   (IC95 % du coefficient mensuel : [{ic.loc['t', 0]:.4f} ; {ic.loc['t', 1]:.4f}])")
print(f"(b) décembre / janvier : x {np.exp(mv.params['C(m)[T.12]']):.2f}")
print(f"(c) confinement : {100 * (np.exp(mv.params['covid']) - 1):.0f} % sur les ventes   (IC95 % : [{100 * (np.exp(ic.loc['covid', 0]) - 1):.0f} % ; {100 * (np.exp(ic.loc['covid', 1]) - 1):.0f} %])")
print(f"    promotion : {100 * (np.exp(mv.params['promo']) - 1):+.1f} %   (IC95 % : [{100 * (np.exp(ic.loc['promo', 0]) - 1):+.1f} % ; {100 * (np.exp(ic.loc['promo', 1]) - 1):+.1f} %])")
r = mv.resid.to_numpy()
print(f"(d) R² = {mv.rsquared:.3f} (contre 0,493 pour la tendance seule) | écart-type résiduel = {np.sqrt(mv.scale):.3f} | Durbin-Watson = {sm.stats.durbin_watson(r):.2f} | autocorrélation d'ordre 1 des résidus = {np.corrcoef(r[1:], r[:-1])[0, 1]:.2f}")
```
<!--sortie-->
```text
(a) croissance annuelle : exp(12 x 0.0072) - 1 = 9.0 % par an   (IC95 % du coefficient mensuel : [0.0068 ; 0.0076])
(b) décembre / janvier : x 2.57
(c) confinement : -42 % sur les ventes   (IC95 % : [-46 % ; -37 %])
    promotion : +5.9 %   (IC95 % : [+1.3 % ; +10.7 %])
(d) R² = 0.964 (contre 0,493 pour la tendance seule) | écart-type résiduel = 0.078 | Durbin-Watson = 0.93 | autocorrélation d'ordre 1 des résidus = 0.54
```

(a) Les ventes croissent d'environ **9 % par an** (0,72 % par mois). (b) Décembre est environ **2,6 fois** plus fort que janvier, à tendance égale (la saisonnalité est massive). (c) Le confinement de 2020 correspond à une baisse d'environ **42 %** des ventes sur les quatre mois concernés (intervalle large, de −46 % à −37 %). L'effet des promotions est estimé à environ +6 %, avec un intervalle de confiance **large** (de +1 % à +11 %) : un mois de promotion est un événement rare (une quinzaine de mois sur 120) et la dépendance entre mois rend l'intervalle encore plus incertain. (d) Le $R^2$ monte à **0,96** : tendance, saisonnalité et chocs expliquent presque tout. Mais le **Durbin-Watson est de 0,93** : l'autocorrélation d'ordre 1 des résidus est **0,54**. Il reste donc de la structure : les erreurs successives se ressemblent, de sorte que les p-valeurs et intervalles ci-dessus sont **trop optimistes** (1.3.3). C'est exactement le sujet du chapitre 4 : modéliser cette dépendance (modèles ARIMA, section 4.2). *(Une dernière remarque : les données ayant été simulées, nous pouvons vérifier que les valeurs estimées retrouvent la vérité : croissance de 0,75 % par mois, facteur saisonnier décembre/janvier de $1{,}55/0{,}62\approx2{,}5$, effet du confinement de $-0{,}55$ en log (soit $-42\,\%$), effet des promotions de $+0{,}10$ en log (soit $+10{,}5\,\%$ : dans l'intervalle, mais près de sa borne haute), autocorrélation des erreurs de 0,5.)*

**Corrigé 11.** (a) Avec $\mathbf X^\top\mathbf X=\mathbf I$, la formule de Ridge $(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y$ devient $\frac1{1+\lambda}\mathbf X^\top\mathbf y=\frac1{1+\lambda}\hat{\boldsymbol\beta}^{\text{MCO}}$. (b) Pour $\beta=2,\sigma=1$ : $\text{EQM}(0)=1$ ; $\text{EQM}(0{,}25)=\dfrac{0{,}0625\times4+1}{1{,}5625}=\dfrac{1{,}25}{1{,}5625}=0{,}8$ ; $\text{EQM}(1)=\dfrac{4+1}{4}=1{,}25$. (c) La dérivée s'annule en $\lambda^\star=\sigma^2/\beta^2=0{,}25$ ; à ce point l'EQM vaut 0,8 (une baisse de 20 % par rapport aux moindres carrés), et elle redevient supérieure à 1 pour $\lambda>0{,}5$ ($\lambda=1$ donne 1,25).

```python
beta_v, sigma_v = 2.0, 1.0
eqm = lambda lam: (lam**2 * beta_v**2 + sigma_v**2) / (1 + lam)**2
for lam in [0, 0.25, 0.5, 1]:
    print(f"lambda = {lam:4.2f} : EQM = {eqm(lam):.4f}")
grille = np.linspace(0, 3, 30001)
print("lambda optimal sur la grille :", round(grille[np.argmin(eqm(grille))], 4), "| sigma²/beta² =", sigma_v**2 / beta_v**2)
rng = np.random.default_rng(1)
est = beta_v + rng.normal(0, sigma_v, 200000)                      # estimations MCO simulées
print("EQM simulée : MCO =", round(np.mean((est - beta_v)**2), 3), "| Ridge (lambda = 0,25) =", round(np.mean((est / 1.25 - beta_v)**2), 3))
```
<!--sortie-->
```text
lambda = 0.00 : EQM = 1.0000
lambda = 0.25 : EQM = 0.8000
lambda = 0.50 : EQM = 0.8889
lambda = 1.00 : EQM = 1.2500
lambda optimal sur la grille : 0.25 | sigma²/beta² = 0.25
EQM simulée : MCO = 0.998 | Ridge (lambda = 0,25) = 0.8
```

**Corrigé 12.** (a) $\text{ICC}=\dfrac{2}{2+6}=0{,}25$. (b) $B_j=\dfrac{\tau^2}{\tau^2+\sigma^2/n_j}=\dfrac{2}{2+6/9}=\dfrac{2}{2{,}667}=0{,}75$ ; $\hat u_j=0{,}75\times3{,}2=2{,}4$ : on retient 75 % de l'écart observé. (c) Avec $n_j=2$ : $B_j=\dfrac{2}{2+3}=0{,}4$ et $\hat u_j=0{,}4\times3{,}2=1{,}28$ : un petit relais est rétréci bien davantage (60 % de l'écart est écarté, contre 25 % pour le grand). (d) Effet de plan $1+(m-1)\rho=1+8\times0{,}25=3$ ; $n=20\times9=180$ commandes valent $180/3=60$ observations indépendantes.

```python
tau2, sigma2 = 2.0, 6.0
print("ICC =", tau2 / (tau2 + sigma2))
for n_j in [9, 2]:
    B = tau2 / (tau2 + sigma2 / n_j)
    print(f"n_j = {n_j}: B = {B:.3f} | BLUP = {B * 3.2:.3f}")
deff = 1 + (9 - 1) * tau2 / (tau2 + sigma2)
print("effet de plan =", deff, "| effectif effectif =", 180 / deff)
```
<!--sortie-->
```text
ICC = 0.25
n_j = 9: B = 0.750 | BLUP = 2.400
n_j = 2: B = 0.400 | BLUP = 1.280
effet de plan = 3.0 | effectif effectif = 60.0
```

**Corrigé 13.**

```python
rng = np.random.default_rng(5)
n = 100
x = rng.uniform(0, 10, n)
y_propre = 2 + 1.5 * x + rng.normal(0, 1, n)
y_corr = y_propre.copy()
idx = rng.choice(n, 5, replace=False)
y_corr[idx] += 25
X = sm.add_constant(x)
lignes = {}
for nom, y in [("données propres", y_propre), ("données corrompues", y_corr)]:
    lignes[(nom, "MCO")] = sm.OLS(y, X).fit().params
    lignes[(nom, "Huber")] = sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit().params
    lignes[(nom, "médiane")] = sm.QuantReg(y, X).fit(q=0.5).params
tab = pd.DataFrame(lignes, index=["constante", "pente"]).T
print("vrais coefficients : constante = 2, pente = 1,5")
print(tab.round(3).to_string())
```
<!--sortie-->
```text
vrais coefficients : constante = 2, pente = 1,5
                            constante  pente
données propres    MCO          2.356  1.450
                   Huber        2.375  1.441
                   médiane      2.297  1.436
données corrompues MCO          2.633  1.637
                   Huber        2.424  1.451
                   médiane      2.297  1.450
```

Sur les données **propres**, les trois méthodes donnent des résultats très proches. Après corruption de 5 % des points, les **moindres carrés dérivent** (la pente passe de 1,45 à 1,64 et la constante de 2,36 à 2,63), alors que **Huber et la régression médiane** restent presque inchangés (pente entre 1,44 et 1,45 dans les deux cas). C'est l'intuition du 1.6 : l'influence des points aberrants est plafonnée par les méthodes robustes.

---

## Bilan du chapitre 1

Vous savez maintenant :

- **écrire et résoudre** un modèle linéaire $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ par les équations normales, comprendre pourquoi la solution est une **projection orthogonale** et démontrer le théorème de **Gauss-Markov** ;
- **interpréter** les coefficients (variables qualitatives par indicatrices, « toutes choses égales par ailleurs », modèles en logarithmes, rétro-transformation pour prédire une moyenne) ;
- **faire de l'inférence** : erreurs standard, tests $t$ et $F$ de modèles emboîtés, intervalles de confiance et de **prédiction**, bootstrap des couples, en sachant sous quelles hypothèses ils sont valables ;
- **poser un diagnostic** : graphiques de résidus, tests de Breusch-Pagan et de Durbin-Watson, **levier** et **distance de Cook**, **VIF**, erreurs standard robustes, et savoir remédier aux défauts (transformer, centrer, changer de modèle) ;
- **choisir un modèle** sans tricher : AIC, BIC, validation croisée (PRESS), tests emboîtés, et se méfier de la sélection automatique ;
- (en option) **régulariser** (Ridge, Lasso, Elastic Net) quand les variables sont nombreuses, **résister** aux aberrations (Huber, régression quantile) et **modéliser des données groupées** (effets mixtes, rétrécissement).

Le chapitre 2 généralise la régression à des réponses qui ne sont **ni continues ni normales** : un client rachète-t-il (oui/non) ? combien de commandes passe-t-il (un entier) ? C'est le cadre des **modèles linéaires généralisés**, dont la régression linéaire de ce chapitre est le cas particulier le plus simple.
