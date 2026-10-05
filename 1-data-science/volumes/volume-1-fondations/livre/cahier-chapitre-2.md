# Chapitre 2 : Probabilités — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 2 du livre (probabilités, lois, espérance et variance, loi des grands nombres, théorème central limite). Les **applications** sont de petites études guidées avec du code ; les **exercices** se travaillent d'abord à la main, puis se vérifient par le calcul. Vous aurez besoin de Python avec NumPy et SciPy. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

## Applications

### Application 2.1 — Classer des avis clients avec la formule de Bayes

**Contexte.** La gérante reçoit des dizaines d'avis par semaine. Elle a lu et étiqueté 40 avis : 28 positifs et 12 négatifs. Pour trois mots-clés, elle a compté dans combien d'avis de chaque type ils apparaissent :

| Mot | Avis positifs (sur 28) | Avis négatifs (sur 12) |
|---|---:|---:|
| « cassé » | 2 | 9 |
| « rapide » | 18 | 2 |
| « déçu » | 1 | 8 |

**Objectif.** Calculer la probabilité qu'un nouvel avis soit négatif, d'après les mots qu'il contient.

**Étape 1 : un seul mot, à la main.** Un avis contient « cassé ». Avec $P(\text{nég})=12/40=0{,}3$, $P(\text{cassé}\mid\text{nég})=9/12$ et $P(\text{cassé}\mid\text{pos})=2/28$, la formule de Bayes donne

$$P(\text{nég}\mid\text{cassé})=\frac{0{,}75\times0{,}3}{0{,}75\times0{,}3+\tfrac{2}{28}\times0{,}7}=\frac{0{,}225}{0{,}225+0{,}05}\approx0{,}818.$$

**Étape 2 : plusieurs mots à la fois.** Le filtre **naïf** de Bayes suppose les mots indépendants *sachant la classe* : on multiplie les vraisemblances de chaque mot, en tenant compte aussi des mots **absents** (probabilité $1-p$). On compare ensuite les deux classes. Écrivons-le en quelques lignes :

```python
import numpy as np
n_pos, n_neg = 28, 12
vus = {"cassé": (2, 9), "rapide": (18, 2), "déçu": (1, 8)}      # (avis positifs, avis négatifs)

def prob_negatif(presents, lissage=0):
    """P(négatif | mots présents), les autres mots du dictionnaire étant absents."""
    vrais = {"pos": n_pos / 40, "neg": n_neg / 40}                # a priori
    for mot, (kp, kn) in vus.items():
        pp = (kp + lissage) / (n_pos + 2 * lissage)
        pn = (kn + lissage) / (n_neg + 2 * lissage)
        vrais["pos"] *= pp if mot in presents else 1 - pp
        vrais["neg"] *= pn if mot in presents else 1 - pn
    return vrais["neg"] / (vrais["pos"] + vrais["neg"])

print("« cassé » et « déçu », sans « rapide » :", round(prob_negatif({"cassé", "déçu"}), 4))
print("« rapide » seulement                   :", round(prob_negatif({"rapide"}), 4))
```
<!--sortie-->
```text
« cassé » et « déçu », sans « rapide » : 0.9949
« rapide » seulement                   : 0.0102
```

Le premier avis a 99,5 % de chances d'être négatif ; le second, seulement 1,0 % (il est donc presque certainement positif). Les mots présents *et* les mots absents pèsent dans la balance.

**Étape 3 : le piège des zéros.** Un nouveau mot, « remboursement », apparaît dans 0 avis positif et 3 avis négatifs. Sa vraisemblance pour la classe positive vaut 0 : un seul de ces mots suffit à écraser toute l'information des autres, et le produit est nul. La parade classique est le **lissage de Laplace** : on ajoute 1 « fictif » à chaque comptage (et 2 au total), ce qui ne laisse jamais une probabilité à zéro.

```python
vus["remboursement"] = (0, 3)
avis = {"cassé", "rapide", "remboursement"}
print("sans lissage :", round(prob_negatif(avis), 4))
print("avec lissage :", round(prob_negatif(avis, lissage=1), 4))
```
<!--sortie-->
```text
sans lissage : 1.0
avec lissage : 0.7726
```

