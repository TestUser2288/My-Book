## 4.3 Classes déséquilibrées : pondération et rééchantillonnage

Une commande frauduleuse sur 120, un client qui part sur sept, une panne de machine sur mille : les événements qui nous intéressent le plus sont presque toujours **rares**. Les modèles, eux, sont construits pour minimiser une erreur **moyenne** sur les données : quand 99 % des lignes appartiennent à une classe, ils apprennent surtout à bien traiter celle-là. Cette section explique pourquoi la métrique habituelle (l'exactitude) devient trompeuse, ce que font réellement les remèdes (poids, rééchantillonnage), et pourquoi le **seuil de décision** est souvent le levier le plus puissant et le plus négligé.

### 4.3.1 Pourquoi l'exactitude trompe

Notre fichier `transactions.csv` contient 60 000 commandes en ligne, dont 0,8 % de fraudes. Après le découpage habituel (70 % pour l'entraînement, 30 % pour le test, stratifié), le jeu de test compte 18 000 commandes dont 146 frauduleuses.

Considérons le **modèle le plus paresseux possible** : il répond « pas de fraude » pour toutes les commandes. Il se trompe sur les 146 fraudes et n'a raison que sur les autres, soit une **exactitude** (part de réponses justes) de $\frac{17\,854}{18\,000}\approx99{,}19\ \%$. Un score qui paraît excellent, pour un modèle qui ne détecte **aucune** fraude.

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_predict, StratifiedKFold
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_score, recall_score, f1_score,
                             confusion_matrix, precision_recall_curve)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

trans = pd.read_csv("donnees/transactions.csv")
Xt = pd.get_dummies(trans.drop(columns=["id_commande", "fraude", "type_fraude"]), dtype=float)
yt = trans["fraude"]
Xa, Xb, ya, yb = train_test_split(Xt, yt, test_size=0.3, random_state=0, stratify=yt)
print("test :", len(yb), "commandes dont", int(yb.sum()), "fraudes (", round(yb.mean() * 100, 2), "%)")
print("modèle paresseux (toujours « pas de fraude ») : exactitude", round((yb == 0).mean(), 4), "| fraudes détectées : 0 sur", int(yb.sum()))
```
<!--sortie-->
```text
test : 18000 commandes dont 146 fraudes ( 0.81 %)
modèle paresseux (toujours « pas de fraude ») : exactitude 0.9919 | fraudes détectées : 0 sur 146
```

La table de confusion rend l'illusion visible. Elle croise la réalité (en lignes) et la décision du modèle (en colonnes) :

| | décision « pas de fraude » | décision « fraude » |
|---|---|---|
| **réellement pas de fraude** | vrais négatifs (VN) : 17 854 | faux positifs (FP) : 0 |
| **réellement fraude** | **faux négatifs (FN) : 146** | vrais positifs (VP) : 0 |

Deux mesures décrivent mieux ce qui compte quand la classe rare est celle qui nous intéresse (elles sont détaillées en 5.1).

$$\text{précision}=\frac{\text{VP}}{\text{VP}+\text{FP}}\quad(\text{parmi les alertes, quelle part est juste ?}),\qquad \text{rappel}=\frac{\text{VP}}{\text{VP}+\text{FN}}\quad(\text{parmi les fraudes, quelle part est détectée ?}).$$

Le modèle paresseux a un rappel de **0 %** ; l'exactitude de 99,19 % n'en dit rien. D'où une règle absolue : **avec des classes déséquilibrées, ne jamais juger sur l'exactitude.**

#### Même l'AUC peut rassurer à tort

Entraînons une régression logistique sur ces données et mesurons deux scores de classement. L'**AUC-ROC** (volume II, section 2.2) compare les taux de vrais et de faux positifs à tous les seuils. La **précision moyenne** (PR-AUC, aire sous la courbe précision-rappel) mesure plutôt la qualité du haut du classement, là où se trouvent les alertes.

```python hide
sc_a = StandardScaler().fit(Xa)
logit = LogisticRegression(max_iter=3000).fit(sc_a.transform(Xa), ya)
p_logit = logit.predict_proba(sc_a.transform(Xb))[:, 1]
pred = (p_logit >= 0.5).astype(int)
tn, fp, fn, tp = confusion_matrix(yb, pred).ravel()
print("régression logistique : AUC-ROC", round(roc_auc_score(yb, p_logit), 3), "| PR-AUC", round(average_precision_score(yb, p_logit), 3))
print(f"à 0,5 : précision {precision_score(yb, pred):.3f}, rappel {recall_score(yb, pred):.3f} (VP {tp}, FP {fp}, FN {fn})")
print("référence PR-AUC d'un classement au hasard :", round(yb.mean(), 4))
```
<!--sortie-->
```text
régression logistique : AUC-ROC 0.921 | PR-AUC 0.26
à 0,5 : précision 0.625, rappel 0.103 (VP 15, FP 9, FN 131)
référence PR-AUC d'un classement au hasard : 0.0081
```

L'AUC-ROC vaut 0,921 : le modèle classe très bien. Mais la PR-AUC n'est que de 0,260 (un classement au hasard donnerait 0,008), et à un seuil de 0,5 la régression logistique ne détecte que **10 % des fraudes** (rappel 0,103) : sur 146 fraudes, elle en trouve 15 et en laisse passer 131. L'AUC-ROC est **optimiste** quand la classe positive est rare : les 17 854 négatifs comptent tant dans les taux de faux positifs qu'une petite erreur sur eux paraît négligeable. La PR-AUC, qui ignore les vrais négatifs, est plus sévère et plus informative.

> ✅ **À retenir.** Exactitude : à proscrire. AUC-ROC : informative mais indulgente. **PR-AUC, précision et rappel** : les bons outils quand la classe rare est l'objet. (Détail et autres métriques : section 5.1.)

### 4.3.2 La pondération des classes

La première idée est de **dire au modèle que la classe rare compte davantage**. La perte d'une régression logistique est la perte logarithmique moyenne (volume II, section 2.2) :

$$L(\boldsymbol\beta)=-\frac1n\sum_{i=1}^n\Bigl[y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr].$$

On la **pondère** : une erreur sur un exemple de la classe 1 coûte $w$ fois plus qu'une erreur sur un exemple de la classe 0.

$$L_w(\boldsymbol\beta)=-\frac1n\sum_{i=1}^n\Bigl[w\,y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr].$$

C'est équivalent à **recopier $w$ fois** chaque exemple positif. L'option `class_weight="balanced"` choisit $w$ pour que les deux classes pèsent autant au total, c'est-à-dire $w=\frac{n_0}{n_1}$ (ici $w\approx122{,}5$). Dans scikit-learn, c'est un simple paramètre du modèle :

```python
from sklearn.linear_model import LogisticRegression

modele_pondere = LogisticRegression(class_weight="balanced", max_iter=3000)      # w = n0 / n1 pour la classe rare
# on peut aussi donner les poids à la main : class_weight={0: 1, 1: 20}
```

#### Ce que cela change exactement

Considérons le cas le plus simple, sans aucune variable explicative : une probabilité constante $p$ pour tous. Si la proportion de positifs est $\pi$, la perte pondérée moyenne vaut $-[\,w\pi\ln p+(1-\pi)\ln(1-p)\,]$. En la dérivant par rapport à $p$ et en annulant la dérivée,

$$\frac{w\pi}{p}-\frac{1-\pi}{1-p}=0\quad\Longrightarrow\quad\frac{p^\star}{1-p^\star}=w\,\frac{\pi}{1-\pi}.$$

La probabilité estimée a donc une **cote multipliée par $w$** : la pondération n'a pas rendu le modèle « plus malin », elle a **déplacé ses probabilités vers le haut**. Pour une régression logistique à plusieurs variables bien spécifiée, le même raisonnement dit que seul le terme constant change, de $\ln w$, et que les autres coefficients (donc le **classement** des clients) ne bougent pas. Vérifions.

```python hide
logit_w = LogisticRegression(max_iter=3000, class_weight="balanced").fit(sc_a.transform(Xa), ya)
p_w = logit_w.predict_proba(sc_a.transform(Xb))[:, 1]
pred_w = (p_w >= 0.5).astype(int)
tn, fp, fn, tp = confusion_matrix(yb, pred_w).ravel()
w = (len(ya) - ya.sum()) / ya.sum()
decalage = float(logit_w.intercept_[0] - logit.intercept_[0])
print("poids w = n0/n1 =", round(w, 1), "| ln w =", round(np.log(w), 3), "| décalage observé de la constante :", round(decalage, 3))
print("probabilité moyenne prédite : sans poids", round(p_logit.mean(), 4), "| avec poids", round(p_w.mean(), 4), "| fréquence réelle", round(yb.mean(), 4))
print("AUC-ROC sans / avec poids :", round(roc_auc_score(yb, p_logit), 3), "/", round(roc_auc_score(yb, p_w), 3))
print(f"à 0,5 avec poids : précision {precision_score(yb, pred_w):.3f}, rappel {recall_score(yb, pred_w):.3f} (FP {fp}, FN {fn})")
# probabilités corrigées : on redivise la cote par w
p_corrigee = p_w / (p_w + (1 - p_w) * w)
print("probabilité moyenne après correction :", round(p_corrigee.mean(), 4))
print("corrélation de rang entre les deux scores :", round(pd.Series(p_logit).corr(pd.Series(p_w), method="spearman"), 4))
```
<!--sortie-->
```text
poids w = n0/n1 = 122.5 | ln w = 4.808 | décalage observé de la constante : 4.675
probabilité moyenne prédite : sans poids 0.008 | avec poids 0.2365 | fréquence réelle 0.0081
AUC-ROC sans / avec poids : 0.921 / 0.923
à 0,5 avec poids : précision 0.049, rappel 0.863 (FP 2432, FN 20)
probabilité moyenne après correction : 0.0098
corrélation de rang entre les deux scores : 0.9854
```

```python hide-code
print("poids w = n0/n1 =", round(w, 1), "| ln w =", round(np.log(w), 3), "| décalage observé de la constante :", round(decalage, 3))
print("probabilité moyenne prédite : sans poids", round(p_logit.mean(), 4), "| avec poids", round(p_w.mean(), 4), "| fréquence réelle", round(yb.mean(), 4))
print(f"à 0,5 avec poids : précision {precision_score(yb, pred_w):.3f}, rappel {recall_score(yb, pred_w):.3f} (FP {fp}, FN {fn})")
print("probabilité moyenne après correction :", round(p_corrigee.mean(), 4))
```
<!--sortie-->
```text
poids w = n0/n1 = 122.5 | ln w = 4.808 | décalage observé de la constante : 4.675
probabilité moyenne prédite : sans poids 0.008 | avec poids 0.2365 | fréquence réelle 0.0081
à 0,5 avec poids : précision 0.049, rappel 0.863 (FP 2432, FN 20)
probabilité moyenne après correction : 0.0098
```

Les constats confirment la théorie. Le poids vaut $w\approx122$, soit $\ln w\approx4{,}81$ ; la constante du modèle a bougé de $4{,}68$, très près de la valeur prévue. Les probabilités moyennes passent de 0,8 % (la vraie fréquence) à **23,7 %** : elles sont **fausses**, gonflées, comme le prédit le calcul. Si on les corrige en divisant la cote par $w$ ($p=\frac{p_w}{p_w+(1-p_w)\,w}$), la moyenne retombe à 1,0 %, bien plus près de la fréquence réelle (0,8 %) ; l'écart restant vient du fait que le modèle n'est pas parfaitement spécifié. L'AUC-ROC reste pratiquement celle du modèle sans poids (0,921 contre 0,923) et la corrélation de rang entre les deux scores vaut 0,985 : **le classement n'a presque pas changé**.

Alors, à quoi sert la pondération ? À **déplacer le seuil implicite**. Avec un seuil de 0,5, le modèle pondéré déclare « fraude » dès que la probabilité *gonflée* dépasse 0,5, ce qui correspond à une probabilité réelle bien plus basse. Le rappel passe de 0,103 à **0,863** : sur 146 fraudes, il en trouve 126. Mais la précision s'effondre à 0,049 : il déclenche 2 432 fausses alertes, contre 9 auparavant. On a gagné 111 détections supplémentaires (de 15 à 126), au prix d'environ 2 400 vérifications inutiles de plus. Est-ce un bon marché ? **Cela dépend uniquement des coûts** (4.3.5).

> ⚠️ **Avec des poids, les probabilités ne sont plus des probabilités.** Si vous avez besoin de probabilités fiables (chiffrer un risque, calculer une espérance de gain), **corrigez-les** comme ci-dessus ou recalibrez-les (section 5.2). Si vous ne vous servez que du classement, la pondération est sans conséquence.

Pour les modèles à base d'arbres, le mécanisme est un peu différent : les poids modifient l'importance de chaque exemple dans le calcul des impuretés et des gradients (chapitre 2), de sorte que les **modèles eux-mêmes** diffèrent, pas seulement leurs probabilités. Sur nos données, le boosting sans correction obtient une PR-AUC de 0,625 et le boosting pondéré de 0,643 : une différence trop faible, avec 146 fraudes de test, pour être distinguée du hasard (4.3.6).

### 4.3.3 Le rééchantillonnage aléatoire

La seconde famille de remèdes agit sur les **données** : on rééquilibre l'échantillon d'entraînement avant d'apprendre.

- Le **sous-échantillonnage** (*undersampling*) retire au hasard des exemples de la classe majoritaire. On garde par exemple 5 non-fraudes pour 1 fraude. Rapide, mais on **jette des données** : ici, plus de 95 % des commandes normales.
- Le **sur-échantillonnage** (*oversampling*) recopie au hasard des exemples de la classe minoritaire jusqu'à égalité. On ne perd rien, mais on duplique : le modèle voit la même fraude des dizaines de fois et peut la **mémoriser**.

Un exemple à la main : 1 000 commandes dont 10 fraudes. Sous-échantillonner à 5 contre 1 garde les 10 fraudes et 50 commandes normales tirées au hasard, soit 60 lignes ; sur-échantillonner à l'égalité garde les 990 commandes normales et recopie chacune des 10 fraudes 99 fois, soit 1 980 lignes.

```python hide
rng = np.random.default_rng(0)
i1, i0 = np.where(ya.values == 1)[0], np.where(ya.values == 0)[0]
sel_u = np.r_[i1, rng.choice(i0, len(i1) * 5, replace=False)]
sel_o = np.r_[i0, rng.choice(i1, len(i0), replace=True)]
res = {}
for nom, sel in [("sous-échantillonnage 5:1", sel_u), ("sur-échantillonnage aléatoire", sel_o)]:
    m = LogisticRegression(max_iter=3000).fit(sc_a.transform(Xa)[sel], ya.values[sel])
    p = m.predict_proba(sc_a.transform(Xb))[:, 1]
    pr = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(yb, pr).ravel()
    res[nom] = (roc_auc_score(yb, p), average_precision_score(yb, p), precision_score(yb, pr), recall_score(yb, pr), len(sel))
print("lignes d'entraînement : sous-échantillonnage", len(sel_u), "| sur-échantillonnage", len(sel_o), "| original", len(ya))
for k, v in res.items():
    print(f"{k:32s} AUC {v[0]:.3f}  PR-AUC {v[1]:.3f}  précision {v[2]:.3f}  rappel {v[3]:.3f}")
```
<!--sortie-->
```text
lignes d'entraînement : sous-échantillonnage 2040 | sur-échantillonnage 83320 | original 42000
sous-échantillonnage 5:1         AUC 0.921  PR-AUC 0.220  précision 0.119  rappel 0.534
sur-échantillonnage aléatoire    AUC 0.923  PR-AUC 0.187  précision 0.049  rappel 0.863
```

```python hide-code
tab_re = pd.DataFrame({"traitement": ["aucun", "poids équilibrés", "sous-échantillonnage 5:1", "sur-échantillonnage aléatoire"],
                       "AUC-ROC": [roc_auc_score(yb, p_logit), roc_auc_score(yb, p_w)] + [res[k][0] for k in res],
                       "PR-AUC": [average_precision_score(yb, p_logit), average_precision_score(yb, p_w)] + [res[k][1] for k in res],
                       "précision à 0,5": [precision_score(yb, (p_logit >= .5).astype(int)), precision_score(yb, pred_w)] + [res[k][2] for k in res],
                       "rappel à 0,5": [recall_score(yb, (p_logit >= .5).astype(int)), recall_score(yb, pred_w)] + [res[k][3] for k in res]}).round(3)
print(tab_re.to_string(index=False))
```
<!--sortie-->
```text
                   traitement  AUC-ROC  PR-AUC  précision à 0,5  rappel à 0,5
                        aucun    0.921   0.260            0.625         0.103
             poids équilibrés    0.923   0.187            0.049         0.863
     sous-échantillonnage 5:1    0.921   0.220            0.119         0.534
sur-échantillonnage aléatoire    0.923   0.187            0.049         0.863
```

Le sur-échantillonnage aléatoire donne **exactement** les mêmes résultats que les poids équilibrés (même AUC, même précision, même rappel) : recopier chaque fraude $w$ fois et la pondérer par $w$ sont, pour une régression logistique, une seule et même opération. Le sous-échantillonnage place le compromis ailleurs (précision 0,119, rappel 0,534) : on a rééquilibré à 5 contre 1, et non à 1 contre 1, donc le décalage des probabilités est moindre. Aucune des trois stratégies n'améliore l'AUC-ROC (0,921 à 0,923) : elles **déplacent le point de fonctionnement**, elles ne rendent pas le modèle meilleur.

> ⚠️ **Rééchantillonner avant de séparer est une fuite d'information.** Si l'on sur-échantillonne la table complète **puis** qu'on la sépare en entraînement et validation (ou qu'on lance une validation croisée), les copies d'une même fraude se retrouvent des deux côtés : le modèle est « testé » sur des exemples qu'il a déjà vus. Le score devient absurde. Nous le mesurons en 4.5. La règle : le rééchantillonnage ne s'applique qu'aux **plis d'entraînement**, dans le pipeline.

### 4.3.4 Le seuil de décision : le levier oublié

Un modèle de classification produit une **probabilité** ; la **décision** (« fraude » ou non) vient d'un **seuil** : on déclare « fraude » si la probabilité dépasse $s$. Le seuil de 0,5 n'a aucune raison d'être le bon : il n'est optimal que si les deux erreurs coûtent autant et si les probabilités sont fidèles. Faire varier $s$ déplace le modèle le long de sa **courbe précision-rappel** : un seuil bas détecte plus de fraudes (rappel haut) mais déclenche plus de fausses alertes (précision basse), un seuil haut fait l'inverse.

```python hide
gb = HistGradientBoostingClassifier(random_state=0, max_iter=150).fit(Xa, ya)
gb_w = HistGradientBoostingClassifier(random_state=0, max_iter=150, class_weight="balanced").fit(Xa, ya)
p_gb, p_gbw = gb.predict_proba(Xb)[:, 1], gb_w.predict_proba(Xb)[:, 1]
pa, ra, _ = precision_recall_curve(yb, p_gb)
pb, rb, _ = precision_recall_curve(yb, p_gbw)
pl, rl, _ = precision_recall_curve(yb, p_logit)
fig, ax = plt.subplots(figsize=(6.2, 4.2))
ax.plot(rl, pl, color=GRIS, lw=1.6, label="régression logistique")
ax.plot(ra, pa, color=BLEU, lw=1.8, label="boosting")
ax.plot(rb, pb, color=ORANGE, lw=1.8, ls="--", label="boosting pondéré")
ax.axhline(yb.mean(), color=ROUGE, lw=1, ls=":")
ax.text(0.02, yb.mean() + 0.02, "classement au hasard (0,8 %)", color=ROUGE, fontsize=8)
ax.set_xlabel("rappel (part des fraudes détectées)")
ax.set_ylabel("précision (part des alertes justes)")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.legend(frameon=False, loc="upper right", fontsize=8)
ax.set_title("Courbes précision-rappel sur le jeu de test", fontsize=10)
plt.tight_layout()
plt.savefig("figures/ch04-precision-rappel.png", dpi=200, bbox_inches="tight")
plt.close()
print("PR-AUC test : logistique", round(average_precision_score(yb, p_logit), 3), "| boosting", round(average_precision_score(yb, p_gb), 3),
      "| boosting pondéré", round(average_precision_score(yb, p_gbw), 3))
print("AUC-ROC test : logistique", round(roc_auc_score(yb, p_logit), 3), "| boosting", round(roc_auc_score(yb, p_gb), 3),
      "| boosting pondéré", round(roc_auc_score(yb, p_gbw), 3))
```
<!--sortie-->
```text
PR-AUC test : logistique 0.26 | boosting 0.625 | boosting pondéré 0.643
AUC-ROC test : logistique 0.921 | boosting 0.97 | boosting pondéré 0.975
```

![Courbes précision-rappel de trois modèles sur les 18 000 commandes de test : le boosting domine nettement la régression logistique, et la pondération déplace peu la courbe elle-même.](figures/ch04-precision-rappel.png)

La figure dit l'essentiel. Le boosting domine la régression logistique sur **toute** la plage (par exemple, à rappel de 0,5, il garde une précision bien supérieure). Et pondérer ou non le boosting ne change presque pas la courbe : les deux courbes se superposent à peu près. **Une courbe précision-rappel est la carte de tous les compromis possibles ; choisir un seuil, c'est choisir un point sur cette carte.**

Où se placer ? Pas en regardant le jeu de test (le choisir sur le test, c'est de nouveau une fuite) : on choisit le seuil sur des **prédictions hors pli** du jeu d'entraînement, obtenues par validation croisée, puis on l'applique au test.

```python hide
oof = cross_val_predict(HistGradientBoostingClassifier(random_state=0, max_iter=150), Xa, ya,
                        cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
seuils = np.linspace(0.01, 0.95, 95)
f1_oof = [f1_score(ya, (oof >= s).astype(int)) for s in seuils]
s_f1 = seuils[int(np.argmax(f1_oof))]
pred_f1 = (p_gb >= s_f1).astype(int)
tn, fp, fn, tp = confusion_matrix(yb, pred_f1).ravel()
print("seuil maximisant le F1 sur les prédictions hors pli :", round(s_f1, 2))
print(f"jeu de test : F1 {f1_score(yb, pred_f1):.3f}, précision {precision_score(yb, pred_f1):.3f}, rappel {recall_score(yb, pred_f1):.3f} (VP {tp}, FP {fp}, FN {fn})")
pred_05 = (p_gb >= 0.5).astype(int)
print(f"à 0,5 : F1 {f1_score(yb, pred_05):.3f}, précision {precision_score(yb, pred_05):.3f}, rappel {recall_score(yb, pred_05):.3f}")
```
<!--sortie-->
```text
seuil maximisant le F1 sur les prédictions hors pli : 0.42
jeu de test : F1 0.598, précision 0.678, rappel 0.534 (VP 78, FP 37, FN 68)
à 0,5 : F1 0.601, précision 0.710, rappel 0.521
```

Avec le boosting, le seuil qui maximise le F1 sur les prédictions hors pli est à $s=0{,}42$ ; sur le test, il donne un F1 de 0,598 (précision 0,678, rappel 0,534), contre 0,601 au seuil de 0,5 (précision 0,710, rappel 0,521). **Aucune différence** : le F1 donne le même poids aux deux erreurs et les probabilités du boosting sont bien calibrées, le seuil de 0,5 était déjà presque optimal pour ce critère. Optimiser un seuil n'est utile que **pour un critère qui correspond à l'usage réel** ; le F1 est rarement ce critère. La section suivante part des coûts.

### 4.3.5 La vue par les coûts

Le meilleur seuil n'est pas celui qui maximise une métrique abstraite, c'est celui qui **minimise ce que coûtent les erreurs**. Supposons qu'une fraude non détectée coûte en moyenne $c_{FN}=100$ € (marchandise perdue), et qu'une fausse alerte coûte $c_{FP}=5$ € (vérification manuelle). Pour une commande dont la **vraie** probabilité de fraude est $p$ :

- si on la laisse passer, le coût espéré est $p\times c_{FN}$ ;
- si on la bloque pour vérification, le coût espéré est $(1-p)\times c_{FP}$.

On bloque quand le second est plus petit que le premier :

$$p\,c_{FN}>(1-p)\,c_{FP}\quad\Longleftrightarrow\quad p>\frac{c_{FP}}{c_{FP}+c_{FN}}.$$

Le **seuil optimal** ne dépend que du rapport des coûts : $s^\star=\frac{5}{105}\approx0{,}048$ ici. Une fraude coûte vingt fois plus qu'une fausse alerte, il faut donc bloquer dès que la probabilité dépasse 4,8 %. Cette formule suppose que les probabilités sont **calibrées** : celles du boosting non pondéré le sont à peu près, pas celles d'un modèle pondéré (4.3.2).

```python hide
c_fn, c_fp = 100, 5


def cout_total(p, s):
    bloque = p >= s
    return int(((~bloque) & (yb.values == 1)).sum() * c_fn + (bloque & (yb.values == 0)).sum() * c_fp)


s_theorique = c_fp / (c_fp + c_fn)
seuils_c = np.linspace(0.005, 0.99, 200)
couts_gb = [cout_total(p_gb, s) for s in seuils_c]
# seuil du modèle pondéré, converti par la formule de correction : p_pondérée = t w / (1 - t + t w)
s_pondere = s_theorique * w / (1 - s_theorique + s_theorique * w)
cout_oof = [int(((oof < s) & (ya.values == 1)).sum() * c_fn + ((oof >= s) & (ya.values == 0)).sum() * c_fp) for s in seuils_c]      # sur l'entraînement, hors pli
s_cout_oof = seuils_c[int(np.argmin(cout_oof))]
tab_cout = pd.DataFrame({
    "règle de décision": ["seuil 0,5 (défaut)", f"seuil théorique {s_theorique:.3f}", f"seuil minimisant le coût hors pli ({s_cout_oof:.3f})", "aucune alerte (modèle paresseux)"],
    "coût total sur le test (€)": [cout_total(p_gb, 0.5), cout_total(p_gb, s_theorique), cout_total(p_gb, s_cout_oof), int(yb.sum() * c_fn)],
})
print(tab_cout.to_string(index=False))
print("seuil équivalent pour le boosting pondéré :", round(s_pondere, 3), "-> coût", cout_total(p_gbw, s_pondere), "| à 0,5 :", cout_total(p_gbw, 0.5))

rng = np.random.default_rng(2)
yv = yb.values
diff = []
for _ in range(500):
    idx = rng.integers(0, len(yv), len(yv))
    c_a = (((p_gb[idx] < s_theorique) & (yv[idx] == 1)).sum() * c_fn + ((p_gb[idx] >= s_theorique) & (yv[idx] == 0)).sum() * c_fp)
    c_b = (((p_gbw[idx] < 0.5) & (yv[idx] == 1)).sum() * c_fn + ((p_gbw[idx] >= 0.5) & (yv[idx] == 0)).sum() * c_fp)
    diff.append(c_b - c_a)
lo, hi = np.percentile(diff, [2.5, 97.5])
print(f"coût du boosting pondéré à 0,5 moins coût du boosting au seuil théorique : moyenne {np.mean(diff):.0f} €, intervalle à 95 % [{lo:.0f} ; {hi:.0f}]")

fig, ax = plt.subplots(figsize=(6.2, 3.8))
ax.plot(seuils_c, np.array(couts_gb) / 1000, color=BLEU, lw=1.8)
ax.axvline(s_theorique, color=ORANGE, lw=1.4, ls="--")
ax.text(s_theorique + 0.01, max(couts_gb) / 1000 * 0.9, f"seuil théorique {s_theorique:.3f}".replace(".", ","), color=ORANGE, fontsize=8)
ax.axvline(0.5, color=GRIS, lw=1, ls=":")
ax.text(0.51, max(couts_gb) / 1000 * 0.9, "seuil 0,5", color=GRIS, fontsize=8)
ax.set_xlabel("seuil de décision")
ax.set_ylabel("coût total sur le test (milliers d'€)")
ax.set_title("Le coût dépend du seuil, et le seuil par défaut n'est pas le bon", fontsize=10)
plt.tight_layout()
plt.savefig("figures/ch04-cout-seuil.png", dpi=200, bbox_inches="tight")
plt.close()
```
<!--sortie-->
```text
                        règle de décision  coût total sur le test (€)
                       seuil 0,5 (défaut)                        7155
                    seuil théorique 0.048                        5575
seuil minimisant le coût hors pli (0.025)                        5420
         aucune alerte (modèle paresseux)                       14600
seuil équivalent pour le boosting pondéré : 0.86 -> coût 5365 | à 0,5 : 4595
coût du boosting pondéré à 0,5 moins coût du boosting au seuil théorique : moyenne -1031 €, intervalle à 95 % [-2198 ; -37]
```

```python hide-code
print(tab_cout.to_string(index=False))
print("boosting pondéré, seuil 0,5 : coût", cout_total(p_gbw, 0.5), "€ ; au seuil équivalent corrigé", round(s_pondere, 2), ":", cout_total(p_gbw, s_pondere), "€")
print(f"coût du boosting pondéré à 0,5 moins coût du boosting au seuil théorique : moyenne {np.mean(diff):.0f} €, intervalle à 95 % [{lo:.0f} ; {hi:.0f}]")
```
<!--sortie-->
```text
                        règle de décision  coût total sur le test (€)
                       seuil 0,5 (défaut)                        7155
                    seuil théorique 0.048                        5575
seuil minimisant le coût hors pli (0.025)                        5420
         aucune alerte (modèle paresseux)                       14600
boosting pondéré, seuil 0,5 : coût 4595 € ; au seuil équivalent corrigé 0.86 : 5365 €
coût du boosting pondéré à 0,5 moins coût du boosting au seuil théorique : moyenne -1031 €, intervalle à 95 % [-2198 ; -37]
```

![Coût total des erreurs de décision sur les 18 000 commandes de test en fonction du seuil, pour le boosting : le coût est minimal pour des seuils bas, bien en dessous de 0,5.](figures/ch04-cout-seuil.png)

En code, appliquer un seuil est une simple comparaison de la probabilité prédite :

```python
proba = gb.predict_proba(Xb)[:, 1]            # probabilité de fraude de chaque commande de test
alerte = proba >= 0.048                       # on bloque dès que la probabilité dépasse le seuil
print(alerte.sum(), "commandes bloquées sur", len(alerte))
```
<!--sortie-->
```text
231 commandes bloquées sur 18000
```

Le tableau et la figure disent trois choses. (1) Le seuil par défaut de 0,5 est **le plus coûteux** des seuils raisonnables : 7 155 €. (2) Le seuil théorique de 0,048 réduit le coût de 22 % (5 575 €), et le seuil qui minimise le coût sur les prédictions hors pli (0,025) donne un résultat voisin (5 420 €) : sur 146 fraudes, la formule suffit, sans chercher le seuil exact. (3) Ne rien bloquer coûterait 14 600 €.

Le boosting **pondéré**, à son seuil par défaut de 0,5, coûte 4 595 € : moins que toutes les lignes précédentes. Il ne faut pas y voir un miracle de la pondération. Les poids ont modifié les **arbres eux-mêmes**, pas seulement les probabilités (4.3.2). Et l'avantage, de 1 031 € en moyenne, est mesuré avec une grande marge (intervalle à 95 % par *bootstrap* du test : de −2 198 à −37 €) : il exclut de peu zéro, mais le *bootstrap* ne rééchantillonne que le test et **ignore la variabilité due à l'entraînement**. Avec 146 fraudes, retenez surtout le constat solide : **le seuil par défaut est mauvais** dès que les erreurs n'ont pas le même coût.

> 💡 **Le rôle des poids, revisité.** Pondérer les classes, rééchantillonner et déplacer le seuil sont **trois façons d'obtenir le même effet** : changer le compromis entre faux négatifs et faux positifs. Si vous connaissez vos coûts, le plus propre est de **laisser le modèle apprendre des probabilités fidèles, puis de choisir le seuil par les coûts**. Poids et rééchantillonnage sont des commodités quand l'algorithme apprend mal avec de rares positifs, pas des objectifs en soi.

### 4.3.6 Comparer honnêtement : et le déséquilibre modéré ?

Avec 146 fraudes de test, toute comparaison de deux stratégies est entachée d'une **forte incertitude**. Mesurons-la par un *bootstrap* du jeu de test (volume I, section 3.3.5) : on rééchantillonne 500 fois les 18 000 commandes de test, et on observe la dispersion de la PR-AUC.

```python hide
rng = np.random.default_rng(1)
n_b = len(yb)
yv = yb.values
bs = {"boosting": [], "boosting pondéré": [], "écart": []}
for _ in range(500):
    idx = rng.integers(0, n_b, n_b)
    a, b = average_precision_score(yv[idx], p_gb[idx]), average_precision_score(yv[idx], p_gbw[idx])
    bs["boosting"].append(a); bs["boosting pondéré"].append(b); bs["écart"].append(b - a)
for k, v in bs.items():
    lo, hi = np.percentile(v, [2.5, 97.5])
    print(f"{k:18s} moyenne {np.mean(v):.3f}  intervalle à 95 % [{lo:.3f} ; {hi:.3f}]")
```
<!--sortie-->
```text
boosting           moyenne 0.623  intervalle à 95 % [0.543 ; 0.701]
boosting pondéré   moyenne 0.642  intervalle à 95 % [0.561 ; 0.716]
écart              moyenne 0.020  intervalle à 95 % [-0.028 ; 0.072]
```

```python hide-code
for k, v in bs.items():
    lo, hi = np.percentile(v, [2.5, 97.5])
    print(f"{k:18s} moyenne {np.mean(v):.3f}  intervalle à 95 % [{lo:.3f} ; {hi:.3f}]")
```
<!--sortie-->
```text
boosting           moyenne 0.623  intervalle à 95 % [0.543 ; 0.701]
boosting pondéré   moyenne 0.642  intervalle à 95 % [0.561 ; 0.716]
écart              moyenne 0.020  intervalle à 95 % [-0.028 ; 0.072]
```

Les intervalles de la PR-AUC du boosting et du boosting pondéré se **recouvrent largement** : l'intervalle de leur écart contient zéro. Nous n'avons **aucune preuve** que la pondération améliore le classement du boosting ; seule l'écart de seuil de décision, lui, est réel.

Reste le cas du **déséquilibre modéré**, celui du départ des clients (14 %). Les mêmes stratégies y changent-elles quelque chose ?

```python hide
clients = pd.read_csv("donnees/clients_ml.csv")
yc = clients["churn_90j"]
Xc = pd.get_dummies(clients.drop(columns=["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]), dtype=float)
Xca, Xcb, yca, ycb = train_test_split(Xc, yc, test_size=0.25, random_state=0, stratify=yc)
lignes = []
for nom, m in [("boosting", HistGradientBoostingClassifier(random_state=0, max_iter=100)),
               ("boosting pondéré", HistGradientBoostingClassifier(random_state=0, max_iter=100, class_weight="balanced"))]:
    m.fit(Xca, yca)
    p = m.predict_proba(Xcb)[:, 1]
    for s in (0.5,):
        pr = (p >= s).astype(int)
        lignes.append({"modèle": nom, "AUC-ROC": roc_auc_score(ycb, p), "PR-AUC": average_precision_score(ycb, p),
                       "précision à 0,5": precision_score(ycb, pr), "rappel à 0,5": recall_score(ycb, pr)})
tab_churn = pd.DataFrame(lignes).round(3)
print("départs :", round(yc.mean() * 100, 1), "% ; exactitude du modèle paresseux :", round((ycb == 0).mean(), 3))
print(tab_churn.to_string(index=False))
```
<!--sortie-->
```text
départs : 14.0 % ; exactitude du modèle paresseux : 0.86
          modèle  AUC-ROC  PR-AUC  précision à 0,5  rappel à 0,5
        boosting    0.899   0.655            0.689         0.458
boosting pondéré    0.899   0.663            0.504         0.717
```

```python hide-code
print(tab_churn.to_string(index=False))
```
<!--sortie-->
```text
          modèle  AUC-ROC  PR-AUC  précision à 0,5  rappel à 0,5
        boosting    0.899   0.655            0.689         0.458
boosting pondéré    0.899   0.663            0.504         0.717
```

À 14 % de positifs, les deux modèles ont presque le même classement (AUC-ROC et PR-AUC proches) ; la pondération déplace surtout le compromis précision-rappel à 0,5, comme avant. **Un déséquilibre de cet ordre n'appelle pas de traitement spécial** : un bon modèle, des probabilités fiables, et un seuil choisi selon l'usage (par exemple, contacter les 10 % de clients les plus à risque, que la capacité du service client permet). Les précautions de cette section prennent toute leur valeur quand la classe rare passe sous quelques pour cent.

> ✅ **À retenir (classes déséquilibrées).** (1) Jugez avec précision, rappel et PR-AUC, jamais avec l'exactitude. (2) Les poids de classes et le rééchantillonnage **déplacent les probabilités et le seuil implicite** ; ils n'améliorent pas, en général, le classement. (3) Le **seuil de décision** se choisit par les coûts, sur des prédictions hors pli, jamais sur le test. (4) Rééchantillonner uniquement à l'intérieur des plis d'entraînement. (5) Avec peu de positifs de test, **chiffrez l'incertitude** de vos comparaisons.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (comparer toutes les stratégies sur les fraudes) et application 4.6 (choisir un seuil par les coûts) ; exercices 4.9 à 4.11.
