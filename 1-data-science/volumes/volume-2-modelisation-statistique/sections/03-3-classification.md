## 3.3 Classification non supervisée

> 💡 **Intuition.** Yasmine a devant elle un millier de clientes et voudrait savoir « qui ressemble à qui ». On ne lui a donné aucune étiquette (« cliente fidèle », « cliente de passage ») : on veut que ce soient **les données elles-mêmes** qui proposent des groupes. C'est la **classification non supervisée** (*clustering*) : regrouper les individus de façon que ceux d'un même groupe se ressemblent plus entre eux qu'avec ceux des autres groupes. Deux familles de méthodes, simples et complémentaires : les **k-means** (on fixe le nombre de groupes et on optimise) et la **classification hiérarchique** (on construit un arbre de fusions successives).

> ⚠️ **Avertissement de départ.** Un algorithme de classification **rend toujours des groupes**, même quand il n'y en a aucun. Donnez-lui un nuage uniforme, il le découpera en morceaux avec le même aplomb. Tout ce que nous apprendrons dans cette section — choisir le nombre de groupes, mesurer leur qualité, tester leur stabilité — sert à répondre à la vraie question : *ces groupes existent-ils, ou est-ce moi qui les ai tracés ?*

### 3.3.1 Ressembler, c'est être proche : la notion de distance

Un groupe, c'est un ensemble de points **proches**. Il faut donc définir « proche ». La distance la plus courante est la distance **euclidienne** : pour deux clientes décrites par $p$ variables $\mathbf x$ et $\mathbf y$,

$$d(\mathbf x,\mathbf y)=\sqrt{\sum_{j=1}^p(x_j-y_j)^2}.$$

Comme en ACP (section 3.1.5), **les unités comptent** : si le panier est en DT et le nombre de commandes en unités, la distance sera dominée par le panier. On **standardise** donc presque toujours les variables avant de classer. Autre limite : la distance euclidienne n'a de sens que pour des variables **numériques**. Pour des variables mixtes (numériques et qualitatives), on utilise des distances adaptées (par exemple celle de Gower) ; pour des variables qualitatives pures, on peut passer par l'analyse des correspondances multiples (section 3.4).

### 3.3.2 Les k-means

**L'objectif.** On cherche à découper $n$ points en $k$ groupes $C_1,\dots,C_k$ de centres (moyennes) $\boldsymbol\mu_1,\dots,\boldsymbol\mu_k$ de façon à minimiser la **variance intra-groupe** (aussi appelée inertie intra-classe) :

$$W(C,\boldsymbol\mu)=\sum_{j=1}^k\sum_{i\in C_j}\|\mathbf x_i-\boldsymbol\mu_j\|^2.$$

Trouver la partition qui minimise $W$ est un problème difficile (il y a un nombre astronomique de partitions possibles) ; on le résout **approximativement** par l'algorithme de **Lloyd**, qui alterne deux étapes simples :

1. **Affectation** : chaque point rejoint le groupe dont le centre est le plus proche.
2. **Mise à jour** : chaque centre est remplacé par la **moyenne** des points de son groupe.

On répète jusqu'à ce que plus aucun point ne change de groupe.

**Un exemple à la main.** Six clientes décrites par une seule variable (leur panier moyen, en dizaines de DT) : $1,\ 2,\ 4,\ 9,\ 11,\ 12$. On veut $k=2$ groupes et on choisit, au hasard, les centres initiaux $\mu_1=1$ et $\mu_2=4$.

- *Affectation 1.* Les points $1$ et $2$ sont plus proches de $\mu_1=1$ ; le point $4$ est son propre centre ; $9$, $11$ et $12$ sont plus proches de $4$ que de $1$. Groupes : $\{1,2\}$ et $\{4,9,11,12\}$.
- *Mise à jour 1.* Les nouvelles moyennes sont $\mu_1=1{,}5$ et $\mu_2=(4+9+11+12)/4=9$.
- *Affectation 2.* Le point $4$ est maintenant à $2{,}5$ de $\mu_1$ et à $5$ de $\mu_2$ : **il change de groupe**. Groupes : $\{1,2,4\}$ et $\{9,11,12\}$.
- *Mise à jour 2.* Moyennes : $\mu_1=7/3\approx2{,}33$ et $\mu_2=32/3\approx10{,}67$.
- *Affectation 3.* Plus personne ne change : l'algorithme s'arrête.

