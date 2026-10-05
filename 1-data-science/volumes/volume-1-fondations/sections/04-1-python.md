## 4.1 Les fondamentaux de Python

> 💡 **Intuition.** Un programme est une **recette de cuisine** écrite pour un exécutant très docile mais totalement dépourvu de bon sens : il fait *exactement* ce que vous écrivez, à une vitesse folle, sans jamais se fatiguer, et sans jamais deviner ce que vous vouliez dire. Apprendre à programmer, c'est apprendre à écrire des recettes sans ambiguïté. Python est un excellent choix pour cela : ses recettes se lisent presque comme des phrases.

Dans cette section, nous partons de zéro et nous terminons par un **programme complet** : la caisse de la boutique de Yasmine. Chaque notion suit le même rythme que dans le reste du livre : une image, un exemple fait à la main, puis le code et sa sortie réelle.

> 🧭 **Section à lire dans l'ordre.** Si vous programmez déjà, lisez seulement les titres et les encadrés ⚠️, puis passez au programme final (4.1.10) pour vérifier que tout vous semble familier.

### 4.1.1 Pourquoi Python, et comment l'exécuter

Python est gratuit, lisible, et il dispose de milliers de bibliothèques pour les données (NumPy, pandas, SciPy, matplotlib…, que nous rencontrerons en 4.4 et 4.5). C'est le langage le plus utilisé en data science, et c'est celui des exemples de ce livre.

Il y a trois façons d'exécuter du code Python :

1. **Interactivement**, en tapant `python` dans un terminal : on écrit une ligne, on voit le résultat tout de suite. Idéal pour essayer.
2. **Dans un fichier** `mon_programme.py`, lancé avec `python mon_programme.py`. Idéal pour garder et rejouer son travail.
3. **Dans un notebook Jupyter** (section 6.2) : des cellules de code mélangées à du texte. Idéal pour explorer et raconter.

Le tout premier programme du monde informatique :

```python
print("Bonjour Dar Jasmin !")
print(2 + 3 * 4)
```
<!--sortie-->
```text
Bonjour Dar Jasmin !
14
```

La fonction `print` affiche ce qu'on lui donne. La deuxième ligne montre que Python respecte la priorité habituelle des opérations : $3\times 4$ d'abord, puis $+2$, soit 14.

> 💡 **Les commentaires.** Tout ce qui suit un `#` sur une ligne est ignoré par Python : c'est une note pour le lecteur humain (vous, dans six mois). Un bon commentaire explique **pourquoi**, pas **quoi**.

### 4.1.2 Variables et types

Une **variable** est une étiquette collée sur une valeur. L'instruction `prix = 12.5` se lit : « colle l'étiquette `prix` sur la valeur 12,5 ». Ce n'est **pas** une égalité mathématique : à droite on calcule, à gauche on nomme.

Les quatre types de base :

| Type | Nom Python | Exemple | À quoi ça sert |
|---|---|---|---|
| Entier | `int` | `3` | compter (articles, jours) |
| Décimal | `float` | `12.5` | mesurer (prix, poids) ; **séparateur : le point** |
| Texte | `str` | `"bol"` | noms, étiquettes |
| Booléen | `bool` | `True`, `False` | vrai ou faux |

**Exemple à la main.** Yasmine vend 3 bols à 12,5 DT hors taxe. Le total HT est $3\times12{,}5=37{,}5$ DT. Avec 19 % de TVA : $37{,}5\times1{,}19=44{,}625$ DT, soit 44,63 DT si l'on arrondit « comme à l'école » (la moitié vers le haut). Faisons-le faire à Python :

```python
quantite = 3
prix_ht = 12.5
total_ht = quantite * prix_ht
total_ttc = total_ht * 1.19

print("total HT  :", total_ht)
print("total TTC :", total_ttc)
print("arrondi   :", round(total_ttc, 2))
print(type(quantite), type(prix_ht), type("bol"), type(True))
```
<!--sortie-->
```text
total HT  : 37.5
total TTC : 44.625
arrondi   : 44.62
<class 'int'> <class 'float'> <class 'str'> <class 'bool'>
```

