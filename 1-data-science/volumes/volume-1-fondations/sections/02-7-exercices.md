## 2.7 Exercices du chapitre 2

> 🧭 Même mode d'emploi qu'au chapitre 1 : cherchez d'abord, comparez ensuite. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (union).** Pour une newsletter : $P(\text{ouvre})=0{,}35$, $P(\text{clique})=0{,}25$, $P(\text{ouvre et clique})=0{,}10$. Quelle est la probabilité qu'un destinataire fasse **au moins une** des deux actions ? Qu'il ne fasse **aucune** ?

**Exercice 2 ⭐⭐ (Bayes).** Dans l'atelier d'un fournisseur, 2 % des bols sont défectueux. Un contrôle automatique signale 90 % des bols défectueux, mais aussi 4 % des bols corrects. Un bol est signalé : quelle est la probabilité qu'il soit réellement défectueux ? Interprétez.

**Exercice 3 ⭐ (« au moins un »).** Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. (a) Probabilité qu'au moins un colis soit endommagé parmi 50 ? (b) Combien de colis faut-il pour que cette probabilité dépasse 90 % ?

**Exercice 4 ⭐ (binomiale).** Sur 15 visiteurs d'une publicité, chacun achète avec la probabilité 0,3. Calculez $P(X=5)$, l'espérance et l'écart-type de $X$, et $P(X\ge8)$.

**Exercice 5 ⭐⭐ (Poisson et exponentielle).** Le service client reçoit en moyenne 4 appels par heure (processus de Poisson). (a) Probabilité de ne recevoir **aucun** appel pendant une demi-heure ? (b) Le temps d'attente entre deux appels est exponentiel : quelle est sa moyenne, et quelle est la probabilité d'attendre plus de 20 minutes ? (c) On a déjà attendu 10 minutes sans appel : quelle est la probabilité d'attendre **encore** 20 minutes ?

**Exercice 6 ⭐⭐ (normale).** Le poids des colis expédiés suit $\mathcal N(500\text{ g},\ 40^2)$. (a) Probabilité qu'un colis pèse moins de 450 g ? (b) Entre 460 et 540 g ? (c) Quel poids n'est dépassé que par 1 % des colis ?

**Exercice 7 ⭐⭐ (espérance et variance).** Un jeu de fidélité distribue : 0 € avec la probabilité 0,80 ; 10 € avec 0,15 ; 50 € avec 0,05. Calculez l'espérance, la variance et l'écart-type du gain. Si participer coûte 5 €, le jeu est-il favorable au client ? Et si le client joue 100 fois, quelle est l'espérance et l'écart-type de son gain total ?

**Exercice 8 ⭐⭐ (covariance).** Cinq clients ont noté le délai de livraison ($x=1,2,3,4,5$ jours) et leur satisfaction ($y=2,4,5,4,5$ sur 5). Calculez à la main la covariance (divisée par $n$), la variance de chaque variable et la corrélation. Vérifiez avec NumPy.

**Exercice 9 ⭐⭐⭐ (TCL).** Le panier d'un client a une moyenne de 45 € et un écart-type de 30 € (loi très asymétrique). On observe 100 clients. (a) Quelle est la loi approchée de la moyenne ? (b) Probabilité que la moyenne dépasse 50 € ? (c) Combien de clients faut-il observer pour que l'erreur-type de la moyenne soit inférieure à 1 € ? (d) Vérifiez (b) par simulation. Attention : une loi exponentielle de moyenne 45 a un écart-type de 45, pas 30 ; quelle loi asymétrique de moyenne 45 et d'écart-type 30 peut-on utiliser à la place ?

**Exercice 10 ⭐⭐⭐ (Markov).** Chaque jour, une machine est **en marche** (M) ou **en panne** (P). Si elle est en marche, elle tombe en panne le lendemain avec probabilité 0,1. Si elle est en panne, elle est réparée le lendemain avec probabilité 0,4. (a) Écrivez la matrice de transition. (b) Si elle est en marche aujourd'hui, quelle est la probabilité qu'elle le soit après-demain ? (c) Quelle est la proportion de temps passée en panne à long terme ?

### Corrigés

