## 5.5 ➕ Pour aller plus loin : quantifier l'incertitude, la prédiction conforme

> 🧭 **Section optionnelle.** Elle prolonge 5.2 (calibration) et 5.1.10 (prédire un quantile).

Un modèle de classification annonce « 62 % de risque de départ ». Un modèle de régression annonce « 83 € de dépense ». Dans les deux cas, **le modèle ne dit pas à quel point il peut se tromper**. La calibration (5.2) répare les probabilités, mais seulement approximativement, et sous l'hypothèse que la recalibration est bonne. La **prédiction conforme** (*conformal prediction*) propose autre chose : transformer *n'importe quel* modèle déjà ajusté en un modèle qui annonce non pas une valeur, mais un **ensemble** (en classification) ou un **intervalle** (en régression), avec une **garantie** de couverture valable à distance finie, sans hypothèse sur la loi des données.

### 5.5.1 L'objectif : une garantie de couverture

On se donne un niveau d'erreur $\alpha$ (par exemple $0{,}10$). On veut, pour un nouveau client, un ensemble $C(x)$ de réponses plausibles tel que
$$P\bigl(Y\in C(X)\bigr)\ \ge\ 1-\alpha.$$
En classification, $C(x)$ est un sous-ensemble des classes ({fidèle}, {partant}, ou les deux). En régression, c'est un intervalle $[\ell(x),u(x)]$. Cette probabilité porte sur le tirage du client *et* du jeu de calibration : on parle de **couverture marginale**.

### 5.5.2 La recette : la prédiction conforme « séparée »

La version la plus simple, dite **split conformal**, utilise trois jeux (ceux du fil rouge) : l'entraînement (pour ajuster le modèle), la **calibration** (pour mesurer ses erreurs), et le test (pour vérifier).

1. On ajuste le modèle sur le jeu d'entraînement.
2. On définit un **score de non-conformité** $s(x,y)$, qui est grand quand le couple $(x,y)$ est « surprenant » pour le modèle. En classification, on prend $s(x,y)=1-\hat p_y(x)$ : un moins la probabilité que le modèle attribuait à la **vraie** classe.
3. On calcule ce score pour chacun des $n$ clients du jeu de calibration, et l'on prend son **quantile** d'ordre $\lceil(n+1)(1-\alpha)\rceil/n$ : le $k$-ième plus petit score, avec $k=\lceil(n+1)(1-\alpha)\rceil$. Notons-le $\hat q$.
4. Pour un nouveau client, l'ensemble prédit est $C(x)=\{y:\ s(x,y)\le\hat q\}$ : toutes les classes dont le score ne dépasse pas $\hat q$.

**Un exemple à la main.** Neuf clients de calibration ($n=9$), $\alpha=0{,}20$. Leurs scores, triés : 0,05 ; 0,10 ; 0,14 ; 0,22 ; 0,31 ; 0,38 ; 0,47 ; 0,55 ; 0,71. On a $k=\lceil10\times0{,}8\rceil=8$ : $\hat q$ est le 8ᵉ score, **0,55**. Un client dont le modèle annonce $\hat p_{\text{partant}}=0{,}62$ donne le score $0{,}38$ pour la classe « partant » et $0{,}62$ pour « fidèle ». L'ensemble est $\{y:s\le0{,}55\}=\{\text{partant}\}$. Un autre client avec $\hat p_{\text{partant}}=0{,}48$ donne $0{,}52$ et $0{,}48$ : les deux sont $\le0{,}55$, l'ensemble est {fidèle, partant} : le modèle **avoue son hésitation**.

Appliquons cela aux 2 400 clients de calibration et au gradient boosting du chapitre, avec $\alpha=0{,}10$ :

