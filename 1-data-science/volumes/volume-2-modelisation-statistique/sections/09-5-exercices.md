## 9.5 Exercices du chapitre 9

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les corrigés réutilisent les fonctions définies dans les sections 9.1 à 9.4 (`haversine`, `moran`, `variogramme_empirique`, `krigeage_ordinaire`, `semis_thomas`, `ripley_K`…) : le chapitre est exécuté d'un seul tenant.

### Énoncés

**Exercice 1 ⭐ (quel type de données ?).** Pour chaque situation, dites s'il s'agit de données **géostatistiques**, **surfaciques** ou d'un **semis de points**, et nommez l'outil de ce chapitre qui répond à la question. (a) Yasmine relève la **température** à l'intérieur de 40 entrepôts de stockage répartis dans la région et veut estimer la température dans un entrepôt qu'elle n'a pas visité. (b) Elle dispose du **taux de retour de colis** de chacune des 24 gouvernorats et se demande si les gouvernorats voisins ont des taux semblables. (c) Elle a les **adresses** de tous ses clients de Sousse et se demande si elles se regroupent. (d) Un transporteur mesure le **délai de livraison** à 300 adresses et veut cartographier le délai moyen attendu sur toute la zone.

**Exercice 2 ⭐ (haversine à la main).** Calculez à la main la distance entre Tunis $(36{,}81^\circ\text{N};\,10{,}18^\circ\text{E})$ et Sousse $(35{,}83^\circ\text{N};\,10{,}61^\circ\text{E})$, en utilisant la latitude moyenne pour le facteur $\cos\varphi$. Comparez au résultat de la formule de haversine.

**Exercice 3 ⭐⭐ (Moran sur quatre zones).** Quatre zones alignées A–B–C–D (chacune voisine de la précédente et de la suivante) ont pour valeurs $1,\,2,\,3,\,4$. (a) Calculez à la main l'indice de Moran avec les poids binaires, puis avec les poids standardisés par ligne. (b) Quelle est son espérance sous l'hypothèse nulle ? (c) Il n'y a que $4!=24$ façons de ranger ces valeurs sur les zones : calculez la distribution **exacte** de $I$ et la p-valeur de l'alignement observé.

**Exercice 4 ⭐⭐ (lire un indice local).** Dans une carte, la zone $i$ a un écart à la moyenne $z_i=+12$ et la moyenne des écarts de ses voisines vaut $(Wz)_i=-8$. La variance empirique est $m_2=100$. (a) Dans quel quadrant se trouve la zone ? (b) Que vaut son indice local $I_i$ ? (c) Peut-on conclure que c'est une valeur atypique significative ? Que faudrait-il faire ?

**Exercice 5 ⭐⭐ (variogramme à la main).** Cinq mesures alignées aux abscisses 0, 1, 2, 3 et 4 km ont pour valeurs $3,\,5,\,4,\,8,\,7$. Calculez le variogramme empirique aux distances 1, 2, 3 et 4 km. Que pouvez-vous dire de la forme de la courbe et de la fiabilité de ces estimations ?

**Exercice 6 ⭐⭐ (krigeage à la main).** En dimension 1, avec le variogramme linéaire $\gamma(h)=0{,}5\,h$, on a mesuré 20 en $x=0$ et 30 en $x=4$. (a) Écrivez et résolvez le système de krigeage ordinaire pour prédire en $x=1$ ; donnez la prédiction et la variance. (b) Si les valeurs mesurées étaient 0 et 100 au lieu de 20 et 30, la variance de krigeage changerait-elle ? Pourquoi ?

