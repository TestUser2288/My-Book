# Chapitre 3 : Régression pour les questions métier

> « Toutes choses égales par ailleurs : la plus belle expression de la statistique, et la plus facile à mal employer. »

Un mardi matin de décembre, la gérante pose une feuille sur votre bureau : le planning des soldes de janvier. Elle hésite entre trois semaines de promotion et deux.

— Quand on lance une promotion, on vend plus de commandes, ça se voit. Mais en janvier on vend toujours peu, et en décembre toujours beaucoup. **Combien de commandes la promotion nous fait-elle gagner par jour, vraiment ?** Et la publicité : je dépense plus de 1 000 € par semaine, est-ce que ça rapporte ?

Vous connaissez déjà la moitié de la réponse. Au volume I (section 1.4), vous avez appris à mesurer une **corrélation** et à vous méfier : la publicité et les ventes montent ensemble parce que **la saison** les fait monter ensemble. Mais « se méfier » ne répond pas à la question de la gérante. Il faut un outil qui **sépare les effets** : la part due à la promotion, la part due au jour de la semaine, la part due à la saison, la part due à la publicité. Cet outil, c'est la **régression**.

La régression est probablement la méthode statistique la plus utilisée en entreprise, pour deux raisons très différentes. On peut s'en servir pour **expliquer** (« la promotion augmente les commandes de 19 % ») ou pour **estimer** et prédire (« combien de commandes demain ? »). Ces deux usages ne demandent pas les mêmes précautions, et ce chapitre vous apprend à ne pas les confondre.

## Le chemin de ce chapitre

Le **parcours essentiel** compte deux sections :

- **3.1 Régression linéaire pour expliquer et estimer** : *comment une droite, puis un plan, puis un modèle à plusieurs variables résume-t-il une relation ?* Les moindres carrés à la main, la lecture d'un tableau de résultats, les variables qualitatives (jours, mois, canaux), les logarithmes, les interactions, les vérifications (résidus, colinéarité, valeurs influentes), et la différence entre expliquer et prédire.
- **3.2 Interpréter les coefficients pour des non-spécialistes** : *comment dire ce que le modèle dit, sans trahir ce qu'il dit ?* Les phrases types, les effets en pourcentage, les graphiques d'effets, ce que l'on peut comparer et ce que l'on ne doit pas comparer, et les erreurs de formulation qui font le plus de dégâts.

Une section facultative (➕) complète le tout : **3.3 Régression logistique pour les résultats métier**, quand la grandeur à expliquer n'est plus un nombre mais un oui ou un non (une ligne est-elle retournée ?), avec les cotes, les rapports de cotes et le choix d'un seuil de décision.

> 🧭 **Comment lire ce chapitre.** Le fil conducteur est la question de la gérante. À chaque étape, nous comparons ce que le modèle trouve à ce que nous savons, puisque les données de la boutique sont **simulées** : nous connaissons l'effet **programmé** de la promotion, de la publicité, de la pluie, des jours de la semaine. Cette « vérité » est le moyen de voir quand une régression tient sa promesse, et quand elle ne peut pas la tenir (par exemple quand l'effet est trop petit pour être mesuré).

## Les données du chapitre

