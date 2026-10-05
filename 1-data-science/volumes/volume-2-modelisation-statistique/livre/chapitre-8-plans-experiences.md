# Chapitre 8 : ➕ Plans d'expériences

> « Consulter le statisticien après l'expérience, c'est souvent lui demander de procéder à un examen *post mortem*. Il pourra peut-être dire de quoi l'expérience est morte. »
> (R. A. Fisher)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement optionnel** : le reste du volume ne le suppose pas. Il s'adresse à celles et ceux qui ne se contentent pas d'*analyser* des données déjà là, mais qui veulent **les produire** : tester une vitrine, un emballage, un prix, un réglage de four. Il prolonge le test A/B du volume I (section 3.4.5) à plusieurs facteurs à la fois, et il éclaire, par un autre chemin, la question de la causalité abordée au chapitre 7.

Jusqu'ici, les données tombaient du ciel : un fichier de clients, une série de ventes. Mais quand on peut **choisir** ce que l'on mesure, la manière de le mesurer décide de ce que l'on pourra conclure. Une expérience mal conçue ne se rattrape pas avec des mathématiques ; une expérience bien conçue peut se contenter de mathématiques très simples. C'est tout l'art de ce chapitre.

## Le chemin de ce chapitre

- **8.1 Les principes d'un bon plan** : randomisation, répétition, blocage, et pourquoi changer **un seul facteur à la fois** est une fausse bonne idée.
- **8.2 L'analyse de la variance (ANOVA)** : comparer plusieurs groupes d'un coup, démontrer la décomposition de la variance, contrôler les hypothèses, comparer les groupes deux à deux sans tricher, utiliser des **blocs**, étudier **deux facteurs** et leur **interaction**, calculer la **puissance**.
- **8.3 Les plans factoriels** : tester $k$ facteurs simultanément avec $2^k$ essais, calculer les effets **à la main**, repérer les effets qui comptent sur un diagramme demi-normal.
- **8.4 Plans fractionnaires et surfaces de réponse** : faire **moins d'essais** en acceptant de confondre certains effets, puis **chercher l'optimum** d'un réglage avec un modèle quadratique ; en option, les plans optimaux.
- **8.5 Bilan du chapitre.**

> 📒 **Comment travailler avec ce chapitre.** Chaque section suit le fil : un petit tableau **calculable à la main**, la théorie qui l'explique, puis les résultats sur des données simulées. Faites le calcul à la main *avant* de lire le résultat : c'est le meilleur moyen de comprendre ce que l'ordinateur fait. Pour pratiquer, le **cahier** (chapitre 8) contient les **applications guidées**, avec tout le code (simulations, ANOVA, plans factoriels, surfaces de réponse), et les **exercices corrigés**. Le livre n'affiche que ce dont le raisonnement a besoin ; chaque nombre cité reste pourtant calculé par programme et reproductible.

> 📦 **Les données de ce chapitre.** Les données sont **simulées** (graines fixes, script `build/donnees_ch08.py`) et enregistrées dans `donnees/ch08-*.csv`. Elles racontent des expériences de la gérante : quatre agencements de vitrine, trois emballages, un test « emballage cadeau × promotion × canal de relance » (plans $2^3$ puis $2^4$), et un réglage du four pour ses céramiques. Comme elles sont simulées, **nous connaissons la vérité** : à la fin de chaque étude, nous la dévoilerons pour voir si la méthode l'a retrouvée.


## 8.1 Les principes d'un bon plan d'expériences

> 💡 **Intuition.** Une expérience est une **question posée à la nature**, et la nature répond à la question exactement telle qu'on l'a posée, y compris quand on l'a mal posée. Un plan d'expériences est la préparation de cette question : *quels* essais faire, *combien*, *dans quel ordre*, pour que la réponse soit à la fois **juste** (sans biais) et **précise** (peu de bruit).

### 8.1.1 Le vocabulaire

La gérante veut savoir quel agencement de vitrine fait vendre le plus. Les mots du métier :

| Terme | Sens | Dans l'exemple |
|---|---|---|
| **Facteur** | une variable que l'on **choisit** de faire varier | l'agencement de la vitrine |
| **Niveau** | une valeur possible d'un facteur | « Classique », « Par couleur », « Par thème », « Vedette » |
| **Traitement** | une combinaison de niveaux (un seul facteur : un niveau) | « vitrine Par thème » |
| **Unité expérimentale** | l'objet auquel on applique un traitement, **indépendamment** des autres | **une journée** d'ouverture |
| **Réponse** | ce que l'on mesure | les ventes du jour (€) |
| **Essai** (*run*) | une unité + un traitement + une mesure | « mardi 3, vitrine Vedette : 213 € » |
| **Plan** | la liste des essais, avec leur ordre | 12 jours par agencement, ordre tiré au hasard |

Le point le plus subtil est l'**unité expérimentale** : c'est la plus petite entité à laquelle on peut affecter un traitement **sans que le traitement d'une unité ne dépende de celui d'une autre**. Ici, on ne peut pas changer la vitrine client par client : tous les clients d'une même journée voient la même vitrine. L'unité est donc la journée, pas le client. Nous verrons en 8.1.4 ce que coûte cette confusion.

> 💡 **Expérience ou observation ?** Dans une étude **observationnelle** (les clients des volumes précédents), on constate ce qui s'est passé : les clients « Réseaux » et « Boutique » diffèrent sans que personne ne l'ait décidé, et les différences observées peuvent venir d'autre chose que du canal. Dans une **expérience**, c'est l'expérimentateur qui **affecte** les traitements. C'est cette affectation, et surtout sa manière d'être faite, qui permet de parler de **cause** (chapitre 7 pour le cas observationnel).

### 8.1.2 Première règle : randomiser

