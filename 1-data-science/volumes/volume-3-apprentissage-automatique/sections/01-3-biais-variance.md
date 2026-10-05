## 1.3 Compromis biais-variance et surapprentissage

Pourquoi un modèle très souple, capable d'épouser les moindres détails des données d'entraînement, prédit-il souvent **moins bien** qu'un modèle plus simple ? Et pourquoi un modèle trop simple échoue-t-il aussi ? Cette section répond par un résultat mathématique d'une grande élégance, la **décomposition biais-variance**, puis le montre à l'œuvre sur un exemple chiffré, sur des polynômes, et sur les données de la boutique.

### 1.3.1 Deux façons de se tromper

Imaginez un tireur à l'arc. Il peut mal viser **systématiquement** du même côté de la cible : ses flèches sont groupées, mais loin du centre. C'est un défaut de **biais**. Il peut aussi avoir la main qui tremble : ses flèches sont réparties autour du centre, sans direction privilégiée, mais très dispersées. C'est un défaut de **variance**. Un bon tireur a peu des deux ; entre deux tireurs mauvais, on ne peut pas dire lequel est « moins mauvais » sans savoir ce qu'on veut.

En apprentissage, la « cible » est la vraie relation $f(x)$ entre les variables d'entrée et ce qu'on prédit. Le « tireur » est **l'algorithme**, qui reçoit un jeu de données d'entraînement $D$ tiré au sort et produit un prédicteur $\hat f_D$. Si on lui donnait un autre jeu de données (d'autres clients, mêmes caractéristiques générales), il produirait un autre prédicteur. Deux questions se posent alors :

- **En moyenne** sur tous les jeux d'entraînement possibles, le prédicteur vise-t-il juste ? Sinon, il a un **biais**.
- D'un jeu à l'autre, le prédicteur change-t-il beaucoup ? Si oui, il a une grande **variance**.

### 1.3.2 Un exemple à la main : estimer une moyenne

Le plus petit exemple possible n'a pas de variables d'entrée. On veut estimer une grandeur inconnue $\mu=2$ (un panier moyen, en dizaines d'euros) à partir de $n=4$ observations de variance $\sigma^2=4$. L'estimateur habituel est la moyenne $\bar y$ : il est **sans biais** (en moyenne il vaut $\mu$) et sa variance est $\sigma^2/n=4/4=1$. Son erreur quadratique moyenne vaut donc $\mathrm{EQM}=\text{biais}^2+\text{variance}=0+1=1$.

Essayons maintenant un estimateur **volontairement biaisé** : $0{,}8\,\bar y$, qui « tire » la moyenne vers zéro.

- Son espérance vaut $0{,}8\mu=1{,}6$ : le **biais** est $1{,}6-2=-0{,}4$, donc $\text{biais}^2=0{,}16$.
- Sa variance vaut $0{,}8^2\times1=0{,}64$.
- Son erreur quadratique moyenne vaut $0{,}16+0{,}64=\mathbf{0{,}80}$.

**L'estimateur biaisé est meilleur que l'estimateur sans biais** (0,80 contre 1). On a accepté un petit biais en échange d'une forte baisse de variance. En général, l'estimateur $c\,\bar y$ a pour erreur $(c-1)^2\mu^2+c^2\sigma^2/n$, minimale pour
$$c^\star=\frac{\mu^2}{\mu^2+\sigma^2/n}=\frac{4}{4+1}=0{,}8.$$
Plus les données sont bruitées ($\sigma^2/n$ grand), plus il faut rétrécir. C'est exactement le principe de la **régularisation** (volume II, section 1.5) : on « tire » les coefficients vers zéro pour réduire la variance.

```python hide
rng = np.random.default_rng(0); mu, s2, n = 2.0, 4.0, 4
mbar = rng.normal(mu, np.sqrt(s2 / n), 400000)
print("EQM simulée : moyenne", ((mbar - mu) ** 2).mean().round(3), "| 0,8 x moyenne", ((0.8 * mbar - mu) ** 2).mean().round(3), "| c* =", mu ** 2 / (mu ** 2 + s2 / n))
```
<!--sortie-->
```text
EQM simulée : moyenne 1.003 | 0,8 x moyenne 0.802 | c* = 0.8
```

Une simulation de 400 000 tirages confirme : l'erreur quadratique moyenne vaut 1,00 pour la moyenne et 0,80 pour l'estimateur rétréci.

### 1.3.3 La décomposition biais-variance

Passons au cas général. On observe $y=f(x)+\varepsilon$, où $f$ est la vraie fonction, et $\varepsilon$ un bruit d'espérance nulle et de variance $\sigma^2$, indépendant du jeu d'entraînement $D$. Fixons un point $x$ et considérons la prédiction $\hat f(x)=\hat f_D(x)$, qui est aléatoire parce que $D$ l'est. L'erreur quadratique d'une nouvelle observation $y$ en ce point, **moyennée sur le bruit et sur le choix de $D$**, se décompose ainsi.

> 📐 **Théorème (décomposition biais-variance).**
> $$\mathbb E\bigl[(y-\hat f(x))^2\bigr]\;=\;\underbrace{\sigma^2}_{\text{bruit irréductible}}\;+\;\underbrace{\bigl(\mathbb E[\hat f(x)]-f(x)\bigr)^2}_{\text{biais}^2}\;+\;\underbrace{\mathbb E\bigl[(\hat f(x)-\mathbb E[\hat f(x)])^2\bigr]}_{\text{variance}}.$$
>
> *Démonstration.* Écrivons $y-\hat f=\varepsilon+(f-\hat f)$ et développons le carré :
> $$\mathbb E\bigl[(y-\hat f)^2\bigr]=\mathbb E[\varepsilon^2]+\mathbb E\bigl[(f-\hat f)^2\bigr]+2\,\mathbb E\bigl[\varepsilon\,(f-\hat f)\bigr].$$
> Le premier terme vaut $\sigma^2$. Le dernier est nul : $\varepsilon$ est indépendant de $\hat f$ (qui ne dépend que de $D$) et d'espérance nulle, donc $\mathbb E[\varepsilon(f-\hat f)]=\mathbb E[\varepsilon]\,\mathbb E[f-\hat f]=0$. Pour le terme central, ajoutons et retranchons $\mathbb E[\hat f]$ :
> $$f-\hat f=\bigl(f-\mathbb E[\hat f]\bigr)+\bigl(\mathbb E[\hat f]-\hat f\bigr).$$
> En développant, le double produit contient le facteur $\mathbb E\bigl[\mathbb E[\hat f]-\hat f\bigr]=0$ et disparaît, d'où
> $$\mathbb E\bigl[(f-\hat f)^2\bigr]=\bigl(f-\mathbb E[\hat f]\bigr)^2+\mathbb E\bigl[(\hat f-\mathbb E[\hat f])^2\bigr]=\text{biais}^2+\text{variance}.\quad\blacksquare$$

Trois lectures de cette formule :

1. Le terme $\sigma^2$ est un **plancher** : aucun modèle ne peut faire mieux que le bruit des données (on l'appelle l'erreur de Bayes dans le cas de la classification). Si une équipe annonce une erreur *inférieure* au bruit connu, elle s'est trompée ou a triché (fuite d'information, section 1.1.6).
2. Le biais mesure l'**écart systématique** entre ce que l'algorithme sait représenter et la réalité ; il baisse quand le modèle devient **plus souple**.
3. La variance mesure la **sensibilité** à l'échantillon ; elle augmente quand le modèle devient **plus souple** (plus de paramètres que de données pour les contraindre).

La conséquence est le **compromis biais-variance** : on ne peut pas minimiser les deux en même temps, et le meilleur modèle est un équilibre.

> ⚠️ **Deux précisions.** La décomposition ci-dessus est exacte pour l'**erreur quadratique**. Pour la classification (perte 0-1) il existe des décompositions analogues, mais plus délicates ; l'intuition reste valable. Et dans les modèles modernes très surdimensionnés (grands réseaux de neurones), on observe parfois que l'erreur de test **rebaisse** quand la complexité continue de croître (phénomène de « double descente ») : le compromis classique est un cadre précieux, pas une loi universelle.

### 1.3.4 Voir le compromis : un polynôme de degré croissant

Rendons cela visible. La vraie fonction est $f(x)=\sin(1{,}5\pi x)$ sur $[0;1]$ et le bruit a un écart-type $\sigma=0{,}3$ (donc $\sigma^2=0{,}09$). Un « jeu d'entraînement » contient 30 points tirés au hasard. Pour chaque degré de polynôme de 1 à 7, on **simule 500 jeux d'entraînement**, on ajuste un polynôme à chacun, et on mesure, en 200 points de $[0;1]$, le biais carré moyen et la variance moyenne de la prédiction.

```python hide
from numpy.polynomial import Polynomial
rng = np.random.default_rng(1); f_vrai = lambda x: np.sin(1.5 * np.pi * x); sig = 0.3; N = 30; R = 500; grille = np.linspace(0, 1, 200)
lignes = []; ex = {}
for d in range(1, 13):
    P = np.empty((R, len(grille)))
    for r in range(R):
        x = rng.uniform(0, 1, N); yy = f_vrai(x) + rng.normal(0, sig, N); P[r] = Polynomial.fit(x, yy, d)(grille)
    lignes.append((d, ((P.mean(0) - f_vrai(grille)) ** 2).mean(), P.var(0).mean()))
    if d in (1, 3, 7): ex[d] = P[:12]
tab = pd.DataFrame(lignes, columns=["degré", "biais²", "variance"]); tab["erreur attendue"] = tab["biais²"] + tab["variance"] + sig ** 2
print(tab[tab["degré"] <= 7].round(4).to_string(index=False))
print("degrés 8 et 9 : variance", tab.loc[7, "variance"].round(2), "et", tab.loc[8, "variance"].round(0))
fig, ax = plt.subplots(1, 4, figsize=(12.5, 3.0), gridspec_kw={"width_ratios": [1, 1, 1, 1.35]})
for a_, d in zip(ax[:3], (1, 3, 7)):
    for p in ex[d]: a_.plot(grille, p, color=BLEU, alpha=0.35, lw=1)
    a_.plot(grille, f_vrai(grille), color=ORANGE, lw=2); a_.set_ylim(-2.2, 2.2); a_.set_title(f"degré {d}", fontsize=10); a_.set_xlabel("x")
ax[0].set_ylabel("prédiction")
ax[3].plot(tab["degré"][:7], tab["biais²"][:7], color=VIOLET, label="biais²"); ax[3].plot(tab["degré"][:7], tab["variance"][:7], color=AQUA, label="variance")
ax[3].plot(tab["degré"][:7], tab["erreur attendue"][:7], color=ROUGE, lw=2.4, label="erreur attendue")
ax[3].axhline(sig ** 2, color=MUET, ls="--", lw=1, label="bruit irréductible")
ax[3].set_xlabel("degré du polynôme"); ax[3].legend(frameon=False, fontsize=8.5); ax[3].set_ylim(0, 0.55)
plt.tight_layout(); plt.savefig("figures/ch01-biais-variance.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
 degré  biais²  variance  erreur attendue
     1  0.1835    0.0241           0.2976
     2  0.0330    0.0166           0.1396
     3  0.0033    0.0175           0.1108
     4  0.0003    0.0252           0.1155
     5  0.0001    0.0758           0.1659
     6  0.0003    0.1434           0.2337
     7  0.0012    0.4150           0.5062
degrés 8 et 9 : variance 5.58 et 1906.0
```

![Biais et variance d'un polynôme de degré croissant. À gauche : 12 ajustements (bleu) de degré 1, 3 et 7 sur des jeux d'entraînement différents, et la vraie fonction (orange). À droite : biais carré, variance et erreur attendue en fonction du degré.](figures/ch01-biais-variance.png)

Les trois panneaux de gauche montrent des **paquets de flèches** : le degré 1 donne toujours à peu près la même droite, mais elle est loin de la courbe (biais fort, variance faible) ; le degré 7 donne des courbes très différentes d'un jeu à l'autre (variance forte) ; le degré 3 épouse bien la courbe, et d'un jeu à l'autre varie peu. À droite, le compromis : le biais s'effondre dès le degré 3, la variance croît, et l'erreur attendue est minimale au **degré 3** (0,111, à comparer au plancher de 0,09). Plus loin, la situation se dégrade vite : la variance dépasse 5 dès le degré 8 et 1 000 dès le degré 9, parce que, avec 30 points, un polynôme de degré 9 peut osciller sauvagement dans les zones sans donnée.

### 1.3.5 Sous-apprentissage, surapprentissage

Le vocabulaire courant désigne les deux extrémités :

- Le **sous-apprentissage** (*underfitting*) : le modèle est **trop rigide** pour représenter la structure des données ; le biais domine. Les erreurs d'entraînement **et** de validation sont élevées.
- Le **surapprentissage** (*overfitting*) : le modèle est **trop souple** ; il a appris le bruit de l'échantillon d'entraînement ; la variance domine. L'erreur d'entraînement est faible, l'erreur de validation beaucoup plus élevée.

Reproduisons cela sur les données de la boutique, avec un arbre de décision dont on fait croître la profondeur (un arbre plus profond pose plus de questions successives : c'est un modèle plus souple ; le chapitre 2 le détaille). Pour chaque profondeur de 1 à 20, on mesure l'AUC sur les données d'entraînement et par validation croisée.

```python hide
from sklearn.tree import DecisionTreeClassifier
arbre = make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(random_state=0))
prof = list(range(1, 21)); cv3 = StratifiedKFold(3, shuffle=True, random_state=0)
tr_, va_ = validation_curve(arbre, X_tr[NUM], y_tr, param_name="decisiontreeclassifier__max_depth", param_range=prof, cv=cv3, scoring="roc_auc")
mt, mv = tr_.mean(1), va_.mean(1); mb = int(mv.argmax())
print("meilleure profondeur", prof[mb], "| AUC validation", mv[mb].round(3), "| AUC entraînement à cette profondeur", mt[mb].round(3), "| profondeur 20 : entraînement", mt[-1].round(3), "validation", mv[-1].round(3), "| profondeur 1 : entraînement", mt[0].round(3), "validation", mv[0].round(3))
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.plot(prof, mt, color=BLEU, lw=2, label="entraînement"); ax.plot(prof, mv, color=ORANGE, lw=2, label="validation croisée")
ax.axvline(prof[mb], color=MUET, ls="--", lw=1); ax.text(prof[mb] + 0.3, 0.52, f"meilleure profondeur : {prof[mb]}", color=ENCRE2, fontsize=9)
ax.set_xlabel("profondeur de l'arbre (complexité du modèle)"); ax.set_ylabel("AUC"); ax.legend(frameon=False, loc="lower left"); ax.set_ylim(0.5, 1.02)
ax.annotate("sous-apprentissage", xy=(1.6, 0.74), color=ENCRE2, fontsize=9); ax.annotate("surapprentissage", xy=(13, 0.79), color=ENCRE2, fontsize=9)
plt.tight_layout(); plt.savefig("figures/ch01-complexite.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
meilleure profondeur 4 | AUC validation 0.864 | AUC entraînement à cette profondeur 0.882 | profondeur 20 : entraînement 1.0 validation 0.681 | profondeur 1 : entraînement 0.708 validation 0.708
```

![AUC d'un arbre de décision sur les données d'entraînement (bleu) et en validation croisée (orange) selon sa profondeur : sous-apprentissage à gauche, surapprentissage à droite.](figures/ch01-complexite.png)

C'est la signature classique : l'AUC d'entraînement ne fait que **monter** avec la complexité (elle atteint 1,00 : l'arbre profond a mémorisé tous les clients) ; l'AUC en validation monte, atteint un maximum à la profondeur **4** (0,864), puis **s'effondre** (0,68 à la profondeur 20). Un arbre de profondeur 20 est « parfait » sur ce qu'il a vu et à peine meilleur que le hasard sur ce qu'il n'a pas vu. Le choix de la complexité se lit **sur la courbe de validation**, jamais sur celle d'entraînement.

### 1.3.6 Les courbes d'apprentissage : diagnostiquer son modèle

La courbe précédente fait varier la complexité. Une **courbe d'apprentissage** fait varier la **quantité de données** d'entraînement, et répond à une question de gestionnaire : *« si on collectait deux fois plus de données, cela servirait-il ? »* On entraîne le modèle sur 200, 500, 1 000, 2 000, 4 000 puis 6 000 clients, et on trace l'AUC d'entraînement et de validation.

```python
from sklearn.model_selection import learning_curve

tailles, train, val = learning_curve(modele_logit(), X_tr, y_tr, train_sizes=[200, 1000, 6000], cv=3, scoring="roc_auc")[:3]
print(tailles, train.mean(1).round(3), val.mean(1).round(3))
```
<!--sortie-->
```text
[ 200 1000 6000] [0.935 0.887 0.868] [0.831 0.851 0.86 ]
```

```python hide
tailles = [200, 500, 1000, 2000, 4000, 6000]; courbes = {}
for nom, mod, Xm in [("régression logistique", modele_logit(), X_tr), ("gradient boosting", modele_hgb(), X_tr),
                     ("arbre de décision profond", make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(random_state=0)), X_tr[NUM])]:
    ts, trn, vl = learning_curve(mod, Xm, y_tr, train_sizes=tailles, cv=cv3, scoring="roc_auc")[:3]
    courbes[nom] = (trn.mean(1), vl.mean(1))
    print(nom, "| entraînement", trn.mean(1).round(3), "| validation", vl.mean(1).round(3))
fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.3), sharey=True)
for a_, (nom, (trn, vl)) in zip(ax, courbes.items()):
    a_.plot(tailles, trn, color=BLEU, lw=2, marker="o", ms=4, label="entraînement"); a_.plot(tailles, vl, color=ORANGE, lw=2, marker="o", ms=4, label="validation")
    a_.set_title(nom, fontsize=10); a_.set_xlabel("clients utilisés pour l'entraînement"); a_.set_xscale("log"); a_.set_xticks([200, 1000, 6000]); a_.set_xticklabels(["200", "1 000", "6 000"]); a_.minorticks_off()
ax[0].set_ylabel("AUC"); ax[0].legend(frameon=False, loc="lower right"); ax[0].set_ylim(0.6, 1.02)
plt.tight_layout(); plt.savefig("figures/ch01-courbes-apprentissage.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
régression logistique | entraînement [0.974 0.91  0.892 0.883 0.872 0.868] | validation [0.826 0.833 0.845 0.851 0.857 0.86 ]
gradient boosting | entraînement [1.    1.    1.    1.    1.    0.999] | validation [0.827 0.847 0.863 0.869 0.877 0.886]
arbre de décision profond | entraînement [1. 1. 1. 1. 1. 1.] | validation [0.657 0.651 0.675 0.686 0.677 0.682]
```

![Courbes d'apprentissage de trois modèles sur les données de la boutique : AUC d'entraînement (bleu) et de validation (orange) selon le nombre de clients utilisés pour l'entraînement.](figures/ch01-courbes-apprentissage.png)

Chaque forme se lit comme un diagnostic :

- **Régression logistique** : les deux courbes **se rejoignent** à un niveau modeste (0,87 et 0,86 avec 6 000 clients). Écart faible, performance plafonnée : le modèle est **trop rigide** (biais). Ajouter des clients n'aidera presque pas ; il faut un modèle plus expressif ou de meilleures variables.
- **Arbre profond** : l'AUC d'entraînement vaut 1,00 dès le départ, celle de validation reste autour de 0,65 à 0,69, même avec beaucoup de données : l'écart est immense (variance). Il faut **contraindre** le modèle (limiter la profondeur, section 1.3.5) ou le moyenner (forêts, chapitre 2).
- **Gradient boosting** : l'AUC d'entraînement est parfaite (1,00) mais **l'AUC de validation continue de monter** avec les données (de 0,83 à 0,89), signe que **plus de données aideraient**. L'écart entre les deux courbes est grand, mais ce n'est pas un défaut ici : ce qui compte est le niveau de la courbe de validation, que le boosting domine nettement.

> 💡 **Le piège de l'écart.** Un grand écart entre entraînement et validation n'est pas, à lui seul, la preuve d'un mauvais modèle : un modèle puissant peut mémoriser l'entraînement et très bien généraliser (c'est le cas du boosting ci-dessus). Ce qu'on regarde, c'est **la validation**, et si elle **progresse** quand on ajoute des données.

### 1.3.7 Que faire quand le modèle ne généralise pas ?

| Diagnostic | Symptôme | Remèdes |
|---|---|---|
| **Biais élevé** (sous-apprentissage) | entraînement et validation tous deux mauvais, courbes qui se rejoignent | modèle plus souple, **meilleures variables** (chapitre 4), moins de régularisation |
| **Variance élevée** (surapprentissage) | entraînement excellent, validation nettement inférieure | **plus de données**, modèle plus simple, **régularisation**, arrêt précoce (section 1.5), **moyenne de modèles** (bagging, chapitre 2) |
| **Bruit irréductible** | tous les modèles plafonnent au même niveau | accepter la limite ; chercher de **nouvelles informations** plutôt qu'un meilleur algorithme |

> ✅ **À retenir.**
> - $\mathbb E[(y-\hat f)^2]=\sigma^2+\text{biais}^2+\text{variance}$ : un plancher de bruit, une erreur systématique, une sensibilité à l'échantillon.
> - Rendre un modèle plus souple **réduit le biais et augmente la variance** ; le meilleur modèle est un **compromis**. Un estimateur légèrement biaisé peut battre un estimateur sans biais (exemple : $0{,}8\bar y$).
> - **Sous-apprentissage** : tout est mauvais. **Surapprentissage** : l'entraînement est excellent, la validation médiocre. On choisit la complexité sur la **courbe de validation**.
> - Une **courbe d'apprentissage** dit si l'on manque de données (la validation monte encore) ou de souplesse (les courbes se rejoignent à un niveau bas).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.7 et 1.8.
