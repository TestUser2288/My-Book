## 3.5 p-valeurs, puissance et tests multiples

Au 3.4, nous avons *utilisé* la p-valeur. Voici maintenant comment ne pas s'en servir de travers. Cette section est celle qui vous évitera le plus d'erreurs concrètes : une bonne partie des « découvertes » publiées qui ne se reproduisent pas viennent de ce que nous allons voir.

### 3.5.1 Ce que la p-valeur est vraiment

> 📐 **Définition.** La **p-valeur** est la probabilité, calculée **en supposant $H_0$ vraie**, d'obtenir une statistique de test **au moins aussi extrême** que celle observée.

$$p=P\bigl(\text{résultat aussi extrême ou plus}\ \big|\ H_0\bigr).$$

Observez la direction du conditionnement : c'est $P(\text{données}\mid H_0)$ et **non** $P(H_0\mid\text{données})$. Nous avons vu au 2.1 que **inverser un conditionnement est l'erreur classique**.

Pour la sentir, rien de mieux que de fabriquer un monde où $H_0$ est vraie et de regarder les p-valeurs qu'on obtient. Simulons 10 000 tests de Student de deux groupes de 30 individus **tirés dans la même loi** (donc aucune vraie différence) :

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(1)
pvals_h0 = np.array([stats.ttest_ind(rng.normal(0, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])

print("proportion de p < 0,05 quand H0 est vraie :", round((pvals_h0 < 0.05).mean(), 4))
print("proportion de p < 0,01                     :", round((pvals_h0 < 0.01).mean(), 4))
print("proportion de p < 0,50                     :", round((pvals_h0 < 0.50).mean(), 4))
print("moyenne des p-valeurs                      :", round(pvals_h0.mean(), 3))
```
<!--sortie-->
```text
proportion de p < 0,05 quand H0 est vraie : 0.0486
proportion de p < 0,01                     : 0.0103
proportion de p < 0,50                     : 0.5013
moyenne des p-valeurs                      : 0.499
```

Quand $H_0$ est vraie, **la p-valeur suit une loi uniforme sur $[0,1]$** : 5 % des tests donnent $p<0{,}05$, 1 % donnent $p<0{,}01$, etc. C'est exactement ce que signifie « niveau $\alpha=5\,\%$ » : **un test sur vingt crie au loup à tort** quand il n'y a rien. Ce n'est pas un défaut du test, c'est sa définition.

Et quand $H_0$ est **fausse** ? Les p-valeurs se tassent vers 0 :

```python
pvals_h1 = np.array([stats.ttest_ind(rng.normal(0.8, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])
print("avec un vrai effet (d = 0,8) : proportion de p < 0,05 :", round((pvals_h1 < 0.05).mean(), 3))
print("histogramme (10 classes) sous H0 :", np.histogram(pvals_h0, bins=10, range=(0, 1))[0])
print("histogramme (10 classes) sous H1 :", np.histogram(pvals_h1, bins=10, range=(0, 1))[0])
```
<!--sortie-->
```text
avec un vrai effet (d = 0,8) : proportion de p < 0,05 : 0.865
histogramme (10 classes) sous H0 : [ 980 1008 1028 1006  991  985 1036  964 1024  978]
histogramme (10 classes) sous H1 : [9248  419  160   62   47   25   16    9    7    7]
```

Sous $H_0$, l'histogramme est **plat** ; sous $H_1$, il est entassé à gauche. C'est un outil de diagnostic précieux : si vous testez des milliers de variables et que l'histogramme de vos p-valeurs est plat, il n'y a probablement **rien** à trouver.

### 3.5.2 Ce que la p-valeur n'est pas

> ⚠️ **Cinq contresens fréquents.** Une p-valeur de 0,03 ne signifie **pas** :
>
> 1. que $H_0$ a 3 % de chances d'être vraie ;
> 2. que $H_1$ a 97 % de chances d'être vraie ;
> 3. que l'effet est **grand** ou **important** ;
> 4. que l'on obtiendrait de nouveau $p<0{,}05$ en refaisant l'étude (la **reproductibilité** dépend de la puissance) ;
> 5. qu'on a 3 % de chances de se tromper en rejetant $H_0$.

**Le point 5 mérite une démonstration**, car il est lourd de conséquences. Le risque réel de se tromper quand on rejette dépend de la **proportion d'hypothèses qui sont vraies** au départ : on retrouve la formule de Bayes de la section 2.1 et l'erreur du taux de base !

> 💡 **Exemple.** Yasmine teste 1 000 idées d'amélioration (couleur d'un bouton, texte d'une promotion, ordre des produits…). Réalistement, **10 %** seulement ont un vrai effet (100 vraies idées, 900 inutiles). Son test a un niveau $\alpha=5\,\%$ et une puissance de 80 %.
>
> - Vraies idées détectées : $100\times0{,}80=80$.
> - Idées inutiles « détectées » à tort : $900\times0{,}05=45$.
> - Au total, 125 résultats « significatifs », dont **45 sont des faux positifs**.

$$P(\text{fausse découverte}\mid\text{significatif})=\frac{45}{125}=36\,\%.$$

Plus d'un résultat « significatif » sur trois est faux, alors que $\alpha$ n'est que de 5 % ! Même mécanisme que l'alerte antifraude du 2.1.6. C'est pourquoi on exige des preuves plus fortes pour des hypothèses peu plausibles a priori (« des affirmations extraordinaires exigent des preuves extraordinaires »).

```python
alpha, puissance, part_vraies = 0.05, 0.80, 0.10
vrais_positifs = part_vraies * puissance
faux_positifs = (1 - part_vraies) * alpha
print("proportion de faux parmi les significatifs :", round(faux_positifs / (vrais_positifs + faux_positifs), 3))
```
<!--sortie-->
```text
proportion de faux parmi les significatifs : 0.36
```

### 3.5.3 Signification statistique ≠ importance pratique

Avec assez de données, **n'importe quelle** différence, même ridicule, devient « significative ». Un exemple extrême : deux versions d'une page ont des taux de conversion de 20,00 % et 20,10 %, mesurés sur 10 millions de visiteurs chacune.

```python
nA = nB = 10_000_000
pA, pB = 0.2000, 0.2010
p_pool = (pA + pB) / 2
z = (pB - pA) / np.sqrt(p_pool * (1 - p_pool) * (2 / nA))
print("z =", round(z, 2), "   p-valeur =", f"{2 * stats.norm.sf(z):.1e}")
print("gain absolu :", round((pB - pA) * 100, 2), "point de pourcentage")
```
<!--sortie-->
```text
z = 5.58    p-valeur = 2.3e-08
gain absolu : 0.1 point de pourcentage
```

La p-valeur est inférieure à 0,001 (hautement « significatif »), mais le gain est de **0,1 point** de conversion. Est-il utile ? Cela dépend du coût du changement, pas de la p-valeur. **Toujours rapporter la taille de l'effet et son intervalle de confiance**, jamais seulement « $p<0{,}05$ ».

### 3.5.4 La puissance : savoir si l'on peut voir ce qu'on cherche

> 💡 **Intuition.** Un test est comme un détecteur de métaux. Un détecteur peu sensible ne signale pas un petit objet enterré profondément : **l'absence de signal ne prouve pas l'absence d'objet**. La **puissance** $1-\beta$ est la probabilité que le test détecte un effet **s'il existe vraiment** (de taille donnée).

La puissance dépend de quatre choses liées entre elles :

| Facteur | Si... | ...alors la puissance |
|---|---|---|
| **Taille de l'effet** | grandit | augmente |
| **Taille d'échantillon** $n$ | grandit | augmente |
| **Dispersion** des données | diminue | augmente |
| **Niveau** $\alpha$ | on l'assouplit (0,10 au lieu de 0,05) | augmente (au prix de plus de faux positifs) |

**Retour sur notre test A/B du 3.4.5** (12 % contre 15 %, 1 000 visiteurs par version). Quelle était la puissance de cette expérience ? Sous $H_1$ avec $p_A=0{,}12$ et $p_B=0{,}15$, l'erreur-type de la différence est $\sqrt{\frac{0{,}12\times0{,}88}{1000}+\frac{0{,}15\times0{,}85}{1000}}=0{,}0154$, et la statistique de test est centrée sur $0{,}03/0{,}0154=1{,}95$. La puissance est donc la probabilité que cette statistique dépasse 1,96 :

$$\text{puissance}=P\bigl(Z>1{,}96-1{,}95\bigr)\approx0{,}50.$$

```python
def puissance_ab(p1, p2, n, alpha=0.05):
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    return stats.norm.cdf(abs(p2 - p1) / se - stats.norm.ppf(1 - alpha / 2))

print("puissance de l'expérience A/B du 3.4.5 :", round(puissance_ab(0.12, 0.15, 1000), 3))

# vérification par simulation
rng = np.random.default_rng(2)
rejets = 0
for _ in range(10_000):
    a, b = rng.binomial(1000, 0.12), rng.binomial(1000, 0.15)
    pp = (a + b) / 2000
    z = (b / 1000 - a / 1000) / np.sqrt(pp * (1 - pp) * 2 / 1000)
    rejets += abs(z) > 1.96
print("puissance simulée                     :", rejets / 10_000)
```
<!--sortie-->
```text
puissance de l'expérience A/B du 3.4.5 : 0.502
puissance simulée                     : 0.4954
```

La puissance n'était que de **50 %** : même si B est réellement meilleure de 3 points, l'expérience n'avait qu'**une chance sur deux** de le détecter. Le résultat « tout juste significatif » obtenu était donc de la chance autant que de l'information. Un test sous-dimensionné est un pari.

**Dimensionner l'expérience avant de la lancer.** On fixe l'effet minimal intéressant (ici +3 points), $\alpha=5\,\%$ et la puissance voulue (80 % est l'usage), puis on calcule $n$ :

$$n\ \text{par groupe}=\frac{(z_{1-\alpha/2}+z_{1-\beta})^2\,\bigl[p_1(1-p_1)+p_2(1-p_2)\bigr]}{(p_2-p_1)^2}.$$

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_par_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2

for delta in (0.05, 0.03, 0.02, 0.01):
    print(f"détecter 12 % -> {12 + delta * 100:.0f} % : {int(np.ceil(n_par_groupe(0.12, 0.12 + delta))):>6} visiteurs par version")
```
<!--sortie-->
```text
détecter 12 % -> 17 % :    775 visiteurs par version
détecter 12 % -> 15 % :   2033 visiteurs par version
détecter 12 % -> 14 % :   4435 visiteurs par version
détecter 12 % -> 13 % :  17166 visiteurs par version
```

Pour détecter 3 points avec 80 % de puissance, il faut **environ 2 000 visiteurs par version**, soit le double de ce que Yasmine avait. Pour détecter 1 point, il en faut **près de 18 000**. La loi en $1/\text{effet}^2$ est impitoyable : diviser l'effet par 3 multiplie les besoins par 9.

![À gauche : puissance d'un test A/B en fonction du nombre de visiteurs, pour trois tailles d'effet. À droite : si l'on « jette un œil » aux résultats de plus en plus souvent et que l'on s'arrête dès que p < 0,05, le taux de faux positifs explose (sous H₀).](figures/ch03-puissance.png)

> ⚠️ **L'arrêt prématuré (*peeking*).** Dans une expérience en ligne, la tentation est forte de regarder les résultats chaque jour et de s'arrêter dès que $p<0{,}05$. La figure de droite montre le résultat : en regardant 20 fois, **le taux de faux positifs passe de 5 % à environ 25 %**, alors qu'il n'y a *aucun* effet réel. Règle : **fixer la taille d'échantillon à l'avance et ne conclure qu'à la fin** (ou utiliser des méthodes séquentielles conçues pour cela).

### 3.5.5 Les tests multiples : le piège du « fouillis de comparaisons »

> 💡 **Intuition.** Si vous lancez un dé 20 fois, vous obtiendrez presque sûrement un 6 quelque part. Si vous effectuez 20 tests à 5 %, il est presque sûr que l'un d'eux sera « significatif » par pur hasard.

Raisonnons comme au 2.1.4 (« au moins un ») : si les 20 tests sont indépendants et que toutes les hypothèses nulles sont vraies, la probabilité d'avoir **au moins un faux positif** est

$$1-(1-\alpha)^m=1-0{,}95^{20}\approx0{,}64.$$

```python
for m_tests in (1, 5, 10, 20, 50, 100):
    print(f"{m_tests:>3} tests : P(au moins un faux positif) = {1 - 0.95 ** m_tests:.3f}")
```
<!--sortie-->
```text
  1 tests : P(au moins un faux positif) = 0.050
  5 tests : P(au moins un faux positif) = 0.226
 10 tests : P(au moins un faux positif) = 0.401
 20 tests : P(au moins un faux positif) = 0.642
 50 tests : P(au moins un faux positif) = 0.923
100 tests : P(au moins un faux positif) = 0.994
```

Avec 100 tests, c'est quasi certain (99,4 %). Dès que l'on teste plusieurs variables, segments ou métriques, il faut en tenir compte. C'est exactement ce qui arrive quand on « fouille » un jeu de données : on regarde 40 sous-groupes et on rapporte celui qui sort (« les femmes de 25 à 34 ans achètent plus le jeudi »).

**Les corrections classiques.** On teste $m$ hypothèses nulles, avec les p-valeurs $p_1,\dots,p_m$.

- **Bonferroni** : on rejette $H_i$ si $p_i<\alpha/m$. Simple, très prudent (le **FWER**, probabilité d'au moins un faux positif, reste ≤ $\alpha$) mais il perd beaucoup de puissance quand $m$ est grand.
- **Holm** : trie les p-valeurs et applique des seuils $\alpha/m,\ \alpha/(m-1),\dots$ ; **toujours** au moins aussi puissant que Bonferroni, avec la même garantie. À préférer.
- **Benjamini–Hochberg (BH)** : contrôle non plus le risque d'*un seul* faux positif, mais la **proportion de fausses découvertes** parmi les rejets (le **FDR**, *false discovery rate*). Moins strict, beaucoup plus puissant. Idéal en exploration (criblage de centaines de variables).

> 📐 **Procédure de Benjamini–Hochberg.** Trier les p-valeurs : $p_{(1)}\le\dots\le p_{(m)}$. Trouver le plus grand $k$ tel que $p_{(k)}\le\dfrac km\,\alpha$. Rejeter les hypothèses correspondant à $p_{(1)},\dots,p_{(k)}$.

Mettons-les à l'épreuve dans une simulation réaliste : Yasmine compare 100 catégories de produits entre deux périodes. Parmi elles, **10** ont vraiment changé (effet $d=1$) et **90** n'ont pas bougé. Chaque comparaison utilise 40 observations par période.

```python
rng = np.random.default_rng(5)
m_tests, n_vrais, n_obs = 100, 10, 40
vraie_diff = np.array([1.0] * n_vrais + [0.0] * (m_tests - n_vrais))
pvals = np.array([stats.ttest_ind(rng.normal(d, 1, n_obs), rng.normal(0, 1, n_obs)).pvalue for d in vraie_diff])

def bonferroni(p, alpha=0.05):
    return p < alpha / len(p)

def holm(p, alpha=0.05):
    ordre = np.argsort(p)
    rejet = np.zeros(len(p), dtype=bool)
    for rang, idx in enumerate(ordre):
        if p[idx] < alpha / (len(p) - rang):
            rejet[idx] = True
        else:
            break
    return rejet

def benjamini_hochberg(p, alpha=0.05):
    m = len(p)
    ordre = np.argsort(p)
    seuils = (np.arange(1, m + 1) / m) * alpha
    ok = p[ordre] <= seuils
    rejet = np.zeros(m, dtype=bool)
    if ok.any():
        k = np.max(np.where(ok)[0])
        rejet[ordre[: k + 1]] = True
    return rejet

vrai = vraie_diff > 0
for nom, rejet in [("aucune correction (p < 0,05)", pvals < 0.05), ("Bonferroni", bonferroni(pvals)),
                   ("Holm", holm(pvals)), ("Benjamini-Hochberg", benjamini_hochberg(pvals))]:
    tp, fp = int((rejet & vrai).sum()), int((rejet & ~vrai).sum())
    print(f"{nom:<30} découvertes = {tp + fp:>2}   vraies = {tp:>2}   fausses = {fp:>2}")
```
<!--sortie-->
```text
aucune correction (p < 0,05)   découvertes = 12   vraies =  9   fausses =  3
Bonferroni                     découvertes =  7   vraies =  7   fausses =  0
Holm                           découvertes =  7   vraies =  7   fausses =  0
Benjamini-Hochberg             découvertes =  9   vraies =  9   fausses =  0
```

Lecture (pour cette graine) : sans correction, on « découvre » 12 effets, dont **3 sont de fausses alertes** (sur 90 hypothèses nulles, on s'attend à environ 4,5 faux positifs à 5 %). Bonferroni et Holm n'en gardent que 7, **tous vrais**, mais au prix d'avoir **raté** 3 vrais effets. Benjamini-Hochberg en retrouve 9 vrais sans aucun faux ici ; par construction, il garantit seulement qu'en moyenne la part de fausses découvertes reste sous 5 %. Le compromis est net : plus on corrige strictement, moins on se trompe, mais plus on rate de vrais effets.

> ✅ **Quel choix pratique ?**
> - Décision importante, peu d'hypothèses, un faux positif coûteux (lancer un produit, un traitement) : **Holm** (ou Bonferroni).
> - Exploration de nombreuses hypothèses, où l'on vérifiera ensuite les candidats : **Benjamini-Hochberg**.
> - Le mieux de tout : **décider à l'avance** de la ou des questions testées. Une analyse exploratoire est une source d'hypothèses, pas une preuve.

### 3.5.6 Les bonnes pratiques, en dix lignes

1. Écrire $H_0$, $H_1$, $\alpha$ et le plan d'analyse **avant** de regarder les données.
2. Dimensionner l'échantillon pour une puissance d'au moins 80 %.
3. Ne pas s'arrêter dès que $p<0{,}05$ (*peeking*).
4. Compter **tous** les tests effectués, pas seulement ceux qui « marchent », et corriger si nécessaire.
5. Rapporter la **taille d'effet** et un **intervalle de confiance**, pas seulement la p-valeur.
6. Distinguer significativité statistique et importance pratique.
7. Ne pas dire « accepter $H_0$ » : dire « pas de preuve suffisante ».
8. Se méfier d'un résultat « juste significatif » (0,04) : il est fragile.
9. Marquer clairement ce qui est **exploratoire** et ce qui est **confirmatoire**.
10. Refaire l'expérience si la décision est importante : la **réplication** est la meilleure preuve.

> ✅ **À retenir (p-valeurs, puissance, tests multiples).**
>
> - $p=P(\text{données aussi extrêmes}\mid H_0)$. Sous $H_0$, elle est **uniforme** sur $[0,1]$ ; 5 % des tests donnent $p<0{,}05$ par hasard.
> - Ce n'est ni $P(H_0\mid\text{données})$, ni la taille de l'effet. Le taux de fausses découvertes dépend de la proportion d'hypothèses vraies (Bayes).
> - **Puissance** $=1-\beta$ : dépend de l'effet, de $n$, de la dispersion et de $\alpha$. Dimensionner avant l'expérience : $n\propto1/\text{effet}^2$.
> - **Tests multiples** : $1-(1-\alpha)^m$ ; corriger par **Holm** (FWER) ou **Benjamini-Hochberg** (FDR). Pas de *peeking*, pas de *p-hacking*.
