## 4.4 ➕ Pour aller plus loin : les méthodes de sélection de variables

> 🧭 **Section optionnelle.** Elle approfondit la sélection de variables vue en 4.2 : les trois grandes familles de méthodes, et surtout le piège qui rend la plupart des sélections trop optimistes. On peut la sauter à la première lecture.

Quand un jeu de données compte des dizaines ou des milliers de variables, on veut en garder **un sous-ensemble utile** : pour des modèles plus rapides, plus lisibles, moins sujets au surapprentissage. Les méthodes se classent selon **le moment** où elles interviennent par rapport au modèle.

### 4.4.1 Trois familles de méthodes

**Les méthodes de filtre** jugent chaque variable **avant** le modèle, par une statistique indépendante de lui. Elles sont rapides et simples, mais regardent les variables **une par une**, donc ignorent les interactions.

**Les méthodes d'enveloppe** (*wrapper*) **essaient** des sous-ensembles en entraînant le modèle et en mesurant sa performance. Elles tiennent compte des interactions et du modèle choisi, mais coûtent cher : chaque essai est un apprentissage complet.

**Les méthodes intégrées** (*embedded*) sélectionnent **pendant** l'apprentissage : une pénalité $\ell_1$ qui met des coefficients à zéro, ou les importances qu'un arbre calcule en se construisant. Elles sont le meilleur compromis coût-qualité, avec leurs propres biais.

### 4.4.2 Les filtres : information mutuelle et $\chi^2$

Le filtre le plus général est l'**information mutuelle**. Pour une variable $X$ et la cible $Y$, elle mesure combien connaître $X$ réduit l'incertitude sur $Y$ :

$$I(X;Y)=\sum_{x,y}p(x,y)\ln\frac{p(x,y)}{p(x)\,p(y)}.$$

Elle vaut zéro si et seulement si $X$ et $Y$ sont **indépendantes**, et elle capte toute dépendance, pas seulement linéaire. Contrairement à une corrélation, elle voit une relation en U ou à seuil. Pour deux variables **qualitatives**, le test du $\chi^2$ d'indépendance (volume I, section 3.4.6) joue un rôle analogue : on garde les variables dont le lien avec la cible est le plus significatif.

Un exemple à la main, avec deux variables binaires et 100 clients dont 20 partent. Si 50 clients ont reçu une promotion et que 10 d'entre eux partent (autant que dans l'autre moitié), la promotion n'apporte aucune information sur le départ : $I=0$. Si au contraire 18 des 20 partants viennent du groupe « sans promotion », alors savoir qu'un client a eu la promotion change beaucoup la probabilité qu'il parte : $I>0$.

### 4.4.3 Les enveloppes : RFE et sélection progressive

La **suppression récursive de variables** (*recursive feature elimination*, RFE) entraîne le modèle avec toutes les variables, élimine la moins importante (par exemple celle au plus petit coefficient en valeur absolue), et recommence jusqu'à ce qu'il reste le nombre voulu. La **sélection progressive** (*forward selection*) fait l'inverse : on part de zéro variable et on ajoute à chaque étape celle qui améliore le plus le score en validation croisée.

Pour $p$ variables, la sélection progressive jusqu'à $k$ variables nécessite environ $p+(p-1)+\dots$ essais, c'est-à-dire de l'ordre de $kp$ validations croisées : raisonnable pour 14 variables, prohibitif pour 5 000.

### 4.4.4 Les méthodes intégrées : $\ell_1$, importances d'arbre, permutation

La **pénalité $\ell_1$** (Lasso, volume II, section 1.5) met à zéro les coefficients des variables peu utiles : la sélection est un effet secondaire de l'apprentissage. Elle suppose des variables **standardisées** (4.1.3).

