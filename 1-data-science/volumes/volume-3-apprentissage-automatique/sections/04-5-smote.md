## 4.5 ➕ Pour aller plus loin : SMOTE et ses variantes

> 🧭 **Section optionnelle.** Elle présente la méthode de rééchantillonnage la plus connue pour les classes rares, et, surtout, montre sur nos données **quand elle ne sert à rien**. On peut la sauter à la première lecture.

Le sur-échantillonnage aléatoire (4.3.3) recopie les exemples rares. Son défaut est évident : il fabrique des **doublons exacts**, que le modèle peut apprendre par cœur. L'idée de **SMOTE** (*Synthetic Minority Over-sampling TEchnique*, Chawla et al., 2002) est de créer des exemples **nouveaux mais plausibles**, en **interpolant** entre exemples rares voisins.

### 4.5.1 L'idée : interpoler entre voisins

Pour fabriquer un exemple synthétique, SMOTE procède ainsi :

1. choisir au hasard un exemple de la classe rare, $x$ ;
2. trouver ses $k$ plus proches voisins **dans la classe rare** (par défaut $k=5$) et en choisir un au hasard, $x'$ ;
3. tirer un nombre $\lambda$ au hasard entre 0 et 1, et créer le point $x_{\text{nouveau}}=x+\lambda\,(x'-x)$, sur le segment qui relie $x$ à $x'$.

On répète jusqu'à obtenir l'équilibre voulu. Un exemple à la main avec une fraude réelle de notre jeu d'entraînement et son **plus proche voisin** parmi les fraudes, décrites par deux variables (le montant et l'ancienneté du compte en jours) :

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold, cross_val_score
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.pipeline import Pipeline as PipeIB
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

trans = pd.read_csv("donnees/transactions.csv")
Xt = pd.get_dummies(trans.drop(columns=["id_commande", "fraude", "type_fraude"]), dtype=float)
yt = trans["fraude"]
Xa, Xb, ya, yb = train_test_split(Xt, yt, test_size=0.3, random_state=0, stratify=yt)
from sklearn.neighbors import NearestNeighbors

fraudes = Xa[ya == 1][["montant", "age_compte_jours"]]
echelle = StandardScaler().fit_transform(np.log1p(fraudes))                    # les voisins se cherchent à l'échelle réduite
voisins = NearestNeighbors(n_neighbors=2).fit(echelle).kneighbors(echelle[:1])[1][0]
x1, x2 = fraudes.iloc[0].values, fraudes.iloc[voisins[1]].values            # une fraude et son plus proche voisin parmi les fraudes
print("types des deux fraudes (1 = compte neuf, 2 = prise de contrôle) :", trans.loc[[fraudes.index[0], fraudes.index[voisins[1]]], "type_fraude"].tolist())
lam = 0.4
nouveau = x1 + lam * (x2 - x1)
print("fraude 1 :", x1.round(1), "| fraude 2 :", x2.round(1))
print("point synthétique pour lambda = 0,4 :", nouveau.round(1))
```
<!--sortie-->
```text
types des deux fraudes (1 = compte neuf, 2 = prise de contrôle) : [1, 1]
fraude 1 : [72.4  2. ] | fraude 2 : [77.4  1. ]
point synthétique pour lambda = 0,4 : [74.4  1.6]
```

```python hide-code
print("types des deux fraudes (1 = compte neuf, 2 = prise de contrôle) :", trans.loc[[fraudes.index[0], fraudes.index[voisins[1]]], "type_fraude"].tolist())
print("fraude 1 :", x1.round(1), "| fraude 2 :", x2.round(1))
print("point synthétique pour lambda = 0,4 :", nouveau.round(1))
```
<!--sortie-->
```text
types des deux fraudes (1 = compte neuf, 2 = prise de contrôle) : [1, 1]
fraude 1 : [72.4  2. ] | fraude 2 : [77.4  1. ]
point synthétique pour lambda = 0,4 : [74.4  1.6]
```

La première fraude est une commande de 72,4 € sur un compte vieux de 2 jours ; son plus proche voisin parmi les fraudes, une commande de 77,4 € sur un compte de 1 jour (les deux sont des fraudes du même type, le « compte neuf »). Pour $\lambda=0{,}4$, le point synthétique est $x_1+0{,}4\,(x_2-x_1)$, soit une commande d'environ 74,4 € sur un compte de 1,6 jour : un « cousin » plausible des deux fraudes, situé à 40 % du chemin de la première vers la seconde.

```python hide
sel = np.r_[np.where(ya.values == 1)[0], np.random.default_rng(0).choice(np.where(ya.values == 0)[0], 1500, replace=False)]
Z = pd.DataFrame({"x": np.log1p(Xa.iloc[sel]["montant"].values), "y": np.log1p(Xa.iloc[sel]["age_compte_jours"].values)})
zy = ya.iloc[sel].values
Zs, zys = SMOTE(sampling_strategy=0.5, random_state=0).fit_resample(Z, zy)
n_orig = len(Z)
synth = Zs.iloc[n_orig:]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9), sharex=True, sharey=True)
for a in ax:
    a.scatter(Z["x"][zy == 0], Z["y"][zy == 0], s=6, color=GRIS, alpha=0.4, label="commandes normales")
    a.scatter(Z["x"][zy == 1], Z["y"][zy == 1], s=14, color=ROUGE, label="fraudes réelles")
    a.set_xlabel("log(1 + montant)")
