## 5.1 Métriques

Une métrique répond à une question précise. Choisir celle qui répond à la **bonne** question, avant de comparer des modèles, évite des semaines de travail dans la mauvaise direction. Cette section suit un fil : on part d'un modèle qui sort un **score** par client, on en fait une **décision** (contacter ou non) en choisissant un seuil, puis on mesure la **valeur** de cette décision.

### 5.1.1 Ce que l'on mesure : un score, une décision, une valeur

Trois objets se confondent souvent, et chacun a ses mesures.

- Le **score** (ou la probabilité) que le modèle attribue à chaque client. On le juge avec des mesures indépendantes de tout seuil : l'**AUC**, la **précision moyenne**, la **log-loss**, le **score de Brier**.
- La **décision** obtenue en comparant le score à un **seuil** : « contacter si le risque dépasse $t$ ». On la juge avec des mesures qui dépendent du seuil : exactitude, précision, rappel, $F_1$…
- La **valeur** de cette décision, en euros : ce que rapporte la campagne, une fois déduits ses coûts. C'est la seule mesure qui compte pour la gérante, et celle qui permet de choisir le seuil.

> 💡 **Intuition.** Un thermomètre (le score) n'est pas un diagnostic (la décision), et un diagnostic n'est pas un traitement réussi (la valeur). Un bon thermomètre est nécessaire ; il n'est jamais suffisant.

Dans toute la suite, **le cas positif est le départ** (`churn_90j` = 1). On appelle *positif* un client qui part et *alerte* un client que le modèle signale comme risqué.

```python hide
# --- matrice de confusion et métriques au seuil 0,5 (boosting)
p = P["boosting"]; yt = yte.to_numpy()
yhat = (p >= 0.5).astype(int)
tn, fp, fn, tp = M.confusion_matrix(yt, yhat).ravel()
print("tn fp fn tp :", tn, fp, fn, tp, "| positifs", int(yt.sum()), "négatifs", int((1 - yt).sum()))
print("exactitude", round((tn + tp) / len(yt), 4), "| précision", round(tp / (tp + fp), 4), "| rappel", round(tp / (tp + fn), 4),
      "| spécificité", round(tn / (tn + fp), 4))
print("F1", round(M.f1_score(yt, yhat), 4), "| F2", round(M.fbeta_score(yt, yhat, beta=2), 4), "| F0.5", round(M.fbeta_score(yt, yhat, beta=0.5), 4),
      "| MCC", round(M.matthews_corrcoef(yt, yhat), 4), "| exactitude du modèle « jamais de départ »", round(1 - yt.mean(), 4))
# --- AUC = probabilité qu'un positif ait un score supérieur à celui d'un négatif
pos, neg = p[yt == 1], p[yt == 0]
prob = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
print("P(score+ > score-) =", round(prob, 4), "| AUC =", round(M.roc_auc_score(yt, p), 4), "| paires :", len(pos) * len(neg))
# --- seuils
for t in [0.1, 0.2, 0.3, 0.5]:
    yh = (p >= t).astype(int)
    print(f"seuil {t:.1f} : alertes {yh.sum():4d}  précision {M.precision_score(yt, yh):.3f}  rappel {M.recall_score(yt, yh):.3f}  F1 {M.f1_score(yt, yh):.3f}")
```
<!--sortie-->
```text
tn fp fn tp : 1996 67 174 163 | positifs 337 négatifs 2063
exactitude 0.8996 | précision 0.7087 | rappel 0.4837 | spécificité 0.9675
F1 0.575 | F2 0.5165 | F0.5 0.6484 | MCC 0.5325 | exactitude du modèle « jamais de départ » 0.8596
P(score+ > score-) = 0.8971 | AUC = 0.8971 | paires : 695231
seuil 0.1 : alertes  692  précision 0.399  rappel 0.819  F1 0.536
seuil 0.2 : alertes  460  précision 0.517  rappel 0.706  F1 0.597
seuil 0.3 : alertes  350  précision 0.603  rappel 0.626  F1 0.614
seuil 0.5 : alertes  230  précision 0.709  rappel 0.484  F1 0.575
```

### 5.1.2 La matrice de confusion et ses dérivés

Fixons un seuil. Chaque client tombe dans l'une des quatre cases du tableau croisant la réalité et la prédiction :

| | Prédit : fidèle | Prédit : partant |
|---|---|---|
| **Réel : fidèle** | vrais négatifs (VN) | faux positifs (FP), les *fausses alertes* |
| **Réel : partant** | faux négatifs (FN), les *départs manqués* | vrais positifs (VP) |

**Un exemple entièrement à la main.** Sur 1 000 clients, 140 vont partir. Le modèle émet 120 alertes, dont 84 sont justes. Il y a donc VP = 84, FP = 120 − 84 = 36, FN = 140 − 84 = 56 et VN = 1 000 − 84 − 36 − 56 = 824. À partir de ces quatre nombres :

