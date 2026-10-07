```python hide
import os, io, re, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

## 1.4 Incohérences et erreurs de format

Dernière famille de défauts, et la plus variée : tout ce qui est *écrit* correctement… dans un autre format que celui que l'on attendait. Un nombre qui contient un symbole monétaire, une unité qui change sans prévenir, une date que l'on peut lire de deux façons, une ville écrite de six manières, un logiciel qui modifie le format de ses exports d'un mois à l'autre. Ces défauts ne se voient pas dans un tableau de comptes ; il faut aller **regarder les valeurs**.

### 1.4.1 Les types : lire d'abord en texte, convertir explicitement

Un fichier CSV ne contient que du texte : c'est le logiciel de lecture qui **devine** les types. Cette devinette est la première source de surprises. L'export du site, par exemple, écrit le total des commandes de trois façons différentes. Lisons-le **sans rien deviner** (`dtype=str`), puis demandons à pandas ce qu'il sait convertir directement.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
direct = pd.to_numeric(site["total"], errors="coerce")
print("montants convertis directement :", int(direct.notna().sum()), "sur", len(site))
print("exemples de montants qui résistent :", site.loc[direct.isna(), "total"].head(4).tolist())
```
<!--sortie-->
```text
montants convertis directement : 4004 sur 6259
exemples de montants qui résistent : ['34,92 €', '63,66 €', '195,40 €', '81,07 €']
```

Seuls 4 004 totaux sur 6 259 se convertissent tels quels : les autres portent un symbole « € », une virgule décimale ou un espace de milliers (« 1 245,00 »). Ils ne sont pas faux, ils sont **écrits pour des humains**. On écrit une petite fonction de conversion, et l'on **vérifie** qu'aucune valeur ne lui échappe.

```python
def nombre(texte):
    """« 1 245,00 € » -> 1245.0 ; « 45.9 » -> 45.9"""
    return float(texte.replace("€", "").replace(" ", "").replace(",", ".").strip())
site["total_n"] = site["total"].map(nombre)
print(site["total_n"].describe().round(1).to_string())
```
<!--sortie-->
```text
count     6259.0
mean      3996.3
std       6926.6
min          1.0
25%         68.9
50%        170.6
75%       5954.0
max      62883.0
```

Aucune erreur de conversion, mais **ce résumé est suspect** : une commande médiane de 171 € tandis que le troisième quartile vaut 5 954 € et le maximum 62 883 € ? La boutique ne vend pas de commandes à 66 000 €. La conversion a réussi sur le plan technique ; il reste un défaut d'**unité**, que la section suivante traque.

> ⚠️ **Piège.** Deux erreurs de type sont particulièrement coûteuses. **Les identifiants lus comme des nombres** : le code postal `01601` devient `1601.0` (le zéro de tête disparaît, et la colonne passe en nombre décimal si elle contient des trous). **Les dates lues comme du texte** : le tri alphabétique range « 10/02/2025 » avant « 2/03/2025 ». Les identifiants se lisent en **texte**, les dates se **convertissent explicitement avec un format**.

```python
crm_defaut = pd.read_csv(os.path.join(D, "crm_clients.csv"))
zero = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)["code_postal"].str.startswith("0", na=False)
print("type deviné :", crm_defaut["code_postal"].dtype, "| codes commençant par 0 lus ainsi :", crm_defaut.loc[zero, "code_postal"].head(3).tolist())
```
<!--sortie-->
```text
type deviné : float64 | codes commençant par 0 lus ainsi : [5723.0, 9321.0, 5723.0]
```

### 1.4.2 Les unités mélangées : le changement de septembre

Revenons à la médiane suspecte. Une unité qui change **au milieu** d'un fichier se détecte en regardant le chiffre **dans le temps**. Calculons, mois par mois, le montant médian d'une commande du site.

```python
site["dt"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="mixed")
site["mois"] = site["dt"].dt.strftime("%Y-%m")
print(site.groupby("mois")["total_n"].median().round(0).rename_axis(None).to_string())
```
<!--sortie-->
```text
2025-01      74.0
2025-02      82.0
2025-03      84.0
2025-04      77.0
2025-05      80.0
2025-06      86.0
2025-07      90.0
2025-08      86.0
2025-09    1641.0
2025-10    8396.0
2025-11    7087.0
2025-12    7808.0
```

