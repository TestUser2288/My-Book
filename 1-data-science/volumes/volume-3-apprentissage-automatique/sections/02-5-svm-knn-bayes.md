## 2.5 ➕ Pour aller plus loin : SVM et noyaux, k plus proches voisins, Bayes naïf

> 🧭 **Section optionnelle.** Trois familles classiques, que l'on rencontre encore souvent et qui illustrent chacune une idée utile : la **marge** et l'astuce du **noyau** (SVM), la **ressemblance** (k plus proches voisins), l'**hypothèse d'indépendance** (Bayes naïf). Sur des données tabulaires de taille moyenne, le boosting les devance généralement ; elles gardent leur intérêt pédagogique et, pour certains problèmes (peu de données, texte, images, données très structurées), leur intérêt pratique.

### 2.5.1 Les machines à vecteurs de support (SVM)

**L'idée de la marge.** Parmi toutes les droites qui séparent deux classes, laquelle choisir ? Celle qui laisse **le plus de place** de part et d'autre : la droite qui maximise la **marge**, la distance entre elle et les clients les plus proches. Une droite collée à des clients est fragile ; une droite au milieu d'une zone vide l'est moins. Les clients qui touchent la marge sont les **vecteurs de support** : ce sont les **seuls** qui déterminent la solution (déplacer un client loin de la marge ne change rien).

Quand les classes se chevauchent (c'est le cas de presque toutes les vraies données), on autorise des violations de la marge, pénalisées. Le problème, pour un score $f(x)=w^\top x+b$, s'écrit exactement dans le cadre de la section 2.1 :

$$\min_{w,b}\ \frac12\|w\|^2+C\sum_{i=1}^n\max\bigl(0,\,1-y_if(x_i)\bigr),$$

soit la **perte charnière** (section 2.1.1) plus une pénalité $\ell_2$. Le paramètre $C$ règle le compromis : grand $C$, on punit fort les violations (marge étroite, risque de surapprentissage) ; petit $C$, on tolère (marge large, modèle plus simple).

**L'astuce du noyau.** Un score linéaire ne sépare pas toujours les classes. L'astuce est de **transformer les variables** pour les rendre séparables, puis d'y chercher une frontière linéaire. Exemple minuscule, en dimension 1 : sept clients repérés par une variable $x$, la classe 1 étant celle des clients proches de zéro.

| $x$ | −3 | −2 | −1 | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|---|---|
| classe | 0 | 0 | 1 | 1 | 1 | 0 | 0 |

Sur la droite des réels, aucun seuil ne sépare les 1 des 0 (les 1 sont au milieu). Mais si l'on associe à chaque $x$ le point $\varphi(x)=(x,\,x^2)$, les clients de la classe 1 ont $x^2\le1$ et ceux de la classe 0 ont $x^2\ge4$ : la droite horizontale $x^2=2{,}5$ les sépare. Une **frontière linéaire dans l'espace transformé** correspond à une frontière **non linéaire** dans l'espace d'origine.

Le miracle est que l'on n'a jamais besoin de calculer $\varphi$ : l'algorithme n'utilise les clients que par leurs **produits scalaires** $\varphi(x)^\top\varphi(x')$, et un **noyau** $k(x,x')$ les calcule directement. Par exemple, le noyau polynomial de degré 2, $k(x,x')=(xx'+1)^2$, correspond à $\varphi(x)=(x^2,\sqrt2\,x,\,1)$ : pour $x=2$ et $x'=3$, $k=(6+1)^2=49$ et $\varphi(x)^\top\varphi(x')=36+12+1=49$. Le noyau le plus utilisé, le noyau **gaussien** (RBF), $k(x,x')=\exp\bigl(-\gamma\|x-x'\|^2\bigr)$, correspond à un espace de dimension *infinie* ; il mesure la **ressemblance** de deux clients, proche de 1 s'ils sont voisins et de 0 s'ils sont éloignés. Le paramètre $\gamma$ règle la portée : grand, chaque client n'influence que son voisinage immédiat (frontière très tourmentée) ; petit, la frontière est lisse.

