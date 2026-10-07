```python hide
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

## 1.6 ➕ Pour aller plus loin : stratégies d'imputation et leur impact

> 🧭 **Section complémentaire.** Elle suppose la section 1.1 (les mécanismes d'absence). On y compare des méthodes d'imputation **à la vérité**, ce qui est le seul moyen honnête d'en juger.

**Imputer**, c'est remplacer une valeur manquante par une valeur estimée. C'est tentant (les modèles aiment les tableaux complets) et risqué (on fabrique des données). La bonne question n'est pas « quelle méthode est la meilleure ? » mais : **que veut-on préserver, et qu'est-ce que les autres colonnes permettent de savoir ?** Les données du chapitre permettent, pour une fois, de mesurer ce que chaque méthode abîme, puisque nous connaissons la vérité.

### 1.6.1 Imputer, c'est prédire : ce qu'on veut préserver

Une imputation est une **prédiction** de la valeur manquante à partir de ce que l'on sait par ailleurs. On peut la juger sur trois critères, qui ne vont pas toujours ensemble.

| On veut préserver… | Pourquoi | Méthode qui le fait mal |
|---|---|---|
| **la moyenne** | le chiffre annoncé ne doit pas se déplacer | supprimer les lignes (si le mécanisme n'est pas MCAR) |
| **la dispersion** | un intervalle de confiance, un écart-type, une part de cas extrêmes | remplacer par la moyenne : les valeurs imputées sont toutes **identiques** |
| **les liaisons entre variables** | un modèle, une corrélation, un tableau croisé | remplacer par la moyenne : le lien est **atténué** |

Quatre méthodes simples couvrent l'essentiel. La **moyenne** (ou la **médiane**, moins sensible aux extrêmes) remplace par une valeur centrale unique. La **moyenne par groupe** remplace par la moyenne d'un groupe proche (âge et canal). La **régression** prédit la valeur par un modèle linéaire des autres colonnes. Les **k plus proches voisins** (en anglais *k-nearest neighbours*) prennent la moyenne des dix clients les plus semblables, d'après leurs autres colonnes. On les écrit en une fonction.

```python
from sklearn.linear_model import LinearRegression
from sklearn.impute import KNNImputer
profil = pd.read_csv(os.path.join(D, "profil_clients.csv"))
verite = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))
profil["classe_age"] = pd.cut(profil["age"], [0, 29, 44, 59, 200], labels=["moins de 30", "30-44", "45-59", "60 et plus"])
X = pd.get_dummies(profil[["age", "canal_acquisition", "nb_commandes_2025", "minutes_site"]], drop_first=True).astype(float)
def imputations(col):
    m, obs = profil[col].isna(), profil[col]
    res = {"moyenne": pd.Series(obs.mean(), index=obs.index[m]), "médiane": pd.Series(obs.median(), index=obs.index[m])}
    res["moyenne par groupe"] = profil.groupby(["classe_age", "canal_acquisition"], observed=True)[col].transform("mean")[m]
    res["régression"] = pd.Series(LinearRegression().fit(X[~m], obs[~m]).predict(X[m]), index=obs.index[m])
    A = X.join(obs); Z = (A - A.mean()) / A.std()
    res["k plus proches voisins"] = pd.Series(KNNImputer(n_neighbors=10).fit_transform(Z)[:, -1][m.values] * obs.std() + obs.mean(), index=obs.index[m])
    return res
