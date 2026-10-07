# Introduction : pourquoi l'essentiel du travail se fait avant l'analyse

> « Une analyse juste sur des données fausses est une erreur bien rédigée. »

## Trois fichiers, trois questions

Le volume I s'est terminé sur une première analyse : un trimestre comparé à un autre, par canal. Nous avions, pour cela, une base propre : une table de commandes, une table de lignes, une table de clients, tout cela cohérent, typé, relié par des identifiants. **La gérante vous annonce un lundi matin que ce n'est pas la situation ordinaire.** Elle pose sur votre bureau l'essentiel de ce que l'entreprise sait vraiment d'elle-même, et ce sont des fichiers qui ne se parlent pas :

- **la caisse** de la boutique, exportée chaque mois par un logiciel qui a changé de réglages au fil de l'année ;
- **le site web**, dont la plateforme fournit un export des commandes, avec ses propres statuts, ses propres formats et quelques surprises ;
- **le fichier clients** (le CRM), alimenté depuis la caisse, le site et des imports, par plusieurs personnes, sans règle commune ;
- **le catalogue du fournisseur**, qui désigne les mêmes articles par d'autres codes et d'autres noms ;
- **un tableur de stocks**, saisi à la main, avec des titres, des cellules fusionnées, des « ND » et des « rupture » dans les colonnes de chiffres.

Elle vous pose trois questions très simples :

1. **« Combien avons-nous de clients ? »**
2. **« Combien le Site a-t-il vendu cette année ? »**
3. **« Quels articles sont en rupture, et d'où viennent-ils ? »**

Ces questions n'ont l'air de rien. Pourtant, **chacune a une mauvaise réponse facile à obtenir**, et c'est précisément ce que ce volume vous apprend à éviter. Nous allons voir deux de ces mauvaises réponses tout de suite : elles montrent mieux que n'importe quel exposé ce qui est en jeu.


## La mauvaise réponse facile

### Combien de clients ? Le fichier en compte 7 140

Le fichier du CRM est un tableau. La réponse qui vient à l'esprit est le nombre de lignes. Regardons.

```python
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str)
print(len(crm), "lignes ;", crm["email"].nunique(), "adresses e-mail différentes")
```
<!--sortie-->
```text
7140 lignes ; 6353 adresses e-mail différentes
```

```text
clients réels : 6000 | lignes de test : 140 | lignes en double : 1000
part de lignes en trop : 19.0 %
doublons exacts (toutes colonnes sauf l'identifiant, hors lignes de test) : 0
```

La réponse « 7 140 clients » est **fausse**, et compter les adresses de messagerie différentes (6 353) ne la corrige pas : une même personne apparaît parfois **deux ou trois fois**, avec son nom en majuscules, sans accents, avec une faute de frappe, son prénom réduit à une initiale, ou son nom et son prénom inversés ; son e-mail est tantôt présent, tantôt en majuscules, tantôt absent. S'y ajoutent des **lignes de test** laissées par l'équipe du site. La vérité (que nous avons programmée et que nous n'ouvrirons qu'à la fin des études, comme le fait un correcteur) est de **6 000 clients réels** : le fichier compte donc 19 % de lignes en trop. Et aucune des lignes en double n'est **identique** à l'originale : une recherche de doublons exacts n'en trouve aucun parmi les lignes réelles. Il faudra un travail plus fin, celui du chapitre 1 (section 1.3) puis du chapitre 2 (section 2.5).

### Combien le Site a-t-il vendu ? L'export répond 25 millions d'euros

