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

```python hide
import numpy as np
from sklearn.metrics import silhouette_samples, calinski_harabasz_score, davies_bouldin_score
pts = np.array([[1.], [2.], [4.], [9.], [11.], [12.]])
lab = np.array([0, 0, 0, 1, 1, 1])
print("silhouettes :", silhouette_samples(pts, lab).round(3), "| moyenne :", silhouette_samples(pts, lab).mean().round(3))
mu = np.array([pts[lab == j].mean() for j in (0, 1)])
W = sum(((pts[lab == j] - mu[j]) ** 2).sum() for j in (0, 1)); B = sum((lab == j).sum() * (mu[j] - pts.mean()) ** 2 for j in (0, 1))
print("W =", round(W, 3), "| B =", round(B, 2), "| CH main =", round((B / 1) / (W / 4), 2), "| CH sklearn =", round(calinski_harabasz_score(pts, lab), 2))
s = np.array([np.abs(pts[lab == j] - mu[j]).mean() for j in (0, 1)])
print("s_j =", s.round(3), "| distance des centres =", round(abs(mu[0] - mu[1]), 3), "| DB main =", round((s.sum()) / abs(mu[0] - mu[1]), 3), "| DB sklearn =", round(davies_bouldin_score(pts, lab), 3))
```
<!--sortie-->
```text
silhouettes : [0.793 0.827 0.625 0.625 0.827 0.793] | moyenne : 0.748
W = 9.333 | B = 104.17 | CH main = 44.64 | CH sklearn = 44.64
s_j = [1.111 1.111] | distance des centres = 8.333 | DB main = 0.267 | DB sklearn = 0.267
```

Ces formules sont celles de `scikit-learn` (les trois résultats à la main coïncident avec la bibliothèque). Voyons ce qu'elles disent sur les 12 000 clients, pour $k$ de 2 à 8. Pour mémoire, nous utilisons la version de la bibliothèque, qui estime la silhouette sur un échantillon de 4 000 clients (le calcul exact coûte $n^2$ distances).

```python hide
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score, normalized_mutual_info_score
lignes = []
modeles = {}
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(Z)
    modeles[k] = km
    lignes.append({"k": k, "inertie": round(km.inertia_), "silhouette": round(silhouette_score(Z, km.labels_, sample_size=4000, random_state=0), 3),
                   "CH": round(calinski_harabasz_score(Z, km.labels_)), "DB": round(davies_bouldin_score(Z, km.labels_), 3),
                   "ARI_vrai": round(adjusted_rand_score(c["segment_vrai"], km.labels_), 3), "NMI_vrai": round(normalized_mutual_info_score(c["segment_vrai"], km.labels_), 3)})
critere = pd.DataFrame(lignes)
print(critere[["k", "inertie", "silhouette", "CH", "DB"]].to_string(index=False))
fig, ax = plt.subplots(1, 4, figsize=(11.5, 2.9))
for a, col, titre, couleur in zip(ax, ["inertie", "silhouette", "CH", "DB"], ["Inertie $W$ (à minimiser… mais décroît toujours)", "Silhouette moyenne (à maximiser)", "Calinski–Harabasz (à maximiser)", "Davies–Bouldin (à minimiser)"], [BLEU, ORANGE, AQUA, VIOLET]):
    a.plot(critere["k"], critere[col], "o-", color=couleur, lw=1.8)
    a.set_title(titre, fontsize=8.5); a.set_xlabel("nombre de groupes $k$")
    a.set_xticks(range(2, 9))
plt.tight_layout(); save(fig, "ch03-criteres.png")
```
<!--sortie-->
```text
 k  inertie  silhouette   CH    DB
 2    62835       0.304 4041 1.193
 3    45645       0.331 5040 1.118
 4    36775       0.284 5135 1.271
 5    32812       0.261 4678 1.311
 6    30347       0.244 4241 1.321
 7    28830       0.231 3825 1.428
 8    27500       0.226 3520 1.334
figure : ch03-criteres.png
```

