# Chapitre 8 : ➕ Apprentissage semi-supervisé et actif

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui se heurtent, en pratique, à un problème très courant : **on a beaucoup de données, mais très peu d'étiquettes**.

> « Les données coulent à flots ; les étiquettes, elles, se paient au compte-gouttes. »

Tout au long du volume, nous avons supposé que chaque ligne du tableau venait avec sa **réponse** : ce client a-t-il résilié ou non, cette image représente-t-elle un 3 ou un 8, cette commande est-elle une fraude. Dans la vie réelle, cette réponse a souvent un **prix** :

- pour savoir si un client a résilié, il faut **attendre** trois mois, ou l'appeler (quelques euros par appel) ;
- pour savoir si une image montre tel chiffre ou tel défaut sur un produit, il faut qu'un **humain** la regarde ;
- pour savoir si une commande est frauduleuse, il faut une **enquête**.

La boutique, elle, possède des dizaines de milliers de lignes de données *brutes* (clients, images, commandes) mais seulement quelques dizaines de lignes *étiquetées*. Deux familles de méthodes répondent à cette situation, avec deux questions différentes :

| | **Question posée** | **Le lecteur retiendra** |
|---|---|---|
| **Apprentissage semi-supervisé** | « Les données **non étiquetées** que j'ai déjà peuvent-elles m'aider à mieux apprendre avec peu d'étiquettes ? » | exploiter ce qu'on a **gratuitement** |
| **Apprentissage actif** | « Si je ne peux payer que $b$ étiquettes, **lesquelles** dois-je demander ? » | choisir ce qu'on **achète** |

> 💡 **Intuition.** Imaginez que vous apprenez à reconnaître des champignons. Un expert est disponible une heure. Vous pouvez (1) *regarder des milliers de photos sans légende* en vous disant « ces deux-là se ressemblent donc sont sans doute de la même espèce » : c'est le **semi-supervisé** ; ou (2) *choisir avec soin les dix champignons que vous montrerez à l'expert*, en lui apportant ceux qui vous font le plus hésiter : c'est l'**actif**. Les deux se combinent.

## Le chemin de ce chapitre

- **8.1 Pourquoi et hypothèses** : ce que les données non étiquetées *peuvent* apporter, les quatre hypothèses qui le permettent, les cas où elles **nuisent**, et le seul outil d'évaluation honnête de ce chapitre, la **courbe d'apprentissage selon le budget d'étiquettes**.
- **8.2 Auto-apprentissage et propagation d'étiquettes** : deux méthodes concrètes, l'une qui étiquette elle-même les cas faciles, l'autre qui fait « couler » les étiquettes le long d'un graphe de similarité.
- **8.3 Apprentissage actif** : la boucle « entraîner, choisir, demander, recommencer », les critères de choix (incertitude, marge, entropie, comité, densité), le **piège du biais d'échantillonnage**, le **démarrage à froid** et un petit calcul de coût.

> 📒 **Pour s'entraîner.** Le cahier de ce chapitre contient huit applications guidées (courbes d'apprentissage, auto-apprentissage, propagation, co-apprentissage, boucle active écrite à la main, comité, biais d'échantillonnage, calcul de coût) et douze exercices corrigés. Chaque section du livre indique celles qui la prolongent.

## Les données du chapitre

Deux jeux de données serviront d'un bout à l'autre, **sans aucun téléchargement** :

| Jeu | Nature | Taille | Rôle |
|---|---|---|---|
| **Chiffres manuscrits** (`load_digits` de scikit-learn) | **réel** : images 8 × 8 pixels de chiffres écrits à la main, 10 classes | 1 797 images ; nous en gardons 1 347 comme **réservoir** (*pool*) à étiqueter et 450 comme **jeu de test** | des classes bien groupées : le cas où les méthodes de ce chapitre brillent |
| **Clients de la boutique** (`donnees/clients_ml.csv`, volume III) | **simulé** : 12 000 clients, résiliation à 90 jours (14 %) | 9 000 en réservoir, 3 000 en test | des variables mélangées (nombres, catégories) et des classes qui se chevauchent : le cas où ces méthodes **déçoivent** |

Les étiquettes de ces deux jeux sont en réalité toutes connues : c'est ce qui permet de **simuler** un budget d'étiquettes limité (on « cache » presque toutes les étiquettes, puis on mesure ce que les méthodes savent en faire) et de vérifier, à la fin, si elles ont deviné juste. Les clients, eux, sont plus difficiles : des variables de natures différentes et des classes qui se chevauchent, comme dans la vraie vie.

> ⚠️ **Une convention à connaître.** Dans scikit-learn, une observation **sans étiquette** se marque par la valeur `-1` dans le vecteur des étiquettes. Les méthodes semi-supervisées reçoivent *tout* le tableau de variables $X$, et un vecteur $y$ où seules quelques entrées sont renseignées.

```python
y_partiel = np.full(len(y), -1)              # -1 = « pas d'étiquette »
y_partiel[indices_etiquetes] = y[indices_etiquetes]
```


## 8.1 Pourquoi et hypothèses

Avant de présenter des méthodes, il faut comprendre **pourquoi** des données sans étiquette pourraient aider, à quelles **conditions**, et comment **vérifier honnêtement** qu'elles aident. Cette section pose le cadre ; les deux suivantes l'utilisent.

### 8.1.1 Le problème de l'étiquette chère

Reprenons les notations du volume. Nous disposons de deux paquets de données :

- un petit ensemble **étiqueté** $\mathcal L=\{(x_i,y_i)\}_{i=1}^{n_\ell}$, où l'on connaît la réponse $y_i$ ;
- un grand ensemble **non étiqueté** $\mathcal U=\{x_j\}_{j=1}^{n_u}$, où l'on ne connaît que les variables $x_j$.

La situation typique est $n_u\gg n_\ell$ : quelques dizaines d'exemples étiquetés, des milliers d'autres sans réponse. On distingue trois façons de s'en sortir :

| Paradigme | Ce qu'on utilise | Ce qu'on produit |
|---|---|---|
| **Supervisé** | seulement $\mathcal L$ | un modèle $f$ qui prédit $y$ à partir de $x$ |
| **Non supervisé** | seulement les $x$ | des groupes, des axes, une structure (chapitre 3) |
| **Semi-supervisé** | $\mathcal L$ **et** $\mathcal U$ | un modèle $f$, appris avec l'aide de la structure de $\mathcal U$ |

Deux nuances de vocabulaire sont utiles pour lire la littérature :

- l'apprentissage est **transductif** quand on ne cherche qu'à étiqueter les points de $\mathcal U$ que l'on a *déjà* sous la main (typiquement : les 5 000 clients de la base à qualifier) ;
- il est **inductif** quand on veut un modèle $f$ capable de prédire sur de **nouveaux** points (les clients de demain).

> 💡 **La seule mesure du succès.** Une méthode semi-supervisée n'a de valeur que si elle fait mieux que le modèle **supervisé entraîné sur les mêmes étiquettes** $\mathcal L$. Comparer à un modèle qui disposerait de *plus* d'étiquettes n'aurait aucun sens : l'enjeu est précisément ce que l'on gagne **à budget d'étiquettes égal**.

### 8.1.2 Ce que les données non étiquetées apportent

Un point $x_j$ sans étiquette ne nous dit rien, à lui seul, sur sa classe. Alors comment pourrait-il aider ? Parce que **l'ensemble** des $x_j$ nous renseigne sur la loi des variables, $p(x)$ : où se concentrent les données, où sont les creux, quelle est la forme des groupes. Si cette structure est **liée** à la classe, l'information est précieuse.

**Un exemple minuscule, entièrement à la main.** Une seule variable $x$, deux classes A et B. Deux clients seulement sont étiquetés :

- le client A vaut $x=-1{,}4$ ;
- le client B vaut $x=+0{,}6$.

Entraîné sur ces deux points, un classifieur « centre le plus proche » place sa frontière au milieu : $(−1{,}4+0{,}6)/2=-0{,}4$. Mais six autres clients, **sans étiquette**, ont été observés :

$$-2{,}1,\quad -1{,}8,\quad -1{,}2,\qquad +1{,}3,\quad +1{,}7,\quad +2{,}0.$$

Ils forment **visiblement deux paquets**, un à gauche et un à droite d'un creux vide autour de $0$. La frontière à $-0{,}4$ passe au bord du paquet de gauche : elle est suspecte. Corrigeons-la en une étape :

1. **Étiqueter provisoirement** chaque point non étiqueté selon la frontière actuelle ($-0{,}4$) : les trois de gauche sont classés A, les trois de droite B.
2. **Recalculer les centres** avec tous les points : $\bar x_A=\dfrac{-1{,}4-2{,}1-1{,}8-1{,}2}{4}=-1{,}625$ et $\bar x_B=\dfrac{0{,}6+1{,}3+1{,}7+2{,}0}{4}=1{,}4$.
3. **Recalculer la frontière** : $\dfrac{-1{,}625+1{,}4}{2}=-0{,}1125$.