L'export de la plateforme web contient une ligne par commande, avec un montant total écrit en texte (`« 34,92 € »`, `« 195.40 »`, `« 1 245,00 »`). On le convertit en nombre et on additionne.

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str)
site["montant"] = (site["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", ".")).astype(float)
print(len(site), "commandes ;", round(site["montant"].sum(), 2), "€")
```
<!--sortie-->
```text
6259 commandes ; 25012599.35 €
```

Voilà **25 millions d'euros** de chiffre d'affaires pour le Site en 2025. Or toute l'enseigne, tous canaux confondus, a réalisé environ 1,3 million d'euros cette année-là. Le chiffre est absurde, et c'est heureux : une erreur qui saute aux yeux se corrige. Pour la comprendre, regardons le total mensuel.

```text
avant le 15 septembre : médiane d'une commande 82.93 € | après : 7808.0
CA brut par mois (k€) : {1: 42, 2: 35, 3: 43, 4: 44, 5: 49, 6: 51, 7: 55, 8: 38, 9: 3138, 10: 5781, 11: 6581, 12: 9156}
lignes d'export à partir du 15 septembre : 2518 sur 6259
```

À partir du **15 septembre**, la plateforme exprime le total **en centimes** (le fichier ne le dit pas et personne ne l'a annoncé) : une commande de 78 € devient `7800`. Avant cette date, la médiane d'une commande est de 82,93 € ; après, elle est de 7 808, soit près de cent fois plus. En divisant par cent les montants postérieurs au 15 septembre, on retrouve des ordres de grandeur sensés, mais l'histoire n'est pas finie : le fichier contient aussi des **commandes de test**, des **commandes en double** (l'export a été relancé après une panne) et des commandes **annulées**. Rien de tout cela ne ressemble à un défaut d'ordre technique : ce sont des décisions à prendre.


Après avoir converti les centimes, retiré les 60 commandes de test et les 121 lignes d'export en double, il reste **6 078 commandes** pour **617 715,45 €** : très exactement ce que contient la base du volume I pour le Site en 2025. Le chiffre est juste, et on le sait parce qu'on dispose d'une vérité ; dans la vie réelle, on n'en a pas, et c'est pourquoi nous apprendrons à **contrôler** un résultat par recoupement (chapitre 3) plutôt que par la vérité.

Reste une décision : parmi ces 6 078 commandes, **181 sont annulées** (17 551,32 €). Faut-il les compter dans le chiffre d'affaires ? Cela dépend de la question : « ce que les clients ont commandé » (on les garde), « ce que nous avons encaissé » (on les retire : 600 164,13 €). Aucune des deux réponses n'est fausse, et **le chiffre n'a de sens qu'avec sa définition**.

![Chiffre d'affaires mensuel du Site en 2025, en échelle logarithmique : la courbe brute (orange) bondit d'un facteur cent à partir de septembre à cause du changement d'unité ; la courbe corrigée (bleue) suit la saison.](figures/ch00-site-unite.png)


> 💡 **Intuition.** Les deux erreurs de cette section ne viennent ni d'un calcul faux ni d'une mauvaise fonction : le programme a fait exactement ce qu'on lui demandait. Elles viennent de **données qui ne veulent pas dire ce qu'on croit**. C'est pour cela que la préparation des données n'est pas une corvée qui précède le « vrai » travail : c'est du travail d'analyse, et c'est celui où l'on se trompe le plus facilement sans le voir.

## Le « 80 % » et ce qu'il recouvre

On entend souvent que les analystes passent « 80 % de leur temps à préparer les données ». Soyons honnêtes : **ce chiffre n'est pas une mesure**, c'est une règle de pouce de praticiens, et la part réelle dépend de la qualité des sources, de l'outillage et du type de question. Ce qu'il traduit en revanche est solide : dans la pratique, **préparer, contrôler et documenter prend plus de temps que calculer**, et c'est là que se joue la fiabilité du résultat.

Que recouvre ce travail ? Cinq familles d'activités, qui sont les chapitres de ce volume.

| Activité | Question que l'on se pose | Chapitre |
|---|---|---|
| **Nettoyer** | Que faire des manques, des valeurs absurdes, des doublons et des formats mêlés ? | 1 |
| **Transformer et fusionner** | Comment fabriquer les variables utiles, relier des tables, changer leur forme ? | 2 |
| **Contrôler et réconcilier** | Les données sont-elles de qualité ? Deux sources racontent-elles la même histoire ? | 3 |
| **Documenter** | Un autre analyste comprendra-t-il d'où vient chaque colonne et chaque décision ? | 4 |
| **Protéger** | Qu'a-t-on le droit de montrer, de garder, de partager ? | 5 (➕) |

Le travail est **d'autant plus important qu'il se voit peu** : une analyse brillante sur un fichier mal préparé est pire qu'une analyse modeste sur un fichier sain, parce qu'elle donne une fausse assurance.

## Le cycle : préparer, contrôler, documenter

Le travail de préparation suit un cycle qui revient à chaque nouveau jeu de données. On **inspecte** la source brute (que contient-elle vraiment ?), on la **prépare** (nettoyer, transformer, fusionner), on la **contrôle** (validations, recoupements avec une autre source), et l'on **documente** ce qu'on a fait. Quand un contrôle échoue, on revient à la préparation, ou parfois à la source elle-même (on demande à la personne qui l'a produite). C'est seulement ensuite qu'on **analyse**.

![Le cycle de préparation des données : sources brutes, préparer (nettoyer, transformer, fusionner), contrôler (valider, réconcilier), documenter (dictionnaire, lignage), jeu de données fiable, analyse. Quand un contrôle échoue, on revient à la préparation.](figures/ch00-cycle.png)


Retenez deux propriétés de ce cycle. **Il est itératif** : on ne nettoie pas une fois pour toutes ; chaque contrôle révèle un cas qu'on n'avait pas prévu (c'est ainsi que nous avons trouvé les centimes). **Il est traçable** : chaque transformation doit pouvoir être expliquée et rejouée, sinon le résultat n'est pas reproductible (volume I, introduction).

## Un nettoyage est une suite de décisions défendables

Quand on corrige une donnée, on **prend une décision**, même si elle paraît évidente. Retirer les 60 commandes de test est évident. Compter ou non les 181 commandes annulées ne l'est pas. Remplacer une valeur manquante par la moyenne est un choix qui change les résultats (section 1.6). Fusionner deux fiches clients qui se ressemblent à 90 % est un pari.

Une décision est **défendable** quand elle respecte quatre règles, que nous suivrons tout au long du volume.

1. **Elle est écrite.** Un journal des décisions (une ligne par règle : quoi, pourquoi, combien de lignes touchées) vaut plus qu'une mémoire.
2. **Elle est mesurée.** On sait combien de lignes la règle modifie. Une règle qui touche 0,3 % du fichier et une qui touche 30 % n'ont pas la même importance.
3. **Elle est réversible.** On ne modifie jamais le fichier source : on part de lui à chaque fois, avec un programme qui produit la version propre. La version brute reste disponible.
4. **Elle est défendue face à la question.** Elle se justifie par ce que l'on veut mesurer, pas par le goût de l'analyste.

Voici à quoi ressemble, pour notre exemple, un début de journal.

| Règle | Pourquoi | Lignes touchées |
|---|---|---|
| Diviser par 100 les totaux postérieurs au 15 septembre | la plateforme est passée en centimes | 2 518 |
| Retirer les commandes dont l'e-mail est `test@example.com` | ce sont des essais | 60 |
| Retirer les lignes d'export qui répètent une référence déjà vue | l'export a été relancé | 121 |
| Garder les commandes annulées dans le « chiffre d'affaires commandé », les retirer dans le « chiffre d'affaires encaissé » | deux définitions, deux indicateurs | 181 |

> ⚠️ **Piège.** La décision la plus risquée est celle que l'on ne sait pas avoir prise. Retirer silencieusement les lignes qui « ne passent pas » dans un calcul est une décision, et elle biaise le résultat si ces lignes ne sont pas au hasard (section 1.1). Ce qu'on écarte doit toujours être **compté et dit**.

## Ne pas embellir : l'éthique de la préparation

Une dernière précaution, qui tient de l'honnêteté plus que de la technique. **Nettoyer n'est pas embellir.** On corrige ce qui est manifestement une erreur de saisie ou de format ; on **n'efface pas** une valeur parce qu'elle gêne la conclusion. Trois situations demandent de la vigilance.

- **Les valeurs extrêmes.** Un montant de 9 999 € est probablement un placeholder de saisie ; une grosse commande réelle ne l'est pas. On vérifie auprès de la source avant de retirer quoi que ce soit (section 1.2).
- **Les manques.** Si les clients mécontents répondent moins à l'enquête, en retirer les non-réponses rend le résultat plus flatteur que la réalité (section 1.1).
- **Les personnes.** Fusionner deux fiches clients à tort, c'est attribuer l'historique de quelqu'un à quelqu'un d'autre ; mal anonymiser un fichier, c'est exposer des personnes (chapitre 5).

Dans tous les cas, **la règle est la même que celle du volume I** : un résultat reproductible, sourcé et borné. Le volume II ajoute une exigence : **un résultat qui sait ce qu'on a fait des données**.

## Ce que contient le volume, et comment il prolonge le volume I

Le volume I vous a donné des outils : un tableur, SQL, Python et R, quelques notions de statistique, les types de données et la collecte. **Le volume II les utilise sur des données qui ne sont pas propres**, ce qui change tout : le geste (« joindre deux tables ») est le même, mais il faut d'abord savoir si les clés sont les mêmes, si elles sont uniques, si elles ont le même format. Vous retrouverez donc, avec un autre regard, `merge`, les jointures SQL, les formules de recherche et Power Query. Chaque fois qu'une notion du volume I est nécessaire, nous la citons (« volume I, section 4.3 ») sans la répéter.

| Chapitre | Question de la gérante | Contenu |
|---|---|---|
| **1. Nettoyage des données** | « Pourquoi ce fichier de clients ne tombe-t-il pas juste ? » | valeurs manquantes, aberrantes, doublons, formats ; ➕ texte, dates et encodage, imputation |
| **2. Transformation et fusion** | « Comment relier la caisse, le site et le fournisseur ? » | variables dérivées, jointures, agrégation, restructuration ; ➕ pivot, rapprochement approximatif |
| **3. Qualité et réconciliation** | « Les chiffres de la caisse et du site disent-ils la même chose ? » | dimensions de la qualité, contrôles de validation, réconciliation ; ➕ rapports d'exceptions, pandera et Great Expectations |
| **4. Documentation** | « Et si une autre personne reprend ce travail dans six mois ? » | documenter, dictionnaire de données ; ➕ lignage et pistes d'audit |
| **5. Confidentialité** (➕) | « Puis-je envoyer ce fichier à un prestataire ? » | données personnelles, pseudonymisation, k-anonymat, bonnes pratiques |
| **Projet (cahier)** | « Je veux un fichier clients et un chiffre d'affaires fiables » | nettoyer et réconcilier deux sources désordonnées |

> ✅ **À retenir.** La préparation des données n'est pas un préalable ennuyeux : c'est l'endroit où l'on décide ce que veulent dire les chiffres. Une donnée n'est « propre » que **par rapport à une question** ; chaque correction est une **décision** qu'il faut écrire, mesurer et pouvoir défendre ; et un nettoyage honnête corrige les erreurs sans embellir la réalité. La section suivante décrit les fichiers désordonnés du volume et l'environnement de travail.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : un mini-diagnostic de huit questions (repérer des problèmes de qualité, manque ou zéro, doublon exact ou flou, jointure qui multiplie les lignes, date ambiguë, valeur aberrante, encodage, changement d'unité), avec corrigés, pour savoir où revenir avant de commencer.


# Carte du volume, données et environnement

Cette section ouvre le volume par quatre choses : la **carte des chapitres**, le **catalogue des sources désordonnées** (avec, pour chacune, ce qui cloche), le mode d'emploi des **fichiers de vérité**, et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à une question de la gérante. Les chapitres se lisent dans l'ordre, mais on peut les prendre séparément ; les sections marquées ➕ sont facultatives, et le chapitre 5 tout entier est complémentaire.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Nettoyage des données** | Pourquoi ce fichier ne tombe-t-il pas juste ? | valeurs manquantes, valeurs aberrantes, doublons, incohérences de format ; ➕ texte, dates, encodage, données multilingues ; ➕ imputation et son impact |
| **2. Transformation et fusion** | Comment relier la caisse, le site, le fournisseur ? | variables dérivées, jointures, agrégation et restructuration ; ➕ pivot et dépivot ; ➕ rapprochement approximatif |
| **3. Qualité et réconciliation** | Les chiffres de deux sources disent-ils la même chose ? | dimensions de la qualité, contrôles de validation, réconciliation ; ➕ règles, seuils, rapports d'exceptions ; ➕ pandera et Great Expectations |
| **4. Documentation** | Qui comprendra ce travail dans six mois ? | documenter les jeux de données et les transformations, dictionnaire de données ; ➕ lignage et pistes d'audit |
| **➕ 5. Confidentialité et anonymisation** | Puis-je partager ce fichier ? | données personnelles, pseudonymisation, k-anonymat, bonnes pratiques |
| **Projet du volume (cahier)** | Je veux un fichier clients et un chiffre d'affaires fiables | nettoyer et réconcilier deux sources désordonnées |

## Les sources désordonnées du volume

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a2.py`. Il part de la base propre du volume I (la boutique, ses clients, ses commandes) et **fabrique des sources désordonnées**, comme celles que l'on reçoit dans la vie réelle, en y injectant des défauts connus. Les noms de personnes sont inventés, sans origine particulière, et les adresses de messagerie utilisent des domaines réservés aux exemples. Aucune donnée ne vient d'une entreprise réelle.