```python hide-code
print(critere[["k", "inertie", "silhouette", "CH", "DB"]].to_string(index=False))
```
<!--sortie-->
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

```python hide
rng = np.random.default_rng(0)
perm = np.column_stack([rng.permutation(Z[:, j]) for j in range(Z.shape[1])])
unif = rng.uniform(Z.min(0), Z.max(0), Z.shape)
res = []
for k in (2, 3, 4, 5):
    s_reel = silhouette_score(Z, modeles[k].labels_, sample_size=4000, random_state=0)
    s_perm = silhouette_score(perm, KMeans(k, n_init=10, random_state=0).fit_predict(perm), sample_size=4000, random_state=0)
    s_unif = silhouette_score(unif, KMeans(k, n_init=10, random_state=0).fit_predict(unif), sample_size=4000, random_state=0)
    res.append({"k": k, "données réelles": round(s_reel, 3), "colonnes permutées": round(s_perm, 3), "boîte uniforme": round(s_unif, 3)})
ref_sil = pd.DataFrame(res)
print(ref_sil.to_string(index=False))
```
<!--sortie-->
```text
 k  données réelles  colonnes permutées  boîte uniforme
 2            0.304               0.180           0.225
 3            0.331               0.190           0.182
 4            0.284               0.193           0.158
 5            0.261               0.191           0.147
```

```python hide-code
print(ref_sil.to_string(index=False))
```
<!--sortie-->
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

```python hide
idx3 = rng.choice(len(Z), 3000, replace=False)
Zs = Z[idx3]
ks = list(range(1, 9))
def log_w(A, k):
    return np.log(KMeans(k, n_init=3, random_state=0).fit(A).inertia_)
lw = np.array([log_w(Zs, k) for k in ks])
B_ref = 10
def ecart(generateur):
    ref = np.zeros((B_ref, len(ks)))
    for b in range(B_ref):
        A = generateur()
        ref[b] = [log_w(A, k) for k in ks]
    g = ref.mean(0) - lw
    s = ref.std(0) * np.sqrt(1 + 1 / B_ref)
    choix = next((k for i, k in enumerate(ks[:-1]) if g[i] >= g[i + 1] - s[i + 1]), ks[-1])
    return g, s, choix
gap_perm, s_perm_, choix_perm = ecart(lambda: np.column_stack([rng.permutation(Zs[:, j]) for j in range(Zs.shape[1])]))
gap_unif, s_unif_, choix_unif = ecart(lambda: rng.uniform(Zs.min(0), Zs.max(0), Zs.shape))
tab_gap = pd.DataFrame({"k": ks, "gap (permutation)": gap_perm.round(3), "gap (uniforme)": gap_unif.round(3)})
print(tab_gap.to_string(index=False)); print("choix par la règle de Tibshirani : permutation", choix_perm, "| uniforme", choix_unif)
fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.1))
ax[0].bar(np.arange(4) - 0.27, ref_sil["données réelles"], 0.27, color=BLEU, label="données réelles")
ax[0].bar(np.arange(4), ref_sil["colonnes permutées"], 0.27, color=ORANGE, label="colonnes permutées")
ax[0].bar(np.arange(4) + 0.27, ref_sil["boîte uniforme"], 0.27, color=MUET, label="boîte uniforme")
ax[0].set_xticks(range(4)); ax[0].set_xticklabels([f"$k={k}$" for k in (2, 3, 4, 5)]); ax[0].set_ylabel("silhouette moyenne"); ax[0].legend(frameon=False, fontsize=8)
ax[0].set_title("Une silhouette se lit par rapport à sa référence", fontsize=9)
ax[1].plot(ks, gap_perm, "o-", color=ORANGE, label="référence : colonnes permutées")
ax[1].plot(ks, gap_unif, "s-", color=MUET, label="référence : boîte uniforme")
ax[1].set_xlabel("nombre de groupes $k$"); ax[1].set_ylabel("statistique de l'écart"); ax[1].legend(frameon=False, fontsize=8)
ax[1].set_title("Statistique de l'écart selon la référence", fontsize=9)
plt.tight_layout(); save(fig, "ch03-reference-gap.png")
```
<!--sortie-->
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
choix par la règle de Tibshirani : permutation 5 | uniforme 6
figure : ch03-reference-gap.png
```

```python hide-code
print(tab_gap.to_string(index=False))
print("choix (règle de Tibshirani) : permutation =", choix_perm, "| uniforme =", choix_unif)
```
<!--sortie-->
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

```python hide
def stabilite(A, k, B=15, seed=0):
    r = np.random.default_rng(seed)
    ref = KMeans(k, n_init=10, random_state=0).fit(A)
    sc = []
    for b in range(B):
        idx = r.choice(len(A), int(0.8 * len(A)), replace=False)
        km = KMeans(k, n_init=5, random_state=b).fit(A[idx])
        sc.append(adjusted_rand_score(ref.predict(A[idx]), km.labels_))
    return np.mean(sc), np.std(sc)
