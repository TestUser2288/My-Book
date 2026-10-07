## 4.1 Les fondamentaux de pandas

**pandas** est la bibliothèque de Python qui sait manipuler des tables : lire un fichier, trier, filtrer, calculer de nouvelles colonnes, regrouper. Cette section en donne les gestes de base, un par un, sur les commandes de la boutique. Elle commence par quelques mots de Python, juste ce qu'il faut pour lire les exemples sans se perdre.

### 4.1.1 Python en dix minutes

Python est un langage où l'on **donne des noms à des valeurs** (des *variables*), puis où l'on calcule avec ces noms. Le signe `=` n'est pas une égalité mathématique : il range une valeur sous un nom. Tout ce qui suit un `#` est un commentaire, ignoré par l'ordinateur.

```python
prix = 19.9                 # un nombre décimal
quantite = 3                # un nombre entier
total = prix * quantite
print(total)
print(round(total, 2))
```
<!--sortie-->
```text
59.699999999999996
59.7
```

Le premier résultat étonne : l'ordinateur calcule en binaire, et la plupart des décimaux ne s'y écrivent pas exactement, d'où un résidu minuscule. Pour **afficher** un montant, on arrondit avec `round`. Ce détail explique pourquoi, dans tout le chapitre, nos montants sont arrondis à deux décimales avant d'être affichés ou comparés.

Deux structures reviennent sans cesse. Une **liste** range des éléments dans l'ordre, entre crochets ; on en prend un par sa position, **en commençant à zéro**. Un **dictionnaire** range des paires « clé : valeur » entre accolades ; on retrouve une valeur par sa clé. Une **fonction** est une recette à laquelle on donne un nom : `def` la définit, `return` renvoie le résultat, et l'indentation (quatre espaces) délimite son contenu.

```python
canaux = ["Boutique", "Site", "Réseaux"]
remises = {"SOLDES": 0.20, "BIENVENUE": 0.10, "FIDELITE": 0.05}

def prix_remise(prix, code):
    return prix * (1 - remises.get(code, 0))     # sans code connu : remise 0

print(canaux[0], len(canaux), remises["SOLDES"])
print(round(prix_remise(49.9, "FIDELITE"), 2), round(prix_remise(49.9, "AUCUN"), 2))
```
<!--sortie-->
```text
Boutique 3 0.2
47.4 49.9
```

Enfin, Python ne connaît au départ qu'une petite partie de ce qu'il sait faire : pour le reste, on **importe** des bibliothèques. La ligne `import pandas as pd` charge pandas et lui donne le surnom `pd`, que tout le monde utilise. Chaque fonction de la bibliothèque s'appelle ensuite par `pd.nom_de_la_fonction`.

> 🧭 **En pratique.** Vous n'avez pas besoin de maîtriser davantage de Python pour la suite : on se sert surtout de pandas, et ses gestes s'apprennent en les pratiquant. Quand un message d'erreur apparaît, lisez sa **dernière ligne** : elle dit presque toujours ce qui ne va pas (un nom mal orthographié, une parenthèse oubliée).

### 4.1.2 Le DataFrame et la Series

Dans pandas, une table s'appelle un **DataFrame** : des lignes (les observations), des colonnes (les variables), chaque colonne ayant **un seul type**. Une colonne prise isolément est une **Series**. Le gabarit de lecture est toujours le même : `pd.read_csv("fichier.csv")` renvoie un DataFrame.

```python
commandes = pd.read_csv("donnees/commandes.csv")
print(commandes.shape)
print(commandes.head(3))
```
<!--sortie-->
```text
(36395, 7)
   id_commande date_commande  heure  id_client     canal   mode_livraison code_promo
0            1    2023-01-01  15:35       2637      Site         Domicile        NaN
1            2    2023-01-01  16:32         96  Boutique  Retrait magasin        NaN
2            3    2023-01-01  18:07       3490  Boutique  Retrait magasin        NaN
```