```python hide
from sklearn.datasets import make_moons
from sklearn.svm import SVC, LinearSVC
a_, b_ = 2.0, 3.0
NUM("noyau_poly", (a_ * b_ + 1) ** 2); NUM("produit_phi", a_ ** 2 * b_ ** 2 + 2 * a_ * b_ + 1)
Pm, cm = make_moons(300, noise=0.28, random_state=0)
Pm_tr, Pm_te, cm_tr, cm_te = train_test_split(Pm, cm, test_size=0.4, random_state=0, stratify=cm)
svm_lin, svm_rbf = SVC(kernel="linear", C=1.0).fit(Pm_tr, cm_tr), SVC(kernel="rbf", C=1.0, gamma=1.0).fit(Pm_tr, cm_tr)
NUM("acc_lin_moons", svm_lin.score(Pm_te, cm_te)); NUM("acc_rbf_moons", svm_rbf.score(Pm_te, cm_te))
NUM("nsv_lin", len(svm_lin.support_)); NUM("nsv_rbf", len(svm_rbf.support_)); NUM("n_moons_tr", len(Pm_tr))
g1, g2 = np.meshgrid(np.linspace(-2, 3, 260), np.linspace(-1.6, 2.1, 260)); Gm = np.c_[g1.ravel(), g2.ravel()]
fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.2), sharey=True)
for ax, mod, titre in ((axs[0], svm_lin, "Noyau linéaire : une droite"), (axs[1], svm_rbf, "Noyau gaussien : une frontière courbe")):
    Z = mod.decision_function(Gm).reshape(g1.shape)
    ax.contourf(g1, g2, Z, levels=[-99, 0, 99], colors=["#c9dffa", "#fbd5c7"], alpha=0.8); ax.contour(g1, g2, Z, levels=[-1, 0, 1], colors=["#52514e"], linestyles=["--", "-", "--"], linewidths=[0.9, 1.6, 0.9])
    ax.scatter(Pm_tr[cm_tr == 0, 0], Pm_tr[cm_tr == 0, 1], s=14, color=BLEU); ax.scatter(Pm_tr[cm_tr == 1, 0], Pm_tr[cm_tr == 1, 1], s=14, color=ORANGE)
    ax.scatter(*mod.support_vectors_.T, s=60, facecolors="none", edgecolors="#0b0b0b", linewidths=0.7)
    ax.set_title(titre, fontsize=10.5); ax.set_xlabel("variable 1")
axs[0].set_ylabel("variable 2")
style.save(fig, "ch02-svm-noyaux.png")
```
<!--sortie-->
```text
NUM noyau_poly 49.0
NUM produit_phi 49.0
NUM acc_lin_moons 0.7583333333333333
NUM acc_rbf_moons 0.9
NUM nsv_lin 61
NUM nsv_rbf 54
NUM n_moons_tr 180
figure : ch02-svm-noyaux.png
```

![Deux SVM sur des données en forme de deux croissants. À gauche, une droite et ses marges (pointillés) : elle sépare mal. À droite, avec un noyau gaussien, la frontière épouse la forme des données. Les points cerclés sont les vecteurs de support.](figures/ch02-svm-noyaux.png)

Sur ces données en deux croissants entremêlés, le SVM linéaire classe correctement 76 % des clients de test, le SVM à noyau gaussien 90 %. Le premier s'appuie sur 61 vecteurs de support, le second sur 54 (sur 180 points d'entraînement).

Sur la résiliation, le SVM exige une chose que le boosting ignore : des variables **à l'échelle** (le noyau gaussien repose sur des distances). Il ne fournit pas directement de probabilités (seulement un score : la distance signée à la frontière, que l'on peut calibrer, section 5.2), et son coût d'entraînement croît environ comme le **carré** du nombre de clients : au-delà de quelques dizaines de milliers de lignes, il devient lent.

```python
from sklearn.svm import SVC

svm = make_pipeline(pre_lin, SVC(kernel="rbf", C=1.0, gamma="scale"))
svm.fit(Xtr, ytr)
print(round(roc_auc_score(yte, svm.decision_function(Xte)), 4))
```
<!--sortie-->
```text
0.8492
```

