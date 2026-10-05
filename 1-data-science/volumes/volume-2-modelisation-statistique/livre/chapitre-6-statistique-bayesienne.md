# Chapitre 6 : Statistique bayésienne et simulation

> « Toute connaissance est une croyance qu'on a promis de réviser à la lumière des faits. »

Dans le volume I, nous avons mesuré l'incertitude avec des **intervalles de confiance** et des **p-valeurs**. Cette façon de faire, dite *fréquentiste*, répond à la question : « *si je refaisais mon étude des milliers de fois, quelle serait la fréquence de telle ou telle erreur de ma méthode ?* » C'est une réponse rigoureuse… mais ce n'est pas celle que la gérante attend. La gérante demande plutôt : « *vu ce que j'ai observé, quelle est la probabilité que l'offre de bienvenue fonctionne ?* ». Une **probabilité sur le paramètre lui-même**.

La statistique **bayésienne** répond directement à cette question, en appliquant la formule de Bayes (volume I, section 2.1) non plus à des événements, mais à des **paramètres inconnus**. Elle y ajoute un ingrédient que le fréquentisme refuse : **ce que l'on sait avant de regarder les données** (la loi *a priori*). En contrepartie, elle exige souvent des calculs d'intégrales que personne ne sait faire à la main : c'est là qu'intervient la **simulation** (Monte-Carlo, MCMC), qui est devenue l'outil central de la modélisation moderne, bayésienne ou non.

## Le chemin de ce chapitre

- **6.1 Inférence bayésienne et lois a priori** : la formule de Bayes pour un paramètre, des exemples à la main, les lois conjuguées, le choix de l'a priori, la loi prédictive.
- **6.2 Méthodes de Monte-Carlo** : estimer une espérance ou une probabilité en **simulant**, vitesse de convergence en $1/\sqrt n$, échantillonnage préférentiel, réduction de variance.
- **6.3 MCMC** : quand on ne sait pas simuler directement, on fabrique une **chaîne de Markov** dont la loi limite est celle qu'on veut. Metropolis-Hastings et Gibbs, dont les cœurs tiennent en quelques lignes de NumPy.
- **6.4 Vérification des modèles bayésiens** : savoir si la chaîne a convergé, si le modèle est plausible, comment comparer deux modèles.
- ➕ **Pour aller plus loin** : la théorie des **valeurs extrêmes** (6.5) et les **copules** (6.6), qui modélisent les événements rares et la dépendance.

> 🧭 **Comment lire ce chapitre.** Les sections 6.1 et 6.2 sont indépendantes l'une de l'autre et se lisent bien d'un trait. La section 6.3 suppose 6.1 (pour le sens de la loi *a posteriori*) et 6.2 (pour le sens d'« échantillon simulé »). La section 6.4 suppose 6.3. Les sections ➕ 6.5 et 6.6 demandent seulement le chapitre 2 du volume I (et, pour la simulation par inversion, la section 6.2.4) ; elles peuvent être lues à part.

