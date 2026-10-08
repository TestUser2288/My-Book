## 3.4 ➕ Pour aller plus loin : AutoML et outils de ML sans code

> 🧭 Section optionnelle. Elle se lit après la section 3.3 et montre ce que ces outils automatisent, comment on en écrit un en quelques lignes, et surtout **comment on lit leur classement**.

Les outils d'**AutoML** (apprentissage automatique « automatique ») et de ML **sans code** promettent de transformer un tableau en modèle en quelques clics : on désigne la colonne à prédire, l'outil essaie des dizaines de modèles et présente un classement. Ils sont utiles, et un analyste en rencontrera. Il faut donc savoir **ce qu'ils font**, **ce qu'ils ne font pas**, et **comment lire** ce qu'ils annoncent.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F
from sklearn.metrics import roc_auc_score
```

### 3.4.1 Ce que ces outils automatisent, et ce qu'ils laissent

| Ils automatisent | Ils laissent à l'analyste |
|---|---|
| le traitement basique des variables (valeurs manquantes, codage des catégories) | **la question** et la définition de la **cible** (section 3.2.6) |
| l'essai de nombreux algorithmes et réglages | la **date de coupure** et la **séparation dans le temps** (section 3.2.8) |
| la validation croisée et le **classement** des essais | la chasse à la **fuite d'information** (section 3.2.11), que peu d'outils détectent |
| parfois des assemblages de modèles, un déploiement (API) | le **coût des erreurs** et l'**effet de l'action** (section 3.2.12) |
| un rapport (importance des variables, courbes) | l'**explication** à la personne qui décide, le **consentement**, la surveillance |

L'outil gagne du **temps de réglage** ; il ne remplace ni la formulation du problème, ni la rigueur d'évaluation. Un outil qui reçoit une cible mal définie ou une variable qui fuit produira, très vite et très bien, un modèle inutilisable. **Aucun produit commercial d'AutoML ou de ML sans code n'est exécuté dans ce livre** ; les noms, les écrans et les paramètres changent d'une version à l'autre, et l'on se reportera à la documentation de l'outil choisi. Ce qui suit se refait avec scikit-learn, pour comprendre le principe.

### 3.4.2 Un mini-AutoML en quelques lignes

Le cœur d'un AutoML tient en trois idées : **un espace de recherche** (des modèles et des réglages), **une validation** qui note chaque essai, **un classement**. Écrivons-le pour le cas B, avec les bonnes pratiques de la section 3.2 : la validation doit être **temporelle**.

On dispose de **huit coupures trimestrielles** (fin 2023 à fin 2025). Les six premières servent à apprendre et à choisir ; la septième (30 juin 2025) est **réservée** au test final, que l'on n'ouvrira qu'une fois. Pour noter un essai sans toucher au test, on rejoue le passé : on apprend sur les trois premières coupures et l'on valide sur la quatrième, puis on apprend sur les quatre premières et l'on valide sur la cinquième, et ainsi de suite (trois plis).

```python
S = O.panel(d)
COUP = O.COUPURES[:6]                         # six coupures pour apprendre ; la septième (juin 2025) reste scellée

def valider(cfg, plis=(3, 4, 5)):
    aucs = []
    for k in plis:                            # on apprend sur les k premières coupures, on valide sur la suivante
        tr, va = pd.concat([S[c] for c in COUP[:k]]), S[COUP[k]]
        m = O.construire(cfg).fit(O.avec_saison(tr), tr["y"].values)
        aucs.append(roc_auc_score(va["y"], m.predict_proba(O.avec_saison(va))[:, 1]))
    return np.mean(aucs), np.std(aucs, ddof=1)

cfgs = O.configurations(60)                   # 60 configurations tirées au sort : logistique, arbre, boosting, forêt
res = pd.DataFrame([{**c, "cv": v[0], "cv_sd": v[1]} for c in cfgs for v in [valider(c)]])
```

Chaque essai est noté par la **moyenne de l'AUC sur les trois plis** et par l'écart-type entre les plis. Voici le début du classement.

```python
print(res.sort_values("cv", ascending=False).head(5)[["id", "famille", "cv", "cv_sd"]].round(4).to_string(index=False))
```
<!--sortie-->
```text
 id  famille     cv  cv_sd
 43    forêt 0.7346 0.0065
 34    forêt 0.7344 0.0065
 60    forêt 0.7344 0.0064
 12 boosting 0.7343 0.0059
 29    forêt 0.7341 0.0063