```python hide
from sklearn.pipeline import Pipeline
sc_svm = svm.decision_function(Xte)
NUM("auc_svm_rbf", roc_auc_score(yte, sc_svm))
lin_svm = make_pipeline(pre_lin, LinearSVC(C=0.05, max_iter=5000)).fit(Xtr, ytr)
NUM("auc_svm_lin", roc_auc_score(yte, lin_svm.decision_function(Xte)))
pre_sans_echelle = ColumnTransformer([("num", SimpleImputer(strategy="median", add_indicator=True), num), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
svm_brut = make_pipeline(pre_sans_echelle, SVC(kernel="rbf", C=1.0, gamma="scale")).fit(Xtr, ytr)
NUM("auc_svm_sans_echelle", roc_auc_score(yte, svm_brut.decision_function(Xte)))
```
<!--sortie-->
```text
NUM auc_svm_rbf 0.8492483138523373
NUM auc_svm_lin 0.8616774072330968
NUM auc_svm_sans_echelle 0.7571155293209635
```

Sur nos clients, le SVM à noyau gaussien atteint une AUC de test de 0,849 et le SVM linéaire 0,862 (à comparer à 0,866 pour la régression logistique : même famille de fonctions, perte différente, résultats voisins). Sans mise à l'échelle des variables, le même SVM à noyau gaussien tombe à 0,757 : la récence en jours écrase tout le reste dans le calcul des distances.

### 2.5.2 Les k plus proches voisins (k-NN)

Le modèle le plus intuitif qui soit : pour prédire un nouveau client, on cherche, dans les données d'entraînement, les **$k$ clients qui lui ressemblent le plus** et l'on prend le vote de leurs classes. Il n'y a pas d'« entraînement » : le modèle **est** les données. Tout repose sur deux choix : la **distance** (en général euclidienne, sur des variables standardisées) et $k$, qui règle le compromis biais-variance du chapitre 1 : $k=1$ colle aux données (variance maximale, frontière en confettis), $k$ très grand lisse tout (biais fort).

**Le fléau de la dimension.** Le k-NN suppose qu'**être proche** a un sens. Or, quand le nombre de variables $d$ grandit, les distances **se concentrent** : tous les points deviennent à peu près aussi éloignés les uns des autres. Pour des points tirés uniformément dans un cube, le rapport entre la distance au voisin le plus proche et la distance au voisin le plus lointain tend vers 1 quand $d$ grandit : la notion de « plus proche voisin » perd son sens.

```python hide
rng = np.random.default_rng(1)
dims = [1, 2, 5, 10, 20, 50, 100, 200, 500]
rapports = []
for d in dims:
    pts = rng.random((600, d)); q = rng.random((60, d))
    dist = np.sqrt(((q[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
    rapports.append(float((dist.min(1) / dist.max(1)).mean()))
NUM("rapport_d2", rapports[1]); NUM("rapport_d10", rapports[3]); NUM("rapport_d500", rapports[-1])
fig, ax = plt.subplots(figsize=(6.6, 3.7))
ax.plot(dims, rapports, color=BLEU, lw=2.2, marker="o", ms=5); ax.set_xscale("log"); ax.set_ylim(0, 1.02)
ax.set_xlabel("nombre de variables $d$ (échelle log)"); ax.set_ylabel("distance au plus proche ÷ distance au plus lointain")
ax.set_title("Le fléau de la dimension : tous les points deviennent « équidistants »")
style.save(fig, "ch02-fleau-dimension.png")

from sklearn.neighbors import KNeighborsClassifier
ks = [1, 3, 5, 15, 50, 150, 400]
cvk = [cross_val_score(make_pipeline(pre_lin, KNeighborsClassifier(k)), Xtr, ytr, cv=cv5, scoring="roc_auc").mean() for k in ks]
k_opt = ks[int(np.argmax(cvk))]
knn = make_pipeline(pre_lin, KNeighborsClassifier(k_opt)).fit(Xtr, ytr)
NUM("k_opt", k_opt); NUM("auc_cv_knn", max(cvk)); NUM("auc_cv_k1", cvk[0]); NUM("auc_knn", roc_auc_score(yte, knn.predict_proba(Xte)[:, 1]))
knn_brut = make_pipeline(pre_sans_echelle, KNeighborsClassifier(k_opt)).fit(Xtr, ytr)
NUM("auc_knn_sans_echelle", roc_auc_score(yte, knn_brut.predict_proba(Xte)[:, 1]))
```
<!--sortie-->
```text
NUM rapport_d2 0.017059328844282483
NUM rapport_d10 0.2829508721942074
NUM rapport_d500 0.8597545981739804
figure : ch02-fleau-dimension.png
NUM k_opt 150
NUM auc_cv_knn 0.849272721351247
NUM auc_cv_k1 0.6434880726574652
NUM auc_knn 0.8578791426089953
NUM auc_knn_sans_echelle 0.8391461641119254
```

