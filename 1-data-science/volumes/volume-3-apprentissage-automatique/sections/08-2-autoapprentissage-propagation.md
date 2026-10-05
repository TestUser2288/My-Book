## 8.2 Auto-apprentissage et propagation d'étiquettes

Deux familles de méthodes concrètes exploitent les points sans étiquette. L'**auto-apprentissage** laisse le modèle étiqueter lui-même les cas dont il est sûr, puis s'entraîne dessus. La **propagation d'étiquettes** fait au contraire « couler » les étiquettes connues le long d'un graphe de similarité. Nous les construisons à la main, puis nous les mesurons sur nos deux jeux, avec les courbes d'apprentissage de la section 8.1.5.

### 8.2.1 L'auto-apprentissage

L'idée est celle du bon élève qui se corrige tout seul : on entraîne un premier modèle sur les rares étiquettes, on lui fait **prédire** les points sans étiquette, on garde les prédictions dont il est **très sûr**, on les ajoute au jeu d'entraînement comme si elles étaient vraies (on parle de **pseudo-étiquettes**), et on recommence.

> 📐 **Algorithme d'auto-apprentissage** (*self-training*), avec un seuil de confiance $\tau\in]0,1[$ :
> 1. Entraîner le modèle $f$ sur $\mathcal L$.
> 2. Calculer, pour chaque $x_j\in\mathcal U$, la classe prédite $\hat y_j$ et la confiance $p_j=\max_c P(c\mid x_j)$.
> 3. Pour chaque $j$ tel que $p_j\ge\tau$ : ajouter $(x_j,\hat y_j)$ à $\mathcal L$ et retirer $x_j$ de $\mathcal U$.
> 4. Recommencer à l'étape 1 jusqu'à ce qu'aucun point ne dépasse le seuil (ou qu'on ait atteint un nombre maximal de tours).

Le modèle de base peut être **n'importe quel** classifieur capable de donner des probabilités. Avec scikit-learn, c'est une enveloppe autour de ce modèle, et il suffit de passer le tableau complet avec les étiquettes partielles (convention `-1`, introduction du chapitre) :

```python hide
rng = np.random.default_rng(100)
indices_etiquetes = rng.choice(len(Xp), 50, replace=False)        # 50 images « étiquetées » parmi 1 347
y_partiel = np.full(len(Xp), -1)
y_partiel[indices_etiquetes] = yp[indices_etiquetes]
```

```python
from sklearn.semi_supervised import SelfTrainingClassifier

base = LogisticRegression(max_iter=2000)
auto = SelfTrainingClassifier(base, threshold=0.9).fit(Xp, y_partiel)
seul = LogisticRegression(max_iter=2000).fit(Xp[indices_etiquetes], yp[indices_etiquetes])
print("auto-apprentissage :", round(auto.score(Xt, yt), 3), "| supervisé seul :", round(seul.score(Xt, yt), 3))
```
<!--sortie-->
```text
auto-apprentissage : 0.831 | supervisé seul : 0.831
```

Sur ce tirage de 50 étiquettes, l'auto-apprentissage fait **exactement aussi bien** que le modèle supervisé seul (0,831 des deux côtés) : il n'a rien apporté. Un seul tirage ne prouve rien, dans un sens comme dans l'autre. Mesurons sur 10 tirages, en faisant varier le seuil. Pour chaque seuil, nous indiquons aussi **combien** de pseudo-étiquettes ont été ajoutées et **quelle part était juste** (on la connaît, car nous avons caché les vraies étiquettes sans les perdre).

```python hide
lignes = []
for seuil in (0.6, 0.8, 0.9, 0.95, 0.99):
    acc, nb, prec = [], [], []
    for s in range(10):
        rng = np.random.default_rng(100 + s)
        idx = rng.choice(len(Xp), 50, replace=False)
        y_part = np.full(len(Xp), -1)
        y_part[idx] = yp[idx]
        st = SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=seuil).fit(Xp, y_part)
        pseudo = st.labeled_iter_ > 0
        acc.append(st.score(Xt, yt)); nb.append(pseudo.sum())
        prec.append((st.transduction_[pseudo] == yp[pseudo]).mean() if pseudo.sum() else np.nan)
    lignes.append((seuil, np.mean(acc), np.mean(nb), np.nanmean(prec) if not np.all(np.isnan(prec)) else np.nan))
sup50 = courbe[2].mean()                     # supervisé seul à 50 étiquettes (8.1.5)
tab = pd.DataFrame(lignes, columns=["seuil", "précision test", "pseudo-étiquettes ajoutées", "part juste"]).round(3)
print(tab.to_string(index=False))
print("supervisé seul, 50 étiquettes :", round(sup50, 3))
```
<!--sortie-->
```text
 seuil  précision test  pseudo-étiquettes ajoutées  part juste
  0.60           0.759                      1216.5       0.783
  0.80           0.593                       888.4       0.734
  0.90           0.706                       175.6       0.912
  0.95           0.781                         2.4       1.000
  0.99           0.782                         0.0         NaN
supervisé seul, 50 étiquettes : 0.782
```

