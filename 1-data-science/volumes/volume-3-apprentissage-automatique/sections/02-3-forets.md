## 2.3 Forêts aléatoires

> 💡 **Intuition.** Demandez à un seul expert d'estimer le poids d'un bœuf : il se trompera, dans un sens ou dans l'autre. Demandez à cent experts **indépendants** et faites la moyenne : les erreurs de signes opposés se compensent, et l'on tombe très près de la vérité. Une forêt aléatoire est cette foule : des centaines d'arbres, chacun entraîné sur une version un peu différente des données, dont on moyenne les prédictions. Chaque arbre est instable (section 2.2.7) ; **la moyenne ne l'est presque plus**.

### 2.3.1 Le bagging : moyenner des arbres entraînés sur des échantillons bootstrap

L'idée porte le nom de **bagging** (*bootstrap aggregating*, Breiman, 1996). Pour construire $B$ arbres, on répète $B$ fois : (1) tirer un **échantillon bootstrap** : $n$ clients tirés **avec remise** dans le jeu d'entraînement (certains clients apparaissent plusieurs fois, d'autres jamais) ; (2) ajuster un arbre profond sur cet échantillon. Pour prédire, on moyenne les $B$ probabilités prédites (ou on prend le vote majoritaire).

Combien de clients distincts un échantillon bootstrap contient-il ? Un client donné n'est **pas** tiré à un tirage donné avec la probabilité $1-\frac1n$, donc il n'est tiré **jamais** sur les $n$ tirages avec la probabilité $\bigl(1-\frac1n\bigr)^n\to e^{-1}\approx0{,}368$. Un échantillon bootstrap contient donc, en moyenne, **63,2 %** des clients distincts, et environ **36,8 %** des clients sont laissés de côté. Ces clients « hors sac » nous serviront en 2.3.4.

```python hide
rng = np.random.default_rng(0)
n = len(Xtr)
idx = rng.integers(0, n, n)
NUM("frac_distincts_theorie", 1 - np.exp(-1)); NUM("frac_distincts_bootstrap", len(np.unique(idx)) / n)
```
<!--sortie-->
```text
NUM frac_distincts_theorie 0.6321205588285577
NUM frac_distincts_bootstrap 0.6343333333333333
```

Vérification sur notre jeu d'entraînement : un échantillon bootstrap contient 63,4 % de clients distincts, pour une valeur théorique de 63,2 %.

### 2.3.2 Pourquoi moyenner réduit la variance : la formule

Soient $B$ prédictions $T_1,\dots,T_B$ (celles de $B$ arbres, en un point $x$ fixé), de même variance $\sigma^2$ et de **corrélation** deux à deux $\rho$. Leur moyenne a pour variance

$$\operatorname{Var}\Bigl(\frac1B\sum_{b=1}^BT_b\Bigr)=\frac1{B^2}\Bigl[\underbrace{B\sigma^2}_{\text{variances}}+\underbrace{B(B-1)\rho\sigma^2}_{\text{covariances}}\Bigr]=\rho\,\sigma^2+\frac{1-\rho}{B}\,\sigma^2.$$

> 📐 **Lecture de la formule.** Le second terme, $\frac{1-\rho}B\sigma^2$, **disparaît quand $B$ augmente** : c'est la part de variance que la moyenne élimine. Le premier, $\rho\sigma^2$, **reste** : si les arbres sont corrélés, moyenner à l'infini n'enlève pas leur erreur commune. Deux cas extrêmes : si les arbres étaient **indépendants** ($\rho=0$), la variance serait divisée par $B$ ; s'ils étaient **identiques** ($\rho=1$), la moyenne ne servirait à rien, la variance resterait $\sigma^2$. Un autre point mérite d'être noté : la moyenne ne change pas le **biais** (c'est la moyenne des biais), c'est pourquoi on moyenne des arbres **profonds**, au biais faible et à la variance forte.