```

On ouvre alors **une fois** le test scellé pour **toutes** les configurations (ce que l'AutoML ne montre pas : il garde tout pour lui). C'est ce qu'il faut regarder pour juger si le classement est fiable.

```python hide
trall, te_ = pd.concat([S[c] for c in COUP]), S["2025-06-30"]
res["test"] = [roc_auc_score(te_["y"], O.construire(c).fit(O.avec_saison(trall), trall["y"].values).predict_proba(O.avec_saison(te_))[:, 1]) for c in cfgs]
top = res.sort_values("cv", ascending=False)
t8 = top.head(8)
assert round(t8["cv"].max() - t8["cv"].min(), 4) == 0.0007 and round(t8["cv_sd"].mean(), 3) == 0.006
assert int((res["test"] > top.iloc[0]["test"]).sum()) + 1 == 16 and round(res[["cv", "test"]].corr(method="spearman").iloc[0, 1], 2) == 0.87
fb = res.groupby("famille")["test"].max()
assert round(fb.max() - fb.min(), 3) == 0.005
lg_ = res[res["famille"] == "logistique"].sort_values("cv", ascending=False).iloc[0]
assert top.iloc[0]["cv"] - lg_["cv"] < lg_["cv_sd"] and round(lg_["test"], 3) == 0.728
```

```python
print(top.head(5)[["id", "famille", "cv", "test"]].round(4).to_string(index=False))
print(res.groupby("famille")[["cv", "test"]].max().round(4))
```
<!--sortie-->
```text
 id  famille     cv   test
 43    forêt 0.7346 0.7307
 34    forêt 0.7344 0.7295
 60    forêt 0.7344 0.7313
 12 boosting 0.7343 0.7322
 29    forêt 0.7341 0.7301
                cv    test
