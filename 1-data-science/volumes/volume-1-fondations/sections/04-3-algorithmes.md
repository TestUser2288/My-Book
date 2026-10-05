## 4.3 Algorithmes et structures de données

> 💡 **Intuition.** Un **algorithme** est une méthode précise pour résoudre un problème, comme une recette. Une **structure de données** est la façon dont on range les ingrédients. Deux cuisiniers peuvent faire le même plat, l'un en dix minutes parce que ses ingrédients sont bien rangés, l'autre en deux heures parce qu'il fouille dans tous les tiroirs. En data science, la différence se joue entre un calcul qui prend une seconde et un calcul qui ne finit jamais.

Cette section est plus « informatique » que les autres : on y apprend à **penser** un calcul, à le **prouver** correct et à **compter** son coût. Rassurez-vous, tout part d'exemples faits à la main.

### 4.3.1 Qu'est-ce qu'un algorithme ?

Un algorithme est une suite d'instructions **non ambiguës** qui, pour toute entrée valide, **se termine** et produit la **bonne** sortie. Trois exigences, donc : être précis, **terminer**, être **correct**.

**Exemple fil rouge : trouver la plus grosse commande** d'une liste, sans utiliser `max`. Méthode : on retient « le plus grand vu jusqu'ici » et on parcourt la liste, en le mettant à jour chaque fois qu'on trouve mieux.

**À la main**, sur $[44{,}8;\ 34{,}5;\ 88{,}2;\ 30{,}1;\ 110{,}1]$ :

| Élément lu | Plus grand vu jusqu'ici |
|---|---|
| 44,8 (on commence avec le premier) | 44,8 |
| 34,5 | 44,8 (34,5 est plus petit) |
| 88,2 | **88,2** (nouveau record) |
| 30,1 | 88,2 |
| 110,1 | **110,1** (nouveau record) |

Résultat : 110,1. En code, avec un compteur de comparaisons pour mesurer le coût :

```python
def plus_grand(valeurs):
    """Renvoie (le maximum, le nombre de comparaisons effectuées)."""
    record = valeurs[0]
    comparaisons = 0
    for v in valeurs[1:]:
        comparaisons += 1
        if v > record:
            record = v
    return record, comparaisons

print(plus_grand([44.8, 34.5, 88.2, 30.1, 110.1]))
```
<!--sortie-->
```text
(110.1, 4)
```

> 📐 **Preuve de correction (par invariant de boucle).** Un **invariant** est une propriété vraie *avant* chaque tour de boucle, qu'on prouve comme une récurrence.
>
> **Invariant :** après avoir lu les $k$ premiers éléments, `record` est le maximum de ces $k$ éléments.
>
> *Initialisation* ($k=1$) : `record` est le premier élément, qui est bien le maximum d'une liste d'un élément.
> *Conservation* : supposons l'invariant vrai pour $k$. On lit l'élément $v$ n° $k+1$. Si $v>$ `record`, le nouveau record est $v$, qui est supérieur à tous les précédents ; sinon `record` reste le maximum. Dans les deux cas l'invariant est vrai pour $k+1$.
> *Fin* : la boucle `for` parcourt une liste finie : elle **termine** après $n-1$ tours. Pour $k=n$, l'invariant dit que `record` est le maximum de **toute** la liste. $\blacksquare$
>
> *Coût :* exactement $n-1$ comparaisons, quelle que soit la liste. On dit que l'algorithme est **linéaire** (section 4.8).

Cette habitude (**invariant, terminaison, coût**) est la boîte à outils de base pour tout algorithme, y compris les plus sophistiqués.

### 4.3.2 Choisir sa structure de données

Les quatre collections de 4.1.4 ne sont pas interchangeables : chacune est **bonne** pour certaines opérations et **mauvaise** pour d'autres.

| Besoin | Meilleure structure | Pourquoi |
|---|---|---|
| Garder un ordre, accéder par position | **liste** | `x[i]` est immédiat |
| Retrouver une valeur à partir d'un nom, d'un identifiant | **dictionnaire** | accès direct par clé |
| Savoir « est-ce que X est déjà vu ? », éliminer les doublons | **ensemble** | test d'appartenance immédiat |
| Traiter dans l'ordre d'arrivée | **file** (`deque`) | retrait au début immédiat |
| Revenir en arrière (annuler) | **pile** (une liste utilisée par la fin) | dernier entré, premier sorti |

