## 1.5 ➕ Pour aller plus loin : le réglage des hyperparamètres

> 🧭 **Section optionnelle.** Elle approfondit un geste que les chapitres suivants pratiquent sans cesse : choisir les réglages d'un modèle. On peut la sauter à la première lecture ; le piège de la section 1.5.5 mérite cependant d'être lu.

Un modèle d'apprentissage automatique a deux sortes de « boutons ». Les premiers sont **appris** à partir des données ; les seconds sont **fixés par vous avant l'apprentissage**. Bien régler les seconds change souvent beaucoup la performance, mais cela se fait avec une méthode, et un piège.

### 1.5.1 Paramètres et hyperparamètres

- Les **paramètres** sont les nombres que l'algorithme **apprend** : les coefficients d'une régression logistique, les questions posées dans les nœuds d'un arbre.
- Les **hyperparamètres** sont les réglages que **vous choisissez** avant l'entraînement et qui gouvernent la souplesse du modèle : la force de la régularisation, la profondeur maximale d'un arbre, la vitesse d'apprentissage d'un boosting. Ils contrôlent le compromis biais-variance de la section 1.3.

| Modèle | Exemples d'hyperparamètres | Effet |
|---|---|---|
| Régression logistique | force de régularisation $C$ | $C$ petit : modèle rigide (biais), $C$ grand : souple (variance) |
| Arbre de décision | profondeur maximale, taille minimale des feuilles | profond : souple |
| Gradient boosting | nombre d'itérations, vitesse d'apprentissage, nombre de feuilles par arbre, régularisation $\ell_2$ | plus d'itérations ou de feuilles : plus souple |

Régler, c'est chercher la combinaison qui **maximise le score de validation** : une fonction coûteuse (chaque évaluation est une validation croisée), sans formule, qu'on ne sait évaluer qu'en l'essayant. C'est de l'**optimisation par boîte noire**.

### 1.5.2 La grille et la recherche aléatoire

La première idée est la **recherche sur grille** (*grid search*) : on liste quelques valeurs pour chaque hyperparamètre et on essaie **toutes les combinaisons**. Trois valeurs pour quatre hyperparamètres, c'est déjà $3^4=81$ combinaisons, multipliées par le nombre de plis : le coût croît **exponentiellement** avec le nombre d'hyperparamètres.

La **recherche aléatoire** (*random search*) tire les combinaisons au hasard dans des intervalles, pour un budget fixé. Bergstra et Bengio (2012) ont montré pourquoi elle est souvent plus efficace : **en pratique, peu d'hyperparamètres comptent vraiment** pour un problème donné, et on ne sait pas lesquels à l'avance. Avec une grille de $3\times3=9$ essais, chaque hyperparamètre n'est testé qu'à **trois valeurs** distinctes ; avec 9 tirages aléatoires, il est testé à **neuf valeurs** distinctes. Si seul l'un des deux compte, la recherche aléatoire a exploré trois fois plus de valeurs de celui-ci.

**Un calcul à la main.** Supposons que 5 % de l'espace des réglages soient « excellents ». Chaque tirage aléatoire tombe dans cette zone avec probabilité $0{,}05$, donc $n$ tirages indépendants **manquent** la zone avec probabilité $0{,}95^n$. La probabilité d'en toucher au moins un est $1-0{,}95^n$ : $0{,}37$ pour $n=9$, et il faut $n=59$ tirages pour atteindre 95 % (car $0{,}95^{59}\approx0{,}05$). **Le budget nécessaire ne dépend pas du nombre d'hyperparamètres** : c'est l'avantage décisif sur la grille.

```python hide
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
from scipy.stats import loguniform, randint
X5 = X_tr.sample(5000, random_state=0); y5 = y_tr.loc[X5.index]
```

Essayons sur la prédiction de départ, avec un gradient boosting, sur un sous-échantillon de 5 000 clients (pour rester rapide) et une validation croisée à 3 plis. La grille : trois vitesses d'apprentissage × trois tailles d'arbre = 9 essais.

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

