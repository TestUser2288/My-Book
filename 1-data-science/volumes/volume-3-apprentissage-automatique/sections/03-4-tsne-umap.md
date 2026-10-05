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

```python hide
from sklearn.manifold import TSNE, trustworthiness
from sklearn.metrics import pairwise_distances
from scipy.stats import spearmanr
import umap
r = np.random.default_rng(0)
idx = r.choice(len(chiffres.data), 800, replace=False)
Xe = chiffres.data[idx] / 16.0; ye = chiffres.target[idx]
centres = lambda E: np.array([E[ye == k].mean(0) for k in range(10)])
D0c = pairwise_distances(centres(Xe))[np.triu_indices(10, 1)]
def evaluer(E):
    return round(trustworthiness(Xe, E, n_neighbors=10), 3), round(spearmanr(D0c, pairwise_distances(centres(E))[np.triu_indices(10, 1)])[0], 3)
plong = {"ACP": PCA(2).fit_transform(Xe)}
for perp in (5, 30, 100):
    plong[f"t-SNE, perplexité {perp}"] = TSNE(2, perplexity=perp, random_state=0, init="pca").fit_transform(Xe)
for nv in (5, 15, 50):
    plong[f"UMAP, {nv} voisins"] = umap.UMAP(n_neighbors=nv, random_state=0).fit_transform(Xe)
from scipy.spatial import ConvexHull
from sklearn.cluster import DBSCAN
aires = [ConvexHull(plong["t-SNE, perplexité 30"][ye == k]).volume for k in range(10)]
eff = [int((ye == k).sum()) for k in range(10)]
print("aires des 10 chiffres (t-SNE, perplexité 30) : min", round(min(aires)), "max", round(max(aires)), "| effectifs min", min(eff), "max", max(eff))
tab_pl = pd.DataFrame([{"méthode": nom, "fiabilité (k=10)": evaluer(E)[0], "fidélité des distances entre chiffres": evaluer(E)[1]} for nom, E in plong.items()])
print(tab_pl.to_string(index=False))
palette = plt.get_cmap("tab10")
def tracer(noms, nom_fichier, largeur, titres=None):
    fig, ax = plt.subplots(1, len(noms), figsize=(largeur, 3.1))
    for a, nom in zip(np.atleast_1d(ax), noms):
        E = plong[nom]
        a.scatter(E[:, 0], E[:, 1], c=ye, cmap="tab10", s=6, alpha=0.85); a.set_title(nom, fontsize=9); a.set_xticks([]); a.set_yticks([]); a.grid(False)
        for k in range(10):
            m = np.median(E[ye == k], axis=0); a.text(m[0], m[1], str(k), fontsize=9, weight="bold", ha="center", va="center", color="black")
    plt.tight_layout(); save(fig, nom_fichier)
tracer(["ACP", "t-SNE, perplexité 5", "t-SNE, perplexité 30", "t-SNE, perplexité 100"], "ch03-tsne.png", 11)
tracer(["UMAP, 5 voisins", "UMAP, 15 voisins", "UMAP, 50 voisins"], "ch03-umap.png", 8.6)
```
<!--sortie-->
```text
aires des 10 chiffres (t-SNE, perplexité 30) : min 85 max 915 | effectifs min 76 max 90
              méthode  fiabilité (k=10)  fidélité des distances entre chiffres
                  ACP             0.827                                  0.801
  t-SNE, perplexité 5             0.987                                  0.710
 t-SNE, perplexité 30             0.991                                  0.819
t-SNE, perplexité 100             0.984                                  0.836
      UMAP, 5 voisins             0.985                                  0.475
     UMAP, 15 voisins             0.987                                  0.674
     UMAP, 50 voisins             0.984                                  0.701
figure : ch03-tsne.png
figure : ch03-umap.png
```

```python hide-code
print(tab_pl.to_string(index=False))
print("aires de l'enveloppe convexe de chaque chiffre (t-SNE, perplexité 30) : de", round(min(aires)), "à", round(max(aires)), "| effectifs de", min(eff), "à", max(eff))
```
<!--sortie-->
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

