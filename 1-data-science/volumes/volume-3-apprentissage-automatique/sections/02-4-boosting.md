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

```python hide
from sklearn.ensemble import GradientBoostingRegressor
xb = np.arange(1, 7).reshape(-1, 1); yb = np.array([3, 5, 4, 12, 20, 13.0])
gb2 = GradientBoostingRegressor(n_estimators=2, learning_rate=0.5, max_depth=1, random_state=0).fit(xb, yb)
F = [np.full(6, yb.mean())] + [p for p in gb2.staged_predict(xb)]
tab = pd.DataFrame({"x": xb[:, 0], "y": yb, "F0": F[0], "résidu 1": yb - F[0], "F1": F[1], "résidu 2": yb - F[1], "F2": F[2]})
NUM("F0", F[0][0]); NUM("F1_g", F[1][0]); NUM("F1_d", F[1][5]); NUM("F2_1", F[2][0]); NUM("F2_4", F[2][3]); NUM("F2_5", F[2][4])
NUM("sse_F0", ((yb - F[0]) ** 2).sum()); NUM("sse_F1", ((yb - F[1]) ** 2).sum()); NUM("sse_F2", ((yb - F[2]) ** 2).sum())
NUM("seuil_s1", gb2.estimators_[0, 0].tree_.threshold[0]); NUM("seuil_s2", gb2.estimators_[1, 0].tree_.threshold[0])
gb_long = GradientBoostingRegressor(n_estimators=100, learning_rate=0.5, max_depth=1, random_state=0).fit(xb, yb)
fig, axs = plt.subplots(1, 4, figsize=(11.2, 3.0), sharey=True)
for ax, k in zip(axs, (0, 1, 2, 100)):
    pred = F[0] if k == 0 else (F[k] if k <= 2 else gb_long.predict(xb))
    xs = np.linspace(0.6, 6.4, 300).reshape(-1, 1)
    yl = np.full(300, yb.mean()) if k == 0 else (gb2.predict(xs) if k == 2 else (gb_long.predict(xs) if k == 100 else None))
    if k == 1:
        s0 = gb2.estimators_[0, 0].predict(xs)
        yl = yb.mean() + 0.5 * s0
    ax.scatter(xb[:, 0], yb, color=ORANGE, s=34, zorder=3); ax.step(xs[:, 0], yl, color=BLEU, lw=2.0, where="mid")
    ax.set_title(f"après {k} tour{'s' if k > 1 else ''}", fontsize=10); ax.set_xlabel("$x$")
axs[0].set_ylabel("dépense $y$ (€)")
style.save(fig, "ch02-boosting-main.png")
```
<!--sortie-->
```text
NUM F0 9.5
NUM F1_g 6.75
NUM F1_d 12.25
NUM F2_1 5.6875
NUM F2_4 11.1875
NUM F2_5 14.375
NUM sse_F0 221.5
NUM sse_F1 85.375
NUM sse_F2 44.734375
NUM seuil_s1 3.5
NUM seuil_s2 4.5
figure : ch02-boosting-main.png
```

