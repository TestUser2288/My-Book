## 5.2 Calibration

Une probabilité n'est utile que si on peut la prendre au mot. Quand la gérante lit « 30 % » sur la fiche d'un client, elle en déduit un coût attendu, un seuil, une priorité. Si ce « 30 % » est en réalité « 55 % », tout ce qui en découle est faux, même si le classement des clients est parfait. Cette section apprend à **vérifier** que les probabilités sont justes, à comprendre pourquoi elles ne le sont pas toujours, et à les **réparer**.

### 5.2.1 Qu'est-ce qu'une probabilité « juste » ?

Un modèle est **calibré** si, parmi tous les clients à qui il attribue une probabilité $p$, une proportion $p$ d'entre eux subit effectivement l'événement :
$$P(Y=1\mid \hat p=p)=p\quad\text{pour tout } p.$$
Il s'agit d'une propriété distincte de la **discrimination** (la capacité à bien classer, mesurée par l'AUC). Un score peut classer parfaitement et être très mal calibré : si l'on divise toutes les probabilités d'un modèle parfaitement calibré par deux, l'ordre reste identique (l'AUC ne bouge pas), mais plus aucune probabilité n'est juste.

**Un exemple à la main.** Vingt clients : dix reçoivent la probabilité $0{,}10$ et deux d'entre eux partent (taux observé $0{,}20$) ; les dix autres reçoivent $0{,}60$ et cinq partent (taux observé $0{,}50$). Le modèle est trop optimiste dans le premier groupe (il annonce 10 %, la réalité est de 20 %) et trop pessimiste dans le second (60 % annoncés, 50 % observés).

On le résume avec le **diagramme de fiabilité** (*reliability diagram*) : on regroupe les clients en classes de probabilités voisines (ici, par classes de même effectif), et l'on trace, pour chaque classe, le **taux observé** en fonction de la **probabilité moyenne prédite**. Un modèle calibré suit la diagonale. L'**erreur de calibration attendue** (ECE) est l'écart moyen à la diagonale, pondéré par l'effectif $n_b$ de chaque classe $b$ :
$$\mathrm{ECE}=\sum_{b}\frac{n_b}{n}\,\bigl|\,\bar p_b-\bar y_b\,\bigr|.$$
Sur notre exemple, $\mathrm{ECE}=\tfrac12\times0{,}10+\tfrac12\times0{,}10=0{,}10$.

> ⚠️ **L'ECE est bruitée.** Avec 10 classes de 240 clients, le taux observé d'une classe où le risque est de 14 % fluctue naturellement de $\sqrt{0{,}14\times0{,}86/240}\approx0{,}022$. Une ECE de 0,01 ou 0,02 est donc **indiscernable d'une calibration parfaite** sur ce jeu. L'ECE dépend aussi du découpage en classes. Elle se lit avec le diagramme, jamais seule.

```python hide
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import CalibratedClassifierCV

def fiabilite(yv, pv, n_bins=10):
    """Diagramme de fiabilité à classes d'effectifs égaux : (probabilité moyenne prédite, taux observé, effectif)."""
    ordre = np.argsort(pv); groupes = np.array_split(ordre, n_bins)
    return np.array([[pv[g].mean(), yv[g].mean(), len(g)] for g in groupes])

def ece(yv, pv, n_bins=10):
    t = fiabilite(yv, pv, n_bins); return float(np.sum(t[:, 2] * np.abs(t[:, 0] - t[:, 1])) / t[:, 2].sum())

gb_sur = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.3, max_leaf_nodes=63, min_samples_leaf=5, early_stopping=False, random_state=0).fit(Xtr, ytr)
lr_pond = LogisticRegression(max_iter=3000, class_weight="balanced").fit(sc.transform(Xtr), ytr)
modeles = {"logistique": (lambda Z: lr.predict_proba(sc.transform(Z))[:, 1]), "forêt": (lambda Z: rf.predict_proba(Z)[:, 1]), "boosting": (lambda Z: gb.predict_proba(Z)[:, 1]),
           "boosting surajusté": (lambda Z: gb_sur.predict_proba(Z)[:, 1]), "logistique pondérée": (lambda Z: lr_pond.predict_proba(sc.transform(Z))[:, 1])}
ste = {k: f(Xte) for k, f in modeles.items()}; sca = {k: f(Xca) for k, f in modeles.items()}
yt = yte.to_numpy(); yc = yca.to_numpy()
print(f"{'modèle':22s} {'AUC':>6s} {'Brier':>7s} {'log-loss':>9s} {'ECE':>6s} {'proba moyenne':>14s}")
for k, pk in ste.items():
    print(f"{k:22s} {M.roc_auc_score(yt, pk):6.3f} {M.brier_score_loss(yt, pk):7.4f} {M.log_loss(yt, np.clip(pk, 1e-6, 1 - 1e-6)):9.4f} {ece(yt, pk):6.4f} {pk.mean():14.3f}")
print("prévalence observée :", round(yt.mean(), 3))
for k in ["forêt", "boosting surajusté", "logistique pondérée"]:
    t = fiabilite(yt, ste[k], 10)
    print(k, "| probas prédites par classe :", np.round(t[:, 0], 3).tolist(), "| taux observés :", np.round(t[:, 1], 3).tolist())
```
<!--sortie-->
```text
modèle                    AUC   Brier  log-loss    ECE  proba moyenne
logistique              0.859  0.0872    0.2886 0.0120          0.136
forêt                   0.888  0.0808    0.2687 0.0314          0.139
boosting                0.897  0.0758    0.2548 0.0137          0.128
boosting surajusté      0.876  0.1010    0.7143 0.0975          0.094
logistique pondérée     0.857  0.1542    0.4588 0.2087          0.349
prévalence observée : 0.14
forêt | probas prédites par classe : [0.003, 0.011, 0.022, 0.04, 0.062, 0.093, 0.135, 0.193, 0.284, 0.543] | taux observés : [0.004, 0.0, 0.008, 0.033, 0.038, 0.079, 0.1, 0.15, 0.317, 0.675]
boosting surajusté | probas prédites par classe : [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.056, 0.886] | taux observés : [0.0, 0.017, 0.017, 0.029, 0.021, 0.096, 0.092, 0.154, 0.35, 0.629]
logistique pondérée | probas prédites par classe : [0.013, 0.041, 0.08, 0.138, 0.225, 0.335, 0.459, 0.596, 0.73, 0.873] | taux observés : [0.008, 0.008, 0.021, 0.017, 0.042, 0.092, 0.162, 0.183, 0.288, 0.583]
```

### 5.2.2 Qui est bien calibré, qui ne l'est pas ?

Comparons cinq modèles sur le jeu de test : les trois du chapitre, plus deux modèles « abîmés » à dessein : un **boosting surajusté** (300 itérations, taux d'apprentissage 0,3, arbres de 63 feuilles) et une **régression logistique avec poids de classes** (`class_weight="balanced"`, qui donne autant de poids aux 14 % de partants qu'aux 86 % de fidèles).

| Modèle | AUC | Brier | Log-loss | ECE | Probabilité moyenne |
|---|---:|---:|---:|---:|---:|
| Régression logistique | 0,859 | 0,0872 | 0,2886 | 0,012 | 0,136 |
| Forêt aléatoire | 0,888 | 0,0808 | 0,2687 | 0,031 | 0,139 |
| Boosting (réglages par défaut) | 0,897 | 0,0758 | 0,2548 | 0,014 | 0,128 |
| Boosting surajusté | 0,876 | 0,1010 | 0,7143 | 0,098 | 0,094 |
| Logistique pondérée | 0,857 | 0,1542 | 0,4588 | 0,209 | 0,349 |

(La prévalence observée sur le jeu de test est de 0,140.)

```python hide
fig, ax = plt.subplots(2, 3, figsize=(11, 7))
for a, (k, pk) in zip(ax.ravel(), list(ste.items()) + [("", None)]):
    if pk is None:
        a.hist(ste["forêt"], bins=30, range=(0, 1), color="#1baf7a", alpha=0.7, label="forêt"); a.hist(ste["boosting surajusté"], bins=30, range=(0, 1), color="#e34948", alpha=0.5, label="boosting surajusté")
        a.set_yscale("log"); a.set_xlabel("probabilité prédite"); a.set_ylabel("nombre de clients (échelle log)"); a.legend(frameon=False, fontsize=8); a.set_title("Distribution des probabilités", fontsize=10); continue
    t = fiabilite(yt, pk, 10); a.plot([0, 1], [0, 1], color="#898781", ls="--", lw=1); a.plot(t[:, 0], t[:, 1], "o-", color="#2a78d6", lw=1.6, ms=4)
    a.set_title(f"{k} (ECE {ece(yt, pk):.3f})", fontsize=10); a.set_xlim(0, 1); a.set_ylim(0, 1); a.set_xlabel("probabilité moyenne prédite"); a.set_ylabel("taux observé")
plt.tight_layout(); plt.savefig("figures/ch05-fiabilite.png", dpi=200, bbox_inches="tight"); plt.close()
```

![Diagrammes de fiabilité des cinq modèles sur le jeu de test (classes de même effectif), et distribution des probabilités de deux d'entre eux. Un modèle calibré suit la diagonale.](figures/ch05-fiabilite.png)

Chaque modèle raconte une histoire différente.

**La régression logistique est calibrée par construction.** Elle maximise la vraisemblance, donc annule la dérivée de la log-vraisemblance par rapport à l'ordonnée à l'origine : $\sum_i(y_i-\hat p_i)=0$. La somme des probabilités prédites sur le jeu d'entraînement est égale au nombre de partants : en moyenne, le modèle est juste (probabilité moyenne 0,136 pour une prévalence de 0,140). Quand le modèle est correctement spécifié, cette justesse vaut aussi à tous les niveaux. Et même s'il ne l'est pas, la calibration reste en général très honorable.

**La forêt est trop prudente aux extrêmes.** Elle moyenne les proportions observées dans les feuilles de ses arbres, avec au moins 5 clients par feuille : ses probabilités sont tirées vers le milieu. Dans la classe des clients les plus à risque, elle annonce **54 %** pour un taux observé de **68 %** ; dans la classe la moins à risque, elle annonce 0,3 % pour 0,4 %. C'est un modèle *sous-confiant* (ECE 0,031, la plus mauvaise des trois modèles « sains »).

**Le boosting par défaut est bien calibré** (ECE 0,014, log-loss 0,255) : il optimise la log-loss, avec un petit pas d'apprentissage, et s'arrête avant de surajuster. Mais le **boosting surajusté** est le contraire de la forêt : il est *sur-confiant*. Ses probabilités se collent à 0 ou à 1 (huit classes sur dix ont une probabilité moyenne prédite inférieure à 0,001), et la classe des plus à risque reçoit **89 %** pour un taux observé de **63 %**. Sa log-loss est de 0,714, près de trois fois celle du boosting réglé. Retenez qu'un boosting n'est bien calibré que si on le laisse peu s'entraîner.

**La logistique pondérée classe aussi bien que la logistique ordinaire (AUC 0,857 contre 0,859) mais ses probabilités sont fausses :** elle annonce en moyenne 35 % de départs alors qu'ils sont 14 %. Les poids de classes déplacent la prévalence apparente. On y revient en 5.2.6.

> 💡 **Ce que montre ce tableau.** L'AUC et la calibration sont indépendantes. La logistique pondérée a une AUC quasi identique à celle de la logistique ordinaire et un Brier presque deux fois plus mauvais (0,154 contre 0,087). Ne choisissez pas un modèle sur la seule AUC si vous comptez utiliser ses probabilités.

> 🧭 **Et les autres modèles ?** Les SVM produisent des scores qui sont des distances à une frontière, pas des probabilités (section 2.5) ; les k plus proches voisins annoncent des proportions de voisins, tirées vers les extrêmes quand $k$ est petit ; le Bayes naïf est souvent sur-confiant, car l'indépendance supposée entre variables compte plusieurs fois la même information. Dans tous les cas, **vérifiez**.

### 5.2.3 Réparer : la méthode de Platt

Si le défaut de calibration est une déformation régulière des probabilités, on peut la corriger après coup par une **recalibration** : on apprend une fonction $g$ telle que $g(\hat s)$ soit calibré, où $\hat s$ est le score du modèle. La première méthode est celle de **Platt** : on suppose que le log-odds de la probabilité vraie est une fonction affine du log-odds du score,
$$P(Y=1\mid \hat s)=\sigma\bigl(a\cdot\operatorname{logit}(\hat s)+b\bigr),\qquad \sigma(z)=\frac1{1+e^{-z}}.$$
Deux paramètres $(a,b)$, estimés par maximum de vraisemblance : c'est une **régression logistique à une variable** (le logit du score), ajustée sur le jeu de **calibration**, qui n'a pas servi à entraîner le modèle.

Les paramètres s'interprètent. Une **pente $a>1$** étire les probabilités vers les extrêmes (corrige un modèle sous-confiant) ; une pente **$a<1$** les écrase vers le centre (corrige un modèle sur-confiant) ; l'**ordonnée $b$** déplace le niveau global. Sur nos trois modèles abîmés :

| Modèle | Pente $a$ | Ordonnée $b$ | Lecture |
|---|---:|---:|---|
| Forêt | 1,42 | 0,55 | étire : le modèle était sous-confiant |
| Boosting surajusté | 0,28 | −0,19 | écrase fortement : il était sur-confiant |
| Logistique pondérée | 1,06 | −1,79 | quasi pas de changement de forme, mais un grand décalage de niveau |

### 5.2.4 Réparer : la régression isotonique

Platt suppose une forme précise (une sigmoïde). La **régression isotonique** n'en suppose aucune, sauf que la probabilité vraie est une fonction **croissante** du score. Elle ajuste, par moindres carrés, la fonction en escalier croissante la plus proche des résultats observés sur le jeu de calibration (par l'algorithme classique « pool adjacent violators » : on fusionne les marches voisines qui violent l'ordre). Elle est donc plus flexible, mais elle demande **plus de données** (compter au moins quelques milliers d'exemples), et elle produit des paliers : plusieurs clients reçoivent exactement la même probabilité.

Voici, pour les trois modèles abîmés, l'effet des deux méthodes, ajustées sur les 2 400 clients du jeu de calibration et évaluées sur le jeu de test :

```python hide
# --- poids de classes : correction exacte par changement de prévalence
pi = ytr.mean(); pi_eff = 0.5                                  # avec class_weight="balanced", tout se passe comme si la prévalence valait 1/2
s = ste["logistique pondérée"]
cote = s / (1 - s) * (pi / (1 - pi)) / (pi_eff / (1 - pi_eff)); corr = cote / (1 + cote)
print("prévalence d'entraînement", round(pi, 4), "| probabilité moyenne brute", round(s.mean(), 3), "-> corrigée", round(corr.mean(), 3), "| prévalence test", round(yt.mean(), 3))
print("Brier brut", round(M.brier_score_loss(yt, s), 4), "-> corrigé", round(M.brier_score_loss(yt, corr), 4), "| ECE brut", round(ece(yt, s), 4), "-> corrigé", round(ece(yt, corr), 4),
      "| Brier de la logistique non pondérée", round(M.brier_score_loss(yt, ste["logistique"]), 4), "| AUC inchangée :", round(M.roc_auc_score(yt, s), 4), round(M.roc_auc_score(yt, corr), 4))
```
<!--sortie-->
```text
prévalence d'entraînement 0.1404 | probabilité moyenne brute 0.349 -> corrigée 0.135 | prévalence test 0.14
Brier brut 0.1542 -> corrigé 0.0881 | ECE brut 0.2087 -> corrigé 0.0153 | Brier de la logistique non pondérée 0.0872 | AUC inchangée : 0.8571 0.8571
```

| Modèle | Méthode | Brier | Log-loss | ECE |
|---|---|---:|---:|---:|
| Forêt | brut | 0,0808 | 0,2687 | 0,031 |
| | Platt | 0,0785 | 0,2629 | 0,009 |
| | isotonique | 0,0780 | 0,2741 | 0,014 |
| Boosting surajusté | brut | 0,1010 | 0,7143 | 0,098 |
| | Platt | 0,0842 | 0,2911 | 0,042 |
| | isotonique | 0,0821 | 0,2734 | 0,012 |
| Logistique pondérée | brut | 0,1542 | 0,4588 | 0,209 |
| | Platt | 0,0881 | 0,2906 | 0,015 |
| | isotonique | 0,0887 | 0,3129 | 0,019 |

![Diagrammes de fiabilité avant (rouge) et après recalibration par Platt (bleu) ou régression isotonique (vert), sur le jeu de test.](figures/ch05-recalibrage.png)

La recalibration est spectaculaire pour les deux modèles les plus abîmés : le Brier de la logistique pondérée passe de 0,154 à 0,088, soit quasiment celui de la logistique ordinaire (0,087), et celui du boosting surajusté de 0,101 à 0,082. Pour la forêt, qui était déjà presque calibrée, le gain est modeste mais réel.

Deux nuances. **Platt est plus stable avec peu de données** (deux paramètres seulement) mais ne peut corriger que des déformations en S ; ici, sur le boosting surajusté, il laisse une ECE de 0,042 que la méthode isotonique ramène à 0,012. **L'isotonique, plus souple, peut perdre en log-loss** : sur la forêt, elle passe de 0,2687 à 0,2741, car ses paliers produisent des probabilités proches de 0 pour des clients dont le risque n'est pas nul. Le Brier, plus tolérant, s'améliore dans les deux cas.

### 5.2.5 Calibrer sans tricher

La recalibration est un **modèle de plus**, qui peut lui aussi surajuster. Trois règles.

1. **Calibrez sur des données que ni le modèle ni vous-même n'avez utilisées pour l'entraîner.** Calibrer sur le jeu d'entraînement revient à corriger un modèle pour les données qu'il connaît déjà par cœur, et donc à ne rien corriger.
2. **Ne touchez pas au jeu de test avant la fin.** Il sert à *mesurer* la calibration, pas à l'obtenir.
3. **Si les données sont comptées**, utilisez la **validation croisée** : à chaque pli, on ajuste le modèle sur les autres et on calibre sur le pli. `CalibratedClassifierCV` fait cela automatiquement.

```python
from sklearn.calibration import CalibratedClassifierCV

foret = RandomForestClassifier(150, min_samples_leaf=5, random_state=0)
foret_calibree = CalibratedClassifierCV(foret, method="isotonic", cv=3).fit(Xtr, ytr)   # 3 plis : chaque pli sert à calibrer le modèle ajusté sur les deux autres
p_cal = foret_calibree.predict_proba(Xte)[:, 1]
print("Brier :", round(M.brier_score_loss(yte, p_cal), 4), "| ECE :", round(ece(yte.to_numpy(), p_cal), 4), "| AUC :", round(M.roc_auc_score(yte, p_cal), 4))
```
<!--sortie-->
```text
Brier : 0.0782 | ECE : 0.0089 | AUC : 0.8888
```

Sur la forêt, la calibration croisée donne un Brier de 0,0782 et une ECE de 0,009, contre 0,0808 et 0,031 avant. L'AUC est quasiment inchangée (0,8888 contre 0,8881) : la recalibration est une fonction croissante des scores, donc elle conserve l'ordre, sauf les égalités que peut créer une fonction en escalier.

> ⚠️ **Recalibrez après tout changement.** Une calibration dépend de la population : si les clients de demain diffèrent de ceux d'hier (nouvelle campagne, nouveau canal), les probabilités dérivent. Un tableau de bord de production doit contenir un diagramme de fiabilité calculé sur les données récentes.

### 5.2.6 Poids de classes et rééchantillonnage : un décalage de prévalence

Le chapitre 4 (section 4.3) présente des remèdes au déséquilibre de classes : **pondérer** les exemples rares, ou **rééchantillonner** (suréchantillonner les rares, sous-échantillonner les fréquents). Ils améliorent souvent le rappel, mais ils déplacent la prévalence que « voit » le modèle, donc ses probabilités. Heureusement, le décalage est **exactement corrigible**.

> 📐 **Correction d'un décalage de prévalence.** D'après la formule de Bayes (volume I, section 2.1.6), la cote *a posteriori* est la cote *a priori* multipliée par un rapport de vraisemblance qui ne dépend que des variables : $\dfrac{P(Y=1\mid x)}{P(Y=0\mid x)}=\dfrac{\pi}{1-\pi}\times\mathrm{LR}(x)$, où $\pi$ est la prévalence. Un modèle entraîné comme si la prévalence valait $\pi'$ (avec `class_weight="balanced"`, on a $\pi'=\tfrac12$) apprend $\dfrac{\pi'}{1-\pi'}\times\mathrm{LR}(x)$ : le même $\mathrm{LR}(x)$, mais un autre a priori. On retrouve donc la vraie cote en la multipliant par $\dfrac{\pi/(1-\pi)}{\pi'/(1-\pi')}$.