L'**importance par impureté** d'une forêt ou d'un arbre additionne, pour chaque variable, la réduction d'impureté obtenue à tous les nœuds où elle est utilisée. Elle est gratuite, mais **biaisée** : une variable continue ou à beaucoup de modalités offre plus de seuils possibles, donc plus d'occasions de réduire l'impureté **par hasard**, même si elle est du pur bruit.

L'**importance par permutation** corrige ce défaut. On entraîne le modèle, puis on mesure la baisse de performance sur un jeu de **validation** quand on **mélange au hasard** les valeurs d'une seule variable (ce qui détruit son lien avec la cible en préservant sa distribution). Plus la baisse est grande, plus la variable compte ; une variable de bruit entraîne une baisse nulle.

#### Que choisissent-elles sur nos clients ?

Nous ajoutons aux 14 variables numériques **cinq variables de bruit pur** (tirées au hasard, sans lien avec la cible : trois continues et deux discrètes), et nous comparons les méthodes. Toutes les sélections sont calculées sur le jeu d'entraînement ; l'importance par permutation utilise une partie de l'entraînement mise de côté comme validation.

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_classif, RFE, SequentialFeatureSelector
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline, Pipeline

rng = np.random.default_rng(5)
Xs = clients[NUM].copy()
for k in range(3):
    Xs[f"bruit_continu_{k + 1}"] = rng.normal(size=len(Xs))
for k in range(2):
    Xs[f"bruit_discret_{k + 1}"] = rng.integers(0, 12, len(Xs))
imp = SimpleImputer(strategy="median")
A = pd.DataFrame(imp.fit_transform(Xs.loc[tr]), columns=Xs.columns, index=tr)
B = pd.DataFrame(imp.transform(Xs.loc[te]), columns=Xs.columns, index=te)
sc = StandardScaler().fit(A)
As, Bs = pd.DataFrame(sc.transform(A), columns=A.columns, index=tr), pd.DataFrame(sc.transform(B), columns=B.columns, index=te)
bruits = [c for c in Xs.columns if c.startswith("bruit")]
K = 8

# 1. filtre : information mutuelle
mi = pd.Series(mutual_info_classif(A, ytr, random_state=0), index=A.columns).sort_values(ascending=False)
sel_mi = list(mi.index[:K])
# 2. enveloppe : RFE avec régression logistique
rfe = RFE(LogisticRegression(max_iter=3000), n_features_to_select=K).fit(As, ytr)
sel_rfe = list(As.columns[rfe.support_])
# 2 bis. sélection progressive (validation croisée à 3 plis)
sfs = SequentialFeatureSelector(LogisticRegression(max_iter=3000), n_features_to_select=K, direction="forward", cv=3, scoring="roc_auc").fit(As, ytr)
sel_sfs = list(As.columns[sfs.get_support()])
# 3. intégrée : pénalité L1
l1 = LogisticRegression(penalty="l1", solver="liblinear", C=0.05, max_iter=5000).fit(As, ytr)
coef_l1 = pd.Series(l1.coef_[0], index=As.columns)
sel_l1 = list(coef_l1[coef_l1 != 0].index)
# 3 bis. importance par impureté d'une forêt, puis par permutation (sur un jeu de validation mis de côté)
a_in, a_val, y_in, y_val = train_test_split(A, ytr, test_size=0.3, random_state=0, stratify=ytr)
rf = RandomForestClassifier(n_estimators=150, min_samples_leaf=5, random_state=0, n_jobs=1).fit(a_in, y_in)
imp_imp = pd.Series(rf.feature_importances_, index=A.columns)
perm = permutation_importance(rf, a_val, y_val, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1)
imp_perm = pd.Series(perm.importances_mean, index=A.columns)
sel_perm = list(imp_perm.sort_values(ascending=False).index[:K])

print("variables de bruit retenues parmi les", K, "choisies :")
for nom, sel in [("information mutuelle", sel_mi), ("RFE (logistique)", sel_rfe), ("sélection progressive", sel_sfs),
                 ("pénalité L1 (toutes les non nulles)", sel_l1), ("importance par permutation", sel_perm)]:
    print(f"  {nom:36s} {len(sel):2d} variables, dont bruit : {[v for v in sel if v in bruits]}")