Un exemple chiffré avec $\sigma^2=1$ et $\rho=0{,}3$ : pour $B=1$ la variance vaut 1 ; pour $B=10$, $0{,}3+0{,}07=0{,}37$ ; pour $B=100$, $0{,}3+0{,}007=0{,}307$ ; pour $B\to\infty$, $0{,}3$. On a éliminé presque toute la variance « évitable » avec une centaine d'arbres, mais jamais les 30 % dus à la corrélation.

Voyons ce que cela donne avec de vrais arbres. On tire 12 sous-échantillons de 4 500 clients dans le jeu d'entraînement (12 « jeux de données » différents) ; sur chacun on ajuste 30 arbres bootstrap. Pour 800 clients du jeu de test, on mesure la variance de la prédiction d'un seul arbre, puis de la moyenne de 5, 15, 30 arbres, **d'un jeu de données à l'autre**.

```python hide
from sklearn.ensemble import RandomForestClassifier

def experience(max_features, S=12, B=30, taille=4500, graine=11):
    rng = np.random.default_rng(graine)
    test_pts = Xte_o.iloc[:800]
    P = np.zeros((S, B, len(test_pts)))
    for s in range(S):
        sub = rng.choice(len(Xtr_o), taille, replace=False)
        for b in range(B):
            bt = rng.choice(sub, taille, replace=True)
            t = DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, max_features=max_features, random_state=int(rng.integers(1e9)))
            P[s, b] = t.fit(Xtr_o.iloc[bt], ytr.iloc[bt]).predict_proba(test_pts)[:, 1]
    return P

def resume(P, tailles=(1, 5, 15, 30)):
    S, B, _ = P.shape
    var1 = P.reshape(S * B, -1).var(0).mean()                       # variance d'un arbre, d'un jeu de données à l'autre et d'un arbre à l'autre
    cov = []                                                          # corrélation de deux arbres issus du même jeu de données
    for x in range(P.shape[2]):
        a, c = P[:, 0, x], P[:, 1, x]
        cov.append(np.cov(a, c)[0, 1])
    rho = float(np.mean(cov) / var1)
    mesure = {k: float(P[:, :k, :].mean(1).var(0).mean()) for k in tailles}
    theorie = {k: rho * var1 + (1 - rho) * var1 / k for k in tailles}
    return var1, rho, mesure, theorie

P_bag = experience(None)
v1, rho_bag, mes_bag, th_bag = resume(P_bag)
NUM("rho_bagging", rho_bag); NUM("var_1_arbre", v1); NUM("plancher_bag", rho_bag * v1)
for k in (1, 5, 15, 30):
    NUM(f"var_bag_{k}", mes_bag[k]); NUM(f"theo_bag_{k}", th_bag[k])
```
<!--sortie-->
```text
NUM rho_bagging 0.04571574677673051
NUM var_1_arbre 0.03270941540828654
NUM plancher_bag 0.0014953353520201146
NUM var_bag_1 0.030599802499028696
NUM theo_bag_1 0.03270941540828654
NUM var_bag_5 0.007094197545463007
NUM theo_bag_5 0.0077381513632734005
NUM var_bag_15 0.003401460710661984
NUM theo_bag_15 0.003576274022437876
NUM var_bag_30 0.002526354593496651
NUM theo_bag_30 0.0025358046872289955
```

```python hide-code
tab = pd.DataFrame({"arbres moyennés": [1, 5, 15, 30], "variance mesurée": [mes_bag[k] for k in (1, 5, 15, 30)], "formule ρσ² + (1−ρ)σ²/B": [th_bag[k] for k in (1, 5, 15, 30)]})
print(tab.round(5).to_string(index=False))
```
<!--sortie-->
```text
 arbres moyennés  variance mesurée  formule ρσ² + (1−ρ)σ²/B
               1           0.03060                  0.03271
               5           0.00709                  0.00774
              15           0.00340                  0.00358
              30           0.00253                  0.00254
```

