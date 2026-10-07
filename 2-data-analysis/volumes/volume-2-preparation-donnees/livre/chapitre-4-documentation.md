# Chapitre 4 : Documentation et dictionnaires de données

> « Un chiffre que personne ne peut refaire est un chiffre que personne ne peut défendre. »


La gérante vous arrête devant la machine à café, un dossier à la main. « Ma collègue de la comptabilité a repris ton analyse du quatrième trimestre pour le bilan. **Elle ne retrouve pas ton chiffre.** Tu m'avais dit 211 434 € pour le Site, elle m'en annonce un autre. Qu'est-ce qui manque ? »

Vous reprenez la question avec calme, parce que vous savez qu'il y a deux réponses possibles. Ou bien l'un de vous deux s'est trompé, ou bien — c'est le cas le plus fréquent — **vous avez tous deux raison**, mais vous ne parlez pas du même chiffre. Faisons l'expérience sur les données de la boutique : quatre calculs honnêtes du « chiffre d'affaires du quatrième trimestre pour le canal Site », qui ne diffèrent que par un choix que personne n'a écrit.

```python
site_t4 = x[(x["canal"] == "Site") & (x["date_commande"] >= "2025-10-01")]
variantes = {
    "TTC, remises déduites, jusqu'au 31/12": site_t4["montant"].sum(),
    "hors taxe (TVA fictive de 20 %)": site_t4["montant"].sum() / 1.2,
    "avant remises": (site_t4["quantite"] * site_t4["prix_unitaire"]).sum(),
    "extraction arrêtée au 15/12": site_t4[site_t4["date_commande"] <= "2025-12-15"]["montant"].sum(),
}
for nom, v in variantes.items():
    print(f"{O.eur(v):>14}  {nom}")
```
<!--sortie-->
```text
  211 433,79 €  TTC, remises déduites, jusqu'au 31/12
  176 194,83 €  hors taxe (TVA fictive de 20 %)
  214 992,95 €  avant remises
  166 108,12 €  extraction arrêtée au 15/12
```

Quatre chiffres, tous **exacts**, séparés de près de 49 000 € entre le plus bas et le plus haut : la **taxe**, les **remises**, la **date** de l'extraction. Aucune erreur de calcul là-dedans ; ce qui manque, c'est la **phrase** qui dit lequel on a calculé. Voici ce que votre collègue aurait voulu trouver à côté du chiffre.


![Le chiffre de 211 434 € et les six questions que se pose quelqu'un qui doit le refaire : de quelle source, extraite quand, TTC ou HT, quelles lignes écartées, quelle définition du trimestre, avec quelle version du code.](figures/ch04-ce-qui-manque.png)

Ce chapitre vous apprend à répondre à ces six questions **avant** qu'on vous les pose : en **documentant** ce que l'on a reçu (les jeux de données), ce que l'on en a fait (les transformations), ce que veulent dire les colonnes (le dictionnaire) et, pour aller plus loin, **d'où vient chaque chiffre** (le lignage).

## Pourquoi un analyste documente

Documenter n'est pas de la bureaucratie ; c'est la partie du travail qui **rend le reste réutilisable**. Quatre raisons, que vous rencontrerez dès la première année.

- **Refaire.** Dans trois mois, la gérante vous demandera la même analyse sur le trimestre suivant. Si le travail est écrit, il se **rejoue** en dix minutes ; sinon, il se **refait** en trois jours, avec des résultats légèrement différents sans que l'on sache pourquoi.
- **Comprendre.** Une colonne `statut` qui contient `PAID`, `paid` et `Paid` ne se comprend pas toute seule. Une colonne `total` qui change d'unité en septembre non plus. La documentation rend ces pièges **visibles pour la personne suivante**, y compris vous dans six mois.
- **Auditer.** Un chiffre qui va dans un bilan, dans un dossier de banque ou dans une décision de prix peut être contesté. Pouvoir montrer la **chaîne** — la source, les règles, les contrôles — transforme une opinion en démonstration.
- **Transmettre.** Un jour, quelqu'un reprendra votre poste. La documentation est la différence entre une passation de dix minutes et une enquête de dix jours.

> 💡 **Intuition.** Documenter, c'est écrire pour **quelqu'un d'intelligent qui n'a pas assisté à la réunion**. Cette personne sait lire du Python, du SQL et des tableaux ; elle ne sait pas ce que **vous** saviez en le faisant. Presque toujours, cette personne, c'est vous dans six mois.

## Le chemin de ce chapitre

Le parcours essentiel suit deux étapes, qui correspondent aux deux choses que l'on documente.

- **4.1 Documenter les jeux de données et les transformations** : la fiche d'un jeu de données (d'où vient-il, que représente une ligne, que sait-on de ses défauts), puis le **journal** d'un nettoyage (une règle, une justification, des effectifs avant et après), écrit par le code lui-même.
- **4.2 Construire un dictionnaire de données** : que veut dire chaque colonne (libellé, type, unité, valeurs permises, codage des manquants, sensibilité), comment en fabriquer un squelette automatiquement, comment **vérifier qu'il reste vrai**, et comment s'accorder sur une définition unique de « client actif », de « commande annulée » ou de « panier moyen ».

