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

```python hide
marges = np.linspace(-2.5, 2.5, 501)
pertes = {
    "0-1": (marges <= 0).astype(float),
    "charnière": np.maximum(0, 1 - marges),
    "logistique": np.log1p(np.exp(-marges)),
    "quadratique": (1 - marges) ** 2,
}
fig, ax = plt.subplots(figsize=(7.2, 4.0))
couleurs = {"0-1": "#898781", "charnière": ORANGE, "logistique": BLEU, "quadratique": VIOLET}
for nom, v in pertes.items():
    ax.plot(marges, np.minimum(v, 4.2), color=couleurs[nom], lw=2.2 if nom != "0-1" else 1.6, label=nom)
ax.set_xlabel("marge  m = y·f(x)   (négative : erreur ; positive : bien classé)")
ax.set_ylabel("coût")
ax.set_ylim(-0.1, 4.3)
ax.set_title("Quatre façons de payer une erreur de classement")
ax.legend(frameon=False, loc="upper right")
style.save(fig, "ch02-pertes.png")
```
<!--sortie-->
```text
figure : ch02-pertes.png
```

![Quatre fonctions de perte en fonction de la marge. La perte 0-1 est un escalier ; les trois autres la majorent et sont convexes, donc minimisables par descente de gradient.](figures/ch02-pertes.png)

```python hide-code
m = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
tab = pd.DataFrame({"marge": m, "0-1": (m <= 0).astype(int), "charnière": np.maximum(0, 1 - m),
                    "logistique": np.log1p(np.exp(-m)), "quadratique": (1 - m) ** 2})
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
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

```python hide
x4 = np.array([-2.0, -1.0, 1.0, 3.0]); y4 = np.array([0, 0, 1, 1])
def perte4(w, b):
    p = 1 / (1 + np.exp(-(w * x4 + b)))
    return float(-np.mean(y4 * np.log(p) + (1 - y4) * np.log(1 - p)))
w1 = 0.5 * 0.875
NUM("grad_w_0", np.mean((0.5 - y4) * x4))
NUM("w_apres_pas", w1)
NUM("perte_avant_pas", perte4(0.0, 0.0))
NUM("perte_apres_pas", perte4(w1, 0.0))
```
<!--sortie-->
```text
NUM grad_w_0 -0.875
NUM w_apres_pas 0.4375
NUM perte_avant_pas 0.6931471805599453
NUM perte_apres_pas 0.39576454603606187
```

La perte passe de 0,693 à 0,396 : un seul pas a déjà nettement amélioré le modèle. Répétés des centaines de fois, ces pas convergent vers le minimum. Dans la **descente de gradient stochastique** (SGD), on ne calcule pas le gradient sur tous les clients mais sur un petit paquet tiré au hasard (un *mini-lot*) : chaque pas est bruité, mais il est $n/\text{taille du lot}$ fois moins cher, ce qui rend l'apprentissage possible sur des millions de lignes. C'est la méthode d'entraînement de presque tous les modèles à grande échelle, des modèles linéaires aux réseaux de neurones.

### 2.1.4 Pourquoi il faut mettre les variables à l'échelle

Sur nos données, la **récence** s'exprime en jours (de 0 à 365), le **nombre de commandes** est de l'ordre de la dizaine, le taux d'ouverture des courriels est entre 0 et 1. Une descente de gradient sur de telles variables brutes est un cauchemar : le gradient est dominé par la variable aux grandes valeurs, et le pas $\eta$ qui évite l'explosion pour celle-là est ridiculement petit pour les autres.

Formellement, la vitesse de convergence dépend du **conditionnement** $\kappa$, le rapport entre la plus grande et la plus petite valeur propre du Hessien de la perte au voisinage du minimum : pour une perte quadratique, l'erreur est multipliée par $\frac{\kappa-1}{\kappa+1}$ à chaque pas au mieux. Plus $\kappa$ est grand, plus la descente zigzague.

```python hide
from sklearn.linear_model import LogisticRegression

duo = ["recence_jours", "nb_commandes_12m"]
A = Xtr[duo].to_numpy(float)
A_std = (A - A.mean(0)) / A.std(0)
yy = ytr.to_numpy(float)

