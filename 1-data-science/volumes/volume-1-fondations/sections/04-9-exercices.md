## 4.9 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 2 et 3 sont ceux que la section 4.1.10 vous avait promis. Les exercices 13 et 14 reprennent les sections optionnelles 4.6 et 4.8.

### Énoncés

**Exercice 1 ⭐ (4.1 : dictionnaires et boucles).** Cinq commandes `(canal, montant)` : `("Site", 40)`, `("Réseaux", 25)`, `("Site", 60)`, `("Boutique", 100)`, `("Réseaux", 35)`. Calculez à la main le chiffre d'affaires de chaque canal et sa part du total. Écrivez ensuite le programme avec un dictionnaire et une boucle, sans bibliothèque.

**Exercice 2 ⭐⭐ (4.1.10 : un produit absent du catalogue).** Reprenez le programme de la caisse. (a) Que se passe-t-il pour le panier `[("bol", 2), ("vase", 1)]` ? (b) Faites afficher un message **aimable** (nom du produit fautif et liste des produits disponibles) au lieu d'un plantage. (c) Variante : ignorez les produits inconnus, calculez le total TTC du reste du panier et listez ce qui a été ignoré. Quel total TTC attendez-vous à la main ?

**Exercice 3 ⭐⭐ (4.1.10 : un code promo).** la gérante crée le code `JASMIN15` (15 % de remise sur le hors-taxe) et le code `RENTREE5` (5 %). Règle : la remise promo **ne se cumule pas** avec la remise fidélité (10 % au-delà de 100 €) ; on applique la **meilleure des deux**. Un code inconnu est ignoré avec un message. Calculez à la main le TTC du panier « 2 bols, 1 plateau, 3 bougies » avec `JASMIN15`, puis celui de « 2 tasses » avec le même code, et vérifiez par le code.

**Exercice 4 ⭐ (4.2 : R).** Quelle part des commandes est « satisfaite » (note $\geq 4$) dans chaque canal ? (a) Sur les notes `5, 4, 2, 3, 5` de l'exemple, calculez la part à la main. (b) Répondez sur `donnees/commandes.csv` en R de base (`tapply` sur un test logique), puis (c) avec `dplyr`, et (d) contrôlez le résultat avec pandas.

**Exercice 5 ⭐ (4.3.3 : une pile).** La notation polonaise inversée (NPI) écrit l'opérateur **après** ses opérandes : `3 4 +` signifie $3+4$. Elle se calcule avec une pile et n'a besoin d'aucune parenthèse. (a) Évaluez à la main `3 4 + 2 *`, puis `5 1 2 + 4 * + 3 -`. (b) Écrivez la fonction d'évaluation. (c) Le prix TTC d'un article à 80 € HT avec 10 % de remise s'écrit `80 1 0.1 - * 1.19 *` : calculez-le. (d) Que doit faire la fonction devant `3 +` ?

**Exercice 6 ⭐⭐ (4.3.3 : une file à deux emballeuses).** Six commandes arrivent aux minutes 0, 1, 2, 3, 10 et 11 ; emballer une commande dure 4 minutes. Calculez à la main l'attente de chaque commande (a) avec **une** emballeuse, (b) avec **deux**, puis écrivez la simulation. Indice : retenez, pour chaque emballeuse, l'instant où elle sera libre ; la prochaine commande est confiée à celle qui est libre **le plus tôt** (le module `heapq` sait trouver le plus petit élément).

**Exercice 7 ⭐⭐ (4.3.5 : une dichotomie à variante).** `bisect_left(liste, x)` renvoie la **première** position où $x$ pourrait être inséré dans une liste triée. (a) Évaluez à la main cette position pour $x=2$ dans `[1, 2, 2, 2, 5]`. (b) Écrivez votre propre version par dichotomie, en énonçant son invariant. (c) Déduisez-en le nombre de commandes ayant la note 5 dans la colonne `satisfaction` triée, et comparez avec `Counter`. (d) Vérifiez votre fonction contre `bisect_left` sur 1 000 listes aléatoires.

