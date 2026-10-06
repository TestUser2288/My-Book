# Chapitre 6 : ➕ Détection d'anomalies et de fraude

> « Chercher une aiguille dans une botte de foin, sans savoir à quoi ressemble l'aiguille. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui veulent voir comment l'apprentissage automatique s'applique à un problème particulier et très répandu : repérer ce qui sort de l'ordinaire.

Une boutique en ligne reçoit chaque jour des centaines de commandes. La très grande majorité sont normales. Quelques-unes, une sur cent environ, sont frauduleuses : une carte volée, un compte piraté, une adresse de livraison jetable. Chaque fraude coûte le montant de la commande (la boutique rembourse la victime et perd la marchandise) ; chaque vérification manuelle coûte du temps. La gérante ne peut pas regarder toutes les commandes ; elle peut en examiner quelques dizaines par jour. **Lesquelles ?**

C'est le problème de la **détection d'anomalies** : classer les observations de la plus suspecte à la moins suspecte, de façon qu'en regardant les premières, on trouve beaucoup plus de fraudes que par hasard. Il a trois particularités qui le distinguent des problèmes de classification du chapitre 2 :

- **les cas intéressants sont rarissimes** (moins d'une commande sur cent), ce qui change la façon de juger un modèle ;
- **on ne sait pas toujours à quoi ressemble une fraude** : les fraudeurs changent de méthode, et ce que l'on n'a jamais vu ne figure dans aucune étiquette ;
- **l'erreur coûte cher dans les deux sens** : rater une fraude coûte la commande, ratisser trop large coûte du temps de vérification et des clients honnêtes importunés.

## Le chemin de ce chapitre

- **6.1 Le problème et son évaluation** : ce qu'est une anomalie, pourquoi l'apprentissage supervisé ne suffit pas toujours, et surtout comment **mesurer** un détecteur quand 99 % des cas sont normaux (l'exactitude ne veut plus rien dire).
- **6.2 Méthodes statistiques, distances et densités** : le z-score et sa version robuste, la distance de Mahalanobis, les plus proches voisins et le *Local Outlier Factor* (LOF). Les idées les plus anciennes, souvent les plus solides.
- **6.3 La forêt d'isolement** : isoler un point par des coupures aléatoires, et la raison pour laquelle les anomalies s'isolent vite.
- **6.4 Autoencodeurs** : apprendre à reconstruire les données normales, et mesurer l'erreur de reconstruction. Suivi d'une **comparaison honnête** de toutes les méthodes du chapitre.
- **Bilan du chapitre** et renvois vers le cahier d'exercices.

> 📒 **Pour s'entraîner.** Chaque section de ce chapitre se termine par un renvoi vers le chapitre 6 du **cahier d'exercices et d'applications** du volume.

## Les données et le protocole

Nous travaillons sur le fichier `donnees/transactions.csv` : **60 000 commandes en ligne** de la boutique, avec, pour chacune, le montant, l'heure, le canal, le mode de paiement, et quelques indices de comportement.

| Variable | Signification |
|---|---|
| `montant` | montant de la commande, en € |
| `heure`, `jour_semaine` | moment de la commande |
| `appareil_connu` | 1 si l'appareil a déjà servi à commander sur ce compte |
| `distance_facturation_livraison_km` | distance entre l'adresse de facturation et l'adresse de livraison |
| `nb_commandes_24h` | nombre de commandes du compte dans les 24 heures précédentes |
| `age_compte_jours` | ancienneté du compte, en jours |
| `ip_pays_different` | 1 si le pays de l'adresse IP diffère du pays de facturation |
| `delai_depuis_derniere_cmd_h` | heures écoulées depuis la dernière commande du compte |
| `nb_articles`, `mode_paiement`, `canal` | taille de la commande, moyen de paiement, canal |
| `fraude`, `type_fraude` | **l'étiquette** (0/1) et le type de fraude (0 : aucune ; 1 : compte neuf ; 2 : prise de contrôle) |

Les données sont **simulées** (graine fixe) : la boutique et ses clients sont fictifs, et nous connaissons la façon dont les fraudes ont été fabriquées. Le fichier contient **486 fraudes** sur 60 000 commandes, soit **0,81 %**, de deux types :

- **type 1, « compte neuf »** : un compte tout juste créé commande un montant élevé, souvent la nuit, avec une adresse de livraison éloignée de l'adresse de facturation ;
- **type 2, « prise de contrôle »** : un compte ancien est piraté ; le fraudeur commande depuis un appareil inconnu, une adresse IP d'un autre pays, en rafale.

Les fraudes réelles se déguisent : aucun des indices ci-dessus n'est infaillible, et beaucoup de commandes **normales** y ressemblent (un client en voyage, un nouveau compte qui fait un cadeau). C'est volontaire.

> 💡 **Le protocole de tout le chapitre.** Nous mettons de côté 30 % des commandes (18 000, dont 146 fraudes) comme **jeu de test**, qui ne sert qu'à **juger**. Les méthodes **non supervisées** sont ajustées sur les 70 % restants **sans jamais voir l'étiquette** ; elles n'ont donc aucun avantage sur la réalité, où l'on ne connaît pas la fraude à l'avance. Parmi ces 42 000 commandes d'apprentissage, 10 000 forment un **échantillon de référence** (qui sert à ajuster les méthodes de voisinage et les autoencodeurs) et les 32 000 autres un **jeu de validation étiqueté** (246 fraudes), qui sert à **choisir les réglages** (le nombre de voisins, l'architecture d'un réseau…). Choisir un réglage sur le jeu de test le rendrait inutilisable pour juger : c'est la rigueur d'évaluation du chapitre 1 (sections 1.1 et 1.4). Quant aux données d'apprentissage, elles contiennent elles-mêmes des fraudes (0,8 %) : un détecteur non supervisé réel est lui aussi entraîné sur des données « contaminées ».


## 6.1 Le problème et son évaluation

Avant de chercher *comment* détecter les anomalies, il faut s'entendre sur ce que l'on cherche et sur la façon de savoir si l'on a réussi. Cette section est la plus importante du chapitre : elle explique pourquoi les réflexes des chapitres précédents (l'exactitude, une simple séparation apprentissage/test) ne suffisent plus quand 99 % des cas sont normaux.

### 6.1.1 Qu'est-ce qu'une anomalie ?

Une **anomalie** est une observation qui s'écarte tellement de ce qui est habituel qu'elle semble provenir d'un autre mécanisme. On en distingue trois sortes, selon ce qui est étrange :

| Type | Ce qui est étrange | Exemple dans la boutique |
|---|---|---|
| **Anomalie ponctuelle** | l'observation, prise seule | une commande de 2 400 € alors que le panier habituel est de 60 € |
| **Anomalie contextuelle** | l'observation *dans son contexte* | une commande de 80 € à trois heures du matin, passée depuis un compte créé la veille ; la même commande à midi, depuis un compte ancien, est banale |
| **Anomalie collective** | un groupe d'observations, banales une à une | quinze commandes de 20 €, en dix minutes, sur le même compte |

Dans nos données, chaque ligne est une commande, mais plusieurs colonnes résument son contexte (l'ancienneté du compte, le nombre de commandes des dernières 24 heures) : c'est ainsi que l'on transforme une anomalie contextuelle ou collective en une anomalie *ponctuelle dans un espace de bonnes variables*. Choisir ces variables est, ici comme ailleurs, la moitié du travail (chapitre 4).

> ⚠️ **Anomalie n'est pas fraude.** Une anomalie est un fait **statistique** (« c'est rare ») ; une fraude est un fait **métier** (« c'est malhonnête »). Un client fidèle qui offre un cadeau de 900 € est une anomalie qui n'est pas une fraude (fausse alerte) ; un fraudeur prudent qui commande 40 € depuis un vieux compte piraté est une fraude qui n'est pas une anomalie (fraude manquée). Un détecteur d'anomalies ne produit jamais que des **pistes** : c'est la vérification qui tranche.

La figure ci-dessous montre pourquoi le problème est difficile. Les deux types de fraude se distinguent des commandes normales sur plusieurs variables, mais **les distributions se chevauchent largement** : aucune variable ne suffit.


![Distribution du montant, de la distance entre les adresses et de l'ancienneté du compte (échelles logarithmiques) pour les commandes normales (gris) et les deux types de fraude (orange et violet). Les fraudes sont décalées, mais leurs distributions chevauchent celle des commandes normales.](figures/ch06-types-fraude.png)

### 6.1.2 Pourquoi l'apprentissage supervisé ne suffit pas toujours

Si l'on dispose d'étiquettes (« fraude » ou « normale »), pourquoi ne pas simplement entraîner un classifieur, comme au chapitre 2 ? Cela marche, et nous le ferons en 6.1.4 : quand les étiquettes sont abondantes et représentatives, c'est souvent la **meilleure** solution. Mais plusieurs obstacles apparaissent, et ils expliquent l'existence de tout un champ de méthodes non supervisées :

1. **Le déséquilibre extrême.** Sur 60 000 commandes, 486 sont des fraudes : environ **une pour 123**. Le modèle voit très peu d'exemples positifs, et un classifieur qui répond « normale » partout se trompe à peine (6.1.3). Le chapitre 4 (section 4.3) présente les remèdes (pondération, rééchantillonnage).
2. **Le délai des étiquettes.** Une fraude n'est *confirmée* que lorsque la victime conteste le débit, souvent **un à trois mois plus tard**. Les étiquettes décrivent donc le monde d'il y a deux mois : le modèle apprend le passé.
3. **L'adversaire s'adapte.** Les fraudeurs changent de méthode dès qu'ils se font prendre. Un modèle entraîné sur les fraudes d'hier reconnaît les fraudes d'hier.
4. **Les fraudes jamais vues.** Un classifieur ne reconnaît que ce qui ressemble à des exemples étiquetés. Un détecteur d'anomalies, lui, signale *tout ce qui est inhabituel*, y compris un type de fraude inédit.
5. **Les étiquettes sont biaisées.** Seules les commandes **examinées** ou **contestées** reçoivent une étiquette ; les fraudes jamais découvertes figurent dans les données comme « normales » (un biais de sélection, au sens du volume II, section 7.1).

Aucune de ces difficultés n'interdit le supervisé ; mais elles justifient d'avoir **plusieurs outils**, de savoir les comparer, et de les combiner (6.4.5).

### 6.1.3 L'exactitude ne veut plus rien dire

Imaginons un détecteur paresseux qui répond « normale » à chaque commande. Sur notre jeu de test, son **exactitude** (la proportion de réponses justes) est élevée :


L'exactitude du détecteur paresseux est de **99,19 %** : il n'y a rien là d'extraordinaire, c'est simplement la part des commandes normales (1 − 0,0081). Il ne détecte pourtant **aucune** fraude. Une mesure qui donne 99,19 % à un détecteur inutile ne peut pas servir à choisir un détecteur.

Un second piège, plus subtil, concerne la **probabilité qu'une alerte soit juste**. Supposons un détecteur plutôt bon : il repère **80 %** des fraudes (rappel) et ne déclenche une fausse alerte que sur **1 %** des commandes normales (taux de fausses alertes). Sur 100 000 commandes avec une fraude pour 123 commandes (0,8 %), combien d'alertes sont de vraies fraudes ? Par la formule de Bayes (volume I, section 2.1.6), avec $F$ = « la commande est une fraude » et $A$ = « le détecteur déclenche une alerte » :

$$P(F\mid A)=\frac{P(A\mid F)\,P(F)}{P(A\mid F)\,P(F)+P(A\mid \bar F)\,P(\bar F)}=\frac{0{,}80\times0{,}008}{0{,}80\times0{,}008+0{,}01\times0{,}992}=\frac{0{,}0064}{0{,}01632}\approx 0{,}39.$$

**Moins de quatre alertes sur dix sont de vraies fraudes**, alors que le détecteur est excellent sur le papier. La raison est la même que pour les tests médicaux du volume I : quand l'événement est rare, même un faible taux de fausses alertes sur l'immense majorité normale produit beaucoup plus de fausses alertes que de vraies. C'est pourquoi il faut raisonner en **précision** (« parmi les alertes, quelle part est juste ? »), et pas seulement en taux d'erreur.

> 💡 **À retenir pour tout problème rare.** L'exactitude mesure surtout la classe majoritaire. Il faut deux questions complémentaires : *« combien de fraudes trouve-t-on ? »* (le **rappel**) et *« parmi les alertes, combien sont de vraies fraudes ? »* (la **précision**).

### 6.1.4 Un modèle supervisé de référence

Avant de regarder les méthodes non supervisées, fixons un point de comparaison : un **classifieur supervisé** entraîné avec les étiquettes du jeu d'apprentissage. C'est la méthode du chapitre 2 (gradient boosting, section 2.4), avec une **pondération des classes** pour compenser le déséquilibre (section 4.3). Les détails d'un tel modèle sont ceux des chapitres 2 et 4 ; il suffit ici de l'ajuster et de scorer le jeu de test :

```python
from sklearn.ensemble import HistGradientBoostingClassifier

modele = HistGradientBoostingClassifier(class_weight="balanced", max_iter=150, random_state=0)
modele.fit(X_app, y_app)                              # les étiquettes sont utilisées ici
scores_gbm = modele.predict_proba(X_test)[:, 1]       # probabilité estimée de fraude
```


Ce modèle de référence obtient, sur le jeu de test, une aire sous la courbe ROC de **0,971** : un résultat qui semble presque parfait. Nous allons voir que cette mesure est trompeuse (6.1.5), car la réalité est beaucoup plus modeste : au budget de 180 alertes (1 % des commandes), **55 %** des alertes sont de vraies fraudes et **68 %** des fraudes du test sont retrouvées.

### 6.1.5 Les bons outils de mesure

Un détecteur produit un **score** (plus il est élevé, plus la commande est suspecte) ; on déclenche une alerte au-dessus d'un seuil. Pour chaque seuil, on compte quatre nombres : les vraies alertes ($VP$), les fausses alertes ($FP$), les fraudes manquées ($FN$) et les commandes normales laissées passer ($VN$). Sur un exemple à la main, 10 000 commandes dont 80 fraudes, et un détecteur qui déclenche 100 alertes dont 40 justes :

| | Fraude | Normale | Total |
|---|---:|---:|---:|
| **Alerte** | $VP=40$ | $FP=60$ | 100 |
| **Pas d'alerte** | $FN=40$ | $VN=9\,860$ | 9 900 |
| **Total** | 80 | 9 920 | 10 000 |

- **Exactitude** : $(40+9\,860)/10\,000=99{,}0\ \%$ (moins bonne que celle du détecteur paresseux, 99,2 %, pourtant bien plus utile).
- **Précision** : $VP/(VP+FP)=40/100=40\ \%$ : sur dix alertes, quatre sont justes.
- **Rappel** : $VP/(VP+FN)=40/80=50\ \%$ : la moitié des fraudes est retrouvée.
- **Mesure F1** (la moyenne harmonique des deux) : $2\times0{,}4\times0{,}5/(0{,}4+0{,}5)\approx 0{,}44$.

Précision et rappel varient en sens inverse quand on déplace le seuil : abaisser le seuil augmente le rappel (on trouve plus de fraudes) mais diminue la précision (on déclenche plus de fausses alertes). La **courbe précision-rappel** (courbe PR) trace cette tension pour tous les seuils, et son aire est la **précision moyenne** (*average precision*, AP). La courbe **ROC**, vue au chapitre 5 (section 5.1), trace le rappel en fonction du taux de fausses alertes, et son aire est l'AUC.

> ⚠️ **Sur des données déséquilibrées, l'AUC est trop optimiste.** Le taux de fausses alertes se calcule par rapport aux 59 000 commandes normales : même 1 000 fausses alertes ne représentent qu'environ 2 % de ce total, et la courbe ROC reste collée au coin supérieur gauche. La précision, elle, est calculée par rapport aux **alertes** : 1 000 fausses alertes écrasent les quelques centaines de vraies. La courbe PR est donc beaucoup plus sévère, donc plus informative. Un détecteur **aléatoire** a une AUC de 0,5 mais une AP égale à la prévalence (ici 0,008) : l'AP se lit en comparaison de ce plancher.


![Le même détecteur supervisé, vu par la courbe ROC (à gauche) et par la courbe précision-rappel (à droite). L'AUC de 0,971 donne l'impression d'un détecteur presque parfait, alors que la précision chute dès que l'on veut retrouver plus de la moitié des fraudes. Le point orange est le fonctionnement au budget de 180 alertes.](figures/ch06-pr-roc.png)

Le même détecteur obtient une AUC de **0,971** et une AP de **0,646**. Au budget de 180 alertes, on n'a que 99 vraies alertes et 81 fausses : le taux de fausses alertes n'est que de **0,45 %** (ce qui paraît négligeable sur la courbe ROC), alors que **45 % des alertes sont fausses** (ce qui compte pour la gérante). C'est la courbe PR qui dit la vérité opérationnelle.

Trois mesures sont utilisées dans tout le chapitre, avec un détecteur évalué **à budget fixé** :

- l'**AP** (précision moyenne), qui résume toute la courbe PR ;
- la **précision à $k$** : la part de vraies fraudes parmi les $k$ commandes les plus suspectes, où $k$ est le nombre de fraudes du test ;
- le **rappel au budget** : la part des fraudes retrouvées parmi les 180 alertes (1 % des commandes), décomposé par type de fraude.

### 6.1.6 Du score à l'argent

Le budget d'alertes est une contrainte de la gérante, pas une loi de la nature. Le bon nombre d'alertes dépend des **coûts**. Posons des hypothèses simples :

- une fraude non détectée **coûte le montant de la commande** (remboursement et marchandise perdue) ;
- une alerte **coûte 4 €** de vérification (que la commande soit frauduleuse ou non, on doit la regarder) ;
- une fraude détectée est bloquée : elle ne coûte rien de plus que sa vérification.

Si l'on déclenche les $n$ alertes les plus suspectes, le coût total est la somme des montants des fraudes qui passent entre les mailles, plus $4\,n$. On peut tracer ce coût en fonction de $n$ :


![Coût total (fraudes manquées plus vérifications) en fonction du nombre d'alertes examinées, avec le détecteur supervisé. Sans aucune alerte, la boutique perd tout le montant des fraudes. Le coût passe par un minimum, puis remonte quand les vérifications coûtent plus que les fraudes qu'elles retrouvent.](figures/ch06-cout.png)

Sans aucune alerte, les fraudes du jeu de test coûtent **14 404 €**. Avec les 180 alertes du budget, le coût tombe à **5 230 €** ; il est minimal pour **461 alertes** (environ 2,6 % des commandes) à **4 453 €**, soit **69 % de moins** que sans détecteur. Au-delà, chaque alerte supplémentaire coûte plus (4 €) que ce qu'elle rapporte (les fraudes restantes sont de moins en moins probables dans les alertes en queue de liste).

Deux remarques sur cette courbe. Elle dépend entièrement des **hypothèses** (le coût d'une vérification, le coût d'une fraude manquée) : la gérante les connaît mieux que le modélisateur, et il faut les lui demander. Et elle dit où s'arrêter : un seuil se choisit sur le **coût**, pas sur une mesure statistique abstraite (le chapitre 5, section 5.1, revient sur le choix d'un seuil pour un classifieur).

> ✅ **À retenir.**
> - Une anomalie est un fait statistique (« c'est rare ») ; une fraude est un fait métier. Le détecteur produit des **pistes** classées, que l'on vérifie.
> - Le supervisé est souvent le meilleur choix quand les étiquettes sont abondantes ; il souffre du déséquilibre, du délai des étiquettes, de l'adaptation des fraudeurs et des fraudes inédites.
> - **L'exactitude est inutile** (99,19 % pour un détecteur qui ne détecte rien). Il faut la **précision** et le **rappel**, résumés par la courbe PR et l'**AP**, comparée au plancher de la prévalence.
> - La courbe ROC est trop optimiste quand les cas positifs sont rarissimes.
> - Un seuil se choisit en comparant les **coûts** (fraude manquée contre vérification).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.1, exercices 6.1 à 6.4.


## 6.2 Méthodes statistiques, distances et densités

Les méthodes les plus anciennes de détection d'anomalies reposent sur une idée simple : **une observation est suspecte si elle est loin des autres**. Tout l'art consiste à définir « loin ». Cette section présente quatre définitions de plus en plus fines : la distance **à la médiane**, la distance qui **tient compte des corrélations** (Mahalanobis), la distance **aux voisins les plus proches**, et la distance **relative à la densité locale** (LOF). Ces méthodes ne font jamais appel à l'étiquette : elles apprennent ce qu'est une commande « normale » à partir des seules variables.


### 6.2.1 Le z-score, et pourquoi il faut parfois le rendre robuste

Le **z-score** d'une valeur $x$ mesure son écart à la moyenne en nombre d'écarts-types : $z=(x-\bar x)/s$. On juge anormale une valeur dont $|z|$ dépasse 3. Mais la moyenne et l'écart-type sont eux-mêmes **sensibles aux anomalies**.

Prenons sept montants de commandes d'un même compte : 12, 15, 14, 13, 16, 15 et **480** €. La moyenne vaut 80,7 € et l'écart-type 176,1 € : l'anomalie a gonflé les deux mesures qui devaient la repérer. Son z-score n'est que de $(480-80{,}7)/176{,}1=\mathbf{2{,}27}$, **sous le seuil habituel de 3** : le z-score classique ne voit pas la commande de 480 €. C'est le phénomène de **masquage** : l'anomalie se cache derrière sa propre influence.

Le remède est de remplacer la moyenne par la **médiane** et l'écart-type par l'**écart absolu médian** (MAD, *median absolute deviation*) :

$$\mathrm{MAD}=\operatorname{médiane}\bigl(|x_i-\operatorname{médiane}(x)|\bigr),\qquad z^{\text{rob}}=\frac{x-\operatorname{médiane}(x)}{1{,}4826\ \mathrm{MAD}}.$$

Sur nos sept montants : la médiane vaut 15, les écarts absolus à 15 sont 3, 0, 1, 2, 1, 0 et 465, rangés 0, 0, 1, 1, 2, 3, 465, de médiane **1**. Le MAD vaut 1 et le z-score robuste de 480 est $465/(1{,}4826\times1)\approx\mathbf{314}$ : l'anomalie saute aux yeux. La médiane et le MAD, eux, ne bougent presque pas quand on ajoute une valeur extrême : on dit qu'ils sont **robustes**.

> 📐 **D'où vient la constante 1,4826 ?** Elle rend le MAD comparable à un écart-type. Pour une loi normale $\mathcal N(\mu,\sigma^2)$, la moitié des valeurs est à moins de $a\sigma$ de la médiane, où $a$ vérifie $P(|Z|\le a)=\tfrac12$, c'est-à-dire $a=\Phi^{-1}(0{,}75)\approx 0{,}6745$. Donc $\mathrm{MAD}\approx0{,}6745\,\sigma$ et $\sigma\approx\mathrm{MAD}/0{,}6745=1{,}4826\ \mathrm{MAD}$.


**Plusieurs variables.** Nos commandes ont dix variables. Pour une variable continue ou de comptage, on calcule le z-score de chaque variable, puis on additionne les valeurs absolues : une fraude qui est *modérément* étrange sur plusieurs variables obtient un score élevé, même si aucune variable ne dépasse seule le seuil. Les variables binaires (appareil inconnu, IP étrangère) n'ont pas de z-score qui ait un sens ; nous n'utilisons ici que les six variables continues ou de comptage : montant, distance entre les adresses, nombre de commandes des dernières 24 heures, ancienneté du compte, délai depuis la dernière commande et nombre d'articles (en logarithme pour les quatre premières, car elles sont très asymétriques : chapitre 4, section 4.1).

> ⚠️ **Le piège du MAD nul.** Si plus de la moitié des valeurs sont égales (donc à la médiane), alors le MAD vaut **zéro** et le z-score robuste est indéfini. C'est exactement le cas du nombre de commandes des dernières 24 heures : **74 %** des commandes sont les premières de la journée pour leur compte, la médiane vaut 0, le MAD vaut 0. Si l'on ignore cette variable (ou si on la laisse à zéro), le détecteur « robuste » devient aveugle à la **rafale de commandes**, qui est justement le signe des prises de contrôle de compte. Une solution classique est d'utiliser, quand le MAD est nul, l'**écart absolu moyen** à la médiane multiplié par 1,2533 (la constante qui le rend comparable à un écart-type pour une loi normale : $E|X-\mu|=\sigma\sqrt{2/\pi}$, donc $\sigma\approx1{,}2533\,E|X-\mu|$).


Les trois variantes donnent des résultats **très différents** (précision moyenne AP, et part des fraudes de chaque type retrouvées parmi les 180 alertes) :

| z-score (somme des écarts) | AP | rappel type 1 | rappel type 2 |
|---|---:|---:|---:|
| classique | 0,433 | 0,46 | 0,48 |
| robuste, MAD seul | 0,296 | 0,57 | 0,17 |
| robuste, avec repli | 0,331 | 0,22 | 0,60 |

Il ne faut pas en conclure que « robuste » est un défaut, mais que **le choix de l'échelle revient à choisir le poids de chaque variable**. Le MAD seul ignore la rafale de commandes (variable à MAD nul) : il retrouve bien les fraudes de type 1 (compte neuf) mais presque aucune de type 2 (prise de contrôle). Le repli donne à la rafale une échelle étroite (0,38 contre 1 à 1,5 pour les autres variables) : le moindre excès de commandes pèse lourd, la prise de contrôle ressort, et les fraudes de type 1 passent au second plan. Le z-score classique, avec ses échelles larges, équilibre les deux. Ici la contamination (0,8 %) est trop faible pour fausser sensiblement moyenne et écart-type, ce qui explique que la version classique s'en sorte bien. La robustesse est une **assurance** : elle coûte un peu quand il n'y a pas de sinistre, et elle sauve quand il y en a un.

Reste un défaut fondamental : le z-score regarde **chaque variable séparément**. Une commande peut avoir un montant banal, une heure banale et une distance banale, et être pourtant inhabituelle par la **combinaison** (par exemple un petit montant, de nuit, depuis un compte vieux de deux jours). La section suivante prend en compte ces liaisons.

### 6.2.2 La distance de Mahalanobis

Considérons deux variables corrélées, par exemple le montant et le nombre d'articles : les grosses commandes contiennent en général plus d'articles. Un point (grosse commande, peu d'articles) est inhabituel *parce qu'il va à contre-courant de la corrélation*, sans être extrême sur aucune variable. La distance euclidienne ne le voit pas ; la **distance de Mahalanobis** le voit, car elle mesure l'écart en tenant compte de la forme du nuage :

$$d_M^2(x)=(x-\mu)^\top\Sigma^{-1}(x-\mu),$$

où $\mu$ est le vecteur des moyennes et $\Sigma$ la matrice de covariance.

**Un exemple à la main.** Deux variables standardisées (moyenne 0, variance 1) de corrélation $\rho=0{,}9$ : $\Sigma=\begin{pmatrix}1&0{,}9\\0{,}9&1\end{pmatrix}$, d'inverse $\Sigma^{-1}=\dfrac{1}{0{,}19}\begin{pmatrix}1&-0{,}9\\-0{,}9&1\end{pmatrix}$ (le déterminant vaut $1-0{,}81=0{,}19$). Comparons deux points à la même distance euclidienne de l'origine :

- $x=(2,\,2)$, qui suit la corrélation : $d_M^2=\dfrac{1}{0{,}19}\bigl(4-2\times0{,}9\times4+4\bigr)=\dfrac{0{,}8}{0{,}19}\approx\mathbf{4{,}21}$ ;
- $x=(2,\,-2)$, qui va à contre-courant : $d_M^2=\dfrac{1}{0{,}19}\bigl(4+2\times0{,}9\times4+4\bigr)=\dfrac{15{,}2}{0{,}19}=\mathbf{80}$.

Les deux points sont à la distance euclidienne $\sqrt 8$ de l'origine, mais l'un est parfaitement banal et l'autre rarissime. Mahalanobis dit que le premier est dans le nuage et le second hors de portée.

> 📐 **Pourquoi cette formule, et quelle valeur seuil ?** Écrivons la décomposition de Cholesky $\Sigma=LL^\top$ et posons $y=L^{-1}(x-\mu)$. Si $x\sim\mathcal N(\mu,\Sigma)$, alors $y\sim\mathcal N(0,I_p)$ : on a « blanchi » les variables, qui deviennent indépendantes et de variance 1. Or $y^\top y=(x-\mu)^\top L^{-\top}L^{-1}(x-\mu)=(x-\mu)^\top\Sigma^{-1}(x-\mu)=d_M^2$. C'est donc une somme de $p$ carrés de lois normales réduites indépendantes, qui suit une **loi du $\chi^2$ à $p$ degrés de liberté**. Un point est « à rejeter » au niveau 99,9 % si $d_M^2$ dépasse le quantile 0,999 de cette loi : 13,8 pour $p=2$, 29,6 pour $p=10$ (nos dix variables).

Cette théorie suppose des données gaussiennes, ce qui n'est pas le cas de nos commandes (certaines variables sont binaires, d'autres très asymétriques). Sur le jeu de test, **2,3 %** des commandes normales dépassent le seuil de 29,6, alors que la théorie en prévoirait 0,1 %. Le seuil théorique n'est donc **pas calibré** ; nous ne l'utilisons pas pour décider, mais pour **classer** (on garde les 180 commandes de plus grande distance).


**Le masquage, encore.** La moyenne $\mu$ et la covariance $\Sigma$ sont **estimées sur les données**, donc faussées par les anomalies elles-mêmes. Quand elles sont nombreuses ou groupées, elles gonflent $\Sigma$ et leurs distances s'écrasent. L'estimateur à **déterminant de covariance minimal** (MCD, *minimum covariance determinant*) calcule $\mu$ et $\Sigma$ sur le sous-ensemble de $h\approx90\ \%$ des points dont la covariance a le plus petit déterminant : on laisse de côté les points qui étirent le nuage. La figure montre l'effet sur un exemple simulé où 20 % des points forment un groupe lointain.


![Un exemple simulé : 800 points normaux (gris) corrélés et 200 points contaminants (rouge). L'ellipse classique (orange), estimée sur tous les points, est étirée vers les contaminants et les englobe ; l'ellipse robuste MCD (bleue) épouse les points normaux et laisse les contaminants à l'extérieur.](figures/ch06-masquage.png)

L'ellipse classique, étirée par les contaminants, **les englobe** : **aucun** d'entre eux (0 %) ne dépasse le seuil, contre 100 % avec l'estimateur robuste. Sur nos transactions, en revanche, les fraudes ne représentent que 0,8 % des données : il n'y a pas de masquage à craindre, et l'estimateur robuste n'apporte pas grand-chose (précision moyenne de 0,410 contre 0,382 pour la version classique, avec un temps de calcul bien plus long). **La robustesse a un coût, qu'il faut payer seulement si la contamination le justifie** : plus les anomalies sont nombreuses ou groupées dans les données d'apprentissage, plus elle devient nécessaire.


### 6.2.3 Les plus proches voisins

La distance de Mahalanobis suppose un seul nuage de forme elliptique. Les vraies données ont souvent plusieurs groupes, des formes courbes, des zones vides. L'idée des **plus proches voisins** s'affranchit de toute forme : *une commande est suspecte si ses voisins sont loin*. Pour chaque commande, on calcule la **distance moyenne à ses $k$ plus proches voisins** dans un échantillon de référence de commandes (supposées en majorité normales) ; plus elle est grande, plus la commande est isolée.

Le nombre de voisins $k$ est un **réglage**. Avec $k=1$, un seul voisin proche suffit à « innocenter » une commande, et le score est bruité ; avec $k$ très grand, on compare la commande à la masse entière des commandes, et l'on perd la finesse. Nous le choisissons **sur le jeu de validation** (jamais sur le test), parmi 1, 3, 5, 10, 30 et 100 :

```text
   k   AP validation   AP test
   1           0.261     0.303
   3           0.321     0.378
   5           0.350     0.411
  10           0.382     0.444
  30           0.400     0.460
 100           0.399     0.448
k choisi sur la validation : 30
```


La précision moyenne sur le jeu de validation passe de 0,261 pour $k=1$ à **0,400 pour $k=30$**, puis plafonne (0,399 pour $k=100$) : nous retenons $k=30$. Le jeu de test donne le même classement des réglages (0,303 pour $k=1$, 0,460 pour $k=30$), ce qui rassure sur le choix.

```python
from sklearn.neighbors import NearestNeighbors

voisins = NearestNeighbors(n_neighbors=k_knn).fit(Z_app[reference])    # 10 000 commandes de référence, variables standardisées
distances, _ = voisins.kneighbors(Z_test)
score_knn = distances.mean(axis=1)                                      # distance moyenne aux k plus proches voisins
```


Quelques points de méthode :

- **Il faut des variables à des échelles comparables** (chapitre 4, section 4.1) : sans cela, la variable d'échelle la plus grande décide seule des distances. La standardisation est le choix par défaut, et nous l'appliquons à tous les détecteurs de ce chapitre pour les comparer sur le même pied. Elle n'est pourtant pas toujours le meilleur : ici nos variables ont déjà été passées au logarithme et ont des échelles voisines, alors que les deux variables binaires (IP étrangère, appareil inconnu) ont un écart-type faible (0,20 et 0,30, contre 0,56 à 1,22 pour les autres) : standardiser les **multiplie par 5 et 3,3** et leur donne un poids très supérieur dans la distance. Avec les variables brutes, la précision moyenne des mêmes voisins monte à **0,511** (contre 0,460) ; en ne standardisant que les variables continues et en laissant les deux variables binaires en 0/1, on obtient **0,513**, ce qui confirme l'explication. L'application 6.3 du cahier reproduit ces calculs.
- **Le coût de calcul.** Comparer chaque commande à toutes les autres est quadratique ; nous utilisons un **échantillon de référence** de 10 000 commandes, ce qui suffit à décrire le comportement normal (l'application 6.3 montre que la précision moyenne passe de 0,37 avec 500 commandes de référence à 0,46 avec 2 000, puis ne progresse plus que lentement, jusqu'à 0,48 avec 20 000). Des structures d'index (arbres, graphes de voisinage approchés) accélèrent le calcul quand la dimension est modeste.

Cette méthode toute simple obtient une précision moyenne de **0,460** sur le jeu de test, et retrouve **69 %** des fraudes de type 2 dans les 180 alertes (contre 26 % de celles de type 1). Elle repose sur très peu d'hypothèses, et c'est l'une des raisons pour lesquelles elle reste un excellent premier essai.

### 6.2.4 Le facteur local d'anomalie (LOF)

Une limite des distances aux voisins : elles supposent que la **densité est la même partout**. Imaginons deux groupes de clients, l'un très concentré (des habitudes d'achat très régulières) et l'autre très étalé. Un point à 1,3 unité du groupe concentré est une **vraie anomalie pour ce groupe**, mais sa distance aux voisins (1,3) est *inférieure* aux distances ordinaires dans le groupe étalé. Une distance globale le noie.

Le **LOF** (*Local Outlier Factor*) compare la densité autour d'un point à celle de ses voisins. Voici les définitions, pour un entier $k$ :

1. la **$k$-distance** $d_k(p)$ : la distance de $p$ à son $k$-ième plus proche voisin ; $N_k(p)$ est l'ensemble de ses $k$ plus proches voisins ;
2. la **distance d'atteignabilité** de $p$ depuis $o$ : $\operatorname{rd}_k(p,o)=\max\{d_k(o),\,d(p,o)\}$ (on ne descend pas en dessous de la $k$-distance du voisin, ce qui lisse les fluctuations) ;
3. la **densité d'atteignabilité locale** : $\operatorname{lrd}_k(p)=\Bigl(\dfrac{1}{|N_k(p)|}\sum_{o\in N_k(p)}\operatorname{rd}_k(p,o)\Bigr)^{-1}$, l'inverse de la distance d'atteignabilité moyenne ;
4. le **facteur d'anomalie** $\mathrm{LOF}_k(p)=\dfrac{1}{|N_k(p)|}\sum_{o\in N_k(p)}\dfrac{\operatorname{lrd}_k(o)}{\operatorname{lrd}_k(p)}$ : le rapport entre la densité des voisins et celle de $p$.

Un $\mathrm{LOF}$ voisin de **1** signifie que $p$ est aussi dense que ses voisins ; un $\mathrm{LOF}$ **nettement supérieur à 1** signifie que $p$ est plus isolé que ses voisins.

**Un exemple à la main : six points sur une droite**, aux abscisses $0;\ 1;\ 3;\ 4{,}4;\ 6{,}1;\ 10$, avec $k=2$. Le tableau donne, pour chaque point, ses deux voisins, sa 2-distance, sa densité et son LOF (calculés ligne à ligne avec les formules ci-dessus, puis vérifiés avec `scikit-learn`) :

```text
abscisse   voisins (abscisses)   2-distance   densité lrd   LOF
    0.0   [1.0, 3.0]                 3.0        0.4000   1.176
    1.0   [0.0, 3.0]                 2.0        0.4000   1.176
    3.0   [4.4, 1.0]                 2.0        0.5405   0.733
    4.4   [3.0, 6.1]                 1.7        0.3922   1.220
    6.1   [4.4, 3.0]                 3.1        0.4167   1.119
   10.0   [6.1, 4.4]                 5.6        0.2105   1.921
(vérification : mêmes LOF que scikit-learn)
```

Lecture : le point d'abscisse **10**, isolé au bout de la droite, a un LOF de **1,92** ; les points au centre du groupe (3 ; 4,4 ; 6,1) ont des LOF proches de 1 (0,73 ; 1,22 ; 1,12) ; le point 3, entouré, est même plus dense que ses voisins (0,73).


![Six points sur une droite. La surface de chaque disque est proportionnelle au carré du facteur d'anomalie (LOF) : le point isolé à 10 a le LOF le plus élevé (1,92).](figures/ch06-lof-jouet.png)

Voici maintenant l'avantage du LOF sur la distance aux voisins, sur un exemple simulé : un groupe concentré de 200 points (écart-type 0,25), un groupe étalé de 100 points (écart-type 1,5), et un point **ajouté à 1,3 unité** du groupe concentré (cercle orange).


![Deux groupes de densités différentes. Les points sont colorés par la distance moyenne aux voisins (à gauche) ou par le LOF (à droite) ; plus la couleur est foncée, plus le score est élevé. Le point ajouté près du groupe concentré (cercle orange) est noyé parmi les points du groupe étalé à gauche, et il est le plus anormal à droite.](figures/ch06-lof-densites.png)

Selon la distance aux voisins, le point ajouté n'arrive qu'au **26e rang** sur 301 : les points du groupe étalé, naturellement plus éloignés les uns des autres, le dominent (la plus grande distance du groupe étalé dépasse 4). Selon le LOF, il est **premier**, avec un LOF d'environ 5 : relativement à ses voisins, il est cinq fois moins dense.

Le LOF dépend lui aussi d'un réglage $k$, et beaucoup plus que les voisins simples. Nous le choisissons sur le jeu de validation, parmi 10, 30, 100 et 300 :

```text
   k   AP validation   AP test
  10           0.114     0.113
  30           0.243     0.306
 100           0.408     0.471
 300           0.433     0.492
k choisi sur la validation : 300
```

La précision moyenne sur la validation passe de **0,114** pour $k=10$ à **0,433** pour $k=300$ : un LOF réglé à la légère est un très mauvais détecteur, un LOF bien réglé est l'un des meilleurs. La raison est que la densité « locale » estimée avec peu de voisins est très bruitée ; avec 300 voisins, elle devient stable. Le meilleur $k$ est en bout de grille : une grille plus large aurait peut-être fait mieux, ce que nous n'avons pas exploré.

```python
from sklearn.neighbors import LocalOutlierFactor

lof = LocalOutlierFactor(n_neighbors=k_lof, novelty=True).fit(Z_app[reference])
score_lof = -lof.score_samples(Z_test)               # novelty=True : on score de nouveaux points
```


Sur nos transactions, le LOF réglé à $k=300$ obtient une précision moyenne de **0,492** sur le jeu de test, mieux que les voisins simples (0,460) ; il retrouve **52 %** des fraudes de type 1 et **49 %** de celles de type 2. Le LOF repère les commandes isolées *par rapport à leur voisinage*, ce qui convient à des fraudes qui s'éloignent localement des habitudes sans être extrêmes dans l'absolu.

### 6.2.5 Ce que voient ces méthodes, et ce qu'elles ratent

Toutes les méthodes de cette section sont ajustées sans étiquette, et toutes ont reçu le même jeu d'apprentissage. Le tableau résume leurs performances sur le jeu de test.

```text
                                 AUC     AP  précision à k  rappel type 1  rappel type 2
z-score classique              0.939  0.433          0.452          0.457          0.477
z-score robuste (avec repli)   0.930  0.331          0.342          0.222          0.600
Mahalanobis                    0.946  0.382          0.356          0.198          0.615
Mahalanobis robuste (MCD)      0.949  0.410          0.404          0.235          0.677
Plus proches voisins (k = 30)  0.959  0.460          0.432          0.259          0.692
LOF (k = 300)                  0.944  0.492          0.493          0.519          0.492
```

Deux enseignements, que la section 6.4.5 reprendra avec les méthodes suivantes :

1. **Chaque méthode définit autrement ce qui est « normal »**, donc trouve d'autres fraudes. Mahalanobis, les voisins (avec 69 %) retrouvent surtout le type 2 et peu le type 1 (de 20 à 26 %) ; le z-score classique les équilibre (0,46 et 0,48) ; et le LOF réglé à $k=300$ retrouve les deux types à parts à peu près égales (52 % et 49 %). Il n'existe pas de « meilleure méthode » dans l'absolu.
2. **Le réglage compte autant que la méthode.** Le LOF passe d'une précision moyenne de 0,11 (avec 10 voisins) à 0,49 (avec 300) ; les voisins simples varient de 0,30 à 0,46 selon $k$. Aucun réglage n'est universel, et sans étiquette on ne peut pas savoir lequel convient : c'est pourquoi on garde un **jeu de validation étiqueté**, même petit, pour régler, et un jeu de test pour juger.

> ✅ **À retenir.**
> - Le **z-score** juge chaque variable seule ; moyenne et écart-type sont faussés par les anomalies (**masquage**) : médiane et **MAD** (constante 1,4826) sont robustes. Attention au **MAD nul** (plus de la moitié de valeurs identiques).
> - La **distance de Mahalanobis** $d_M^2=(x-\mu)^\top\Sigma^{-1}(x-\mu)$ tient compte des corrélations ; sous hypothèse gaussienne elle suit un $\chi^2_p$. La version robuste (MCD) n'est utile que si la contamination est importante.
> - La **distance aux $k$ plus proches voisins** ne suppose aucune forme ; il faut des variables à des échelles comparables et un $k$ **choisi sur un jeu de validation**.
> - Le **LOF** compare la densité d'un point à celle de ses voisins : il détecte les anomalies **locales** quand les densités varient ; il est **très sensible à $k$** (précision moyenne de 0,11 à 0,49 selon le réglage).
> - Aucune de ces méthodes n'est la meilleure partout ; chacune a ses fraudes de prédilection.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.2 et 6.3, exercices 6.5 à 6.7.


## 6.3 La forêt d'isolement

Les méthodes de la section précédente décrivent d'abord ce qui est **normal** (un centre, une covariance, une densité), puis déclarent anormal ce qui s'en écarte. Elles font un travail inutile : on ne cherche pas à bien décrire les commandes normales, mais à repérer les rares qui ne le sont pas. La **forêt d'isolement** (*isolation forest*, Liu, Ting et Zhou, 2008) prend le problème à l'envers : au lieu de décrire le normal, elle mesure **la facilité avec laquelle on isole chaque point**.


### 6.3.1 L'idée : isoler plutôt que décrire

Voici huit valeurs : sept proches les unes des autres (2 ; 3 ; 3,5 ; 4 ; 4,5 ; 5 ; 5,5) et une très éloignée (30). On joue à un jeu : on tire une **coupure au hasard** entre le minimum et le maximum, ce qui sépare les valeurs en deux groupes ; on garde le groupe qui contient la valeur étudiée, on recommence, et on compte le nombre de coupures nécessaires pour la **laisser seule**.

- Pour la valeur 30, la première coupure l'isole dès qu'elle tombe entre 5,5 et 30 : c'est le cas avec la probabilité $(30-5{,}5)/(30-2)=\mathbf{87{,}5\ \%}$. Il suffit **d'une coupure ou deux**.
- Pour la valeur 4, au milieu du groupe, il faut en général **cinq coupures** : elle est entourée de voisines qu'il faut écarter une à une.

En répétant ce jeu avec 5 000 séquences de coupures aléatoires, on obtient le nombre moyen de coupures nécessaires pour isoler chaque valeur :

```text
valeur   coupures moyennes pour l'isoler
   2.0    2.95
   3.0    4.19
   3.5    4.70
   4.0    4.76
   4.5    4.70
   5.0    4.40
   5.5    3.55
  30.0    1.14
probabilité que 30 soit isolée dès la 1re coupure (simulation) : 0.869 ; calcul exact : 0,875
```

La valeur 30 est isolée en **1,14 coupure** en moyenne, contre 4,4 à 4,8 pour les valeurs centrales. **Les anomalies sont peu nombreuses et différentes : elles s'isolent vite.** C'est tout le principe de la méthode : la longueur moyenne du « chemin » qui mène à une observation est une mesure d'anormalité, sans qu'on ait jamais eu à décrire ce qu'est la normalité.

> 💡 **Pourquoi cela marche.** Les points normaux se trouvent dans des régions denses : il faut beaucoup de coupures pour les séparer de leurs voisins. Un point isolé a autour de lui du vide : presque n'importe quelle coupure le sépare du reste.

### 6.3.2 La longueur de chemin et le score d'anomalie

Cette idée s'applique à plusieurs variables : à chaque étape, on choisit **une variable au hasard**, puis une **coupure au hasard** entre le minimum et le maximum de cette variable dans le groupe courant. On répète jusqu'à ce que chaque point soit seul (ou qu'une hauteur maximale soit atteinte). Le résultat est un **arbre d'isolement** ; la **longueur de chemin** $h(x)$ d'un point $x$ est le nombre de coupures qui l'isolent. Une **forêt** de nombreux arbres, construits chacun sur un sous-échantillon, donne une longueur moyenne $E[h(x)]$.

Pour transformer cette longueur en score comparable d'un jeu de données à l'autre, on la normalise. Un arbre d'isolement de $n$ points a la même structure qu'un **arbre binaire de recherche** : la longueur moyenne d'un chemin y est connue. C'est celle d'une recherche infructueuse, soit

$$c(n)=2H(n-1)-\frac{2(n-1)}{n},\qquad H(i)\approx\ln(i)+0{,}5772\ \ (\text{constante d'Euler}),$$

où $H(i)$ est le $i$-ième nombre harmonique. On définit alors le **score d'anomalie**

$$\boxed{\ s(x,n)=2^{-E[h(x)]/c(n)}\ }$$

Le score est toujours entre 0 et 1, et se lit ainsi :

- si $E[h(x)]$ est **très petit** (isolé presque immédiatement), $s\to 1$ : forte anomalie ;
- si $E[h(x)]=c(n)$ (un point moyen), $s=2^{-1}=\mathbf{0{,}5}$ : rien de particulier ;
- si $E[h(x)]$ est **grand** (profondément enfoui), $s\to 0$ : point très normal.

```text
n      c(n)
    2   1.000
    8   3.296
   16   4.696
   64   7.472
  256  10.245
 1000  12.970

score pour n = 256 (c = 10.24) : {'E[h] = 2': 0.873, 'E[h] = 4': 0.763, 'E[h] = 10.2': 0.502, 'E[h] = 20': 0.258}
```

Pour $n=256$ points, $c(256)\approx10{,}2$ : un point isolé en 2 coupures a un score de 0,87, un point isolé en 4 coupures de 0,76, un point moyen de 0,50, et un point qu'il faut 20 coupures pour isoler de 0,26.

> ⚠️ **Une approximation, pas une identité.** La normalisation $c(n)$ est une *analogie* avec les arbres de recherche (c'est l'argument de l'article d'origine). Nos coupures sont tirées uniformément entre le minimum et le maximum, et non selon les rangs, ce qui change un peu la structure des arbres. En simulant directement des coupures uniformes sur des échantillons de $n$ valeurs normales, on trouve une profondeur moyenne légèrement supérieure à $c(n)$ (de 7 à 10 % de plus, pour $n=8$, 64 et 256). Cela ne change pas l'**ordre** des scores, qui est ce dont on se sert pour classer les alertes ; seul le point d'équilibre à 0,5 est un peu décalé.


### 6.3.3 De l'arbre à la forêt

Dans la pratique, la forêt d'isolement construit **$t$ arbres** (200 dans nos essais). Chacun est bâti sur un **petit sous-échantillon** de $\psi$ points tirés au hasard (256 par défaut), avec une hauteur maximale de $\lceil\log_2\psi\rceil=8$ : inutile de pousser l'arbre plus profond, puisque les anomalies s'isolent bien avant. Ces choix donnent trois propriétés précieuses :

- **Elle ne calcule aucune distance** et n'estime ni moyenne ni covariance : son coût de construction ne dépend presque pas de la taille $n$ du jeu de données (chaque arbre n'utilise que $\psi$ points), et le score d'un point coûte $t\log\psi$ opérations. Elle passe à l'échelle de millions de lignes.
- **Le sous-échantillonnage la protège du masquage et de l'« engorgement »** (*swamping*) : avec peu de points par arbre, les anomalies ne sont plus noyées dans des régions denses de points normaux voisins, et les points normaux ne sont plus pris pour des anomalies parce qu'ils voisinent avec elles.
- **Elle est invariante aux changements d'échelle linéaires** de chaque variable (la coupure est tirée dans l'étendue de la variable), mais pas aux transformations non linéaires comme le logarithme : c'est pourquoi nos variables très asymétriques (montant, distance, ancienneté, délai) sont transformées en logarithme avant tout (chapitre 4, section 4.1).

Les choix de $t$ et de $\psi$ comptent. Voici la précision moyenne (AP) obtenue sur le jeu de test pour différentes valeurs, en moyenne sur trois graines :

```text
nombre d'arbres (psi = 256) : {10: 0.216, 50: 0.318, 200: 0.366}
taille du sous-échantillon psi (100 arbres) : {32: 0.287, 64: 0.3, 256: 0.355, 1024: 0.373, 4096: 0.398}
```

Avec trop peu d'arbres (10), le score est bruité ; au-delà de 100 arbres, on gagne peu. Quant au sous-échantillon, ici, **plus il est grand, mieux c'est** (de 0,29 pour $\psi=32$ à 0,40 pour $\psi=4096$) : la valeur de 256 recommandée par l'article d'origine est une valeur par défaut raisonnable, pas un optimum. Comme toujours, ces réglages se décident mieux avec quelques étiquettes pour évaluer.

### 6.3.4 Le paramètre de contamination et le seuil

La forêt produit un **score**, pas une décision. Pour décider, `scikit-learn` propose un paramètre `contamination` : la proportion supposée d'anomalies dans les données. Il fixe le **seuil** au quantile correspondant des scores d'apprentissage. Sa valeur par défaut, `"auto"`, utilise un seuil fixe (score de 0,5) tiré de l'article d'origine.


Sur nos données, le seuil par défaut déclenche une alerte sur **20,5 %** des commandes (3 699 alertes) : on retrouve **92,5 %** des fraudes, mais la précision tombe à **3,6 %**, et la gérante croulerait sous les vérifications. En fixant `contamination = 0,0081` (la vraie proportion de fraudes), on obtient environ 150 alertes, de précision **34 %**, et un rappel de **35 %**.

Cet exemple dit quelque chose d'important : **la contamination n'est pas un paramètre statistique que les données révèlent, c'est un choix opérationnel.** En pratique on ne connaît pas la proportion de fraudes ; ce que l'on connaît, c'est le **budget d'alertes** que l'on peut traiter. C'est pourquoi nous classons toujours les commandes par score et gardons les 180 plus suspectes (1 % du test), plutôt que de nous fier à un seuil théorique.

### 6.3.5 Sur nos transactions

```python
from sklearn.ensemble import IsolationForest

foret = IsolationForest(n_estimators=200, random_state=0).fit(Z_app)     # aucune étiquette
score_isolement = -foret.score_samples(Z_test)                           # score s : plus grand = plus anormal
```


![À gauche, le petit exemple de huit valeurs : nombre moyen de coupures nécessaires pour isoler chacune (la valeur 30, en rouge, s'isole en une coupure environ). À droite, la distribution des scores de la forêt d'isolement sur le jeu de test pour les commandes normales (gris) et les deux types de fraude ; la ligne pointillée marque le seuil qui garde 180 alertes.](figures/ch06-isolement.png)

La forêt d'isolement obtient une précision moyenne de **0,332** : un peu en dessous des voisins (0,444), au niveau de Mahalanobis (0,382) ou du LOF (0,306). Sa force est qu'elle est **rapide et sans réglage délicat**. Mais comme le montre la figure de droite, ses scores séparent bien les fraudes de **type 2** (dont le score moyen de 0,626 est bien au-dessus de celui des commandes normales, 0,459) et beaucoup moins bien les fraudes de **type 1** (0,555) : 68 % des fraudes de type 2 sont dans les 180 alertes, contre 12 % seulement de celles de type 1.

Pourquoi cette différence ? Ce n'est pas faute de valeurs extrêmes : la vérification ci-dessus montre que **78 %** des fraudes de type 1 ont au moins une variable à plus de 3 écarts-types (contre 89 % pour le type 2 et 10 % pour les commandes normales), et qu'elles s'écartent en moyenne de plus de 1,5 écart-type sur 3 variables (3,6 pour le type 2). Les deux types sont donc bien loin de la normale, le type 2 un peu plus. Nous n'avons **pas démontré** pourquoi cela suffit à placer les fraudes de type 2 beaucoup plus haut dans le classement de la forêt. Une hypothèse, que nous n'avons pas testée, est que les variables caractéristiques du type 2 (appareil inconnu, adresse IP étrangère, rafale de commandes) sont rares et à valeurs discrètes, donc qu'une seule coupure suffit à les isoler, alors que celles du type 1 (montant, distance) ont des queues lourdes qui rendent de nombreuses commandes **normales** presque aussi faciles à isoler. Le seul fait établi est empirique : sur ces données, la forêt classe bien le type 2 et mal le type 1.

> ✅ **À retenir.**
> - La forêt d'isolement mesure la **facilité à isoler** un point par des coupures aléatoires : les anomalies, rares et différentes, s'isolent vite.
> - Le score $s=2^{-E[h(x)]/c(n)}$ vaut 0,5 pour un point moyen et tend vers 1 pour une anomalie ; $c(n)=2H(n-1)-2(n-1)/n$ est une normalisation approchée.
> - Elle est **rapide**, sans distance ni hypothèse de loi, et passe à l'échelle grâce au sous-échantillonnage.
> - La **contamination** est un choix opérationnel (le budget d'alertes), pas une vérité statistique : le seuil par défaut peut donner des milliers de fausses alertes.
> - Sa qualité dépend de la nature des anomalies : ici elle retrouve bien les fraudes de type 2 et mal celles de type 1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.4, exercices 6.8 et 6.9.


## 6.4 Autoencodeurs, et comparaison des méthodes

La forêt d'isolement mesure la facilité à *isoler* un point. Un **autoencodeur** suit une logique opposée : il apprend à *reproduire* ses entrées après les avoir comprimées, et l'on juge anormal ce qu'il ne parvient pas à reproduire. Cette section présente l'idée, son lien exact avec l'ACP, un exemple avec `scikit-learn`, et ses pièges. Elle se termine par la **comparaison honnête** de toutes les méthodes du chapitre.


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

```python
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


## Bilan du chapitre 6

Vous savez maintenant :

- **distinguer** anomalie ponctuelle, contextuelle et collective, et **ne pas confondre** anomalie (fait statistique) et fraude (fait métier) ;
- **expliquer** pourquoi l'apprentissage supervisé suffit rarement (déséquilibre extrême, délai des étiquettes, adversaire qui s'adapte, fraudes inédites, étiquettes biaisées) et quand il reste le meilleur choix ;
- **évaluer un détecteur sous déséquilibre extrême** : l'exactitude est trompeuse (99,19 % pour un détecteur inutile), la formule de Bayes explique pourquoi la précision est faible, la **courbe précision-rappel** et l'**AP** remplacent la ROC, et le **budget d'alertes** et le **coût** fixent le seuil ;
- **utiliser le z-score** et sa version **robuste** (médiane, MAD de constante 1,4826, piège du MAD nul), la **distance de Mahalanobis** (loi du $\chi^2$, masquage, MCD), la **distance aux plus proches voisins** et le **LOF** (densité locale) ;
- **comprendre la forêt d'isolement** : longueur de chemin, score $s=2^{-E[h]/c(n)}$, sous-échantillonnage, et pourquoi la contamination est un choix opérationnel ;
- **construire un autoencodeur** avec `scikit-learn`, savoir qu'**il est équivalent à l'ACP quand il est linéaire**, que sa capacité doit être contrainte, qu'un réseau isolé est instable et qu'un comité de réseaux stabilise ;
- **comparer honnêtement** plusieurs détecteurs : un jeu de validation étiqueté pour régler, le jeu de test seulement pour juger, et se méfier des combinaisons naïves, qui ne battent pas forcément leur meilleur membre.

Le fil rouge du chapitre est le même que celui du volume : **la rigueur d'évaluation compte plus que la sophistication du modèle**. Les distances et les densités de la section 6.2 sont des idées anciennes qui rivalisent avec des méthodes récentes ; l'autoencodeur, le plus moderne, n'a été meilleur que parce que nous l'avons réglé sur un jeu de validation et moyenné sur plusieurs graines. Sur un problème où les erreurs coûtent de l'argent, la bonne question n'est jamais « quel est le meilleur algorithme ? », mais « *combien d'argent économise-t-on pour un budget de vérification donné, et comment le sait-on sans se tromper soi-même ?* ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.12.

Le chapitre 7 (complémentaire, lui aussi) change de problème : au lieu de signaler ce qui est étrange, il s'agit de **recommander** à chaque client les produits qu'il aimera, à partir des achats de tous les clients.
