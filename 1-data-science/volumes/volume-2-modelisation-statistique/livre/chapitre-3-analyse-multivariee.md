# Chapitre 3 : Analyse multivariée

> « Une variable, on la regarde. Deux variables, on les relie.
> Vingt variables, il faut apprendre à les **résumer**. »

Les chapitres 1 et 2 avaient un point commun : une variable **à expliquer** (la dépense, le rachat, le nombre de commandes) et des variables **explicatives**. Ici, le décor change. Nous n'avons plus de variable réponse : nous avons **un tableau de variables**, et la question est « que contient ce tableau ? ». Quelles variables disent la même chose ? Peut-on les remplacer par deux ou trois indicateurs qui conservent l'essentiel ? Les clients se rangent-ils naturellement en familles ? C'est ce qu'on appelle l'**analyse multivariée**, ou, dans le vocabulaire de l'apprentissage automatique, l'apprentissage **non supervisé** : on cherche de la structure sans qu'aucune « bonne réponse » ne guide la recherche.

La gérante a posé ces questions sans le savoir. Elle a envoyé à ses clientes un petit questionnaire de huit questions et se retrouve avec huit colonnes de notes qui se ressemblent beaucoup : « Les clientes qui aiment la qualité des vases aiment aussi celle des écharpes, non ? » Elle voudrait **un ou deux chiffres par cliente** plutôt que huit. Et elle voudrait aussi savoir si ses 2 000 clientes forment des « types » (les occasionnelles, les fidèles, les grosses acheteuses) à qui s'adresser différemment.

## Le chemin de ce chapitre