print("importance par impureté, variables de bruit :", imp_imp[bruits].round(4).to_dict())
print("importance par impureté, médiane des 14 vraies variables :", round(float(imp_imp[NUM].median()), 4))
print("importance par permutation, variables de bruit :", imp_perm[bruits].round(4).to_dict())
print("importance par permutation, recence_jours :", round(float(imp_perm["recence_jours"]), 4))
```
<!--sortie-->
```text
variables de bruit retenues parmi les 8 choisies :
  information mutuelle                  8 variables, dont bruit : []
  RFE (logistique)                      8 variables, dont bruit : []
  sélection progressive                 8 variables, dont bruit : []
  pénalité L1 (toutes les non nulles)  14 variables, dont bruit : ['bruit_continu_1', 'bruit_continu_2', 'bruit_discret_1']
  importance par permutation            8 variables, dont bruit : ['bruit_continu_3']
importance par impureté, variables de bruit : {'bruit_continu_1': 0.038, 'bruit_continu_2': 0.0382, 'bruit_continu_3': 0.0359, 'bruit_discret_1': 0.021, 'bruit_discret_2': 0.0241}
importance par impureté, médiane des 14 vraies variables : 0.0435
importance par permutation, variables de bruit : {'bruit_continu_1': 0.0003, 'bruit_continu_2': -0.0008, 'bruit_continu_3': 0.001, 'bruit_discret_1': -0.0002, 'bruit_discret_2': -0.0}
importance par permutation, recence_jours : 0.0459
```

```python hide
def auc_sous_ensemble(cols):
    m = LogisticRegression(max_iter=3000).fit(As[cols], ytr)
    return roc_auc_score(yte, m.predict_proba(Bs[cols])[:, 1])


lignes = [("toutes les variables (14 vraies + 5 de bruit)", list(As.columns)), ("information mutuelle", sel_mi), ("RFE", sel_rfe),
          ("sélection progressive", sel_sfs), ("pénalité L1", sel_l1), ("permutation (forêt)", sel_perm)]
tab_sel = pd.DataFrame({"méthode": [l[0] for l in lignes], "variables retenues": [len(l[1]) for l in lignes],
                        "dont bruit": [sum(v in bruits for v in l[1]) for l in lignes],
                        "AUC test (logistique)": [auc_sous_ensemble(l[1]) for l in lignes]}).round(3)
print(tab_sel.to_string(index=False))
```
<!--sortie-->
```text
                                      méthode  variables retenues  dont bruit  AUC test (logistique)
toutes les variables (14 vraies + 5 de bruit)                  19           5                  0.857
                         information mutuelle                   8           0                  0.855
                                          RFE                   8           0                  0.857
                        sélection progressive                   8           0                  0.858
                                  pénalité L1                  14           3                  0.858
                          permutation (forêt)                   8           1                  0.858
```

```python hide-code
print(tab_sel.to_string(index=False))
print()
print("importance par impureté (forêt), variables de bruit :", imp_imp[bruits].round(4).to_dict())
print("importance par impureté, médiane des 14 vraies variables :", round(float(imp_imp[NUM].median()), 4))
print("importance par permutation, variables de bruit :", imp_perm[bruits].round(4).to_dict())
```
<!--sortie-->
```text
                                      méthode  variables retenues  dont bruit  AUC test (logistique)
toutes les variables (14 vraies + 5 de bruit)                  19           5                  0.857
                         information mutuelle                   8           0                  0.855
                                          RFE                   8           0                  0.857
                        sélection progressive                   8           0                  0.858
                                  pénalité L1                  14           3                  0.858
                          permutation (forêt)                   8           1                  0.858

