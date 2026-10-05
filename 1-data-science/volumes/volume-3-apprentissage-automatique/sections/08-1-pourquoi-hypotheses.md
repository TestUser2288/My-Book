## 8.1 Pourquoi et hypothèses

Avant de présenter des méthodes, il faut comprendre **pourquoi** des données sans étiquette pourraient aider, à quelles **conditions**, et comment **vérifier honnêtement** qu'elles aident. Cette section pose le cadre ; les deux suivantes l'utilisent.

### 8.1.1 Le problème de l'étiquette chère

Reprenons les notations du volume. Nous disposons de deux paquets de données :

- un petit ensemble **étiqueté** $\mathcal L=\{(x_i,y_i)\}_{i=1}^{n_\ell}$, où l'on connaît la réponse $y_i$ ;
- un grand ensemble **non étiqueté** $\mathcal U=\{x_j\}_{j=1}^{n_u}$, où l'on ne connaît que les variables $x_j$.

La situation typique est $n_u\gg n_\ell$ : quelques dizaines d'exemples étiquetés, des milliers d'autres sans réponse. On distingue trois façons de s'en sortir :

| Paradigme | Ce qu'on utilise | Ce qu'on produit |
|---|---|---|
| **Supervisé** | seulement $\mathcal L$ | un modèle $f$ qui prédit $y$ à partir de $x$ |
| **Non supervisé** | seulement les $x$ | des groupes, des axes, une structure (chapitre 3) |
| **Semi-supervisé** | $\mathcal L$ **et** $\mathcal U$ | un modèle $f$, appris avec l'aide de la structure de $\mathcal U$ |

Deux nuances de vocabulaire sont utiles pour lire la littérature :

- l'apprentissage est **transductif** quand on ne cherche qu'à étiqueter les points de $\mathcal U$ que l'on a *déjà* sous la main (typiquement : les 5 000 clients de la base à qualifier) ;
- il est **inductif** quand on veut un modèle $f$ capable de prédire sur de **nouveaux** points (les clients de demain).

> 💡 **La seule mesure du succès.** Une méthode semi-supervisée n'a de valeur que si elle fait mieux que le modèle **supervisé entraîné sur les mêmes étiquettes** $\mathcal L$. Comparer à un modèle qui disposerait de *plus* d'étiquettes n'aurait aucun sens : l'enjeu est précisément ce que l'on gagne **à budget d'étiquettes égal**.

### 8.1.2 Ce que les données non étiquetées apportent

Un point $x_j$ sans étiquette ne nous dit rien, à lui seul, sur sa classe. Alors comment pourrait-il aider ? Parce que **l'ensemble** des $x_j$ nous renseigne sur la loi des variables, $p(x)$ : où se concentrent les données, où sont les creux, quelle est la forme des groupes. Si cette structure est **liée** à la classe, l'information est précieuse.

**Un exemple minuscule, entièrement à la main.** Une seule variable $x$, deux classes A et B. Deux clients seulement sont étiquetés :

- le client A vaut $x=-1{,}4$ ;
- le client B vaut $x=+0{,}6$.

Entraîné sur ces deux points, un classifieur « centre le plus proche » place sa frontière au milieu : $(−1{,}4+0{,}6)/2=-0{,}4$. Mais six autres clients, **sans étiquette**, ont été observés :

$$-2{,}1,\quad -1{,}8,\quad -1{,}2,\qquad +1{,}3,\quad +1{,}7,\quad +2{,}0.$$

Ils forment **visiblement deux paquets**, un à gauche et un à droite d'un creux vide autour de $0$. La frontière à $-0{,}4$ passe au bord du paquet de gauche : elle est suspecte. Corrigeons-la en une étape :

1. **Étiqueter provisoirement** chaque point non étiqueté selon la frontière actuelle ($-0{,}4$) : les trois de gauche sont classés A, les trois de droite B.
2. **Recalculer les centres** avec tous les points : $\bar x_A=\dfrac{-1{,}4-2{,}1-1{,}8-1{,}2}{4}=-1{,}625$ et $\bar x_B=\dfrac{0{,}6+1{,}3+1{,}7+2{,}0}{4}=1{,}4$.
3. **Recalculer la frontière** : $\dfrac{-1{,}625+1{,}4}{2}=-0{,}1125$.

Si les deux classes sont des cloches symétriques de même largeur, la vraie frontière est en $0$. La frontière est passée de $-0{,}4$ à $-0{,}11$ : **elle s'est rapprochée du creux**, grâce aux six points sans étiquette.