| Fichier | D'où il vient | Ce qui cloche | Lignes | Chapitres |
|---|---|---|---|---|
| `crm_clients.csv` | le fichier clients, alimenté par la caisse, le site et des imports | doublons flous, lignes de test, formats de date et de téléphone mêlés, codes postaux amputés, villes écrites de six façons, texte abîmé | 7 140 | 1, 2, 3, 5, projet |
| `site_commandes.csv`, `site_lignes.csv` | export de la plateforme web (Site, 2025) | commandes en double, de test, annulées ; montants en texte ; changement de format de date et **d'unité** | 6 259 ; 13 928 | 1, 2, 3, projet |
| `caisse/caisse_2025-01.csv` … `-12.csv` | export mensuel de la caisse de la boutique | **dérive de schéma** : encodage, séparateur, décimale, noms de colonnes, format de date ; titres, en-têtes répétés, total, montants vides, lignes doublées | 12 fichiers | 1, 2, 3, projet |
| `catalogue_fournisseur.csv` | catalogue d'un fournisseur | autres codes, désignations réécrites, produits en plus et en moins | 118 | 2, 3 |
| `stocks_tableur.xlsx` | tableur saisi à la main | titres, cellules fusionnées, sous-totaux, mois en colonnes, « ND », « rupture », nombres en texte | 1 feuille | 2 |
| `profil_clients.csv` | fichier de profils (âge, revenu estimé, dépenses, satisfaction) | valeurs **manquantes** de trois natures différentes | 6 000 | 1 |
| `montants_saisis.csv` | saisie de montants de lignes de commande | valeurs aberrantes : décimale décalée, signe, zéro, 9 999 | 6 000 | 1, 3 |
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv` | la base propre du volume I | (copies, pour recouper) | 6 000 ; 120 ; 36 395 ; 83 905 | tous |

### Le fichier clients : un CRM alimenté par trois sources

Le CRM (*customer relationship management*, la base des contacts) compte 7 140 lignes pour 6 000 clients réels.

| Colonne | Contenu | Ce qu'on y trouve |
|---|---|---|
| `id_crm` | numéro de ligne du CRM | **pas** un identifiant de client : un client peut avoir plusieurs lignes |
| `prenom`, `nom` | identité | majuscules, accents retirés, fautes, initiales, inversions, espaces |
| `email` | adresse | absente, en majuscules, malformée |
| `telephone` | numéro | cinq présentations |
| `ville`, `code_postal` | adresse | variantes d'orthographe, ville en arabe, code sans son zéro initial, absent |
| `date_naissance`, `date_inscription` | dates | quatre formats de naissance, dont des dates impossibles ; inscription en `jj/mm/aaaa` |
| `consentement_marketing` | accord pour les messages commerciaux | sept façons de l'écrire |
| `source_saisie` | `caisse`, `site` ou `import` | peut expliquer la façon d'écrire |

```text
lignes : 7140 | e-mails absents : 231 (3.2%) | codes postaux absents : 424 | de moins de 5 chiffres : 199
formats de naissance : {'xx/xx/aaaa': 4674, 'aaaa-mm-jj': 1749, 'texte': 717}
graphies de ville : 119 pour 20 villes ; 191 en arabe
consentement : {'oui': 2411, '(vide)': 2161, 'Oui': 703, '1': 687, 'O': 369, 'TRUE': 338, 'OUI': 331, 'non': 140}
présentations du téléphone : 5 | noms abîmés (« Ã ») : 213
source de saisie : {'caisse': 3507, 'site': 2965, 'import': 668}
```

Les 119 graphies de ville pour 20 villes, les cinq formats de téléphone et les sept écritures du consentement donnent une idée de ce qu'est un champ saisi par plusieurs mains. Notez le nombre de dates écrites `xx/xx/aaaa` : pour la plupart, on lit « jour/mois », mais **pas pour toutes** (certaines lignes saisies sur le site écrivent « mois/jour »), et c'est un piège que nous rencontrerons à la section 1.4.

### L'export du site web

La plateforme exporte une ligne par commande (`site_commandes.csv`) et une ligne par article (`site_lignes.csv`), avec des noms de colonnes en anglais.

| Colonne | Contenu | Ce qu'on y trouve |
|---|---|---|
| `order_ref` | référence de la commande (`WEB-023450`) | répétée quand l'export est relancé |
| `created_at` | date et heure | `2025-03-04 14:22:05` (sans fuseau) jusqu'au 14 septembre, `2025-09-16T14:22:05Z` (en UTC) ensuite |
| `status` | statut | `paid`, `PAID`, `Paid`, `cancelled` |
| `customer_email`, `customer_name` | client | en majuscules, avec espaces, ou `test@example.com` |
| `total`, `currency` | montant et devise | texte (`34,92 €`, `195.40`, `1 245,00`), **en centimes** depuis le 15 septembre ; `EUR`, `eur`, `€` |
| `promo_code`, `shipping_mode` | code promotionnel, livraison | vides pour « aucun » |
| (lignes) `sku`, `qty`, `unit_price`, `discount_pct` | article, quantité, prix, remise | le `sku` s'écrit `P043` : le code produit de la boutique, sans le zéro de gauche |

```text
commandes (lignes d'export) : 6259 | références distinctes : 6138 | lignes d'articles : 13928
statuts : {'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186} | devises : {'EUR': 4987, 'eur': 643, '€': 629}
présentations du total : {'entier': 2494, 'point': 1510, 'euro': 1476, 'virgule': 779} | promo absente : 84.2%
```

### Les exports de caisse : douze fichiers, trois réglages

L'export de la caisse est produit chaque mois, mais **le logiciel a changé de réglages deux fois dans l'année**. Concaténer les douze fichiers sans précaution échoue ou donne des colonnes mélangées.

| Mois | Encodage | Séparateur | Décimale | Colonne des quantités | Date | Colonnes |
|---|---|---|---|---|---|---|
| janvier à juin | `cp1252` (Windows) | `;` | virgule | `Qté` | `jj/mm/aaaa` | 8 |
| juillet à septembre | UTF-8 avec marque BOM | `;` | virgule | `Quantité` | `jj/mm/aa` | 8 |
| octobre à décembre | UTF-8 avec marque BOM | `,` | point | `Qté` | `jj/mm/aaaa` | 9 (une colonne `Remise (%)` en plus) |

Chaque fichier commence par trois lignes de titre, répète son en-tête toutes les soixante lignes (le « changement de page »), se termine par une ligne de total, comporte quelques montants vides et, parfois, une ligne répétée par un double passage en caisse.

```text
réglages distincts : 3
('cp1252', ';', 8) → mois 01, 02, 03, 04, 05, 06
('utf-8', ';', 8) → mois 07, 08, 09
('utf-8', ',', 9) → mois 10, 11, 12
lignes de fichier au total : 12943
```

### Le catalogue du fournisseur et le tableur de stocks

Le **catalogue du fournisseur** décrit les articles par un code `F-xxxx` et une désignation réécrite (casse, accents, abréviations, ordre des mots, quelques mots anglais). Il manque 12 produits de la boutique, et 10 articles du fournisseur ne sont pas à la boutique. Attention à un détail hérité du volume I : **la boutique compte 120 produits mais seulement 60 noms distincts**, parce que chaque nom est porté par deux produits à prix différents. La désignation seule ne suffit donc pas à rapprocher les deux listes : il faudra s'aider du prix (sections 2.2 et 2.5).

Le **tableur de stocks** est une feuille « à la main » : un titre, une phrase de consigne, une ligne d'en-têtes, puis les catégories en cellules fusionnées, les produits (un par ligne, les douze mois en colonnes), un sous-total par catégorie avec une formule, et des cellules qui contiennent « ND », un tiret, « rupture » ou un nombre écrit avec une espace.

```text
catalogue : lignes 118 | familles écrites : 12 pour 6 catégories | désignations avec espaces autour : 19
boutique : produits 120 | noms distincts : 60 | noms portés par deux produits : 60
feuille : A1:N141 | cellules fusionnées : 6 | cellules de données : 1512
  « ND » : 49 | tirets : 22 | « rupture » : 120 | nombres écrits en texte avec espace : 131
```

### Les profils clients et les montants saisis

Deux petits jeux servent aux chapitres de nettoyage proprement dit. **`profil_clients.csv`** donne, pour 6 000 clients, l'âge, le revenu annuel estimé, le nombre de commandes et la dépense de 2025, la satisfaction moyenne et le temps passé sur le site ; trois colonnes ont des **trous**, et ils n'ont pas la même origine, ce qui change tout (section 1.1). **`montants_saisis.csv`** reprend 6 000 lignes de commande de 2024 dans lesquelles ont été glissées des anomalies de saisie, que le chapitre 1 apprend à repérer (section 1.2).

```text
profils : manquants par colonne : {'revenu_annuel': 1039, 'depense_2025': 297, 'satisfaction_moy': 562}
part des manquants : {'revenu_annuel': 0.173, 'depense_2025': 0.05, 'satisfaction_moy': 0.094}
montants saisis : lignes 6000 | médiane 31.43 | minimum -153.8 | maximum 26070.0
```

## Les fichiers de vérité

Pour chaque source désordonnée, le script écrit un fichier `verite_*.csv` qui dit **ce qui a été injecté** et ce que la valeur propre aurait dû être.

| Fichier | Ce qu'il contient |
|---|---|
| `verite_crm.csv` | pour chaque ligne du CRM, le vrai client, l'indicateur de doublon et les défauts injectés |
| `verite_identites.csv` | l'identité propre de chaque client (prénom, nom, e-mail) |
| `verite_site.csv` | pour chaque référence de l'export du site, la vraie commande, le vrai total et le défaut |
| `verite_caisse.csv` | pour chaque ligne des fichiers de caisse, la vraie ligne de la base et l'indicateur de doublon |
| `verite_produits.csv` | pour chaque code du fournisseur, le vrai produit de la boutique (ou -1) |
| `verite_stocks.csv` | le vrai stock de chaque produit et de chaque mois |
| `profil_clients_verite.csv` | les valeurs complètes, sans trous |
| `verite_montants.csv` | le type d'anomalie et le vrai montant |

> ⚠️ **Piège.** Ces fichiers sont des **corrigés**, pas des données : dans la vie réelle, il n'y a pas de fichier de vérité, et c'est tout l'intérêt de ce volume d'apprendre à **contrôler sans lui** (chapitre 3). On les ouvre à la fin d'une étude pour mesurer ce qu'on a bien et mal fait, comme on regarde le corrigé d'un exercice après l'avoir cherché. Un nettoyage qui s'appuie sur eux pour décider n'a rien démontré.

## L'environnement de travail

### Python, R et SQL

Les calculs du livre sont faits en **Python** (pandas), en **R** (tidyverse) et en **SQL** (SQLite et DuckDB), comme au volume I. Ce volume ajoute des bibliothèques propres à la préparation des données.

| Bibliothèque | À quoi elle sert | Chapitres |
|---|---|---|
| `pandas`, `polars` | lire, nettoyer, transformer | tous |
| `rapidfuzz`, `jellyfish` | mesurer la ressemblance entre deux textes (distance d'édition, Jaro-Winkler) | 2.5 |
| `unidecode`, `ftfy` | retirer les accents ; réparer un texte abîmé par un mauvais encodage | 1.5 |
| `pandera`, `great-expectations` | écrire des contrôles de qualité exécutables | 3.5 |
| `openpyxl`, `XlsxWriter` | lire et écrire des classeurs Excel | 1, 2, 3 |

```text
python 3.13.3 | pandas 3.0.6, numpy 2.5.3, polars 2.0.0, openpyxl 3.1.5
préparation : rapidfuzz 3.14.6, jellyfish 1.2.1, Unidecode 1.4.0, ftfy 6.3.1, pandera 0.34.1, great_expectations 1.24.0
SQLite 3.46.1
R version 4.4.3 (2025-02-28)
```

### Le tableur : Excel, LibreOffice et nos maquettes

Même précision d'honnêteté qu'au volume I. **Excel n'est pas installé** sur la machine qui produit ce livre, mais **LibreOffice Calc** l'est : les formules du livre sont **écrites dans des classeurs, recalculées par LibreOffice et comparées aux résultats de pandas**. Les noms de menus et de fonctions varient avec la version et la langue d'Excel : à vérifier dans la vôtre. Ce qui n'est pas exécutable ici (Power Query et son langage M, tableaux croisés dynamiques réels, macros) est signalé **« non exécuté »**, avec un équivalent calculé en pandas quand c'est possible.

### Les captures d'écran

Les copies d'écran ne sont pas toutes de la même nature, et le livre le dit chaque fois dans la légende :

- les **maquettes** sont dessinées avec matplotlib (comme celles de Power Query ou d'un classeur) ;
- les **captures réelles** sont faites sur des outils libres que l'on exécute ici, avec un navigateur sans interface (par exemple un rapport HTML de Great Expectations) ;
- les **images empruntées** à Internet ne le sont que si leur licence autorise la réutilisation ; elles sont alors créditées dans la légende et dans le fichier `figures/credits.md`. Nous n'utilisons pas de captures prises dans la documentation ou le site d'un éditeur de logiciel commercial.

### Régénérer les données et refaire les calculs

Tout le dossier `donnees/` se régénère à l'identique par un script, et les calculs du livre se rejouent par `make check` (qui vérifie que chaque sortie est inchangée).

```bash
python build/donnees_a2.py        # régénère donnees/ (une dizaine de secondes, graines fixes)
make check                        # rejoue tous les blocs de code et signale toute différence
make pdf                          # reconstruit le livre et le cahier en PDF
```

## Conventions du volume

- **Monnaie, villes, canaux** : montants en **€** ; villes « Ville A » à « Ville T » ; canaux `Boutique`, `Site`, `Réseaux`.
- **Personnes** : tous les noms sont **inventés** ; les adresses de messagerie utilisent des domaines réservés aux exemples (`exemple.org`, `courrier.test`, `mail.example`).
- **Nombres** : à la française dans le texte (espace pour les milliers, virgule décimale), à l'anglaise dans les sorties de programme.
- **Dates** : `aaaa-mm-jj` dans les programmes ; les formats `jj/mm/aaaa` ou `mm/jj/aaaa` sont ceux des fichiers reçus.
- **Aléatoire** : toute simulation fixe sa **graine**.
- **Encadrés** : 💡 intuition · 📐 formule · 🧪 expérience · ⚠️ piège · ✅ à retenir · 🧭 repère ou section facultative · 📒 pour s'entraîner · 📦 données.

> ✅ **À retenir.** Les sources du volume sont **simulées et volontairement désordonnées** : un CRM de 7 140 lignes pour 6 000 clients, un export web qui change d'unité en septembre, douze exports de caisse sous trois réglages, un catalogue fournisseur, un tableur saisi à la main, des profils à trous et des montants à anomalies. Les fichiers `verite_*` sont des **corrigés** à n'ouvrir qu'à la fin. Les formules Excel sont vérifiées avec LibreOffice ; les captures d'écran sont des maquettes, des captures d'outils libres ou des images sous licence libre créditées.