Sans lissage, le mot jamais vu dans un avis positif impose une probabilité de 100 % d'être négatif, quoi que dise le mot « rapide ». Avec lissage, on obtient 77 % : un verdict nuancé, où la contradiction entre « rapide » et « remboursement » est enfin visible.

**Pour aller plus loin.** Que se passe-t-il quand on change l'a priori (par exemple 50/50 au lieu de 70/30) ? Quelle est la sensibilité du résultat au lissage (essayez `lissage=0.1`) ?

### Application 2.2 — Voir pour croire : trois résultats par simulation

**Contexte.** Trois résultats du chapitre peuvent sembler incroyables. La simulation est la meilleure façon de s'en convaincre : on joue le jeu des milliers de fois et on compte.

**Partie A — Monty Hall.** Trois portes, une voiture ; vous choisissez la porte 0 ; l'animateur ouvre une porte vide parmi les deux autres. Gagne-t-on plus en changeant ?

```python
import numpy as np
rng = np.random.default_rng(3)
voiture = rng.integers(0, 3, size=100_000)         # porte gagnante de chaque partie
# on a toujours choisi la porte 0 ; si on change, on gagne exactement quand 0 était mauvaise
print("gain en restant   :", round((voiture == 0).mean(), 3))
print("gain en changeant :", round((voiture != 0).mean(), 3))
```
<!--sortie-->
```text
gain en restant   : 0.333
gain en changeant : 0.667
```

**Partie B — Anniversaires.** Dans un groupe de $n$ personnes, quelle est la probabilité qu'au moins deux partagent leur anniversaire ? On compare la formule exacte (par le complémentaire) et la simulation de 20 000 groupes.

```python
def exacte(n):
    return 1 - np.prod([(365 - i) / 365 for i in range(n)])

rng = np.random.default_rng(7)
for n in (10, 23, 40):
    groupes = rng.integers(0, 365, size=(20_000, n))
    simulee = np.mean([len(set(g)) < n for g in groupes])       # y a-t-il un doublon ?
    print(f"n = {n:>2} : exacte = {exacte(n):.3f}   simulée = {simulee:.3f}")
```
<!--sortie-->
```text
n = 10 : exacte = 0.117   simulée = 0.119
n = 23 : exacte = 0.507   simulée = 0.503
n = 40 : exacte = 0.891   simulée = 0.892
```

**Partie C — Un processus de Poisson par ses temps d'attente.** Les commandes arrivent au rythme de 3 par heure. On construit le processus **uniquement** à partir de temps d'attente exponentiels, puis on compte les commandes de chaque heure et on compare à la loi de Poisson de paramètre 3.

```python
from scipy import stats
rng = np.random.default_rng(15)
lam, n_heures = 3, 20_000
comptes = np.empty(n_heures, dtype=int)
for h in range(n_heures):
    t, k = rng.exponential(1 / lam), 0
    while t <= 1.0:                       # tant qu'on est dans l'heure
        k += 1
        t += rng.exponential(1 / lam)     # temps d'attente jusqu'à la commande suivante
    comptes[h] = k
print("moyenne, variance des comptes :", comptes.mean().round(3), comptes.var().round(3), "(théorie : 3 et 3)")
for k in range(5):
    print(f"P(N = {k}) : simulée = {(comptes == k).mean():.4f}   Poisson(3) = {stats.poisson(3).pmf(k):.4f}")
```
<!--sortie-->
```text
moyenne, variance des comptes : 2.998 2.932 (théorie : 3 et 3)
P(N = 0) : simulée = 0.0493   Poisson(3) = 0.0498
P(N = 1) : simulée = 0.1479   Poisson(3) = 0.1494
P(N = 2) : simulée = 0.2207   Poisson(3) = 0.2240
P(N = 3) : simulée = 0.2313   Poisson(3) = 0.2240
P(N = 4) : simulée = 0.1688   Poisson(3) = 0.1680
```

Repères : en B, l'écart entre exacte et simulée ne dépasse pas 0,004 ; en C, la moyenne des comptes vaut 2,998 et leur variance 2,93.

**Questions.** (1) Que valent les écarts entre simulation et théorie, et comment évoluent-ils si l'on multiplie le nombre de répétitions par 100 ? (2) Dans la partie C, la variance observée est-elle proche de la moyenne ? Que cela dit-il de la loi de Poisson ?