def descente(M, pas, n_iter=400):
    M1 = np.column_stack([np.ones(len(M)), M])
    th = np.zeros(M1.shape[1]); hist = []
    for _ in range(n_iter):
        p = 1 / (1 + np.exp(-M1 @ th))
        hist.append(float(-np.mean(yy * np.log(p + 1e-12) + (1 - yy) * np.log(1 - p + 1e-12))))
        th = th - pas * M1.T @ (p - yy) / len(yy)
    return np.array(hist)

def hess_cond(M):
    M1 = np.column_stack([np.ones(len(M)), M])
    lr_ = LogisticRegression(C=1e6, max_iter=5000).fit(M, yy)
    p = lr_.predict_proba(M)[:, 1]
    H = M1.T @ (M1 * (p * (1 - p))[:, None]) / len(M)
    v = np.linalg.eigvalsh(H)
    return float(v.max() / v.min())

# plus grand pas de la grille pour lequel la perte décroît à chaque itération (sinon la descente oscille ou explose)
monotone = lambda h: bool(np.all(np.diff(h) <= 1e-12))
pas_brut = next(g for g in [1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6]
                if np.isfinite(descente(A, g)[-1]) and monotone(descente(A, g)))
h_brut, h_std = descente(A, pas_brut), descente(A_std, 0.5)
opt = LogisticRegression(C=1e6, max_iter=5000).fit(A, yy)
perte_opt = log_loss(yy, opt.predict_proba(A)[:, 1])
NUM("pas_brut", pas_brut)
NUM("perte_brut_400", h_brut[-1])
NUM("perte_std_400", h_std[-1])
NUM("perte_optimale", perte_opt)
NUM("kappa_brut", hess_cond(A))
NUM("kappa_std", hess_cond(A_std))

fig, ax = plt.subplots(figsize=(7.2, 3.9))
ax.plot(np.arange(1, 401), h_brut - perte_opt, color=ORANGE, lw=2.2)
ax.plot(np.arange(1, 401), h_std - perte_opt, color=BLEU, lw=2.2)
ax.set_yscale("log")
ax.set_xlabel("itération de la descente de gradient")
ax.set_ylabel("écart à la perte minimale (échelle log)")
ax.text(260, (h_brut - perte_opt)[260] * 1.5, "variables brutes\n(pas maximal stable)", color=ORANGE, fontsize=9, ha="left")
ax.text(120, (h_std - perte_opt)[120] * 3.0, "variables standardisées", color=BLEU, fontsize=9, ha="left")
ax.set_title("La même descente de gradient, avec et sans mise à l'échelle")
style.save(fig, "ch02-gradient-echelle.png")
```
<!--sortie-->
```text
NUM pas_brut 0.0003
NUM perte_brut_400 0.5013224176347075
NUM perte_std_400 0.34231381827021456
NUM perte_optimale 0.3423125804263067
NUM kappa_brut 377485.95008772163
NUM kappa_std 13.579850952663138
figure : ch02-gradient-echelle.png
```

Sur un modèle à deux variables seulement (la récence et le nombre de commandes), le conditionnement du Hessien est d'environ 377 486 avec les variables brutes, et de 13,6 une fois les variables **standardisées** (moyenne 0, écart-type 1). Le graphique montre la conséquence : avec le plus grand pas de la grille pour lequel la perte décroît sans osciller (0,000), la perte vaut encore 0,50 après 400 itérations (le minimum est 0,342), tandis que la descente sur variables standardisées atteint 0,342, soit le minimum à quelques millièmes près.

![Écart à la perte minimale au fil des itérations, pour la même descente de gradient. Orange : variables brutes (le pas doit rester minuscule). Bleu : variables standardisées.](figures/ch02-gradient-echelle.png)

> ⚠️ **Standardiser n'est pas facultatif… pour certains modèles.** Les modèles entraînés par descente de gradient (linéaire, logistique, réseaux de neurones), à pénalité (Ridge, Lasso) ou fondés sur des **distances** (k plus proches voisins, SVM) exigent des variables à des échelles comparables. Les **arbres** et leurs dérivés (forêts, boosting) n'en ont pas besoin : ils ne comparent une variable qu'à des seuils, et une transformation croissante (changer l'unité, passer au logarithme) ne change ni l'ordre ni donc les découpages. Le chapitre 4 reviendra sur ces règles en détail (section 4.1).

### 2.1.5 La pénalité : une contrainte déguisée

Quand les variables sont nombreuses ou corrélées, les coefficients de la régression logistique peuvent devenir grands, instables, et le modèle sur-apprend. On ajoute à la perte une **pénalité** :

$$\min_{w,b}\ L(w,b)+\lambda\,\Omega(w),\qquad \Omega(w)=\|w\|_2^2\ \text{(Ridge)}\quad\text{ou}\quad\|w\|_1=\sum_j|w_j|\ \text{(Lasso)}.$$

> 📐 **Pénalité et contrainte, deux visages du même problème.** Par la théorie des multiplicateurs de Lagrange (volume I, section 1.3.5), minimiser $L+\lambda\Omega$ revient à minimiser $L$ **sous la contrainte** $\Omega(w)\le t$, avec $t$ qui décroît quand $\lambda$ croît. Choisir un $\lambda$ plus grand, c'est se limiter à un plus **petit domaine** de coefficients possibles : le modèle est moins riche, donc moins sujet au surapprentissage. Le domaine $\|w\|_2\le t$ est un **disque** ; le domaine $\|w\|_1\le t$ est un **losange** dont les sommets sont sur les axes. La solution est le point où les courbes de niveau de la perte touchent le domaine. Sur un disque, ce point est « n'importe où » ; sur un losange, il est très souvent **à un sommet**, c'est-à-dire avec **un coefficient exactement nul**. D'où la propriété du Lasso : il **sélectionne** des variables.

```python hide
from scipy.optimize import minimize