![Rapport entre la distance au plus proche voisin et la distance au plus lointain pour des points tirés au hasard, en fonction du nombre de variables : il tend vers 1.](figures/ch02-fleau-dimension.png)

Le rapport moyen est de 0,02 en dimension 2, de 0,28 en dimension 10 et de 0,86 en dimension 500 : dans ce dernier cas, le voisin « le plus proche » est presque aussi loin que le plus lointain. Pour un k-NN, ajouter des variables **inutiles** noie les variables utiles.

Sur la résiliation (45 colonnes après encodage), la validation croisée retient $k=$ 150 (AUC 0,849 ; avec $k=1$, seulement 0,643 : la variance). Sur le jeu de test, l'AUC est de 0,858, et de 0,839 sans mise à l'échelle. Le k-NN fait moins bien que les modèles précédents ici : trop de variables peu informatives, et une prédiction lente (il faut comparer le client à *tous* les autres).

### 2.5.3 Bayes naïf

Le classifieur de **Bayes naïf** applique la règle de Bayes (volume I, section 2.1) en faisant une hypothèse brutale : **les variables sont indépendantes entre elles, une fois la classe connue**. Pour une classe $k$ (parti, resté) et des variables $x_1,\dots,x_p$ :

$$P(k\mid x)\ \propto\ P(k)\prod_{j=1}^pP(x_j\mid k).$$

On n'a donc besoin d'estimer que des lois **à une variable**, ce qui est facile, même avec peu de données. Un exemple chiffré : douze clients, dont 4 sont partis. Parmi les 4 partis, 1 avait ouvert le dernier courriel et 3 avaient ouvert un ticket au support ; parmi les 8 restés, 6 avaient ouvert le courriel et 2 un ticket. Un nouveau client **n'a pas ouvert** le courriel et **a ouvert** un ticket :

- score « parti » : $\frac4{12}\times\frac34\times\frac34=0{,}1875$ ;
- score « resté » : $\frac8{12}\times\frac28\times\frac28=0{,}0417$ ;
- probabilité de départ : $\dfrac{0{,}1875}{0{,}1875+0{,}0417}\approx\mathbf{0{,}818}$.

```python hide
sp = 4 / 12 * 3 / 4 * 3 / 4; sr = 8 / 12 * 2 / 8 * 2 / 8
NUM("nb_score_parti", sp); NUM("nb_score_reste", sr); NUM("nb_proba", sp / (sp + sr))
from sklearn.naive_bayes import GaussianNB
cols_num = [c_ for c_ in num]
nb = make_pipeline(SimpleImputer(strategy="median"), GaussianNB()).fit(Xtr[cols_num], ytr)
p_nb = nb.predict_proba(Xte[cols_num])[:, 1]
NUM("auc_nb", roc_auc_score(yte, p_nb)); NUM("logloss_nb", log_loss(yte, np.clip(p_nb, 1e-4, 1 - 1e-4)))
p_lr_ = test_p["régression logistique"]; yt_ = yte.to_numpy()
for nom_, pp in (("nb", p_nb), ("lr", p_lr_)):
    h = pp > 0.9
    NUM(f"n_{nom_}_haut", int(h.sum())); NUM(f"pred_{nom_}_haut", pp[h].mean() if h.any() else 0); NUM(f"obs_{nom_}_haut", yt_[h].mean() if h.any() else 0)
```
<!--sortie-->
```text
NUM nb_score_parti 0.1875
NUM nb_score_reste 0.041666666666666664
NUM nb_proba 0.8181818181818182
NUM auc_nb 0.8395491080433134
NUM logloss_nb 0.7438849366830594
NUM n_nb_haut 570
NUM pred_nb_haut 0.9687122937916571
NUM obs_nb_haut 0.4263157894736842
NUM n_lr_haut 3
NUM pred_lr_haut 0.9100568337519582
NUM obs_lr_haut 1.0
```