- l'**exactitude** (*accuracy*) est la part de bonnes réponses : $\dfrac{VP+VN}{n}=\dfrac{84+824}{1000}=0{,}908$ ;
- la **précision** est la part d'alertes justes : $\dfrac{VP}{VP+FP}=\dfrac{84}{120}=0{,}70$ ;
- le **rappel** (*recall*, ou *sensibilité*, ou taux de vrais positifs) est la part des départs détectés : $\dfrac{VP}{VP+FN}=\dfrac{84}{140}=0{,}60$ ;
- la **spécificité** est la part des fidèles correctement laissés en paix : $\dfrac{VN}{VN+FP}=\dfrac{824}{860}\approx0{,}958$ ; son complément, $1-$ spécificité, est le **taux de fausses alertes** (FPR) ;
- le **$F_1$** est la moyenne **harmonique** de la précision et du rappel : $F_1=\dfrac{2PR}{P+R}=\dfrac{2\times0{,}7\times0{,}6}{1{,}3}\approx0{,}646$.

Le $F_1$ pondère précision et rappel également. Si manquer un départ coûte plus cher qu'une fausse alerte, on utilise sa généralisation, le **$F_\beta$** : $F_\beta=\dfrac{(1+\beta^2)\,PR}{\beta^2P+R}$. Avec $\beta=2$, le rappel compte deux fois plus que la précision ($F_2\approx0{,}618$ ici) ; avec $\beta=0{,}5$, c'est l'inverse ($F_{0,5}\approx0{,}677$).

Enfin, le **coefficient de corrélation de Matthews** (MCC) résume les quatre cases d'un seul nombre entre $-1$ et $1$ : $\text{MCC}=\dfrac{VP\cdot VN-FP\cdot FN}{\sqrt{(VP+FP)(VP+FN)(VN+FP)(VN+FN)}}$, soit $\dfrac{69\,216-2\,016}{\sqrt{120\cdot140\cdot860\cdot880}}\approx0{,}596$. C'est la corrélation entre prédiction et réalité ; elle reste informative même quand les classes sont très déséquilibrées.

> ⚠️ **Le piège de l'exactitude.** Ici, un modèle qui répondrait « personne ne part » aurait une exactitude de $860/1000=86\ \%$. Notre modèle à 90,8 % ne fait donc que quatre points de mieux, alors qu'il a détecté 60 % des départs. Quand une classe est rare, l'exactitude récompense surtout la prudence. Comparez-la toujours à celle du modèle « toujours la classe majoritaire ».

Voyons maintenant ces mesures sur le **vrai** jeu de test (2 400 clients dont 337 partants), avec le boosting et le seuil habituel de 0,5.

```python hide
# vérification de l'exemple fait à la main (1 000 clients, 140 partants, 120 alertes dont 84 justes)
VP, FP, FN, VN = 84, 36, 56, 824
P_, R_ = VP / (VP + FP), VP / (VP + FN)
print("exactitude", (VP + VN) / 1000, "| précision", P_, "| rappel", R_, "| spécificité", round(VN / (VN + FP), 4))
print("F1", round(2 * P_ * R_ / (P_ + R_), 4), "| F2", round(5 * P_ * R_ / (4 * P_ + R_), 4), "| F0.5", round(1.25 * P_ * R_ / (0.25 * P_ + R_), 4),
      "| MCC", round((VP * VN - FP * FN) / np.sqrt((VP + FP) * (VP + FN) * (VN + FP) * (VN + FN)), 4))
```
<!--sortie-->
```text
exactitude 0.908 | précision 0.7 | rappel 0.6 | spécificité 0.9581
F1 0.6462 | F2 0.6176 | F0.5 0.6774 | MCC 0.596
```

Voici les quatre cases :

| | Prédit : fidèle | Prédit : partant |
|---|---:|---:|
| **Réel : fidèle** (2 063) | 1 996 | 67 |
| **Réel : partant** (337) | 174 | 163 |

On en tire : exactitude 0,900 (contre 0,860 pour « personne ne part »), précision 0,709, rappel 0,484, spécificité 0,968, $F_1=0{,}575$, $F_2=0{,}517$, $F_{0,5}=0{,}648$ et MCC = 0,533. La lecture est limpide : quand le modèle alerte, il a raison sept fois sur dix, mais il laisse passer plus de la moitié des départs.

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score

yhat = (p >= 0.5).astype(int)                     # p : probabilités prédites du boosting sur le jeu de test
print(confusion_matrix(yt, yhat))                 # lignes : réalité ; colonnes : prédiction
print(round(precision_score(yt, yhat), 3), round(recall_score(yt, yhat), 3), round(roc_auc_score(yt, p), 3))
```
<!--sortie-->
```text
[[1996   67]
 [ 174  163]]
