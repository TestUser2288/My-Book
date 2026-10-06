## 1.4 ➕ WOE/IV et discrétisation des variables

> 🧭 **Section optionnelle.** Elle reprend, avec plus de précision, les classes et le poids de l'évidence de la section 1.1. Vous pouvez passer à 1.5 sans la lire.

La section 1.1 a découpé les variables en classes « à la main ». Cette section répond aux trois questions que pose tout relecteur de la grille : **à quoi sert l'IV, un indicateur très utilisé, et que mesure-t-il vraiment ? Comment découpe-t-on sans arbitraire ? Quels pièges guettent le WOE ?** Le fil conducteur est un avertissement : le WOE et l'IV sont d'excellents outils de **lecture**, et de mauvais juges d'un découpage sans garde-fous.

### 1.4.1 L'information qu'une variable apporte : l'IV

Pour une variable découpée en classes $j=1,\dots,J$, avec $g_j=B_j/B$ la part des bons et $b_j=M_j/M$ celle des mauvais dans la classe $j$, la **valeur d'information** (*information value*, IV) est

$$\text{IV}=\sum_{j=1}^{J}(g_j-b_j)\,\ln\frac{g_j}{b_j}=\sum_{j=1}^J(g_j-b_j)\,\text{WOE}_j.$$

Chaque terme est **positif** : si $g_j>b_j$, le WOE est positif et la différence aussi ; si $g_j<b_j$, les deux sont négatifs. L'IV est donc une somme de termes positifs, nulle seulement si les bons et les mauvais ont la **même distribution** sur les classes. Il a une lecture précise :

> 📐 **L'IV est une divergence symétrisée.** Développons : $\text{IV}=\sum_j g_j\ln\frac{g_j}{b_j}+\sum_j b_j\ln\frac{b_j}{g_j}=\text{KL}(g\,\|\,b)+\text{KL}(b\,\|\,g)$, la somme des deux **divergences de Kullback–Leibler** entre la distribution des bons et celle des mauvais. L'IV mesure donc *à quel point on distingue* les deux populations avec cette variable, dans les deux sens. Les conventions du métier lisent un IV de la façon suivante.

| IV | Lecture usuelle |
|---|---|
| moins de 0,02 | variable sans intérêt |
| de 0,02 à 0,1 | pouvoir prédictif faible |
| de 0,1 à 0,3 | pouvoir prédictif moyen |
| de 0,3 à 0,5 | pouvoir prédictif fort |
| plus de 0,5 | **suspect** : fuite d'information probable |

Ces seuils sont des **conventions de praticiens**, pas des résultats théoriques ; la dernière ligne est la plus utile : un IV trop beau est presque toujours un défaut de construction (nous le provoquons en 1.4.3). Voici les IV de nos dix variables, calculés sur l'échantillon de développement avec les classes de la section 1.1 :

```python hide-code
iv = pd.Series({v: G.tables[v]["iv"].sum() for v in G.variables}).sort_values(ascending=False)
print(iv.round(3).to_string())
```
<!--sortie-->
```text
taux_endettement       0.403
anciennete_emploi      0.258
nb_incidents_12m       0.240
revenu_annuel          0.236
age                    0.145
montant                0.071
logement               0.054
anciennete_relation    0.051
duree_mois             0.029
objet                  0.015
```

Le taux d'endettement est de loin le plus informatif (IV 0,40, fort), devant l'ancienneté dans l'emploi, les incidents et le revenu (de 0,24 à 0,26, moyens), l'âge (0,15) ; le montant, l'ancienneté de la relation et le logement sont faibles, la durée et l'objet sont au bord de l'inutilité. Cet ordre est cohérent avec les amplitudes de points de 1.1.6. Les variables d'IV très faible ne coûtent rien à garder, mais elles alourdissent la carte : on en retire souvent sous 0,02 ou 0,03.

⚠️ L'IV est une mesure **univariée** : il ne tient pas compte de la redondance entre variables (le revenu et l'endettement se recoupent), que la régression gère ensuite.