La variance d'un seul arbre est 0,0327 ; la corrélation estimée entre deux arbres du même jeu de données est 0,05, ce qui fixe un plancher $\rho\sigma^2\approx$ 0,0015. La corrélation est modeste en valeur absolue parce qu'une grande part de la variance d'un arbre profond vient de l'aléa du bootstrap lui-même, que la moyenne élimine ; mais c'est la part restante qui compte quand $B$ est grand. En moyennant 30 arbres, la variance mesurée tombe à 0,0025, soit une division par environ 12,9 ; la colonne de droite montre que la formule, alimentée par ces deux estimations, retrouve les variances mesurées (à l'échantillonnage près : seulement 12 jeux de données).

```python hide
NUM("ratio_bag", v1 / mes_bag[30])
```
<!--sortie-->
```text
NUM ratio_bag 12.947278063216942
```

### 2.3.3 La forêt aléatoire : décorréler les arbres

Le bagging a un défaut : si une variable est très prédictive (la récence, ici), **tous** les arbres l'utilisent en première coupe, donc se ressemblent : $\rho$ reste élevé. Les **forêts aléatoires** (*random forests*, Breiman, 2001) ajoutent une idée simple : à **chaque coupe**, l'arbre ne considère qu'un **sous-ensemble tiré au hasard** de $m$ variables parmi $p$ (par défaut $m=\sqrt p$ en classification). Une variable dominante n'est plus disponible à toutes les coupes ; les arbres sont forcés d'explorer d'autres pistes, donc de se **décorréler**. Chaque arbre individuel est un peu moins bon (il a moins de choix), mais la moyenne l'est davantage, parce que $\rho$ a baissé.

```python hide
P_rf = experience("sqrt")
v1_rf, rho_rf, mes_rf, th_rf = resume(P_rf)
NUM("rho_foret", rho_rf); NUM("var_1_arbre_foret", v1_rf); NUM("var_foret_30", mes_rf[30]); NUM("plancher_foret", rho_rf * v1_rf)
```
<!--sortie-->
```text
NUM rho_foret 0.03897873048352261
NUM var_1_arbre_foret 0.027320359488440915
NUM var_foret_30 0.001144207674333028
NUM plancher_foret 0.001064912929212888
```

Sur la même expérience, mais avec $m=\sqrt p$ variables tirées à chaque coupe, la corrélation entre deux arbres passe de 0,046 à 0,039 (plancher : de 0,0015 à 0,0011), et la variance de la moyenne de 30 arbres tombe de 0,0025 à 0,0011, soit une division par plus de deux, alors que chaque arbre pris seul a une variance comparable (0,0273 contre 0,0327). Décorréler fait gagner plus que ce que fait perdre l'appauvrissement de chaque arbre.

### 2.3.4 L'erreur « hors sac » : une validation gratuite

Chaque arbre n'a vu que 63,2 % des clients. Pour chaque client $i$, on peut donc faire voter **uniquement les arbres qui ne l'ont jamais vu**, soit environ 37 % de la forêt : on obtient une prédiction **honnête** pour ce client, comme en validation croisée, mais sans entraîner un seul modèle supplémentaire. C'est l'estimation **hors sac** (*out-of-bag*, OOB). On s'en sert pour régler les hyperparamètres d'une forêt à coût nul.

```python hide
foret = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, max_features="sqrt", oob_score=True, n_jobs=1, random_state=0).fit(Xtr_o, ytr)
p_foret = foret.predict_proba(Xte_o)[:, 1]
auc_oob = roc_auc_score(ytr, foret.oob_decision_function_[:, 1])
NUM("auc_oob", auc_oob); NUM("auc_foret_test", roc_auc_score(yte, p_foret)); NUM("logloss_foret", log_loss(yte, np.clip(p_foret, 1e-4, 1 - 1e-4)))
```
<!--sortie-->
```text
NUM auc_oob 0.8884013014935924
NUM auc_foret_test 0.8963618998322832
NUM logloss_foret 0.2606991545842332
```

