## 1.2 Validation croisée

Mettre de côté un jeu de test (section 1.1) protège de l'optimisme, mais coûte cher : ces clients ne participent pas à l'apprentissage, et la note obtenue dépend du **hasard du découpage**. Quand il s'agit de **choisir** entre modèles ou de les régler, on a besoin de nombreuses évaluations fiables. La **validation croisée** est la réponse standard : elle fait servir chaque observation tantôt à l'entraînement, tantôt à la validation, sans jamais mélanger les deux rôles pour une même évaluation.

### 1.2.1 Un seul découpage ne suffit pas

Prenons un petit échantillon de 2 000 clients, et mesurons l'AUC d'une régression logistique sur un jeu de validation de 20 % (400 clients, dont 56 partis). Recommençons **200 fois**, avec 200 découpages aléatoires différents. Le modèle, les données et la métrique sont les mêmes ; seul le hasard du découpage change.

```python hide
sub = X_tr.sample(2000, random_state=0); ysub = y_tr.loc[sub.index]
aucs = []
for s in range(200):
    a, b, ya, yb = train_test_split(sub, ysub, test_size=0.2, stratify=ysub, random_state=s)
    aucs.append(roc_auc_score(yb, modele_logit().fit(a, ya).predict_proba(b)[:, 1]))
aucs = np.array(aucs)
print("200 découpages : moyenne", aucs.mean().round(3), "| écart-type", aucs.std().round(3), "| min", aucs.min().round(3), "| max", aucs.max().round(3), "| 95 % central", np.percentile(aucs, [2.5, 97.5]).round(3), "| validation", len(yb), "dont partis", int(yb.sum()))
fig, ax = plt.subplots(figsize=(7.2, 3.4))
ax.hist(aucs, bins=22, color=BLEU, alpha=0.85, edgecolor="white")
ax.axvline(aucs.mean(), color=ORANGE, lw=2); ax.text(aucs.mean() - 0.003, ax.get_ylim()[1] * 0.92, f"moyenne {aucs.mean():.3f}".replace(".", ","), color=ORANGE, ha="right")
ax.set_xlabel("AUC mesurée sur le jeu de validation"); ax.set_ylabel("nombre de découpages")
ax.set_title("Même modèle, mêmes données : 200 découpages différents"); ax.grid(axis="x", visible=False)
plt.tight_layout(); plt.savefig("figures/ch01-decoupage-variabilite.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
200 découpages : moyenne 0.864 | écart-type 0.024 | min 0.788 | max 0.914 | 95 % central [0.816 0.908] | validation 400 dont partis 56
```