**Pourquoi un dictionnaire ou un ensemble est-il si rapide ?** Ils reposent sur une **table de hachage** : une fonction (le *hachage*) transforme la clé en un numéro de case, et l'on va **directement** à cette case, sans parcourir quoi que ce soit. Imaginez un vestiaire où chaque cintre porte le numéro calculé à partir du nom du client : pas besoin de passer en revue tous les manteaux. Une liste, elle, doit être parcourue de gauche à droite pour savoir si une valeur y figure. Mesurons ce parcours en **nombre de comparaisons** (une mesure qui ne dépend pas de l'ordinateur) sur nos 400 montants :

```python
import csv

with open("donnees/commandes.csv", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))
montants = [float(l["montant"]) for l in lignes]
print("nombre de montants :", len(montants))

def recherche_lineaire(liste, cible):
    """Parcourt la liste de gauche à droite. Renvoie (position ou -1, nombre de comparaisons)."""
    comparaisons = 0
    for i, v in enumerate(liste):
        comparaisons += 1
        if v == cible:
            return i, comparaisons
    return -1, comparaisons

print("cherche 44.8  (en tête) :", recherche_lineaire(montants, 44.8))
print("cherche 255.7 (la plus grosse commande) :", recherche_lineaire(montants, 255.7))
print("cherche 1.0   (absent)  :", recherche_lineaire(montants, 1.0))
```
<!--sortie-->
```text
nombre de montants : 400
cherche 44.8  (en tête) : (0, 1)
cherche 255.7 (la plus grosse commande) : (156, 157)
cherche 1.0   (absent)  : (-1, 400)
```

Quand la valeur est **absente**, il faut lire les 400 éléments pour en être sûr : le pire cas est proportionnel à la taille de la liste. Un ensemble ou un dictionnaire, lui, répond en une seule opération, quel que soit le nombre d'éléments. Nous mesurerons l'écart en secondes à la section 4.8 ; retenez pour l'instant l'ordre de grandeur : pour un million d'éléments, une liste doit parcourir *jusqu'à un million* de cases, un ensemble en regarde *quelques-unes*.

Application directe : **compter les montants différents** et **les plus fréquents** :

```python
from collections import Counter

distincts = set(montants)
print("montants distincts :", len(distincts), "sur", len(montants), "commandes")

frequences = Counter(montants)
print("les 5 montants les plus fréquents :", frequences.most_common(5))
```
<!--sortie-->
```text
montants distincts : 344 sur 400 commandes
les 5 montants les plus fréquents : [(37.5, 4), (53.5, 4), (65.8, 3), (35.7, 3), (21.5, 3)]
```

Un `Counter` est un dictionnaire spécialisé dans le comptage : la clé est la valeur, la valeur est son nombre d'occurrences. C'est l'outil idéal pour une table de fréquences (3.1) construite à la main.

### 4.3.3 Piles et files

Deux structures très simples, définies par **l'ordre** dans lequel on y entre et sort.

- La **pile** (*stack*, **LIFO** : *last in, first out*) : le dernier arrivé est le premier servi. Une pile d'assiettes : on pose et on reprend toujours en haut. C'est le mécanisme du bouton « annuler » de votre éditeur de texte, et de l'**historique** de votre navigateur.
- La **file** (*queue*, **FIFO** : *first in, first out*) : le premier arrivé est le premier servi. La file d'attente à la caisse.

En Python, une pile est une simple liste que l'on manipule **par la fin** (`append` pour empiler, `pop` pour dépiler). Pour une file, on utilise `deque` (prononcez « dèque »), car retirer un élément au **début** d'une liste est lent, alors qu'un `deque` le fait à coût constant.

```python
from collections import deque

pile = []
for action in ["ajouter bol", "ajouter tasse", "ajouter plateau"]:
    pile.append(action)                       # empiler
print("pile :", pile)
print("annuler :", pile.pop(), "| il reste :", pile)      # dépiler : le dernier entré sort

file = deque()
for client in ["Sana", "Mehdi", "Ines"]:
    file.append(client)                       # arriver au bout de la file
print("file :", list(file))
print("servi :", file.popleft(), "| il reste :", list(file))   # le premier arrivé sort
```
<!--sortie-->
```text
pile : ['ajouter bol', 'ajouter tasse', 'ajouter plateau']
annuler : ajouter plateau | il reste : ['ajouter bol', 'ajouter tasse']
file : ['Sana', 'Mehdi', 'Ines']
servi : Sana | il reste : ['Mehdi', 'Ines']
```

