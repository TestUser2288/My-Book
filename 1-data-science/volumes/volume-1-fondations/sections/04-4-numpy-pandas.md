## 4.4 NumPy et pandas : manipuler des données

> 💡 **Intuition.** Python « de base » (section 4.1) sait faire des calculs, mais il est lent et verbeux dès qu'il faut traiter des milliers de nombres. Deux bibliothèques ont changé la donne et sont aujourd'hui **le** socle de la data science en Python :
>
> - **NumPy** ajoute un nouveau type d'objet, le **tableau** (`ndarray`), qui permet de calculer sur *toute une colonne de nombres d'un seul coup*, à vitesse quasi native ;
> - **pandas** pose par-dessus un **tableau étiqueté** (le `DataFrame`) : des colonnes qui ont un nom et un type, des lignes qui ont une étiquette, des dates, des valeurs manquantes… bref, un tableur programmable, sans souris et sans limite de taille.
>
> La gérante a l'habitude d'Excel. Tout ce que nous allons faire ici, elle pourrait le faire à la main dans une feuille de calcul, mais pour 400 lignes ce serait pénible, et pour 400 000 lignes ce serait impossible. Surtout, **le code est rejouable** : on corrige une erreur, on relance, on retrouve toutes les analyses mises à jour.

> 🧭 **Comment lire cette section.** Elle est longue parce que pandas est *l'*outil que vous utiliserez tous les jours. Les trois premières parties (4.4.1 à 4.4.4) concernent NumPy ; la suite concerne pandas. Chaque notion est introduite par un **petit exemple à la main**, puis appliquée aux 400 commandes de la boutique. Si vous êtes pressé(e), lisez au moins 4.4.5 à 4.4.9, puis la conclusion de 4.4.13.

### 4.4.1 NumPy : pourquoi un tableau n'est pas une liste

La gérante veut afficher les prix TTC de cinq articles à partir de leurs prix hors taxe (TVA à 19 %). Avec une **liste** Python classique, on écrit une boucle :

```python
import numpy as np

print([round(p * 1.19, 2) for p in [10, 20, 5, 40, 15]])      # avec une liste : une boucle
```
<!--sortie-->
```text
[11.9, 23.8, 5.95, 47.6, 17.85]
```

À la main : $10\times1{,}19=11{,}90$, $20\times1{,}19=23{,}80$, $5\times 1{,}19 = 5{,}95$, $40\times1{,}19=47{,}60$ et $15\times1{,}19=17{,}85$. Le résultat est celui attendu. Avec un **tableau NumPy**, la boucle disparaît :

```python
ht = np.array([10, 20, 5, 40, 15])
print(ht * 1.19)
print(type(ht), ht.dtype, ht.shape)
```
<!--sortie-->
```text
[11.9  23.8   5.95 47.6  17.85]
<class 'numpy.ndarray'> int64 (5,)
```

Une seule opération `ht * 1.19` s'applique **à chaque élément** : on dit qu'elle est **vectorisée**. Ce n'est pas qu'une commodité d'écriture : les listes Python sont des collections d'objets quelconques (un entier, puis un texte, puis une autre liste…), alors qu'un tableau NumPy est un **bloc de mémoire homogène** (ici des entiers de 64 bits, `dtype=int64`) traité par du code compilé en C. D'où deux différences que tout le monde rencontre un jour :

```python
print([10, 20] * 2)               # liste : * 2 répète la liste
print(np.array([10, 20]) * 2)     # tableau : * 2 multiplie chaque élément
```
<!--sortie-->
```text
[10, 20, 10, 20]
[20 40]
```

> ⚠️ **Piège classique.** Sur une liste, `*` et `+` **répètent** et **concatènent**. Sur un tableau, ils **calculent**. Si vous voyez une liste de 10 000 nombres se mettre à « doubler de longueur » au lieu de doubler de valeur, c'est qu'un tableau a été oublié.

```python hide
import time

x = np.random.default_rng(0).uniform(10, 100, size=1_000_000)
liste = x.tolist()

t0 = time.perf_counter()
ttc_boucle = [v * 1.19 for v in liste]      # une boucle Python
t1 = time.perf_counter()
ttc_numpy = x * 1.19                        # une opération vectorisée
t2 = time.perf_counter()

print("mêmes résultats :", np.array_equal(ttc_boucle, ttc_numpy))
print("NumPy au moins 5 fois plus rapide :", (t1 - t0) / (t2 - t1) > 5)
```
<!--sortie-->
```text
mêmes résultats : True
NumPy au moins 5 fois plus rapide : True
```

Mesurons l'écart de vitesse sur un million de prix : une boucle `[v * 1.19 for v in liste]` contre l'opération vectorisée `x * 1.19`. Les deux donnent exactement les mêmes résultats, et la version NumPy est **au moins 5 fois plus rapide** ; les durées exactes dépendent de votre machine, nous ne retenons donc que cette conclusion robuste. Sur du calcul plus lourd que cette simple multiplication, l'écart se compte en **dizaines, voire centaines de fois**. C'est la raison pour laquelle on cherche toujours à **vectoriser** : écrire `x * 1.19` plutôt qu'une boucle `for`.

> ✅ **À retenir.** Un tableau NumPy = un bloc de nombres **du même type**, sur lequel les opérations s'appliquent **élément par élément** et vite. Règle d'or : *pas de boucle `for` sur des données, sauf si l'on n'a vraiment pas le choix.*

### 4.4.2 Créer, indexer, trancher

Quelques manières courantes de fabriquer des tableaux :

```python
print(np.arange(0, 10, 2))            # de 0 à 10 (exclu), pas de 2
print(np.linspace(0, 1, 5))           # 5 points régulièrement espacés entre 0 et 1
print(np.zeros(3), np.ones(3))        # que des 0, que des 1
```
<!--sortie-->
```text
[0 2 4 6 8]
[0.   0.25 0.5  0.75 1.  ]
[0. 0. 0.] [1. 1. 1.]
```

Un tableau a trois caractéristiques à toujours avoir en tête : sa **forme** (`shape`), son nombre de dimensions (`ndim`) et son type (`dtype`). Prenons les ventes hebdomadaires (en €) des trois canaux de la boutique sur quatre semaines : une **matrice** de 3 lignes (canaux) et 4 colonnes (semaines), exactement comme celles du chapitre 1.

| | Sem. 1 | Sem. 2 | Sem. 3 | Sem. 4 |
|---|---|---|---|---|
| Réseaux | 120 | 150 | 90 | 140 |
| Site | 90 | 100 | 120 | 70 |
| Boutique | 60 | 50 | 90 | 105 |

```python
A = np.array([[120, 150,  90, 140],
              [ 90, 100, 120,  70],
              [ 60,  50,  90, 105]])
print(A.shape, A.ndim, A.dtype, A.size)
```
<!--sortie-->
```text
(3, 4) 2 int64 12
```

**Indexation.** On désigne un élément par `A[ligne, colonne]`, en comptant **à partir de 0** (comme partout en Python). Quelques exemples à vérifier *sur le tableau ci-dessus* avant de regarder la sortie :