w0 = np.array([1.6, 0.9]); Q = np.array([[1.0, 0.55], [0.55, 0.35]])    # perte quadratique centrée en w0
perte_q = lambda w: (w - w0) @ Q @ (w - w0)
def sol(contrainte):
    r = minimize(perte_q, x0=[0.1, 0.1], constraints=[{"type": "ineq", "fun": contrainte}], method="SLSQP")
    return r.x
t = 1.0
w_l2 = sol(lambda w: t ** 2 - w @ w)
w_l1 = sol(lambda w: t - np.abs(w).sum())
NUM("w_l1_1", w_l1[0]); NUM("w_l1_2", w_l1[1]); NUM("w_l2_1", w_l2[0]); NUM("w_l2_2", w_l2[1])

g1, g2 = np.meshgrid(np.linspace(-1.5, 2.4, 300), np.linspace(-1.2, 1.9, 300))
Z = np.einsum("...i,ij,...j->...", np.stack([g1 - w0[0], g2 - w0[1]], -1), Q, np.stack([g1 - w0[0], g2 - w0[1]], -1))
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.3), sharey=True)
th = np.linspace(0, 2 * np.pi, 200)
for ax, titre, w_s in ((axs[0], "Pénalité $\\ell_2$ (Ridge) : un disque", w_l2), (axs[1], "Pénalité $\\ell_1$ (Lasso) : un losange", w_l1)):
    ax.contour(g1, g2, Z, levels=[0.1, 0.35, 0.8, 1.5], colors=[BLEU], linewidths=1.1)
    ax.plot(*w0, "o", color=BLEU, ms=6); ax.annotate("optimum sans contrainte", w0, (0.55, 1.62), color=BLEU, fontsize=8.5, bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1.5), arrowprops=dict(arrowstyle="-", color=BLEU, lw=0.8))
    ax.axhline(0, color="#c3c2b7", lw=0.8); ax.axvline(0, color="#c3c2b7", lw=0.8)
    ax.plot(*w_s, "o", color=ORANGE, ms=8)
    ax.set_title(titre, fontsize=10.5); ax.set_xlabel("coefficient $w_1$"); ax.set_aspect("equal")
