## 1.1 Formulation du problème et séparation des données

Avant de choisir un algorithme, un projet d'apprentissage automatique commence par trois décisions qui pèsent plus lourd que n'importe quel hyperparamètre : **ce que l'on prédit** (et pour quelle ligne du tableau), **avec quelles informations** (et à quel moment), et **comment on jugera le résultat**. Cette section pose le cadre mathématique, puis montre pourquoi on met des données de côté et comment une erreur de formulation, la **fuite d'information**, peut faire passer un modèle inutilisable pour un excellent modèle.

### 1.1.1 Un exemple minuscule, entièrement à la main

Huit clients de la boutique, une variable (le nombre de jours depuis la dernière commande), et un modèle qui, pour chaque client, donne une **probabilité de départ** $\hat p$ :

| Client | Récence (jours) | Parti ? ($y$) | Probabilité prédite $\hat p$ |
|---|---:|---:|---:|
| A | 20 | 0 | 0,05 |
| B | 35 | 0 | 0,10 |
| C | 60 | 0 | 0,20 |
| D | 90 | 1 | 0,30 |
| E | 120 | 0 | 0,40 |
| F | 150 | 1 | 0,60 |
| G | 200 | 1 | 0,80 |
| H | 300 | 1 | 0,90 |

Comment dire si ce modèle est bon ? Cela dépend de **ce qu'on appelle « bon »**. Voici trois mesures, calculées à la main.

**Le taux d'erreur.** Prédisons « parti » quand $\hat p>0{,}5$. Le modèle prédit F, G, H comme partis, les autres comme restants. Il se trompe sur D (parti, prédit restant) seulement : 7 bonnes réponses sur 8, soit une **exactitude** de $7/8=0{,}875$.