**Exercice 8 ⭐ (4.3.6 : tri stable).** Rangez les commandes `("Site", 40.1)`, `("Boutique", 65.8)`, `("Site", 19.6)`, `("Boutique", 17.4)`, `("Réseaux", 30.1)`, `("Site", 75.0)` **par canal croissant puis, dans chaque canal, par montant décroissant**, avec uniquement des appels à `sorted`. Dans quel ordre faut-il enchaîner les deux tris ? Que se passe-t-il si on les inverse ?

**Exercice 9 ⭐ (4.4 : NumPy et broadcasting).** Les quantités vendues sur trois jours pour (bol, tasse, plateau, bougie) sont les lignes de $Q=\begin{pmatrix}2&0&1&3\\1&1&0&0\\0&4&2&1\end{pmatrix}$, les prix HT sont `[12.5, 8, 45, 15.9]`. (a) Calculez à la main le chiffre d'affaires de chaque jour. (b) Une promotion retire `[0, 10 %, 0, 20 %]` aux prix ; recalculez le chiffre d'affaires quotidien **en une seule ligne** grâce au broadcasting. (c) Quel produit s'est le mieux vendu en nombre d'unités ?

**Exercice 10 ⭐⭐ (4.4 : groupby et dates).** Six ventes : (5 janv., Site, 30), (20 janv., Réseaux, 50), (2 févr., Site, 70), (10 févr., Site, 20), (11 févr., Boutique, 100), (1er mars, Réseaux, 40). (a) Dressez à la main le tableau **mois × canal** des montants et les totaux mensuels. (b) Obtenez-le avec `pivot_table`. (c) Sur les 400 commandes (avec les colonnes `date` et `id_client` simulées en 4.4.5), quel mois rapporte le plus, et quel jour de la semaine compte le plus de commandes ?

**Exercice 11 ⭐⭐ (4.4.10 : jointure et clients dormants).** (a) Quatre commandes portent les numéros de client `1, 1, 3, 5` ; la table des clients contient les numéros 1 à 5. Qui n'a jamais commandé ? (b) Sur les données du livre (table `clients` de 4.4.10), combien de clients n'ont **aucune** commande ? Répondez de deux façons : avec `isin`, puis avec une jointure `left` et le comptage des valeurs manquantes. (c) Quel est le chiffre d'affaires par ville ?

**Exercice 12 ⭐⭐ (4.5 : un graphique honnête).** Tracez le montant moyen par canal en barres **triées par ordre décroissant**, avec un axe qui commence à zéro, un titre qui énonce le message, des axes nommés avec leur unité. Vérifiez par le code que les hauteurs des barres sont bien les moyennes, que l'axe commence à 0 et que le fichier est enregistré. Citez deux défauts qu'aurait une version avec axe tronqué et camembert 3D.

**Exercice 13 ⭐⭐ (4.6 : un test unitaire).** Règle de livraison : retrait en boutique gratuit ; sur le Site ou Réseaux, 7 €, **offerts à partir de 100 € TTC** (100 compris) ; un canal inconnu est une erreur. (a) Dressez la liste des cas à tester, en pensant aux **bornes**. (b) Écrivez la fonction **avec le défaut classique** (`>` au lieu de `>=`) et les tests avec `pytest` ; constatez l'échec. (c) Corrigez et relancez.

