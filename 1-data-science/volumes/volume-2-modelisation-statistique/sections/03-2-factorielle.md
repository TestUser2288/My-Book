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

```python hide
import numpy as np
import pandas as pd

r12, r13, r23 = 0.72, 0.63, 0.56
l1 = np.sqrt(r12 * r13 / r23)
l = np.array([l1, r12 / l1, r13 / l1])
print("saturations :", l.round(2))
print("communalités :", (l**2).round(2))
print("unicités     :", (1 - l**2).round(2))
# contrôle : on reconstruit les corrélations
print("r12, r13, r23 reconstruits :", (l[0]*l[1]).round(2), (l[0]*l[2]).round(2), (l[1]*l[2]).round(2))
```
<!--sortie-->
```text
saturations : [0.9 0.8 0.7]
communalités : [0.81 0.64 0.49]
unicités     : [0.19 0.36 0.51]
r12, r13, r23 reconstruits : 0.72 0.63 0.56
```

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

```python hide
rng = np.random.default_rng(0)
Lam = np.array([[0.8, 0.1], [0.7, 0.2], [0.1, 0.9], [0.2, 0.7]])      # saturations d'un modèle à 2 facteurs
Psi = np.diag(1 - (Lam**2).sum(axis=1))
Sigma = Lam @ Lam.T + Psi

angle = 0.7                                                          # rotation de 0,7 radian
T = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
Lam_rot = Lam @ T
Sigma_rot = Lam_rot @ Lam_rot.T + Psi
print("même matrice Sigma :", np.allclose(Sigma, Sigma_rot))
print("communalités avant :", (Lam**2).sum(axis=1).round(3))
print("communalités après :", (Lam_rot**2).sum(axis=1).round(3))
print("saturations avant :\n", Lam.round(2))
print("saturations après :\n", Lam_rot.round(2))
```
<!--sortie-->
```text
même matrice Sigma : True
communalités avant : [0.65 0.53 0.82 0.53]
communalités après : [0.65 0.53 0.82 0.53]
saturations avant :
 [[0.8 0.1]
 [0.7 0.2]
 [0.1 0.9]
 [0.2 0.7]]
saturations après :
 [[ 0.68 -0.44]
 [ 0.66 -0.3 ]
 [ 0.66  0.62]
 [ 0.6   0.41]]
```

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

```python hide
q = pd.read_csv("donnees/enquete_satisfaction.csv")
items = [f"q{j}" for j in range(1, 9)]
Q = q[items]
Zq = ((Q - Q.mean()) / Q.std()).to_numpy()
R = np.corrcoef(Zq, rowvar=False)
n, p = Zq.shape

def axes_principaux(R, k, iterations=200, tol=1e-9):
    """Axes principaux itérés : renvoie les saturations (non tournées) et les communalités."""
    h2 = 1 - 1 / np.diag(np.linalg.inv(R))              # départ : R² de chaque variable sur les autres
    for _ in range(iterations):
        Rr = R.copy()
        np.fill_diagonal(Rr, h2)                        # corrélation « réduite »
        w, V = np.linalg.eigh(Rr)
        o = np.argsort(w)[::-1][:k]
        L = V[:, o] * np.sqrt(np.maximum(w[o], 0))
        h2_nouveau = (L**2).sum(axis=1)
        if np.abs(h2_nouveau - h2).max() < tol:
            break
        h2 = h2_nouveau
    return L, h2_nouveau

L_paf, h2_paf = axes_principaux(R, k=2)
print("communalités (axes principaux) :", h2_paf.round(3))
```
<!--sortie-->
```text
communalités (axes principaux) : [0.57  0.413 0.447 0.277 0.571 0.418 0.522 0.408]
```

**2. Le maximum de vraisemblance.** On suppose $\mathbf x\sim\mathcal N(0,\Sigma)$ avec $\Sigma=\Lambda\Lambda^\top+\Psi$ et on maximise la vraisemblance (volume I, section 3.2.5) par rapport à $\Lambda$ et $\Psi$. Pas de formule fermée : on utilise un algorithme itératif. Avantage décisif : on dispose d'un **test d'ajustement** (section 3.2.4). Nous utilisons l'implémentation de `scikit-learn` et nous comparons les deux méthodes, question par question :