0.709 0.484 0.897
```

Ces mesures sont disponibles en une ligne dans `scikit-learn`. Le plus difficile est de les **lire**.

### 5.1.3 Le seuil change tout

Le seuil de 0,5 n'a rien de sacré : il n'est « naturel » que si fausses alertes et départs manqués coûtent pareil. Voyons ce que devient la même sortie du modèle pour d'autres seuils :

| Seuil | Alertes | Précision | Rappel | $F_1$ |
|---:|---:|---:|---:|---:|
| 0,1 | 692 | 0,399 | 0,819 | 0,536 |
| 0,2 | 460 | 0,517 | 0,706 | 0,597 |
| 0,3 | 350 | 0,603 | 0,626 | 0,614 |
| 0,5 | 230 | 0,709 | 0,484 | 0,575 |

En abaissant le seuil, on signale plus de clients : le **rappel monte** (on détecte plus de départs) mais la **précision baisse** (plus de fausses alertes). C'est un **compromis**, pas un réglage à optimiser une fois pour toutes. Le $F_1$ est maximal autour de 0,3, mais ce « maximum » ne dit rien de ce qui compte vraiment pour la boutique ; nous y reviendrons en 5.1.7 en passant aux coûts.

> 💡 **Ce qu'il faut retenir du seuil.** Le même modèle peut être un détecteur prudent (précision 71 %, rappel 48 %) ou un détecteur large (précision 40 %, rappel 82 %). Comparer deux modèles à un seuil fixé arbitrairement mélange la qualité du score et le choix du seuil. Pour juger le **score** seul, il faut des mesures qui balaient tous les seuils.

### 5.1.4 La courbe ROC et l'AUC

La **courbe ROC** (*Receiver Operating Characteristic*) balaie tous les seuils possibles. Pour chaque seuil $t$, elle place un point d'abscisse le taux de fausses alertes $\mathrm{FPR}(t)$ et d'ordonnée le rappel $\mathrm{TPR}(t)$. Un seuil très élevé ne signale personne : on est en $(0,0)$. Un seuil nul signale tout le monde : on est en $(1,1)$. Entre les deux, plus la courbe se rapproche du coin supérieur gauche $(0,1)$, meilleur est le score ; la diagonale correspond au hasard.

```python hide
# --- courbes ROC et PR des trois modèles
couleur = {"logistique": "#2a78d6", "forêt": "#1baf7a", "boosting": "#eb6834"}
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.3))
for k, pk in P.items():
    f, t, _ = M.roc_curve(yt, pk); ax[0].plot(f, t, color=couleur[k], lw=1.8)
    r_, p_, _ = M.precision_recall_curve(yt, pk); ax[1].plot(r_, p_, color=couleur[k], lw=1.8)
    ax[0].text(0.5, {"logistique": 0.16, "forêt": 0.24, "boosting": 0.32}[k], f"{k} (AUC {M.roc_auc_score(yt, pk):.3f})", color=couleur[k], fontsize=9)
    ax[1].text(0.17, {"logistique": 0.20, "forêt": 0.27, "boosting": 0.34}[k], f"{k} (AP {M.average_precision_score(yt, pk):.3f})", color=couleur[k], fontsize=9)
ax[0].plot([0, 1], [0, 1], color="#898781", lw=1, ls="--"); ax[0].text(0.74, 0.62, "hasard", color="#898781", fontsize=9)
ax[1].axhline(yt.mean(), color="#898781", lw=1, ls="--"); ax[1].text(0.17, yt.mean() + 0.012, f"hasard : {yt.mean():.2f}", color="#898781", fontsize=9)
ax[0].set_xlabel("taux de fausses alertes (1 − spécificité)"); ax[0].set_ylabel("rappel (taux de vrais positifs)"); ax[0].set_title("Courbe ROC")
ax[1].set_xlabel("rappel"); ax[1].set_ylabel("précision"); ax[1].set_title("Courbe précision-rappel")
plt.tight_layout(); plt.savefig("figures/ch05-roc-pr.png", dpi=200, bbox_inches="tight"); plt.close()
# --- ROC insensible à la prévalence, PR non : on multiplie les négatifs par 10 (poids)
w = np.where(yt == 0, 10.0, 1.0)
print("AUC :", round(M.roc_auc_score(yt, p), 4), "->", round(M.roc_auc_score(yt, p, sample_weight=w), 4),
      "| AP :", round(M.average_precision_score(yt, p), 4), "->", round(M.average_precision_score(yt, p, sample_weight=w), 4),
      "| prévalence :", round(yt.mean(), 3), "->", round(float((w * yt).sum() / w.sum()), 3))
# --- log-loss et Brier à la main
eps = 1e-15; pc = np.clip(p, eps, 1 - eps)
print("log-loss à la main", round(float(-(yt * np.log(pc) + (1 - yt) * np.log(1 - pc)).mean()), 4), "| Brier à la main", round(float(((p - yt) ** 2).mean()), 4),
      "| Brier du modèle constant", round(float(((yt.mean() - yt) ** 2).mean()), 4), "| log-loss constant", round(float(-(yt.mean() * np.log(yt.mean()) + (1 - yt.mean()) * np.log(1 - yt.mean()))), 4))