```python
from sklearn.ensemble import RandomForestClassifier

foret = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, max_features="sqrt",
                               oob_score=True, n_jobs=1, random_state=0)
foret.fit(Xtr_o, ytr)
print(round(roc_auc_score(yte, foret.predict_proba(Xte_o)[:, 1]), 4))
```
<!--sortie-->
```text
0.8964
```

Une forêt de 300 arbres obtient une AUC de **0,896** sur le jeu de test, contre 0,885 pour l'arbre unique de profondeur 5 et 0,866 pour la régression logistique. L'estimation hors sac, calculée **sans utiliser le jeu de test**, donne 0,888 : elle est proche de la valeur de test, avec un léger pessimisme (chaque client n'est évalué que par environ 37 % des arbres, donc par une sous-forêt plus petite).

### 2.3.5 Combien d'arbres ? Quels réglages ?

Une particularité des forêts : **ajouter des arbres ne fait pas surapprendre**. La performance monte puis se stabilise, parce que l'erreur de la moyenne converge vers une limite quand $B\to\infty$ (c'est la loi des grands nombres appliquée aux arbres ; le terme $\rho\sigma^2$ de la formule est un plancher, pas un risque). Il suffit donc de prendre « assez » d'arbres : plus, c'est seulement plus lent.

```python hide
tailles = [1, 5, 10, 25, 50, 100, 200, 300]
indiv = np.array([t.predict_proba(Xte_o.to_numpy())[:, 1] for t in foret.estimators_])
courbe = [(k, roc_auc_score(yte, indiv[:k].mean(0))) for k in tailles]
NUM("auc_1_arbre_foret", courbe[0][1]); NUM("auc_25_arbres", dict(courbe)[25]); NUM("auc_300_arbres", courbe[-1][1])
fig, ax = plt.subplots(figsize=(6.8, 3.7))
ax.plot([k for k, _ in courbe], [a for _, a in courbe], color=BLEU, lw=2.2, marker="o", ms=4)
ax.set_xscale("log"); ax.set_xlabel("nombre d'arbres dans la forêt (échelle log)"); ax.set_ylabel("AUC sur le jeu de test"); ax.set_title("La performance se stabilise : on ne sur-apprend pas en ajoutant des arbres")
style.save(fig, "ch02-foret-nb-arbres.png")
# réglage de max_features par l'erreur hors sac
lig = []
for mf in (0.05, 0.1, 0.2, 0.4, 0.7, 1.0):
    f = RandomForestClassifier(n_estimators=120, min_samples_leaf=5, max_features=mf, oob_score=True, n_jobs=1, random_state=0).fit(Xtr_o, ytr)
    lig.append({"max_features (fraction)": mf, "AUC hors sac": roc_auc_score(ytr, f.oob_decision_function_[:, 1]), "AUC test": roc_auc_score(yte, f.predict_proba(Xte_o)[:, 1])})
mf_tab = pd.DataFrame(lig)
mf_opt = mf_tab.loc[mf_tab["AUC hors sac"].idxmax()]
NUM("mf_opt", mf_opt["max_features (fraction)"]); NUM("auc_oob_mf_opt", mf_opt["AUC hors sac"]); NUM("auc_test_mf_opt", mf_opt["AUC test"])
NUM("auc_oob_mf_1", mf_tab["AUC hors sac"].iloc[-1]); NUM("auc_oob_mf_005", mf_tab["AUC hors sac"].iloc[0])
```
<!--sortie-->
```text
NUM auc_1_arbre_foret 0.7517846962355366
NUM auc_25_arbres 0.8906815416680866
NUM auc_300_arbres 0.8963618998322832
figure : ch02-foret-nb-arbres.png
NUM mf_opt 0.7
NUM auc_oob_mf_opt 0.8854084511997171
NUM auc_test_mf_opt 0.8944802667995384
NUM auc_oob_mf_1 0.8825559115363975
NUM auc_oob_mf_005 0.8700589590996557
```

![AUC d'une forêt sur le jeu de test selon le nombre d'arbres : elle monte vite puis forme un plateau.](figures/ch02-foret-nb-arbres.png)