importance par impureté (forêt), variables de bruit : {'bruit_continu_1': 0.038, 'bruit_continu_2': 0.0382, 'bruit_continu_3': 0.0359, 'bruit_discret_1': 0.021, 'bruit_discret_2': 0.0241}
importance par impureté, médiane des 14 vraies variables : 0.0435
importance par permutation, variables de bruit : {'bruit_continu_1': 0.0003, 'bruit_continu_2': -0.0008, 'bruit_continu_3': 0.001, 'bruit_discret_1': -0.0002, 'bruit_discret_2': -0.0}
```

Trois méthodes (information mutuelle, RFE, sélection progressive) retiennent chacune 8 variables parmi 19 et **aucune des cinq variables de bruit**. La pénalité $\ell_1$ (avec $C=0{,}05$) en garde 14, dont **trois variables de bruit** : à ce niveau de pénalité, elle laisse de petits coefficients non nuls ; son résultat dépend du paramètre $C$, à régler par validation croisée (chapitre 1, 1.5). La sélection par permutation d'une forêt laisse passer une variable de bruit (`bruit_continu_3`) dans ses huit premières.

Côté performance, **aucune sélection n'améliore l'AUC** : de 0,855 à 0,858 pour tous les sous-ensembles, contre 0,857 avec les 19 variables. Ici la sélection ne sert donc pas la performance mais la **simplicité** : un modèle à huit variables est aussi bon qu'un modèle à dix-neuf, et plus facile à expliquer et à maintenir.

Le contraste est plus net sur les **importances**. Dans la forêt, les trois variables de bruit **continues** obtiennent une importance par impureté de 0,036 à 0,038, presque celle de la variable réelle médiane (0,0435) ; l'importance par permutation les ramène à 0,000 ± 0,001, alors qu'elle donne 0,046 à la récence.

> ⚠️ **L'importance par impureté peut récompenser du bruit.** Les trois variables de bruit **continues** obtiennent une importance par impureté de 0,036 à 0,038, parce qu'elles offrent de nombreux seuils à tester (et les deux variables de bruit discrètes, à douze modalités, de 0,021 à 0,024) ; l'importance par permutation, mesurée sur un jeu de validation, les ramène près de zéro. Pour décider quelles variables garder, préférez la permutation (section 5.3).

### 4.4.5 Le piège : sélectionner avant de valider

Voici l'erreur la plus répandue de toute la sélection de variables. On dispose de beaucoup de variables et de peu de clients ; on commence par **choisir les variables les plus liées à la cible sur tout le jeu de données**, puis on **évalue** le modèle sur ces variables par validation croisée. Le résultat semble excellent. Il est faux.

Pour le voir, prenons le cas extrême : 150 clients, 500 variables **entièrement aléatoires**, et une cible **tirée à pile ou face**, donc sans aucun lien avec les variables. Aucun modèle ne peut faire mieux que le hasard (AUC de 0,5). On répète l'expérience de deux manières, sur 40 jeux de données différents.

- **Sélection avant la validation croisée (fautive)** : on garde les 20 variables les mieux classées sur les 150 clients, puis on valide par validation croisée sur ces 20 colonnes.
- **Sélection dans la validation croisée (correcte)** : la sélection fait partie du `Pipeline`, donc elle est refaite à chaque pli sur les plis d'entraînement seulement.

```python hide
from sklearn.feature_selection import SelectKBest, f_classif

fautif, correct = [], []
cv = StratifiedKFold(5, shuffle=True, random_state=0)
for graine in range(40):
    rg = np.random.default_rng(100 + graine)
    Xb = rg.normal(size=(150, 500))
    yb_ = rg.integers(0, 2, 150)
    Xsel = SelectKBest(f_classif, k=20).fit_transform(Xb, yb_)                     # sélection sur TOUTES les lignes
    fautif.append(cross_val_score(LogisticRegression(max_iter=2000), Xsel, yb_, cv=cv, scoring="roc_auc").mean())
    pipe = Pipeline([("sel", SelectKBest(f_classif, k=20)), ("lr", LogisticRegression(max_iter=2000))])
    correct.append(cross_val_score(pipe, Xb, yb_, cv=cv, scoring="roc_auc").mean())
