## 3.6 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 13 et 14 portent sur les sections optionnelles 3.5 et 3.4.

### Énoncés

**Exercice 1 ⭐ (ACP à la main).** Cinq clientes ont passé $4,\,5,\,6,\,7,\,8$ commandes dans l'année, pour un panier moyen respectif de $4,\,3,\,6,\,7,\,5$ dizaines de €. (a) Centrez les données et calculez la matrice de covariance. (b) Trouvez ses valeurs propres et ses vecteurs propres unitaires. (c) Quelle part de la variance la première composante explique-t-elle ? (d) Calculez les scores des cinq clientes sur cette composante. (e) Vérifiez par le code.

**Exercice 2 ⭐ (lire un éboulis).** Une ACP normée sur 5 variables a donné les valeurs propres $2{,}6;\ 1{,}1;\ 0{,}7;\ 0{,}4;\ 0{,}2$. (a) Quelle est la variance totale ? (b) Calculez la part de variance de chaque composante et les parts cumulées. (c) Combien de composantes retient la règle de Kaiser ? Combien faut-il pour atteindre 80 % de la variance ? (d) Pourquoi les deux critères ne donnent-ils pas la même réponse, et lequel préférez-vous ?

**Exercice 3 ⭐ (les unités).** Dans la table `clients.csv`, on exprime la dépense annuelle en **centimes** de euro au lieu de euros. (a) Que devient la part de variance de la première composante d'une ACP **non standardisée** ? (b) Et d'une ACP **standardisée** ? Justifiez, puis vérifiez par le code.

**Exercice 4 ⭐⭐ (propriétés des scores).** Soit $Z$ un tableau de variables standardisées, $R$ sa matrice de corrélation, $\mathbf v_j$ et $\lambda_j$ ses éléments propres, et $\mathbf t_j=Z\mathbf v_j$ les scores. (a) Démontrez que $\operatorname{Var}(\mathbf t_j)=\lambda_j$ et que $\operatorname{Cov}(\mathbf t_i,\mathbf t_j)=0$ pour $i\neq j$. (b) Démontrez que la corrélation entre la variable $z_i$ et le score $\mathbf t_j$ vaut $v_{ij}\sqrt{\lambda_j}$. (c) Vérifiez les deux propriétés numériquement sur les cinq variables numériques de `clients.csv` standardisées.

**Exercice 5 ⭐⭐ (reconstruction).** Sur les huit questions standardisées du questionnaire : (a) combien de composantes faut-il pour restituer au moins 80 % de la variance ? (b) Calculez l'erreur quadratique moyenne par case (RMSE) de la reconstruction avec 2 composantes, et comparez-la à l'erreur d'une reconstruction **triviale** par la moyenne (c'est-à-dire avec 0 composante). (c) Vérifiez que l'erreur totale vaut $(n-1)\sum_{j>k}\lambda_j$.

**Exercice 6 ⭐⭐ (modèle factoriel à un facteur).** Trois questions sur la rapidité de la livraison ont les corrélations $r_{12}=0{,}48$, $r_{13}=0{,}40$, $r_{23}=0{,}30$. (a) Calculez les saturations d'un modèle à un facteur, les communalités et les unicités. (b) Quelle question est le meilleur indicateur du facteur ? (c) Que se passe-t-il si $r_{23}$ valait $0{,}15$ ? Qu'est-ce que cela signifie pour le modèle ?

**Exercice 7 ⭐⭐ (invariance par rotation).** Les saturations d'un modèle à deux facteurs pour quatre questions sont $\Lambda=\begin{pmatrix}0{,}7&0{,}3\\0{,}6&0{,}4\\0{,}2&0{,}8\\0{,}3&0{,}7\end{pmatrix}$. (a) Calculez les communalités. (b) On applique une rotation d'angle $\theta=30^\circ$ : $\Lambda^*=\Lambda T$ avec $T=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$. Calculez $\Lambda^*$ et vérifiez que les communalités et la matrice $\Lambda\Lambda^\top$ sont inchangées. (c) Pourquoi cela empêche-t-il de dire « la vraie valeur » d'une saturation ?

**Exercice 8 ⭐⭐ (alpha de Cronbach).** Une échelle de trois questions standardisées a une corrélation moyenne de $0{,}5$ entre questions. (a) Calculez la variance de la somme des trois questions, puis l'alpha de Cronbach. (b) Combien de questions de même corrélation moyenne faut-il pour atteindre $\alpha\geq0{,}9$ ? On rappelle la formule de Spearman-Brown : pour des questions standardisées, $\alpha=\dfrac{k\,\bar r}{1+(k-1)\bar r}$.

**Exercice 9 ⭐⭐ (k-means : le piège du minimum local).** Six paniers (en dizaines de €) : $2,\ 3,\ 4,\ 10,\ 12,\ 20$. On cherche $k=2$ groupes. (a) Déroulez l'algorithme de Lloyd à partir des centres $(2;\,20)$ et calculez la variance intra-groupe finale $W$. (b) Recommencez à partir des centres $(2;\,10)$. (c) Comparez les deux solutions : que conclure sur l'algorithme ?