Avec $\pi=0{,}1404$ (prévalence d'entraînement) et $\pi'=\tfrac12$, le facteur est $0{,}1404/0{,}8596\approx0{,}163$. Appliquée à la logistique pondérée, la correction ramène la probabilité moyenne de **0,349 à 0,135** (la prévalence du test est 0,140), le Brier de **0,1542 à 0,0881** et l'ECE de **0,209 à 0,015**, **sans aucun jeu de calibration** et sans changer l'AUC. Cela explique l'ordonnée trouvée par Platt en 5.2.3 : $b=-1{,}79$, très proche de $\ln(0{,}163)=-1{,}81$. **Platt retrouve le décalage de prévalence tout seul.**

> 💡 **Quand faut-il corriger ?** Si vous n'utilisez que le **classement** (cibler les 20 % les plus à risque, ou calculer une AUC), le décalage est sans importance : l'ordre est conservé. Si vous utilisez la **probabilité** (calculer un seuil par les coûts comme en 5.1.7, estimer un nombre attendu de départs), il faut corriger ou recalibrer. Le même raisonnement vaut après un suréchantillonnage ou un sous-échantillonnage (section 4.3 et ➕ 4.5) : la prévalence apparente est celle de l'échantillon rééquilibré.

> ✅ **À retenir.**
> - Un modèle est **calibré** si $P(Y=1\mid\hat p=p)=p$. La calibration est indépendante de la discrimination (AUC).
> - Le **diagramme de fiabilité** la révèle ; l'**ECE** la résume mais est bruitée (≈ ±0,02 avec 240 clients par classe).
> - La régression logistique est calibrée par construction ; les forêts sont sous-confiantes ; un boosting trop entraîné est sur-confiant ; les poids de classes décalent la prévalence.
> - **Platt** (deux paramètres, sigmoïde) et la **régression isotonique** (escalier croissant, plus de données) recalibrent sur un jeu **séparé**.
> - Un décalage de prévalence se corrige exactement : cote × $\frac{\pi/(1-\pi)}{\pi'/(1-\pi')}$.
> - Une recalibration doit être **surveillée** : elle dépend de la population.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercices 5.7 et 5.8.