```

Pour **juger** chaque méthode, on compare les valeurs imputées aux vraies valeurs : l'erreur typique (racine de l'erreur quadratique moyenne, sur les seules cases imputées), le **biais** de la moyenne obtenue après imputation, et l'écart-type du tableau complété. La dernière ligne rappelle la **suppression** des lignes incomplètes (on garde les valeurs observées, on ignore le reste).

```python
def tableau(col):
    m = profil[col].isna(); vrai = verite.loc[m, col]; lignes = []
    for nom, imp in imputations(col).items():
        complet = profil[col].copy(); complet[m] = imp
        lignes.append((nom, np.sqrt(((imp - vrai) ** 2).mean()), complet.mean() - verite[col].mean(), complet.std()))
    lignes.append(("suppression des manquants", np.nan, profil[col].mean() - verite[col].mean(), profil[col].std()))
    print(f"vérité : moyenne {verite[col].mean():.2f}, écart-type {verite[col].std():.2f}")
    print(pd.DataFrame(lignes, columns=["méthode", "erreur_typique", "biais_moyenne", "écart_type"]).round(2).to_string(index=False))
```

### 1.6.2 Le revenu : une variable peu prévisible

Commençons par le revenu annuel, qui manque pour 17 % des clients selon un mécanisme MAR (section 1.1.3) : il manque plus souvent chez les moins de 30 ans et pour le canal réseaux.

```python
tableau("revenu_annuel")
```
<!--sortie-->
```text
vérité : moyenne 28321.77, écart-type 11212.22
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne        11188.57         218.89    10201.99
                  médiane        11137.51        -117.17    10228.39
       moyenne par groupe        10180.03         -24.14    10364.80
               régression        10079.84         -23.01    10369.30
   k plus proches voisins        10457.96         -20.77    10433.35
suppression des manquants             NaN         218.89    11219.76
```

Trois enseignements. **Premier : la moyenne est bien retrouvée par les méthodes qui tiennent compte de l'âge et du canal** (biais d'environ −20 à −24 €, contre +219 € pour la moyenne simple et pour la suppression). Les premières corrigent le mécanisme MAR, les secondes **l'ignorent**. **Deuxième : l'erreur individuelle reste énorme** (environ 10 000 € sur une valeur moyenne de 28 000 €), parce que l'âge, le canal et le comportement d'achat disent peu de chose sur le revenu : aucune méthode ne retrouve la valeur d'un client, elles ne font que respecter la moyenne d'un groupe. **Troisième : la moyenne simple écrase la dispersion** : l'écart-type tombe à 10 202 € au lieu de 11 212 € (−9 %), parce que 1 039 clients reçoivent exactement la même valeur.

![Distribution du revenu : la vérité, puis après imputation par la moyenne (un pic artificiel) et par la régression (une distribution plus étroite).](figures/ch01-imputation.png)

```python hide
m_rev = profil["revenu_annuel"].isna()
imp_rev = imputations("revenu_annuel")
rev_moy, rev_reg = profil["revenu_annuel"].copy(), profil["revenu_annuel"].copy()
rev_moy[m_rev], rev_reg[m_rev] = imp_rev["moyenne"], imp_rev["régression"]
C.fig_imputation(verite["revenu_annuel"], rev_moy, rev_reg, "figures/ch01-imputation.png")
```

> ⚠️ **Piège.** Un tableau imputé **a l'air complet** et donc plus fiable ; il est en réalité plus **trompeur** qu'un tableau avec des trous honnêtes, parce que les valeurs fabriquées n'ont pas la variabilité des vraies. Un écart-type, un intervalle de confiance ou une part de clients « à risque » calculés après une imputation par la moyenne sont **sous-estimés**.

### 1.6.3 La dépense : quand les autres colonnes savent

La dépense 2025 manque pour 5 % des clients, **au hasard** (MCAR). Mais, contrairement au revenu, elle est très prévisible à partir d'une autre colonne connue : le nombre de commandes (corrélation de 0,92 dans la vérité).

```python
tableau("depense_2025")
```
<!--sortie-->
```text
vérité : moyenne 220.79, écart-type 317.98
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne          286.54           0.68      311.53
                  médiane          307.15          -5.52      312.71
       moyenne par groupe          286.11           0.66      311.55
               régression          106.83           0.27      316.67
   k plus proches voisins          118.76          -0.17      316.17