```python hide
a, b = -1.4, 0.6
U = np.array([-2.1, -1.8, -1.2, 1.3, 1.7, 2.0])
f0 = (a + b) / 2
A = [a] + [u for u in U if u < f0]
B = [b] + [u for u in U if u >= f0]
print("frontière initiale :", round(f0, 4), "| centres :", round(np.mean(A), 4), round(np.mean(B), 4),
      "| nouvelle frontière :", round((np.mean(A) + np.mean(B)) / 2, 4))
```
<!--sortie-->
```text
frontière initiale : -0.4 | centres : -1.625 1.4 | nouvelle frontière : -0.1125
```

> 📐 **Le principe derrière l'exemple : la vraisemblance mixte.** Supposons un modèle génératif $p(x,y\mid\theta)=p(y)\,p(x\mid y,\theta)$ (par exemple, deux lois normales). Pour un point étiqueté, la contribution à la log-vraisemblance est $\log p(x_i,y_i\mid\theta)$. Pour un point **non** étiqueté, on ne voit pas $y_j$ ; on **somme** sur toutes ses valeurs possibles :
> $$\ell(\theta)=\sum_{i\in\mathcal L}\log p(x_i,y_i\mid\theta)\;+\;\sum_{j\in\mathcal U}\log\sum_{c}p(y_j=c)\,p(x_j\mid y_j=c,\theta).$$
> Le second terme est exactement celui d'un **mélange de lois** (nous retrouverons les mélanges gaussiens en section 3.3 du présent volume). On le maximise par l'algorithme **EM** : l'étape **E** calcule, pour chaque point sans étiquette, la probabilité $r_{jc}=P(y_j=c\mid x_j,\theta)$ (« à quel point ce point appartient-il à la classe $c$ ? ») ; l'étape **M** réestime $\theta$ en comptant chaque point à hauteur de ces probabilités, les points étiquetés comptant pour 1 dans leur classe. L'exemple ci-dessus est une version **dure** d'EM : les probabilités $r_{jc}$ y valent 0 ou 1.
>
> **Ce qu'il faut en retenir** : les points sans étiquette n'agissent que par le terme $\log p(x_j\mid\theta)$, c'est-à-dire par ce qu'ils disent de **la loi des $x$**. Ils ne peuvent aider **que si** cette loi contient de l'information sur la frontière entre classes.

### 8.1.3 Les quatre hypothèses qui permettent d'aider

La théorie et la pratique du semi-supervisé reposent sur quelques **hypothèses sur le monde**, jamais vérifiables à 100 % :

| Hypothèse | Énoncé en une phrase | Ce que ça autorise |
|---|---|---|
| **Lissage** (*smoothness*) | deux points **proches** dans une région **dense** ont probablement la même étiquette | propager une étiquette aux voisins |
| **Groupes** (*cluster*) | les points d'un **même groupe** partagent la même classe | étiqueter un groupe entier à partir d'un seul de ses points |
| **Basse densité** | la frontière entre classes passe par une région **peu peuplée** | déplacer la frontière vers les creux (notre exemple à la main) |
| **Variété** (*manifold*) | les données vivent près d'une surface de faible dimension, et ce sont les distances **le long de cette surface** qui comptent | utiliser un graphe de voisinage plutôt que la distance « à vol d'oiseau » |

Voyons-les au travail sur deux jeux de 300 points en deux dimensions. En haut, deux « lunes » entrelacées : les groupes sont nets, la frontière naturelle passe dans le creux. En bas, deux nuages qui **se chevauchent** : il n'y a pas de creux, la structure de $p(x)$ ne dit rien de plus que ce que disent les étiquettes. Dans les deux cas, on ne donne que **trois étiquettes par classe**.

