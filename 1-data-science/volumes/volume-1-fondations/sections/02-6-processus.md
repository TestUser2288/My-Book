## 2.6 ➕ Pour aller plus loin : les processus stochastiques

> 🧭 **Section optionnelle.** Jusqu'ici, une variable aléatoire était un nombre tiré **une fois**. Un **processus stochastique** est une variable aléatoire qui **évolue dans le temps** : $X_0,X_1,X_2,\dots$ Les stocks, les clients actifs, le cours d'une action, le nombre d'appels : tout cela est une suite de variables aléatoires dépendantes les unes des autres.

### 2.6.1 La marche aléatoire

> 💡 **Intuition.** Chaque jour, le stock d'un produit varie de +1 ou −1 de façon aléatoire. Où sera-t-il après 100 jours ?

On part de $S_0=0$ et on pose $S_n=S_{n-1}+\xi_n$ où chaque pas $\xi_n$ vaut $+1$ ou $-1$ avec probabilité $\tfrac12$. Comme $E[\xi_n]=0$ et $\operatorname{Var}(\xi_n)=1$, les propriétés du 2.3 (somme de variables indépendantes) donnent

$$E[S_n]=0,\qquad\operatorname{Var}(S_n)=n,\qquad\sigma(S_n)=\sqrt n.$$

Une marche aléatoire n'a donc **pas de tendance**, mais elle s'écarte de 0 de l'ordre de $\sqrt n$. Après 100 pas, on s'attend à être à environ 10 de l'origine, pas à 100 ! C'est la même loi en $\sqrt n$ que celle de l'erreur-type.

Une simulation de 20 000 marches de 100 pas confirme la théorie : la moyenne des positions finales est proche de 0 (0,08) et leur écart-type vaut 10,08, pour $\sqrt{100}=10$ en théorie.

Par le TCL, $S_n/\sqrt n\approx\mathcal N(0,1)$ : environ 68 % des marches finissent à moins de $\sqrt n$ de l'origine (ici, 72 % : un peu plus que 68 %, car la borne $\pm10$ est incluse et la marche ne prend que des valeurs paires).

> 🧪 **La marche aléatoire est partout.** Le cours d'une action est souvent modélisé comme une marche aléatoire (le **mouvement brownien**, limite continue de la marche quand les pas deviennent infiniment petits). Elle explique aussi pourquoi les prévisions à long terme sont si incertaines : l'incertitude grandit en $\sqrt{\text{temps}}$.

### 2.6.2 Les chaînes de Markov : le futur ne dépend que du présent

> 💡 **Intuition.** Dans une **chaîne de Markov**, la probabilité de passer à l'état suivant ne dépend que de l'**état actuel**, pas de la manière dont on y est arrivé :
>
> $$P(X_{n+1}=j\mid X_n=i,\ X_{n-1},\dots,X_0)=P(X_{n+1}=j\mid X_n=i)=P_{ij}.$$

La gérante classe chaque mois ses clients en trois états : **Actif** (A : au moins 2 achats ce mois), **Occasionnel** (O : 1 achat) et **Inactif** (I : aucun achat). Elle a estimé les transitions d'un mois au suivant :

| de ↓ / vers → | Actif | Occasionnel | Inactif |
|---|---:|---:|---:|
| **Actif** | 0,80 | 0,15 | 0,05 |
| **Occasionnel** | 0,30 | 0,50 | 0,20 |
| **Inactif** | 0,10 | 0,20 | 0,70 |

On range ces nombres dans la **matrice de transition** $\mathbf{P}$ : chaque **ligne** est une loi de probabilité (somme égale à 1).

**Où sera un client dans 2 mois ?** Un client Actif aujourd'hui peut être Actif dans 2 mois de plusieurs façons : A→A→A, A→O→A, A→I→A. La probabilité totale est $0{,}8\times0{,}8+0{,}15\times0{,}3+0{,}05\times0{,}1=0{,}64+0{,}045+0{,}005=0{,}69$. Mais c'est **exactement** le produit matriciel de la ligne A par la colonne A de $\mathbf{P}$ ! En général :