- **3.1 Analyse en composantes principales (ACP)** : la technique reine pour **résumer** des variables numériques corrélées. Nous la construirons à la main sur cinq clientes, la démontrerons proprement (c'est un problème d'optimisation, avec les valeurs propres du volume I), puis l'appliquerons au questionnaire.
- **3.2 Analyse factorielle** : un modèle voisin mais différent. L'ACP **résume** ; l'analyse factorielle **explique** les corrélations par des causes cachées (des « facteurs »), comme la qualité du service. Nous apprendrons à les estimer, à les faire tourner (rotation), et à vérifier si l'on retrouve ce que la simulation avait programmé.
- **3.3 Classification non supervisée** : les **k-means** et la **classification hiérarchique**, avec leurs pièges, et une segmentation honnête des clientes de la boutique.
- ➕ **3.4 Analyse des correspondances (AC et ACM)** : l'équivalent de l'ACP pour des **variables qualitatives** (canal, ville, tranche d'âge).
- ➕ **3.5 Analyse discriminante** : quand les groupes sont connus d'avance et que l'on cherche la meilleure frontière entre eux ; le lien avec la régression logistique de la section 2.2.
- **Bilan du chapitre**, puis, dans le **cahier**, les exercices corrigés et les applications guidées.

> 📒 **Comment travailler avec ce chapitre.** Le livre explique chaque méthode avec un exemple calculé à la main, puis en montre le résultat sur les données (chiffres et figures). Les algorithmes de ce chapitre sont courts : le cahier (chapitre 3) vous les fait écrire **vous-même** en NumPy avant d'utiliser `scikit-learn`, puis compare les deux. Si votre version et celle de la bibliothèque donnent les mêmes nombres, vous avez compris l'algorithme. Un conseil : à chaque figure, **prédisez ce que vous allez voir** avant de lire la légende.

> 🧭 **Ce que vous devez avoir en tête du volume I.** Le chapitre s'appuie sur les valeurs propres et la décomposition en valeurs singulières (volume I, sections 1.1.3 et 1.1.4), sur la covariance et la corrélation (volume I, sections 2.3 et 3.1.7) et sur les multiplicateurs de Lagrange (volume I, section 1.3.5). Si ces notions sont floues, relisez-les d'abord : l'ACP n'en est, au fond, que l'application directe.

> 📦 **Les données.** Deux fichiers du dossier `donnees/`, **entièrement simulés** :
> - `enquete_satisfaction.csv` : 1 212 répondantes (60 % des clientes, tirées au hasard) et leurs huit notes de 1 à 5, `q1` à `q8`. Les quatre premières portent sur les **produits** (qualité, finitions…), les quatre dernières sur le **service** (livraison, emballage…).
> - `clients.csv` : les 2 000 clientes, avec âge, canal d'acquisition, nombre de commandes, panier moyen, dépense annuelle et durée de la relation.
>
> Comme les données sont simulées, nous connaîtrons **la vérité** et nous la révélerons à la fin de chaque étude pour juger de la qualité de nos méthodes. Dans la vraie vie, cette vérité n'est jamais disponible : c'est précisément ce qui rend les méthodes de ce chapitre difficiles à valider, et ce qui impose la prudence que nous cultiverons à chaque page.


## 3.1 Analyse en composantes principales

> 💡 **Intuition.** Vous photographiez une sculpture. Sous certains angles, la photo est plate et on ne comprend rien ; sous d'autres, on voit tout de suite la forme. L'**analyse en composantes principales** (ACP) cherche **l'angle de prise de vue qui garde le plus d'information possible** quand on aplatit un nuage de points en haute dimension vers une dimension plus petite. Ici, « information » veut dire **variance** : on garde les directions dans lesquelles les données s'étalent le plus, et on jette celles où elles sont presque constantes.

### 3.1.1 Le problème : huit colonnes qui se ressemblent

Reprenons le questionnaire de la gérante. Voici la **matrice de corrélation** de ses huit questions (volume I, section 3.1.7), représentée en couleurs (chaque case donne la corrélation entre deux questions) :


![Matrice de corrélation des huit questions du questionnaire : deux blocs de questions corrélées entre elles (q1 à q4, q5 à q8), faiblement corrélés entre eux.](figures/ch03-correlations-enquete.png)

Regardez la structure en blocs. Les questions `q1` à `q4` sont toutes corrélées entre elles (de 0,3 à 0,5 environ), de même que `q5` à `q8` (de 0,4 à 0,55), alors que les corrélations **entre** les deux groupes sont faibles (autour de 0,1). Autrement dit, ce tableau de huit colonnes contient probablement **deux informations** : un niveau d'appréciation des produits, un niveau d'appréciation du service. Si c'est vrai, deux nombres par répondante devraient suffire à résumer les huit notes sans trop de perte.

L'ACP est la méthode qui transforme cette intuition visuelle en calcul : elle trouve automatiquement les « bonnes » directions.

### 3.1.2 Un exemple à la main : cinq clientes, deux variables

Avant les huit dimensions, restons dans le plan, où l'on peut tout dessiner. Cinq clientes, deux variables : le **nombre de commandes** dans l'année et le **panier moyen**, exprimé ici en **dizaines de €** pour garder des nombres simples (nous verrons en 3.1.5 pourquoi ce choix d'unité n'est pas innocent).

| Cliente | Commandes ($x$) | Panier en dizaines de € ($y$) |
|---|---|---|
| A | 4 | 4 |
| B | 5 | 3 |
| C | 6 | 6 |
| D | 7 | 5 |
| E | 8 | 7 |

**Étape 1 : centrer.** Les moyennes sont $\bar x=6$ et $\bar y=5$. Les écarts à la moyenne valent donc $x_c=(-2,-1,0,1,2)$ et $y_c=(-1,-2,1,0,2)$. Le nuage est maintenant centré sur l'origine.

**Étape 2 : la matrice de covariance.** Avec le diviseur $n-1=4$ (volume I, section 3.2.3) :

$$s_{xx}=\frac{4+1+0+1+4}{4}=2{,}5,\qquad s_{yy}=\frac{1+4+1+0+4}{4}=2{,}5,\qquad s_{xy}=\frac{2+2+0+0+4}{4}=2.$$

$$S=\begin{pmatrix}2{,}5&2\\2&2{,}5\end{pmatrix}.$$

**Étape 3 : les valeurs propres.** On résout $\det(S-\lambda I)=0$ :
$(2{,}5-\lambda)^2-4=0$, donc $2{,}5-\lambda=\pm2$, soit $\lambda_1=4{,}5$ et $\lambda_2=0{,}5$.

**Étape 4 : les vecteurs propres.** Pour $\lambda_1=4{,}5$, $(S-4{,}5I)v=0$ donne $-2v_1+2v_2=0$, donc $v_1=v_2$ : le vecteur unitaire est $\mathbf v_1=\tfrac{1}{\sqrt2}(1,1)$. Pour $\lambda_2=0{,}5$, on trouve $\mathbf v_2=\tfrac1{\sqrt2}(1,-1)$. Ils sont bien orthogonaux.

**Étape 5 : interpréter.** La variance totale est $2{,}5+2{,}5=5$ (c'est la trace de $S$) et $\lambda_1+\lambda_2=5$ aussi : l'ACP **redistribue** la variance totale entre les nouveaux axes, sans en perdre. Le premier axe en porte $4{,}5/5=90\ \%$. Sa direction $(1,1)/\sqrt2$ dit : « plus on commande, plus le panier est gros », c'est l'axe **« valeur de la cliente »**. Le deuxième axe, $(1,-1)/\sqrt2$, oppose les grosses commandeuses à petit panier aux petites commandeuses à gros panier.

**Étape 6 : les scores.** Le *score* d'une cliente sur l'axe $j$ est sa coordonnée dans la nouvelle base : $t_{ij}=\mathbf v_j^\top\mathbf x_{c,i}$. Pour la cliente A, $\mathbf x_c=(-2,-1)$, donc $t_{A1}=(-2-1)/\sqrt2\approx-2{,}12$ et $t_{A2}=(-2+1)/\sqrt2\approx-0{,}71$. 


Un logiciel retrouve ces nombres : valeurs propres $4{,}5$ et $0{,}5$, variances des scores $4{,}5$ et $0{,}5$, scores de la cliente A égaux à $-2{,}12$ et $\pm0{,}71$. Le signe d'un vecteur propre est arbitraire (si $\mathbf v$ convient, $-\mathbf v$ aussi) : un logiciel peut renvoyer $(-0{,}707;\,-0{,}707)$ au lieu de $(0{,}707;\,0{,}707)$, ou le signe opposé pour le second axe, c'est le même axe. Remarquez aussi que la **variance de chaque score** est égale à la valeur propre correspondante, et que les deux scores sont **non corrélés**. Ce n'est pas un hasard, nous le démontrons plus bas.

![Les cinq clientes dans le plan commandes x panier (en dizaines de €), les deux axes principaux (en trait plein, le premier ; en pointillés, le second) et les projections sur le premier axe.](figures/ch03-acp-2d.png)

> 🧪 **Ce que la figure montre.** Projeter les cinq points sur le premier axe (la droite de plus grande dispersion) conserve 90 % de la variance : on résume le nuage par **un seul nombre par cliente** en ne perdant que 10 %. Les segments gris sont ce qu'on jette. Projeter sur le second axe, au contraire, écraserait presque tout.

### 3.1.3 La théorie : l'ACP est un problème d'optimisation

Cherchons la direction (un vecteur unitaire $\mathbf v$) sur laquelle la variance des projections est maximale. Pour un tableau centré $X_c$ de $n$ lignes et $p$ colonnes, de matrice de covariance $S=\frac1{n-1}X_c^\top X_c$, la projection de la ligne $i$ est $\mathbf v^\top\mathbf x_{c,i}$ et la variance des projections vaut

$$\operatorname{Var}(X_c\mathbf v)=\frac1{n-1}\,\mathbf v^\top X_c^\top X_c\,\mathbf v=\mathbf v^\top S\,\mathbf v.$$

> 📐 **Théorème (première composante).** Le maximum de $\mathbf v^\top S\mathbf v$ sous la contrainte $\|\mathbf v\|=1$ est la plus grande valeur propre $\lambda_1$ de $S$, atteinte en un vecteur propre associé.
>
> **Démonstration.** On utilise les multiplicateurs de Lagrange (volume I, section 1.3.5). Le lagrangien est $\mathcal L(\mathbf v,\lambda)=\mathbf v^\top S\mathbf v-\lambda(\mathbf v^\top\mathbf v-1)$. Comme $S$ est symétrique, le gradient en $\mathbf v$ vaut $2S\mathbf v-2\lambda\mathbf v$. Il s'annule si et seulement si $S\mathbf v=\lambda\mathbf v$ : **tout point critique est un vecteur propre**. En un tel point, la valeur à maximiser est $\mathbf v^\top S\mathbf v=\lambda\,\mathbf v^\top\mathbf v=\lambda$. Le maximum est donc la plus grande des valeurs propres. $\square$
>
> **Les composantes suivantes.** On cherche ensuite le vecteur unitaire de variance maximale **parmi ceux orthogonaux au premier**. Le même raisonnement, avec une contrainte d'orthogonalité supplémentaire, conduit au deuxième plus grand $\lambda_2$ et à son vecteur propre. Et ainsi de suite : les directions de l'ACP sont les vecteurs propres de $S$ rangés par valeur propre décroissante.

Trois conséquences à connaître, toutes immédiates :

1. **Les scores sont non corrélés.** Si $t_j=X_c\mathbf v_j$, alors $\operatorname{Cov}(t_i,t_j)=\mathbf v_i^\top S\mathbf v_j=\lambda_j\,\mathbf v_i^\top\mathbf v_j=0$ pour $i\neq j$, car les vecteurs propres d'une matrice symétrique sont orthogonaux (volume I, section 1.1.3).
2. **La variance du score $j$ vaut $\lambda_j$** : $\operatorname{Var}(t_j)=\mathbf v_j^\top S\mathbf v_j=\lambda_j$.
3. **La variance totale est conservée** : $\sum_j\lambda_j=\operatorname{tr}(S)=\sum_j s_{jj}$. La part de variance expliquée par la composante $j$ est donc $\lambda_j/\operatorname{tr}(S)$.

> 💡 **Lecture géométrique.** L'ACP est une **rotation** du nuage de points : on choisit de nouveaux axes, orthogonaux, le premier dans la direction de plus grande dispersion, le deuxième dans la plus grande dispersion restante, etc. Aucune information n'est perdue tant que l'on garde **tous** les axes ; c'est quand on **en jette** (les derniers) que l'on compresse.

### 3.1.4 L'ACP par la décomposition en valeurs singulières

En pratique, on ne forme pas la matrice de covariance : on décompose directement le tableau centré par la **SVD** (volume I, section 1.1.4), $X_c=U\Sigma V^\top$. Alors $X_c^\top X_c=V\Sigma^2V^\top$, donc les colonnes de $V$ sont les vecteurs propres de $S$, et

$$\lambda_j=\frac{\sigma_j^2}{n-1},\qquad \text{scores}=X_cV=U\Sigma.$$

C'est numériquement plus stable (nous avons vu au volume I, section 1.5.4, que former $X^\top X$ élève au carré le conditionnement). 


Sur les huit questions, un contrôle numérique montre que les deux routes (valeurs propres de la covariance, ou SVD du tableau centré) donnent les mêmes valeurs propres, $2{,}4143$ ; $1{,}6167$ ; $0{,}5921$… à la précision machine (écart de l'ordre de $10^{-15}$), et que $U\Sigma=X_cV$. Les bibliothèques font ce calcul pour nous. Voici la version de `scikit-learn`, qui utilise la SVD en interne (`Q` désigne le tableau des huit notes) :

```python
from sklearn.decomposition import PCA

pca = PCA().fit(Q)
print(pca.explained_variance_ratio_.round(3))
```
<!--sortie-->
```text
[0.352 0.236 0.086 0.074 0.07  0.068 0.059 0.056]
```

### 3.1.5 Faut-il standardiser ? Le piège des unités

L'ACP maximise la variance. Or la variance dépend des **unités** : exprimer un panier en centimes de euro plutôt qu'en euros multiplie sa variance par dix mille, et l'ACP ne verrait plus que lui. Voyons-le sur la table des clientes, avec cinq variables d'échelles très différentes : l'âge, le nombre de commandes, le panier moyen, la dépense annuelle et la durée de la relation.


La dépense annuelle (en €, jusqu'à plus de 2 000) a une variance plusieurs milliers de fois supérieure à celle du nombre de commandes (88 322 contre 13,3). Sans précaution, l'ACP va simplement redécouvrir… la dépense.


Voici la première direction de l'ACP dans les deux cas :

| Variable | Sans standardiser | Standardisé |
|---|---:|---:|
| `age` | 0,00 | 0,10 |
| `nb_commandes_an` | 0,01 | 0,58 |
| `panier_moyen` | 0,06 | 0,49 |
| `depense_annuelle` | **1,00** | 0,64 |
| `duree_mois` | 0,00 | 0,07 |
| *part de variance de la 1re composante* | *98,8 %* | *44,2 %* |

Sans standardisation, la première composante absorbe près de 99 % de la variance et pointe presque entièrement sur `depense_annuelle` (saturation de 1,0, contre 0,06 pour le panier) : c'est un artefact de l'unité, pas une découverte. Après standardisation (centrer **et réduire** chaque variable à un écart-type de 1), chaque variable pèse autant au départ, et la première composante n'absorbe plus que 44 % de la variance et mélange nombre de commandes, panier et dépense (0,58, 0,49 et 0,64), tandis que l'âge et la durée de la relation y pèsent très peu : c'est l'**activité d'achat**, une information qui a un vrai sens.

> ⚠️ **La règle pratique.** Standardisez dès que vos variables ont des **unités ou des échelles différentes**. Faire l'ACP sur les données standardisées revient à diagonaliser la **matrice de corrélation** (c'est la convention de la plupart des logiciels : on dit « ACP normée »). Ne pas standardiser n'a de sens que si toutes les variables sont dans la même unité et que les différences d'échelle sont **informatives** (par exemple, des notes toutes sur 5).

> 🧪 **Un détail à retenir.** Pour une ACP normée de $p$ variables, la variance totale est $p$ (chaque variable standardisée a une variance de 1). La **règle de Kaiser** dit alors : une composante est « intéressante » si sa valeur propre dépasse 1, c'est-à-dire si elle explique plus de variance qu'**une seule variable d'origine**. Nous verrons au 3.1.6 pourquoi cette règle est pratique mais grossière.

### 3.1.6 Lire une ACP : éboulis, saturations, scores

Revenons au questionnaire (les notes sont toutes sur 5, mais nous standardiserons quand même pour travailler sur la matrice de corrélation). Trois outils pour lire une ACP.

**1. L'éboulis des valeurs propres : combien de composantes garder ?**

```text
     valeur propre  part de variance  part cumulée
CP1          2.797             0.350         0.350
CP2          1.894             0.237         0.586
CP3          0.712             0.089         0.675
CP4          0.578             0.072         0.748
CP5          0.562             0.070         0.818
CP6          0.550             0.069         0.887
CP7          0.475             0.059         0.946
CP8          0.433             0.054         1.000
```

Trois critères pour choisir le nombre de composantes à garder :

- **L'éboulis (coude)** : on cherche le point où la courbe des valeurs propres cesse de chuter brutalement pour devenir un plateau. Ici, il y a un « coude » net après la deuxième composante.
- **La règle de Kaiser** : on garde les valeurs propres supérieures à 1. Elle en retient deux.
- **L'analyse parallèle**, plus rigoureuse : on compare les valeurs propres observées à celles que donneraient des données **sans structure** (huit variables indépendantes, même effectif). On ne garde que les composantes qui font mieux que le hasard.

```text
     observée  seuil du hasard (95 %)  on garde ?
CP1     2.797                   1.160        True
CP2     1.894                   1.107        True
CP3     0.712                   1.067       False
CP4     0.578                   1.033       False
CP5     0.562                   1.003       False
CP6     0.550                   0.976       False
CP7     0.475                   0.947       False
CP8     0.433                   0.915       False
```

> 📐 **Pourquoi des valeurs propres de données aléatoires dépassent 1.** Même avec des variables parfaitement indépendantes, les corrélations empiriques ne sont pas exactement nulles ($n$ est fini). Les valeurs propres de la matrice de corrélation sont alors étalées autour de 1 : la première est supérieure à 1, la dernière inférieure. L'analyse parallèle mesure **de combien** : c'est un seuil calibré sur le bruit, plus honnête que le « 1 » de Kaiser.

**2. Les saturations (loadings) : que veut dire chaque axe ?**

Les colonnes de $V$ sont les **directions** des composantes. Pour interpréter, on préfère souvent les **corrélations entre les variables d'origine et les composantes**. Pour des variables standardisées, $\operatorname{cor}(x_i,t_j)=v_{ij}\sqrt{\lambda_j}$ (démonstration : $\operatorname{Cov}(x_i,t_j)=(S\mathbf v_j)_i=\lambda_jv_{ij}$, puis on divise par les écarts-types $1$ et $\sqrt{\lambda_j}$).

```text
     CP1   CP2  cos² (qualité sur CP1-CP2)
q1  0.56  0.58                        0.65
q2  0.52  0.54                        0.56
q3  0.57  0.51                        0.58
q4  0.48  0.47                        0.45
q5  0.68 -0.45                        0.66
q6  0.64 -0.39                        0.56
q7  0.64 -0.48                        0.64
q8  0.61 -0.44                        0.57
```

La première composante a des corrélations **de même signe pour les huit questions** : c'est une dimension de **satisfaction générale** (les répondantes qui notent bien une chose notent bien le reste). La deuxième **oppose** les questions sur les produits (`q1` à `q4`) à celles sur le service (`q5` à `q8`) : c'est la dimension « produit plutôt que service, ou l'inverse ». Le signe global d'un axe est arbitraire (nous avons adopté la convention « la plus grande saturation est positive », ce qui rend CP1 positive pour toutes les questions), mais les **contrastes** entre variables, eux, ont un sens. Le `cos²` indique quelle fraction de la variance de la question est restituée par le plan des deux premières composantes.

> ⚠️ **Ne confondez pas direction et corrélation.** Les éléments de $V$ sont des coefficients de combinaison linéaire (la composante est $\sum_i v_{ij}\,x_i$) ; les corrélations $v_{ij}\sqrt{\lambda_j}$ sont les quantités que l'on compare entre variables. Les deux sont proportionnelles pour une composante donnée, mais seules les corrélations sont comparables d'une composante à l'autre.

**3. Le biplot : variables et individus sur la même carte.**

![À gauche : éboulis des valeurs propres du questionnaire, avec le seuil de Kaiser et le seuil de l'analyse parallèle. À droite : biplot du plan CP1-CP2 : un point par répondante (échantillon de 300), une flèche par question.](figures/ch03-acp-eboulis-biplot.png)

Le biplot superpose les **scores** des répondantes (les points) et les **corrélations** des variables (les flèches). Deux flèches proches signalent des questions corrélées ; une flèche longue est bien représentée par le plan ; une répondante située du côté d'une flèche a une note élevée à cette question. Remarquez que les flèches se répartissent en **deux faisceaux** : produits d'un côté du deuxième axe, service de l'autre. L'ACP a retrouvé les deux blocs que l'œil voyait dans la matrice de corrélation.

### 3.1.7 Compression et reconstruction

Garder $k$ composantes revient à **approcher** le tableau centré par sa projection : $\hat X_c=T_kV_k^\top=X_cV_kV_k^\top$ (matrice de rang $k$). Le théorème d'**Eckart-Young** dit que c'est la **meilleure** approximation de rang $k$ au sens des moindres carrés, et que l'erreur est exactement la somme des carrés des valeurs singulières jetées. En termes de valeurs propres de la matrice de corrélation, pour des données standardisées :

$$\sum_{i,l}\bigl(Z_{il}-\hat Z_{il}\bigr)^2=(n-1)\sum_{j>k}\lambda_j.$$

Un contrôle numérique sur le questionnaire confirme cette égalité pour chaque $k$ de 1 à 8 : pour $k=2$, l'erreur de reconstruction vaut $4\,007{,}48$ des deux côtés ; pour $k=7$, $524{,}38$ ; pour $k=8$, zéro.


L'erreur de reconstruction décroît à mesure qu'on garde de composantes, jusqu'à devenir nulle pour $k=8$ (on garde tout). Elle est **exactement** égale à ce qu'annonce le théorème : la valeur propre d'une composante mesure donc très concrètement **ce que l'on perd** en l'abandonnant.

Les deux premiers scores sont précisément les « un ou deux chiffres par cliente » que voulait la gérante. Reste à voir s'ils disent quelque chose du comportement d'achat : c'est l'objet de l'application 3.1 du cahier.

### 3.1.8 Les pièges de l'ACP

> ⚠️ **1. Le signe et l'ordre ne sont pas la vérité.** Un axe peut être retourné sans changer le modèle, et deux valeurs propres voisines donnent des axes **instables** (un peu de bruit les mélange). Si $\lambda_2\approx\lambda_3$, n'interprétez pas séparément CP2 et CP3.
>
> **2. Linéaire seulement.** L'ACP ne voit que les relations **linéaires**. Un nuage en forme de croissant (corrélation nulle, structure évidente) lui échappe.
>
> **3. Sensible aux valeurs extrêmes.** Quelques points très éloignés peuvent à eux seuls orienter un axe, puisque la variance est un critère quadratique.
>
> **4. Interprétable ne veut pas dire vrai.** Une composante est une combinaison **mathématiquement optimale**, pas forcément une **cause** réelle. Si vous voulez dire « il existe un facteur caché de qualité de service », il faut un autre outil, qui postule explicitement des facteurs : l'analyse factorielle (section 3.2).
>
> **5. Pas d'inférence.** L'ACP est une technique **descriptive** : elle n'a ni p-valeur ni intervalle de confiance (sauf à utiliser le bootstrap, volume I, section 3.3.5). Elle décrit **ce tableau**, pas la population.
>
> **6. Des notes ordinales.** Nos questions sont notées de 1 à 5, ce qui n'est pas une variable continue au sens strict (volume I, section 3.1.1). L'ACP sur ces notes fonctionne bien en pratique (on traite la note comme un nombre), mais pour des échelles très courtes ou très déséquilibrées, on préfère des corrélations adaptées (polychoriques).

> ✅ **À retenir**
> - L'ACP cherche des **axes orthogonaux de variance maximale** : ce sont les vecteurs propres de la matrice de covariance, rangés par valeur propre décroissante ; la valeur propre est la **variance** du score correspondant.
> - On la calcule par la **SVD** du tableau centré ; scores $=X_cV=U\Sigma$ et $\lambda_j=\sigma_j^2/(n-1)$.
> - **Standardisez** quand les unités diffèrent : sinon l'ACP ne retrouve que la variable de plus grande variance.
> - Pour choisir le nombre de composantes : éboulis, règle de Kaiser, mieux, **analyse parallèle**.
> - On interprète les **corrélations variable-composante** ; les scores sont les coordonnées des individus ; le **biplot** réunit les deux.
> - Garder $k$ composantes est la **meilleure approximation de rang $k$** ; l'erreur vaut la somme des valeurs propres jetées.
> - L'ACP **résume**, elle ne **postule pas de causes** : c'est le rôle de l'analyse factorielle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.5.


## 3.2 Analyse factorielle

> 💡 **Intuition.** Quand vous prenez la température d'un malade avec trois thermomètres, les trois valeurs diffèrent un peu, mais elles « parlent » toutes de la **même chose** : la vraie température, que vous ne voyez pas directement. L'**analyse factorielle** repose sur la même idée : derrière des variables observées corrélées, il y a un petit nombre de **facteurs cachés** (la qualité du service, le goût pour les produits…). Chaque variable observée est un **thermomètre imparfait** d'un facteur : elle contient une part du facteur et une part qui lui est propre (le bruit de mesure, l'effet de la formulation de la question). L'ACP **résume** des variables ; l'analyse factorielle **modélise** la façon dont elles ont été engendrées.

### 3.2.1 Un exemple à la main : trois thermomètres, un facteur

Trois questions sur le service, standardisées (moyenne 0, variance 1). Leurs corrélations sont $r_{12}=0{,}72$, $r_{13}=0{,}63$ et $r_{23}=0{,}56$. Supposons qu'un seul facteur $f$ (de variance 1) explique tout :

$$x_i=\ell_i\,f+\varepsilon_i,\qquad \operatorname{Var}(\varepsilon_i)=\psi_i,\qquad \varepsilon_i\text{ indépendants entre eux et de }f.$$

Les $\ell_i$ s'appellent les **saturations** (*loadings*) et $\psi_i$ l'**unicité** de la variable $i$. Comme $x_i$ est standardisée, $1=\operatorname{Var}(x_i)=\ell_i^2+\psi_i$. Et pour deux variables différentes, comme les bruits sont indépendants :

$$r_{ij}=\operatorname{Cov}(x_i,x_j)=\ell_i\,\ell_j.$$

Nous avons donc trois équations pour trois inconnues : $\ell_1\ell_2=0{,}72$, $\ell_1\ell_3=0{,}63$, $\ell_2\ell_3=0{,}56$. En multipliant les deux premières et en divisant par la troisième :

$$\ell_1^2=\frac{r_{12}\,r_{13}}{r_{23}}=\frac{0{,}72\times0{,}63}{0{,}56}=0{,}81,\qquad\text{donc }\ell_1=0{,}9,\ \ \ell_2=\frac{0{,}72}{0{,}9}=0{,}8,\ \ \ell_3=\frac{0{,}63}{0{,}9}=0{,}7.$$

La **communalité** $h_i^2=\ell_i^2$ est la part de la variance de la variable expliquée par le facteur commun : $0{,}81$, $0{,}64$, $0{,}49$. Les **unicités** sont les compléments à 1 : $\psi=(0{,}19;\ 0{,}36;\ 0{,}51)$. La première question est donc un excellent thermomètre du facteur (81 % de sa variance en vient), la troisième un thermomètre médiocre (49 %).


> 💡 **Pourquoi trois variables au minimum ?** Avec deux variables, on a une équation ($\ell_1\ell_2=r_{12}$) pour deux inconnues : une infinité de solutions. Avec trois, le modèle à un facteur est exactement identifié. Avec quatre ou plus, il devient **testable** : il impose des contraintes sur les corrélations (comme $r_{12}r_{34}=r_{13}r_{24}$), qui peuvent être vraies ou fausses. C'est ce qui distingue l'analyse factorielle de l'ACP : c'est un **modèle**, que les données peuvent contredire.

### 3.2.2 Le modèle général

Avec $p$ variables et $k$ facteurs, on écrit, pour un vecteur d'observations centré $\mathbf x\in\mathbb R^p$ :

$$\mathbf x=\Lambda\,\mathbf f+\boldsymbol\varepsilon,\qquad \mathbb E[\mathbf f]=0,\ \operatorname{Var}(\mathbf f)=I_k,\qquad \mathbb E[\boldsymbol\varepsilon]=0,\ \operatorname{Var}(\boldsymbol\varepsilon)=\Psi\ (\text{diagonale}),\qquad \mathbf f\perp\boldsymbol\varepsilon.$$

$\Lambda$ est la matrice $p\times k$ des saturations. La matrice de covariance de $\mathbf x$ s'en déduit immédiatement :

$$\boxed{\Sigma=\Lambda\Lambda^\top+\Psi.}$$

Tout est là : le modèle dit que les **covariances** (les termes hors diagonale de $\Sigma$) viennent **uniquement** des facteurs communs ; les termes diagonaux sont la somme d'une part commune $\sum_j\ell_{ij}^2=h_i^2$ et d'une part propre $\psi_i$.

> 📐 **L'indétermination des rotations.** Soit $T$ une matrice orthogonale $k\times k$ ($TT^\top=I$). Remplaçons $\Lambda$ par $\Lambda^*=\Lambda T$. Alors $\Lambda^*\Lambda^{*\top}=\Lambda TT^\top\Lambda^\top=\Lambda\Lambda^\top$ : **la même matrice $\Sigma$**, donc exactement le même ajustement aux données. Les saturations ne sont donc définies qu'**à une rotation près** ; les communalités $h_i^2=\sum_j\ell_{ij}^2$, elles, ne changent pas (la norme de chaque ligne est conservée par une rotation). Cette liberté n'est pas un défaut mais une chance : parmi toutes les solutions équivalentes, on choisira celle qui est **la plus facile à interpréter** (section 3.2.5).

Un exemple chiffré. Prenons un modèle à deux facteurs pour quatre questions et tournons les axes de $0{,}7$ radian :

| Question | Saturations avant $(F_1\,;\,F_2)$ | Saturations après $(F_1\,;\,F_2)$ | Communalité (avant **et** après) |
|---|---|---|---|
| $q_1$ | $(0{,}80\,;\,0{,}10)$ | $(0{,}68\,;\,-0{,}44)$ | $0{,}65$ |
| $q_2$ | $(0{,}70\,;\,0{,}20)$ | $(0{,}66\,;\,-0{,}30)$ | $0{,}53$ |
| $q_3$ | $(0{,}10\,;\,0{,}90)$ | $(0{,}66\,;\,0{,}62)$ | $0{,}82$ |
| $q_4$ | $(0{,}20\,;\,0{,}70)$ | $(0{,}60\,;\,0{,}41)$ | $0{,}53$ |

Les saturations ont changé de façon spectaculaire, mais la matrice $\Sigma=\Lambda\Lambda^\top+\Psi$ reconstruite est **exactement** la même (un contrôle numérique le confirme à la précision machine) et les communalités n'ont pas bougé.


> ⚠️ **Combien de paramètres, combien de contraintes ?** Le modèle a $pk$ saturations et $p$ unicités, auxquelles il faut retrancher $k(k-1)/2$ pour lever l'indétermination de la rotation. La matrice $\Sigma$ compte $p(p+1)/2$ paramètres libres. Le modèle est donc plus économe que $\Sigma$ libre de
>
> $$\mathrm{ddl}=\frac{(p-k)^2-(p+k)}{2}$$
>
> degrés de liberté. Pour $p=8$ questions : $20$ degrés de liberté avec $k=1$ facteur, $13$ avec $k=2$, $7$ avec $k=3$. C'est ce nombre qui permet de **tester** l'ajustement (section 3.2.4).

### 3.2.3 Estimer les saturations

Deux grandes familles de méthodes.

**1. Les axes principaux itérés** (méthode de la « matrice de corrélation réduite »). Si le modèle est exact, $R-\Psi=\Lambda\Lambda^\top$ est une matrice de rang $k$ : on devrait pouvoir la reconstruire avec ses $k$ premières valeurs propres. L'algorithme alterne :

1. partir d'une estimation des communalités (par exemple $h_i^2=$ le $R^2$ de la régression de la variable $i$ sur toutes les autres) ;
2. remplacer la diagonale de $R$ par ces communalités, extraire les $k$ premières valeurs propres/vecteurs propres : $\Lambda=V_k\sqrt{D_k}$ ;
3. recalculer les communalités $h_i^2=\sum_j\ell_{ij}^2$ ; recommencer jusqu'à stabilisation.

C'est **l'ACP appliquée à une matrice dont la diagonale a été corrigée** pour ne garder que la variance commune. L'algorithme tient en une quinzaine de lignes de NumPy (non reproduites ici) ; sur le questionnaire, avec $k=2$ facteurs, il converge en quelques itérations.


**2. Le maximum de vraisemblance.** On suppose $\mathbf x\sim\mathcal N(0,\Sigma)$ avec $\Sigma=\Lambda\Lambda^\top+\Psi$ et on maximise la vraisemblance (volume I, section 3.2.5) par rapport à $\Lambda$ et $\Psi$. Pas de formule fermée : on utilise un algorithme itératif. Avantage décisif : on dispose d'un **test d'ajustement** (section 3.2.4). Nous utilisons l'implémentation de `scikit-learn` et nous comparons les deux méthodes, question par question :

```text
    axes principaux  maximum de vraisemblance
q1            0.570                     0.564
q2            0.413                     0.414
q3            0.447                     0.448
q4            0.277                     0.279
q5            0.571                     0.572
q6            0.418                     0.413
q7            0.522                     0.526
q8            0.408                     0.405
écart maximal entre les deux corrélations reproduites : 0.005
```

Les deux méthodes donnent des communalités presque identiques (au troisième chiffre près pour la plupart des questions), et reproduisent la matrice de corrélation à moins de 0,01 près. Les communalités sont modestes : entre 0,28 et 0,57. Chaque question est un thermomètre bruité de son facteur, ce qui est typique d'un questionnaire où l'on n'a posé que quatre questions par dimension. La question `q4` est la plus « bruyante » (0,28) : 72 % de sa variance lui est propre.

### 3.2.4 Combien de facteurs ?

Même question qu'en ACP, avec plus de rigueur disponible, puisque l'on a un modèle.

- **Éboulis, Kaiser, analyse parallèle** : les trois outils de la section 3.1.6 s'appliquent aux valeurs propres de $R$. Ils conduisaient à **deux** composantes.
- **Le test du rapport de vraisemblance.** On teste $H_0$ : « $k$ facteurs suffisent » contre « $\Sigma$ est une matrice quelconque ». Avec la correction de Bartlett, la statistique est

$$\chi^2=\Bigl(n-1-\tfrac{2p+5}{6}-\tfrac{2k}{3}\Bigr)\,\Bigl[\ln|\hat\Sigma|-\ln|R|+\operatorname{tr}(\hat\Sigma^{-1}R)-p\Bigr],\qquad \hat\Sigma=\hat\Lambda\hat\Lambda^\top+\hat\Psi,$$

et elle suit approximativement une loi du $\chi^2$ à $\mathrm{ddl}=\frac{(p-k)^2-(p+k)}{2}$ degrés de liberté. Une p-valeur **petite** signale que $k$ facteurs sont **insuffisants**.

- **Les critères d'information.** On compare $\chi^2-\mathrm{ddl}\times\ln n$ (de type BIC) : le modèle qui le minimise offre le meilleur compromis entre ajustement et complexité.

Calculons tout cela pour $k=1,2,3$ :

```text
      chi2  ddl  p-valeur  chi2 - ddl*ln(n)
k                                          
1  947.357   20     0.000           805.357
2   18.443   13     0.141           -73.857
3    8.749    7     0.271           -40.951
```

Lecture du tableau :

- **Avec un seul facteur**, $\chi^2\approx947$ pour 20 degrés de liberté : la p-valeur est nulle à trois décimales. Un seul facteur est **massivement rejeté** : les huit questions ne forment pas une seule dimension.
- **Avec deux facteurs**, $\chi^2\approx18{,}4$ pour 13 degrés de liberté, soit $p\approx0{,}14$ : on **ne rejette pas** le modèle. Rappelons qu'ici, c'est « ne pas rejeter » qui est la bonne nouvelle : le modèle à deux facteurs est compatible avec les données (volume I, section 3.4.1 : ne pas rejeter n'est pas prouver, mais c'est tout ce que l'on peut espérer).
- **Avec trois facteurs**, le modèle est évidemment encore compatible ($p\approx0{,}27$), mais le critère de type BIC remonte (de $-73{,}9$ à $-41{,}0$) : le troisième facteur n'améliore pas assez l'ajustement pour justifier ses paramètres supplémentaires.

Les trois outils (éboulis/analyse parallèle, test d'ajustement, BIC) convergent : **deux facteurs**.

### 3.2.5 La rotation : rendre les facteurs lisibles

Regardons les saturations « brutes » du modèle à deux facteurs :

```text
      F1    F2
q1  0.48  0.58
q2  0.42  0.49
q3  0.47  0.47
q4  0.36  0.38
q5  0.67 -0.35
q6  0.58 -0.27
q7  0.63 -0.37
q8  0.56 -0.30
```

Les saturations brutes se ressemblent beaucoup à celles de l'ACP : un premier axe « général » (toutes les questions du même côté) et un second axe qui **oppose** produits et service. Ce n'est pas un hasard : l'algorithme choisit la solution où le premier facteur capte le maximum de variance commune, ce qui produit un facteur général. Mais, comme nous l'avons montré en 3.2.2, **toute rotation de ces axes explique les données aussi bien**. On peut donc faire tourner les axes jusqu'à ce que chaque question soit proche d'**un seul** facteur : c'est ce qu'on appelle la **structure simple** (Thurstone).

La **rotation varimax** (Kaiser, 1958) cherche la rotation orthogonale qui **maximise la variance des carrés des saturations** dans chaque colonne. Intuition : la variance des carrés est grande quand certaines saturations sont proches de 1 et les autres proches de 0, c'est-à-dire quand les saturations sont « tranchées ». Un algorithme itératif (celui de Kaiser, qui s'écrit en dix lignes grâce à la SVD) trouve cette rotation. Après varimax, les saturations deviennent presque un tableau de $0$ et de $1$ :


```text
    F1 (produits)  F2 (service)
q1           0.75          0.07
q2           0.64          0.07
q3           0.66          0.12
q4           0.52          0.08
q5           0.09          0.75
q6           0.11          0.63
q7           0.05          0.72
q8           0.07          0.63
```

Les bibliothèques font tout cela en une ligne :

```python
from sklearn.decomposition import FactorAnalysis

fa = FactorAnalysis(n_components=2, rotation="varimax").fit(Zq)      # Zq : les notes standardisées
print(fa.components_.T.round(2))
```
<!--sortie-->
```text
[[-0.07 -0.75]
 [-0.07 -0.64]
 [-0.12 -0.66]
 [-0.08 -0.52]
 [-0.75 -0.09]
 [-0.63 -0.11]
 [-0.72 -0.05]
 [-0.63 -0.07]]
```

La bibliothèque donne la même solution que le tableau ci-dessus, à l'ordre et au signe des colonnes près : ici, le facteur « service » vient en premier et les saturations sont de signe opposé. Cet ordre et ce signe sont arbitraires d'une bibliothèque à l'autre, comme pour les axes d'une ACP. Un contrôle numérique confirme que notre propre implémentation de varimax coïncide avec celle-ci à $0{,}01$ près et que les communalités n'ont pas bougé.

![Les huit questions dans le plan des deux facteurs : avant rotation (à gauche) et après rotation varimax (à droite). La rotation fait tourner les axes sans modifier la position relative des points ; après rotation, chaque question est proche d'un seul axe.](figures/ch03-af-rotation.png)

La figure montre ce que fait la rotation : **les points ne bougent pas** (leurs positions relatives sont identiques), ce sont les **axes** qui tournent. À gauche, les deux groupes de questions sont écartés des axes, ce qui rend leur lecture confuse ; à droite, chaque groupe se range le long d'un axe. Après rotation, les saturations se lisent presque comme un tableau de 0 et de 1 : $F_1$ pour un groupe de questions, $F_2$ pour l'autre.

> 💡 **Rotation orthogonale ou oblique ?** Varimax impose des facteurs **non corrélés** (la rotation est orthogonale). Or, dans la réalité, il est courant que « le goût pour les produits » et « l'appréciation du service » soient un peu corrélés : une cliente globalement contente aura tendance à bien noter les deux. Les rotations **obliques** (promax, oblimin) autorisent des facteurs corrélés et produisent souvent une structure plus nette, au prix d'une interprétation un peu plus délicate (deux tableaux : les saturations « de structure » et « de configuration »). Nous reviendrons sur ce point à la section 3.2.7.

### 3.2.6 ACP contre analyse factorielle : que choisir ?

Les deux méthodes donnent souvent des résultats voisins, mais elles ne répondent pas à la même question.

| | **ACP** | **Analyse factorielle** |
|---|---|---|
| Objectif | **Résumer** les variables | **Expliquer** les corrélations par des facteurs |
| Modèle | Aucun : transformation exacte | $\Sigma=\Lambda\Lambda^\top+\Psi$ (testable) |
| Variance expliquée | Totale (diagonale de $R$ à 1) | **Commune** seulement ($\Psi$ absorbe le reste) |
| Les composantes sont… | Des **combinaisons** des variables | Des **causes** supposées des variables |
| Unicité de la solution | Unique (à un signe près) | **À une rotation près** |
| Test d'ajustement | Non | Oui (maximum de vraisemblance) |
| Quand ? | Compresser, visualiser, prétraiter | Construire une **échelle de mesure** (questionnaires), tester une théorie |

Comparons, sur nos données, la façon dont chacune des deux méthodes « voit » la qualité de la représentation de chaque question :

```text
         part de variance (ACP, 2 comp.)  communalité (AF, 2 facteurs)
q1                                  0.66                          0.56
q2                                  0.57                          0.41
q3                                  0.59                          0.45
q4                                  0.45                          0.28
q5                                  0.66                          0.57
q6                                  0.57                          0.41
q7                                  0.64                          0.53
q8                                  0.56                          0.41
moyenne                             0.59                          0.45
```

Sur les huit questions, la part de variance restituée vaut en moyenne $0{,}59$ pour l'ACP à deux composantes et $0{,}45$ pour l'analyse factorielle à deux facteurs : l'ACP attribue toujours aux composantes **plus** de variance que l'analyse factorielle n'en attribue aux facteurs : l'ACP considère que toute la variance d'une question est « à expliquer », alors que l'analyse factorielle admet qu'une partie est du bruit propre à la question (l'unicité). Quand les variables sont très corrélées, l'écart est petit ; quand elles le sont peu, comme ici (les corrélations intra-groupe sont autour de 0,4), il est notable.

### 3.2.7 La révélation : qu'avait-on programmé ?

Les données sont simulées. Voici la vérité : deux facteurs latents (la qualité des produits, la qualité du service) avec une corrélation de **0,30**, et des saturations vraies de $(0{,}80;\ 0{,}70;\ 0{,}75;\ 0{,}60)$ pour `q1` à `q4` sur le premier facteur et $(0{,}80;\ 0{,}70;\ 0{,}75;\ 0{,}65)$ pour `q5` à `q8` sur le second. Chaque note a ensuite été **arrondie et bornée** entre 1 et 5, comme dans un vrai questionnaire. Comparons à ce que la méthode a estimé :

```text
    vraie  estimée (varimax)  saturation croisée
q1   0.80               0.75                0.07
q2   0.70               0.64                0.07
q3   0.75               0.66                0.12
q4   0.60               0.52                0.08
q5   0.80               0.75                0.09
q6   0.70               0.63                0.11
q7   0.75               0.72                0.05
q8   0.65               0.63                0.07
erreur absolue moyenne sur les saturations principales : 0.055
```

> ⚠️ **Pourquoi l'estimation n'est pas exacte.** Trois raisons. (1) L'**échantillon** est fini (1 212 répondantes) : toute estimation fluctue. (2) Les notes ont été **arrondies** à des entiers de 1 à 5, ce qui atténue les corrélations et donc les saturations (l'arrondi est une forme de bruit de mesure). (3) Les facteurs vrais sont **corrélés** (0,30) alors que varimax les impose orthogonaux : il compense en attribuant de petites **saturations croisées** aux questions de l'autre groupe, ce qui explique les valeurs non nulles de la dernière colonne.

### 3.2.8 Construire deux échelles de mesure

Le but pratique d'une analyse factorielle de questionnaire est de **construire des échelles** : un score « produits » et un score « service », moyennes des questions de chaque groupe. Il faut alors vérifier que les questions d'un groupe forment bien un ensemble **cohérent**. L'indicateur classique est l'**alpha de Cronbach** :

$$\alpha=\frac{k}{k-1}\Bigl(1-\frac{\sum_{i=1}^k\operatorname{Var}(x_i)}{\operatorname{Var}\bigl(\sum_{i=1}^kx_i\bigr)}\Bigr).$$

Il vaut 0 si les questions ne sont pas corrélées et tend vers 1 si elles le sont toutes parfaitement ; au-dessus de 0,7 on parle de cohérence acceptable (convention usuelle, sans valeur de loi universelle).


Les deux échelles sont **cohérentes** ($\alpha=0{,}74$ et $0{,}78$, au-dessus du repère de 0,7). Leur corrélation, de $0{,}19$, est plus faible que la corrélation **vraie** de $0{,}30$ entre les facteurs : c'est l'effet classique d'**atténuation par l'erreur de mesure** (chaque score contient du bruit propre aux questions, qui dilue la corrélation entre les facteurs sous-jacents). Remarquez que l'alpha des huit questions réunies reste honorable ($0{,}73$), mais qu'il serait trompeur de conclure à « une seule dimension » : un alpha élevé est compatible avec **plusieurs** dimensions corrélées. C'est l'analyse factorielle, pas l'alpha, qui répond à la question « combien de dimensions ? ».

Reste la question de fond : ces deux scores sont-ils liés au comportement des clientes ? On les joint au fichier des clientes (l'application 3.2 du cahier détaille la démarche) et l'on regarde, parmi les clientes ayant commandé, leurs corrélations avec quelques comportements d'achat :

| | panier moyen | durée de la relation | nombre de commandes | âge |
|---|---:|---:|---:|---:|
| score « produits » | 0,24 | 0,04 | 0,20 | 0,03 |
| score « service » | 0,09 | 0,16 | 0,16 | −0,00 |


Les deux échelles ne sont **pas redondantes**, elles sont associées à des comportements différents. (Parmi les clientes qui ont racheté dans les douze mois, le score moyen « produits » est de $3{,}80$ contre $3{,}46$ pour les autres, et le score « service » de $3{,}68$ contre $3{,}41$.) Le score « produits » est le mieux corrélé au **panier moyen** ($0{,}24$ contre $0{,}09$ pour le score « service »), tandis que le score « service » est le mieux corrélé à la **durée de la relation** ($0{,}16$ contre $0{,}04$). Les deux sont liés au nombre de commandes ($0{,}20$ et $0{,}16$), et les clientes qui rachètent sont plus satisfaites sur les deux plans.

> 🧪 **Révélation.** C'est exactement ce qui avait été programmé : le facteur « produits » influence le panier (et le nombre de commandes), le facteur « service » influence la durée de la relation (et le rachat). Notez que l'analyse factorielle ne **savait rien** de ces liens : elle a simplement séparé deux dimensions, et c'est en les confrontant ensuite à des comportements que leur sens apparaît.

> ⚠️ **Ce que l'on peut dire, et ne pas dire.** Ces corrélations sont **modestes** (entre 0,1 et 0,25) et elles ne prouvent aucune causalité : une cliente satisfaite rachète peut-être pour des raisons qui jouent aussi sur ses réponses. Mais la gérante dispose désormais de deux indicateurs fiables, chacun résumant quatre questions, à suivre dans le temps, et d'une hypothèse de travail claire : le **produit** fait le panier, le **service** fait la fidélité. Pour vérifier la part de chacun une fois les autres facteurs contrôlés, il faudra un modèle de régression (chapitres 1 et 2) ou, pour la durée de la relation, un modèle de survie (chapitre 5).

> ✅ **À retenir**
> - Le modèle factoriel écrit $\Sigma=\Lambda\Lambda^\top+\Psi$ : les covariances viennent de **facteurs communs**, le reste est de l'**unicité**. La **communalité** d'une variable est la part de sa variance expliquée par les facteurs.
> - Les saturations ne sont définies qu'**à une rotation orthogonale près** : on choisit la rotation la plus lisible (**varimax** = structure simple ; **obliques** si les facteurs sont corrélés).
> - On estime par **axes principaux** ou **maximum de vraisemblance** ; ce dernier fournit un **test d'ajustement** et permet de comparer des modèles à $k$ différents.
> - **ACP** = résumer ; **analyse factorielle** = modéliser des causes cachées. Elles diffèrent par la variance expliquée (totale contre commune) et par le statut des axes.
> - Pour un questionnaire : construire des **échelles**, mesurer leur cohérence (**alpha de Cronbach**), et ne pas confondre alpha élevé et unidimensionnalité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2, exercices 3.6 à 3.8.


## 3.3 Classification non supervisée

> 💡 **Intuition.** La gérante a devant elle un millier de clientes et voudrait savoir « qui ressemble à qui ». On ne lui a donné aucune étiquette (« cliente fidèle », « cliente de passage ») : on veut que ce soient **les données elles-mêmes** qui proposent des groupes. C'est la **classification non supervisée** (*clustering*) : regrouper les individus de façon que ceux d'un même groupe se ressemblent plus entre eux qu'avec ceux des autres groupes. Deux familles de méthodes, simples et complémentaires : les **k-means** (on fixe le nombre de groupes et on optimise) et la **classification hiérarchique** (on construit un arbre de fusions successives).

> ⚠️ **Avertissement de départ.** Un algorithme de classification **rend toujours des groupes**, même quand il n'y en a aucun. Donnez-lui un nuage uniforme, il le découpera en morceaux avec le même aplomb. Tout ce que nous apprendrons dans cette section — choisir le nombre de groupes, mesurer leur qualité, tester leur stabilité — sert à répondre à la vraie question : *ces groupes existent-ils, ou est-ce moi qui les ai tracés ?*

### 3.3.1 Ressembler, c'est être proche : la notion de distance

Un groupe, c'est un ensemble de points **proches**. Il faut donc définir « proche ». La distance la plus courante est la distance **euclidienne** : pour deux clientes décrites par $p$ variables $\mathbf x$ et $\mathbf y$,

$$d(\mathbf x,\mathbf y)=\sqrt{\sum_{j=1}^p(x_j-y_j)^2}.$$

Comme en ACP (section 3.1.5), **les unités comptent** : si le panier est en € et le nombre de commandes en unités, la distance sera dominée par le panier. On **standardise** donc presque toujours les variables avant de classer. Autre limite : la distance euclidienne n'a de sens que pour des variables **numériques**. Pour des variables mixtes (numériques et qualitatives), on utilise des distances adaptées (par exemple celle de Gower) ; pour des variables qualitatives pures, on peut passer par l'analyse des correspondances multiples (section 3.4).

### 3.3.2 Les k-means

**L'objectif.** On cherche à découper $n$ points en $k$ groupes $C_1,\dots,C_k$ de centres (moyennes) $\boldsymbol\mu_1,\dots,\boldsymbol\mu_k$ de façon à minimiser la **variance intra-groupe** (aussi appelée inertie intra-classe) :

$$W(C,\boldsymbol\mu)=\sum_{j=1}^k\sum_{i\in C_j}\|\mathbf x_i-\boldsymbol\mu_j\|^2.$$

Trouver la partition qui minimise $W$ est un problème difficile (il y a un nombre astronomique de partitions possibles) ; on le résout **approximativement** par l'algorithme de **Lloyd**, qui alterne deux étapes simples :

1. **Affectation** : chaque point rejoint le groupe dont le centre est le plus proche.
2. **Mise à jour** : chaque centre est remplacé par la **moyenne** des points de son groupe.

On répète jusqu'à ce que plus aucun point ne change de groupe.

**Un exemple à la main.** Six clientes décrites par une seule variable (leur panier moyen, en dizaines de €) : $1,\ 2,\ 4,\ 9,\ 11,\ 12$. On veut $k=2$ groupes et on choisit, au hasard, les centres initiaux $\mu_1=1$ et $\mu_2=4$.

- *Affectation 1.* Les points $1$ et $2$ sont plus proches de $\mu_1=1$ ; le point $4$ est son propre centre ; $9$, $11$ et $12$ sont plus proches de $4$ que de $1$. Groupes : $\{1,2\}$ et $\{4,9,11,12\}$.
- *Mise à jour 1.* Les nouvelles moyennes sont $\mu_1=1{,}5$ et $\mu_2=(4+9+11+12)/4=9$.
- *Affectation 2.* Le point $4$ est maintenant à $2{,}5$ de $\mu_1$ et à $5$ de $\mu_2$ : **il change de groupe**. Groupes : $\{1,2,4\}$ et $\{9,11,12\}$.
- *Mise à jour 2.* Moyennes : $\mu_1=7/3\approx2{,}33$ et $\mu_2=32/3\approx10{,}67$.
- *Affectation 3.* Plus personne ne change : l'algorithme s'arrête.

Suivons la variance intra-groupe $W$ : avec les centres de départ $(1;\ 4)$ et les groupes $\{1,2\},\{4,9,11,12\}$, $W=(0+1)+(0+25+49+64)=139$ ; après la première mise à jour (centres $1{,}5$ et $9$), $W=0{,}5+38=38{,}5$ ; après la deuxième affectation, $W=19{,}75$ ; après la deuxième mise à jour, $W=28/3\approx9{,}33$. **$W$ n'a fait que diminuer** : $139\to38{,}5\to19{,}75\to9{,}33$.

Un petit programme qui suit $W$ à chaque étape retrouve exactement ces nombres ($139\to38{,}5\to19{,}75\to9{,}33$) et s'arrête au troisième tour, quand les centres ne bougent plus.


> 📐 **Pourquoi l'algorithme converge : $W$ ne peut que diminuer.**
>
> - **L'étape d'affectation ne peut pas augmenter $W$** : à centres fixés, chaque point contribue par son carré de distance à son centre ; en le plaçant dans le groupe du centre le plus proche, on minimise sa contribution.
> - **L'étape de mise à jour ne peut pas augmenter $W$** : à groupes fixés, la moyenne est le point qui minimise la somme des carrés des distances aux points du groupe. En effet, pour tout point $\mathbf m$,
> $$\sum_{i\in C}\|\mathbf x_i-\mathbf m\|^2=\sum_{i\in C}\|\mathbf x_i-\bar{\mathbf x}_C\|^2+|C|\,\|\bar{\mathbf x}_C-\mathbf m\|^2,$$
> (on développe en insérant $\bar{\mathbf x}_C$ ; le terme croisé s'annule parce que $\sum_i(\mathbf x_i-\bar{\mathbf x}_C)=0$), donc le minimum est atteint en $\mathbf m=\bar{\mathbf x}_C$.
>
> $W$ est donc une suite **décroissante et minorée par 0**. Comme il n'y a qu'un nombre **fini** de partitions possibles et que $W$ décroît strictement tant que la partition change, l'algorithme s'arrête après un nombre fini d'étapes. $\square$
>
> **Mais attention** : il s'arrête sur un **minimum local**, pas forcément global. Le résultat dépend des centres de départ.

**Les centres de départ : k-means++ et redémarrages.** Deux précautions pour éviter les mauvais minima locaux. D'abord, **plusieurs départs aléatoires** (on garde la solution de plus petit $W$). Ensuite, l'initialisation **k-means++** : le premier centre est tiré au hasard parmi les points, puis chaque centre suivant est tiré avec une probabilité proportionnelle au **carré de la distance** au centre le plus proche déjà choisi. Les centres de départ sont ainsi bien étalés. L'algorithme complet (Lloyd, k-means++ et dix redémarrages) tient en une vingtaine de lignes de NumPy ; nous l'écrivons pas à pas dans l'application 3.3 du cahier.


**Un jeu de données avec de vrais groupes.** Pour voir l'algorithme réussir, il faut des données qui **contiennent** des groupes. Simulons (graine fixée) 600 clientes issues de trois profils distincts, décrites par leur nombre de commandes annuel et leur panier moyen :

- les **occasionnelles** (300) : peu de commandes, petit panier ;
- les **fidèles** (200) : beaucoup de commandes, panier moyen ;
- les **cadeaux** (100) : peu de commandes mais très gros panier (offrir un cadeau de valeur).


Voici l'appel de `scikit-learn` sur ces données (`Zs` désigne les variables standardisées) :

```python
from sklearn.cluster import KMeans

km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Zs)
print(round(km.inertia_, 1), np.bincount(km.labels_).tolist())
```
<!--sortie-->
```text
188.1 [191, 310, 99]
```

Notre propre implémentation (celle du cahier) trouve **exactement** la même inertie (188,1). Les effectifs trouvés ($191$, $310$ et $99$ ; l'ordre des étiquettes est arbitraire) sont proches des vrais ($200$, $300$ et $100$) et l'accord avec les profils programmés est excellent ($\mathrm{ARI}\approx0{,}94$). Il n'est pas parfait, et ne le sera jamais : les nuages des « occasionnelles » et des « fidèles » se chevauchent un peu, et les clientes situées à la frontière sont inévitablement rangées au hasard de leur position.

> 💡 **L'indice de Rand ajusté (ARI).** Pour comparer deux partitions sans avoir à numéroter les groupes de la même façon, on compte les **paires de points** : une paire est « d'accord » si les deux partitions la placent ensemble toutes les deux, ou séparée toutes les deux. L'indice de Rand est la proportion de paires d'accord ; la version **ajustée** retire l'accord attendu du hasard, de sorte que $\mathrm{ARI}=1$ signifie des partitions identiques et $\mathrm{ARI}\approx0$ un accord de hasard. Nous nous en servirons pour mesurer à la fois l'exactitude (contre la vérité, quand on l'a) et la **stabilité** (entre deux exécutions).

![L'algorithme de Lloyd sur les 600 clientes simulées (variables standardisées) : initialisation k-means++, premières mises à jour puis solution finale. Les losanges sont les centres ; la couleur d'un point est celle du centre le plus proche.](figures/ch03-kmeans-iterations.png)

### 3.3.3 Combien de groupes ?

Il faut choisir $k$ **avant** de lancer l'algorithme, et la variance intra-groupe $W$ **ne peut pas servir de critère** : elle décroît toujours quand $k$ augmente (avec $k=n$, chaque point est son propre groupe et $W=0$). Deux outils.

**1. Le coude.** On trace $W(k)$ pour $k=1,2,3,\dots$ et on cherche le point où la décroissance ralentit nettement : ajouter un groupe supplémentaire n'apporte plus grand-chose.

**2. La silhouette.** Pour chaque point $i$, on calcule :

- $a(i)$ : la distance moyenne de $i$ aux **autres points de son propre groupe** (est-il bien « chez lui » ?) ;
- $b(i)$ : la distance moyenne de $i$ aux points du **groupe voisin le plus proche** (le meilleur « plan B »).

La silhouette du point $i$ est

$$s(i)=\frac{b(i)-a(i)}{\max\bigl(a(i),\,b(i)\bigr)}\in[-1,1].$$

Proche de $1$ : le point est bien à l'intérieur de son groupe. Proche de $0$ : il est à la frontière. Négatif : il est probablement mal classé. La **silhouette moyenne** sur tous les points mesure la qualité globale de la partition ; on choisit le $k$ qui la maximise.

*À la main, sur nos six clientes* ($\{1,2,4\}$ et $\{9,11,12\}$) : pour le point $4$, $a=(|4-1|+|4-2|)/2=2{,}5$ et $b=(|4-9|+|4-11|+|4-12|)/3=20/3\approx6{,}67$, donc $s(4)=(6{,}67-2{,}5)/6{,}67=0{,}625$. Pour l'ensemble des six points, les silhouettes valent $0{,}793$ ; $0{,}827$ ; $0{,}625$ ; $0{,}625$ ; $0{,}827$ ; $0{,}793$, d'où une silhouette moyenne de $0{,}748$ (la fonction de la bibliothèque donne le même nombre).


Appliquons les deux outils aux **trois groupes simulés** : le bon nombre est connu, c'est 3. Sachons-nous le retrouver ?

```text
          W  silhouette moyenne
k                              
1  1200.000                 NaN
2   607.380               0.533
3   188.103               0.676
4   140.201               0.582
5   123.191               0.402
6   108.734               0.387
7    97.185               0.396
```

Deux lectures concordantes. La **variance intra-groupe** s'effondre de $1\,200$ à $607$ puis à $188$ quand on passe de $1$ à $2$ puis à $3$ groupes (pour $k=1$, $W=n\times p=600\times2=1\,200$ puisque les variables sont standardisées), puis ne décroît plus que lentement : le **coude** est net en $k=3$. La **silhouette moyenne** atteint son maximum en $k=3$ ($0{,}676$) et chute ensuite. Les deux outils retrouvent le bon nombre de groupes. Pour interpréter une silhouette moyenne, on utilise des repères conventionnels (Kaufman et Rousseeuw) : au-dessus de $0{,}5$, la structure est réelle ; entre $0{,}25$ et $0{,}5$, elle est faible ; en dessous de $0{,}25$, on ne peut pas dire qu'il y ait une structure. Ces repères restent **indicatifs** : des variables très asymétriques produisent des silhouettes élevées même sans aucun groupe, et l'on ne peut interpréter une silhouette qu'en la comparant à celle d'un nuage témoin sans structure (voir l'exercice 3.12 du cahier).

![Choix du nombre de groupes : variance intra-groupe (le coude) et silhouette moyenne, pour les clientes simulées avec trois vrais profils et pour les clientes réelles de la boutique.](figures/ch03-choix-k.png)

### 3.3.4 La classification hiérarchique

Ici, on ne fixe pas $k$ à l'avance : on construit **un arbre** de regroupements. L'algorithme **ascendant** (agglomératif) est d'une simplicité désarmante :

1. au départ, chaque point est un groupe à lui seul ;
2. on **fusionne** les deux groupes les plus proches ;
3. on recommence jusqu'à n'avoir plus qu'un seul groupe.

Il reste à définir la **distance entre deux groupes** : c'est le **critère d'agrégation** (*linkage*).

| Critère | Distance entre deux groupes $A$ et $B$ | Effet typique |
|---|---|---|
| **Simple** (*single*) | $\min_{a\in A,b\in B}d(a,b)$ : les deux points les plus proches | groupes **allongés** (effet de chaîne), sensible aux points isolés |
| **Complet** (*complete*) | $\max_{a\in A,b\in B}d(a,b)$ : les deux points les plus éloignés | groupes **compacts** de diamètre comparable |
| **Moyen** (*average*) | moyenne des $d(a,b)$ | compromis |
| **Ward** | augmentation de $W$ due à la fusion : $\dfrac{|A||B|}{|A|+|B|}\|\bar a-\bar b\|^2$ | groupes **sphériques** de taille homogène, comparable aux k-means |

**À la main, sur cinq clientes** décrites par une variable : $A=0,\ B=1,\ C=4,\ D=6,\ E=11$.

- *Fusion 1* : la paire la plus proche est $\{A,B\}$ (distance $1$).
- *Fusion 2* : la plus proche ensuite est $\{C,D\}$ (distance $2$).
- *Fusion 3* : on fusionne $\{A,B\}$ et $\{C,D\}$. La distance entre eux vaut, selon le critère : **simple** $\min=d(B,C)=3$ ; **complet** $\max=d(A,D)=6$.
- *Fusion 4* : on rattache $E$. Distance **simple** $=d(D,E)=5$ ; **complète** $=d(A,E)=11$.


Les hauteurs de fusion confirment le calcul à la main : $1,\,2,\,3,\,5$ pour le critère simple et $1,\,2,\,6,\,11$ pour le critère complet. Le **dendrogramme** dessine cet arbre, la hauteur de chaque fusion étant la distance à laquelle elle s'est produite. **Couper l'arbre** à une hauteur donnée fournit une partition : plus on coupe bas, plus il y a de groupes.

> 💡 **Lire un dendrogramme.** Une longue branche verticale avant une fusion signale que deux groupes **bien séparés** ont été réunis de force : c'est là qu'il faut couper. Si toutes les fusions se font à des hauteurs graduellement croissantes (pas de saut), c'est que les données ne contiennent pas de groupes nets.

Appliquons-le aux 600 clientes simulées (critère de Ward, variables standardisées), et comparons la partition à trois groupes ainsi obtenue à celle des k-means. (Pour le dessin, nous ne représenterons que 40 clientes : un dendrogramme de 600 feuilles serait illisible.)


Les **deux dernières fusions** ont lieu à des hauteurs de $29{,}1$ et $34{,}3$, contre $9{,}3$ et $6{,}1$ pour les deux précédentes : l'arbre fait un **grand saut** avant de passer de trois groupes à deux, puis à un. C'est le signe qu'il y a trois groupes. La coupe à trois groupes redonne les trois profils (ARI de $0{,}96$ contre les vrais profils) et coïncide presque avec les k-means ($0{,}97$) : sur des groupes aussi bien séparés, les deux méthodes s'accordent. La corrélation cophénétique de $0{,}82$ indique que l'arbre est une bonne représentation des distances.

> 📐 **La corrélation cophénétique.** La *distance cophénétique* de deux points est la hauteur à laquelle ils sont fusionnés dans l'arbre. La corrélation entre ces distances et les vraies distances mesure **dans quelle mesure l'arbre est fidèle** aux données : proche de 1, l'arbre résume bien les distances ; faible, il les déforme.

![Dendrogramme de 40 clientes simulées (critère de Ward). La ligne en pointillés coupe l'arbre en trois groupes, colorés ; on remarque les deux fusions finales, très hautes, par rapport aux précédentes.](figures/ch03-dendrogramme.png)

**k-means ou hiérarchique ?** Les k-means passent très bien à l'échelle (des millions de points), mais exigent $k$ à l'avance et ne trouvent que des groupes « arrondis ». La classification hiérarchique donne une vue **à toutes les échelles** et ne dépend pas d'une initialisation, mais elle exige de stocker les $n^2/2$ distances (elle ne dépasse guère quelques dizaines de milliers de points) et ses fusions sont définitives : une erreur précoce ne se corrige jamais.

### 3.3.5 Une segmentation honnête des clientes de la boutique

Passons aux **vraies** clientes (celles du fichier `clients.csv`, qui sont simulées mais **sans** segments programmés, comme dans la plupart des situations réelles). Nous décrivons chaque cliente par quatre variables : nombre de commandes par an, panier moyen, durée de la relation et âge. On écarte la dépense annuelle (elle est quasiment le produit de deux autres variables), et les clientes sans commande (panier nul).

```text
clientes retenues : 1740 sur 2000
          W  silhouette moyenne
k                              
1  6956.000                 NaN
2  5526.143               0.224
3  4607.880               0.228
4  3812.099               0.242
5  3243.262               0.246
6  3029.588               0.232
7  2826.824               0.223
8  2658.348               0.201
```

Sur les clientes réelles, la variance intra-groupe décroît **régulièrement** de $6\,956$ à $2\,658$, sans coude (la courbe orange de la figure est presque une droite), et la silhouette moyenne **ne dépasse jamais $0{,}25$** (maximum $0{,}246$ pour $k=5$, valeurs voisines pour tous les autres $k$). D'après les repères ci-dessus, on ne peut pas dire qu'il existe une structure en groupes.

Comparez avec le tableau des clientes simulées (3.3.3) : sur des données qui contiennent de vrais groupes, la silhouette atteint un maximum **franc** ($0{,}68$) au bon $k$ ; ici, rien de tel. Les données ne se laissent pas découper naturellement.

Ce constat n'interdit pas de **segmenter** : pour un usage commercial, on a le droit de découper un continuum en tranches commodes, comme on découpe un âge en tranches de dix ans, pourvu que l'on **ne prétende pas** avoir découvert des types naturels de clientes. Prenons $k=4$ et décrivons les groupes :

```text
         effectif  commandes  panier  duree   age  part
segment                                                
3             695        3.2    46.8   16.8  28.8  40.0
1             282        4.0    63.0   52.9  36.6  16.0
2             237       11.2    67.9   20.8  34.3  14.0
0             526        3.4    76.4   17.5  45.4  30.0
```

Quatre profils lisibles se dégagent, pour peu qu'on les nomme avec prudence :

- **Segment 3** (40 % des clientes) : les plus **jeunes** (29 ans en moyenne) au **plus petit panier** (47 €) ;
- **Segment 0** (30 %) : les plus **âgées** (45 ans) au **plus gros panier** (76 €) ;
- **Segment 2** (14 %) : les **habituées**, avec 11 commandes par an en moyenne, contre 3 à 4 pour les autres ;
- **Segment 1** (16 %) : les **anciennes**, dont la relation dure en moyenne 53 mois, contre 17 à 21 pour les autres.

Ces portraits sont **utiles** (on n'enverra pas le même message à une étudiante et à une cliente de longue date), mais ils décrivent des *tendances*, pas des types : chaque segment contient des clientes très variées.

Il reste à tester si ces segments sont **stables** : si l'on tire d'autres clientes dans la même population, retrouve-t-on les mêmes groupes ? On ré-estime les k-means sur 30 échantillons bootstrap (volume I, section 3.3.5), on range **toutes** les clientes d'origine dans le groupe du centre le plus proche, et on compare à la partition de référence avec l'ARI.


Les clientes simulées avec de vrais groupes donnent une stabilité **quasi parfaite** (ARI moyen $0{,}994$, minimum $0{,}985$ : on retrouve la même partition quel que soit l'échantillon). Sur les clientes réelles, la stabilité est **honorable en moyenne** ($0{,}86$) mais le **pire cas** est mauvais ($0{,}51$) : sur certains échantillons, le découpage est très différent de la référence.

> ⚠️ **Stabilité n'est pas existence.** Une partition peut être reproductible sans correspondre à des groupes réels : avec 1 740 clientes, les k-means retrouvent à peu près les mêmes quatre « tranches » à chaque tirage, comme un découpeur de gâteau qui poserait toujours son couteau aux mêmes endroits. La stabilité est une condition **nécessaire** (une partition instable est sûrement arbitraire), jamais **suffisante**. C'est pourquoi on la combine avec la silhouette et le coude.

![Les clientes de la boutique (variables standardisées) projetées sur les deux premières composantes principales, colorées par segment k-means (k = 4). Les segments se touchent : ils découpent un nuage continu.](figures/ch03-segments-clients.png)

> 🧪 **Révélation.** Aucun segment n'avait été programmé dans ces données : les variables ont été générées indépendamment de toute notion de « type de cliente ». Les k-means ont pourtant rendu quatre groupes, tout aussi sérieux en apparence que les trois profils simulés. Seuls les **indicateurs** (silhouette inférieure à $0{,}25$, absence de coude, stabilité inégale dans le pire cas) pouvaient nous avertir qu'ils n'étaient pas réels. Voilà pourquoi on ne livre jamais une segmentation sans ces diagnostics.

### 3.3.6 Les pièges de la classification

> ⚠️ **1. Les k-means supposent des groupes « arrondis ».** Comme ils minimisent des distances à des centres, ils découpent l'espace en polyèdres et échouent sur des formes allongées, incurvées ou de tailles très inégales. La classification hiérarchique à lien simple, au contraire, suit les chaînes de points voisins. Exemple classique, ci-dessous : deux « croissants » de lune. Les k-means les coupent en travers (indice de Rand ajusté de $0{,}23$ avec la vraie partition), alors que la classification hiérarchique à lien simple les retrouve parfaitement (indice de $1{,}0$).


![Deux croissants de lune. À gauche, les k-means coupent chaque croissant en deux ; à droite, la classification hiérarchique à lien simple suit la forme des croissants.](figures/ch03-lunes.png)

> **2. L'échelle des variables** décide du résultat : sans standardisation, la variable de plus grande variance fait la loi (section 3.1.5).
>
> **3. Les valeurs extrêmes** attirent un centre (la moyenne est sensible aux extrêmes) ou forment des groupes à un seul point.
>
> **4. La dimension.** Quand le nombre de variables est grand, toutes les distances tendent à se ressembler (le « fléau de la dimension ») et la notion de « proche » perd son sens. On réduit d'abord la dimension (ACP, section 3.1), puis on classe les scores.
>
> **5. Le choix de $k$ n'est jamais « objectif »** : le coude est une impression, la silhouette un compromis. Documentez le choix, testez plusieurs valeurs, vérifiez la stabilité et **l'utilité** du découpage pour la décision à prendre.
>
> **6. Pas de vérité à laquelle comparer.** Contrairement à une régression, il n'y a pas de variable à prédire : la qualité d'une classification ne se mesure que par des indicateurs internes (silhouette, stabilité) ou par sa **valeur d'usage**.

> ✅ **À retenir**
> - Classer, c'est regrouper des points **proches** ; **standardisez** d'abord.
> - **K-means** : on minimise $W=\sum_j\sum_{i\in C_j}\|\mathbf x_i-\boldsymbol\mu_j\|^2$ par l'algorithme de Lloyd (affectation / mise à jour) ; $W$ décroît à chaque étape, mais on n'atteint qu'un **minimum local** : initialisation **k-means++** et plusieurs départs.
> - **$k$** : jamais choisi avec $W$ seule ; on regarde le **coude**, la **silhouette** $s(i)=\frac{b-a}{\max(a,b)}$, et surtout la **stabilité** (bootstrap + ARI).
> - **Hiérarchique** : on fusionne pas à pas ; le **critère d'agrégation** (simple, complet, moyen, Ward) détermine la forme des groupes ; le **dendrogramme** montre toutes les échelles.
> - Un algorithme de classification **rend toujours des groupes** : sans indicateurs de qualité et de stabilité, on ne peut pas savoir s'ils existent.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3, exercices 3.9 à 3.12.


## 3.4 ➕ Pour aller plus loin : l'analyse des correspondances (AC et ACM)

> 🧭 **Section optionnelle.** Elle étend l'idée de l'ACP aux **variables qualitatives** (canal, ville, tranche d'âge), pour lesquelles moyenne et variance n'ont pas de sens. On peut sauter cette section sans perdre le fil du chapitre. Elle s'appuie sur le test du khi-deux du volume I (section 3.4.6) et sur la décomposition en valeurs singulières (volume I, section 1.1.4).

> 💡 **Intuition.** L'ACP regarde un nuage de points dans un espace de nombres. Mais comment « dessiner » un tableau croisant le canal d'acquisition (trois modalités) et la taille du panier (quatre tranches) ? L'**analyse factorielle des correspondances** (AFC, ou simplement AC) transforme un tableau de contingence en **deux nuages de points** (un pour les lignes, un pour les colonnes), placés sur une même carte, de façon que **deux modalités proches sur la carte soient fréquemment associées** dans les données. Quant à l'**analyse des correspondances multiples** (ACM), c'est l'AC appliquée à plusieurs variables qualitatives à la fois.

### 3.4.1 Le point de départ : un tableau de contingence

Prenons les clientes ayant déjà commandé (1 740 sur 2 000) et croisons leur **canal d'acquisition** avec la **tranche de leur panier moyen**, définie par les quartiles : « très petit » pour le quart le plus bas, jusqu'à « très grand » pour le quart le plus haut.

```text
tranche_panier     T1 très petit  T2 petit  T3 grand  T4 très grand
canal_acquisition                                                  
Boutique                      46        93       126            184
Réseaux                      258       184       158             87
Site                         132       157       152            163

profils-lignes (en %) : répartition des paniers dans chaque canal
tranche_panier     T1 très petit  T2 petit  T3 grand  T4 très grand
canal_acquisition                                                  
Boutique                    10.2      20.7      28.1           41.0
Réseaux                     37.6      26.8      23.0           12.7
Site                        21.9      26.0      25.2           27.0
```

Les **profils-lignes** (la répartition des tranches de panier dans chaque canal) sont très différents d'un canal à l'autre : la boutique compte 69 % de paniers « grands » ou « très grands » (T3 et T4) contre 36 % pour Réseaux, dont 64 % des paniers sont « petits » ou « très petits » (T1 et T2). Si le canal et le panier étaient **indépendants**, les trois lignes auraient le même profil, égal au profil des totaux. L'analyse des correspondances décrit **comment et dans quelle direction** les profils s'écartent de cette indépendance.

Mesurons d'abord l'écart global avec le test du khi-deux (volume I, section 3.4.6) : on trouve $\chi^2=180{,}7$ pour $6$ degrés de liberté, soit une p-valeur de l'ordre de $10^{-36}$ : l'indépendance est massivement rejetée. Rapporté à l'effectif ($n=1\,740$), cela donne $\chi^2/n=0{,}1038$.


La quantité $\chi^2/n$ est appelée **inertie totale** du tableau. Elle ne dépend pas de la taille de l'échantillon et mesure l'intensité de l'association : $0$ en cas d'indépendance parfaite. C'est ce nombre que l'analyse des correspondances va **décomposer sur des axes**, exactement comme l'ACP décompose la variance totale.

### 3.4.2 La méthode : une SVD sur les résidus standardisés

Notons $P=N/n$ la matrice des fréquences, $\mathbf r$ le vecteur des fréquences de lignes (marges de $P$) et $\mathbf c$ celui des colonnes. Sous indépendance, la fréquence attendue de la case $(i,j)$ est $r_ic_j$. La matrice des **résidus standardisés** est

$$S_{ij}=\frac{p_{ij}-r_ic_j}{\sqrt{r_ic_j}}.$$

> 📐 **L'inertie totale est $\|S\|^2=\chi^2/n$.** Il suffit de développer : $\sum_{i,j}S_{ij}^2=\sum_{i,j}\frac{(p_{ij}-r_ic_j)^2}{r_ic_j}=\frac1n\sum_{i,j}\frac{(n_{ij}-E_{ij})^2}{E_{ij}}=\frac{\chi^2}{n}$, car $n\,p_{ij}=n_{ij}$ et $n\,r_ic_j=E_{ij}$ (effectifs attendus).

L'analyse des correspondances **est** la SVD de cette matrice : $S=U\Sigma V^\top$, avec $\Sigma=\operatorname{diag}(\sigma_1\geq\sigma_2\geq\dots)$. Comme la norme de Frobenius au carré est la somme des carrés des valeurs singulières, l'inertie totale se **répartit sur les axes** :

$$\frac{\chi^2}{n}=\sum_k\sigma_k^2,\qquad\text{l'axe }k\text{ porte la part }\frac{\sigma_k^2}{\sum_l\sigma_l^2}.$$

Les **coordonnées principales** des lignes et des colonnes sur l'axe $k$ sont, en notant $D_{\mathbf r}=\operatorname{diag}(\mathbf r)$ et $D_{\mathbf c}=\operatorname{diag}(\mathbf c)$ :

$$F=D_{\mathbf r}^{-1/2}\,U\,\Sigma\quad(\text{lignes}),\qquad G=D_{\mathbf c}^{-1/2}\,V\,\Sigma\quad(\text{colonnes}).$$

On dessine $F$ et $G$ sur la même carte. Ce choix a une conséquence élégante, la **relation barycentrique** : la coordonnée d'une ligne est, au facteur $1/\sigma_k$ près, la **moyenne pondérée** des coordonnées des colonnes, les poids étant son profil. Une modalité-ligne est donc attirée vers les modalités-colonnes avec lesquelles elle est fortement associée.

**Un exemple à la main : un tableau $2\times2$.** Deux canaux, deux tranches de panier, 80 clientes :

| | Petit panier | Grand panier |
|---|---|---|
| **Réseaux** | 30 | 10 |
| **Boutique** | 10 | 30 |

Les marges valent $\mathbf r=(0{,}5;0{,}5)$ et $\mathbf c=(0{,}5;0{,}5)$ ; $P=\begin{pmatrix}0{,}375&0{,}125\\0{,}125&0{,}375\end{pmatrix}$ ; $r_ic_j=0{,}25$ partout. Donc

$$S=\frac{P-0{,}25}{\sqrt{0{,}25}}=\frac{1}{0{,}5}\begin{pmatrix}0{,}125&-0{,}125\\-0{,}125&0{,}125\end{pmatrix}=\begin{pmatrix}0{,}25&-0{,}25\\-0{,}25&0{,}25\end{pmatrix}.$$

Cette matrice est de rang 1 : $S=0{,}5\times\begin{pmatrix}1/\sqrt2\\-1/\sqrt2\end{pmatrix}\begin{pmatrix}1/\sqrt2&-1/\sqrt2\end{pmatrix}$, donc $\sigma_1=0{,}5$ et $\sigma_1^2=0{,}25$. Vérification avec le khi-deux : les effectifs attendus valent $20$ partout, d'où $\chi^2=4\times\frac{(\pm10)^2}{20}=20$ et $\chi^2/n=20/80=0{,}25$. ✓ Les coordonnées des lignes sont $\pm\frac{1}{\sqrt{0{,}5}}\cdot\frac{1}{\sqrt2}\cdot0{,}5=\pm0{,}5$ : Réseaux à $-0{,}5$ d'un côté, Boutique à $+0{,}5$ de l'autre. Un tableau $2\times2$ n'a qu'**un seul axe**, sur lequel les deux modalités s'opposent. Plus généralement, un tableau $I\times J$ a au plus $\min(I,J)-1$ axes non triviaux.

Une implémentation de ces formules (une quinzaine de lignes de NumPy, qui sont l'objet de l'application 3.4 du cahier) donne, sur l'exemple $2\times2$, une inertie de $0{,}25$ sur le seul axe et des coordonnées de $\pm0{,}5$, comme à la main. Sur notre tableau canal $\times$ panier, les inerties des trois axes valent $0{,}1031$, $0{,}0007$ et presque $0$ ; leur somme, $0{,}1038$, est bien égale à $\chi^2/n$, et le premier axe en porte $99{,}3\ \%$.


### 3.4.3 Lire la carte

Les coordonnées des trois canaux (lignes) puis des quatre tranches de panier (colonnes) sur les deux premiers axes sont :

```text
               axe 1  axe 2
Boutique       0.448 -0.026
Réseaux       -0.354 -0.015
Site           0.070  0.036
T1 très petit -0.440 -0.024
T2 petit      -0.090  0.046
T3 grand       0.079 -0.010
T4 très grand  0.452 -0.012
```

![Analyse des correspondances du tableau canal x tranche de panier (à gauche) et, en comparaison, du tableau canal x ville (à droite). Attention aux échelles : à gauche les points sont répartis sur près de ±0,45, à droite sur ±0,1 seulement.](figures/ch03-ca-carte.png)

Sur la carte de gauche, **tout se passe sur le premier axe** (il porte presque toute l'inertie). Les trois canaux s'y rangent dans l'ordre Réseaux, Site, Boutique ; et les quatre tranches de panier dans l'ordre T1, T2, T3, T4, **du même côté que** les canaux auxquels elles sont associées : les très grands paniers (T4) sont du côté de la boutique, les très petits (T1) du côté du canal Réseaux. L'axe 1 est donc un axe **« petits paniers / gros paniers »** commun aux deux variables. Le fait que les tranches de panier s'ordonnent exactement comme leur numérotation est typique : pour une variable ordinale, l'AC retrouve l'ordre sans qu'on le lui ait dit.

> 🧪 **Révélation.** C'est ce qui avait été programmé : le canal d'acquisition agit sur le panier (en échelle logarithmique : $+0{,}22$ pour la boutique, $+0{,}05$ pour le site, $-0{,}12$ pour Réseaux). L'AC a retrouvé cette association sans qu'on lui désigne de variable « à expliquer », et a même restitué l'ordre des canaux.

> ⚠️ **Piège numéro un : une carte a toujours l'air de dire quelque chose.** Faites maintenant l'expérience inverse, avec deux variables qui n'ont **aucun lien** dans la simulation : le canal d'acquisition et la ville.


Le test du khi-deux ne rejette pas l'indépendance, et l'inertie totale est de l'ordre de grandeur de ce que le **hasard seul** produit (en moyenne $\text{ddl}/n$ sous l'indépendance). Pourtant, l'axe 1 « explique » $74\ \%$ de l'inertie et l'axe 2 les $26\ \%$ restants : un tableau $3\times6$ n'a que deux axes non triviaux, qui se partagent donc **toujours** 100 % de l'inertie, quel que soit le tableau. La carte de droite de la figure montre des points bien répartis, mais sur une échelle minuscule (de l'ordre de $\pm0{,}1$, contre $\pm0{,}45$ à gauche). **Un pourcentage d'inertie ne prouve jamais rien** : il faut d'abord regarder le khi-deux et l'**inertie totale**, qui mesure l'intensité de l'association.

### 3.4.4 L'analyse des correspondances multiples (ACM)

Pour étudier **plusieurs** variables qualitatives à la fois (disons $Q$), on recode chaque individu par un vecteur d'indicatrices : pour la variable « canal », trois colonnes (0 ou 1), dont une seule vaut 1. On obtient le **tableau disjonctif complet** $Z$, de $n$ lignes et $J=\sum_q J_q$ colonnes ($J_q$ modalités pour la variable $q$). L'ACM est simplement **l'analyse des correspondances de ce tableau $Z$**, avec les mêmes formules.

Appliquons-la à six variables : canal, ville, tranche d'âge, tranche de panier, offre de bienvenue et rachat dans les 12 mois.


Deux remarques sur ces nombres. D'abord, l'inertie totale de l'ACM vaut **toujours** $(J-Q)/Q$, indépendamment des données : ici $(20-6)/6\approx2{,}33$ (le nombre de modalités moins le nombre de variables, rapporté au nombre de variables). Ensuite, les valeurs propres décroissent **très lentement**, et les pourcentages d'inertie sont donc faibles ($10{,}1\ \%$ et $8{,}4\ \%$ pour les deux premiers axes) : c'est normal en ACM, c'est un effet du codage, pas un signe d'absence de structure. Une correction classique, due à **Benzécri**, ne garde que les valeurs propres supérieures à $1/Q$ et les transforme en

$$\lambda_k^{\text{corr}}=\Bigl(\frac{Q}{Q-1}\Bigr)^2\Bigl(\lambda_k-\frac1Q\Bigr)^2\qquad(\lambda_k>1/Q),$$

ce qui donne des pourcentages plus réalistes (six valeurs propres dépassent $1/Q=0{,}1667$) :


Pour savoir **quelle variable construit quel axe**, on calcule les **contributions** : celle de la modalité $j$ à l'axe $k$ vaut $c_j\,G_{jk}^2/\sigma_k^2$ (somme égale à 1 sur les modalités d'un même axe). En additionnant par variable, on voit quelles variables « fabriquent » chaque axe.

```text
                   axe 1  axe 2  axe 3
canal_acquisition   36.0    2.0   17.0
ville                1.0   11.0   27.0
tranche_age         11.0   17.0   37.0
tranche_panier      47.0    5.0   17.0
offre_bienvenue      0.0   28.0    2.0
rachat_12m           5.0   37.0    0.0
```

![Analyse des correspondances multiples : plan des deux premiers axes. Les modalités des quatre variables d'intérêt sont étiquetées (couleur par variable) ; les six modalités de ville sont les points gris.](figures/ch03-acm-carte.png)

Avec la correction de Benzécri, le premier axe porte à lui seul près de $78\ \%$ de l'« inertie utile » et le deuxième $15\ \%$ : l'essentiel de la structure est dans le plan de la carte. Le tableau des contributions et la carte se lisent ensemble :

1. **L'axe 1** est construit par la **tranche de panier** ($47\ \%$) et le **canal** ($36\ \%$) : il oppose Boutique et très grands paniers (à droite) à Réseaux et très petits paniers (à gauche), l'association déjà vue en 3.4.3. L'âge y contribue un peu ($11\ \%$) : les moins de 30 ans sont du côté des petits paniers.
2. **L'axe 2** est construit par le **rachat** ($37\ \%$), l'**offre de bienvenue** ($28\ \%$) et, dans une moindre mesure, l'**âge** ($17\ \%$) : `offre=1` est proche de `rachat=1`, loin de `offre=0` et `rachat=0`, et les moins de 30 ans sont du même côté que les rachats.
3. **Les villes** contribuent à peine aux deux premiers axes ($1\ \%$ et $11\ \%$) : leurs points gris sont dispersés (ce sont de petits groupes, dont les coordonnées sont instables) mais ne s'associent à rien de particulier.

> 🧪 **Révélation.** Tout cela correspond à la simulation : le canal détermine le panier ; l'offre de bienvenue augmente la probabilité de rachat ; l'âge agit à la fois sur le panier (les plus âgées dépensent un peu plus) et sur le rachat (les plus jeunes rachètent davantage) ; la ville n'a aucun effet. L'ACM n'a reçu aucune variable « à expliquer » : elle a simplement dessiné les associations qui existent dans le tableau.

> 💡 **À quoi sert l'ACM ?** L'ACM est la porte d'entrée classique pour explorer **un questionnaire avec des modalités qualitatives** (profils de clientes, réponses à choix multiples). Elle est aussi utilisée pour construire des **typologies** : on calcule les coordonnées des individus sur les premiers axes, puis on les classe par k-means ou classification hiérarchique (section 3.3). Mais prudence : l'ACM décrit **les associations observées**, elle n'établit pas de causalité.

> ⚠️ **Autres pièges.** (1) Les **modalités rares** (quelques individus) ont des coordonnées extrêmes et peuvent dominer un axe : regroupez-les ou mettez-les en éléments supplémentaires. (2) L'AC est **descriptive** : testez d'abord l'association (khi-deux), puis décrivez-la. (3) Dans l'ACM, **chaque variable pèse son nombre de modalités** : une variable à 15 modalités dominera une variable à 2.

> ✅ **À retenir**
> - L'AC transforme un **tableau de contingence** en cartes : les modalités fréquemment associées sont **proches**.
> - Mathématiquement, c'est la **SVD des résidus standardisés** $S_{ij}=(p_{ij}-r_ic_j)/\sqrt{r_ic_j}$ ; l'**inertie totale** vaut $\chi^2/n$ et se répartit sur les axes.
> - Avant d'interpréter une carte, **testez l'association** : une carte d'indépendance a l'air tout aussi sérieuse.
> - L'**ACM** est l'AC du tableau disjonctif complet ; son inertie totale vaut $(J-Q)/Q$ ; les pourcentages d'inertie sont faibles par construction (corrigez avec Benzécri) ; les **contributions** disent quelle variable construit quel axe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.4, exercice 3.14.


## 3.5 ➕ Pour aller plus loin : l'analyse discriminante

> 🧭 **Section optionnelle.** Elle fait le pont entre ce chapitre (où l'on cherche des groupes inconnus) et le chapitre 2 (où l'on prédit une catégorie à partir de variables). Elle suppose connue la régression logistique de la section 2.2, et reprend la formule de Bayes et la loi normale du volume I (sections 2.1 et 2.2) ; la loi normale **multivariée** est rappelée en 3.5.1.

> 💡 **Intuition.** Jusqu'ici, nous avons cherché des groupes **sans savoir** à quoi ils ressemblent. Ici, on **connaît** les groupes (les clientes qui ont racheté, celles qui n'ont pas racheté) et l'on veut deux choses : (1) **classer** une nouvelle cliente dans le bon groupe, (2) **décrire** ce qui distingue le mieux les groupes. L'idée de l'**analyse discriminante** est élégante : on suppose que, **dans chaque groupe**, les variables suivent une loi normale, et l'on applique la formule de Bayes pour calculer la probabilité d'appartenir à chaque groupe étant donné ce que l'on observe.

### 3.5.1 La règle de Bayes avec des groupes gaussiens

Soit $K$ groupes de probabilités a priori $\pi_1,\dots,\pi_K$ (la part de chaque groupe dans la population). Supposons qu'au sein du groupe $k$, le vecteur de variables $\mathbf x\in\mathbb R^p$ suive une loi normale $\mathcal N(\boldsymbol\mu_k,\Sigma_k)$, de densité $f_k$. (Rappel : la densité d'une loi normale multivariée est $f(\mathbf x)=(2\pi)^{-p/2}|\Sigma|^{-1/2}\exp\bigl(-\tfrac12(\mathbf x-\boldsymbol\mu)^\top\Sigma^{-1}(\mathbf x-\boldsymbol\mu)\bigr)$ ; avec $p=1$, on retrouve la loi normale usuelle de moyenne $\mu$ et de variance $\Sigma=\sigma^2$.) La formule de Bayes donne

$$\mathbb P(G=k\mid\mathbf x)=\frac{\pi_k\,f_k(\mathbf x)}{\sum_l\pi_l\,f_l(\mathbf x)}.$$

La règle de classement la plus naturelle consiste à **choisir le groupe de plus grande probabilité a posteriori**, c'est-à-dire de plus grand $\pi_kf_k(\mathbf x)$. En passant au logarithme (qui conserve l'ordre) :

$$\ln\bigl(\pi_kf_k(\mathbf x)\bigr)=\ln\pi_k-\tfrac12\ln|\Sigma_k|-\tfrac12(\mathbf x-\boldsymbol\mu_k)^\top\Sigma_k^{-1}(\mathbf x-\boldsymbol\mu_k)+\text{constante}.$$

> 📐 **Le cas particulier de la covariance commune (LDA).** Supposons que **tous les groupes aient la même matrice de covariance** : $\Sigma_k=\Sigma$. Les termes $-\tfrac12\ln|\Sigma|$ et $-\tfrac12\mathbf x^\top\Sigma^{-1}\mathbf x$ sont alors identiques pour tous les groupes : ils ne changent pas le classement. En développant le carré, il reste la **fonction discriminante linéaire**
>
> $$\boxed{\delta_k(\mathbf x)=\mathbf x^\top\Sigma^{-1}\boldsymbol\mu_k-\tfrac12\boldsymbol\mu_k^\top\Sigma^{-1}\boldsymbol\mu_k+\ln\pi_k}$$
>
> et l'on classe $\mathbf x$ dans le groupe de plus grand $\delta_k$. La frontière entre deux groupes $k$ et $l$ est l'ensemble des $\mathbf x$ où $\delta_k=\delta_l$ : c'est une équation du **premier degré** en $\mathbf x$, donc un **hyperplan**. D'où le nom d'**analyse discriminante linéaire** (LDA, *linear discriminant analysis*). Si l'on abandonne l'hypothèse $\Sigma_k=\Sigma$, les termes quadratiques ne s'annulent plus et la frontière est une quadrique : c'est l'**analyse discriminante quadratique** (QDA).

**Un exemple à la main, avec une seule variable.** La gérante note la satisfaction (de 1 à 5) de chaque cliente. Parmi celles qui **n'ont pas** racheté, la satisfaction moyenne est $\mu_0=3$ ; parmi celles qui ont racheté, $\mu_1=4$. Dans les deux groupes, l'écart-type est $\sigma=0{,}8$. Pour deux groupes et une variable, la règle « $\delta_1(x)>\delta_0(x)$ » équivaut à

$$x>\frac{\mu_0+\mu_1}{2}+\frac{\sigma^2}{\mu_1-\mu_0}\ln\frac{\pi_0}{\pi_1}.$$

- **Groupes de même taille** ($\pi_0=\pi_1=0{,}5$) : le logarithme est nul, et le seuil est le **milieu** des deux moyennes, $3{,}5$. Au-dessus de $3{,}5$, on prédit « rachète ».
- **Beaucoup de non-racheteuses** ($\pi_0=0{,}7$, $\pi_1=0{,}3$) : le seuil devient $3{,}5+\dfrac{0{,}64}{1}\ln\dfrac{0{,}7}{0{,}3}\approx3{,}5+0{,}64\times0{,}847\approx4{,}04$. Comme la population compte surtout des non-racheteuses, la règle devient **plus exigeante** avant de prédire « rachète » : le seuil est remonté vers le groupe rare.


### 3.5.2 Estimer le modèle

Dans la pratique, les paramètres sont inconnus : on les remplace par leurs estimations sur un échantillon d'apprentissage :

- $\hat\pi_k=n_k/n$, la proportion de chaque groupe ;
- $\hat{\boldsymbol\mu}_k$ : la moyenne des observations du groupe $k$ ;
- $\hat\Sigma=\dfrac{1}{n-K}\sum_k\sum_{i\in G_k}(\mathbf x_i-\hat{\boldsymbol\mu}_k)(\mathbf x_i-\hat{\boldsymbol\mu}_k)^\top$ : la **covariance intra-groupe poolée** (pour la LDA), moyenne pondérée des covariances de chaque groupe, avec le diviseur $n-K$ (le même raisonnement qu'au volume I, section 3.2.3, pour la variance sans biais).

> ⚠️ **Le nombre de paramètres.** La LDA estime $Kp$ moyennes et $p(p+1)/2$ covariances (une seule matrice) ; la QDA estime $Kp$ moyennes et $K\,p(p+1)/2$ covariances (une par groupe). Pour $p=3$ variables et $K=2$ groupes : $6+6=12$ paramètres (plus les proportions) pour la LDA, contre $6+12=18$ pour la QDA. Avec $p=30$ variables, la différence devient énorme (465 paramètres de covariance contre 930). La QDA est plus **flexible** mais plus **variable** : avec peu de données, la LDA, plus simple, est souvent meilleure même quand ses hypothèses ne sont pas tout à fait vraies. C'est le compromis biais-variance du volume I.

**Un exemple sur les données : prédire le rachat.** Reprenons le questionnaire de satisfaction (section 3.2.8). Chaque répondante a deux scores (produits, service), un âge, et l'on sait si elle a **racheté dans les 12 mois** (`rachat_12m`). On met de côté 362 répondantes pour **tester** la règle sur des données qu'elle n'a jamais vues (l'évaluation sur données de test est approfondie au volume III) ; le reste (850) sert à l'ajuster.


Écrite à la main (trois petites fonctions : estimer, calculer les scores $\delta_k$, en déduire les probabilités ; voir l'application 3.5 du cahier), la LDA estime, sur les 850 répondantes d'apprentissage, des probabilités a priori de $0{,}499$ et $0{,}501$ et les moyennes suivantes :

| | score produits | score service | âge |
|---|---:|---:|---:|
| pas de rachat | 3,46 | 3,42 | 36,82 |
| rachat | 3,78 | 3,68 | 35,60 |


Évaluons maintenant la règle sur les 362 répondantes de test, et comparons-la à la bibliothèque (`scikit-learn`) et à la QDA :

| | précision (test) | AUC (test) |
|---|---:|---:|
| LDA | 0,657 | 0,705 |
| QDA | 0,638 | 0,708 |


> 💡 **Lire la précision et l'AUC.** La **précision** est la proportion de bonnes prédictions. L'**AUC** (aire sous la courbe ROC) mesure la capacité du modèle à **ordonner** les individus : c'est la probabilité qu'une cliente qui rachète reçoive un score plus élevé qu'une cliente qui ne rachète pas (0,5 : hasard ; 1 : parfait). Ces deux mesures et leurs pièges font l'objet du volume III ; retenez simplement ici qu'on les calcule **sur des données de test**, jamais sur celles qui ont servi à l'ajustement.

La règle écrite à la main reproduit celle de la bibliothèque (mêmes prédictions, probabilités identiques à $0{,}0005$ près). Le résultat est modeste : la matrice de confusion montre $121+117=238$ bonnes prédictions sur 362, soit environ deux sur trois ($65{,}7\ \%$). C'est mieux que le hasard (la précision d'un tirage à pile ou face serait de $50\ \%$) mais loin d'une prédiction fiable : 55 non-racheteuses sont prédites racheteuses, et 69 racheteuses passent inaperçues. C'est normal : la satisfaction mesurée n'est qu'**un** déterminant du rachat parmi d'autres, et celui-ci est intrinsèquement incertain. Notez aussi que la **QDA ne fait pas mieux** que la LDA ($63{,}8\ \%$ contre $65{,}7\ \%$ de précision, des AUC quasi identiques) : ses 6 paramètres de covariance supplémentaires n'apportent rien. L'écart de 2 points est de l'ordre du bruit d'un échantillon de test de 362 personnes, il ne faut donc pas en tirer plus que : « elle ne fait pas mieux ». Cela suggère que l'hypothèse de covariance commune est raisonnable ici.

### 3.5.3 LDA et régression logistique : deux routes vers la même frontière

Calculons le **logarithme du rapport des probabilités a posteriori** (la « log-cote ») de deux groupes, avec la covariance commune :

$$\ln\frac{\mathbb P(G=1\mid\mathbf x)}{\mathbb P(G=0\mid\mathbf x)}=\delta_1(\mathbf x)-\delta_0(\mathbf x)=\underbrace{\ln\frac{\pi_1}{\pi_0}-\tfrac12(\boldsymbol\mu_1+\boldsymbol\mu_0)^\top\boldsymbol\beta}_{\beta_0}+\boldsymbol\beta^\top\mathbf x,\qquad \boldsymbol\beta=\Sigma^{-1}(\boldsymbol\mu_1-\boldsymbol\mu_0).$$

(on vérifie que $\tfrac12(\boldsymbol\mu_0^\top\Sigma^{-1}\boldsymbol\mu_0-\boldsymbol\mu_1^\top\Sigma^{-1}\boldsymbol\mu_1)=-\tfrac12(\boldsymbol\mu_1+\boldsymbol\mu_0)^\top\Sigma^{-1}(\boldsymbol\mu_1-\boldsymbol\mu_0)$.) La log-cote est donc **linéaire en $\mathbf x$** : c'est précisément la forme du modèle de la régression logistique de la section 2.2, $\ln\frac{p}{1-p}=\beta_0+\boldsymbol\beta^\top\mathbf x$.

Les deux méthodes ont donc **la même forme**, mais elles ne **calculent pas** les coefficients de la même façon :

- la **LDA** estime les moyennes et la covariance, puis en déduit $\boldsymbol\beta=\hat\Sigma^{-1}(\hat{\boldsymbol\mu}_1-\hat{\boldsymbol\mu}_0)$ : elle modélise **comment les $\mathbf x$ sont distribués dans chaque groupe** (modèle *génératif*) ;
- la **régression logistique** maximise directement la vraisemblance de $P(G\mid\mathbf x)$ (modèle *discriminatif*) et ne dit rien de la distribution des $\mathbf x$.

Comparons les coefficients des trois approches sur nos données :

```text
                LDA (formule)  LDA (scikit-learn)  régression logistique
constante              -3.345              -3.353                 -3.341
score_produits          0.663               0.664                  0.663
score_service           0.401               0.402                  0.399
age                    -0.013              -0.013                 -0.013
AUC de la régression logistique (test) : 0.705
```

Les trois colonnes sont presque identiques. Quand les données sont vraiment gaussiennes avec une covariance commune, la LDA est légèrement **plus efficace** (elle exploite l'hypothèse de forme) ; quand elles ne le sont pas, la régression logistique est plus **robuste** (elle ne fait pas d'hypothèse sur la loi des $\mathbf x$). En pratique, avec des variables qui ne sont pas gaussiennes (une variable 0/1 comme l'offre de bienvenue, par exemple), on préfère la **régression logistique** (section 2.2).

> 🧪 **Révélation.** Dans la simulation, la log-cote de rachat dépend, par unité de facteur latent, de $+0{,}45$ pour le facteur « produits », $+0{,}35$ pour le facteur « service », et de $-0{,}015$ par année d'âge (plus l'effet de l'offre de bienvenue, que nous n'avons pas inclus ici). Les coefficients des **scores** ne sont pas directement comparables à ceux des **facteurs** : un facteur latent a un écart-type de 1, un score est une moyenne de notes de 1 à 5 dont l'écart-type est bien plus petit, de sorte qu'une unité de score correspond à beaucoup plus d'unités de facteur. Ce que l'on peut comparer, c'est le **signe** et l'**ordre** : le score « produits » pèse plus que le score « service », comme les facteurs, et l'âge a un effet négatif d'environ $-0{,}013$ par an, très proche des $-0{,}015$ programmés (l'âge, lui, est mesuré sans erreur).

### 3.5.4 Fisher : la projection qui sépare le mieux les groupes

Il existe une autre façon, géométrique, d'arriver à la LDA, due à R. A. Fisher. Au lieu d'un modèle de probabilité, on cherche **la direction $\mathbf a$ sur laquelle projeter les données** pour que les groupes soient le plus séparés possible, c'est-à-dire pour maximiser le rapport

$$J(\mathbf a)=\frac{\mathbf a^\top B\,\mathbf a}{\mathbf a^\top W\,\mathbf a}=\frac{\text{variance entre les groupes}}{\text{variance à l'intérieur des groupes}},$$

où $B$ est la covariance **entre** groupes (dispersion des moyennes de groupes autour de la moyenne générale) et $W$ la covariance **intra**-groupe (la matrice $\hat\Sigma$ de plus haut). En annulant le gradient, on tombe sur un **problème aux valeurs propres généralisé** (comme pour l'ACP, section 3.1.3) : $W^{-1}B\,\mathbf a=\lambda\mathbf a$. Avec $K$ groupes, la matrice $B$ est de rang au plus $K-1$ : il y a **au plus $K-1$ axes discriminants** utiles. La LDA devient alors une technique de **réduction de dimension supervisée** : contrairement à l'ACP, qui cherche la direction de plus grande variance **totale**, elle cherche la direction qui **sépare les groupes connus**.

Illustrons-le avec les **600 clientes simulées** de la section 3.3, dont on connaît les trois profils (occasionnelles, fidèles, cadeaux). Les variables sont leurs deux caractéristiques standardisées.


Avec trois groupes et deux variables, il y a deux axes discriminants (au plus $K-1=2$). Le premier porte les deux tiers du pouvoir séparateur ($65{,}5\ \%$), le second le tiers restant ($34{,}5\ \%$) : les deux axes sont utiles, ce qui est naturel puisque les trois profils s'étalent dans les deux directions du plan. Les deux méthodes classent très bien (plus de $98\ \%$ des 600 clientes). La QDA fait **un peu mieux** ($99{,}2\ \%$ contre $98{,}3\ \%$, soit cinq clientes de plus bien classées) : les trois profils n'ont pas la même dispersion (les clientes « cadeaux » ont un panier beaucoup plus variable que les autres), l'hypothèse de covariance commune est donc fausse, et des frontières courbes s'adaptent un peu mieux. Prudence : il s'agit de la précision sur les données d'**apprentissage** (voir le piège 5), et l'écart est faible.

![Frontières de décision de la LDA (à gauche, droites) et de la QDA (à droite, courbes) sur les 600 clientes simulées de la section 3.3. Chaque point est coloré par son vrai profil ; la couleur de fond est la classe prédite.](figures/ch03-lda-frontieres.png)

### 3.5.5 Les pièges de l'analyse discriminante

> ⚠️ **1. L'hypothèse gaussienne.** Les variables d'un même groupe doivent être à peu près normales. Elle est violée par des variables binaires, des comptages, des variables très asymétriques (montants) : transformez-les (par exemple en logarithme, volume I, section 3.1.3) ou utilisez la régression logistique (section 2.2).
>
> **2. La covariance commune.** À vérifier (comparez les covariances de chaque groupe) : si elle est fausse et que l'on a beaucoup de données, préférez la QDA ; sinon, la LDA est plus stable.
>
> **3. Les probabilités a priori.** Elles déplacent la frontière (voir l'exemple à la main). Par défaut, on prend les proportions de l'échantillon d'apprentissage : cela suppose que les futurs individus auront les mêmes proportions. Si l'on classe des clientes dont la composition diffère de celle de l'échantillon, il faut les modifier.
>
> **4. Beaucoup de variables, peu d'individus.** $\hat\Sigma$ devient instable, puis non inversible quand $p\geq n$. On régularise (méthodes du volume III) ou on réduit d'abord la dimension par ACP.
>
> **5. L'évaluation sur les données d'apprentissage est trompeuse.** Une règle ajustée sur un échantillon classe presque toujours mieux cet échantillon que de nouvelles données : on évalue sur un échantillon de test ou par validation croisée (volume III).

> ✅ **À retenir**
> - Avec des groupes gaussiens, la **règle de Bayes** classe un individu dans le groupe de plus grande probabilité a posteriori.
> - **LDA** (covariance commune) : fonction discriminante $\delta_k(\mathbf x)=\mathbf x^\top\Sigma^{-1}\boldsymbol\mu_k-\frac12\boldsymbol\mu_k^\top\Sigma^{-1}\boldsymbol\mu_k+\ln\pi_k$, **frontières linéaires** ; **QDA** (une covariance par groupe) : frontières **quadratiques**, plus flexible mais plus variable.
> - La log-cote de la LDA est **linéaire** : même forme que la **régression logistique** (section 2.2), estimée autrement (modèle génératif contre discriminatif).
> - **Fisher** : la LDA maximise le rapport variance entre groupes / variance intra-groupe ; avec $K$ groupes, au plus $K-1$ axes discriminants.
> - Les probabilités a priori déplacent le seuil ; on évalue toujours sur des données de test.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.13.


## Bilan du chapitre 3

Vous savez maintenant :

- **résumer** un tableau de variables numériques par une **ACP** : l'écrire comme la diagonalisation de la matrice de covariance (ou la SVD du tableau centré), choisir entre covariance et corrélation (**standardiser** quand les unités diffèrent), choisir le nombre de composantes (éboulis, Kaiser, **analyse parallèle**), lire saturations, scores et biplot, et mesurer ce que l'on perd (somme des valeurs propres jetées) ;
- distinguer l'ACP, qui **résume**, de l'**analyse factorielle**, qui **modélise** les corrélations par des facteurs cachés ($\Sigma=\Lambda\Lambda^\top+\Psi$) ; estimer, **tester l'ajustement**, choisir le nombre de facteurs, **faire tourner** les axes (varimax) sans changer l'ajustement, et construire des échelles de mesure (alpha de Cronbach) ;
- **classer sans étiquettes** : les **k-means** (algorithme de Lloyd, k-means++, minimum local), la **classification hiérarchique** (critères d'agrégation, dendrogramme) ; **choisir $k$** (coude, silhouette) et surtout **vérifier qu'il y a des groupes** (silhouette, stabilité par bootstrap et ARI) ;
- (en option) étendre l'idée aux **variables qualitatives** par l'**analyse des correspondances** (SVD des résidus standardisés, inertie $=\chi^2/n$) et l'**ACM** ;
- (en option) passer des groupes inconnus aux groupes connus avec l'**analyse discriminante** : règle de Bayes avec des classes gaussiennes, LDA (frontières linéaires) et QDA, lien avec la **régression logistique**, projection de Fisher.

Un fil rouge traverse le chapitre : **une méthode descriptive rend toujours un résultat**, même sur du bruit. Un axe, un facteur, un groupe, une carte n'ont de valeur qu'accompagnés de leurs **diagnostics** (parts d'inertie et analyse parallèle, test d'ajustement, silhouette et stabilité, khi-deux avant de lire une carte).

Le chapitre 4 change d'horizon : après les données « en coupe » (un instantané de clientes), les **séries temporelles**, où l'ordre des observations compte et où la mémoire du passé devient l'information principale. Les ventes mensuelles de la boutique, de 2016 à 2025, nous y attendent.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.5 et exercices 3.1 à 3.14, tous corrigés.