De janvier à août, la commande médiane vaut entre 74 € et 90 €. En septembre elle bondit à 1 641 €, puis oscille autour de 7 000 à 8 400 € jusqu'en décembre : un facteur de **près de cent**. Septembre est un mois « de transition », avec une médiane intermédiaire : cela signale un changement **en cours de mois**. On cherche le jour exact.

```python
quotidien = site.set_index("dt")["total_n"].resample("D").median()
for jour, valeur in quotidien["2025-09-12":"2025-09-17"].items():
    print(jour.date(), round(valeur))
```
<!--sortie-->
```text
2025-09-12 97
2025-09-13 79
2025-09-14 49
2025-09-15 11676
2025-09-16 6979
2025-09-17 4419
```

La rupture est nette : **le 15 septembre**, le montant d'une commande est multiplié par cent environ. La plateforme a commencé à exporter les totaux **en centimes**, sans que personne l'annonce. Cette erreur est la plus dangereuse de toutes : aucune valeur n'est invalide, aucun contrôle de plage simple ne sonne, et la somme annuelle du site (plus de 25 millions) est fausse d'un facteur quarante.

![Montant médian d'une commande du site, par mois, avant et après correction de l'unité (échelle logarithmique).](figures/ch01-unite.png)

Pour corriger, on applique la division par cent **à partir de la date de rupture**, puis on vérifie. La correction est justifiée par trois indices : la rupture est datée, son rapport est de cent, et elle touche **toutes** les lignes après le 15 septembre.

```python
site["total_corrige"] = np.where(site["dt"] >= "2025-09-15", site["total_n"] / 100, site["total_n"])
verite_site = pd.read_csv(os.path.join(D, "verite_site.csv")).drop_duplicates("order_ref")
verifie = site.merge(verite_site[verite_site["defaut"] != "test"], on="order_ref")
print("lignes comparées à la vérité :", len(verifie), "| écart maximal :", round((verifie["total_corrige"] - verifie["total_vrai"]).abs().max(), 2), "€")
```
<!--sortie-->
```text
lignes comparées à la vérité : 6199 | écart maximal : 0.0 €
```

Sur les 6 199 commandes comparables, l'écart maximal est de **0,00 €** : la correction retrouve exactement les montants d'origine. Reprenons maintenant le chiffre d'affaires du site, en appliquant dans l'ordre les corrections vues depuis 1.3 : doublons, tests, annulées, unité.

```python
propre = site.drop_duplicates("order_ref")
propre = propre[~propre["customer_email"].str.strip().str.lower().eq("test@example.com") & (propre["status"].str.lower() != "cancelled")]
vraie = verite_site[verite_site["defaut"].isna()]
print("chiffre d'affaires propre :", f"{propre['total_corrige'].sum():,.2f}".replace(",", " "), "€ sur", len(propre), "commandes | vérité :", f"{vraie['total_vrai'].sum():,.2f}".replace(",", " "), "€ sur", len(vraie))
```
<!--sortie-->
```text
chiffre d'affaires propre : 600 164.13 € sur 5897 commandes | vérité : 600 164.13 € sur 5897
```

Après les quatre corrections, le chiffre d'affaires du site est de **600 164,13 € sur 5 897 commandes**, **identique** à la vérité, alors que la somme brute valait plus de 25 millions : un facteur quarante.

```python hide
C.fig_unite(site.assign(total_brut=site["total_n"]), "figures/ch01-unite.png")
```

> ✅ **À retenir.** Pour détecter un changement d'unité ou de format : (1) **regardez la distribution dans le temps** (médiane par mois ou par jour) ; (2) cherchez une **rupture datée** et un **rapport simple** (100, 1 000, 1,2 pour une TVA) ; (3) corrigez **à partir de la date**, jamais « là où la valeur est grande » ; (4) **vérifiez** par une source indépendante. Et prévenez l'équipe qui exploite la plateforme : l'erreur se reproduira.

### 1.4.3 Les dates ambiguës : jour/mois ou mois/jour ?