**Corrigé 1.** $P(\text{au moins une})=0{,}35+0{,}25-0{,}10=0{,}50$. Aucune : $1-0{,}50=0{,}50$. (On retranche l'intersection pour ne pas la compter deux fois ; le complémentaire de « au moins une » est « aucune ».)

**Corrigé 2.** Sur 10 000 bols : 200 défectueux, dont 180 signalés ; 9 800 corrects, dont 392 signalés à tort. Total des signalements : 572, dont 180 justifiés : $180/572\approx0{,}315$.

```python
p_def, sens, fausse = 0.02, 0.90, 0.04
p_signal = sens * p_def + fausse * (1 - p_def)
print("P(défectueux | signalé) =", round(sens * p_def / p_signal, 4))
```
<!--sortie-->
```text
P(défectueux | signalé) = 0.3147
```

Seulement **31,5 %** : même avec un bon contrôle, **deux bols signalés sur trois sont corrects**, car les défauts sont rares (erreur du taux de base). Ils justifient une seconde vérification plutôt qu'un rejet automatique.

**Corrigé 3.** (a) $1-0{,}98^{50}\approx0{,}636$. (b) On veut $1-0{,}98^n>0{,}9\iff0{,}98^n<0{,}1\iff n>\dfrac{\ln0{,}1}{\ln0{,}98}\approx113{,}97$, donc **114 colis**.

```python
import numpy as np
from scipy import stats
print("(a)", round(1 - 0.98**50, 4))
print("(b)", np.log(0.1) / np.log(0.98), "-> n =", int(np.ceil(np.log(0.1) / np.log(0.98))))
```
<!--sortie-->
```text
(a) 0.6358
(b) 113.97408559184939 -> n = 114
```

**Corrigé 4.** $P(X=5)=\binom{15}5\,0{,}3^5\,0{,}7^{10}$. $E[X]=np=4{,}5$ ; $\sigma=\sqrt{np(1-p)}=\sqrt{3{,}15}\approx1{,}775$ ; $P(X\ge8)=1-P(X\le7)$.

```python
X = stats.binom(15, 0.3)
print("P(X=5)  =", round(X.pmf(5), 4))
print("E, sigma=", X.mean(), round(X.std(), 3))
print("P(X>=8) =", round(X.sf(7), 4))
```
<!--sortie-->
```text
P(X=5)  = 0.2061
E, sigma= 4.5 1.775
P(X>=8) = 0.05
```

**Corrigé 5.** (a) Sur une demi-heure, $N\sim\text{Poisson}(4\times0{,}5=2)$ : $P(N=0)=e^{-2}\approx0{,}135$. (b) Le temps d'attente est $\text{Exp}(4/\text{h})$, de moyenne $1/4$ h $=15$ min. 20 min $=1/3$ h : $P(T>1/3)=e^{-4/3}\approx0{,}264$. (c) Par absence de mémoire, c'est la même probabilité : **0,264**.

```python
print("(a)", round(np.exp(-2), 4), round(stats.poisson(2).pmf(0), 4))
T = stats.expon(scale=1 / 4)               # unité : heure
print("(b)", round(T.sf(1 / 3), 4))
print("(c)", round(T.sf(10 / 60 + 1 / 3) / T.sf(10 / 60), 4))
```
<!--sortie-->
```text
(a) 0.1353 0.1353
(b) 0.2636
(c) 0.2636
```

**Corrigé 6.** (a) $z=(450-500)/40=-1{,}25$, $P=\Phi(-1{,}25)\approx0{,}106$. (b) $z$ de $-1$ à $+1$ : $\approx0{,}683$. (c) $z_{0{,}99}\approx2{,}326$, donc $500+2{,}326\times40\approx593$ g.

```python
W = stats.norm(500, 40)
print("(a)", round(W.cdf(450), 4))
print("(b)", round(W.cdf(540) - W.cdf(460), 4))
print("(c)", round(W.ppf(0.99), 1))
```
<!--sortie-->
```text
(a) 0.1056
(b) 0.6827
(c) 593.1
```

**Corrigé 7.** $E=0{,}15\times10+0{,}05\times50=1{,}5+2{,}5=4$ €. $E[X^2]=0{,}15\times100+0{,}05\times2500=15+125=140$, $\operatorname{Var}=140-16=124$, $\sigma\approx11{,}1$ €. À 5 € la partie, l'espérance du **gain net** est $4-5=-1$ € : défavorable en moyenne (c'est favorable à la boutique). Sur 100 parties (indépendantes) : espérance $100\times4=400$ €, variance $100\times124=12\,400$, écart-type $\sqrt{12400}\approx111$ €. Remarquez que l'écart-type relatif diminue : 111/400 = 28 % contre 11,1/4 = 278 % pour une seule partie.

```python
gains = np.array([0, 10, 50]); probas = np.array([0.8, 0.15, 0.05])
E = (gains * probas).sum(); V = (gains**2 * probas).sum() - E**2
print("E =", E, " Var =", round(V, 2), " sigma =", round(np.sqrt(V), 2))
print("100 parties : E =", 100 * E, " sigma =", round(np.sqrt(100 * V), 1))
```
<!--sortie-->
```text
E = 4.0  Var = 124.0  sigma = 11.14
100 parties : E = 400.0  sigma = 111.4
```

