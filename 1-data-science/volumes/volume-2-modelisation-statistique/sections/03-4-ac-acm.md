## 3.4 ➕ Pour aller plus loin : l'analyse des correspondances (AC et ACM)

> 🧭 **Section optionnelle.** Elle étend l'idée de l'ACP aux **variables qualitatives** (canal, ville, tranche d'âge), pour lesquelles moyenne et variance n'ont pas de sens. On peut sauter cette section sans perdre le fil du chapitre. Elle s'appuie sur le test du khi-deux du volume I (section 3.4.6) et sur la décomposition en valeurs singulières (volume I, section 1.1.4).

> 💡 **Intuition.** L'ACP regarde un nuage de points dans un espace de nombres. Mais comment « dessiner » un tableau croisant le canal d'acquisition (trois modalités) et la taille du panier (quatre tranches) ? L'**analyse factorielle des correspondances** (AFC, ou simplement AC) transforme un tableau de contingence en **deux nuages de points** (un pour les lignes, un pour les colonnes), placés sur une même carte, de façon que **deux modalités proches sur la carte soient fréquemment associées** dans les données. Quant à l'**analyse des correspondances multiples** (ACM), c'est l'AC appliquée à plusieurs variables qualitatives à la fois.

### 3.4.1 Le point de départ : un tableau de contingence

Prenons les clientes ayant déjà commandé (1 740 sur 2 000) et croisons leur **canal d'acquisition** avec la **tranche de leur panier moyen**, définie par les quartiles : « très petit » pour le quart le plus bas, jusqu'à « très grand » pour le quart le plus haut.

```python
import numpy as np
import pandas as pd
from scipy import stats

c = pd.read_csv("donnees/clients.csv")
a = c[c["nb_commandes_an"] > 0].copy()
a["tranche_panier"] = pd.qcut(a["panier_moyen"], 4, labels=["T1 très petit", "T2 petit", "T3 grand", "T4 très grand"])
a["tranche_age"] = pd.cut(a["age"], [0, 29, 39, 200], labels=["moins de 30", "30-39", "40 et plus"])

N = pd.crosstab(a["canal_acquisition"], a["tranche_panier"])
print(N.to_string())
print()
print("profils-lignes (en %) : répartition des paniers dans chaque canal")
print((100 * N.div(N.sum(axis=1), axis=0)).round(1).to_string())
```
<!--sortie-->
```text
tranche_panier     T1 très petit  T2 petit  T3 grand  T4 très grand
canal_acquisition                                                  
Boutique                      46        93       126            184
Instagram                    258       184       158             87
Site                         132       157       152            163

profils-lignes (en %) : répartition des paniers dans chaque canal
tranche_panier     T1 très petit  T2 petit  T3 grand  T4 très grand
canal_acquisition                                                  
Boutique                    10.2      20.7      28.1           41.0
Instagram                   37.6      26.8      23.0           12.7
Site                        21.9      26.0      25.2           27.0
```

Les **profils-lignes** (la répartition des tranches de panier dans chaque canal) sont très différents d'un canal à l'autre : la boutique compte 69 % de paniers « grands » ou « très grands » (T3 et T4) contre 36 % pour Instagram, dont 64 % des paniers sont « petits » ou « très petits » (T1 et T2). Si le canal et le panier étaient **indépendants**, les trois lignes auraient le même profil, égal au profil des totaux. L'analyse des correspondances décrit **comment et dans quelle direction** les profils s'écartent de cette indépendance.

Mesurons d'abord l'écart global avec le test du khi-deux (volume I, section 3.4.6) :

```python
chi2, p, ddl, attendus = stats.chi2_contingency(N, correction=False)
n = N.values.sum()
print(f"khi-deux = {chi2:.1f}, ddl = {ddl}, p = {p:.2g}")
print(f"khi-deux / n = {chi2 / n:.4f}")
```
<!--sortie-->
```text
khi-deux = 180.7, ddl = 6, p = 2.5e-36
khi-deux / n = 0.1038
```

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
| **Instagram** | 30 | 10 |
| **Boutique** | 10 | 30 |

Les marges valent $\mathbf r=(0{,}5;0{,}5)$ et $\mathbf c=(0{,}5;0{,}5)$ ; $P=\begin{pmatrix}0{,}375&0{,}125\\0{,}125&0{,}375\end{pmatrix}$ ; $r_ic_j=0{,}25$ partout. Donc

$$S=\frac{P-0{,}25}{\sqrt{0{,}25}}=\frac{1}{0{,}5}\begin{pmatrix}0{,}125&-0{,}125\\-0{,}125&0{,}125\end{pmatrix}=\begin{pmatrix}0{,}25&-0{,}25\\-0{,}25&0{,}25\end{pmatrix}.$$

Cette matrice est de rang 1 : $S=0{,}5\times\begin{pmatrix}1/\sqrt2\\-1/\sqrt2\end{pmatrix}\begin{pmatrix}1/\sqrt2&-1/\sqrt2\end{pmatrix}$, donc $\sigma_1=0{,}5$ et $\sigma_1^2=0{,}25$. Vérification avec le khi-deux : les effectifs attendus valent $20$ partout, d'où $\chi^2=4\times\frac{(\pm10)^2}{20}=20$ et $\chi^2/n=20/80=0{,}25$. ✓ Les coordonnées des lignes sont $\pm\frac{1}{\sqrt{0{,}5}}\cdot\frac{1}{\sqrt2}\cdot0{,}5=\pm0{,}5$ : Instagram à $-0{,}5$ d'un côté, Boutique à $+0{,}5$ de l'autre. Un tableau $2\times2$ n'a qu'**un seul axe**, sur lequel les deux modalités s'opposent. Plus généralement, un tableau $I\times J$ a au plus $\min(I,J)-1$ axes non triviaux.

Écrivons la méthode et vérifions-la sur cet exemple, puis sur notre tableau :

```python
def analyse_correspondances(N):
    """AC par SVD des résidus standardisés. Renvoie l'inertie par axe et les coordonnées principales."""
    N = np.asarray(N, dtype=float)
    P = N / N.sum()
    r, c = P.sum(axis=1), P.sum(axis=0)
    S = (P - np.outer(r, c)) / np.sqrt(np.outer(r, c))
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    F = (U / np.sqrt(r)[:, None]) * sv          # coordonnées principales des lignes
    G = (Vt.T / np.sqrt(c)[:, None]) * sv       # coordonnées principales des colonnes
    return {"inertie": sv**2, "F": F, "G": G}

petit = analyse_correspondances([[30, 10], [10, 30]])
print("exemple 2x2 : inertie =", petit["inertie"].round(4), "| coordonnées des lignes sur l'axe 1 =", np.abs(petit["F"][:, 0]).round(3))

ac = analyse_correspondances(N.values)
print("tableau canal x panier : inertie par axe =", ac["inertie"].round(4))
print("somme des inerties =", ac["inertie"].sum().round(4), "  et khi-deux/n =", round(chi2 / n, 4))
print("part de l'axe 1 :", f"{100 * ac['inertie'][0] / ac['inertie'].sum():.1f} %")
```
<!--sortie-->
```text
exemple 2x2 : inertie = [0.25 0.  ] | coordonnées des lignes sur l'axe 1 = [0.5 0.5]
tableau canal x panier : inertie par axe = [0.1031 0.0007 0.    ]
somme des inerties = 0.1038   et khi-deux/n = 0.1038
part de l'axe 1 : 99.3 %
```

### 3.4.3 Lire la carte

```python
lignes = pd.DataFrame(ac["F"][:, :2], index=N.index, columns=["axe 1", "axe 2"])
colonnes = pd.DataFrame(ac["G"][:, :2], index=N.columns, columns=["axe 1", "axe 2"])
print("canaux :")
print(lignes.round(3).to_string())
print("tranches de panier :")
print(colonnes.round(3).to_string())
```
<!--sortie-->
```text
canaux :
                   axe 1  axe 2
canal_acquisition              
Boutique           0.448 -0.026
Instagram         -0.354 -0.015
Site               0.070  0.036
tranches de panier :
                axe 1  axe 2
tranche_panier              
T1 très petit  -0.440 -0.024
T2 petit       -0.090  0.046
T3 grand        0.079 -0.010
T4 très grand   0.452 -0.012
```

![Analyse des correspondances du tableau canal x tranche de panier (à gauche) et, en comparaison, du tableau canal x ville (à droite). Attention aux échelles : à gauche les points sont répartis sur près de ±0,45, à droite sur ±0,1 seulement.](figures/ch03-ca-carte.png)

Sur la carte de gauche, **tout se passe sur le premier axe** (il porte presque toute l'inertie). Les trois canaux s'y rangent dans l'ordre Instagram, Site, Boutique ; et les quatre tranches de panier dans l'ordre T1, T2, T3, T4, **du même côté que** les canaux auxquels elles sont associées : les très grands paniers (T4) sont du côté de la boutique, les très petits (T1) du côté d'Instagram. L'axe 1 est donc un axe **« petits paniers / gros paniers »** commun aux deux variables. Le fait que les tranches de panier s'ordonnent exactement comme leur numérotation est typique : pour une variable ordinale, l'AC retrouve l'ordre sans qu'on le lui ait dit.

> 🧪 **Révélation.** C'est ce qui avait été programmé : le canal d'acquisition agit sur le panier (en échelle logarithmique : $+0{,}22$ pour la boutique, $+0{,}05$ pour le site, $-0{,}12$ pour Instagram). L'AC a retrouvé cette association sans qu'on lui désigne de variable « à expliquer », et a même restitué l'ordre des canaux.

> ⚠️ **Piège numéro un : une carte a toujours l'air de dire quelque chose.** Faites maintenant l'expérience inverse, avec deux variables qui n'ont **aucun lien** dans la simulation : le canal d'acquisition et la ville.

```python
N2 = pd.crosstab(a["canal_acquisition"], a["ville"])
chi2_b, p_b, ddl_b, _ = stats.chi2_contingency(N2, correction=False)
ac2 = analyse_correspondances(N2.values)
print(f"canal x ville : khi-deux = {chi2_b:.1f}, ddl = {ddl_b}, p = {p_b:.2f}")
print("inertie totale :", round(chi2_b / N2.values.sum(), 4), "(valeur attendue par pur hasard : environ ddl/n =", round(ddl_b / N2.values.sum(), 4), ")")
print("part de l'axe 1 :", f"{100 * ac2['inertie'][0] / ac2['inertie'].sum():.0f} %", " part de l'axe 2 :", f"{100 * ac2['inertie'][1] / ac2['inertie'].sum():.0f} %")
```
<!--sortie-->
```text
canal x ville : khi-deux = 8.1, ddl = 10, p = 0.62
inertie totale : 0.0047 (valeur attendue par pur hasard : environ ddl/n = 0.0057 )
part de l'axe 1 : 74 %  part de l'axe 2 : 26 %
```

Le test du khi-deux ne rejette pas l'indépendance, et l'inertie totale est de l'ordre de grandeur de ce que le **hasard seul** produit (en moyenne $\text{ddl}/n$ sous l'indépendance). Pourtant, l'axe 1 « explique » $74\ \%$ de l'inertie et l'axe 2 les $26\ \%$ restants : un tableau $3\times6$ n'a que deux axes non triviaux, qui se partagent donc **toujours** 100 % de l'inertie, quel que soit le tableau. La carte de droite de la figure montre des points bien répartis, mais sur une échelle minuscule (de l'ordre de $\pm0{,}1$, contre $\pm0{,}45$ à gauche). **Un pourcentage d'inertie ne prouve jamais rien** : il faut d'abord regarder le khi-deux et l'**inertie totale**, qui mesure l'intensité de l'association.