```python hide-code
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
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

```python hide
g = np.array([-0.5, 0.5, -0.5, -0.5]); hh = np.full(4, 0.25); lam = 1.0
G, Hh = g.sum(), hh.sum()
NUM("w_feuille", -G / (Hh + lam)); NUM("w_newton_sans_reg", -G / Hh)
GG, HG, GD, HD = g[:2].sum(), hh[:2].sum(), g[2:].sum(), hh[2:].sum()
NUM("gain_coupe", 0.5 * (GG ** 2 / (HG + lam) + GD ** 2 / (HD + lam) - (GG + GD) ** 2 / (HG + HD + lam)))
```
<!--sortie-->
```text
NUM w_feuille 0.5
NUM w_newton_sans_reg 1.0
NUM gain_coupe 0.08333333333333331
```

Le calcul est confirmé : la valeur de feuille est 0,50 (1,00 sans régularisation) et le gain de la coupe 0,083. Le régulariseur $\lambda$ **rétrécit** les valeurs de feuilles, surtout pour celles qui reposent sur peu de clients (petit $H_j$) : c'est une protection contre le surapprentissage, intégrée à l'algorithme.

Troisième apport : XGBoost est **rapide**. Il regroupe les valeurs des variables en **histogrammes** (au plus 256 intervalles) : au lieu d'essayer chaque seuil, on n'en essaie que 255, ce qui rend le calcul presque indépendant de $n$.

### 2.4.4 LightGBM et le choix d'une stratégie de croissance

**LightGBM** (Ke et coll., 2017) va plus loin dans la vitesse. Il utilise lui aussi des histogrammes, et ajoute deux idées : la **croissance par feuille** (*leaf-wise*) et l'économie de calcul sur les données. XGBoost (par défaut) fait grandir l'arbre **niveau par niveau** : toutes les feuilles du niveau courant sont coupées, puis celles du niveau suivant. LightGBM coupe à chaque étape **la feuille dont le gain est le plus grand**, où qu'elle soit : l'arbre devient asymétrique, avec parfois une longue branche profonde, et réduit plus vite l'erreur pour un même nombre de feuilles. Le réglage principal n'est donc plus la profondeur mais le **nombre de feuilles** (`num_leaves`), avec un garde-fou sur la taille minimale des feuilles (`min_child_samples`). La version de `scikit-learn`, `HistGradientBoostingClassifier`, reprend cette philosophie et n'exige aucune installation supplémentaire.

Trois précautions communes : (1) le boosting **surapprend si on le laisse tourner**, d'où l'**arrêt précoce** (section suivante) ; (2) il est **sensible au bruit des étiquettes** (il insiste sur les clients mal prédits, même quand c'est du hasard) ; (3) il **n'extrapole pas** : comme tout modèle à base d'arbres, il prédit une valeur constante en dehors du domaine des données d'entraînement.

### 2.4.5 Régler le boosting : pas, nombre d'arbres et arrêt précoce

Le pas $\nu$ et le nombre d'arbres $M$ sont liés : diviser $\nu$ par deux oblige à doubler $M$ pour atteindre un niveau de performance comparable. Plutôt que de choisir $M$ à la main, on prend un $\nu$ petit et l'on **arrête quand la perte de validation cesse de baisser** : c'est l'**arrêt précoce** (*early stopping*). On réserve pour cela une partie de l'entraînement (ici 20 %) comme **jeu de validation**, distinct du jeu de test.

```python hide
import lightgbm as lgb
import xgboost as xgb

Xa, Xv, ya, yv = train_test_split(Xtr_c, ytr, test_size=0.2, stratify=ytr, random_state=1)
courbes = {}
for lr in (0.3, 0.1, 0.03):
    m = lgb.LGBMClassifier(n_estimators=700, learning_rate=lr, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                           n_jobs=1, random_state=0, verbose=-1)
    m.fit(Xa, ya, eval_set=[(Xv, yv)], eval_metric="binary_logloss")
    courbes[lr] = np.array(m.evals_result_["valid_0"]["binary_logloss"])
fig, ax = plt.subplots(figsize=(7.2, 3.9))
for lr, col in ((0.3, ROUGE), (0.1, ORANGE), (0.03, BLEU)):
    c = courbes[lr]; k = int(c.argmin())
    ax.plot(np.arange(1, len(c) + 1), c, color=col, lw=2.0, label=f"pas {str(lr).replace('.', ',')} : minimum à {k + 1} arbres")
    ax.plot(k + 1, c[k], "o", color=col, ms=6)
    NUM(f"best_iter_{str(lr).replace('.', '')}", k + 1); NUM(f"best_loss_{str(lr).replace('.', '')}", c[k])
