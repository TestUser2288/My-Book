# Chapitre 5 : Analyse de survie

> « La question n'est pas seulement *si* l'événement arrivera, mais *quand*, et ce que l'on peut dire des personnes qu'on n'a pas encore vues partir. »

La gérante a une inquiétude que tous les commerçants connaissent : **combien de temps un client reste-t-il fidèle ?** Elle sait que 49 % de ses 2 000 clients ont cessé d'acheter à la fin de 2025. Mais les autres ? Certains sont arrivés en 2019 et sont toujours là ; d'autres se sont inscrits il y a trois mois et n'ont tout simplement pas eu le temps de partir. Peut-on dire qu'ils « ne partiront jamais » ? Bien sûr que non : on ne sait pas encore. C'est un problème très particulier : **une partie de l'information est incomplète, et pourtant elle n'est pas sans valeur**, puisque savoir qu'un client est resté au moins 40 mois est un renseignement précieux.

L'**analyse de survie** (on dit aussi *analyse des durées*) est la branche de la statistique qui traite ce problème. Son nom vient de la médecine (durée de survie d'un patient), mais ses applications dépassent largement l'hôpital : durée de vie d'un client, d'un abonnement, d'une machine, délai avant un remboursement anticipé de crédit, durée d'un chômage, temps avant le premier sinistre d'une assurance…

> 🧭 **Ce que ce chapitre suppose.** Les chapitres 1 à 3 du volume I (surtout : lois de probabilité et loi exponentielle, estimation par maximum de vraisemblance, intervalles de confiance, tests, bootstrap) et le chapitre 2 de ce volume (modèles linéaires généralisés) pour l'idée de « modèle de régression avec une fonction de lien ». Aucune connaissance préalable en analyse de survie n'est nécessaire.

## Le chemin de ce chapitre

- **5.1 Censure et fonctions de survie** : pourquoi la moyenne ne marche pas, ce qu'est la censure, et les trois fonctions (survie, risque instantané, risque cumulé) qui décrivent une durée.
- **5.2 L'estimateur de Kaplan-Meier** : estimer la courbe de survie **sans hypothèse de forme**, avec son intervalle de confiance, et comparer des groupes (test du log-rank).
- **5.3 Le modèle de Cox à risques proportionnels** : une régression pour les durées, le modèle le plus utilisé de la discipline. Comment l'ajuster, l'interpréter, le vérifier.
- **5.4 Modèles de durée paramétriques** : exponentiel, Weibull, log-normal ; extrapoler au-delà des données et calculer la **valeur vie client**.
- ➕ **5.5 Pour aller plus loin : les risques concurrents** : quand plusieurs événements peuvent interrompre la durée et s'excluent mutuellement.
- **Bilan du chapitre.** Les applications guidées et les exercices corrigés sont dans le **cahier** (chapitre 5), auquel renvoient les encadrés 📒 de chaque section.

## Les données de ce chapitre

Nous utilisons le fichier `donnees/clients.csv`, déjà présenté en début de volume : 2 000 clients de la boutique inscrits entre janvier 2019 et juin 2025, observés jusqu'au **31 décembre 2025**. Quatre colonnes comptent ici :

| Colonne | Signification |
|---|---|
| `duree_mois` | durée pendant laquelle le client a été **observé** (en mois) |
| `churn` | **1** si le départ a été observé, **0** si le client était encore là à la fin de l'observation (durée *censurée*) |
| `offre_bienvenue` | 1 si le client a reçu une offre de bienvenue, 0 sinon, **attribuée au hasard** |
| `canal_acquisition`, `age` | canal par lequel le client est arrivé, âge à l'inscription |

> 📦 **Des données simulées.** Comme dans tout le volume, ces données sont **simulées** avec une graine fixe : nous connaissons donc la loi qui les a engendrées. Nous ne la révélerons qu'à la fin du chapitre (section 5.4.7), pour pouvoir vérifier ce que les méthodes retrouvent, et ce qu'elles retrouvent mal. Faites comme si la gérante ne la connaissait pas.

> 🧭 **Les outils.** Les estimateurs importants (Kaplan-Meier, log-rank, vraisemblance de Cox, maximum de vraisemblance paramétrique, incidences cumulées) ont été **écrits à la main** pour s'assurer de comprendre ce qu'ils calculent, puis comparés aux bibliothèques : `statsmodels` (`SurvfuncRight`, `survdiff`, `PHReg`), `lifelines` et le paquet R `survival`, qui est la référence de la discipline. Ces comparaisons ont été exécutées et leurs résultats sont cités dans le texte ; le code complet est dans le **cahier** (applications 5.1 à 5.6) et dans le fichier `build/outils_ch05.py`.


## 5.1 Censure et fonctions de survie

> 💡 **Intuition.** Une durée est un nombre comme un autre, sauf sur un point : **on n'a pas toujours le temps d'attendre la fin**. Quand l'étude s'arrête, certains clients sont encore là. Pour eux, on ne connaît pas la durée complète, mais on sait quelque chose de précieux : *elle dépasse celle observée*. Toute l'analyse de survie consiste à **utiliser cette information partielle sans la déformer**.

### 5.1.1 Un problème que la moyenne ne sait pas résoudre