Les dates sont le champ de mines des formats. Dans le CRM, les dates de naissance sont écrites sous trois formes : `1960-05-02` (année-mois-jour, sans ambiguïté), `2 mai 1960` (en toutes lettres, sans ambiguïté non plus) et `05/02/1960`, qui est **ambiguë** : le 5 février, ou le 2 mai ? Voyons ce que l'on peut déduire des valeurs elles-mêmes.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
crm["id_crm"] = crm["id_crm"].astype(int)
crm = crm.merge(pd.read_csv(os.path.join(D, "verite_crm.csv")), on="id_crm")
crm = crm[crm["id_client"] > 0].copy()                      # on met de côté les 140 lignes de test
slash = crm["date_naissance"].str.fullmatch(r"\d\d/\d\d/\d{4}")
champ1, champ2 = (pd.to_numeric(crm.loc[slash, "date_naissance"].str[a:b]) for a, b in ((0, 2), (3, 5)))
print("dates avec des « / » :", int(slash.sum()), "sur", len(crm))
print("jour/mois certain (1er champ > 12) :", int((champ1 > 12).sum()), "| mois/jour certain (2e champ > 12) :", int((champ2 > 12).sum()), "| ambiguës :", int(((champ1 <= 12) & (champ2 <= 12)).sum()))
```
<!--sortie-->
```text
dates avec des « / » : 4534 sur 7000
jour/mois certain (1er champ > 12) : 2083 | mois/jour certain (2e champ > 12) : 634 | ambiguës : 1829
```

Sur 4 534 dates avec des « / », 2 083 sont **certainement** écrites jour/mois (le premier nombre dépasse 12), 634 **certainement** mois/jour (le deuxième dépasse 12), et **1 829 sont ambiguës**. Une partie de la saisie du CRM a donc été faite à l'américaine, et rien dans le fichier ne l'annonce. Peut-on s'aider d'une autre colonne ? Regardons si la source de saisie (caisse, site, import) explique le format, **en utilisant la vérité** pour savoir quelles lignes sont vraiment américaines.

```python
americaine = crm["defauts"].fillna("").str.contains("americain")
print((americaine.groupby(crm["source_saisie"]).mean() * 100).round(1).to_string())
ambigues_fausses = americaine[slash] & (champ1 <= 12) & (champ2 <= 12) & (champ1 != champ2)
print("dates américaines lues à tort en jour/mois, sans erreur visible :", int(ambigues_fausses.sum()), "sur", len(crm), "lignes")
```
<!--sortie-->
```text
source_saisie
caisse    14.8
import    15.9
site      15.0
dates américaines lues à tort en jour/mois, sans erreur visible : 398 sur 7000 lignes
```

La part de dates à l'américaine est la même (environ 15 %) quelle que soit la source : **aucune colonne ne permet de trancher**. Si l'on suppose partout « jour/mois », les dates américaines dont le deuxième nombre dépasse 12 deviennent impossibles (« 05/27/1970 » donne un mois 27) et se détectent ; en revanche, celles dont les deux nombres sont inférieurs ou égaux à 12 se lisent **sans erreur… mais fausses**. On en compte **398**, soit 5,7 % des 7 000 lignes : près d'une date de naissance sur dix-huit est fausse, sans le moindre message d'erreur.

> 💡 **Intuition.** Une date ambiguë n'est pas un défaut de la donnée, c'est un défaut de **l'information** : le format n'a pas été transmis. Il se règle à la source (demander au service qui a saisi, imposer le format ISO `AAAA-MM-JJ` dans les exports), pas par un algorithme. L'algorithme ne peut que **mesurer** le risque : combien de lignes sont indécidables ?

Un choix défendable consiste à lire en jour/mois (hypothèse majoritaire : plus des trois quarts des dates certaines le sont), à **basculer** en mois/jour quand le jour est impossible, et à **signaler** le risque pour les dates ambiguës.

```python
def lire_naissance(s):
    if re.fullmatch(r"\d\d/\d\d/\d{4}", s) and int(s[3:5]) > 12:       # 2e champ impossible comme mois : c'est mm/jj
        return C.date_mixte(s, americain=True)
    return C.date_mixte(s)                                             # sinon jj/mm (pari, risqué si ambiguë)