**Corrigé 8.** Moyennes $\bar x=3$, $\bar y=4$. Écarts : $x-\bar x=(-2,-1,0,1,2)$, $y-\bar y=(-2,0,1,0,1)$. Produits : $4,0,0,0,2$, de somme 6, donc $\operatorname{Cov}=6/5=1{,}2$. $\operatorname{Var}(x)=(4+1+0+1+4)/5=2$ ; $\operatorname{Var}(y)=(4+0+1+0+1)/5=1{,}2$. $\rho=\dfrac{1{,}2}{\sqrt{2\times1{,}2}}=\dfrac{1{,}2}{1{,}549}\approx0{,}775$. Lecture : la corrélation est *positive* : plus la livraison est lente, plus la satisfaction serait élevée ? Ce n'est pas plausible : avec seulement cinq points, c'est probablement un hasard de l'échantillon. Nous verrons au chapitre 3 comment tester si une corrélation observée est significative.

```python
x = np.array([1, 2, 3, 4, 5.0]); y = np.array([2, 4, 5, 4, 5.0])
print("cov =", ((x - x.mean()) * (y - y.mean())).mean(), "  var x, y =", x.var(), y.var())
print("rho =", round(np.corrcoef(x, y)[0, 1], 4))
```
<!--sortie-->
```text
cov = 1.2   var x, y = 2.0 1.2
rho = 0.7746
```

**Corrigé 9.** (a) Par le TCL, $\bar X_{100}\approx\mathcal N(45,\ 30^2/100)=\mathcal N(45,\ 3^2)$ : erreur-type 3 €. (b) $z=(50-45)/3\approx1{,}667$, $P(\bar X>50)\approx0{,}048$. (c) $\sigma/\sqrt n<1\iff n>900$. (d) Pour la simulation, une exponentielle de moyenne 45 a un écart-type de **45** (pas 30) : elle ne convient pas. On utilise une loi Gamma de moyenne 45 et d'écart-type 30 (forme $k=(45/30)^2=2{,}25$, échelle $\theta=30^2/45=20$). La simulation donne 5,1 % contre 4,8 % par le TCL : l'écart vient de l'asymétrie résiduelle à $n=100$.

```python
print("(b) TCL :", round(stats.norm(45, 3).sf(50), 4))
rng = np.random.default_rng(9)
echantillons = rng.gamma(shape=2.25, scale=20, size=(100_000, 100))
print("moyenne, écart-type du panier simulé :", echantillons.mean().round(2), echantillons.std().round(2))
print("(b) simulée :", round((echantillons.mean(axis=1) > 50).mean(), 4))
print("(c) n minimal :", (30 / 1) ** 2)
```
<!--sortie-->
```text
(b) TCL : 0.0478
moyenne, écart-type du panier simulé : 45.01 30.0
(b) simulée : 0.0512
(c) n minimal : 900.0
```

**Corrigé 10.** (a) $\mathbf{P}=\begin{pmatrix}0{,}9&0{,}1\\0{,}4&0{,}6\end{pmatrix}$ (lignes M, P). (b) $\mathbf{P}^2_{MM}=0{,}9\times0{,}9+0{,}1\times0{,}4=0{,}85$. (c) On cherche $\boldsymbol\pi=(\pi_M,\pi_P)$ avec $\boldsymbol\pi\mathbf P=\boldsymbol\pi$ : de la seconde colonne, $0{,}1\pi_M+0{,}6\pi_P=\pi_P$, soit $0{,}1\pi_M=0{,}4\pi_P$, donc $\pi_M=4\pi_P$ ; avec $\pi_M+\pi_P=1$ : $\pi_P=0{,}2$. La machine est en panne **20 % du temps** à long terme.

```python
P = np.array([[0.9, 0.1], [0.4, 0.6]])
print("P^2[M,M] =", np.linalg.matrix_power(P, 2)[0, 0])
w, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
print("loi stationnaire :", pi.round(3))
```
<!--sortie-->
```text
P^2[M,M] = 0.8500000000000001
loi stationnaire : [0.8 0.2]
```

---

## Bilan du chapitre 2

Vous savez maintenant :

- **calculer** des probabilités (complémentaire, union, conditionnel) et **inverser** un conditionnement avec Bayes, en vous méfiant de l'erreur du taux de base ;
- **modéliser** un phénomène par la bonne loi (Bernoulli, binomiale, Poisson, exponentielle, normale) et calculer des probabilités avec `scipy.stats` ;
- **résumer** une loi par son espérance et sa variance, et mesurer le lien entre deux variables par la covariance et la corrélation ;
- **comprendre** pourquoi une moyenne devient fiable (LGN) et pourquoi son erreur est normale (TCL), avec une erreur-type en $\sigma/\sqrt n$ ;
- (en option) **situer** tout cela dans le cadre de la théorie de la mesure et des processus stochastiques.

Le chapitre 3 retourne le problème : on ne **connaît** plus la loi, on a seulement des **données**, et il faut en déduire la loi. C'est la statistique.