**Application 1 : vérifier les parenthèses d'une formule (avec une pile).** Un tableur doit rejeter `=(B2+B3)*(1-(C2/100)` car il manque une parenthèse fermante. Comment un programme le détecte-t-il ?

*Idée :* à chaque parenthèse **ouvrante**, on empile ; à chaque parenthèse **fermante**, on dépile et on vérifie qu'elle correspond. La formule est correcte si, **à la fin**, la pile est vide et si nous n'avons jamais dû dépiler une pile vide.

**À la main** sur `(1+(2*3))` : `(` → pile `[(]` ; `1`, `+` ignorés ; `(` → `[(, (]` ; `2*3` ignorés ; `)` → on dépile : `[(]` ; `)` → on dépile : `[]`. Pile vide à la fin : équilibrée. Sur `(1+2))` : après le premier `)` la pile est vide ; le second `)` ne trouve rien à dépiler : **erreur**.

```python
def equilibre(formule):
    ouvrantes = {")": "(", "]": "[", "}": "{"}
    pile = []
    for caractere in formule:
        if caractere in "([{":
            pile.append(caractere)
        elif caractere in ")]}":
            if not pile or pile.pop() != ouvrantes[caractere]:
                return False
    return not pile            # vrai seulement si tout a été refermé

tests = ["(1+(2*3))", "(1+2))", "=(B2+B3)*(1-(C2/100)", "[(1+2)*3]", "[(1+2]*3)", ""]
for t in tests:
    print(f"{t!r:<28} -> {equilibre(t)}")
```
<!--sortie-->
```text
'(1+(2*3))'                  -> True
'(1+2))'                     -> False
'=(B2+B3)*(1-(C2/100)'       -> False
'[(1+2)*3]'                  -> True
'[(1+2]*3)'                  -> False
''                           -> True
```

Le cas `[(1+2]*3)` est instructif : il y a autant d'ouvrantes que de fermantes, mais elles sont **mal imbriquées** : une simple comptabilité ne suffirait pas, la pile, si. Voilà pourquoi tous les compilateurs et analyseurs de formules utilisent cette structure.

**Application 2 : une file d'attente à l'atelier d'emballage.** Cinq commandes arrivent aux minutes 0, 1, 2, 10 et 11. L'emballage d'une commande dure 4 minutes, avec **une seule** emballeuse, qui traite les commandes dans l'ordre d'arrivée.

**À la main** :

| Commande | Arrivée | Début d'emballage | Attente |
|---|---|---|---|
| 1 | 0 | 0 | 0 |
| 2 | 1 | 4 (la 1 se termine à 4) | 3 |
| 3 | 2 | 8 | 6 |
| 4 | 10 | 12 (la 3 se termine à 12) | 2 |
| 5 | 11 | 16 | 5 |

Attente moyenne : $(0+3+6+2+5)/5=3{,}2$ minutes. Le programme :

```python
def simuler_file(arrivees, duree):
    attente_totale, libre_a = 0, 0
    file = deque(arrivees)                 # les commandes en attente, dans l'ordre
    attentes = []
    while file:
        arrivee = file.popleft()           # premier arrivé, premier servi
        debut = max(arrivee, libre_a)      # on commence quand la commande est là ET l'emballeuse libre
        attentes.append(debut - arrivee)
        libre_a = debut + duree
    return attentes

attentes = simuler_file([0, 1, 2, 10, 11], duree=4)
print("attentes :", attentes, "| moyenne :", sum(attentes) / len(attentes))
```
<!--sortie-->
```text
attentes : [0, 3, 6, 2, 5] | moyenne : 3.2
```

Cette mini-simulation est le premier pas vers la **théorie des files d'attente**, vue au chapitre 2 (processus de Poisson et loi exponentielle) : on peut maintenant la tester numériquement.

### 4.3.4 La récursion : une fonction qui s'appelle elle-même