crm["naissance"] = crm["date_naissance"].map(lire_naissance)
print("dates illisibles (NaT) :", int(crm["naissance"].isna().sum()), "| lues :", int(crm["naissance"].notna().sum()))
```
<!--sortie-->
```text
dates illisibles (NaT) : 44 | lues : 6956
```

Il reste 44 dates **illisibles** (le 31 février, le « 00/00/0000 », le mois 13) : elles ne se corrigent pas, elles se **signalent**. Ce sont des vraies erreurs de saisie, que la section 1.4.5 traitera par des règles de cohérence.

> ⚠️ **Piège.** Une lecture « qui marche » n'est pas une lecture juste. `pd.to_datetime("05/02/1960")` lit par défaut en mois/jour ; `dayfirst=True` lit en jour/mois ; dans les deux cas, **aucune erreur n'est levée**. Écrivez toujours le **format attendu** (`format="%d/%m/%Y"`) : il échoue bruyamment sur ce qu'il ne comprend pas, c'est précisément ce que l'on souhaite.

### 1.4.4 Les catégories écrites de six façons

Une colonne catégorielle (la ville, le canal, le consentement) ne devrait contenir qu'une poignée de valeurs. Les saisies libres en produisent des dizaines. Combien d'écritures distinctes du nom de la ville dans le CRM ?

```python
print("écritures distinctes de la ville :", crm["ville"].nunique())
print(crm["ville"].value_counts().head(6).to_string())
```
<!--sortie-->
```text
écritures distinctes de la ville : 119
ville
Ville A    618
Ville B    507
Ville C    440
Ville D    391
Ville E    331
Ville F    261
```

On compte 119 écritures pour 20 villes. Les plus fréquentes sont propres ; la longue traîne contient des **majuscules** (« VILLE A »), des **minuscules** (« ville a »), des **fautes** (« Vile A »), un **point final** (« Ville A. ») et, pour environ 2,7 % des lignes, l'**arabe** (« المدينة أ » : « la ville A »). Regardons les écritures de la ville A.

```python
print(sorted(crm.loc[crm["ville"].str.strip().str.lower().str.rstrip(".").isin(["ville a", "vile a"]) | crm["ville"].str.endswith("أ"), "ville"].unique()))
```
<!--sortie-->
```text
['VILLE A', 'Vile A', 'Ville A', 'Ville A.', 'ville a', 'المدينة أ']
```

Six écritures pour une seule ville. La méthode est toujours la même : une **fonction de normalisation** (retirer les espaces et le point, mettre la casse, corriger la faute connue, traduire l'arabe) et, surtout, une **table de correspondance** conservée avec le traitement, pour que l'on sache d'où vient chaque valeur.

```python
def ville_propre(s):
    s = s.strip()
    if s.startswith("المدينة"):                                  # arabe : « المدينة أ » = « la ville A »
        return "Ville " + chr(65 + C.AR.index(s.split()[-1]))
    return C.normaliser_ville(s)