| Seuil $\tau$ | Précision sur le test | Pseudo-étiquettes ajoutées (moyenne) | Part des pseudo-étiquettes qui sont justes |
|---:|---:|---:|---:|
| 0,60 | 0,759 | 1 216 | 0,783 |
| 0,80 | 0,593 | 888 | 0,734 |
| 0,90 | 0,706 | 176 | 0,912 |
| 0,95 | 0,781 | 2 | 1,000 |
| 0,99 | 0,782 | 0 | (aucune) |

Le modèle supervisé seul, avec les mêmes 50 étiquettes, atteint **0,782**. Aucun seuil ne fait **mieux**. Les deux extrêmes sont instructifs :

- à $\tau=0{,}99$ et $\tau=0{,}95$, le modèle n'est jamais assez sûr de lui : presque aucune pseudo-étiquette n'est ajoutée, et le résultat est celui du supervisé seul (**0,78**) ;
- à $\tau=0{,}6$ ou $0{,}8$, le modèle ajoute **plusieurs centaines** de pseudo-étiquettes dont **environ un cinquième à un quart sont fausses** (0,78 et 0,73 justes) : il apprend sur ses propres erreurs.

Le seuil intermédiaire de 0,90 est le plus dangereux de façon trompeuse : 91 % des 176 pseudo-étiquettes sont justes, mais celles qui sont fausses sont **faussement confiantes**, et la précision finale baisse tout de même à 0,71.

### 8.2.2 Pourquoi l'auto-apprentissage peut s'auto-tromper

Ce qui précède n'est pas un accident de réglage : c'est le **biais de confirmation** de la méthode. Trois mécanismes s'additionnent.

1. **Une confiance qui n'est pas une probabilité.** Un modèle logistique entraîné sur 50 images en 64 dimensions est typiquement **trop sûr de lui** : il annonce 0,95 là où il se trompe un cas sur cinq. Un seuil de 0,9 sur une probabilité mal calibrée (section 5.2) n'est pas un seuil de 90 % de réussite.
2. **L'erreur devient une donnée.** Une fausse pseudo-étiquette entre dans le jeu d'entraînement avec le même poids qu'une vraie. Le tour suivant, le modèle s'y adapte, et il devient *plus* sûr de lui sur des points voisins : l'erreur se **renforce** au lieu de se corriger.
3. **La classe déjà majoritaire s'étend.** Reprenons le jeu d'étiquettes déséquilibré de 8.1.4 (39 % de « 0 » parmi les étiquettes, contre 10 % dans la population). Regardons de quelles classes sont les pseudo-étiquettes ajoutées.

```python hide
pred0, vrai0, nb_pseudo = [], [], []
w = np.array([6] + [1] * 9, float)
for s in range(10):
    rng = np.random.default_rng(300 + s)
    idx = rng.choice(len(yp), 50, replace=False, p=w[yp] / w[yp].sum())
    y_part = np.full(len(yp), -1)
    y_part[idx] = yp[idx]
    st = SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=0.9).fit(Xp, y_part)
    ps = st.labeled_iter_ > 0
    nb_pseudo.append(ps.sum()); pred0.append((st.transduction_[ps] == 0).mean()); vrai0.append((yp[ps] == 0).mean())
print("pseudo-étiquettes ajoutées (moyenne) :", round(np.mean(nb_pseudo)))
print("part prédite « 0 » parmi elles :", round(np.nanmean(pred0), 3), "| part réellement « 0 » :", round(np.nanmean(vrai0), 3), "| part de « 0 » dans la population :", round((yp == 0).mean(), 3))
```
<!--sortie-->
```text
pseudo-étiquettes ajoutées (moyenne) : 150
part prédite « 0 » parmi elles : 0.875 | part réellement « 0 » : 0.85 | part de « 0 » dans la population : 0.099
```

En moyenne, **88 %** des pseudo-étiquettes ajoutées sont des « 0 » (et 85 % de ces points sont réellement des 0 : le modèle ne se trompe pas beaucoup sur eux), alors que les « 0 » ne forment que 10 % des images. Les points que le modèle juge sûrs sont, de très loin, ceux de la classe qu'il a le plus vue : il l'ajoute massivement à son jeu d'entraînement, le déséquilibre initial **s'aggrave** (c'est l'explication la plus plausible, que nous n'avons pas isolée par une expérience dédiée), et la précision tombe à 0,65 (section 8.1.4).

> ⚠️ **Quand l'auto-apprentissage peut fonctionner.** Il a ses bons cas : quand le modèle initial est déjà **bon** (de l'ordre de 90 % de précision) et que les groupes sont bien séparés, ajouter ses cas faciles élargit un peu la base sans la polluer. Mais c'est exactement le cas où l'on a le *moins* besoin du semi-supervisé. Avec très peu d'étiquettes et un modèle médiocre, il est le plus dangereux.

Quelques garde-fous usuels : un seuil **élevé** ; une probabilité **calibrée** (section 5.2) ; ajouter des pseudo-étiquettes **par classe** en proportion de leur fréquence attendue plutôt que par seuil global ; ne jamais s'évaluer sur les pseudo-étiquettes ; et surtout **comparer au supervisé seul sur les mêmes étiquettes**.