```python hide
from sklearn.ensemble import HistGradientBoostingRegressor
alpha = 0.10
def q_conf(s, alpha):
    """k-ième plus petit score, k = ⌈(n+1)(1-α)⌉ (infini si k > n) : exactement la règle de la démonstration."""
    s = np.sort(s); k = int(np.ceil((len(s) + 1) * (1 - alpha)))
    return float(s[k - 1]) if k <= len(s) else float("inf")
y5c = yte.to_numpy(); ycal = yca.to_numpy()
pcal = gb.predict_proba(Xca); ptest = gb.predict_proba(Xte)
# --- LAC : score = 1 - probabilité de la vraie classe
s_cal = 1 - pcal[np.arange(len(ycal)), ycal]
n_cal = len(s_cal); niveau = np.ceil((n_cal + 1) * (1 - alpha)) / n_cal
qhat = q_conf(s_cal, alpha)
ens = (1 - ptest) <= qhat
couv = ens[np.arange(len(y5c)), y5c]; taille = ens.sum(axis=1)
print("n calibration", n_cal, "| niveau du quantile", round(niveau, 4), "| qhat", round(qhat, 4), "-> un ensemble contient la classe k si p_k >=", round(1 - qhat, 4))
print("couverture globale", round(float(couv.mean()), 4), "| couverture si départ", round(float(couv[y5c == 1].mean()), 4), "| si fidèle", round(float(couv[y5c == 0].mean()), 4))
print("répartition des ensembles : vide", round(float((taille == 0).mean()), 3), "| un seul élément", round(float((taille == 1).mean()), 3), "| {fidèle, départ}", round(float((taille == 2).mean()), 3))
# --- Mondrian : un quantile par classe
qk = {}
for k in (0, 1):
    sk = s_cal[ycal == k]; nk = len(sk); qk[k] = q_conf(sk, alpha)
ens_m = np.column_stack([(1 - ptest[:, 0]) <= qk[0], (1 - ptest[:, 1]) <= qk[1]])
cm = ens_m[np.arange(len(y5c)), y5c]
print("Mondrian : couverture si départ", round(float(cm[y5c == 1].mean()), 4), "| si fidèle", round(float(cm[y5c == 0].mean()), 4), "| taille moyenne", round(float(ens_m.sum(axis=1).mean()), 3), "(LAC :", round(float(taille.mean()), 3), ")")
# --- APS randomisé (cas binaire)
rng = np.random.default_rng(0)
def aps_scores(p, U):
    top = p.argmax(axis=1); ptop = p.max(axis=1); pmin = 1 - ptop
    s = np.empty_like(p); s[np.arange(len(p)), top] = U * ptop; s[np.arange(len(p)), 1 - top] = ptop + U * pmin
    return s
Ucal = rng.random(len(ycal)); Ute = rng.random(len(y5c))
sc_ = aps_scores(pcal, Ucal)[np.arange(len(ycal)), ycal]
qa = q_conf(sc_, alpha); ens_a = aps_scores(ptest, Ute) <= qa
print("APS : couverture", round(float(ens_a[np.arange(len(y5c)), y5c].mean()), 4), "| taille moyenne", round(float(ens_a.sum(axis=1).mean()), 3), "| vide", round(float((ens_a.sum(axis=1) == 0).mean()), 3))
```
<!--sortie-->
```text
n calibration 2400 | niveau du quantile 0.9004 | qhat 0.5221 -> un ensemble contient la classe k si p_k >= 0.4779
couverture globale 0.9025 | couverture si départ 0.4955 | si fidèle 0.969
répartition des ensembles : vide 0.0 | un seul élément 0.994 | {fidèle, départ} 0.006
Mondrian : couverture si départ 0.9021 | si fidèle 0.9157 | taille moyenne 1.213 (LAC : 1.006 )
APS : couverture 0.9 | taille moyenne 1.107 | vide 0.045
```

```python
scores_cal = 1 - pcal[np.arange(len(ycal)), ycal]       # non-conformité : 1 - probabilité de la VRAIE classe, sur le jeu de calibration
k = int(np.ceil((len(scores_cal) + 1) * (1 - alpha)))   # rang du quantile : ⌈(n + 1)(1 - α)⌉
q = np.sort(scores_cal)[k - 1]                          # le k-ième plus petit score
ensembles = (1 - ptest) <= q                            # pour chaque client de test : les classes dont le score est <= q
couvert = ensembles[np.arange(len(y5c)), y5c]           # la vraie classe est-elle dans l'ensemble ?
print("k =", k, "sur", len(scores_cal), "| q =", round(q, 4), "| couverture :", round(couvert.mean(), 4))
```
<!--sortie-->
```text
k = 2161 sur 2400 | q = 0.5221 | couverture : 0.9025
```

C'est le 2 161ᵉ plus petit des 2 400 scores ($k=\lceil2401\times0{,}9\rceil=2\,161$) : $\hat q=0{,}5221$. Un client reçoit la classe $k$ dans son ensemble si la probabilité de cette classe est au moins $1-0{,}5221=0{,}4779$. En classification binaire, cela revient à dire : **si la probabilité de départ est comprise entre 0,478 et 0,522, on répond « les deux » ; sinon, on répond une seule classe**. Sur le jeu de test, 99,4 % des clients reçoivent une réponse unique, et 0,6 % reçoivent les deux ; la **couverture globale vaut 0,9025**, conforme à l'objectif de 90 %.