crm["ville_propre"] = crm["ville"].map(ville_propre)
correspondance = crm.groupby(["ville_propre", "ville"]).size().rename("lignes").reset_index()
print("écritures distinctes après nettoyage :", crm["ville_propre"].nunique(), "| lignes dans la table de correspondance :", len(correspondance))
```
<!--sortie-->
```text
écritures distinctes après nettoyage : 20 | lignes dans la table de correspondance : 119
```

On passe de 119 à 20 valeurs, avec une table de 119 lignes qui documente chaque substitution. Reste à **vérifier** : la ville nettoyée est-elle la vraie ville du client ?

```python
vraie_ville = crm.merge(pd.read_csv(os.path.join(D, "clients.csv"))[["id_client", "ville"]].rename(columns={"ville": "ville_vraie"}), on="id_client")
print("villes nettoyées identiques à la vérité :", round((vraie_ville["ville_propre"] == vraie_ville["ville_vraie"]).mean() * 100, 1), "% de", len(vraie_ville), "lignes")
```
<!--sortie-->
```text
villes nettoyées identiques à la vérité : 100.0 % de 7000 lignes
```

Le consentement marketing est un autre exemple, plus délicat : sept écritures (`oui`, `Oui`, `OUI`, `O`, `1`, `TRUE`, vide).

```python
consentement = {"oui": True, "o": True, "1": True, "true": True, "non": False}
crm["consentement_propre"] = crm["consentement_marketing"].str.strip().str.lower().map(consentement)
print(crm["consentement_propre"].value_counts(dropna=False).to_string())
```
<!--sortie-->
```text
consentement_propre
True    4839
NaN     2161
```

Parmi les 7 000 lignes, 4 839 expriment un consentement ; **2 161 sont vides**. Le point important : un vide n'est **pas un « non »**. Ce n'est pas non plus un « oui ». C'est l'absence de réponse, qui se traite comme un **manquant**, avec une conséquence concrète : sans consentement explicite, on n'envoie pas de message promotionnel (chapitre 5 sur la confidentialité). La valeur `False` n'apparaît pas dans ces lignes : le seul « non » du fichier d'origine se trouve dans les lignes de test.

### 1.4.5 Les règles de cohérence entre colonnes

Une valeur peut être correcte **seule** et absurde **avec une autre** : une date d'inscription antérieure à la naissance, un code postal de quatre chiffres, une adresse électronique sans arobase. Ces **règles de cohérence** s'écrivent comme de petites expressions logiques ; on compte les lignes en infraction.

```python
ins = pd.to_datetime(crm["date_inscription"], format="%d/%m/%Y")
lisible = crm["naissance"].notna()
regles = {"naissance lisible": lisible,
          "naissance entre 1920 et 2010 (parmi les lisibles)": ~lisible | crm["naissance"].between("1920-01-01", "2010-12-31"),
          "inscription après la naissance": ~lisible | (ins >= crm["naissance"]),
          "code postal de 5 chiffres (quand il est renseigné)": crm["code_postal"].isna() | crm["code_postal"].str.fullmatch(r"\d{5}"),
          "e-mail de forme valide (quand il est renseigné)": crm["email"].isna() | crm["email"].str.fullmatch(r"(?!.*\.\.)[\w.+-]+@[\w-]+\.[\w.]+")}
for nom, ok in regles.items():
    print(f"{nom:52s} {int((~ok).sum()):4d} lignes en infraction")
```
<!--sortie-->
```text
naissance lisible                                      44 lignes en infraction
naissance entre 1920 et 2010 (parmi les lisibles)      24 lignes en infraction
inscription après la naissance                         11 lignes en infraction
code postal de 5 chiffres (quand il est renseigné)    199 lignes en infraction
e-mail de forme valide (quand il est renseigné)        95 lignes en infraction
```

Chaque règle compte ses infractions, et chacune se **vérifie** contre la vérité : les 44 dates illisibles et les 24 dates hors de l'intervalle 1920-2010 font **68 dates impossibles**, exactement le nombre injecté. Les 199 codes postaux de quatre chiffres sont ceux dont le zéro initial a été perdu (on les **répare** en les complétant à gauche : `.str.zfill(5)`), et les 95 adresses invalides viennent de doubles arobases ou de points consécutifs (une expression régulière trop permissive laisse passer ces derniers : on les interdit explicitement avec `(?!.*\.\.)`). Quant aux 11 infractions de la règle « inscription après la naissance », ce sont les dates de naissance fixées en 2030.

```python
cp_repare = crm["code_postal"].str.zfill(5)
print("codes postaux de 5 chiffres après réparation :", int(cp_repare.str.fullmatch(r"\d{5}").sum()), "sur", int(cp_repare.notna().sum()), "renseignés")
```
<!--sortie-->
```text
codes postaux de 5 chiffres après réparation : 6576 sur 6576 renseignés
```

> 🧭 **En pratique.** Écrivez vos règles **dans une table** (nom, formule, nombre d'infractions, décision) et rejouez-la à chaque nouvelle livraison de données. C'est le début d'un contrôle de qualité (chapitre 3). Et distinguez **ce qui se répare** (un zéro perdu), **ce qui se signale** (une date impossible) et **ce qui se demande** : combien de clients ont moins de 18 ans à l'inscription ? La boutique accepte-t-elle les mineurs ? Une règle métier **inventée** vaut moins qu'une question posée à la gérante.

### 1.4.6 Quand le schéma change d'un fichier à l'autre

Le logiciel de caisse envoie un fichier par mois. Il semble identique d'un mois à l'autre ; il ne l'est pas. Regardons l'en-tête et la première ligne de trois mois.

```python
for mois in ("01", "07", "10"):
    brut = open(os.path.join(D, "caisse", f"caisse_2025-{mois}.csv"), "rb").read()
    texte = (brut.decode("cp1252") if mois == "01" else brut.decode("utf-8-sig")).splitlines()
    print(mois, "|", texte[3][:78], "\n   |", texte[4][:78])
