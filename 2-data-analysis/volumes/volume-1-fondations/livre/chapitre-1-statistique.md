# Chapitre 1 : Les essentiels de la statistique

> « Un chiffre sans contexte est une opinion qui se fait passer pour un fait. »

C'est votre deuxième semaine à la boutique. La gérante passe la tête dans la porte de votre bureau, un tableau imprimé à la main :

— Notre panier moyen est de **100 €**. C'est un bon chiffre ?

Vous ouvrez la bouche pour répondre « oui » ou « non », et vous vous arrêtez. Bon **par rapport à quoi** ? À l'an dernier, à ce que fait la concurrence, à ce qu'il faudrait pour couvrir les frais ? Et surtout : ce « 100 € » est-il un montant que **beaucoup de clients dépensent vraiment**, ou le résultat de quelques grosses commandes qui tirent la moyenne vers le haut ? Les deux situations donnent le même chiffre, et pourtant elles appellent des décisions très différentes.

Ce chapitre vous donne le **vocabulaire** pour répondre à ce genre de question. La statistique que vous allez y rencontrer n'est pas de la « grosse mathématique » : c'est un petit nombre d'idées, que l'on retrouve à chaque analyse, et qu'il faut avoir **dans les doigts** avant d'ouvrir Excel, d'écrire une requête SQL ou de lancer un notebook.

## Le chemin de ce chapitre

Le **parcours essentiel** compte quatre sections, qui répondent chacune à une question de la gérante :

- **1.1 Statistique descriptive** : *comment résumer des milliers de commandes en quelques nombres honnêtes ?* Le centre (moyenne, médiane), la dispersion (écart-type, quartiles), la forme (asymétrie, valeurs aberrantes), et les moyennes qui trompent.
- **1.2 Distributions et courbe normale** : *quelle forme prennent les phénomènes que nous observons ?* Compter des retours, des commandes, mesurer des âges, des montants : quelques « lois » suffisent pour décrire la plupart des situations.
- **1.3 Échantillonnage et erreur d'échantillonnage** : *si je n'observe qu'une partie des clients, de combien mon chiffre peut-il se tromper ?* L'intervalle de confiance, la taille d'échantillon, et les biais qu'aucune taille d'échantillon ne corrige.
- **1.4 Corrélation et causalité** : *les ventes montent quand la publicité monte : est-ce la publicité qui les fait monter ?* Mesurer une liaison, puis apprendre à ne pas en tirer de conclusion hâtive.

Une section facultative (➕) complète le tout : **1.5 Mathématiques du quotidien en entreprise**, avec les pourcentages, les taux de croissance, les moyennes pondérées, les marges et les arrondis, c'est-à-dire les calculs que vous ferez **tous les jours**.

> 🧭 **Comment lire ce chapitre.** Chaque notion suit le même rythme : une **question** concrète, un **petit exemple calculé à la main** (sur quelques lignes, pour que vous voyiez ce qui se passe), la **formule** expliquée, puis l'**application aux données de la boutique**. Le code est réduit au strict nécessaire : l'essentiel est de comprendre ce que l'on calcule. Les exercices et les applications à refaire se trouvent dans le **cahier**, signalé par le symbole 📒 à la fin de chaque section.

## Les données du chapitre