### 1.4.2 Combien de classes ? L'IV grandit avec leur nombre

Si l'on raffine le découpage, l'IV ne peut que croître : il y a plus de façons de séparer bons et mauvais. Cette croissance n'est pas toute de l'information, c'est aussi du **bruit** que l'on apprend. Pour le voir, découpons l'âge en $k$ classes d'effectifs égaux, puis, comme contrôle, une variable de **pur bruit** (un tirage gaussien indépendant du défaut). Pour chaque découpage, nous mesurons l'IV sur l'échantillon de développement, puis la **même quantité** sur l'échantillon de test, avec les WOE appris sur le développement :

```python hide-code
def iv_k(x, y, k, x2=None, y2=None):
    q = np.unique(np.quantile(x, np.linspace(0, 1, k + 1)[1:-1])); i = np.searchsorted(q, x, side="right")
    n = np.bincount(i, minlength=len(q) + 1); m = np.bincount(i, weights=y, minlength=len(q) + 1)
    iv_dev = O.iv_partition(n, m)
    b = n - m; pb = (b + .5) / (b.sum() + .5 * len(n)); pm = (m + .5) / (m.sum() + .5 * len(n)); woe_ = np.log(pb / pm)
    j = np.searchsorted(q, x2, side="right"); n2 = np.bincount(j, minlength=len(q) + 1); m2 = np.bincount(j, weights=y2, minlength=len(q) + 1)
    b2 = n2 - m2
    return iv_dev, float(((b2 / b2.sum() - m2 / m2.sum()) * woe_).sum())
rng7 = np.random.default_rng(0)
bruit_tr, bruit_te = rng7.normal(size=len(tr)), rng7.normal(size=len(te))
lignes = []
for k in (3, 6, 12, 25, 50, 100):
    a_dev, a_te = iv_k(tr["age"].values.astype(float), y_tr, k, te["age"].values.astype(float), y_te)
    b_dev, b_te = iv_k(bruit_tr, y_tr, k, bruit_te, y_te)
    lignes.append((k, a_dev, a_te, b_dev, b_te))
tk = pd.DataFrame(lignes, columns=["classes", "âge dév.", "âge test", "bruit dév.", "bruit test"]).round(4)
print(tk.to_string(index=False))
```
<!--sortie-->
```text
 classes  âge dév.  âge test  bruit dév.  bruit test
       3    0.0603    0.0657      0.0001      0.0008
       6    0.1096    0.1268      0.0015     -0.0012
      12    0.1453    0.1594      0.0032     -0.0034
      25    0.1515    0.1617      0.0096     -0.0048
      50    0.1664    0.1712      0.0332     -0.0108
     100    0.1785    0.1725      0.0553     -0.0155
```

```python hide
for _, r in tk.iterrows(): print("NUM ivk", int(r["classes"]), r["âge dév."], r["âge test"], r["bruit dév."], r["bruit test"])
```
<!--sortie-->
```text
NUM ivk 3 0.0603 0.0657 0.0001 0.0008
NUM ivk 6 0.1096 0.1268 0.0015 -0.0012
NUM ivk 12 0.1453 0.1594 0.0032 -0.0034
NUM ivk 25 0.1515 0.1617 0.0096 -0.0048
NUM ivk 50 0.1664 0.1712 0.0332 -0.0108
NUM ivk 100 0.1785 0.1725 0.0553 -0.0155
```

L'âge gagne beaucoup entre 3 et 12 classes (0,06 à 0,15) puis plafonne : au-delà, les classes supplémentaires n'ajoutent presque rien sur le test. La variable de **bruit** montre l'autre face : son IV de développement monte à 0,055 avec 100 classes alors qu'elle ne contient **aucune information** ; sur le test, il tombe à zéro ou devient négatif (aucun signal). C'est l'effet qu'on appelle **surapprentissage du découpage**. Deux règles en découlent : on ne choisit pas le nombre de classes en maximisant l'IV de développement, et on regarde toujours l'IV **sur un échantillon de contrôle**.

