## 1.5 ➕ Pour aller plus loin : la régularisation (Ridge, Lasso, Elastic Net)

> 🧭 **Section optionnelle.** Elle prolonge directement 1.3 (multicolinéarité) et 1.4 (surajustement) et sert de pont vers l'apprentissage automatique (volume III). On peut la sauter sans perdre le fil du chapitre.

> 💡 **Intuition.** Quand un modèle a beaucoup de variables pour peu de données, les moindres carrés ont **trop de liberté** : ils utilisent chaque coefficient pour coller au bruit, d'où des coefficients énormes et instables. La **régularisation** consiste à leur mettre une **laisse** : on minimise l'erreur *plus* une pénalité qui grandit avec la taille des coefficients. On accepte un petit biais volontaire (les coefficients sont « rétrécis » vers 0) en échange d'une **forte baisse de variance**. C'est une application directe du dilemme biais-variance, et la preuve que le théorème de Gauss-Markov (1.1.5) a des limites : il ne dit rien des estimateurs **biaisés**.

```python hide
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

```python hide-code
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

**À la main contre `scikit-learn`.** Sur les données de la boutique (âge, canal, notes de l'enquête), la formule explicite et la fonction `Ridge` de `scikit-learn` donnent exactement les mêmes coefficients (à cinq décimales) ; ceux des moindres carrés ($\lambda=0$) sont un peu plus grands :

```python hide
clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client").reset_index(drop=True)

# Un petit jeu de variables : l'âge, le canal, les scores
Xp = pd.DataFrame({"age": bq["a"], "Site": (bq["canal"] == "Site").astype(float), "Réseaux": (bq["canal"] == "Réseaux").astype(float),
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
Réseaux         -0.15797      -0.15797     -0.17241
score_produit    0.09827       0.09827      0.10322
score_service    0.02016       0.02016      0.02035
```

Les deux colonnes de Ridge coïncident : `scikit-learn` fait exactement le calcul de la formule. Les coefficients de Ridge sont **rétrécis** par rapport aux moindres carrés, modestement ici ($\lambda=50$ est petit devant $n\approx1\,000$) : environ 4 % pour l'âge, 15 % pour le Site, 8 % pour Réseaux. Le rétrécissement est le plus marqué pour les indicatrices du canal, qui sont **corrélées entre elles** (les clients Site ne sont pas Réseaux) : leurs directions ont de petites valeurs singulières, exactement celles que le facteur $d_j^2/(d_j^2+\lambda)$ pénalise le plus.

### 1.5.2 Le Lasso : la pénalité qui élimine des variables

Ridge rétrécit tous les coefficients, mais **n'en met jamais aucun exactement à 0**. Le **Lasso** (*Least Absolute Shrinkage and Selection Operator*) remplace le carré par la **valeur absolue** :

$$\hat{\boldsymbol\beta}_{\text{lasso}}(\alpha)=\arg\min_{\boldsymbol\beta}\ \frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\sum_j|\beta_j| .$$

(La normalisation $1/(2n)$ est celle de `scikit-learn`.) Ce changement apparemment minuscule a une conséquence majeure : le Lasso produit des solutions **creuses**, où beaucoup de coefficients sont **exactement nuls**. C'est une régression qui **sélectionne** ses variables tout en les ajustant.

> 💡 **Pourquoi des zéros ? La géométrie.** Minimiser la somme des carrés sous la contrainte $\sum_j\beta_j^2\le r^2$ (Ridge) ou $\sum_j|\beta_j|\le r$ (Lasso) donne le même résultat que les versions pénalisées. Les courbes de niveau de la somme des carrés sont des **ellipses** centrées sur la solution des moindres carrés ; la solution contrainte est le **premier point de contact** entre une ellipse qui grandit et la région admissible. Pour Ridge, la région est un **disque** : le contact est un point lisse, quelconque, où aucun coefficient n'est nul. Pour le Lasso, la région est un **losange** dont les **sommets sont sur les axes** : une ellipse qui grandit touche très souvent un sommet, où un coefficient est exactement nul.

```python hide
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

Écrite à la main, cette descente par coordonnées donne exactement les coefficients de `scikit-learn`. Avec $\alpha=0{,}05$, on trouve 0,053 pour l'âge, −0,075 pour Réseaux, 0,055 pour le score produit, et **exactement zéro** pour `Site` et `score_service` (les moindres carrés donnaient 0,103 ; −0,172 ; 0,103 ; −0,075 et 0,020).

```python hide
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
Réseaux         -0.07486      -0.07486 -0.17241
score_produit    0.05465       0.05465  0.10322
score_service    0.00000       0.00000  0.02035
coefficients exactement nuls (à la main) : ['Site', 'score_service']
```

Cette coïncidence valide l'algorithme. Mais regardez ce que fait ce seuil $\alpha=0{,}05$, choisi arbitrairement : le Lasso met à zéro `score_service`, qui (dans le vrai modèle) n'a pas d'effet direct sur le panier, mais aussi `Site`, qui **a** un vrai effet (−15 % environ, 1.2.2), et il **divise par deux** à peu près les autres coefficients. Cette pénalité est donc **trop forte** : un $\alpha$ mal choisi supprime de vraies variables et sous-estime les effets. D'où l'importance de choisir $\alpha$ par validation croisée, ce que nous faisons maintenant.

### 1.5.3 L'Elastic Net : un compromis

Le Lasso a un défaut : face à un **groupe de variables très corrélées**, il en choisit une presque au hasard et élimine les autres, de façon instable. Ridge, au contraire, répartit le poids entre elles. L'**Elastic Net** combine les deux pénalités :

$$\frac1{2n}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2+\alpha\Big(\rho\sum_j|\beta_j|+\frac{1-\rho}2\sum_j\beta_j^2\Big),\qquad\rho\in[0,1].$$

Pour $\rho=1$ c'est le Lasso, pour $\rho\to0$, Ridge. Il fournit des solutions **creuses** tout en étant **stables** en présence de variables corrélées. On choisit $\alpha$ et $\rho$ par validation croisée.

### 1.5.4 Beaucoup de variables, peu de clients : l'expérience

Mettons les trois méthodes à l'épreuve (code pas à pas dans le cahier, application 1.9) dans un scénario réaliste d'**analyse exploratoire** : on dispose de **35 variables candidates** pour prévoir le log-panier d'un client, et de seulement **120 clients** pour apprendre le modèle. Parmi ces 35 variables : 4 portent un vrai signal (l'âge, deux indicatrices de canal, le score produit), quelques-unes sont des **variables pertinentes mais inutiles** (ville, offre de bienvenue, score service, courbure de l'âge, interactions), et **20 sont du pur bruit** que nous ajoutons (nombres tirés au hasard : des « variables » sans aucun rapport avec les clients). On teste sur les 956 autres clients de l'enquête.

```python hide
rng = np.random.default_rng(31)
ville = bq["id_client"].map(clients.set_index("id_client")["ville"])
villes = pd.get_dummies(ville, prefix="ville", drop_first=True, dtype=float)       # 5 indicatrices (Autre = référence)
F = pd.DataFrame({
    "age": bq["a"].astype(float), "age_carre": bq["a"].astype(float) ** 2, "age_cube": bq["a"].astype(float) ** 3,
    "canal_Site": (bq["canal"] == "Site").astype(float), "canal_Reseaux": (bq["canal"] == "Réseaux").astype(float),
    "offre_bienvenue": bq["id_client"].map(clients.set_index("id_client")["offre_bienvenue"]).astype(float),
    "score_produit": bq["score_produit"], "score_service": bq["score_service"],
    "age_x_Site": bq["a"] * (bq["canal"] == "Site").astype(float), "age_x_Reseaux": bq["a"] * (bq["canal"] == "Réseaux").astype(float),
})
F = pd.concat([F, villes], axis=1)
bruit = pd.DataFrame(rng.normal(size=(len(F), 20)), columns=[f"bruit_{i+1:02d}" for i in range(20)])
F = pd.concat([F, bruit], axis=1)
signal = ["age", "canal_Site", "canal_Reseaux", "score_produit"]               # les variables qui ont un VRAI effet dans la simulation
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

```python hide-code
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

Les coefficients retenus par le Lasso, comparés à ceux des moindres carrés, racontent la même histoire.

```python hide
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
age            0.165  0.033  0.050        0.050
age_carre      0.052  0.015  0.011        0.010
canal_Site    -0.174 -0.033 -0.091       -0.090
canal_Reseaux -0.218 -0.056 -0.132       -0.131
score_produit  0.106  0.053  0.096        0.095
age_x_Reseaux -0.005  0.022  0.026        0.026
ville_Ville D -0.067 -0.021 -0.013       -0.013
ville_Ville E -0.037  0.013  0.004        0.003
bruit_01       0.073  0.024  0.025        0.024
bruit_02       0.060  0.012  0.013        0.012
bruit_11      -0.034 -0.016 -0.005       -0.004
bruit_13      -0.052 -0.013 -0.004       -0.003
bruit_14       0.020  0.020  0.021        0.021
bruit_19       0.013  0.015  0.004        0.003
bruit_20      -0.054 -0.021 -0.014       -0.014

variables de bruit : plus grand |coefficient| MCO = 0.073 | Ridge = 0.024 | Lasso = 0.025
```

Le Lasso retient **les quatre vraies variables** (âge, Site, Réseaux, score produit), avec des coefficients de 0,05 à 0,13 en valeur absolue, et laisse passer 7 variables de bruit dont les coefficients sont **au plus 0,025**, c'est-à-dire plus de deux fois plus petits que le plus petit coefficient d'une vraie variable : l'ordre de grandeur permet de les distinguer. Avec les moindres carrés, au contraire, les variables de bruit atteignent 0,073, un coefficient du même ordre que celui du score produit (0,106) : on ne peut plus faire la différence. Remarquez aussi que les coefficients MCO des vraies variables sont **gonflés** par rapport à ceux du Lasso (l'âge : 0,165 contre 0,050) : c'est le **biais de sélection** vu au 1.4.5, qui joue ici à l'envers, puisque la régularisation le contrôle.

**Les chemins de régularisation.** Pour voir la régularisation à l'œuvre, on trace comment chaque coefficient évolue quand la pénalité varie, de très forte (tous les coefficients à 0) à très faible (on retrouve les moindres carrés).

```python hide
alphas_l, coefs_l, _ = lasso_path(Ztr, ytr - ytr.mean(), alphas=80)
alphas_r = np.logspace(-1, 4, 80)
coefs_r = np.array([np.linalg.solve(Ztr.T @ Ztr + a * np.eye(Ztr.shape[1]), Ztr.T @ (ytr - ytr.mean())) for a in alphas_r]).T
couleurs = {"age": VIOLET, "canal_Site": AQUA, "canal_Reseaux": ORANGE, "score_produit": BLEU}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
for ax, al, cf, titre, choisi in [(ax1, alphas_r, coefs_r, "Ridge", ridge.alpha_), (ax2, alphas_l, coefs_l, "Lasso", lasso.alpha_)]:
    for i, nom in enumerate(noms):
        if nom in couleurs:
            continue
        ax.plot(np.log10(al), cf[i], color=GRIS, lw=0.7, alpha=0.55)
    for i, nom in enumerate(noms):
        if nom in couleurs:
            ax.plot(np.log10(al), cf[i], color=couleurs[nom], lw=2.2, label={"canal_Reseaux": "canal Réseaux"}.get(nom, nom.replace("_", " ")))
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
