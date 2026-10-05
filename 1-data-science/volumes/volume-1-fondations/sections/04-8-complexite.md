## 4.8 ➕ Pour aller plus loin : complexité algorithmique et optimisation du code

> 🧭 **Section optionnelle.** Un code correct n'est pas toujours un code **utilisable** : le même résultat peut prendre une seconde ou trois jours selon la manière dont on s'y prend. La **complexité algorithmique** donne un langage pour comparer des méthodes *avant* de les écrire, et la mesure du temps (le *profilage*) dit où agir *après*. Cette section tient la promesse faite à la section 1.6, où nous avions vu que Dar Jasmin ne peut pas « énumérer tous les paniers possibles ».

### 4.8.1 L'idée : compter les opérations, pas les secondes

> 💡 **Intuition.** Yasmine cherche un client dans son carnet d'adresses. Si le carnet n'est **pas trié**, elle doit lire les noms un par un : pour 1 000 clients, il lui faut en moyenne 500 lectures, et 1 000 dans le pire cas. Si le carnet est **trié par ordre alphabétique**, elle l'ouvre au milieu, regarde si le nom cherché est avant ou après, et élimine la moitié du carnet à chaque étape : 1 000 clients se règlent en **10 étapes** (car $2^{10}=1\,024$). Avec un million de clients, la première méthode demande un million de lectures, la seconde **20**.

Ce qui compte n'est pas la vitesse de l'ordinateur ou du langage, mais la **manière dont le nombre d'opérations grandit quand la taille $n$ des données grandit**. C'est la **complexité** de l'algorithme. Vérifions-la en comptant effectivement les comparaisons :

```python
def recherche_lineaire(liste, cible):
    """Lit les éléments un par un. Renvoie le nombre de comparaisons effectuées."""
    comparaisons = 0
    for x in liste:
        comparaisons += 1
        if x == cible:
            break
    return comparaisons

def recherche_binaire(triee, cible):
    """Coupe l'intervalle en deux à chaque étape (liste TRIÉE). Renvoie le nombre de comparaisons."""
    bas, haut, comparaisons = 0, len(triee) - 1, 0
    while bas <= haut:
        milieu = (bas + haut) // 2
        comparaisons += 1
        if triee[milieu] == cible:
            break
        if triee[milieu] < cible:
            bas = milieu + 1
        else:
            haut = milieu - 1
    return comparaisons

for n in [1_000, 1_000_000]:
    clients = list(range(n))                 # identifiants triés 0, 1, ..., n-1
    cible = n - 1                            # le pire cas pour la lecture linéaire
    print(f"n = {n:>9,} : linéaire = {recherche_lineaire(clients, cible):>9,} comparaisons, "
          f"binaire = {recherche_binaire(clients, cible)} comparaisons")
```
<!--sortie-->
```text
n =     1,000 : linéaire =     1,000 comparaisons, binaire = 10 comparaisons
n = 1,000,000 : linéaire = 1,000,000 comparaisons, binaire = 20 comparaisons
```

Ces nombres ne dépendent pas de la machine : c'est ce qui rend la complexité si utile. La première méthode est **linéaire**, la seconde **logarithmique** : multiplier $n$ par 1 000 multiplie le travail de la première par 1 000, mais ajoute seulement une dizaine d'étapes à la seconde.

### 4.8.2 La notation $O(\cdot)$ : une définition rigoureuse

On ne se soucie pas des détails (« 3 opérations par tour de boucle » ou « 5 »). On garde seulement la **forme de la croissance**, d'où une notation qui « oublie » les constantes.

> 📐 **Définition (grand O).** On écrit $f(n)=O(g(n))$ s'il existe une constante $c>0$ et un rang $n_0$ tels que
> $$f(n)\le c\,g(n)\qquad\text{pour tout }n\ge n_0 .$$
> En mots : à partir d'un certain rang, $f$ ne dépasse pas un multiple fixe de $g$.