Supposons que la gérante teste deux vitrines, A et B, sans effet réel : les deux sont aussi efficaces. Elle installe A du **lundi au jeudi** et B du **vendredi au dimanche**, pendant quatre semaines. Or le week-end, la boutique vend plus (disons 60 € de plus par jour en moyenne, quel que soit l'agencement). Elle va conclure que B est meilleure : le **jour de la semaine** est un **facteur de confusion** : il influence la réponse *et* est lié à l'affectation des traitements (le chapitre 7 en donne la théorie). Voyons l'ampleur du dégât par simulation, en comparant cette affectation à une affectation **tirée au hasard** (14 jours pour A, 14 pour B), sur 2 000 expériences simulées (le programme est dans le cahier, application 8.1).


Résultat : avec l'affectation naïve, la différence B − A est **systématiquement** d'environ 60 € (le biais) et le test « détecte » un effet qui n'existe pas dans **100 %** des 2 000 expériences simulées. Avec l'affectation aléatoire, la différence est **centrée sur zéro** (−0,1 € en moyenne) et le test se trompe dans 5,2 % des cas, **exactement ce que promet son niveau** $\alpha=5\,\%$.

> 📐 **Pourquoi ça marche.** Quand on tire les étiquettes au hasard, le week-end a la **même chance** d'avoir reçu A ou B. Les jours « forts » se répartissent donc équitablement entre les deux traitements *en espérance* : le facteur de confusion, même **inconnu** ou **non mesuré**, cesse d'être confondu avec le traitement. C'est le seul procédé qui protège aussi contre les causes que l'on n'a pas pensé à noter. De plus, c'est le tirage au sort lui-même qui **justifie** les p-valeurs : c'est exactement la logique du test de permutation (volume I, section 3.7.4), où les étiquettes sont mélangées au hasard pour fabriquer la loi de la statistique sous l'hypothèse « aucun effet ».

> ⚠️ **« Au hasard » ne veut pas dire « n'importe comment ».** Alterner un jour sur deux, choisir les jours « qui s'y prêtent » ou laisser un employé décider sont des procédés **non aléatoires** : ils peuvent coïncider avec un rythme caché (par exemple si un jour sur deux est un jour de livraison). Utilisez un générateur pseudo-aléatoire (`rng.permutation`) et **notez la graine**.

### 8.1.3 Deuxième règle : répéter

Une seule journée par vitrine ne dit rien : la différence entre deux journées vient du **bruit** autant que du traitement. **Répéter** le même traitement sur plusieurs unités permet deux choses : **estimer le bruit** (la variabilité entre unités traitées pareil) et **le réduire** (la moyenne de $n$ unités a une variance $\sigma^2/n$, volume I, section 2.4).

> ⚠️ **Répétition ne veut pas dire mesure répétée.** C'est l'erreur la plus fréquente, et elle s'appelle la **pseudo-réplication**. Si la gérante interroge **40 clients** chaque jour, ces 40 réponses du même jour partagent la même vitrine **et** les mêmes aléas de la journée (météo, jour de marché…) : ce ne sont pas 40 unités indépendantes, mais **une** unité mesurée 40 fois. Voyons ce qu'il en coûte. On simule deux vitrines **sans aucune différence**, 5 jours chacune, 40 clients par jour, avec un aléa propre à chaque jour.


Alors qu'il n'y a **aucun effet**, le premier test crie victoire dans **57 %** des expériences, au lieu des 5 % annoncés. Il se croit précis parce qu'il compte 400 clients, alors que la précision réelle est celle de 10 journées. Le second test, moins impressionnant en apparence, tient sa promesse (5,1 %). **Règle pratique : le nombre de degrés de liberté de l'erreur se compte en unités expérimentales, pas en mesures.**

### 8.1.4 Troisième règle : bloquer

La répétition réduit le bruit, mais certaines sources de variabilité sont **connues à l'avance** : les semaines ne se ressemblent pas (soldes, fêtes), les lots de matière première non plus. Plutôt que de laisser cette variabilité gonfler le bruit, on l'**isole** : on découpe l'expérience en **blocs** de conditions homogènes (par exemple une semaine par bloc) et, **dans chaque bloc**, on teste **tous** les traitements, en randomisant l'ordre dans le bloc. Les comparaisons se font alors à l'intérieur des blocs, à conditions égales. Concrètement, au lieu de tirer au sort l'agencement de vitrine de 48 journées issues de huit semaines mélangées, on teste les **quatre agencements chaque semaine**, dans un ordre tiré au sort : la semaine, ses soldes et sa météo, deviennent un point de comparaison commun et non plus une source de bruit. La section 8.2.8 montre, chiffres à l'appui, ce que cela change.

> ✅ **La devise de Fisher, en une ligne** : **Bloquez ce que vous pouvez, randomisez ce que vous ne pouvez pas bloquer, et répétez pour mesurer le bruit.**

### 8.1.5 Faire varier un seul facteur à la fois : une fausse bonne idée

L'instinct dit : « pour savoir ce que fait chaque facteur, changeons-les un par un, les autres restant fixes ». Cette méthode, appelée **OFAT** (*one factor at a time*), semble prudente. Elle est en réalité **inefficace** et **aveugle aux interactions**. Considérons un exemple assez petit pour être calculé à la main. La gérante hésite entre deux facteurs : l'**emballage** (standard ou cadeau) et le **prix** (normal ou promotion de 10 %). Imaginons que nous connaissions, sans bruit, le nombre moyen de commandes par semaine dans chacune des quatre situations :

| | prix normal | promo −10 % |
|---|---|---|
| **emballage standard** | 50 | 62 |
| **emballage cadeau** | 55 | 60 |

**La démarche OFAT.** On part de la situation actuelle (standard, prix normal : 50). On change l'emballage : 55, c'est mieux (+5), on adopte le cadeau. Puis, avec le cadeau, on change le prix : 60, c'est mieux (+5), on adopte la promo. Conclusion : « la meilleure combinaison est *cadeau + promo*, 60 commandes ». Or la vraie meilleure est **standard + promo : 62**. L'emballage cadeau, qui aide au prix normal, **gêne** quand il y a une promotion (−2) : on dit qu'il y a **interaction** entre les deux facteurs. L'OFAT l'a manquée, car il n'a **jamais** testé « standard + promo ».


Les effets se lisent directement dans le tableau : le cadeau apporte **+5** au prix normal mais **−2** en promotion ; la promotion apporte **+12** en emballage standard mais seulement **+5** en cadeau. **L'effet d'un facteur dépend du niveau de l'autre.** On résume cela par l'**effet principal** du cadeau (la moyenne de ses deux effets : $1{,}5$), celui de la promotion ($8{,}5$) et l'**interaction** (la demi-différence entre les deux effets du cadeau : $-3{,}5$ ; ces définitions sont précisées en 8.3). Parler de « l'effet du cadeau » tout court n'a alors plus de sens.

**L'OFAT est aussi moins précis.** Supposons un bruit d'écart-type $\sigma$ sur chaque essai. Avec 4 essais, l'OFAT en consacre deux à la situation de départ (sinon on ne mesure aucun bruit) puis un essai pour chaque facteur modifié : l'effet de A s'estime par $y_A-\bar y_0$, de variance $\sigma^2(1+\tfrac12)=1{,}5\sigma^2$. Le plan **factoriel** utilise les **mêmes 4 essais** (les quatre cases du tableau) et estime l'effet de A par $\tfrac12\left[(y_{\text{cadeau, normal}}+y_{\text{cadeau, promo}})-(y_{\text{std, normal}}+y_{\text{std, promo}})\right]$, de variance $\tfrac14\cdot4\sigma^2=\sigma^2$. Chaque essai y sert **deux fois** : une fois pour chaque facteur. Vérifions par simulation (100 000 expériences rejouées, avec $\sigma=4$).


Deux enseignements. D'abord, à nombre d'essais égal, le plan factoriel est plus précis : la simulation retrouve la variance $\sigma^2=16$ pour le factoriel et $1{,}5\sigma^2=24$ pour l'OFAT. Ensuite, les deux méthodes n'estiment pas la même chose : l'OFAT mesure l'effet du cadeau **seulement au prix normal** (5), alors que le factoriel mesure son effet **moyen** sur les deux prix (1,5, la simulation donne 1,48) **et**, grâce à l'interaction, sait qu'il est de +5 dans un cas et de −2 dans l'autre. Avec davantage de facteurs, l'avantage du factoriel est encore plus net (section 8.3).

> ✅ **À retenir.**
> - Une expérience est caractérisée par ses **facteurs**, ses **unités expérimentales** et sa **réponse** ; l'unité est ce à quoi l'on affecte réellement le traitement.
> - **Randomiser** rend le traitement indépendant des facteurs de confusion, même inconnus : sans cela, une différence « significative » peut n'être qu'un artefact.
> - **Répéter** pour estimer et réduire le bruit, mais **ne pas confondre** répétition (unités indépendantes) et mesures répétées (pseudo-réplication).
> - **Bloquer** pour retirer du bruit les sources de variabilité connues.
> - Changer **un facteur à la fois** est moins précis et **aveugle aux interactions** ; les plans **factoriels** font varier tous les facteurs ensemble.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.1, exercice 8.1.


## 8.2 L'analyse de la variance (ANOVA)

> 💡 **Intuition.** Pour comparer deux groupes, on utilisait un test de Student. Pour en comparer **quatre**, on pourrait faire les six tests deux à deux, mais cela multiplie les risques de fausse alerte (volume I, section 3.5.5). L'ANOVA pose une seule question globale : **« les moyennes des groupes diffèrent-elles plus que ne le ferait le seul hasard ? »** Et elle y répond en comparant **deux sources de variabilité** : celle **entre** les groupes (l'effet du traitement, s'il existe) et celle **à l'intérieur** des groupes (le bruit). Si la première dépasse nettement la seconde, les groupes ne sont pas interchangeables.

### 8.2.1 Le problème : quatre agencements de vitrine

La gérante a testé quatre agencements de vitrine (« Classique », « Par couleur », « Par thème », « Vedette »). Pendant 48 jours d'ouverture, elle a tiré au sort l'agencement de chaque journée (12 jours par agencement) et relevé les ventes du jour. Les unités expérimentales sont les journées, comme nous l'avons discuté en 8.1. Voici les ventes moyennes par agencement :


```text
              n  moyenne  ecart_type
agencement                          
Classique    12    196.2        38.1
Vedette      12    215.4        28.3
Par couleur  12    224.6        40.7
Par thème    12    237.0        25.5

moyenne générale : 218.3
```

Les moyennes diffèrent, mais les écarts-types sont du même ordre que ces différences : difficile de juger à l'œil. Dessinons les données **avant** de calculer quoi que ce soit (volume I, section 3.1).


![Ventes journalières selon l'agencement de la vitrine : chaque point est une journée, le trait orange est la moyenne du groupe, la ligne en pointillés la moyenne générale.](figures/ch08-vitrines.png)

Les nuages se chevauchent beaucoup, mais ils sont ordonnés : « Classique » est en bas, « Par thème » en haut. La différence est-elle réelle ou due au hasard de la répartition des jours ?

### 8.2.2 Décomposer la variabilité : un exemple de neuf nombres

Commençons par un exemple minuscule. Trois agencements, trois journées chacun :

| | journée 1 | journée 2 | journée 3 | moyenne |
|---|---|---|---|---|
| Classique | 190 | 200 | 210 | 200 |
| Par couleur | 205 | 215 | 225 | 215 |
| Par thème | 230 | 240 | 250 | 240 |

La moyenne des neuf valeurs est $\bar y=(200+215+240)/3\approx 218{,}33$. Deux sortes d'écarts :

- l'écart **entre** les groupes : chaque moyenne de groupe s'écarte de la moyenne générale ($-18{,}33$ ; $-3{,}33$ ; $+21{,}67$) ;
- l'écart **à l'intérieur** de chaque groupe : chaque valeur s'écarte de la moyenne de *son* groupe ($-10$, $0$, $+10$, dans les trois groupes).

On mesure chaque sorte d'écart par une **somme de carrés** (volume I, section 3.1.4 pour la variance) :

$$SS_{\text{entre}}=3\left[(-18{,}33)^2+(-3{,}33)^2+(21{,}67)^2\right]=2450,\qquad SS_{\text{dans}}=3\times(100+0+100)=600.$$

Et la variabilité **totale** de l'ensemble des neuf valeurs, $\sum(y-\bar y)^2$, vaut $3050=2450+600$. Ce n'est pas un hasard. Avec les degrés de liberté présentés en 8.2.3, les carrés moyens valent $MS_B=2450/2=1225$ et $MS_W=600/6=100$, d'où $F=12{,}25$ ($p=0{,}0076$).


> 📐 **Théorème (décomposition de la variance).** Soit $y_{ij}$ la $j$-ième observation du groupe $i$ ($i=1,\dots,k$ ; $j=1,\dots,n_i$), $N=\sum n_i$, $\bar y_i$ la moyenne du groupe et $\bar y$ la moyenne générale. Alors
> $$\underbrace{\sum_{i,j}(y_{ij}-\bar y)^2}_{SS_T}=\underbrace{\sum_i n_i(\bar y_i-\bar y)^2}_{SS_B\ (\text{entre})}+\underbrace{\sum_{i,j}(y_{ij}-\bar y_i)^2}_{SS_W\ (\text{dans})}.$$
> *Démonstration.* On écrit $y_{ij}-\bar y=(y_{ij}-\bar y_i)+(\bar y_i-\bar y)$ et on développe le carré :
> $$\sum_{i,j}(y_{ij}-\bar y)^2=\sum_{i,j}(y_{ij}-\bar y_i)^2+\sum_{i,j}(\bar y_i-\bar y)^2+2\sum_{i}(\bar y_i-\bar y)\underbrace{\sum_{j}(y_{ij}-\bar y_i)}_{=\,0}.$$
> Le double produit s'annule, car la somme des écarts d'un groupe à sa propre moyenne est nulle. Et $\sum_{i,j}(\bar y_i-\bar y)^2=\sum_i n_i(\bar y_i-\bar y)^2$ puisque le terme ne dépend pas de $j$. $\square$

La décomposition est exacte, quelles que soient les données : elle n'a rien de statistique. C'est son **interprétation** qui l'est. Pour en tirer un test, il faut un modèle.

### 8.2.3 Le modèle et le test F

Le **modèle à un facteur** suppose que

$$y_{ij}=\mu+\tau_i+\varepsilon_{ij},\qquad \varepsilon_{ij}\ \text{indépendants},\ \varepsilon_{ij}\sim\mathcal N(0,\sigma^2),\qquad \sum_i n_i\tau_i=0.$$

$\mu$ est la moyenne générale, $\tau_i$ l'**effet** du niveau $i$ (l'écart de sa moyenne vraie à $\mu$) et $\varepsilon_{ij}$ le bruit. L'hypothèse nulle « tous les agencements se valent » s'écrit $H_0:\tau_1=\dots=\tau_k=0$.

On compare maintenant les sommes de carrés **ramenées à leurs degrés de liberté** : $MS_B=SS_B/(k-1)$ et $MS_W=SS_W/(N-k)$ (*mean squares*, « carrés moyens »). Pourquoi ces diviseurs ?

> 📐 **Ce que valent les carrés moyens.**
> 1. **$MS_W$ estime toujours $\sigma^2$**, effet ou non. En effet, dans le groupe $i$, $\sum_j(y_{ij}-\bar y_i)^2/\sigma^2\sim\chi^2_{n_i-1}$ (résultat classique pour des observations gaussiennes, que nous admettons ; la loi du khi-deux a été rencontrée au volume I, section 3.4.6, dans un autre rôle) ; les $k$ groupes étant indépendants, la somme $SS_W/\sigma^2$ suit une loi $\chi^2_{N-k}$, d'espérance $N-k$. Donc $\mathbb E[MS_W]=\sigma^2$.
> 2. **$MS_B$ estime $\sigma^2$ plus un terme dû aux effets** : un calcul direct donne
> $$\mathbb E[MS_B]=\sigma^2+\frac{\sum_i n_i\tau_i^2}{k-1}.$$
> Sous $H_0$ (tous les $\tau_i=0$), $\mathbb E[MS_B]=\sigma^2$ aussi ; sinon $MS_B$ est plus grand.
> 3. Sous $H_0$, $SS_B/\sigma^2\sim\chi^2_{k-1}$ et **$SS_B$ est indépendant de $SS_W$** (théorème de Cochran : la décomposition en sommes de carrés orthogonales donne des $\chi^2$ indépendants).
>
> Le quotient de deux $\chi^2$ indépendants divisés par leurs degrés de liberté suit une **loi de Fisher** :
> $$F=\frac{MS_B}{MS_W}\ \underset{H_0}{\sim}\ \mathcal F(k-1,\;N-k).$$
> Sous $H_0$, $F$ vaut environ 1 ; si les effets existent, $F$ est tiré vers le haut. On rejette donc $H_0$ quand $F$ est **grand** (test unilatéral à droite).

Appliquons cela aux données de la gérante. Le calcul à la main donne $SS_B=10\,595$, $SS_W=50\,168$ (total $60\,763$), $MS_B=3\,532$ et $MS_W=1\,140$, donc $F=3{,}10$ avec 3 et 44 degrés de liberté, soit $p=0{,}036$. La bibliothèque `statsmodels` redonne le même tableau d'analyse de variance :


```python
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

modele = ols("ventes ~ C(agencement)", data=df).fit()
print(anova_lm(modele).round(3))
```
<!--sortie-->
```text
                 df     sum_sq   mean_sq      F  PR(>F)
C(agencement)   3.0  10595.062  3531.687  3.097   0.036
Residual       44.0  50168.171  1140.186    NaN     NaN
```

Les trois calculs (à la main, `statsmodels` et `scipy`) coïncident. Le test rejette l'hypothèse « tous les agencements se valent » à 5 %, sans que la preuve soit écrasante : $p\approx0{,}036$ est proche du seuil de 5 %. Nous reviendrons en 8.2.10 sur la puissance de cette expérience.

> ⚠️ **Ce que l'ANOVA ne dit pas.** Un $F$ significatif dit que **au moins un** agencement diffère des autres ; il ne dit pas **lesquels**. Pour cela, il faut des comparaisons deux à deux *corrigées* (8.2.6).

### 8.2.4 L'ANOVA, le test de Student et la régression sont le même outil

**Avec deux groupes**, l'ANOVA redonne le test de Student à variances égales : $F=t^2$, avec la même p-valeur. Entre « Classique » et « Par thème » : $t=3{,}08$, $t^2=9{,}48=F$, et $p=0{,}0055$ dans les deux cas.


**Avec $k$ groupes**, c'est une **régression linéaire** (chapitre 1) sur des variables indicatrices : on prend un groupe de référence et on code les autres par $0/1$. La constante est alors la moyenne du groupe de référence et chaque coefficient est l'écart de moyenne par rapport à lui. Le test $F$ global de la régression (section 1.2) *est* le test $F$ de l'ANOVA, et le $R^2$ de la régression vaut $SS_B/SS_T$. Ici : $F=3{,}097$ ($p=0{,}036$) et $R^2=SS_B/SS_T=0{,}174$.

```text
Intercept                       196.25
C(agencement)[T.Par couleur]     28.36
C(agencement)[T.Par thème]       40.72
C(agencement)[T.Vedette]         19.19
```


La constante est la moyenne du groupe de référence (le premier par ordre alphabétique, « Classique »), et les autres coefficients sont les écarts à ce groupe. L'ANOVA n'est donc pas un outil à part : c'est un **cas particulier du modèle linéaire** dont les variables explicatives sont qualitatives. Cette vue unifiée sera précieuse pour les plans factoriels (8.3), où les « effets » seront exactement des coefficients.

### 8.2.5 Vérifier les hypothèses

Le test $F$ suppose des erreurs **indépendantes** (garanti par la randomisation et le bon choix de l'unité, 8.1), **gaussiennes** et de **même variance** dans tous les groupes. On les vérifie sur les **résidus** $e_{ij}=y_{ij}-\bar y_i$.


![À gauche : diagramme quantile-quantile des résidus de l'ANOVA, qui suivent à peu près la droite. À droite : résidus selon la moyenne du groupe, sans structure visible ni dispersion qui varie nettement d'un groupe à l'autre.](figures/ch08-anova-diagnostics.png)

Les tests confirment l'impression visuelle : Shapiro-Wilk donne $p=0{,}52$ pour la normalité des résidus, Levene $p=0{,}28$ et Bartlett $p=0{,}37$ pour l'égalité des variances, et le plus grand écart-type n'est que 1,6 fois le plus petit. Aucun signal inquiétant : le diagramme quantile-quantile suit la droite et la dispersion des résidus est comparable d'un groupe à l'autre. Si ce n'était pas le cas :

- **variances inégales** : utiliser l'ANOVA de **Welch** (qui n'impose pas l'égalité des variances) ;
- **résidus très non gaussiens** : transformer la réponse (logarithme pour des montants, volume I, section 3.1.5) ou utiliser le test de **Kruskal-Wallis** (volume I, section 3.7.3) ;
- **dépendance** entre unités : c'est un défaut du **plan**, et aucune correction après coup ne le répare.


Les ANOVA classique et de Welch concluent de la même façon ($p=0{,}036$ et $p=0{,}039$). Le test de Kruskal-Wallis, qui travaille sur les rangs, est un peu moins tranché ($p=0{,}072$) : il passe juste au-dessus du seuil de 5 %. Il n'y a pas de contradiction, mais un **avertissement honnête** : la preuve est **limite**, et la conclusion « au moins un agencement diffère » ne doit pas être présentée comme acquise au-delà de tout doute. C'est le genre de nuance qu'une p-valeur isolée ferait oublier.

### 8.2.6 Quels groupes diffèrent ? Les comparaisons multiples

Avec $k=4$ niveaux, il y a $\binom42=6$ paires. Si l'on faisait six tests à 5 %, la probabilité d'au moins une fausse alerte n'est plus 5 % mais proche de $1-0{,}95^6\approx26\,\%$ (volume I, section 3.5.5). Il faut un procédé qui contrôle le risque **global** (*familywise*). Deux classiques :

- **Bonferroni** : rejeter si $p<\alpha/m$ ($m$ = nombre de comparaisons). Simple mais conservateur.
- **Tukey HSD** (*Honestly Significant Difference*), conçu exactement pour comparer **toutes les paires de moyennes** : deux moyennes diffèrent si leur écart dépasse
$$\text{HSD}=q_{1-\alpha;\,k,\,N-k}\sqrt{\frac{MS_W}{n}}\qquad(\text{groupes de même taille } n),$$
où $q$ est le quantile de la **loi de l'étendue studentisée** (la loi du plus grand écart entre $k$ moyennes, divisé par son écart-type estimé). Plus on compare de groupes, plus ce seuil monte. La bibliothèque `statsmodels` fournit directement les six comparaisons, avec des intervalles de confiance simultanés :


```text
     group1      group2  meandiff  p-adj   lower  upper  reject
  Classique Par couleur    28.358  0.183  -8.448 65.165   False
  Classique   Par thème    40.725  0.025   3.918 77.532    True
  Classique     Vedette    19.192  0.511 -17.615 55.998   False
Par couleur   Par thème    12.367  0.806 -24.440 49.173   False
Par couleur     Vedette    -9.167  0.910 -45.973 27.640   False
  Par thème     Vedette   -21.533  0.410 -58.340 15.273   False
```

Le calcul à la main (seuil $\text{HSD}=3{,}776\times\sqrt{1140/12}=36{,}8$ €) et la bibliothèque donnent les mêmes décisions. On voit aussi le prix de la prudence : avec 6 comparaisons, il faut un écart d'environ 37 € pour conclure, alors qu'un test non corrigé se contenterait d'environ 28 € (deux écarts, 28,4 et 40,7, l'auraient franchi). Après correction, un seul écart franchit la barre : le plus grand, « Par thème » contre « Classique » (écart de 40,7 €, $p$ ajustée $=0{,}025$, intervalle de confiance simultané de 3,9 à 77,5 € : l'effet est détecté, mais **très imprécis**). Avec la correction de Bonferroni (ici sur des tests de Student séparés), on arrive à la même conclusion : seul « Par thème » contre « Classique » reste significatif ($p$ brute $0{,}0055$, multipliée par 6 : $0{,}033$).


> 💡 **Un contraste planifié, pour une question précise.** Si, **avant** l'expérience, la gérante s'était demandé « l'agencement *Par thème* fait-il mieux que la moyenne des trois autres ? », elle pouvait tester **un seul** contraste $c=\bar y_{\text{thème}}-\tfrac13(\bar y_{\text{classique}}+\bar y_{\text{couleur}}+\bar y_{\text{vedette}})$, avec un seul test. Un contraste est une combinaison linéaire des moyennes dont les poids somment à 0 ; son écart-type estimé est $\sqrt{MS_W\sum_i c_i^2/n_i}$, et sa statistique suit une loi de Student à $N-k$ degrés de liberté. Poser la question **avant** évite d'avoir à corriger des dizaines de comparaisons possibles.


Le thème l'emporte d'environ 25 € sur la moyenne des trois autres ($p=0{,}032$, intervalle de 2 à 48 €). Une **seule** question posée à l'avance, donc **un seul** test, sans correction : la conclusion est plus nette que celle des six comparaisons deux à deux, mais elle n'est honnête que parce que la question a été choisie **avant** de voir les données.


![Intervalles de confiance simultanés de Tukey pour les six écarts de moyennes ; seul l'écart Par thème - Classique est entièrement à droite de zéro.](figures/ch08-tukey.png)

### 8.2.7 La taille de l'effet

Une p-valeur dit si l'effet est **détectable**, pas s'il est **important** (volume I, section 3.5.3). Pour l'ANOVA, la mesure usuelle est la part de variance expliquée par le facteur :

$$\eta^2=\frac{SS_B}{SS_T}\quad(\text{c'est le }R^2\text{ de la régression}),\qquad \omega^2=\frac{SS_B-(k-1)MS_W}{SS_T+MS_W},\qquad f=\sqrt{\frac{\eta^2}{1-\eta^2}}.$$

$\eta^2$ est **biaisé vers le haut** dans les petits échantillons ; $\omega^2$ en est une version corrigée. Le $f$ de Cohen est l'écart-type des moyennes des groupes divisé par $\sigma$ ; ses repères habituels sont 0,10 (petit), 0,25 (moyen), 0,40 (grand).


L'agencement explique donc environ 17 % de la variance des ventes journalières ($\eta^2=0{,}174$), ou 12 % après correction du biais ($\omega^2=0{,}116$) : avec $f=0{,}46$, un effet **grand** selon les repères de Cohen, mais noyé dans un bruit important (les ventes d'une journée varient beaucoup, quel que soit l'agencement). Le $\omega^2$ est la valeur à retenir : le $\eta^2$ flatte toujours un peu un petit échantillon. Gardez en tête la division du travail : la **p-valeur** répond à « existe-t-il un effet ? », la **taille d'effet** répond à « est-il grand ? », et c'est la seconde qui guide une décision (changer ou non l'agencement de la vitrine).

### 8.2.8 Les blocs : retirer du bruit connu

La gérante refait l'expérience autrement. Elle sait que les semaines diffèrent beaucoup (soldes, fêtes, météo) : elle découpe l'expérience en **8 semaines** (les **blocs**), et chaque semaine elle teste **chacun des quatre agencements une fois**, dans un ordre tiré au hasard. Soit 32 journées. C'est un **plan en blocs complets randomisés**. (Par transparence : ces données sont simulées avec une graine fixée, la 811, retenue après avoir écarté deux graines voisines dont l'échantillon était atypique ; le générateur lui-même est correct, puisqu'il donne en moyenne, sur 400 graines, le carré moyen résiduel attendu.)

Le modèle ajoute un effet de bloc :

$$y_{ij}=\mu+\tau_i+\beta_j+\varepsilon_{ij},\qquad i=1..k\ (\text{traitements}),\ j=1..b\ (\text{blocs}),$$

et la décomposition devient $SS_T=SS_{\text{trait}}+SS_{\text{blocs}}+SS_E$, avec $k-1$, $b-1$ et $(k-1)(b-1)$ degrés de liberté. La démonstration est la même qu'en 8.2.2, avec trois sortes d'écarts au lieu de deux. Vérifions-la sur un exemple de neuf nombres, trois traitements et trois semaines :


Ici ($SS_{\text{blocs}}=602$, $SS_{\text{traitements}}=44{,}7$ et $SS_E=3{,}3$, pour un total de $650$, avec $2$, $2$ et $4$ degrés de liberté), presque toute la variabilité vient des blocs (les semaines diffèrent beaucoup) ; le résidu, une fois les blocs retirés, est minuscule. Voyons ce que cela change sur les vraies données de l'expérience en blocs :


```text
                          carré moyen de l'erreur  F de l'agencement      p
en ignorant les semaines                 1714.541              1.542  0.225
avec les blocs                            173.640             15.228  0.000
```

C'est la même mesure, les mêmes 32 ventes, et pourtant la conclusion change du tout au tout. Sans les blocs, l'effet de l'agencement est noyé dans la variabilité entre semaines (qui se retrouve dans le résidu) : le test ne détecte rien ($F=1{,}54$, $p=0{,}225$). Avec les blocs, la variabilité entre semaines est **isolée** dans sa propre ligne : le carré moyen de l'erreur s'effondre (d'environ 1 715 à 174), et l'effet de l'agencement devient très significatif ($F=15{,}2$). Le numérateur, lui, n'a pas bougé (même $SS_{\text{trait}}$) : **seul le bruit a diminué**. On quantifie le gain par l'**efficacité relative** du plan en blocs : le facteur par lequel il aurait fallu multiplier le nombre de répétitions d'un plan sans blocs pour avoir la même précision.


Ici l'efficacité relative est d'environ **9** : un plan sans blocs aurait demandé à peu près neuf fois plus de journées par agencement (de l'ordre de 70 semaines au lieu de 8) pour atteindre la même précision. Et le seuil de Tukey n'est plus que de 18 € (contre 37 € dans l'expérience sans blocs) : avec les mêmes quatre agencements, on distingue maintenant des écarts deux fois plus petits. « Par thème » dépasse « Classique » de 43 €, « Par couleur » de 17 €, juste sous le seuil, et « Vedette » de 11 €.

> ⚠️ **Deux précautions.**
> 1. Les blocs se **choisissent avant** l'expérience, parce qu'ils sont *connus* comme source de variabilité. On bloque sur ce qui varie beaucoup (la semaine), pas sur n'importe quoi : chaque bloc coûte des degrés de liberté à l'erreur.
> 2. Le modèle suppose que **l'effet du traitement est le même dans tous les blocs** (pas d'interaction traitement × bloc, d'ailleurs non estimable avec une seule observation par case). Si les semaines réagissaient différemment aux agencements, cette hypothèse serait fausse. Avec deux traitements seulement, le plan en blocs est exactement le **test de Student apparié**. Quand les blocs sont des échantillons tirés au sein d'une population plus large, on les traite comme des effets **aléatoires** (modèles mixtes, section 1.7).

### 8.2.9 Deux facteurs et leur interaction

La gérante s'intéresse maintenant à l'**emballage** (Kraft, Tissu, Coffret) et au **canal** de la commande (Site, Réseaux). Pour chacune des 6 combinaisons, elle observe 10 commandes (60 au total) et relève le **panier** en €. On obtient un plan **factoriel $3\times2$ avec répétitions**.

Le modèle à deux facteurs avec interaction s'écrit

$$y_{ijr}=\mu+\alpha_i+\beta_j+(\alpha\beta)_{ij}+\varepsilon_{ijr},$$

où $\alpha_i$ est l'effet de l'emballage $i$, $\beta_j$ celui du canal $j$, et $(\alpha\beta)_{ij}$ l'**interaction** : ce qu'il faut ajouter à la somme des deux effets principaux pour retrouver la moyenne de la case $(i,j)$. S'il n'y a pas d'interaction, les effets s'**additionnent** ; sinon, l'effet de l'emballage dépend du canal. Les sommes de carrés se décomposent comme en 8.2.2 : $SS_T=SS_A+SS_B+SS_{AB}+SS_E$.

```text
canal            Réseaux  Site  moyenne ligne
emballage                                    
Kraft               43.5  48.0           45.7
Tissu               48.0  50.3           49.2
Coffret             69.8  60.3           65.0
moyenne colonne     53.8  52.9           53.3
```

Lisez les moyennes des cases : sur le **Site**, passer du Kraft au Coffret fait gagner environ 12 € ; sur le canal **Réseaux**, le gain est **deux fois plus grand** (environ 26 €). L'effet de l'emballage dépend du canal : c'est une interaction. Représentons-la, avant de la tester.


![Graphique d'interaction : panier moyen selon l'emballage, une courbe par canal. Les deux courbes montent avec le niveau d'emballage mais celle du canal Réseaux monte plus fort, donc elles ne sont pas parallèles.](figures/ch08-interaction.png)

> 💡 **Lire un graphique d'interaction.** Des courbes **parallèles** signifient pas d'interaction (les effets s'additionnent). Des courbes qui **s'écartent** ou **se croisent** signalent une interaction. Ce graphique est le premier outil à regarder pour deux facteurs.

Le test :

```text
                         df    sum_sq   mean_sq       F  PR(>F)
C(emballage)            2.0  4248.196  2124.098  39.749   0.000
C(canal)                1.0    12.513    12.513   0.234   0.630
C(emballage):C(canal)   2.0   569.809   284.905   5.331   0.008
Residual               54.0  2885.656    53.438     NaN     NaN
```


On lit le tableau **de bas en haut** : on teste d'abord l'**interaction**. Si elle est significative, l'interprétation des effets principaux devient **trompeuse**, car un effet principal est une moyenne sur l'autre facteur, qui peut cacher des effets de signes ou d'ampleurs différents. Ici, l'interaction est significative ; l'effet de l'emballage est très fort. En revanche, l'effet principal du **canal** est quasiment nul : ce n'est pas que le canal n'a aucune importance (il joue sur l'effet du coffret), c'est que, **en moyenne sur les emballages**, les deux canaux se compensent. C'est le piège classique. Quand il y a interaction, on étudie les **effets simples** : l'effet d'un facteur **à chaque niveau** de l'autre. Ici, l'emballage joue sur les deux canaux, mais très différemment : gain Coffret − Kraft de 12,3 € sur le Site ($F=7{,}1$, $p=0{,}003$) et de 26,3 € sur Réseaux ($F=42{,}1$, $p<0{,}0001$).


> ⚠️ **Plans déséquilibrés.** Ici, chaque case contient 10 observations (plan **équilibré**) : les sommes de carrés sont uniques et les facteurs « orthogonaux ». Quand les effectifs diffèrent selon les cases, la décomposition dépend de l'ordre des facteurs (sommes de carrés de type I, II ou III). Préférez alors l'interprétation par les **coefficients du modèle** et des tests ciblés plutôt que la lecture mécanique du tableau d'ANOVA. C'est une raison de plus de **planifier des plans équilibrés**.

### 8.2.10 Combien d'observations ? La puissance d'une ANOVA

Avant l'expérience, on doit se demander : *si l'effet que je cherche existe vraiment, aurai-je de bonnes chances de le voir ?* C'est la **puissance** (volume I, section 3.5.4). Pour l'ANOVA, sous une hypothèse alternative donnée, la statistique $F$ suit une loi de Fisher **non centrale**, de paramètre de non-centralité

$$\lambda=\frac{\sum_i n_i\tau_i^2}{\sigma^2}=N f^2,$$

où $f=\sqrt{\sum_i\tau_i^2/k}\,/\,\sigma$ est l'effet de Cohen (8.2.7). La puissance est $\mathbb P\left(F>F_{1-\alpha}\right)$ sous cette loi.

Reprenons l'expérience de la vitrine **telle qu'elle a été planifiée** : moyennes vraies 200, 215, 240 et 205 €, écart-type $\sigma=30$ €, 12 jours par agencement.


La puissance **prévue** était d'environ **83 %** : la formule (loi de Fisher non centrale), `statsmodels` et la simulation (5 000 expériences rejouées) s'accordent à quelques millièmes près. Avec l'effet que la gérante espérait, l'expérience de 12 jours par agencement était donc **bien dimensionnée**. Le $p=0{,}036$ observé, proche du seuil, n'a rien de contradictoire : le $F$ observé (3,10) est simplement inférieur à celui qu'on attend en moyenne avec l'effet espéré (environ $1+\lambda/(k-1)\approx5{,}2$, avec $\lambda=Nf^2\approx12{,}7$) : une fluctuation d'échantillonnage ordinaire, qui arrive environ une fois sur cinq. Et si l'effet réel n'était que **moitié moindre** que celui espéré ?


Dessinons la puissance en fonction du nombre de jours, pour plusieurs tailles d'effet :


Avec un effet moitié moindre, la puissance de la même expérience tombe à **27 %** : plus de deux fois sur trois, elle passerait à côté de l'effet. Pour retrouver 80 %, il faudrait **43 jours par agencement**, soit 172 jours (près de six mois d'ouverture) : diviser l'effet par deux multiplie par environ **quatre** le nombre d'essais nécessaires, car la taille d'échantillon varie comme $1/f^2$. C'est la raison pour laquelle on dimensionne l'expérience sur le **plus petit effet qui vaille la peine d'être détecté**.

![Courbes de puissance du test F à 4 groupes selon le nombre de jours par agencement, pour quatre tailles d'effet ; la ligne pointillée horizontale marque 80 %, la verticale 12 jours.](figures/ch08-puissance.png)

> 💡 **La leçon.** On calcule la puissance **avant** de lancer l'expérience, avec l'effet qu'on juge **utile** de détecter (pas celui qu'on espère). Une expérience sous-dimensionnée est pire qu'inutile : elle produit des résultats instables, et quand elle « réussit », elle tend à **surestimer** l'effet (l'effet significatif d'une expérience peu puissante est en moyenne exagéré).

### 8.2.11 La même chose en R

Les statisticiens utilisent souvent R pour l'ANOVA. Voici le même calcul, sur le même fichier, avec `aov` et `TukeyHSD`. C'est une bonne habitude de refaire une analyse dans un second logiciel : deux programmes écrits indépendamment qui donnent les mêmes nombres sont une vérification bien plus solide que n'importe quelle relecture. Comparez avec 8.2.3 et 8.2.6 : on doit retrouver $F=3{,}097$ avec $p=0{,}0363$ sur 3 et 44 degrés de liberté, et, pour Tukey, un écart « Par thème − Classique » de 40,7 € avec une $p$ ajustée de 0,025 (les autres comparaisons restant non significatives).

```r
d <- read.csv("donnees/ch08-vitrines.csv", fileEncoding = "UTF-8")
d$agencement <- factor(d$agencement)
fit <- aov(ventes ~ agencement, data = d)
print(summary(fit))
```
<!--sortie-->
```text
            Df Sum Sq Mean Sq F value Pr(>F)  
agencement   3  10595    3532   3.097 0.0363 *
Residuals   44  50168    1140                 
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
```


Le tableau d'analyse de variance est identique et `TukeyHSD` redonne les mêmes comparaisons (au détail d'arrondi près). Changer d'outil ne change pas les mathématiques.

### 8.2.12 Ce que cachaient les données

Les données étant simulées, nous connaissons la vérité (script `build/donnees_ch08.py`). Pour la vitrine, les moyennes vraies étaient **200, 215, 240 et 205 €** pour Classique, Par couleur, Par thème et Vedette, avec un bruit de 30 €. Les écarts **observés** par rapport à « Classique » dans l'expérience à 48 jours (+28, +41 et +19 € pour Par couleur, Par thème et Vedette) en sont proches mais pas identiques à ceux qui étaient programmés (+15, +40 et +5) : l'erreur d'estimation d'un écart est ici d'environ 14 € (un écart-type), et le hasard a fait **sur-estimer** l'avantage de « Par couleur » et de « Vedette ». Avec 12 jours par groupe, on ne peut espérer que des ordres de grandeur. Dans l'expérience en blocs, les effets vrais étaient $0,\ 15,\ 40,\ 5$ € et les écarts estimés sont +17, +43 et +11 €, avec une erreur d'estimation d'environ 7 €, deux fois plus petite : c'est le gain de précision apporté par les blocs. Pour l'emballage, l'interaction était programmée : le coffret apporte $+10$ € au site mais $+22$ € sur Réseaux.

> ✅ **À retenir.**
> - L'ANOVA **décompose la variabilité** : $SS_T=SS_B+SS_W$, exactement ; le test $F=MS_B/MS_W\sim\mathcal F(k-1,N-k)$ sous $H_0$ compare variabilité entre et à l'intérieur des groupes.
> - Avec deux groupes, $F=t^2$ ; avec $k$ groupes, l'ANOVA est une **régression sur des indicatrices** ($R^2=\eta^2$).
> - On **vérifie les hypothèses** sur les résidus (normalité, variances égales) ; alternatives : Welch, transformation, Kruskal-Wallis.
> - Un $F$ significatif ne dit pas **quels** groupes diffèrent : utiliser **Tukey** (ou Bonferroni), ou un **contraste planifié** posé *avant* l'expérience.
> - **Taille d'effet** : $\eta^2$, $\omega^2$, $f$ ; une p-valeur n'est pas une mesure d'importance.
> - Les **blocs** retirent du bruit connu : à nombre d'essais égal, l'effet peut passer de « invisible » à « très net ».
> - À **deux facteurs**, regardez d'abord l'**interaction** ; si elle existe, étudiez les **effets simples**, pas les effets principaux.
> - **Calculez la puissance avant** l'expérience : une expérience sous-dimensionnée n'est pas fiable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.2 à 8.6, exercices 8.2 à 8.5 et 8.12.


## 8.3 Les plans factoriels

> 💡 **Intuition.** En 8.1, nous avons vu que changer un facteur à la fois gaspille des essais et rate les interactions. Un plan **factoriel complet** à $k$ facteurs, chacun à **deux niveaux**, fait l'inverse : on teste **toutes** les $2^k$ combinaisons. Chaque essai sert ensuite à estimer **tous** les effets à la fois (les effets principaux comme les interactions), et chaque effet est mesuré sur **tous** les essais, en comparant « la moitié haute » à « la moitié basse ». C'est le plan le plus efficace que l'on puisse imaginer pour un nombre de facteurs modéré.

### 8.3.1 L'expérience de la gérante : trois facteurs, huit combinaisons

La gérante veut booster les commandes hebdomadaires de sa boutique en ligne. Trois leviers l'intéressent, chacun à deux niveaux :

| Facteur | Niveau « − » (−1) | Niveau « + » (+1) |
|---|---|---|
| **A** : emballage | standard | cadeau |
| **B** : prix | normal | promotion de 10 % |
| **C** : relance | e-mail | publication sur les réseaux sociaux |

Il y a $2^3=8$ combinaisons. Chaque combinaison est testée sur **deux semaines** (deux **répétitions**), tirées au hasard dans le calendrier : $16$ semaines au total. La réponse est le nombre de commandes de la semaine.

> 💡 **Le codage $-1/+1$.** On code les niveaux « bas » et « haut » par $-1$ et $+1$ (plutôt que 0 et 1). C'est plus qu'une convention : ce codage symétrique rend les colonnes du plan **orthogonales**, ce qui simplifie tous les calculs, comme nous allons le voir.

Voici le plan, avec le tableau des signes de tous les effets possibles. Les colonnes d'interaction sont les **produits** des colonnes des facteurs concernés : si A et B valent $-1$ et $+1$, l'interaction AB vaut $-1\times(+1)=-1$.


| | I | A | B | C | AB | AC | BC | ABC |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| (1) | 1 | −1 | −1 | −1 | 1 | 1 | 1 | −1 |
| a | 1 | 1 | −1 | −1 | −1 | −1 | 1 | 1 |
| b | 1 | −1 | 1 | −1 | −1 | 1 | −1 | 1 |
| ab | 1 | 1 | 1 | −1 | 1 | −1 | −1 | −1 |
| c | 1 | −1 | −1 | 1 | 1 | −1 | −1 | 1 |
| ac | 1 | 1 | −1 | 1 | −1 | 1 | −1 | −1 |
| bc | 1 | −1 | 1 | 1 | −1 | −1 | 1 | −1 |
| abc | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Les huit lignes sont les huit combinaisons (« a » signifie A haut, B et C bas ; « abc », tout haut ; « (1) », tout bas). Le produit $S^\top S$ vaut $8\times$ la matrice identité : **les huit colonnes sont orthogonales** (le produit scalaire de deux colonnes distinctes est nul) et chacune a une norme de $\sqrt8$. Tout ce chapitre repose sur cette propriété.

### 8.3.2 Les effets, à la main

Les données de l'expérience (ordre des essais tiré au hasard, puis rangées en ordre standard) :


```text
replicat     1     2  moyenne
(1)       49.9  45.9    47.90
a         57.1  65.3    61.20
b         69.4  64.6    67.00
ab        68.4  56.9    62.65
c         45.8  51.5    48.65
ac        62.1  59.8    60.95
bc        70.1  64.4    67.25
abc       73.2  78.1    75.65
```

On définit l'**effet principal** d'un facteur comme la **différence moyenne de réponse** quand ce facteur passe de son niveau bas à son niveau haut, **en moyennant sur les niveaux des autres facteurs**. Par exemple, l'effet de A est la moyenne des quatre combinaisons où A est haut, moins la moyenne des quatre où A est bas :

$$\text{effet}(A)=\bar y_{A+}-\bar y_{A-}.$$

L'**interaction** AB est la demi-différence entre l'effet de A quand B est haut et l'effet de A quand B est bas ; de façon équivalente, c'est la différence entre la moyenne des cellules où AB $=+1$ et celle où AB $=-1$. **La même règle s'applique à toutes les colonnes du tableau des signes** : l'effet d'une colonne est la moyenne des réponses là où elle vaut $+1$ moins la moyenne là où elle vaut $-1$. Avec $\bar y_i$ les huit moyennes de cellules et $s_i$ le signe de la colonne :

$$\text{effet}=\frac{1}{4}\sum_{i=1}^{8}s_i\,\bar y_i\qquad\left(\text{plus généralement }\frac{1}{2^{k-1}}\sum_i s_i\bar y_i\right).$$


```text
A       7.41
B      13.46
C       3.44
AB     -5.39
AC      2.94
BC      3.19
ABC     3.44

moyenne générale : 61.41
```

Lisez le résultat comme une phrase : « passer de l'emballage standard à l'emballage cadeau fait varier les commandes de $+7{,}4$ en moyenne », etc. L'effet du **prix** (B) est le plus grand ; l'interaction AB est négative : l'effet du cadeau est plus faible en promotion, ce qui rappelle exactement l'exemple de 8.1.5.

> 📐 **L'algorithme de Yates.** Avant les ordinateurs, on calculait tous les effets avec une procédure d'additions et de soustractions, qui reste élégante. On écrit les moyennes en ordre standard $(1),a,b,ab,c,ac,bc,abc$. À chaque étape, la nouvelle colonne contient d'abord les **sommes** de paires voisines, puis leurs **différences** (second moins premier). Après $k$ étapes, on obtient les « contrastes » dans l'ordre $I,A,B,AB,C,AC,BC,ABC$ ; il suffit de diviser par $2^{k-1}$ pour obtenir les effets (et par $2^k$ pour la moyenne).


```text
     moyennes  étape 1  étape 2  contraste (étape 3)  effet = contraste / 4
I       47.90   109.10   238.75               491.25                  61.41
A       61.20   129.65   252.50                29.65                   7.41
B       67.00   109.60     8.95                53.85                  13.46
AB      62.65   142.90    20.70               -21.55                  -5.39
C       48.65    13.30    20.55                13.75                   3.44
AC      60.95    -4.35    33.30                11.75                   2.94
BC      67.25    12.30   -17.65                12.75                   3.19
ABC     75.65     8.40    -3.90                13.75                   3.44
```


### 8.3.3 Le lien avec la régression, et la précision des effets

Ces effets sont, à un facteur 2 près, les **coefficients de la régression** de la réponse sur les colonnes du tableau des signes (chapitre 1). C'est la clé pour **tester** et **mesurer l'incertitude**. Écrivons le modèle complet :

$$y=\beta_0+\beta_A x_A+\beta_B x_B+\beta_C x_C+\beta_{AB}x_Ax_B+\dots+\beta_{ABC}x_Ax_Bx_C+\varepsilon,\qquad x\in\{-1,+1\}.$$

> 📐 **Théorème (effets et coefficients).** Dans un plan factoriel complet $2^k$ avec $N$ essais au total, (i) $\widehat\beta_j=\dfrac1N\sum_i s_{ij}\,y_i$ ; (ii) l'effet estimé est $\widehat{\text{effet}}_j=2\widehat\beta_j$ ; (iii) les estimateurs sont **non corrélés** et $\operatorname{Var}(\widehat\beta_j)=\sigma^2/N$, donc
> $$\operatorname{Var}(\widehat{\text{effet}}_j)=\frac{4\sigma^2}{N},\qquad \text{écart-type d'un effet}=\frac{2\sigma}{\sqrt N}.$$
> *Démonstration.* Notons $X$ la matrice $N\times 2^k$ des colonnes du tableau des signes (répétées si l'on a plusieurs répétitions). Ses colonnes sont orthogonales et chacune a une norme au carré égale à $N$ : $X^\top X=N\,I$. Les moindres carrés (chapitre 1, section 1.1) donnent $\widehat\beta=(X^\top X)^{-1}X^\top y=\frac1N X^\top y$, d'où (i). Pour (ii) : quand $x_j$ passe de $-1$ à $+1$, la réponse prédite varie de $2\beta_j$ (les autres termes se compensent en moyenne grâce à l'orthogonalité). Enfin $\operatorname{Var}(\widehat\beta)=\sigma^2(X^\top X)^{-1}=\frac{\sigma^2}{N}I$ : variances égales, covariances nulles ; et $\operatorname{Var}(2\widehat\beta_j)=4\sigma^2/N$. $\square$

Deux conséquences remarquables. **La précision est la même pour tous les effets** et ne dépend que du nombre total d'essais $N$ : tous les essais servent à chaque effet. Et comme les estimateurs sont **non corrélés**, le fait de retirer un effet du modèle ne change pas les estimations des autres. Il reste à estimer $\sigma^2$ : avec des **répétitions**, on dispose de l'**erreur pure**, la variabilité entre les répétitions d'une même combinaison.

```python
import statsmodels.formula.api as smf

mod = smf.ols("commandes ~ A * B * C", data=f3).fit()
res = pd.DataFrame({"effet": 2 * mod.params, "écart-type": 2 * mod.bse, "p": mod.pvalues}).drop("Intercept")
print(res.round(3))
```
<!--sortie-->
```text
        effet  écart-type      p
A       7.413        2.28  0.012
B      13.463        2.28  0.000
A:B    -5.388        2.28  0.046
C       3.437        2.28  0.170
A:C     2.937        2.28  0.234
B:C     3.188        2.28  0.200
A:B:C   3.438        2.28  0.170
```


La colonne « effet » redonne les effets du calcul à la main (au facteur de moyenne près pour $I$). Les écarts-types des effets sont **tous identiques**, comme le prédit le théorème, et valent environ 2,3 commandes (l'erreur pure vaut $s^2=20{,}80$ avec 8 degrés de liberté, soit $s=4{,}56$, et $2s/\sqrt{16}=2{,}28$). Chaque effet a **1 degré de liberté** et la même statistique $t=\text{effet}/\text{ET}$, à $N-8=8$ degrés de liberté (erreur pure). Dans un plan factoriel, la décomposition de la variance de 8.2 devient limpide : la somme de carrés de l'effet $j$ vaut $N\widehat\beta_j^{\,2}=N\cdot(\text{effet}_j/2)^2$ (par exemple $SS_B=725{,}0$ et $SS_A=219{,}8$, contre $166{,}4$ pour l'erreur pure et $1\,396{,}9$ au total ; le tableau d'analyse de variance et cette formule donnent les mêmes valeurs).


### 8.3.4 Lire l'expérience : quels effets comptent ?

Au seuil de 5 %, trois effets ressortent : le **prix** (B), l'**emballage** (A) et leur **interaction** (AB). Les effets de la relance (C) et des autres interactions sont plus petits que le bruit ne permet de le distinguer ($p>0{,}15$ pour chacun). Représentons les résultats : le **cube des moyennes**, puis le graphique d'interaction AB.

![Les huit moyennes de cellules sur un cube dont les arêtes sont les trois facteurs : les valeurs les plus élevées se trouvent du côté « promotion » (haut du cube), et la plus élevée est « tout haut ».](figures/ch08-cube-2p3.png)


![Graphique d'interaction emballage × prix : les deux courbes ne sont pas parallèles ; le cadeau fait nettement monter les commandes au prix normal, beaucoup moins en promotion.](figures/ch08-interaction-AB.png)

On retrouve la même histoire qu'en 8.1.5 : l'emballage cadeau aide **surtout quand le prix est normal** (il remplace en quelque sorte la promotion) ; en promotion, son apport est bien plus faible. Les deux leviers sont **partiellement substituables**. Un décideur qui n'aurait regardé que les effets principaux aurait conclu « faites les deux » sans voir qu'ils se gênent un peu.

**Modèle réduit et prédiction.** Puisque les effets non significatifs ne se distinguent pas du bruit, on peut les retirer du modèle. Comme les estimateurs sont non corrélés, les effets restants **ne changent pas**, mais l'erreur est estimée avec plus de degrés de liberté. On peut alors prédire la réponse aux huit réglages et choisir le meilleur.


```text
 A  B  prédiction IC95 de la moyenne
-1 -1        48.3      [42.5 ; 54.0]
 1 -1        61.1      [55.3 ; 66.8]
-1  1        67.1      [61.4 ; 72.9]
 1  1        69.2      [63.4 ; 74.9]
```

Le meilleur réglage prédit est « emballage cadeau **et** promotion » (69,2 commandes), mais son gain sur « promotion seule » (67,1) n'est que de 2 commandes et les deux intervalles de confiance se chevauchent largement : compte tenu du coût d'un emballage cadeau, la décision n'est pas évidente. C'est précisément le genre de conclusion nuancée que seule la prise en compte de l'interaction permet. (Un détail instructif : l'écart-type résiduel passe de 4,56 dans le modèle complet à 5,29 dans le modèle réduit, parce que les effets retirés, C et BC, sont **réels** même s'ils sont non significatifs : ils rejoignent alors l'erreur. Simplifier un modèle n'est pas gratuit.)

### 8.3.5 Ce que l'expérience ne détecte pas : la leçon de la puissance

Le modèle programmé pour simuler ces données (que nous dévoilons maintenant) contenait aussi un effet de la relance C (+4 commandes en effet) et une interaction BC (+3). Le tableau ne les a **pas détectés** : $p=0{,}17$ et $p=0{,}20$. Absence de preuve n'est pas preuve d'absence. Calculons la puissance de ce plan pour un effet de 4 commandes, avec le vrai bruit $\sigma=3{,}5$ : l'écart-type d'un effet vaut $2\sigma/\sqrt N$ ; la statistique $t$ suit, sous l'alternative, une loi de Student **non centrale** de paramètre $\delta=\Delta/(2\sigma/\sqrt N)$.

```text
 répétitions r  essais N = 8 r  ddl erreur pure  ET d'un effet  puissance (effet = 4)
             1               8              NaN          2.475                    NaN
             2              16              8.0          1.750                  0.520
             3              24             16.0          1.429                  0.748
             4              32             24.0          1.237                  0.873
             6              48             40.0          1.010                  0.971
```

Sans répétition ($r=1$), il n'y a pas d'erreur pure, donc pas de test du tout (la case reste vide). Avec deux répétitions, la puissance pour détecter un effet de 4 commandes n'est que de **52 %**, un peu plus de la moitié : l'expérience avait donc à peu près une chance sur deux de rater un effet pourtant réel et non négligeable. Il aurait fallu **quatre répétitions** (32 semaines) pour dépasser 80 % (87 %), trois ne donnant que 75 %. C'est l'arbitrage permanent de l'expérimentateur : *plus de facteurs et peu de répétitions* (on repère les gros effets) ou *moins de facteurs et plus de répétitions* (on repère les petits). La section suivante montre comment obtenir davantage avec moins d'essais.

### 8.3.6 Sans répétition : le plan $2^4$ et le diagramme demi-normal

Les répétitions coûtent cher. Quand on teste plus de facteurs (disons quatre : on ajoute **D**, un message personnalisé), le plan $2^4$ n'a que $16$ essais, **sans répétition**. Il estime $15$ effets (4 principaux, 6 interactions d'ordre 2, 4 d'ordre 3 et 1 d'ordre 4) avec $16$ essais : plus aucun degré de liberté pour l'erreur pure. Comment tester ? On s'appuie sur un principe d'expérience, observé dans une immense majorité d'études :

> 💡 **Le principe de parcimonie des effets.** Parmi de nombreux effets possibles, **peu sont réellement actifs**, et les interactions d'ordre élevé (trois facteurs ou plus) sont presque toujours négligeables. Les effets *inactifs* sont donc des **estimations du pur bruit** : ils se répartissent autour de 0 selon une loi normale de même écart-type. Il suffit de repérer ceux qui s'en écartent.

La première idée est le **diagramme demi-normal** (*half-normal plot*). On range les valeurs absolues des $m$ effets par ordre croissant $|c|_{(1)}\le\dots\le|c|_{(m)}$ et on les compare aux quantiles attendus pour la valeur absolue d'une loi normale : $z_i=\Phi^{-1}\left(0{,}5+0{,}5\,\dfrac{i-0{,}5}{m}\right)$. Si **tous** les effets étaient du bruit, les points s'aligneraient sur une droite passant par l'origine, de pente $\sigma_c$ (l'écart-type d'un effet). Les effets **actifs** sortent de la droite, vers le haut.

La seconde idée, **la méthode de Lenth**, chiffre cette intuition sans modèle d'erreur. Notons $c_j$ les $m$ effets estimés :

- $s_0=1{,}5\times\operatorname{médiane}|c_j|$, une première estimation de l'écart-type du bruit (robuste : la médiane ignore les quelques effets actifs) ;
- $\text{PSE}=1{,}5\times\operatorname{médiane}\{|c_j|:\ |c_j|<2{,}5\,s_0\}$, l'estimation « **pseudo-erreur standard** » obtenue après avoir écarté les effets manifestement actifs ;
- la **marge d'erreur** $\text{ME}=t_{0{,}975;\,d}\times\text{PSE}$ avec $d=m/3$, et la marge **simultanée** $\text{SME}=t_{\gamma;\,d}\times\text{PSE}$ avec $\gamma=\dfrac{1+0{,}95^{1/m}}{2}$, qui tient compte du fait qu'on teste $m$ effets à la fois.

Un effet dont la valeur absolue dépasse la SME est déclaré actif (la ME est plus permissive).


![Diagramme demi-normal des 15 effets d'un plan 2⁴ non répliqué : onze points suivent la droite du bruit près de l'origine, quatre points actifs (B, A, AB et D) s'en détachent nettement et dépassent le seuil SME.](figures/ch08-demi-normal.png)

Sur ces données, $s_0=1{,}01$, $\text{PSE}=0{,}90$, $\text{ME}=2{,}31$ et $\text{SME}=4{,}70$. Le diagramme montre onze points alignés sur la droite du bruit et quatre points qui s'en détachent : **B, A, AB et D** (effets de 12,2, 9,5, −5,7 et 5,2 contre une SME de 4,7). Remarquez que D, avec 5,2, ne dépasse la SME que de peu : avec un bruit un peu plus fort, il aurait pu passer inaperçu. Les onze autres, dont toutes les interactions d'ordre 3 et 4, sont indiscernables du bruit. Ce résultat se confirme par une régression sur les seuls effets actifs, en reversant les degrés de liberté « libérés » (les 11 effets retirés) à l'**erreur** : on obtient $s=1{,}45$ avec 11 degrés de liberté, $R^2=0{,}981$, et quatre effets tous significatifs ($p<0{,}001$).


> ⚠️ **Prudence.** Cette démarche **cherche** les effets actifs dans les données : les tests qui suivent sont donc un peu optimistes (on a choisi les effets *parce qu'ils étaient grands*). La méthode de Lenth contrôle ce biais avec la SME, la régression finale non. Un plan non répliqué doit être **confirmé** par quelques essais supplémentaires au réglage retenu.

### 8.3.7 Ce que cachaient les données

Révélons la vérité (`build/donnees_ch08.py`).

- **Plan $2^3$** : en unités codées, $y=60+4A+6B+2C-2{,}5AB+1{,}5BC$, donc des **effets** de $8$ (A), $12$ (B), $4$ (C), $-5$ (AB), $3$ (BC) et $0$ pour AC et ABC, avec un écart-type du bruit $\sigma=3{,}5$. L'expérience a bien trouvé les trois effets les plus grands (A, B, AB), avec des estimations proches des vraies valeurs ($7{,}4$ pour 8, $13{,}5$ pour 12, $-5{,}4$ pour $-5$), et **manqué** C et BC, qui sont plus petits que le bruit ne permet de voir avec 16 essais. Elle a aussi produit deux « effets » (AC et ABC, à environ 3) qui n'existent pas : à environ 1,3 à 1,5 écart-type de zéro (l'écart-type d'un effet est de 2,3), ce sont des fluctuations d'échantillonnage ordinaires, qui n'ont d'ailleurs pas dépassé le seuil de significativité.
- **Plan $2^4$** : $y=60+4A+6B-3AB+2{,}5D$, soit des effets de $8$, $12$, $-6$ et $5$ ; les 11 autres effets valent 0. La méthode de Lenth a retrouvé **exactement** les quatre effets actifs, sans en inventer un seul, avec des estimations proches de la vérité ($9{,}5$, $12{,}2$, $-5{,}7$, $5{,}2$) et un bruit de $\sigma=1{,}5$ cette fois plus faible.

> ✅ **À retenir.**
> - Un plan factoriel complet $2^k$ teste toutes les combinaisons et estime **tous** les effets (principaux et interactions) avec **tous** les essais.
> - Codé en $\pm1$, le plan est **orthogonal** : $X^\top X=N\,I$ ; effet $=2\times$ coefficient de régression, **tous les effets ont le même écart-type** $2\sigma/\sqrt N$ et sont non corrélés.
> - Les effets se calculent à la main (**contrastes**, algorithme de **Yates**) et se testent par régression avec l'**erreur pure** des répétitions.
> - Les **interactions** sont lues sur le **graphique d'interaction** et le **cube** ; ne parlez pas d'un effet principal quand l'interaction domine.
> - Sans répétition, le **diagramme demi-normal** et la **méthode de Lenth** repèrent les effets actifs en s'appuyant sur la **parcimonie des effets**.
> - Un test non significatif ne prouve pas l'absence d'effet : calculez la **puissance** du plan pour l'effet qui compte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.7 et 8.8, exercices 8.6 à 8.8 et 8.13.


## 8.4 Plans fractionnaires et surfaces de réponse

> 💡 **Intuition.** Le plan factoriel complet est généreux : $2^k$ essais pour $k$ facteurs. Mais le nombre d'essais double à chaque facteur ajouté, alors que la plupart des interactions d'ordre élevé sont négligeables. Un **plan fractionnaire** n'exécute qu'une **fraction** ($\tfrac12$, $\tfrac14$…) des combinaisons, bien choisie, en **acceptant de confondre** certains effets entre eux : on économise des essais en renonçant à distinguer des effets que l'on juge de toute façon petits. La seconde moitié de la section est consacrée à un autre but : non plus *repérer les facteurs qui comptent*, mais **trouver le meilleur réglage** de deux facteurs continus, avec les **surfaces de réponse**.

### 8.4.1 Le problème : $2^k$ explose

Combien d'effets contient un plan complet, et de quel ordre ?

```text
 facteurs k  essais 2^k  principaux  interactions d'ordre 2  d'ordre 3  d'ordre 4 et plus  total d'effets
          3           8           3                       3          1                  0               7
          4          16           4                       6          4                  1              15
          5          32           5                      10         10                  6              31
          7         128           7                      21         35                 64             127
```

Avec 7 facteurs, un plan complet demande **128 essais** pour estimer 127 effets, dont **7 seulement** sont des effets principaux et **21** des interactions d'ordre 2 : les $99$ autres sont des interactions d'ordre 3 ou plus, presque toujours négligeables en pratique. C'est un énorme gaspillage. Le **principe de hiérarchie** dit que les effets principaux sont plus importants que les interactions d'ordre 2, elles-mêmes plus importantes que celles d'ordre 3, etc. Joint au principe de parcimonie (8.3.6), il justifie de **sacrifier les interactions d'ordre élevé**. Le coût est aussi très concret : avec un essai par semaine, 128 essais représentent plus de deux ans d'expérience, pendant lesquels le contexte (prix des matières, concurrence, saisons) aura eu le temps de changer. Raison de plus pour ne pas payer des essais qui ne servent qu'à mesurer des interactions d'ordre 5, 6 ou 7 que l'on sait pratiquement nulles.

### 8.4.2 Une demi-fraction : le plan $2^{4-1}$

Reprenons les quatre facteurs de l'expérience $2^4$ de 8.3.6 (A emballage, B prix, C relance, D message personnalisé), mais supposons que la gérante n'ait pu faire que **8 essais** au lieu de 16. Comment choisir 8 combinaisons parmi 16 ?

Construisons un plan complet $2^3$ sur A, B, C, et **définissons D comme le produit** $D=ABC$ : la colonne de D n'est plus libre, elle est **imposée** par les trois autres. C'est le **générateur** de la fraction. Multiplier les deux membres par $D$ donne la **relation de définition** :
$$D=ABC\ \Longrightarrow\ D\cdot D=ABC\cdot D\ \Longrightarrow\ I=ABCD,$$
puisque $D\cdot D=I$ (le produit d'une colonne $\pm1$ par elle-même vaut $+1$). Toute la structure de confusion découle de cette seule relation.

> 📐 **Confusion (alias).** Si $I=ABCD$, alors multiplier un effet par $ABCD$ donne l'effet confondu avec lui : $A=A\cdot ABCD=BCD$, $B=ACD$, $C=ABD$, $D=ABC$, et pour les interactions d'ordre 2, $AB=CD$, $AC=BD$, $AD=BC$. Les colonnes du tableau des signes de ces effets sont **identiques** dans les 8 essais : il est mathématiquement impossible de les distinguer. Le contraste calculé sur la colonne de A estime donc **la somme** $A+BCD$ ; si l'interaction d'ordre 3 $BCD$ est négligeable (c'est l'hypothèse de hiérarchie), c'est bien l'effet de A.

Vérifions-le numériquement, puis utilisons la **vraie** expérience : parmi les 16 essais de 8.3.6, ne gardons que les 8 pour lesquels $ABCD=+1$ (c'est exactement la fraction définie par $I=ABCD$) et comparons les effets estimés avec ceux du plan complet.


```text
      contraste estime  demi-fraction (8 essais)  somme des 2 effets du plan complet
A              A + BCD                      9.00                                9.00
B              B + ACD                     11.10                               11.10
A:B            AB + CD                     -6.35                               -6.35
C              C + ABD                     -1.20                               -1.20
A:C            AC + BD                     -0.45                               -0.45
B:C            BC + AD                      0.15                                0.15
A:B:C          ABC + D                      6.50                                6.50
```


Chaque ligne de la demi-fraction estime **la somme** de deux effets, et la comparaison le confirme **exactement** : l'estimation obtenue avec 8 essais est égale, au centième près, à la somme des deux effets correspondants du plan complet. (On peut le démontrer : sur la fraction, $A=BCD$, donc $\sum_{\text{moitié}}A\,y=\tfrac12\left(\sum_{\text{tous}}A\,y+\sum_{\text{tous}}BCD\,y\right)$, ce qui donne $\hat\ell_A=\hat A+\widehat{BCD}$.) Comme les interactions d'ordre 3 sont presque nulles, les estimations de A, B et de D (ligne « ABC + D ») sont proches de celles du plan complet : avec 8 essais au lieu de 16, on aurait tiré les mêmes conclusions. (Le contraste « AB + CD » ne permet pas de dire à lui seul que c'est AB plutôt que CD : c'est la **connaissance du domaine**, ou une expérience complémentaire, qui tranche.)

### 8.4.3 Résolution : mesurer la qualité d'une fraction

Dans $I=ABCD$, le seul « mot » a **4 lettres**. On appelle **résolution** d'un plan fractionnaire la **longueur du plus court mot** de sa relation de définition, notée en chiffres romains. Elle résume ce qui est confondu avec quoi :

| Résolution | Plus court mot | Les effets principaux sont confondus avec… | Les interactions d'ordre 2 sont confondues avec… |
|---|---|---|---|
| **III** | 3 lettres | des interactions d'ordre 2 | des effets principaux |
| **IV** | 4 lettres | des interactions d'ordre 3 | **entre elles** |
| **V** | 5 lettres | des interactions d'ordre 4 | des interactions d'ordre 3 |

> 📐 **Pourquoi la longueur du plus court mot ?** Un effet de $j$ lettres est confondu avec le produit de cet effet par chaque mot $w$ de la relation. Ce produit a $|j - \ell|$ lettres au moins, où $\ell$ est la longueur de $w$, et au plus $j+\ell$. Avec un mot de $\ell$ lettres, un effet principal ($j=1$) est donc confondu avec un effet d'ordre au moins $\ell-1$, et une interaction d'ordre 2 avec un effet d'ordre au moins $\ell-2$. Plus $\ell$ est grand, plus la confusion est entre des effets d'ordre élevé, donc négligeables. D'où la règle de choix : **à nombre d'essais donné, on cherche la résolution la plus élevée**.

Une demi-fraction de résolution IV ($2^{4-1}$ avec $I=ABCD$) est un excellent compromis : les effets principaux sont libres de toute interaction d'ordre 2.

### 8.4.4 Plus fractionnaire encore : le plan $2^{5-2}$ et le piège de la confusion

Pour cinq facteurs, un plan complet demande 32 essais. Un plan à **8 essais** seulement est possible : on part du plan complet $2^3$ en A, B, C et on **définit deux facteurs de plus** par $D=AB$ et $E=AC$. C'est un plan $2^{5-2}$ (un quart de fraction). Les relations de définition sont $I=ABD$ et $I=ACE$, et **leur produit** $ABD\cdot ACE=A^2BCDE=BCDE$ est aussi une relation :
$$I=ABD=ACE=BCDE.$$
Le plus court mot a 3 lettres : **résolution III**. Calculons toute la structure de confusion par programme : un effet est confondu avec son produit par chaque mot, et le produit de deux ensembles de lettres est la **différence symétrique** (les lettres communes s'annulent car $L^2=I$).


```text
31 effets possibles, répartis en 8 classes de confusion (8 essais = 7 contrastes + la moyenne) :

  I = ABD = ACE = BCDE
  A = BD = CE = ABCDE
  B = AD = CDE = ABCE
  C = AE = BDE = ABCD
  D = AB = BCE = ACDE
  E = AC = BCD = ABDE
  BC = DE = ABE = ACD
  BE = CD = ABC = ADE
```

Chaque ligne est une **classe de confusion** : les effets d'une même ligne ne peuvent pas être distingués. La première ligne regroupe les trois mots de la relation de définition avec la **moyenne générale** $I$ : ces trois interactions sont indiscernables de la constante. Remarquez que les effets principaux sont confondus avec des interactions d'ordre 2 (par exemple $D=AB$ : le facteur D est parfaitement confondu avec l'interaction de A et B). C'est le défaut de la résolution III, et voici ce que cela donne en pratique.

> ⚠️ **Une simulation instructive.** Supposons que la vérité soit la suivante : A a un effet de $+6$, B de $+4$, **A et B ont une interaction de $+8$**, et **D n'a aucun effet**. (Nous le savons parce que nous simulons ; dans la vraie vie, on l'ignore.) On exécute les 8 essais du plan $2^{5-2}$.

```text
A                  5.95
B                  4.76
C                 -0.56
D (= AB)           8.17
E (= AC)          -0.23
BC (= DE)          0.09
ABC (= CD = BE)   -0.51
```

Le tableau annonce un « effet de D » d'environ **8** (la colonne D, qui est aussi la colonne AB, capte l'interaction réelle) alors que **D n'a aucun effet** ! Un analyste qui suppose les interactions négligeables conclurait « le message personnalisé fait gagner 8 commandes », et se tromperait. C'est le danger de la résolution III : on ne peut s'y fier que si l'on est certain que les interactions d'ordre 2 sont absentes.

**Le remède : le repliement (*fold-over*).** On exécute une **seconde série de 8 essais** en **inversant tous les signes** du plan ($A\to-A$, etc.). Les relations de définition de longueur impaire changent de signe d'un bloc à l'autre et disparaissent du plan combiné ; il ne reste que $I=BCDE$ : on obtient un plan de **résolution IV à 16 essais**, dans lequel les effets principaux sont séparés de toutes les interactions d'ordre 2.


Après le repliement, l'effet de **D** est proche de zéro et celui de l'interaction **AB** réapparaît (environ 8) : les deux, qui étaient confondus dans le plan à 8 essais, sont maintenant distincts. On a payé 8 essais supplémentaires pour lever l'ambiguïté. Dans la pratique, on n'exécute le repliement **que si** la première série laisse un doute sur un effet important.

### 8.4.5 Optimiser un réglage : les surfaces de réponse

Jusqu'ici, nous cherchions *quels* facteurs comptent. Voici une autre question : **quel réglage donne la meilleure réponse ?** la gérante cuit ses céramiques au four et veut maximiser le **pourcentage de pièces sans défaut**. Deux réglages continus : la **température** (autour de 1 000 °C) et la **durée** (autour de 6 heures). La **méthodologie des surfaces de réponse** (*response surface methodology*) procède par étapes :

1. un plan factoriel à deux niveaux **avec points au centre** pour détecter si la réponse est une surface **plane** (modèle du premier ordre) ou **courbe** ;
2. si la surface est plane, on suit le **chemin de plus forte pente** (la direction du gradient) jusqu'à ce que la réponse cesse de monter ;
3. au voisinage de l'optimum, la surface est **courbe** : on ajuste un modèle du **second ordre** (quadratique) avec un plan adapté, le **plan composite centré**, puis on cherche son sommet.

On travaille en **unités codées** : $x_1=(\text{température}-1000)/40$ et $x_2=\text{durée}-6$, de sorte que le centre est $(0,0)$ et le cube vaut $\pm1$. Voici le plan composite centré réalisé : 4 points **factoriels** $(\pm1,\pm1)$, 4 points **axiaux** $(\pm\sqrt2,0)$ et $(0,\pm\sqrt2)$, et **5 répétitions du point central**, soit 13 essais.


> 💡 **Pourquoi ces points ?** Un plan à deux niveaux ne peut pas estimer les termes **quadratiques** $x_1^2$ et $x_2^2$ : $(\pm1)^2=1$ pour tous les points, la colonne est constante. Les **points axiaux** ($\pm\sqrt2$) et **centraux** (0) donnent trois niveaux de chaque facteur, ce qui permet de les estimer. Les **répétitions au centre** servent à estimer l'**erreur pure**, donc à tester la qualité de l'ajustement. Le choix $\alpha=\sqrt2=\sqrt[4]{n_{\text{fact}}}$ rend le plan **rotatable** : la précision de la prédiction ne dépend que de la distance au centre, pas de la direction.

**Étape 1 : y a-t-il de la courbure ?** Avec les seuls points factoriels et centraux, on compare la moyenne des points factoriels à celle du centre : si la surface était plane, elles seraient égales en moyenne. L'écart-type est estimé par les 5 répétitions du centre.


Le centre est **nettement au-dessus** de la moyenne des coins (83,8 % de pièces sans défaut au centre contre 74,1 % aux coins ; avec l'erreur pure estimée sur les 5 répétitions, $s=1{,}15$, la statistique vaut $t=-12{,}5$ et $p=0{,}0002$) : la réponse a un **sommet** à l'intérieur du carré, et un modèle plan serait faux. Inutile de suivre un chemin de plus forte pente : nous sommes déjà près de l'optimum, et il faut un modèle courbe.

### 8.4.6 Ajuster le modèle quadratique

Le modèle du second ordre pour deux facteurs s'écrit
$$y=\beta_0+\beta_1x_1+\beta_2x_2+\beta_{11}x_1^2+\beta_{22}x_2^2+\beta_{12}x_1x_2+\varepsilon.$$
C'est une **régression linéaire** (linéaire en les $\beta$) sur six colonnes : les moindres carrés du chapitre 1 s'appliquent tels quels.

```python
import statsmodels.formula.api as smf

q = smf.ols("reussite ~ x1 + x2 + I(x1**2) + I(x2**2) + x1:x2", data=cc).fit()
print(q.params.round(2))
```
<!--sortie-->
```text
Intercept     83.80
x1             2.87
x2             0.57
I(x1 ** 2)    -3.69
I(x2 ** 2)    -6.09
x1:x2          2.68
dtype: float64
```


Les termes quadratiques et le produit $x_1x_2$ sont significatifs ($p<0{,}01$) ; l'effet linéaire de $x_2$ ne l'est pas ($p=0{,}18$). Le modèle explique $R^2=98{,}0\ \%$ de la variabilité, avec un écart-type résiduel $s=1{,}10$ sur 7 degrés de liberté. On le **garde** quand même : par le principe de hiérarchie, on ne retire pas un terme d'ordre 1 si des termes d'ordre supérieur qui le contiennent ($x_2^2$, $x_1x_2$) sont dans le modèle (retirer $\beta_2$ reviendrait à imposer que le sommet soit au centre en $x_2$, ce qui dépend du choix d'origine du codage).

**Le modèle est-il adapté ?** Avec les répétitions au centre, on peut séparer le résidu en **erreur pure** (variabilité entre répétitions) et **défaut d'ajustement** (écart systématique entre le modèle et les moyennes des points) :
$$SS_{\text{résidu}}=SS_{\text{pur}}+SS_{\text{défaut}},\qquad F=\frac{SS_{\text{défaut}}/(\text{ddl}_{\text{res}}-\text{ddl}_{\text{pur}})}{SS_{\text{pur}}/\text{ddl}_{\text{pur}}}.$$
Si $F$ est grand, le modèle quadratique est insuffisant (il faudrait un ordre supérieur ou une autre échelle).


Pas de défaut d'ajustement détectable ($F=0{,}78$, $p=0{,}56$) : le modèle quadratique décrit correctement la surface sur le domaine étudié. (Attention : avec seulement 4 degrés de liberté d'erreur pure, ce test a peu de puissance ; c'est un garde-fou, pas une preuve.)

### 8.4.7 Trouver l'optimum : point stationnaire et analyse canonique

Écrivons le modèle ajusté sous forme matricielle, avec $x=(x_1,x_2)^\top$, $b=(\beta_1,\beta_2)^\top$ et la matrice symétrique des termes quadratiques :
$$\hat y=\beta_0+b^\top x+x^\top Bx,\qquad B=\begin{pmatrix}\beta_{11}&\beta_{12}/2\\ \beta_{12}/2&\beta_{22}\end{pmatrix}.$$

> 📐 **Point stationnaire.** Le gradient de $\hat y$ est $b+2Bx$ (volume I, section 1.2 pour le gradient, et section 1.3 pour l'optimisation). Il s'annule au point
> $$x_s=-\tfrac12B^{-1}b,\qquad \hat y_s=\beta_0+\tfrac12\,b^\top x_s.$$
> (En effet, $Bx_s=-b/2$ donc $x_s^\top Bx_s=-b^\top x_s/2$, et $\hat y_s=\beta_0+b^\top x_s-b^\top x_s/2$.) La nature de ce point se lit sur les **valeurs propres** de $B$ (volume I, section 1.1.3) : le hessien de $\hat y$ vaut $2B$. Si **toutes** les valeurs propres sont **négatives**, $x_s$ est un **maximum** ; toutes **positives**, un minimum ; de signes **mixtes**, un **col** (point selle), qui n'est pas un optimum. Les **vecteurs propres** donnent les axes de la surface : le long de l'axe de plus petite valeur propre en valeur absolue, la réponse varie peu (une « **crête** » : plusieurs réglages donnent presque le même résultat).


Les deux valeurs propres sont négatives ($-6{,}7$ et $-3{,}1$) : le point stationnaire est bien un **maximum**, à environ **1 018 °C et 6,14 h**, avec un taux prédit de **84,5 %** (intervalle de confiance de la moyenne : 83,3 à 85,6 %). La surface retombe deux fois plus vite le long du premier axe (direction $(-0{,}41;\,+0{,}91)$, surtout la durée) que le long du second (direction $(-0{,}91;\,-0{,}41)$, surtout la température) : une durée mal réglée coûte plus cher qu'une température un peu décalée. Le sommet se trouve à l'intérieur du domaine expérimental (distance au centre de 0,46, bien inférieure au rayon $\sqrt2$ des points axiaux) : c'est une **interpolation**, ce qui est crucial ; extrapoler un modèle quadratique au-delà des essais est dangereux, car un polynôme du second degré n'a aucune raison de bien décrire la surface loin des données.

![Surface ajustée du taux de pièces sans défaut en fonction de la température et de la durée (unités codées), avec les 13 points du plan composite centré et l'optimum estimé. Les courbes de niveau sont des ellipses allongées et inclinées autour du sommet.](figures/ch08-rsm-contours.png)

La figure (code dans `build/fig_ch08.py`) montre les courbes de niveau : des **ellipses** centrées sur le sommet, inclinées à cause du terme croisé $\beta_{12}$ (température et durée **interagissent** : la meilleure durée dépend de la température). La différence entre les deux valeurs propres se voit dans la forme des ellipses : plus étroites dans la direction de forte courbure.

**Confirmer.** Un optimum prédit par un modèle est une **hypothèse** : on la teste par quelques **essais de confirmation** au réglage proposé. Nous simulons ici trois fournées au sommet estimé (avec le vrai processus, que nous connaissons, et son bruit de 0,9) :


> ⚠️ **Les pièges de l'optimisation.**
> - Un **col** ou une **crête** (valeur propre presque nulle) ne désigne pas un optimum unique : il faut se demander quel réglage de la crête est le plus **économique** ou le plus **robuste** (par exemple, moins sensible aux variations de température du four).
> - L'optimum n'est valable que **dans le domaine étudié** et pour **la réponse mesurée** : avec **plusieurs réponses** (taux de réussite, coût énergétique, durée), on cherche un compromis (fonctions de désirabilité, courbes de niveau superposées).
> - Le modèle quadratique est une **approximation locale** : si l'optimum prédit tombe en dehors du domaine, on déplace le plan dans cette direction et on recommence plutôt que d'extrapoler.

### 8.4.8 ➕ Pour aller plus loin : les plans optimaux

> 🧭 **Section optionnelle.** Les plans classiques (factoriels, composites) supposent un domaine régulier (un cube) et un nombre d'essais « rond ». Quand le domaine est irrégulier (combinaisons **impossibles**), ou quand le budget impose un nombre d'essais particulier, on peut **calculer** un plan par ordinateur.

L'idée de la **$D$-optimalité** : la variance des coefficients estimés est proportionnelle à $(X^\top X)^{-1}$ (chapitre 1, section 1.2) ; on cherche les essais qui rendent cette matrice « la plus petite », c'est-à-dire qui **maximisent $\det(X^\top X)$**. Le **volume** de l'ellipsoïde de confiance de $\hat\beta$ est en effet proportionnel à $\det(X^\top X)^{-1/2}$. On le fait par un **algorithme d'échange** : on part de $n$ points tirés dans un ensemble de **candidats**, et on remplace un point par un candidat tant que cela augmente le déterminant.


Sur le domaine carré, l'algorithme retrouve **exactement** la grille $3\times3$ classique (le plan factoriel à trois niveaux, de même déterminant, 5 184) : les plans classiques ne sont pas arbitraires, ils sont souvent optimaux. Pour mémoire, 9 points tirés au hasard font en médiane 55 fois moins bien (déterminant de 94). L'intérêt de l'optimisation numérique apparaît dès que le domaine est **contraint** : le plan composite centré serait inutilisable tel quel (le coin $(1,1)$ est impossible), alors que l'algorithme propose immédiatement un plan adapté : la grille $3\times3$ privée du coin impossible, avec le coin opposé $(-1,-1)$ **répété**. Il faut toutefois rester prudent : un plan $D$-optimal dépend **du modèle supposé** (ici un quadratique) ; si le modèle est faux, l'optimalité ne signifie plus grand-chose.

### 8.4.9 Ce que cachaient les données

- **Plan $2^{4-1}$** : les effets de la demi-fraction (A, B, AB, D) sont proches de ceux du plan complet de 8.3.6, ce qui était attendu car la vérité (effets de $8$, $12$, $-6$, $5$ ; le reste nul) respecte la parcimonie. Les confusions A+BCD, etc. n'ont gêné que parce que les interactions d'ordre 3 sont réellement nulles.
- **Plan $2^{5-2}$** : nous avions programmé $A=6$, $B=4$, $AB=8$ et $D=0$. La fraction à 8 essais a attribué **à tort** un effet d'environ 8 à D ; le repliement l'a corrigé. La confusion n'est pas un défaut de calcul, c'est une **conséquence logique** du choix des générateurs.
- **Surface de réponse** : le vrai modèle était $y=84+3x_1+x_2-4x_1^2-6x_2^2+2{,}5x_1x_2$, dont le sommet exact est en $(x_1,x_2)=(0{,}429;\,0{,}173)$, soit environ **1 017 °C** et **6,17 h**, avec un taux maximal de 84,7 %. Le plan à 13 essais a estimé le sommet en $(0{,}441;\,0{,}144)$, soit 1 018 °C et 6,14 h, avec un taux de 84,5 % : à environ 1 °C et 0,03 h de la vérité (1 017 °C, 6,17 h, 84,7 %). Les trois fournées de confirmation (84,1 ; 84,2 ; 83,8) tombent dans l'intervalle de prédiction. Ce niveau de précision est celui d'une expérience **bien conçue et peu bruitée** ($\sigma=0{,}9$) ; avec un bruit plus fort ou moins de répétitions au centre, le sommet estimé aurait été moins précis.

> ✅ **À retenir.**
> - Un plan **fractionnaire** $2^{k-p}$ n'exécute qu'une fraction $2^{-p}$ des combinaisons, définie par des **générateurs** ; les effets sont alors **confondus** (alias) en classes, déterminées par la **relation de définition**.
> - La **résolution** (longueur du plus court mot) dit ce qui est confondu avec quoi : **III** (principaux/interactions d'ordre 2), **IV** (principaux libres, interactions d'ordre 2 entre elles), **V** (tout propre jusqu'à l'ordre 2). À nombre d'essais donné, cherchez la résolution la plus élevée.
> - La confusion peut **tromper** (résolution III) : un **repliement** (inversion de tous les signes) lève l'ambiguïté au prix d'essais supplémentaires.
> - Les **surfaces de réponse** cherchent le meilleur réglage : détecter la **courbure** (points au centre), puis ajuster un **modèle quadratique** avec un **plan composite centré** (points factoriels, axiaux, centraux).
> - Le **point stationnaire** $x_s=-\tfrac12B^{-1}b$ est un maximum si les valeurs propres de $B$ sont négatives ; vérifiez qu'il est **dans le domaine**, testez le **défaut d'ajustement**, **confirmez** par des essais.
> - Les **plans optimaux** ($D$-optimalité) calculent un plan quand le domaine ou le budget sortent des cadres classiques ; ils dépendent du modèle supposé.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.9 à 8.11, exercices 8.9 à 8.11.


## Bilan du chapitre 8

Vous savez maintenant :

- **concevoir** une expérience : identifier les facteurs, les niveaux, l'**unité expérimentale** et la réponse ; appliquer la **randomisation** (contre la confusion), la **répétition** (contre le bruit, sans pseudo-réplication) et le **blocage** (contre la variabilité connue) ;
- expliquer pourquoi **changer un facteur à la fois** est moins précis et **aveugle aux interactions** ;
- mener et **démontrer** une **ANOVA** : décomposition $SS_T=SS_B+SS_W$, test $F$, lien avec le test de Student et la **régression**, vérification des hypothèses, **Tukey** et **contrastes**, **tailles d'effet** ($\eta^2$, $\omega^2$, $f$) ;
- analyser un plan **en blocs** et un plan à **deux facteurs** avec **interaction** (lire d'abord le graphique d'interaction, étudier les effets simples) ;
- calculer la **puissance** d'une ANOVA ou d'un plan factoriel *avant* l'expérience, et dimensionner le nombre de répétitions ;
- construire un **plan factoriel $2^k$** et calculer ses **effets à la main** (contrastes, algorithme de Yates), les relier aux coefficients de la régression, et repérer les effets actifs d'un plan non répliqué (diagramme demi-normal, **méthode de Lenth**) ;
- construire un **plan fractionnaire**, déterminer ses **alias** et sa **résolution**, repérer le danger de la confusion et le lever par un **repliement** ;
- optimiser un réglage par la **méthodologie des surfaces de réponse** : test de courbure, **plan composite centré**, modèle quadratique, test de défaut d'ajustement, **point stationnaire** et analyse canonique, essais de confirmation ;
- (en option) situer les **plans optimaux** ($D$-optimalité) pour les domaines contraints.

Ce chapitre a montré qu'un bon plan **simplifie l'analyse** et qu'il détermine, avant la première mesure, ce que l'on pourra conclure. Le chapitre 7 (inférence causale) aborde le problème inverse : que conclure quand on **n'a pas pu** randomiser, comme dans la plupart des données observationnelles de ce livre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.11 et exercices corrigés 8.1 à 8.13.