- `A[1, 2]` : ligne 1 (le Site), colonne 2 (semaine 3) → **120** ;
- `A[0]` : toute la ligne 0 (Réseaux) ;
- `A[:, 3]` : toute la colonne 3 (semaine 4) ; le « `:` » signifie « tout » ;
- `A[0:2, 1:3]` : lignes 0 et 1, colonnes 1 et 2 (la borne de fin est **exclue**).

```python
print(A[1, 2])
print(A[0])
print(A[:, 3])
print(A[0:2, 1:3])
```
<!--sortie-->
```text
120
[120 150  90 140]
[140  70 105]
[[150  90]
 [100 120]]
```

**Filtrer avec un masque booléen.** Comparer un tableau à un nombre produit un tableau de `True`/`False` de même forme : le **masque**. Utilisé comme indice, il ne garde que les cases `True`.

```python
masque = A > 100
print(A[masque])                 # les ventes strictement supérieures à 100 €
print("combien ?", masque.sum()) # True compte pour 1 : on compte donc les cases vraies
```
<!--sortie-->
```text
[120 150 140 120 105]
combien ? 5
```

Dans le masque, on compte 5 cases vraies : 120, 150 et 140 (Réseaux), 120 (Site, semaine 3) et 105 (Boutique, semaine 4). Notez que le 100 du Site (semaine 2) n'est **pas** compté : la condition est « strictement supérieur à 100 ». La somme d'un masque est une astuce très utile : elle **compte** les `True`.

Pour combiner deux conditions, on utilise `&` (et), `|` (ou) et `~` (non), **avec des parenthèses** :

```python
print(A[(A > 80) & (A < 130)])      # entre 80 et 130 exclus
```
<!--sortie-->
```text
[120  90  90 100 120  90 105]
```

> ⚠️ **Tranche = vue, pas copie.** Tailler un morceau d'un tableau avec `:` ne copie pas les données : la tranche est une **fenêtre** sur le tableau d'origine. Modifier la fenêtre modifie l'original ! Pour obtenir une copie indépendante, écrivez explicitement `.copy()`.

```python
C = A.copy()
fenetre = C[0, :]      # une vue sur la ligne de Réseaux
fenetre[0] = 999
print(C[0, 0], "<- modifié par la vue ;  A[0, 0] =", A[0, 0], "(intact, car C est une copie)")
```
<!--sortie-->
```text
999 <- modifié par la vue ;  A[0, 0] = 120 (intact, car C est une copie)
```

Enfin, un tableau a **un seul type** : si l'on mélange entiers et décimaux, tout devient décimal (`np.array([1, 2, 3.5])` donne `[1. 2. 3.5]`). Et un tableau d'entiers ne sait pas représenter une valeur manquante, ce qui sera une raison de plus d'aimer pandas (4.4.11).


### 4.4.3 Le broadcasting : calculer entre tableaux de formes différentes

Que se passe-t-il si l'on fait `A - m` où $A$ est une matrice $3\times 4$ et $m$ un vecteur de 4 nombres ? Mathématiquement, la soustraction n'est pas définie (les formes diffèrent) ; NumPy, lui, **étire** le plus petit tableau pour qu'il s'adapte : c'est le **broadcasting** (« diffusion »).

Reprenons l'exemple de la gérante. Elle veut savoir, pour chaque semaine, **de combien chaque canal s'écarte de la moyenne de cette semaine**. Moyenne de la semaine 1 : $(120+90+60)/3=90$. Semaine 2 : $(150+100+50)/3=100$. Semaine 3 : $(90+120+90)/3=100$. Semaine 4 : $(140+70+105)/3=105$. Donc $m=(90,\,100,\,100,\,105)$ et, par exemple, Réseaux en semaine 1 s'écarte de $120-90=+30$.

![Le broadcasting : le vecteur m (4 nombres) est « étiré » sur les trois lignes de A, puis la soustraction se fait case par case.](figures/ch04-broadcasting.png)

```python
m = A.mean(axis=0)       # moyenne de chaque colonne (axis=0 : on « écrase » les lignes)
print("moyennes par semaine :", m)
print(A - m)
```
<!--sortie-->
```text
moyennes par semaine : [ 90. 100. 100. 105.]
[[ 30.  50. -10.  35.]
 [  0.   0.  20. -35.]
 [-30. -50. -10.   0.]]
```

Le résultat reproduit les valeurs du dessin : `30` pour Réseaux en semaine 1, `-35` pour le Site en semaine 4, etc.

> 📐 **La règle du broadcasting.** NumPy compare les formes **en partant de la droite**. Deux dimensions sont compatibles si elles sont **égales** ou si l'une des deux vaut **1** (elle est alors étirée). Une dimension manquante à gauche est comptée comme 1.
>
> - $(3,4)$ et $(4,)$ : $4=4$ ✓, puis le 3 n'a pas de vis-à-vis → compatible, résultat $(3,4)$ ;
> - $(3,4)$ et $(3,1)$ : $4$ vs $1$ ✓, $3=3$ ✓ → compatible, résultat $(3,4)$ ;
> - $(3,4)$ et $(3,)$ : $4$ vs $3$ ✗ → **erreur**.

Pour soustraire cette fois la **moyenne de chaque ligne** (la vente moyenne de chaque canal), il faut un vecteur *colonne* de forme $(3,1)$. L'argument `keepdims=True` garde la dimension écrasée avec la taille 1, ce qui rend le broadcasting possible :

```python
moy_canal = A.mean(axis=1, keepdims=True)
print(moy_canal.shape, "->", moy_canal.ravel())
print(A - moy_canal)
```
<!--sortie-->
```text
(3, 1) -> [125.    95.    76.25]
[[ -5.    25.   -35.    15.  ]
 [ -5.     5.    25.   -25.  ]
 [-16.25 -26.25  13.75  28.75]]
```

À la main : la moyenne de Réseaux est $(120+150+90+140)/4=125$, donc la première ligne devient $(-5,\ 25,\ -35,\ 15)$. Et si on oublie `keepdims` ? NumPy refuse et le dit clairement (`operands could not be broadcast together with shapes (3,4) (3,)`), ce qui rappelle la règle.

```python hide
try:
    A - A.mean(axis=1)          # forme (3,) au lieu de (3, 1)
except ValueError as e:
    print("ValueError :", e)
```
<!--sortie-->
```text
ValueError : operands could not be broadcast together with shapes (3,4) (3,) 
```

> 💡 **Standardiser des colonnes.** Au chapitre 1, nous avons vu que les algorithmes de modélisation aiment que les variables aient la même échelle. Centrer-réduire chaque colonne (soustraire sa moyenne, diviser par son écart-type) s'écrit sans boucle grâce au broadcasting : `(X - X.mean(axis=0)) / X.std(axis=0, ddof=1)`. Vous le ferez avec pandas à la section 4.4.7.

### 4.4.4 Agréger, trier, tirer au hasard