**Exemple fait à la main.** Un algorithme effectue $f(n)=3n^2+5n+2$ opérations. Montrons que $f(n)=O(n^2)$ avec $c=4$. Il faut $3n^2+5n+2\le 4n^2$, c'est-à-dire $n^2-5n-2\ge0$. Pour $n=5$ : $25-25-2=-2<0$ (l'inégalité est fausse). Pour $n=6$ : $36-30-2=4\ge0$ (vraie), et le trinôme est croissant ensuite : $n_0=6$ convient. Vérifions par le calcul :

```python
f = lambda n: 3 * n**2 + 5 * n + 2
faux = [n for n in range(1, 10_000) if f(n) > 4 * n**2]
print("valeurs de n pour lesquelles f(n) > 4 n² :", faux)
print("donc l'inégalité f(n) <= 4 n² est vraie dès n =", faux[-1] + 1)
```
<!--sortie-->
```text
valeurs de n pour lesquelles f(n) > 4 n² : [1, 2, 3, 4, 5]
donc l'inégalité f(n) <= 4 n² est vraie dès n = 6
```

Le terme dominant ($n^2$) décide de tout, les termes d'ordre inférieur ($5n$, $2$) et le facteur 3 disparaissent. Voici les classes que vous rencontrerez le plus souvent, de la plus rapide à la plus lente :

| Classe | Nom | Exemple typique |
|---|---|---|
| $O(1)$ | constante | lire l'élément d'indice 5 d'une liste ; chercher une clé dans un dictionnaire |
| $O(\log n)$ | logarithmique | recherche binaire dans une liste triée |
| $O(n)$ | linéaire | parcourir une liste ; calculer une moyenne |
| $O(n\log n)$ | quasi-linéaire | trier une liste (tri efficace) |
| $O(n^2)$ | quadratique | comparer **toutes les paires** d'éléments |
| $O(2^n)$ | exponentielle | énumérer **tous les sous-ensembles** (tous les paniers possibles) |

Pour sentir ce que ces lettres veulent dire en pratique, supposons un ordinateur capable de **un milliard d'opérations par seconde** (c'est du bon matériel) et calculons le temps que chaque classe demande :

```python
import math

def duree(operations, vitesse=1e9):
    """Traduit un nombre d'opérations en durée lisible."""
    s = operations / vitesse
    for seuil, nom in [(3.15e7, "ans"), (86400, "jours"), (3600, "heures"), (60, "minutes"), (1, "secondes")]:
        if s >= seuil:
            valeur = s / seuil
            return f"{valeur:,.1f} {nom}" if valeur < 1e6 else f"{valeur:.2e} {nom}"
    if s < 1e-6:
        return f"{s * 1e9:.3g} ns"
    if s < 1e-3:
        return f"{s * 1e6:.3g} µs"
    return f"{s * 1e3:.3g} ms"

print(f"{'n':>10} | {'n':>12} | {'n log2 n':>12} | {'n²':>14} | 2^n")
for n in [10, 40, 1_000, 1_000_000]:
    ligne = [duree(n), duree(n * math.log2(n)), duree(n**2)]
    expo = duree(2**n) if n <= 100 else "(astronomique)"
    print(f"{n:>10,} | {ligne[0]:>12} | {ligne[1]:>12} | {ligne[2]:>14} | {expo}")
print()
print("Pour n = 100 : 2^100 opérations demandent", duree(2**100))
print("(l'âge de l'Univers est d'environ 13,8 milliards d'années)")
```
<!--sortie-->
```text
         n |            n |     n log2 n |             n² | 2^n
        10 |        10 ns |      33.2 ns |         100 ns | 1.02 µs
        40 |        40 ns |       213 ns |         1.6 µs | 18.3 minutes
     1,000 |         1 µs |      9.97 µs |           1 ms | (astronomique)
 1,000,000 |         1 ms |      19.9 ms |   16.7 minutes | (astronomique)

Pour n = 100 : 2^100 opérations demandent 4.02e+13 ans
(l'âge de l'Univers est d'environ 13,8 milliards d'années)
```