### 3.4.4 L'analyse des correspondances multiples (ACM)

Pour étudier **plusieurs** variables qualitatives à la fois (disons $Q$), on recode chaque individu par un vecteur d'indicatrices : pour la variable « canal », trois colonnes (0 ou 1), dont une seule vaut 1. On obtient le **tableau disjonctif complet** $Z$, de $n$ lignes et $J=\sum_q J_q$ colonnes ($J_q$ modalités pour la variable $q$). L'ACM est simplement **l'analyse des correspondances de ce tableau $Z$**, avec les mêmes formules.

Appliquons-la à six variables : canal, ville, tranche d'âge, tranche de panier, offre de bienvenue et rachat dans les 12 mois.

```python
cols = ["canal_acquisition", "ville", "tranche_age", "tranche_panier", "offre_bienvenue", "rachat_12m"]
D = pd.get_dummies(a[cols].astype(str), dtype=float)             # tableau disjonctif complet
Q_, J = len(cols), D.shape[1]
print("individus :", D.shape[0], "| variables Q =", Q_, "| modalités J =", J)

acm = analyse_correspondances(D.values)
lam = acm["inertie"]
print("inertie totale =", lam.sum().round(4), "  théorie (J - Q)/Q =", round((J - Q_) / Q_, 4))
print("8 premières valeurs propres :", lam[:8].round(4))
print("part de variance des deux premiers axes :", (100 * lam[:2] / lam.sum()).round(1), "%")
```
<!--sortie-->
```text
individus : 1740 | variables Q = 6 | modalités J = 20
inertie totale = 2.3333   théorie (J - Q)/Q = 2.3333
8 premières valeurs propres : [0.2347 0.1967 0.1826 0.1777 0.1738 0.1682 0.1663 0.1646]
part de variance des deux premiers axes : [10.1  8.4] %
```