Une section facultative prolonge ce parcours : **➕ 4.3 Lignage des données et pistes d'audit**, pour savoir **d'où vient** un chiffre, prouver qu'une entrée n'a pas changé (les empreintes), tenir un journal d'audit et rejouer un résultat depuis le brut grâce à sa documentation.

## Les données du chapitre

> 📦 **Quatre jeux de la boutique.** Le chapitre documente des fichiers que vous connaissez déjà ou que vous allez retrouver : `crm_clients.csv` (le CRM, 7 140 lignes, désordonné : il sert à l'exemple de la fiche et du journal), `clients.csv` et `produits.csv` (les référentiels propres du volume I), et `profil_clients.csv` (le profil de 6 000 clients, avec des valeurs manquantes : il sert à l'exemple du dictionnaire). Les commandes (`commandes.csv`, `lignes_commande.csv`) servent à calculer les chiffres que l'on documente. Tous sont **simulés** ; les fichiers `verite_*.csv` ne servent qu'à **juger** nos choix à la fin d'une étude : on ne les ouvre pas pour nettoyer.

Tout le code de ce chapitre est **réellement exécuté** : ce que vous lirez sous un bloc est ce que le code a produit, pas une illustration.

> 📒 **Pour s'entraîner.** Le chapitre 4 du cahier propose huit applications (fiches, journaux, dictionnaires, lignage, empreintes) et douze exercices corrigés ; chaque section du livre indique ceux qui la prolongent.


## 4.1 Documenter les jeux de données et les transformations

Documenter deux choses distinctes : **ce que l'on a reçu** (un jeu de données, avec son histoire et ses défauts) et **ce que l'on en a fait** (une suite de transformations, chacune avec une règle et une justification). La première se consigne dans une **fiche**, la seconde dans un **journal**. Cette section montre les deux, puis comment les ranger pour que quelqu'un d'autre — ou vous, plus tard — puisse tout rejouer depuis le fichier brut.


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


![Effectif du CRM après chaque étape : 7 140 lignes lues, 140 lignes de test retirées, 357 adresses et 5 624 téléphones normalisés, puis 677 doublons retirés. Les barres orange sont les étapes qui retirent des lignes, les barres bleues celles qui modifient sans retirer.](figures/ch04-journal-crm.png)

Deux colonnes demandent un mot. **« modifiées »** compte les lignes dont au moins la valeur d'une cellule a changé : 357 adresses ont été corrigées ou mises à vide (espaces, majuscules, adresse invalide), 5 624 téléphones ont changé de format. Aucune ligne n'a disparu à ces étapes : l'effectif ne bouge pas, mais le journal montre l'**ampleur** de la transformation. **« empreinte »** est celle du tableau obtenu à la fin de l'étape ; deux personnes qui appliquent les mêmes règles au même fichier obtiendront les mêmes empreintes, étape par étape. Si elles divergent à l'étape 3, le désaccord se **localise** immédiatement.

> 💡 **Intuition.** Le journal est un **relevé de compte** : chaque débit est justifié, le solde final est vérifié. On ne demande pas à une banque de nous croire sur parole, on ne devrait pas non plus demander à un analyste de croire son propre chiffre sans relevé.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2, exercice 4.3.

### 4.1.5 Le journal face à la vérité : ce qu'il montre, ce qu'il ne dit pas

Le journal consigne **ce que l'on a fait**. Il ne dit pas si c'était **juste**. Comme le CRM est simulé, nous pouvons ouvrir le fichier de vérité (`verite_crm.csv`) pour savoir ce que nos quatre étapes ont réellement accompli. C'est un luxe que l'on n'a jamais en vrai ; il nous permet de mesurer la différence entre « j'ai appliqué la règle » et « la règle avait raison ».

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

```markdown
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

```python
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


## 4.2 Construire un dictionnaire de données