```
<!--sortie-->
```text
AUC : 0.8971 -> 0.8971 | AP : 0.6496 -> 0.2343 | prévalence : 0.14 -> 0.016
log-loss à la main 0.2548 | Brier à la main 0.0758 | Brier du modèle constant 0.1207 | log-loss constant 0.4057
```

![Courbes ROC (à gauche) et précision-rappel (à droite) des trois modèles sur le jeu de test. Le boosting domine, mais l'écart est bien plus lisible sur la courbe précision-rappel.](figures/ch05-roc-pr.png)

**L'aire sous la courbe ROC** (AUC, *Area Under the Curve*) résume la courbe en un nombre entre 0,5 (hasard) et 1 (classement parfait). Elle a une interprétation probabiliste remarquable.

> 📐 **Démonstration : l'AUC est une probabilité.** Notons $S^+$ le score d'un client qui part tiré au hasard et $S^-$ celui d'un client fidèle tiré au hasard, indépendamment. Pour un seuil $t$, $\mathrm{TPR}(t)=P(S^+>t)$ et $\mathrm{FPR}(t)=P(S^->t)$. Quand $t$ parcourt les valeurs de la plus grande à la plus petite, $\mathrm{FPR}$ augmente de $0$ à $1$, et sa « vitesse » est la densité $f^-$ de $S^-$ : $d\,\mathrm{FPR}=-f^-(t)\,dt$. Donc
> $$\mathrm{AUC}=\int \mathrm{TPR}\;d\mathrm{FPR}=\int_{-\infty}^{+\infty}P(S^+>t)\,f^-(t)\,dt=P(S^+>S^-),$$
> la dernière égalité venant de la formule des probabilités totales en conditionnant par la valeur $S^-=t$. (En cas d'égalité de scores, on compte une demi-paire.) $\blacksquare$

**L'AUC est donc la probabilité qu'un client qui part ait un score plus élevé qu'un client qui reste.** Une AUC de 0,90 signifie : si l'on prend un partant et un fidèle au hasard, le modèle les classe dans le bon ordre neuf fois sur dix. Sur notre jeu de test, il y a $337\times2\,063=695\,231$ paires (partant, fidèle) ; en les comparant une à une, on trouve exactement la même valeur que le calcul de l'AUC : **0,8971**.

Ce résultat est la même chose que la **statistique $U$ du test de Mann-Whitney** (volume I, section 3.7.2) : $\mathrm{AUC}=U/(n^+n^-)$. Tester si deux modèles ont la même AUC, c'est comparer des rangs.

> ⚠️ **L'AUC ne dit rien de la calibration ni du seuil.** Deux scores qui rangent les clients dans le même ordre ont exactement la même AUC, même si l'un annonce 1 % et l'autre 90 % pour le même client. L'AUC mesure le **classement**, pas la justesse des probabilités (voir 5.2).

### 5.1.5 Précision-rappel : ce que la ROC ne voit pas

Sur la courbe de droite de la figure, on trace la **précision en fonction du rappel**. Son résumé est la **précision moyenne** (*average precision*, AP) : $\mathrm{AP}=\sum_n(R_n-R_{n-1})P_n$, la moyenne des précisions obtenues à chaque nouveau départ détecté. Le « hasard » n'est pas une diagonale : c'est une droite horizontale à hauteur de la **prévalence** (14 % ici).

Pourquoi deux courbes ? Parce qu'elles ne réagissent pas de la même façon quand les positifs sont rares. La ROC compare des **taux** calculés séparément parmi les positifs et parmi les négatifs ; la précision, elle, mélange les deux populations : sa valeur dépend du **nombre de négatifs**. Une expérience le montre bien. Multiplions (par un poids) le nombre de clients fidèles par 10, sans changer les scores : la prévalence tombe de 14 % à 1,6 %.

| | Avant | Après (négatifs × 10) |
|---|---:|---:|
| Prévalence | 0,140 | 0,016 |
| **AUC** | 0,8971 | **0,8971** |
| **Précision moyenne** | 0,6496 | **0,2343** |

L'AUC n'a pas bougé d'un millième ; la précision moyenne s'est effondrée. Elle a raison : avec 10 fois plus de fidèles, une alerte a beaucoup plus de chances d'être une fausse alerte. La ROC rend ce modèle « aussi bon qu'avant » parce qu'elle regarde le classement ; la courbe précision-rappel rend compte de ce que l'on vivra en réalité, à savoir une montagne de fausses alertes.

> 💡 **Règle pratique.** Quand les positifs sont rares (fraude à 1 %, départ à 5 %…) et que ce sont eux qui intéressent, **regardez la courbe précision-rappel**. L'AUC reste pratique pour comparer des classements, mais elle peut rester élevée (0,95 !) pour un modèle dont 90 % des alertes sont fausses.

### 5.1.6 Juger les probabilités : log-loss et score de Brier

Les mesures précédentes ne regardent que l'**ordre** des scores. Si l'on veut utiliser la probabilité elle-même (pour calculer un coût attendu, par exemple), il faut une mesure qui juge sa **justesse**. Deux sont standard. Pour $n$ clients de probabilités prédites $\hat p_i$ et de résultats $y_i\in\{0,1\}$ :

$$\text{log-loss}=-\frac1n\sum_i\bigl[y_i\ln\hat p_i+(1-y_i)\ln(1-\hat p_i)\bigr],\qquad \text{Brier}=\frac1n\sum_i(\hat p_i-y_i)^2.$$

La log-loss est la **vraisemblance négative** : c'est ce que minimise la régression logistique (volume II, section 2.2). Elle punit très fort un modèle qui annonce « 1 % » pour un événement qui arrive. Le Brier est l'erreur quadratique moyenne des probabilités : plus doux, mais plus robuste.

Ces deux mesures sont des **règles de score propres** : en espérance, elles sont minimisées en annonçant la **vraie** probabilité. Pour le Brier, c'est immédiat. Si la vraie probabilité d'un départ, pour un type de client, est $q$, et que l'on annonce $p$, alors $E[(p-Y)^2]=(p-q)^2+q(1-q)$ : le premier terme s'annule exactement pour $p=q$, et le second est la part d'incertitude irréductible. Impossible de « tricher » en exagérant ou en minimisant.

Il faut un point de repère. Le modèle constant, qui annonce 14 % à tout le monde, a un Brier de $0{,}14\times0{,}86\approx0{,}1207$ et une log-loss de 0,4057. Notre boosting obtient 0,0758 et 0,2548, soit un **gain de 37 % sur le Brier** (le « score de compétence » $1-0{,}0758/0{,}1207$). La régression logistique est à 0,0872 et 0,2886 : meilleure que le hasard, moins bonne que la forêt (0,0808 ; 0,2687) et que le boosting. L'ordre est le même qu'avec l'AUC, mais ce n'est pas une règle : on verra en 5.2 des modèles dont l'AUC est bonne et le Brier mauvais.

### 5.1.7 Choisir le seuil par les coûts

Voici enfin la manière de choisir un seuil qui ait un sens. La gérante veut proposer une offre de rétention aux clients à risque. Chaque contact coûte 5 €. Un client contacté qui allait partir est « sauvé » avec une probabilité de 40 %, et un client sauvé vaut 60 € de marge future. Pour un client dont la probabilité de départ est $p$, le **gain net attendu** d'un contact est

$$g(p)=p\times0{,}4\times60-5=24\,p-5.$$

> 📐 **Le seuil optimal.** Il faut contacter si et seulement si $g(p)>0$, c'est-à-dire si $p>\dfrac{5}{24}\approx0{,}208$. Plus généralement, avec un coût de contact $c$, une probabilité de succès $s$ et une valeur $V$, le seuil optimal est $t^\star=\dfrac{c}{sV}$. Il ne dépend que de l'économie du problème, pas du modèle. (Sous la forme classique des « coûts de mauvaise classification », $t^\star=\dfrac{C_{FP}}{C_{FP}+C_{FN}}$.)

Cette formule suppose que $p$ est une **vraie** probabilité : il faut donc un modèle calibré (section 5.2). Vérifions-la sur le jeu de test, en comptant pour chaque seuil le gain net réalisé :

```python hide
# --- choisir un seuil à partir des coûts : contact = 5 €, sauvetage d'un partant = 40 % de chances, valeur 60 € -> gain attendu d'un contact : 24 p - 5
cout_contact, p_succes, valeur = 5.0, 0.4, 60.0
def gain_net(t, score=p):
    contacte = score >= t
    return float((p_succes * valeur * yt[contacte]).sum() - cout_contact * contacte.sum())
