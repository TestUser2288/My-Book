# Chapitre 4 : Ingénierie des variables et données déséquilibrées

> « Les algorithmes ne voient pas vos données : ils voient les nombres que vous leur donnez. »

Les chapitres précédents ont traité du **modèle** : comment l'évaluer (chapitre 1), quelles familles choisir (chapitre 2). Ce chapitre s'occupe de ce qui se passe **avant** le modèle : la façon dont on **présente** les données à l'algorithme. Un même modèle, sur les mêmes clients, peut passer d'un résultat médiocre à un très bon résultat selon la manière dont une ville est codée, dont une valeur manquante est remplacée, ou dont une règle de bon sens est transformée en variable. Et il peut se tromper de façon spectaculaire, tout en affichant 99 % d'exactitude, quand ce qu'il doit détecter est rare.

## Le chemin de ce chapitre

- **4.1 Encodage, mise à l'échelle, transformations** : transformer des catégories, des unités et des valeurs manquantes en nombres que les modèles savent lire, **sans fuite d'information** ; assembler le tout dans un `Pipeline`.
- **4.2 Création et sélection de variables** : fabriquer des variables qui expriment ce que l'on sait du métier, découvrir des seuils à partir des données, repérer redondances et fuites.
- **4.3 Classes déséquilibrées** : pourquoi l'exactitude trompe, ce que font réellement les poids de classes, le rééchantillonnage, et le rôle décisif du **seuil de décision** et des **coûts**.
- ➕ **4.4 Méthodes de sélection de variables** : filtre, enveloppe, méthodes intégrées, et le piège du biais de sélection.
- ➕ **4.5 SMOTE et variantes** : fabriquer des exemples synthétiques, et surtout savoir quand ne pas le faire.
- **Bilan du chapitre**.

> 🧭 **Fil rouge du chapitre : l'ordre des opérations.** Presque toutes les erreurs graves de ce chapitre ont la même forme : une opération qui *apprend quelque chose des données* (une moyenne, une catégorie fréquente, un seuil, un échantillon synthétique) est appliquée **avant** la séparation entre entraînement et validation. Le jeu de validation « sait » alors des choses sur lui-même, et la performance affichée est trop belle. Retenez la règle ; nous la rencontrerons cinq fois : **tout ce qui est appris est appris sur le jeu d'entraînement, et seulement lui** (chapitre 1, section 1.1).

## Les données du chapitre

Deux fichiers de la boutique servent d'exemples (tous deux **simulés** ; voir l'introduction du volume).

| Fichier | Contenu | Cible | Sert pour |
|---|---|---|---|
| `clients_ml.csv` | 12 000 clients observés au 31 décembre 2025 : âge, ville (20 modalités), canal d'acquisition, activité des 12 derniers mois, satisfaction, assistance, promotions… | `churn_90j` : le client ne commande plus dans les 90 jours suivants (14 % des clients) | encodage, échelles, valeurs manquantes, création de variables, sélection |
| `transactions.csv` | 60 000 commandes en ligne : montant, heure, appareil, distance entre adresses, ancienneté du compte… | `fraude` : la commande est frauduleuse (0,8 % des commandes) | classes déséquilibrées, SMOTE |


Le découpage entraînement/test (75 % / 25 %, stratifié sur la cible, graine fixée) est le même dans tout le chapitre ; il est fait **une fois pour toutes, avant** tout apprentissage. Sur les variables numériques brutes, une régression logistique atteint une AUC de 0,858 sur le jeu de test et un gradient boosting 0,892 : ce sont nos **points de départ**. Les sections qui suivent montrent ce que valent, ou ne valent pas, les différentes façons de préparer les variables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : le chapitre du cahier commence par une section « Préparation » qui recharge ces données et refait ce découpage.


## 4.1 Encodage, mise à l'échelle, transformations

Un modèle ne manipule que des **nombres**. Or une table de clients contient des villes, des canaux, des valeurs manquantes, des montants qui vont de 5 € à 3 000 €, des âges, des indicateurs 0/1. Passer de la table au tableau de nombres que le modèle consommera s'appelle le **prétraitement** (*preprocessing*). Cette section en détaille les quatre grandes opérations : encoder les catégories, mettre les variables à une échelle comparable, corriger les distributions asymétriques, et traiter les valeurs manquantes. La dernière sous-section montre comment tout assembler **sans fuite**.

### 4.1.1 Deux familles de modèles, deux besoins

Avant d'apprendre à transformer, demandons-nous **quand c'est nécessaire**. Les modèles se répartissent en deux familles très différentes face au prétraitement.

- Les modèles **à base de distances ou de pénalités** (k plus proches voisins, SVM, régression logistique régularisée, réseaux de neurones) comparent des variables entre elles par des sommes de carrés. Si une variable s'exprime en euros (de 0 à 3 000) et une autre en nombre de tickets (de 0 à 8), la première écrase l'autre : l'**échelle** décide, sans qu'on l'ait voulu.
- Les modèles **à base d'arbres** (arbres, forêts, boosting) ne font que **comparer une variable à un seuil**. Multiplier une variable par 1 000, ou lui appliquer une transformation croissante comme le logarithme, ne change aucune comparaison « inférieur à ? » : les partitions possibles sont les mêmes. Ils sont donc **insensibles à l'échelle et aux transformations monotones**. En revanche, ils ne « voient » pas facilement qu'un ratio de deux variables compte, et la plupart des implémentations ne lisent pas une catégorie de texte (certaines, comme `HistGradientBoosting`, LightGBM ou CatBoost, acceptent des variables déclarées comme qualitatives).

Cette observation guide tout le reste : on choisit le prétraitement **en fonction du modèle**, et non pas une fois pour toutes.

### 4.1.2 Encoder une variable qualitative