> 📐 **Les probabilités de transition en $n$ pas sont les éléments de $\mathbf{P}^n$.** (Même mécanisme que pour compter les chemins d'un graphe au 1.6.3 : la formule des probabilités totales fait apparaître le produit matriciel.)

Avec NumPy, la puissance d'une matrice est un appel de fonction :

```python
import numpy as np
P = np.array([[0.80, 0.15, 0.05],       # lignes : état de départ (Actif, Occasionnel, Inactif)
              [0.30, 0.50, 0.20],       # colonnes : état d'arrivée
              [0.10, 0.20, 0.70]])
print(np.linalg.matrix_power(P, 2).round(3))
```
<!--sortie-->
```text
[[0.69  0.205 0.105]
 [0.41  0.335 0.255]
 [0.21  0.255 0.535]]
```

On retrouve $0{,}69$ en haut à gauche : la probabilité d'être Actif dans 2 mois quand on l'est aujourd'hui.

**Et dans 12 mois, ou 2 ans ?** On calcule des puissances plus élevées :

Voici la ligne « Actif » de $\mathbf{P}^n$, c'est-à-dire la loi de l'état d'un client **Actif aujourd'hui**, après $n$ mois, puis celle d'un client **Inactif** aujourd'hui :

| $n$ (mois) | 1 | 3 | 6 | 12 | 24 |
|---|---|---|---|---|---|
| Départ **Actif** : (A, O, I) | (0,800 ; 0,150 ; 0,050) | (0,624 ; 0,227 ; 0,149) | (0,537 ; 0,245 ; 0,218) | (0,503 ; 0,250 ; 0,247) | (0,500 ; 0,250 ; 0,250) |
| Départ **Inactif** : (A, O, I) | (0,100 ; 0,200 ; 0,700) | (0,298 ; 0,266 ; 0,436) | (0,437 ; 0,258 ; 0,305) | (0,494 ; 0,251 ; 0,255) | (0,500 ; 0,250 ; 0,250) |

Observez : à mesure que $n$ grandit, **toutes les lignes deviennent identiques**. Le système « oublie » son point de départ : qu'un client ait commencé Actif ou Inactif, sa probabilité d'être dans chaque état dans 2 ans est la même. Cette loi limite $\boldsymbol\pi$ s'appelle la **distribution stationnaire**.

**La calculer exactement : valeurs propres, encore !** La loi stationnaire vérifie $\boldsymbol\pi\mathbf{P}=\boldsymbol\pi$ : elle ne change plus après une transition. En transposant, $\mathbf{P}^\top\boldsymbol\pi^\top=\boldsymbol\pi^\top$ : c'est un **vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1** (section 1.1.3).

On peut **vérifier à la main** que $\boldsymbol\pi=(0{,}5\ ;\ 0{,}25\ ;\ 0{,}25)$ convient. Colonne Actif : $0{,}5\times0{,}8+0{,}25\times0{,}3+0{,}25\times0{,}1=0{,}4+0{,}075+0{,}025=0{,}5$ ✓. Colonne Occasionnel : $0{,}5\times0{,}15+0{,}25\times0{,}5+0{,}25\times0{,}2=0{,}075+0{,}125+0{,}05=0{,}25$ ✓. Colonne Inactif : $0{,}5\times0{,}05+0{,}25\times0{,}2+0{,}25\times0{,}7=0{,}025+0{,}05+0{,}175=0{,}25$ ✓. Pour la **trouver** quand on ne la connaît pas, on résout ce système linéaire (avec $\pi_A+\pi_O+\pi_I=1$), ou on demande à l'ordinateur le vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1.

À long terme, exactement **50 %** des clients sont Actifs, **25 %** Occasionnels et **25 %** Inactifs. Les deux autres valeurs propres de $\mathbf{P}$ (0,673 et 0,327, de module < 1) pilotent la **vitesse** de convergence : plus elles sont petites, plus vite le système oublie son passé.

**Une application économique : la valeur à long terme d'un client.** Supposons qu'un client Actif rapporte en moyenne 30 € par mois, un Occasionnel 10 €, un Inactif 0 €. À long terme, le revenu moyen mensuel par client est $\boldsymbol\pi\cdot\mathbf{v}$ :

Soit **17,5 € par client et par mois** : $\boldsymbol\pi\cdot\mathbf v=0{,}5\times30+0{,}25\times10+0{,}25\times0=15+2{,}5=17{,}5$. Cette quantité permet de **chiffrer** l'effet d'une campagne : si une relance fait passer la probabilité Inactif→Actif de 0,10 à 0,20, il suffit de modifier $\mathbf{P}$ et de recalculer $\boldsymbol\pi$. C'est un modèle simple, mais l'idée (états, transitions, régime permanent) est utilisée en analyse de la fidélité, en marketing, et à la base de l'algorithme PageRank (le web est une chaîne de Markov dont les états sont les pages).

> 📒 **Pour s'entraîner.** L'application 2.4 du cahier mesure l'effet de cette relance sur le revenu à long terme.

### 2.6.3 Le processus de Poisson : des arrivées au hasard

Un **processus de Poisson** de cadence $\lambda$ modélise des événements arrivant au hasard et indépendamment : appels, commandes, pannes. Il a deux visages **équivalents**, que nous avons déjà croisés :

- le **nombre** d'événements dans une durée $t$ suit une loi de **Poisson**$(\lambda t)$ (2.2.4) ;
- les **temps d'attente** entre événements successifs sont **exponentiels**$(\lambda)$, indépendants (2.2.5).

Vérifions que ces deux visages coïncident : on construit le processus **uniquement** par ses temps d'attente exponentiels (de cadence 3 par heure), puis on compte les arrivées dans chaque heure. Sur 50 000 heures simulées, la moyenne des comptes vaut 3,005 et leur variance 2,98 (théorie : 3 et 3, comme il se doit pour une loi de Poisson). Les fréquences observées collent à la loi de Poisson(3) :

| Nombre de commandes $k$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fréquence simulée | 0,0492 | 0,1491 | 0,2228 | 0,2241 | 0,1687 | 0,1023 | 0,0511 |
| Poisson(3) | 0,0498 | 0,1494 | 0,2240 | 0,2240 | 0,1680 | 0,1008 | 0,0504 |

Les deux descriptions sont bien le même objet. C'est pourquoi les files d'attente (guichets, serveurs, centres d'appels) se modélisent presque toujours avec ce processus.

> ✅ **À retenir (processus stochastiques).**
>
> - Un processus stochastique est une famille $(X_t)$ de variables aléatoires indexée par le temps.
> - **Marche aléatoire** : $E[S_n]=0$, $\sigma(S_n)=\sqrt n$ ; l'incertitude croît en $\sqrt{\text{temps}}$.
> - **Chaîne de Markov** : le futur ne dépend que du présent ; probabilités en $n$ pas $=\mathbf{P}^n$ ; **loi stationnaire** = vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1.
> - **Processus de Poisson** : nombres de Poisson ⇔ temps d'attente exponentiels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 (processus de Poisson simulé) et 2.4 (chaîne de Markov), exercice 2.10.

```python hide
# Vérifie tous les nombres cités dans la section 2.6.
import numpy as np
from scipy import stats
rng = np.random.default_rng(14)
fin = rng.choice([-1, 1], size=(20_000, 100)).sum(axis=1)
print("marche : moyenne", round(fin.mean(), 3), "| écart-type", round(fin.std(), 3), "| P(|S|<=10) =", round((np.abs(fin) <= 10).mean(), 3))
P = np.array([[0.80, 0.15, 0.05], [0.30, 0.50, 0.20], [0.10, 0.20, 0.70]])
print("lignes :", P.sum(axis=1), "| P^2 =", np.linalg.matrix_power(P, 2).round(3).tolist())
for n in (1, 3, 6, 12, 24):
    Pn = np.linalg.matrix_power(P, n)
    print(f"n={n:>2} Actif {Pn[0].round(4)} | Inactif {Pn[2].round(4)}")
w, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
print("pi =", pi.round(4), "| valeurs propres de P :", np.round(np.sort(np.real(w))[::-1], 3), "| revenu =", round(pi @ np.array([30, 10, 0]), 2))
print("pi P = pi ?", np.allclose(pi @ P, pi))
rng = np.random.default_rng(15)
lam, n_h = 3, 50_000
comptes = np.empty(n_h, dtype=int)
for h in range(n_h):
    t, k = 0.0, 0
    while True:
        t += rng.exponential(1 / lam)
        if t > 1.0:
            break
        k += 1
    comptes[h] = k
print("Poisson simulé : moyenne", round(comptes.mean(), 3), "| variance", round(comptes.var(), 3))
print([round((comptes == k).mean(), 4) for k in range(7)], [round(stats.poisson(3).pmf(k), 4) for k in range(7)])
```
<!--sortie-->
```text
marche : moyenne 0.082 | écart-type 10.076 | P(|S|<=10) = 0.723
lignes : [1. 1. 1.] | P^2 = [[0.69, 0.205, 0.105], [0.41, 0.335, 0.255], [0.21, 0.255, 0.535]]
n= 1 Actif [0.8  0.15 0.05] | Inactif [0.1 0.2 0.7]
n= 3 Actif [0.624 0.227 0.149] | Inactif [0.298 0.266 0.436]
n= 6 Actif [0.5368 0.2448 0.2183] | Inactif [0.4366 0.2581 0.3053]
n=12 Actif [0.5034 0.2495 0.247 ] | Inactif [0.4941 0.2508 0.2551]
n=24 Actif [0.5  0.25 0.25] | Inactif [0.4999 0.25   0.25  ]
pi = [0.5  0.25 0.25] | valeurs propres de P : [1.    0.673 0.327] | revenu = 17.5
pi P = pi ? True
Poisson simulé : moyenne 3.005 | variance 2.98
[np.float64(0.0492), np.float64(0.1491), np.float64(0.2228), np.float64(0.2241), np.float64(0.1687), np.float64(0.1023), np.float64(0.0511)] [np.float64(0.0498), np.float64(0.1494), np.float64(0.224), np.float64(0.224), np.float64(0.168), np.float64(0.1008), np.float64(0.0504)]
```