```python hide-code
from sklearn.decomposition import FactorAnalysis

fa_ml = FactorAnalysis(n_components=2, rotation=None, random_state=0).fit(Zq)
L_ml = fa_ml.components_.T                       # p x k
L_ml = L_ml * np.sign(L_ml.sum(axis=0))          # signe arbitraire : on rend positive la somme de chaque colonne
h2_ml = (L_ml**2).sum(axis=1)

comparaison = pd.DataFrame({"axes principaux": h2_paf, "maximum de vraisemblance": h2_ml}, index=items)
print(comparaison.round(3).to_string())

# les saturations dépendent de la rotation, mais la matrice reproduite Lambda Lambda' n'en dépend pas
ecart = np.abs(L_paf @ L_paf.T - L_ml @ L_ml.T).max()
print("écart maximal entre les deux corrélations reproduites :", ecart.round(3))
```
<!--sortie-->
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

```python hide-code
from scipy import stats

def test_ajustement(R, k, n):
    fa = FactorAnalysis(n_components=k, rotation=None, random_state=0).fit(Zq)
    L = fa.components_.T
    Sigma_hat = L @ L.T + np.diag(fa.noise_variance_)
    p = R.shape[0]
    F = np.linalg.slogdet(Sigma_hat)[1] - np.linalg.slogdet(R)[1] + np.trace(np.linalg.solve(Sigma_hat, R)) - p
    chi2 = (n - 1 - (2 * p + 5) / 6 - 2 * k / 3) * F
    ddl = ((p - k) ** 2 - (p + k)) / 2
    return chi2, ddl, stats.chi2.sf(chi2, ddl), chi2 - ddl * np.log(n)

lignes = []
for k in (1, 2, 3):
    chi2, ddl, pval, bic = test_ajustement(R, k, n)
    lignes.append({"k": k, "chi2": chi2, "ddl": int(ddl), "p-valeur": pval, "chi2 - ddl*ln(n)": bic})
print(pd.DataFrame(lignes).set_index("k").round(3).to_string())
```
<!--sortie-->
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

```python hide-code
brut = pd.DataFrame(L_ml, index=items, columns=["F1", "F2"])
print(brut.round(2).to_string())
```
<!--sortie-->
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

```python hide
def varimax(L, gamma=1.0, iterations=100, tol=1e-9):
    """Rotation varimax orthogonale (algorithme de Kaiser, version SVD). Renvoie L tournée et la rotation."""
    p, k = L.shape
    T = np.eye(k)
    critere = 0.0
    for _ in range(iterations):
        Lr = L @ T
        u, s, vt = np.linalg.svd(L.T @ (Lr**3 - (gamma / p) * Lr @ np.diag((Lr**2).sum(axis=0))))
        T = u @ vt
        if s.sum() < critere * (1 + tol):
            break
        critere = s.sum()
    return L @ T, T

L_vm, T_vm = varimax(L_ml)

def aligner(M):
    """Colonne 1 = le bloc de questions q1-q4 ; convention de signe : la plus grande saturation de chaque colonne est positive."""
    M = M[:, np.argsort(-np.abs(M[:4]).mean(axis=0))]
    return M * np.sign(M[np.abs(M).argmax(axis=0), [0, 1]])

tourne = pd.DataFrame(aligner(L_vm), index=items, columns=["F1 (produits)", "F2 (service)"])
assert np.allclose((L_vm**2).sum(axis=1), h2_ml)          # les communalités sont inchangées

# comparaison avec la rotation varimax de scikit-learn
L_sk = FactorAnalysis(n_components=2, rotation="varimax", random_state=0).fit(Zq).components_.T
assert np.abs(aligner(L_vm) - aligner(L_sk)).max() < 0.01   # même solution que scikit-learn
```

```python hide-code
print(tourne.round(2).to_string())
```
<!--sortie-->
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

```python hide-code
w, V = np.linalg.eigh(R)
o = np.argsort(w)[::-1]
w, V = w[o], V[:, o]
Lacp = V[:, :2] * np.sqrt(w[:2])
h2_acp = (Lacp**2).sum(axis=1)

tab = pd.DataFrame({"part de variance (ACP, 2 comp.)": h2_acp, "communalité (AF, 2 facteurs)": h2_ml}, index=items)
tab.loc["moyenne"] = tab.mean()
print(tab.round(2).to_string())
```
<!--sortie-->
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

