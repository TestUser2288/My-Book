# Chapitre 4 : Séries temporelles

> « Hier explique un peu aujourd'hui.
> Les séries temporelles sont l'art de mesurer *combien*. »

Jusqu'ici, nous avons presque toujours supposé que nos observations étaient **indépendantes** : 400 commandes tirées au hasard, 2 000 clients qui ne se parlent pas. Cette hypothèse a fait toute la force du volume I (la loi des grands nombres, le théorème central limite, les intervalles de confiance) et celle des régressions des chapitres 1 et 2.

Elle tombe dès qu'on observe **la même chose au fil du temps**. Le chiffre d'affaires de la boutique en mars dépend de celui de février : une bonne année tire les mois vers le haut, décembre est toujours le mois des fêtes, et un choc comme celui de 2020 se prolonge pendant des mois. Les observations sont **dépendantes**, et c'est précisément cette dépendance qui est à la fois le **piège** (les formules du volume I deviennent fausses) et la **ressource** (le passé permet de prévoir l'avenir).

Ce chapitre apprend à lire, à modéliser et à prévoir une série temporelle, avec une seule série en fil rouge : **dix ans de chiffre d'affaires mensuel de la boutique** (janvier 2016 à décembre 2025).

## Le chemin de ce chapitre

- **4.1 Stationnarité, autocorrélation, décomposition** : que veut dire « avoir une structure stable dans le temps » ? Comment mesurer la mémoire d'une série (la fonction d'autocorrélation) ? Comment séparer tendance, saisonnalité et bruit ?
- **4.2 Modèles ARIMA et saisonniers** : les briques AR et MA, la méthode de Box-Jenkins, l'ajout de variables explicatives (promotions, COVID), le diagnostic des résidus.
- **4.3 Prévision et évaluation** : prévoir, quantifier l'incertitude, comparer honnêtement des modèles (découpage temporel, mesures d'erreur, validation à origine glissante), et une première révélation sur la façon dont les données ont été fabriquées.
- ➕ **Pour aller plus loin** : modèles multivariés VAR, cointégration et GARCH (4.4) ; modèles d'espace d'états et filtre de Kalman (4.5) ; Prophet et les bibliothèques modernes de prévision (4.6).
- **Bilan du chapitre**. Les quatre applications guidées et les treize exercices corrigés de ce chapitre se trouvent dans le **cahier** d'exercices et d'applications (repérez l'encadré 📒 en fin de section).

> 💡 **Comment travailler avec ce chapitre.** Le fil conducteur est un **concours de prévision** : plusieurs modèles prévoient les 24 derniers mois de la série, que nous aurons mis de côté **dès le début**, avant même d'avoir regardé les données. Vous verrez que le modèle qui paraît le meilleur sur le papier n'est pas toujours celui qui gagne, et pourquoi. Le livre ne montre du code que lorsqu'il aide à comprendre (quelques appels `statsmodels`) ; les simulations et les figures sont produites par du code caché, mais chaque nombre cité est reproductible, et les applications complètes sont dans le cahier, où vous pourrez taper le code vous-même, changer les paramètres et regarder ce qui casse.

> 📦 **Les données.** Le fichier `donnees/ventes_mensuelles.csv` contient 120 mois : `mois`, `ca` (chiffre d'affaires en €), `nb_commandes`, `promo` (1 si une promotion a eu lieu dans le mois) et `covid` (1 de mars à juin 2020, quatre mois de fermeture partielle). Comme au chapitre précédent, ces données sont **simulées** avec des graines fixes : nous connaissons donc la vérité, et nous la révélerons à la fin de la section 4.3, pour voir si les méthodes l'ont retrouvée. Les sections 4.4 et 4.5 utilisent aussi des séries simulées à part, annoncées chaque fois.

> 🧭 **Prérequis.** Le volume I (section 2.4 sur la loi des grands nombres, section 3.3 sur les intervalles de confiance, section 3.5 sur les p-valeurs, section 1.1 sur les valeurs propres) et le chapitre 1 de ce volume (la régression linéaire et ses diagnostics, section 1.3). Les modèles ARIMA sont, au fond, des régressions où les variables explicatives sont le passé de la série elle-même.


## 4.1 Stationnarité, autocorrélation, décomposition

> 💡 **Intuition.** Un statisticien qui regarde une série temporelle se pose trois questions, dans cet ordre. **(1)** « Cette série a-t-elle des règles stables dans le temps ? » (la **stationnarité**). **(2)** « Combien de mémoire a-t-elle ? Aujourd'hui ressemble-t-il à hier, à il y a un an ? » (l'**autocorrélation**). **(3)** « Quelle part de ce que je vois est une tendance, une saison, ou du bruit ? » (la **décomposition**). Les modèles des sections suivantes ne sont que des réponses chiffrées à ces trois questions.

### 4.1.1 Pourquoi l'ordre compte : le test du mélange

Prenez 100 commandes tirées au hasard : vous pouvez les mélanger, l'histogramme reste le même, la moyenne aussi. Prenez les 96 chiffres d'affaires mensuels de 2016 à 2023 : si vous les mélangez, **vous détruisez l'information**. Un décembre n'est plus à côté d'un janvier, la tendance a disparu, la mémoire aussi. C'est la différence fondamentale entre un échantillon et une **série temporelle** : l'ordre est une partie de la donnée.

Une règle d'hygiène avant d'aller plus loin. Nous voulons, en fin de chapitre, juger honnêtement des prévisions. Il faut donc **mettre de côté dès maintenant** les 24 derniers mois (2024 et 2025) et ne plus les regarder tant que nous n'avons pas choisi nos modèles. Tout ce que nous ferons dans les sections 4.1 et 4.2 (graphiques, tests, choix d'un modèle) utilisera **uniquement les 96 premiers mois**. Un analyste qui choisit son modèle après avoir vu l'avenir ne prévoit rien : il décrit le passé.


Le découpage tient en deux lignes (la série est passée en logarithme, voir 4.1.2) :

```python
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]     # 96 mois pour apprendre, 24 mis de côté
```

Chaque ligne du fichier `ventes_mensuelles.csv` est un mois : par exemple, le chiffre d'affaires (`ca`) de janvier 2016 est de 620 €. Les colonnes `promo` et `covid` sont des variables **explicatives** que nous utiliserons en 4.2.

Pour mesurer à quel point l'ordre compte, nous avons calculé la **corrélation entre un mois et le suivant** (nous la définirons proprement en 4.1.4) sur la série, puis sur 1 000 mélanges aléatoires de la même série.


La série réelle a une corrélation de l'ordre de 0,48 entre un mois et le suivant ; après mélange, elle tombe en moyenne à zéro, avec une dispersion d'environ 0,10, c'est-à-dire $1/\sqrt{96}$. Cette valeur n'est pas un hasard : nous la retrouverons en 4.1.4 comme **bande de confiance** du graphique d'autocorrélation.

### 4.1.2 Première lecture : tendance, saison, bruit, et pourquoi on prend le logarithme

Voici la série d'apprentissage, d'abord en euros, puis en logarithme :


![Chiffre d'affaires mensuel de la boutique de 2016 à 2023 : en euros (à gauche) l'amplitude des oscillations saisonnières grandit avec le niveau ; en logarithme (à droite), elle reste à peu près constante. La bande orange marque mars-juin 2020.](figures/ch04-serie.png)

On lit quatre choses :

1. Une **tendance** : la série monte globalement, d'un peu plus de 1 000 € par mois en 2016 à près de 2 000 € en 2023.
2. Une **saisonnalité** : chaque année se ressemble (creux en janvier, plateau haut l'été, pic en décembre).
3. Un **accident** : le trou de mars à juin 2020.
4. Du **bruit** : des écarts irréguliers autour de la tendance et de la saison.

Observez aussi le panneau de gauche : plus la série monte, plus les oscillations saisonnières s'**élargissent** (l'écart entre le mois le plus haut et le mois le plus bas de l'année est d'environ 1 160 € en 2017 et d'environ 1 970 € en 2023). C'est un schéma **multiplicatif** : la saison *multiplie* le niveau au lieu de s'y *ajouter*. Le panneau de droite montre le remède : en **logarithme**, un produit devient une somme ($\log(T\times S\times R)=\log T+\log S+\log R$), et les oscillations ont une amplitude à peu près constante. Les chiffres le confirment (amplitude de l'année, en euros bruts puis en logarithme) :


L'amplitude brute passe d'environ 1 160 € (2017) à environ 1 970 € (2023), en suivant la croissance du niveau moyen ; l'amplitude en logarithme, elle, reste comprise entre 0,9 et 1,2 pour toutes les années. À partir de maintenant, **nous modélisons le logarithme du chiffre d'affaires**.

> 💡 **Lire une variation en logarithme.** Si $\log y$ augmente de $0{,}05$, alors $y$ est multiplié par $e^{0{,}05}\approx1{,}051$ : une hausse d'environ 5 %. Pour de petites variations, *différence de logarithmes ≈ variation relative*. C'est pourquoi les coefficients des modèles en log se lisent comme des pourcentages.

### 4.1.3 La stationnarité

Pour estimer quelque chose à partir d'**une seule trajectoire** (nous n'avons qu'une seule histoire de la boutique, on ne peut pas rejouer 2016), il faut que le processus ait des règles qui ne changent pas dans le temps. C'est le sens de la stationnarité.

> 📐 **Définition (stationnarité faible).** Une série $(Y_t)$ est **stationnaire au second ordre** si
> 1. $\mathbb E[Y_t]=\mu$ ne dépend pas de $t$ ;
> 2. $\operatorname{Var}(Y_t)=\sigma^2<\infty$ ne dépend pas de $t$ ;
> 3. $\operatorname{Cov}(Y_t,Y_{t+k})=\gamma(k)$ ne dépend que du **décalage** $k$, pas de $t$.
>
> On appelle $\gamma(k)$ l'**autocovariance** et $\rho(k)=\gamma(k)/\gamma(0)$ l'**autocorrélation** d'ordre $k$. Une série *strictement* stationnaire a toutes ses lois jointes invariantes par translation ; avec une variance finie, elle est faiblement stationnaire. La réciproque est fausse en général (elle est vraie pour les séries gaussiennes). Nous n'utiliserons que la version faible.

Quatre exemples simulés montrent à quoi cela ressemble. Chacun a 200 points, et nous comparons la moyenne et la variance de la **première moitié** à celles de la **seconde** (figure ci-dessous) :


![Quatre séries simulées : le bruit blanc et l'AR(1) fluctuent autour d'un niveau fixe (stationnaires) ; la marche aléatoire erre sans revenir ; la série « tendance + bruit » monte (la moyenne change avec le temps).](figures/ch04-stationnarite.png)

- Le **bruit blanc** (des chocs indépendants) et l'**AR(1)** (nous l'étudierons en 4.2) gardent des moyennes et des variances comparables d'une moitié à l'autre : ils sont stationnaires.
- La **série avec tendance** a une variance stable mais une moyenne qui change (environ 2,5 puis 7,5) : elle viole la condition 1.
- La **marche aléatoire** a une moyenne et une variance très différentes d'une moitié à l'autre : elle viole les conditions 1 et 2.

La marche aléatoire est l'exemple fondamental de non-stationnarité. Montrons rigoureusement que sa variance explose :

> 📐 **Démonstration : la variance d'une marche aléatoire croît linéairement.** Soit $Y_t=Y_{t-1}+\varepsilon_t$ avec $Y_0=0$ et des $\varepsilon_t$ indépendants de variance $\sigma^2$. En remplaçant récursivement, $Y_t=\varepsilon_1+\varepsilon_2+\dots+\varepsilon_t$ : une somme de $t$ chocs indépendants. Donc $\operatorname{Var}(Y_t)=t\,\sigma^2$, qui dépend de $t$ et tend vers l'infini. La série ne revient jamais « se stabiliser » : chaque choc a un effet **permanent**. $\blacksquare$

Une simulation de 5 000 marches aléatoires de 200 pas le confirme : la variance **à travers les trajectoires** vaut environ 50 à l'instant 50, 96 à l'instant 100 et 194 à l'instant 200, pour des valeurs théoriques de 50, 100 et 200.


