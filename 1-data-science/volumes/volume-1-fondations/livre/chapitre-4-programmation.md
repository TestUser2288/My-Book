# Chapitre 4 : Programmation

> « Les mathématiques vous disent **quoi** calculer.
> La programmation vous permet de le calculer sur **un million de lignes**. »

Jusqu'ici, nous avons utilisé du code comme un outil de vérification. Ce chapitre prend le code **au sérieux** : c'est lui qui transforme vos idées en résultats reproductibles. Pas besoin d'avoir jamais programmé : on part de zéro. Si vous programmez déjà, parcourez les premières sections en diagonale et attardez-vous sur NumPy, pandas et les visualisations.

## Le chemin de ce chapitre

- **4.1 Python** : le langage de ce livre, des variables aux fonctions, avec un petit programme complet (la caisse de la boutique).
- **4.2 R** : l'autre grand langage de la statistique ; on refait les mêmes analyses pour comparer.
- **4.3 Algorithmes et structures de données** : piles, files, dictionnaires, récursion, tris, recherche. Penser comme un informaticien.
- **4.4 NumPy et pandas** : les deux bibliothèques qui font de Python un outil d'analyse de données.
- **4.5 Visualisations** : choisir le bon graphique, le tracer proprement, avec matplotlib, pandas, seaborn et ggplot2.
- ➕ **Pour aller plus loin** : programmation orientée objet, code propre et tests (4.6) ; d'autres langages (4.7) ; complexité algorithmique (4.8).
- **4.9 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** *Tapez* le code vous-même plutôt que de le copier : c'est la seule façon d'apprendre à programmer. Modifiez-le, cassez-le, observez les messages d'erreur. Ils sont vos amis : un message d'erreur lu attentivement dit presque toujours où est le problème. Pour exécuter du code Python, vous pouvez utiliser un notebook Jupyter (section 6.2) ou simplement un terminal avec la commande `python`.