### 1.4.3 Fusionner pour rendre monotone

Beaucoup de variables ont un effet que l'économie dit **monotone** : plus d'ancienneté dans la relation, moins de risque. Un découpage en classes d'effectifs égaux produit pourtant de petites inversions dues au hasard : le taux de la deuxième classe dépasse celui de la troisième sans raison. L'algorithme classique est la **fusion monotone** : on part de $k=10$ classes d'effectifs égaux et, tant que le taux de défaut n'est pas monotone, on **fusionne les deux classes voisines fautives dont la fusion fait perdre le moins d'IV**. Voici le résultat sur l'ancienneté de la relation, puis sur l'âge :

```python hide-code
def avant_apres(nom, sens):
    x = tr[nom]
    q = np.unique(np.quantile(x.dropna(), np.linspace(0, 1, 11)[1:-1])); i = np.searchsorted(q, x.dropna().values, side="right")
    n0 = np.bincount(i); m0 = np.bincount(i, weights=y_tr[x.notna().values])
    b, n, m = O.fusion_monotone(x, y_tr, 10, sens)
    return (len(n0), m0 / n0, O.iv_partition(n0, m0)), (len(n), m / n, O.iv_partition(n, m))
for nom in ("anciennete_relation", "age"):
    (k0, t0, v0), (k1, t1, v1) = avant_apres(nom, -1)
    print(f"{nom}\n  avant : {k0} classes, IV {v0:.3f}, taux (%) {np.round(100 * t0, 1)}")
    print(f"  après : {k1} classes, IV {v1:.3f}, taux (%) {np.round(100 * t1, 1)}")
```
<!--sortie-->
```text
anciennete_relation
  avant : 10 classes, IV 0.054, taux (%) [8.2 6.8 7.2 6.7 6.3 6.  5.5 5.3 4.6 3.5]
  après : 9 classes, IV 0.054, taux (%) [8.2 7.  6.7 6.3 6.  5.5 5.3 4.6 3.5]
age
  avant : 10 classes, IV 0.138, taux (%) [13.4  6.3  5.8  5.1  4.9  4.5  4.7  4.1  5.3  6.3]
  après : 5 classes, IV 0.127, taux (%) [13.4  6.3  5.8  5.1  5. ]
```

```python hide
(k0, t0, v0), (k1, t1, v1) = avant_apres("anciennete_relation", -1)
print("NUM mono_rel", k0, k1, round(v0, 3), round(v1, 3))
(k0, t0, v0), (k1, t1, v1) = avant_apres("age", -1)
print("NUM mono_age", k0, k1, round(v0, 3), round(v1, 3))
```
<!--sortie-->
```text
NUM mono_rel 10 9 0.054 0.054
NUM mono_age 10 5 0.138 0.127
```

Pour l'ancienneté de la relation, une seule fusion (dix classes deviennent neuf) suffit et l'IV ne bouge pas (0,054) : le découpage monotone est **gratuit**. Pour l'âge, au contraire, la fusion **force** la monotonie là où la vérité est en U : elle regroupe les 25–30 ans avec les suivants et fait **disparaître le sur-risque des plus de 65 ans** (la dernière classe a un taux de 5,0 %, alors que celui des plus de 65 ans est de 8,7 %). L'IV baisse peu (de 0,138 à 0,127), ce qui montre que l'IV ne suffit pas pour juger un découpage : la perte est concentrée dans une zone peu peuplée mais économiquement sensible.