### Application 2.3 — Dimensionner un échantillon : Tchebychev contre TCL

**Contexte.** La boutique veut estimer son taux de conversion (proche de 0,205) à ±2 points avec 95 % de confiance. Combien de visiteurs faut-il observer ? Le livre donne deux réponses : la borne de Tchebychev (valable pour toute loi, donc pessimiste) et celle du théorème central limite. Voyons ce que valent vraiment ces deux bornes.

**Étape 1 : les deux tailles.**

```python
import numpy as np
p, eps = 0.205, 0.02
n_tcheb = p * (1 - p) / (0.05 * eps**2)
n_tcl = (1.96 / eps) ** 2 * p * (1 - p)
print(f"Tchebychev : {n_tcheb:,.0f} visiteurs    TCL : {n_tcl:,.0f} visiteurs    rapport : {n_tcheb / n_tcl:.2f}")
```
<!--sortie-->
```text
Tchebychev : 8,149 visiteurs    TCL : 1,565 visiteurs    rapport : 5.21
```

**Étape 2 : la couverture réelle.** Pour une taille $n$ donnée, on simule 100 000 échantillons et on calcule la proportion de ceux dont le taux observé est à moins de 2 points de la vérité. Cette proportion devrait dépasser 95 %.

```python
rng = np.random.default_rng(6)
for n in (500, 1000, 1565, 3000, 8150):
    taux = rng.binomial(n, p, size=100_000) / n
    print(f"n = {n:>5} : couverture = {(np.abs(taux - p) <= eps).mean():.4f}")
```
<!--sortie-->
```text
n =   500 : couverture = 0.7321
n =  1000 : couverture = 0.8827
n =  1565 : couverture = 0.9508
n =  3000 : couverture = 0.9932
n =  8150 : couverture = 1.0000
```

**Lecture et questions.** La couverture passe de 73 % pour 500 visiteurs à 95,1 % pour 1 565 : c'est la prédiction du TCL. À 8 150, elle vaut 100 % (à la précision de la simulation).

(1) Quelle taille est vraiment nécessaire ? Tchebychev est-il « faux » ? (2) À $n=8\,150$, quelle est la couverture ? Que signifie « borne pessimiste » ? (3) Si la gérante veut une marge de ±1 point au lieu de ±2, par combien faut-il multiplier $n$ ? Vérifiez par la formule, puis par simulation.

### Application 2.4 — Chaîne de Markov : la valeur à long terme d'un client

**Contexte.** Chaque mois, un client est Actif (A), Occasionnel (O) ou Inactif (I). La gérante a estimé la matrice de transition $\mathbf{P}$ (lignes : état actuel ; colonnes : état du mois suivant) et la contribution mensuelle moyenne de chaque état : 30 €, 10 € et 0 €. Elle envisage une campagne de relance qui ferait passer la probabilité Inactif→Actif de 0,10 à 0,20.

```python
import numpy as np
P = np.array([[0.80, 0.15, 0.05],
              [0.30, 0.50, 0.20],
              [0.10, 0.20, 0.70]])
valeur = np.array([30, 10, 0])

def loi_stationnaire(P):
    """Vecteur propre de P^T pour la valeur propre 1, normalisé pour sommer à 1."""
    w, V = np.linalg.eig(P.T)
    pi = np.real(V[:, np.argmin(np.abs(w - 1))])
    return pi / pi.sum()

pi = loi_stationnaire(P)
print("loi stationnaire :", pi.round(3), "  revenu mensuel moyen :", round(pi @ valeur, 2), "€")
```
<!--sortie-->
```text
loi stationnaire : [0.5  0.25 0.25]   revenu mensuel moyen : 17.5 €
```

**Étape 2 : la relance.** On modifie la ligne « Inactif » (0,20 vers Actif, 0,20 vers Occasionnel, donc 0,60 de rester inactif) et on recalcule.

```python
P_relance = P.copy()
P_relance[2] = [0.20, 0.20, 0.60]
gain = loi_stationnaire(P_relance) @ valeur - pi @ valeur
print("nouveau revenu :", round(loi_stationnaire(P_relance) @ valeur, 2), "€ ; gain :", round(gain, 2), "€ par client et par mois")
print("avec 2 000 clients :", round(gain * 2000), "€ par mois")
```
<!--sortie-->
```text
nouveau revenu : 19.3 € ; gain : 1.8 € par client et par mois
avec 2 000 clients : 3596 € par mois
```