La fiche décrit un fichier ; le **dictionnaire de données** décrit ses **colonnes**. C'est le document qui dit ce que veut dire `satisfaction_moy`, en quelle unité est `revenu_annuel`, quelles valeurs sont permises dans `canal_acquisition` et ce que signifie une cellule vide. Cette section montre comment en construire un sans y passer des jours (un squelette automatique, enrichi à la main), comment le **ranger**, comment **vérifier qu'il reste vrai** et comment s'entendre, au-delà des colonnes, sur les **mots** de l'entreprise.


### 4.2.1 À quoi sert un dictionnaire, et ce qu'il contient

Imaginez que vous receviez le fichier `profil_clients.csv` sans autre explication. Vous voyez une colonne `satisfaction_moy` : est-elle sur 5 ? sur 10 ? calculée sur combien de réponses ? Une colonne `revenu_annuel` : en euros ? du client ou de son foyer ? réel ou estimé ? Un dictionnaire répond à ces questions **une fois pour toutes**, au lieu que chaque lecteur les pose à chaque analyse.

Pour chaque colonne, on documente onze attributs. Les premiers décrivent la colonne, les suivants disent quelles valeurs on peut y rencontrer, les derniers d'où elle vient.

| Attribut | Question | Exemple pour `revenu_annuel` |
|---|---|---|
| **Nom** | Comment s'appelle-t-elle dans le fichier ? | `revenu_annuel` |
| **Libellé** | Que représente-t-elle, en une phrase ? | revenu annuel estimé du foyer |
| **Type** | Quel type de valeur, technique et logique ? | décimal (`float64`) |
| **Unité** | En quelle unité ? | € |
| **Valeurs permises** | Quel domaine, quelles bornes ? | positif ; modalités listées pour les catégories |
| **Obligatoire** | Peut-elle être vide ? | non |
| **Codage des manquants** | Que veut dire une cellule vide ? | « non estimé » |
| **Exemple** | À quoi ressemble une valeur ? | 54 000 |
| **Règle de calcul ou source** | D'où vient-elle ? | modèle d'estimation externe |
| **Sensibilité** | Faut-il la protéger ? | personnelle |
| **Version** | Depuis quand, avec quels changements ? | v1 |

Deux d'entre eux méritent qu'on s'y attarde. Le **type** est double : il y a le type **technique** (ce que dit l'ordinateur : entier, décimal, texte) et le type **logique** (ce que veut dire la colonne : une date, un identifiant, une catégorie, un montant). Une date lue comme du texte a un type technique `str` et un type logique « date » : le dictionnaire doit donner **les deux**, parce que c'est l'écart entre eux qui annonce un nettoyage à faire. Le **codage des manquants** est le plus oublié : une cellule vide peut vouloir dire « non demandé », « inconnu », « refusé » ou « zéro », et l'analyse change complètement selon la réponse (chapitre 1).

> 💡 **Intuition.** Un dictionnaire est un **contrat** entre celui qui produit le fichier et ceux qui l'utilisent : « voici ce que vous trouverez dans chaque colonne ». Quand le contrat est rompu (une colonne change d'unité sans prévenir), c'est le contrat qui permet de le **constater**.

### 4.2.2 Partir d'un squelette fabriqué par le code

Écrire un dictionnaire à la main, colonne par colonne, est long et source de fautes. Une bonne partie des informations se **lit** pourtant directement dans le tableau : le type technique, la part de valeurs manquantes, le nombre de valeurs distinctes, le minimum, le maximum, un exemple. La fonction `squelette` les rassemble en une ligne par colonne.

```python
sq = O.squelette(profil)
print(sq.to_string(index=False))
```
<!--sortie-->
```text
          colonne    type  manquants_pct  distincts      min       max  exemple
        id_client   int64            0.0       6000        1      6000        1
              age   int64            0.0         68       18        85       33
canal_acquisition     str            0.0          3 Boutique      Site Boutique
    revenu_annuel float64           17.3        555   6900.0  104400.0  54000.0
nb_commandes_2025   int64            0.0         24        0        25        0
     depense_2025 float64            5.0       2838      0.0   3382.33      0.0
 satisfaction_moy float64            9.4        312      1.0       5.0     4.61
     minutes_site float64            0.0        533      0.2      86.4      2.4
```

En un coup d'œil, ce squelette signale déjà ce qu'il faudra documenter : trois colonnes ont des **valeurs manquantes** (17,3 % des revenus, 5,0 % des dépenses, 9,4 % des satisfactions), `canal_acquisition` ne prend que **trois valeurs** (c'est une catégorie : on listera ses modalités), `satisfaction_moy` va de 1,0 à 5,0 (une note sur 5), et `id_client` a autant de valeurs distinctes que de lignes (c'est une clé).