```python hide
from sklearn.datasets import make_moons, make_blobs
jeux = {"lunes": make_moons(300, noise=0.08, random_state=0),
        "chevauchement": make_blobs(300, centers=[[-0.75, 0], [0.75, 0]], cluster_std=1.6, random_state=0)}

def deux_methodes(X, y, graine):
    rng = np.random.default_rng(graine)
    idx = np.r_[rng.choice(np.where(y == 0)[0], 3, replace=False), rng.choice(np.where(y == 1)[0], 3, replace=False)]
    y_part = np.full(len(y), -1)
    y_part[idx] = y[idx]
    sup = LogisticRegression().fit(X[idx], y[idx])
    prop = LabelSpreading(kernel="knn", n_neighbors=10, alpha=0.2, max_iter=300).fit(X, y_part)
    return idx, sup, prop

res = {}
for nom, (X, y) in jeux.items():
    sc = np.array([[m.score(X, y) for m in deux_methodes(X, y, s)[1:]] for s in range(20)])
    res[nom] = sc
    print(f"{nom:14s} supervisé {sc[:, 0].mean():.3f} (± {sc[:, 0].std():.3f})   propagation {sc[:, 1].mean():.3f} (± {sc[:, 1].std():.3f})")

fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.6))
for r, (nom, (X, y)) in enumerate(jeux.items()):
    gains = res[nom][:, 1] - res[nom][:, 0]
    graine_type = int(np.argmin(np.abs(gains - gains.mean())))          # tirage représentatif : gain proche du gain moyen
    idx, sup, prop = deux_methodes(X, y, graine_type)
    xx, yy_ = np.meshgrid(np.linspace(X[:, 0].min() - 0.5, X[:, 0].max() + 0.5, 220), np.linspace(X[:, 1].min() - 0.5, X[:, 1].max() + 0.5, 220))
    grille = np.c_[xx.ravel(), yy_.ravel()]
    for c, (titre, m) in enumerate([("modèle supervisé (6 étiquettes)", sup), ("avec propagation (mêmes 6 étiquettes)", prop)]):
        ax = axes[r, c]
        ax.contourf(xx, yy_, m.predict(grille).reshape(xx.shape), levels=[-0.5, 0.5, 1.5], colors=["#cde2fb", "#fbd9cc"], alpha=0.8)
        ax.scatter(X[:, 0], X[:, 1], c="#9a9892", s=9, zorder=2)
        ax.scatter(X[idx, 0], X[idx, 1], c=[BLEU if v == 0 else ORANGE for v in y[idx]], s=85, edgecolor="white", linewidth=1.2, zorder=3)
        ax.set_title(f"{titre}\nprécision sur les 300 points : {m.score(X, y):.2f}", fontsize=9.5)
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    axes[r, 0].set_ylabel("deux lunes" if r == 0 else "deux nuages qui se chevauchent", fontsize=10)
plt.tight_layout()
style.save(fig, "ch08-hypotheses-lunes.png")
```
<!--sortie-->
```text
lunes          supervisé 0.819 (± 0.046)   propagation 0.897 (± 0.062)
chevauchement  supervisé 0.591 (± 0.076)   propagation 0.573 (± 0.056)
figure : ch08-hypotheses-lunes.png
```