stab = pd.DataFrame([{"k": k, "ARI moyen": round(m, 3), "écart-type": round(s, 3)} for k in range(2, 8) for m, s in [stabilite(Z, k)]])
print(stab.to_string(index=False))
fig, ax = plt.subplots(figsize=(5.2, 3.0))
ax.errorbar(stab["k"], stab["ARI moyen"], yerr=stab["écart-type"], fmt="o-", color=BLEU, capsize=4, lw=1.8)
ax.axhline(1, color=MUET, lw=0.8, ls=":"); ax.set_xlabel("nombre de groupes $k$"); ax.set_ylabel("ARI entre sous-échantillons et référence")
ax.set_title("Stabilité de k-means selon $k$ (15 sous-échantillons à 80 %)", fontsize=9)
plt.tight_layout(); save(fig, "ch03-stabilite.png")
```
<!--sortie-->
```text
 k  ARI moyen  écart-type
 2      0.729       0.318
 3      0.996       0.004
 4      0.986       0.007
 5      0.981       0.016
 6      0.964       0.029
 7      0.782       0.120
figure : ch03-stabilite.png
```

```python hide-code
print(stab.to_string(index=False))
```
<!--sortie-->
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

```python hide
from sklearn.metrics import adjusted_rand_score
vrai = np.array([0] * 5 + [1] * 5); trouve = np.array([0] * 4 + [1] + [0] + [1] * 4)
print("ARI de l'exemple à la main :", round(adjusted_rand_score(vrai, trouve), 3))
```
<!--sortie-->
```text
ARI de l'exemple à la main : 0.28
```

Appliquons ces mesures aux découpages de 3.1.2.

```python hide-code
print(critere[["k", "ARI_vrai", "NMI_vrai"]].rename(columns={"ARI_vrai": "ARI", "NMI_vrai": "NMI"}).to_string(index=False))
ct = pd.crosstab(modeles[4].labels_, c["segment_vrai"])
print("pureté à k = 4 :", round(ct.max(axis=1).sum() / len(c), 3))
```
<!--sortie-->
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

```python hide
ct = pd.crosstab(modeles[4].labels_, c["segment_vrai"])
ct.index = [f"groupe {i}" for i in ct.index]; ct.columns = [f"vrai {j}" for j in ct.columns]
print(ct.to_string())
```
<!--sortie-->
```text
          vrai 0  vrai 1  vrai 2  vrai 3