### 8.2.3 Le co-apprentissage

Le **co-apprentissage** (*co-training*) est une variante qui limite le biais de confirmation en faisant s'entraider **deux** modèles. On suppose que chaque observation possède **deux « vues »** $x=(x^{(1)},x^{(2)})$, c'est-à-dire deux jeux de variables, et que :

1. **chaque vue suffit** à prédire la classe (chacune porte assez d'information pour un modèle correct) ;
2. les deux vues sont **indépendantes sachant la classe**.

On entraîne un modèle par vue ; chacun étiquette les points sans étiquette dont il est le plus sûr, et **ces pseudo-étiquettes servent à entraîner l'autre**. L'idée est qu'une erreur du premier modèle est, par indépendance, un cas « ordinaire » pour le second, qui peut la corriger.

L'exemple de référence est celui d'une page web, décrite par son **texte** et par les **liens qui pointent vers elle**. Pour la boutique, on pourrait imaginer décrire un client par son **comportement d'achat** d'un côté et par son **profil déclaré** (âge, ville) de l'autre, si chacun suffisait à prédire un attribut.

Les conditions sont **exigeantes** et rarement réunies. Sur nos chiffres manuscrits, on peut tenter de prendre comme vues la **moitié haute** et la **moitié basse** de l'image : aucune des deux moitiés ne suffit à elle seule, et elles sont fortement dépendantes (elles décrivent le même tracé). Le cahier propose cet essai (application 8.4) ; il se solde par un **échec instructif**, bien pire que le supervisé seul. C'est la leçon à retenir : une méthode dont les hypothèses ne sont pas vérifiées n'est pas « un peu moins efficace », elle peut être franchement nuisible.

### 8.2.4 Propager les étiquettes le long d'un graphe

Changeons de point de vue. Au lieu d'un modèle qui se prédit lui-même, construisons un **graphe de similarité** entre *tous* les points (étiquetés ou non) et laissons les étiquettes **se diffuser** de proche en proche, comme de l'encre dans un réseau de canaux.

**Le graphe.** Chaque observation est un **nœud**. On relie deux nœuds proches : par exemple chaque point à ses $k$ plus proches voisins. On obtient une matrice de **poids** $W$ ($W_{ij}>0$ si $i$ et $j$ sont voisins, 0 sinon, $W$ symétrique), les **degrés** $d_i=\sum_jW_{ij}$, et la matrice normalisée
$$S=D^{-1/2}\,W\,D^{-1/2},\qquad S_{ij}=\frac{W_{ij}}{\sqrt{d_i\,d_j}}.$$

**La diffusion.** Notons $Y$ la matrice des étiquettes ($n\times c$) : la ligne $i$ vaut le vecteur indicateur de la classe si $i$ est étiqueté, et zéro sinon. On part de $F^{(0)}=Y$ et on répète
$$F^{(t+1)}=\alpha\,S\,F^{(t)}+(1-\alpha)\,Y,\qquad \alpha\in]0,1[.$$
À chaque tour, chaque nœud reçoit une moyenne pondérée des scores de ses voisins (le terme $\alpha SF$), tout en gardant une part $(1-\alpha)$ de son étiquette d'origine (ce qui empêche les étiquettes connues de se diluer). À la fin, chaque nœud reçoit la classe de **plus grand score** : $\hat y_i=\arg\max_c F_{ic}$. C'est l'algorithme de **propagation** (ou d'*étalement*, *label spreading*) de Zhou et coll.

> 📐 **Pourquoi cela converge, et vers quoi.** Le point clé est que les valeurs propres de $S$ sont dans $[-1,1]$. En effet, $S=D^{-1/2}WD^{-1/2}$ est **semblable** à $P=D^{-1}W$ (puisque $S=D^{1/2}PD^{-1/2}$), et $P$ est une matrice **stochastique** (ses lignes sont positives et somment à 1), dont les valeurs propres sont de module au plus 1. Le rayon spectral de $\alpha S$ est donc au plus $\alpha<1$. En dépliant la récurrence :
> $$F^{(t)}=(\alpha S)^tY+(1-\alpha)\sum_{s=0}^{t-1}(\alpha S)^sY\ \xrightarrow[t\to\infty]{}\ F^*=(1-\alpha)\,(I-\alpha S)^{-1}\,Y,$$
> car $(\alpha S)^t\to0$ et la série de Neumann $\sum_s(\alpha S)^s$ converge vers $(I-\alpha S)^{-1}$. **On n'a donc pas besoin d'itérer** : une résolution de système linéaire suffit.
>
> **Ce que l'on minimise.** $F^*$ est l'unique minimiseur de
> $$J(F)=\tfrac12\sum_{i,j}W_{ij}\Bigl\|\tfrac{F_i}{\sqrt{d_i}}-\tfrac{F_j}{\sqrt{d_j}}\Bigr\|^2+\mu\,\|F-Y\|_F^2,\qquad \mu=\tfrac{1-\alpha}{\alpha}.$$
> Le premier terme est un terme de **lissage** : il est petit quand deux nœuds proches ont des scores proches (c'est l'hypothèse de lissage de 8.1.3). Le second est un terme de **fidélité** : il demande de ne pas trop s'éloigner des étiquettes connues. En développant, le premier terme vaut $\operatorname{tr}\bigl(F^\top(I-S)F\bigr)$, et annuler le gradient donne $(I-S)F+\mu(F-Y)=0$, soit $F=\frac{\mu}{1+\mu}\bigl(I-\frac{1}{1+\mu}S\bigr)^{-1}Y$, ce qui est exactement $F^*$ avec $\alpha=1/(1+\mu)$.