Commençons petit, avec huit clients que la gérante a suivis dans son cahier. Pour chacun, elle a noté le nombre de mois pendant lesquels elle l'a observé, et si elle l'a vu **partir** (il n'a plus jamais commandé) ou s'il était **encore là** quand elle a fermé son cahier.

| Client | Mois observés | Situation |
|---|---|---|
| A | 3 | parti |
| B | 5 | parti |
| C | 6 | encore là (**censuré**) |
| D | 8 | parti |
| E | 10 | encore là (**censuré**) |
| F | 12 | parti |
| G | 14 | encore là (**censuré**) |
| H | 14 | encore là (**censuré**) |

Quelle est la durée de fidélité d'un client « typique » ? Trois réponses viennent naturellement, et **les trois sont fausses**.


- **(1) Tout moyenner.** C'est traiter C, E, G et H comme s'ils étaient partis à l'instant où l'on a cessé de les regarder. Or ils sont toujours là : leur vraie durée est **plus longue** que celle notée. La moyenne de 9 mois est donc **trop faible**.
- **(2) Ne garder que les clients partis.** On jette les censurés, comme s'ils n'avaient pas existé. Mais on jette précisément ceux qui **restent le plus longtemps**. On ne garde que les départs précoces : la moyenne de 7 mois est **encore plus faible**.
- **(3) Compter la proportion de départs.** La moitié des clients sont partis, mais cette proportion dépend uniquement de **la durée pendant laquelle on a regardé**. Avec un cahier fermé plus tard, la proportion serait plus grande ; elle ne mesure aucune propriété du client.

Le dessin rend la situation limpide. Chaque ligne est un client ; le trait s'arrête quand on cesse de l'observer ; le point plein marque un départ, le cercle vide un client **encore présent**, dont l'histoire continue hors du cadre.


![Huit clients suivis : un trait par client, un point plein pour un départ observé, un cercle vide et une flèche pour un client encore présent (durée censurée).](figures/ch05-clients-censures.png)

> ⚠️ **Une durée censurée n'est pas une donnée manquante.** On ne la supprime pas, et on ne la remplace pas par la durée observée. Elle dit : « *cette personne a survécu au moins jusque-là* ». C'est exactement l'information que les méthodes de ce chapitre exploitent.

**Mesurer l'erreur.** Avec huit clients, on ne peut pas savoir ce qui est « juste ». Faisons donc une **expérience contrôlée**, possible parce que nous simulons : nous créons 5 000 clients dont nous **connaissons les vraies durées** (une loi de Weibull, que nous définirons au 5.1.3), puis nous les « observons » en coupant l'étude à une date quelconque entre 6 et 60 mois après leur inscription (l'expérience est détaillée dans le cahier, application 5.1).


La vérité est de **33 mois** ; les deux moyennes naïves donnent environ 21,5 et 18,5, soit **un tiers à presque la moitié de moins**. Aucune ne converge vers la bonne valeur quand on ajoute des données : ce sont des **estimateurs biaisés**, au sens du volume I (section 3.2). Les méthodes du chapitre corrigent ce biais.

### 5.1.2 Le vocabulaire

Posons les notations, qui serviront jusqu'à la fin du chapitre. Pour chaque client $i$ :

- $T_i$ est la **durée vraie** (le temps entre l'**origine** et l'**événement**), généralement inconnue ;
- $C_i$ est la **durée de censure** : le temps entre l'origine et l'instant où l'on cesse d'observer ;
- ce que l'on **voit** est le couple $(Y_i, \delta_i)$ avec
$$Y_i=\min(T_i, C_i),\qquad \delta_i=\begin{cases}1&\text{si } T_i\le C_i\ \text{(événement observé)}\\0&\text{si } T_i> C_i\ \text{(censuré)}\end{cases}$$

Dans notre fichier, `duree_mois` est $Y$ et `churn` est $\delta$. Trois choix, souvent oubliés, définissent proprement une étude de survie :

1. **L'événement** : ici, « le client cesse d'acheter ». À définir précisément (dans le fichier simulé, la colonne est donnée ; dans la réalité, on décide, par exemple, « aucun achat depuis 6 mois »).
2. **L'origine du temps** : ici, la date d'inscription. Chaque client a *sa propre* horloge, qui démarre à *son* inscription ; c'est ce qui permet de comparer des clients arrivés à des dates différentes.
3. **L'unité** : le mois.

### 5.1.3 Trois fonctions pour décrire une durée

Soit $T$ une durée (positive) de fonction de répartition $F(t)=P(T\le t)$ et de densité $f(t)$. On définit trois objets, équivalents mais qui éclairent chacun un aspect différent.

**La fonction de survie.**
$$S(t)=P(T>t)=1-F(t)$$
C'est la proportion de clients encore là à l'instant $t$. Elle vaut 1 en $t=0$, décroît, et tend vers 0 (si tout le monde finit par partir).

**Le risque instantané** (en anglais *hazard*) :
$$h(t)=\lim_{\Delta t\to 0}\frac{P(t\le T<t+\Delta t\mid T\ge t)}{\Delta t}=\frac{f(t)}{S(t)}$$
C'est le **taux de départ, à l'instant $t$, parmi ceux qui sont encore là**. Ce n'est pas une probabilité (il peut dépasser 1, il se mesure « par mois ») : c'est une vitesse. Si $h(10)=0{,}03$ par mois, un client encore présent au dixième mois a environ 3 % de chances de partir dans le mois qui suit.

**Le risque cumulé** :
$$H(t)=\int_0^t h(u)\,du$$
C'est le « total de risque » accumulé depuis l'origine.

> 📐 **Les trois fonctions sont reliées : $S(t)=e^{-H(t)}$.** Partons de $f=-S'$, car $S=1-F$ et $F'=f$. Alors
> $$h(t)=\frac{f(t)}{S(t)}=-\frac{S'(t)}{S(t)}=-\frac{d}{dt}\ln S(t).$$
> Intégrons de 0 à $t$ en utilisant $S(0)=1$, donc $\ln S(0)=0$ :
> $$H(t)=\int_0^t h(u)\,du=-\ln S(t)+\ln S(0)=-\ln S(t),\qquad\text{d'où}\qquad S(t)=e^{-H(t)}.$$
> Connaître l'une des trois fonctions suffit donc à retrouver les deux autres : $f(t)=h(t)\,e^{-H(t)}$.

**Exemple à la main : le risque constant.** Supposons que, chaque mois, un client encore présent ait la même chance de partir : $h(t)=\lambda=0{,}03$ par mois. Alors $H(t)=0{,}03\,t$ et $S(t)=e^{-0{,}03t}$ : la loi **exponentielle** du volume I. Au bout de 12 mois, $S(12)=e^{-0{,}36}\approx0{,}698$ : 70 % des clients sont encore là. La médiane vérifie $S(t)=0{,}5$, soit $t=\ln 2/0{,}03\approx23{,}1$ mois. La moyenne vaut $1/\lambda\approx33{,}3$ mois.


Un risque constant a une propriété remarquable (et très restrictive) : la loi exponentielle est **sans mémoire**. Un client qui est là depuis 30 mois a *exactement* la même chance de partir le mois prochain qu'un client arrivé hier. Est-ce réaliste ? En pratique, rarement : les premiers mois d'une relation commerciale sont souvent les plus risqués (on essaie, on est déçu, on part), ou au contraire le risque augmente avec le temps (lassitude, usure). Il faut une famille plus souple.

**La loi de Weibull** généralise l'exponentielle avec un paramètre de **forme** $k>0$ et un paramètre d'**échelle** $\sigma>0$ :
$$h(t)=\frac{k}{\sigma}\Big(\frac t\sigma\Big)^{k-1},\qquad H(t)=\Big(\frac t\sigma\Big)^{k},\qquad S(t)=\exp\!\Big[-\Big(\frac t\sigma\Big)^{k}\Big].$$
Le risque est **décroissant** si $k<1$, **constant** si $k=1$ (c'est l'exponentielle, avec $\lambda=1/\sigma$), **croissant** si $k>1$. La médiane est $\sigma(\ln 2)^{1/k}$ et la moyenne $\sigma\,\Gamma(1+1/k)$.


![Quatre lois de Weibull de même échelle (36 mois) : à gauche le risque instantané, à droite la courbe de survie correspondante. Le pointillé marque la médiane (S = 0,5).](figures/ch05-formes-risque.png)

Remarquez que les quatre courbes de survie se croisent au même point, à $t=\sigma=36$ mois, où elles valent toutes $e^{-1}\approx0{,}37$ : c'est la conséquence de $S(\sigma)=\exp[-(\sigma/\sigma)^k]=e^{-1}$, quel que soit $k$. On lit ensuite l'effet de la forme : à échelle égale, un risque qui **monte** (k > 1) laisse presque tous les clients survivre au début puis les fait partir massivement plus tard, tandis qu'un risque qui **baisse** (k < 1) en élimine beaucoup tôt et laisse un noyau de fidèles.

> 📐 **La durée moyenne est l'aire sous la courbe de survie : $E[T]=\int_0^\infty S(t)\,dt$.** Pour le voir, écrivons $T=\int_0^\infty \mathbf 1_{\{T>t\}}\,dt$ (l'intégrale de la fonction qui vaut 1 tant que $t<T$ vaut $T$). L'espérance de l'intégrale est l'intégrale de l'espérance (théorème de Fubini, valable ici car tout est positif) :
> $$E[T]=\int_0^\infty E\big[\mathbf 1_{\{T>t\}}\big]\,dt=\int_0^\infty P(T>t)\,dt=\int_0^\infty S(t)\,dt.$$
> Cette formule sera notre boussole : estimer la durée moyenne, c'est estimer **l'aire sous la courbe de survie**.

Vérification numérique pour la Weibull ($k=1{,}35$, $\sigma=36$) : l'aire sous $S$ vaut 33,01 mois, exactement la valeur de la formule $\sigma\,\Gamma(1+1/k)$ ; la médiane est de $\sigma(\ln2)^{1/k}\approx27{,}4$ mois.


### 5.1.4 Les différentes sortes de censure

Nous avons parlé de censure « à droite » sans la définir précisément. Il en existe plusieurs sortes, qu'il faut savoir reconnaître car elles ne se traitent pas de la même façon.

| Type | Ce que l'on sait | Exemple pour la boutique |
|---|---|---|
| **À droite** | $T > c$ : l'événement n'a pas eu lieu à la fin de l'observation | un client inscrit en mars 2025, toujours actif en décembre |
| **À gauche** | $T < c$ : l'événement a *déjà* eu lieu avant la première observation | on découvre en 2025 qu'un client de la base n'a rien acheté depuis une date inconnue, avant l'étude |
| **Par intervalle** | $a < T \le b$ | une enquête annuelle : « le client est encore là en 2023, parti en 2024 » |

Ne confondez pas la censure avec la **troncature** (ou **entrée tardive**) : un client qui a rejoint le programme de fidélité en 2022 alors qu'il était client depuis 2018 n'est observé qu'à partir de 2022. Ceux qui sont partis *avant* 2022 n'apparaissent jamais dans la base. La censure, elle, conserve l'individu dans l'échantillon ; la troncature le fait **disparaître** s'il n'a pas « survécu jusqu'à l'entrée ». Il faut alors corriger les ensembles à risque (nous le ferons à la section 5.2 avec des entrées tardives). Dans notre fichier, tous les clients sont observés **dès leur inscription** : il n'y a pas de troncature, et la seule censure est à droite.

On distingue encore, pour la censure à droite :

- la censure **administrative** (type I) : l'étude s'arrête à une date fixée à l'avance, ici le 31 décembre 2025 ;
- la censure **aléatoire** : des individus sortent de l'étude pour une raison propre (déménagement, perte de contact, décès par une autre cause) ;
- la censure de **type II** : on arrête quand un nombre fixé d'événements est atteint (fréquent en essais industriels).

> 📐 **L'hypothèse de censure non informative.** Toute la théorie qui suit suppose que **la censure est indépendante de la durée** : savoir qu'un client est censuré à $c$ ne doit rien dire sur son risque de partir juste après $c$. Autrement dit, les clients encore sous observation au temps $c$ sont **représentatifs** de tous ceux qui seraient encore là à $c$. Pour la censure administrative, c'est plausible (la date du 31 décembre ne dépend pas des clients). Pour une perte de vue, c'est souvent **faux** : un client qui cesse de répondre est peut-être précisément en train de partir. Cette hypothèse n'est **pas testable** avec les seules données ; il faut la défendre par la connaissance du terrain.

Regardons ce que contient notre fichier : quelle part des durées censurées est purement administrative ?


Environ **deux tiers** des durées censurées (660 sur 1 023) sont purement administratives : ces clients sont encore là le 31 décembre 2025. Le tiers restant (363) est constitué de **pertes de vue** : des clients qui sortent de l'observation avant la fin sans que l'on ait vu de départ (changement d'adresse, compte clos par erreur, perte de contact...). Ce n'est donc pas un détail. La durée de suivi possible va de 6 mois (inscrits en juin 2025) à 84 mois (inscrits en janvier 2019).

Que faire de ces pertes de vue ? Nous les traiterons, comme le fait toute analyse standard, comme une censure **non informative**. Ici, c'est justifié par une raison que nous connaissons parce que nous simulons : elles sont indépendantes de la durée par construction. Dans une vraie étude, ce serait **une hypothèse à discuter** : si les clients « perdus de vue » étaient en réalité des clients qui partent sans prévenir, les traiter comme censurés *surestimerait* la survie. Une analyse de sensibilité classique consiste à les recompter comme des départs (le pire cas) pour encadrer la vérité.

### 5.1.5 La vraisemblance avec censure

Comment estimer des paramètres quand une partie des durées est censurée ? Par le **maximum de vraisemblance** (volume I, section 3.2), à condition d'écrire correctement la contribution de chaque client.

- Un client dont le départ est **observé** à $y_i$ apporte la densité $f(y_i)$ : « la durée est exactement $y_i$ ».
- Un client **censuré** à $y_i$ apporte $S(y_i)=P(T>y_i)$ : « la durée dépasse $y_i$ ».

La vraisemblance du paramètre $\theta$ de la loi de $T$ est donc, pour des durées indépendantes :
$$L(\theta)=\prod_{i=1}^{n} f(y_i;\theta)^{\delta_i}\;S(y_i;\theta)^{1-\delta_i}=\prod_{i=1}^n h(y_i;\theta)^{\delta_i}\,S(y_i;\theta),$$
puisque $f=h\,S$. En passant au logarithme et en utilisant $\ln S=-H$ :
$$\boxed{\ \ell(\theta)=\sum_{i=1}^n\Big[\delta_i\ln h(y_i;\theta)-H(y_i;\theta)\Big]\ }$$
La loi de la censure $C$ n'apparaît pas : sous l'hypothèse d'indépendance, elle ne dépend pas de $\theta$ et se factorise hors de la vraisemblance. C'est cette forme que nous utiliserons aux sections 5.3 (vraisemblance partielle de Cox) et 5.4 (modèles paramétriques).

**Premier calcul : le taux de départ constant.** Pour la loi exponentielle, $h=\lambda$ et $H(y)=\lambda y$ :
$$\ell(\lambda)=D\ln\lambda-\lambda\sum_i y_i,\qquad D=\sum_i\delta_i\ \text{(nombre de départs)}.$$
En dérivant, $\ell'(\lambda)=D/\lambda-\sum y_i=0$, donc
$$\hat\lambda=\frac{D}{\sum_i y_i}=\frac{\text{nombre de départs observés}}{\text{total des mois d'exposition}}.$$
Le dénominateur est l'**exposition**, en « mois-clients » : chaque client, parti ou censuré, contribue par **tout** le temps qu'il a passé sous observation. La dérivée seconde $-D/\lambda^2$ donne l'écart-type $\hat\lambda/\sqrt D$.

Sur nos huit clients : $D=4$ départs et $\sum y_i=3+5+6+8+10+12+14+14=72$ mois-clients, donc $\hat\lambda=4/72\approx0{,}056$ par mois. La durée moyenne estimée est $1/\hat\lambda=18$ mois et la médiane $18\ln2\approx12{,}5$ mois. Un optimiseur numérique retrouve le même $\hat\lambda$ pour les huit clients ; appliquons maintenant la formule aux 2 000 clients.


Sur les 2 000 clients : $D=977$ départs pour $46\,761$ mois-clients d'exposition, donc $\hat\lambda=0{,}0209$ par mois (IC95 : de 0,0196 à 0,0222), une durée moyenne estimée de $1/\hat\lambda=47{,}9$ mois et une médiane de $\ln2/\hat\lambda=33{,}2$ mois. Pour comparer, la moyenne naïve de toutes les durées vaut 23,4 mois.

L'estimation exponentielle donne environ 48 mois de durée moyenne, plus du double de la moyenne naïve (23 mois). Est-elle pour autant fiable ? Elle repose sur une hypothèse très forte : un risque **constant**. Si le vrai risque est croissant ou décroissant, l'estimation est biaisée. Il nous faut donc une méthode qui **ne suppose pas la forme du risque** : c'est l'objet de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 à 5.3.

> ✅ **À retenir**
> - Une durée est **censurée à droite** quand l'événement n'a pas eu lieu à la fin de l'observation : on sait seulement $T>y$. Ce n'est pas une donnée manquante.
> - Ni la moyenne de toutes les durées, ni celle des seuls événements, ni la proportion d'événements ne convergent vers la vraie durée moyenne : ces trois résumés sont **biaisés** par la censure.
> - Trois fonctions décrivent une durée : $S(t)=P(T>t)$, le risque instantané $h(t)=f/S$ et le risque cumulé $H(t)$, reliés par $S(t)=e^{-H(t)}$ ; et $E[T]=\int_0^\infty S(t)\,dt$.
> - La loi de Weibull offre un risque décroissant, constant ou croissant selon sa forme $k$ ; l'exponentielle est le cas $k=1$ (sans mémoire).
> - La vraisemblance avec censure est $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ ; pour un risque constant, $\hat\lambda=D/\sum y_i$ (événements par mois d'exposition).
> - Toute la théorie suppose une censure **non informative** (indépendante de la durée) : une hypothèse qui se défend, mais ne se teste pas.


## 5.2 L'estimateur de Kaplan-Meier

> 💡 **Intuition.** Pour savoir quelle part des clients est encore là au bout de 24 mois, on ne peut pas simplement compter ceux qui ont duré 24 mois : beaucoup de clients récents n'ont pas encore atteint cet âge. L'idée de Kaplan et Meier (1958) est de **découper le temps** : à chaque moment où quelqu'un part, on regarde *parmi ceux qui étaient encore sous observation à cet instant* quelle fraction est partie, et on **multiplie** les fractions de survie successives. Chaque client, censuré ou non, participe tant qu'il est observé, puis sort proprement du calcul.

### 5.2.1 Le principe, à la main

Reprenons nos huit clients (section 5.1.1). Les départs ont lieu aux mois 3, 5, 8 et 12. À chacun de ces instants, on se demande : *parmi les clients encore présents et observés juste avant, quelle fraction part ?*

- Mois 3 : les 8 clients sont là. Un part (A). La survie sur cet instant est $1-\tfrac18=\tfrac78=0{,}875$.
- Mois 5 : 7 clients sont là (A est parti). B part : $1-\tfrac17=\tfrac67$. La survie cumulée est $\tfrac78\times\tfrac67=0{,}75$.
- Mois 6 : C est **censuré**. Personne ne part. La courbe ne bouge pas, mais C **quitte l'ensemble à risque** : à partir de maintenant, il n'est plus compté.
- Mois 8 : il reste 5 clients (D, E, F, G, H). D part : $1-\tfrac15=\tfrac45$, survie cumulée $0{,}75\times0{,}8=0{,}6$.
- Mois 10 : E est censuré, sort de l'ensemble à risque.
- Mois 12 : il reste 3 clients (F, G, H). F part : $1-\tfrac13=\tfrac23$, survie cumulée $0{,}6\times\tfrac23=0{,}4$.
- Mois 14 : G et H sont censurés. Il n'y a plus d'autre départ : la courbe reste à 0,4.

Le nombre de clients sous observation juste avant l'instant $t_j$ s'appelle l'**ensemble à risque** (*risk set*), noté $n_j$. Le nombre de départs à $t_j$ est $d_j$. Voilà l'estimateur de Kaplan-Meier :

$$\boxed{\ \hat S(t)=\prod_{j:\,t_j\le t}\Big(1-\frac{d_j}{n_j}\Big)\ }$$

où le produit porte sur tous les instants $t_j\le t$ où au moins un départ a été observé. Les censures **n'apparaissent pas** dans la formule, mais elles agissent *indirectement* en réduisant $n_j$ : un client censuré à 6 mois compte dans les $n_j$ des instants antérieurs à 6 mois, mais plus ensuite.

Voici le même calcul, rangé dans un tableau (une ligne par instant de départ) :


| $t_j$ | $n_j$ (à risque) | $d_j$ (départs) | $d_j/n_j$ | $\hat S(t_j)$ | somme de Greenwood |
|---:|---:|---:|---:|---:|---:|
| 3 | 8 | 1 | 0,1250 | 0,875 | 0,0179 |
| 5 | 7 | 1 | 0,1429 | 0,750 | 0,0417 |
| 8 | 5 | 1 | 0,2000 | 0,600 | 0,0917 |
| 12 | 3 | 1 | 0,3333 | 0,400 | 0,2583 |


On retrouve les valeurs de la main : $0{,}875\to0{,}75\to0{,}6\to0{,}4$. La dernière colonne servira au 5.2.3.

> 📐 **Pourquoi cette formule, et pourquoi est-elle « la bonne » ?** Deux justifications.
>
> *Par les probabilités conditionnelles.* Découpons l'axe du temps en intervalles autour des instants de départ. Survivre au-delà de $t$ revient à survivre à chacun des instants de départ précédents *en ayant survécu aux précédents* :
> $$S(t)=\prod_{j:\,t_j\le t}P(T>t_j\mid T\ge t_j)=\prod_{j}(1-h_j),\qquad h_j=P(T=t_j\mid T\ge t_j).$$
> Le « risque discret » $h_j$ se lit directement dans les données : parmi les $n_j$ clients à risque, $d_j$ partent, d'où l'estimation naturelle $\hat h_j=d_j/n_j$.
>
> *Par le maximum de vraisemblance.* Supposons que la loi de $T$ ne charge que les instants observés, avec des risques $h_1,\dots,h_J$ libres. À l'instant $t_j$, parmi les $n_j$ clients à risque, $d_j$ partent (probabilité $h_j$ chacun) et $n_j-d_j$ restent (probabilité $1-h_j$). Les censures n'ajoutent aucun facteur en $h_j$ au-delà de leur participation aux $n_j$. La vraisemblance (section 5.1.5) est donc
> $$L(h_1,\dots,h_J)=\prod_{j=1}^J h_j^{d_j}(1-h_j)^{n_j-d_j}.$$
> Chaque facteur est une vraisemblance binomiale ; on le maximise séparément en $\hat h_j=d_j/n_j$. Kaplan-Meier est donc l'**estimateur du maximum de vraisemblance non paramétrique** de la fonction de survie : on ne suppose *aucune forme* pour $S$.

### 5.2.2 L'estimateur sur les 2 000 clients, comparé aux bibliothèques

Sur les 2 000 clients, le calcul est exactement le même ; son écriture efficace (vectorisée, avec prise en charge des **entrées tardives** dont nous aurons besoin au 5.2.6) est détaillée dans le cahier, application 5.2.


On trouve 882 instants de départ distincts pour 977 départs : comme les durées sont mesurées au centième de mois, 91 instants comptent plusieurs départs (les *ex aequo*), que la formule traite d'un seul bloc : $d_j>1$. Nous avons comparé ce calcul à `statsmodels` et au paquet R de référence, `survival`, à plusieurs instants.


Les trois sources donnent la même courbe et les mêmes erreurs standard (identiques à cinq décimales) :

| Mois | Clients à risque | Survie $\hat S(t)$ | Erreur standard | IC95 |
|---:|---:|---:|---:|---|
| 12 | 1 378 | 0,825 | 0,0089 | [0,808 ; 0,843] |
| 24 | 814 | 0,634 | 0,0121 | [0,610 ; 0,658] |
| 36 | 416 | 0,453 | 0,0140 | [0,426 ; 0,481] |
| 48 | 186 | 0,308 | 0,0150 | [0,280 ; 0,338] |
| 60 | 96 | 0,248 | 0,0156 | [0,219 ; 0,280] |

Lecture : **82,5 %** des clients sont encore là à 12 mois, **63,4 %** à 24 mois, **45,3 %** à 36 mois, et **24,8 %** à 60 mois. La colonne des clients à risque est instructive : à 60 mois, il ne reste que 96 clients sous observation, contre 1 378 à 12 mois. Ce sont les *clients récents*, sortis de l'ensemble à risque par censure, qui font fondre l'effectif.

Voyons maintenant la courbe. Nous y superposons le modèle **exponentiel** de la section 5.1.5 (risque constant, $\hat\lambda=0{,}0209$ par mois) pour juger de sa pertinence :


![Courbe de Kaplan-Meier des 2 000 clients de la boutique, avec son intervalle de confiance à 95 %, et courbe du modèle exponentiel ajusté par maximum de vraisemblance.](figures/ch05-km-global.png)

La courbe exponentielle passe **sous** Kaplan-Meier pendant les 28 premiers mois environ (elle prévoit trop de départs précoces), croise la courbe vers 30 mois, puis reste **au-dessus** ensuite (elle prévoit trop peu de départs tardifs). Ce schéma est la signature d'un risque qui **augmente** avec l'ancienneté : un risque constant ne peut pas le reproduire. La section 5.4 le confirmera. C'est un avantage décisif de Kaplan-Meier : il ne parie sur aucune forme.

### 5.2.3 Précision : la variance de Greenwood et les intervalles de confiance

Une courbe sans mesure d'incertitude est un dessin, pas un résultat. Que vaut $\hat S(t)$ ? Reprenons le raisonnement binomial.

> 📐 **La formule de Greenwood.** À l'instant $t_j$, parmi $n_j$ clients à risque, la fraction qui survit est $\hat p_j=1-d_j/n_j$. Conditionnellement à $n_j$, $d_j$ est binomial : $\mathrm{Var}(\hat p_j)\approx p_j(1-p_j)/n_j$. Comme $\ln\hat S(t)=\sum_j\ln\hat p_j$, la **méthode delta** (qui approche la variance d'une fonction régulière $g$ d'une quantité aléatoire : $\mathrm{Var}\,g(X)\approx g'(E[X])^2\,\mathrm{Var}\,X$) donne
> $$\mathrm{Var}(\ln\hat p_j)\approx\frac{\mathrm{Var}(\hat p_j)}{p_j^2}=\frac{1-p_j}{n_jp_j}\approx\frac{d_j}{n_j(n_j-d_j)}.$$
> Les facteurs des différents instants sont (conditionnellement) non corrélés, donc les variances s'additionnent :
> $$\mathrm{Var}\big(\ln\hat S(t)\big)\approx\sum_{j:\,t_j\le t}\frac{d_j}{n_j(n_j-d_j)},\qquad\mathrm{Var}\big(\hat S(t)\big)\approx\hat S(t)^2\sum_{j:\,t_j\le t}\frac{d_j}{n_j(n_j-d_j)}.$$
> C'est la **formule de Greenwood** : la dernière colonne de notre tableau (la « somme Greenwood ») en est la somme partielle.

Sur nos huit clients à $t=12$ : $\hat S=0{,}4$ et la somme vaut $0{,}2583$, donc l'écart-type est $0{,}4\sqrt{0{,}2583}\approx0{,}20$ : énorme, ce qui n'a rien d'étonnant avec huit clients.

Pour un intervalle de confiance, on peut prendre $\hat S\pm1{,}96\,\widehat{se}$ (intervalle **plan**), mais il peut sortir de $[0,1]$ et se comporte mal quand $\hat S$ est proche de 0 ou de 1. On préfère transformer d'abord :

- **intervalle « log »** (le défaut de R) : $\hat S\,\exp\!\big(\pm1{,}96\sqrt{G(t)}\big)$, avec $G(t)=\sum d_j/[n_j(n_j-d_j)]$ ;
- **intervalle « log-log »**, souvent recommandé : on travaille sur $\ln(-\ln\hat S)$, dont la variance est $G(t)/(\ln\hat S)^2$, ce qui donne $\hat S^{\,\exp(\pm1{,}96\sqrt{G(t)}/|\ln\hat S|)}$ (les bornes restent toujours dans $[0,1]$).


À 36 mois ($\hat S=0{,}4528$), les trois intervalles sont :

| Intervalle | Borne basse | Borne haute |
|---|---:|---:|
| plan | 0,4254 | 0,4801 |
| log | 0,4262 | 0,4810 |
| log-log | 0,4252 | 0,4799 |

Ils coïncident avec ceux de R à la quatrième décimale. Sur 2 000 clients, ils sont presque identiques ; la différence se voit sur les petits effectifs : avec les huit clients, l'intervalle plan est large (de presque 0 à 0,80), et le log-log est plus raisonnable. Ces intervalles s'interprètent comme au volume I (section 3.3.2) : la *méthode* encadre la vraie valeur dans 95 % des échantillons.

### 5.2.4 Médiane, quantiles et durée moyenne « restreinte »

**La médiane de survie** est le premier instant où la courbe passe sous 0,5. C'est le bon résumé de la « durée typique » : contrairement à la moyenne, elle est définie dès que la courbe descend sous 0,5, même si certains clients ne sont jamais partis. Son intervalle de confiance s'obtient en cherchant où la **bande de confiance** de la courbe coupe le niveau 0,5 (méthode de Brookmeyer et Crowley).


Avec la bibliothèque, tout tient en deux lignes (`c` est le tableau des clients) :

```python
from statsmodels.duration.survfunc import SurvfuncRight

km = SurvfuncRight(c["duree_mois"], c["churn"])        # estimateur de Kaplan-Meier
print(f"médiane de survie : {km.quantile(0.5):.2f} mois")
```
<!--sortie-->
```text
médiane de survie : 32.45 mois
```


La médiane est d'environ **32,5 mois** (IC95 : 29,9 à 34,2). La moitié des clients ont quitté la boutique au bout de deux ans et huit mois et demi. Notez que ce chiffre est bien supérieur à la moyenne « naïve » de 23 mois de la section 5.1.

**Et la durée moyenne ?** Nous savons que $E[T]=\int_0^\infty S(t)\,dt$. Mais Kaplan-Meier ne descend pas jusqu'à zéro : le dernier client est censuré, et la courbe s'arrête à 0,11 (dernier départ au mois 80,2). L'aire totale n'est pas définie ; elle dépend de ce que l'on suppose *au-delà* des données. On calcule donc la **durée moyenne restreinte** (en anglais *restricted mean survival time*, RMST) jusqu'à un horizon $\tau$ choisi :
$$\mathrm{RMST}(\tau)=\int_0^{\tau}\hat S(t)\,dt.$$
C'est le **nombre moyen de mois passés dans la clientèle pendant les $\tau$ premiers mois**. Comme $\hat S$ est une fonction en escalier, l'intégrale est une somme de rectangles. À la main, pour nos huit clients et $\tau=14$ : $3\times1+2\times0{,}875+3\times0{,}75+4\times0{,}6+2\times0{,}4=3+1{,}75+2{,}25+2{,}4+0{,}8=10{,}2$ mois. (Ni 9 mois ni 7 mois : on a bien utilisé l'information des censurés.)


Sur 24 mois, un nouveau client passe en moyenne 19,8 mois dans la clientèle de la boutique ; sur 36 mois, un peu plus de 26 mois (sur un maximum possible de 36) ; sur 60 mois, 33,9 mois. C'est une quantité très parlante pour décider (nous la retrouverons au 5.4 pour la valeur vie client), et elle ne dépend d'aucune hypothèse de forme.

### 5.2.5 Comparer des groupes : courbes et test du log-rank

La gérante a envoyé une **offre de bienvenue** à la moitié de ses clients, **tirée au hasard**. Cette offre prolonge-t-elle la relation ? Et le canal d'acquisition joue-t-il un rôle ? Traçons Kaplan-Meier par groupe, avec les bandes de confiance log-log.


![Courbes de Kaplan-Meier par groupe, avec bandes de confiance à 95 % : à gauche selon l'offre de bienvenue, à droite selon le canal d'acquisition.](figures/ch05-km-groupes.png)

Les courbes avec et sans offre se séparent nettement et durablement ; à droite, Boutique est au-dessus de Site, lui-même au-dessus de Réseaux (les bandes de Boutique et de Site se chevauchent par endroits). Résumons chaque groupe (médiane de survie et durée moyenne restreinte à 36 mois) :


| Variable | Groupe | Clients | Départs | Médiane (mois) | Durée moyenne restreinte à 36 mois |
|---|---|---:|---:|---:|---:|
| Offre de bienvenue | sans offre | 985 | 528 | 28,2 | 24,62 |
| | avec offre | 1 015 | 449 | 36,6 | 27,69 |
| Canal d'acquisition | Boutique | 504 | 212 | 41,2 | 29,10 |
| | Réseaux | 816 | 443 | 26,4 | 23,93 |
| | Site | 680 | 322 | 34,1 | 26,67 |


Les chiffres sont éloquents : sans offre, la médiane est de 28 mois ; avec l'offre, de près de 37. Mais est-ce un vrai effet ou le hasard de l'échantillonnage ? Il faut un **test**.

**Le test du log-rank.** C'est le test de référence pour comparer deux courbes de survie (ou plus). Son principe est celui du volume I (section 3.4), appliqué *à chaque instant de départ* : à l'instant $t_j$, $d_j$ départs ont lieu parmi $n_j$ clients à risque, dont $n_{1j}$ dans le groupe 1. Si les deux groupes avaient **le même risque** (hypothèse nulle), les $d_j$ départs seraient répartis « au hasard » entre les clients à risque, et le nombre de départs dans le groupe 1 suivrait une loi **hypergéométrique** :
$$E_{1j}=d_j\frac{n_{1j}}{n_j},\qquad V_j=d_j\,\frac{n_{1j}}{n_j}\Big(1-\frac{n_{1j}}{n_j}\Big)\frac{n_j-d_j}{n_j-1}.$$
On additionne, sur tous les instants, les écarts entre départs observés $O_1$ et attendus $E_1=\sum_jE_{1j}$ :
$$\chi^2=\frac{(O_1-E_1)^2}{\sum_jV_j}\ \approx\ \chi^2_1\quad\text{sous }H_0.$$
Pour $K$ groupes, on utilise la forme quadratique du vecteur $(O_k-E_k)_{k<K}$ avec la matrice de covariance correspondante : $\chi^2_{K-1}$.

**À la main, sur les huit clients.** Imaginons que C, E, F et G aient reçu l'offre, et A, B, D et H non. Aux quatre instants de départ :

| $t_j$ | $n_j$ | $n_{1j}$ (avec offre) | $d_j$ | qui part | $E_{1j}=d_jn_{1j}/n_j$ | $V_j$ |
|---|---|---|---|---|---|---|
| 3 | 8 | 4 | 1 | A (sans offre) | 0,500 | 0,250 |
| 5 | 7 | 4 | 1 | B (sans offre) | 0,571 | 0,245 |
| 8 | 5 | 3 | 1 | D (sans offre) | 0,600 | 0,240 |
| 12 | 3 | 2 | 1 | F (avec offre) | 0,667 | 0,222 |

Le groupe « avec offre » a eu $O_1=1$ départ pour $E_1=2{,}338$ attendus ; $\sum V_j=0{,}957$ ; $\chi^2=(1-2{,}338)^2/0{,}957=1{,}87$, soit $p\approx0{,}17$ : avec huit clients, aucune conclusion, évidemment. La formule se généralise à $K$ groupes (le code est dans le cahier, application 5.3).


Appliquons maintenant le test aux données réelles (nous l'avons calculé à la main, avec `statsmodels` et avec R : les trois résultats coïncident).


Les trois calculs donnent $\chi^2\approx35{,}5$ ($p\approx3\times10^{-9}$) : dans le groupe avec offre, on observe 449 départs là où l'on en attendrait 541 si l'offre ne changeait rien ; dans le groupe sans offre, 528 au lieu de 436. L'offre étant attribuée **au hasard**, la différence peut être lue comme **l'effet causal de l'offre** sur la durée de la relation (nous reviendrons sur la mesure de cet effet au 5.3).

Pour le canal d'acquisition (trois groupes, $\chi^2_2$) puis les comparaisons deux à deux, avec la correction de **Holm** du volume I (section 3.5.5).


Les trois canaux diffèrent ($\chi^2_2=55{,}0$). Deux à deux, toutes les comparaisons restent significatives après correction de Holm : la plus nette oppose Boutique et Réseaux (p de l'ordre de $10^{-12}$), la plus faible Boutique et Site (p $\approx9\times10^{-4}$). Les clients arrivés par la boutique restent le plus longtemps, ceux d'Réseaux partent le plus vite : 212 départs observés en Boutique contre 296 attendus sous l'hypothèse « aucune différence », mais 443 contre 342 pour Réseaux.

**Autres pondérations.** Le log-rank donne le **même poids** à tous les instants ; il est le plus puissant quand les risques des groupes sont **proportionnels** (section 5.3). D'autres tests pondèrent davantage le début (Gehan-Breslow, Tarone-Ware, Fleming-Harrington) ; ils sont plus sensibles aux différences précoces et moins aux différences tardives.


Sur l'offre de bienvenue, les quatre tests donnent $\chi^2=35{,}5$ (log-rank), $31{,}5$ (Gehan-Breslow), $35{,}1$ (Tarone-Ware) et $35{,}0$ (Fleming-Harrington, que R retrouve avec `rho = 1`) : toutes les pondérations concluent de la même façon. Quand elles divergent, c'est un signal qu'**il se passe quelque chose de différent selon l'âge de la relation** (par exemple des courbes qui se croisent) : on regarde alors les courbes plutôt que de choisir le test qui nous arrange.

> ⚠️ **Le choix du test ne se fait pas après avoir vu les résultats.** Décidez de la pondération *avant* (par défaut, le log-rank). Essayer plusieurs tests et ne retenir que le meilleur est un cas de tests multiples (volume I, section 3.5.5).

### 5.2.6 Quand les clients entrent tard : la troncature à gauche

Nous avons promis (5.1.4) de montrer comment traiter les **entrées tardives**. Imaginons que la gérante n'ait enregistré les clients qu'à partir de leur **adhésion au programme de fidélité**, qui peut intervenir longtemps après le premier achat. On mesure la durée depuis le premier achat, mais un client n'apparaît dans la base que s'il était **encore client** à sa date d'adhésion. Les clients partis avant n'ont jamais été vus.

La règle est simple : **un client n'est dans l'ensemble à risque à l'instant $t$ que s'il est entré dans l'observation avant $t$ et n'en est pas encore sorti** :
$$n_j=\#\{i:\ e_i<t_j\le y_i\}.$$
Ignorer cette règle (prendre $e_i=0$ pour tout le monde) revient à compter, dans les ensembles à risque des premiers mois, des clients qui *n'étaient pas encore observables* ; on sous-estime le risque précoce et on **surestime la survie**. Nous l'avons vérifié par simulation, avec une vérité connue : 6 000 clients dont les durées suivent une loi de Weibull, n'entrant dans la base qu'à leur adhésion (uniforme entre 0 et 30 mois après le premier achat) ; la simulation est reprise dans le cahier, application 5.3.


Les estimations qui **ignorent** l'entrée surestiment fortement la survie : 0,76 au lieu de 0,56 à 24 mois, par exemple. Celles qui **la prennent en compte** (à la main comme avec `statsmodels`, qui donnent exactement les mêmes valeurs) restent à environ deux points de la vérité à tous les horizons. Cet exemple n'est pas qu'académique : il explique pourquoi l'on dit que **la survie d'« ex-clients encore actifs » ou de patients « prévalents » est toujours plus belle que la réalité**.

### 5.2.7 Pièges et analyses de sensibilité

> ⚠️ **La queue de la courbe est fragile.** Quand l'ensemble à risque devient petit (ici : moins de 100 clients au-delà de 60 mois, 7 avant le dernier départ), un seul départ fait chuter la courbe de plusieurs points. On présente toujours sous la courbe le **nombre de clients à risque** et on arrête l'interprétation là où il devient trop faible.


| Clients à risque | 0 mois | 12 mois | 24 mois | 36 mois | 48 mois | 60 mois | 72 mois |
|---|---:|---:|---:|---:|---:|---:|---:|
| sans offre | 985 | 647 | 359 | 179 | 70 | 29 | 13 |
| avec offre | 1 015 | 731 | 455 | 237 | 116 | 67 | 24 |


> ⚠️ **La censure non informative est une hypothèse, pas un fait.** À la section 5.1.4, nous avons vu que 363 clients sont des *pertes de vue*. Et si, en réalité, tous étaient partis sans prévenir ? Une **analyse de sensibilité du pire cas** consiste à les recompter comme des départs, à la date où l'on les perd de vue : la vraie courbe se trouve alors entre les deux.


À 36 mois, la survie est de **45 %** sous l'hypothèse standard et de **34 %** dans le pire cas : l'incertitude liée à nos 363 pertes de vue pèse onze points, bien plus que l'incertitude statistique (l'intervalle à 95 % mesurait moins de trois points de demi-largeur). La vraie survie se situe entre les deux ; elle est plus proche de la première si les pertes de vue sont réellement indépendantes du risque de départ, ce qui est le cas dans notre simulation. Et la **conclusion sur l'offre** survit à l'épreuve : le test du log-rank reste très significatif même dans le pire cas (dernière ligne : $\chi^2=27{,}4$ contre 35,5), ce qui est cohérent avec le fait que, dans notre simulation, les pertes de vue ne dépendent pas de l'offre. Ce genre de vérification est précieux : il sépare les résultats **robustes** (la conclusion ne bouge pas) des chiffres **fragiles** (le niveau de survie, lui, dépend de l'hypothèse).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.2 et 5.3, exercices 5.4 à 5.6.

> ✅ **À retenir**
> - **Kaplan-Meier** : $\hat S(t)=\prod_{t_j\le t}(1-d_j/n_j)$, où $n_j$ est l'ensemble à risque (les censurés y restent jusqu'à leur censure, puis en sortent). C'est l'estimateur du maximum de vraisemblance **non paramétrique**.
> - **Greenwood** : $\mathrm{Var}\,\hat S\approx\hat S^2\sum d_j/[n_j(n_j-d_j)]$ ; on préfère les intervalles **log-log**, qui restent dans $[0,1]$.
> - La **médiane** se lit sur la courbe ; la **durée moyenne** n'est pas définie si la courbe ne descend pas à 0, d'où la **RMST** (aire jusqu'à un horizon $\tau$).
> - Le **log-rank** compare les groupes en cumulant, instant par instant, départs observés et attendus sous $H_0$ ; il est le plus puissant sous risques proportionnels.
> - Une **entrée tardive** impose de n'inclure un client dans l'ensemble à risque qu'**après** son entrée ; l'oublier surestime la survie.
> - La queue de la courbe est fragile (peu de clients à risque), et la censure non informative est une hypothèse qu'on peut éprouver par une analyse de sensibilité.


## 5.3 Le modèle de Cox à risques proportionnels

> 💡 **Intuition.** Kaplan-Meier sait comparer deux ou trois groupes, mais pas dire *« à canal et à offre égaux, que change un an de plus d'âge ? »*. Il faut un modèle de **régression**. David Cox (1972) a eu l'idée géniale de modéliser le **risque instantané** plutôt que la durée, en ne supposant que ceci : le risque d'un client est le risque d'un client « de référence », multiplié par un facteur qui dépend de ses caractéristiques, **le même à tout âge de la relation**. La forme du risque de référence reste libre, ce qui rend le modèle très robuste. Et miracle : on peut estimer les facteurs *sans jamais estimer ce risque de référence*.

### 5.3.1 Le modèle

Pour un client de caractéristiques $x=(x_1,\dots,x_p)$, le **modèle de Cox** s'écrit
$$\boxed{\ h(t\mid x)=h_0(t)\,\exp(\beta_1x_1+\dots+\beta_px_p)=h_0(t)\,e^{x^\top\beta}\ }$$
- $h_0(t)$ est le **risque de base** : le risque d'un client dont toutes les caractéristiques valent 0. **On ne lui impose aucune forme** : c'est la partie « non paramétrique » du modèle. Le modèle est donc dit **semi-paramétrique**.
- $e^{x^\top\beta}$ est le **facteur multiplicatif** : il ne dépend pas de $t$.

**Comment lire un coefficient.** Prenons deux clients identiques sauf pour la variable $x_j$, qui vaut $a+1$ pour l'un et $a$ pour l'autre. Le rapport de leurs risques est
$$\frac{h(t\mid x_j=a+1)}{h(t\mid x_j=a)}=\frac{h_0(t)\,e^{\beta_j(a+1)+\dots}}{h_0(t)\,e^{\beta_ja+\dots}}=e^{\beta_j}.$$
Le terme $h_0(t)$ s'est **simplifié** : ce rapport ne dépend pas de $t$. C'est le **rapport de risques** (en anglais *hazard ratio*, HR) :

- $\mathrm{HR}=e^{\beta_j}<1$ : la variable **réduit** le risque de partir à tout instant (protectrice) ;
- $\mathrm{HR}>1$ : elle l'**augmente** ;
- $\mathrm{HR}=1$ ($\beta_j=0$) : aucun effet.

**Exemple chiffré.** Si $\mathrm{HR}=0{,}67$ pour l'offre de bienvenue, cela signifie : *à n'importe quel âge de la relation, parmi deux clients identiques encore là, celui qui a eu l'offre a un risque instantané de partir égal à 67 % de celui qui ne l'a pas eu*, soit un risque réduit d'un tiers.

> ⚠️ **Un rapport de risques n'est pas un rapport de probabilités.** « Le risque est réduit d'un tiers » ne veut pas dire « un tiers de départs en moins sur 3 ans » : le risque instantané et la proportion cumulée de départs sont deux choses différentes. C'est la **courbe de survie** (section 5.3.7) qui traduit le HR en pourcentages de clients conservés.

### 5.3.2 La vraisemblance partielle : estimer $\beta$ sans connaître $h_0$

Comment estimer $\beta$ si $h_0(t)$ est inconnue ? L'idée de Cox est d'utiliser un **argument conditionnel**, que l'on comprend sur un exemple.

Reprenons nos huit clients (section 5.1.1) et supposons que C, E, F et G aient reçu l'offre ($x=1$) et A, B, D, H non ($x=0$). À l'instant $t=3$, **un** départ a lieu, et les huit clients sont à risque. *Sachant qu'un départ a lieu à cet instant*, quelle est la probabilité que ce soit A ? Chaque client $k$ à risque a un risque $h_0(3)e^{\beta x_k}$ : la probabilité que ce soit A est sa part du risque total,
$$\frac{h_0(3)\,e^{\beta x_A}}{\sum_{k\in\text{à risque}}h_0(3)\,e^{\beta x_k}}=\frac{e^{\beta x_A}}{\sum_{k\in\text{à risque}}e^{\beta x_k}}.$$
**Le risque de base $h_0(3)$ s'est simplifié**, en haut comme en bas ! Il en est de même à chaque instant de départ. En multipliant ces probabilités conditionnelles sur tous les départs, on obtient la **vraisemblance partielle** de Cox :
$$\boxed{\ L_p(\beta)=\prod_{i:\ \delta_i=1}\frac{e^{x_i^\top\beta}}{\sum_{k\in R_i}e^{x_k^\top\beta}}\ }\qquad\ell_p(\beta)=\sum_{i:\ \delta_i=1}\Big[x_i^\top\beta-\ln\sum_{k\in R_i}e^{x_k^\top\beta}\Big]$$
où $R_i$ est l'**ensemble à risque** à l'instant du départ du client $i$ (ceux encore sous observation juste avant). Les clients censurés n'ont pas de facteur propre, mais ils figurent dans les ensembles à risque tant qu'ils sont observés.

À la main, pour nos huit clients (en notant $u=e^\beta$) :

| Départ | $t$ | Ensemble à risque | Facteur de $L_p$ |
|---|---|---|---|
| A ($x=0$) | 3 | A à H : 4 avec offre, 4 sans | $\dfrac{1}{4+4u}$ |
| B ($x=0$) | 5 | B, C, D, E, F, G, H : 4 avec, 3 sans | $\dfrac{1}{3+4u}$ |
| D ($x=0$) | 8 | D, E, F, G, H : 3 avec, 2 sans | $\dfrac{1}{2+3u}$ |
| F ($x=1$) | 12 | F, G, H : 2 avec, 1 sans | $\dfrac{u}{1+2u}$ |

D'où $\ell_p(\beta)=-\ln(4+4u)-\ln(3+4u)-\ln(2+3u)+\beta-\ln(1+2u)$. Où est son maximum ? Pour le trouver, on dérive. Le **score** et l'**information** ont une interprétation simple (cas d'une seule variable) :
$$U(\beta)=\ell_p'(\beta)=\sum_{i:\,\delta_i=1}\big[x_i-\bar x_{R_i}(\beta)\big],\qquad I(\beta)=-\ell_p''(\beta)=\sum_{i:\,\delta_i=1}\mathrm{Var}_{R_i}(x;\beta),$$
où $\bar x_{R_i}(\beta)=\sum_{k\in R_i}x_ke^{\beta x_k}/\sum_{k\in R_i}e^{\beta x_k}$ est la **moyenne pondérée** de $x$ dans l'ensemble à risque (les poids sont les risques relatifs $e^{\beta x_k}$), et $\mathrm{Var}_{R_i}$ la variance pondérée correspondante. Le score compare, à chaque départ, la valeur de $x$ du client parti à la valeur « attendue » : si ceux qui partent ont systématiquement un $x$ plus grand que la moyenne de ceux qui restent, $\beta$ doit être positif. C'est ce qu'on appelle les **résidus de Schoenfeld** $x_i-\bar x_{R_i}$, que nous retrouverons au 5.3.5.


Trois enseignements.

1. **La méthode de Newton** converge en quatre itérations (le cinquième chiffre décimal ne bouge plus ensuite) vers $\hat\beta\approx-1{,}46$, donc $\widehat{\mathrm{HR}}=e^{-1{,}46}\approx0{,}23$ : l'offre semblerait diviser le risque par quatre. Mais ce n'est qu'un exemple jouet à huit clients ; l'erreur standard est de $1/\sqrt{I}\approx1{,}16$, de sorte qu'un intervalle de confiance irait de $e^{-1{,}46-1{,}96\times1{,}16}\approx0{,}02$ à $e^{-1{,}46+1{,}96\times1{,}16}\approx2{,}3$.
2. La statistique de score en $\beta=0$ vaut exactement $1{,}87$ : c'est **le chi-deux du test du log-rank** de la section 5.2.5.
3. Ce n'est pas un hasard.

> 📐 **Le test du log-rank est le test de score du modèle de Cox.** En $\beta=0$, $e^{\beta x_k}=1$ pour tous : la moyenne pondérée $\bar x_{R_i}(0)$ est la **proportion de clients du groupe 1** dans l'ensemble à risque ($n_{1j}/n_j$), et le score vaut $\sum_j(d_{1j}-d_jn_{1j}/n_j)=O_1-E_1$. L'information est la variance de la loi hypergéométrique. Autrement dit, tester $H_0:\beta=0$ par le score revient à calculer le log-rank. Le test du log-rank est donc exactement ce que « donne » le modèle de Cox lorsqu'on n'a que la variable de groupe.


![Log-vraisemblance partielle de Cox pour les huit clients, en fonction du coefficient β de l'offre : le maximum se trouve à β ≈ −1,46 et la courbe est très plate autour, signe d'une grande incertitude.](figures/ch05-cox-vraisemblance.png)

La courbe est **plate** autour de son maximum : beaucoup de valeurs de $\beta$ sont presque aussi vraisemblables. C'est la traduction graphique de l'erreur standard élevée.

### 5.3.3 Ajuster le modèle sur les 2 000 clients

Pour plusieurs variables, les mêmes formules s'écrivent avec des vecteurs : le score est $U(\beta)=\sum_i[x_i-\bar x_{R_i}]$ (un vecteur) et l'information $I(\beta)$ est la matrice (variances et covariances pondérées dans les ensembles à risque). L'estimateur $\hat\beta$ est asymptotiquement normal de matrice de covariance $I(\hat\beta)^{-1}$, comme tout estimateur du maximum de vraisemblance (volume I, section 3.2).

Nous avons écrit à la main cet estimateur (le code, vectorisé, est dans le cahier, application 5.4) : il maximise la vraisemblance partielle et traite les départs simultanés (*ex aequo*) par la correction de **Breslow** (voir 5.3.4). Voici le résultat sur les 2 000 clients, la catégorie de référence du canal étant la boutique :


| Variable | Coefficient | Erreur standard | Rapport de risques | IC95 du rapport | $p$ |
|---|---:|---:|---:|---|---|
| offre de bienvenue | −0,4061 | 0,0645 | 0,666 | [0,587 ; 0,756] | < 0,001 |
| âge (par année) | −0,0136 | 0,0030 | 0,987 | [0,981 ; 0,992] | < 0,001 |
| canal Réseaux (réf. Boutique) | 0,6351 | 0,0842 | 1,887 | [1,600 ; 2,226] | < 0,001 |
| canal Site (réf. Boutique) | 0,3258 | 0,0887 | 1,385 | [1,164 ; 1,648] | 0,0002 |


Nous avons vérifié ces valeurs avec `statsmodels` (`PHReg`) et avec **R** (`coxph`), la référence.


Les trois calculs coïncident à la cinquième décimale. En pratique, un appel de bibliothèque suffit :

```python
from statsmodels.duration.hazard_regression import PHReg

cox_sm = PHReg(y, X, status=d, ties="efron").fit()   # y : durées, d : départ observé, X : offre, âge, canal
print(np.exp(cox_sm.params).round(3))               # rapports de risques (offre, âge, Réseaux, Site)
```
<!--sortie-->
```text
[0.666 0.986 1.887 1.385]
```

Lisons le tableau.

- **Offre de bienvenue** : $\widehat{\mathrm{HR}}\approx0{,}67$ (IC95 : de 0,59 à 0,76). À âge et canal égaux, l'offre réduit le risque de départ d'environ **un tiers**, à n'importe quel âge de la relation. Comme l'offre est **attribuée au hasard**, l'interprétation causale est licite ; l'intervalle exclut nettement 1.
- **Âge** : $\widehat{\mathrm{HR}}\approx0{,}986$ **par année** : chaque année d'âge de plus réduit le risque d'environ 1,4 %. Pour parler à la gérante, on exprime l'effet par tranche : *dix ans de plus* correspondent à $\mathrm{HR}=e^{10\hat\beta}$, soit environ $0{,}87$ (IC95 : de 0,82 à 0,93).
- **Canal** : par rapport à la boutique (référence), un client arrivé par **Réseaux** a un risque environ **1,9 fois plus élevé** et un client arrivé par le **site**, environ **1,4 fois**. C'est cohérent avec les courbes de la section 5.2.


> 💡 **Les trois tests classiques.** Pour un modèle de maximum de vraisemblance, on peut tester $H_0:\beta=0$ de trois façons : par le **rapport de vraisemblance** (comparer $\ell_p(\hat\beta)$ à $\ell_p(0)$), par le test de **Wald** ($\hat\beta^\top I\hat\beta$, valeur de $z^2$ pour un seul coefficient), ou par le test de **score** (évaluer le score en $\beta=0$ : c'est le log-rank). Ils sont équivalents asymptotiquement et donnent ici des conclusions identiques ; Ici : rapport de vraisemblance $112{,}0$, Wald $110{,}3$, score $111{,}8$, tous à 4 degrés de liberté ($p<10^{-22}$). R affiche les trois.

### 5.3.4 Les ex aequo : Breslow, Efron et les autres

Si deux clients partent exactement au même instant, la vraisemblance partielle ne dit pas dans quel ordre : les facteurs de la formule ne sont plus bien définis. Trois approches :

- **Breslow** : on traite tous les ex aequo comme si l'ensemble à risque était *le même* pour chacun (celui d'avant l'instant). Simple, mais approximative quand les ex aequo sont nombreux. C'est ce que nous avons codé.
- **Efron** : on retire progressivement les clients partis simultanément de l'ensemble à risque, en moyenne. Plus précise ; c'est le **défaut de R** (`coxph`) et de `lifelines`.
- **Exacte** : on somme sur tous les ordres possibles. Précise mais coûteuse quand les ex aequo sont nombreux.

Dans nos données, mesurées au centième de mois, il y a peu d'ex aequo (91 instants sur 882 comportent plusieurs départs) ; la différence est **négligeable** : le coefficient de l'offre vaut $-0{,}40616$ avec Efron et $-0{,}40612$ avec Breslow.


Mais voyons ce qui se passe quand on **arrondit** les durées au mois supérieur, comme le ferait une base de données qui ne stocke que des mois entiers : les ex aequo deviennent massifs.


Après arrondi, les 977 départs se répartissent sur seulement 75 instants (une douzaine d'ex aequo par instant en moyenne). Breslow tire alors chaque coefficient **vers zéro** (son coefficient est plus petit en valeur absolue que celui d'Efron, de l'ordre de 1 % ici : $-0{,}403$ contre $-0{,}408$ pour l'offre), alors que sans arrondi, les deux méthodes étaient confondues à la quatrième décimale. L'écart reste modeste parce que les ex aequo sont, ici, une petite fraction de chaque ensemble à risque (quelques dizaines sur plusieurs centaines) ; il deviendrait important si la fraction de clients partant à chaque instant était grande. La règle pratique : **utilisez Efron par défaut**.

### 5.3.5 Vérifier l'hypothèse : les risques sont-ils vraiment proportionnels ?

Tout le modèle repose sur *un seul* pari : l'effet d'une variable est **le même à tout âge de la relation**. L'offre de bienvenue divise-t-elle le risque par 0,67 aussi bien le premier mois que la troisième année ? Si ce n'est pas le cas, le coefficient estimé n'est qu'une **moyenne**, potentiellement trompeuse. Il faut **vérifier**.

**(a) Le graphique log-log.** Si les risques sont proportionnels, $H(t\mid x)=H_0(t)e^{x^\top\beta}$, donc $\ln\big(-\ln S(t\mid x)\big)=\ln H_0(t)+x^\top\beta$ : en traçant $\ln(-\ln\hat S)$ contre $\ln t$ pour plusieurs groupes, on doit obtenir des courbes **parallèles** (décalées de $x^\top\beta$).

**(b) Les résidus de Schoenfeld.** Le résidu du client $i$ parti à $t_i$ est $r_i=x_i-\bar x_{R_i}(\hat\beta)$ (5.3.2). Si l'effet de $x_j$ était constant, ces résidus n'auraient aucune tendance en fonction du temps. S'ils croissent avec $t$, l'effet réel de $x_j$ augmente avec le temps ; s'ils décroissent, il diminue. Grambsch et Therneau transforment cette idée en **test de score** : on ajoute au modèle un terme $\theta_j\,x_j\,g(t)$ où $g$ est une fonction du temps (ici, le **rang** de la durée), et l'on teste $\theta_j=0$ au point $(\hat\beta,\ \theta=0)$. Les trois ingrédients se calculent avec les mêmes sommes que précédemment : le score $U_{\theta_j}=\sum_ig(t_i)\,r_{ij}$, et la matrice d'information du modèle étendu.


| Variable | $\chi^2$ | $p$ |
|---|---:|---:|
| offre de bienvenue | 0,56 | 0,45 |
| âge | 0,73 | 0,39 |
| canal Réseaux | 2,21 | 0,14 |
| canal Site | 0,01 | 0,90 |
| **global** (4 ddl) | 4,95 | 0,29 |


Notre test à la main et `cox.zph` de R donnent les **mêmes** statistiques. Aucune p-valeur n'est petite : la proportionnalité des risques est **plausible**. Ce n'est pas une surprise : les données ont été simulées avec un modèle de Weibull, qui est à risques proportionnels (nous le démontrerons au 5.4).

Que se passe-t-il quand l'hypothèse est **fausse** ? Simulons deux groupes de 750 clients : dans le groupe A, le risque de partir **diminue** avec le temps (Weibull de forme 0,8) ; dans le groupe B, il **augmente** (forme 1,8). Leurs risques se croisent.


Le HR global (0,73) est une moyenne qui ne décrit **aucune période réelle** : le groupe B est bien plus protégé au début (HR $\approx0{,}43$ sur les 25 premiers mois), puis devient moins bon que A (HR $\approx2{,}2$ ensuite). Le test de proportionnalité le détecte immédiatement ($\chi^2$ très grand). Visualisons-le, avec les deux graphiques (courbes de survie qui se croisent ; graphique log-log) :


![À gauche : graphique log-log des trois canaux de la boutique (courbes presque parallèles). Au centre et à droite : deux groupes simulés dont les risques se croisent (courbes de survie qui se coupent, courbes log-log non parallèles).](figures/ch05-cox-loglog.png)

**Que faire quand les risques ne sont pas proportionnels ?** Plusieurs remèdes, du plus simple au plus fin :

1. **Stratifier** sur la variable fautive : chaque strate (par exemple chaque canal) a son propre risque de base $h_{0s}(t)$, mais les autres coefficients sont communs. On n'obtient plus de coefficient pour la variable de stratification, mais on se libère de l'hypothèse pour elle.
2. **Estimer un effet qui change avec le temps** : $\beta_j(t)=\beta_j+\theta_jg(t)$, ou un coefficient différent par période (comme ci-dessus).
3. **Changer de résumé** : comparer des durées moyennes restreintes (5.2.4), qui n'exigent pas la proportionnalité.


Les coefficients de l'offre et de l'âge changent peu (offre : $-0{,}407$ avec stratification, $-0{,}395$ sans) ; la différence vient surtout de ce que le canal, facteur important du risque, est omis dans le second modèle.

> ⚠️ **Un test non significatif ne prouve pas la proportionnalité.** Avec peu de données, le test manque de puissance ; avec beaucoup, il détecte des écarts sans importance pratique. Combinez le test avec le **graphique**, et posez-vous la question du **mécanisme** : est-il plausible qu'une offre de bienvenue ait le même effet relatif au premier mois et à la cinquième année ?

### 5.3.6 Variables qui changent avec le temps, et le piège de l'« immortalité »

Jusqu'ici, chaque variable était fixée à l'inscription. Mais certaines évoluent : un client reçoit une carte de fidélité au mois 12, passe à un abonnement premium au mois 20, etc. Le modèle de Cox accepte des **covariables dépendant du temps** $x(t)$ ; on les représente en découpant la vie du client en **épisodes** $(\text{début},\text{fin}]$ sur chacun desquels la covariable est constante : c'est le format **« processus de comptage »**.

| Client | Épisode | début | fin | carte de fidélité | départ à la fin de l'épisode ? |
|---|---|---|---|---|---|
| Z (a eu la carte au mois 12, parti au mois 30) | 1 | 0 | 12 | 0 | non |
| | 2 | 12 | 30 | 1 | oui |
| W (jamais de carte, parti au mois 8) | 1 | 0 | 8 | 0 | oui |

Dans la vraisemblance partielle, à chaque instant de départ, un client est à risque **avec la valeur de sa covariable à cet instant-là**. La date de début de l'épisode joue le rôle d'une **entrée tardive** (comme en 5.2.6).

> ⚠️ **Le biais d'immortalité.** Voici l'erreur la plus fréquente, et la plus trompeuse. La gérante veut savoir si la **carte de fidélité** (remise aux clients encore là au mois 12) réduit les départs. Elle crée une colonne « a la carte » = 1 pour tous ceux qui l'ont **un jour** reçue, et ajuste un modèle de Cox. Problème : pour avoir la carte, il fallait **être encore client au mois 12**. Les porteurs de carte ont donc, par construction, **survécu 12 mois** : ils sont « immortels » pendant cette période. La variable prédit le futur depuis le passé.

Simulons une situation où la carte n'a **strictement aucun effet** (le risque de tout le monde est constant, 3 % par mois) et comparons deux analyses.


L'analyse naïve « découvre » que la carte divise le risque par plus de deux (HR ≈ 0,46) alors qu'elle n'a **aucun effet** ; l'analyse correcte trouve un HR proche de 1, avec un intervalle de confiance qui contient 1. Cette erreur est célèbre (elle a faussé des études médicales entières, par exemple sur les bénéfices d'un traitement reçu « un jour »). **Règle** : toute variable dont la valeur n'est connue qu'*après* un certain temps de survie doit être traitée comme dépendant du temps.

### 5.3.7 Prédire : la courbe de survie d'un client donné

Le risque de base $h_0$ a disparu de la vraisemblance, mais on peut l'estimer *après coup*. Pour un client de profil $x$, $S(t\mid x)=\exp\big(-H_0(t)\,e^{x^\top\beta}\big)$, où le **risque cumulé de base** $H_0(t)$ est estimé par l'**estimateur de Breslow** :
$$\hat H_0(t)=\sum_{j:\,t_j\le t}\frac{d_j}{\sum_{k\in R_j}e^{x_k^\top\hat\beta}}.$$
C'est une version « pondérée » de l'estimateur de Nelson-Aalen $\sum d_j/n_j$ (si $\beta=0$, les deux coïncident). Chaque saut est le nombre de départs divisé par la **somme des risques relatifs** des clients à risque.


| Profil | 12 mois | 24 mois | 36 mois | 60 mois |
|---|---:|---:|---:|---:|
| A : Réseaux, 25 ans, sans offre | 0,711 | 0,438 | 0,230 | 0,069 |
| B : Réseaux, 25 ans, avec offre | 0,797 | 0,577 | 0,375 | 0,168 |
| C : Boutique, 45 ans, avec offre | 0,912 | 0,801 | 0,673 | 0,487 |


Les prédictions à la main et celles de R sont identiques. Elles se traduisent en pourcentages de clients : un client arrivé par Réseaux à 25 ans **sans offre** a environ 44 % de chances d'être encore là à 24 mois, contre 58 % **avec** l'offre ; un client de 45 ans arrivé par la boutique avec l'offre : 80 %. Dessinons ces courbes :


![Courbes de survie prédites par le modèle de Cox pour trois profils de clients de la boutique.](figures/ch05-cox-profils.png)

### 5.3.8 Le modèle sépare-t-il bien les clients ? L'indice de concordance

Un modèle de survie est-il bon ? Une mesure très utilisée est l'**indice de concordance** de Harrell (C-index) : parmi tous les **couples comparables** de clients (c'est-à-dire ceux dont on sait lequel est parti le premier), quelle proportion le modèle ordonne-t-il correctement, c'est-à-dire en attribuant le **risque le plus élevé** à celui qui est parti le plus tôt ? Un couple $(i,j)$ est comparable si $y_i<y_j$ et que $i$ est un départ observé (le client $j$, lui, peut être censuré : on sait qu'il est resté plus longtemps). C'est l'extension du « AUC » du volume I à des durées censurées : 0,5 = hasard, 1 = tri parfait.


Le C-index est d'environ **0,605**, identique à celui de R. C'est **modeste**, et c'est normal : nous n'avons que trois variables, et surtout, la durée d'un client individuel comporte une très grande part d'aléa. Le modèle explique bien les **différences entre groupes** (le HR de 0,67 est très significatif) mais prédit mal le sort d'un client *particulier*. C'est une distinction capitale en pratique : *un résultat significatif n'est pas un modèle prédictif performant* (volume I, section 3.5.3).

### 5.3.9 Un second jeu de données : la récidive (Rossi)

Pour nous assurer que le modèle ne marche pas que sur des données que nous avons simulées, essayons un jeu de données **réel** classique, livré avec la bibliothèque `lifelines` (donc utilisable hors ligne). Il provient de l'étude de **Rossi, Berk et Lenihan (1980)** : 432 hommes libérés de prison dans le Maryland, suivis pendant 52 semaines ; l'événement est une **nouvelle arrestation**. La moitié, tirée au hasard, a reçu une **aide financière** (variable `fin`) pendant sa période de libération. Les autres variables : âge, origine (`race`), expérience professionnelle (`wexp`), marié (`mar`), libération conditionnelle (`paro`), nombre de condamnations antérieures (`prio`).


Les deux bibliothèques donnent les mêmes résultats. L'**aide financière** (`fin`, attribuée au hasard) réduit le risque de nouvelle arrestation d'environ **32 %** ($\mathrm{HR}\approx0{,}68$), un effet à la limite de la significativité ($p\approx0{,}047$ : avec 114 arrestations seulement, la précision est limitée) ; chaque condamnation antérieure l'augmente d'environ 10 % ; chaque année d'âge de plus le réduit de près de 6 %. Notez que, comme pour notre offre de bienvenue, la variable d'intérêt a été **randomisée** : c'est ce qui autorise la lecture causale (volume II, chapitre 7, pour aller plus loin).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercices 5.7, 5.8, 5.10 et 5.13.

> ✅ **À retenir**
> - Le modèle de Cox : $h(t\mid x)=h_0(t)e^{x^\top\beta}$. Le risque de base $h_0$ est **libre** ; chaque coefficient est un **rapport de risques** $\mathrm{HR}=e^{\beta}$, constant dans le temps.
> - La **vraisemblance partielle** $\prod_i e^{x_i^\top\beta}/\sum_{k\in R_i}e^{x_k^\top\beta}$ ne contient pas $h_0$. Son score est $\sum_i(x_i-\bar x_{R_i})$ (les résidus de Schoenfeld) ; **le test du log-rank est le test de score** du modèle à une variable de groupe.
> - Pour les **ex aequo**, préférez **Efron** à Breslow, surtout quand les durées sont arrondies.
> - L'hypothèse de **proportionnalité** se vérifie par le graphique log-log et par le test de score de Grambsch-Therneau (par défaut avec le rang du temps) ; en cas de violation : stratifier, introduire un effet variable dans le temps, ou changer de résumé.
> - Une variable connue seulement **après** un certain temps de survie doit être traitée comme **dépendant du temps** (format à épisodes), sinon on tombe dans le **biais d'immortalité**.
> - Le **risque de base** s'estime a posteriori par Breslow ; on en déduit $S(t\mid x)=\exp[-H_0(t)e^{x^\top\beta}]$ pour tout profil.
> - L'**indice de concordance** mesure la capacité à ordonner les clients ; un effet très significatif peut aller avec un C-index modeste.


## 5.4 Modèles de durée paramétriques

> 💡 **Intuition.** Le modèle de Cox est élégant parce qu'il ne dit rien sur la forme du risque de base. Mais ce silence a un prix : on ne peut rien dire **au-delà** de ce qu'on a observé. La gérante voudrait savoir combien un client rapporte *au total*, y compris pendant les années à venir que personne n'a encore vécues. Pour extrapoler, il faut **parier sur une forme** de loi. Les modèles paramétriques font ce pari : ils décrivent la durée par une loi connue (exponentielle, Weibull, log-normale…) dont les paramètres dépendent des caractéristiques du client. En échange du pari, on obtient des courbes lisses, des durées moyennes, des extrapolations, et des estimations plus précises *si la forme est bonne*.

### 5.4.1 Le modèle à temps de vie accéléré

Les modèles paramétriques s'écrivent le plus naturellement sur le **logarithme de la durée** (le logarithme transforme une quantité positive et asymétrique en une quantité symétrique, comme pour la régression linéaire du début du volume) :
$$\boxed{\ \ln T=\mu(x)+\sigma\,W,\qquad \mu(x)=x^\top\gamma\ }$$
où $W$ est une variable aléatoire de loi **fixée** (le « bruit ») et $\sigma>0$ un paramètre d'**échelle**. C'est le **modèle à temps de vie accéléré** (en anglais *accelerated failure time*, AFT). Le choix de la loi de $W$ détermine la famille :

| Loi de $W$ | Loi de $T$ | $S(t\mid x)$, avec $z=(\ln t-\mu)/\sigma$ | Forme du risque $h(t)$ |
|---|---|---|---|
| $\sigma=1$, valeur extrême | **exponentielle** | $\exp(-e^{z})$ | constant |
| valeur extrême (Gumbel du minimum) | **Weibull** | $\exp(-e^{z})$ | monotone : croissant si $\sigma<1$, décroissant si $\sigma>1$ |
| normale | **log-normale** | $1-\Phi(z)$ | croît puis décroît |
| logistique | **log-logistique** | $1/(1+e^{z})$ | croît puis décroît (ou décroît seulement si $\sigma\ge1$) |

(On reconnaît la forme de Weibull du 5.1.3 avec la **forme** $k=1/\sigma$ et l'**échelle** $e^{\mu}$.)

**Interprétation : l'« accélération ».** Écrivons $T=e^{x^\top\gamma}\,T_0$, où $T_0=e^{\sigma W}$ est la durée d'un client « de référence » ($x=0$). Un client de caractéristiques $x$ vit **$e^{x^\top\gamma}$ fois plus longtemps** : les covariables **accélèrent ou ralentissent l'horloge** :
$$S(t\mid x)=S_0\big(t\,e^{-x^\top\gamma}\big).$$
Le facteur $e^{\gamma_j}$ est le **facteur d'accélération** : s'il vaut 1,37 pour l'offre de bienvenue, tout se passe comme si le temps s'écoulait 1,37 fois plus lentement pour un client qui l'a reçue ; sa durée **médiane** (et sa durée moyenne) est 37 % plus longue. C'est un langage plus parlant que le rapport de risques : *« l'offre rallonge la relation de 37 % »*.

> ⚠️ **Attention au sens des coefficients.** Dans un modèle AFT, un coefficient **positif** signifie une durée **plus longue** (protecteur). Dans le modèle de Cox, un coefficient **positif** signifie un risque **plus élevé** (néfaste). Les signes sont opposés ! Si l'on compare ce que fait Cox et ce que fait un AFT, il faut convertir (ce que nous ferons au 5.4.2).

### 5.4.2 La Weibull : à la fois « risques proportionnels » et « temps accéléré »

Parmi toutes les lois, la Weibull a une propriété unique : elle appartient aux **deux** familles. Montrons-le. Avec $k=1/\sigma$ et $\lambda(x)=e^{x^\top\gamma}$,
$$S(t\mid x)=\exp\!\Big[-\Big(\frac{t}{\lambda(x)}\Big)^{k}\Big],\qquad H(t\mid x)=\Big(\frac{t}{\lambda(x)}\Big)^{k}=t^{k}\,e^{-k\,x^\top\gamma}.$$
Dérivons pour obtenir le risque :
$$h(t\mid x)=k\,t^{k-1}\,e^{-k\,x^\top\gamma}=\underbrace{k\,t^{k-1}}_{h_0(t)}\ \cdot\ e^{x^\top\beta}\qquad\text{avec}\quad\boxed{\ \beta=-k\,\gamma=-\gamma/\sigma\ }.$$
C'est exactement la forme du modèle de Cox, avec un risque de base **imposé** $h_0(t)=kt^{k-1}$. Les coefficients des deux modèles se déduisent l'un de l'autre. C'est un excellent test de cohérence : *si les données sont vraiment Weibull, un modèle de Cox et un AFT Weibull doivent donner les mêmes effets*.

### 5.4.3 Le maximum de vraisemblance, écrit à la main

La vraisemblance avec censure (5.1.5) s'écrit pour un AFT, avec $z_i=(\ln y_i-x_i^\top\gamma)/\sigma$, $f_W$ la densité et $S_W$ la survie de $W$ :
$$\ell(\gamma,\sigma)=\sum_i\Big[\delta_i\big(\ln f_W(z_i)-\ln\sigma-\ln y_i\big)+(1-\delta_i)\ln S_W(z_i)\Big].$$
(La densité de $T=e^{\mu+\sigma W}$ est $f_W(z)/(\sigma t)$ : c'est le changement de variable habituel.) Pour la Weibull, $\ln f_W(z)=z-e^z$ et $\ln S_W(z)=-e^z$ ; pour la log-normale, $f_W=\varphi$ et $S_W=1-\Phi$ ; pour la log-logistique, $\ln f_W(z)=z-2\ln(1+e^z)$ et $\ln S_W(z)=-\ln(1+e^z)$. Nous avons programmé ces trois vraisemblances, les avons maximisées numériquement et avons calculé les erreurs standard par la **hessienne** numérique de $-\ell$ (l'inverse de l'information, comme au volume I, section 3.2) : le code est dans le cahier, application 5.5. Voici l'ajustement de la Weibull sur les 2 000 clients.


| Paramètre | $\gamma$ | Erreur standard | Facteur d'accélération $e^{\gamma}$ |
|---|---:|---:|---:|
| constante | 3,5257 | 0,0970 | 33,98 |
| offre de bienvenue | 0,3132 | 0,0489 | 1,368 |
| âge (par année) | 0,0102 | 0,0023 | 1,010 |
| canal Réseaux (réf. Boutique) | −0,4799 | 0,0636 | 0,619 |
| canal Site (réf. Boutique) | −0,2452 | 0,0671 | 0,783 |

L'échelle estimée est $\hat\sigma=0{,}7563$, soit une forme $k=1/\hat\sigma=1{,}3223$ (log-vraisemblance : $-4\,657{,}38$).


Ces résultats sont identiques à ceux de **R** (`survreg`, la référence) et de `lifelines` : mêmes coefficients, même échelle, même log-vraisemblance.


Avec `lifelines`, l'ajustement tient en trois lignes (`df_ll` rassemble la durée, le départ observé et les variables explicatives) :

```python
from lifelines import WeibullAFTFitter

aft = WeibullAFTFitter().fit(df_ll, "duree_mois", "churn")
print(aft.params_["lambda_"].round(3))                      # coefficients gamma de ln(durée)
```
<!--sortie-->
```text
covariate
age                          0.010
canal_acquisition_Réseaux   -0.480
canal_acquisition_Site      -0.245
offre_bienvenue              0.313
Intercept                    3.526
dtype: float64
```


Lecture :

- **Offre de bienvenue** : facteur d'accélération $e^{0{,}313}\approx1{,}37$ : la durée de vie d'un client qui l'a reçue est **37 % plus longue** (à âge et canal égaux).
- **Canal** : par rapport à la boutique, un client arrivé par Réseaux a une durée de vie **38 % plus courte** ($e^{-0{,}48}\approx0{,}62$) et un client arrivé par le site, **22 % plus courte** ($e^{-0{,}245}\approx0{,}78$).
- **Âge** : chaque année en plus allonge la durée d'environ 1 %.
- **Forme** : $k\approx1{,}32>1$ : le risque **augmente** avec l'ancienneté, ce qui confirme ce que montrait la comparaison de Kaplan-Meier et de l'exponentielle (5.2.2).

**La vérification croisée avec Cox.** Convertissons ces coefficients AFT en coefficients de risques par $\beta=-\gamma/\sigma$ et comparons au modèle de Cox de la section 5.3 :


| Variable | Weibull converti ($-\gamma/\sigma$) | Cox (5.3.3) |
|---|---:|---:|
| offre de bienvenue | −0,4141 | −0,4061 |
| âge | −0,0135 | −0,0136 |
| canal Réseaux | 0,6346 | 0,6351 |
| canal Site | 0,3242 | 0,3258 |


Les deux séries sont presque identiques : les données sont bien compatibles avec une Weibull. Les erreurs standard sont, elles aussi, voisines (environ 0,065 pour l'offre dans les deux cas, en convertissant celle de l'AFT par $0{,}0489/0{,}756$). Quand la forme paramétrique est bonne, on pourrait espérer un gain de précision par rapport à Cox ; ici il est négligeable : avec 977 départs, le risque de base est déjà estimé très précisément, et Cox ne perd presque rien.

### 5.4.4 Choisir entre plusieurs lois

Tous ces modèles ont le même nombre de paramètres sauf l'exponentielle (un de moins) ; on peut donc les comparer par la **vraisemblance** et le **critère d'Akaike** (AIC $=2k-2\ell$, voir la section 1.4 de ce volume ; plus petit = meilleur).


| Loi | Paramètres | Log-vraisemblance | AIC |
|---|---:|---:|---:|
| **Weibull** | 6 | −4 657,38 | **9 326,76** |
| log-logistique | 6 | −4 663,73 | 9 339,45 |
| log-normale | 6 | −4 697,20 | 9 406,40 |
| exponentielle | 5 | −4 710,58 | 9 431,17 |

Le test du rapport de vraisemblance de l'exponentielle contre la Weibull donne $\chi^2=106{,}4$ (1 degré de liberté, $p=6\times10^{-25}$).


La **Weibull** est nettement la meilleure ; la log-logistique arrive deuxième (13 points d'AIC derrière), la log-normale troisième, l'exponentielle dernière. Le test du rapport de vraisemblance rejette l'exponentielle de façon écrasante : le risque n'est pas constant. Les valeurs coïncident avec celles de R.

Un AIC compare des modèles **entre eux** ; il ne dit pas si le meilleur est *bon*. Pour juger l'adéquation, on utilise les **résidus de Cox-Snell**.

> 📐 **Résidus de Cox-Snell.** Si $T$ a pour fonction de survie $S$, alors $S(T)$ suit une loi uniforme (transformée intégrale de probabilité) et donc $H(T)=-\ln S(T)$ suit une loi **exponentielle de paramètre 1**. Pour un modèle correct, les résidus $r_i=\hat H(y_i\mid x_i)$ se comportent comme un échantillon **censuré** de loi exponentielle(1). On estime donc le risque cumulé de ces résidus par Kaplan-Meier (on garde la censure, $\delta_i$) : le graphique de ce risque cumulé contre $r$ doit suivre la **diagonale**.

Superposons la comparaison globale (survie marginale prédite par chaque modèle, contre Kaplan-Meier) et les résidus de Cox-Snell, pour la Weibull et pour l'exponentielle :


![À gauche : survie de Kaplan-Meier des 2 000 clients et survie moyenne prédite par quatre modèles paramétriques. À droite : résidus de Cox-Snell du modèle de Weibull et du modèle exponentiel avec covariables ; le bon modèle suit la diagonale.](figures/ch05-param-ajustement.png)

À gauche, les quatre modèles sont presque indiscernables de Kaplan-Meier jusqu'à 35 mois environ, sauf l'exponentielle, qui prévoit trop de départs au tout début (le schéma de la section 5.2.2). Au-delà de 40 mois, les courbes se séparent : la Weibull suit Kaplan-Meier jusqu'à 55 mois environ, puis passe **un peu en dessous** ; les trois autres lois restent **au-dessus**. À droite, les résidus de Cox-Snell du modèle de Weibull suivent la diagonale jusqu'à $r\approx1{,}5$ (au-delà, quelques résidus seulement : le tracé est instable), tandis que ceux du modèle exponentiel s'en écartent dès que $r$ dépasse environ 0,7.

### 5.4.5 Extrapoler et chiffrer : la valeur vie client

La gérante veut savoir **ce que rapporte un client en moyenne sur toute sa vie**. Pour cela, il lui faut la survie *au-delà* de la fenêtre observée (84 mois au plus). Seul un modèle paramétrique peut fournir cette extrapolation.

La **durée de vie moyenne** d'un client de profil $x$ dans un modèle de Weibull est $E[T\mid x]=\lambda(x)\,\Gamma(1+1/k)$ (section 5.1.3). La **valeur vie client** actualisée (en anglais *customer lifetime value*, CLV) combine cette survie avec un revenu :
$$\mathrm{CLV}(x)=m\sum_{t=0}^{T_{\max}}\frac{S(t\mid x)}{(1+r)^{t}}$$
où $m$ est la **marge mensuelle** par client encore actif, $r$ le taux d'actualisation mensuel (un euro dans un an vaut moins qu'un euro aujourd'hui), et $S(t\mid x)$ la probabilité d'être encore client au mois $t$.

> 🧭 **Des hypothèses, pas des données.** Nous n'avons dans nos fichiers **ni marge ni coût**. Les trois chiffres ci-dessous sont des hypothèses que la gérante devrait remplacer par les siens : une marge de **6 € par mois** et par client actif, un taux d'actualisation de **1 % par mois** (environ 13 % par an) et un horizon de 20 ans (240 mois). Le but est de montrer la **mécanique** du calcul, pas de chiffrer vraiment la boutique.


| Groupe | Clients | Durée moyenne (mois) | Survie à 36 mois | CLV (€) | Part de la CLV après 84 mois |
|---|---:|---:|---:|---:|---:|
| tous les clients | 2 000 | 41,3 | 0,453 | 186,1 | 3,7 % |
| sans offre | 985 | 35,2 | 0,384 | 165,8 | 2,2 % |
| avec offre | 1 015 | 47,3 | 0,521 | 205,8 | 5,0 % |
| Boutique | 504 | 53,2 | 0,574 | 223,5 | 6,4 % |
| Site | 680 | 42,1 | 0,471 | 189,8 | 3,5 % |
| Réseaux | 816 | 33,4 | 0,364 | 160,0 | 1,7 % |


Quelques vérifications de bon sens. La survie moyenne à 36 mois du modèle (0,453) retrouve **exactement** la valeur de Kaplan-Meier de la section 5.2 (0,453), ce qui confirme que le modèle colle aux données observées. La durée moyenne d'un client est de **41 mois**, tandis que la durée moyenne *restreinte* à 60 mois de Kaplan-Meier valait 34 mois : l'écart (7 mois) est la part de la vie *au-delà de 60 mois*, que Kaplan-Meier ne peut pas chiffrer et que le modèle extrapole. Et la durée moyenne **exponentielle** de la section 5.1.5 (48 mois) était trop optimiste.

**L'offre de bienvenue en valait-elle la peine ?** Elle augmente la CLV de 166 à 206 € par client, soit un gain de **40 €** d'actualisé. Si l'offre coûte, par hypothèse, 10 € par client, le gain net est de 30 € par client. Comme l'offre est randomisée, cette différence est une estimation de **l'effet causal** de l'offre sur la valeur. Voyons si le résultat dépend des hypothèses.


Gain net par client (CLV avec offre $-$ CLV sans offre $-$ coût de 10 €), selon les hypothèses :

| Taux d'actualisation | marge 3 €/mois | marge 6 €/mois | marge 9 €/mois |
|---|---:|---:|---:|
| 0,5 % par mois | 16,5 | 42,9 | 69,4 |
| 1,0 % par mois | 10,0 | 30,0 | 50,0 |
| 2,0 % par mois | 2,4 | 14,7 | 27,1 |


Le gain net reste **positif dans les neuf cas testés**, mais son ordre de grandeur varie d'un facteur 30 : de 69 € par client (marge de 9 €, actualisation faible) à seulement 2,4 € (marge de 3 €, actualisation de 2 % par mois), c'est-à-dire presque rien. La conclusion « l'offre est rentable » est donc **robuste** ; la conclusion « elle rapporte 30 € par client » ne l'est pas. Voilà exactement le genre d'information utile : on peut dire à la gérante que l'offre ne perd pas d'argent dans ce domaine d'hypothèses, et lui demander sa vraie marge pour chiffrer le gain.

> ⚠️ **Les limites de l'extrapolation.** La CLV dépend de la survie *au-delà* des données, donc de la forme de loi supposée. La dernière colonne du premier tableau chiffre cette dépendance : la part de la valeur située **après 84 mois** n'est que d'environ 4 % pour l'ensemble des clients (6 % pour la boutique), parce que l'**actualisation** écrase les mois lointains et que beaucoup de clients sont déjà partis. La CLV est donc peu sensible à l'extrapolation. Ce n'est pas le cas de la **durée moyenne**, qui n'est pas actualisée : c'est elle qui réclame de l'extrapolation (7 mois de plus que la RMST à 60 mois). Deux lois qui s'ajustent presque aussi bien sur 84 mois peuvent extrapoler très différemment : la figure du 5.4.4 le montre, avec une Weibull qui passe sous Kaplan-Meier à partir de 55 mois et des lois log-logistique et log-normale qui restent au-dessus. Le bon réflexe : refaire le calcul avec une autre loi (log-logistique) et comparer ; et ne jamais interpréter une CLV comme une certitude.

### 5.4.6 Une variable manquante : le service

Nos modèles ne connaissent ni la qualité du service reçu, ni la satisfaction du client. Or l'enquête de satisfaction (`donnees/enquete_satisfaction.csv`) en mesure une partie : les notes `q5` à `q8` portent sur le service et la livraison. Environ 60 % des clients ont répondu. Que se passe-t-il si l'on ajoute leur **note moyenne de service** au modèle de survie, sur les répondants ?


Sur les 1 212 répondants, ajouter la note de service fait passer la log-vraisemblance de $-2\,785{,}8$ à $-2\,750{,}2$ (rapport de vraisemblance : $\chi^2=71{,}2$ à 1 degré de liberté, $p=3\times10^{-17}$) ; son coefficient vaut 0,262 (erreur standard 0,031) par écart-type de la note.

Un client dont la note de service est **un écart-type au-dessus de la moyenne** reste en moyenne environ **30 % plus longtemps** (facteur 1,30) : le service compte, et le test du rapport de vraisemblance le confirme. C'est un exemple concret de ce qu'apportent les **variables explicatives pertinentes** (et du travail de construction d'indicateurs de la section 3.2 de ce volume, l'analyse factorielle, pour condenser huit notes en un score de service).

### 5.4.7 Révéler la vérité

Comme les données sont simulées, nous pouvons maintenant comparer nos estimations à la loi qui les a engendrées (documentée en tête de `build/donnees2.py`). Les durées sont de loi de **Weibull de forme 1,35**, avec
$$\ln T=3{,}6+0{,}30\,F_2+0{,}35\,\mathrm{offre}+\big\{\text{Boutique }{+}0{,}30,\ \text{Site }0,\ \text{Réseaux }{-}0{,}15\big\}+0{,}008\,(\mathrm{âge}-36)+\sigma W,$$
où $F_2$ est un **facteur de sensibilité au service** (loi normale centrée réduite) **que le fichier ne contient pas**, et où $\sigma=1/1{,}35\approx0{,}74$. On peut même reconstruire ce facteur manquant avec le générateur de données, et ajuster le modèle « oracle » qui le connaît :


| Paramètre | Vérité | Estimé sans $F_2$ | Erreur standard | Écart (en erreurs standard) | Modèle « oracle » (avec $F_2$) |
|---|---:|---:|---:|---:|---:|
| constante | 3,612 | 3,526 | 0,097 | −0,89 | 3,562 |
| offre de bienvenue | 0,350 | 0,313 | 0,049 | −0,75 | 0,299 |
| âge | 0,008 | 0,010 | 0,002 | 0,96 | 0,009 |
| canal Réseaux | −0,450 | −0,480 | 0,064 | −0,47 | −0,486 |
| canal Site | −0,300 | −0,245 | 0,067 | 0,82 | −0,242 |
| forme $k=1/\sigma$ | 1,350 | 1,322 | | | 1,400 |
| facteur manquant $F_2$ | 0,300 | | | | 0,310 |

Que montre cette comparaison ?

1. **Tous les coefficients du modèle réaliste sont à moins d'une erreur standard de la vérité** (colonne « écart / ET ») : la méthode retrouve ce qu'on a programmé (effet de l'offre : $+0{,}31$ estimé contre $+0{,}35$ ; les canaux et l'âge aussi).
2. Le modèle **oracle**, qui connaît le facteur manquant, retrouve **son coefficient** ($\approx0{,}31$ pour une vérité de 0,30). Il estime aussi une forme de $1{,}40$, contre $1{,}32$ pour le modèle sans $F_2$ : la vraie valeur (1,35) se situe entre les deux, et l'écart entre les deux estimations est précisément ce que prédit le point suivant. (De même, sur les répondants à l'enquête, la forme passe de 1,31 à 1,37 quand on ajoute la note de service.)
3. Le **déplacement de la forme** est un phénomène classique : quand une variable qui joue sur le risque est **omise**, le risque observé pour l'ensemble de la population est un **mélange** de risques individuels ; les clients les plus fragiles partent les premiers, de sorte que les survivants sont de plus en plus robustes. La population semble avoir un risque qui augmente **moins vite** que celui de chaque individu. En termes de modèle, on parle d'**hétérogénéité non observée** (ou de **fragilité**, *frailty*). Elle est inévitable : il y a toujours des variables que l'on ne mesure pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercices 5.9 et 5.11.

> ✅ **À retenir**
> - Un modèle **paramétrique** parie sur la loi de la durée. Il permet d'**extrapoler**, de calculer des durées moyennes et d'être plus précis que Cox *si la forme est bonne*.
> - Le modèle **AFT** s'écrit $\ln T=x^\top\gamma+\sigma W$ : les covariables **accélèrent ou ralentissent le temps** ; $e^{\gamma}$ est le facteur d'accélération (**signe opposé** à celui de Cox).
> - La **Weibull** est à la fois AFT et à risques proportionnels, avec $\beta=-\gamma/\sigma$ : un excellent test de cohérence avec Cox.
> - La vraisemblance avec censure s'écrit à la main pour chaque loi ; le résultat doit coïncider avec `survreg` de R. On choisit entre lois par l'**AIC** et on vérifie l'**adéquation** par les **résidus de Cox-Snell**.
> - La **valeur vie client** $\sum_t S(t\mid x)\,m/(1+r)^t$ repose sur des hypothèses explicites (marge, actualisation, horizon) et sur une extrapolation : on la présente avec une analyse de sensibilité, jamais comme une certitude.
> - Une variable pertinente **omise** (hétérogénéité non observée) déplace la forme apparente du risque ; on ne peut jamais exclure qu'il en existe.


## 5.5 ➕ Pour aller plus loin : les risques concurrents

> 🧭 **Section optionnelle.** Elle prolonge le chapitre quand **plusieurs événements** peuvent mettre fin à la durée et s'excluent mutuellement. Les sections 5.1 à 5.4 se lisent sans elle.

> 💡 **Intuition.** Jusqu'ici, il n'y avait qu'une façon de « sortir » : le client partait, ou on ne l'avait pas encore vu partir. Mais dans la vie d'une boutique, un compte peut aussi être **fermé de force** (impayés, soupçon de fraude, adresse invalide). Dès qu'une sortie de ce type survient, le client **ne peut plus partir volontairement** : les deux événements sont en **compétition**, et le premier qui arrive élimine l'autre. Si l'on oublie cette compétition, on surestime les probabilités de chaque cause.

### 5.5.1 Deux façons de sortir

Reprenons le fil de la boutique. Un client peut :

- **cause 1 : partir volontairement** (il ne commande plus et se désinscrit) ;
- **cause 2 : voir son compte fermé de force** (un incident de paiement, par exemple).

On observe un seul de ces événements, **le premier**. Notons $T_1$ et $T_2$ les durées « potentielles » jusqu'à chaque cause (la seconde n'est jamais observée si la première survient avant) ; la durée observée est $T=\min(T_1,T_2)$ (ou la durée de censure, comme avant) et la **cause** est celle qui l'emporte.

Les objets du 5.1 se généralisent :

- le **risque propre à la cause $k$** (*cause-specific hazard*) :
$$h_k(t)=\lim_{\Delta t\to0}\frac{P(t\le T<t+\Delta t,\ \text{cause}=k\mid T\ge t)}{\Delta t}\quad\text{: le taux de sortie par la cause }k\text{ parmi ceux encore là} ;$$
- le risque total $h(t)=h_1(t)+h_2(t)$ : les risques **s'additionnent**, et la survie (« rester client, quelle que soit la cause de départ ») est donc
$$S(t)=\exp\!\Big[-\int_0^t\big(h_1(u)+h_2(u)\big)du\Big]=\exp\big[-H_1(t)-H_2(t)\big] ;$$
- la **fonction d'incidence cumulée** (CIF) de la cause $k$ : la **probabilité** d'être sorti *par la cause $k$* avant $t$,
$$\boxed{\ F_k(t)=P(T\le t,\ \text{cause}=k)=\int_0^t h_k(u)\,S(u)\,du\ }$$

> 📐 **Pourquoi cette formule ?** Pour sortir par la cause $k$ **entre** $u$ et $u+du$, il faut deux choses : être encore là en $u$ (probabilité $S(u)$), puis sortir par la cause $k$ à cet instant (probabilité $h_k(u)\,du$). On additionne sur tous les instants. Le point crucial est que **$S(u)$ est la survie *totale*** : elle dépend des *deux* risques. La probabilité d'une cause dépend donc de l'autre. De plus, comme tout client finit dans l'un des trois états (encore là, sorti par 1, sorti par 2),
> $$S(t)+F_1(t)+F_2(t)=1\quad\text{à tout instant.}$$

### 5.5.2 Pourquoi « 1 − Kaplan-Meier » trompe

La tentation est de traiter la cause 2 comme une simple *censure* : « pour estimer le départ volontaire, on compte les fermetures forcées comme des clients perdus de vue ». Et d'estimer la probabilité de partir volontairement par $1-\hat S_{KM}(t)$. C'est **faux** : on estime ainsi la probabilité de départ volontaire *dans un monde imaginaire où aucune fermeture forcée n'existerait*, que l'on n'a jamais observé. Voyons-le sur dix clients.

| Client | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mois | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 |
| Issue | départ (1) | fermé (2) | départ (1) | censuré | fermé (2) | départ (1) | censuré | départ (1) | fermé (2) | censuré |

**L'estimateur d'Aalen-Johansen** de la CIF de la cause $k$ applique la formule précédente en version « escalier » :
$$\hat F_k(t)=\sum_{j:\,t_j\le t}\hat S(t_{j}^{-})\,\frac{d_{kj}}{n_j}$$
où $n_j$ est l'ensemble à risque en $t_j$, $d_{kj}$ le nombre de sorties par la cause $k$ en $t_j$, et $\hat S(t_j^-)$ la survie **totale** de Kaplan-Meier (toutes causes confondues) juste avant $t_j$. Calculons à la main :

| $t_j$ | $n_j$ | $d_{1j}$ | $d_{2j}$ | $\hat S(t_j^-)$ | ajout à $\hat F_1$ | $\hat F_1$ | ajout à $\hat F_2$ | $\hat F_2$ | $\hat S(t_j)$ |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 10 | 1 | 0 | 1,000 | $1/10=0{,}100$ | 0,100 | 0 | 0 | 0,900 |
| 3 | 9 | 0 | 1 | 0,900 | 0 | 0,100 | $0{,}9/9=0{,}100$ | 0,100 | 0,800 |
| 4 | 8 | 1 | 0 | 0,800 | $0{,}8/8=0{,}100$ | 0,200 | 0 | 0,100 | 0,700 |
| 6 | 6 | 0 | 1 | 0,700 | 0 | 0,200 | $0{,}7/6=0{,}117$ | 0,217 | 0,583 |
| 7 | 5 | 1 | 0 | 0,583 | $0{,}583/5=0{,}117$ | 0,317 | 0 | 0,217 | 0,467 |
| 9 | 3 | 1 | 0 | 0,467 | $0{,}467/3=0{,}156$ | 0,472 | 0 | 0,217 | 0,311 |
| 10 | 2 | 0 | 1 | 0,311 | 0 | 0,472 | $0{,}311/2=0{,}156$ | 0,372 | 0,156 |

(Les censures des mois 5, 8 et 12 réduisent $n_j$ sans produire de ligne.) À la fin, $0{,}156+0{,}472+0{,}372=1$ : la propriété $S+F_1+F_2=1$ est respectée. Comparons avec « 1 − KM » obtenu en traitant les fermetures comme des censures.


Le « 1 − KM » donne 0,58 pour la probabilité de départ volontaire à 9 mois, alors que la vraie incidence cumulée est de 0,47. Il est **trop grand** : il fait comme si les trois clients dont le compte a été fermé (aux mois 3, 6, 10) étaient restés exposés au départ volontaire.

> ⚠️ **Les risques concurrents ne s'additionnent pas comme les 1 − KM.** Avec la méthode erronée, la somme des deux « probabilités » de sortie peut dépasser 1, ce qui est absurde. Avec les incidences cumulées, la somme $F_1+F_2$ est toujours $1-S\le1$.

### 5.5.3 Une simulation avec une vérité connue

Pour voir tout cela à l'échelle, simulons 6 000 clients avec deux causes. Nous choisissons les risques de sorte que :

- **cause 1 (départ volontaire)** : durée de loi de Weibull (forme 1,3), allongée par l'offre de bienvenue (offre tirée au hasard) ;
- **cause 2 (fermeture forcée)** : risque **constant** de 0,6 % par mois, multiplié par 2,2 pour les clients arrivés par Réseaux, et **sans effet de l'offre** ;
- une censure uniforme entre 12 et 72 mois.


Effectifs par issue : 2 079 clients censurés, 2 655 départs volontaires, 1 266 fermetures forcées.

| Horizon | $\hat S$ (encore client) | $\hat F_1$ (départ volontaire) | $\hat F_2$ (fermeture forcée) | « 1 − KM » naïf (cause 1) |
|---|---:|---:|---:|---:|
| 12 mois | 0,762 | 0,143 | 0,095 | 0,151 |
| 24 mois | 0,538 | 0,299 | 0,163 | 0,335 |
| 36 mois | 0,367 | 0,422 | 0,211 | 0,494 |
| 48 mois | 0,251 | 0,514 | 0,235 | 0,627 |


Ces estimations coïncident avec celles de **R** (`cmprsk::cuminc`, qui relit le fichier `donnees/ch05-risques-concurrents.csv` déposé par la simulation) et de `lifelines`, dont voici l'appel :


```python
from lifelines import AalenJohansenFitter

aj = AalenJohansenFitter(calculate_variance=False, seed=1).fit(rc["duree"], rc["cause"], event_of_interest=1)
print(round(float(aj.cumulative_density_.loc[:36].iloc[-1, 0]), 4))      # incidence du départ volontaire à 36 mois
```
<!--sortie-->
```text
0.4217
```


Les trois méthodes donnent les mêmes incidences (0,4217 à 36 mois, par exemple). Remarquez la dernière colonne du tableau : le « 1 − KM » naïf **surestime** systématiquement la probabilité de départ volontaire (par exemple 0,49 contre 0,42 à 36 mois, et 0,63 contre 0,51 à 48 mois). La simulation nous permet même de comparer à la **vérité** : pour un groupe donné, $F_k(t)=\int_0^th_k(u)S(u)\,du$ s'évalue par une intégrale numérique, en mélangeant les clients de Réseaux (45 %) et des autres canaux.


![Incidences cumulées estimées (traits pleins) et vraies (pointillés) des deux causes de sortie, selon l'offre de bienvenue : à gauche le départ volontaire, à droite la fermeture forcée.](figures/ch05-risques-concurrents.png)

Observons la **cause 2**, à droite. L'offre n'a *aucun effet sur le risque de fermeture* (nous l'avons simulée ainsi). Pourtant, les deux courbes ne sont pas superposées : les clients avec offre ont une incidence de fermeture **plus élevée** (le test de Gray, plus bas, rejette l'égalité des deux courbes avec $p\approx3\times10^{-4}$). Pourquoi ? Parce qu'ils partent moins volontairement, donc **restent plus longtemps exposés** au risque de fermeture. La probabilité d'une cause dépend de l'autre : c'est la compétition.

### 5.5.4 Modéliser : deux questions, deux modèles

On peut régresser sur chaque cause de deux façons, qui répondent à **deux questions différentes**.

**Le modèle de Cox par cause.** On ajuste un modèle de Cox pour la cause $k$ en traitant les sorties par les *autres* causes comme des censures. Les coefficients sont des rapports de **risques propres à la cause** : *« parmi les clients encore là, comment la variable change-t-elle le taux de sortie par la cause $k$ ? »*. C'est la bonne question pour **comprendre le mécanisme** (l'offre diminue-t-elle le départ volontaire ?).

**Le modèle de Fine et Gray.** Il modélise directement le **risque de sous-distribution** : le taux de sortie par la cause $k$ parmi ceux qui *n'ont pas encore connu la cause $k$* (ceux qui ont eu l'autre cause restent dans l'ensemble à risque, avec un poids qui décroît). Le coefficient décrit alors l'effet de la variable **sur la CIF** elle-même. C'est la bonne question pour **prédire des probabilités** (quelle part de nos clients quittera volontairement d'ici trois ans ?).


Lisons ces deux familles de résultats ensemble.

- **Cause 1 (départ volontaire).** L'offre réduit le risque propre à la cause 1 : $\widehat{\mathrm{HR}}\approx0{,}58$ (IC95 : 0,54 à 0,63), ce qui retrouve l'effet programmé ($e^{-0{,}40\times1{,}3}\approx0{,}59$ ; voir la conversion AFT ↔ risques proportionnels au 5.4.2). Le modèle de Fine et Gray donne un rapport de sous-distribution du même ordre (environ 0,60) : la réduction du risque se traduit en réduction de l'incidence.
- **Cause 2 (fermeture forcée).** Les clients d'**Réseaux** ont un risque propre multiplié par **2,3** environ (IC95 : 2,07 à 2,60 ; la valeur programmée est $e^{0{,}8}\approx2{,}2$). Et l'**offre** n'a **aucun effet sur le risque** de fermeture : HR $=1{,}03$ (IC95 : 0,93 à 1,15). Mais, dans le modèle de Fine et Gray, l'offre **augmente significativement l'incidence** de la cause 2 : rapport de sous-distribution d'environ **1,22** (IC95 : 1,09 à 1,36). C'est exactement l'effet de compétition que montrait la figure : l'offre ne change pas le risque de fermeture, mais, en retenant plus longtemps les clients, elle les expose plus longtemps à ce risque.
- **Réseaux et la cause 1 : le piège.** Dans le modèle par cause, Réseaux n'a **aucun effet** sur le départ volontaire : HR $=0{,}97$ (IC95 : 0,90 à 1,05), et c'est la vérité. Mais dans le modèle de Fine et Gray, son rapport de sous-distribution est de **0,79** (IC95 : 0,73 à 0,86), **significativement inférieur à 1** : les clients de Réseaux ont une *incidence cumulée de départ volontaire plus faible*. Ce n'est pas qu'ils soient plus fidèles : ils sont **plus souvent éliminés avant** par la fermeture forcée, qui les empêche de partir volontairement. Le coefficient de Fine et Gray mélange l'effet direct sur la cause et l'effet de la compétition.

> 💡 **Quelle question posez-vous ?**
> - *« Pourquoi les clients partent-ils ? »* (étiologie, mécanisme) : **modèles par cause**. On y lit l'effet de chaque variable sur chaque cause, toutes choses égales.
> - *« Combien de clients seront perdus par chaque cause ? »* (pronostic, planification) : **incidences cumulées** (Aalen-Johansen) et **modèle de Fine et Gray**.
> - En cas de doute, présentez **les deux**, avec leurs interprétations.

### 5.5.5 Pièges

> ⚠️ **L'indépendance des causes ne se teste pas.** On ne peut observer que la première des deux durées $T_1,T_2$ : leur loi **jointe** n'est pas identifiable à partir des données. Le modèle par cause n'a pas besoin de cette hypothèse pour estimer les *risques propres* ; mais toute phrase du type « que se passerait-il si l'on supprimait la fermeture forcée ? » en a besoin, et elle est invérifiable. C'est la raison profonde pour laquelle « $1-\mathrm{KM}$ » n'a pas de sens ici.

> ⚠️ **Ne déclarez pas la cause 2 « censure » pour calculer une probabilité.** C'est valable pour estimer un *risque*, jamais pour estimer une *probabilité cumulée*. Si l'on veut une probabilité, on utilise l'incidence cumulée.

> ⚠️ **Événement composite.** Une autre option est de regrouper les causes (« tout départ, volontaire ou forcé ») et d'appliquer les méthodes des sections 5.1 à 5.4 : c'est licite si la question porte sur « rester client » et non sur le mécanisme. Il est alors plus sûr de **le dire**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercice 5.12.

> ✅ **À retenir**
> - Avec plusieurs causes de sortie **concurrentes**, on observe la première seulement. Les risques propres $h_k$ s'additionnent ; $S=e^{-H_1-H_2}$ ; la **CIF** de la cause $k$ est $F_k(t)=\int_0^th_k(u)S(u)\,du$ et $S+F_1+F_2=1$.
> - **1 − Kaplan-Meier** (autres causes traitées en censure) **surestime** la probabilité d'une cause. Utilisez l'estimateur d'**Aalen-Johansen** $\hat F_k(t)=\sum_{t_j\le t}\hat S(t_j^-)\,d_{kj}/n_j$.
> - Le **modèle de Cox par cause** estime l'effet sur le **risque** (mécanisme) ; le modèle de **Fine et Gray** estime l'effet sur l'**incidence cumulée** (pronostic). Les deux peuvent diverger : une variable sans effet direct sur une cause peut modifier son incidence par la compétition.
> - La dépendance entre causes n'est pas identifiable : on évite les phrases « si l'autre cause n'existait pas ».


## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître la censure** et expliquer pourquoi la moyenne des durées, la moyenne des seuls événements et la proportion d'événements sont toutes **biaisées** ; distinguer censure à droite, à gauche, par intervalle et **troncature** (entrée tardive) ; énoncer l'hypothèse de **censure non informative** ;
- manier les trois fonctions d'une durée, **survie** $S(t)$, **risque instantané** $h(t)$ et **risque cumulé** $H(t)$, reliées par $S=e^{-H}$, et la formule $E[T]=\int_0^\infty S(t)\,dt$ ;
- écrire la **vraisemblance avec censure** $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ et en tirer le taux constant $\hat\lambda=D/\sum y_i$ ;
- calculer l'**estimateur de Kaplan-Meier** à la main et par code, ses intervalles de confiance (**Greenwood**, log-log), la **médiane** et la **durée moyenne restreinte** ; comparer des groupes par le **log-rank** et ses variantes ;
- ajuster et interpréter un **modèle de Cox** : vraisemblance partielle, rapports de risques, **ex aequo** (Breslow, Efron), **vérification de la proportionnalité** (graphique log-log, test de score de Grambsch-Therneau), **covariables dépendant du temps** et **biais d'immortalité**, courbes de survie prédites, **indice de concordance** ;
- ajuster des **modèles paramétriques** (Weibull, log-normal, log-logistique) par maximum de vraisemblance, lire un **facteur d'accélération**, passer de l'AFT aux risques proportionnels ($\beta=-\gamma/\sigma$ pour la Weibull), choisir par l'**AIC** et les **résidus de Cox-Snell**, **extrapoler** et calculer une **valeur vie client** avec une analyse de sensibilité ;
- (en option) traiter des **risques concurrents** : incidences cumulées d'**Aalen-Johansen**, pourquoi « 1 − KM » est faux, **modèle par cause** contre **Fine et Gray**.

Deux messages à garder en mémoire. **Un chiffre de survie n'a de sens qu'avec son traitement de la censure et ses hypothèses** (non informative, proportionnalité, forme de la loi) : on les énonce, on les vérifie quand c'est possible, on mesure leur influence sinon. Et **la randomisation reste l'arme la plus solide** : l'offre de bienvenue a un effet causal mesurable parce qu'elle a été attribuée au hasard ; pour les variables non randomisées (le canal, l'âge), les résultats sont des **associations**.

> 📒 **Pour s'entraîner.** Le cahier (chapitre 5) rassemble six applications guidées et treize exercices corrigés.

Le chapitre 6 change de perspective : au lieu de chercher *une* estimation et son incertitude, la **statistique bayésienne** attribue une **loi de probabilité** aux paramètres eux-mêmes, et la **simulation** (Monte-Carlo, MCMC) permet de calculer ce que l'algèbre ne sait pas faire.