```
<!--sortie-->
```text
01 | N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant 
   | T23468;01/01/2025;11:18;Poêle mat;Cuisine;1;40,07;40,07
07 | N° ticket;Date;Heure;Article;Catégorie;Quantité;Prix unitaire;Montant 
   | T29050;01/07/25;10:59;Jardinière design;Jardin;1;51,40;51,40
10 | Ticket,Date,Heure,Article,Catégorie,Qté,Prix unitaire,Remise (%),Montant 
   | "T31901","01/10/2025","10:05","Jardinière design","Jardin","3","51.40","0","15
```

Les trois mois ont **trois formats** : encodage `cp1252` puis UTF-8, séparateur `;` puis `,`, virgule puis point décimal, « Qté » puis « Quantité », date `01/07/25` à deux chiffres pour l'année, une colonne « Remise (%) » ajoutée, des champs entre guillemets. On ne lit pas douze fichiers avec douze scripts : on écrit **une fonction de lecture qui détecte** le format, en trois petites étapes. La première **ouvre** le fichier en essayant UTF-8 puis l'ancien encodage Windows.

```python
def ouvrir(fichier):
    """lignes du fichier, en essayant UTF-8 puis l'ancien encodage Windows"""
    brut = open(fichier, "rb").read()
    try:
        return brut.decode("utf-8-sig").splitlines(), "utf-8"
    except UnicodeDecodeError:
        return brut.decode("cp1252").splitlines(), "cp1252"
```

La deuxième **découpe** : elle saute les lignes de titre, repère l'en-tête, déduit le séparateur, retire les en-têtes répétés à chaque « page » et lit le **total affiché** à la dernière ligne.

```python
est_entete = lambda l: re.match(r'^"?(N° ticket|Ticket)', l) is not None
def decouper(lignes):
    """(en-tête, lignes de données, séparateur, total affiché)"""
    i0 = next(i for i, l in enumerate(lignes) if est_entete(l))
    sep = ";" if lignes[i0].count(";") > lignes[i0].count(",") else ","
    total = float(lignes[-1].split(sep)[-1].strip('"').replace(",", "."))
    return lignes[i0], [l for l in lignes[i0 + 1:-1] if not est_entete(l)], sep, total
```

La troisième **uniformise** les noms de colonnes, convertit les nombres et les dates, et assemble le tout.

```python
RENOMMER = {"N° ticket": "ticket", "Ticket": "ticket", "Qté": "quantite", "Quantité": "quantite", "Date": "date", "Heure": "heure", "Article": "article",
            "Catégorie": "categorie", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}
def lire_caisse(fichier):
    lignes, enc = ouvrir(fichier)
    entete, corps, sep, total = decouper(lignes)
    t = pd.read_csv(io.StringIO("\n".join([entete] + corps)), sep=sep, dtype=str).rename(columns=RENOMMER)
    for c in ("prix_unitaire", "montant"):
        t[c] = pd.to_numeric(t[c].str.replace(",", "."), errors="coerce")
    t["date"] = pd.to_datetime(t["date"], format="%d/%m/%y" if len(t["date"].iloc[0]) == 8 else "%d/%m/%Y")
    t["quantite"], t["id_commande"] = t["quantite"].astype(int), t["ticket"].str[1:].astype(int)
    return t, total, f"{enc}, séparateur « {sep} »"
