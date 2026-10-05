# Chapitre 7 : ➕ Inférence causale

> « Les données vous disent ce qui *accompagne* quoi. Pour savoir ce qui *provoque* quoi, il faut en plus une idée de la façon dont les données ont été fabriquées. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 6 se lisent et se comprennent sans lui. Mais si vous ne devez retenir qu'un chapitre « de métier » de ce volume, c'est peut-être celui-ci : c'est lui qui transforme un modèle statistique correct en **décision correcte**.

Tout au long des chapitres précédents, nous avons posé des questions de **prédiction** et d'**association** : « les clients venus des réseaux sociaux dépensent-ils moins ? », « quel est le lien entre l'âge et le rachat ? ». Les modèles linéaires et généralisés y répondent très bien. Mais la question que se pose réellement la gérante, le plus souvent, est d'un autre genre :

- « Si j'envoie une offre de bienvenue à un client, **va-t-il** davantage racheter ? »
- « Si je lance une campagne publicitaire dans telle ville, **les commandes vont-elles** augmenter ? »
- « Si mes clients suivent le compte de la boutique sur les réseaux sociaux, **dépensent-ils plus à cause de cela**, ou est-ce simplement que ce sont déjà mes meilleurs clients qui me suivent ? »

Ce sont des questions **causales** : elles portent sur ce qui se passerait si l'on **agissait**. Et la leçon la plus importante de ce chapitre est la suivante : **aucun modèle, même sophistiqué, ne répond à une question causale à partir des seules données. Il faut y ajouter des hypothèses sur la façon dont ces données ont été produites**. Le chapitre vous apprend à les formuler (avec des graphes), à les justifier (avec la randomisation, quand on le peut) et à les exploiter (quand on ne le peut pas).

## Le chemin de ce chapitre

- **7.1 Raisonner en causes** : les résultats potentiels (le « problème fondamental »), pourquoi la **randomisation** résout tout, une vraie expérience sur l'offre de bienvenue, puis les **graphes causaux** (DAG) et leurs trois structures de base (fourche, chaîne, collision), le paradoxe de Simpson, et le critère de la porte dérobée.
- **7.2 Scores de propension** : quand on ne peut pas randomiser mais que l'on observe les raisons du choix : appariement, pondération, estimateur doublement robuste.
- **7.3 Différences de différences** : une campagne lancée dans certaines villes seulement ; comparer l'évolution des villes traitées à celle des villes témoins.
- **7.4 Variables instrumentales** : quand la confusion n'est **pas observée**, un « coup de pouce » aléatoire peut sauver l'analyse ; avec un panorama honnête des limites de toutes ces méthodes.
- **Le cahier** : chaque section se termine par un renvoi `📒` vers des applications et des exercices corrigés, rassemblés dans le *Cahier d'exercices et d'applications* du volume.

> 🧭 **Comment travailler avec ce chapitre.** Il repose sur un procédé très particulier : **nous simulons nous-mêmes les données**. Le gros avantage est que nous connaissons la **vraie** valeur de chaque effet, et nous pouvons donc vérifier honnêtement si chaque méthode la retrouve. Dans la vraie vie, ce ne sera jamais le cas : c'est précisément pour cela que le raisonnement causal est difficile. À chaque méthode, nous commencerons donc par faire comme si nous ne connaissions pas la vérité, puis nous la **révélerons**. Gardez bien en tête que cette simulation est une loupe pédagogique, pas une garantie : une méthode qui retrouve la vérité dans une simulation propre n'est pas pour autant infaillible sur des données réelles.

> 📦 **Les données de ce chapitre.**
>
> - `donnees/clients.csv` (2 000 clients, présenté dans l'introduction du volume) : on y trouve la variable `offre_bienvenue`, **attribuée au hasard**. C'est une vraie expérience randomisée (section 7.1.4).
> - `donnees/ch07-observationnel.csv` (4 000 clients) : une version **non randomisée** de la même histoire, où la gérante a choisi à qui envoyer l'offre (section 7.1.9 et 7.2). Le fichier `ch07-observationnel-verite.csv` contient les « résultats potentiels » que personne ne peut observer en pratique ; nous ne l'ouvrirons que pour vérifier.
> - `donnees/ch07-panel-villes.csv` : 20 villes suivies pendant 24 mois autour d'une campagne publicitaire (section 7.3).
> - `donnees/ch07-iv.csv` (5 000 clients) : une étude du lien entre le suivi du compte de la boutique sur les réseaux sociaux et la dépense (section 7.4).
>
> Les fichiers `ch07-*` sont produits par `build/sim_ch07.py` (graines fixes). Les analyses complètes, avec leur code, sont dans le cahier (applications 7.1 à 7.9) ; ce chapitre en donne les résultats et le raisonnement.

> 💡 **Une convention de notation.** Dans tout le chapitre, $T$ désigne le **traitement** (ce que l'on décide : 1 = offre reçue, 0 = pas d'offre), $Y$ le **résultat observé** (ce que l'on mesure : dépense, rachat…) et $X$ les **covariables** (ce que l'on sait du client avant le traitement : âge, canal, engagement…). Dans le volume I, les sections 3.3 à 3.5 (intervalles de confiance, tests, tests multiples) sont les prérequis statistiques ; le chapitre 2 de ce volume (section 2.2, régression logistique) est utilisé pour les scores de propension.


## 7.1 Raisonner en causes : résultats potentiels, expérience randomisée, DAG et confusion

> 💡 **Intuition.** Dire « l'offre de bienvenue **augmente** la dépense » signifie : *pour le même client, au même moment*, la dépense avec offre est supérieure à la dépense sans offre. Le problème, c'est que **ce même client ne peut pas recevoir et ne pas recevoir l'offre en même temps**. L'une des deux dépenses n'existera jamais. Toute la pensée causale consiste à compenser, par une astuce (la randomisation) ou par une hypothèse (le raisonnement sur un graphe), cette moitié de réalité qui nous manque.

### 7.1.1 Une conclusion trop rapide

Voici l'histoire qui motive tout le chapitre. La gérante a envoyé, pendant un an, une offre de bienvenue (un bon d'achat) à une partie de ses nouveaux clients. En comparant les dépenses, elle constate que les clients qui ont reçu l'offre dépensent **beaucoup plus** que les autres. Conclusion immédiate : « l'offre rapporte, je l'envoie à tout le monde ».

Avant de croire ce raisonnement, regardons ce qu'il a de fragile. La gérante n'a pas envoyé l'offre au hasard : elle l'a envoyée à ceux qui lui semblaient les plus prometteurs, ceux qui ouvrent ses e-mails, qui aiment ses publications, qui sont déjà très actifs. Ce sont **ces clients-là** qui dépensent beaucoup, avec ou sans bon d'achat. La comparaison « offre contre pas d'offre » compare donc des clients **différents dès le départ**, et pas seulement à cause de l'offre. Nous allons mettre des chiffres sur cette intuition.

### 7.1.2 Les résultats potentiels

Le langage standard pour parler de causalité est celui des **résultats potentiels** (cadre de Neyman-Rubin). Pour chaque client $i$, on imagine deux nombres :

- $Y_i(1)$ : la dépense du client $i$ **s'il reçoit** l'offre ;
- $Y_i(0)$ : la dépense du client $i$ **s'il ne la reçoit pas**.

L'**effet causal individuel** de l'offre sur le client $i$ est $\tau_i = Y_i(1)-Y_i(0)$. Un seul des deux résultats est observé, celui qui correspond au traitement réellement reçu $T_i\in\{0,1\}$ :

$$Y_i = T_i\,Y_i(1) + (1-T_i)\,Y_i(0).$$

C'est le **problème fondamental de l'inférence causale** (Holland, 1986) : pour chaque client, l'une des deux colonnes est *toujours manquante*. Les effets individuels sont inobservables. On vise donc des **effets moyens** :

- **ATE** (*average treatment effect*) : $\ \mathbb E[Y(1)-Y(0)]$, l'effet moyen sur *toute* la population ;
- **ATT** (*on the treated*) : $\ \mathbb E[Y(1)-Y(0)\mid T=1]$, l'effet moyen sur ceux qui ont **effectivement** reçu l'offre ;
- **ATU** (*on the untreated*) : $\ \mathbb E[Y(1)-Y(0)\mid T=0]$, l'effet moyen sur ceux qui ne l'ont pas reçue.

> 📐 **Une hypothèse cachée : la SUTVA.** Écrire $Y_i(1)$ et $Y_i(0)$ suppose deux choses : (1) il n'y a **qu'une seule version** du traitement (un bon d'achat de 10 €, pas « un bon de 5 € ou de 20 € selon les cas ») ; (2) le résultat du client $i$ ne dépend **pas** du traitement des autres (pas de contagion : si votre voisine reçoit l'offre et vous en parle, la formulation se complique). Dans tout ce chapitre, nous supposerons que ces deux conditions sont raisonnablement satisfaites, et nous reviendrons sur la deuxième à propos des campagnes par ville (7.3).

Pour **voir** le problème, jouons à Dieu. Voici huit clients dont nous connaissons, exceptionnellement, les **deux** dépenses potentielles. (Ce tableau est inventé de toutes pièces, et calculable à la main.)

**Le tableau vu par Dieu :**

| Client | $Y(0)$ sans offre | $Y(1)$ avec offre | Offre reçue | Effet $Y(1)-Y(0)$ |
|---|---:|---:|---|---:|
| A | 100 | 120 | oui | +20 |
| B | 150 | 165 | oui | +15 |
| C | 180 | 190 | oui | +10 |
| D | 130 | 145 | oui | +15 |
| E | 50 | 60 | non | +10 |
| F | 80 | 85 | non | +5 |
| G | 60 | 75 | non | +15 |
| H | 90 | 100 | non | +10 |

**Le tableau vu par la gérante** (une moitié du tableau manque toujours) :

| Client | Offre reçue | $Y(0)$ observé | $Y(1)$ observé |
|---|---|---:|---:|
| A | oui | ? | 120 |
| B | oui | ? | 165 |
| C | oui | ? | 190 |
| D | oui | ? | 145 |
| E | non | 50 | ? |
| F | non | 80 | ? |
| G | non | 60 | ? |
| H | non | 90 | ? |


Calculons à la main ce que Dieu sait. Les effets individuels sont $+20,+15,+10,+15$ pour les quatre clients qui ont reçu l'offre (**ATT** $=60/4=15$ €), et $+10,+5,+15,+10$ pour les quatre autres (**ATU** $=40/4=10$ €). Sur les huit, l'**ATE** vaut $100/8=12{,}5$ €. Voyons maintenant ce que fait la gérante : elle compare les dépenses moyennes **observées**. Avec offre : $(120+165+190+145)/4=155$ € ; sans offre : $(50+80+60+90)/4=70$ €. Sa différence naïve vaut donc $155-70=85$ €.


La comparaison naïve donne **85 €**, alors que l'effet réel de l'offre n'est que de 15 € pour ceux qui l'ont reçue ! D'où vient l'écart ? Il se démontre en deux lignes.