**Étape 3 : jusqu'où la relance vaut-elle la peine ?** On fait varier la probabilité Inactif→Actif de 0,10 à 0,40 (en retirant ce qu'on ajoute à « rester inactif »).

```python
for q in (0.10, 0.20, 0.30, 0.40):
    Pq = P.copy(); Pq[2] = [q, 0.20, 0.80 - q]
    print(f"Inactif→Actif = {q:.2f} : revenu mensuel moyen = {loi_stationnaire(Pq) @ valeur:.2f} €")
```
<!--sortie-->
```text
Inactif→Actif = 0.10 : revenu mensuel moyen = 17.50 €
Inactif→Actif = 0.20 : revenu mensuel moyen = 19.30 €
Inactif→Actif = 0.30 : revenu mensuel moyen = 20.43 €
Inactif→Actif = 0.40 : revenu mensuel moyen = 21.20 €
```

Les gains successifs diminuent : passer de 0,10 à 0,20 rapporte 1,80 € par client et par mois, de 0,20 à 0,30 seulement 1,13 €, de 0,30 à 0,40 0,77 €.

**Questions.** (1) Que représente chaque valeur propre de $\mathbf{P}$ en dehors de 1 ? (2) Si la campagne coûte 1,50 € par client et par mois, est-elle rentable pour $q=0{,}20$ ? Pour $q=0{,}15$ ? (3) Le modèle suppose que les probabilités de transition sont constantes. Citez deux raisons pour lesquelles c'est discutable.

### Application 2.5 — Diversification et matrice de covariance

**Contexte.** Deux produits ont des ventes quotidiennes de moyenne 50 et d'écart-type 10. Plus leurs ventes sont corrélées négativement, plus le total est stable. On vérifie la formule $\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)$ sur une famille de corrélations, puis on lit une matrice de covariance sur des données simulées.

**Partie A — La variabilité du total selon la corrélation.**

```python
import numpy as np
rng = np.random.default_rng(8)
print("   rho   écart-type théorique   écart-type simulé")
for rho in (-0.8, -0.5, 0.0, 0.5, 0.8):
    cov = [[100, rho * 100], [rho * 100, 100]]
    total = rng.multivariate_normal([50, 50], cov, size=100_000).sum(axis=1)
    print(f"{rho:+5.1f}   {np.sqrt(200 + 200 * rho):18.2f}   {total.std():17.2f}")
```
<!--sortie-->
```text
   rho   écart-type théorique   écart-type simulé
 -0.8                 6.32                6.34
 -0.5                10.00                9.97
 +0.0                14.14               14.14
 +0.5                17.32               17.30
 +0.8                18.97               18.97
```

**Partie B — Une matrice de covariance, trois variables.** Sur 365 jours, la température influence les visites, qui influencent les ventes.

```python
rng = np.random.default_rng(2)
n = 365
temperature = rng.normal(25, 6, n)
visites = 80 + 3 * temperature + rng.normal(0, 15, n)
ventes = 0.2 * visites + rng.normal(0, 3, n)
donnees = np.column_stack([temperature, visites, ventes])
print("covariances :\n", np.cov(donnees.T).round(1))
print("corrélations :\n", np.corrcoef(donnees.T).round(2))
```
<!--sortie-->
```text
covariances :
 [[ 36.7 106.2  22.6]
 [106.2 529.4 107.1]
 [ 22.6 107.1  31.1]]
corrélations :
 [[1.   0.76 0.67]
 [0.76 1.   0.84]
 [0.67 0.84 1.  ]]
```

Le total est d'autant plus stable que la corrélation est négative : l'écart-type passe de 18,97 pour $\rho=+0{,}8$ à 6,32 pour $\rho=-0{,}8$, et la simulation retombe sur la théorie à 0,03 près.

**Questions.** (1) Pour quelle valeur de $\rho$ la variabilité du total est-elle minimale, et quelle est-elle ? (2) Dans la partie B, expliquez pourquoi la corrélation température–ventes (0,67) est plus faible que les deux autres. (3) Calculez à la main $\operatorname{Var}(\text{visites}+\text{ventes})$ à partir de la matrice de covariance, puis vérifiez avec `np.var(donnees[:,1]+donnees[:,2], ddof=1)`.