`shape` donne le nombre de lignes et de colonnes ; `head(3)` montre les trois premières lignes (sans argument, cinq). Regardez toujours vos données après les avoir lues : ce petit coup d'œil détecte la moitié des problèmes. Le **type** de chaque colonne se lit avec `dtypes`.

```python
print(commandes.dtypes)
```
<!--sortie-->
```text
id_commande       int64
date_commande       str
heure               str
id_client         int64
canal               str
mode_livraison      str
code_promo          str
dtype: object
```

Les colonnes numériques sont de type `int64` (entiers) ou `float64` (décimaux). Les textes sont de type `str`, depuis la version 3 de pandas ; dans les versions plus anciennes, vous verriez `object`, et un bloc de code écrit pour l'une fonctionne presque toujours avec l'autre. Remarquez que `date_commande` est lue comme **du texte** : pandas ne devine pas qu'il s'agit de dates. Nous allons le lui dire.

### 4.1.3 Lire un fichier : les arguments qui comptent

`read_csv` accepte des dizaines d'arguments. Une poignée suffit presque toujours.

| Argument | À quoi il sert | Exemple |
|---|---|---|
| `sep` | le séparateur de colonnes | `sep=";"` (fichiers « à la française ») |
| `decimal` | le signe décimal | `decimal=","` |
| `encoding` | le codage des caractères accentués | `encoding="cp1252"` (anciens fichiers Windows) |
| `parse_dates` | les colonnes à lire comme des dates | `parse_dates=["date_commande"]` |
| `dtype` | forcer le type d'une colonne | `dtype={"id_client": "str"}` |
| `usecols`, `nrows` | ne lire que certaines colonnes, ou les premières lignes | `usecols=["id_ligne", "montant"]`, `nrows=1000` |
| `na_values` | les textes à traiter comme « manquant » | `na_values=["n/a", "-"]` |

On range donc les dates dans le bon type dès la lecture. Voici le chargement de toutes les tables dont nous aurons besoin dans ce chapitre.

```python
commandes = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
lignes = pd.read_csv("donnees/lignes_commande.csv")
produits = pd.read_csv("donnees/produits.csv")
clients = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
retours = pd.read_csv("donnees/retours.csv", parse_dates=["date_retour"])
jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
print({nom: len(t) for nom, t in [("commandes", commandes), ("lignes", lignes), ("clients", clients), ("retours", retours)]})
print(commandes["date_commande"].dtype)
```
<!--sortie-->
```text
{'commandes': 36395, 'lignes': 83905, 'clients': 6000, 'retours': 5002}
datetime64[us]
```

Le type affiché pour la date, `datetime64`, est celui des **dates et heures** : on peut désormais en extraire l'année, le mois, le jour de la semaine, ou les comparer. Un type bien choisi à la lecture évite des heures de travail ensuite.

> ⚠️ **Piège : un identifiant n'est pas un nombre.** Le numéro d'un client ou d'une commande se lit comme un entier, mais ne se somme pas et ne se moyenne pas : « le numéro moyen des clients » n'a aucun sens. Quand un identifiant commence par des zéros (`00123`), la lecture comme entier les supprime : forcez alors `dtype="str"`. La section 5.1 reviendra sur cette distinction entre types de données.

### 4.1.4 Sélectionner : colonnes, lignes, cellules

Il y a trois façons de désigner une partie d'une table. Les **crochets** sélectionnent des **colonnes** : un nom donne une Series, une liste de noms donne un DataFrame.

```python
canal = commandes["canal"]                        # une colonne : une Series
extrait = commandes[["id_commande", "canal"]]     # deux colonnes : un DataFrame
print(type(canal).__name__, extrait.shape)
```
<!--sortie-->
```text
Series (36395, 2)
```

`.loc` sélectionne par **étiquette** (le nom des lignes et des colonnes) ; `.iloc` sélectionne par **position** (le rang, en commençant à zéro). Les deux se ressemblent et se comportent **différemment** sur un point : avec `.loc`, la borne de fin est **incluse** ; avec `.iloc`, elle est **exclue**.