cv = StratifiedKFold(3, shuffle=True, random_state=0)
grille = {"learning_rate": [0.03, 0.1, 0.3], "max_leaf_nodes": [8, 31, 63]}
gs = GridSearchCV(modele_hgb(), grille, cv=cv, scoring="roc_auc").fit(X5, y5)
print(gs.best_params_, round(gs.best_score_, 4))
```
<!--sortie-->
```text
{'learning_rate': 0.03, 'max_leaf_nodes': 8} 0.8975
```

```python hide
scores_grille = np.sort(gs.cv_results_["mean_test_score"])
dist = {"learning_rate": loguniform(0.01, 0.5), "max_leaf_nodes": randint(4, 128), "l2_regularization": loguniform(1e-3, 10), "min_samples_leaf": randint(5, 100)}
meilleurs = []
for s in range(5):
    meilleurs.append(RandomizedSearchCV(modele_hgb(), dist, n_iter=9, cv=cv, scoring="roc_auc", random_state=s).fit(X5, y5).best_score_)
print("grille : meilleur", gs.best_params_, round(gs.best_score_, 4), "| les 9 scores", scores_grille.round(4))
print("recherche aléatoire (9 essais, 5 graines) : meilleurs scores", np.round(meilleurs, 4), "| moyenne", np.mean(meilleurs).round(4))
print("probabilité de toucher une zone de 5 % : n=9 :", round(1 - 0.95 ** 9, 3), "| n pour 95 % :", int(np.ceil(np.log(0.05) / np.log(0.95))))
```
<!--sortie-->
```text
grille : meilleur {'learning_rate': 0.03, 'max_leaf_nodes': 8} 0.8975 | les 9 scores [0.8744 0.8759 0.885  0.8854 0.8862 0.8868 0.8913 0.8966 0.8975]
recherche aléatoire (9 essais, 5 graines) : meilleurs scores [0.8941 0.8966 0.8918 0.8951 0.8974] | moyenne 0.895
probabilité de toucher une zone de 5 % : n=9 : 0.37 | n pour 95 % : 59
```

Sur ces données, la grille trouve un réglage à **0,8975** d'AUC (vitesse 0,03, arbres de 8 feuilles) ; les 9 combinaisons s'échelonnent de 0,874 à 0,8975, ce qui montre que **le réglage compte** (jusqu'à 2,3 points). Cinq recherches aléatoires de 9 essais, avec des graines différentes, trouvent entre 0,892 et 0,897 (moyenne 0,895), **sans faire mieux** que la grille. Ce n'est pas un échec de la méthode : avec 9 essais et un espace réduit, la grille s'est trouvée bien placée. L'avantage de l'aléatoire apparaît quand l'espace compte **beaucoup** d'hyperparamètres ou quand on ne sait pas où chercher.

> 💡 **Où se trouve le bon réglage ?** Ici, le meilleur modèle est **simple** (8 feuilles par arbre, apprentissage lent). Rien d'étonnant : le signal se résume à quelques seuils (section 1.3), et un modèle trop souple ajusterait le bruit. Cette observation rejoint la leçon du compromis biais-variance : le bon réglage est celui que la **validation** désigne, pas le plus puissant en apparence.

### 1.5.3 L'optimisation bayésienne : apprendre des essais précédents

La grille et le hasard **n'apprennent rien** de leurs essais : le vingtième tirage ignore que les dix-neuf premiers étaient mauvais dans telle région. L'**optimisation bayésienne** utilise l'historique pour décider où essayer ensuite : on construit un **modèle de substitution** du score de validation en fonction des hyperparamètres (un processus gaussien, ou, dans Optuna, des estimateurs de densité), et on essaie ensuite le point qui semble **le plus prometteur**, en équilibrant *exploitation* (près des bons points connus) et *exploration* (là où l'on ne sait rien).

Le plus répandu dans les bibliothèques actuelles est le **TPE** (*Tree-structured Parzen Estimator*). Son idée tient en trois phrases : on sépare les essais déjà faits en deux groupes, les **bons** (les 25 % meilleurs scores) et les **autres** ; on estime la densité $\ell(x)$ des réglages parmi les bons et la densité $g(x)$ parmi les autres ; on essaie ensuite le réglage $x$ qui **maximise le rapport $\ell(x)/g(x)$**, c'est-à-dire un réglage « typique des bons essais et rare parmi les mauvais ».

```python
import optuna