```python hide
res = []
for s in range(3):
    E = TSNE(2, perplexity=30, random_state=s, init="random").fit_transform(Xe)
    res.append((E, KMeans(10, n_init=5, random_state=0).fit_predict(E)))
tab_seed = pd.DataFrame([{"graine": s, "fiabilité": round(trustworthiness(Xe, res[s][0], n_neighbors=10), 3), "ARI des 10 groupes avec les vrais chiffres": round(adjusted_rand_score(ye, res[s][1]), 3)} for s in range(3)])
print(tab_seed.to_string(index=False))
print("ARI entre les groupes des graines 0 et 1 :", round(adjusted_rand_score(res[0][1], res[1][1]), 3), "| 0 et 2 :", round(adjusted_rand_score(res[0][1], res[2][1]), 3))
fig, ax = plt.subplots(1, 3, figsize=(9.4, 3.0))
for s, a in enumerate(ax):
    a.scatter(res[s][0][:, 0], res[s][0][:, 1], c=ye, cmap="tab10", s=6, alpha=0.85); a.set_title(f"t-SNE, graine {s}", fontsize=9); a.set_xticks([]); a.set_yticks([]); a.grid(False)
plt.tight_layout(); save(fig, "ch03-tsne-graines.png")
```
<!--sortie-->
```text
 graine  fiabilité  ARI des 10 groupes avec les vrais chiffres
      0      0.991                                       0.811
      1      0.990                                       0.807
      2      0.990                                       0.793
ARI entre les groupes des graines 0 et 1 : 0.987 | 0 et 2 : 0.923
figure : ch03-tsne-graines.png
```

```python hide-code
print(tab_seed.to_string(index=False))
print("ARI entre les groupes des graines 0 et 1 :", round(adjusted_rand_score(res[0][1], res[1][1]), 3), "| 0 et 2 :", round(adjusted_rand_score(res[0][1], res[2][1]), 3))
```
<!--sortie-->
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

```python hide
sub = np.random.default_rng(3).choice(len(Z), 1000, replace=False)
Eu = umap.UMAP(n_neighbors=15, random_state=0).fit_transform(Z[sub])
lab_u = KMeans(4, n_init=10, random_state=0).fit_predict(Eu)
lab_z = KMeans(4, n_init=10, random_state=0).fit_predict(Z[sub])
print("fiabilité de UMAP sur 1 000 clients :", round(trustworthiness(Z[sub], Eu, n_neighbors=10), 3))
print("ARI avec la vérité, k-means sur les 7 variables :", round(adjusted_rand_score(c["segment_vrai"].to_numpy()[sub], lab_z), 3), "| k-means sur le plan UMAP :", round(adjusted_rand_score(c["segment_vrai"].to_numpy()[sub], lab_u), 3))
ilots = DBSCAN(eps=0.6, min_samples=10).fit_predict(Eu)
sub_c = c.iloc[sub].assign(ilot=ilots)
lignes = []
for g in sorted(set(ilots)):
    d_ = sub_c[sub_c["ilot"] == g]
    lignes.append({"îlot": "bruit" if g == -1 else g, "clients": len(d_), "segment majoritaire": int(d_["segment_vrai"].mode()[0]), "part du segment": round((d_["segment_vrai"] == d_["segment_vrai"].mode()[0]).mean(), 2),
                   "commandes (moy.)": round(d_["nb_commandes_12m"].mean(), 2), "départ à 90 j": round(d_["churn_90j"].mean(), 3)})
tab_ilots = pd.DataFrame(lignes); print(tab_ilots.to_string(index=False))
fig, ax = plt.subplots(1, 2, figsize=(8.6, 3.2))
coul = [BLEU, ORANGE, AQUA, VIOLET]; noms_seg = ["occasionnels", "fidèles", "chasseurs de promotions", "grands paniers"]
for k in range(4):
    m = c["segment_vrai"].to_numpy()[sub] == k
    ax[0].scatter(Eu[m, 0], Eu[m, 1], s=7, color=coul[k], alpha=0.8, label=noms_seg[k])
ax[0].legend(frameon=False, fontsize=7, markerscale=1.5); ax[0].set_title("Vrais segments (cachés)", fontsize=9)
sc = ax[1].scatter(Eu[:, 0], Eu[:, 1], s=7, c=c["churn_90j"].to_numpy()[sub], cmap="coolwarm", alpha=0.8); ax[1].set_title("Départ à 90 jours (non utilisé)", fontsize=9)
for a in ax: a.set_xticks([]); a.set_yticks([]); a.grid(False)
plt.tight_layout(); save(fig, "ch03-umap-clients.png")
```
<!--sortie-->
```text
fiabilité de UMAP sur 1 000 clients : 0.967
ARI avec la vérité, k-means sur les 7 variables : 0.491 | k-means sur le plan UMAP : 0.514
 îlot  clients  segment majoritaire  part du segment  commandes (moy.)  départ à 90 j
    0      135                    0             0.83              0.00          0.378
    1      673                    1             0.42              4.23          0.064
    2      192                    2             1.00              4.20          0.193
figure : ch03-umap-clients.png
```

```python hide-code
print(tab_ilots.to_string(index=False))
print("fiabilité de UMAP sur 1 000 clients :", round(trustworthiness(Z[sub], Eu, n_neighbors=10), 3))
print("ARI avec la vérité, k-means sur les 7 variables :", round(adjusted_rand_score(c["segment_vrai"].to_numpy()[sub], lab_z), 3), "| k-means sur le plan UMAP :", round(adjusted_rand_score(c["segment_vrai"].to_numpy()[sub], lab_u), 3))
```
<!--sortie-->
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