**La perte logarithmique** (*log-loss*). Elle punit une probabilité confiante et fausse bien plus qu'une probabilité prudente et fausse :
$$\mathrm{LL}=-\frac18\sum_{i=1}^8\bigl[y_i\ln\hat p_i+(1-y_i)\ln(1-\hat p_i)\bigr].$$
Les huit termes $-\ln(\text{probabilité attribuée à ce qui s'est réellement passé})$ valent : A $-\ln0{,}95=0{,}051$ ; B $0{,}105$ ; C $0{,}223$ ; D $-\ln0{,}3=1{,}204$ ; E $-\ln0{,}6=0{,}511$ ; F $-\ln0{,}6=0{,}511$ ; G $0{,}223$ ; H $0{,}105$. Leur somme est $2{,}934$, d'où $\mathrm{LL}=2{,}934/8\approx0{,}367$. Remarquez que **D à lui seul pèse 41 %** du total : le modèle était assez sûr que D resterait (il lui donnait 30 % de risque) et il est parti.

**L'AUC.** C'est la probabilité qu'un client parti, tiré au hasard, ait reçu une probabilité **plus élevée** qu'un client resté tiré au hasard. Il y a $4\times4=16$ paires (parti, resté). Le client D (0,30) bat A, B, C mais pas E : 3 paires gagnées sur 4. F, G et H (0,60 ; 0,80 ; 0,90) battent les quatre clients restés : 12 paires sur 12. Total : $15/16=0{,}9375$.

```python hide
from sklearn.metrics import log_loss, accuracy_score, brier_score_loss
yy = np.array([0, 0, 0, 1, 0, 1, 1, 1]); pp = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 0.90])
print("exactitude", accuracy_score(yy, pp > 0.5), "| log-loss", round(log_loss(yy, pp), 4), "| Brier", round(brier_score_loss(yy, pp), 4), "| AUC", roc_auc_score(yy, pp))
termes = -np.log(np.where(yy == 1, pp, 1 - pp)); print("termes", termes.round(3), "somme", termes.sum().round(3), "part de D", (termes[3] / termes.sum()).round(3))
```
<!--sortie-->
```text
exactitude 0.875 | log-loss 0.3667 | Brier 0.1141 | AUC 0.9375
termes [0.051 0.105 0.223 1.204 0.511 0.511 0.223 0.105] somme 2.934 part de D 0.41
```

Trois mesures, trois lectures : 87,5 % de bonnes réponses, une perte de 0,367, une capacité à classer les clients de 0,94. Aucune n'est « la » vérité : elles répondent à des questions différentes (*combien de décisions justes ? les probabilités sont-elles bien dosées ? l'ordre est-il bon ?*). Garder cette idée en tête évite bien des malentendus.

### 1.1.2 Le cadre : prédire, perte, risque

Formalisons. Chaque observation est une paire $(x,y)$ : $x$ regroupe les **variables d'entrée** (les *features*) et $y$ la **cible**. On suppose que ces paires sont tirées indépendamment d'une même loi inconnue $P$. Un **prédicteur** est une fonction $f$ qui associe à $x$ une prédiction $f(x)$. Une **fonction de perte** $\ell(y,f(x))\ge0$ mesure le coût d'une prédiction (erreur au carré, perte logarithmique, erreur 0-1…).

Le **risque** de $f$ est sa perte moyenne **sur la population entière**, c'est-à-dire sur les clients à venir :
$$R(f)=\mathbb E_{(x,y)\sim P}\bigl[\ell(y,f(x))\bigr].$$
On ne peut pas le calculer, puisque $P$ est inconnue. On dispose seulement d'un échantillon $S=\{(x_i,y_i)\}_{i=1}^n$ et du **risque empirique**
$$\widehat R_S(f)=\frac1n\sum_{i=1}^n\ell\bigl(y_i,f(x_i)\bigr).$$
Apprendre, c'est choisir $\hat f$ dans une famille $\mathcal F$ de prédicteurs possibles (les droites, les arbres de profondeur 5, etc.) en minimisant $\widehat R_S$ : c'est la **minimisation du risque empirique**. Ce qui nous intéresse, cependant, est $R(\hat f)$, le risque **sur des clients que le modèle n'a pas vus**. L'écart $R(\hat f)-\widehat R_S(\hat f)$ s'appelle l'**erreur de généralisation**.

> 📐 **Pourquoi l'erreur d'entraînement est optimiste.** Deux faits, faciles à démontrer.
>
> **(1) Si $f$ ne dépend pas de l'échantillon $S$**, alors $\widehat R_S(f)$ est un estimateur **sans biais** de $R(f)$. En effet, par linéarité de l'espérance et parce que chaque $(x_i,y_i)$ suit la loi $P$ :
> $$\mathbb E\bigl[\widehat R_S(f)\bigr]=\frac1n\sum_i\mathbb E\bigl[\ell(y_i,f(x_i))\bigr]=R(f).$$
> C'est la situation d'un **jeu de test** : un prédicteur déjà figé, évalué sur des données qui ne l'ont pas influencé.
>
> **(2) Si $\hat f$ est choisi *en minimisant* $\widehat R_S$**, l'estimateur devient optimiste. Soit $f^\star$ le meilleur prédicteur de la famille au sens du vrai risque ($R(f^\star)\le R(f)$ pour tout $f\in\mathcal F$). Par construction $\widehat R_S(\hat f)\le\widehat R_S(f^\star)$ ; en prenant l'espérance et en utilisant le fait (1) pour le prédicteur **fixe** $f^\star$ :
> $$\mathbb E\bigl[\widehat R_S(\hat f)\bigr]\ \le\ \mathbb E\bigl[\widehat R_S(f^\star)\bigr]=R(f^\star)\ \le\ \mathbb E\bigl[R(\hat f)\bigr].$$
> Donc **en moyenne, l'erreur d'entraînement est inférieure à l'erreur réelle** de $\hat f$. Plus la famille $\mathcal F$ est riche, plus l'écart peut être grand. $\blacksquare$

Voilà la raison d'être de tout ce chapitre : **on ne peut pas juger un modèle sur les données qui ont servi à le construire.** Il faut des données *neuves*, ou des méthodes qui simulent la nouveauté (section 1.2).

### 1.1.3 La perte n'est pas la métrique

Deux notions voisines sont à distinguer, parce qu'on les confond tout le temps :

- La **perte** est ce que l'algorithme **minimise** pendant l'apprentissage. Elle doit être commode : dérivable, convexe si possible (la perte logarithmique pour une régression logistique, l'erreur quadratique pour une régression).
- La **métrique** est ce que l'**utilisateur** veut maximiser dans la vie réelle. Elle peut être discontinue, difficile à optimiser, et dépend du métier : « parmi les cent clients que la gérante appellera cette semaine, combien sont vraiment sur le point de partir ? »

| Question du métier | Perte typique pour l'apprentissage | Métrique de décision |
|---|---|---|
| Quels clients appeler ? | perte logarithmique | précision sur les 100 meilleurs scores |
| Combien de ventes le mois prochain ? | erreur quadratique | erreur moyenne en € (MAE) |
| Cette transaction est-elle frauduleuse ? | perte logarithmique pondérée | coût total des fraudes manquées et des fausses alertes |

Le chapitre 5 détaille les métriques. Retenons ici un **piège élémentaire** : l'exactitude (*accuracy*) trompe quand les classes sont déséquilibrées. Dans notre tableau, 14,0 % des clients partent ; un « modèle » qui répond toujours « il reste » obtient donc **86,0 % d'exactitude** sans rien avoir appris. Un score de 88 % n'a de sens que comparé à ce repère (section 1.4).

### 1.1.4 L'unité d'analyse et le moment de la prédiction

Un projet bien posé répond d'abord à quatre questions simples, que l'on s'oblige à écrire :

1. **Que représente une ligne ?** Ici : *un client, vu à une date donnée*. Ce n'est pas « le client » en général, mais son état au 31 décembre 2025.
2. **À quel moment prédit-on ?** Le modèle sera utilisé le 31 décembre pour décider qui appeler en janvier. La date de prédiction $t_0$ est donc le 31 décembre.
3. **Qu'est-ce qui est connu à $t_0$ ?** Tout ce qui s'est passé **jusqu'à** $t_0$ : l'historique de commandes, les tickets, la satisfaction déclarée. Rien de ce qui se passera après.
4. **Quand la cible est-elle connue ?** Le départ à 90 jours ne se saura que **le 31 mars** : il y a un **délai d'étiquetage**. Pour construire le jeu d'entraînement, on a dû se placer dans le passé, à une date $t_0$ assez ancienne pour que les 90 jours suivants soient écoulés.

```python hide
fig, ax = plt.subplots(figsize=(10, 3.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 3.2); ax.axis("off")
ax.annotate("", xy=(9.8, 0.75), xytext=(0.2, 0.75), arrowprops=dict(arrowstyle="->", color=ENCRE2, lw=1.6))
ax.plot([5, 5], [0.55, 2.15], color=ROUGE, lw=2.4)
ax.text(5, 2.5, "date de prédiction $t_0$ (31 décembre)", ha="center", color=ROUGE, fontsize=10)
ax.add_patch(plt.Rectangle((0.4, 1.0), 4.5, 0.95, color=BLEU, alpha=0.18))
ax.text(2.65, 1.48, "passé : variables d'entrée\n(historique, tickets, satisfaction…)", ha="center", va="center", color=BLEU, fontsize=10)
ax.add_patch(plt.Rectangle((5.1, 1.0), 3.3, 0.95, color=ORANGE, alpha=0.22))
ax.text(6.75, 1.48, "90 jours : on observe la cible\n(le client a-t-il recommandé ?)", ha="center", va="center", color=ORANGE, fontsize=10)
ax.plot([8.4, 8.4], [0.6, 1.95], color=ENCRE2, lw=1.2, ls="--")
ax.text(8.5, 0.2, "31 mars : la cible est connue", ha="center", color=ENCRE2, fontsize=9.5)
ax.text(9.6, 0.95, "temps", color=MUET, fontsize=9)
plt.savefig("figures/ch01-chronologie.png", dpi=200, bbox_inches="tight"); plt.close()
```

![Chronologie d'un problème de prédiction : les variables d'entrée appartiennent au passé de la date de prédiction, la cible est observée pendant les 90 jours suivants et n'est connue que le 31 mars.](figures/ch01-chronologie.png)

> ⚠️ **La question qui évite les catastrophes.** Pour chaque variable d'entrée, demandez-vous : *« à la date où j'utiliserai le modèle, cette valeur existe-t-elle déjà ? »* Si la réponse est « non » ou « pas sûr », la variable est interdite. Cette seule question aurait suffi à éviter la plupart des projets de ML qui échouent au moment du déploiement.

### 1.1.5 Séparer les données : entraînement, validation, test

Comme l'erreur d'entraînement est optimiste (section 1.1.2), on garde de côté des données que le modèle ne verra pas pendant sa construction. On distingue **trois rôles**, qui correspondent à trois questions différentes :

| Jeu | Rôle | Question | Qui l'utilise |
|---|---|---|---|
| **Entraînement** (*train*) | ajuster les paramètres du modèle | « quels coefficients, quels arbres ? » | l'algorithme |
| **Validation** | comparer des modèles, régler les hyperparamètres | « lequel choisir ? » | **vous**, de nombreuses fois |
| **Test** | estimer la performance finale du modèle choisi | « que vaudra-t-il en production ? » | **vous, une seule fois** |

L'analogie qui aide : l'entraînement, ce sont les **exercices** que l'on fait en révisant ; la validation, ce sont les **examens blancs**, que l'on peut passer plusieurs fois pour ajuster sa méthode ; le test est **l'examen final**. Si on regarde le sujet de l'examen final pour adapter sa révision, la note ne mesure plus rien. Dès que le jeu de test a influencé une décision (choisir un modèle, régler un seuil, supprimer une variable), il devient un jeu de validation, et il n'y a plus de jeu de test.

**Comment découper ?** Plusieurs façons, qui ne sont pas interchangeables :

- **Aléatoire**, quand les lignes sont indépendantes : on tire au hasard, par exemple 75 % pour l'entraînement et 25 % pour le test.
- **Stratifié**, quand la cible est rare : on garde la même proportion de clients partis (14 %) dans chaque jeu. Sans cela, un petit jeu de test pourrait n'en contenir que 10 % ou 18 % par hasard.
- **Temporel**, quand le futur doit être prédit à partir du passé : on entraîne sur les périodes anciennes, on teste sur les récentes. Un tirage aléatoire mélangerait passé et futur et serait trop favorable (section 1.2.3).
- **Groupé**, quand plusieurs lignes concernent la même entité (plusieurs commandes d'un même client, plusieurs photos d'un même objet) : toutes les lignes d'une entité vont du même côté, sinon le modèle « reconnaît » l'entité au lieu de généraliser.

Dans tout le chapitre, nous mettons de côté **25 % des clients** (3 000) pour le test final, en conservant la proportion de départs. Le jeu d'entraînement (9 000 clients) sert à toutes les expériences ; le jeu de test ne sera ouvert qu'**une fois**, à la section 1.4.

```python
from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
print(X_tr.shape, X_te.shape, y_tr.mean().round(4), y_te.mean().round(4))
```
<!--sortie-->
```text
(9000, 19) (3000, 19) 0.1404 0.1403
```

Le résultat est : 9 000 clients d'entraînement (14,04 % de départs) et 3 000 clients de test (14,03 %). L'argument `random_state=0` fixe la graine : le même découpage sera obtenu à chaque exécution, condition indispensable pour qu'une expérience soit **reproductible**.

> 💡 **Quelle taille pour le jeu de test ?** Plus il est petit, plus la note finale est incertaine. Pour une exactitude voisine de 0,9 mesurée sur $n$ clients, l'erreur-type est environ $\sqrt{0{,}9\times0{,}1/n}$ : 0,5 point pour $n=3\,000$ mais 1,7 point pour $n=300$ (un intervalle à 95 % est environ deux fois plus large de chaque côté). Sur un problème rare (14 % de positifs), c'est le nombre de **positifs** dans le test qui compte : ici environ 420. Nous mesurerons précisément cette incertitude à la section 1.4.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.3.

### 1.1.6 La fuite d'information

La **fuite d'information** (*data leakage*) désigne toute situation où le modèle, pendant sa construction, a accès à une information qu'il n'aura pas au moment de l'utilisation réelle. C'est la cause la plus fréquente de projets dont les résultats brillants s'effondrent en production. Elle se présente sous plusieurs formes :

- **La fuite par la cible** : une variable d'entrée contient, directement ou indirectement, la réponse (un « motif de résiliation » enregistré *après* le départ).
- **La contamination du jeu de test** : un traitement qui *apprend* des données (calcul d'une moyenne, choix de variables, normalisation) est appliqué **avant** le découpage, sur l'ensemble des données.
- **La fuite temporelle** : on prédit le passé avec le futur (section 1.2.3).
- **Les doublons et les entités partagées** : le même client apparaît des deux côtés du découpage.

**Un cas concret : la colonne `commandes_apres_cible`.** Notre tableau contient le nombre de commandes passées dans les **trois mois suivant** la date de prédiction. Elle semble anodine : c'est un nombre de commandes comme un autre. Ajoutons-la aux variables d'entrée et mesurons la performance par validation croisée (la méthode de la section 1.2).

```python hide
Xl = X_tr.copy(); Xl["commandes_apres_cible"] = df.loc[X_tr.index, "commandes_apres_cible"]
sans = cross_val_score(modele_hgb(), X_tr, y_tr, cv=5, scoring="roc_auc")
avec = cross_val_score(modele_hgb(), Xl, y_tr, cv=5, scoring="roc_auc")
print("AUC en validation croisée : sans", sans.mean().round(4), "| avec", avec.mean().round(4), "| écart", (avec.mean() - sans.mean()).round(4))
auc_uni = {c: roc_auc_score(y_tr, df.loc[X_tr.index, c].fillna(df[c].median())) for c in NUM + ["commandes_apres_cible"]}
auc_uni = pd.Series({k: max(v, 1 - v) for k, v in auc_uni.items()}).sort_values(ascending=False)
print("AUC univariée de la colonne piège :", auc_uni["commandes_apres_cible"].round(3), "| rang", list(auc_uni.index).index("commandes_apres_cible") + 1, "sur", len(auc_uni), "| meilleure variable honnête :", auc_uni.drop("commandes_apres_cible").index[0], auc_uni.drop("commandes_apres_cible").iloc[0].round(3))
from sklearn.inspection import permutation_importance
a, b, ya, yb = train_test_split(Xl, y_tr, test_size=0.3, stratify=y_tr, random_state=1)
m1 = modele_hgb().fit(a, ya)
pi = permutation_importance(m1, b, yb, scoring="roc_auc", n_repeats=3, random_state=0)
rang = pd.Series(pi.importances_mean, index=b.columns).sort_values(ascending=False)
print("importance par permutation (perte d'AUC) :", rang.head(4).round(3).to_dict(), "| rang de la colonne piège :", list(rang.index).index("commandes_apres_cible") + 1)
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw={"width_ratios": [0.8, 1.2]})
ax[0].bar(["sans la colonne\npiège", "avec la colonne\npiège"], [sans.mean(), avec.mean()], color=[BLEU, ROUGE], width=0.55)
for i, v in enumerate([sans.mean(), avec.mean()]): ax[0].text(i, v + 0.004, f"{v:.3f}".replace(".", ","), ha="center", color=ENCRE2)
ax[0].set_ylim(0.8, 0.95); ax[0].set_ylabel("AUC en validation croisée"); ax[0].set_title("Le « gain » est un mirage"); ax[0].grid(axis="x", visible=False)
top = rang.head(6)[::-1]
ax[1].barh([n.replace("_", " ") for n in top.index], top.values, color=[ROUGE if n == "commandes_apres_cible" else BLEU for n in top.index])
ax[1].set_xlabel("perte d'AUC quand on mélange la variable"); ax[1].set_title("Importance par permutation"); ax[1].grid(axis="y", visible=False)
plt.tight_layout(); plt.savefig("figures/ch01-fuite.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
AUC en validation croisée : sans 0.8895 | avec 0.9221 | écart 0.0325
AUC univariée de la colonne piège : 0.759 | rang 2 sur 16 | meilleure variable honnête : montant_12m 0.774
importance par permutation (perte d'AUC) : {'commandes_apres_cible': 0.156, 'age': 0.047, 'recence_jours': 0.034, 'satisfaction_moy': 0.024} | rang de la colonne piège : 1
```

![À gauche : l'AUC en validation croisée passe de 0,89 à 0,92 quand on ajoute la colonne des commandes futures. À droite : cette colonne devient la variable la plus « importante » du modèle.](figures/ch01-fuite.png)

L'AUC passe de 0,890 à 0,922 : un gain de trois points, qui ferait la joie de n'importe quelle équipe. Et la colonne piège devient la variable la plus importante du modèle (figure de droite). **C'est un mirage.** Le nombre de commandes des trois mois suivants est précisément ce que l'on cherche à prédire : un client qui ne commande plus a, par définition, zéro commande après. Au 31 décembre, cette colonne **n'existe pas encore**. Le modèle « avec » ne peut donc pas être utilisé : appliqué en production, il recevrait des valeurs manquantes ou inventées, et sa performance réelle s'effondrerait à celle du modèle « sans », voire pire (il s'est appuyé sur une information qui n'arrive jamais).

> ⚠️ **Un détecteur de fuite imparfait.** On entend souvent qu'une variable « trop belle » trahit la fuite. Ici, elle est discrète : prise seule, la colonne piège a une AUC de 0,76, au **deuxième rang** sur 16 variables, juste derrière le montant des commandes (0,77) ; rien d'aberrant, et un tri des variables par pouvoir prédictif individuel ne l'aurait pas signalée. Ce qui la trahit, c'est (1) **l'audit du calendrier** (« quand cette valeur est-elle connue ? ») et (2) le **bond** de performance quand on l'ajoute, combiné à son importance démesurée. La fuite par la cible est une faute de **raisonnement**, rarement visible dans les chiffres seuls.

**Un second cas : la contamination par le choix des variables.** Voici une expérience classique. On génère 100 clients fictifs avec 2 000 variables de **pur bruit** et une cible tirée à pile ou face : aucune information à trouver. On retient les 10 variables les mieux corrélées à la cible, puis on estime la performance par validation croisée.

```python hide
from sklearn.feature_selection import SelectKBest, f_classif
rng = np.random.default_rng(0); Xn = rng.normal(size=(100, 2000)); yn = rng.integers(0, 2, 100)
cvn = StratifiedKFold(5, shuffle=True, random_state=0)
faux = cross_val_score(LogisticRegression(max_iter=1000), SelectKBest(f_classif, k=10).fit_transform(Xn, yn), yn, cv=cvn, scoring="roc_auc").mean()
juste = cross_val_score(make_pipeline(SelectKBest(f_classif, k=10), LogisticRegression(max_iter=1000)), Xn, yn, cv=cvn, scoring="roc_auc").mean()
print("sélection AVANT la validation croisée :", round(faux, 3), "| sélection DANS le pipeline :", round(juste, 3))
```
<!--sortie-->
```text
sélection AVANT la validation croisée : 0.879 | sélection DANS le pipeline : 0.602
```

En sélectionnant les variables **sur toutes les données avant** de valider, on obtient une AUC de **0,88** sur un jeu qui ne contient que du bruit. En refaisant la sélection **à l'intérieur de chaque pli** (dans un *pipeline*), on tombe à 0,60, ce qui est, sur 100 observations, la dispersion normale autour du hasard (0,5). La différence entre 0,88 et 0,60 est la mesure de la contamination : les données de validation avaient « voté » pour le choix des variables.

> ✅ **À retenir.**
> - Un modèle se juge sur des données **qu'il n'a pas vues**, parce que l'erreur d'entraînement est en moyenne **optimiste** (démonstration 1.1.2).
> - Une ligne = une unité d'analyse à une **date de prédiction** ; chaque variable doit être **connue à cette date**. L'audit du calendrier est la meilleure défense contre la fuite.
> - Trois rôles : **entraînement** (ajuster), **validation** (choisir, souvent), **test** (évaluer, **une seule fois**).
> - Tout traitement qui *apprend* des données (imputation, normalisation, sélection, encodage cible) fait partie du modèle : il doit être **entraîné sur le jeu d'entraînement seulement**, dans un pipeline.
> - La perte guide l'algorithme, la **métrique** guide la décision ; l'exactitude seule trompe sur les classes déséquilibrées.