Mais ce squelette ne sait **pas** dire l'essentiel. Il ne sait pas que `revenu_annuel` est un revenu **estimé** et **du foyer**, que `age` est l'âge **au 31 décembre 2025**, que `depense_2025` est **TTC** et **remises déduites**, que `satisfaction_moy` est une moyenne de **réponses à une enquête** (donc vide pour qui n'a pas répondu). Ni l'unité, ni la règle de calcul, ni la sensibilité ne se déduisent des valeurs. Un squelette automatique fait la partie **la moins difficile** du travail ; le reste demande quelqu'un qui connaît l'activité.

> ⚠️ **Piège.** Ne confondez pas **minimum et maximum observés** avec **valeurs permises**. Le squelette dit que `satisfaction_moy` va de 1,0 à 5,0 *dans ce fichier* ; ce n'est pas lui qui garantit que la note n'a pas le droit de valoir 0 ou 6. La règle est une **décision** (une note de 1 à 5), à écrire à la main.

### 4.2.3 L'enrichir à la main

On complète le squelette avec ce que seule une personne du métier sait : le libellé, l'unité, les valeurs permises, le caractère obligatoire, le codage des manquants, la règle de calcul, la sensibilité. Le plus simple est de saisir ces informations dans un fichier texte structuré, puis de les **fusionner** avec le squelette : la partie automatique reste toujours à jour, la partie humaine est saisie une fois. Voici, au format YAML, l'entrée complète d'une colonne.

```python
import yaml
dico = O.dico_complet(profil, "profil_clients")
fiche = dico[dico["colonne"] == "revenu_annuel"].iloc[0]
cles = ["colonne", "libelle", "unite", "type", "manquants_pct", "codage_manquant", "regle_ou_source", "sensibilite"]
entree = {k: (None if pd.isna(fiche[k]) else fiche[k]) for k in cles}
print(yaml.safe_dump({k: (v.item() if hasattr(v, "item") else v) for k, v in entree.items()}, allow_unicode=True, sort_keys=False))
```
<!--sortie-->
```text
colonne: revenu_annuel
libelle: Revenu annuel estimé du foyer
unite: €
type: float64
manquants_pct: 17.3
codage_manquant: vide = non estimé
regle_ou_source: modèle d'estimation externe (voir limites)
sensibilite: personnelle
```

Le dictionnaire complet du jeu tient ensuite en une table lisible. Voici ses colonnes principales.

```python
print(dico[["colonne", "libelle", "unite", "manquants_pct", "sensibilite"]].to_string(index=False))
```
<!--sortie-->
```text
          colonne                                       libelle         unite  manquants_pct sensibilite
        id_client                         Identifiant du client                          0.0   indirecte
              age                             Âge au 31/12/2025        années            0.0 personnelle
canal_acquisition         Canal par lequel le client est arrivé                          0.0            
    revenu_annuel                 Revenu annuel estimé du foyer             €           17.3 personnelle
nb_commandes_2025           Nombre de commandes passées en 2025     commandes            0.0            
     depense_2025 Dépense totale en 2025, TTC, remises déduites             €            5.0            
 satisfaction_moy                 Satisfaction moyenne déclarée note de 1 à 5            9.4            
     minutes_site                       Temps passé sur le site       minutes            0.0 personnelle
```

La colonne **« sensibilité »** mérite un mot : elle ne sert pas à l'analyse, elle sert à la **protection**. Elle distingue les colonnes qui identifient directement une personne (nom, adresse), celles qui permettent de la retrouver en les croisant (âge, ville, identifiant) et celles qui sont confidentielles pour l'entreprise (le coût d'achat). On la remplit dès maintenant, parce que le chapitre 5 en aura besoin.

> 🧭 **En pratique.** Faites remplir le dictionnaire par **deux personnes** : celle qui connaît les données (l'analyste) pour les types et les manquants, celle qui connaît le métier (la gérante, un responsable) pour les libellés, les unités et les règles. Une colonne que personne ne sait décrire est une colonne qu'il ne faut pas utiliser.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3, exercices 4.6 et 4.7.

### 4.2.4 Où ranger le dictionnaire : quelques formats

Un dictionnaire ne sert que s'il est **trouvable, lisible et exploitable par un programme**. Cinq formats courants, aucun n'est le meilleur partout.

| Format | Les + | Les − | Quand l'utiliser |
|---|---|---|---|
| **Tableur** (`.xlsx`) | tout le monde sait l'ouvrir, saisie facile pour les non-techniciens | peu lisible par un programme, se périme en silence | dictionnaire rédigé par des métiers |
| **CSV** | simple, versionnable, lisible par un programme | pas de mise en forme, pas de structure imbriquée | dictionnaire d'un seul jeu, en entrée d'un contrôle automatique |
| **YAML** (ou JSON) | structuré, imbriqué, lisible par un humain et un programme | demande un peu de rigueur de syntaxe | dictionnaire pilotant un traitement |
| **Markdown** | se lit tel quel, se range avec le code (README) | pas fait pour être lu par un programme | documentation publiée |
| **Commentaires de la base** | le dictionnaire vit **dans** la base, à côté de la colonne | propre à chaque moteur, souvent ignoré | bases de données d'entreprise |

Quel que soit le format, le dictionnaire se range **à côté du fichier** qu'il décrit, avec le même nom, la même version et la même date. Il peut aussi être **publié** sous une forme agréable à lire : voici le dictionnaire de `profil_clients` rendu sous forme d'une page web.


![Le dictionnaire de profil_clients publié en page web : une ligne par colonne, avec libellé, unité, type, part de valeurs manquantes et sensibilité. Capture réelle d'une page produite localement et rendue avec un navigateur sans interface.](figures/ch04-dictionnaire-capture.png)

> 🧭 **En pratique.** Pour un analyste isolé, un **CSV par jeu de données** (une ligne par colonne) rangé à côté du fichier est le meilleur rapport simplicité/utilité. Il se lit dans un tableur, se versionne avec le code et se **vérifie par programme**, ce que nous allons faire.

### 4.2.5 Un dictionnaire qui ment : le vérifier automatiquement

Le pire dictionnaire est celui qui **est faux sans que personne le sache** : la colonne a changé d'unité, une colonne a été ajoutée, une valeur interdite est apparue. Il est alors plus dangereux que pas de dictionnaire du tout, parce qu'il inspire confiance. Un dictionnaire se **vérifie** comme le reste : par un test automatique, rejoué à chaque réception de fichier.

La fonction `verifier_dictionnaire` compare un tableau à son dictionnaire et liste les écarts : colonne absente du dictionnaire ou du fichier, type différent, valeur hors domaine, colonne obligatoire vide. Sur le fichier tel que nous l'avons décrit, tout est en règle ; puis nous le **dégradons** exprès de quatre façons pour voir ce que le test attrape.

```python
print("profil_clients :", O.verifier_dictionnaire(profil, dico) or "aucune anomalie")
profil2 = profil.assign(segment="A").drop(columns="minutes_site")
profil2["age"] = profil2["age"].astype(float)
profil2.loc[0, "canal_acquisition"] = "Magasin"
for a in O.verifier_dictionnaire(profil2, dico):
    print("-", a)
```
<!--sortie-->
```text
profil_clients : aucune anomalie
- colonne absente du dictionnaire : segment
- type de age : attendu int64, trouvé float64
- canal_acquisition : 1 valeurs hors domaine (Boutique|Site|Réseaux)
- colonne du dictionnaire absente du fichier : minutes_site
```

Les quatre dégradations ont été détectées : une colonne apparue, une colonne disparue, un type qui a glissé et une valeur inconnue. Aucune de ces anomalies ne fait planter un calcul, et toutes peuvent fausser un résultat sans qu'on s'en aperçoive. Le même test, appliqué au CRM brut, vérifie son dictionnaire cette fois-ci contre **de vrais défauts**.

```python
crm_dico = O.dico_complet(crm, "crm_clients")
for a in O.verifier_dictionnaire(crm, crm_dico):
    print("-", a)
```
<!--sortie-->
```text
- ville : 2808 valeurs hors domaine (20 valeurs permises)
- consentement_marketing : 2428 valeurs hors domaine (oui|non)
- consentement_marketing : 2161 valeurs vides alors que la colonne est obligatoire
```

Ici, le dictionnaire est **juste** (ce qu'on attend d'une ville, d'un consentement), et c'est **le fichier** qui ne le respecte pas : 2 808 villes écrites autrement que « Ville A » à « Ville T » (casse, faute, arabe), 2 428 consentements écrits autrement que « oui » ou « non » (`O`, `1`, `TRUE`, `OUI`…), et 2 161 consentements vides. Le test n'est pas un reproche fait aux données, c'est le **cahier des charges du nettoyage** : exactement ce que le chapitre 1 va corriger.

On branche ce test à la chaîne de traitement de façon qu'il l'arrête quand le fichier ne respecte plus son contrat.

```python
anomalies = O.verifier_dictionnaire(df, dico)
assert not anomalies, "\n".join(anomalies)     # la construction s'arrête : le fichier ne respecte plus son dictionnaire
```

> ⚠️ **Piège.** Un test qui échoue **sans rien bloquer** est un témoin que personne n'entend. Décidez à l'avance ce que l'échec fait : arrêter la chaîne, envoyer un message, ou classer le fichier en quarantaine. Un contrôle qui ne déclenche rien est une décoration.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4, exercice 4.8.

### 4.2.6 Dictionnaire et glossaire métier : une définition unique

Le dictionnaire dit ce que contient une **colonne**. Mais bien des désaccords ne portent pas sur une colonne : ils portent sur un **mot**. Qu'est-ce qu'un « client actif » ? Une « commande annulée » ? Un « panier moyen » ? Chacun a sa définition, et les chiffres divergent sans que personne n'ait fait d'erreur — nous l'avons vu avec les quatre chiffres de l'introduction.

Prenons « client actif ». Trois définitions raisonnables, sur les mêmes commandes, au 31 décembre 2025.

```python
ref = pd.Timestamp("2025-12-31")
cmd["jour"] = pd.to_datetime(cmd["date_commande"])
def actifs(jours, mini=1):
    r = cmd[cmd["jour"] > ref - pd.Timedelta(days=jours)]
    return int((r.groupby("id_client").size() >= mini).sum())
print("au moins 1 commande sur 12 mois :", actifs(365))
print("au moins 1 commande sur 6 mois  :", actifs(183))
print("au moins 2 commandes sur 12 mois:", actifs(365, 2))
print("clients inscrits                :", len(O.charger("clients")))
```
<!--sortie-->
```text
au moins 1 commande sur 12 mois : 3875
au moins 1 commande sur 6 mois  : 3148
au moins 2 commandes sur 12 mois: 2654
clients inscrits                : 6000
```

Selon la définition, la boutique a **2 654, 3 148 ou 3 875 clients actifs**, sans compter les 6 000 inscrits. L'écart entre la première et la dernière est de **plus de 1 200 clients**, soit près d'un tiers. Une campagne budgétée « par client actif » coûterait près de moitié plus cher (3 875 contre 2 654 clients) selon qui a rédigé la définition. D'où le **glossaire métier** : un document court qui donne **une définition par mot**, avec son calcul exact.

| Terme | Définition retenue | Calcul | Contre-exemple |
|---|---|---|---|
| **Client actif** | client ayant passé au moins une commande payée au cours des 12 derniers mois | `id_client` distincts dans les commandes du 01/01 au 31/12 | un client inscrit sans commande n'est pas actif |
| **Commande annulée** | commande dont le statut est `cancelled` après normalisation de la casse ; **exclue** du chiffre d'affaires et du nombre de commandes | `lower(status) = 'cancelled'` | une commande retournée n'est pas annulée : elle a été livrée |
| **Panier moyen** | chiffre d'affaires **TTC remises déduites** divisé par le nombre de commandes **distinctes**, calculé sur le total | `SUM(montant) / COUNT(DISTINCT id_commande)` | la moyenne des paniers moyens des canaux n'est pas le panier moyen |
| **Trimestre** | trimestre civil : T4 = du 1er octobre au 31 décembre inclus | `date >= '2025-10-01' AND date <= '2025-12-31'` | une extraction arrêtée le 15/12 n'est pas un trimestre |

On voit la même chose avec la **commande annulée** : dans l'export brut du site, le statut s'écrit de **trois manières** selon l'origine de la ligne.

```python
so = O.charger("site_commandes")
print(so["status"].value_counts().to_dict())
```
<!--sortie-->
```text
{'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186}
```

Trois écritures du même mot « payée » (`paid`, `PAID`, `Paid`) et 186 lignes `cancelled`. Une règle qui compterait « les commandes dont le statut vaut `paid` » ne verrait que 3 629 commandes sur 6 073 payées, soit **60 %** : près de **40 %** des commandes payées disparaîtraient du chiffre d'affaires. C'est le dictionnaire qui doit dire que le statut a deux modalités **après normalisation**, et le glossaire qui dit que l'annulée est exclue.

> 💡 **Intuition.** Le dictionnaire dit **ce qu'il y a dans le fichier** ; le glossaire dit **ce que veulent dire les mots de l'entreprise**. Sans le second, deux analystes qui lisent parfaitement le premier peuvent encore annoncer deux chiffres différents.

Trois règles pour qu'un glossaire serve.

1. **Un mot, une définition, un propriétaire.** La personne qui peut trancher en cas de désaccord est nommée.
2. **Le calcul écrit à côté de la phrase.** « Client actif » ne suffit pas ; `COUNT(DISTINCT id_client)` sur une période précise, si.
3. **Les mots changent, pas leur historique.** Si l'on redéfinit « client actif » (de 12 à 6 mois), on **conserve** l'ancienne définition dans une version antérieure et l'on recalcule les anciens chiffres, sans quoi la courbe saute.

### 4.2.7 Trois dictionnaires pour la boutique

Rassemblons ce que nous venons de construire pour trois jeux : le référentiel `clients`, le référentiel `produits` et le CRM brut. Le tableau compte, pour chacun, les colonnes, celles qui sont sensibles, celles qui sont obligatoires, celles dont les valeurs sont **listées** (un domaine), et celles qui ont des manquants.

```text
        jeu  colonnes  sensibles (personnelles ou indirectes)  confidentielles  obligatoires  domaine listé  avec manquants
    clients         8                                       5                0             8              4               0
   produits         7                                       0                1             7              1               0
crm_clients        11                                       9                0             7              3               3
```

Le CRM est de loin le jeu le plus **sensible** : 9 colonnes sur 11 sont des données personnelles ou permettent de les retrouver. Le référentiel `produits` n'a aucune donnée personnelle, mais son `cout_achat` est **confidentiel** pour l'entreprise : le dictionnaire doit le dire pour qu'on ne le publie pas par mégarde. Et c'est le CRM encore qui a **trois colonnes avec des manquants**, que l'équipe devra décider de traiter ou d'accepter. Ce tableau est le début d'un **inventaire** des données de l'entreprise : on y voit où se trouvent les risques et les travaux à venir.

### 4.2.8 Faire vivre le dictionnaire : versions et changements

Un dictionnaire n'est jamais « terminé » : les colonnes évoluent, les unités changent, des modalités apparaissent. Ce qui compte est de **suivre** ces changements au lieu de les subir. Deux habitudes suffisent.

**Un journal des changements** (*change log*) en tête du dictionnaire : à chaque modification, la date, le changement, la raison et le nom de la personne. Par exemple : « 2025-09-15 : `total` passe de l'euro au centime (changement de la plateforme du site) ; ancienne valeur : euros ». C'est ce qui permet, six mois plus tard, de comprendre pourquoi une série **saute** à une date précise.

**Un numéro de version qui dit la gravité du changement.** On distingue deux sortes de modifications.

| Type de changement | Exemple | Effet sur les analyses existantes | Version |
|---|---|---|---|
| **Compatible** | ajouter une colonne, préciser un libellé, ajouter une modalité à une catégorie | aucun : les analyses d'hier tournent toujours | 1.1 → 1.2 |
| **Incompatible** | changer l'unité d'une colonne, renommer ou supprimer une colonne, redéfinir un mot du glossaire | les analyses d'hier peuvent donner un résultat **faux** sans erreur visible | 1.2 → **2.0** |

Un changement **incompatible** se **prévient**, avant qu'il n'arrive : qui lit cette colonne ? (le lignage de colonnes de la section 4.3 répond), qui doit adapter son calcul ? À partir de quand ? Le test automatique de la section 4.2.5 attrape les changements incompatibles **après** coup ; le journal des changements et le lignage permettent de les **anticiper**.

> 💡 **Intuition.** Un dictionnaire est comme la notice d'un appareil : utile surtout quand l'appareil change. Sa valeur se mesure à la facilité avec laquelle on retrouve **ce qui a changé et quand**.

> ✅ **À retenir.** Un dictionnaire décrit chaque colonne (**libellé, type technique et logique, unité, valeurs permises, caractère obligatoire, codage des manquants, règle ou source, sensibilité**) ; on en fabrique un **squelette automatique** (types, manquants, distincts, bornes, exemple) qu'on **enrichit à la main** ; on le range à côté du fichier, en CSV ou en YAML ; on le **vérifie par un test** qui arrête la chaîne ; et on le complète par un **glossaire** qui donne **une définition unique** de chaque mot de l'entreprise : sur les mêmes commandes, « client actif » vaut 2 654, 3 148 ou 3 875.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.3 à 4.5, exercices 4.6 à 4.9.


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

```yaml
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


## Bilan du chapitre 4

Vous savez maintenant :

- **expliquer pourquoi on documente** (refaire, comprendre, auditer, transmettre) et **reconnaître ce qui manque** quand un chiffre ne se retrouve pas : la source, la date d'extraction, le périmètre, la taxe, les remises, la définition des mots ;
- **remplir la fiche d'un jeu de données** (source, date d'extraction, périmètre, grain, clé, contenu, limites connues, version, propriétaire, droits) et savoir pourquoi le **grain** et la **source** en sont les deux rubriques décisives ;
- **tenir le journal d'un nettoyage** : une règle, une justification, des effectifs avant et après, les lignes retirées et modifiées, une empreinte du résultat, et le **faire écrire par le code** ; vérifier l'**équation de conservation** (lignes lues − lignes retirées = lignes finales) ;
- **juger un nettoyage** autrement que sur la foi de son propre journal : un journal le rend **contestable**, une vérité (quand on en a une) le **mesure** ;
- **ranger la documentation** : README, commentaires qui disent *pourquoi*, noms de fichiers datés et versionnés, brut jamais modifié, une commande qui refait tout, et un test de reproductibilité par les empreintes ;
- **construire un dictionnaire de données** : un squelette automatique (types, manquants, valeurs distinctes, bornes, exemple) enrichi à la main (libellé, unité, valeurs permises, obligatoire, codage des manquants, règle ou source, sensibilité), rangé à côté du fichier en CSV ou en YAML ;
- **vérifier qu'un dictionnaire reste vrai** par un test automatique qui arrête la chaîne, et s'accorder sur **une définition unique** des mots de l'entreprise grâce à un glossaire ;
- (en option) **dessiner un lignage** au niveau des fichiers et des colonnes, remonter en amont et mesurer l'impact en aval, **prouver qu'un fichier n'a pas changé** par son empreinte, tenir un **journal d'audit**, **versionner** une livraison par un manifeste et **rejouer un chiffre depuis le brut**.

Le chapitre a mis des chiffres sur des idées qui restent souvent abstraites. Tous viennent de calculs réellement exécutés sur les données de la boutique :

| Question | Résultat mesuré |
|---|---|
| Un même « chiffre d'affaires du T4 pour le Site », quatre calculs honnêtes | 211 434 € (TTC), 176 195 € (HT), 214 993 € (avant remises), 166 108 € (extraction arrêtée au 15/12) |
| Journal du nettoyage du CRM | 7 140 lignes lues, 140 de test et 677 doublons d'e-mail retirés, **6 323** lignes finales (équation de conservation vérifiée) |
| Ce que ce nettoyage a réellement accompli (vérité) | les 140 lignes de test sont toutes bien retirées ; sur 677 doublons retirés, 674 sont vrais et **3** sont des fusions à tort ; **326** vrais doublons restent ; 5 997 clients distincts sur 6 000 |
| Reproductibilité | deux exécutions depuis le brut : mêmes empreintes à chaque étape |
| Le dictionnaire de `profil_clients` face à un fichier dégradé | 4 anomalies détectées sur 4 (colonne ajoutée, colonne disparue, type glissé, valeur hors domaine) |
| Le dictionnaire du CRM face au CRM brut | 2 808 villes hors domaine, 2 428 consentements hors domaine, 2 161 consentements vides alors qu'ils sont obligatoires |
| Combien de « clients actifs » ? | **2 654**, **3 148** ou **3 875** selon la définition (sur 6 000 inscrits) |
| Statut des commandes du site, avant normalisation | `paid` : 3 629 ; `PAID` : 1 537 ; `Paid` : 907 ; `cancelled` : 186 : filtrer sur `paid` ferait perdre 40 % des commandes payées |
| Lignage de la synthèse du T4 | 9 éléments en amont du message, 4 sources ; modifier `produits` touche 4 éléments |
| Rejouer le chiffre du Site depuis le brut | 211 433,79 € sur 4 911 lignes, avec contrôle des empreintes |

Le fil conducteur du chapitre tient en une phrase : **un chiffre est une conclusion, sa documentation est la preuve**. Presque tous les désaccords d'analyse — « elle ne retrouve pas mon chiffre » — viennent de ce qui n'a pas été écrit : une taxe, un filtre, une définition, une date. On ne documente pas par scrupule, on documente pour que le chiffre **survive** à celui qui l'a produit.

> ⚠️ **Rappel d'honnêteté.** Aucun des outils de lignage ou de catalogue évoqués en 4.3.7 n'a été exécuté ici : ils sont décrits, pas démontrés. Le CRM, les commandes et les profils sont **simulés** ; la « vérité » qui a servi à juger le nettoyage du CRM n'existe pas dans un cas réel, où l'on dispose seulement du journal.

Le chapitre 5 ferme le volume par une question qui touche toute la documentation que nous venons de construire : une colonne marquée **« sensible »** dans un dictionnaire change ce que l'on a le droit de **garder, partager et publier**. C'est le sujet de la **confidentialité et de l'anonymisation des données**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (fiche d'un jeu, journal d'un nettoyage, dictionnaires, test de dictionnaire, glossaire, lignage, empreintes, rejouer un chiffre) et exercices 4.1 à 4.12.