Suivons la variance intra-groupe $W$ : avec les centres de départ $(1;\ 4)$ et les groupes $\{1,2\},\{4,9,11,12\}$, $W=(0+1)+(0+25+49+64)=139$ ; après la première mise à jour (centres $1{,}5$ et $9$), $W=0{,}5+38=38{,}5$ ; après la deuxième affectation, $W=19{,}75$ ; après la deuxième mise à jour, $W=28/3\approx9{,}33$. **$W$ n'a fait que diminuer** : $139\to38{,}5\to19{,}75\to9{,}33$.

Le code suivant écrit l'algorithme et suit $W$ à chaque étape :

```python
import numpy as np
import pandas as pd

x = np.array([1.0, 2.0, 4.0, 9.0, 11.0, 12.0])
centres = np.array([1.0, 4.0])

for tour in range(1, 6):
    groupes = np.abs(x[:, None] - centres[None, :]).argmin(axis=1)           # affectation
    W = sum(((x[groupes == j] - centres[j]) ** 2).sum() for j in range(2))   # inertie avec les centres actuels
    nouveaux = np.array([x[groupes == j].mean() for j in range(2)])           # mise à jour
    W_apres = sum(((x[groupes == j] - nouveaux[j]) ** 2).sum() for j in range(2))
    print(f"tour {tour} : groupes = {groupes.tolist()}, W avant mise à jour = {W:.2f}, après = {W_apres:.2f}, centres = {nouveaux.round(2).tolist()}")
    if np.allclose(nouveaux, centres):
        print("convergence")
        break
    centres = nouveaux
```
<!--sortie-->
```text
tour 1 : groupes = [0, 0, 1, 1, 1, 1], W avant mise à jour = 139.00, après = 38.50, centres = [1.5, 9.0]
tour 2 : groupes = [0, 0, 0, 1, 1, 1], W avant mise à jour = 19.75, après = 9.33, centres = [2.33, 10.67]
tour 3 : groupes = [0, 0, 0, 1, 1, 1], W avant mise à jour = 9.33, après = 9.33, centres = [2.33, 10.67]
convergence
```

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

**Les centres de départ : k-means++ et redémarrages.** Deux précautions pour éviter les mauvais minima locaux. D'abord, **plusieurs départs aléatoires** (on garde la solution de plus petit $W$). Ensuite, l'initialisation **k-means++** : le premier centre est tiré au hasard parmi les points, puis chaque centre suivant est tiré avec une probabilité proportionnelle au **carré de la distance** au centre le plus proche déjà choisi. Les centres de départ sont ainsi bien étalés. Voici l'algorithme complet en NumPy :

```python
def kmeans(X, k, rng, n_init=10, max_iter=100):
    """k-means (algorithme de Lloyd, initialisation k-means++, n_init redémarrages)."""
    meilleur = None
    for _ in range(n_init):
        # initialisation k-means++
        centres = [X[rng.integers(len(X))]]
        for _ in range(k - 1):
            d2 = ((X[:, None, :] - np.array(centres)[None, :, :]) ** 2).sum(axis=2).min(axis=1)
            centres.append(X[rng.choice(len(X), p=d2 / d2.sum())])
        centres = np.array(centres)
        for iteration in range(max_iter):
            d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
            groupes = d.argmin(axis=1)                                                  # affectation
            nouveaux = np.array([X[groupes == j].mean(axis=0) if (groupes == j).any() else centres[j] for j in range(k)])
            if np.allclose(nouveaux, centres):
                break
            centres = nouveaux                                                          # mise à jour
        W = ((X - centres[groupes]) ** 2).sum()
        if meilleur is None or W < meilleur["W"]:
            meilleur = {"W": W, "groupes": groupes, "centres": centres, "iterations": iteration + 1}
    return meilleur
```

**Un jeu de données avec de vrais groupes.** Pour voir l'algorithme réussir, il faut des données qui **contiennent** des groupes. Simulons (graine fixée) 600 clientes issues de trois profils distincts, décrites par leur nombre de commandes annuel et leur panier moyen :

- les **occasionnelles** (300) : peu de commandes, petit panier ;
- les **fidèles** (200) : beaucoup de commandes, panier moyen ;
- les **cadeaux** (100) : peu de commandes mais très gros panier (offrir un margoum).

