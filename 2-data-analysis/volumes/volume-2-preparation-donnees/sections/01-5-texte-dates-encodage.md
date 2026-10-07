```python hide
import os, io, re, sys, glob, unicodedata
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

## 1.5 ➕ Pour aller plus loin : texte, dates et heures, encodage, données multilingues

> 🧭 **Section complémentaire.** Elle prolonge la section 1.4 par les défauts propres au **texte** : espaces, casse, accents, caractères invisibles, encodage, et l'arabe qui s'invite dans une colonne de villes. Le reste du chapitre ne la suppose pas.

Un tableau de nombres se nettoie avec des comparaisons ; un tableau de **texte** se nettoie avec des conventions, parce que deux chaînes qui paraissent identiques à l'écran peuvent être différentes pour l'ordinateur. Cette section en donne les quelques règles qui évitent 90 % des mauvaises surprises.

### 1.5.1 Espaces, casse et accents : comparer sans se tromper

Deux fichiers parlent des mêmes produits : le catalogue de la boutique et celui du fournisseur. Pour savoir combien de désignations du fournisseur correspondent à un produit de la boutique, on les compare. Voyons ce que donne une comparaison naïve, puis une comparaison **normalisée**.

```python
cat = pd.read_csv(os.path.join(D, "catalogue_fournisseur.csv"), dtype=str)
noms = set(pd.read_csv(os.path.join(D, "produits.csv"))["nom_produit"])
print("désignations du fournisseur :", len(cat), "| noms distincts à la boutique :", len(noms))
print("correspondance exacte :", int(cat["designation"].isin(noms).sum()))
print(cat["designation"].head(4).tolist())
```
<!--sortie-->
```text
désignations du fournisseur : 118 | noms distincts à la boutique : 60
correspondance exacte : 34
[' Pochette compact ', 'PLANCHE COMPACT', 'COUSSIN MAT', 'Diffu. design']
```

Sur 118 désignations, seules 34 correspondent exactement à un nom de la boutique. Les exemples montrent pourquoi : des espaces superflus (`'  Pochette compact '`), des majuscules (`'PLANCHE COMPACT'`), des abréviations (`'Diffu. design'`). Les deux premiers défauts se corrigent par **normalisation** ; le troisième exige un rapprochement approché (section 2.5).

On construit une **clé de comparaison** : on retire les espaces aux extrémités, on réduit les espaces multiples, on passe en minuscules et on supprime les accents. Cette clé ne remplace pas le texte d'origine (on garde l'original pour l'affichage) : elle sert uniquement à **comparer**.

```python
from unidecode import unidecode
def cle(texte):
    return re.sub(r"\s+", " ", unidecode(texte).strip().lower())