> 📦 **Les données.** Deux jeux de la boutique, que vous connaissez depuis le volume I.
>
> - `jours_exploitation.csv` : une ligne par jour entre janvier 2023 et décembre 2025 (1 096 jours, dont 1 090 utilisables ici : la dépense des sept derniers jours n'existe pas pour les six premiers), avec le nombre de commandes et le chiffre d'affaires du jour, la température, la pluie, un indicateur de **promotion** (soldes d'hiver et d'été, semaine du « Vendredi noir ») et la **dépense publicitaire** du jour. Nous y ajouterons la dépense des **sept derniers jours**, plus parlante que celle d'un seul jour.
> - `lignes_commande.csv`, `commandes.csv`, `retours.csv` et `produits.csv` : les 83 905 lignes de commande, leur canal, leur catégorie et le fait d'avoir été retournées ou non (section 3.3).
>
> Les données sont déjà propres (le nettoyage est l'objet du volume II). Elles sont **simulées** par `build/donnees_a1.py`.

```python
import pandas as pd
import statsmodels.formula.api as smf
import outils_ch03 as O

jr = O.charger_jours()                  # un jour par ligne, avec la dépense des sept derniers jours en k€
print(len(jr), "jours ;", jr["date"].min().date(), "->", jr["date"].max().date())
print("commandes par jour : moyenne", round(jr["nb_commandes"].mean(), 1), "| jours de promotion :", int(jr["promo_active"].sum()))
```
<!--sortie-->
```text
1090 jours ; 2023-01-07 -> 2025-12-31
commandes par jour : moyenne 33.3 | jours de promotion : 153
```


## 3.1 Régression linéaire pour expliquer et estimer

Cette section construit la régression pas à pas : d'abord une droite sur six points que l'on calcule à la main, puis un modèle à plusieurs variables sur les 1 090 jours de la boutique, avec ses précautions d'emploi. Le fil rouge est la question de la gérante : *que fait la promotion, que fait la publicité, toutes choses égales par ailleurs ?*

### 3.1.1 Une droite qui passe « au mieux » parmi les points

Reprenons les six jours du volume I (section 1.4.1) : la dépense publicitaire $x$ (en euros) et le nombre de commandes $y$ des six premiers jours de novembre 2025 à partir du lundi 3. Le nuage est dispersé ; on veut pourtant une **règle** qui, à une dépense, associe un nombre de commandes **attendu**. La plus simple est une droite :

$$\hat y = a + b\,x .$$

Il y a une infinité de droites. La régression retient celle qui **se trompe le moins**, au sens suivant : pour chaque jour, on mesure l'écart vertical $e_i=y_i-\hat y_i$ entre le point et la droite (le **résidu**), et l'on choisit $a$ et $b$ qui minimisent la somme des **carrés** de ces écarts. C'est la méthode des **moindres carrés**. Pourquoi des carrés ? Parce qu'ils empêchent les écarts positifs et négatifs de s'annuler, et parce qu'ils punissent davantage les grosses erreurs. La solution s'écrit avec les mêmes sommes que la corrélation :

$$b=\frac{\sum (x_i-\bar x)(y_i-\bar y)}{\sum (x_i-\bar x)^2}=\frac{S_{xy}}{S_{xx}},\qquad a=\bar y-b\,\bar x .$$

La droite passe toujours par le point moyen $(\bar x,\bar y)$, et sa **pente** $b$ est la covariance divisée par la variance de $x$. Avec les sommes du volume I ($S_{xy}=2\,948{,}7$, $S_{xx}=74\,298{,}8$, $\bar x=395{,}2$ et $\bar y=46{,}3$) :

$$b=\frac{2\,948{,}7}{74\,298{,}8}\approx 0,0397\ \text{commande par euro},\qquad a=46{,}3-0,0397\times395{,}2\approx 30,7.$$

Soit une prévision de 30,7 commandes pour une dépense nulle, plus 4,0 commandes pour chaque centaine d'euros dépensés. Le tableau suivant donne, pour chaque jour, la valeur prévue et le résidu.

```text
 x (pub, €)  y (commandes)  prévu  résidu e  e au carré
        242             32   40.3      -8.3        68.1
        358             45   44.9       0.1         0.0
        374             32   45.5     -13.5       182.1
        583             41   53.8     -12.8       163.5
        325             58   43.5      14.5       208.8
        489             70   50.1      19.9       397.7
somme des carrés des résidus : 1020.3 | somme des résidus : -0.0
NUM pente6 0.039687
NUM ord6 30.651
NUM pente6x100 3.969
NUM r2_6 0.1029
NUM ssr6 1020.3
NUM sst6 1137.3
```

Deux remarques. D'abord, **les résidus s'annulent** (leur somme vaut zéro) : c'est une propriété de la droite des moindres carrés, pas un hasard. Ensuite, la somme des carrés des résidus vaut 1020,3, à comparer à la variabilité totale des commandes autour de leur moyenne, $\sum (y_i-\bar y)^2=1137{,}3$. Le rapport mesure ce que la droite a **expliqué** :

$$R^2=1-\frac{\sum e_i^2}{\sum (y_i-\bar y)^2}=1-\frac{1020,3}{1137,3}\approx 0,103 .$$

Le $R^2$ est la part de la variabilité de $y$ que le modèle reproduit. Ici, 10% : la dépense publicitaire explique **un dixième** des écarts entre ces six jours, et c'est exactement le carré de la corrélation trouvée au volume I (0,32). Une pente positive, un $R^2$ modeste, six points : on ne peut rien conclure, et la section suivante apprend à le dire avec des chiffres.

![Six jours de novembre : dépense publicitaire et commandes, droite des moindres carrés et résidus (segments verticaux).](figures/ch03-moindres-carres.png)


Le même calcul, fait sur les 1 090 jours de la boutique, se réduit à un appel de bibliothèque. Nous régressons le nombre de commandes sur la dépense publicitaire **du jour**.

```python
naif = smf.ols("nb_commandes ~ depense_pub", data=jr).fit()      # y ~ x : une droite
print(naif.summary2().tables[1].round(3))
print("R2 =", round(naif.rsquared, 3), "| R2 ajusté =", round(naif.rsquared_adj, 3), "| n =", int(naif.nobs))
```
<!--sortie-->
```text
              Coef.  Std.Err.       t  P>|t|  [0.025  0.975]
Intercept    20.658     0.700  29.530    0.0  19.285  22.031
depense_pub   0.061     0.003  20.528    0.0   0.055   0.066
R2 = 0.279 | R2 ajusté = 0.279 | n = 1090
```


### 3.1.2 Lire un tableau de résultats

Le tableau précédent contient, pour chaque coefficient, six nombres. Les connaître tous, et savoir à quoi ils servent, est la première compétence d'un analyste qui utilise une régression.

- **`Coef.`** : l'estimation. La pente vaut 0,0605 : en moyenne, **un euro de publicité de plus le même jour s'accompagne de 0,060 commande de plus**, soit environ 6,0 commandes pour 100 €. L'ordonnée (20,7) est le nombre de commandes attendu pour une dépense nulle.
- **`Std.Err.`** : l'**erreur type**, c'est-à-dire l'incertitude de l'estimation due à l'échantillon (volume I, section 1.3). Plus il y a de jours, plus elle est petite ; plus les points sont dispersés, plus elle est grande. Ici, 0,0029.
- **`t`** : le coefficient divisé par son erreur type (20,5). Ordre de grandeur utile : un $|t|$ supérieur à 2 signale un coefficient que le hasard d'échantillonnage explique mal.
- **`P>|t|`** : la **p-valeur** : la probabilité d'obtenir un coefficient au moins aussi éloigné de zéro **si** l'effet réel était nul. Elle est ici indiquée comme nulle (en réalité inférieure à 0,0005). Attention : elle ne dit ni si l'effet est grand, ni s'il est causal.
- **`[0.025 ; 0.975]`** : l'**intervalle de confiance à 95 %** : de 0,0547 à 0,0663. C'est le nombre le plus utile à montrer à la gérante, parce qu'il dit **de combien l'estimation peut se tromper**.

Sous le tableau, deux mesures de qualité globale. Le **$R^2$** (0,279) est la part de la variabilité des commandes reproduite par la droite. Le **$R^2$ ajusté** (0,279) corrige le $R^2$ du fait qu'ajouter une variable, même absurde, le fait toujours monter : on retire une pénalité qui dépend du nombre de variables $p$,

$$R^2_{\text{ajusté}}=1-(1-R^2)\,\frac{n-1}{n-p-1}.$$

Avec 1 090 jours et une seule variable, la correction est minuscule ; elle devient importante quand on ajoute des dizaines de variables (nous allons le faire).

> 💡 **Intuition.** Une régression est un **résumé** : elle remplace un nuage de points par une règle et un ordre de grandeur de ses erreurs. L'erreur type et l'intervalle de confiance répondent à « si j'avais observé d'autres jours, de combien le coefficient aurait-il changé ? ». Le $R^2$, lui, répond à une question différente : « de combien le modèle réduit-il l'incertitude sur les commandes d'un jour donné ? ». Un coefficient peut être très **précis** (petit intervalle) et un $R^2$ pourtant **faible**.

La droite ci-dessus affirme que la publicité fait gagner 6,0 commandes par centaine d'euros. Hélas, c'est le **même** piège que celui de la section 1.4.3 du volume I, et nous allons le défaire en ajoutant des variables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1 et exercices 3.1 à 3.3.

### 3.1.3 Passer à plusieurs variables : « toutes choses égales par ailleurs »

Quand on ajoute des variables explicatives, la droite devient un modèle à plusieurs entrées :

$$y = \beta_0+\beta_1x_1+\beta_2x_2+\dots+\beta_px_p+\varepsilon .$$

Chaque coefficient $\beta_k$ se lit alors **« toutes choses égales par ailleurs »** : c'est la variation moyenne de $y$ quand $x_k$ augmente d'une unité **et que toutes les autres variables du modèle restent fixes**. C'est l'idée qui répond à la gérante : comparer des jours de promotion et des jours sans promotion **qui se ressemblent par ailleurs** (même jour de la semaine, même mois, même tendance), au lieu de comparer des soldes de janvier à des journées de décembre.

Nous utiliserons une variable plus parlante que la dépense du jour : la **dépense des sept derniers jours** `pub_hebdo`, en milliers d'euros (une publicité agit plus qu'un jour). Nous prenons aussi le **logarithme** des commandes comme grandeur à expliquer, ce qui permettra de lire les coefficients en pourcentage (section 3.1.5). Le modèle complet est le suivant ; la syntaxe « formule » de `statsmodels` s'écrit presque comme l'équation.

```python
f = "np.log(nb_commandes) ~ promo_active + pub_hebdo + pluie_jour + C(jour_semaine) + C(mois) + t"
mod = smf.ols(f, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})   # erreurs robustes (section 3.1.7)
cle = ["promo_active", "pub_hebdo", "pluie_jour", "t"]
print(mod.summary2().tables[1].loc[cle, ["Coef.", "Std.Err.", "[0.025", "0.975]"]].round(3))
print("R2 =", round(mod.rsquared, 3), "| R2 ajusté =", round(mod.rsquared_adj, 3))
```
<!--sortie-->
```text
              Coef.  Std.Err.  [0.025  0.975]
promo_active  0.175     0.025   0.127   0.224
pub_hebdo     0.001     0.027  -0.052   0.055
pluie_jour   -0.017     0.011  -0.039   0.005
t             0.063     0.006   0.051   0.075
R2 = 0.777 | R2 ajusté = 0.772
```


Les quatre lignes affichées sont les **effets d'intérêt**. Le tableau complet compte 22 coefficients, car il contient aussi les jours de la semaine et les mois (section 3.1.4). Lisons-les en pourcentage (nous verrons au 3.1.5 pourquoi $e^{\beta}-1$) :

- **La promotion** : +19,2 % de commandes les jours de promotion, avec un intervalle de confiance de +13,5 % à +25,1 %. L'effet est net : l'intervalle est loin de zéro.
- **La publicité** : +0,14 % de commandes pour 1 000 € dépensés de plus sur la semaine, avec un intervalle de -5,1 % à +5,7 %. L'intervalle **contient zéro** : le modèle **ne détecte pas** d'effet de la publicité. Ce n'est pas la même chose que de dire qu'il n'y en a pas, nous y reviendrons.
- **La pluie** : -1,7 % de commandes les jours de pluie, intervalle de -3,8 % à +0,5 % : plutôt négatif, mais proche de ce que le hasard peut produire.
- **Le temps** (en années) : +6,5 % de commandes par an, toutes choses égales par ailleurs : la tendance de fond de la boutique.

Le modèle explique 78% de la variabilité du logarithme des commandes (le $R^2$ ajusté est de 0,772). Mais voyons surtout ce qui s'est passé pour la publicité : la droite de la section précédente promettait une forte hausse, et le modèle complet ne trouve plus rien. Pour le comprendre, construisons le modèle **marche par marche**.


```text
                                 modèle   promo     pub   pub (IC 95 %)   R2
       A. promotion et publicité seules  +2.4 % +31.4 % [+25.7 ; +37.4] 0.25
                B. + jour de la semaine  +2.0 % +31.5 % [+25.9 ; +37.4] 0.57
                              C. + mois +18.8 %  -0.2 %   [-6.5 ; +6.6] 0.76
D. + pluie et tendance (modèle complet) +19.2 %  +0.1 %   [-5.1 ; +5.7] 0.78
```

C'est le résultat central de la section. Dans le modèle A, qui ne contrôle rien, **la publicité semble multiplier les commandes de +31 % par millier d'euros** hebdomadaire et **la promotion semble inutile** (+2,4 %). Chaque ajout de variable corrige un peu : le jour de la semaine (B) ne change presque rien, mais le **mois** (C) fait tout basculer. Pourquoi ? Parce que la dépense publicitaire est **plus forte en novembre-décembre et au printemps**, quand les ventes sont déjà hautes pour d'autres raisons, et que les promotions tombent dans les creux de janvier et de l'été : les comparer sans tenir compte du mois, c'est comparer des saisons, pas des effets.

> ⚠️ **Piège.** Un coefficient n'est jamais « l'effet de la variable » : c'est l'effet **conditionnel aux autres variables du modèle**. Changez la liste des variables, et le coefficient change, parfois de signe. Le choix des variables à contrôler est une décision d'analyste (il faut contrôler ce qui influence à la fois la cause supposée et le résultat, comme la saison), pas un détail technique.

![Effet estimé de la publicité (par millier d'euros hebdomadaire) et de la promotion, selon les variables de contrôle ajoutées.](figures/ch03-marche-par-marche.png)


### 3.1.4 Les variables qualitatives : jours, mois, canaux

Le jour de la semaine et le mois sont des **catégories**, pas des quantités : le jour « 6 » n'est pas « deux fois » le jour « 3 ». La formule `C(jour_semaine)` demande à `statsmodels` de créer, pour chaque catégorie sauf une, une variable **indicatrice** valant 1 si le jour est de cette catégorie et 0 sinon. La catégorie omise est la **référence** (ici le lundi, jour 1, et janvier) : chaque coefficient se lit **par rapport à elle**.

| jour | coefficient (log) | effet par rapport au lundi |
|---|---:|---:|
| mardi (2) | -0,057 | -5,6 % |
| samedi (6) | +0,375 | +45,5 % |
| dimanche (7) | -0,366 | -30,7 % |


Un samedi apporte +45,5 % de commandes par rapport à un lundi, un dimanche -30,7 %, toutes choses égales par ailleurs ; décembre +112,5 % par rapport à janvier. Le choix de la référence ne change **pas** le modèle (les prévisions sont identiques), il change seulement la façon de lire les coefficients : prenez comme référence la catégorie la plus naturelle ou la plus fréquente.

Il y a deux pièges. Le premier est la **trappe aux variables indicatrices** : on ne peut pas inclure les sept jours **et** une constante, car leur somme égale toujours la constante (les colonnes seraient parfaitement redondantes) ; d'où le jour omis. Le second est de croire qu'un mois ou un jour « significatif » est une découverte : février et juillet n'ont pas de coefficient significatif par rapport à janvier, et c'est l'ensemble des mois qui compte (un test global, que `statsmodels` donne par `anova_lm`, répond à « le mois joue-t-il un rôle ? »).

Le canal (Boutique, Site, Réseaux) se traite de la même manière, et la section 3.3 en donnera un exemple sur les retours.

### 3.1.5 Les logarithmes : des effets en pourcentage et des élasticités

Pourquoi expliquer le **logarithme** des commandes plutôt que les commandes ? Parce qu'en entreprise, les effets sont presque toujours **proportionnels** : une promotion ne fait pas « 6 commandes de plus » tous les jours, elle fait « 19 % de plus », c'est-à-dire 6 un jour calme et 15 un jour chargé. Dans un modèle sur le logarithme, un coefficient $\beta$ se lit comme une variation relative :

$$\ln y=\beta_0+\beta_1x_1+\dots \;\Longrightarrow\; \text{quand }x_1\text{ augmente d'une unité, }y\text{ est multiplié par }e^{\beta_1}.$$

L'effet en pourcentage est donc $e^{\beta_1}-1$. Pour un petit coefficient, c'est presque $\beta_1$ lui-même (0,175 pour la promotion donne $e^{0{,}175}-1=19{,}2$ %, ce qui n'est pas tout à fait 0,175) ; pour un coefficient plus grand, l'écart se voit (décembre : coefficient 0,754, effet +112,5 %).

> 📐 **Pourquoi $e^{\beta}-1$.** Si $\ln y$ augmente de $\beta$, alors $y$ est multiplié par $e^{\beta}$ : le pourcentage de variation est $e^{\beta}-1$. Pour $\beta=0{,}1$ : $e^{0{,}1}=1{,}105$, soit $+10{,}5\ \%$ et non $+10\ \%$.

Si l'on prend aussi le logarithme de la variable explicative, le coefficient devient une **élasticité** : une variation de 1 % de $x$ s'accompagne d'une variation de $\beta$ % de $y$. Appliquons-le à la publicité (en remplaçant `pub_hebdo` par son logarithme) :

```python
mod_log = smf.ols(f.replace("pub_hebdo", "np.log(pub_hebdo)"), data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
el, (lo, hi) = mod_log.params["np.log(pub_hebdo)"], mod_log.conf_int().loc["np.log(pub_hebdo)"]
print("élasticité de la publicité :", round(el, 3), "| intervalle de confiance à 95 % :", round(lo, 3), "à", round(hi, 3))
```
<!--sortie-->
```text
élasticité de la publicité : -0.01 | intervalle de confiance à 95 % : -0.088 à 0.067
```


L'élasticité estimée est de -0,010 (intervalle de -0,088 à +0,067) : une dépense publicitaire 10 % plus élevée ne s'accompagne d'aucun effet détectable sur les commandes. L'intervalle va d'une légère baisse à une légère hausse : le message est le même que précédemment, **les données ne permettent pas de trancher**.

### 3.1.6 Les interactions : l'effet dépend-il du contexte ?

Jusqu'ici, l'effet de la promotion est supposé **identique** tous les jours de la semaine. Est-ce plausible ? Peut-être qu'une promotion « marche » mieux le week-end. On teste cette hypothèse par une **interaction** : on ajoute au modèle le produit de la promotion par le jour de la semaine, et l'on regarde si cet ajout **améliore** significativement le modèle.

```python
from statsmodels.stats.anova import anova_lm
mod_int = smf.ols(f.replace("promo_active", "promo_active * C(jour_semaine)"), data=jr).fit()
test_int = anova_lm(mco, mod_int)                  # F-test : l'interaction apporte-t-elle quelque chose ?
print("p-valeur du test d'interaction promotion x jour :", round(test_int["Pr(>F)"].iloc[1], 3))
```
<!--sortie-->
```text
p-valeur du test d'interaction promotion x jour : 0.152
```


La p-valeur est de 0,15 : rien n'autorise à dire que la promotion agit différemment selon le jour. On garde donc le modèle simple, et c'est une règle de prudence : **ne pas ajouter d'interaction parce qu'on les trouve intéressantes**, mais parce qu'une raison métier ou un test l'exige. Chaque interaction ajoutée dépense de la précision et multiplie les résultats « significatifs par hasard » (si vous testez vingt interactions, une sera significative au seuil de 5 % même si aucune n'existe).

### 3.1.7 Vérifier le modèle : résidus, robustesse, colinéarité, points influents

Un modèle de régression repose sur des hypothèses. On ne les « démontre » pas, on les **inspecte** avec quatre contrôles, par ordre de gravité.

**1. Regarder les résidus.** Si le modèle est adapté, les résidus (écarts entre le réel et le prévu) n'ont **pas de structure** : pas de courbe, pas d'éventail. Le graphique des résidus contre les valeurs prévues est le contrôle le plus utile.

![À gauche, résidus du modèle complet contre valeurs prévues ; à droite, diagramme quantile-quantile des résidus.](figures/ch03-diagnostics.png)


Les résidus sont centrés sur zéro, sans courbure, mais leur dispersion est **plus grande pour les jours à peu de commandes** (partie gauche du nuage) : c'est normal pour des comptages, dont la variabilité relative diminue avec le niveau. Le diagramme quantile-quantile (à droite) compare les résidus à une loi normale : les points suivent la diagonale, avec de légers écarts aux extrémités. Un test formel (Breusch-Pagan) confirme l'inégalité de variance (p-valeur de 0,0001, c'est-à-dire pratiquement nulle).

**2. Corriger les erreurs types.** Une variance qui change n'invalide pas les coefficients, mais fausse leurs **erreurs types** et donc les intervalles. De même, sur une série de jours consécutifs, les résidus d'un jour peuvent ressembler à ceux de la veille (**autocorrélation**). La statistique de Durbin-Watson vaut 1,99 (proche de 2 : pas d'autocorrélation notable), mais on prend la précaution d'utiliser des erreurs types **robustes** (de type « HAC », qui tiennent compte des deux phénomènes) : c'est ce que fait l'option `cov_type="HAC"` utilisée plus haut. L'effet est modeste ici : l'erreur type de la promotion passe de 0,0215 à 0,0248, celle de la publicité de 0,0234 à 0,0274. Retenez le principe : **les coefficients ne bougent pas, les intervalles s'élargissent**.

**3. Chercher la colinéarité.** Quand deux variables explicatives varient presque ensemble, le modèle ne sait pas leur attribuer séparément l'effet : les coefficients deviennent **instables** et leurs intervalles très larges. Le **facteur d'inflation de la variance** (VIF) mesure cette redondance : il vaut 1 pour une variable indépendante des autres, et l'on s'inquiète au-delà de 5 à 10. Ici, la dépense publicitaire a un VIF de 8,7 (elle est très liée aux mois), la promotion de 1,9 et le temps de 1,1. La publicité est donc la variable que le modèle a **le plus de mal à isoler**, ce qui explique en partie la largeur de son intervalle.

**4. Repérer les jours influents.** Un jour peut tirer la droite à lui à lui seul. La **distance de Cook** mesure combien les coefficients changeraient si l'on retirait ce jour. Un seuil usuel est $4/n$, soit 0,0037 ici ; 59 jours le dépassent. Le plus influent est le 2024-01-01 (distance 0,034), un jour de très peu de commandes (14) en tout début de janvier ; le deuxième est le 2024-01-02. Rien d'alarmant : on regarde ces jours, on comprend pourquoi, et l'on vérifie que les conclusions ne tiennent pas à eux seuls.

> ✅ **À retenir.** Quatre contrôles : (1) les **résidus** sans structure, (2) des **erreurs types robustes** quand on travaille sur des jours consécutifs, (3) la **colinéarité** (VIF), (4) les **jours influents**. Aucun ne « valide » un modèle ; ils permettent d'écarter les défauts grossiers, et de dire honnêtement quelle confiance accorder aux intervalles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 à 3.4 et exercices 3.4 à 3.8.

### 3.1.8 Expliquer ou prédire ?

Un même modèle peut servir à deux choses, qui ne demandent pas les mêmes précautions.

- **Expliquer** : estimer l'effet d'une variable (promotion, publicité). Ce qui compte : le **bon choix des variables de contrôle** et la **précision** des coefficients (intervalles). Le $R^2$ importe peu : un modèle qui explique peu de variance peut quand même estimer un effet de façon fiable.
- **Prédire** : annoncer les commandes de demain. Ce qui compte : l'**erreur sur des jours que le modèle n'a pas vus**. Le $R^2$ calculé sur les données d'ajustement est trompeur, puisque le modèle a été réglé pour coller à elles.

On juge donc une prévision sur des données **mises de côté** : nous ajustons le modèle sur 2023 et 2024, puis nous prévoyons chaque jour de 2025. Comme référence, deux prévisions naïves : « le même jour de la semaine, 364 jours plus tôt » et le modèle A de la section 3.1.3 (promotion et publicité seulement).

```python
app, test = jr[jr["annee"] <= 2024], jr[jr["annee"] == 2025]          # on ajuste sur le passé, on juge sur l'avenir
m_app = smf.ols(f, data=app).fit()
prevu = np.exp(m_app.predict(test))                                    # retour des logarithmes aux commandes
mae = (test["nb_commandes"] - prevu).abs().mean()
print("erreur absolue moyenne en 2025 :", round(mae, 2), "commandes par jour (moyenne observée :", round(test["nb_commandes"].mean(), 1), ")")
```
<!--sortie-->
```text
erreur absolue moyenne en 2025 : 4.44 commandes par jour (moyenne observée : 35.5 )
```


![Commandes moyennes par jour et par semaine en 2025 : observées et prévues par un modèle ajusté sur 2023 et 2024.](figures/ch03-previsions-2025.png)

L'erreur absolue moyenne est de 4,44 commandes par jour (soit 12,9 % en moyenne), pour une moyenne de 35,5 commandes par jour. Trois comparaisons donnent la mesure : la prévision « même jour, 364 jours plus tôt » se trompe de 6,66 commandes par jour ; le modèle A, sans saison, de 8,98. Le modèle complet réduit donc l'erreur de la référence naïve d'environ 33 %. Et le $R^2$ sur les données d'ajustement (0,76) ne dit pas cela : il faut mesurer **sur des jours mis de côté**.

> ⚠️ **Piège.** Un modèle peut très bien **expliquer** (coefficients fiables) et mal **prédire** (beaucoup de bruit autour de la moyenne), et l'inverse. Un bon $R^2$ n'est ni nécessaire ni suffisant pour estimer l'effet d'une promotion, et un coefficient « significatif » ne garantit pas une bonne prévision. Dites toujours **lequel des deux usages** vous visez.

### 3.1.9 Ce que disait la vérité programmée

La comparaison avec ce qui a été programmé est la meilleure façon de savoir si la méthode a fait son travail. Voici ce que le modèle complet a retrouvé.

| Effet | Estimation (intervalle à 95 %) | Vérité programmée |
|---|---|---|
| Promotion | +19,2 % (+13,5 ; +25,1) | +18 % de commandes |
| Publicité, par 1 000 € hebdomadaires | +0,1 % (-5,1 ; +5,7) | +1,5 % |
| Pluie | -1,7 % (-3,8 ; +0,5) | environ −1,7 % en moyenne (−8 % en boutique, +5 % sur le site, selon le poids de chaque canal) |
| Samedi par rapport à lundi | +45,5 % | +47 % (1,40 contre 0,95) |
| Tendance par an | +6,5 % | +6 % |

La promotion est **retrouvée** avec précision (l'effet programmé de +18 % est dans l'intervalle). Les jours de la semaine et la tendance aussi. La pluie, dont l'effet est faible et compensé entre les canaux, reste dans l'incertitude. Quant à la publicité, **l'effet programmé (+1,5 %) est dans l'intervalle, mais l'intervalle est trop large pour le mesurer** : on ne peut pas distinguer +1,5 % de zéro, ni de +5 %. C'est une leçon importante : l'absence d'effet détecté n'est pas la preuve d'une absence d'effet. Il aurait fallu beaucoup plus de jours, ou une expérience volontaire (faire varier la dépense au hasard), pour trancher.

Enfin, un mot sur le **chiffre d'affaires**. Si l'on refait le même modèle sur le chiffre d'affaires plutôt que sur le nombre de commandes, l'effet de la promotion tombe à +8,3 %, au lieu de +19,2 % sur les commandes : c'est que les promotions s'accompagnent de remises de 5 à 20 % sur les prix. La promotion **fait venir** plus de commandes, mais chacune **rapporte moins** ; la question de la gérante (« est-ce que ça rapporte ? ») ne se résume pas au nombre de commandes.


> ✅ **À retenir.**
> - La régression ajuste la droite (ou le plan) qui **minimise la somme des carrés des écarts** ; la pente est la covariance divisée par la variance de $x$.
> - Un coefficient se lit « **toutes choses égales par ailleurs** » : il dépend des autres variables du modèle. Changez les contrôles, il change.
> - Lisez toujours **l'intervalle de confiance**, pas seulement la p-valeur : un intervalle qui contient zéro et un intervalle étroit autour de zéro ne disent pas la même chose.
> - Sur le logarithme de $y$, $e^{\beta}-1$ est l'effet en pourcentage ; avec un logarithme de chaque côté, $\beta$ est une élasticité.
> - Quatre contrôles : résidus, erreurs types robustes, colinéarité (VIF), points influents.
> - **Expliquer** demande les bons contrôles ; **prédire** demande des **données mises de côté**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 et exercices 3.9 à 3.10.


## 3.2 Interpréter les coefficients pour des non-spécialistes

Un modèle qui reste dans un notebook n'a servi à personne. La gérante ne lit pas de tableau de régression : elle veut une phrase, un ordre de grandeur et une idée de la fiabilité. Cette section apprend à traduire les coefficients en phrases justes, à les montrer, à comparer les variables sans abus, et à éviter les formulations qui font dire au modèle ce qu'il ne dit pas.

### 3.2.1 Une phrase, trois ingrédients

Une bonne phrase d'interprétation contient **trois** ingrédients : l'**effet** (de combien ?), son **incertitude** (entre quoi et quoi ?) et ses **conditions** (par rapport à quoi, à quoi d'autre égal ?). Pour la promotion :

> « Toutes choses égales par ailleurs (même jour de la semaine, même mois, même niveau de publicité, même météo, même tendance), un jour de promotion s'accompagne d'environ **19 % de commandes de plus**, soit **5,7 commandes de plus** par jour de promotion, avec une incertitude comprise entre **4,2 et 7,1** commandes (intervalle de confiance à 95 %). »

Le passage du pourcentage au nombre de commandes se fait avec une base : les jours de promotion comptent en moyenne 35,4 commandes, ce qui correspond à 29,7 sans la promotion ; la différence est 5,7. Pour la publicité, la phrase est différente, parce que l'intervalle contient zéro :

> « Le modèle ne détecte pas d'effet de la publicité sur le nombre de commandes : 1 000 € de dépense hebdomadaire de plus correspondent à +0,1 % de commandes, avec une incertitude de -5,1 % à +5,7 %. Nos données ne permettent pas de dire si l'effet est nul ou de quelques pour cent. »

C'est une phrase honnête, et elle est **utile** : elle dit à la gérante qu'on ne peut pas justifier la dépense publicitaire par ces données-là, **ni** conclure qu'elle est inutile.

| Coefficient | Ce que l'on dit | Ce que l'on ne dit pas |
|---|---|---|
| Promotion : +19 % | « Un jour de promotion apporte environ 19 % de commandes de plus, toutes choses égales par ailleurs » | « La promotion cause 19 % de ventes en plus partout et toujours » |
| Publicité : +0,1 % (-5,1 ; +5,7) | « Pas d'effet détecté ; un effet de quelques pour cent n'est pas exclu » | « La publicité ne marche pas » |
| Pluie : -1,7 % (-3,8 ; +0,5) | « Les jours de pluie sont peut-être un peu plus calmes ; l'effet, s'il existe, est petit » | « La pluie n'a aucun effet » |
| Samedi : +46 % | « À date égale, un samedi apporte près de 46 % de commandes de plus qu'un lundi » | « Il faut ouvrir plus de jours le samedi » |


### 3.2.2 Points ou pour cent ? Effet relatif, effet absolu, effet sur le chiffre d'affaires

Trois confusions reviennent sans cesse.

**Relatif ou absolu.** « +19 % » est un effet **relatif** : il vaut 5,7 commandes un jour de promotion à 35 commandes, mais bien moins un jour de janvier à 20 commandes. Dire « +19 % » suppose de préciser la base ; dire « +6 commandes » suppose de préciser les jours auxquels on pense.

**Points ou pour cent.** Si le taux de retour passe de 6 % à 8 %, c'est une hausse de 2 **points** de pourcentage, mais de 33 % **en valeur relative** (volume I, section 1.5.1). Un coefficient de régression sur le logarithme est toujours relatif ; un coefficient de régression linéaire sur un taux est en points.

**Commandes ou chiffre d'affaires.** Ce que la gérante appelle « rapporter » est le chiffre d'affaires, voire la marge, pas le nombre de commandes. Refaisons l'estimation sur le chiffre d'affaires du jour : la promotion y représente +8,3 %, au lieu de +19,2 % pour les commandes. Les promotions font venir des clients, mais avec des remises ; en euros, l'effet d'un jour de promotion est d'environ **252 €** de chiffre d'affaires de plus (hors effet sur la marge, qu'il faudrait mesurer avec le coût des produits : voir le chapitre 9).


Voici la réponse chiffrée à la décision de la gérante (trois semaines de promotion en janvier plutôt que deux) : **une semaine de promotion de plus**, soit 7 jours, représente environ 1 763 € de chiffre d'affaires de plus, **sous réserve** que les jours de janvier se comportent comme les jours de promotion de l'ensemble des données (hypothèse forte), et avant de regarder la marge. C'est un ordre de grandeur, pas une prévision.

### 3.2.3 Montrer les effets

Un tableau de coefficients est un mauvais support. Deux graphiques disent l'essentiel.

**Le graphique des effets** montre, pour chaque variable d'intérêt, l'estimation et son intervalle de confiance, sur une même échelle (en pourcentage), avec une ligne verticale à zéro. On y voit d'un coup d'œil ce qui est détecté (l'intervalle ne touche pas zéro) et ce qui ne l'est pas. **Le graphique des effets marginaux** montre ce que le modèle prévoit quand **une seule** variable change, les autres restant ce qu'elles sont : ici, le nombre moyen de commandes par jour en fonction de la dépense publicitaire hebdomadaire.

![À gauche, effets estimés en pourcentage de commandes, avec intervalle de confiance à 95 %. À droite, commandes moyennes par jour prévues par le modèle selon la dépense publicitaire hebdomadaire, avec sa bande d'incertitude.](figures/ch03-effets.png)


À droite, la courbe est presque **plate** : de 0,3 k€ à 3,4 k€ de dépense hebdomadaire, les commandes moyennes passent de 32,8 à 32,9 par jour, et la bande d'incertitude au bord droit (29,7 à 36,5) englobe aussi bien une hausse qu'une baisse. Montrer cette bande à la gérante vaut mieux qu'un long discours : le modèle n'a pas de réponse sur la publicité.

> 💡 **Intuition.** Les graphiques d'effets rendent visible un fait que les tableaux cachent : un effet « non significatif » n'est pas un effet nul, c'est un **intervalle large**. Un intervalle qui va de −5 % à +6 % ne dit pas « zéro » ; il dit « nous ne savons pas ».

### 3.2.4 Comparer les variables : standardisation et importance

« Quelle variable compte le plus ? » est une question naturelle. Le piège est que les coefficients ne se comparent **pas** directement, parce que les unités diffèrent : un coefficient de promotion (0 ou 1) et un coefficient de publicité (par millier d'euros) ne mesurent pas le même « pas ».

Une première approche est de **standardiser** : mesurer l'effet d'un écart-type de la variable. La dépense publicitaire hebdomadaire a un écart-type de 0,68 k€ (entre 0,7 et 3,7 k€) ; un écart-type de publicité correspond à +0,1 % de commandes. Ce n'est pas plus parlant que le coefficient par millier d'euros, mais cela permet de comparer à l'écart-type d'une autre variable continue.

Une deuxième approche mesure la **contribution de chaque variable à la variance expliquée** : de combien le $R^2$ baisse-t-il quand on retire la variable ou le groupe de variables (jour de la semaine, mois…) du modèle ?

![Baisse du R2 du modèle quand on retire chaque groupe de variables.](figures/ch03-importance.png)


Le **jour de la semaine** explique à lui seul 32 points de $R^2$, le mois 15, la tendance 2, la promotion 1, la publicité et la pluie presque rien. Faut-il conclure que la promotion est « peu importante » ? Non, et c'est la leçon de cette section : **l'importance pour expliquer la variance n'est pas un levier d'action**. Le jour de la semaine explique beaucoup de variations, mais on ne peut pas l'activer ; la promotion en explique peu parce qu'elle ne concerne que 153 jours sur 1090, mais c'est **la** variable que la gérante peut décider. Pour une décision, on regarde l'**effet de la variable que l'on peut piloter**, avec son intervalle, pas son rang dans un classement d'importance.

> ⚠️ **Piège.** Les classements d'importance dépendent de la **variabilité** de chaque variable dans les données (une variable qui ne varie presque pas explique peu), de l'**ordre** dans lequel on les ajoute quand elles sont liées entre elles, et ne disent rien de la **causalité**. Servez-vous-en pour comprendre la structure du modèle, pas pour hiérarchiser des actions.

### 3.2.5 Les formulations à éviter

Voici les phrases que l'on entend le plus souvent, et leur version corrigée.

| Formulation fautive | Pourquoi elle est fautive | Version correcte |
|---|---|---|
| « La promotion **cause** 19 % de commandes. » | Une régression sur données d'observation mesure une association, ajustée sur les variables incluses : des facteurs oubliés peuvent subsister. | « À jours comparables, les jours de promotion ont 19 % de commandes de plus. » |
| « Le coefficient de la pluie est faible, **donc la pluie ne compte pas**. » | Un intervalle qui contient zéro dit « incertain », pas « nul ». Et l'effet est compensé entre canaux. | « Pas d'effet net détecté de la pluie ; il peut être petit. » |
| « p < 0,05 : **l'effet est important**. » | La p-valeur dit si l'effet est distinguable du hasard, pas s'il est grand. | « L'effet est de X %, avec un intervalle de … à …. » |
| « $R^2$ de 78% : **le modèle est excellent pour prédire**. » | Le $R^2$ est calculé sur les données d'ajustement ; il est dopé par le jour de la semaine et le mois, qui sont connus à l'avance. | « Sur 2025, que le modèle n'a pas vue, l'erreur moyenne est de 4,4 commandes par jour. » |
| « Chaque euro de publicité rapporte 0,06 commande. » | C'est le coefficient du modèle sans contrôle (section 3.1.2), où la saison se cache dans la publicité. | « Après contrôle de la saison, nous ne détectons pas d'effet de la publicité. » |
| « Toutes choses égales par ailleurs, une promotion un dimanche… » | Si la combinaison n'existe pas dans les données (ou presque), le modèle extrapole. | Vérifier qu'il y a des jours comparables avant de projeter. |

### 3.2.6 Présenter le modèle à la gérante en cinq lignes

Voici ce que vous pouvez lui écrire, sans aucun terme technique, avec les chiffres calculés plus haut. Chacune des cinq lignes répond à une question qu'elle se pose.

> **Objet : ce que disent les 3 ans de ventes sur la promotion et la publicité.**
> 1. **Promotion** : à jours comparables (même jour de la semaine, même mois, même tendance), un jour de promotion apporte environ 19 % de commandes de plus, soit 6 par jour, avec une fourchette de 4 à 7.
> 2. **Chiffre d'affaires** : à cause des remises, l'effet sur le chiffre d'affaires est plus faible (+8 %), soit environ 252 € par jour de promotion ; la marge reste à vérifier.
> 3. **Publicité** : nos données ne permettent pas de détecter un effet ; une expérience volontaire (changer la dépense au hasard sur quelques semaines) serait nécessaire pour trancher.
> 4. **Calendrier** : le jour de la semaine et le mois pèsent bien plus que tout le reste ; le samedi apporte près de 46 % de commandes de plus qu'un lundi.
> 5. **Fiabilité** : en prévision, le modèle se trompe de 4,4 commandes par jour en moyenne sur 2025, soit 13 % ; c'est utile pour planifier, pas pour piloter au jour le jour.

> ✅ **À retenir.**
> - Une phrase d'interprétation contient l'**effet**, son **incertitude** et ses **conditions**.
> - Un intervalle qui contient zéro dit « **on ne sait pas** », pas « zéro ».
> - Distinguez **relatif et absolu**, **points et pour cent**, **commandes et chiffre d'affaires**.
> - Montrez des **graphiques d'effets** avec leurs intervalles plutôt que des tableaux.
> - L'**importance pour la variance** n'est pas un **levier d'action**.
> - Évitez « cause », « ne compte pas », « significatif donc important » : une régression sur données d'observation n'établit pas une causalité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.6 et exercices 3.11 à 3.12.


## 3.3 ➕ Pour aller plus loin : régression logistique pour les résultats métier

> 🧭 **Section complémentaire.** Elle traite le cas où l'on explique non plus un nombre, mais un **oui ou non** : une ligne de commande est-elle retournée ? Un client rachète-t-il ? Un e-mail est-il ouvert ? Elle n'est pas nécessaire à la suite du volume.

La gérante a une autre inquiétude : « Les retours nous coûtent cher en transport et en manutention. **Quelles lignes reviennent le plus ?** Est-ce qu'on peut le voir venir ? » La grandeur à expliquer est ici binaire (retournée ou non) : une régression linéaire ordinaire prédirait des « probabilités » négatives ou supérieures à 1. On utilise la **régression logistique**.

### 3.3.1 Probabilités, cotes et rapports de cotes

Commençons par le calcul le plus simple, un tableau à deux lignes et deux colonnes : les lignes vendues sur le **Site** et en **Boutique**, retournées ou non.

```text
          gardées  retournées  total taux de retour
canal                                              
Site        32286        3186  35472           9.0%
Boutique    38151        1211  39362           3.1%
```


Trois façons de comparer les deux canaux :

- **Différence de probabilités** : 9,0 % contre 3,1 %, soit 5,9 points d'écart.
- **Rapport de probabilités** (risque relatif) : 2,92 : une ligne du Site a environ 2,9 fois plus de chances d'être retournée.
- **Rapport de cotes** (*odds ratio*) : la **cote** (*odds*) d'un événement de probabilité $p$ est $p/(1-p)$, le nombre de « oui » pour un « non ». Ici, 0,0987 retour par ligne gardée pour le Site (environ 1 pour 10) et 0,0317 en Boutique (1 pour 32). Le rapport de cotes vaut 3,11.


Pourquoi s'embarrasser de cotes, qui sont moins intuitives que les probabilités ? Parce qu'elles ont une propriété que les probabilités n'ont pas : une probabilité est bornée entre 0 et 1, une cote va de 0 à l'infini, et le **logarithme de la cote** (le *logit*) va de moins l'infini à plus l'infini, comme n'importe quelle grandeur que l'on peut modéliser par une droite. Le modèle logistique écrit :

$$\ln\frac{p}{1-p}=\beta_0+\beta_1x_1+\dots+\beta_px_p .$$

Chaque coefficient est donc un effet sur le **logarithme de la cote**, et $e^{\beta}$ est un **rapport de cotes** : le facteur par lequel la cote est multipliée quand $x$ augmente d'une unité, les autres variables restant fixes. Quand l'événement est rare (moins de 10 %), la cote et la probabilité sont presque égales, et le rapport de cotes ressemble au rapport de probabilités (3,11 contre 2,92 ici) ; quand l'événement est fréquent, ils s'écartent, et lire un rapport de cotes comme « trois fois plus de chances » devient faux.

> ⚠️ **Piège.** « Le rapport de cotes est de 3 » ne veut pas dire « trois fois plus de chances » sauf si l'événement est rare. Pour dire à la gérante quelque chose de juste, préférez la **différence de probabilités** (en points), ou donnez les deux probabilités.

### 3.3.2 Le modèle logistique

Nous expliquons le retour d'une ligne par plusieurs variables à la fois : le canal, la catégorie du produit, le prix (en logarithme), l'existence d'une remise et la quantité. La formule s'écrit comme pour la régression linéaire, avec `logit` à la place de `ols`.

```python
fl = "retour ~ C(canal, Treatment('Boutique')) + C(categorie) + np.log(prix_unitaire) + promo + quantite"
mlog = smf.logit(fl, data=lg).fit(disp=0)
rc = np.exp(pd.concat([mlog.params, mlog.conf_int()], axis=1)); rc.columns = ["rapport de cotes", "bas", "haut"]
print(rc.drop("Intercept").round(2))
```
<!--sortie-->
```text
                                            rapport de cotes   bas  haut
C(canal, Treatment('Boutique'))[T.Réseaux]              2.25  2.04  2.49
C(canal, Treatment('Boutique'))[T.Site]                 3.11  2.91  3.33
C(categorie)[T.Cuisine]                                 1.01  0.90  1.12
C(categorie)[T.Décoration]                              0.99  0.89  1.10
C(categorie)[T.Jardin]                                  1.01  0.91  1.13
C(categorie)[T.Maison]                                  0.95  0.85  1.06
C(categorie)[T.Papeterie]                               0.89  0.79  1.00
np.log(prix_unitaire)                                   1.01  0.96  1.05
promo                                                   0.99  0.92  1.07
quantite                                                1.02  0.97  1.08
```


### 3.3.3 Lire les rapports de cotes

Lisons le tableau, ligne par ligne.

- **Site** : rapport de cotes de 3,11 (intervalle à 95 % de 2,91 à 3,33). À catégorie, prix, remise et quantité égaux, la cote de retour d'une ligne du Site est environ **3,1 fois** celle d'une ligne de la Boutique. L'intervalle est loin de 1 : l'effet est net.
- **Réseaux** : 2,25 (2,04 à 2,49) : un effet net aussi, moins fort que le Site.
- **Remise** : 0,99 (p-valeur 0,82) ; **prix** : 1,01 (0,76) ; **quantité** : 1,02 (0,49). Un rapport de cotes de 1 signifie « pas d'effet » : ces trois variables n'en montrent aucun.
- **Catégories** : tous les rapports sont proches de 1. Un seul s'écarte un peu : la papeterie (0,89, p-valeur de 0,059), proche du seuil habituel de 5 %. Faut-il y voir une catégorie qui revient moins ? Pas sans précaution : avec cinq comparaisons, **une p-valeur de 6 % est attendue par hasard** une fois sur quatre environ. Le test d'ensemble (est-ce que les cinq catégories, **ensemble**, améliorent le modèle ?) donne une p-valeur de 0,27 : non.

Les rapports de cotes se lisent sur une échelle **logarithmique** (3 fois plus et 3 fois moins sont symétriques), et la figure suivante les montre avec leurs intervalles.

![Rapports de cotes de retour d'une ligne, avec intervalle de confiance à 95 % (échelle logarithmique). La ligne verticale à 1 signifie « pas d'effet ».](figures/ch03-rapports-de-cotes.png)


Pour la gérante, un rapport de cotes se traduit en **probabilités**. Les **effets marginaux moyens** donnent directement la variation moyenne de la probabilité quand une variable change : passer de la Boutique au Site augmente la probabilité de retour d'environ 6,5 points en moyenne, toutes choses égales par ailleurs (un peu plus que l'écart brut de 5,9 points, parce que la moyenne est prise sur toutes les lignes, y compris celles des Réseaux). Et les probabilités prévues pour une ligne « moyenne » sont de 3,1 % en Boutique, 6,7 % en Réseaux et 9,0 % sur le Site.


#### Ce que disait la vérité programmée

Dans le générateur des données, la probabilité de retour d'une ligne dépend **uniquement du canal** : 9 % sur le Site, 7 % pour les Réseaux, 3 % en Boutique. Ni le prix, ni la catégorie, ni la remise, ni la quantité n'interviennent. Le modèle a retrouvé exactement cela : un effet net du canal, et aucun effet des autres variables. C'est un exemple utile : une régression logistique qui **ne trouve rien** là où il n'y a rien est un résultat à part entière, et la fausse alerte de la papeterie montre pourquoi il faut se méfier d'une seule p-valeur isolée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.7 et exercices 3.13 à 3.14.

### 3.3.4 Mesurer la qualité : l'exactitude trompe

Un modèle de classification se juge sur une question simple : sait-il **séparer** les lignes qui reviennent de celles qui restent ? Le premier réflexe, l'exactitude (la part de bonnes réponses), est trompeur quand l'événement est rare. Ici, 6,0 % des lignes sont retournées : un « modèle » qui répond toujours « gardée » a raison 94,0 % du temps, sans rien savoir.

On préfère regarder ce qui se passe quand on **déclenche une action** pour les lignes dont la probabilité prévue dépasse un seuil. La **matrice de confusion** compte les quatre cas : retours détectés (vrais positifs), alertes inutiles (faux positifs), retours manqués (faux négatifs), lignes ignorées à raison (vrais négatifs).

```python
from sklearn.metrics import confusion_matrix, roc_auc_score
seuil = 0.08                                                   # on signale les lignes dont la probabilité prévue dépasse 8 %
tn, fp, fn, tp = confusion_matrix(lg["retour"], (lg["p_prevu"] >= seuil).astype(int)).ravel()
print("détectés :", tp, "| alertes inutiles :", fp, "| manqués :", fn, "| ignorés à raison :", tn)
print("AUC :", round(roc_auc_score(lg["retour"], lg["p_prevu"]), 3))
```
<!--sortie-->
```text
détectés : 3186 | alertes inutiles : 32286 | manqués : 1816 | ignorés à raison : 46617
AUC : 0.636
```


Au seuil de 8 %, le modèle signale 35472 lignes (42 % du total) ; parmi elles, 3186 sont réellement retournées (**précision** de 9,0 %, à comparer aux 6,0 % de base) et il en manque 1816 (**rappel** de 64 %). L'exactitude, elle, est de 59,4 %, **moins** bonne que celle du modèle qui ne fait rien (94,0 %), alors que le modèle apporte une information réelle. C'est le défaut de l'exactitude pour un événement rare.

L'**AUC** est la mesure standard de séparation : c'est la probabilité qu'une ligne retournée tirée au hasard ait une probabilité prévue plus élevée qu'une ligne gardée tirée au hasard ; 0,5 signifie « aucune information », 1 « séparation parfaite ». Ici, 0,636 : le modèle sépare un peu, **uniquement parce qu'il connaît le canal**. Il ne sait pas trier les lignes **à l'intérieur** d'un même canal, puisque rien d'autre ne les distingue. Un AUC de cet ordre est typique d'un modèle qui n'a qu'un seul vrai signal.

Une dernière vérification est la **calibration** : quand le modèle annonce 9 %, observe-t-on 9 % ?

```text
          lignes  prévu (%)  observé (%)
canal                                   
Boutique   39362        3.1          3.1
Réseaux     9071        6.7          6.7
Site       35472        9.0          9.0
```

La calibration est excellente, ce qui est normal : un modèle logistique avec le canal comme variable reproduit les taux moyens de chaque canal. Mais retenez qu'une bonne calibration **ne dit rien** de la capacité à trier.

### 3.3.5 Choisir un seuil selon les coûts

Quel seuil retenir ? Il n'y a **pas** de bon seuil universel : le bon seuil est celui qui rend **rentable** l'action que l'on déclenche. Supposons (hypothèses d'illustration) qu'une ligne retournée coûte 18 € à la boutique (transport aller-retour, manutention, perte de revente), qu'une vérification avant expédition (contrôle du colis, message au client) coûte 0,50 € par ligne et qu'elle évite le retour dans 40% des cas où il aurait eu lieu.


Signaler une ligne de probabilité $p$ coûte 0,50 € et rapporte en espérance $p\times q\times s$ avec $q$ le taux de succès et $s$ le coût d'un retour. L'action est rentable si $p\,q\,s\ge c$, c'est-à-dire pour un seuil

$$p^{*}=\frac{c}{q\,s}=\frac{0,50}{0,4\times18}\approx 0,069 .$$

Avec ces hypothèses, le seuil est d'environ 6,9 % : il faut signaler les lignes dont la probabilité de retour dépasse 6,9 %. Cela revient ici à signaler **les lignes du Site** (9,0 %) mais pas celles des Réseaux (6,7 %) ni de la Boutique. Le tableau suivant donne le bilan, par canal, sur les trois années.

```text
          lignes  retours  coût de l'action (€)  retours évités (€)  gain net (€) signalé
canal                                                                                    
Boutique   39362     1211               19681.0              8719.0      -10962.0     non
Réseaux     9071      605                4536.0              4356.0        -180.0     non
Site       35472     3186               17736.0             22939.0        5203.0     oui
```

Le canal Site dégage un gain net positif, les Réseaux sont à la limite, la Boutique perdrait de l'argent. Mais le **chiffre** dépend entièrement des hypothèses : si l'action n'évite le retour que dans 25% des cas, le seuil monte à 11,1 % et plus rien n'est rentable. Ce raisonnement est la vraie conclusion : le seuil se déduit **d'un calcul de coûts**, qu'on montre à la gérante avec ses hypothèses, pas d'une valeur « par défaut » de 0,5.

> ✅ **À retenir.**
> - La régression logistique explique un **oui/non** : elle modélise le logarithme de la **cote** ; $e^{\beta}$ est un **rapport de cotes**.
> - Un rapport de cotes de 1 signifie « pas d'effet » ; pour un événement **rare**, il ressemble au risque relatif, sinon **il l'exagère**.
> - Une p-valeur isolée parmi plusieurs comparaisons peut être un hasard : regardez le **test d'ensemble**.
> - L'**exactitude trompe** pour un événement rare ; regardez la matrice de confusion, l'AUC et la calibration.
> - Le **seuil** de décision se déduit d'un **calcul de coûts**, avec ses hypothèses écrites.


## Bilan du chapitre 3

Vous savez maintenant :

- **ajuster une droite par les moindres carrés** (la pente est la covariance divisée par la variance de $x$, le $R^2$ la part de variabilité expliquée), et **lire un tableau de résultats** : coefficient, erreur type, $t$, p-valeur, intervalle de confiance, $R^2$ ajusté ;
- **passer à plusieurs variables** et lire un coefficient « toutes choses égales par ailleurs », en sachant qu'il **change avec les variables de contrôle** (la publicité passe de +31 % à +0,1 % quand on contrôle la saison) ;
- **traiter les catégories** par des indicatrices et une référence, **lire des effets en pourcentage** ($e^{\beta}-1$) et des élasticités, et **tester une interaction** plutôt que la supposer ;
- **inspecter un modèle** : résidus, erreurs types robustes (HAC), colinéarité (VIF), distance de Cook ;
- **distinguer expliquer et prédire** : un modèle jugé sur des jours mis de côté ;
- **traduire en langage clair** : phrases avec effet, incertitude et conditions ; relatif et absolu ; commandes et chiffre d'affaires ; graphiques d'effets ; mises en garde sur l'importance relative ;
- (en option) **modéliser un oui/non** : cotes, rapports de cotes, effets marginaux, matrice de confusion, AUC, calibration, et un **seuil** déduit d'un calcul de coûts.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée :

| Question | Résultat | Vérité programmée |
|---|---|---|
| Effet d'un jour de promotion sur les commandes | +19,2 % (+13,5 ; +25,1) | +18 % |
| Effet sur le chiffre d'affaires | +8,3 % | (remises de 5 à 20 %) |
| Effet de 1 000 € de publicité hebdomadaire | +0,1 % (-5,1 ; +5,7) : non détecté | +1,5 % |
| Pluie | -1,7 % | environ −1,7 % |
| Prévision 2025 (erreur moyenne par jour) | 4,4 commandes (13 %) | référence naïve : 6,7 |
| Rapport de cotes de retour, Site contre Boutique | 3,1 (2,9 ; 3,3) | ≈ 3,1 (9 % contre 3 %) |
| Autres variables (prix, catégorie, remise, quantité) | aucun effet net | aucun effet |

Le fil conducteur du chapitre tient en une phrase : **un coefficient n'est pas un fait de la nature, c'est la réponse d'un modèle à une question précise, avec une incertitude.** La promotion est mesurée avec précision parce que l'effet est grand et que les jours de promotion sont nombreux ; la publicité ne l'est pas, parce que l'effet est petit et noyé dans la saison. Dans les deux cas, la bonne conduite est la même : **contrôler ce qui trompe, montrer l'intervalle, et dire ce que les données ne permettent pas de dire.**

La régression explique des effets **moyens** sur l'ensemble des jours ou des clients. Le chapitre 4 s'intéresse aux **différences entre groupes** de clients (segmentation) et à leur **évolution dans le temps** (cohortes) ; le chapitre 5 revient sur le temps pour **prévoir** avec des méthodes spécialisées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.7 (droite à la main, lire un tableau, modèle de promotion et de publicité, diagnostic, prévision, présentation à la gérante, retours) et exercices 3.1 à 3.14.
