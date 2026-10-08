## 2.2 Tableau : feuilles, tableaux de bord, partage

Tableau est un outil de visualisation né de l'**exploration** : on glisse des champs sur une feuille, le graphique se dessine, on le modifie, on en essaie un autre. L'approche est symétrique de celle de la section 2.1 : au lieu de **construire le modèle puis dessiner**, on **dessine pour comprendre**, et le modèle suit. Cette section présente les idées de Tableau (les **marques** et leurs canaux, les **calculs de table**, les **niveaux de détail**, les tableaux de bord et leur partage), avec le même réflexe qu'avant : reproduire chaque résultat en pandas pour le vérifier.

> 🧭 **Même précaution.** Tableau est un produit commercial **non exécuté** ici : nous décrivons ses **notions**, pas ses menus, qui changent d'une version à l'autre et sont à vérifier dans la documentation de la vôtre. Les figures sont des maquettes calculées ou dessinées avec matplotlib, jamais des captures.

### 2.2.1 Feuilles, marques et canaux visuels

Une **feuille** est un graphique. Elle se construit en déposant des **champs** sur des **étagères**. Deux familles de champs existent :

- les **dimensions**, qui **découpent** (catégorie, canal, mois, région) ;
- les **mesures**, qui **comptent** (chiffre d'affaires, quantité, marge).

Les champs déposés sur les étagères *Colonnes* et *Lignes* fixent la **structure** de la feuille ; ceux déposés sur la carte des **marques** fixent l'**apparence** de chaque mark (un point, une barre, une ligne, un carré). Les canaux de la carte des marques sont ceux que vous connaissez : la **position**, la **couleur**, la **taille**, une **étiquette**, le **détail** (qui multiplie les marques sans les colorier) et l'**infobulle**. C'est exactement la grammaire des graphiques du chapitre 1 (section 1.1) : on **encode** une variable de la table par un canal visuel, et l'on choisit le canal selon la précision avec laquelle l'œil le lit (la position est lue le plus précisément, la taille et la couleur beaucoup moins).

| Champ déposé… | …sur | Effet dans la feuille |
|---|---|---|
| `categorie` (dimension) | Lignes | une ligne de marques par catégorie |
| `canal` (dimension) | Colonnes | une colonne de marques par canal |
| `montant` (mesure, somme) | Couleur | l'intensité de chaque case dépend du chiffre d'affaires |
| `montant` (mesure, somme) | Taille | l'aire de chaque cercle dépend du chiffre d'affaires |
| `id_commande` (dimension) | Détail | une marque par commande, sans couleur supplémentaire |

La « feuille » de la première ligne de ce tableau est, en pandas, un **tableau croisé** : une dimension en lignes, une en colonnes, une mesure agrégée dans les cases.

```python
feuille = v25.pivot_table(index="categorie", columns="canal", values="montant", aggfunc="sum")
print((feuille / 1000).round(0).to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux   Site
categorie                           
Bien-être       49.0     14.0   55.0
Cuisine         99.0     25.0  110.0
Décoration     112.0     28.0  119.0
Jardin         149.0     39.0  166.0
Maison         129.0     35.0  141.0
Papeterie       24.0      6.0   27.0
```

La même feuille, projetée sur trois canaux visuels différents, donne trois lectures.

![Une même feuille (chiffre d'affaires 2025 par catégorie et par canal) encodée de trois façons : la position, la couleur et la taille. Maquette dessinée avec matplotlib, pas une capture de Tableau.](figures/ch02-marques.png)

```python hide
O.fig_marques(d)
```
<!--sortie-->
```text
figure : ch02-marques.png
```

La position (barres) permet de **comparer précisément** ; la couleur (carte de chaleur) montre le **motif d'ensemble** mais ne se lit pas au chiffre près, d'où les valeurs écrites dans les cases ; la taille (cercles proportionnels) est la plus approximative. L'exercice de l'analyste est de choisir **le canal qui correspond à la question**, pas celui que l'outil propose par défaut. Ici, la question de la gérante (« qu'est-ce qui vend le plus ? ») est une question de comparaison : on prend la position, on trie, et l'on garde la couleur pour une seule chose (par exemple, mettre en valeur la catégorie qui pose problème).

> 💡 **Intuition.** Dans un outil comme Tableau, **construire une feuille revient à répondre à trois questions** : qu'est-ce que je découpe (dimensions), qu'est-ce que je compte (mesures), et par quel canal visuel je montre chaque variable. Le glisser-déposer ne dispense pas de les poser.

Les champs d'une feuille ont aussi un **type de granularité** : une dimension « discrète » donne des catégories séparées (un en-tête par valeur) ; une dimension « continue » (une date, un nombre) donne un axe continu. Une date peut s'utiliser de **deux façons** : discrète (« chaque mois, tous les ans confondus ») ou continue (une ligne du temps). Choisir la mauvaise donne soit une courbe sans sens, soit un axe sans repères ; vérifiez toujours quelle est la granularité attendue.

### 2.2.2 Calculs de table et niveaux de détail

Les champs de base ne suffisent pas : on veut des parts, des cumuls, des moyennes mobiles, des rangs. Tableau offre deux mécanismes, que l'on confond souvent parce qu'ils donnent des résultats d'apparence voisine, alors que **leur logique est différente**.

#### Les calculs de table : sur le résultat affiché

Un **calcul de table** s'applique **à ce qui est déjà affiché**, au tableau agrégé que la feuille vient de calculer : « part du total », « cumul », « moyenne mobile », « rang », « différence avec la ligne précédente ». Il dépend donc de la **structure** de la feuille : si l'on change les dimensions, il se recalcule autrement. Voici les quatre calculs sur les catégories de la boutique.

```python
t = v25.groupby("categorie")["montant"].sum().sort_values(ascending=False).to_frame("ca")
t["pct_total"] = t["ca"] / t["ca"].sum() * 100
t["cumul_pct"] = t["pct_total"].cumsum()
t["rang"] = t["ca"].rank(ascending=False).astype(int)
print(t.round(1).to_string())
```
<!--sortie-->
```text
                  ca  pct_total  cumul_pct  rang
categorie                                       
Jardin      353954.6       26.7       26.7     1
Maison      304614.0       23.0       49.7     2
Décoration  258742.3       19.5       69.2     3
Cuisine     233312.6       17.6       86.9     4
Bien-être   117510.8        8.9       95.7     5
Papeterie    56629.3        4.3      100.0     6
```

On lit tout de suite que **Jardin pèse 26,7 %** du chiffre d'affaires 2025, que **les trois premières catégories en font 69,2 %**, et que Papeterie, avec 4,3 %, ferme la marche. Chaque colonne est un calcul de table différent ; remarquez que le **cumul** n'a de sens que si l'ordre est celui du tri (sinon, il additionne dans un ordre arbitraire), et que le **rang** dépend du sens du tri choisi. Ce sont ces dépendances qu'il faut vérifier quand on pose un calcul de table : *sur quelle dimension se calcule-t-il, dans quel ordre ?*

La **moyenne mobile** est le calcul de table le plus utile pour une courbe hebdomadaire bruitée : la moyenne des quatre dernières semaines.

```python
mm4 = hebdo["ca"].rolling(4).mean()
print(f"dernière semaine : {hebdo['ca'].iloc[-1]:,.0f} €  | moyenne mobile sur 4 semaines : {mm4.iloc[-1]:,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
dernière semaine : 44 168 €  | moyenne mobile sur 4 semaines : 43 018 €
```

La semaine du 22 décembre a rapporté 44 168 €, mais la moyenne des quatre dernières semaines est de 43 018 € : la moyenne mobile **lisse** le bruit, au prix d'un **retard** (elle met quelques semaines à réagir à un changement). Montrer les **deux** courbes est souvent la bonne réponse.

#### Les niveaux de détail : à une granularité choisie

Une expression de **niveau de détail** (en anglais *level of detail*, LOD) calcule une valeur **à une granularité que vous choisissez**, **indépendamment de la structure de la feuille**. Trois variantes existent : **FIXED** (on fixe la granularité : « le total par client »), **INCLUDE** (on ajoute une dimension à la feuille pour le calcul) et **EXCLUDE** (on en retire une). Le cas d'usage type est le **calcul en deux temps** : agréger à un niveau fin, puis agréger de nouveau à un niveau plus grossier.

Un exemple. « Quel est le chiffre d'affaires moyen par client ? » est une question à deux temps : on calcule d'abord le **total de chaque client**, puis on **moyenne ces totaux**. Moyenner directement les lignes de commande répondrait à une autre question (le montant moyen d'une ligne).

```python
ca_client = v25.groupby("id_client")["montant"].sum()
print(len(ca_client), "clients actifs en 2025 | moyenne", round(ca_client.mean(), 2), "€ | médiane", round(ca_client.median(), 2), "€")
print("montant moyen d'une ligne :", round(v25["montant"].mean(), 2), "€")
```
<!--sortie-->
```text
3875 clients actifs en 2025 | moyenne 341.87 € | médiane 233.21 €
montant moyen d'une ligne : 44.41 €
```

Les **3 875 clients actifs** ont dépensé en moyenne **342 €** en 2025, la médiane est de **233 €** (quelques gros clients tirent la moyenne vers le haut, comme au volume III, section 1.1) ; une ligne de commande, elle, vaut en moyenne 44 €. Le **panier moyen** de 102 € est encore autre chose : le total d'une **commande**. **Trois « moyennes » légitimes, trois granularités**, et la boutique en a besoin des trois. C'est exactement ce que les niveaux de détail permettent de nommer proprement dans l'outil.

> 💡 **Intuition.** Un calcul de table répond à « **que dit le tableau que j'ai sous les yeux ?** » (part, cumul, rang) ; un niveau de détail répond à « **que dit la table au niveau X, quoi que j'affiche ?** ». Quand un chiffre change parce que l'on a retiré une colonne de la feuille, c'est un calcul de table ; quand il ne bouge pas, c'est un niveau de détail.

Un point de méthode, enfin : les filtres n'agissent pas tous **au même moment**. Tableau applique ses opérations dans un **ordre fixe** (la documentation le résume sous le nom d'*ordre des opérations*) : par exemple, les filtres de dimension d'une feuille s'appliquent **après** un niveau de détail FIXED, ce qui peut surprendre (un filtre sur la catégorie ne change pas le « total par client » calculé en FIXED, à moins d'être défini comme filtre de contexte). L'équivalent pandas est de se demander si l'on **filtre avant ou après** le `groupby` :

```python
tous = v25.groupby("id_client")["montant"].sum()
jardin = v25[v25["categorie"] == "Jardin"].groupby("id_client")["montant"].sum()
print(len(jardin), "clients du Jardin")
print("dépense dans le Jardin :", round(jardin.mean(), 2), "€ | dépense totale :", round(tous[jardin.index].mean(), 2), "€")
```
<!--sortie-->
```text
2402 clients du Jardin
dépense dans le Jardin : 147.36 € | dépense totale : 457.93 €
```

Selon que l'on filtre la catégorie **avant** ou **après** le premier regroupement, on ne répond pas à la même question : « combien dépense un client du Jardin **en tout** ? » ou « combien dépense-t-il **dans** la catégorie Jardin ? ». Les 2 402 clients qui ont acheté dans le Jardin ont dépensé **457,93 €** en moyenne sur l'ensemble de la boutique en 2025, mais **147,36 €** dans la seule catégorie Jardin : un facteur trois. Le premier chiffre est celui d'une expression FIXED (le total du client, quoi que la feuille filtre) ; le second, celui d'un calcul sur la feuille filtrée. **Les deux sont justes, mais l'un d'eux seulement est celui que l'on attendait** ; vérifiez dans l'outil lequel s'affiche.

> ⚠️ **Piège.** Un calcul de table ou un niveau de détail qui **donne un résultat plausible** n'est pas forcément le résultat voulu. Après chaque calcul, posez-vous trois questions : sur quelle granularité ? avec quels filtres ? dans quel ordre ? Et reproduisez le chiffre d'une case en pandas.

### 2.2.3 Du classeur au tableau de bord

Les feuilles sont des briques ; le **tableau de bord** les assemble sur une page. Les outils de la famille de Tableau l'organisent avec des **conteneurs** (horizontaux ou verticaux) qui répartissent l'espace, et offrent le choix entre une **taille fixe** (la page a les dimensions voulues, elle est identique sur tous les écrans, avec des barres de défilement si l'écran est trop petit) et une taille **adaptée** (elle s'étire, mais la disposition peut s'abîmer). Pour un tableau de bord lu **sur un écran de bureau**, la taille fixe et un ordre de lecture soigné (section 2.3.4) donnent les résultats les plus prévisibles ; pour un affichage **sur téléphone**, on prépare une **mise en page dédiée**, plus étroite et plus simple, plutôt que de réduire la version de bureau.

Ce qui distingue un tableau de bord d'un ensemble de graphiques, ce sont les **actions** : cliquer sur une barre pour **filtrer** les autres feuilles, **surligner** les points apparentés, ouvrir une page de détail ou un document externe, changer un **paramètre** (par exemple, le seuil de l'alerte). Chaque action est un petit contrat avec le lecteur : « si vous cliquez ici, il se passe ceci ». Il faut le **dire** (une phrase d'instruction, un curseur visible, un bouton « effacer les filtres ») ; une interaction cachée n'existe pas pour la plupart des lecteurs.

La **connexion** aux données reprend le choix de la section 2.1.1 : une connexion **directe** interroge la source à chaque action ; un **extrait** (*extract*) est une copie compressée, plus rapide, actualisée à des heures fixes. Pour un tableau de bord hebdomadaire, l'extrait est le choix raisonnable.

Le **partage** se fait selon trois grandes formules. Un **serveur** ou un **service en ligne** de l'éditeur, avec des comptes, des groupes et des droits : c'est la voie normale en entreprise. Une **publication publique** (il existe une offre gratuite qui publie sur un site ouvert à tous) : **tout y est public**, données comprises, et l'on n'y met jamais de données de la boutique. Enfin, le **fichier** exporté (image, PDF, classeur) : pratique pour une réunion, mais figé, sans actualisation, et facile à transmettre hors de tout contrôle. On vérifie dans la documentation de sa version ce que chaque formule permet exactement, et à quelles conditions de licence.

Les **histoires** (*stories*) enchaînent plusieurs feuilles ou tableaux de bord en une séquence commentée : c'est un outil de présentation, étudié au chapitre 4 (section 4.3).

### 2.2.4 Deux philosophies, un même chemin

Les approches de Power BI et de Tableau diffèrent par leur **point de départ**, et se rejoignent très vite. L'analyste qui connaît l'une apprend l'autre en quelques semaines **à condition d'avoir compris les notions de fond**.

| Notion | Approche « modèle d'abord » (Power BI, 2.1) | Approche « exploration d'abord » (Tableau, 2.2) |
|---|---|---|
| Point de départ | le modèle de données, relié en étoile | une feuille, puis les liens entre les sources |
| Calcul réutilisable | **mesure** écrite dans le modèle | **champ calculé**, calcul de table ou niveau de détail |
| Granularité | contexte de filtres de chaque visuel | dimensions de la feuille, niveaux de détail |
| Force | cohérence de définitions entre rapports | rapidité d'exploration, souplesse visuelle |
| Risque | modèle lourd à faire évoluer | calculs dispersés dans chaque classeur |

Cette comparaison est volontairement **schématique** : les deux produits ont tellement évolué que chacun a emprunté à l'autre. Retenez-en l'essentiel : **dans les deux cas, le travail difficile est le même** : un modèle de données juste, des définitions claires, des chiffres vérifiés. Le reste (choix de couleur, disposition, interaction) relève de la conception, que nous abordons en 2.3.

> ✅ **À retenir.**
> - Une **feuille** encode des champs par des **canaux** (position, couleur, taille, détail) ; on choisit le canal selon la **question** et selon la précision de lecture.
> - Un **calcul de table** opère sur le **tableau affiché** (part, cumul, moyenne mobile, rang) et dépend de la structure de la feuille ; un **niveau de détail** opère à une **granularité choisie**, indépendamment d'elle.
> - Un chiffre plausible n'est pas forcément **le chiffre voulu** : on se demande sur quelle granularité, avec quels filtres, dans quel ordre, et on **recalcule en pandas** une case de la feuille.
> - Un tableau de bord assemble des feuilles avec des **actions** qu'il faut **annoncer** ; on partage par groupes, et une publication **publique** ne convient jamais aux données internes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3, exercices 2.4 et 2.5.