Les totaux correspondent au calcul à la main, **sauf l'arrondi** : Python affiche `44.62` et non 44,63. La raison : 44,625 tombe pile à mi-chemin entre 44,62 et 44,63, et `round` arrondit ces cas vers le chiffre **pair** (« arrondi du banquier »), d'où 44,62. Dans d'autres cas, c'est l'approximation binaire des décimaux (1.5.1) qui fait pencher l'arrondi d'un côté ou de l'autre. Pour des centimes exacts, on utilise le module `decimal` ; pour un ticket de caisse, on peut aussi calculer en **millimes** (entiers). Gardez cet écart en tête : il illustre qu'un résultat de programme se **vérifie** toujours contre un calcul indépendant. Notez enfin que `type(...)` révèle le type d'une valeur : une commande que vous utiliserez souvent pour comprendre une erreur.

Les opérateurs arithmétiques sont `+ - * /` et trois autres moins connus :

| Opérateur | Sens | Exemple | Résultat |
|---|---|---|---|
| `**` | puissance | `2 ** 10` | 1024 |
| `//` | division entière | `17 // 5` | 3 |
| `%` | reste (modulo) | `17 % 5` | 2 |

```python
print(2 ** 10)
print(17 // 5, 17 % 5)      # 17 = 3*5 + 2
print(17 / 5)               # la division « / » donne toujours un float
print(7 % 2 == 0)           # un nombre est pair si son reste modulo 2 vaut 0
```
<!--sortie-->
```text
1024
3 2
3.4
False
```

> ⚠️ **Les décimaux sont approchés.** Python (comme tous les langages) stocke les `float` en binaire, ce qui explique les petites surprises du type $0{,}1+0{,}2\neq0{,}3$ expliquées en 1.5.1. Conséquence pratique : on **n'écrit jamais** `a == b` pour comparer deux décimaux calculés, on utilise `math.isclose(a, b)`. Et pour des montants d'argent, on arrondit explicitement avec `round(x, 2)` à l'affichage.

### 4.1.3 Le texte et les f-strings

Un texte (`str`) s'écrit entre guillemets. On peut le découper, le mettre en majuscules, le chercher :

```python
nom = "  Bol en céramique bleue "
print(nom.strip())               # enlève les espaces au début et à la fin
print(nom.strip().upper())
print(nom.strip().replace("bleue", "verte"))
print(len(nom.strip()))          # nombre de caractères
print("céramique" in nom)        # True si le morceau est présent
print(nom.strip().split(" "))    # découpe en liste de mots
```
<!--sortie-->
```text
Bol en céramique bleue
BOL EN CÉRAMIQUE BLEUE
Bol en céramique verte
22
True
['Bol', 'en', 'céramique', 'bleue']
```

Pour **insérer des valeurs dans une phrase**, la méthode moderne est la **f-string** : on fait précéder le guillemet d'un `f` et on met les valeurs entre accolades. Après les deux-points, on peut régler le format.

```python
produit, quantite, prix = "bol", 3, 12.5
print(f"{quantite} x {produit} à {prix} DT")
print(f"total : {quantite * prix:.2f} DT")      # .2f : 2 décimales
print(f"part de TVA : {0.19:.0%}")              # .0% : pourcentage
print(f"{'produit':<10}|{'prix':>8}")           # < aligne à gauche, > à droite
print(f"{produit:<10}|{prix:>8.2f}")
```
<!--sortie-->
```text
3 x bol à 12.5 DT
total : 37.50 DT
part de TVA : 19%
produit   |    prix
bol       |   12.50
```

Les f-strings sont la base de tous les rapports et tickets de caisse que vous écrirez.

### 4.1.4 Les collections : listes, tuples, dictionnaires, ensembles

