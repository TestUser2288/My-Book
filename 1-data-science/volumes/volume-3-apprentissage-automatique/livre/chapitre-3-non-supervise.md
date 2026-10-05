# Chapitre 3 : Apprentissage non supervisé et réduction de dimension

> « Un algorithme de classification rend toujours des groupes. La vraie question n'est pas *combien*, c'est *est-ce que ça existe* ? »

Jusqu'ici, dans ce volume, chaque observation portait une **étiquette** : le client est parti ou non, la commande est frauduleuse ou non. On pouvait donc **vérifier** un modèle en comparant ses réponses à la bonne réponse. Ce chapitre quitte ce confort. On dispose seulement de **variables** décrivant les clients, et on demande à la machine de **découvrir de la structure** : des groupes qui se ressemblent, des directions qui résument les données, des représentations plus courtes.

La difficulté change de nature. Quand il n'y a pas de bonne réponse à vérifier, comment savoir qu'un résultat est **bon** ? C'est la question qui traverse tout le chapitre, et la réponse tient en une idée : on ne vérifie pas un résultat non supervisé contre la vérité, on le **soumet à plusieurs épreuves** (cohérence interne, comparaison avec un hasard sans structure, stabilité quand on perturbe les données, utilité pour une décision) et on regarde si elles se rejoignent.

> 🧭 **Ce que le volume II a déjà couvert.** L'analyse en composantes principales (volume II, section 3.1), l'analyse factorielle (section 3.2), les k-means et la classification hiérarchique (section 3.3) y sont présentées avec leurs bases : distance, algorithme de Lloyd, choix du nombre de groupes par le coude et la silhouette, avertissement « une méthode rend toujours des groupes ». Nous **ne les refaisons pas** : nous allons plus loin, vers la **validation** rigoureuse des groupes, vers des méthodes de réduction qui ne sont pas linéaires, et vers des méthodes de classification qui ne cherchent pas des boules.

## Le chemin de ce chapitre

- **3.1 Classification non supervisée et validation** : critères internes (inertie, silhouette, Calinski–Harabasz, Davies–Bouldin, statistique de l'écart), stabilité par rééchantillonnage, validation externe contre une vérité cachée, rôle de l'échelle et du choix des variables, lecture des groupes pour une décision.
- **3.2 Réduction de dimension** : pourquoi réduire (la malédiction de la dimension), rappel de l'ACP et reconstruction, ACP à noyau, SVD tronquée, factorisation non négative, projections aléatoires et le lemme de Johnson–Lindenstrauss, combien de dimensions garder.
- ➕ **3.3 DBSCAN, classification hiérarchique, mélanges gaussiens** : des groupes qui ne sont pas des boules, des groupes « flous », l'algorithme EM.
- ➕ **3.4 t-SNE et UMAP** : dessiner des données en haute dimension, et ce que ces dessins n'ont pas le droit de dire.

> 📒 **Pour s'entraîner.** Le cahier de ce chapitre propose huit applications guidées (segmentation de bout en bout, statistique de l'écart, réduction des chiffres manuscrits, EM écrit à la main, t-SNE et UMAP…) et douze exercices corrigés.

## Les données de ce chapitre

Deux jeux de données, de natures opposées, servent de fil conducteur.

- **Les clients de la boutique** (`donnees/clients_ml.csv`, 12 000 clients, **simulés**). Nous retenons sept variables de comportement : `age`, `nb_commandes_12m`, `montant_12m` (en logarithme, car très asymétrique), `recence_jours`, `part_achats_promo`, `taux_ouverture_email` et `nb_promos_recues_12m`. Le fichier contient aussi une variable `segment_vrai` : la **classe latente** qui a servi à fabriquer les comportements (quatre types : occasionnels, fidèles, chasseurs de promotions, grands paniers). Nous la gardons **de côté**, comme un examinateur garde le corrigé : elle servira à juger les méthodes en 3.1.6, mais aucune méthode ne la voit. Dans la vie réelle, cette vérité n'existe pas ; ici, elle nous permet de mesurer ce que valent nos critères.
- **Les chiffres manuscrits** (`load_digits` de scikit-learn, **réel**, intégré à la bibliothèque : 1 797 images de 8 × 8 pixels, donc 64 variables, représentant les chiffres de 0 à 9 écrits à la main). C'est un jeu classique pour les méthodes de réduction, parce qu'on peut **voir** les observations et savoir à quel chiffre elles correspondent.


## 3.1 Classification non supervisée et validation

> 💡 **Intuition.** Un cartographe dessine des frontières entre des régions sans qu'aucun panneau n'indique où elles passent. Il peut dessiner des frontières **utiles** ou des frontières **arbitraires**, et rien, dans le dessin lui-même, ne dit laquelle des deux il a faites. La classification non supervisée est ce travail de cartographe appliqué à des clients : on veut des groupes, et on doit apprendre à distinguer un groupe qui **existe** d'un groupe que l'algorithme a **fabriqué**.