ax.set_xlabel("nombre d'arbres"); ax.set_ylabel("perte logistique sur la validation"); ax.set_ylim(0.24, 0.40); ax.legend(frameon=False, loc="upper right", fontsize=9)
ax.set_title("Un pas plus petit demande plus d'arbres, et l'on s'arrête au minimum")
style.save(fig, "ch02-boosting-pas-arbres.png")
```
<!--sortie-->
```text
NUM best_iter_03 16
NUM best_loss_03 0.2612117256916711
NUM best_iter_01 57
NUM best_loss_01 0.24895201681593074
NUM best_iter_003 246
NUM best_loss_003 0.250046488502416
figure : ch02-boosting-pas-arbres.png
```

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

```python hide
xg = xgb.XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8, enable_categorical=True,
                       early_stopping_rounds=30, eval_metric="logloss", n_jobs=1, random_state=0).fit(Xa, ya, eval_set=[(Xv, yv)], verbose=False)
lg = lgb.LGBMClassifier(n_estimators=1000, learning_rate=0.05, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=1,
                        random_state=0, verbose=-1).fit(Xa, ya, eval_set=[(Xv, yv)], callbacks=[lgb.early_stopping(30, verbose=False)])
p_xg, p_lg = xg.predict_proba(Xte_c)[:, 1], lg.predict_proba(Xte_c)[:, 1]
NUM("diff_xl", abs(roc_auc_score(yte, p_lg) - roc_auc_score(yte, p_xg))); NUM("iter_xgb", xg.best_iteration); NUM("auc_xgb", roc_auc_score(yte, p_xg)); NUM("iter_lgb", lg.best_iteration_); NUM("auc_lgb", roc_auc_score(yte, p_lg))
```
<!--sortie-->
```text
NUM diff_xl 0.004420870561515078
NUM iter_xgb 227
NUM auc_xgb 0.898176298791905
NUM iter_lgb 198
NUM auc_lgb 0.90259716935342
```

Les deux bibliothèques s'arrêtent après 227 (XGBoost) et 198 (LightGBM) arbres et obtiennent respectivement des AUC de test de 0,898 et 0,903 : des valeurs voisines (la différence de 0,004 vient des détails d'implémentation : croissance par niveau ou par feuille, histogrammes, traitement des catégories), car l'algorithme de fond est le même. Les autres réglages usuels, avec leurs ordres de grandeur : profondeur 3 à 8 (XGBoost) ou 15 à 63 feuilles (LightGBM) ; taille minimale des feuilles ; `subsample` et `colsample_bytree` de 0,5 à 1 ; régularisation $\lambda$ de 0 à 10. Le chapitre 1 (section 1.5, ➕) présente les méthodes pour les chercher de façon systématique.

### 2.4.6 Valeurs manquantes et catégories : sans artifice

Les modèles à base d'arbres modernes traitent **nativement** deux difficultés qui occupent un modèle linéaire : les valeurs manquantes et les catégories à nombreuses modalités.

- **Valeurs manquantes.** À chaque coupe, XGBoost, LightGBM et `HistGradientBoostingClassifier` **apprennent** vers quel côté envoyer les clients dont la valeur manque, en choisissant la direction qui réduit le plus la perte. Pas d'imputation : et le **fait d'être manquant**, souvent informatif (ici la satisfaction manque plus souvent quand elle est basse), est exploité directement.
- **Catégories.** Une variable comme `ville` (20 modalités) donnerait 20 colonnes en encodage par indicatrices. LightGBM et `HistGradientBoostingClassifier` cherchent directement, pour une variable catégorielle, **le meilleur partage des modalités en deux ensembles**.

```python hide
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer

