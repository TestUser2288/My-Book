## 1.2 Modèles de prédiction du défaut

La grille de la section 1.1 est un modèle **volontairement contraint** : des classes, des effets additifs, des points. Les données d'aujourd'hui permettent des modèles bien plus souples, comme les arbres de gradient (volume III, section 2.4). Cette section pose la question qu'un comité de risque pose toujours : **que gagne-t-on à abandonner la grille, et que perd-on ?** Nous comparons trois candidats **fixés d'avance** sur le même échantillon de test, nous regardons **pourquoi** l'un l'emporte sur l'autre en nous appuyant sur la vérité programmée, puis nous traitons deux sujets propres au crédit : la **calibration** et les **motifs de refus**.

### 1.2.1 Trois candidats

- **La régression logistique « brute »** : les variables sont prises telles quelles (âge, taux d'endettement… en nombres), avec des indicateurs pour les manquants et des modalités pour les catégories. C'est la première chose qu'un statisticien essaie (volume II, section 2.2).
- **La grille de score** de la section 1.1 : classes, WOE, régression, points.
- **Un modèle de boosting** (LightGBM) : un ensemble d'arbres qui apprend lui-même les seuils et les interactions. On en examine deux versions, libre et **monotone** (nous y revenons en 1.2.3).

Les trois sont entraînés sur les mêmes 28 000 prêts et mesurés sur les mêmes 12 000 prêts de test. Aucun réglage n'a été fait en regardant le test ; les paramètres du boosting sont ceux d'un réglage modeste (300 petits arbres de huit feuilles, pas d'apprentissage de 0,03, au moins 200 prêts par feuille), choisis pour éviter le surapprentissage, non pour gagner un dixième de point.

```python hide
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb

def brut(d):
    X = d[["age", "revenu_annuel", "anciennete_emploi", "montant", "duree_mois", "taux_endettement",
           "nb_incidents_12m", "anciennete_relation"]].copy()
    for k in ["revenu_annuel", "anciennete_emploi"]:
        X[k + "_manq"] = X[k].isna().astype(int)
    return pd.concat([X, pd.get_dummies(d[["logement", "objet"]]).astype(int)], axis=1)

Xb_tr, Xb_te = brut(tr), brut(te)
med = Xb_tr.median(); mu_b = Xb_tr.fillna(med).mean(); sd_b = Xb_tr.fillna(med).std()
lr_brut = LogisticRegression(max_iter=3000).fit((Xb_tr.fillna(med) - mu_b) / sd_b, y_tr)
p_brut = lr_brut.predict_proba((Xb_te.fillna(med) - mu_b) / sd_b)[:, 1]
```

La version du boosting contrainte demande que le risque **ne puisse que croître** avec le taux d'endettement et le nombre d'incidents, et **que décroître** avec le revenu, l'ancienneté dans l'emploi et l'ancienneté de la relation, pour que la forme du modèle reste défendable devant un auditeur :

```python
contraintes = {"taux_endettement": 1, "nb_incidents_12m": 1, "revenu_annuel": -1,
               "anciennete_emploi": -1, "anciennete_relation": -1}       # +1 : le risque ne peut que croître
mc = [contraintes.get(c, 0) for c in Xb_tr.columns]
gbm = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.8, monotone_constraints=mc, random_state=0, verbose=-1)
gbm.fit(Xb_tr, y_tr)
```

```python hide
p_gbm = gbm.predict_proba(Xb_te)[:, 1]
gbm_libre = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8,
                               subsample_freq=1, colsample_bytree=0.8, random_state=0, verbose=-1).fit(Xb_tr, y_tr)
p_libre = gbm_libre.predict_proba(Xb_te)[:, 1]
r_grille = -s_te                                     # pour comparer : un nombre élevé = un risque élevé
# vérité : la régression logistique à laquelle on donnerait les VRAIES formes (âge au carré, coude de l'endettement)
def vraies_formes(X):
    X = X.copy(); X["age_c2"] = (X["age"] - 47) ** 2; X["dti_coude"] = np.maximum(0, X["taux_endettement"] - 0.5); X["lrev"] = np.log(X["revenu_annuel"])
    return X
A_tr, A_te = vraies_formes(Xb_tr.fillna(med)), vraies_formes(Xb_te.fillna(med)); mu_a, sd_a = A_tr.mean(), A_tr.std()
lr_vrai = LogisticRegression(max_iter=3000).fit((A_tr - mu_a) / sd_a, y_tr)
p_vrai = lr_vrai.predict_proba((A_te - mu_a) / sd_a)[:, 1]
modeles = {"logistique brute": p_brut, "grille de score": r_grille, "boosting libre": p_libre, "boosting monotone": p_gbm, "logistique, vraies formes": p_vrai}
res = pd.DataFrame({k: [O.auc(y_te, v), O.gini(y_te, v), O.ks(y_te, v)] + list(O.bootstrap_auc(y_te, v, 200)) for k, v in modeles.items()},
                   index=["AUC", "Gini", "KS", "AUC bas", "AUC haut"]).T
d_gl = O.bootstrap_diff_auc(y_te, r_grille, p_brut, 300, 1)
d_gb = O.bootstrap_diff_auc(y_te, r_grille, p_gbm, 300, 1)
```

### 1.2.2 Le verdict mesuré

Les mesures sont celles de la section 1.3 (AUC, Gini = 2·AUC − 1, KS) ; ici, lisons-les en gros.

```python hide-code
print(res[["AUC", "Gini", "KS"]].round(3).to_string())
print("intervalle de l'AUC (rééchantillonnage, 95 %) :")
for k in ["logistique brute", "grille de score", "boosting monotone"]:
    print(f"  {k:20s} [{res.loc[k, 'AUC bas']:.3f} ; {res.loc[k, 'AUC haut']:.3f}]")
print(f"AUC grille - AUC logistique brute : {d_gl[0]:+.4f}  [{d_gl[1][0]:+.4f} ; {d_gl[1][1]:+.4f}]")
print(f"AUC grille - AUC boosting monotone : {d_gb[0]:+.4f}  [{d_gb[1][0]:+.4f} ; {d_gb[1][1]:+.4f}]")
```
<!--sortie-->
```text
                             AUC   Gini     KS
logistique brute           0.762  0.524  0.396
grille de score            0.771  0.542  0.406
boosting libre             0.772  0.545  0.407
boosting monotone          0.774  0.547  0.409
logistique, vraies formes  0.777  0.555  0.420
intervalle de l'AUC (rééchantillonnage, 95 %) :
  logistique brute     [0.741 ; 0.779]
  grille de score      [0.751 ; 0.789]
  boosting monotone    [0.753 ; 0.790]
AUC grille - AUC logistique brute : +0.0097  [+0.0009 ; +0.0182]
AUC grille - AUC boosting monotone : -0.0022  [-0.0089 ; +0.0040]
```

```python hide
print("NUM auc_brute", round(res.loc["logistique brute", "AUC"], 4)); print("NUM auc_grille", round(res.loc["grille de score", "AUC"], 4))
print("NUM auc_libre", round(res.loc["boosting libre", "AUC"], 4)); print("NUM auc_mono", round(res.loc["boosting monotone", "AUC"], 4))
print("NUM auc_vrai", round(res.loc["logistique, vraies formes", "AUC"], 4))
```
<!--sortie-->
```text
NUM auc_brute 0.7618
NUM auc_grille 0.7712
NUM auc_libre 0.7725
NUM auc_mono 0.7737
NUM auc_vrai 0.7773
```

Le tableau raconte une histoire nette :

- La **grille** (AUC 0,771) fait **mieux que la logistique brute** (0,762). L'écart est petit (un point d'AUC), mais l'intervalle de la différence **apparié** (mêmes dossiers dans les deux calculs, volume III, section 1.4) est entièrement positif : il n'est pas dû au hasard de l'échantillon de test.
- Le **boosting** (0,774 pour la version monotone, 0,772 pour la version libre) **ne fait pas mieux que la grille** : la différence de 0,002 est dans le bruit (l'intervalle apparié contient zéro). Imposer la monotonie ne coûte rien ici, elle améliore même un tout petit peu.
- La logistique à laquelle on donne les **vraies formes** (nous allons voir lesquelles) atteint 0,777 : c'est le **plafond atteignable** avec ces variables et cet échantillon, la mesure de ce que valent les meilleurs modèles possibles. La grille en est à 0,6 point.

> 🧪 **Un résultat qui n'est pas un slogan.** On lit souvent que « les modèles d'arbres battent la régression logistique ». Sur ce jeu, **ce n'est pas le cas** : les variables sont peu nombreuses, la vérité est une somme d'effets (des formes simples sans interaction), et 28 000 lignes ne laissent pas de quoi apprendre des interactions fines. Sur d'autres données (le jeu réel de la section 1.3, où l'effet du statut de paiement est très non linéaire), le boosting gagne nettement. **La bonne démarche est de mesurer**, et non de supposer.

### 1.2.3 Pourquoi la grille bat la logistique brute : les formes

Pourquoi les classes aident-elles ? Parce que la vérité n'est **pas linéaire**. Les données ont été simulées avec un risque dont l'effet sur la log-cote est :

- **en U pour l'âge** : $0{,}0012\,(\text{âge}-47)^2$ (multiplié par 1,3 comme tous les effets du jeu), ce qui donne un risque plus élevé chez les jeunes que chez les plus de 65 ans, et minimal vers 47 ans ;
- **en coude pour le taux d'endettement** : 1,5 par point d'endettement, puis 3 de plus par point **au-delà de 50 %**.

Une régression logistique brute ne peut pas représenter un U avec **un seul coefficient** : elle ajuste la meilleure droite, qui **décroît** lentement avec l'âge : elle dit que les plus âgés sont les plus sûrs, alors qu'ils sont plus risqués que les 40–55 ans. La grille, qui donne à chaque classe son propre niveau, suit la courbe :

```python hide
a_grid = np.arange(20, 76)
def centre(v, ref):
    return v - np.average(ref)
# effets sur la log-cote de MAUVAIS (centrés sur la population de développement)
age_vrai = 1.3 * 0.0012 * (a_grid - 47) ** 2
cl_age = O.classer(pd.Series(a_grid), "age").map(G.tables["age"]["woe"]).values
age_grille = -G.beta["age"] * cl_age
c_age = lr_brut.coef_[0][list(Xb_tr.columns).index("age")] / sd_b["age"]
age_lin = c_age * a_grid
ref_age = np.arange(20, 76)
poids_age = tr["age"].value_counts().reindex(a_grid).fillna(0).values
d_grid = np.arange(0.0, 1.0, 0.01)
dti_vrai = 1.3 * (1.5 * d_grid + 3 * np.maximum(0, d_grid - 0.5))
dti_grille = -G.beta["taux_endettement"] * O.classer(pd.Series(d_grid), "taux_endettement").map(G.tables["taux_endettement"]["woe"]).values
c_dti = lr_brut.coef_[0][list(Xb_tr.columns).index("taux_endettement")] / sd_b["taux_endettement"]
dti_lin = c_dti * d_grid
poids_dti = np.histogram(tr["taux_endettement"].clip(0, 0.99), bins=np.r_[d_grid, 1.0])[0]
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.4))
for ax, g, vrai, grille, lin, w, titre in [(axs[0], a_grid, age_vrai, age_grille, age_lin, poids_age, "Âge (années)"),
                                           (axs[1], d_grid, dti_vrai, dti_grille, dti_lin, poids_dti, "Taux d'endettement")]:
    mu0 = lambda v: v - np.average(v, weights=w)
    ax.plot(g, mu0(vrai), color=ENCRE, lw=2, label="vérité programmée")
    ax.step(g, mu0(grille), color=BLEU, lw=1.8, where="post", label="grille (classes)")
    ax.plot(g, mu0(lin), color=ORANGE, lw=1.8, ls="--", label="logistique brute (droite)")
    ax.set_xlabel(titre); ax.set_ylabel("effet sur la log-cote de défaut"); ax.legend(frameon=False, fontsize=8.5)
fig.tight_layout(); fig.savefig("figures/ch01-formes.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM c_age", round(float(c_age), 4)); print("NUM c_dti", round(float(c_dti), 3))
```
<!--sortie-->
```text
NUM c_age -0.0142
NUM c_dti 3.621
```

![Effet de l'âge et du taux d'endettement sur la log-cote de défaut, centré sur la population : la vérité programmée (noir), la grille qui suit sa forme (bleu), la droite de la logistique brute (orange pointillé) qui rate le U et le coude.](figures/ch01-formes.png)

La droite orange est la meilleure approximation linéaire, et elle **se trompe aux endroits qui comptent** : elle sous-estime le risque des très jeunes, des plus âgés et des très endettés, qui sont justement ceux que l'on veut repérer. La grille suit le U de l'âge et le coude de l'endettement par paliers. Le boosting, lui, les découvre seul grâce aux seuils de ses arbres.

⚠️ **Ne retenez pas « la grille bat la logistique », mais « les formes comptent ».** Une logistique à laquelle on ajoute un terme quadratique en âge et un coude en endettement (la ligne « vraies formes » du tableau) fait aussi bien que la grille, sans classes. L'avantage de la grille est ailleurs : **elle trouve les formes sans que l'on ait à les deviner**, traite proprement les manquants et reste lisible.

### 1.2.4 Le boosting monotone

Un arbre de gradient libre peut produire des effets **non monotones** là où l'économie n'en admet pas : par exemple un risque qui *baisse* quand l'endettement passe de 55 % à 60 %, simple accident d'un échantillon creux. Pour un modèle de crédit, c'est un problème de **gouvernance** : on ne sait pas l'expliquer, et un client pourrait améliorer son score en détériorant son dossier. Les contraintes de monotonie imposent à chaque arbre de ne jamais inverser le sens d'une variable : la fonction de score est alors **monotone** dans chaque variable contrainte.

Le code de 1.2.1 en montre la mise en œuvre : une liste de signes, un par colonne. Son coût en performance est ici nul. Dans d'autres situations, il peut être de quelques millièmes d'AUC ; **c'est le prix d'un modèle défendable**. Pour comprendre les contributions d'un modèle de ce type, les méthodes du volume III (section 5.3, importance par permutation, SHAP) s'appliquent sans changement ; en crédit, on leur préfère souvent des **motifs de refus** adossés à la grille (1.2.6) ou à des contributions par variable.

### 1.2.5 Calibrer : une probabilité n'est pas un rang

Un score qui classe bien peut annoncer des probabilités fausses. Or le crédit **utilise les probabilités** : pour fixer un prix, pour calculer la perte attendue, pour le capital réglementaire. La **calibration** (volume III, section 5.2) vérifie qu'un groupe de dossiers annoncés à 3 % fait bien environ 3 % de défauts. Regroupons les dossiers du test en dix groupes de taille égale, selon la probabilité annoncée par la grille :

```python hide-code
pp = G.pd_predite(te)
dec = pd.DataFrame({"pd_annoncee": pp, "defaut": y_te, "groupe": pd.qcut(pp, 10, labels=False) + 1})
cal = dec.groupby("groupe").agg(n=("defaut", "size"), annoncee=("pd_annoncee", "mean"), observee=("defaut", "mean")).round(4)
print(cal.to_string())
```
<!--sortie-->
```text
           n  annoncee  observee
groupe                          
1       1200    0.0094    0.0108
2       1200    0.0151    0.0167
3       1201    0.0200    0.0216
4       1199    0.0253    0.0192
5       1200    0.0314    0.0242
6       1200    0.0395    0.0500
7       1200    0.0501    0.0500
8       1200    0.0670    0.0633
9       1200    0.0995    0.1117
10      1200    0.2356    0.2292
```

```python hide
print("NUM pd_moy_te", round(float(pp.mean()), 4)); print("NUM pd_dec1_ann", float(cal.loc[1, "annoncee"])); print("NUM pd_dec1_obs", float(cal.loc[1, "observee"]))
print("NUM pd_dec10_ann", float(cal.loc[10, "annoncee"])); print("NUM pd_dec10_obs", float(cal.loc[10, "observee"]))
```
<!--sortie-->
```text
NUM pd_moy_te 0.0593
NUM pd_dec1_ann 0.0094
NUM pd_dec1_obs 0.0108
NUM pd_dec10_ann 0.2356
NUM pd_dec10_obs 0.2292
```

La grille est **bien calibrée** : la probabilité moyenne annoncée (5,9 %) est celle du défaut observé (6,0 %) et, groupe par groupe, les écarts restent dans une marge de deux écarts-types (le dixième groupe annonce 23,6 % et observe 22,9 %). Ce n'est pas un hasard : une régression logistique **calibre en moyenne par construction** sur son échantillon de développement. Cette propriété se perd quand la population change (section 1.3) ; un boosting, lui, n'est pas calibré par construction et demande souvent une recalibration (régression logistique ou isotonique sur la sortie, volume III, section 5.2).

### 1.2.6 Expliquer un refus : les motifs

Dans beaucoup de juridictions, un client refusé est en droit de connaître **les principales raisons** de la décision, et le prêteur doit pouvoir les produire (nous reviendrons sur la réglementation au chapitre 4 ; le droit exact dépend du pays et de l'époque, à vérifier). La grille y répond naturellement : les **motifs de refus** (*reason codes*) sont les variables pour lesquelles le dossier **perd le plus de points** par rapport au meilleur cas possible de chaque variable.

```python
def motifs(i, k=3):
    """Les k variables où le dossier te.iloc[i] perd le plus de points, par rapport à la meilleure classe de la variable."""
    perte = {}
    for v in O.VARIABLES:
        classes = pts[pts.variable == v]
        c = O.classer(te.iloc[[i]][v], v).iloc[0]
        perte[v] = classes.points.max() - float(classes[classes.classe == c].points.iloc[0])
    return pd.Series(perte).sort_values(ascending=False).head(k).round(1)

print(motifs(trois["risqué"]))
```
<!--sortie-->
```text
age                    30.1
anciennete_relation    23.4
anciennete_emploi      22.8
dtype: float64
```

```python hide
m_ = motifs(trois["risqué"]); print("NUM motif1", m_.index[0], m_.iloc[0]); print("NUM motif2", m_.index[1], m_.iloc[1]); print("NUM motif3", m_.index[2], m_.iloc[2])
```
<!--sortie-->
```text
NUM motif1 age 30.1
NUM motif2 anciennete_relation 23.4
NUM motif3 anciennete_emploi 22.8
```

Pour ce dossier très risqué, les trois motifs sont l'âge (30 points perdus par rapport à la meilleure tranche d'âge), l'ancienneté de la relation (23 points) et l'ancienneté dans l'emploi (23 points). Remarquez qu'**un motif n'est pas un conseil** : un client de 24 ans ne peut pas « corriger » son âge. La réglementation de certains pays interdit d'ailleurs que certaines variables (le sexe, par exemple) servent à décider ; l'âge lui-même est parfois encadré. La question de savoir **quelles variables on a le droit d'utiliser**, et ce qu'on fait de celles qui servent de substitut à des variables interdites, relève du volume III (section 5.4, équité) et du cadre légal local.

### 1.2.7 Choisir

Le comité de risque ne choisit pas sur l'AUC seule. Les critères qui comptent, dans l'ordre où on les rencontre en pratique :

| Critère | Grille | Boosting monotone | Boosting libre |
|---|---|---|---|
| Pouvoir de classement (mesuré ici) | 0,771 | 0,774 | 0,772 |
| Explicabilité d'un refus | directe (points) | par contributions | par contributions |
| Monotonie garantie | oui, si les classes le sont | oui (contraintes) | non |
| Stabilité face à une population qui change | bonne (classes larges) | moyenne | plus fragile |
| Surveillance et validation | outils standard (PSI, tables) | outils standard + explicabilité | plus lourde |
| Traitement des manquants | classe à part, lisible | natif | natif |

Dans la pratique, beaucoup de banques conservent une **grille comme modèle de référence** et la mettent en concurrence avec un modèle plus souple, le **challenger** : si l'écart de performance est faible, comme ici, on garde la grille ; s'il est large et stable, on adopte le challenger **avec ses garde-fous**. C'est la logique de la **rigueur d'évaluation** du volume III : on ne s'incline pas devant la sophistication sans l'avoir mesurée, avec son incertitude.

> ✅ **À retenir.**
> - Sur nos données, trois candidats classent presque aussi bien : la **forme des effets** compte plus que l'algorithme. La grille gagne sur la logistique brute (+0,010 d'AUC, intervalle apparié positif) parce que la vérité n'est pas linéaire ; elle ne perd rien face au boosting (écart de 0,002 dans le bruit).
> - Le **plafond** (la logistique aux vraies formes) vaut 0,777 : il situe les candidats sur l'échelle de ce qui est atteignable.
> - Un modèle de crédit doit être **monotone** quand l'économie l'exige : les contraintes de monotonie ne coûtent ici rien.
> - Un score doit être **calibré** : la grille l'est par construction sur son échantillon, pas forcément ailleurs.
> - Les **motifs de refus** se lisent dans les points perdus ; ils expliquent, ils ne prescrivent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3, exercices 1.4 et 1.5.