ax[0].set_ylabel("log(1 + ancienneté du compte)")
ax[0].set_title("Avant", fontsize=10)
ax[1].scatter(synth["x"], synth["y"], s=14, color=ORANGE, marker="x", label="exemples synthétiques (SMOTE)")
ax[1].set_title("Après SMOTE : des points sur les segments entre fraudes voisines", fontsize=10)
handles, labels = ax[1].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8)
plt.tight_layout(rect=(0, 0.07, 1, 1))
plt.savefig("figures/ch04-smote.png", dpi=200, bbox_inches="tight")
plt.close()
print("fraudes réelles dans la figure :", int(zy.sum()), "| exemples synthétiques créés :", len(synth))
```
<!--sortie-->
```text
fraudes réelles dans la figure : 340 | exemples synthétiques créés : 410
```

![À gauche : fraudes (rouge) et commandes normales (gris) dans le plan (montant, ancienneté du compte) en échelle logarithmique. À droite : les exemples synthétiques créés par SMOTE (croix orange) s'alignent sur des segments entre fraudes voisines et restent dans la zone des fraudes.](figures/ch04-smote.png)

La figure montre le mécanisme et sa limite. Les croix orange sont **entre** des fraudes voisines : SMOTE remplit les trous de la région des fraudes. Les fraudes forment ici **deux groupes** nets (les comptes très récents, en bas, et les comptes anciens mêlés aux commandes normales, en haut), et comme les $k=5$ voisins d'une fraude sont presque toujours du même groupe, les points synthétiques restent dans chacun : l'espace vide entre les deux groupes n'est pas comblé. Mais l'algorithme **suppose que la région des fraudes est compacte** : que n'importe quel point d'un segment entre deux voisines est une fraude plausible. Si un groupe est petit, si $k$ est grand ou si un segment traverse une zone de commandes normales, les points synthétiques deviennent faux. Remarquez enfin que le groupe du haut est **entièrement mêlé aux commandes normales** : y ajouter des fraudes synthétiques ne facilite pas leur séparation.

### 4.5.2 Les variantes

Plusieurs variantes corrigent des défauts de l'algorithme de base. Elles sont toutes disponibles dans la bibliothèque `imbalanced-learn` (`imblearn`).

| Variante | Idée | Quand l'envisager |
|---|---|---|
| **Borderline-SMOTE** | ne crée des points que **près de la frontière** : à partir des exemples rares dont les voisins sont en majorité de la classe normale | on veut renforcer la zone d'incertitude plutôt que le cœur de la classe |
| **ADASYN** | crée plus de points pour les exemples rares **difficiles** (entourés de voisins normaux), moins pour les faciles | les classes se mélangent fortement |
| **SMOTE-NC** | gère les variables **qualitatives** : la catégorie du point synthétique est la plus fréquente parmi les $k$ voisins | des variables non numériques sont mêlées aux numériques |
| **SMOTEN** | variante pour des variables **toutes** qualitatives | données entièrement catégorielles |

Toutes partagent la même limite : elles **inventent des exemples** à partir d'exemples existants, donc ne créent pas d'information nouvelle sur la classe rare. Elles ne font que **remplir** la région déjà observée.

### 4.5.3 Dans un pipeline, et seulement dans le pli d'entraînement

Comme tout ce qui apprend sur les données, SMOTE ne doit s'appliquer qu'au jeu **d'entraînement**. La bibliothèque `imbalanced-learn` fournit un `Pipeline` qui le garantit : l'étape de rééchantillonnage n'est exécutée **que pendant `fit`**, jamais au moment de prédire ni d'évaluer sur le pli de validation.

```python
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import cross_val_score

pipe = Pipeline([("echelle", StandardScaler()),
                 ("smote", SMOTE(k_neighbors=5, random_state=0)),
                 ("modele", LogisticRegression(max_iter=3000))])