> 📦 **Le fichier de données.** Au chapitre 3, nous avons construit un tableau de 400 commandes. Il a été enregistré dans le fichier `donnees/commandes.csv`, fourni avec le livre (c'est la sortie de `df.to_csv("donnees/commandes.csv", index=False)` appliqué au tableau du 3.1.2). Nous l'utiliserons pour les sections 4.2, 4.4 et 4.5, ainsi qu'au chapitre 5 (SQL).


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


## 4.2 Les fondamentaux de R

> 💡 **Intuition.** Si Python est un couteau suisse qui sait tout faire, **R est le scalpel du statisticien** : il a été conçu dès l'origine (années 1990, par des statisticiens) pour manipuler des tableaux de données, calculer des statistiques et tracer des graphiques. Les tests, les modèles et les méthodes de recherche récentes y arrivent souvent *en premier*. Dans l'industrie comme à l'université, vous croiserez du R : savoir le lire est un vrai atout.

Cette section ne vous demande pas de choisir un camp. Nous allons **refaire dans R les analyses des sections 3.1, 3.3 et 3.4 et du 4.1**, sur le même fichier `donnees/commandes.csv`. Retrouver les mêmes nombres avec un autre langage est la meilleure des vérifications : si deux outils indépendants donnent la même réponse, vous pouvez avoir confiance.

> 🧭 **Section à lire après 4.1.** Nous supposons connues les notions de variable, fonction, boucle et condition vues en 4.1 ; ici on ne s'attarde que sur ce qui **change** en R.

### 4.2.1 Lancer R, et premières différences

On lance R avec la commande `R` (session interactive) ou `Rscript mon_script.R` (pour exécuter un fichier). Le confort d'un éditeur s'obtient avec **RStudio** ou VS Code. Tous les blocs R de ce livre ont été **réellement exécutés** avec R, et leur sortie est affichée juste en dessous, comme pour Python.

Voici un premier contact, à comparer avec Python :

```r
version$version.string
x <- 12.5            # l'affectation s'écrit « <- » (le « = » marche aussi, mais on utilise « <- »)
x * 3
print("Bonjour Dar Jasmin !")
```
<!--sortie-->
```text
[1] "R version 4.4.3 (2025-02-28)"
[1] 37.5
[1] "Bonjour Dar Jasmin !"
```

Les trois différences à connaître tout de suite :

| | Python | R |
|---|---|---|
| Affectation | `x = 12.5` | `x <- 12.5` |
| Premier indice d'une liste | **0** | **1** |
| Fin de ligne | indentation | accolades `{ }` |

> ⚠️ **En R, on compte à partir de 1.** `x[1]` est le **premier** élément (en Python : `x[0]`). Et le découpage `x[2:4]` donne les éléments 2, 3 **et 4** : les deux bornes sont **incluses** (en Python, la borne de droite est exclue). C'est la source n°1 d'erreurs quand on passe d'un langage à l'autre.

### 4.2.2 Vecteurs : la brique de base

En R, il n'existe pas de « nombre seul » : `12.5` est un **vecteur de longueur 1**. La fonction `c()` (*combine*) assemble un vecteur, et **toutes les opérations s'appliquent élément par élément**, sans boucle. Cette idée de **vectorisation** est le cœur de R (et, nous le verrons, de NumPy en 4.4).

**Exemple à la main.** Quatre commandes de 44,8 ; 34,5 ; 88,2 et 30,1 DT. Leur somme est $197{,}6$, leur moyenne $49{,}4$ DT. Avec 19 % de TVA, chaque montant est multiplié par 1,19 : $44{,}8\to53{,}31$ (arrondi), etc.

```r
montants <- c(44.8, 34.5, 88.2, 30.1)
sum(montants)
mean(montants)
montants * 1.19                 # la multiplication s'applique à chaque élément
round(montants * 1.19, 2)
montants[1]                     # le PREMIER élément
montants[2:3]                   # éléments 2 et 3 (bornes incluses)
montants[-1]                    # indice négatif : tout SAUF le premier
montants[montants > 40]         # sélection par condition
```
<!--sortie-->
```text
[1] 197.6
[1] 49.4
[1]  53.312  41.055 104.958  35.819
[1]  53.31  41.06 104.96  35.82
[1] 44.8
[1] 34.5 88.2
[1] 34.5 88.2 30.1
[1] 44.8 88.2
```

Les valeurs 197,6 et 49,4 retombent sur le calcul à la main. Remarquez les deux emplois de `[ ]` :

- `montants[-1]` signifie « **tout sauf** le premier » (en Python, `-1` désignait le **dernier** !) ;
- `montants[montants > 40]` : on donne au crochet un vecteur de vrai/faux et R ne garde que les `TRUE`. Ce « **filtrage logique** » est l'équivalent exact de la compréhension de liste de 4.1.6 ; on le retrouvera avec pandas.

Les autres types de base ressemblent à ceux de Python : `numeric` (décimaux), `integer`, `character` (texte), `logical` (`TRUE`/`FALSE`). Une particularité précieuse : R a une **valeur manquante intégrée**, `NA` (*not available*), qui contamine les calculs tant qu'on ne demande pas explicitement de l'ignorer :

```r
ventes <- c(12, 15, NA, 9)
mean(ventes)                    # une valeur manquante rend la moyenne inconnue
mean(ventes, na.rm = TRUE)      # on demande d'ignorer les NA
sum(is.na(ventes))              # compter les valeurs manquantes
```
<!--sortie-->
```text
[1] NA
[1] 12
[1] 1
```

> 💡 **Pourquoi `NA` contamine-t-il ?** Si une valeur est inconnue, la moyenne l'est aussi : R refuse de faire comme si de rien n'était. C'est un comportement *honnête*, qui évite d'oublier des données manquantes sans s'en rendre compte. Nous verrons au volume suivant comment les traiter avec soin.

### 4.2.3 Fonctions, conditions et boucles

La syntaxe change, pas les idées :

```r
ttc <- function(prix_ht, taux_tva = 0.19) {
  round(prix_ht * (1 + taux_tva), 2)      # la dernière valeur calculée est renvoyée
}
ttc(100)
ttc(100, 0.07)
ttc(c(12.5, 45, 15.9))                    # la fonction marche sur un vecteur entier, gratuitement
```
<!--sortie-->
```text
[1] 119
[1] 107
[1] 14.88 53.55 18.92
```

La dernière ligne est remarquable : parce que `*` et `round` sont vectorisés, notre fonction `ttc`, écrite pour **un** prix, marche telle quelle sur **une liste** de prix. En Python pur, il aurait fallu une boucle ou une compréhension.

Les conditions et les boucles :

```r
frais_livraison <- function(total, retrait_boutique) {
  if (retrait_boutique) {
    0
  } else if (total >= 100) {
    0
  } else {
    7
  }
}
c(frais_livraison(80, FALSE), frais_livraison(120, FALSE), frais_livraison(80, TRUE))

capital <- 1000; annees <- 0
while (capital < 2000) {
  capital <- capital * 1.05
  annees <- annees + 1
}
annees

# version vectorisée de « si… alors… sinon » : ifelse
totaux <- c(80, 120, 100, 35)
ifelse(totaux >= 100, 0, 7)
```
<!--sortie-->
```text
[1] 7 0 0
[1] 15
[1] 7 0 0 7
```

On retrouve 7, 0, 0 pour les frais, et 15 années pour doubler un capital placé à 5 % : exactement ce que Python a donné en 4.1. La fonction `ifelse` applique le test à **chaque élément** d'un vecteur, ce que `if` ne sait pas faire.

> ⚠️ **Piège de la vectorisation.** `if (totaux >= 100)` appliqué à un vecteur de plusieurs éléments n'a pas de sens : `if` attend **un seul** vrai/faux. Utilisez `ifelse` pour les vecteurs.

**La caisse de la boutique, en R.** Reprenons le calcul du sous-total du ticket (4.1.10) avec un **vecteur nommé**, qui joue le rôle du dictionnaire :

```r
catalogue <- c(bol = 12.5, tasse = 8.0, plateau = 45.0, bougie = 15.9)
panier    <- c(bol = 2, plateau = 1, bougie = 3)

catalogue[names(panier)]                         # les prix des produits du panier
sous_total <- sum(catalogue[names(panier)] * panier)
remise <- if (sous_total > 100) 0.10 * sous_total else 0
net <- sous_total - remise
c(HT = sous_total, remise = remise, TVA = 0.19 * net, TTC = 1.19 * net)
```
<!--sortie-->
```text
    bol plateau  bougie 
   12.5    45.0    15.9 
      HT   remise      TVA      TTC 
117.7000  11.7700  20.1267 126.0567 
```

Nous retrouvons un sous-total de 117,70 DT, une remise de 11,77 DT et un total TTC de 126,06 DT (aux arrondis près) : le même ticket qu'en Python, en quatre lignes grâce à la vectorisation.

### 4.2.4 Le `data.frame` : le tableau de données

Le tableau est **l'objet central de R**. Un `data.frame` est un tableau dont chaque colonne est un vecteur (de types éventuellement différents). Chargeons les commandes, avec les trois gestes de 3.1.2 : forme, types, résumé.

```r
df <- read.csv("donnees/commandes.csv")      # lit le CSV directement en tableau
dim(df)                                      # lignes, colonnes
str(df)                                      # structure : type de chaque colonne
head(df, 4)
```
<!--sortie-->
```text
[1] 400   4
'data.frame':	400 obs. of  4 variables:
 $ canal       : chr  "Boutique" "Site" "Instagram" "Instagram" ...
 $ montant     : num  44.8 34.5 88.2 30.1 110.1 ...
 $ livraison   : int  0 2 5 4 0 5 0 0 5 6 ...
 $ satisfaction: int  4 4 4 4 5 3 5 4 4 3 ...
      canal montant livraison satisfaction
1  Boutique    44.8         0            4
2      Site    34.5         2            4
3 Instagram    88.2         5            4
4 Instagram    30.1         4            4
```

`read.csv` a deviné les types : `canal` est du texte (`chr`), les trois autres colonnes sont numériques. Contrairement au module `csv` de Python (4.1.9) qui lisait tout en texte, la conversion est faite pour nous. Le résumé numérique :

```r
summary(df)
colSums(is.na(df))                           # valeurs manquantes par colonne
```
<!--sortie-->
```text
    canal              montant         livraison       satisfaction  
 Length:400         Min.   :  8.60   Min.   : 0.000   Min.   :1.000  
 Class :character   1st Qu.: 34.17   1st Qu.: 0.000   1st Qu.:3.000  
 Mode  :character   Median : 51.00   Median : 3.000   Median :4.000  
                    Mean   : 60.25   Mean   : 3.288   Mean   :3.965  
                    3rd Qu.: 75.83   3rd Qu.: 5.000   3rd Qu.:5.000  
                    Max.   :255.70   Max.   :13.000   Max.   :5.000  
       canal      montant    livraison satisfaction 
           0            0            0            0 
```

La ligne `montant` donne un minimum de 8,6, une médiane de 51, une moyenne de 60,25 et un maximum de 255,7 : **les mêmes chiffres** que le `describe()` de pandas au 3.1.2. On accède à une colonne avec `$` :

```r
m <- df$montant
c(moyenne = mean(m), mediane = median(m), ecart_type = sd(m), iqr = IQR(m))
quantile(m, c(0.05, 0.25, 0.50, 0.75, 0.95))
```
<!--sortie-->
```text
   moyenne    mediane ecart_type        iqr 
  60.24575   51.00000   38.01791   41.65000 
     5%     25%     50%     75%     95% 
 18.985  34.175  51.000  75.825 128.555 
```

Les nombres sont ceux du 3.1 : moyenne 60,25 ; médiane 51 ; écart-type 38,02 (R divise par $n-1$, comme pandas) ; quartiles 34,2 et 75,8. Les deux logiciels utilisent la même définition par défaut du quantile (interpolation linéaire), ce qui explique la concordance exacte. Pour résumer **par groupe** :

```r
tapply(df$montant, df$canal, mean)           # moyenne par canal
table(df$canal)                              # effectifs par canal
aggregate(montant ~ canal, data = df, FUN = function(v) c(n = length(v), moyenne = mean(v), sd = sd(v)))
```
<!--sortie-->
```text
 Boutique Instagram      Site 
 74.80965  49.01087  59.50338 

 Boutique Instagram      Site 
      114       138       148 
      canal montant.n montant.moyenne montant.sd
1  Boutique 114.00000        74.80965   40.64683
2 Instagram 138.00000        49.01087   31.08370
3      Site 148.00000        59.50338   38.32863
```

La formule `montant ~ canal` se lit « le montant **en fonction du** canal » : cette notation en tilde est partout en R (nous la retrouverons pour les modèles de régression au volume suivant). Les moyennes par canal (74,81 ; 59,50 ; 49,01) sont celles que nous avions obtenues avec Python au 4.1.9, à la main.

### 4.2.5 Les statistiques « sortent de la boîte »

C'est ici que R brille : les procédures de la statistique classique sont **au catalogue de base**, sans rien installer.

**Intervalle de confiance et test de Welch.** Rappel du 3.3 et du 3.4 : IC à 95 % de la moyenne, [56,51 ; 63,98] ; test boutique contre Instagram, $t=5{,}565$, 208,4 degrés de liberté, $p\approx8\times10^{-8}$.

```r
test_moyenne <- t.test(df$montant)           # IC de la moyenne (test contre 0 sans intérêt, mais l'IC est utile)
round(test_moyenne$conf.int, 2)

b <- df$montant[df$canal == "Boutique"]
i <- df$montant[df$canal == "Instagram"]
w <- t.test(b, i)                            # R fait le test de Welch par défaut
c(t = unname(w$statistic), ddl = unname(w$parameter), p = w$p.value)
round(w$conf.int, 1)                         # IC95 % de la différence des moyennes
```
<!--sortie-->
```text
[1] 56.51 63.98
attr(,"conf.level")
[1] 0.95
           t          ddl            p 
5.564672e+00 2.084304e+02 8.016366e-08 
[1] 16.7 34.9
attr(,"conf.level")
[1] 0.95
```

On lit exactement $t=5{,}565$, 208,4 degrés de liberté et une p-valeur $p\approx8\times10^{-8}$ : les valeurs obtenues avec `scipy` au 3.4.3. Un seul appel de fonction fait ce que nous avions codé en plusieurs lignes à la main.

> 💡 **R fait le test de Welch par défaut**, ce qui est bien la bonne pratique recommandée en 3.4.3 (en Python, il faut penser à écrire `equal_var=False`). Chaque langage a ses défauts : **lisez la documentation** (`?t.test` en R, `help()` en Python) pour savoir ce que fait réellement une fonction.

**Corrélation et régression, un avant-goût.** Les mêmes outils donnent la corrélation entre délai de livraison et satisfaction, et une droite de régression, que le volume II étudiera en détail :

```r
livres <- subset(df, canal != "Boutique")            # on exclut les retraits en boutique (délai = 0)
cor(livres$livraison, livres$satisfaction)
modele <- lm(satisfaction ~ livraison, data = livres)
round(coef(modele), 3)
```
<!--sortie-->
```text
[1] -0.4069396
(Intercept)   livraison 
      4.581      -0.180 
```

La corrélation vaut environ $-0{,}41$ : elle est **négative**, plus le délai est long, moins les clients sont satisfaits. La pente estimée, $-0{,}18$, est la perte de satisfaction **par jour de retard supplémentaire**. Elle coïncide avec le coefficient $-0{,}18$ qui a servi à fabriquer les données au 3.1.2 (et l'ordonnée à l'origine, 4,58, est proche du 4,6 utilisé) : un joli moyen de vérifier que la machine retrouve bien ce qu'on y a mis.

### 4.2.6 Le tidyverse : manipuler les tableaux avec des « phrases »

Les fonctions de base de R sont puissantes mais leur syntaxe est parfois irrégulière. Un ensemble de packages cohérents, le **tidyverse** (dplyr, tidyr, readr, ggplot2…), a standardisé une façon de travailler : des **verbes** simples enchaînés par un **tube** (`|>`, qui se lit « puis »). Chaque verbe prend un tableau et rend un tableau.

| Verbe | Rôle | Équivalent SQL (chapitre 5) |
|---|---|---|
| `filter()` | garder des lignes | `WHERE` |
| `select()` | garder des colonnes | `SELECT` |
| `mutate()` | créer ou modifier une colonne | colonne calculée |
| `arrange()` | trier | `ORDER BY` |
| `group_by()` + `summarise()` | résumer par groupe | `GROUP BY` |

```r
suppressPackageStartupMessages(library(dplyr))

df |>
  group_by(canal) |>
  summarise(n = n(),
            panier_moyen = round(mean(montant), 2),
            ecart_type = round(sd(montant), 2),
            satisfaction = round(mean(satisfaction), 2)) |>
  arrange(desc(panier_moyen))
```
<!--sortie-->
```text
# A tibble: 3 × 5
  canal         n panier_moyen ecart_type satisfaction
  <chr>     <int>        <dbl>      <dbl>        <dbl>
1 Boutique    114         74.8       40.6         4.49
2 Site        148         59.5       38.3         3.79
3 Instagram   138         49.0       31.1         3.72
```

Lisez cette « phrase » à voix haute : *prends le tableau des commandes, puis groupe par canal, puis résume (effectif, panier moyen, écart-type, satisfaction), puis trie par panier moyen décroissant.* C'est presque du français, et c'est ce qui rend le tidyverse si agréable à lire. Une seconde phrase, avec filtre et colonne calculée :

```r
df |>
  filter(canal != "Boutique", livraison > 8) |>      # livraisons lentes
  mutate(montant_ttc = round(montant * 1.19, 2)) |>
  select(canal, montant, montant_ttc, livraison, satisfaction) |>
  arrange(desc(livraison)) |>
  head(5)
```
<!--sortie-->
```text
      canal montant montant_ttc livraison satisfaction
1      Site    40.1       47.72        13            2
2      Site    65.4       77.83        10            3
3      Site    98.1      116.74        10            1
4 Instagram    61.1       72.71         9            4
5      Site   105.1      125.07         9            3
```

Nous retrouverons exactement cette logique, en Python, avec **pandas** (section 4.4), puis en SQL au chapitre 5. Les trois langages expriment les mêmes idées : *filtrer, sélectionner, créer, trier, regrouper*. Apprendre l'un fait gagner du temps sur les deux autres.

> 🧭 **Et les graphiques ?** R possède aussi une bibliothèque de graphiques célèbre, **ggplot2**. Nous la présentons à la section 4.5, côte à côte avec matplotlib et seaborn.

### 4.2.7 Python ou R ? Un tableau de correspondance

| Tâche | Python (pandas) | R |
|---|---|---|
| Lire un CSV | `pd.read_csv("f.csv")` | `read.csv("f.csv")` |
| Moyenne d'une colonne | `df["montant"].mean()` | `mean(df$montant)` |
| Filtrer des lignes | `df[df["canal"] == "Site"]` | `df[df$canal == "Site", ]` ou `filter(df, canal == "Site")` |
| Moyenne par groupe | `df.groupby("canal")["montant"].mean()` | `tapply(df$montant, df$canal, mean)` |
| Test de Welch | `stats.ttest_ind(a, b, equal_var=False)` | `t.test(a, b)` |
| Premier élément | `x[0]` | `x[1]` |
| Valeur manquante | `NaN` / `None` | `NA` |

> 💡 **Comment choisir ?** Python est un langage généraliste : il excelle dès qu'il faut **mettre en production**, automatiser, faire de l'apprentissage automatique (volume III) ou du traitement de texte. R excelle pour **l'analyse statistique exploratoire et les rapports**. Beaucoup de professionnels utilisent les deux. La stratégie de ce livre : **Python comme langage principal**, R en parallèle quand il éclaire un concept ou qu'il est l'outil naturel.

> ✅ **À retenir**
> - R est un langage pensé pour les statistiques ; les opérations y sont **vectorisées** (élément par élément, sans boucle).
> - Attention aux différences de Python : on **compte à partir de 1**, les bornes d'un découpage sont **incluses**, `x[-1]` signifie « tout sauf le premier » et `<-` est l'affectation.
> - Le `data.frame` est l'objet central ; `read.csv`, `summary`, `tapply`, `aggregate` couvrent l'essentiel de l'exploration.
> - `NA` représente une valeur manquante et **contamine** les calculs sauf si l'on écrit `na.rm = TRUE`.
> - Les tests classiques (`t.test`, `cor`, `lm`) sont fournis d'origine ; `t.test` fait le test de **Welch** par défaut.
> - Le tidyverse (`filter`, `mutate`, `group_by`, `summarise`) enchaîne des « verbes » avec `|>`, comme pandas et SQL.
> - Retrouver les mêmes nombres dans deux langages indépendants (moyenne 60,25 ; $t=5{,}565$) est la meilleure des vérifications.


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


## 4.4 NumPy et pandas : manipuler des données

> 💡 **Intuition.** Python « de base » (section 4.1) sait faire des calculs, mais il est lent et verbeux dès qu'il faut traiter des milliers de nombres. Deux bibliothèques ont changé la donne et sont aujourd'hui **le** socle de la data science en Python :
>
> - **NumPy** ajoute un nouveau type d'objet, le **tableau** (`ndarray`), qui permet de calculer sur *toute une colonne de nombres d'un seul coup*, à vitesse quasi native ;
> - **pandas** pose par-dessus un **tableau étiqueté** (le `DataFrame`) : des colonnes qui ont un nom et un type, des lignes qui ont une étiquette, des dates, des valeurs manquantes… bref, un tableur programmable, sans souris et sans limite de taille.
>
> Yasmine a l'habitude d'Excel. Tout ce que nous allons faire ici, elle pourrait le faire à la main dans une feuille de calcul, mais pour 400 lignes ce serait pénible, et pour 400 000 lignes ce serait impossible. Surtout, **le code est rejouable** : on corrige une erreur, on relance, on retrouve toutes les analyses mises à jour.

> 🧭 **Comment lire cette section.** Elle est longue parce que pandas est *l'*outil que vous utiliserez tous les jours. Les trois premières parties (4.4.1 à 4.4.4) concernent NumPy ; la suite concerne pandas. Chaque notion est introduite par un **petit exemple à la main**, puis appliquée aux 400 commandes de Dar Jasmin. Si vous êtes pressé(e), lisez au moins 4.4.5 à 4.4.9, puis la petite application de 4.4.13.

### 4.4.1 NumPy : pourquoi un tableau n'est pas une liste

Yasmine veut afficher les prix TTC de cinq articles à partir de leurs prix hors taxe (TVA à 19 %). Avec une **liste** Python classique, on écrit une boucle :

```python
import numpy as np

prix_ht = [10, 20, 5, 40, 15]
prix_ttc = [round(p * 1.19, 2) for p in prix_ht]
print(prix_ttc)
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

Mesurons maintenant l'écart de vitesse sur un million de prix :

```python
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

Les durées exactes dépendent de votre machine (nous n'affichons donc que des conclusions robustes). Sur du calcul plus lourd que cette simple multiplication, l'écart se compte en **dizaines, voire centaines de fois**. C'est la raison pour laquelle on cherche toujours à **vectoriser** : écrire `x * 1.19` plutôt qu'une boucle `for`.

> ✅ **À retenir.** Un tableau NumPy = un bloc de nombres **du même type**, sur lequel les opérations s'appliquent **élément par élément** et vite. Règle d'or : *pas de boucle `for` sur des données, sauf si l'on n'a vraiment pas le choix.*

### 4.4.2 Créer, indexer, trancher

Quelques manières courantes de fabriquer des tableaux :

```python
print(np.arange(0, 10, 2))            # de 0 à 10 (exclu), pas de 2
print(np.linspace(0, 1, 5))           # 5 points régulièrement espacés entre 0 et 1
print(np.zeros(3), np.ones(3))        # que des 0, que des 1
print(np.full((2, 3), 7))             # un tableau 2×3 rempli de 7
```
<!--sortie-->
```text
[0 2 4 6 8]
[0.   0.25 0.5  0.75 1.  ]
[0. 0. 0.] [1. 1. 1.]
[[7 7 7]
 [7 7 7]]
```

Un tableau a trois caractéristiques à toujours avoir en tête : sa **forme** (`shape`), son nombre de dimensions (`ndim`) et son type (`dtype`). Prenons les ventes hebdomadaires (en DT) des trois canaux de Dar Jasmin sur quatre semaines : une **matrice** de 3 lignes (canaux) et 4 colonnes (semaines), exactement comme celles du chapitre 1.

| | Sem. 1 | Sem. 2 | Sem. 3 | Sem. 4 |
|---|---|---|---|---|
| Instagram | 120 | 150 | 90 | 140 |
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
- `A[0]` : toute la ligne 0 (Instagram) ;
- `A[:, 3]` : toute la colonne 3 (semaine 4) ; le « `:` » signifie « tout » ;
- `A[0:2, 1:3]` : lignes 0 et 1, colonnes 1 et 2 (la borne de fin est **exclue**).

```python
print(A[1, 2])
print(A[0])
print(A[:, 3])
print(A[0:2, 1:3])
print(A[-1, -1])      # les indices négatifs partent de la fin : dernière ligne, dernière colonne
```
<!--sortie-->
```text
120
[120 150  90 140]
[140  70 105]
[[150  90]
 [100 120]]
105
```

**Filtrer avec un masque booléen.** Comparer un tableau à un nombre produit un tableau de `True`/`False` de même forme : le **masque**. Utilisé comme indice, il ne garde que les cases `True`.

```python
masque = A > 100
print(masque)
print(A[masque])                 # les ventes strictement supérieures à 100 DT
print("combien ?", masque.sum()) # True compte pour 1 : on compte donc les cases vraies
print(np.where(A > 100, "bien", "—"))   # np.where(condition, si_vrai, si_faux)
```
<!--sortie-->
```text
[[ True  True False  True]
 [False False  True False]
 [False False False  True]]
[120 150 140 120 105]
combien ? 5
[['bien' 'bien' '—' 'bien']
 ['—' '—' 'bien' '—']
 ['—' '—' '—' 'bien']]
```

Dans le masque, on compte 5 cases vraies : 120, 150 et 140 (Instagram), 120 (Site, semaine 3) et 105 (Boutique, semaine 4). Notez que le 100 du Site (semaine 2) n'est **pas** compté : la condition est « strictement supérieur à 100 ». La somme d'un masque est une astuce très utile : elle **compte** les `True`.

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
fenetre = C[0, :]      # une vue sur la ligne d'Instagram
fenetre[0] = 999
print(C[0, 0], "<- modifié par la vue ;  A[0, 0] =", A[0, 0], "(intact, car C est une copie)")
```
<!--sortie-->
```text
999 <- modifié par la vue ;  A[0, 0] = 120 (intact, car C est une copie)
```

Enfin, un tableau a **un seul type** : si l'on mélange entiers et décimaux, tout devient décimal. Et un tableau d'entiers ne sait pas représenter une valeur manquante, ce qui sera une raison de plus d'aimer pandas (4.4.11).

```python
print(np.array([1, 2, 3.5]))             # tout devient décimal
print(np.array([1, 2, 3]).astype(float)) # conversion explicite
```
<!--sortie-->
```text
[1.  2.  3.5]
[1. 2. 3.]
```

### 4.4.3 Le broadcasting : calculer entre tableaux de formes différentes

Que se passe-t-il si l'on fait `A - m` où $A$ est une matrice $3\times 4$ et $m$ un vecteur de 4 nombres ? Mathématiquement, la soustraction n'est pas définie (les formes diffèrent) ; NumPy, lui, **étire** le plus petit tableau pour qu'il s'adapte : c'est le **broadcasting** (« diffusion »).

Reprenons l'exemple de Yasmine. Elle veut savoir, pour chaque semaine, **de combien chaque canal s'écarte de la moyenne de cette semaine**. Moyenne de la semaine 1 : $(120+90+60)/3=90$. Semaine 2 : $(150+100+50)/3=100$. Semaine 3 : $(90+120+90)/3=100$. Semaine 4 : $(140+70+105)/3=105$. Donc $m=(90,\,100,\,100,\,105)$ et, par exemple, Instagram en semaine 1 s'écarte de $120-90=+30$.

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

Le résultat reproduit les valeurs du dessin : `30` pour Instagram en semaine 1, `-35` pour le Site en semaine 4, etc.

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

À la main : la moyenne d'Instagram est $(120+150+90+140)/4=125$, donc la première ligne devient $(-5,\ 25,\ -35,\ 15)$. Et si on oublie `keepdims` ? Un message d'erreur clair nous rappelle la règle :

```python
try:
    A - A.mean(axis=1)          # forme (3,) au lieu de (3, 1)
except ValueError as e:
    print("ValueError :", e)
```
<!--sortie-->
```text
ValueError : operands could not be broadcast together with shapes (3,4) (3,) 
```

> 🛠️ **Application : standardiser des colonnes.** Au chapitre 1, nous avons vu que les algorithmes de modélisation aiment que les variables aient la même échelle. Centrer-réduire chaque colonne (soustraire sa moyenne, diviser par son écart-type) s'écrit sans boucle grâce au broadcasting : `(X - X.mean(axis=0)) / X.std(axis=0, ddof=1)`. Vous le ferez avec pandas à la section 4.4.7.

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
ligne, colonne = divmod(int(A.argmax()), A.shape[1])      # argmax numérote les cases ligne après ligne
print("meilleure case :", A.max(), "en ligne", ligne, ", colonne", colonne)
```
<!--sortie-->
```text
total général  : 1185
par semaine    : [270 300 300 315]
par canal      : [500 380 305]
meilleure case : 150 en ligne 0 , colonne 1
```

Vérification à la main : Instagram $120+150+90+140=500$, Site $90+100+120+70=380$, Boutique $60+50+90+105=305$, soit $1\,185$ DT au total, ce qui est aussi la somme des totaux par semaine ($270+300+300+315$).

Autres opérations fréquentes :

```python
ventes_instagram = A[0]
print("cumul          :", np.cumsum(ventes_instagram))     # somme cumulée
print("variation      :", np.diff(ventes_instagram))       # différences successives
print("tri croissant  :", np.sort(ventes_instagram))
print("ordre des semaines (de la pire à la meilleure) :", np.argsort(ventes_instagram))
print("écart-type (n-1) :", round(ventes_instagram.std(ddof=1), 2))
```
<!--sortie-->
```text
cumul          : [120 270 360 500]
variation      : [ 30 -60  50]
tri croissant  : [ 90 120 140 150]
ordre des semaines (de la pire à la meilleure) : [2 0 3 1]
écart-type (n-1) : 26.46
```

> ⚠️ **`ddof` encore.** Comme pour `np.std` à la section 3.1.4, NumPy divise par $n$ par défaut. Pour estimer la variance d'une population à partir d'un échantillon, il faut **`ddof=1`** (division par $n-1$). pandas, lui, utilise $n-1$ par défaut : un écart entre `np.std(x)` et `serie.std()` n'est donc pas un bug.

**Nombres aléatoires.** On rencontre le générateur de nombres aléatoires depuis le chapitre 2 : on le crée une fois avec une **graine** (*seed*), puis on tire.

```python
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

La moyenne d'un masque booléen est la **proportion** de `True` : c'est la façon la plus économique d'estimer une probabilité par simulation. On retrouve (à très peu près) les 2,3 % calculés à la main au 2.2 pour un jour à plus de deux écarts-types au-dessus de la moyenne.

Enfin, NumPy sait faire l'algèbre linéaire du chapitre 1 : produit matriciel `@`, transposée `.T`, inverse, valeurs propres, résolution de système, etc.

```python
M = np.array([[2.0, 1.0], [1.0, 3.0]])
b = np.array([5.0, 10.0])
print("solution de M x = b :", np.linalg.solve(M, b))
print("valeurs propres de M :", np.round(np.linalg.eigvalsh(M), 3))
```
<!--sortie-->
```text
solution de M x = b : [1. 3.]
valeurs propres de M : [1.382 3.618]
```

À la main : $2x+y=5$ et $x+3y=10$ donnent $x=1$, $y=3$.

> ✅ **À retenir (NumPy).** (1) tableau = type unique + forme ; (2) indexer avec `[ligne, colonne]`, tranches `a:b` (fin exclue) et masques booléens ; (3) le **broadcasting** étire les dimensions de taille 1 ; (4) `axis` = la dimension qui disparaît ; (5) une tranche est une **vue** : `.copy()` pour travailler sans risque.

### 4.4.5 pandas : Series et DataFrame

NumPy ne connaît que des nombres rangés dans des cases numérotées. Mais une vraie table de données, ce sont des colonnes **nommées** (« montant », « canal ») de **types différents** (nombres, texte, dates), avec des lignes qu'on veut pouvoir **identifier**. C'est ce que fait pandas.

Deux objets suffisent pour commencer :

- la **Series** : une colonne, c'est-à-dire un tableau NumPy muni d'un **index** (une étiquette par valeur) et d'un nom ;
- le **DataFrame** : un tableau de plusieurs Series partageant le même index.

```python
import numpy as np
import pandas as pd

pd.set_option("display.width", 110)          # pour que les tableaux larges ne soient pas coupés à l'affichage
pd.set_option("display.max_columns", 20)

ventes = pd.Series([500, 380, 305], index=["Instagram", "Site", "Boutique"], name="ventes")
print(ventes)
print()
print("accès par étiquette :", ventes["Site"], "| par position :", ventes.iloc[2])
```
<!--sortie-->
```text
Instagram    500
Site         380
Boutique     305
Name: ventes, dtype: int64

accès par étiquette : 380 | par position : 305
```

Un `DataFrame` s'obtient, par exemple, à partir d'un dictionnaire « nom de colonne → valeurs » :

```python
mini = pd.DataFrame({
    "canal": ["Instagram", "Site", "Boutique"],
    "ventes": [500, 380, 305],
    "ouvert_le_dimanche": [True, True, False],
})
print(mini)
print()
print(mini.dtypes)
```
<!--sortie-->
```text
       canal  ventes  ouvert_le_dimanche
0  Instagram     500                True
1       Site     380                True
2   Boutique     305               False

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
print(df.head())
print()
df.info()
```
<!--sortie-->
```text
(400, 4)
       canal  montant  livraison  satisfaction
0   Boutique     44.8          0             4
1       Site     34.5          2             4
2  Instagram     88.2          5             4
3  Instagram     30.1          4             4
4   Boutique    110.1          0             5

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

Le fichier ne contient pas de **date**, or la plupart des vraies données de vente en ont une. Pour illustrer le travail sur les dates (4.4.12) et sur plusieurs tables (4.4.10), nous allons **ajouter deux colonnes simulées** : la date de chaque commande (réparties sur 20 semaines à partir du lundi 5 janvier 2026) et un numéro de client (120 clients possibles). Rappelons que tout est fictif et reproductible grâce à la graine :

```python
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
   id_commande      canal  montant  livraison  satisfaction       date  id_client
0            1       Site     49.9          8             2 2026-01-05        100
1            2  Instagram     21.5          3             4 2026-01-05         46
2            3   Boutique     34.2          0             4 2026-01-05         26
3            4       Site    103.0          3             5 2026-01-05         97
4            5  Instagram     26.7          4             4 2026-01-06        105
5            6   Boutique     37.4          0             4 2026-01-06        120

id_commande              int64
canal                      str
montant                float64
livraison                int64
satisfaction             int64
date            datetime64[us]
id_client                int64
dtype: object
```

Notez le type `datetime64` de la colonne `date` : pandas sait que ce ne sont pas du texte, mais de vraies dates, avec lesquelles on peut calculer. Dernier réflexe, le résumé statistique :

```python
print(df.describe().round(2))
print()
print(df["canal"].value_counts())
```
<!--sortie-->
```text
       id_commande  montant  livraison  satisfaction                 date  id_client
count       400.00   400.00     400.00        400.00                  400     400.00
mean        200.50    60.25       3.29          3.96  2026-03-18 06:25:12      61.87
min           1.00     8.60       0.00          1.00  2026-01-05 00:00:00       2.00
25%         100.75    34.18       0.00          3.00  2026-02-09 00:00:00      30.75
50%         200.50    51.00       3.00          4.00  2026-03-19 12:00:00      62.00
75%         300.25    75.82       5.00          5.00  2026-04-25 00:00:00      93.00
max         400.00   255.70      13.00          5.00  2026-05-24 00:00:00     120.00
std         115.61    38.02       2.56          0.80                  NaN      34.71

canal
Site         148
Instagram    138
Boutique     114
Name: count, dtype: int64
```

### 4.4.6 Sélectionner : colonnes, lignes, conditions

Pour sélectionner, on dispose de plusieurs outils, résumés dans le tableau ci-dessous. Prenons une toute petite table pour voir clairement ce qui se passe :

```python
petit = df[["id_commande", "canal", "montant"]].head(5)
print(petit)
```
<!--sortie-->
```text
   id_commande      canal  montant
0            1       Site     49.9
1            2  Instagram     21.5
2            3   Boutique     34.2
3            4       Site    103.0
4            5  Instagram     26.7
```

| Je veux… | J'écris | Remarque |
|---|---|---|
| une colonne | `petit["montant"]` | donne une Series |
| plusieurs colonnes | `petit[["canal", "montant"]]` | **doubles crochets** : une liste de noms |
| des lignes **par position** | `petit.iloc[1:3]` | `iloc` = *integer location* ; fin **exclue** |
| des lignes **par étiquette** | `petit.loc[1:3]` | `loc` = *label* ; fin **incluse** ! |
| des lignes par condition | `petit[petit["montant"] > 50]` | masque booléen, comme en NumPy |

```python
print(petit["montant"].tolist())
print(petit[["canal", "montant"]].iloc[1:3])
print(petit.loc[1:3, ["canal", "montant"]])      # lignes d'étiquettes 1 à 3 INCLUSES
```
<!--sortie-->
```text
[49.9, 21.5, 34.2, 103.0, 26.7]
       canal  montant
1  Instagram     21.5
2   Boutique     34.2
       canal  montant
1  Instagram     21.5
2   Boutique     34.2
3       Site    103.0
```

> ⚠️ **`iloc` exclut la fin, `loc` l'inclut.** `iloc[1:3]` renvoie les lignes 1 et 2 ; `loc[1:3]` renvoie les lignes 1, 2 **et 3** (car on désigne des étiquettes, et on veut « de 1 jusqu'à 3 »). C'est l'une des étourderies les plus fréquentes.

**Filtrer avec des conditions.** Les opérateurs `&`, `|`, `~` demandent **des parenthèses** autour de chaque condition (car `&` s'évalue avant `>`) :

```python
gros_insta = df[(df["canal"] == "Instagram") & (df["montant"] > 100)]
print("commandes Instagram de plus de 100 DT :", len(gros_insta))

# trois autres formes pratiques
print(df["canal"].isin(["Site", "Boutique"]).sum())
print(df["montant"].between(50, 100).sum())          # bornes incluses
print(df.query("canal == 'Site' and livraison >= 7").shape[0])
```
<!--sortie-->
```text
commandes Instagram de plus de 100 DT : 11
262
153
21
```

La méthode `query` accepte une condition écrite comme une phrase : elle se lit mieux sur des conditions longues. Pour **trier** et chercher les extrêmes :

```python
print(df.sort_values("montant", ascending=False).head(3)[["id_commande", "canal", "montant"]])
print(df.nsmallest(3, "montant")[["id_commande", "canal", "montant"]])
```
<!--sortie-->
```text
     id_commande canal  montant
380          381  Site    255.7
102          103  Site    243.8
198          199  Site    217.1
     id_commande      canal  montant
289          290  Instagram      8.6
366          367  Instagram     10.3
326          327  Instagram     10.7
```

### 4.4.7 Créer et transformer des colonnes

Une nouvelle colonne s'obtient en l'assignant, avec des opérations **vectorisées** (comme dans NumPy, sans boucle) :

```python
df["livraison_rapide"] = df["livraison"] <= 3
df["gros_panier"] = np.where(df["montant"] >= 100, "oui", "non")
df["canal_court"] = df["canal"].str[:3].str.upper()           # méthodes .str : opérations sur le texte
print(df[["canal", "canal_court", "montant", "gros_panier", "livraison_rapide"]].head(4))
```
<!--sortie-->
```text
       canal canal_court  montant gros_panier  livraison_rapide
0       Site         SIT     49.9         non             False
1  Instagram         INS     21.5         non              True
2   Boutique         BOU     34.2         non              True
3       Site         SIT    103.0         oui              True
```

Le préfixe `.str` donne accès à toutes les méthodes de texte (`upper`, `lower`, `contains`, `replace`, `split`…) appliquées à **chaque élément** de la colonne.

**Découper une variable continue en classes.** `pd.cut` fabrique des classes de bornes choisies, `pd.qcut` des classes d'effectifs égaux (par quantiles). Par exemple, quatre tranches de panier : « petit » (moins de 30 DT), « moyen » (30 à 60), « grand » (60 à 100) et « très grand » (plus de 100) :

```python
bornes = [0, 30, 60, 100, np.inf]
noms = ["petit", "moyen", "grand", "très grand"]
df["tranche"] = pd.cut(df["montant"], bins=bornes, labels=noms)
print(df["tranche"].value_counts().reindex(noms))
print()
quartiles = pd.qcut(df["montant"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
print(quartiles.value_counts().sort_index())     # ~100 commandes dans chaque quartile par construction
```
<!--sortie-->
```text
tranche
petit          76
moyen         160
grand         112
très grand     52
Name: count, dtype: int64

montant
Q1    100
Q2    100
Q3    100
Q4    100
Name: count, dtype: int64
```

Remarquez la nuance : avec `cut`, les classes sont **définies par vous** et leurs effectifs sont inégaux ; avec `qcut`, ce sont les effectifs qui sont **égaux** (400 / 4 = 100) et les bornes qui s'adaptent aux données.

**Remplacer des valeurs selon un dictionnaire** avec `map` :

```python
etiquettes = {1: "très mécontent", 2: "mécontent", 3: "neutre", 4: "content", 5: "très content"}
df["avis"] = df["satisfaction"].map(etiquettes)
print(df["avis"].value_counts().reindex(list(etiquettes.values())))
```
<!--sortie-->
```text
avis
très mécontent      1
mécontent          15
neutre             85
content           195
très content      104
Name: count, dtype: int64
```

**Standardiser** (centrer-réduire), comme annoncé à la fin de 4.4.3, se fait sur une colonne entière :

```python
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

> 💡 **`apply` : à garder en dernier recours.** Si une transformation n'existe pas en version vectorisée, `df["col"].apply(ma_fonction)` appelle votre fonction **ligne par ligne** : pratique, mais lent (une boucle Python déguisée). Réflexe : chercher d'abord une opération vectorisée (`.str`, `np.where`, `cut`, `map`, opérateurs arithmétiques…). Sur nos 400 lignes la différence est invisible ; pour la mesurer, on répète les montants 500 fois (200 000 lignes) :

```python
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
print("df['montant'] au premier rang :", df["montant"].iloc[0], "(inchangé : montants est indépendant de df)")
```
<!--sortie-->
```text
df['montant'] au premier rang : 49.9 (inchangé : montants est indépendant de df)
```

La conséquence la plus importante : l'**assignation en chaîne** (`df[condition]["colonne"] = valeur`) **ne fonctionne plus**, car `df[condition]` fabrique une copie temporaire que l'on modifie puis que l'on jette. pandas 3.0 émet même un avertissement. Vérifions-le :

```python
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

> ✅ **La bonne écriture, toujours : `df.loc[condition, "colonne"] = valeur`.** Une seule opération, qui désigne à la fois les lignes et la colonne. Et pour *vraiment* garder une copie intacte avant de modifier : `df2 = df.copy()`.

### 4.4.9 Regrouper : le « split-apply-combine » (`groupby`)

C'est l'outil le plus important de pandas pour répondre à des questions du type : *« quel est le montant moyen **par canal** ? », « combien de commandes **par semaine** ? »* La méthode s'appelle **découper – appliquer – combiner** (*split-apply-combine*) :

1. **découper** le tableau en groupes (une valeur de canal = un groupe) ;
2. **appliquer** un calcul à chaque groupe (moyenne, somme, comptage…) ;
3. **combiner** les résultats dans un nouveau tableau.

Faisons-le **à la main** sur six commandes :

| Commande | Canal | Montant |
|---|---|---|
| 1 | Instagram | 20 |
| 2 | Site | 30 |
| 3 | Instagram | 40 |
| 4 | Site | 50 |
| 5 | Boutique | 100 |
| 6 | Site | 70 |

Groupes : Instagram $\{20,40\}$, Site $\{30,50,70\}$, Boutique $\{100\}$. Moyennes : $30$, $50$ et $100$. Comptes : $2$, $3$, $1$. Voici le même calcul en code (pandas range les groupes par ordre alphabétique) :

```python
six = pd.DataFrame({"canal": ["Instagram", "Site", "Instagram", "Site", "Boutique", "Site"],
                    "montant": [20, 30, 40, 50, 100, 70]})
print(six.groupby("canal")["montant"].agg(["mean", "count"]))
```
<!--sortie-->
```text
            mean  count
canal                  
Boutique   100.0      1
Instagram   30.0      2
Site        50.0      3
```

Passons aux 400 commandes. L'**agrégation nommée** donne des colonnes lisibles : `nom=("colonne", "fonction")`.

```python
resume = df.groupby("canal").agg(
    commandes=("montant", "count"),
    ca=("montant", "sum"),
    panier_moyen=("montant", "mean"),
    panier_median=("montant", "median"),
    satisfaction=("satisfaction", "mean"),
).round(2)
print(resume.sort_values("ca", ascending=False))
```
<!--sortie-->
```text
           commandes      ca  panier_moyen  panier_median  satisfaction
canal                                                                  
Site             148  8806.5         59.50          49.50          3.79
Boutique         114  8528.3         74.81          64.85          4.49
Instagram        138  6763.5         49.01          41.50          3.72
```

On peut regrouper selon **plusieurs** critères, ou demander une répartition en proportions :

```python
print(df.groupby(["canal", "gros_panier"]).size().unstack())     # unstack : un niveau d'index devient colonnes
print()
print(pd.crosstab(df["canal"], df["tranche"], normalize="index").round(2))   # proportions par ligne
```
<!--sortie-->
```text
gros_panier  non  oui
canal                
Boutique      87   27
Instagram    127   11
Site         134   14

tranche    petit  moyen  grand  très grand
canal                                     
Boutique    0.07   0.37   0.32        0.24
Instagram   0.32   0.38   0.22        0.08
Site        0.16   0.44   0.30        0.09
```

`crosstab` (tableau croisé) est un raccourci pour compter les effectifs de deux variables qualitatives ; avec `normalize="index"` chaque ligne est ramenée à 1, ce qui répond à « *parmi* les commandes Instagram, quelle part de petits paniers ? ». Pour des tableaux de synthèse à deux entrées sur une variable numérique, on a `pivot_table` :

```python
print(df.pivot_table(index="canal", columns="gros_panier", values="satisfaction", aggfunc="mean").round(2))
```
<!--sortie-->
```text
gros_panier   non   oui
canal                  
Boutique     4.49  4.48
Instagram    3.72  3.64
Site         3.80  3.71
```

Enfin `transform` calcule un résultat **par groupe** mais le renvoie **aligné sur les lignes d'origine**, ce qui permet de comparer chaque commande à son groupe :

```python
df["ecart_moy_canal"] = df["montant"] - df.groupby("canal")["montant"].transform("mean")
print(df[["canal", "montant", "ecart_moy_canal"]].head(4).round(1))
print("moyenne des écarts nulle dans chaque canal :", bool(np.allclose(df.groupby("canal")["ecart_moy_canal"].mean(), 0)))
```
<!--sortie-->
```text
       canal  montant  ecart_moy_canal
0       Site     49.9             -9.6
1  Instagram     21.5            -27.5
2   Boutique     34.2            -40.6
3       Site    103.0             43.5
moyenne des écarts nulle dans chaque canal : True
```

> ✅ **À retenir (`groupby`).** `df.groupby(clé)[colonne].fonction()` : *découper, appliquer, combiner*. `agg` pour plusieurs résumés, `size` pour compter les lignes, `transform` pour ré-aligner un résultat de groupe sur chaque ligne, `pivot_table` et `crosstab` pour des tableaux croisés.

### 4.4.10 Combiner plusieurs tables : `merge` et `concat`

Dans la vraie vie, l'information est **répartie sur plusieurs tables** : la liste des commandes d'un côté, celle des clients de l'autre (nous verrons au chapitre 5 pourquoi, et comment SQL fait la même chose avec `JOIN`). Le travail s'appelle une **jointure** : on associe les lignes qui partagent la même **clé**.

Créons la table des clients : 125 clients, chacun avec une ville. (Les clients 121 à 125 n'ont, par construction, jamais commandé ; comme les commandes ont été attribuées au hasard à des clients de 1 à 120, quelques autres clients n'auront rien commandé non plus. Cela nous servira.)

```python
rng_c = np.random.default_rng(11)
clients = pd.DataFrame({
    "id_client": np.arange(1, 126),
    "ville": rng_c.choice(["Tunis", "Sfax", "Sousse", "Nabeul", "Bizerte"], size=125, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
})
print(clients.head(3))
print("clients :", len(clients), "| commandes :", len(df))
```
<!--sortie-->
```text
   id_client   ville
0          1   Tunis
1          2    Sfax
2          3  Sousse
clients : 125 | commandes : 400
```

Voici d'abord un exemple minuscule pour comprendre les types de jointure. Deux commandes (clients 1 et 9) et deux fiches clients (1 et 2) :

```python
cmd = pd.DataFrame({"id_client": [1, 9], "montant": [50, 80]})
fiche = pd.DataFrame({"id_client": [1, 2], "ville": ["Tunis", "Sfax"]})
for how in ["inner", "left", "outer"]:
    print(f"--- how='{how}'")
    print(cmd.merge(fiche, on="id_client", how=how))
```
<!--sortie-->
```text
--- how='inner'
   id_client  montant  ville
0          1       50  Tunis
--- how='left'
   id_client  montant  ville
0          1       50  Tunis
1          9       80    NaN
--- how='outer'
   id_client  montant  ville
0          1     50.0  Tunis
1          2      NaN   Sfax
2          9     80.0    NaN
```

- **`inner`** : seulement les clés présentes **des deux côtés** (client 1) ;
- **`left`** : toutes les lignes de la table de gauche ; on met `NaN` (valeur manquante) quand il n'y a pas de correspondance (client 9 sans fiche) ;
- **`outer`** : tout ce qui existe d'un côté **ou** de l'autre.

> 💡 **Quel `how` choisir ?** Dans 90 % des cas : `left`, avec votre table « principale » (les commandes) à gauche. On garde alors *toutes* les commandes et on y ajoute des informations, sans en perdre en route. Et on **vérifie** toujours le nombre de lignes avant/après.

Sur nos données :

```python
cmd_ville = df.merge(clients, on="id_client", how="left")
print("lignes avant/après la jointure :", len(df), len(cmd_ville))
print("commandes sans ville connue    :", int(cmd_ville["ville"].isna().sum()))
print()
print(cmd_ville.groupby("ville")["montant"].agg(["count", "mean"]).round(1).sort_values("count", ascending=False))
```
<!--sortie-->
```text
lignes avant/après la jointure : 400 400
commandes sans ville connue    : 0

         count  mean
ville               
Tunis      176  59.6
Sousse      92  59.7
Sfax        71  63.6
Nabeul      42  56.0
Bizerte     19  65.5
```

Quels sont les clients qui n'ont **jamais** commandé ? `indicator=True` ajoute une colonne `_merge` qui dit d'où vient chaque ligne (`both` : présent des deux côtés ; `left_only` : seulement dans la table de gauche) :

```python
test = clients.merge(df[["id_client"]].drop_duplicates(), on="id_client", how="left", indicator=True)
print(test["_merge"].value_counts())
print("sans commande :", test.loc[test["_merge"] == "left_only", "id_client"].tolist())
```
<!--sortie-->
```text
_merge
both          114
left_only      11
right_only      0
Name: count, dtype: int64
sans commande : [1, 6, 43, 50, 67, 84, 121, 122, 123, 124, 125]
```

Onze clients n'ont jamais commandé : les cinq prévus (121 à 125) et six clients de la plage 1 à 120 que le hasard n'a pas tirés (1, 6, 43, 50, 67 et 84). Le comptage `both` (114) + `left_only` (11) retombe bien sur nos 125 clients.

> ⚠️ **Le piège n°1 des jointures : l'explosion du nombre de lignes.** Si la clé est **dupliquée** dans la table de droite, chaque ligne de gauche est recopiée autant de fois. Imaginez que la fiche du client 1 ait été saisie deux fois : sa commande apparaîtrait en double, et le chiffre d'affaires serait faux sans qu'aucune erreur ne soit signalée. Le paramètre **`validate`** déclenche une erreur dans ce cas : `"m:1"` signifie « plusieurs lignes à gauche pour une seule à droite ».

```python
fiche_doublon = pd.DataFrame({"id_client": [1, 1], "ville": ["Tunis", "Tunis"]})
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

Pour **empiler** des tables de même structure (les commandes de janvier et celles de février, par exemple), on utilise `concat` :

```python
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

Dans les données réelles, il manque toujours quelque chose : un client n'a pas laissé de note, un capteur est tombé en panne, une case n'a pas été remplie. pandas représente ces trous par **`NaN`** (*not a number*) pour les nombres, et par `NaT` pour les dates. Créons une copie de nos données où 30 notes de satisfaction sont perdues :

```python
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
Boutique      7
Instagram    10
Site         13
Name: satisfaction, dtype: int64
```

D'abord, **comment les calculs se comportent-ils ?** Sur un exemple à la main : les notes `4, 5, NaN, 3` ont pour moyenne $(4+5+3)/3=4$ (pandas **ignore** le `NaN`, il ne le compte pas comme 0 ; sinon on trouverait $12/4=3$).

```python
notes = pd.Series([4, 5, np.nan, 3])
print("moyenne :", notes.mean(), "| effectif :", notes.count(), "| taille :", len(notes))
print("somme avec skipna=False :", notes.sum(skipna=False))     # un seul NaN contamine la somme
```
<!--sortie-->
```text
moyenne : 4.0 | effectif : 3 | taille : 4
somme avec skipna=False : nan
```

> ⚠️ **Piège.** Comparer avec `==` ne détecte pas un `NaN` (`NaN == NaN` est faux, par convention). Utilisez **`isna()`** / `notna()`.

Que faire des trous ? Trois stratégies, à choisir selon le contexte :

```python
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
print(df["date"].min(), "->", df["date"].max())
print("durée couverte :", df["date"].max() - df["date"].min())
df["jour_semaine"] = df["date"].dt.dayofweek          # 0 = lundi … 6 = dimanche
df["mois"] = df["date"].dt.month
print(df[["date", "jour_semaine", "mois"]].head(4))
```
<!--sortie-->
```text
2026-01-05 00:00:00 -> 2026-05-24 00:00:00
durée couverte : 139 days 00:00:00
        date  jour_semaine  mois
0 2026-01-05             0     1
1 2026-01-05             0     1
2 2026-01-05             0     1
3 2026-01-05             0     1
```

Si vos dates sont lues comme du **texte** (cas fréquent à l'import d'un fichier), on les convertit avec `pd.to_datetime`, en précisant le format pour éviter l'ambiguïté jour/mois :

```python
textes = pd.Series(["05/01/2026", "12/01/2026", "03/02/2026"])
dates = pd.to_datetime(textes, format="%d/%m/%Y")
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
print("nombre de semaines distinctes :", df["semaine"].nunique())
```
<!--sortie-->
```text
        date    semaine
0 2026-01-05 2026-01-05
1 2026-01-05 2026-01-05
2 2026-01-05 2026-01-05
nombre de semaines distinctes : 20
```

> 🧪 **Vérifions sur un exemple.** Le 5 janvier 2026 est un lundi : la semaine du 5 au 11 janvier est donc repérée par le **5 janvier**. Une commande du jeudi 8 janvier doit avoir pour semaine le 5 janvier ; une commande du lundi 12 janvier, le 12.

```python
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

### 4.4.13 🛠️ Petite application : le rapport hebdomadaire de Yasmine

Rassemblons tout ce que nous venons d'apprendre dans une vraie **mini-application** : un petit programme qui produit, pour une semaine donnée, le rapport que Yasmine lit chaque lundi. D'abord le **tableau de bord hebdomadaire** : une ligne par semaine.

```python
hebdo = df.groupby("semaine").agg(
    commandes=("montant", "count"),
    ca=("montant", "sum"),
    panier_moyen=("montant", "mean"),
    part_instagram=("canal", lambda s: (s == "Instagram").mean()),
).round(2)
hebdo["ca_lisse"] = hebdo["ca"].rolling(4).mean().round(1)       # moyenne mobile sur 4 semaines
print(hebdo.head(6))
print("...")
print(hebdo.tail(3))
```
<!--sortie-->
```text
            commandes      ca  panier_moyen  part_instagram  ca_lisse
semaine                                                              
2026-01-05         20  1082.4         54.12            0.25       NaN
2026-01-12         19  1083.0         57.00            0.53       NaN
2026-01-19         18  1403.0         77.94            0.22       NaN
2026-01-26         20   750.7         37.54            0.40    1079.8
2026-02-02         21  1447.6         68.93            0.33    1171.1
2026-02-09         14   975.8         69.70            0.21    1144.3
...
            commandes      ca  panier_moyen  part_instagram  ca_lisse
semaine                                                              
2026-05-04         20  1482.8         74.14            0.35    1162.0
2026-05-11         23  1306.3         56.80            0.39    1225.5
2026-05-18         27  1585.4         58.72            0.37    1433.7
```

(La fonction anonyme `lambda s: (s == "Instagram").mean()` calcule, dans chaque semaine, la proportion de commandes Instagram, grâce à l'astuce « moyenne d'un masque » vue en 4.4.4.) Puis une **fonction** qui rédige le rapport d'une semaine :

```python
def rapport_hebdo(df, debut):
    """Rapport de la semaine commençant le lundi `debut` (texte 'AAAA-MM-JJ')."""
    debut = pd.Timestamp(debut)
    sem = df[df["semaine"] == debut]
    if sem.empty:
        return f"Aucune commande la semaine du {debut:%d/%m/%Y}."
    precedente = df[df["semaine"] == debut - pd.Timedelta(weeks=1)]
    ca, ca_prec = sem["montant"].sum(), precedente["montant"].sum()
    par_canal = sem.groupby("canal")["montant"].sum().sort_values(ascending=False)
    top = sem.groupby("id_client")["montant"].sum().nlargest(3)

    lignes = [f"Semaine du {debut:%d/%m/%Y}",
              f"  commandes : {len(sem)}   |   panier moyen : {sem['montant'].mean():.2f} DT",
              f"  chiffre d'affaires : {ca:.2f} DT"]
    if ca_prec > 0:
        lignes[-1] += f"  ({(ca / ca_prec - 1) * 100:+.1f} % vs semaine précédente)"
    lignes.append("  par canal : " + ", ".join(f"{c} {v:.0f} DT" for c, v in par_canal.items()))
    lignes.append("  meilleurs clients : " + ", ".join(f"n°{i} ({v:.0f} DT)" for i, v in top.items()))
    note = sem["satisfaction"].mean()
    lignes.append(f"  satisfaction moyenne : {note:.2f}/5" + ("   ⚠ à surveiller" if note < 3.5 else ""))
    return "\n".join(lignes)


print(rapport_hebdo(df, "2026-03-02"))
print()
print(rapport_hebdo(df, "2026-05-18"))
print()
print(rapport_hebdo(df, "2025-01-06"))      # une semaine sans données

# contrôle croisé : le rapport et le tableau hebdomadaire doivent donner les mêmes nombres
print(hebdo.loc["2026-03-02", ["commandes", "ca"]].tolist())
```
<!--sortie-->
```text
Semaine du 02/03/2026
  commandes : 23   |   panier moyen : 72.96 DT
  chiffre d'affaires : 1678.00 DT  (+59.4 % vs semaine précédente)
  par canal : Site 707 DT, Boutique 502 DT, Instagram 469 DT
  meilleurs clients : n°42 (189 DT), n°7 (170 DT), n°83 (160 DT)
  satisfaction moyenne : 3.78/5

Semaine du 18/05/2026
  commandes : 27   |   panier moyen : 58.72 DT
  chiffre d'affaires : 1585.40 DT  (+21.4 % vs semaine précédente)
  par canal : Site 682 DT, Instagram 465 DT, Boutique 438 DT
  meilleurs clients : n°9 (256 DT), n°22 (237 DT), n°93 (146 DT)
  satisfaction moyenne : 3.85/5

Aucune commande la semaine du 06/01/2025.
[23.0, 1678.0]
```

Le contrôle croisé final confirme que le rapport et le tableau hebdomadaire disent la même chose (23 commandes et 1 678 DT pour la semaine du 2 mars). Ce petit programme utilise presque tout : filtrage, `groupby`, tri, dates, formatage. Il est surtout **réutilisable** : la semaine prochaine, Yasmine changera la date et obtiendra le nouveau rapport sans rien refaire. C'est ce qui sépare une analyse « à la souris » d'une analyse reproductible.

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
> *Pour s'entraîner :* les exercices de la section 4.9 reprennent ces notions.


## 4.5 Premières visualisations

> 💡 **Intuition.** Un tableau de 400 lignes, personne ne le « lit » vraiment ; un graphique bien choisi, on le comprend en trois secondes. Au 3.1 nous avons vu avec le quartet d'Anscombe que des données très différentes peuvent avoir **les mêmes statistiques** : seul le dessin révèle la différence. Visualiser n'est donc pas de la décoration, c'est un **outil de réflexion** (on dessine pour *comprendre*) et un **outil de communication** (on dessine pour *convaincre* sans tromper).
>
> Cette section a trois objectifs : savoir **quel graphique choisir** selon la question (4.5.1), savoir **le tracer** avec les trois bibliothèques les plus utilisées (matplotlib et pandas, seaborn, puis ggplot2 en R : 4.5.2 à 4.5.5), et savoir **éviter les graphiques trompeurs** (4.5.6).

> 🧭 **Pour la suite du livre.** Nous ne ferons ici que les graphiques fondamentaux. Les graphiques interactifs, les cartes ou les tableaux de bord complets sont abordés dans la série Data Analyst.

Pour être autonome, cette section recharge les données de 4.4 (même graine, mêmes résultats) et règle l'apparence des figures du livre : traits fins, grille discrète, pas de cadre inutile.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BLEU, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"     # la palette du livre
COULEURS = {"Instagram": BLEU, "Site": ORANGE, "Boutique": AQUA}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6,
    "axes.titlesize": 11, "axes.labelcolor": "#52514e", "legend.frameon": False,
})

# le jeu de données de 4.4 (identique : mêmes graines)
df = pd.read_csv("donnees/commandes.csv")
rng = np.random.default_rng(7)
jours = rng.integers(0, 140, size=len(df))
df["date"] = pd.Timestamp("2026-01-05") + pd.to_timedelta(jours, unit="D")
df["id_client"] = rng.integers(1, 121, size=len(df))
df = df.sort_values("date").reset_index(drop=True)
df["semaine"] = df["date"].dt.to_period("W").dt.start_time
hebdo = df.groupby("semaine").agg(commandes=("montant", "count"), ca=("montant", "sum"))
print(df.shape, "|", len(hebdo), "semaines | CA total :", round(df["montant"].sum(), 1), "DT")
```
<!--sortie-->
```text
(400, 7) | 20 semaines | CA total : 24098.3 DT
```

### 4.5.1 Quel graphique pour quelle question ?

La première erreur du débutant est de commencer par se demander « quel joli graphique ? ». La bonne démarche est inverse : on part de la **question**, puis du **type des variables** (revoyez le tableau du 3.1.1), et le graphique s'impose presque tout seul.

| La question | Les variables | Le graphique | Pourquoi |
|---|---|---|---|
| Comment se répartissent les montants ? | 1 quantitative | **histogramme** (ou boîte à moustaches) | montre la forme : symétrie, queue, valeurs atypiques |
| Quelle part de chaque canal ? | 1 qualitative | **diagramme en barres** (trié) | on compare des longueurs alignées, ce que l'œil fait très bien |
| Quel canal vend le plus ? | 1 qualitative + 1 quantitative | **barres** (une valeur par groupe) ou **boîtes à moustaches** (toute la distribution) | comparer des groupes |
| Comment évolue le chiffre d'affaires ? | 1 quantitative + le temps | **courbe** | la ligne relie les points : on voit la tendance |
| Les retards de livraison font-ils baisser la satisfaction ? | 2 quantitatives | **nuage de points** | montre la forme de la relation, pas seulement un nombre |
| Comment se croisent deux variables qualitatives ? | 2 qualitatives | **carte de chaleur** (*heatmap*) d'un tableau croisé | couleur = fréquence |

> 💡 **Trois questions avant de tracer.** (1) *Quel message* veux-je faire passer en une phrase ? (2) *Quelles variables* sont en jeu, et de quel type ? (3) *Qui va lire* ce graphique, en combien de temps ? Un graphique pour votre propre exploration peut être brouillon ; un graphique pour un patron pressé doit contenir **un message et un seul**.

> ⚠️ **Et le camembert ?** Il est partout, mais il est un mauvais choix dès qu'il y a plus de trois parts : l'œil compare mal des angles et des aires, bien mieux des **longueurs**. Pour montrer 3 canaux, un camembert est acceptable ; pour 8 produits, des barres triées sont toujours plus lisibles. (Les camemberts « en 3D » sont à proscrire absolument, voir 4.5.6.)

### 4.5.2 Anatomie d'un graphique matplotlib

**matplotlib** est la bibliothèque de base de la visualisation en Python : presque toutes les autres (pandas, seaborn…) s'appuient dessus. Elle est très complète, donc un peu intimidante ; comprendre sa structure suffit à s'y retrouver.

![Les pièces d'un graphique matplotlib : la Figure (la page entière), l'Axes (le repère, cadre pointillé), puis les éléments dessinés dedans.](figures/ch04-anatomie.png)

- La **Figure** est la page entière (sa taille se règle avec `figsize=(largeur, hauteur)` en pouces).
- L'**Axes** (au pluriel malgré les apparences : c'est *un* repère) est la zone où l'on dessine. Une figure peut en contenir un seul ou plusieurs (une grille 2×2, par exemple).
- Dans un Axes vivent des **objets** : lignes, barres, points, textes, légende, graduations, grille.

Il existe deux manières de s'en servir. L'interface « état » (`plt.plot(...)`) agit sur « le graphique courant » : très courte, mais confuse dès qu'il y a plusieurs panneaux. L'interface **orientée objet** crée explicitement la figure et l'axes, puis envoie des commandes à *l'axes* : c'est celle que nous utiliserons toujours, car elle ne laisse aucune ambiguïté sur « où » l'on dessine.

```python
fig, ax = plt.subplots(figsize=(7, 3.6))              # une figure contenant un seul Axes
ax.plot(hebdo.index, hebdo["ca"], marker="o", ms=4, color=BLEU)
ax.set_title("Chiffre d'affaires hebdomadaire de Dar Jasmin")
ax.set_xlabel("semaine (lundi)")
ax.set_ylabel("chiffre d'affaires (DT)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))   # dates au format jour/mois
fig.autofmt_xdate()                                    # incline les dates si nécessaire
fig.savefig("figures/ch04-premier-graphique.png", dpi=150, bbox_inches="tight")
plt.close(fig)                                         # libère la mémoire
print("figure enregistrée :", "semaine la plus forte =", hebdo["ca"].idxmax().date(), f"({hebdo['ca'].max():.0f} DT)")
```
<!--sortie-->
```text
figure enregistrée : semaine la plus forte = 2026-03-23 (1737 DT)
```

![Notre premier graphique : une courbe du chiffre d'affaires par semaine.](figures/ch04-premier-graphique.png)

Tout y est : un **titre**, des **axes nommés avec leur unité**, une ligne avec des **marqueurs** (un point par semaine, pour ne pas laisser croire que l'on connaît les valeurs entre les semaines). La courbe est irrégulière d'une semaine à l'autre, ce qui est normal : chaque semaine ne compte qu'entre 14 et 27 commandes, donc quelques gros paniers suffisent à faire bondir le total. Pour voir la **tendance**, on lisse avec une moyenne mobile, que nous ajouterons en 4.5.3.

> 🛠️ **Le patron de tous les graphiques matplotlib.** (1) `fig, ax = plt.subplots(...)` ; (2) `ax.plot / ax.bar / ax.hist / ax.scatter(...)` ; (3) `ax.set_title / set_xlabel / set_ylabel` ; (4) `fig.savefig(...)`. Pour *plusieurs* panneaux : `fig, axes = plt.subplots(2, 2)` renvoie un tableau d'Axes que l'on indexe `axes[0, 0]`, `axes[0, 1]`, etc. (c'est un tableau NumPy, voir 4.4.2).

### 4.5.3 Les quatre graphiques essentiels, avec pandas

pandas offre une méthode `.plot` sur ses Series et DataFrames, qui appelle matplotlib en coulisses et **renvoie l'Axes** : on peut donc la combiner avec tout ce qui précède, en lui passant l'argument `ax=`. Voici les quatre graphiques que vous tracerez le plus souvent, dans une seule figure à quatre panneaux :

1. **histogramme** des montants ;
2. **barres horizontales** du chiffre d'affaires par canal (triées) ;
3. **courbe** du chiffre d'affaires hebdomadaire avec sa moyenne mobile ;
4. **nuage de points** livraison/satisfaction.

Pour le quatrième, un détail d'importance. La livraison est un nombre entier de jours et la satisfaction une note entière de 1 à 5 : beaucoup de commandes tombent *exactement au même point*, et un nuage de points normal en cacherait la plupart. On les **décale aléatoirement d'un tout petit peu** (« jitter », en français *jitter* ou *bruitage*) et on rend les points translucides : les zones denses apparaissent plus foncées.

```python
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2))
fig.subplots_adjust(hspace=0.38, wspace=0.28)

# 1. histogramme (pandas)
ax = axes[0, 0]
df["montant"].plot.hist(bins=30, ax=ax, color=BLEU, alpha=0.7, edgecolor="white")
ax.axvline(df["montant"].median(), color=ORANGE, ls="--", lw=2)
ax.text(df["montant"].median() + 5, ax.get_ylim()[1] * 0.9, "médiane", color=ORANGE)
ax.set(title="Histogramme : la distribution des montants", xlabel="montant d'une commande (DT)", ylabel="nombre de commandes")

# 2. barres horizontales, triées (pandas)
ax = axes[0, 1]
ca_canal = df.groupby("canal")["montant"].sum().sort_values()
ca_canal.plot.barh(ax=ax, color=[COULEURS[c] for c in ca_canal.index], alpha=0.8)
for i, v in enumerate(ca_canal):
    ax.text(v + 80, i, f"{v:,.0f} DT".replace(",", " "), va="center")
ax.set(title="Barres : le chiffre d'affaires par canal", xlabel="chiffre d'affaires (DT)", ylabel="", xlim=(0, ca_canal.max() * 1.2))
ax.grid(axis="y", visible=False)

# 3. courbe + moyenne mobile (pandas)
ax = axes[1, 0]
hebdo["ca"].plot(ax=ax, color=BLEU, alpha=0.45, marker="o", ms=3, label="une semaine")
hebdo["ca"].rolling(4).mean().plot(ax=ax, color=ORANGE, lw=2.5, label="moyenne mobile sur 4 semaines")
ax.set_ylim(top=2100)                                   # on laisse de la place en haut pour la légende
ax.legend(loc="upper left")
ax.set(title="Courbe : l'évolution dans le temps", xlabel="semaine", ylabel="chiffre d'affaires (DT)")

# 4. nuage de points avec jitter (matplotlib)
ax = axes[1, 1]
bruit = np.random.default_rng(5)
x = df["livraison"] + bruit.uniform(-0.25, 0.25, len(df))
y = df["satisfaction"] + bruit.uniform(-0.25, 0.25, len(df))
ax.scatter(x, y, s=14, alpha=0.35, color=VIOLET, edgecolors="none")
ax.set_yticks(range(1, 6))
ax.set(title="Nuage de points : livraison et satisfaction", xlabel="délai de livraison (jours)", ylabel="note de satisfaction")

fig.savefig("figures/ch04-essentiels.png", dpi=150, bbox_inches="tight")
plt.close(fig)
r = df[["livraison", "satisfaction"]].corr().iloc[0, 1]
print("corrélation livraison / satisfaction :", round(r, 2))
print("part du CA du canal en tête :", f"{ca_canal.iloc[-1] / ca_canal.sum():.0%}")
```
<!--sortie-->
```text
corrélation livraison / satisfaction : -0.53
part du CA du canal en tête : 37%
```

![Les quatre graphiques essentiels : histogramme, barres triées, courbe avec moyenne mobile, nuage de points « bruité ».](figures/ch04-essentiels.png)

**Comment lire chaque panneau** (c'est aussi comme cela qu'on doit *légender* un graphique dans un rapport) :

- **Histogramme** : la forme est asymétrique à droite, avec une longue queue de grosses commandes ; la médiane (trait orange, 51 DT) est nettement sous la moyenne (60 DT), tirée vers le haut par les grosses commandes (revoir 3.1.5).
- **Barres** : on lit au premier coup d'œil l'ordre des canaux, et les valeurs sont écrites au bout des barres : plus besoin de deviner sur l'axe. Les barres sont **triées** : un classement doit être lisible.
- **Courbe** : le trait pâle est le chiffre d'affaires de chaque semaine, très irrégulier ; le trait orange, plus lisse, montre la **tendance**.
- **Nuage de points** : plus le délai augmente, plus les notes basses apparaissent ; la corrélation affichée (−0,53) est négative et d'intensité moyenne : un retard fait *tendanciellement* baisser la note, sans que ce soit une règle absolue (beaucoup de commandes tardives ont quand même 4).

> 🧪 **Pourquoi `.plot` renvoie-t-il l'Axes ?** Parce que ainsi tout est modifiable après coup : titre, limites, annotations. Si vous écrivez `ax = df["montant"].plot.hist()`, vous pouvez ensuite faire `ax.set_title(...)`. pandas propose aussi `.plot.bar()`, `.plot.line()`, `.plot.box()`, `.plot.scatter(x=, y=)`, `.plot.pie()`, `.plot.area()`… Pour l'exploration rapide, c'est imbattable (une ligne par graphique).

### 4.5.4 seaborn : des graphiques statistiques en une ligne

**seaborn** est une couche au-dessus de matplotlib spécialisée dans les graphiques **statistiques**. Son atout : on lui donne le **tableau complet** (`data=df`) et on dit quelle colonne va où (`x=`, `y=`, `hue=` pour la couleur), et seaborn s'occupe des regroupements, des légendes et des couleurs.

Deux exemples. D'abord la distribution des montants **selon le canal**, en histogramme et en boîte à moustaches :

```python
import seaborn as sns

sns.set_theme(style="whitegrid", rc={"axes.spines.top": False, "axes.spines.right": False})
ordre = ["Instagram", "Site", "Boutique"]

fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.25})
sns.histplot(data=df, x="montant", hue="canal", hue_order=ordre, palette=COULEURS, bins=30,
             element="step", alpha=0.3, ax=axes[0])
axes[0].set(title="Histogrammes superposés selon le canal", xlabel="montant (DT)", ylabel="nombre de commandes")

sns.boxplot(data=df, x="canal", y="montant", order=ordre, hue="canal", palette=COULEURS, legend=False,
            width=0.55, fliersize=3, ax=axes[1])
axes[1].set(title="Boîtes à moustaches selon le canal", xlabel="", ylabel="montant (DT)")

fig.savefig("figures/ch04-seaborn-distributions.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(df.groupby("canal")["montant"].median().reindex(ordre).round(1).to_string())
```
<!--sortie-->
```text
canal
Instagram    41.5
Site         49.5
Boutique     64.8
```

![Avec seaborn, une ligne suffit pour séparer les données par canal : histogrammes superposés et boîtes à moustaches.](figures/ch04-seaborn-distributions.png)

Les médianes imprimées confirment la lecture : 64,8 DT pour la boutique, 49,5 DT pour le site, 41,5 DT pour Instagram. (Cette différence est-elle réelle ou due au hasard ? C'est la question d'un test statistique, 3.4.)

Deuxième exemple : une **carte de chaleur** pour le croisement de deux variables qualitatives, le canal et la note de satisfaction. On calcule d'abord le tableau croisé (en proportions par canal), puis on le colore :

```python
tab = pd.crosstab(df["canal"], df["satisfaction"], normalize="index").loc[ordre]
print(tab.round(2))

fig, ax = plt.subplots(figsize=(6.5, 3))
sns.heatmap(tab, annot=True, fmt=".0%", cmap="Blues", cbar=False, linewidths=2, linecolor="white", ax=ax)
ax.set(title="Part de chaque note, selon le canal", xlabel="note de satisfaction", ylabel="")
fig.savefig("figures/ch04-seaborn-heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```
<!--sortie-->
```text
satisfaction     1     2     3     4     5
canal                                     
Instagram     0.00  0.06  0.31  0.49  0.14
Site          0.01  0.05  0.25  0.54  0.16
Boutique      0.00  0.00  0.04  0.42  0.54
```

![Carte de chaleur : chaque ligne (canal) somme à 100 %. Plus la case est foncée, plus la note est fréquente dans ce canal.](figures/ch04-seaborn-heatmap.png)

Chaque ligne du tableau somme à 1 (donc 100 %) : on lit « *parmi* les commandes de la boutique, 54 % ont donné la note 5 » (contre 14 % pour Instagram et 16 % pour le Site). La case la plus foncée de la ligne Boutique est à droite (la note 5), celles d'Instagram et du Site sont sur la note 4, avec une part importante de 3 : la boutique, où la livraison est immédiate, a les clients les plus satisfaits.

> 💡 **matplotlib, pandas ou seaborn ?** Ce n'est pas un choix exclusif : seaborn et pandas **dessinent dans des Axes matplotlib**, que l'on peut retoucher avec les méthodes de 4.5.2. Règle pratique : pandas `.plot` pour regarder vite, seaborn pour les graphiques statistiques avec groupes, matplotlib pour tout ce qui doit être personnalisé au pixel près.

### 4.5.5 ggplot2 : la grammaire des graphiques en R

En R, la bibliothèque de référence est **ggplot2**. Son idée, la « **grammaire des graphiques** » (*grammar of graphics*), est de **décrire** un graphique par couches plutôt que de le dessiner pas à pas :

- les **données** (`ggplot(data, ...)`) ;
- une **correspondance esthétique** `aes(x=, y=, fill=)` : quelle colonne va sur quel axe ou dans quelle couleur ;
- une ou plusieurs **géométries** `geom_...()` : histogramme, barres, points, lignes ;
- éventuellement des **facettes** (`facet_wrap`) pour faire un panneau par groupe, des **échelles** et un **thème**.

On additionne ces couches avec le signe `+`. Reproduisons l'histogramme par canal ; R lit le même fichier CSV (les bases du langage R sont présentées en 4.2) :

```r
library(ggplot2)
commandes <- read.csv("donnees/commandes.csv")
commandes$canal <- factor(commandes$canal, levels = c("Instagram", "Site", "Boutique"))
print(aggregate(montant ~ canal, data = commandes, FUN = function(x) round(median(x), 1)))

p <- ggplot(commandes, aes(x = montant, fill = canal)) +
  geom_histogram(bins = 30, alpha = 0.8, colour = "white") +
  facet_wrap(~ canal, ncol = 1) +
  scale_fill_manual(values = c(Instagram = "#2a78d6", Site = "#eb6834", Boutique = "#1baf7a")) +
  labs(title = "Distribution des montants selon le canal", x = "montant (DT)", y = "nombre de commandes") +
  theme_minimal(base_size = 11) +
  theme(legend.position = "none")
ggsave("figures/ch04-ggplot-montants.png", plot = p, width = 7, height = 5, dpi = 150)
cat("figure enregistrée\n")
```
<!--sortie-->
```text
      canal montant
1 Instagram    41.5
2      Site    49.5
3  Boutique    64.8
figure enregistrée
```

![Le même type de graphique avec ggplot2 : un panneau par canal (facettes), même échelle horizontale.](figures/ch04-ggplot-montants.png)

On retrouve les mêmes médianes qu'en Python (confirmant que les deux outils lisent bien les mêmes données). Le tableau suivant résume la différence de philosophie :

| | matplotlib / seaborn (Python) | ggplot2 (R) |
|---|---|---|
| Style | **impératif** : on construit pas à pas (figure → axes → éléments) | **déclaratif** : on décrit le résultat par couches |
| Séparer par groupe | `hue=` (seaborn) ou une boucle sur les groupes | `fill=`, `colour=`, ou `facet_wrap()` |
| Personnalisation fine | très grande, mais verbeuse | grande, via `theme()` et `scale_*()` |
| Combiner plusieurs couches | appels successifs sur le même `ax` | `+ geom_...()` |

> 🧪 **Honnêteté d'exécution.** Les graphiques de cette section ont tous été produits par le code affiché (sauf trois dessins explicatifs, produits par `build/fig_ch04.py` : l'anatomie d'une figure, le broadcasting et l'axe tronqué) ; le bloc R ci-dessus a bien été exécuté (R avec ggplot2). Les versions de bibliothèques peuvent légèrement modifier l'aspect (polices, marges) sans changer l'information.

### 4.5.6 Bien faire, mal faire : les pièges du graphique trompeur

Un graphique peut mentir sans qu'une seule donnée soit fausse. Voici les six pièges les plus répandus. Le premier mérite une démonstration.

**Piège n°1 : l'axe tronqué.** Comparons la satisfaction moyenne d'Instagram et du Site. Les deux graphiques ci-dessous montrent **exactement les mêmes deux nombres**.

```python
moy = df[df["canal"].isin(["Instagram", "Site"])].groupby("canal")["satisfaction"].mean()
insta, site = moy["Instagram"], moy["Site"]
print("moyennes :", round(insta, 2), "et", round(site, 2))
print("écart réel : +", round((site / insta - 1) * 100, 1), "%")
print("barre du Site / barre d'Instagram si l'axe commence à 3,70 :", round((site - 3.70) / (insta - 3.70), 1), "fois plus haute")
```
<!--sortie-->
```text
moyennes : 3.72 et 3.79
écart réel : + 2.0 %
barre du Site / barre d'Instagram si l'axe commence à 3,70 : 5.2 fois plus haute
```

![Mêmes données, deux impressions opposées : à gauche l'axe commence à 3,70, à droite à 0.](figures/ch04-axe-tronque.png)

À gauche, avec un axe qui commence à 3,70, la barre du Site paraît **plus de 5 fois plus haute** que celle d'Instagram (c'est le « 5,2 fois » imprimé ci-dessus) ; à droite, sur un axe complet, les deux barres sont quasiment identiques, ce qui correspond bien à l'écart réel de 2 %. **Règle : pour un diagramme en barres, l'axe doit commencer à 0**, car c'est la *longueur* de la barre qui porte l'information. (Pour une courbe ou un nuage de points, c'est la position qui compte : on peut zoomer, à condition de le signaler.)

**Les autres pièges, et leurs remèdes :**

| Piège | Pourquoi c'est un problème | Remède |
|---|---|---|
| **Camembert en 3D, ou à beaucoup de parts** | la perspective déforme les aires ; l'œil compare mal les angles | barres triées, en 2D |
| **Double axe vertical** | on peut rendre n'importe quelle corrélation « visible » en choisissant les échelles | deux graphiques superposés, ou un seul axe |
| **Trop de couleurs** | 10 couleurs sans ordre : personne ne retient la légende | 3 à 5 couleurs, avec un sens (une couleur = un canal, partout dans le document) |
| **Points superposés** | 400 observations qui se cachent les unes les autres (voir le jitter, 4.5.3) | transparence, bruitage, ou histogramme 2D |
| **Titre vague** (« Graphique 3 ») | le lecteur doit deviner la conclusion | un titre qui **dit** le message : « La boutique a les clients les plus satisfaits » |
| **Axes sans nom ni unité** | « 60 », mais de quoi ? | toujours nommer et donner l'unité (DT, jours, %) |

> ✅ **La liste de contrôle d'un bon graphique.** (1) Un message, un titre qui le dit. (2) Le bon type de graphique pour la question (tableau 4.5.1). (3) Des axes nommés avec leurs unités ; **zéro pour les barres**. (4) Des barres **triées** quand elles représentent un classement. (5) Peu de couleurs, avec un sens constant. (6) Lisible en noir et blanc et pour un daltonien : ne pas reposer sur l'opposition rouge/vert seule. (7) La source des données et la date, si l'on communique à d'autres.

### 4.5.7 Enregistrer, réutiliser : de la figure au rapport

Un graphique n'est utile que s'il sort de votre ordinateur. `fig.savefig(chemin)` choisit le format d'après l'extension, avec trois réglages à connaître :

| Format | Quand l'utiliser |
|---|---|
| **PNG** (`.png`) | pages web, diapositives, e-mails : image « pixels », léger |
| **SVG / PDF** (`.svg`, `.pdf`) | impression, articles, LaTeX : image **vectorielle**, nette à toute taille |
| `dpi=` | résolution en pixels par pouce : **150** pour l'écran, **300** pour l'impression |
| `bbox_inches="tight"` | rogne les marges blanches inutiles |

```python
import os
import tempfile

dossier = tempfile.mkdtemp()
fig, ax = plt.subplots(figsize=(4, 2.5))
ax.bar(ordre, [df[df["canal"] == c]["montant"].sum() for c in ordre], color=[COULEURS[c] for c in ordre])
for ext in ["png", "svg", "pdf"]:
    chemin = os.path.join(dossier, f"exemple.{ext}")
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    print(f".{ext} enregistré, taille non nulle :", os.path.getsize(chemin) > 0)
plt.close(fig)
```
<!--sortie-->
```text
.png enregistré, taille non nulle : True
.svg enregistré, taille non nulle : True
.pdf enregistré, taille non nulle : True
```

> 🛠️ **Application : le tableau de bord de Yasmine.** Mettons tout en commun dans une **fonction** qui produit en une fois la figure que Yasmine joint à son rapport du lundi (celui de 4.4.13). Remarquez que chaque panneau a un **titre qui énonce sa conclusion**, calculée à partir des données (et non écrite à la main) : si les chiffres changent, le titre reste vrai.

```python
def tableau_de_bord(df, chemin):
    """Dessine le tableau de bord de Dar Jasmin à partir du DataFrame `df` et l'enregistre dans `chemin`."""
    ca = df.groupby("semaine")["montant"].sum()
    lisse = ca.rolling(4).mean().dropna()
    par_canal = df.groupby("canal")["montant"].sum().sort_values()
    notes = df["satisfaction"].value_counts().sort_index()
    sens = "monte" if lisse.iloc[-1] > lisse.iloc[0] else "baisse"

    fig = plt.figure(figsize=(10.5, 6.6))
    grille = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.5, wspace=0.3)

    ax = fig.add_subplot(grille[0, :])                              # panneau du haut : toute la largeur
    ax.plot(ca.index, ca.values, color=BLEU, alpha=0.35, marker="o", ms=3)
    ax.plot(lisse.index, lisse.values, color=BLEU, lw=2.5)
    ax.set_title(f"Le chiffre d'affaires hebdomadaire {sens} : de {lisse.iloc[0]:.0f} à {lisse.iloc[-1]:.0f} DT (moyenne mobile)")
    ax.set_ylabel("DT par semaine")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

    ax = fig.add_subplot(grille[1, 0])
    ax.barh(par_canal.index, par_canal.values, color=[COULEURS[c] for c in par_canal.index], alpha=0.85)
    for i, v in enumerate(par_canal):
        ax.text(v + 80, i, f"{v / par_canal.sum():.0%}".replace("%", " %"), va="center")
    ax.set_title(f"{par_canal.index[-1]} : {par_canal.iloc[-1] / par_canal.sum():.0%} du chiffre d'affaires".replace("%", " %"))
    ax.set_xlabel("chiffre d'affaires (DT)")
    ax.set_xlim(0, par_canal.max() * 1.2)
    ax.grid(axis="y", visible=False)

    ax = fig.add_subplot(grille[1, 1])
    ax.bar(notes.index, notes.values, color=[ORANGE if n <= 2 else BLEU for n in notes.index], alpha=0.85)
    ax.set_title(f"{(df['satisfaction'] >= 4).mean():.0%} des clients notent 4 ou 5".replace("%", " %"))
    ax.set_xlabel("note de satisfaction")
    ax.set_ylabel("commandes")
    ax.grid(axis="x", visible=False)

    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return par_canal.index[-1], round(float(lisse.iloc[-1]), 1)


print(tableau_de_bord(df, "figures/ch04-tableau-de-bord.png"))
```
<!--sortie-->
```text
('Site', 1433.7)
```

![Le tableau de bord produit par la fonction : trois panneaux, chacun avec un titre qui énonce sa conclusion.](figures/ch04-tableau-de-bord.png)

Lisons-le comme le ferait Yasmine : la tendance du chiffre d'affaires est à la hausse (1 080 → 1 434 DT par semaine en moyenne mobile), le Site et la Boutique pèsent chacun plus d'un tiers des ventes, et trois clients sur quatre sont satisfaits (4 ou 5). Voilà le chemin complet : des **données brutes** (fichier CSV) aux **tableaux** (pandas, 4.4) puis aux **figures** prêtes à insérer dans un rapport, le tout dans un script que l'on peut relancer chaque semaine. C'est l'esprit de la **recherche reproductible** que nous retrouverons au chapitre 6.

> ✅ **À retenir (visualisation).**
>
> 1. On part de la **question** et du **type des variables**, pas du joli graphique ;
> 2. matplotlib : `fig, ax = plt.subplots()`, on dessine dans l'`ax`, on nomme, on enregistre ; pandas `.plot` et seaborn dessinent dans le même cadre ;
> 3. quatre fondamentaux : histogramme (forme), barres triées (comparaison), courbe (temps), nuage de points (relation) ;
> 4. **barres : l'axe commence à zéro** ; pas de 3D ; peu de couleurs, avec un sens ; titre = message ;
> 5. ggplot2 (R) décrit un graphique par **couches** : données + esthétique + géométrie ;
> 6. **PNG** pour l'écran, **PDF/SVG** pour l'impression ; une fonction de tracé rend l'analyse reproductible.


## 4.6 ➕ Pour aller plus loin : programmation orientée objet, code propre et tests

> 🧭 **Section optionnelle.** Vous pouvez faire toute une carrière d'analyste avec des fonctions, des listes et des tableaux pandas. Mais dès que votre code dépasse quelques dizaines de lignes, ou qu'un collègue (ou vous-même, dans six mois) doit le relire, trois outils changent la vie : **regrouper** les données et les opérations qui vont ensemble (les *objets*), **écrire clairement** (le *code propre*), et **vérifier automatiquement** que le code fait ce qu'on croit (les *tests*). Cette section les présente sur un exemple concret : le panier d'une cliente de Dar Jasmin.

Pour cette section, nous écrivons de vrais **fichiers** Python, puis nous les exécutons depuis un terminal, exactement comme vous le feriez sur votre machine. Les blocs ci-dessous sont donc des commandes du terminal (`bash`) : la commande `cat > fichier <<'FIN' … FIN` crée un fichier avec le texte qui suit, et `python fichier.py` l'exécute. (Le chapitre 6.3 détaille le terminal.)

### 4.6.1 Pourquoi des objets ? Le problème des dictionnaires

> 💡 **Intuition.** Jusqu'ici, un panier pouvait être une simple liste de prix. Mais un panier, ce n'est pas qu'une liste : c'est aussi *« savoir calculer son total, ajouter un article, refuser une quantité négative »*. Un **objet** est un petit paquet qui contient à la fois des **données** (les *attributs*) et les **opérations** qui vont avec (les *méthodes*). Sa **classe** est le moule qui fabrique ces objets, comme un patron de couture fabrique des robes.

Voyons pourquoi cela sert à quelque chose. Voici un panier représenté « à la main » par un dictionnaire, et une fonction qui calcule le total :

```python
panier = {"savon": (20.0, 2), "plateau": (30.0, 1)}      # nom -> (prix HT, quantité)

def total_ht(p):
    return sum(prix * qte for prix, qte in p.values())

print("total HT :", total_ht(panier))
panier["plateau"] = (30.0, -3)                            # une erreur de saisie…
print("total HT :", total_ht(panier), "  <- personne ne nous a prévenus !")
```
<!--sortie-->
```text
total HT : 70.0
total HT : -50.0   <- personne ne nous a prévenus !
```

Rien ne protège le dictionnaire : une quantité négative passe sans bruit, et le total devient faux **sans aucune erreur**. C'est le pire cas possible pour un analyste (un résultat faux qui a l'air normal). Avec une classe, on décide **à un seul endroit** de ce qui est permis.

### 4.6.2 Votre première classe

Commençons par la version « longue », avec une classe ordinaire, pour comprendre les mécanismes :

```bash
cat > article_simple.py <<'FIN'
class Article:
    def __init__(self, nom, prix_ht):      # appelée à la création de l'objet
        self.nom = nom                     # self = l'objet en cours de création
        self.prix_ht = prix_ht

    def prix_ttc(self):                    # une méthode : une fonction de l'objet
        return round(self.prix_ht * 1.19, 2)

savon = Article("savon", 20.0)
print(savon.nom, savon.prix_ht, savon.prix_ttc())
print(savon)                               # affichage par défaut : peu lisible
FIN
python article_simple.py | sed -E 's/0x[0-9a-f]+/0x…/'     # on masque l'adresse mémoire, qui change à chaque exécution
```
<!--sortie-->
```text
savon 20.0 23.8
<__main__.Article object at 0x…>
```

Lisez ligne à ligne :

- `class Article:` définit le moule.
- `__init__` est le **constructeur** : Python l'appelle quand on écrit `Article("savon", 20.0)`. Le premier paramètre, `self`, désigne l'objet qu'on est en train de fabriquer ; on y accroche les attributs (`self.nom`, `self.prix_ht`).
- `prix_ttc` est une **méthode** : on l'appelle avec un point, `savon.prix_ttc()`, et `self` est passé automatiquement.
- Le dernier `print` montre le défaut de cette version : l'affichage `<__main__.Article object at 0x…>` ne dit rien d'utile (et l'adresse change à chaque exécution).

Écrire `__init__` et un affichage lisible pour chaque classe devient vite répétitif. C'est le rôle des **dataclasses** (`@dataclass`) : Python écrit pour vous le constructeur, un affichage lisible et la comparaison `==`.

```bash
cat > article_dc.py <<'FIN'
from dataclasses import dataclass

@dataclass
class Article:
    nom: str
    prix_ht: float

a = Article("savon", 20.0)
b = Article("savon", 20.0)
print(a)                 # affichage lisible, fabriqué automatiquement
print("a == b ?", a == b)
FIN
python article_dc.py
```
<!--sortie-->
```text
Article(nom='savon', prix_ht=20.0)
a == b ? True
```

Deux articles ayant les mêmes attributs sont égaux : c'est ce qu'on attend d'une « valeur ». Deux lignes de déclaration ont remplacé une quinzaine de lignes de code.

### 4.6.3 Le cahier des charges du module

Nous construirons le module de la boutique en 4.6.5, en deux temps : d'abord une fonction de remise, volontairement écrite **trop vite** (c'est l'occasion de découvrir les tests), puis les classes. Mais avant d'écrire du code, posons les règles.

Voici les règles métier, que nous vérifierons **à la main** avant de coder :

- la TVA est de 19 % ;
- un panier de 2 savons à 20 DT et 1 plateau à 30 DT vaut $2\times 20+30=70$ DT hors taxe, soit $70\times1{,}19=83{,}30$ DT TTC ;
- avec une remise de 10 % sur le hors-taxe : $70\times0{,}90=63$ DT HT, soit $63\times1{,}19=74{,}97$ DT TTC ;
- sur le site, la livraison coûte 7 DT, **offerte** si le panier TTC atteint 100 DT ; en boutique, le retrait est gratuit.

### 4.6.4 Code propre : lisible avant tout

> 💡 **Intuition.** Le code est lu bien plus souvent qu'il n'est écrit. L'objectif n'est pas de « faire marcher » un programme, mais de le rendre **compréhensible** par quelqu'un qui n'était pas là quand vous l'avez écrit (y compris vous, dans six mois). Cinq habitudes suffisent pour 90 % du résultat :

1. **Des noms qui parlent.** `total_ttc` plutôt que `t`, `remise` plutôt que `r`. Un nom long et clair vaut mieux qu'un commentaire.
2. **Des fonctions courtes qui font une seule chose.** Si vous devez écrire « et » pour décrire ce que fait une fonction, coupez-la en deux.
3. **Pas de nombres magiques.** Écrivez `TVA = 0.19` une fois en haut du fichier, pas `1.19` à quinze endroits (le jour où le taux change, vous n'en oublierez aucun).
4. **Une docstring** : une phrase entre triples guillemets sous la ligne `def` ou `class`, qui dit *ce que* fait la fonction. Elle s'affiche avec `help(...)`.
5. **Des annotations de type** (`nom: str`, `-> float`) : elles documentent ce que la fonction attend et renvoie.

> ⚠️ **Les annotations de type ne sont pas vérifiées à l'exécution.** Python les lit, mais ne les impose pas. Ce sont des indications pour les humains et pour les outils de vérification (comme `mypy`). Regardez :

```bash
cat > typage.py <<'FIN'
def double(x: int) -> int:
    return x * 2

print(double(21))
print(double("ab"))      # une chaîne n'est pas un entier… et pourtant, aucune erreur
FIN
python typage.py
```
<!--sortie-->
```text
42
abab
```

> ⚠️ **Piège classique : l'argument par défaut modifiable.** Une valeur par défaut comme `[]` est créée **une seule fois**, à la définition de la fonction, puis partagée entre tous les appels. C'est une des erreurs les plus fréquentes en Python :

```bash
cat > piege.py <<'FIN'
def ajouter_mauvais(article, panier=[]):          # MAUVAIS : la liste est partagée
    panier.append(article)
    return panier

def ajouter_bon(article, panier=None):            # BON : on crée la liste à chaque appel
    if panier is None:
        panier = []
    panier.append(article)
    return panier

print("mauvais :", ajouter_mauvais("savon"), ajouter_mauvais("plateau"))
print("bon     :", ajouter_bon("savon"), ajouter_bon("plateau"))
FIN
python piege.py
```
<!--sortie-->
```text
mauvais : ['savon', 'plateau'] ['savon', 'plateau']
bon     : ['savon'] ['plateau']
```

Avec la version fautive, le deuxième panier *contient aussi le savon* du premier : deux clientes se retrouvent avec le même panier. Vous retrouverez ce motif (`None` puis création) dans les dataclasses sous la forme `field(default_factory=list)`.

### 4.6.5 Tester son code : le filet de sécurité

> 💡 **Intuition.** Un **test unitaire** est un petit programme qui appelle une fonction avec des entrées dont **vous connaissez la bonne réponse**, et vérifie qu'elle renvoie bien cette réponse. Vous les écrivez une fois ; ils se rejouent en une seconde après chaque modification. Si un test devient rouge, vous savez *quoi* vous venez de casser, *tout de suite*, et pas un mois plus tard en lisant un rapport faux.

Le schéma universel d'un test s'appelle **Arrange – Act – Assert** : on **prépare** les données (*arrange*), on **exécute** la fonction (*act*), on **vérifie** le résultat (*assert*). Nous utilisons **pytest**, l'outil standard : il suffit d'écrire des fonctions dont le nom commence par `test_` et d'y mettre des `assert`.

**Étape 1 : une fonction de remise, écrite trop vite.**

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    """Prix après une remise de `taux` (0,25 pour 25 %)."""
    return prix - taux
FIN

cat > test_remises.py <<'FIN'
from remises import prix_apres_remise

def test_remise_de_25_pour_cent():
    # 80 DT avec 25 % de remise : 80 * (1 - 0,25) = 60 DT
    assert prix_apres_remise(80.0, 0.25) == 60.0

def test_sans_remise():
    assert prix_apres_remise(80.0, 0.0) == 80.0
FIN

python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
F.                                                                       [100%]
=================================== FAILURES ===================================
_________________________ test_remise_de_25_pour_cent __________________________
test_remises.py:5: in test_remise_de_25_pour_cent
    assert prix_apres_remise(80.0, 0.25) == 60.0
E   assert 79.75 == 60.0
E    +  where 79.75 = prix_apres_remise(80.0, 0.25)
=========================== short test summary info ============================
FAILED test_remises.py::test_remise_de_25_pour_cent - assert 79.75 == 60.0
1 failed, 1 passed
```

Le test a fait son travail : la fonction soustrait le *taux* (0,25 DT !) au lieu d'appliquer le pourcentage. Notez que `test_sans_remise` passe, ce qui montre pourquoi **un seul test ne suffit pas** : un code faux peut réussir un cas particulier. Le message affiche la ligne en cause, la valeur obtenue (79,75) et la valeur attendue (60).

**Étape 2 : on corrige, on relance.**

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    """Prix après une remise de `taux` (0,25 pour 25 %)."""
    if not 0 <= taux <= 1:
        raise ValueError(f"le taux doit être entre 0 et 1, reçu {taux}")
    return prix * (1 - taux)
FIN

python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
..                                                                       [100%]
2 passed
```

Deux tests verts. Remarquez que nous avons aussi ajouté une **validation** : un taux de 25 (au lieu de 0,25) lèverait une erreur claire plutôt que de produire un prix négatif.

> 🛠️ **Un réflexe d'expert : écrire le test *avant* le correctif.** Quand vous découvrez un bogue, écrivez d'abord un test qui l'attrape (il est rouge), puis corrigez le code (il devient vert). Ce bogue ne reviendra jamais sans que quelqu'un le remarque. Cette discipline s'appelle le **développement piloté par les tests** (*TDD*).

**Étape 3 : le module de la boutique.** Les quatre classes, avec docstrings, annotations de types, validation et une constante pour la TVA :

```bash
cat > boutique.py <<'FIN'
"""Modèle objet minimal de la boutique Dar Jasmin."""
from dataclasses import dataclass, field

from remises import prix_apres_remise

TVA = 0.19
SEUIL_LIVRAISON_OFFERTE = 100.0     # DT, panier TTC
FRAIS_LIVRAISON_SITE = 7.0          # DT


@dataclass(frozen=True)             # frozen : on ne peut plus modifier un article créé
class Article:
    """Un article du catalogue : un nom et un prix hors taxe (DT)."""
    nom: str
    prix_ht: float

    def __post_init__(self) -> None:
        if self.prix_ht < 0:
            raise ValueError(f"prix négatif pour {self.nom!r} : {self.prix_ht}")


@dataclass
class Panier:
    """Un panier : des lignes (article, quantité)."""
    lignes: list = field(default_factory=list)

    def ajouter(self, article: Article, quantite: int = 1) -> None:
        if quantite <= 0:
            raise ValueError("la quantité doit être strictement positive")
        self.lignes.append((article, quantite))

    def __len__(self) -> int:           # len(panier) = nombre total d'unités
        return sum(quantite for _, quantite in self.lignes)

    def total_ht(self) -> float:
        return sum(article.prix_ht * quantite for article, quantite in self.lignes)

    def total_ttc(self, remise: float = 0.0) -> float:
        """Total TTC arrondi au centime, après une remise sur le hors-taxe."""
        return round(prix_apres_remise(self.total_ht(), remise) * (1 + TVA), 2)


class Commande:
    """Une commande en boutique : retrait gratuit."""

    def __init__(self, panier: Panier) -> None:
        self.panier = panier

    def frais_livraison(self) -> float:
        return 0.0

    def total_a_payer(self) -> float:
        return round(self.panier.total_ttc() + self.frais_livraison(), 2)


class CommandeSite(Commande):
    """Une commande sur le site : 7 DT de livraison, offerts dès 100 DT TTC."""

    def frais_livraison(self) -> float:
        if self.panier.total_ttc() >= SEUIL_LIVRAISON_OFFERTE:
            return 0.0
        return FRAIS_LIVRAISON_SITE
FIN
echo "module écrit : $(wc -l < boutique.py) lignes"
```
<!--sortie-->
```text
module écrit : 62 lignes
```

Quelques points de lecture :

- `frozen=True` rend l'article **immuable** : impossible d'écrire `article.prix_ht = -5` après coup. Moins de bogues possibles.
- `__post_init__` est appelé juste après le constructeur généré par la dataclass : c'est l'endroit idéal pour **valider** les données.
- `__len__` est une **méthode spéciale** (on les reconnaît à leurs doubles tirets bas) : elle fait fonctionner `len(panier)`.
- `CommandeSite(Commande)` est un exemple d'**héritage** : la classe fille reprend tout de la classe mère et ne **redéfinit** que ce qui change, ici `frais_livraison`. La méthode `total_a_payer`, écrite une seule fois dans `Commande`, appelle `self.frais_livraison()` et obtient automatiquement le bon comportement selon le type d'objet : c'est le **polymorphisme**.

> 💡 **Quand utiliser l'héritage ?** Avec parcimonie. Deux classes dont l'une « *est une sorte de* » l'autre (une commande du site *est une* commande) : oui. Pour simplement réutiliser du code, préférez la **composition** (un objet qui *contient* un autre, comme `Commande` contient un `Panier`). Beaucoup de projets de data science n'ont besoin que de fonctions et de dataclasses.

**Étape 4 : les tests du module.** Chaque règle métier vérifiée à la main plus haut devient un test. Le décorateur `@pytest.fixture` prépare le panier de l'exemple (le *arrange*) ; `pytest.approx` compare des nombres décimaux avec une petite tolérance (rappelez-vous, section 1.5 : `0.1 + 0.2 != 0.3` en binaire !) ; `@pytest.mark.parametrize` rejoue le même test avec plusieurs valeurs.

```bash
cat > test_boutique.py <<'FIN'
import pytest

from boutique import Article, Commande, CommandeSite, Panier


@pytest.fixture
def panier():
    """Le panier de l'exemple : 2 savons à 20 DT + 1 plateau à 30 DT."""
    p = Panier()
    p.ajouter(Article("savon", 20.0), 2)
    p.ajouter(Article("plateau", 30.0))
    return p


def test_nombre_d_unites(panier):
    assert len(panier) == 3


def test_total_ht(panier):
    assert panier.total_ht() == 70.0


def test_total_ttc(panier):
    assert panier.total_ttc() == pytest.approx(83.30)


def test_total_ttc_avec_remise(panier):
    assert panier.total_ttc(remise=0.10) == pytest.approx(74.97)


@pytest.mark.parametrize("quantite", [0, -2])
def test_quantite_invalide(quantite):
    with pytest.raises(ValueError):
        Panier().ajouter(Article("savon", 20.0), quantite)


def test_prix_negatif_refuse():
    with pytest.raises(ValueError):
        Article("cadeau", -1.0)


def test_retrait_boutique_gratuit(panier):
    assert Commande(panier).total_a_payer() == pytest.approx(83.30)


def test_livraison_payante_sous_le_seuil(panier):
    # 83,30 DT < 100 DT : 7 DT de frais -> 90,30 DT
    assert CommandeSite(panier).total_a_payer() == pytest.approx(90.30)


def test_livraison_offerte_au_dessus_du_seuil(panier):
    panier.ajouter(Article("coffret", 20.0))     # 90 DT HT -> 107,10 DT TTC
    assert CommandeSite(panier).total_a_payer() == pytest.approx(107.10)
FIN

python -m pytest -v --color=no --tb=short -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | grep -v -E "^(platform|rootdir|cachedir|plugins|configfile)"
```
<!--sortie-->
```text
============================= test session starts ==============================
collecting ... collected 12 items

test_boutique.py::test_nombre_d_unites PASSED                            [  8%]
test_boutique.py::test_total_ht PASSED                                   [ 16%]
test_boutique.py::test_total_ttc PASSED                                  [ 25%]
test_boutique.py::test_total_ttc_avec_remise PASSED                      [ 33%]
test_boutique.py::test_quantite_invalide[0] PASSED                       [ 41%]
test_boutique.py::test_quantite_invalide[-2] PASSED                      [ 50%]
test_boutique.py::test_prix_negatif_refuse PASSED                        [ 58%]
test_boutique.py::test_retrait_boutique_gratuit PASSED                   [ 66%]
test_boutique.py::test_livraison_payante_sous_le_seuil PASSED            [ 75%]
test_boutique.py::test_livraison_offerte_au_dessus_du_seuil PASSED       [ 83%]
test_remises.py::test_remise_de_25_pour_cent PASSED                      [ 91%]
test_remises.py::test_sans_remise PASSED                                 [100%]

============================== 12 passed ==============================
```

Chaque ligne verte est une promesse tenue. Vérifiez qu'elles correspondent bien aux calculs faits à la main : $83{,}30$, $74{,}97$, $83{,}30+7=90{,}30$, et le panier de $90$ DT HT qui vaut $90\times1{,}19=107{,}10$ DT TTC, donc livraison offerte.

> 🧪 **Que se passe-t-il si on casse le code ?** Modifions le seuil de livraison offerte à 1 000 DT dans le module (une faute de frappe plausible : un zéro en trop), et relançons les tests. Un seul test devrait passer au rouge, celui qui protège précisément cette règle :

```bash
sed -i 's/SEUIL_LIVRAISON_OFFERTE = 100.0/SEUIL_LIVRAISON_OFFERTE = 1000.0/' boutique.py
python -m pytest -q --color=no --tb=no -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | tail -2
sed -i 's/SEUIL_LIVRAISON_OFFERTE = 1000.0/SEUIL_LIVRAISON_OFFERTE = 100.0/' boutique.py   # on remet la bonne valeur
python -m pytest -q --color=no -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | tail -1
```
<!--sortie-->
```text
FAILED test_boutique.py::test_livraison_offerte_au_dessus_du_seuil - assert 1...
1 failed, 11 passed
12 passed
```

Voilà la valeur d'une suite de tests : une modification « innocente » est détectée **immédiatement**, avec le nom du test et la règle violée.

### 4.6.6 Une application : tester une fonction d'analyse

Les tests ne servent pas qu'aux classes : une fonction d'analyse de données mérite les mêmes soins, surtout si elle sera réutilisée dans un rapport. Voici le panier moyen par canal (le même calcul que celui du chapitre 3), testé sur un **petit tableau dont on connaît la réponse à la main**.

```bash
cat > analyse.py <<'FIN'
import pandas as pd


def panier_moyen_par_canal(commandes: pd.DataFrame) -> pd.Series:
    """Montant moyen des commandes pour chaque canal de vente."""
    return commandes.groupby("canal")["montant"].mean()
FIN

cat > test_analyse.py <<'FIN'
import pandas as pd
import pytest

from analyse import panier_moyen_par_canal


def test_panier_moyen_par_canal():
    petit = pd.DataFrame({
        "canal":   ["Site", "Site", "Boutique"],
        "montant": [10.0, 30.0, 50.0],
    })
    resultat = panier_moyen_par_canal(petit)
    assert resultat["Site"] == pytest.approx(20.0)        # (10 + 30) / 2
    assert resultat["Boutique"] == pytest.approx(50.0)    # une seule commande
FIN

python -m pytest -v --color=no --tb=short -p no:cacheprovider test_analyse.py 2>&1 | sed -E 's/ in [0-9.]+s//' | grep -E "PASSED|FAILED|passed|failed"
```
<!--sortie-->
```text
test_analyse.py::test_panier_moyen_par_canal PASSED                      [100%]
============================== 1 passed ===============================
```

Cette fonction renvoie la même chose que `df.groupby("canal")["montant"].mean()` appliqué aux 400 commandes (section 4.4), mais elle est maintenant **nommée, documentée et protégée**. Dans un vrai projet, on range le code dans un dossier `src/` et les tests dans un dossier `tests/` ; la commande `pytest` trouve alors tout seule les fichiers `test_*.py` (chapitre 6.1 pour les ranger sous Git).

> ✅ **À retenir (objets, code propre, tests).**
>
> - Une **classe** regroupe des **données** (attributs) et des **opérations** (méthodes) ; `self` désigne l'objet courant. Une **dataclass** génère le constructeur, l'affichage et l'égalité à votre place.
> - On **valide** les données à l'entrée (`__post_init__`, `raise ValueError`) : mieux vaut une erreur claire qu'un résultat faux silencieux.
> - **Héritage** : la classe fille redéfinit seulement ce qui change ; **composition** : un objet en contient un autre. Dans le doute, préférez la composition.
> - **Code propre** : noms parlants, fonctions courtes, constantes nommées (`TVA`), docstrings, annotations de type (non vérifiées à l'exécution), pas de `[]` comme valeur par défaut.
> - **Test unitaire** = Arrange, Act, Assert. Avec **pytest** : fonctions `test_…`, `assert`, `pytest.approx` pour les décimaux, `pytest.raises` pour les erreurs attendues, `@pytest.mark.parametrize` pour plusieurs cas.
> - Un bogue trouvé ? Écrivez d'abord le test qui l'attrape, puis corrigez.


## 4.7 ➕ Pour aller plus loin : d'autres langages (SAS, MATLAB, Julia)

> 🧭 **Section optionnelle.** Python et R vous couvriront dans la grande majorité des cas. Mais vous croiserez peut-être, dans une offre d'emploi, un stage ou le code d'un collègue, **SAS**, **MATLAB** ou **Julia**. Cette section ne vous apprend pas ces langages : elle vous donne le **vocabulaire** pour les lire sans panique, en refaisant *la même petite analyse* dans chacun.

> ⚠️ **Honnêteté sur ce qui a été exécuté.** Python et R sont installés sur la machine qui a produit ce livre : leurs sorties ci-dessous sont **réelles**. SAS, MATLAB et Julia ne le sont pas : leurs blocs de code sont marqués « **non exécuté** » et ne sont accompagnés d'aucune sortie. Ils sont écrits à partir de leur documentation, avec les conventions habituelles de chaque langage ; **vérifiez-les chez vous** avant de les utiliser dans un travail important. Le résultat attendu est celui de Python et R (section 3.1 : il est le même partout, car le calcul est le même).

### 4.7.1 La tâche : un résumé par canal

Yasmine demande : *« Pour chaque canal de vente, combien de commandes, quel montant moyen, et quel écart-type ? »* C'est le calcul du 3.1, appliqué au fichier `donnees/commandes.csv` : lire, regrouper, résumer. Cinq lignes dans chaque langage.

**En Python** (pandas, section 4.4) :

```python
import pandas as pd

commandes = pd.read_csv("donnees/commandes.csv")
resume = (commandes.groupby("canal")["montant"]
          .agg(n="count", moyenne="mean", ecart_type="std")
          .round(1))
print(resume)
```
<!--sortie-->
```text
             n  moyenne  ecart_type
canal                              
Boutique   114     74.8        40.6
Instagram  138     49.0        31.1
Site       148     59.5        38.3
```

**En R** (le même calcul avec le paquet `dplyr`, section 4.2) :

```r
suppressPackageStartupMessages(library(dplyr))

commandes <- read.csv("donnees/commandes.csv")
commandes |>
  group_by(canal) |>
  summarise(n = n(), moyenne = round(mean(montant), 1), ecart_type = round(sd(montant), 1))
```
<!--sortie-->
```text
# A tibble: 3 × 4
  canal         n moyenne ecart_type
  <chr>     <int>   <dbl>      <dbl>
1 Boutique    114    74.8       40.6
2 Instagram   138    49         31.1
3 Site        148    59.5       38.3
```

Les deux langages donnent exactement les mêmes nombres : 114 commandes en boutique pour un montant moyen d'environ 75 DT, comme au 3.1. (Le tri alphabétique des canaux est le même ; seule la présentation du tableau diffère.)

### 4.7.2 SAS : le langage des grandes organisations

> 💡 **Intuition.** **SAS** (*Statistical Analysis System*) est un logiciel commercial né dans les années 1970. Il est resté très présent dans les **banques, les assurances, l'industrie pharmaceutique et les administrations**, où l'on valorise la stabilité, la traçabilité et le fait que les résultats d'un programme écrit il y a vingt ans soient toujours identiques. C'est souvent le cas dans les métiers de l'actuariat et du risque (le thème du volume V de cette série). Pour vous former gratuitement, SAS propose une version en ligne destinée à l'enseignement (*SAS OnDemand for Academics*).

Un programme SAS est une suite d'**étapes** : les étapes `DATA` fabriquent ou transforment des tables, les étapes `PROC` (procédures) appliquent un traitement statistique prêt à l'emploi. Chaque instruction se termine par un point-virgule, et un bloc par `run;`.

```sas noexec
/* SAS — non exécuté dans ce livre */
proc import datafile="donnees/commandes.csv"
            out=commandes dbms=csv replace;
    guessingrows=max;
run;

proc means data=commandes n mean std maxdec=1;
    class canal;          /* un résumé par canal */
    var montant;          /* la variable à résumer */
run;
```

On lit : « importer le CSV dans une table `commandes` » puis « *procédure MEANS* : pour chaque `canal` (`class`), donner l'effectif (`n`), la moyenne et l'écart-type de `montant` ». Aucune boucle explicite : SAS parcourt lui-même les lignes.

### 4.7.3 MATLAB : le calcul numérique des ingénieurs

> 💡 **Intuition.** **MATLAB** (*Matrix Laboratory*) est un environnement commercial centré sur les **matrices**, très utilisé en ingénierie, en traitement du signal et en automatique, souvent enseigné dans les écoles d'ingénieurs. Tout y est une matrice, même un nombre seul (une matrice $1\times1$). Si vous avez aimé le chapitre 1 (algèbre linéaire), vous serez chez vous. Une alternative libre, **GNU Octave**, exécute une grande partie du même code.

Deux particularités à connaître : les indices **commencent à 1**, et les fichiers de données se lisent dans une `table`.

```matlab noexec
% MATLAB — non exécuté dans ce livre
T = readtable("donnees/commandes.csv");

G = groupsummary(T, "canal", ["mean" "std"], "montant");
disp(G)
```

`groupsummary` regroupe les lignes par `canal` et calcule la moyenne et l'écart-type de `montant`. Le résultat est une nouvelle table avec les colonnes `mean_montant` et `std_montant`.

### 4.7.4 Julia : la promesse « rapide comme C, simple comme Python »

> 💡 **Intuition.** **Julia** (libre, créé en 2012) vise un compromis : une syntaxe lisible proche de Python et de MATLAB, mais un code **compilé à la volée** presque aussi rapide qu'un programme en C. Il est apprécié pour le calcul scientifique, les simulations lourdes et l'optimisation. Son écosystème de science des données est plus jeune que celui de Python ; une particularité est le temps d'attente à la première exécution (la compilation).

```julia noexec
# Julia — non exécuté dans ce livre
using CSV, DataFrames, Statistics

commandes = CSV.read("donnees/commandes.csv", DataFrame)

resume = combine(groupby(commandes, :canal),
                 nrow => :n,
                 :montant => mean => :moyenne,
                 :montant => std => :ecart_type)
println(resume)
```

On retrouve la logique de pandas : `groupby` puis `combine` (on lit `colonne => fonction => nom_du_résultat`). Les colonnes se désignent par des *symboles* (`:canal`).

### 4.7.5 Le même calcul, vu de près : un dictionnaire de traduction

Voici de quoi passer d'un langage à l'autre. (Les cases SAS, MATLAB et Julia sont **non exécutées**, comme les blocs ci-dessus.)

| Idée | Python | R | MATLAB | Julia | SAS |
|---|---|---|---|---|---|
| Affecter | `x = 5` | `x <- 5` | `x = 5;` | `x = 5` | `x = 5;` (étape DATA) |
| Premier élément d'une liste | `x[0]` | `x[1]` | `x(1)` | `x[1]` | — |
| Moyenne | `np.mean(x)` | `mean(x)` | `mean(x)` | `mean(x)` | `proc means` |
| Écart-type | `np.std(x, ddof=1)` | `sd(x)` | `std(x)` | `std(x)` | `proc means std` |
| Lire un CSV | `pd.read_csv(f)` | `read.csv(f)` | `readtable(f)` | `CSV.read(f, DataFrame)` | `proc import` |
| Résumé par groupe | `groupby().agg()` | `group_by()` puis `summarise()` | `groupsummary` | `proc means; class` |
| Blocs | indentation | `{ }` | `end` | `end` | `run;` |

> ⚠️ **Le piège des indices : 0 ou 1 ?** Python (comme C, Java) compte à partir de **0** ; R, MATLAB et Julia à partir de **1**. De plus, les *tranches* ne se comportent pas pareil, et l'indice négatif signifie des choses opposées. Voyez la différence entre Python et R, tous les deux exécutés :

```python
x = [10, 20, 30, 40, 50]
print("x[0]    =", x[0])
print("x[0:2]  =", x[0:2], "  (la borne de droite est exclue)")
print("x[-1]   =", x[-1], "  (le dernier élément)")
```
<!--sortie-->
```text
x[0]    = 10
x[0:2]  = [10, 20]   (la borne de droite est exclue)
x[-1]   = 50   (le dernier élément)
```

```r
x <- c(10, 20, 30, 40, 50)
cat("x[1]    =", x[1], "\n")
cat("x[1:2]  =", x[1:2], "  (la borne de droite est incluse)\n")
cat("x[-1]   =", x[-1], "  (tout sauf le premier élément !)\n")
```
<!--sortie-->
```text
x[1]    = 10 
x[1:2]  = 10 20   (la borne de droite est incluse)
x[-1]   = 20 30 40 50   (tout sauf le premier élément !)
```

Même symbole `x[-1]`, **deux sens opposés** : le dernier élément en Python, « tout sauf le premier » en R. Si vous traduisez du code d'un langage à l'autre, c'est la première chose à vérifier.

> 📐 **Un point commun rassurant : $n-1$.** Les écarts-types par défaut de pandas, R (`sd`), MATLAB (`std`) et Julia (`std`) divisent par $n-1$ (l'estimateur sans biais démontré au 3.2) ; seul `np.std` de NumPy divise par $n$ si on ne précise pas `ddof=1`. Même formule, mêmes nombres : le fait que vos résultats concordent d'un langage à l'autre est d'ailleurs une excellente manière de **vérifier** un calcul.

### 4.7.6 Alors, lequel choisir ?

| Langage | Atouts | Limites | À privilégier si… |
|---|---|---|---|
| **Python** | généraliste, immense écosystème, apprentissage automatique, mise en production | graphiques statistiques moins « clés en main » que R | vous voulez **un seul langage** pour tout (ce livre) |
| **R** | statistique de référence, `ggplot2`, rapports reproductibles | moins à l'aise pour le développement logiciel | votre travail est surtout statistique ou académique |
| **SAS** | stabilité, validation réglementaire, très robuste sur de gros fichiers | licence payante, communauté plus fermée | votre employeur (banque, assurance, pharma) l'impose |
| **MATLAB** | calcul matriciel, boîtes à outils d'ingénierie | licence payante, moins utilisé en science des données | vous venez de l'ingénierie ou du signal |
| **Julia** | très rapide, syntaxe claire, calcul scientifique | écosystème plus jeune, compilation au premier appel | vous faites des **simulations lourdes** ou de l'optimisation |

> 💡 **Le conseil pratique.** On n'apprend pas un langage par collection, on l'apprend par **projet**. Maîtrisez Python (et un peu de R pour lire du code de statisticien). Le jour où un poste exige SAS, MATLAB ou Julia, la bonne nouvelle est que *les idées sont les mêmes* : tableau, regroupement, résumé, graphique. Il ne reste qu'à apprendre la syntaxe, avec ce dictionnaire sous la main. Regardez les offres d'emploi de votre domaine et de votre pays pour savoir quels langages y sont demandés avant d'investir du temps.

> ✅ **À retenir (autres langages).**
>
> - **SAS** : étapes `DATA` et `PROC`, point-virgule partout, très répandu en banque, assurance et pharma ; version d'apprentissage gratuite en ligne.
> - **MATLAB** : tout est matrice, indices à partir de 1 ; **Octave** en est une alternative libre.
> - **Julia** : rapide et lisible, compilé à la volée ; écosystème plus jeune.
> - Python et R ont été exécutés ici ; **SAS, MATLAB et Julia ne l'ont pas été** (blocs « non exécuté »).
> - Pièges de traduction : indices à partir de 0 ou de 1, signification de `x[-1]`, bornes des tranches ; l'écart-type par défaut divise par $n-1$ presque partout.
> - Quel que soit le langage, le raisonnement est le même : **lire → regrouper → résumer → vérifier**.


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


## 4.9 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 2 et 3 sont ceux que la section 4.1.10 vous avait promis. Les exercices 13 et 14 reprennent les sections optionnelles 4.6 et 4.8.

### Énoncés

**Exercice 1 ⭐ (4.1 : dictionnaires et boucles).** Cinq commandes `(canal, montant)` : `("Site", 40)`, `("Instagram", 25)`, `("Site", 60)`, `("Boutique", 100)`, `("Instagram", 35)`. Calculez à la main le chiffre d'affaires de chaque canal et sa part du total. Écrivez ensuite le programme avec un dictionnaire et une boucle, sans bibliothèque.

**Exercice 2 ⭐⭐ (4.1.10 : un produit absent du catalogue).** Reprenez le programme de la caisse. (a) Que se passe-t-il pour le panier `[("bol", 2), ("vase", 1)]` ? (b) Faites afficher un message **aimable** (nom du produit fautif et liste des produits disponibles) au lieu d'un plantage. (c) Variante : ignorez les produits inconnus, calculez le total TTC du reste du panier et listez ce qui a été ignoré. Quel total TTC attendez-vous à la main ?

**Exercice 3 ⭐⭐ (4.1.10 : un code promo).** Yasmine crée le code `JASMIN15` (15 % de remise sur le hors-taxe) et le code `RENTREE5` (5 %). Règle : la remise promo **ne se cumule pas** avec la remise fidélité (10 % au-delà de 100 DT) ; on applique la **meilleure des deux**. Un code inconnu est ignoré avec un message. Calculez à la main le TTC du panier « 2 bols, 1 plateau, 3 bougies » avec `JASMIN15`, puis celui de « 2 tasses » avec le même code, et vérifiez par le code.

**Exercice 4 ⭐ (4.2 : R).** Quelle part des commandes est « satisfaite » (note $\geq 4$) dans chaque canal ? (a) Sur les notes `5, 4, 2, 3, 5` de l'exemple, calculez la part à la main. (b) Répondez sur `donnees/commandes.csv` en R de base (`tapply` sur un test logique), puis (c) avec `dplyr`, et (d) contrôlez le résultat avec pandas.

**Exercice 5 ⭐ (4.3.3 : une pile).** La notation polonaise inversée (NPI) écrit l'opérateur **après** ses opérandes : `3 4 +` signifie $3+4$. Elle se calcule avec une pile et n'a besoin d'aucune parenthèse. (a) Évaluez à la main `3 4 + 2 *`, puis `5 1 2 + 4 * + 3 -`. (b) Écrivez la fonction d'évaluation. (c) Le prix TTC d'un article à 80 DT HT avec 10 % de remise s'écrit `80 1 0.1 - * 1.19 *` : calculez-le. (d) Que doit faire la fonction devant `3 +` ?

**Exercice 6 ⭐⭐ (4.3.3 : une file à deux emballeuses).** Six commandes arrivent aux minutes 0, 1, 2, 3, 10 et 11 ; emballer une commande dure 4 minutes. Calculez à la main l'attente de chaque commande (a) avec **une** emballeuse, (b) avec **deux**, puis écrivez la simulation. Indice : retenez, pour chaque emballeuse, l'instant où elle sera libre ; la prochaine commande est confiée à celle qui est libre **le plus tôt** (le module `heapq` sait trouver le plus petit élément).

**Exercice 7 ⭐⭐ (4.3.5 : une dichotomie à variante).** `bisect_left(liste, x)` renvoie la **première** position où $x$ pourrait être inséré dans une liste triée. (a) Évaluez à la main cette position pour $x=2$ dans `[1, 2, 2, 2, 5]`. (b) Écrivez votre propre version par dichotomie, en énonçant son invariant. (c) Déduisez-en le nombre de commandes ayant la note 5 dans la colonne `satisfaction` triée, et comparez avec `Counter`. (d) Vérifiez votre fonction contre `bisect_left` sur 1 000 listes aléatoires.

**Exercice 8 ⭐ (4.3.6 : tri stable).** Rangez les commandes `("Site", 40.1)`, `("Boutique", 65.8)`, `("Site", 19.6)`, `("Boutique", 17.4)`, `("Instagram", 30.1)`, `("Site", 75.0)` **par canal croissant puis, dans chaque canal, par montant décroissant**, avec uniquement des appels à `sorted`. Dans quel ordre faut-il enchaîner les deux tris ? Que se passe-t-il si on les inverse ?

**Exercice 9 ⭐ (4.4 : NumPy et broadcasting).** Les quantités vendues sur trois jours pour (bol, tasse, plateau, bougie) sont les lignes de $Q=\begin{pmatrix}2&0&1&3\\1&1&0&0\\0&4&2&1\end{pmatrix}$, les prix HT sont `[12.5, 8, 45, 15.9]`. (a) Calculez à la main le chiffre d'affaires de chaque jour. (b) Une promotion retire `[0, 10 %, 0, 20 %]` aux prix ; recalculez le chiffre d'affaires quotidien **en une seule ligne** grâce au broadcasting. (c) Quel produit s'est le mieux vendu en nombre d'unités ?

**Exercice 10 ⭐⭐ (4.4 : groupby et dates).** Six ventes : (5 janv., Site, 30), (20 janv., Instagram, 50), (2 févr., Site, 70), (10 févr., Site, 20), (11 févr., Boutique, 100), (1er mars, Instagram, 40). (a) Dressez à la main le tableau **mois × canal** des montants et les totaux mensuels. (b) Obtenez-le avec `pivot_table`. (c) Sur les 400 commandes (avec les colonnes `date` et `id_client` simulées en 4.4.5), quel mois rapporte le plus, et quel jour de la semaine compte le plus de commandes ?

**Exercice 11 ⭐⭐ (4.4.10 : jointure et clients dormants).** (a) Quatre commandes portent les numéros de client `1, 1, 3, 5` ; la table des clients contient les numéros 1 à 5. Qui n'a jamais commandé ? (b) Sur les données du livre (table `clients` de 4.4.10), combien de clients n'ont **aucune** commande ? Répondez de deux façons : avec `isin`, puis avec une jointure `left` et le comptage des valeurs manquantes. (c) Quel est le chiffre d'affaires par ville ?

**Exercice 12 ⭐⭐ (4.5 : un graphique honnête).** Tracez le montant moyen par canal en barres **triées par ordre décroissant**, avec un axe qui commence à zéro, un titre qui énonce le message, des axes nommés avec leur unité. Vérifiez par le code que les hauteurs des barres sont bien les moyennes, que l'axe commence à 0 et que le fichier est enregistré. Citez deux défauts qu'aurait une version avec axe tronqué et camembert 3D.

**Exercice 13 ⭐⭐ (4.6 : un test unitaire).** Règle de livraison : retrait en boutique gratuit ; sur le Site ou Instagram, 7 DT, **offerts à partir de 100 DT TTC** (100 compris) ; un canal inconnu est une erreur. (a) Dressez la liste des cas à tester, en pensant aux **bornes**. (b) Écrivez la fonction **avec le défaut classique** (`>` au lieu de `>=`) et les tests avec `pytest` ; constatez l'échec. (c) Corrigez et relancez.

**Exercice 14 ⭐⭐⭐ (4.8 : coût d'un algorithme).** On veut compter les **paires de commandes passées par le même client**. (a) Combien de paires de commandes y a-t-il en tout parmi $n=400$ ? Et parmi $n=800$ ? Quel est le facteur ? (b) Écrivez la version « double boucle » et comptez ses tours. (c) Écrivez une version en $O(n)$ avec un dictionnaire de compteurs (un client avec $c$ commandes produit $c(c-1)/2$ paires). (d) Vérifiez qu'elles donnent le même résultat. (e) Estimez, avec la formule, le nombre de tours de la double boucle pour un million de commandes.

### Corrigés

**Corrigé 1.** Site : $40+60=100$ ; Instagram : $25+35=60$ ; Boutique : $100$. Total : $260$. Parts : $100/260\approx38{,}5\,\%$ pour le Site, $60/260\approx23{,}1\,\%$ pour Instagram, $38{,}5\,\%$ pour la Boutique (la somme des parts doit faire 100 %).

```python
commandes = [("Site", 40), ("Instagram", 25), ("Site", 60), ("Boutique", 100), ("Instagram", 35)]
ca = {}
for canal, montant in commandes:
    ca[canal] = ca.get(canal, 0) + montant          # .get évite la KeyError au premier passage
total = sum(ca.values())
for canal, valeur in sorted(ca.items()):
    print(f"{canal:<10} {valeur:>4} DT   {valeur / total:6.1%}")
print("total :", total, "| somme des parts :", round(sum(v / total for v in ca.values()), 6))
```
<!--sortie-->
```text
Boutique    100 DT    38.5%
Instagram    60 DT    23.1%
Site        100 DT    38.5%
total : 260 | somme des parts : 1.0
```

**Corrigé 2.** (a) Le programme cherche `CATALOGUE["vase"]`, qui n'existe pas : Python s'arrête avec `KeyError: 'vase'` (voir 4.1.8). (b) On rattrape l'erreur avec `try / except KeyError`, et on utilise la clé fautive que l'exception transporte. (c) On sépare les produits connus des inconnus **avant** de calculer. À la main : 2 bols $=25$ DT HT, sous le seuil de remise ; TVA $25\times0{,}19=4{,}75$ ; TTC $=29{,}75$ DT.

```python
CATALOGUE = {"bol": 12.5, "tasse": 8.0, "plateau": 45.0, "bougie": 15.9}     # identique à 4.1.10
TVA, SEUIL_REMISE, TAUX_REMISE = 0.19, 100, 0.10


def sous_total(panier):
    return sum(CATALOGUE[nom] * qte for nom, qte in panier)


def remise(montant_ht):
    return montant_ht * TAUX_REMISE if montant_ht > SEUIL_REMISE else 0.0


panier = [("bol", 2), ("vase", 1)]
try:
    sous_total(panier)
except KeyError as e:
    print("(a) KeyError, clé fautive :", e)
    print(f"(b) Désolé, {e.args[0]!r} n'est pas au catalogue. Disponibles : {', '.join(sorted(CATALOGUE))}.")


def total_prudent(panier):
    """Renvoie (total TTC, liste des produits ignorés)."""
    connus = [(nom, qte) for nom, qte in panier if nom in CATALOGUE]
    ignores = [nom for nom, _ in panier if nom not in CATALOGUE]
    ht = sous_total(connus)
    net = ht - remise(ht)
    return round(net * (1 + TVA), 2), ignores


print("(c)", total_prudent(panier))
```
<!--sortie-->
```text
(a) KeyError, clé fautive : 'vase'
(b) Désolé, 'vase' n'est pas au catalogue. Disponibles : bol, bougie, plateau, tasse.
(c) (29.75, ['vase'])
```

On retrouve le TTC de 29,75 DT calculé à la main, et `'vase'` est signalé comme ignoré. Le choix entre « refuser le panier » (b) et « ignorer et signaler » (c) est une **décision métier**, pas technique : ce qui compte, c'est de ne jamais avaler une erreur en silence.

> ⚠️ **Piège.** Un `except:` nu (sans type d'erreur) rattrape *tout*, y compris vos propres fautes de frappe : on ne rattrape que l'erreur **attendue** (`KeyError`, `ValueError`…).

**Corrigé 3.** Panier de 4.1.10 : sous-total HT $=117{,}70$. Remise fidélité : $10\,\%$ soit $11{,}77$ DT ; remise promo : $15\,\%$ soit $17{,}655$ DT. On garde la meilleure, la promo : net $=117{,}70\times0{,}85=100{,}045$ ; TTC $=100{,}045\times1{,}19=119{,}05355\approx119{,}05$ DT (contre $126{,}06$ sans code). Panier de 2 tasses : HT $=16$, pas de remise fidélité (sous 100 DT), promo 15 % : net $=13{,}60$, TTC $=13{,}60\times1{,}19=16{,}184\approx16{,}18$ DT.

```python
CODES = {"JASMIN15": 0.15, "RENTREE5": 0.05}


def total_ttc(panier, code=None):
    ht = sous_total(panier)
    taux = TAUX_REMISE if ht > SEUIL_REMISE else 0.0       # remise fidélité
    if code is not None:
        if code in CODES:
            taux = max(taux, CODES[code])                  # la meilleure des deux, sans cumul
        else:
            print(f"  code {code!r} inconnu : ignoré")
    return round(ht * (1 - taux) * (1 + TVA), 2)


gros = [("bol", 2), ("plateau", 1), ("bougie", 3)]
print("gros panier sans code   :", total_ttc(gros))
print("gros panier JASMIN15    :", total_ttc(gros, "JASMIN15"))
print("gros panier RENTREE5    :", total_ttc(gros, "RENTREE5"), "(la fidélité de 10 % est meilleure)")
print("2 tasses JASMIN15       :", total_ttc([("tasse", 2)], "JASMIN15"))
print("2 tasses code bidon     :", total_ttc([("tasse", 2)], "PROMO99"))
assert total_ttc(gros, "JASMIN15") == 119.05 and total_ttc([("tasse", 2)], "JASMIN15") == 16.18
```
<!--sortie-->
```text
gros panier sans code   : 126.06
gros panier JASMIN15    : 119.05
gros panier RENTREE5    : 126.06 (la fidélité de 10 % est meilleure)
2 tasses JASMIN15       : 16.18
  code 'PROMO99' inconnu : ignoré
2 tasses code bidon     : 19.04
```

Les valeurs coïncident avec la main. Remarquez le troisième cas : `RENTREE5` (5 %) est **moins bon** que la fidélité (10 %), donc le total reste celui sans code.

**Corrigé 4.** (a) Notes $5,4,2,3,5$ : trois notes sur cinq sont $\ge4$, soit $60\,\%$. (b) En R, un test logique vaut `TRUE` (1) ou `FALSE` (0) : la **moyenne** d'un test logique est donc la **proportion** de `TRUE`. (c) La version `dplyr`. (d) Le contrôle avec pandas utilise exactement la même idée.

```r
notes <- c(5, 4, 2, 3, 5)
mean(notes >= 4)                                       # (a) : 0.6

df <- read.csv("donnees/commandes.csv")
round(tapply(df$satisfaction >= 4, df$canal, mean), 3) # (b) R de base

suppressPackageStartupMessages(library(dplyr))
df |>                                                  # (c) dplyr
  group_by(canal) |>
  summarise(n = n(), part_satisfaits = round(mean(satisfaction >= 4), 3))
```
<!--sortie-->
```text
[1] 0.6
 Boutique Instagram      Site 
    0.956     0.630     0.696 
# A tibble: 3 × 3
  canal         n part_satisfaits
  <chr>     <int>           <dbl>
1 Boutique    114           0.956
2 Instagram   138           0.63 
3 Site        148           0.696
```

```python
import pandas as pd

df = pd.read_csv("donnees/commandes.csv")
print((df["satisfaction"] >= 4).groupby(df["canal"]).mean().round(3))       # (d) pandas
```
<!--sortie-->
```text
canal
Boutique     0.956
Instagram    0.630
Site         0.696
Name: satisfaction, dtype: float64
```

Les trois méthodes donnent les mêmes proportions : 95,6 % de commandes satisfaites en **Boutique**, 69,6 % sur le **Site** et 63,0 % sur **Instagram**. La Boutique est loin devant : le retrait est immédiat, or la satisfaction baisse d'environ 0,18 point par jour de délai (4.2.5). C'est une description de l'échantillon : savoir si un écart est *significatif* demanderait un test, comme au 3.4.

**Corrigé 5.** (a) `3 4 + 2 *` : on empile 3 puis 4 ; `+` dépile 4 et 3 et empile 7 ; on empile 2 ; `*` dépile 2 et 7 et empile 14. Résultat : $(3+4)\times2=14$. Pour `5 1 2 + 4 * + 3 -` : pile `[5]`, `[5,1]`, `[5,1,2]` ; `+` → `[5,3]` ; `4` → `[5,3,4]` ; `*` → `[5,12]` ; `+` → `[17]` ; `3` → `[17,3]` ; `-` → `[14]`. Soit $5+(1+2)\times4-3=14$. **Attention à l'ordre** : pour `-` et `/`, le **premier** dépilé est l'opérande de **droite**. (c) $80\times(1-0{,}1)\times1{,}19=85{,}68$ DT.

```python
def evaluer_npi(expression):
    operations = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
                  "*": lambda a, b: a * b, "/": lambda a, b: a / b}
    pile = []
    for jeton in expression.split():
        if jeton in operations:
            if len(pile) < 2:
                raise ValueError(f"expression invalide : il manque un opérande pour {jeton!r}")
            droite = pile.pop()                    # le dernier empilé est l'opérande de droite
            gauche = pile.pop()
            pile.append(operations[jeton](gauche, droite))
        else:
            pile.append(float(jeton))
    if len(pile) != 1:
        raise ValueError("expression invalide : il reste plusieurs valeurs sur la pile")
    return pile[0]


print(evaluer_npi("3 4 + 2 *"))
print(evaluer_npi("5 1 2 + 4 * + 3 -"))
print(round(evaluer_npi("80 1 0.1 - * 1.19 *"), 2))
try:
    evaluer_npi("3 +")
except ValueError as e:
    print("(d) ValueError :", e)
```
<!--sortie-->
```text
14.0
14.0
85.68
(d) ValueError : expression invalide : il manque un opérande pour '+'
```

(d) Devant `3 +`, la pile ne contient qu'une valeur quand arrive `+` : la fonction doit **signaler l'erreur** plutôt que de planter obscurément sur un `pop` de pile vide.

**Corrigé 6.** (a) Une emballeuse (libre en 0, 4, 8, 12, …) : débuts 0, 4, 8, 12, 16, 20 ; attentes $0,3,6,9,6,9$ ; moyenne $33/6=5{,}5$ min. (b) Deux emballeuses : la commande 0 démarre en 0 (emballeuse A, libre à 4) ; la 1 démarre en 1 (B, libre à 5), attente 0 ; la 2 attend A jusqu'à 4 : attente 2 (A libre à 8) ; la 3 attend B jusqu'à 5 : attente 2 (B libre à 9) ; la 4 (arrivée 10) trouve tout libre : attente 0 ; la 5 (arrivée 11) trouve B libre depuis 9 : attente 0. Attentes $0,0,2,2,0,0$ ; moyenne $4/6\approx0{,}67$ min.

```python
import heapq
from collections import deque


def simuler(arrivees, duree, nb_emballeuses):
    libres = [0] * nb_emballeuses              # instant où chaque emballeuse sera libre (un « tas »)
    heapq.heapify(libres)
    file = deque(arrivees)
    attentes = []
    while file:
        arrivee = file.popleft()               # premier arrivé, premier servi
        libre_a = heapq.heappop(libres)        # l'emballeuse libre le plus tôt
        debut = max(arrivee, libre_a)
        attentes.append(debut - arrivee)
        heapq.heappush(libres, debut + duree)
    return attentes


arrivees = [0, 1, 2, 3, 10, 11]
for k in (1, 2):
    a = simuler(arrivees, 4, k)
    print(f"{k} emballeuse(s) : attentes {a} | moyenne {sum(a) / len(a):.2f} min")
```
<!--sortie-->
```text
1 emballeuse(s) : attentes [0, 3, 6, 9, 6, 9] | moyenne 5.50 min
2 emballeuse(s) : attentes [0, 0, 2, 2, 0, 0] | moyenne 0.67 min
```

Doubler l'effectif divise l'attente moyenne **par plus de huit** (de 5,5 à 0,67 minute) : les files d'attente sont non linéaires, et c'est ce qu'étudie la théorie évoquée au chapitre 2.

**Corrigé 7.** (a) Dans `[1, 2, 2, 2, 5]`, la première position où l'on peut insérer 2 sans casser l'ordre est l'indice 1 (juste devant le premier 2). (b) On cherche le **plus petit indice $p$ tel que `liste[p] >= x`** (ou $n$ s'il n'existe pas). *Invariant :* tous les éléments d'indice $<g$ sont $<x$ et tous ceux d'indice $\ge d$ sont $\ge x$. *Initialisation :* $g=0$, $d=n$ (zones vides). *Conservation :* si `liste[m] < x`, tous ceux d'indice $\le m$ sont $<x$ (liste triée) donc $g=m+1$ ; sinon tous ceux d'indice $\ge m$ sont $\ge x$ donc $d=m$. *Terminaison :* la zone $[g,d[$ perd au moins la moitié de sa taille à chaque tour. À la sortie $g=d$, et l'invariant dit que $g$ est la réponse. À la main sur $x=2$ : $[g,d[=[0,5[$, $m=2$, `liste[2]=2` n'est pas $<2$ donc $d=2$ ; $m=1$, même chose, $d=1$ ; $m=0$, `liste[0]=1<2` donc $g=1$ ; $g=d=1$ : réponse 1. (c) Les notes sont entières : le nombre de 5 vaut `première_position(liste, 6) − première_position(liste, 5)` ; le code trouve 104 notes de 5 sur 400, comme `Counter`.

```python
import bisect
import random
from collections import Counter


def premiere_position(triee, x):
    g, d = 0, len(triee)
    while g < d:
        m = (g + d) // 2
        if triee[m] < x:
            g = m + 1
        else:
            d = m
    return g


print("(a)", premiere_position([1, 2, 2, 2, 5], 2), "| occurrences de 2 :",
      premiere_position([1, 2, 2, 2, 5], 3) - premiere_position([1, 2, 2, 2, 5], 2))

notes = sorted(pd.read_csv("donnees/commandes.csv")["satisfaction"])
nb5 = premiere_position(notes, 6) - premiere_position(notes, 5)
print("(c) notes 5 :", nb5, "| Counter :", Counter(notes)[5])

random.seed(1)
for _ in range(1000):
    liste = sorted(random.choices(range(20), k=random.randint(0, 30)))
    x = random.randint(-1, 21)
    assert premiere_position(liste, x) == bisect.bisect_left(liste, x)
print("(d) 1000 listes aléatoires : même réponse que bisect_left")
```
<!--sortie-->
```text
(a) 1 | occurrences de 2 : 3
(c) notes 5 : 104 | Counter : 104
(d) 1000 listes aléatoires : même réponse que bisect_left
```

**Corrigé 8.** Les deux tris sont **stables** : le second préserve l'ordre produit par le premier pour les éléments à égalité. Il faut donc trier d'abord selon le critère **secondaire** (montant décroissant), puis selon le critère **principal** (canal).

```python
cmds = [("Site", 40.1), ("Boutique", 65.8), ("Site", 19.6), ("Boutique", 17.4), ("Instagram", 30.1), ("Site", 75.0)]
bon = sorted(sorted(cmds, key=lambda c: c[1], reverse=True), key=lambda c: c[0])
print("secondaire puis principal :")
for c in bon:
    print("  ", c)
mauvais = sorted(sorted(cmds, key=lambda c: c[0]), key=lambda c: c[1], reverse=True)
print("ordre inversé (faux) :")
for c in mauvais:
    print("  ", c)
```
<!--sortie-->
```text
secondaire puis principal :
   ('Boutique', 65.8)
   ('Boutique', 17.4)
   ('Instagram', 30.1)
   ('Site', 75.0)
   ('Site', 40.1)
   ('Site', 19.6)
ordre inversé (faux) :
   ('Site', 75.0)
   ('Boutique', 65.8)
   ('Site', 40.1)
   ('Instagram', 30.1)
   ('Site', 19.6)
   ('Boutique', 17.4)
```

Le bon résultat est Boutique (65,8 puis 17,4), Instagram (30,1), Site (75,0 ; 40,1 ; 19,6). Dans la version inversée, le dernier tri est celui des montants : les canaux sont mélangés, et leur ordre n'est conservé que pour les montants égaux, ce qui n'arrive pas ici. Raccourci équivalent : `sorted(cmds, key=lambda c: (c[0], -c[1]))`.

**Corrigé 9.** (a) Jour 1 : $2\times12{,}5+0\times8+1\times45+3\times15{,}9=25+45+47{,}7=117{,}7$. Jour 2 : $12{,}5+8=20{,}5$. Jour 3 : $4\times8+2\times45+15{,}9=32+90+15{,}9=137{,}9$. (b) Prix remisés : $12{,}5\;;\;7{,}2\;;\;45\;;\;12{,}72$. Jour 1 : $25+45+3\times12{,}72=108{,}16$ ; jour 2 : $12{,}5+7{,}2=19{,}7$ ; jour 3 : $4\times7{,}2+90+12{,}72=131{,}52$. (c) Unités par produit (somme des colonnes) : $3,\,5,\,3,\,4$ : la tasse.

```python
import numpy as np

Q = np.array([[2, 0, 1, 3], [1, 1, 0, 0], [0, 4, 2, 1]])
prix = np.array([12.5, 8, 45, 15.9])
promo = np.array([0, 0.10, 0, 0.20])

print("(a) CA par jour      :", Q @ prix)
print("(b) CA avec promotion :", (Q * (prix * (1 - promo))).sum(axis=1))
print("    formes :", Q.shape, "*", prix.shape, "->", (Q * prix).shape, "(le vecteur est répété sur chaque ligne)")
produits = ["bol", "tasse", "plateau", "bougie"]
print("(c) unités par produit :", {p: int(q) for p, q in zip(produits, Q.sum(axis=0))}, "-> meilleur :", produits[Q.sum(axis=0).argmax()])
```
<!--sortie-->
```text
(a) CA par jour      : [117.7  20.5 137.9]
(b) CA avec promotion : [108.16  19.7  131.52]
    formes : (3, 4) * (4,) -> (3, 4) (le vecteur est répété sur chaque ligne)
(c) unités par produit : {'bol': 3, 'tasse': 5, 'plateau': 3, 'bougie': 4} -> meilleur : tasse
```

`Q * prix` marche parce que les formes $(3,4)$ et $(4,)$ sont **compatibles** : NumPy « étire » le vecteur sur les trois lignes (broadcasting, 4.4.3). `axis=1` somme **le long des colonnes**, c'est-à-dire produit un total par ligne (par jour).

**Corrigé 10.** (a) Janvier : Instagram 50, Site 30, Boutique 0 (total 80). Février : Site $70+20=90$, Boutique 100 (total 190). Mars : Instagram 40 (total 40). (b) et (c) :

```python
mini = pd.DataFrame({
    "date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-02-02", "2026-02-10", "2026-02-11", "2026-03-01"]),
    "canal": ["Site", "Instagram", "Site", "Site", "Boutique", "Instagram"],
    "montant": [30, 50, 70, 20, 100, 40],
})
mini["mois"] = mini["date"].dt.month
tab = mini.pivot_table(index="mois", columns="canal", values="montant", aggfunc="sum", fill_value=0)
tab["total"] = tab.sum(axis=1)
print(tab)

# --- les 400 commandes, avec les colonnes simulées de 4.4.5 (même recette, même graine)
df = pd.read_csv("donnees/commandes.csv")
rng = np.random.default_rng(7)
jours = rng.integers(0, 140, size=len(df))
df["date"] = pd.Timestamp("2026-01-05") + pd.to_timedelta(jours, unit="D")
df["id_client"] = rng.integers(1, 121, size=len(df))
df = df.sort_values("date").reset_index(drop=True)
df["mois"] = df["date"].dt.month

par_mois = df.pivot_table(index="mois", columns="canal", values="montant", aggfunc="sum", fill_value=0).round(0)
par_mois["total"] = par_mois.sum(axis=1)
print()
print(par_mois)
print("mois le plus rentable :", par_mois["total"].idxmax(), "(", par_mois["total"].max(), "DT )")

noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
par_jour = df["date"].dt.dayofweek.value_counts().sort_index()
print()
print({noms[j]: int(n) for j, n in par_jour.items()})
print("jour le plus chargé :", noms[par_jour.idxmax()])
```
<!--sortie-->
```text
canal  Boutique  Instagram  Site  total
mois                                   
1             0         50    30     80
2           100          0    90    190
3             0         40     0     40

canal  Boutique  Instagram    Site   total
mois                                      
1        1861.0      853.0  1483.0  4197.0
2        1316.0     1366.0  1863.0  4545.0
3        1948.0     2073.0  2037.0  6058.0
4        1648.0      998.0  1752.0  4398.0
5        1755.0     1473.0  1672.0  4900.0
mois le plus rentable : 3 ( 6058.0 DT )

{'lundi': 53, 'mardi': 63, 'mercredi': 65, 'jeudi': 53, 'vendredi': 51, 'samedi': 52, 'dimanche': 63}
jour le plus chargé : mercredi
```

Le tableau de la main est reproduit exactement par `pivot_table` (le `fill_value=0` remplace les cases vides par 0 au lieu de `NaN`). Sur les 400 commandes, **mars** est le mois le plus rentable (6 058 DT). Attention toutefois à comparer des mois **inégalement couverts** : nos données vont du 5 janvier au 24 mai, donc janvier (27 jours) et mai (24 jours) sont incomplets, alors que mars l'est : un mois incomplet est un piège classique de lecture. Quant au jour de la semaine, les 140 jours de la période contiennent exactement 20 lundis, 20 mardis, etc. ; les dates ayant été tirées **au hasard et uniformément**, les écarts (de 51 commandes le vendredi à 65 le mercredi) ne sont que du hasard d'échantillonnage. Sur de vraies ventes, de telles différences guideraient les horaires d'ouverture ; ici, il ne faut surtout pas les « interpréter ».

**Corrigé 11.** (a) Les numéros 2 et 4 n'apparaissent dans aucune commande : ce sont les clients **dormants**. (b) et (c) :

```python
petit_clients = pd.DataFrame({"id_client": [1, 2, 3, 4, 5]})
petites_cmds = pd.DataFrame({"id_client": [1, 1, 3, 5]})
print("(a) sans commande :", petit_clients[~petit_clients["id_client"].isin(petites_cmds["id_client"])]["id_client"].tolist())

rng_c = np.random.default_rng(11)                                   # même recette qu'en 4.4.10
clients = pd.DataFrame({
    "id_client": np.arange(1, 126),
    "ville": rng_c.choice(["Tunis", "Sfax", "Sousse", "Nabeul", "Bizerte"], size=125, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
})

# méthode 1 : isin
dormants1 = clients[~clients["id_client"].isin(df["id_client"])]
# méthode 2 : jointure « left » depuis les clients, vers le nombre de commandes par client
nb_cmd = df.groupby("id_client").size().rename("nb_commandes").reset_index()
jointure = clients.merge(nb_cmd, on="id_client", how="left")
dormants2 = jointure[jointure["nb_commandes"].isna()]
print("(b) clients dormants :", len(dormants1), "=", len(dormants2), "| identiques :",
      dormants1["id_client"].tolist() == dormants2["id_client"].tolist())
print("    dont les clients 121 à 125 :", sorted(set(range(121, 126)) & set(dormants1["id_client"])))

ca_ville = df.merge(clients, on="id_client", how="left").groupby("ville")["montant"].sum().round(0).sort_values(ascending=False)
print("(c) CA par ville :")
print(ca_ville)
print("somme :", ca_ville.sum(), "| total des commandes :", round(df["montant"].sum()))
```
<!--sortie-->
```text
(a) sans commande : [2, 4]
(b) clients dormants : 11 = 11 | identiques : True
    dont les clients 121 à 125 : [121, 122, 123, 124, 125]
(c) CA par ville :
ville
Tunis      10491.0
Sousse      5492.0
Sfax        4518.0
Nabeul      2352.0
Bizerte     1245.0
Name: montant, dtype: float64
somme : 24098.0 | total des commandes : 24098
```

Le contrôle de cohérence final (la **somme par ville égale le total**) est un réflexe : une jointure qui dupliquerait ou perdrait des lignes (clés en double, clés absentes avec `inner`) fausserait silencieusement les totaux. C'est pourquoi on précise `how="left"` quand on veut conserver toutes les commandes. Onze clients sur 125 n'ont jamais commandé : les cinq clients 121 à 125 (dormants **par construction**, ce que le résultat confirme) et six autres que le hasard a laissés de côté. Tunis réalise à elle seule près de 44 % du chiffre d'affaires.

**Corrigé 12.** Le message est visible d'un coup d'œil si les barres sont triées et si l'axe part de zéro (la longueur de la barre porte l'information, voir 4.5.6).

```python
import os
import tempfile
import matplotlib.pyplot as plt

moy = df.groupby("canal")["montant"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 3.4))
barres = ax.bar(moy.index, moy.values, color="#2a78d6")
ax.bar_label(barres, fmt="%.1f")                                   # valeur écrite au-dessus de chaque barre
ax.set_ylim(bottom=0)
ax.set_title("La boutique a le panier moyen le plus élevé")
ax.set_xlabel("canal de vente")
ax.set_ylabel("montant moyen par commande (DT)")

chemin = os.path.join(tempfile.mkdtemp(), "panier-moyen.png")
fig.savefig(chemin, dpi=150, bbox_inches="tight")

print("ordre des barres :", [t.get_text() for t in ax.get_xticklabels()])
print("hauteurs = moyennes :", np.allclose([b.get_height() for b in barres], moy.values))
print("axe vertical démarre à :", ax.get_ylim()[0])
print("fichier enregistré :", os.path.getsize(chemin) > 0)
plt.close(fig)
```
<!--sortie-->
```text
ordre des barres : ['Boutique', 'Site', 'Instagram']
hauteurs = moyennes : True
axe vertical démarre à : 0.0
fichier enregistré : True
```

Les moyennes par canal sont celles obtenues au 4.1.9 (Boutique devant le Site, puis Instagram). **Défauts d'une version truquée :** (1) un axe tronqué (par exemple de 45 à 75 DT) ferait paraître la barre de la Boutique plusieurs fois plus haute que celle d'Instagram alors que l'écart réel est de l'ordre de 50 % ; (2) un camembert en 3D déforme les aires par la perspective et force l'œil à comparer des angles, ce qu'il fait très mal ; pour trois catégories, des barres triées sont toujours plus lisibles.

**Corrigé 13.** (a) Cas à tester : boutique à n'importe quel montant (0) ; Site à 99,99 (7) ; Site **à 100,00 exactement** (0, la borne) ; Site à 150 (0) ; Instagram à 50 (7) ; canal inconnu (erreur). Les **bornes** sont l'endroit où se cachent les bogues. (b) La version fautive utilise `>` : un panier à 100,00 DT pile paierait 7 DT.

```bash
cat > livraison_frais.py <<'FIN'
def frais_livraison(canal, total_ttc):
    """Frais de livraison en DT : 0 en boutique ; 7 DT sinon, offerts dès 100 DT TTC."""
    if canal == "Boutique":
        return 0.0
    if canal in ("Site", "Instagram"):
        return 0.0 if total_ttc > 100 else 7.0      # <-- défaut volontaire : devrait être >=
    raise ValueError(f"canal inconnu : {canal!r}")
FIN

cat > test_livraison_frais.py <<'FIN'
import pytest
from livraison_frais import frais_livraison

@pytest.mark.parametrize("canal, total, attendu", [
    ("Boutique", 20.0, 0.0),
    ("Site", 99.99, 7.0),
    ("Site", 100.0, 0.0),        # la borne : 100 compris
    ("Site", 150.0, 0.0),
    ("Instagram", 50.0, 7.0),
])
def test_frais(canal, total, attendu):
    assert frais_livraison(canal, total) == attendu

def test_canal_inconnu():
    with pytest.raises(ValueError):
        frais_livraison("Telephone", 10.0)
FIN

python -m pytest -q --color=no --tb=short -p no:cacheprovider test_livraison_frais.py 2>&1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
..F...                                                                   [100%]
=================================== FAILURES ===================================
__________________________ test_frais[Site-100.0-0.0] __________________________
test_livraison_frais.py:12: in test_frais
    assert frais_livraison(canal, total) == attendu
E   AssertionError: assert 7.0 == 0.0
E    +  where 7.0 = frais_livraison('Site', 100.0)
=========================== short test summary info ============================
FAILED test_livraison_frais.py::test_frais[Site-100.0-0.0] - AssertionError: ...
1 failed, 5 passed
```

Le test de la borne a trouvé le défaut : pour 100,00 DT, la fonction renvoie 7 au lieu de 0 ; les cinq autres tests passent, preuve qu'un test « du milieu » n'aurait rien vu. (c) On corrige (`>=`) et on relance :

```bash
sed -i 's/total_ttc > 100 else/total_ttc >= 100 else/; s/ *# <-- défaut volontaire.*//' livraison_frais.py
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_livraison_frais.py 2>&1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
......                                                                   [100%]
6 passed
```

> 🛠️ **À retenir.** On teste les **bornes** (juste en dessous, pile, juste au-dessus) et les **cas d'erreur**. Ces tests, écrits une fois, protégeront la règle des 100 DT de toute régression future.

**Corrigé 14.** (a) Le nombre de paires parmi $n$ éléments est $\binom n2=n(n-1)/2$ : pour $n=400$, $400\times399/2=79\,800$ ; pour $n=800$, $800\times799/2=319\,600$. Le facteur est $319\,600/79\,800\approx4{,}005$ : **doubler $n$ quadruple** le travail, signature d'un coût en $O(n^2)$. (b)–(d) :

```python
from math import comb
import time

ids = df["id_client"].tolist()                         # les 400 numéros de client (4.4.5)


def paires_double_boucle(ids):
    tours, paires = 0, 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            tours += 1
            if ids[i] == ids[j]:
                paires += 1
    return paires, tours


def paires_dictionnaire(ids):
    compteurs = {}
    for c in ids:                                       # un seul passage : O(n)
        compteurs[c] = compteurs.get(c, 0) + 1
    return sum(k * (k - 1) // 2 for k in compteurs.values()), len(ids)


for n in (200, 400):
    p1, tours = paires_double_boucle(ids[:n])
    p2, passages = paires_dictionnaire(ids[:n])
    print(f"n = {n} : double boucle {tours:>6} tours | dictionnaire {passages:>3} passages | "
          f"paires de même client : {p1} = {p2}")

t0 = time.perf_counter(); paires_double_boucle(ids); t1 = time.perf_counter()
paires_dictionnaire(ids); t2 = time.perf_counter()
print("la version dictionnaire est plus rapide :", (t2 - t1) < (t1 - t0))
print("rapport des tours quand n double (200 -> 400) :", round(79800 / 19900, 2), "pour la double boucle, 2.0 pour le dictionnaire")
print("(e) pour n = 1 000 000 :", f"{comb(1_000_000, 2):,}".replace(",", " "), "tours de double boucle")
```
<!--sortie-->
```text
n = 200 : double boucle  19900 tours | dictionnaire 200 passages | paires de même client : 212 = 212
n = 400 : double boucle  79800 tours | dictionnaire 400 passages | paires de même client : 702 = 702
la version dictionnaire est plus rapide : True
rapport des tours quand n double (200 -> 400) : 4.01 pour la double boucle, 2.0 pour le dictionnaire
(e) pour n = 1 000 000 : 499 999 500 000 tours de double boucle
```

Les deux versions comptent **le même nombre de paires** (702 parmi les 400 commandes, 212 parmi les 200 premières), mais l'une fait 79 800 tours et l'autre 400 passages. Quand $n$ passe de 200 à 400, la double boucle est $\approx4$ fois plus longue (19 900 → 79 800), le dictionnaire seulement 2 fois. À un million de commandes la double boucle ferait environ $5\times10^{11}$ tours, soit des heures voire des jours de calcul contre une fraction de seconde pour le dictionnaire : **même résultat, deux mondes de coûts**. Seule la mesure du temps dépend de la machine ; le booléen « le dictionnaire est plus rapide » vaut `True` partout, et les comptes de tours sont exacts.

---

## Bilan du chapitre 4

Vous savez maintenant :

- **programmer en Python** (4.1) : variables et types, collections (liste, tuple, dictionnaire, ensemble), conditions, boucles, fonctions, erreurs et `try / except`, lecture d'un fichier CSV, et un programme complet testé par `assert` ;
- **refaire les mêmes analyses en R** (4.2) : vecteurs, `data.frame`, tests statistiques « de la boîte », `dplyr` ; et savoir que Python et R donnent les mêmes nombres quand on leur pose la même question ;
- **raisonner comme un informaticien** (4.3) : choisir une structure (liste, dictionnaire, ensemble, pile, file), écrire une récursion avec son cas de base, prouver une dichotomie ou un tri par un invariant, et ne pas trier plus que nécessaire ;
- **manipuler des données** (4.4) : tableaux NumPy et broadcasting ; DataFrames pandas, sélection, `groupby`, jointures, valeurs manquantes, dates ;
- **dessiner honnêtement** (4.5) : choisir le bon graphique pour la question, l'anatomie d'un graphique matplotlib, seaborn, ggplot2, et les pièges du graphique trompeur (axe tronqué en tête) ;
- (en option, 4.6) **structurer et tester** : classes et dataclasses, code lisible, tests `pytest` qui visent les bornes ;
- (en option, 4.7) **situer** SAS, MATLAB et Julia par rapport à Python et R ;
- (en option, 4.8) **compter le coût** d'un algorithme (notation $O(\cdot)$), préférer la vectorisation, mémoïser, et mesurer avant d'optimiser.

> ✅ **Trois réflexes à emporter.** (1) *Calculer à la main un petit cas avant de coder* : c'est votre oracle. (2) *Lire le message d'erreur par la dernière ligne.* (3) *Vérifier un résultat par une seconde voie* (Python contre R, deux méthodes, une somme de contrôle).

Le chapitre 5 apprend à **aller chercher** les données là où elles vivent réellement : dans des bases de données relationnelles, avec le langage SQL. Vous y retrouverez `commandes.csv`, des jointures (comme en 4.4.10), des agrégations (comme le `groupby`) et l'idée de l'**index**, cet arbre trié qui permet une recherche dichotomique.