```python
print(commandes.loc[0:2, ["id_commande", "canal"]])
print(commandes.iloc[0:2, [0, 4]])
```
<!--sortie-->
```text
   id_commande     canal
0            1      Site
1            2  Boutique
2            3  Boutique
   id_commande     canal
0            1      Site
1            2  Boutique
```

La première commande renvoie trois lignes (les étiquettes 0, 1 et 2), la seconde deux lignes (les positions 0 et 1). C'est l'une des sources d'erreur les plus fréquentes des débutants : en cas de doute, comptez les lignes obtenues.

### 4.1.5 Filtrer : garder les lignes qui répondent à une condition

Filtrer, c'est garder les lignes pour lesquelles une condition est vraie. On écrit la condition comme un calcul, qui produit une colonne de vrais et de faux, et on la passe entre crochets. Pour combiner plusieurs conditions, on utilise `&` (et), `|` (ou) et `~` (non), **en entourant chaque condition de parenthèses** quand on les écrit en une seule expression.

Combien de commandes passées sur le Site en 2025 avec le code `SOLDES` ?

```python
est_site = commandes["canal"] == "Site"
en_2025 = commandes["date_commande"].dt.year == 2025
avec_soldes = commandes["code_promo"] == "SOLDES"
print(len(commandes[est_site & en_2025 & avec_soldes]))
```
<!--sortie-->
```text
495
```

Trois conditions, nommées une à une, se relisent mieux qu'une seule ligne interminable. La méthode `query` permet d'écrire le même filtre sous forme de texte, souvent plus lisible ; `isin` teste l'appartenance à une liste ; `between` teste l'appartenance à un intervalle (bornes incluses).

```python
n_query = len(commandes.query("canal == 'Site' and date_commande >= '2025-01-01' and code_promo == 'SOLDES'"))
n_isin = commandes["canal"].isin(["Boutique", "Réseaux"]).sum()
n_nov = commandes["date_commande"].between("2025-11-01", "2025-11-30").sum()
print(n_query, n_isin, n_nov)
```
<!--sortie-->
```text
495 20932 1509
```

On retrouve les 495 commandes du premier filtre (par une autre écriture), puis 20 932 commandes passées en boutique ou sur les réseaux, et 1 509 commandes en novembre 2025. Les mêmes comptages en R sont faits en section 4.2.

### 4.1.6 Colonnes calculées et tri

Créer une colonne, c'est lui donner un nom et un calcul qui porte sur d'autres colonnes, ligne par ligne. La méthode `assign` le fait sans modifier la table d'origine : elle renvoie une **nouvelle** table. Sur les lignes de commande, calculons le montant avant remise, la remise en euros, puis vérifions que le fichier est cohérent.

```python
l2 = lignes.assign(
    brut=lambda d: d["quantite"] * d["prix_unitaire"],
    remise_eur=lambda d: d["brut"] * d["remise_pct"] / 100,
)
print((l2["brut"] - l2["remise_eur"] - l2["montant"]).abs().max().round(2))
```
<!--sortie-->
```text
0.01
```

La notation `lambda d: …` se lit « pour une table `d`, calculer … » : elle permet à la seconde colonne d'utiliser la première, tout juste créée. Le plus grand écart vaut un centime : `montant = quantité × prix × (1 − remise)` pour **toutes** les lignes, à l'arrondi du montant au centime près. Le fichier est cohérent, et nous pourrons nous fier à `montant`.

Trier se fait par `sort_values`, en précisant la colonne et le sens. Les cinq lignes les plus chères :

```python
print(l2.sort_values("montant", ascending=False).head(5)[["id_ligne", "quantite", "prix_unitaire", "remise_pct", "montant"]])
```
<!--sortie-->
```text
       id_ligne  quantite  prix_unitaire  remise_pct  montant
68711     68712         4         157.49           0   629.96
78316     78317         4         157.49           0   629.96
70637     70638         4         157.49           0   629.96
64160     64161         4         157.49           0   629.96
23327     23328         4         152.90           0   611.60
```