**Un exemple à la main : six nœuds.** Deux triangles reliés par une seule arête : les nœuds $1,2,3$ d'un côté, $4,5,6$ de l'autre, et l'arête $3$–$4$ au milieu. Le nœud 1 est étiqueté **A**, le nœud 6 est étiqueté **B**, les quatre autres ne le sont pas. Les degrés sont $d=(2,2,3,3,2,2)$. Les poids normalisés dont nous avons besoin sont

$$S_{12}=\frac1{\sqrt{2\cdot2}}=0{,}5,\qquad S_{13}=S_{23}=\frac1{\sqrt{2\cdot3}}\approx0{,}408,\qquad S_{34}=\frac1{\sqrt{3\cdot3}}=\tfrac13,$$

et symétriquement de l'autre côté ($S_{56}=0{,}5$, $S_{45}=S_{46}\approx0{,}408$). Prenons $\alpha=0{,}5$. Calculons le premier tour pour la colonne de la classe A, en partant de $F^{(0)}_A=(1,0,0,0,0,0)$ :

- nœud 1 : $0{,}5\cdot(S_{12}\cdot0+S_{13}\cdot0)+0{,}5\cdot1=0{,}5$ ;
- nœud 2 : $0{,}5\cdot S_{21}\cdot1+0=0{,}5\cdot0{,}5=0{,}25$ ;
- nœud 3 : $0{,}5\cdot S_{31}\cdot1=0{,}5\cdot0{,}408\approx0{,}204$ ;
- nœuds 4, 5, 6 : aucun voisin n'a encore de score A : $0$.

