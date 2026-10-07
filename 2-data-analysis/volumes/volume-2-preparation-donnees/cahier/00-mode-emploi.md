# Mode d'emploi

> « On nettoie en regardant, on valide en recoupant. »

Ce cahier est le **compagnon du livre** du volume II (*Préparation des données*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (nettoyer et réconcilier deux sources désordonnées en un jeu de données fiable) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Regardez les données avant de les corriger.** Ouvrez le fichier, comptez les lignes, listez les valeurs distinctes d'une colonne, regardez les premières et les dernières lignes. Un tiers des erreurs se voit à cette étape.
3. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre.
4. **Écrivez ce que vous décidez.** Pour chaque règle de nettoyage, notez ce qu'elle fait, pourquoi, et **combien de lignes** elle touche. C'est l'habitude centrale du volume.
5. **Vérifiez par un second chemin.** Un total obtenu par pandas se recoupe par SQL ou par une autre source ; un écart est un signal, pas un détail.
6. **N'utilisez pas les fichiers `verite_*` pour décider.** Ce sont des corrigés : on les ouvre après avoir fait son travail, pour mesurer ce qu'on a bien et mal fait.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 2.1 : première application du chapitre 2 |
| Exercice | `Exercice N.k` | Exercice 2.3 : troisième exercice du chapitre 2 |
| Corrigé | `Corrigé N.k` | Corrigé 2.3 : correction de l'exercice 2.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une idée ou d'un geste vu dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, un choix de règle ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/`. Elles sont toutes **simulées**, avec des graines fixes (script `build/donnees_a2.py`) : vos résultats seront identiques à ceux du livre. Le catalogue complet figure dans la section « Carte du volume, données et environnement » du livre ; en voici l'essentiel.

| Fichier | Contenu | Chapitres |
|---|---|---|
| `crm_clients.csv` | le fichier clients : doublons, formats mêlés, lignes de test | 1, 2, 3, 5, projet |
| `site_commandes.csv`, `site_lignes.csv` | export de la plateforme web (Site, 2025) | 1, 2, 3, projet |
| `caisse/caisse_2025-01.csv` … `-12.csv` | exports mensuels de la caisse, trois réglages différents | 1, 2, 3, projet |
| `catalogue_fournisseur.csv` | catalogue d'un fournisseur | 2, 3 |
| `stocks_tableur.xlsx` | stocks saisis dans un tableur | 2 |
| `profil_clients.csv` | profils avec des valeurs manquantes | 1 |
| `montants_saisis.csv` | montants avec anomalies de saisie | 1, 3 |
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv` | la base propre du volume I | tous |
| `verite_*.csv`, `profil_clients_verite.csv` | **corrigés** de chaque source | à la fin |

> ⚠️ **Les chiffres sont fictifs.** La boutique, ses clients et leurs noms sont inventés. Ne tirez de ces données aucune conclusion sur le monde réel : elles servent à apprendre une méthode.

Chaque chapitre du cahier est **autonome** : il commence par ses imports et recharge ses données. Les applications sont dimensionnées pour s'exécuter en **quelques secondes** sur un ordinateur ordinaire, sans réseau.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/crm_clients.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, dans RStudio pour R, ou dans un outil de bases de données pour SQL.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **L'encodage.** Les fichiers de caisse de janvier à juin sont en `cp1252` (Windows), les suivants en UTF-8. Si vous lisez un fichier avec le mauvais encodage, vous obtenez une erreur (`UnicodeDecodeError`) ou des caractères étranges (`NÂ°`, `Ã©`) : c'est un exercice du chapitre 1, pas une panne de votre ordinateur.

> ⚠️ **Excel.** Les exercices qui demandent un tableur se font dans Excel ou dans LibreOffice Calc (gratuit), qui lit les mêmes fichiers ; quand un menu ou une fonction diffère, la documentation de votre version fait foi.

## Vérifier son installation

Quatre courts blocs vérifient que les bibliothèques sont installées et que les données se chargent, en Python, en SQL puis en R.

**1. Les bibliothèques Python** (le volume utilise en plus celles du volume I) :

```python
import sys
from importlib import import_module
from importlib.metadata import version
print("python", sys.version.split()[0])
for p in ["numpy", "pandas", "openpyxl", "rapidfuzz", "jellyfish", "unidecode", "ftfy", "pandera"]:
    import_module(p)                              # échoue si la bibliothèque est absente
    print(f"{p:12s}", version(p))
```
<!--sortie-->
```text
python 3.13.3
numpy        2.5.3
pandas       3.0.6
openpyxl     3.1.5
rapidfuzz    3.14.6
jellyfish    1.2.1
unidecode    1.4.0
ftfy         6.3.1
pandera      0.34.1
```

**2. Les données.** Nous chargeons le CRM (tout en texte, pour ne rien déformer) et comptons les fichiers de caisse :

```python
import glob
import pandas as pd

crm = pd.read_csv("donnees/crm_clients.csv", dtype=str)
print("CRM :", len(crm), "lignes,", crm.shape[1], "colonnes")
print("fichiers de caisse :", len(glob.glob("donnees/caisse/caisse_2025-*.csv")))
```
<!--sortie-->
```text
CRM : 7140 lignes, 11 colonnes
fichiers de caisse : 12
```

**3. Une requête SQL.** Nous copions le CRM dans une base SQLite en mémoire, puis interrogeons-la :

```python
import sqlite3
con = sqlite3.connect(":memory:")
crm.to_sql("crm", con, index=False)
```

```sql
SELECT source_saisie, COUNT(*) AS lignes
FROM crm
GROUP BY source_saisie
ORDER BY lignes DESC;
```
<!--sortie-->
```text
source_saisie  lignes
       caisse    3507
         site    2965
       import     668
```

**4. Le même comptage en R**, pour vérifier que R et le tidyverse sont là :

```r
suppressPackageStartupMessages({library(readr); library(dplyr)})
crm <- read_csv(file.path(Sys.getenv("DONNEES"), "crm_clients.csv"), col_types = cols(.default = col_character()))
print(count(crm, source_saisie, sort = TRUE))
```
<!--sortie-->
```text
# A tibble: 3 × 2
  source_saisie     n
  <chr>         <int>
1 caisse         3507
2 site           2965
3 import          668
```

Vous devez lire une version pour chaque bibliothèque, **7 140 lignes** de CRM pour **11 colonnes**, **12 fichiers de caisse**, et **le même tableau** par source de saisie en SQL et en R. Si tout concorde, votre installation est prête.

## Mini-diagnostic de départ

Huit questions pour vérifier que les réflexes de base de la préparation des données sont en place. Répondez par écrit, puis comparez avec les corrigés plus bas ; chaque corrigé indique le chapitre à lire en cas d'hésitation. Il n'y a pas de note : l'objectif est de savoir **où revenir** avant de commencer.

1. Voici un extrait de six lignes d'un fichier clients (tout est inventé). Listez **tous** les problèmes de qualité que vous y voyez.

```python hide-code
import pandas as pd
pd.set_option("display.width", 200)
extrait = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "prenom": ["Mirela", "MIRELA", "Tavin", "Tavin", "Test", "Solena"],
    "nom": ["Dorvane", "DORVANE", "Kelmar", "Kelmar", "TEST", "Barvert"],
    "email": ["mirela.dorvane@exemple.org", "MIRELA.DORVANE@EXEMPLE.ORG", "tavin.kelmar@courrier.test", None, "test@example.com", "solena.barvert@mail.example"],
    "ville": ["Ville A", "ville a", "Ville B", "Vile B", "Ville A", "المدينة ج"],
    "code_postal": ["01234", "1234", "05100", None, "01000", "12345"],
    "naissance": ["12/03/1985", "1985-03-12", "31/02/1990", "03/04/1990", "01/01/2000", "5 mai 1971"],
})
print(extrait.to_string(index=False))
```
<!--sortie-->
```text
 id prenom     nom                       email     ville code_postal  naissance
  1 Mirela Dorvane  mirela.dorvane@exemple.org   Ville A       01234 12/03/1985
  2 MIRELA DORVANE  MIRELA.DORVANE@EXEMPLE.ORG   ville a        1234 1985-03-12
  3  Tavin  Kelmar  tavin.kelmar@courrier.test   Ville B       05100 31/02/1990
  4  Tavin  Kelmar                         NaN    Vile B         NaN 03/04/1990
  5   Test    TEST            test@example.com   Ville A       01000 01/01/2000
  6 Solena Barvert solena.barvert@mail.example المدينة ج       12345 5 mai 1971
```

2. Dans `profil_clients.csv`, la colonne `depense_2025` contient des valeurs manquantes. Combien y en a-t-il, combien de clients ont une dépense égale à **zéro**, et que peut-on déduire de la colonne `nb_commandes_2025` pour les manquants ?
3. Dans le CRM, combien de lignes sont **exactement** identiques (toutes colonnes sauf `id_crm`), parmi les lignes qui ne sont pas des lignes de test ? Si vous normalisez l'adresse e-mail (espaces, majuscules), combien de lignes partagent leur adresse avec une autre ?
4. On joint les 120 produits de la boutique au catalogue du fournisseur en comparant le nom en minuscules. Combien de lignes attendez-vous ? Combien obtenez-vous, et pourquoi ?
5. Un fichier contient la date `03/04/2025`. S'agit-il du 3 avril ou du 4 mars ? Comment trancher, et que montrent les dates de naissance du CRM écrites `xx/xx/aaaa` ?
6. Dans `montants_saisis.csv`, combien de lignes ont un montant qui diffère de « quantité × prix unitaire » ? Que faut-il savoir avant de les déclarer fausses ?
7. Le fichier `caisse/caisse_2025-01.csv` provoque une `UnicodeDecodeError` quand on le lit avec les réglages par défaut de Python (UTF-8). Que se passe-t-il, et comment lire correctement le fichier de janvier puis celui de juillet ?
8. Dans l'export du site, le total d'une commande vaut en médiane 82,93 avant le 15 septembre et 7 808 après. Que s'est-il passé et comment le vérifier ?

## Corrigés du mini-diagnostic

**1.** Les problèmes visibles : (a) les lignes 1 et 2 sont la **même personne** (casse du nom et de l'adresse, ville « ville a », code postal amputé de son zéro, date écrite dans deux formats), donc un **doublon flou** ; (b) les lignes 3 et 4 sont probablement la même personne aussi (même nom, même ville à une faute près), avec une **adresse manquante**, un **code postal manquant** et deux dates **différentes** ; (c) la date `31/02/1990` est **impossible** ; (d) `03/04/1990` est **ambiguë** (3 avril ou 4 mars ?) ; (e) la ligne 5 est une **ligne de test** à retirer ; (f) la ligne 6 écrit la ville en **arabe** et la date en **texte** (« 5 mai 1971 »), deux formats à unifier ; (g) la ville « Vile B » est une **faute de frappe**. Aucune de ces corrections n'est difficile ; la difficulté est de les **repérer toutes** et de **décider** sans les propager aux autres lignes. À relire : sections 1.3 et 1.4.

```python
dates = pd.to_datetime(pd.Series(["31/02/1990", "03/04/1990", "12/03/1985"]), format="%d/%m/%Y", errors="coerce")
print(dates.dt.strftime("%Y-%m-%d").fillna("impossible").tolist())
```
<!--sortie-->
```text
['impossible', '1990-04-03', '1985-03-12']
```

**2.** Les valeurs manquantes se comptent avec `isna`, les vrais zéros avec une comparaison :

```python
prof = pd.read_csv("donnees/profil_clients.csv")
manque = prof["depense_2025"].isna()
print("manquants :", int(manque.sum()), "| zéros :", int((prof["depense_2025"] == 0).sum()))
print("manquants avec 0 commande :", int((manque & (prof["nb_commandes_2025"] == 0)).sum()), "| avec au moins 1 commande :", int((manque & (prof["nb_commandes_2025"] > 0)).sum()))
print("clients à dépense nulle ayant commandé :", int(((prof["depense_2025"] == 0) & (prof["nb_commandes_2025"] > 0)).sum()))
```
<!--sortie-->
```text
manquants : 297 | zéros : 2024
manquants avec 0 commande : 101 | avec au moins 1 commande : 196
clients à dépense nulle ayant commandé : 0
```

Il y a **297 manquants** et **2 024 zéros**. Un manquant n'est pas un zéro : le zéro est une **information** (« n'a rien dépensé »), le manquant est une **absence** d'information. La colonne `nb_commandes_2025` permet de **reconstituer** une partie des manquants : 101 des 297 clients n'ont passé aucune commande, leur dépense est donc **forcément nulle** ; pour les 196 autres (au moins une commande), elle est strictement positive mais **inconnue**. Aucun client qui a commandé n'a une dépense nulle : une dépense de zéro avec des commandes serait une incohérence. À relire : section 1.1.

**3.** Parmi les lignes réelles, il n'y a **aucune** ligne exactement identique : une recherche de doublons exacts ne trouve rien, alors que le fichier en contient bel et bien. Avec une adresse normalisée, c'est différent :

```python
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str)
reel = crm[crm["nom"] != "TEST"]
print("lignes identiques (hors id_crm, lignes de test exclues) :", int(reel.drop(columns="id_crm").duplicated().sum()))
mail = reel["email"].str.strip().str.lower().dropna()
partage = mail.value_counts()
print("adresses partagées par plusieurs lignes :", int((partage > 1).sum()), "| lignes concernées :", int(partage[partage > 1].sum()))
```
<!--sortie-->
```text
lignes identiques (hors id_crm, lignes de test exclues) : 0
adresses partagées par plusieurs lignes : 656 | lignes concernées : 1333
```

Après normalisation, **656 adresses** sont partagées par **1 333 lignes**. Le doublon exact ne trouve rien parce que les doublons sont **flous** (casse, accents, fautes) : il faut **normaliser** avant de comparer, puis comparer des textes qui se ressemblent (chapitre 2, section 2.5). Et l'adresse seule ne suffit pas : certaines lignes en double n'ont pas d'adresse. À relire : section 1.3.

**4.** On attend **120 lignes** (une par produit, en joignant « un à un »). On en obtient davantage :

```python
produits = pd.read_csv("donnees/produits.csv")
cat = pd.read_csv("donnees/catalogue_fournisseur.csv")
produits["cle"] = produits["nom_produit"].str.lower()
cat["cle"] = cat["designation"].str.strip().str.lower()
j = produits.merge(cat, on="cle", how="left")
print(len(produits), "produits ->", len(j), "lignes après jointure |", int(j["code_fournisseur"].isna().sum()), "produits sans correspondance")
```
<!--sortie-->
```text
120 produits -> 160 lignes après jointure | 12 produits sans correspondance
```

On obtient **160 lignes** : la jointure **multiplie** les lignes parce que le **nom n'est pas une clé**. La boutique compte 120 produits mais seulement 60 noms distincts (chaque nom est porté par deux produits à prix différents) : un nom qui apparaît deux fois à gauche et deux fois à droite produit quatre lignes. Douze produits restent sans correspondance (absents du catalogue, ou désignation trop réécrite). La parade : vérifier l'unicité de la clé **avant** de joindre, ajouter un second critère (le prix), ou rapprocher autrement. À relire : sections 2.2 et 2.5.

**5.** Rien dans `03/04/2025` ne permet de trancher : c'est le **3 avril** en ordre jour-mois, le **4 mars** en ordre mois-jour. On tranche en regardant les **autres valeurs de la même colonne** : si l'on trouve `25/04/2025`, le premier nombre est un jour ; si l'on trouve `04/25/2025`, c'est un mois. À défaut, on demande à la source, ou on lit la documentation du logiciel. Dans le CRM :

```python
x = crm.loc[crm["date_naissance"].str.fullmatch(r"\d{2}/\d{2}/\d{4}"), "date_naissance"]
a, b = x.str[:2].astype(int), x.str[3:5].astype(int)
print("dates xx/xx/aaaa :", len(x), "| premier nombre > 12 (jour sûr) :", int((a > 12).sum()), "| second nombre > 12 (mois en premier) :", int((b > 12).sum()), "| ambiguës :", int(((a <= 12) & (b <= 12)).sum()))
```
<!--sortie-->
```text
dates xx/xx/aaaa : 4674 | premier nombre > 12 (jour sûr) : 2083 | second nombre > 12 (mois en premier) : 634 | ambiguës : 1969
```

La colonne mélange **les deux ordres** : 2 083 dates ont un premier nombre supérieur à 12 (ordre jour-mois), 634 ont un second nombre supérieur à 12 (ordre mois-jour), et **1 969 sont ambiguës**. On n'applique donc pas un seul format à toute la colonne ; on se sert de la source de saisie, et l'on accepte de laisser certaines dates **non résolues** plutôt que de les inventer. À relire : section 1.4.

**6.** On compare le montant à la quantité multipliée par le prix :

```python
m = pd.read_csv("donnees/montants_saisis.csv")
l = pd.read_csv("donnees/lignes_commande.csv", usecols=["id_ligne", "remise_pct"]).set_index("id_ligne")
m["remise"] = m["id_ligne"].map(l["remise_pct"])
sans = (m["montant"] - m["quantite"] * m["prix_unitaire"]).abs() >= 0.01
avec = (m["montant"] - (m["quantite"] * m["prix_unitaire"] * (1 - m["remise"] / 100)).round(2)).abs() >= 0.01
print("écarts sans tenir compte de la remise :", int(sans.sum()), "| en tenant compte de la remise :", int(avec.sum()))
print("lignes remisées :", int((m["remise"] > 0).sum()), "| valeurs 9999 :", int((m["montant"] == 9999).sum()), "| négatives :", int((m["montant"] < 0).sum()), "| nulles :", int((m["montant"] == 0).sum()))
```
<!--sortie-->
```text
écarts sans tenir compte de la remise : 1103 | en tenant compte de la remise : 85
lignes remisées : 1030 | valeurs 9999 : 9 | négatives : 22 | nulles : 10
```

Sans précaution, **1 103** lignes diffèrent ; mais **1 030** lignes ont une remise, qui explique la plupart des écarts. En tenant compte de la remise, il n'en reste que **85**, qui sont les vraies anomalies (décimale décalée, signe inversé, zéro, valeur 9999). Avant de déclarer une valeur fausse, il faut donc connaître la **règle** qui relie les colonnes. On recoupe **à l'intérieur** du fichier. À relire : section 1.2.

**7.** Python lit par défaut en UTF-8, or le fichier de janvier est encodé en `cp1252` : un octet comme `é` n'y a pas la même forme et la lecture échoue. En forçant `cp1252`, on lit correctement. Le fichier de juillet est en UTF-8 avec **marque BOM** : lu avec le mauvais encodage, il donne des symboles étranges au début de la première ligne ; lu en `utf-8-sig`, il est propre.

```python
brut = open("donnees/caisse/caisse_2025-01.csv", "rb").read()
try:
    brut.decode("utf-8")
except UnicodeDecodeError as e:
    print(type(e).__name__, "-", str(e)[:48])
print(repr(brut.decode("cp1252").splitlines()[3][:30]))
juillet = open("donnees/caisse/caisse_2025-07.csv", "rb").read()
print(repr(juillet.decode("cp1252").splitlines()[0][:34]), "|", repr(juillet.decode("utf-8-sig").splitlines()[0][:34]))
```
<!--sortie-->
```text
UnicodeDecodeError - 'utf-8' codec can't decode byte 0xe9 in position
'N° ticket;Date;Heure;Article;C'
'ï»¿Export caisse - Boutique;;;;;;;' | 'Export caisse - Boutique;;;;;;;'
```

La règle : **ne jamais deviner**. On essaie UTF-8, on regarde le résultat, et l'on traite chaque fichier selon son encodage (section 1.5). Un bon réflexe est de **noter l'encodage** de chaque source dans la documentation (chapitre 4). À relire : sections 1.4 et 1.5.

**8.** À partir du 15 septembre, la plateforme exprime le total **en centimes** (une commande de 78 € est écrite `7800`). La médiane est multipliée par près de cent. On le vérifie en regardant la **distribution par période** et en la comparant à une source indépendante :

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str)
site["montant"] = site["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", ".").astype(float)
site["date"] = pd.to_datetime(site["created_at"].str.replace("T", " ").str.replace("Z", ""))
print("médiane avant le 15 septembre :", float(site.loc[site["date"] < "2025-09-15", "montant"].median()), "| après :", float(site.loc[site["date"] >= "2025-09-15", "montant"].median()))
```
<!--sortie-->
```text
médiane avant le 15 septembre : 82.93 | après : 7808.0
```

Le contrôle qui l'aurait révélé : **comparer un total à un ordre de grandeur connu** (le chiffre d'affaires d'un mois ne peut pas être cent fois celui du précédent), ou au total d'une autre source (la base de commandes). La correction (diviser par 100 après la date de bascule) est une **décision** à noter dans le journal. À relire : sections 1.4 et 3.2.

> ✅ **À retenir.** Si vous avez repéré la plupart des défauts des questions 1 à 3, votre œil de nettoyeur est en place ; les questions 4 à 6 testent des réflexes de **vérification** (unicité d'une clé, ambiguïté d'un format, règle interne qui relie les colonnes) ; les questions 7 et 8 testent la **méthode** (ne jamais deviner un encodage, contrôler un ordre de grandeur). Le chapitre 1 détaille les cinq premiers, les chapitres 2 et 3 les trois autres.
