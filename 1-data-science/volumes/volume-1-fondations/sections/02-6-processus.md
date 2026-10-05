## 2.6 ➕ Pour aller plus loin : les processus stochastiques

> 🧭 **Section optionnelle.** Jusqu'ici, une variable aléatoire était un nombre tiré **une fois**. Un **processus stochastique** est une variable aléatoire qui **évolue dans le temps** : $X_0,X_1,X_2,\dots$ Les stocks, les clients actifs, le cours d'une action, le nombre d'appels : tout cela est une suite de variables aléatoires dépendantes les unes des autres.

### 2.6.1 La marche aléatoire

> 💡 **Intuition.** Chaque jour, le stock d'un produit varie de +1 ou −1 de façon aléatoire. Où sera-t-il après 100 jours ?

On part de $S_0=0$ et on pose $S_n=S_{n-1}+\xi_n$ où chaque pas $\xi_n$ vaut $+1$ ou $-1$ avec probabilité $\tfrac12$. Comme $E[\xi_n]=0$ et $\operatorname{Var}(\xi_n)=1$, les propriétés du 2.3 (somme de variables indépendantes) donnent

$$E[S_n]=0,\qquad\operatorname{Var}(S_n)=n,\qquad\sigma(S_n)=\sqrt n.$$

Une marche aléatoire n'a donc **pas de tendance**, mais elle s'écarte de 0 de l'ordre de $\sqrt n$. Après 100 pas, on s'attend à être à environ 10 de l'origine, pas à 100 ! C'est la même loi en $\sqrt n$ que celle de l'erreur-type.

```python
import numpy as np
rng = np.random.default_rng(14)

pas = rng.choice([-1, 1], size=(20_000, 100))           # 20 000 marches de 100 pas
position_finale = pas.sum(axis=1)
print("moyenne des positions finales :", round(position_finale.mean(), 3))
print("écart-type des positions      :", round(position_finale.std(), 3), "(théorie : √100 = 10)")
print("P(|S_100| <= 10)              :", round((np.abs(position_finale) <= 10).mean(), 3))
```
<!--sortie-->
```text
moyenne des positions finales : 0.082
écart-type des positions      : 10.076 (théorie : √100 = 10)
P(|S_100| <= 10)              : 0.723
```

Par le TCL, $S_n/\sqrt n\approx\mathcal N(0,1)$ : environ 68 % des marches finissent à moins de $\sqrt n$ de l'origine (ici, 72 % : un peu plus que 68 %, car la borne $\pm10$ est incluse et la marche ne prend que des valeurs paires).

> 🧪 **La marche aléatoire est partout.** Le cours d'une action est souvent modélisé comme une marche aléatoire (le **mouvement brownien**, limite continue de la marche quand les pas deviennent infiniment petits). Elle explique aussi pourquoi les prévisions à long terme sont si incertaines : l'incertitude grandit en $\sqrt{\text{temps}}$.

### 2.6.2 Les chaînes de Markov : le futur ne dépend que du présent

> 💡 **Intuition.** Dans une **chaîne de Markov**, la probabilité de passer à l'état suivant ne dépend que de l'**état actuel**, pas de la manière dont on y est arrivé :
>
> $$P(X_{n+1}=j\mid X_n=i,\ X_{n-1},\dots,X_0)=P(X_{n+1}=j\mid X_n=i)=P_{ij}.$$

Yasmine classe chaque mois ses clients en trois états : **Actif** (A : au moins 2 achats ce mois), **Occasionnel** (O : 1 achat) et **Inactif** (I : aucun achat). Elle a estimé les transitions d'un mois au suivant :

| de ↓ / vers → | Actif | Occasionnel | Inactif |
|---|---:|---:|---:|
| **Actif** | 0,80 | 0,15 | 0,05 |
| **Occasionnel** | 0,30 | 0,50 | 0,20 |
| **Inactif** | 0,10 | 0,20 | 0,70 |

On range ces nombres dans la **matrice de transition** $\mathbf{P}$ : chaque **ligne** est une loi de probabilité (somme égale à 1).

```python
P = np.array([[0.80, 0.15, 0.05],
              [0.30, 0.50, 0.20],
              [0.10, 0.20, 0.70]])
etats = ["Actif", "Occasionnel", "Inactif"]
print("somme des lignes :", P.sum(axis=1))
```
<!--sortie-->
```text
somme des lignes : [1. 1. 1.]
```