> 📦 **Les données.** Tout le volume s'appuie sur les données **simulées** de la boutique (le générateur est dans `build/donnees_a1.py`) : une petite enseigne de maison et de décoration, avec **6 catégories** et **120 produits**, trois canaux de vente (`Boutique`, `Site`, `Réseaux`) et des clients répartis dans vingt villes fictives (« Ville A » à « Ville T »). Dans ce chapitre, nous utilisons :
>
> - `commandes.csv` et `lignes_commande.csv` : environ 36 395 commandes et 83 905 lignes de commande entre janvier 2023 et décembre 2025 ;
> - `clients.csv` : 6 000 clients inscrits ;
> - `retours.csv` : les lignes que les clients ont renvoyées ;
> - `jours_exploitation.csv` : une ligne par jour (commandes, chiffre d'affaires, météo, promotion, dépense publicitaire).
>
> Comme les données sont fabriquées, nous connaissons la **vérité** qui les a générées, et nous la révélerons au fil du chapitre : c'est le seul moyen de **vérifier** qu'une méthode statistique répond bien à la question posée, ce que la réalité ne permet presque jamais.

Une commande est composée d'une ou de plusieurs **lignes** (un produit, une quantité, un prix). Le **panier** d'une commande est la somme des montants de ses lignes : c'est la grandeur que la gérante appelle « panier moyen » quand elle fait la moyenne sur toutes les commandes. Chargeons les données et calculons ce premier chiffre.

```python
import pandas as pd
commandes = pd.read_csv("donnees/commandes.csv")
lignes = pd.read_csv("donnees/lignes_commande.csv")
panier = lignes.groupby("id_commande")["montant"].sum()     # une commande = une ou plusieurs lignes
print(len(commandes), "commandes,", len(lignes), "lignes")
print("panier moyen :", round(panier.mean(), 2), "€")
```
<!--sortie-->
```text
36395 commandes, 83905 lignes
panier moyen : 100.38 €
```


Cette moyenne est exacte, mais elle ne répond pas encore à la question de la gérante. Les quatre sections qui suivent expliquent pourquoi, et ce qu'il faut calculer **en plus**.


## 1.1 Statistique descriptive : centre, dispersion, forme

Décrire un jeu de données, c'est répondre à trois questions : **autour de quelle valeur** se répartissent les observations (le centre), **à quel point** elles s'écartent les unes des autres (la dispersion), et **quelle allure** a cette répartition (la forme : symétrique ou étirée, avec ou sans valeurs extrêmes). Ces trois familles de nombres sont les **statistiques descriptives**. Elles ne démontrent rien : elles **résument**. Mais un bon résumé évite la moitié des erreurs d'analyse, et un mauvais résumé (une moyenne seule, par exemple) en fabrique beaucoup.

### 1.1.1 Résumer un panier : le centre

Pour garder les calculs lisibles, partons de **neuf commandes seulement** : les neuf premières enregistrées en boutique le 15 avril 2025. Leurs paniers, en euros, dans l'ordre où elles sont arrivées :

$$9{,}69\;;\;207{,}56\;;\;132{,}37\;;\;258{,}83\;;\;66{,}75\;;\;22{,}56\;;\;50{,}27\;;\;48{,}74\;;\;128{,}25.$$

**La moyenne** est le total divisé par le nombre d'observations :

$$\bar x=\frac{1}{n}\sum_{i=1}^{n}x_i=\frac{925{,}02}{9}=102{,}78\ €.$$

C'est le montant que chaque commande aurait si l'on **répartissait le total à parts égales**. C'est aussi le point d'équilibre : si l'on posait les neuf montants sur une règle, la règle tiendrait en équilibre sur 102,78 €.

**La médiane** est la valeur du milieu quand on range les observations par ordre croissant : la moitié des commandes est en dessous, la moitié au-dessus. Rangeons :

$$9{,}69\;;\;22{,}56\;;\;48{,}74\;;\;50{,}27\;;\;\mathbf{66{,}75}\;;\;128{,}25\;;\;132{,}37\;;\;207{,}56\;;\;258{,}83.$$

Avec neuf valeurs, c'est la cinquième : **66,75 €**. (Avec un nombre pair de valeurs, on fait la moyenne des deux valeurs centrales.)

Les deux résumés diffèrent de **36 €**, et cet écart est une information : quelques grosses commandes (207,56 € et 258,83 €) **tirent la moyenne vers le haut** sans toucher la médiane. Si l'on retirait la commande de 258,83 €, la moyenne tomberait à 83,3 € et la médiane à 58,5 € ; si on la remplaçait par 2 588,30 € (une erreur de virgule), la moyenne exploserait à 361,6 €, alors que la médiane ne bougerait pas. La médiane est **robuste** aux valeurs extrêmes ; la moyenne ne l'est pas.

> 💡 **Moyenne et médiane, en une image.** La moyenne est le **centre de gravité** de la distribution : elle tient compte de la distance de chaque valeur. La médiane est le **centre de position** : elle ne tient compte que de l'ordre. Quand la distribution est étirée d'un côté, la moyenne se laisse entraîner de ce côté ; la médiane reste au milieu des observations.

Deux autres résumés du centre servent régulièrement. **Le mode** est la valeur la plus fréquente : il a un sens pour une variable qui prend peu de valeurs (le nombre d'articles par commande), pas pour un montant en euros où presque toutes les valeurs sont distinctes (on le remplace alors par la **classe modale** d'un histogramme). **La moyenne tronquée** retire un pourcentage de valeurs de chaque extrémité avant de moyenner : c'est un compromis entre la moyenne (sensible aux extrêmes) et la médiane (qui les ignore toutes).

Voyons ces quatre résumés sur les 36 395 commandes de la boutique.

```python
from scipy.stats import trim_mean
print(panier.agg(["mean", "median"]).round(2).to_dict())
print("moyenne tronquée à 5 % :", round(trim_mean(panier, 0.05), 2))
print("mode du nombre de lignes par commande :", lignes.groupby("id_commande").size().mode()[0])
```
<!--sortie-->
```text
{'mean': 100.38, 'median': 79.8}
moyenne tronquée à 5 % : 92.44
mode du nombre de lignes par commande : 2
```


L'écart entre moyenne et médiane se retrouve à grande échelle : **100,38 €** contre **79,80 €**, soit 21 € d'écart. La moyenne tronquée (92,44 €) tombe entre les deux. Et le fait le plus parlant est que **61 % des commandes sont en dessous de la moyenne** : la gérante voit passer une majorité de paniers inférieurs au « panier moyen » de la boutique. Par ailleurs, le nombre de lignes par commande est le plus souvent de **2** (c'est le mode, atteint par 35 % des commandes).

#### Quel résumé annoncer ?

Il n'y a pas de bon résumé en soi : il y a un résumé adapté à la **question posée**.

| Question | Résumé adapté | Pourquoi |
|---|---|---|
| Combien une commande rapporte-t-elle **en moyenne**, pour prévoir le chiffre d'affaires d'un mois ? | la **moyenne** | total = moyenne × nombre de commandes ; la moyenne conserve le total |
| Que dépense un client **typique** ? | la **médiane** | elle n'est pas tirée par les grosses commandes |
| À partir de quel montant une commande est-elle « grosse » ? | un **centile** (par exemple le 95ᵉ : 254 €) | on cherche un seuil, pas un centre |
| Quel est le nombre d'articles le plus courant ? | le **mode** | variable à peu de valeurs |

Pour la gérante, la réponse honnête est donc : « le panier moyen est de 100 € ; **mais** une commande sur deux est inférieure à 80 €, et les 10 % de commandes les plus importantes représentent à elles seules **28 %** du chiffre d'affaires ». La moyenne sert à prévoir, la médiane à décrire. Les deux ensemble disent quelque chose que ni l'une ni l'autre ne dit seule.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.1.

### 1.1.2 Mesurer la dispersion

Deux boutiques peuvent avoir le même panier moyen de 100 € : l'une avec des paniers tous compris entre 90 € et 110 €, l'autre avec des paniers de 5 € à 900 €. Le centre ne les distingue pas. La **dispersion** mesure l'écart entre les observations.

**L'étendue** est la différence entre la plus grande et la plus petite valeur : $258{,}83-9{,}69=249{,}14$ € pour nos neuf commandes. Simple, mais fragile : elle ne dépend que de deux observations.

**Les quartiles** coupent les observations rangées en quatre parts égales. Le premier quartile $Q_1$ laisse 25 % des valeurs en dessous, le troisième $Q_3$ en laisse 75 %. Avec $n$ valeurs rangées, la méthode la plus courante (celle d'Excel avec `QUARTILE.INCLURE`, de R et de pandas par défaut) cherche la valeur à la position $1+p\,(n-1)$, en interpolant entre deux observations voisines si la position n'est pas entière. Pour $n=9$ : $Q_1$ est à la position $1+0{,}25\times8=3$, soit **48,74 €**, et $Q_3$ à la position $1+0{,}75\times8=7$, soit **132,37 €**. **L'écart interquartile** (EIQ) est $Q_3-Q_1=83{,}63$ € : c'est l'étendue des 50 % de valeurs centrales, insensible aux extrêmes.

**La variance et l'écart-type** mesurent la distance **typique** des observations à la moyenne. On part des écarts $x_i-\bar x$, on les élève au carré (pour que les écarts positifs et négatifs ne s'annulent pas), on les additionne, et l'on divise par $n-1$ :

$$s^2=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)^2,\qquad s=\sqrt{s^2}.$$

Le calcul sur nos neuf commandes, moyenne 102,78 € :

| Commande $x_i$ | Écart $x_i-\bar x$ | Écart au carré |
|---:|---:|---:|
| 9,69 | −93,09 | 8 665,7 |
| 22,56 | −80,22 | 6 435,2 |
| 48,74 | −54,04 | 2 920,3 |
| 50,27 | −52,51 | 2 757,3 |
| 66,75 | −36,03 | 1 298,2 |
| 128,25 | 25,47 | 648,7 |
| 132,37 | 29,59 | 875,6 |
| 207,56 | 104,78 | 10 978,8 |
| 258,83 | 156,05 | 24 351,6 |
| **Somme** | 0 | **58 931,5** |

La somme des écarts vaut 0 par construction (c'est ce qui définit la moyenne). La variance vaut $58\,931{,}5/8\approx7\,366{,}4$ €² et l'écart-type $s=\sqrt{7\,366{,}4}\approx\mathbf{85{,}83}$ €. L'écart-type s'exprime dans **la même unité** que les données, ce qui le rend interprétable : un panier s'écarte typiquement de 86 € de la moyenne.

> 💡 **Pourquoi diviser par $n-1$ et pas par $n$ ?** Les écarts sont mesurés par rapport à la moyenne **de l'échantillon**, qui est précisément la valeur la plus proche des observations : ils sont mécaniquement un peu plus petits que les écarts à la vraie moyenne (inconnue). Diviser par $n-1$ corrige ce biais. On dit aussi que, la moyenne étant connue, **seuls $n-1$ écarts sont libres** : le dernier se déduit des autres, puisque leur somme vaut zéro. Pour des milliers d'observations, la différence entre $n$ et $n-1$ disparaît ; pour neuf observations, elle compte.

Enfin, **le coefficient de variation** $\text{CV}=s/\bar x$ exprime la dispersion **relativement** au centre. Il permet de comparer des grandeurs d'unités différentes (des paniers en euros et des délais en jours) : ici $85{,}83/102{,}78\approx0{,}84$.

Sur l'ensemble des commandes :

```python
q1, q3 = panier.quantile([0.25, 0.75])
print("quartiles :", round(q1, 2), round(q3, 2), "| écart interquartile :", round(q3 - q1, 2))
print("écart-type :", round(panier.std(), 2), "| coefficient de variation :", round(panier.std() / panier.mean(), 2))
print("min et max :", panier.min(), panier.max())
```
<!--sortie-->
```text
quartiles : 42.9 135.4 | écart interquartile : 92.5
écart-type : 80.73 | coefficient de variation : 0.8
min et max : 2.32 987.9
```


Les paniers de la boutique ont un écart-type de **81 €** pour une moyenne de 100 € : un coefficient de variation de **0,80**, très élevé. Les 50 % de commandes centrales vont de 43 € à 135 € (EIQ de 92 €), alors que la plus petite vaut 2,32 € et la plus grande 988 €. Il y a de tout, et c'est pourquoi **la moyenne seule est un mauvais portrait** de la clientèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.2.

### 1.1.3 La forme : asymétrie, queues et valeurs aberrantes

Le troisième aspect d'une distribution est sa **forme**. Dessinons les paniers.


![Les paniers des commandes de la boutique. À gauche, l'histogramme (classes de 20 €) : la distribution est étirée vers la droite, la moyenne (orange) est plus grande que la médiane (violet). À droite, la boîte à moustaches : la boîte va du premier au troisième quartile, le trait central est la médiane, les points au-dessus de la moustache sont les valeurs jugées « aberrantes » par la règle de 1,5 écart interquartile.](figures/ch01-paniers.png)

L'histogramme a une allure typique des montants : un **pic à gauche** (beaucoup de petits paniers) et une **longue traîne à droite** (quelques paniers très gros). On dit que la distribution est **asymétrique à droite** (ou « étalée à droite »). La **boîte à moustaches** résume la même information : la boîte contient la moitié centrale des commandes ($Q_1$ à $Q_3$), le trait épais est la médiane, les moustaches s'étendent jusqu'aux valeurs les plus éloignées qui ne sont pas jugées extrêmes, et les points isolés sont les extrêmes.

On mesure l'asymétrie par le **coefficient d'asymétrie** (*skewness*), la moyenne des écarts réduits élevés au cube :

$$g_1=\frac{1}{n}\sum_{i=1}^{n}\left(\frac{x_i-\bar x}{s}\right)^3.$$

Il vaut 0 pour une distribution symétrique, est positif quand la traîne est à droite et négatif quand elle est à gauche. Le **coefficient d'aplatissement** (*kurtosis*, ici en « excès » : 0 pour une courbe normale) mesure le poids des **queues** : il est grand quand il y a plus de valeurs extrêmes que ne le prévoirait une courbe normale. Excel (`COEFFICIENT.ASYMETRIE`, `KURTOSIS`) et pandas utilisent la même version corrigée pour les petits échantillons.

```python
print("asymétrie :", round(panier.skew(), 2), "| aplatissement (excès) :", round(panier.kurt(), 2))
```
<!--sortie-->
```text
asymétrie : 1.85 | aplatissement (excès) : 5.8
```

#### Les valeurs aberrantes : une règle, pas un verdict

Quand une valeur est-elle « aberrante » ? La règle de **Tukey** (celle qui dessine les moustaches) déclare extrême toute valeur située à plus de **1,5 écart interquartile** au-delà des quartiles :

$$x<Q_1-1{,}5\times\text{EIQ}\qquad\text{ou}\qquad x>Q_3+1{,}5\times\text{EIQ}.$$

Pour nos neuf commandes, la borne supérieure est $132{,}37+1{,}5\times83{,}63\approx257{,}8$ € : la commande de 258,83 € la dépasse **d'un euro**. Pour l'ensemble des commandes, la borne inférieure est négative (aucun panier ne peut être « trop petit ») et la borne supérieure vaut :


135,40 + 1,5 × 92,50 = **274,15 €**. Au-delà, la règle signale **1 400 commandes**, soit 3,8 % du total ; l'asymétrie vaut **1,85** et l'aplatissement **5,8**, confirmant une traîne droite lourde.

> ⚠️ **« Aberrant » ne veut pas dire « faux ».** La règle de Tukey signale des valeurs **inhabituelles**, pas des erreurs. Une commande de 700 € passée par un client qui meuble son salon est parfaitement valide ; une commande de 2 588,30 € parce que la virgule a glissé est une erreur de saisie. Devant une valeur extrême, on se pose **trois questions dans cet ordre** : est-ce une *erreur* (à corriger ou à retirer) ? est-ce un cas *légitime mais rare* (à garder, en le sachant) ? ou est-ce un cas d'un **autre type** (une commande de professionnel, une revente) qui mérite une analyse à part ? On **ne supprime jamais** une valeur au seul motif qu'elle est grande, et l'on dit toujours ce que l'on a fait.

Le **résumé des cinq nombres** (minimum, $Q_1$, médiane, $Q_3$, maximum) est le portrait le plus économique d'une distribution : 2,32 ; 42,90 ; 79,80 ; 135,40 ; 987,90. Il montre l'asymétrie d'un coup d'œil : la médiane est plus proche de $Q_1$ que de $Q_3$, et le maximum est très loin de $Q_3$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.3.

### 1.1.4 Quand les moyennes mentent

Une moyenne est un calcul simple, ce qui la rend dangereuse : on la calcule sans réfléchir à **ce qu'elle moyenne**. Deux pièges reviennent sans cesse.

#### La moyenne des moyennes

La gérante demande : « Quel est le taux de retour de la boutique ? » Vous avez le taux de chacun des trois canaux, calculé sur les lignes vendues en 2023-2025 :

| Canal | Lignes vendues | Lignes retournées | Taux de retour |
|---|---:|---:|---:|
| Boutique | 39 362 | 1 211 | 3,08 % |
| Réseaux | 9 071 | 605 | 6,67 % |
| Site | 35 472 | 3 186 | 8,98 % |

Faire la moyenne des trois taux donne 6,24 %. Mais le taux de **toute la boutique** est le nombre total de retours divisé par le nombre total de lignes : 5 002 / 83 905 = **5,96 %**. L'écart (0,28 point) vient de ce que la moyenne simple traite les trois canaux **à égalité**, alors que les canaux n'ont pas le même poids : la Boutique vend près de la moitié des lignes, et son taux est le plus bas. **Une moyenne de pourcentages doit être pondérée** par la taille de chaque groupe (c'est la moyenne pondérée, que la section 1.5.3 détaille). La règle pratique : **repartez toujours des totaux** (retours et lignes), jamais des ratios.


#### Le paradoxe de Simpson

Le second piège est plus troublant : **une tendance observée sur l'ensemble peut s'inverser dans chaque sous-groupe**. Voici un exemple volontairement inventé (les chiffres ne viennent pas des données de la boutique). La boutique a testé deux campagnes d'e-mail, A et B, auprès de 1 500 clients chacune. On compte les clients qui ont acheté dans la semaine, en séparant les clients fidèles (titulaires d'une carte) des nouveaux :

| | Campagne A | | Campagne B | |
|---|---:|---:|---:|---:|
| | envois | achats | envois | achats |
| Clients fidèles | 1 200 | 240 (20 %) | 300 | 66 (22 %) |
| Nouveaux clients | 300 | 15 (5 %) | 1 200 | 78 (6,5 %) |
| **Ensemble** | 1 500 | 255 (**17,0 %**) | 1 500 | 144 (**9,6 %**) |

Dans **chaque** groupe, la campagne B convertit mieux (22 % contre 20 % chez les fidèles, 6,5 % contre 5 % chez les nouveaux). Et pourtant, **sur l'ensemble**, A l'emporte nettement (17,0 % contre 9,6 %). Il n'y a pas d'erreur de calcul : la campagne B a été envoyée surtout à des nouveaux clients, qui achètent beaucoup moins par nature. Le **type de client** est un **facteur de confusion** : il influence à la fois la campagne reçue et le résultat.


La leçon n'est pas « il faut toujours découper » (on peut découper à l'infini et trouver n'importe quoi), mais : **avant de comparer des groupes, demandez-vous s'ils sont comparables**. Les sections 1.3 et 1.4 reviendront sur cette question, qui est au cœur de l'analyse de données.

> ✅ **À retenir.** (1) Moyenne et médiane répondent à des questions différentes : la moyenne conserve le total, la médiane décrit le cas typique. (2) Un centre sans dispersion n'est pas un résumé. (3) Une valeur extrême est une question, pas une erreur. (4) Une moyenne de ratios se calcule à partir des totaux ; une comparaison de groupes suppose des groupes comparables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.2, exercices 1.4 et 1.5.

### 1.1.5 Les mêmes chiffres dans Excel et dans R

Un chiffre qui sort d'un seul outil est un chiffre à vérifier. Voyons comment obtenir les mêmes résumés dans **Excel** et dans **R**, et pourquoi ils concordent.

Dans Excel, on écrit les neuf paniers dans une colonne, puis chaque résumé est une formule. Voici la feuille avec les formules saisies en français ; les formules ont été **vérifiées en les faisant calculer par LibreOffice Calc**, et le dessin est une maquette (ce n'est pas une capture d'Excel).


![Maquette d'une feuille Excel : les neuf paniers en colonne A, et les résumés calculés par des formules (colonnes C à E). La maquette est dessinée à partir des valeurs calculées par LibreOffice Calc : ce n'est pas une capture d'écran d'Excel.](figures/ch01-excel-resume.png)

Les résultats concordent avec le calcul à la main : 102,78 € ; 66,75 € ; 48,74 € ; 132,37 € ; 85,83 €. Trois remarques de lecture :

- `QUARTILE.INCLURE` utilise l'interpolation « inclusive » vue plus haut (position $1+p(n-1)$) ; il existe aussi `QUARTILE.EXCLURE`, qui donne **d'autres quartiles** sur de petits jeux de données. Précisez toujours la version que vous utilisez.
- `ECARTYPE.STANDARD` divise par $n-1$ (écart-type d'échantillon) ; `ECARTYPE.PEARSON` divise par $n$. Sur un échantillon, c'est le premier qu'il faut.
- `MOYENNE.REDUITE(plage ; proportion)` retire la proportion indiquée **au total** (moitié de chaque côté) et arrondit le nombre de valeurs retirées vers le bas, à un nombre pair : avec 9 valeurs et 0,25, on retire 2,25 → 2 valeurs (la plus petite et la plus grande) ; la moyenne tronquée de la feuille porte donc sur 7 valeurs.

Dans R, les mêmes résumés tiennent en quelques lignes. Calculons-les sur les paniers de **l'année 2025** (le même fichier, un autre outil) :

```r
cmd <- read.csv("donnees/commandes.csv"); lig <- read.csv("donnees/lignes_commande.csv")
panier <- tapply(lig$montant, lig$id_commande, sum)
p25 <- panier[as.character(cmd$id_commande[substr(cmd$date_commande, 1, 4) == "2025"])]
c(moyenne = mean(p25), mediane = median(p25), ecart_type = sd(p25))
quantile(p25, c(0.25, 0.75))      # type 7 : même méthode que pandas et QUARTILE.INCLURE
```
<!--sortie-->
```text
   moyenne    mediane ecart_type 
 102.32996   81.61500   82.32644 
   25%    75% 
 44.09 137.72 
```


En pandas sur les mêmes 12 946 commandes de 2025 : moyenne **102,33**, médiane **81,62**, écart-type **82,33**, quartiles 44,09 et 137,72 : ce sont les nombres que R vient d'afficher (à l'arrondi d'affichage près). Que les trois outils s'accordent n'est pas une formalité : c'est la première **vérification croisée**, que ce livre pratique autant que possible. Quand deux outils donnent deux résultats, la différence est presque toujours une **convention** (quartiles inclusifs ou exclusifs, $n$ ou $n-1$) ou une **donnée différente** (lignes filtrées, valeurs vides), et il faut la trouver avant de publier.

> 🧭 **En pratique.** Excel pour explorer et partager, SQL pour interroger de gros volumes, Python ou R pour automatiser et reproduire : le chapitre 2 détaille Excel, le chapitre 3 SQL et le chapitre 4 Python et R. Ce volume apprend à **passer de l'un à l'autre** en retrouvant les mêmes chiffres.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3.


## 1.2 Distributions et courbe normale

Dire qu'un panier moyen est de 100 € ne dit pas **quelle proportion** de clients dépense plus de 200 €. Pour répondre à ce genre de question, il faut connaître la **forme** de la répartition des valeurs, c'est-à-dire une **distribution**. Cette section présente les quelques distributions qui suffisent à décrire la plupart des phénomènes que l'on rencontre en entreprise : des **comptages** (retours, commandes), des **mesures** (âges) et des **montants**. Elle apprend aussi à reconnaître quand aucune de ces lois ne convient, ce qui arrive plus souvent qu'on ne le croit.

### 1.2.1 Qu'est-ce qu'une distribution ?

Une **distribution** décrit **à quelle fréquence** chaque valeur (ou chaque intervalle de valeurs) apparaît. On en distingue deux grandes familles :

- une variable **discrète** ne prend que des valeurs isolées (le nombre de lignes d'une commande : 1, 2, 3…) ; sa distribution est la liste des probabilités $P(X=k)$ ;
- une variable **continue** prend toutes les valeurs d'un intervalle (le panier en euros, une température) ; on ne parle plus de la probabilité d'une valeur exacte (nulle) mais de la probabilité de tomber **dans un intervalle**, qui est l'**aire** sous une courbe appelée **densité**.

L'histogramme est l'image **observée** d'une distribution ; une loi théorique (binomiale, de Poisson, normale…) en est un **modèle**, c'est-à-dire une formule à un ou deux paramètres qui reproduit la forme. Le modèle est pratique : il permet de calculer des probabilités qu'on ne peut pas lire directement sur les données (la probabilité d'un événement rare, par exemple), à condition que **ses hypothèses tiennent**.

La plus simple des lois est la loi **uniforme** : toutes les valeurs ont la même probabilité. La minute à laquelle une commande est passée (de 0 à 59) en est un bon exemple : rien ne distingue 17 heures 03 de 17 heures 48. Les commandes tombent dans les quinze premières minutes de l'heure avec une fréquence de 25,0 %, très près des 25 % que prédit l'uniforme ($15/60$).


### 1.2.2 Compter : les lois binomiale et de Poisson

#### La loi binomiale : combien de retours sur $n$ lignes ?

La gérante veut savoir si un lot de **50 lignes vendues sur le Site** peut contenir 10 retours ou plus, ce qui serait un signal d'alerte. Le taux de retour du Site est de 8,98 %. Chaque ligne est retournée ou non (deux issues), indépendamment des autres, avec la même probabilité $p$ : c'est le schéma de la loi **binomiale** de paramètres $n=50$ et $p=0{,}0898$.

La probabilité d'obtenir exactement $k$ retours est

$$P(K=k)=\binom{n}{k}\,p^k\,(1-p)^{n-k},\qquad E(K)=np,\qquad \text{Var}(K)=np(1-p).$$

Le coefficient $\binom nk=\frac{n!}{k!\,(n-k)!}$ compte les façons de choisir quelles lignes sont retournées. Calculons à la main les deux cas les plus simples : **aucun retour** ($k=0$), $P(K=0)=(1-p)^{50}=0{,}9102^{50}$, soit environ 0,0091 ou 0,9 % ; et le nombre de retours **attendu**, $np=50\times0{,}0898=4{,}49$, avec un écart-type $\sqrt{np(1-p)}$ de 2,02. Obtenir 10 retours ou plus, c'est donc s'éloigner de la moyenne de plus de deux écarts-types : un événement possible mais rare.

```python
from scipy.stats import binom
print("P(0 retour) :", round(binom.pmf(0, 50, 0.0898), 4))
print("P(10 retours ou plus) :", round(binom.sf(9, 50, 0.0898), 4))      # sf(9) = P(K > 9)
```
<!--sortie-->
```text
P(0 retour) : 0.0091
P(10 retours ou plus) : 0.0123
```

Pour **vérifier** que le modèle décrit bien les données, on tire 20 000 fois 50 lignes du Site au hasard dans les données réelles et l'on compte les retours. La figure de gauche ci-dessous compare les fréquences observées aux probabilités de la loi : elles se superposent presque parfaitement. La fréquence observée de « 10 retours ou plus » est de 1,24 % pour 1,23 % attendus.


#### La loi de Poisson : combien d'articles de plus dans un panier ?

Quand on **compte des événements dans un intervalle** (une journée, une commande, une heure) et que ces événements surviennent **indépendamment** et à un rythme moyen constant $\lambda$, on obtient la loi de **Poisson** :

$$P(N=k)=e^{-\lambda}\,\frac{\lambda^k}{k!},\qquad E(N)=\text{Var}(N)=\lambda.$$

Sa signature est que **la variance est égale à la moyenne**. Vérifions sur un cas simple : le nombre d'articles **en plus du premier** dans une commande (nombre de lignes moins un). Sa moyenne vaut 1,31 et sa variance 1,31 : deux nombres voisins, ce qui est bon signe. À la main, avec $\lambda=1{,}3$ : $P(N=0)=e^{-1{,}3}\approx0{,}273$, $P(N=1)=1{,}3\,e^{-1{,}3}\approx0{,}354$, $P(N=2)=\frac{1{,}3^2}{2}e^{-1{,}3}\approx0{,}230$. La figure de droite compare fréquences observées et loi de Poisson : l'accord est excellent.


![Deux lois de comptage face aux données de la boutique. À gauche : le nombre de retours dans un lot de 50 lignes du Site (barres bleues : 20 000 tirages dans les données ; points orange : loi binomiale). À droite : le nombre d'articles supplémentaires dans une commande (barres : fréquences observées ; points : loi de Poisson de même moyenne).](figures/ch01-comptage.png)

#### Quand la loi de Poisson ne convient plus

Appliquons maintenant la même loi à une quantité voisine, le **nombre de commandes par jour**. La moyenne est de 33,2 commandes, mais la variance vaut 169 : **5,1 fois** la moyenne. Ce n'est plus du Poisson. La raison est que les journées ne sont pas comparables : un samedi de décembre en période de soldes n'a rien à voir avec un mardi d'août. La loi de Poisson suppose un **rythme constant** ; ici, le rythme change tous les jours, et mélanger des rythmes différents **gonfle la variance**.

Si l'on se restreint à des journées **comparables** (les mardis hors promotion de septembre et octobre, sur trois ans), le rapport variance/moyenne tombe à 1,3, beaucoup plus près de 1 (il reste un peu au-dessus, car l'activité croît d'une année sur l'autre ; avec 27 journées seulement, l'estimation est elle-même bruitée). La leçon est générale : **un modèle n'est valable que dans les conditions où ses hypothèses tiennent**, et la comparaison variance/moyenne est un test rapide pour la loi de Poisson.


### 1.2.3 La courbe normale

La loi **normale** (ou de Laplace-Gauss, la « courbe en cloche ») est la plus célèbre. Elle est caractérisée par deux paramètres : la **moyenne** $\mu$ (le centre de la cloche) et l'**écart-type** $\sigma$ (sa largeur). Sa densité est

$$f(x)=\frac{1}{\sigma\sqrt{2\pi}}\exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right).$$

Il n'est pas nécessaire de retenir la formule. Il faut retenir **trois propriétés** : la courbe est **symétrique** autour de $\mu$ ; elle est **entièrement déterminée** par $\mu$ et $\sigma$ ; et elle obéit à la règle **68-95-99,7** :

- environ **68 %** des valeurs se trouvent à moins de **1 écart-type** de la moyenne ;
- environ **95 %** à moins de **2 écarts-types** ;
- environ **99,7 %** à moins de **3 écarts-types**.

L'âge des clients de la boutique en offre un exemple. Sur les 6 000 clients, l'âge moyen est de 43,3 ans et l'écart-type de 13,7 ans. La règle prédit 68 % des clients entre 30 et 57 ans ; on observe **66,3 %**. À deux écarts-types (de 16 à 71 ans) on observe **97,4 %** (prédit : 95 %), et à trois écarts-types **99,8 %** (prédit : 99,7 %). L'accord est bon : l'âge est une grandeur à peu près normale. (Le pic isolé à 18 ans, visible sur la figure, est un artefact de la simulation : les clients « plus jeunes » ont été ramenés à 18 ans. Dans des données réelles, un tel pic signale une **coupure** ou une valeur par défaut, et mérite une vérification.)


![L'âge des clients (histogramme, contour gris) et la courbe normale de même moyenne et de même écart-type (orange). Les trois zones bleues correspondent à ±1, ±2 et ±3 écarts-types : elles contiennent environ 68 %, 95 % et 99,7 % des valeurs.](figures/ch01-normale.png)

#### Le score $z$ : mesurer en écarts-types

Comment dire qu'une cliente de 70 ans est « très âgée » pour la clientèle ? En la situant **par rapport à la moyenne, en nombre d'écarts-types**. C'est le **score $z$** :

$$z=\frac{x-\mu}{\sigma}.$$

Pour 70 ans : z = (70 − 43,3) / 13,7 ≈ 1,95.

Un score de 1,95 signifie que la cliente se situe à presque deux écarts-types **au-dessus** de la moyenne. Les tables de la loi normale (ou la fonction `LOI.NORMALE.STANDARD.N` d'Excel, avec l'option cumulative à `VRAI` : à vérifier dans votre version) donnent la probabilité d'être en dessous d'un score $z$ : pour $z=1{,}95$, **97,4 %** (c'est le **centile** de la cliente). Environ **2,5 %** des clients devraient donc avoir 70 ans ou plus si l'âge était exactement normal ; on en observe **3,1 %**. Le score $z$ a un avantage précieux : il permet de **comparer des grandeurs d'unités différentes** (un panier de 250 € et un âge de 70 ans) en les ramenant à la même échelle.

> 💡 **Pourquoi la normale est-elle partout ?** Quand on **additionne** (ou moyenne) beaucoup de petites influences indépendantes, le résultat est approximativement normal, même si chaque influence ne l'est pas. C'est ce qu'établit le **théorème central limite**, que la section 1.3 illustre. Voilà pourquoi la taille ou l'âge d'une population suivent souvent une cloche, et pourquoi les **moyennes** d'échantillons sont presque toujours normales, quelle que soit la forme des données d'origine.

### 1.2.4 Quand la normale ne convient pas

Les montants des paniers, eux, ne sont **pas** normaux : nous l'avons vu, leur histogramme est étiré à droite (asymétrie 1,85). Un modèle normal ajusté à ces paniers prévoirait des paniers **négatifs**. Comment le **vérifier** autrement qu'« à l'œil » ? Avec un **diagramme quantile-quantile** (*Q-Q plot*). On compare chaque quantile des données au quantile correspondant de la loi normale : si les données sont normales, les points s'alignent sur une droite ; une courbure révèle l'écart.


![Diagrammes quantile-quantile. À gauche, les paniers : les points s'écartent nettement de la droite (la traîne droite est bien plus longue que celle d'une normale). À droite, leur logarithme : l'alignement est bien meilleur, mais pas parfait (les petits paniers sont plus rares que ne le prévoit une normale).](figures/ch01-qq.png)

Les paniers forment une courbe très nette (corrélation avec la droite de 0,925) ; leur **logarithme** s'aligne bien mieux (0,986). Quand le logarithme d'une variable est à peu près normal, la variable est dite **log-normale** : c'est le cas typique des montants, des revenus, des tailles d'entreprises, qui résultent de **multiplications** d'effets (un prix multiplié par une quantité, multiplié par une remise…) plutôt que d'additions. Le modèle normal prévoirait 11 % de paniers négatifs, ce qui est absurde ; le modèle log-normal ne le peut pas. Le diagramme montre pourtant que la log-normale n'est elle non plus **qu'une approximation** (asymétrie résiduelle de -0,71) : les paniers très petits sont moins nombreux que le modèle ne le prévoit.

Que faire d'une variable qui n'est pas normale ? Trois attitudes sont courantes. On peut **transformer** (le logarithme) pour se ramener à une cloche. On peut **changer de résumé** : médiane et centiles au lieu de moyenne et écart-type, ce qui ne suppose aucune forme. Ou l'on peut **ne rien supposer** et laisser les données parler (simulation, méthodes dites « non paramétriques »). L'important est de **ne pas appliquer par réflexe** une règle 68-95-99,7 à une variable qui n'est pas en cloche.

#### Quelle loi pour quel phénomène ?

| Phénomène de la boutique | Loi plausible | Paramètres | À vérifier |
|---|---|---|---|
| Minute d'une commande | uniforme | aucun | fréquences égales |
| Retours parmi $n$ lignes | binomiale | $n$, $p$ (9,0 % pour le Site) | indépendance, $p$ constant |
| Articles supplémentaires par commande | Poisson | $\lambda$ (1,3) | variance ≈ moyenne |
| Commandes par jour | Poisson **par tranche homogène** | $\lambda$ qui varie | variance ≈ moyenne dans la tranche |
| Âge des clients | normale | $\mu$ (43 ans), $\sigma$ (14 ans) | Q-Q plot, symétrie |
| Panier d'une commande | asymétrique ; log-normale en première approximation | moyenne et écart-type du logarithme | Q-Q plot du logarithme |

> ✅ **À retenir.** (1) Une distribution est un modèle de la forme des données ; elle permet de calculer des probabilités, **si ses hypothèses tiennent**. (2) Binomiale pour compter des succès sur $n$ essais, Poisson pour compter des événements dans un intervalle (variance = moyenne). (3) La normale est décrite par $\mu$ et $\sigma$ ; le score $z$ mesure en écarts-types ; la règle 68-95-99,7 n'a de sens que pour une variable en cloche. (4) Les montants sont asymétriques : prenez le logarithme, ou résumez par la médiane et les centiles ; vérifiez par un Q-Q plot.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.4, exercices 1.6 et 1.7.


## 1.3 Échantillonnage et erreur d'échantillonnage

Presque toute analyse repose sur un **échantillon** : une partie des clients, des commandes, des réponses à une enquête, dont on veut tirer une conclusion sur **l'ensemble**. La gérante demande : « Vous avez regardé 100 commandes et trouvé un panier moyen de 98 € : est-ce que le vrai chiffre peut être de 110 € ? » Pour répondre, il faut savoir de combien un chiffre calculé sur une partie peut s'écarter du chiffre « vrai ». C'est le sujet de cette section : **quantifier l'erreur due au hasard du tirage**, puis reconnaître les erreurs que le hasard n'explique pas.

### 1.3.1 Population, échantillon, paramètre, statistique

Quatre mots suffisent pour tout ce qui suit.

- La **population** est l'ensemble sur lequel on veut conclure (toutes les commandes de 2025, tous les clients de la boutique).
- L'**échantillon** est la partie effectivement observée, de taille $n$.
- Un **paramètre** est une caractéristique de la population (la moyenne $\mu$ des paniers de 2025), fixe mais généralement inconnue.
- Une **statistique** est une caractéristique de l'échantillon (la moyenne $\bar x$ des 100 paniers observés), connue, mais **qui change d'un échantillon à l'autre**.

On utilise la statistique $\bar x$ pour **estimer** le paramètre $\mu$. L'**erreur d'échantillonnage** est l'écart $\bar x-\mu$ dû uniquement au fait que l'on n'a pas vu toute la population : un autre tirage de 100 commandes aurait donné un autre $\bar x$.

Cette boutique a un luxe que vous aurez rarement : les 12 946 commandes de 2025 sont toutes dans le fichier, et leur panier moyen vaut **102,33 €**. Ici, pour une question sur 2025, il n'y a donc pas d'échantillonnage à faire. Nous allons pourtant **faire comme si** nous ne pouvions voir que 100 commandes, parce que c'est le meilleur moyen de voir la méthode fonctionner : on connaît la réponse exacte, on peut juger l'estimation. Deux remarques de fond avant de commencer :

- **Un recensement n'est pas la fin de l'incertitude.** Les commandes de 2025 sont une population complète pour décrire 2025 ; elles sont **un échantillon** de ce que sera 2026. Dès que l'on généralise à l'avenir (« le panier moyen sera de… »), on est de nouveau en situation d'échantillonnage.
- **« Population » est un choix de l'analyste**, pas une donnée : si la question porte sur les clients actifs, les clients inscrits depuis dix ans ne font pas partie de la population.

### 1.3.2 L'erreur d'échantillonnage en action

Simulons le travail de l'analyste qui ne voit que 100 commandes. On tire au hasard 100 commandes de 2025, on calcule leur moyenne, et l'on **recommence 1 000 fois**.

```python
import numpy as np
rng = np.random.default_rng(1)
ids25 = commandes.loc[commandes["date_commande"] >= "2025-01-01", "id_commande"]
pop = panier.loc[ids25].values                      # la population : tous les paniers de 2025
moyennes = [rng.choice(pop, 100, replace=False).mean() for _ in range(1000)]
print("moyenne des moyennes :", round(np.mean(moyennes), 2), "| vraie moyenne :", round(pop.mean(), 2))
print("écart-type des moyennes :", round(np.std(moyennes), 2), "| σ/√n :", round(pop.std() / 10, 2))
```
<!--sortie-->
```text
moyenne des moyennes : 102.17 | vraie moyenne : 102.33
écart-type des moyennes : 8.11 | σ/√n : 8.23
```


Trois constats. D'abord, **les 1 000 moyennes sont toutes différentes** : de 79,5 € à 132,1 €, alors que la vraie moyenne est 102,3 €. Ensuite, elles sont **centrées sur la vraie valeur** (leur moyenne vaut 102,17 €) : tirer au hasard ne crée pas de biais. Enfin, leur dispersion, l'**erreur type** (*standard error*), vaut 8,11 € : elle est très proche de $\sigma/\sqrt n$ (8,23 €). C'est la formule centrale de cette section :

$$\text{erreur type de }\bar x=\frac{\sigma}{\sqrt n}.$$

L'erreur type dit **de combien la moyenne d'un échantillon s'écarte typiquement de la vraie moyenne**. Elle décroît avec la **racine** de $n$ : pour diviser l'erreur par 2, il faut **quadrupler** l'échantillon ; pour la diviser par 10, il faut le multiplier par 100. Les rendements décroissent vite. Voici l'erreur observée et l'erreur prévue pour quatre tailles d'échantillon :

| Taille $n$ | Erreur type observée (1 000 tirages) | $\sigma/\sqrt n$ |
|---:|---:|---:|
| 10 | 25,4 € | 26,0 € |
| 30 | 14,8 € | 15,0 € |
| 100 | 8,3 € | 8,2 € |
| 400 | 4,1 € | 4,1 € |


> 💡 **La loi des grands nombres.** Quand $n$ augmente, $\bar x$ se rapproche de $\mu$. C'est ce que dit l'erreur type : elle tend vers zéro. En pratique : la moyenne de 10 commandes tirées au hasard vaut 68,3 €, celle de 100 commandes 98,1 €, celle de 1 000 commandes 97,2 € et celle des 12 946 commandes 102,3 €. Mais la loi ne dit pas **à quelle vitesse** : c'est le rôle de l'erreur type. Et elle suppose un **tirage au hasard** : les 1 000 *premières* commandes de l'année (en janvier, pendant les soldes) ont un panier moyen de 92,6 €, loin de la vérité. Ce n'est pas un échantillon, c'est un morceau de calendrier.


#### La forme de la distribution des moyennes : le théorème central limite

Les paniers eux-mêmes ont une distribution très asymétrique. Mais regardons la distribution des **moyennes** de plusieurs paniers.


![Le théorème central limite sur les paniers de 2025. À gauche, la distribution d'un panier (très asymétrique). Ensuite, la distribution de la moyenne de 5, de 30 puis de 200 paniers, sur 2 000 tirages chacune : elle devient de plus en plus symétrique et se rapproche de la courbe normale (orange) de moyenne μ et d'écart-type σ/√n.](figures/ch01-tcl.png)

Avec 5 paniers, la distribution de la moyenne reste étirée à droite (asymétrie 0,88) ; avec 30, elle est déjà presque symétrique (0,43) ; avec 200, elle épouse la courbe normale (0,04). C'est le **théorème central limite** : **la moyenne d'un grand nombre d'observations indépendantes suit approximativement une loi normale, quelle que soit la forme des données d'origine**, de moyenne $\mu$ et d'écart-type $\sigma/\sqrt n$. C'est lui qui justifie tous les intervalles de confiance et tous les tests des chapitres suivants. Il demande, en contrepartie, que $n$ soit assez grand : plus la distribution d'origine est asymétrique, plus il faut d'observations (quelques dizaines suffisent ici ; pour des montants très concentrés sur quelques gros clients, il en faudrait bien davantage).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercice 1.8.

### 1.3.3 L'intervalle de confiance d'une moyenne

Une moyenne seule est une estimation **ponctuelle** : on ne sait pas si elle est précise. Un **intervalle de confiance** (IC) lui ajoute une fourchette. Puisque $\bar x$ est à peu près normale, centrée sur $\mu$ avec l'écart-type $\sigma/\sqrt n$, 95 % des échantillons donnent une moyenne à moins de **deux erreurs types** de la vraie valeur. On en déduit l'intervalle :

$$\bar x\;\pm\;t\,\frac{s}{\sqrt n},$$

où $s$ est l'écart-type de l'échantillon (on ne connaît pas $\sigma$) et $t$ un coefficient (1,96 pour un grand $n$ ; un peu plus pour un petit $n$, d'après la **loi de Student** : 2,306 pour $n=9$).

**À la main, sur nos neuf commandes** (moyenne 102,78 €, écart-type 85,83 €) : l'erreur type vaut $85{,}83/\sqrt9=28{,}61$ €, la marge $2{,}306\times28{,}61\approx65{,}98$ €, d'où l'intervalle **[36,8 € ; 168,8 €]**. Il est **immense**, et c'est normal : avec neuf commandes très dispersées, on ne sait presque rien du vrai panier moyen.

Avec un échantillon de **100 commandes** de 2025, tiré au hasard :

```python
from outils_ch01 import ic_moyenne
echantillon = np.random.default_rng(12).choice(pop, 100, replace=False)
bas, haut = ic_moyenne(echantillon)
print("moyenne :", round(echantillon.mean(), 2), "| IC à 95 % : [", round(bas, 1), ";", round(haut, 1), "]")
```
<!--sortie-->
```text
moyenne : 110.94 | IC à 95 % : [ 92.9 ; 129.0 ]
```


On a trouvé 110,9 € avec un écart-type de 91,1 € ; l'intervalle à 95 % est [92,9 € ; 129,0 €], de **demi-largeur 18,1 €**. La vraie moyenne (102,3 €) se trouve bien dans l'intervalle. La gérante peut donc être informée : avec 100 commandes, le panier moyen est connu à environ **plus ou moins 18 €**, soit 16 %. Avec un panier observé de 98 € et la même précision, « 110 € » ne serait donc pas exclu : il se trouverait à l'intérieur de l'intervalle.

#### Que signifie « 95 % » ?

Le « 95 % » **ne** décrit **pas** la probabilité que $\mu$ soit dans *cet* intervalle (une fois l'intervalle calculé, $\mu$ y est ou n'y est pas). Il décrit la **méthode** : si l'on répétait l'échantillonnage un grand nombre de fois, **95 % des intervalles construits ainsi contiendraient** la vraie valeur. Vérifions-le : on construit 1 000 intervalles à partir de 1 000 échantillons de 100 commandes.


![Quarante intervalles de confiance à 95 %, chacun construit sur un échantillon différent de 100 commandes. La ligne verticale est la vraie moyenne ; les intervalles bleus la contiennent, les intervalles rouges la manquent.](figures/ch01-ic.png)

Sur les 1 000 intervalles, **94,2 %** contiennent la vraie moyenne : 58 la manquent, soit un peu plus que les 5 % annoncés (le théorème central limite n'est qu'une approximation pour des paniers aussi asymétriques). Sur les 40 premiers de la figure, quelques-uns, en rouge, la manquent : c'est le **prix** d'un niveau de confiance de 95 % et non de 100 %. Pour viser 99 %, on élargit l'intervalle (coefficient 2,58 au lieu de 1,96) ; pour un intervalle plus étroit, on paie par un niveau de confiance plus faible.

> ⚠️ **Trois lectures fausses à éviter.** (1) « Il y a 95 % de chances que $\mu$ soit dans l'intervalle » : le hasard est dans l'échantillon, pas dans $\mu$. (2) « 95 % des commandes sont dans l'intervalle » : l'intervalle concerne la **moyenne**, pas les commandes individuelles ; les paniers vont de 2 à 988 €. (3) « Deux intervalles qui se chevauchent prouvent qu'il n'y a pas de différence » : c'est plus subtil, et c'est l'objet des tests du volume III.

### 1.3.4 L'intervalle de confiance d'une proportion

Beaucoup de questions d'entreprise portent sur une **proportion** : le taux de retour, la part de clients satisfaits, le taux d'ouverture d'un e-mail. La gérante demande : « Sur 400 lignes du Site, 36 ont été retournées : est-ce 9 % ? » Le chiffre observé est $\hat p=36/400=9{,}0\ \%$. Son erreur type est

$$\text{erreur type}(\hat p)=\sqrt{\frac{\hat p\,(1-\hat p)}{n}}=\sqrt{\frac{0{,}09\times0{,}91}{400}}\approx0{,}0143,$$

et l'intervalle à 95 % est $\hat p\pm1{,}96\times0{,}0143$, soit $9{,}0\ \%\pm2{,}8$ points : **[6,2 % ; 11,8 %]**. Même avec 400 lignes, le taux de retour est connu à près de trois points près, ce qui est large devant un taux de 9 %. Voyons ce que donne un tirage de 400 lignes dans les données.

```python
from outils_ch01 import ic_proportion
site = lignes.merge(commandes[["id_commande", "canal"]], on="id_commande").query("canal == 'Site'")
retourne = site["id_ligne"].isin(pd.read_csv("donnees/retours.csv")["id_ligne"]).values
tirage = np.random.default_rng(8).choice(retourne, 400, replace=False)
print("taux observé :", round(tirage.mean(), 4), "| IC de Wald :", np.round(ic_proportion(tirage.sum(), 400), 4))
```
<!--sortie-->
```text
taux observé : 0.0975 | IC de Wald : [0.0684 0.1266]
```


Sur ces 400 lignes, 39 sont retournées : 9,75 %, avec un intervalle de [6,8 % ; 12,7 %]. Le taux de retour de l'ensemble du Site, lui, est de 8,98 %. Quand la proportion est **proche de 0 ou de 1**, ou l'échantillon petit, l'intervalle « de Wald » ci-dessus (symétrique autour de $\hat p$) devient peu fiable (il peut même descendre sous 0 %) ; l'intervalle de **Wilson**, légèrement asymétrique, donne [7,2 % ; 13,1 %] ici, et c'est celui qu'on préfère. Retenez surtout l'**ordre de grandeur** : pour une proportion voisine de 50 %, la marge vaut environ $1/\sqrt n$ (3 points pour $n=1\,000$, 5 points pour $n=400$).


### 1.3.5 Combien d'observations faut-il ?

Avant une enquête, une question domine : **quelle taille d'échantillon** pour atteindre une précision donnée ? On inverse les formules. Pour une **moyenne** et une marge d'erreur souhaitée $e$ :

$$n=\left(\frac{1{,}96\,\sigma}{e}\right)^2.$$

Pour connaître le panier moyen à plus ou moins 5 € près, avec un écart-type de 82,3 €, il faut $n=(1{,}96\times82,3/5)^2\approx$ **1 041 commandes**. À ±10 €, il en faut le quart : 260. Pour une **proportion** $p$ et une marge $e$ :

$$n=\frac{1{,}96^2\;p\,(1-p)}{e^2}.$$

Pour un taux de retour d'environ 9 %, connu à ±2 points, il faut $n=1{,}96^2\times0{,}09\times0{,}91/0{,}02^2\approx$ **787 lignes** ; à ±1 point, **3 146**. Si l'on ne sait rien de $p$, on prend le cas le plus défavorable $p=0{,}5$ (le produit $p(1-p)$ est maximal) : $\pm3$ points demandent alors 1 067 répondants, le chiffre classique des sondages.


Deux points de méthode. D'abord, **les formules supposent un échantillon tiré au hasard dans une population très grande** devant lui. Quand l'échantillon représente une fraction notable de la population (disons plus de 5 %), l'erreur est plus petite : on la multiplie par le **facteur de correction de population finie** $\sqrt{(N-n)/(N-1)}$. Pour 400 commandes tirées sur 12 946, il vaut 0,984 (négligeable) ; pour 5 000 commandes, 0,78. Ensuite, la **précision a un coût qui croît très vite** : passer de ±10 € à ±5 € demande quatre fois plus de commandes, de ±5 € à ±2,5 € encore quatre fois plus. Il est souvent plus rentable de **mieux tirer** un petit échantillon que d'en agrandir un mauvais, ce qui nous amène à la dernière question.


### 1.3.6 Les biais, que la taille ne corrige pas

Toute la section précédente mesure l'erreur due **au hasard**. Elle disparaît quand $n$ augmente. Il existe une autre sorte d'erreur, le **biais**, qui ne disparaît **jamais** avec la taille : il vient de la **façon** dont l'échantillon a été constitué, et un grand échantillon biaisé donne simplement une mauvaise réponse **avec une grande assurance**.

Un exemple tiré de la boutique. La gérante veut savoir : « **En moyenne, combien de commandes passe un client en trois ans ?** » Deux manières d'interroger les données :

- **Méthode A** : tirer au hasard 300 clients dans la liste des 6 000 clients inscrits et compter leurs commandes.
- **Méthode B** : tirer au hasard 300 *commandes* (« les clients que l'on croise à la caisse ») et compter, pour chacune, les commandes de son client.

La méthode B paraît naturelle (« on prend des gens qui achètent ») ; mais un client qui commande 40 fois a **40 fois plus de chances** d'être croisé qu'un client qui commande une seule fois. On sur-représente les fidèles.


![Deux façons d'estimer le nombre moyen de commandes par client, avec 1 000 échantillons de 300 chacune. La méthode A (bleu), qui tire des clients dans la liste, est centrée sur la vérité (trait noir). La méthode B (orange), qui tire des commandes, est centrée très au-dessus : le biais ne dépend pas de la taille de l'échantillon.](figures/ch01-biais.png)

La vérité est de **6,07 commandes par client** (en comptant les 1 194 clients inscrits qui n'ont jamais commandé). La méthode A donne en moyenne 6,06, avec une erreur type de 0,44 : sans biais. La méthode B donne en moyenne **15,88**, plus de deux fois trop. Et ce n'est pas une question de taille : avec 3 000 commandes tirées par la méthode B, l'intervalle de confiance à 95 % devient [15,6 ; 16,5], **très étroit et très faux**. C'est l'image de ce que l'on appelle être « précisément à côté de la plaque ».

On retrouve ce mécanisme partout : l'enquête auprès des clients qui ont **accepté** de répondre (les mécontents et les enthousiastes répondent plus que les indifférents), l'analyse des clients **encore actifs** (on a oublié ceux qui sont partis), l'étude des seules **réussites**. La section 5.3 y revient dans le cadre des enquêtes.

> ⚠️ **Erreur d'échantillonnage, biais, erreur de mesure : trois choses différentes.** L'**erreur d'échantillonnage** vient du hasard du tirage ; elle diminue en $1/\sqrt n$ et se quantifie par l'intervalle de confiance. Le **biais de sélection** vient de la façon de constituer l'échantillon ; il ne diminue pas avec $n$ et ne se voit **pas** dans l'intervalle de confiance. L'**erreur de mesure** vient de la façon d'observer (une saisie fausse, une question mal posée, un capteur déréglé) ; elle aussi persiste quand $n$ augmente. Un intervalle étroit ne garantit que l'absence de hasard, **jamais** l'absence d'erreur.

> ✅ **À retenir.** (1) Une statistique d'échantillon varie d'un tirage à l'autre ; son écart-type est l'erreur type $\sigma/\sqrt n$ (division par deux : quadrupler $n$). (2) Le théorème central limite rend la moyenne approximativement normale, d'où l'intervalle $\bar x\pm t\,s/\sqrt n$ ; « 95 % » décrit la méthode, pas une probabilité sur $\mu$. (3) Une proportion a une erreur type $\sqrt{\hat p(1-\hat p)/n}$ ; $n$ se calcule en inversant la formule. (4) Aucune taille d'échantillon ne corrige un biais de sélection : posez toujours la question « **comment ces observations sont-elles arrivées dans mon fichier ?** ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.9 et 1.10.


## 1.4 Corrélation et causalité

Voici la question qui revient dans toutes les entreprises : « Les jours où nous dépensons plus en publicité, nous vendons plus. La publicité marche, non ? » La première moitié de la phrase est un constat sur les données (une **corrélation**) ; la seconde est une **affirmation sur le monde** (une **causalité**). On passe de l'une à l'autre bien plus vite qu'on ne le devrait. Cette section apprend à mesurer une liaison, à la lire correctement, puis à se demander ce qui la produit.

### 1.4.1 Mesurer une liaison : covariance et corrélation

Pour deux grandeurs mesurées sur les mêmes jours (la dépense publicitaire $x$ et le nombre de commandes $y$), la **covariance** moyenne les produits des écarts à la moyenne :

$$\text{cov}(x,y)=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)(y_i-\bar y).$$

Elle est positive quand $x$ et $y$ sont **ensemble** au-dessus ou au-dessous de leur moyenne, négative quand l'un est haut quand l'autre est bas. Mais son échelle dépend des unités (euros × commandes). On la divise donc par les deux écarts-types pour obtenir le **coefficient de corrélation de Pearson**, sans unité, compris entre $-1$ et $+1$ :

$$r=\frac{\text{cov}(x,y)}{s_x\,s_y}=\frac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2\;\sum(y_i-\bar y)^2}}.$$

$r=+1$ : les points sont exactement alignés sur une droite croissante ; $r=-1$ : sur une droite décroissante ; $r=0$ : aucune **liaison linéaire**. Le carré $r^2$ s'interprète comme la part de la variation de $y$ « partagée » avec celle de $x$ le long de la droite.

**À la main sur six jours.** Prenons les six premiers jours de novembre 2025 à partir du lundi 3 : dépense publicitaire (en euros arrondis) et nombre de commandes.

| Jour | $x$ (pub, €) | $y$ (commandes) | $x-\bar x$ | $y-\bar y$ | produit |
|---|---:|---:|---:|---:|---:|
| 1 | 242 | 32 | −153,2 | −14,3 | 2 195,4 |
| 2 | 358 | 45 | −37,2 | −1,3 | 49,6 |
| 3 | 374 | 32 | −21,2 | −14,3 | 303,4 |
| 4 | 583 | 41 | 187,8 | −5,3 | −1 001,8 |
| 5 | 325 | 58 | −70,2 | 11,7 | −818,6 |
| 6 | 489 | 70 | 93,8 | 23,7 | 2 220,7 |
| **Somme** | | | 0 | 0 | **2 948,7** |

Avec $\bar x=395{,}2$ €, $\bar y=46{,}3$, $\sum(x-\bar x)^2=74\,298{,}8$ et $\sum(y-\bar y)^2=1\,137{,}3$ :

$$r=\frac{2\,948{,}7}{\sqrt{74\,298{,}8\times1\,137{,}3}}=\frac{2\,948{,}7}{9\,192{,}4}\approx0{,}32.$$

Une corrélation modérée et positive. Mais **six jours, c'est très peu**. En prenant d'autres semaines de six jours, on obtient des coefficients de -0,81, -0,24, 0,32 et 0,45 : de fortement négatif à modérément positif, pour la **même** relation sous-jacente. Un coefficient de corrélation calculé sur peu d'observations est **très instable** ; l'intervalle de confiance de la section 1.3 s'applique aussi à $r$.


Le coefficient de Pearson mesure une relation **linéaire**. Quand la relation est monotone sans être linéaire, ou en présence de valeurs extrêmes, on préfère le coefficient de **Spearman**, qui n'est autre que le coefficient de Pearson calculé sur les **rangs** (on remplace chaque valeur par sa position dans l'ordre croissant) : il ne dépend que de l'ordre, pas de l'échelle, et résiste aux valeurs aberrantes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.11.

### 1.4.2 Toujours regarder le nuage de points

Un seul nombre ne peut pas résumer une relation. L'exemple classique est celui du statisticien Francis Anscombe (1973) : **quatre jeux de onze points** qui ont exactement les mêmes moyennes, les mêmes variances et **le même coefficient de corrélation** ($r=0{,}816$), mais des formes très différentes.


![Les quatre jeux d'Anscombe : mêmes moyennes, mêmes écarts-types, même droite de régression et même corrélation (0,816). A : une vraie relation linéaire. B : une relation courbe, que la droite décrit mal. C : une relation parfaitement linéaire, déformée par un point isolé. D : aucune relation, sauf un point extrême qui, à lui seul, crée la corrélation.](figures/ch01-anscombe.png)

Dans le jeu B, la relation est **parfaite mais courbe** ; dans C, un seul point isolé fait baisser un alignement parfait ; dans D, il n'y a **aucune** relation, hormis un point extrême qui fabrique la corrélation à lui seul. Le coefficient $r$ est **aveugle** à ces différences. Les règles qui en découlent :

- **Dessinez toujours** le nuage de points avant de calculer $r$.
- Un $r$ proche de 0 n'implique pas l'**absence** de relation, seulement l'absence de relation *linéaire* (une relation en U donne $r\approx0$).
- Un $r$ élevé peut être l'œuvre d'un **seul point** : retirez-le pour voir.
- Le $r$ calculé sur des **moyennes** (par mois, par ville) est généralement plus fort que celui calculé sur les individus, car la moyenne gomme le bruit : c'est l'**erreur écologique** quand on en tire des conclusions sur des individus.

### 1.4.3 La publicité et les ventes : une corrélation trompeuse

Revenons à la gérante. Sur les 1 096 jours de la boutique, la corrélation de Pearson entre la **dépense publicitaire du jour** et le **chiffre d'affaires du jour** vaut **0,42** (Spearman : 0,29). C'est une liaison positive franche. Regardons le nuage.


![À gauche, chaque point est un jour : la dépense publicitaire (horizontal) et le chiffre d'affaires (vertical), colorés selon la période de l'année. Les points de novembre-décembre (orange) sont en haut à droite : forte dépense et fortes ventes. À droite, les mêmes données après avoir retiré, pour chaque mois, la moyenne du mois : à mois égal, la relation disparaît presque.](figures/ch01-pub.png)

Le nuage de gauche a une structure : les jours de **novembre-décembre** (orange) ont à la fois les plus fortes dépenses (en moyenne 400 € par jour, contre 141 € les autres mois) et les plus fortes ventes (4 895 € par jour contre 3 006 €). La **saison** pousse **en même temps** la dépense (la boutique fait plus de publicité avant Noël) et les ventes (les clients achètent plus avant Noël). La publicité et les ventes sont corrélées parce qu'elles **ont une cause commune**, la saison.

Pour tester cette explication, on compare des jours **du même mois** : on retire à chaque jour la moyenne de son mois, pour la dépense et pour le chiffre d'affaires, et l'on regarde la corrélation entre les **écarts**. Elle tombe de 0,42 à **0,05** (graphique de droite) : à mois égal, un jour de forte dépense n'est pas sensiblement meilleur qu'un jour de faible dépense. Le coefficient initial mesurait surtout l'**effet du calendrier**.

> 💡 **Le facteur de confusion.** Quand une troisième grandeur $Z$ (ici la saison) influence à la fois $X$ (la dépense) et $Y$ (les ventes), $X$ et $Y$ sont corrélées **même si $X$ n'a aucun effet sur $Y$**. On dit que $Z$ est un **facteur de confusion**. C'est la raison de principe pour laquelle une corrélation observée ne prouve pas une causalité.

Peut-on aller plus loin, et chiffrer le **vrai** effet de la publicité ? On compare des journées qui ne diffèrent que par la dépense, en neutralisant simultanément le mois, le jour de la semaine, la promotion, la pluie et la tendance (une **régression multiple**, que le volume III de cette série détaille). Voici le résultat pour la dépense cumulée sur les sept derniers jours, en milliers d'euros, et la variation relative du nombre de commandes :

| Effet de 1 000 € de dépense hebdomadaire sur le nombre de commandes | Estimation | Intervalle à 95 % |
|---|---:|---:|
| **Naïf** : sans rien neutraliser | +32 % | |
| **Ajusté** : à mois, jour, promotion, pluie et tendance égaux | +0,7 % | de -3,7 % à +5,3 % |
| **Vérité programmée** | +1,5 % | |

L'estimation naïve annonce que 1 000 € de plus par semaine augmentent les commandes de **32 %** : un résultat énorme, qui est un artefact de la saison. L'estimation ajustée est de l'ordre de **0,7 %**, avec un intervalle qui contient à la fois **zéro** et la vérité (+1,5 %). Honnêtement : avec trois ans de données et un effet aussi petit, on **ne sait pas distinguer** une publicité utile d'une publicité inutile. C'est une conclusion modeste, et c'est la bonne : pour la trancher, il faudrait **faire varier la dépense exprès** (une expérience), pas attendre que le calendrier la fasse varier à notre place.


> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7.

### 1.4.4 La température et les ventes de jardin

Un second exemple, plus subtil. La boutique vend, dans sa catégorie « Jardin », des arrosoirs, des parasols, des transats. Sur les 1 096 jours, le nombre de lignes « Jardin » vendues dans la journée est corrélé à la température moyenne du jour (coefficient de corrélation de 0,69). Le froid ou la chaleur du jour pilotent-ils les achats de jardin ?

On refait le test précédent : comparer des jours **du même mois**. À mois égal, la corrélation entre l'écart de température et l'écart de lignes « Jardin » vaut **-0,00** : rien. C'est **la saison**, une fois de plus, qui produit la liaison : en été il fait chaud *et* l'on achète des transats ; mais un jour de juillet plus frais que la moyenne ne fait pas vendre moins. (Dans cette simulation, la température intervient dans le *choix des catégories* selon le mois, jamais selon le temps du jour. Dans la réalité, la météo du jour peut avoir un effet réel : on ne le saurait qu'en le mesurant à saison égale, comme on vient de le faire.)


### 1.4.5 Les corrélations fortuites

Troisième piège : à force de chercher, on **trouve**. Avec 100 variables, il y a $100\times99/2=4\,950$ paires. Si chacune est testée au risque habituel de 5 %, on s'attend à voir environ 5 % de paires « significativement » corrélées **par pur hasard**, soit quelque 250. Vérifions avec 100 séries de 30 nombres tirés au hasard, **indépendantes** par construction.

```python
import numpy as np
rng = np.random.default_rng(7)
series = rng.normal(size=(30, 100))                   # 100 variables sans aucun lien, 30 observations
r = np.corrcoef(series.T)[np.triu_indices(100, 1)]    # les 4 950 corrélations
print("paires :", len(r), "| |r| > 0,36 :", int((abs(r) > 0.36).sum()), "| plus grand |r| :", round(abs(r).max(), 2))
```
<!--sortie-->
```text
paires : 4950 | |r| > 0,36 : 271 | plus grand |r| : 0.63
```


Avec 30 observations, un coefficient dépasse 0,36 en valeur absolue dans environ 5 % des cas **sous l'hypothèse d'indépendance** ; on en trouve ici **271 sur 4 950** (5,5 %), et le plus grand atteint **0,63**, un chiffre qui ferait un joli graphique dans une présentation. Aucune de ces liaisons n'est réelle. La leçon est celle du **dragage de données** (*p-hacking*) : plus on teste de relations, plus on est sûr d'en trouver une « remarquable ». Le remède est de **formuler l'hypothèse avant** de regarder les données, de **corriger** pour le nombre de comparaisons (le volume III y revient), et surtout de **vérifier sur des données nouvelles** : une vraie relation survit, une relation fortuite disparaît.

### 1.4.6 De la corrélation à la causalité

Quand on observe que $X$ et $Y$ sont corrélées, il y a **quatre** explications possibles :

1. **$X$ cause $Y$** (la publicité fait vendre).
2. **$Y$ cause $X$** : la **causalité inverse**. La gérante règle son budget de décembre sur les ventes qu'elle attend : les ventes « causent » la dépense.
3. **Un tiers $Z$ cause les deux** : le **facteur de confusion** (la saison).
4. **Le hasard** : une corrélation fortuite, surtout quand on a cherché ou que $n$ est petit.

Les explications se combinent, et les données seules ne disent pas laquelle est la bonne. Dessiner la situation aide : une flèche par influence supposée.


![Le schéma du facteur de confusion dans la boutique. La saison influence fortement la dépense publicitaire et les ventes (flèches grises) ; l'effet direct de la dépense sur les ventes (flèche rouge pointillée) est petit. La corrélation observée entre dépense et ventes mélange les deux chemins.](figures/ch01-confusion.png)

Comment établir qu'une relation est **causale** ? La méthode la plus solide est l'**expérience aléatoire** : on **décide au hasard** quels clients (ou quels jours) reçoivent le « traitement » (la publicité, la promotion, l'e-mail) et l'on compare les groupes. Le tirage au sort garantit que tous les facteurs de confusion, connus ou inconnus, se répartissent également entre les groupes ; la différence qui reste ne peut venir que du traitement. C'est le **test A/B**, que le volume III détaille. Quand l'expérience est impossible (on ne peut pas tirer au sort la saison), on **ajuste** par des facteurs mesurés, comme nous l'avons fait ; mais l'ajustement ne neutralise que ce que l'on a **pensé** à mesurer.

Les données de la boutique, parce qu'elles sont simulées, permettent un contrôle rare : comparer ce que l'on estime à ce qui a **réellement** été programmé.

| Effet | Estimation naïve | Estimation ajustée | Vérité programmée |
|---|---:|---:|---|
| Promotion sur le nombre de commandes du jour | +8 % | +19 % (de +14 à +24 %) | +18 % |
| Dépense hebdomadaire (+1 000 €) sur les commandes | +32 % | +0,7 % (de -3,7 à +5,3 %) | +1,5 % |
| Tendance annuelle des commandes | | +6,5 % | +6 % |

Pour la **promotion**, la comparaison naïve (nombre moyen de commandes les jours de promotion et les autres) donne +8 % : la plupart des jours de promotion tombent **en creux saisonnier** (soldes de janvier et d'été), ce qui réduit l'écart apparent. En comparant à mois, jour de semaine et tendance égaux, on retrouve +19 %, tout près des +18 % programmés. Même méthode que pour la publicité, même facteur de confusion (le calendrier), mais **ici** l'effet est assez grand pour émerger du bruit, **là** il ne l'est pas. Le contrôle par les facteurs mesurés a donc **fonctionné pour la promotion** et **révélé un effet minuscule pour la publicité** : deux conclusions honnêtes à partir des mêmes outils.


> ⚠️ **Le vocabulaire compte.** « La publicité **augmente** les ventes » est une affirmation causale ; « les ventes sont **plus élevées** les jours de forte publicité » est un constat. Dans un rapport, écrivez le constat sauf si votre méthode (expérience, ajustement soigneux, argument de mécanisme) justifie l'affirmation, et **dites laquelle**.

> ✅ **À retenir.** (1) $r$ mesure une liaison **linéaire**, entre −1 et +1 ; il est instable sur peu de données et aveugle à la forme (Anscombe) : **dessinez**. (2) Une corrélation a quatre explications : cause, cause inverse, facteur de confusion, hasard. (3) Comparer **à saison égale** fait souvent disparaître une corrélation : la saison, le calendrier, la taille des clients sont les facteurs de confusion habituels. (4) À force de chercher, on trouve : formulez l'hypothèse avant, vérifiez sur des données nouvelles. (5) La preuve causale la plus solide est l'expérience aléatoire ; à défaut, ajuster honnêtement et dire ce que l'on n'a pas pu mesurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.11 et 1.12.


## 1.5 ➕ Pour aller plus loin : mathématiques du quotidien en entreprise

> 🧭 **Section complémentaire.** Elle ne demande aucune statistique, seulement des calculs que **tout analyste fait chaque semaine** et que l'on rate pourtant régulièrement : pourcentages, taux de croissance, moyennes pondérées, marges, arrondis. Chaque calcul est d'abord fait à la main sur un exemple court, puis vérifié sur les données de la boutique. On peut la lire à tout moment, ou y revenir quand un chiffre « ne tombe pas juste ».

### 1.5.1 Pourcentages : part, variation, points

Un **pourcentage** est une fraction exprimée sur cent. Il sert à deux choses très différentes qu'il faut savoir distinguer :

- une **part** : « le Site représente 47 % des commandes » (une partie rapportée à un tout) ;
- une **variation** : « le chiffre d'affaires a augmenté de 11 % » (un changement rapporté à la valeur de départ), $\dfrac{\text{valeur finale}-\text{valeur initiale}}{\text{valeur initiale}}$.

La confusion classique concerne les **points** et les **pour cent**. La part des commandes passées sur le Site est passée de 37,4 % en 2023 à 46,9 % en 2025. On peut dire :

- « la part du Site a augmenté de **9,5 points** » : c'est la différence entre deux pourcentages, exprimée en **points de pourcentage** ;
- « la part du Site a augmenté de **25 %** » : c'est la variation **relative** ((46,9 − 37,4) / 37,4).

Les deux sont exacts, et ils ne disent pas la même chose. Dans un rapport, écrivez toujours **l'unité** (« points » ou « % ») : écrire « +9 % » pour 9 points est l'erreur la plus fréquente des tableaux de bord.

Trois pièges de calcul reviennent sans cesse.

- **Les variations ne s'additionnent pas.** Une hausse de 10 % suivie d'une baisse de 10 % ne ramène pas au point de départ : $100\times1{,}10\times0{,}90=99$, soit **−1 %**. De même, pour revenir au point de départ après une baisse de 20 %, il faut une hausse de **25 %** ($0{,}80\times1{,}25=1$), pas de 20 %.
- **Une réduction ne se défait pas avec le même pourcentage.** Un prix de 60 € réduit de 20 % vaut 48 € ; pour retrouver 60 €, on ajoute 12 € à 48 €, soit 25 %.
- **Retrouver la base : on divise, on ne retranche pas.** Un prix TTC de 120 € avec une TVA de 20 % (taux d'exemple) correspond à un prix HT de $120/1{,}20=100$ €, **pas** de $120-20\,\%\times120=96$ €. Le pourcentage s'applique à la **base**, c'est-à-dire au prix HT, non au prix TTC.


### 1.5.2 Taux de croissance

Le chiffre d'affaires de la boutique était de **1 138 932 €** en 2023, **1 189 461 €** en 2024 et **1 324 764 €** en 2025. Comment résumer cette évolution ?

**Le taux de croissance** entre deux périodes est la variation relative : +4,4 % de 2023 à 2024 et +11,4 % de 2024 à 2025. Mais sur deux ans, la hausse totale n'est **pas** la somme des deux taux. Les taux **se composent** (on les multiplie) :

$$(1+g_{24})\,(1+g_{25})=1+g_{23\to25}.$$

Ici, le produit des deux coefficients vaut 1,1632, soit **+16,3 %** sur deux ans.

Pour comparer des périodes de durées différentes, on utilise le **taux de croissance annuel moyen** (TCAM, *CAGR* en anglais) : le taux constant qui produirait la même croissance totale.

$$\text{TCAM}=\left(\frac{\text{valeur finale}}{\text{valeur initiale}}\right)^{1/\text{nombre d'années}}-1.$$

**À la main.** Un chiffre qui passe de 100 à 121 en deux ans a un TCAM de $\sqrt{1{,}21}-1=10\ \%$ par an (et non 21/2 = 10,5 %) : $100\times1{,}10\times1{,}10=121$. Pour la boutique : (1 324 764 / 1 138 932)^(1/2) − 1 = **7,85 %** par an, alors que la moyenne arithmétique des deux taux annuels vaut 7,91 %. Les deux sont proches ici (les taux annuels sont proches) ; ils divergent quand les taux sont très différents.

Une **échelle en indice** (base 100) facilite la lecture : on fixe la valeur de départ à 100. Avec la base 100 en 2023, le chiffre d'affaires vaut 104,4 en 2024 et 116,3 en 2025 : on lit directement les variations en pourcentage depuis 2023.

#### Comparer avec le bon mois

Peut-on dire « les ventes de décembre ont augmenté de 28 % : excellent mois » ? Seulement par rapport à novembre, et c'est trompeur : **la saisonnalité** rend tout mois de décembre supérieur à novembre. La figure montre le chiffre d'affaires mensuel de chaque année (à gauche), puis, pour 2025, la variation par rapport **au mois précédent** (barres bleues) et par rapport **au même mois de l'année précédente** (barres orange).


![À gauche, le chiffre d'affaires mensuel de chaque année : la saison (creux d'été, pic de novembre-décembre) est la même d'une année à l'autre, avec un niveau qui monte. À droite, pour 2025, la variation par rapport au mois précédent (bleu) oscille fortement à cause de la saison ; la variation par rapport au même mois de l'année précédente (orange) reste dans une fourchette plus étroite, autour de la croissance annuelle.](figures/ch01-croissance.png)

Les variations « par rapport au mois précédent » vont de -19 % à +28 % : elles décrivent le **calendrier**, pas la santé de l'entreprise. Les variations « par rapport au même mois de 2024 » vont de -1 % à +19 %, une fourchette moitié moins large, centrée sur la croissance annuelle de 11 % : c'est la comparaison qui **neutralise la saison**, et celle qu'il faut privilégier dans un rapport mensuel. Décembre 2025, par exemple, est à **+16,9 %** de décembre 2024.

### 1.5.3 Moyennes pondérées et décomposition prix-volume

#### La moyenne pondérée

Quand on moyenne des groupes de **tailles différentes**, chaque groupe doit compter proportionnellement à sa taille. La **moyenne pondérée** est

$$\bar x_w=\frac{\sum_i w_i\,x_i}{\sum_i w_i},$$

où $w_i$ est le poids du groupe $i$ (le nombre de commandes, le chiffre d'affaires…). **À la main.** Deux canaux : le Site, avec 300 commandes à un panier moyen de 90 €, et la Boutique, avec 100 commandes à 130 € : la moyenne simple des deux paniers moyens est de 110 €, mais la moyenne **pondérée** est $(300\times90+100\times130)/400=100$ €. C'est le panier moyen de l'ensemble.

Sur la boutique en 2025, les trois canaux ont les paniers moyens suivants :

| Canal | Commandes 2025 | Panier moyen |
|---|---:|---:|
| Boutique | 5 442 | 103,08 € |
| Réseaux | 1 426 | 102,44 € |
| Site | 6 078 | 101,63 € |

La moyenne simple des trois est de 102,38 € ; la moyenne pondérée par les commandes est de **102,33 €**, qui est exactement le panier moyen de 2025 (102,33 €). Le poids est la **bonne** quantité à utiliser, et la règle générale demeure : **pour recomposer un total, pondérez**.


#### Prix, volume, mix : pourquoi le chiffre d'affaires a-t-il augmenté ?

La gérante demande : « Le chiffre d'affaires 2025 est en hausse de 11,4 % : est-ce parce que nous avons **vendu plus** ou parce que nous avons **augmenté les prix** ? » Le chiffre d'affaires est un **produit** : $\text{CA}=\text{unités vendues}\times\text{CA moyen par unité}$. Sa variation se décompose donc en deux facteurs qui **se multiplient** :

$$1+g_{\text{CA}}=\underbrace{(1+g_{\text{volume}})}_{\text{unités vendues}}\times\underbrace{(1+g_{\text{prix-mix}})}_{\text{CA moyen par unité}}.$$

En 2025, le nombre d'unités vendues a augmenté de **7,4 %** (de 33 323 à 35 801 unités), et le chiffre d'affaires moyen par unité de **3,7 %** (de 35,69 € à 37,00 €). Vérification : 1,0744 × 1,0367 = 1,1138, soit bien 1 + 11,4 %. Le catalogue a en effet été augmenté de **3 %** le 1ᵉʳ janvier 2025 ; l'écart avec les 3,7 % constatés vient du **mix** (la part de chaque produit dans les ventes) et des **remises** (la part des ventes sous promotion). Moralité : en proportion (logarithmique) de la croissance de 2025, environ **67 %** vient du **volume** et le reste du prix et du mix : une décomposition qu'aucun des deux chiffres, pris seuls, ne révèle.


### 1.5.4 Marge, marque et TVA

Le prix affiché en rayon est **TTC** (toutes taxes comprises) ; le chiffre d'affaires comptable est **HT** (hors taxes), car la TVA est reversée à l'État. Pour parler de rentabilité, il faut donc d'abord passer en HT : $\text{prix HT}=\text{prix TTC}/(1+\text{taux de TVA})$. Dans ce livre, la TVA est de **20 %** : c'est un taux d'exemple, il varie selon les pays et les produits.

Trois notions se ressemblent et ne se confondent pas :

- la **marge brute** (en euros) : prix de vente HT − coût d'achat HT ;
- le **taux de marque** : marge brute / **prix de vente HT** (c'est la part du prix qui reste) ;
- le **taux de marge** : marge brute / **coût d'achat** (c'est le « coefficient » ajouté au coût).

**À la main.** Un produit vendu 30,00 € TTC, acheté 15,00 € HT. Prix HT : $30/1{,}2=25{,}00$ €. Marge brute : $25-15=10$ €. Taux de marque : $10/25=\mathbf{40\ \%}$. Taux de marge : $10/15\approx\mathbf{66{,}7\ \%}$. Les deux sont reliés par :

$$\text{taux de marque}=\frac{\text{taux de marge}}{1+\text{taux de marge}}\qquad\Longleftrightarrow\qquad\text{taux de marge}=\frac{\text{taux de marque}}{1-\text{taux de marque}}.$$

> ⚠️ **L'erreur de coefficient.** On veut un taux de marque de 40 % sur un produit acheté 15 € HT. Appliquer « +40 % » au coût donne un prix HT de $15\times1{,}4=21$ €, soit une marque de $6/21\approx28{,}6\ \%$ seulement. Le bon prix HT est $15/(1-0{,}40)=25$ €. **Précisez toujours** quelle marge vous annoncez : selon les entreprises et les pays, « taux de marge » et « taux de marque » sont employés l'un pour l'autre.

Sur la boutique, calculons le taux de marque de l'année 2025, par catégorie (chiffre d'affaires HT = montant / 1,2 ; coût = quantité × coût d'achat HT).

```python
lg25 = lignes.merge(commandes[["id_commande", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
produits = pd.read_csv("donnees/produits.csv")
lg25 = lg25.merge(produits[["id_produit", "categorie", "cout_achat"]], on="id_produit")
lg25["ca_ht"] = lg25["montant"] / 1.2
lg25["cout"] = lg25["quantite"] * lg25["cout_achat"]
cat = lg25.groupby("categorie")[["ca_ht", "cout"]].sum()
cat["taux_marque_%"] = ((cat["ca_ht"] - cat["cout"]) / cat["ca_ht"] * 100).round(1)
print(cat["taux_marque_%"].to_dict())
print("ensemble :", round((cat["ca_ht"].sum() - cat["cout"].sum()) / cat["ca_ht"].sum() * 100, 1), "%")
```
<!--sortie-->
```text
{'Bien-être': 35.1, 'Cuisine': 37.3, 'Décoration': 39.7, 'Jardin': 38.3, 'Maison': 37.9, 'Papeterie': 36.9}
ensemble : 38.0 %
```


Les taux de marque vont de **35,1 %** (Bien-être) à **39,7 %** (Décoration) ; celui de l'**ensemble** est de **38,0 %** (soit un taux de marge de 61 %), sur un chiffre d'affaires HT de 1 103 970 €. La moyenne **simple** des taux par catégorie (37,5 %) ne coïncide pas avec le taux de l'ensemble : c'est, une fois de plus, la moyenne de ratios qu'il faut pondérer par le chiffre d'affaires. (Cette marge est « brute » : elle ignore les retours remboursés, les frais de livraison, de personnel et de loyer.)

### 1.5.5 Arrondis : où et quand

Les arrondis semblent anodins, jusqu'à ce qu'un total ne tombe pas juste. Deux difficultés.

**La somme des arrondis n'est pas l'arrondi de la somme.** Une commande de trois articles à 1,04 € HT chacun. Si l'on calcule la TVA ligne par ligne, chaque ligne donne $1{,}04\times0{,}20=0{,}208$ €, arrondi à **0,21** €, soit **0,63 €** au total ; si on la calcule sur le total, $3{,}12\times0{,}20=0{,}624$, arrondi à **0,62 €**. Un centime d'écart, qui devient **des milliers d'euros** à l'échelle de millions de lignes. La règle : **arrondissez le plus tard possible** (à l'affichage), conservez les décimales dans les calculs, et quand la règle comptable impose un arrondi par ligne, **écrivez-le dans la documentation**.

**Les outils n'arrondissent pas tous de la même manière.** Excel arrondit les cas « à égalité » (le chiffre 5 exactement) **à l'écart de zéro** (2,5 → 3 ; −2,5 → −3). Python (la fonction `round`) et pandas arrondissent **au pair le plus proche** (2,5 → 2 ; 3,5 → 4), et à cela s'ajoute la représentation binaire des décimaux (2,675 n'est pas exactement représentable). Comparons, avec les formules vérifiées par LibreOffice Calc :


| Cas | Excel (`ARRONDI`) | Python (`round`) |
|---|---:|---:|
| 2,5 à 0 décimale | 3 | 2 |
| 3,5 à 0 décimale | 4 | 4 |
| −2,5 à 0 décimale | -3 | -2 |
| 0,125 à 2 décimales | 0,13 | 0,12 |
| 2,675 à 2 décimales | 2,68 | 2,67 |

Excel, sur la ligne « 0,125 à 2 décimales », renvoie 0,13 (arrondi « commercial » à l'écart de zéro) ; Python renvoie 0,12 parce que 0,125 est exactement représentable en binaire et que l'égalité est départagée **au pair**. Pour 2,675, Excel renvoie 2,68 (il raisonne sur le nombre décimal tel qu'on l'a écrit) et Python 2,67 (la valeur binaire réellement stockée est légèrement inférieure à 2,675). Le calcul de TVA ligne par ligne contre sur le total se vérifie aussi par formule : `=SOMMEPROD(ARRONDI(A9:A11*0,2;2))` donne **0,63** et `=ARRONDI(SOMME(A9:A11)*0,2;2)` donne **0,62**.

> ⚠️ **Deux outils, deux arrondis.** Quand un total Excel et un total Python diffèrent d'un centime, cherchez d'abord **la règle d'arrondi** avant de chercher une erreur de données. Dans un rapport financier, la règle (à l'écart de zéro, au pair, par ligne, sur le total) fait partie de la méthode.

> ✅ **À retenir.** (1) Distinguez **points** et **pour cent**, **part** et **variation** ; retrouvez une base en **divisant**. (2) Les variations se **multiplient** ; le TCAM est la racine $n$-ième du rapport final sur initial ; comparez au **même mois** de l'an passé. (3) Pour recomposer un total, **pondérez** ; CA = unités × CA moyen par unité, et la croissance se décompose en volume et prix-mix. (4) Marque (sur le prix) et marge (sur le coût) ne sont pas interchangeables : précisez laquelle vous annoncez ; passez en HT avant de parler de rentabilité. (5) Arrondissez le plus tard possible et notez la règle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.13 et 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **résumer** une variable par son **centre** (moyenne, médiane, mode, moyenne tronquée), sa **dispersion** (étendue, quartiles, écart interquartile, écart-type, coefficient de variation) et sa **forme** (asymétrie, aplatissement, valeurs aberrantes par la règle de 1,5 écart interquartile), et **choisir** le résumé qui répond à la question posée ;
- **éviter** deux pièges de moyenne : la moyenne de ratios non pondérée (on repart des totaux) et le **paradoxe de Simpson** (comparer des groupes comparables) ;
- **retrouver les mêmes résumés** dans Excel, dans R et dans pandas, en connaissant les conventions qui les distinguent (quartiles inclusifs ou exclusifs, $n$ ou $n-1$) ;
- **reconnaître** la loi qui décrit un phénomène : **binomiale** pour des succès parmi $n$ essais, **de Poisson** pour des événements dans un intervalle (variance = moyenne, valable par tranche homogène), **normale** pour une grandeur en cloche (règle 68-95-99,7, score $z$), **log-normale** en première approximation pour des montants ; et le **vérifier** par un diagramme quantile-quantile ;
- **mesurer l'erreur d'échantillonnage** : erreur type $\sigma/\sqrt n$, théorème central limite, **intervalle de confiance** d'une moyenne et d'une proportion, **taille d'échantillon** nécessaire, et distinguer l'erreur du hasard, le **biais de sélection** (qu'aucune taille ne corrige) et l'erreur de mesure ;
- **mesurer une liaison** (corrélation de Pearson et de Spearman), **dessiner** avant de calculer (jeux d'Anscombe), repérer un **facteur de confusion** en comparant « à saison égale », se méfier des corrélations fortuites, et énoncer les quatre explications d'une corrélation (cause, cause inverse, confusion, hasard) ;
- (en option) faire les **calculs du quotidien** : points et pour cent, variations qui se composent, taux de croissance annuel moyen, comparaison au même mois, moyennes pondérées, décomposition prix-volume, marque, marge et TVA, arrondis.

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec, quand elle est connue, la **vérité programmée** :

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Panier moyen et panier médian | 100,4 € et 79,8 € | 61 % des commandes sont sous la moyenne : annoncer les deux |
| Dispersion des paniers | écart-type 81 €, CV 0,80 ; asymétrie 1,85 | la moyenne seule est un mauvais portrait |
| Taux de retour : moyenne des canaux ou taux global | 6,24 % contre 5,96 % | repartir des totaux |
| L'âge des clients et la règle 68-95-99,7 | 66 %, 97 %, 99,8 % | l'âge est à peu près normal ; les paniers ne le sont pas |
| Erreur type de la moyenne de 100 paniers | 8,1 € (formule : 8,2 €) | quadrupler $n$ divise l'erreur par 2 |
| Intervalle à 95 % : couverture réelle | 94,2 % des 1 000 intervalles contiennent la vérité | « 95 % » décrit la méthode |
| Commandes par client : tirer des clients ou des commandes | 6,1 contre 15,9 (vérité : 6,1) | un biais de sélection ne se corrige pas par la taille |
| Corrélation dépense publicitaire – chiffre d'affaires | 0,42 au total, 0,05 à mois égal | la saison est un facteur de confusion |
| Effet de la dépense publicitaire (par 1 000 € par semaine) | +32 % naïf, +0,7 % ajusté (vérité +1,5 %) | l'effet est trop petit pour être mesuré avec ces données |
| Effet de la promotion sur les commandes | +8 % naïf, +19 % ajusté (vérité +18 %) | ajuster sur le calendrier retrouve la vérité |
| Croissance du chiffre d'affaires 2023-2025 | TCAM 7,85 % par an ; en 2025, 67 % portée par le volume | décomposer prix et volume |

Le fil conducteur du chapitre tient en une phrase : **un chiffre n'a de valeur que si l'on sait ce qu'il résume, ce qu'il ignore, et de combien il peut se tromper**. Une moyenne sans dispersion, un pourcentage sans base, une corrélation sans explication ni intervalle sont des demi-vérités ; les corriger est le travail le plus ordinaire, et le plus utile, de l'analyste.

> 🧭 **En pratique : cinq questions avant de publier un chiffre.**
> 1. **Quel résumé** ? (moyenne, médiane, centile : lequel répond à la question ?)
> 2. **Quelle dispersion** ? (écart-type, quartiles : le chiffre est-il représentatif ?)
> 3. **Quelle base** ? (population, échantillon : comment les observations sont-elles arrivées dans mon fichier ?)
> 4. **Quelle précision** ? (intervalle de confiance, taille d'échantillon)
> 5. **Quelle explication** ? (corrélation ou causalité : quels facteurs de confusion ai-je écartés ?)

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (résumer un panier, moyennes qui trompent, Excel contre pandas, quelle loi pour quoi, simuler un échantillonnage, intervalles de confiance et biais, corrélation et confusion, mathématiques du quotidien) et exercices 1.1 à 1.14.

Le chapitre 2 aborde le premier outil du quotidien de l'analyste : **Excel**. Vous y retrouverez les résumés de ce chapitre (moyennes, quartiles, pourcentages) sous forme de formules, puis les tableaux croisés dynamiques et Power Query pour importer et transformer des données.
