# Chapitre 4 : Programmation

> « Les mathématiques vous disent **quoi** calculer.
> La programmation vous permet de le calculer sur **un million de lignes**. »

Jusqu'ici, nous avons utilisé du code comme un outil de vérification. Ce chapitre prend le code **au sérieux** : c'est lui qui transforme vos idées en résultats reproductibles. Pas besoin d'avoir jamais programmé : on part de zéro. Si vous programmez déjà, parcourez les premières sections en diagonale et attardez-vous sur NumPy, pandas et les visualisations.

## Le chemin de ce chapitre

- **4.1 Python** : le langage de ce livre, des variables aux fonctions, avec un petit programme complet (un ticket de caisse).
- **4.2 R** : l'autre grand langage de la statistique ; on refait les mêmes analyses pour comparer.
- **4.3 Algorithmes et structures de données** : piles, files, dictionnaires, récursion, tris, recherche. Penser comme un informaticien.
- **4.4 NumPy et pandas** : les deux bibliothèques qui font de Python un outil d'analyse de données.
- **4.5 Visualisations** : choisir le bon graphique, le tracer proprement, avec matplotlib, pandas, seaborn et ggplot2.
- ➕ **Pour aller plus loin** : programmation orientée objet, code propre et tests (4.6) ; d'autres langages (4.7) ; complexité algorithmique (4.8).
- Le **bilan** du chapitre ; les **applications et exercices corrigés** sont dans le **cahier** du volume.

> 💡 **Comment travailler avec ce chapitre.** *Tapez* le code vous-même plutôt que de le copier : c'est la seule façon d'apprendre à programmer. Modifiez-le, cassez-le, observez les messages d'erreur. Ils sont vos amis : un message d'erreur lu attentivement dit presque toujours où est le problème. Pour exécuter du code Python, vous pouvez utiliser un notebook Jupyter (section 6.2) ou simplement un terminal avec la commande `python`. Dans ce chapitre, le code est le sujet : il reste donc visible, mais **par petits morceaux**, toujours introduits et commentés. Les programmes complets et les études plus longues sont dans le cahier (chapitre 4).

