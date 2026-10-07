## 4.3 ➕ Pour aller plus loin : lignage des données et pistes d'audit

> 🧭 **Section complémentaire.** Elle prolonge la documentation d'un jeu de données et d'un nettoyage par la question que pose tout lecteur d'un rapport : **d'où vient ce chiffre ?** Elle montre comment dessiner la chaîne de dépendances (le **lignage**), prouver qu'un fichier n'a pas changé (les **empreintes**), tenir un **journal d'audit** et **rejouer** un résultat depuis le brut. Rien de ce qui suit n'est nécessaire au reste du volume.

### 4.3.1 D'où vient ce chiffre ?

Le **lignage des données** (*data lineage*) est la carte des dépendances : quelle source alimente quelle table, quelle requête produit quel résultat, quel graphique repose sur quel tableau. On lui pose deux questions, dans les deux sens.

- **En amont** : *d'où vient ce chiffre ?* On remonte du résultat vers ses sources. C'est la question de l'auditeur, de la collègue de la comptabilité, de la gérante qui doute.
- **En aval** : *si ce fichier change, qu'est-ce qui est touché ?* On descend de la source vers ses livrables. C'est la question de l'analyste qui s'apprête à modifier une table et qui veut savoir ce qu'il risque de casser : l'**analyse d'impact**.

Sans lignage, ces deux questions se règlent à la main, en fouillant des dossiers et en interrogeant des collègues : lent, incomplet, et surtout impossible à **vérifier**. Avec un lignage, même simple, elles se règlent en une ligne.

### 4.3.2 Un lignage à la main, au niveau des fichiers

Pas besoin d'un logiciel pour commencer. Un lignage est un **dictionnaire** : pour chaque élément, la liste des éléments dont il dépend. Voici celui de la synthèse du quatrième trimestre (celle du projet du volume I) : quatre tables sources, trois traitements, un tableau de synthèse, un graphique et le message adressé à la gérante.

```python
L = O.Lignage()
for nom in ["commandes", "lignes_commande", "produits", "retours"]:
    L.ajouter(nom, "source")
L.ajouter("ca_par_canal.sql", "requete", ["commandes", "lignes_commande"])
L.ajouter("marge.py", "script", ["lignes_commande", "produits"])
L.ajouter("taux_retour.sql", "requete", ["lignes_commande", "retours", "commandes"])
L.ajouter("synthese_t4.csv", "table", ["ca_par_canal.sql", "marge.py", "taux_retour.sql"])
L.ajouter("graphique_t4.png", "sortie", ["synthese_t4.csv"])
L.ajouter("message_gerante.md", "sortie", ["synthese_t4.csv", "graphique_t4.png"])
print("amont du message :", L.amont("message_gerante.md"))
print("sources du message :", L.sources("message_gerante.md"))
print("si `produits` change :", L.aval("produits"))
```
<!--sortie-->
```text
amont du message : ['ca_par_canal.sql', 'commandes', 'graphique_t4.png', 'lignes_commande', 'marge.py', 'produits', 'retours', 'synthese_t4.csv', 'taux_retour.sql']
sources du message : ['commandes', 'lignes_commande', 'produits', 'retours']
si `produits` change : ['graphique_t4.png', 'marge.py', 'message_gerante.md', 'synthese_t4.csv']
```

La première réponse dit que le message dépend, directement ou non, de **neuf éléments** ; la deuxième, que tout repose sur **quatre sources** ; la troisième, que modifier la table `produits` touche **quatre éléments**, dont le message lui-même. Cette dernière réponse est l'**analyse d'impact** : avant de corriger un prix dans `produits`, on sait déjà quoi relancer et qui prévenir. Le graphe ci-dessous montre la même chose ; les éléments qui ne dépendent pas de `produits` sont grisés.

```python hide
F4.lignage_tables(L, surligne=["produits"] + L.aval("produits"))
```
<!--sortie-->
```text
figure : ch04-lignage-tables.png
```

![Lignage de la synthèse du quatrième trimestre : de gauche à droite, les sources (gris), les traitements SQL (bleu) et Python (violet), le tableau de synthèse (vert), le graphique et le message (orange). Les éléments qui dépendent de la table produits sont en couleur pleine, les autres sont grisés.](figures/ch04-lignage-tables.png)

> 💡 **Intuition.** Le lignage est un **plan de plomberie** : on ne l'ouvre que quand une fuite apparaît ou qu'on veut changer un tuyau. Le moment où il sert est justement celui où l'on n'a pas le temps de le reconstituer : il faut l'avoir dessiné avant.

