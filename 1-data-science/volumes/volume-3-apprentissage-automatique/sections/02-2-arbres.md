## 2.2 Arbres de décision

> 💡 **Intuition.** Un arbre de décision, c'est le **questionnaire** que ferait un conseiller expérimenté : « Le client a-t-il commandé il y a plus de 140 jours ? Si oui, est-il satisfait ? Si non, rien à craindre. » Chaque question coupe l'ensemble des clients en deux groupes plus homogènes, et l'on recommence dans chaque groupe. L'arbre **apprend lui-même** les questions à poser, leur ordre et les seuils.

Les arbres ont trois qualités qui expliquent leur succès : ils sont **lisibles** (on peut tracer l'arbre et le raconter), ils n'exigent **ni mise à l'échelle ni imputation** pour fonctionner, et surtout ils écrivent des **règles non linéaires** : seuils, interactions, effets qui changent de sens selon la zone. Leur défaut, nous le verrons, est l'**instabilité**. C'est ce défaut que corrigeront les forêts (section 2.3) et le boosting (section 2.4).

### 2.2.1 Un arbre minuscule, entièrement à la main

Voici dix clients, décrits par la récence (jours depuis la dernière commande), la satisfaction (de 1 à 5) et le fait d'être partis dans les 90 jours.

| Client | Récence | Satisfaction | Parti |
|---|---|---|---|
| 1 | 15 | 4,5 | 0 |
| 2 | 30 | 3,0 | 0 |
| 3 | 45 | 4,0 | 0 |
| 4 | 70 | 4,1 | 0 |
| 5 | 95 | 3,1 | 0 |
| 6 | 120 | 4,4 | 0 |
| 7 | 160 | 3,0 | 1 |
| 8 | 200 | 4,3 | 0 |
| 9 | 260 | 2,9 | 1 |
| 10 | 320 | 3,8 | 1 |

Trois clients sur dix sont partis. Nous cherchons **la meilleure première question**, de la forme « la variable $j$ est-elle inférieure ou égale au seuil $s$ ? ». Pour la comparer à d'autres, il nous faut une mesure de l'**homogénéité** d'un groupe.

### 2.2.2 Mesurer l'impureté

Dans un groupe où une proportion $p$ de clients sont partis, on veut une mesure qui vaut 0 quand le groupe est **pur** ($p=0$ ou $p=1$) et qui est maximale quand il est le plus mélangé ($p=\frac12$). Les trois mesures usuelles, pour deux classes, sont :

| Mesure | Formule | Valeur maximale (en $p=\frac12$) |
|---|---|---|
| Impureté de **Gini** | $G=1-p^2-(1-p)^2=2p(1-p)$ | 0,5 |
| **Entropie** (en bits) | $H=-p\log_2p-(1-p)\log_2(1-p)$ | 1 |
| Taux d'erreur | $E=\min(p,1-p)$ | 0,5 |

L'impureté de Gini est celle qu'utilise `scikit-learn` par défaut. Elle s'interprète ainsi : c'est la probabilité de se tromper si l'on attribue au hasard à un client une étiquette tirée dans le groupe. L'entropie mesure l'information (en bits) qui manque pour connaître l'issue. En pratique, Gini et entropie donnent presque toujours des arbres très voisins ; le taux d'erreur, lui, est trop « plat » pour guider la construction.

```python hide
p = np.linspace(0.001, 0.999, 400)
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.plot(p, 2 * p * (1 - p), color=BLEU, lw=2.2); ax.plot(p, -(p * np.log2(p) + (1 - p) * np.log2(1 - p)) / 2, color=ORANGE, lw=2.2)
ax.plot(p, np.minimum(p, 1 - p), color="#898781", lw=1.8, ls="--")
ax.plot([], [], color=BLEU, lw=2.2, label="Gini"); ax.plot([], [], color=ORANGE, lw=2.2, label="entropie ÷ 2"); ax.plot([], [], color="#898781", lw=1.8, ls="--", label="taux d'erreur")
ax.legend(frameon=False, loc="lower center", fontsize=9.5)
ax.set_xlabel("proportion $p$ de clients partis dans le groupe"); ax.set_ylabel("impureté")
ax.set_title("Trois mesures d'impureté pour un groupe à deux classes")
style.save(fig, "ch02-impuretes.png")
```
<!--sortie-->
```text
figure : ch02-impuretes.png
```

![Impureté d'un groupe en fonction de la proportion de clients partis. Gini et entropie (divisée par deux pour tenir à l'échelle) ont la même allure en cloche ; le taux d'erreur est une tente à pointe.](figures/ch02-impuretes.png)

Pour notre groupe de dix clients ($p=0{,}3$), l'impureté de Gini vaut $1-0{,}3^2-0{,}7^2=1-0{,}09-0{,}49=0{,}42$ et l'entropie $-0{,}3\log_20{,}3-0{,}7\log_20{,}7\approx0{,}881$ bit.

### 2.2.3 Le meilleur découpage : un par un

Une question « récence $\le s$ ? » coupe les clients en un groupe de gauche (de taille $n_G$) et un groupe de droite ($n_D$). Sa qualité est la **diminution d'impureté** :

$$\text{gain}(s)=G(\text{parent})-\frac{n_G}{n}\,G(\text{gauche})-\frac{n_D}{n}\,G(\text{droite}).$$

Il suffit d'essayer, comme seuils candidats, les **milieux** entre deux valeurs consécutives de la variable triée (au-dessus et au-dessous d'un tel seuil, les groupes sont les mêmes, quel que soit le seuil exact choisi dans l'intervalle). Faisons-le à la main pour le seuil $s=140$ (entre 120 et 160) :

- groupe de gauche : les clients 1 à 6, tous restés ($p=0$) : $G=0$ ;
- groupe de droite : les clients 7 à 10, dont trois partis ($p=\frac34$) : $G=1-\frac9{16}-\frac1{16}=0{,}375$ ;
- impureté après découpage : $\frac6{10}\times0+\frac4{10}\times0{,}375=0{,}15$ ; gain $=0{,}42-0{,}15=0{,}27$.

```python hide
ex = pd.DataFrame({"recence": [15, 30, 45, 70, 95, 120, 160, 200, 260, 320],
                   "satisfaction": [4.5, 3.0, 4.0, 4.1, 3.1, 4.4, 3.0, 4.3, 2.9, 3.8],
                   "parti": [0, 0, 0, 0, 0, 0, 1, 0, 1, 1]})
gini = lambda yv: 1 - ((yv == 1).mean()) ** 2 - ((yv == 0).mean()) ** 2 if len(yv) else 0.0
def table_seuils(var):
    v = np.sort(ex[var].unique()); lignes = []
    for s in (v[:-1] + v[1:]) / 2:
        g, d = ex[ex[var] <= s], ex[ex[var] > s]
        imp = (len(g) * gini(g["parti"]) + len(d) * gini(d["parti"])) / len(ex)
        lignes.append({"seuil": s, "gauche (n, partis)": f"{len(g)}, {int(g['parti'].sum())}", "droite (n, partis)": f"{len(d)}, {int(d['parti'].sum())}",
                       "impureté après": imp, "gain": gini(ex["parti"]) - imp})
    return pd.DataFrame(lignes)
t_rec, t_sat = table_seuils("recence"), table_seuils("satisfaction")
NUM("gini_racine", gini(ex["parti"]))
NUM("gain_rec_max", t_rec["gain"].max()); NUM("seuil_rec", t_rec.loc[t_rec["gain"].idxmax(), "seuil"])
NUM("gain_sat_max", t_sat["gain"].max()); NUM("seuil_sat", t_sat.loc[t_sat["gain"].idxmax(), "seuil"])
H = lambda q: -q * np.log2(q) - (1 - q) * np.log2(1 - q)
NUM("entropie_racine", H(0.3))
```
<!--sortie-->
```text
NUM gini_racine 0.4200000000000001
NUM gain_rec_max 0.27000000000000013
NUM seuil_rec 140.0
NUM gain_sat_max 0.1800000000000001
NUM seuil_sat 3.9
NUM entropie_racine 0.8812908992306927
```

```python hide-code
print(t_rec.round(4).to_string(index=False))
```
<!--sortie-->
```text
 seuil gauche (n, partis) droite (n, partis)  impureté après   gain
  22.5               1, 0               9, 3          0.4000 0.0200
  37.5               2, 0               8, 3          0.3750 0.0450
  57.5               3, 0               7, 3          0.3429 0.0771
  82.5               4, 0               6, 3          0.3000 0.1200
 107.5               5, 0               5, 3          0.2400 0.1800
 140.0               6, 0               4, 3          0.1500 0.2700
 180.0               7, 1               3, 2          0.3048 0.1152
 230.0               8, 1               2, 2          0.1750 0.2450
 290.0               9, 2               1, 1          0.3111 0.1089
```

Le tableau reprend ce calcul pour tous les seuils de récence. Le meilleur est bien $s=$ 140, avec un gain de 0,27. Le meilleur seuil de satisfaction ne donne que 0,180 : la première question est donc « **récence ≤ 140 jours ?** ». À gauche, le groupe est pur : on s'arrête, la prédiction est « reste ». À droite, il reste quatre clients (7, 8, 9, 10) dont un est resté (le 8, très satisfait : 4,3) ; on recommence avec la satisfaction : le seuil $s=4{,}05$ sépare les clients 7, 9 et 10 (satisfaction $\le4{,}05$, tous partis) du client 8 (resté). Les deux feuilles sont pures : l'arbre est terminé.

```python hide
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text, plot_tree
petit = DecisionTreeClassifier(max_depth=2, random_state=0).fit(ex[["recence", "satisfaction"]], ex["parti"])
NUM("n_feuilles_petit", petit.get_n_leaves())
NUM("seuil_arbre_1", petit.tree_.threshold[0]); NUM("seuil_arbre_2", petit.tree_.threshold[petit.tree_.children_right[0]])
NUM("acc_petit", petit.score(ex[["recence", "satisfaction"]], ex["parti"]))
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.3), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axs[0]
ax.scatter(ex.loc[ex.parti == 0, "recence"], ex.loc[ex.parti == 0, "satisfaction"], s=55, color=BLEU, label="reste")
ax.scatter(ex.loc[ex.parti == 1, "recence"], ex.loc[ex.parti == 1, "satisfaction"], s=55, color=ORANGE, label="parti")
for i, r in ex.iterrows(): ax.annotate(str(i + 1), (r.recence, r.satisfaction), (4, 5), textcoords="offset points", fontsize=8.5, color="#52514e")
ax.axvline(140, color="#52514e", lw=1.4); ax.plot([140, 340], [4.05, 4.05], color="#52514e", lw=1.4)
ax.set_xlim(0, 340); ax.set_ylim(2.6, 4.8); ax.set_xlabel("récence (jours)"); ax.set_ylabel("satisfaction")
ax.set_title("Les deux questions de l'arbre", fontsize=10.5); ax.legend(frameon=False, loc="lower left", fontsize=8.5)
plot_tree(petit, feature_names=["récence", "satisfaction"], class_names=["reste", "parti"], filled=True, rounded=True, impurity=True, fontsize=8, ax=axs[1], precision=2)
axs[1].set_title("L'arbre appris", fontsize=10.5)
style.save(fig, "ch02-arbre-main.png")
```
<!--sortie-->
```text
NUM n_feuilles_petit 3
NUM seuil_arbre_1 140.0
NUM seuil_arbre_2 4.050000071525574
NUM acc_petit 1.0
figure : ch02-arbre-main.png
```

![À gauche : les dix clients dans le plan (récence, satisfaction) et les deux coupes de l'arbre. À droite : l'arbre appris par scikit-learn, qui retrouve exactement les seuils du calcul à la main.](figures/ch02-arbre-main.png)

`scikit-learn` retrouve exactement ce calcul : première coupe à 140 jours, seconde à 4,05, 3 feuilles pures. L'arbre peut se lire comme deux règles : « **si la récence dépasse 140 jours *et* la satisfaction est inférieure à 4,05, alors le client part** ; sinon il reste ». Remarquez que cette règle est une **interaction** : ni la récence seule ni la satisfaction seule ne suffit à prédire. Un score linéaire n'aurait pas pu l'écrire.

> 📐 **L'algorithme, en toutes lettres (CART).** Pour construire un arbre à partir d'un jeu d'exemples : (1) pour **chaque variable** et **chaque seuil candidat**, calculer le gain d'impureté ; (2) retenir la coupe de **gain maximal** ; (3) recommencer **séparément** dans chacun des deux groupes ; (4) s'arrêter quand un critère d'arrêt est atteint (groupe pur, profondeur maximale, trop peu de clients). C'est un algorithme **glouton** : il choisit la meilleure coupe *maintenant*, sans se demander si une coupe moins bonne aujourd'hui permettrait de meilleures coupes demain. Il ne trouve donc pas forcément **le** meilleur arbre, mais il en trouve un bon très vite : en triant une fois chaque variable, évaluer tous les seuils d'une variable coûte de l'ordre de $n\log n$.
>
> La **prédiction** d'une feuille est la classe majoritaire (ou la proportion de clients partis, utilisée comme probabilité) des exemples d'entraînement qui y tombent. Les variables catégorielles se traitent par des questions « la modalité est-elle dans cet ensemble ? » ou, dans `scikit-learn`, après encodage en indicatrices ; les valeurs manquantes sont gérées nativement par les versions récentes.

### 2.2.4 Les arbres de régression

Pour prédire une **quantité** (la dépense des six prochains mois, par exemple), la prédiction d'une feuille est la **moyenne** des valeurs de ses exemples, et le critère de coupe est la **réduction de la somme des carrés des écarts** (les écarts à la moyenne du groupe). Un exemple minuscule : six clients, $x$ = nombre de commandes et $y$ = dépense (en €).

| $x$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| $y$ | 10 | 14 | 12 | 40 | 44 | 42 |

La moyenne générale vaut 27, et la somme des carrés des écarts $(10-27)^2+(14-27)^2+\dots=$ 1366. La coupe « $x\le3$ » donne deux feuilles : à gauche la moyenne est 12 (écarts : −2, +2, 0 : somme des carrés 8), à droite la moyenne est 42 (écarts −2, +2, 0 : somme des carrés 8). Après la coupe, la somme des carrés tombe de 1366 à 16 : le modèle prédit 12 pour les petits acheteurs et 42 pour les gros. C'est une fonction **en escalier**.

```python hide
xr = np.arange(1, 7).reshape(-1, 1); yr = np.array([10, 14, 12, 40, 44, 42.0])
reg = DecisionTreeRegressor(max_depth=1).fit(xr, yr)
NUM("sse_total", ((yr - yr.mean()) ** 2).sum()); NUM("sse_apres", ((yr[:3] - 12) ** 2).sum() + ((yr[3:] - 42) ** 2).sum())
NUM("seuil_reg", reg.tree_.threshold[0]); NUM("val_gauche", reg.tree_.value[1][0][0]); NUM("val_droite", reg.tree_.value[2][0][0])
```
<!--sortie-->
```text
NUM sse_total 1366.0
NUM sse_apres 16.0
NUM seuil_reg 3.5
NUM val_gauche 12.0
NUM val_droite 42.0
```

### 2.2.5 Jusqu'où laisser pousser l'arbre ?

Un arbre qu'on laisse pousser sans limite finit par isoler **chaque client** dans sa propre feuille : l'erreur d'entraînement tombe à zéro, mais l'arbre a appris le bruit. C'est l'exemple le plus pur de **surapprentissage** (volume III, section 1.3). On contrôle la complexité par des **hyperparamètres** : la profondeur maximale, le nombre minimal de clients par feuille, ou le nombre maximal de feuilles.

Voyons-le sur la résiliation : pour des profondeurs croissantes, on mesure l'AUC sur l'entraînement et, par validation croisée à cinq plis **à l'intérieur** de l'entraînement, sur des clients que l'arbre n'a pas vus.

```python hide
from sklearn.model_selection import cross_val_score
cv5 = StratifiedKFold(5, shuffle=True, random_state=0)
profs = list(range(1, 15))
res = []
for d in profs:
    m = DecisionTreeClassifier(max_depth=d, min_samples_leaf=5, random_state=0)
    auc_tr = roc_auc_score(ytr, m.fit(Xtr_o, ytr).predict_proba(Xtr_o)[:, 1])
    auc_cv = cross_val_score(m, Xtr_o, ytr, cv=cv5, scoring="roc_auc").mean()
    res.append((d, auc_tr, auc_cv))
res = pd.DataFrame(res, columns=["profondeur", "AUC entraînement", "AUC validation"])
d_opt = int(res.loc[res["AUC validation"].idxmax(), "profondeur"])
arbre_opt = DecisionTreeClassifier(max_depth=d_opt, min_samples_leaf=5, random_state=0).fit(Xtr_o, ytr)
NUM("prof_opt", d_opt); NUM("auc_cv_prof_opt", res["AUC validation"].max()); NUM("auc_test_arbre", roc_auc_score(yte, arbre_opt.predict_proba(Xte_o)[:, 1]))
NUM("auc_tr_prof14", res["AUC entraînement"].iloc[-1]); NUM("auc_cv_prof14", res["AUC validation"].iloc[-1]); NUM("auc_cv_prof2", res["AUC validation"].iloc[1])
fig, ax = plt.subplots(figsize=(7.0, 3.9))
ax.plot(res["profondeur"], res["AUC entraînement"], color=ORANGE, lw=2.2, marker="o", ms=4); ax.plot(res["profondeur"], res["AUC validation"], color=BLEU, lw=2.2, marker="o", ms=4)
ax.axvline(d_opt, color="#c3c2b7", lw=1.2, ls="--")
ax.text(1.2, 0.975 * res["AUC entraînement"].max(), "entraînement", color=ORANGE, fontsize=9.5); ax.text(7.2, res["AUC validation"].max() - 0.025, "validation croisée", color=BLEU, fontsize=9.5)
ax.set_xlabel("profondeur maximale de l'arbre"); ax.set_ylabel("AUC"); ax.set_title("Un arbre trop profond apprend le bruit")
style.save(fig, "ch02-arbre-profondeur.png")
```
<!--sortie-->
```text
NUM prof_opt 5
NUM auc_cv_prof_opt 0.8630064145279306
NUM auc_test_arbre 0.8846884990131328
NUM auc_tr_prof14 0.9805622222422211
NUM auc_cv_prof14 0.74853717914358
NUM auc_cv_prof2 0.7926417257087721
figure : ch02-arbre-profondeur.png
```

![AUC d'un arbre de décision selon sa profondeur maximale : sur l'entraînement elle monte sans cesse, en validation croisée elle atteint un sommet puis redescend.](figures/ch02-arbre-profondeur.png)

La courbe d'entraînement (orange) monte sans cesse, jusqu'à 0,981 pour une profondeur de 14. La courbe de validation (bleue) monte jusqu'à une profondeur de **5** (AUC 0,863), puis **redescend** : au-delà, l'arbre mémorise. C'est la signature classique de l'arbitrage biais-variance. Un arbre trop court (profondeur 2) est trop simple (AUC 0,793 en validation) ; un arbre trop profond (14) a trop de liberté (0,749). Sur le jeu de test, l'arbre de profondeur 5 obtient une AUC de **0,885**, contre 0,866 pour la régression logistique.

```python
from sklearn.tree import DecisionTreeClassifier

arbre = DecisionTreeClassifier(max_depth=d_opt, min_samples_leaf=5, random_state=0)
arbre.fit(Xtr_o, ytr)
print(round(roc_auc_score(yte, arbre.predict_proba(Xte_o)[:, 1]), 4))
```
<!--sortie-->
```text
0.8847
```

(Ici, `Xtr_o` est le tableau d'entraînement dont les catégories ont été transformées en indicatrices, et `d_opt` la profondeur retenue par la validation croisée.)

**Une autre façon de limiter : élaguer.** Plutôt que d'interdire à l'arbre de grandir, on le laisse pousser puis on **coupe les branches** qui apportent trop peu. L'élagage par **coût-complexité** minimise
$$R_\alpha(T)=R(T)+\alpha\,|T|,$$
où $R(T)$ est l'erreur de l'arbre $T$ sur l'entraînement, $|T|$ son nombre de feuilles et $\alpha\ge0$ le prix d'une feuille supplémentaire. Pour $\alpha=0$, on garde tout ; quand $\alpha$ augmente, on supprime d'abord la branche dont la suppression coûte le moins par feuille retirée, et ainsi de suite jusqu'à la racine. On obtient une **suite d'arbres emboîtés**, et la validation croisée choisit $\alpha$.

```python hide
base = DecisionTreeClassifier(min_samples_leaf=5, random_state=0)
alphas = np.unique(np.round(base.cost_complexity_pruning_path(Xtr_o, ytr).ccp_alphas, 7))
alphas = alphas[np.linspace(0, len(alphas) - 1, 30).astype(int)] if len(alphas) > 30 else alphas
alphas = alphas[alphas < 0.01]
lignes = []
for a in alphas:
    m = DecisionTreeClassifier(min_samples_leaf=5, ccp_alpha=a, random_state=0)
    lignes.append((a, cross_val_score(m, Xtr_o, ytr, cv=cv5, scoring="roc_auc").mean(), m.fit(Xtr_o, ytr).get_n_leaves()))
elag = pd.DataFrame(lignes, columns=["alpha", "AUC validation", "feuilles"])
a_opt = elag.loc[elag["AUC validation"].idxmax()]
arbre_elague = DecisionTreeClassifier(min_samples_leaf=5, ccp_alpha=a_opt["alpha"], random_state=0).fit(Xtr_o, ytr)
NUM("alpha_opt", a_opt["alpha"]); NUM("feuilles_opt", a_opt["feuilles"]); NUM("auc_cv_elague", a_opt["AUC validation"])
NUM("feuilles_complet", DecisionTreeClassifier(min_samples_leaf=5, random_state=0).fit(Xtr_o, ytr).get_n_leaves())
NUM("auc_test_elague", roc_auc_score(yte, arbre_elague.predict_proba(Xte_o)[:, 1]))
fig, ax = plt.subplots(figsize=(7.0, 3.9)); ax2 = ax.twinx()
ax.plot(elag["alpha"].clip(lower=1e-6), elag["AUC validation"], color=BLEU, lw=2.2, marker="o", ms=4); ax2.plot(elag["alpha"].clip(lower=1e-6), elag["feuilles"], color="#898781", lw=1.6, ls="--")
ax.set_xscale("log"); ax.set_xlabel("prix d'une feuille  α  (échelle log)"); ax.set_ylabel("AUC en validation croisée", color=BLEU); ax2.set_ylabel("nombre de feuilles", color="#898781"); ax2.grid(False)
ax.axvline(max(a_opt["alpha"], 1e-6), color=ORANGE, lw=1.2, ls=":"); ax.set_title("Élaguer : un compromis entre précision et nombre de feuilles")
style.save(fig, "ch02-arbre-elagage.png")
```
<!--sortie-->
```text
NUM alpha_opt 0.0006474
NUM feuilles_opt 20.0
NUM auc_cv_elague 0.8612553979642195
NUM feuilles_complet 458
NUM auc_test_elague 0.8728414869229727
figure : ch02-arbre-elagage.png
```

![Élagage par coût-complexité : l'AUC en validation croisée (courbe bleue, axe de gauche) selon le prix α d'une feuille, et le nombre de feuilles de l'arbre (tirets gris, axe de droite). Le maximum (pointillé orange) correspond à un petit arbre d'une vingtaine de feuilles ; un arbre complet de 458 feuilles généralise moins bien.](figures/ch02-arbre-elagage.png)

Ici, l'élagage retient $\alpha\approx$ 0,0006 : un arbre de 20 feuilles (au lieu de 458 pour l'arbre complet), d'AUC de validation 0,861 et d'AUC de test 0,873. Les deux méthodes (limiter la profondeur, élaguer) conduisent à des arbres comparables : retenons que **la complexité d'un arbre est un réglage à choisir par validation**, jamais à laisser au maximum.

### 2.2.6 Ce que les arbres savent écrire : effets non linéaires et interactions

Sur les données de résiliation, la régression logistique atteint 0,866 et l'arbre de profondeur 5 0,885 : un arbre **seul** dépasse déjà un peu le modèle linéaire. D'où vient l'écart ? Il ne vient pas d'une grande découverte, mais de **plusieurs petites formes** que le score linéaire ne sait pas écrire. Voyons les deux plus parlantes.

**Un effet qui sature : le nombre de commandes.** Un score linéaire attribue à une variable un effet qui va **toujours dans le même sens et au même rythme** : chaque commande supplémentaire retranche la même quantité de log-cote, que l'on passe de 0 à 1 commande ou de 11 à 12. Or le risque de départ ne se comporte pas ainsi : il est très élevé pour les clients qui n'ont **rien commandé** en douze mois, il chute dès les premières commandes, puis **se stabilise** : au-delà d'une demi-douzaine de commandes, une de plus ne change plus rien.

```python hide
from sklearn.preprocessing import StandardScaler
n_tr, n_te = Xtr[["nb_commandes_12m"]], Xte[["nb_commandes_12m"]]
lr_nb = make_pipeline(StandardScaler(), LogisticRegression()).fit(n_tr, ytr)
ar_nb = DecisionTreeClassifier(max_depth=3, min_samples_leaf=100, random_state=0).fit(n_tr, ytr)
NUM("auc_lr_nb", roc_auc_score(yte, lr_nb.predict_proba(n_te)[:, 1])); NUM("auc_arbre_nb", roc_auc_score(yte, ar_nb.predict_proba(n_te)[:, 1]))
obs_nb = ytr.groupby(np.minimum(Xtr["nb_commandes_12m"], 14)).agg(["mean", "size"])
NUM("taux_0cmd", obs_nb.loc[0, "mean"]); NUM("taux_1_2cmd", ytr[Xtr["nb_commandes_12m"].between(1, 2)].mean()); NUM("taux_6pluscmd", ytr[Xtr["nb_commandes_12m"] >= 6].mean())
duo2 = ["age", "nb_commandes_12m"]
lr2 = make_pipeline(StandardScaler(), LogisticRegression()).fit(Xtr[duo2], ytr)
ar2 = DecisionTreeClassifier(max_depth=5, min_samples_leaf=80, random_state=0).fit(Xtr[duo2], ytr)
NUM("auc_lr_2var", roc_auc_score(yte, lr2.predict_proba(Xte[duo2])[:, 1])); NUM("auc_arbre_2var", roc_auc_score(yte, ar2.predict_proba(Xte[duo2])[:, 1]))
g_nb = pd.DataFrame({"nb_commandes_12m": np.linspace(0, 14, 200)})
g1, g2 = np.meshgrid(np.linspace(18, 78, 200), np.linspace(0, 20, 200)); Gm = pd.DataFrame({"age": g1.ravel(), "nb_commandes_12m": g2.ravel()})
fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.0), gridspec_kw={"width_ratios": [1.2, 1, 1]})
ax = axs[0]
ax.scatter(obs_nb.index, obs_nb["mean"], s=obs_nb["size"] / 12, color="#898781", alpha=0.85, label="taux observé (la taille du point = effectif)")
ax.plot(g_nb["nb_commandes_12m"], lr_nb.predict_proba(g_nb)[:, 1], color=ORANGE, lw=2.2, label="régression logistique")
ax.plot(g_nb["nb_commandes_12m"], ar_nb.predict_proba(g_nb)[:, 1], color=BLEU, lw=2.2, drawstyle="steps-mid", label="arbre (profondeur 3)")
ax.set_xlabel("nombre de commandes (12 mois ; 14 = 14 ou plus)"); ax.set_ylabel("probabilité de départ"); ax.set_title("Un effet qui sature", fontsize=10.5); ax.legend(frameon=False, fontsize=8, loc="upper right")
for ax, mod, titre in ((axs[1], lr2, "Logistique : bandes obliques"), (axs[2], ar2, "Arbre : rectangles")):
    Z = mod.predict_proba(Gm)[:, 1].reshape(g1.shape)
    im = ax.contourf(g1, g2, Z, levels=np.linspace(0, 0.8, 9), cmap=style.SEQ, extend="max", alpha=0.95); ax.set_title(titre, fontsize=9.5); ax.set_xlabel("âge")
axs[1].set_ylabel("commandes (12 mois)"); axs[2].set_yticklabels([]); fig.colorbar(im, ax=axs[1:], label="probabilité de départ prédite", shrink=0.85)
style.save(fig, "ch02-regions-lineaire-arbre.png")
```
<!--sortie-->
```text
NUM auc_lr_nb 0.7658191182389462
NUM auc_arbre_nb 0.7621433485699866
NUM taux_0cmd 0.4182572614107884
NUM taux_1_2cmd 0.14889402443050512
NUM taux_6pluscmd 0.023287671232876714
NUM auc_lr_2var 0.8141760740643181
NUM auc_arbre_2var 0.8310817593959616
figure : ch02-regions-lineaire-arbre.png
```

![À gauche : le taux de départ observé selon le nombre de commandes (points gris), la prédiction d'une régression logistique (une courbe lisse qui ne sature pas) et celle d'un arbre (un escalier qui épouse le saut à 0 commande et le plateau). Au centre et à droite : probabilité de départ prédite en fonction de l'âge et du nombre de commandes, par une régression logistique (bandes obliques) et par un arbre (rectangles).](figures/ch02-regions-lineaire-arbre.png)

Le taux de départ observé est de 42 % pour les clients sans commande, de 15 % pour ceux qui en ont une ou deux, de 2 % à partir de six. Avec cette seule variable, la régression logistique atteint une AUC de test de 0,766 et l'arbre de profondeur 3 de 0,762 : la différence est faible, mais l'arbre dessine ce que montrent les données (un saut, puis un plateau), alors que la courbe logistique continue à descendre. Avec **deux** variables (le nombre de commandes et l'âge), les cartes de droite montrent la différence de **forme** : la régression logistique ne sait tracer que des bandes obliques, l'arbre découpe des rectangles, et isole notamment la bande horizontale des clients sans commande. L'AUC passe à 0,814 pour la première et à 0,831 pour le second.

**Une interaction : deux conditions à la fois.** La récence et la satisfaction illustrent l'autre limite. Regardons le taux de départ observé selon que la récence dépasse 150 jours et que la satisfaction est inférieure à 3,2 (en laissant de côté les clients dont la satisfaction manque), puis comparons-le à ce que prédit un modèle **additif** (logistique) sur ces deux variables.

```python hide
tr_obs = Xtr["satisfaction_moy"].notna()
Z2 = Xtr.loc[tr_obs, ["recence_jours", "satisfaction_moy"]]; y2 = ytr[tr_obs]
add = make_pipeline(StandardScaler(), LogisticRegression()).fit(Z2, y2)
quad = pd.DataFrame({"récence": np.where(Z2["recence_jours"] > 150, "> 150 jours", "≤ 150 jours"), "satisfaction": np.where(Z2["satisfaction_moy"] < 3.2, "< 3,2", "≥ 3,2"),
                     "observé": y2.to_numpy(), "additif": add.predict_proba(Z2)[:, 1]})
qt = quad.groupby(["récence", "satisfaction"]).agg(clients=("observé", "size"), observé=("observé", "mean"), additif=("additif", "mean")).reset_index()
cel = lambda r, sa: qt[(qt["récence"] == r) & (qt["satisfaction"] == sa)].iloc[0]
coin, base, rec, sat = cel("> 150 jours", "< 3,2"), cel("≤ 150 jours", "≥ 3,2"), cel("> 150 jours", "≥ 3,2"), cel("≤ 150 jours", "< 3,2")
NUM("n_coin", coin["clients"]); NUM("taux_coin", coin["observé"]); NUM("pred_coin", coin["additif"]); NUM("taux_base", base["observé"])
NUM("taux_rec_seule", rec["observé"]); NUM("taux_sat_seule", sat["observé"]); NUM("rapport_coin_base", coin["observé"] / base["observé"])
NUM("pred_rec", rec["additif"]); NUM("pred_sat", sat["additif"])
```
<!--sortie-->
```text
NUM n_coin 562
NUM taux_coin 0.7170818505338078
NUM pred_coin 0.5070527087854765
NUM taux_base 0.06423895253682488
NUM taux_rec_seule 0.21703703703703703
NUM taux_sat_seule 0.1213546566321731
NUM rapport_coin_base 11.16272638665367
NUM pred_rec 0.2913260805366343
NUM pred_sat 0.15877893799724202
```

```python hide-code
print(qt.round(3).to_string(index=False))
```
<!--sortie-->
```text
    récence satisfaction  clients  observé  additif
> 150 jours        < 3,2      562    0.717    0.507
> 150 jours        ≥ 3,2     1350    0.217    0.291
≤ 150 jours        < 3,2     1063    0.121    0.159
≤ 150 jours        ≥ 3,2     4888    0.064    0.060
```

Dans le coin « récence > 150 jours *et* satisfaction < 3,2 » (562 clients d'entraînement), le taux de départ observé est de **72 %**. Pour les clients qui ne remplissent aucune des deux conditions, il est de 6 % ; chaque condition **seule** le fait monter à 12 % (satisfaction basse) ou 22 % (récence élevée) ; les deux **ensemble** le multiplient par 11. Or un modèle additif ne peut qu'**ajouter** les deux effets (sur l'échelle de la log-cote) : il prédit 51 % pour le coin, soit vingt points de moins que la réalité, et surestime les deux cases voisines (29 % et 16 % prédits, contre 22 % et 12 % observés). Un arbre écrit cela avec deux questions.

> 💡 **La vérité programmée.** Ces données sont simulées : nous pouvons donc révéler ce qui les produit. Le risque de départ contient bien une forte hausse quand la récence dépasse **150 jours** *et* la satisfaction est inférieure à **3,2** (un terme d'interaction), un effet du nombre de commandes qui **sature** à six, un surcroît de risque pour les clients anciens sans aucune commande, et d'autres interactions (trois tickets au support et beaucoup de retours ; beaucoup de promotions sans programme de fidélité). Le modèle linéaire en capte la part régulière ; les arbres captent aussi ces formes irrégulières, et la somme de ces petits gains explique l'écart global entre 0,866 et 0,885.

### 2.2.7 Le point faible : l'instabilité

Si les arbres sont aussi pratiques, pourquoi ne s'arrête-t-on pas là ? Parce qu'un arbre est **instable** : une petite modification des données peut changer complètement la première question, donc tout ce qui suit. L'algorithme étant glouton, une coupe presque aussi bonne que la meilleure, mais portant sur une autre variable, change toute la suite de l'arbre.

Mesurons-le sur un jeu modeste : on tire 30 sous-échantillons de **2 000 clients** dans le jeu d'entraînement, on ajuste sur chacun un arbre de profondeur 4 et l'on regarde **quelle variable ouvre l'arbre**. (Avec les 9 000 clients complets, la première variable serait presque toujours la même ; c'est le **seuil** et la **suite** qui bougent, comme on le voit plus bas.)

```python hide
rng = np.random.default_rng(3)
racines, preds = [], []
for b in range(30):
    idx = rng.choice(len(Xtr_o), 2000, replace=False)
    m = DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=0).fit(Xtr_o.iloc[idx], ytr.iloc[idx])
    racines.append(Xtr_o.columns[m.tree_.feature[0]]); preds.append(m.predict_proba(Xte_o)[:, 1])
freq = pd.Series(racines).value_counts()
cm_ = np.corrcoef(np.array(preds))
NUM("n_racines_distinctes", len(freq)); NUM("freq_racine_top", freq.iloc[0]); NUM("nom_racine_top", freq.index[0]); NUM("freq_racine_2", freq.iloc[1]); NUM("nom_racine_2", freq.index[1])
NUM("corr_arbres", cm_[np.triu_indices(30, 1)].mean())
# avec les 9 000 clients (bootstrap) : même variable, mais quel seuil ?
rng = np.random.default_rng(3); seuils = []
for b in range(30):
    idx = rng.integers(0, len(Xtr_o), len(Xtr_o))
    m = DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=0).fit(Xtr_o.iloc[idx], ytr.iloc[idx]); seuils.append((Xtr_o.columns[m.tree_.feature[0]], m.tree_.threshold[0]))
NUM("seuil_min", min(s for _, s in seuils)); NUM("seuil_max", max(s for _, s in seuils)); NUM("nb_var_racine_9000", len({v for v, _ in seuils}))
```
<!--sortie-->
```text
NUM n_racines_distinctes 4
NUM freq_racine_top 19
NUM nom_racine_top recence_jours
NUM freq_racine_2 5
NUM nom_racine_2 age
NUM corr_arbres 0.7790334392154666
NUM seuil_min 155.5
NUM seuil_max 312.5
NUM nb_var_racine_9000 1
```

Sur 30 sous-échantillons de 2 000 clients, 4 variables différentes ouvrent l'arbre : `recence_jours` dans 19 cas, `age` dans 5 cas, et les autres variables dans les cas restants. Et même quand la variable est la même, le seuil change : avec les 9 000 clients, 1 seule variable ouvre les 30 arbres bootstrap, mais le seuil de la première coupe va de 156 à 312 jours. Les prédictions de deux arbres de ce type ne sont corrélées qu'à 0,78 en moyenne sur le jeu de test : **chaque arbre raconte une histoire différente**. En termes du chapitre 1, un arbre profond a un **biais** faible et une **variance** élevée. Or il existe un remède universel contre la variance : **moyenner**. C'est le sujet de la section suivante.

> ✅ **À retenir.**
> - Un arbre pose une suite de questions « variable ≤ seuil ? » ; il est construit **gloutonnement**, en maximisant à chaque étape la **diminution d'impureté** (Gini ou entropie en classification, somme des carrés en régression).
> - Il capture **seuils et interactions** et n'exige ni standardisation ni modèle de la loi des données ; ses règles sont lisibles.
> - Sa complexité (profondeur, taille minimale des feuilles, élagage par coût-complexité $R(T)+\alpha|T|$) est un **hyperparamètre à régler par validation croisée**.
> - Il est **instable** : forte variance, d'où les forêts (2.3) et le boosting (2.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3 (construire un arbre à la main puis avec `scikit-learn`, élaguer), exercices 2.4 à 2.6.