### Application 2.6 — Les dépenses « à zéros » : une loi mixte

**Contexte.** Un visiteur dépense 0 € avec une probabilité de 70 % ; sinon sa dépense suit une loi exponentielle de moyenne 80 €. On calcule les résumés de cette loi mixte à la main, puis on les vérifie par simulation et on voit pourquoi un seul chiffre ne suffit pas.

**À la main.** $E[X]=0{,}3\times80=24$. Pour la variance : $E[X^2]=0{,}3\times E[Y^2]$ avec $Y\sim\text{Exp}$ de moyenne 80, donc $E[Y^2]=2\times80^2=12\,800$ et $E[X^2]=3\,840$ ; ainsi $\operatorname{Var}(X)=3\,840-24^2=3\,264$ et $\sigma\approx57{,}1$.

```python
import numpy as np
rng = np.random.default_rng(31)
n = 500_000
achete = rng.random(n) < 0.3
depense = np.where(achete, rng.exponential(80, size=n), 0.0)
print("part de zéros     :", round((depense == 0).mean(), 4))
print("moyenne, écart-type :", depense.mean().round(2), depense.std().round(2), "(théorie : 24 et 57,1)")
print("médiane           :", np.median(depense).round(2))
print("moyenne chez les acheteurs :", depense[achete].mean().round(2))
```
<!--sortie-->
```text
part de zéros     : 0.6998
moyenne, écart-type : 24.03 57.09 (théorie : 24 et 57,1)
médiane           : 0.0
moyenne chez les acheteurs : 80.04
```

La simulation donne 70,0 % de zéros, une moyenne de 24,03 et un écart-type de 57,09 (théorie : 24 et 57,1) ; la médiane est nulle, et la dépense moyenne des seuls acheteurs vaut 80,04.

**Questions.** (1) Quelle est la médiane de $X$ en théorie ? Pourquoi la moyenne et la médiane racontent-elles des histoires opposées ? (2) Comment présenteriez-vous ces dépenses à la gérante en deux chiffres plutôt qu'un ? (3) Quelle est la part du chiffre d'affaires total réalisée par les 10 % de clients qui dépensent le plus ? Estimez-la avec `np.sort` et `cumsum`.

## Exercices

### Exercice 2.1 ⭐ — Union (section 2.1)
Pour une newsletter : $P(\text{ouvre})=0{,}35$, $P(\text{clique})=0{,}25$, $P(\text{ouvre et clique})=0{,}10$. Quelle est la probabilité qu'un destinataire fasse **au moins une** des deux actions ? Qu'il ne fasse **aucune** ?

### Exercice 2.2 ⭐⭐ — Bayes (section 2.1)
Chez un fournisseur, 2 % des articles sont défectueux. Un contrôle automatique signale 90 % des articles défectueux, mais aussi 4 % des articles corrects. Un article est signalé : quelle est la probabilité qu'il soit réellement défectueux ? Interprétez.

### Exercice 2.3 ⭐ — « Au moins un » (section 2.1)
Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. (a) Probabilité qu'au moins un colis soit endommagé parmi 50 ? (b) Combien de colis faut-il pour que cette probabilité dépasse 90 % ?

### Exercice 2.4 ⭐ — Binomiale (section 2.2)
Sur 15 visiteurs d'une publicité, chacun achète avec la probabilité 0,3. Calculez $P(X=5)$, l'espérance et l'écart-type de $X$, et $P(X\ge8)$.

### Exercice 2.5 ⭐⭐ — Poisson et exponentielle (section 2.2)
Le service client reçoit en moyenne 4 appels par heure (processus de Poisson). (a) Probabilité de ne recevoir **aucun** appel pendant une demi-heure ? (b) Le temps d'attente entre deux appels est exponentiel : quelle est sa moyenne, et quelle est la probabilité d'attendre plus de 20 minutes ? (c) On a déjà attendu 10 minutes sans appel : quelle est la probabilité d'attendre **encore** 20 minutes ?