Cette section répond à quatre questions, dans l'ordre : *comment mesurer la qualité d'un découpage quand on n'a pas de bonne réponse* (3.1.2), *ce découpage fait-il mieux que le hasard* (3.1.3), *est-il solide si l'on change l'échantillon* (3.1.4), et *que vaut-il contre une vérité connue, dans le cas où on la connaît* (3.1.5). Les deux dernières sous-sections traitent de ce qui décide du résultat avant même de lancer l'algorithme (l'échelle et le choix des variables, 3.1.6) et de la façon d'utiliser les groupes dans une décision (3.1.7).

### 3.1.1 Le problème : des clients, aucune étiquette

La gérante de la boutique voudrait **segmenter** sa clientèle pour adapter ses envois : ne pas proposer la même chose à une cliente qui commande chaque mois et à une cliente qui n'est pas revenue depuis un an. Elle ne dispose d'aucune étiquette « type de client » ; elle a seulement, pour chaque client, les sept variables de comportement présentées en introduction, centrées et réduites.

Le volume II (section 3.3) a présenté l'outil standard, les **k-means** : on fixe un nombre de groupes $k$ et on cherche la partition qui minimise la variance à l'intérieur des groupes (l'**inertie**). Cet outil pose immédiatement la question de ce chapitre : *quel $k$* ? Et plus fondamentalement : *les groupes trouvés sont-ils réels ?* L'inertie ne peut pas répondre, puisqu'elle **décroît toujours** quand $k$ augmente (au maximum, chaque client forme son propre groupe, et l'inertie vaut zéro). Il faut des critères qui pénalisent la complexité.

> 📐 **Trois familles de preuves.** Pour juger un découpage non supervisé, on dispose de trois familles d'épreuves, qui se complètent :
> 1. les critères **internes** : le découpage est-il à la fois *compact* (les points d'un groupe sont proches) et *séparé* (les groupes sont éloignés) ? Ils n'utilisent que les données ;
> 2. la **stabilité** : si l'on perturbe un peu les données (on en retire 20 %, on en rééchantillonne), retrouve-t-on les mêmes groupes ? Un découpage qui change à chaque tirage décrit le hasard de l'échantillon, pas la clientèle ;
> 3. les critères **externes** : le découpage retrouve-t-il une structure connue par ailleurs ? Ils exigent une vérité, donc ne servent qu'en laboratoire ou, dans la vie réelle, avec une étiquette partielle ou une **utilité mesurée** (les groupes prédisent-ils le départ des clients ?).

### 3.1.2 Critères internes : compacité et séparation

Notons $C_1,\dots,C_k$ les groupes, $\boldsymbol\mu_j$ leurs centres, $\bar{\mathbf x}$ le centre global, $n$ le nombre de points. Deux quantités décrivent tout découpage :

$$W=\sum_{j=1}^k\sum_{i\in C_j}\|\mathbf x_i-\boldsymbol\mu_j\|^2\quad\text{(dispersion intra-groupes)},\qquad B=\sum_{j=1}^k n_j\,\|\boldsymbol\mu_j-\bar{\mathbf x}\|^2\quad\text{(dispersion inter-groupes)}.$$

$W$ mesure la **compacité** ; $B$ mesure la **séparation** des centres. On a toujours $W+B=T$, la dispersion totale, qui ne dépend pas du découpage. Trois critères en découlent.

**Le coefficient de silhouette** (Rousseeuw, 1987) se calcule point par point. Pour un point $i$ du groupe $C$ :

- $a(i)$ est la **distance moyenne** de $i$ aux autres points de son groupe ;
- $b(i)$ est la distance moyenne de $i$ aux points du **groupe le plus proche** (hors du sien) ;
- $s(i)=\dfrac{b(i)-a(i)}{\max\{a(i),b(i)\}}$.

Une silhouette proche de $1$ signifie « bien rangé » ($a\ll b$) ; proche de $0$, « à la frontière » ; négative, « probablement dans le mauvais groupe ». On résume le découpage par la **silhouette moyenne**.

**Un exemple entièrement à la main.** Reprenons les six paniers moyens (en dizaines d'€) du volume II : $1,2,4,9,11,12$, découpés en $\{1,2,4\}$ et $\{9,11,12\}$.

- Point $4$ : distances aux autres points de son groupe, $3$ et $2$, donc $a=2{,}5$. Distances aux points de l'autre groupe, $5$, $7$ et $8$, donc $b=20/3\approx6{,}67$. Silhouette : $1-2{,}5/6{,}67=0{,}625$.
- Point $1$ : $a=(1+3)/2=2$, $b=(8+10+11)/3\approx9{,}67$, $s\approx0{,}793$. Point $2$ : $a=1{,}5$, $b=26/3\approx8{,}67$, $s\approx0{,}827$.
- Par symétrie, les points $12$, $11$ et $9$ ont les mêmes silhouettes que $1$, $2$ et $4$. La silhouette moyenne vaut $(0{,}793+0{,}827+0{,}625)/3\approx0{,}748$.

**L'indice de Calinski–Harabasz** compare séparation et compacité, en tenant compte du nombre de paramètres :

$$\mathrm{CH}(k)=\frac{B/(k-1)}{W/(n-k)}.$$

Plus il est **grand**, meilleur est le découpage. Sur l'exemple : les moyennes sont $7/3$ et $32/3$, la moyenne globale est $6{,}5$, donc $W=4{,}67+4{,}67=9{,}33$ et $B=3\,(7/3-6{,}5)^2+3\,(32/3-6{,}5)^2\approx104{,}2$, d'où $\mathrm{CH}=\dfrac{104{,}2/1}{9{,}33/4}\approx44{,}6$.

**L'indice de Davies–Bouldin** mesure, pour chaque groupe, son pire « voisin » : avec $s_j$ la distance moyenne des points du groupe $j$ à son centre,

$$\mathrm{DB}=\frac1k\sum_{j=1}^k\max_{l\ne j}\frac{s_j+s_l}{d(\boldsymbol\mu_j,\boldsymbol\mu_l)}.$$

Plus il est **petit**, mieux c'est. Sur l'exemple, $s_1=s_2\approx1{,}11$ et la distance entre les centres vaut $8{,}33$ : $\mathrm{DB}=2{,}22/8{,}33\approx0{,}267$.


Ces formules sont celles de `scikit-learn` (les trois résultats à la main coïncident avec la bibliothèque). Voyons ce qu'elles disent sur les 12 000 clients, pour $k$ de 2 à 8. Pour mémoire, nous utilisons la version de la bibliothèque, qui estime la silhouette sur un échantillon de 4 000 clients (le calcul exact coûte $n^2$ distances).


```text
 k  inertie  silhouette   CH    DB
 2    62835       0.304 4041 1.193
 3    45645       0.331 5040 1.118
 4    36775       0.284 5135 1.271
 5    32812       0.261 4678 1.311
 6    30347       0.244 4241 1.321
 7    28830       0.231 3825 1.428
 8    27500       0.226 3520 1.334
```

![Quatre critères internes en fonction du nombre de groupes $k$ pour les 12 000 clients. L'inertie décroît toujours ; les trois autres critères ne désignent pas le même $k$.](figures/ch03-criteres.png)

**Les critères ne s'accordent pas, et c'est normal.** L'inertie, comme on l'a dit, décroît partout sans coude net. La silhouette et l'indice de Davies–Bouldin préfèrent $k=3$ (silhouette $0{,}331$, DB $1{,}118$), tandis que l'indice de Calinski–Harabasz est maximal à $k=4$ ($5\,135$, contre $5\,040$ à $k=3$). Chaque critère encode une idée différente de la « bonne » séparation ; aucun ne détient la vérité. La pratique raisonnable consiste à retenir **une plage** de valeurs plausibles ($k=3$ à $5$ ici) et à départager avec les épreuves suivantes.

> ⚠️ **Piège : prendre le maximum d'un critère pour une réponse.** Un critère qui culmine à $k=3$ dit seulement que, *selon cette définition de la séparation*, trois groupes font mieux que deux ou quatre. Il ne dit pas que trois groupes existent. Les données peuvent former un continuum que tout découpage tranche arbitrairement : la silhouette aura quand même un maximum. C'est l'objet de la sous-section suivante.

### 3.1.3 Y a-t-il seulement des groupes ? La référence sans structure

Une silhouette de $0{,}33$ est-elle « bonne » ? Cela dépend de ce qu'on obtiendrait **sans aucune structure de groupes**. L'idée est de fabriquer des données de même nature mais **sans groupes**, de les passer dans le même algorithme et de comparer. Deux fabrications sont classiques :

- **la référence par permutation** : on mélange indépendamment chaque colonne. Chaque variable garde sa distribution (asymétrie, valeurs extrêmes), mais les liens entre variables disparaissent ;
- **la référence uniforme** : on tire des points uniformément dans la boîte englobant les données.


```text
 k  données réelles  colonnes permutées  boîte uniforme
 2            0.304               0.180           0.225
 3            0.331               0.190           0.182
 4            0.284               0.193           0.158
 5            0.261               0.191           0.147
```

Sur des données **sans aucune structure de groupes**, k-means rend quand même des groupes, avec une silhouette qui n'est pas nulle : de l'ordre de $0{,}18$ à $0{,}19$ pour les colonnes permutées. Les clients réels font mieux (de $0{,}26$ à $0{,}33$ selon $k$), ce qui est un premier indice de structure. Mais la marge n'est pas écrasante : une silhouette « honnête » se lit **par rapport à sa référence**, jamais dans l'absolu.

**La statistique de l'écart** (*gap statistic*, Tibshirani, Walther et Hastie, 2001) systématise cette idée. Pour chaque $k$, on compare le logarithme de la dispersion intra-groupes observée à son espérance sous la référence :

$$\mathrm{Gap}(k)=\mathbb E^{*}\!\left[\log W_k\right]-\log W_k,$$

où l'espérance $\mathbb E^*$ est estimée par un petit nombre $B$ de jeux de référence. On retient le plus petit $k$ tel que $\mathrm{Gap}(k)\ge\mathrm{Gap}(k+1)-s_{k+1}$, où $s_{k+1}$ est l'écart-type des $\log W_{k+1}^*$ corrigé par $\sqrt{1+1/B}$. L'idée : on s'arrête quand ajouter un groupe n'apporte plus, au-delà du bruit, plus que ce que ferait le hasard.


```text
 k  gap (permutation)  gap (uniforme)
 1              0.000           0.775
 2              0.176           0.818
 3              0.359           0.991
 4              0.488           1.119
 5              0.500           1.171
 6              0.494           1.197
 7              0.459           1.198
 8              0.454           1.212
choix (règle de Tibshirani) : permutation = 5 | uniforme = 6
```

![À gauche : silhouette moyenne des données réelles comparée à celle de deux références sans structure. À droite : statistique de l'écart selon la référence choisie ; avec la boîte uniforme, elle ne présente aucun maximum.](figures/ch03-reference-gap.png)

Avec la référence par permutation, l'écart culmine à $k=5$ ($0{,}500$, juste devant $0{,}494$ pour $k=6$ et $0{,}488$ pour $k=4$) et la règle de Tibshirani retient $k=5$ : le gain est net jusqu'à $k=4$ ou $5$, puis s'aplatit. Avec la référence **uniforme**, l'écart est déjà de $0{,}775$ pour un seul groupe et **ne cesse de croître** jusqu'à $k=8$ ($1{,}212$) : il n'y a pas de maximum, et la règle ne s'arrête à $k=6$ que parce que la courbe s'aplatit par endroits, sans rapport avec une structure. Presque n'importe quelle partition « bat » un nuage uniforme, parce que nos variables sont **asymétriques et corrélées**, ce que le nuage uniforme ne reproduit pas. Le choix de la référence est donc une **hypothèse** : une référence trop naïve rend n'importe quel découpage impressionnant.

### 3.1.4 Stabilité : les mêmes groupes si l'on change l'échantillon ?

Un découpage solide doit survivre à une perturbation raisonnable des données. Le protocole est simple et s'applique à n'importe quelle méthode :

1. on ajuste le modèle de référence sur **tous** les clients ;
2. on tire $B$ sous-échantillons de 80 % des clients (sans remise) ;
3. sur chacun, on ajuste de nouveau l'algorithme et on compare, sur les clients du sous-échantillon, le découpage obtenu à celui du modèle de référence, avec l'**indice de Rand ajusté** (ARI, défini en 3.1.5) ;
4. on moyenne : un ARI moyen proche de $1$ signifie que le découpage se **reproduit**.


```text
 k  ARI moyen  écart-type
 2      0.729       0.318
 3      0.996       0.004
 4      0.986       0.007
 5      0.981       0.016
 6      0.964       0.029
 7      0.782       0.120
```

![Stabilité de k-means : ARI moyen entre le découpage de référence et ceux de sous-échantillons de 80 %, avec son écart-type, pour $k$ de 2 à 7.](figures/ch03-stabilite.png)

La lecture est instructive. **De $k=3$ à $k=6$, les découpages sont remarquablement stables** (ARI moyen de $0{,}996$, $0{,}986$, $0{,}981$ puis $0{,}964$) ; la stabilité s'effondre à $k=7$ ($0{,}782$, avec un écart-type de $0{,}120$), signe que k-means « choisit » entre plusieurs découpages équivalents. Le cas $k=2$ est le plus curieux : un ARI moyen de $0{,}729$ avec un très grand écart-type ($0{,}318$). Selon les sous-échantillons, l'algorithme tombe sur **deux découpages en deux groupes différents** ; aucun des deux ne s'impose. La stabilité recoupe donc les critères internes sur un point : elle écarte $k=2$ (et $k\ge7$), mais elle **ne suffit pas à choisir** entre $3$, $4$, $5$ et $6$.

> 💡 **Stable ne veut pas dire vrai.** Un découpage peut être parfaitement reproductible et pourtant arbitraire (partager un nuage uniforme en deux moitiés, toujours au même endroit). La stabilité est une condition **nécessaire** de la validité, pas une condition suffisante : elle se combine avec la comparaison à une référence (3.1.3) et avec l'utilité (3.1.7).

### 3.1.5 Validation externe : confronter les groupes à une vérité connue

Ici, la simulation nous offre un luxe : nous connaissons la classe latente qui a engendré chaque client (`segment_vrai`). Nous pouvons donc mesurer à quel point chaque découpage la retrouve. Trois mesures, toutes calculées à partir du **tableau croisé** des groupes trouvés et des vrais groupes ($n_{ij}$ est le nombre de clients dans le groupe trouvé $i$ et le vrai groupe $j$, $a_i$ et $b_j$ les totaux des lignes et des colonnes) :

- la **pureté** : la part de clients appartenant, dans chaque groupe trouvé, à la classe majoritaire ; facile à lire, mais elle **augmente mécaniquement avec $k$** (à $k=n$, elle vaut $1$) ;
- l'**information mutuelle normalisée** (NMI) : $I(U;V)$ divisée par la moyenne des entropies des deux découpages ; elle vaut $0$ pour deux découpages indépendants et $1$ pour deux découpages identiques ;
- l'**indice de Rand ajusté** (ARI) : il compte les **paires de clients** rangées de la même façon dans les deux découpages (ensemble ou séparés), corrigé de la valeur attendue **au hasard** :

$$\mathrm{ARI}=\frac{\sum_{ij}\binom{n_{ij}}2-\Big[\sum_i\binom{a_i}2\sum_j\binom{b_j}2\Big]\Big/\binom n2}{\tfrac12\Big[\sum_i\binom{a_i}2+\sum_j\binom{b_j}2\Big]-\Big[\sum_i\binom{a_i}2\sum_j\binom{b_j}2\Big]\Big/\binom n2}.$$

L'ARI vaut $1$ pour un accord parfait, **environ $0$ pour un découpage aléatoire** (quel que soit $k$), et peut être négatif.

**Un exemple à la main.** Dix clients, deux vrais groupes de cinq ; l'algorithme en range quatre du premier et un du second dans son groupe 1, et inversement dans son groupe 2 : $n_{11}=4$, $n_{12}=1$, $n_{21}=1$, $n_{22}=4$. Alors $\sum_{ij}\binom{n_{ij}}2=6+0+0+6=12$, $\sum_i\binom{a_i}2=\sum_j\binom{b_j}2=10+10=20$, $\binom{10}2=45$. L'espérance au hasard vaut $20\times20/45\approx8{,}89$, le maximum $20$, d'où $\mathrm{ARI}=\dfrac{12-8{,}89}{20-8{,}89}\approx0{,}28$ : un accord qui paraît bon (8 clients sur 10 bien rangés) mais que la correction ramène à une valeur modeste, parce qu'avec deux groupes équilibrés le hasard seul rangerait déjà la moitié des clients correctement.


Appliquons ces mesures aux découpages de 3.1.2.

```text
 k   ARI   NMI
 2 0.022 0.121
 3 0.288 0.462
 4 0.487 0.535
 5 0.417 0.496
 6 0.397 0.473
 7 0.355 0.458
 8 0.352 0.470
pureté à k = 4 : 0.799
```

C'est à $k=4$, le nombre de vrais segments, que l'ARI est maximal ($0{,}487$) ; il retombe à $0{,}288$ pour $k=3$ et à $0{,}022$ pour $k=2$, découpage qui ne retrouve presque rien du vrai partage. Remarquez à quel point cette mesure externe est plus favorable à $k=4$ que la silhouette, qui préférait $3$ : **la silhouette récompense la séparation géométrique, pas la fidélité à une structure de décision**. Mais même au meilleur $k$, l'accord n'est que moyen (ARI $0{,}487$, pureté $0{,}799$). Regardons pourquoi.


```text
          vrai 0  vrai 1  vrai 2  vrai 3
groupe 0       5      22    2197       2
groupe 1      84    2879      23     567
groupe 2    1405      66     107     161
groupe 3    3112     590      20     760
```

Le tableau croisé montre trois choses. Les « chasseurs de promotions » (vrai segment 2) sont retrouvés presque tels quels : $2\,197$ sur $2\,347$ dans le groupe 0. Les « fidèles » (vrai 1) sont bien regroupés ($2\,879$ sur $3\,557$ dans le groupe 1), mais $590$ d'entre eux se retrouvent dans le groupe 3. Surtout, les « occasionnels » (vrai 0) et les « grands paniers » (vrai 3) ne sont pas séparés : le groupe 3 mélange à lui seul $3\,112$ occasionnels, $760$ grands paniers et $590$ fidèles, parce que, mesurés par ces sept variables, ces clients ne se distinguent pas : un client « grand panier » qui commande rarement ressemble à un occasionnel. Aucun algorithme, aucun $k$ ne résoudra cela ; le problème est dans les **variables**, pas dans la méthode.

> ⚠️ **Piège : croire qu'un ARI de $0{,}5$ est un échec de l'algorithme.** Un ARI modéré mesure l'écart entre *deux* partitions : la vraie, et celle qu'on peut déduire des variables disponibles. Quand les classes se recouvrent dans l'espace des variables, même un algorithme parfait ne peut pas les séparer. En situation réelle, c'est précisément cet écart qu'il faut anticiper : les groupes que vous trouvez décrivent ce que les **données permettent de distinguer**, pas ce que le monde contient.

### 3.1.6 Les variables et l'échelle décident des groupes

Avant même de choisir $k$, deux décisions pèsent plus lourd que l'algorithme.

**L'échelle.** k-means repose sur la distance euclidienne : une variable en milliers d'€ écrase une variable comprise entre 0 et 1. Comparons trois préparations des mêmes clients.


```text
                             préparation  ARI avec la vérité
variables standardisées (montant en log)               0.487
    montant en log, sans standardisation               0.081
      montant brut, sans standardisation               0.110
standardisées + 5 variables de pur bruit               0.485
```

Sans standardisation, l'ARI s'effondre (de $0{,}487$ à $0{,}081$ avec le montant en logarithme, $0{,}110$ avec le montant brut) : la variable `recence_jours`, dont l'échelle va de 0 à 365, impose sa géométrie à toutes les autres. Standardiser n'est pas un détail technique, c'est une **décision de modélisation** : on affirme que toutes les variables comptent à poids égal.

**Le choix des variables.** Ajouter cinq variables de pur bruit ne dégrade ici quasiment rien (ARI de $0{,}485$) : avec sept variables informatives, le signal reste dominant. Ce n'est pas une règle générale. Quand le nombre de variables inutiles grandit, les distances se **brouillent** (nous verrons pourquoi en 3.2.1) et les groupes se diluent. Le conseil pratique est de choisir les variables **pour une raison métier** (ce qui distingue les comportements qu'on veut traiter différemment), plutôt que d'y verser « tout ce qu'on a ».

### 3.1.7 Lire les groupes : de la partition à la décision

Un découpage n'a de valeur que par ce qu'on peut **en faire**. L'étape finale consiste donc à **profiler** les groupes (moyennes des variables, taille) et, surtout, à les confronter à une variable d'**utilité** que l'algorithme n'a pas vue. Ici, le départ à 90 jours (`churn_90j`) joue ce rôle : il n'a servi ni à construire ni à choisir les groupes.


```text
        part    age  commandes  montant  recence  part_promo  ouverture  churn  depense_6m
groupe                                                                                    
0       0.19  29.59       4.28   124.03    62.15        0.75       0.57   0.20       52.37
1       0.30  43.58       7.30   372.64    39.02        0.19       0.56   0.01      168.24
2       0.14  35.34       0.11     3.49   363.85        0.19       0.29   0.41       22.16
3       0.37  36.29       2.28   121.05    91.66        0.16       0.28   0.11       57.80
churn global : 0.14
```

![Profil des quatre groupes de k-means : écart de chaque moyenne à la moyenne générale, en écarts-types.](figures/ch03-profils.png)

Les groupes se lisent sans effort. Le **groupe 1** (environ 30 % des clients) réunit les **fidèles** : 7,3 commandes par an, un panier annuel de 373 €, une récence de 39 jours, et un départ à 90 jours de seulement 1 %. Le **groupe 2** (environ 14 %) regroupe les **dormants** : à peine 0,11 commande par an, 364 jours depuis la dernière, et un départ à 41 %, trois fois la moyenne de 14 %. Le **groupe 0** (environ 19 %) est celui des **chasseurs de promotions** : 75 % des achats en promotion, neuf promotions reçues, et un départ à 20 %. Le **groupe 3** (environ 37 %) rassemble les **occasionnels réguliers**, au comportement moyen et à 11 % de départ.

Voilà ce que veut dire « un découpage utile » : le départ, que l'algorithme n'a jamais vu, **varie de 1 % à 41 % selon le groupe**. C'est une validation d'une troisième sorte, **par l'utilité**, qui compte plus que n'importe quelle silhouette : si la gérante envoie une offre de réactivation au seul groupe 2, elle cible les clients dont le risque de départ est de 41 %. (Pour *prédire* le départ individu par individu, on utilisera plutôt un modèle supervisé, chapitre 2 ; la classification sert ici à **comprendre et à cibler**, pas à prédire.)

> ✅ **À retenir (validation d'une classification non supervisée).**
> - Un algorithme rend toujours des groupes : on ne juge pas un découpage dans l'absolu, mais **par rapport à une référence sans structure** (silhouette comparée, statistique de l'écart avec une référence choisie avec soin).
> - Les **critères internes** (silhouette, Calinski–Harabasz, Davies–Bouldin) ne désignent pas toujours le même $k$ : on retient une plage, pas un chiffre.
> - La **stabilité** par sous-échantillonnage écarte les découpages qui décrivent le hasard de l'échantillon ; elle est nécessaire, non suffisante.
> - Avec une vérité connue (laboratoire), l'**ARI** corrige les accords dus au hasard ; avec une vérité absente, c'est l'**utilité** (les groupes expliquent-ils un comportement non utilisé pour les construire ?) qui tranche.
> - L'**échelle** et le **choix des variables** pèsent plus que l'algorithme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.3, exercices 3.1 à 3.5.


## 3.2 Réduction de dimension

> 💡 **Intuition.** Une photographie de $64$ pixels n'a pas besoin de $64$ nombres indépendants pour être reconnue : les pixels voisins se ressemblent, les traits se répètent. La réduction de dimension cherche **la description courte** que cachent les données longues : moins de variables, presque la même information. Elle sert à **comprendre** (peut-on dessiner les données ?), à **compresser**, à **débruiter** et à **accélérer** les modèles qui suivent.

Le volume II a présenté la plus célèbre de ces méthodes, l'ACP (section 3.1). Cette section commence par expliquer *pourquoi* réduire est souvent indispensable (la « malédiction de la dimension »), rappelle l'ACP en une page pour mesurer ce qu'elle garde, puis présente les méthodes qui prolongent l'ACP quand ses hypothèses ne tiennent pas : données non linéaires, données positives à interpréter par « parties », données si nombreuses qu'on ne peut plus les centrer, ou si larges qu'on préfère une projection au hasard.

### 3.2.1 Pourquoi réduire : la malédiction de la dimension

Quand on ajoute des variables, on s'attend à *mieux* décrire les clients. La géométrie dit le contraire dès qu'on raisonne en **distances**, base de nombreuses méthodes (k plus proches voisins, k-means, noyaux). Prenons des points tirés uniformément dans un cube de dimension $d$, et regardons les distances entre paires de points.

Pour deux points $\mathbf x$ et $\mathbf y$ dont les coordonnées sont indépendantes et de même loi, le carré de la distance $\|\mathbf x-\mathbf y\|^2=\sum_{j=1}^d(x_j-y_j)^2$ est une somme de $d$ termes indépendants : son espérance croît comme $d$ et son écart-type comme $\sqrt d$. La **dispersion relative** des distances décroît donc comme $1/\sqrt d$ : quand $d$ grandit, **toutes les distances deviennent presque égales**, et la notion de « plus proche voisin » perd son sens.


```text
 dimension  rapport max/min  écart-type / moyenne
         2          1429.48                 0.475
         5            32.82                 0.283
        10             7.32                 0.193
        50             2.11                 0.086
       200             1.42                 0.042
      1000             1.18                 0.018
```

![Distances entre 500 points tirés uniformément dans un cube de dimension $d$ : le rapport entre la plus grande et la plus petite distance et la dispersion relative des distances décroissent avec $d$.](figures/ch03-malediction.png)

En dimension 2, la plus grande distance est environ $1\,400$ fois la plus petite ; en dimension 50, ce rapport tombe à $2{,}1$ ; en dimension 1 000, à $1{,}18$ : tous les points sont à peu près à la même distance de tous les autres. Un k-means ou un plus proche voisin qui s'appuie sur ces distances ne sait plus distinguer proche et lointain.

> ⚠️ **Nuance importante.** La malédiction est la plus sévère quand les variables sont **indépendantes** et **toutes pertinentes**. Les données réelles ont presque toujours une structure bien plus pauvre que leur nombre de colonnes : les chiffres manuscrits ont 64 pixels mais occupent une portion très réduite de l'espace des images possibles. C'est ce qui rend la réduction de dimension **possible** : on ne comprime pas l'espace entier, seulement la petite région où vivent les données.

### 3.2.2 L'ACP en une page, et ce qu'elle garde

Rappelons l'essentiel (volume II, sections 3.1.3 et 3.1.4). Pour des données centrées $\mathbf X$ de $n$ lignes et $p$ colonnes, l'ACP cherche les directions orthogonales de variance maximale ; ce sont les vecteurs propres de la matrice de covariance, et la variance portée par la $j$-ième direction est la valeur propre $\lambda_j$. Garder les $m$ premières composantes revient à projeter chaque observation sur le sous-espace de dimension $m$ le plus proche des données.

Ce que l'on **perd** s'exprime exactement. D'après le théorème d'**Eckart–Young**, la meilleure approximation de rang $m$ de $\mathbf X$ (au sens de la somme des carrés des erreurs) est obtenue par la SVD tronquée, et l'erreur quadratique de reconstruction vaut la somme des valeurs propres **écartées** :

$$\sum_{i}\|\mathbf x_i-\hat{\mathbf x}_i\|^2=(n-1)\sum_{j>m}\lambda_j,\qquad\text{soit en proportion : }\ 1-\frac{\lambda_1+\dots+\lambda_m}{\lambda_1+\dots+\lambda_p}.$$

L'erreur *relative* de reconstruction est donc exactement **un moins la part de variance expliquée** : c'est ce qui rend le tableau de bord de l'ACP (le graphique cumulé des valeurs propres) aussi utile. Appliquons-le aux 1 797 chiffres manuscrits ($p=64$).


```text
 composantes  variance gardée  erreur relative  précision 5-ppv
           2            0.285            0.715            0.603
           5            0.545            0.455            0.888
          10            0.738            0.262            0.937
          20            0.894            0.106            0.959
          30            0.959            0.041            0.962
          40            0.988            0.012            0.961
précision 5-ppv sur les 64 pixels bruts : 0.963
```

![Gauche : variance cumulée des composantes principales des chiffres manuscrits et nombre de composantes nécessaires pour 80, 90, 95 et 99 %. Droite : précision d'un classifieur des 5 plus proches voisins selon le nombre de composantes gardées, comparée aux 64 pixels bruts.](figures/ch03-chiffres-pca.png)

![Quatre lignes : six chiffres originaux, puis leur reconstruction avec 2, 10 et 30 composantes principales.](figures/ch03-chiffres-reconstruction.png)

Trois lectures. **(i)** Il faut $13$ composantes pour garder $80\ \%$ de la variance, $21$ pour $90\ \%$, $29$ pour $95\ \%$ et $41$ pour $99\ \%$ : une compression par trois sans perte visible. **(ii)** L'erreur relative de reconstruction coïncide bien avec « un moins la variance gardée » (à $10$ composantes : $0{,}738$ de variance gardée et $0{,}262$ d'erreur, ce que dit Eckart–Young). **(iii)** Surtout, **l'information utile pour reconnaître un chiffre survit à la compression** : avec $20$ composantes, la précision d'un classifieur des 5 plus proches voisins est de $0{,}959$ contre $0{,}963$ sur les $64$ pixels bruts, alors qu'avec $2$ composantes elle tombe à $0{,}603$. Le graphique des reconstructions le montre : à $2$ composantes on devine à peine la forme, à $10$ on lit le chiffre, à $30$ on ne voit plus la différence.

### 3.2.3 Quand la structure n'est pas linéaire : l'ACP à noyau

L'ACP ne trouve que des directions **linéaires**. Sur deux cercles concentriques, aucune droite ne sépare le cercle intérieur du cercle extérieur : la première composante principale, qui est une direction, les mélange.

L'**ACP à noyau** (*kernel PCA*, Schölkopf et coll., 1998) contourne cette limite par une idée remarquable : au lieu de projeter les données elles-mêmes, on les envoie d'abord dans un espace de très grande dimension où elles deviennent séparables, puis on y fait une ACP, **sans jamais calculer explicitement** cet espace. Il suffit de connaître les **produits scalaires** entre points dans cet espace, que fournit une fonction appelée **noyau**, par exemple le noyau gaussien :

$$k(\mathbf x,\mathbf y)=\exp\!\big(-\gamma\,\|\mathbf x-\mathbf y\|^2\big).$$

La méthode a quatre étapes : (1) calculer la matrice de Gram $K_{ij}=k(\mathbf x_i,\mathbf x_j)$ ; (2) la **centrer** dans l'espace transformé, $\tilde K=K-\mathbf 1K-K\mathbf 1+\mathbf 1K\mathbf 1$ où $\mathbf 1$ est la matrice $n\times n$ dont toutes les entrées valent $1/n$ ; (3) calculer ses valeurs propres $\lambda_j$ et vecteurs propres $\mathbf v_j$ ; (4) les coordonnées du point $i$ sur la $j$-ième composante sont $\sqrt{\lambda_j}\,v_{j,i}$.


```text
précision d'une séparation par seuil sur la 1re composante : {'ACP': 0.498, 'ACP à noyau': 1.0}
```

![Deux cercles concentriques : les données, leur projection par ACP linéaire, puis par ACP à noyau gaussien, qui sépare les deux cercles le long de la première composante.](figures/ch03-kpca.png)

Une séparation par un simple seuil sur la première composante a une précision de $0{,}498$ avec l'ACP (le hasard) et de $1{,}0$ avec l'ACP à noyau. Deux mises en garde : le paramètre $\gamma$ du noyau **décide** de ce que la méthode voit (trop grand, chaque point est isolé ; trop petit, le noyau devient presque linéaire) et il se règle par validation, comme n'importe quel hyperparamètre (section 1.5) ; et, contrairement à l'ACP, la **reconstruction** n'est pas directe (retrouver un point de l'espace d'origine à partir d'une position dans l'espace transformé est un problème d'« image réciproque » approchée).

### 3.2.4 SVD tronquée : quand on ne peut pas centrer

L'ACP exige de **centrer** les données, ce qui détruit la **parcimonie** : une matrice de $100\,000$ documents et de $50\,000$ mots, presque toute faite de zéros, devient dense une fois centrée, donc impossible à stocker. La **SVD tronquée** (`TruncatedSVD`) applique la même décomposition en valeurs singulières **sans centrer** ; elle conserve la parcimonie et reste calculable. Quand les colonnes sont déjà centrées, elle coïncide avec l'ACP. Appliquée à des tableaux de comptages de mots, elle porte le nom d'**analyse sémantique latente** (LSA).


```text
variance expliquée par 10 composantes : SVD tronquée 0.732 | ACP 0.738
```

Sur les chiffres, dont les pixels ne sont pas centrés, les deux méthodes donnent presque la même part de variance expliquée par $10$ composantes ($0{,}732$ contre $0{,}738$) : l'écart, minime, tient à l'absence de centrage.

### 3.2.5 La factorisation non négative : décrire par parties

Les composantes principales ont des coefficients positifs et négatifs : une image se décrit comme un mélange où certaines directions *retranchent* de l'information, ce qui rend les composantes difficiles à lire (« moitié d'un chiffre, moins un autre »). Quand les données sont **positives** (pixels, comptages, montants), on peut exiger une description **purement additive**.

La **factorisation non négative** (NMF, Lee et Seung, 1999) approche la matrice des données $V\ (n\times p)$ par un produit de deux matrices à entrées positives ou nulles :

$$V\approx WH,\qquad W\ge0\ (n\times m),\quad H\ge0\ (m\times p),$$

en minimisant $\|V-WH\|_F^2$. Chaque ligne de $H$ est une « partie » (un motif de base) ; chaque observation est une **somme** de parties pondérées par sa ligne de $W$. Les mises à jour multiplicatives de Lee et Seung, $H\leftarrow H\circ\dfrac{W^\top V}{W^\top WH}$ et $W\leftarrow W\circ\dfrac{VH^\top}{WHH^\top}$ (produit et quotient *terme à terme*), préservent la positivité et diminuent l'erreur à chaque pas.


```text
NMF, 10 composantes : précision 5-ppv 0.84 | ACP, 10 composantes : 0.937
```

![Les dix « parties » apprises par la factorisation non négative sur les chiffres manuscrits : chacune est un motif de traits que l'on additionne.](figures/ch03-nmf.png)

Les dix parties sont des **motifs de traits** que l'on peut additionner pour composer un chiffre : c'est la lisibilité qu'on cherche. Elle a un prix : avec $10$ composantes, un classifieur des 5 plus proches voisins atteint $0{,}840$ sur la NMF contre $0{,}937$ sur l'ACP. La NMF n'est donc **pas** une compression meilleure ; c'est une **représentation plus lisible**. Elle sert quand on veut interpréter (thèmes d'un corpus, profils d'achat, spectres).

### 3.2.6 Les projections aléatoires et le lemme de Johnson–Lindenstrauss

Dernière idée, qui surprend : pour réduire la dimension, **on peut projeter au hasard**. Choisissons une matrice $R$ de $k$ lignes et $p$ colonnes dont les entrées sont des tirages indépendants d'une loi $\mathcal N(0,1/k)$, et remplaçons chaque observation $\mathbf x$ par $R\mathbf x$. Cela paraît absurde (aucune information sur les données n'a servi à construire $R$), et pourtant :

> 📐 **Lemme de Johnson–Lindenstrauss (1984).** Pour tout $0<\varepsilon<1$ et tout ensemble de $n$ points de $\mathbb R^p$, il existe une application linéaire vers $\mathbb R^k$ avec
> $$k\ \ge\ \frac{4\ln n}{\varepsilon^2/2-\varepsilon^3/3}$$
> qui préserve toutes les distances à un facteur près : $(1-\varepsilon)\|\mathbf x-\mathbf y\|^2\le\|f(\mathbf x)-f(\mathbf y)\|^2\le(1+\varepsilon)\|\mathbf x-\mathbf y\|^2$ pour tous les couples. De plus, une projection gaussienne aléatoire convient avec une probabilité élevée.

*Idée de la démonstration.* Pour un vecteur fixe $\mathbf u$ et $R$ gaussienne, $\|R\mathbf u\|^2/\|\mathbf u\|^2$ suit la loi $\chi^2_k/k$, d'espérance $1$ et de variance $2/k$ : elle se **concentre** autour de $1$ quand $k$ grandit, avec une queue exponentielle. On applique ensuite une **borne de l'union** sur les $n(n-1)/2$ différences $\mathbf x_i-\mathbf x_j$ : si la probabilité d'erreur de chacune est de l'ordre de $n^{-2}$, la probabilité qu'une seule échoue reste faible, ce qui impose $k$ de l'ordre de $\ln n/\varepsilon^2$.

Deux remarques déroutantes. Le résultat est **indépendant de $p$** : seul le nombre de points $n$ compte (de façon logarithmique). Et la borne est **pessimiste** : elle garantit *toutes* les paires. Mesurons ce qui se passe réellement sur nos 1 797 chiffres ($p=64$).


```text
  k  ratio moyen  écart-type  5 % - 95 % paires à ±20 %
  5        0.944       0.286 0.49 - 1.43          48.9%
 10        0.978       0.202 0.65 - 1.32          66.7%
 20        0.978       0.148 0.74 - 1.23          81.7%
 40        0.963       0.096 0.81 - 1.12          95.0%
 64        0.968       0.075 0.85 - 1.09          98.7%
100        0.970       0.062 0.87 - 1.07          99.7%
200        0.965       0.046 0.89 - 1.04         100.0%
bornes de la bibliothèque (n = 1797) : epsilon 0,5 -> 359 | epsilon 0,2 -> 1729
```

![Rapport entre la distance après et avant projection aléatoire, pour 1 797 chiffres et des projections de dimension $k$ de 5 à 200 : les boîtes se resserrent autour de 1 quand $k$ augmente.](figures/ch03-jl.png)

La borne théorique exige $k\ge359$ pour $\varepsilon=0{,}5$ et $k\ge1\,729$ pour $\varepsilon=0{,}2$, c'est-à-dire **plus que les 64 pixels d'origine** : elle n'est utile qu'en très grande dimension. Dans la pratique, la conservation est bien meilleure : avec $k=40$, $95{,}0\ \%$ des distances sont conservées à $\pm20\ \%$, avec $k=64$ $98{,}7\ \%$, et avec $k=200$ toutes. La moyenne des rapports est légèrement inférieure à $1$ (entre $0{,}94$ et $0{,}98$ selon $k$) : c'est la distance, et non son carré, qui est mesurée, et l'inégalité de Jensen fait $\mathbb E\sqrt X\le\sqrt{\mathbb EX}$.

> 💡 **Quand les projections aléatoires servent-elles ?** Quand $p$ est énorme (dizaines de milliers de colonnes), parce qu'elles sont **instantanées**, ne dépendent d'aucune donnée (on peut projeter un nouveau point sans ré-ajuster), et conservent les distances nécessaires aux méthodes de voisinage. Pour comprendre des données de dimension modérée, l'ACP reste préférable : elle choisit les directions **qui comptent**.

### 3.2.7 Combien de dimensions garder ? Et l'idée de variété

Il n'existe pas de règle universelle ; on combine trois indices.

1. **La variance gardée** : un seuil (80 %, 90 %, 95 %) ou un coude sur le graphique cumulé. Rapide, mais le seuil est arbitraire.
2. **La reconstruction** : l'erreur relative de reconstruction vaut un moins la variance gardée (Eckart–Young) ; on la compare à ce qu'on tolère.
3. **L'utilité en aval** : on mesure la performance de la tâche finale (la précision d'un classifieur, la qualité d'un regroupement) en fonction du nombre de dimensions, **par validation croisée** (section 1.2), et on s'arrête quand elle plafonne. Sur les chiffres, la précision plafonne vers $20$ composantes : c'est le critère qui compte, parce qu'il mesure ce qu'on veut en faire.

Le volume II (section 3.1.6) mentionne aussi l'analyse parallèle, qui compare les valeurs propres à celles de données sans structure : c'est la même logique de « référence sans structure » que celle de 3.1.3.

**L'hypothèse de variété.** Pourquoi une compression est-elle possible ? Parce que les données réelles vivent souvent au voisinage d'une **variété** de faible dimension : une surface (courbe, repliée) plongée dans un espace de grande dimension. Le célèbre « rouleau suisse » en est l'illustration : des points sur une feuille enroulée, dans un espace à 3 dimensions, alors que la feuille est de dimension 2. L'ACP, qui ne sait projeter que sur un plan, **écrase les couches du rouleau les unes sur les autres** ; une méthode qui respecte les **distances le long de la surface** (Isomap, qui déroule la variété à partir du graphe des plus proches voisins) le déplie. Les méthodes t-SNE et UMAP (section 3.4) reposent sur cette même hypothèse.


![Le rouleau suisse en 3 dimensions, sa projection par ACP (les couches se recouvrent) et son dépliage par Isomap (la couleur, qui repère la position le long du rouleau, varie régulièrement).](figures/ch03-rouleau.png)

### 3.2.8 Réduire avant de classer : sur les clients de la boutique

Revenons aux 12 000 clients. Une pratique répandue consiste à **réduire** les sept variables par ACP avant de lancer k-means. Est-ce neutre ?


```text
 composantes gardées  variance gardée  ARI avec la vérité (k=4)
                   2            0.641                     0.480
                   3            0.762                     0.489
                   4            0.857                     0.502
                   5            0.932                     0.479
                   7            1.000                     0.487
                   CP1   CP2   CP3
âge               0.04 -0.43  0.80
commandes         0.47 -0.20 -0.10
montant (log)     0.52 -0.27 -0.22
récence          -0.50  0.15  0.22
part promo        0.25  0.58  0.13
ouverture e-mail  0.39  0.16  0.46
promos reçues     0.21  0.57  0.14
```

![Cercle des corrélations de l'ACP sur les sept variables de comportement : la première composante oppose récence et activité, la deuxième regroupe les variables liées aux promotions.](figures/ch03-acp-boutique.png)

La première composante ($37\ \%$ de la variance) oppose la **récence** à l'**activité** (nombre de commandes, montant, ouverture des e-mails) : c'est un axe « client actif contre client endormi ». La deuxième ($27\ \%$) regroupe `part_achats_promo` et `nb_promos_recues_12m` : un axe « sensibilité aux promotions ». Garder $4$ composantes ($85{,}7\ \%$ de la variance) donne un ARI de $0{,}502$ avec la vérité cachée, contre $0{,}487$ avec les $7$ variables : la réduction **ne détruit pas** la structure et la débruite même un peu. Avec seulement $2$ composantes, on retombe à $0{,}480$. La leçon : la réduction n'est pas neutre, et son effet se **mesure** avec les mêmes épreuves que la classification (3.1), au lieu de se supposer.

> ✅ **À retenir (réduction de dimension).**
> - En grande dimension, les distances se resserrent (dispersion relative en $1/\sqrt d$) : les méthodes de voisinage souffrent, d'où l'intérêt de réduire.
> - L'ACP garde la variance, et l'erreur relative de reconstruction vaut **un moins la variance gardée** (Eckart–Young) ; le bon nombre de composantes se choisit par **l'utilité en aval**, validée par validation croisée.
> - L'**ACP à noyau** capte des structures non linéaires ; la **SVD tronquée** évite de centrer (données parcimonieuses) ; la **NMF** donne des composantes **additives et lisibles** ; les **projections aléatoires** conservent les distances (Johnson–Lindenstrauss) à moindre coût quand $p$ est énorme.
> - Les données réelles vivent souvent près d'une **variété** de faible dimension : c'est ce qui rend la réduction possible, et ce que t-SNE et UMAP cherchent à déplier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.4 et 3.8, exercices 3.6 à 3.8.


## 3.3 ➕ Pour aller plus loin : DBSCAN, classification hiérarchique, mélanges gaussiens

> 🧭 **Section optionnelle.** Elle prolonge 3.1 avec trois méthodes qui lèvent chacune une hypothèse de k-means : que les groupes soient des **boules** (DBSCAN et les liens hiérarchiques), qu'ils soient **bien tranchés** (les mélanges gaussiens donnent des appartenances « floues »). On peut la sauter sans perdre le fil du chapitre.

k-means suppose, sans le dire, que chaque groupe est une région **convexe** et à peu près **sphérique** autour de son centre : il découpe l'espace en cellules de Voronoï. Quand les groupes ont une forme allongée, courbe ou imbriquée, cette hypothèse trahit les données. Le cas d'école est celui des **deux lunes** : deux croissants entrelacés. Un humain y voit tout de suite deux groupes ; k-means, qui doit couper l'espace par une droite, les mélange.

### 3.3.1 DBSCAN : les groupes comme régions denses

**DBSCAN** (Ester et coll., 1996) définit un groupe comme une **région dense** séparée d'autres régions denses par des zones vides. Il n'a pas besoin de connaître le nombre de groupes, accepte des formes quelconques, et surtout il a une réponse naturelle pour les points qui n'appartiennent à aucun groupe : ce sont du **bruit**.

Deux paramètres seulement : un rayon $\varepsilon$ et un effectif minimal $m$ (`min_samples`). Pour un point $\mathbf x$, son **voisinage** est l'ensemble des points à distance au plus $\varepsilon$ de lui (lui-même compris). Les points se classent alors en trois types :

- un point **cœur** a au moins $m$ points dans son voisinage ;
- un point **de bordure** n'est pas un cœur, mais se trouve dans le voisinage d'un cœur ;
- un point **de bruit** n'est ni l'un ni l'autre.

Un groupe est l'ensemble des points obtenus en partant d'un cœur et en **suivant de proche en proche les cœurs voisins** (deux cœurs sont connectés s'ils sont à distance $\le\varepsilon$), auxquels on ajoute leurs points de bordure.

**Un exemple à la main, en dimension 1.** Neuf valeurs : $1;\ 1{,}2;\ 1{,}4;\ 1{,}85;\ 2{,}5;\ 5;\ 5{,}1;\ 5{,}3;\ 9$, avec $\varepsilon=0{,}5$ et $m=3$.

- Le voisinage de $1$ est $\{1;\ 1{,}2;\ 1{,}4\}$ : trois points, c'est un **cœur**. De même pour $1{,}2$ (voisinage $\{1;\ 1{,}2;\ 1{,}4\}$) et pour $1{,}4$ (voisinage $\{1;\ 1{,}2;\ 1{,}4;\ 1{,}85\}$).
- Le point $1{,}85$ n'a que deux points dans son voisinage ($1{,}4$ et lui-même) : ce n'est pas un cœur ; mais il est à $0{,}45$ du cœur $1{,}4$, c'est un point **de bordure** : il rejoint le premier groupe.
- Le point $2{,}5$ est à $0{,}65$ du point le plus proche : ni cœur, ni voisin d'un cœur, c'est du **bruit**.
- $5$, $5{,}1$ et $5{,}3$ forment un second groupe, chacun étant un cœur. Enfin $9$ est du bruit.


```text
 valeur    type  groupe
   1.00    cœur       0
   1.20    cœur       0
   1.40    cœur       0
   1.85 bordure       0
   2.50   bruit      -1
   5.00    cœur       1
   5.10    cœur       1
   5.30    cœur       1
   9.00   bruit      -1
```

Le tableau de la bibliothèque confirme le raisonnement : deux groupes (étiquettes $0$ et $1$), six cœurs, un point de bordure et deux points de bruit (étiquette $-1$).

**Choisir $\varepsilon$ et $m$.** L'effectif minimal $m$ se prend en général égal à $2p$ ($p$ étant la dimension), ou plus quand les données sont bruitées. Le rayon $\varepsilon$ se lit sur le **graphique des $k$-distances** : pour chaque point, on calcule la distance à son $m$-ième plus proche voisin, on trie ces distances, et on cherche le « coude » de la courbe, au-delà duquel les distances grimpent brusquement (les points isolés). Sur les deux lunes, avec $m=5$, la distance au 5e voisin est de $0{,}057$ pour la moitié des points et de $0{,}128$ pour $99\ \%$ d'entre eux.


```text
 epsilon  groupes  points de bruit   ARI
    0.05       35              266 0.021
    0.10        2                4 0.987
    0.15        2                0 1.000
    0.20        2                0 1.000
    0.30        1                0 0.000
```

![Deux lunes entrelacées : k-means, DBSCAN avec $\varepsilon=0{,}15$, classification hiérarchique à lien simple et à lien de Ward. Les points gris seraient du bruit.](figures/ch03-lunes.png)

![Graphique des $k$-distances des deux lunes (distance au 5e voisin, triée) avec deux valeurs de $\varepsilon$ testées.](figures/ch03-kdistances.png)

La sensibilité à $\varepsilon$ est nette. Trop petit ($0{,}05$), il **fragmente** les lunes en 35 groupes minuscules et déclare 266 points « bruit » (ARI $0{,}021$). Dans l'intervalle $0{,}1$ à $0{,}2$, il retrouve les deux lunes (ARI $0{,}987$ à $1{,}0$). Trop grand ($0{,}3$), les deux lunes **fusionnent** en un seul groupe (ARI nul). C'est la limite principale de DBSCAN : un seul rayon pour toute la population, donc une **densité unique**. Quand les groupes ont des densités très différentes, aucun $\varepsilon$ ne convient.

> ⚠️ **DBSCAN ne marche pas partout.** Sur les clients de la boutique, il échoue : les distributions sont asymétriques et le nuage forme un **continuum** de densités variables. Avec $m=14$ ($=2p$), $\varepsilon=0{,}8$ donne 3 groupes mais **16,5 %** de bruit et un ARI de $0{,}214$ avec la vérité (contre $0{,}487$ pour k-means) ; $\varepsilon=0{,}5$ déclare 86 % de bruit ; $\varepsilon=1{,}2$ fusionne tout. La méthode excelle sur des formes géométriques bien séparées, pas sur des profils de comportement à frontières floues.


```text
 epsilon  groupes  part de bruit    ARI
     0.5        7          0.860 -0.016
     0.8        3          0.165  0.214
     1.2        2          0.008 -0.002
```

### 3.3.2 La classification hiérarchique, revue par les liens

Le volume II (section 3.3.4) a présenté la classification ascendante hiérarchique : on part de $n$ groupes d'un point et on fusionne à chaque étape les deux groupes les plus proches, ce qui produit un **dendrogramme** que l'on coupe à la hauteur voulue. Reste à définir la distance entre **deux groupes** : c'est le **lien** (*linkage*).

- **Lien simple** : distance minimale entre un point de chaque groupe. Il suit les « chaînes » de points proches, et retrouve donc les formes allongées, mais il est sensible au **chaînage** (un pont de quelques points fusionne deux groupes distincts).
- **Lien complet** : distance maximale. Il produit des groupes compacts de diamètre limité.
- **Lien moyen** : distance moyenne entre toutes les paires.
- **Lien de Ward** : on fusionne les deux groupes dont la fusion fait **le moins augmenter la variance intra** $W$ ; c'est l'analogue hiérarchique de k-means, qui donne des groupes en boules.

Sur les deux lunes, l'effet du lien est spectaculaire (voir le tableau : le lien simple retrouve parfaitement les croissants, l'ARI du lien de Ward est modeste).

```text
                   méthode   ARI
             k-means (k=2) 0.252
     DBSCAN (epsilon=0,15) 1.000
 hiérarchique, lien simple 1.000
hiérarchique, lien complet 0.426
  hiérarchique, lien moyen 0.557
hiérarchique, lien de Ward 0.557
```

Le lien simple atteint un ARI de $1{,}0$ ; le lien moyen et celui de Ward, $0{,}557$ ; le lien complet, $0{,}426$ ; k-means, $0{,}252$. **Aucun lien n'est « le bon »** : chacun encode une idée de la forme d'un groupe. Une limite pratique commune : la classification hiérarchique doit stocker les distances entre toutes les paires, soit un coût en mémoire de l'ordre de $n^2$ : acceptable pour quelques milliers de points, impossible pour nos 12 000 clients.

### 3.3.3 Les mélanges gaussiens : des appartenances « floues »

k-means affecte chaque client à **un** groupe, de façon tranchée. Or un client à mi-chemin entre fidèle et occasionnel n'appartient pas vraiment à l'un ou à l'autre. Les **mélanges gaussiens** (*Gaussian mixture models*, GMM) modélisent cela en supposant que les données sont tirées d'un **mélange de lois normales** :

$$p(\mathbf x)=\sum_{k=1}^K\pi_k\,\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k),\qquad \pi_k\ge0,\ \sum_k\pi_k=1.$$

Chaque groupe $k$ a son centre $\boldsymbol\mu_k$, sa **forme** (la matrice de covariance $\Sigma_k$ : boule, ellipse, ellipse inclinée) et son **poids** $\pi_k$. La grande différence : pour un client $\mathbf x_i$, le modèle ne dit pas « groupe 2 », il donne les **probabilités d'appartenance** (ou *responsabilités*)

$$\gamma_{ik}=\frac{\pi_k\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_{l=1}^K\pi_l\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_l,\Sigma_l)}.$$

Les paramètres se choisissent en maximisant la vraisemblance, mais la somme dans le logarithme rend le calcul direct impossible. On le contourne par l'algorithme **EM** (*Expectation–Maximization*, Dempster, Laird et Rubin, 1977), qui alterne deux étapes simples :

- **étape E** (espérance) : avec les paramètres actuels, calculer les responsabilités $\gamma_{ik}$ ;
- **étape M** (maximisation) : remettre à jour les paramètres en traitant les $\gamma_{ik}$ comme des poids :
$$N_k=\sum_i\gamma_{ik},\qquad \boldsymbol\mu_k=\frac1{N_k}\sum_i\gamma_{ik}\,\mathbf x_i,\qquad \Sigma_k=\frac1{N_k}\sum_i\gamma_{ik}(\mathbf x_i-\boldsymbol\mu_k)(\mathbf x_i-\boldsymbol\mu_k)^\top,\qquad \pi_k=\frac{N_k}n.$$

> 📐 **D'où viennent ces formules ?** Dérivons la mise à jour de $\boldsymbol\mu_k$. La log-vraisemblance est $\ell=\sum_i\ln\sum_k\pi_k\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)$. Comme $\partial_{\boldsymbol\mu_k}\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k)=\mathcal N\,\Sigma_k^{-1}(\mathbf x-\boldsymbol\mu_k)$, on obtient
> $$\frac{\partial\ell}{\partial\boldsymbol\mu_k}=\sum_i\underbrace{\frac{\pi_k\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_l\pi_l\mathcal N(\mathbf x_i\mid\boldsymbol\mu_l,\Sigma_l)}}_{\gamma_{ik}}\Sigma_k^{-1}(\mathbf x_i-\boldsymbol\mu_k).$$
> Annuler ce gradient donne $\sum_i\gamma_{ik}(\mathbf x_i-\boldsymbol\mu_k)=0$, soit $\boldsymbol\mu_k=\sum_i\gamma_{ik}\mathbf x_i/N_k$ : **une moyenne pondérée par les responsabilités**. Les autres formules se démontrent de même (avec un multiplicateur de Lagrange pour la contrainte $\sum_k\pi_k=1$). On montre ensuite (par l'inégalité de Jensen, qui fournit une minoration de $\ell$ que l'étape E rend exacte au point courant) que **chaque tour EM ne peut pas faire baisser la vraisemblance** ; l'algorithme converge donc vers un maximum **local**, ce qui impose, comme pour k-means, de relancer plusieurs fois.

> 💡 **k-means est un cas limite d'EM.** Si tous les groupes sont des boules de même variance $\sigma^2$ et de même poids, et que l'on fait tendre $\sigma\to0$, les responsabilités deviennent des $0$ ou des $1$ (le groupe le plus proche l'emporte) : l'étape E devient l'affectation de Lloyd, l'étape M devient le recalcul des centres. Un mélange gaussien est un k-means « avec des nuances ».

**Un tour d'EM à la main.** Quatre valeurs, $0;\ 1;\ 4;\ 6$, deux groupes. Pour que le calcul reste faisable à la main, on simplifie : les deux groupes ont la même variance $\sigma^2=1$ et le même poids $1/2$, et **seules les moyennes** sont à estimer ; on part de $\mu_1=0$ et $\mu_2=3$. La responsabilité du groupe 1 pour une valeur $x$ s'écrit $\gamma_1(x)=1/\big(1+e^{-[(x-\mu_2)^2-(x-\mu_1)^2]/2}\big)$.

- $x=0$ : $(9-0)/2=4{,}5$, donc $\gamma_1=1/(1+e^{-4{,}5})\approx0{,}989$.
- $x=1$ : $(4-1)/2=1{,}5$, donc $\gamma_1\approx0{,}818$.
- $x=4$ : $(1-16)/2=-7{,}5$, donc $\gamma_1\approx0{,}0006$ ; $x=6$ : $\gamma_1\approx0$.

Étape M : $\mu_1=\dfrac{0\times0{,}989+1\times0{,}818+4\times0{,}0006}{0{,}989+0{,}818+0{,}0006}\approx0{,}454$ et, avec $\gamma_2=1-\gamma_1$, $\mu_2=\dfrac{1\times0{,}182+4\times0{,}9994+6\times1}{0{,}011+0{,}182+0{,}9994+1}\approx4{,}642$. Les deux centres se sont rapprochés de leurs vraies valeurs ; deux ou trois tours suffisent.


```text
responsabilités du groupe 1 au tour 1 : [9.890e-01 8.176e-01 6.000e-04 0.000e+00]
tour 0 : mu = [0. 3.]
tour 1 : mu = [0.454 4.642]
tour 2 : mu = [0.504 4.998]
tour 3 : mu = [0.506 5.001]
```

![Trois étapes de l'algorithme EM sur six valeurs : le mélange (bleu) et ses deux composantes (pointillés) au départ, après un tour, puis à la convergence ; la log-vraisemblance $\ell$ augmente.](figures/ch03-em.png)

La bibliothèque confirme les nombres de la main : après un tour, $\mu=(0{,}454;\ 4{,}642)$. Le graphique montre un EM **complet** (moyennes, écarts-types et poids) sur six valeurs : la vraisemblance augmente à chaque tour, ce que garantit la théorie.

**Choisir le nombre de composantes : le critère BIC.** Contrairement à k-means, un GMM possède une **vraisemblance**, donc un critère de sélection de modèle : le **BIC** (*Bayesian Information Criterion*), $\mathrm{BIC}=-2\ln\hat L+q\ln n$, où $q$ est le nombre de paramètres libres. Il récompense l'ajustement et pénalise la complexité (à minimiser). Sur les clients, avec $p=7$ variables et une covariance complète, chaque composante coûte $7+28=35$ paramètres (plus un poids).


```text
 k    BIC  ARI avec la vérité
 1 207243               0.000
 2 180819               0.336
 3 117562               0.276
 4 106300               0.503
 5 104420               0.469
 6 102459               0.407
 7 101505               0.358
 8 101462               0.358
covariance    BIC  ARI avec la vérité
      full 106300               0.503
      diag 114379               0.477
 spherical 197934               0.497
      tied 181073               0.506
part de clients avec probabilité maximale < 0,7 : 0.07
```

![BIC d'un mélange gaussien à covariance complète selon le nombre de composantes (à gauche) et ARI avec la vérité cachée (à droite).](figures/ch03-bic.png)

Le BIC chute violemment jusqu'à $k=4$ (de $117\,562$ à $106\,300$ entre $k=3$ et $k=4$), puis ne gagne plus que de petits montants ($104\,420$ à $k=5$, $102\,459$ à $k=6$, et à peine $43$ de $k=7$ à $k=8$) : le coude est à $4$. Le BIC continue pourtant de décroître lentement, parce que les variables (comptages, montants) ne sont **pas exactement gaussiennes** : de petites composantes supplémentaires servent à épouser les asymétries. À $k=4$, le mélange à covariance complète atteint un ARI de $0{,}503$, un peu mieux que k-means ($0{,}487$).

Le tableau des types de covariance est une mise en garde. La covariance **sphérique** (des boules, comme k-means) a un BIC très mauvais ($197\,934$) mais un ARI quasi identique ($0{,}497$) ; la covariance **complète** a le meilleur BIC ($106\,300$). Le BIC juge **la qualité de l'ajustement de la densité**, l'ARI juge **la qualité de la partition** : ce sont deux objectifs différents, qui ne se classent pas toujours de la même façon.

Enfin, l'intérêt propre du mélange : **$7{,}0\ \%$** des clients ont une probabilité maximale d'appartenance inférieure à $0{,}7$ (et $16{,}8\ \%$ sous $0{,}9$), c'est-à-dire qu'ils sont réellement « entre deux groupes ». Cette incertitude, qu'un k-means tranché cache, est une information utile : on peut réserver les messages très ciblés aux clients dont l'appartenance est sûre.

> ✅ **À retenir (méthodes au-delà de k-means).**
> - **DBSCAN** : groupes = régions denses, forme libre, bruit explicite ; mais un seul rayon $\varepsilon$ (une seule densité), et inadapté à des données en continuum.
> - **Classification hiérarchique** : le **lien** (simple, complet, moyen, Ward) définit la forme des groupes ; coût mémoire en $n^2$.
> - **Mélanges gaussiens** : appartenances **probabilistes**, formes elliptiques, estimation par **EM** (la vraisemblance ne baisse jamais, optimum local) ; le **BIC** guide le choix de $K$.
> - Aucune méthode n'est supérieure en soi : on choisit selon la forme probable des groupes, puis on **valide** avec les épreuves de 3.1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 et 3.6, exercices 3.9 à 3.11.


## 3.4 ➕ Pour aller plus loin : t-SNE et UMAP

> 🧭 **Section optionnelle.** Elle présente les deux méthodes les plus utilisées pour **dessiner** des données de grande dimension. Surtout, elle explique ce que ces dessins permettent de conclure, et ce qu'ils ne permettent **pas** : c'est la partie la plus importante, et celle que la littérature rapide oublie.

L'ACP projette sur un plan en gardant les directions de grande variance : excellente pour comprendre la structure d'ensemble, mais elle écrase les groupes fins quand ils se distinguent par des différences *locales*. Les chiffres manuscrits en sont un exemple : sur un plan d'ACP, les dix chiffres se recouvrent largement. Les méthodes de **plongement non linéaire** visent un autre objectif : que **deux points voisins dans l'espace d'origine restent voisins sur le dessin**. Elles reposent sur l'hypothèse de variété vue en 3.2.7.

### 3.4.1 t-SNE : conserver les voisinages

**t-SNE** (van der Maaten et Hinton, 2008) fonctionne en deux temps.

**(1) Mesurer les voisinages dans l'espace d'origine.** Pour chaque point $\mathbf x_i$, on définit la probabilité que $\mathbf x_j$ soit « choisi comme voisin » de $\mathbf x_i$ par une courbe gaussienne centrée en $\mathbf x_i$ :

$$p_{j\mid i}=\frac{\exp\!\big(-\|\mathbf x_i-\mathbf x_j\|^2/2\sigma_i^2\big)}{\sum_{l\ne i}\exp\!\big(-\|\mathbf x_i-\mathbf x_l\|^2/2\sigma_i^2\big)},\qquad p_{ij}=\frac{p_{j\mid i}+p_{i\mid j}}{2n}.$$

La largeur $\sigma_i$ est choisie **point par point** pour que la distribution $p_{\cdot\mid i}$ ait une **perplexité** donnée, $2^{H(p_{\cdot\mid i})}$, où $H$ est l'entropie de Shannon : la perplexité se lit comme le **nombre effectif de voisins** de chaque point (5 à 50 en pratique). Un point dans une région dense reçoit un $\sigma_i$ petit, un point isolé un $\sigma_i$ grand : chacun a toujours « à peu près le même nombre de voisins ».

**(2) Retrouver ces voisinages sur un dessin.** On place chaque point à une position $\mathbf y_i$ du plan, avec des similarités

$$q_{ij}=\frac{(1+\|\mathbf y_i-\mathbf y_j\|^2)^{-1}}{\sum_{k\ne l}(1+\|\mathbf y_k-\mathbf y_l\|^2)^{-1}},$$

qui utilisent une loi de Student à un degré de liberté (une loi de Cauchy) au lieu d'une gaussienne : ses **queues lourdes** laissent de la place aux groupes, sur un dessin où l'espace manque (c'est le « problème d'entassement » que la gaussienne résout mal). On cherche les positions qui rendent $q$ proche de $p$, en minimisant la **divergence de Kullback–Leibler**

$$\mathrm{KL}(P\,\|\,Q)=\sum_{i\ne j}p_{ij}\ln\frac{p_{ij}}{q_{ij}}$$

par descente de gradient, dont le gradient a une forme simple :

$$\frac{\partial\,\mathrm{KL}}{\partial\mathbf y_i}=4\sum_{j}(p_{ij}-q_{ij})\,(\mathbf y_i-\mathbf y_j)\,(1+\|\mathbf y_i-\mathbf y_j\|^2)^{-1}.$$

Chaque point est **attiré** par ses vrais voisins ($p_{ij}>q_{ij}$) et **repoussé** par les faux ($q_{ij}>p_{ij}$). Le problème n'est pas convexe : le résultat dépend de l'initialisation et du hasard.

### 3.4.2 UMAP : un graphe de voisins, puis un dessin

**UMAP** (McInnes, Healy et Melville, 2018) suit la même logique avec d'autres outils, issus de la topologie. On construit d'abord un **graphe pondéré des plus proches voisins** : chaque point est relié à ses $n_{\text{voisins}}$ plus proches voisins avec un poids qui décroît avec la distance, **recalé sur la distance au voisin le plus proche** (ainsi chaque point est fortement relié à au moins un autre, quelle que soit la densité locale) ; on symétrise le graphe par une union « floue ». On cherche ensuite des positions dans le plan dont le graphe de similarités ressemble à ce graphe, en minimisant une **entropie croisée** par descente de gradient stochastique, avec un échantillonnage de paires éloignées pour la répulsion. Deux paramètres principaux : `n_neighbors` (taille du voisinage local ; petit = détails fins, grand = vue d'ensemble) et `min_dist` (à quel point les points d'un même groupe peuvent se serrer sur le dessin).

Par rapport à t-SNE, UMAP est **plus rapide** (surtout au-delà de quelques milliers de points) et sait **projeter un nouveau point** sur un dessin existant (méthode `transform`), ce que t-SNE ne sait pas faire.

### 3.4.3 Les chiffres manuscrits, vus par trois méthodes

Pour mesurer objectivement la qualité d'un plongement, on utilise la **fiabilité** (*trustworthiness*) : pour chaque point, on regarde ses $k$ plus proches voisins **sur le dessin** et on pénalise ceux qui n'étaient pas parmi ses $k$ plus proches voisins dans l'espace d'origine, d'autant plus que leur rang d'origine est lointain :

$$T(k)=1-\frac{2}{nk(2n-3k-1)}\sum_{i=1}^n\ \sum_{j\in U_i(k)}\big(r(i,j)-k\big),$$

où $U_i(k)$ est l'ensemble des « faux voisins » du point $i$ et $r(i,j)$ le rang de $j$ parmi les voisins de $i$ dans l'espace d'origine. Elle vaut $1$ pour un plongement qui ne crée aucun faux voisin. Nous travaillons sur un échantillon de 800 chiffres (les méthodes sont lentes) et prenons $k=10$.


```text
              méthode  fiabilité (k=10)  fidélité des distances entre chiffres
                  ACP             0.827                                  0.801
  t-SNE, perplexité 5             0.987                                  0.710
 t-SNE, perplexité 30             0.991                                  0.819
t-SNE, perplexité 100             0.984                                  0.836
      UMAP, 5 voisins             0.985                                  0.475
     UMAP, 15 voisins             0.987                                  0.674
     UMAP, 50 voisins             0.984                                  0.701
aires de l'enveloppe convexe de chaque chiffre (t-SNE, perplexité 30) : de 85 à 915 | effectifs de 76 à 90
```

![Les 800 chiffres manuscrits en deux dimensions par ACP et par t-SNE (perplexité 5, 30 et 100). Chaque couleur est un chiffre ; le numéro marque la médiane du chiffre.](figures/ch03-tsne.png)

![Les mêmes chiffres par UMAP, avec 5, 15 et 50 voisins.](figures/ch03-umap.png)

La différence avec l'ACP saute aux yeux : sur le plan de l'ACP, les chiffres se recouvrent ; avec t-SNE et UMAP, **dix îlots** bien séparés apparaissent. La fiabilité le confirme : $0{,}827$ pour l'ACP, de $0{,}984$ à $0{,}991$ pour t-SNE (le meilleur réglage est la perplexité $30$, avec $0{,}991$), de $0{,}984$ à $0{,}987$ pour UMAP. Ces méthodes **préservent remarquablement les voisinages locaux**. Mais regardez la colonne de droite du tableau.

### 3.4.4 Ce qu'on n'a pas le droit de lire sur un dessin

La dernière colonne du tableau mesure la **fidélité des distances entre chiffres** : on calcule le centre de chaque chiffre dans l'espace d'origine puis sur le dessin, et on mesure à quel point les deux classements de distances entre centres concordent (corrélation de rangs de Spearman). Surprise : l'ACP, qui a pourtant un moins bon voisinage local, obtient $0{,}801$, **autant que** les meilleurs t-SNE ($0{,}836$ pour la perplexité $100$, $0{,}819$ pour $30$) et nettement plus qu'UMAP à 15 voisins ($0{,}674$) ou 5 voisins ($0{,}475$). t-SNE à perplexité $5$ ($0{,}710$) est moins fidèle que l'ACP. **Ces méthodes préservent le voisinage local, pas la géométrie globale.** D'où quatre interdits.

1. **Ne pas lire les distances entre groupes.** Deux îlots proches sur le dessin ne sont pas forcément proches dans l'espace d'origine ; deux îlots lointains peuvent l'être aussi peu que d'autres.
2. **Ne pas lire la taille des groupes.** Les algorithmes dilatent les régions denses et contractent les régions clairsemées. Les aires de l'enveloppe convexe de chaque chiffre sur le dessin t-SNE (perplexité $30$) varient de $85$ à $915$ unités (un rapport de plus de $10$) pour des classes de tailles comparables ($76$ à $90$ chiffres).
3. **Ne pas croire aux formes fines.** Un groupe allongé, un « pont » entre deux îlots dépendent des hyperparamètres : en changeant la perplexité de $5$ à $100$ (figure), la disposition d'ensemble et les îlots se réarrangent.
4. **Ne pas oublier que le résultat dépend du hasard.** L'optimisation n'est pas convexe. Avec trois initialisations aléatoires différentes, les dessins diffèrent, même si le fond reste stable.


```text
 graine  fiabilité  ARI des 10 groupes avec les vrais chiffres
      0      0.991                                       0.811
      1      0.990                                       0.807
      2      0.990                                       0.793
ARI entre les groupes des graines 0 et 1 : 0.987 | 0 et 2 : 0.923
```

![Trois exécutions de t-SNE avec des initialisations aléatoires différentes (perplexité 30) : les positions des îlots changent, les voisinages locaux restent.](figures/ch03-tsne-graines.png)

Les trois dessins sont différents (les îlots ne sont pas aux mêmes endroits), mais les **voisinages** restent les mêmes : fiabilité quasi identique ($0{,}990$ à $0{,}991$) et, si on classe les points de chaque dessin en 10 groupes avec k-means, les groupes sont presque les mêmes d'une graine à l'autre (ARI de $0{,}987$ entre les graines 0 et 1, $0{,}923$ entre 0 et 2). La structure *locale* est stable ; la disposition *globale* ne l'est pas.

> ⚠️ **Règle d'usage.** t-SNE et UMAP sont des outils d'**exploration visuelle** : ils suggèrent des hypothèses (ces clients forment-ils un groupe ? cette classe est-elle homogène ?) qu'il faut ensuite **vérifier avec des méthodes quantitatives** (3.1). Ne classez pas sur les coordonnées d'un plongement sans précaution, et ne publiez jamais un dessin sans préciser la méthode, ses hyperparamètres et la graine. Pour la reproductibilité : fixer `random_state`, préférer l'initialisation par ACP (`init="pca"`, plus stable pour la disposition globale) et noter le nombre de points.

### 3.4.5 Un dernier regard : les clients de la boutique

Que donne UMAP sur nos clients, dont on connaît la vérité cachée ?


```text
 îlot  clients  segment majoritaire  part du segment  commandes (moy.)  départ à 90 j
    0      135                    0             0.83              0.00          0.378
    1      673                    1             0.42              4.23          0.064
    2      192                    2             1.00              4.20          0.193
fiabilité de UMAP sur 1 000 clients : 0.967
ARI avec la vérité, k-means sur les 7 variables : 0.491 | k-means sur le plan UMAP : 0.514
```

![UMAP de 1 000 clients de la boutique, coloré par le vrai segment caché (à gauche) puis par le départ à 90 jours (à droite).](figures/ch03-umap-clients.png)

Contrairement aux chiffres, le dessin ne montre pas dix îlots nets : il en montre **deux très nets** et un grand nuage. Pour les isoler objectivement, on regroupe les points du plan par DBSCAN ($\varepsilon=0{,}6$), ce qui donne le tableau ci-dessus.

- L'**îlot 2** (192 clients) est composé à $100\ \%$ de « chasseurs de promotions » (vrai segment 2) : leur comportement est si particulier qu'aucun autre client ne leur ressemble.
- L'**îlot 0** (135 clients, $83\ \%$ d'occasionnels) rassemble des clients qui n'ont **aucune commande** dans l'année (moyenne de $0{,}00$) et qui partent à $37{,}8\ \%$ : ce sont les **dormants** repérés en 3.1.7.
- Le reste (673 clients) est un **nuage continu** où les fidèles ne forment que $42\ \%$ du total, mêlés aux grands paniers et aux occasionnels : c'est précisément la zone que k-means n'arrivait pas à séparer, et le plongement ne la sépare pas non plus.

Le plongement est fidèle aux voisinages (fiabilité de $0{,}967$), mais k-means sur le plan UMAP ne retrouve qu'à peine mieux la vérité que k-means sur les variables d'origine (ARI de $0{,}514$ contre $0{,}491$). Le dessin a donc **confirmé** ce que les épreuves de 3.1 laissaient voir (des segments tranchés pour les comportements extrêmes, un continuum pour les autres) sans rien révéler de nouveau. Un dessin séduisant n'est pas une preuve de groupes, mais il aide à comprendre **où** la structure existe et où elle n'existe pas.

> ✅ **À retenir (t-SNE et UMAP).**
> - Objectif : conserver les **voisinages locaux** (t-SNE : divergence de Kullback–Leibler entre voisinages gaussiens et de Student ; UMAP : graphe flou de voisins et entropie croisée).
> - La **fiabilité** (trustworthiness) mesure la qualité locale ; ces méthodes la poussent très haut, bien au-delà de l'ACP.
> - Mais **la géométrie globale n'est pas conservée** : on ne lit ni les distances entre groupes, ni leur taille, ni les formes fines ; le résultat dépend de la perplexité, du nombre de voisins et de la graine.
> - Ce sont des outils d'**exploration**, pas de démonstration : toute hypothèse lue sur un dessin se vérifie avec les épreuves de 3.1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7, exercice 3.12.


## Bilan du chapitre 3

Vous savez maintenant :

- **juger un découpage sans bonne réponse** : critères internes (inertie, silhouette, Calinski–Harabasz, Davies–Bouldin), comparaison à une **référence sans structure** (silhouette comparée, statistique de l'écart, avec l'importance du choix de la référence), **stabilité** par sous-échantillonnage, **indice de Rand ajusté** et information mutuelle normalisée quand une vérité existe, et surtout **utilité** des groupes pour une décision ;
- repérer ce qui décide du résultat avant l'algorithme : l'**échelle** des variables (un ARI de $0{,}49$ tombe à $0{,}08$ sans standardisation) et le **choix des variables** ;
- expliquer la **malédiction de la dimension** (les distances se resserrent en $1/\sqrt d$) et choisir une méthode de réduction : **ACP** (erreur de reconstruction = un moins la variance gardée, théorème d'Eckart–Young), **ACP à noyau** pour le non-linéaire, **SVD tronquée** pour le parcimonieux, **NMF** pour des parties lisibles, **projections aléatoires** et lemme de **Johnson–Lindenstrauss** ;
- fixer le nombre de dimensions par l'**utilité en aval**, validée par validation croisée ;
- (en option) utiliser **DBSCAN** (groupes denses, bruit explicite, rayon $\varepsilon$ unique), les **liens** de la classification hiérarchique (le lien simple retrouve des formes allongées), et les **mélanges gaussiens** estimés par **EM** (appartenances probabilistes, BIC) ;
- (en option) dessiner des données en haute dimension avec **t-SNE** et **UMAP**, mesurer leur **fiabilité**, et **ne pas lire** distances entre groupes, tailles et formes fines.

Trois messages à garder en mémoire. **Un résultat non supervisé se valide par plusieurs épreuves qui se rejoignent**, jamais par un seul chiffre. **Une méthode rend toujours un résultat** : la référence sans structure est votre meilleur garde-fou. Et **réduire n'est pas neutre** : son effet se mesure, il ne se suppose pas.

Le chapitre 4 revient aux **modèles supervisés** par l'angle le plus concret : les variables. Avant d'entraîner un modèle, il faut les encoder, les mettre à l'échelle, les fabriquer, les sélectionner, et composer avec des classes déséquilibrées. Beaucoup de gains en apprentissage automatique se jouent là.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8, exercices 3.1 à 3.12.