Le score A est passé du nœud 1 à ses deux voisins, **atténué** par la distance. Au deuxième tour, il atteint le nœud 4 (à travers l'arête $3$–$4$), toujours très faiblement. Les deux colonnes se calculent ensemble ; en laissant converger (ou en résolvant directement $F^*$), on obtient :

```python hide
W6 = np.zeros((6, 6))
for i, j in [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]:
    W6[i, j] = W6[j, i] = 1
d6 = W6.sum(axis=1)
S6 = W6 / np.sqrt(np.outer(d6, d6))
Y6 = np.zeros((6, 2)); Y6[0, 0] = 1; Y6[5, 1] = 1
al = 0.5
F = Y6.copy()
tours = [F.copy()]
for _ in range(3):
    F = al * S6 @ F + (1 - al) * Y6
    tours.append(F.copy())
Fstar = (1 - al) * np.linalg.inv(np.eye(6) - al * S6) @ Y6
print("tour 1, colonne A :", tours[1][:, 0].round(3))
print("tour 2, colonne A :", tours[2][:, 0].round(3))
print("solution exacte F* (A, B) :")
print(np.c_[np.arange(1, 7), Fstar.round(3)])
print("classes :", np.array(list("AB"))[Fstar.argmax(axis=1)])
print("plus grande valeur propre de S :", round(np.linalg.eigvalsh(S6).max(), 6))

from matplotlib.colors import to_rgb
fig, ax = plt.subplots(figsize=(7.2, 3.6))
pos = {0: (0, 1), 1: (0, -1), 2: (1.3, 0), 3: (3.0, 0), 4: (4.3, 1), 5: (4.3, -1)}
for i in range(6):
    for j in range(i + 1, 6):
        if W6[i, j]:
            ax.plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]], color=MUET, lw=1.4, zorder=1)
decalage = {0: (-0.35, "right"), 1: (-0.35, "right"), 2: (0, "center"), 3: (0, "center"), 4: (0.35, "left"), 5: (0.35, "left")}
for i in range(6):
    a_, b_ = Fstar[i]
    base = np.array(to_rgb(BLEU if a_ >= b_ else ORANGE))
    force = 0.3 + 0.7 * max(a_, b_) / Fstar.max()
    ax.scatter(*pos[i], s=1500, color=tuple(force * base + (1 - force) * np.ones(3)), edgecolor="white", linewidth=2, zorder=2)
    ax.text(pos[i][0], pos[i][1], f"{i + 1}", ha="center", va="center", fontsize=12, color="white", fontweight="bold", zorder=3)
    dx, ha = decalage[i]
    dy = -0.62 if i in (2, 3) else 0
    ax.text(pos[i][0] + dx, pos[i][1] + dy, f"A {a_:.2f}\nB {b_:.2f}", ha=ha, va="top" if i in (2, 3) else "center", fontsize=8.5, color=ENCRE2)
ax.text(0, 1.55, "étiquette A", ha="center", fontsize=9.5, color=BLEU)
ax.text(4.3, -1.75, "étiquette B", ha="center", fontsize=9.5, color=ORANGE)
ax.set_xlim(-1.4, 5.6); ax.set_ylim(-2.2, 2.0); ax.axis("off")
plt.tight_layout()
style.save(fig, "ch08-propagation-graphe.png")
```
<!--sortie-->
```text
tour 1, colonne A : [0.5   0.25  0.204 0.    0.    0.   ]
tour 2, colonne A : [0.604 0.167 0.153 0.034 0.    0.   ]
solution exacte F* (A, B) :
[[1.    0.577 0.008]
 [2.    0.177 0.008]
 [3.    0.159 0.03 ]
 [4.    0.03  0.159]
 [5.    0.008 0.177]
 [6.    0.008 0.577]]
classes : ['A' 'A' 'A' 'B' 'B' 'B']
plus grande valeur propre de S : 1.0
figure : ch08-propagation-graphe.png
```

| Nœud | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Score A | 0,577 | 0,177 | 0,159 | 0,030 | 0,008 | 0,008 |
| Score B | 0,008 | 0,008 | 0,030 | 0,159 | 0,177 | 0,577 |
| **Classe** | A | A | A | B | B | B |

![Propagation d'étiquettes sur six nœuds : deux triangles reliés par une arête. Seuls les nœuds 1 (classe A) et 6 (classe B) sont étiquetés. Les scores finaux (A et B) sont indiqués sous chaque nœud ; l'intensité de la couleur suit le score le plus élevé.](figures/ch08-propagation-graphe.png)

La classe attribuée à chaque nœud correspond à la **forme du graphe** : les trois nœuds du triangle de gauche reçoivent A, ceux de droite reçoivent B. Remarquez que le nœud 3, voisin direct du nœud 4 et donc exposé aux deux classes, penche malgré tout (0,159 contre 0,030) du côté de son triangle : l'étiquette s'est propagée **à l'intérieur** des groupes bien plus qu'**entre** eux, parce qu'il y a beaucoup de liens dans chaque triangle et un seul au milieu. C'est exactement l'hypothèse des groupes de 8.1.3.

### 8.2.5 La propagation sur les chiffres manuscrits

Passons à la pratique. Pour les chiffres, le graphe relie chaque image à ses **7 plus proches voisins** (distance euclidienne entre les 64 pixels). Voici l'appel, comme pour l'auto-apprentissage :

```python
from sklearn.semi_supervised import LabelSpreading

prop = LabelSpreading(kernel="knn", n_neighbors=7, alpha=0.2).fit(Xp, y_partiel)
print("propagation :", round(prop.score(Xt, yt), 3), "| auto-apprentissage :", round(auto.score(Xt, yt), 3), "| supervisé seul :", round(seul.score(Xt, yt), 3))
```
<!--sortie-->
```text
propagation : 0.949 | auto-apprentissage : 0.831 | supervisé seul : 0.831
```

Sur ce même tirage de 50 étiquettes, la propagation atteint **0,95** de précision, contre 0,83 pour le supervisé seul et pour l'auto-apprentissage. Un seul tirage ne prouve rien : voici la courbe d'apprentissage complète, avec les **mêmes étiquettes** pour les trois méthodes, 10 tirages par budget.

```python hide
bud = [10, 20, 50, 100, 200]
cs = o.courbe_semi(Xp, yp, Xt, yt, bud, graines=10)
for nom, v in cs.items():
    print(f"{nom:12s}", " ".join(f"{m:.3f}±{s:.3f}" for m, s in zip(v.mean(axis=1), v.std(axis=1))))
gain = cs["propagation"] - cs["supervise"]
print("gain moyen de la propagation :", np.round(gain.mean(axis=1), 3), "| tirages où la propagation fait mieux :", (gain > 0).sum(axis=1).tolist(), "sur 10")

fig, ax = plt.subplots(figsize=(7.6, 4.4))
for nom, couleur, etiq in [("supervise", BLEU, "supervisé seul"), ("auto", ROUGE, "auto-apprentissage (seuil 0,9)"), ("propagation", AQUA, "propagation (7 voisins)")]:
    m, s = cs[nom].mean(axis=1), cs[nom].std(axis=1)
    ax.fill_between(bud, m - s, m + s, color=couleur, alpha=0.14)
    ax.plot(bud, m, "o-", color=couleur, lw=2, label=etiq)
ax.set_xscale("log"); ax.set_xticks(bud); ax.set_xticklabels(bud)
ax.set_xlabel("nombre d'étiquettes disponibles (échelle logarithmique)")
ax.set_ylabel("précision sur le jeu de test")
ax.set_ylim(0.3, 1.0)
ax.legend(frameon=False, loc="lower right")
ax.set_title("Chiffres manuscrits : trois façons d'utiliser les mêmes étiquettes")
plt.tight_layout()
style.save(fig, "ch08-courbes-semi.png")
```
<!--sortie-->
```text
supervise    0.429±0.082 0.577±0.056 0.782±0.042 0.874±0.010 0.927±0.008
auto         0.429±0.082 0.577±0.056 0.706±0.082 0.840±0.019 0.923±0.007
propagation  0.540±0.083 0.779±0.075 0.913±0.041 0.940±0.013 0.966±0.006
gain moyen de la propagation : [0.111 0.202 0.131 0.066 0.039] | tirages où la propagation fait mieux : [10, 10, 10, 10, 10] sur 10
figure : ch08-courbes-semi.png
```

![Précision sur le jeu de test des chiffres manuscrits selon le nombre d'étiquettes, pour le modèle supervisé seul, l'auto-apprentissage et la propagation d'étiquettes (moyenne et écart-type sur 10 tirages, mêmes étiquettes pour les trois méthodes). La propagation domine nettement à petit budget ; l'auto-apprentissage ne fait pas mieux que le supervisé.](figures/ch08-courbes-semi.png)

| Étiquettes | 10 | 20 | 50 | 100 | 200 |
|---|---:|---:|---:|---:|---:|
| Supervisé seul | 0,429 | 0,577 | 0,782 | 0,874 | 0,927 |
| Auto-apprentissage ($\tau=0{,}9$) | 0,429 | 0,577 | 0,706 | 0,840 | 0,923 |
| **Propagation** | **0,540** | **0,779** | **0,913** | **0,940** | **0,966** |

Trois constats :

- Avec **20 étiquettes**, la propagation gagne **20 points** de précision sur le modèle supervisé (0,78 contre 0,58) ; avec 50, **13 points**. C'est considérable, et le gain est **plus grand là où la courbe supervisée est la plus raide** (8.1.5).
- Le gain **diminue avec le budget** : à 200 étiquettes, 4 points. Quand on a beaucoup d'étiquettes, la structure du graphe n'apprend plus grand-chose de neuf.
- La propagation fait mieux que le supervisé dans **les 10 tirages, à chacun des cinq budgets**.
- L'auto-apprentissage ne fait **jamais mieux** que le supervisé : il est à égalité aux petits budgets (le modèle n'est presque jamais sûr de lui) puis moins bon.

