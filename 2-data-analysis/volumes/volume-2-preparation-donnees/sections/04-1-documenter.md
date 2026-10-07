## 4.1 Documenter les jeux de données et les transformations

Documenter deux choses distinctes : **ce que l'on a reçu** (un jeu de données, avec son histoire et ses défauts) et **ce que l'on en a fait** (une suite de transformations, chacune avec une règle et une justification). La première se consigne dans une **fiche**, la seconde dans un **journal**. Cette section montre les deux, puis comment les ranger pour que quelqu'un d'autre — ou vous, plus tard — puisse tout rejouer depuis le fichier brut.

```python hide
crm = O.charger("crm_clients", dtype=str)
```

### 4.1.1 Ce que l'on documente : une fiche par jeu de données

Un jeu de données n'est pas seulement un tableau : c'est un tableau **avec une histoire**. Deux fichiers identiques en apparence peuvent ne pas vouloir dire la même chose, selon qui les a produits, quand, et avec quel périmètre. La fiche d'un jeu de données (on dit aussi *datasheet*, ou « carte d'identité ») consigne dix informations.

| Rubrique | Question à laquelle elle répond | Exemple pour le CRM |
|---|---|---|
| **Source** | Qui l'a produit, avec quel outil ? | export du CRM de la boutique |
| **Date d'extraction** | À quelle date l'a-t-on obtenu ? | 31 décembre 2025 |
| **Périmètre** | Qu'est-ce qui est dedans, et qu'est-ce qui n'y est pas ? | clients saisis depuis 2018, doublons compris |
| **Grain** | Qu'est-ce qu'**une ligne** ? | une saisie de fiche, pas un client |
| **Clé** | Qu'est-ce qui identifie une ligne ? | `id_crm`, numéro de saisie |
| **Contenu** | Combien de lignes, de colonnes, quelle empreinte ? | mesurés par le code |
| **Limites connues** | Quels défauts a-t-on déjà repérés ? | doublons, formats mixtes, lignes de test |
| **Version** | Quelle version, quel nom de fichier ? | `v1` |
| **Propriétaire** | Qui répond des questions sur ce jeu ? | le service relation client |
| **Droits et sensibilité** | A-t-on le droit de l'utiliser, comment ? | données personnelles, usage interne |

