## 4.1 Encodage, mise à l'échelle, transformations

Un modèle ne manipule que des **nombres**. Or une table de clients contient des villes, des canaux, des valeurs manquantes, des montants qui vont de 5 € à 3 000 €, des âges, des indicateurs 0/1. Passer de la table au tableau de nombres que le modèle consommera s'appelle le **prétraitement** (*preprocessing*). Cette section en détaille les quatre grandes opérations : encoder les catégories, mettre les variables à une échelle comparable, corriger les distributions asymétriques, et traiter les valeurs manquantes. La dernière sous-section montre comment tout assembler **sans fuite**.

### 4.1.1 Deux familles de modèles, deux besoins

Avant d'apprendre à transformer, demandons-nous **quand c'est nécessaire**. Les modèles se répartissent en deux familles très différentes face au prétraitement.

- Les modèles **à base de distances ou de pénalités** (k plus proches voisins, SVM, régression logistique régularisée, réseaux de neurones) comparent des variables entre elles par des sommes de carrés. Si une variable s'exprime en euros (de 0 à 3 000) et une autre en nombre de tickets (de 0 à 8), la première écrase l'autre : l'**échelle** décide, sans qu'on l'ait voulu.
- Les modèles **à base d'arbres** (arbres, forêts, boosting) ne font que **comparer une variable à un seuil**. Multiplier une variable par 1 000, ou lui appliquer une transformation croissante comme le logarithme, ne change aucune comparaison « inférieur à ? » : les partitions possibles sont les mêmes. Ils sont donc **insensibles à l'échelle et aux transformations monotones**. En revanche, ils ne « voient » pas facilement qu'un ratio de deux variables compte, et la plupart des implémentations ne lisent pas une catégorie de texte (certaines, comme `HistGradientBoosting`, LightGBM ou CatBoost, acceptent des variables déclarées comme qualitatives).

Cette observation guide tout le reste : on choisit le prétraitement **en fonction du modèle**, et non pas une fois pour toutes.

### 4.1.2 Encoder une variable qualitative