suppression des manquants             NaN           0.68      319.54
```

Le contraste avec le revenu est frappant. Les méthodes qui exploitent le nombre de commandes **divisent l'erreur par près de trois** (107 € pour la régression, 119 € pour les voisins, contre 287 € pour la moyenne) et conservent l'écart-type (317 € et 316 €, contre 318 € en vérité). Quand une autre colonne **sait** quelque chose, l'imputation par modèle est précieuse ; quand aucune ne sait rien, elle n'apporte presque rien. Une imputation ne crée jamais d'information : elle **redistribue** celle qui existe.

Regardons enfin ce que l'imputation fait aux **liaisons** : la corrélation entre dépense et nombre de commandes vaut 0,923 en vérité.

```python
md = profil["depense_2025"].isna()
print("corrélation vraie :", round(verite["depense_2025"].corr(verite["nb_commandes_2025"]), 3), "| valeurs observées seules :", round(profil["depense_2025"].corr(profil["nb_commandes_2025"]), 3))
for nom, imp in imputations("depense_2025").items():
    complet = profil["depense_2025"].copy(); complet[md] = imp
    print(f"{nom:24s} {complet.corr(profil['nb_commandes_2025']):.3f}")
```
<!--sortie-->
```text
corrélation vraie : 0.923 | valeurs observées seules : 0.922
moyenne                  0.905
médiane                  0.902
moyenne par groupe       0.905
régression               0.925
k plus proches voisins   0.924
```

La moyenne **atténue** la corrélation (0,905 au lieu de 0,923 : les valeurs imputées n'ont aucun lien avec le nombre de commandes), la régression et les voisins la **préservent** (0,925 et 0,924). Attention au revers : une imputation par régression **fabrique** une relation (elle utilise la relation pour prédire) ; si l'on calcule ensuite un modèle entre ces deux variables, la relation est en partie **circulaire**.

### 1.6.4 La satisfaction : aucune méthode ne répare un MNAR

Dernier cas, le plus instructif : la satisfaction moyenne, qui manque pour 9 % des clients **selon sa propre valeur** (section 1.1.3). Aucune autre colonne ne sait ce que pense le client.

```python
tableau("satisfaction_moy")
```
<!--sortie-->
```text
vérité : moyenne 3.73, écart-type 0.68
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne            0.83           0.02        0.64
                  médiane            0.83           0.02        0.64
       moyenne par groupe            0.82           0.02        0.64
               régression            0.82           0.02        0.64
   k plus proches voisins            0.84           0.02        0.64
suppression des manquants             NaN           0.02        0.67
```

Toutes les méthodes se valent : l'erreur individuelle (0,83 point) est celle que l'on commettrait en devinant la moyenne, et **toutes conservent le même biais** de +0,02 point. Sur la moyenne, le dégât est faible. Sur la **part de clients très mécontents** (satisfaction inférieure ou égale à 2,5), il est important.

```python
ms = profil["satisfaction_moy"].isna()
print("part de satisfactions ≤ 2,5 : vérité", round((verite["satisfaction_moy"] <= 2.5).mean() * 100, 2), "% | valeurs observées seules", round((profil["satisfaction_moy"].dropna() <= 2.5).mean() * 100, 2), "%")
for nom, imp in imputations("satisfaction_moy").items():
    complet = profil["satisfaction_moy"].copy(); complet[ms] = imp
    print(f"après imputation ({nom}) : {(complet <= 2.5).mean() * 100:.2f} %")