### 4.1.7 Valeurs manquantes et comptages

Une cellule vide est lue comme **`NaN`** (« not a number »), la valeur manquante de pandas. `isna()` la détecte, et la somme des vrais donne le nombre de manquants par colonne.

```python
print(commandes.isna().sum())
```
<!--sortie-->
```text
id_commande           0
date_commande         0
heure                 0
id_client             0
canal                 0
mode_livraison        0
code_promo        30652
dtype: int64
```

Seul `code_promo` a des manquants, pour une raison **métier** : une cellule vide signifie « pas de code promotionnel ». Ce n'est pas une donnée perdue. Pour compter proprement, on le dit explicitement avec `fillna`, puis `value_counts` donne la fréquence de chaque valeur ; avec `normalize=True`, des proportions.

```python
codes = commandes["code_promo"].fillna("aucun")
print((codes.value_counts(normalize=True) * 100).round(1))
```
<!--sortie-->
```text
code_promo
aucun        84.2
SOLDES        8.3
FIDELITE      6.7
BIENVENUE     0.9
Name: proportion, dtype: float64
```

> ⚠️ **Piège : `NaN` n'est égal à rien, pas même à lui-même.** `commandes["code_promo"] == np.nan` ne renvoie que des faux : pour tester un manquant, utilisez toujours `isna()` (ou `notna()`). Par ailleurs, la plupart des calculs (somme, moyenne) **ignorent** les `NaN` : une moyenne sur une colonne à moitié vide est une moyenne sur la moitié des lignes, sans le dire. Interrogez toujours le nombre de manquants **avant** de calculer.

### 4.1.8 La méthode chaînée

Chaque méthode de pandas renvoie une table, sur laquelle on peut appliquer la suivante : on peut donc **enchaîner** les étapes, une par ligne, dans des parenthèses. Le résultat se lit de haut en bas comme une recette. Quelle est, selon le canal, la part des commandes de 2025 passées avec un code promotionnel ?

```python
part_promo = (
    commandes
    .loc[commandes["date_commande"].dt.year == 2025]
    .assign(avec_code=lambda d: d["code_promo"].notna())
    .groupby("canal")["avec_code"].mean()
    .mul(100).round(1)
)
print(part_promo)
```
<!--sortie-->
```text
canal
Boutique    15.1
Réseaux     15.0
Site        15.8
Name: avec_code, dtype: float64
```

La part est d'environ 15 % dans les trois canaux : les codes ne sont pas l'affaire d'un canal en particulier. Chaque ligne du programme est une étape : on garde 2025, on ajoute un indicateur « a un code », on regroupe par canal, on prend la moyenne de l'indicateur (la moyenne de vrais et de faux est la proportion de vrais), on exprime en pourcentage. Ce style est précisément celui que le tidyverse rend plus naturel encore, comme on le voit en 4.2.

Une dernière propriété mérite d'être connue : dans pandas 3, un extrait de table est toujours **une copie indépendante**. Modifier l'extrait ne touche jamais la table d'origine, ce qui supprime une classe entière d'erreurs qui hantait les versions précédentes.

```python
extrait = commandes.loc[commandes["canal"] == "Site"].copy()
extrait["canal"] = "X"
print(commandes["canal"].unique().tolist())
```
<!--sortie-->
```text
['Site', 'Boutique', 'Réseaux']
```

> ✅ **À retenir.** Une table pandas est un *DataFrame* ; on **lit** en précisant séparateur, décimale, encodage et colonnes de dates ; on **sélectionne** avec `[]`, `.loc` (étiquettes, fin incluse) et `.iloc` (positions, fin exclue) ; on **filtre** avec des conditions combinées par `&`, `|`, `~` ; on **calcule** avec `assign` ; on **compte** avec `value_counts` ; on **enchaîne** les étapes entre parenthèses. Un manquant se détecte par `isna()`, jamais par `==`.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 et 4.2, exercices 4.1 à 4.5.