Les fonctions de résumé (`sum`, `mean`, `std`, `min`, `max`…) prennent un argument **`axis`** qui choisit la direction du calcul. Une mnémotechnique : *`axis` est la dimension qui disparaît*.

| Appel | Ce qui disparaît | Résultat pour notre $A$ ($3\times4$) |
|---|---|---|
| `A.sum()` | tout | un seul nombre (le chiffre d'affaires total) |
| `A.sum(axis=0)` | les lignes | un total **par semaine** (4 nombres) |
| `A.sum(axis=1)` | les colonnes | un total **par canal** (3 nombres) |

```python
print("total général  :", A.sum())
print("par semaine    :", A.sum(axis=0))
print("par canal      :", A.sum(axis=1))
```
<!--sortie-->
```text
total général  : 1185
par semaine    : [270 300 300 315]
par canal      : [500 380 305]
```

Vérification à la main : Réseaux $120+150+90+140=500$, Site $90+100+120+70=380$, Boutique $60+50+90+105=305$, soit $1\,185$ € au total, ce qui est aussi la somme des totaux par semaine ($270+300+300+315$).

Autres opérations fréquentes : `np.cumsum` (somme cumulée), `np.diff` (différences successives), `np.sort` et `np.argsort` (le tri, et l'ordre qui trierait).


> ⚠️ **`ddof` encore.** Comme pour `np.std` à la section 3.1.4, NumPy divise par $n$ par défaut. Pour estimer la variance d'une population à partir d'un échantillon, il faut **`ddof=1`** (division par $n-1$). pandas, lui, utilise $n-1$ par défaut : un écart entre `np.std(x)` et `serie.std()` n'est donc pas un bug.

**Nombres aléatoires.** On rencontre le générateur de nombres aléatoires depuis le chapitre 2 : on le crée une fois avec une **graine** (*seed*), puis on tire.

```python hide
rng = np.random.default_rng(42)
jours = rng.normal(loc=120, scale=15, size=100_000)    # 100 000 journées simulées, N(120 ; 15²)
print("moyenne simulée :", round(jours.mean(), 1))
print("part des jours à plus de 150 ventes :", round((jours > 150).mean(), 4))
```
<!--sortie-->
```text
moyenne simulée : 119.9
part des jours à plus de 150 ventes : 0.0233
```

Avec 100 000 journées simulées (`rng.normal(120, 15, size=100_000)`), la moyenne simulée est 119,9 et la part des jours à plus de 150 ventes est 0,0233. La moyenne d'un masque booléen est la **proportion** de `True` : c'est la façon la plus économique d'estimer une probabilité par simulation. On retrouve (à très peu près) les 2,3 % calculés à la main au 2.2 pour un jour à plus de deux écarts-types au-dessus de la moyenne.

Enfin, NumPy sait faire l'algèbre linéaire du chapitre 1 : produit matriciel `@`, transposée `.T`, inverse, valeurs propres, résolution de système, etc.

```python
M = np.array([[2.0, 1.0], [1.0, 3.0]])
b = np.array([5.0, 10.0])
print("solution de M x = b :", np.linalg.solve(M, b))
```
<!--sortie-->
```text
solution de M x = b : [1. 3.]
```

À la main : $2x+y=5$ et $x+3y=10$ donnent $x=1$, $y=3$. (`np.linalg` sait aussi inverser, calculer des valeurs propres, etc. : voir le chapitre 1.)

> ✅ **À retenir (NumPy).** (1) tableau = type unique + forme ; (2) indexer avec `[ligne, colonne]`, tranches `a:b` (fin exclue) et masques booléens ; (3) le **broadcasting** étire les dimensions de taille 1 ; (4) `axis` = la dimension qui disparaît ; (5) une tranche est une **vue** : `.copy()` pour travailler sans risque.

### 4.4.5 pandas : Series et DataFrame

NumPy ne connaît que des nombres rangés dans des cases numérotées. Mais une vraie table de données, ce sont des colonnes **nommées** (« montant », « canal ») de **types différents** (nombres, texte, dates), avec des lignes qu'on veut pouvoir **identifier**. C'est ce que fait pandas.

Deux objets suffisent pour commencer :

- la **Series** : une colonne, c'est-à-dire un tableau NumPy muni d'un **index** (une étiquette par valeur) et d'un nom ;
- le **DataFrame** : un tableau de plusieurs Series partageant le même index.

```python hide
import numpy as np
import pandas as pd

pd.set_option("display.width", 110)          # pour que les tableaux larges ne soient pas coupés à l'affichage
pd.set_option("display.max_columns", 20)
```

```python
import pandas as pd

ventes = pd.Series([500, 380, 305], index=["Réseaux", "Site", "Boutique"], name="ventes")
print(ventes)
print("par étiquette :", ventes["Site"], "| par position :", ventes.iloc[2])
```
<!--sortie-->
```text
Réseaux     500
Site        380
Boutique    305
Name: ventes, dtype: int64
par étiquette : 380 | par position : 305
```

Un `DataFrame` s'obtient, par exemple, à partir d'un dictionnaire « nom de colonne → valeurs » :

```python
mini = pd.DataFrame({"canal": ["Réseaux", "Site", "Boutique"], "ventes": [500, 380, 305],
                     "ouvert_le_dimanche": [True, True, False]})
print(mini.dtypes)
```
<!--sortie-->
```text
canal                   str
ventes                int64
ouvert_le_dimanche     bool
dtype: object
```

Chaque colonne a **son** type : `str` (texte), `int64` (entiers), `bool` (vrai/faux).

> 🧪 **pandas 3.0 : le texte a désormais son propre type.** Dans les versions de pandas antérieures à la 3.0, les colonnes de texte avaient le type `object` (« n'importe quoi »). Depuis la **version 3.0**, elles ont un type dédié, affiché `str`, plus rapide, plus économe en mémoire, et qui représente les valeurs manquantes de façon uniforme. Si vous lisez un vieux tutoriel qui affiche `dtype: object` pour une colonne de texte, ne vous inquiétez pas : seul l'affichage a changé. Ce livre a été exécuté avec pandas 3.0.

**Charger le fichier de données.** Voici le fichier `donnees/commandes.csv` du chapitre 3 :

```python
df = pd.read_csv("donnees/commandes.csv")
print(df.shape)
print(df.head(3))
```
<!--sortie-->
```text
(400, 4)
      canal  montant  livraison  satisfaction
0  Boutique     44.8          0             4
1      Site     34.5          2             4
2   Réseaux     88.2          5             4
```

```python hide
df.info()
```
<!--sortie-->
```text
<class 'pandas.DataFrame'>
RangeIndex: 400 entries, 0 to 399
Data columns (total 4 columns):
 #   Column        Non-Null Count  Dtype  
---  ------        --------------  -----  
 0   canal         400 non-null    str    
 1   montant       400 non-null    float64
 2   livraison     400 non-null    int64  
 3   satisfaction  400 non-null    int64  
dtypes: float64(1), int64(2), str(1)
memory usage: 12.6 KB
```

`info()` est le meilleur premier réflexe : nombre de lignes, nom et type de chaque colonne, nombre de valeurs **non nulles** (ici, 400 partout : aucune valeur manquante) et mémoire utilisée.

Le fichier ne contient pas de **date**, or la plupart des vraies données de vente en ont une. Pour illustrer le travail sur les dates (4.4.12) et sur plusieurs tables (4.4.10), nous allons **ajouter deux colonnes simulées** : la date de chaque commande (réparties sur 20 semaines à partir du lundi 5 janvier 2026) et un numéro de client (120 clients possibles). La simulation est reproductible grâce à la graine (le code est donné dans la préparation du cahier, chapitre 4) ; la colonne `date` a le type `datetime64`, et `id_commande` numérote les commandes par ordre chronologique :

```python hide
rng = np.random.default_rng(7)
jours = rng.integers(0, 140, size=len(df))            # un jour tiré parmi 140 (= 20 semaines)
df["date"] = pd.Timestamp("2026-01-05") + pd.to_timedelta(jours, unit="D")
df["id_client"] = rng.integers(1, 121, size=len(df))   # clients numérotés de 1 à 120
df = df.sort_values("date").reset_index(drop=True)     # on trie par date et on renumérote les lignes
df.insert(0, "id_commande", np.arange(1, len(df) + 1)) # une colonne identifiant, placée en premier
print(df.head(6))
print()
print(df.dtypes)
```
<!--sortie-->
```text
   id_commande     canal  montant  livraison  satisfaction       date  id_client
0            1      Site     49.9          8             2 2026-01-05        100
1            2   Réseaux     21.5          3             4 2026-01-05         46
2            3  Boutique     34.2          0             4 2026-01-05         26
3            4      Site    103.0          3             5 2026-01-05         97
4            5   Réseaux     26.7          4             4 2026-01-06        105
5            6  Boutique     37.4          0             4 2026-01-06        120

id_commande              int64
canal                      str
montant                float64
livraison                int64
satisfaction             int64
date            datetime64[us]
id_client                int64
dtype: object
```

```python
print(df.head(4))
```
<!--sortie-->
```text
   id_commande     canal  montant  livraison  satisfaction       date  id_client
0            1      Site     49.9          8             2 2026-01-05        100
1            2   Réseaux     21.5          3             4 2026-01-05         46
2            3  Boutique     34.2          0             4 2026-01-05         26
3            4      Site    103.0          3             5 2026-01-05         97
```

Notez que pandas sait que `date` n'est pas du texte, mais de vraies dates, avec lesquelles on peut calculer. Dernier réflexe, le résumé statistique (ici, pour le montant) :

```python
print(df["montant"].describe().round(2))
```
<!--sortie-->
```text
count    400.00
mean      60.25
std       38.02
min        8.60
25%       34.18
50%       51.00
75%       75.82
max      255.70
Name: montant, dtype: float64
```

### 4.4.6 Sélectionner : colonnes, lignes, conditions

Pour sélectionner, on dispose de plusieurs outils, résumés dans le tableau ci-dessous. Prenons une toute petite table pour voir clairement ce qui se passe :

```python
petit = df[["id_commande", "canal", "montant"]].head(5)
print(petit)
```
<!--sortie-->
```text
   id_commande     canal  montant
0            1      Site     49.9
1            2   Réseaux     21.5
2            3  Boutique     34.2
3            4      Site    103.0
4            5   Réseaux     26.7
```

| Je veux… | J'écris | Remarque |
|---|---|---|
| une colonne | `petit["montant"]` | donne une Series |
| plusieurs colonnes | `petit[["canal", "montant"]]` | **doubles crochets** : une liste de noms |
| des lignes **par position** | `petit.iloc[1:3]` | `iloc` = *integer location* ; fin **exclue** |
| des lignes **par étiquette** | `petit.loc[1:3]` | `loc` = *label* ; fin **incluse** ! |
| des lignes par condition | `petit[petit["montant"] > 50]` | masque booléen, comme en NumPy |

```python
print(petit[["canal", "montant"]].iloc[1:3])      # par position : fin exclue
print(petit.loc[1:3, ["canal", "montant"]])      # par étiquette : fin INCLUSE
```
<!--sortie-->
```text
      canal  montant
1   Réseaux     21.5
2  Boutique     34.2
      canal  montant
1   Réseaux     21.5
2  Boutique     34.2
3      Site    103.0
```

> ⚠️ **`iloc` exclut la fin, `loc` l'inclut.** `iloc[1:3]` renvoie les lignes 1 et 2 ; `loc[1:3]` renvoie les lignes 1, 2 **et 3** (car on désigne des étiquettes, et on veut « de 1 jusqu'à 3 »). C'est l'une des étourderies les plus fréquentes.

**Filtrer avec des conditions.** Les opérateurs `&`, `|`, `~` demandent **des parenthèses** autour de chaque condition (car `&` s'évalue avant `>`) :

```python
gros_reseaux = df[(df["canal"] == "Réseaux") & (df["montant"] > 100)]
print("commandes Réseaux de plus de 100 € :", len(gros_reseaux))
print(df.query("canal == 'Site' and livraison >= 7").shape[0])     # la même idée, écrite comme une phrase
```
<!--sortie-->
```text
commandes Réseaux de plus de 100 € : 11
21
```

La méthode `query` accepte une condition écrite comme une phrase : elle se lit mieux sur des conditions longues. Deux autres formes pratiques : `isin([...])` (appartient à une liste) et `between(a, b)` (bornes incluses). Pour **trier** et chercher les extrêmes, on a `sort_values` ; `nsmallest(3, "montant")` donne directement les trois plus petits :

```python
print(df.sort_values("montant", ascending=False).head(3)[["id_commande", "canal", "montant"]])
```
<!--sortie-->
```text
     id_commande canal  montant
380          381  Site    255.7
102          103  Site    243.8
198          199  Site    217.1
```

### 4.4.7 Créer et transformer des colonnes

Une nouvelle colonne s'obtient en l'assignant, avec des opérations **vectorisées** (comme dans NumPy, sans boucle) :

```python
df["livraison_rapide"] = df["livraison"] <= 3
df["gros_panier"] = np.where(df["montant"] >= 100, "oui", "non")
print(df[["canal", "montant", "gros_panier", "livraison_rapide"]].head(3))
```
<!--sortie-->
```text
      canal  montant gros_panier  livraison_rapide
0      Site     49.9         non             False
1   Réseaux     21.5         non              True
2  Boutique     34.2         non              True
```

Pour le texte, le préfixe `.str` donne accès à toutes les méthodes de Python (`upper`, `lower`, `contains`, `replace`, `split`…) appliquées à **chaque élément** de la colonne : par exemple `df["canal"].str.upper()`.

**Découper une variable continue en classes.** `pd.cut` fabrique des classes de bornes choisies, `pd.qcut` des classes d'effectifs égaux (par quantiles). Par exemple, quatre tranches de panier : « petit » (moins de 30 €), « moyen » (30 à 60), « grand » (60 à 100) et « très grand » (plus de 100) :

```python
noms = ["petit", "moyen", "grand", "très grand"]
df["tranche"] = pd.cut(df["montant"], bins=[0, 30, 60, 100, np.inf], labels=noms)
print(df["tranche"].value_counts().reindex(noms))
```
<!--sortie-->
```text
tranche
petit          76
moyen         160
grand         112
très grand     52
Name: count, dtype: int64
```

```python hide
quartiles = pd.qcut(df["montant"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
print(quartiles.value_counts().sort_index())     # 100 commandes dans chaque quartile par construction
```
<!--sortie-->
```text
montant
Q1    100
Q2    100
Q3    100
Q4    100
Name: count, dtype: int64
```

Remarquez la nuance : avec `cut`, les classes sont **définies par vous** et leurs effectifs sont inégaux ; avec `qcut`, ce sont les effectifs qui sont **égaux** (400 / 4 = 100) et les bornes qui s'adaptent aux données.

**Remplacer des valeurs selon un dictionnaire** se fait avec `map` : `df["satisfaction"].map({1: "très mécontent", 2: "mécontent", 3: "neutre", 4: "content", 5: "très content"})` remplace chaque note par son libellé (195 commandes sont « content » et 104 « très content »).

**Standardiser** (centrer-réduire), comme annoncé à la fin de 4.4.3, se fait sur une colonne entière :

```python hide
z = (df["montant"] - df["montant"].mean()) / df["montant"].std()
print("moyenne de z nulle :", bool(np.isclose(z.mean(), 0)), "| écart-type de z :", round(z.std(), 6))
print("commandes à plus de 3 écarts-types de la moyenne :", int((z.abs() > 3).sum()))
```
<!--sortie-->
```text
moyenne de z nulle : True | écart-type de z : 1.0
commandes à plus de 3 écarts-types de la moyenne : 7
```

Par construction, $z$ a une moyenne nulle et un écart-type de 1. Sept commandes dépassent 3 écarts-types. Si les montants suivaient une loi normale, on n'en attendrait qu'**une seule** sur 400 environ (la probabilité d'être à plus de 3 écarts-types est de 0,27 %, d'après les repères du 2.2). En trouver sept confirme ce que nous avions vu au 3.1.5 : la distribution des montants a une **queue lourde à droite**.

> 💡 **`apply` : à garder en dernier recours.** Si une transformation n'existe pas en version vectorisée, `df["col"].apply(ma_fonction)` appelle votre fonction **ligne par ligne** : pratique, mais lent (une boucle Python déguisée). Réflexe : chercher d'abord une opération vectorisée (`.str`, `np.where`, `cut`, `map`, opérateurs arithmétiques…). Sur nos 400 lignes la différence est invisible ; en répétant les montants 500 fois (200 000 lignes), `apply` donne le même résultat que la version vectorisée `np.where(gros > 50, gros * 1.19, gros)` mais s'avère **plus lent**.

```python hide
import time

gros = pd.concat([df["montant"]] * 500, ignore_index=True)      # 200 000 montants

t0 = time.perf_counter()
a = gros.apply(lambda v: v * 1.19 if v > 50 else v)               # une boucle Python déguisée
t1 = time.perf_counter()
b = np.where(gros > 50, gros * 1.19, gros)                         # vectorisé
t2 = time.perf_counter()
print("même résultat :", np.allclose(a, b))
print("apply plus lent que la version vectorisée :", (t1 - t0) > (t2 - t1))
```
<!--sortie-->
```text
même résultat : True
apply plus lent que la version vectorisée : True
```

### 4.4.8 Copie, vue et pièges de pandas 3.0

Une question revient sans cesse : *si je modifie un morceau de mon tableau, est-ce que je modifie aussi l'original ?* Dans les versions anciennes de pandas, la réponse dépendait de détails obscurs (c'était le fameux `SettingWithCopyWarning`). **Depuis pandas 3.0, la règle est simple : le *copy-on-write* (copie à l'écriture).** Tout objet dérivé d'un autre se comporte comme **une copie indépendante** ; modifier l'un ne modifie jamais l'autre.

```python
montants = df["montant"]               # une Series dérivée de df
montants.iloc[0] = -1                  # on la modifie…
print("df['montant'] au premier rang :", df["montant"].iloc[0], "(inchangé)")
```
<!--sortie-->
```text
df['montant'] au premier rang : 49.9 (inchangé)
```

La conséquence la plus importante : l'**assignation en chaîne** (`df[condition]["colonne"] = valeur`) **ne fonctionne plus**, car `df[condition]` fabrique une copie temporaire que l'on modifie puis que l'on jette. pandas 3.0 émet même un avertissement (`ChainedAssignmentError`). Vérifions-le :

```python
copie = df.copy()
copie[copie["canal"] == "Site"]["montant"] = 0           # ✗ assignation en chaîne : sans effet
copie.loc[copie["canal"] == "Site", "montant"] = 0       # ✓ la bonne écriture
print(int((copie["montant"] == 0).sum()), "montants mis à zéro")
```
<!--sortie-->
```text
148 montants mis à zéro
```

```python hide
import warnings

copie = df.copy()
with warnings.catch_warnings(record=True) as avert:
    warnings.simplefilter("always")
    copie[copie["canal"] == "Site"]["montant"] = 0        # ✗ assignation en chaîne
print("avertissement reçu :", avert[0].category.__name__)
print("montants mis à 0 par la mauvaise écriture :", int((copie["montant"] == 0).sum()))

copie.loc[copie["canal"] == "Site", "montant"] = 0        # ✓ une seule opération avec loc
print("montants mis à 0 par la bonne écriture   :", int((copie["montant"] == 0).sum()))
```
<!--sortie-->
```text
avertissement reçu : ChainedAssignmentError
montants mis à 0 par la mauvaise écriture : 0
montants mis à 0 par la bonne écriture   : 148
```

Avec la mauvaise écriture, **aucun** montant n'est modifié (0) ; avec la bonne, 148 le sont : les 148 commandes du Site.

> ✅ **La bonne écriture, toujours : `df.loc[condition, "colonne"] = valeur`.** Une seule opération, qui désigne à la fois les lignes et la colonne. Et pour *vraiment* garder une copie intacte avant de modifier : `df2 = df.copy()`.

### 4.4.9 Regrouper : le « split-apply-combine » (`groupby`)

C'est l'outil le plus important de pandas pour répondre à des questions du type : *« quel est le montant moyen **par canal** ? », « combien de commandes **par semaine** ? »* La méthode s'appelle **découper – appliquer – combiner** (*split-apply-combine*) :

1. **découper** le tableau en groupes (une valeur de canal = un groupe) ;
2. **appliquer** un calcul à chaque groupe (moyenne, somme, comptage…) ;
3. **combiner** les résultats dans un nouveau tableau.

Faisons-le **à la main** sur six commandes :

| Commande | Canal | Montant |
|---|---|---|
| 1 | Réseaux | 20 |
| 2 | Site | 30 |
| 3 | Réseaux | 40 |
| 4 | Site | 50 |
| 5 | Boutique | 100 |
| 6 | Site | 70 |

Groupes : Réseaux $\{20,40\}$, Site $\{30,50,70\}$, Boutique $\{100\}$. Moyennes : $30$, $50$ et $100$. Comptes : $2$, $3$, $1$. Voici le même calcul en code (pandas range les groupes par ordre alphabétique) :

```python
six = pd.DataFrame({"canal": ["Réseaux", "Site", "Réseaux", "Site", "Boutique", "Site"],
                    "montant": [20, 30, 40, 50, 100, 70]})
print(six.groupby("canal")["montant"].agg(["mean", "count"]))
```
<!--sortie-->
```text
           mean  count
canal                 
Boutique  100.0      1
Réseaux    30.0      2
Site       50.0      3
```

Passons aux 400 commandes. L'**agrégation nommée** donne des colonnes lisibles : `nom=("colonne", "fonction")`.

```python
resume = df.groupby("canal").agg(
    commandes=("montant", "count"),
    ca=("montant", "sum"),
    panier_moyen=("montant", "mean"),
).round(2)
print(resume)
```
<!--sortie-->
```text
          commandes      ca  panier_moyen
canal                                    
Boutique        114  8528.3         74.81
Réseaux         138  6763.5         49.01
Site            148  8806.5         59.50
```

On peut regrouper selon **plusieurs** critères (`df.groupby(["canal", "gros_panier"]).size().unstack()` donne un tableau canal × panier) ou demander une répartition en proportions :

```python
print(pd.crosstab(df["canal"], df["tranche"], normalize="index").round(2))   # proportions par ligne
```
<!--sortie-->
```text
tranche   petit  moyen  grand  très grand
canal                                    
Boutique   0.07   0.37   0.32        0.24
Réseaux    0.32   0.38   0.22        0.08
Site       0.16   0.44   0.30        0.09
```

`crosstab` (tableau croisé) est un raccourci pour compter les effectifs de deux variables qualitatives ; avec `normalize="index"` chaque ligne est ramenée à 1, ce qui répond à « *parmi* les commandes Réseaux, quelle part de petits paniers ? ». Pour des tableaux de synthèse à deux entrées sur une variable numérique, on a `pivot_table` :

```python
print(df.pivot_table(index="canal", columns="gros_panier", values="satisfaction", aggfunc="mean").round(2))
```
<!--sortie-->
```text
gros_panier   non   oui
canal                  
Boutique     4.49  4.48
Réseaux      3.72  3.64
Site         3.80  3.71
```

Enfin `transform` calcule un résultat **par groupe** mais le renvoie **aligné sur les lignes d'origine**, ce qui permet de comparer chaque commande à son groupe :

```python
df["ecart_moy_canal"] = df["montant"] - df.groupby("canal")["montant"].transform("mean")
print(df[["canal", "montant", "ecart_moy_canal"]].head(3).round(1))
```
<!--sortie-->
```text
      canal  montant  ecart_moy_canal
0      Site     49.9             -9.6
1   Réseaux     21.5            -27.5
2  Boutique     34.2            -40.6
```

```python hide
print("moyenne des écarts nulle dans chaque canal :", bool(np.allclose(df.groupby("canal")["ecart_moy_canal"].mean(), 0)))
```
<!--sortie-->
```text
moyenne des écarts nulle dans chaque canal : True
```

> ✅ **À retenir (`groupby`).** `df.groupby(clé)[colonne].fonction()` : *découper, appliquer, combiner*. `agg` pour plusieurs résumés, `size` pour compter les lignes, `transform` pour ré-aligner un résultat de groupe sur chaque ligne, `pivot_table` et `crosstab` pour des tableaux croisés.

### 4.4.10 Combiner plusieurs tables : `merge` et `concat`

Dans la vraie vie, l'information est **répartie sur plusieurs tables** : la liste des commandes d'un côté, celle des clients de l'autre (nous verrons au chapitre 5 pourquoi, et comment SQL fait la même chose avec `JOIN`). Le travail s'appelle une **jointure** : on associe les lignes qui partagent la même **clé**.

Créons la table des clients : 125 clients, chacun avec une ville. (Les clients 121 à 125 n'ont, par construction, jamais commandé ; comme les commandes ont été attribuées au hasard à des clients de 1 à 120, quelques autres clients n'auront rien commandé non plus. Cela nous servira.)

```python hide
rng_c = np.random.default_rng(11)
clients = pd.DataFrame({
    "id_client": np.arange(1, 126),
    "ville": rng_c.choice(["Ville H", "Ville F", "Ville G", "Ville E", "Ville B"], size=125, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
})

```

```python
print(clients.head(3))
print("clients :", len(clients), "| commandes :", len(df))
```
<!--sortie-->
```text
   id_client    ville
0          1  Ville H
1          2  Ville F
2          3  Ville G
clients : 125 | commandes : 400
```

Voici d'abord un exemple minuscule pour comprendre les types de jointure. Deux commandes (clients 1 et 9) et deux fiches clients (1 et 2) :

```python
cmd = pd.DataFrame({"id_client": [1, 9], "montant": [50, 80]})
fiche = pd.DataFrame({"id_client": [1, 2], "ville": ["Ville H", "Ville F"]})
print(cmd.merge(fiche, on="id_client", how="left"))
```
<!--sortie-->
```text
   id_client  montant    ville
0          1       50  Ville H
1          9       80      NaN
```

```python hide
for how in ["inner", "outer"]:
    print(f"--- how='{how}'")
    print(cmd.merge(fiche, on="id_client", how=how))
```
<!--sortie-->
```text
--- how='inner'
   id_client  montant    ville
0          1       50  Ville H
--- how='outer'
   id_client  montant    ville
0          1     50.0  Ville H
1          2      NaN  Ville F
2          9     80.0      NaN
```

(Avec `how="inner"`, on n'obtiendrait que la ligne du client 1 ; avec `how="outer"`, trois lignes : les clients 1, 2 et 9.)

- **`inner`** : seulement les clés présentes **des deux côtés** (client 1) ;
- **`left`** : toutes les lignes de la table de gauche ; on met `NaN` (valeur manquante) quand il n'y a pas de correspondance (client 9 sans fiche) ;
- **`outer`** : tout ce qui existe d'un côté **ou** de l'autre.

> 💡 **Quel `how` choisir ?** Dans 90 % des cas : `left`, avec votre table « principale » (les commandes) à gauche. On garde alors *toutes* les commandes et on y ajoute des informations, sans en perdre en route. Et on **vérifie** toujours le nombre de lignes avant/après.

Sur nos données :

```python
cmd_ville = df.merge(clients, on="id_client", how="left")
print("lignes avant/après la jointure :", len(df), len(cmd_ville))      # aucune ligne perdue ni dupliquée
print(cmd_ville.groupby("ville")["montant"].agg(["count", "mean"]).round(1))
```
<!--sortie-->
```text
lignes avant/après la jointure : 400 400
         count  mean
ville               
Ville B     19  65.5
Ville E     42  56.0
Ville F     71  63.6
Ville G     92  59.7
Ville H    176  59.6
```

Quels sont les clients qui n'ont **jamais** commandé ? `indicator=True` ajoute une colonne `_merge` qui dit d'où vient chaque ligne (`both` : présent des deux côtés ; `left_only` : seulement dans la table de gauche) :

```python
test = clients.merge(df[["id_client"]].drop_duplicates(), on="id_client", how="left", indicator=True)
print(test["_merge"].value_counts())
```
<!--sortie-->
```text
_merge
both          114
left_only      11
right_only      0
Name: count, dtype: int64
```

```python hide
print("sans commande :", test.loc[test["_merge"] == "left_only", "id_client"].tolist())
```
<!--sortie-->
```text
sans commande : [1, 6, 43, 50, 67, 84, 121, 122, 123, 124, 125]
```

Onze clients n'ont jamais commandé : les cinq prévus (121 à 125) et six clients de la plage 1 à 120 que le hasard n'a pas tirés (1, 6, 43, 50, 67 et 84). Le comptage `both` (114) + `left_only` (11) retombe bien sur nos 125 clients.

> ⚠️ **Le piège n°1 des jointures : l'explosion du nombre de lignes.** Si la clé est **dupliquée** dans la table de droite, chaque ligne de gauche est recopiée autant de fois. Imaginez que la fiche du client 1 ait été saisie deux fois : sa commande apparaîtrait en double, et le chiffre d'affaires serait faux sans qu'aucune erreur ne soit signalée. Le paramètre **`validate`** déclenche une erreur dans ce cas : `"m:1"` signifie « plusieurs lignes à gauche pour une seule à droite ».

```python
fiche_doublon = pd.DataFrame({"id_client": [1, 1], "ville": ["Ville H", "Ville H"]})
print("sans validate :", len(cmd.merge(fiche_doublon, on="id_client", how="left")), "lignes au lieu de 2")
try:
    cmd.merge(fiche_doublon, on="id_client", how="left", validate="m:1")
except Exception as e:
    print(type(e).__name__, ":", str(e).split("\n")[0])
```
<!--sortie-->
```text
sans validate : 3 lignes au lieu de 2
MergeError : Merge keys are not unique in right dataset; not a many-to-one merge
```

Pour **empiler** des tables de même structure (les commandes de janvier et celles de février, par exemple), on utilise `pd.concat([janvier, fevrier])` : 75 + 69 lignes donnent bien 144.

```python hide
janvier = df[df["date"] < "2026-02-01"]
fevrier = df[(df["date"] >= "2026-02-01") & (df["date"] < "2026-03-01")]
empile = pd.concat([janvier, fevrier])
print(len(janvier), "+", len(fevrier), "=", len(empile))
```
<!--sortie-->
```text
75 + 69 = 144
```

### 4.4.11 Valeurs manquantes

Dans les données réelles, il manque toujours quelque chose : un client n'a pas laissé de note, un capteur est tombé en panne, une case n'a pas été remplie. pandas représente ces trous par **`NaN`** (*not a number*) pour les nombres, et par `NaT` pour les dates. Créons (code non reproduit) une copie de nos données où 30 notes de satisfaction, tirées au hasard, sont perdues : 7 chez Boutique, 10 chez Réseaux, 13 chez Site.

```python hide
rng_m = np.random.default_rng(3)
trous = rng_m.choice(len(df), size=30, replace=False)
dfm = df[["id_commande", "canal", "montant", "satisfaction"]].copy()
dfm["satisfaction"] = dfm["satisfaction"].astype(float)      # float, car un entier NumPy ne peut pas contenir NaN
dfm.loc[trous, "satisfaction"] = np.nan
print(dfm["satisfaction"].isna().sum(), "notes manquantes sur", len(dfm))
print(dfm["satisfaction"].isna().groupby(dfm["canal"]).sum())
```
<!--sortie-->
```text
30 notes manquantes sur 400
canal
Boutique     7
Réseaux     10
Site        13
Name: satisfaction, dtype: int64
```

D'abord, **comment les calculs se comportent-ils ?** Sur un exemple à la main : les notes `4, 5, NaN, 3` ont pour moyenne $(4+5+3)/3=4$ (pandas **ignore** le `NaN`, il ne le compte pas comme 0 ; sinon on trouverait $12/4=3$).

```python
notes = pd.Series([4, 5, np.nan, 3])
print("moyenne :", notes.mean(), "| somme avec skipna=False :", notes.sum(skipna=False))
```
<!--sortie-->
```text
moyenne : 4.0 | somme avec skipna=False : nan
```

> ⚠️ **Piège.** Comparer avec `==` ne détecte pas un `NaN` (`NaN == NaN` est faux, par convention). Utilisez **`isna()`** / `notna()`.

Que faire des trous ? Trois stratégies, à choisir selon le contexte : supprimer les lignes incomplètes (`dropna`), remplacer par une valeur « raisonnable » comme la médiane (`fillna`), ou remplacer par la médiane **du groupe** (`fillna` avec `groupby(...).transform("median")`). Voici les deux premières :

```python
supprimee = dfm.dropna(subset=["satisfaction"])                        # 1. supprimer les lignes incomplètes
remplie = dfm["satisfaction"].fillna(dfm["satisfaction"].median())     # 2. remplacer par la médiane
print(len(supprimee), "lignes conservées ; moyenne après remplissage :", round(remplie.mean(), 3))
```
<!--sortie-->
```text
370 lignes conservées ; moyenne après remplissage : 3.985
```

```python hide
a_supprimer = dfm.dropna(subset=["satisfaction"])                       # 1. supprimer les lignes incomplètes
remplie_med = dfm["satisfaction"].fillna(dfm["satisfaction"].median())  # 2. remplacer par une valeur « raisonnable »
remplie_canal = dfm["satisfaction"].fillna(                             # 3. remplacer par la médiane du groupe
    dfm.groupby("canal")["satisfaction"].transform("median"))

print("lignes après dropna :", len(a_supprimer))
print("moyenne exacte (données complètes) :", round(df["satisfaction"].mean(), 3))
print("moyenne avec trous (ignorés)       :", round(dfm["satisfaction"].mean(), 3))
print("moyenne après remplissage (médiane):", round(remplie_med.mean(), 3))
print("moyenne après remplissage (par canal):", round(remplie_canal.mean(), 3))
```
<!--sortie-->
```text
lignes après dropna : 370
moyenne exacte (données complètes) : 3.965
moyenne avec trous (ignorés)       : 3.984
moyenne après remplissage (médiane): 3.985
moyenne après remplissage (par canal): 4.003
```

Lisons les résultats. La vraie moyenne (calculée avant de perdre les 30 notes) est **3,965**. En ignorant simplement les trous, on trouve 3,984 ; avec un remplissage par la médiane globale, 3,985 ; avec la médiane de chaque canal, 4,003. Les écarts sont **petits** parce que nous avons effacé les notes **au hasard** (30 tirées au sort). Si les notes manquantes avaient été celles des clients mécontents, toutes les méthodes auraient surestimé la satisfaction, et d'autant plus que les trous seraient nombreux.

> 💡 **Ce qu'il faut comprendre.** Il n'y a pas de bonne réponse universelle. Supprimer des lignes est simple mais perd de l'information, et **biaise** les résultats si les données manquantes ne sont pas dues au hasard (par exemple, si les clients mécontents répondent moins souvent). Remplir par la moyenne ou la médiane garde les effectifs mais **écrase la variabilité** (tous les trous prennent la même valeur). Retenez surtout un réflexe : **toujours compter les manquants (`isna().sum()`) avant d'analyser**, et se demander *pourquoi* ils manquent. Les méthodes d'imputation plus fines viendront dans la suite de la série.

Enfin, pandas propose des types **à valeurs manquantes natives** (`Int64` avec un grand « I ») qui permettent de garder des entiers malgré les trous :

```python
print(pd.Series([1, 2, None]).dtype, "|", pd.Series([1, 2, None], dtype="Int64").dtype)
```
<!--sortie-->
```text
float64 | Int64
```

### 4.4.12 Travailler avec des dates

Avec une colonne de vrais **dates** (type `datetime64`), pandas offre un accès `.dt` aux composantes (année, mois, jour de la semaine…), de l'arithmétique et des regroupements par période.

```python
df["jour_semaine"] = df["date"].dt.dayofweek          # 0 = lundi … 6 = dimanche
df["mois"] = df["date"].dt.month
print(df[["date", "jour_semaine", "mois"]].head(3))
```
<!--sortie-->
```text
        date  jour_semaine  mois
0 2026-01-05             0     1
1 2026-01-05             0     1
2 2026-01-05             0     1
```

```python hide
print(df["date"].min(), "->", df["date"].max())
print("durée couverte :", df["date"].max() - df["date"].min())
```
<!--sortie-->
```text
2026-01-05 00:00:00 -> 2026-05-24 00:00:00
durée couverte : 139 days 00:00:00
```

Si vos dates sont lues comme du **texte** (cas fréquent à l'import d'un fichier), on les convertit avec `pd.to_datetime`, en précisant le format pour éviter l'ambiguïté jour/mois :

```python
dates = pd.to_datetime(pd.Series(["05/01/2026", "12/01/2026", "03/02/2026"]), format="%d/%m/%Y")
print(dates.dt.month.tolist(), "<- 3 février = mois 2, comme attendu")
```
<!--sortie-->
```text
[1, 1, 2] <- 3 février = mois 2, comme attendu
```

Pour **regrouper par semaine**, on convertit chaque date en période hebdomadaire (du lundi au dimanche) et on prend son premier jour :

```python
df["semaine"] = df["date"].dt.to_period("W").dt.start_time      # le lundi de la semaine de chaque commande
print(df[["date", "semaine"]].head(3))
```
<!--sortie-->
```text
        date    semaine
0 2026-01-05 2026-01-05
1 2026-01-05 2026-01-05
2 2026-01-05 2026-01-05
```

```python hide
print("nombre de semaines distinctes :", df["semaine"].nunique())
```
<!--sortie-->
```text
nombre de semaines distinctes : 20
```

> 🧪 **Vérifions sur un exemple.** Le 5 janvier 2026 est un lundi : la semaine du 5 au 11 janvier est donc repérée par le **5 janvier**. Une commande du jeudi 8 janvier doit avoir pour semaine le 5 janvier ; une commande du lundi 12 janvier, le 12. Le programme le confirme : le lundi 5, le jeudi 8 et le dimanche 11 tombent tous dans la semaine du 5 ; le lundi 12 ouvre celle du 12.

```python hide
test = pd.Series(pd.to_datetime(["2026-01-05", "2026-01-08", "2026-01-11", "2026-01-12"]))
print(pd.DataFrame({"date": test, "jour": test.dt.day_name(), "semaine": test.dt.to_period("W").dt.start_time}))
```
<!--sortie-->
```text
        date      jour    semaine
0 2026-01-05    Monday 2026-01-05
1 2026-01-08  Thursday 2026-01-05
2 2026-01-11    Sunday 2026-01-05
3 2026-01-12    Monday 2026-01-12
```

Dernier outil, la **moyenne mobile** (*rolling*), qui lisse une série en moyennant les $k$ dernières valeurs. À la main : pour les ventes `10, 20, 30, 40`, la moyenne mobile sur 2 périodes vaut `NaN, 15, 25, 35` (la première valeur n'a pas assez d'historique).

```python
print(pd.Series([10, 20, 30, 40]).rolling(2).mean().tolist())
```
<!--sortie-->
```text
[nan, 15.0, 25.0, 35.0]
```

### 4.4.13 Du tableau au rapport

Tout ce qui précède se combine naturellement. En regroupant les commandes par semaine (`groupby("semaine")`), on obtient un **tableau de bord hebdomadaire** : une ligne par semaine, avec le nombre de commandes, le chiffre d'affaires, le panier moyen, la part du canal Réseaux et une **moyenne mobile** sur quatre semaines qui lisse les à-coups. Une petite fonction qui rédige, pour une semaine donnée, le rapport que la gérante lit chaque lundi (chiffre d'affaires, variation par rapport à la semaine précédente, répartition par canal, meilleurs clients, satisfaction) n'est alors qu'un assemblage de filtres, de `groupby` et de formatage. Cette fonction est **réutilisable** : la semaine suivante, on change la date et on obtient le nouveau rapport sans rien refaire. C'est ce qui sépare une analyse « à la souris » d'une analyse reproductible. Vous la construirez pas à pas dans l'application 4.5 du cahier.

> ✅ **À retenir (pandas).**
>
> 1. `read_csv` → `head()`, `info()`, `describe()` : toujours **regarder** avant de calculer ;
> 2. sélection : `df["col"]`, `df[["a","b"]]`, `loc` (étiquettes, fin incluse), `iloc` (positions, fin exclue), masques avec `&`, `|`, `~` **et parenthèses** ;
> 3. écrire **`df.loc[condition, "col"] = valeur`**, jamais d'assignation en chaîne (copy-on-write de pandas 3.0) ;
> 4. `groupby(...).agg(...)` : découper, appliquer, combiner ;
> 5. `merge(..., how="left", validate="m:1")` : toujours vérifier le nombre de lignes avant/après ;
> 6. compter les manquants avec `isna().sum()` *avant* de choisir quoi en faire ;
> 7. des dates en type `datetime64` (`to_datetime`), puis `.dt`, `to_period`, `rolling`.
>
> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (le rapport hebdomadaire) ; exercices 4.9 à 4.11 (NumPy et broadcasting, `groupby` et dates, jointure et clients dormants).