> 📦 **Les données utilisées.** Principalement `donnees/clients.csv` (2 000 clients de la boutique, simulés ; voir l'introduction du volume). Nous nous intéressons surtout à `rachat_12m` (le client a-t-il recommandé dans les 12 mois ?), à `offre_bienvenue` (une offre attribuée **au hasard** à la moitié des clients), à `canal_acquisition` et à `nb_commandes_an`. Comme les données sont **simulées**, nous connaîtrons à la fin la vraie valeur de plusieurs paramètres : ce sera l'occasion de vérifier que la méthode les retrouve.

> ⚠️ **Honnêteté sur les outils.** Les bibliothèques bayésiennes professionnelles (PyMC, Stan) **ne sont pas installées** dans l'environnement qui a servi à produire ce livre. Leur code est montré dans la section 6.3.7, marqué « non exécuté ». Tous les algorithmes dont nous donnons les résultats sont **écrits à la main en NumPy** : c'est aussi la meilleure façon de comprendre ce que ces bibliothèques font à votre place.

> 📒 **Le code et les exercices.** Dans ce livre, le code n'apparaît que lorsque l'algorithme est le sujet (la marche de Metropolis, l'échantillonneur de Gibbs, le log-posterior). Toutes les simulations, tous les graphiques et tous les chiffres cités sont pourtant produits par du code exécuté, avec des graines fixes. Le **cahier d'exercices et d'applications** (chapitre 6) donne ce code pas à pas, six applications guidées et quatorze exercices corrigés. Les graines sont fixées : vous retrouverez les mêmes nombres, à de très légères variations près selon les versions des bibliothèques.


## 6.1 Inférence bayésienne et lois a priori

> 💡 **Intuition.** Un détective arrive sur une scène de crime avec des **soupçons** (« le jardinier a déjà été condamné »). Chaque indice (une empreinte, un alibi) **déplace** ses soupçons : certains suspects deviennent plus probables, d'autres moins. À la fin, il a des soupçons *mis à jour*. L'inférence bayésienne est exactement cela, avec des nombres : on part d'une loi *a priori* (les soupçons), on observe des données (les indices), on obtient une loi *a posteriori* (les soupçons mis à jour). Et la **règle de mise à jour** est la formule de Bayes que vous connaissez depuis le volume I (section 2.1).

### 6.1.1 La formule de Bayes, version « paramètre »

Au volume I, la formule de Bayes disait : $P(A\mid B)=\dfrac{P(B\mid A)\,P(A)}{P(B)}$. Remplaçons $A$ par « le paramètre vaut $\theta$ » et $B$ par « nous avons observé les données $y$ » :

$$\underbrace{p(\theta\mid y)}_{\text{a posteriori}}\;=\;\frac{\overbrace{p(y\mid\theta)}^{\text{vraisemblance}}\;\overbrace{p(\theta)}^{\text{a priori}}}{\underbrace{p(y)}_{\text{constante de normalisation}}}\;\propto\;p(y\mid\theta)\,p(\theta).$$

Trois ingrédients, trois noms à retenir :

- la **vraisemblance** $p(y\mid\theta)$ : *la même fonction* que celle du maximum de vraisemblance du volume I (section 3.2). Elle dit à quel point les données observées sont plausibles pour chaque valeur de $\theta$ ;
- la loi **a priori** $p(\theta)$ : ce que l'on croit de $\theta$ **avant** de voir les données ;
- la loi **a posteriori** $p(\theta\mid y)$ : ce que l'on croit **après**. C'est *le* résultat d'une analyse bayésienne : toute l'information sur $\theta$ tient dans cette loi.

Le symbole $\propto$ se lit « proportionnel à » : le dénominateur $p(y)=\int p(y\mid\theta)p(\theta)\,d\theta$ ne dépend pas de $\theta$, il sert seulement à ce que l'aire sous la courbe vaille 1. **Tout le travail bayésien tient dans cette phrase : a posteriori = vraisemblance × a priori, puis on normalise.**

> ⚠️ **Le point qui divise.** Pour un fréquentiste, $\theta$ est une constante inconnue : dire « $P(\theta>0{,}5)=0{,}98$ » n'a pas de sens, car $\theta$ est soit plus grand que 0,5, soit non. Pour un bayésien, la probabilité mesure **notre degré de connaissance**, donc elle s'applique aussi à $\theta$. Ce n'est pas une querelle de mots : cela change les phrases qu'on a le droit de prononcer (6.1.4). Dans ce livre, nous adoptons une position pragmatique : les deux approches sont des outils, et les chiffres qu'elles donnent coïncident souvent quand les données sont abondantes.

### 6.1.2 Un exemple minuscule, calculé à la main

La gérante envoie une offre de bienvenue à **10 nouveaux clients**. Sept d'entre eux repassent commande dans l'année. Appelons $\theta$ la probabilité qu'un client avec offre rachète. Que sait-on de $\theta$ ?

**Vraisemblance.** Si les clients sont indépendants, le nombre $y$ de rachats suit une loi binomiale $\mathrm{Bin}(10,\theta)$ (volume I, section 2.2) :
$$p(y=7\mid\theta)=\binom{10}{7}\theta^{7}(1-\theta)^{3}.$$

**A priori.** La gérante n'a aucune idée précise : elle juge que toutes les valeurs de $\theta$ entre 0 et 1 sont également plausibles ($p(\theta)=1$ sur $[0,1]$).

Pour calculer à la main sans intégrale, regardons seulement **onze valeurs** possibles : $\theta\in\{0;\,0{,}1;\,0{,}2;\dots;1\}$, chacune avec la probabilité *a priori* $1/11$. C'est l'**approximation sur grille**. Il suffit de multiplier, puis de diviser par la somme.

Par exemple pour $\theta=0{,}7$ : $\theta^{7}(1-\theta)^{3}=0{,}7^{7}\times0{,}3^{3}=0{,}0823543\times0{,}027=0{,}0022236$. (On peut ignorer le coefficient binomial $\binom{10}{7}$, qui est le même pour toutes les valeurs de $\theta$ et disparaît à la normalisation.) Un tableur (ou quelques lignes de code) fait les onze calculs. Voici le résultat :

| $\theta$ | a priori | vraisemblance (sans le coefficient binomial) | a posteriori |
|---:|---:|---:|---:|
| 0,0 | 0,091 | 0 | 0,000 |
| 0,1 | 0,091 | 0,00000 | 0,000 |
| 0,2 | 0,091 | 0,00001 | 0,001 |
| 0,3 | 0,091 | 0,00008 | 0,010 |
| 0,4 | 0,091 | 0,00035 | 0,047 |
| 0,5 | 0,091 | 0,00098 | 0,129 |
| 0,6 | 0,091 | 0,00179 | 0,236 |
| **0,7** | 0,091 | **0,00222** | **0,293** |
| 0,8 | 0,091 | 0,00168 | 0,221 |
| 0,9 | 0,091 | 0,00048 | 0,063 |
| 1,0 | 0,091 | 0 | 0,000 |

Les probabilités a posteriori somment bien à 1 (c'est le rôle de la normalisation), la valeur la plus probable est $\theta=0{,}7$ et l'espérance a posteriori vaut $0{,}667$.


On lit le résultat : avant les données, les onze valeurs sont à égalité ; après, la probabilité se concentre autour de 0,7. Les valeurs extrêmes (0, 1) sont **exclues** : 0 est impossible puisque nous avons vu des rachats, 1 est impossible puisque nous avons vu des non-rachats. La valeur la plus plausible est celle du maximum de vraisemblance, $\hat\theta=7/10$, mais l'**espérance a posteriori** est un peu plus basse (la loi est étalée plus du côté bas que du côté haut). Nous allons voir pourquoi.

### 6.1.3 La loi Bêta : le coup de génie de la conjugaison

Onze valeurs de $\theta$, c'est grossier. Avec un continuum de valeurs, il faut une intégrale. Heureusement, ici, elle se calcule **exactement**, grâce à un choix d'*a priori* bien assorti à la vraisemblance.

**Définition.** La loi **Bêta**$(a,b)$ a pour densité sur $[0,1]$
$$p(\theta)=\frac{\theta^{a-1}(1-\theta)^{b-1}}{B(a,b)},\qquad B(a,b)=\int_0^1\theta^{a-1}(1-\theta)^{b-1}d\theta .$$
Sa moyenne est $\dfrac{a}{a+b}$. Quand $a=b=1$, c'est la loi uniforme ; quand $a$ et $b$ grandissent, elle se resserre autour de sa moyenne.

> 📐 **Théorème (conjugaison bêta-binomiale).** Si $\theta\sim\mathrm{Beta}(a,b)$ et si, sachant $\theta$, $y\sim\mathrm{Bin}(n,\theta)$, alors
> $$\theta\mid y\;\sim\;\mathrm{Beta}(a+y,\;b+n-y).$$
>
> *Démonstration.* D'après la formule de Bayes, $p(\theta\mid y)\propto p(y\mid\theta)\,p(\theta)$, donc
> $$p(\theta\mid y)\;\propto\;\theta^{y}(1-\theta)^{n-y}\cdot\theta^{a-1}(1-\theta)^{b-1}\;=\;\theta^{(a+y)-1}(1-\theta)^{(b+n-y)-1}.$$
> On reconnaît, **à une constante près**, la densité d'une loi $\mathrm{Beta}(a+y,\,b+n-y)$. Comme une densité est entièrement déterminée par sa forme et par la condition « l'aire vaut 1 », la constante manquante ne peut être que $1/B(a+y,b+n-y)$. $\square$

Les statisticiens disent que la loi Bêta est **conjuguée** à la loi binomiale : l'*a posteriori* reste dans la même famille que l'*a priori*, seuls les paramètres changent. La mise à jour se résume à une **addition** :

$$\boxed{a_{\text{post}}=a+\underbrace{y}_{\text{succès}},\qquad b_{\text{post}}=b+\underbrace{n-y}_{\text{échecs}}.}$$

On peut donc voir $a$ et $b$ comme des **pseudo-observations** : $\mathrm{Beta}(a,b)$ est l'a priori qu'aurait quelqu'un qui aurait déjà vu $a-1$ succès et $b-1$ échecs. Notre exemple : $\mathrm{Beta}(1,1)$ puis $y=7,\ n=10$, donc $\theta\mid y\sim\mathrm{Beta}(8,4)$, de moyenne $8/12\approx0{,}667$.

> 📐 **L'espérance a posteriori est une moyenne pondérée.** La moyenne a posteriori vaut
> $$\mathbb E[\theta\mid y]=\frac{a+y}{a+b+n}=\underbrace{\frac{a+b}{a+b+n}}_{w}\cdot\underbrace{\frac{a}{a+b}}_{\text{moyenne a priori}}+\underbrace{\frac{n}{a+b+n}}_{1-w}\cdot\underbrace{\frac{y}{n}}_{\hat\theta_{\text{EMV}}}.$$
> C'est un **compromis** entre ce que l'on croyait (moyenne a priori) et ce que disent les données (la fréquence observée), et le poids de l'a priori, $w=\frac{a+b}{a+b+n}$, **diminue** quand $n$ augmente. Avec 10 observations et un a priori uniforme ($a+b=2$), $w=2/12\approx0{,}17$ : 17 % de l'a priori, 83 % des données. C'est la raison pour laquelle $0{,}667<0{,}7$ : l'a priori uniforme tire un peu l'estimation vers 0,5. Avec 1 000 observations, $w\approx0{,}002$ : l'a priori a disparu.

Traçons les trois lois (a priori, vraisemblance normalisée, a posteriori), et vérifions au passage que la formule exacte et la grille de onze points donnent les mêmes probabilités :


![Avec 7 rachats sur 10 : l'a priori plat (tirets gris), la vraisemblance normalisée (orange épais) et l'a posteriori Beta(8, 4) (bleu) sont superposés ; avec un a priori informatif Beta(5, 5), l'a posteriori Beta(12, 8) (violet, tirets-points) est tiré vers 0,5.](figures/ch06-bayes-10-clients.png)

L'écart maximal entre la grille et la loi exacte est nul à trois décimales près (et la moyenne exacte vaut bien $8/12=0{,}6667$) : la grille de onze points n'était pas si mauvaise. Remarquez, sur le dessin, que l'*a posteriori* et la vraisemblance normalisée sont **exactement superposés** : avec un a priori plat, **les données parlent seules** (c'est évident dans la formule : multiplier par une constante ne change pas la forme). Avec un a priori informatif $\mathrm{Beta}(5,5)$ (celui d'une personne qui croit déjà à un taux proche de 50 %), l'a posteriori $\mathrm{Beta}(12,8)$ a pour moyenne $12/20=0{,}60$ : il est **tiré vers 0,5**, c'est le compromis de la formule ci-dessus.

> ✅ **À retenir (6.1.1 à 6.1.3).** A posteriori $\propto$ vraisemblance $\times$ a priori. Avec un a priori bêta et des données binomiales, l'a posteriori est une bêta dont les paramètres s'obtiennent en **ajoutant les succès et les échecs observés**. La moyenne a posteriori est un compromis entre a priori et données, où l'a priori pèse de moins en moins quand les données s'accumulent.

### 6.1.4 Comparer deux groupes : la loi de la différence

Passons aux 2 000 clients. L'offre de bienvenue a été attribuée **au hasard** à une moitié d'entre eux : la comparaison des deux groupes est donc une vraie expérience (nous y reviendrons dans le chapitre ➕ 7). Sans offre, 441 des 985 clients ont racheté (44,77 %) ; avec offre, 578 des 1 015 (56,95 %).


Avec un a priori $\mathrm{Beta}(1,1)$ pour chaque groupe, les deux lois a posteriori sont $\mathrm{Beta}(1+y,\,1+n-y)$, soit :

| Groupe | A posteriori | Moyenne | Intervalle de crédibilité à 95 % |
|---|---|---:|---|
| sans offre | $\mathrm{Beta}(442,\,545)$ | 0,4478 | [0,4169 ; 0,4789] |
| avec offre | $\mathrm{Beta}(579,\,438)$ | 0,5693 | [0,5388 ; 0,5996] |


Pour répondre à *la* question (« l'offre augmente-t-elle le taux de rachat ? »), il faut la loi de la **différence** $\delta=\theta_1-\theta_0$. Elle n'est pas une bêta, mais on peut la **simuler** : on tire de nombreuses valeurs de $\theta_1$ et de $\theta_0$ dans leurs lois a posteriori, et on calcule leur différence. C'est la première apparition du Monte-Carlo, que nous étudions à fond en 6.2.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(61)
S = 200_000
theta1 = stats.beta(579, 438).rvs(S, random_state=rng)   # avec offre
theta0 = stats.beta(442, 545).rvs(S, random_state=rng)   # sans offre
delta = theta1 - theta0

print(f"moyenne de la différence       : {delta.mean():.4f}")
print(f"IC de crédibilité à 95 %       : [{np.percentile(delta, 2.5):.4f} ; {np.percentile(delta, 97.5):.4f}]")
print(f"P(l'offre augmente le rachat)  : {(delta > 0).mean():.5f}")
print(f"P(l'effet dépasse 5 points)    : {(delta > 0.05).mean():.4f}")
print(f"P(l'effet dépasse 10 points)   : {(delta > 0.10).mean():.4f}")
```
<!--sortie-->
```text
moyenne de la différence       : 0.1214
IC de crédibilité à 95 %       : [0.0778 ; 0.1647]
P(l'offre augmente le rachat)  : 1.00000
P(l'effet dépasse 5 points)    : 0.9993
P(l'effet dépasse 10 points)   : 0.8346
```

On peut maintenant prononcer des phrases que le volume I interdisait : « *sachant les données, l'offre augmente le rachat avec une probabilité quasi certaine* » (aucun de nos 200 000 tirages ne donne une différence négative ; l'approximation normale de la différence donne une probabilité d'erreur de l'ordre de $2\times10^{-8}$), « *la probabilité que l'effet dépasse 5 points de pourcentage est de 99,9 %, et qu'il dépasse 10 points de 83 %* ». Pour comparer avec l'approche fréquentiste, l'intervalle de confiance de Wald de la différence de proportions (volume I, section 3.4.5) est [0,0782 ; 0,1652], pour une différence observée de 0,1217.


Les deux intervalles ([0,0778 ; 0,1647] pour la crédibilité, [0,0782 ; 0,1652] pour la confiance) sont **presque identiques** (à la troisième décimale). C'est normal : avec 1 000 observations par groupe, l'a priori uniforme ne pèse presque rien. Mais l'**interprétation** diffère profondément :

| | Intervalle de confiance (fréquentiste) | Intervalle de crédibilité (bayésien) |
|---|---|---|
| Ce qui est aléatoire | l'intervalle (il change d'un échantillon à l'autre) | le paramètre $\theta$ (notre connaissance) |
| Phrase correcte | « la *méthode* encadre la vraie valeur dans 95 % des échantillons » | « sachant les données, $\delta$ est dans l'intervalle avec la probabilité 0,95 » |
| Peut-on dire « $P(\delta>0)=\dots$ » ? | non | **oui** |
| Dépend d'un a priori ? | non | oui (mais l'effet s'efface quand $n$ grandit) |

> 💡 **Ce que la gérante veut entendre.** « L'offre est presque certainement utile, et le gain est de l'ordre de 12 points de pourcentage de rachat (entre 8 et 16 avec 95 % de probabilité). » C'est une phrase bayésienne. Elle est parfaitement naturelle, et la plupart des gens interprètent d'ailleurs *intuitivement* les intervalles de confiance de cette façon (à tort, nous l'avons vu au volume I, section 3.3.2).

### 6.1.5 Intervalle de crédibilité : équi-queue ou HPD ?

Il existe plusieurs façons de fabriquer un intervalle contenant 95 % de la probabilité a posteriori. Les deux principales :

- l'intervalle **à queues égales** : il laisse 2,5 % de probabilité de chaque côté (c'est ce que fait `ppf([0.025, 0.975])`) ;
- l'intervalle de **plus haute densité** (HPD, *highest posterior density*) : le **plus court** intervalle de probabilité 95 %. Tous ses points ont une densité supérieure à ceux qui sont en dehors.

Pour une loi symétrique, ils coïncident. Pour une loi asymétrique (proche de 0 ou de 1, par exemple), ils diffèrent. Prenons un nouveau canal testé auprès de 20 clients, dont un seul a racheté : l'a posteriori est $\mathrm{Beta}(2,20)$, de moyenne 0,0909. L'intervalle à queues égales est [0,0117 ; 0,2382] (largeur 0,2264) ; le HPD, qu'on obtient en faisant glisser une fenêtre de probabilité 95 % le long de la loi et en gardant la plus étroite, est [0,0026 ; 0,2080] (largeur 0,2054).


Le HPD est donc plus court et plus proche de zéro, ce qui correspond mieux à l'idée intuitive d'un intervalle qui « suit » la densité. Pour les lois à peu près symétriques de ce chapitre, la différence est mineure ; l'intervalle à queues égales est le plus répandu.

### 6.1.6 Le choix de l'a priori : liberté, responsabilité, et sensibilité

C'est la grande critique adressée à la méthode : « *l'a priori est subjectif* ». Voyons concrètement ce qu'il change.

**Quatre a priori pour une probabilité de rachat $\theta$.**

| A priori | Paramètres | Ce qu'il dit | Pseudo-observations |
|---|---|---|---|
| Uniforme | $\mathrm{Beta}(1,1)$ | « je n'ai aucune idée » | 2 |
| Jeffreys | $\mathrm{Beta}(\tfrac12,\tfrac12)$ | invariant par reparamétrisation (plus de poids aux bords) | 1 |
| Informatif réaliste | $\mathrm{Beta}(20,20)$ | « d'après mon expérience, autour de 50 %, à quelques points près » | 40 |
| Informatif **faux** | $\mathrm{Beta}(2,18)$ | « je suis sûre que très peu de clients rachètent » (≈ 10 %) | 20 |

Comparons les lois a posteriori pour des données de plus en plus abondantes : les **10** premiers clients avec offre (3 rachats), puis les **100** premiers (55 rachats), puis les **1 015** (578 rachats). Voici la moyenne a posteriori et l'intervalle de crédibilité à 95 % :

| $n$ | Uniforme Beta(1,1) | Jeffreys Beta(½,½) | Informatif Beta(20,20) | Informatif faux Beta(2,18) |
|---:|---|---|---|---|
| 10 | 0,333 [0,109 ; 0,610] | 0,318 [0,093 ; 0,606] | 0,460 [0,325 ; 0,598] | **0,167** [0,058 ; 0,317] |
| 100 | 0,549 [0,452 ; 0,644] | 0,550 [0,452 ; 0,645] | 0,536 [0,453 ; 0,617] | 0,475 [0,387 ; 0,564] |
| 1 015 | 0,569 [0,539 ; 0,600] | 0,569 [0,539 ; 0,600] | 0,567 [0,537 ; 0,597] | 0,560 [0,530 ; 0,590] |

Les fréquences observées sont respectivement 0,30, 0,55 et 0,569.


Lisons ce tableau par bloc :

- **$n=10$** : les a priori comptent *beaucoup*. Les quatre résultats diffèrent nettement, et l'a priori « faux » (qui croit à 10 %) tire fortement la moyenne vers le bas.
- **$n=100$** : les écarts se réduisent, mais l'a priori faux pèse encore.
- **$n=1\,015$** : les quatre moyennes a posteriori sont **quasiment égales** (à moins d'un point de pourcentage près : 0,560 à 0,569), même celle de l'a priori faux. L'a priori a été « oublié ».

> 🧪 **C'est un théorème, pas seulement une observation.** Quand $n\to\infty$, tant que l'a priori n'attribue pas une probabilité nulle à la vraie valeur de $\theta$, la loi a posteriori se concentre autour de la vraie valeur, et sa forme devient celle d'une loi normale (théorème de Bernstein-von Mises). Autrement dit : **avec assez de données, des personnes aux a priori différents finissent par être d'accord**. C'est l'argument le plus fort en faveur de la méthode. L'argument le plus fort contre : avec *peu* de données, la conclusion dépend de l'a priori, et il faut alors **le dire**.

> ⚠️ **Trois règles d'hygiène.**
> 1. **Toujours dire quel a priori a été utilisé**, et le justifier en une phrase.
> 2. **Faire une analyse de sensibilité** : refaire le calcul avec deux ou trois a priori raisonnables. Si la conclusion ne change pas, tant mieux ; sinon, c'est une information importante pour le lecteur (« nos données sont insuffisantes pour trancher »).
> 3. **Ne jamais mettre une probabilité nulle** sur une valeur possible : aucune donnée ne pourrait la réhabiliter (c'est la « règle de Cromwell » : « *je vous en conjure, songez que vous puissiez vous tromper* »).

**Les a priori « faiblement informatifs ».** En pratique, ni l'uniforme total ni l'a priori très précis ne sont idéaux. On préfère souvent des lois larges mais qui **excluent l'absurde** : par exemple, pour un coefficient de régression logistique, une loi normale centrée en 0 avec un écart-type de 1,5 ou 2,5 écarte les rapports de cotes de $e^{10}$ tout en laissant passer toutes les valeurs plausibles. Nous les utiliserons en 6.3, et nous verrons en 6.4.3 comment *vérifier* qu'un a priori est raisonnable.

### 6.1.7 Intervalle de crédibilité contre intervalle de confiance : une expérience

Un intervalle de crédibilité à 95 % est-il « bon » au sens fréquentiste ? Faisons l'expérience : fixons une vraie valeur $\theta$, simulons 20 000 échantillons de taille $n=30$, et comptons dans combien de cas chaque intervalle contient $\theta$ (la **couverture**). Nous comparons l'intervalle de Wald (volume I, section 3.3.4), l'intervalle de Wilson et l'intervalle de crédibilité $\mathrm{Beta}(1,1)$ à queues égales. Voici la couverture obtenue (la valeur visée est 0,95) :

| vrai $\theta$ | Wald | Wilson | crédibilité |
|---:|---:|---:|---:|
| 0,05 | 0,781 | 0,940 | 0,940 |
| 0,10 | 0,806 | 0,974 | 0,974 |
| 0,30 | 0,954 | 0,930 | 0,930 |
| 0,50 | 0,958 | 0,958 | 0,958 |


Pour $\theta$ proche de 0 (5 % ou 10 %), l'intervalle de Wald est très en dessous de 95 % : il ne couvre la vraie valeur que dans 78 % à 81 % des cas (c'est le défaut connu qu'on avait signalé au volume I). L'intervalle de crédibilité à a priori uniforme, lui, reste dans une fourchette de 93 % à 97 %, ce qui n'a rien d'évident : *il a été construit sans aucun souci de couverture*. Remarquez aussi que sa couverture est **identique** à celle de l'intervalle de Wilson, dans les quatre lignes : ce n'est pas un hasard, les deux intervalles ne diffèrent que de 0,002 au plus pour $n=30$ et décident de la même façon pour chaque valeur possible du nombre de succès. L'approche bayésienne et le meilleur intervalle fréquentiste se rejoignent. C'est un résultat général : sous des hypothèses douces, les intervalles de crédibilité des modèles réguliers ont une bonne couverture fréquentiste quand $n$ est assez grand.

### 6.1.8 Autres couples conjugués : Poisson-Gamma et Normal-Normal

L'idée de conjugaison dépasse le cas bêta-binomial. Voici deux autres couples très utiles ; leurs démonstrations ont **exactement la même structure** (multiplier, reconnaître une forme, normaliser).

**Poisson-Gamma (comptages).** On observe des comptages $y_1,\dots,y_n$ indépendants de loi $\mathrm{Poisson}(\lambda)$, avec $\lambda\sim\mathrm{Gamma}(a,\text{taux }b)$ de densité $\propto\lambda^{a-1}e^{-b\lambda}$.

> 📐 **Théorème.** $\lambda\mid y\;\sim\;\mathrm{Gamma}\!\left(a+\sum_i y_i,\;\; b+n\right)$.
>
> *Démonstration.* $p(y\mid\lambda)\propto\prod_i\lambda^{y_i}e^{-\lambda}=\lambda^{\sum y_i}e^{-n\lambda}$. En multipliant par l'a priori : $p(\lambda\mid y)\propto\lambda^{a+\sum y_i-1}e^{-(b+n)\lambda}$, qui est la densité d'une $\mathrm{Gamma}(a+\sum y_i,\,b+n)$. $\square$

*Exemple à la main.* Cinq semaines, 3, 5, 4, 6, 2 commandes sur le site. A priori $\mathrm{Gamma}(a=2,\ b=0{,}5)$ (moyenne $a/b=4$ commandes par semaine, très vague). $\sum y_i=20$, $n=5$ : a posteriori $\mathrm{Gamma}(22,\ 5{,}5)$, de moyenne $22/5{,}5=4$. (Coïncidence : l'a priori et les données étaient d'accord sur 4.)

Appliquons cela aux **clients acquis par le canal Boutique** : nombre de commandes par an (`nb_commandes_an`), modélisé par $\mathrm{Poisson}(\lambda)$ avec le même $\lambda$ pour tous. Ils sont 504, pour 2 085 commandes au total (moyenne 4,137). Avec l'a priori $\mathrm{Gamma}(2;\,0{,}5)$ (moyenne 4, très vague), l'a posteriori est $\mathrm{Gamma}(2\,087;\ 504{,}5)$, de moyenne 4,137 et d'intervalle de crédibilité à 95 % [3,961 ; 4,316].


L'intervalle est étroit : on est « sûr » de $\lambda$ à 0,18 près environ. Mais regardons la dispersion : pour une vraie loi de Poisson, variance et moyenne sont égales (volume I, section 2.2) ; ici le rapport variance/moyenne vaut 3,32, soit **plus de trois fois** la valeur attendue. Les clients sont *hétérogènes* (certains commandent beaucoup, d'autres peu), et le modèle de Poisson, qui suppose le même $\lambda$ pour tous, est **faux**. L'intervalle est donc trop étroit, **et le calcul bayésien ne nous l'a pas dit**. Il ne le dit jamais tout seul : un a posteriori est toujours *conditionnel à la validité du modèle*. Nous verrons en 6.4.2 comment vérifier un modèle et en réparer un (c'est aussi le sujet de la section 2.6 pour les modèles surdispersés).

> ⚠️ **Le piège le plus fréquent de la modélisation bayésienne.** Un a posteriori très étroit ne prouve **pas** qu'on est sûr de soi : il prouve qu'on est sûr *si le modèle est juste*. Un modèle faux produit des intervalles étroits et faux, avec la même élégance.

**Normal-Normal (moyenne d'une loi normale, variance connue).** Si $y_i\sim\mathcal N(\mu,\sigma^2)$ avec $\sigma$ connu et $\mu\sim\mathcal N(\mu_0,\tau_0^2)$, alors $\mu\mid y\sim\mathcal N(\mu_n,\tau_n^2)$ avec
$$\frac1{\tau_n^2}=\frac1{\tau_0^2}+\frac n{\sigma^2},\qquad \mu_n=\tau_n^2\left(\frac{\mu_0}{\tau_0^2}+\frac{n\bar y}{\sigma^2}\right).$$
On additionne des **précisions** (l'inverse des variances) et on fait une moyenne **pondérée par les précisions**.

> 📐 **Démonstration.** On écrit les logarithmes : $\log p(\mu\mid y)=\text{cte}-\frac{(\mu-\mu_0)^2}{2\tau_0^2}-\frac{\sum(y_i-\mu)^2}{2\sigma^2}$. Or $\sum(y_i-\mu)^2=\sum(y_i-\bar y)^2+n(\bar y-\mu)^2$ ; le premier terme ne dépend pas de $\mu$. Il reste un polynôme du second degré en $\mu$ :
> $$-\tfrac12\left[\mu^2\left(\tfrac1{\tau_0^2}+\tfrac n{\sigma^2}\right)-2\mu\left(\tfrac{\mu_0}{\tau_0^2}+\tfrac{n\bar y}{\sigma^2}\right)\right]+\text{cte}.$$
> Un polynôme du second degré en $\mu$ dans l'exponentielle est une densité normale ; en « complétant le carré », on lit sa précision $\frac1{\tau_n^2}$ (le coefficient de $\mu^2$) et sa moyenne $\mu_n$ (le rapport entre le coefficient de $\mu$ et celui de $\mu^2$). $\square$

*Exemple à la main.* On s'intéresse à $\mu$ = logarithme du panier moyen d'un client. Supposons $\sigma=0{,}35$ connu (hypothèse de confort, qu'on lèvera en 6.3), un a priori $\mathcal N(4{,}0;\ 0{,}5^2)$, et $n=5$ clients de moyenne $\bar y=4{,}4$. Les précisions valent $1/0{,}5^2=4$ pour l'a priori et $5/0{,}35^2=40{,}82$ pour les données. Précision totale : $44{,}82$, donc $\tau_n=1/\sqrt{44{,}82}=0{,}149$. Moyenne : $\mu_n=\dfrac{4\times4{,}0+40{,}82\times4{,}4}{44{,}82}=\dfrac{16+179{,}6}{44{,}82}=4{,}364$. Les données (91 % du poids) l'emportent largement.

Sur les 449 acheteurs du canal Boutique, la moyenne du log-panier est 4,2183 ; avec les mêmes hypothèses, l'a posteriori de $\mu$ est $\mathcal N(4{,}2181;\ 0{,}0165^2)$, d'intervalle à 95 % [4,1857 ; 4,2504].


Le panier « typique » (médiane, puisque $\mu$ est le logarithme) d'un acheteur du canal Boutique est d'environ 67,9 €, intervalle à 95 % [65,7 ; 70,1] €. Les données étant simulées, nous connaissons la vérité : le générateur a programmé un log-panier moyen de $4{,}00+0{,}22=4{,}22$ pour la boutique, soit $e^{4{,}22}\approx68{,}0$ €. L'intervalle de crédibilité contient bien cette valeur.

### 6.1.9 La loi prédictive : prédire du nouveau

Un estimateur de $\theta$ n'est pas un but en soi. La gérante veut des **prédictions** : « *sur les 100 prochains clients avec offre, combien rachèteront ?* » Deux façons de répondre :

- **Plug-in** : on remplace $\theta$ par son estimation $\hat\theta=0{,}5695$ et on prend $\mathrm{Bin}(100,\hat\theta)$. Cela **ignore** l'incertitude sur $\theta$.
- **Prédictive a posteriori** : on **moyenne** la loi binomiale sur toutes les valeurs plausibles de $\theta$, pondérées par leur probabilité a posteriori :
$$p(\tilde y\mid y)=\int p(\tilde y\mid\theta)\,p(\theta\mid y)\,d\theta.$$
Pour un a posteriori bêta, cette intégrale est connue : c'est la loi **bêta-binomiale**. Pour 100 nouveaux clients avec offre, on obtient :

| Méthode | Moyenne | Écart-type | Intervalle à 95 % |
|---|---:|---:|---|
| plug-in $\mathrm{Bin}(100,\hat\theta)$ | 56,95 | 4,95 | [47 ; 67] |
| prédictive bêta-binomiale | 56,93 | 5,19 | [47 ; 67] |
| simulation ($\theta$ puis $y$) | 56,94 | 5,20 | [47 ; 67] |


La loi prédictive est **un peu plus large** que le plug-in (écart-type 5,19 contre 4,95) : elle ajoute à la variabilité du tirage binomial l'incertitude sur $\theta$. Les intervalles à 95 % sont ici identiques ([47 ; 67]) car, avec 1 015 clients dans l'échantillon, l'incertitude sur $\theta$ est faible ; avec 10 clients, l'écart serait énorme. La simulation (tirer $\theta$, puis $y$) retrouve la loi exacte : 56,94 contre 56,93 pour la moyenne. Retenez le principe, car il est général : **une prédiction honnête incorpore l'incertitude sur les paramètres**. C'est un avantage naturel de l'approche bayésienne : la loi prédictive s'obtient sans effort supplémentaire, simplement en simulant (*simuler $\theta$, puis simuler les données sachant $\theta$*), ce que nous ferons systématiquement pour vérifier les modèles en 6.4.

> ✅ **À retenir (6.1).**
> - A posteriori $\propto$ vraisemblance $\times$ a priori. La vraisemblance est celle du volume I.
> - Les **lois conjuguées** (bêta-binomiale, gamma-Poisson, normale-normale) donnent l'a posteriori **exactement**, par simple addition de paramètres ou de précisions.
> - Un **intervalle de crédibilité** autorise la phrase « $\theta$ est dans l'intervalle avec la probabilité 95 % » ; il coïncide numériquement avec l'intervalle de confiance quand l'a priori est plat et les données abondantes.
> - L'a priori compte beaucoup avec peu de données et presque pas avec beaucoup. **Dites-le, justifiez-le, testez-en plusieurs.**
> - Un a posteriori étroit n'est valable que si le **modèle** est juste (le cas du modèle de Poisson ci-dessus).
> - La loi **prédictive** incorpore l'incertitude sur les paramètres.
> - Quand l'a posteriori n'est pas une loi connue (régression logistique, modèles hiérarchiques…), il faut **simuler** : c'est l'objet des sections 6.2 et 6.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.1, exercices 6.1 à 6.4.


## 6.2 Méthodes de Monte-Carlo

> 💡 **Intuition.** Comment connaître la probabilité de faire un « double six » avec deux dés ? On peut raisonner ($1/36$). Ou bien… **lancer les dés** dix mille fois et compter. La seconde méthode est moins élégante, mais elle a une qualité inestimable : elle marche **aussi** quand le raisonnement est impossible. Tout le monde ne sait pas calculer la probabilité qu'un portefeuille perde plus de 10 %, ou la probabilité qu'une loi *a posteriori* complexe dépasse un seuil. Mais tout le monde peut **simuler** et compter. Le nom vient du casino de Monte-Carlo, où le hasard est le métier. La méthode a été mise au point à Los Alamos dans les années 1940.

### 6.2.1 Le principe : une espérance se calcule en moyennant des simulations

Presque tout ce que l'on veut calculer en probabilités et en statistique est une **espérance** :
- une probabilité est l'espérance d'un indicateur : $P(X\in A)=\mathbb E[\mathbf 1_{A}(X)]$ ;
- une intégrale $\int g(x)f(x)\,dx$ est l'espérance $\mathbb E[g(X)]$ pour $X$ de densité $f$ ;
- une moyenne a posteriori, un risque, un prix, une probabilité de ruine…

La loi des grands nombres (volume I, section 2.4) dit que la moyenne empirique converge vers l'espérance. D'où l'idée :

> **Estimateur de Monte-Carlo.** Pour estimer $\theta=\mathbb E[g(X)]$, on simule $X_1,\dots,X_n$ indépendants de même loi que $X$, et on prend
> $$\hat\theta_n=\frac1n\sum_{i=1}^n g(X_i).$$

**Exemple à la main : estimer $\pi$ avec des fléchettes.** On lance des fléchettes uniformément dans le carré $[0,1]^2$. La probabilité de tomber dans le quart de disque $x^2+y^2<1$ est son aire, $\pi/4$. Donc $\pi=4\,\mathbb E[\mathbf 1\{X^2+Y^2<1\}]$. Voici dix fléchettes (choisies une fois pour toutes) ; on vérifie à la main pour chacune si $x^2+y^2<1$ :

| fléchette | $(x,y)$ | $x^2+y^2$ | dedans ? |
|---|---|---|---|
| 1 | (0,10 ; 0,90) | 0,82 | oui |
| 2 | (0,80 ; 0,70) | 1,13 | non |
| 3 | (0,35 ; 0,20) | 0,1625 | oui |
| 4 | (0,95 ; 0,30) | 0,9925 | oui |
| 5 | (0,60 ; 0,55) | 0,6625 | oui |
| 6 | (0,05 ; 0,15) | 0,025 | oui |
| 7 | (0,90 ; 0,90) | 1,62 | non |
| 8 | (0,45 ; 0,85) | 0,925 | oui |
| 9 | (0,70 ; 0,10) | 0,50 | oui |
| 10 | (0,25 ; 0,65) | 0,485 | oui |

Huit fléchettes sur dix sont dedans : $\hat\pi=4\times0{,}8=3{,}2$. Pas très précis, mais l'idée est là. Laissons maintenant l'ordinateur lancer un million de fléchettes. L'estimateur de Monte-Carlo tient en trois lignes :

```python
rng = np.random.default_rng(640)
xy = rng.random((1_000_000, 2))                        # un million de fléchettes dans le carré
print(4 * ((xy**2).sum(axis=1) < 1).mean())            # 4 fois la proportion dans le quart de disque
```
<!--sortie-->
```text
3.140556
```
Avec un million de fléchettes, on trouve $3{,}1406$ : l'erreur est de l'ordre du millième (le chiffre exact dépend de la graine du générateur).


En faisant varier le nombre de fléchettes $n$, l'estimation s'approche de $\pi$, **sans jamais être exacte** :

| $n$ | estimation | erreur | écart-type théorique de l'estimateur |
|---:|---:|---:|---:|
| 100 | 3,12000 | −0,02159 | 0,16422 |
| 1 000 | 3,15200 | 0,01041 | 0,05193 |
| 10 000 | 3,13000 | −0,01159 | 0,01642 |
| 100 000 | 3,13760 | −0,00399 | 0,00519 |
| 1 000 000 | 3,14366 | 0,00207 | 0,00164 |

Mais à quelle vitesse l'erreur décroît-elle ? C'est la question suivante.

### 6.2.2 La vitesse de convergence : $1/\sqrt n$

Chaque terme $g(X_i)$ est une variable aléatoire de variance $\sigma^2=\mathrm{Var}(g(X))$. L'estimateur $\hat\theta_n$ est sans biais, et, puisque les $X_i$ sont indépendants (volume I, section 2.3) :
$$\mathrm{Var}(\hat\theta_n)=\frac{\sigma^2}{n},\qquad\text{donc}\qquad \text{erreur type}=\frac{\sigma}{\sqrt n}.$$
Le théorème central limite (volume I, section 2.4) dit en plus que, pour $n$ grand, $\hat\theta_n\approx\mathcal N(\theta,\sigma^2/n)$ : on obtient donc un **intervalle de confiance** de Monte-Carlo, $\hat\theta_n\pm1{,}96\,\hat\sigma/\sqrt n$, où $\hat\sigma$ est l'écart-type empirique des $g(X_i)$. Pour $\pi$, $g=4\cdot\mathbf 1\{\dots\}$ est une variable qui vaut 4 avec la probabilité $p=\pi/4$ et 0 sinon, d'où $\sigma^2=16\,p(1-p)=\pi(4-\pi)$ : c'est la formule utilisée dans le code ci-dessus.

**Conséquence pratique.** Pour **diviser l'erreur par 10**, il faut **100 fois plus de simulations**. Pour gagner une décimale de précision, 100 fois plus de calcul. C'est lent. Vérifions-le par une expérience : pour chaque $n$, on répète 300 fois l'estimation de $\pi$ et on mesure l'écart-type observé des estimations. Résultat :

| $n$ | écart-type observé | théorie $\sigma/\sqrt n$ |
|---:|---:|---:|
| 100 | 0,16832 | 0,16422 |
| 1 000 | 0,05164 | 0,05193 |
| 10 000 | 0,01591 | 0,01642 |
| 100 000 | 0,00503 | 0,00519 |


La pente de $\log(\text{écart-type})$ en fonction de $\log n$ vaut $-0{,}508$, presque exactement $-1/2$ : doubler le nombre de chiffres décimaux coûte un facteur $10^4$ en simulations.


![À gauche : 1 000 fléchettes dans le carré, bleues si elles tombent dans le quart de disque, orange sinon. À droite : l'écart-type de l'estimateur de π en fonction du nombre de simulations, en échelles logarithmiques ; il suit la droite de pente −1/2.](figures/ch06-monte-carlo-pi.png)

> 💡 **Pourquoi utiliser une méthode si lente ?** En dimension 1, une méthode déterministe (les rectangles du volume I, section 1.2) est bien plus efficace : l'erreur de la règle des trapèzes décroît comme $1/n^2$. Mais la vitesse $1/\sqrt n$ de Monte-Carlo a une propriété extraordinaire : **elle ne dépend pas de la dimension**. Un quadrillage de 10 points par axe demande $10^{d}$ évaluations en dimension $d$ ; Monte-Carlo, lui, garde le même rythme. Illustration : le volume de la boule unité en dimension 10, dont la valeur exacte est $\pi^{5}/5!\approx2{,}5502$. On tire un million de points dans le cube $[-1,1]^{10}$ (de volume $2^{10}$) et on compte ceux qui tombent dans la boule : l'estimation vaut $2{,}602\pm0{,}101$ (intervalle à 95 %), compatible avec la valeur exacte. Un quadrillage de 10 points par axe aurait demandé dix milliards d'évaluations.


> ⚠️ **Le revers de la médaille.** Remarquez que seule une fraction minuscule des points tombe dans la boule en dimension 10 (2 541 sur un million, soit 0,25 %) : le cube est « presque vide de boule ». Cette inefficacité s'aggrave avec la dimension. Les sections 6.2.5 (échantillonnage préférentiel) et 6.3 (MCMC) sont les réponses à ce problème : mettre les points **là où ils comptent**.

### 6.2.3 Propager toute l'incertitude jusqu'à une décision

En 6.1.4, nous avons montré que l'offre de bienvenue augmente la probabilité de rachat d'environ 12 points. Mais elle **coûte** quelque chose : la remise accordée. Faut-il l'offrir à tous les futurs clients ?

Posons les hypothèses de l'étude (inventées pour l'exercice, à remplacer par les vraies valeurs de la boutique) :
- la marge de la gérante est de **30 %** du panier ;
- l'offre coûte **1,50 € par client** (la remise, quel que soit le client) ;
- un client qui rachète génère un panier tiré au hasard parmi les paniers des acheteurs observés (la distribution empirique, qui est notre meilleure image de la loi des paniers).

Le gain net **par client** de la politique « envoyer l'offre » vaut donc
$$G=(\theta_1-\theta_0)\times m-c,\qquad m=0{,}30\times\text{panier moyen d'un acheteur},\quad c=1{,}50.$$
Les inconnues sont $\theta_1,\theta_0$ (nous avons leurs lois a posteriori, 6.1.4) et $m$ (nous le « simulons » par rééchantillonnage des paniers observés, c'est un bootstrap). Monte-Carlo permet de propager **toute** l'incertitude jusqu'au résultat, ce qu'aucune formule simple ne ferait. Concrètement, on fabrique 100 000 « scénarios » : dans chacun, on tire $\theta_1$ et $\theta_0$ dans leurs lois a posteriori, une marge moyenne $m$ par rééchantillonnage des paniers, et on calcule $G$. La distribution des $G$ est la réponse. Avec une marge moyenne de 18,37 € par rachat (panier moyen des acheteurs : 61,23 €) :


Le calcul donne un gain net moyen de $+0{,}731$ € par client (intervalle à 90 % : [+0,062 ; +1,400] €), une probabilité de 0,964 que l'offre soit rentable, et, pour 5 000 nouveaux clients, un gain attendu de +3 656 € (dépassant +312 € dans 95 % des scénarios). C'est le genre de réponse qu'attend vraiment une décisionnaire : pas « l'effet est significatif » mais « *l'offre est très probablement rentable (environ 96 % de chances), le gain attendu est de 0,73 € par client, soit 3 700 € pour 5 000 clients, et dans 95 % des scénarios on gagne au moins 300 €* ». Remarquez que le gain par client reste **modeste** et que l'intervalle à 90 % ([+0,06 ; +1,40] €) s'approche de zéro : l'offre n'est pas une mine d'or, et un coût de 2 € (au lieu de 1,50) la rendrait douteuse. Les chiffres de coût et de marge étant inventés, la bonne pratique est de refaire le calcul pour plusieurs valeurs. Observez aussi que **toutes** les sources d'incertitude (les deux taux, la marge) sont propagées d'un seul mouvement, simplement en les simulant ensemble.

> 🧪 **Point de rigueur.** Le calcul suppose que l'effet de l'offre sur le rachat se traduit, pour chaque client qui rachète en plus, par un panier « moyen ». Dans les données simulées, l'offre agit sur la *probabilité* de rachat (c'est vrai par construction) ; une vraie étude vérifierait aussi si les clients « incités » dépensent autant que les autres. Un modèle ne répond qu'à la question qu'on lui a posée.

### 6.2.4 Fabriquer des tirages : l'inversion et le rejet

Jusqu'ici, nous avons utilisé `rng.random`, `stats.beta.rvs`, etc., comme des boîtes noires. Comment un ordinateur fabrique-t-il un tirage dans une loi donnée ? Voici les deux méthodes de base, qui expliquent aussi pourquoi les lois *a posteriori* compliquées posent problème.

**Méthode 1 : l'inversion.** On part d'une loi uniforme $U\sim\mathcal U(0,1)$, que l'ordinateur sait fabriquer.

> 📐 **Théorème (inversion).** Soit $F$ une fonction de répartition continue et strictement croissante, d'inverse $F^{-1}$. Alors $X=F^{-1}(U)$ a pour fonction de répartition $F$.
>
> *Démonstration.* Pour tout $x$, $P(X\le x)=P(F^{-1}(U)\le x)=P(U\le F(x))=F(x)$, car $F$ est croissante et $P(U\le u)=u$ pour $u\in[0,1]$. $\square$

*Exemple.* Le délai d'attente d'un colis suit une loi exponentielle de moyenne 3 jours, $F(x)=1-e^{-x/3}$. En résolvant $u=1-e^{-x/3}$ : $x=-3\ln(1-u)$. On simule donc des délais avec `-3 * np.log(1 - u)`, où `u` est un tirage uniforme. Avec 100 000 tirages, la moyenne simulée est 3,007 (théorie : 3) et l'écart-type 3,001 (théorie : 3) ; la probabilité simulée d'un délai de 3 jours au plus est 0,6311, contre 0,6321 exactement.


L'inversion est parfaite quand on connaît $F^{-1}$ (exponentielle, Weibull, Cauchy…), mais ce n'est **presque jamais** le cas pour une loi *a posteriori* : on ne sait même pas calculer $F$.

**Méthode 2 : le rejet.** Supposons qu'on connaisse la densité cible $f$ (même à une constante près) et qu'on sache simuler selon une loi plus simple de densité $g$, avec $f(x)\le M\,g(x)$ pour tout $x$. L'algorithme :

1. tirer $X\sim g$ et $U\sim\mathcal U(0,1)$ indépendants ;
2. **accepter** $X$ si $U\le \dfrac{f(X)}{M\,g(X)}$, sinon recommencer.

> 📐 **Théorème.** Les valeurs acceptées ont pour densité $f$, et la probabilité d'acceptation est $1/M$.
>
> *Démonstration.* La probabilité d'accepter un tirage $X\in dx$ est $g(x)\,dx\cdot\dfrac{f(x)}{Mg(x)}=\dfrac{f(x)}{M}dx$. Sommée sur $x$, elle vaut $\int\dfrac{f}{M}=\dfrac1M$ : c'est la probabilité d'acceptation. La densité de $X$ **sachant qu'il est accepté** est donc $\dfrac{f(x)/M}{1/M}=f(x)$. $\square$

*Exemple.* Simulons la loi a posteriori $\mathrm{Beta}(8,4)$ de 6.1 avec une proposition uniforme sur $[0,1]$ ($g=1$). Il faut $M\ge\max f$ : le maximum de la densité est atteint en $\theta=(8-1)/(8+4-2)=0{,}7$ et vaut $M\approx2{,}9351$, d'où une probabilité d'acceptation théorique $1/M=0{,}3407$. Sur 200 000 essais, le taux d'acceptation observé est 0,3428 (68 564 tirages conservés), la moyenne des tirages conservés 0,6665 (exacte : 0,6667) et leur écart-type 0,1305 (exact : 0,1307).


Le rejet marche, mais gaspille : environ deux tirages sur trois sont jetés. En dimension 10 ou 100, la constante $M$ devient astronomique et l'acceptation tombe à presque zéro : c'est la **malédiction de la dimension** (ce que le volume de la boule laissait deviner). Il faut une autre idée : celle des chaînes de Markov, en 6.3.

### 6.2.5 L'échantillonnage préférentiel (*importance sampling*)

Quand on cherche la probabilité d'un événement **rare**, simuler naïvement est désespérant : on attend longtemps un seul succès. Exemple : $P(Z>4)$ pour $Z\sim\mathcal N(0,1)$, qui vaut $3{,}17\times10^{-5}$ (environ une chance sur 31 600). Avec 10 000 tirages, on s'attend à $0{,}3$ succès : le plus souvent, l'estimateur naïf vaut 0.

L'idée de l'échantillonnage préférentiel : **tirer là où l'événement se produit**, puis **corriger** le biais par des poids. Pour estimer $\mathbb E_f[g(X)]=\int g(x)f(x)dx$, on tire $X_i\sim h$ (une autre densité, qui charge davantage la zone d'intérêt) et on écrit
$$\int g(x)f(x)dx=\int g(x)\frac{f(x)}{h(x)}h(x)dx=\mathbb E_h\!\left[g(X)\,w(X)\right],\qquad w=\frac fh .$$
L'estimateur $\hat\theta=\frac1n\sum g(X_i)w(X_i)$ est donc **sans biais** (même démonstration : un changement de variable dans l'intégrale), pourvu que $h>0$ partout où $gf\ne0$. Pour $P(Z>4)$, on choisit $h=\mathcal N(4,1)$ : la moitié des tirages dépasse 4.


L'écart-type de l'estimateur naïf (5,8 $\times10^{-5}$) est plus grand que la quantité à estimer elle-même ($3{,}2\times10^{-5}$), et 69 % des estimations naïves valent exactement 0. Celui de l'échantillonnage préférentiel (6,8 $\times10^{-7}$) est 86 fois plus petit, ce qui équivaut à $86^2\approx7\,400$ fois plus de tirages pour la même précision. Quand on connaît la forme de la zone d'intérêt, c'est un gain colossal.

> ⚠️ **Choisir $h$ avec soin.** Une proposition mal placée peut être aussi mauvaise que la méthode naïve : trop loin de la zone d'intérêt, quelques tirages portent presque tout le poids et l'estimation devient instable. On mesure cette dégénérescence par la **taille d'échantillon effective** (*effective sample size*), calculée sur les contributions $c_i=g(X_i)\,w(X_i)$ :
> $$\mathrm{ESS}=\frac{\left(\sum_i c_i\right)^2}{\sum_i c_i^{2}},$$
> qui vaut $n$ si toutes les contributions sont égales et 1 si un seul tirage porte tout. Nous retrouverons cette idée d'ESS en 6.4. Faisons varier le centre $c$ de la proposition $h=\mathcal N(c,1)$ (le cas $c=0$ est la méthode naïve), avec 300 répétitions de 10 000 tirages :

| centre $c$ | part de tirages $>4$ | ESS moyenne | écart-type de l'estimateur | erreur relative |
|---:|---:|---:|---:|---:|
| 0 | 0,0000 | 0,3 | $6{,}16\times10^{-5}$ | 1,946 |
| 2 | 0,0228 | 187,1 | $2{,}34\times10^{-6}$ | 0,074 |
| 3 | 0,1584 | 965,9 | $1{,}04\times10^{-6}$ | 0,033 |
| **4** | 0,4996 | **1 814,0** | $6{,}81\times10^{-7}$ | **0,022** |
| 5 | 0,8413 | 1 235,0 | $8{,}03\times10^{-7}$ | 0,025 |
| 6 | 0,9771 | 304,9 | $1{,}68\times10^{-6}$ | 0,053 |
| 8 | 1,0000 | 3,2 | $3{,}53\times10^{-5}$ | 1,114 |


Le tableau raconte toute l'histoire. Avec $c=0$ (méthode naïve), pratiquement aucun tirage ne dépasse 4 : l'ESS est inférieure à 1 et l'erreur relative est de l'ordre de 200 %. En se rapprochant de 4, la part de tirages utiles croît, l'ESS atteint **son maximum autour de $c=4$** (environ 1 800 tirages « effectifs » sur 10 000) et l'erreur relative tombe à environ 2 %. Mais si l'on place la proposition **trop loin** ($c=8$), tous les tirages dépassent 4 et pourtant l'estimateur redevient mauvais : les poids $f/h$ sont minuscules pour presque tous les tirages et énormes pour de rares valeurs proches de 4. L'ESS s'effondre (environ 3), et l'erreur relative remonte à plus de 100 %. **Centrer la proposition juste sur la zone d'intérêt**, ni trop près ni trop loin, c'est tout l'art.

### 6.2.6 Réduire la variance : faire mieux avec les mêmes tirages

L'erreur est $\sigma/\sqrt n$ ; plutôt que de multiplier $n$, on peut **réduire $\sigma$**. Prenons une intégrale que l'on sait calculer autrement (pour avoir une référence) : $I=\int_0^1e^{-x^2}dx\approx0{,}746824$. Estimateur naïf : $f(U)=e^{-U^2}$ avec $U\sim\mathcal U(0,1)$.

**Variables antithétiques.** À chaque tirage $U$, on utilise aussi $1-U$ (qui suit aussi la loi uniforme) et on moyenne les deux : $\frac12[f(U)+f(1-U)]$.

> 📐 **Pourquoi ça marche.** Si $\rho=\mathrm{Corr}(f(U),f(1-U))$, la variance de la moyenne de ces deux valeurs est $\frac{\sigma^2}{2}(1+\rho)$ (volume I, section 2.3). Pour une fonction **monotone** (ici décroissante), $f(U)$ et $f(1-U)$ varient en sens contraire : $\rho<0$, et la variance diminue (elle serait même nulle si $\rho=-1$). Mais attention : on a utilisé **deux** évaluations de $f$ ; la comparaison honnête se fait à nombre d'évaluations égal.

**Variable de contrôle.** On connaît l'espérance exacte d'une variable $h(U)$ corrélée à $f(U)$ (ici $h(U)=U$, d'espérance $1/2$). On corrige l'estimateur :
$$\hat I_c=\frac1n\sum\Big[f(U_i)-c\,\big(h(U_i)-\mathbb E[h]\big)\Big].$$
Il reste sans biais pour tout $c$, et sa variance est minimale pour $c^{*}=\mathrm{Cov}(f,h)/\mathrm{Var}(h)$, où elle vaut $(1-\rho^2)\,\sigma^2/n$ avec $\rho=\mathrm{Corr}(f(U),h(U))$ : plus $h$ ressemble à $f$, plus on gagne.

**Stratification.** On découpe $[0,1]$ en $K$ tranches égales et on tire le même nombre de points dans chaque, ce qui garantit une couverture régulière de l'intervalle.

On compare les quatre méthodes à budget égal ($n=1\,000$ évaluations de $f$), en répétant 500 fois l'expérience :

| méthode | moyenne | biais | écart-type | gain de variance |
|---|---:|---:|---:|---:|
| naïf | 0,747244 | 0,000420 | 0,006639 | 1 |
| antithétique | 0,746821 | −0,000003 | 0,001311 | 25,6 |
| variable de contrôle | 0,746816 | −0,000008 | 0,000942 | 49,7 |
| stratifié | 0,746838 | 0,000013 | 0,000645 | 105,9 |


Les quatre méthodes sont (à peu près) **sans biais** (la colonne `biais` est de l'ordre de l'erreur de simulation : l'écart-type d'une moyenne de 500 répétitions est d'environ 0,0003), mais leurs écarts-types diffèrent : la colonne `gain de variance` dit combien de fois moins de tirages on aurait pu faire pour la même précision. Les antithétiques gagnent un facteur 26 (écart-type divisé par 5), la variable de contrôle un facteur 50, et la stratification un facteur 106 (écart-type divisé par 10). Elles sont ici très efficaces parce que la fonction est lisse et monotone. Dans des problèmes réels à haute dimension, le gain est plus modeste, mais jamais négligeable : **un peu de réflexion avant de simuler vaut souvent mieux qu'un facteur 100 de calcul**.

### 6.2.7 Le bootstrap et le bootstrap bayésien : deux Monte-Carlo que vous connaissez déjà

Le bootstrap du volume I (section 3.3.5) *est* une méthode de Monte-Carlo : au lieu de simuler à partir d'une loi théorique, on simule à partir de la **loi empirique** (on rééchantillonne les données avec remise). Il existe une version « bayésienne » : plutôt que de tirer des entiers (nombre de fois que chaque observation apparaît), on tire des **poids continus** $w\sim\mathrm{Dirichlet}(1,\dots,1)$ et on calcule la statistique pondérée. Les deux donnent des résultats très proches ; le bootstrap bayésien a l'avantage d'une interprétation directe : c'est la loi *a posteriori* d'un modèle sans forme paramétrique, avec un a priori très diffus.

Exemple : la **médiane** du panier des acheteurs acquis par le canal Boutique (une statistique sans formule d'erreur simple). Sur 449 acheteurs, la médiane observée est 67,92 € ; le bootstrap classique donne un intervalle à 95 % de [64,62 ; 70,61] (écart-type 1,56), le bootstrap bayésien [64,66 ; 70,61] (écart-type 1,55), pratiquement le même.


> ✅ **À retenir (6.2).**
> - Une espérance se calcule en **moyennant des simulations** : $\hat\theta=\frac1n\sum g(X_i)$. Les probabilités, intégrales et moyennes a posteriori sont toutes des espérances.
> - L'erreur décroît en $\sigma/\sqrt n$ : **100 fois plus de tirages pour 10 fois moins d'erreur**. Cette vitesse ne dépend pas de la dimension, d'où l'intérêt de la méthode pour les problèmes complexes.
> - Pour simuler une loi donnée : **inversion** ($F^{-1}(U)$) si on connaît $F^{-1}$ ; **rejet** sinon (efficace seulement en petite dimension).
> - L'**échantillonnage préférentiel** estime les événements rares en tirant là où ils se produisent et en corrigeant par des poids $f/h$ ; l'**ESS** détecte les poids dégénérés.
> - Les **variables antithétiques, de contrôle et la stratification** réduisent la variance à nombre de tirages égal.
> - Le **bootstrap** est un Monte-Carlo sur la loi empirique ; sa version bayésienne tire des poids de Dirichlet.
> - Quand ni l'inversion ni le rejet ne marchent (cas général d'une loi a posteriori), il reste les **chaînes de Markov** : section 6.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.2, exercices 6.5 à 6.7.


## 6.3 MCMC : Metropolis-Hastings et échantillonnage de Gibbs

> 💡 **Intuition.** Imaginez un randonneur aveugle lâché dans une chaîne de montagnes, avec pour consigne de **passer plus de temps dans les hautes vallées que dans les basses**, exactement en proportion de l'altitude. Il ne voit pas la carte : il peut seulement, à chaque pas, tâter un point voisin et comparer son altitude à celle de sa position. Règle : *si le point voisin est plus haut, j'y vais toujours ; s'il est plus bas, j'y vais avec une probabilité égale au rapport des altitudes.* Au bout de très longtemps, la proportion du temps passé en chaque lieu est proportionnelle à l'altitude. C'est **Metropolis**. L'« altitude » est la densité a posteriori ; la proportion du temps passé, c'est l'échantillon qu'on cherche.

### 6.3.1 Pourquoi les chaînes de Markov ?

Considérons la régression logistique de `rachat_12m` sur l'offre, le canal et l'âge (nous la ferons en 6.3.5). L'a posteriori est
$$p(\beta\mid y)\;\propto\;\underbrace{\prod_{i}\sigma(x_i^\top\beta)^{y_i}\bigl(1-\sigma(x_i^\top\beta)\bigr)^{1-y_i}}_{\text{vraisemblance}}\;\times\;\underbrace{\prod_j\mathcal N(\beta_j;\,0,\,s^2)}_{\text{a priori}}.$$
Ce n'est **aucune loi connue** : pas de conjugaison, pas de fonction de répartition inversible, et le rejet de 6.2.4 serait inapplicable en dimension 5. Pire : nous ne connaissons même pas la **constante de normalisation** $p(y)$, qui est une intégrale en dimension 5. Mais nous savons calculer, pour tout $\beta$, la quantité **non normalisée** ci-dessus. Les méthodes MCMC (*Markov chain Monte Carlo*) n'ont besoin que de cela : elles ne s'intéressent qu'aux **rapports** $p(\beta')/p(\beta)$, dans lesquels la constante s'annule.

L'idée générale : au lieu de tirer des points *indépendants*, construire une **chaîne de Markov** $\theta^{(1)},\theta^{(2)},\dots$ (chaque point dépend seulement du précédent, volume I, section 2.6.2), conçue pour que sa **loi stationnaire** soit exactement la loi cible. Après un temps de chauffe, les points de la chaîne sont (corrélés) des tirages de la cible.

### 6.3.2 Les chaînes de Markov : loi stationnaire et réversibilité

Rappel (volume I, 2.6.2) : une chaîne à états finis de matrice de transition $P$ ($P_{ij}=P(\text{aller de }i\text{ à }j)$) admet une **loi stationnaire** $\pi$ si $\pi P=\pi$ : si la chaîne a la loi $\pi$ à un instant, elle l'a encore à l'instant suivant. Sous de bonnes conditions (la chaîne peut aller de tout état à tout état, et n'est pas périodique : on dit qu'elle est *ergodique*), la chaîne **converge** vers $\pi$ quelle que soit sa position de départ, et la proportion du temps passé dans chaque état tend vers $\pi$ (théorème ergodique, admis).

Comment fabriquer une chaîne dont la loi stationnaire est une loi $\pi$ donnée ? Par une condition suffisante simple.

> 📐 **Théorème (réversibilité ⇒ stationnarité).** Si une matrice de transition $P$ vérifie l'**équation de bilan détaillé**
> $$\pi_i\,P_{ij}=\pi_j\,P_{ji}\qquad\text{pour tous }i,j,$$
> alors $\pi P=\pi$.
>
> *Démonstration.* La $j$-ième composante de $\pi P$ est $\sum_i\pi_iP_{ij}=\sum_i\pi_jP_{ji}=\pi_j\sum_iP_{ji}=\pi_j$, car chaque ligne de $P$ somme à 1. $\square$

L'équation dit : « *en régime stationnaire, le flux de $i$ vers $j$ égale le flux de $j$ vers $i$* ». Si les flux sont équilibrés pour chaque paire d'états, la population de chaque état est stable.

**Exemple à la main : trois canaux.** La gérante choisit chaque semaine un canal à mettre en avant parmi 1 = Boutique, 2 = Site, 3 = Réseaux, et elle voudrait que ses choix, sur le long terme, suivent des poids $(2,5,3)$, c'est-à-dire la loi $\pi=(0{,}2;\,0{,}5;\,0{,}3)$. Elle applique la règle de Metropolis : **proposer** l'un des deux autres canaux au hasard (probabilité $\tfrac12$ chacun), puis **accepter** avec la probabilité $\alpha=\min\bigl(1,\ \pi_j/\pi_i\bigr)$, et sinon rester sur place. Construisons la matrice :

- depuis 1 (poids 2) : vers 2, $\tfrac12\min(1,5/2)=\tfrac12$ ; vers 3, $\tfrac12\min(1,3/2)=\tfrac12$ ; rester : $0$ ;
- depuis 2 (poids 5) : vers 1, $\tfrac12\cdot\tfrac25=0{,}2$ ; vers 3, $\tfrac12\cdot\tfrac35=0{,}3$ ; rester : $0{,}5$ ;
- depuis 3 (poids 3) : vers 1, $\tfrac12\cdot\tfrac23=\tfrac13$ ; vers 2, $\tfrac12\cdot1=0{,}5$ ; rester : $\tfrac16$.

Vérifions le bilan détaillé à la main : $\pi_1P_{12}=0{,}2\times0{,}5=0{,}1=\pi_2P_{21}=0{,}5\times0{,}2$ ✓ ; $\pi_1P_{13}=0{,}2\times0{,}5=0{,}1=\pi_3P_{31}=0{,}3\times\tfrac13$ ✓ ; $\pi_2P_{23}=0{,}5\times0{,}3=0{,}15=\pi_3P_{32}=0{,}3\times0{,}5$ ✓. Un calcul numérique confirme tout cela : l'écart maximal au bilan détaillé est nul aux arrondis près (de l'ordre de $10^{-17}$) ; la loi stationnaire, trouvée par algèbre linéaire (volume I, section 1.1.3 : vecteur propre associé à la valeur propre 1), est bien $(0{,}2;\,0{,}5;\,0{,}3)$ ; et une simulation de 100 000 pas de la chaîne, partie du canal 1, visite les canaux avec les fréquences $(0{,}2009;\,0{,}5005;\,0{,}2986)$.


Les trois vérifications (vecteur propre, bilan détaillé, simulation) s'accordent : la chaîne visite chaque canal en proportion de son poids. Remarquez que nous n'avons utilisé que les **rapports** de poids $\pi_j/\pi_i$ : le calcul aurait été le même avec des poids $(20,50,30)$. C'est exactement ce qui nous servira quand la constante de normalisation sera inconnue.

### 6.3.3 L'algorithme de Metropolis-Hastings

Généralisons à une loi continue de densité cible $\pi(\theta)$ (connue à une constante près), en dimension quelconque.

> **Metropolis-Hastings.** On se donne une loi de **proposition** $q(\theta'\mid\theta)$ dont on sait simuler. Partant de $\theta^{(t)}$ :
> 1. tirer une **proposition** $\theta'\sim q(\cdot\mid\theta^{(t)})$ ;
> 2. calculer la probabilité d'acceptation $$\alpha(\theta,\theta')=\min\left(1,\ \frac{\pi(\theta')\,q(\theta\mid\theta')}{\pi(\theta)\,q(\theta'\mid\theta)}\right);$$
> 3. tirer $U\sim\mathcal U(0,1)$ ; si $U\le\alpha$ : $\theta^{(t+1)}=\theta'$ (on **accepte**), sinon $\theta^{(t+1)}=\theta^{(t)}$ (on **reste**, et on **recompte** la valeur).

Quand la proposition est **symétrique** ($q(\theta'\mid\theta)=q(\theta\mid\theta')$, par exemple $\theta'=\theta+\text{bruit gaussien}$, la « marche aléatoire »), le rapport des $q$ disparaît et on retrouve la règle de Metropolis de l'exemple précédent : $\alpha=\min(1,\pi(\theta')/\pi(\theta))$.

> 📐 **Théorème.** La chaîne de Metropolis-Hastings vérifie le bilan détaillé par rapport à $\pi$ ; donc $\pi$ est sa loi stationnaire.
>
> *Démonstration.* Pour $\theta\neq\theta'$, la densité de transition est $K(\theta,\theta')=q(\theta'\mid\theta)\,\alpha(\theta,\theta')$. Alors
> $$\pi(\theta)K(\theta,\theta')=\pi(\theta)\,q(\theta'\mid\theta)\,\min\!\left(1,\frac{\pi(\theta')q(\theta\mid\theta')}{\pi(\theta)q(\theta'\mid\theta)}\right)=\min\bigl(\pi(\theta)q(\theta'\mid\theta),\ \pi(\theta')q(\theta\mid\theta')\bigr).$$
> L'expression de droite est **symétrique** en $(\theta,\theta')$ : elle est égale à $\pi(\theta')K(\theta',\theta)$. C'est le bilan détaillé. Il reste à vérifier la stationnarité : pour tout ensemble $A$, $\int\pi(\theta)K(\theta,A)\,d\theta=\int_A\left[\int\pi(\theta)K(\theta,\theta')d\theta\right]d\theta'+(\text{mass du rejet})$. Grâce au bilan détaillé, le crochet vaut $\pi(\theta')\int K(\theta',\theta)d\theta=\pi(\theta')\bigl(1-r(\theta')\bigr)$, où $r(\theta')$ est la probabilité de rejet en $\theta'$ ; la part de la chaîne qui reste sur place (probabilité $r(\theta)$ en chaque $\theta$) apporte exactement $\int_A\pi(\theta')r(\theta')d\theta'$. La somme redonne $\int_A\pi$. $\square$
>
> Pour que la chaîne **converge** effectivement vers $\pi$ depuis n'importe quel point de départ, il faut en plus qu'elle soit irréductible (elle peut atteindre toute région de probabilité positive) et apériodique ; c'est le cas dès que la proposition gaussienne de la marche aléatoire est utilisée sur un espace continu (théorème admis, voir les références en fin de volume).

**La constante de normalisation disparaît.** Dans $\alpha$, $\pi$ n'intervient que par le rapport $\pi(\theta')/\pi(\theta)$ : on peut remplacer $\pi$ par n'importe quelle fonction proportionnelle (vraisemblance × a priori, sans la constante $p(y)$). Pour éviter les dépassements numériques, on travaille toujours avec les **logarithmes** : on accepte si $\log U<\log\pi(\theta')-\log\pi(\theta)$.

**Premier test : retrouver la loi $\mathrm{Beta}(8,4)$ de 6.1.** Nous connaissons la bonne réponse (moyenne $2/3$, écart-type $0{,}1307$) : nous pouvons donc juger l'algorithme. Voici l'algorithme en dimension 1, tel qu'on l'écrit en pratique (la densité cible n'intervient que par son logarithme, non normalisé) :

```python
from scipy import stats

def metropolis_1d(logp, x0, n, pas, rng):
    """Marche aléatoire de Metropolis en dimension 1 : proposition x' = x + pas * N(0, 1)."""
    x, lp = x0, logp(x0)
    chaine = np.empty(n)
    acceptes = 0
    for i in range(n):
        prop = x + pas * rng.standard_normal()
        lpp = logp(prop)
        if np.log(rng.random()) < lpp - lp:               # critère d'acceptation, en logarithmes
            x, lp = prop, lpp
            acceptes += 1
        chaine[i] = x                                     # on recompte la valeur même si on a refusé
    return chaine, acceptes / n
```


Lancée 20 000 pas depuis $x_0=0{,}5$ avec un pas de 0,2 (taux d'acceptation : 0,589) et après avoir jeté les 1 000 premiers points, la chaîne reproduit la loi cible : moyenne 0,6674 (exacte 0,6667), écart-type 0,1334 (exact 0,1307), quantiles à 5 %, 50 % et 95 % de 0,4321 ; 0,6779 ; 0,8656 (exacts : 0,4356 ; 0,6762 ; 0,8649). Tout coïncide à environ le centième. (Le test de Kolmogorov-Smirnov fournit une statistique faible ; sa p-valeur serait trompeuse ici, car les points d'une chaîne sont **corrélés** : le test suppose des observations indépendantes.)  Pour comprendre le rôle du **pas**, comparons-en plusieurs.

### 6.3.4 Régler l'algorithme : le pas de la marche aléatoire

Le seul réglage de la marche aléatoire est le **pas** (l'écart-type de la proposition). Il faut le choisir avec soin :

- **pas trop petit** : presque toutes les propositions sont acceptées, mais elles sont minuscules ; la chaîne rampe et met un temps énorme à explorer la loi ;
- **pas trop grand** : presque toutes les propositions tombent dans des zones de faible densité et sont rejetées ; la chaîne reste bloquée sur place ;
- **pas intermédiaire** : un bon compromis.

Pour *mesurer* la qualité de l'exploration, on utilise la **taille d'échantillon effective** (ESS), que nous reverrons en 6.4 : $n$ points **corrélés** d'une chaîne valent seulement $\mathrm{ESS}=\dfrac{n}{1+2\sum_{k\ge1}\rho_k}$ points indépendants, où $\rho_k$ est l'autocorrélation de la chaîne au décalage $k$ (volume II, chapitre 4, pour la notion d'autocorrélation). (la somme s'arrête à la première autocorrélation négative). Sur 20 000 pas de la loi $\mathrm{Beta}(8,4)$, on obtient :

| pas | taux d'acceptation | ESS | ESS / $n$ | autocorr. au décalage 1 | moyenne |
|---:|---:|---:|---:|---:|---:|
| 0,01 | 0,970 | 25 | 0,001 | 0,997 | 0,6900 |
| 0,05 | 0,876 | 444 | 0,023 | 0,944 | 0,6773 |
| **0,20** | 0,594 | **3 731** | 0,196 | 0,675 | 0,6662 |
| **0,50** | 0,307 | **3 593** | 0,189 | 0,686 | 0,6649 |
| 2,00 | 0,083 | 870 | 0,046 | 0,909 | 0,6612 |
| 10,00 | 0,017 | 217 | 0,011 | 0,978 | 0,6751 |


On lit : avec un pas de 0,01, le taux d'acceptation est proche de 1 mais l'ESS est minuscule (la chaîne ne bouge presque pas) ; avec un pas de 10, le taux d'acceptation s'effondre (1,7 % des propositions seulement tombent dans une zone de densité raisonnable) et l'ESS est de 217, dix-sept fois plus faible qu'à l'optimum ; l'optimum est autour d'un pas de 0,2 à 0,5 (ESS d'environ 3 600 à 3 700, soit 19 % de $n$), avec un taux d'acceptation de 30 à 60 %. Noter que **le taux d'acceptation seul ne suffit pas à juger un réglage** : il vaut 97 % avec le pas de 0,01 (mauvais) et 59 % avec le pas de 0,2 (bon). L'ESS est le vrai juge. Voici les traces correspondantes (pour les pas 0,01, 0,2 et 10).


![Trois traces de la marche aléatoire de Metropolis pour la loi Beta(8, 4), avec trois pas différents. Pas trop petit : la chaîne rampe lentement. Bon pas : la chaîne explore toute la zone de forte densité. Pas trop grand : la chaîne reste longtemps bloquée sur des paliers.](figures/ch06-mh-pas.png)

> 💡 **Lire une trace.** Une bonne trace ressemble à une **« chenille velue »** : un nuage de points qui oscille de façon irrégulière autour d'une valeur centrale, sans tendance. Une trace **rampante** (trop petit) ressemble à une courbe lisse qui dérive lentement ; une trace **à paliers** (trop grand) a de longs segments plats (la chaîne reste bloquée sur ses refus). Nous verrons en 6.4 comment objectiver cette impression.

> 📐 **Règles pratiques.** En dimension 1, un taux d'acceptation d'environ 44 % est optimal ; en dimension élevée, des résultats théoriques (Roberts, Gelman et Gilks, 1997) donnent un taux optimal d'environ **23 %**, obtenu avec une proposition gaussienne de covariance $\dfrac{2{,}38^2}{d}\,\hat\Sigma$, où $d$ est la dimension et $\hat\Sigma$ une estimation de la covariance de la loi cible. Nous utiliserons cette règle pour la régression logistique.

### 6.3.5 Un exemple complet : la régression logistique bayésienne du rachat

Passons au problème réel. Nous modélisons le rachat dans les 12 mois par
$$y_i\sim\mathrm{Bernoulli}\bigl(\sigma(\eta_i)\bigr),\qquad \eta_i=\beta_0+\beta_1\,\text{offre}_i+\beta_2\,\text{Réseaux}_i+\beta_3\,\text{Site}_i+\beta_4\,\text{âge}_i,$$
où $\sigma(u)=1/(1+e^{-u})$, la Boutique est le canal de référence et l'âge est **standardisé** (centré, divisé par son écart-type : une unité = un écart-type). (La régression logistique est étudiée au chapitre 2, section 2.2 ; ici, on s'intéresse à la façon de **l'estimer** par une méthode bayésienne.) A priori : $\beta_j\sim\mathcal N(0,\,2{,}5^2)$ pour tous les coefficients, un a priori « faiblement informatif » (6.1.6) : il écarte les rapports de cotes extrêmes ($e^{\pm 5}$) sans trop contraindre.


```python
def log_post(beta):
    eta = Xm @ beta
    log_vrais = np.sum(y * eta - np.logaddexp(0, eta))     # somme de y*eta - log(1 + exp(eta))
    log_prior = -0.5 * np.sum(beta**2) / 2.5**2            # a priori normal centré, écart-type 2,5
    return log_vrais + log_prior
```


Le **log-posterior** tient en quelques lignes : c'est toute la modélisation. (Le tableau `X` contient une colonne de constantes, l'offre, l'âge standardisé et les indicatrices des canaux Réseaux et Site ; il y a 2 000 clients, dont 50,9 % ont racheté.) Pour situer le résultat, le point de repère est l'estimation du maximum de vraisemblance, fournie par `statsmodels`. Il reste à fabriquer la chaîne. Nous prenons une marche aléatoire à **proposition gaussienne multivariée** de covariance $\frac{2{,}38^2}{d}\hat\Sigma$, où $\hat\Sigma$ est la covariance estimée des coefficients par le maximum de vraisemblance (l'inverse de la hessienne, que statsmodels fournit) : c'est un bon « premier dessin » de la forme de l'a posteriori. Pour pouvoir diagnostiquer la convergence en 6.4, nous lançons **quatre chaînes** de points de départ dispersés.


Les taux d'acceptation des quatre chaînes (0,284 ; 0,297 ; 0,293 ; 0,274) sont proches de la valeur théorique. Les 1 000 premières itérations de chaque chaîne (la « chauffe ») sont écartées, ce qui laisse $4\times5\,000=20\,000$ tirages. Voici le résumé a posteriori, à côté du maximum de vraisemblance :

| coefficient | EMV | écart-type EMV | moyenne a posteriori | écart-type a posteriori | crédibilité 95 % | ESS |
|---|---:|---:|---:|---:|---|---:|
| constante | 0,034 | 0,100 | 0,033 | 0,098 | [−0,162 ; 0,227] | 1 281 |
| offre | 0,493 | 0,091 | 0,493 | 0,089 | [0,316 ; 0,663] | 1 276 |
| âge (standardisé) | −0,163 | 0,046 | −0,163 | 0,045 | [−0,256 ; −0,076] | 1 114 |
| Réseaux | −0,463 | 0,116 | −0,459 | 0,113 | [−0,681 ; −0,232] | 1 158 |
| Site | −0,168 | 0,120 | −0,163 | 0,118 | [−0,393 ; 0,073] | 1 205 |


Les moyennes a posteriori sont **presque identiques** aux estimations du maximum de vraisemblance, et les écarts-types a posteriori sont presque ceux de l'EMV (c'est le théorème de Bernstein-von Mises du 6.1.6 à l'œuvre : avec 2 000 observations et un a priori large, a posteriori et vraisemblance se confondent). Les ESS sont d'environ 1 100 à 1 300 sur 20 000 tirages (l'ESS ne représente qu'environ 6 % du nombre de tirages : les points d'une marche aléatoire sont fortement corrélés). C'est suffisant : l'erreur de simulation sur une moyenne a posteriori vaut $\sigma/\sqrt{\mathrm{ESS}}\approx0{,}089/\sqrt{1\,276}\approx0{,}0025$ pour le coefficient de l'offre, soit moins de 3 % de son incertitude a posteriori. (Nous reviendrons en 6.4 sur ce qui rend un ESS « suffisant ».)

Le point clé de l'approche bayésienne est que nous **possédons maintenant des tirages de la loi jointe a posteriori** des cinq coefficients : tout ce que l'on veut calculer devient une moyenne sur ces tirages, sans formule. Par exemple, le **rapport de cotes** de l'offre (médiane 1,639, intervalle de crédibilité à 95 % [1,372 ; 1,940]), et surtout l'**effet de l'offre sur la probabilité de rachat** pour un client de référence (acquis en Boutique, d'âge moyen) : +0,120, intervalle à 95 % [+0,078 ; +0,161], à comparer à la différence brute des fréquences de 6.1.4 (+0,122). Il suffit pour cela de transformer chaque tirage $(\beta_0,\beta_1)$ en $\sigma(\beta_0+\beta_1)-\sigma(\beta_0)$ et de résumer les 20 000 valeurs obtenues.


Quatre phrases que l'on peut maintenant écrire, avec leur chiffre : le rapport de cotes de l'offre est de l'ordre de 1,6 ; la probabilité qu'il dépasse 1 est quasi certaine ; la probabilité qu'il dépasse 1,5 est de 83,6 % ; et l'effet de l'offre sur la probabilité de rachat d'un client moyen est de l'ordre de 12 points, en cohérence avec l'estimation brute de 6.1.4 (l'offre ayant été attribuée au hasard, ajuster sur le canal et l'âge ne change presque rien, comme on l'attend). Pour finir, un graphique : pour chaque coefficient, l'intervalle de crédibilité et l'intervalle de confiance du maximum de vraisemblance.


![Pour chacun des cinq coefficients de la régression logistique du rachat, l'intervalle de crédibilité à 95 % obtenu par MCMC (bleu) et l'intervalle de confiance à 95 % du maximum de vraisemblance (orange). Les deux approches coïncident presque exactement.](figures/ch06-logit-bayes.png)

> 🧪 **Que valent ces estimations ? Réponse de la simulation.** Les données étant simulées, nous connaissons les vrais paramètres du générateur : un effet de l'offre de **+0,55** sur le logit, un avantage de la Boutique de +0,3 par rapport aux deux autres canaux (donc −0,3 pour Réseaux et pour le Site), un effet de l'âge de −0,015 par an. Notre estimation de l'offre (0,49) est **inférieure à 0,55** mais compatible avec elle (l'intervalle de crédibilité est d'environ ±0,17). L'effet de l'âge (−0,163 par écart-type, soit $-0{,}163/10{,}5\approx-0{,}0155$ par an) retrouve le −0,015 programmé, et les intervalles des canaux contiennent les valeurs programmées ($-0{,}3$ pour Réseaux comme pour le Site). Mais il y a une raison **systématique**, et pas seulement le hasard, pour laquelle l'effet de l'offre est un peu sous-estimé : le générateur utilise deux facteurs latents (goût pour les produits, sensibilité au service) qui influencent aussi le rachat, et que notre modèle **n'observe pas**. Omettre des variables explicatives *atténue* les coefficients d'une régression logistique, même quand ces variables sont indépendantes de l'offre (c'est la « non-collapsibilité » du rapport de cotes). Vérifions-le sur un très grand échantillon simulé avec la même formule (400 000 observations, vrai coefficient 0,55) : sans les facteurs latents dans le modèle, le coefficient estimé de l'offre vaut 0,499 ; avec eux, 0,548.


Sans les facteurs latents, le coefficient attendu est donc d'environ 0,50 : notre estimation de 0,49 est exactement ce que la théorie prédit. Voilà un bel exemple de modèle bien estimé mais **mal spécifié** : l'estimation est correcte pour la question posée au modèle, qui n'est pas exactement celle du générateur.

### 6.3.6 L'échantillonnage de Gibbs

Quand le paramètre a plusieurs composantes, $\theta=(\theta_1,\dots,\theta_d)$, il est parfois facile de simuler chaque composante **sachant toutes les autres** (on dit : selon sa **loi conditionnelle complète**), même si la loi jointe est compliquée. L'échantillonneur de Gibbs en fait un algorithme : à chaque itération, on met à jour les composantes l'une après l'autre.

> **Gibbs.** Partant de $\theta^{(t)}$ : tirer $\theta_1^{(t+1)}\sim p(\theta_1\mid\theta_2^{(t)},\dots,\theta_d^{(t)})$, puis $\theta_2^{(t+1)}\sim p(\theta_2\mid\theta_1^{(t+1)},\theta_3^{(t)},\dots)$, et ainsi de suite jusqu'à $\theta_d$.

> 📐 **Gibbs est un cas particulier de Metropolis-Hastings, avec acceptation 1.** Mettons à jour la composante $j$ avec la proposition $q(\theta'\mid\theta)=\pi(\theta'_j\mid\theta_{-j})$ (les autres composantes inchangées). Le rapport d'acceptation est
> $$\frac{\pi(\theta')q(\theta\mid\theta')}{\pi(\theta)q(\theta'\mid\theta)}=\frac{\pi(\theta'_j\mid\theta_{-j})\,\pi(\theta_{-j})\;\pi(\theta_j\mid\theta_{-j})}{\pi(\theta_j\mid\theta_{-j})\,\pi(\theta_{-j})\;\pi(\theta'_j\mid\theta_{-j})}=1,$$
> puisque $\pi(\theta)=\pi(\theta_j\mid\theta_{-j})\pi(\theta_{-j})$. La proposition est donc **toujours acceptée**, et le théorème de 6.3.3 garantit que $\pi$ est stationnaire.

**Exemple 1 : la loi normale bivariée.** Simulons $(X,Y)$ de corrélation $\rho$ (lois marginales $\mathcal N(0,1)$). Les lois conditionnelles sont connues : $X\mid Y=y\sim\mathcal N(\rho y,\,1-\rho^2)$, et symétriquement. Gibbs alterne les deux. C'est aussi l'occasion de voir son **point faible** : si les composantes sont fortement corrélées, chaque pas ne peut bouger que dans la direction d'un axe, et la chaîne progresse en zigzag minuscule.

```python
def gibbs_binormale(rho, n, rng):
    x = y = 0.0
    s = np.sqrt(1 - rho**2)
    out = np.empty((n, 2))
    for i in range(n):
        x = rng.normal(rho * y, s)                            # X | Y
        y = rng.normal(rho * x, s)                            # Y | X
        out[i] = (x, y)
    return out
```


Sur 20 000 itérations (1 000 écartées), les résultats sont :

| $\rho$ vrai | corrélation estimée | écart-type de $X$ | autocorr. au décalage 1 | ESS de $X$ (sur 19 000) |
|---:|---:|---:|---:|---:|
| 0,00 | −0,003 | 0,997 | −0,006 | 19 000 |
| 0,50 | 0,493 | 1,001 | 0,246 | 11 638 |
| 0,90 | 0,902 | 1,003 | 0,816 | 1 966 |
| 0,99 | 0,990 | 1,011 | 0,980 | 177 |

Les corrélations estimées retrouvent les $\rho$ et les écarts-types valent 1, comme prévu. Mais regardez l'ESS : avec $\rho=0$ la chaîne est indépendante (ESS proche de $n$), tandis qu'avec $\rho=0{,}9$ elle tombe à environ 2 000 et qu'avec $\rho=0{,}99$ elle s'effondre à moins de 200 tirages efficaces sur 19 000 (1 % du total) : **la corrélation entre composantes ruine Gibbs**. C'est la raison pour laquelle on **reparamétrise** (on décorrèle les paramètres) ou on utilise des méthodes plus sophistiquées comme l'HMC (6.3.7).

**Exemple 2 : une loi normale à moyenne et variance inconnues.** En 6.1.8, nous avons fait l'hypothèse (de confort) que l'écart-type $\sigma$ du logarithme du panier était *connu*. Levons-la. Les données : les logarithmes des paniers des 449 acheteurs acquis par le canal Boutique. Le modèle : $y_i\sim\mathcal N(\mu,\sigma^2)$, avec les a priori **indépendants** $\mu\sim\mathcal N(4{,}\,10^2)$ (très large) et la **précision** $\tau=1/\sigma^2\sim\mathrm{Gamma}(a_0=0{,}01,\ b_0=0{,}01)$ (très diffuse). Les lois conditionnelles complètes sont connues :

- $\mu\mid\tau,y\sim\mathcal N(\mu_n,v_n)$ avec $\dfrac1{v_n}=\dfrac1{\tau_0^2}+n\tau$ et $\mu_n=v_n\left(\dfrac{\mu_0}{\tau_0^2}+\tau\,n\bar y\right)$ (c'est la formule normale-normale de 6.1.8, avec $\sigma^2=1/\tau$) ;
- $\tau\mid\mu,y\sim\mathrm{Gamma}\!\left(a_0+\dfrac n2,\ b_0+\dfrac12\sum_i(y_i-\mu)^2\right)$ (même calcul que gamma-Poisson : multiplier les formes en $\tau^{\cdot}e^{-\cdot\tau}$).

Il n'y a **pas de formule fermée** pour la loi jointe de $(\mu,\sigma)$ avec ces a priori indépendants ; Gibbs nous en donne des tirages (on alterne le tirage de $\mu$ et celui de $\tau$ avec les deux formules ci-dessus, 11 000 fois, en partant volontairement d'un très mauvais point de départ $\mu=0$, $\tau=1$, et en écartant les 1 000 premiers points). Pour les 449 acheteurs (log-panier moyen 4,2183, écart-type empirique 0,3758), on obtient pour $\mu$ une moyenne a posteriori de 4,2182 (intervalle à 95 % [4,1838 ; 4,2529]) et pour $\sigma$ une moyenne de 0,3766 ([0,3525 ; 0,4023]).


Ces résultats concordent avec le calcul classique de Student (intervalle de $\mu$ : [4,1834 ; 4,2532]). Les ESS (10 000 pour $\mu$ et 9 629 pour $\sigma$, sur 10 000 tirages) sont très proches du nombre de tirages : ici $\mu$ et $\sigma$ sont presque indépendants a posteriori (corrélation proche de 0), donc Gibbs est quasi parfait. Et on peut enfin comparer à la vérité : le générateur combine un bruit de 0,35 et l'effet du facteur latent $F_1$ (écart-type 0,12), soit un écart-type total de $\sqrt{0{,}35^2+0{,}12^2}\approx0{,}370$, et un log-panier moyen de 4,22 pour la Boutique. L'a posteriori contient les deux.

### 6.3.7 En pratique : PyMC, Stan et l'HMC (non exécuté)

Dans les projets réels, on n'écrit pas ses échantillonneurs à la main. Les bibliothèques **PyMC** (Python) et **Stan** (langage dédié, accessible depuis Python, R, etc.) permettent de décrire le modèle et se chargent de l'inférence. Elles utilisent une méthode bien plus puissante que la marche aléatoire : le **Monte-Carlo hamiltonien** (HMC), et sa variante adaptative NUTS. L'idée : au lieu de proposer un pas au hasard, on **simule le mouvement d'une bille** qui roule sur la surface $-\log\pi(\theta)$ en utilisant le **gradient** de $\log\pi$ (volume I, section 1.2) ; elle se déplace loin, dans la bonne direction, et les propositions sont presque toujours acceptées. En grande dimension, l'écart d'efficacité avec la marche aléatoire est considérable.

> ⚠️ **Non exécuté.** PyMC et Stan **ne sont pas installés** dans l'environnement qui a servi à écrire ce livre. Les deux blocs de code ci-dessous sont donc **montrés sans avoir été exécutés** ; leur résultat attendu est celui de la section 6.3.5 (même modèle, mêmes a priori), mais nous n'avons pas pu le vérifier ici.

```python noexec
import pymc as pm

with pm.Model() as modele:
    beta = pm.Normal("beta", mu=0, sigma=2.5, shape=5)           # le même a priori que dans 6.3.5
    eta = pm.math.dot(Xm, beta)
    pm.Bernoulli("rachat", logit_p=eta, observed=y)
    trace = pm.sample(2000, tune=1000, chains=4, random_seed=1)  # NUTS par défaut
```

```text noexec
data { int<lower=0> n; matrix[n, 5] X; array[n] int<lower=0, upper=1> y; }
parameters { vector[5] beta; }
model {
  beta ~ normal(0, 2.5);
  y ~ bernoulli_logit(X * beta);
}
```

Comprendre ce que PyMC et Stan font à votre place, c'est comprendre ce chapitre : un log-posterior (que vous venez d'écrire en trois lignes), un algorithme qui explore sa surface, des diagnostics pour savoir s'il a bien exploré (6.4).

> ✅ **À retenir (6.3).**
> - Quand l'a posteriori n'est pas une loi connue, on le **simule avec une chaîne de Markov** dont la loi stationnaire est la cible. Seul le rapport $\pi(\theta')/\pi(\theta)$ est nécessaire : la constante de normalisation disparaît.
> - **Metropolis-Hastings** : proposer, calculer $\alpha=\min\!\bigl(1,\frac{\pi(\theta')q(\theta|\theta')}{\pi(\theta)q(\theta'|\theta)}\bigr)$, accepter ou rester. Il vérifie le **bilan détaillé**, donc $\pi$ est stationnaire.
> - Le **pas** de la marche aléatoire se règle : trop petit, on rampe ; trop grand, on reste bloqué ; en dimension élevée, viser 23 % d'acceptation avec une covariance $2{,}38^2\hat\Sigma/d$.
> - Les points d'une chaîne sont **corrélés** : on les juge par l'**ESS**, pas par leur nombre. On écarte une période de **chauffe**.
> - **Gibbs** met à jour une composante à la fois selon sa loi conditionnelle (acceptation 1) ; il souffre quand les composantes sont très corrélées.
> - Une fois les tirages obtenus, **tout** se calcule par moyenne : rapports de cotes, effets sur les probabilités, probabilités de seuils, prédictions.
> - PyMC et Stan (HMC/NUTS) font cela mieux et plus vite, mais ne dispensent pas de **vérifier** le résultat (6.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.3, exercices 6.8 et 6.9.


## 6.4 Vérification des modèles bayésiens

> 💡 **Intuition.** Un pilote ne décolle pas sans sa liste de contrôle : carburant, volets, instruments. Un analyste bayésien devrait faire de même, car **deux choses peuvent tourner mal**, et elles sont indépendantes : (1) *l'algorithme* peut avoir mal exploré la loi a posteriori (la chaîne n'a pas convergé), et (2) *le modèle* peut être faux (la loi a posteriori, même parfaitement calculée, répond à une question mal posée). Nous avons vu un exemple de la seconde en 6.1.8 : un modèle de Poisson aux intervalles trop étroits. Cette section donne les outils pour détecter l'une et l'autre.

Dans tout ce qui suit, un échantillon MCMC n'est jamais « bon par nature » : on **démontre** qu'il est bon, ou du moins qu'il ne manifeste aucun signe de mauvaise santé. Un diagnostic qui passe ne prouve pas la convergence (on ne peut jamais prouver qu'une chaîne a tout exploré), mais un diagnostic qui échoue prouve un problème.

### 6.4.1 L'algorithme a-t-il convergé ? Les diagnostics de convergence

Nous reprenons les quatre chaînes de la régression logistique de 6.3.5, lancées depuis des points de départ **dispersés**. Le premier diagnostic, et le plus parlant, est le dessin : la **trace** de chaque chaîne, et la distribution des valeurs prises, chaîne par chaîne.


![À gauche : la trace du coefficient de l'offre pour les quatre chaînes lancées de points de départ dispersés. La zone grise correspond à la chauffe, écartée. À droite : après la chauffe, les histogrammes des quatre chaînes se superposent.](figures/ch06-traces-quatre-chaines.png)

Ce qu'on cherche (et ce que l'on voit ici) : (i) **les quatre chaînes, parties de points très différents, se retrouvent dans la même zone** après quelques dizaines ou centaines d'itérations (c'est la « chauffe », en anglais *burn-in* ou *warm-up*, que l'on écarte) ; (ii) **elles se mélangent** : on ne distingue plus de quelle chaîne provient chaque point ; (iii) les histogrammes des quatre chaînes **coïncident**. Le dessin ne suffit pourtant pas : une trace peut sembler « stationnaire » à l'œil alors que la chaîne explore à peine un coin de la loi. On quantifie avec le **$\widehat R$ de Gelman-Rubin**.

> 📐 **L'idée du $\widehat R$ (R-chapeau).** Si $m$ chaînes de longueur $n$ ont convergé vers la même loi, la variabilité **entre** les chaînes ne doit pas dépasser la variabilité **à l'intérieur** de chaque chaîne. Soient $\bar\theta_j$ et $s_j^2$ la moyenne et la variance de la chaîne $j$, et $\bar\theta$ la moyenne générale. On calcule
> $$W=\frac1m\sum_j s_j^2\quad(\text{variance intra}),\qquad B=\frac{n}{m-1}\sum_j(\bar\theta_j-\bar\theta)^2\quad(\text{variance inter}),$$
> puis la meilleure estimation de la variance de la loi cible, $\widehat{\mathrm{var}}^+=\dfrac{n-1}{n}W+\dfrac Bn$, qui **surestime** cette variance tant que les chaînes n'ont pas convergé. On pose
> $$\widehat R=\sqrt{\frac{\widehat{\mathrm{var}}^+}{W}}\ \ge\ 1\ \text{(approximativement)}.$$
> Si les chaînes sont bien mélangées, $B\approx W$ et $\widehat R\approx1$ ; si elles sont chacune bloquées dans un coin différent, $B\gg W$ et $\widehat R\gg1$. On utilise aujourd'hui la version **« découpée »** (*split*-$\widehat R$) : on coupe chaque chaîne en deux moitiés avant de calculer, ce qui permet de détecter aussi une chaîne qui dérive lentement (ses deux moitiés ne se ressemblent pas). La recommandation actuelle est $\widehat R<1{,}01$ (l'ancien seuil de 1,1 est jugé trop laxiste).


Le tableau suivant donne le $\widehat R$ de chaque coefficient, avec et sans la chauffe, et l'ESS totale :

| coefficient | $\widehat R$ (chauffe incluse) | $\widehat R$ (chauffe écartée) | ESS |
|---|---:|---:|---:|
| constante | 1,0037 | 1,0010 | 1 281 |
| offre | 1,0064 | 1,0023 | 1 276 |
| âge | **1,0163** | 1,0009 | 1 114 |
| Réseaux | 1,0022 | 1,0037 | 1 158 |
| Site | 1,0043 | 1,0024 | 1 205 |

Deux enseignements. D'abord, **écarter la chauffe améliore le diagnostic** : en gardant les 1 000 premières itérations, le $\widehat R$ de l'âge est de 1,016 (au-dessus du seuil de 1,01) ; une fois la chauffe retirée, les cinq $\widehat R$ sont inférieurs à 1,004 : les quatre chaînes disent la même chose. (L'effet est modeste ici parce que la loi est presque gaussienne et que la chaîne s'y installe vite ; dans un modèle plus difficile, la chauffe peut faire la différence entre $\widehat R=1{,}5$ et $\widehat R=1{,}00$.) Ensuite, les **ESS** sont de l'ordre de 1 100 à 1 300 : pour estimer une moyenne ou un intervalle de crédibilité à 95 %, la règle usuelle est de viser au moins 400 à 1 000 ; nous sommes dans la fourchette. (Pour des quantiles extrêmes, il en faut davantage.)

> ⚠️ **Ce que l'ESS que nous calculons simplifie.** Nous additionnons les ESS de chaque chaîne. Les logiciels (Stan, ArviZ) utilisent une version qui combine les autocorrélations de toutes les chaînes et des transformations par rangs : elle est plus fiable pour les lois à queues lourdes. Pour nos besoins, l'ordre de grandeur est le même.

**Que se passe-t-il quand la convergence échoue ?** Un diagnostic n'a de valeur que si on a vu au moins une fois à quoi il ressemble quand il détecte quelque chose. Prenons une loi cible à **deux bosses**, mélange à parts égales de $\mathcal N(-4,1)$ et $\mathcal N(4,1)$ (moyenne exacte : 0), et lançons quatre chaînes de Metropolis de points de départ $-6,-2,2,6$, avec un pas petit (0,5) puis grand (6) :

| pas | moyennes des 4 chaînes | moyenne globale | $\widehat R$ | ESS |
|---:|---|---:|---:|---:|
| 0,5 | −4,08 ; 3,71 ; 4,06 ; 3,92 | 1,90 | **3,072** | 546 |
| 6,0 | −0,16 ; 0,16 ; −0,28 ; 0,17 | −0,03 | 1,002 | 1 430 |


Avec le petit pas, chaque chaîne reste **piégée dans sa bosse** : une chaîne est restée autour de $-4$, les trois autres autour de $+4$ ; la moyenne globale vaut 1,90 au lieu de 0 ; et le $\widehat R$ vaut 3,07, très loin de 1. Remarquez que l'ESS (546) a l'air honorable : elle est calculée chaîne par chaîne et ne voit pas qu'il manque une bosse. **Seule la comparaison entre chaînes (le $\widehat R$) donne l'alerte.** Fait plus grave : si on n'avait lancé *qu'une seule chaîne*, on aurait trouvé une moyenne proche de $-4$ ou de $+4$ avec un bel intervalle de crédibilité étroit, **tout à fait faux** : rien dans une chaîne unique ne signale qu'il manque une bosse. C'est la raison pour laquelle on lance toujours **plusieurs chaînes depuis des points de départ dispersés**. Avec le grand pas, les chaînes sautent d'une bosse à l'autre : $\widehat R=1{,}002$ et la moyenne globale (−0,03) est proche de 0.

> 💡 **Le diagnostic le plus important : plusieurs chaînes dispersées.** Presque tous les problèmes de convergence se voient en comparant des chaînes parties de points différents. **Ne jamais se contenter d'une seule chaîne.**

### 6.4.2 Le modèle est-il plausible ? Les vérifications prédictives a posteriori

Même si la chaîne est parfaite, le modèle peut être faux. Le test de bon sens est le suivant : **si le modèle était vrai, les données qu'il simulerait ressembleraient-elles aux données réelles ?** C'est la **vérification prédictive a posteriori** (*posterior predictive check*).

> **Procédure.** (1) Tirer un jeu de paramètres $\theta^{(s)}$ dans la loi a posteriori. (2) Simuler un **jeu de données répliqué** $y^{\mathrm{rep},(s)}$ avec ce $\theta^{(s)}$, de la même taille que les données observées. (3) Calculer une **statistique-test** $T$ (une caractéristique qui nous inquiète : variance, maximum, proportion de zéros…) sur chaque jeu répliqué. (4) Comparer $T(y)$ observé à la distribution des $T(y^{\mathrm{rep}})$. Le **p-value bayésien** $p_B=P\bigl(T(y^{\mathrm{rep}})\ge T(y)\mid y\bigr)$ est la fraction de répliques au-dessus de l'observé : une valeur proche de 0 ou de 1 signale un désaccord.

*Remarque :* il ne s'agit pas d'un test au sens du volume I : le $p_B$ n'est pas uniforme sous le modèle vrai (il est conservateur, car les données servent deux fois : à ajuster le modèle et à le tester). On l'utilise comme **indicateur de désaccord**, pas comme un seuil de décision.

**Retour sur le modèle de Poisson de 6.1.8.** Nous avions modélisé le nombre de commandes annuelles `nb_commandes_an` des 504 clients acquis par le canal Boutique par une loi de Poisson de paramètre $\lambda$ commun, et obtenu l'a posteriori $\mathrm{Gamma}(2087;\ 504{,}5)$. Il avait l'air parfait : un intervalle étroit. Soumettons-le à la vérification : on tire 2 000 valeurs de $\lambda$ dans cet a posteriori, on simule pour chacune un jeu de 504 comptages de Poisson, et on compare trois statistiques de ces jeux répliqués aux valeurs observées.

| statistique | observée | répliques : moyenne | répliques : 2,5 % – 97,5 % | $p$ bayésien |
|---|---:|---:|---|---:|
| variance / moyenne | 3,324 | 1,000 | [0,879 ; 1,127] | 0,0 |
| part de zéros | 0,109 | 0,016 | [0,006 ; 0,030] | 0,0 |
| maximum | 21 | 11,541 | [10 ; 14] | 0,0 |


Le verdict est sans appel. La variance observée est **3,3 fois la moyenne**, alors que les jeux répliqués par le modèle de Poisson ont un rapport proche de 1. Le modèle ne simule **ni autant de zéros** (11 % observés, environ 1,6 % répliqués), **ni de valeurs aussi grandes** (maximum observé de 21, contre 11,5 en moyenne dans les répliques, avec un intervalle à 95 % de [10 ; 14]). Les trois $p_B$ valent 0 : aucune réplique sur 2 000 n'atteint les données. **Le modèle de Poisson est rejeté**, et la raison est celle qu'on soupçonnait : les clients sont hétérogènes.

**Réparation : la loi binomiale négative.** On suppose que le paramètre de Poisson **varie d'un client à l'autre** selon une loi gamma ; en intégrant cette variation (la marginalisation d'un mélange gamma-Poisson, que nous retrouverons au chapitre 2, section 2.6), le nombre de commandes suit une loi **binomiale négative** de moyenne $\mu$ et de paramètre de dispersion $k$ : $\mathrm{Var}=\mu+\mu^2/k$. Quand $k\to\infty$, on retrouve Poisson ; plus $k$ est petit, plus la surdispersion est forte. Il n'y a plus de conjugaison, donc… on utilise notre MCMC. Paramétrons $\theta=(\log\mu,\log k)$ pour travailler sur des réels, avec des a priori $\log\mu\sim\mathcal N(1,2^2)$ et $\log k\sim\mathcal N(0,2^2)$, larges.


Les chaînes sont saines (taux d'acceptation de 0,35 à 0,37 ; $\widehat R$ de 1,0029 pour $\log\mu$ et 1,0019 pour $\log k$ ; ESS de 1 951 et 2 241). L'a posteriori de la moyenne est de 4,134 (intervalle à 95 % [3,817 ; 4,457]) ; la dispersion $k$ a pour médiane 1,817 (intervalle [1,513 ; 2,199]), loin de l'infini de Poisson. Notez surtout que **l'intervalle de crédibilité de la moyenne est plus large que celui du modèle de Poisson** (largeur 0,639 contre 0,355) : le modèle de Poisson **sous-estimait l'incertitude** en la faisant porter par une moyenne unique, alors que les clients varient. C'est l'effet typique d'un modèle trop simple : intervalles trop étroits. Les données étant simulées, la vérité est connue : le générateur utilise justement une dispersion $k=2$ (avec, en plus, d'autres sources d'hétérogénéité : le goût pour les produits et l'âge) : le $k$ estimé est cohérent. Revérifions le modèle réparé avec les mêmes statistiques :

| statistique | observée | répliques : moyenne | répliques : 2,5 % – 97,5 % | $p$ bayésien |
|---|---:|---:|---|---:|
| variance / moyenne | 3,324 | 3,287 | [2,653 ; 4,049] | 0,434 |
| part de zéros | 0,109 | 0,117 | [0,083 ; 0,155] | 0,667 |
| maximum | 21 | 22,964 | [17 ; 32] | 0,714 |


![Vérification prédictive a posteriori de deux modèles pour le nombre de commandes annuelles des clients du canal Boutique. En haut, le modèle de Poisson : les histogrammes des trois statistiques répliquées (variance sur moyenne, part de zéros, maximum) sont loin de la valeur observée (trait rouge). En bas, la binomiale négative : la valeur observée est au milieu des répliques.](figures/ch06-ppc-poisson-binneg.png)

Cette fois, les trois statistiques observées tombent **au milieu** des répliques (les $p_B$ sont loin de 0 et de 1). Le dessin résume la morale : en haut, les données (trait rouge) sont à l'extérieur du nuage des répliques de Poisson ; en bas, elles sont à l'intérieur de celui de la binomiale négative. **Le modèle n'est pas « prouvé vrai »** (aucun ne l'est), mais il a passé trois épreuves que l'autre a échouées.

> ⚠️ **Choisir ses statistiques-test.** Une vérification prédictive ne détecte que les défauts que l'on a pensé à tester. Choisissez des statistiques qui **ne sont pas directement ajustées** par le modèle (la moyenne, que le modèle reproduit par construction, ne révélerait rien) et qui correspondent à vos **soucis** : queues, zéros, asymétrie, dépendance dans le temps, etc.

### 6.4.3 L'a priori est-il raisonnable ? La vérification prédictive *a priori*

Avant même de regarder les données, on peut se demander ce que **l'a priori seul implique**. On simule des paramètres dans l'a priori, puis des données dans le modèle : on obtient la loi **prédictive a priori**. Si elle attribue des probabilités énormes à des scénarios absurdes, l'a priori est mal choisi.

Pour la régression logistique du rachat, regardons ce que signifient des a priori $\beta_j\sim\mathcal N(0,s^2)$ de plus en plus larges, en calculant, pour chaque tirage de $\beta$, la **proportion prédite de clients qui rachètent** (le taux de rachat réel observé est 0,509) :

| écart-type $s$ de l'a priori | taux prédit (5 % – 95 %) | tirages avec taux $<5$ % ou $>95$ % | clients avec $p<1$ % ou $>99$ % (en moyenne) |
|---:|---|---:|---:|
| 0,5 | [0,28 ; 0,71] | 0,0 % | 0,0 % |
| 1,5 | [0,12 ; 0,90] | 2,8 % | 8,6 % |
| 2,5 | [0,05 ; 0,94] | 9,2 % | 28,7 % |
| 10 | [0,01 ; 0,99] | 19,3 % | 79,2 % |


Lecture : avec $s=0{,}5$, l'a priori est **trop serré** : il n'autorise pratiquement que des taux entre 30 % et 70 %, alors que nous ne savons pas à l'avance qu'ils sont dans cette fourchette. Avec $s=10$, l'a priori est **absurde** : en moyenne, **79 % des clients** y ont une probabilité individuelle de rachat inférieure à 1 % ou supérieure à 99 %, et dans un tirage sur cinq le taux global est inférieur à 5 % ou supérieur à 95 %. Cela n'a rien d'une « ignorance » : c'est une opinion très tranchée, que nous n'avons aucune raison d'avoir. Le choix $s=2{,}5$ de la section 6.3.5 est déjà **généreux** (29 % des clients à probabilité individuelle extrême), $s=1{,}5$ plus prudent (9 %). Les deux autorisent une **large gamme de taux globaux** sans verser dans l'extrême ; nous vérifierons en 6.4.4 que le choix entre eux n'influence pas nos conclusions. Voici le dessin :


![Taux de rachat global prédit par l'a priori seul, pour trois largeurs d'a priori sur les coefficients de la régression logistique. Trop serré (à gauche) : tous les modèles prédisent à peu près le même taux. Raisonnable (au milieu) : une gamme étendue de taux plausibles. Trop large (à droite) : la masse s'accumule près de 0 et de 1, des scénarios absurdes.](figures/ch06-prior-predictive.png)

> 💡 **Règle pratique.** On ne peut pas vérifier un a priori par les données (ce serait les utiliser deux fois), mais on peut vérifier ses **conséquences** sur des quantités que l'on comprend (un taux, une moyenne, une durée). Si l'a priori produit des scénarios que vous jugeriez ridicules, resserrez-le.

### 6.4.4 Comparer des modèles : facteur de Bayes et WAIC

**Le facteur de Bayes.** Comparons deux modèles (ou deux hypothèses) $H_0$ et $H_1$ par la formule de Bayes appliquée aux modèles : $\dfrac{P(H_1\mid y)}{P(H_0\mid y)}=\underbrace{\dfrac{p(y\mid H_1)}{p(y\mid H_0)}}_{\text{facteur de Bayes }\mathrm{BF}_{10}}\times\dfrac{P(H_1)}{P(H_0)}$, où $p(y\mid H)=\int p(y\mid\theta,H)\,p(\theta\mid H)\,d\theta$ est la **vraisemblance marginale** (la moyenne de la vraisemblance sur l'a priori). Le $\mathrm{BF}_{10}$ mesure de combien les données déplacent la cote en faveur de $H_1$.

*Exemple à la main.* Une pièce (ou une offre) donne $y$ succès sur $n$ essais. $H_0$ : $\theta=0{,}5$ exactement. $H_1$ : $\theta$ est inconnu avec un a priori uniforme sur $[0,1]$. Alors $p(y\mid H_0)=\binom ny0{,}5^n$ et
$$p(y\mid H_1)=\binom ny\int_0^1\theta^y(1-\theta)^{n-y}d\theta=\binom ny B(y+1,n-y+1)=\frac1{n+1}.$$
(Résultat remarquable : avec un a priori uniforme, **chaque** valeur de $y$ entre 0 et $n$ est également probable a priori.) Pour $n=10,\ y=7$ : $p(y\mid H_0)=120/1024=0{,}1172$ et $p(y\mid H_1)=1/11=0{,}0909$. Donc $\mathrm{BF}_{10}=0{,}0909/0{,}1172=0{,}776$ : les données sont **un peu plus probables sous $H_0$** que sous $H_1$. Sept succès sur dix ne suffisent pas à abandonner la pièce équilibrée ! Le p-value fréquentiste bilatéral est 0,34 : le même message. Appliqué à trois cas (a priori uniforme sous $H_1$, probabilités 50/50 a priori) :

| cas | fréquence | p-valeur (bilatérale) | $\mathrm{BF}_{10}$ | $P(H_1\mid\text{données})$ |
|---|---:|---:|---:|---:|
| 7 rachats sur 10 | 0,7000 | 0,34 | 0,776 | 0,437 |
| offre : 578 sur 1 015 | 0,5695 | $1{,}1\times10^{-5}$ | 720 | 0,999 |
| 50 400 sur 100 000 | 0,5040 | 0,012 | 0,0972 | 0,089 |


Trois cas, trois leçons. (1) *Peu de données* : le facteur de Bayes de 0,78 et la p-valeur de 0,34 s'accordent : on ne peut pas conclure. (2) *Beaucoup de données et un grand écart* (578 sur 1 015) : les deux approches rejettent fermement $H_0$. (3) Le dernier cas est le **paradoxe de Lindley** : avec 100 000 observations et une fréquence de 50,4 %, la p-valeur fréquentiste est petite (0,012 : « significatif au seuil de 5 % », voire de 2 %), alors que le facteur de Bayes ($0{,}097$) **favorise $H_0$ d'un facteur 10** : un écart de 0,4 point est ridicule comparé à ce que prédit l'hypothèse $H_1$ (qui étale sa probabilité sur tout l'intervalle $[0,1]$). La p-valeur se laisse impressionner par la taille de l'échantillon ; le facteur de Bayes pénalise l'hypothèse qui « dilue » sa probabilité inutilement. C'est aussi le **point faible** du facteur de Bayes : il **dépend fortement de l'a priori** (ici, de l'étalement uniforme sous $H_1$). Un a priori plus concentré autour de 0,5 donnerait un autre résultat.

> ⚠️ **Prudence.** Le facteur de Bayes est très sensible au choix de l'a priori sur les paramètres. Il est difficile à calculer pour des modèles complexes (une intégrale en grande dimension). Beaucoup de praticiens bayésiens lui préfèrent des outils prédictifs comme le WAIC ci-dessous.

**Le WAIC : juger un modèle par ses prédictions.** L'idée : un bon modèle est celui qui **prédit bien des données nouvelles**. Le critère **WAIC** (*widely applicable information criterion*) estime la qualité prédictive hors échantillon à partir des seuls tirages a posteriori :
$$\mathrm{lppd}=\sum_{i=1}^n\log\!\Big(\frac1S\sum_{s=1}^S p(y_i\mid\theta^{(s)})\Big),\qquad p_{\mathrm{WAIC}}=\sum_{i=1}^n\mathrm{Var}_s\big[\log p(y_i\mid\theta^{(s)})\big],\qquad \mathrm{WAIC}=-2\,(\mathrm{lppd}-p_{\mathrm{WAIC}}).$$
Le premier terme mesure l'ajustement aux données (plus il est grand, mieux le modèle colle) ; $p_{\mathrm{WAIC}}$ est le **nombre effectif de paramètres**, une pénalité qui punit la complexité (c'est l'analogue bayésien de la pénalité de l'AIC, section 1.4). **Plus le WAIC est petit, meilleur est le modèle.** Comparons quatre modèles du rachat, du plus simple au plus complet, en les estimant tous par notre MCMC (le critère est calculé à partir des tirages a posteriori, sans aucun ajustement supplémentaire) :

| modèle | paramètres | $p_{\mathrm{WAIC}}$ | WAIC | AIC (maximum de vraisemblance) |
|---|---:|---:|---:|---:|
| M0 : constante | 1 | 1,00 | 2 773,9 | 2 773,9 |
| M1 : + offre | 2 | 1,89 | 2 745,9 | 2 746,1 |
| M2 : + canal | 4 | 4,26 | 2 732,1 | 2 731,6 |
| M3 : + âge | 5 | 4,95 | **2 720,8** | 2 720,8 |


Le WAIC **décroît** à mesure que l'on ajoute l'offre, puis le canal, puis l'âge. Le $p_{\mathrm{WAIC}}$ est très proche du nombre de paramètres (comme il se doit pour un modèle régulier avec beaucoup de données), et le WAIC est quasiment égal à l'AIC calculé par le maximum de vraisemblance : avec un a priori diffus et beaucoup de données, les deux critères racontent la même histoire. Les dernières lignes comparent les gains avec leur **incertitude** (un WAIC isolé ne signifie rien : seules les **différences entre modèles** comptent, et leur erreur-type). Une différence est jugée « claire » si elle dépasse environ deux erreurs-types. Ici, l'offre apporte un gain net (27,9 ± 10,9, soit 2,6 erreurs-types) ; le canal (13,8 ± 8,5) et l'âge (11,4 ± 7,0) apportent des gains d'environ 1,6 erreur-type : **plausibles mais non tranchés** par le WAIC seul. Cela ne contredit pas la section 6.3.5, où les intervalles de crédibilité de l'âge et du canal Réseaux excluent 0 : le WAIC répond à la question « *ce coefficient améliore-t-il la prédiction de clients nouveaux ?* », pas à « *ce coefficient est-il différent de zéro ?* ».

**Sensibilité à l'a priori (6.1.6, enfin faite).** Terminons par l'analyse de sensibilité promise : le coefficient de l'offre change-t-il si l'on modifie l'écart-type $s$ de l'a priori ? (Moyenne a posteriori et intervalle de crédibilité à 95 % ; le maximum de vraisemblance donne 0,493.)

| $s$ | moyenne a posteriori de $\beta_{\text{offre}}$ | intervalle à 95 % |
|---:|---:|---|
| 0,5 | 0,476 | [0,291 ; 0,653] |
| 1,5 | 0,488 | [0,296 ; 0,672] |
| 2,5 | 0,492 | [0,314 ; 0,665] |
| 10 | 0,494 | [0,321 ; 0,658] |


Les résultats sont presque identiques pour les quatre a priori (moyenne a posteriori de 0,476 à 0,494, contre 0,493 pour le maximum de vraisemblance), y compris pour l'a priori très serré ($s=0{,}5$, qui ramène un peu le coefficient vers 0) et l'a priori très large ($s=10$) : **nos conclusions ne dépendent pas de l'a priori**, parce que 2 000 observations suffisent à dominer. C'est la situation confortable décrite en 6.1.6, mais elle ne se serait pas produite avec 20 clients.

### 6.4.5 Le flux de travail bayésien, en une page

Voici la liste de contrôle qui résume cette section. Elle est le prolongement bayésien de la démarche du volume I (« décrire, dessiner, contrôler »).

1. **Écrire le modèle** : vraisemblance et a priori. Dire pourquoi.
2. **Vérifier l'a priori** (6.4.3) : la loi prédictive a priori produit-elle des scénarios plausibles ?
3. **Ajuster** avec plusieurs chaînes dispersées (6.3), chauffe écartée.
4. **Diagnostiquer l'algorithme** (6.4.1) : traces en « chenille velue », $\widehat R<1{,}01$, ESS d'au moins quelques centaines pour chaque paramètre d'intérêt. En cas d'échec : changer le pas, reparamétriser, allonger.
5. **Vérifier le modèle** (6.4.2) : jeux répliqués comparables aux données sur des statistiques qui vous inquiètent. En cas d'échec : enrichir le modèle (comme la binomiale négative).
6. **Analyser la sensibilité** (6.1.6) : refaire avec d'autres a priori raisonnables ; la conclusion change-t-elle ?
7. **Comparer** éventuellement des modèles (WAIC, facteur de Bayes en connaissance de cause).
8. **Rapporter** : le modèle, les a priori, les diagnostics, les intervalles de crédibilité, les limites.

> ✅ **À retenir (6.4).**
> - Deux risques indépendants : **l'algorithme** n'a pas convergé, ou **le modèle** est faux. Un diagnostic qui passe ne prouve rien ; un diagnostic qui échoue signale un problème.
> - **Convergence** : plusieurs chaînes dispersées, chauffe écartée, traces en « chenille velue », $\widehat R<1{,}01$, ESS suffisante. Une chaîne unique piégée dans un mode ne signale rien : c'est la comparaison entre chaînes qui détecte le problème.
> - **Vérification prédictive a posteriori** : simuler des données répliquées avec le modèle ajusté et les comparer aux données sur des statistiques ciblées. Le modèle de Poisson échoue (surdispersion), la binomiale négative passe.
> - **Vérification prédictive a priori** : examiner ce que l'a priori implique. Un a priori « vague » mal choisi (écart-type 10 sur un logit) est tout sauf neutre.
> - **Facteur de Bayes** (rapport des vraisemblances marginales) : mesure intuitive mais très sensible à l'a priori (paradoxe de Lindley). **WAIC** : qualité prédictive estimée à partir des tirages ; comparer des modèles par leurs **différences** et leurs erreurs-types.
> - Un a posteriori n'est valide que **conditionnellement au modèle** : la vérification du modèle est une étape à part entière, jamais facultative.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.4, exercices 6.10 à 6.12.


## 6.5 ➕ Pour aller plus loin : la théorie des valeurs extrêmes

> 🧭 **Section optionnelle.** Elle ne suppose que le chapitre 2 du volume I (lois, fonction de répartition, loi des grands nombres) et le maximum de vraisemblance du chapitre 3. Elle peut se lire indépendamment des sections 6.1 à 6.4. Elle prolonge cependant leur esprit : **simuler** pour comprendre, et **vérifier** par rapport à une vérité connue.

> 💡 **Intuition.** La plupart de la statistique s'intéresse au **centre** d'une distribution : la moyenne, la médiane, l'écart-type. Mais certaines décisions se jouent dans les **queues** : « *quel est le plus long retard de livraison que je risque une fois par an ? une fois tous les dix ans ?* », « *quelle est la plus grosse commande à prévoir ?* », « *quel niveau de crue une digue doit-elle supporter ?* ». Ce sont des événements **rares**, que l'on n'a souvent jamais observés. Or **la queue d'une loi n'est pas bien décrite par son centre** : ajuster une loi normale à des données et en extrapoler la queue est l'une des erreurs les plus coûteuses de l'histoire de la gestion du risque. La théorie des valeurs extrêmes fournit des modèles **faits pour la queue**.

### 6.5.1 Le problème : la queue d'une loi normale est trompeuse

Un exemple simple pour fixer les idées. La gérante suit la **durée de livraison** de chaque colis (en jours). Elle veut savoir quel retard est « tellement long qu'on ne le voit qu'une fois en dix ans ». Elle n'a que dix ans de données : l'événement qu'elle cherche est, au mieux, **à la limite de ce qu'elle a observé**, et souvent au-delà. Il faut donc **extrapoler** hors des données, et la forme de la queue décide du résultat.

**Trois comportements de queue.**

| Type de queue | La probabilité de dépasser $x$ décroît comme… | Exemples | Indice $\xi$ |
|---|---|---|---|
| **Légère, bornée** | s'annule au-delà d'un maximum fini | temps de trajet maximal physique | $\xi<0$ (Weibull) |
| **Exponentielle** | $e^{-x}$ : très vite | lois normale, exponentielle, gamma | $\xi=0$ (Gumbel) |
| **Lourde** | $x^{-1/\xi}$ : lentement, comme une puissance | retards logistiques, pertes d'assurance, crues, montants | $\xi>0$ (Fréchet) |

Pour une queue lourde, des valeurs **énormes** surviennent bien plus souvent que ce que la loi normale ne laisse imaginer. L'indice $\xi$ (« indice de queue » ou *shape*) est le paramètre-clé de la théorie.

### 6.5.2 Le théorème fondamental : la loi du maximum

Soit $X_1,\dots,X_n$ indépendantes de même loi, et $M_n=\max(X_1,\dots,X_n)$. Combien vaut sa loi ? Facile : $P(M_n\le x)=F(x)^n$, où $F$ est la fonction de répartition de chaque $X_i$. Mais cela dépend de $F$ et tend vers 0 ou 1. On cherche une loi **limite** après normalisation.

> 📐 **Exemple à la main (lois exponentielles).** Soient $X_i\sim\mathrm{Exp}(1)$ de fonction de répartition $F(x)=1-e^{-x}$. Normalisons le maximum en le décalant de $\ln n$ : pour tout réel $x$,
> $$P\bigl(M_n-\ln n\le x\bigr)=F(x+\ln n)^n=\left(1-\frac{e^{-x}}{n}\right)^{n}\ \xrightarrow[n\to\infty]{}\ \exp\!\left(-e^{-x}\right),$$
> car $(1-a/n)^n\to e^{-a}$. La loi limite, de fonction de répartition $\exp(-e^{-x})$, s'appelle la loi de **Gumbel**. On vient de démontrer que le maximum de $n$ exponentielles, décalé de $\ln n$, suit approximativement une loi de Gumbel.

> 📐 **Théorème de Fisher-Tippett-Gnedenko (admis).** Si, après un changement d'échelle $M_n\mapsto(M_n-b_n)/a_n$, le maximum converge en loi vers une loi non dégénérée, celle-ci est nécessairement de la forme **GEV** (*Generalized Extreme Value*) :
> $$G(z)=\exp\left\{-\left[1+\xi\,\frac{z-\mu}{\sigma}\right]^{-1/\xi}\right\},\qquad 1+\xi\frac{z-\mu}\sigma>0,$$
> avec trois paramètres : **position** $\mu$, **échelle** $\sigma>0$, **forme** $\xi$ (le cas $\xi=0$ se lit comme la limite $\exp\{-e^{-(z-\mu)/\sigma}\}$, la loi de Gumbel).

Autrement dit, comme le théorème central limite pour les moyennes (volume I, section 2.4), il existe un **résultat universel pour les maxima** : quelle que soit la loi d'origine (ou presque), le maximum d'un grand nombre de valeurs suit une loi GEV. Vérifions-le par simulation sur l'exemple exponentiel : on tire 20 000 fois le maximum de 1 000 variables exponentielles, décalé de $\ln 1000\approx6{,}908$, et on compare à la loi de Gumbel.

| $x$ | $-1$ | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|---:|
| $P(M_n-\ln n\le x)$ simulée | 0,0650 | 0,3685 | 0,6922 | 0,8711 | 0,9496 |
| Gumbel $\exp(-e^{-x})$ | 0,0660 | 0,3679 | 0,6922 | 0,8734 | 0,9514 |


La loi de Gumbel colle presque parfaitement (statistique de Kolmogorov-Smirnov : 0,0044). Pour un **autre type de queue**, le résultat est différent : le maximum de variables à queue lourde (loi de Pareto) converge vers une loi de Fréchet, de $\xi>0$. Le type de la loi limite est dicté par la **queue** de la loi d'origine : c'est précisément pourquoi on peut modéliser un maximum sans connaître la loi des observations.

### 6.5.3 Les données : des retards de livraison simulés, à queue lourde

Pour que nous puissions **comparer à la vérité**, nous simulons un jeu de données de colis (il s'agit bien d'une **simulation**, de graine 671 ; ce ne sont pas des données réelles). Dix ans (2016-2025) de livraisons : environ 3 colis par jour en moyenne (loi de Poisson), chacun avec une durée de livraison en jours qui suit une loi de **Pareto généralisée** décalée de 1 jour (la durée minimale) :
$$P(\text{durée}>x)=\Bigl(1+\xi\,\frac{x-1}{\sigma}\Bigr)^{-1/\xi},\qquad x\ge1,$$
avec $\xi=0{,}25$ (queue lourde modérée : la variance est finie, mais pas le moment d'ordre 4) et $\sigma=1{,}5$ jour. Nous garderons ces valeurs **cachées** de nos calculs : nous les utiliserons à la fin pour juger les estimations. Le jeu obtenu compte 10 981 colis sur 3 652 jours (3,01 par jour en moyenne) ; la durée moyenne est de 3,04 jours (écart-type 2,89), la médiane de 2,14, le maximum de 56,32.


La médiane est d'environ 2 jours, mais la queue est longue : 13 % des colis dépassent 5 jours, 2,7 % dépassent 10 jours, et 0,37 % (environ un colis sur 270) dépassent 20 jours. Le plus long retard de la décennie est de 56 jours. Voyons comment la forme de cette queue se lit dans les données, puis comment extrapoler.

### 6.5.4 Première approche : les maxima par blocs

On découpe les dix ans en **blocs** (ici : les mois) et on garde le **plus long retard de chaque mois**, ce qui donne 120 maxima. D'après le théorème de la section 6.5.2, ces maxima suivent approximativement une loi GEV, dont on estime les paramètres par **maximum de vraisemblance** (volume I, section 3.2). (Attention : `scipy` paramètre la GEV par $c=-\xi$, signe opposé à la convention de ce livre.)


Les 120 maxima mensuels vont de 7,68 à 56,32 jours (médiane 15,54). L'ajustement par maximum de vraisemblance donne $\hat\mu=13{,}741$, $\hat\sigma=4{,}772$ et $\hat\xi=0{,}324$, avec un intervalle de confiance bootstrap (300 rééchantillonnages des 120 maxima) de $\xi$ égal à [0,213 ; 0,459] (écart-type 0,066).

L'estimation de $\xi$ est positive, ce qui indique une queue lourde, mais son **intervalle d'incertitude est large** : avec seulement 120 maxima, la forme de la queue est difficile à préciser. C'est la caractéristique majeure de la théorie des extrêmes : **on dispose de très peu de données par construction** (les extrêmes sont rares), et donc l'incertitude est grande.

**Les niveaux de retour.** La quantité que la gérante veut vraiment est le **niveau de retour** $z_T$ : la valeur dépassée en moyenne **une fois toutes les $T$ périodes** (ici, $T$ mois). Autrement dit, la valeur telle que $P(\text{max mensuel}>z_T)=1/T$, soit $G(z_T)=1-1/T$. En résolvant l'équation avec la forme de la GEV, on trouve
$$z_T=\mu-\frac\sigma\xi\Bigl[1-\bigl(-\ln(1-1/T)\bigr)^{-\xi}\Bigr].$$
(*Démonstration* : $G(z)=1-1/T\iff\bigl[1+\xi\frac{z-\mu}\sigma\bigr]^{-1/\xi}=-\ln(1-1/T)$, car $\exp(-y)=1-1/T\iff y=-\ln(1-1/T)$ ; on élève à la puissance $-\xi$ et on isole $z$.) Un niveau de retour à **10 ans**, c'est $T=120$ mois ; à **100 ans**, $T=1\,200$ mois.

Pour montrer le danger de la loi normale, nous comparons trois estimations : (i) la GEV ajustée ; (ii) une loi **normale** ajustée aux mêmes 120 maxima ; (iii) la **vérité** (calculable car nous connaissons le générateur : le maximum mensuel d'un nombre de colis de moyenne $\lambda_m=3\times30{,}4375$ suit exactement une GEV de paramètres $\xi=\xi_0$, $\sigma=\sigma_0\lambda_m^{\xi_0}$, $\mu=1+\sigma_0(\lambda_m^{\xi_0}-1)/\xi_0$, soit $\mu=13{,}547$, $\sigma=4{,}637$, $\xi=0{,}25$). Les niveaux de retour, en jours, sont :

| retour | vérité | GEV ajustée | intervalle bootstrap de la GEV | loi normale ajustée |
|---|---:|---:|---|---:|
| 1 an | 29,1 | 31,5 | [27 ; 37] | 31,5 |
| 10 ans | 56,3 | 68,5 | [51 ; 101] | 41,1 |
| 100 ans | 104,2 | 145,8 | [89 ; 289] | 48,2 |


Le tableau livre le message central. À 1 an, les deux ajustements donnent la même valeur (31,5 jours, pour une vérité de 29,1) : on est **dans** le domaine des données. Mais à 10 ans puis à 100 ans, **la loi normale s'effondre** : elle prédit 41 puis 48 jours, quand la vérité est de 56 puis 104 jours. Elle se trompe de plus de moitié à 100 ans, et dans le sens **rassurant**. La GEV, elle, se trompe plutôt par excès : 68 jours à 10 ans (vérité 56) et 146 à 100 ans (vérité 104), parce que son $\hat\xi=0{,}32$ est un peu supérieur au vrai $0{,}25$ (une petite erreur sur $\xi$ est amplifiée par l'extrapolation). Mais **son intervalle de confiance contient la vérité** ([51 ; 101] à 10 ans, [89 ; 289] à 100 ans), et il est **très large** à 100 ans : c'est honnête, car on extrapole dix fois au-delà de la durée des données. Retenons : la loi normale ne produit pas seulement des erreurs, elle produit des erreurs **rassurantes** et **sans avertissement** (elle n'a pas d'intervalle qui s'élargisse).


![À gauche : niveaux de retour estimés à partir des 120 maxima mensuels de retards de livraison (simulés). La loi normale ajustée (orange) sous-estime fortement les niveaux de retour, alors que la GEV (bleue) reste du bon ordre de grandeur, avec une légère tendance à surestimer, et à intervalle de confiance qui contient la vérité (tirets noirs). À droite : l'excès moyen des retards au-dessus d'un seuil, en fonction du seuil ; une relation à peu près linéaire indique une queue de type GPD.](figures/ch06-extremes-retour.png)

### 6.5.5 Seconde approche : les excès au-dessus d'un seuil (POT)

Garder un seul maximum par mois, c'est **jeter** beaucoup d'information : le deuxième plus long retard d'un mois est peut-être supérieur au maximum d'un autre mois. L'approche **POT** (*peaks over threshold*) exploite **toutes les valeurs qui dépassent un seuil élevé $u$**.

> 📐 **Théorème de Pickands-Balkema-de Haan (admis).** Pour un seuil $u$ assez élevé, la loi des **excès** $X-u$ sachant $X>u$ est approximativement une loi de **Pareto généralisée** (GPD) :
> $$P(X-u>y\mid X>u)\approx\Bigl(1+\xi\,\frac y{\sigma_u}\Bigr)^{-1/\xi},\qquad y>0,$$
> **avec le même indice $\xi$ que la GEV des maxima** (le paramètre d'échelle $\sigma_u$ dépend du seuil).

Un seuil trop bas rend l'approximation GPD fausse (biais) ; un seuil trop haut laisse trop peu de points (variance). C'est le compromis habituel. Deux outils guident le choix (on a ici fait varier le seuil du 80ᵉ au 98ᵉ centile) :

- le **graphique de l'excès moyen** (*mean residual life plot*, panneau de droite ci-dessus) : pour une GPD, l'excès moyen au-dessus de $u$ vaut $\dfrac{\sigma_u}{1-\xi}$ et croît **linéairement** avec $u$. On choisit le plus petit seuil à partir duquel la courbe est à peu près une droite ;
- la **stabilité de $\hat\xi$** : on estime $\xi$ pour plusieurs seuils ; au-delà du bon seuil, l'estimation doit se stabiliser.


Pour six seuils, on obtient :

| centile du seuil | seuil $u$ (jours) | nombre d'excès | $\hat\xi$ | $\hat\sigma_u$ |
|---:|---:|---:|---:|---:|
| 80 % | 4,02 | 2 196 | 0,273 | 2,237 |
| 90 % | 5,69 | 1 098 | 0,252 | 2,795 |
| 93 % | 6,76 | 769 | 0,265 | 2,990 |
| 95 % | 7,73 | 549 | 0,239 | 3,440 |
| 97 % | 9,62 | 330 | 0,301 | 3,550 |
| 98 % | 11,16 | 220 | 0,289 | 4,073 |

L'estimation de $\xi$ reste entre 0,24 et 0,30 pour tous les seuils raisonnables (la vraie valeur est 0,25) : le choix d'un seuil au 95ᵉ centile, qui laisse environ 550 excès, est un bon compromis. Passons maintenant à l'estimation du niveau de retour. Si $\zeta_u=P(X>u)$ est la probabilité d'un dépassement du seuil, la loi de $X$ au-dessus de $u$ s'écrit $P(X>x)=\zeta_u\bigl(1+\xi(x-u)/\sigma_u\bigr)^{-1/\xi}$. Le niveau $x_m$ dépassé **en moyenne une fois tous les $m$ colis** vérifie $P(X>x_m)=1/m$, d'où
$$x_m=u+\frac{\sigma_u}{\xi}\Bigl[(m\,\zeta_u)^{\xi}-1\Bigr].$$
Une période de retour de 10 ans correspond à $m=$ nombre de colis en 10 ans (environ 11 000), de 100 ans à dix fois plus. Avec le seuil au 95ᵉ centile ($u=7{,}73$ jours, 549 excès, soit 5,0 % des colis), on obtient $\hat\xi=0{,}239$ (intervalle bootstrap [0,148 ; 0,330]) et $\hat\sigma_u=3{,}440$, d'où les niveaux de retour :

| retour | vérité | POT (GPD) | intervalle bootstrap POT |
|---|---:|---:|---|
| 1 an | 29,5 | 30,8 | [27 ; 35] |
| 10 ans | 56,4 | 58,3 | [45 ; 73] |
| 100 ans | 104,2 | 105,9 | [71 ; 159] |


La méthode POT donne des estimations très proches de la vérité (58 jours à 10 ans pour une vérité de 56 ; 106 à 100 ans pour 104) et des intervalles d'incertitude **plus étroits** que ceux des maxima par blocs (à 100 ans : [71 ; 159] contre [89 ; 289]), parce qu'elle utilise 549 valeurs au lieu de 120. L'intervalle de $\xi$ est aussi plus étroit ([0,15 ; 0,33] contre [0,21 ; 0,46]). Une remarque sur les deux colonnes « vérité » : elles diffèrent à peine (56,3 contre 56,4 à 10 ans), car elles mesurent deux choses voisines : l'une, le *maximum mensuel* dépassé une fois tous les 120 mois ; l'autre, le *colis individuel* dépassé une fois tous les 11 000 colis environ. Pour un grand nombre de colis, ces deux notions sont presque identiques.

> ⚠️ **Les pièges de l'extrapolation.**
> 1. **Le seuil** : toujours examiner la sensibilité à son choix. Une conclusion qui change radicalement avec le seuil n'est pas fiable.
> 2. **L'indépendance** : les théorèmes supposent des observations (à peu près) indépendantes. Des extrêmes **regroupés** (une tempête qui donne dix journées d'extrêmes consécutives) doivent être « dégroupés » : on ne garde que le plus grand de chaque grappe.
> 3. **La stationnarité** : si la loi change avec le temps (saison, tendance), les niveaux de retour d'hier ne valent plus pour demain. On peut faire dépendre $\mu$ ou $\sigma$ du temps (tendance, covariables).
> 4. **L'extrapolation reste une extrapolation** : un niveau de retour à 100 ans estimé sur 10 ans de données est une **projection**, avec une incertitude énorme. L'intervalle, bien plus que l'estimation ponctuelle, est le résultat à communiquer.
> 5. **Les moments** : pour $\xi\ge1/2$ la variance est infinie ; pour $\xi\ge1$ la moyenne l'est. Les résumés habituels deviennent alors trompeurs, et « la moyenne des retards » n'a plus de sens statistique stable.

> 💡 **Lien avec le bayésien.** Quand les données sont rares, les extrêmes se prêtent très bien à l'approche bayésienne : un a priori informatif sur $\xi$ (« les queues de retards logistiques ont typiquement $0<\xi<0{,}5$ ») stabilise l'estimation, et le Monte-Carlo (6.2) fournit directement une **loi a posteriori des niveaux de retour**. C'est l'approche standard en hydrologie.

> ✅ **À retenir (6.5).**
> - Les décisions de **risque** dépendent de la **queue** de la distribution, et la loi normale en donne une image **dangereusement optimiste**.
> - **Théorème de Fisher-Tippett-Gnedenko** : le maximum de $n$ observations (normalisé) suit une loi **GEV**, de paramètres position $\mu$, échelle $\sigma$ et forme $\xi$ ; $\xi>0$ signale une queue lourde.
> - **Deux approches** : maxima par blocs (GEV) ou excès au-dessus d'un seuil (**POT**, loi de Pareto généralisée). POT utilise davantage de données ; il demande de choisir un seuil.
> - Le **niveau de retour** $z_T$ est la valeur dépassée en moyenne une fois toutes les $T$ périodes ; on l'estime par une formule explicite dans les paramètres.
> - **L'incertitude est grande par construction** : toujours donner un intervalle (bootstrap, vraisemblance profilée, ou a posteriori bayésien).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.5, exercice 6.13.


## 6.6 ➕ Pour aller plus loin : les copules et la modélisation de la dépendance

> 🧭 **Section optionnelle.** Elle suppose les lois jointes et la corrélation (volume I, chapitre 2), la simulation par inversion (6.2.4) et, pour la fin, l'estimation par maximum de vraisemblance. Elle ne dépend pas des sections 6.3 à 6.5.

> 💡 **Intuition.** Deux transporteurs livrent les colis de la boutique. Chacun a ses propres retards, parfois très longs. Mais le vrai risque pour la gérante n'est pas qu'*un* transporteur ait un mauvais jour : c'est que **les deux aient un très mauvais jour en même temps** (un jour de grève, de tempête, de veille de fête), car alors elle n'a plus de solution de repli. Ce risque ne dépend pas seulement de la loi de chaque transporteur (les « lois marginales »), mais de la façon dont ils sont **liés** : de la **structure de dépendance**. La corrélation ne la résume pas : deux paires de variables peuvent avoir la même corrélation et des comportements extrêmes opposés. Une **copule** isole cette structure de dépendance, séparément des marginales, et permet de la modéliser.

### 6.6.1 La corrélation ne dit pas tout

Rappelons (volume I, section 3.1.7) que le coefficient de corrélation de Pearson ne mesure que la dépendance **linéaire**, et qu'il est sensible aux marginales. On lui préfère souvent des mesures **de rang**, qui ne changent pas quand on applique une transformation croissante à l'une des variables :

- le **tau de Kendall** $\tau$ : la probabilité que deux observations soient « concordantes » (l'une est plus grande dans les deux variables) moins la probabilité qu'elles soient « discordantes » ;
- le **rho de Spearman** : la corrélation de Pearson des **rangs**.

*Exemple à la main.* Quatre clients, avec (panier, nombre de commandes) = $(10,1),(20,3),(30,2),(40,4)$. Il y a $\binom42=6$ paires. Paires concordantes (les deux variables vont dans le même sens) : $\{1,2\},\{1,3\},\{1,4\},\{2,4\},\{3,4\}$ : 5. Paire discordante : $\{2,3\}$ (le panier monte de 20 à 30 mais les commandes passent de 3 à 2) : 1. Donc $\tau=(5-1)/6=0{,}667$. Le rho de Spearman de ces quatre clients vaut 0,8. Et si l'on remplace les paniers par leur logarithme et les nombres de commandes par leur carré (deux transformations croissantes), le tau reste exactement $0{,}667$, alors que la corrélation de Pearson passe de 0,8 à 0,7592.


Le tau de Kendall est inchangé par toute transformation croissante des variables ; la corrélation de Pearson, elle, change. **Ce qui ne bouge pas quand on transforme les marginales, c'est précisément la structure de dépendance.** La copule est l'objet mathématique qui la capture.

### 6.6.2 Le théorème de Sklar

> 📐 **Le principe : la transformation intégrale de probabilité.** Si $X$ a une fonction de répartition $F$ continue, alors $U=F(X)$ suit la loi uniforme sur $[0,1]$.
>
> *Démonstration.* Pour $u\in[0,1]$, $P(F(X)\le u)=P(X\le F^{-1}(u))=F(F^{-1}(u))=u$. C'est la réciproque du théorème d'inversion de 6.2.4. $\square$

Passer de $X$ à $U=F(X)$ efface la marginale (toute variable continue devient uniforme) mais **garde le rang**, donc la dépendance.

> 📐 **Définition.** Une **copule** est la fonction de répartition jointe d'un couple $(U,V)$ dont les deux marginales sont uniformes sur $[0,1]$ : $C(u,v)=P(U\le u,\,V\le v)$.
>
> **Théorème de Sklar.** Pour tout couple $(X,Y)$ de fonction de répartition jointe $H$ et de marginales $F,G$, il existe une copule $C$ telle que
> $$H(x,y)=C\bigl(F(x),\,G(y)\bigr),$$
> unique si $F$ et $G$ sont continues. Réciproquement, toute copule $C$ combinée à des marginales $F,G$ quelconques définit une loi jointe.

Le théorème sépare l'énoncé « loi jointe » en deux : **(1) les marginales** (le comportement de chaque variable seule) et **(2) la copule** (la dépendance). On peut modéliser l'une et l'autre **séparément**, puis les assembler. C'est ce qui rend l'outil si commode : on choisit une marginale réaliste pour chaque variable (par exemple, une loi de Pareto généralisée pour des retards, comme en 6.5) et une copule pour les relier.

**Trois copules extrêmes (bornes de Fréchet).** *Indépendance* : $C(u,v)=uv$. *Dépendance parfaite positive* (comonotonie : $V=U$) : $C(u,v)=\min(u,v)$. *Dépendance parfaite négative* ($V=1-U$) : $C(u,v)=\max(u+v-1,\,0)$. Toute copule est coincée entre les deux dernières : $\max(u+v-1,0)\le C(u,v)\le\min(u,v)$.

### 6.6.3 La copule gaussienne

Idée : prendre le couple normal bivarié, **effacer ses marginales normales** (en les transformant en uniformes), **garder sa dépendance**. Soient $(Z_1,Z_2)$ normaux standard de corrélation $\rho$ et $\Phi$ la fonction de répartition de $\mathcal N(0,1)$. Alors $(U,V)=(\Phi(Z_1),\Phi(Z_2))$ a des marginales uniformes ; sa fonction de répartition est la **copule gaussienne**
$$C_\rho(u,v)=\Phi_2\bigl(\Phi^{-1}(u),\Phi^{-1}(v);\,\rho\bigr).$$
Pour simuler un couple $(X,Y)$ de marginales $F$ et $G$ et de dépendance gaussienne : tirer $(Z_1,Z_2)$, poser $U_i=\Phi(Z_i)$, puis $X=F^{-1}(U_1)$ et $Y=G^{-1}(U_2)$ (**inversion**, 6.2.4). Le tau de Kendall d'une copule gaussienne vaut
$$\tau=\frac2\pi\arcsin\rho\qquad\Longleftrightarrow\qquad\rho=\sin\!\left(\frac{\pi\tau}2\right)\quad(\text{formule admise}).$$

La copule gaussienne est simple et très utilisée, mais elle a un défaut majeur : elle n'a **aucune dépendance de queue**. Quand $\rho<1$, la probabilité que les deux variables soient *simultanément* extrêmes devient négligeable plus vite que ne le ferait une vraie dépendance. En deux mots : un modèle gaussien suppose que « quand ça va très mal, ça va très mal *séparément* ».

### 6.6.4 La copule de Clayton : la dépendance dans les queues

La **copule de Clayton** de paramètre $\theta>0$ est
$$C_\theta(u,v)=\bigl(u^{-\theta}+v^{-\theta}-1\bigr)^{-1/\theta}.$$
Elle vérifie $\tau=\dfrac{\theta}{\theta+2}$ (formule admise) : $\theta\to0$ donne l'indépendance, $\theta\to\infty$ la dépendance parfaite. Sa particularité est la **dépendance de queue inférieure** : $\lambda_L=\lim_{q\to0}P(V\le q\mid U\le q)=2^{-1/\theta}>0$. Quand l'une des variables est très petite, l'autre l'est aussi avec une probabilité non négligeable, même à l'extrême.

> 📐 **Comment la simuler ? L'algorithme de Marshall-Olkin.** Soit $V\sim\mathrm{Gamma}(1/\theta,\,\text{taux }1)$ et $E_1,E_2\sim\mathrm{Exp}(1)$ indépendantes de $V$ et entre elles. Alors
> $$U_i=\Bigl(1+\frac{E_i}{V}\Bigr)^{-1/\theta},\quad i=1,2,$$
> est un couple de loi de Clayton.
>
> *Démonstration.* Posons $\psi(t)=(1+t)^{-1/\theta}$. C'est la transformée de Laplace de la loi $\mathrm{Gamma}(1/\theta,1)$ : $\mathbb E[e^{-tV}]=\psi(t)$. Son inverse est $\psi^{-1}(u)=u^{-\theta}-1$. On a $U_i=\psi(E_i/V)$ et $\psi$ est décroissante, donc $U_i\le u\iff E_i\ge V\,\psi^{-1}(u)$, d'où, **sachant $V$**, $P(U_i\le u\mid V)=\exp(-V\psi^{-1}(u))$. Les $E_i$ étant indépendantes sachant $V$,
> $$P(U_1\le u_1,U_2\le u_2)=\mathbb E\Bigl[e^{-V\psi^{-1}(u_1)}\,e^{-V\psi^{-1}(u_2)}\Bigr]=\psi\bigl(\psi^{-1}(u_1)+\psi^{-1}(u_2)\bigr)=\bigl(u_1^{-\theta}+u_2^{-\theta}-1\bigr)^{-1/\theta}.\ \square$$
> (Le facteur $V$ est un « facteur commun » : quand $V$ est petit, les deux $U_i$ sont petits **ensemble**. C'est exactement l'idée d'un événement qui touche les deux transporteurs à la fois.)

Pour obtenir une dépendance dans la queue **supérieure** (les deux variables sont grandes ensemble), on **retourne** la copule : si $(U,V)$ suit Clayton, alors $(1-U,\,1-V)$ suit la **copule de Clayton retournée** (ou « de survie »), de dépendance de queue supérieure $\lambda_U=2^{-1/\theta}$.

### 6.6.5 Deux copules, même tau, comportements extrêmes opposés

Fixons $\tau=0{,}5$ (une dépendance modérément forte). Alors $\rho=\sin(\pi/4)=0{,}7071$ pour la copule gaussienne et $\theta=2\tau/(1-\tau)=2$ pour Clayton. Nous simulons 200 000 couples de chacune. Le premier générateur est la définition même de la copule gaussienne (on prend des normales corrélées, on les passe dans $\Phi$) ; le second est l'algorithme de Marshall-Olkin ci-dessus (un facteur commun gamma $V$, deux exponentielles) :


```python
def sim_gauss(rho, n, rng):
    z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], n)
    return norm.cdf(z)

def sim_clayton(theta, n, rng):
    v = rng.gamma(1 / theta, 1.0, n)                      # facteur commun
    e = rng.exponential(size=(n, 2))
    return (1 + e / v[:, None]) ** (-1 / theta)
```


On compare à la formule exacte la probabilité que les deux variables soient simultanément parmi les 1 %, 5 % ou 10 % **les plus petites** (le tau de Kendall simulé vaut 0,500 pour la gaussienne et 0,506 pour Clayton ; $\lambda_L=2^{-1/\theta}=0{,}707$ pour Clayton, 0 pour la gaussienne) :

| $q$ | indépendance $q^2$ | gaussienne : exact | gaussienne : simulé | Clayton : exact | Clayton : simulé | Clayton / gaussienne |
|---:|---:|---:|---:|---:|---:|---:|
| 0,10 | 0,01000 | 0,04739 | 0,04682 | 0,07089 | 0,07184 | 1,50 |
| 0,05 | 0,00250 | 0,01992 | 0,01959 | 0,03538 | 0,03565 | 1,78 |
| 0,01 | 0,00010 | 0,00273 | 0,00281 | 0,00707 | 0,00681 | 2,59 |

Les formules exactes et les simulations s'accordent. Lecture : avec le **même tau** de 0,5, la probabilité que les deux variables soient *simultanément* parmi les 1 % les plus petites est de 0,71 % avec Clayton contre 0,27 % avec la gaussienne, soit **2,6 fois plus** (dernière colonne), et le rapport **augmente à mesure que l'événement devient plus rare** (1,5 à 10 %, 1,8 à 5 %, 2,6 à 1 %). Pour référence, sous indépendance, cette probabilité serait de 0,01 %. Voici le dessin des deux nuages de points : même dépendance « moyenne », des queues très différentes.


![Deux copules de même tau de Kendall (0,5), 2 500 points chacune, dans l'échelle des rangs. À gauche : la copule gaussienne. À droite : la copule de Clayton, dont les points se concentrent dans le coin inférieur gauche (les deux variables très petites ensemble). Les points rouges sont ceux dont les deux coordonnées sont inférieures à 5 %.](figures/ch06-copules-gauss-clayton.png)

> ⚠️ **L'enseignement de la crise de 2008.** Avant 2008, de nombreux produits financiers (les « CDO ») évaluaient le risque de défaut simultané de nombreux emprunteurs avec une **copule gaussienne**, calibrée sur des corrélations. En période de crise, les défauts se sont produits **ensemble** (dépendance de queue) bien plus souvent que le modèle ne le prévoyait. Le choix de la copule n'est pas un détail technique : c'est une hypothèse sur la dépendance **dans les extrêmes**, précisément là où les données sont les plus rares.

### 6.6.6 Estimer une copule à partir de données

Procédure standard (« semi-paramétrique ») : 

1. transformer chaque variable en **pseudo-observations** $\hat U_i=\mathrm{rang}(X_i)/(n+1)$ (une estimation de $F(X_i)$ par le rang, qui efface la marginale sans la modéliser) ;
2. estimer le paramètre de la copule, soit par **inversion du tau de Kendall** (calculer $\hat\tau$ puis résoudre $\tau(\theta)=\hat\tau$ : $\hat\rho=\sin(\pi\hat\tau/2)$, $\hat\theta=2\hat\tau/(1-\hat\tau)$), soit par **maximum de vraisemblance** sur les pseudo-observations ;
3. **choisir** entre familles par la vraisemblance (comme en 1.4 : l'AIC compte les paramètres ; ici une famille à un paramètre contre une autre à un paramètre : la comparaison directe des log-vraisemblances suffit).

La vraisemblance fait appel à la **densité de copule** $c(u,v)=\partial^2C/\partial u\,\partial v$, que voici : pour Clayton, $c_\theta(u,v)=(1+\theta)(uv)^{-\theta-1}(u^{-\theta}+v^{-\theta}-1)^{-2-1/\theta}$ ; pour la gaussienne, avec $x=\Phi^{-1}(u)$ et $y=\Phi^{-1}(v)$, $c_\rho(u,v)=\dfrac1{\sqrt{1-\rho^2}}\exp\!\Bigl(-\dfrac{\rho^2(x^2+y^2)-2\rho xy}{2(1-\rho^2)}\Bigr)$. Avant d'attaquer un cas réel, **testons la procédure sur des données simulées dont on connaît la copule** : nous simulons 500 couples gaussiens, puis 500 couples de Clayton (avec des marginales quelconques, exponentielle et log-normale : le rang les efface), et nous demandons à la procédure de retrouver la bonne copule :

| données | $\hat\tau$ | $\hat\rho$ | $\hat\theta$ (inversion) | $\hat\theta$ (max. de vraisemblance) | log-vraisemblance gaussienne | log-vraisemblance Clayton |
|---|---:|---:|---:|---:|---:|---:|
| gaussiennes ($\rho=0{,}71$) | 0,452 | 0,652 | 1,65 | 1,08 | **137,0** | 85,6 |
| Clayton ($\theta=2$) | 0,564 | 0,774 | 2,58 | 2,34 | 203,4 | **251,5** |


Dans chaque cas, la famille qui a engendré les données obtient la **plus grande log-vraisemblance** (137,0 contre 85,6 pour les données gaussiennes ; 251,5 contre 203,4 pour les données de Clayton) : la procédure sait distinguer. Pour les données de Clayton, les deux estimations de $\theta$ (2,58 par inversion du tau, 2,34 par maximum de vraisemblance) sont voisines du vrai $\theta=2$, à l'erreur d'échantillonnage près (cet échantillon de 500 points a un tau empirique de 0,56 au lieu de 0,50). Notez qu'en cas de mauvaise famille (Clayton ajustée sur données gaussiennes) les deux méthodes d'estimation de $\theta$ divergent (1,65 contre 1,08) : c'est un signal de mauvaise spécification. (Avec 500 points, la différence de log-vraisemblance est nette ; avec 50, elle ne le serait pas.)

### 6.6.7 Deux études de cas

**Un cas réel (simulé) de dépendance faible.** Dans le fichier `clients.csv`, le panier moyen et le nombre de commandes par an des acheteurs sont-ils liés ? Les clients qui achètent souvent sont-ils aussi ceux qui dépensent plus par commande ? Le nombre de commandes est un entier : de nombreuses égalités rendent les rangs ambigus (la copule n'est pas unique pour des marginales discrètes). Nous **départageons les égalités au hasard**, par une petite astuce standard. Sur les 1 740 acheteurs, le tau de Kendall vaut 0,079 et le rho de Spearman 0,118 ; la log-vraisemblance est 12,8 pour la gaussienne et 3,4 pour Clayton. La part de clients dans le décile supérieur des **deux** variables à la fois est de 0,0121 observée, contre 0,0100 sous indépendance et 0,0142 sous la copule gaussienne ajustée.


La dépendance est **réelle mais faible** (tau de Kendall de 0,079) : la copule gaussienne prédit 1,42 % de clients dans le décile supérieur des deux variables à la fois, contre 1,00 % sous indépendance ; la fréquence observée (1,21 %, soit 21 clients sur 1 740) se situe entre les deux, et un si petit effectif ne permet pas de trancher. Rien d'alarmant et rien d'exploitable : il est tout aussi important de savoir quand une dépendance est **négligeable**. (Dans le générateur de données, le goût pour les produits, facteur latent, influence légèrement les deux variables.)

**Le vrai problème : deux transporteurs en même temps.** Revenons à notre inquiétude. La gérante observe depuis 1 500 jours les retards moyens de ses deux transporteurs (simulés ici ; graine 683). Le transporteur A a des retards (en jours) de marginale Pareto généralisée décalée de 1, $\xi=0{,}25$, $\sigma=1{,}5$ ; le B de $\xi=0{,}20$, $\sigma=2$. **La vraie dépendance** (que la gérante ignore) est une copule de Clayton **retournée** de $\theta=1{,}5$ : les deux transporteurs sont **simultanément très en retard** bien plus souvent que ne le laisserait croire une dépendance gaussienne. Elle ajuste les deux familles et calcule la probabilité qu'*un même jour*, les deux retards dépassent leur propre 99ᵉ centile. Sur les 1 500 jours simulés, les retards moyens sont de 2,94 jours pour A et 3,39 pour B (maxima : 23,1 et 31,4). Le tau de Kendall estimé est 0,416, d'où $\hat\rho=0{,}608$ pour la gaussienne et $\hat\theta=1{,}42$ pour Clayton ; les log-vraisemblances sont 332,6 (gaussienne), 11,0 (Clayton, queue inférieure) et 431,7 (Clayton retournée, queue supérieure).


La comparaison des log-vraisemblances désigne sans ambiguïté la **Clayton retournée**, la bonne famille : elle dépasse la gaussienne d'une centaine d'unités de log-vraisemblance (431,7 contre 332,6), alors que la Clayton « classique » (dépendance dans la queue inférieure, ce qui est le mauvais côté) est de loin la pire des trois (11,0). Le $\hat\theta=1{,}42$ obtenu est proche du vrai 1,5. Maintenant, le calcul qui compte, la probabilité que les deux retards dépassent leur 99ᵉ centile le même jour, sous chaque modèle (mêmes marginales, seules les copules diffèrent) :

| modèle | probabilité | fois plus que l'indépendance | une fois tous les… (jours) |
|---|---:|---:|---:|
| indépendance | 0,00010 | 1,0 | 10 000 |
| copule gaussienne ajustée | 0,00193 | 19,3 | 518 |
| Clayton retournée ajustée | 0,00615 | 61,5 | 163 |
| **vérité** ($\theta=1{,}5$) | 0,00630 | 63,0 | 159 |
| observé sur les 1 500 jours | 0,00533 | 53,3 | 188 |


C'est la leçon centrale de cette section. À marginales identiques et à dépendance **globale** identique (même tau), la copule gaussienne ajustée prévoit des doubles retards extrêmes **3,3 fois moins fréquents** que la vérité : un jour sur 518 contre un jour sur 159. Pour la gérante, c'est la différence entre « un tel jour tous les 17 mois » et « un tel jour tous les 5 mois ». Et par rapport à l'indépendance (un jour sur 10 000), les deux modèles de dépendance annoncent un risque 19 à 63 fois plus grand : ignorer la dépendance serait bien pire encore. La Clayton retournée ajustée (un jour sur 163) est quasiment sur la vérité (un jour sur 159). Ce calcul est essentiellement un calcul de **queue conjointe**, et il dépend presque entièrement du **choix de la copule**, pas des marginales. (L'observation directe sur 1 500 jours ne contient que 8 jours de ce type, soit une fréquence de 0,53 % : le modèle de Clayton en prévoyait 9,2, la copule gaussienne 2,9. Huit événements, c'est peu pour trancher à eux seuls, ce qui illustre pourquoi on **modélise** la dépendance plutôt que de compter les événements rares.)

> ⚠️ **Limites.** (1) **La dépendance de queue est très difficile à estimer** : elle repose sur les quelques points extrêmes. Choisir une famille par la vraisemblance globale (qui est dominée par le centre des données) n'est pas une garantie sur les queues. (2) Les copules à un paramètre ont une forme de dépendance rigide ; pour **plus de deux variables**, on utilise des « vines » (lianes de copules à deux variables), et des modèles plus riches. (3) La dépendance peut **changer avec le temps** (les périodes de crise ont leur propre structure) : le modèle estimé sur une période calme est silencieux sur la crise. (4) Les copules décrivent une **association**, pas une causalité (volume III).

> ✅ **À retenir (6.6).**
> - La corrélation de Pearson ne capture que la dépendance linéaire ; le **tau de Kendall** et le **rho de Spearman** sont des mesures de **rang**, invariantes par transformation croissante.
> - **Théorème de Sklar** : toute loi jointe $=$ des **marginales** $+$ une **copule** ($H=C(F,G)$). On modélise séparément les deux.
> - La copule est la loi jointe des **rangs normalisés** $U=F(X)$ (transformation intégrale de probabilité).
> - **Gaussienne** : pas de dépendance de queue. **Clayton** : dépendance de queue inférieure ($\lambda_L=2^{-1/\theta}$) ; sa version **retournée** donne une dépendance de queue supérieure.
> - On estime une copule sur des **pseudo-observations** (rangs divisés par $n+1$), par inversion du tau ou maximum de vraisemblance ; on **valide la procédure sur des données simulées** de copule connue.
> - **À même tau, des copules différentes ont des comportements extrêmes très différents** : la probabilité d'événements simultanément rares dépend presque uniquement de la copule. C'est le risque principal d'un choix par défaut (gaussien).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.6, exercice 6.14.


## Bilan du chapitre 6

Vous savez maintenant :

- **raisonner à la bayésienne** : a posteriori $\propto$ vraisemblance $\times$ a priori ; utiliser les **lois conjuguées** (bêta-binomiale, gamma-Poisson, normale-normale) pour obtenir des résultats exacts par simple addition ; lire et interpréter un **intervalle de crédibilité** ; formuler des phrases comme « *la probabilité que l'offre soit utile est de…* » ;
- **choisir et justifier un a priori**, mesurer son influence par une **analyse de sensibilité**, et savoir qu'il s'efface quand les données sont abondantes (Bernstein-von Mises) ;
- **estimer par simulation** (Monte-Carlo) : une espérance, une probabilité, une intégrale ; connaître la vitesse en $1/\sqrt n$ ; fabriquer des tirages par **inversion** ou **rejet** ; utiliser l'**échantillonnage préférentiel** pour les événements rares, avec son **ESS**, et les **techniques de réduction de variance** ;
- **simuler une loi a posteriori** non conjuguée avec une chaîne de Markov : **Metropolis-Hastings** (bilan détaillé, réglage du pas, taux d'acceptation) et **Gibbs** (lois conditionnelles complètes), puis calculer *tout* (rapports de cotes, effets sur les probabilités, prédictions) par de simples moyennes ;
- **vérifier ses modèles** : plusieurs chaînes dispersées, traces, $\widehat R$, ESS ; vérifications prédictives **a priori** et **a posteriori** ; comparaison par facteur de Bayes (et ses limites : sensibilité à l'a priori, paradoxe de Lindley) et par WAIC ;
- (en option) **modéliser les extrêmes** par la loi GEV et les excès au-delà d'un seuil (GPD), estimer des **niveaux de retour** avec leur incertitude ;
- (en option) **modéliser la dépendance** par les **copules**, comprendre la différence entre corrélation et dépendance de queue, et pourquoi le choix de la copule décide du risque de **catastrophes simultanées**.

Les deux fils conducteurs de ce chapitre sont **l'incertitude** (qu'il faut quantifier et propager jusqu'à la décision) et **la vérification** (un modèle, un a priori ou un algorithme ne sont jamais acceptés sur parole). Ces deux idées ne s'arrêtent pas aux méthodes bayésiennes : elles guident tout le reste du métier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.14.

Le prochain chapitre, optionnel, aborde l'**inférence causale** : comment passer de « *deux variables varient ensemble* » à « *agir sur l'une changera l'autre* », et ce qu'il faut pour que cette inférence soit légitime. Les sections 6.1 et 6.4 (a priori, vérification de modèle) en seront un outil précieux.
