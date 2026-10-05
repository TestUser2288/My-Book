## 2.6 ➕ Pour aller plus loin : CatBoost, stacking et blending

> 🧭 **Section optionnelle.** Deux idées pour aller au-delà d'un modèle unique : un boosting conçu pour les **variables catégorielles** (CatBoost), et la **combinaison** de plusieurs modèles différents (blending, stacking). Dans les deux cas, le danger principal est le même, et il est discret : la **fuite d'information** de la cible vers les variables.

### 2.6.1 CatBoost et le piège de l'encodage par la cible

Comment donner une variable à beaucoup de modalités (la ville, le code d'un produit) à un modèle ? L'encodage par indicatrices crée autant de colonnes que de modalités. Une idée tentante : remplacer la modalité par la **moyenne de la cible** dans cette modalité (l'**encodage par la cible**, *target encoding*). La ville D devient « 0,17 », parce que 17 % des clients de la ville D sont partis.

L'idée est excellente, **mais elle fuit** si on la calcule naïvement. La moyenne de la ville D contient la réponse du client lui-même : pour un client dont la ville ne compte que quelques clients, la valeur encodée *est* sa propre étiquette, à peine diluée. Le modèle apprend « une valeur élevée signifie parti » sur l'entraînement, où c'est vrai par construction, puis échoue sur de nouvelles données.

Pour le voir, fabriquons une variable **sans aucune information** : un identifiant de zone à 1 500 modalités, tiré au hasard, indépendant de la résiliation. Encodons-la naïvement par la moyenne de la cible, et ajustons un modèle logistique sur cette seule colonne.

```python hide
from scipy.special import logit as logit_
rng = np.random.default_rng(8)
zone_tr = rng.integers(0, 1500, len(Xtr)); zone_te = rng.integers(0, 1500, len(Xte))
moy = pd.Series(ytr.to_numpy()).groupby(zone_tr).mean()
enc_tr = pd.Series(zone_tr).map(moy).to_numpy()
enc_te = pd.Series(zone_te).map(moy).fillna(ytr.mean()).to_numpy()
naif = LogisticRegression().fit(enc_tr.reshape(-1, 1), ytr)
NUM("auc_te_naif_train", roc_auc_score(ytr, naif.predict_proba(enc_tr.reshape(-1, 1))[:, 1]))
NUM("auc_te_naif_test", roc_auc_score(yte, naif.predict_proba(enc_te.reshape(-1, 1))[:, 1]))
NUM("n_par_zone", len(Xtr) / 1500)
# encodage « ordonné » : pour chaque client, moyenne des SEULS clients qui le précèdent dans un ordre aléatoire (avec un a priori lissé)
ordre = rng.permutation(len(Xtr)); s = {}; n_ = {}; prior = ytr.mean(); a = 10; enc_ord = np.zeros(len(Xtr))
for i in ordre:
    z = zone_tr[i]
    enc_ord[i] = (s.get(z, 0.0) + a * prior) / (n_.get(z, 0) + a)
    s[z] = s.get(z, 0.0) + ytr.iloc[i]; n_[z] = n_.get(z, 0) + 1
ord_lr = LogisticRegression().fit(enc_ord.reshape(-1, 1), ytr)
NUM("auc_ord_train", roc_auc_score(ytr, ord_lr.predict_proba(enc_ord.reshape(-1, 1))[:, 1]))
# exemple à la main : six clients, deux villes
dem = pd.DataFrame({"ville": list("AAABBB"), "y": [1, 0, 1, 0, 0, 1]})
prev = {}; vals = []
for _, r_ in dem.iterrows():
    h = prev.get(r_.ville, []); vals.append((sum(h) + 0.5) / (len(h) + 1)); prev.setdefault(r_.ville, []).append(r_.y)
dem["encodage_ordonne"] = vals
dem["encodage_naif"] = dem.groupby("ville")["y"].transform("mean")
```
<!--sortie-->
```text
NUM auc_te_naif_train 0.8007282244446481
NUM auc_te_naif_test 0.5049665717714521
NUM n_par_zone 6.0
NUM auc_ord_train 0.5283304753053291
```

Avec environ 6 clients par zone, le modèle ajusté sur l'encodage naïf atteint une AUC de **0,801** sur l'entraînement, sur une variable qui ne contient *rien*. Sur le jeu de test, l'AUC retombe à 0,505 : le hasard. C'est de la fuite pure : l'étiquette du client est passée dans la variable.

**La solution de CatBoost : l'encodage ordonné.** On met les clients dans un **ordre aléatoire** et l'on encode chaque client par la moyenne de la cible des **seuls clients qui le précèdent** dans cet ordre, avec un petit a priori pour lisser :

$$\text{enc}_i=\frac{\sum_{j<i,\ x_j=x_i}y_j+a\,p}{\#\{j<i:\ x_j=x_i\}+a},$$

où $p$ est la moyenne générale de la cible et $a$ un poids d'a priori. L'étiquette d'un client n'intervient donc **jamais** dans sa propre valeur. Un exemple à la main : six clients de deux villes, $a=1$ et $p=0{,}5$.

```python hide-code
print(dem.round(3).to_string(index=False))
```
<!--sortie-->
```text
ville  y  encodage_ordonne  encodage_naif
    A  1             0.500          0.667
    A  0             0.750          0.667
    A  1             0.500          0.667
    B  0             0.500          0.333
    B  0             0.250          0.333
    B  1             0.167          0.333
```

Pour la ville A, le premier client n'a pas d'historique : $\frac{0+0{,}5}{0+1}=0{,}5$ ; le deuxième voit un seul prédécesseur, parti ($y=1$) : $\frac{1+0{,}5}{1+1}=0{,}75$ ; le troisième voit deux prédécesseurs, un parti et un resté : $\frac{1+0{,}5}{2+1}=0{,}5$. L'encodage naïf aurait donné $0{,}667$ à tous les clients de la ville A, y compris ceux qui ont contribué à ce 0,667. Sur notre variable de bruit, l'encodage ordonné ramène l'AUC d'entraînement à 0,528 : le modèle n'a plus rien à mémoriser, ce qui est la bonne réponse.

**CatBoost** (Prokhorenkova et coll., 2018) fait de cette idée un principe : encodage ordonné des catégories, mais aussi **boosting ordonné** (les pseudo-résidus d'un client sont calculés avec un modèle qui ne l'a pas vu), et des arbres **symétriques** (*oblivious trees*, la même question à tous les nœuds d'un niveau), plus rapides et moins sujets au surapprentissage. En pratique, on lui passe les colonnes catégorielles telles quelles :

```python
from catboost import CatBoostClassifier

Xtr_cb, Xte_cb = Xtr.copy(), Xte.copy()
Xtr_cb[cat], Xte_cb[cat] = Xtr_cb[cat].fillna("manquant"), Xte_cb[cat].fillna("manquant")
catb = CatBoostClassifier(iterations=300, learning_rate=0.08, depth=6, cat_features=cat, random_seed=0, verbose=False, thread_count=1)
catb.fit(Xtr_cb, ytr)
print(round(roc_auc_score(yte, catb.predict_proba(Xte_cb)[:, 1]), 4))
```
<!--sortie-->
```text
0.9046
```

```python hide
Xtr_cb, Xte_cb = Xtr.copy(), Xte.copy()
Xtr_cb[cat], Xte_cb[cat] = Xtr_cb[cat].fillna("manquant"), Xte_cb[cat].fillna("manquant")
from catboost import CatBoostClassifier
catb = CatBoostClassifier(iterations=300, learning_rate=0.08, depth=6, cat_features=cat, random_seed=0, verbose=False, thread_count=1).fit(Xtr_cb, ytr)
p_cb = catb.predict_proba(Xte_cb)[:, 1]
NUM("auc_catboost", roc_auc_score(yte, p_cb)); NUM("auc_boost_ref", roc_auc_score(yte, test_p["gradient boosting"]))
```
<!--sortie-->
```text
NUM auc_catboost 0.9046344538705182
NUM auc_boost_ref 0.9025142780303917
```

CatBoost obtient une AUC de test de 0,905, à comparer à 0,903 pour le boosting de la section 2.4 : sur ces données, avec peu de catégories, les deux sont équivalents. CatBoost brille surtout quand les variables catégorielles sont nombreuses ou à très grand nombre de modalités, et sa configuration par défaut est réputée robuste.

### 2.6.2 Combiner des modèles : le blending

Les modèles de la section 2.4 ne se trompent pas tous sur les mêmes clients. **Combiner** leurs prédictions peut donc faire mieux que le meilleur. Le plus simple est le **blending** (mélange) : une **moyenne** des probabilités prédites, éventuellement pondérée.

Pourquoi cela marche-t-il ? Par la même formule qu'en 2.3.2 : la variance de la moyenne de prédictions $\rho\sigma^2+\frac{1-\rho}B\sigma^2$ ne diminue que si les prédictions sont **peu corrélées**. Moyenner trois modèles quasi identiques ne sert à rien ; moyenner trois modèles de **familles différentes** (un linéaire, une forêt, un boosting) apporte quelque chose.

Une règle essentielle : les prédictions utilisées pour **choisir** les poids ne doivent pas être des prédictions **faites sur les données d'entraînement** du modèle, qui sont trop belles. On utilise des prédictions **hors pli** (*out-of-fold*, OOF) : pour chaque client, la prédiction d'un modèle entraîné sans lui, par validation croisée.

```python hide
from sklearn.model_selection import cross_val_predict
bases = {
    "régression logistique": (make_pipeline(pre_lin, LogisticRegression(C=0.3, max_iter=1000)), Xtr, Xte),
    "forêt aléatoire": (RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_features="sqrt", n_jobs=1, random_state=0), Xtr_o, Xte_o),
    "gradient boosting": (HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, early_stopping=True, validation_fraction=0.15, n_iter_no_change=20,
                                                          categorical_features="from_dtype", random_state=0), Xtr_c, Xte_c),
}
oof = np.column_stack([cross_val_predict(m, A, ytr, cv=cv5, method="predict_proba")[:, 1] for m, A, _ in bases.values()])
pte = np.column_stack([test_p[k] for k in bases])
cor = np.corrcoef(oof.T)
NUM("cor_lr_foret", cor[0, 1]); NUM("cor_lr_boost", cor[0, 2]); NUM("cor_foret_boost", cor[1, 2])
moyenne_simple = pte.mean(1)
NUM("auc_blend_3", roc_auc_score(yte, moyenne_simple))
NUM("auc_blend_foret_boost", roc_auc_score(yte, pte[:, 1:].mean(1)))
NUM("auc_oof_blend", roc_auc_score(ytr, oof.mean(1)))
```
<!--sortie-->
```text
NUM cor_lr_foret 0.8809587794627431
NUM cor_lr_boost 0.8261617428643281
NUM cor_foret_boost 0.9242796166100327
NUM auc_blend_3 0.9003508144993503
NUM auc_blend_foret_boost 0.9043351240929157
NUM auc_oof_blend 0.8901172432356369
```

Les corrélations entre les prédictions hors pli sont de 0,88 (régression logistique et forêt), 0,83 (régression logistique et boosting) et 0,92 (forêt et boosting). La moyenne simple des trois modèles obtient une AUC de test de **0,900**, contre 0,903 pour le boosting seul : **le mélange est un peu moins bon que son meilleur membre**, parce que le modèle linéaire, nettement plus faible, dilue les autres. La moyenne forêt + boosting seulement obtient 0,904, un peu au-dessus. Moyennez des modèles de **niveau comparable**, ou pondérez-les (c'est ce que fait le stacking). Ces corrélations, toutes élevées, expliquent aussi la modestie du gain : ces modèles se trompent largement sur les mêmes clients.

### 2.6.3 Le stacking : laisser un modèle apprendre à combiner

Le **stacking** (empilement) pousse l'idée plus loin : au lieu de fixer les poids du mélange, on les **apprend** avec un **méta-modèle** (souvent une régression logistique), dont les variables d'entrée sont les prédictions des modèles de base. On passe de « moyenne égale » à « donne trois fois plus de poids au boosting qu'à la forêt, et un petit poids au modèle linéaire ». La condition de validité est celle du blending, et le piège est sournois : **le méta-modèle doit être entraîné sur des prédictions hors pli.**

```python
# oof : une colonne par modèle de base, prédictions HORS PLI (calculées plus haut avec cross_val_predict)
meta = LogisticRegression().fit(logit_(np.clip(oof, 1e-4, 1 - 1e-4)), ytr)
print(meta.coef_.round(2))
```
<!--sortie-->
```text
[[0.09 0.47 0.57]]
```

(`oof` a été calculé plus haut : pour chaque client, la prédiction de chaque modèle de base entraîné **sans lui**, par validation croisée à cinq plis. Les prédictions de test s'obtiennent en réentraînant chaque modèle sur tout l'entraînement.)

```python hide
lg_ = lambda P: logit_(np.clip(P, 1e-4, 1 - 1e-4))
meta_ok = LogisticRegression().fit(lg_(oof), ytr)
NUM("auc_stack_ok", roc_auc_score(yte, meta_ok.predict_proba(lg_(pte))[:, 1]))
for k, v in zip(("lr", "foret", "boost"), meta_ok.coef_[0]): NUM(f"coef_ok_{k}", v)
# la version FAUTIVE : méta-modèle entraîné sur les prédictions faites sur les données d'entraînement elles-mêmes
ptr_insample = np.column_stack([m.fit(A, ytr).predict_proba(A)[:, 1] for m, A, _ in bases.values()])
meta_naif = LogisticRegression().fit(lg_(ptr_insample), ytr)
NUM("auc_stack_naif", roc_auc_score(yte, meta_naif.predict_proba(lg_(pte))[:, 1]))
for k, v in zip(("lr", "foret", "boost"), meta_naif.coef_[0]): NUM(f"coef_naif_{k}", v)
NUM("auc_foret_insample", roc_auc_score(ytr, ptr_insample[:, 1]))
rng = np.random.default_rng(42); yv_ = yte.to_numpy(); n_t = len(yv_); pk = meta_ok.predict_proba(lg_(pte))[:, 1]; pb = test_p["gradient boosting"]
d = [roc_auc_score(yv_[i], pk[i]) - roc_auc_score(yv_[i], pb[i]) for i in (rng.integers(0, n_t, n_t) for _ in range(400))]
NUM("stack_vs_boost_m", np.mean(d)); NUM("stack_vs_boost_lo", np.percentile(d, 2.5)); NUM("stack_vs_boost_hi", np.percentile(d, 97.5))
```
<!--sortie-->
```text
NUM auc_stack_ok 0.9044916965919693
NUM coef_ok_lr 0.09060248579237268
NUM coef_ok_foret 0.46522052375650286
NUM coef_ok_boost 0.567389814837675
NUM auc_stack_naif 0.8825236539600408
NUM coef_naif_lr -1.6739287868052057
NUM coef_naif_foret 5.64424169565157
NUM coef_naif_boost -0.1206757556335855
NUM auc_foret_insample 0.9855464710444675
NUM stack_vs_boost_m 0.002083321243169975
NUM stack_vs_boost_lo -0.0007968744304916119
NUM stack_vs_boost_hi 0.00487755024670674
```

Les coefficients appris sur des prédictions hors pli sont 0,09 (régression logistique), 0,47 (forêt) et 0,57 (boosting) ; l'AUC de test de l'empilement est **0,904**. Que se passe-t-il si l'on commet la faute et que l'on entraîne le méta-modèle sur les prédictions que chaque modèle fait **sur ses propres données d'entraînement** ? La forêt, qui a vu ces clients, y est presque parfaite (AUC 0,986 sur l'entraînement) ; le méta-modèle conclut que la forêt est un oracle et lui donne un poids énorme (coefficients −1,67, 5,64, −0,12). Résultat sur le jeu de test : 0,883 au lieu de 0,904. Le coût d'un méta-modèle fautif n'est pas toujours spectaculaire, mais il va toujours dans le mauvais sens, et il **fausse l'évaluation** si on l'évalue lui aussi sur des données déjà vues.

### 2.6.4 Quand cela vaut-il la peine ?

Le gain de l'empilement sur le meilleur modèle seul est ici de 0,002 d'AUC, avec un intervalle à 95 % de [−0,001 ; 0,005] (bootstrap apparié sur le jeu de test). Aucune de ces combinaisons n'apporte plus qu'un gain marginal, et c'est typique : sur des données tabulaires de cette taille, **le boosting bien réglé capte l'essentiel**. Dans les compétitions de prédiction, où l'on se bat pour le troisième chiffre après la virgule, on empile systématiquement. Dans une entreprise, chaque modèle supplémentaire est un **coût** : plus de code, plus de dépendances, plus de pannes, plus de difficulté à expliquer. La question honnête n'est pas « peut-on gagner 0,002 ? » mais « ce gain justifie-t-il la complexité, au regard de la décision que l'on prend avec la prédiction ? »

> ✅ **À retenir.**
> - L'**encodage par la cible** naïf **fuit** : l'étiquette du client entre dans sa propre variable (sur du bruit pur, il « apprend » l'étiquette). **CatBoost** l'évite par l'**encodage ordonné** (on n'utilise que les clients qui précèdent).
> - Le **blending** moyenne des modèles ; il ne marche que si leurs erreurs sont **peu corrélées**.
> - Le **stacking** apprend la combinaison avec un méta-modèle, qui doit être entraîné sur des prédictions **hors pli**, jamais sur des prédictions faites sur les données d'entraînement.
> - Les gains sont souvent minces ; comparez-les à leur **coût de complexité**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.10 (encodage ordonné, CatBoost et empilement sans fuite), exercice 2.12 (blending et corrélation des erreurs).