famille                   
arbre       0.7252  0.7269
boosting    0.7343  0.7322
forêt       0.7346  0.7313
logistique  0.7313  0.7279
```

### 3.4.3 Le piège du classement

Deux phénomènes se lisent dans ces sorties. Ils sont la raison pour laquelle on ne se fie pas au classement d'un outil.

**1. Les premiers sont à égalité.** Les huit meilleurs essais ont des scores de validation qui tiennent dans 0,0007 d'AUC, alors que l'écart-type **entre plis** d'un même essai est d'environ 0,006 : les écarts entre eux sont près de **dix fois plus petits** que le bruit. Leur ordre n'est pas une information : le premier de la validation arrive **seizième sur soixante** au test, et le meilleur du test n'était que quatrième à la validation. La validation sait **séparer les bons des mauvais** (l'ordre des soixante essais se ressemble d'une évaluation à l'autre, avec une corrélation des rangs de 0,87), mais pas **les bons entre eux**. Les meilleurs de chaque famille (régression, arbre, boosting, forêt) sont, au test, à 0,005 d'AUC les uns des autres. La **famille** compte peu, le **réglage** compte peu : ce qui comptait, c'étaient les variables (section 3.3.2).

**2. Plus on essaie, plus le gagnant est flatté.** Même sans que rien ne diffère vraiment, le meilleur de cent essais est celui qui a eu **le plus de chance** sur le jeu de validation, et son score y est donc trop beau. Pour mesurer cet effet, créons 200 régressions logistiques qui ne diffèrent que par le sous-ensemble de variables et la régularisation, et suivons, sur 600 tirages aléatoires d'un petit jeu de validation, l'écart entre le **score du gagnant sur la validation** et son score **sur tous les autres clients**.

```python
P, y_te = O.variantes_logistiques(S)                      # 200 variantes, scores sur la coupure de test
opt = O.optimisme(P, y_te)                                # écart « gagnant sur la validation − gagnant sur le reste », selon n et la taille
print(opt.pivot(index="candidats", columns="validation", values="écart").mul(100).round(2).rename(columns=lambda c: f"{c} clients"))
```
<!--sortie-->
```text
validation  500 clients  4000 clients
candidats                            
1                 -0.01         -0.08
5                  0.56          0.01
20                 0.66          0.01
60                 1.03          0.11
200                1.17          0.21
```

```python hide
F.fig_classement(res, opt)
```
<!--sortie-->
```text
figure : ch03-classement.png
```

![À gauche, les huit premiers essais du mini-AutoML : leurs scores de validation sont à égalité (la barre est l'écart-type entre plis) et ne reproduisent pas leur ordre au test. À droite, l'écart entre le score du gagnant sur la validation et sur le reste : il augmente avec le nombre d'essais et diminue avec la taille de la validation.](figures/ch03-classement.png)

Avec une validation de **500 clients**, le gagnant parmi 200 essais est flatté d'environ **1,2 point d'AUC**, soit plus de deux fois l'écart entre les meilleures familles de modèles (0,5 point) ; avec 4 000 clients, il n'est que de 0,2 point. C'est l'effet de **malédiction du gagnant** : on sélectionne ce qui a eu de la chance, puis on la prend pour un talent. Il se combat de trois façons.

- **Mettre un test de côté, et ne l'ouvrir qu'une fois**, comme ici (la septième coupure). Chaque fois qu'on le consulte pour choisir, il devient un deuxième jeu de validation.
- **Valider sur beaucoup de données**, de préférence plusieurs périodes (ici, trois plis temporels) ; la validation d'un petit échantillon est fragile.
- **Choisir le modèle le plus simple parmi ceux qui sont à moins d'un écart-type du meilleur** (la « règle de l'écart-type »). Ici, la régression logistique est à moins d'un écart-type du meilleur (0,003 d'AUC d'écart pour un écart-type de 0,008) : on la choisit ; elle perd 0,003 d'AUC au test, mais elle s'explique, se maintient et se surveille.

> ⚠️ **Piège.** Un classement qui montre « meilleur modèle : 0,7346 » à quatre décimales donne une **illusion de précision**. Sans l'écart-type entre plis ou un intervalle, on ne sait pas si l'écart avec le suivant est de 0,0001 ou de 0,01. Si l'outil ne les montre pas, calculez-les ; s'il ne permet pas de les calculer, méfiez-vous de ses classements.

### 3.4.4 Évaluer un outil sans code

Un outil sans code est souvent le bon choix : il évite d'écrire du code que personne ne maintiendra, et il rend des modèles raisonnables. On l'évalue avec les mêmes questions que celles du dossier de passation, adaptées à l'outil.

1. **Comment sépare-t-il les données ?** Au hasard (risque d'optimisme dès que le temps compte) ou dans le temps ? Peut-on **fixer** la date de coupure ?
2. **Peut-on exclure des variables** ? Signale-t-il les variables suspectes (une variable qui « prédit » presque parfaitement est une fuite probable) ?
3. **Quelle métrique optimise-t-il ?** Celle de la décision (gain en euros, rappel à 20 %) ou une métrique générique ?
4. **Les probabilités sont-elles calibrées ?** Sinon, on ne peut pas les utiliser dans un calcul de coût.
5. **Que montre-t-il de l'incertitude ?** Écart-type entre plis, intervalle, ou rien.
6. **Peut-on reproduire le résultat** (graine, versions, export du modèle) ? Un résultat qui change à chaque exécution ne se documente pas.
7. **Où partent les données ?** Un outil hébergé reçoit les données de l'entreprise : confidentialité, consentement des personnes, localisation des données.
8. **Comment surveille-t-il le modèle une fois en service ?**

> ✅ **À retenir de la section 3.4.** Un AutoML automatise **le réglage**, pas la formulation du problème ni la rigueur d'évaluation. Son classement est **bruité** : les meilleurs sont souvent à égalité, et **plus on essaie, plus le gagnant est flatté**. On garde un **test scellé**, on valide **dans le temps** sur beaucoup de données, et l'on choisit **le plus simple parmi les meilleurs**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercices 3.11 et 3.12.