### 4.3.3 Le lignage des colonnes

Le lignage de fichiers répond à « quel fichier ? ». Pour savoir **quelle colonne** et **quel calcul**, il faut descendre d'un niveau : le **lignage de colonnes**. C'est lui qui répond à une question comme : « le panier moyen de la synthèse change quand on change quoi, exactement ? ».

```python
C = O.Lignage()
for c in ["quantite", "prix_unitaire", "remise_pct", "canal", "date_commande", "id_commande"]:
    C.ajouter(c, "source")
C.ajouter("montant", "table", ["quantite", "prix_unitaire", "remise_pct"])
C.ajouter("ca_t4_canal", "table", ["montant", "canal", "date_commande"])
C.ajouter("nb_commandes_t4", "table", ["id_commande", "canal", "date_commande"])
C.ajouter("panier_moyen", "sortie", ["ca_t4_canal", "nb_commandes_t4"])
print("colonnes sources du panier moyen :", C.sources("panier_moyen"))
print("ce qui dépend de `remise_pct` :", C.aval("remise_pct"))
```
<!--sortie-->
```text
colonnes sources du panier moyen : ['canal', 'date_commande', 'id_commande', 'prix_unitaire', 'quantite', 'remise_pct']
ce qui dépend de `remise_pct` : ['ca_t4_canal', 'montant', 'panier_moyen']
```

Le panier moyen dépend de **six colonnes sources**. Si la plateforme change l'unité de `prix_unitaire` (centimes au lieu d'euros), le graphe montre en un coup d'œil que `montant`, `ca_t4_canal` et `panier_moyen` sont touchés, alors que `nb_commandes_t4` ne l'est pas. C'est exactement le cas du changement d'unité du total dans l'export du site, en septembre (voir les données du volume) : un lignage de colonnes aurait indiqué les calculs à vérifier.

```python hide
F4.lignage_colonnes(C, surligne=["remise_pct"] + C.aval("remise_pct"))
```
<!--sortie-->
```text
figure : ch04-lignage-colonnes.png
```