def hgb(): return HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, early_stopping=True, validation_fraction=0.15, n_iter_no_change=20, random_state=0)
auc = lambda m, A, B: roc_auc_score(yte, m.fit(A, ytr).predict_proba(B)[:, 1])
a_natif = auc(hgb().set_params(categorical_features="from_dtype"), Xtr_c, Xte_c)
imp = SimpleImputer(strategy="median"); numeric_cols = num
Xtr_i, Xte_i = Xtr_o.copy(), Xte_o.copy()
Xtr_i[numeric_cols] = imp.fit_transform(Xtr_o[numeric_cols]); Xte_i[numeric_cols] = imp.transform(Xte_o[numeric_cols])
a_imput = auc(hgb(), Xtr_i, Xte_i)
a_onehot = auc(hgb(), Xtr_o, Xte_o)
Xtr_k, Xte_k = Xtr.copy(), Xte.copy()
for c_ in cat:
    codes = {v: k for k, v in enumerate(sorted(Xtr[c_].dropna().unique()))}
    Xtr_k[c_], Xte_k[c_] = Xtr[c_].map(codes), Xte[c_].map(codes)
a_ordinal = auc(hgb(), Xtr_k, Xte_k)
for k, v in (("nat", a_natif), ("imput", a_imput), ("onehot", a_onehot), ("ordinal", a_ordinal)): NUM(f"auc_miss_{k}", v)
NUM("ecart_miss", max(a_natif, a_imput, a_onehot, a_ordinal) - min(a_natif, a_imput, a_onehot, a_ordinal))
```
<!--sortie-->
```text
NUM auc_miss_nat 0.9025142780303917
NUM auc_miss_imput 0.9018824619459752
NUM auc_miss_onehot 0.9017949655494452
NUM auc_miss_ordinal 0.9012506458615586
NUM ecart_miss 0.0012636321688331842
```

```python hide-code
print(pd.DataFrame({"traitement": ["natif (NaN gardés, catégories natives)", "NaN gardés, catégories en indicatrices", "NaN gardés, catégories en codes entiers", "médiane à la place des NaN, catégories en indicatrices"],
                    "AUC test": [a_natif, a_onehot, a_ordinal, a_imput]}).round(4).to_string(index=False))
```
<!--sortie-->
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

```python hide
from sklearn.model_selection import cross_val_score

modeles = {
    "régression logistique": (make_pipeline(pre_lin, LogisticRegression(C=0.3, max_iter=1000)), Xtr, Xte),
    "arbre (profondeur choisie)": (DecisionTreeClassifier(max_depth=d_opt, min_samples_leaf=5, random_state=0), Xtr_o, Xte_o),
    "forêt aléatoire": (RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_features="sqrt", n_jobs=1, random_state=0), Xtr_o, Xte_o),
    "gradient boosting": (HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, early_stopping=True, validation_fraction=0.15, n_iter_no_change=20,
                                                          categorical_features="from_dtype", random_state=0), Xtr_c, Xte_c),
}
cv_scores, test_p = {}, {}
for nom, (m, A, B) in modeles.items():
    cv_scores[nom] = cross_val_score(m, A, ytr, cv=cv5, scoring="roc_auc")
    test_p[nom] = m.fit(A, ytr).predict_proba(B)[:, 1]
resu = pd.DataFrame({"modèle": list(modeles), "AUC validation croisée (moyenne)": [cv_scores[k].mean() for k in modeles],
                     "écart-type entre plis": [cv_scores[k].std() for k in modeles], "AUC test": [roc_auc_score(yte, test_p[k]) for k in modeles],
                     "perte logistique test": [log_loss(yte, np.clip(test_p[k], 1e-4, 1 - 1e-4)) for k in modeles]})
for k, nom in zip(("lr", "arbre", "foret", "boost"), modeles):
    NUM(f"cmp_cv_{k}", cv_scores[nom].mean()); NUM(f"cmp_sd_{k}", cv_scores[nom].std()); NUM(f"cmp_test_{k}", roc_auc_score(yte, test_p[nom])); NUM(f"cmp_ll_{k}", resu.loc[resu['modèle'] == nom, 'perte logistique test'].iloc[0])