```
<!--sortie-->
```text
part de satisfactions ≤ 2,5 : vérité 4.08 % | valeurs observées seules 2.81 %
après imputation (moyenne) : 2.55 %
après imputation (médiane) : 2.55 %
après imputation (moyenne par groupe) : 2.55 %
après imputation (régression) : 2.55 %
après imputation (k plus proches voisins) : 2.55 %
```

Les clients très mécontents représentent 4,08 % de la clientèle en vérité. Les valeurs observées seules en montrent 2,81 %, parce que les mécontents répondent moins. Et **chaque imputation donne 2,55 %**, **pire** que de ne rien faire : on remplit les trous avec des valeurs centrales, qui ne sont jamais « très mécontentes ». Le MNAR a effacé l'information, et l'imputation ne l'a pas retrouvée.

Que peut-on faire ? On ne peut pas **corriger** un MNAR, mais on peut en mesurer l'**importance** par une **analyse de sensibilité** : supposer que les non-répondants sont moins satisfaits que les répondants d'un certain écart $\delta$, et regarder ce que devient la conclusion.

```python
obs = profil["satisfaction_moy"]
for delta in (0, 0.1, 0.2, 0.3):
    complet = obs.copy(); complet[ms] = obs.mean() - delta
    print(f"si les non-répondants sont {delta:.1f} point moins satisfaits : moyenne {complet.mean():.3f}")
print("vérité :", round(verite["satisfaction_moy"].mean(), 3), "| écart réel entre répondants et non-répondants :", round(obs.mean() - verite.loc[ms, "satisfaction_moy"].mean(), 3))
```
<!--sortie-->
```text
si les non-répondants sont 0.0 point moins satisfaits : moyenne 3.747
si les non-répondants sont 0.1 point moins satisfaits : moyenne 3.738
si les non-répondants sont 0.2 point moins satisfaits : moyenne 3.728
si les non-répondants sont 0.3 point moins satisfaits : moyenne 3.719
vérité : 3.729 | écart réel entre répondants et non-répondants : 0.195
```

Dans la vraie vie, on ne connaît pas l'écart (0,195 point ici, que seule la vérité programmée révèle) ; on essaie une plage plausible et l'on **dit ce que devient la conclusion** : « avec un écart entre 0 et 0,3 point, la satisfaction moyenne se situe entre 3,72 et 3,75 ». Si la décision change selon l'hypothèse, il faut collecter des données, pas imputer.

> ✅ **À retenir.** Aucune imputation ne répare un **MNAR**. Pour MCAR, presque toutes les méthodes préservent la moyenne ; pour MAR, il faut des méthodes qui utilisent les variables dont dépend l'absence ; pour MNAR, il reste **l'analyse de sensibilité** et la collecte d'information supplémentaire.

### 1.6.5 L'imputation multiple : dire l'incertitude

Une imputation unique a un défaut fondamental : on traite la valeur imputée comme **si elle était vraie**. Les intervalles de confiance calculés ensuite sont donc **trop étroits** : ils ignorent que 17 % des revenus sont des estimations. L'**imputation multiple** corrige cela en produisant non pas un tableau complété, mais **plusieurs** (par exemple vingt), chacun avec des valeurs imputées **tirées au hasard** dans l'incertitude du modèle. On analyse chaque tableau, puis on **combine** les résultats : la moyenne des moyennes est l'estimation, et l'incertitude additionne la variabilité à l'intérieur de chaque tableau et celle **entre** les tableaux.

> 📐 **Règles de combinaison (Rubin).** Avec $m$ tableaux imputés, d'estimations $\hat Q_1,\dots,\hat Q_m$ et de variances estimées $U_1,\dots,U_m$ : l'estimation finale est $\bar Q=\frac1m\sum \hat Q_i$ ; la variance intra est $\bar U=\frac1m\sum U_i$ ; la variance inter est $B=\frac1{m-1}\sum(\hat Q_i-\bar Q)^2$ ; la variance totale est $T=\bar U+\left(1+\frac1m\right)B$.

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
A = X.join(profil["revenu_annuel"]); estim, variances = [], []
for graine in range(20):
    complet = pd.Series(IterativeImputer(sample_posterior=True, random_state=graine, max_iter=10).fit_transform(A)[:, -1], index=profil.index)
    estim.append(complet.mean()); variances.append(complet.var() / len(complet))
estim, variances = np.array(estim), np.array(variances)
intra, inter = variances.mean(), estim.var(ddof=1)
print("moyenne combinée :", round(estim.mean(), 1), "| erreur type totale :", round(np.sqrt(intra + (1 + 1 / 20) * inter), 1), "(intra", round(np.sqrt(intra), 1), ", inter", round(np.sqrt(inter), 1), ")")
```
<!--sortie-->
```text
moyenne combinée : 28303.9 | erreur type totale : 159.3 (intra 145.4 , inter 63.4 )
```