axs[0].plot(np.cos(th), np.sin(th), color=ORANGE, lw=2); axs[0].set_ylabel("coefficient $w_2$")
axs[0].annotate("solution", w_l2, (0.2, -0.85), color=ORANGE, fontsize=9, bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1.5), arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
axs[1].fill([1, 0, -1, 0, 1], [0, 1, 0, -1, 0], facecolor="none", edgecolor=ORANGE, lw=2)
axs[1].annotate("solution : $w_2=0$", w_l1, (0.9, -0.85), color=ORANGE, fontsize=9, bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1.5), arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
style.save(fig, "ch02-ridge-lasso-geometrie.png")
```
<!--sortie-->
```text
NUM w_l1_1 0.9999990251792866
NUM w_l1_2 9.74820713611349e-07
NUM w_l2_1 0.8687242347744353
NUM w_l2_2 0.49529614022577667
figure : ch02-ridge-lasso-geometrie.png
```

![Courbes de niveau d'une perte (bleu) et domaine autorisé (orange) pour une pénalité l2 (disque) et l1 (losange). La solution du Lasso tombe sur un sommet du losange, où un coefficient est nul.](figures/ch02-ridge-lasso-geometrie.png)

Un cas simple permet de voir le mécanisme sans algorithme : si les variables sont orthonormées et la perte quadratique, le Lasso **seuille** les coefficients estimés $z_j$ : $\hat w_j=\operatorname{signe}(z_j)\,(|z_j|-\lambda)_+$, alors que Ridge les **rétrécit** : $\hat w_j=z_j/(1+\lambda)$. Avec $z=(3;\,0{,}8;\,-0{,}3)$ et $\lambda=0{,}5$, le Lasso donne $(2{,}5;\ 0{,}3;\ 0)$ (la petite variable disparaît) et Ridge donne $(2;\ 0{,}533;\ -0{,}2)$ (toutes survivent, rétrécies).

Sur la résiliation, voyons ce que fait le Lasso quand on fait varier la force de la pénalité. En `scikit-learn`, le réglage se nomme `C` et vaut l'**inverse** de la force : un petit `C` donne une forte pénalité.

```python hide
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

pre_lin = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
cv5 = StratifiedKFold(5, shuffle=True, random_state=0)
grille_C = np.logspace(-3, 1, 9)
lignes = []
for C in grille_C:
    for pen in ("l1", "l2"):
        mod = make_pipeline(pre_lin, LogisticRegression(C=C, penalty=pen, solver="liblinear", max_iter=2000, random_state=0))
        auc_cv = cross_val_score(mod, Xtr, ytr, cv=cv5, scoring="roc_auc").mean()
        nz = int((mod.fit(Xtr, ytr)[-1].coef_ != 0).sum())
        lignes.append({"C": C, "pénalité": pen, "AUC CV": auc_cv, "coefficients non nuls": nz})