```python
rng = np.random.default_rng(11)
profils = {"occasionnelles": (300, (1.5, 35), (0.7, 8)),
           "fidèles": (200, (6.0, 50), (1.4, 10)),
           "cadeaux": (100, (3.0, 110), (0.9, 15))}
blocs, vrais = [], []
for numero, (nom, (n_p, moyennes, ecarts)) in enumerate(profils.items()):
    blocs.append(rng.normal(moyennes, ecarts, size=(n_p, 2)))
    vrais += [numero] * n_p
sim = np.vstack(blocs)
sim[:, 0] = np.clip(sim[:, 0], 0, None)
vrais = np.array(vrais)
Zs = (sim - sim.mean(axis=0)) / sim.std(axis=0)             # on standardise

resultat = kmeans(Zs, 3, np.random.default_rng(0))
print("inertie intra-groupe W :", round(resultat["W"], 1))
print("itérations de la meilleure exécution :", resultat["iterations"])
print("effectifs des groupes trouvés :", np.bincount(resultat["groupes"]).tolist())

# comparaison avec scikit-learn
from sklearn.cluster import KMeans
km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Zs)
print("inertie scikit-learn :", round(km.inertia_, 1))

# accord avec les vrais profils (indice de Rand ajusté : 1 = partitions identiques, 0 = accord du hasard)
from sklearn.metrics import adjusted_rand_score
print("indice de Rand ajusté (k-means de ce chapitre vs vrais profils) :", round(adjusted_rand_score(vrais, resultat["groupes"]), 3))
```
<!--sortie-->
```text
inertie intra-groupe W : 188.1
itérations de la meilleure exécution : 6
effectifs des groupes trouvés : [99, 191, 310]
inertie scikit-learn : 188.1
indice de Rand ajusté (k-means de ce chapitre vs vrais profils) : 0.941
```

Notre implémentation trouve **exactement** la même inertie que celle de `scikit-learn` (188,1). Les effectifs trouvés ($99$, $191$ et $310$) sont proches des vrais ($100$, $200$ et $300$) et l'accord avec les profils programmés est excellent ($\mathrm{ARI}\approx0{,}94$). Il n'est pas parfait, et ne le sera jamais : les nuages des « occasionnelles » et des « fidèles » se chevauchent un peu, et les clientes situées à la frontière sont inévitablement rangées au hasard de leur position.

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

*À la main, sur nos six clientes* ($\{1,2,4\}$ et $\{9,11,12\}$) : pour le point $4$, $a=(|4-1|+|4-2|)/2=2{,}5$ et $b=(|4-9|+|4-11|+|4-12|)/3=20/3\approx6{,}67$, donc $s(4)=(6{,}67-2{,}5)/6{,}67=0{,}625$. Vérifions avec une fonction écrite à la main, puis avec la bibliothèque.

```python
def silhouette_points(X, groupes):
    """Silhouette de chaque point (distances euclidiennes)."""
    D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))
    n = len(X)
    s = np.zeros(n)
    for i in range(n):
        propre = groupes == groupes[i]
        if propre.sum() == 1:
            continue                                              # groupe d'un seul point : silhouette 0 par convention
        a = D[i, propre].sum() / (propre.sum() - 1)               # on exclut la distance de i à lui-même (0)
        b = min(D[i, groupes == g].mean() for g in set(groupes) if g != groupes[i])
        s[i] = (b - a) / max(a, b)
    return s

from sklearn.metrics import silhouette_score
x2 = x.reshape(-1, 1)
g = np.array([0, 0, 0, 1, 1, 1])
print("silhouette à la main de chaque point :", silhouette_points(x2, g).round(3))
print("silhouette moyenne (à la main)       :", silhouette_points(x2, g).mean().round(4))
print("silhouette moyenne (scikit-learn)    :", round(silhouette_score(x2, g), 4))
```
<!--sortie-->
```text
silhouette à la main de chaque point : [0.793 0.827 0.625 0.625 0.827 0.793]
silhouette moyenne (à la main)       : 0.7483
silhouette moyenne (scikit-learn)    : 0.7483
```

Appliquons les deux outils aux **trois groupes simulés** : le bon nombre est connu, c'est 3. Sachons-nous le retrouver ?

```python
lignes = []
for k in range(1, 8):
    r = kmeans(Zs, k, np.random.default_rng(0))
    sil = silhouette_score(Zs, r["groupes"]) if k > 1 else np.nan
    lignes.append({"k": k, "W": r["W"], "silhouette moyenne": sil})
tab_sim = pd.DataFrame(lignes).set_index("k")
print(tab_sim.round(3).to_string())
```
<!--sortie-->
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