t_theo = cout_contact / (p_succes * valeur)
grille = np.round(np.arange(0.02, 0.80, 0.01), 2)
gains = np.array([gain_net(t) for t in grille])
t_best = grille[gains.argmax()]
print("seuil théorique c/(s V) =", round(t_theo, 4), "| seuil optimal sur la grille =", t_best, "| gain max =", round(gains.max(), 1))
for t in [0.1, 0.2, 0.208, 0.3, 0.5]:
    print(f"seuil {t:.3f} : contacts {int((p >= t).sum()):4d}  gain net {gain_net(t):8.1f} €")
print("contacter tout le monde :", round(gain_net(0.0), 1), "€ | ne contacter personne : 0 €")
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(grille, gains, color="#2a78d6", lw=2); ax.axvline(t_theo, color="#eb6834", ls="--", lw=1.3); ax.axhline(0, color="#898781", lw=0.8)
ax.text(t_theo + 0.01, gains.min() * 0.15, f"seuil théorique {t_theo:.3f}", color="#eb6834", fontsize=9)
ax.plot([t_best], [gains.max()], "o", color="#eb6834"); ax.set_xlabel("seuil sur la probabilité de départ"); ax.set_ylabel("gain net de la campagne (€)")
ax.set_title("Le seuil se choisit sur les coûts, pas sur 0,5"); plt.tight_layout(); plt.savefig("figures/ch05-seuil-cout.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
seuil théorique c/(s V) = 0.2083 | seuil optimal sur la grille = 0.18 | gain max = 3473.0
seuil 0.100 : contacts  692  gain net   3164.0 €
seuil 0.200 : contacts  460  gain net   3412.0 €
seuil 0.208 : contacts  446  gain net   3386.0 €
seuil 0.300 : contacts  350  gain net   3314.0 €
seuil 0.500 : contacts  230  gain net   2762.0 €
contacter tout le monde : -3912.0 € | ne contacter personne : 0 €
```

| Seuil | Clients contactés | Gain net |
|---:|---:|---:|
| 0,10 | 692 | 3 164 € |
| 0,20 | 460 | 3 412 € |
| 0,208 (théorique) | 446 | 3 386 € |
| 0,30 | 350 | 3 314 € |
| 0,50 (habituel) | 230 | 2 762 € |
| contacter tout le monde | 2 400 | −3 912 € |

![Gain net de la campagne selon le seuil. Le maximum observé est atteint vers 0,18 ; la courbe est plate entre 0,15 et 0,30.](figures/ch05-seuil-cout.png)

Le message est triple. D'abord, **le seuil de 0,5 laisse environ 700 € sur la table** (2 762 € contre 3 473 € au meilleur seuil de la grille, 0,18). Ensuite, le seuil théorique (0,208) donne 3 386 €, soit 87 € de moins que le maximum observé : la courbe est plate autour de l'optimum, et l'optimum exact sur un jeu de 2 400 clients est bruité. Enfin, **contacter tout le monde perd de l'argent** : c'est ce que fait, en pratique, une campagne sans modèle.

> ⚠️ **Le gain mesuré sur le jeu de test sert à illustrer, pas à choisir.** Pour choisir le seuil dans un vrai projet, on utilise le jeu de **calibration** (ou la validation croisée), puis on mesure une dernière fois sur le jeu de test.

### 5.1.8 Gain et lift : la lecture du marketing

Une campagne n'a souvent pas de seuil : elle a un **budget** (« nous pouvons contacter 20 % des clients »). On classe alors les clients par score décroissant, on les découpe en déciles, et on regarde où se trouvent les partants.

```python hide
# --- gain et lift par déciles
ordre = np.argsort(-p); ys = yt[ordre]; n = len(ys)
dec = pd.DataFrame({"décile": np.repeat(np.arange(1, 11), n // 10), "y": ys[: (n // 10) * 10]})
tab = dec.groupby("décile")["y"].agg(clients="size", partants="sum")
tab["taux"] = tab["partants"] / tab["clients"]; tab["lift"] = tab["taux"] / yt.mean(); tab["cumul_capturé"] = tab["partants"].cumsum() / tab["partants"].sum()
print(tab.round(3).to_string())
fig, ax = plt.subplots(figsize=(6.5, 4.3))
for k, pk in P.items():
    o = np.argsort(-pk); cum = np.cumsum(yt[o]) / yt.sum(); ax.plot(np.arange(1, n + 1) / n, cum, color=couleur[k], lw=1.8)
ax.plot([0, 1], [0, 1], color="#898781", ls="--", lw=1); ax.set_xlabel("part des clients contactés (classés par score)"); ax.set_ylabel("part des partants atteints")
ax.text(0.55, 0.40, "boosting", color=couleur["boosting"], fontsize=9); ax.text(0.55, 0.32, "forêt", color=couleur["forêt"], fontsize=9); ax.text(0.55, 0.24, "logistique", color=couleur["logistique"], fontsize=9)
ax.set_title("Courbe de gain"); plt.tight_layout(); plt.savefig("figures/ch05-gain.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
        clients  partants   taux   lift  cumul_capturé
décile                                                
1           240       168  0.700  4.985          0.499
2           240        76  0.317  2.255          0.724
3           240        36  0.150  1.068          0.831
4           240        27  0.112  0.801          0.911
5           240        10  0.042  0.297          0.941
6           240        11  0.046  0.326          0.973
7           240         6  0.025  0.178          0.991
8           240         1  0.004  0.030          0.994
9           240         2  0.008  0.059          1.000
10          240         0  0.000  0.000          1.000
```

```python hide
# --- multiclasses : prédire la classe latente (segment) à partir des comportements
seg = c["segment_vrai"]
gm = HistGradientBoostingClassifier(random_state=0).fit(Xtr, seg.loc[Xtr.index])
ps = gm.predict(Xte); ys_ = seg.loc[Xte.index].to_numpy()
print("matrice (lignes = vrai segment) :\n", M.confusion_matrix(ys_, ps))
print("exactitude", round(M.accuracy_score(ys_, ps), 4), "| F1 macro", round(M.f1_score(ys_, ps, average="macro"), 4), "| F1 micro", round(M.f1_score(ys_, ps, average="micro"), 4),
      "| F1 pondéré", round(M.f1_score(ys_, ps, average="weighted"), 4))
print("rappel par classe", np.round(M.recall_score(ys_, ps, average=None), 3), "| effectifs", np.bincount(ys_))
# --- régression : dépense à 6 mois (34 % de zéros)
yr = c["depense_6m"]
gr = __import__("sklearn.ensemble", fromlist=["HistGradientBoostingRegressor"]).HistGradientBoostingRegressor(max_iter=150, random_state=0).fit(Xtr, yr.loc[Xtr.index])
yt_r = yr.loc[Xte.index].to_numpy(); pr = np.clip(gr.predict(Xte), 0, None)
mae = M.mean_absolute_error(yt_r, pr); rmse = M.mean_squared_error(yt_r, pr) ** 0.5; r2 = M.r2_score(yt_r, pr)
mu = yr.loc[Xtr.index].mean()
print("part de zéros", round((yt_r == 0).mean(), 3), "| moyenne", round(yt_r.mean(), 1), "| écart-type", round(yt_r.std(), 1))
print("MAE", round(mae, 2), "RMSE", round(rmse, 2), "R2", round(r2, 4), "| référence (moyenne d'entraînement) MAE", round(M.mean_absolute_error(yt_r, np.full_like(yt_r, mu)), 2),
      "RMSE", round(M.mean_squared_error(yt_r, np.full_like(yt_r, mu)) ** 0.5, 2), "| référence (médiane =", float(yr.loc[Xtr.index].median()), ") MAE", round(M.mean_absolute_error(yt_r, np.full_like(yt_r, yr.loc[Xtr.index].median())), 2))
pos_ = yt_r > 0
print("MAPE sur les dépenses > 0 :", round(float((np.abs(yt_r[pos_] - pr[pos_]) / yt_r[pos_]).mean()), 3), "| nb de zéros (MAPE impossible) :", int((~pos_).sum()),
      "| sMAPE :", round(float((2 * np.abs(yt_r - pr) / (np.abs(yt_r) + np.abs(pr) + 1e-9)).mean()), 3))
e2 = (yt_r - pr) ** 2; top = np.sort(e2)[::-1]
print("part de l'erreur quadratique due aux 1 % pires erreurs :", round(float(top[: len(top) // 100].sum() / top.sum()), 3), "| part de l'erreur absolue :", round(float(np.sort(np.abs(yt_r - pr))[::-1][: len(top) // 100].sum() / np.abs(yt_r - pr).sum()), 3))
gq = __import__("sklearn.ensemble", fromlist=["HistGradientBoostingRegressor"]).HistGradientBoostingRegressor(loss="quantile", quantile=0.9, max_iter=150, random_state=0).fit(Xtr, yr.loc[Xtr.index])
q90 = np.clip(gq.predict(Xte), 0, None)
def pinball(yv, qv, tau): return float(np.mean(np.maximum(tau * (yv - qv), (tau - 1) * (yv - qv))))
print("quantile 0,9 : perte pinball du modèle quantile", round(pinball(yt_r, q90, 0.9), 3), "| du modèle de la moyenne", round(pinball(yt_r, pr, 0.9), 3), "| part des y <= q90 prédit :", round(float((yt_r <= q90).mean()), 3), "| du modèle moyen :", round(float((yt_r <= pr).mean()), 3))
```
<!--sortie-->
```text
matrice (lignes = vrai segment) :
 [[873  44   0  19]
 [ 30 655   5  13]
 [  0   1 478   0]
 [ 31   7   0 244]]
exactitude 0.9375 | F1 macro 0.9328 | F1 micro 0.9375 | F1 pondéré 0.9374
rappel par classe [0.933 0.932 0.998 0.865] | effectifs [936 703 479 282]
part de zéros 0.358 | moyenne 83.2 | écart-type 125.7
MAE 59.21 RMSE 98.61 R2 0.385 | référence (moyenne d'entraînement) MAE 83.5 RMSE 125.74 | référence (médiane = 41.94 ) MAE 75.11
MAPE sur les dépenses > 0 : 0.597 | nb de zéros (MAPE impossible) : 860 | sMAPE : 1.073
part de l'erreur quadratique due aux 1 % pires erreurs : 0.352 | part de l'erreur absolue : 0.096
quantile 0,9 : perte pinball du modèle quantile 17.189 | du modèle de la moyenne 29.007 | part des y <= q90 prédit : 0.858 | du modèle moyen : 0.612
```

| Décile | Clients | Partants | Taux de départ | Lift | Part cumulée des partants |
|---:|---:|---:|---:|---:|---:|
| 1 | 240 | 168 | 70,0 % | 4,99 | 49,9 % |
| 2 | 240 | 76 | 31,7 % | 2,26 | 72,4 % |
| 3 | 240 | 36 | 15,0 % | 1,07 | 83,1 % |
| 4 | 240 | 27 | 11,2 % | 0,80 | 91,1 % |
| 5 | 240 | 10 | 4,2 % | 0,30 | 94,1 % |
| 6 | 240 | 11 | 4,6 % | 0,33 | 97,3 % |
| 7 | 240 | 6 | 2,5 % | 0,18 | 99,1 % |
| 8 | 240 | 1 | 0,4 % | 0,03 | 99,4 % |
| 9 | 240 | 2 | 0,8 % | 0,06 | 100,0 % |
| 10 | 240 | 0 | 0,0 % | 0,00 | 100,0 % |

Le **lift** d'un décile est son taux de départ divisé par le taux moyen (14 %) : le premier décile « vaut » 4,99 fois un tirage au hasard. La dernière colonne donne la **courbe de gain** : **en contactant 20 % des clients seulement, on atteint 72 % des partants**. Aucun partant dans le dernier décile : le modèle repère bien les clients qui ne partiront pas, ce qui permet de ne pas les déranger.

![Courbe de gain : part des partants atteinte en fonction de la part de clients contactés, classés par score. La diagonale est le ciblage au hasard.](figures/ch05-gain.png)

> 💡 **À quoi sert cette lecture ?** Elle parle le langage du budget : « pour 20 % de l'effort, 72 % du résultat ». Elle ne demande aucun seuil, et elle se compare directement à un tirage au hasard, ce qui la rend lisible par des non-spécialistes.

### 5.1.9 Plus de deux classes

Quand la cible a plus de deux modalités, on garde la matrice de confusion (une ligne par classe réelle), et on **moyenne** les métriques par classe de trois façons :

- la moyenne **macro** calcule la métrique par classe, puis moyenne sans pondération : chaque classe pèse autant ;
- la moyenne **micro** additionne tous les VP, FP, FN avant de calculer : chaque *client* pèse autant (pour un problème à une seule étiquette par client, le $F_1$ micro est égal à l'exactitude) ;
- la moyenne **pondérée** moyenne par classe, avec des poids proportionnels aux effectifs.

Pour illustrer, tentons de reconnaître à quel **segment** appartient un client (4 segments latents simulés, dont les proportions sont 39, 29, 20 et 12 %) à partir de ses comportements. Ce n'est qu'une démonstration : ailleurs, ce segment ne sert jamais d'entrée.

| Segment réel \ prédit | 0 | 1 | 2 | 3 | Rappel |
|---|---:|---:|---:|---:|---:|
| 0 (936 clients) | 873 | 44 | 0 | 19 | 0,933 |
| 1 (703) | 30 | 655 | 5 | 13 | 0,932 |
| 2 (479) | 0 | 1 | 478 | 0 | 0,998 |
| 3 (282) | 31 | 7 | 0 | 244 | 0,865 |

L'exactitude est de 0,9375, le $F_1$ micro lui est égal (0,9375), le $F_1$ pondéré vaut 0,9374 et le $F_1$ **macro** 0,9328. Le macro est le plus bas parce qu'il donne autant de poids à la plus petite classe (les « grands paniers », 12 % des clients, rappel 0,865) qu'à la plus grande. **Si une classe rare est précisément celle qui vous importe, c'est le macro, ou le rappel par classe, qu'il faut regarder.**

### 5.1.10 Régression : choisir sa perte

Pour une cible numérique, les métriques mesurent l'écart entre la valeur prédite $\hat y_i$ et la valeur réelle $y_i$. Prenons la **dépense des six mois suivants** (en euros). Elle est difficile à prédire : 36 % des clients du jeu de test ne dépensent rien, et le reste a une distribution très étalée (moyenne 83,2 €, écart-type 125,7 €).

| Mesure | Formule | Remarque |
|---|---|---|
| **MAE** (erreur absolue moyenne) | $\frac1n\sum\lvert y_i-\hat y_i\rvert$ | en euros ; robuste aux valeurs extrêmes ; cible la **médiane** |
| **RMSE** (racine de l'erreur quadratique) | $\sqrt{\frac1n\sum(y_i-\hat y_i)^2}$ | en euros ; punit les gros écarts ; cible la **moyenne** |
| **$R^2$** | $1-\frac{\sum(y_i-\hat y_i)^2}{\sum(y_i-\bar y)^2}$ | part de variance expliquée par rapport à la moyenne |
| **MAPE** | $\frac1n\sum\frac{\lvert y_i-\hat y_i\rvert}{\lvert y_i\rvert}$ | erreur relative ; **indéfinie si $y_i=0$**, asymétrique |
| **Perte pinball** | $\max\bigl(\tau(y-q),\,(\tau-1)(y-q)\bigr)$ | juge un **quantile** $q$ de niveau $\tau$ |

Un gradient boosting entraîné pour minimiser l'erreur quadratique obtient sur le jeu de test **MAE = 59,2 €, RMSE = 98,6 € et $R^2=0{,}385$**. Pour savoir si c'est bien, il faut des références : prédire la moyenne d'entraînement à tout le monde donne MAE = 83,5 € et RMSE = 125,7 € ; prédire la médiane (41,9 €) donne MAE = 75,1 €. Le modèle réduit donc l'erreur absolue de 29 % par rapport à la moyenne. On vérifie la cohérence du $R^2$ : $1-(98{,}6/125{,}7)^2\approx0{,}385$.

> 💡 **MAE et RMSE ne mesurent pas la même chose.** Le RMSE est toujours supérieur ou égal au MAE, et l'écart entre les deux dit si les erreurs sont régulières ou concentrées. Ici, les 1 % de plus grosses erreurs représentent **35 %** de l'erreur quadratique mais seulement **10 %** de l'erreur absolue. Si quelques gros clients mal prédits sont l'enjeu, le RMSE est le bon juge ; si l'on veut juger le client « typique », c'est le MAE.

**Le piège du MAPE.** Il est calculé en divisant par la valeur réelle : impossible pour les 860 clients du jeu de test dont la dépense est nulle. En se limitant aux dépenses positives, on trouve 60 %, un nombre qui dépend beaucoup de la façon dont on traite les petits montants. Quant au sMAPE (qui divise par la moyenne de $\lvert y\rvert$ et $\lvert\hat y\rvert$), il vaut ici 1,07, car chaque prédiction positive d'une dépense nulle donne une erreur de 200 %. **Sur une cible qui contient des zéros, évitez les erreurs relatives.**

**Prédire un quantile.** Parfois, on ne veut pas la valeur la plus probable mais une valeur « haute » : *quelle dépense sera dépassée dans seulement 10 % des cas ?* (pour dimensionner un stock, par exemple). On entraîne alors le modèle avec la **perte pinball** de niveau $\tau=0{,}9$, qui pénalise davantage de sous-estimer que de surestimer. Le modèle quantile obtient une perte pinball de 17,2, contre 29,0 pour le modèle de la moyenne utilisé comme prédicteur de quantile. Mais il faut vérifier sa **couverture** : seuls 85,8 % des clients ont une dépense inférieure au quantile annoncé, et non 90 %. (Le modèle de la moyenne, lui, en couvre 61,2 %.) Un quantile estimé n'est pas garanti : en 5.5, on le réparera.

> ✅ **À retenir.**
> - L'exactitude se compare toujours au modèle « classe majoritaire » ; avec des classes rares, préférez rappel, précision, $F_\beta$, MCC.
> - L'**AUC** est la probabilité qu'un positif ait un score supérieur à celui d'un négatif (statistique de Mann-Whitney) : elle mesure le classement, pas la justesse des probabilités, et elle ne voit pas la prévalence.
> - Avec des positifs rares, la **courbe précision-rappel** et l'AP disent ce que l'AUC cache.
> - La **log-loss** et le **Brier** jugent les probabilités ; ce sont des règles de score propres.
> - Le seuil se déduit des **coûts** : $t^\star=c/(sV)$ pour une campagne, à condition que les probabilités soient calibrées.
> - Le **lift** et la courbe de gain parlent le langage du budget.
> - En régression, **MAE** (médiane) et **RMSE** (moyenne) répondent à des questions différentes ; évitez le MAPE avec des zéros ; la perte **pinball** juge un quantile.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.4, exercices 5.1 à 5.6.