**Exercice 7 ⭐⭐ (le problème de l'unité spatiale modifiable).** On construit une variable $x$ corrélée aux `ventes_hab` des 144 délégations (la graine est donnée dans le corrigé). On **agrège** ensuite les zones en blocs de $2\times2$, $3\times3$, $4\times4$ et $6\times6$ cases (moyenne par bloc). Comment évoluent la corrélation entre $x$ et les ventes, l'écart-type des ventes et l'indice de Moran ? Qu'en conclure pour l'interprétation d'une corrélation calculée sur des zones ?

**Exercice 8 ⭐⭐ (l'effet de bord sur les indices locaux).** Sur la grille $12\times12$ avec voisinage « reine », les cases ont 3 voisines (coins), 5 (bords) ou 8 (intérieur). Sans autocorrélation, la variance de l'indice local $I_i$ devrait varier comme $1/k$ où $k$ est le nombre de voisines. Vérifiez-le par simulation et expliquez pourquoi les zones de bord sont plus souvent « significatives » avec une p-valeur naïve.

**Exercice 9 ⭐⭐ (nombre efficace d'observations).** Pour un modèle SAR sur la grille $12\times12$ avec $\rho\in\{0{,}3;\,0{,}5;\,0{,}7;\,0{,}9;\,0{,}95\}$, estimez par simulation le **nombre efficace d'observations indépendantes** pour estimer une moyenne, défini par $n_{\text{eff}}=\operatorname{Var}(y_i)/\operatorname{Var}(\bar y)$. Commentez.

**Exercice 10 ⭐⭐ (cases vides).** On répartit 100 points au hasard (CSR) dans une fenêtre de $10\times10$ km, divisée en $4\times4$ cases. (a) Quelle est, à la main, la probabilité qu'une case donnée soit vide, et le nombre moyen de cases vides ? (b) Vérifiez par simulation, puis comparez au nombre de cases vides du semis agrégé de la section 9.4. Que cela dit-il ?

**Exercice 11 ⭐⭐⭐ (l'estimateur du variogramme est-il sans biais ?).** Le variogramme empirique est une moyenne de $\frac12(z_i-z_j)^2$. Montrez que $\mathbb E\big[\tfrac12(Z(s+h)-Z(s))^2\big]=\gamma(h)$ pour un processus stationnaire de moyenne $\mu$, puis vérifiez par simulation, en moyennant le variogramme empirique de 60 jeux de livraisons indépendants (même processus que 9.3) et en le comparant au variogramme **vrai** $\gamma(h)=0{,}4+1{,}0\,(1-e^{-h/12})$.

**Exercice 12 ⭐⭐⭐ (la fonction $K$ d'un processus de Thomas).** Pour un processus de Thomas de densité de centres $\kappa$ et d'étalement $\sigma$ (par coordonnée), on admet que la fonction de corrélation de paires est $g(r)=1+\dfrac{1}{4\pi\kappa\sigma^2}e^{-r^2/(4\sigma^2)}$. (a) Montrez que $K(r)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. (b) Vérifiez par simulation pour $\kappa=0{,}5$, $\mu=2$, $\sigma=0{,}4$, puis pour $\kappa=0{,}08$, $\mu=12$, $\sigma=0{,}4$. Que constatez-vous ?

### Corrigés

**Corrigé 1.** (a) **Géostatistique** : la température existe en tout point de la région et on la mesure en 40 lieux ; on veut prédire ailleurs : variogramme et **krigeage**. (b) **Surfacique** : une valeur par zone, la question est la ressemblance entre zones voisines : matrice de poids et **indice de Moran** (avec 24 zones seulement, on teste par permutations et on indique la définition du voisinage). (c) **Semis de points** : ce sont les positions qui sont le phénomène ; on les compare au hasard complet avec les quadrats, le plus proche voisin et la fonction **$K$ de Ripley**, en pensant à la densité de population qui peut varier (9.4.5). (d) **Géostatistique** : un délai défini en tout point mesuré en 300 adresses ; **variogramme et krigeage** donnent la carte du délai attendu et une carte d'incertitude.

**Corrigé 2.** $\Delta\varphi=0{,}98^\circ$ donne $0{,}98\times111{,}2\approx109{,}0$ km vers le sud. $\Delta\lambda=0{,}43^\circ$ : avec $\cos(36{,}32^\circ)\approx0{,}806$, $0{,}43\times111{,}2\times0{,}806\approx38{,}5$ km vers l'est. La distance est $\sqrt{109{,}0^2+38{,}5^2}\approx115{,}6$ km.

```python
print("haversine Tunis - Sousse :", round(float(haversine(36.81, 10.18, 35.83, 10.61)), 1), "km")
print("estimation à la main     :", round(float(np.hypot(0.98 * 111.2, 0.43 * 111.2 * np.cos(np.radians(36.32)))), 1), "km")
```
<!--sortie-->
```text
haversine Tunis - Sousse : 115.6 km
estimation à la main     : 115.6 km
```

**Corrigé 3.** (a) Les écarts à la moyenne $\bar y=2{,}5$ sont $z=(-1{,}5;-0{,}5;0{,}5;1{,}5)$ et $\sum z^2=5$. Les frontières sont A–B, B–C et C–D : produits $(-1{,}5)(-0{,}5)=0{,}75$, $(-0{,}5)(0{,}5)=-0{,}25$, $(0{,}5)(1{,}5)=0{,}75$, de somme $1{,}25$. **Poids binaires** ($S_0=6$ liens orientés) : $\sum_{ij}w_{ij}z_iz_j=2\times1{,}25=2{,}5$ et $I=\frac46\times\frac{2{,}5}{5}=\frac13$. **Poids standardisés** ($S_0=4$) : A et D n'ont qu'une voisine (poids 1), B et C deux (poids $\frac12$ chacune), donc $z^\top Wz=z_Az_B+\tfrac12z_B(z_A+z_C)+\tfrac12z_C(z_B+z_D)+z_Dz_C=0{,}75+0{,}25+0{,}25+0{,}75=2$ et $I=\frac{2}{5}=0{,}4$. (b) $\mathbb E[I]=-1/(n-1)=-\frac13$ : avec $n=4$ zones seulement, l'espérance sous le hasard est loin de zéro. (c) On énumère les 24 permutations.

```python
from itertools import permutations

W4 = std_lignes(np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float))
W4b = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float)
vals = np.array([1.0, 2, 3, 4])
print("I (poids binaires)      :", round(moran(vals, W4b), 4), "| I (poids standardisés) :", round(moran(vals, W4), 4))
toutes = np.array([moran(np.array(p), W4) for p in permutations(vals)])
print("nombre de permutations :", len(toutes), "| valeurs distinctes de I :", np.unique(toutes.round(4)).tolist())
print("moyenne de I sur les 24 permutations :", round(toutes.mean(), 4), "(= -1/(n-1) =", round(-1 / 3, 4), ")")
print("p-valeur exacte (I >= observé) :", round(float((toutes >= moran(vals, W4) - 1e-12).mean()), 4))
```
<!--sortie-->
```text
I (poids binaires)      : 0.3333 | I (poids standardisés) : 0.4
nombre de permutations : 24 | valeurs distinctes de I : [-0.9, -0.6, -0.5, -0.3, 0.0, 0.3, 0.4]
moyenne de I sur les 24 permutations : -0.3333 (= -1/(n-1) = -0.3333 )
p-valeur exacte (I >= observé) : 0.0833
```

L'espérance exacte sur les permutations est bien $-\frac13$. L'alignement observé (1, 2, 3, 4) et son image inversée (4, 3, 2, 1) sont les deux seuls arrangements qui atteignent cette valeur maximale : la p-valeur exacte est $2/24\approx0{,}083$, **supérieure à 5 %**. Avec quatre zones, aucune autocorrélation, même parfaite, ne peut être significative : c'est le prix du petit nombre de permutations.

**Corrigé 4.** (a) $z_i>0$ (zone haute) et $(Wz)_i<0$ (voisines basses) : quadrant **HL** (haute entourée de basses). (b) $I_i=\dfrac{z_i\,(Wz)_i}{m_2}=\dfrac{12\times(-8)}{100}=-0{,}96$ : négatif, car la zone s'oppose à ses voisines. (c) Non : un indice local négatif ne dit rien de sa significativité. Il faut une **permutation conditionnelle** (fixer $z_i$, mélanger les autres valeurs) pour obtenir une p-valeur, puis **corriger** pour les tests multiples (Benjamini-Hochberg), comme au 9.2.4.

**Corrigé 5.** Distance 1 : paires (3,5), (5,4), (4,8), (8,7) ; carrés des écarts 4, 1, 16, 1, total 22 ; $\hat\gamma(1)=\frac{22}{2\times4}=2{,}75$. Distance 2 : (3,4), (5,8), (4,7) ; carrés 1, 9, 9, total 19 ; $\hat\gamma(2)=\frac{19}{2\times3}\approx3{,}17$. Distance 3 : (3,8), (5,7) ; carrés 25, 4 ; $\hat\gamma(3)=\frac{29}{2\times2}=7{,}25$. Distance 4 : (3,7) ; $\hat\gamma(4)=\frac{16}{2}=8$.

```python
P5 = np.array([[0.0, 0], [1, 0], [2, 0], [3, 0], [4, 0]])
z5 = np.array([3.0, 5, 4, 8, 7])
print(variogramme_empirique(P5, z5, largeur=1.0, hmax=4.0).round(3).to_string(index=False))
```
<!--sortie-->
```text
  h  gamma  paires
1.0  2.750       4
2.0  3.167       3
3.0  7.250       2
4.0  8.000       1
```

La courbe est **croissante** (2,75 ; 3,17 ; 7,25 ; 8) et ne montre aucun palier : on ne peut pas estimer de portée. Deux raisons : il y a très peu de données, et ces valeurs montrent une **tendance** (elles augmentent avec l'abscisse), qui fait monter le variogramme (9.3.7). Surtout, le nombre de paires **diminue** avec la distance (4, 3, 2, 1) : l'estimation à 4 km repose sur **une seule paire** et n'a quasiment aucune fiabilité. C'est l'inverse de ce qui se passe en deux dimensions, où les paires lointaines sont nombreuses, mais cela rappelle qu'un variogramme se lit en regardant les effectifs.

**Corrigé 6.** (a) $\Gamma=\begin{pmatrix}0&2\\2&0\end{pmatrix}$ (car $\gamma(4)=2$) et $\gamma_0=(\gamma(1),\gamma(3))^\top=(0{,}5;\,1{,}5)^\top$. Les équations sont $2\lambda_2+m=0{,}5$, $2\lambda_1+m=1{,}5$ et $\lambda_1+\lambda_2=1$. En soustrayant, $2(\lambda_1-\lambda_2)=1$, donc $\lambda_1=0{,}75$, $\lambda_2=0{,}25$ et $m=0$. Prédiction : $0{,}75\times20+0{,}25\times30=22{,}5$, variance $\lambda^\top\gamma_0+m=0{,}75\times0{,}5+0{,}25\times1{,}5=0{,}75$. C'est l'interpolation linéaire (de 20 à 30 sur 4 km, soit 22,5 à 1 km). (b) **Non** : la variance de krigeage $\lambda^\top\gamma_0+m$ ne dépend que de la **géométrie** (les distances) et du variogramme, jamais des valeurs mesurées. Les poids sont identiques, donc la prédiction vaudrait $0{,}75\times0+0{,}25\times100=25$ et la variance resterait $0{,}75$. Le krigeage dit à quel point le *plan d'échantillonnage* est informatif, pas si les données observées sont « surprenantes ».

```python
for valeurs in ([20.0, 30.0], [0.0, 100.0]):
    pred, var, lam = krigeage_ordinaire(np.array([[0.0, 0], [4, 0]]), np.array(valeurs), np.array([[1.0, 0]]), lineaire, (0.5,))
    print("valeurs", valeurs, "-> poids", lam.ravel().round(3), "| prédiction", pred.round(3), "| variance", var.round(3))
```
<!--sortie-->
```text
valeurs [20.0, 30.0] -> poids [0.75 0.25] | prédiction [22.5] | variance [0.75]
valeurs [0.0, 100.0] -> poids [0.75 0.25] | prédiction [25.] | variance [0.75]
```

**Corrigé 7.** Nous construisons $x$ comme un mélange de `ventes_hab` standardisées et d'un autre champ SAR indépendant, puis nous agrégeons.

```python
Wr = std_lignes(contiguite_reine(12, 12))
rng7 = np.random.default_rng(5)
A7 = np.linalg.inv(np.eye(144) - 0.9 * Wr)
y7 = deleg["ventes_hab"].to_numpy()
champ = A7 @ rng7.normal(size=144)
x7 = 0.5 * (y7 - y7.mean()) / y7.std() + 0.87 * champ / champ.std()

def agrege(v, k):
    m = 12 // k
    return v.reshape(12, 12).reshape(m, k, m, k).mean(axis=(1, 3)).ravel()

lignes = []
for k in (1, 2, 3, 4, 6):
    m = 12 // k
    ya, xa = agrege(y7, k), agrege(x7, k)
    I_k = moran(ya, std_lignes(contiguite_reine(m, m))) if m >= 3 else np.nan
    lignes.append({"bloc": f"{k} x {k}", "zones": m * m, "corr(x, ventes)": np.corrcoef(xa, ya)[0, 1],
                   "ecart_type_ventes": ya.std(), "Moran_ventes": I_k, "E[I]": -1 / (m * m - 1) if m >= 3 else np.nan})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 bloc  zones  corr(x, ventes)  ecart_type_ventes  Moran_ventes   E[I]
1 x 1    144            0.597             13.468         0.621 -0.007
2 x 2     36            0.619             11.142         0.570 -0.029
3 x 3     16            0.646             10.010         0.291 -0.067
4 x 4      9            0.774              9.350        -0.054 -0.125
6 x 6      4            0.869              8.431           NaN    NaN
```

La **corrélation augmente** avec l'agrégation (de 0,60 sur les 144 zones à 0,87 sur les 4 blocs de $6\times6$), l'**écart-type** des ventes diminue (de 13,5 à 8,4 : les moyennes de blocs lissent les fluctuations) et l'**indice de Moran** chute : de 0,62 à 0,57 (blocs de $2\times2$), à 0,29 ($3\times3$, soit 16 zones) puis à $-0{,}05$ ($4\times4$, soit 9 zones), à comparer à $-0{,}125$ sous le hasard pour 9 zones : à cette échelle, l'autocorrélation a pratiquement disparu (et avec 9 zones, un test aurait de toute façon très peu de puissance). Les mêmes personnes, les mêmes ventes, trois « résultats » différents selon le découpage : c'est le **problème de l'unité spatiale modifiable** (MAUP). Une corrélation calculée sur des zones n'est vraie que pour **ce découpage** : on ne peut pas la transposer à l'échelle des individus (sophisme écologique), ni à un autre découpage, sans précaution.

**Corrigé 8.** On simule le hasard en mélangeant les valeurs de `ventes_bruit` et on calcule, pour chaque case, l'indice local $I_i=z_i(Wz)_i/m_2$.

```python
rng8 = np.random.default_rng(8)
zb = deleg["ventes_bruit"].to_numpy() - deleg["ventes_bruit"].mean()
m2 = zb @ zb / 144
perms = np.argsort(rng8.random((3000, 144)), axis=1)
Zs = zb[perms]
Ii_sim = Zs * (Zs @ Wr.T) / m2                                   # (3000, 144) : indices locaux sous H0
k_vois = contiguite_reine(12, 12).sum(axis=1)
lignes = []
for kk in (3, 5, 8):
    cols = k_vois == kk
    lignes.append({"voisines": kk, "cases": int(cols.sum()), "variance de I_i": Ii_sim[:, cols].var(), "variance x k": Ii_sim[:, cols].var() * kk})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 voisines  cases  variance de I_i  variance x k
        3      4            0.333         1.000
        5     40            0.191         0.957
        8    100            0.117         0.936
```

La variance de $I_i$ est environ **2,8 fois plus grande** pour un coin (3 voisines) que pour une case intérieure (8 voisines), à comparer au rapport théorique $8/3\approx2{,}67$ ; la colonne « variance × $k$ » est à peu près constante, ce qui confirme la loi en $1/k$ : la moyenne des voisines est plus bruitée quand il y a moins de voisines. Une zone de bord ressemble donc plus facilement à une valeur extrême par hasard, et une p-valeur calculée avec la **même** loi pour toutes les zones la déclarerait trop souvent significative. Les **permutations conditionnelles** du 9.2.4 évitent ce piège, car elles tirent exactement le bon nombre de voisines pour chaque zone. Par prudence, on examine séparément les zones de bord.

**Corrigé 9.** Pour chaque $\rho$, on simule 4 000 champs SAR et on compare la variance d'une zone à celle de la moyenne des 144 zones.

```python
rng9 = np.random.default_rng(9)
lignes = []
for rho in (0.3, 0.5, 0.7, 0.9, 0.95):
    Y9 = np.linalg.inv(np.eye(144) - rho * Wr) @ rng9.normal(size=(144, 4000))
    lignes.append({"rho": rho, "variance d'une zone": Y9.var(), "variance de la moyenne": Y9.mean(axis=0).var(), "n_eff": Y9.var() / Y9.mean(axis=0).var()})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 rho  variance d'une zone  variance de la moyenne  n_eff
0.30                1.052                   0.014 75.715
0.50                1.179                   0.028 42.577
0.70                1.555                   0.077 20.203
0.90                3.917                   0.708  5.532
0.95                8.383                   2.805  2.989
```

Le nombre efficace d'observations **s'effondre** quand $\rho$ augmente : d'environ 76 pour $\rho=0{,}3$, il tombe à 43 pour $\rho=0{,}5$, à 20 pour $\rho=0{,}7$, à 5,5 pour $\rho=0{,}9$ (la valeur de la section 9.2.5) et à 3 pour $\rho=0{,}95$. Même pour une dépendance modérée ($\rho=0{,}5$), les 144 zones n'apportent l'information que d'environ 43 observations indépendantes. C'est la raison de la surconfiance des tests usuels.

**Corrigé 10.** (a) Les cases ont une aire de $2{,}5\times2{,}5=6{,}25$ km² et l'intensité vaut $\lambda=1$ par km² : le nombre de points d'une case suit approximativement une loi de Poisson de moyenne $6{,}25$, donc $\mathbb P(\text{vide})=e^{-6{,}25}\approx0{,}0019$. Plus exactement, conditionnellement à $n=100$ points, chaque point tombe hors d'une case donnée avec la probabilité $\frac{15}{16}$ : $\mathbb P(\text{vide})=(15/16)^{100}\approx0{,}0016$. Pour 16 cases, le nombre moyen de cases vides est $16\times0{,}0016\approx0{,}025$ : sous le hasard complet, on s'attend à **ne presque jamais** voir de case vide.

```python
print("e^-6,25 =", round(float(np.exp(-6.25)), 5), "| (15/16)^100 =", round((15 / 16) ** 100, 5), "| 16 x (15/16)^100 =", round(16 * (15 / 16) ** 100, 4))
rng10 = np.random.default_rng(10)
vides = [(comptages(semis_poisson(100, rng10)) == 0).sum() for _ in range(5000)]
print("nombre moyen de cases vides sur 5000 semis CSR :", round(float(np.mean(vides)), 4), "| part des semis avec au moins une case vide :", round(float(np.mean(np.array(vides) > 0)), 4))
print("cases vides dans le semis agrégé :", int((comptages(semis["agrégé (Thomas)"]) == 0).sum()), "sur 16")
```
<!--sortie-->
```text
e^-6,25 = 0.00193 | (15/16)^100 = 0.00157 | 16 x (15/16)^100 = 0.0252
nombre moyen de cases vides sur 5000 semis CSR : 0.0226 | part des semis avec au moins une case vide : 0.0224
cases vides dans le semis agrégé : 7 sur 16
```

(b) La simulation confirme le calcul (environ 0,025 case vide en moyenne). Le semis agrégé de 9.4 a **7 cases vides sur 16** : un événement quasi impossible sous le hasard, qui est un autre visage de l'agrégation. (Attention : ce semis compte 75 points et non 100, ce qui rend les cases vides un peu plus plausibles, sans changer la conclusion.)

**Corrigé 11.** Notons $\delta=Z(s+h)-Z(s)$. Par stationnarité, $\mathbb E[Z(s+h)]=\mathbb E[Z(s)]=\mu$, donc $\mathbb E[\delta]=0$, et $\mathbb E[\delta^2]=\operatorname{Var}(\delta)$. Par définition du semi-variogramme, $\gamma(h)=\frac12\mathbb E[\delta^2]$. L'estimateur $\hat\gamma(h)$ est une moyenne de $\frac12\delta^2$ sur des paires **dont la distance est $h$** : son espérance est donc $\gamma(h)$ ; il est sans biais **à $\mu$ inconnue** (ce qui le distingue de la covariance empirique, qui exige d'estimer la moyenne). Le seul biais vient du regroupement par classes (nous comparons à $\gamma$ à la distance moyenne de la classe) et d'éventuelles tendances. Vérifions par simulation.

```python
accumule = []
for graine in range(300, 360):
    d_sim, _ = livraisons(seed=graine)
    accumule.append(variogramme_empirique(d_sim[["x", "y"]].to_numpy(), d_sim["delai_jours"].to_numpy()))
h_moy = np.mean([e["h"].to_numpy() for e in accumule], axis=0)
g_moy = np.mean([e["gamma"].to_numpy() for e in accumule], axis=0)
g_sd = np.std([e["gamma"].to_numpy() for e in accumule], axis=0, ddof=1) / np.sqrt(len(accumule))
vrai_g = gamma_exp(h_moy, 0.4, 1.0, 12.0)
print(pd.DataFrame({"h": h_moy, "gamma_moyen": g_moy, "erreur_type_moyenne": g_sd, "gamma_vrai": vrai_g, "ecart_%": 100 * (g_moy / vrai_g - 1)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
     h  gamma_moyen  erreur_type_moyenne  gamma_vrai  ecart_%
 3.324        0.632                0.011       0.642   -1.592
 7.745        0.867                0.014       0.876   -0.956
12.636        1.033                0.019       1.051   -1.751
17.593        1.164                0.022       1.169   -0.416
22.548        1.242                0.027       1.247   -0.389
27.549        1.303                0.030       1.299    0.277
32.529        1.329                0.032       1.334   -0.326
37.509        1.367                0.037       1.356    0.809
42.512        1.404                0.036       1.371    2.385
47.503        1.405                0.037       1.381    1.719
```

La moyenne sur 60 jeux colle au variogramme vrai à toutes les distances, à moins de 2,5 % près, et les écarts restent de l'ordre de l'erreur-type de la moyenne (colonne suivante) : rien ne montre de biais. Mais regardons la colonne des erreurs-types : elle **augmente avec la distance**. C'est la signature d'une corrélation forte entre classes de distance voisines et de grandes fluctuations d'un jeu à l'autre aux distances élevées : une moyenne de 60 jeux est précise, mais **un seul jeu** de données réelles est un tirage unique, d'où la dispersion observée en 9.3.3 sur les paramètres ajustés.

**Corrigé 12.** (a) Par définition, $K(r)=\int_0^r 2\pi s\,g(s)\,ds$ (le nombre moyen d'autres points à moins de $r$, divisé par $\lambda$, est l'intégrale de la fonction de corrélation de paires sur le disque). Donc $K(r)=\pi r^2+\dfrac{2\pi}{4\pi\kappa\sigma^2}\int_0^r s\,e^{-s^2/(4\sigma^2)}\,ds$. Or $\int_0^r s\,e^{-s^2/(4\sigma^2)}ds=2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)$, d'où $K(r)=\pi r^2+\dfrac{1}{2\kappa\sigma^2}\cdot2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. Remarquons que $K$ ne dépend ni de $\mu$ ni de l'intensité totale : l'excès par rapport au hasard est $\frac1\kappa(1-e^{-r^2/4\sigma^2})$, et il tend vers $1/\kappa$ (le nombre moyen de centres par km² est $\kappa$, donc $1/\kappa$ est l'aire d'« un agrégat »). (b) Simulons.

```python
def K_thomas_theorique(r, kappa, sigma):
    return np.pi * r ** 2 + (1 / kappa) * (1 - np.exp(-r ** 2 / (4 * sigma ** 2)))

rs12 = np.array([0.25, 0.5, 1.0, 1.5, 2.0])
for kappa, mu, sigma, B in [(0.5, 2, 0.4, 500), (0.08, 12, 0.4, 300)]:
    rng12 = np.random.default_rng(12)
    Ks, effectifs = [], []
    while len(Ks) < B:
        pts12 = semis_thomas(kappa, mu, sigma, rng12)
        if len(pts12) > 10:
            Ks.append(ripley_K(pts12, rs12))
            effectifs.append(len(pts12))
    Ks = np.array(Ks)
    theo = K_thomas_theorique(rs12, kappa, sigma)
    tab = pd.DataFrame({"r": rs12, "pi r^2 (hasard)": np.pi * rs12 ** 2, "K théorique": theo, "K simulé (moyenne)": np.nanmean(Ks, axis=0)})
    tab["écart_%"] = 100 * (tab["K simulé (moyenne)"] / tab["K théorique"] - 1)
    print(f"kappa = {kappa}, mu = {mu}, sigma = {sigma}  ({B} semis) | nombre de points : moyenne {np.mean(effectifs):.0f}, "
          f"écart-type {np.std(effectifs):.0f}, coefficient de variation {np.std(effectifs) / np.mean(effectifs):.0%}")
    print(tab.round(2).to_string(index=False))
    print()
```
<!--sortie-->
```text
kappa = 0.5, mu = 2, sigma = 0.4  (500 semis) | nombre de points : moyenne 101, écart-type 17, coefficient de variation 16%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         0.38                0.38    -0.15
0.50             0.79         1.43                1.43    -0.19
1.00             3.14         4.72                4.68    -0.82
1.50             7.07         9.01                8.81    -2.25
2.00            12.57        14.56               13.96    -4.13

kappa = 0.08, mu = 12, sigma = 0.4  (300 semis) | nombre de points : moyenne 97, écart-type 31, coefficient de variation 32%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         1.36                1.46     7.63
0.50             0.79         4.83                5.16     6.94
1.00             3.14        13.02               13.67     4.95
1.50             7.07        19.20               19.05    -0.77
2.00            12.57        25.04               23.21    -7.34
```

Pour le premier réglage (agrégats faibles et nombreux : en moyenne 2 descendants par centre), la simulation retrouve la théorie à moins de 1 % jusqu'à $r=1$ km, puis s'en écarte de $-2{,}3\,\%$ à 1,5 km et de $-4{,}1\,\%$ à 2 km. Pour le second (agrégats forts : 12 descendants par centre), les écarts sont nettement plus importants et de **signe variable** : $+7{,}6\,\%$ à 0,25 km, $+5\,\%$ à 1 km, $-7{,}3\,\%$ à 2 km. **Cela ne signifie pas que la formule est fausse**, mais que l'**estimateur** $\hat K$ est biaisé quand le nombre total de points varie beaucoup d'un semis à l'autre : le coefficient de variation de $n$ est de 16 % pour le premier réglage et de 32 % pour le second (voir la ligne imprimée au-dessus de chaque tableau). Une cause probable est que l'estimateur divise par un nombre de points aléatoire, lui-même corrélé aux comptages de voisins : l'espérance d'un rapport n'est pas le rapport des espérances. Ajoutons que, pour les grandes distances, la méthode du bord n'utilise qu'une petite fraction des points (à 2 km, seuls ceux situés à plus de 2 km du bord, soit 36 %). Morale : **ne pas surinterpréter $\hat K$ pour des semis très agrégés ni aux grandes distances**, ce que résume la règle de ne pas dépasser le quart du côté de la fenêtre.

---

## Bilan du chapitre 9

Vous savez maintenant :

- distinguer les **trois familles** de données spatiales (géostatistique, surfacique, semis de points) en se demandant *qu'est-ce qui est aléatoire ?* ;
- repérer un point et **mesurer une distance** correctement (haversine, projection locale) et dessiner une carte honnête sans fond de carte ;
- **définir un voisinage** par une matrice de poids et mesurer l'**autocorrélation** avec les indices de **Moran** et de **Geary**, les tester par **permutations**, et localiser les îlots avec les indices locaux (LISA) en **corrigeant** les tests multiples ;
- expliquer pourquoi ignorer l'autocorrélation fait **rejeter à tort** (46 % de faux positifs au lieu de 5 % dans notre simulation) et la tester sur les **résidus** d'un modèle ;
- estimer et ajuster un **variogramme** (pépite, palier, portée), connaître ses incertitudes, et **prédire par krigeage** avec une variance d'erreur, en validant par **validation croisée** ;
- étudier un **semis de points** par quadrats, plus proche voisin et **fonction $K$ de Ripley**, avec une **enveloppe de Monte-Carlo** et une **correction de bord**.

Ce chapitre a aussi rassemblé les **limites** qui reviennent à chaque étape :

| Limite | Où elle apparaît | Précaution |
|---|---|---|
| **Effet de bord** | plus proche voisin (biais de $R$), fonction $K$, indices locaux | correction (Donnelly, méthode du bord), enveloppe de Monte-Carlo dans la même fenêtre, examiner les bords à part |
| **Problème de l'unité spatiale modifiable** | corrélations et indices calculés sur des zones | indiquer le découpage, tester plusieurs échelles, ne pas transposer à l'individu |
| **Non-stationnarité** | variogramme, krigeage | retirer ou modéliser la tendance (krigeage universel) |
| **Anisotropie** | variogramme | variogrammes directionnels, **calibrés** par simulation |
| **Densité variable** | fonction $K$ | $K$ inhomogène ; ne pas confondre premier et second ordre |
| **Variogramme estimé, pas connu** | barres d'erreur du krigeage | validation croisée avec réajustement, prudence sur les intervalles |

> ✅ **Si vous ne deviez retenir qu'une idée.** *L'espace n'est pas une colonne de plus dans le tableau : il change la nature de l'information.* Des observations voisines ne sont pas indépendantes, donc : définissez le voisinage, mesurez la dépendance, vérifiez-la dans les résidus, et attribuez-lui une incertitude honnête.

> 🧭 **Pour aller plus loin** (hors de ce chapitre) : les modèles de régression spatiale (*spatial lag* et *spatial error*, par maximum de vraisemblance), le krigeage universel et le co-krigeage, les modèles géostatistiques bayésiens, la fonction $K$ inhomogène et les modèles de Cox log-gaussiens pour les semis de points, la statistique spatio-temporelle. Ces extensions reposent exactement sur les trois idées que vous venez de pratiquer : un **voisinage**, une **fonction de dépendance** et une **comparaison à un hasard bien défini**.