Une **variable qualitative** (la ville, le canal d'acquisition, la catégorie de produit préférée) doit être traduite en nombres. Quatre méthodes couvrent presque tous les cas, auxquelles s'ajoute une cinquième pour les très grands nombres de modalités.

**L'encodage disjonctif (*one-hot*).** On crée une colonne 0/1 par modalité : pour le canal, `canal_Boutique`, `canal_Site`, `canal_Réseaux`. Un client de la boutique vaut $(1,0,0)$. C'est la méthode par défaut pour les modèles linéaires : chaque modalité reçoit son propre coefficient, sans ordre imposé. Ses défauts apparaissent quand il y a beaucoup de modalités : 20 villes donnent 20 colonnes, 2 000 codes postaux en donneraient 2 000, presque toutes vides, et les arbres perdent en efficacité à fragmenter l'information.

**L'encodage ordinal.** On remplace chaque modalité par un entier (1, 2, 3…). Il n'est correct que si les modalités ont un **ordre naturel** (« jamais / parfois / souvent »). Appliqué à des villes, il invente un ordre qui n'existe pas : un modèle linéaire croirait que la ville 3 est « entre » les villes 2 et 4.

**L'encodage par fréquence.** On remplace chaque modalité par sa **fréquence** dans le jeu d'entraînement (la part des clients qui y habitent). Une seule colonne, aucune fuite de la cible, mais l'information « grande ou petite ville » est mélangée à toute autre.

**L'encodage par la cible (*target encoding*).** On remplace chaque modalité par la **moyenne de la cible** observée dans cette modalité : pour la ville, le taux de départ des clients qui y habitent. C'est puissant (une seule colonne, qui contient directement l'information utile), mais c'est aussi **la source de fuite d'information la plus classique** du prétraitement. Voyons pourquoi.

**L'encodage par hachage (*hashing trick*).** Quand une variable a des milliers, voire des millions de modalités (des identifiants de produits, des mots), on applique une **fonction de hachage** au nom de la modalité, on prend le résultat modulo $m$, et on place la modalité dans l'une des $m$ colonnes d'un *one-hot* de largeur fixe (par exemple $m=256$). Il n'y a pas de dictionnaire à garder et de nouvelles modalités sont acceptées sans erreur. Le prix : des **collisions**, c'est-à-dire des modalités différentes qui partagent une colonne, et des colonnes qu'on ne sait plus interpréter. C'est ce que fait `FeatureHasher` dans scikit-learn.

#### Un exemple minuscule

Huit clients, trois villes, et la cible « le client est parti » :

| client | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **ville** | A | A | A | B | B | B | C | A |
| **parti** | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 |

La moyenne de la cible par ville vaut : pour A (clients 1, 2, 3, 8), $\frac{1+0+0+0}{4}=0{,}25$ ; pour B (clients 4, 5, 6), $\frac{1+1+0}{3}\approx0{,}67$ ; pour C (client 7 seul), $\frac11=1$. La moyenne générale vaut $\frac48=0{,}5$.

Regardons le client 7. Il est **seul** dans sa ville, et son encodage vaut **1, c'est-à-dire exactement sa propre étiquette**. Le modèle apprend « les clients de la ville C partent toujours », alors qu'il s'est simplement relu lui-même. C'est la **fuite par la cible** : l'encodage d'une ligne a été calculé **en utilisant la cible de cette même ligne**. Plus une modalité est rare, plus l'encodage de ses lignes ressemble à leur étiquette, et plus l'effet est trompeur.

#### Deux remèdes

**Le lissage.** On « tire » la moyenne d'une modalité vers la moyenne générale $\mu$, d'autant plus fort que la modalité est petite :

$$\text{encodage}(m)=\frac{n_m\,\bar y_m+k\,\mu}{n_m+k},$$

où $n_m$ est l'effectif de la modalité, $\bar y_m$ sa moyenne et $k$ un paramètre de lissage (un « nombre d'observations virtuelles » à la moyenne $\mu$). Avec $k=2$, la ville C passe de $1$ à $\frac{1+2\times0{,}5}{1+2}\approx0{,}67$ : on ne fait plus confiance à un client isolé. Cette formule est une **moyenne pondérée** entre l'estimation locale et l'estimation globale, la même idée que le rétrécissement des modèles mixtes du volume II (section 1.7).

**Le calcul hors pli (*out-of-fold*).** On découpe le jeu d'entraînement en $K$ plis. L'encodage des lignes du pli $j$ est calculé **uniquement avec les lignes des autres plis**. Ainsi aucune ligne n'est jamais encodée avec sa propre étiquette. Les valeurs obtenues sont bruitées, et c'est tant mieux : ce bruit est celui que le modèle rencontrera réellement sur des données nouvelles. Pour encoder le jeu de test, on utilise les moyennes calculées sur **tout** le jeu d'entraînement.

> ⚠️ **Le piège du « leave-one-out ».** Une variante populaire retire seulement la ligne courante du calcul de la moyenne de sa modalité. Elle paraît raisonnable, mais elle fuit **à l'envers** : dans une même ville, toutes les lignes dont la cible vaut 1 reçoivent une valeur *plus basse* que celles dont la cible vaut 0. Un arbre sépare alors parfaitement les deux groupes en lisant l'encodage. Préférez le calcul par plis.

#### Ce que cela change, en vrai

Pour mesurer l'effet de la fuite, il faut une variable **à forte cardinalité** : beaucoup de modalités, peu de lignes par modalité. Nos 20 villes comptent entre 141 et 1 788 clients, ce qui est trop peu « fin » pour que la fuite se voie. Nous ajoutons donc une variable fictive, un **code postal à 400 modalités tiré au hasard**, qui n'a *par construction* aucun lien avec le départ (22 clients en moyenne par code dans le jeu d'entraînement).

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import TargetEncoder

rng = np.random.default_rng(4)
code_postal = pd.Series(rng.integers(0, 400, len(clients)), index=clients.index)      # aucun lien avec la cible


def encodage_naif(col_tr, y_tr, col_te):
    moy = y_tr.groupby(col_tr).mean()
    return col_tr.map(moy), col_te.map(moy).fillna(y_tr.mean())


def encodage_hors_pli(col_tr, y_tr, plis=5, graine=0):
    sortie = pd.Series(index=col_tr.index, dtype=float)
    for i, j in KFold(plis, shuffle=True, random_state=graine).split(col_tr):
        moy = y_tr.iloc[i].groupby(col_tr.iloc[i]).mean()
        sortie.iloc[j] = col_tr.iloc[j].map(moy).fillna(y_tr.iloc[i].mean()).values
    return sortie


a_tr, a_te = encodage_naif(code_postal[tr], ytr, code_postal[te])
o_tr = encodage_hors_pli(code_postal[tr], ytr)
bruit = pd.DataFrame({
    "encodage": ["moyenne par code, calculée sur tout l'entraînement", "moyenne par code, calculée hors pli"],
    "AUC entraînement": [roc_auc_score(ytr, a_tr), roc_auc_score(ytr, o_tr)],
    "AUC test": [roc_auc_score(yte, a_te), np.nan],
}).round(3)
print("effectif moyen par code (entraînement) :", round(len(tr) / 400, 1))
print(bruit.to_string(index=False))
```
<!--sortie-->
```text
effectif moyen par code (entraînement) : 22.5
                                          encodage  AUC entraînement  AUC test
moyenne par code, calculée sur tout l'entraînement             0.678      0.51
               moyenne par code, calculée hors pli             0.509       NaN
```

```python hide-code
print(bruit.to_string(index=False, na_rep="(non applicable)"))
```
<!--sortie-->
```text
                                          encodage  AUC entraînement         AUC test
moyenne par code, calculée sur tout l'entraînement             0.678             0.51
               moyenne par code, calculée hors pli             0.509 (non applicable)
```

Le résultat est sans ambiguïté. Avec l'encodage naïf, la variable semble prédire le départ sur le jeu d'entraînement (AUC 0,678) alors qu'elle est **du pur bruit** : sur le jeu de test, l'AUC tombe à 0,510, c'est-à-dire au niveau du hasard. Le calcul hors pli, lui, donne honnêtement 0,509 dès l'entraînement : il ne se laisse pas tromper. Un modèle qui apprendrait sur la version naïve accorderait de l'importance à une variable qui n'en a pas.

Et pour les **vraies** villes de la boutique ? Le tableau suivant compare quatre encodages sur le jeu de test. Chaque nombre est une AUC, pour une régression logistique et pour un boosting.

```python hide
from sklearn.preprocessing import OneHotEncoder

base = clients[NUM].copy()
res = []
modes = {}
modes["sans la ville"] = (base.loc[tr], base.loc[te])
oh = pd.get_dummies(clients["ville"], dtype=float)
modes["disjonctif (one-hot)"] = (pd.concat([base, oh], axis=1).loc[tr], pd.concat([base, oh], axis=1).loc[te])
freq = clients["ville"].map(clients.loc[tr, "ville"].value_counts(normalize=True))
modes["fréquence"] = (base.assign(ville_freq=freq).loc[tr], base.assign(ville_freq=freq).loc[te])
oof = encodage_hors_pli(clients.loc[tr, "ville"], ytr)
_, ville_te_test = encodage_naif(clients.loc[tr, "ville"], ytr, clients.loc[te, "ville"])
modes["cible, hors pli"] = (base.loc[tr].assign(ville_cible=oof), base.loc[te].assign(ville_cible=ville_te_test))
te_sk = TargetEncoder(smooth="auto", cv=5, random_state=0).fit(clients.loc[tr, ["ville"]], ytr)
modes["cible (TargetEncoder, lissé)"] = (base.loc[tr].assign(ville_cible=te_sk.transform(clients.loc[tr, ["ville"]]).ravel()),
                                         base.loc[te].assign(ville_cible=te_sk.transform(clients.loc[te, ["ville"]]).ravel()))


def auc_deux_modeles(Xa, Xb):
    lg = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xa, ytr)
    gb = HistGradientBoostingClassifier(random_state=0, max_iter=100).fit(Xa, ytr)
    return roc_auc_score(yte, lg.predict_proba(Xb)[:, 1]), roc_auc_score(yte, gb.predict_proba(Xb)[:, 1])


lignes = []
for nom, (Xa, Xb) in modes.items():
    a, b = auc_deux_modeles(Xa, Xb)
    lignes.append({"encodage de la ville": nom, "AUC logistique": a, "AUC boosting": b})
tab_villes = pd.DataFrame(lignes).round(3)
print(tab_villes.to_string(index=False))

# incertitude d'une AUC mesurée sur ce jeu de test (formule de Hanley et McNeil)
n1, n0 = int(yte.sum()), int((1 - yte).sum())
A = 0.87
Q1, Q2 = A / (2 - A), 2 * A * A / (1 + A)
se_auc = np.sqrt((A * (1 - A) + (n1 - 1) * (Q1 - A * A) + (n0 - 1) * (Q2 - A * A)) / (n1 * n0))
print("jeu de test :", n1, "départs et", n0, "autres ; erreur-type approchée d'une AUC de 0,87 :", round(se_auc, 4))
```
<!--sortie-->
```text
        encodage de la ville  AUC logistique  AUC boosting
               sans la ville           0.858         0.892
        disjonctif (one-hot)           0.863         0.895
                   fréquence           0.859         0.897
             cible, hors pli           0.864         0.896
cible (TargetEncoder, lissé)           0.864         0.900
jeu de test : 421 départs et 2579 autres ; erreur-type approchée d'une AUC de 0,87 : 0.0114
```

```python hide-code
print(tab_villes.to_string(index=False))
```
<!--sortie-->
```text
        encodage de la ville  AUC logistique  AUC boosting
               sans la ville           0.858         0.892
        disjonctif (one-hot)           0.863         0.895
                   fréquence           0.859         0.897
             cible, hors pli           0.864         0.896
cible (TargetEncoder, lissé)           0.864         0.900
```

Les cinq lignes se ressemblent : ajouter l'information de la ville améliore l'AUC de quelques millièmes (de 0,858 à 0,864 pour la logistique, de 0,892 à 0,895–0,900 pour le boosting), mais **les écarts entre les encodages sont plus petits que l'incertitude** d'une AUC mesurée sur 3 000 clients de test (une erreur-type d'environ 0,011, formule de Hanley et McNeil ; section 1.4). N'en tirez pas de classement. La leçon n'est pas « tel encodage est le meilleur » ; elle est : **avec peu de modalités bien peuplées, tous conviennent ; avec beaucoup de modalités rares, seul le calcul hors pli reste honnête**.

> ✅ **À retenir (encodage).** *One-hot* pour les modèles linéaires et peu de modalités ; ordinal seulement si l'ordre existe ; fréquence quand on veut une seule colonne sans la cible ; **cible** pour beaucoup de modalités, mais **toujours hors pli et lissée**. Et jamais avec les lignes du jeu de test.

### 4.1.3 Mettre les variables à la même échelle

La **mise à l'échelle** (*scaling*) remplace chaque variable $x$ par une version dont l'unité a disparu. Quatre transformations dominent.

| Transformation | Formule | Propriété |
|---|---|---|
| **Standardisation** | $\dfrac{x-\bar x}{s}$ | moyenne 0, écart-type 1 ; sensible aux valeurs extrêmes |
| **Min-max** | $\dfrac{x-x_{\min}}{x_{\max}-x_{\min}}$ | tout dans $[0,1]$ ; une valeur extrême écrase les autres |
| **Robuste** | $\dfrac{x-\text{médiane}}{Q_3-Q_1}$ | utilise médiane et écart interquartile, **insensible** aux extrêmes |
| **Quantile** | rang de $x$ dans le jeu d'entraînement, ramené à $[0,1]$ | distribution uniforme ; défait toute asymétrie |

Un exemple à la main montre leurs différences. Cinq montants d'achats : 20, 25, 30, 35 et 400 € (le dernier est un gros achat professionnel). La moyenne vaut $102$ et l'écart-type $\approx149{,}1$ ; la médiane vaut $30$ et l'écart interquartile $35-25=10$.

```python hide
valeurs = np.array([20, 25, 30, 35, 400.0])
mu, sd = valeurs.mean(), valeurs.std()
exemple = pd.DataFrame({
    "montant": valeurs,
    "standardisé": (valeurs - mu) / sd,
    "min-max": (valeurs - valeurs.min()) / (valeurs.max() - valeurs.min()),
    "robuste": (valeurs - np.median(valeurs)) / (np.percentile(valeurs, 75) - np.percentile(valeurs, 25)),
    "quantile (rang)": pd.Series(valeurs).rank(method="min").sub(1).div(len(valeurs) - 1).values,
}).round(3)
print("moyenne", mu, "écart-type", round(sd, 2))
print(exemple.to_string(index=False))
```
<!--sortie-->
```text
moyenne 102.0 écart-type 149.08
 montant  standardisé  min-max  robuste  quantile (rang)
    20.0       -0.550    0.000     -1.0             0.00
    25.0       -0.516    0.013     -0.5             0.25
    30.0       -0.483    0.026      0.0             0.50
    35.0       -0.449    0.039      0.5             0.75
   400.0        1.999    1.000     37.0             1.00
```

```python hide-code
print(exemple.to_string(index=False))
```
<!--sortie-->
```text
 montant  standardisé  min-max  robuste  quantile (rang)
    20.0       -0.550    0.000     -1.0             0.00
    25.0       -0.516    0.013     -0.5             0.25
    30.0       -0.483    0.026      0.0             0.50
    35.0       -0.449    0.039      0.5             0.75
   400.0        1.999    1.000     37.0             1.00
```

La valeur extrême a deux effets opposés. Avec la **standardisation** et le **min-max**, les quatre petits montants se retrouvent **tassés** dans une toute petite plage (de $-0{,}55$ à $-0{,}45$ ; de $0$ à $0{,}04$) : l'information qui les distingue s'écrase. Avec la transformation **robuste**, ils gardent leur écart ($-1$ à $0{,}5$) et c'est la valeur extrême qui part très loin ($37$) : c'est exactement ce qu'on souhaite. La transformation **quantile** étale tout régulièrement et ne se soucie plus des écarts réels : elle est utile quand seule l'**ordre** compte.

#### Quel modèle a besoin de quoi ?

Mesurons-le sur les clients : 12 variables numériques, quatre modèles, avec et sans standardisation.

```python hide
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import QuantileTransformer, RobustScaler

num12 = ["age", "anciennete_mois", "nb_commandes_12m", "montant_12m", "recence_jours", "nb_retours_12m",
         "nb_tickets_support_12m", "programme_fidelite", "nb_promos_recues_12m", "part_achats_promo",
         "taux_ouverture_email", "revenu_zone"]
Xn = clients[num12]


def score(modele, scaler=None, decision=False):
    m = make_pipeline(scaler, modele) if scaler is not None else modele
    m.fit(Xn.loc[tr], ytr)
    s = m.decision_function(Xn.loc[te]) if decision else m.predict_proba(Xn.loc[te])[:, 1]
    return roc_auc_score(yte, s)


echelles = pd.DataFrame({
    "modèle": ["régression logistique", "k plus proches voisins (k = 25)", "SVM à noyau gaussien", "arbre de décision (profondeur 5)"],
    "sans mise à l'échelle": [score(LogisticRegression(max_iter=5000)), score(KNeighborsClassifier(25)),
                              score(SVC(), decision=True), score(DecisionTreeClassifier(max_depth=5, random_state=0))],
    "standardisation": [score(LogisticRegression(max_iter=5000), StandardScaler()), score(KNeighborsClassifier(25), StandardScaler()),
                        score(SVC(), StandardScaler(), decision=True), score(DecisionTreeClassifier(max_depth=5, random_state=0), StandardScaler())],
    "quantile": [score(LogisticRegression(max_iter=5000), QuantileTransformer(n_quantiles=200)),
                 score(KNeighborsClassifier(25), QuantileTransformer(n_quantiles=200)),
                 score(SVC(), QuantileTransformer(n_quantiles=200), decision=True),
                 score(DecisionTreeClassifier(max_depth=5, random_state=0), QuantileTransformer(n_quantiles=200))],
}).round(3)
print(echelles.to_string(index=False))
raw = LogisticRegression(penalty="l1", solver="liblinear", C=0.01, max_iter=5000).fit(Xn.loc[tr], ytr)
std = LogisticRegression(penalty="l1", solver="liblinear", C=0.01, max_iter=5000).fit(StandardScaler().fit(Xn.loc[tr]).transform(Xn.loc[tr]), ytr)
gardees_brut = [n for n, k in zip(num12, raw.coef_[0]) if k != 0]
gardees_std = [n for n, k in zip(num12, std.coef_[0]) if k != 0]
print("pénalité L1 (C = 0,01), variables conservées :", len(gardees_brut), "sans mise à l'échelle,", len(gardees_std), "avec")
print("conservées seulement sans mise à l'échelle :", sorted(set(gardees_brut) - set(gardees_std)))
print("conservées seulement avec standardisation  :", sorted(set(gardees_std) - set(gardees_brut)))
```
<!--sortie-->
```text
                          modèle  sans mise à l'échelle  standardisation  quantile
           régression logistique                  0.856            0.856     0.850
 k plus proches voisins (k = 25)                  0.828            0.853     0.838
            SVM à noyau gaussien                  0.746            0.788     0.781
arbre de décision (profondeur 5)                  0.859            0.859     0.859
pénalité L1 (C = 0,01), variables conservées : 8 sans mise à l'échelle, 8 avec
conservées seulement sans mise à l'échelle : ['nb_promos_recues_12m', 'revenu_zone']
conservées seulement avec standardisation  : ['part_achats_promo', 'programme_fidelite']
```

```python hide-code
print(echelles.to_string(index=False))
print("L1, C = 0,01 -> conservées seulement SANS échelle :", sorted(set(gardees_brut) - set(gardees_std)))
print("L1, C = 0,01 -> conservées seulement AVEC standardisation :", sorted(set(gardees_std) - set(gardees_brut)))
```
<!--sortie-->
```text
                          modèle  sans mise à l'échelle  standardisation  quantile
           régression logistique                  0.856            0.856     0.850
 k plus proches voisins (k = 25)                  0.828            0.853     0.838
            SVM à noyau gaussien                  0.746            0.788     0.781
arbre de décision (profondeur 5)                  0.859            0.859     0.859
L1, C = 0,01 -> conservées seulement SANS échelle : ['nb_promos_recues_12m', 'revenu_zone']
L1, C = 0,01 -> conservées seulement AVEC standardisation : ['part_achats_promo', 'programme_fidelite']
```

Le tableau confirme la théorie. Pour le **k plus proches voisins**, la standardisation fait passer l'AUC de 0,828 à 0,853 : sans elle, le montant (en centaines d'euros) écrase tout dans le calcul des distances. Pour le **SVM**, le gain est de 0,746 à 0,788. L'**arbre** ne bouge pas (0,859 dans tous les cas) : les seuils changent de valeur, pas de sens. Quant à la **régression logistique**, son AUC ne change pas ici (0,856), parce que la solution d'un modèle sans pénalité ne dépend pas de l'unité des variables : si l'on multiplie une variable par 1 000, son coefficient est divisé par 1 000 et les prédictions restent les mêmes. Il en va autrement dès qu'on **pénalise** les coefficients (régularisation, volume II, section 1.5 ; nous y revenons au chapitre 2) : une pénalité compte les coefficients, et un coefficient dépend de l'unité de sa variable. La dernière ligne de la sortie montre l'effet sur une pénalité $\ell_1$ forte (qui met à zéro les variables peu utiles) : sans mise à l'échelle, elle **écarte** `programme_fidelite` et `part_achats_promo` (des variables de petite échelle, 0/1 et 0 à 1, qui ont besoin de gros coefficients pour peser) et garde `revenu_zone` et `nb_promos_recues_12m` ; avec la standardisation, la sélection s'inverse. L'AUC bouge peu, mais **le modèle n'est plus le même** : sans mise à l'échelle, l'unité décide de ce qui est « important ».

> 💡 **Règle pratique.** Standardisez pour tout ce qui calcule des distances ou pénalise des coefficients (kNN, SVM, régression régularisée, réseaux, ACP). Ne vous en souciez pas pour les arbres, forêts et boosting. En cas de valeurs extrêmes marquées, préférez la version robuste.

### 4.1.4 Corriger l'asymétrie : logarithme, Box-Cox, Yeo-Johnson

Les montants, les durées et les effectifs sont presque toujours **asymétriques à droite** : beaucoup de petites valeurs, quelques très grandes (c'est la situation des paniers, vue au volume I, section 3.1.3). Une transformation **concave** (le logarithme, la racine) resserre la queue de droite et rend la distribution plus symétrique. La famille de **Box-Cox** généralise cette idée avec un paramètre $\lambda$ choisi sur les données :

$$x\mapsto\begin{cases}\dfrac{x^{\lambda}-1}{\lambda}&\lambda\neq0\\[2mm]\ln x&\lambda=0\end{cases}\qquad(x>0).$$

Pour $\lambda=1$, on ne change rien (à une translation près) ; pour $\lambda=0$, c'est le logarithme ; pour $\lambda=\frac12$, une racine. Box-Cox exige des valeurs **strictement positives**. La version de **Yeo-Johnson** accepte aussi zéro et les valeurs négatives, en traitant chaque signe à part :

$$x\mapsto\begin{cases}\dfrac{(x+1)^{\lambda}-1}{\lambda}&x\ge0,\ \lambda\neq0\\[1mm]\ln(x+1)&x\ge0,\ \lambda=0\\[1mm]-\dfrac{(1-x)^{2-\lambda}-1}{2-\lambda}&x<0,\ \lambda\neq2\end{cases}$$

(le cas $x<0,\ \lambda=2$ est $-\ln(1-x)$). Le paramètre $\lambda$ est choisi par maximum de vraisemblance, **sur le jeu d'entraînement**.

```python hide
from sklearn.preprocessing import PowerTransformer

cols_asym = ["montant_12m", "nb_commandes_12m", "recence_jours", "panier_moyen"]
Z = clients[cols_asym].dropna()
pt = PowerTransformer(method="yeo-johnson").fit(Z)
asym = pd.DataFrame({
    "brute": Z.skew(),
    "après log(1 + x)": np.log1p(Z).skew(),
    "après Yeo-Johnson": pd.DataFrame(pt.transform(Z), columns=cols_asym).skew(),
}).round(2)
lambdas = dict(zip(cols_asym, pt.lambdas_.round(2)))
print(asym.to_string())
print("paramètres lambda de Yeo-Johnson :", lambdas)

fig, ax = plt.subplots(1, 3, figsize=(11, 3.2), sharey=False)
v = Z["montant_12m"]
for a, (titre, donnees, coul) in zip(ax, [("Brut", v, BLEU), ("log(1 + x)", np.log1p(v), ORANGE),
                                           ("Yeo-Johnson", pd.Series(pt.transform(Z)[:, 0]), AQUA)]):
    a.hist(donnees, bins=45, color=coul, alpha=0.9)
    a.set_title(titre)
    a.set_xlabel("montant des 12 derniers mois")
ax[0].set_ylabel("nombre de clients")
plt.tight_layout()
plt.savefig("figures/ch04-asymetrie.png", dpi=200, bbox_inches="tight")
plt.close()

Xlog = clients[NUM].copy()
for col in ["montant_12m", "nb_commandes_12m", "recence_jours", "panier_moyen", "nb_retours_12m", "nb_tickets_support_12m", "nb_promos_recues_12m"]:
    Xlog[col] = np.log1p(Xlog[col])
print("logistique : variables brutes", auc_logit(clients[NUM]), "| variables en log(1 + x)", auc_logit(Xlog))
```
<!--sortie-->
```text
                  brute  après log(1 + x)  après Yeo-Johnson
montant_12m        2.88              0.06               0.00
nb_commandes_12m   1.71              0.35               0.06
recence_jours      1.89             -0.48              -0.03
panier_moyen       2.54              0.75              -0.00
paramètres lambda de Yeo-Johnson : {'montant_12m': np.float64(-0.03), 'nb_commandes_12m': np.float64(-0.29), 'recence_jours': np.float64(0.15), 'panier_moyen': np.float64(-0.47)}
logistique : variables brutes 0.858 | variables en log(1 + x) 0.852
```

```python hide-code
print(asym.to_string())
```
<!--sortie-->
```text
                  brute  après log(1 + x)  après Yeo-Johnson
montant_12m        2.88              0.06               0.00
nb_commandes_12m   1.71              0.35               0.06
recence_jours      1.89             -0.48              -0.03
panier_moyen       2.54              0.75              -0.00
```

![Distribution du montant dépensé sur 12 mois (clients ayant commandé) : brut, après le logarithme, après la transformation de Yeo-Johnson.](figures/ch04-asymetrie.png)

Le coefficient d'asymétrie (volume I, section 3.1) du montant passe de 2,88 à 0,06 avec le logarithme, et à 0,00 avec Yeo-Johnson : la distribution devient presque symétrique. Mais une transformation qui rend les histogrammes plus jolis **améliore-t-elle le modèle** ? Ici, non : la régression logistique sur les variables brutes obtient une AUC de 0,858, et de 0,852 après passage au logarithme. Le départ d'un client dépend de variables comme la récence *en jours* avec des seuils qui ont un sens dans cette unité ; les écraser ne l'aide pas. **Une transformation est une hypothèse sur la forme de la relation avec la cible**, pas un nettoyage neutre.

> ⚠️ **Normaliser n'est pas toujours utile.** On transforme pour un modèle donné et pour une raison précise (une régression linéaire sensible aux extrêmes, un SVM, un graphique lisible), pas par réflexe. Les modèles à base d'arbres n'en tirent rien. Et il faut **toujours** mesurer sur un jeu de validation.

**Découper en classes** (*binning*) est une autre façon de se libérer de la forme : on remplace une variable continue par des classes (« moins de 30 jours », « 30 à 60 jours »…), ensuite encodées en *one-hot*. Cela permet à un modèle linéaire de représenter une relation non monotone ou à seuils, mais au prix de pertes d'information à l'intérieur des classes, et de frontières à choisir. Nous verrons mieux en 4.2 comment trouver des frontières utiles à partir des données.

### 4.1.5 Les valeurs manquantes

Une valeur manquante n'est pas un détail technique : elle **raconte quelque chose** sur la façon dont les données ont été produites. On distingue trois mécanismes (volume II, introduction : les hypothèses se vérifient).

- **MCAR** (*missing completely at random*) : l'absence ne dépend de rien. Un capteur tombe en panne au hasard. Supprimer les lignes ou imputer ne biaise pas.
- **MAR** (*missing at random*) : l'absence dépend d'autres variables **observées**. Les clients qui n'ont pas d'appareil enregistré sont plus souvent ceux venus en boutique. On peut corriger en s'appuyant sur ces variables.
- **MNAR** (*missing not at random*) : l'absence dépend de la valeur **manquante elle-même**. Les clients mécontents répondent moins à l'enquête de satisfaction. On ne peut pas la corriger complètement avec les seules données observées.

Nos clients contiennent quatre variables incomplètes, de natures différentes.

```python hide
manque = []
for col, nature in [("panier_moyen", "structurelle : aucune commande, donc aucun panier"),
                    ("satisfaction_moy", "probablement MNAR : les clients peu satisfaits répondent moins"),
                    ("appareil", "aléatoire (MCAR) : appareil non enregistré"),
                    ("delai_livraison_moy", "aléatoire (MCAR) : livraison non renseignée")]:
    m = clients[col].isna()
    manque.append({"variable": col, "part manquante": m.mean(), "départs si manquante": y[m].mean(),
                   "départs si renseignée": y[~m].mean(), "nature": nature})
tab_manque = pd.DataFrame(manque).round(3)
sans_commande = (clients["nb_commandes_12m"] == 0)
print(tab_manque.drop(columns="nature").to_string(index=False))
print("panier manquant exactement quand aucune commande :", bool((clients["panier_moyen"].isna() == sans_commande).all()))
print("part des clients sans aucune valeur manquante (14 variables numériques) :", round(clients[NUM].notna().all(axis=1).mean(), 3))
```
<!--sortie-->
```text
           variable  part manquante  départs si manquante  départs si renseignée
       panier_moyen           0.136                 0.420                  0.096
   satisfaction_moy           0.128                 0.115                  0.144
           appareil           0.152                 0.154                  0.138
delai_livraison_moy           0.120                 0.135                  0.141
panier manquant exactement quand aucune commande : True
part des clients sans aucune valeur manquante (14 variables numériques) : 0.664
```

```python hide-code
print(tab_manque.drop(columns="nature").to_string(index=False))
```
<!--sortie-->
```text
           variable  part manquante  départs si manquante  départs si renseignée
       panier_moyen           0.136                 0.420                  0.096
   satisfaction_moy           0.128                 0.115                  0.144
           appareil           0.152                 0.154                  0.138
delai_livraison_moy           0.120                 0.135                  0.141
```

Les chiffres montrent que **le fait d'être manquant est parfois très informatif**. Un panier manquant signifie « aucune commande en 12 mois », et ces clients partent dans **42 %** des cas contre 9,6 % pour les autres. L'absence de satisfaction, elle, est liée à un taux de départ plus faible (11,5 % contre 14,4 %). Les deux autres variables (appareil, livraison) n'ont aucun lien avec le départ, comme attendu d'une absence aléatoire.

#### Que faire ?

- **Supprimer les lignes incomplètes** : simple, mais dans ce jeu seules 66 % des lignes sont complètes ; on jette un tiers des clients et on biaise l'échantillon dès que l'absence est informative.
- **Imputer** par une valeur : la moyenne, la médiane, une constante, la valeur des plus proches voisins, ou une prédiction par un autre modèle (imputation itérative).
- **Ajouter un indicateur d'absence** : une colonne 0/1 « cette valeur était manquante », à côté de la valeur imputée. Le modèle peut ainsi utiliser l'absence comme information.
- **Laisser le modèle s'en occuper** : certains boostings (`HistGradientBoosting`, XGBoost, LightGBM) gèrent nativement les valeurs manquantes en apprenant, à chaque seuil, de quel côté les envoyer.

Comparons-les sur nos données.

```python hide
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer

Xm = clients[NUM]
strategies = [("moyenne", SimpleImputer(strategy="mean")), ("médiane", SimpleImputer(strategy="median")),
              ("médiane + indicateurs d'absence", SimpleImputer(strategy="median", add_indicator=True)),
              ("constante 0 + indicateurs d'absence", SimpleImputer(strategy="constant", fill_value=0, add_indicator=True)),
              ("plus proches voisins (k = 5)", KNNImputer(n_neighbors=5)),
              ("imputation itérative", IterativeImputer(random_state=0, max_iter=5))]
lignes = []
for nom, imp in strategies:
    A, B = imp.fit_transform(Xm.loc[tr]), imp.transform(Xm.loc[te])
    sc = StandardScaler().fit(A)
    lg = LogisticRegression(max_iter=3000).fit(sc.transform(A), ytr)
    gb = HistGradientBoostingClassifier(random_state=0, max_iter=100).fit(A, ytr)
    lignes.append({"stratégie": nom, "AUC logistique": roc_auc_score(yte, lg.predict_proba(sc.transform(B))[:, 1]),
                   "AUC boosting": roc_auc_score(yte, gb.predict_proba(B)[:, 1])})
gb_nat = HistGradientBoostingClassifier(random_state=0, max_iter=100).fit(Xm.loc[tr], ytr)
lignes.append({"stratégie": "boosting : gestion native (aucune imputation)", "AUC logistique": np.nan,
               "AUC boosting": roc_auc_score(yte, gb_nat.predict_proba(Xm.loc[te])[:, 1])})
tab_imput = pd.DataFrame(lignes).round(3)
print(tab_imput.to_string(index=False, na_rep="-"))
```
<!--sortie-->
```text
                                    stratégie  AUC logistique  AUC boosting
                                      moyenne           0.859         0.894
                                      médiane           0.859         0.896
              médiane + indicateurs d'absence           0.858         0.896
          constante 0 + indicateurs d'absence           0.858         0.894
                 plus proches voisins (k = 5)           0.859         0.894
                         imputation itérative           0.859         0.894
boosting : gestion native (aucune imputation)               -         0.892
```

```python hide-code
print(tab_imput.to_string(index=False, na_rep="-"))
```
<!--sortie-->
```text
                                    stratégie  AUC logistique  AUC boosting
                                      moyenne           0.859         0.894
                                      médiane           0.859         0.896
              médiane + indicateurs d'absence           0.858         0.896
          constante 0 + indicateurs d'absence           0.858         0.894
                 plus proches voisins (k = 5)           0.859         0.894
                         imputation itérative           0.859         0.894
boosting : gestion native (aucune imputation)               -         0.892
```

Les sept lignes donnent **pratiquement le même résultat** : de 0,858 à 0,859 pour la logistique, de 0,892 à 0,896 pour le boosting. Dans ces données, le choix de l'imputation n'a quasiment aucune importance, d'abord parce que les variables qui comptent vraiment (récence, nombre de commandes) sont complètes, ensuite parce que l'information « pas de commande » est déjà portée par une variable observée. C'est rassurant, mais **pas universel** : le petit exemple suivant montre un cas où l'indicateur d'absence change tout.

#### Quand l'absence est l'information

Simulons 6 000 clients avec une variable $x$ liée à la cible ($y=1$ si le client part), et rendons $x$ manquante **plus souvent quand le client part** : un mécanisme MNAR, comme un client qui a demandé à résilier et que l'on n'a plus mesuré.

```python hide
rng = np.random.default_rng(11)
n = 6000
x = rng.normal(size=n)
yy = rng.binomial(1, 1 / (1 + np.exp(-(-1.5 + 0.8 * x))))
manquant = rng.random(n) < np.where(yy == 1, 0.55, 0.10)                  # absence beaucoup plus fréquente quand yy = 1
xobs = np.where(manquant, np.nan, x)
Xd = pd.DataFrame({"x": xobs})
a_tr, a_te, b_tr, b_te = train_test_split(Xd, yy, test_size=0.3, random_state=0, stratify=yy)


def auc_imput(add_ind):
    m = make_pipeline(SimpleImputer(strategy="mean", add_indicator=add_ind), LogisticRegression())
    m.fit(a_tr, b_tr)
    return roc_auc_score(b_te, m.predict_proba(a_te)[:, 1])


mn = pd.DataFrame({"traitement": ["imputation par la moyenne seule", "moyenne + indicateur d'absence"],
                   "AUC": [auc_imput(False), auc_imput(True)]}).round(3)
print("part manquante parmi les départs", round(manquant[yy == 1].mean(), 3), "| parmi les autres", round(manquant[yy == 0].mean(), 3))
print(mn.to_string(index=False))
```
<!--sortie-->
```text
part manquante parmi les départs 0.535 | parmi les autres 0.094
                     traitement   AUC
imputation par la moyenne seule 0.610
 moyenne + indicateur d'absence 0.819
```

```python hide-code
print(mn.to_string(index=False))
```
<!--sortie-->
```text
                     traitement   AUC
imputation par la moyenne seule 0.610
 moyenne + indicateur d'absence 0.819
```

Dans cette simulation, la valeur est manquante pour 53,5 % des départs contre 9,4 % des autres. Quand l'absence est informative, l'imputation seule jette cette information : l'AUC reste modeste (0,610). Avec l'indicateur, le modèle apprend que « absent » veut dire « probablement parti », et l'AUC grimpe à 0,819. D'où une règle simple : **ajoutez systématiquement un indicateur d'absence pour les variables dont on soupçonne que l'absence est informative**, et laissez le modèle juger.

> ⚠️ **Imputer avant de séparer, c'est une fuite.** La moyenne, la médiane ou les voisins utilisés pour remplir les trous doivent être calculés sur le jeu d'entraînement et **appliqués ensuite** au test. Imputer tout le tableau avant la séparation fait entrer de l'information du test dans l'entraînement. La fuite est faible pour une moyenne sur 12 000 lignes ; elle devient sérieuse avec de petits échantillons ou des imputations par modèle.

> ✅ **À retenir (valeurs manquantes).** Comprenez d'abord *pourquoi* c'est manquant (structurel, aléatoire, informatif). Supprimer des lignes est le dernier recours. Imputez par la médiane, **ajoutez un indicateur** quand l'absence peut signifier quelque chose, ou laissez un boosting gérer le manque. Et imputez **à l'intérieur** de la validation croisée.

### 4.1.6 Tout assembler, sans fuite : `Pipeline` et `ColumnTransformer`

Nous avons rencontré quatre opérations qui **apprennent quelque chose des données** : l'encodage par la cible (des moyennes), la standardisation (une moyenne et un écart-type), l'imputation (une médiane), la transformation de puissance (un $\lambda$). Pour chacune, la règle est la même : l'apprendre sur le jeu d'entraînement (ou, dans une validation croisée, sur les plis d'entraînement uniquement), puis l'appliquer au reste.

Faire cela à la main, pli après pli, est source d'oublis. Les bibliothèques fournissent des objets qui l'**imposent** :

- un **`Pipeline`** enchaîne des étapes (prétraitement, puis modèle) et se comporte comme un seul modèle : `fit` apprend toutes les étapes sur les données qu'on lui donne, `predict` les applique ;
- un **`ColumnTransformer`** applique des traitements différents à des groupes de colonnes (numériques d'un côté, qualitatives de l'autre).

Passé à `cross_val_score`, un pipeline refait **à chaque pli** l'apprentissage complet du prétraitement sur les plis d'entraînement : il n'y a plus de fuite possible, même par maladresse.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

numeriques = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
categories = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))
prep = ColumnTransformer([("num", numeriques, NUM),
                          ("cat", categories, ["ville", "canal_acquisition", "appareil", "categorie_preferee"])])
modele = make_pipeline(prep, LogisticRegression(max_iter=3000))
scores = cross_val_score(modele, clients.loc[tr], ytr, cv=5, scoring="roc_auc")
print(f"AUC en validation croisée : {scores.mean():.3f} (± {scores.std():.3f})")
```
<!--sortie-->
```text
AUC en validation croisée : 0.860 (± 0.013)
```

Cet assemblage est le **modèle complet** : les quatorze variables numériques sont imputées (avec indicateurs) puis standardisées, les quatre variables qualitatives sont imputées puis encodées en *one-hot* (`handle_unknown="ignore"` évite une erreur si une modalité n'a pas été vue à l'entraînement), puis la régression logistique est ajustée. La validation croisée porte sur le jeu d'entraînement (le jeu de test reste intouchable, chapitre 1, section 1.2) et donne une AUC de 0,860, avec un écart-type de 0,013 d'un pli à l'autre. Une fois ajusté sur tout l'entraînement, le pipeline obtient 0,866 sur le jeu de test, cohérent avec la validation croisée et un peu meilleur que la régression logistique sur les seules variables numériques (0,858), grâce aux quatre variables qualitatives.

> 💡 **Un seul objet à sauvegarder.** Une fois ajusté sur tout l'entraînement, le pipeline contient **tout** : prétraitement et modèle. Pour prédire sur de nouveaux clients, on lui donne la table brute. Impossible d'oublier une étape, ni d'appliquer à la production un prétraitement différent de celui de l'entraînement.

```python hide
modele_complet = make_pipeline(prep, LogisticRegression(max_iter=3000)).fit(clients.loc[tr], ytr)
auc_pipeline = roc_auc_score(yte, modele_complet.predict_proba(clients.loc[te])[:, 1])
print("AUC test du pipeline logistique complet :", round(auc_pipeline, 3))
```
<!--sortie-->
```text
AUC test du pipeline logistique complet : 0.866
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 (un pipeline complet pas à pas), 4.2 (l'encodage par la cible hors pli, écrit à la main) et 4.3 (comparer des stratégies pour les valeurs manquantes) ; exercices 4.1 à 4.5.
