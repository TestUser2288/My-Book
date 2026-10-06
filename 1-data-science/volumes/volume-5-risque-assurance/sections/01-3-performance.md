## 1.3 Mesures de performance : Gini, KS, ROC

Un score se juge sur quatre questions distinctes, que l'on confond trop souvent : **classe-t-il bien** (discrimination : AUC, Gini, KS), **annonce-t-il de bonnes probabilités** (calibration), **reste-t-il bon quand la clientèle change** (stabilité), et **avec quelle incertitude** connaît-on ces mesures ? Cette section donne à chaque question son outil, avec les démonstrations qui permettent de les relire, puis un détour par un jeu **réel** pour ne pas croire que tout se passe toujours comme dans nos données simulées.

### 1.3.1 La courbe ROC et l'AUC

Pour un seuil de risque $c$, un dossier est « alerté » si son score de risque dépasse $c$. Deux taux décrivent la règle :

- le **taux de vrais positifs** (TPR, la *sensibilité*) : la part des **mauvais** qui sont alertés ;
- le **taux de faux positifs** (FPR) : la part des **bons** qui sont alertés à tort.

La courbe **ROC** (*receiver operating characteristic*) trace le TPR en fonction du FPR quand le seuil parcourt toutes ses valeurs. Un score aléatoire donne la diagonale ; un score parfait, un angle droit en haut à gauche. L'**AUC**, l'aire sous la courbe, a une interprétation probabiliste directe que l'on retient mieux que l'aire :

$$\text{AUC}=P(S_{\text{mauvais}}>S_{\text{bon}})+\tfrac12\,P(S_{\text{mauvais}}=S_{\text{bon}}),$$

c'est la probabilité qu'un **mauvais** tiré au hasard ait un score de risque **plus élevé** qu'un **bon** tiré au hasard. Calculons-la à la main sur six dossiers : trois mauvais (scores de risque 0,9 ; 0,6 ; 0,4) et trois bons (0,7 ; 0,3 ; 0,2). Il y a $3\times3=9$ paires (un mauvais, un bon) ; comptons celles où le mauvais a le score le plus élevé :

| mauvais | contre 0,7 | contre 0,3 | contre 0,2 | paires gagnées |
|---|---|---|---|---|
| 0,9 | oui | oui | oui | 3 |
| 0,6 | non | oui | oui | 2 |
| 0,4 | non | oui | oui | 2 |

Sept paires sur neuf : $\text{AUC}=7/9\approx0{,}778$.

### 1.3.2 Le Gini et la courbe CAP

Les risquologues préfèrent souvent le **Gini** (ou *accuracy ratio*) : $\text{Gini}=2\,\text{AUC}-1$. Il vaut 0 pour un score aléatoire et 1 pour un score parfait. Dans l'exemple, $2\times\frac79-1=\frac49\approx0{,}444$. D'où vient cette formule ? D'une autre courbe, la **CAP** (*cumulative accuracy profile*), qui classe les dossiers du plus risqué au moins risqué et trace, en fonction de la part de la population examinée, la part des mauvais **capturés**.

> 📐 **Démonstration : Gini = 2·AUC − 1.** Notons $\pi$ la proportion de mauvais dans la population. Quand on examine les dossiers dont le score dépasse un seuil, la part de la population examinée est $x=\pi\,\text{TPR}+(1-\pi)\,\text{FPR}$ et la part des mauvais capturés est $y=\text{TPR}$. L'aire sous la CAP vaut donc
> $$A_{\text{CAP}}=\int \text{TPR}\;d\bigl[\pi\,\text{TPR}+(1-\pi)\,\text{FPR}\bigr]=\pi\int \text{TPR}\,d\text{TPR}+(1-\pi)\int\text{TPR}\,d\text{FPR}=\frac\pi2+(1-\pi)\,\text{AUC}.$$
> Le score aléatoire a une aire de $\frac12$ ; le score parfait capture tous les mauvais dans les premiers $\pi$ de la population, soit une aire de $1-\frac\pi2$. Le **rapport de précision** est le rapport des aires entre le score étudié et l'aléatoire, et entre le parfait et l'aléatoire :
> $$\text{AR}=\frac{A_{\text{CAP}}-\frac12}{(1-\frac\pi2)-\frac12}=\frac{\frac\pi2+(1-\pi)\text{AUC}-\frac12}{\frac{1-\pi}{2}}=\frac{(1-\pi)(\text{AUC}-\frac12)}{\frac{1-\pi}{2}}=2\,\text{AUC}-1.$$
> Le résultat **ne dépend pas de $\pi$** : c'est ce qui permet de comparer des Gini d'un portefeuille à l'autre... sous réserve des précautions de 1.3.7.