cles = {cle(n) for n in noms}
print("après strip et minuscules :", int(cat["designation"].str.strip().str.lower().isin({n.lower() for n in noms}).sum()), "| après clé complète (accents et espaces) :", int(cat["designation"].map(cle).isin(cles).sum()))
```
<!--sortie-->
```text
après strip et minuscules : 74 | après clé complète (accents et espaces) : 78
```

On passe de 34 à 74 correspondances en retirant espaces et majuscules, puis à 78 en supprimant les accents (`Étagère` devient `etagere`). Les 40 désignations restantes sont des abréviations, des mots dans un autre ordre ou des produits absents de la boutique : un problème de rapprochement, non de normalisation.

> ⚠️ **Piège.** Supprimer les accents est **une opération destructrice** : `cote` et `côté`, `ou` et `où`, deviennent identiques. Faites-le pour **comparer**, jamais pour **stocker**. Même précaution pour la casse : `str.title()` transforme « d'Alembert » en « D'Alembert » et « McDonald » en « Mcdonald ». Normalisez dans une colonne clé, gardez l'original à côté.

### 1.5.2 Unicode : le même caractère de deux façons, et le mojibake

Un caractère accentué peut s'écrire de deux manières en Unicode : en **un seul signe** (`é`, forme composée, NFC) ou en **deux signes** (la lettre `e` suivie d'un accent combinant, forme décomposée, NFD). À l'écran, c'est identique. Pour l'ordinateur, ce sont deux chaînes différentes.

```python
a, b = "Zoé", "Zoé"                      # « Zoé » : accent combinant, puis caractère composé
print(a == b, "| longueurs :", len(a), len(b), "| égales après normalisation NFC :", unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))
```
<!--sortie-->
```text
False | longueurs : 4 3 | égales après normalisation NFC : True
```

Deux chaînes qui s'affichent pareil mais ne sont pas égales, de longueurs différentes : c'est le genre de défaut qui fait **échouer une jointure sans raison apparente**. Le remède est de normaliser en NFC dès la lecture (`unicodedata.normalize("NFC", texte)`, ou `.str.normalize("NFC")` en pandas).

Le défaut le plus visible de ce genre est le **mojibake** : du texte lu avec le mauvais encodage. Le CRM en contient. Le caractère `é` s'écrit, en UTF-8, avec **deux octets** ; si un logiciel les lit comme deux caractères de l'ancien encodage Windows (cp1252), il affiche `Ã©`.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
mojibake = crm["nom"].str.contains("Ã|Â", regex=True)
print("é en UTF-8 :", "é".encode("utf-8"), "| lu comme cp1252 :", "é".encode("utf-8").decode("cp1252"))
print("noms abîmés dans le CRM :", int(mojibake.sum()), "|", crm.loc[mojibake, "nom"].head(3).tolist())
```
<!--sortie-->
```text
é en UTF-8 : b'\xc3\xa9' | lu comme cp1252 : Ã©
noms abîmés dans le CRM : 213 | ['TarvaneÃ©', 'SomariÃ©', 'RavtierÃ©']
```

Une bibliothèque, `ftfy` (*fixes text for you*), détecte ces enchaînements typiques et **inverse l'erreur** : elle devine que `Ã©` est un `é` mal décodé.

```python
import ftfy
corrige = crm.loc[mojibake, "nom"].map(ftfy.fix_text)
print(list(zip(crm.loc[mojibake, "nom"].head(3), corrige.head(3))))
print("noms intacts modifiés à tort par ftfy :", int((crm.loc[~mojibake, "nom"].map(ftfy.fix_text) != crm.loc[~mojibake, "nom"]).sum()))
```
<!--sortie-->
```text
[('TarvaneÃ©', 'Tarvaneé'), ('SomariÃ©', 'Somarié'), ('RavtierÃ©', 'Ravtieré')]
noms intacts modifiés à tort par ftfy : 0
```

La correction rend le texte **tel qu'il a été écrit** (le `é` final fait bien partie de la saisie abîmée) et ne modifie aucun des noms corrects : c'est ce que l'on attend d'un bon outil de réparation, qui doit être **conservateur**. Mais la meilleure réparation est de ne pas casser le texte : lire le fichier avec le **bon encodage** dès le départ (section 1.5.5).

### 1.5.3 Caractères invisibles et expressions régulières

Deux défauts échappent à l'œil : l'**espace insécable** (le caractère ` `, qui ressemble à une espace) et les caractères de largeur nulle, qui n'occupent aucune place à l'écran. Ils font échouer comparaisons et jointures.

```python
v1, v2 = "Ville A", "Ville A"
print(v1 == v2, "|", repr(v2), "| avec \\s dans une expression régulière :", re.sub(r"\s+", " ", v2) == v1)
```
<!--sortie-->
```text
False | 'Ville\xa0A' | avec \s dans une expression régulière : True
```