```python hide-code
vrai = np.array([0.80, 0.70, 0.75, 0.60, 0.80, 0.70, 0.75, 0.65])
principale = pd.concat([tourne.iloc[:4, 0], tourne.iloc[4:, 1]])      # saturation sur le « bon » facteur
croisee = pd.concat([tourne.iloc[:4, 1], tourne.iloc[4:, 0]]).abs()    # saturation sur l'autre facteur
bilan = pd.DataFrame({"vraie": vrai, "estimée (varimax)": principale, "saturation croisée": croisee})
print(bilan.round(2).to_string())
print("erreur absolue moyenne sur les saturations principales :", np.abs(bilan["vraie"] - bilan["estimée (varimax)"]).mean().round(3))
```
<!--sortie-->
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

```python hide
def alpha_cronbach(D):
    D = np.asarray(D, dtype=float)
    k = D.shape[1]
    return k / (k - 1) * (1 - D.var(axis=0, ddof=1).sum() / D.sum(axis=1).var(ddof=1))

produits = Q[["q1", "q2", "q3", "q4"]]
service = Q[["q5", "q6", "q7", "q8"]]
print("alpha, échelle produits :", round(alpha_cronbach(produits), 3))
print("alpha, échelle service  :", round(alpha_cronbach(service), 3))
print("alpha des 8 questions ensemble :", round(alpha_cronbach(Q), 3))

scores = pd.DataFrame({"id_client": q["id_client"], "score_produits": produits.mean(axis=1), "score_service": service.mean(axis=1)})
print("corrélation entre les deux échelles :", round(scores["score_produits"].corr(scores["score_service"]), 3))
```
<!--sortie-->
```text
alpha, échelle produits : 0.741
alpha, échelle service  : 0.784
alpha des 8 questions ensemble : 0.732
corrélation entre les deux échelles : 0.19
```

Les deux échelles sont **cohérentes** ($\alpha=0{,}74$ et $0{,}78$, au-dessus du repère de 0,7). Leur corrélation, de $0{,}19$, est plus faible que la corrélation **vraie** de $0{,}30$ entre les facteurs : c'est l'effet classique d'**atténuation par l'erreur de mesure** (chaque score contient du bruit propre aux questions, qui dilue la corrélation entre les facteurs sous-jacents). Remarquez que l'alpha des huit questions réunies reste honorable ($0{,}73$), mais qu'il serait trompeur de conclure à « une seule dimension » : un alpha élevé est compatible avec **plusieurs** dimensions corrélées. C'est l'analyse factorielle, pas l'alpha, qui répond à la question « combien de dimensions ? ».

Reste la question de fond : ces deux scores sont-ils liés au comportement des clientes ? On les joint au fichier des clientes (l'application 3.2 du cahier détaille la démarche) et l'on regarde, parmi les clientes ayant commandé, leurs corrélations avec quelques comportements d'achat :

| | panier moyen | durée de la relation | nombre de commandes | âge |
|---|---:|---:|---:|---:|
| score « produits » | 0,24 | 0,04 | 0,20 | 0,03 |
| score « service » | 0,09 | 0,16 | 0,16 | −0,00 |

```python hide
c = pd.read_csv("donnees/clients.csv")
f = scores.merge(c[["id_client", "rachat_12m", "panier_moyen", "duree_mois", "nb_commandes_an", "age"]], on="id_client")
f = f[f["panier_moyen"] > 0]                     # clientes ayant commandé
print(f[["score_produits", "score_service", "panier_moyen", "duree_mois", "nb_commandes_an", "age"]].corr().round(2)
       .loc[["score_produits", "score_service"], ["panier_moyen", "duree_mois", "nb_commandes_an", "age"]].to_string())
print()
print(f.groupby("rachat_12m")[["score_produits", "score_service"]].mean().round(2).to_string())
```
<!--sortie-->
```text
                panier_moyen  duree_mois  nb_commandes_an   age
score_produits          0.24        0.04             0.20  0.03
score_service           0.09        0.16             0.16 -0.00

            score_produits  score_service
rachat_12m                               
0                     3.46           3.41
1                     3.80           3.68
```

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