Une fonction est **récursive** quand elle se résout en s'appelant sur un problème **plus petit**. Pour qu'elle marche, il faut toujours deux ingrédients :

1. un **cas de base** (le plus petit problème, résolu directement) ;
2. un **cas général** qui ramène le problème à un problème **strictement plus petit**.

Sans cela, la fonction s'appelle à l'infini (Python finit par s'arrêter avec une erreur `RecursionError`).

**Premier exemple : la factorielle.** $n!=n\times(n-1)!$ avec $0!=1$. Elle compte les façons d'ordonner $n$ objets (1.6). **À la main** : $4!=4\times3!=4\times3\times2!=4\times3\times2\times1!=24$.

```python
def factorielle(n):
    if n == 0:                           # cas de base
        return 1
    return n * factorielle(n - 1)        # cas général : un problème plus petit

print([factorielle(n) for n in range(7)])
```
<!--sortie-->
```text
[1, 1, 2, 6, 24, 120, 720]
```

> 📐 **Preuve (par récurrence).** *Terminaison* : à chaque appel, $n$ diminue de 1 et reste un entier $\ge0$ : on atteint forcément le cas de base. *Correction* : `factorielle(0)` renvoie $1=0!$ (base). Si `factorielle(n-1)` renvoie $(n-1)!$ (hypothèse), alors `factorielle(n)` renvoie $n\times(n-1)!=n!$. $\blacksquare$ C'est la même récurrence qu'en mathématiques : écrire une fonction récursive *est* écrire une preuve par récurrence.

**Une application naturelle : parcourir un arbre.** Le catalogue de Dar Jasmin est organisé en catégories contenant des sous-catégories contenant des produits (prix, stock). On veut la **valeur totale du stock**. La difficulté : on ne sait pas combien de niveaux il y a. La récursion le fait tout naturellement : *la valeur d'une catégorie est la somme des valeurs de ses éléments, la valeur d'un produit est prix × stock.*

**À la main** : bol bleu $12{,}5\times10=125$ ; bol vert $12{,}5\times4=50$ ; tasse $8\times20=160$ ; bougie $15{,}9\times6=95{,}4$ ; plateau $45\times2=90$. Total : $520{,}4$ DT.

```python
catalogue = {
    "Vaisselle": {
        "bols": {"bol bleu": (12.5, 10), "bol vert": (12.5, 4)},
        "tasses": {"tasse": (8.0, 20)},
    },
    "Déco": {"bougie": (15.9, 6), "plateau": (45.0, 2)},
}

def valeur_stock(noeud):
    if isinstance(noeud, tuple):                     # cas de base : un produit (prix, stock)
        prix, stock = noeud
        return prix * stock
    return sum(valeur_stock(enfant) for enfant in noeud.values())   # une catégorie

print("valeur totale :", round(valeur_stock(catalogue), 2), "DT")
for categorie, contenu in catalogue.items():
    print(f"  {categorie:<10} {valeur_stock(contenu):8.2f} DT")
```
<!--sortie-->
```text
valeur totale : 520.4 DT
  Vaisselle    335.00 DT
  Déco         185.40 DT
```

**Le danger : la récursion naïve peut être catastrophique.** Les nombres de Fibonacci ($F_0=0$, $F_1=1$, $F_n=F_{n-1}+F_{n-2}$) se codent en deux lignes récursives, mais le programme refait **sans cesse les mêmes calculs** : pour calculer `fib(5)`, on calcule deux fois `fib(3)`, trois fois `fib(2)`, etc. Comptons les appels :

```python
from functools import lru_cache

appels = 0
def fib(n):
    global appels
    appels += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

for n in (10, 20, 25):
    appels = 0
    valeur = fib(n)
    print(f"fib({n}) = {valeur}   nombre d'appels : {appels}")

appels_memo = 0
@lru_cache(maxsize=None)                  # « mémoïsation » : on retient les résultats déjà calculés
def fib_memo(n):
    global appels_memo
    appels_memo += 1
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

print(f"fib_memo(25) = {fib_memo(25)}   nombre d'exécutions réelles : {appels_memo}")
```
<!--sortie-->
```text
fib(10) = 55   nombre d'appels : 177
fib(20) = 6765   nombre d'appels : 21891
fib(25) = 75025   nombre d'appels : 242785
fib_memo(25) = 75025   nombre d'exécutions réelles : 26
```

Le nombre d'appels de la version naïve **explose** (il est lui-même de l'ordre de $F_n$, donc il croît environ de 62 % à chaque pas), alors que la version qui **mémorise** ne calcule chaque valeur qu'une seule fois. Même problème, même résultat, des ordres de grandeur d'écart : c'est tout l'enjeu de la complexité (section ➕ 4.8). La mémoïsation est la première idée de la **programmation dynamique**, très utilisée en optimisation.