Deux lectures concordantes. La **variance intra-groupe** s'effondre de $1\,200$ à $607$ puis à $188$ quand on passe de $1$ à $2$ puis à $3$ groupes (pour $k=1$, $W=n\times p=600\times2=1\,200$ puisque les variables sont standardisées), puis ne décroît plus que lentement : le **coude** est net en $k=3$. La **silhouette moyenne** atteint son maximum en $k=3$ ($0{,}676$) et chute ensuite. Les deux outils retrouvent le bon nombre de groupes. Pour interpréter une silhouette moyenne, on utilise des repères conventionnels (Kaufman et Rousseeuw) : au-dessus de $0{,}5$, la structure est réelle ; entre $0{,}25$ et $0{,}5$, elle est faible ; en dessous de $0{,}25$, on ne peut pas dire qu'il y ait une structure. Ces repères restent **indicatifs** : des variables très asymétriques produisent des silhouettes élevées même sans aucun groupe, et l'on ne peut interpréter une silhouette qu'en la comparant à celle d'un nuage témoin sans structure (voir l'exercice 12).

![Choix du nombre de groupes : variance intra-groupe (le coude) et silhouette moyenne, pour les clientes simulées avec trois vrais profils et pour les clientes réelles de Dar Jasmin.](figures/ch03-choix-k.png)

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

```python
from scipy.cluster.hierarchy import linkage

pts = np.array([[0.0], [1.0], [4.0], [6.0], [11.0]])
for methode in ["single", "complete"]:
    Zlien = linkage(pts, method=methode)
    print(f"critère {methode} : hauteurs des fusions =", Zlien[:, 2].round(2).tolist())
```
<!--sortie-->
```text
critère single : hauteurs des fusions = [1.0, 2.0, 3.0, 5.0]
critère complete : hauteurs des fusions = [1.0, 2.0, 6.0, 11.0]
```

Les hauteurs de fusion confirment le calcul à la main : $1,\,2,\,3,\,5$ pour le critère simple et $1,\,2,\,6,\,11$ pour le critère complet. Le **dendrogramme** dessine cet arbre, la hauteur de chaque fusion étant la distance à laquelle elle s'est produite. **Couper l'arbre** à une hauteur donnée fournit une partition : plus on coupe bas, plus il y a de groupes.

> 💡 **Lire un dendrogramme.** Une longue branche verticale avant une fusion signale que deux groupes **bien séparés** ont été réunis de force : c'est là qu'il faut couper. Si toutes les fusions se font à des hauteurs graduellement croissantes (pas de saut), c'est que les données ne contiennent pas de groupes nets.

Appliquons-le aux 600 clientes simulées (critère de Ward, variables standardisées), et comparons la partition à trois groupes ainsi obtenue à celle des k-means. (Pour le dessin, nous ne représenterons que 40 clientes : un dendrogramme de 600 feuilles serait illisible.)

```python
from scipy.cluster.hierarchy import fcluster, cophenet
from scipy.spatial.distance import pdist

L = linkage(Zs, method="ward")
hier3 = fcluster(L, t=3, criterion="maxclust") - 1
print("hauteurs des 4 dernières fusions (Ward) :", L[-4:, 2].round(1).tolist())
print("effectifs des 3 groupes hiérarchiques    :", np.bincount(hier3).tolist())
print("ARI hiérarchique (Ward) vs vrais profils :", round(adjusted_rand_score(vrais, hier3), 3))
print("ARI k-means vs hiérarchique              :", round(adjusted_rand_score(resultat["groupes"], hier3), 3))
c_corr, _ = cophenet(L, pdist(Zs))
print("corrélation cophénétique (fidélité de l'arbre aux distances) :", round(c_corr, 3))
```
<!--sortie-->
```text
hauteurs des 4 dernières fusions (Ward) : [6.1, 9.3, 29.1, 34.3]
effectifs des 3 groupes hiérarchiques    : [304, 99, 197]
ARI hiérarchique (Ward) vs vrais profils : 0.964
ARI k-means vs hiérarchique              : 0.965
corrélation cophénétique (fidélité de l'arbre aux distances) : 0.82
```