fautif, correct = np.array(fautif), np.array(correct)
print(f"sélection AVANT la validation croisée : AUC moyenne {fautif.mean():.3f} (min {fautif.min():.3f}, max {fautif.max():.3f})")
print(f"sélection DANS la validation croisée  : AUC moyenne {correct.mean():.3f} (min {correct.min():.3f}, max {correct.max():.3f})")

fig, ax = plt.subplots(figsize=(6.0, 3.6))
ax.hist(fautif, bins=14, color=ROUGE, alpha=0.85, label="sélection avant la validation (fautive)")
ax.hist(correct, bins=14, color=BLEU, alpha=0.85, label="sélection dans la validation (correcte)")
ax.axvline(0.5, color="#0b0b0b", lw=1, ls=":")
ax.set_xlabel("AUC en validation croisée")
ax.set_ylabel("nombre de jeux simulés (sur 40)")
ax.set_title("Cible aléatoire : aucun modèle ne devrait dépasser 0,5", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch04-biais-selection.png", dpi=200, bbox_inches="tight")
plt.close()
```
<!--sortie-->
```text
sélection AVANT la validation croisée : AUC moyenne 0.831 (min 0.762, max 0.909)
sélection DANS la validation croisée  : AUC moyenne 0.510 (min 0.351, max 0.663)
```

```python hide-code
print(f"sélection AVANT la validation croisée : AUC moyenne {fautif.mean():.3f} (min {fautif.min():.3f}, max {fautif.max():.3f})")
print(f"sélection DANS la validation croisée  : AUC moyenne {correct.mean():.3f} (min {correct.min():.3f}, max {correct.max():.3f})")
```
<!--sortie-->
```text
sélection AVANT la validation croisée : AUC moyenne 0.831 (min 0.762, max 0.909)
sélection DANS la validation croisée  : AUC moyenne 0.510 (min 0.351, max 0.663)
```

![Distribution de l'AUC en validation croisée sur 40 jeux simulés où la cible est du pur hasard : la sélection de variables faite avant la validation donne une AUC trompeusement élevée, celle faite dans la validation reste autour de 0,5.](figures/ch04-biais-selection.png)

Le contraste est total. En sélectionnant d'abord, **tous** les jeux simulés donnent une AUC bien supérieure à 0,5 (de 0,76 à 0,91, moyenne 0,83) pour des données sans aucune information ; en sélectionnant à l'intérieur de la validation, on retrouve honnêtement le hasard (moyenne 0,51, de 0,35 à 0,66 selon les jeux, ce qui rappelle aussi qu'une seule AUC sur 150 clients est très bruitée). Pourquoi ? Parmi 500 variables aléatoires, on en trouve toujours 20 qui, **par chance**, ressemblent à la cible sur ces 150 clients ; la sélection les a choisies *en regardant les étiquettes de tous les clients, y compris ceux des plis de validation*. Le pli de validation n'est plus vierge : l'information sur ses étiquettes a servi à choisir les colonnes.

> ⚠️ **Règle absolue.** Toute opération qui **regarde la cible** (sélection de variables, choix de seuils, encodage par la cible, réglage) doit être **dans** le pipeline validé, refaite pli par pli. Et une fois le modèle final choisi, le jeu de test ne doit servir qu'**une** fois, à la fin.

> ✅ **À retenir (sélection).** Filtre : rapide, aveugle aux interactions. Enveloppe : fidèle au modèle, mais coûteuse. Intégrée : bon compromis. Préférez l'**importance par permutation** à l'importance par impureté. Et mettez la sélection **dans le pipeline** : sinon la validation croisée est faussée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (comparer filtre, enveloppe et méthodes intégrées, et refaire le piège de la sélection) ; exercices 4.12.