### Exercice 2.6 ⭐⭐ — Normale (section 2.2)
Le poids des colis expédiés suit $\mathcal N(500\text{ g},\ 40^2)$. (a) Probabilité qu'un colis pèse moins de 450 g ? (b) Entre 460 et 540 g ? (c) Quel poids n'est dépassé que par 1 % des colis ?

### Exercice 2.7 ⭐⭐ — Espérance et variance (section 2.3)
Un jeu de fidélité distribue : 0 € avec la probabilité 0,80 ; 10 € avec 0,15 ; 50 € avec 0,05. Calculez l'espérance, la variance et l'écart-type du gain. Si participer coûte 5 €, le jeu est-il favorable au client ? Et si le client joue 100 fois, quelle est l'espérance et l'écart-type de son gain total ?

### Exercice 2.8 ⭐⭐ — Covariance (section 2.3)
Cinq clients ont noté le délai de livraison ($x=1,2,3,4,5$ jours) et leur satisfaction ($y=2,4,5,4,5$ sur 5). Calculez à la main la covariance (divisée par $n$), la variance de chaque variable et la corrélation. Vérifiez avec NumPy.

### Exercice 2.9 ⭐⭐⭐ — Théorème central limite (section 2.4)
Le panier d'un client a une moyenne de 45 € et un écart-type de 30 € (loi très asymétrique). On observe 100 clients. (a) Quelle est la loi approchée de la moyenne ? (b) Probabilité que la moyenne dépasse 50 € ? (c) Combien de clients faut-il observer pour que l'erreur-type de la moyenne soit inférieure à 1 € ? (d) Vérifiez (b) par simulation. Attention : une loi exponentielle de moyenne 45 a un écart-type de 45, pas 30 ; quelle loi asymétrique de moyenne 45 et d'écart-type 30 peut-on utiliser à la place ?

### Exercice 2.10 ⭐⭐⭐ — Chaîne de Markov (section 2.6)
Chaque jour, une machine est **en marche** (M) ou **en panne** (P). Si elle est en marche, elle tombe en panne le lendemain avec probabilité 0,1. Si elle est en panne, elle est réparée le lendemain avec probabilité 0,4. (a) Écrivez la matrice de transition. (b) Si elle est en marche aujourd'hui, quelle est la probabilité qu'elle le soit après-demain ? (c) Quelle est la proportion de temps passée en panne à long terme ?

## Corrigés

### Corrigé 2.1
$P(\text{au moins une})=0{,}35+0{,}25-0{,}10=0{,}50$. Aucune : $1-0{,}50=0{,}50$. (On retranche l'intersection pour ne pas la compter deux fois ; le complémentaire de « au moins une » est « aucune ».)

### Corrigé 2.2
Sur 10 000 articles : 200 défectueux, dont 180 signalés ; 9 800 corrects, dont 392 signalés à tort. Total des signalements : 572, dont 180 justifiés : $180/572\approx0{,}315$.

```python
p_def, sens, fausse = 0.02, 0.90, 0.04
p_signal = sens * p_def + fausse * (1 - p_def)
print("P(défectueux | signalé) =", round(sens * p_def / p_signal, 4))
```
<!--sortie-->
```text
P(défectueux | signalé) = 0.3147
```

Seulement **31,5 %** : même avec un bon contrôle, **deux articles signalés sur trois sont corrects**, car les défauts sont rares (erreur du taux de base). Ils justifient une seconde vérification plutôt qu'un rejet automatique.

### Corrigé 2.3
(a) $1-0{,}98^{50}\approx0{,}636$. (b) On veut $1-0{,}98^n>0{,}9\iff0{,}98^n<0{,}1\iff n>\dfrac{\ln0{,}1}{\ln0{,}98}\approx113{,}97$, donc **114 colis**.

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

### Corrigé 2.4
$P(X=5)=\binom{15}5\,0{,}3^5\,0{,}7^{10}$. $E[X]=np=4{,}5$ ; $\sigma=\sqrt{np(1-p)}=\sqrt{3{,}15}\approx1{,}775$ ; $P(X\ge8)=1-P(X\le7)$.

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

### Corrigé 2.5
(a) Sur une demi-heure, $N\sim\text{Poisson}(4\times0{,}5=2)$ : $P(N=0)=e^{-2}\approx0{,}135$. (b) Le temps d'attente est $\text{Exp}(4/\text{h})$, de moyenne $1/4$ h $=15$ min. 20 min $=1/3$ h : $P(T>1/3)=e^{-4/3}\approx0{,}264$. (c) Par absence de mémoire, c'est la même probabilité : **0,264**.

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

### Corrigé 2.6
(a) $z=(450-500)/40=-1{,}25$, $P=\Phi(-1{,}25)\approx0{,}106$. (b) $z$ de $-1$ à $+1$ : $\approx0{,}683$. (c) $z_{0{,}99}\approx2{,}326$, donc $500+2{,}326\times40\approx593$ g.

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

### Corrigé 2.7
$E=0{,}15\times10+0{,}05\times50=1{,}5+2{,}5=4$ €. $E[X^2]=0{,}15\times100+0{,}05\times2500=15+125=140$, $\operatorname{Var}=140-16=124$, $\sigma\approx11{,}1$ €. À 5 € la partie, l'espérance du **gain net** est $4-5=-1$ € : défavorable en moyenne (c'est favorable à la boutique). Sur 100 parties (indépendantes) : espérance $100\times4=400$ €, variance $100\times124=12\,400$, écart-type $\sqrt{12400}\approx111$ €. Remarquez que l'écart-type relatif diminue : 111/400 = 28 % contre 11,1/4 = 278 % pour une seule partie.

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