![En haut, deux lunes entrelacées : avec trois étiquettes par classe, un modèle supervisé trace une frontière droite ; la propagation, qui s'appuie sur la forme des groupes, suit le creux entre les lunes. En bas, deux nuages qui se chevauchent : il n'y a pas de creux à exploiter, la propagation n'apporte rien. Les points colorés sont les six points étiquetés, les points gris sont les autres. Chaque ligne montre un tirage représentatif (dont le gain est le plus proche du gain moyen sur 20 tirages).](figures/ch08-hypotheses-lunes.png)

Sur 20 tirages différents des six étiquettes, la précision moyenne sur les lunes passe de **0,82** (supervisé) à **0,90** (propagation) : un gain net, qui vient de ce que la méthode a *vu* la forme des deux croissants. Sur les nuages qui se chevauchent, elle **ne bouge pas** (0,59 pour le supervisé, 0,57 pour la propagation, des différences très inférieures à l'écart-type d'un tirage à l'autre).

> ⚠️ **Le même algorithme, deux résultats opposés.** Rien, dans la méthode, ne l'a prévenue de ce qui allait se passer. C'est la **structure des données** qui décide. Avant de recourir au semi-supervisé, posez-vous toujours la question : *est-il plausible que la forme de $p(x)$ renseigne sur la frontière entre classes ?*

### 8.1.4 Quand ça aide, quand ça nuit

Il n'existe pas de « repas gratuit » : les données sans étiquette ne sont pas toujours une bonne affaire. Voici les situations à surveiller.

| Situation | Effet | Pourquoi |
|---|---|---|
| **L'hypothèse est vraie** (groupes nets, variété) | **gain** souvent important quand les étiquettes sont très rares | l'information de $p(x)$ est utile |
| **L'hypothèse est fausse** (classes qui se chevauchent, variables hétérogènes) | **aucun gain**, voire **perte** | la méthode « suit » une structure sans rapport avec les classes |
| **Les étiquettes disponibles sont déséquilibrées ou peu représentatives** | la méthode **amplifie** le défaut | elle étend ce qu'elle croit savoir à tous les voisins |
| **Les données sans étiquette viennent d'ailleurs** (autre période, autre population) | **perte** probable | $p(x)$ n'est plus celle du problème visé |
| **Un modèle sûr de lui à tort** (auto-apprentissage) | **dérive** | il se nourrit de ses propres erreurs (section 8.2.2) |

Un exemple chiffré du troisième cas, sur nos chiffres manuscrits. On tire 50 étiquettes, mais de façon **déséquilibrée** : le chiffre 0 reçoit six fois plus de chances d'être tiré que chacun des autres. En moyenne, 39 % des étiquettes sont alors des « 0 », contre 10 % attendus.

```python hide
w = np.array([6] + [1] * 9, float)
lignes = []
for s in range(10):
    rng = np.random.default_rng(300 + s)
    idx = rng.choice(len(yp), 50, replace=False, p=w[yp] / w[yp].sum())
    y_part = np.full(len(yp), -1)
    y_part[idx] = yp[idx]
    lignes.append((LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx]).score(Xt, yt),
                   LabelSpreading(kernel="knn", n_neighbors=7, alpha=0.2, max_iter=200).fit(Xp, y_part).score(Xt, yt),
                   SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=0.9).fit(Xp, y_part).score(Xt, yt),
                   (yp[idx] == 0).mean()))
desequilibre = np.array(lignes).mean(axis=0)
print("part de « 0 » parmi les étiquettes :", round(desequilibre[3], 3))
print("supervisé", round(desequilibre[0], 3), "| propagation", round(desequilibre[1], 3), "| auto-apprentissage", round(desequilibre[2], 3))
```
<!--sortie-->
```text
part de « 0 » parmi les étiquettes : 0.388
supervisé 0.695 | propagation 0.894 | auto-apprentissage 0.649
```

Avec ces étiquettes mal réparties, le modèle supervisé atteint **0,70** de précision ; la propagation (qui s'appuie sur le graphe de voisinage) reste robuste, à **0,89** ; mais l'**auto-apprentissage** *descend* à **0,65**, en dessous du supervisé : il prend ses propres préjugés pour des certitudes. Nous comprendrons le mécanisme en 8.2.2.

> 💡 **Règle pratique.** Si vous hésitez, commencez par la méthode **non supervisée** de votre choix (chapitre 3) : regardez si les groupes existent et s'ils ressemblent à vos classes sur le petit échantillon étiqueté. Si oui, le semi-supervisé a de bonnes chances d'aider ; sinon, passez directement à l'apprentissage actif (section 8.3), qui ne fait pas ce pari.

### 8.1.5 Évaluer à budget d'étiquettes fixé : la courbe d'apprentissage

La bonne façon de mesurer l'intérêt d'une méthode de ce chapitre est de tracer une **courbe d'apprentissage selon le budget d'étiquettes** : on fait varier le nombre $n_\ell$ d'étiquettes disponibles, et pour chacun on mesure la qualité sur un **jeu de test** étiqueté, tenu à l'écart. Le protocole est strict :

1. **Un jeu de test fixe**, tiré au hasard, jamais utilisé pour apprendre ni pour choisir quoi que ce soit (section 1.1). Ici : 450 images, **toutes** étiquetées.
2. **Un réservoir** dont on « cache » presque toutes les étiquettes (ici 1 347 images).
3. Pour chaque budget $n_\ell$ : tirer **plusieurs** ensembles d'étiquettes différents (ici 10, avec des graines fixées), car un seul tirage est trompeur quand $n_\ell$ est petit.
4. **Les mêmes étiquettes pour toutes les méthodes** : ainsi la comparaison est **appariée**, et la différence est due à la méthode et non à la chance du tirage.
5. Reporter **la moyenne et l'écart-type** (ou un intervalle) sur les tirages, pas une valeur unique.
6. **Aucun réglage fin** sur le jeu de test. Et attention : avec 10 étiquettes, on ne peut pas faire de validation croisée sérieuse. Si l'on garde des étiquettes pour régler un hyperparamètre, **elles comptent dans le budget**.

Voici la courbe du modèle **supervisé seul** (une régression logistique) sur les chiffres. C'est la référence à battre.

```python hide
budgets = [10, 20, 50, 100, 200, 400, 800]
courbe = []
for nl in budgets:
    sc = []
    for s in range(10):
        rng = np.random.default_rng(100 + s)
        idx = rng.choice(len(Xp), nl, replace=False)
        sc.append(LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx]).score(Xt, yt))
    courbe.append(sc)
courbe = np.array(courbe)
plafond = LogisticRegression(max_iter=3000).fit(Xp, yp).score(Xt, yt)
for nl, sc in zip(budgets, courbe):
    print(f"{nl:4d} étiquettes : {sc.mean():.3f} (± {sc.std():.3f})")
print("avec les 1347 étiquettes :", round(plafond, 3))
print("à 10 étiquettes, de", round(courbe[0].min(), 3), "à", round(courbe[0].max(), 3), "selon le tirage")

fig, ax = plt.subplots(figsize=(7.4, 4.2))
m, s = courbe.mean(axis=1), courbe.std(axis=1)
ax.fill_between(budgets, m - s, m + s, color=BLEU, alpha=0.18)
ax.plot(budgets, m, "o-", color=BLEU, lw=2)
ax.axhline(plafond, color=MUET, ls="--", lw=1)
ax.text(11, plafond + 0.012, f"toutes les étiquettes : {plafond:.2f}", color=ENCRE2, fontsize=9)
ax.set_xscale("log"); ax.set_xticks(budgets); ax.set_xticklabels(budgets)
ax.set_xlabel("nombre d'étiquettes disponibles (échelle logarithmique)")
ax.set_ylabel("précision sur le jeu de test")
ax.set_ylim(0.2, 1.02)
ax.set_title("Chiffres manuscrits : modèle supervisé seul")
plt.tight_layout()
style.save(fig, "ch08-courbe-supervisee.png")
```
<!--sortie-->
```text
  10 étiquettes : 0.429 (± 0.082)
  20 étiquettes : 0.577 (± 0.056)
  50 étiquettes : 0.782 (± 0.042)
 100 étiquettes : 0.874 (± 0.010)
 200 étiquettes : 0.927 (± 0.008)
 400 étiquettes : 0.947 (± 0.009)
 800 étiquettes : 0.962 (± 0.003)
avec les 1347 étiquettes : 0.969
à 10 étiquettes, de 0.331 à 0.571 selon le tirage
figure : ch08-courbe-supervisee.png
```

![Précision d'une régression logistique sur le jeu de test des chiffres manuscrits, selon le nombre d'images étiquetées (moyenne et écart-type sur 10 tirages ; échelle logarithmique en abscisse). La courbe monte très vite avec les premières étiquettes puis s'aplatit vers la valeur obtenue avec toutes les étiquettes.](figures/ch08-courbe-supervisee.png)

Trois lectures de cette courbe :

- **Elle est très raide au début.** Avec 10 étiquettes, la précision est de **0,43** ; avec 50, de **0,78** ; avec 100, de **0,87**. C'est dans ce régime que les méthodes de ce chapitre ont le plus à offrir.
- **Elle s'aplatit ensuite.** Avec 200 étiquettes, **0,93** ; avec les 1 347, **0,97**. Passé un certain budget, les étiquettes supplémentaires rapportent peu : l'apprentissage actif (8.3) cherche à *atteindre plus vite* ce plateau.
- **L'écart entre tirages est énorme à petit budget** : **± 0,08** à 10 étiquettes, contre ± 0,01 à 100. Sur nos dix tirages de 10 étiquettes, la précision va de **0,33** à **0,57** : un tirage isolé pourrait nous faire croire à n'importe quelle valeur dans cet intervalle. C'est pourquoi on **répète** les tirages.

> ✅ **À retenir.**
> - Le semi-supervisé utilise les points **sans étiquette** pour apprendre la forme de $p(x)$ ; l'actif choisit **quels points faire étiqueter**.
> - Les données sans étiquette n'aident que si $p(x)$ renseigne sur les classes : hypothèses de **lissage**, de **groupes**, de **basse densité**, de **variété**. Même méthode, même budget : gain sur des lunes entrelacées, rien sur des nuages qui se chevauchent.
> - Une méthode ne vaut que par rapport au **modèle supervisé entraîné sur les mêmes étiquettes**. Des étiquettes mal réparties peuvent faire **perdre** à une méthode ce qu'elle gagnait.
> - L'outil de mesure est la **courbe d'apprentissage selon le budget d'étiquettes** : jeu de test fixe, tirages répétés, **mêmes étiquettes** pour toutes les méthodes, moyenne et écart-type.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.1, exercices 8.1 à 8.3.