![Distribution de l'AUC d'une même régression logistique sur 200 découpages aléatoires différents d'un échantillon de 2 000 clients.](figures/ch01-decoupage-variabilite.png)

Selon le découpage, l'AUC varie de **0,79 à 0,91**, avec un intervalle central à 95 % de 0,82 à 0,91. Deux analystes qui utilisent des graines différentes pourraient publier des conclusions opposées sur le même modèle, et choisir, entre deux modèles proches, celui que le hasard a favorisé. Un découpage unique est un instrument de mesure **bruité**. Avec 56 clients partis dans le jeu de validation, rien d'étonnant : la mesure s'appuie sur un petit nombre d'événements.

### 1.2.2 La validation croisée à $k$ plis

L'idée : au lieu d'un découpage, on en fait $k$, **de façon systématique**, pour que chaque client serve exactement une fois à la validation.

1. On mélange les données et on les coupe en $k$ parties de taille égale, les **plis** (*folds*).
2. Pour chaque pli $j=1,\dots,k$ : on **entraîne** le modèle sur les $k-1$ autres plis, et on mesure sa perte sur le pli $j$, qui n'a pas servi à l'entraînement.
3. On **moyenne** les $k$ mesures :
$$\mathrm{CV}_k=\frac1k\sum_{j=1}^k\ \frac1{|F_j|}\sum_{i\in F_j}\ell\bigl(y_i,\ \hat f^{(-j)}(x_i)\bigr),$$
où $\hat f^{(-j)}$ est le modèle entraîné **sans** le pli $F_j$.

```python hide
fig, ax = plt.subplots(figsize=(9.2, 2.7)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5.6)
for j in range(5):
    y0 = 4.4 - j * 0.95
    for f in range(5):
        ax.add_patch(plt.Rectangle((1.4 + f * 1.4, y0), 1.35, 0.7, color=ORANGE if f == j else BLEU, alpha=0.85 if f == j else 0.3))
    ax.text(1.2, y0 + 0.35, f"essai {j + 1}", ha="right", va="center", fontsize=9.5, color=ENCRE2)
    ax.text(1.4 + j * 1.4 + 0.675, y0 + 0.35, "validation", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
for f in range(5): ax.text(1.4 + f * 1.4 + 0.675, 5.3, f"pli {f + 1}", ha="center", fontsize=9.5, color=ENCRE2)
plt.savefig("figures/ch01-schema-kplis.png", dpi=200, bbox_inches="tight"); plt.close()
```

![Validation croisée à 5 plis : à chaque essai, un pli (orange) sert à la validation et les quatre autres (bleu) à l'entraînement.](figures/ch01-schema-kplis.png)

**Un exemple à la main.** Le cas extrême $k=n$ (chaque observation forme un pli) s'appelle la validation croisée **« un seul laissé de côté »** (*leave-one-out*, LOO). Prenons trois montants de commandes $y=(2;\ 4;\ 9)$ et un « modèle » très simple : prédire la **moyenne des données d'entraînement**. L'erreur sur les données d'entraînement vaut, avec $\bar y=5$ : $\frac{(2-5)^2+(4-5)^2+(9-5)^2}{3}=\frac{26}{3}\approx8{,}67$. Voyons maintenant la validation LOO :

- on retire 2, on prédit avec la moyenne de (4 ; 9), soit 6,5 : erreur $-4{,}5$ ;
- on retire 4, on prédit avec la moyenne de (2 ; 9), soit 5,5 : erreur $-1{,}5$ ;
- on retire 9, on prédit avec la moyenne de (2 ; 4), soit 3 : erreur $6$.

L'erreur quadratique LOO vaut $\frac{20{,}25+2{,}25+36}{3}=19{,}5$, soit **plus du double** de l'erreur d'entraînement (8,67). On voit à l'œuvre l'optimisme de la section 1.1.2. Et il existe ici une jolie formule : si l'on retire $y_i$, la moyenne des autres vaut $\frac{n\bar y-y_i}{n-1}$, donc l'erreur est $y_i-\frac{n\bar y-y_i}{n-1}=\frac{n}{n-1}(y_i-\bar y)$ ; l'erreur LOO est ainsi l'erreur d'entraînement multipliée par $\left(\frac n{n-1}\right)^2=2{,}25$, et $2{,}25\times8{,}67=19{,}5$. (Pour la régression linéaire, il existe de même une formule exacte qui évite de réentraîner $n$ fois : le **PRESS**, vu dans le volume II, section 1.4.)

```python hide
yv = np.array([2., 4., 9.]); loo = np.array([yv[i] - np.delete(yv, i).mean() for i in range(3)])
print("erreurs LOO", loo, "| MSE LOO", (loo ** 2).mean(), "| MSE d'entraînement", round(((yv - yv.mean()) ** 2).mean(), 4), "| facteur", (3 / 2) ** 2)
```
<!--sortie-->
```text
erreurs LOO [-4.5 -1.5  6. ] | MSE LOO 19.5 | MSE d'entraînement 8.6667 | facteur 2.25
```

En pratique, sur les données de la boutique, une validation croisée à 5 plis de la régression logistique tient en trois lignes :

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(modele_logit(), X_tr, y_tr, cv=5, scoring="roc_auc")
print(scores.round(3), scores.mean().round(3))
```
<!--sortie-->
```text
[0.873 0.858 0.87  0.836 0.862] 0.86
```

Les cinq plis donnent des AUC de 0,84 à 0,87 ; l'estimation retenue est leur moyenne, **0,860**. Ici, `cv=5` découpe en cinq plis *stratifiés* (même proportion de départs dans chacun), comportement par défaut pour un classifieur.

> 💡 **Ce que la validation croisée estime vraiment.** Chacun des $k$ modèles est entraîné sur $\frac{k-1}k$ des données ; la moyenne estime donc la performance d'un modèle entraîné sur **un peu moins** de données que le jeu complet. C'est une estimation de la *procédure* d'apprentissage (« entraîner ce type de modèle sur ce volume de données »), pas du modèle final particulier que l'on livrera en réentraînant sur tout.

**Combien de plis ?** Il y a un compromis. Avec peu de plis ($k=2$), chaque modèle voit la moitié des données : il est moins bon que le modèle final, et la validation est **pessimiste** (biais). Avec beaucoup de plis, le biais disparaît, mais les modèles entraînés sont presque identiques, donc les erreurs sont très corrélées, et le calcul coûte $k$ entraînements. Vérifions sur nos données : on tire 10 sous-échantillons de 1 000 clients ; pour chacun, on compare l'estimation par validation croisée à la **vraie performance** du modèle entraîné sur ces 1 000 clients, mesurée sur les 8 000 clients restants.

```python hide
res = {k: [] for k in (2, 5, 10, 20)}; vrai = []
for r in range(10):
    sb = X_tr.sample(1000, random_state=100 + r); ys = y_tr.loc[sb.index]; hors = X_tr.drop(sb.index); yh = y_tr.loc[hors.index]
    vrai.append(roc_auc_score(yh, modele_logit().fit(sb, ys).predict_proba(hors)[:, 1]))
    for k in res:
        res[k].append(cross_val_score(modele_logit(), sb, ys, cv=StratifiedKFold(k, shuffle=True, random_state=r), scoring="roc_auc").mean())
tab = pd.DataFrame({"k": list(res), "AUC moyenne": [np.mean(v) for v in res.values()], "biais": [np.mean(v) - np.mean(vrai) for v in res.values()], "écart-type": [np.std(v) for v in res.values()]}).round(4)
print("vraie AUC (modèles entraînés sur 1000 clients) :", np.mean(vrai).round(4)); print(tab.to_string(index=False))
```
<!--sortie-->
```text
vraie AUC (modèles entraînés sur 1000 clients) : 0.8441
 k  AUC moyenne   biais  écart-type
 2       0.8335 -0.0106      0.0212
 5       0.8454  0.0013      0.0139
10       0.8455  0.0015      0.0145
20       0.8471  0.0030      0.0133
```

Avec $k=2$, l'estimation est **pessimiste** de 1 point d'AUC et plus dispersée (écart-type 0,021). À partir de $k=5$, le biais est de l'ordre du millième, plus petit que la dispersion, et augmenter encore $k$ n'apporte rien de mesurable. D'où la règle pratique : **$k=5$ ou $k=10$**. Le « un seul laissé de côté » est surtout réservé aux très petits jeux de données ou aux modèles pour lesquels une formule évite les réentraînements.

### 1.2.3 Les variantes : stratifiée, répétée, groupée, temporelle

Le découpage en plis n'est pas anodin : il doit **reproduire la situation de l'utilisation réelle**. Les variantes suivantes répondent à quatre situations différentes.

| Variante | Quand l'utiliser | Idée |
|---|---|---|
| **Stratifiée** | cible rare ou classes déséquilibrées | même proportion de chaque classe dans chaque pli |
| **Répétée** | jeu de données petit, mesure instable | on refait la validation $m$ fois avec des découpages différents |
| **Groupée** | plusieurs lignes par entité (client, magasin, patient) | toutes les lignes d'une entité sont dans le même pli |
| **Temporelle** | prédire l'avenir à partir du passé | on entraîne sur le passé, on valide sur le futur proche |

**Répétée.** Refaire 5 plis 20 fois (avec 20 découpages différents) réduit le bruit dû au découpage lui-même. Sur nos 9 000 clients, il est déjà minuscule : l'écart-type des moyennes entre répétitions vaut seulement 0,0007 d'AUC. La répétition est utile pour de **petits** jeux de données.

```python hide
rep = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0)
sc_rep = cross_val_score(modele_logit(), X_tr, y_tr, cv=rep, scoring="roc_auc").reshape(20, 5)
print("répété 5x20 : écart-type des moyennes entre répétitions", sc_rep.mean(1).std().round(4), "| moyenne", sc_rep.mean().round(4))
```
<!--sortie-->
```text
répété 5x20 : écart-type des moyennes entre répétitions 0.0007 | moyenne 0.8606
```

**Groupée.** Supposons qu'on veuille savoir comment le modèle se comportera dans une **ville qu'il n'a jamais vue**. On place alors chaque ville tout entière dans un seul pli.

```python
from sklearn.model_selection import GroupKFold

villes = df.loc[X_tr.index, "ville"]
cv_ville = cross_val_score(modele_logit(), X_tr, y_tr, groups=villes, cv=GroupKFold(5), scoring="roc_auc")
print(cv_ville.mean().round(4))
```
<!--sortie-->
```text
0.8577
```

L'AUC « par ville » (0,858) est à peine inférieure à celle de la validation stratifiée (0,860) : dans nos données, l'effet de la ville est modeste. Dans un jeu où le même **client** apparaît sur plusieurs lignes (plusieurs commandes), la différence serait énorme, car le modèle reconnaîtrait le client plutôt que de généraliser.

**Temporelle.** C'est la variante où l'erreur est la plus courante, et la plus coûteuse. Prenons une série mensuelle simulée sur 11 ans (tendance, saisonnalité, bruit corrélé) et un modèle qui prédit chaque mois à partir des valeurs de 1, 2, 3 et 12 mois plus tôt. Trois estimations de l'erreur (RMSE) :

```python hide
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
rng = np.random.default_rng(7); T = 144; t = np.arange(T)
bruit = np.zeros(T)
for i in range(1, T): bruit[i] = 0.8 * bruit[i - 1] + rng.normal(0, 2)
serie = 100 + 0.5 * t + 8 * np.sin(2 * np.pi * t / 12) + bruit
ds = pd.DataFrame({"y": serie})
for l in (1, 2, 3, 12): ds[f"l{l}"] = ds.y.shift(l)
ds["mois"] = t % 12; ds = ds.dropna().reset_index(drop=True)
Xs, ys = ds.drop(columns="y"), ds.y
mod = lambda: RandomForestRegressor(100, min_samples_leaf=2, random_state=0, n_jobs=1)
rmse = lambda u, v: np.sqrt(mean_squared_error(u, v))
cv_alea = -cross_val_score(mod(), Xs, ys, cv=KFold(5, shuffle=True, random_state=0), scoring="neg_root_mean_squared_error").mean()
cv_temp = -cross_val_score(mod(), Xs, ys, cv=TimeSeriesSplit(5), scoring="neg_root_mean_squared_error").mean()
n = len(ds); fin = n - 24; futur = rmse(ys[fin:], mod().fit(Xs[:fin], ys[:fin]).predict(Xs[fin:]))
print("RMSE : CV aléatoire", round(cv_alea, 2), "| CV temporelle", round(cv_temp, 2), "| vrai futur (24 derniers mois)", round(futur, 2))
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.1)); 
for a_ in ax: a_.axis("off"); a_.set_xlim(0, 10); a_.set_ylim(0, 5.6)
ax[0].set_title("Plis aléatoires : le futur aide à prédire le passé", fontsize=10)
rng2 = np.random.default_rng(3); aff = rng2.integers(0, 5, 20)
for j in range(3):
    for p in range(20):
        ax[0].add_patch(plt.Rectangle((0.3 + p * 0.46, 4.2 - j * 1.3), 0.4, 0.8, color=ORANGE if aff[p] == j else BLEU, alpha=0.85 if aff[p] == j else 0.3))
    ax[0].text(0.2, 4.6 - j * 1.3, f"essai {j + 1}", ha="right", fontsize=9, va="center", color=ENCRE2)