**Exercice 14 ⭐⭐⭐ (4.8 : coût d'un algorithme).** On veut compter les **paires de commandes passées par le même client**. (a) Combien de paires de commandes y a-t-il en tout parmi $n=400$ ? Et parmi $n=800$ ? Quel est le facteur ? (b) Écrivez la version « double boucle » et comptez ses tours. (c) Écrivez une version en $O(n)$ avec un dictionnaire de compteurs (un client avec $c$ commandes produit $c(c-1)/2$ paires). (d) Vérifiez qu'elles donnent le même résultat. (e) Estimez, avec la formule, le nombre de tours de la double boucle pour un million de commandes.

### Corrigés

**Corrigé 1.** Site : $40+60=100$ ; Réseaux : $25+35=60$ ; Boutique : $100$. Total : $260$. Parts : $100/260\approx38{,}5\,\%$ pour le Site, $60/260\approx23{,}1\,\%$ pour Réseaux, $38{,}5\,\%$ pour la Boutique (la somme des parts doit faire 100 %).

```python
commandes = [("Site", 40), ("Réseaux", 25), ("Site", 60), ("Boutique", 100), ("Réseaux", 35)]
ca = {}
for canal, montant in commandes:
    ca[canal] = ca.get(canal, 0) + montant          # .get évite la KeyError au premier passage
total = sum(ca.values())
for canal, valeur in sorted(ca.items()):
    print(f"{canal:<10} {valeur:>4} €   {valeur / total:6.1%}")
print("total :", total, "| somme des parts :", round(sum(v / total for v in ca.values()), 6))
```
<!--sortie-->
```text
Boutique    100 €    38.5%
Réseaux    60 €    23.1%
Site        100 €    38.5%
total : 260 | somme des parts : 1.0
```

**Corrigé 2.** (a) Le programme cherche `CATALOGUE["vase"]`, qui n'existe pas : Python s'arrête avec `KeyError: 'vase'` (voir 4.1.8). (b) On rattrape l'erreur avec `try / except KeyError`, et on utilise la clé fautive que l'exception transporte. (c) On sépare les produits connus des inconnus **avant** de calculer. À la main : 2 bols $=25$ € HT, sous le seuil de remise ; TVA $25\times0{,}19=4{,}75$ ; TTC $=29{,}75$ €.

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

On retrouve le TTC de 29,75 € calculé à la main, et `'vase'` est signalé comme ignoré. Le choix entre « refuser le panier » (b) et « ignorer et signaler » (c) est une **décision métier**, pas technique : ce qui compte, c'est de ne jamais avaler une erreur en silence.

> ⚠️ **Piège.** Un `except:` nu (sans type d'erreur) rattrape *tout*, y compris vos propres fautes de frappe : on ne rattrape que l'erreur **attendue** (`KeyError`, `ValueError`…).

**Corrigé 3.** Panier de 4.1.10 : sous-total HT $=117{,}70$. Remise fidélité : $10\,\%$ soit $11{,}77$ € ; remise promo : $15\,\%$ soit $17{,}655$ €. On garde la meilleure, la promo : net $=117{,}70\times0{,}85=100{,}045$ ; TTC $=100{,}045\times1{,}19=119{,}05355\approx119{,}05$ € (contre $126{,}06$ sans code). Panier de 2 tasses : HT $=16$, pas de remise fidélité (sous 100 €), promo 15 % : net $=13{,}60$, TTC $=13{,}60\times1{,}19=16{,}184\approx16{,}18$ €.

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
 Boutique Réseaux      Site 
    0.956     0.630     0.696 
# A tibble: 3 × 3
  canal         n part_satisfaits
  <chr>     <int>           <dbl>
1 Boutique    114           0.956
2 Réseaux   138           0.63 
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
Réseaux    0.630
Site         0.696
Name: satisfaction, dtype: float64
```

Les trois méthodes donnent les mêmes proportions : 95,6 % de commandes satisfaites en **Boutique**, 69,6 % sur le **Site** et 63,0 % sur **Réseaux**. La Boutique est loin devant : le retrait est immédiat, or la satisfaction baisse d'environ 0,18 point par jour de délai (4.2.5). C'est une description de l'échantillon : savoir si un écart est *significatif* demanderait un test, comme au 3.4.

**Corrigé 5.** (a) `3 4 + 2 *` : on empile 3 puis 4 ; `+` dépile 4 et 3 et empile 7 ; on empile 2 ; `*` dépile 2 et 7 et empile 14. Résultat : $(3+4)\times2=14$. Pour `5 1 2 + 4 * + 3 -` : pile `[5]`, `[5,1]`, `[5,1,2]` ; `+` → `[5,3]` ; `4` → `[5,3,4]` ; `*` → `[5,12]` ; `+` → `[17]` ; `3` → `[17,3]` ; `-` → `[14]`. Soit $5+(1+2)\times4-3=14$. **Attention à l'ordre** : pour `-` et `/`, le **premier** dépilé est l'opérande de **droite**. (c) $80\times(1-0{,}1)\times1{,}19=85{,}68$ €.

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
cmds = [("Site", 40.1), ("Boutique", 65.8), ("Site", 19.6), ("Boutique", 17.4), ("Réseaux", 30.1), ("Site", 75.0)]
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
   ('Réseaux', 30.1)
   ('Site', 75.0)
   ('Site', 40.1)
   ('Site', 19.6)
ordre inversé (faux) :
   ('Site', 75.0)
   ('Boutique', 65.8)
   ('Site', 40.1)
   ('Réseaux', 30.1)
   ('Site', 19.6)
   ('Boutique', 17.4)
```

Le bon résultat est Boutique (65,8 puis 17,4), Réseaux (30,1), Site (75,0 ; 40,1 ; 19,6). Dans la version inversée, le dernier tri est celui des montants : les canaux sont mélangés, et leur ordre n'est conservé que pour les montants égaux, ce qui n'arrive pas ici. Raccourci équivalent : `sorted(cmds, key=lambda c: (c[0], -c[1]))`.

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

**Corrigé 10.** (a) Janvier : Réseaux 50, Site 30, Boutique 0 (total 80). Février : Site $70+20=90$, Boutique 100 (total 190). Mars : Réseaux 40 (total 40). (b) et (c) :

```python
mini = pd.DataFrame({
    "date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-02-02", "2026-02-10", "2026-02-11", "2026-03-01"]),
    "canal": ["Site", "Réseaux", "Site", "Site", "Boutique", "Réseaux"],
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
print("mois le plus rentable :", par_mois["total"].idxmax(), "(", par_mois["total"].max(), "€ )")

noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
par_jour = df["date"].dt.dayofweek.value_counts().sort_index()
print()
print({noms[j]: int(n) for j, n in par_jour.items()})
print("jour le plus chargé :", noms[par_jour.idxmax()])
```
<!--sortie-->
```text
canal  Boutique  Réseaux  Site  total
mois                                   
1             0         50    30     80
2           100          0    90    190
3             0         40     0     40

canal  Boutique  Réseaux    Site   total
mois                                      
1        1861.0      853.0  1483.0  4197.0
2        1316.0     1366.0  1863.0  4545.0
3        1948.0     2073.0  2037.0  6058.0
4        1648.0      998.0  1752.0  4398.0
5        1755.0     1473.0  1672.0  4900.0
mois le plus rentable : 3 ( 6058.0 € )

{'lundi': 53, 'mardi': 63, 'mercredi': 65, 'jeudi': 53, 'vendredi': 51, 'samedi': 52, 'dimanche': 63}
jour le plus chargé : mercredi
```

Le tableau de la main est reproduit exactement par `pivot_table` (le `fill_value=0` remplace les cases vides par 0 au lieu de `NaN`). Sur les 400 commandes, **mars** est le mois le plus rentable (6 058 €). Attention toutefois à comparer des mois **inégalement couverts** : nos données vont du 5 janvier au 24 mai, donc janvier (27 jours) et mai (24 jours) sont incomplets, alors que mars l'est : un mois incomplet est un piège classique de lecture. Quant au jour de la semaine, les 140 jours de la période contiennent exactement 20 lundis, 20 mardis, etc. ; les dates ayant été tirées **au hasard et uniformément**, les écarts (de 51 commandes le vendredi à 65 le mercredi) ne sont que du hasard d'échantillonnage. Sur de vraies ventes, de telles différences guideraient les horaires d'ouverture ; ici, il ne faut surtout pas les « interpréter ».

**Corrigé 11.** (a) Les numéros 2 et 4 n'apparaissent dans aucune commande : ce sont les clients **dormants**. (b) et (c) :

```python
petit_clients = pd.DataFrame({"id_client": [1, 2, 3, 4, 5]})
petites_cmds = pd.DataFrame({"id_client": [1, 1, 3, 5]})
print("(a) sans commande :", petit_clients[~petit_clients["id_client"].isin(petites_cmds["id_client"])]["id_client"].tolist())

rng_c = np.random.default_rng(11)                                   # même recette qu'en 4.4.10
clients = pd.DataFrame({
    "id_client": np.arange(1, 126),
    "ville": rng_c.choice(["Ville H", "Ville F", "Ville G", "Ville E", "Ville B"], size=125, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
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
Ville H      10491.0
Ville G      5492.0
Ville F        4518.0
Ville E      2352.0
Ville B     1245.0
Name: montant, dtype: float64
somme : 24098.0 | total des commandes : 24098
```

Le contrôle de cohérence final (la **somme par ville égale le total**) est un réflexe : une jointure qui dupliquerait ou perdrait des lignes (clés en double, clés absentes avec `inner`) fausserait silencieusement les totaux. C'est pourquoi on précise `how="left"` quand on veut conserver toutes les commandes. Onze clients sur 125 n'ont jamais commandé : les cinq clients 121 à 125 (dormants **par construction**, ce que le résultat confirme) et six autres que le hasard a laissés de côté. Ville H réalise à elle seule près de 44 % du chiffre d'affaires.

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
ax.set_ylabel("montant moyen par commande (€)")

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
ordre des barres : ['Boutique', 'Site', 'Réseaux']
hauteurs = moyennes : True
axe vertical démarre à : 0.0
fichier enregistré : True
```

Les moyennes par canal sont celles obtenues au 4.1.9 (Boutique devant le Site, puis Réseaux). **Défauts d'une version truquée :** (1) un axe tronqué (par exemple de 45 à 75 €) ferait paraître la barre de la Boutique plusieurs fois plus haute que celle d'Réseaux alors que l'écart réel est de l'ordre de 50 % ; (2) un camembert en 3D déforme les aires par la perspective et force l'œil à comparer des angles, ce qu'il fait très mal ; pour trois catégories, des barres triées sont toujours plus lisibles.

**Corrigé 13.** (a) Cas à tester : boutique à n'importe quel montant (0) ; Site à 99,99 (7) ; Site **à 100,00 exactement** (0, la borne) ; Site à 150 (0) ; Réseaux à 50 (7) ; canal inconnu (erreur). Les **bornes** sont l'endroit où se cachent les bogues. (b) La version fautive utilise `>` : un panier à 100,00 € pile paierait 7 €.

```bash
cat > livraison_frais.py <<'FIN'
def frais_livraison(canal, total_ttc):
    """Frais de livraison en € : 0 en boutique ; 7 € sinon, offerts dès 100 € TTC."""
    if canal == "Boutique":
        return 0.0
    if canal in ("Site", "Réseaux"):
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
    ("Réseaux", 50.0, 7.0),
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

Le test de la borne a trouvé le défaut : pour 100,00 €, la fonction renvoie 7 au lieu de 0 ; les cinq autres tests passent, preuve qu'un test « du milieu » n'aurait rien vu. (c) On corrige (`>=`) et on relance :

```bash
sed -i 's/total_ttc > 100 else/total_ttc >= 100 else/; s/ *# <-- défaut volontaire.*//' livraison_frais.py
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_livraison_frais.py 2>&1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
......                                                                   [100%]
6 passed
```

> 🛠️ **À retenir.** On teste les **bornes** (juste en dessous, pile, juste au-dessus) et les **cas d'erreur**. Ces tests, écrits une fois, protégeront la règle des 100 € de toute régression future.

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