> 🧪 **La monotonie est une hypothèse, pas un dogme.** On l'impose quand elle a un fondement (plus d'endettement, plus de risque ; plus de revenu, moins de risque) et on la **refuse** quand on a de bonnes raisons de voir un U (l'âge) ou un palier (le logement). Une grille dont toutes les variables sont forcément monotones est plus facile à défendre, et parfois moins juste. Dans les deux cas : décidez avant de regarder le résultat, et écrivez la raison.

Les outils qui font cette recherche automatiquement (arbres de décision de profondeur limitée, algorithmes de fusion avec test du $\chi^2$, optimisation par programmation en nombres entiers) donnent des découpages proches. Ce qui compte, c'est le garde-fou : effectifs minimaux, monotonie justifiée, contrôle sur un échantillon à part.

### 1.4.4 Trois pièges du WOE

**Les classes rares.** Si une classe ne contient aucun mauvais, $b_j=0$ et $\text{WOE}_j=\ln(g_j/0)=+\infty$. Même avec peu de mauvais, le WOE est très instable. On le **lisse** en ajoutant une demi-observation à chaque effectif (c'est le choix du code du chapitre) ou en fusionnant la classe avec sa voisine. La section 1.1.7 en a donné un exemple concret : la classe d'endettement de 50 à 60 % de l'échantillon des acceptés ne contenait que 20 prêts et recevait un WOE de +0,66.

**Les manquants informatifs.** Dans nos données, l'ancienneté dans l'emploi manque pour 7 % des prêts, et le défaut y est de 11,9 % contre 5,5 % pour les autres : le fait de ne pas fournir l'information est lui-même un signal. Le garder comme **classe à part** (« manquant », WOE −0,75) conserve ce signal ; l'**imputer** (par la médiane, 6,3 ans) le détruit :

```python hide-code
x_e = tr["anciennete_emploi"]
iv_sep = O.table_woe(x_e, tr["defaut_12m"], "anciennete_emploi")["iv"].sum()
iv_imp = O.table_woe(x_e.fillna(x_e.median()), tr["defaut_12m"], "anciennete_emploi")["iv"].sum()
print(f"IV de l'ancienneté dans l'emploi, manquant en classe à part : {iv_sep:.3f}")
print(f"IV après imputation par la médiane ({x_e.median():.1f} ans)        : {iv_imp:.3f}")
```
<!--sortie-->
```text
IV de l'ancienneté dans l'emploi, manquant en classe à part : 0.258
IV après imputation par la médiane (6.3 ans)        : 0.163
```

```python hide
print("NUM iv_sep", round(float(iv_sep), 3)); print("NUM iv_imp", round(float(iv_imp), 3)); print("NUM med_emploi", round(float(x_e.median()), 1))
print("NUM woe_manq", round(float(O.table_woe(x_e, tr["defaut_12m"], "anciennete_emploi").loc["manquant", "woe"]), 2))
```
<!--sortie-->
```text
NUM iv_sep 0.258
NUM iv_imp 0.163
NUM med_emploi 6.3
NUM woe_manq -0.75
```

L'imputation fait perdre plus du tiers de l'information de la variable (0,26 contre 0,16). Cela vaut pour la grille ; un modèle d'arbres gère aussi les manquants nativement. Ce qu'il faut éviter, c'est de **supposer que le manquant est neutre**.

**La fuite d'information.** Le dernier piège est le plus coûteux : un IV énorme. Simulons une variable « nombre de retards de paiement du prêt » qui serait connue après la souscription : elle vaut zéro ou presque pour les bons, quelques unités pour les mauvais.

```python hide-code
rng_f = np.random.default_rng(1)
fuite = pd.Series(y_tr * rng_f.poisson(3, len(tr)) + rng_f.poisson(0.1, len(tr)), index=tr.index).astype(float)
q_f = np.unique(np.quantile(fuite, np.linspace(0, 1, 11)[1:-1])); i_f = np.searchsorted(q_f, fuite.values, side="right")
n_f = np.bincount(i_f); m_f = np.bincount(i_f, weights=y_tr)
print(f"IV de la variable « retards du prêt » : {O.iv_partition(n_f, m_f):.2f}  (repère de suspicion : 0,5)")
```
<!--sortie-->
```text
IV de la variable « retards du prêt » : 4.64  (repère de suspicion : 0,5)
```

```python hide
print("NUM iv_fuite", round(float(O.iv_partition(n_f, m_f)), 2))
```
<!--sortie-->
```text
NUM iv_fuite 4.64
```

Un IV de 4,6 (plus de dix fois celui du taux d'endettement) n'est pas une aubaine, c'est **une alarme** : une variable de ce genre n'existe pas à la date de la demande. Quand un IV dépasse nettement 0,5, on ne félicite pas le modèle, on cherche **quand** la variable est connue (volume III, section 1.1).

### 1.4.5 Le WOE est une paramétrisation, pas une magie

Que perd-on à passer par les WOE plutôt que de donner à une régression les **indicateurs de classe** (une variable 0/1 par classe) ? Le WOE impose à chaque variable **un seul** coefficient $\beta_k$ multiplié à des valeurs précalculées, alors que les indicateurs laissent la régression ajuster chaque classe librement. Comparons les deux sur le test :

```python hide-code
def dums(d):
    return pd.concat([pd.get_dummies(O.classer(d[v], v), prefix=v) for v in O.VARIABLES], axis=1).astype(float)
D_tr = dums(tr); D_te = dums(te).reindex(columns=D_tr.columns, fill_value=0)
p_dum = LogisticRegression(C=1.0, max_iter=5000).fit(D_tr, y_tr).predict_proba(D_te)[:, 1]
dd_ = O.bootstrap_diff_auc(y_te, p_dum, r_grille, 300, 2)
print(f"AUC, grille par WOE            : {O.auc(y_te, r_grille):.4f}")
print(f"AUC, indicateurs de classes    : {O.auc(y_te, p_dum):.4f}")
print(f"différence (indicateurs - WOE) : {dd_[0]:+.4f}  [{dd_[1][0]:+.4f} ; {dd_[1][1]:+.4f}]")
```
<!--sortie-->
```text
AUC, grille par WOE            : 0.7712
AUC, indicateurs de classes    : 0.7778
différence (indicateurs - WOE) : +0.0065  [+0.0023 ; +0.0105]
```

```python hide
print("NUM auc_dum", round(O.auc(y_te, p_dum), 4)); print("NUM d_dum", round(dd_[0], 4), round(dd_[1][0], 4), round(dd_[1][1], 4))
```
<!--sortie-->
```text
NUM auc_dum 0.7778
NUM d_dum 0.0065 0.0023 0.0105
```

Les deux approches sont **très proches** : les indicateurs gagnent 0,007 d'AUC, un écart petit mais réel (l'intervalle apparié, de +0,002 à +0,011, exclut zéro), parce que la régression peut ajuster chaque classe librement au lieu de se plier à un seul coefficient par variable. Le WOE n'est donc pas un gain de précision ; il rend le modèle **plus lisible** : un coefficient par variable, des points qui s'additionnent, la même échelle pour toutes les variables, et un moyen de repérer d'un coup d'œil les classes aberrantes. Il porte aussi un risque que les indicateurs n'ont pas : le WOE est un **encodage par la cible** (volume III, section 4.1), calculé avec les étiquettes ; calculé sur toutes les données avant un découpage de validation, il fuit.

> ✅ **À retenir.**
> - $\text{WOE}_j=\ln\frac{g_j}{b_j}$ ; $\text{IV}=\sum_j(g_j-b_j)\text{WOE}_j=\text{KL}(g\|b)+\text{KL}(b\|g)$ : un indicateur univarié du pouvoir de séparation, lu avec des seuils **conventionnels**, et **suspect au-dessus de 0,5**.
> - L'IV de développement **grandit avec le nombre de classes**, même pour du bruit : on le contrôle sur un échantillon à part et on garde peu de classes lisibles.
> - La **fusion monotone** est gratuite quand l'économie impose la monotonie ; elle **abîme** quand la vérité est en U.
> - Les **manquants** forment souvent une classe informative ; les **classes rares** se lissent ou se fusionnent ; un **IV énorme** est une alarme de fuite.
> - Le WOE est une **paramétrisation commode**, pas une source de performance : les indicateurs de classes font légèrement mieux (+0,007 d'AUC).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercices 1.9 et 1.10.