> ⚠️ **Récursion ou boucle ?** Tout algorithme récursif peut s'écrire avec une boucle (et inversement). La récursion est souvent plus *lisible* pour les structures **arborescentes** (catalogue, dossiers, expressions) ; la boucle est plus économe en mémoire. Python limite la profondeur de récursion à environ 1 000 appels : au-delà, préférez une boucle.

### 4.3.5 Rechercher : de la liste à la dichotomie

Reprenons la **recherche linéaire** de 4.3.2 : sur une liste quelconque, elle est inévitable. Mais si la liste est **triée**, on peut faire beaucoup mieux, comme quand vous cherchez un mot dans un dictionnaire papier : vous ouvrez au milieu, vous voyez si le mot est avant ou après, et vous éliminez **la moitié** des pages d'un coup. C'est la **recherche dichotomique** (*binary search*).

**À la main.** Liste triée de 9 montants : $[8;\ 15;\ 22;\ 31;\ 40;\ 47;\ 58;\ 66;\ 79]$ (indices 0 à 8). On cherche 47.

| Étape | Zone d'indices $[g,d]$ | Milieu $m=\lfloor(g+d)/2\rfloor$ | Valeur | Décision |
|---|---|---|---|---|
| 1 | $[0,8]$ | 4 | 40 | $40<47$ : on cherche à droite, $g=5$ |
| 2 | $[5,8]$ | 6 | 58 | $58>47$ : on cherche à gauche, $d=5$ |
| 3 | $[5,5]$ | 5 | 47 | trouvé ! |

Trois étapes au lieu de six pour la recherche linéaire. Le programme :

```python
def recherche_dichotomique(triee, cible):
    """Renvoie (position ou -1, nombre de comparaisons). La liste doit être triée."""
    g, d, comparaisons = 0, len(triee) - 1, 0
    while g <= d:
        m = (g + d) // 2
        comparaisons += 1
        if triee[m] == cible:
            return m, comparaisons
        elif triee[m] < cible:
            g = m + 1
        else:
            d = m - 1
    return -1, comparaisons

exemple = [8, 15, 22, 31, 40, 47, 58, 66, 79]
print(recherche_dichotomique(exemple, 47))
print(recherche_dichotomique(exemple, 50))      # absent
```
<!--sortie-->
```text
(5, 3)
(-1, 3)
```

> 📐 **Preuve de correction et de terminaison.**
>
> **Invariant :** *si la cible est dans la liste, elle se trouve à un indice entre $g$ et $d$ inclus.*
> *Initialisation* : $g=0$, $d=n-1$ : toute la liste. *Conservation* : si `triee[m] < cible`, comme la liste est triée, tous les éléments d'indice $\le m$ sont $<$ cible : on peut les éliminer, d'où $g=m+1$. Symétriquement si `triee[m] > cible`. L'invariant reste vrai. *Conclusion* : si la boucle s'arrête parce que $g>d$, la zone est vide, donc la cible est absente (on renvoie $-1$) ; si elle s'arrête sur `triee[m] == cible`, c'est gagné.
>
> **Terminaison et coût :** appelons $s=d-g+1$ la taille de la zone. À chaque tour, la nouvelle zone a au plus $\lfloor s/2\rfloor$ éléments (on a éliminé le milieu et une moitié). Après $k$ tours, la taille est au plus $\lfloor n/2^k\rfloor$, qui devient $0$ dès que $2^k>n$. L'algorithme s'arrête donc en **au plus $\lfloor\log_2 n\rfloor+1$ tours**. $\blacksquare$

Vérifions la borne théorique sur nos 400 montants triés, en cherchant **chacun** des 400 montants et en relevant le pire cas :