Deux remarques sur ces nombres. D'abord, l'inertie totale de l'ACM vaut **toujours** $(J-Q)/Q$, indépendamment des données : ici $(20-6)/6\approx2{,}33$ (le nombre de modalités moins le nombre de variables, rapporté au nombre de variables). Ensuite, les valeurs propres décroissent **très lentement**, et les pourcentages d'inertie sont donc faibles ($10{,}1\ \%$ et $8{,}4\ \%$ pour les deux premiers axes) : c'est normal en ACM, c'est un effet du codage, pas un signe d'absence de structure. Une correction classique, due à **Benzécri**, ne garde que les valeurs propres supérieures à $1/Q$ et les transforme en

$$\lambda_k^{\text{corr}}=\Bigl(\frac{Q}{Q-1}\Bigr)^2\Bigl(\lambda_k-\frac1Q\Bigr)^2\qquad(\lambda_k>1/Q),$$

ce qui donne des pourcentages plus réalistes (six valeurs propres dépassent $1/Q=0{,}1667$) :

```python
seuil = 1 / Q_
gardees = lam[lam > seuil]
corrigees = (Q_ / (Q_ - 1)) ** 2 * (gardees - seuil) ** 2
print("valeurs propres supérieures à 1/Q =", round(seuil, 4), ":", len(gardees))
print("parts corrigées (Benzécri) des deux premiers axes :", (100 * corrigees[:2] / corrigees.sum()).round(1), "%")
```
<!--sortie-->
```text
valeurs propres supérieures à 1/Q = 0.1667 : 6
parts corrigées (Benzécri) des deux premiers axes : [77.7 15.1] %
```