### Corrigé 2.8
Moyennes $\bar x=3$, $\bar y=4$. Écarts : $x-\bar x=(-2,-1,0,1,2)$, $y-\bar y=(-2,0,1,0,1)$. Produits : $4,0,0,0,2$, de somme 6, donc $\operatorname{Cov}=6/5=1{,}2$. $\operatorname{Var}(x)=(4+1+0+1+4)/5=2$ ; $\operatorname{Var}(y)=(4+0+1+0+1)/5=1{,}2$. $\rho=\dfrac{1{,}2}{\sqrt{2\times1{,}2}}=\dfrac{1{,}2}{1{,}549}\approx0{,}775$. Lecture : la corrélation est *positive* : plus la livraison est lente, plus la satisfaction serait élevée ? Ce n'est pas plausible : avec seulement cinq points, c'est probablement un hasard de l'échantillon. Nous verrons au chapitre 3 comment tester si une corrélation observée est significative.

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

### Corrigé 2.9
(a) Par le TCL, $\bar X_{100}\approx\mathcal N(45,\ 30^2/100)=\mathcal N(45,\ 3^2)$ : erreur-type 3 €. (b) $z=(50-45)/3\approx1{,}667$, $P(\bar X>50)\approx0{,}048$. (c) $\sigma/\sqrt n<1\iff n>900$. (d) Pour la simulation, une exponentielle de moyenne 45 a un écart-type de **45** (pas 30) : elle ne convient pas. On utilise une loi Gamma de moyenne 45 et d'écart-type 30 (forme $k=(45/30)^2=2{,}25$, échelle $\theta=30^2/45=20$). La simulation donne 5,1 % contre 4,8 % par le TCL : l'écart vient de l'asymétrie résiduelle à $n=100$.

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

### Corrigé 2.10
(a) $\mathbf{P}=\begin{pmatrix}0{,}9&0{,}1\\0{,}4&0{,}6\end{pmatrix}$ (lignes M, P). (b) $\mathbf{P}^2_{MM}=0{,}9\times0{,}9+0{,}1\times0{,}4=0{,}85$. (c) On cherche $\boldsymbol\pi=(\pi_M,\pi_P)$ avec $\boldsymbol\pi\mathbf P=\boldsymbol\pi$ : de la seconde colonne, $0{,}1\pi_M+0{,}6\pi_P=\pi_P$, soit $0{,}1\pi_M=0{,}4\pi_P$, donc $\pi_M=4\pi_P$ ; avec $\pi_M+\pi_P=1$ : $\pi_P=0{,}2$. La machine est en panne **20 % du temps** à long terme.

```python
P = np.array([[0.9, 0.1], [0.4, 0.6]])
print("P^2[M,M] =", np.linalg.matrix_power(P, 2)[0, 0].round(4))
w, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
print("loi stationnaire :", pi.round(3))
```
<!--sortie-->
```text
P^2[M,M] = 0.85
loi stationnaire : [0.8 0.2]
```