scores = cross_val_score(pipe, Xa, ya, cv=5, scoring="average_precision")
print(f"PR-AUC en validation croisée : {scores.mean():.3f} (± {scores.std():.3f})")
```
<!--sortie-->
```text
PR-AUC en validation croisée : 0.212 (± 0.021)
```

### 4.5.4 Faut-il vraiment rééchantillonner ? Une comparaison honnête

Comparons, en validation croisée à 5 plis sur les 42 000 commandes d'entraînement, les stratégies de 4.3 et de 4.5 pour deux modèles. Chaque nombre est la moyenne sur 5 plis, avec son écart-type d'un pli à l'autre.

```python hide
cv = StratifiedKFold(5, shuffle=True, random_state=0)


def evaluer(nom, modele):
    r = cross_validate(modele, Xa, ya, cv=cv, scoring={"auc": "roc_auc", "ap": "average_precision"})
    return {"modèle et traitement": nom, "AUC-ROC": f"{r['test_auc'].mean():.3f} (± {r['test_auc'].std():.3f})",
            "PR-AUC": f"{r['test_ap'].mean():.3f} (± {r['test_ap'].std():.3f})", "_ap": r["test_ap"].mean()}


lg = lambda **k: LogisticRegression(max_iter=3000, **k)
gb = lambda **k: HistGradientBoostingClassifier(random_state=0, max_iter=100, **k)
lignes = [
    evaluer("logistique, aucun traitement", PipeIB([("sc", StandardScaler()), ("m", lg())])),
    evaluer("logistique, poids équilibrés", PipeIB([("sc", StandardScaler()), ("m", lg(class_weight="balanced"))])),
    evaluer("logistique + sur-échantillonnage aléatoire", PipeIB([("sc", StandardScaler()), ("o", RandomOverSampler(random_state=0)), ("m", lg())])),
    evaluer("logistique + SMOTE", PipeIB([("sc", StandardScaler()), ("o", SMOTE(random_state=0)), ("m", lg())])),
    evaluer("logistique + Borderline-SMOTE", PipeIB([("sc", StandardScaler()), ("o", BorderlineSMOTE(random_state=0)), ("m", lg())])),
    evaluer("logistique + ADASYN", PipeIB([("sc", StandardScaler()), ("o", ADASYN(random_state=0)), ("m", lg())])),
    evaluer("boosting, aucun traitement", PipeIB([("m", gb())])),
    evaluer("boosting, poids équilibrés", PipeIB([("m", gb(class_weight="balanced"))])),
    evaluer("boosting + SMOTE", PipeIB([("o", SMOTE(random_state=0)), ("m", gb())])),
]
tab_smote = pd.DataFrame(lignes).drop(columns="_ap")
print(tab_smote.to_string(index=False))
```
<!--sortie-->
```text
                      modèle et traitement         AUC-ROC          PR-AUC
              logistique, aucun traitement 0.907 (± 0.019) 0.280 (± 0.059)
              logistique, poids équilibrés 0.910 (± 0.018) 0.219 (± 0.041)
logistique + sur-échantillonnage aléatoire 0.911 (± 0.018) 0.218 (± 0.041)
                        logistique + SMOTE 0.908 (± 0.020) 0.214 (± 0.039)
             logistique + Borderline-SMOTE 0.907 (± 0.018) 0.195 (± 0.028)
                       logistique + ADASYN 0.908 (± 0.020) 0.212 (± 0.038)
                boosting, aucun traitement 0.950 (± 0.010) 0.575 (± 0.040)
                boosting, poids équilibrés 0.966 (± 0.013) 0.544 (± 0.072)
                          boosting + SMOTE 0.945 (± 0.011) 0.500 (± 0.033)
```

```python hide-code
print(tab_smote.to_string(index=False))
```
<!--sortie-->
```text
                      modèle et traitement         AUC-ROC          PR-AUC
              logistique, aucun traitement 0.907 (± 0.019) 0.280 (± 0.059)
              logistique, poids équilibrés 0.910 (± 0.018) 0.219 (± 0.041)
logistique + sur-échantillonnage aléatoire 0.911 (± 0.018) 0.218 (± 0.041)
                        logistique + SMOTE 0.908 (± 0.020) 0.214 (± 0.039)
             logistique + Borderline-SMOTE 0.907 (± 0.018) 0.195 (± 0.028)
                       logistique + ADASYN 0.908 (± 0.020) 0.212 (± 0.038)
                boosting, aucun traitement 0.950 (± 0.010) 0.575 (± 0.040)
                boosting, poids équilibrés 0.966 (± 0.013) 0.544 (± 0.072)
                          boosting + SMOTE 0.945 (± 0.011) 0.500 (± 0.033)