> 📐 **La décomposition du biais de sélection.** Écrivons $\mu_1=\mathbb E[Y\mid T=1]$ et $\mu_0=\mathbb E[Y\mid T=0]$ les moyennes observées. Chez les traités, on observe $Y(1)$ ; chez les non-traités, $Y(0)$. Donc
>
> $$\mu_1-\mu_0=\mathbb E[Y(1)\mid T=1]-\mathbb E[Y(0)\mid T=0].$$
>
> En ajoutant et retranchant $\mathbb E[Y(0)\mid T=1]$ (ce que les traités auraient dépensé **sans** l'offre, une quantité inobservable) :
>
> $$\underbrace{\mu_1-\mu_0}_{\text{différence naïve}}=\underbrace{\mathbb E[Y(1)-Y(0)\mid T=1]}_{\text{ATT : l'effet qui nous intéresse}}+\underbrace{\mathbb E[Y(0)\mid T=1]-\mathbb E[Y(0)\mid T=0]}_{\text{biais de sélection}}.$$
>
> Le **biais de sélection** mesure à quel point les traités et les non-traités auraient été **différents même sans le traitement**.

Dans notre petit exemple, les clients choisis par la gérante auraient dépensé en moyenne $(100+150+180+130)/4=140$ € *sans* offre, contre $(50+80+60+90)/4=70$ € pour les autres : biais de sélection $=70$ €. Et $15+70=85$ : la décomposition retombe sur la différence naïve.


> ⚠️ **Retenir cette équation.** Elle explique tous les résultats trompeurs de ce chapitre : une différence entre groupes est la somme d'un effet **causal** et d'un **biais de sélection**. Tout l'art est de faire disparaître le second terme, ou de l'estimer.

### 7.1.3 Pourquoi la randomisation résout tout

Qu'est-ce qui ferait disparaître le biais de sélection ? Il faudrait que, **sans** le traitement, les deux groupes se ressemblent en moyenne : $\mathbb E[Y(0)\mid T=1]=\mathbb E[Y(0)\mid T=0]$. Or il existe une façon de **garantir** cela : tirer au sort qui reçoit l'offre. Si l'attribution est aléatoire, elle est **indépendante** de tout ce qui caractérise les clients, y compris de leurs résultats potentiels : $T\perp (Y(0),Y(1))$. On a alors $\mathbb E[Y(0)\mid T=1]=\mathbb E[Y(0)\mid T=0]=\mathbb E[Y(0)]$, et le biais de sélection est **nul** :

$$\mu_1-\mu_0=\mathbb E[Y(1)]-\mathbb E[Y(0)]=\text{ATE}.$$

La différence des moyennes, bête et simple, est alors un estimateur **sans biais** de l'effet moyen. Aucun modèle, aucune hypothèse sur la forme de la relation n'est nécessaire : c'est la force de la randomisation.

Sur nos huit clients, on peut **vérifier** cette affirmation exhaustivement. Il y a $\binom{8}{4}=70$ façons de choisir les quatre clients qui reçoivent l'offre ; si la gérante tire au sort l'une d'elles avec la même probabilité, la moyenne des 70 différences naïves possibles doit retomber sur l'ATE.


La moyenne vaut exactement l'ATE : **en moyenne sur les tirages possibles**, l'estimateur est juste. Mais une expérience particulière n'est qu'un tirage parmi les 70, et celui-ci peut tomber très loin de la vérité (les 70 tirages donnent des estimations de −60 à +85 € : avec seulement huit clients, on peut même obtenir le mauvais signe) : c'est pourquoi on accompagne toujours l'estimation d'un intervalle de confiance, comme au volume I (section 3.3).

Passons à l'échelle d'une vraie clientèle. Le fichier `ch07-observationnel.csv` contient 4 000 clients dont la gérante a **ciblé** l'offre, et `ch07-observationnel-verite.csv` leurs deux dépenses potentielles (information que, dans la vraie vie, personne n'a). Rejouons l'histoire de deux façons : avec le ciblage réel de la gérante, et avec des attributions tirées au sort (2 000 tirages, avec la même proportion de clients traités).

Sur ces 4 000 clients, 46,2 % ont reçu l'offre. Les effets vrais sont **ATE = 15,53 €** et ATT = 16,64 €. Avec le ciblage de la gérante, la différence naïve vaut **50,50 €**, plus de trois fois l'ATE. Avec les 2 000 attributions tirées au sort, la différence moyenne est de 15,46 €.


![Distribution de la différence naïve quand l'attribution est tirée au sort (2 000 tirages), comparée à la valeur obtenue avec le ciblage de la gérante et à la vérité.](figures/ch07-randomisation.png)


Les 2 000 attributions aléatoires se répartissent **autour de la vérité** (en bleu), avec un écart-type d'environ 2,3 € (95 % des tirages tombent entre 11,1 et 19,9). Le ciblage de la gérante, lui, donne un résultat très éloigné, **bien en dehors** de cette distribution : ce n'est pas un hasard d'échantillonnage, c'est un **biais** systématique.

> ✅ **À retenir (7.1.2 et 7.1.3).** Un effet causal compare **deux mondes**, dont un seul est observé. Une différence entre groupes = effet causal + biais de sélection. La **randomisation** annule le biais de sélection *par construction*, sans modèle.

### 7.1.4 Une vraie expérience : l'offre de bienvenue

Bonne nouvelle : pour l'un de ses lancements, la gérante a **vraiment** tiré au sort. Dans `clients.csv`, la colonne `offre_bienvenue` a été attribuée par pile ou face à chacun des 2 000 clients. Analysons cette expérience comme le ferait un data scientist, en trois temps : vérifier la randomisation, estimer l'effet, interpréter.

**Étape 1 : la randomisation a-t-elle bien « marché » ?** Une randomisation équilibre les groupes *en moyenne* ; sur un échantillon fini, un déséquilibre est possible. On le contrôle avec un tableau d'équilibre. Pour comparer des variables d'unités différentes, on utilise la **différence moyenne standardisée** (SMD) : l'écart des moyennes divisé par l'écart-type typique,

$$\text{SMD}=\frac{\bar x_1-\bar x_0}{\sqrt{(s_1^2+s_0^2)/2}},$$

et l'on considère en pratique qu'une valeur inférieure à 0,1 en valeur absolue est un bon équilibre.


Le tirage a donné 1 015 clients avec offre et 985 sans. Toutes les SMD sont bien inférieures à 0,1 en valeur absolue (la plus grande, −0,068, concerne l'âge : 35,4 ans en moyenne avec offre, 36,1 sans) : les deux groupes se ressemblent sur tout ce que nous observons. Les tests donnent des p-valeurs de 0,13 (âge, test de Welch), 0,47 (canal, khi-deux) et 0,98 (ville, khi-deux) : rien de significatif. Les tests de significativité sont ici **secondaires** : le tirage au sort a été fait, donc toute différence est par construction due au hasard, et il est inutile de « tester » l'hypothèse que le hasard est hasardeux. (Si l'on testait pourtant des dizaines de variables à 5 %, on s'attendrait à trouver quelques « différences significatives » par pur hasard : c'est le problème des comparaisons multiples du volume I, section 3.5.5.)

**Étape 2 : estimer l'effet.** Pour le rachat à 12 mois (variable binaire), l'estimateur de l'effet moyen est la différence de proportions $\hat p_1-\hat p_0$, et son intervalle de confiance de Wald est celui de la section 3.4.5 du volume I : $\hat p_1-\hat p_0\pm1{,}96\sqrt{\hat p_1(1-\hat p_1)/n_1+\hat p_0(1-\hat p_0)/n_0}$.

**Résultat.** 56,9 % des clients avec offre rachètent dans l'année, contre 44,8 % sans : l'effet moyen est de **+12,2 points** (intervalle de confiance à 95 % : de 7,8 à 16,5 points), soit +27 % en relatif, ou encore environ un rachat de plus pour 8 offres envoyées.


Même question avec un modèle logistique (chapitre 2, section 2.2). Attention : le coefficient de la régression est un **rapport de cotes** (échelle logarithmique), pas une différence de probabilités. Pour retrouver une différence de probabilités, on calcule l'**effet marginal moyen** :

```python
import statsmodels.formula.api as smf

logit = smf.logit("rachat_12m ~ offre_bienvenue", data=c).fit(disp=0)
marg = logit.get_margeff(dummy=True).summary_frame()     # dummy=True : vraie différence de probabilités 1 - 0
print(marg[["dy/dx", "Conf. Int. Low", "Cont. Int. Hi."]].round(3).to_string())
```
<!--sortie-->
```text
                 dy/dx  Conf. Int. Low  Cont. Int. Hi.
offre_bienvenue  0.122           0.078           0.165
```

Le coefficient vaut 0,49 (rapport de cotes 1,63) et l'effet marginal moyen 0,122, avec le même intervalle que ci-dessus : les deux approches coïncident (c'est normal : avec une seule variable binaire explicative, le modèle logistique est « saturé » et reproduit exactement les deux proportions ; l'option `dummy=True` demande la vraie différence de probabilités entre $T=1$ et $T=0$, et non une dérivée). Pour la dépense annuelle, variable continue et asymétrique, on compare les moyennes avec le test de Welch du volume I (section 3.4.3). Résultat : 243,5 € de dépense moyenne avec offre contre 250,5 € sans, soit un effet de −7,0 € (intervalle de confiance à 95 % : de −33,1 à +19,0 € ; p = 0,60).


On peut aussi **ajuster** l'estimation sur des covariables. Dans une expérience randomisée, ce n'est pas pour corriger un biais (il n'y en a pas) mais pour gagner en **précision** : les covariables qui expliquent la dépense réduisent le bruit résiduel. Ici le gain est négligeable : l'effet passe de 0,122 à 0,121 et l'erreur-type de 0,0222 à 0,0221 (l'âge, le canal et la ville expliquent très peu le rachat).


**Étape 3 : interpréter, et révéler la vérité.** L'offre augmente de façon nette la probabilité de rachat, de l'ordre de 12 points de pourcentage (57 % de rachat avec l'offre, contre 45 % sans), alors qu'on ne détecte **aucun effet sur la dépense annuelle** (l'intervalle de confiance contient très largement 0). Comme les données sont simulées, nous pouvons comparer à la vérité. Dans le modèle de simulation, l'offre augmente de **0,55** la log-cote du rachat et n'intervient pas du tout dans le nombre de commandes ni dans le panier. L'effet moyen en probabilité se calcule en moyennant sur la population simulée la différence $\text{expit}(\eta+0{,}55)-\text{expit}(\eta)$ :


L'estimation expérimentale (0,122) est très proche de la vérité (0,124), et l'intervalle de confiance la contient. Notez aussi ce que l'expérience **ne** dit **pas** : elle donne l'effet *moyen* ; elle ne dit pas pour qui l'offre marche le mieux, ni *pourquoi* elle marche. Et si l'on fouille dix sous-groupes à la recherche d'un effet, on retombe dans le piège des tests multiples.

> ⚠️ **Absence de preuve n'est pas preuve d'absence.** L'intervalle de confiance de l'effet sur la dépense va de −33 à +19 € environ, pour une dépense moyenne d'environ 247 € : il exclut un effet massif, mais pas un effet de quelques dizaines de euros (une dizaine de pour cent de la dépense), dans un sens ou dans l'autre. Ce que l'on peut dire honnêtement : « cette expérience n'a pas détecté d'effet sur la dépense annuelle ». Ici, nous savons que l'effet est réellement nul ; dans la vraie vie, on ne le saurait pas. Ce qui compte pour la décision, c'est la **largeur** de l'intervalle.

> ✅ **À retenir (7.1.4).** Une expérience randomisée s'analyse simplement : tableau d'équilibre, différence de moyennes, intervalle de confiance. L'ajustement sur covariables, facultatif, améliore la précision. Tout le reste de ce chapitre sert à *approcher* ce résultat quand le tirage au sort n'a pas été possible.

### 7.1.5 Quand on ne peut pas tirer au sort : les graphes causaux

Beaucoup de questions causales ne se prêtent pas à une expérience : on ne peut pas choisir au hasard dans quelle ville vit un client, ni refaire le passé. Il faut alors **raisonner** sur la façon dont les données ont été produites. L'outil standard est le **graphe orienté acyclique** (DAG, de l'anglais *directed acyclic graph*, popularisé par Judea Pearl) : chaque variable est un **nœud**, et une **flèche** $A\to B$ signifie « $A$ a une influence causale directe sur $B$ ». Il est acyclique : aucune variable ne peut être sa propre cause en suivant les flèches.

Un graphe est une **hypothèse sur le monde**, pas une conclusion tirée des données. Mais cette hypothèse est explicite, discutable, et elle détermine très précisément **quelles variables il faut ajuster, et lesquelles il ne faut surtout pas ajuster**. Trois structures élémentaires suffisent à comprendre tous les graphes.


![Les trois structures élémentaires d'un graphe causal : la chaîne (la cause agit à travers un médiateur), la fourche (une cause commune crée une association), la collision (deux causes d'un même effet).](figures/ch07-dag-structures.png)

- **La chaîne** $A\to M\to B$ : $A$ agit sur $B$ **à travers** $M$ (le médiateur). Exemple : l'offre incite à *utiliser le code*, qui fait dépenser. $A$ et $B$ sont associés ; si l'on **fige** $M$, l'association disparaît (la voie est bloquée).
- **La fourche** $A\leftarrow C\to B$ : $C$ est une **cause commune** (un *facteur de confusion*). Elle crée une association entre $A$ et $B$ **sans** qu'aucune des deux n'agisse sur l'autre. Exemple : l'engagement pousse la gérante à envoyer l'offre *et* fait dépenser. Si l'on **fige** $C$, l'association disparaît.
- **La collision** $A\to K\leftarrow B$ : $K$ est un **effet commun** (un *collider*). $A$ et $B$ sont **indépendants**, et ne deviennent associés que si l'on **fige** $K$ : une surprise à retenir, que nous illustrons plus bas.

Dans les deux premiers cas, « figer » une variable la rend inoffensive ; dans le troisième, c'est au contraire **la figer qui crée le problème**. C'est pourquoi on ne peut pas se contenter de la règle « ajustons sur tout ce que l'on a ». Pour chaque structure, nous allons maintenant **simuler** le phénomène et regarder ce que fait la régression.

### 7.1.6 La fourche : confusion et paradoxe de Simpson

Reprenons des chiffres à la main. La gérante a envoyé l'offre à 120 clients et pas à 120 autres, et observe le rachat à 12 mois. Les clients viennent de deux canaux : la **boutique** (clients très fidèles, taux de rachat élevé) et **Réseaux** (clients venus des réseaux sociaux, plus volatils). La gérante a envoyé l'offre surtout à des clients venus des réseaux sociaux, ceux qu'elle « avait envie de convaincre ».

| Canal | Offre envoyée | Clients | Rachats | Taux |
|---|---|---|---|---|
| Boutique | oui | 20 | 18 | 90 % |
| Boutique | non | 100 | 80 | 80 % |
| Réseaux | oui | 100 | 40 | 40 % |
| Réseaux | non | 20 | 6 | 30 % |
| **Total** | **oui** | **120** | **58** | **48,3 %** |
| **Total** | **non** | **120** | **86** | **71,7 %** |

Lisez les deux dernières lignes : **globalement**, les clients qui ont reçu l'offre rachètent *moins* (48 % contre 72 %). Mais regardez chaque canal : en boutique, l'offre fait passer le taux de 80 % à 90 % ; sur Réseaux, de 30 % à 40 %. L'offre **améliore** le rachat de **10 points dans chaque canal**. Comment le total peut-il dire l'inverse ? Parce que l'offre a été envoyée surtout au canal où l'on rachète peu : les « traités » sont majoritairement des clients venus des réseaux sociaux, qui auraient peu racheté de toute façon. C'est le **paradoxe de Simpson**, qui n'est un paradoxe que si l'on oublie la fourche *Canal → Offre*, *Canal → Rachat*.

Quelle est alors la bonne réponse ? Celle qui **compare à canal égal**, puis fait la moyenne. L'effet moyen (ATE) se calcule par **standardisation** : on pondère l'effet dans chaque canal par la part de ce canal dans toute la population (ici 120 clients sur 240 de chaque canal, soit 50 %) : $0{,}5\times10\,\%+0{,}5\times10\,\%=10$ points. Vérifions au calcul, puis avec une régression logistique.


Le signe change : sans ajustement, le modèle logistique conclut que l'offre est **nuisible** (coefficient −0,99) ; avec le canal, qui est la cause commune, il retrouve un effet **positif** (+0,56). Moralité : la bonne analyse **dépend de l'histoire causale**, pas seulement des chiffres. Les mêmes données, avec une histoire différente, pourraient exiger de ne *pas* ajuster : nous l'illustrons tout de suite.

> ⚠️ **Le paradoxe de Simpson n'est pas une bizarrerie arithmétique.** Les mêmes chiffres, lus avec deux histoires causales différentes, appellent deux conclusions opposées. Si le canal était une **conséquence** de l'offre (disons que l'offre fait venir des clients d'un autre canal), il ne faudrait *pas* ajuster dessus. C'est pourquoi aucun test statistique ne peut décider seul s'il faut ou non ajuster.

### 7.1.7 La chaîne : ne pas ajuster sur un médiateur

Autre cas : l'offre agit **à travers** un médiateur. Simulons une expérience où l'offre est **randomisée**, et où elle agit de deux façons : par l'utilisation du code promotionnel (effet de 30 € quand le code est utilisé), et par un petit effet direct de « bonne image » (8 €). Les clients les plus motivés (variable `motivation`, qui influence aussi la dépense) utilisent plus souvent le code.


Sans ajustement, la régression retrouve l'**effet total** (25,6 € estimés pour 25,5 vrais) (le chiffre que la gérante cherche : « que rapporte l'envoi d'une offre ? »). En ajoutant le médiateur, on obtient −0,8 € : un chiffre qui n'est **ni l'effet total** (on a retiré la voie par le code), **ni l'effet direct** de 8 € que l'on pourrait croire avoir isolé. Pourquoi ? En comparant, parmi les clients sans code, ceux qui ont reçu l'offre à ceux qui ne l'ont pas reçue, on compare des clients **peu motivés** (ceux qui n'ont pas utilisé le code malgré l'offre) à des clients **de motivation moyenne** (tous ceux qui n'ont pas reçu d'offre) : la dernière sortie montre cet écart de motivation, qui à lui seul fait baisser la dépense d'environ 9 € et masque presque exactement les 8 € de l'effet direct. Nous avons ouvert, sans le vouloir, un chemin biaisé. Retenez la règle d'or : **n'ajustez jamais sur une variable qui est affectée par le traitement** (variable « post-traitement »), sauf si l'on cherche explicitement un effet direct *et* que l'on sait justifier l'absence de confusion entre médiateur et résultat.

### 7.1.8 La collision : ne pas conditionner sur un effet commun

Dernier cas, le plus surprenant. La boutique garde au catalogue les prototypes de produits qui ont une bonne **qualité** *ou* un grand **attrait** visuel (ou les deux) : un produit à la fois laid et fragile est abandonné. Imaginons que, dans la réalité, qualité et attrait sont **parfaitement indépendants** : savoir qu'un prototype est beau ne dit rien sur sa solidité.


![À gauche, tous les prototypes : aucune relation entre qualité et attrait. À droite, seuls les produits retenus au catalogue : une relation négative apparaît.](figures/ch07-collider.png)


Parmi les 1 811 produits **retenus** sur 6 000, la corrélation est de −0,48, alors qu'elle est nulle (+0,01) sur l'ensemble : un produit moins beau doit, pour être gardé, être plus solide, et réciproquement. Aucun lien réel n'existe pourtant entre les deux. L'effet est dû uniquement au **filtre** : on a conditionné sur un effet commun. Ce mécanisme est partout : on ne voit que les clients qui ont **répondu** à l'enquête (tous ne le font pas), les entreprises qui ont **survécu**, les patients **hospitalisés**. Quand on n'observe qu'une population sélectionnée par un effet commun, on crée des associations fantômes. Cette situation s'appelle aussi un **biais de sélection** (au sens des graphes), et on ne peut pas la corriger en ajoutant des variables : il faut éviter de conditionner dessus, ou modéliser la sélection.

> ✅ **À retenir (7.1.5 à 7.1.8).** Un graphe causal rend explicites les hypothèses. **Fourche** : ajuster sur la cause commune (c'est la correction du biais de confusion). **Chaîne** : ne pas ajuster sur le médiateur si l'on veut l'effet total. **Collision** : ne pas conditionner sur un effet commun. Aucune de ces règles ne se lit dans les données : elles viennent du **raisonnement**.

### 7.1.9 Le critère de la porte dérobée

Ces trois structures sont les briques d'une règle générale, le **critère de la porte dérobée** (*back-door criterion*). Dans un graphe, un **chemin** entre $T$ et $Y$ est une suite de flèches reliant les deux, quel que soit leur sens. On distingue :

- les **chemins directs** $T\to\cdots\to Y$ (toutes les flèches vont dans le sens de $T$ vers $Y$) : ce sont eux qui portent l'effet causal ;
- les **chemins « porte dérobée »** : ceux qui **commencent par une flèche entrant dans $T$** ($T\leftarrow\cdots$) ; ils créent une association non causale (la confusion).

Un ensemble de variables $S$ **satisfait le critère de la porte dérobée** pour estimer l'effet de $T$ sur $Y$ si : (i) aucune variable de $S$ n'est un **descendant** de $T$ (pas de variable post-traitement) ; (ii) $S$ **bloque** tous les chemins porte dérobée entre $T$ et $Y$. Un chemin est bloqué par $S$ s'il contient une chaîne ou une fourche dont le nœud central est dans $S$, ou une collision dont ni le nœud central, ni aucun descendant, n'est dans $S$.

> 📐 **Ce que garantit le critère.** Si $S$ satisfait le critère, alors, **à valeur de $S$ fixée**, le traitement est comme tiré au sort : $Y(t)\perp T\mid S$ (c'est l'hypothèse d'**ignorabilité conditionnelle**). Alors $\mathbb E[Y(t)\mid S=s]=\mathbb E[Y\mid T=t,S=s]$, et en moyennant sur la population on obtient la **formule d'ajustement** :
>
> $$\mathbb E[Y(t)]=\sum_s \mathbb E[Y\mid T=t,\,S=s]\;\mathbb P(S=s),\qquad \text{ATE}=\sum_s\big(\mathbb E[Y\mid T=1,S=s]-\mathbb E[Y\mid T=0,S=s]\big)\mathbb P(S=s).$$
>
> C'est exactement la standardisation que nous avons faite à la main pour le paradoxe de Simpson (avec $S$ = le canal). Si $S$ contient des variables continues, le même principe s'écrit avec des intégrales, et on le met en œuvre par régression, appariement ou pondération.

Appliquons cela au cas d'étude de la suite : l'offre de bienvenue **ciblée** par la gérante (fichier `ch07-observationnel.csv`). Nous supposons le graphe suivant : l'âge et le canal influencent l'engagement ; l'âge, le canal **et** l'engagement influencent à la fois la décision d'envoyer l'offre (c'est ainsi que la gérante choisit) et la dépense ; l'offre influence la dépense.


```python
modele = smf.ols("depense ~ offre + age + C(canal) + engagement", d).fit()
print(f"effet estimé de l'offre, après ajustement sur l'âge, le canal et l'engagement : {modele.params['offre']:.1f} €")
```
<!--sortie-->
```text
effet estimé de l'offre, après ajustement sur l'âge, le canal et l'engagement : 14.8 €
```

![Le graphe supposé de l'étude observationnelle : l'âge, le canal et l'engagement sont des causes communes de l'offre et de la dépense.](figures/ch07-dag-etude.png)

Les chemins porte dérobée de *Offre* vers *Dépense* passent tous par l'âge, le canal ou l'engagement (par exemple *Offre ← Engagement → Dépense*). L'ensemble $S=\{\text{âge},\text{canal},\text{engagement}\}$ les bloque tous, et ne contient aucun descendant de l'offre : il satisfait le critère. Un ensemble incomplet, comme $\{\text{âge},\text{canal}\}$, laisse ouvert le chemin par l'engagement. Mettons-le à l'épreuve en ajustant par régression de façon **progressive**, et en comparant avec la vérité (15,5 €, calculée plus haut avec les résultats potentiels).

```text
     ensemble d'ajustement  effet estimé  IC95 bas  IC95 haut
          aucun ajustement          50.5      46.3       54.7
                     + âge          46.1      41.9       50.3
             + âge + canal          47.0      42.8       51.2
+ âge + canal + engagement          14.8      11.0       18.7

vérité : ATE = 15.5   ATT = 16.6
```

Voilà la leçon en une table : tant que l'**engagement** manque, l'estimation reste entre 46 et 51 €, **plus de trois fois** la vérité (15,5 €), et ajouter l'âge et le canal, variables pourtant « sensées », n'y change presque rien. Dès que l'engagement est inclus, l'estimation tombe près de la vérité et son intervalle de confiance (de 11,0 à 18,7) contient la vérité (15,5). Le **bon ensemble** n'est pas « le plus grand possible » mais celui qui bloque les chemins de confusion.

> ⚠️ **Deux pièges de cet exemple.** (1) Le critère suppose que l'on a **mesuré** tous les facteurs de confusion. Ici, l'engagement est observé ; s'il ne l'était pas, aucun ajustement ne pourrait corriger le biais (c'est le sujet de 7.4). (2) Dans une régression linéaire, le coefficient de l'offre est une moyenne **pondérée** des effets individuels : lorsque l'effet varie d'un client à l'autre (ici, il est plus fort sur Réseaux), elle ne coïncide pas exactement avec l'ATE. C'est une raison, parmi d'autres, d'utiliser les méthodes de la section 7.2 qui visent explicitement l'ATE ou l'ATT.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.5, exercices 7.1 à 7.4 et 7.11.

> ✅ **À retenir (7.1).** (1) Effet causal = comparaison de deux mondes, dont un seul est observé. (2) Différence observée = effet causal + biais de sélection. (3) La **randomisation** supprime le biais de sélection. (4) Sans randomisation, on s'appuie sur un **graphe** et le critère de la porte dérobée : ajuster sur les causes communes, **pas** sur les médiateurs ni sur les effets communs. (5) Aucun ajustement ne corrige une confusion **non mesurée**.


## 7.2 Scores de propension : comparer ce qui est comparable

> 💡 **Intuition.** la gérante n'a pas tiré au sort ; elle a **choisi** à qui envoyer l'offre. Mais en observant comment elle a choisi (engagement, âge, canal), on peut reconstituer, pour chaque client, la **probabilité** qu'il ait reçu l'offre : son *score de propension*. Deux clients qui avaient la **même** probabilité de recevoir l'offre, dont l'un l'a reçue et l'autre non, sont presque comme deux clients tirés au sort : la différence entre eux, c'est la chance. Le score de propension résume en **un seul nombre** tout ce qui a guidé le choix.

Nous poursuivons l'étude de la section 7.1.9 : le fichier `ch07-observationnel.csv`, 4 000 clients, et le critère de la porte dérobée, satisfait par l'ensemble $S=\{\text{âge},\text{canal},\text{engagement}\}$. L'ajustement par régression y a donné une estimation proche de la vérité. Pourquoi aller plus loin ? Pour trois raisons : la régression suppose une **forme** particulière pour le lien entre covariables et résultat ; elle ne dit rien sur le **chevauchement** entre traités et non-traités (peut-on réellement comparer ces clients ?) ; et elle ne permet pas de cibler explicitement l'ATE ou l'ATT.

### 7.2.1 Pourquoi un score ? La malédiction de la dimension

L'idée naturelle serait de comparer **à l'identique** : pour chaque combinaison d'âge, de canal et d'engagement, comparer les clients qui ont reçu l'offre à ceux qui ne l'ont pas reçue. Voyons ce que cela donne en pratique.


Avec seulement trois covariables, les 4 000 clients se dispersent en 2 923 cellules, et **seules 413 d'entre elles** contiennent à la fois un client avec offre et un client sans offre : 1 035 clients, soit un peu plus d'un quart, sont comparables « à l'identique ». Les trois quarts restants n'ont aucun jumeau de l'autre groupe. Avec dix ou vingt covariables, ce serait sans espoir. C'est la **malédiction de la dimension**. Le **score de propension** de Rosenbaum et Rubin (1983) l'évite :

$$e(x)=\mathbb P(T=1\mid X=x).$$

> 📐 **Pourquoi un nombre suffit : le théorème du score d'équilibrage.** Faisons deux affirmations.
>
> **(1) Le score équilibre les covariables.** Par définition, $\mathbb P(T=1\mid X)=e(X)$, qui est une fonction de $X$. Donc, une fois $e(X)$ fixé, $X$ n'apporte plus aucune information supplémentaire sur $T$ : $\mathbb P(T=1\mid X,e(X))=e(X)=\mathbb P(T=1\mid e(X))$, c'est-à-dire $T\perp X\mid e(X)$. Parmi les clients qui ont le **même score**, ceux qui ont reçu l'offre et les autres ont la **même distribution de covariables**.
>
> **(2) Si l'ignorabilité tient avec $X$, elle tient avec $e(X)$.** Supposons $T\perp Y(t)\mid X$. Alors
> $$\mathbb P\big(T=1\mid Y(t),e(X)\big)=\mathbb E\big[\mathbb P(T=1\mid Y(t),X)\mid Y(t),e(X)\big]=\mathbb E\big[e(X)\mid Y(t),e(X)\big]=e(X),$$
> qui ne dépend pas de $Y(t)$ : $T\perp Y(t)\mid e(X)$. **Comparer des clients de même score suffit** à supprimer le biais de confusion.
>
> On a donc remplacé un problème en dimension $p$ par un problème en dimension 1. (Le prix à payer : il faut **estimer** $e(x)$, et la qualité de cette estimation conditionne tout.)

Deux hypothèses sont nécessaires, et il faut les avoir en tête à chaque étape :

1. **Ignorabilité conditionnelle** (« pas de confusion non mesurée ») : après avoir tenu compte de $X$, l'attribution est comme tirée au sort. Elle est **invérifiable** à partir des données : c'est une hypothèse sur le monde, justifiée par la connaissance du métier (le graphe de 7.1.9).
2. **Chevauchement** (*positivité*) : $0<e(x)<1$ pour tous les $x$ rencontrés. Si un type de client n'a *jamais* reçu d'offre, on ne peut rien dire de ce qui se serait passé s'il l'avait reçue. Cette hypothèse, elle, se **vérifie en partie** sur les données.

### 7.2.2 Estimer le score et vérifier le chevauchement

Le score est une probabilité qui dépend de covariables : c'est un problème de régression logistique (chapitre 2, section 2.2). Le modèle doit inclure les variables qui ont guidé le choix de l'attribution.

```python
modele_ps = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
d["ps"] = modele_ps.predict(d)            # score de propension de chaque client
```

Un coefficient positif sur l'engagement et sur Réseaux, négatif sur l'âge : le modèle retrouve la manière dont la gérante choisissait. L'AUC (aire sous la courbe ROC : la probabilité qu'un client avec offre ait un score plus élevé qu'un client sans offre tiré au hasard) mesure à quel point on peut *prédire* l'attribution : ici 0,76, avec un score moyen de 0,57 chez les clients avec offre contre 0,37 chez les autres. Contrairement à un projet de prédiction, **on ne cherche pas ici un score parfait** : un modèle d'attribution qui prédit parfaitement l'offre signalerait au contraire un **manque de chevauchement**.


![Distribution du score de propension estimé selon que le client a reçu l'offre ou non : les deux distributions sont décalées, mais se chevauchent largement.](figures/ch07-chevauchement.png)

Les clients avec offre ont des scores plus élevés, ce qui est normal : c'est la trace du ciblage. L'important est que **les deux histogrammes se recouvrent** sur presque tout l'intervalle : pour (presque) chaque client avec offre, on trouve des clients sans offre qui lui ressemblent. Calcul fait sur les bornes, seuls 22 clients sur 4 000 se trouvent en dehors du support commun (de 0,049 à 0,966) : le chevauchement est bon. C'est le diagnostic de positivité.

> ⚠️ **Le diagnostic le plus important.** Avant d'estimer quoi que ce soit, regardez ce graphique. Si les deux distributions sont presque disjointes, aucune méthode ne pourra répondre, et il faut le dire (ou restreindre la population étudiée). Un score proche de 0 ou de 1 pour de nombreux clients annonce des poids énormes et une estimation instable.

### 7.2.3 L'appariement

La première méthode est la plus intuitive : pour chaque client **avec** offre, on cherche un client **sans** offre qui lui **ressemble** (score voisin), et on compare leurs dépenses. L'effet estimé est alors la moyenne de ces différences. Comme on part des traités, on estime l'**ATT**.

Voici la procédure. On travaille sur le *logit* du score (qui s'étale mieux que le score). Pour chaque client avec offre, on cherche le client sans offre dont le logit est le plus proche, **avec remise** (un même témoin peut servir plusieurs fois). On impose un **calibre** : on refuse les appariements trop lointains (écart de logit supérieur à 0,2 écart-type), faute de quoi on compare des clients qui ne se ressemblent pas. L'effet estimé est la moyenne des différences de dépense entre chaque traité apparié et son témoin.


Presque tous les traités (1 843 sur 1 850) ont trouvé un voisin acceptable, et l'estimation (14,4 €) est du bon ordre de grandeur face à l'ATT vrai (16,6 €), sans être exacte : combien faut-il s'en méfier ? C'est la question de l'incertitude.

Pour l'incertitude, la formule de la variance n'est pas simple (la procédure inclut l'estimation du score *et* l'appariement). On utilise donc le **bootstrap** (volume I, section 3.3.5) en **refaisant toute la procédure** sur chaque échantillon rééchantillonné : c'est la bonne façon de tenir compte de toutes les sources d'aléa.


L'intervalle de confiance, de 6,6 à 20,2 €, contient la vérité (16,6) mais il est **large** : l'erreur-type de 3,7 € est près de deux fois celle de la régression. C'est une caractéristique de l'appariement au plus proche voisin, qui ne compare chaque traité qu'à *un seul* témoin et gaspille donc de l'information.

Vérifions surtout que l'appariement a bien **rendu les groupes comparables**. On mesure la SMD de chaque covariable **avant** et **après** appariement (les témoins sont comptés autant de fois qu'ils sont utilisés).


Avant l'appariement, l'engagement présente une SMD de 0,92 (un écart considérable : les traités sont presque un écart-type plus engagés que les témoins), et l'âge et le canal Réseaux des SMD de −0,34 et +0,31 ; après, toutes les SMD sont inférieures à 0,05 en valeur absolue. L'appariement a bien produit des groupes comparables sur ce que nous avons mesuré. Notez que ce diagnostic porte uniquement sur les covariables **observées** : il ne dit rien sur celles que nous aurions oublié de mesurer.

### 7.2.4 La pondération par l'inverse du score (IPW)

L'appariement jette des données (les traités sans voisin, les témoins jamais utilisés). Une autre façon de rendre les groupes comparables est de les **repondérer** : on donne plus de poids aux clients **peu probables** dans leur groupe (un client avec offre qui avait peu de chances de la recevoir « représente » beaucoup de clients semblables qui, eux, ne l'ont pas reçue). Ce procédé, la **pondération par l'inverse de la probabilité de traitement** (IPW), s'illustre à la main.

Imaginons deux types de clients, 10 de chaque. Les clients de type A (jeunes, très engagés) reçoivent l'offre avec probabilité $0{,}8$ (8 sur 10) ; ceux de type B, avec probabilité $0{,}2$ (2 sur 10). L'effet réel de l'offre est de $+30$ € dans les deux types. Les dépenses moyennes observées sont :

| | Type A ($e=0{,}8$) | Type B ($e=0{,}2$) |
|---|---|---|
| avec offre | 200 € (8 clients) | 120 € (2 clients) |
| sans offre | 170 € (2 clients) | 90 € (8 clients) |

La comparaison brute donne $(8\times200+2\times120)/10-(2\times170+8\times90)/10=184-106=78$ € : à nouveau très loin des 30 réels, parce que les traités sont surtout de type A. Pondérons chaque client par $1/e$ pour les traités et $1/(1-e)$ pour les témoins :

- traités de type A : poids $1/0{,}8=1{,}25$ ; traités de type B : poids $1/0{,}2=5$ ;
- témoins de type A : poids $1/(1-0{,}8)=5$ ; témoins de type B : poids $1/(1-0{,}2)=1{,}25$.

La « population pondérée » a alors, dans chaque type, **10 traités et 10 témoins** : $8\times1{,}25=10$ et $2\times5=10$ pour les traités, et symétriquement pour les témoins. Le biais de confusion a disparu : le type ne prédit plus l'attribution.

```python
w = np.where(d["offre"] == 1, 1 / d["ps"], 1 / (1 - d["ps"]))      # poids IPW de chaque client
traites, temoins = d["offre"] == 1, d["offre"] == 0
ate_ipw = (np.average(d.loc[traites, "depense"], weights=w[traites])
           - np.average(d.loc[temoins, "depense"], weights=w[temoins]))
print(f"ATE estimé par IPW (version normalisée) : {ate_ipw:.2f} €")
```
<!--sortie-->
```text
ATE estimé par IPW (version normalisée) : 14.36 €
```
On obtient 13,4 € avec l'estimateur de Horvitz-Thompson et 14,4 € avec la version normalisée pour l'ATE (vérité : 15,5 €), et 11,8 € pour l'ATT (vérité : 16,6 €).


Les moyennes pondérées valent : pour les traités, $(8\times1{,}25\times200+2\times5\times120)/20=160$ € ; pour les témoins, $(2\times5\times170+8\times1{,}25\times90)/20=130$ €. La différence $160-130=30$ € retrouve **exactement** l'effet réel. Voici la justification générale.

> 📐 **Pourquoi l'IPW est sans biais.** Si l'ignorabilité tient avec $X$, alors
> $$\mathbb E\!\left[\frac{T\,Y}{e(X)}\right]=\mathbb E\!\left[\frac{T\,Y(1)}{e(X)}\right]=\mathbb E\!\left[\mathbb E\!\left[\frac{T}{e(X)}\,\Big|\,X,Y(1)\right]Y(1)\right]=\mathbb E\big[Y(1)\big],$$
> car $\mathbb E[T\mid X,Y(1)]=e(X)$. De même $\mathbb E\big[(1-T)Y/(1-e(X))\big]=\mathbb E[Y(0)]$. D'où l'estimateur de l'ATE (de Horvitz-Thompson)
> $$\widehat{\text{ATE}}_{\text{IPW}}=\frac1n\sum_i\left(\frac{T_iY_i}{\hat e(X_i)}-\frac{(1-T_i)Y_i}{1-\hat e(X_i)}\right).$$
> En pratique, on préfère la version **normalisée** (de Hájek) qui divise par la somme des poids dans chaque groupe : $\ \frac{\sum_i w_iT_iY_i}{\sum_i w_iT_i}-\frac{\sum_i w_i(1-T_i)Y_i}{\sum_i w_i(1-T_i)}$. Elle est moins sensible aux poids extrêmes. Pour l'ATT, les traités gardent le poids 1 et les témoins reçoivent $e/(1-e)$.


Premier diagnostic des poids : **l'effectif effectif**, $n_{\text{eff}}=(\sum w_i)^2/\sum w_i^2$. Des poids très inégaux signifient que quelques clients pèsent énormément et que l'information réelle est bien inférieure à $n$.


Les poids sont inégaux (de 1 à près de 30, avec une médiane voisine de 1,6), mais pas dramatiquement : l'effectif effectif est d'environ 1 260 pour les 1 850 traités et 1 510 pour les 2 150 témoins, soit une perte d'information de l'ordre d'un quart à un tiers. Le bon chevauchement évite le pire ; si quelques poids dépassaient 50 ou 100, on tronquerait ou on restreindrait la population, au prix d'un léger biais pour gagner beaucoup de stabilité.

Notez que **la troncature a fait passer l'estimation de 14,4 à 17,5 €** : l'IPW est sensible à quelques poids élevés. C'est son talon d'Achille : un estimateur sans biais, mais **plus variable** que la régression. Mesurons cette variabilité avec le bootstrap, en réestimant le score à chaque rééchantillonnage.


Les deux intervalles contiennent la vérité. Mais regardez les erreurs-types : 2,5 € pour l'ATE et 3,4 € pour l'ATT, plus que les 2,0 € de la régression de 7.1.9. L'écart de 4,8 € entre l'ATT estimé par IPW (11,8) et l'ATT vrai (16,6) représente environ 1,4 erreur-type : rien d'anormal, mais une bonne illustration de la précision limitée de la méthode. L'ATT est plus incertain que l'ATE ici, car il ne repose que sur les 1 850 traités et sur des témoins très inégalement pondérés.

Le même diagnostic d'équilibre que pour l'appariement s'applique, et se représente par un **graphique de Love** : une ligne par covariable, la SMD avant (rond gris) et après pondération (rond bleu).

On trouve **14,9 €** (erreur-type bootstrap 2,4 € ; intervalle de confiance à 95 % de 10,1 à 19,7 €), pour une vérité de 15,5 €.


![Graphique de Love : la différence moyenne standardisée de chaque covariable avant et après pondération par l'inverse du score ; la bande grise marque l'intervalle de ±0,1.](figures/ch07-love.png)

Toutes les covariables, qui avaient un déséquilibre marqué (surtout l'engagement), tombent dans la bande de $\pm0{,}1$ après pondération : la pseudo-population est équilibrée.

### 7.2.5 Le meilleur des deux mondes : l'estimateur doublement robuste

Deux stratégies, deux paris. L'**ajustement par régression** parie sur un bon modèle du **résultat** ($Y$ selon $X$ et $T$). L'**IPW** parie sur un bon modèle de l'**attribution** ($T$ selon $X$). L'estimateur **doublement robuste** (AIPW, pour *augmented* IPW) utilise **les deux** :

$$\widehat{\text{ATE}}_{\text{AIPW}}=\frac1n\sum_i\Big[\hat\mu_1(X_i)-\hat\mu_0(X_i)+\frac{T_i\,(Y_i-\hat\mu_1(X_i))}{\hat e(X_i)}-\frac{(1-T_i)\,(Y_i-\hat\mu_0(X_i))}{1-\hat e(X_i)}\Big],$$

où $\hat\mu_t(x)$ est l'espérance estimée du résultat sous le traitement $t$. On lit l'estimateur ainsi : on **impute** l'effet par le modèle de résultat ($\hat\mu_1-\hat\mu_0$), puis on **corrige** la prédiction par les résidus pondérés de l'IPW. Son nom vient de sa propriété remarquable : l'estimateur est **cohérent si au moins l'un des deux modèles est correct** (pas besoin que les deux le soient). C'est une assurance contre l'erreur de spécification.

> 📐 **Pourquoi « doublement » ?** Si $\hat\mu_t=\mu_t$ (modèle de résultat correct), les résidus $Y-\mu_t(X)$ sont de moyenne nulle à $X$ et $T$ fixés, donc le terme de correction s'annule en espérance quel que soit $e$, et il reste $\mathbb E[\mu_1-\mu_0]=\text{ATE}$. Si au contraire $\hat e=e$ (score correct), le terme de correction compense exactement l'erreur d'un mauvais modèle de résultat : $\mathbb E\big[\tfrac{T}{e}(Y-\hat\mu_1)\big]=\mathbb E[Y(1)-\hat\mu_1(X)]$, ce qui annule le biais de $\hat\mu_1$. Dans les deux cas, on retrouve $\mathbb E[Y(1)]-\mathbb E[Y(0)]$.

Mettons cette promesse à l'épreuve avec une **expérience** : on estime l'ATE de quatre façons, en rendant volontairement mauvais l'un des deux modèles. Un « mauvais » modèle de résultat est ici un modèle qui ignore les covariables (une constante par groupe) ; un « mauvais » modèle d'attribution est un score constant (il ignore le ciblage).

```text
modèle de résultat modèle d'attribution  régression  IPW  doublement robuste
           correct              correct        15.0 14.4                14.9
           correct                 faux        15.0 50.5                15.0
              faux              correct        50.5 14.4                14.3
              faux                 faux        50.5 50.5                50.5

ATE vrai : 15.5   (différence naïve : 50.5)
```

Lisons la table. Quand le modèle de résultat est faux, la **régression** échoue (elle donne la différence naïve) ; quand le modèle d'attribution est faux, l'**IPW** échoue ; mais l'estimateur **doublement robuste** reste proche de la vérité dès que **l'un des deux** est correct, et n'échoue que lorsque **les deux** sont faux. C'est une assurance, pas une garantie. Calculons l'estimation « principale » avec l'incertitude correspondante par bootstrap :


Récapitulons toutes les estimations de l'**ATE** et de l'**ATT** de la section, face à la vérité :

```text
                 méthode  estimation  vérité
        différence naïve        50.5    15.5
      régression (7.1.9)        14.8    15.5
               IPW (ATE)        14.4    15.5
doublement robuste (ATE)        14.9    15.5
       appariement (ATT)        14.4    16.6
               IPW (ATT)        11.8    16.6
```

Lecture de la table : toutes les méthodes qui tiennent compte de l'engagement ramènent l'ATE vers la vérité (entre 14,4 et 14,9 contre 15,5, alors que la différence naïve est à 50,5), et l'ATT estimé par appariement (14,4) ou par IPW (11,8) est plus bas que l'ATT vrai (16,6) mais dans l'incertitude statistique de chaque méthode. Ces estimations ne sont pas identiques, et il n'y a aucune raison qu'elles le soient : chacune a sa variance et ses hypothèses. L'essentiel est qu'elles **convergent** vers le même ordre de grandeur, très loin de l'estimation naïve.

> ✅ **À retenir (7.2.1 à 7.2.5).** Le score de propension résume l'attribution en un nombre. Trois usages : **apparier**, **pondérer**, ou combiner avec un modèle de résultat (**doublement robuste**). Dans tous les cas : (1) vérifier le **chevauchement**, (2) vérifier l'**équilibre** après l'ajustement (SMD), (3) accompagner l'estimation d'un intervalle (bootstrap de *toute* la procédure). Ces méthodes ne corrigent que la confusion due aux covariables **observées**.

### 7.2.6 Ce que le score de propension ne fait pas

Terminons par l'avertissement le plus important de la section. Tous les résultats précédents reposaient sur le fait que **l'engagement était observé**. Que se passe-t-il s'il ne l'est pas ? Reprenons l'analyse en le cachant à tous les modèles, ou en ne le mesurant qu'avec du **bruit** (ce qui est le cas typique : un score d'engagement n'est qu'un reflet imparfait de l'enthousiasme réel du client).

```text
                                      situation  ATE doublement robuste
                 engagement parfaitement mesuré                    14.9
engagement mesuré avec du bruit (écart-type 15)                    32.5
engagement mesuré avec du bruit (écart-type 30)                    41.8
engagement mesuré avec du bruit (écart-type 60)                    45.6
                         engagement non observé                    46.9

ATE vrai : 15.5
écart-type de l'engagement lui-même : 15.5
```

À mesure que l'engagement est de moins en moins bien mesuré, l'estimation, pourtant « doublement robuste », **dérive** vers la différence naïve. Les méthodes sophistiquées ne remplacent pas l'information manquante : un facteur de confusion mal mesuré laisse une **confusion résiduelle**. Les écarts-types de bruit (15, 30, 60) sont à comparer à l'écart-type de l'engagement lui-même (15,5, dernière ligne de la sortie) : avec un bruit de 15, la mesure contient autant de bruit que de signal, et l'estimation, pourtant « doublement robuste », est déjà à 32,5 €, au milieu du chemin entre la vérité (15,5) et la différence naïve (50,5).

Reste la question honnête : dans la vraie vie, comment sait-on que l'on a mesuré tous les facteurs de confusion importants ? **On ne le sait pas.** On peut seulement (1) s'appuyer sur la connaissance du processus d'attribution (« comment la gérante a-t-elle décidé ? »), (2) faire des **analyses de sensibilité** (quelle intensité devrait avoir un facteur de confusion caché pour annuler le résultat ?), (3) chercher des situations qui contournent le problème : c'est le rôle des deux sections suivantes.

> ⚠️ **Les trois erreurs classiques avec les scores de propension.** (1) **Régler le score pour qu'il prédise bien** : le but est l'équilibre des covariables, pas l'AUC. (2) **Inclure des variables post-traitement** ou des variables qui ne sont causes que du traitement (cela gonfle la variance sans corriger le biais). (3) **Oublier de vérifier l'équilibre** après ajustement. Une analyse par score sans tableau d'équilibre est incomplète.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.6 et 7.7, exercices 7.5 et 7.6.

> ✅ **À retenir (7.2).** Avec ignorabilité et chevauchement, on peut estimer un effet causal sans randomisation, **à condition d'avoir mesuré les facteurs de confusion**. Cette condition est une hypothèse sur le monde, qu'aucun diagnostic ne confirme complètement.


## 7.3 Différences de différences : l'évolution des uns contre l'évolution des autres

> 💡 **Intuition.** En juillet 2025, la gérante lance une campagne publicitaire sur les réseaux sociaux, mais seulement dans huit grandes villes. Les commandes y augmentent. Est-ce la campagne ? Peut-être, mais les commandes augmentent aussi à l'approche des fêtes, et ces huit villes sont de toute façon plus grandes que les autres. Deux comparaisons naïves sont tentantes : **avant contre après** dans les villes traitées (mais l'été n'est pas l'hiver), ou **traitées contre témoins** après la campagne (mais ces villes étaient déjà plus grosses). La **différence de différences** (DiD) combine les deux pour éliminer les deux pièges à la fois : on compare **l'évolution** des villes traitées à **l'évolution** des villes témoins.

Dans la section précédente, nous avions besoin d'observer tous les facteurs de confusion. Ici, on peut se contenter de beaucoup moins : un facteur de confusion **inobservé** est toléré, **à condition qu'il soit constant dans le temps** (la taille d'une ville) ou qu'il évolue de la même façon pour les deux groupes (la saison). C'est l'avantage des données en **panel** : suivre les mêmes unités avant et après.

### 7.3.1 Les données, et le calcul à la main

Le fichier `ch07-panel-villes.csv` suit 20 villes pendant 24 mois (janvier 2024 à décembre 2025). Huit d'entre elles (les grandes villes) ont reçu la campagne à partir de juillet 2025 (`t = 18`). Cela fait 480 observations, dont 8 villes traitées. Les données sont simulées (`build/sim_ch07.py`, fonction `panel_villes`) : chaque ville a son niveau propre (les grandes villes commandent nettement plus que les autres), une saisonnalité commune à toutes (creux en janvier, pic en décembre), une croissance de 0,4 % par mois, et la campagne multiplie les commandes des villes traitées par $e^{0{,}15}\approx1{,}16$ ; le nombre de commandes est un comptage de Poisson.


Avant tout calcul, on regarde les moyennes de commandes par ville et par mois, dans chaque groupe, avant (`t < 18`) et après (`t ≥ 18`) le lancement :


Faisons les trois comparaisons à la main, à partir de ce tableau :

| | avant | après | variation |
|---|---|---|---|
| villes témoins | 30,6 | 36,1 | $+5{,}5$ |
| villes traitées | 46,9 | 63,0 | $+16{,}1$ |

1. **Avant contre après, villes traitées seulement** : $63{,}0-46{,}9=+16{,}1$ commandes par mois. Mais cette hausse mélange l'effet de la campagne et celui de la saison (le second semestre est plus actif que le premier) : on ne peut pas les séparer.
2. **Traitées contre témoins, après** : $63{,}0-36{,}1=+26{,}9$. Mais les villes traitées étaient déjà plus grandes avant : $46{,}9-30{,}6=+16{,}3$ d'écart *avant* la campagne.
3. **La différence de différences** : on retire à la hausse des villes traitées (+16,1) la hausse que **les villes témoins ont connue sans campagne** (+5,5) :
$$\widehat{\text{DiD}}=\big(\bar Y_{T,\text{après}}-\bar Y_{T,\text{avant}}\big)-\big(\bar Y_{C,\text{après}}-\bar Y_{C,\text{avant}}\big)=16{,}1-5{,}5=+10{,}6\ \text{commandes par mois.}$$

Les villes témoins jouent le rôle de **mesure de ce qui se serait passé** dans les villes traitées en l'absence de campagne : leur hausse naturelle (saison, tendance) est retranchée.

> 📐 **Pourquoi ça marche : l'hypothèse des tendances parallèles.** Notons $Y_{it}(0)$ le résultat de la ville $i$ au mois $t$ **sans** campagne. L'effet moyen de la campagne sur les villes traitées (l'ATT) est $\mathbb E[Y_{it}(1)-Y_{it}(0)\mid T_i=1]$ après le lancement. Le terme $\mathbb E[Y_{it}(0)\mid T_i=1]$ après le lancement est inobservable (ce qui se serait passé sans campagne). La DiD l'approche en supposant que, **sans campagne**, la variation moyenne des villes traitées aurait été **la même** que celle des villes témoins :
> $$\underbrace{\mathbb E[Y_{\text{après}}(0)-Y_{\text{avant}}(0)\mid T=1]}_{\text{inobservable}}=\underbrace{\mathbb E[Y_{\text{après}}(0)-Y_{\text{avant}}(0)\mid T=0]}_{\text{observable}}.$$
> C'est l'hypothèse des **tendances parallèles**. Sous cette hypothèse, et si la campagne n'a pas d'effet **avant** son lancement (pas d'anticipation), $\widehat{\text{DiD}}$ estime l'ATT. Remarquez ce que l'on **n'** a **pas** besoin de supposer : que les villes traitées et témoins aient le même niveau (elles ne l'ont pas), ni que l'on observe tout ce qui les distingue.

### 7.3.2 À quelle échelle les tendances sont-elles parallèles ?

Regardons les données avant de régresser. Voici le nombre moyen de commandes par ville et par mois dans chaque groupe, en niveau (à gauche) et en échelle logarithmique (à droite).


![Commandes moyennes par ville et par mois, villes traitées (orange) et témoins (bleu), en niveau à gauche et en échelle logarithmique à droite. La ligne pointillée marque le lancement de la campagne.](figures/ch07-did-tendances.png)

Avant le lancement, les deux courbes suivent **la même saisonnalité** (creux en janvier, pic en décembre), mais avec des niveaux différents : les villes traitées sont plus grandes. Les chiffres mensuels sont bruités (ce sont des comptages), si bien que l'effet de la campagne ne saute pas aux yeux sur le graphique : il faut le **mesurer**, ce que font les sections suivantes.

Avant de commenter, mesurons deux façons de comparer les groupes **avant** le lancement : par leur **écart** de niveau (traitées moins témoins) et par leur **rapport** (traitées divisées par témoins).


La sortie répond. Avant le lancement, l'**écart** de niveau entre les deux groupes varie beaucoup d'un mois à l'autre (de 5,7 à 24,5 commandes, soit une variabilité relative de 30 %) : il se creuse aux mois d'affluence et se resserre aux mois creux. Leur **rapport**, lui, reste bien plus stable (de 1,25 à 1,77, variabilité relative de 9 %) : les villes traitées commandent environ une fois et demie plus que les témoins, en toute saison.

Voilà un point crucial : l'hypothèse des tendances parallèles **dépend de l'échelle**. Si l'effet de la saison est **multiplicatif** (proportionnel à la taille de la ville : un mois de décembre gonfle les commandes de toutes les villes dans la même **proportion**), alors une grande ville gagne en niveau absolu plus qu'une petite à chaque pic, et les courbes **ne sont pas parallèles en niveau** ; elles le sont **en logarithme**, où un effet multiplicatif devient additif. C'est le cas ici (et pour la plupart des chiffres d'affaires, dont les variations se pensent en pourcentage). Recalculons donc la DiD **en logarithme**, ce qui revient à estimer un effet **relatif**. La moyenne du logarithme des commandes passe de 3,369 à 3,537 dans les villes témoins ($+0{,}168$) et de 3,784 à 4,089 dans les villes traitées ($+0{,}305$) : la DiD vaut $0{,}305-0{,}168=0{,}137$ (0,138 sans les arrondis intermédiaires), soit un effet relatif de $e^{0{,}138}-1=+14{,}8\,\%$.


La campagne est associée à une hausse relative de 14,8 % des commandes dans les villes traitées. L'estimation en niveau (10,6 commandes par mois, soit environ 23 % des 46,9 commandes d'avant) et celle en pourcentage ne racontent pas tout à fait la même histoire : **la seconde est plus fiable**, parce que l'hypothèse de tendances parallèles est plus plausible à cette échelle (voir le diagnostic ci-dessus).

### 7.3.3 La régression à effets fixes (TWFE)

Le calcul des moyennes ne fournit pas d'erreur-type et ne permet pas d'ajouter des covariables. On le généralise avec une **régression à deux effets fixes** (*two-way fixed effects*, TWFE) : une constante par ville (qui absorbe le niveau de chaque ville), une constante par mois (qui absorbe la saison et la tendance commune), et une variable `campagne` qui vaut 1 uniquement pour une ville traitée après le lancement :

$$\log Y_{it}=\alpha_i+\gamma_t+\tau\,D_{it}+\varepsilon_{it},\qquad D_{it}=\mathbb 1\{i\text{ traitée et }t\ge 18\}.$$

Le coefficient $\tau$ est l'effet relatif de la campagne. Deux précisions importantes sur l'inférence : les erreurs d'une même ville sont **corrélées dans le temps** (une ville qui commande plus que prévu en janvier a tendance à le faire en février), donc on calcule des erreurs-types **groupées par ville** (*cluster-robust*) ; sans cela, on sous-estime fortement l'incertitude.

On estime ce modèle par une seule ligne de régression (ici sur le logarithme des commandes) :


```python
p["camp"] = ((p["groupe_traite"] == 1) & (p["t"] >= 18)).astype(int)     # 1 si ville traitée et après le lancement
mod = smf.ols("np.log(commandes) ~ camp + C(ville) + C(t)", p).fit(
    cov_type="cluster", cov_kwds={"groups": p["vid"]})                    # erreurs-types groupées par ville
print(f"effet = {mod.params['camp']:.3f}   erreur-type groupée = {mod.bse['camp']:.3f}")
```
<!--sortie-->
```text
effet = 0.138   erreur-type groupée = 0.032
```

L'effet vaut 0,138 (intervalle de confiance à 95 % : de 0,076 à 0,200), soit +14,8 %. Ce coefficient coïncide avec la DiD calculée à la main : **dans ce cas simple** (une seule date de lancement, panel complet), la régression à effets fixes redonne exactement la différence de différences des moyennes. Le modèle de **Poisson** (chapitre 2, section 2.3), qui traite les commandes comme un comptage plutôt que de passer au logarithme, donne un résultat voisin (0,131 avec une erreur-type de 0,028, soit +14,0 %) ; c'est même préférable quand certains comptages sont proches de zéro (le logarithme de 0 n'existe pas), ce qui n'est pas le cas ici.

> ⚠️ **Le nombre de groupes.** Nous n'avons que **20 villes** : les erreurs-types groupées reposent sur un raisonnement asymptotique (beaucoup de groupes) qui est approximatif quand il y en a si peu. Avec moins d'une trentaine de groupes, ou peu de groupes traités (ici 8), l'intervalle de confiance risque d'être trop optimiste ; des méthodes plus robustes (bootstrap par groupes, tests de permutation, section 3.7 du volume I) existent. Gardez en tête que l'intervalle ci-dessus est un ordre de grandeur, pas une certitude à la décimale.

### 7.3.4 L'étude d'événement : regarder les tendances avant et après

L'hypothèse des tendances parallèles porte sur l'**inobservable** (ce qui aurait eu lieu sans la campagne), donc elle ne se teste pas directement. Mais on peut examiner ses **implications observables** : si les villes traitées et témoins évoluaient de façon parallèle *avant* le lancement, un modèle qui laisse l'effet varier mois par mois devrait trouver des coefficients **proches de zéro avant** la campagne. C'est l'**étude d'événement** (*event study*) : on remplace l'unique variable `campagne` par un coefficient pour chaque mois relatif au lancement, en prenant le mois précédant le lancement (`-1`) comme référence.


![Étude d'événement : coefficients mois par mois (avec intervalle de confiance à 95 %). Avant le lancement, ils fluctuent autour de zéro ; après, ils se situent autour de la vérité.](figures/ch07-did-evenement.png)

Avant le lancement, les coefficients fluctuent autour de zéro (moyenne +0,05, et **aucun** des 17 intervalles de confiance n'exclut zéro) : **pas de tendance différentielle visible** entre les deux groupes. Après le lancement, ils se situent autour de 0,19 en moyenne (la vérité est 0,15), nettement plus haut. Les intervalles sont larges : chaque mois pris isolément est peu informatif ; c'est la **configuration d'ensemble** qui compte. Ce graphique est **le diagnostic standard** d'une DiD, et il devrait figurer dans toute analyse de ce type. Il ne **prouve** pas l'hypothèse (rien ne garantit que les tendances n'auraient pas divergé *après* le lancement pour une autre raison), mais il rend très difficile de croire à une explication par une tendance préexistante.

### 7.3.5 Quand les tendances ne sont pas parallèles

Que se passe-t-il quand l'hypothèse est **fausse** ? Ajoutons un défaut : les grandes villes, déjà plus dynamiques, ont une croissance propre un peu plus rapide que les autres (+1 % par mois, hors campagne). Elles auraient donc davantage progressé de toute façon, et la DiD va attribuer cet écart à la campagne. Le simulateur a un paramètre pour cela.


![Études d'événement comparées : à gauche les tendances sont parallèles (coefficients proches de zéro avant le lancement) ; à droite, les villes traitées croissaient plus vite, et les coefficients montent déjà avant le lancement.](figures/ch07-did-violation.png)

Le résultat est trompeur : l'estimation de l'effet (0,315) est à peu près le **double** de la vérité (0,15), avec une erreur-type (0,031) identique à celle du cas sans défaut : l'intervalle de confiance **exclut la vérité**, et rien dans ce seul chiffre ne l'indique. Mais l'étude d'événement le **révèle** : dans le graphique de droite, les coefficients ont une **pente ascendante** dès avant le lancement (ils passent d'environ −0,1 en début de période à environ +0,1 juste avant), et 2 des 17 intervalles d'avant le lancement excluent déjà zéro. C'est pourquoi on la regarde toujours.

Un second diagnostic complète l'étude d'événement : le **test placebo**. On refait l'analyse **sur la seule période d'avant** en prétendant que la campagne a commencé plus tôt (disons au mois 9). Comme il ne s'est rien passé, l'effet « placebo » devrait être proche de zéro.


Quand les tendances sont parallèles, l'effet placebo (−0,062) n'est pas distinguable de zéro (rapport à son erreur-type de −1,6, inférieur à 2 en valeur absolue). Quand elles ne le sont pas, l'effet placebo (+0,097) est environ 2,3 fois son erreur-type : le placebo **donne l'alerte**. Notez qu'avec un seul test et un seuil à 2, l'alerte reste un indice, pas une preuve : le placebo du cas parallèle atteint déjà −1,6.

> ⚠️ **Que faire si les tendances ne sont pas parallèles ?** Plusieurs remèdes existent, tous avec un prix. (1) **Ajouter une tendance linéaire propre à chaque groupe** : on peut le faire en ajoutant `groupe_traite:t` dans la régression (essayons ci-dessous). Mais cela suppose que la tendance différentielle est *linéaire* et qu'on peut l'extrapoler après le lancement. (2) **Choisir de meilleurs témoins** : des villes comparables par la taille et la dynamique, ou un **contrôle synthétique** qui construit un témoin sur mesure à partir d'une combinaison pondérée de villes. (3) **Changer de question ou de méthode**. Aucun remède n'est automatique ; ils reposent tous sur d'autres hypothèses.


La tendance de groupe ramène l'estimation de 0,315 à 0,185, c'est-à-dire dans l'incertitude statistique de la vérité (0,150 ; l'écart est de 0,035, soit environ la moitié de l'erreur-type), mais au prix d'une **perte de précision** : l'erreur-type double (0,063 au lieu de 0,031). Et sur les données initiales, où cette tendance n'était pas nécessaire, elle ne fait que gonfler l'erreur-type (0,062 au lieu de 0,032) et déplacer l'estimation (0,181 au lieu de 0,138). C'est le compromis typique entre robustesse et précision.

### 7.3.6 Ce que la DiD ne règle pas

- **Les effets de débordement (SUTVA).** Si la campagne dans une grande ville fait aussi venir des clients de sa banlieue (une ville « témoin »), les témoins sont contaminés et l'effet est sous-estimé. Il faut choisir des témoins suffisamment éloignés ou modéliser le débordement.
- **L'anticipation.** Si les clients retardent leurs achats à l'annonce de la campagne, les mois d'avant sont déjà « traités ». L'étude d'événement le montre.
- **Un choc simultané.** Si, à la même date, un événement touche *seulement* les villes traitées (un concurrent s'installe dans l'une des villes traitées), la DiD l'attribue à la campagne.
- **Les lancements échelonnés.** Si les villes sont traitées à des dates différentes, la régression TWFE ci-dessus peut donner un résultat **trompeur** : elle utilise parfois des villes *déjà traitées* comme témoins de villes traitées plus tard, ce qui fausse la comparaison quand l'effet varie dans le temps. Des estimateurs modernes (Callaway et Sant'Anna, Sun et Abraham, entre autres) corrigent ce problème. Nous ne les présentons pas ici (nous n'avons qu'une seule date de lancement) et **ne les avons pas exécutés** ; si votre situation est échelonnée, il faut les étudier avant de se fier à une régression TWFE simple.
- **Le choix des témoins.** Ici, huit grandes villes ont été choisies pour la campagne *parce qu'elles étaient grandes* : cela ne gêne pas la DiD tant que la croissance n'est pas liée à la taille. Mais si la gérante avait choisi les villes *parce qu'elles étaient en croissance*, l'hypothèse serait fausse.

**La vérité, révélée.** Dans la simulation, la campagne multiplie les commandes par $e^{0{,}15}=1{,}162$, soit +16,2 %. L'estimation par DiD en logarithme est de 0,138 (erreur-type 0,032), soit +14,8 % : proche de la vérité, avec un intervalle de confiance qui la contient. L'estimation avant/après seule (+16,1 commandes, soit +34 % des 46,9 commandes d'avant) et la comparaison traités contre témoins seule (63,0 contre 36,1 commandes, soit +75 %) auraient donné, en termes relatifs, des valeurs respectivement **un peu plus de deux fois** et **plus de quatre fois** trop élevées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.8, exercices 7.7 et 7.8.

> ✅ **À retenir (7.3).** La différence de différences compare **l'évolution** des traités à celle des témoins : elle élimine les différences **de niveau** stables et les chocs **communs**. Elle repose sur l'hypothèse invérifiable de **tendances parallèles** (à la bonne échelle) : on la défend avec un **graphique**, une **étude d'événement** et des **tests placebo**. Les erreurs-types doivent être **groupées**, et les lancements échelonnés exigent des méthodes spécifiques.


## 7.4 Variables instrumentales : un coup de pouce aléatoire

> 💡 **Intuition.** Les méthodes de 7.2 et 7.3 exigent de **mesurer** les facteurs de confusion (ou de les supposer stables dans le temps). Mais le facteur de confusion le plus redoutable est celui que l'on **ne peut pas** mesurer : la passion d'un client pour l'artisanat, son goût, sa motivation. Une **variable instrumentale** est un levier extérieur qui pousse le traitement dans un sens, **sans** passer par la voie cachée. Si un tirage au sort fait suivre le compte à quelques clients de plus, la différence de dépense qui en résulte ne peut pas venir de leur passion : le hasard ne la connaît pas.

### 7.4.1 Le problème : suivre le compte, cause ou symptôme ?

La gérante remarque que les clients qui **suivent** le compte de la boutique sur les réseaux sociaux dépensent plus. Faut-il investir pour augmenter le nombre d'abonnés ? Tout dépend du sens de la causalité : est-ce que **suivre** fait dépenser (par les publications, les promotions, le sentiment d'appartenance) ? Ou est-ce que les clients **passionnés** à la fois suivent le compte et dépensent beaucoup, sans que l'un cause l'autre ?

Le fichier `ch07-iv.csv` contient 5 000 clients : leur âge, la dépense annuelle, le fait de suivre le compte (`suit_compte`, choix libre), et une variable particulière, `rappel` : un e-mail invitant à suivre le compte a été envoyé à **la moitié des clients tirée au hasard**. Les données sont simulées (`build/sim_ch07.py`, fonction `iv`) ; la vérité (l'effet réel de suivre le compte) ne sera révélée qu'à la fin de la section. Dans ces données, 62,3 % des clients suivent le compte et 48,8 % ont reçu le rappel ; ceux qui suivent le compte dépensent en moyenne 109,8 €, les autres 68,7 €.


La comparaison naïve est à l'œuvre : ceux qui suivent le compte dépensent bien plus. Un modèle de régression qui ajuste sur l'âge (la seule covariable observée) n'y change presque rien : il estime l'effet de suivre le compte à 41,9 € (erreur-type 1,4 € ; intervalle de confiance à 95 % de 39,1 à 44,7 €).


Rien dans ce modèle n'avertit que le chiffre est faux : l'erreur-type est petite, l'intervalle étroit. Mais il suppose que les clients qui suivent le compte et ceux qui ne le suivent pas **ne diffèrent que par l'âge**, ce que l'on a de bonnes raisons de contester. Un facteur non mesuré, la passion, pousse à la fois à suivre et à dépenser : c'est la fourche de 7.1.5, avec une cause commune que **personne ne peut ajuster**.


![Le schéma d'une variable instrumentale : l'instrument Z (rappel tiré au hasard) agit sur le traitement T, qui agit sur Y ; une cause cachée U agit à la fois sur T et sur Y. Il n'existe aucune flèche directe de Z vers Y, ni de U vers Z.](figures/ch07-iv-schema.png)

### 7.4.2 Les conditions d'un bon instrument

Le schéma résume la structure. Un **instrument** $Z$ pour estimer l'effet de $T$ sur $Y$ doit satisfaire trois conditions :

1. **Pertinence** : $Z$ influence $T$. (Le rappel fait réellement suivre le compte à davantage de clients.) Cette condition **se vérifie** sur les données.
2. **Indépendance** : $Z$ est indépendante des facteurs cachés $U$ (« comme tiré au sort »). Ici, c'est vrai **par construction** : nous avons tiré le rappel au hasard. Quand $Z$ n'est pas randomisé, c'est une hypothèse à défendre.
3. **Exclusion** : $Z$ n'affecte $Y$ **que par** $T$ (aucune flèche directe de $Z$ vers $Y$). Ici : le rappel ne fait dépenser que parce qu'il fait suivre le compte. Cette condition **ne se vérifie pas** sur les données : c'est un argument de métier. Nous verrons ce qui arrive quand elle est fausse.

Vérifions les deux premières. L'indépendance, d'abord : le tirage au sort doit équilibrer les covariables observées, et c'est le cas (âge moyen de 36,5 ans avec rappel contre 36,4 sans).


La pertinence, ensuite : c'est la **première étape**, la régression du traitement sur l'instrument. On y regarde non seulement le coefficient, mais la **statistique $F$**, qui mesure la force de l'instrument (nous verrons pourquoi en 7.4.6). Ici, 44,1 % des clients sans rappel suivent le compte contre 81,3 % avec rappel, soit un écart de 0,372 (erreur-type 0,013) et une statistique $F$ de 874.


Le rappel augmente de façon massive la probabilité de suivre le compte : l'instrument est **très pertinent** (une statistique $F$ de plusieurs centaines, à comparer au seuil conventionnel de 10).

### 7.4.3 L'estimateur de Wald : un rapport de deux différences

L'idée est simple. Le rappel est tiré au sort : la comparaison **avec rappel contre sans rappel** est donc une comparaison propre, comme dans une expérience (7.1.4). Elle donne deux différences :

- l'effet du rappel sur le traitement (**première étape**) : $\ \pi=\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]$ ;
- l'effet du rappel sur le résultat (**forme réduite**, ou *intention de traiter*) : $\ \rho=\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]$.

Si le rappel n'agit sur la dépense **que** par le suivi du compte, alors $\rho$ est l'effet de suivre multiplié par la proportion de clients que le rappel a fait suivre : $\rho=\beta\times\pi$. D'où l'estimateur de Wald :

$$\hat\beta_{\text{Wald}}=\frac{\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]}{\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]}=\frac{\rho}{\pi}.$$

> 📐 **Une démonstration en trois lignes.** Écrivons le modèle structurel $Y=a+\beta T+\gamma U+\varepsilon$, où $U$ est le facteur caché. L'indépendance et l'exclusion donnent $\operatorname{Cov}(Z,U)=0$ et $\operatorname{Cov}(Z,\varepsilon)=0$. Donc
> $$\operatorname{Cov}(Z,Y)=\beta\operatorname{Cov}(Z,T)+\gamma\underbrace{\operatorname{Cov}(Z,U)}_{=0}+\underbrace{\operatorname{Cov}(Z,\varepsilon)}_{=0}=\beta\operatorname{Cov}(Z,T),\qquad\text{soit}\qquad \beta=\frac{\operatorname{Cov}(Z,Y)}{\operatorname{Cov}(Z,T)}.$$
> Quand $Z$ est binaire, cette covariance se simplifie en la différence des moyennes selon $Z$, d'où le rapport $\rho/\pi$. Le facteur caché **disparaît** du calcul : c'est tout l'intérêt de l'instrument. (Il faut en revanche que $\operatorname{Cov}(Z,T)\ne0$, d'où la condition de pertinence.)

Les deux différences se lisent directement dans les moyennes :


À la main : avec le rappel, 81 % des clients suivent le compte contre 44 % sans, soit $\pi\approx0{,}37$ ; la dépense moyenne augmente de $\rho\approx8{,}8$ €. Le rapport donne un effet de suivre le compte d'environ $8{,}8/0{,}372\approx23{,}7$ €, **très inférieur** aux 41,9 € du modèle naïf : une grande partie de l'écart de dépense entre abonnés et non-abonnés venait de la passion, pas du suivi lui-même.

### 7.4.4 Les moindres carrés en deux étapes (2SLS)

L'estimateur de Wald se généralise à plusieurs covariables et plusieurs instruments avec les **moindres carrés en deux étapes** :

1. **Première étape** : régresser le traitement $T$ sur l'instrument $Z$ et les covariables $W$ (ici l'âge) ; en déduire la **partie de $T$ expliquée par l'instrument**, $\hat T$ ;
2. **Seconde étape** : régresser $Y$ sur $\hat T$ et $W$.

Comme $\hat T$ ne contient que la variation de $T$ **causée par l'instrument** (donc indépendante de $U$), le coefficient de $\hat T$ est l'effet recherché. On peut l'écrire **à la main**, avec la formule matricielle $\hat\beta=(X^\top P_ZX)^{-1}X^\top P_Zy$ où $P_Z=Z(Z^\top Z)^{-1}Z^\top$ est le projecteur sur les instruments.


Les trois écritures (deux régressions successives, formule matricielle, estimateur $(Z^\top X)^{-1}Z^\top y$) coïncident exactement : l'effet du suivi vaut 23,84 €, très proche de l'estimateur de Wald (23,7 €). **Attention** aux erreurs-types : si l'on lit simplement la sortie d'une régression de $Y$ sur $\hat T$, on obtient des erreurs-types **fausses**, parce que les résidus qu'elle calcule utilisent $\hat T$ au lieu du vrai traitement $T$. La bonne variance utilise les résidus $y-X\hat\beta$ calculés avec les **vrais** régresseurs :

$$\widehat{\operatorname{Var}}(\hat\beta)=\hat\sigma^2\,(X^\top P_ZX)^{-1},\qquad \hat\sigma^2=\frac{\|y-X\hat\beta\|^2}{n-k}.$$

La bibliothèque `statsmodels` fait tout cela en une ligne, avec les bonnes erreurs-types :


```python
from statsmodels.sandbox.regression.gmm import IV2SLS

res = IV2SLS(y, X, Z).fit()      # y : dépense ; X : constante, suivi, âge ; Z : constante, rappel, âge
print(f"effet du suivi = {res.params[1]:.2f} €   erreur-type = {res.bse[1]:.2f}")
```
<!--sortie-->
```text
effet du suivi = 23.84 €   erreur-type = 3.80
```


Elle redonne exactement notre calcul à la main (intervalle de confiance à 95 % : de 16,4 à 31,3 €). L'erreur-type « naïve » de la seconde régression (4,03) est ici un peu plus grande que la correcte ; dans d'autres situations elle peut être trop petite : elle n'a **aucune garantie**, il ne faut jamais la lire. Le prix de la robustesse à la confusion cachée se paie en **précision** : l'erreur-type de l'estimateur par variable instrumentale (3,8 €) est presque trois fois celle des moindres carrés ordinaires (1,4 €), parce qu'on n'utilise qu'une partie de la variation de $T$ (celle que le rappel déclenche).

> ✅ **À retenir (7.4.1 à 7.4.4).** Une variable instrumentale permet d'estimer un effet causal malgré un facteur de confusion **non observé**, à trois conditions : pertinence (vérifiable), indépendance (garantie si l'instrument est randomisé) et exclusion (invérifiable). Avec un seul instrument, l'estimateur est le **rapport de Wald** $\rho/\pi$ ; en général, c'est le 2SLS, avec des erreurs-types calculées sur les vrais régresseurs. La précision est plus faible que celle des MCO.

### 7.4.5 Ce que l'on estime vraiment : l'effet pour les « complaisants »

Un point subtil, mais essentiel pour interpréter le résultat. Un instrument ne fait changer de comportement que **certains** clients : ceux que le rappel **décide** à suivre le compte. Imaginons trois types de clients :

- les **toujours-abonnés** (*always-takers*) suivraient le compte avec ou sans rappel ;
- les **jamais-abonnés** (*never-takers*) ne le suivraient dans aucun cas ;
- les **complaisants** (*compliers*) suivent le compte **si et seulement si** ils reçoivent le rappel.

(Nous supposons qu'il n'existe pas de « contrariants » qui feraient l'inverse du rappel : c'est l'hypothèse de **monotonie**.) Les toujours-abonnés et les jamais-abonnés ne réagissent pas au rappel : ils ne contribuent donc **pas** à la différence $\rho$. Seuls les complaisants y contribuent. L'estimateur de Wald estime par conséquent l'effet moyen **parmi les complaisants** (le *LATE*, pour *local average treatment effect*), et pas l'effet moyen sur tous les clients.


Le rappel convainc 38 % des clients (les complaisants) ; 43 % suivaient déjà le compte et 18 % ne le suivront jamais. L'estimateur de Wald (21,75 €) tombe sur le **LATE** (21,64 €) et **non** sur l'ATE (24,99 €) : les deux diffèrent dès que l'effet varie d'un client à l'autre. Ici, les passionnés profitent davantage du suivi, mais ce sont aussi eux qui suivent le compte **sans** qu'on le leur demande (passion moyenne de +0,40 chez les toujours-abonnés), donc l'instrument n'apprend rien sur eux ; les complaisants (−0,17) sont des clients de passion intermédiaire, un peu en dessous de la moyenne, d'où un effet moyen un peu plus faible.

> ⚠️ **Conséquence pratique.** Le LATE est l'effet pour les clients **sur lesquels le levier agit**. Si la gérante veut savoir ce que rapporterait une campagne d'invitation **comme celle du rappel**, c'est exactement la bonne quantité. Si elle veut l'effet de suivre le compte pour *tous* ses clients, ce n'est pas garanti. Un instrument différent aurait d'autres complaisants, donc un autre LATE.

### 7.4.6 Quand l'instrument est faible

Que se passe-t-il quand l'instrument ne pousse presque personne à changer de comportement ? Le dénominateur de Wald, $\pi$, devient très petit, et le rapport $\rho/\pi$ explose à la moindre fluctuation. Dans notre fichier, le rappel faisait passer la part d'abonnés de 44 % à 81 %. Refaisons l'analyse avec un rappel **beaucoup moins efficace** (le simulateur a un paramètre qui règle la force de l'instrument) sur 5 000 clients :


L'estimation ponctuelle (14,9 €) reste de l'ordre de grandeur de la vérité, mais l'intervalle de confiance est devenu **énorme** : de −51 à +81 €, il est compatible avec un effet fortement négatif comme avec un effet très élevé. Comme les données sont simulées, on peut aller plus loin : **répéter** l'expérience 500 fois avec de nouvelles données, et regarder la distribution de l'estimateur pour trois forces d'instrument. On compte aussi la fréquence à laquelle l'intervalle de confiance à 95 % **contient** vraiment la vérité (25 €).


![Distribution de l'estimateur IV sur 500 répétitions, pour un instrument fort, moyen et faible. La ligne verte marque la vraie valeur (25 €). Plus l'instrument est faible, plus la distribution est étalée et plus elle comporte de valeurs aberrantes.](figures/ch07-iv-faible.png)

**Lecture.** Avec l'instrument **fort** (F médian de 937), les estimations se concentrent autour de la vérité : médiane de 25,1 €, et 90 % des estimations entre 19,3 et 31,1. Avec l'instrument **moyen** (F médian de 14,7, au-dessus du seuil habituel de 10), la médiane reste bonne (25,5 €) mais la dispersion est déjà considérable : 90 % des estimations tombent entre −24,7 et +67,5 €, soit une fourchette de plus de 90 €, et plus d'une fois sur vingt l'estimation a le **mauvais signe**. Avec l'instrument **faible** (F médian de 3,0), c'est pire : 90 % des estimations sont entre −185 et +159 €. Les histogrammes (tronqués) montrent les **queues lourdes** typiques de ce rapport dont le dénominateur peut être proche de zéro.

Le résultat sur la couverture est plus nuancé qu'on ne le dit parfois : les intervalles de confiance à 95 % contiennent bien la vérité (97 %, 98 % et 99 % des cas). Ils sont donc **valides**, mais parce qu'ils sont devenus **immenses** : un intervalle de −185 à +159 € contient la vérité... et presque tout le reste. L'instrument faible ne produit pas ici des conclusions fausses mais confiantes ; il produit des conclusions **inutilisables**. (Des distorsions plus sournoises existent dans la littérature, notamment avec plusieurs instruments faibles ou une forte confusion ; notre simulation, à un seul instrument, ne les fait pas apparaître, et il ne faut pas en conclure que la faiblesse est sans danger.)

> ⚠️ **La règle du « F > 10 ».** Une règle empirique courante dit qu'un instrument est « assez fort » quand la statistique $F$ de la première étape dépasse 10. C'est une règle **approximative**, plutôt optimiste (de nombreux auteurs recommandent des seuils plus élevés quand on veut des intervalles de confiance fiables), et elle ne remplace pas le jugement : regardez l'ordre de grandeur du $F$ et la largeur des intervalles. Quand l'instrument est faible, des méthodes d'inférence robustes existent (test d'Anderson-Rubin) ; nous ne les détaillons pas ici.

### 7.4.7 Quand l'exclusion est fausse

La dernière condition, l'exclusion, est la plus fragile : elle ne se teste pas. Voyons ce que coûte sa violation. Supposons que le rappel ne se contente pas d'inviter à suivre le compte, mais contienne aussi un **bon de réduction** qui fait dépenser **directement** 15 € de plus, qu'on suive le compte ou non. Cette flèche de $Z$ vers $Y$ ne passe pas par $T$.


Le résultat (64,2 € au lieu de 25) est faux de **près de 40 euros**, soit presque exactement le biais théorique de 40,3 €, avec une erreur-type aussi petite qu'avant (3,8) : l'instrument violé fournit une estimation précise, mais de la mauvaise quantité. Le biais vaut $\gamma_Z/\pi$, où $\gamma_Z$ est l'effet direct du rappel et $\pi$ la force de la première étape : même une petite violation de l'exclusion est **amplifiée** par un instrument faible (division par un $\pi$ petit). Rien dans les données ne signale le problème (avec un seul instrument, l'hypothèse n'est pas testable). Avec **plusieurs** instruments, on peut tester leur cohérence mutuelle (test de suridentification, de Sargan ou de Hansen), mais ce test ne détecte pas les cas où *tous* les instruments sont invalides de la même manière.

> ⚠️ **Où trouve-t-on de bons instruments ?** C'est la vraie difficulté. Les cas les plus convaincants sont les **tirages au sort** (comme le rappel ici, ou une loterie administrative) et les **expériences naturelles** (une règle administrative, une distance, un événement météorologique). Les instruments « de bureau », choisis parce qu'ils sont corrélés au traitement et qu'on a un bon argument pour l'exclusion, sont fréquemment contestés. Face à tout instrument, la question à se poser est : « existe-t-il un chemin, même improbable, par lequel il affecterait directement le résultat ? »

### 7.4.8 Quelle méthode, quand ? Panorama et limites

Nous avons vu quatre façons de passer de l'association à la causalité. Chacune échange une hypothèse contre une autre :

| Situation | Méthode | Hypothèse-clé (invérifiable) | Ce qui la fragilise | Voir |
|---|---|---|---|---|
| On peut tirer au sort | **Expérience randomisée** | l'attribution est aléatoire et respectée | non-respect du protocole, attrition, débordements | 7.1.4 |
| Tout ce qui guide le choix est mesuré | **Ajustement, scores de propension** | ignorabilité conditionnelle + chevauchement | un facteur de confusion non mesuré ou mal mesuré | 7.1.9, 7.2 |
| Données avant/après avec des témoins | **Différences de différences** | tendances parallèles (à la bonne échelle) | tendances divergentes, chocs simultanés, lancements échelonnés | 7.3 |
| Un levier extérieur pousse le traitement | **Variable instrumentale** | exclusion + indépendance de l'instrument | effet direct de l'instrument, instrument faible | 7.4 |

On mentionnera aussi, sans les développer ici, la **régression sur discontinuité** (un seuil arbitraire décide du traitement, par exemple une réduction à partir de 100 € d'achat) et les **contrôles synthétiques** (un témoin construit sur mesure pour une seule unité traitée) : ce sont des cousins de la DiD et de l'IV, avec leurs propres hypothèses.

**Les limites, dites franchement.**

- **Aucune de ces méthodes ne se vérifie complètement.** Elles traduisent toutes des hypothèses sur le monde (ignorabilité, tendances parallèles, exclusion) en un estimateur. Les diagnostics (équilibre, étude d'événement, force de l'instrument) *réfutent parfois* l'hypothèse, jamais ne la *prouvent*.
- **Ce chapitre était artificiellement simple.** Nous avons simulé les données, donc nous *connaissions* la vérité et la structure. Dans la réalité, le graphe est incertain, les covariables sont imparfaitement mesurées, les effets varient d'un individu à l'autre, et les données sont tronquées ou manquantes.
- **Chaque méthode répond à une question légèrement différente** : ATE, ATT, effet pour les complaisants. Ces effets ne sont pas interchangeables, et il faut dire lequel on estime.
- **La convergence de plusieurs approches rassure.** Si une expérience, une DiD et une analyse par score de propension, qui reposent sur des hypothèses *différentes*, donnent le même ordre de grandeur, la conclusion est beaucoup plus solide. C'est la **triangulation**.
- **Le vocabulaire compte.** Écrire « l'offre *augmente* la dépense » sans préciser l'hypothèse revient à affirmer plus que ce que l'analyse justifie. Préférez « *sous l'hypothèse que…*, l'effet estimé est de… ». La recommandation honnête à un décideur est : « voici l'effet estimé, voici l'hypothèse sur laquelle il repose, et voici ce qui la rendrait fausse ».

**La vérité, révélée.** Dans la simulation, l'effet réel de suivre le compte est de **25 €**. L'estimation par MCO donnait 42 € (la passion, non observée, gonflait la comparaison). L'estimateur de Wald et le 2SLS donnent 23,8 € avec l'instrument fort (23,7 pour Wald, 23,8 pour le 2SLS avec l'âge), très proche de la vérité malgré le facteur de confusion caché, mais avec une erreur-type de 3,8 € contre 1,4 pour les MCO : la protection contre le biais se paie en précision. Si l'on se limite aux clients « complaisants », la vraie cible serait légèrement différente (21,6 € dans notre mini-simulation avec effets variables) : l'instrument répond à une question un peu plus étroite.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.9, exercices 7.9, 7.10 et 7.12.

> ✅ **À retenir (7.4).** Une variable instrumentale contourne la confusion **non observée** grâce à un levier extérieur (idéalement tiré au sort) qui agit sur le résultat **uniquement** à travers le traitement. L'estimateur est un rapport (Wald / 2SLS) dont la précision dépend de la **force** de l'instrument, et il cible l'effet pour les **complaisants**. L'hypothèse d'exclusion ne se teste pas. Aucune des quatre méthodes du chapitre ne dispense de la question de départ : *comment les données ont-elles été fabriquées ?*


## Bilan du chapitre 7

Vous savez maintenant :

- **formuler** une question causale avec les **résultats potentiels**, distinguer ATE, ATT et ATU, et comprendre pourquoi l'estimation d'un effet est un problème de **données manquantes** (le problème fondamental) ;
- **décomposer** une différence observée en effet causal et **biais de sélection**, et expliquer pourquoi la **randomisation** supprime le second ;
- **analyser une expérience randomisée** : tableau d'équilibre, effet moyen, intervalle de confiance, ajustement pour la précision ;
- **lire un graphe causal** (DAG) : chaîne, fourche, collision ; savoir ce qu'il faut ajuster (les causes communes) et ce qu'il ne faut **pas** ajuster (médiateurs, effets communs) ; énoncer le **critère de la porte dérobée** ;
- **estimer** un effet à partir de données observationnelles avec un **score de propension** (appariement, IPW, estimateur doublement robuste), et **vérifier** le chevauchement et l'équilibre ;
- **mener une différence de différences** : calcul à la main, régression à effets fixes avec erreurs-types groupées, **étude d'événement**, test placebo, et connaître ses pièges (tendances non parallèles, échelle, peu de groupes, lancements échelonnés) ;
- **utiliser une variable instrumentale** : Wald et 2SLS, conditions de validité, interprétation en **effet pour les complaisants**, danger des instruments faibles et de l'exclusion violée ;
- **comparer** ces méthodes et **dire honnêtement** ce qu'aucune d'elles ne peut garantir : toutes remplacent une information absente par une **hypothèse**.

> 💡 **La seule phrase à retenir.** Un résultat causal s'écrit toujours sous la forme : « *si* (hypothèse), *alors* (effet estimé, avec son incertitude) ». Ce chapitre vous a appris à écrire des hypothèses honnêtes, et à les mettre à l'épreuve.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : les applications 7.1 à 7.9 (analyses complètes avec leur code) et les douze exercices corrigés 7.1 à 7.12.