Comparons à ce qu'aurait donné l'imputation par la moyenne : le calcul naïf trouve une **erreur type de 131,7 €**, soit 17 % **de moins** que les 159,3 € de l'imputation multiple. Le calcul naïf **se croit plus précis qu'il ne l'est**. L'estimation combinée (28 304 €) est aussi plus proche de la vérité (28 322 €) que la suppression des lignes (28 541 €). L'imputation multiple est la méthode de référence quand on a besoin d'intervalles honnêtes ; elle est plus lourde, et rarement nécessaire pour une simple moyenne par groupe.

```python
complet = profil["revenu_annuel"].fillna(profil["revenu_annuel"].mean())
print("erreur type après imputation par la moyenne :", round(complet.std() / np.sqrt(len(complet)), 1), "| avec les seules valeurs observées :", round(profil["revenu_annuel"].std() / np.sqrt(profil["revenu_annuel"].notna().sum()), 1))
```
<!--sortie-->
```text
erreur type après imputation par la moyenne : 131.7 | avec les seules valeurs observées : 159.3
```

### 1.6.6 L'indicateur de manquant et la décision finale

Une dernière technique, simple, évite de choisir : **garder trace de l'absence**. On ajoute à côté de la colonne une colonne `…_manquant` (1 si la valeur manquait, 0 sinon) et l'on peut ensuite imputer ce que l'on veut. L'indicateur laisse à un modèle la possibilité de **voir** l'absence, qui est elle-même une information. Elle l'est ici : les clients dont la satisfaction manque sont, en vérité, **moins satisfaits** que les répondants (3,55 en moyenne contre 3,75).

```python
profil["satisfaction_manquante"] = profil["satisfaction_moy"].isna().astype(int)
print("satisfaction vraie moyenne des clients dont la valeur manque :", round(verite.loc[ms, "satisfaction_moy"].mean(), 2), "| de ceux qui ont répondu :", round(verite.loc[~ms, "satisfaction_moy"].mean(), 2))
```
<!--sortie-->
```text
satisfaction vraie moyenne des clients dont la valeur manque : 3.55 | de ceux qui ont répondu : 3.75
```

Voici le tableau de décision que l'on peut retenir pour la préparation d'une colonne avec trous.

| Situation | Que faire | Méthode adaptée |
|---|---|---|
| Une règle logique donne la valeur | **déduire** (section 1.1.2) | zéro logique, valeur d'une autre colonne |
| Peu de trous (moins de 5 %), au hasard | supprimer ou laisser | moyennes qui ignorent les manquants |
| Trous qui dépendent d'une variable connue (MAR) | imputer **avec** cette variable | moyenne par groupe, régression, voisins |
| Une autre colonne prédit bien la valeur | imputer par modèle | régression, voisins, imputation multiple |
| On a besoin d'intervalles de confiance | imputer **plusieurs fois** | imputation multiple |
| Le trou dépend de la valeur manquante (MNAR) | **mesurer la sensibilité**, collecter | indicateur de manquant, hypothèses explicites |

> ⚠️ **Piège.** Ne jamais imputer **avant** de séparer l'entraînement du test, quand l'imputation sert à un modèle de prédiction : calculer la moyenne sur tout le tableau fait fuir de l'information du test vers l'entraînement. L'imputation s'apprend sur l'entraînement et s'applique au test (c'est ce que fait un *pipeline*).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.11 et 1.12.
