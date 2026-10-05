## 2.5 ➕ Pour aller plus loin : la théorie de la mesure (ce que « probabilité » veut vraiment dire)

> 🧭 **Section optionnelle**, plus abstraite. Elle n'est pas nécessaire pour la suite du livre. Elle répond à une question que se posent les lecteurs curieux : *« jusqu'ici, on a dit « une probabilité est un nombre entre 0 et 1 qui vérifie des règles », mais pour quels événements est-elle définie, et pourquoi ces règles ? »*

### 2.5.1 Le problème : on ne peut pas mesurer tous les ensembles

Pour un dé, tout est simple : $\Omega$ a six éléments et on peut attribuer une probabilité à **n'importe quelle** partie. Mais prenons une variable **uniforme sur $[0,1]$** : on voudrait que la probabilité d'un intervalle soit sa **longueur** ($P([a,b])=b-a$). Peut-on étendre cette idée à **tous** les sous-ensembles de $[0,1]$ en gardant des règles raisonnables (invariance par translation, additivité) ?

**Non.** En 1905, Giuseppe Vitali a construit des ensembles « pathologiques » auxquels aucune longueur cohérente ne peut être attribuée (la construction utilise l'axiome du choix). Ce n'est pas une curiosité : cela oblige à **limiter** les événements auxquels on attribue une probabilité.

### 2.5.2 Le cadre : un espace probabilisé $(\Omega,\mathcal F,P)$

La théorie moderne (Kolmogorov, 1933) est fondée sur trois objets.

- $\Omega$ : l'**univers** (toutes les issues).
- $\mathcal F$ : une **tribu** (ou σ-algèbre), c'est-à-dire la famille des événements **dont on sait parler**. Elle doit contenir $\Omega$, être stable par complémentaire et par **union dénombrable**. (Pour $[0,1]$, on prend la tribu **borélienne**, engendrée par les intervalles.)
- $P$ : une **mesure de probabilité** sur $\mathcal F$, avec $P(\Omega)=1$ et la **σ-additivité** : pour des événements $A_1,A_2,\dots$ deux à deux incompatibles,

$$P\Bigl(\bigcup_{i=1}^{\infty}A_i\Bigr)=\sum_{i=1}^{\infty}P(A_i).$$

Notez la différence avec l'axiome 3 du 2.1.1 : on demande l'additivité pour des unions **infinies dénombrables**, pas seulement finies. C'est elle qui rend possibles les passages à la limite (comme la loi des grands nombres).

> 💡 **Intuition.** La tribu est la liste des « questions autorisées » : « la variable tombe-t-elle entre 0,3 et 0,4 ? », « est-elle rationnelle ? », « est-elle dans l'union d'une suite d'intervalles ? ». La mesure $P$ répond à chacune par un nombre.

### 2.5.3 Une conséquence surprenante : événements de probabilité 0 qui arrivent

Soit $X$ uniforme sur $[0,1]$. Pour tout réel $x$, $P(X=x)=0$ (déjà vu en 2.2.1). Et pourtant $X$ prend bien *une* valeur. Un événement de probabilité nulle n'est donc **pas impossible**.

> 📐 **Les rationnels ont une probabilité nulle.** Les nombres rationnels de $[0,1]$ forment un ensemble **dénombrable** : $q_1,q_2,q_3,\dots$. Par σ-additivité,
>
> $$P(X\in\mathbb Q)=\sum_{i=1}^\infty P(X=q_i)=\sum_{i=1}^\infty 0=0.$$
>
> **Presque sûrement**, un nombre tiré au hasard dans $[0,1]$ est irrationnel ! (On dit qu'un événement est vrai **presque sûrement** (p.s.) quand sa probabilité vaut 1.)

### 2.5.4 L'espérance comme intégrale

En théorie de la mesure, une **variable aléatoire** est une fonction $X:\Omega\to\mathbb R$ **mesurable** (pour toute question « $X\le x$ ? », la réponse est un événement de la tribu). Son espérance est l'**intégrale de Lebesgue** :

$$E[X]=\int_\Omega X\,dP .$$

Cette seule définition recouvre les cas discret ($\sum$) et continu ($\int f$) du 2.3.1, mais aussi les cas **mixtes** que ni l'un ni l'autre ne gère. Voici un exemple pratique.

> 💡 **Un cas réel : les dépenses « à zéros ».** Un client visitant la boutique dépense **0 €** avec une probabilité de 70 % (il regarde sans acheter) ; sinon sa dépense suit une loi exponentielle de moyenne 80 €. Cette variable n'a **ni** fonction de masse (car elle prend un continuum de valeurs) **ni** densité (car elle a un « atome » en 0 : $P(X=0)=0{,}7>0$). C'est une loi **mixte**. Mais son espérance se calcule sans difficulté : on décompose selon le cas.

$$E[X]=0{,}7\times0+0{,}3\times80=24\ \text{€}.$$

Une simulation de 500 000 clients confirme ces chiffres : 70,0 % de dépenses nulles, une dépense moyenne de 24,03 € (théorie : 24), et une **médiane égale à 0** (70 % des clients ne dépensent rien).

Les données réelles de commerce sont très souvent de ce type (« zero-inflated »), et c'est la raison pour laquelle on ne peut pas toujours plaquer une loi normale ou exponentielle sans réfléchir.

> ⚠️ **Un conseil pratique.** Pour une loi mixte, la moyenne (24) et la médiane (0) racontent des histoires totalement différentes. Résumer par un seul nombre est trompeur ; il faut présenter la part de zéros et la moyenne conditionnelle aux achats.

### 2.5.5 Les modes de convergence

Quand on dit « $\bar X_n$ converge vers $\mu$ », encore faut-il dire **en quel sens**. Pour des variables aléatoires, il existe plusieurs façons, de la plus forte à la plus faible :

| Mode | Notation | Signification | Exemple |
|---|---|---|---|
| **Presque sûre** | $X_n\xrightarrow{p.s.}X$ | pour (presque) chaque « histoire » $\omega$, la suite de nombres $X_n(\omega)$ converge au sens usuel | **loi forte** des grands nombres |
| **En probabilité** | $X_n\xrightarrow{P}X$ | $P(\lvert X_n-X\rvert>\varepsilon)\to0$ | **loi faible** (démontrée en 2.4.2) |
| **En loi** | $X_n\xrightarrow{\mathcal L}X$ | les fonctions de répartition convergent | **TCL** |

On a : p.s. ⟹ en probabilité ⟹ en loi (et jamais l'inverse en général). La **loi forte** des grands nombres, plus difficile à démontrer, affirme que, pour *presque* chaque suite d'observations, la moyenne cumulée converge. C'est ce que montre chacune des courbes de la figure de la section 2.4.2 : chaque trajectoire se stabilise.

> 💡 **Pourquoi se soucier de cela ?** Pour un praticien, la différence compte surtout dans la formulation des garanties : « avec une probabilité 95 %, mon estimation est à ±2 points » est un énoncé **en probabilité/en loi** sur *un* échantillon ; « mon estimateur finira par donner la bonne valeur » est un énoncé **presque sûr** sur une suite infinie de données.

### 2.5.6 La densité comme dérivée d'une mesure

Quand dit-on qu'une variable « a une densité » ? Réponse : quand sa loi $P_X$ est **absolument continue** par rapport à la mesure de Lebesgue (la « longueur »), c'est-à-dire que tout ensemble de longueur nulle a probabilité nulle. Le **théorème de Radon–Nikodym** garantit alors l'existence d'une densité $f$ telle que $P_X(A)=\int_Af(x)\,dx$. Dans l'exemple des dépenses à zéros, $P_X(\{0\})=0{,}7$ alors que $\{0\}$ est de longueur nulle : pas de densité, ce que nous avions remarqué.

> ✅ **À retenir (théorie de la mesure).**
>
> - On ne peut pas assigner de probabilité à *tous* les sous-ensembles : on se limite à une **tribu** $\mathcal F$.
> - Un espace probabilisé est $(\Omega,\mathcal F,P)$ avec $P$ **σ-additive**.
> - Un événement de probabilité 0 n'est pas impossible ; « presque sûrement » = avec probabilité 1.
> - Espérance = intégrale de Lebesgue ; elle gère les lois mixtes (atome + densité).
> - Trois convergences : presque sûre ⟹ en probabilité ⟹ en loi (LGN forte, LGN faible, TCL).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6 (dépenses « à zéros »).

```python hide
# Vérifie les nombres cités dans la section 2.5 (loi mixte « dépenses à zéros »).
import numpy as np
rng = np.random.default_rng(31)
n = 500_000
achete = rng.random(n) < 0.3
depense = np.where(achete, rng.exponential(80, size=n), 0.0)
print("P(X = 0) simulée :", round((depense == 0).mean(), 4), "| E[X] simulée :", round(depense.mean(), 2), "| médiane :", round(np.median(depense), 2), "| théorie E = ", 0.3 * 80)
```
<!--sortie-->
```text
P(X = 0) simulée : 0.6998 | E[X] simulée : 24.03 | médiane : 0.0 | théorie E =  24.0
```