```python
import math

triee = sorted(montants)
pire = max(recherche_dichotomique(triee, v)[1] for v in montants)
moyen = sum(recherche_dichotomique(triee, v)[1] for v in montants) / len(montants)
print("borne théorique (floor(log2 n) + 1) :", math.floor(math.log2(len(montants))) + 1)
print("pire cas observé                     :", pire)
print("moyenne observée                     :", round(moyen, 2))
print("recherche absente (linéaire / dichotomique) :",
      recherche_lineaire(triee, 1.0)[1], "/", recherche_dichotomique(triee, 1.0)[1])
```
<!--sortie-->
```text
borne théorique (floor(log2 n) + 1) : 9
pire cas observé                     : 9
moyenne observée                     : 7.42
recherche absente (linéaire / dichotomique) : 400 / 8
```

Le pire cas observé respecte bien la borne (au plus 9 comparaisons pour 400 éléments, et 8 pour une valeur absente comme 1,0, contre 400 pour la recherche linéaire de cette même valeur). Pour **un million** d'éléments : $\lfloor\log_2 10^6\rfloor+1=20$ comparaisons seulement. C'est le pouvoir du logarithme : chaque doublement de la taille ne coûte qu'**une** comparaison de plus.

**Application : le seuil de livraison gratuite.** Yasmine veut offrir la livraison à partir d'un seuil tel qu'environ **30 %** des commandes y aient droit. Une liste triée permet de répondre à « quelle part des commandes dépasse $s$ DT ? » avec le module `bisect`, qui contient la recherche dichotomique toute faite :

```python
import bisect
import numpy as np

def part_au_dessus(seuil):
    # bisect_left donne le nombre de montants STRICTEMENT inférieurs au seuil
    return 1 - bisect.bisect_left(triee, seuil) / len(triee)

for seuil in (50, 60, 70, 80, 90, 100):
    print(f"seuil {seuil:3d} DT : {part_au_dessus(seuil):6.1%} des commandes y ont droit")

print("quantile 70 % (numpy) :", round(float(np.quantile(montants, 0.70)), 1), "DT")
```
<!--sortie-->
```text
seuil  50 DT :  51.2% des commandes y ont droit
seuil  60 DT :  41.0% des commandes y ont droit
seuil  70 DT :  29.2% des commandes y ont droit
seuil  80 DT :  21.8% des commandes y ont droit
seuil  90 DT :  17.2% des commandes y ont droit
seuil 100 DT :  13.0% des commandes y ont droit
quantile 70 % (numpy) : 68.9 DT
```

Le tableau montre qu'un seuil de **70 DT** concerne 29,2 % des commandes, soit à peu près les 30 % visés ; le quantile à 70 % calculé par NumPy (68,9 DT) pointe au même endroit, puisque par définition 30 % des commandes lui sont supérieures. Nous avons retrouvé par un algorithme de recherche ce que les quantiles du 3.1.3 donnaient directement, un bon moyen de comprendre ce que « quantile » veut dire : *la position dans la liste triée*.

### 4.3.6 Trier

**Trier** est l'un des problèmes les plus étudiés. Il sert partout : classer les clients, calculer une médiane, préparer une recherche dichotomique. Voyons deux algorithmes : un simple, un efficace.

**Le tri par insertion.** On procède comme avec des cartes à jouer : on prend les éléments un à un et on **insère** chacun à sa place dans la partie déjà triée.

**À la main** sur $[30;\ 12;\ 25;\ 8;\ 19]$ (la partie triée est à gauche de la double barre ‖) :

| Étape | Liste | Action |
|---|---|---|
| départ | [30 ‖ 12, 25, 8, 19] | |
| 1 | [12, 30 ‖ 25, 8, 19] | 12 passe devant 30 |
| 2 | [12, 25, 30 ‖ 8, 19] | 25 passe devant 30 |
| 3 | [8, 12, 25, 30 ‖ 19] | 8 passe devant tous |
| 4 | $[8, 12, 19, 25, 30]$ | 19 s'insère entre 12 et 25 |