```

Trois enseignements se dégagent.

1. **Le boosting domine la régression logistique**, quel que soit le traitement : PR-AUC de 0,50 à 0,58 contre 0,19 à 0,28. Le choix du modèle pèse bien plus que celui du traitement.
2. **Rééchantillonner n'améliore pas la PR-AUC ; elle baisse.** Pour la logistique, de 0,280 (sans traitement) à 0,195–0,219 avec poids, sur-échantillonnage, SMOTE ou ses variantes ; pour le boosting, de 0,575 à 0,544 avec poids et à 0,500 avec SMOTE. Les écarts entre variantes de SMOTE (0,195 à 0,214) sont du même ordre que l'écart-type d'un pli à l'autre (0,03 à 0,04) : **aucune ne se distingue**.
3. L'AUC-ROC, elle, ne dit pas la même chose : elle reste stable (0,907 à 0,911 pour la logistique) ou monte un peu avec les poids (0,950 à 0,966 pour le boosting). Deux métriques de classement, deux verdicts : c'est un rappel que la **PR-AUC**, centrée sur le haut du classement, est la mesure pertinente quand la classe est rare.

#### L'erreur à ne jamais commettre

Que se passe-t-il si l'on rééquilibre **toute la table d'abord**, puis qu'on lance la validation croisée sur le résultat ? C'est une erreur de débutant très fréquente, parce qu'elle semble innocente.

```python hide
Xo, yo = RandomOverSampler(random_state=0).fit_resample(Xa, ya)
r_o = cross_validate(gb(), Xo, yo, cv=cv, scoring={"ap": "average_precision"})
Xsm, ysm = SMOTE(random_state=0).fit_resample(Xa, ya)
r_s = cross_validate(gb(), Xsm, ysm, cv=cv, scoring={"ap": "average_precision"})
print(f"boosting, sur-échantillonnage aléatoire AVANT la validation croisée : PR-AUC {r_o['test_ap'].mean():.3f}")
print(f"boosting, SMOTE AVANT la validation croisée                        : PR-AUC {r_s['test_ap'].mean():.3f}")
```
<!--sortie-->
```text
boosting, sur-échantillonnage aléatoire AVANT la validation croisée : PR-AUC 1.000
boosting, SMOTE AVANT la validation croisée                        : PR-AUC 0.999
```

```python hide-code
print(f"boosting, sur-échantillonnage aléatoire AVANT la validation croisée : PR-AUC {r_o['test_ap'].mean():.3f}")
print(f"boosting, SMOTE AVANT la validation croisée                        : PR-AUC {r_s['test_ap'].mean():.3f}")
```
<!--sortie-->
```text
boosting, sur-échantillonnage aléatoire AVANT la validation croisée : PR-AUC 1.000
boosting, SMOTE AVANT la validation croisée                        : PR-AUC 0.999
```

Les scores s'envolent à **1,000** (sur-échantillonnage aléatoire) et **0,999** (SMOTE) : un modèle presque parfait sur un problème que le même boosting, évalué correctement, ne résout qu'à 0,575 de PR-AUC. Aucune magie : avec le sur-échantillonnage avant la séparation, les **copies d'une même fraude se retrouvent des deux côtés** de la validation ; avec SMOTE, les points synthétiques sont des interpolations entre fraudes voisines, dont une partie se trouve dans le pli de validation. Le modèle est évalué sur des exemples qu'il a, en pratique, déjà vus.

> ⚠️ **Rééchantillonner dans le pipeline, jamais avant.** Le jeu de validation (et le jeu de test) ne doivent contenir **que des exemples réels, dans leur proportion réelle**. C'est la seule façon de savoir comment le modèle se comportera en production, où les fraudes ne seront ni dupliquées ni synthétiques.

### 4.5.5 Que retenir de SMOTE ?

Pour les modèles d'aujourd'hui (boosting, forêts), nos résultats vont dans le même sens que l'expérience de nombreux praticiens : **SMOTE est rarement meilleur que la simple pondération des classes ou que le réglage du seuil**, et il peut dégrader les probabilités et le classement (ici, la PR-AUC du boosting passe de 0,575 à 0,500). Son intérêt est plus net pour des modèles qui apprennent mal avec très peu de positifs (certains réseaux de neurones, des modèles basés sur les distances), ou quand on ne dispose d'**aucun** moyen de pondérer. Avant de l'utiliser :

1. **mesurez** la performance sans rééchantillonnage, avec poids, avec choix de seuil par les coûts (4.3) ;
2. si vous rééchantillonnez, faites-le **dans le pipeline** ;
3. **recalibrez** les probabilités ensuite (section 5.2), car elles sont faussées.

> ✅ **À retenir (SMOTE).** SMOTE crée des exemples rares par interpolation entre voisins ; ses variantes (Borderline, ADASYN, SMOTE-NC) en changent la zone ou le type de variables. Il n'ajoute pas d'information, il est sensible à la forme de la classe rare, et sur des modèles à base d'arbres il fait rarement mieux que les poids ou le seuil. **Dans le pipeline, ou pas du tout.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8 (SMOTE et variantes dans un pipeline, et la fuite par rééchantillonnage) ; exercices 4.13 et 4.14.