**Transductif ou inductif ?** Avec 50 étiquettes, la précision de la propagation sur les points sans étiquette *du réservoir* (c'est l'usage **transductif**) et sur le jeu de test (l'usage **inductif**, via `predict`) sont très voisines : respectivement 0,90 et 0,91 en moyenne. Pour un modèle destiné à prédire de nouveaux clients demain, il faut prévoir **de re-propager** (ou de remplacer la propagation par un classifieur entraîné sur ses étiquettes) : le graphe n'existe que sur les points qu'il contient.

```python hide
trans, induc = [], []
for s in range(10):
    rng = np.random.default_rng(100 + s)
    idx = rng.choice(len(Xp), 50, replace=False)
    y_part = np.full(len(Xp), -1)
    y_part[idx] = yp[idx]
    ls = LabelSpreading(kernel="knn", n_neighbors=7, alpha=0.2, max_iter=200).fit(Xp, y_part)
    libre = y_part == -1
    trans.append((ls.transduction_[libre] == yp[libre]).mean()); induc.append(ls.score(Xt, yt))
print("propagation, 50 étiquettes : transductif", round(np.mean(trans), 3), "| inductif", round(np.mean(induc), 3))
print("colonnes des clients :", Xc.shape[1], "dont", Xc.shape[1] - 15, "indicatrices")
```
<!--sortie-->
```text
propagation, 50 étiquettes : transductif 0.897 | inductif 0.913
colonnes des clients : 49 dont 34 indicatrices
```

**Les réglages comptent, surtout le nombre de voisins.** Avec 20 étiquettes, voici la précision selon $k$ (nombre de voisins) et $\alpha$ :

```python hide-code
res_k = {}
for k in (3, 7, 15, 30, 60):
    for al_ in (0.2, 0.9):
        sc = []
        for s in range(10):
            rng = np.random.default_rng(100 + s)
            idx = rng.choice(len(Xp), 20, replace=False)
            y_part = np.full(len(Xp), -1)
            y_part[idx] = yp[idx]
            sc.append(LabelSpreading(kernel="knn", n_neighbors=k, alpha=al_, max_iter=300).fit(Xp, y_part).score(Xt, yt))
        res_k[(k, al_)] = np.mean(sc)
tab_k = pd.DataFrame({"α = 0,2": [res_k[(k, 0.2)] for k in (3, 7, 15, 30, 60)], "α = 0,9": [res_k[(k, 0.9)] for k in (3, 7, 15, 30, 60)]},
                     index=pd.Index([3, 7, 15, 30, 60], name="voisins k")).round(3)
print(tab_k.to_string())
```
<!--sortie-->
```text
           α = 0,2  α = 0,9
voisins k                  
3            0.290    0.309
7            0.779    0.780
15           0.785    0.780
30           0.775    0.754
60           0.739    0.685
```

```python hide
atteints = {}
for k in (3, 7, 15):
    sans = []
    for s_ in range(10):
        rng = np.random.default_rng(100 + s_)
        idx = rng.choice(len(Xp), 20, replace=False)
        y_part = np.full(len(Xp), -1)
        y_part[idx] = yp[idx]
        D = LabelSpreading(kernel="knn", n_neighbors=k, alpha=0.2, max_iter=300).fit(Xp, y_part).label_distributions_
        sans.append((D.sum(axis=1)[y_part == -1] == 0).mean())
    atteints[k] = np.mean(sans)
print("part des points non étiquetés qui ne reçoivent AUCUN score (20 étiquettes) :", {k: round(v, 3) for k, v in atteints.items()})
```
<!--sortie-->
```text
part des points non étiquetés qui ne reçoivent AUCUN score (20 étiquettes) : {3: np.float64(0.858), 7: np.float64(0.131), 15: np.float64(0.005)}
```

- **$k=3$ est catastrophique** (0,29). Le graphe de scikit-learn est **orienté** : chaque image ne regarde que ses $k$ voisins, et une étiquette ne peut atteindre une image que si celle-ci compte un point déjà atteint parmi ses $k$ plus proches voisins. Avec $k=3$ et 20 étiquettes, **86 %** des images non étiquetées ne reçoivent **aucun score** (13 % avec $k=7$, 0,5 % avec $k=15$) : la méthode ne sait plus que dire. (Un graphe **symétrisé**, où l'on relie deux images dès que l'une est voisine de l'autre, ne souffre pas de ce défaut : voir l'application 8.3 du cahier.)
- **De $k=7$ à $k=30$**, le résultat est stable et bon (entre 0,75 et 0,79). C'est la zone où le graphe est connexe sans mélanger les classes.
- **À $k=60$**, les voisins deviennent trop lointains : des liens traversent les frontières entre chiffres et la précision recule (0,74 pour $\alpha=0{,}2$, 0,69 pour $\alpha=0{,}9$).
- Le paramètre $\alpha$ compte peu tant que $k$ est raisonnable.

> ⚠️ **Le coût.** Un graphe à noyau gaussien sur $n$ points est une matrice $n\times n$ dense : pour $n=100\,000$, c'est $10^{10}$ nombres, hors de portée. Le noyau **à $k$ plus proches voisins** (utilisé ici) est **creux** et passe à l'échelle. Quant au choix de $k$, on ne peut pas le régler par validation sur 20 étiquettes : on le choisit par principe (graphe connexe, $k$ de l'ordre de 7 à 15) et on le contrôle avec le diagnostic de la section suivante.

### 8.2.6 Quand le graphe ne dit rien : les clients de la boutique

La propagation brille sur les chiffres. Qu'en est-il sur les **clients de la boutique**, où l'on veut prédire la résiliation à 90 jours avec très peu d'étiquettes ? Même protocole : étiquettes tirées avec leurs proportions (14 % de résiliations ; au moins 2 positifs), mesure par l'**aire sous la courbe ROC** (AUC, section 5.1) puisque les classes sont déséquilibrées.

```python hide
from sklearn.metrics import roc_auc_score
lignes = []
for nl in (30, 100, 300):
    sup_t, st_t, ls_p, sup_p, couv = [], [], [], [], []
    for s in range(6):
        rng = np.random.default_rng(10 + s)
        idx = o.tirer_etiquettes(yc, nl, rng, stratifie=True)
        y_part = np.full(len(Xc), -1)
        y_part[idx] = yc[idx]
        lr = LogisticRegression(max_iter=2000).fit(Xc[idx], yc[idx])
        sup_t.append(roc_auc_score(yct, lr.predict_proba(Xct)[:, 1]))
        st_t.append(roc_auc_score(yct, SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=0.9).fit(Xc, y_part).predict_proba(Xct)[:, 1]))
        ls = LabelSpreading(kernel="knn", n_neighbors=10, alpha=0.2, max_iter=100).fit(Xc, y_part)
        D = ls.label_distributions_
        somme = D.sum(axis=1)
        atteint = (y_part == -1) & (somme > 0)                   # points non étiquetés que les étiquettes ont atteints
        score = D[:, 1] / np.where(somme > 0, somme, 1)
        ls_p.append(roc_auc_score(yc[atteint], score[atteint]))
        sup_p.append(roc_auc_score(yc[atteint], lr.predict_proba(Xc[atteint])[:, 1]))
        couv.append(atteint.sum() / (y_part == -1).sum())
    lignes.append((nl, np.mean(sup_t), np.mean(st_t), np.mean(sup_p), np.mean(ls_p), np.mean(couv)))
tab_c = pd.DataFrame(lignes, columns=["étiquettes", "supervisé (test)", "auto-appr. (test)", "supervisé (pool atteint)", "propagation (pool atteint)", "part du pool atteinte"]).round(3)
print(tab_c.to_string(index=False))
```
<!--sortie-->
```text
 étiquettes  supervisé (test)  auto-appr. (test)  supervisé (pool atteint)  propagation (pool atteint)  part du pool atteinte
         30             0.719              0.718                     0.705                       0.510                  0.741
        100             0.734              0.731                     0.727                       0.527                  0.956
        300             0.791              0.792                     0.787                       0.577                  1.000
```

| Étiquettes | Supervisé (AUC, test) | Auto-apprentissage (AUC, test) | Supervisé (AUC, points atteints) | **Propagation** (AUC, points atteints) | Part du réservoir atteinte |
|---:|---:|---:|---:|---:|---:|
| 30 | 0,719 | 0,718 | 0,705 | **0,510** | 74 % |
| 100 | 0,734 | 0,731 | 0,727 | **0,527** | 96 % |
| 300 | 0,791 | 0,792 | 0,787 | **0,577** | 100 % |

(La propagation est évaluée sur les clients non étiquetés que les étiquettes ont atteints, avec le supervisé évalué sur ces mêmes clients pour la comparaison : il y est à peu près identique à son résultat sur le test.)

Le verdict est net : l'auto-apprentissage **ne change rien**, et la propagation est **à peine meilleure que le hasard** (AUC de 0,51 à 0,58, pour 0,5 d'un tirage au sort) là où le supervisé atteint 0,71 à 0,79. Pourquoi ? Parce que l'hypothèse de 8.1.3 est fausse ici. Un diagnostic simple le montre : **à quel point les voisins d'un point partagent-ils son étiquette ?**

```python hide
from sklearn.neighbors import NearestNeighbors
def homophilie(X, y, k=7):
    idx = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X, return_distance=False)[:, 1:]
    meme = (y[idx] == y[:, None]).mean()
    hasard = ((np.bincount(y) / len(y)) ** 2).sum()
    return meme, hasard, y[idx[y == 1]].mean() if y.max() == 1 else np.nan
m_ch, h_ch, _ = homophilie(Xp, yp)
m_cl, h_cl, v_cl = homophilie(Xc, yc)
print(f"chiffres : {m_ch:.3f} des voisins ont la même étiquette (au hasard : {h_ch:.3f})")
print(f"clients  : {m_cl:.3f} des voisins ont la même étiquette (au hasard : {h_cl:.3f}) ; parmi les résiliations, {v_cl:.3f} des voisins résilient aussi (taux de base {yc.mean():.3f})")
```
<!--sortie-->
```text
chiffres : 0.969 des voisins ont la même étiquette (au hasard : 0.100)
clients  : 0.805 des voisins ont la même étiquette (au hasard : 0.759) ; parmi les résiliations, 0.269 des voisins résilient aussi (taux de base 0.140)
```

| | Voisins de même étiquette | Part attendue au hasard |
|---|---:|---:|
| **Chiffres** (7 voisins) | **96,9 %** | 10,0 % |
| **Clients** (7 voisins) | 80,5 % | 75,9 % |

Sur les chiffres, **97 %** des 7 plus proches voisins d'une image portent le même chiffre : le graphe est presque parfaitement « propre ». Sur les clients, **80,5 %** seulement, à peine plus que les **75,9 %** qu'on obtiendrait en choisissant des voisins au hasard (puisque 86 % des clients ne résilient pas). Parmi les clients qui résilient, 27 % seulement de leurs voisins résilient aussi (pour un taux de base de 14 %) : le lien existe, mais il est faible. La distance entre deux clients, calculée sur 49 variables (dont 34 colonnes indicatrices de villes, de canaux, d'appareils et de catégories) de natures très différentes, **ne reflète pas ce qui fait résilier** : un seuil sur la récence, une interaction entre tickets de support et retours, c'est-à-dire des seuils et des interactions que les arbres du chapitre 2 savent capturer, mais pas une distance Le graphe relie des clients qui se ressemblent *en apparence*, pas des clients qui se ressemblent *par leur risque*.

> 💡 **Un test à faire avant de propager.** Même avec peu d'étiquettes, on peut estimer ce taux d'**homophilie** : parmi les points *étiquetés* qui sont voisins l'un de l'autre, quelle part partage la même étiquette ? Comparez-le à la part attendue au hasard. S'il est proche, ne comptez pas sur la propagation. Une autre piste est d'apprendre **d'abord** une représentation adaptée (par exemple un modèle supervisé sur les étiquettes disponibles, puis un graphe construit sur ses sorties), mais cela sort du cadre de ce chapitre.

> ✅ **À retenir.**
> - L'**auto-apprentissage** ajoute les pseudo-étiquettes dont le modèle est sûr. Avec peu d'étiquettes et un modèle médiocre, il se confirme dans ses erreurs et **ne bat pas** le supervisé seul (chiffres, 50 étiquettes : jamais mieux que 0,78).
> - Les erreurs **se renforcent** (biais de confirmation) ; une classe déjà majoritaire s'étend. Garde-fous : seuil élevé, probabilités calibrées, comparaison systématique au supervisé sur les mêmes étiquettes.
> - Le **co-apprentissage** demande deux vues suffisantes et indépendantes : condition rarement réunie.
> - La **propagation d'étiquettes** diffuse les étiquettes sur un graphe de similarité ; elle se calcule en fermé, $F^*=(1-\alpha)(I-\alpha S)^{-1}Y$, et minimise lissage + fidélité. Sur les chiffres, **+20 points** à 20 étiquettes ; le réglage de $k$ est critique ($k=3$ morcelle le graphe).
> - Elle suppose que **les voisins se ressemblent par la classe** : sur les clients (80,5 % de voisins de même étiquette contre 75,9 % au hasard), elle échoue. **Mesurez l'homophilie avant de propager.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.2 à 8.5, exercices 8.4 à 8.6.