> 📦 **Le fichier de données.** Au chapitre 3, nous avons construit un tableau de 400 commandes. Il a été enregistré dans le fichier `donnees/commandes.csv`, fourni avec le livre (c'est la sortie de `df.to_csv("donnees/commandes.csv", index=False)` appliqué au tableau du 3.1.2). Nous l'utiliserons pour les sections 4.2, 4.4 et 4.5, ainsi qu'au chapitre 5 (SQL).


## 4.1 Les fondamentaux de Python

> 💡 **Intuition.** Un programme est une **recette de cuisine** écrite pour un exécutant très docile mais totalement dépourvu de bon sens : il fait *exactement* ce que vous écrivez, à une vitesse folle, sans jamais se fatiguer, et sans jamais deviner ce que vous vouliez dire. Apprendre à programmer, c'est apprendre à écrire des recettes sans ambiguïté. Python est un excellent choix pour cela : ses recettes se lisent presque comme des phrases.

Dans cette section, nous partons de zéro et nous terminons par un **programme complet** : le ticket de caisse d'une boutique. Chaque notion suit le même rythme que dans le reste du livre : une image, un exemple fait à la main, puis un court morceau de code et sa sortie réelle.

> 🧭 **Section à lire dans l'ordre.** Si vous programmez déjà, lisez seulement les titres et les encadrés ⚠️, puis passez au petit programme final (4.1.10) pour vérifier que tout vous semble familier.

### 4.1.1 Pourquoi Python, et comment l'exécuter

Python est gratuit, lisible, et il dispose de milliers de bibliothèques pour les données (NumPy, pandas, SciPy, matplotlib…, que nous rencontrerons en 4.4 et 4.5). C'est le langage le plus utilisé en data science, et c'est celui des exemples de ce livre.

Il y a trois façons d'exécuter du code Python :

1. **Interactivement**, en tapant `python` dans un terminal : on écrit une ligne, on voit le résultat tout de suite. Idéal pour essayer.
2. **Dans un fichier** `mon_programme.py`, lancé avec `python mon_programme.py`. Idéal pour garder et rejouer son travail.
3. **Dans un notebook Jupyter** (section 6.2) : des cellules de code mélangées à du texte. Idéal pour explorer et raconter.

Le tout premier programme du monde informatique :

```python
print("Bonjour la boutique !")
print(2 + 3 * 4)
```
<!--sortie-->
```text
Bonjour la boutique !
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

**Exemple à la main.** La gérante vend 3 bols à 12,5 € hors taxe. Le total HT est $3\times12{,}5=37{,}5$ €. Avec 19 % de TVA : $37{,}5\times1{,}19=44{,}625$ €, soit 44,63 € si l'on arrondit « comme à l'école » (la moitié vers le haut). Faisons-le faire à Python :

```python
quantite, prix_ht = 3, 12.5
total_ttc = quantite * prix_ht * 1.19
print("total TTC :", total_ttc)
print("arrondi   :", round(total_ttc, 2))
print(type(quantite), type(prix_ht), type("bol"), type(True))
```
<!--sortie-->
```text
total TTC : 44.625
arrondi   : 44.62
<class 'int'> <class 'float'> <class 'str'> <class 'bool'>
```

Le total correspond au calcul à la main, **sauf l'arrondi** : Python affiche `44.62` et non 44,63. La raison : 44,625 tombe pile à mi-chemin entre 44,62 et 44,63, et `round` arrondit ces cas vers le chiffre **pair** (« arrondi du banquier »), d'où 44,62. Dans d'autres cas, c'est l'approximation binaire des décimaux (1.5.1) qui fait pencher l'arrondi d'un côté ou de l'autre. Pour des centimes exacts, on utilise le module `decimal` ; pour un ticket de caisse, on peut aussi calculer en **millimes** (entiers). Gardez cet écart en tête : il illustre qu'un résultat de programme se **vérifie** toujours contre un calcul indépendant. Notez enfin que `type(...)` révèle le type d'une valeur : une commande que vous utiliserez souvent pour comprendre une erreur.

Les opérateurs arithmétiques sont `+ - * /` et trois autres moins connus :

| Opérateur | Sens | Exemple | Résultat |
|---|---|---|---|
| `**` | puissance | `2 ** 10` | 1024 |
| `//` | division entière | `17 // 5` | 3 |
| `%` | reste (modulo) | `17 % 5` | 2 |

Par exemple, $17=3\times5+2$, d'où `17 // 5` $=3$ et `17 % 5` $=2$ ; un nombre est pair si son reste modulo 2 vaut 0. Quant à la division `/`, elle donne toujours un `float` : `17 / 5` vaut $3{,}4$.


> ⚠️ **Les décimaux sont approchés.** Python (comme tous les langages) stocke les `float` en binaire, ce qui explique les petites surprises du type $0{,}1+0{,}2\neq0{,}3$ expliquées en 1.5.1. Conséquence pratique : on **n'écrit jamais** `a == b` pour comparer deux décimaux calculés, on utilise `math.isclose(a, b)`. Et pour des montants d'argent, on arrondit explicitement avec `round(x, 2)` à l'affichage.

### 4.1.3 Le texte et les f-strings

Un texte (`str`) s'écrit entre guillemets. On peut le découper, le mettre en majuscules, le chercher :

```python
nom = "  Bol en céramique bleue "
print(nom.strip().upper())
print(nom.strip().replace("bleue", "verte"))
print(len(nom.strip()), "céramique" in nom)       # longueur, présence d'un morceau
print(nom.strip().split(" "))                      # découpe en liste de mots
```
<!--sortie-->
```text
BOL EN CÉRAMIQUE BLEUE
Bol en céramique verte
22 True
['Bol', 'en', 'céramique', 'bleue']
```

Pour **insérer des valeurs dans une phrase**, la méthode moderne est la **f-string** : on fait précéder le guillemet d'un `f` et on met les valeurs entre accolades. Après les deux-points, on peut régler le format.

```python
produit, quantite, prix = "bol", 3, 12.5
print(f"{quantite} x {produit} à {prix} €")
print(f"total : {quantite * prix:.2f} €  (TVA {0.19:.0%})")      # .2f : 2 décimales ; .0% : pourcentage
```
<!--sortie-->
```text
3 x bol à 12.5 €
total : 37.50 €  (TVA 19%)
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
print(montants[0], montants[-1], montants[1:4])     # premier, dernier, indices 1 à 3
montants.append(39.8)                                # ajoute à la fin
print(len(montants), sum(montants), max(montants), min(montants))
print(sorted(montants))                              # copie triée ; l'original ne change pas
```
<!--sortie-->
```text
44.8 110.1 [34.5, 88.2, 30.1]
6 347.5 110.1 30.1
[30.1, 34.5, 39.8, 44.8, 88.2, 110.1]
```

> ⚠️ **Piège classique du débutant : le décalage de 1.** Dans une liste de 6 éléments, les indices vont de 0 à **5** ; `montants[6]` provoque une erreur. Et `montants[1:4]` contient **3** éléments (1, 2, 3), pas 4. Règle : la longueur d'un découpage est `b - a`.

**Les tuples** sont des listes figées : une fois créés on ne les modifie plus. Parfaits pour des paires qui ne doivent pas bouger, comme (code produit, quantité).

**Les dictionnaires** associent une **clé** à une **valeur**, comme un annuaire : on cherche par le nom, pas par la position.

```python
catalogue = {"bol": 12.5, "tasse": 8.0, "plateau": 45.0}
catalogue["bougie"] = 15.9                           # ajout
print(catalogue["tasse"], catalogue.get("lampe", "inconnu"))   # .get évite l'erreur
for nom, prix in catalogue.items():
    print(f"  {nom:<8} {prix:>6.2f} €")
```
<!--sortie-->
```text
8.0 inconnu
  bol       12.50 €
  tasse      8.00 €
  plateau   45.00 €
  bougie    15.90 €
```

**Les ensembles** oublient l'ordre et éliminent les doublons : exactement ce qu'il faut pour compter des clients **distincts**.

```python
acheteurs = ["Léa", "Hugo", "Léa", "Inès", "Hugo", "Léa"]
distincts = set(acheteurs)
print(len(acheteurs), "achats par", len(distincts), "clients distincts")
print(sorted(distincts))              # trié pour un affichage stable
```
<!--sortie-->
```text
6 achats par 3 clients distincts
['Hugo', 'Inès', 'Léa']
```

L'ordre d'affichage d'un ensemble peut changer d'une exécution à l'autre : n'y comptez jamais (c'est pourquoi nous l'avons passé par `sorted` pour l'afficher).

### 4.1.5 Décider : conditions

Un programme doit pouvoir **choisir**. L'instruction `if` exécute un bloc seulement si la condition est vraie. En Python, **l'indentation** (4 espaces) délimite le bloc : c'est la grammaire du langage, pas un détail de présentation.

Comparaisons : `==` (égal), `!=` (différent), `<`, `<=`, `>`, `>=`. Combinaisons : `and`, `or`, `not`.

**Exemple à la main.** Règle de livraison de la boutique : *gratuite à partir de 100 €, sinon 7 € ; et pour un retrait en boutique, toujours 0.* Pour un panier de 80 € livré : 7 €. Pour 120 € livré : 0. Pour 80 € en retrait : 0.

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

**Exemple à la main.** La gérante place 1 000 € à 5 % par an, intérêts composés. Au bout d'un an : $1000\times1{,}05=1050$. Deux ans : $1050\times1{,}05=1102{,}5$. Combien d'années pour **doubler** ? C'est une question « jusqu'à ce que » : une boucle `while`.

```python
capital, annees = 1000.0, 0
while capital < 2000:
    capital = capital * 1.05
    annees += 1                       # raccourci pour annees = annees + 1
print("doublé en", annees, "ans :", round(capital, 2), "€")
```
<!--sortie-->
```text
doublé en 15 ans : 2078.93 €
```

Vérification mathématique : on cherche le plus petit $n$ tel que $1{,}05^n\ge2$, soit $n\ge\ln 2/\ln1{,}05\approx14{,}21$.


Le résultat réel (14,21) est entre 14 et 15 : il faut donc 15 années entières, ce que la boucle a trouvé.

> ⚠️ **La boucle infinie.** Si, dans un `while`, la condition ne devient jamais fausse (ici, si on oubliait la ligne `capital = ...`), le programme tourne éternellement. Dans un terminal, `Ctrl+C` l'arrête. Avant de lancer un `while`, demandez-vous : *qu'est-ce qui le fera s'arrêter ?* (La même question sera posée avec rigueur pour les algorithmes en 4.3.)

La boucle `for` parcourt n'importe quelle collection ; `range(n)` produit les entiers de 0 à $n-1$, et `enumerate` donne en plus la position :

```python
for i in range(3):
    print("i =", i)
for rang, nom in enumerate(["Léa", "Hugo", "Inès"], start=1):
    print(rang, nom)
```
<!--sortie-->
```text
i = 0
i = 1
i = 2
1 Léa
2 Hugo
3 Inès
```

**Les compréhensions de liste** sont une écriture compacte d'une boucle qui construit une liste : `[expression for x in collection if condition]`. Elles se lisent comme une phrase mathématique « l'ensemble des $f(x)$ pour $x$ dans… tel que… ».

```python
montants = [44.8, 34.5, 88.2, 30.1, 110.1, 39.8, 74.7]
ttc = [round(m * 1.19, 2) for m in montants]
gros = [m for m in montants if m > 60]
print(ttc)
print(gros)
print({n: n ** 2 for n in range(1, 6)})      # même idée pour un dictionnaire
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
commandes = [("Léa", 44.8), ("Hugo", 110.1), ("Inès", 30.1)]
print(sorted(commandes, key=lambda c: c[1]))                   # du plus petit au plus gros montant
print(sorted(commandes, key=lambda c: c[1], reverse=True)[0])  # la plus grosse
```
<!--sortie-->
```text
[('Inès', 30.1), ('Léa', 44.8), ('Hugo', 110.1)]
('Hugo', 110.1)
```

`lambda c: c[1]` est une mini-fonction sans nom qui renvoie le second élément du couple.

### 4.1.8 Les erreurs : vos meilleures amies

Quand quelque chose ne va pas, Python s'arrête et affiche un **message d'erreur** (*traceback*). Il se lit **de bas en haut** : la dernière ligne dit *quel type d'erreur* et *pourquoi* ; les lignes au-dessus disent *où*. Voici les erreurs que vous rencontrerez le plus souvent, provoquées volontairement et rattrapées avec `try / except` pour pouvoir les afficher :

```python
def tenter(description, fonction):
    try:
        fonction()
    except Exception as e:
        print(f"{description:<20} -> {type(e).__name__}: {e}")

tenter("indice hors liste", lambda: [44.8, 34.5, 88.2][5])
tenter("clé absente", lambda: {"bol": 12.5}["lampe"])
tenter("division par zéro", lambda: 10 / 0)
tenter("texte + nombre", lambda: "total : " + 12.5)
tenter("texte vers entier", lambda: int("douze"))
tenter("nom inconnu", lambda: variable_inexistante)
```
<!--sortie-->
```text
indice hors liste    -> IndexError: list index out of range
clé absente          -> KeyError: 'lampe'
division par zéro    -> ZeroDivisionError: division by zero
texte + nombre       -> TypeError: can only concatenate str (not "float") to str
texte vers entier    -> ValueError: invalid literal for int() with base 10: 'douze'
nom inconnu          -> NameError: name 'variable_inexistante' is not defined
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
valides = []
for s in saisies:
    try:
        valides.append(float(s))
    except ValueError:
        print("rejetée :", repr(s))
print("valides :", valides)
```
<!--sortie-->
```text
rejetée : 'abc'
rejetée : ''
rejetée : '15,9'
valides : [12.5, 8.0, 45.0]
```

Remarquez que `"15,9"` (virgule française) est rejeté : Python attend le **point** décimal. C'est une cause fréquente de données « cassées » quand elles viennent d'un tableur configuré en français.

> 💡 **Méthode pour déboguer** (à épingler au-dessus de votre écran). (1) Lisez la **dernière ligne** du message. (2) Repérez la ligne de code citée. (3) Affichez avec `print` les valeurs et les types utilisés à cet endroit. (4) Réduisez le problème au plus petit exemple qui échoue. (5) Seulement ensuite, cherchez le message sur Internet. Neuf fois sur dix, les étapes 1 à 3 suffisent.

### 4.1.9 Modules, fichiers et données réelles

Python ne contient pas tout, mais il sait **importer** du code déjà écrit. Un **module** est un fichier de fonctions ; la bibliothèque standard en fournit des dizaines (`math`, `random`, `statistics`, `csv`, `datetime`…), et on en installe d'autres avec `pip` (section 6.3).

```python
import math, statistics
from collections import Counter

print(math.sqrt(144), statistics.mean([2, 4, 4, 4, 5, 5, 7, 9]))
print(Counter("abracadabra"))     # compte les occurrences
```
<!--sortie-->
```text
12.0 5
Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
```

Lisons maintenant le fichier de données du livre, `donnees/commandes.csv`, **sans aucune bibliothèque externe**, avec le module `csv`. Un fichier CSV est du texte brut : une ligne par commande, des valeurs séparées par des virgules, la première ligne contenant les noms des colonnes.

```python
import csv

with open("donnees/commandes.csv", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))     # chaque ligne devient un dictionnaire
print(len(lignes), "commandes ; première :", lignes[0])
print("type du montant :", type(lignes[0]["montant"]))
```
<!--sortie-->
```text
400 commandes ; première : {'canal': 'Boutique', 'montant': '44.8', 'livraison': '0', 'satisfaction': '4'}
type du montant : <class 'str'>
```

Le mot-clé `with` ouvre le fichier **et le referme proprement** à la sortie du bloc, même en cas d'erreur. Remarquez que les valeurs sont lues comme du **texte** : `"44.8"` n'est pas un nombre ! Il faut convertir.

```python
montants = [float(l["montant"]) for l in lignes]
print("montant moyen :", round(sum(montants) / len(montants), 2))

par_canal = {}                           # un dictionnaire de listes
for l in lignes:
    par_canal.setdefault(l["canal"], []).append(float(l["montant"]))
for canal, valeurs in par_canal.items():
    print(f"  {canal:<10} n = {len(valeurs):3d}   moyenne = {sum(valeurs) / len(valeurs):6.2f} €")
```
<!--sortie-->
```text
montant moyen : 60.25
  Boutique   n = 114   moyenne =  74.81 €
  Site       n = 148   moyenne =  59.50 €
  Réseaux    n = 138   moyenne =  49.01 €
```

On retrouve le montant moyen de 60,25 € calculé au chapitre 3. Nous avons tout fait à la main, avec des boucles et des dictionnaires : c'est précisément le travail que pandas fera en **une ligne** à la section 4.4. Savoir le faire « à la main » vous permet de comprendre ce que pandas fait pour vous.

### 4.1.10 Un petit programme complet : le ticket de caisse

Rassemblons tout. La gérante veut un petit programme qui, pour un panier, **édite un ticket de caisse** avec les règles suivantes :

- les prix du catalogue sont **hors taxe** ;
- une **remise fidélité de 10 %** s'applique si le sous-total HT dépasse 100 € ;
- la **TVA de 19 %** s'applique sur le montant après remise ;
- le ticket affiche chaque ligne, le sous-total, la remise, la TVA et le total TTC.

**Calcul à la main** pour le panier « 2 bols, 1 plateau, 3 bougies » (prix HT : bol 12,5 ; plateau 45 ; bougie 15,9) :

- bols : $2\times12{,}5=25{,}00$ ; plateau : $45{,}00$ ; bougies : $3\times15{,}9=47{,}70$ ;
- sous-total HT : $25+45+47{,}7=117{,}70$ € ;
- le sous-total dépasse 100 €, donc remise de $10\%$ : $11{,}77$ €, soit $105{,}93$ € après remise ;
- TVA : $105{,}93\times0{,}19=20{,}1267\approx20{,}13$ € ;
- total TTC : $105{,}93+20{,}13=126{,}06$ €.

Le programme se découpe en **petites fonctions** faciles à tester. Les deux premières suffisent à calculer les montants :

```python
CATALOGUE = {"bol": 12.5, "tasse": 8.0, "plateau": 45.0, "bougie": 15.9}
TVA, SEUIL_REMISE, TAUX_REMISE = 0.19, 100, 0.10

def sous_total(panier):
    """panier : liste de couples (produit, quantité)."""
    return sum(CATALOGUE[nom] * qte for nom, qte in panier)

def remise(montant_ht):
    return montant_ht * TAUX_REMISE if montant_ht > SEUIL_REMISE else 0.0
```

Une troisième fonction, `ticket`, appelle les deux premières puis met le résultat en forme avec des f-strings (l'application 4.1 du cahier la construit pas à pas). Pour notre panier, elle produit :

```text
=== BOUTIQUE ===
2 x bol       12.50     25.00
1 x plateau   45.00     45.00
3 x bougie    15.90     47.70
Sous-total HT         117.70
Remise fidélité       -11.77
TVA 19 %               20.13
TOTAL TTC             126.06
```

Le ticket affiche 117,70 € de sous-total, 11,77 de remise, 20,13 de TVA et 126,06 € au total : **exactement** nos valeurs à la main. Testons aussi les cas limites avec `assert`, une instruction qui ne dit rien quand la condition est vraie et **arrête** le programme avec une erreur quand elle est fausse :

```python
assert remise(100) == 0.0                          # pile au seuil : pas de remise (condition « > »)
assert ticket([("tasse", 2)])[1] == 19.04          # 2 tasses : 16,00 HT ; TVA 3,04
assert ticket([])[1] == 0.0                        # panier vide
assert ticket([("bol", 2), ("plateau", 1), ("bougie", 3)])[1] == 126.06
print("tous les tests passent")
```
<!--sortie-->
```text
tous les tests passent
```

> 💡 **Ce qu'on vient de faire, c'est de la rigueur.** Calculer à la main *avant* de coder fournit un « oracle » : si le programme et la main divergent, l'un des deux a tort, et on cherche lequel. Les `assert` transforment cette vérification en filet de sécurité automatique. Nous irons plus loin avec de vrais tests unitaires en 4.6.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1 (le programme complet de la caisse) ; exercices 4.1 à 4.3 (dictionnaires et boucles, produit absent du catalogue, code promo).

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
x <- 12.5            # l'affectation s'écrit « <- » (le « = » marche aussi, mais on utilise « <- »)
x * 3
print("Bonjour la boutique !")
```
<!--sortie-->
```text
[1] 37.5
[1] "Bonjour la boutique !"
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

**Exemple à la main.** Quatre commandes de 44,8 ; 34,5 ; 88,2 et 30,1 €. Leur somme est $197{,}6$, leur moyenne $49{,}4$ €. Avec 19 % de TVA, chaque montant est multiplié par 1,19 : $44{,}8\to53{,}31$ (arrondi), etc.

```r
montants <- c(44.8, 34.5, 88.2, 30.1)
c(sum(montants), mean(montants))
round(montants * 1.19, 2)       # la multiplication s'applique à chaque élément
montants[2:3]                   # éléments 2 et 3 (bornes incluses)
montants[-1]                    # indice négatif : tout SAUF le premier
montants[montants > 40]         # sélection par condition
```
<!--sortie-->
```text
[1] 197.6  49.4
[1]  53.31  41.06 104.96  35.82
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
```
<!--sortie-->
```text
[1] NA
[1] 12
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

Les conditions s'écrivent avec `if` / `else`, et la version vectorisée avec `ifelse` :

```r
frais_livraison <- function(total, retrait_boutique) {
  if (retrait_boutique) 0 else if (total >= 100) 0 else 7
}
c(frais_livraison(80, FALSE), frais_livraison(120, FALSE), frais_livraison(80, TRUE))

ifelse(c(80, 120, 100, 35) >= 100, 0, 7)     # version vectorisée de « si… alors… sinon »
```
<!--sortie-->
```text
[1] 7 0 0
[1] 7 0 0 7
```


On retrouve 7, 0, 0 pour les frais ; la boucle `while (capital < 2000) { … }` s'écrit presque comme en Python et trouve elle aussi 15 années pour doubler un capital placé à 5 % : exactement ce que Python a donné en 4.1. La fonction `ifelse` applique le test à **chaque élément** d'un vecteur, ce que `if` ne sait pas faire.

> ⚠️ **Piège de la vectorisation.** `if (totaux >= 100)` appliqué à un vecteur de plusieurs éléments n'a pas de sens : `if` attend **un seul** vrai/faux. Utilisez `ifelse` pour les vecteurs.

**Le dictionnaire de R.** Un vecteur dont les éléments portent un **nom** joue le rôle du dictionnaire de Python : on retrouve un prix par son nom, ou plusieurs d'un coup. Le ticket de caisse de 4.1.10 se refait en quelques lignes grâce à la vectorisation (c'est l'application 4.2 du cahier).

```r
catalogue <- c(bol = 12.5, tasse = 8.0, plateau = 45.0, bougie = 15.9)   # un vecteur nommé joue le rôle du dictionnaire
catalogue[c("bol", "bougie")]
```
<!--sortie-->
```text
   bol bougie 
  12.5   15.9 
```

### 4.2.4 Le `data.frame` : le tableau de données

Le tableau est **l'objet central de R**. Un `data.frame` est un tableau dont chaque colonne est un vecteur (de types éventuellement différents). Chargeons les commandes, avec les trois gestes de 3.1.2 : forme, types, résumé.

```r
df <- read.csv("donnees/commandes.csv")      # lit le CSV directement en tableau
str(df)                                      # structure : type de chaque colonne
```
<!--sortie-->
```text
'data.frame':	400 obs. of  4 variables:
 $ canal       : chr  "Boutique" "Site" "Réseaux" "Réseaux" ...
 $ montant     : num  44.8 34.5 88.2 30.1 110.1 ...
 $ livraison   : int  0 2 5 4 0 5 0 0 5 6 ...
 $ satisfaction: int  4 4 4 4 5 3 5 4 4 3 ...
```

`read.csv` a deviné les types : `canal` est du texte (`chr`), les trois autres colonnes sont numériques. Contrairement au module `csv` de Python (4.1.9) qui lisait tout en texte, la conversion est faite pour nous. Le résumé numérique :

```r
summary(df)
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
tapply(df$montant, df$canal, mean)                    # moyenne par canal
aggregate(montant ~ canal, data = df, FUN = mean)     # même chose, avec la notation « formule »
```
<!--sortie-->
```text
Boutique  Réseaux     Site 
74.80965 49.01087 59.50338 
     canal  montant
1 Boutique 74.80965
2  Réseaux 49.01087
3     Site 59.50338
```

La formule `montant ~ canal` se lit « le montant **en fonction du** canal » : cette notation en tilde est partout en R (nous la retrouverons pour les modèles de régression au volume suivant). Les moyennes par canal (74,81 ; 59,50 ; 49,01) sont celles que nous avions obtenues avec Python au 4.1.9, à la main.

### 4.2.5 Les statistiques « sortent de la boîte »

C'est ici que R brille : les procédures de la statistique classique sont **au catalogue de base**, sans rien installer.

**Intervalle de confiance et test de Welch.** Rappel du 3.3 et du 3.4 : IC à 95 % de la moyenne, [56,51 ; 63,98] ; test boutique contre Réseaux, $t=5{,}565$, 208,4 degrés de liberté, $p\approx8\times10^{-8}$.


```r
b <- df$montant[df$canal == "Boutique"]
i <- df$montant[df$canal == "Réseaux"]
w <- t.test(b, i)                            # R fait le test de Welch par défaut
c(t = unname(w$statistic), ddl = unname(w$parameter), p = w$p.value)
round(w$conf.int, 1)                         # IC95 % de la différence des moyennes
```
<!--sortie-->
```text
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
library(dplyr)

df |>
  group_by(canal) |>
  summarise(n = n(), panier_moyen = round(mean(montant), 2),
            satisfaction = round(mean(satisfaction), 2)) |>
  arrange(desc(panier_moyen))
```
<!--sortie-->
```text

Attaching package: ‘dplyr’

The following objects are masked from ‘package:stats’:

    filter, lag

The following objects are masked from ‘package:base’:

    intersect, setdiff, setequal, union

# A tibble: 3 × 4
  canal        n panier_moyen satisfaction
  <chr>    <int>        <dbl>        <dbl>
1 Boutique   114         74.8         4.49
2 Site       148         59.5         3.79
3 Réseaux    138         49.0         3.72
```

Lisez cette « phrase » à voix haute : *prends le tableau des commandes, puis groupe par canal, puis résume (effectif, panier moyen, écart-type, satisfaction), puis trie par panier moyen décroissant.* C'est presque du français, et c'est ce qui rend le tidyverse si agréable à lire. Une seconde phrase, avec filtre et colonne calculée :

```r
df |>
  filter(canal != "Boutique", livraison > 8) |>      # livraisons lentes
  mutate(montant_ttc = round(montant * 1.19, 2)) |>
  select(canal, montant, montant_ttc, livraison, satisfaction) |>
  head(3)
```
<!--sortie-->
```text
    canal montant montant_ttc livraison satisfaction
1    Site    40.1       47.72        13            2
2 Réseaux    61.1       72.71         9            4
3    Site    65.4       77.83        10            3
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

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2 (le ticket de caisse en R) ; exercice 4.4 (part de commandes satisfaites, en R de base, avec `dplyr` et avec pandas).

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

Résultat : 110,1. En code :

```python
def plus_grand(valeurs):
    record = valeurs[0]
    for v in valeurs[1:]:
        if v > record:
            record = v
    return record

print(plus_grand([44.8, 34.5, 88.2, 30.1, 110.1]))
```
<!--sortie-->
```text
110.1
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

**Pourquoi un dictionnaire ou un ensemble est-il si rapide ?** Ils reposent sur une **table de hachage** : une fonction (le *hachage*) transforme la clé en un numéro de case, et l'on va **directement** à cette case, sans parcourir quoi que ce soit. Imaginez un vestiaire où chaque cintre porte le numéro calculé à partir du nom du client : pas besoin de passer en revue tous les manteaux. Une liste, elle, doit être parcourue de gauche à droite pour savoir si une valeur y figure : c'est la **recherche linéaire**, une boucle `for` qui compare chaque élément à la cible. Mesurons ce parcours en **nombre de comparaisons** (une mesure qui ne dépend pas de l'ordinateur) sur la liste `montants` des 400 montants lus en 4.1.9 : trouver 44,8, qui est en tête, coûte **1** comparaison ; trouver la plus grosse commande (255,7) en coûte **157** ; et constater qu'une valeur est **absente** (1,0) en coûte **400**.


Quand la valeur est **absente**, il faut lire les 400 éléments pour en être sûr : le pire cas est proportionnel à la taille de la liste. Un ensemble ou un dictionnaire, lui, répond en une seule opération, quel que soit le nombre d'éléments. Nous mesurerons l'écart en secondes à la section 4.8 ; retenez pour l'instant l'ordre de grandeur : pour un million d'éléments, une liste doit parcourir *jusqu'à un million* de cases, un ensemble en regarde *quelques-unes*.

Application directe : **compter les montants différents** et **les plus fréquents** (`montants` est la liste des 400 montants) :

```python
from collections import Counter

print("montants distincts :", len(set(montants)), "sur", len(montants), "commandes")
print(Counter(montants).most_common(3))      # un Counter est un dictionnaire de comptage
```
<!--sortie-->
```text
montants distincts : 344 sur 400 commandes
[(37.5, 4), (53.5, 4), (65.8, 3)]
```

Un `Counter` est un dictionnaire spécialisé dans le comptage : la clé est la valeur, la valeur est son nombre d'occurrences. C'est l'outil idéal pour une table de fréquences (3.1) construite à la main.

### 4.3.3 Piles et files

Deux structures très simples, définies par **l'ordre** dans lequel on y entre et sort.

- La **pile** (*stack*, **LIFO** : *last in, first out*) : le dernier arrivé est le premier servi. Une pile d'assiettes : on pose et on reprend toujours en haut. C'est le mécanisme du bouton « annuler » de votre éditeur de texte, et de l'**historique** de votre navigateur.
- La **file** (*queue*, **FIFO** : *first in, first out*) : le premier arrivé est le premier servi. La file d'attente à la caisse.

En Python, une pile est une simple liste que l'on manipule **par la fin** (`append` pour empiler, `pop` pour dépiler). Pour une file, on utilise `deque` (prononcez « dèque »), car retirer un élément au **début** d'une liste est lent, alors qu'un `deque` le fait à coût constant.

```python
from collections import deque

pile = ["ajouter bol", "ajouter tasse", "ajouter plateau"]       # une liste utilisée par la fin
print("annuler :", pile.pop(), "| il reste :", pile)
file = deque(["Léa", "Hugo", "Inès"])
print("servi :", file.popleft(), "| il reste :", list(file))
```
<!--sortie-->
```text
annuler : ajouter plateau | il reste : ['ajouter bol', 'ajouter tasse']
servi : Léa | il reste : ['Hugo', 'Inès']
```

**Exemple : vérifier les parenthèses d'une formule (avec une pile).** Un tableur doit rejeter `=(B2+B3)*(1-(C2/100)` car il manque une parenthèse fermante. Comment un programme le détecte-t-il ?

*Idée :* à chaque parenthèse **ouvrante**, on empile ; à chaque parenthèse **fermante**, on dépile et on vérifie qu'elle correspond. La formule est correcte si, **à la fin**, la pile est vide et si nous n'avons jamais dû dépiler une pile vide.

**À la main** sur `(1+(2*3))` : `(` → pile `[(]` ; `1`, `+` ignorés ; `(` → `[(, (]` ; `2*3` ignorés ; `)` → on dépile : `[(]` ; `)` → on dépile : `[]`. Pile vide à la fin : équilibrée. Sur `(1+2))` : après le premier `)` la pile est vide ; le second `)` ne trouve rien à dépiler : **erreur**.

```python
def equilibre(formule):
    ouvrantes, pile = {")": "(", "]": "[", "}": "{"}, []
    for c in formule:
        if c in "([{":
            pile.append(c)
        elif c in ")]}" and (not pile or pile.pop() != ouvrantes[c]):
            return False
    return not pile            # vrai seulement si tout a été refermé

print([equilibre(t) for t in ["(1+(2*3))", "(1+2))", "(1-(C2/100)", "[(1+2]*3)", ""]])
```
<!--sortie-->
```text
[True, False, False, False, True]
```

Le cas `[(1+2]*3)` est instructif : il y a autant d'ouvrantes que de fermantes, mais elles sont **mal imbriquées** : une simple comptabilité ne suffirait pas, la pile, si. Voilà pourquoi tous les compilateurs et analyseurs de formules utilisent cette structure.

Avec une file, on peut aussi **simuler** une caisse ou un atelier d'emballage : les commandes arrivent, attendent leur tour, sont traitées une à une. C'est le premier pas vers la **théorie des files d'attente** vue au chapitre 2 (processus de Poisson et loi exponentielle). Le cahier en propose une simulation complète (application 4.3).

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

**Une application naturelle : parcourir un arbre.** Le catalogue de la boutique est un dictionnaire de dictionnaires : des catégories contenant des sous-catégories contenant des produits `(prix, stock)`. On veut la **valeur totale du stock**. La difficulté : on ne sait pas combien de niveaux il y a. La récursion le fait tout naturellement : *la valeur d'une catégorie est la somme des valeurs de ses éléments, la valeur d'un produit est prix × stock.*

**À la main** : bol bleu $12{,}5\times10=125$ ; bol vert $12{,}5\times4=50$ ; tasse $8\times20=160$ ; bougie $15{,}9\times6=95{,}4$ ; plateau $45\times2=90$. Total : $520{,}4$ €. La fonction ci-dessous le retrouve sur ce catalogue.


```python
def valeur_stock(noeud):
    if isinstance(noeud, tuple):                     # cas de base : un produit (prix, stock)
        prix, stock = noeud
        return prix * stock
    return sum(valeur_stock(enfant) for enfant in noeud.values())   # une catégorie

print(round(valeur_stock(catalogue), 2), "€")
```
<!--sortie-->
```text
520.4 €
```

**Le danger : la récursion naïve peut être catastrophique.** Les nombres de Fibonacci ($F_0=0$, $F_1=1$, $F_n=F_{n-1}+F_{n-2}$) se codent en deux lignes récursives, mais le programme refait **sans cesse les mêmes calculs** : pour calculer `fib(5)`, on calcule deux fois `fib(3)`, trois fois `fib(2)`, etc. En comptant les appels de la version naïve, on trouve 177 appels pour $n=10$, 21 891 pour $n=20$ et **242 785** pour $n=25$. Une seule ligne ajoutée, le décorateur `lru_cache`, qui retient chaque résultat déjà calculé, change tout :


```python
from functools import lru_cache

@lru_cache(maxsize=None)       # « mémoïsation » : on retient les résultats déjà calculés
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(25))
```
<!--sortie-->
```text
75025
```

Le nombre d'appels de la version naïve **explose** (il est lui-même de l'ordre de $F_n$, donc il croît environ de 62 % à chaque pas), alors que la version qui **mémorise** ne calcule chaque valeur qu'une seule fois (26 exécutions réelles pour $n=25$). Même problème, même résultat, des ordres de grandeur d'écart : c'est tout l'enjeu de la complexité (section ➕ 4.8). La mémoïsation est la première idée de la **programmation dynamique**, très utilisée en optimisation.

> ⚠️ **Récursion ou boucle ?** Tout algorithme récursif peut s'écrire avec une boucle (et inversement). La récursion est souvent plus *lisible* pour les structures **arborescentes** (catalogue, dossiers, expressions) ; la boucle est plus économe en mémoire. Python limite la profondeur de récursion à environ 1 000 appels : au-delà, préférez une boucle.

### 4.3.5 Rechercher : de la liste à la dichotomie

Reprenons la **recherche linéaire** de 4.3.2 : sur une liste quelconque, elle est inévitable. Mais si la liste est **triée**, on peut faire beaucoup mieux, comme quand vous cherchez un mot dans un dictionnaire papier : vous ouvrez au milieu, vous voyez si le mot est avant ou après, et vous éliminez **la moitié** des pages d'un coup. C'est la **recherche dichotomique** (*binary search*).

**À la main.** Liste triée de 9 montants : $[8;\ 15;\ 22;\ 31;\ 40;\ 47;\ 58;\ 66;\ 79]$ (indices 0 à 8). On cherche 47.

| Étape | Zone d'indices $[g,d]$ | Milieu $m=\lfloor(g+d)/2\rfloor$ | Valeur | Décision |
|---|---|---|---|---|
| 1 | $[0,8]$ | 4 | 40 | $40<47$ : on cherche à droite, $g=5$ |
| 2 | $[5,8]$ | 6 | 58 | $58>47$ : on cherche à gauche, $d=5$ |
| 3 | $[5,5]$ | 5 | 47 | trouvé ! |

Trois étapes au lieu de six pour la recherche linéaire. Le programme (il renvoie la position, ou $-1$) :

```python
def recherche_dichotomique(triee, cible):
    """Renvoie la position de la cible, ou -1. La liste doit être triée."""
    g, d = 0, len(triee) - 1
    while g <= d:
        m = (g + d) // 2
        if triee[m] == cible:
            return m
        elif triee[m] < cible:
            g = m + 1
        else:
            d = m - 1
    return -1

print(recherche_dichotomique([8, 15, 22, 31, 40, 47, 58, 66, 79], 47))
```
<!--sortie-->
```text
5
```


> 📐 **Preuve de correction et de terminaison.**
>
> **Invariant :** *si la cible est dans la liste, elle se trouve à un indice entre $g$ et $d$ inclus.*
> *Initialisation* : $g=0$, $d=n-1$ : toute la liste. *Conservation* : si `triee[m] < cible`, comme la liste est triée, tous les éléments d'indice $\le m$ sont $<$ cible : on peut les éliminer, d'où $g=m+1$. Symétriquement si `triee[m] > cible`. L'invariant reste vrai. *Conclusion* : si la boucle s'arrête parce que $g>d$, la zone est vide, donc la cible est absente (on renvoie $-1$) ; si elle s'arrête sur `triee[m] == cible`, c'est gagné.
>
> **Terminaison et coût :** appelons $s=d-g+1$ la taille de la zone. À chaque tour, la nouvelle zone a au plus $\lfloor s/2\rfloor$ éléments (on a éliminé le milieu et une moitié). Après $k$ tours, la taille est au plus $\lfloor n/2^k\rfloor$, qui devient $0$ dès que $2^k>n$. L'algorithme s'arrête donc en **au plus $\lfloor\log_2 n\rfloor+1$ tours**. $\blacksquare$

Vérifions la borne théorique sur nos 400 montants triés, en cherchant **chacun** des 400 montants et en relevant le pire cas : on observe au plus **9** comparaisons (la borne vaut $\lfloor\log_2 400\rfloor+1=9$), **7,42** en moyenne, et 8 pour une valeur absente comme 1,0.


Le pire cas observé respecte bien la borne (au plus 9 comparaisons pour 400 éléments, et 8 pour une valeur absente comme 1,0, contre 400 pour la recherche linéaire de cette même valeur). Pour **un million** d'éléments : $\lfloor\log_2 10^6\rfloor+1=20$ comparaisons seulement. C'est le pouvoir du logarithme : chaque doublement de la taille ne coûte qu'**une** comparaison de plus.

**Une application : le seuil de livraison gratuite.** Une liste triée et la dichotomie répondent à « quelle part des commandes dépasse $s$ € ? » : le module `bisect` contient la recherche dichotomique toute faite. Avec nos montants, un seuil de **70 €** concerne 29,2 % des commandes, à peu près les 30 % qu'une gérante pourrait viser ; le quantile à 70 % (68,9 €) pointe au même endroit. Nous avons retrouvé par un algorithme de recherche ce que les quantiles du 3.1.3 donnaient directement : un bon moyen de comprendre ce que « quantile » veut dire, *la position dans la liste triée*. Le cahier détaille ce calcul (application 4.4).

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


Le programme tient en une dizaine de lignes (deux boucles imbriquées : l'une parcourt les éléments, l'autre décale les plus grands vers la droite) ; la preuve ci-dessous en dit plus que le code.

> 📐 **Correction.** *Invariant :* avant le tour $i$, les $i$ premiers éléments de `a` sont triés (et ce sont les $i$ premiers éléments d'origine). Au tour $i$, on décale vers la droite tous les éléments plus grands que $x$ puis on place $x$ juste avant eux : les $i+1$ premiers éléments sont triés. À la fin ($i=n$), tout est trié. *Terminaison :* deux boucles bornées. *Coût :* au pire (liste triée à l'envers), le tour $i$ fait $i$ comparaisons, soit $1+2+\dots+(n-1)=n(n-1)/2$ comparaisons au total, de l'ordre de $n^2$. $\blacksquare$

**Le tri fusion** (*merge sort*) applique la stratégie « **diviser pour régner** » : on coupe la liste en deux, on trie chaque moitié (récursivement), puis on **fusionne** les deux moitiés triées. Fusionner est facile : on compare les deux premiers éléments des moitiés, on prend le plus petit, et on recommence, comme deux files de gens que l'on entrelace.

**À la main** sur $[44;\ 12;\ 30;\ 8;\ 25;\ 19]$ : on coupe en $[44,12,30]$ et $[8,25,19]$ ; chacun est trié en $[12,30,44]$ et $[8,19,25]$ ; la fusion donne $8<12$ → 8 ; $12<19$ → 12 ; $19<30$ → 19 ; $25<30$ → 25 ; il reste $30,\,44$ : $[8,12,19,25,30,44]$.

```python
def tri_fusion(liste):
    if len(liste) <= 1:                              # cas de base
        return liste
    g, d = tri_fusion(liste[:len(liste) // 2]), tri_fusion(liste[len(liste) // 2:])
    fusion = []
    while g and d:                                   # on entrelace les deux moitiés triées
        fusion.append(g.pop(0) if g[0] <= d[0] else d.pop(0))
    return fusion + g + d

print(tri_fusion([44, 12, 30, 8, 25, 19]))
```
<!--sortie-->
```text
[8, 12, 19, 25, 30, 44]
```

Pour **mesurer** les coûts, on ajoute un compteur de comparaisons aux deux algorithmes (versions de mesure, non reproduites ici) :


Comparons les deux sur nos 400 montants. Le tri par insertion fait **41 010** comparaisons, le tri fusion **2 972** ; les deux donnent le même résultat que `sorted()`, et les formules $n^2/4=40\,000$ et $n\log_2 n\approx3\,458$ donnent le bon ordre de grandeur.


En moyenne, le tri par insertion fait de l'ordre de $n^2/4$ comparaisons (près de quatorze fois plus que le tri fusion ici), le tri fusion de l'ordre de $n\log_2 n$. Pour 400 éléments, cela fait la différence entre « bien » et « très bien » ; pour 10 millions, entre quelques secondes et plusieurs jours. Le tri intégré de Python, `sorted`, utilise un algorithme hybride très optimisé (*Timsort*) de coût $n\log n$ : **en pratique, on utilise toujours `sorted()` ou `.sort()`**, mais comprendre ce qu'il fait permet de raisonner sur son coût.

> 💡 **Un tri est dit stable** s'il laisse dans leur ordre d'origine les éléments « égaux » au regard du critère de tri. C'est ce que garantit `sorted` de Python, et cela permet d'enchaîner des tris successifs : trier d'abord par montant, puis par canal, donne les commandes **rangées par canal et, à l'intérieur de chaque canal, par montant croissant**.

```python
cmds = [("Site", 40.1), ("Boutique", 65.8), ("Site", 19.6), ("Boutique", 17.4), ("Réseaux", 30.1)]
print(sorted(sorted(cmds, key=lambda c: c[1]), key=lambda c: c[0]))   # stable : l'ordre par montant est conservé
```
<!--sortie-->
```text
[('Boutique', 17.4), ('Boutique', 65.8), ('Réseaux', 30.1), ('Site', 19.6), ('Site', 40.1)]
```

### 4.3.7 Une dernière application : les « top k »

La gérante demande : « Quelles sont mes **cinq plus grosses commandes** ? » On pourrait trier les 400 montants puis prendre les cinq derniers (coût de l'ordre de $n\log n$). Mais c'est du gaspillage : on n'a pas besoin que *tout* soit trié. Une structure appelée **tas** (*heap*) maintient efficacement les $k$ plus grands vus jusqu'ici, avec un coût de l'ordre de $n\log k$. Le module `heapq` la fournit :

```python
import heapq

print(heapq.nlargest(5, montants))
print(sorted(montants, reverse=True)[:5])        # même réponse, mais en triant tout
```
<!--sortie-->
```text
[255.7, 243.8, 217.1, 212.4, 208.8]
[255.7, 243.8, 217.1, 212.4, 208.8]
```

Les deux listes sont identiques, la version `heapq` coûtant moins cher quand $k\ll n$ (pensez aux *dix* meilleurs clients sur *dix millions*). Ce réflexe, **ne pas faire plus de travail que nécessaire**, est l'une des habitudes les plus rentables de la programmation scientifique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.3 (file d'attente à l'atelier) et 4.4 (seuil de livraison gratuite) ; exercices 4.5 à 4.8 (pile et notation polonaise inversée, file à deux emballeuses, dichotomie à variante, tri stable).

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


`info()` est le meilleur premier réflexe : nombre de lignes, nom et type de chaque colonne, nombre de valeurs **non nulles** (ici, 400 partout : aucune valeur manquante) et mémoire utilisée.

Le fichier ne contient pas de **date**, or la plupart des vraies données de vente en ont une. Pour illustrer le travail sur les dates (4.4.12) et sur plusieurs tables (4.4.10), nous allons **ajouter deux colonnes simulées** : la date de chaque commande (réparties sur 20 semaines à partir du lundi 5 janvier 2026) et un numéro de client (120 clients possibles). La simulation est reproductible grâce à la graine (le code est donné dans la préparation du cahier, chapitre 4) ; la colonne `date` a le type `datetime64`, et `id_commande` numérote les commandes par ordre chronologique :


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


Remarquez la nuance : avec `cut`, les classes sont **définies par vous** et leurs effectifs sont inégaux ; avec `qcut`, ce sont les effectifs qui sont **égaux** (400 / 4 = 100) et les bornes qui s'adaptent aux données.

**Remplacer des valeurs selon un dictionnaire** se fait avec `map` : `df["satisfaction"].map({1: "très mécontent", 2: "mécontent", 3: "neutre", 4: "content", 5: "très content"})` remplace chaque note par son libellé (195 commandes sont « content » et 104 « très content »).

**Standardiser** (centrer-réduire), comme annoncé à la fin de 4.4.3, se fait sur une colonne entière :


Par construction, $z$ a une moyenne nulle et un écart-type de 1. Sept commandes dépassent 3 écarts-types. Si les montants suivaient une loi normale, on n'en attendrait qu'**une seule** sur 400 environ (la probabilité d'être à plus de 3 écarts-types est de 0,27 %, d'après les repères du 2.2). En trouver sept confirme ce que nous avions vu au 3.1.5 : la distribution des montants a une **queue lourde à droite**.

> 💡 **`apply` : à garder en dernier recours.** Si une transformation n'existe pas en version vectorisée, `df["col"].apply(ma_fonction)` appelle votre fonction **ligne par ligne** : pratique, mais lent (une boucle Python déguisée). Réflexe : chercher d'abord une opération vectorisée (`.str`, `np.where`, `cut`, `map`, opérateurs arithmétiques…). Sur nos 400 lignes la différence est invisible ; en répétant les montants 500 fois (200 000 lignes), `apply` donne le même résultat que la version vectorisée `np.where(gros > 50, gros * 1.19, gros)` mais s'avère **plus lent**.


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


> ✅ **À retenir (`groupby`).** `df.groupby(clé)[colonne].fonction()` : *découper, appliquer, combiner*. `agg` pour plusieurs résumés, `size` pour compter les lignes, `transform` pour ré-aligner un résultat de groupe sur chaque ligne, `pivot_table` et `crosstab` pour des tableaux croisés.

### 4.4.10 Combiner plusieurs tables : `merge` et `concat`

Dans la vraie vie, l'information est **répartie sur plusieurs tables** : la liste des commandes d'un côté, celle des clients de l'autre (nous verrons au chapitre 5 pourquoi, et comment SQL fait la même chose avec `JOIN`). Le travail s'appelle une **jointure** : on associe les lignes qui partagent la même **clé**.

Créons la table des clients : 125 clients, chacun avec une ville. (Les clients 121 à 125 n'ont, par construction, jamais commandé ; comme les commandes ont été attribuées au hasard à des clients de 1 à 120, quelques autres clients n'auront rien commandé non plus. Cela nous servira.)


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


### 4.4.11 Valeurs manquantes

Dans les données réelles, il manque toujours quelque chose : un client n'a pas laissé de note, un capteur est tombé en panne, une case n'a pas été remplie. pandas représente ces trous par **`NaN`** (*not a number*) pour les nombres, et par `NaT` pour les dates. Créons (code non reproduit) une copie de nos données où 30 notes de satisfaction, tirées au hasard, sont perdues : 7 chez Boutique, 10 chez Réseaux, 13 chez Site.


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


> 🧪 **Vérifions sur un exemple.** Le 5 janvier 2026 est un lundi : la semaine du 5 au 11 janvier est donc repérée par le **5 janvier**. Une commande du jeudi 8 janvier doit avoir pour semaine le 5 janvier ; une commande du lundi 12 janvier, le 12. Le programme le confirme : le lundi 5, le jeudi 8 et le dimanche 11 tombent tous dans la semaine du 5 ; le lundi 12 ouvre celle du 12.


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


## 4.5 Premières visualisations

> 💡 **Intuition.** Un tableau de 400 lignes, personne ne le « lit » vraiment ; un graphique bien choisi, on le comprend en trois secondes. Au 3.1 nous avons vu avec le quartet d'Anscombe que des données très différentes peuvent avoir **les mêmes statistiques** : seul le dessin révèle la différence. Visualiser n'est donc pas de la décoration, c'est un **outil de réflexion** (on dessine pour *comprendre*) et un **outil de communication** (on dessine pour *convaincre* sans tromper).
>
> Cette section a trois objectifs : savoir **quel graphique choisir** selon la question (4.5.1), savoir **le tracer** avec les trois bibliothèques les plus utilisées (matplotlib et pandas, seaborn, puis ggplot2 en R : 4.5.2 à 4.5.5), et savoir **éviter les graphiques trompeurs** (4.5.6).

> 🧭 **Pour la suite du livre.** Nous ne ferons ici que les graphiques fondamentaux. Les graphiques interactifs, les cartes ou les tableaux de bord complets sont abordés dans la série Data Analyst.

Les figures de cette section utilisent les données de 4.4 (mêmes graines, mêmes résultats) et la palette du livre : traits fins, grille discrète, pas de cadre inutile. Seuls les extraits utiles sont reproduits ; le code complet de chaque figure se trouve dans le fichier source de la section, exécuté à chaque construction du livre.


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
ax.set(title="Chiffre d'affaires hebdomadaire de la boutique",
       xlabel="semaine (lundi)", ylabel="chiffre d'affaires (€)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))   # dates au format jour/mois
fig.savefig("figures/ch04-premier-graphique.png", dpi=150, bbox_inches="tight")
plt.close(fig)                                         # libère la mémoire
```

![Notre premier graphique : une courbe du chiffre d'affaires par semaine.](figures/ch04-premier-graphique.png)

Tout y est : un **titre**, des **axes nommés avec leur unité**, une ligne avec des **marqueurs** (un point par semaine, pour ne pas laisser croire que l'on connaît les valeurs entre les semaines). La courbe est irrégulière d'une semaine à l'autre, ce qui est normal : chaque semaine ne compte qu'entre 14 et 27 commandes, donc quelques gros paniers suffisent à faire bondir le total. Pour voir la **tendance**, on lisse avec une moyenne mobile, que nous ajouterons en 4.5.3.

> 💡 **Le patron de tous les graphiques matplotlib.** (1) `fig, ax = plt.subplots(...)` ; (2) `ax.plot / ax.bar / ax.hist / ax.scatter(...)` ; (3) `ax.set_title / set_xlabel / set_ylabel` ; (4) `fig.savefig(...)`. Pour *plusieurs* panneaux : `fig, axes = plt.subplots(2, 2)` renvoie un tableau d'Axes que l'on indexe `axes[0, 0]`, `axes[0, 1]`, etc. (c'est un tableau NumPy, voir 4.4.2).

### 4.5.3 Les quatre graphiques essentiels, avec pandas

pandas offre une méthode `.plot` sur ses Series et DataFrames, qui appelle matplotlib en coulisses et **renvoie l'Axes** : on peut donc la combiner avec tout ce qui précède, en lui passant l'argument `ax=`. Voici les quatre graphiques que vous tracerez le plus souvent, dans une seule figure à quatre panneaux. En une ligne chacun, ils s'écrivent ainsi :

1. **histogramme** des montants ;
2. **barres horizontales** du chiffre d'affaires par canal (triées) ;
3. **courbe** du chiffre d'affaires hebdomadaire avec sa moyenne mobile ;
4. **nuage de points** livraison/satisfaction.

Le code complet de la figure ajoute les titres, les étiquettes et les annotations. Pour le quatrième graphique, un détail d'importance. La livraison est un nombre entier de jours et la satisfaction une note entière de 1 à 5 : beaucoup de commandes tombent *exactement au même point*, et un nuage de points normal en cacherait la plupart. On les **décale aléatoirement d'un tout petit peu** (« jitter », en français *jitter* ou *bruitage*) et on rend les points translucides : les zones denses apparaissent plus foncées.

```python noexec
df["montant"].plot.hist(bins=30, color=BLEU)                      # histogramme
ca_canal = df.groupby("canal")["montant"].sum().sort_values()
ca_canal.plot.barh(color=BLEU)                                   # barres horizontales, triées
hebdo["ca"].rolling(4).mean().plot()                             # courbe lissée
df.plot.scatter(x="livraison", y="satisfaction", alpha=0.3)      # nuage de points
```


![Les quatre graphiques essentiels : histogramme, barres triées, courbe avec moyenne mobile, nuage de points « bruité ».](figures/ch04-essentiels.png)

**Comment lire chaque panneau** (c'est aussi comme cela qu'on doit *légender* un graphique dans un rapport) :

- **Histogramme** : la forme est asymétrique à droite, avec une longue queue de grosses commandes ; la médiane (trait orange, 51 €) est nettement sous la moyenne (60 €), tirée vers le haut par les grosses commandes (revoir 3.1.5).
- **Barres** : on lit au premier coup d'œil l'ordre des canaux, et les valeurs sont écrites au bout des barres : plus besoin de deviner sur l'axe. Les barres sont **triées** : un classement doit être lisible.
- **Courbe** : le trait pâle est le chiffre d'affaires de chaque semaine, très irrégulier ; le trait orange, plus lisse, montre la **tendance**.
- **Nuage de points** : plus le délai augmente, plus les notes basses apparaissent ; la corrélation affichée (−0,53) est négative et d'intensité moyenne : un retard fait *tendanciellement* baisser la note, sans que ce soit une règle absolue (beaucoup de commandes tardives ont quand même 4).

> 🧪 **Pourquoi `.plot` renvoie-t-il l'Axes ?** Parce que ainsi tout est modifiable après coup : titre, limites, annotations. Si vous écrivez `ax = df["montant"].plot.hist()`, vous pouvez ensuite faire `ax.set_title(...)`. pandas propose aussi `.plot.bar()`, `.plot.line()`, `.plot.box()`, `.plot.scatter(x=, y=)`, `.plot.pie()`, `.plot.area()`… Pour l'exploration rapide, c'est imbattable (une ligne par graphique).

### 4.5.4 seaborn : des graphiques statistiques en une ligne

**seaborn** est une couche au-dessus de matplotlib spécialisée dans les graphiques **statistiques**. Son atout : on lui donne le **tableau complet** (`data=df`) et on dit quelle colonne va où (`x=`, `y=`, `hue=` pour la couleur), et seaborn s'occupe des regroupements, des légendes et des couleurs.

Deux exemples. D'abord la distribution des montants **selon le canal**, en histogramme et en boîte à moustaches (on précise juste `hue=` pour la couleur) :


```python
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
sns.histplot(data=df, x="montant", hue="canal", hue_order=ordre, palette=COULEURS, element="step", alpha=0.3, ax=axes[0])
sns.boxplot(data=df, x="canal", y="montant", order=ordre, hue="canal", palette=COULEURS, ax=axes[1])
axes[0].set(title="Histogrammes superposés selon le canal", xlabel="montant (€)", ylabel="nombre de commandes")
axes[1].set(title="Boîtes à moustaches selon le canal", xlabel="", ylabel="montant (€)")
fig.savefig("figures/ch04-seaborn-distributions.png", dpi=150, bbox_inches="tight")
print(df.groupby("canal")["montant"].median().reindex(ordre).round(1).to_string())
```
<!--sortie-->
```text
canal
Réseaux     41.5
Site        49.5
Boutique    64.8
```

![Avec seaborn, une ligne suffit pour séparer les données par canal : histogrammes superposés et boîtes à moustaches.](figures/ch04-seaborn-distributions.png)

Les médianes imprimées confirment la lecture : 64,8 € pour la boutique, 49,5 € pour le site, 41,5 € pour Réseaux. (Cette différence est-elle réelle ou due au hasard ? C'est la question d'un test statistique, 3.4.)

Deuxième exemple : une **carte de chaleur** pour le croisement de deux variables qualitatives, le canal et la note de satisfaction. On calcule d'abord le tableau croisé (en proportions par canal), puis on le colore :

```python
tab = pd.crosstab(df["canal"], df["satisfaction"], normalize="index").loc[ordre]
print(tab.round(2))

fig, ax = plt.subplots(figsize=(6.5, 3))
sns.heatmap(tab, annot=True, fmt=".0%", cmap="Blues", cbar=False, linewidths=2, linecolor="white", ax=ax)
fig.savefig("figures/ch04-seaborn-heatmap.png", dpi=150, bbox_inches="tight")
```
<!--sortie-->
```text
satisfaction     1     2     3     4     5
canal                                     
Réseaux       0.00  0.06  0.31  0.49  0.14
Site          0.01  0.05  0.25  0.54  0.16
Boutique      0.00  0.00  0.04  0.42  0.54
```

![Carte de chaleur : chaque ligne (canal) somme à 100 %. Plus la case est foncée, plus la note est fréquente dans ce canal.](figures/ch04-seaborn-heatmap.png)

Chaque ligne du tableau somme à 1 (donc 100 %) : on lit « *parmi* les commandes de la boutique, 54 % ont donné la note 5 » (contre 14 % pour Réseaux et 16 % pour le Site). La case la plus foncée de la ligne Boutique est à droite (la note 5), celles de Réseaux et du Site sont sur la note 4, avec une part importante de 3 : la boutique, où la livraison est immédiate, a les clients les plus satisfaits.

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
commandes$canal <- factor(commandes$canal, levels = c("Réseaux", "Site", "Boutique"))

p <- ggplot(commandes, aes(x = montant, fill = canal)) +
  geom_histogram(bins = 30, colour = "white") +             # une géométrie : l'histogramme
  facet_wrap(~ canal, ncol = 1) +                           # un panneau par canal
  scale_fill_manual(values = c(Réseaux = "#2a78d6", Site = "#eb6834", Boutique = "#1baf7a")) +
  labs(title = "Distribution des montants selon le canal", x = "montant (€)", y = "nombre de commandes") +
  theme_minimal(base_size = 11) + theme(legend.position = "none")
ggsave("figures/ch04-ggplot-montants.png", plot = p, width = 7, height = 5, dpi = 150)
```


![Le même type de graphique avec ggplot2 : un panneau par canal (facettes), même échelle horizontale.](figures/ch04-ggplot-montants.png)

On retrouve les mêmes médianes qu'en Python (41,5 € pour Réseaux, 49,5 € pour le Site, 64,8 € pour la Boutique) (confirmant que les deux outils lisent bien les mêmes données). Le tableau suivant résume la différence de philosophie :

| | matplotlib / seaborn (Python) | ggplot2 (R) |
|---|---|---|
| Style | **impératif** : on construit pas à pas (figure → axes → éléments) | **déclaratif** : on décrit le résultat par couches |
| Séparer par groupe | `hue=` (seaborn) ou une boucle sur les groupes | `fill=`, `colour=`, ou `facet_wrap()` |
| Personnalisation fine | très grande, mais verbeuse | grande, via `theme()` et `scale_*()` |
| Combiner plusieurs couches | appels successifs sur le même `ax` | `+ geom_...()` |

> 🧪 **Honnêteté d'exécution.** Les graphiques de cette section ont tous été produits par du code exécuté à chaque construction du livre (sauf trois dessins explicatifs, produits par `build/fig_ch04.py` : l'anatomie d'une figure, le broadcasting et l'axe tronqué) ; le bloc R a bien été exécuté (R avec ggplot2). Les versions de bibliothèques peuvent légèrement modifier l'aspect (polices, marges) sans changer l'information.

### 4.5.6 Bien faire, mal faire : les pièges du graphique trompeur

Un graphique peut mentir sans qu'une seule donnée soit fausse. Voici les six pièges les plus répandus. Le premier mérite une démonstration.

**Piège n°1 : l'axe tronqué.** Comparons la satisfaction moyenne du canal Réseaux et du Site. Les deux graphiques ci-dessous montrent **exactement les mêmes deux nombres** : 3,72 pour Réseaux et 3,79 pour le Site, soit un écart réel de 2 %.


![Mêmes données, deux impressions opposées : à gauche l'axe commence à 3,70, à droite à 0.](figures/ch04-axe-tronque.png)

À gauche, avec un axe qui commence à 3,70, la barre du Site paraît **plus de 5 fois plus haute** que celle de Réseaux (exactement 5,2 fois : $(3{,}79-3{,}70)/(3{,}72-3{,}70)$) ; à droite, sur un axe complet, les deux barres sont quasiment identiques, ce qui correspond bien à l'écart réel de 2 %. **Règle : pour un diagramme en barres, l'axe doit commencer à 0**, car c'est la *longueur* de la barre qui porte l'information. (Pour une courbe ou un nuage de points, c'est la position qui compte : on peut zoomer, à condition de le signaler.)

**Les autres pièges, et leurs remèdes :**

| Piège | Pourquoi c'est un problème | Remède |
|---|---|---|
| **Camembert en 3D, ou à beaucoup de parts** | la perspective déforme les aires ; l'œil compare mal les angles | barres triées, en 2D |
| **Double axe vertical** | on peut rendre n'importe quelle corrélation « visible » en choisissant les échelles | deux graphiques superposés, ou un seul axe |
| **Trop de couleurs** | 10 couleurs sans ordre : personne ne retient la légende | 3 à 5 couleurs, avec un sens (une couleur = un canal, partout dans le document) |
| **Points superposés** | 400 observations qui se cachent les unes les autres (voir le jitter, 4.5.3) | transparence, bruitage, ou histogramme 2D |
| **Titre vague** (« Graphique 3 ») | le lecteur doit deviner la conclusion | un titre qui **dit** le message : « La boutique a les clients les plus satisfaits » |
| **Axes sans nom ni unité** | « 60 », mais de quoi ? | toujours nommer et donner l'unité (€, jours, %) |

> ✅ **La liste de contrôle d'un bon graphique.** (1) Un message, un titre qui le dit. (2) Le bon type de graphique pour la question (tableau 4.5.1). (3) Des axes nommés avec leurs unités ; **zéro pour les barres**. (4) Des barres **triées** quand elles représentent un classement. (5) Peu de couleurs, avec un sens constant. (6) Lisible en noir et blanc et pour un daltonien : ne pas reposer sur l'opposition rouge/vert seule. (7) La source des données et la date, si l'on communique à d'autres.

### 4.5.7 Enregistrer, réutiliser : de la figure au rapport

Un graphique n'est utile que s'il sort de votre ordinateur. `fig.savefig(chemin)` choisit le format d'après l'extension, avec trois réglages à connaître :

| Format | Quand l'utiliser |
|---|---|
| **PNG** (`.png`) | pages web, diapositives, e-mails : image « pixels », léger |
| **SVG / PDF** (`.svg`, `.pdf`) | impression, articles, LaTeX : image **vectorielle**, nette à toute taille |
| `dpi=` | résolution en pixels par pouce : **150** pour l'écran, **300** pour l'impression |
| `bbox_inches="tight"` | rogne les marges blanches inutiles |

En pratique, `fig.savefig("exemple.pdf", dpi=150, bbox_inches="tight")` suffit : l'extension choisit le format (nous avons vérifié que PNG, SVG et PDF s'enregistrent bien).


Mettons tout en commun dans une **fonction** qui produit, en une seule figure, le tableau de bord que la gérante joint à son rapport du lundi : la courbe lissée du chiffre d'affaires, la part de chaque canal, la répartition des notes. Chaque panneau a un **titre qui énonce sa conclusion, calculée à partir des données** (et non écrite à la main) : si les chiffres changent, le titre reste vrai. Tel que la gérante le lit, il dit que la tendance du chiffre d'affaires est à la hausse (de 1 080 à 1 434 € par semaine en moyenne mobile), que le Site et la Boutique pèsent chacun plus d'un tiers des ventes, et que trois clients sur quatre sont satisfaits (4 ou 5). Voilà le chemin complet : des **données brutes** (fichier CSV) aux **tableaux** (pandas, 4.4) puis aux **figures** prêtes à insérer dans un rapport, le tout dans un script que l'on peut relancer chaque semaine. C'est l'esprit de la **recherche reproductible** que nous retrouverons au chapitre 6. La fonction complète est construite pas à pas dans l'application 4.6 du cahier.

![Le tableau de bord produit par la fonction : trois panneaux, chacun avec un titre qui énonce sa conclusion.](figures/ch04-tableau-de-bord.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6 (le tableau de bord) ; exercice 4.12 (un graphique honnête).


## 4.6 ➕ Pour aller plus loin : programmation orientée objet, code propre et tests

> 🧭 **Section optionnelle.** Vous pouvez faire toute une carrière d'analyste avec des fonctions, des listes et des tableaux pandas. Mais dès que votre code dépasse quelques dizaines de lignes, ou qu'un collègue (ou vous-même, dans six mois) doit le relire, trois outils changent la vie : **regrouper** les données et les opérations qui vont ensemble (les *objets*), **écrire clairement** (le *code propre*), et **vérifier automatiquement** que le code fait ce qu'on croit (les *tests*). Cette section les présente sur un exemple concret : le panier d'une cliente de la boutique.

Pour les tests, nous écrivons de vrais **fichiers** Python que nous exécutons depuis un terminal, exactement comme vous le feriez sur votre machine : la commande `cat > fichier <<'FIN' … FIN` crée un fichier avec le texte qui suit, et `python -m pytest` lance les tests. (Le chapitre 6.3 détaille le terminal.) Le module complet de la boutique et sa suite de tests sont donnés dans le cahier ; ici, nous n'en montrons que les passages utiles.

### 4.6.1 Pourquoi des objets ? Le problème des dictionnaires

> 💡 **Intuition.** Jusqu'ici, un panier pouvait être une simple liste de prix. Mais un panier, ce n'est pas qu'une liste : c'est aussi *« savoir calculer son total, ajouter un article, refuser une quantité négative »*. Un **objet** est un petit paquet qui contient à la fois des **données** (les *attributs*) et les **opérations** qui vont avec (les *méthodes*). Sa **classe** est le moule qui fabrique ces objets, comme un patron de couture fabrique des robes.

Voyons pourquoi cela sert à quelque chose. Voici un panier représenté « à la main » par un dictionnaire, et une fonction qui calcule le total :

```python
panier = {"savon": (20.0, 2), "plateau": (30.0, 1)}      # nom -> (prix HT, quantité)
total_ht = lambda p: sum(prix * qte for prix, qte in p.values())

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

```python
class Article:
    def __init__(self, nom, prix_ht):      # appelée à la création de l'objet
        self.nom = nom                     # self = l'objet en cours de création
        self.prix_ht = prix_ht

    def prix_ttc(self):                    # une méthode : une fonction de l'objet
        return round(self.prix_ht * 1.19, 2)

savon = Article("savon", 20.0)
print(savon.nom, savon.prix_ht, savon.prix_ttc())
```
<!--sortie-->
```text
savon 20.0 23.8
```

Lisez ligne à ligne :

- `class Article:` définit le moule.
- `__init__` est le **constructeur** : Python l'appelle quand on écrit `Article("savon", 20.0)`. Le premier paramètre, `self`, désigne l'objet qu'on est en train de fabriquer ; on y accroche les attributs (`self.nom`, `self.prix_ht`).
- `prix_ttc` est une **méthode** : on l'appelle avec un point, `savon.prix_ttc()`, et `self` est passé automatiquement.
- Un défaut de cette version : si l'on écrit `print(savon)`, l'affichage `<__main__.Article object at 0x…>` ne dit rien d'utile (et l'adresse mémoire change à chaque exécution).

Écrire `__init__` et un affichage lisible pour chaque classe devient vite répétitif. C'est le rôle des **dataclasses** (`@dataclass`) : Python écrit pour vous le constructeur, un affichage lisible et la comparaison `==`.

```python
from dataclasses import dataclass

@dataclass
class Article:
    nom: str
    prix_ht: float

a, b = Article("savon", 20.0), Article("savon", 20.0)
print(a)                 # affichage lisible, fabriqué automatiquement
print("a == b ?", a == b)
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
- un panier de 2 savons à 20 € et 1 plateau à 30 € vaut $2\times 20+30=70$ € hors taxe, soit $70\times1{,}19=83{,}30$ € TTC ;
- avec une remise de 10 % sur le hors-taxe : $70\times0{,}90=63$ € HT, soit $63\times1{,}19=74{,}97$ € TTC ;
- sur le site, la livraison coûte 7 €, **offerte** si le panier TTC atteint 100 € ; en boutique, le retrait est gratuit.

### 4.6.4 Code propre : lisible avant tout

> 💡 **Intuition.** Le code est lu bien plus souvent qu'il n'est écrit. L'objectif n'est pas de « faire marcher » un programme, mais de le rendre **compréhensible** par quelqu'un qui n'était pas là quand vous l'avez écrit (y compris vous, dans six mois). Cinq habitudes suffisent pour 90 % du résultat :

1. **Des noms qui parlent.** `total_ttc` plutôt que `t`, `remise` plutôt que `r`. Un nom long et clair vaut mieux qu'un commentaire.
2. **Des fonctions courtes qui font une seule chose.** Si vous devez écrire « et » pour décrire ce que fait une fonction, coupez-la en deux.
3. **Pas de nombres magiques.** Écrivez `TVA = 0.19` une fois en haut du fichier, pas `1.19` à quinze endroits (le jour où le taux change, vous n'en oublierez aucun).
4. **Une docstring** : une phrase entre triples guillemets sous la ligne `def` ou `class`, qui dit *ce que* fait la fonction. Elle s'affiche avec `help(...)`.
5. **Des annotations de type** (`nom: str`, `-> float`) : elles documentent ce que la fonction attend et renvoie.

> ⚠️ **Les annotations de type ne sont pas vérifiées à l'exécution.** Python les lit, mais ne les impose pas. Ce sont des indications pour les humains et pour les outils de vérification (comme `mypy`). Regardez :

```python
def double(x: int) -> int:
    return x * 2

print(double(21), double("ab"))      # une chaîne n'est pas un entier… et pourtant, aucune erreur
```
<!--sortie-->
```text
42 abab
```

> ⚠️ **Piège classique : l'argument par défaut modifiable.** Une valeur par défaut comme `[]` est créée **une seule fois**, à la définition de la fonction, puis partagée entre tous les appels. C'est une des erreurs les plus fréquentes en Python :

```python
def ajouter_mauvais(article, panier=[]):          # MAUVAIS : la liste est partagée entre les appels
    panier.append(article)
    return panier

print(ajouter_mauvais("savon"), ajouter_mauvais("plateau"))
```
<!--sortie-->
```text
['savon', 'plateau'] ['savon', 'plateau']
```

Avec la version fautive, le deuxième panier *contient aussi le savon* du premier : deux clientes se retrouvent avec le même panier. La version correcte écrit `panier=None` dans la signature, puis `if panier is None: panier = []` dans le corps de la fonction (on obtient alors `['savon']` puis `['plateau']`). Vous retrouverez ce motif dans les dataclasses sous la forme `field(default_factory=list)`.

### 4.6.5 Tester son code : le filet de sécurité

> 💡 **Intuition.** Un **test unitaire** est un petit programme qui appelle une fonction avec des entrées dont **vous connaissez la bonne réponse**, et vérifie qu'elle renvoie bien cette réponse. Vous les écrivez une fois ; ils se rejouent en une seconde après chaque modification. Si un test devient rouge, vous savez *quoi* vous venez de casser, *tout de suite*, et pas un mois plus tard en lisant un rapport faux.

Le schéma universel d'un test s'appelle **Arrange – Act – Assert** : on **prépare** les données (*arrange*), on **exécute** la fonction (*act*), on **vérifie** le résultat (*assert*). Nous utilisons **pytest**, l'outil standard : il suffit d'écrire des fonctions dont le nom commence par `test_` et d'y mettre des `assert`.

**Étape 1 : une fonction de remise, écrite trop vite.** Un test attend 60 € pour 80 € avec 25 % de remise :

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    return prix - taux
FIN
cat > test_remises.py <<'FIN'
from remises import prix_apres_remise

def test_remise_de_25_pour_cent():
    assert prix_apres_remise(80.0, 0.25) == 60.0      # 80 * (1 - 0,25) = 60
FIN
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | grep -E "^E |passed|failed" | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
E   assert 79.75 == 60.0
E    +  where 79.75 = prix_apres_remise(80.0, 0.25)
1 failed
```

Le test a fait son travail : la fonction soustrait le *taux* (0,25 € !) au lieu d'appliquer le pourcentage. Le message affiche la ligne en cause, la valeur obtenue (79,75) et la valeur attendue (60). Notez qu'un second test, `prix_apres_remise(80.0, 0.0) == 80.0`, passerait : un code faux peut réussir un cas particulier, ce qui montre pourquoi **un seul test ne suffit pas**.

**Étape 2 : on corrige, on relance.**

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    if not 0 <= taux <= 1:
        raise ValueError(f"le taux doit être entre 0 et 1, reçu {taux}")
    return prix * (1 - taux)
FIN
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | grep -E "passed|failed" | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
1 passed
```

Test vert. Remarquez que nous avons aussi ajouté une **validation** : un taux de 25 (au lieu de 0,25) lèverait une erreur claire plutôt que de produire un prix négatif.

> 💡 **Un réflexe d'expert : écrire le test *avant* le correctif.** Quand vous découvrez un bogue, écrivez d'abord un test qui l'attrape (il est rouge), puis corrigez le code (il devient vert). Ce bogue ne reviendra jamais sans que quelqu'un le remarque. Cette discipline s'appelle le **développement piloté par les tests** (*TDD*).

**Étape 3 : le module de la boutique.** Il contient quatre classes (un article, un panier, une commande en boutique, une commande sur le site), avec docstrings, annotations de types, validation et une constante pour la TVA (une soixantaine de lignes, données dans le cahier). Voici les passages qui illustrent la section :


```python noexec
@dataclass(frozen=True)             # frozen : on ne peut plus modifier un article créé
class Article:
    nom: str
    prix_ht: float

    def __post_init__(self):
        if self.prix_ht < 0:
            raise ValueError(f"prix négatif pour {self.nom!r}")

class Commande:                     # une commande en boutique : retrait gratuit
    def __init__(self, panier):
        self.panier = panier
    def frais_livraison(self):
        return 0.0
    def total_a_payer(self):
        return round(self.panier.total_ttc() + self.frais_livraison(), 2)

class CommandeSite(Commande):       # héritage : on ne redéfinit que ce qui change
    def frais_livraison(self):
        return 0.0 if self.panier.total_ttc() >= 100.0 else 7.0
```

Quelques points de lecture :

- `frozen=True` rend l'article **immuable** : impossible d'écrire `article.prix_ht = -5` après coup. Moins de bogues possibles.
- `__post_init__` est appelé juste après le constructeur généré par la dataclass : c'est l'endroit idéal pour **valider** les données.
- `__len__` est une **méthode spéciale** (on les reconnaît à leurs doubles tirets bas) : elle fait fonctionner `len(panier)`.
- `CommandeSite(Commande)` est un exemple d'**héritage** : la classe fille reprend tout de la classe mère et ne **redéfinit** que ce qui change, ici `frais_livraison`. La méthode `total_a_payer`, écrite une seule fois dans `Commande`, appelle `self.frais_livraison()` et obtient automatiquement le bon comportement selon le type d'objet : c'est le **polymorphisme**.

> 💡 **Quand utiliser l'héritage ?** Avec parcimonie. Deux classes dont l'une « *est une sorte de* » l'autre (une commande du site *est une* commande) : oui. Pour simplement réutiliser du code, préférez la **composition** (un objet qui *contient* un autre, comme `Commande` contient un `Panier`). Beaucoup de projets de data science n'ont besoin que de fonctions et de dataclasses.

**Étape 4 : les tests du module.** Chaque règle métier vérifiée à la main plus haut devient un test (il y en a dix dans le module complet). Le décorateur `@pytest.fixture` prépare le panier de l'exemple (le *arrange*) ; `pytest.approx` compare des nombres décimaux avec une petite tolérance (rappelez-vous, section 1.5 : `0.1 + 0.2 != 0.3` en binaire !) ; `@pytest.mark.parametrize` rejoue le même test avec plusieurs valeurs. Voici deux tests, puis la suite complète :


```python noexec
@pytest.fixture
def panier():                                   # Arrange : le panier de l'exemple
    p = Panier()
    p.ajouter(Article("savon", 20.0), 2)
    p.ajouter(Article("plateau", 30.0))
    return p

def test_total_ttc(panier):                     # Act + Assert
    assert panier.total_ttc() == pytest.approx(83.30)

@pytest.mark.parametrize("quantite", [0, -2])   # le même test, rejoué avec plusieurs valeurs
def test_quantite_invalide(quantite):
    with pytest.raises(ValueError):
        Panier().ajouter(Article("savon", 20.0), quantite)
```

```bash
python -m pytest -q --color=no -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
11 passed
```

Les onze tests (dix pour le module, un pour la remise) passent : chaque test vert est une promesse tenue. Ils vérifient les calculs faits à la main : $83{,}30$, $74{,}97$, $83{,}30+7=90{,}30$, et le panier de $90$ € HT qui vaut $90\times1{,}19=107{,}10$ € TTC, donc livraison offerte.

> 🧪 **Que se passe-t-il si on casse le code ?** Modifions le seuil de livraison offerte à 1 000 € dans le module (une faute de frappe plausible : un zéro en trop), et relançons les tests : un seul passe au rouge (« 1 failed, 10 passed »), celui qui protège précisément cette règle ; en remettant la bonne valeur, on retrouve « 11 passed ».


Voilà la valeur d'une suite de tests : une modification « innocente » est détectée **immédiatement**, avec le nom du test et la règle violée.

### 4.6.6 Tester une fonction d'analyse

Les tests ne servent pas qu'aux classes : une fonction d'analyse de données mérite les mêmes soins, surtout si elle sera réutilisée dans un rapport. Prenons le panier moyen par canal (le même calcul que celui du chapitre 3, `commandes.groupby("canal")["montant"].mean()`). On le teste sur un **petit tableau dont on connaît la réponse à la main** : deux commandes du Site à 10 et 30 € (moyenne $(10+30)/2=20$) et une commande de la Boutique à 50 € (moyenne 50). Si la fonction renvoie autre chose, un test devient rouge. Elle est alors **nommée, documentée et protégée**. Dans un vrai projet, on range le code dans un dossier `src/` et les tests dans un dossier `tests/` ; la commande `pytest` trouve alors tout seule les fichiers `test_*.py` (chapitre 6.1 pour les ranger sous Git). L'application 4.7 du cahier fait cet exercice complet.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (module de la boutique et ses tests) ; exercice 4.13 (un test unitaire qui vise la borne).

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

La gérante demande : *« Pour chaque canal de vente, combien de commandes, quel montant moyen, et quel écart-type ? »* C'est le calcul du 3.1, appliqué au fichier `donnees/commandes.csv` : lire, regrouper, résumer. Cinq lignes dans chaque langage.

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
Boutique  114     74.8        40.6
Réseaux   138     49.0        31.1
Site      148     59.5        38.3
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
  canal        n moyenne ecart_type
  <chr>    <int>   <dbl>      <dbl>
1 Boutique   114    74.8       40.6
2 Réseaux    138    49         31.1
3 Site       148    59.5       38.3
```

Les deux langages donnent exactement les mêmes nombres : 114 commandes en boutique pour un montant moyen d'environ 75 €, comme au 3.1. (Le tri alphabétique des canaux est le même ; seule la présentation du tableau diffère.)

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

> 🧭 **Section optionnelle.** Un code correct n'est pas toujours un code **utilisable** : le même résultat peut prendre une seconde ou trois jours selon la manière dont on s'y prend. La **complexité algorithmique** donne un langage pour comparer des méthodes *avant* de les écrire, et la mesure du temps (le *profilage*) dit où agir *après*. Cette section tient la promesse faite à la section 1.6, où nous avions vu que la boutique ne peut pas « énumérer tous les paniers possibles ».

### 4.8.1 L'idée : compter les opérations, pas les secondes

> 💡 **Intuition.** La gérante cherche un client dans son carnet d'adresses. Si le carnet n'est **pas trié**, elle doit lire les noms un par un : pour 1 000 clients, il lui faut en moyenne 500 lectures, et 1 000 dans le pire cas. Si le carnet est **trié par ordre alphabétique**, elle l'ouvre au milieu, regarde si le nom cherché est avant ou après, et élimine la moitié du carnet à chaque étape : 1 000 clients se règlent en **10 étapes** (car $2^{10}=1\,024$). Avec un million de clients, la première méthode demande un million de lectures, la seconde **20**.

Ce qui compte n'est pas la vitesse de l'ordinateur ou du langage, mais la **manière dont le nombre d'opérations grandit quand la taille $n$ des données grandit**. C'est la **complexité** de l'algorithme. Vérifions-la en comptant effectivement les comparaisons (par un petit programme de mesure, non reproduit ici) : pour $n=1\,000$ clients, la lecture linéaire demande **1 000** comparaisons dans le pire cas, la recherche binaire **10** ; pour $n=1\,000\,000$, **1 000 000** contre **20**.


Ces nombres ne dépendent pas de la machine : c'est ce qui rend la complexité si utile. La première méthode est **linéaire**, la seconde **logarithmique** : multiplier $n$ par 1 000 multiplie le travail de la première par 1 000, mais ajoute seulement une dizaine d'étapes à la seconde.

### 4.8.2 La notation $O(\cdot)$ : une définition rigoureuse

On ne se soucie pas des détails (« 3 opérations par tour de boucle » ou « 5 »). On garde seulement la **forme de la croissance**, d'où une notation qui « oublie » les constantes.

> 📐 **Définition (grand O).** On écrit $f(n)=O(g(n))$ s'il existe une constante $c>0$ et un rang $n_0$ tels que
> $$f(n)\le c\,g(n)\qquad\text{pour tout }n\ge n_0 .$$
> En mots : à partir d'un certain rang, $f$ ne dépasse pas un multiple fixe de $g$.

**Exemple fait à la main.** Un algorithme effectue $f(n)=3n^2+5n+2$ opérations. Montrons que $f(n)=O(n^2)$ avec $c=4$. Il faut $3n^2+5n+2\le 4n^2$, c'est-à-dire $n^2-5n-2\ge0$. Pour $n=5$ : $25-25-2=-2<0$ (l'inégalité est fausse). Pour $n=6$ : $36-30-2=4\ge0$ (vraie), et le trinôme est croissant ensuite : $n_0=6$ convient. Le calcul numérique le confirme : l'inégalité $f(n)\le4n^2$ est fausse pour $n=1,\dots,5$ et vraie dès $n=6$.


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

**Test 1 : la liste contre l'ensemble.** Chercher si un identifiant est présent parmi $n$ clients. Dans une liste (`x in liste`), Python lit les éléments un par un : $O(n)$. Dans un **ensemble** (`set`), qui range ses éléments à la manière d'un dictionnaire, la recherche est en $O(1)$ en moyenne. Nous cherchons un élément **absent** (pire cas pour la liste) et nous multiplions $n$ par 100 (code de mesure non reproduit) :


Le test confirme que la liste a un temps proportionnel à $n$ (multiplier $n$ par 100 multiplie le temps par un nombre de l'ordre de 100), alors que l'ensemble est **insensible** à la taille (rapport proche de 1). Le gain n'est pas de 20 % : à $n=100\,000$, la figure (b) ci-dessous montre un écart de **plusieurs ordres de grandeur** entre les deux courbes.

> 💡 **Un réflexe à retenir.** Vous avez une liste de 100 000 clients à vérifier contre une liste de 50 000 clients « actifs ». Écrire `[c for c in clients if c in actifs]` avec `actifs` en **liste** fait jusqu'à $100\,000\times50\,000=5\cdot10^9$ comparaisons. Une seule ligne, `actifs = set(actifs)`, ramène cela à $\approx100\,000$ opérations. C'est probablement l'optimisation la plus rentable de toute la data science pratique.

**Test 2 : le test du « doublement ».** Une technique simple pour deviner la complexité d'un code : doubler $n$ et regarder de combien le temps est multiplié. Environ ×2 : linéaire. Environ ×4 : quadratique. Environ ×8 : cubique. Comparons deux manières de détecter des commandes en double, la première par paires, la seconde en un seul passage :

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

print(doublons_naif([4, 8, 4, 1, 8]), doublons_ensemble([4, 8, 4, 1, 8]))
```
<!--sortie-->
```text
[4, 8] [4, 8]
```


La version par paires est **quadratique** : doubler $n$ multiplie le temps par un nombre proche de 4. La version à un passage est **linéaire** : doubler $n$ multiplie le temps par un nombre proche de 2 (un peu plus, parfois, à cause de la mémoire cache de l'ordinateur). Les mesures sont bruitées : relancez le bloc plusieurs fois et vous verrez ces rapports fluctuer légèrement, mais pas changer d'ordre de grandeur.

### 4.8.4 Boucles Python contre calcul vectorisé

Au 4.4, nous avons dit que NumPy et pandas sont « rapides ». Voici de quoi : calculer la somme des carrés de 1 million de montants. Les deux versions sont en $O(n)$, mais la **constante** n'est pas du tout la même : une boucle Python interprète les tours un par un, alors que NumPy exécute une boucle en code compilé.

```python
import numpy as np

rng = np.random.default_rng(7)
montants = np.exp(rng.normal(3.9, 0.55, size=1_000_000))       # 1 million de montants simulés
liste = montants.tolist()

total = 0.0
for v in liste:                        # une boucle Python
    total += v * v
print(np.isclose(total, np.sum(montants ** 2)))     # la même somme, vectorisée : np.sum(montants ** 2)
```
<!--sortie-->
```text
True
```


Même complexité théorique, mais un facteur de **dizaines** (voire de centaines selon la machine) en faveur de NumPy : la complexité ne dit donc pas tout, les constantes comptent aussi. La règle pratique du data scientist : **dès que vous écrivez une boucle `for` sur les lignes d'un tableau, demandez-vous s'il existe une opération vectorisée**. Même chose avec pandas : une opération sur une colonne entière est presque toujours préférable à `apply` ligne par ligne.


Même verdict avec pandas (`df["montant_ht"].apply(lambda x: x * 1.19)` contre `df["montant_ht"] * 1.19`, sur 200 000 lignes) : `apply` appelle une fonction Python **pour chaque ligne**, alors que la multiplication de la colonne entière se fait d'un coup, dans du code compilé. Le facteur dépend de la machine (de l'ordre de plusieurs dizaines à plusieurs centaines de fois), mais le message est toujours le même.

### 4.8.5 La mémoïsation : ne jamais calculer deux fois la même chose

> 💡 **Intuition.** Quand on vous demande « combien font 17 × 23 ? », vous calculez. Si on vous le redemande dix fois, vous n'allez pas refaire le calcul : vous vous souvenez de la réponse. La **mémoïsation** (*memoization*) fait de même : on **mémorise** le résultat d'une fonction pour chaque argument déjà rencontré.

L'exemple classique est la suite de Fibonacci : $F(0)=0$, $F(1)=1$, $F(n)=F(n-1)+F(n-2)$. La définition récursive est très élégante, mais elle recalcule les mêmes valeurs un nombre énorme de fois : pour calculer $F(5)$, on calcule $F(3)$ deux fois, $F(2)$ trois fois, etc. Comptons les appels de la version naïve (programme de mesure non reproduit ; c'est celui de 4.3.4) : 15 appels pour $F(5)$, 1 973 pour $F(15)$, **242 785** pour $F(25)$. Avec la mémoire, il suffit de 6, 16 et 26 calculs : une seule ligne ajoutée, `@lru_cache(maxsize=None)` au-dessus de la définition de la fonction (voir 4.3.4).


Pour $F(25)$ : 242 785 appels contre 26 (un par valeur de 0 à 25). La version naïve est **exponentielle** (le nombre d'appels croît comme $1{,}6^n$), la version mémoïsée est **linéaire**. On a transformé un calcul impossible en un calcul instantané, en échange d'un peu de **mémoire** : c'est le compromis classique entre le temps et l'espace.

Ce compromis existe partout : un million de montants occupent environ **32 Mo** dans une liste Python, mais **8 Mo** seulement dans un tableau NumPy, qui range ses nombres côte à côte, sans « emballage » : environ quatre fois moins de mémoire, ce qui est l'une des raisons de sa vitesse.


### 4.8.6 Profiler : mesurer avant d'optimiser

> 💡 **Règle d'or.** *« L'optimisation prématurée est la racine de tous les maux. »* (Donald Knuth). Ne devinez pas où le programme est lent : **mesurez**. Dans un programme de 50 lignes, 95 % du temps se passe typiquement dans 1 ou 2 lignes. Les optimiser donne tout ; optimiser le reste ne change rien.

L'outil s'appelle un **profileur** : `cProfile` enregistre, pour chaque fonction, le nombre d'appels et le temps passé. Voici un petit rapport qui nettoie des identifiants de commandes, cherche les doublons et calcule une moyenne. Il est écrit sans malice, mais l'une de ses étapes est un piège caché. Laquelle ?

```python
def nettoyer(ids):
    return [int(x) for x in ids]

def moyenne(ids):
    return sum(ids) / len(ids)

def rapport(ids):
    propres = nettoyer(ids)
    return len(doublons_naif(propres)), moyenne(propres)
```

On le profile avec `cProfile` (la sortie, longue, n'est pas reproduite ; nous en résumons l'essentiel) :

```python noexec
import cProfile

cProfile.run("rapport(donnees)", sort="cumtime")       # affiche, par fonction, le nombre d'appels et le temps passé
```


Le rapport du profileur désigne immédiatement le coupable : `doublons_naif` (notre détecteur par paires, quadratique) occupe près de 100 % du temps, loin devant `nettoyer`, `moyenne` et `rapport` (0 %). Inutile d'accélérer `nettoyer` : on remplace plutôt `doublons_naif` par `doublons_ensemble`, qui est linéaire (4.8.3). C'est la démarche en trois temps de tout travail d'optimisation : **mesurer**, **trouver le goulot d'étranglement**, **changer d'algorithme ou de structure de données**, puis **mesurer encore** pour confirmer le gain.

> ⚠️ **Ordre des priorités.** (1) D'abord un code **correct** et lisible (4.6, avec ses tests). (2) Ensuite, si c'est trop lent, **mesurer**. (3) Optimiser d'abord l'**algorithme** (complexité), ensuite la **vectorisation**, et seulement en dernier recours les micro-détails. Un test qui reste vert après l'optimisation prouve que vous n'avez rien cassé.

### 4.8.7 Un exemple : les paires de produits achetés ensemble

Retour à la boutique. La gérante voudrait savoir quels produits sont **souvent achetés ensemble** pour proposer des offres groupées. Son catalogue contient 40 produits. Première idée : examiner **tous les paniers possibles** de 10 produits... Souvenez-vous du 1.6 : il y en a $\binom{40}{10}=847\,660\,528$. Même à un million de paniers examinés par seconde, cela fait plus de 14 minutes *pour une seule taille de panier*, et le nombre de sous-ensembles totaux est $2^{40}\approx 10^{12}$. Mais la gérante n'a pas besoin de tous les paniers **possibles** : seulement des paniers **réellement achetés**. Il suffit de compter, panier par panier, les paires qu'il contient : la complexité dépend alors de la taille des données, pas de la taille de l'univers des possibles. Ici, `paniers` est une liste de 20 000 paniers simulés (de 2 à 5 produits chacun), dont 15 % contiennent le couple de produits 7 et 12.


```python
compteur = Counter()
for panier in paniers:
    for paire in combinations(panier, 2):                    # toutes les paires DU panier
        compteur[paire] += 1
print(compteur.most_common(3))
```
<!--sortie-->
```text
[((7, 12), 3017), ((7, 8), 395), ((5, 12), 392)]
```


En à peine plus de 120 000 opérations (au lieu de plusieurs centaines de millions), le couple $(7,12)$ ressort nettement : c'est l'association que nous avions planifiée dans la simulation, et les autres paires, simplement dues au hasard, ont des effectifs bien plus faibles. La méthode est **linéaire** en nombre de paniers (chaque panier de $k$ produits fournit $\binom k2$ paires, et $k\le 5$ ici). C'est exactement l'idée derrière les algorithmes de recommandation (« règles d'association ») : on compte ce qui s'est vraiment passé, on n'explore pas ce qui aurait pu se passer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8 (règles d'association : support, confiance, lift) ; exercice 4.14 (coût d'un algorithme).

> ✅ **À retenir (complexité et optimisation).**
>
> - La **complexité** mesure comment le nombre d'opérations grandit avec $n$, indépendamment de la machine. $f(n)=O(g(n))$ : à partir d'un rang $n_0$, $f\le c\,g$.
> - De la plus lente à la plus rapide : $O(2^n)$ (impraticable dès $n\approx 50$), $O(n^2)$, $O(n\log n)$, $O(n)$, $O(\log n)$, $O(1)$.
> - **Structure de données = complexité.** Chercher dans une liste est $O(n)$, dans un `set` ou un dictionnaire $O(1)$ ; une liste triée permet la recherche binaire en $O(\log n)$.
> - **Test du doublement** : $n$ double, temps ×2 → linéaire ; ×4 → quadratique.
> - **Vectorisez** : NumPy et pandas battent les boucles Python de plusieurs ordres de grandeur, à complexité égale.
> - **Mémoïsation** (`@lru_cache`) : échanger de la mémoire contre du temps, en ne calculant jamais deux fois la même chose.
> - **Mesurez, ne devinez pas** : profilez (`cProfile`), trouvez le goulot, changez d'algorithme, remesurez. Les durées varient d'une machine à l'autre ; les ordres de grandeur et les rapports, non.


## Bilan du chapitre 4

Vous savez maintenant :

- **programmer en Python** (4.1) : variables et types, collections (liste, tuple, dictionnaire, ensemble), conditions, boucles, fonctions, erreurs et `try / except`, lecture d'un fichier CSV, et un petit programme complet (le ticket de caisse) testé par `assert` ;
- **refaire les mêmes analyses en R** (4.2) : vecteurs, `data.frame`, tests statistiques « de la boîte », `dplyr` ; et savoir que Python et R donnent les mêmes nombres quand on leur pose la même question ;
- **raisonner comme un informaticien** (4.3) : choisir une structure (liste, dictionnaire, ensemble, pile, file), écrire une récursion avec son cas de base, prouver une dichotomie ou un tri par un invariant, et ne pas trier plus que nécessaire ;
- **manipuler des données** (4.4) : tableaux NumPy et broadcasting ; DataFrames pandas, sélection, `groupby`, jointures, valeurs manquantes, dates ;
- **dessiner honnêtement** (4.5) : choisir le bon graphique pour la question, l'anatomie d'un graphique matplotlib, seaborn, ggplot2, et les pièges du graphique trompeur (axe tronqué en tête) ;
- (en option, 4.6) **structurer et tester** : classes et dataclasses, code lisible, tests `pytest` qui visent les bornes ;
- (en option, 4.7) **situer** SAS, MATLAB et Julia par rapport à Python et R ;
- (en option, 4.8) **compter le coût** d'un algorithme (notation $O(\cdot)$), préférer la vectorisation, mémoïser, et mesurer avant d'optimiser.

> ✅ **Trois réflexes à emporter.** (1) *Calculer à la main un petit cas avant de coder* : c'est votre oracle. (2) *Lire le message d'erreur par la dernière ligne.* (3) *Vérifier un résultat par une seconde voie* (Python contre R, deux méthodes, une somme de contrôle).

Le chapitre 5 apprend à **aller chercher** les données là où elles vivent réellement : dans des bases de données relationnelles, avec le langage SQL. Vous y retrouverez `commandes.csv`, des jointures (comme en 4.4.10), des agrégations (comme le `groupby`) et l'idée de l'**index**, cet arbre trié qui permet une recherche dichotomique.

> 📒 **Pour s'entraîner.** Le **cahier** du volume I (chapitre 4) contient huit applications guidées (le ticket de caisse complet, le rapport hebdomadaire, le tableau de bord, le module testé de la boutique, les règles d'association…) et quatorze exercices corrigés.