Une variable ne contient pas forcément une seule valeur. Python offre quatre « boîtes » pour en regrouper plusieurs. On les étudie plus en détail à la section 4.3 (algorithmes et structures de données) ; voici l'essentiel.

| Collection | Notation | Ordonnée ? | Modifiable ? | Doublons ? | Cas typique |
|---|---|---|---|---|---|
| **liste** | `[1, 2, 3]` | oui | oui | oui | une suite de montants |
| **tuple** | `(1, 2, 3)` | oui | non | oui | un couple (code, quantité) |
| **dictionnaire** | `{"bol": 12.5}` | par insertion | oui | clés uniques | un catalogue : nom → prix |
| **ensemble** | `{1, 2, 3}` | non | oui | non | les clients distincts |

**Les listes.** Les positions (**indices**) commencent à **0**. Un indice négatif compte depuis la fin. Le **découpage** `liste[a:b]` prend de l'indice `a` inclus à `b` **exclu**.

```python
montants = [44.8, 34.5, 88.2, 30.1, 110.1]
print(montants[0], montants[-1])     # premier et dernier
print(montants[1:4])                  # indices 1, 2, 3
montants.append(39.8)                 # ajoute à la fin
print(len(montants), sum(montants), max(montants), min(montants))
print(sorted(montants))               # copie triée ; la liste d'origine ne change pas
print(f"moyenne = {sum(montants) / len(montants):.2f}")
```
<!--sortie-->
```text
44.8 110.1
[34.5, 88.2, 30.1]
6 347.5 110.1 30.1
[30.1, 34.5, 39.8, 44.8, 88.2, 110.1]
moyenne = 57.92
```

> ⚠️ **Piège classique du débutant : le décalage de 1.** Dans une liste de 6 éléments, les indices vont de 0 à **5** ; `montants[6]` provoque une erreur. Et `montants[1:4]` contient **3** éléments (1, 2, 3), pas 4. Règle : la longueur d'un découpage est `b - a`.

**Les tuples** sont des listes figées : une fois créés on ne les modifie plus. Parfaits pour des paires qui ne doivent pas bouger, comme (code produit, quantité).

**Les dictionnaires** associent une **clé** à une **valeur**, comme un annuaire : on cherche par le nom, pas par la position.

```python
catalogue = {"bol": 12.5, "tasse": 8.0, "plateau": 45.0}
print(catalogue["tasse"])
catalogue["bougie"] = 15.9            # ajout
catalogue["bol"] = 13.0               # modification
print(catalogue)
print(catalogue.get("lampe", "inconnu"))   # .get évite l'erreur si la clé n'existe pas
for nom, prix in catalogue.items():
    print(f"  {nom:<8} {prix:>6.2f} DT")
```
<!--sortie-->
```text
8.0
{'bol': 13.0, 'tasse': 8.0, 'plateau': 45.0, 'bougie': 15.9}
inconnu
  bol       13.00 DT
  tasse      8.00 DT
  plateau   45.00 DT
  bougie    15.90 DT
```

**Les ensembles** oublient l'ordre et éliminent les doublons : exactement ce qu'il faut pour compter des clients **distincts**.

```python
acheteurs = ["Sana", "Mehdi", "Sana", "Ines", "Mehdi", "Sana"]
distincts = set(acheteurs)
print(len(acheteurs), "achats par", len(distincts), "clients distincts")
print(sorted(distincts))              # trié pour un affichage stable
```
<!--sortie-->
```text
6 achats par 3 clients distincts
['Ines', 'Mehdi', 'Sana']
```