def objectif(essai):
    p = {"learning_rate": essai.suggest_float("learning_rate", 0.01, 0.5, log=True),
         "max_leaf_nodes": essai.suggest_int("max_leaf_nodes", 4, 128),
         "l2_regularization": essai.suggest_float("l2_regularization", 1e-3, 10, log=True),
         "min_samples_leaf": essai.suggest_int("min_samples_leaf", 5, 100)}
    return cross_val_score(modele_hgb(**p), X5, y5, cv=cv, scoring="roc_auc").mean()

etude = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0))
etude.optimize(objectif, n_trials=30)
print(round(etude.best_value, 4))
```
<!--sortie-->
```text
0.8951
```

```python hide
etude_alea = optuna.create_study(direction="maximize", sampler=optuna.samplers.RandomSampler(seed=0))
etude_alea.optimize(objectif, n_trials=30)
vt = [t.value for t in etude.trials]; va = [t.value for t in etude_alea.trials]
print("TPE : meilleur", round(max(vt), 4), "à l'essai", int(np.argmax(vt)) + 1, "| aléatoire : meilleur", round(max(va), 4), "à l'essai", int(np.argmax(va)) + 1)
print("TPE : meilleurs paramètres", {k: round(v, 3) for k, v in etude.best_params.items()})
print("moyenne des 10 premiers essais : TPE", np.mean(vt[:10]).round(4), "aléatoire", np.mean(va[:10]).round(4), "| moyenne des 10 derniers : TPE", np.mean(vt[-10:]).round(4), "aléatoire", np.mean(va[-10:]).round(4))
fig, ax = plt.subplots(figsize=(7.2, 3.5))
ax.plot(range(1, 31), np.maximum.accumulate(vt), color=BLEU, lw=2, drawstyle="steps-post", label="TPE (Optuna)")
ax.plot(range(1, 31), np.maximum.accumulate(va), color=ORANGE, lw=2, drawstyle="steps-post", label="recherche aléatoire")
ax.scatter(range(1, 31), vt, color=BLEU, s=14, alpha=0.5); ax.scatter(range(1, 31), va, color=ORANGE, s=14, alpha=0.5)
ax.set_xlabel("numéro de l'essai"); ax.set_ylabel("AUC en validation croisée"); ax.legend(frameon=False, loc="lower right"); ax.set_ylim(0.84, 0.905)
ax.set_title("Meilleur score atteint après chaque essai (traits) et score de chaque essai (points)", fontsize=9.5)
plt.tight_layout(); plt.savefig("figures/ch01-recherche.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
TPE : meilleur 0.8951 à l'essai 29 | aléatoire : meilleur 0.8984 à l'essai 25
TPE : meilleurs paramètres {'learning_rate': 0.038, 'max_leaf_nodes': 121, 'l2_regularization': 0.261, 'min_samples_leaf': 95}
moyenne des 10 premiers essais : TPE 0.8862 aléatoire 0.8862 | moyenne des 10 derniers : TPE 0.8926 aléatoire 0.888
```

![Optimisation de 4 hyperparamètres d'un gradient boosting en 30 essais : meilleur score atteint après chaque essai (traits) et score de chaque essai (points), pour le TPE d'Optuna (bleu) et pour la recherche aléatoire (orange).](figures/ch01-recherche.png)

(Le TPE démarre par 10 essais **aléatoires**, identiques ici à ceux de la recherche aléatoire puisque la graine est la même : c'est pourquoi les dix premiers points de la figure sont confondus.) Les deux méthodes finissent au même niveau : **0,895** pour le TPE, **0,898** pour la recherche aléatoire, un écart de 0,003, dans le bruit de la mesure (section 1.4.3). Dans cette expérience, **le TPE n'a pas fait mieux que le hasard** ; les dix premiers essais des deux méthodes valent la même moyenne (0,886), mais les **dix derniers** du TPE ont une moyenne de 0,893, contre 0,888 pour le hasard : il a bien appris à se concentrer sur les bonnes régions, sans que cela ait suffi, ici, à battre le meilleur tirage du hasard. Ce résultat est un bon exemple d'**honnêteté expérimentale** : on ne peut pas conclure qu'une méthode « plus intelligente » gagne toujours, surtout avec un budget de 30 essais sur 4 hyperparamètres. L'optimisation bayésienne tient surtout ses promesses quand **chaque essai coûte très cher** (réseaux de neurones, grands jeux de données) et que le budget est de l'ordre de quelques dizaines d'essais.

### 1.5.4 L'arrêt précoce

Pour les modèles construits **itération après itération** (boosting, réseaux de neurones), le **nombre d'itérations** est lui-même un hyperparamètre, et un régulateur très efficace : trop peu, le modèle sous-apprend ; trop, il surapprend. L'**arrêt précoce** (*early stopping*) évite d'avoir à le deviner : on met de côté une petite partie des données (15 % ici), on suit la perte sur cette partie à chaque itération, et on **s'arrête quand elle cesse de baisser** pendant un nombre fixé d'itérations (la « patience », ici 10).

```python hide
m = HistGradientBoostingClassifier(categorical_features="from_dtype", early_stopping=True, validation_fraction=0.15, n_iter_no_change=10, max_iter=500, learning_rate=0.1, random_state=0).fit(X_tr, y_tr)
perte_tr, perte_va = -m.train_score_[1:], -m.validation_score_[1:]; meilleure = int(np.argmin(perte_va)) + 1
print("arrêt après", m.n_iter_, "itérations sur un maximum de 500 | meilleure itération", meilleure, "| perte de validation minimale", perte_va.min().round(4), "| perte d'entraînement à l'arrêt", perte_tr[-1].round(4))
fig, ax = plt.subplots(figsize=(7.2, 3.4))
ax.plot(range(1, len(perte_tr) + 1), perte_tr, color=BLEU, lw=2, label="entraînement"); ax.plot(range(1, len(perte_va) + 1), perte_va, color=ORANGE, lw=2, label="validation interne")
ax.axvline(meilleure, color=MUET, ls="--", lw=1); ax.text(meilleure + 1, perte_va.max() * 0.93, f"meilleure itération : {meilleure}", fontsize=9, color=ENCRE2)
ax.set_xlabel("itération (nombre d'arbres)"); ax.set_ylabel("perte logarithmique"); ax.legend(frameon=False)
plt.tight_layout(); plt.savefig("figures/ch01-arret-precoce.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
arrêt après 55 itérations sur un maximum de 500 | meilleure itération 45 | perte de validation minimale 0.2709 | perte d'entraînement à l'arrêt 0.1485
```

![Perte logarithmique d'un gradient boosting sur les données d'entraînement (bleu) et sur la partie de validation interne (orange) selon le nombre d'itérations ; l'arrêt précoce interrompt l'entraînement peu après le minimum de la validation.](figures/ch01-arret-precoce.png)

La perte d'entraînement baisse sans cesse, celle de la validation interne atteint son minimum à l'itération 45 puis cesse de baisser ; l'algorithme s'arrête à l'itération 55 (45 plus la patience de 10), bien avant le maximum de 500. **On a évité de choisir le nombre d'arbres à la main.** Attention cependant : la partie de validation interne est tirée **au hasard**, ce qui rend le nombre d'itérations dépendant de la graine (c'est le phénomène de la section 1.4.3).

### 1.5.5 Le piège du réglage et la validation imbriquée

Voici le piège central de cette section. Chaque fois que l'on essaie une combinaison et qu'on lit son score de validation, on **apprend quelque chose du jeu de validation**. Après des centaines d'essais, le meilleur score est celui d'une combinaison **sélectionnée pour avoir bien marché sur cette validation**, en partie par chance : c'est le biais d'optimisme de la démonstration 1.1.2, appliqué à la sélection d'un réglage.

Mesurons-le dans un cas où l'on connaît la vérité : **il n'y a rien à apprendre**. On prend 150 clients dont on remplace les étiquettes par un tirage à pile ou face, et on règle un arbre de décision (profondeur, taille des feuilles, nombre de variables considérées) par 300 essais aléatoires évalués par validation croisée à 5 plis. On évalue ensuite le réglage retenu sur 1 000 clients « neufs », eux aussi à étiquettes aléatoires.

```python hide
rng = np.random.default_rng(0); n_app = 150
Xb = X_tr[NUM].fillna(X_tr[NUM].median()).sample(n_app + 1000, random_state=1).values; yb_ = rng.integers(0, 2, n_app + 1000)
Xa, Xh, ya_, yh = Xb[:n_app], Xb[n_app:], yb_[:n_app], yb_[n_app:]
from sklearn.tree import DecisionTreeClassifier
dist_arbre = {"max_depth": randint(1, 12), "min_samples_leaf": randint(1, 20), "max_features": randint(1, len(NUM))}
r = RandomizedSearchCV(DecisionTreeClassifier(random_state=0), dist_arbre, n_iter=300, cv=5, scoring="roc_auc", random_state=0).fit(Xa, ya_)
print("bruit pur : meilleur AUC de validation croisée", round(r.best_score_, 3), "| AUC du même réglage sur 1000 clients neufs", round(roc_auc_score(yh, r.predict_proba(Xh)[:, 1]), 3))
```
<!--sortie-->
```text
bruit pur : meilleur AUC de validation croisée 0.661 | AUC du même réglage sur 1000 clients neufs 0.533
```

Le réglage sélectionné annonce une AUC de **0,66** en validation croisée, alors qu'il n'y a **aucun signal** ; sur des données neuves, il tombe à **0,53**, le hasard. Les 0,13 de différence mesurent l'auto-persuasion de la recherche : avec 300 essais, l'un d'eux a forcément eu de la chance. La parade est la **validation croisée imbriquée** (section 1.2.5) : la recherche d'hyperparamètres est refaite **à l'intérieur** de chaque pli d'une validation externe, et le score est mesuré sur le pli externe, que la recherche n'a jamais vu.

Le même calcul, **imbriqué**, pour 30 essais par recherche interne (`Xa` et `ya_` désignent les 150 clients aux étiquettes aléatoires) :

```python
recherche = RandomizedSearchCV(DecisionTreeClassifier(random_state=0), dist_arbre, n_iter=30, cv=3, scoring="roc_auc", random_state=0)
imbrique = cross_val_score(recherche, Xa, ya_, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc")
print("validation imbriquée :", imbrique.mean().round(3))
```
<!--sortie-->
```text
validation imbriquée : 0.483
```

La validation imbriquée donne **0,48** : elle voit juste (pas de signal, donc le hasard). Elle estime la performance de la **procédure complète** « régler, puis entraîner », et c'est cette procédure qu'il faut évaluer.

> ⚠️ **Règles pour un réglage honnête.**
> - Le **jeu de test** (section 1.1) ne sert **jamais** au réglage.
> - Limitez la **taille de la recherche** : plus on essaie de combinaisons sur peu de données, plus l'optimisme grandit. Ici, 300 essais sur 150 clients ; sur 9 000 clients et 30 essais, l'effet est bien plus faible.
> - Quand l'estimation honnête de la performance compte (publication, décision d'investissement), utilisez la validation **imbriquée**.
> - Après le réglage, **réentraînez** le modèle final avec les meilleurs hyperparamètres sur toutes les données d'entraînement.

> ✅ **À retenir.**
> - Les **hyperparamètres** sont fixés avant l'apprentissage et pilotent le compromis biais-variance ; on les règle par le score de **validation**.
> - La **recherche aléatoire** coûte un budget fixe, quel que soit le nombre d'hyperparamètres ($1-0{,}95^n$ chances de toucher une zone excellente de 5 %) ; la grille croît exponentiellement.
> - L'**optimisation bayésienne** (TPE, Optuna) exploite l'historique des essais : utile quand chaque essai coûte cher, **sans garantie** de gagner (ici : 0,895 contre 0,898 pour le hasard).
> - L'**arrêt précoce** choisit le nombre d'itérations d'un modèle itératif en surveillant une validation interne.
> - Le meilleur score d'une recherche est **optimiste** : sur du bruit pur, 0,66 annoncé pour 0,53 réel. Seule la validation **imbriquée** estime honnêtement la procédure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.8 et 1.9, exercices 1.11 et 1.12.