ax[1].set_title("Plis temporels : on ne valide que sur le futur", fontsize=10)
for j, lim in enumerate([8, 12, 16]):
    for p in range(20):
        c = BLEU if p < lim else (ORANGE if p < lim + 4 else MUET)
        ax[1].add_patch(plt.Rectangle((0.3 + p * 0.46, 4.2 - j * 1.3), 0.4, 0.8, color=c, alpha=0.85 if c == ORANGE else 0.3 if c == BLEU else 0.12))
    ax[1].text(0.2, 4.6 - j * 1.3, f"essai {j + 1}", ha="right", fontsize=9, va="center", color=ENCRE2)
ax[1].text(5, 0.1, "temps →  (bleu : entraînement, orange : validation, gris : non utilisé)", ha="center", fontsize=8.5, color=ENCRE2)
plt.tight_layout(); plt.savefig("figures/ch01-schemas-cv.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
RMSE : CV aléatoire 3.51 | CV temporelle 7.31 | vrai futur (24 derniers mois) 6.75
```

![Deux façons de découper une série temporelle : plis aléatoires (à gauche, le modèle voit des mois situés après ceux qu'il doit prédire) et plis temporels (à droite, l'entraînement précède toujours la validation).](figures/ch01-schemas-cv.png)

La validation croisée **aléatoire** annonce une erreur de **3,5** : elle est presque deux fois trop optimiste. La validation **temporelle** annonce 7,3, proche de l'erreur réellement observée sur les 24 derniers mois (6,75). La raison est simple : en mélangeant les mois, le modèle s'entraîne sur des mois **voisins** du mois à prédire (le mois d'avant et le mois d'après se ressemblent), ce qu'il ne pourra jamais faire en production, où l'avenir est inconnu. C'est une **fuite temporelle**.

> ⚠️ **Règle de décision.** Avant de choisir une validation croisée, posez la question : *« en production, qu'est-ce qui sera connu de ce qui m'entoure ? »* Si le futur n'est pas connu, la validation doit respecter l'ordre du temps ; si les lignes d'une même entité arrivent ensemble, elles doivent rester ensemble.

### 1.2.4 Quelle confiance accorder à l'estimation ?

La validation croisée donne un **nombre**, pas une certitude. Deux sources de bruit s'y mélangent : le découpage (que la répétition réduit) et, surtout, **l'échantillon lui-même**, c'est-à-dire le fait qu'on ait observé ces 9 000 clients et pas d'autres. La seconde source est la plus importante, et on ne peut pas la réduire par des calculs.

On est tenté de calculer une erreur-type avec les $k$ scores des plis : $\hat\sigma/\sqrt k$. **Ce n'est pas valable.** Les $k$ modèles sont entraînés sur des données qui se recouvrent presque entièrement : les $k$ mesures ne sont pas indépendantes, et la formule suppose qu'elles le sont. Un résultat théorique (Bengio et Grandvalet, 2004) montre même qu'**il n'existe pas d'estimateur sans biais universel** de la variance de la validation croisée. Vérifions numériquement. On découpe nos 9 000 clients en 12 blocs disjoints de 750 ; sur chacun, on fait une validation à 5 plis. Les 12 estimations sont indépendantes : leur dispersion est la **vraie** incertitude d'une validation croisée sur 750 clients.

```python hide
idx = np.random.default_rng(0).permutation(len(X_tr)); est = []; nai = []
for k in range(12):
    ii = idx[k * 750:(k + 1) * 750]
    sc = cross_val_score(modele_logit(), X_tr.iloc[ii], y_tr.iloc[ii], cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc")
    est.append(sc.mean()); nai.append(sc.std(ddof=1) / np.sqrt(5))
print("12 blocs de 750 : écart-type réel des estimations", np.std(est, ddof=1).round(4), "| erreur-type 'naïve' moyenne", np.mean(nai).round(4), "| moyenne des estimations", np.mean(est).round(4))
```
<!--sortie-->
```text
12 blocs de 750 : écart-type réel des estimations 0.0145 | erreur-type 'naïve' moyenne 0.0215 | moyenne des estimations 0.8296
```

L'incertitude réelle (écart-type 0,0145) diffère de l'erreur-type « naïve » tirée des plis (0,0215) : ici, cette dernière est trop **pessimiste** ; dans d'autres situations, elle est trop optimiste. Le message est clair : **ne présentez jamais $\hat\sigma/\sqrt k$ comme une barre d'erreur.** Pour comparer deux modèles ou rapporter un intervalle, la section 1.4 présente des outils adaptés (test t corrigé, bootstrap du jeu de test). Retenez surtout un ordre de grandeur : avec quelques centaines à quelques milliers de clients, **des écarts de moins d'un point d'AUC ne sont pas interprétables**.

### 1.2.5 La validation croisée imbriquée : un aperçu

Un dernier piège guette dès qu'on se sert de la validation croisée pour **choisir** : un modèle parmi dix, un hyperparamètre parmi cent. Le meilleur score obtenu est alors lui-même le résultat d'une **sélection**, donc optimiste (c'est exactement l'argument de la démonstration 1.1.2, appliqué à la validation). La parade est la **validation croisée imbriquée** (*nested cross-validation*) :

1. une **boucle externe** découpe les données en plis ; chaque pli externe est un jeu de test provisoire ;
2. pour chaque pli externe, une **boucle interne** (une autre validation croisée sur les données d'entraînement externes seulement) choisit le meilleur modèle ou réglage ;
3. le modèle ainsi choisi est évalué **sur le pli externe**, que la sélection n'a jamais vu ;
4. la moyenne des évaluations externes estime la performance de **toute la procédure** « choisir puis entraîner ».

Le coût est multiplicatif ($k_{\text{ext}}\times k_{\text{int}}\times$ le nombre de candidats), mais c'est le prix d'une estimation honnête. Nous la mettrons en œuvre à la section 1.5, où nous verrons sur un jeu de pur bruit à quel point le réglage peut s'auto-persuader.

> ✅ **À retenir.**
> - Un seul découpage est un instrument **bruité** : sur 400 clients de validation, l'AUC varie de 0,79 à 0,91 selon la graine.
> - La **validation croisée à $k$ plis** utilise chaque observation pour valider exactement une fois ; **$k=5$ ou $10$** est un bon compromis (biais de l'ordre du millième pour $k\ge5$, pessimiste pour $k=2$).
> - Le découpage doit **imiter l'usage réel** : stratifié (classes rares), groupé (entités répétées), **temporel** (prédire l'avenir). Une validation aléatoire sur une série temporelle annonce 3,5 d'erreur au lieu de 7.
> - L'**écart-type entre plis n'est pas une barre d'erreur** : les plis ne sont pas indépendants.
> - Quand la validation croisée sert à **choisir**, son meilleur score est optimiste : on utilise la validation **imbriquée**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 à 1.4, exercices 1.4 à 1.6.