L'ordre d'affichage d'un ensemble peut changer d'une exécution à l'autre : n'y comptez jamais (c'est pourquoi nous l'avons passé par `sorted` pour l'afficher).

### 4.1.5 Décider : conditions

Un programme doit pouvoir **choisir**. L'instruction `if` exécute un bloc seulement si la condition est vraie. En Python, **l'indentation** (4 espaces) délimite le bloc : c'est la grammaire du langage, pas un détail de présentation.

Comparaisons : `==` (égal), `!=` (différent), `<`, `<=`, `>`, `>=`. Combinaisons : `and`, `or`, `not`.

**Exemple à la main.** Règle de livraison de Dar Jasmin : *gratuite à partir de 100 DT, sinon 7 DT ; et pour un retrait en boutique, toujours 0.* Pour un panier de 80 DT livré : 7 DT. Pour 120 DT livré : 0. Pour 80 DT en retrait : 0.

```python
def frais_livraison(total, retrait_boutique):
    if retrait_boutique:
        return 0
    elif total >= 100:
        return 0
    else:
        return 7

print(frais_livraison(80, False), frais_livraison(120, False), frais_livraison(80, True))
```
<!--sortie-->
```text
7 0 0
```

Les trois cas retombent sur les valeurs trouvées à la main. (Nous n'avons pas encore parlé des **fonctions** : le mot `def` en 4.1.7 va tout expliquer.)

> ⚠️ **`=` et `==`.** Un seul signe égal **colle** une étiquette ; deux signes égaux **testent** l'égalité. Python refuse d'ailleurs `if x = 3`, ce qui vous évite un grand classique des autres langages.

### 4.1.6 Répéter : boucles

Une **boucle** répète un bloc. Deux formes :

- `for élément in collection:` : une fois pour chaque élément (on sait combien).
- `while condition:` : tant que la condition est vraie (on ne sait pas combien).

**Exemple à la main.** Yasmine place 1 000 DT à 5 % par an, intérêts composés. Au bout d'un an : $1000\times1{,}05=1050$. Deux ans : $1050\times1{,}05=1102{,}5$. Combien d'années pour **doubler** ? C'est une question « jusqu'à ce que » : une boucle `while`.

```python
capital, annees = 1000.0, 0
while capital < 2000:
    capital = capital * 1.05
    annees += 1                       # raccourci pour annees = annees + 1
    print(f"année {annees:2d} : {capital:8.2f} DT")
print("doublé en", annees, "ans")
```
<!--sortie-->
```text
année  1 :  1050.00 DT
année  2 :  1102.50 DT
année  3 :  1157.62 DT
année  4 :  1215.51 DT
année  5 :  1276.28 DT
année  6 :  1340.10 DT
année  7 :  1407.10 DT
année  8 :  1477.46 DT
année  9 :  1551.33 DT
année 10 :  1628.89 DT
année 11 :  1710.34 DT
année 12 :  1795.86 DT
année 13 :  1885.65 DT
année 14 :  1979.93 DT
année 15 :  2078.93 DT
doublé en 15 ans
```

Vérification mathématique : on cherche le plus petit $n$ tel que $1{,}05^n\ge2$, soit $n\ge\ln 2/\ln1{,}05$.

```python
import math
print(round(math.log(2) / math.log(1.05), 2))
```
<!--sortie-->
```text
14.21
```

Le résultat réel est entre 14 et 15 : il faut donc 15 années entières, ce que la boucle a trouvé.

> ⚠️ **La boucle infinie.** Si, dans un `while`, la condition ne devient jamais fausse (ici, si on oubliait la ligne `capital = ...`), le programme tourne éternellement. Dans un terminal, `Ctrl+C` l'arrête. Avant de lancer un `while`, demandez-vous : *qu'est-ce qui le fera s'arrêter ?* (La même question sera posée avec rigueur pour les algorithmes en 4.3.)

La boucle `for` parcourt n'importe quelle collection ; `range(n)` produit les entiers de 0 à $n-1$, et `enumerate` donne en plus la position :

```python
for i in range(3):
    print("i =", i)
for rang, nom in enumerate(["Sana", "Mehdi", "Ines"], start=1):
    print(rang, nom)
```
<!--sortie-->
```text
i = 0
i = 1
i = 2
1 Sana
2 Mehdi
3 Ines
```

**Les compréhensions de liste** sont une écriture compacte d'une boucle qui construit une liste : `[expression for x in collection if condition]`. Elles se lisent comme une phrase mathématique « l'ensemble des $f(x)$ pour $x$ dans… tel que… ».

```python
montants = [44.8, 34.5, 88.2, 30.1, 110.1, 39.8, 74.7]
ttc = [round(m * 1.19, 2) for m in montants]
gros = [m for m in montants if m > 60]
print(ttc)
print(gros)
carres = {n: n ** 2 for n in range(1, 6)}      # même idée pour un dictionnaire
print(carres)
```
<!--sortie-->
```text
[53.31, 41.05, 104.96, 35.82, 131.02, 47.36, 88.89]
[88.2, 110.1, 74.7]
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

### 4.1.7 Fonctions : écrire ses propres outils

Une **fonction** est une recette nommée qu'on peut réutiliser. Elle reçoit des **paramètres**, fait un calcul, et **renvoie** un résultat avec `return`. Sans fonctions, un programme devient vite un long ruban illisible ; avec elles, on le découpe en briques que l'on teste séparément.

Mathématiquement, c'est la même idée que $f(x)=1{,}19\,x$ : on la définit une fois, on l'utilise partout.

```python
def ttc(prix_ht, taux_tva=0.19):
    """Renvoie le prix TTC arrondi au centime."""
    return round(prix_ht * (1 + taux_tva), 2)

print(ttc(100))             # utilise la TVA par défaut : 19 %
print(ttc(100, 0.07))       # TVA à 7 % : on remplace la valeur par défaut
print(ttc(prix_ht=50))      # appel par nom : plus lisible
```
<!--sortie-->
```text
119.0
107.0
59.5
```

Trois choses à retenir : (1) la ligne entre triples guillemets, la **docstring**, documente la fonction ; (2) `taux_tva=0.19` est un paramètre **par défaut** ; (3) une fonction peut renvoyer **plusieurs** valeurs, sous forme de tuple.

```python
def resume(valeurs):
    """Renvoie (minimum, moyenne, maximum)."""
    return min(valeurs), sum(valeurs) / len(valeurs), max(valeurs)

mini, moy, maxi = resume([44.8, 34.5, 88.2, 30.1, 110.1])
print(f"min = {mini}, moyenne = {moy:.2f}, max = {maxi}")
```
<!--sortie-->
```text
min = 30.1, moyenne = 61.54, max = 110.1
```

> 💡 **La portée.** Les variables créées *dans* une fonction n'existent que dans la fonction (on dit qu'elles sont **locales**). Cela évite les mélanges : deux fonctions peuvent utiliser chacune une variable `total` sans se gêner.

> ⚠️ **Piège : le paramètre par défaut modifiable.** N'écrivez jamais `def f(x, liste=[])` : cette liste est créée **une seule fois** et partagée par tous les appels. Écrivez `liste=None` puis `if liste is None: liste = []`.

Les fonctions peuvent aussi être **passées** à d'autres fonctions, ce qui donne des écritures très concises. Exemple : trier des commandes selon un critère choisi avec l'argument `key`.

```python
commandes = [("Sana", 44.8), ("Mehdi", 110.1), ("Ines", 30.1)]
print(sorted(commandes, key=lambda c: c[1]))                 # du plus petit au plus gros montant
print(sorted(commandes, key=lambda c: c[1], reverse=True)[0]) # la plus grosse
```
<!--sortie-->
```text
[('Ines', 30.1), ('Sana', 44.8), ('Mehdi', 110.1)]
('Mehdi', 110.1)
```

`lambda c: c[1]` est une mini-fonction sans nom qui renvoie le second élément du couple.

### 4.1.8 Les erreurs : vos meilleures amies

Quand quelque chose ne va pas, Python s'arrête et affiche un **message d'erreur** (*traceback*). Il se lit **de bas en haut** : la dernière ligne dit *quel type d'erreur* et *pourquoi* ; les lignes au-dessus disent *où*. Voici les erreurs que vous rencontrerez le plus souvent, provoquées volontairement et rattrapées avec `try / except` pour pouvoir les afficher :

```python
def tenter(description, fonction):
    try:
        fonction()
    except Exception as e:
        print(f"{description:<26} -> {type(e).__name__}: {e}")

montants = [44.8, 34.5, 88.2]
tenter("indice hors liste", lambda: montants[5])
tenter("clé absente", lambda: {"bol": 12.5}["lampe"])
tenter("division par zéro", lambda: 10 / 0)
tenter("texte + nombre", lambda: "total : " + 12.5)
tenter("texte vers entier", lambda: int("douze"))
tenter("nom inconnu", lambda: variable_inexistante)
```
<!--sortie-->
```text
indice hors liste          -> IndexError: list index out of range
clé absente                -> KeyError: 'lampe'
division par zéro          -> ZeroDivisionError: division by zero
texte + nombre             -> TypeError: can only concatenate str (not "float") to str
texte vers entier          -> ValueError: invalid literal for int() with base 10: 'douze'
nom inconnu                -> NameError: name 'variable_inexistante' is not defined
```

Lecture :

- `IndexError` : vous demandez un indice qui n'existe pas (rappelez-vous le décalage de 1).
- `KeyError` : la clé n'est pas dans le dictionnaire (pensez à `.get`).
- `ZeroDivisionError` : on ne divise pas par zéro, ni en Python ni ailleurs.
- `TypeError` : on a mélangé des types incompatibles (texte et nombre).
- `ValueError` : le bon type, mais une valeur impossible à convertir.
- `NameError` : le nom n'existe pas (faute de frappe ? variable pas encore créée ?).

**Attraper une erreur à bon escient.** Quand on lit des données saisies par des humains, certaines valeurs sont inexploitables. On préfère alors **prévoir** l'erreur plutôt que de planter :

```python
saisies = ["12.5", "8", "abc", "", "15,9", "45.0"]
valides, rejetees = [], []
for s in saisies:
    try:
        valides.append(float(s))
    except ValueError:
        rejetees.append(s)
print("valides :", valides)
print("rejetées :", rejetees)
```
<!--sortie-->
```text
valides : [12.5, 8.0, 45.0]
rejetées : ['abc', '', '15,9']
```

Remarquez que `"15,9"` (virgule française) est rejeté : Python attend le **point** décimal. C'est une cause fréquente de données « cassées » quand elles viennent d'un tableur configuré en français.

> 🛠️ **Méthode pour déboguer** (à épingler au-dessus de votre écran). (1) Lisez la **dernière ligne** du message. (2) Repérez la ligne de code citée. (3) Affichez avec `print` les valeurs et les types utilisés à cet endroit. (4) Réduisez le problème au plus petit exemple qui échoue. (5) Seulement ensuite, cherchez le message sur Internet. Neuf fois sur dix, les étapes 1 à 3 suffisent.

### 4.1.9 Modules, fichiers et données réelles

Python ne contient pas tout, mais il sait **importer** du code déjà écrit. Un **module** est un fichier de fonctions ; la bibliothèque standard en fournit des dizaines (`math`, `random`, `statistics`, `csv`, `datetime`…), et on en installe d'autres avec `pip` (section 6.3).

```python
import math
import statistics
from collections import Counter

print(math.sqrt(144), math.pi)
print(statistics.mean([2, 4, 4, 4, 5, 5, 7, 9]), statistics.pstdev([2, 4, 4, 4, 5, 5, 7, 9]))
print(Counter("abracadabra"))     # compte les occurrences
```
<!--sortie-->
```text
12.0 3.141592653589793
5 2.0
Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
```

Lisons maintenant le fichier de données du livre, `donnees/commandes.csv`, **sans aucune bibliothèque externe**, avec le module `csv`. Un fichier CSV est du texte brut : une ligne par commande, des valeurs séparées par des virgules, la première ligne contenant les noms des colonnes.

```python
import csv
from collections import Counter

with open("donnees/commandes.csv", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))     # chaque ligne devient un dictionnaire

print("nombre de commandes :", len(lignes))
print("première commande   :", lignes[0])
print("type du montant     :", type(lignes[0]["montant"]))
```
<!--sortie-->
```text
nombre de commandes : 400
première commande   : {'canal': 'Boutique', 'montant': '44.8', 'livraison': '0', 'satisfaction': '4'}
type du montant     : <class 'str'>
```

Le mot-clé `with` ouvre le fichier **et le referme proprement** à la sortie du bloc, même en cas d'erreur. Remarquez que les valeurs sont lues comme du **texte** : `"44.8"` n'est pas un nombre ! Il faut convertir.

```python
montants = [float(l["montant"]) for l in lignes]
canaux = Counter(l["canal"] for l in lignes)
print("montant moyen :", round(sum(montants) / len(montants), 2))
print("répartition   :", dict(canaux))

# montant moyen par canal, avec un dictionnaire de listes
par_canal = {}
for l in lignes:
    par_canal.setdefault(l["canal"], []).append(float(l["montant"]))
for canal, valeurs in par_canal.items():
    print(f"  {canal:<10} n = {len(valeurs):3d}   moyenne = {sum(valeurs) / len(valeurs):6.2f} DT")
```
<!--sortie-->
```text
montant moyen : 60.25
répartition   : {'Boutique': 114, 'Site': 148, 'Instagram': 138}
  Boutique   n = 114   moyenne =  74.81 DT
  Site       n = 148   moyenne =  59.50 DT
  Instagram  n = 138   moyenne =  49.01 DT
```

On retrouve le montant moyen de 60,25 DT calculé au chapitre 3. Nous avons tout fait à la main, avec des boucles et des dictionnaires : c'est précisément le travail que pandas fera en **une ligne** à la section 4.4. Savoir le faire « à la main » vous permet de comprendre ce que pandas fait pour vous.

### 4.1.10 Un programme complet : la caisse de la boutique

Rassemblons tout. Yasmine veut un petit programme qui, pour un panier, **édite un ticket de caisse** avec les règles suivantes :

- les prix du catalogue sont **hors taxe** ;
- une **remise fidélité de 10 %** s'applique si le sous-total HT dépasse 100 DT ;
- la **TVA de 19 %** s'applique sur le montant après remise ;
- le ticket affiche chaque ligne, le sous-total, la remise, la TVA et le total TTC.

**Calcul à la main** pour le panier « 2 bols, 1 plateau, 3 bougies » (prix HT : bol 12,5 ; plateau 45 ; bougie 15,9) :

- bols : $2\times12{,}5=25{,}00$ ; plateau : $45{,}00$ ; bougies : $3\times15{,}9=47{,}70$ ;
- sous-total HT : $25+45+47{,}7=117{,}70$ DT ;
- le sous-total dépasse 100 DT, donc remise de $10\%$ : $11{,}77$ DT, soit $105{,}93$ DT après remise ;
- TVA : $105{,}93\times0{,}19=20{,}1267\approx20{,}13$ DT ;
- total TTC : $105{,}93+20{,}13=126{,}06$ DT.

Le programme, découpé en petites fonctions faciles à tester :

```python
CATALOGUE = {"bol": 12.5, "tasse": 8.0, "plateau": 45.0, "bougie": 15.9}
TVA = 0.19
SEUIL_REMISE = 100
TAUX_REMISE = 0.10


def sous_total(panier):
    """panier : liste de couples (nom du produit, quantité)."""
    return sum(CATALOGUE[nom] * qte for nom, qte in panier)


def remise(montant_ht):
    return montant_ht * TAUX_REMISE if montant_ht > SEUIL_REMISE else 0.0


def ticket(panier):
    ht = sous_total(panier)
    r = remise(ht)
    net = ht - r
    tva = net * TVA
    lignes = ["=== DAR JASMIN ==="]
    for nom, qte in panier:
        lignes.append(f"{qte} x {nom:<8} {CATALOGUE[nom]:>6.2f}  {qte * CATALOGUE[nom]:>8.2f}")
    lignes.append(f"{'Sous-total HT':<20}{ht:>8.2f}")
    lignes.append(f"{'Remise fidélité':<20}{-r:>8.2f}")
    lignes.append(f"{'TVA 19 %':<20}{tva:>8.2f}")
    lignes.append(f"{'TOTAL TTC':<20}{net + tva:>8.2f}")
    return "\n".join(lignes), round(net + tva, 2)


texte, total = ticket([("bol", 2), ("plateau", 1), ("bougie", 3)])
print(texte)
```
<!--sortie-->
```text
=== DAR JASMIN ===
2 x bol       12.50     25.00
1 x plateau   45.00     45.00
3 x bougie    15.90     47.70
Sous-total HT         117.70
Remise fidélité       -11.77
TVA 19 %               20.13
TOTAL TTC             126.06
```

Le ticket affiche 117,70 DT de sous-total, 11,77 de remise, 20,13 de TVA et 126,06 DT au total : **exactement** nos valeurs à la main. Testons aussi les cas limites avec `assert`, une instruction qui ne dit rien quand la condition est vraie et **arrête** le programme avec une erreur quand elle est fausse :

```python
# Cas 1 : petit panier, pas de remise. 2 tasses = 16,00 HT ; TVA = 3,04 ; TTC = 19,04
assert ticket([("tasse", 2)])[1] == 19.04
# Cas 2 : panier vide
assert ticket([])[1] == 0.0
# Cas 3 : juste au seuil (100 DT pile) : la remise ne s'applique PAS (condition « > »)
assert remise(100) == 0.0
# Cas 4 : le panier précédent
assert ticket([("bol", 2), ("plateau", 1), ("bougie", 3)])[1] == 126.06
print("tous les tests passent")
```
<!--sortie-->
```text
tous les tests passent
```

> 🛠️ **Ce qu'on vient de faire, c'est de la rigueur.** Calculer à la main *avant* de coder fournit un « oracle » : si le programme et la main divergent, l'un des deux a tort, et on cherche lequel. Les `assert` transforment cette vérification en filet de sécurité automatique. Nous irons plus loin avec de vrais tests unitaires en 4.6.

> 🧪 **Pour aller plus loin, essayez de modifier le programme.** Que se passe-t-il si on demande un produit absent du catalogue ? (Réponse : une `KeyError`, comme en 4.1.8.) Comment afficher un message gentil plutôt qu'un plantage ? Comment ajouter un code promo ? Ces trois questions sont des exercices de la section 4.9.

> ✅ **À retenir**
> - Une **variable** est une étiquette sur une valeur ; les types de base sont `int`, `float`, `str`, `bool`.
> - Les décimaux sont approchés : on les arrondit à l'affichage et on ne les compare pas avec `==`.
> - **Listes** (ordonnées, modifiables), **tuples** (figés), **dictionnaires** (clé → valeur), **ensembles** (sans doublons). Les indices commencent à **0**.
> - `if/elif/else` pour décider, `for` et `while` pour répéter ; l'**indentation** délimite les blocs.
> - Une **fonction** (`def`, `return`) est une brique réutilisable ; on la documente (docstring) et on la teste.
> - Un message d'erreur se lit **par la dernière ligne** ; `try/except` permet de prévoir les erreurs attendues.
> - Les fichiers CSV sont du texte : il faut convertir les nombres avant de calculer.
> - Méthode d'or : **calculer à la main un petit cas, puis vérifier que le programme donne la même chose**.