Dans une **expression régulière**, `\s` désigne toute espace (y compris l'insécable) : `re.sub(r"\s+", " ", texte)` est donc un bon réflexe de nettoyage. Les expressions régulières sont l'outil naturel de tout ce qui a une **forme** : téléphone, code postal, adresse électronique, référence produit. Voici les motifs les plus utiles.

| Besoin | Motif | Exemple |
|---|---|---|
| un chiffre, des chiffres | `\d`, `\d+` | `\d{5}` : exactement cinq chiffres |
| tout sauf un chiffre | `\D` | `re.sub(r"\D", "", "02 19.86")` retire les séparateurs |
| espace(s) | `\s`, `\s+` | `re.sub(r"\s+", " ", t)` |
| un ensemble de caractères | `[a-z]`, `[\w.+-]` | `[\w.+-]+@` : début d'une adresse |
| début, fin de chaîne | `^`, `$` | `str.fullmatch` impose que tout le texte corresponde |

Appliquons-les aux **numéros de téléphone** du CRM, écrits de cinq façons différentes. Classons d'abord les formats (sans afficher les numéros eux-mêmes : on ne diffuse pas de données personnelles pour illustrer un nettoyage).

```python
def forme(s):
    if s.startswith("+"):
        return "préfixe international"
    return "parenthèses" if s.startswith("(") else "points" if "." in s else "espaces" if " " in s else "chiffres collés"
print(crm["telephone"].map(forme).value_counts().to_string())
```
<!--sortie-->
```text
telephone
chiffres collés          1516
points                   1469
préfixe international    1420
parenthèses              1408
espaces                  1327
```

Cinq formes, à peu près également réparties. La normalisation retient les **chiffres** et traite à part le préfixe international (dont on remplace l'indicatif par le zéro initial, dans la convention locale). On accepte le résultat s'il a la forme attendue (dix chiffres commençant par 0), sinon on **rejette** : une valeur invalide vaut mieux qu'une valeur inventée.

```python
def telephone_propre(s):
    chiffres = re.sub(r"\D", "", s)
    if s.startswith("+"):                                    # préfixe international : l'indicatif (2 chiffres ici) devient 0
        chiffres = "0" + chiffres[2:]
    return chiffres if re.fullmatch(r"0\d{9}", chiffres) else None
crm["tel"] = crm["telephone"].map(telephone_propre)
print("numéros invalides :", int(crm["tel"].isna().sum()), "| formes distinctes après nettoyage :", int(crm["tel"].str.len().nunique()))
```
<!--sortie-->
```text
numéros invalides : 0 | formes distinctes après nettoyage : 1
```

Les 7 140 numéros se ramènent à une forme unique. Reste à **vérifier** que la normalisation n'invente rien : si deux lignes décrivent le même client, elles doivent avoir **le même numéro normalisé**.

```python
verite = pd.read_csv(os.path.join(D, "verite_crm.csv"))
crm["id_crm"] = crm["id_crm"].astype(int)
x = crm.merge(verite, on="id_crm")
x = x[x["id_client"] > 0]
print("clients dont les lignes ont plusieurs numéros normalisés différents :", int((x.groupby("id_client")["tel"].nunique() > 1).sum()), "sur", x["id_client"].nunique())
```
<!--sortie-->
```text
clients dont les lignes ont plusieurs numéros normalisés différents : 0 sur 6000
```

> ✅ **À retenir.** Quatre gestes pour normaliser un texte : **couper** les espaces, **réduire** les espaces multiples (`\s+`), **uniformiser** la casse et, si l'on compare, les accents, puis **vérifier** la forme avec `fullmatch`. Et toujours **conserver l'original** à côté de la valeur nettoyée.

### 1.5.4 Dates et heures : fuseaux et heure d'été

Une heure sans fuseau est ambiguë. L'export du site écrit les dates de deux façons : `2025-03-04 14:22:05` jusqu'au 14 septembre (heure sans indication) et `2025-09-15T14:22:05Z` à partir du 15 (le `Z` signifie « heure UTC », l'heure du méridien de référence). Si ce `Z` était vrai, les commandes du jour se répartiraient autrement : une boutique située à une heure ou deux de UTC verrait ses heures de commande **décalées d'autant**. Regardons.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
site["utc"] = site["created_at"].str.endswith("Z")
site["heure"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="mixed").dt.hour
print(site.groupby("utc")["heure"].agg(["size", "mean"]).round(2).rename(index={False: "sans indication", True: "avec Z"}).to_string())
```
<!--sortie-->
```text
                 size   mean
utc                         
sans indication  3741  15.45
avec Z           2518  15.37
```

L'heure moyenne d'une commande est de 15,45 avant le 15 septembre et de 15,37 après : **aucun décalage** d'une ou deux heures. Le `Z` n'a donc **pas** accompagné un changement réel de fuseau : soit la plateforme étiquette « UTC » des heures locales (le plus probable), soit les clients ont brusquement changé d'habitude. On ne tranche pas par un calcul : on **pose la question** à l'équipe qui gère la plateforme. Retenez le raisonnement : **comparer une distribution avant et après un changement de format** est un bon test de cohérence.

Le passage à l'heure d'été ajoute une difficulté. Quand l'horloge avance (au printemps), une heure locale **n'existe pas** ; quand elle recule (en automne), une heure locale existe **deux fois**. Le même texte `02:30` désigne alors deux instants différents, ce que seul le décalage par rapport à UTC distingue.

```python
avant = pd.Timestamp("2025-10-26 02:30:00+02:00").tz_convert("UTC")
apres = pd.Timestamp("2025-10-26 02:30:00+01:00").tz_convert("UTC")
print("02:30 locale, première fois :", avant, "| deuxième fois :", apres, "| écart :", apres - avant)
```
<!--sortie-->
```text
02:30 locale, première fois : 2025-10-26 00:30:00+00:00 | deuxième fois : 2025-10-26 01:30:00+00:00 | écart : 0 days 01:00:00
```

> 🧭 **En pratique.** Pour les dates : stockez en **ISO 8601** (`AAAA-MM-JJTHH:MM:SS`) ; **indiquez le fuseau** (ou stockez en UTC) dès que des données viennent de plusieurs sources ; écrivez toujours le **format** à la lecture (`format="%d/%m/%Y"`) ; et méfiez-vous des calculs de durée à travers un changement d'heure.

### 1.5.5 Encodage : cp1252, UTF-8 et la marque d'ordre des octets

Un fichier texte n'est qu'une suite d'octets ; l'**encodage** dit comment les transformer en caractères. Les deux que vous rencontrerez : **cp1252** (ancien encodage de Windows pour l'Europe occidentale) et **UTF-8** (le standard actuel, qui sait tout écrire, de l'accent au caractère arabe). Un fichier UTF-8 peut commencer par trois octets invisibles, la **marque d'ordre des octets** (*BOM*), ajoutée par certains logiciels. Les douze fichiers de caisse en fournissent une démonstration.

```python
janvier = open(os.path.join(D, "caisse", "caisse_2025-01.csv"), "rb").read()
juillet = open(os.path.join(D, "caisse", "caisse_2025-07.csv"), "rb").read()
print("début de janvier :", janvier[:3], "| début de juillet :", juillet[:3])
print("juillet lu en cp1252 :", repr(juillet.decode("cp1252")[:27]))
try:
    janvier.decode("utf-8")
except UnicodeDecodeError as erreur:
    print("janvier lu en UTF-8 :", str(erreur))
```
<!--sortie-->
```text
début de janvier : b'Exp' | début de juillet : b'\xef\xbb\xbf'
juillet lu en cp1252 : 'ï»¿Export caisse - Boutique'
janvier lu en UTF-8 : 'utf-8' codec can't decode byte 0xe9 in position 33: invalid continuation byte
```

Le fichier de juillet commence par les trois octets `ef bb bf` du BOM : lu comme du cp1252, ils s'affichent `ï»¿` devant le premier mot (c'est ce « ï»¿ » que l'on voit parfois en tête d'une colonne mal lue). Le fichier de janvier, lui, n'est **pas** de l'UTF-8 : le `é` est codé par un seul octet (`0xe9`), ce qui est interdit en UTF-8, d'où l'erreur. La règle de lecture est celle de la fonction écrite en 1.4.6 : **essayer UTF-8 d'abord** (qui échoue bruyamment sur un fichier qui n'en est pas), puis cp1252 ; avec `utf-8-sig`, le BOM est avalé.

> ⚠️ **Piège.** Lire un fichier cp1252 en UTF-8 plante (bruyant, donc tant mieux) ; lire un fichier UTF-8 en cp1252 ne plante **jamais** et produit du mojibake (silencieux, donc dangereux). Quand vous voyez `Ã©` dans vos données, c'est un UTF-8 lu en cp1252 : relisez le fichier avec le bon encodage plutôt que de réparer le texte après coup.

### 1.5.6 Données multilingues : l'arabe dans une colonne de villes

La boutique a des clients arabophones, et certains ont saisi leur ville dans leur langue : la ville A s'écrit `المدينة أ` (« la ville A »). Sur 7 000 lignes, 191 (2,7 %) sont dans ce cas. Trois choses méritent d'être comprises avant de traiter ce texte, sans être spécialiste de la langue.

**L'ordre logique et l'ordre d'affichage.** L'arabe s'écrit de droite à gauche. Mais le fichier stocke les caractères **dans l'ordre où on les lit** (ordre logique) ; c'est l'affichage qui les range de droite à gauche. Le dernier caractère de la chaîne est donc bien la dernière lettre lue, quelle que soit sa position à l'écran.

```python
ville = "المدينة أ"
print("longueur :", len(ville), "| dernier caractère :", ville[-1], unicodedata.name(ville[-1]), "| sens d'écriture :", unicodedata.bidirectional(ville[-1]), "(AL = arabe, L = latin)")
```
<!--sortie-->
```text
longueur : 9 | dernier caractère : أ ARABIC LETTER ALEF WITH HAMZA ABOVE | sens d'écriture : AL (AL = arabe, L = latin)
```

**Les signes qui varient.** L'arabe s'écrit avec ou sans **voyelles brèves** (signes combinants placés au-dessus ou au-dessous des lettres, par exemple dans un texte vocalisé), et peut étirer les lettres par un trait horizontal décoratif (le *tatweel*). Deux écritures qui se lisent pareil sont alors deux chaînes différentes, que l'on **normalise** en retirant ces signes.

```python
vocalise = "الْمَدِينَة"
simple = re.sub("[\u064b-\u065f\u0640]", "", vocalise)         # voyelles brèves et tatweel
print("caractères avant :", len(vocalise), "| après :", len(simple), "| résultat :", simple)
```
<!--sortie-->
```text
caractères avant : 11 | après : 7 | résultat : المدينة
```

**Une normalisation qui détruit.** Ici, le piège est subtil : la lettre qui distingue les villes (`أ`, alef avec hamza) a des variantes proches (`ا`, `إ`, `آ`) que beaucoup de recettes de normalisation **fusionnent**. Appliquée à `المدينة أ`, une telle recette donnerait `المدينة ا` : la ville A et d'éventuelles autres lettres se confondraient, ce qui casserait notre table de correspondance. Notre fonction `ville_propre` (section 1.4.4) s'appuie sur la lettre **exacte**, et la **table de correspondance** garde la trace de chaque substitution.

> 🧪 **Remarque.** Il n'existe pas de recette universelle pour le texte multilingue. Trois habitudes simples : **conserver l'original** et ajouter une colonne normalisée ; **ne normaliser que ce que l'on sait** (retirer les voyelles brèves est sûr, fusionner des lettres ne l'est pas) ; **faire valider** par un lecteur de la langue les correspondances qui comptent. Un français tiré de l'arabe, ou l'inverse, ne se « transcrit » pas par une simple substitution de caractères.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercice 1.10.