Si les deux classes sont des cloches symétriques de même largeur, la vraie frontière est en $0$. La frontière est passée de $-0{,}4$ à $-0{,}11$ : **elle s'est rapprochée du creux**, grâce aux six points sans étiquette.


> 📐 **Le principe derrière l'exemple : la vraisemblance mixte.** Supposons un modèle génératif $p(x,y\mid\theta)=p(y)\,p(x\mid y,\theta)$ (par exemple, deux lois normales). Pour un point étiqueté, la contribution à la log-vraisemblance est $\log p(x_i,y_i\mid\theta)$. Pour un point **non** étiqueté, on ne voit pas $y_j$ ; on **somme** sur toutes ses valeurs possibles :
> $$\ell(\theta)=\sum_{i\in\mathcal L}\log p(x_i,y_i\mid\theta)\;+\;\sum_{j\in\mathcal U}\log\sum_{c}p(y_j=c)\,p(x_j\mid y_j=c,\theta).$$
> Le second terme est exactement celui d'un **mélange de lois** (nous retrouverons les mélanges gaussiens en section 3.3 du présent volume). On le maximise par l'algorithme **EM** : l'étape **E** calcule, pour chaque point sans étiquette, la probabilité $r_{jc}=P(y_j=c\mid x_j,\theta)$ (« à quel point ce point appartient-il à la classe $c$ ? ») ; l'étape **M** réestime $\theta$ en comptant chaque point à hauteur de ces probabilités, les points étiquetés comptant pour 1 dans leur classe. L'exemple ci-dessus est une version **dure** d'EM : les probabilités $r_{jc}$ y valent 0 ou 1.
>
> **Ce qu'il faut en retenir** : les points sans étiquette n'agissent que par le terme $\log p(x_j\mid\theta)$, c'est-à-dire par ce qu'ils disent de **la loi des $x$**. Ils ne peuvent aider **que si** cette loi contient de l'information sur la frontière entre classes.

### 8.1.3 Les quatre hypothèses qui permettent d'aider

La théorie et la pratique du semi-supervisé reposent sur quelques **hypothèses sur le monde**, jamais vérifiables à 100 % :

| Hypothèse | Énoncé en une phrase | Ce que ça autorise |
|---|---|---|
| **Lissage** (*smoothness*) | deux points **proches** dans une région **dense** ont probablement la même étiquette | propager une étiquette aux voisins |
| **Groupes** (*cluster*) | les points d'un **même groupe** partagent la même classe | étiqueter un groupe entier à partir d'un seul de ses points |
| **Basse densité** | la frontière entre classes passe par une région **peu peuplée** | déplacer la frontière vers les creux (notre exemple à la main) |
| **Variété** (*manifold*) | les données vivent près d'une surface de faible dimension, et ce sont les distances **le long de cette surface** qui comptent | utiliser un graphe de voisinage plutôt que la distance « à vol d'oiseau » |

Voyons-les au travail sur deux jeux de 300 points en deux dimensions. En haut, deux « lunes » entrelacées : les groupes sont nets, la frontière naturelle passe dans le creux. En bas, deux nuages qui **se chevauchent** : il n'y a pas de creux, la structure de $p(x)$ ne dit rien de plus que ce que disent les étiquettes. Dans les deux cas, on ne donne que **trois étiquettes par classe**.