```python
def tri_insertion(liste):
    a = list(liste)                       # on travaille sur une copie
    comparaisons = 0
    for i in range(1, len(a)):
        x = a[i]
        j = i - 1
        while j >= 0:
            comparaisons += 1
            if a[j] > x:
                a[j + 1] = a[j]           # on décale vers la droite
                j -= 1
            else:
                break
        a[j + 1] = x                      # on insère x à sa place
    return a, comparaisons

print(tri_insertion([30, 12, 25, 8, 19]))
```
<!--sortie-->
```text
([8, 12, 19, 25, 30], 9)
```

> 📐 **Correction.** *Invariant :* avant le tour $i$, les $i$ premiers éléments de `a` sont triés (et ce sont les $i$ premiers éléments d'origine). Au tour $i$, on décale vers la droite tous les éléments plus grands que $x$ puis on place $x$ juste avant eux : les $i+1$ premiers éléments sont triés. À la fin ($i=n$), tout est trié. *Terminaison :* deux boucles bornées. *Coût :* au pire (liste triée à l'envers), le tour $i$ fait $i$ comparaisons, soit $1+2+\dots+(n-1)=n(n-1)/2$ comparaisons au total, de l'ordre de $n^2$. $\blacksquare$

**Le tri fusion** (*merge sort*) applique la stratégie « **diviser pour régner** » : on coupe la liste en deux, on trie chaque moitié (récursivement), puis on **fusionne** les deux moitiés triées. Fusionner est facile : on compare les deux premiers éléments des moitiés, on prend le plus petit, et on recommence, comme deux files de gens que l'on entrelace.

**À la main** sur $[44;\ 12;\ 30;\ 8;\ 25;\ 19]$ : on coupe en $[44,12,30]$ et $[8,25,19]$ ; chacun est trié en $[12,30,44]$ et $[8,19,25]$ ; la fusion donne $8<12$ → 8 ; $12<19$ → 12 ; $19<30$ → 19 ; $25<30$ → 25 ; il reste $30,\,44$ : $[8,12,19,25,30,44]$.

```python
def tri_fusion(liste):
    """Renvoie (liste triée, nombre de comparaisons)."""
    if len(liste) <= 1:                           # cas de base
        return list(liste), 0
    milieu = len(liste) // 2
    gauche, c1 = tri_fusion(liste[:milieu])
    droite, c2 = tri_fusion(liste[milieu:])
    fusion, i, j, c = [], 0, 0, 0
    while i < len(gauche) and j < len(droite):    # on entrelace les deux moitiés triées
        c += 1
        if gauche[i] <= droite[j]:
            fusion.append(gauche[i]); i += 1
        else:
            fusion.append(droite[j]); j += 1
    fusion.extend(gauche[i:])                     # il ne reste d'un seul côté
    fusion.extend(droite[j:])
    return fusion, c1 + c2 + c

print(tri_fusion([44, 12, 30, 8, 25, 19]))
```
<!--sortie-->
```text
([8, 12, 19, 25, 30, 44], 9)
```

Comparons les deux sur nos 400 montants (ce sont aussi des sorties à contrôler contre le tri de Python) :

```python
tri1, c_ins = tri_insertion(montants)
tri2, c_fus = tri_fusion(montants)
print("tri par insertion : ", c_ins, "comparaisons")
print("tri fusion        : ", c_fus, "comparaisons")
print("même résultat que sorted() :", tri1 == sorted(montants) == tri2)
print("n^2 / 4 =", len(montants) ** 2 // 4, "  |  n log2 n =", round(len(montants) * math.log2(len(montants))))
```
<!--sortie-->
```text
tri par insertion :  41010 comparaisons
tri fusion        :  2972 comparaisons
même résultat que sorted() : True
n^2 / 4 = 40000   |  n log2 n = 3458
```

Le tri par insertion fait de l'ordre de $n^2/4$ comparaisons en moyenne (41 010 ici, soit près de quatorze fois plus que les 2 972 du tri fusion), le tri fusion de l'ordre de $n\log_2 n$. Pour 400 éléments, cela fait la différence entre « bien » et « très bien » ; pour 10 millions, entre quelques secondes et plusieurs jours. Le tri intégré de Python, `sorted`, utilise un algorithme hybride très optimisé (*Timsort*) de coût $n\log n$ : **en pratique, on utilise toujours `sorted()` ou `.sort()`**, mais comprendre ce qu'il fait permet de raisonner sur son coût.