dif_plis = cv_scores["gradient boosting"] - cv_scores["régression logistique"]
NUM("dif_plis_moy", dif_plis.mean()); NUM("dif_plis_min", dif_plis.min()); NUM("dif_plis_max", dif_plis.max())
# bootstrap apparié sur le jeu de test : on rééchantillonne les MÊMES clients pour les deux modèles
rng = np.random.default_rng(42); n_t = len(yte); yv_ = yte.to_numpy()
def boot_diff(a, b, B=400):
    d = []
    for _ in range(B):
        i = rng.integers(0, n_t, n_t); d.append(roc_auc_score(yv_[i], test_p[a][i]) - roc_auc_score(yv_[i], test_p[b][i]))
    return np.percentile(d, [2.5, 97.5]), float(np.mean(d))
(ic_bl, m_bl) = boot_diff("gradient boosting", "régression logistique"); (ic_bf, m_bf) = boot_diff("gradient boosting", "forêt aléatoire"); (ic_fl, m_fl) = boot_diff("forêt aléatoire", "régression logistique")
NUM("bl_lo", ic_bl[0]); NUM("bl_hi", ic_bl[1]); NUM("bl_m", m_bl); NUM("bf_lo", ic_bf[0]); NUM("bf_hi", ic_bf[1]); NUM("bf_m", m_bf); NUM("fl_lo", ic_fl[0]); NUM("fl_hi", ic_fl[1]); NUM("fl_m", m_fl)
fig, ax = plt.subplots(figsize=(7.4, 3.8))
noms = list(modeles)[::-1]
for i, nom in enumerate(noms):
    ax.errorbar(cv_scores[nom].mean(), i, xerr=cv_scores[nom].std(), fmt="o", color=BLEU, capsize=4, ms=7, lw=1.8)
    ax.plot(roc_auc_score(yte, test_p[nom]), i, "D", color=ORANGE, ms=7)
ax.set_yticks(range(len(noms))); ax.set_yticklabels(noms); ax.set_xlabel("AUC")
ax.set_title("Quatre familles, mêmes données : validation croisée (± 1 écart-type) et test")
ax.plot([], [], "o", color=BLEU, label="validation croisée (5 plis)"); ax.plot([], [], "D", color=ORANGE, label="jeu de test"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, fontsize=9)
style.save(fig, "ch02-comparaison-modeles.png")
```
<!--sortie-->
```text
NUM cmp_cv_lr 0.8604952187606483
NUM cmp_sd_lr 0.00976691303196902
NUM cmp_test_lr 0.8659260480456529
NUM cmp_ll_lr 0.281619361166037
NUM cmp_cv_arbre 0.8630064145279306
NUM cmp_sd_arbre 0.0065562797967407115
NUM cmp_test_arbre 0.8846884990131328
NUM cmp_ll_arbre 0.2584057980041127
NUM cmp_cv_foret 0.8856381691177188
NUM cmp_sd_foret 0.008547343755860241
NUM cmp_test_foret 0.896308480979665
NUM cmp_ll_foret 0.26076026403624336
NUM cmp_cv_boost 0.890040519139282
NUM cmp_sd_boost 0.007714006266178971
NUM cmp_test_boost 0.9025142780303917
NUM cmp_ll_boost 0.24373326413122975
NUM dif_plis_moy 0.029545300378633742
NUM dif_plis_min 0.0204961279130077
NUM dif_plis_max 0.03459200645901439
NUM bl_lo 0.024526955942610226
NUM bl_hi 0.04874745812343218
NUM bl_m 0.036596826728586745
NUM bf_lo -0.0008815001168591376
NUM bf_hi 0.013776925431040175
NUM bf_m 0.006168714765503391
NUM fl_lo 0.02137125880847495
NUM fl_hi 0.041793330933795454
NUM fl_m 0.03044933357355249
figure : ch02-comparaison-modeles.png
```

```python hide-code
print(resu.round(4).to_string(index=False))
```
<!--sortie-->
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