L'hypothèse d'indépendance est presque toujours **fausse** (la récence et le nombre de commandes sont liés) mais, pour **classer**, elle est souvent tolérable : le classement reste raisonnable même quand les probabilités sont fausses. Sur nos données, un Bayes naïf gaussien (sur les variables numériques seules) obtient une AUC de 0,840. En revanche, ses **probabilités** sont mauvaises : en comptant plusieurs fois la même information, il devient **sûr de lui à tort**. Quand il annonce plus de 90 % de risque de départ (570 clients du jeu de test), il prédit en moyenne 97 % alors que 43 % seulement de ces clients partent. À titre de comparaison, la régression logistique annonce plus de 90 % pour 3 clients, avec 91 % prédits et 100 % observés. La perte logistique du Bayes naïf vaut 0,74 (contre 0,28 pour la régression logistique). C'est un exemple parfait de modèle **bien classant mais mal calibré** (section 5.2).

### 2.5.4 Comment choisir entre elles ?

```python hide-code
print(pd.DataFrame({"modèle": ["régression logistique", "SVM linéaire", "SVM gaussien", "k-NN", "Bayes naïf gaussien", "gradient boosting"],
                    "AUC test": [roc_auc_score(yte, test_p["régression logistique"]), roc_auc_score(yte, lin_svm.decision_function(Xte)), roc_auc_score(yte, sc_svm),
                                 roc_auc_score(yte, knn.predict_proba(Xte)[:, 1]), roc_auc_score(yte, p_nb), roc_auc_score(yte, test_p["gradient boosting"])]}).round(4).to_string(index=False))
```
<!--sortie-->
```text
               modèle  AUC test
régression logistique    0.8659
         SVM linéaire    0.8617
         SVM gaussien    0.8492
                 k-NN    0.8579
  Bayes naïf gaussien    0.8395
    gradient boosting    0.9025
```

| Modèle | Hypothèse implicite | Atouts | Faiblesses |
|---|---|---|---|
| SVM à noyau | la ressemblance (le noyau) est bien choisie | peu de données, grande dimension, bonne frontière | exige des variables à l'échelle ; lent au-delà de quelques dizaines de milliers de lignes ; pas de probabilités directes |
| k-NN | les voisins se ressemblent | aucun entraînement, très simple, naturellement non linéaire | fléau de la dimension ; prédiction lente ; sensible à l'échelle |
| Bayes naïf | variables indépendantes entre elles à classe donnée | rapide, peu de données, texte | probabilités mal calibrées ; ignore les interactions |

Le tableau du dessus récapitule les AUC de test : sur ces données, le boosting reste devant. Mais ces trois modèles ont une vertu : ils obligent à penser en termes de **distance**, de **marge** et d'**indépendance**, trois idées qui reviennent partout en apprentissage automatique.

> ✅ **À retenir.**
> - Le **SVM** cherche la droite de **marge maximale** ; il minimise la perte charnière plus une pénalité $\ell_2$. Avec un **noyau** (gaussien, polynomial), il fait des frontières non linéaires sans calculer les variables transformées. Mise à l'échelle obligatoire.
> - Le **k-NN** prédit par vote des $k$ plus proches voisins : $k$ règle le compromis biais-variance ; le **fléau de la dimension** le rend fragile quand les variables sont nombreuses.
> - Le **Bayes naïf** suppose l'indépendance des variables à classe donnée : rapide et robuste pour classer, **mal calibré** pour estimer des probabilités.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.9 (SVM, k-NN, Bayes naïf face au boosting, et le fléau de la dimension), exercice 2.11 (Bayes naïf à la main).