![En haut, deux lunes entrelacées : avec trois étiquettes par classe, un modèle supervisé trace une frontière droite ; la propagation, qui s'appuie sur la forme des groupes, suit le creux entre les lunes. En bas, deux nuages qui se chevauchent : il n'y a pas de creux à exploiter, la propagation n'apporte rien. Les points colorés sont les six points étiquetés, les points gris sont les autres. Chaque ligne montre un tirage représentatif (dont le gain est le plus proche du gain moyen sur 20 tirages).](figures/ch08-hypotheses-lunes.png)

Sur 20 tirages différents des six étiquettes, la précision moyenne sur les lunes passe de **0,82** (supervisé) à **0,90** (propagation) : un gain net, qui vient de ce que la méthode a *vu* la forme des deux croissants. Sur les nuages qui se chevauchent, elle **ne bouge pas** (0,59 pour le supervisé, 0,57 pour la propagation, des différences très inférieures à l'écart-type d'un tirage à l'autre).

> ⚠️ **Le même algorithme, deux résultats opposés.** Rien, dans la méthode, ne l'a prévenue de ce qui allait se passer. C'est la **structure des données** qui décide. Avant de recourir au semi-supervisé, posez-vous toujours la question : *est-il plausible que la forme de $p(x)$ renseigne sur la frontière entre classes ?*

### 8.1.4 Quand ça aide, quand ça nuit

Il n'existe pas de « repas gratuit » : les données sans étiquette ne sont pas toujours une bonne affaire. Voici les situations à surveiller.

| Situation | Effet | Pourquoi |
|---|---|---|
| **L'hypothèse est vraie** (groupes nets, variété) | **gain** souvent important quand les étiquettes sont très rares | l'information de $p(x)$ est utile |
| **L'hypothèse est fausse** (classes qui se chevauchent, variables hétérogènes) | **aucun gain**, voire **perte** | la méthode « suit » une structure sans rapport avec les classes |
| **Les étiquettes disponibles sont déséquilibrées ou peu représentatives** | la méthode **amplifie** le défaut | elle étend ce qu'elle croit savoir à tous les voisins |
| **Les données sans étiquette viennent d'ailleurs** (autre période, autre population) | **perte** probable | $p(x)$ n'est plus celle du problème visé |
| **Un modèle sûr de lui à tort** (auto-apprentissage) | **dérive** | il se nourrit de ses propres erreurs (section 8.2.2) |

Un exemple chiffré du troisième cas, sur nos chiffres manuscrits. On tire 50 étiquettes, mais de façon **déséquilibrée** : le chiffre 0 reçoit six fois plus de chances d'être tiré que chacun des autres. En moyenne, 39 % des étiquettes sont alors des « 0 », contre 10 % attendus.


Avec ces étiquettes mal réparties, le modèle supervisé atteint **0,70** de précision ; la propagation (qui s'appuie sur le graphe de voisinage) reste robuste, à **0,89** ; mais l'**auto-apprentissage** *descend* à **0,65**, en dessous du supervisé : il prend ses propres préjugés pour des certitudes. Nous comprendrons le mécanisme en 8.2.2.

> 💡 **Règle pratique.** Si vous hésitez, commencez par la méthode **non supervisée** de votre choix (chapitre 3) : regardez si les groupes existent et s'ils ressemblent à vos classes sur le petit échantillon étiqueté. Si oui, le semi-supervisé a de bonnes chances d'aider ; sinon, passez directement à l'apprentissage actif (section 8.3), qui ne fait pas ce pari.

### 8.1.5 Évaluer à budget d'étiquettes fixé : la courbe d'apprentissage

La bonne façon de mesurer l'intérêt d'une méthode de ce chapitre est de tracer une **courbe d'apprentissage selon le budget d'étiquettes** : on fait varier le nombre $n_\ell$ d'étiquettes disponibles, et pour chacun on mesure la qualité sur un **jeu de test** étiqueté, tenu à l'écart. Le protocole est strict :

1. **Un jeu de test fixe**, tiré au hasard, jamais utilisé pour apprendre ni pour choisir quoi que ce soit (section 1.1). Ici : 450 images, **toutes** étiquetées.
2. **Un réservoir** dont on « cache » presque toutes les étiquettes (ici 1 347 images).
3. Pour chaque budget $n_\ell$ : tirer **plusieurs** ensembles d'étiquettes différents (ici 10, avec des graines fixées), car un seul tirage est trompeur quand $n_\ell$ est petit.
4. **Les mêmes étiquettes pour toutes les méthodes** : ainsi la comparaison est **appariée**, et la différence est due à la méthode et non à la chance du tirage.
5. Reporter **la moyenne et l'écart-type** (ou un intervalle) sur les tirages, pas une valeur unique.
6. **Aucun réglage fin** sur le jeu de test. Et attention : avec 10 étiquettes, on ne peut pas faire de validation croisée sérieuse. Si l'on garde des étiquettes pour régler un hyperparamètre, **elles comptent dans le budget**.

Voici la courbe du modèle **supervisé seul** (une régression logistique) sur les chiffres. C'est la référence à battre.


![Précision d'une régression logistique sur le jeu de test des chiffres manuscrits, selon le nombre d'images étiquetées (moyenne et écart-type sur 10 tirages ; échelle logarithmique en abscisse). La courbe monte très vite avec les premières étiquettes puis s'aplatit vers la valeur obtenue avec toutes les étiquettes.](figures/ch08-courbe-supervisee.png)

Trois lectures de cette courbe :

- **Elle est très raide au début.** Avec 10 étiquettes, la précision est de **0,43** ; avec 50, de **0,78** ; avec 100, de **0,87**. C'est dans ce régime que les méthodes de ce chapitre ont le plus à offrir.
- **Elle s'aplatit ensuite.** Avec 200 étiquettes, **0,93** ; avec les 1 347, **0,97**. Passé un certain budget, les étiquettes supplémentaires rapportent peu : l'apprentissage actif (8.3) cherche à *atteindre plus vite* ce plateau.
- **L'écart entre tirages est énorme à petit budget** : **± 0,08** à 10 étiquettes, contre ± 0,01 à 100. Sur nos dix tirages de 10 étiquettes, la précision va de **0,33** à **0,57** : un tirage isolé pourrait nous faire croire à n'importe quelle valeur dans cet intervalle. C'est pourquoi on **répète** les tirages.

> ✅ **À retenir.**
> - Le semi-supervisé utilise les points **sans étiquette** pour apprendre la forme de $p(x)$ ; l'actif choisit **quels points faire étiqueter**.
> - Les données sans étiquette n'aident que si $p(x)$ renseigne sur les classes : hypothèses de **lissage**, de **groupes**, de **basse densité**, de **variété**. Même méthode, même budget : gain sur des lunes entrelacées, rien sur des nuages qui se chevauchent.
> - Une méthode ne vaut que par rapport au **modèle supervisé entraîné sur les mêmes étiquettes**. Des étiquettes mal réparties peuvent faire **perdre** à une méthode ce qu'elle gagnait.
> - L'outil de mesure est la **courbe d'apprentissage selon le budget d'étiquettes** : jeu de test fixe, tirages répétés, **mêmes étiquettes** pour toutes les méthodes, moyenne et écart-type.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.1, exercices 8.1 à 8.3.


## 8.2 Auto-apprentissage et propagation d'étiquettes

Deux familles de méthodes concrètes exploitent les points sans étiquette. L'**auto-apprentissage** laisse le modèle étiqueter lui-même les cas dont il est sûr, puis s'entraîne dessus. La **propagation d'étiquettes** fait au contraire « couler » les étiquettes connues le long d'un graphe de similarité. Nous les construisons à la main, puis nous les mesurons sur nos deux jeux, avec les courbes d'apprentissage de la section 8.1.5.

### 8.2.1 L'auto-apprentissage

L'idée est celle du bon élève qui se corrige tout seul : on entraîne un premier modèle sur les rares étiquettes, on lui fait **prédire** les points sans étiquette, on garde les prédictions dont il est **très sûr**, on les ajoute au jeu d'entraînement comme si elles étaient vraies (on parle de **pseudo-étiquettes**), et on recommence.

> 📐 **Algorithme d'auto-apprentissage** (*self-training*), avec un seuil de confiance $\tau\in]0,1[$ :
> 1. Entraîner le modèle $f$ sur $\mathcal L$.
> 2. Calculer, pour chaque $x_j\in\mathcal U$, la classe prédite $\hat y_j$ et la confiance $p_j=\max_c P(c\mid x_j)$.
> 3. Pour chaque $j$ tel que $p_j\ge\tau$ : ajouter $(x_j,\hat y_j)$ à $\mathcal L$ et retirer $x_j$ de $\mathcal U$.
> 4. Recommencer à l'étape 1 jusqu'à ce qu'aucun point ne dépasse le seuil (ou qu'on ait atteint un nombre maximal de tours).

Le modèle de base peut être **n'importe quel** classifieur capable de donner des probabilités. Avec scikit-learn, c'est une enveloppe autour de ce modèle, et il suffit de passer le tableau complet avec les étiquettes partielles (convention `-1`, introduction du chapitre) :


```python
from sklearn.semi_supervised import SelfTrainingClassifier

base = LogisticRegression(max_iter=2000)
auto = SelfTrainingClassifier(base, threshold=0.9).fit(Xp, y_partiel)
seul = LogisticRegression(max_iter=2000).fit(Xp[indices_etiquetes], yp[indices_etiquetes])
print("auto-apprentissage :", round(auto.score(Xt, yt), 3), "| supervisé seul :", round(seul.score(Xt, yt), 3))
```
<!--sortie-->
```text
auto-apprentissage : 0.831 | supervisé seul : 0.831
```

Sur ce tirage de 50 étiquettes, l'auto-apprentissage fait **exactement aussi bien** que le modèle supervisé seul (0,831 des deux côtés) : il n'a rien apporté. Un seul tirage ne prouve rien, dans un sens comme dans l'autre. Mesurons sur 10 tirages, en faisant varier le seuil. Pour chaque seuil, nous indiquons aussi **combien** de pseudo-étiquettes ont été ajoutées et **quelle part était juste** (on la connaît, car nous avons caché les vraies étiquettes sans les perdre).


| Seuil $\tau$ | Précision sur le test | Pseudo-étiquettes ajoutées (moyenne) | Part des pseudo-étiquettes qui sont justes |
|---:|---:|---:|---:|
| 0,60 | 0,759 | 1 216 | 0,783 |
| 0,80 | 0,593 | 888 | 0,734 |
| 0,90 | 0,706 | 176 | 0,912 |
| 0,95 | 0,781 | 2 | 1,000 |
| 0,99 | 0,782 | 0 | (aucune) |

Le modèle supervisé seul, avec les mêmes 50 étiquettes, atteint **0,782**. Aucun seuil ne fait **mieux**. Les deux extrêmes sont instructifs :

- à $\tau=0{,}99$ et $\tau=0{,}95$, le modèle n'est jamais assez sûr de lui : presque aucune pseudo-étiquette n'est ajoutée, et le résultat est celui du supervisé seul (**0,78**) ;
- à $\tau=0{,}6$ ou $0{,}8$, le modèle ajoute **plusieurs centaines** de pseudo-étiquettes dont **environ un cinquième à un quart sont fausses** (0,78 et 0,73 justes) : il apprend sur ses propres erreurs.

Le seuil intermédiaire de 0,90 est le plus dangereux de façon trompeuse : 91 % des 176 pseudo-étiquettes sont justes, mais celles qui sont fausses sont **faussement confiantes**, et la précision finale baisse tout de même à 0,71.

### 8.2.2 Pourquoi l'auto-apprentissage peut s'auto-tromper

Ce qui précède n'est pas un accident de réglage : c'est le **biais de confirmation** de la méthode. Trois mécanismes s'additionnent.

1. **Une confiance qui n'est pas une probabilité.** Un modèle logistique entraîné sur 50 images en 64 dimensions est typiquement **trop sûr de lui** : il annonce 0,95 là où il se trompe un cas sur cinq. Un seuil de 0,9 sur une probabilité mal calibrée (section 5.2) n'est pas un seuil de 90 % de réussite.
2. **L'erreur devient une donnée.** Une fausse pseudo-étiquette entre dans le jeu d'entraînement avec le même poids qu'une vraie. Le tour suivant, le modèle s'y adapte, et il devient *plus* sûr de lui sur des points voisins : l'erreur se **renforce** au lieu de se corriger.
3. **La classe déjà majoritaire s'étend.** Reprenons le jeu d'étiquettes déséquilibré de 8.1.4 (39 % de « 0 » parmi les étiquettes, contre 10 % dans la population). Regardons de quelles classes sont les pseudo-étiquettes ajoutées.


En moyenne, **88 %** des pseudo-étiquettes ajoutées sont des « 0 » (et 85 % de ces points sont réellement des 0 : le modèle ne se trompe pas beaucoup sur eux), alors que les « 0 » ne forment que 10 % des images. Les points que le modèle juge sûrs sont, de très loin, ceux de la classe qu'il a le plus vue : il l'ajoute massivement à son jeu d'entraînement, le déséquilibre initial **s'aggrave** (c'est l'explication la plus plausible, que nous n'avons pas isolée par une expérience dédiée), et la précision tombe à 0,65 (section 8.1.4).

> ⚠️ **Quand l'auto-apprentissage peut fonctionner.** Il a ses bons cas : quand le modèle initial est déjà **bon** (de l'ordre de 90 % de précision) et que les groupes sont bien séparés, ajouter ses cas faciles élargit un peu la base sans la polluer. Mais c'est exactement le cas où l'on a le *moins* besoin du semi-supervisé. Avec très peu d'étiquettes et un modèle médiocre, il est le plus dangereux.

Quelques garde-fous usuels : un seuil **élevé** ; une probabilité **calibrée** (section 5.2) ; ajouter des pseudo-étiquettes **par classe** en proportion de leur fréquence attendue plutôt que par seuil global ; ne jamais s'évaluer sur les pseudo-étiquettes ; et surtout **comparer au supervisé seul sur les mêmes étiquettes**.

### 8.2.3 Le co-apprentissage

Le **co-apprentissage** (*co-training*) est une variante qui limite le biais de confirmation en faisant s'entraider **deux** modèles. On suppose que chaque observation possède **deux « vues »** $x=(x^{(1)},x^{(2)})$, c'est-à-dire deux jeux de variables, et que :

1. **chaque vue suffit** à prédire la classe (chacune porte assez d'information pour un modèle correct) ;
2. les deux vues sont **indépendantes sachant la classe**.

On entraîne un modèle par vue ; chacun étiquette les points sans étiquette dont il est le plus sûr, et **ces pseudo-étiquettes servent à entraîner l'autre**. L'idée est qu'une erreur du premier modèle est, par indépendance, un cas « ordinaire » pour le second, qui peut la corriger.

L'exemple de référence est celui d'une page web, décrite par son **texte** et par les **liens qui pointent vers elle**. Pour la boutique, on pourrait imaginer décrire un client par son **comportement d'achat** d'un côté et par son **profil déclaré** (âge, ville) de l'autre, si chacun suffisait à prédire un attribut.

Les conditions sont **exigeantes** et rarement réunies. Sur nos chiffres manuscrits, on peut tenter de prendre comme vues la **moitié haute** et la **moitié basse** de l'image : aucune des deux moitiés ne suffit à elle seule, et elles sont fortement dépendantes (elles décrivent le même tracé). Le cahier propose cet essai (application 8.4) ; il se solde par un **échec instructif**, bien pire que le supervisé seul. C'est la leçon à retenir : une méthode dont les hypothèses ne sont pas vérifiées n'est pas « un peu moins efficace », elle peut être franchement nuisible.

### 8.2.4 Propager les étiquettes le long d'un graphe

Changeons de point de vue. Au lieu d'un modèle qui se prédit lui-même, construisons un **graphe de similarité** entre *tous* les points (étiquetés ou non) et laissons les étiquettes **se diffuser** de proche en proche, comme de l'encre dans un réseau de canaux.

**Le graphe.** Chaque observation est un **nœud**. On relie deux nœuds proches : par exemple chaque point à ses $k$ plus proches voisins. On obtient une matrice de **poids** $W$ ($W_{ij}>0$ si $i$ et $j$ sont voisins, 0 sinon, $W$ symétrique), les **degrés** $d_i=\sum_jW_{ij}$, et la matrice normalisée
$$S=D^{-1/2}\,W\,D^{-1/2},\qquad S_{ij}=\frac{W_{ij}}{\sqrt{d_i\,d_j}}.$$

**La diffusion.** Notons $Y$ la matrice des étiquettes ($n\times c$) : la ligne $i$ vaut le vecteur indicateur de la classe si $i$ est étiqueté, et zéro sinon. On part de $F^{(0)}=Y$ et on répète
$$F^{(t+1)}=\alpha\,S\,F^{(t)}+(1-\alpha)\,Y,\qquad \alpha\in]0,1[.$$
À chaque tour, chaque nœud reçoit une moyenne pondérée des scores de ses voisins (le terme $\alpha SF$), tout en gardant une part $(1-\alpha)$ de son étiquette d'origine (ce qui empêche les étiquettes connues de se diluer). À la fin, chaque nœud reçoit la classe de **plus grand score** : $\hat y_i=\arg\max_c F_{ic}$. C'est l'algorithme de **propagation** (ou d'*étalement*, *label spreading*) de Zhou et coll.

> 📐 **Pourquoi cela converge, et vers quoi.** Le point clé est que les valeurs propres de $S$ sont dans $[-1,1]$. En effet, $S=D^{-1/2}WD^{-1/2}$ est **semblable** à $P=D^{-1}W$ (puisque $S=D^{1/2}PD^{-1/2}$), et $P$ est une matrice **stochastique** (ses lignes sont positives et somment à 1), dont les valeurs propres sont de module au plus 1. Le rayon spectral de $\alpha S$ est donc au plus $\alpha<1$. En dépliant la récurrence :
> $$F^{(t)}=(\alpha S)^tY+(1-\alpha)\sum_{s=0}^{t-1}(\alpha S)^sY\ \xrightarrow[t\to\infty]{}\ F^*=(1-\alpha)\,(I-\alpha S)^{-1}\,Y,$$
> car $(\alpha S)^t\to0$ et la série de Neumann $\sum_s(\alpha S)^s$ converge vers $(I-\alpha S)^{-1}$. **On n'a donc pas besoin d'itérer** : une résolution de système linéaire suffit.
>
> **Ce que l'on minimise.** $F^*$ est l'unique minimiseur de
> $$J(F)=\tfrac12\sum_{i,j}W_{ij}\Bigl\|\tfrac{F_i}{\sqrt{d_i}}-\tfrac{F_j}{\sqrt{d_j}}\Bigr\|^2+\mu\,\|F-Y\|_F^2,\qquad \mu=\tfrac{1-\alpha}{\alpha}.$$
> Le premier terme est un terme de **lissage** : il est petit quand deux nœuds proches ont des scores proches (c'est l'hypothèse de lissage de 8.1.3). Le second est un terme de **fidélité** : il demande de ne pas trop s'éloigner des étiquettes connues. En développant, le premier terme vaut $\operatorname{tr}\bigl(F^\top(I-S)F\bigr)$, et annuler le gradient donne $(I-S)F+\mu(F-Y)=0$, soit $F=\frac{\mu}{1+\mu}\bigl(I-\frac{1}{1+\mu}S\bigr)^{-1}Y$, ce qui est exactement $F^*$ avec $\alpha=1/(1+\mu)$.

**Un exemple à la main : six nœuds.** Deux triangles reliés par une seule arête : les nœuds $1,2,3$ d'un côté, $4,5,6$ de l'autre, et l'arête $3$–$4$ au milieu. Le nœud 1 est étiqueté **A**, le nœud 6 est étiqueté **B**, les quatre autres ne le sont pas. Les degrés sont $d=(2,2,3,3,2,2)$. Les poids normalisés dont nous avons besoin sont

$$S_{12}=\frac1{\sqrt{2\cdot2}}=0{,}5,\qquad S_{13}=S_{23}=\frac1{\sqrt{2\cdot3}}\approx0{,}408,\qquad S_{34}=\frac1{\sqrt{3\cdot3}}=\tfrac13,$$

et symétriquement de l'autre côté ($S_{56}=0{,}5$, $S_{45}=S_{46}\approx0{,}408$). Prenons $\alpha=0{,}5$. Calculons le premier tour pour la colonne de la classe A, en partant de $F^{(0)}_A=(1,0,0,0,0,0)$ :

- nœud 1 : $0{,}5\cdot(S_{12}\cdot0+S_{13}\cdot0)+0{,}5\cdot1=0{,}5$ ;
- nœud 2 : $0{,}5\cdot S_{21}\cdot1+0=0{,}5\cdot0{,}5=0{,}25$ ;
- nœud 3 : $0{,}5\cdot S_{31}\cdot1=0{,}5\cdot0{,}408\approx0{,}204$ ;
- nœuds 4, 5, 6 : aucun voisin n'a encore de score A : $0$.

Le score A est passé du nœud 1 à ses deux voisins, **atténué** par la distance. Au deuxième tour, il atteint le nœud 4 (à travers l'arête $3$–$4$), toujours très faiblement. Les deux colonnes se calculent ensemble ; en laissant converger (ou en résolvant directement $F^*$), on obtient :


| Nœud | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Score A | 0,577 | 0,177 | 0,159 | 0,030 | 0,008 | 0,008 |
| Score B | 0,008 | 0,008 | 0,030 | 0,159 | 0,177 | 0,577 |
| **Classe** | A | A | A | B | B | B |

![Propagation d'étiquettes sur six nœuds : deux triangles reliés par une arête. Seuls les nœuds 1 (classe A) et 6 (classe B) sont étiquetés. Les scores finaux (A et B) sont indiqués sous chaque nœud ; l'intensité de la couleur suit le score le plus élevé.](figures/ch08-propagation-graphe.png)

La classe attribuée à chaque nœud correspond à la **forme du graphe** : les trois nœuds du triangle de gauche reçoivent A, ceux de droite reçoivent B. Remarquez que le nœud 3, voisin direct du nœud 4 et donc exposé aux deux classes, penche malgré tout (0,159 contre 0,030) du côté de son triangle : l'étiquette s'est propagée **à l'intérieur** des groupes bien plus qu'**entre** eux, parce qu'il y a beaucoup de liens dans chaque triangle et un seul au milieu. C'est exactement l'hypothèse des groupes de 8.1.3.

### 8.2.5 La propagation sur les chiffres manuscrits

Passons à la pratique. Pour les chiffres, le graphe relie chaque image à ses **7 plus proches voisins** (distance euclidienne entre les 64 pixels). Voici l'appel, comme pour l'auto-apprentissage :

```python
from sklearn.semi_supervised import LabelSpreading

prop = LabelSpreading(kernel="knn", n_neighbors=7, alpha=0.2).fit(Xp, y_partiel)
print("propagation :", round(prop.score(Xt, yt), 3), "| auto-apprentissage :", round(auto.score(Xt, yt), 3), "| supervisé seul :", round(seul.score(Xt, yt), 3))
```
<!--sortie-->
```text
propagation : 0.949 | auto-apprentissage : 0.831 | supervisé seul : 0.831
```

Sur ce même tirage de 50 étiquettes, la propagation atteint **0,95** de précision, contre 0,83 pour le supervisé seul et pour l'auto-apprentissage. Un seul tirage ne prouve rien : voici la courbe d'apprentissage complète, avec les **mêmes étiquettes** pour les trois méthodes, 10 tirages par budget.


![Précision sur le jeu de test des chiffres manuscrits selon le nombre d'étiquettes, pour le modèle supervisé seul, l'auto-apprentissage et la propagation d'étiquettes (moyenne et écart-type sur 10 tirages, mêmes étiquettes pour les trois méthodes). La propagation domine nettement à petit budget ; l'auto-apprentissage ne fait pas mieux que le supervisé.](figures/ch08-courbes-semi.png)

| Étiquettes | 10 | 20 | 50 | 100 | 200 |
|---|---:|---:|---:|---:|---:|
| Supervisé seul | 0,429 | 0,577 | 0,782 | 0,874 | 0,927 |
| Auto-apprentissage ($\tau=0{,}9$) | 0,429 | 0,577 | 0,706 | 0,840 | 0,923 |
| **Propagation** | **0,540** | **0,779** | **0,913** | **0,940** | **0,966** |

Trois constats :

- Avec **20 étiquettes**, la propagation gagne **20 points** de précision sur le modèle supervisé (0,78 contre 0,58) ; avec 50, **13 points**. C'est considérable, et le gain est **plus grand là où la courbe supervisée est la plus raide** (8.1.5).
- Le gain **diminue avec le budget** : à 200 étiquettes, 4 points. Quand on a beaucoup d'étiquettes, la structure du graphe n'apprend plus grand-chose de neuf.
- La propagation fait mieux que le supervisé dans **les 10 tirages, à chacun des cinq budgets**.
- L'auto-apprentissage ne fait **jamais mieux** que le supervisé : il est à égalité aux petits budgets (le modèle n'est presque jamais sûr de lui) puis moins bon.

**Transductif ou inductif ?** Avec 50 étiquettes, la précision de la propagation sur les points sans étiquette *du réservoir* (c'est l'usage **transductif**) et sur le jeu de test (l'usage **inductif**, via `predict`) sont très voisines : respectivement 0,90 et 0,91 en moyenne. Pour un modèle destiné à prédire de nouveaux clients demain, il faut prévoir **de re-propager** (ou de remplacer la propagation par un classifieur entraîné sur ses étiquettes) : le graphe n'existe que sur les points qu'il contient.


**Les réglages comptent, surtout le nombre de voisins.** Avec 20 étiquettes, voici la précision selon $k$ (nombre de voisins) et $\alpha$ :

```text
           α = 0,2  α = 0,9
voisins k                  
3            0.290    0.309
7            0.779    0.780
15           0.785    0.780
30           0.775    0.754
60           0.739    0.685
```


- **$k=3$ est catastrophique** (0,29). Le graphe de scikit-learn est **orienté** : chaque image ne regarde que ses $k$ voisins, et une étiquette ne peut atteindre une image que si celle-ci compte un point déjà atteint parmi ses $k$ plus proches voisins. Avec $k=3$ et 20 étiquettes, **86 %** des images non étiquetées ne reçoivent **aucun score** (13 % avec $k=7$, 0,5 % avec $k=15$) : la méthode ne sait plus que dire. (Un graphe **symétrisé**, où l'on relie deux images dès que l'une est voisine de l'autre, ne souffre pas de ce défaut : voir l'application 8.3 du cahier.)
- **De $k=7$ à $k=30$**, le résultat est stable et bon (entre 0,75 et 0,79). C'est la zone où le graphe est connexe sans mélanger les classes.
- **À $k=60$**, les voisins deviennent trop lointains : des liens traversent les frontières entre chiffres et la précision recule (0,74 pour $\alpha=0{,}2$, 0,69 pour $\alpha=0{,}9$).
- Le paramètre $\alpha$ compte peu tant que $k$ est raisonnable.

> ⚠️ **Le coût.** Un graphe à noyau gaussien sur $n$ points est une matrice $n\times n$ dense : pour $n=100\,000$, c'est $10^{10}$ nombres, hors de portée. Le noyau **à $k$ plus proches voisins** (utilisé ici) est **creux** et passe à l'échelle. Quant au choix de $k$, on ne peut pas le régler par validation sur 20 étiquettes : on le choisit par principe (graphe connexe, $k$ de l'ordre de 7 à 15) et on le contrôle avec le diagnostic de la section suivante.

### 8.2.6 Quand le graphe ne dit rien : les clients de la boutique

La propagation brille sur les chiffres. Qu'en est-il sur les **clients de la boutique**, où l'on veut prédire la résiliation à 90 jours avec très peu d'étiquettes ? Même protocole : étiquettes tirées avec leurs proportions (14 % de résiliations ; au moins 2 positifs), mesure par l'**aire sous la courbe ROC** (AUC, section 5.1) puisque les classes sont déséquilibrées.


| Étiquettes | Supervisé (AUC, test) | Auto-apprentissage (AUC, test) | Supervisé (AUC, points atteints) | **Propagation** (AUC, points atteints) | Part du réservoir atteinte |
|---:|---:|---:|---:|---:|---:|
| 30 | 0,719 | 0,718 | 0,705 | **0,510** | 74 % |
| 100 | 0,734 | 0,731 | 0,727 | **0,527** | 96 % |
| 300 | 0,791 | 0,792 | 0,787 | **0,577** | 100 % |

(La propagation est évaluée sur les clients non étiquetés que les étiquettes ont atteints, avec le supervisé évalué sur ces mêmes clients pour la comparaison : il y est à peu près identique à son résultat sur le test.)

Le verdict est net : l'auto-apprentissage **ne change rien**, et la propagation est **à peine meilleure que le hasard** (AUC de 0,51 à 0,58, pour 0,5 d'un tirage au sort) là où le supervisé atteint 0,71 à 0,79. Pourquoi ? Parce que l'hypothèse de 8.1.3 est fausse ici. Un diagnostic simple le montre : **à quel point les voisins d'un point partagent-ils son étiquette ?**


| | Voisins de même étiquette | Part attendue au hasard |
|---|---:|---:|
| **Chiffres** (7 voisins) | **96,9 %** | 10,0 % |
| **Clients** (7 voisins) | 80,5 % | 75,9 % |

Sur les chiffres, **97 %** des 7 plus proches voisins d'une image portent le même chiffre : le graphe est presque parfaitement « propre ». Sur les clients, **80,5 %** seulement, à peine plus que les **75,9 %** qu'on obtiendrait en choisissant des voisins au hasard (puisque 86 % des clients ne résilient pas). Parmi les clients qui résilient, 27 % seulement de leurs voisins résilient aussi (pour un taux de base de 14 %) : le lien existe, mais il est faible. La distance entre deux clients, calculée sur 49 variables (dont 34 colonnes indicatrices de villes, de canaux, d'appareils et de catégories) de natures très différentes, **ne reflète pas ce qui fait résilier** : un seuil sur la récence, une interaction entre tickets de support et retours, c'est-à-dire des seuils et des interactions que les arbres du chapitre 2 savent capturer, mais pas une distance Le graphe relie des clients qui se ressemblent *en apparence*, pas des clients qui se ressemblent *par leur risque*.

> 💡 **Un test à faire avant de propager.** Même avec peu d'étiquettes, on peut estimer ce taux d'**homophilie** : parmi les points *étiquetés* qui sont voisins l'un de l'autre, quelle part partage la même étiquette ? Comparez-le à la part attendue au hasard. S'il est proche, ne comptez pas sur la propagation. Une autre piste est d'apprendre **d'abord** une représentation adaptée (par exemple un modèle supervisé sur les étiquettes disponibles, puis un graphe construit sur ses sorties), mais cela sort du cadre de ce chapitre.

> ✅ **À retenir.**
> - L'**auto-apprentissage** ajoute les pseudo-étiquettes dont le modèle est sûr. Avec peu d'étiquettes et un modèle médiocre, il se confirme dans ses erreurs et **ne bat pas** le supervisé seul (chiffres, 50 étiquettes : jamais mieux que 0,78).
> - Les erreurs **se renforcent** (biais de confirmation) ; une classe déjà majoritaire s'étend. Garde-fous : seuil élevé, probabilités calibrées, comparaison systématique au supervisé sur les mêmes étiquettes.
> - Le **co-apprentissage** demande deux vues suffisantes et indépendantes : condition rarement réunie.
> - La **propagation d'étiquettes** diffuse les étiquettes sur un graphe de similarité ; elle se calcule en fermé, $F^*=(1-\alpha)(I-\alpha S)^{-1}Y$, et minimise lissage + fidélité. Sur les chiffres, **+20 points** à 20 étiquettes ; le réglage de $k$ est critique ($k=3$ morcelle le graphe).
> - Elle suppose que **les voisins se ressemblent par la classe** : sur les clients (80,5 % de voisins de même étiquette contre 75,9 % au hasard), elle échoue. **Mesurez l'homophilie avant de propager.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.2 à 8.5, exercices 8.4 à 8.6.


## 8.3 Apprentissage actif

L'apprentissage semi-supervisé exploite ce qu'on possède déjà. L'**apprentissage actif** pose l'autre question : *puisqu'il faut payer pour chaque étiquette, lesquelles acheter ?* Au lieu de faire étiqueter des exemples tirés au hasard, on laisse le **modèle choisir** ceux dont il a le plus à apprendre.

### 8.3.1 L'idée et la boucle

Imaginez un élève qui prépare un examen avec un professeur disponible une heure. Un élève passif écoute ce que le professeur choisit de dire. Un élève **actif** pose les questions sur ce qu'il ne comprend pas encore. Pour le même temps, il apprend plus vite. L'apprentissage actif applique cette idée à un modèle : il demande l'étiquette des points qui, croit-il, lui apprendront le plus.

On distingue trois cadres ; nous travaillerons dans le premier, le plus courant :

| Cadre | Principe | Exemple |
|---|---|---|
| **Par réservoir** (*pool-based*) | on dispose d'un grand ensemble non étiqueté ; à chaque tour, on choisit dans cet ensemble ce qu'on fait étiqueter | les 9 000 clients dont on ignore le comportement futur |
| **En flux** (*stream-based*) | les points arrivent un à un ; on décide à la volée de demander ou non leur étiquette | des transactions qui défilent |
| **Par requêtes synthétiques** | le modèle *invente* le point dont il veut l'étiquette | rarement possible : un humain doit savoir étiqueter un point qui n'existe pas |

> 📐 **La boucle d'apprentissage actif** (par réservoir, par lots de $b$ points) :
> 1. Choisir un petit **jeu initial** et le faire étiqueter ; entraîner un modèle $f$.
> 2. Calculer, pour chaque point $x$ non étiqueté, un **score d'utilité** $u(x)$ (nous en voyons plusieurs en 8.3.2 à 8.3.4).
> 3. Faire étiqueter les $b$ points de **plus grand score** ; les ajouter au jeu étiqueté.
> 4. Réentraîner $f$. Si le budget n'est pas épuisé, retourner à l'étape 2.

Tout l'art est dans le choix du score $u$. Pour la stratégie de la marge (8.3.2), l'étape 2 se résume à quelques lignes :

```python
P = modele.predict_proba(X_libres)                  # probabilités du modèle sur les points non étiquetés
tri = np.sort(P, axis=1)
marge = tri[:, -1] - tri[:, -2]                     # écart entre les deux classes les plus probables
a_demander = libres[np.argsort(marge)[:10]]         # les 10 points sur lesquels le modèle hésite le plus
```

> ⚠️ **Deux précautions dès le départ.** Un modèle appris sur des points *choisis* n'est plus appris sur un échantillon représentatif : cela a des conséquences sur la mesure de sa qualité et sur ses probabilités (8.3.6). Et au début, un modèle presque ignorant ne sait pas bien ce qui l'informerait : c'est le problème du démarrage à froid (8.3.7).

### 8.3.2 Mesurer l'incertitude

Le critère le plus naturel : demander les points sur lesquels le modèle **hésite**. Pour un point $x$, le modèle donne des probabilités $P(c\mid x)$ pour chaque classe $c$. Trois façons de mesurer l'hésitation :

| Critère | Formule (grand = plus incertain) | Idée |
|---|---|---|
| **Confiance minimale** (*least confidence*) | $1-\max_cP(c\mid x)$ | la meilleure classe est-elle peu probable ? |
| **Marge** | $-\bigl(P(c_1\mid x)-P(c_2\mid x)\bigr)$, où $c_1,c_2$ sont les deux classes les plus probables | le modèle hésite-t-il **entre deux** classes ? |
| **Entropie** | $-\sum_cP(c\mid x)\ln P(c\mid x)$ | les probabilités sont-elles **étalées** sur toutes les classes ? |

Pour deux classes, les trois critères sont **équivalents** : ils classent les points dans le même ordre (le plus incertain est celui dont la probabilité est la plus proche de $1/2$). Avec trois classes ou plus, ils peuvent **diverger**. Voici trois candidats à étiqueter, pour un problème à trois classes :

| Candidat | Probabilités | $1-\max$ | Écart entre les deux meilleures | Entropie |
|---|---|---:|---:|---:|
| **a** | $(0{,}50;\ 0{,}45;\ 0{,}05)$ | 0,50 | **0,05** | 0,856 |
| **b** | $(0{,}40;\ 0{,}30;\ 0{,}30)$ | **0,60** | 0,10 | **1,089** |
| **c** | $(0{,}60;\ 0{,}20;\ 0{,}20)$ | 0,40 | 0,40 | 0,950 |

(Par exemple, pour le candidat a : $-\bigl(0{,}5\ln0{,}5+0{,}45\ln0{,}45+0{,}05\ln0{,}05\bigr)=0{,}347+0{,}359+0{,}150=0{,}856$.) Les trois critères donnent **trois classements différents** :

- la **confiance minimale** met b en premier (sa meilleure classe n'a que 0,40), puis a, puis c ;
- la **marge** met **a** en premier (le modèle hésite quasiment à pile ou face entre deux classes : 0,50 contre 0,45), puis b, puis c ;
- l'**entropie** met b en premier (probabilités très étalées), puis c, puis a : elle juge le candidat a *moins* incertain que c, parce que la troisième classe est quasi exclue.


Lequel choisir ? La **marge** vise précisément la **frontière de décision** : un point dont deux classes sont à égalité est exactement un point qui déplacerait la frontière si on connaissait sa vraie classe. Quand il y a beaucoup de classes (10 chiffres), l'entropie peut au contraire être élevée pour un point que le modèle sait assigner à deux ou trois candidats parmi dix : une partie de l'étiquette « achetée » est gaspillée sur des classes sans rapport. Nous le vérifierons en 8.3.5.

### 8.3.3 Le comité de modèles

Une autre façon de repérer un point utile : **demander l'avis de plusieurs modèles** et regarder s'ils se disputent. C'est la stratégie du **comité** (*query by committee*).

On construit un comité de $M$ modèles (ici $M=5$), tous entraînés sur le **jeu étiqueté actuel**, mais rendus différents : chacun est appris sur un **rééchantillonnage avec remise** du jeu étiqueté (bootstrap, volume I, section 3.3.5). Chaque modèle **vote** pour une classe. On mesure le **désaccord** par l'**entropie du vote** : si $v_c$ est la part des modèles qui votent pour la classe $c$, le score est $-\sum_cv_c\ln v_c$.

Pour un comité de cinq modèles et deux classes :

| Répartition des votes | Part des votes | Entropie du vote |
|---|---|---:|
| 5 contre 0 | $(1;\ 0)$ | 0 |
| 4 contre 1 | $(0{,}8;\ 0{,}2)$ | 0,500 |
| 3 contre 2 | $(0{,}6;\ 0{,}4)$ | 0,673 |

L'unanimité donne un score nul ; la division la plus équilibrée, le plus grand. On fait donc étiqueter les cas qui **départagent** les modèles encore plausibles : en réduisant le nombre de modèles compatibles avec les données, chaque étiquette est utile.

Le comité a un **avantage** sur la marge : il mesure l'incertitude *du modèle* (ce qu'il ne sait pas, parce qu'il manque de données) et non seulement l'incertitude *des données* (un point intrinsèquement ambigu, dont aucune étiquette ne réduira le doute). Son **coût** : $M$ entraînements par tour au lieu d'un.

### 8.3.4 Densité et représentativité

Les critères d'incertitude ont un défaut connu : ils peuvent désigner des **valeurs aberrantes**. Un point très atypique, loin de toutes les autres données, rend le modèle perplexe ; mais l'étiqueter n'apprend presque rien sur les cas courants, qui forment l'essentiel de ce que l'on veut prédire.

Pour limiter ce risque, on pondère l'incertitude par la **densité** : la valeur d'un point est son incertitude *multipliée* par sa ressemblance moyenne avec le reste du réservoir. Un point à la fois **incertain** et **typique** est le meilleur candidat :
$$u(x)=\underbrace{H(x)}_{\text{incertitude}}\times\Bigl(\underbrace{\tfrac1n\sum_{x'}\operatorname{sim}(x,x')}_{\text{densité}}\Bigr)^{\beta}.$$
Ici, la similarité est le cosinus de l'angle entre deux vecteurs, et $\beta=1$. Une autre famille de critères, que nous ne calculerons pas, vise à **estimer directement la réduction de l'erreur** que procurerait chaque étiquette (*expected error reduction*) : très coûteuse, car elle impose de réentraîner le modèle pour chaque point candidat et chaque étiquette possible.

> 💡 **Représentatif ou informatif ?** L'**incertitude** cherche les points *informatifs* (qui déplaceraient la frontière) ; la **densité** cherche les points *représentatifs* (qui ressemblent à la masse). Aucun des deux n'est suffisant seul. En pratique on les combine, ou l'on alterne : un tour sur deux, quelques points tirés au hasard pour garder un contact avec la distribution réelle.

### 8.3.5 Comparer les stratégies

Comparons six stratégies sur les **chiffres manuscrits**, avec le protocole de 8.1.5 : le même jeu initial de 10 images tirées au hasard pour toutes les stratégies, 10 tirages différents, lots de 10 images, jusqu'à 150 étiquettes, précision mesurée sur le jeu de test de 450 images. Le modèle est la régression logistique.


![Précision sur le jeu de test des chiffres manuscrits selon le nombre d'étiquettes demandées, pour six stratégies de choix (moyenne sur 10 tirages ; bandes : écart-type pour le tirage au hasard et pour la marge). La marge domine nettement ; l'entropie et l'entropie pondérée par la densité font moins bien que le tirage au hasard.](figures/ch08-actif-chiffres.png)

| Stratégie | 30 étiquettes | 60 | 100 | 150 | Premier budget où la précision moyenne atteint 0,90 |
|---|---:|---:|---:|---:|---:|
| Aléatoire | 0,673 | 0,815 | 0,890 | 0,919 | 130 |
| Incertitude | 0,607 | 0,808 | 0,901 | 0,938 | 100 |
| **Marge** | **0,744** | **0,886** | **0,928** | **0,950** | **80** |
| Entropie | 0,576 | 0,755 | 0,864 | 0,917 | 140 |
| Comité | 0,655 | 0,833 | 0,898 | 0,931 | 110 |
| Entropie × densité | 0,527 | 0,718 | 0,842 | 0,901 | 150 |

Que lit-on ?

- **La marge est la grande gagnante.** À 60 étiquettes, elle dépasse le tirage au hasard de **7 points** (0,886 contre 0,815), et elle le dépasse dans **les 10 tirages**. Elle atteint 0,90 de précision avec **80 étiquettes**, contre **130** pour le tirage au hasard : **38 % d'étiquettes en moins**. Elle est aussi plus **régulière** : l'écart-type d'un tirage à l'autre à 60 étiquettes est de 0,014, contre 0,048 pour le tirage au hasard.
- **Plusieurs stratégies sont pires que le hasard au début.** Avec 30 étiquettes, la confiance minimale (0,607), l'entropie (0,576) et l'entropie pondérée par la densité (0,527) sont **en dessous** du tirage aléatoire (0,673). La confiance minimale passe devant le hasard aux points de contrôle de 100 et 150 étiquettes (0,901 contre 0,890, puis 0,938 contre 0,919) ; l'entropie ne le dépasse jamais dans cette fenêtre (0,917 contre 0,919 à 150).
- **Le comité se place entre les deux** : un peu meilleur que le hasard à 60 étiquettes (0,833 contre 0,815), mais loin de la marge, au prix de cinq entraînements par tour.
- **La densité n'aide pas ici.** L'entropie pondérée par la densité est la **moins bonne** de toutes. Les chiffres manuscrits n'ont presque pas de valeurs aberrantes : le garde-fou coûte plus qu'il ne rapporte. Sur des données bruitées, le verdict pourrait s'inverser.

> ⚠️ **Pourquoi un critère raisonnable peut-il perdre contre le hasard ?** Au début, le modèle n'a vu que quelques images de quelques chiffres. Ses « incertitudes » sont celles d'un modèle ignorant : l'entropie sur dix classes, par exemple, est élevée pour *presque* toute image qui n'est pas proche d'un exemple connu, c'est-à-dire pour beaucoup d'images très différentes, sans que cela dise lesquelles seraient les plus instructives. C'est une explication plausible, que ces expériences ne démontrent pas ; ce qui est établi, c'est le classement, mesuré sur les mêmes tirages. Retenez surtout qu'**il faut mesurer** : aucune stratégie n'est sûre de battre le hasard.

### 8.3.6 Le piège du biais d'échantillonnage

Passons aux **clients de la boutique**, où l'on cherche à prédire la résiliation à 90 jours. On démarre avec 40 étiquettes (tirées en respectant la proportion de résiliations, au moins 2), par lots de 20 jusqu'à 400. Le modèle est une régression logistique ; la qualité est mesurée par l'AUC sur un jeu de test de 3 000 clients tirés au hasard.


![À gauche : AUC sur le jeu de test selon le nombre d'étiquettes, pour quatre stratégies sur les clients de la boutique (moyenne de 10 tirages). À droite : part de résiliations parmi les clients étiquetés ; le tirage au hasard reste au taux réel de 14 %, les stratégies actives s'en éloignent beaucoup.](figures/ch08-actif-clients.png)

Deux enseignements.

**1. L'apprentissage actif aide, modestement.** À 400 étiquettes, l'AUC est de **0,845** pour la confiance minimale et **0,843** pour le comité, contre **0,827** au hasard. Pour atteindre 0,80 d'AUC, il faut **200** étiquettes au hasard mais **140** avec l'une ou l'autre stratégie active (30 % de moins). La densité, ici encore, n'aide pas (180 étiquettes).

**2. Mais le jeu étiqueté n'est plus représentatif, et ses probabilités non plus.** Le graphique de droite le montre : parmi les 400 clients étiquetés par la stratégie d'incertitude, **38 %** résilient, alors que le taux réel est de **14 %**. Normal : en demandant les clients « frontière », on est tombé sur beaucoup de cas intermédiaires. Le tirage au hasard, lui, reste fidèle (14,5 %). Conséquence concrète sur les **probabilités prédites** : la probabilité moyenne de résiliation prédite sur le jeu de test est de **0,078** pour le modèle actif, alors que la vérité est **0,14** : le modèle **sous-estime** le risque de 44 %. Celui entraîné au hasard donne 0,142. L'ordre des clients (l'AUC) est meilleur ; les **niveaux** de probabilité, eux, sont faux.

> ⚠️ **Trois règles d'hygiène.**
> 1. **Le jeu de test doit être tiré au hasard** et n'avoir *jamais* été utilisé pour choisir des points. Évaluer un modèle actif sur des points actifs serait doublement trompeur.
> 2. **On ne peut pas estimer un taux (de résiliation, de fraude…) sur le jeu étiqueté.** Celui-ci a été **choisi** pour être atypique.
> 3. **Si l'on a besoin de probabilités fiables**, il faut les **recalibrer** (section 5.2) sur un petit échantillon étiqueté **tiré au hasard**.

Essayons la règle 3 : on fait étiqueter **300 clients de plus, au hasard**, et l'on recale les probabilités du modèle par une régression logistique à une variable (« mise à l'échelle de Platt », section 5.2). Après recalibrage, la probabilité moyenne du modèle actif passe de **0,078 à 0,141** (le taux réel est 0,14), et son **score de Brier** (l'erreur quadratique moyenne des probabilités, section 5.1) de **0,1040 à 0,0920**. Le modèle tiré au hasard passe de 0,1014 à 0,0959 : le modèle actif, une fois recalibré, est le meilleur des deux. Mais ces 300 étiquettes ont un **coût** : nous y revenons en 8.3.8.

### 8.3.7 Le démarrage à froid

Reste la question du **premier lot**. Un modèle sans données ne sait pas ce qu'il ignore. Deux phénomènes se combinent.

**Il manque des classes.** Sur les chiffres, 10 images tirées au hasard ne couvrent en moyenne que **6,5 chiffres sur 10** ; le modèle ne peut tout simplement pas prédire les classes qu'il n'a jamais vues, et sa précision initiale n'est que de **0,37**. Sur les clients, la probabilité qu'un tirage de 10 clients ne contienne **aucun résiliateur** est de $0{,}86^{10}\approx0{,}22$ : l'entraînement échouerait une fois sur cinq.

**Une parade simple : des médoïdes.** On regroupe d'abord les données non étiquetées avec les k-means (volume II, section 3.3), puis on fait étiqueter, pour chaque groupe, l'image **la plus proche de son centre** (le *médoïde*). Avec 10 groupes sur les chiffres, les 10 médoïdes couvrent en moyenne **9,2 chiffres** et donnent une précision de départ de **0,71**, contre 0,37 pour 10 étiquettes au hasard.


Mais la suite est plus nuancée. Si l'on poursuit ensuite avec la stratégie de la marge, l'avantage des médoïdes **fond vite** :

| Étiquettes | 10 | 30 | 60 | 100 |
|---|---:|---:|---:|---:|
| Marge, départ aléatoire | 0,374 | 0,744 | 0,886 | 0,928 |
| Marge, départ par médoïdes | 0,713 | 0,781 | 0,887 | 0,926 |

À 60 étiquettes, les deux démarrages sont **à égalité** : la stratégie active corrige elle-même un mauvais départ en quelques tours. Le démarrage à froid pèse donc surtout lorsque le budget est **très** petit, ou lorsqu'il manque une **classe rare** (comme les résiliateurs) que la stratégie ne risque pas de découvrir seule : on garantit alors sa présence en incluant, par exemple, quelques clients déjà connus pour avoir résilié.

### 8.3.8 Combien ça rapporte ?

L'apprentissage actif n'est pas gratuit : il faut un système capable de **réentraîner** et de **servir** des questions à des annotateurs qui attendent, et chaque tour est un aller-retour. Pour savoir s'il en vaut la peine, on raisonne en **euros**.

**Hypothèses de calcul** (inventées pour l'illustration, à remplacer par vos coûts réels) : faire étiqueter une image de chiffre coûte **0,40 €** ; faire étiqueter un client (par un appel) coûte **4 €**.


| | Étiquettes pour atteindre le but | Coût d'étiquetage |
|---|---:|---:|
| **Chiffres**, précision $\ge0{,}90$ : tirage au hasard | 130 | 52 € |
| **Chiffres**, précision $\ge0{,}90$ : marge | 80 | 32 € |
| **Clients**, AUC $\ge0{,}80$ : tirage au hasard | 200 | 800 € |
| **Clients**, AUC $\ge0{,}80$ : incertitude | 140 | 560 € |

Les économies : **20 €** (38 %) sur les chiffres, **240 €** (30 %) sur les clients. Mais regardons le piège de 8.3.6 : si l'on a besoin de **probabilités calibrées**, le modèle actif exige 300 étiquettes aléatoires supplémentaires, soit **1 200 €**, bien plus que les 240 € économisés. Le modèle tiré au hasard, lui, est déjà calibré (0,142 de probabilité moyenne). La conclusion dépend donc de l'**usage** :

- si l'on veut seulement **classer** les clients (appeler les 10 % les plus à risque), l'AUC suffit, et l'apprentissage actif **fait économiser** ;
- si l'on veut **chiffrer** le risque (calculer une perte attendue en euros), le coût de recalibrage peut **annuler** le gain.

**Quand s'arrêter ?** Le gain de précision par étiquette décroît : plus on avance, moins une étiquette supplémentaire rapporte. Sur les chiffres, voici le gain par tranche de 10 étiquettes :

| Tranche | 60 → 70 | 100 → 110 | 140 → 150 |
|---|---:|---:|---:|
| Tirage au hasard | + 2,6 points | + 0,7 point | + 0,5 point |
| Marge | + 1,2 point | + 0,6 point | + 0,2 point |

(Le gain de la marge est plus faible en valeur absolue parce qu'elle part déjà plus haut.) Une règle simple : **continuer tant que le gain attendu vaut plus que le coût**. Supposons qu'un point de précision supplémentaire vaille **5 €** (hypothèse) : dix étiquettes coûtent 4 €, il faut donc un gain d'**au moins 0,8 point** pour 10 étiquettes. Avec la marge, à 60 étiquettes le gain (1,2 point, soit 5,9 €) dépasse le coût (4 €) : on continue ; à 100 étiquettes (0,6 point, soit 2,8 €), non : on s'arrête, autour de **80 à 100 étiquettes**.

> ✅ **À retenir.**
> - L'**apprentissage actif** fait étiqueter les points les plus utiles : boucle *entraîner, scorer, demander, recommencer*. Il vise le même niveau avec **moins d'étiquettes**.
> - **Critères** : confiance minimale, **marge** (hésitation entre deux classes), entropie, **comité** (désaccord de modèles), pondération par la **densité** (éviter les points aberrants). Les critères diffèrent dès trois classes ; sur les chiffres, la **marge** gagne nettement (80 étiquettes pour 0,90 au lieu de 130), l'entropie et la densité font **moins bien que le hasard**.
> - Le jeu étiqueté n'est pas un échantillon représentatif : jeu de test **aléatoire**, pas d'estimation de taux sur le jeu étiqueté, **recalibrage** sur un petit échantillon aléatoire (probabilité moyenne 0,078 avant, 0,141 après).
> - **Démarrage à froid** : 10 étiquettes aléatoires couvrent 6,5 classes sur 10 ; des **médoïdes** (9,2 classes) aident surtout à très petit budget.
> - Raisonner en **euros** : l'économie d'étiquettes peut être annulée par le coût de recalibrage ; s'arrêter quand le gain attendu ne couvre plus le coût.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.6 à 8.8, exercices 8.7 à 8.12.


## Bilan du chapitre 8

Vous savez maintenant :

- **situer** les deux familles de méthodes qui répondent au problème de l'**étiquette chère** : le **semi-supervisé**, qui exploite les données déjà disponibles mais sans étiquette, et l'**apprentissage actif**, qui choisit quelles étiquettes acheter ;
- **énoncer** les hypothèses qui permettent aux points sans étiquette d'aider (lissage, groupes, basse densité, variété), voir sur un exemple à la main comment un déplacement de frontière en résulte, et **reconnaître les cas où elles nuisent** (classes qui se chevauchent, étiquettes déséquilibrées, variables hétérogènes) ;
- **évaluer honnêtement** une méthode par une **courbe d'apprentissage selon le budget d'étiquettes** : jeu de test aléatoire et fixe, tirages répétés, **mêmes étiquettes** pour toutes les méthodes, comparaison au supervisé seul ;
- **expliquer** l'**auto-apprentissage** et son biais de confirmation, le **co-apprentissage** et ses conditions, et la **propagation d'étiquettes** (diffusion sur un graphe, solution fermée $F^*=(1-\alpha)(I-\alpha S)^{-1}Y$, minimisation d'un critère de lissage et de fidélité), la calculer **à la main** sur six nœuds ;
- **diagnostiquer** par l'**homophilie** (part de voisins de même étiquette) si un graphe a des chances d'aider : oui sur les chiffres (97 %), non sur les clients de la boutique (80,5 % contre 75,9 % au hasard) ;
- **écrire** la boucle d'apprentissage actif, **calculer** les critères d'incertitude (confiance minimale, **marge**, entropie), le **comité** et la pondération par la **densité**, et mesurer lequel est le meilleur *sur votre problème* (chiffres : la marge, 80 étiquettes pour 0,90 au lieu de 130) ;
- **éviter** les pièges de l'apprentissage actif : jeu étiqueté non représentatif et probabilités faussées (0,078 prédit pour 0,14 réel), jeu de test à tirer au hasard, **démarrage à froid** ;
- **raisonner en coût** : économie d'étiquettes contre coût de recalibrage, et règle d'arrêt « continuer tant que le gain attendu vaut plus que le coût ».

Deux messages à garder. **Le semi-supervisé et l'actif ne sont pas des baguettes magiques** : chacun repose sur une hypothèse sur les données, et la seule façon de savoir si elle tient est de **mesurer** à budget d'étiquettes égal. Et **les données ne sont pas des étiquettes** : tout le travail de ce chapitre vient de ce qu'on sait *faire* de ce qu'on possède (la structure) et de ce qu'on *décide d'acheter* (les étiquettes).

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.8 et exercices 8.1 à 8.12.

Le chapitre 9, également facultatif, change de décor : au lieu d'apprendre à partir d'exemples étiquetés, un agent apprend à **décider** en interagissant avec un environnement, c'est l'apprentissage par renforcement. Les bandits manchots y retrouvent une idée de ce chapitre : choisir *quoi essayer* pour apprendre le plus vite.