Pour savoir **quelle variable construit quel axe**, on calcule les **contributions** : celle de la modalité $j$ à l'axe $k$ vaut $c_j\,G_{jk}^2/\sigma_k^2$ (somme égale à 1 sur les modalités d'un même axe). En additionnant par variable, on voit quelles variables « fabriquent » chaque axe.

```python
c_mod = D.values.sum(axis=0) / D.values.sum()                    # poids des modalités
ctr = (c_mod[:, None] * acm["G"][:, :3] ** 2) / acm["inertie"][:3]
ctr = pd.DataFrame(ctr, index=D.columns, columns=["axe 1", "axe 2", "axe 3"])
par_variable = ctr.groupby([next(v for v in cols if m.startswith(v + "_")) for m in D.columns]).sum()
print((100 * par_variable).round(0).loc[cols].to_string())
```
<!--sortie-->
```text
                   axe 1  axe 2  axe 3
canal_acquisition   36.0    2.0   17.0
ville                1.0   11.0   27.0
tranche_age         11.0   17.0   37.0
tranche_panier      47.0    5.0   17.0
offre_bienvenue      0.0   28.0    2.0
rachat_12m           5.0   37.0    0.0
```

![Analyse des correspondances multiples : plan des deux premiers axes. Les modalités des quatre variables d'intérêt sont étiquetées (couleur par variable) ; les six villes sont les points gris.](figures/ch03-acm-carte.png)

Avec la correction de Benzécri, le premier axe porte à lui seul près de $78\ \%$ de l'« inertie utile » et le deuxième $15\ \%$ : l'essentiel de la structure est dans le plan de la carte. Le tableau des contributions et la carte se lisent ensemble :

1. **L'axe 1** est construit par la **tranche de panier** ($47\ \%$) et le **canal** ($36\ \%$) : il oppose Boutique et très grands paniers (à droite) à Instagram et très petits paniers (à gauche), l'association déjà vue en 3.4.3. L'âge y contribue un peu ($11\ \%$) : les moins de 30 ans sont du côté des petits paniers.
2. **L'axe 2** est construit par le **rachat** ($37\ \%$), l'**offre de bienvenue** ($28\ \%$) et, dans une moindre mesure, l'**âge** ($17\ \%$) : `offre=1` est proche de `rachat=1`, loin de `offre=0` et `rachat=0`, et les moins de 30 ans sont du même côté que les rachats.
3. **Les villes** contribuent à peine aux deux premiers axes ($1\ \%$ et $11\ \%$) : leurs points gris sont dispersés (ce sont de petits groupes, dont les coordonnées sont instables) mais ne s'associent à rien de particulier.

> 🧪 **Révélation.** Tout cela correspond à la simulation : le canal détermine le panier ; l'offre de bienvenue augmente la probabilité de rachat ; l'âge agit à la fois sur le panier (les plus âgées dépensent un peu plus) et sur le rachat (les plus jeunes rachètent davantage) ; la ville n'a aucun effet. L'ACM n'a reçu aucune variable « à expliquer » : elle a simplement dessiné les associations qui existent dans le tableau.

> 🛠️ **Application.** L'ACM est la porte d'entrée classique pour explorer **un questionnaire avec des modalités qualitatives** (profils de clientes, réponses à choix multiples). Elle est aussi utilisée pour construire des **typologies** : on calcule les coordonnées des individus sur les premiers axes, puis on les classe par k-means ou classification hiérarchique (section 3.3). Mais prudence : l'ACM décrit **les associations observées**, elle n'établit pas de causalité.

> ⚠️ **Autres pièges.** (1) Les **modalités rares** (quelques individus) ont des coordonnées extrêmes et peuvent dominer un axe : regroupez-les ou mettez-les en éléments supplémentaires. (2) L'AC est **descriptive** : testez d'abord l'association (khi-deux), puis décrivez-la. (3) Dans l'ACM, **chaque variable pèse son nombre de modalités** : une variable à 15 modalités dominera une variable à 2.

> ✅ **À retenir**
> - L'AC transforme un **tableau de contingence** en cartes : les modalités fréquemment associées sont **proches**.
> - Mathématiquement, c'est la **SVD des résidus standardisés** $S_{ij}=(p_{ij}-r_ic_j)/\sqrt{r_ic_j}$ ; l'**inertie totale** vaut $\chi^2/n$ et se répartit sur les axes.
> - Avant d'interpréter une carte, **testez l'association** : une carte d'indépendance a l'air tout aussi sérieuse.
> - L'**ACM** est l'AC du tableau disjonctif complet ; son inertie totale vaut $(J-Q)/Q$ ; les pourcentages d'inertie sont faibles par construction (corrigez avec Benzécri) ; les **contributions** disent quelle variable construit quel axe.