groupe 0       5      22    2197       2
groupe 1      84    2879      23     567
groupe 2    1405      66     107     161
groupe 3    3112     590      20     760
```

```python hide-code
print(ct.to_string())
```
<!--sortie-->
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

```python hide
Xbrut = c[cols].to_numpy(dtype=float)
res_ech = []
for nom, A in [("variables standardisées (montant en log)", Z), ("montant en log, sans standardisation", X.to_numpy()), ("montant brut, sans standardisation", Xbrut)]:
    lab = KMeans(4, n_init=10, random_state=0).fit_predict(A)
    res_ech.append({"préparation": nom, "ARI avec la vérité": round(adjusted_rand_score(c["segment_vrai"], lab), 3)})
Zbruit = np.column_stack([Z, np.random.default_rng(5).normal(size=(len(Z), 5))])
lab = KMeans(4, n_init=10, random_state=0).fit_predict(Zbruit)
res_ech.append({"préparation": "standardisées + 5 variables de pur bruit", "ARI avec la vérité": round(adjusted_rand_score(c["segment_vrai"], lab), 3)})
tab_ech = pd.DataFrame(res_ech); print(tab_ech.to_string(index=False))
```
<!--sortie-->
```text
                             préparation  ARI avec la vérité
variables standardisées (montant en log)               0.487
    montant en log, sans standardisation               0.081
      montant brut, sans standardisation               0.110
standardisées + 5 variables de pur bruit               0.485
```

```python hide-code
print(tab_ech.to_string(index=False))
```
<!--sortie-->
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

```python hide
c["groupe"] = modeles[4].labels_
profil = c.groupby("groupe").agg(part=("age", lambda s: len(s) / len(c)), age=("age", "mean"), commandes=("nb_commandes_12m", "mean"), montant=("montant_12m", "mean"),
                                 recence=("recence_jours", "mean"), part_promo=("part_achats_promo", "mean"), ouverture=("taux_ouverture_email", "mean"),
                                 churn=("churn_90j", "mean"), depense_6m=("depense_6m", "mean")).round(2)
print(profil.to_string())
print("churn global :", round(c["churn_90j"].mean(), 3), "| dépense moyenne à 6 mois :", round(c["depense_6m"].mean(), 1))
prof_z = (c.groupby("groupe")[cols].mean() - c[cols].mean()) / c[cols].std()
fig, ax = plt.subplots(figsize=(6.4, 2.9))
im = ax.imshow(prof_z.to_numpy(), cmap="RdBu_r", vmin=-2, vmax=2, aspect="auto")
ax.set_xticks(range(len(cols))); ax.set_xticklabels(["âge", "commandes", "montant", "récence", "part promo", "ouverture e-mail", "promos reçues"], rotation=30, ha="right", fontsize=8)
ax.set_yticks(range(4)); ax.set_yticklabels([f"groupe {g} ({profil.loc[g, 'part']:.0%})" for g in range(4)], fontsize=8)
for i in range(4):
    for j in range(len(cols)):
        ax.text(j, i, f"{prof_z.iloc[i, j]:+.1f}", ha="center", va="center", fontsize=7.5, color="white" if abs(prof_z.iloc[i, j]) > 1.2 else "black")
ax.set_title("Profil des quatre groupes (écarts à la moyenne, en écarts-types)", fontsize=9)
fig.colorbar(im, ax=ax, fraction=0.03); plt.tight_layout(); save(fig, "ch03-profils.png")
```
<!--sortie-->
```text
        part    age  commandes  montant  recence  part_promo  ouverture  churn  depense_6m
groupe                                                                                    
0       0.19  29.59       4.28   124.03    62.15        0.75       0.57   0.20       52.37
1       0.30  43.58       7.30   372.64    39.02        0.19       0.56   0.01      168.24
2       0.14  35.34       0.11     3.49   363.85        0.19       0.29   0.41       22.16
3       0.37  36.29       2.28   121.05    91.66        0.16       0.28   0.11       57.80
churn global : 0.14 | dépense moyenne à 6 mois : 84.3
figure : ch03-profils.png
```

```python hide-code
print(profil.to_string())
print("churn global :", round(c["churn_90j"].mean(), 3))
```
<!--sortie-->
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