Sur nos données, voici le Gini de la grille et les deux courbes :

```python
from sklearn.metrics import roc_auc_score, roc_curve
auc = roc_auc_score(y_te, r_grille)                  # r_grille : risque = − score
fpr, tpr, _ = roc_curve(y_te, r_grille)
print(f"AUC {auc:.3f}   Gini {2 * auc - 1:.3f}   KS {np.max(tpr - fpr):.3f}")
```
<!--sortie-->
```text
AUC 0.771   Gini 0.542   KS 0.406
```

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.8))
ax = axs[0]
for nom, v, col, ls in [("grille", r_grille, BLEU, "-"), ("logistique brute", p_brut, ORANGE, "--"), ("boosting monotone", p_gbm, VIOLET, ":")]:
    f_, t_, _ = roc_curve(y_te, v); ax.plot(f_, t_, color=col, lw=1.8, ls=ls, label=f"{nom} (AUC {roc_auc_score(y_te, v):.3f})")
ax.plot([0, 1], [0, 1], color=MUET, lw=1); ax.set_xlabel("taux de faux positifs (bons alertés)"); ax.set_ylabel("taux de vrais positifs (mauvais alertés)")
ax.set_title("Courbe ROC"); ax.legend(frameon=False, fontsize=8.5, loc="lower right")
ax = axs[1]
o = np.argsort(-r_grille); yy = y_te[o]; pi_ = y_te.mean()
x = np.r_[0, np.arange(1, len(yy) + 1) / len(yy)]; yc = np.r_[0, np.cumsum(yy) / yy.sum()]
ax.plot(x, yc, color=BLEU, lw=2, label="grille")
ax.plot([0, pi_, 1], [0, 1, 1], color=VIOLET, lw=1.3, ls="--", label="score parfait")
ax.plot([0, 1], [0, 1], color=MUET, lw=1, label="score aléatoire")
for q in (0.1, 0.2):
    k = int(q * len(yy)); ax.plot([q], [yc[k]], "o", color=ROUGE, ms=4.5); ax.annotate(f"{q:.0%} les plus risqués\n→ {yc[k]:.0%} des mauvais", (q, yc[k]), xytext=(q + 0.12, yc[k] - 0.16), fontsize=8.5, color=ENCRE, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
ax.set_xlabel("part de la population examinée (du plus risqué au moins risqué)"); ax.set_ylabel("part des mauvais capturés"); ax.set_title("Courbe CAP"); ax.legend(frameon=False, fontsize=8.5, loc="lower right")
fig.tight_layout(); fig.savefig("figures/ch01-roc-cap.png", dpi=200, bbox_inches="tight"); plt.close(fig)
c10 = float(yc[int(0.1 * len(yy))]); c20 = float(yc[int(0.2 * len(yy))])
print("NUM cap10", round(c10, 3)); print("NUM cap20", round(c20, 3))
print("NUM auc_main", round(float(auc), 4)); print("NUM gini_main", round(float(2 * auc - 1), 4)); print("NUM ks_main", round(float(np.max(tpr - fpr)), 4))
```
<!--sortie-->
```text
NUM cap10 0.384
NUM cap20 0.571
NUM auc_main 0.7712
NUM gini_main 0.5425
NUM ks_main 0.4058
```

![À gauche, courbes ROC des trois candidats du test ; à droite, courbe CAP de la grille : examiner les 10 % de dossiers les plus risqués capture une part très supérieure de 10 % des mauvais.](figures/ch01-roc-cap.png)

La courbe CAP se lit sans équation : en examinant les 10 % de dossiers que la grille juge les plus risqués, on capture **38 % des mauvais** (un score aléatoire en capturerait 10 %) ; avec 20 % des dossiers, 57 %. Les trois courbes ROC se **confondent presque** : les trois modèles de la section 1.2 sont, pour la discrimination, d'un niveau voisin.

### 1.3.3 Le KS : l'écart maximal entre bons et mauvais

La statistique de **Kolmogorov–Smirnov** mesure la plus grande distance verticale entre les fonctions de répartition des scores des bons et des mauvais :

$$\text{KS}=\max_c\,\bigl|F_{\text{mauvais}}(c)-F_{\text{bon}}(c)\bigr|=\max_c\,\bigl(\text{TPR}(c)-\text{FPR}(c)\bigr).$$

C'est la plus grande différence qu'un seuil unique puisse faire entre la part de mauvais et la part de bons captés. Le point où elle est atteinte est un **seuil naturel** de décision quand on n'a pas d'information de coûts. Le KS est très lu en banque, parce qu'il se résume en un nombre et un seuil.

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.5))
ax = axs[0]
bins = np.linspace(470, 660, 40)
ax.hist(s_te[y_te == 0], bins=bins, density=True, color=BLEU, alpha=0.6, label="bons")
ax.hist(s_te[y_te == 1], bins=bins, density=True, color=ROUGE, alpha=0.6, label="mauvais")
ax.set_xlabel("score (points)"); ax.set_ylabel("densité"); ax.set_title("Distributions du score"); ax.legend(frameon=False, fontsize=9)
ax = axs[1]
g_ = np.sort(s_te[y_te == 0]); m_ = np.sort(s_te[y_te == 1]); grid = np.linspace(470, 660, 400)
Fg = np.searchsorted(g_, grid) / len(g_); Fm = np.searchsorted(m_, grid) / len(m_)
k = int(np.argmax(np.abs(Fm - Fg)))
ax.plot(grid, Fg, color=BLEU, lw=1.8, label="bons"); ax.plot(grid, Fm, color=ROUGE, lw=1.8, label="mauvais")
ax.plot([grid[k]] * 2, [Fg[k], Fm[k]], color=ENCRE, lw=1.6)
ax.annotate(f"KS = {abs(Fm[k] - Fg[k]):.2f}\nau score {grid[k]:.0f}", (grid[k], (Fg[k] + Fm[k]) / 2), xytext=(grid[k] + 18, 0.30), fontsize=9, arrowprops=dict(arrowstyle="-", color=MUET, lw=0.8))
ax.set_xlabel("score (points)"); ax.set_ylabel("part cumulée"); ax.set_title("Fonctions de répartition et KS"); ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig("figures/ch01-ks.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM ks_score", round(float(grid[k]), 0))
```
<!--sortie-->
```text
NUM ks_score 567.0
```

![Distributions du score des bons et des mauvais (à gauche) et leurs fonctions de répartition (à droite) : le KS est l'écart vertical maximal.](figures/ch01-ks.png)

### 1.3.4 Du score à la politique d'acceptation

Un indicateur de rang ne dit pas **où couper**. La politique d'acceptation se lit dans un tableau de compromis : à chaque seuil, quelle part des demandes accepte-t-on, quel taux de défaut paie-t-on parmi les acceptés, et quel taux auraient eu les refusés ?

```python hide-code
tab = []
for seuil in (540, 560, 580, 600):
    ok = s_te >= seuil
    tab.append((seuil, ok.mean(), y_te[ok].mean(), y_te[~ok].mean()))
tab = pd.DataFrame(tab, columns=["seuil", "part acceptée", "défaut des acceptés", "défaut des refusés"]).round(4)
print(tab.to_string(index=False))
```
<!--sortie-->
```text
 seuil  part acceptée  défaut des acceptés  défaut des refusés
   540         0.9116               0.0417              0.2451
   560         0.7828               0.0312              0.1623
   580         0.5392               0.0202              0.1058
   600         0.2431               0.0154              0.0739
```

```python hide
for i, r in tab.iterrows():
    print("NUM cut", int(r["seuil"]), r["part acceptée"], r["défaut des acceptés"], r["défaut des refusés"])
```
<!--sortie-->
```text
NUM cut 540 0.9116 0.0417 0.2451
NUM cut 560 0.7828 0.0312 0.1623
NUM cut 580 0.5392 0.0202 0.1058
NUM cut 600 0.2431 0.0154 0.0739
```

Un seuil de 560 points accepte 78 % des demandes pour un taux de défaut de 3,1 % parmi les acceptés (contre 6,0 % sans score) et refuse des dossiers qui auraient fait 16 % de défauts. Monter à 600 points ramène le défaut des acceptés à 1,5 %, au prix de **refuser les trois quarts** des clients. Le bon seuil n'est pas statistique : il dépend du **coût d'un défaut** (la perte de l'exposition, section 1.5) et du **gain d'un bon client** (les intérêts), donc de la marge de la banque. L'AUC ne choisit pas le seuil, elle dit seulement si la courbe de ce compromis est bonne.

### 1.3.5 L'incertitude de la mesure

```python hide
bi = O.bootstrap_auc(y_te, r_grille, 500, 0)
print("NUM boot_lo", round(float(bi[0]), 3)); print("NUM boot_hi", round(float(bi[1]), 3)); print("NUM nb_mauvais_te", int(y_te.sum()))
```
<!--sortie-->
```text
NUM boot_lo 0.752
NUM boot_hi 0.791
NUM nb_mauvais_te 716
```

Une AUC est une **estimation** à partir de 12 000 prêts dont 716 mauvais (volume III, section 5.1 : c'est le nombre de mauvais qui compte). Quelle est sa marge d'erreur ? Un **bootstrap** (volume III, section 1.2) rééchantillonne les lignes du test avec remise et recalcule l'AUC : l'intervalle à 95 % de la grille est **[0,752 ; 0,791]**. L'incertitude est de près de **deux points d'AUC** de chaque côté, alors que les écarts entre modèles de la section 1.2 sont d'un point. C'est pourquoi l'on compare deux modèles par un **intervalle de la différence** sur des rééchantillons **appariés** (les mêmes lignes pour les deux modèles), plus étroit que chaque intervalle pris isolément.

⚠️ Il y a trois sources distinctes d'incertitude : l'**échantillon de test** (ce que mesure le bootstrap), l'**échantillon de développement** (un autre échantillon donnerait une autre grille ; on le mesure en refaisant tout le processus sur des rééchantillons de développement) et la **dérive** future de la population. Seule la première est facile à chiffrer, ce qui explique que les performances réelles soient généralement inférieures à celles du test.

### 1.3.6 Stabilité : la population change

Une grille est utilisée pendant des années. La clientèle, elle, change : la banque s'étend vers les jeunes, la conjoncture se dégrade, une campagne attire un autre profil. Le **PSI** (*population stability index*, volume IV, section 4.7) compare la distribution d'une variable, ou du score, entre la population de développement et la population actuelle :

$$\text{PSI}=\sum_{j}(p_j^{\text{actuel}}-p_j^{\text{dév.}})\,\ln\frac{p_j^{\text{actuel}}}{p_j^{\text{dév.}}}.$$

L'usage place des **repères** : moins de 0,10, la population est stable ; entre 0,10 et 0,25, un changement à examiner ; au-delà, un changement important. Ce sont des conventions, pas des lois.

Simulons un afflux de jeunes emprunteurs et de dossiers très endettés : nous tirons, dans le **jeu de test**, 6 000 prêts avec une probabilité d'autant plus forte que le client a moins de 30 ans ou un taux d'endettement supérieur à 40 %.

```python hide-code
w = np.exp(1.2 * (te["age"] < 30) + 0.8 * (te["taux_endettement"] > 0.4)); w = w / w.sum()
nv = te.sample(6000, replace=True, weights=w, random_state=3)
s_nv = G.score(nv); y_nv = nv["defaut_12m"].values
psi_tab = pd.DataFrame({"PSI": [O.psi(s_tr, s_nv, 10), O.psi(tr["age"], nv["age"], 10), O.psi(tr["taux_endettement"], nv["taux_endettement"], 10)]},
                       index=["score", "âge", "taux d'endettement"]).round(3)
print(psi_tab.to_string())
print(f"défaut observé : {y_nv.mean():.4f}   PD annoncée : {G.pd_predite(nv).mean():.4f}   AUC : {O.auc(y_nv, -s_nv):.3f}")
```
<!--sortie-->
```text
                      PSI
score               0.129
âge                 0.246
taux d'endettement  0.149
défaut observé : 0.0893   PD annoncée : 0.0873   AUC : 0.788
```

```python hide
print("NUM psi_score", psi_tab.loc["score", "PSI"]); print("NUM psi_age", psi_tab.loc["âge", "PSI"]); print("NUM psi_dti", psi_tab.loc["taux d'endettement", "PSI"])
print("NUM nv_def", round(float(y_nv.mean()), 4)); print("NUM nv_pd", round(float(G.pd_predite(nv).mean()), 4)); print("NUM nv_auc", round(O.auc(y_nv, -s_nv), 4))
```
<!--sortie-->
```text
NUM psi_score 0.129
NUM psi_age 0.246
NUM psi_dti 0.149
NUM nv_def 0.0893
NUM nv_pd 0.0873
NUM nv_auc 0.7875
```

Le PSI du score dépasse 0,10 et celui de l'âge dépasse 0,20 : l'alarme sonne. Pourtant, le **pouvoir de classement tient** (l'AUC de 0,788 est du niveau de celle du test), et la probabilité annoncée de défaut (8,7 %) reste proche du défaut observé (8,9 %) : la grille a **vu venir** le risque supplémentaire, parce que les nouveaux clients lui ressemblent par leurs variables. Ce qui casserait le score, c'est un changement de la **relation** entre les variables et le défaut (la dérive du concept du volume IV, section 4.7), que le PSI ne voit pas.

### 1.3.7 Calibration : la probabilité annoncée est-elle la bonne ?

La calibration se contrôle **classe de risque par classe de risque**. Les banques regroupent leurs clients en quelques **notes** (une *échelle maîtresse*) auxquelles est attachée une probabilité de défaut. Découpons les dossiers du test en sept notes selon la PD annoncée, et testons, pour chaque note, l'hypothèse « la probabilité de défaut vraie est celle qui est annoncée » par un **test binomial** : sous l'hypothèse, le nombre de défauts d'une note de $n$ dossiers suit une loi binomiale $\mathcal{B}(n,\text{PD})$.

```python hide-code
from scipy.stats import binomtest, chi2
bornes_pd = [0, 0.01, 0.02, 0.035, 0.06, 0.10, 0.20, 1.0]
pp = G.pd_predite(te)
note = np.digitize(pp, bornes_pd[1:-1]) + 1
lignes = []
for k in range(1, 8):
    m = note == k; n_k = int(m.sum()); d_k = int(y_te[m].sum()); p_k = float(pp[m].mean())
    lignes.append((k, n_k, p_k, d_k / n_k, binomtest(d_k, n_k, p_k).pvalue))
tn = pd.DataFrame(lignes, columns=["note", "dossiers", "PD annoncée", "défaut observé", "p-valeur"]).round(4)
print(tn.to_string(index=False))
dd = pd.DataFrame({"p": pp, "y": y_te, "g": pd.qcut(pp, 10, labels=False)}).groupby("g").agg(n=("y", "size"), o=("y", "sum"), e=("p", "sum"))
hl = float((((dd.o - dd.e) ** 2) / (dd.e * (1 - dd.e / dd.n))).sum()); p_hl = float(1 - chi2.cdf(hl, 8))
print(f"Hosmer-Lemeshow (10 groupes, 8 degrés de liberté) : {hl:.2f}   p-valeur {p_hl:.3f}")
```
<!--sortie-->
```text
 note  dossiers  PD annoncée  défaut observé  p-valeur
    1       648       0.0077          0.0093    0.6484
    2      2373       0.0152          0.0169    0.5019
    3      2958       0.0269          0.0216    0.0780
    4      2628       0.0458          0.0498    0.3269
    5      1647       0.0766          0.0826    0.3542
    6      1200       0.1367          0.1300    0.5285
    7       546       0.3299          0.3352    0.7850
Hosmer-Lemeshow (10 groupes, 8 degrés de liberté) : 10.50   p-valeur 0.232
```

```python hide
print("NUM hl", round(hl, 2)); print("NUM p_hl", round(p_hl, 3)); print("NUM min_p", float(tn["p-valeur"].min()))
```
<!--sortie-->
```text
NUM hl 10.5
NUM p_hl 0.232
NUM min_p 0.078
```

Les p-valeurs sont élevées (aucune note n'est rejetée au seuil de 5 %), et le test de **Hosmer–Lemeshow**, qui regroupe les dossiers en dix groupes et additionne les écarts $(O_g-E_g)^2/[E_g(1-E_g/n_g)]$ (loi du $\chi^2$ à 8 degrés de liberté), ne rejette pas non plus la calibration. La grille est calibrée **sur cet échantillon**. Le test n'a pourtant qu'une portée limitée, et nous allons voir pourquoi.

#### La conjoncture ruine le test binomial

Le fichier `taux_defaut_macro.csv` donne 80 trimestres de taux de défaut d'un portefeuille de 20 000 prêts (nombre supposé). Le taux moyen est de 3,06 %. Appliquons le test binomial trimestre par trimestre à la PD « moyenne sur le cycle » :

```python hide
import statsmodels.api as sm
mac = pd.read_csv("donnees/taux_defaut_macro.csv")
n_p = 20000; pd_cycle = mac["taux_defaut"].mean()
rej = np.array([binomtest(int(round(r * n_p)), n_p, pd_cycle).pvalue < 0.05 for r in mac["taux_defaut"]])
rng_m = np.random.default_rng(0); rho = 0.03; from scipy.stats import norm
rej0 = 0
for _ in range(2000):
    z_ = rng_m.normal(); pc = norm.cdf((norm.ppf(0.03) - np.sqrt(rho) * z_) / np.sqrt(1 - rho))
    rej0 += binomtest(int(rng_m.binomial(n_p, pc)), n_p, 0.03).pvalue < 0.05
taille = rej0 / 2000
fig, ax = plt.subplots(figsize=(8.6, 3.4))
ax.plot(mac["trimestre"], mac["taux_defaut"] * 100, color=BLEU, lw=1.8, label="taux de défaut observé")
band = 1.96 * np.sqrt(pd_cycle * (1 - pd_cycle) / n_p) * 100
ax.axhline(pd_cycle * 100, color=ENCRE, lw=1.2); ax.fill_between([1, 80], pd_cycle * 100 - band, pd_cycle * 100 + band, color=ORANGE, alpha=0.45, label="intervalle du test binomial (95 %)")
ax.axvspan(48, 55, color=ROUGE, alpha=0.10); ax.text(51.5, 12.3, "récession", ha="center", color=ROUGE, fontsize=9)
ax.set_xlabel("trimestre"); ax.set_ylabel("défaut (%)"); ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout(); fig.savefig("figures/ch01-cycle-binomial.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM pd_cycle", round(float(pd_cycle), 4)); print("NUM rej", int(rej.sum())); print("NUM taille_test", round(taille, 3))
print("NUM max_macro", round(float(mac["taux_defaut"].max()), 4)); print("NUM min_macro", round(float(mac["taux_defaut"].min()), 4)); print("NUM band", round(float(band), 3))
```
<!--sortie-->
```text
NUM pd_cycle 0.0306
NUM rej 65
NUM taille_test 0.848
NUM max_macro 0.1283
NUM min_macro 0.0099
NUM band 0.239
```

![Taux de défaut trimestriel d'un portefeuille et bande de confiance (95 %) du test binomial autour de la PD moyenne : presque tous les trimestres sortent de la bande.](figures/ch01-cycle-binomial.png)

Le test **rejette 65 trimestres sur 80** : la bande de confiance du test binomial est étroite (± 0,24 point) alors que le taux de défaut oscille entre 1,0 % et 12,8 %. Ces rejets ne disent pas que la PD est mal estimée : ils disent que **le test suppose des défauts indépendants**. Or les défauts d'un portefeuille sont **corrélés par la conjoncture** : une récession touche tous les emprunteurs à la fois. On modélise cette dépendance par un **facteur commun** (modèle de Vasicek, retrouvé au chapitre 4 dans la formule de capital de Bâle) : sous une corrélation d'actifs de seulement 3 %, un test binomial à 5 % rejette à tort la vraie PD **dans 85 % des cas** (simulation de 2 000 portefeuilles de 20 000 prêts, PD vraie de 3 %). La taille du test est pulvérisée.

Deux enseignements à retenir :

- une **PD « sur le cycle »** (*through the cycle*, la moyenne des années) et une **PD « à la date »** (*point in time*, qui suit la conjoncture) répondent à deux questions différentes ; la première sert au capital, la seconde aux provisions (section 1.5) ;
- le **test binomial** est **trop sévère** pour un portefeuille agrégé : les validateurs utilisent des variantes qui intègrent une corrélation (tests de Blochwitz, de Vasicek, test de Jeffreys) ou simplement des seuils de tolérance fixés d'avance. Les noms des variantes varient selon les pratiques ; le point à retenir est l'indépendance supposée.

### 1.3.8 Un détour par des données réelles

Pour ne pas conclure sur des données que nous avons nous-mêmes fabriquées, voici les mêmes mesures sur un **jeu réel** : 30 000 titulaires d'une carte de crédit (source UCI, licence CC0, Yeh et Lien, 2009 ; 22 % de défaut le mois suivant). Les variables sont la limite de crédit, l'âge, le niveau d'études, six mois de **statuts de paiement** (`pay_1` à `pay_6` : −2 = pas de consommation, −1 = payé en totalité, 0 = paiement minimal, 1 à 8 = mois de retard), les montants de facture et de paiement. Deux modèles, entraînés sur 70 % et mesurés sur 30 % :

```python hide-code
rr = pd.read_csv("donnees/credit_defaut.csv")
Xr, yr = rr.drop(columns="default"), rr["default"]
from sklearn.model_selection import train_test_split
ra, rb, rya, ryb = train_test_split(Xr, yr, test_size=0.3, random_state=7, stratify=yr)
lr_r = LogisticRegression(max_iter=5000).fit((ra - ra.mean()) / ra.std(), rya); pr_lr = lr_r.predict_proba((rb - ra.mean()) / ra.std())[:, 1]
gb_r = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=8, min_child_samples=100, verbose=-1).fit(ra, rya); pr_gb = gb_r.predict_proba(rb)[:, 1]
# logistique avec le dernier statut de paiement traité comme des modalités et non comme un nombre
def cat_pay(d):
    D = pd.get_dummies(d["pay_1"].clip(-2, 4).astype(str), prefix="pay1").astype(float)
    return pd.concat([d.drop(columns=["pay_1"]), D], axis=1)
ca, cb = cat_pay(ra), cat_pay(rb)
lr_c = LogisticRegression(max_iter=5000).fit((ca - ca.mean()) / ca.std().replace(0, 1), rya); pr_c = lr_c.predict_proba((cb - ca.mean()) / ca.std().replace(0, 1))[:, 1]
rt = pd.DataFrame({m: [O.auc(ryb, p_), O.gini(ryb, p_), O.ks(ryb, p_)] for m, p_ in [("pay_1 seul (nombre)", rb["pay_1"]), ("logistique, tout en nombres", pr_lr), ("logistique, pay_1 en modalités", pr_c), ("boosting", pr_gb)]},
                  index=["AUC", "Gini", "KS"]).T.round(3)
print(rt.to_string())
```
<!--sortie-->
```text
                                  AUC   Gini     KS
pay_1 seul (nombre)             0.694  0.388  0.383
logistique, tout en nombres     0.728  0.457  0.381
logistique, pay_1 en modalités  0.768  0.536  0.424
boosting                        0.791  0.582  0.448
```

```python hide
print("NUM reel_taux", round(float(yr.mean()), 3))
for k, v in rt.iterrows(): print("NUM reel", k, v["AUC"], v["KS"])
```
<!--sortie-->
```text
NUM reel_taux 0.221
NUM reel pay_1 seul (nombre) 0.694 0.383
NUM reel logistique, tout en nombres 0.728 0.381
NUM reel logistique, pay_1 en modalités 0.768 0.424
NUM reel boosting 0.791 0.448
```

Les chiffres sont d'un autre ordre que ceux de nos prêts simulés (le défaut est près de quatre fois plus fréquent, l'information sur le comportement récent est directe), et l'histoire diffère : la logistique qui prend `pay_1` comme un **nombre** (de −2 à 8) perd beaucoup, parce que l'effet n'est pas linéaire (−2, −1 et 0 sont des statuts de bons payeurs, 2 est déjà une alerte) ; **traiter `pay_1` en modalités**, comme le fait une grille par classes, récupère l'essentiel du gain, et le boosting fait encore un peu mieux (il trouve en plus des interactions). La leçon est celle de 1.2 : **ce sont les formes qui comptent**, et elles se découvrent en regardant les données ; la grille est un bon moyen de ne pas les rater.

### 1.3.9 Les pièges de la mesure

- **L'AUC ne dit rien de la calibration.** Un score qui annoncerait partout deux fois la vraie probabilité classe aussi bien (le rang ne change pas) et se trompe sur chaque prix.
- **L'AUC ignore les coûts.** Deux scores de même AUC peuvent être très différents dans la zone où l'on décide (les 20 % de dossiers les plus risqués, ou le seuil d'acceptation).
- **Le Gini dépend de la population.** Un Gini de 55 % sur la clientèle d'un prêteur n'est pas comparable à un Gini de 45 % sur un portefeuille plus homogène : avec des clients plus semblables, le classement est plus difficile. On ne compare des Gini **qu'à population comparable**.
- **Le Gini de développement est optimiste.** Il se mesure sur l'échantillon où les classes ont été choisies ; la mesure honnête est celle du **test** (et, mieux, d'une période postérieure).
- **Un Gini qui baisse n'est pas toujours un modèle qui vieillit** : il peut refléter un changement de politique d'acceptation (1.1.7).

> ✅ **À retenir.**
> - **AUC** = probabilité qu'un mauvais ait un score de risque plus élevé qu'un bon ; **Gini** = 2·AUC − 1 (démontré par la courbe CAP, indépendant de la proportion de mauvais) ; **KS** = écart maximal TPR − FPR.
> - Les trois mesurent la **discrimination**, pas la **calibration**, pas la **décision** : le seuil se choisit sur un tableau de compromis et sur des coûts.
> - Une AUC s'accompagne de son **intervalle** (bootstrap), et deux modèles se comparent sur des rééchantillons **appariés**.
> - Le **PSI** repère un changement de population ; il ne voit pas une dérive du concept.
> - Le **test binomial** de calibration suppose des défauts indépendants et rejette à tort un portefeuille soumis à la conjoncture ; il faut le compléter par des variantes qui tiennent compte de la corrélation.
> - Sur des données réelles aussi, **les formes des effets** décident de la performance : mesurez, regardez les effets, ne supposez pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4, exercices 1.6 à 1.8.