> 💡 **Un tri est dit stable** s'il laisse dans leur ordre d'origine les éléments « égaux » au regard du critère de tri. C'est ce que garantit `sorted` de Python, et cela permet d'enchaîner des tris successifs : trier d'abord par montant, puis par canal, donne les commandes **rangées par canal et, à l'intérieur de chaque canal, par montant croissant**.

```python
commandes = [("Site", 40.1), ("Boutique", 65.8), ("Site", 19.6), ("Boutique", 17.4), ("Instagram", 30.1)]
par_montant = sorted(commandes, key=lambda c: c[1])
par_canal_puis_montant = sorted(par_montant, key=lambda c: c[0])   # stable : conserve l'ordre par montant
for c in par_canal_puis_montant:
    print(c)
```
<!--sortie-->
```text
('Boutique', 17.4)
('Boutique', 65.8)
('Instagram', 30.1)
('Site', 19.6)
('Site', 40.1)
```

### 4.3.7 Une dernière application : les « top k »

Question de Yasmine : « Quelles sont mes **cinq plus grosses commandes** ? » On pourrait trier les 400 montants puis prendre les cinq derniers (coût de l'ordre de $n\log n$). Mais c'est du gaspillage : on n'a pas besoin que *tout* soit trié. Une structure appelée **tas** (*heap*) maintient efficacement les $k$ plus grands vus jusqu'ici, avec un coût de l'ordre de $n\log k$. Le module `heapq` la fournit :

```python
import heapq

top5 = heapq.nlargest(5, montants)
print("5 plus grosses commandes (heapq)  :", top5)
print("5 plus grosses commandes (tri)    :", sorted(montants, reverse=True)[:5])

# top 3 avec leur canal : on classe les lignes selon une clé
top3_lignes = heapq.nlargest(3, lignes, key=lambda l: float(l["montant"]))
for l in top3_lignes:
    print(f"  {l['canal']:<10} {l['montant']:>6} DT   livraison {l['livraison']} j   satisfaction {l['satisfaction']}/5")
```
<!--sortie-->
```text
5 plus grosses commandes (heapq)  : [255.7, 243.8, 217.1, 212.4, 208.8]
5 plus grosses commandes (tri)    : [255.7, 243.8, 217.1, 212.4, 208.8]
  Site        255.7 DT   livraison 4 j   satisfaction 3/5
  Site        243.8 DT   livraison 5 j   satisfaction 3/5
  Site        217.1 DT   livraison 7 j   satisfaction 4/5
```

Les deux listes sont identiques, la version `heapq` coûtant moins cher quand $k\ll n$ (pensez aux *dix* meilleurs clients sur *dix millions*). Ce réflexe, **ne pas faire plus de travail que nécessaire**, est l'une des habitudes les plus rentables de la programmation scientifique.

> 🧪 **Pour aller plus loin.** Les mêmes idées (hachage, tri, recherche dichotomique, arbres) sont au cœur des **bases de données** : l'**index** d'une table SQL (chapitre 5) est précisément un arbre trié qui permet une recherche dichotomique ; les `GROUP BY` s'appuient sur des tables de hachage ou des tris. Comprendre cette section, c'est comprendre pourquoi une requête est rapide ou lente.

> ✅ **À retenir**
> - Un algorithme doit être **précis, terminer, et être correct** ; on le prouve avec un **invariant** (vrai à chaque tour) et un argument de **terminaison** ; on mesure son coût en **nombre d'opérations**.
> - **Liste** : ordre et position ; **dictionnaire / ensemble** : accès et test d'appartenance immédiats (table de hachage) ; **pile** : dernier entré, premier sorti ; **file** : premier entré, premier sorti.
> - La **récursion** exige un cas de base et un problème strictement plus petit ; elle se prouve comme une récurrence. Sans précaution (mémoïsation), elle peut refaire des calculs en nombre exponentiel.
> - La **recherche dichotomique** (liste triée) coûte au plus $\lfloor\log_2 n\rfloor+1$ comparaisons : 9 pour 400 éléments, 20 pour un million.
> - Le **tri par insertion** coûte de l'ordre de $n^2$, le **tri fusion** de l'ordre de $n\log n$ ; en pratique on utilise `sorted()`, qui est stable.
> - Ne trier que ce qui est nécessaire : pour les « top $k$ », `heapq.nlargest` suffit.