### 5.5.3 Pourquoi cela marche

La garantie est étonnamment simple à démontrer. Elle ne suppose **ni** que le modèle est bon, **ni** que les probabilités sont calibrées, **ni** une loi particulière : seulement que les données de calibration et le nouveau client sont **échangeables** (par exemple, tirés indépendamment de la même population).

> 📐 **Théorème (couverture du « split conformal »).** Soient $(X_i,Y_i)$, $i=1,\dots,n+1$, échangeables, et $s_i=s(X_i,Y_i)$ les scores calculés avec un modèle fixé indépendamment d'eux. Soit $\hat q$ le $k$-ième plus petit des $n$ scores de calibration, $k=\lceil(n+1)(1-\alpha)\rceil$ (par convention $\hat q=+\infty$ si $k>n$). Alors
> $$1-\alpha\ \le\ P\bigl(s_{n+1}\le\hat q\bigr)\ \le\ 1-\alpha+\frac1{n+1}\quad\text{(borne supérieure : si les scores sont presque sûrement distincts).}$$
>
> *Démonstration.* L'événement $\{s_{n+1}\le\hat q\}$ signifie que $s_{n+1}$ est au plus égal au $k$-ième plus petit des $n$ scores de calibration, c'est-à-dire que le **rang** de $s_{n+1}$ parmi les $n+1$ scores est au plus $k$. Par échangeabilité, les $n+1$ scores jouent des rôles symétriques : si les scores sont tous distincts, le rang de $s_{n+1}$ est **uniforme** sur $\{1,\dots,n+1\}$. La probabilité vaut donc $\dfrac{k}{n+1}=\dfrac{\lceil(n+1)(1-\alpha)\rceil}{n+1}\in\Bigl[1-\alpha,\ 1-\alpha+\dfrac1{n+1}\Bigr)$. S'il y a des égalités, le rang n'est plus uniforme mais $P(\text{rang}\le k)\ge\dfrac{k}{n+1}$, et la borne inférieure subsiste. $\blacksquare$

Remarquez ce que la démonstration n'utilise pas : le modèle, la calibration, la loi des données. Plus le modèle est bon, plus les ensembles sont **petits** ; mais la couverture, elle, est garantie quel que soit le modèle.

**La garantie, vue par simulation.** La couverture garantie est une moyenne sur le tirage du jeu de calibration : pour *un* jeu de calibration donné, la couverture réelle fluctue. On peut même dire comment : elle suit une **loi Bêta**$(k,\,n+1-k)$. Pour le voir, on mélange 1 000 fois les 4 800 clients des jeux de calibration et de test, on prend à chaque fois 300 clients pour calibrer et l'on mesure la couverture sur les 4 500 autres.

```python hide
# --- la garantie vue par simulation : 1 000 découpages aléatoires (n = 300 en calibration)
pool_p = np.vstack([pcal, ptest]); pool_y = np.concatenate([ycal, y5c]); pool_s = 1 - pool_p[np.arange(len(pool_y)), pool_y]
rng = np.random.default_rng(1); couvs = []; n_ = 300
for _ in range(1000):
    perm = rng.permutation(len(pool_s)); cal, tst = perm[:n_], perm[n_:]
    q = q_conf(pool_s[cal], alpha); couvs.append(float((pool_s[tst] <= q).mean()))
couvs = np.array(couvs); l_ = int(np.floor((n_ + 1) * alpha)); a_, b_ = n_ + 1 - l_, l_
from scipy.stats import beta as beta_
print("simulation : couverture moyenne", round(couvs.mean(), 4), "écart-type", round(couvs.std(), 4), "min", round(couvs.min(), 4), "max", round(couvs.max(), 4),
      "| théorie Beta(", a_, ",", b_, ") : moyenne", round(a_ / (a_ + b_), 4), "écart-type", round(float(beta_.std(a_, b_)), 4), "| bornes garanties : [", 1 - alpha, ",", round(1 - alpha + 1 / (n_ + 1), 4), "]")
fig, ax = plt.subplots(figsize=(7, 4)); ax.hist(couvs, bins=30, density=True, color="#2a78d6", alpha=0.65)
xs = np.linspace(couvs.min(), couvs.max(), 300); ax.plot(xs, beta_.pdf(xs, a_, b_), color="#eb6834", lw=2); ax.axvline(1 - alpha, color="#898781", ls="--", lw=1)
ax.text(1 - alpha + 0.002, 1.5, "objectif 90 %", color="#898781", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=1.5)); ax.text(xs[0], beta_.pdf(xs[0] + 0.06, a_, b_), "loi Bêta théorique", color="#eb6834", fontsize=9)
ax.set_xlabel("couverture sur le jeu de test (un point par découpage)"); ax.set_ylabel("densité"); ax.set_title("La couverture fluctue, mais autour de 90 %")
plt.tight_layout(); plt.savefig("figures/ch05-conforme-couverture.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
simulation : couverture moyenne 0.9003 écart-type 0.0177 min 0.8411 max 0.9447 | théorie Beta( 271 , 30 ) : moyenne 0.9003 écart-type 0.0172 | bornes garanties : [ 0.9 , 0.9033 ]
```