**Où sera un client dans 2 mois ?** Un client Actif aujourd'hui peut être Actif dans 2 mois de plusieurs façons : A→A→A, A→O→A, A→I→A. La probabilité totale est $0{,}8\times0{,}8+0{,}15\times0{,}3+0{,}05\times0{,}1=0{,}64+0{,}045+0{,}005=0{,}69$. Mais c'est **exactement** le produit matriciel de la ligne A par la colonne A de $\mathbf{P}$ ! En général :

> 📐 **Les probabilités de transition en $n$ pas sont les éléments de $\mathbf{P}^n$.** (Même mécanisme que pour compter les chemins d'un graphe au 1.6.3 : la formule des probabilités totales fait apparaître le produit matriciel.)

```python
P2 = np.linalg.matrix_power(P, 2)
print("P^2 :\n", P2.round(3))
print("P(Actif -> Actif en 2 mois) =", P2[0, 0].round(3))
```
<!--sortie-->
```text
P^2 :
 [[0.69  0.205 0.105]
 [0.41  0.335 0.255]
 [0.21  0.255 0.535]]
P(Actif -> Actif en 2 mois) = 0.69
```

**Et dans 12 mois, ou 2 ans ?** On calcule des puissances plus élevées :

```python
for n in (1, 3, 6, 12, 24):
    Pn = np.linalg.matrix_power(P, n)
    print(f"n = {n:>2} mois : ligne 'Actif' = {Pn[0].round(4)}   ligne 'Inactif' = {Pn[2].round(4)}")
```
<!--sortie-->
```text
n =  1 mois : ligne 'Actif' = [0.8  0.15 0.05]   ligne 'Inactif' = [0.1 0.2 0.7]
n =  3 mois : ligne 'Actif' = [0.624 0.227 0.149]   ligne 'Inactif' = [0.298 0.266 0.436]
n =  6 mois : ligne 'Actif' = [0.5368 0.2448 0.2183]   ligne 'Inactif' = [0.4366 0.2581 0.3053]
n = 12 mois : ligne 'Actif' = [0.5034 0.2495 0.247 ]   ligne 'Inactif' = [0.4941 0.2508 0.2551]
n = 24 mois : ligne 'Actif' = [0.5  0.25 0.25]   ligne 'Inactif' = [0.4999 0.25   0.25  ]
```

Observez : à mesure que $n$ grandit, **toutes les lignes deviennent identiques**. Le système « oublie » son point de départ : qu'un client ait commencé Actif ou Inactif, sa probabilité d'être dans chaque état dans 2 ans est la même. Cette loi limite $\boldsymbol\pi$ s'appelle la **distribution stationnaire**.

**La calculer exactement : valeurs propres, encore !** La loi stationnaire vérifie $\boldsymbol\pi\mathbf{P}=\boldsymbol\pi$ : elle ne change plus après une transition. En transposant, $\mathbf{P}^\top\boldsymbol\pi^\top=\boldsymbol\pi^\top$ : c'est un **vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1** (section 1.1.3).

```python
valeurs, vecteurs = np.linalg.eig(P.T)
k = np.argmin(np.abs(valeurs - 1))                 # la valeur propre égale à 1
pi = np.real(vecteurs[:, k])
pi = pi / pi.sum()                                 # normaliser pour que la somme soit 1
for e, v in zip(etats, pi):
    print(f"{e:<12} {v:.4f}")
print("valeurs propres de P :", np.round(np.real(valeurs), 3))
```
<!--sortie-->
```text
Actif        0.5000
Occasionnel  0.2500
Inactif      0.2500
valeurs propres de P : [1.    0.673 0.327]
```

À long terme, exactement **50 %** des clients sont Actifs, **25 %** Occasionnels et **25 %** Inactifs. Les deux autres valeurs propres (0,673 et 0,327, de module < 1) pilotent la **vitesse** de convergence : plus elles sont petites, plus vite le système oublie son passé.

**Une application économique : la valeur à long terme d'un client.** Supposons qu'un client Actif rapporte en moyenne 30 DT par mois, un Occasionnel 10 DT, un Inactif 0 DT. À long terme, le revenu moyen mensuel par client est $\boldsymbol\pi\cdot\mathbf{v}$ :

```python
v = np.array([30, 10, 0])
print("revenu mensuel moyen par client (long terme) :", round(pi @ v, 2), "DT")
```
<!--sortie-->
```text
revenu mensuel moyen par client (long terme) : 17.5 DT
```

Soit 17,5 DT par client et par mois. Cette quantité permet à Yasmine de **chiffrer** l'effet d'une campagne : si une relance fait passer la probabilité Inactif→Actif de 0,10 à 0,20, quel est le gain ? Il suffit de modifier $\mathbf{P}$ et de recalculer $\boldsymbol\pi$.

```python
def revenu_long_terme(P, v):
    valeurs, vecteurs = np.linalg.eig(P.T)
    pi = np.real(vecteurs[:, np.argmin(np.abs(valeurs - 1))])
    pi = pi / pi.sum()
    return pi @ v

P_relance = np.array([[0.80, 0.15, 0.05],
                      [0.30, 0.50, 0.20],
                      [0.20, 0.20, 0.60]])           # Inactif -> Actif passe de 0,10 à 0,20
print("avant relance :", round(revenu_long_terme(P, v), 2), "DT")
print("après relance :", round(revenu_long_terme(P_relance, v), 2), "DT")
```
<!--sortie-->
```text
avant relance : 17.5 DT
après relance : 19.3 DT
```

La relance fait gagner environ 1,8 DT par client et par mois, soit +10 %. Avec 2 000 clients, cela représente environ 3 600 DT par mois, de quoi décider si la relance vaut son coût. C'est un modèle simple, mais l'idée (états, transitions, régime permanent) est utilisée en analyse de la fidélité, en marketing, et à la base de l'algorithme PageRank de Google (le web est une chaîne de Markov dont les états sont les pages).

### 2.6.3 Le processus de Poisson : des arrivées au hasard

Un **processus de Poisson** de cadence $\lambda$ modélise des événements arrivant au hasard et indépendamment : appels, commandes, pannes. Il a deux visages **équivalents**, que nous avons déjà croisés :

- le **nombre** d'événements dans une durée $t$ suit une loi de **Poisson**$(\lambda t)$ (2.2.4) ;
- les **temps d'attente** entre événements successifs sont **exponentiels**$(\lambda)$, indépendants (2.2.5).

Vérifions que ces deux visages coïncident, en construisant le processus par ses temps d'attente puis en comptant :

```python
from scipy import stats
rng = np.random.default_rng(15)
lam = 3                                               # 3 commandes par heure
n_heures = 50_000

comptes = np.empty(n_heures, dtype=int)
for h in range(n_heures):
    t, k = 0.0, 0
    while True:
        t += rng.exponential(1 / lam)                 # temps d'attente jusqu'à la prochaine commande
        if t > 1.0:                                   # on sort de l'heure
            break
        k += 1
    comptes[h] = k

print("moyenne des comptes   :", round(comptes.mean(), 3), "(théorie 3)")
print("variance des comptes  :", round(comptes.var(), 3), "(théorie 3)")
for k in range(0, 7):
    print(f"P(N = {k}) : simulée = {(comptes == k).mean():.4f}   Poisson(3) = {stats.poisson(3).pmf(k):.4f}")
```
<!--sortie-->
```text
moyenne des comptes   : 3.005 (théorie 3)
variance des comptes  : 2.98 (théorie 3)
P(N = 0) : simulée = 0.0492   Poisson(3) = 0.0498
P(N = 1) : simulée = 0.1491   Poisson(3) = 0.1494
P(N = 2) : simulée = 0.2228   Poisson(3) = 0.2240
P(N = 3) : simulée = 0.2241   Poisson(3) = 0.2240
P(N = 4) : simulée = 0.1687   Poisson(3) = 0.1680
P(N = 5) : simulée = 0.1023   Poisson(3) = 0.1008
P(N = 6) : simulée = 0.0511   Poisson(3) = 0.0504
```

Les fréquences simulées (obtenues **uniquement** avec des temps d'attente exponentiels) correspondent à la loi de Poisson : les deux descriptions sont bien le même objet. C'est pourquoi les files d'attente (guichets, serveurs, centres d'appels) se modélisent presque toujours avec ce processus.

> ✅ **À retenir (processus stochastiques).**
>
> - Un processus stochastique est une famille $(X_t)$ de variables aléatoires indexée par le temps.
> - **Marche aléatoire** : $E[S_n]=0$, $\sigma(S_n)=\sqrt n$ ; l'incertitude croît en $\sqrt{\text{temps}}$.
> - **Chaîne de Markov** : le futur ne dépend que du présent ; probabilités en $n$ pas $=\mathbf{P}^n$ ; **loi stationnaire** = vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1.
> - **Processus de Poisson** : nombres de Poisson ⇔ temps d'attente exponentiels.