> ⚠️ **Deux façons d'être non stationnaire, deux traitements.** Une série peut avoir une **tendance déterministe** (comme $Y_t=a+bt+u_t$ avec $u_t$ stationnaire : on dit « stationnaire autour d'une tendance »), ou une **tendance stochastique** (comme la marche aléatoire : les chocs s'accumulent). Le premier cas se traite en **retirant la tendance par régression** ; le second en **différenciant** ($Z_t=Y_t-Y_{t-1}$). Appliquer le mauvais remède abîme la série : nous le montrerons en 4.1.6.

Et notre série de chiffre d'affaires ? Elle a une tendance, une saison forte et un accident : elle n'est évidemment **pas stationnaire telle quelle**. La question est de savoir *quelle sorte* de non-stationnarité elle a, ce qui détermine le traitement.

### 4.1.4 L'autocorrélation : mesurer la mémoire

Reprenons la définition : $\rho(k)=\operatorname{Corr}(Y_t,Y_{t+k})$, la corrélation entre la série et elle-même décalée de $k$ pas. On l'estime à partir d'un échantillon $y_1,\dots,y_n$ par

$$r_k=\frac{\sum_{t=k+1}^{n}(y_t-\bar y)(y_{t-k}-\bar y)}{\sum_{t=1}^{n}(y_t-\bar y)^2}.$$

> 💡 **Exemple à la main.** Six chiffres : $10,\ 12,\ 11,\ 14,\ 13,\ 15$. Leur moyenne est $\bar y=12{,}5$ ; les écarts sont $-2{,}5,\ -0{,}5,\ -1{,}5,\ 1{,}5,\ 0{,}5,\ 2{,}5$. Le dénominateur est $\sum(y_t-\bar y)^2=6{,}25+0{,}25+2{,}25+2{,}25+0{,}25+6{,}25=17{,}5$.
> **Décalage 1** : on multiplie chaque écart par le précédent : $(-0{,}5)(-2{,}5)=1{,}25$ ; $(-1{,}5)(-0{,}5)=0{,}75$ ; $(1{,}5)(-1{,}5)=-2{,}25$ ; $(0{,}5)(1{,}5)=0{,}75$ ; $(2{,}5)(0{,}5)=1{,}25$. La somme vaut $1{,}75$, donc $r_1=1{,}75/17{,}5=0{,}10$.
> **Décalage 2** : $(-1{,}5)(-2{,}5)=3{,}75$ ; $(1{,}5)(-0{,}5)=-0{,}75$ ; $(0{,}5)(-1{,}5)=-0{,}75$ ; $(2{,}5)(1{,}5)=3{,}75$. La somme vaut $6$, donc $r_2=6/17{,}5\approx0{,}343$.


Un calcul par programme retrouve exactement les valeurs de la main (0,1 et 0,3429). Notez que le dénominateur est toujours la somme des **$n$ termes** (même pour $k$ grand), ce qui garantit que les autocorrélations estimées forment toujours une suite « possible » (semi-définie positive). Sur la série d'apprentissage, la fonction `acf` de `statsmodels` donne les valeurs suivantes (un calcul direct de la formule ci-dessus retrouve exactement les mêmes nombres) :

```python
from statsmodels.tsa.stattools import acf
print(acf(train, nlags=6).round(3))          # r_0 (toujours 1), r_1, ..., r_6
```
<!--sortie-->
```text
[1.    0.479 0.224 0.305 0.344 0.283 0.191]
```


#### L'autocorrélation partielle

L'autocorrélation d'ordre 2 mélange deux effets : l'influence directe de $y_{t-2}$ sur $y_t$, et l'influence **indirecte** passant par $y_{t-1}$ (qui dépend lui-même de $y_{t-2}$). L'**autocorrélation partielle** d'ordre $k$, notée $\varphi_{kk}$, isole l'effet direct : c'est le **coefficient de $y_{t-k}$ dans la régression de $y_t$ sur $y_{t-1},\dots,y_{t-k}$**. On peut donc la calculer avec les moindres carrés du chapitre 1 : c'est ce que nous avons fait, et nous retrouvons exactement les valeurs de `statsmodels` (0,507, 0,004 et 0,281 aux décalages 1, 2 et 3).


L'autocorrélation partielle n'est donc rien d'autre qu'une régression, ce qui annonce les modèles autorégressifs de la section 4.2.

#### Les bandes de confiance

Sur un graphique d'autocorrélation, on trace une bande autour de zéro. D'où vient-elle ? Pour un **bruit blanc** (aucune mémoire), les $r_k$ sont approximativement gaussiens, centrés, de variance $1/n$ (c'est le théorème central limite du volume I, section 2.4, appliqué à une somme de produits). D'où la bande $\pm1{,}96/\sqrt n$ à 95 %. Une simulation de 2 000 bruits blancs de 96 points confirme que le taux de fausses alertes est bien d'environ 5 % (4,6 % observé, pour une bande de $\pm0{,}20$).


> ⚠️ **Une barre qui dépasse n'est pas une catastrophe.** À 95 %, sur 20 décalages, **une** barre dépasse en moyenne la bande même pour du bruit pur. Ce qui compte, ce sont les barres **nettement** hors bande, ou une structure répétée (tous les 12 mois, par exemple).

Voici l'autocorrélation et l'autocorrélation partielle de notre série d'apprentissage (en logarithme), sur 24 décalages :


![Autocorrélation (à gauche) et autocorrélation partielle (à droite) du logarithme du chiffre d'affaires sur les 96 mois d'apprentissage ; la zone colorée est la bande de confiance à 95 % d'un bruit blanc.](figures/ch04-acf-serie.png)

L'autocorrélation reste significative sur de nombreux décalages (la série a une longue mémoire, due à la tendance et à la saison), avec des bosses aux multiples de 12 : la signature de la saisonnalité annuelle.

### 4.1.5 Le bruit blanc et le test de Ljung-Box

Un **bruit blanc** est une suite de variables indépendantes, centrées, de même variance : la série la plus ennuyeuse possible, **sans mémoire**. Il joue un rôle central, car c'est ce qu'il doit **rester** quand un modèle a tout expliqué : si les résidus d'un modèle ne ressemblent pas à un bruit blanc, il reste de l'information à exploiter.

Pour tester cela globalement (plutôt que décalage par décalage), on utilise la statistique de **Ljung-Box** :

$$Q(h)=n(n+2)\sum_{k=1}^{h}\frac{r_k^2}{n-k}.$$

Sous l'hypothèse « bruit blanc », $Q(h)$ suit approximativement une loi du khi-deux à $h$ degrés de liberté (volume I, section 3.4.6). Une grande valeur de $Q$ signifie qu'au moins une autocorrélation est trop forte pour être due au hasard. Appliquons-la à un vrai bruit blanc simulé et à notre série (le calcul à la main est retrouvé exactement par `statsmodels`).


Pour la série d'apprentissage, `statsmodels` donne :

```python
from statsmodels.stats.diagnostic import acorr_ljungbox
print(acorr_ljungbox(train, lags=[10]))      # statistique Q(10) et p-valeur
```
<!--sortie-->
```text
      lb_stat     lb_pvalue
10  84.003207  8.205675e-14
```

Pour le bruit blanc simulé ($Q(10)=9{,}52$, p-valeur $0{,}48$), la p-valeur est grande : on ne rejette pas l'hypothèse « pas de mémoire ». Pour notre série ($Q(10)=84{,}0$), elle est pratiquement nulle : la série a de la mémoire, ce que l'œil voyait déjà.

> ⚠️ **Quand on teste des résidus de modèle.** Si l'on applique Ljung-Box aux résidus d'un modèle qui a estimé $m$ paramètres de type AR ou MA, il faut réduire les degrés de liberté à $h-m$. Nous le ferons en 4.2.

### 4.1.6 Rendre une série stationnaire : différencier, et tester

Reprenons la distinction de 4.1.3. Pour une **marche aléatoire**, on **différencie** : $\nabla Y_t=Y_t-Y_{t-1}=\varepsilon_t$ est un bruit blanc. Pour une série à **saison** de période $s=12$, on peut utiliser la **différence saisonnière** $\nabla_{12}Y_t=Y_t-Y_{t-12}$ (comparer chaque mois au même mois de l'an passé). Pour notre série en logarithme, cela a une belle interprétation :

- $\nabla\log y_t=\log y_t-\log y_{t-1}\approx$ **taux de croissance mensuel** ;
- $\nabla_{12}\log y_t\approx$ **taux de croissance sur un an**, c'est-à-dire le « +x % par rapport au même mois l'an dernier » des bilans d'entreprise.

Comment décider si une série a besoin d'être différenciée ? On utilise des **tests de racine unitaire**. Le plus célèbre est le **test de Dickey-Fuller**. Son idée : dans le modèle $Y_t=\rho Y_{t-1}+\varepsilon_t$, la série est une marche aléatoire si $\rho=1$ (racine unitaire) et stationnaire si $|\rho|<1$. En retranchant $Y_{t-1}$ des deux côtés, on obtient la régression

$$\nabla Y_t=\alpha+\gamma\,Y_{t-1}+e_t,\qquad \gamma=\rho-1,$$

et on teste $H_0:\gamma=0$ (racine unitaire) contre $\gamma<0$ (stationnaire), avec la statistique de Student habituelle de $\hat\gamma$.

> ⚠️ **Le piège : cette statistique ne suit PAS la loi de Student.** Sous $H_0$, la série n'est pas stationnaire, et les théorèmes du volume I (sur lesquels reposent Student et la loi normale) ne s'appliquent plus. La loi de la statistique est **différente** et se simule. Faisons-le : 5 000 marches aléatoires de 100 pas, la statistique de Dickey-Fuller de chacune, et ses quantiles.


![Loi simulée de la statistique de Dickey-Fuller sous l'hypothèse de racine unitaire (histogramme bleu), décalée vers la gauche par rapport à la loi normale (orange). Le seuil à 5 % se situe vers −2,9 et non −1,64.](figures/ch04-dickey-fuller.png)

Les seuils à 1 %, 5 % et 10 % valent environ $-3{,}5$, $-2{,}9$ et $-2{,}6$ (contre $-2{,}33$, $-1{,}64$ et $-1{,}28$ pour la loi normale). Le seuil à 5 % est donc d'environ $-2{,}9$ (et non $-1{,}645$). Utiliser par erreur le seuil normal ferait « rejeter » la racine unitaire pour près d'une marche aléatoire sur deux : un test nul. Les logiciels utilisent les vraies tables, obtenues par simulation comme ici (Dickey et Fuller, 1979).

Le test de Dickey-Fuller **augmenté** (ADF) ajoute à la régression des différences retardées $\nabla Y_{t-1},\nabla Y_{t-2},\dots$ pour absorber l'autocorrélation. Le test **KPSS** renverse les rôles : son hypothèse nulle est que la série est **stationnaire** (autour d'un niveau ou d'une tendance). Les deux tests se complètent :

| ADF | KPSS | Lecture |
|---|---|---|
| rejette la racine unitaire | ne rejette pas la stationnarité | **stationnaire** (autour de la tendance éventuelle) |
| ne rejette pas | rejette | **racine unitaire** : différencier |
| les deux rejettent / aucun ne rejette | | **verdict ambigu** : les données ne tranchent pas |

Appliquons les deux à notre série d'apprentissage, selon qu'on autorise ou non une tendance déterministe :

```text
                             ADF stat  ADF p  retards  seuil 5 %  KPSS stat  KPSS p
série                                                                              
log(ca), avec tendance         -3.228  0.079       12     -3.465      0.042    0.10
log(ca), niveau seul           -1.064  0.729       12     -2.897      1.561    0.01
différence première            -3.617  0.005       12     -2.897      0.185    0.10
différence saisonnière (12)    -2.418  0.137       12     -2.903      0.057    0.10
différences 1 et 12            -4.436  0.000       11     -2.903      0.023    0.10
```

> ⚠️ **La lecture honnête de ce tableau.** La p-valeur de KPSS est tronquée à 0,10 (borne de la table) ou à 0,01, d'où les valeurs « rondes ».
> - **Avec tendance** : ADF obtient une p-valeur de l'ordre de 0,08, **au-dessus de 5 %**, donc il ne rejette pas la racine unitaire ; mais KPSS, de son côté, **ne rejette pas non plus** la stationnarité autour d'une tendance. C'est le cas ambigu de la troisième ligne du tableau. Avec seulement 96 observations, un COVID au milieu et une saison forte (l'ADF a dû utiliser 12 retards pour l'absorber), le test a **peu de puissance** : il ne peut pas trancher.
> - **Sans tendance** : les deux tests s'accordent pour dire que la série n'est pas stationnaire autour d'un niveau constant (ce qui est évident : elle monte).
> - **Après différenciation** : avec la différence première ou avec les deux différences (1 et 12), les deux tests s'accordent pour la stationnarité. La seule différence saisonnière laisse en revanche un verdict ambigu (l'ADF a une p-valeur de l'ordre de 0,14 : il ne rejette pas la racine unitaire).
>
> **Conclusion** : les données sont compatibles avec **deux** descriptions, « tendance stochastique » (il faut différencier) et « tendance déterministe » (il faut modéliser la tendance et la saison). Plutôt que de forcer un verdict, nous garderons **les deux** candidats en 4.2 et les départagerons en 4.3 par ce qui compte vraiment : la qualité des prévisions.

#### Le danger de la sur-différenciation

Que se passe-t-il si l'on différencie une série qui n'en avait pas besoin ? Prenons un bruit blanc pur, déjà stationnaire, et différencions-le : $\nabla\varepsilon_t=\varepsilon_t-\varepsilon_{t-1}$.

> 📐 **Calcul.** $\operatorname{Var}(\nabla\varepsilon_t)=2\sigma^2$ et $\operatorname{Cov}(\nabla\varepsilon_t,\nabla\varepsilon_{t-1})=\operatorname{Cov}(\varepsilon_t-\varepsilon_{t-1},\varepsilon_{t-1}-\varepsilon_{t-2})=-\sigma^2$. Donc l'autocorrélation d'ordre 1 de la série différenciée vaut $-\sigma^2/(2\sigma^2)=-0{,}5$ : on a **fabriqué** une mémoire artificielle (un « MA(1) avec $\theta=-1$ », que nous étudierons en 4.2).


Une simulation de 2 000 points le confirme (autocorrélation observée de $-0{,}52$ pour une théorie de $-0{,}5$), et la différence première de $\log$(ca) présente elle aussi une autocorrélation négative aux premiers décalages ($-0{,}24$ puis $-0{,}31$). Un signe de sur-différenciation est donc une autocorrélation d'ordre 1 **fortement négative** (autour de $-0{,}5$) et un modèle dont le coefficient MA est proche de $-1$. Gardons cela en tête.

### 4.1.7 Décomposer : tendance, saison, reste

La **décomposition** sépare la série en trois composantes. Sur le logarithme (donc **multiplicative** sur la série d'origine) :

$$\log y_t=T_t+S_t+R_t \quad\Longleftrightarrow\quad y_t=e^{T_t}\times e^{S_t}\times e^{R_t}.$$

La méthode **classique** procède en trois temps :
1. **Tendance** $T_t$ : une moyenne mobile **centrée** sur 12 mois, qui « efface » la saison puisqu'elle contient un exemplaire de chaque mois. Pour une période paire, on utilise la moyenne mobile $2\times12$ (poids $1/24$ aux extrémités, $1/12$ pour les 11 mois du milieu) afin de rester centré sur un mois.
2. **Saison** $S_t$ : on retire la tendance, puis on **moyenne par mois calendaire** (tous les janviers, tous les février…), et on recentre pour que la somme sur l'année soit nulle.
3. **Reste** $R_t=\log y_t-T_t-S_t$.


(Une implémentation à la main de ces trois étapes retrouve exactement la fonction `seasonal_decompose` de `statsmodels`.) La méthode classique a deux défauts : elle perd 6 mois à chaque extrémité (la moyenne mobile centrée n'est pas définie), et elle est **sensible aux accidents** : le COVID de 2020 contamine à la fois la tendance et, via les moyennes par mois, la saison. La méthode **STL** (*Seasonal-Trend decomposition using LOESS*) remédie aux deux : elle estime tendance et saison par régressions locales, et son option `robust=True` **réduit le poids des observations aberrantes** pour que l'accident n'abîme pas les composantes.

```python
from statsmodels.tsa.seasonal import STL
stl = STL(train, period=12, robust=True).fit()      # composantes : stl.trend, stl.seasonal, stl.resid
```


![Décomposition STL robuste du logarithme du chiffre d'affaires (96 mois) : série, tendance, saison, reste. Le reste est petit partout, sauf pendant le COVID (bande orange).](figures/ch04-decomposition.png)

La décomposition raconte l'histoire de la boutique : la **tendance** monte régulièrement, puis semble ralentir à partir de 2021 (STL est un lissage : sa fin de tendance est moins fiable, et nous reverrons en 4.3 si ce ralentissement est réel) ; la **saison** a un profil stable d'une année sur l'autre ; les **résidus** sont petits, sauf les quatre mois de mars à juin 2020 qui ressortent comme les quatre plus gros résidus négatifs. Les **indices saisonniers** se lisent directement : décembre est environ 60 % au-dessus du mois moyen, janvier et février environ 20 à 35 % en dessous.

> 💡 **À quoi sert la décomposition ?** (1) À **comprendre** : « quelle part de la hausse est de la vraie croissance, quelle part est la saison ? ». (2) À **corriger des variations saisonnières** (CVS) : diviser par l'indice saisonnier pour comparer février à décembre. (3) À **repérer les accidents**, ici le COVID, que nous devrons traiter explicitement dans les modèles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercices 4.1, 4.2, 4.5 et 4.9.

> ✅ **À retenir.**
> - Une série temporelle a des observations **dépendantes** ; l'ordre fait partie de la donnée. Mettez de côté la fin de la série **avant** de choisir un modèle.
> - La **stationnarité faible** : moyenne et variance constantes, autocovariance qui ne dépend que du décalage. La marche aléatoire n'est pas stationnaire ($\operatorname{Var}=t\sigma^2$).
> - L'**autocorrélation** mesure la mémoire ; l'**autocorrélation partielle** est un coefficient de régression qui isole l'effet direct. Bande de confiance : $\pm1{,}96/\sqrt n$.
> - **Ljung-Box** teste globalement l'absence d'autocorrélation ; un bon modèle laisse des résidus « bruit blanc ».
> - **Différencier** retire une tendance stochastique ; **sur-différencier** crée une autocorrélation artificielle de $-0{,}5$. La statistique de Dickey-Fuller n'est **pas** de loi normale : son seuil à 5 % est d'environ $-2{,}9$.
> - Les tests de racine unitaire (ADF, KPSS) ont **peu de puissance** sur de courtes séries : quand ils ne tranchent pas, gardez les deux hypothèses de travail et départagez-les par la prévision.
> - On **décompose** (STL robuste) en tendance, saison et reste ; le logarithme transforme un schéma multiplicatif en schéma additif.


## 4.2 Modèles ARIMA et saisonniers

> 💡 **Intuition.** Une série temporelle, c'est un enchaînement : ce qui se passe aujourd'hui dépend un peu de ce qui s'est passé hier, et un peu des **surprises** récentes. Les modèles ARIMA formalisent ces deux idées avec deux briques. La brique **AR** (*autorégressive*) dit : « la valeur d'aujourd'hui est un écho de celle d'hier ». La brique **MA** (*moyenne mobile*, *moving average*) dit : « la valeur d'aujourd'hui garde la trace des chocs d'hier ». On les assemble, on ajoute une différenciation (le **I** de *integrated*) et une version saisonnière, et on obtient la famille la plus utilisée de la prévision statistique.

Nous partons des briques sur des séries **simulées**, où l'on connaît la vérité, pour comprendre ce que chaque modèle fabrique et comment le reconnaître. Puis nous les appliquerons aux ventes de la boutique.

### 4.2.1 Les deux briques : AR et MA

Dans toute la suite, $\varepsilon_t$ désigne un **bruit blanc** (4.1.5), les « surprises » du mois : des chocs indépendants, centrés, de variance $\sigma^2$.

- **AR(1)** : $\;Y_t=\varphi\,Y_{t-1}+\varepsilon_t$. La valeur du jour est une fraction $\varphi$ de celle de la veille, plus une surprise. Si $\varphi=0{,}7$, 70 % du niveau d'hier « survit » aujourd'hui.
- **AR($p$)** : $\;Y_t=\varphi_1Y_{t-1}+\dots+\varphi_pY_{t-p}+\varepsilon_t$ (une régression sur ses $p$ propres valeurs passées).
- **MA(1)** : $\;Y_t=\varepsilon_t+\theta\,\varepsilon_{t-1}$. La valeur du jour est la surprise du jour plus une fraction $\theta$ de la surprise d'hier. Un choc a donc un effet qui dure **exactement un pas**, puis disparaît.
- **MA($q$)** : $\;Y_t=\varepsilon_t+\theta_1\varepsilon_{t-1}+\dots+\theta_q\varepsilon_{t-q}$.

> 💡 **Deux mémoires différentes.** Dans un AR, un choc se **propage indéfiniment** en s'estompant (hier m'influence, qui a influencé avant-hier, etc.). Dans un MA($q$), un choc a un effet **limité** à $q$ pas. Pensez à un AR comme à une cloche qui résonne, et à un MA comme à un coup de tampon qui laisse une trace de durée fixe.

Comment reconnaître l'un ou l'autre sur des données ? Grâce à leurs **signatures** dans l'autocorrélation (ACF) et l'autocorrélation partielle (PACF) de 4.1.4 :

| Modèle | ACF | PACF |
|---|---|---|
| AR($p$) | décroît progressivement (géométriquement) | **s'annule après le décalage $p$** |
| MA($q$) | **s'annule après le décalage $q$** | décroît progressivement |
| ARMA($p,q$) | décroît progressivement | décroît progressivement |

Voici ces signatures pour trois modèles : AR(1) avec $\varphi=0{,}7$, AR(2) avec $\varphi_1=0{,}5$ et $\varphi_2=0{,}3$, MA(1) avec $\theta=0{,}7$. Les barres sont les autocorrélations **théoriques** du modèle ; les points rouges sont celles d'une trajectoire simulée de 500 points.


![Signatures théoriques (barres) et empiriques (points rouges, 500 observations simulées) : l'AR(1) a une ACF qui décroît et une PACF qui s'arrête au décalage 1 ; l'AR(2) a une PACF qui s'arrête au décalage 2 ; le MA(1) a une ACF qui s'arrête au décalage 1 et une PACF qui décroît.](figures/ch04-signatures.png)

Les signatures du tableau apparaissent nettement : la PACF de l'AR(1) n'a qu'une barre, celle de l'AR(2) en a deux, et l'ACF du MA(1) n'en a qu'une. Retenez cette figure : **c'est l'outil d'identification des modèles** que nous utiliserons en 4.2.4.

### 4.2.2 L'AR(1) et le MA(1) en profondeur

#### L'AR(1) : stationnarité, variance, autocorrélations

> 📐 **Proposition.** Soit $Y_t=\varphi Y_{t-1}+\varepsilon_t$ avec $|\varphi|<1$. Alors la série admet la représentation $Y_t=\sum_{j=0}^{\infty}\varphi^j\varepsilon_{t-j}$, elle est stationnaire, de moyenne $0$ et de variance $\gamma(0)=\dfrac{\sigma^2}{1-\varphi^2}$, et son autocorrélation est $\rho(k)=\varphi^{k}$.
>
> **Démonstration.** En remplaçant $Y_{t-1}$ par $\varphi Y_{t-2}+\varepsilon_{t-1}$, puis $Y_{t-2}$, etc., on obtient $Y_t=\varepsilon_t+\varphi\varepsilon_{t-1}+\varphi^2\varepsilon_{t-2}+\dots$. La série $\sum\varphi^{2j}$ converge si et seulement si $|\varphi|<1$, vers $1/(1-\varphi^2)$. Les $\varepsilon$ étant non corrélés, $\operatorname{Var}(Y_t)=\sigma^2\sum_j\varphi^{2j}=\sigma^2/(1-\varphi^2)$, indépendant de $t$ ; la moyenne est nulle. Pour l'autocovariance, on multiplie l'équation par $Y_{t-k}$ ($k\ge1$) et on prend l'espérance : $\gamma(k)=\varphi\,\gamma(k-1)$ (car $\varepsilon_t$ est non corrélé avec $Y_{t-k}$). Donc $\gamma(k)=\varphi^k\gamma(0)$ et $\rho(k)=\varphi^k$. $\blacksquare$
>
> Si $|\varphi|\ge1$, la somme diverge : la série **n'est pas stationnaire** (pour $\varphi=1$, c'est la marche aléatoire de 4.1.3 ; pour $|\varphi|>1$, elle explose).

> 💡 **Exemple à la main.** Avec $\varphi=0{,}5$ et $\sigma=1$ : $\gamma(0)=1/(1-0{,}25)=1{,}333$ ; $\rho(1)=0{,}5$, $\rho(2)=0{,}25$, $\rho(3)=0{,}125$. La mémoire est divisée par deux à chaque pas, et un choc d'il y a trois mois n'a plus que 12,5 % d'influence.


Une simulation de 200 000 points le confirme : variance de 1,328 (théorie : 1,333) et autocorrélations de 0,498, 0,248 et 0,125 aux décalages 1 à 3.

Qu'est-ce que la condition $|\varphi|<1$ devient pour un AR($p$) ? On écrit l'équation avec l'**opérateur retard** $B$ (défini par $BY_t=Y_{t-1}$) : $\varphi(B)Y_t=\varepsilon_t$ avec $\varphi(z)=1-\varphi_1z-\dots-\varphi_pz^p$. La série est stationnaire si et seulement si **toutes les racines du polynôme $\varphi(z)$ sont en dehors du cercle unité** ($|z|>1$). Pour l'AR(1), l'unique racine est $z=1/\varphi$, et $|1/\varphi|>1\iff|\varphi|<1$. On retrouve la condition. Vérifions pour deux AR(2) : pour $\varphi=(0{,}5\,;\,0{,}3)$, les racines ont pour modules 2,84 et 1,17 (toutes deux supérieures à 1 : stationnaire) ; pour $\varphi=(0{,}5\,;\,0{,}6)$, elles ont pour modules 1,77 et 0,94 (**non stationnaire**).


Le second modèle a une racine de module $0{,}94<1$ : sa trajectoire diverge, même si chaque coefficient « a l'air raisonnable ».

#### Le MA(1) : autocorrélation et inversibilité

> 📐 **Proposition.** Pour $Y_t=\varepsilon_t+\theta\varepsilon_{t-1}$ : $\gamma(0)=\sigma^2(1+\theta^2)$, $\gamma(1)=\theta\sigma^2$, $\gamma(k)=0$ pour $k\ge2$. Donc $\rho(1)=\dfrac{\theta}{1+\theta^2}$ et $\rho(k)=0$ au-delà. Un MA est toujours stationnaire.
>
> **Démonstration.** $\operatorname{Var}(Y_t)=\sigma^2+\theta^2\sigma^2$. Et $\operatorname{Cov}(Y_t,Y_{t-1})=\operatorname{Cov}(\varepsilon_t+\theta\varepsilon_{t-1},\varepsilon_{t-1}+\theta\varepsilon_{t-2})=\theta\sigma^2$ (seul le terme $\theta\varepsilon_{t-1}\cdot\varepsilon_{t-1}$ survit). $\blacksquare$

Une subtilité qui surprend : **deux valeurs de $\theta$ donnent exactement la même autocorrélation**, car $\theta/(1+\theta^2)$ est inchangé si l'on remplace $\theta$ par $1/\theta$. Pour $\theta=0{,}5$ comme pour $\theta=2$, on a $\rho(1)=0{,}4$ (un calcul par programme le confirme).


Les données ne permettent donc pas de distinguer les deux. Par convention, on retient celui qui est **inversible** : $|\theta|<1$. Pourquoi ? Un MA(1) inversible peut se réécrire $\varepsilon_t=\sum_{j\ge0}(-\theta)^jY_{t-j}$ : on peut **reconstituer les chocs passés à partir des observations**, ce qui est indispensable pour estimer et prévoir. Si $|\theta|>1$, cette somme diverge. La condition est la même que pour l'AR, côté MA : les racines de $\theta(z)=1+\theta_1z+\dots$ doivent être hors du cercle unité.

### 4.2.3 ARMA, ARIMA et SARIMA

On assemble les briques. Avec l'opérateur retard $B$ :

- **ARMA($p,q$)** : $\varphi(B)\,Y_t=\theta(B)\,\varepsilon_t$.
- **ARIMA($p,d,q$)** : on applique d'abord $d$ différenciations : $\varphi(B)(1-B)^d\,Y_t=\theta(B)\,\varepsilon_t$. Le « I » signifie que $Y$ doit être *intégrée* $d$ fois pour revenir de la série différenciée à $Y$.
- **SARIMA($p,d,q)(P,D,Q)_s$** : on ajoute des briques et des différences **saisonnières**, de période $s$ ($s=12$ pour des données mensuelles) :
$$\varphi(B)\,\Phi(B^s)\,(1-B)^d(1-B^s)^D\,Y_t=\theta(B)\,\Theta(B^s)\,\varepsilon_t.$$

> 📐 **Le « modèle de la compagnie aérienne ».** Le SARIMA$(0,1,1)(0,1,1)_{12}$, popularisé par Box et Jenkins sur les passagers aériens, s'écrit $(1-B)(1-B^{12})Y_t=(1+\theta B)(1+\Theta B^{12})\varepsilon_t$. En développant, $Y_t-Y_{t-1}-Y_{t-12}+Y_{t-13}=\varepsilon_t+\theta\varepsilon_{t-1}+\Theta\varepsilon_{t-12}+\theta\Theta\varepsilon_{t-13}$. Le membre de gauche compare le mois courant au mois précédent, **et** compare ce changement au changement observé un an plus tôt. Avec deux paramètres seulement, ce modèle décrit une tendance, une saison qui évolue lentement, et du bruit : il est le point de départ naturel des séries mensuelles.

#### Comment estime-t-on ces modèles ?

Pour un AR(1), c'est une régression. Estimer $\varphi$ revient à régresser $y_t$ sur $y_{t-1}$ par moindres carrés (c'est la méthode des *moindres carrés conditionnels*), ce qui donne $\hat\varphi=\sum y_ty_{t-1}/\sum y_{t-1}^2$ pour une série centrée. Pour les modèles avec une partie MA, les chocs $\varepsilon_t$ ne sont pas observés, et l'on maximise la **vraisemblance gaussienne** : à chaque date, on calcule la prévision à un pas, et on suppose que l'erreur de prévision suit une loi normale ; la vraisemblance est le produit de ces densités. Le calcul récursif utilise le **filtre de Kalman**, que nous verrons en 4.5. Sur un AR(1) simulé de 300 points (vrai $\varphi=0{,}7$), les moindres carrés donnent $0{,}712$ et le maximum de vraisemblance $0{,}710$.


Les deux estimations sont très proches l'une de l'autre (écart d'environ 0,002) et de la vraie valeur. Qu'en est-il de leur **précision** ? Un résultat classique (Kendall, 1954) dit que l'estimateur des moindres carrés d'un AR(1) est **biaisé vers zéro** : $\mathbb E[\hat\varphi]\approx\varphi-\dfrac{1+3\varphi}{n}$. Une simulation de 4 000 séries de 100 points avec $\varphi=0{,}6$ donne une moyenne des estimations de $0{,}571$ (la formule prédit $0{,}572$), avec un écart-type de $0{,}084$.


Le biais est petit (environ $-0{,}03$ pour $n=100$), mais réel : avec peu de données, un AR estimé paraît **moins persistant** qu'il ne l'est. Étudions maintenant un ARMA(1,1) ($\varphi=0{,}6$, $\theta=0{,}4$) : sur une série de 500 points, l'estimation donne $\hat\varphi=0{,}58$ (erreur type $0{,}04$) et $\hat\theta=0{,}45$ (erreur type $0{,}05$) ; sur 200 séries de 200 points, les moyennes des estimations sont $0{,}59$ et $0{,}41$, avec un écart-type de $0{,}08$ pour chacune.


Sur la série de 500 points, les estimations sont proches des vraies valeurs (0,6 et 0,4), à l'intérieur de leurs marges d'erreur. Sur 200 séries de 200 points, la moyenne est proche de la vérité, mais la **dispersion** est importante (de l'ordre de 0,08 pour chaque paramètre) : estimer les deux paramètres d'un ARMA est nettement plus incertain qu'estimer un AR seul, parce que $\varphi$ et $\theta$ jouent des rôles voisins.

> ⚠️ **Un piège classique : la redondance.** Un ARMA(1,1) avec $\varphi=\theta'$ (où le MA est « l'opposé » de l'AR) se simplifie : $(1-\varphi B)Y_t=(1-\varphi B)\varepsilon_t$ donne $Y_t=\varepsilon_t$. Quand les deux racines sont presque égales, les paramètres ne sont plus identifiables. Si votre modèle estime $\varphi\approx0{,}9$ et $\theta\approx-0{,}9$, il est probablement trop gros : **simplifiez**.

### 4.2.4 La méthode de Box-Jenkins appliquée aux ventes de la boutique

Box et Jenkins ont proposé un cycle en quatre temps : **(1) identifier** la structure à partir de l'ACF et de la PACF, **(2) estimer** les paramètres, **(3) diagnostiquer** les résidus, et, si tout est correct, **(4) prévoir**. Appliquons-le à notre série d'apprentissage (96 mois, en logarithme).

**Étape 1 : stationnariser.** D'après 4.1.6, la série a une tendance et une saison. Les deux différences ($d=1$ et $D=1$, $s=12$) font disparaître la tendance et la saison **stochastiques**. Regardons ce qui reste :


![ACF et PACF de la série différenciée (différence première et différence saisonnière) : une barre négative nette au décalage 12 dans les deux graphiques ; les autres barres restent dans la bande ou l'effleurent.](figures/ch04-acf-diff.png)

**Lecture.** La série différenciée n'a plus de mémoire à long terme. Il reste une **seule structure nette** : une forte barre négative au décalage 12 dans l'ACF (environ $-0{,}43$) et dans la PACF (environ $-0{,}50$). Selon le tableau de 4.2.1, une ACF qui s'arrête au décalage 12 (un seul pic saisonnier) évoque un **MA saisonnier d'ordre 1** ($Q=1$). Aux décalages courts (1 à 3), rien ne dépasse la bande ; le décalage 4 l'effleure à peine (une barre sur quatorze : à ne pas sur-interpréter). La partie non saisonnière est donc modeste, peut-être nulle. On part donc du modèle de la compagnie aérienne, SARIMA$(0,1,1)(0,1,1)_{12}$, et de ses voisins.

**Étape 2 : estimer, avec des variables explicatives.** Nous savons qu'il y a eu un accident (COVID) et des promotions. Nous les ajoutons comme **variables explicatives** (*exogènes*) : le modèle devient une régression dont les erreurs suivent un SARIMA. (Nous détaillons cette idée en 4.2.5.) Ajustons une petite grille de modèles avec $d=1$, $D=1$, $p,q\in\{0,1,2\}$ et $Q\in\{0,1\}$, et comparons-les par **AIC** et **BIC** (chapitre 1, section 1.4 : ces critères mesurent l'ajustement en pénalisant la complexité ; plus petit = meilleur).

```text
les 8 meilleurs modèles par AIC (d = 1, D = 1, s = 12) :
   p  q  Q    AIC    BIC  convergé
0  1  1  1 -176.7 -162.2      True
1  2  1  1 -175.5 -158.6      True
2  1  2  1 -175.5 -158.6      True
3  0  2  1 -173.3 -158.8      True
4  2  2  1 -172.9 -153.5      True
5  2  0  1 -166.4 -151.9      True
6  0  1  1 -165.9 -153.8      True
7  0  0  1 -164.7 -155.1      True

tous convergés : True | meilleur par BIC : (p, q, Q) = (1, 1, 1)
```

Le modèle SARIMAX$(1,1,1)(0,1,1)_{12}$ arrive en tête à la fois par l'AIC et par le BIC. Voici son ajustement (`Xtr` contient les colonnes `promo` et `covid` de la période d'apprentissage) et ses coefficients :

```python
mod_A = SARIMAX(train, exog=Xtr, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print(mod_A.summary().tables[1])
```
<!--sortie-->
```text
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
promo          0.1061      0.022      4.887      0.000       0.064       0.149
covid         -0.5371      0.037    -14.464      0.000      -0.610      -0.464
ar.L1          0.5583      0.115      4.870      0.000       0.334       0.783
ma.L1         -0.9919      0.331     -3.001      0.003      -1.640      -0.344
ma.S.L12      -0.8889      0.262     -3.389      0.001      -1.403      -0.375
sigma2         0.0047      0.002      2.383      0.017       0.001       0.009
==============================================================================
```

> ⚠️ **Les deux coefficients MA sont proches de $-1$ : un signal d'alerte.** `ma.L1` vaut environ $-0{,}99$ et `ma.S.L12` environ $-0{,}89$, avec de très grandes incertitudes (erreurs types de l'ordre de $0{,}3$). Rappelez-vous la sur-différenciation de 4.1.6 : différencier une série qui n'en avait pas besoin crée un MA dont le coefficient est $-1$. Un MA non saisonnier proche de $-1$ suggère que la **différence première** est de trop (la tendance serait **déterministe**, une droite, et non un cumul de chocs) ; un MA **saisonnier** proche de $-1$ suggère que la **différence saisonnière** l'est aussi (la saison serait **déterministe** : le même profil chaque année, fixé une fois pour toutes, et non un profil qui évolue). Le modèle a trouvé le meilleur ajustement *parmi les modèles différenciés*, mais ses propres coefficients nous disent qu'il compense une différenciation excessive. Nous allons mettre cette hypothèse à l'épreuve en 4.2.7.

### 4.2.5 Variables explicatives : la régression à erreurs ARMA

Le modèle que vient d'ajuster `SARIMAX` est une **régression à erreurs ARIMA** :

$$\log y_t=\beta_1\,\text{promo}_t+\beta_2\,\text{covid}_t+\eta_t,\qquad \eta_t\sim\text{SARIMA}(1,1,1)(0,1,1)_{12}.$$

Les variables explicatives interviennent **en niveau** (pas différenciées) et l'ARIMA décrit ce qui reste. C'est la bonne façon de combiner une régression (chapitre 1) et de la mémoire temporelle : si l'on ignorait la mémoire des erreurs, les erreurs types de la régression seraient fausses (le volume I, section 2.4, suppose l'indépendance).

Les coefficients se lisent comme des pourcentages, puisque la variable dépendante est un logarithme : un coefficient $\beta$ correspond à un facteur $e^\beta$, soit une variation de $100\,(e^\beta-1)\,\%$. Ici, la promotion correspond à $+11{,}2\ \%$ (intervalle à 95 % : de $+6{,}6$ à $+16{,}0\ \%$) et le COVID à $-41{,}6\ \%$ (de $-45{,}7$ à $-37{,}1\ \%$).


Une promotion est associée à des ventes environ 11 % plus élevées le mois où elle a lieu, et les quatre mois de COVID à des ventes environ 42 % plus basses, toutes choses égales par ailleurs. Sans ces deux variables, le modèle aurait dû « expliquer » le COVID par du bruit, ce qui aurait dégradé tous les paramètres : l'AIC passe de $-98{,}1$ sans variables explicatives à $-176{,}7$ avec, et l'écart-type estimé des chocs de $0{,}107$ à $0{,}068$.


> 💡 **Les variables explicatives doivent être connues pour prévoir.** Pour prévoir 2026, il faudra fournir la valeur future de `promo` (les promotions sont décidées par la gérante : on peut les supposer connues ou raisonner en scénarios) et de `covid` (nulle). Une variable explicative inconnue dans le futur est inutilisable telle quelle : il faudrait la prévoir elle-même.

### 4.2.6 Le diagnostic des résidus

Un modèle n'est pas fini quand il est ajusté : il faut vérifier qu'il a **tout expliqué**, c'est-à-dire que ses résidus ressemblent à un bruit blanc gaussien. On regarde quatre choses : les résidus dans le temps (pas de structure, variance stable), l'ACF des résidus (pas de barre hors bande), la normalité (histogramme et QQ-plot) et le test de Ljung-Box. Les premiers résidus d'un SARIMA avec différences (ici 13) n'ont pas de sens (ils servent à initialiser le calcul) : on les ignore.


![Diagnostic des résidus du SARIMAX(1,1,1)(0,1,1)12 : résidus standardisés sans structure, histogramme proche de la loi normale, QQ-plot proche de la droite, ACF sans barre hors bande.](figures/ch04-diagnostics.png)

Les résidus ne montrent pas de structure : l'ACF reste dans la bande, les p-valeurs de Ljung-Box sont grandes ($0{,}44$ et $0{,}38$ aux décalages 12 et 24 : on ne rejette pas « bruit blanc »), la normalité n'est pas rejetée (Shapiro-Wilk : $p=0{,}33$). Le modèle a donc **capté l'essentiel de la dynamique linéaire** de la série d'apprentissage.

> ⚠️ **Un bon diagnostic ne prouve pas un bon modèle.** Des résidus blancs montrent qu'il ne reste pas d'**autocorrélation exploitable**, pas que le modèle **prévoira bien** : un modèle trop flexible peut avoir des résidus parfaits sur l'apprentissage et prévoir mal (surajustement). Seule la prévision hors échantillon (4.3) le dira.

### 4.2.7 Deux visions du monde : saison stochastique ou déterministe ?

Nous avons soupçonné plusieurs fois que la tendance et la saison sont **déterministes** (4.1.6 : tests ambigus ; 4.2.4 : deux coefficients MA proches de $-1$). Construisons deux modèles alternatifs, qui **différencient moins** :

- **Modèle B** : SARIMAX$(1,0,0)(0,1,1)_{12}$ avec tendance linéaire (`trend="ct"`) : on garde la différence saisonnière mais on modélise la tendance par une droite.
- **Modèle C** : régression sur **tendance linéaire + 11 indicatrices de mois + promo + COVID**, avec des **erreurs AR(1)**. Ici, la saison est un profil fixe (11 coefficients) et aucune différenciation n'est appliquée.

```text
                                      promo  covid
modèle A : SARIMAX(1,1,1)(0,1,1)      0.106 -0.537
modèle B : (1,0,0)(0,1,1) + tendance  0.100 -0.506
modèle C : régression + AR(1)         0.106 -0.541

modèle C : pente de la tendance = 0.0077 par mois, soit 9.7 % par an ; AR(1) : phi = 0.539 | sigma = 0.06
AIC : A = -176.7 | B = -174.3 | C = -232.5
```

Les trois modèles s'accordent sur les effets de la promotion (coefficient d'environ 0,10 à 0,11, soit +10 à +11 %) et du COVID (coefficient d'environ −0,51 à −0,54, soit −40 à −42 %). Ils diffèrent sur la **dynamique**. Le modèle C décrit une croissance régulière de 0,0077 par mois (9,7 % par an), un AR(1) modéré ($\varphi=0{,}54$), et il obtient l'AIC le plus bas de loin ($-232{,}5$, contre $-176{,}7$ et $-174{,}3$). Attention : **cette comparaison d'AIC n'a pas de sens**.

> ⚠️ **On ne compare pas des AIC entre modèles de différenciations différentes.** L'AIC est calculé à partir de la vraisemblance des **données modélisées**. Le modèle A modélise une série différenciée deux fois, le modèle B une série différenciée une fois, le modèle C la série non différenciée : les vraisemblances portent sur des objets différents, et leurs valeurs ne sont pas comparables (même si le logiciel les affiche sans protester). L'AIC ne peut départager que des modèles de **même $d$ et même $D$** (comme dans la grille de 4.2.4). Pour comparer A, B et C, il n'y a **qu'un seul juge** légitime : leurs **prévisions** sur des données qu'ils n'ont pas vues. C'est l'objet de 4.3.

### 4.2.8 Le même travail en R : `auto.arima`

Les statisticiens utilisent aussi R, où le paquet `forecast` propose `auto.arima`, qui automatise la grille de 4.2.4 (et choisit même les différences par des tests de racine unitaire). Voici ce que donne la fonction sur la même série d'apprentissage, avec les mêmes variables explicatives :

```r
suppressPackageStartupMessages(library(forecast))
d <- read.csv("donnees/ventes_mensuelles.csv")
d <- d[1:96, ]                                       # les 96 mois d'apprentissage
y <- ts(log(d$ca), start = c(2016, 1), frequency = 12)
xreg <- as.matrix(d[, c("promo", "covid")])
modele <- auto.arima(y, xreg = xreg, seasonal = TRUE, ic = "aicc")
print(modele)
```
<!--sortie-->
```text
Series: y 
Regression with ARIMA(0,0,1)(0,1,1)[12] errors 

Coefficients:
         ma1     sma1   drift   promo    covid
      0.4942  -0.8836  0.0078  0.0976  -0.5425
s.e.  0.0798   0.2637  0.0004  0.0210   0.0459

sigma^2 = 0.005107:  log likelihood = 96.73
AIC=-181.47   AICc=-180.38   BIC=-166.88
```

R a retenu un **ARIMA$(0,0,1)(0,1,1)_{12}$ avec une dérive** (une tendance linéaire, `drift`) : pas de différence première, une différence saisonnière, un MA(1) de coefficient d'environ 0,49 et un MA saisonnier d'environ $-0{,}88$. Les effets estimés sont voisins des nôtres (promo : $0{,}098$ ; COVID : $-0{,}54$). Ce choix automatique, fondé sur des tests de racine unitaire pour $d$ et $D$, **va dans le même sens que nos soupçons** : la tendance se modélise bien par une dérive déterministe, sans différence première. Il diffère de la grille de 4.2.4, où nous avions *imposé* $d=1$ ; `auto.arima` utilise de plus l'AICc (une version de l'AIC corrigée pour les petits échantillons). Ce n'est pas une contradiction, mais un rappel : **la sélection automatique n'est pas une vérité**, seulement un point de départ à confronter au diagnostic et à la prévision.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercices 4.3, 4.4 et 4.8.

> ✅ **À retenir.**
> - **AR** : la valeur d'aujourd'hui est un écho de ses propres valeurs passées ; **MA** : elle garde la trace des chocs récents. Signatures : un AR($p$) a une PACF qui s'arrête à $p$, un MA($q$) une ACF qui s'arrête à $q$.
> - **AR(1) stationnaire $\iff|\varphi|<1$**, avec $\gamma(0)=\sigma^2/(1-\varphi^2)$ et $\rho(k)=\varphi^k$. **MA inversible $\iff|\theta|<1$** ; deux valeurs $\theta$ et $1/\theta$ ont la même ACF. Pour un AR($p$) ou MA($q$), les racines du polynôme doivent être hors du cercle unité.
> - **SARIMA$(p,d,q)(P,D,Q)_s$** : $\varphi(B)\Phi(B^s)(1-B)^d(1-B^s)^DY_t=\theta(B)\Theta(B^s)\varepsilon_t$. L'estimation se fait par maximum de vraisemblance ; l'estimateur d'un AR(1) est biaisé vers zéro d'environ $(1+3\varphi)/n$.
> - **Box-Jenkins** : stationnariser, identifier avec ACF/PACF, estimer plusieurs candidats, comparer par AIC/BIC (**à même $d$ et $D$ seulement**), diagnostiquer les résidus (Ljung-Box avec degrés de liberté réduits du nombre de paramètres AR et MA).
> - Une **régression à erreurs ARIMA** (`SARIMAX` avec variables explicatives) combine les effets de variables connues et la mémoire des erreurs ; les coefficients en log se lisent en pourcentages.
> - Un coefficient MA proche de $-1$ signale souvent une **sur-différenciation** : ici, une saison qui pourrait être déterministe.
> - Des résidus blancs ne garantissent pas de bonnes prévisions. **Le juge de paix est la prévision hors échantillon** (4.3).


## 4.3 Prévision et évaluation des prévisions

> 💡 **Intuition.** Prévoir, ce n'est pas deviner un nombre : c'est annoncer **un nombre et son incertitude**. « Les ventes de décembre seront de 3 300 €, avec 95 % de chances de tomber entre 2 800 et 3 900 » est une prévision utile ; « 3 300 » tout court n'en est pas une. Et un modèle ne se juge pas à la beauté de son ajustement passé, mais à la qualité des prévisions qu'il fait sur des données qu'il **n'a pas vues**.

Dans cette section, nous faisons trois choses : comprendre comment un modèle ARIMA prévoit et d'où viennent ses intervalles (4.3.1 et 4.3.2) ; mettre en place une **évaluation honnête** (4.3.3 à 4.3.6) ; puis prévoir 2026 pour la gérante (4.3.7) et **lever le voile** sur la fabrication des données (4.3.8).

### 4.3.1 Comment un modèle prévoit : l'exemple de l'AR(1)

La meilleure prévision ponctuelle de $Y_{T+h}$ à partir de ce qu'on sait à la date $T$ est l'**espérance conditionnelle** $\hat y_{T+h}=\mathbb E[Y_{T+h}\mid Y_T,Y_{T-1},\dots]$ : c'est elle qui minimise l'erreur quadratique moyenne (chapitre 1, section 1.1, avec le passé comme variables explicatives). Pour un AR(1) de moyenne $\mu$, on peut tout calculer.

> 📐 **Prévision d'un AR(1).** Soit $Y_t-\mu=\varphi(Y_{t-1}-\mu)+\varepsilon_t$ avec $|\varphi|<1$. En remplaçant récursivement, $Y_{T+h}-\mu=\varphi^{h}(Y_T-\mu)+\sum_{j=0}^{h-1}\varphi^{j}\varepsilon_{T+h-j}$. Les chocs futurs $\varepsilon_{T+1},\dots,\varepsilon_{T+h}$ sont d'espérance nulle et indépendants du passé, donc
> $$\hat y_{T+h}=\mu+\varphi^{h}(Y_T-\mu),\qquad \operatorname{Var}(Y_{T+h}-\hat y_{T+h})=\sigma^2\sum_{j=0}^{h-1}\varphi^{2j}=\sigma^2\,\frac{1-\varphi^{2h}}{1-\varphi^2}.$$
> La prévision **revient vers la moyenne** à vitesse géométrique, et l'incertitude **croît** de $\sigma^2$ (à un pas) vers la variance de la série elle-même, $\sigma^2/(1-\varphi^2)$. $\blacksquare$

> 💡 **Exemple à la main** (`statsmodels`, appliqué à ces valeurs, retrouve exactement ces nombres). Avec $\varphi=0{,}6$, $\mu=0$, $\sigma=1$ et $Y_T=2$ : $\hat y_{T+1}=0{,}6\times2=1{,}2$ ; $\hat y_{T+2}=0{,}6\times1{,}2=0{,}72$ ; $\hat y_{T+3}=0{,}432$. Les demi-largeurs des intervalles à 95 % sont $1{,}96\sqrt{1}=1{,}96$ ; $1{,}96\sqrt{1+0{,}36}\approx2{,}286$ ; $1{,}96\sqrt{1+0{,}36+0{,}1296}\approx2{,}392$, et tendent vers $1{,}96/\sqrt{1-0{,}36}=2{,}45$. L'avenir lointain n'est pas plus prévisible que « la valeur moyenne, avec la dispersion habituelle ».


Pour un MA(1), la prévision à un pas utilise le dernier choc, et **au-delà d'un pas la prévision est la moyenne** (le choc n'a plus d'effet). Et pour une série **différenciée** ($d=1$), la prévision n'est pas stationnaire : c'est la dernière valeur (plus une éventuelle dérive), et l'incertitude ne se stabilise **jamais**. Voici la demi-largeur d'un intervalle à 95 % pour une marche aléatoire ($\sigma=1$) et pour l'AR(1) précédent, selon l'horizon :

```text
 horizon   marche aléatoire   AR(1), phi = 0,6
       1               1.96               1.96
       3               3.39               2.39
      12               6.79               2.45
      60              15.18               2.45
```

> ⚠️ **Conséquence pratique.** Un modèle avec une différence (première ou saisonnière) a des intervalles de prévision qui **s'élargissent sans limite** quand l'horizon grandit ; un modèle stationnaire autour d'une tendance et d'une saison **déterministes** a des intervalles qui se stabilisent. Parmi nos trois modèles de 4.2, A (deux différences) et B (une différence saisonnière) sont du premier type, et C (aucune différence) du second. Choisir entre les deux, c'est choisir ce que l'on croit de l'avenir lointain : des chocs qui laissent une trace **permanente** ou qui s'effacent.

### 4.3.2 Prévoir en logarithme, annoncer en euros

Nos modèles prévoient $\log(\text{ca})$. Pour annoncer des euros, on revient par l'exponentielle. Deux précautions :

- **Les intervalles** se transforment sans difficulté : si $[L,U]$ est un intervalle à 95 % pour $\log y$, alors $[e^L,e^U]$ en est un pour $y$ (l'exponentielle est croissante).
- **La prévision ponctuelle** $e^{\hat y}$ est la **médiane** de la loi de $Y$, pas sa moyenne : si $\log Y\sim\mathcal N(m,s^2)$, alors $\mathbb E[Y]=e^{m+s^2/2}$. Pour des erreurs de l'ordre de 0,07 en log, le facteur $e^{s^2/2}$ vaut environ 1,0025 : négligeable ici. Il ne le serait pas pour une série plus volatile.

Voyons ce que donnent nos trois modèles (A, B, C de 4.2) sur les 24 mois mis de côté : ils sont ajustés **sur les 96 mois d'apprentissage seulement**, puis on leur demande la prévision des 24 mois suivants. Avec `statsmodels`, c'est un appel :

```python
prev = modele.get_forecast(24, exog=X_test)          # prévision des 24 mois de test
prev.predicted_mean, prev.conf_int(alpha=0.05)        # valeur centrale (en log) et intervalle à 95 %
```

Les résultats, en comptant combien des 24 mois réels tombent dans l'intervalle à 95 % :

```text
facteur de correction moyenne/médiane exp(s^2/2) pour C, 1er et 24e mois : [1.0018 1.0026]
A : SARIMAX(1,1,1)(0,1,1)          : 22 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.41)
B : (1,0,0)(0,1,1) + tendance      : 24 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.43)
C : régression + AR(1)             : 21 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.32)
```

> 📐 **La couverture.** Un intervalle à 95 % **bien calibré** devrait contenir la vraie valeur 95 % du temps. Sur 24 mois, on attend 22 à 23 mois dedans. Observer 21, 22 ou 24 n'est pas une preuve de mauvaise calibration : avec 24 points **corrélés** entre eux, l'incertitude sur la couverture est très grande. Remarquez aussi que les intervalles des modèles qui différencient (A et B, rapports moyens de 1,41 et 1,43) sont plus larges que celui de C (1,32) : conséquence de la remarque de 4.3.1. À retenir : la couverture se vérifie sur de **longues** périodes ou sur **beaucoup** de séries.

### 4.3.3 Le découpage temporel : ne jamais mélanger le passé et l'avenir

En régression ordinaire (chapitre 1), on peut tirer au hasard 20 % des observations pour les tenir à l'écart et évaluer le modèle dessus : les observations sont indépendantes. En série temporelle, **c'est une faute** : un mois « tenu à l'écart » a ses voisins dans l'échantillon d'apprentissage, et le modèle peut les interpoler. On estime alors la capacité du modèle à **combler un trou**, pas à **prévoir**.

Voyons cela sur un cas où le piège est spectaculaire. Nous ajustons des régressions où la tendance est un **polynôme** de degré $1$, $3$, $6$ ou $10$ (plus saison et COVID) sur nos 96 mois d'apprentissage, et nous les évaluons de deux façons : **(a)** en tenant à l'écart 24 mois tirés au hasard (moyenne de 50 tirages) ; **(b)** en apprenant sur les 72 premiers mois et en prévoyant les 24 suivants (donc toujours *dans* la période d'apprentissage : nous ne touchons pas aux données de test). Erreurs quadratiques moyennes (RMSE, en logarithme) :

```text
 degré du polynôme  RMSE (log), 24 mois au hasard  RMSE (log), 24 derniers mois
                 1                          0.093                         0.102
                 3                          0.098                         0.123
                 6                          0.097                         4.442
                10                          0.103                       157.857
```

Avec l'évaluation au hasard, tous les polynômes se valent (erreur de l'ordre de 0,1, sans lien avec le degré) : l'évaluation ne détecte rien. Avec l'évaluation chronologique, la vérité éclate : le polynôme de degré 6 **explose** hors de la zone d'apprentissage (une erreur de 4,4 en logarithme, soit des prévisions fausses d'un facteur de l'ordre de $e^{4{,}4}\approx80$), et celui de degré 10 est absurde (erreur de près de 158). Un modèle flexible ajuste parfaitement le passé et **extrapole n'importe comment**.

> ⚠️ **La règle d'or.** En série temporelle, les données d'évaluation doivent toujours être **postérieures** aux données d'apprentissage. Même règle pour la validation croisée (4.3.6 : on la fait à origine glissante, jamais au hasard) et pour tout prétraitement (une moyenne ou une normalisation doivent être calculées sur l'apprentissage seul).

### 4.3.4 Des références simples, puis des mesures d'erreur

Avant de juger un modèle sophistiqué, on le compare à une **référence simple**. Un modèle qui ne bat pas la référence ne mérite pas sa complexité. Pour une série saisonnière, deux références naturelles :

- le **naïf saisonnier** : prévoir pour un mois la valeur du **même mois l'an dernier** ;
- le **naïf saisonnier avec dérive** : idem, plus la croissance annuelle moyenne observée sur tout l'apprentissage (en logarithme : la moyenne de $y_t-y_{t-12}$).

Pour mesurer l'erreur, quatre indicateurs usuels, avec $e_t=y_t-\hat y_t$ l'erreur de prévision sur $n$ points :

| Mesure | Définition | Remarque |
|---|---|---|
| **MAE** | $\frac1n\sum\lvert e_t\rvert$ | dans l'unité de la série ; robuste |
| **RMSE** | $\sqrt{\frac1n\sum e_t^2}$ | pénalise fortement les grosses erreurs |
| **MAPE** | $\frac{100}{n}\sum\lvert e_t\rvert/\lvert y_t\rvert$ | en %, mais **indéfini** si $y_t=0$ et asymétrique (une surestimation coûte plus qu'une sous-estimation de même taille) |
| **MASE** | MAE / (MAE *dans l'échantillon* du naïf saisonnier) | **sans unité** : $<1$ signifie « mieux que le naïf saisonnier » ; utilisable pour comparer des séries |

> 💡 **Exemple à la main.** Valeurs réelles $100,120,90,110$ ; prévisions $110,115,100,105$. Erreurs : $-10,\,5,\,-10,\,5$. MAE $=(10+5+10+5)/4=7{,}5$. RMSE $=\sqrt{(100+25+100+25)/4}=\sqrt{62{,}5}\approx7{,}91$. MAPE $=\frac{100}{4}\left(\frac{10}{100}+\frac5{120}+\frac{10}{90}+\frac5{110}\right)\approx7{,}46\,\%$. Si le naïf saisonnier avait une MAE de $5$ sur l'apprentissage, la MASE vaudrait $7{,}5/5=1{,}5$ : **pire** que la référence.


Appliquons-les à nos cinq prévisions des 24 mois de test, **en euros** (on revient de l'échelle logarithmique par l'exponentielle). Le tableau est trié par RMSE ; la première ligne rappelle la croissance annuelle moyenne observée en apprentissage, utilisée par le naïf avec dérive :

```text
croissance annuelle moyenne en apprentissage : 0.086 soit 9.0 % par an
                                   MAE     RMSE    MAPE   MASE  biais (log)  RMSE (log)
B : (1,0,0)(0,1,1) + tendance  136.571  169.051   6.132  0.641       -0.004       0.074
naïf saisonnier + dérive       156.641  209.579   6.700  0.735        0.013       0.085
A : SARIMAX(1,1,1)(0,1,1)      173.243  225.707   8.229  0.813       -0.069       0.100
C : régression + AR(1)         175.374  227.290   8.366  0.823       -0.070       0.101
naïf saisonnier                309.604  386.582  13.487  1.452        0.141       0.169
```

Lisons ce tableau (`biais (log)` est la moyenne de $y-\hat y$ en logarithme, donc un biais **positif** signifie que le modèle **sous-estime**).

- Le **naïf saisonnier simple** est le plus mauvais, avec une MASE de 1,45 (pire que lui-même sur l'apprentissage) et un biais de $+0{,}14$ : il répète l'année passée sans tenir compte de la croissance, et donc sous-estime d'environ 14 %.
- Le **naïf saisonnier avec dérive**, une règle élémentaire, est déjà très honorable : MASE de 0,74, MAPE de 6,7 %. Il **bat deux de nos trois modèles ARIMA** (A et C) sur cette fenêtre, en euros comme en MAPE. Voilà pourquoi on ne néglige jamais les références simples.
- Le modèle **B** est le seul à faire nettement mieux que la référence (MASE de 0,64, MAPE de 6,1 %). Les modèles **A** et **C** ont un biais négatif d'environ $-0{,}07$ : ils **surestiment** de 7 % en moyenne. Nous verrons en 4.3.8 pourquoi.

> ⚠️ **Prévoir en euros ou en logarithme ?** Nous avons optimisé les modèles en log (erreurs relatives), mais nous les jugeons en euros (ce qui intéresse la gérante) : une erreur de 300 € en décembre et de 300 € en février n'ont pas le même poids en log, mais le même en euros. Quand l'objectif métier est en unités de la série, évaluez dans ces unités.

### 4.3.5 Vingt-quatre mois suffisent-ils pour conclure ?

Le tableau précédent donne un classement. Mais il repose sur **un seul** découpage, 24 erreurs **corrélées entre elles** (une erreur en mars annonce souvent une erreur en avril), et sur un seul tirage du hasard. Deux garde-fous.

**(1) Le plancher du bruit.** Même le *meilleur modèle possible* ne peut pas prévoir mieux que le bruit qui reste. Le modèle C estime les erreurs d'un AR(1) autour de la tendance et de la saison ; leur écart-type est $\sigma/\sqrt{1-\varphi^2}$, soit $0{,}0715$ ici (contre $0{,}0603$ pour les chocs d'un mois à l'autre).


Pour des prévisions à long terme (au-delà de quelques mois), aucun modèle ne peut descendre durablement sous une erreur de l'ordre de 0,07 en logarithme (environ 7 %) : c'est la limite physique. Un écart de 0,01 entre deux modèles n'est pas une différence que 24 points permettent d'établir.

**(2) Un bootstrap par blocs.** Pour quantifier l'incertitude sur l'écart de performance entre deux modèles, on rééchantillonne les **différences d'erreurs quadratiques** par **blocs** de 6 mois consécutifs (pour conserver la corrélation) : si l'intervalle à 95 % de la différence moyenne **contient 0**, l'avantage d'un modèle n'est pas établi. Voici les résultats pour quatre paires de modèles (intervalle à 95 % de la différence d'erreur quadratique moyenne du premier moins celle du second) :

```text
B : (1,0,0)(0,1,1) + ten  contre A : SARIMAX(1,1,1)(0,1,1  : IC95 = [-0.0092 ; -0.0011]  | part où le 1er est meilleur : 0.99
B : (1,0,0)(0,1,1) + ten  contre C : régression + AR(1)    : IC95 = [-0.0097 ; -0.0010]  | part où le 1er est meilleur : 0.99
A : SARIMAX(1,1,1)(0,1,1  contre C : régression + AR(1)    : IC95 = [-0.0007 ; +0.0004]  | part où le 1er est meilleur : 0.76
A : SARIMAX(1,1,1)(0,1,1  contre naïf saisonnier + dérive  : IC95 = [-0.0028 ; +0.0083]  | part où le 1er est meilleur : 0.17
```

Lecture : un intervalle **entièrement négatif** signifie que le premier modèle est meilleur de façon robuste *sur cette fenêtre* ; un intervalle contenant 0, qu'on ne peut pas conclure. Ici, **B bat A et C** (intervalles négatifs, mais proches de 0 : l'avantage est réel sur cette fenêtre et modeste), tandis que **A et C sont indiscernables**, et que **A ne se distingue pas de la référence simple** (intervalle qui contient 0). Ces résultats portent sur **cette** fenêtre de 24 mois, et nous allons voir en 4.3.8 qu'elle n'est pas anodine.

> ⚠️ **Le test de Diebold-Mariano.** On rencontre souvent ce test pour comparer deux prévisions. Il suppose des erreurs d'**un même horizon** (une suite temporelle de différences de pertes) ; appliqué à des prévisions de 1 à 24 mois issues d'**une seule** origine, il mélange des horizons dont la variance n'est pas la même. Le bootstrap par blocs ci-dessus est plus simple et rend le même service ; le test de Diebold-Mariano trouve sa place quand on dispose d'erreurs à horizon fixe pour de nombreuses origines (4.3.6).

### 4.3.6 La validation à origine glissante

Un seul découpage ne donne qu'un seul exemple d'erreur. Pour en avoir plusieurs, on **recommence plusieurs fois** en avançant l'origine : à chaque étape on ajuste le modèle sur les données jusqu'à la date $T$, on prévoit les $H=12$ mois suivants, on mesure l'erreur, puis on avance $T$ d'un mois (fenêtre **croissante**). On obtient, pour chaque horizon $h$ de 1 à 12, une dizaine d'erreurs. C'est la **validation croisée à origine glissante** (*rolling-origin*, ou *time-series cross-validation*).

> ⚠️ **Honnêteté.** Ces origines (décembre 2023 à décembre 2024) sont celles de notre jeu de test : nous réutilisons la **même période**, avec un autre usage. Les structures des modèles (A, B, C) ont été choisies en 4.2 sur l'apprentissage seul ; ce qui est ré-estimé à chaque origine, ce sont les paramètres. Il n'y a donc pas de fuite, mais il n'y a pas non plus de nouvelles données : le test de 24 mois est « utilisé » ici et ne servira plus à rien d'autre.

On ajoute une sixième prévision, une **combinaison** : la moyenne des prévisions des trois modèles A, B, C (la combinaison de prévisions est connue pour être robuste : les erreurs de modèles différents ne se corrigent qu'en partie, mais elles se corrigent). Résultat : RMSE en logarithme, 13 origines × 12 horizons.

```text
RMSE en logarithme, 13 origines x 12 horizons :
                               RMSE global   h = 1   h = 6  h = 12   biais
modèle                                                                    
B : (1,0,0)(0,1,1) + tendance       0.0670  0.0712  0.0581  0.0889  0.0037
combinaison A+B+C                   0.0687  0.0708  0.0521  0.0808 -0.0295
A : SARIMAX(1,1,1)(0,1,1)           0.0763  0.0737  0.0572  0.0890 -0.0416
C : régression + AR(1)              0.0807  0.0742  0.0637  0.0903 -0.0506
naïf saisonnier + dérive            0.0839  0.0753  0.0801  0.1052 -0.0175
naïf saisonnier                     0.1081  0.1213  0.1100  0.1264  0.0707
```

![Erreur de prévision (RMSE en logarithme) selon l'horizon, pour six méthodes évaluées à 13 origines glissantes. Le naïf saisonnier est nettement derrière ; les modèles ARIMA et leur combinaison sont proches les uns des autres.](figures/ch04-origine-glissante.png)

Trois enseignements, que les chiffres du tableau confirment :

1. **Le naïf saisonnier simple est nettement le moins bon** : il ne sait pas que la série croît. Le naïf **avec dérive** (RMSE de 0,084), une règle élémentaire, fait déjà beaucoup mieux, et fait presque jeu égal avec le modèle C (0,081) : **toujours essayer les références simples**.
2. **Les modèles ARIMA/régression sont proches les uns des autres**, avec un avantage au modèle B (RMSE global de 0,067), qui combine différence saisonnière (il s'adapte au niveau de l'an dernier) et tendance déterministe. La **combinaison** A+B+C (0,069) est presque aussi bonne, **sans avoir à choisir**, et elle est la meilleure aux horizons 1, 6 et 12 du tableau.
3. L'erreur **ne croît pas régulièrement avec l'horizon** (le graphique est irrégulier, avec seulement 13 origines) : elle se situe entre 0,05 et 0,10 pour tous les modèles ARIMA, c'est-à-dire autour du plancher de 0,07 évoqué en 4.3.5. Les écarts entre courbes sont petits devant cette bande de bruit.

### 4.3.7 De la prévision mensuelle à la prévision de l'année : les ventes de 2026

La gérante prépare son budget. Nous prévoyons maintenant 2026 avec le modèle retenu (B), ajusté sur les **120** mois, en supposant une promotion en décembre 2026 (prévue par la gérante), pas de COVID. Outre la prévision mois par mois, on lui donne une **prévision de l'année entière** avec son incertitude, obtenue par **simulation** : on tire 2 000 trajectoires futures plausibles du modèle (en respectant la corrélation entre mois) et on additionne les 12 mois de chacune.

Le chiffre d'affaires de 2025 était de 27 630 €. Pour 2026, le modèle prévoit une médiane de **29 169 €** (soit +5,6 %), avec un intervalle à 80 % de 27 823 à 30 597 € et un intervalle à 95 % de 27 073 à 31 397 €. Mois par mois, la prévision va de 1 414 € en janvier à 4 195 € en décembre (intervalle à 95 % de 3 541 à 4 970 €), comme le montre la figure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1 (construire cette prévision pas à pas).


![Chiffre d'affaires mensuel depuis 2023 et prévision pour 2026 (courbe orange) avec son intervalle de prévision à 95 %.](figures/ch04-prevision-2026.png)

La gérante peut retenir trois messages : (1) **le profil de l'année** : le creux de janvier, le plateau d'été, le pic de décembre ; (2) une **fourchette** de chiffre d'affaires annuel plutôt qu'un point (la fourchette à 80 % est un bon outil de budget) ; (3) une croissance attendue de l'ordre de **+5 %** sur 2025, avec une incertitude que la fourchette rend visible. Cette croissance est inférieure à la tendance de long terme de la série (environ 9 % par an, voir 4.3.4) parce que le modèle B repart du **niveau récent**, resté sous la tendance : nous verrons en 4.3.8 que ce choix est un pari sur la persistance de ces écarts.

> ⚠️ **Ce que cette prévision suppose.** Que la structure observée de 2016 à 2025 **se prolonge** (même croissance, même saisonnalité), que la promotion de décembre ait lieu, et qu'aucun choc du type COVID n'arrive (un tel choc est par nature imprévisible : les intervalles de prévision ne le contiennent pas). Une prévision n'est pas une promesse : c'est le résultat d'un modèle et d'hypothèses, qu'il faut toujours énoncer à côté du chiffre.

### 4.3.8 Révélation : comment les données ont été fabriquées

Les ventes de la boutique sont **simulées**. Il est temps de lever le voile. Voici la recette complète (le script `build/donnees2.py` la reproduit exactement) :

$$\log y_t=\log 1000+0{,}0075\,t+\log s_{\text{mois}(t)}+\eta_t+0{,}10\,\text{promo}_t-0{,}55\,\text{covid}_t,\qquad \eta_t=0{,}5\,\eta_{t-1}+\varepsilon_t,\ \ \varepsilon_t\sim\mathcal N(0,0{,}07^2),$$

soit une tendance exponentielle (+0,75 % par mois), une saisonnalité **déterministe** (un facteur multiplicatif $s$ par mois, de 0,62 en janvier à 1,55 en décembre), un bruit **AR(1)** (coefficient 0,5, chocs de 0,07), un effet de promotion (+10 % en log) et un choc COVID (−0,55 en log, mars à juin 2020).


Comparons ce que les modèles ont **estimé** à ce qui a été **programmé** (paramètres, puis profil saisonnier) :

```text
                                 programmé  modèle A  modèle B  modèle C
pente de la tendance (par mois)     0.0075       NaN       NaN    0.0077
effet promo (log)                   0.1000    0.1061    0.0995    0.1063
effet COVID (log)                  -0.5500   -0.5371   -0.5055   -0.5408
AR(1) : phi                         0.5000       NaN       NaN    0.5388
chocs : sigma                       0.0700       NaN       NaN    0.0603
```

```text
profil saisonnier, en log et relativement à janvier :
                   jan   fév   mar   avr   mai  juin  juil  août  sept   oct   nov   déc
programmé          0.0  0.15  0.43  0.48  0.59  0.64  0.68  0.62  0.37  0.23  0.53  0.92
estimé (modèle C)  0.0  0.18  0.46  0.51  0.59  0.66  0.70  0.61  0.37  0.20  0.48  0.94
```

Les modèles ont **retrouvé** la recette : la pente de la tendance (0,0077 estimé pour 0,0075), l'effet de la promotion (0,106 pour 0,10), l'effet du COVID (de $-0{,}51$ à $-0{,}54$ pour $-0{,}55$), la saison mois par mois (écarts de quelques centièmes en log), le coefficient AR (0,54 pour 0,5) ; seule la taille des chocs est un peu sous-estimée (0,060 pour 0,07). Et nos soupçons étaient fondés : la tendance et la saison étaient bien **déterministes**, ce que laissaient entendre les tests ambigus de 4.1.6 et les MA proches de $-1$ de 4.2.4. Le modèle C a la **structure exacte** de la vérité.

**Pourtant, C n'a pas gagné le concours de 4.3.4.** Pourquoi un modèle correctement spécifié perd-il ? La réponse tient au bruit. Le **bruit programmé** valait, en moyenne, $-0{,}014$ pendant l'apprentissage et $-0{,}0695$ sur les 24 mois de test (écart-type $0{,}066$) ; le biais moyen des prévisions du modèle C sur le test est de $-0{,}0696$.


Le bruit programmé sur les 24 mois de test est **négativement décalé** en moyenne : $-0{,}0695$ en log, soit environ 7 % de ventes en dessous de la tendance et de la saison (contre $-0{,}014$ pendant l'apprentissage). Le modèle C, qui ne croit qu'à la tendance et à la saison, prévoit « la tendance » : son erreur moyenne ($y-\hat y$ vaut $-0{,}0696$ en moyenne, contre $-0{,}0695$ pour le bruit) est **exactement ce bruit**. Le « biais » de C n'est pas un défaut du modèle : c'est la trajectoire du hasard. Même un « modèle parfait » qui connaîtrait tous les paramètres aurait une RMSE de 0,095 sur ces 24 mois, **plus** que le modèle B (0,074, en log). C'est la malchance de cet échantillon de test : la série est restée sous sa tendance pendant deux ans, et le modèle B, qui **s'ajuste au niveau récent** grâce à sa différence saisonnière, a bénéficié de cette persistance. (Dans cette situation, il a *parié* sur la persistance des écarts, et il a gagné. Ce pari est bon quand les écarts sont persistants et mauvais quand ils sont transitoires.)

Un test sur **une** trajectoire ne distingue pas « bon modèle » et « modèle chanceux ». La seule façon de le savoir est de **rejouer le hasard** : nous avons tiré 30 historiques complets avec la même recette (graines différentes), ajusté B et C sur les 96 premiers mois de chacun, prévu les 24 suivants et comparé les erreurs. RMSE moyenne en logarithme : $0{,}129$ pour le naïf avec dérive, $0{,}111$ pour B et $0{,}088$ pour C ; C bat B dans 25 historiques sur 30, et le naïf avec dérive dans 30 sur 30.


Sur 30 historiques, c'est le **modèle de structure exacte (C)** qui a en moyenne la meilleure performance, mais il **ne gagne pas à chaque fois** : le résultat d'un seul découpage dépend beaucoup de la trajectoire du bruit. C'est exactement ce qu'on attend de la statistique : une conclusion se juge sur la **répétition**, pas sur un tirage.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4 (validation à origine glissante), exercices 4.6, 4.7 et 4.13.

> ✅ **À retenir.**
> - Une prévision est un **couple** (valeur, incertitude). Pour un AR(1) : $\hat y_{T+h}=\mu+\varphi^h(Y_T-\mu)$ et la variance de l'erreur croît de $\sigma^2$ vers $\sigma^2/(1-\varphi^2)$ ; avec une différence première, elle croît **sans limite**.
> - En logarithme, $e^{\hat y}$ est la **médiane** ; les intervalles se transforment par l'exponentielle.
> - **Découpage temporel obligatoire** : jamais de mélange au hasard. Un modèle flexible peut avoir une excellente évaluation « au hasard » et extrapoler n'importe comment.
> - Toujours comparer à des **références simples** (naïf saisonnier, avec dérive). Mesures : MAE, RMSE, MAPE (attention aux zéros), **MASE** (sans unité, $<1$ = bat le naïf).
> - Un seul découpage de 24 mois est **bruité** : l'erreur d'un modèle parfait est plafonnée par le bruit de la série ; on utilise un bootstrap par blocs, et surtout la **validation à origine glissante**. Les **combinaisons** de prévisions sont robustes.
> - Les modèles ne s'évaluent pas par l'AIC entre familles différentes, mais par la **prévision hors échantillon**, répétée.
> - Une prévision se publie avec ses **hypothèses** (promotions connues, pas de choc type COVID).


## 4.4 ➕ Pour aller plus loin : séries multivariées, cointégration et GARCH

> 🧭 **Section optionnelle.** Les sections 4.1 à 4.3 traitent **une** série à la fois et se suffisent à elles-mêmes. Ici, nous élargissons le cadre dans trois directions : **plusieurs séries qui s'influencent** (VAR), **des séries qui dérivent mais restent liées** (cointégration), et **une variabilité qui change dans le temps** (GARCH). Si vous cherchez l'essentiel, sautez à la section 4.5 ou aux exercices.

### 4.4.1 Plusieurs séries à la fois : le modèle VAR

Le chiffre d'affaires et le **nombre de commandes** sont deux séries liées. Un modèle **VAR** (*vector autoregression*) décrit chacune comme une combinaison du passé de *toutes* les séries. Pour deux séries $y_{1,t}$ et $y_{2,t}$, regroupées dans le vecteur $\mathbf y_t$, le VAR(1) s'écrit

$$\mathbf y_t=\mathbf c+A\,\mathbf y_{t-1}+\boldsymbol\varepsilon_t,\qquad A=\begin{pmatrix}a_{11}&a_{12}\\a_{21}&a_{22}\end{pmatrix}.$$

C'est un AR(1) où le coefficient $\varphi$ devient une **matrice**. Chaque ligne est une régression linéaire ordinaire (chapitre 1) de $y_{i,t}$ sur les deux retards : le coefficient $a_{12}$ dit combien le passé de la série 2 aide à prévoir la série 1, **au-delà** du passé de la série 1 elle-même.

> 📐 **Stationnarité d'un VAR(1).** Comme pour l'AR(1) ($|\varphi|<1$), la condition est que **toutes les valeurs propres de $A$ soient de module strictement inférieur à 1** (volume I, section 1.1.3 : une valeur propre mesure de combien la matrice étire une direction ; $A^k\to0$ si et seulement si ce facteur est inférieur à 1). Pour un VAR($p$), on applique la même condition à la « matrice compagne » du système.

> 💡 **Exemple à la main.** Soit $A=\begin{pmatrix}0{,}5&0{,}2\\0{,}1&0{,}4\end{pmatrix}$. Sa trace vaut $0{,}9$ et son déterminant $0{,}5\times0{,}4-0{,}2\times0{,}1=0{,}18$. Les valeurs propres sont solutions de $\lambda^2-0{,}9\lambda+0{,}18=0$, soit $\lambda=\frac{0{,}9\pm\sqrt{0{,}81-0{,}72}}2=\frac{0{,}9\pm0{,}3}2$, donc $0{,}6$ et $0{,}3$ : le système est stationnaire. Si un choc de 1 frappe la série 1 à la date 0, la réponse au pas $k$ est la première colonne de $A^k$ : $(1;0)$, puis $(0{,}5;\,0{,}1)$, puis $A^2\binom10=(0{,}27;\,0{,}09)$… C'est la **fonction de réponse impulsionnelle** : un choc sur une série se propage dans l'autre.


#### Un exemple : ventes et commandes

Le VAR suppose des séries **stationnaires**. Pour les rendre telles, on utilise l'idée de 4.2.7 : on retire de chaque série (en logarithme) sa **tendance, sa saison, la promotion et le COVID** par régression, et on garde l'**écart** — ce qui reste quand on a enlevé tout ce qu'on sait expliquer. Ces écarts sont stationnaires (nous le vérifions) et ce sont eux qui portent la dynamique conjointe. Nous utilisons les 96 mois d'apprentissage.


Les deux écarts sont stationnaires (tests ADF : p-valeurs de l'ordre de $10^{-7}$). Les critères (AIC, BIC) choisissent **un seul retard**. Voici l'estimation du VAR(1) (un seul appel ; `ecarts` contient les deux écarts) :

```python
from statsmodels.tsa.api import VAR
var1 = VAR(ecarts).fit(maxlags=1)          # chaque écart est régressé sur les retards des deux écarts
print(var1.params.round(3))
```
<!--sortie-->
```text
          e_ca   e_nb
const   -0.001 -0.005
L1.e_ca  0.520  0.675
L1.e_nb  0.026 -0.003
```

Lecture des coefficients : l'écart de chiffre d'affaires d'un mois influence celui du mois suivant (coefficient d'environ $0{,}52$, comme le AR(1) du modèle C), et il **prévoit aussi** l'écart du nombre de commandes ($\approx0{,}68$, p-valeur $\approx0{,}04$). L'effet inverse (commandes $\to$ chiffre d'affaires) est proche de zéro.

> 📐 **Causalité au sens de Granger.** On dit que $x$ *cause* $y$ **au sens de Granger** si le passé de $x$ améliore la prévision de $y$ au-delà de son propre passé ; on le teste par un test de Fisher sur les coefficients du retard de $x$ dans l'équation de $y$ (hypothèse nulle : ils sont tous nuls). Ici, le chiffre d'affaires « précède » le nombre de commandes ($F=4{,}41$, $p=0{,}037$), mais pas l'inverse ($F=0{,}81$, $p=0{,}37$) ; la figure ci-dessous montre les réponses impulsionnelles.


![Fonctions de réponse impulsionnelle du VAR(1) : un choc de 1 sur l'écart de chiffre d'affaires (à gauche) se transmet à l'écart de commandes avec un effet plus important, puis s'atténue ; un choc sur les commandes (à droite) a très peu d'effet sur le chiffre d'affaires.](figures/ch04-var-irf.png)

> ⚠️ **« Cause au sens de Granger » ne veut pas dire « cause ».** Le test dit seulement que le passé du chiffre d'affaires **aide à prévoir** le nombre de commandes. Ici, la raison est connue, puisque nous avons fabriqué les données : le nombre de commandes est tiré d'une loi de Poisson dont la moyenne est le chiffre d'affaires du mois divisé par 58 (le panier moyen). Le nombre de commandes est donc une **mesure bruitée** du chiffre d'affaires *du même mois* ; comme le chiffre d'affaires est lui-même autocorrélé, son passé aide à prévoir cette mesure, et un nombre de commandes passé n'apporte rien de plus sur le chiffre d'affaires futur que le chiffre d'affaires passé lui-même. Aucune « influence » ne passe d'un mois à l'autre : c'est de l'**information**, pas de la causalité. Pour parler de causalité, il faut un schéma d'étude, pas un test de précédence (chapitre 7).

### 4.4.2 Cointégration : des séries qui dérivent ensemble

Passons à un autre piège, plus dangereux. Deux séries qui montent toutes les deux **semblent** liées, même si elles n'ont rien à voir. Prenons deux marches aléatoires **indépendantes** (4.1.3), régressons l'une sur l'autre, et regardons ce que dit la régression du chapitre 1. Nous avons répété l'expérience 1 000 fois (figure ci-dessous) :


![À gauche, deux marches aléatoires indépendantes qui semblent évoluer ensemble. À droite, les statistiques t de la pente de 1 000 régressions de ce type : elles sont bien plus dispersées que la loi de Student, et une majorité franchit les seuils de ±1,96.](figures/ch04-regression-fallacieuse.png)

Résultat : près de **quatre régressions sur cinq** (76,9 %) déclarent « significatif » un lien qui n'existe pas (au lieu de 5 %), avec un $R^2$ moyen de 0,244 et une statistique de Durbin-Watson moyenne de 0,17, très basse (les résidus sont très autocorrélés). C'est la **régression fallacieuse** (Granger et Newbold, 1974) : quand les séries ne sont pas stationnaires, les p-valeurs de la régression sont **fausses** (les hypothèses du chapitre 1 ne tiennent plus). Règle de prudence : si le $R^2$ est supérieur à la statistique de Durbin-Watson, méfiez-vous.

Comment distinguer une vraie relation d'une illusion ? Par la **cointégration**. Deux séries non stationnaires (intégrées d'ordre 1) sont **cointégrées** s'il existe une combinaison linéaire $y_t-\beta x_t$ qui, elle, est **stationnaire** : les deux séries dérivent, mais **elles dérivent ensemble**, comme deux promeneurs liés par une corde élastique. Exemple plausible pour la boutique : un indice du coût des matières premières ($x_t$, une marche aléatoire) et le prix moyen de vente ($y_t$), qui suit le coût avec un écart temporaire. Nous les **simulons** : $x_t$ est une marche aléatoire, $y_t=2+1{,}5\,x_t+u_t$ avec $u_t$ un AR(1) de coefficient $0{,}6$.

La **méthode d'Engle et Granger** a deux temps : (1) on régresse $y$ sur $x$ ; (2) on teste la **racine unitaire des résidus** (ADF de 4.1.6, avec des seuils adaptés car les résidus sont estimés). S'ils sont stationnaires, il y a cointégration.


Avec `statsmodels`, le test tient en une ligne :

```python
from statsmodels.tsa.stattools import coint
stat, p, _ = coint(y_coint, x, trend="c")          # test d'Engle-Granger ; y_coint et x : les deux séries simulées
print(round(stat, 2), round(p, 3))
```
<!--sortie-->
```text
-4.54 0.001
```

Sur nos deux séries cointégrées, la statistique vaut $-4{,}54$ ($p=0{,}001$) ; pour une série indépendante de $x$, $-2{,}55$ ($p=0{,}26$). La régression de $y$ sur $x$ donne une constante de $2{,}118$ et une pente de $1{,}494$ (programmé : 2 et 1,5).

Pour la série cointégrée, le test rejette « pas de cointégration » (p-valeur proche de 0,001) et la pente estimée est très proche de 1,5 (les estimateurs de cointégration sont *super-convergents* : ils convergent à la vitesse $n$ au lieu de $\sqrt n$). Pour la série indépendante, le test ne rejette pas.

> 📐 **Le modèle à correction d'erreur.** Si $y_t-\beta x_t-c=u_t$ avec $u_t=\varphi u_{t-1}+e_t$ stationnaire ($|\varphi|<1$), alors en différenciant $y_t=\beta x_t+c+u_t$ : $\Delta y_t=\beta\,\Delta x_t+\Delta u_t=\beta\,\Delta x_t+(\varphi-1)\,u_{t-1}+e_t$. En remplaçant $u_{t-1}$ par l'**écart à l'équilibre** $y_{t-1}-\beta x_{t-1}-c$, on obtient
> $$\Delta y_t=\gamma\,\Delta x_t+\alpha\,(y_{t-1}-\beta x_{t-1}-c)+e_t,\qquad \gamma=\beta,\quad\alpha=\varphi-1<0.$$
> Le coefficient $\alpha$ est la **vitesse de rappel** : une fraction $|\alpha|=1-\varphi$ de l'écart à l'équilibre se résorbe à chaque période. Ici, on s'attend à $\alpha=-0{,}4$ et $\gamma=1{,}5$.


Les estimations sont proches de la théorie ($\hat\alpha\approx-0{,}42$ pour $-0{,}4$ ; $\hat\gamma\approx1{,}52$ pour $1{,}5$) : environ 40 % de l'écart entre le prix de vente et son équilibre se résorbent chaque période, et une hausse immédiate du coût se répercute presque un pour un (à 1,5) sur le prix.

### 4.4.3 Quand la variabilité change : le modèle GARCH

Les modèles précédents supposent que les chocs $\varepsilon_t$ ont une **variance constante**. Certaines séries violent cette hypothèse de façon flagrante : en finance, les rendements calmes alternent avec des périodes agitées (**clusters de volatilité**). C'est le cas, par exemple, d'un taux de change qui préoccupe la gérante quand elle paie un fournisseur étranger : la variation quotidienne du taux est difficile à prévoir **en moyenne**, mais ses variations *absolues* se regroupent.

> 🧭 **Les données de cette sous-section sont simulées** : un jeu de 1 500 « rendements quotidiens » (en %) tiré d'un modèle GARCH(1,1) à paramètres connus (graine 41). Nous n'avons pas de série réelle de taux de change hors ligne ; ce n'est donc **pas** un historique réel.

Le modèle **GARCH(1,1)** (Bollerslev, 1986) écrit le rendement $r_t=\mu+\varepsilon_t$, avec $\varepsilon_t=\sigma_tz_t$ ($z_t$ de loi $\mathcal N(0,1)$) et une variance qui **évolue** :

$$\sigma_t^2=\omega+\alpha\,\varepsilon_{t-1}^2+\beta\,\sigma_{t-1}^2.$$

Un gros choc hier ($\varepsilon_{t-1}^2$ grand) augmente la variance d'aujourd'hui (terme en $\alpha$) ; et la variance est persistante (terme en $\beta$).

> 📐 **Variance inconditionnelle.** Si $\alpha+\beta<1$, la variance moyenne à long terme existe : en prenant l'espérance de l'équation (avec $\mathbb E[\varepsilon_{t-1}^2]=\mathbb E[\sigma_{t-1}^2]=\sigma^2$), on obtient $\sigma^2=\omega+(\alpha+\beta)\sigma^2$, d'où $\sigma^2=\dfrac{\omega}{1-\alpha-\beta}$. La quantité $\alpha+\beta$ mesure la **persistance** de la volatilité.

> 💡 **Exemple à la main.** Avec $\omega=0{,}05$, $\alpha=0{,}10$, $\beta=0{,}85$ : la variance de long terme est $0{,}05/(1-0{,}95)=1$. Si hier le rendement s'est écarté de sa moyenne de $\varepsilon_{t-1}=3$ (un choc de 3 écarts-types) alors que la variance valait 1, la variance d'aujourd'hui sera $0{,}05+0{,}10\times9+0{,}85\times1=1{,}8$ : presque le double, d'un seul coup.


Les rendements eux-mêmes n'ont, par construction, **aucune** mémoire dans leur moyenne ; leurs **carrés** (la variance) en ont beaucoup : le test de Ljung-Box appliqué aux carrés, et le test ARCH-LM (qui régresse $\varepsilon_t^2$ sur ses retards), rejettent massivement l'hypothèse de variance constante (p-valeurs de l'ordre de $10^{-22}$ et $10^{-8}$) ; l'excès de kurtosis des rendements est modeste (0,25). Remarquez que le Ljung-Box appliqué aux rendements bruts rejette *aussi* faiblement (p-valeur d'environ 0,002) alors qu'il n'y a pas de mémoire en moyenne : ce test suppose une variance constante, et il est lui-même perturbé quand elle ne l'est pas. C'est une raison de plus de tester les carrés. Ajustons le GARCH(1,1) avec la bibliothèque `arch` :

```python
from arch import arch_model
fit = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1).fit(disp="off")      # r : les 1 500 rendements
```

```text
       programmé  estimé  erreur type
mu          0.02   0.010        0.024
omega       0.05   0.041        0.013
alpha       0.10   0.070        0.014
beta        0.85   0.891        0.020
```


Les estimations se rapprochent des vraies valeurs, avec des écarts de l'ordre de une à deux erreurs types ($\alpha$ est sous-estimé de deux erreurs types environ, $\beta$ surestimé d'autant : ils jouent des rôles voisins, comme $\varphi$ et $\theta$ en 4.2.3, et leurs erreurs se compensent). C'est la **persistance** $\alpha+\beta$ (0,961 pour 0,95) qui est bien estimée. Après ajustement, les résidus standardisés au carré n'ont plus de mémoire : le modèle a absorbé le regroupement de volatilité. La prévision de la variance **remonte lentement vers sa valeur de long terme** (d'environ 0,74 à un jour à 0,90 à vingt jours, pour une cible de 1,05) : comme la prévision d'un AR(1) (4.3.1) qui revient vers sa moyenne, mais lentement, car la persistance est proche de 1.


![Rendements simulés (en haut), avec des périodes calmes et agitées, et volatilité conditionnelle (en bas) : la volatilité programmée (gris) et celle estimée par le GARCH (orange) se superposent presque.](figures/ch04-garch.png)

> ⚠️ **Ce que le GARCH modélise, et ce qu'il ne modélise pas.** Il prévoit la **variance** (donc l'incertitude, les intervalles de prévision, le risque), pas le niveau. Il est fondamental en gestion du risque financier (le volume V y reviendra). Sa validité repose sur l'hypothèse de loi (ici normale) pour les $z_t$ ; sur des données réelles, les queues sont souvent plus épaisses, et on utilise une loi de Student.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercices 4.11 et 4.12.

> ✅ **À retenir.**
> - Un **VAR($p$)** régresse chaque série sur les retards de **toutes** les séries ; il est stationnaire si les valeurs propres de la matrice (compagne) sont de module $<1$ ; les **réponses impulsionnelles** suivent la propagation d'un choc.
> - La **causalité de Granger** est une précédence prédictive, **pas** une causalité.
> - La **régression entre séries non stationnaires est trompeuse** : environ quatre fois sur cinq, deux marches aléatoires indépendantes paraissent « significativement » liées. Méfiance quand $R^2>$ Durbin-Watson.
> - **Cointégration** : deux séries intégrées dont une combinaison est stationnaire ; test d'Engle-Granger ; le **modèle à correction d'erreur** a pour coefficient de rappel $\alpha=\varphi-1$.
> - **GARCH(1,1)** : $\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2+\beta\sigma_{t-1}^2$ ; variance de long terme $\omega/(1-\alpha-\beta)$ ; il modélise la volatilité qui se regroupe. Les rendements ont peu de mémoire, leurs **carrés** beaucoup.


## 4.5 ➕ Pour aller plus loin : modèles d'espace d'états et filtre de Kalman

> 🧭 **Section optionnelle.** Elle ne demande aucun prérequis nouveau (seulement le chapitre 1 de ce volume et la section 4.2), mais elle est plus abstraite que le reste du chapitre. Elle vaut le détour : les modèles ARIMA de 4.2 sont **un cas particulier** de ce cadre, et le **filtre de Kalman** que vous allez construire est l'algorithme qui a calculé, en coulisses, toutes les vraisemblances de `SARIMAX`.

### 4.5.1 L'idée : un état caché, des observations bruitées

La gérante voudrait connaître le **niveau réel** de ses ventes, c'est-à-dire ce que serait son chiffre d'affaires sans les accidents du mois (une grosse commande, un jour de pluie). Elle n'observe que le chiffre d'affaires du mois, qui est **le niveau réel plus du bruit**. Le niveau réel, lui, évolue lentement. C'est un problème à **deux niveaux** :

- une **équation d'observation** : ce que l'on mesure, $y_t=\mu_t+\varepsilon_t$, avec $\varepsilon_t\sim\mathcal N(0,\sigma_\varepsilon^2)$ ;
- une **équation d'état** : comment l'état caché évolue, $\mu_{t+1}=\mu_t+\eta_t$, avec $\eta_t\sim\mathcal N(0,\sigma_\eta^2)$.

C'est le **modèle de niveau local** (*local level*). Le niveau $\mu_t$ est une marche aléatoire (il dérive sans retour), que l'on n'observe qu'à travers le bruit $\varepsilon_t$. Tout le problème est de **reconstituer** $\mu_t$ à partir des $y_t$ : c'est le rôle du **filtre de Kalman**. L'idée se généralise à un état de plusieurs composantes (niveau, pente, saison, régression), et à des observations manquantes ; nous verrons les deux.

### 4.5.2 Le filtre de Kalman, à la main

À chaque date, le filtre maintient une **croyance** sur l'état : une loi normale $\mathcal N(a,P)$ dont $a$ est la meilleure estimation et $P$ l'incertitude. Il alterne deux gestes.

1. **Prédiction.** Entre deux dates, le niveau dérive : l'estimation ne bouge pas ($a_{t+1|t}=a_{t|t}$) mais l'incertitude grandit : $P_{t+1|t}=P_{t|t}+\sigma_\eta^2$.
2. **Mise à jour.** On observe $y_t$. L'**innovation** $v_t=y_t-a_{t|t-1}$ est la surprise (ce que l'on n'avait pas prévu). On corrige l'estimation d'une fraction $K_t$ de cette surprise :
$$a_{t|t}=a_{t|t-1}+K_t\,v_t,\qquad K_t=\frac{P_{t|t-1}}{P_{t|t-1}+\sigma_\varepsilon^2},\qquad P_{t|t}=(1-K_t)\,P_{t|t-1}.$$

Le coefficient $K_t$ s'appelle le **gain de Kalman**. Il vaut entre 0 et 1 et arbitre entre deux sources d'information : l'ancienne croyance (si elle est incertaine, $P$ grand, $K$ proche de 1 : on se fie à la mesure) et la mesure (si elle est bruyante, $\sigma_\varepsilon^2$ grand, $K$ proche de 0 : on se fie à l'ancienne croyance).

> 📐 **D'où vient la formule ?** C'est le calcul bayésien le plus simple : un a priori normal $\mathcal N(a,P)$ sur $\mu$, une mesure $y=\mu+\varepsilon$ avec $\varepsilon\sim\mathcal N(0,\sigma^2)$. La loi *a posteriori* de $\mu$ est normale, de précision (inverse de la variance) **égale à la somme des précisions** : $\dfrac1{P_{\text{post}}}=\dfrac1P+\dfrac1{\sigma^2}$, d'où $P_{\text{post}}=\dfrac{P\sigma^2}{P+\sigma^2}=(1-K)P$ ; et de moyenne égale à la **moyenne des deux informations pondérée par leur précision** : $a_{\text{post}}=\dfrac{a/P+y/\sigma^2}{1/P+1/\sigma^2}=a+K(y-a)$. Le filtre de Kalman est donc une mise à jour bayésienne répétée, avec une étape de « vieillissement » entre deux (nous reverrons ce principe au chapitre 6).

> 💡 **Exemple à la main.** Prenons $\sigma_\varepsilon^2=4$, $\sigma_\eta^2=1$, et une croyance initiale $\mathcal N(100,\,5)$ sur le niveau avant la première mesure. On observe $y_1=103$, $y_2=101$, $y_3=106$.
>
> **Date 1.** $a_{1|0}=100$, $P_{1|0}=5$. Variance de l'innovation : $F_1=P+\sigma_\varepsilon^2=9$. Gain $K_1=5/9=0{,}5556$. Surprise $v_1=103-100=3$. Donc $a_{1|1}=100+0{,}5556\times3=101{,}667$ et $P_{1|1}=5\times(1-0{,}5556)=2{,}222$.
> **Date 2.** Prédiction : $a_{2|1}=101{,}667$, $P_{2|1}=2{,}222+1=3{,}222$. $F_2=7{,}222$, $K_2=3{,}222/7{,}222=0{,}4462$. Surprise $v_2=101-101{,}667=-0{,}667$. Donc $a_{2|2}=101{,}667+0{,}4462\times(-0{,}667)=101{,}369$ et $P_{2|2}=3{,}222\times(1-0{,}4462)=1{,}785$.
> **Date 3.** $P_{3|2}=2{,}785$, $F_3=6{,}785$, $K_3=0{,}4104$, $v_3=106-101{,}369=4{,}631$, $a_{3|3}=101{,}369+0{,}4104\times4{,}631=103{,}270$, $P_{3|3}=1{,}642$.
>
> Observez deux choses : le gain **diminue** (0,56 puis 0,45 puis 0,41) à mesure que l'on en sait plus, et l'incertitude $P_{t|t}$ diminue aussi.

### 4.5.3 Le filtre de Kalman en numpy, et comparaison avec statsmodels

Le filtre complet pour le niveau local tient en une vingtaine de lignes (nous le programmons pas à pas dans l'application 4.2 du cahier). Il traite aussi les **observations manquantes** (une valeur `NaN`) : on ne fait alors **que la prédiction**, sans mise à jour, et l'incertitude grandit. À chaque étape, il cumule la **log-vraisemblance** gaussienne des innovations (c'est ce qu'optimisent les logiciels pour estimer les variances).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2 (le filtre de Kalman en numpy).


Le filtre écrit en numpy retrouve les valeurs calculées à la main (101,667 ; 101,369 ; 103,270) et celles de `statsmodels`, **à la quatrième décimale**, y compris la log-vraisemblance.

#### Estimer les variances

Dans la pratique, on ne connaît pas $\sigma_\varepsilon^2$ ni $\sigma_\eta^2$ : on les **estime par maximum de vraisemblance**. Sur un niveau local **simulé** de 200 points (variances programmées : 4 pour le bruit d'observation et 1 pour le niveau), l'estimation par maximum de vraisemblance donne $3{,}05$ (erreur type $0{,}45$) et $1{,}45$ (erreur type $0{,}38$).


> ⚠️ **Estimer deux variances est difficile.** Les estimations sont dans la bonne région (3,05 pour 4 et 1,45 pour 1) mais avec de **grandes erreurs types** (la variance d'observation est sous-estimée d'environ deux erreurs types) : à partir de la seule série, la part du « bruit de mesure » et celle de la « vraie dérive » du niveau sont difficiles à séparer, comme $\varphi$ et $\theta$ en 4.2.3. Seul le **rapport** $q=\sigma_\eta^2/\sigma_\varepsilon^2$ gouverne le comportement du filtre (nous le voyons ci-dessous), ce qui limite l'effet de cette incertitude sur les prévisions.

### 4.5.4 Régime permanent et lissage exponentiel

Quand le filtre a tourné assez longtemps, le gain $K_t$ **se stabilise** à une valeur $K_\infty$. Calculons-la pour $\sigma_\varepsilon^2=4$ et $\sigma_\eta^2=1$ : en régime permanent, la variance prédite $p=P_{t+1|t}$ vérifie $p=\dfrac{p\,\sigma_\varepsilon^2}{p+\sigma_\varepsilon^2}+\sigma_\eta^2$. En multipliant par $p+4$ : $p(p+4)=4p+(p+4)$, soit $p^2-p-4=0$, d'où $p=\dfrac{1+\sqrt{17}}2\approx2{,}562$ et $K_\infty=\dfrac p{p+4}\approx0{,}390$.

Or, une fois $K$ constant, la mise à jour devient $a_{t|t}=a_{t-1|t-1}+K\,(y_t-a_{t-1|t-1})=K\,y_t+(1-K)\,a_{t-1|t-1}$ : exactement le **lissage exponentiel simple** de paramètre $\alpha=K_\infty$ (la moyenne mobile exponentielle bien connue des prévisionnistes). Le lissage exponentiel est donc le filtre de Kalman d'un niveau local en régime permanent. Une vérification numérique sur la série simulée le confirme.


Le gain converge vers sa valeur théorique, et le lissage exponentiel avec $\alpha=0{,}39$ **est** le filtre de Kalman une fois le régime permanent atteint (écart de l'ordre de $10^{-7}$). Plus le niveau bouge vite par rapport au bruit ($q$ grand), plus $K_\infty$ est grand : le filtre « oublie » vite le passé.

### 4.5.5 Un modèle structurel pour les ventes de la boutique

L'intérêt des modèles d'espace d'états est de **mettre bout à bout** des composantes comprises : un niveau, une pente, une saison, des variables explicatives. C'est ce qu'on appelle un **modèle structurel**. Pour nos ventes (en logarithme, 96 mois d'apprentissage), prenons un niveau, une pente, une saison de période 12 et les variables `promo` et `covid`. Pour commencer, laissons la pente évoluer aléatoirement (le « *local linear trend* » classique) :


L'estimation donne une **variance de la pente égale à zéro** (`sigma2.trend` $=0{,}0000$ ; les autres variances valent $0{,}0014$ pour le bruit irrégulier et $0{,}0028$ pour le niveau) : les données disent que la pente est **constante**. Le modèle se simplifie alors en un niveau qui dérive à vitesse constante plus un bruit de niveau (en langage statsmodels : `level="rwdrift"`, une marche aléatoire avec dérive). Gardons ce modèle, plus simple, avec une saison **déterministe** (profil fixe) :

```python
mod_ss = UnobservedComponents(train, exog=Xtr, level="rwdrift", seasonal=12, stochastic_seasonal=False)
fit_ss = mod_ss.fit(disp=False, maxiter=300)
print(pd.Series(fit_ss.params, index=mod_ss.param_names).round(4).to_string())
```
<!--sortie-->
```text
sigma2.level    0.0054
beta.promo      0.1090
beta.covid     -0.5263
```


Les variances et les effets estimés sont ci-dessus ; sur les 24 mois de test, le modèle structurel a une erreur (RMSE en logarithme) de $0{,}082$ et un biais de $-0{,}036$ : cette erreur se situe entre celle du modèle B (0,074) et celle des modèles A et C (environ 0,10). Il estime que l'effet de la promotion vaut environ $+0{,}11$ et celui du COVID environ $-0{,}53$, des valeurs voisines de celles de 4.2. Voyons les composantes que l'on peut **lire** dans ce modèle : le niveau lissé (la « vraie » tendance, débarrassée de la saison et du bruit) et le profil saisonnier.


![À gauche : le logarithme du chiffre d'affaires (gris) et le niveau lissé par le filtre de Kalman (violet) qui en retire la saison et le bruit. À droite : le profil saisonnier estimé, avec le pic de décembre et le creux de janvier.](figures/ch04-structurel.png)

Le profil saisonnier estimé donne $+59\ \%$ en décembre et $-38\ \%$ en janvier par rapport au niveau.

### 4.5.6 Combler un trou : les données manquantes

Un atout décisif du filtre de Kalman est de traiter les **observations manquantes** sans bricolage : à une date sans mesure, il ne fait que prédire (l'incertitude grandit), et le **lissage** (qui utilise aussi l'avenir) reconstitue la valeur manquante avec son intervalle d'incertitude. Un cas réaliste : les registres de la gérante ont perdu les ventes de **mars à août 2022**. Nous effaçons ces six mois de la série d'apprentissage (nous connaissons les vraies valeurs, ce qui permet de vérifier), ajustons le modèle sur ce qui reste, puis **reconstituons** les mois manquants. Résultats (en logarithme du chiffre d'affaires), avec l'intervalle d'incertitude de Kalman et, pour comparer, deux méthodes sans modèle (interpolation linéaire, et « même mois l'an dernier » corrigé de la croissance annuelle) :

```text
            vrai (log)  Kalman  ± 1,96 se  interp. linéaire  an dernier + croiss.
mois                                                                             
2022-03-01       7.400   7.371      0.142             7.127                 7.491
2022-04-01       7.553   7.442      0.183             7.182                 7.553
2022-05-01       7.711   7.550      0.201             7.238                 7.706
2022-06-01       7.667   7.661      0.201             7.293                 7.881
2022-07-01       7.803   7.722      0.183             7.349                 7.909
2022-08-01       7.717   7.674      0.142             7.404                 7.701

RMSE de reconstitution (log) : Kalman = 0.089 | interpolation linéaire = 0.383 | an dernier corrigé = 0.104
mois réels dans l'intervalle à 95 % de Kalman : 6 sur 6
```

Le filtre reconstitue les six mois avec une erreur quadratique moyenne de 0,09 en logarithme (soit 9 %) et les six vraies valeurs tombent dans son intervalle à 95 %, plus large au milieu du trou (là où l'on est le plus loin des mesures). C'est bien mieux que l'**interpolation linéaire** (0,38), qui ignore la saison et lisse une bosse qui existe réellement. La comparaison avec la méthode « l'an dernier corrigé de la croissance » (0,10) est plus serrée : elle utilise déjà la saison, mais pas l'information des mois qui entourent le trou. Les écarts du filtre ne sont pas nuls : la plus grosse erreur, en mai, est d'environ 0,16.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.10.

> ✅ **À retenir.**
> - Un **modèle d'espace d'états** distingue un **état caché** (niveau, pente, saison…) qui évolue, et des **observations bruitées**. Les ARIMA en sont un cas particulier.
> - Le **filtre de Kalman** alterne **prédiction** (l'incertitude grandit) et **mise à jour** : $a\leftarrow a+K(y-a)$, avec le **gain** $K=P/(P+\sigma_\varepsilon^2)$ qui arbitre entre ancienne croyance et mesure. C'est une mise à jour bayésienne répétée.
> - Il fournit aussi la **log-vraisemblance** des données : c'est elle qui sert à estimer les paramètres (variances), dans `SARIMAX` comme dans `UnobservedComponents`.
> - En régime permanent, le filtre d'un niveau local **est** un lissage exponentiel de paramètre $\alpha=K_\infty$.
> - Les **modèles structurels** assemblent niveau, pente, saison et variables explicatives en composantes lisibles ; ici, l'estimation de la variance de la pente à zéro a simplifié le modèle.
> - Les **observations manquantes** se traitent naturellement (prédire sans mettre à jour, puis lisser), avec une incertitude honnête.


## 4.6 ➕ Pour aller plus loin : Prophet et les bibliothèques modernes de prévision

> 🧭 **Section optionnelle.** Elle répond à une question que se posent beaucoup de lecteurs : « Et les bibliothèques à la mode, qui font tout en trois lignes ? ». Réponse en trois temps : comprendre ce qu'elles font **vraiment** (4.6.1 et 4.6.2), les **évaluer honnêtement** comme les autres (4.6.3), et savoir où chercher la suite (4.6.4).

### 4.6.1 Prophet : l'idée

**Prophet** est une bibliothèque de prévision publiée par des ingénieurs de Facebook (Taylor et Letham, 2018), conçue pour des séries d'entreprise avec des saisons marquées, des jours fériés et des ruptures de tendance. Son modèle est **additif** :

$$y(t)=g(t)+s(t)+h(t)+\varepsilon_t,$$

avec **$g(t)$** une tendance **linéaire par morceaux** (la pente peut changer en quelques dates candidates, les *points de rupture*, avec une pénalisation qui évite que toutes les ruptures soient utilisées), **$s(t)$** une saisonnalité décrite par une **série de Fourier** (une somme de sinus et de cosinus de période 1 an : $\sum_k a_k\sin(2\pi kt/P)+b_k\cos(2\pi kt/P)$), et **$h(t)$** l'effet d'événements (jours fériés, promotions) ou de variables explicatives. L'ajustement est bayésien (les coefficients ont des lois a priori ; l'estimation se fait avec le logiciel Stan), et les intervalles de prévision sont obtenus par simulation.

Rien de magique donc : c'est une **régression linéaire** sur des variables bien construites (la tendance par morceaux, les termes de Fourier, les événements), assortie d'une pénalisation, exactement dans l'esprit du chapitre 1 (section 1.5 : la régularisation). Voici le code typique, tel qu'on le trouve dans la documentation de la bibliothèque :

```python
from prophet import Prophet

df = v.reset_index().rename(columns={"mois": "ds"})        # Prophet attend les colonnes « ds » (date) et « y »
df["y"] = np.log(df["ca"])
m = Prophet(yearly_seasonality=6, weekly_seasonality=False, daily_seasonality=False,
            changepoint_prior_scale=0.05)                   # nombre de termes de Fourier ; souplesse de la tendance
m.add_regressor("promo")
m.add_regressor("covid")
m.fit(df[df["ds"] < "2024-01-01"])
futur = m.make_future_dataframe(periods=24, freq="MS")
futur = futur.merge(df[["ds", "promo", "covid"]], on="ds")
prevision = m.predict(futur)                                # colonnes yhat, yhat_lower, yhat_upper, trend, yearly...
```

> ⚠️ **Ce bloc n'est pas exécuté.** La bibliothèque Prophet n'est pas installée dans l'environnement qui a produit ce livre (elle nécessite le compilateur Stan) : le code ci-dessus est donné **à titre d'illustration**, d'après la documentation ; les noms d'arguments peuvent différer selon la version, et vous devrez le vérifier chez vous. Les résultats chiffrés de cette section ne viennent **pas** de Prophet, mais du modèle équivalent écrit à la main ci-dessous.

### 4.6.2 Le même modèle, écrit à la main

Pour comprendre, le plus sûr est de **construire** le modèle. Nous ajustons, sur $\log(\text{ca})$ :

- une **tendance linéaire par morceaux** : $g(t)=k+a\,t+\sum_j\delta_j\max(0,\,t-s_j)$, où les $s_j$ sont 20 points de rupture candidats et chaque $\delta_j$ est le changement de pente en $s_j$. Les $\delta_j$ sont **pénalisés** (régression ridge, chapitre 1, section 1.5), de sorte que la pente ne change que si les données l'exigent ;
- une **saisonnalité de Fourier** à $K$ harmoniques : $s(t)=\sum_{k=1}^{K}[a_k\sin(2\pi k\,m/12)+b_k\cos(2\pi k\,m/12)]$, où $m$ est le numéro du mois ;
- les variables explicatives `promo` et `covid`.

C'est une régression linéaire pénalisée : les moindres carrés avec un terme $\lambda\sum\delta_j^2$. Deux réglages à choisir : le nombre $K$ d'harmoniques et la pénalité $\lambda$. Plutôt que de les fixer au hasard, on les **valide** : on apprend sur les 72 premiers mois de l'apprentissage et on évalue sur les 24 suivants (toujours dans la période d'apprentissage : le test de 2024-2025 reste intact). La grille testée croise 6 valeurs de $K$ et 5 valeurs de $\lambda$ ; elle retient $K=6$ et $\lambda=0{,}1$, avec une erreur de validation (RMSE en logarithme) de $0{,}090$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3 (écrire ce modèle pas à pas).


Lecture de la grille. Avec **peu d'harmoniques** ($K=1$ à $3$), la saison est trop lisse : une seule ondulation sinusoïdale ne peut pas reproduire le **pic étroit de décembre** et le creux de janvier, et l'erreur de validation est grande (de 0,18 à 0,39). Il en faut davantage : l'erreur chute pour $K=4$ puis atteint son minimum pour $K=6$. Or $K=6$ harmoniques sur des données mensuelles équivaut à **un effet libre pour chaque mois** (12 paramètres au total), comme les 11 indicatrices de 4.2.7 : c'est la limite du système. Sur des données quotidiennes, 10 harmoniques suffisent à décrire un profil annuel détaillé ; avec seulement 12 points par an, il ne reste rien à *lisser*.

Refaisons l'ajustement sur les 96 mois et prévoyons les 24 mois de test : l'erreur (RMSE en logarithme) est de $0{,}0801$, avec un biais de $+0{,}017$, pour $0{,}0679$ d'erreur d'ajustement sur l'apprentissage.


![Modèle de type Prophet écrit à la main : ajustement sur l'apprentissage (violet) et prévision des 24 mois de test (orange), comparés aux observations (gris puis bleu).](figures/ch04-fourier.png)

Le modèle fait presque aussi bien que le meilleur des modèles de 4.3 sur la fenêtre de test (RMSE de 0,080 contre 0,074 pour B, et mieux que A, C et le naïf avec dérive en log). Ce que fait Prophet, au fond, ce n'est pas de la magie : c'est cela, avec des a priori bayésiens, des intervalles simulés, et une interface qui évite d'écrire la matrice de dessin.

### 4.6.3 Évaluation honnête : tout le monde au même concours

Un nouveau venu doit passer **le même concours** que les autres, sans faveur. Nous ajoutons donc à la validation à origine glissante de 4.3.6 deux nouveaux concurrents : le **modèle de type Prophet** que nous venons de construire (avec les réglages $K$ et $\lambda$ retenus *sur l'apprentissage*), et le **modèle structurel** de 4.5.5. Même protocole que 4.3.6 (13 origines, 12 horizons) : on ajoute simplement deux séries de prévisions à celles de 4.3. Résultats, RMSE en logarithme :

```text
validation à origine glissante (13 origines, 12 horizons), RMSE en logarithme :
                                                RMSE global   h = 1  h = 12   biais
modèle                                                                             
type Prophet (Fourier + tendance par morceaux)       0.0665  0.0777  0.0673  0.0125
B : (1,0,0)(0,1,1) + tendance                        0.0670  0.0712  0.0889  0.0037
combinaison A+B+C                                    0.0687  0.0708  0.0808 -0.0295
A : SARIMAX(1,1,1)(0,1,1)                            0.0763  0.0737  0.0890 -0.0416
C : régression + AR(1)                               0.0807  0.0742  0.0903 -0.0506
naïf saisonnier + dérive                             0.0839  0.0753  0.1052 -0.0175
modèle structurel (niveau local + saison)            0.0996  0.0786  0.1022 -0.0066
naïf saisonnier                                      0.1081  0.1213  0.1264  0.0707
```

![Concours final à origine glissante : RMSE (en logarithme) de huit méthodes, avec en pointillé l'écart-type du bruit de la série estimé en 4.3.5. Les trois meilleures, dont le modèle de type Prophet, sont voisines et au niveau de ce bruit.](figures/ch04-concours.png)

Lecture honnête du tableau :

1. Le modèle de type Prophet, tel que nous l'avons écrit, arrive **en tête** du classement (RMSE de 0,0665), de très peu devant le modèle B (0,0670) : un écart bien inférieur à ce que 13 origines permettent de distinguer (4.3.5). Il est **dans le peloton de tête**, pas au-dessus.
2. Il y est parce que, pour des données mensuelles à saison nette, il se ramène à **« tendance linéaire par morceaux + effets de mois libres + régresseurs »**, une structure très proche de la vérité (le modèle C de 4.2.7 en est le cousin direct, sans changement de pente).
3. Le **modèle structurel**, très bon pour reconstituer des trous (4.5.6), fait ici **moins bien que la référence simple avec dérive** (0,0996 contre 0,0839) : son niveau en marche aléatoire « suit le bruit » et l'ancre sur des écarts qui s'effacent. Un bon outil pour une tâche (interpoler) n'est pas forcément le meilleur pour une autre (prévoir).
4. Les meilleurs modèles ont une erreur de 0,067 : entre l'écart-type des chocs mensuels (0,060, le minimum pour une prévision à un mois) et celui de l'écart à la tendance (0,0715, valeur à long terme). Ils font **à peu près ce que le bruit permet** : **plus de sophistication n'achète pas de précision** quand on est déjà proche de ce que les données permettent.

> ⚠️ **Mise en garde sur ce classement.** Il porte sur **une** série, **une** période de test, des réglages choisis par nous. Nous avons vu en 4.3.8 que le classement d'un jeu de test de deux ans peut s'inverser avec un autre tirage du hasard. Ne généralisez pas : un benchmark honnête (nombreuses séries, nombreuses origines, mêmes données pour tous) est un travail à part entière.

### 4.6.4 Les autres bibliothèques, et comment choisir

Voici un tour d'horizon, **sans exécution** ici (aucune de ces bibliothèques n'est installée dans l'environnement du livre) ; vérifiez la documentation de la version que vous utilisez.

| Bibliothèque | Idée | Quand l'utiliser |
|---|---|---|
| `statsmodels` (utilisée ici) | ARIMA, SARIMAX, espace d'états, ETS, VAR | comprendre, diagnostiquer, un petit nombre de séries |
| `statsforecast` | versions très rapides d'AutoARIMA, ETS, modèles naïfs | **des milliers de séries** à prévoir d'un coup |
| `sktime`, `darts` | interface unifiée (même syntaxe pour des dizaines de modèles), validation à origine glissante intégrée | comparer plusieurs familles de modèles proprement |
| `Prophet`, `NeuralProphet` | décomposition additive, événements, intervalles | séries d'entreprise à plusieurs saisons et jours fériés |
| modèles de fondation (par exemple Chronos, TimesFM) | grands réseaux pré-entraînés sur de nombreuses séries, utilisables sans ré-entraînement | prévision rapide « prête à l'emploi » à évaluer sur **vos** données |
| R : `forecast`, `fable` | `auto.arima`, `ets`, écosystème très complet | si votre équipe travaille en R |

Quelques principes pour choisir, tirés de ce chapitre :

- **Commencez par les références simples** (naïf saisonnier avec dérive) : elles sont le seuil à battre.
- **Comparez à origine glissante**, jamais sur un seul découpage, avec **le même protocole pour tous**.
- Une bibliothèque qui « fait tout en trois lignes » **cache** les choix (nombre d'harmoniques, flexibilité de la tendance, a priori) : sachez ce qu'elle fait (c'est le sens de 4.6.2).
- À précision comparable, **préférez le modèle que vous pouvez expliquer** : celui dont vous savez dire pourquoi il prévoit ce qu'il prévoit.

> ✅ **À retenir.**
> - **Prophet** est un modèle additif : tendance linéaire par morceaux + saisonnalité de Fourier + événements, ajusté par une régression pénalisée avec des a priori bayésiens. On peut l'écrire à la main avec une régression ridge.
> - Sur des données **mensuelles**, avec seulement 12 points par an, une saison nette demande beaucoup d'harmoniques ($K=6$ revient à un effet libre par mois).
> - Un nouveau modèle se juge **au même concours** que les autres (origine glissante, mêmes données). Sur notre série, le modèle de type Prophet, les modèles ARIMA et leur combinaison sont **tous proches de ce que le bruit permet** : la sophistication n'améliore pas ce que les données ne contiennent pas.
> - Choisissez en cascade : références simples, modèles statistiques compréhensibles, puis bibliothèques modernes ; et exigez toujours une évaluation honnête.


## Bilan du chapitre 4

Vous savez maintenant :

- **décrire** une série temporelle (tendance, saison, bruit, accident) et la **décomposer** (classique, STL robuste), en travaillant sur le **logarithme** quand la saison est proportionnelle au niveau ;
- définir la **stationnarité**, mesurer la mémoire par l'**autocorrélation** et l'**autocorrélation partielle**, tester le bruit blanc (**Ljung-Box**) et la racine unitaire (**ADF**, **KPSS**) en connaissant leurs limites (peu de puissance, loi de Dickey-Fuller non normale) ;
- distinguer **tendance déterministe** et **tendance stochastique**, et éviter la **sur-différenciation** ;
- construire des modèles **AR, MA, ARMA, ARIMA, SARIMA** et **SARIMAX**, connaître leurs conditions de stationnarité et d'inversibilité, suivre la méthode de **Box-Jenkins** (identification, estimation, diagnostic, prévision) et lire un diagnostic de résidus ;
- **prévoir** avec ses intervalles, passer du logarithme aux euros, et **évaluer honnêtement** : découpage temporel, références simples, MAE, RMSE, MAPE, **MASE**, bootstrap par blocs, **validation à origine glissante**, combinaison de prévisions ;
- comprendre qu'un seul jeu de test est **bruité** : le meilleur modèle en espérance ne gagne pas toujours (4.3.8) ;
- (en option) modéliser **plusieurs séries** (VAR, causalité de Granger, **cointégration**, régression fallacieuse), la **volatilité** (GARCH), les **modèles d'espace d'états** et le **filtre de Kalman** (lissage exponentiel, données manquantes), et situer **Prophet** et les bibliothèques modernes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.4 et exercices 4.1 à 4.13.

Le chapitre 5 change d'univers : il ne s'agit plus d'une série qui évolue **dans le temps calendaire**, mais d'un événement dont on mesure **la durée d'attente**, avec le défi particulier de la **censure** : combien de temps un client reste-t-il fidèle, quand certains sont encore clients aujourd'hui ?