Avec un seul arbre de la forêt, l'AUC est de 0,752 ; avec 25 arbres, de 0,891 ; avec 300, de 0,896. Au-delà de quelques dizaines d'arbres, le gain devient marginal.

Les réglages qui comptent vraiment sont ailleurs : la **profondeur** ou la **taille minimale des feuilles** (le compromis biais-variance de chaque arbre), et surtout `max_features`, la fraction de variables examinées à chaque coupe. En voici l'effet, mesuré par l'erreur hors sac (donc sans toucher au jeu de test) :

```python hide-code
print(mf_tab.round(4).to_string(index=False))
```
<!--sortie-->
```text
 max_features (fraction)  AUC hors sac  AUC test
                    0.05        0.8701    0.8814
                    0.10        0.8821    0.8925
                    0.20        0.8848    0.8967
                    0.40        0.8852    0.8948
                    0.70        0.8854    0.8945
                    1.00        0.8826    0.8942
```

L'AUC hors sac est maximale pour une fraction de 0,70 des variables (0,885), contre 0,883 quand on les examine toutes (c'est du bagging pur) et 0,870 quand on n'en examine presque aucune. Trop peu de variables : chaque arbre est trop pauvre ; trop : les arbres se ressemblent. Le sommet est entre les deux, et il est peu marqué : les forêts sont, parmi tous les modèles, **les plus tolérantes aux mauvais réglages**.

### 2.3.6 Quelles variables comptent ? Importance et ses pièges

Une forêt ne se lit pas comme un arbre, mais on peut lui demander **quelles variables elle utilise le plus**. Deux mesures s'opposent.

- L'**importance par impureté** (*mean decrease in impurity*, MDI) additionne, pour chaque variable, les diminutions d'impureté de toutes les coupes où elle intervient. Elle est gratuite (calculée pendant l'entraînement), mais elle est **biaisée** : elle favorise les variables à **beaucoup de valeurs distinctes** (une variable continue offre beaucoup plus de seuils possibles, donc beaucoup plus d'occasions de trouver une coupe qui améliore *par hasard* l'impureté de l'entraînement) et elle est calculée **sur l'entraînement**, donc elle récompense aussi ce que la forêt a mémorisé.
- L'**importance par permutation** mélange au hasard les valeurs d'**une** variable sur des données **non vues** (le jeu de test) et mesure la **baisse de performance** : si le modèle s'effondre, la variable compte ; si rien ne change, elle ne compte pas.

Pour voir le biais, on ajoute au jeu deux variables **de pur bruit** : l'une continue (tirée dans une loi normale), l'autre un « identifiant » à 2 000 valeurs entières. Elles ne contiennent aucune information sur le départ.