![Couverture sur le jeu de test pour 1 000 découpages aléatoires (300 clients de calibration à chaque fois), et densité de la loi Bêta théorique. La couverture fluctue, mais autour de 90 %.](figures/ch05-conforme-couverture.png)

Ici $n=300$ et $k=\lceil301\times0{,}9\rceil=271$ : la théorie donne une loi Bêta(271 ; 30), de moyenne $0{,}9003$ et d'écart-type $0{,}0172$. La simulation donne une moyenne de **0,9003** et un écart-type de **0,0177**, avec des couvertures allant de 0,841 à 0,945. La moyenne coïncide avec la théorie (0,9003, dans l'intervalle garanti $[0{,}9\,;\,0{,}9033]$) et l'écart-type est proche de 0,0172. La théorie décrit fidèlement l'expérience.

> 💡 **Combien de clients de calibration ?** Avec $n=300$, la couverture réelle d'un jeu de calibration donné peut tomber à 85 % ou monter à 94 % (± deux écarts-types : ±3,5 points). Avec $n=2\,400$, l'écart-type est de l'ordre de $0{,}006$. La garantie est valide pour tout $n$, mais plus $n$ est grand, plus la couverture *réelle* se rapproche de la couverture *annoncée*.

### 5.5.4 Garantie marginale, pas conditionnelle

Voici la nuance qui se perd le plus souvent. Calculons la couverture **séparément** pour chaque classe réelle :

| | Couverture | Taille moyenne de l'ensemble |
|---|---:|---:|
| **Globale** | 0,9025 | 1,006 |
| Parmi les clients qui **partent** | **0,4955** | |
| Parmi les clients qui restent | 0,969 | |

La couverture globale est de 90 %, mais elle est de **49,6 % seulement pour les clients qui partent**, ceux qui nous intéressent. Comment est-ce possible ? La garantie est *marginale* : elle moyenne sur tous les clients. Or 86 % des clients restent, et le modèle les couvre à 97 % ; cela suffit à atteindre 90 % en moyenne, même en laissant à découvert un partant sur deux. C'est l'analogue, en prédiction d'ensembles, du piège de l'exactitude de 5.1.2.