Deux de ces rubriques font à elles seules la moitié du travail : le **grain** (qu'est-ce qu'une ligne ?) et la **source** (d'où vient-elle ?). Dans le volume I, vous avez vu qu'oublier le grain est la cause du double comptage ; oublier la source est la cause de la plupart des chiffres qui ne se recoupent pas.

> 💡 **Intuition.** La fiche répond à une seule question, posée par quelqu'un qui n'a jamais vu le fichier : **« Puis-je lui faire confiance pour ce que je veux en faire ? »** Si la fiche ne permet pas de répondre, elle est incomplète.

### 4.1.2 Remplir la fiche du CRM

Une partie de la fiche se **mesure** (le nombre de lignes, de colonnes, l'empreinte du contenu) ; l'autre se **demande** (à la personne qui a fait l'export) ou se **constate** en regardant les données. Mélangeons les deux : la fonction `fiche_jeu` prend les informations saisies à la main et ajoute celles que le tableau livre lui-même.

```python
O.fiche_jeu(crm, **{
    "nom": "crm_clients (v1)", "source": "export du CRM de la boutique", "date d'extraction": "2025-12-31",
    "périmètre": "clients saisis depuis 2018, doublons compris", "une ligne =": "une saisie de fiche (pas un client)",
    "clé": "id_crm (numéro de saisie)", "propriétaire": "service relation client",
    "limites connues": "doublons, formats mixtes, lignes de test", "droits": "données personnelles, usage interne"})
```
<!--sortie-->
```text
nom                   : crm_clients (v1)
source                : export du CRM de la boutique
date d'extraction     : 2025-12-31
périmètre             : clients saisis depuis 2018, doublons compris
une ligne =           : une saisie de fiche (pas un client)
clé                   : id_crm (numéro de saisie)
propriétaire          : service relation client
limites connues       : doublons, formats mixtes, lignes de test
droits                : données personnelles, usage interne
lignes                : 7 140
colonnes              : 11
empreinte du contenu  : 84f642145769
```

Le CRM compte **7 140 lignes** pour **11 colonnes**. L'**empreinte** est un code de douze caractères calculé sur tout le contenu : la même fiche, appliquée plus tard au même fichier, donnera la même empreinte ; si quelqu'un modifie une seule cellule, elle changera (nous y reviendrons en 4.3). C'est un moyen simple de **prouver** qu'on parle du même fichier.

Trois remarques sur cette fiche.

- **La rubrique « limites connues » est la plus utile et la plus négligée.** On y écrit ce que l'on sait déjà, même approximativement : « doublons probables, non mesurés », « montants parfois vides », « dates en formats mixtes ». Une limite signalée est un piège évité pour le lecteur suivant.
- **Le grain n'est pas le client.** La ligne du CRM est une **saisie**, et un client saisi trois fois apparaît trois fois. Écrire « une ligne = une saisie de fiche » évite qu'un collègue compte `len(crm)` comme le nombre de clients.
- **La fiche se range avec le fichier.** Dans le même dossier, sous le nom `crm_clients_v1.md`, ou en tête du dossier du projet : un fichier de données sans sa fiche est un fichier orphelin.

> ⚠️ **Piège.** Ne **déduisez pas** la fiche en regardant le fichier. Le tableau peut vous apprendre le nombre de lignes, pas pourquoi les clients de 2018 y sont ni qui a fait l'export. Posez la question à la source, **par écrit**, et gardez la réponse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1, exercices 4.1 et 4.2.

### 4.1.3 Documenter une transformation : le journal des décisions

La fiche décrit le brut. Reste à documenter **ce que l'on en fait**. Un nettoyage de données est une suite de **décisions** : on retire les lignes de test, on met les adresses électroniques en minuscules, on fusionne les doublons. Chacune est discutable, chacune a un effet mesurable. Le **journal des décisions** consigne, pour chaque étape, cinq informations.

1. **La règle** : ce que l'on fait, en une phrase précise (« retirer les lignes dont l'adresse est `test@example.com` »).
2. **La justification** : pourquoi (« ce ne sont pas des clients »). C'est la partie que personne n'écrit, et que tout le monde regrette.
3. **Les effectifs** : combien de lignes **avant**, combien **après**.
4. **Le nombre de lignes touchées** : retirées, ou modifiées sans être retirées.
5. **Une empreinte du résultat** : pour pouvoir vérifier, plus tard, qu'en rejouant les étapes on retombe sur le **même tableau**.

Ces effectifs ne sont pas décoratifs : ils obéissent à une **équation de conservation**.

> 📐 **L'équation de conservation.** Pour toute suite d'étapes qui ne fait que retirer ou modifier des lignes, le nombre de lignes lues, moins le nombre de lignes retirées à chaque étape, est le nombre de lignes finales : $N_{\text{lues}}-\sum_k r_k=N_{\text{finales}}$. Si ce calcul ne tombe pas juste, une étape a **perdu** ou **inventé** des lignes sans le dire. C'est le contrôle le plus simple et le plus puissant d'un nettoyage.

Ce qui rend le journal précieux, c'est qu'il transforme une affirmation (« j'ai nettoyé le CRM ») en une **suite vérifiable** : chaque ligne du journal peut être rejouée, contestée et corrigée séparément.

### 4.1.4 Un journal écrit par le code

Tenir ce journal à la main est fastidieux et fragile : on oublie une étape, on recopie mal un effectif. Mieux vaut que **le code l'écrive lui-même**, à chaque étape, au moment où il agit. Le principe tient en quelques lignes : une petite classe `Journal` dont la méthode `etape` reçoit le tableau avant, le tableau après, la règle et la justification, et consigne le reste automatiquement.

```python
j = O.Journal("crm", crm)
est_test = crm["email"].fillna("").str.strip().str.lower().eq("test@example.com")
apres = j.etape(crm, crm[~est_test].copy(), "retirer les lignes de test", "ce ne sont pas des clients")
print(j.table()[["etape", "regle", "avant", "apres", "retirees"]].to_string(index=False))
```
<!--sortie-->
```text
  etape                                  regle  avant  apres  retirees
lecture lecture du fichier brut, tout en texte   7140   7140         0
      1             retirer les lignes de test   7140   7000       140
```

Dans l'exemple, une seule étape est consignée : 7 140 lignes lues, 140 lignes de test retirées, 7 000 lignes restantes. La fonction `nettoyer_crm`, fournie avec le chapitre, enchaîne **quatre** étapes de ce genre. Voici ce qu'elle consigne.

```python
propre, journal = O.nettoyer_crm(crm)
t = journal.table()
print(t[["etape", "avant", "apres", "retirees", "modifiees", "empreinte"]].to_string(index=False))
print("lues, retirées, finales :", journal.conservation())
```
<!--sortie-->
```text
  etape  avant  apres  retirees  modifiees    empreinte
lecture   7140   7140         0          0 84f642145769
      1   7140   7000       140          0 2cf9dc57b1dd
      2   7000   7000         0        357 a8e64c9664db
      3   7000   7000         0       5624 2eeca19cf76d
      4   7000   6323       677          0 e729855c52a1
lues, retirées, finales : (7140, 817, 6323)
```

La dernière ligne est l'équation de conservation : **7 140 lignes lues, 817 retirées (140 + 677), 6 323 lignes finales**. Elle tombe juste. Les quatre étapes sont les suivantes.

| Étape | Règle | Justification |
|---|---|---|
| 1 | retirer les lignes de test (adresse `test@example.com`) | ce ne sont pas des clients |
| 2 | adresses e-mail : retirer les espaces, passer en minuscules ; mettre à vide celles qui n'ont pas exactement un `@` ou qui contiennent deux points de suite | une adresse n'est comparable que normalisée ; une adresse invalide n'est pas une information |
| 3 | téléphones : ne garder que les chiffres | un seul format, pour pouvoir comparer |
| 4 | doublons : une seule ligne par adresse normalisée, en gardant le plus petit `id_crm` | deux saisies de la même adresse sont le même client |

```python hide
F4.cascade(t)
```
<!--sortie-->
```text
figure : ch04-journal-crm.png
```

![Effectif du CRM après chaque étape : 7 140 lignes lues, 140 lignes de test retirées, 357 adresses et 5 624 téléphones normalisés, puis 677 doublons retirés. Les barres orange sont les étapes qui retirent des lignes, les barres bleues celles qui modifient sans retirer.](figures/ch04-journal-crm.png)

Deux colonnes demandent un mot. **« modifiées »** compte les lignes dont au moins la valeur d'une cellule a changé : 357 adresses ont été corrigées ou mises à vide (espaces, majuscules, adresse invalide), 5 624 téléphones ont changé de format. Aucune ligne n'a disparu à ces étapes : l'effectif ne bouge pas, mais le journal montre l'**ampleur** de la transformation. **« empreinte »** est celle du tableau obtenu à la fin de l'étape ; deux personnes qui appliquent les mêmes règles au même fichier obtiendront les mêmes empreintes, étape par étape. Si elles divergent à l'étape 3, le désaccord se **localise** immédiatement.

> 💡 **Intuition.** Le journal est un **relevé de compte** : chaque débit est justifié, le solde final est vérifié. On ne demande pas à une banque de nous croire sur parole, on ne devrait pas non plus demander à un analyste de croire son propre chiffre sans relevé.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2, exercice 4.3.

### 4.1.5 Le journal face à la vérité : ce qu'il montre, ce qu'il ne dit pas

Le journal consigne **ce que l'on a fait**. Il ne dit pas si c'était **juste**. Comme le CRM est simulé, nous pouvons ouvrir le fichier de vérité (`verite_crm.csv`) pour savoir ce que nos quatre étapes ont réellement accompli. C'est un luxe que l'on n'a jamais en vrai ; il nous permet de mesurer la différence entre « j'ai appliqué la règle » et « la règle avait raison ».

```python hide-code
v = O.charger("verite_crm")
vv = crm.assign(id_crm=crm["id_crm"].astype(int)).merge(v, on="id_crm")
gardes = propre.merge(v, on="id_crm")
retirees_mail = vv[~vv["id_crm"].isin(propre["id_crm"]) & (vv["defauts"] != "test")]
fusions_a_tort = int((retirees_mail["est_doublon"] == 0).sum())
print(f"lignes de test retirées à l'étape 1        : {int((vv['defauts'] == 'test').sum())} sur {int((vv['defauts'] == 'test').sum())}")
print(f"lignes retirées à l'étape 4                : {len(retirees_mail)} dont {len(retirees_mail) - fusions_a_tort} vrais doublons et {fusions_a_tort} fusions à tort")
print(f"lignes finales                             : {len(gardes)} pour {gardes['id_client'].nunique()} clients distincts (vérité : 6 000)")
print(f"vrais doublons qui restent                 : {int(gardes['est_doublon'].sum())}")
```
<!--sortie-->
```text
lignes de test retirées à l'étape 1        : 140 sur 140
lignes retirées à l'étape 4                : 677 dont 674 vrais doublons et 3 fusions à tort
lignes finales                             : 6323 pour 5997 clients distincts (vérité : 6 000)
vrais doublons qui restent                 : 326
```

Quatre enseignements.

1. **L'étape 1 est parfaite** : les 140 lignes de test, et seulement elles, ont été retirées.
2. **L'étape 4 retire presque exclusivement de vrais doublons** (674 sur 677) mais **fusionne à tort trois clients différents** qui avaient la même adresse normalisée. Les trois personnes ont simplement une adresse identique — homonymes dont les adresses coïncident. La règle « une adresse égale un client » est raisonnable, **pas infaillible** : le journal l'écrit, la vérité la juge.
3. **Il reste 326 doublons**, puisque la règle ne voit que les adresses **identiques** : les doublons dont l'adresse est absente ou différente passent au travers. Les 6 323 lignes finales décrivent 5 997 clients distincts, alors qu'il y en a 6 000 : **trois clients ont disparu** et 326 lignes sont en trop. Retrouver le reste exige un rapprochement approché des noms, ce que nous verrons en section 2.5.
4. **Le journal n'a rien caché** : c'est précisément parce que la règle, la justification et les effectifs sont écrits que l'on peut, après coup, mesurer ses défauts. Un nettoyage sans journal laisse le même résultat, sans moyen de le discuter.

> ⚠️ **Piège.** Un journal bien tenu ne rend pas un nettoyage correct ; il le rend **contestable**, et c'est mieux. Ne jamais écrire dans le journal « données nettoyées » sans les effectifs : ce n'est pas une documentation, c'est une affirmation.

### 4.1.6 README, commentaires, noms de fichiers : le reste de la documentation

La fiche et le journal sont le cœur. Autour d'eux, trois habitudes complètent le dispositif.

**Un README de projet.** C'est le premier fichier qu'ouvre quelqu'un qui découvre le dossier. Il tient en vingt lignes et répond à : *à quoi sert ce projet ? comment relancer ? qu'est-ce qu'il y a dans chaque dossier ? qui contacter ?*

```markdown noexec
# Synthèse du quatrième trimestre 2025 — boutique

**Question** : chiffre d'affaires, panier moyen et taux de retour par canal, T4 2025 contre T4 2024.
**Livrables** : `sortie/synthese_t4.csv`, `sortie/graphique_t4.png`, `sortie/message_gerante.md`.

## Relancer
1. Placer les fichiers bruts de `entree/` (voir leur fiche : `entree/*.md`).
2. Lancer `python run.py` (une seule commande, tout depuis le brut).
3. Comparer `sortie/journal.csv` à la version précédente.

## Dossiers
`entree/` fichiers bruts, jamais modifiés · `travail/` fichiers intermédiaires · `sortie/` livrables · `docs/` dictionnaire, glossaire

**Auteur** : analyse · **Dernière mise à jour** : 2026-01-05 · **Version des données** : v1
```

**Des commentaires qui disent *pourquoi*.** Un commentaire qui répète le code est du bruit ; un commentaire qui explique une **décision** est une documentation. Comparez.

```python noexec
df = df[df["total"] < 1000]   # on garde les totaux inférieurs à 1000          <- inutile : le code le dit déjà
df = df[df["total"] < 1000]   # au-delà : montants en centimes (changement d'unité du site au 15/09)   <- utile : il dit POURQUOI
```

**Des noms de fichiers qui portent la date et la version.** Pas de `donnees_final.csv`, `donnees_final2.csv` ni `donnees_VRAI_final.csv`. Une convention simple suffit : `nom_AAAA-MM-JJ_vN.ext`, avec la **date de l'extraction** (pas celle où l'on a ouvert le fichier) et un numéro de version qui monte à chaque modification de contenu.

| À éviter | À préférer | Pourquoi |
|---|---|---|
| `clients_final.csv` | `crm_clients_2025-12-31_v1.csv` | la date de l'extraction se lit, et le fichier se retrouve |
| `clients_final2.csv`, `clients_VRAI.csv` | `crm_clients_2025-12-31_v2.csv` | une version = un numéro, pas un adjectif |
| `Copie de ventes (3).xlsx` | `ventes_t4_2025_v3.xlsx` | pas de copie sans nom |
| `export 05-12.csv` | `export_caisse_2025-12-05.csv` | dates en ISO (année d'abord) : l'ordre alphabétique est l'ordre chronologique |

> 🧭 **En pratique.** On ne modifie **jamais** un fichier brut : on le copie dans `travail/` et l'on travaille sur la copie. Le brut dans `entree/` reste ce qu'il était le jour de la livraison, accompagné de sa fiche et de son empreinte ; c'est lui qui permet de **tout rejouer**.

### 4.1.7 La reproductibilité : tout refaire depuis le brut

Le test ultime d'une documentation est simple : **quelqu'un d'autre, ou vous dans six mois, peut-il refaire le travail depuis le brut et retrouver le même résultat ?** Concrètement : une seule commande, qui lit les fichiers bruts, applique les étapes dans l'ordre, écrit le journal et les livrables. Pas de manipulation manuelle entre deux étapes, pas d'état caché.

On peut le **vérifier** : relancer tout le nettoyage deux fois, depuis le brut lu à nouveau, et comparer les empreintes.

```python
brut2 = O.charger("crm_clients", dtype=str)            # on relit le fichier : aucun état conservé
propre2, journal2 = O.nettoyer_crm(brut2)
print("même empreinte finale :", O.empreinte_df(propre2) == O.empreinte_df(propre))
print("mêmes empreintes à chaque étape :", list(journal2.table()["empreinte"]) == list(journal.table()["empreinte"]))
```
<!--sortie-->
```text
même empreinte finale : True
mêmes empreintes à chaque étape : True
```

Les deux exécutions produisent exactement le même résultat, étape par étape. C'est la définition pratique de la **reproductibilité** : pas « on devrait retrouver à peu près la même chose », mais « les empreintes sont identiques ».

> ⚠️ **Piège.** Une opération qui dépend du **hasard** (un échantillon tiré sans graine), de l'**heure** (une date du jour écrite dans le résultat) ou de l'**ordre** de lecture d'un dossier (des fichiers lus dans l'ordre où le système les liste) casse la reproductibilité. On fixe la graine, on passe la date en paramètre, on trie les fichiers.

### 4.1.8 Bonne et mauvaise documentation

Terminons par un portrait-robot. Une documentation est bonne quand elle est **courte, vérifiable et à jour**. Elle est mauvaise quand elle est vague, invérifiable, ou périmée.

| Mauvaise documentation | Bonne documentation | Ce qui change |
|---|---|---|
| « Données nettoyées. » | « 7 140 lignes lues, 140 lignes de test et 677 doublons d'e-mail retirés, 6 323 lignes finales. » | des effectifs vérifiables |
| « Export du CRM. » | « Export du CRM du 31/12/2025, tous clients saisis depuis 2018, v1, empreinte `dc4918622cc0`. » | une date, un périmètre, une version |
| « Les montants sont en euros. » | « `total` : euros jusqu'au 14/09/2025, **centimes** à partir du 15/09 (changement du site). » | l'unité et sa limite |
| « Voir le notebook. » | « `python run.py` refait tout depuis `entree/` ; résultat attendu : empreinte `a4c09a3fa175`. » | une commande et un résultat attendu |
| « Ancien dictionnaire, peut-être encore valable. » | « Dictionnaire v3, vérifié automatiquement contre le fichier le 05/01/2026. » | un contrôle daté |

La dernière ligne annonce la section suivante : un dictionnaire de données qui ne se vérifie pas finit toujours par mentir.

### 4.1.9 Combien documenter ? Proportionner à l'enjeu

Tout documenter autant serait absurde : on ne rédige pas une fiche de six rubriques pour un calcul que l'on jette dans l'heure. La règle est de **proportionner la documentation à l'enjeu** et à la **durée de vie** du travail. Trois niveaux couvrent presque tous les cas.

| Niveau | Exemple | Ce que l'on écrit |
|---|---|---|
| **Exploration jetable** | regarder un fichier pour se faire une idée, un calcul à la main | une ligne en tête du notebook : la question, la source, la date |
| **Rapport récurrent** | la synthèse du trimestre, un tableau de bord mensuel | la fiche des fichiers d'entrée, le journal des étapes, un README, une commande qui refait tout |
| **Chiffre engageant** | un bilan, un dossier de banque, une décision de prix ou de personnel | tout ce qui précède, plus le dictionnaire vérifié, le glossaire, les empreintes, le journal d'audit et une relecture par une autre personne |

Un travail change de niveau sans prévenir : l'exploration jetable de lundi devient le chiffre du bilan de vendredi. Le bon réflexe est de se demander, **dès le début**, « cela peut-il me resservir, ou servir à quelqu'un d'autre ? ». Si la réponse est oui, on passe au niveau du dessus avant de produire le chiffre, pas après.

> 🧭 **En pratique.** Documentez **en travaillant**, pas à la fin. Une règle de nettoyage écrite au moment où on la décide prend dix secondes ; la reconstituer trois semaines plus tard prend une heure et se fait de travers.

> ✅ **À retenir.** Une **fiche** par jeu de données (source, extraction, périmètre, grain, clé, limites, version, propriétaire, droits) ; un **journal** par transformation (règle, justification, effectifs avant et après, lignes touchées, empreinte) **écrit par le code** ; l'**équation de conservation** (lignes lues − lignes retirées = lignes finales) comme contrôle de base ; le **brut intact**, une commande qui **refait tout**, et des empreintes identiques d'une exécution à l'autre. Sur le CRM : 7 140 lignes lues, 817 retirées, 6 323 restantes, dont 326 doublons que seul un rapprochement approché trouvera.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 et 4.2, exercices 4.1 à 4.5.