```python hide
from sklearn.inspection import permutation_importance
rb = np.random.default_rng(5)
Xtr_b, Xte_b = Xtr_o.copy(), Xte_o.copy()
for nom, f in (("bruit_continu", lambda k: rb.normal(size=k)), ("bruit_identifiant", lambda k: rb.integers(0, 2000, k).astype(float))):
    Xtr_b[nom], Xte_b[nom] = f(len(Xtr_b)), f(len(Xte_b))
fb = RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_features="sqrt", n_jobs=1, random_state=0).fit(Xtr_b, ytr)
imp_mdi = pd.Series(fb.feature_importances_, index=Xtr_b.columns)
pi = permutation_importance(fb, Xte_b, yte, scoring="roc_auc", n_repeats=3, random_state=0, n_jobs=1)
imp_perm = pd.Series(pi.importances_mean, index=Xtr_b.columns)
rang_mdi = imp_mdi.rank(ascending=False); rang_perm = imp_perm.rank(ascending=False)
NUM("rang_mdi_bruit_cont", rang_mdi["bruit_continu"]); NUM("rang_mdi_bruit_id", rang_mdi["bruit_identifiant"])
NUM("mdi_bruit_id", imp_mdi["bruit_identifiant"]); NUM("perm_bruit_id", imp_perm["bruit_identifiant"]); NUM("perm_bruit_cont", imp_perm["bruit_continu"])
NUM("n_vars_bruitees", Xtr_b.shape[1])
bruit = ["bruit_continu", "bruit_identifiant"]
ordre_aff = list(imp_mdi.drop(bruit).sort_values(ascending=False).head(8).index) + bruit          # mêmes variables, même ordre, dans les deux panneaux
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.3), sharey=True)
for ax, serie, titre in ((axs[0], imp_mdi, "Importance par impureté (entraînement)"), (axs[1], imp_perm, "Importance par permutation (test)")):
    v = serie[ordre_aff][::-1]
    cols = [ORANGE if "bruit" in k else BLEU for k in v.index]
    ax.barh(range(len(v)), v.values, color=cols); ax.set_yticks(range(len(v))); ax.set_yticklabels(v.index, fontsize=8.5); ax.set_title(titre, fontsize=10.5)
axs[0].set_xlabel("part de la baisse d'impureté"); axs[1].set_xlabel("baisse d'AUC quand on mélange la variable")
style.save(fig, "ch02-foret-importances.png")
```
<!--sortie-->
```text
NUM rang_mdi_bruit_cont 11.0
NUM rang_mdi_bruit_id 12.0
NUM mdi_bruit_id 0.035808656857798875
NUM perm_bruit_id 5.8023926119902626e-05
NUM perm_bruit_cont -0.0005044090508728635
NUM n_vars_bruitees 47
figure : ch02-foret-importances.png
```

![Les huit variables les plus importantes selon l'impureté et les deux variables de pur bruit (en orange) ajoutées au tableau, avec deux mesures d'importance. L'importance par impureté (à gauche) accorde de l'importance au bruit ; l'importance par permutation sur le jeu de test (à droite) la ramène à zéro.](figures/ch02-foret-importances.png)

Parmi les 47 colonnes, l'importance par impureté classe la variable de bruit continue au rang **11** et l'identifiant aléatoire au rang **12**, c'est-à-dire parmi les premières colonnes, devant des variables qui portent une vraie information : l'identifiant, sans aucune information, reçoit une importance de 0,0358. L'importance par permutation, elle, donne −0,0005 et 0,0001 aux deux variables de bruit : **zéro, ou à peu près**, ce qui est la bonne réponse.

> ⚠️ **Deux précautions.** (1) Ne vous fiez jamais à l'importance par impureté pour comparer des variables de types différents (continues contre catégories à peu de modalités) : préférez l'importance par permutation, calculée sur des données de test. (2) Quand deux variables sont **fortement corrélées**, la forêt répartit l'importance entre elles (et la permutation en sous-estime chacune, car l'autre « compense ») : l'importance dit *ce que le modèle utilise*, pas *ce qui cause le phénomène*. La section 5.3 reprendra l'interprétation de façon plus complète (valeurs de Shapley, PDP).

> ✅ **À retenir.**
> - Le **bagging** moyenne des arbres profonds entraînés sur des échantillons bootstrap ; la variance de la moyenne vaut $\rho\sigma^2+\frac{1-\rho}B\sigma^2$ : elle baisse avec $B$ mais plafonne à $\rho\sigma^2$.
> - La **forêt aléatoire** diminue $\rho$ en ne laissant, à chaque coupe, qu'un sous-ensemble de variables : les arbres se ressemblent moins, la moyenne est meilleure.
> - L'**erreur hors sac** (63,2 % / 36,8 % des clients) est une validation gratuite. **Ajouter des arbres ne fait pas surapprendre.**
> - Les réglages qui comptent : profondeur ou taille des feuilles, `max_features`. Une forêt est robuste et exige peu de réglages.
> - L'importance par **impureté** est biaisée (variables à nombreuses valeurs) ; préférez celle **par permutation**, mesurée sur des données non vues.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 (bagging écrit à la main) et 2.5 (importances et variables de bruit), exercices 2.7 à 2.8.