**Le remède : la prédiction conforme de Mondrian (conditionnelle à la classe).** On calcule un quantile **par classe** (en n'utilisant que les clients de calibration de cette classe). La garantie devient valable *dans chaque classe* :

| | LAC (global) | Mondrian |
|---|---:|---:|
| Couverture parmi les partants | 0,4955 | **0,9021** |
| Couverture parmi les fidèles | 0,969 | 0,9157 |
| Taille moyenne des ensembles | 1,006 | 1,213 |

Le prix : des ensembles plus gros (en moyenne 1,21 classe au lieu de 1,01), c'est-à-dire plus d'hésitations affichées. C'est normal : on ne peut pas être à la fois sûr de couvrir les partants à 90 % et de rester précis, avec un modèle dont l'AUC est de 0,90.

Il existe d'autres scores de non-conformité. Le score **APS** (*adaptive prediction sets*) cumule les probabilités des classes par ordre décroissant ; avec une petite part d'aléa, il donne ici une couverture de 0,900 et une taille moyenne de 1,107, avec 4,5 % d'ensembles vides. On note que le choix du score est un compromis entre taille des ensembles et homogénéité de la couverture.

### 5.5.5 En régression : des intervalles avec garantie

Le même principe s'applique à une cible numérique, ici la dépense à six mois. Le score est l'**erreur absolue** $s(x,y)=\lvert y-\hat f(x)\rvert$, et l'intervalle est $[\hat f(x)-\hat q,\ \hat f(x)+\hat q]$ (borné par zéro, une dépense ne pouvant être négative).

```python hide
# --- régression conforme : dépense à 6 mois
yr = c["depense_6m"]; ytr_r, ycal_r, yte_r = yr.loc[Xtr.index].to_numpy(), yr.loc[Xca.index].to_numpy(), yr.loc[Xte.index].to_numpy()
reg5 = HistGradientBoostingRegressor(max_iter=150, random_state=0).fit(Xtr, ytr_r)
res_cal = np.abs(ycal_r - reg5.predict(Xca)); nr = len(res_cal)
q_r = q_conf(res_cal, alpha)
mu_te = reg5.predict(Xte); lo, hi = np.maximum(mu_te - q_r, 0), mu_te + q_r
ok = (yte_r >= lo) & (yte_r <= hi)
tert = pd.qcut(mu_te, 3, labels=["prévision basse", "prévision moyenne", "prévision haute"])
print("intervalle absolu : demi-largeur", round(q_r, 2), "| couverture", round(float(ok.mean()), 4), "| largeur moyenne", round(float((hi - lo).mean()), 2))
print("couverture par tercile de prévision :", {t: round(float(ok[(tert == t)].mean()), 3) for t in tert.categories}, "| zéros :", round(float(ok[yte_r == 0].mean()), 3), "| dépenses > 0 :", round(float(ok[yte_r > 0].mean()), 3))
# --- CQR : régression quantile conformalisée
gl = HistGradientBoostingRegressor(loss="quantile", quantile=alpha / 2, max_iter=150, random_state=0).fit(Xtr, ytr_r)
gh = HistGradientBoostingRegressor(loss="quantile", quantile=1 - alpha / 2, max_iter=150, random_state=0).fit(Xtr, ytr_r)
lo_c, hi_c = gl.predict(Xca), gh.predict(Xca)
E = np.maximum(lo_c - ycal_r, ycal_r - hi_c); q_c = q_conf(E, alpha)
lo2, hi2 = np.maximum(gl.predict(Xte) - q_c, 0), gh.predict(Xte) + q_c; ok2 = (yte_r >= lo2) & (yte_r <= hi2)
print("CQR : correction", round(q_c, 4), "| couverture", round(float(ok2.mean()), 4), "| largeur moyenne", round(float((hi2 - lo2).mean()), 2))
print("couverture par tercile :", {t: round(float(ok2[(tert == t)].mean()), 3) for t in tert.categories}, "| zéros :", round(float(ok2[yte_r == 0].mean()), 3), "| > 0 :", round(float(ok2[yte_r > 0].mean()), 3),
      "| largeur par tercile :", {t: round(float((hi2 - lo2)[(tert == t)].mean()), 1) for t in tert.categories})
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2)); o = np.argsort(mu_te)[::24]
for a, (l_, h_, tt) in zip(ax, [(lo, hi, "Intervalles à largeur constante"), (lo2, hi2, "Régression quantile conformalisée (CQR)")]):
    a.fill_between(np.arange(len(o)), l_[o], h_[o], color="#2a78d6", alpha=0.25); a.plot(np.arange(len(o)), mu_te[o], color="#2a78d6", lw=1.2); a.plot(np.arange(len(o)), yte_r[o], ".", color="#eb6834", ms=5)
    a.set_title(tt, fontsize=10); a.set_xlabel("clients triés par dépense prévue"); a.set_ylabel("dépense à 6 mois (€)"); a.set_ylim(-5, 400)
plt.tight_layout(); plt.savefig("figures/ch05-conforme-regression.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
intervalle absolu : demi-largeur 142.44 | couverture 0.9096 | largeur moyenne 210.1
couverture par tercile de prévision : {'prévision basse': 0.994, 'prévision moyenne': 0.975, 'prévision haute': 0.76} | zéros : 0.935 | dépenses > 0 : 0.895
CQR : correction 0.0 | couverture 0.9104 | largeur moyenne 185.35
couverture par tercile : {'prévision basse': 0.922, 'prévision moyenne': 0.916, 'prévision haute': 0.892} | zéros : 1.0 | > 0 : 0.86 | largeur par tercile : {'prévision basse': 74.1, 'prévision moyenne': 138.1, 'prévision haute': 343.9}
```

Avec $\alpha=0{,}10$, la demi-largeur est de $\hat q=142{,}4$ €. La couverture sur le jeu de test vaut **0,910**, conforme à la garantie. Mais le défaut est immédiat : **la largeur est la même pour tous les clients**, qu'ils soient de petits ou de gros dépensiers. Séparons les clients en trois tiers selon la dépense prévue :

| Tiers de la dépense prévue | Couverture (intervalle de largeur constante) | Couverture (CQR) | Largeur moyenne CQR |
|---|---:|---:|---:|
| Prévision basse | 0,994 | 0,922 | 74 € |
| Prévision moyenne | 0,975 | 0,916 | 138 € |
| Prévision haute | **0,760** | 0,892 | 344 € |

Les intervalles de largeur constante sont **trop larges** pour les petits clients (couverture de 99 %, soit un gaspillage de précision) et **trop étroits** pour les gros (76 %, bien en dessous de l'objectif). On préfère des intervalles qui s'adaptent. La **régression quantile conformalisée** (CQR) en offre un moyen : on entraîne d'abord deux modèles de régression quantile (aux niveaux 5 % et 95 %, avec la perte pinball de 5.1.10), qui fournissent un intervalle $[\hat\ell(x),\hat u(x)]$ de largeur variable. Mais, on l'a vu en 5.1.10, un quantile estimé n'a aucune garantie. On corrige donc par conformalisation : le score est $s(x,y)=\max\bigl(\hat\ell(x)-y,\ y-\hat u(x)\bigr)$ (négatif quand $y$ est dans l'intervalle), et l'intervalle final est $[\hat\ell(x)-\hat q,\ \hat u(x)+\hat q]$.

Ici, la correction est **exactement nulle** ($\hat q=0$) : les deux modèles quantiles couvraient déjà 90 % des clients de calibration. (Avec 36 % de clients à dépense nulle, le modèle du quantile à 5 % prédit exactement 0 pour beaucoup d'entre eux, et leur score de non-conformité est exactement 0.) La couverture est de **0,910**, la largeur moyenne de **185 €** (contre 210 € pour l'intervalle constant : des intervalles *plus courts* à couverture égale), et les couvertures par tiers sont beaucoup plus homogènes (0,92 ; 0,92 ; 0,89). La largeur s'adapte : 74 € pour les clients peu dépensiers, 344 € pour les gros.

![Intervalles à 90 % pour un client sur 24 trié par dépense prévue : largeur constante (à gauche) et CQR (à droite). Les points orange sont les dépenses réelles.](figures/ch05-conforme-regression.png)

### 5.5.6 Limites et bonnes pratiques

- **La couverture reste marginale.** Même avec CQR, la couverture parmi les clients dont la dépense est strictement positive n'est que de 0,860 (les 36 % de clients qui ne dépensent rien sont couverts à 100 % et relèvent la moyenne). Une garantie *conditionnelle* à un sous-groupe demande de calibrer sur ce sous-groupe (comme Mondrian) ou des méthodes plus avancées.
- **L'échangeabilité est une vraie hypothèse.** Si les clients de demain ne ressemblent pas à ceux de la calibration (changement de saison, de population), la garantie tombe. Surveillez la couverture empirique en production, et recalibrez.
- **La garantie ne remplace pas un bon modèle.** Un mauvais modèle donne des ensembles énormes ou des intervalles très larges : ils sont valides, mais inutiles. La largeur moyenne est donc, en soi, une mesure de qualité.
- **Il faut des données de calibration** (quelques centaines au minimum) que l'on ne peut pas réutiliser pour l'entraînement. La variante *cross-conformal* ou *jackknife+* évite de sacrifier des données, au prix d'un calcul plus lourd.

> ✅ **À retenir.**
> - La prédiction conforme transforme **n'importe quel modèle** en un modèle qui annonce un **ensemble** ou un **intervalle** avec une couverture garantie $\ge1-\alpha$.
> - Recette : un score de non-conformité, son quantile d'ordre $\lceil(n+1)(1-\alpha)\rceil/n$ sur un jeu de calibration séparé, puis l'ensemble $\{y:s(x,y)\le\hat q\}$.
> - La preuve ne demande que l'**échangeabilité** : le rang d'un score parmi $n+1$ est uniforme.
> - La garantie est **marginale** : elle peut cacher une couverture très faible pour une classe rare (49,6 % pour les partants !) ; la version de **Mondrian** la rend valable par classe.
> - En régression, des intervalles de largeur constante sont inadaptés ; **CQR** les rend adaptatifs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.10, exercices 5.13 et 5.14.