![Lignage des colonnes du panier moyen : six colonnes sources (gris), trois colonnes calculées (vert), l'indicateur final (orange). En couleur pleine : ce qui dépend de la remise.](figures/ch04-lignage-colonnes.png)

> 🧭 **En pratique.** Le lignage de colonnes d'un grand entrepôt ne se dessine pas à la main : il se **déduit** des requêtes (en lisant les `SELECT`) ou se déclare dans les outils de transformation. À l'échelle d'une analyse, un dictionnaire Python de vingt lignes, tenu à jour dans le dossier du projet, suffit amplement et vaut mieux qu'un outil que personne ne maintient.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6, exercice 4.10.

### 4.3.4 Prouver qu'une entrée n'a pas changé : les empreintes

Le lignage dit **quel fichier** alimente un chiffre. Il ne dit pas si ce fichier est **le même** que celui de l'an dernier. Quelqu'un a pu le remplacer, le corriger, le ré-exporter. Pour le **prouver**, on calcule une **empreinte** : une chaîne de caractères, de longueur fixe, calculée à partir de **tout le contenu** du fichier par une fonction de hachage (ici SHA-256). Propriété essentielle : le même contenu donne **toujours** la même empreinte ; un contenu qui diffère, même d'un seul caractère, en donne une **tout autre**.

```python
for nom in ["commandes.csv", "lignes_commande.csv", "clients.csv"]:
    print(f"{nom:22s} {O.empreinte_fichier(os.path.join(O.donnees(), nom))[:16]}")
copie = os.path.join(TMP4, "commandes_copie.csv")
with open(os.path.join(O.donnees(), "commandes.csv"), encoding="utf-8") as f:
    contenu = f.read().replace("Site", "Sitf", 1)             # un seul caractère modifié, une seule fois
open(copie, "w", encoding="utf-8").write(contenu)
print(f"{'copie modifiée':22s} {O.empreinte_fichier(copie)[:16]}")
```
<!--sortie-->
```text
commandes.csv          284247714df1013f
lignes_commande.csv    3320bc35e48b90f6
clients.csv            7c3ef5cbc42f6e5f
copie modifiée         92fe621230c2173d
```

Un fichier de 36 395 commandes dont **un seul mot** a changé a une empreinte entièrement différente. On garde cette empreinte avec la fiche du fichier : le jour où l'on rejoue l'analyse, on recalcule l'empreinte, et l'on sait **sans rien ouvrir** si l'on part du même fichier.

> ⚠️ **Piège.** Une empreinte prouve que le fichier est **identique**, pas qu'il est **juste**. Deux fichiers faux de la même façon ont la même empreinte. L'empreinte répond à « est-ce bien le fichier que j'ai documenté ? », jamais à « ce fichier est-il correct ? ». La seconde question relève du dictionnaire et des contrôles de qualité (chapitre 3).

### 4.3.5 Le journal d'audit : qui, quand, quoi

Le lignage dit d'où vient un chiffre ; le journal d'audit dit **ce qui s'est passé** : qui a reçu quel fichier, qui l'a transformé, qui l'a validé, à quelle date. C'est un fichier texte dans lequel on **ajoute** une ligne à chaque événement, **jamais** on n'en modifie une. Cette règle (on ajoute, on ne réécrit pas) lui donne sa valeur : un journal que l'on peut retoucher ne prouve plus rien.

```python
audit = os.path.join(TMP4, "audit.jsonl")
O.consigner(audit, "2026-01-05 09:12", "analyste", "réception", "crm_clients_v1.csv", O.empreinte_df(crm))
O.consigner(audit, "2026-01-05 09:40", "analyste", "nettoyage", "crm_propre_v1.csv", O.empreinte_df(propre))
O.consigner(audit, "2026-01-06 14:05", "gérante", "validation", "crm_propre_v1.csv", O.empreinte_df(propre))
print(O.lire_audit(audit).to_string(index=False))
```
<!--sortie-->
```text
           quand      qui     action              objet    empreinte
2026-01-05 09:12 analyste  réception crm_clients_v1.csv 84f642145769
2026-01-05 09:40 analyste  nettoyage  crm_propre_v1.csv e729855c52a1
2026-01-06 14:05  gérante validation  crm_propre_v1.csv e729855c52a1
```

On lit l'histoire d'un coup d'œil : l'analyste a reçu le CRM brut (empreinte `dc49…`), l'a transformé en un fichier propre (empreinte `a4c0…`), et la gérante a **validé exactement ce fichier-là**, puisque son empreinte est la même. Si, le lendemain, quelqu'un modifie le fichier propre, son empreinte changera et la validation ne portera plus sur le fichier en circulation. Cette phrase simple est ce qu'un audit demande.

Quatre règles pour un journal d'audit utile : **ajouter seulement** ; consigner **qui, quand, quoi, sur quel objet, avec quelle empreinte** ; noter **les validations** autant que les modifications ; ne jamais y mettre de données personnelles (on y met des **noms de fichiers** et des empreintes, pas leur contenu).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.7, exercice 4.11.

### 4.3.6 Versionner des données, sans outil lourd

Les outils de gestion de versions (Git) conviennent au code, pas aux gros fichiers de données. À l'échelle d'une analyse, trois pratiques légères suffisent.

1. **Un dossier par livraison**, daté : `entree/2025-12-31/`, `entree/2026-03-31/`. On ne remplace jamais un fichier : on ajoute un dossier.
2. **Un manifeste** : un petit fichier qui liste, pour chaque dossier de livraison, les fichiers et leur empreinte. Il se versionne avec le code.
3. **Une vérification à l'ouverture** : le programme compare les empreintes des fichiers qu'il va lire à celles du manifeste, et s'arrête s'il y a un écart.

```python
manifeste = {nom: O.empreinte_fichier(os.path.join(O.donnees(), nom))[:12] for nom in ["commandes.csv", "lignes_commande.csv"]}
chemin = os.path.join(TMP4, "MANIFESTE_2025-12-31.json")
json.dump(manifeste, open(chemin, "w"), indent=1)
print(open(chemin).read())
```
<!--sortie-->
```text
{
 "commandes.csv": "284247714df1",
 "lignes_commande.csv": "3320bc35e48b"
}
```

Ce petit manifeste est la **carte d'identité d'une livraison**. Il pèse quelques octets, se lit dans n'importe quel éditeur et suffit à répondre à la question « partons-nous des mêmes fichiers ? ». Pour de grosses volumétries ou de nombreux fichiers, des outils spécialisés de versionnement de données existent ; ils reprennent la même idée (une empreinte par fichier, un fichier de description versionné avec le code).

### 4.3.7 Les outils existants (non exécutés)

Tout ce que nous venons de faire à la main, des outils le font à l'échelle d'une entreprise. Nous ne les installons pas ici : voici ce qu'ils apportent, **sans prétendre les avoir exécutés**.

- **Les catalogues de données** rassemblent, pour tous les jeux d'une entreprise, leur fiche, leur dictionnaire, leur propriétaire et leur sensibilité, avec une recherche. Ils remplacent « le classeur partagé que personne ne retrouve ».
- **Les outils de transformation par fichiers SQL** (dbt est le plus connu) déclarent les dépendances entre tables dans les requêtes elles-mêmes, en **déduisent** le graphe de lignage et **publient** un site de documentation. Ils permettent aussi d'écrire les tests (valeurs permises, absence de vide, unicité) à côté de la description de la colonne.
- **Des standards ouverts de lignage** (OpenLineage, par exemple) décrivent comment un outil de traitement signale « j'ai lu ceci, j'ai produit cela », pour que les graphes de plusieurs outils s'assemblent.

À titre d'exemple de ce qu'on y écrit, voici le dictionnaire d'une colonne avec ses tests, dans la syntaxe de l'un de ces outils (non exécuté ; la syntaxe varie selon l'outil et la version, **à vérifier dans sa documentation**).

```yaml noexec
version: 2
models:
  - name: synthese_t4
    description: Synthèse du quatrième trimestre par canal (CA TTC remises déduites)
    columns:
      - name: canal
        description: Canal de vente
        tests:
          - not_null
          - accepted_values: {values: [Boutique, Site, Réseaux]}
```

> 🧭 **En pratique.** Un outil de lignage ne vaut que s'il est **tenu à jour** par ceux qui produisent les données. Avant d'en adopter un, commencez par un dictionnaire Python et un manifeste : s'ils restent à jour chez vous pendant six mois, vous saurez ce que vous attendez d'un outil.

### 4.3.8 Mini-projet : rejouer un chiffre depuis le brut

Réunissons tout. La question de l'introduction était : *comment refaire le chiffre de 211 434 € du Site au quatrième trimestre ?* Si la documentation est bonne, la réponse tient dans un dictionnaire qui dit **quelles sources** (avec leur empreinte), **quels filtres** et **quelle mesure**, et dans une fonction `rejouer` qui exécute cette description.

```python
doc = {
    "question": "CA TTC du canal Site au quatrième trimestre 2025",
    "sources": {"commandes": {"fichier": "commandes.csv", "empreinte": manifeste["commandes.csv"]},
                "lignes_commande": {"fichier": "lignes_commande.csv", "empreinte": manifeste["lignes_commande.csv"]}},
    "filtres": [("canal", "==", "Site"), ("date_commande", ">=", "2025-10-01"), ("date_commande", "<=", "2025-12-31")],
    "mesure": "montant"}
res = O.rejouer(doc)
print(res)
```
<!--sortie-->
```text
{'empreintes_ok': True, 'valeur': 211433.79, 'lignes': 4911}
```

La documentation redonne **211 433,79 €**, calculé sur les 4 911 lignes de commande du canal Site du 1er octobre au 31 décembre, et confirme que les fichiers lus sont ceux de la livraison documentée (`empreintes_ok`). Un collègue qui lit ce dictionnaire sait **quoi** calculer, **sur quoi**, et **comment vérifier** qu'il part des mêmes fichiers. Les quatre chiffres de l'introduction (211 434, 176 195, 214 993, 166 108) se distinguent désormais par une ligne du dictionnaire : le filtre, le taux de taxe, l'étendue des dates.

Reste à voir ce que fait la fonction quand la documentation et la réalité **divergent** : on modifie l'empreinte attendue du fichier des commandes, comme si quelqu'un avait remplacé le fichier.

```python
doc["sources"]["commandes"]["empreinte"] = "000000000000"
print(O.rejouer(doc)["empreintes_ok"])
```
<!--sortie-->
```text
False
```

Le calcul se fait toujours, mais le drapeau passe à `False` : on **sait** que l'on n'est plus sur la livraison documentée. C'est exactement ce qu'on attend d'une documentation vivante : elle ne garantit pas que tout est juste, elle garantit qu'**on saura** quand quelque chose a changé.

> ✅ **À retenir.** Le **lignage** donne la carte des dépendances, dans les deux sens (**amont** : d'où vient ce chiffre ; **aval** : qu'est-ce qui est touché si ceci change), au niveau des fichiers et des colonnes. Les **empreintes** prouvent qu'un fichier n'a pas changé (pas qu'il est juste). Le **journal d'audit** consigne qui, quand, quoi et avec quelle empreinte, en **ajoutant** seulement. Un **manifeste** versionne une livraison. Avec ces quatre outils légers, un chiffre se **rejoue** depuis le brut : celui du Site au quatrième trimestre, 211 433,79 €, se retrouve à partir d'une documentation d'une dizaine de lignes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.6 à 4.8, exercices 4.10 à 4.12.