Une **variable qualitative** (la ville, le canal d'acquisition, la catégorie de produit préférée) doit être traduite en nombres. Quatre méthodes couvrent presque tous les cas, auxquelles s'ajoute une cinquième pour les très grands nombres de modalités.

**L'encodage disjonctif (*one-hot*).** On crée une colonne 0/1 par modalité : pour le canal, `canal_Boutique`, `canal_Site`, `canal_Réseaux`. Un client de la boutique vaut $(1,0,0)$. C'est la méthode par défaut pour les modèles linéaires : chaque modalité reçoit son propre coefficient, sans ordre imposé. Ses défauts apparaissent quand il y a beaucoup de modalités : 20 villes donnent 20 colonnes, 2 000 codes postaux en donneraient 2 000, presque toutes vides, et les arbres perdent en efficacité à fragmenter l'information.

**L'encodage ordinal.** On remplace chaque modalité par un entier (1, 2, 3…). Il n'est correct que si les modalités ont un **ordre naturel** (« jamais / parfois / souvent »). Appliqué à des villes, il invente un ordre qui n'existe pas : un modèle linéaire croirait que la ville 3 est « entre » les villes 2 et 4.

**L'encodage par fréquence.** On remplace chaque modalité par sa **fréquence** dans le jeu d'entraînement (la part des clients qui y habitent). Une seule colonne, aucune fuite de la cible, mais l'information « grande ou petite ville » est mélangée à toute autre.

**L'encodage par la cible (*target encoding*).** On remplace chaque modalité par la **moyenne de la cible** observée dans cette modalité : pour la ville, le taux de départ des clients qui y habitent. C'est puissant (une seule colonne, qui contient directement l'information utile), mais c'est aussi **la source de fuite d'information la plus classique** du prétraitement. Voyons pourquoi.

**L'encodage par hachage (*hashing trick*).** Quand une variable a des milliers, voire des millions de modalités (des identifiants de produits, des mots), on applique une **fonction de hachage** au nom de la modalité, on prend le résultat modulo $m$, et on place la modalité dans l'une des $m$ colonnes d'un *one-hot* de largeur fixe (par exemple $m=256$). Il n'y a pas de dictionnaire à garder et de nouvelles modalités sont acceptées sans erreur. Le prix : des **collisions**, c'est-à-dire des modalités différentes qui partagent une colonne, et des colonnes qu'on ne sait plus interpréter. C'est ce que fait `FeatureHasher` dans scikit-learn.

#### Un exemple minuscule

Huit clients, trois villes, et la cible « le client est parti » :

| client | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| **ville** | A | A | A | B | B | B | C | A |
| **parti** | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 |

La moyenne de la cible par ville vaut : pour A (clients 1, 2, 3, 8), $\frac{1+0+0+0}{4}=0{,}25$ ; pour B (clients 4, 5, 6), $\frac{1+1+0}{3}\approx0{,}67$ ; pour C (client 7 seul), $\frac11=1$. La moyenne générale vaut $\frac48=0{,}5$.

Regardons le client 7. Il est **seul** dans sa ville, et son encodage vaut **1, c'est-à-dire exactement sa propre étiquette**. Le modèle apprend « les clients de la ville C partent toujours », alors qu'il s'est simplement relu lui-même. C'est la **fuite par la cible** : l'encodage d'une ligne a été calculé **en utilisant la cible de cette même ligne**. Plus une modalité est rare, plus l'encodage de ses lignes ressemble à leur étiquette, et plus l'effet est trompeur.

#### Deux remèdes

**Le lissage.** On « tire » la moyenne d'une modalité vers la moyenne générale $\mu$, d'autant plus fort que la modalité est petite :

$$\text{encodage}(m)=\frac{n_m\,\bar y_m+k\,\mu}{n_m+k},$$

où $n_m$ est l'effectif de la modalité, $\bar y_m$ sa moyenne et $k$ un paramètre de lissage (un « nombre d'observations virtuelles » à la moyenne $\mu$). Avec $k=2$, la ville C passe de $1$ à $\frac{1+2\times0{,}5}{1+2}\approx0{,}67$ : on ne fait plus confiance à un client isolé. Cette formule est une **moyenne pondérée** entre l'estimation locale et l'estimation globale, la même idée que le rétrécissement des modèles mixtes du volume II (section 1.7).

**Le calcul hors pli (*out-of-fold*).** On découpe le jeu d'entraînement en $K$ plis. L'encodage des lignes du pli $j$ est calculé **uniquement avec les lignes des autres plis**. Ainsi aucune ligne n'est jamais encodée avec sa propre étiquette. Les valeurs obtenues sont bruitées, et c'est tant mieux : ce bruit est celui que le modèle rencontrera réellement sur des données nouvelles. Pour encoder le jeu de test, on utilise les moyennes calculées sur **tout** le jeu d'entraînement.

> ⚠️ **Le piège du « leave-one-out ».** Une variante populaire retire seulement la ligne courante du calcul de la moyenne de sa modalité. Elle paraît raisonnable, mais elle fuit **à l'envers** : dans une même ville, toutes les lignes dont la cible vaut 1 reçoivent une valeur *plus basse* que celles dont la cible vaut 0. Un arbre sépare alors parfaitement les deux groupes en lisant l'encodage. Préférez le calcul par plis.

#### Ce que cela change, en vrai

Pour mesurer l'effet de la fuite, il faut une variable **à forte cardinalité** : beaucoup de modalités, peu de lignes par modalité. Nos 20 villes comptent entre 141 et 1 788 clients, ce qui est trop peu « fin » pour que la fuite se voie. Nous ajoutons donc une variable fictive, un **code postal à 400 modalités tiré au hasard**, qui n'a *par construction* aucun lien avec le départ (22 clients en moyenne par code dans le jeu d'entraînement).


```text
                                          encodage  AUC entraînement         AUC test
moyenne par code, calculée sur tout l'entraînement             0.678             0.51
               moyenne par code, calculée hors pli             0.509 (non applicable)
```

Le résultat est sans ambiguïté. Avec l'encodage naïf, la variable semble prédire le départ sur le jeu d'entraînement (AUC 0,678) alors qu'elle est **du pur bruit** : sur le jeu de test, l'AUC tombe à 0,510, c'est-à-dire au niveau du hasard. Le calcul hors pli, lui, donne honnêtement 0,509 dès l'entraînement : il ne se laisse pas tromper. Un modèle qui apprendrait sur la version naïve accorderait de l'importance à une variable qui n'en a pas.

Et pour les **vraies** villes de la boutique ? Le tableau suivant compare quatre encodages sur le jeu de test. Chaque nombre est une AUC, pour une régression logistique et pour un boosting.


```text
        encodage de la ville  AUC logistique  AUC boosting
               sans la ville           0.858         0.892
        disjonctif (one-hot)           0.863         0.895
                   fréquence           0.859         0.897
             cible, hors pli           0.864         0.896
cible (TargetEncoder, lissé)           0.864         0.900
```

Les cinq lignes se ressemblent : ajouter l'information de la ville améliore l'AUC de quelques millièmes (de 0,858 à 0,864 pour la logistique, de 0,892 à 0,895–0,900 pour le boosting), mais **les écarts entre les encodages sont plus petits que l'incertitude** d'une AUC mesurée sur 3 000 clients de test (une erreur-type d'environ 0,011, formule de Hanley et McNeil ; section 1.4). N'en tirez pas de classement. La leçon n'est pas « tel encodage est le meilleur » ; elle est : **avec peu de modalités bien peuplées, tous conviennent ; avec beaucoup de modalités rares, seul le calcul hors pli reste honnête**.

> ✅ **À retenir (encodage).** *One-hot* pour les modèles linéaires et peu de modalités ; ordinal seulement si l'ordre existe ; fréquence quand on veut une seule colonne sans la cible ; **cible** pour beaucoup de modalités, mais **toujours hors pli et lissée**. Et jamais avec les lignes du jeu de test.

### 4.1.3 Mettre les variables à la même échelle

La **mise à l'échelle** (*scaling*) remplace chaque variable $x$ par une version dont l'unité a disparu. Quatre transformations dominent.

| Transformation | Formule | Propriété |
|---|---|---|
| **Standardisation** | $\dfrac{x-\bar x}{s}$ | moyenne 0, écart-type 1 ; sensible aux valeurs extrêmes |
| **Min-max** | $\dfrac{x-x_{\min}}{x_{\max}-x_{\min}}$ | tout dans $[0,1]$ ; une valeur extrême écrase les autres |
| **Robuste** | $\dfrac{x-\text{médiane}}{Q_3-Q_1}$ | utilise médiane et écart interquartile, **insensible** aux extrêmes |
| **Quantile** | rang de $x$ dans le jeu d'entraînement, ramené à $[0,1]$ | distribution uniforme ; défait toute asymétrie |

Un exemple à la main montre leurs différences. Cinq montants d'achats : 20, 25, 30, 35 et 400 € (le dernier est un gros achat professionnel). La moyenne vaut $102$ et l'écart-type $\approx149{,}1$ ; la médiane vaut $30$ et l'écart interquartile $35-25=10$.


```text
 montant  standardisé  min-max  robuste  quantile (rang)
    20.0       -0.550    0.000     -1.0             0.00
    25.0       -0.516    0.013     -0.5             0.25
    30.0       -0.483    0.026      0.0             0.50
    35.0       -0.449    0.039      0.5             0.75
   400.0        1.999    1.000     37.0             1.00
```

La valeur extrême a deux effets opposés. Avec la **standardisation** et le **min-max**, les quatre petits montants se retrouvent **tassés** dans une toute petite plage (de $-0{,}55$ à $-0{,}45$ ; de $0$ à $0{,}04$) : l'information qui les distingue s'écrase. Avec la transformation **robuste**, ils gardent leur écart ($-1$ à $0{,}5$) et c'est la valeur extrême qui part très loin ($37$) : c'est exactement ce qu'on souhaite. La transformation **quantile** étale tout régulièrement et ne se soucie plus des écarts réels : elle est utile quand seule l'**ordre** compte.

#### Quel modèle a besoin de quoi ?

Mesurons-le sur les clients : 12 variables numériques, quatre modèles, avec et sans standardisation.


```text
                          modèle  sans mise à l'échelle  standardisation  quantile
           régression logistique                  0.856            0.856     0.850
 k plus proches voisins (k = 25)                  0.828            0.853     0.838
            SVM à noyau gaussien                  0.746            0.788     0.781
arbre de décision (profondeur 5)                  0.859            0.859     0.859
L1, C = 0,01 -> conservées seulement SANS échelle : ['nb_promos_recues_12m', 'revenu_zone']
L1, C = 0,01 -> conservées seulement AVEC standardisation : ['part_achats_promo', 'programme_fidelite']
```

Le tableau confirme la théorie. Pour le **k plus proches voisins**, la standardisation fait passer l'AUC de 0,828 à 0,853 : sans elle, le montant (en centaines d'euros) écrase tout dans le calcul des distances. Pour le **SVM**, le gain est de 0,746 à 0,788. L'**arbre** ne bouge pas (0,859 dans tous les cas) : les seuils changent de valeur, pas de sens. Quant à la **régression logistique**, son AUC ne change pas ici (0,856), parce que la solution d'un modèle sans pénalité ne dépend pas de l'unité des variables : si l'on multiplie une variable par 1 000, son coefficient est divisé par 1 000 et les prédictions restent les mêmes. Il en va autrement dès qu'on **pénalise** les coefficients (régularisation, volume II, section 1.5 ; nous y revenons au chapitre 2) : une pénalité compte les coefficients, et un coefficient dépend de l'unité de sa variable. La dernière ligne de la sortie montre l'effet sur une pénalité $\ell_1$ forte (qui met à zéro les variables peu utiles) : sans mise à l'échelle, elle **écarte** `programme_fidelite` et `part_achats_promo` (des variables de petite échelle, 0/1 et 0 à 1, qui ont besoin de gros coefficients pour peser) et garde `revenu_zone` et `nb_promos_recues_12m` ; avec la standardisation, la sélection s'inverse. L'AUC bouge peu, mais **le modèle n'est plus le même** : sans mise à l'échelle, l'unité décide de ce qui est « important ».

> 💡 **Règle pratique.** Standardisez pour tout ce qui calcule des distances ou pénalise des coefficients (kNN, SVM, régression régularisée, réseaux, ACP). Ne vous en souciez pas pour les arbres, forêts et boosting. En cas de valeurs extrêmes marquées, préférez la version robuste.

### 4.1.4 Corriger l'asymétrie : logarithme, Box-Cox, Yeo-Johnson

Les montants, les durées et les effectifs sont presque toujours **asymétriques à droite** : beaucoup de petites valeurs, quelques très grandes (c'est la situation des paniers, vue au volume I, section 3.1.3). Une transformation **concave** (le logarithme, la racine) resserre la queue de droite et rend la distribution plus symétrique. La famille de **Box-Cox** généralise cette idée avec un paramètre $\lambda$ choisi sur les données :

$$x\mapsto\begin{cases}\dfrac{x^{\lambda}-1}{\lambda}&\lambda\neq0\\[2mm]\ln x&\lambda=0\end{cases}\qquad(x>0).$$

Pour $\lambda=1$, on ne change rien (à une translation près) ; pour $\lambda=0$, c'est le logarithme ; pour $\lambda=\frac12$, une racine. Box-Cox exige des valeurs **strictement positives**. La version de **Yeo-Johnson** accepte aussi zéro et les valeurs négatives, en traitant chaque signe à part :

$$x\mapsto\begin{cases}\dfrac{(x+1)^{\lambda}-1}{\lambda}&x\ge0,\ \lambda\neq0\\[1mm]\ln(x+1)&x\ge0,\ \lambda=0\\[1mm]-\dfrac{(1-x)^{2-\lambda}-1}{2-\lambda}&x<0,\ \lambda\neq2\end{cases}$$

(le cas $x<0,\ \lambda=2$ est $-\ln(1-x)$). Le paramètre $\lambda$ est choisi par maximum de vraisemblance, **sur le jeu d'entraînement**.


```text
                  brute  après log(1 + x)  après Yeo-Johnson
montant_12m        2.88              0.06               0.00
nb_commandes_12m   1.71              0.35               0.06
recence_jours      1.89             -0.48              -0.03
panier_moyen       2.54              0.75              -0.00
```

![Distribution du montant dépensé sur 12 mois (clients ayant commandé) : brut, après le logarithme, après la transformation de Yeo-Johnson.](figures/ch04-asymetrie.png)

Le coefficient d'asymétrie (volume I, section 3.1) du montant passe de 2,88 à 0,06 avec le logarithme, et à 0,00 avec Yeo-Johnson : la distribution devient presque symétrique. Mais une transformation qui rend les histogrammes plus jolis **améliore-t-elle le modèle** ? Ici, non : la régression logistique sur les variables brutes obtient une AUC de 0,858, et de 0,852 après passage au logarithme. Le départ d'un client dépend de variables comme la récence *en jours* avec des seuils qui ont un sens dans cette unité ; les écraser ne l'aide pas. **Une transformation est une hypothèse sur la forme de la relation avec la cible**, pas un nettoyage neutre.

> ⚠️ **Normaliser n'est pas toujours utile.** On transforme pour un modèle donné et pour une raison précise (une régression linéaire sensible aux extrêmes, un SVM, un graphique lisible), pas par réflexe. Les modèles à base d'arbres n'en tirent rien. Et il faut **toujours** mesurer sur un jeu de validation.

**Découper en classes** (*binning*) est une autre façon de se libérer de la forme : on remplace une variable continue par des classes (« moins de 30 jours », « 30 à 60 jours »…), ensuite encodées en *one-hot*. Cela permet à un modèle linéaire de représenter une relation non monotone ou à seuils, mais au prix de pertes d'information à l'intérieur des classes, et de frontières à choisir. Nous verrons mieux en 4.2 comment trouver des frontières utiles à partir des données.

### 4.1.5 Les valeurs manquantes

Une valeur manquante n'est pas un détail technique : elle **raconte quelque chose** sur la façon dont les données ont été produites. On distingue trois mécanismes (volume II, introduction : les hypothèses se vérifient).

- **MCAR** (*missing completely at random*) : l'absence ne dépend de rien. Un capteur tombe en panne au hasard. Supprimer les lignes ou imputer ne biaise pas.
- **MAR** (*missing at random*) : l'absence dépend d'autres variables **observées**. Les clients qui n'ont pas d'appareil enregistré sont plus souvent ceux venus en boutique. On peut corriger en s'appuyant sur ces variables.
- **MNAR** (*missing not at random*) : l'absence dépend de la valeur **manquante elle-même**. Les clients mécontents répondent moins à l'enquête de satisfaction. On ne peut pas la corriger complètement avec les seules données observées.

Nos clients contiennent quatre variables incomplètes, de natures différentes.


```text
           variable  part manquante  départs si manquante  départs si renseignée
       panier_moyen           0.136                 0.420                  0.096
   satisfaction_moy           0.128                 0.115                  0.144
           appareil           0.152                 0.154                  0.138
delai_livraison_moy           0.120                 0.135                  0.141
```

Les chiffres montrent que **le fait d'être manquant est parfois très informatif**. Un panier manquant signifie « aucune commande en 12 mois », et ces clients partent dans **42 %** des cas contre 9,6 % pour les autres. L'absence de satisfaction, elle, est liée à un taux de départ plus faible (11,5 % contre 14,4 %). Les deux autres variables (appareil, livraison) n'ont aucun lien avec le départ, comme attendu d'une absence aléatoire.

#### Que faire ?

- **Supprimer les lignes incomplètes** : simple, mais dans ce jeu seules 66 % des lignes sont complètes ; on jette un tiers des clients et on biaise l'échantillon dès que l'absence est informative.
- **Imputer** par une valeur : la moyenne, la médiane, une constante, la valeur des plus proches voisins, ou une prédiction par un autre modèle (imputation itérative).
- **Ajouter un indicateur d'absence** : une colonne 0/1 « cette valeur était manquante », à côté de la valeur imputée. Le modèle peut ainsi utiliser l'absence comme information.
- **Laisser le modèle s'en occuper** : certains boostings (`HistGradientBoosting`, XGBoost, LightGBM) gèrent nativement les valeurs manquantes en apprenant, à chaque seuil, de quel côté les envoyer.

Comparons-les sur nos données.


```text
                                    stratégie  AUC logistique  AUC boosting
                                      moyenne           0.859         0.894
                                      médiane           0.859         0.896
              médiane + indicateurs d'absence           0.858         0.896
          constante 0 + indicateurs d'absence           0.858         0.894
                 plus proches voisins (k = 5)           0.859         0.894
                         imputation itérative           0.859         0.894
boosting : gestion native (aucune imputation)               -         0.892
```

Les sept lignes donnent **pratiquement le même résultat** : de 0,858 à 0,859 pour la logistique, de 0,892 à 0,896 pour le boosting. Dans ces données, le choix de l'imputation n'a quasiment aucune importance, d'abord parce que les variables qui comptent vraiment (récence, nombre de commandes) sont complètes, ensuite parce que l'information « pas de commande » est déjà portée par une variable observée. C'est rassurant, mais **pas universel** : le petit exemple suivant montre un cas où l'indicateur d'absence change tout.

#### Quand l'absence est l'information

Simulons 6 000 clients avec une variable $x$ liée à la cible ($y=1$ si le client part), et rendons $x$ manquante **plus souvent quand le client part** : un mécanisme MNAR, comme un client qui a demandé à résilier et que l'on n'a plus mesuré.


```text
                     traitement   AUC
imputation par la moyenne seule 0.610
 moyenne + indicateur d'absence 0.819
```

Dans cette simulation, la valeur est manquante pour 53,5 % des départs contre 9,4 % des autres. Quand l'absence est informative, l'imputation seule jette cette information : l'AUC reste modeste (0,610). Avec l'indicateur, le modèle apprend que « absent » veut dire « probablement parti », et l'AUC grimpe à 0,819. D'où une règle simple : **ajoutez systématiquement un indicateur d'absence pour les variables dont on soupçonne que l'absence est informative**, et laissez le modèle juger.

> ⚠️ **Imputer avant de séparer, c'est une fuite.** La moyenne, la médiane ou les voisins utilisés pour remplir les trous doivent être calculés sur le jeu d'entraînement et **appliqués ensuite** au test. Imputer tout le tableau avant la séparation fait entrer de l'information du test dans l'entraînement. La fuite est faible pour une moyenne sur 12 000 lignes ; elle devient sérieuse avec de petits échantillons ou des imputations par modèle.

> ✅ **À retenir (valeurs manquantes).** Comprenez d'abord *pourquoi* c'est manquant (structurel, aléatoire, informatif). Supprimer des lignes est le dernier recours. Imputez par la médiane, **ajoutez un indicateur** quand l'absence peut signifier quelque chose, ou laissez un boosting gérer le manque. Et imputez **à l'intérieur** de la validation croisée.

### 4.1.6 Tout assembler, sans fuite : `Pipeline` et `ColumnTransformer`

Nous avons rencontré quatre opérations qui **apprennent quelque chose des données** : l'encodage par la cible (des moyennes), la standardisation (une moyenne et un écart-type), l'imputation (une médiane), la transformation de puissance (un $\lambda$). Pour chacune, la règle est la même : l'apprendre sur le jeu d'entraînement (ou, dans une validation croisée, sur les plis d'entraînement uniquement), puis l'appliquer au reste.

Faire cela à la main, pli après pli, est source d'oublis. Les bibliothèques fournissent des objets qui l'**imposent** :

- un **`Pipeline`** enchaîne des étapes (prétraitement, puis modèle) et se comporte comme un seul modèle : `fit` apprend toutes les étapes sur les données qu'on lui donne, `predict` les applique ;
- un **`ColumnTransformer`** applique des traitements différents à des groupes de colonnes (numériques d'un côté, qualitatives de l'autre).

Passé à `cross_val_score`, un pipeline refait **à chaque pli** l'apprentissage complet du prétraitement sur les plis d'entraînement : il n'y a plus de fuite possible, même par maladresse.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

numeriques = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
categories = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))
prep = ColumnTransformer([("num", numeriques, NUM),
                          ("cat", categories, ["ville", "canal_acquisition", "appareil", "categorie_preferee"])])
modele = make_pipeline(prep, LogisticRegression(max_iter=3000))
scores = cross_val_score(modele, clients.loc[tr], ytr, cv=5, scoring="roc_auc")
print(f"AUC en validation croisée : {scores.mean():.3f} (± {scores.std():.3f})")
```
<!--sortie-->
```text
AUC en validation croisée : 0.860 (± 0.013)
```

Cet assemblage est le **modèle complet** : les quatorze variables numériques sont imputées (avec indicateurs) puis standardisées, les quatre variables qualitatives sont imputées puis encodées en *one-hot* (`handle_unknown="ignore"` évite une erreur si une modalité n'a pas été vue à l'entraînement), puis la régression logistique est ajustée. La validation croisée porte sur le jeu d'entraînement (le jeu de test reste intouchable, chapitre 1, section 1.2) et donne une AUC de 0,860, avec un écart-type de 0,013 d'un pli à l'autre. Une fois ajusté sur tout l'entraînement, le pipeline obtient 0,866 sur le jeu de test, cohérent avec la validation croisée et un peu meilleur que la régression logistique sur les seules variables numériques (0,858), grâce aux quatre variables qualitatives.

> 💡 **Un seul objet à sauvegarder.** Une fois ajusté sur tout l'entraînement, le pipeline contient **tout** : prétraitement et modèle. Pour prédire sur de nouveaux clients, on lui donne la table brute. Impossible d'oublier une étape, ni d'appliquer à la production un prétraitement différent de celui de l'entraînement.


> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 (un pipeline complet pas à pas), 4.2 (l'encodage par la cible hors pli, écrit à la main) et 4.3 (comparer des stratégies pour les valeurs manquantes) ; exercices 4.1 à 4.5.


## 4.2 Création et sélection de variables

La section précédente apprenait à **présenter** les variables existantes. Celle-ci apprend à en **fabriquer** de nouvelles et à décider lesquelles garder. C'est souvent là que se joue l'essentiel de la performance : un modèle sait combiner des variables, mais il ne devine pas toujours les **notions** que vous, vous connaissez du métier (« un client qui ne revient plus », « une promotion qui attire des chasseurs d'affaires »).

### 4.2.1 Penser métier : des variables qui ont du sens

Une nouvelle variable est un **calcul sur les colonnes existantes** qui exprime une idée. Les familles les plus utiles sont les suivantes.

**Les ratios et les taux.** Un nombre brut est rarement comparable d'un client à l'autre : 3 retours, c'est beaucoup pour 4 commandes, très peu pour 40. Le **taux de retour** (retours divisés par commandes) et les **tickets d'assistance par commande** se comparent, eux. Une **fréquence mensuelle** (commandes divisées par l'ancienneté, plafonnée à 12 mois) corrige l'effet « client récent ».

**Les profils RFM.** En commerce, trois grandeurs résument un client : la **récence** (depuis combien de temps a-t-il commandé ?), la **fréquence** (combien de fois ?) et le **montant** (combien a-t-il dépensé ?). Nos données les contiennent déjà ; on les combine pour faire apparaître des profils (« gros mais endormi », « petit mais assidu »).

**Les indicateurs de situation.** Un 0/1 qui code un fait métier : *jamais commandé*, *inactif depuis plus de cinq mois*, *a contacté l'assistance au moins trois fois*. Ils rendent explicites des **seuils** que les modèles linéaires ne peuvent pas apprendre seuls.

**Les interactions.** Le produit ou la combinaison de deux variables : un client peu satisfait **et** inactif est bien plus à risque que la somme des deux risques. Un modèle linéaire ne voit que des effets *additifs* ; l'interaction doit lui être donnée.

**Les composantes temporelles.** Une date se décompose en jour de la semaine, mois, heure, délai écoulé depuis un événement. Une heure se pose un problème particulier, traité plus loin (4.2.4).

> 💡 **Où trouver des idées ?** (1) Interrogez les gens du métier : *qu'est-ce qui fait partir un client ?* (2) Regardez les erreurs du modèle de base : quels clients se trompe-t-il, qu'ont-ils en commun ? (3) Regardez les arbres : leurs premières questions suggèrent des seuils utiles (4.2.2). Une variable créée est une **hypothèse** ; elle se teste sur la validation.

### 4.2.2 Découvrir les seuils à partir des données

Dans quelle zone de récence le risque de départ s'envole-t-il ? Plutôt que de deviner, regardons le taux de départ observé **sur le jeu d'entraînement** (jamais sur le test : choisir un seuil en regardant le test serait une fuite), en croisant la récence et la satisfaction.


![Taux de départ (en %) selon la récence, séparé selon la satisfaction : le risque est modéré jusqu'à environ 160 jours, puis explose, surtout chez les clients peu satisfaits.](figures/ch04-seuils-recence.png)

Deux faits ressortent. Le risque de départ est **faible et presque plat** jusqu'à 120 jours de récence (de 5,9 % à 9,3 %), puis il **monte** : 12,9 % entre 121 et 160 jours, 28,4 % entre 161 et 200, 36,5 % au-delà. Et la montée est **beaucoup plus forte quand la satisfaction est basse** : entre 161 et 200 jours, le taux de départ atteint **67 %** chez les clients peu satisfaits (moins de 3,15) contre **15 %** chez les autres. Le même nombre de jours sans commander n'a pas la même signification pour un client content et pour un client mécontent. C'est une **interaction avec seuil**, exactement ce qu'un modèle linéaire ne peut pas représenter avec les variables brutes.

Pour trouver les seuils avec précision, on peut laisser un **arbre peu profond** les proposer. Ses premières questions sont, par construction, celles qui séparent le mieux les départs des autres.


```text
seuils proposés par l'arbre de profondeur 3 (entraînement uniquement) :
  recence_jours <= 160.5
  age <= 20.5
  satisfaction_moy <= 3.15
  age <= 28.5
```

L'arbre place en tête la **récence autour de 160 jours**, puis, dans la branche des clients inactifs, la **satisfaction autour de 3,15** ; il isole aussi un seuil de **part d'achats en promotion proche de 0,60** et un effet d'âge aux deux extrémités. Ces valeurs sont des **candidates** : on les transforme en variables et on mesure si elles aident.

### 4.2.3 Fabriquer, puis mesurer

Un indicateur de règle s'écrit en une ligne :

```python
inactif_et_mecontent = ((clients["recence_jours"] > 160) & (clients["satisfaction_moy"] < 3.15)).astype(int)
print("part des clients concernés :", round(inactif_et_mecontent.mean(), 3))
```
<!--sortie-->
```text
part des clients concernés : 0.062
```

Construisons un jeu de variables enrichi, en trois étages : des variables **génériques** (ratios, fréquences, log), puis des **indicateurs de règles** construits avec les seuils découverts à l'étape précédente.


```text
           mean         size      
retours   False  True  False True 
tickets3                          
False     0.139  0.098  7591  1099
True      0.303  0.615   284    26

                variables  nombre de colonnes  AUC logistique  AUC boosting
      14 variables brutes                  14           0.858         0.892
 + 6 variables génériques                  20           0.871         0.893
+ 3 indicateurs de règles                  23           0.900         0.900
```

La troisième règle vient d'un tableau croisé calculé sur l'entraînement : parmi les 26 clients qui cumulent au moins trois tickets d'assistance et plus de 20 % de retours, **61,5 %** partent, contre 13,9 % des clients qui n'ont ni l'un ni l'autre (et 30,3 % de ceux qui n'ont que les tickets). Le groupe est petit, mais l'écart est net.

Le tableau est riche d'enseignements.

- Les **variables génériques** font gagner à la régression logistique 0,013 point d'AUC (de 0,858 à 0,871) et ne changent presque rien au boosting (0,892 puis 0,893).
- Les **indicateurs de règles**, eux, font passer la régression logistique à **0,900** : un gain de 0,042 point par rapport aux variables brutes, soit **autant que le boosting** (0,900), alors que la régression logistique reste un modèle simple, rapide et interprétable. Le boosting, qui découvrait déjà seul ces seuils et ces interactions, gagne peu (0,008), moins que l'incertitude d'une AUC sur 3 000 clients (environ 0,011, section 4.1).

> 💡 **Ingénierie des variables et choix du modèle sont deux manières d'obtenir la même chose.** Un modèle flexible (arbres, boosting) apprend lui-même seuils et interactions ; un modèle simple a besoin qu'on les lui **donne**. Quand les deux atteignent le même niveau, le modèle simple l'emporte souvent par sa lisibilité. À l'inverse, ne vous attendez pas à ce que les mêmes variables aident un boosting.

> ⚠️ **Des seuils découverts sur l'entraînement, évalués sur le test.** Les seuils (160 jours, 3,15, 0,60, ainsi que « au moins 3 tickets et plus de 20 % de retours ») ont été lus sur le jeu d'entraînement. Si nous les avions choisis en regardant le jeu de test, le gain affiché aurait été gonflé : c'est la forme discrète de la fuite d'information. Les règles du métier connues d'avance ne posent pas ce problème ; celles trouvées dans les données, si.

### 4.2.4 Les variables cycliques : l'exemple de l'heure

Une commande passée à 23 h et une autre à 1 h sont **proches** dans la journée, mais leurs valeurs (23 et 1) sont **éloignées** sur l'axe des nombres. Pour un modèle linéaire ou une distance, l'heure comme entier est trompeuse : le « bout » de la journée est collé à son « début ». La solution est de placer l'heure sur un **cercle**, en la remplaçant par deux coordonnées :

$$\text{heure}\ \mapsto\ \Bigl(\sin\frac{2\pi\,h}{24},\ \cos\frac{2\pi\,h}{24}\Bigr).$$

Minuit et 23 h deviennent deux points voisins du cercle, tandis que minuit et midi en sont deux points opposés. La même idée s'applique au jour de la semaine (période 7) et au mois (période 12).

Voyons son effet sur les fraudes de `transactions.csv`, qui se concentrent la nuit.


```text
               codage de l'heure   AUC  précision moyenne (PR-AUC)
     heure comme entier (0 à 23) 0.920                       0.254
       heure en sinus et cosinus 0.928                       0.262
indicateur « nuit » (23 h à 4 h) 0.935                       0.284
```

Sur le jeu d'entraînement, 4,1 % des commandes passées entre 23 h et 4 h sont frauduleuses, contre 0,6 % le reste du temps : la concentration nocturne se lit directement dans les taux par heure. Le codage de l'heure compte, mais **modestement** : l'AUC passe de 0,920 (heure comme entier) à 0,928 (sinus et cosinus) puis 0,935 (indicateur « nuit »), et la précision moyenne de 0,254 à 0,262 puis 0,284. Les écarts sont cohérents avec la théorie, mais sur 146 fraudes de test ils restent fragiles (4.3.6). L'indicateur est le plus économe et le plus parlant, **à condition de connaître la zone utile** (ici, lue sur l'entraînement) ; le couple sinus/cosinus est le choix général quand on ne sait pas d'avance où elle se trouve.

### 4.2.5 Agréger : passer de plusieurs lignes à une ligne par client

Beaucoup de jeux de données contiennent **plusieurs lignes par entité** : toutes les commandes d'un client, tous les passages d'une machine. Le modèle attend **une ligne par client**. On **agrège** alors, avec des fonctions qui résument chaque entité : le nombre de commandes, le montant total, moyen, maximal, l'écart-type, la date de la dernière commande, la part de commandes en promotion… Les variables `nb_commandes_12m`, `montant_12m`, `panier_moyen` et `recence_jours` de notre fichier de clients sont précisément des agrégats d'un historique de commandes.

Un exemple à la main : un client a passé quatre commandes de 30, 45, 45 et 120 €, la dernière il y a 12 jours. Ses variables agrégées sont : nombre $=4$, total $=240$, moyenne $=60$, maximum $=120$, médiane $=45$, récence $=12$ jours. Chaque agrégat est une **hypothèse sur ce qui compte** : la moyenne cache un gros achat isolé, le maximum le révèle.

> ⚠️ **Agréger dans le temps, c'est choisir une date.** Les agrégats d'un client ne doivent utiliser que les commandes **antérieures à la date de prédiction**. Inclure une commande postérieure à la date de référence est une fuite d'information, la plus fréquente en pratique (voir plus bas).

### 4.2.6 Redondance, variance nulle et fuite

Avant de nourrir le modèle, trois contrôles de bon sens.

**Les variables quasi constantes** n'apportent rien (une colonne dont 99,9 % des valeurs sont égales). On les écarte sans regret.

**Les variables redondantes** portent la même information : `montant_12m` vaut approximativement le nombre de commandes multiplié par le panier moyen, et la part d'achats en promotion est liée au nombre de promotions reçues. Elles n'abîment pas un arbre, mais rendent les coefficients d'un modèle linéaire instables (volume II, section 1.3, multicolinéarité).


```text
nb_commandes_12m      montant_12m          0.74
nb_promos_recues_12m  part_achats_promo    0.67
montant_12m           panier_moyen         0.50
nb_commandes_12m      nb_retours_12m       0.49
```

**La fuite d'information** est le contrôle le plus important. Notre fichier contient volontairement une variable piège, `commandes_apres_cible`, qui compte les commandes des **trois mois suivants**. Elle appartient au futur : on ne la connaît pas au moment de prédire. Comment la repérer ?


```text
             variable  AUC seule
          montant_12m      0.780
commandes_apres_cible      0.760
     nb_commandes_12m      0.752
        recence_jours      0.740
                  age      0.717
```

La première idée est de regarder la **qualité de chaque variable prise seule** (AUC univariée). Elle échoue ici : la variable de fuite atteint 0,760, **moins** que le montant des 12 derniers mois (0,780), et elle n'est même pas la plus prédictive des variables « normales ». Cette fuite est **insidieuse** parce qu'elle est bruitée : un nombre de commandes futures est aléatoire, et seuls les clients qui ne reviendront plus ont systématiquement zéro. En revanche, elle **ajoute** de l'information que les autres variables n'ont pas : avec elle, le boosting passe de 0,892 à 0,928, un gain de 0,036 point que l'on ne sait expliquer par aucune idée du métier.

Aucun test automatique ne remplace donc la **question de bon sens** à poser pour chaque variable : *à quelle date cette valeur est-elle connue, par rapport à la date où je veux prédire ?* Pour `commandes_apres_cible`, la réponse est « trois mois **après** », la variable est exclue. Les autres signaux d'alerte sont un gain « trop beau » après l'ajout d'une seule variable, une importance démesurée d'une variable dont le nom évoque un **résultat** (« après », « résiliation », « solde final »), et une performance qui **s'effondre** en production (chapitre 1, section 1.1). Une variable qui rend le modèle bien meilleur que ce que le métier permet d'espérer est suspecte avant d'être précieuse.

> ✅ **À retenir (création et sélection).** Fabriquez des variables qui expriment des idées métier (ratios, taux, indicateurs de situation, interactions) ; trouvez les seuils sur l'entraînement ; donnez à un modèle simple ce qu'un modèle flexible découvre seul. Codez les variables cycliques sur un cercle. Écartez variables constantes et redondantes, et **traquez la fuite** : une variable trop belle est suspecte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4 (créer des variables RFM et mesurer leur apport), exercices 4.6 à 4.8.


## 4.3 Classes déséquilibrées : pondération et rééchantillonnage

Une commande frauduleuse sur 120, un client qui part sur sept, une panne de machine sur mille : les événements qui nous intéressent le plus sont presque toujours **rares**. Les modèles, eux, sont construits pour minimiser une erreur **moyenne** sur les données : quand 99 % des lignes appartiennent à une classe, ils apprennent surtout à bien traiter celle-là. Cette section explique pourquoi la métrique habituelle (l'exactitude) devient trompeuse, ce que font réellement les remèdes (poids, rééchantillonnage), et pourquoi le **seuil de décision** est souvent le levier le plus puissant et le plus négligé.

### 4.3.1 Pourquoi l'exactitude trompe

Notre fichier `transactions.csv` contient 60 000 commandes en ligne, dont 0,8 % de fraudes. Après le découpage habituel (70 % pour l'entraînement, 30 % pour le test, stratifié), le jeu de test compte 18 000 commandes dont 146 frauduleuses.

Considérons le **modèle le plus paresseux possible** : il répond « pas de fraude » pour toutes les commandes. Il se trompe sur les 146 fraudes et n'a raison que sur les autres, soit une **exactitude** (part de réponses justes) de $\frac{17\,854}{18\,000}\approx99{,}19\ \%$. Un score qui paraît excellent, pour un modèle qui ne détecte **aucune** fraude.


La table de confusion rend l'illusion visible. Elle croise la réalité (en lignes) et la décision du modèle (en colonnes) :

| | décision « pas de fraude » | décision « fraude » |
|---|---|---|
| **réellement pas de fraude** | vrais négatifs (VN) : 17 854 | faux positifs (FP) : 0 |
| **réellement fraude** | **faux négatifs (FN) : 146** | vrais positifs (VP) : 0 |

Deux mesures décrivent mieux ce qui compte quand la classe rare est celle qui nous intéresse (elles sont détaillées en 5.1).

$$\text{précision}=\frac{\text{VP}}{\text{VP}+\text{FP}}\quad(\text{parmi les alertes, quelle part est juste ?}),\qquad \text{rappel}=\frac{\text{VP}}{\text{VP}+\text{FN}}\quad(\text{parmi les fraudes, quelle part est détectée ?}).$$

Le modèle paresseux a un rappel de **0 %** ; l'exactitude de 99,19 % n'en dit rien. D'où une règle absolue : **avec des classes déséquilibrées, ne jamais juger sur l'exactitude.**

#### Même l'AUC peut rassurer à tort

Entraînons une régression logistique sur ces données et mesurons deux scores de classement. L'**AUC-ROC** (volume II, section 2.2) compare les taux de vrais et de faux positifs à tous les seuils. La **précision moyenne** (PR-AUC, aire sous la courbe précision-rappel) mesure plutôt la qualité du haut du classement, là où se trouvent les alertes.


L'AUC-ROC vaut 0,921 : le modèle classe très bien. Mais la PR-AUC n'est que de 0,260 (un classement au hasard donnerait 0,008), et à un seuil de 0,5 la régression logistique ne détecte que **10 % des fraudes** (rappel 0,103) : sur 146 fraudes, elle en trouve 15 et en laisse passer 131. L'AUC-ROC est **optimiste** quand la classe positive est rare : les 17 854 négatifs comptent tant dans les taux de faux positifs qu'une petite erreur sur eux paraît négligeable. La PR-AUC, qui ignore les vrais négatifs, est plus sévère et plus informative.

> ✅ **À retenir.** Exactitude : à proscrire. AUC-ROC : informative mais indulgente. **PR-AUC, précision et rappel** : les bons outils quand la classe rare est l'objet. (Détail et autres métriques : section 5.1.)

### 4.3.2 La pondération des classes

La première idée est de **dire au modèle que la classe rare compte davantage**. La perte d'une régression logistique est la perte logarithmique moyenne (volume II, section 2.2) :

$$L(\boldsymbol\beta)=-\frac1n\sum_{i=1}^n\Bigl[y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr].$$

On la **pondère** : une erreur sur un exemple de la classe 1 coûte $w$ fois plus qu'une erreur sur un exemple de la classe 0.

$$L_w(\boldsymbol\beta)=-\frac1n\sum_{i=1}^n\Bigl[w\,y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr].$$

C'est équivalent à **recopier $w$ fois** chaque exemple positif. L'option `class_weight="balanced"` choisit $w$ pour que les deux classes pèsent autant au total, c'est-à-dire $w=\frac{n_0}{n_1}$ (ici $w\approx122{,}5$). Dans scikit-learn, c'est un simple paramètre du modèle :

```python
from sklearn.linear_model import LogisticRegression

modele_pondere = LogisticRegression(class_weight="balanced", max_iter=3000)      # w = n0 / n1 pour la classe rare
# on peut aussi donner les poids à la main : class_weight={0: 1, 1: 20}
```

#### Ce que cela change exactement

Considérons le cas le plus simple, sans aucune variable explicative : une probabilité constante $p$ pour tous. Si la proportion de positifs est $\pi$, la perte pondérée moyenne vaut $-[\,w\pi\ln p+(1-\pi)\ln(1-p)\,]$. En la dérivant par rapport à $p$ et en annulant la dérivée,

$$\frac{w\pi}{p}-\frac{1-\pi}{1-p}=0\quad\Longrightarrow\quad\frac{p^\star}{1-p^\star}=w\,\frac{\pi}{1-\pi}.$$

La probabilité estimée a donc une **cote multipliée par $w$** : la pondération n'a pas rendu le modèle « plus malin », elle a **déplacé ses probabilités vers le haut**. Pour une régression logistique à plusieurs variables bien spécifiée, le même raisonnement dit que seul le terme constant change, de $\ln w$, et que les autres coefficients (donc le **classement** des clients) ne bougent pas. Vérifions.


```text
poids w = n0/n1 = 122.5 | ln w = 4.808 | décalage observé de la constante : 4.675
probabilité moyenne prédite : sans poids 0.008 | avec poids 0.2365 | fréquence réelle 0.0081
à 0,5 avec poids : précision 0.049, rappel 0.863 (FP 2432, FN 20)
probabilité moyenne après correction : 0.0098
```

Les constats confirment la théorie. Le poids vaut $w\approx122$, soit $\ln w\approx4{,}81$ ; la constante du modèle a bougé de $4{,}68$, très près de la valeur prévue. Les probabilités moyennes passent de 0,8 % (la vraie fréquence) à **23,7 %** : elles sont **fausses**, gonflées, comme le prédit le calcul. Si on les corrige en divisant la cote par $w$ ($p=\frac{p_w}{p_w+(1-p_w)\,w}$), la moyenne retombe à 1,0 %, bien plus près de la fréquence réelle (0,8 %) ; l'écart restant vient du fait que le modèle n'est pas parfaitement spécifié. L'AUC-ROC reste pratiquement celle du modèle sans poids (0,921 contre 0,923) et la corrélation de rang entre les deux scores vaut 0,985 : **le classement n'a presque pas changé**.

Alors, à quoi sert la pondération ? À **déplacer le seuil implicite**. Avec un seuil de 0,5, le modèle pondéré déclare « fraude » dès que la probabilité *gonflée* dépasse 0,5, ce qui correspond à une probabilité réelle bien plus basse. Le rappel passe de 0,103 à **0,863** : sur 146 fraudes, il en trouve 126. Mais la précision s'effondre à 0,049 : il déclenche 2 432 fausses alertes, contre 9 auparavant. On a gagné 111 détections supplémentaires (de 15 à 126), au prix d'environ 2 400 vérifications inutiles de plus. Est-ce un bon marché ? **Cela dépend uniquement des coûts** (4.3.5).

> ⚠️ **Avec des poids, les probabilités ne sont plus des probabilités.** Si vous avez besoin de probabilités fiables (chiffrer un risque, calculer une espérance de gain), **corrigez-les** comme ci-dessus ou recalibrez-les (section 5.2). Si vous ne vous servez que du classement, la pondération est sans conséquence.

Pour les modèles à base d'arbres, le mécanisme est un peu différent : les poids modifient l'importance de chaque exemple dans le calcul des impuretés et des gradients (chapitre 2), de sorte que les **modèles eux-mêmes** diffèrent, pas seulement leurs probabilités. Sur nos données, le boosting sans correction obtient une PR-AUC de 0,625 et le boosting pondéré de 0,643 : une différence trop faible, avec 146 fraudes de test, pour être distinguée du hasard (4.3.6).

### 4.3.3 Le rééchantillonnage aléatoire

La seconde famille de remèdes agit sur les **données** : on rééquilibre l'échantillon d'entraînement avant d'apprendre.

- Le **sous-échantillonnage** (*undersampling*) retire au hasard des exemples de la classe majoritaire. On garde par exemple 5 non-fraudes pour 1 fraude. Rapide, mais on **jette des données** : ici, plus de 95 % des commandes normales.
- Le **sur-échantillonnage** (*oversampling*) recopie au hasard des exemples de la classe minoritaire jusqu'à égalité. On ne perd rien, mais on duplique : le modèle voit la même fraude des dizaines de fois et peut la **mémoriser**.

Un exemple à la main : 1 000 commandes dont 10 fraudes. Sous-échantillonner à 5 contre 1 garde les 10 fraudes et 50 commandes normales tirées au hasard, soit 60 lignes ; sur-échantillonner à l'égalité garde les 990 commandes normales et recopie chacune des 10 fraudes 99 fois, soit 1 980 lignes.


```text
                   traitement  AUC-ROC  PR-AUC  précision à 0,5  rappel à 0,5
                        aucun    0.921   0.260            0.625         0.103
             poids équilibrés    0.923   0.187            0.049         0.863
     sous-échantillonnage 5:1    0.921   0.220            0.119         0.534
sur-échantillonnage aléatoire    0.923   0.187            0.049         0.863
```

Le sur-échantillonnage aléatoire donne **exactement** les mêmes résultats que les poids équilibrés (même AUC, même précision, même rappel) : recopier chaque fraude $w$ fois et la pondérer par $w$ sont, pour une régression logistique, une seule et même opération. Le sous-échantillonnage place le compromis ailleurs (précision 0,119, rappel 0,534) : on a rééquilibré à 5 contre 1, et non à 1 contre 1, donc le décalage des probabilités est moindre. Aucune des trois stratégies n'améliore l'AUC-ROC (0,921 à 0,923) : elles **déplacent le point de fonctionnement**, elles ne rendent pas le modèle meilleur.

> ⚠️ **Rééchantillonner avant de séparer est une fuite d'information.** Si l'on sur-échantillonne la table complète **puis** qu'on la sépare en entraînement et validation (ou qu'on lance une validation croisée), les copies d'une même fraude se retrouvent des deux côtés : le modèle est « testé » sur des exemples qu'il a déjà vus. Le score devient absurde. Nous le mesurons en 4.5. La règle : le rééchantillonnage ne s'applique qu'aux **plis d'entraînement**, dans le pipeline.

### 4.3.4 Le seuil de décision : le levier oublié

Un modèle de classification produit une **probabilité** ; la **décision** (« fraude » ou non) vient d'un **seuil** : on déclare « fraude » si la probabilité dépasse $s$. Le seuil de 0,5 n'a aucune raison d'être le bon : il n'est optimal que si les deux erreurs coûtent autant et si les probabilités sont fidèles. Faire varier $s$ déplace le modèle le long de sa **courbe précision-rappel** : un seuil bas détecte plus de fraudes (rappel haut) mais déclenche plus de fausses alertes (précision basse), un seuil haut fait l'inverse.


![Courbes précision-rappel de trois modèles sur les 18 000 commandes de test : le boosting domine nettement la régression logistique, et la pondération déplace peu la courbe elle-même.](figures/ch04-precision-rappel.png)

La figure dit l'essentiel. Le boosting domine la régression logistique sur **toute** la plage (par exemple, à rappel de 0,5, il garde une précision bien supérieure). Et pondérer ou non le boosting ne change presque pas la courbe : les deux courbes se superposent à peu près. **Une courbe précision-rappel est la carte de tous les compromis possibles ; choisir un seuil, c'est choisir un point sur cette carte.**

Où se placer ? Pas en regardant le jeu de test (le choisir sur le test, c'est de nouveau une fuite) : on choisit le seuil sur des **prédictions hors pli** du jeu d'entraînement, obtenues par validation croisée, puis on l'applique au test.


Avec le boosting, le seuil qui maximise le F1 sur les prédictions hors pli est à $s=0{,}42$ ; sur le test, il donne un F1 de 0,598 (précision 0,678, rappel 0,534), contre 0,601 au seuil de 0,5 (précision 0,710, rappel 0,521). **Aucune différence** : le F1 donne le même poids aux deux erreurs et les probabilités du boosting sont bien calibrées, le seuil de 0,5 était déjà presque optimal pour ce critère. Optimiser un seuil n'est utile que **pour un critère qui correspond à l'usage réel** ; le F1 est rarement ce critère. La section suivante part des coûts.

### 4.3.5 La vue par les coûts

Le meilleur seuil n'est pas celui qui maximise une métrique abstraite, c'est celui qui **minimise ce que coûtent les erreurs**. Supposons qu'une fraude non détectée coûte en moyenne $c_{FN}=100$ € (marchandise perdue), et qu'une fausse alerte coûte $c_{FP}=5$ € (vérification manuelle). Pour une commande dont la **vraie** probabilité de fraude est $p$ :

- si on la laisse passer, le coût espéré est $p\times c_{FN}$ ;
- si on la bloque pour vérification, le coût espéré est $(1-p)\times c_{FP}$.

On bloque quand le second est plus petit que le premier :

$$p\,c_{FN}>(1-p)\,c_{FP}\quad\Longleftrightarrow\quad p>\frac{c_{FP}}{c_{FP}+c_{FN}}.$$

Le **seuil optimal** ne dépend que du rapport des coûts : $s^\star=\frac{5}{105}\approx0{,}048$ ici. Une fraude coûte vingt fois plus qu'une fausse alerte, il faut donc bloquer dès que la probabilité dépasse 4,8 %. Cette formule suppose que les probabilités sont **calibrées** : celles du boosting non pondéré le sont à peu près, pas celles d'un modèle pondéré (4.3.2).


```text
                        règle de décision  coût total sur le test (€)
                       seuil 0,5 (défaut)                        7155
                    seuil théorique 0.048                        5575
seuil minimisant le coût hors pli (0.025)                        5420
         aucune alerte (modèle paresseux)                       14600
boosting pondéré, seuil 0,5 : coût 4595 € ; au seuil équivalent corrigé 0.86 : 5365 €
coût du boosting pondéré à 0,5 moins coût du boosting au seuil théorique : moyenne -1031 €, intervalle à 95 % [-2198 ; -37]
```

![Coût total des erreurs de décision sur les 18 000 commandes de test en fonction du seuil, pour le boosting : le coût est minimal pour des seuils bas, bien en dessous de 0,5.](figures/ch04-cout-seuil.png)

En code, appliquer un seuil est une simple comparaison de la probabilité prédite :

```python
proba = gb.predict_proba(Xb)[:, 1]            # probabilité de fraude de chaque commande de test
alerte = proba >= 0.048                       # on bloque dès que la probabilité dépasse le seuil
print(alerte.sum(), "commandes bloquées sur", len(alerte))
```
<!--sortie-->
```text
231 commandes bloquées sur 18000
```

Le tableau et la figure disent trois choses. (1) Le seuil par défaut de 0,5 est **le plus coûteux** des seuils raisonnables : 7 155 €. (2) Le seuil théorique de 0,048 réduit le coût de 22 % (5 575 €), et le seuil qui minimise le coût sur les prédictions hors pli (0,025) donne un résultat voisin (5 420 €) : sur 146 fraudes, la formule suffit, sans chercher le seuil exact. (3) Ne rien bloquer coûterait 14 600 €.

Le boosting **pondéré**, à son seuil par défaut de 0,5, coûte 4 595 € : moins que toutes les lignes précédentes. Il ne faut pas y voir un miracle de la pondération. Les poids ont modifié les **arbres eux-mêmes**, pas seulement les probabilités (4.3.2). Et l'avantage, de 1 031 € en moyenne, est mesuré avec une grande marge (intervalle à 95 % par *bootstrap* du test : de −2 198 à −37 €) : il exclut de peu zéro, mais le *bootstrap* ne rééchantillonne que le test et **ignore la variabilité due à l'entraînement**. Avec 146 fraudes, retenez surtout le constat solide : **le seuil par défaut est mauvais** dès que les erreurs n'ont pas le même coût.

> 💡 **Le rôle des poids, revisité.** Pondérer les classes, rééchantillonner et déplacer le seuil sont **trois façons d'obtenir le même effet** : changer le compromis entre faux négatifs et faux positifs. Si vous connaissez vos coûts, le plus propre est de **laisser le modèle apprendre des probabilités fidèles, puis de choisir le seuil par les coûts**. Poids et rééchantillonnage sont des commodités quand l'algorithme apprend mal avec de rares positifs, pas des objectifs en soi.

### 4.3.6 Comparer honnêtement : et le déséquilibre modéré ?

Avec 146 fraudes de test, toute comparaison de deux stratégies est entachée d'une **forte incertitude**. Mesurons-la par un *bootstrap* du jeu de test (volume I, section 3.3.5) : on rééchantillonne 500 fois les 18 000 commandes de test, et on observe la dispersion de la PR-AUC.


```text
boosting           moyenne 0.623  intervalle à 95 % [0.543 ; 0.701]
boosting pondéré   moyenne 0.642  intervalle à 95 % [0.561 ; 0.716]
écart              moyenne 0.020  intervalle à 95 % [-0.028 ; 0.072]
```

Les intervalles de la PR-AUC du boosting et du boosting pondéré se **recouvrent largement** : l'intervalle de leur écart contient zéro. Nous n'avons **aucune preuve** que la pondération améliore le classement du boosting ; seule l'écart de seuil de décision, lui, est réel.

Reste le cas du **déséquilibre modéré**, celui du départ des clients (14 %). Les mêmes stratégies y changent-elles quelque chose ?


```text
          modèle  AUC-ROC  PR-AUC  précision à 0,5  rappel à 0,5
        boosting    0.899   0.655            0.689         0.458
boosting pondéré    0.899   0.663            0.504         0.717
```

À 14 % de positifs, les deux modèles ont presque le même classement (AUC-ROC et PR-AUC proches) ; la pondération déplace surtout le compromis précision-rappel à 0,5, comme avant. **Un déséquilibre de cet ordre n'appelle pas de traitement spécial** : un bon modèle, des probabilités fiables, et un seuil choisi selon l'usage (par exemple, contacter les 10 % de clients les plus à risque, que la capacité du service client permet). Les précautions de cette section prennent toute leur valeur quand la classe rare passe sous quelques pour cent.

> ✅ **À retenir (classes déséquilibrées).** (1) Jugez avec précision, rappel et PR-AUC, jamais avec l'exactitude. (2) Les poids de classes et le rééchantillonnage **déplacent les probabilités et le seuil implicite** ; ils n'améliorent pas, en général, le classement. (3) Le **seuil de décision** se choisit par les coûts, sur des prédictions hors pli, jamais sur le test. (4) Rééchantillonner uniquement à l'intérieur des plis d'entraînement. (5) Avec peu de positifs de test, **chiffrez l'incertitude** de vos comparaisons.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (comparer toutes les stratégies sur les fraudes) et application 4.6 (choisir un seuil par les coûts) ; exercices 4.9 à 4.11.


## 4.4 ➕ Pour aller plus loin : les méthodes de sélection de variables

> 🧭 **Section optionnelle.** Elle approfondit la sélection de variables vue en 4.2 : les trois grandes familles de méthodes, et surtout le piège qui rend la plupart des sélections trop optimistes. On peut la sauter à la première lecture.

Quand un jeu de données compte des dizaines ou des milliers de variables, on veut en garder **un sous-ensemble utile** : pour des modèles plus rapides, plus lisibles, moins sujets au surapprentissage. Les méthodes se classent selon **le moment** où elles interviennent par rapport au modèle.

### 4.4.1 Trois familles de méthodes

**Les méthodes de filtre** jugent chaque variable **avant** le modèle, par une statistique indépendante de lui. Elles sont rapides et simples, mais regardent les variables **une par une**, donc ignorent les interactions.

**Les méthodes d'enveloppe** (*wrapper*) **essaient** des sous-ensembles en entraînant le modèle et en mesurant sa performance. Elles tiennent compte des interactions et du modèle choisi, mais coûtent cher : chaque essai est un apprentissage complet.

**Les méthodes intégrées** (*embedded*) sélectionnent **pendant** l'apprentissage : une pénalité $\ell_1$ qui met des coefficients à zéro, ou les importances qu'un arbre calcule en se construisant. Elles sont le meilleur compromis coût-qualité, avec leurs propres biais.

### 4.4.2 Les filtres : information mutuelle et $\chi^2$

Le filtre le plus général est l'**information mutuelle**. Pour une variable $X$ et la cible $Y$, elle mesure combien connaître $X$ réduit l'incertitude sur $Y$ :

$$I(X;Y)=\sum_{x,y}p(x,y)\ln\frac{p(x,y)}{p(x)\,p(y)}.$$

Elle vaut zéro si et seulement si $X$ et $Y$ sont **indépendantes**, et elle capte toute dépendance, pas seulement linéaire. Contrairement à une corrélation, elle voit une relation en U ou à seuil. Pour deux variables **qualitatives**, le test du $\chi^2$ d'indépendance (volume I, section 3.4.6) joue un rôle analogue : on garde les variables dont le lien avec la cible est le plus significatif.

Un exemple à la main, avec deux variables binaires et 100 clients dont 20 partent. Si 50 clients ont reçu une promotion et que 10 d'entre eux partent (autant que dans l'autre moitié), la promotion n'apporte aucune information sur le départ : $I=0$. Si au contraire 18 des 20 partants viennent du groupe « sans promotion », alors savoir qu'un client a eu la promotion change beaucoup la probabilité qu'il parte : $I>0$.

### 4.4.3 Les enveloppes : RFE et sélection progressive

La **suppression récursive de variables** (*recursive feature elimination*, RFE) entraîne le modèle avec toutes les variables, élimine la moins importante (par exemple celle au plus petit coefficient en valeur absolue), et recommence jusqu'à ce qu'il reste le nombre voulu. La **sélection progressive** (*forward selection*) fait l'inverse : on part de zéro variable et on ajoute à chaque étape celle qui améliore le plus le score en validation croisée.

Pour $p$ variables, la sélection progressive jusqu'à $k$ variables nécessite environ $p+(p-1)+\dots$ essais, c'est-à-dire de l'ordre de $kp$ validations croisées : raisonnable pour 14 variables, prohibitif pour 5 000.

### 4.4.4 Les méthodes intégrées : $\ell_1$, importances d'arbre, permutation

La **pénalité $\ell_1$** (Lasso, volume II, section 1.5) met à zéro les coefficients des variables peu utiles : la sélection est un effet secondaire de l'apprentissage. Elle suppose des variables **standardisées** (4.1.3).

L'**importance par impureté** d'une forêt ou d'un arbre additionne, pour chaque variable, la réduction d'impureté obtenue à tous les nœuds où elle est utilisée. Elle est gratuite, mais **biaisée** : une variable continue ou à beaucoup de modalités offre plus de seuils possibles, donc plus d'occasions de réduire l'impureté **par hasard**, même si elle est du pur bruit.

L'**importance par permutation** corrige ce défaut. On entraîne le modèle, puis on mesure la baisse de performance sur un jeu de **validation** quand on **mélange au hasard** les valeurs d'une seule variable (ce qui détruit son lien avec la cible en préservant sa distribution). Plus la baisse est grande, plus la variable compte ; une variable de bruit entraîne une baisse nulle.

#### Que choisissent-elles sur nos clients ?

Nous ajoutons aux 14 variables numériques **cinq variables de bruit pur** (tirées au hasard, sans lien avec la cible : trois continues et deux discrètes), et nous comparons les méthodes. Toutes les sélections sont calculées sur le jeu d'entraînement ; l'importance par permutation utilise une partie de l'entraînement mise de côté comme validation.


```text
                                      méthode  variables retenues  dont bruit  AUC test (logistique)
toutes les variables (14 vraies + 5 de bruit)                  19           5                  0.857
                         information mutuelle                   8           0                  0.855
                                          RFE                   8           0                  0.857
                        sélection progressive                   8           0                  0.858
                                  pénalité L1                  14           3                  0.858
                          permutation (forêt)                   8           1                  0.858

importance par impureté (forêt), variables de bruit : {'bruit_continu_1': 0.038, 'bruit_continu_2': 0.0382, 'bruit_continu_3': 0.0359, 'bruit_discret_1': 0.021, 'bruit_discret_2': 0.0241}
importance par impureté, médiane des 14 vraies variables : 0.0435
importance par permutation, variables de bruit : {'bruit_continu_1': 0.0003, 'bruit_continu_2': -0.0008, 'bruit_continu_3': 0.001, 'bruit_discret_1': -0.0002, 'bruit_discret_2': -0.0}
```

Trois méthodes (information mutuelle, RFE, sélection progressive) retiennent chacune 8 variables parmi 19 et **aucune des cinq variables de bruit**. La pénalité $\ell_1$ (avec $C=0{,}05$) en garde 14, dont **trois variables de bruit** : à ce niveau de pénalité, elle laisse de petits coefficients non nuls ; son résultat dépend du paramètre $C$, à régler par validation croisée (chapitre 1, 1.5). La sélection par permutation d'une forêt laisse passer une variable de bruit (`bruit_continu_3`) dans ses huit premières.

Côté performance, **aucune sélection n'améliore l'AUC** : de 0,855 à 0,858 pour tous les sous-ensembles, contre 0,857 avec les 19 variables. Ici la sélection ne sert donc pas la performance mais la **simplicité** : un modèle à huit variables est aussi bon qu'un modèle à dix-neuf, et plus facile à expliquer et à maintenir.

Le contraste est plus net sur les **importances**. Dans la forêt, les trois variables de bruit **continues** obtiennent une importance par impureté de 0,036 à 0,038, presque celle de la variable réelle médiane (0,0435) ; l'importance par permutation les ramène à 0,000 ± 0,001, alors qu'elle donne 0,046 à la récence.

> ⚠️ **L'importance par impureté peut récompenser du bruit.** Les trois variables de bruit **continues** obtiennent une importance par impureté de 0,036 à 0,038, parce qu'elles offrent de nombreux seuils à tester (et les deux variables de bruit discrètes, à douze modalités, de 0,021 à 0,024) ; l'importance par permutation, mesurée sur un jeu de validation, les ramène près de zéro. Pour décider quelles variables garder, préférez la permutation (section 5.3).

### 4.4.5 Le piège : sélectionner avant de valider

Voici l'erreur la plus répandue de toute la sélection de variables. On dispose de beaucoup de variables et de peu de clients ; on commence par **choisir les variables les plus liées à la cible sur tout le jeu de données**, puis on **évalue** le modèle sur ces variables par validation croisée. Le résultat semble excellent. Il est faux.

Pour le voir, prenons le cas extrême : 150 clients, 500 variables **entièrement aléatoires**, et une cible **tirée à pile ou face**, donc sans aucun lien avec les variables. Aucun modèle ne peut faire mieux que le hasard (AUC de 0,5). On répète l'expérience de deux manières, sur 40 jeux de données différents.

- **Sélection avant la validation croisée (fautive)** : on garde les 20 variables les mieux classées sur les 150 clients, puis on valide par validation croisée sur ces 20 colonnes.
- **Sélection dans la validation croisée (correcte)** : la sélection fait partie du `Pipeline`, donc elle est refaite à chaque pli sur les plis d'entraînement seulement.


```text
sélection AVANT la validation croisée : AUC moyenne 0.831 (min 0.762, max 0.909)
sélection DANS la validation croisée  : AUC moyenne 0.510 (min 0.351, max 0.663)
```

![Distribution de l'AUC en validation croisée sur 40 jeux simulés où la cible est du pur hasard : la sélection de variables faite avant la validation donne une AUC trompeusement élevée, celle faite dans la validation reste autour de 0,5.](figures/ch04-biais-selection.png)

Le contraste est total. En sélectionnant d'abord, **tous** les jeux simulés donnent une AUC bien supérieure à 0,5 (de 0,76 à 0,91, moyenne 0,83) pour des données sans aucune information ; en sélectionnant à l'intérieur de la validation, on retrouve honnêtement le hasard (moyenne 0,51, de 0,35 à 0,66 selon les jeux, ce qui rappelle aussi qu'une seule AUC sur 150 clients est très bruitée). Pourquoi ? Parmi 500 variables aléatoires, on en trouve toujours 20 qui, **par chance**, ressemblent à la cible sur ces 150 clients ; la sélection les a choisies *en regardant les étiquettes de tous les clients, y compris ceux des plis de validation*. Le pli de validation n'est plus vierge : l'information sur ses étiquettes a servi à choisir les colonnes.

> ⚠️ **Règle absolue.** Toute opération qui **regarde la cible** (sélection de variables, choix de seuils, encodage par la cible, réglage) doit être **dans** le pipeline validé, refaite pli par pli. Et une fois le modèle final choisi, le jeu de test ne doit servir qu'**une** fois, à la fin.

> ✅ **À retenir (sélection).** Filtre : rapide, aveugle aux interactions. Enveloppe : fidèle au modèle, mais coûteuse. Intégrée : bon compromis. Préférez l'**importance par permutation** à l'importance par impureté. Et mettez la sélection **dans le pipeline** : sinon la validation croisée est faussée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (comparer filtre, enveloppe et méthodes intégrées, et refaire le piège de la sélection) ; exercices 4.12.


## 4.5 ➕ Pour aller plus loin : SMOTE et ses variantes

> 🧭 **Section optionnelle.** Elle présente la méthode de rééchantillonnage la plus connue pour les classes rares, et, surtout, montre sur nos données **quand elle ne sert à rien**. On peut la sauter à la première lecture.

Le sur-échantillonnage aléatoire (4.3.3) recopie les exemples rares. Son défaut est évident : il fabrique des **doublons exacts**, que le modèle peut apprendre par cœur. L'idée de **SMOTE** (*Synthetic Minority Over-sampling TEchnique*, Chawla et al., 2002) est de créer des exemples **nouveaux mais plausibles**, en **interpolant** entre exemples rares voisins.

### 4.5.1 L'idée : interpoler entre voisins

Pour fabriquer un exemple synthétique, SMOTE procède ainsi :

1. choisir au hasard un exemple de la classe rare, $x$ ;
2. trouver ses $k$ plus proches voisins **dans la classe rare** (par défaut $k=5$) et en choisir un au hasard, $x'$ ;
3. tirer un nombre $\lambda$ au hasard entre 0 et 1, et créer le point $x_{\text{nouveau}}=x+\lambda\,(x'-x)$, sur le segment qui relie $x$ à $x'$.

On répète jusqu'à obtenir l'équilibre voulu. Un exemple à la main avec une fraude réelle de notre jeu d'entraînement et son **plus proche voisin** parmi les fraudes, décrites par deux variables (le montant et l'ancienneté du compte en jours) :


```text
types des deux fraudes (1 = compte neuf, 2 = prise de contrôle) : [1, 1]
fraude 1 : [72.4  2. ] | fraude 2 : [77.4  1. ]
point synthétique pour lambda = 0,4 : [74.4  1.6]
```

La première fraude est une commande de 72,4 € sur un compte vieux de 2 jours ; son plus proche voisin parmi les fraudes, une commande de 77,4 € sur un compte de 1 jour (les deux sont des fraudes du même type, le « compte neuf »). Pour $\lambda=0{,}4$, le point synthétique est $x_1+0{,}4\,(x_2-x_1)$, soit une commande d'environ 74,4 € sur un compte de 1,6 jour : un « cousin » plausible des deux fraudes, situé à 40 % du chemin de la première vers la seconde.


![À gauche : fraudes (rouge) et commandes normales (gris) dans le plan (montant, ancienneté du compte) en échelle logarithmique. À droite : les exemples synthétiques créés par SMOTE (croix orange) s'alignent sur des segments entre fraudes voisines et restent dans la zone des fraudes.](figures/ch04-smote.png)

La figure montre le mécanisme et sa limite. Les croix orange sont **entre** des fraudes voisines : SMOTE remplit les trous de la région des fraudes. Les fraudes forment ici **deux groupes** nets (les comptes très récents, en bas, et les comptes anciens mêlés aux commandes normales, en haut), et comme les $k=5$ voisins d'une fraude sont presque toujours du même groupe, les points synthétiques restent dans chacun : l'espace vide entre les deux groupes n'est pas comblé. Mais l'algorithme **suppose que la région des fraudes est compacte** : que n'importe quel point d'un segment entre deux voisines est une fraude plausible. Si un groupe est petit, si $k$ est grand ou si un segment traverse une zone de commandes normales, les points synthétiques deviennent faux. Remarquez enfin que le groupe du haut est **entièrement mêlé aux commandes normales** : y ajouter des fraudes synthétiques ne facilite pas leur séparation.

### 4.5.2 Les variantes

Plusieurs variantes corrigent des défauts de l'algorithme de base. Elles sont toutes disponibles dans la bibliothèque `imbalanced-learn` (`imblearn`).

| Variante | Idée | Quand l'envisager |
|---|---|---|
| **Borderline-SMOTE** | ne crée des points que **près de la frontière** : à partir des exemples rares dont les voisins sont en majorité de la classe normale | on veut renforcer la zone d'incertitude plutôt que le cœur de la classe |
| **ADASYN** | crée plus de points pour les exemples rares **difficiles** (entourés de voisins normaux), moins pour les faciles | les classes se mélangent fortement |
| **SMOTE-NC** | gère les variables **qualitatives** : la catégorie du point synthétique est la plus fréquente parmi les $k$ voisins | des variables non numériques sont mêlées aux numériques |
| **SMOTEN** | variante pour des variables **toutes** qualitatives | données entièrement catégorielles |

Toutes partagent la même limite : elles **inventent des exemples** à partir d'exemples existants, donc ne créent pas d'information nouvelle sur la classe rare. Elles ne font que **remplir** la région déjà observée.

### 4.5.3 Dans un pipeline, et seulement dans le pli d'entraînement

Comme tout ce qui apprend sur les données, SMOTE ne doit s'appliquer qu'au jeu **d'entraînement**. La bibliothèque `imbalanced-learn` fournit un `Pipeline` qui le garantit : l'étape de rééchantillonnage n'est exécutée **que pendant `fit`**, jamais au moment de prédire ni d'évaluer sur le pli de validation.

```python
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import cross_val_score

pipe = Pipeline([("echelle", StandardScaler()),
                 ("smote", SMOTE(k_neighbors=5, random_state=0)),
                 ("modele", LogisticRegression(max_iter=3000))])
scores = cross_val_score(pipe, Xa, ya, cv=5, scoring="average_precision")
print(f"PR-AUC en validation croisée : {scores.mean():.3f} (± {scores.std():.3f})")
```
<!--sortie-->
```text
PR-AUC en validation croisée : 0.212 (± 0.021)
```

### 4.5.4 Faut-il vraiment rééchantillonner ? Une comparaison honnête

Comparons, en validation croisée à 5 plis sur les 42 000 commandes d'entraînement, les stratégies de 4.3 et de 4.5 pour deux modèles. Chaque nombre est la moyenne sur 5 plis, avec son écart-type d'un pli à l'autre.


```text
                      modèle et traitement         AUC-ROC          PR-AUC
              logistique, aucun traitement 0.907 (± 0.019) 0.280 (± 0.059)
              logistique, poids équilibrés 0.910 (± 0.018) 0.219 (± 0.041)
logistique + sur-échantillonnage aléatoire 0.911 (± 0.018) 0.218 (± 0.041)
                        logistique + SMOTE 0.908 (± 0.020) 0.214 (± 0.039)
             logistique + Borderline-SMOTE 0.907 (± 0.018) 0.195 (± 0.028)
                       logistique + ADASYN 0.908 (± 0.020) 0.212 (± 0.038)
                boosting, aucun traitement 0.950 (± 0.010) 0.575 (± 0.040)
                boosting, poids équilibrés 0.966 (± 0.013) 0.544 (± 0.072)
                          boosting + SMOTE 0.945 (± 0.011) 0.500 (± 0.033)
```

Trois enseignements se dégagent.

1. **Le boosting domine la régression logistique**, quel que soit le traitement : PR-AUC de 0,50 à 0,58 contre 0,19 à 0,28. Le choix du modèle pèse bien plus que celui du traitement.
2. **Rééchantillonner n'améliore pas la PR-AUC ; elle baisse.** Pour la logistique, de 0,280 (sans traitement) à 0,195–0,219 avec poids, sur-échantillonnage, SMOTE ou ses variantes ; pour le boosting, de 0,575 à 0,544 avec poids et à 0,500 avec SMOTE. Les écarts entre variantes de SMOTE (0,195 à 0,214) sont du même ordre que l'écart-type d'un pli à l'autre (0,03 à 0,04) : **aucune ne se distingue**.
3. L'AUC-ROC, elle, ne dit pas la même chose : elle reste stable (0,907 à 0,911 pour la logistique) ou monte un peu avec les poids (0,950 à 0,966 pour le boosting). Deux métriques de classement, deux verdicts : c'est un rappel que la **PR-AUC**, centrée sur le haut du classement, est la mesure pertinente quand la classe est rare.

#### L'erreur à ne jamais commettre

Que se passe-t-il si l'on rééquilibre **toute la table d'abord**, puis qu'on lance la validation croisée sur le résultat ? C'est une erreur de débutant très fréquente, parce qu'elle semble innocente.


```text
boosting, sur-échantillonnage aléatoire AVANT la validation croisée : PR-AUC 1.000
boosting, SMOTE AVANT la validation croisée                        : PR-AUC 0.999
```

Les scores s'envolent à **1,000** (sur-échantillonnage aléatoire) et **0,999** (SMOTE) : un modèle presque parfait sur un problème que le même boosting, évalué correctement, ne résout qu'à 0,575 de PR-AUC. Aucune magie : avec le sur-échantillonnage avant la séparation, les **copies d'une même fraude se retrouvent des deux côtés** de la validation ; avec SMOTE, les points synthétiques sont des interpolations entre fraudes voisines, dont une partie se trouve dans le pli de validation. Le modèle est évalué sur des exemples qu'il a, en pratique, déjà vus.

> ⚠️ **Rééchantillonner dans le pipeline, jamais avant.** Le jeu de validation (et le jeu de test) ne doivent contenir **que des exemples réels, dans leur proportion réelle**. C'est la seule façon de savoir comment le modèle se comportera en production, où les fraudes ne seront ni dupliquées ni synthétiques.

### 4.5.5 Que retenir de SMOTE ?

Pour les modèles d'aujourd'hui (boosting, forêts), nos résultats vont dans le même sens que l'expérience de nombreux praticiens : **SMOTE est rarement meilleur que la simple pondération des classes ou que le réglage du seuil**, et il peut dégrader les probabilités et le classement (ici, la PR-AUC du boosting passe de 0,575 à 0,500). Son intérêt est plus net pour des modèles qui apprennent mal avec très peu de positifs (certains réseaux de neurones, des modèles basés sur les distances), ou quand on ne dispose d'**aucun** moyen de pondérer. Avant de l'utiliser :

1. **mesurez** la performance sans rééchantillonnage, avec poids, avec choix de seuil par les coûts (4.3) ;
2. si vous rééchantillonnez, faites-le **dans le pipeline** ;
3. **recalibrez** les probabilités ensuite (section 5.2), car elles sont faussées.

> ✅ **À retenir (SMOTE).** SMOTE crée des exemples rares par interpolation entre voisins ; ses variantes (Borderline, ADASYN, SMOTE-NC) en changent la zone ou le type de variables. Il n'ajoute pas d'information, il est sensible à la forme de la classe rare, et sur des modèles à base d'arbres il fait rarement mieux que les poids ou le seuil. **Dans le pipeline, ou pas du tout.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8 (SMOTE et variantes dans un pipeline, et la fuite par rééchantillonnage) ; exercices 4.13 et 4.14.


## Bilan du chapitre 4

Vous savez maintenant :

- **préparer les variables selon le modèle** : encoder une variable qualitative (disjonctif, ordinal, fréquence, cible), mettre à l'échelle (standardisation, min-max, robuste, quantile) quand le modèle compare des distances ou pénalise des coefficients, corriger l'asymétrie (logarithme, Box-Cox, Yeo-Johnson) quand cela aide vraiment, et **savoir que les arbres n'en ont pas besoin** ;
- **encoder par la cible sans fuite** : calcul hors pli et lissage, et pourquoi le calcul naïf transforme du bruit en « signal » (AUC de 0,678 à l'entraînement, 0,510 au test) ;
- **traiter les valeurs manquantes** en comprenant leur mécanisme (MCAR, MAR, MNAR, structurel), ajouter un **indicateur d'absence** quand l'absence est informative, et ne jamais imputer avant la séparation ;
- **assembler un `Pipeline`** avec `ColumnTransformer`, pour que tout ce qui est appris le soit sur les plis d'entraînement seulement ;
- **fabriquer des variables métier** (ratios, taux, RFM, indicateurs de situation, interactions, variables cycliques), **découvrir des seuils sur l'entraînement**, et comprendre qu'un modèle simple muni des bonnes variables peut égaler un modèle flexible (0,900 d'AUC pour la logistique enrichie, comme pour le boosting) ;
- **repérer la fuite d'information** par la question « quand cette valeur est-elle connue ? » : aucune statistique ne la détecte à coup sûr ;
- **traiter des classes déséquilibrées** : ne jamais juger sur l'exactitude, lire précision, rappel et PR-AUC, comprendre que **poids et rééchantillonnage déplacent les probabilités et le seuil** sans améliorer le classement, et choisir le **seuil par les coûts** ($s^\star=\frac{c_{FP}}{c_{FP}+c_{FN}}$) sur des prédictions hors pli ;
- (en option) **comparer les méthodes de sélection** (filtre, enveloppe, intégrée), préférer l'importance par **permutation**, et **mettre la sélection dans la validation croisée** ; **utiliser SMOTE et ses variantes** dans un pipeline, en sachant qu'il n'améliore pas toujours, et qu'appliqué avant la validation il produit des scores absurdes.

Le fil rouge du chapitre tient en une phrase : **ce qui apprend, apprend sur l'entraînement, et rien que lui**. Encodage par la cible, imputation, mise à l'échelle, choix de seuils, sélection de variables, rééchantillonnage : cinq façons de tricher par inadvertance, que le `Pipeline` et la validation croisée rendent impossibles quand on les utilise correctement.

Le chapitre 5 aborde la question qui conclut toute modélisation : **comment juger un modèle, lui faire confiance et l'expliquer ?** Métriques adaptées au problème, calibration des probabilités, interprétabilité (importance par permutation, SHAP, LIME), puis équité et incertitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 et exercices 4.1 à 4.14.