Les **deux dernières fusions** ont lieu à des hauteurs de $29{,}1$ et $34{,}3$, contre $9{,}3$ et $6{,}1$ pour les deux précédentes : l'arbre fait un **grand saut** avant de passer de trois groupes à deux, puis à un. C'est le signe qu'il y a trois groupes. La coupe à trois groupes redonne les trois profils (ARI de $0{,}96$ contre les vrais profils) et coïncide presque avec les k-means ($0{,}97$) : sur des groupes aussi bien séparés, les deux méthodes s'accordent. La corrélation cophénétique de $0{,}82$ indique que l'arbre est une bonne représentation des distances.

> 📐 **La corrélation cophénétique.** La *distance cophénétique* de deux points est la hauteur à laquelle ils sont fusionnés dans l'arbre. La corrélation entre ces distances et les vraies distances mesure **dans quelle mesure l'arbre est fidèle** aux données : proche de 1, l'arbre résume bien les distances ; faible, il les déforme.

![Dendrogramme de 40 clientes simulées (critère de Ward). La ligne en pointillés coupe l'arbre en trois groupes, colorés ; on remarque les deux fusions finales, très hautes, par rapport aux précédentes.](figures/ch03-dendrogramme.png)

**k-means ou hiérarchique ?** Les k-means passent très bien à l'échelle (des millions de points), mais exigent $k$ à l'avance et ne trouvent que des groupes « arrondis ». La classification hiérarchique donne une vue **à toutes les échelles** et ne dépend pas d'une initialisation, mais elle exige de stocker les $n^2/2$ distances (elle ne dépasse guère quelques dizaines de milliers de points) et ses fusions sont définitives : une erreur précoce ne se corrige jamais.

### 3.3.5 Une segmentation honnête des clientes de Dar Jasmin

Passons aux **vraies** clientes (celles du fichier `clients.csv`, qui sont simulées mais **sans** segments programmés, comme dans la plupart des situations réelles). Nous décrivons chaque cliente par quatre variables : nombre de commandes par an, panier moyen, durée de la relation et âge. On écarte la dépense annuelle (elle est quasiment le produit de deux autres variables), et les clientes sans commande (panier nul).

```python
c = pd.read_csv("donnees/clients.csv")
act = c[c["nb_commandes_an"] > 0].copy()
var = ["nb_commandes_an", "panier_moyen", "duree_mois", "age"]
Zc = ((act[var] - act[var].mean()) / act[var].std()).to_numpy()
print("clientes retenues :", len(act), "sur", len(c))

lignes = []
for k in range(1, 9):
    r = kmeans(Zc, k, np.random.default_rng(0), n_init=5)
    sil = silhouette_score(Zc, r["groupes"]) if k > 1 else np.nan
    lignes.append({"k": k, "W": r["W"], "silhouette moyenne": sil})
tab_c = pd.DataFrame(lignes).set_index("k")
print(tab_c.round(3).to_string())
```
<!--sortie-->
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

```python
r4 = kmeans(Zc, 4, np.random.default_rng(0), n_init=10)
act["segment"] = r4["groupes"]
profil = act.groupby("segment").agg(effectif=("id_client", "size"), commandes=("nb_commandes_an", "mean"),
                                    panier=("panier_moyen", "mean"), duree=("duree_mois", "mean"), age=("age", "mean")).round(1)
profil["part"] = (100 * profil["effectif"] / len(act)).round(0)
print(profil.sort_values("panier").to_string())
```
<!--sortie-->
```text
         effectif  commandes  panier  duree   age  part
segment                                                
3             695        3.2    46.8   16.8  28.8  40.0
1             282        4.0    63.0   52.9  36.6  16.0
2             237       11.2    67.9   20.8  34.3  14.0
0             526        3.4    76.4   17.5  45.4  30.0
```

Quatre profils lisibles se dégagent, pour peu qu'on les nomme avec prudence :

- **Segment 3** (40 % des clientes) : les plus **jeunes** (29 ans en moyenne) au **plus petit panier** (47 DT) ;
- **Segment 0** (30 %) : les plus **âgées** (45 ans) au **plus gros panier** (76 DT) ;
- **Segment 2** (14 %) : les **habituées**, avec 11 commandes par an en moyenne, contre 3 à 4 pour les autres ;
- **Segment 1** (16 %) : les **anciennes**, dont la relation dure en moyenne 53 mois, contre 17 à 21 pour les autres.

Ces portraits sont **utiles** (on n'enverra pas le même message à une étudiante et à une cliente de longue date), mais ils décrivent des *tendances*, pas des types : chaque segment contient des clientes très variées.

Il reste à tester si ces segments sont **stables** : si l'on tire d'autres clientes dans la même population, retrouve-t-on les mêmes groupes ? On ré-estime les k-means sur 30 échantillons bootstrap (volume I, section 3.3.5), on range **toutes** les clientes d'origine dans le groupe du centre le plus proche, et on compare à la partition de référence avec l'ARI.

```python
def stabilite(X, k, ref, rng, B=30):
    ari = []
    for _ in range(B):
        idx = rng.integers(0, len(X), len(X))
        r = kmeans(X[idx], k, rng, n_init=3)
        d = ((X[:, None, :] - r["centres"][None, :, :]) ** 2).sum(axis=2)
        ari.append(adjusted_rand_score(ref, d.argmin(axis=1)))
    return np.mean(ari), np.min(ari)

m_sim, mn_sim = stabilite(Zs, 3, resultat["groupes"], np.random.default_rng(1))
m_c, mn_c = stabilite(Zc, 4, r4["groupes"], np.random.default_rng(1))
print(f"clientes simulées avec vrais groupes (k=3) : ARI moyen = {m_sim:.3f}, minimum = {mn_sim:.3f}")
print(f"clientes réelles (k=4)                     : ARI moyen = {m_c:.3f}, minimum = {mn_c:.3f}")
```
<!--sortie-->
```text
clientes simulées avec vrais groupes (k=3) : ARI moyen = 0.994, minimum = 0.985
clientes réelles (k=4)                     : ARI moyen = 0.864, minimum = 0.510
```

Les clientes simulées avec de vrais groupes donnent une stabilité **quasi parfaite** (ARI moyen $0{,}994$, minimum $0{,}985$ : on retrouve la même partition quel que soit l'échantillon). Sur les clientes réelles, la stabilité est **honorable en moyenne** ($0{,}86$) mais le **pire cas** est mauvais ($0{,}51$) : sur certains échantillons, le découpage est très différent de la référence.

> ⚠️ **Stabilité n'est pas existence.** Une partition peut être reproductible sans correspondre à des groupes réels : avec 1 740 clientes, les k-means retrouvent à peu près les mêmes quatre « tranches » à chaque tirage, comme un découpeur de gâteau qui poserait toujours son couteau aux mêmes endroits. La stabilité est une condition **nécessaire** (une partition instable est sûrement arbitraire), jamais **suffisante**. C'est pourquoi on la combine avec la silhouette et le coude.

![Les clientes de Dar Jasmin (variables standardisées) projetées sur les deux premières composantes principales, colorées par segment k-means (k = 4). Les segments se touchent : ils découpent un nuage continu.](figures/ch03-segments-clients.png)

> 🧪 **Révélation.** Aucun segment n'avait été programmé dans ces données : les variables ont été générées indépendamment de toute notion de « type de cliente ». Les k-means ont pourtant rendu quatre groupes, tout aussi sérieux en apparence que les trois profils simulés. Seuls les **indicateurs** (silhouette inférieure à $0{,}25$, absence de coude, stabilité inégale dans le pire cas) pouvaient nous avertir qu'ils n'étaient pas réels. Voilà pourquoi on ne livre jamais une segmentation sans ces diagnostics.

### 3.3.6 Les pièges de la classification

> ⚠️ **1. Les k-means supposent des groupes « arrondis ».** Comme ils minimisent des distances à des centres, ils découpent l'espace en polyèdres et échouent sur des formes allongées, incurvées ou de tailles très inégales. La classification hiérarchique à lien simple, au contraire, suit les chaînes de points voisins. Exemple classique, ci-dessous : deux « croissants » de lune.

```python
from sklearn.datasets import make_moons
from sklearn.cluster import AgglomerativeClustering

lune, vrai_lune = make_moons(n_samples=300, noise=0.07, random_state=0)
km_lune = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(lune)
simple_lune = AgglomerativeClustering(n_clusters=2, linkage="single").fit_predict(lune)
print("ARI k-means           :", round(adjusted_rand_score(vrai_lune, km_lune), 3))
print("ARI lien simple       :", round(adjusted_rand_score(vrai_lune, simple_lune), 3))
```
<!--sortie-->
```text
ARI k-means           : 0.234
ARI lien simple       : 1.0
```

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
