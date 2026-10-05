## 6.3 La forêt d'isolement

Les méthodes de la section précédente décrivent d'abord ce qui est **normal** (un centre, une covariance, une densité), puis déclarent anormal ce qui s'en écarte. Elles font un travail inutile : on ne cherche pas à bien décrire les commandes normales, mais à repérer les rares qui ne le sont pas. La **forêt d'isolement** (*isolation forest*, Liu, Ting et Zhou, 2008) prend le problème à l'envers : au lieu de décrire le normal, elle mesure **la facilité avec laquelle on isole chaque point**.

```python hide
from sklearn.ensemble import IsolationForest

def profondeur(valeurs, cible, rng):
    """Nombre de coupures aléatoires nécessaires pour isoler `cible` : on coupe au hasard entre le min et le max du groupe courant."""
    d, courant = 0, valeurs
    while len(courant) > 1:
        coupure = rng.uniform(courant.min(), courant.max())
        courant = courant[courant < coupure] if cible < coupure else courant[courant >= coupure]
        d += 1
    return d

def c_de_n(n):
    """Longueur moyenne d'une recherche infructueuse dans un arbre binaire de recherche de n points."""
    return 1.0 if n == 2 else 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n
```

### 6.3.1 L'idée : isoler plutôt que décrire

Voici huit valeurs : sept proches les unes des autres (2 ; 3 ; 3,5 ; 4 ; 4,5 ; 5 ; 5,5) et une très éloignée (30). On joue à un jeu : on tire une **coupure au hasard** entre le minimum et le maximum, ce qui sépare les valeurs en deux groupes ; on garde le groupe qui contient la valeur étudiée, on recommence, et on compte le nombre de coupures nécessaires pour la **laisser seule**.

- Pour la valeur 30, la première coupure l'isole dès qu'elle tombe entre 5,5 et 30 : c'est le cas avec la probabilité $(30-5{,}5)/(30-2)=\mathbf{87{,}5\ \%}$. Il suffit **d'une coupure ou deux**.
- Pour la valeur 4, au milieu du groupe, il faut en général **cinq coupures** : elle est entourée de voisines qu'il faut écarter une à une.

En répétant ce jeu avec 5 000 séquences de coupures aléatoires, on obtient le nombre moyen de coupures nécessaires pour isoler chaque valeur :

```python hide-code
valeurs = np.array([2, 3, 3.5, 4, 4.5, 5, 5.5, 30.])
rng_i = np.random.default_rng(0)
profs = {float(v): [] for v in valeurs}
for _ in range(5000):
    for v in valeurs:
        profs[float(v)].append(profondeur(valeurs, v, rng_i))
moy_prof = {v: float(np.mean(p)) for v, p in profs.items()}
print("valeur   coupures moyennes pour l'isoler")
for v, m in moy_prof.items():
    print(f"{v:6.1f}   {m:5.2f}")
print("probabilité que 30 soit isolée dès la 1re coupure (simulation) :", round(float(np.mean(np.array(profs[30.0]) == 1)), 3), "; calcul exact : 0,875")
```
<!--sortie-->
```text
valeur   coupures moyennes pour l'isoler
   2.0    2.95
   3.0    4.19
   3.5    4.70
   4.0    4.76
   4.5    4.70
   5.0    4.40
   5.5    3.55
  30.0    1.14
probabilité que 30 soit isolée dès la 1re coupure (simulation) : 0.869 ; calcul exact : 0,875
```

La valeur 30 est isolée en **1,14 coupure** en moyenne, contre 4,4 à 4,8 pour les valeurs centrales. **Les anomalies sont peu nombreuses et différentes : elles s'isolent vite.** C'est tout le principe de la méthode : la longueur moyenne du « chemin » qui mène à une observation est une mesure d'anormalité, sans qu'on ait jamais eu à décrire ce qu'est la normalité.

> 💡 **Pourquoi cela marche.** Les points normaux se trouvent dans des régions denses : il faut beaucoup de coupures pour les séparer de leurs voisins. Un point isolé a autour de lui du vide : presque n'importe quelle coupure le sépare du reste.