Lisez la dernière colonne : pour $n=40$ éléments seulement, énumérer tous les sous-ensembles prendrait déjà plus de **18 minutes**... et pour $n=100$, des milliers de fois l'âge de l'Univers (voir les deux lignes sous le tableau). À l'inverse, pour un million de clients, la méthode linéaire ou quasi-linéaire reste à la portée d'un ordinateur portable (de l'ordre de la milliseconde à la vingtaine de millisecondes), alors que la méthode quadratique demande environ **17 minutes**. Même matériel, mêmes données : seule la **complexité** change.

> ⚠️ **Le grand O décrit la croissance, pas la vitesse.** Un algorithme $O(n)$ avec une énorme constante peut être plus lent qu'un $O(n^2)$ pour $n$ petit. Mais, quand les données grossissent, la forme de la courbe finit toujours par gagner : c'est ce que montre la figure ci-dessous.

![À gauche : nombre d'opérations selon la classe de complexité (échelle logarithmique en ordonnée). À droite : temps mesuré pour chercher un élément absent dans une liste (linéaire) et dans un ensemble (constant).](figures/ch04-complexite.png)

### 4.8.3 Mesurer : le temps, avec méthode

La théorie dit ce qui *devrait* se passer, la **mesure** vérifie ce qui se passe *vraiment*. Python fournit le module `timeit`. Deux précautions : répéter la mesure et garder le **minimum** (les autres programmes de la machine ne peuvent que ralentir la mesure, jamais l'accélérer), et comparer des **rapports** plutôt que des durées brutes, car celles-ci dépendent de la machine.

> ⚠️ **Les temps de cette section varient d'une machine à l'autre, et d'une exécution à l'autre.** Nous n'affichons donc que des **rapports arrondis**. Chez vous, les valeurs exactes différeront, mais l'**ordre de grandeur** doit être le même. Si ce n'est pas le cas, c'est intéressant : cherchez pourquoi !

**Test 1 : la liste contre l'ensemble.** Chercher si un identifiant est présent parmi $n$ clients. Dans une liste (`x in liste`), Python lit les éléments un par un : $O(n)$. Dans un **ensemble** (`set`), qui range ses éléments à la manière d'un dictionnaire, la recherche est en $O(1)$ en moyenne. Nous cherchons un élément **absent** (pire cas pour la liste) et nous multiplions $n$ par 100 :

```python
from timeit import repeat

def temps(f, nombre):
    """Temps minimal (en secondes) d'UN appel de f, sur 5 répétitions de `nombre` appels."""
    return min(repeat(f, number=nombre, repeat=5)) / nombre

resultats = {}
for n in [1_000, 100_000]:
    liste = list(range(n))
    ensemble = set(liste)
    resultats[n] = (temps(lambda: -1 in liste, 200), temps(lambda: -1 in ensemble, 200_000))

for nom, i in [("liste   ", 0), ("ensemble", 1)]:
    rapport = resultats[100_000][i] / resultats[1_000][i]
    print(f"{nom} : n est multiplié par 100  ->  le temps est multiplié par {rapport:.1f}")
```
<!--sortie-->
```text
liste    : n est multiplié par 100  ->  le temps est multiplié par 82.7
ensemble : n est multiplié par 100  ->  le temps est multiplié par 0.8
```

La liste a bien un temps proportionnel à $n$ (multiplier $n$ par 100 multiplie le temps par un nombre de l'ordre de 100), alors que l'ensemble est **insensible** à la taille (rapport proche de 1). Le gain n'est pas de 20 % : à $n=100\,000$, la figure (b) ci-dessous montre un écart de **plusieurs ordres de grandeur** entre les deux courbes.

> 🛠️ **Application directe.** Vous avez une liste de 100 000 clients à vérifier contre une liste de 50 000 clients « actifs ». Écrire `[c for c in clients if c in actifs]` avec `actifs` en **liste** fait jusqu'à $100\,000\times50\,000=5\cdot10^9$ comparaisons. Une seule ligne, `actifs = set(actifs)`, ramène cela à $\approx100\,000$ opérations. C'est probablement l'optimisation la plus rentable de toute la data science pratique.

**Test 2 : le test du « doublement ».** Une technique simple pour deviner la complexité d'un code : doubler $n$ et regarder de combien le temps est multiplié. Environ ×2 : linéaire. Environ ×4 : quadratique. Environ ×8 : cubique. Comparons deux manières de détecter des commandes en double :

```python
def doublons_naif(ids):
    """Compare chaque paire : O(n²)."""
    n = len(ids)
    return [ids[i] for i in range(n) for j in range(i + 1, n) if ids[i] == ids[j]]

def doublons_ensemble(ids):
    """Un seul passage avec un ensemble de valeurs déjà vues : O(n)."""
    vus, doubles = set(), []
    for x in ids:
        if x in vus:
            doubles.append(x)
        vus.add(x)
    return doubles

print("même résultat sur un petit exemple :", doublons_naif([4, 8, 4, 1, 8]), doublons_ensemble([4, 8, 4, 1, 8]))

for nom, f, tailles in [("naïf (paires)", doublons_naif, [1_000, 2_000, 4_000]),
                        ("ensemble     ", doublons_ensemble, [50_000, 100_000, 200_000])]:
    jeux = [list(range(n)) for n in tailles]                  # les données sont préparées AVANT la mesure
    t = [temps(lambda ids=ids: f(ids), 1) for ids in jeux]
    print(f"{nom} : n x2 -> temps x{t[1]/t[0]:.1f} ; n x2 -> temps x{t[2]/t[1]:.1f}")
```
<!--sortie-->
```text
même résultat sur un petit exemple : [4, 8] [4, 8]
naïf (paires) : n x2 -> temps x4.1 ; n x2 -> temps x4.1
ensemble      : n x2 -> temps x2.2 ; n x2 -> temps x2.5
```

La version par paires est **quadratique** : doubler $n$ multiplie le temps par un nombre proche de 4. La version à un passage est **linéaire** : doubler $n$ multiplie le temps par un nombre proche de 2 (un peu plus, parfois, à cause de la mémoire cache de l'ordinateur). Les mesures sont bruitées : relancez le bloc plusieurs fois et vous verrez ces rapports fluctuer légèrement, mais pas changer d'ordre de grandeur.

### 4.8.4 Boucles Python contre calcul vectorisé

Au 4.4, nous avons dit que NumPy et pandas sont « rapides ». Voici de quoi : calculer la somme des carrés de 1 million de montants. Les deux versions sont en $O(n)$, mais la **constante** n'est pas du tout la même : une boucle Python interprète les tours un par un, alors que NumPy exécute une boucle en code compilé.

```python
import numpy as np

rng = np.random.default_rng(7)
montants = np.exp(rng.normal(3.9, 0.55, size=1_000_000))       # 1 million de montants simulés
liste = montants.tolist()

def somme_carres_boucle(valeurs):
    total = 0.0
    for v in valeurs:
        total += v * v
    return total

def somme_carres_numpy(valeurs):
    return float(np.sum(valeurs ** 2))

print("mêmes résultats ?", np.isclose(somme_carres_boucle(liste), somme_carres_numpy(montants)))
t_boucle = temps(lambda: somme_carres_boucle(liste), 3)
t_numpy = temps(lambda: somme_carres_numpy(montants), 3)
print(f"la version NumPy est environ {t_boucle / t_numpy:.0f} fois plus rapide")
```
<!--sortie-->
```text
mêmes résultats ? True
la version NumPy est environ 20 fois plus rapide
```

Même complexité théorique, mais un facteur de **dizaines** (voire de centaines selon la machine) en faveur de NumPy : la complexité ne dit donc pas tout, les constantes comptent aussi. La règle pratique du data scientist : **dès que vous écrivez une boucle `for` sur les lignes d'un tableau, demandez-vous s'il existe une opération vectorisée**. Même chose avec pandas : une opération sur une colonne entière est presque toujours préférable à `apply` ligne par ligne.

```python
import pandas as pd

df = pd.DataFrame({"montant_ht": montants[:200_000]})
ttc_apply = df["montant_ht"].apply(lambda x: x * 1.19)       # une fonction Python par ligne
ttc_colonne = df["montant_ht"] * 1.19                        # une opération sur toute la colonne

print("mêmes résultats ?", np.allclose(ttc_apply, ttc_colonne))
t_apply = temps(lambda: df["montant_ht"].apply(lambda x: x * 1.19), 3)
t_colonne = temps(lambda: df["montant_ht"] * 1.19, 3)
print(f"l'opération sur la colonne est environ {t_apply / t_colonne:.0f} fois plus rapide")
```
<!--sortie-->
```text
mêmes résultats ? True
l'opération sur la colonne est environ 117 fois plus rapide
```

Même verdict avec pandas : `apply` appelle une fonction Python **pour chaque ligne**, alors que la multiplication de la colonne entière se fait d'un coup, dans du code compilé. Le facteur dépend de la machine (de l'ordre de plusieurs dizaines à plusieurs centaines de fois), mais le message est toujours le même.

### 4.8.5 La mémoïsation : ne jamais calculer deux fois la même chose

> 💡 **Intuition.** Quand on vous demande « combien font 17 × 23 ? », vous calculez. Si on vous le redemande dix fois, vous n'allez pas refaire le calcul : vous vous souvenez de la réponse. La **mémoïsation** (*memoization*) fait de même : on **mémorise** le résultat d'une fonction pour chaque argument déjà rencontré.

L'exemple classique est la suite de Fibonacci : $F(0)=0$, $F(1)=1$, $F(n)=F(n-1)+F(n-2)$. La définition récursive est très élégante, mais elle recalcule les mêmes valeurs un nombre énorme de fois : pour calculer $F(5)$, on calcule $F(3)$ deux fois, $F(2)$ trois fois, etc. Comptons les appels :

```python
from functools import lru_cache

appels = 0
def fib(n):
    global appels
    appels += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@lru_cache(maxsize=None)             # une seule ligne ajoutée : « mémorise les résultats »
def fib_memo(n):
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

for n in [5, 15, 25]:
    appels = 0
    valeur = fib(n)
    print(f"F({n}) = {valeur:>6} : version naïve = {appels:>7,} appels", end="")
    fib_memo.cache_clear()
    fib_memo(n)
    print(f", avec mémoire = {fib_memo.cache_info().misses} calculs")

print("F(80) avec mémoire :", fib_memo(80), "(la version naïve ne terminerait jamais)")
```
<!--sortie-->
```text
F(5) =      5 : version naïve =      15 appels, avec mémoire = 6 calculs
F(15) =    610 : version naïve =   1,973 appels, avec mémoire = 16 calculs
F(25) =  75025 : version naïve = 242,785 appels, avec mémoire = 26 calculs
F(80) avec mémoire : 23416728348467685 (la version naïve ne terminerait jamais)
```

Pour $F(25)$ : 242 785 appels contre 26 (un par valeur de 0 à 25). La version naïve est **exponentielle** (le nombre d'appels croît comme $1{,}6^n$), la version mémoïsée est **linéaire**. On a transformé un calcul impossible en un calcul instantané, en échange d'un peu de **mémoire** : c'est le compromis classique entre le temps et l'espace.

Ce compromis existe partout. Voici un exemple de l'espace utilisé par un million de montants :

```python
import sys

liste_python = montants.tolist()
octets_liste = sys.getsizeof(liste_python) + sum(sys.getsizeof(v) for v in liste_python)
print(f"liste Python de 1 000 000 de flottants : {octets_liste / 1e6:.0f} Mo")
print(f"tableau NumPy du même contenu         : {montants.nbytes / 1e6:.0f} Mo")
```
<!--sortie-->
```text
liste Python de 1 000 000 de flottants : 32 Mo
tableau NumPy du même contenu         : 8 Mo
```

Un tableau NumPy range ses nombres côte à côte, sans « emballage » : environ quatre fois moins de mémoire ici, ce qui est l'une des raisons de sa vitesse.

### 4.8.6 Profiler : mesurer avant d'optimiser

> 💡 **Règle d'or.** *« L'optimisation prématurée est la racine de tous les maux. »* (Donald Knuth). Ne devinez pas où le programme est lent : **mesurez**. Dans un programme de 50 lignes, 95 % du temps se passe typiquement dans 1 ou 2 lignes. Les optimiser donne tout ; optimiser le reste ne change rien.

L'outil s'appelle un **profileur** : `cProfile` enregistre, pour chaque fonction, le nombre d'appels et le temps passé. Voici un petit rapport qui nettoie des identifiants de commandes, cherche les doublons et calcule une moyenne. Il est écrit sans malice, mais l'une de ses étapes est un piège caché. Laquelle ?

```python
import cProfile
import pstats

def nettoyer(ids):
    return [int(x) for x in ids]

def moyenne(ids):
    return sum(ids) / len(ids)

def rapport(ids):
    propres = nettoyer(ids)
    n_doublons = len(doublons_naif(propres))
    return n_doublons, moyenne(propres)

donnees = [str(i % 3000) for i in range(6000)]       # 6 000 identifiants dont 3 000 en double

profil = cProfile.Profile()
profil.runcall(rapport, donnees)
stats = pstats.Stats(profil)
total = sum(tt for (_, _, tt, _, _) in stats.stats.values())
classement = sorted(stats.stats.items(), key=lambda kv: kv[1][2], reverse=True)

print(f"{'fonction':<18}{'appels':>10}{'part du temps':>16}")
for (fichier, ligne, nom), (cc, nc, tt, ct, _) in [c for c in classement if c[0][0] != "~"][:4]:   # on écarte les fonctions internes
    print(f"{nom:<18}{nc:>10,}{100 * tt / total:>14.0f} %")
```
<!--sortie-->
```text
fonction              appels   part du temps
doublons_naif              1           100 %
nettoyer                   1             0 %
rapport                    1             0 %
moyenne                    1             0 %
```

Le coupable est immédiat : `doublons_naif` (notre détecteur par paires, quadratique) occupe l'immense majorité du temps, loin devant le nettoyage et la moyenne, qui ne comptent presque pour rien. Inutile d'accélérer `nettoyer` : on remplace plutôt `doublons_naif` par `doublons_ensemble`, qui est linéaire (4.8.3). C'est la démarche en trois temps de tout travail d'optimisation : **mesurer**, **trouver le goulot d'étranglement**, **changer d'algorithme ou de structure de données**, puis **mesurer encore** pour confirmer le gain.

> ⚠️ **Ordre des priorités.** (1) D'abord un code **correct** et lisible (4.6, avec ses tests). (2) Ensuite, si c'est trop lent, **mesurer**. (3) Optimiser d'abord l'**algorithme** (complexité), ensuite la **vectorisation**, et seulement en dernier recours les micro-détails. Un test qui reste vert après l'optimisation prouve que vous n'avez rien cassé.

### 4.8.7 Application : les paires de produits achetés ensemble

Retour à Dar Jasmin. Yasmine voudrait savoir quels produits sont **souvent achetés ensemble** pour proposer des offres groupées. Son catalogue contient 40 produits. Première idée : examiner **tous les paniers possibles** de 10 produits... Souvenez-vous du 1.6 : il y en a $\binom{40}{10}=847\,660\,528$. Même à un million de paniers examinés par seconde, cela fait plus de 14 minutes *pour une seule taille de panier*, et le nombre de sous-ensembles totaux est $2^{40}\approx 10^{12}$. Mais Yasmine n'a pas besoin de tous les paniers **possibles** : seulement des paniers **réellement achetés**. Il suffit de compter, panier par panier, les paires qu'il contient : la complexité dépend alors de la taille des données, pas de la taille de l'univers des possibles.

```python
from collections import Counter
from itertools import combinations

rng = np.random.default_rng(21)
n_paniers, n_produits = 20_000, 40
paniers = []
for _ in range(n_paniers):
    taille = int(rng.integers(2, 6))                         # entre 2 et 5 produits
    panier = set(rng.choice(n_produits, size=taille, replace=False).tolist())
    if rng.random() < 0.15:                                  # 15 % des clientes achètent le couple 7 + 12
        panier |= {7, 12}
    paniers.append(sorted(panier))

compteur = Counter()
operations = 0
for panier in paniers:
    for paire in combinations(panier, 2):                    # toutes les paires DU panier
        compteur[paire] += 1
        operations += 1

print(f"{n_paniers:,} paniers lus, {operations:,} paires comptées au total")
print(f"(contre {math.comb(40, 10):,} sous-ensembles à 10 produits en énumérant tout)")
print("les 3 paires les plus fréquentes :")
for paire, effectif in compteur.most_common(3):
    print(f"   produits {paire} : {effectif:,} paniers ({100 * effectif / n_paniers:.1f} %)")
```
<!--sortie-->
```text
20,000 paniers lus, 120,761 paires comptées au total
(contre 847,660,528 sous-ensembles à 10 produits en énumérant tout)
les 3 paires les plus fréquentes :
   produits (7, 12) : 3,017 paniers (15.1 %)
   produits (7, 8) : 395 paniers (2.0 %)
   produits (5, 12) : 392 paniers (2.0 %)
```

En à peine plus de 120 000 opérations (au lieu de plusieurs centaines de millions), le couple $(7,12)$ ressort nettement : c'est l'association que nous avions planifiée dans la simulation, et les autres paires, simplement dues au hasard, ont des effectifs bien plus faibles. La méthode est **linéaire** en nombre de paniers (chaque panier de $k$ produits fournit $\binom k2$ paires, et $k\le 5$ ici). C'est exactement l'idée derrière les algorithmes de recommandation (« règles d'association ») : on compte ce qui s'est vraiment passé, on n'explore pas ce qui aurait pu se passer.

> ✅ **À retenir (complexité et optimisation).**
>
> - La **complexité** mesure comment le nombre d'opérations grandit avec $n$, indépendamment de la machine. $f(n)=O(g(n))$ : à partir d'un rang $n_0$, $f\le c\,g$.
> - De la plus lente à la plus rapide : $O(2^n)$ (impraticable dès $n\approx 50$), $O(n^2)$, $O(n\log n)$, $O(n)$, $O(\log n)$, $O(1)$.
> - **Structure de données = complexité.** Chercher dans une liste est $O(n)$, dans un `set` ou un dictionnaire $O(1)$ ; une liste triée permet la recherche binaire en $O(\log n)$.
> - **Test du doublement** : $n$ double, temps ×2 → linéaire ; ×4 → quadratique.
> - **Vectorisez** : NumPy et pandas battent les boucles Python de plusieurs ordres de grandeur, à complexité égale.
> - **Mémoïsation** (`@lru_cache`) : échanger de la mémoire contre du temps, en ne calculant jamais deux fois la même chose.
> - **Mesurez, ne devinez pas** : profilez (`cProfile`), trouvez le goulot, changez d'algorithme, remesurez. Les durées varient d'une machine à l'autre ; les ordres de grandeur et les rapports, non.
