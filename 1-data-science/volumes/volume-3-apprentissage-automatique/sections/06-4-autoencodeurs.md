## 6.4 Autoencodeurs, et comparaison des méthodes

La forêt d'isolement mesure la facilité à *isoler* un point. Un **autoencodeur** suit une logique opposée : il apprend à *reproduire* ses entrées après les avoir comprimées, et l'on juge anormal ce qu'il ne parvient pas à reproduire. Cette section présente l'idée, son lien exact avec l'ACP, un exemple avec `scikit-learn`, et ses pièges. Elle se termine par la **comparaison honnête** de toutes les méthodes du chapitre.

```python hide
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from scipy.stats import rankdata

print("jeu de validation (défini au début du chapitre) :", len(valid), "commandes dont", int(y_val.sum()), "fraudes")
```
<!--sortie-->
```text
jeu de validation (défini au début du chapitre) : 32000 commandes dont 246 fraudes
```

### 6.4.1 L'idée : comprimer, puis reconstruire

Un **autoencodeur** est un réseau de neurones formé de deux parties :

- un **encodeur** $f$ qui transforme une commande $x\in\mathbb R^p$ en un petit résumé $z=f(x)\in\mathbb R^q$ avec $q<p$ (le **goulot d'étranglement**) ;
- un **décodeur** $g$ qui reconstruit $\hat x=g(z)$, de même taille que $x$.

On l'entraîne à minimiser l'**erreur de reconstruction** $\sum_i\lVert x_i-g(f(x_i))\rVert^2$ sur des données, **sans aucune étiquette**. Comme le goulot est étroit, le réseau ne peut pas recopier ses entrées : il doit retenir ce qui est **typique** (les régularités de la plupart des commandes). Une commande normale se reconstruit bien, avec une petite erreur. Une commande qui ne suit pas ces régularités se reconstruit mal : son **erreur de reconstruction** est grande, et c'est notre **score d'anomalie**.

> 💡 **L'image du portraitiste.** Un dessinateur à qui on montre un visage pendant trois secondes retient les traits habituels (deux yeux, un nez, une bouche) et dessine un visage moyen ressemblant. Si le visage comporte trois yeux, le dessin ne le reproduira pas : l'écart entre le visage et le dessin dénonce l'anomalie. Cela ne marche que si la mémoire du dessinateur est **limitée** : avec une mémoire parfaite, il recopierait aussi le troisième œil.

### 6.4.2 L'ACP est un autoencodeur linéaire

Si l'encodeur et le décodeur sont **linéaires**, trouver les meilleures matrices revient à chercher l'approximation de rang $q$ du tableau de données la plus proche au sens des moindres carrés. Le **théorème d'Eckart-Young** (volume I, section 1.1.4 sur la décomposition en valeurs singulières) dit que cette meilleure approximation est la projection sur les $q$ premières directions principales : c'est exactement l'**ACP** (volume II, section 3.1, et en particulier 3.1.7 sur la compression et la reconstruction). Un autoencodeur linéaire n'est donc rien d'autre qu'une ACP ; les autoencodeurs non linéaires la généralisent à des surfaces courbes.

**Un exemple à la main.** Reprenons les deux variables standardisées de corrélation $\rho=0{,}9$ de la section 6.2.2. Les directions principales sont $(1,1)/\sqrt2$ (variance $\lambda_1=1{,}9$) et $(1,-1)/\sqrt2$ (variance $\lambda_2=0{,}1$). Avec une seule composante ($q=1$), on reconstruit chaque point par sa projection sur $(1,1)/\sqrt2$.

- Le point $x=(2,2)$ est **sur** cette direction : sa reconstruction est exacte, **erreur 0**.
- Le point $x=(2,-2)$ est **perpendiculaire** à elle : la projection est nulle, la reconstruction est l'origine, et l'erreur au carré vaut $\lVert x\rVert^2=8$. Sa coordonnée sur la seconde direction est $y_2=(2+2)/\sqrt2=2{,}83$, d'où $y_2^2=8$.

C'est le même verdict que celui de Mahalanobis (section 6.2.2, où les deux points avaient pour distances 4,21 et 80), et le lien est exact : $d_M^2=\sum_j y_j^2/\lambda_j$, soit pour le second point $8/0{,}1=80$. L'erreur de reconstruction de l'ACP, elle, ne garde que les composantes **écartées**, **sans les diviser par leur variance** ($8$ au lieu de $80$). La distance de Mahalanobis les pondère par l'inverse de leur variance : elle est plus sensible aux petites directions.

Appliquons cela à nos transactions, en reconstruisant avec $k=1$ à $9$ composantes. Le nombre de composantes joue le rôle de la taille du goulot ; nous le **choisissons sur le jeu de validation**, et nous regardons ensuite ce que donne le jeu de test :

```python hide
def ap_acp(k):
    pca = PCA(n_components=k).fit(Z_app)
    err = lambda Z: ((Z - pca.inverse_transform(pca.transform(Z))) ** 2).sum(axis=1)
    return average_precision_score(y_val, err(Z_val)), average_precision_score(y_test, err(Z_test)), err
resultats_acp = {k: ap_acp(k) for k in range(1, 10)}
k_acp = max(resultats_acp, key=lambda k: resultats_acp[k][0])
evaluer("ACP (erreur de reconstruction)", resultats_acp[k_acp][2](Z_test))
print("AP selon le nombre de composantes (validation | test) :", {k: (round(v[0], 3), round(v[1], 3)) for k, v in resultats_acp.items()})
print("nombre de composantes choisi sur la validation :", k_acp, "| part de variance de cette composante :", round(float(PCA(n_components=k_acp).fit(Z_app).explained_variance_ratio_.sum()), 3))
```
<!--sortie-->
```text
AP selon le nombre de composantes (validation | test) : {1: (0.364, 0.391), 2: (0.139, 0.141), 3: (0.052, 0.045), 4: (0.05, 0.046), 5: (0.052, 0.046), 6: (0.036, 0.046), 7: (0.043, 0.056), 8: (0.038, 0.048), 9: (0.016, 0.017)}
nombre de composantes choisi sur la validation : 1 | part de variance de cette composante : 0.128
```

Le résultat est contre-intuitif : **la meilleure ACP est celle qui garde une seule composante**, et la qualité s'effondre ensuite (sur le jeu de test, la précision moyenne passe de 0,39 pour une composante à 0,14 pour deux, puis à 0,02-0,06 pour trois ou plus, contre un plancher de 0,008). La validation choisit la même valeur, une composante, qui n'explique pourtant que **12,8 %** de la variance : nos dix variables sont peu corrélées entre elles, donc il y a peu de structure linéaire à compresser, et l'erreur de reconstruction avec une composante est presque la somme des carrés des dix variables standardisées, c'est-à-dire une distance au centre (proche du z-score classique de la section 6.2.1). Avec peu de composantes, l'erreur de reconstruction agrège beaucoup de directions : elle est grande dès que la commande s'écarte du schéma principal. Avec davantage de composantes, le modèle devient capable de reconstruire aussi les **directions dans lesquelles se trouvent les fraudes** : l'anomalie se « cache » dans le sous-espace appris. C'est le **piège central de la reconstruction** : *un modèle trop riche reconstruit aussi les anomalies*, et sa capacité doit donc être **contrainte**.

### 6.4.3 Un autoencodeur non linéaire avec `scikit-learn`

`scikit-learn` n'a pas de bibliothèque d'autoencodeurs, mais un réseau de neurones de régression (`MLPRegressor`) entraîné à prédire **ses propres entrées** en est un : couches cachées de tailles décroissantes puis croissantes, avec un goulot au milieu. Le réseau ci-dessous a trois couches cachées de 6, 3 et 6 neurones (un goulot de 3 pour 10 variables) :

```python
from sklearn.neural_network import MLPRegressor

ae = MLPRegressor(hidden_layer_sizes=(6, 3, 6), activation="tanh", max_iter=100, random_state=0)
ae.fit(Z_app[reference], Z_app[reference])                         # apprendre à reconstruire ses propres entrées
erreur = ((ae.predict(Z_test) - Z_test) ** 2).sum(axis=1)          # erreur de reconstruction = score d'anomalie
```

Trois choix de méthode méritent attention :

- **Les données d'apprentissage sont contaminées.** Le réseau est entraîné sur des commandes qui contiennent environ 0,8 % de fraudes. Tant qu'elles sont rares, il les traite comme du bruit et ne les apprend pas ; si elles étaient nombreuses, il apprendrait à les reconstruire.
- **Les variables doivent être standardisées**, sinon les variables d'échelle la plus grande dominent l'erreur de reconstruction.
- **L'architecture est un réglage qu'on ne peut pas tester sur le jeu de test.** La tentation est grande d'essayer plusieurs tailles, de regarder laquelle donne la meilleure précision moyenne sur le jeu de test, et de la présenter comme résultat. C'est exactement la faute de méthode que condamne le chapitre 1 (section 1.4) : le jeu de test aurait servi à choisir, donc il ne mesurerait plus rien. Nous utilisons donc le **jeu de validation** défini plus haut.

Nous comparons cinq architectures, chacune entraînée avec **quatre graines aléatoires** (le résultat d'un réseau dépend de son initialisation), sur l'échantillon de référence. Pour chaque graine, l'erreur de reconstruction est mise à l'échelle avec la moyenne et l'écart-type de l'erreur **sur la validation** (aucune information de test), puis on moyenne les quatre scores : c'est un petit **comité** de réseaux.

```python hide
architectures = {"(2,)": (2,), "(5,)": (5,), "(6, 3, 6)": (6, 3, 6), "(16, 8, 16)": (16, 8, 16), "(64, 32, 64)": (64, 32, 64)}
res_ae = {}
for nom, h in architectures.items():
    val_s, test_s, ap_val, ap_test = [], [], [], []
    for graine in range(4):
        reseau = MLPRegressor(hidden_layer_sizes=h, activation="tanh", max_iter=100, random_state=graine).fit(Z_app[reference], Z_app[reference])
        e_val = ((reseau.predict(Z_val) - Z_val) ** 2).sum(axis=1)
        e_test = ((reseau.predict(Z_test) - Z_test) ** 2).sum(axis=1)
        mu_e, sd_e = e_val.mean(), e_val.std()
        val_s.append((e_val - mu_e) / sd_e); test_s.append((e_test - mu_e) / sd_e)
        ap_val.append(average_precision_score(y_val, e_val)); ap_test.append(average_precision_score(y_test, e_test))
    res_ae[nom] = dict(ap_val=ap_val, ap_test=ap_test, comite_val=average_precision_score(y_val, np.mean(val_s, axis=0)),
                       comite_test=average_precision_score(y_test, np.mean(test_s, axis=0)), score_test=np.mean(test_s, axis=0))
choix = max(res_ae, key=lambda n: res_ae[n]["comite_val"])
evaluer("Autoencodeur (comité de 4)", res_ae[choix]["score_test"])
for nom, r in res_ae.items():
    print(f"{nom:14s} AP par graine (test) {np.round(r['ap_test'], 3)} | comité : validation {r['comite_val']:.3f}, test {r['comite_test']:.3f}")
print("architecture choisie sur la validation :", choix)
fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.9))
ks = list(resultats_acp)
ax[0].plot(ks, [resultats_acp[k][0] for k in ks], "o--", color=ORANGE, lw=1.5, label="jeu de validation")
ax[0].plot(ks, [resultats_acp[k][1] for k in ks], "o-", color=BLEU, lw=2, label="jeu de test")
ax[0].axhline(y_test.mean(), color=MUET, ls=":", lw=1); ax[0].set_ylim(-0.03, 0.42); ax[0].text(3.0, -0.022, "plancher d'un score aléatoire (prévalence = 0,8 %)", color=MUET, fontsize=8)
ax[0].set_xlabel("nombre de composantes conservées"); ax[0].set_ylabel("précision moyenne (AP)"); ax[0].set_title("ACP : plus de composantes, moins de détection", fontsize=10); ax[0].legend(frameon=False, fontsize=8)
for i, (nom, r) in enumerate(res_ae.items()):
    ax[1].scatter([i] * 4, r["ap_test"], s=16, color=MUET, zorder=2, label="une graine (test)" if i == 0 else None)
    ax[1].scatter([i], [r["comite_test"]], marker="D", s=50, color=BLEU, zorder=3, label="comité de 4 (test)" if i == 0 else None)
    ax[1].scatter([i], [r["comite_val"]], marker="D", s=50, facecolors="none", edgecolors=ORANGE, lw=1.6, zorder=3, label="comité de 4 (validation)" if i == 0 else None)
ax[1].set_xticks(range(5)); ax[1].set_xticklabels(list(res_ae)); ax[1].set_xlabel("couches cachées du réseau"); ax[1].set_ylabel("précision moyenne (AP)")
ax[1].set_title("Autoencodeur : une architecture instable", fontsize=10); ax[1].legend(frameon=False, fontsize=8, loc="upper right")
plt.tight_layout(); plt.savefig("figures/ch06-autoencodeur.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
(2,)           AP par graine (test) [0.317 0.32  0.235 0.351] | comité : validation 0.285, test 0.323
(5,)           AP par graine (test) [0.068 0.176 0.109 0.14 ] | comité : validation 0.144, test 0.136
(6, 3, 6)      AP par graine (test) [0.368 0.238 0.491 0.479] | comité : validation 0.478, test 0.526
(16, 8, 16)    AP par graine (test) [0.135 0.127 0.087 0.126] | comité : validation 0.169, test 0.152
(64, 32, 64)   AP par graine (test) [0.323 0.39  0.326 0.357] | comité : validation 0.324, test 0.369
architecture choisie sur la validation : (6, 3, 6)
```

![À gauche : précision moyenne de l'ACP selon le nombre de composantes conservées, sur le jeu de validation (orange, pointillé) et le jeu de test (bleu). À droite : précision moyenne de cinq architectures d'autoencodeur : les petits points gris sont les quatre graines individuelles (jeu de test), le losange bleu le comité de quatre réseaux (test), le losange orange vide le même comité sur le jeu de validation.](figures/ch06-autoencodeur.png)

Ce que montre la figure de droite est instructif et **ne se résume pas en une règle simple** :

- **Les graines comptent.** Pour l'architecture (6, 3, 6), la précision moyenne des quatre réseaux va de **0,24 à 0,49** : le même modèle, entraîné quatre fois, donne des détecteurs de qualité très différente. Un autoencodeur isolé est une loterie.
- **Le comité stabilise.** Moyenner les quatre scores donne mieux que **chacun** des quatre réseaux isolés : **0,53 sur le jeu de test** pour (6, 3, 6).
- **La capacité n'est pas monotone.** L'architecture (6, 3, 6) (comité à 0,53) fait mieux que (5,) et (16, 8, 16) (comités à 0,14 et 0,15), mais plus grand n'est pas mieux (le réseau (64, 32, 64) donne 0,37), et plus petit non plus ((2,) donne 0,32). Nous n'avons **pas d'explication simple** de ce non-monotonisme. Une hypothèse naturelle, un entraînement trop court (100 itérations), est **infirmée** : en autorisant 400 itérations aux deux architectures les moins bonnes, la précision moyenne ne change pas (cahier, application 6.5). Les réseaux convergent vers des solutions différentes selon leur initialisation et leur taille, et un réseau n'est pas bon ou mauvais *par principe*.
- **Le jeu de validation désigne la bonne architecture.** Celle qu'il choisit, (6, 3, 6), est celle qui est la meilleure sur le test : on peut donc rapporter son résultat comme une estimation honnête (aucune information du test n'a servi à choisir).

Ce dernier point demande tout de même une réserve : **un jeu de validation étiqueté** (ici 246 fraudes) est nécessaire pour choisir. Un détecteur non supervisé n'a pas besoin d'étiquettes pour *fonctionner*, mais il en a besoin pour *être réglé*. Quelques centaines d'exemples confirmés suffisent, et la gérante en dispose après quelques semaines.

> ⚠️ **Les pièges de l'autoencodeur.**
> - *Un goulot trop large* : le réseau recopie tout, y compris les anomalies (erreur faible partout).
> - *Des données d'apprentissage trop contaminées* : le réseau apprend à reconstruire les fraudes.
> - *Une instabilité d'une graine à l'autre* : toujours **moyenner plusieurs réseaux**.
> - *Un score qui additionne des erreurs de variables d'échelles ou de natures différentes* (continues, binaires) : les variables binaires rares pèsent lourd quand elles prennent leur valeur rare. Standardiser ne règle pas tout.

### 6.4.4 La version PyTorch

Dans la pratique, on écrit plutôt les autoencodeurs avec une bibliothèque d'apprentissage profond, qui permet des architectures plus riches (convolutions pour les images, couches récurrentes pour les séquences), un entraînement par lots sur carte graphique, et un contrôle fin de l'optimisation (arrêt précoce, régularisation). Voici l'équivalent PyTorch du réseau précédent. **Ce code n'est pas exécuté dans ce livre** : PyTorch n'est pas installé dans l'environnement qui a produit les sorties.

```python noexec
import torch
from torch import nn

autoencodeur = nn.Sequential(
    nn.Linear(10, 6), nn.Tanh(), nn.Linear(6, 3), nn.Tanh(),     # encodeur : 10 -> 3
    nn.Linear(3, 6), nn.Tanh(), nn.Linear(6, 10))                 # décodeur : 3 -> 10
optimiseur = torch.optim.Adam(autoencodeur.parameters(), lr=1e-3)
X_app_t = torch.tensor(Z_app[reference], dtype=torch.float32)
for epoque in range(100):
    optimiseur.zero_grad()
    perte = ((autoencodeur(X_app_t) - X_app_t) ** 2).sum(dim=1).mean()   # erreur de reconstruction
    perte.backward(); optimiseur.step()
```

> *Non exécuté.* Les résultats chiffrés de cette section proviennent exclusivement de `MLPRegressor` ; le code PyTorch ci-dessus est donné à titre d'illustration.

### 6.4.5 Comparer honnêtement les méthodes

Nous avons maintenant toutes les méthodes. Pour ne pas se tromper soi-même, rappelons le protocole : toutes les méthodes non supervisées ont été ajustées **sans étiquette** sur le jeu d'apprentissage ; leurs réglages ont été **choisis sur le jeu de validation** (nombre de voisins, nombre de voisins du LOF, nombre de composantes de l'ACP, architecture de l'autoencodeur) ou **fixés à l'avance** sans réglage possible (z-scores, Mahalanobis, 200 arbres pour la forêt d'isolement) ; le jeu de test n'a servi qu'à les juger. La dernière ligne est une **combinaison** fixée à l'avance, sans aucun réglage : on classe les commandes par chacun des trois détecteurs de familles différentes (voisins, forêt d'isolement, autoencodeur) et on prend la **moyenne des rangs**.

```python hide
rang = lambda s: rankdata(s) / len(s)
evaluer("Moyenne des rangs (3 familles)", rang(S[nom_knn]) + rang(S["Forêt d'isolement"]) + rang(S["Autoencodeur (comité de 4)"]))
liste = ["Gradient boosting (supervisé)", "z-score classique", "Mahalanobis", "Mahalanobis robuste (MCD)", nom_knn, nom_lof,
         "Forêt d'isolement", "ACP (erreur de reconstruction)", "Autoencodeur (comité de 4)", "Moyenne des rangs (3 familles)"]
```

```python hide-code
print(tableau(liste).to_string())
```
<!--sortie-->
```text
                                  AUC     AP  précision à k  rappel type 1  rappel type 2
Gradient boosting (supervisé)   0.971  0.646          0.616          0.716          0.631
z-score classique               0.939  0.433          0.452          0.457          0.477
Mahalanobis                     0.946  0.382          0.356          0.198          0.615
Mahalanobis robuste (MCD)       0.949  0.410          0.404          0.235          0.677
Plus proches voisins (k = 30)   0.959  0.460          0.432          0.259          0.692
LOF (k = 300)                   0.944  0.492          0.493          0.519          0.492
Forêt d'isolement               0.937  0.332          0.342          0.123          0.677
ACP (erreur de reconstruction)  0.946  0.391          0.363          0.198          0.615
Autoencodeur (comité de 4)      0.962  0.526          0.514          0.519          0.677
Moyenne des rangs (3 familles)  0.958  0.438          0.404          0.259          0.662
```

```python hide
ordre_ap = sorted(liste, key=lambda n: R[n]["AP"])
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw={"width_ratios": [1.15, 1]}, sharey=True)
couleurs = [BLEU if n.startswith("Gradient") else (AQUA if n.startswith("Moyenne") else ORANGE) for n in ordre_ap]
ax[0].barh(range(len(ordre_ap)), [R[n]["AP"] for n in ordre_ap], color=couleurs)
ax[0].axvline(y_test.mean(), color=MUET, ls=":", lw=1); ax[0].set_yticks(range(len(ordre_ap))); ax[0].set_yticklabels(ordre_ap, fontsize=8.5)
ax[0].set_xlabel("précision moyenne (AP)"); ax[0].set_title("Qualité globale (bleu : supervisé ; vert : combinaison)", fontsize=10)
ax[1].scatter([R[n]["rappel1"] for n in ordre_ap], range(len(ordre_ap)), color=ORANGE, s=42, label="type 1 (compte neuf)")
ax[1].scatter([R[n]["rappel2"] for n in ordre_ap], range(len(ordre_ap)), color=VIOLET, s=42, marker="s", label="type 2 (prise de contrôle)")
ax[1].set_xlim(0, 1); ax[1].set_xlabel("part des fraudes de ce type parmi les 180 alertes"); ax[1].set_title("Qui trouve quoi ?", fontsize=10); ax[1].legend(frameon=False, fontsize=8, loc="lower right")
for a in ax: a.grid(axis="y", visible=False)
plt.tight_layout(); plt.savefig("figures/ch06-comparaison.png", dpi=200, bbox_inches="tight"); plt.close()
meilleur_non_sup = max([n for n in liste if not n.startswith("Gradient") and not n.startswith("Moyenne")], key=lambda n: R[n]["AP"])
print("meilleure méthode non supervisée (AP) :", meilleur_non_sup, round(R[meilleur_non_sup]["AP"], 3))
print("supervisé :", round(R["Gradient boosting (supervisé)"]["AP"], 3), "| combinaison :", round(R["Moyenne des rangs (3 familles)"]["AP"], 3))
```
<!--sortie-->
```text
meilleure méthode non supervisée (AP) : Autoencodeur (comité de 4) 0.526
supervisé : 0.646 | combinaison : 0.438
```

![À gauche : précision moyenne de chaque méthode (la ligne pointillée est le plancher d'un score aléatoire). À droite : pour chaque méthode, la part des fraudes de type 1 (cercles orange) et de type 2 (carrés violets) retrouvées parmi les 180 alertes du budget.](figures/ch06-comparaison.png)

Que lire dans ce tableau ?

1. **Le supervisé gagne quand on a des étiquettes** : précision moyenne de 0,65, contre 0,53 pour le meilleur détecteur non supervisé (le comité d'autoencodeurs) et 0,49 pour le LOF réglé. L'écart est le prix de ne pas connaître la fraude : il est modeste, et le détecteur supervisé aura du mal avec une fraude inédite.
2. **Les méthodes non supervisées surpassent largement le hasard** (plancher à 0,008) : une précision moyenne de 0,33 à 0,53, c'est de 41 à 65 fois mieux.
3. **Elles ne trouvent pas les mêmes fraudes.** Mahalanobis, les voisins, la forêt d'isolement et l'ACP retrouvent surtout le type 2 (de 0,62 à 0,69, contre 0,12 à 0,26 pour le type 1) ; le z-score classique les équilibre (0,46 et 0,48) ; les **deux meilleurs détecteurs non supervisés, le comité d'autoencodeurs (0,52 et 0,68) et le LOF réglé (0,52 et 0,49), retrouvent bien les deux types**.
4. **Les meilleurs détecteurs sont aussi les plus délicats à régler.** Le LOF vaut 0,11 avec 10 voisins et 0,49 avec 300 ; l'architecture (5,) donne 0,14 et (6, 3, 6) 0,53. Les méthodes simples (le z-score classique à 0,43, les voisins à 0,46) sont beaucoup moins sensibles à leurs réglages. La sophistication peut être payante, mais **à condition de disposer d'un jeu de validation pour régler**, et il vaut mieux **essayer d'abord les méthodes simples**.
5. **Une combinaison n'est pas magique.** La moyenne des rangs de trois familles (voisins, forêt d'isolement, autoencodeur) obtient une précision moyenne de 0,44 : **moins** que son meilleur membre (le comité d'autoencodeurs, 0,53). Les deux autres membres, qui retrouvent mal le type 1, tirent le classement moyen vers le bas. Une combinaison aide quand ses membres sont de qualité comparable et vraiment complémentaires ; elle ne remplace pas la mesure.

> ⚠️ **Les limites de cette comparaison.** (i) Les données sont **simulées** : les fraudes y ont été fabriquées d'une certaine façon, et les classements pourraient changer sur des fraudes réelles. (ii) Un seul jeu de test, de 146 fraudes : les différences de quelques centièmes ne sont pas significatives (une autre graine pour la séparation changerait certains rangs). (iii) Les détecteurs ne sont comparés qu'au **même budget d'alertes** et à une répartition de coût simple. (iv) Aucun n'est évalué sur une dérive dans le temps, qui est le vrai défi de la fraude réelle.

En pratique, on retient de ce chapitre une démarche plus qu'une méthode :

- **commencer simple** (distance aux voisins ou Mahalanobis, un modèle supervisé de référence si l'on a des étiquettes) ;
- **évaluer sous déséquilibre** avec l'AP, le rappel au budget et le coût, jamais avec l'exactitude ;
- **ne pas régler sur le jeu de test** : garder un jeu de validation étiqueté, même petit ;
- **tester des combinaisons** de familles de détecteurs, sans présumer qu'elles aident (voir ci-dessus), et utiliser leurs scores comme variables d'entrée d'un modèle supervisé quand des étiquettes existent ;
- **surveiller dans le temps** : la fraude évolue, la qualité du détecteur aussi (un contrôle régulier sur les alertes confirmées en témoigne) ;
- se rappeler qu'un détecteur ne produit que des **pistes** : le dernier mot revient à une vérification humaine, dont le temps est le véritable budget.

> ✅ **À retenir.**
> - Un **autoencodeur** apprend à reconstruire les données normales à travers un goulot étroit ; l'**erreur de reconstruction** est le score d'anomalie. Linéaire, il est **équivalent à l'ACP**.
> - Un modèle trop riche reconstruit aussi les anomalies : la **capacité doit être contrainte** (peu de composantes, goulot étroit), et le bon réglage se **choisit sur un jeu de validation**, jamais sur le test.
> - Un réseau isolé est instable d'une graine à l'autre : on **moyenne un comité**.
> - Chaque méthode trouve d'autres fraudes ; le supervisé est le meilleur quand les étiquettes existent ; une **combinaison** naïve ne bat pas forcément son meilleur membre.
> - Les comparaisons sur un jeu simulé et un seul jeu de test sont des **indications**, pas des lois.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.5 et 6.6, exercices 6.10 à 6.12.