**Exercice 10 ⭐⭐ (silhouette).** Pour la partition $\{2,3,4\}$ et $\{10,12,20\}$ de l'exercice 9, calculez à la main la silhouette des points $4$, $10$ et $20$, puis la silhouette moyenne (code). Quel point est le moins bien classé ?

**Exercice 11 ⭐⭐ (critères d'agrégation).** Quatre clientes $A,B,C,D$ ont les distances deux à deux suivantes : $AB=2$, $AC=5$, $AD=9$, $BC=3$, $BD=7$, $CD=4{,}5$. Construisez à la main l'arbre de la classification hiérarchique pour les critères **simple**, **complet** et **moyen**, en donnant les fusions successives et leurs hauteurs. Vérifiez avec `scipy`.

**Exercice 12 ⭐⭐⭐ (une segmentation, ou pas ?).** la gérante veut des segments de clientes selon deux critères seulement : le nombre de commandes par an et le panier moyen (clientes ayant commandé, variables standardisées). (a) Calculez la silhouette moyenne des k-means pour $k=2,\dots,6$. (b) Évaluez la stabilité (indice de Rand ajusté entre deux ré-estimations sur des échantillons bootstrap) du découpage en $k=3$. (c) Que conseillez-vous à la gérante ? Rédigez deux phrases pour elle, sans jargon.

**Exercice 13 ⭐⭐ (analyse discriminante, section 3.5).** Les clientes à petit panier ont un panier moyen de 40 €, celles à gros panier de 55 €, avec un écart-type de 10 € dans chaque groupe, et les gros paniers représentent 20 % des commandes. (a) À partir de quel panier la règle de Bayes (LDA à une variable) classe-t-elle une commande dans « gros panier » ? (b) Quelle est la probabilité a posteriori d'être un gros panier pour une commande de 55 € ? (c) Commentez : une commande de 55 €, égale à la moyenne du groupe « gros panier », est-elle classée dans ce groupe ?

**Exercice 14 ⭐⭐⭐ (analyse des correspondances, section 3.4).** Un tableau croise le canal (Réseaux, Boutique) et trois tranches de délai de livraison (court, moyen, long) :

| | court | moyen | long |
|---|---|---|---|
| Réseaux | 40 | 30 | 10 |
| Boutique | 10 | 30 | 30 |

(a) Calculez $\chi^2$ et l'inertie totale $\chi^2/n$. (b) Combien d'axes non triviaux l'AC aura-t-elle ? (c) Vérifiez par le code que la somme des inerties des axes est égale à $\chi^2/n$, et dites quelle modalité de délai est la plus associée à Réseaux.

### Corrigés

**Corrigé 1.** (a) Moyennes : $\bar x=6$, $\bar y=5$. Écarts : $x_c=(-2,-1,0,1,2)$ et $y_c=(-1,-2,1,2,0)$. Variances : $s_{xx}=10/4=2{,}5$, $s_{yy}=(1+4+1+4+0)/4=2{,}5$ ; covariance : $s_{xy}=(2+2+0+2+0)/4=1{,}5$. Donc $S=\begin{pmatrix}2{,}5&1{,}5\\1{,}5&2{,}5\end{pmatrix}$.

(b) $\det(S-\lambda I)=(2{,}5-\lambda)^2-1{,}5^2=0$ donne $\lambda=2{,}5\pm1{,}5$, soit $\lambda_1=4$ et $\lambda_2=1$. Pour $\lambda_1=4$ : $-1{,}5v_1+1{,}5v_2=0$, donc $\mathbf v_1=(1,1)/\sqrt2$. Pour $\lambda_2=1$ : $\mathbf v_2=(1,-1)/\sqrt2$.

(c) Variance totale $=5$ ; la première composante en explique $4/5=80\ \%$.

(d) $t_{i1}=(x_{c,i}+y_{c,i})/\sqrt2$ : les sommes $x_c+y_c$ valent $(-3,-3,1,3,2)$, donc les scores sont $(-3,-3,1,3,2)/\sqrt2\approx(-2{,}12;\,-2{,}12;\,0{,}71;\,2{,}12;\,1{,}41)$. On vérifie que leur variance est $(9+9+1+9+4)/(2\times4)=32/8=4=\lambda_1$ ✓.

```python
import numpy as np
X = np.array([[4, 4], [5, 3], [6, 6], [7, 7], [8, 5]], dtype=float)
Xc = X - X.mean(axis=0)
S = np.cov(Xc, rowvar=False)
w, V = np.linalg.eigh(S)
o = np.argsort(w)[::-1]
w, V = w[o], V[:, o]
print("S =", S.tolist())
print("valeurs propres :", w.round(3), "| parts :", (w / w.sum()).round(3))
print("scores sur CP1 (au signe près) :", np.abs(Xc @ V[:, 0]).round(2))
```
<!--sortie-->
```text
S = [[2.5, 1.5], [1.5, 2.5]]
valeurs propres : [4. 1.] | parts : [0.8 0.2]
scores sur CP1 (au signe près) : [2.12 2.12 0.71 2.12 1.41]
```

**Corrigé 2.** (a) Pour une ACP normée, la variance totale est le nombre de variables : $5$ (et c'est bien la somme $2{,}6+1{,}1+0{,}7+0{,}4+0{,}2=5$). (b) Parts : $52\ \%$, $22\ \%$, $14\ \%$, $8\ \%$, $4\ \%$ ; cumul : $52,\ 74,\ 88,\ 96,\ 100\ \%$. (c) Kaiser garde les valeurs propres $>1$ : **deux** composantes ($2{,}6$ et $1{,}1$). Pour atteindre 80 %, il en faut **trois** (74 % avec deux, 88 % avec trois). (d) Les deux critères répondent à des questions différentes : Kaiser compare chaque composante à « une variable d'origine » ; la règle des 80 % fixe un objectif de restitution. Ici, la deuxième composante ($1{,}1$) dépasse de très peu le seuil de 1 : c'est le cas où l'**analyse parallèle** est utile, car elle compare à ce que ferait le bruit (qui dépasse souvent 1 pour la deuxième valeur propre, comme au 3.1.6).

```python
w = np.array([2.6, 1.1, 0.7, 0.4, 0.2])
print("variance totale :", w.sum())
print("parts (%)   :", (100 * w / w.sum()).round(0))
print("cumul (%)   :", (100 * w.cumsum() / w.sum()).round(0))
print("Kaiser (> 1):", int((w > 1).sum()), "| composantes pour 80 % :", int(np.argmax(w.cumsum() / w.sum() >= 0.8)) + 1)
```
<!--sortie-->
```text
variance totale : 5.000000000000001
parts (%)   : [52. 22. 14.  8.  4.]
cumul (%)   : [ 52.  74.  88.  96. 100.]
Kaiser (> 1): 2 | composantes pour 80 % : 3
```

**Corrigé 3.** (a) Multiplier une variable par 100 multiplie sa variance par $10\,000$ : la dépense, qui dominait déjà, **écrase** tout le reste. La première composante, qui expliquait déjà $98{,}8\ \%$ de la variance en euros, en explique alors pratiquement $100\ \%$ (le code arrondit à $1{,}0$) et pointe sur la dépense. (b) Avec la standardisation, chaque variable est divisée par son écart-type : **changer d'unité ne change rien** (la variable standardisée est la même). Les parts de variance sont identiques à celles du 3.1.5.

```python
import pandas as pd
c = pd.read_csv("donnees/clients.csv")
cols = ["age", "nb_commandes_an", "panier_moyen", "depense_annuelle", "duree_mois"]
X0 = c[cols].copy()
X1 = X0.copy(); X1["depense_annuelle"] = X1["depense_annuelle"] * 100        # en centimes

def parts(M, standardiser):
    M = (M - M.mean()) / M.std() if standardiser else M - M.mean()
    w = np.sort(np.linalg.eigvalsh(np.cov(M.to_numpy(), rowvar=False)))[::-1]
    return w / w.sum()

print("non standardisé, euros   :", parts(X0, False)[0].round(5))
print("non standardisé, centimes :", parts(X1, False)[0].round(5))
print("standardisé, euros       :", parts(X0, True).round(3))
print("standardisé, centimes     :", parts(X1, True).round(3))
```
<!--sortie-->
```text
non standardisé, euros   : 0.98789
non standardisé, centimes : 1.0
standardisé, euros       : [0.442 0.214 0.194 0.125 0.025]
standardisé, centimes     : [0.442 0.214 0.194 0.125 0.025]
```

**Corrigé 4.** (a) Les colonnes de $Z$ sont centrées, donc $\operatorname{Cov}(\mathbf t_i,\mathbf t_j)=\frac1{n-1}\mathbf v_i^\top Z^\top Z\,\mathbf v_j=\mathbf v_i^\top R\,\mathbf v_j=\lambda_j\,\mathbf v_i^\top\mathbf v_j$ (car $R\mathbf v_j=\lambda_j\mathbf v_j$). Les vecteurs propres d'une matrice symétrique sont orthonormés : $\mathbf v_i^\top\mathbf v_j=\delta_{ij}$. D'où $\operatorname{Cov}(\mathbf t_i,\mathbf t_j)=\lambda_j\delta_{ij}$.

(b) $\operatorname{Cov}(\mathbf z_i,\mathbf t_j)=\frac1{n-1}\mathbf z_i^\top Z\mathbf v_j=(R\mathbf v_j)_i=\lambda_jv_{ij}$. Comme $\operatorname{Var}(\mathbf z_i)=1$ et $\operatorname{Var}(\mathbf t_j)=\lambda_j$, la corrélation vaut $\dfrac{\lambda_jv_{ij}}{1\times\sqrt{\lambda_j}}=v_{ij}\sqrt{\lambda_j}$.

(c)

```python
Z = ((X0 - X0.mean()) / X0.std()).to_numpy()
R = np.corrcoef(Z, rowvar=False)
w, V = np.linalg.eigh(R)
o = np.argsort(w)[::-1]
w, V = w[o], V[:, o]
T = Z @ V
print("variances des scores :", T.var(axis=0, ddof=1).round(4))
print("valeurs propres      :", w.round(4))
corr_scores = np.corrcoef(T, rowvar=False)
print("plus grande corrélation entre deux scores différents :", np.abs(corr_scores - np.eye(5)).max().round(10))
cor_var_comp = np.array([[np.corrcoef(Z[:, i], T[:, j])[0, 1] for j in range(5)] for i in range(5)])
print("cor(variable, composante) = v * sqrt(lambda) ?", np.allclose(cor_var_comp, V * np.sqrt(w)))
```
<!--sortie-->
```text
variances des scores : [2.2115 1.0702 0.9684 0.6256 0.1242]
valeurs propres      : [2.2115 1.0702 0.9684 0.6256 0.1242]
plus grande corrélation entre deux scores différents : 0.0
cor(variable, composante) = v * sqrt(lambda) ? True
```

**Corrigé 5.** (a) On lit les parts cumulées : $0{,}748$ avec quatre composantes, $0{,}818$ avec cinq : il en faut **cinq**. C'est beaucoup pour huit questions, et c'est instructif : la règle des 80 % est ici bien moins sévère que Kaiser et l'analyse parallèle, qui retiennent deux composantes ; le questionnaire contient deux dimensions nettes, mais chaque question a aussi une grande part de variance qui lui est propre (3.2). (b) La reconstruction avec $k$ composantes a pour erreur $(n-1)\sum_{j>k}\lambda_j$ ; la RMSE par case vaut $\sqrt{\text{erreur}/(np)}$. Avec $0$ composante, on reconstruit chaque case par $0$ (la moyenne des variables standardisées) et l'erreur est la variance totale $(n-1)p$ ; la RMSE vaut alors à peu près $1$ (l'écart-type des variables standardisées). (c) Vérification par le code : avec deux composantes, la RMSE tombe de $1{,}000$ à $0{,}643$, et l'erreur totale ($4\,007{,}5$) coïncide exactement avec la formule.

```python
q = pd.read_csv("donnees/enquete_satisfaction.csv")
Q = q[[f"q{j}" for j in range(1, 9)]]
Zq = ((Q - Q.mean()) / Q.std()).to_numpy()
n, p = Zq.shape
w, V = np.linalg.eigh(np.corrcoef(Zq, rowvar=False))
o = np.argsort(w)[::-1]
w, V = w[o], V[:, o]

cumul = (w / w.sum()).cumsum()
print("composantes pour au moins 80 % :", int(np.argmax(cumul >= 0.8)) + 1, "(parts cumulées :", cumul.round(3).tolist(), ")")

for k in (0, 2):
    Vk = V[:, :k]
    erreur = ((Zq - Zq @ Vk @ Vk.T) ** 2).sum()
    print(f"k = {k} : erreur totale = {erreur:.1f}, théorie (n-1) x somme(valeurs jetées) = {(n - 1) * w[k:].sum():.1f}, RMSE par case = {np.sqrt(erreur / (n * p)):.3f}")
```
<!--sortie-->
```text
composantes pour au moins 80 % : 5 (parts cumulées : [0.35, 0.586, 0.675, 0.748, 0.818, 0.887, 0.946, 1.0] )
k = 0 : erreur totale = 9688.0, théorie (n-1) x somme(valeurs jetées) = 9688.0, RMSE par case = 1.000
k = 2 : erreur totale = 4007.5, théorie (n-1) x somme(valeurs jetées) = 4007.5, RMSE par case = 0.643
```

**Corrigé 6.** (a) $\ell_1^2=\dfrac{r_{12}r_{13}}{r_{23}}=\dfrac{0{,}48\times0{,}40}{0{,}30}=0{,}64$, donc $\ell_1=0{,}8$ ; $\ell_2=0{,}48/0{,}8=0{,}6$ ; $\ell_3=0{,}40/0{,}8=0{,}5$. Communalités : $0{,}64;\ 0{,}36;\ 0{,}25$. Unicités : $0{,}36;\ 0{,}64;\ 0{,}75$. Contrôle : $\ell_2\ell_3=0{,}30=r_{23}$ ✓. (b) La question 1 : saturation la plus forte ($0{,}8$) et unicité la plus faible. (c) Avec $r_{23}=0{,}15$ : $\ell_1^2=0{,}48\times0{,}40/0{,}15=1{,}28>1$. Une communalité supérieure à 1 est **impossible** (elle dépasserait la variance de la variable, soit une unicité négative $1-1{,}28=-0{,}28$) : c'est un **cas de Heywood**. Il signale que le modèle à un facteur est incompatible avec ces corrélations (par exemple, la question 1 est trop corrélée aux deux autres par rapport à leur corrélation mutuelle), ou que l'échantillon est trop petit.

```python
for r23 in (0.30, 0.15):
    l1_carre = 0.48 * 0.40 / r23
    print(f"r23 = {r23} : l1^2 = {l1_carre:.2f}", "-> impossible (cas de Heywood)" if l1_carre > 1 else f"-> l1 = {np.sqrt(l1_carre):.2f}")
```
<!--sortie-->
```text
r23 = 0.3 : l1^2 = 0.64 -> l1 = 0.80
r23 = 0.15 : l1^2 = 1.28 -> impossible (cas de Heywood)
```

**Corrigé 7.** (a) Communalités : $0{,}49+0{,}09=0{,}58$ ; $0{,}36+0{,}16=0{,}52$ ; $0{,}04+0{,}64=0{,}68$ ; $0{,}09+0{,}49=0{,}58$. (b) Voir le code : $\Lambda^*$ est différente de $\Lambda$ mais communalités et $\Lambda\Lambda^\top$ sont identiques, puisque $\Lambda^*\Lambda^{*\top}=\Lambda TT^\top\Lambda^\top=\Lambda\Lambda^\top$. (c) Comme l'ajustement est strictement le même pour tous les angles, les données **ne peuvent pas choisir** entre « la saturation de la question 1 sur le facteur 1 vaut $0{,}7$ » et « elle vaut $0{,}66$ » : seule la convention de rotation (varimax, etc.) fixe une valeur.

```python
Lam = np.array([[0.7, 0.3], [0.6, 0.4], [0.2, 0.8], [0.3, 0.7]])
th = np.deg2rad(30)
T = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
Lam2 = Lam @ T
print("communalités avant :", (Lam**2).sum(axis=1).round(3))
print("communalités après :", (Lam2**2).sum(axis=1).round(3))
print("Lambda* =\n", Lam2.round(3))
print("même Lambda Lambda' :", np.allclose(Lam @ Lam.T, Lam2 @ Lam2.T))
```
<!--sortie-->
```text
communalités avant : [0.58 0.52 0.68 0.58]
communalités après : [0.58 0.52 0.68 0.58]
Lambda* =
 [[ 0.756 -0.09 ]
 [ 0.72   0.046]
 [ 0.573  0.593]
 [ 0.61   0.456]]
même Lambda Lambda' : True
```

**Corrigé 8.** (a) Variance de la somme de $k=3$ variables de variance 1 et de covariance $0{,}5$ : $3+3\times2\times0{,}5=6$. Alpha : $\dfrac{3}{2}\Bigl(1-\dfrac36\Bigr)=0{,}75$. Cohérent avec Spearman-Brown : $\dfrac{3\times0{,}5}{1+2\times0{,}5}=0{,}75$ ✓. (b) On résout $\dfrac{0{,}5k}{1+0{,}5(k-1)}=0{,}9$, soit $0{,}5k=0{,}9\,(0{,}5+0{,}5k)=0{,}45+0{,}45k$, donc $0{,}05k=0{,}45$ et $k=9$. Il faut **neuf** questions de corrélation moyenne $0{,}5$ pour atteindre $\alpha=0{,}9$ : l'alpha augmente avec la longueur de l'échelle, ce qui rend toute comparaison entre échelles de longueurs différentes délicate.

```python
def alpha_std(k, r): return k * r / (1 + (k - 1) * r)
print("alpha, k = 3 :", alpha_std(3, 0.5))
print("k pour alpha >= 0,9 :", next(k for k in range(2, 50) if alpha_std(k, 0.5) >= 0.9), "| alpha(k = 9) =", round(alpha_std(9, 0.5), 3))
```
<!--sortie-->
```text
alpha, k = 3 : 0.75
k pour alpha >= 0,9 : 9 | alpha(k = 9) = 0.9
```

**Corrigé 9.** (a) Centres $(2;20)$. *Affectation* : $2,3,4$ vont avec $2$ ; $10$ est à $8$ de $2$ et à $10$ de $20$ : il va avec $2$ ; $12$ est à $10$ de $2$ et à $8$ de $20$ : il va avec $20$. Groupes $\{2,3,4,10\}$ et $\{12,20\}$. *Mise à jour* : centres $4{,}75$ et $16$. *Affectation* : $10$ est à $5{,}25$ de $4{,}75$ et à $6$ de $16$ ; $12$ est à $7{,}25$ et à $4$ : rien ne change. Fin. $W=(2{,}75^2+1{,}75^2+0{,}75^2+5{,}25^2)+(4^2+4^2)=7{,}5625+3{,}0625+0{,}5625+27{,}5625+32=70{,}75$. (b) Centres $(2;10)$ : groupes $\{2,3,4\}$ et $\{10,12,20\}$ ; centres $3$ et $14$ ; plus rien ne change. $W=(1+0+1)+(16+4+36)=58$. (c) Les deux exécutions **convergent**, mais vers deux solutions différentes ($70{,}75$ et $58$) : la seconde est meilleure. L'algorithme de Lloyd ne trouve qu'un **minimum local**, qui dépend de l'initialisation : d'où les redémarrages multiples et k-means++.

```python
pts = np.array([2, 3, 4, 10, 12, 20.0])
for init in ([2.0, 20.0], [2.0, 10.0]):
    centres = np.array(init)
    while True:
        g = np.abs(pts[:, None] - centres[None, :]).argmin(axis=1)
        nouveaux = np.array([pts[g == j].mean() for j in range(2)])
        if np.allclose(nouveaux, centres):
            break
        centres = nouveaux
    W = sum(((pts[g == j] - centres[j]) ** 2).sum() for j in range(2))
    print(f"départ {init} -> groupes {g.tolist()}, centres {centres.round(2).tolist()}, W = {W:.2f}")
```
<!--sortie-->
```text
départ [2.0, 20.0] -> groupes [0, 0, 0, 0, 1, 1], centres [4.75, 16.0], W = 70.75
départ [2.0, 10.0] -> groupes [0, 0, 0, 1, 1, 1], centres [3.0, 14.0], W = 58.00
```

**Corrigé 10.** *Point 4* (groupe $\{2,3,4\}$) : $a=(2+1)/2=1{,}5$ ; $b=(6+8+16)/3=10$ ; $s=(10-1{,}5)/10=0{,}85$. *Point 10* (groupe $\{10,12,20\}$) : $a=(2+10)/2=6$ ; $b=(8+7+6)/3=7$ ; $s=(7-6)/7\approx0{,}143$. *Point 20* : $a=(10+8)/2=9$ ; $b=(18+17+16)/3=17$ ; $s=(17-9)/17\approx0{,}471$. Le point **10** est le moins bien classé : presque à égale distance des deux groupes (son groupe est étiré par le point extrême 20).

```python
from sklearn.metrics import silhouette_samples
s = silhouette_samples(pts.reshape(-1, 1), np.array([0, 0, 0, 1, 1, 1]))
print("silhouettes :", dict(zip(pts.astype(int).tolist(), s.round(3).tolist())))
print("silhouette moyenne :", s.mean().round(3))
```
<!--sortie-->
```text
silhouettes : {2: 0.875, 3: 0.909, 4: 0.85, 10: 0.143, 12: 0.444, 20: 0.471}
silhouette moyenne : 0.615
```

**Corrigé 11.** *Lien simple* (distance minimale entre groupes) : fusion de $\{A,B\}$ à $2$ ; puis $\{A,B\}$–$C$ vaut $\min(5;3)=3$, $\{A,B\}$–$D$ vaut $\min(9;7)=7$, $C$–$D$ vaut $4{,}5$ : on fusionne $C$ à $\{A,B\}$ à la hauteur $3$ ; enfin $D$ à la hauteur $\min(9;7;4{,}5)=4{,}5$. Hauteurs : $2;\,3;\,4{,}5$ (effet de **chaîne** : $A,B,C,D$ s'enchaînent). *Lien complet* (distance maximale) : $\{A,B\}$ à $2$ ; puis $\{A,B\}$–$C$ vaut $\max(5;3)=5$, $\{A,B\}$–$D$ vaut $9$, $C$–$D$ vaut $4{,}5$ : on fusionne $\{C,D\}$ à $4{,}5$ ; enfin $\{A,B\}$–$\{C,D\}$ vaut $\max(5;9;3;7)=9$. Hauteurs : $2;\,4{,}5;\,9$. *Lien moyen* : $\{A,B\}$ à $2$ ; $\{A,B\}$–$C$ vaut $(5+3)/2=4$, $\{A,B\}$–$D$ vaut $8$, $C$–$D$ vaut $4{,}5$ : on fusionne $C$ à $\{A,B\}$ à $4$ ; puis $D$ à $(9+7+4{,}5)/3\approx6{,}83$. Hauteurs : $2;\,4;\,6{,}83$. Les **trois arbres diffèrent** : le critère simple et le moyen rattachent $C$ à $\{A,B\}$, le critère complet préfère former $\{C,D\}$.

```python
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
D = np.array([[0, 2, 5, 9], [2, 0, 3, 7], [5, 3, 0, 4.5], [9, 7, 4.5, 0]], dtype=float)
for m in ["single", "complete", "average"]:
    L = linkage(squareform(D), method=m)
    print(f"{m:9s} : fusions (indices) = {L[:, :2].astype(int).tolist()}, hauteurs = {L[:, 2].round(3).tolist()}")
```
<!--sortie-->
```text
single    : fusions (indices) = [[0, 1], [2, 4], [3, 5]], hauteurs = [2.0, 3.0, 4.5]
complete  : fusions (indices) = [[0, 1], [2, 3], [4, 5]], hauteurs = [2.0, 4.5, 9.0]
average   : fusions (indices) = [[0, 1], [2, 4], [3, 5]], hauteurs = [2.0, 4.0, 6.833]
```

**Corrigé 12.** (a) et (b) par le code, ainsi qu'un point de comparaison indispensable : la silhouette qu'obtiendrait un nuage **sans aucun groupe**, mais de même taille et d'asymétrie comparable (variables log-normales, comme le sont le nombre de commandes et le panier). (c) Voir la discussion sous le code.

```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

act = c[c["nb_commandes_an"] > 0]
Z2 = ((act[["nb_commandes_an", "panier_moyen"]] - act[["nb_commandes_an", "panier_moyen"]].mean())
      / act[["nb_commandes_an", "panier_moyen"]].std()).to_numpy()

# nuage témoin : mêmes effectifs, variables asymétriques (log-normales) corrélées, mais AUCUN groupe
rng = np.random.default_rng(0)
temoin = np.exp(rng.multivariate_normal([0, 0], [[0.4, 0.15], [0.15, 0.3]], len(Z2)))
temoin = (temoin - temoin.mean(axis=0)) / temoin.std(axis=0)

lignes = []
for k in range(2, 7):
    sil_reel = silhouette_score(Z2, KMeans(n_clusters=k, n_init=10, random_state=0).fit(Z2).labels_)
    sil_temoin = silhouette_score(temoin, KMeans(n_clusters=k, n_init=10, random_state=0).fit(temoin).labels_)
    lignes.append({"k": k, "silhouette (clientes)": sil_reel, "silhouette (nuage sans groupe)": sil_temoin})
print(pd.DataFrame(lignes).set_index("k").round(3).to_string())

ref = KMeans(n_clusters=3, n_init=10, random_state=0).fit(Z2)
rng = np.random.default_rng(4)
ari = []
for _ in range(30):
    idx = rng.integers(0, len(Z2), len(Z2))
    km = KMeans(n_clusters=3, n_init=3, random_state=int(rng.integers(10**6))).fit(Z2[idx])
    ari.append(adjusted_rand_score(ref.labels_, km.predict(Z2)))
print(f"stabilité (k = 3) : ARI moyen = {np.mean(ari):.3f}, minimum = {np.min(ari):.3f}")
```
<!--sortie-->
```text
   silhouette (clientes)  silhouette (nuage sans groupe)
k                                                       
2                  0.422                           0.511
3                  0.450                           0.496
4                  0.392                           0.420
5                  0.375                           0.416
6                  0.358                           0.390
stabilité (k = 3) : ARI moyen = 0.920, minimum = 0.824
```

(a) La silhouette moyenne des clientes atteint son maximum en $k=3$ ($0{,}450$). Cette valeur tombe dans la zone « structure faible » ($0{,}25$ à $0{,}50$) et l'on pourrait être tenté de conclure à trois familles. Mais le **nuage témoin**, qui ne contient **aucun** groupe, obtient une silhouette **plus élevée à chaque $k$** ($0{,}511$ en $k=2$, $0{,}496$ en $k=3$). L'explication : des variables fortement **asymétriques** (longue queue vers les grandes valeurs) font que les k-means découpent le nuage en tranches « cœur dense » / « queue », et la silhouette récompense ce découpage. **Moralité : une silhouette ne se lit jamais seule, il faut une valeur de comparaison obtenue sur des données sans structure** ; ici, les clientes ne montrent aucune structure en groupes au-delà de ce que produit une simple asymétrie.

(b) La stabilité du découpage en trois groupes est bonne (ARI moyen $0{,}92$, minimum $0{,}82$) : la partition est reproductible. Comme au 3.3.5, **stabilité n'est pas existence** : ce sont des tranches reproductibles d'un nuage continu.

(c) *Conseil à la gérante :* « Vos clientes ne forment pas des familles distinctes selon le nombre de commandes et le panier : elles se répartissent sur un continuum, avec beaucoup de petites clientes et quelques très grosses. Pour vos relances, vous pouvez néanmoins utiliser trois tranches pratiques (peu actives, régulières, très actives), à condition de les voir comme des repères commodes, pas comme des types de clientes qui existeraient vraiment. »

**Corrigé 13.** (a) Seuil $=\dfrac{40+55}{2}+\dfrac{10^2}{55-40}\ln\dfrac{0{,}8}{0{,}2}=47{,}5+6{,}667\times1{,}386\approx56{,}74$ €. (b) $\mathbb P(\text{gros}\mid55)=\dfrac{0{,}2\,f_{55}(55)}{0{,}8\,f_{40}(55)+0{,}2\,f_{55}(55)}$ : calculé par le code, environ $0{,}435$. (c) **Non** : malgré un panier égal à la moyenne du groupe « gros panier », la commande est classée « petit panier » ($0{,}435<0{,}5$). Les gros paniers étant quatre fois plus rares, il faut une commande plus élevée ($\geq56{,}74$) pour faire basculer la décision : c'est l'effet de la probabilité a priori (3.5.1).

```python
from scipy.stats import norm
mu0, mu1, sig, pi0 = 40, 55, 10, 0.8
seuil = (mu0 + mu1) / 2 + sig**2 / (mu1 - mu0) * np.log(pi0 / (1 - pi0))
print("seuil de décision :", round(seuil, 2), "€")
for x in (50, 55, 60):
    a = pi0 * norm.pdf(x, mu0, sig); b = (1 - pi0) * norm.pdf(x, mu1, sig)
    print(f"panier de {x} € : P(gros panier | x) = {b / (a + b):.3f}")
```
<!--sortie-->
```text
seuil de décision : 56.74 €
panier de 50 € : P(gros panier | x) = 0.267
panier de 55 € : P(gros panier | x) = 0.435
panier de 60 € : P(gros panier | x) = 0.620
```

**Corrigé 14.** (a) $n=150$ ; marges des lignes $80$ et $70$ ; marges des colonnes $50$, $60$, $40$. Effectifs attendus : $\frac{80\times50}{150}\approx26{,}67$, $\frac{80\times60}{150}=32$, $\frac{80\times40}{150}\approx21{,}33$ pour Réseaux, et $23{,}33$, $28$, $18{,}67$ pour la boutique. $\chi^2=\frac{13{,}33^2}{26{,}67}+\frac{2^2}{32}+\frac{11{,}33^2}{21{,}33}+\frac{13{,}33^2}{23{,}33}+\frac{2^2}{28}+\frac{11{,}33^2}{18{,}67}\approx6{,}67+0{,}13+6{,}02+7{,}62+0{,}14+6{,}88\approx27{,}5$ ; inertie totale $\chi^2/n\approx0{,}183$. (b) Un tableau $2\times3$ a $\min(2,3)-1=1$ axe non trivial. (c) Voir le code ; la modalité de délai la plus proche d'Réseaux sur l'axe est « court » (Réseaux a $50\ \%$ de délais courts contre $14\ \%$ pour la boutique).

```python
from scipy import stats
N = np.array([[40, 30, 10], [10, 30, 30]], dtype=float)
chi2 = stats.chi2_contingency(N, correction=False)[0]
P = N / N.sum(); r, cc = P.sum(axis=1), P.sum(axis=0)
S = (P - np.outer(r, cc)) / np.sqrt(np.outer(r, cc))
U, sv, Vt = np.linalg.svd(S, full_matrices=False)
F = (U / np.sqrt(r)[:, None]) * sv
G = (Vt.T / np.sqrt(cc)[:, None]) * sv
print("khi-deux =", round(chi2, 2), "| khi-deux / n =", round(chi2 / N.sum(), 4))
print("inerties des axes :", (sv**2).round(4), "| somme :", (sv**2).sum().round(4))
print("axe 1, lignes   :", pd.Series(F[:, 0], index=["Réseaux", "Boutique"]).round(3).to_dict())
print("axe 1, colonnes :", pd.Series(G[:, 0], index=["court", "moyen", "long"]).round(3).to_dict())
```
<!--sortie-->
```text
khi-deux = 27.46 | khi-deux / n = 0.183
inerties des axes : [0.183 0.   ] | somme : 0.183
axe 1, lignes   : {'Réseaux': -0.4, 'Boutique': 0.457}
axe 1, colonnes : {'court': -0.535, 'moyen': 0.067, 'long': 0.568}
```

---

## Bilan du chapitre 3

Vous savez maintenant :

- **résumer** un tableau de variables numériques par une **ACP** : l'écrire comme la diagonalisation de la matrice de covariance (ou la SVD du tableau centré), choisir entre covariance et corrélation (**standardiser** quand les unités diffèrent), choisir le nombre de composantes (éboulis, Kaiser, **analyse parallèle**), lire saturations, scores et biplot, et mesurer ce que l'on perd (somme des valeurs propres jetées) ;
- distinguer l'ACP, qui **résume**, de l'**analyse factorielle**, qui **modélise** les corrélations par des facteurs cachés ($\Sigma=\Lambda\Lambda^\top+\Psi$) ; estimer, **tester l'ajustement**, choisir le nombre de facteurs, **faire tourner** les axes (varimax) sans changer l'ajustement, et construire des échelles de mesure (alpha de Cronbach) ;
- **classer sans étiquettes** : les **k-means** (algorithme de Lloyd, k-means++, minimum local), la **classification hiérarchique** (critères d'agrégation, dendrogramme) ; **choisir $k$** (coude, silhouette) et surtout **vérifier qu'il y a des groupes** (silhouette, stabilité par bootstrap et ARI) ;
- (en option) étendre l'idée aux **variables qualitatives** par l'**analyse des correspondances** (SVD des résidus standardisés, inertie $=\chi^2/n$) et l'**ACM** ;
- (en option) passer des groupes inconnus aux groupes connus avec l'**analyse discriminante** : règle de Bayes avec des classes gaussiennes, LDA (frontières linéaires) et QDA, lien avec la **régression logistique**, projection de Fisher.

Un fil rouge traverse le chapitre : **une méthode descriptive rend toujours un résultat**, même sur du bruit. Un axe, un facteur, un groupe, une carte n'ont de valeur qu'accompagnés de leurs **diagnostics** (parts d'inertie et analyse parallèle, test d'ajustement, silhouette et stabilité, khi-deux avant de lire une carte).

Le chapitre 4 change d'horizon : après les données « en coupe » (un instantané de clientes), les **séries temporelles**, où l'ordre des observations compte et où la mémoire du passé devient l'information principale. Les ventes mensuelles de la boutique, de 2016 à 2025, nous y attendent.