chemin = pd.DataFrame(lignes)
meilleur = chemin.sort_values("AUC CV", ascending=False).iloc[0]
NUM("C_opt", meilleur["C"]); NUM("pen_opt", meilleur["pénalité"]); NUM("auc_cv_opt", meilleur["AUC CV"])
nz_l1 = chemin[chemin["pénalité"] == "l1"].set_index("C")["coefficients non nuls"]
NUM("nz_l1_fort", nz_l1.iloc[0]); NUM("nz_l1_faible", nz_l1.iloc[-1]); NUM("nz_l2_tous", chemin[chemin["pénalité"] == "l2"]["coefficients non nuls"].iloc[0])
NUM("nb_coef_total", len(pre_lin.fit(Xtr, ytr).get_feature_names_out()))
```
<!--sortie-->
```text
NUM C_opt 0.31622776601683794
NUM pen_opt l2
NUM auc_cv_opt 0.8605095725050026
NUM nz_l1_fort 1
NUM nz_l1_faible 44
NUM nz_l2_tous 49
NUM nb_coef_total 49
```

```python hide-code
aff = chemin.pivot(index="C", columns="pénalité", values=["AUC CV", "coefficients non nuls"])
aff.columns = ["AUC l1", "AUC l2", "nb coef. l1", "nb coef. l2"]
print(aff.round(4).to_string())
```
<!--sortie-->
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

```python hide
p_lr = logistique.predict_proba(Xte)[:, 1]
NUM("auc_lr", roc_auc_score(yte, p_lr)); NUM("logloss_lr", log_loss(yte, p_lr))
```
<!--sortie-->
```text
NUM auc_lr 0.8655723784007316
NUM logloss_lr 0.28194274326161317
```

Avec une **AUC** de 0,866 sur le jeu de test (l'aire sous la courbe ROC : la probabilité qu'un client parti ait un score plus élevé qu'un client resté ; 0,5 = hasard, 1 = parfait ; chapitre 5, section 5.1), ce modèle de référence est déjà solide. Voyons maintenant ce qu'il **ne sait pas** faire.

### 2.1.6 Ce qu'un score linéaire ne sait pas écrire

Un score linéaire est une **somme** : chaque variable pousse le résultat dans un sens, indépendamment des autres, et proportionnellement à sa valeur. Il ne peut donc exprimer ni une **interaction** (« le risque explose quand *à la fois* la récence est grande *et* la satisfaction est basse ») ni un **seuil** (« rien ne se passe avant 150 jours, puis tout change »).

L'exemple d'école est le « ou exclusif » (XOR) : la classe dépend du **signe du produit** de deux variables.

```python hide
rng = np.random.default_rng(7)
P = rng.uniform(-1, 1, (600, 2))
cl = ((P[:, 0] * P[:, 1]) > 0).astype(int)
cl = np.where(rng.random(600) < 0.05, 1 - cl, cl)
Ptr, Pte, ctr, cte = train_test_split(P, cl, test_size=0.4, random_state=0, stratify=cl)
auc_xor_lin = roc_auc_score(cte, LogisticRegression().fit(Ptr, ctr).predict_proba(Pte)[:, 1])
aug = lambda M: np.column_stack([M, M[:, 0] * M[:, 1]])
auc_xor_int = roc_auc_score(cte, LogisticRegression().fit(aug(Ptr), ctr).predict_proba(aug(Pte))[:, 1])
NUM("auc_xor_lin", auc_xor_lin); NUM("auc_xor_int", auc_xor_int)
fig, ax = plt.subplots(figsize=(4.8, 4.4))
ax.scatter(P[cl == 0, 0], P[cl == 0, 1], s=14, color=BLEU, alpha=0.75, label="classe 0")
ax.scatter(P[cl == 1, 0], P[cl == 1, 1], s=14, color=ORANGE, alpha=0.75, label="classe 1")
ax.axhline(0, color="#c3c2b7", lw=0.8); ax.axvline(0, color="#c3c2b7", lw=0.8)
ax.set_xlabel("variable 1"); ax.set_ylabel("variable 2"); ax.set_title("Le « ou exclusif »"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=9)
style.save(fig, "ch02-xor.png")
```
<!--sortie-->
```text
NUM auc_xor_lin 0.5026506696428572
NUM auc_xor_int 0.9364536830357143
figure : ch02-xor.png
```

![Deux classes disposées en damier : la classe dépend du signe du produit des deux variables. Aucune droite ne les sépare.](figures/ch02-xor.png)

Une régression logistique sur ces deux variables obtient une AUC de 0,503 : **le hasard**. Aucune droite ne sépare un damier. Pourtant, si l'on **ajoute à la main** la variable « produit » $x_1x_2$, l'AUC passe à 0,936. L'information était là ; c'est la **forme** de la règle qui manquait. Il existe deux réponses : fabriquer à la main les bonnes variables (les interactions, les seuils : c'est l'*ingénierie des variables* du chapitre 4), ou utiliser un modèle capable d'écrire des règles non linéaires **tout seul**. Les arbres sont le premier de ces modèles.

> ✅ **À retenir.**
> - Un modèle supervisé = **famille de fonctions + perte + algorithme**. Le modèle linéaire calcule un score $w^\top x+b$ ; la perte logistique (ou charnière) remplace le coût 0-1, non minimisable.
> - Le gradient de la perte logistique est $\frac1n\sum(p_i-y_i)x_i$ ; la **descente de gradient** (et sa version stochastique, la SGD) le suit pas à pas. Elle exige des variables **à l'échelle** : le conditionnement du problème en dépend.
> - **Pénalité = contrainte** : Ridge (disque) rétrécit, Lasso (losange) met des coefficients à zéro. `C` est l'inverse de la force de pénalisation.
> - Un score linéaire **ne peut exprimer ni interaction ni seuil** ; sur la résiliation, il fournit pourtant une référence honorable (AUC 0,866).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1 (descente de gradient écrite à la main) et application 2.2 (chemins de régularisation), exercices 2.1 à 2.3.