```

Reste le plus important : **vérifier**. Chaque fichier se termine par un total affiché. Si notre lecture est fidèle, la somme des montants lus doit retrouver ce total, ou bien l'écart doit **s'expliquer**.

```python
fichiers = sorted(glob.glob(os.path.join(D, "caisse", "*.csv")))
for f in fichiers:
    t, total, desc = lire_caisse(f)
    print(f"{os.path.basename(f)[7:14]} {desc:26s} {len(t):5d} lignes {int(t['montant'].isna().sum()):3d} vides  somme {t['montant'].sum():9.2f}  total {total:9.2f}  écart {total - t['montant'].sum():8.2f}")
```
<!--sortie-->
```text
2025-01 cp1252, séparateur « ; »     955 lignes  36 vides  somme  37826.31  total  38882.41  écart  1056.10
2025-02 cp1252, séparateur « ; »     770 lignes  22 vides  somme  32273.46  total  33079.41  écart   805.95
2025-03 cp1252, séparateur « ; »     916 lignes  28 vides  somme  37863.67  total  39038.90  écart  1175.23
2025-04 cp1252, séparateur « ; »    1013 lignes  31 vides  somme  45426.14  total  45832.57  écart   406.43
2025-05 cp1252, séparateur « ; »    1028 lignes  31 vides  somme  43381.31  total  44905.92  écart  1524.61
2025-06 cp1252, séparateur « ; »     973 lignes  30 vides  somme  42277.42  total  43118.16  écart   840.74
2025-07 utf-8, séparateur « ; »      877 lignes  21 vides  somme  41035.68  total  41595.82  écart   560.14
2025-08 utf-8, séparateur « ; »      814 lignes  20 vides  somme  42350.83  total  42873.50  écart   522.67
2025-09 utf-8, séparateur « ; »     1048 lignes  31 vides  somme  45600.67  total  46354.25  écart   753.58
2025-10 utf-8, séparateur « , »     1138 lignes  38 vides  somme  49839.95  total  51321.48  écart  1481.53
2025-11 utf-8, séparateur « , »     1452 lignes  48 vides  somme  59096.64  total  60586.62  écart  1489.98
2025-12 utf-8, séparateur « , »     1694 lignes  63 vides  somme  70924.34  total  73384.87  écart  2460.53
```

La fonction lit les douze fichiers, quel que soit leur format. Chaque mois présente un **écart positif** (le total affiché dépasse la somme lue) et un nombre de montants **vides** : c'est la signature de la perte de montants. Mais les lignes en double, elles, font l'inverse (elles ajoutent des montants que le total n'inclut pas). L'écart est-il donc **entièrement expliqué** ? C'est le moment de reprendre le tableau `rapproche` de la section 1.3.3, qui rapproche chaque ligne de la caisse d'une ligne de la base.

```python
lue = rapproche["montant"].sum()
vides_retrouves = rapproche.loc[rapproche["montant"].isna() & ~en_trop, "montant_base"].sum()
doubles = rapproche.loc[en_trop, "montant"].sum()
affiche = sum(lire_caisse(f)[1] for f in fichiers)
print(f"somme lue {lue:,.2f} − lignes en double {doubles:,.2f} + montants vides retrouvés dans la base {vides_retrouves:,.2f} = {lue - doubles + vides_retrouves:,.2f} €".replace(",", " "))
print("total affiché par la caisse (somme des douze fichiers) :", f"{affiche:,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
somme lue 547 896.42 − lignes en double 3 126.29 + montants vides retrouvés dans la base 16 203.78 = 560 973.91 €
total affiché par la caisse (somme des douze fichiers) : 560 973.91 €
```

L'écart global (13 077,49 €) s'explique **au centime près** : les montants vides en retranchent 16 203,78 €, les lignes en double en ajoutent 3 126,29 €. C'est la forme la plus satisfaisante du contrôle : non pas « ça a l'air bon », mais « l'écart est expliqué, ligne à ligne ».

> ✅ **À retenir.** Une lecture robuste d'un fichier qui évolue suit quatre principes : **détecter** (encodage, séparateur, en-tête) plutôt que supposer ; **tout lire en texte** puis convertir explicitement ; **uniformiser** les noms de colonnes dans une table de correspondance ; **contrôler** chaque fichier à l'aide d'un point fixe (le total affiché) et expliquer les écarts. Et gardez le **fichier d'origine** intact.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.8 et 1.9.