### 6.3.2 La longueur de chemin et le score d'anomalie

Cette idée s'applique à plusieurs variables : à chaque étape, on choisit **une variable au hasard**, puis une **coupure au hasard** entre le minimum et le maximum de cette variable dans le groupe courant. On répète jusqu'à ce que chaque point soit seul (ou qu'une hauteur maximale soit atteinte). Le résultat est un **arbre d'isolement** ; la **longueur de chemin** $h(x)$ d'un point $x$ est le nombre de coupures qui l'isolent. Une **forêt** de nombreux arbres, construits chacun sur un sous-échantillon, donne une longueur moyenne $E[h(x)]$.

Pour transformer cette longueur en score comparable d'un jeu de données à l'autre, on la normalise. Un arbre d'isolement de $n$ points a la même structure qu'un **arbre binaire de recherche** : la longueur moyenne d'un chemin y est connue. C'est celle d'une recherche infructueuse, soit

$$c(n)=2H(n-1)-\frac{2(n-1)}{n},\qquad H(i)\approx\ln(i)+0{,}5772\ \ (\text{constante d'Euler}),$$

où $H(i)$ est le $i$-ième nombre harmonique. On définit alors le **score d'anomalie**

$$\boxed{\ s(x,n)=2^{-E[h(x)]/c(n)}\ }$$

Le score est toujours entre 0 et 1, et se lit ainsi :

- si $E[h(x)]$ est **très petit** (isolé presque immédiatement), $s\to 1$ : forte anomalie ;
- si $E[h(x)]=c(n)$ (un point moyen), $s=2^{-1}=\mathbf{0{,}5}$ : rien de particulier ;
- si $E[h(x)]$ est **grand** (profondément enfoui), $s\to 0$ : point très normal.

```python hide-code
print("n      c(n)")
for n in [2, 8, 16, 64, 256, 1000]:
    print(f"{n:5d}  {c_de_n(n):6.3f}")
print()
print("score pour n = 256 (c = %.2f) :" % c_de_n(256), {f"E[h] = {Eh:g}": round(float(2 ** (-Eh / c_de_n(256))), 3) for Eh in [2, 4, round(c_de_n(256), 1), 20]})
```
<!--sortie-->
```text
n      c(n)
    2   1.000
    8   3.296
   16   4.696
   64   7.472
  256  10.245
 1000  12.970

score pour n = 256 (c = 10.24) : {'E[h] = 2': 0.873, 'E[h] = 4': 0.763, 'E[h] = 10.2': 0.502, 'E[h] = 20': 0.258}
```

Pour $n=256$ points, $c(256)\approx10{,}2$ : un point isolé en 2 coupures a un score de 0,87, un point isolé en 4 coupures de 0,76, un point moyen de 0,50, et un point qu'il faut 20 coupures pour isoler de 0,26.

> ⚠️ **Une approximation, pas une identité.** La normalisation $c(n)$ est une *analogie* avec les arbres de recherche (c'est l'argument de l'article d'origine). Nos coupures sont tirées uniformément entre le minimum et le maximum, et non selon les rangs, ce qui change un peu la structure des arbres. En simulant directement des coupures uniformes sur des échantillons de $n$ valeurs normales, on trouve une profondeur moyenne légèrement supérieure à $c(n)$ (de 7 à 10 % de plus, pour $n=8$, 64 et 256). Cela ne change pas l'**ordre** des scores, qui est ce dont on se sert pour classer les alertes ; seul le point d'équilibre à 0,5 est un peu décalé.

```python hide
rng_c = np.random.default_rng(1)
comparaison = {}
for n in [8, 64, 256]:
    tout = []
    for _ in range(100):
        v = rng_c.normal(size=n)
        tout += [profondeur(v, x, rng_c) for x in v]
    comparaison[n] = (float(np.mean(tout)), c_de_n(n))
print({n: (round(a, 2), round(b, 2), round(100 * (a / b - 1))) for n, (a, b) in comparaison.items()})
```
<!--sortie-->
```text
{8: (3.52, np.float64(3.3), 7), 64: (8.09, np.float64(7.47), 8), 256: (11.28, np.float64(10.24), 10)}
```

### 6.3.3 De l'arbre à la forêt

Dans la pratique, la forêt d'isolement construit **$t$ arbres** (200 dans nos essais). Chacun est bâti sur un **petit sous-échantillon** de $\psi$ points tirés au hasard (256 par défaut), avec une hauteur maximale de $\lceil\log_2\psi\rceil=8$ : inutile de pousser l'arbre plus profond, puisque les anomalies s'isolent bien avant. Ces choix donnent trois propriétés précieuses :

- **Elle ne calcule aucune distance** et n'estime ni moyenne ni covariance : son coût de construction ne dépend presque pas de la taille $n$ du jeu de données (chaque arbre n'utilise que $\psi$ points), et le score d'un point coûte $t\log\psi$ opérations. Elle passe à l'échelle de millions de lignes.
- **Le sous-échantillonnage la protège du masquage et de l'« engorgement »** (*swamping*) : avec peu de points par arbre, les anomalies ne sont plus noyées dans des régions denses de points normaux voisins, et les points normaux ne sont plus pris pour des anomalies parce qu'ils voisinent avec elles.
- **Elle est invariante aux changements d'échelle linéaires** de chaque variable (la coupure est tirée dans l'étendue de la variable), mais pas aux transformations non linéaires comme le logarithme : c'est pourquoi nos variables très asymétriques (montant, distance, ancienneté, délai) sont transformées en logarithme avant tout (chapitre 4, section 4.1).

Les choix de $t$ et de $\psi$ comptent. Voici la précision moyenne (AP) obtenue sur le jeu de test pour différentes valeurs, en moyenne sur trois graines :

```python hide-code
def ap_moyenne(n_estimators, max_samples, graines=(0, 1, 2)):
    return float(np.mean([average_precision_score(y_test, -IsolationForest(n_estimators=n_estimators, max_samples=max_samples, random_state=g).fit(Z_app).score_samples(Z_test)) for g in graines]))
print("nombre d'arbres (psi = 256) :", {t_: round(ap_moyenne(t_, 256), 3) for t_ in [10, 50, 200]})
print("taille du sous-échantillon psi (100 arbres) :", {p_: round(ap_moyenne(100, p_), 3) for p_ in [32, 64, 256, 1024, 4096]})
```
<!--sortie-->
```text
nombre d'arbres (psi = 256) : {10: 0.216, 50: 0.318, 200: 0.366}
taille du sous-échantillon psi (100 arbres) : {32: 0.287, 64: 0.3, 256: 0.355, 1024: 0.373, 4096: 0.398}
```

Avec trop peu d'arbres (10), le score est bruité ; au-delà de 100 arbres, on gagne peu. Quant au sous-échantillon, ici, **plus il est grand, mieux c'est** (de 0,29 pour $\psi=32$ à 0,40 pour $\psi=4096$) : la valeur de 256 recommandée par l'article d'origine est une valeur par défaut raisonnable, pas un optimum. Comme toujours, ces réglages se décident mieux avec quelques étiquettes pour évaluer.

### 6.3.4 Le paramètre de contamination et le seuil

La forêt produit un **score**, pas une décision. Pour décider, `scikit-learn` propose un paramètre `contamination` : la proportion supposée d'anomalies dans les données. Il fixe le **seuil** au quantile correspondant des scores d'apprentissage. Sa valeur par défaut, `"auto"`, utilise un seuil fixe (score de 0,5) tiré de l'article d'origine.

```python hide
avec_defaut = IsolationForest(n_estimators=200, random_state=0).fit(Z_app)
drapeau_auto = avec_defaut.predict(Z_test) == -1
avec_contam = IsolationForest(n_estimators=200, contamination=0.0081, random_state=0).fit(Z_app)
drapeau_contam = avec_contam.predict(Z_test) == -1
print("seuil par défaut (auto) : alertes", int(drapeau_auto.sum()), "soit", round(100 * float(drapeau_auto.mean()), 1), "% des commandes ; précision", round(float(y_test[drapeau_auto].mean()), 3), "; rappel", round(float(y_test[drapeau_auto].sum() / y_test.sum()), 3))
print("contamination = 0,0081 : alertes", int(drapeau_contam.sum()), "soit", round(100 * float(drapeau_contam.mean()), 2), "% ; précision", round(float(y_test[drapeau_contam].mean()), 3), "; rappel", round(float(y_test[drapeau_contam].sum() / y_test.sum()), 3))
```
<!--sortie-->
```text
seuil par défaut (auto) : alertes 3699 soit 20.5 % des commandes ; précision 0.036 ; rappel 0.925
contamination = 0,0081 : alertes 150 soit 0.83 % ; précision 0.34 ; rappel 0.349
```

Sur nos données, le seuil par défaut déclenche une alerte sur **20,5 %** des commandes (3 699 alertes) : on retrouve **92,5 %** des fraudes, mais la précision tombe à **3,6 %**, et la gérante croulerait sous les vérifications. En fixant `contamination = 0,0081` (la vraie proportion de fraudes), on obtient environ 150 alertes, de précision **34 %**, et un rappel de **35 %**.

Cet exemple dit quelque chose d'important : **la contamination n'est pas un paramètre statistique que les données révèlent, c'est un choix opérationnel.** En pratique on ne connaît pas la proportion de fraudes ; ce que l'on connaît, c'est le **budget d'alertes** que l'on peut traiter. C'est pourquoi nous classons toujours les commandes par score et gardons les 180 plus suspectes (1 % du test), plutôt que de nous fier à un seuil théorique.

### 6.3.5 Sur nos transactions

```python
from sklearn.ensemble import IsolationForest

foret = IsolationForest(n_estimators=200, random_state=0).fit(Z_app)     # aucune étiquette
score_isolement = -foret.score_samples(Z_test)                           # score s : plus grand = plus anormal
```

```python hide
evaluer("Forêt d'isolement", score_isolement)
print(tableau(["Forêt d'isolement"]).to_string())
print("score moyen : normales", round(float(score_isolement[y_test == 0].mean()), 3), "| type 1", round(float(score_isolement[type_test == 1].mean()), 3), "| type 2", round(float(score_isolement[type_test == 2].mean()), 3), "| plus grand score", round(float(score_isolement.max()), 3))
z_abs = np.abs(Z_test)
for g, nom in [(0, "normales"), (1, "type 1"), (2, "type 2")]:
    m_ = type_test == g
    print(f"{nom:9s} : au moins une variable à |z| > 3 : {100 * float((z_abs[m_].max(axis=1) > 3).mean()):.0f} % ; nombre moyen de variables à |z| > 1,5 : {float((z_abs[m_] > 1.5).sum(axis=1).mean()):.2f}")
seuil_budget = np.sort(score_isolement)[-budget]
print("seuil du budget de 180 alertes : score >=", round(float(seuil_budget), 3))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ordre_v = list(moy_prof.keys())
ax[0].bar(range(8), [moy_prof[v] for v in ordre_v], color=[ROUGE if v > 20 else BLEU for v in ordre_v])
ax[0].set_xticks(range(8)); ax[0].set_xticklabels([f"{v:g}" for v in ordre_v]); ax[0].set_xlabel("valeur à isoler"); ax[0].set_ylabel("coupures moyennes pour l'isoler")
ax[0].set_title("Le petit exemple : la valeur 30 s'isole vite", fontsize=10)
bins = np.linspace(score_isolement.min(), score_isolement.max(), 40)
for g, nom, col in [(0, "normales", MUET), (1, "fraude de type 1", ORANGE), (2, "fraude de type 2", VIOLET)]:
    ax[1].hist(score_isolement[type_test == g], bins=bins, density=True, histtype="stepfilled" if g == 0 else "step", color=col, alpha=0.35 if g == 0 else 1, lw=1.8, label=nom)
ax[1].axvline(seuil_budget, color="#0b0b0b", ls="--", lw=1); ax[1].text(seuil_budget + 0.004, ax[1].get_ylim()[1] * 0.8, "seuil du budget\nde 180 alertes", fontsize=8)
ax[1].set_xlabel("score d'anomalie de la forêt d'isolement"); ax[1].set_yticks([]); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
ax[1].set_title("Les transactions du jeu de test", fontsize=10)
plt.tight_layout(); plt.savefig("figures/ch06-isolement.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
                     AUC     AP  précision à k  rappel type 1  rappel type 2
Forêt d'isolement  0.937  0.332          0.342          0.123          0.677
score moyen : normales 0.459 | type 1 0.555 | type 2 0.626 | plus grand score 0.727
normales  : au moins une variable à |z| > 3 : 10 % ; nombre moyen de variables à |z| > 1,5 : 0.99
type 1    : au moins une variable à |z| > 3 : 78 % ; nombre moyen de variables à |z| > 1,5 : 2.96
type 2    : au moins une variable à |z| > 3 : 89 % ; nombre moyen de variables à |z| > 1,5 : 3.60
seuil du budget de 180 alertes : score >= 0.611
```

![À gauche, le petit exemple de huit valeurs : nombre moyen de coupures nécessaires pour isoler chacune (la valeur 30, en rouge, s'isole en une coupure environ). À droite, la distribution des scores de la forêt d'isolement sur le jeu de test pour les commandes normales (gris) et les deux types de fraude ; la ligne pointillée marque le seuil qui garde 180 alertes.](figures/ch06-isolement.png)

La forêt d'isolement obtient une précision moyenne de **0,332** : un peu en dessous des voisins (0,444), au niveau de Mahalanobis (0,382) ou du LOF (0,306). Sa force est qu'elle est **rapide et sans réglage délicat**. Mais comme le montre la figure de droite, ses scores séparent bien les fraudes de **type 2** (dont le score moyen de 0,626 est bien au-dessus de celui des commandes normales, 0,459) et beaucoup moins bien les fraudes de **type 1** (0,555) : 68 % des fraudes de type 2 sont dans les 180 alertes, contre 12 % seulement de celles de type 1.

Pourquoi cette différence ? Ce n'est pas faute de valeurs extrêmes : la vérification ci-dessus montre que **78 %** des fraudes de type 1 ont au moins une variable à plus de 3 écarts-types (contre 89 % pour le type 2 et 10 % pour les commandes normales), et qu'elles s'écartent en moyenne de plus de 1,5 écart-type sur 3 variables (3,6 pour le type 2). Les deux types sont donc bien loin de la normale, le type 2 un peu plus. Nous n'avons **pas démontré** pourquoi cela suffit à placer les fraudes de type 2 beaucoup plus haut dans le classement de la forêt. Une hypothèse, que nous n'avons pas testée, est que les variables caractéristiques du type 2 (appareil inconnu, adresse IP étrangère, rafale de commandes) sont rares et à valeurs discrètes, donc qu'une seule coupure suffit à les isoler, alors que celles du type 1 (montant, distance) ont des queues lourdes qui rendent de nombreuses commandes **normales** presque aussi faciles à isoler. Le seul fait établi est empirique : sur ces données, la forêt classe bien le type 2 et mal le type 1.

> ✅ **À retenir.**
> - La forêt d'isolement mesure la **facilité à isoler** un point par des coupures aléatoires : les anomalies, rares et différentes, s'isolent vite.
> - Le score $s=2^{-E[h(x)]/c(n)}$ vaut 0,5 pour un point moyen et tend vers 1 pour une anomalie ; $c(n)=2H(n-1)-2(n-1)/n$ est une normalisation approchée.
> - Elle est **rapide**, sans distance ni hypothèse de loi, et passe à l'échelle grâce au sous-échantillonnage.
> - La **contamination** est un choix opérationnel (le budget d'alertes), pas une vérité statistique : le seuil par défaut peut donner des milliers de fausses alertes.
> - Sa qualité dépend de la nature des anomalies : ici elle retrouve bien les fraudes de type 2 et mal celles de type 1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.4, exercices 6.8 et 6.9.
