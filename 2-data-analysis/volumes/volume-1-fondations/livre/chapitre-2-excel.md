# Chapitre 2 : Excel

> « Le tableur est le premier outil de la plupart des analystes, et le dernier dont ils se méfient. »

La gérante de la boutique ouvre un classeur Excel tous les lundis matin. Elle y colle l'export des ventes de la semaine, recalcule à la main les totaux par catégorie, les compare à ceux du mois précédent, puis recopie les chiffres dans un tableau qu'elle envoie à son associé. Elle vous pose aujourd'hui la question que se posent tous les gens qui travaillent ainsi :

> « Peux-tu me dire, **par catégorie et par mois, ce que nous avons vendu en 2025**, sans que je refasse le calcul à la main chaque lundi ? Et peux-tu faire en sorte que je puisse **me fier** aux chiffres ? »

La seconde phrase compte autant que la première. Un tableur est un outil extraordinaire de rapidité : en quelques minutes, on obtient un tableau, un graphique, un chiffre. C'est aussi un outil sans garde-fou : une formule recopiée sur une plage trop courte, un nombre stocké comme du texte, une cellule fusionnée, un total qui ignore les dernières lignes, et personne ne le voit. Ce chapitre vous apprend à la fois **à aller vite** (formules, tableaux croisés dynamiques, Power Query) et **à vérifier** (contrôles, recoupements, bonnes pratiques de structure).

> ⚠️ **Honnêteté sur les outils.** Le livre a été produit sur une machine **sans Excel**. Voici ce que cela change pour vous :
> - **Les formules sont vérifiées**, mais avec **LibreOffice Calc**, un tableur libre qui lit les fichiers Excel (`.xlsx`) et calcule les mêmes fonctions. Chaque résultat chiffré du chapitre a été calculé ainsi, puis **recoupé par un second outil** (pandas ou SQL). LibreOffice et Excel peuvent différer sur des fonctions récentes ou des détails d'affichage : les cas connus sont signalés.
> - **Les formules sont écrites comme dans l'Excel en français** (`SOMME.SI.ENS`, séparateur `;`, virgule décimale). Un tableau de correspondance avec les noms anglais figure en section 2.1.10.
> - **Les « copies d'écran » sont des maquettes dessinées** avec un programme de dessin : elles montrent ce que vous verrez à l'écran, avec des valeurs réellement calculées, mais ce **ne sont pas des captures d'Excel**. Les menus, les libellés et les icônes varient selon la **version** d'Excel et la **langue** : traitez nos descriptions de menus comme des repères, **à vérifier** sur votre poste.
> - **Ce qui n'a pas pu être exécuté** : les tableaux croisés dynamiques réels, Power Query, Power Pivot et le langage DAX, VBA, Office Scripts, Google Sheets et Looker Studio. Ces blocs sont signalés « non exécuté » ; quand c'est possible, le même résultat est **recalculé en pandas ou en SQL** pour que vous puissiez vérifier ce que l'outil devrait donner.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 2.1 | Comment calculer, chercher et nettoyer avec des formules ? | Références, fonctions conditionnelles, recherches, dates, texte, erreurs |
| 2.2 | Comment résumer 30 000 lignes en un tableau ? | Le tableau croisé dynamique, et pourquoi il faut le recouper |
| 2.3 | Comment importer et nettoyer un export désordonné ? | Power Query : des étapes enregistrées et rejouables |
| 2.4 | Comment ne pas se tromper ? | Structure, données propres, contrôles, erreurs célèbres |
| ➕ 2.5 | Que fait Excel au-delà du tableur ? | Modèle de données, DAX, macros, et quand passer à SQL ou Python |
| ➕ 2.6 | Et dans le nuage ? | Google Sheets, Looker Studio, équivalences |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a1.py`) : la boutique, ses clients et ses ventes n'existent pas. La « vérité » du simulateur est documentée en tête du générateur ; nous n'en avons pas besoin ici, mais elle nous permet de savoir que les totaux sont exacts.

- **`ventes_2025.xlsx`**, le classeur de la gérante, contient trois feuilles : `Lignes` (une ligne par article vendu en 2025), `Produits` (le catalogue) et `Clients`.
- **`export_caisse_brut.csv`** est un export de caisse de la boutique physique, tel que la caisse le fournit : désordonné, avec un titre, un total et des formats « à la française ». Il sert à la section 2.3.
- Les autres fichiers du volume (`commandes.csv`, `boutique.db`…) servent dans les chapitres suivants ; nous les utilisons ici pour **recouper** les résultats.


Le classeur de la gérante compte **29 827 lignes** de ventes, réparties en 12 946 commandes passées par 3 875 clients, du 1ᵉʳ janvier au 31 décembre 2025, pour un montant total de **1 324 763,72 €**. La figure suivante montre ce que la gérante voit en ouvrant la feuille `Lignes`.


![La feuille `Lignes` de `ventes_2025.xlsx` : une ligne par article vendu, une colonne par caractéristique (les colonnes D, G, K et L sont masquées pour que la figure reste lisible). Maquette dessinée avec matplotlib, pas une capture d'Excel.](figures/ch02-classeur.png)

Remarquez déjà trois choses, que tout analyste vérifie en ouvrant un classeur inconnu. **Une ligne d'en-tête** unique, sans cellule fusionnée. **Une ligne = une observation** (ici, un article vendu). **Des colonnes homogènes** : une colonne de dates ne contient que des dates, une colonne de montants que des montants. C'est la forme que les outils d'analyse attendent, et nous y reviendrons en section 2.4.2. Les cellules vides de la colonne `code_promo` ne sont pas une erreur : elles signifient « pas de code promo » (25 221 lignes sur 29 827).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1 (explorer et contrôler le classeur).


## 2.1 Formules et fonctions

Une formule Excel est un **petit programme** que l'on écrit dans une cellule : elle commence par `=`, elle lit d'autres cellules et elle affiche un résultat qui se **met à jour tout seul** quand ces cellules changent. Cette section présente les familles de fonctions dont un analyste se sert tous les jours : agréger sous conditions, décider, chercher, nettoyer du texte, manipuler des dates, et comprendre les erreurs. Tous les résultats cités ont été calculés sur le classeur `ventes_2025.xlsx` et **recoupés par pandas** : le bloc suivant (caché dans le livre) le fait une fois pour toutes, et nous n'y reviendrons que pour citer les chiffres.


### 2.1.1 Anatomie d'un classeur et d'une formule

Un **classeur** (le fichier `.xlsx`) contient des **feuilles** ; une feuille est une grille de **cellules** repérées par une lettre (la colonne) et un numéro (la ligne) : `M2` est la cellule de la colonne M, ligne 2. Une **plage** désigne un rectangle de cellules : `M2:M29828` est la colonne des montants, de la ligne 2 à la ligne 29828. Pour parler d'une cellule d'une autre feuille, on préfixe : `Lignes!M2`.

Une cellule contient soit une **valeur** (un nombre, un texte, une date), soit une **formule**. Pour calculer le montant d'une ligne de vente, la formule est `=J2*K2*(1-L2/100)` : le prix unitaire, multiplié par la quantité, multiplié par un moins la remise exprimée en pourcentage. Excel applique les règles de priorité de l'arithmétique : d'abord les parenthèses, puis les pourcentages et les puissances, puis les multiplications et divisions, puis les additions et soustractions, puis la concaténation de texte (`&`), enfin les comparaisons (`=`, `<>`, `<`, `>=`…). **Dans le doute, mettez des parenthèses** : elles ne coûtent rien et se lisent mieux.

Quand vous modifiez une cellule, Excel **recalcule** toutes les formules qui en dépendent (le mode par défaut est le calcul automatique ; la touche `F9` force un recalcul en mode manuel). C'est ce qui fait la force du tableur, et c'est aussi ce qui le rend dangereux : un changement oublié se propage sans bruit.

Faisons le calcul sur toute l'année. Si l'on recalcule chaque ligne par `prix × quantité × (1 − remise)` puis que l'on additionne, on trouve un total **légèrement différent** de la somme de la colonne `montant` :

```text
=SOMME(Lignes!M2:M29828)  →  1 324 763,7200
=SOMMEPROD(Lignes!J2:J29828;Lignes!K2:K29828;1-Lignes!L2:L29828/100)  →  1 324 763,6395
écart : 0,0805 € sur 29 827 lignes
```

L'écart est de **8 centimes** pour 29 827 lignes : la colonne `montant` est arrondie au centime **ligne par ligne** (c'est ce que fait une caisse), alors que le recalcul additionne des produits non arrondis. Ce n'est pas une erreur, mais c'est la première leçon de rigueur : **une somme de valeurs arrondies n'est pas l'arrondi de la somme**. Nous retrouverons ce phénomène en section 2.4.5.

> 💡 **Intuition.** Une formule ne « contient » pas son résultat : elle contient une **recette**. Si vous copiez la recette sur une autre ligne, Excel adapte les ingrédients à la nouvelle ligne. C'est le sujet de la sous-section suivante.

### 2.1.2 Références relatives, absolues et mixtes

Quand on copie la formule `=J2*K2` de la ligne 2 vers la ligne 3, Excel écrit `=J3*K3` : la référence est **relative**, elle se décale avec la formule. Pour qu'une référence **ne bouge pas**, on la fige avec des dollars : `$A$1` est **absolue** (ni la colonne ni la ligne ne changent), `$A1` est **mixte** (la colonne est figée, la ligne se décale) et `A$1` est mixte dans l'autre sens. La touche `F4` fait défiler ces quatre variantes.

| Écriture | Copiée une ligne plus bas | Copiée une colonne plus à droite |
|---|---|---|
| `B2` (relative) | `B3` | `C2` |
| `$B$2` (absolue) | `$B$2` | `$B$2` |
| `$B2` (colonne figée) | `$B3` | `$B2` |
| `B$2` (ligne figée) | `B$2` | `C$2` |

Prenons un exemple où les références mixtes sont indispensables : une table de multiplication, avec les facteurs 1, 2, 3 en ligne 1 et en colonne A. La formule de la cellule `B2` est `=B$1*$A2`. Elle fige la **ligne** du facteur en haut (`B$1`) et la **colonne** du facteur à gauche (`$A2`) : copiée partout, elle fait toujours le produit de l'en-tête de colonne et de l'en-tête de ligne.


![Une table de multiplication avec une seule formule recopiée : `=B$1*$A2`. En colonne et en ligne, les en-têtes (surlignés) restent figés. Maquette dessinée avec matplotlib, valeurs calculées par LibreOffice.](figures/ch02-references.png)

⚠️ **Piège.** La cause la plus fréquente de résultats faux dans un tableur est une **référence qui devait être figée et ne l'était pas** : par exemple une cellule de taux de remise `B1` utilisée dans `=J2*B1`, qui devient `=J3*B2` à la ligne suivante, et multiplie par une cellule vide. Règle : toute cellule de paramètre (un taux, un seuil) est référencée avec des **dollars** ou, mieux, par un **nom** (sous-section suivante).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : exercice 2.1.

### 2.1.3 Plages nommées et tableaux structurés

Écrire `Lignes!$M$2:$M$29828` est exact mais illisible, et fragile : si l'on ajoute une ligne en bas, la plage ne s'étend pas. Deux mécanismes règlent le problème.

La **plage nommée** donne un nom à une plage (menu *Formules → Gestionnaire de noms*, ou la zone de nom à gauche de la barre de formule) : après avoir nommé `Montant` la colonne M, la formule devient `=SOMME(Montant)`. Le nom se lit comme une phrase, et il est stable quand on copie la formule.

Le **tableau structuré** (*Insertion → Tableau*, ou `Ctrl+T`) transforme la plage de données en objet : il reçoit un nom (ici `Ventes`), ses colonnes se citent par leur en-tête (`Ventes[montant]`), et surtout **il grandit tout seul** quand on ajoute des lignes en dessous. Toutes les formules, les tableaux croisés et les requêtes qui s'y réfèrent suivent.

```text
=SOMME(Lignes!M2:M29828)  →  1 324 763,72
=SOMME(Montant)  →  1 324 763,72
=SOMME(Ventes[montant])  →  1 324 763,72
trois écritures, un même total : True
```

Les trois écritures donnent le même total, **1 324 763,72 €**. La différence est ailleurs : elle apparaît le jour où le classeur change. Les tableaux structurés sont la première des bonnes pratiques de la section 2.4.

### 2.1.4 Agréger sous conditions : SOMME.SI.ENS, NB.SI.ENS, MOYENNE.SI.ENS

La plupart des questions d'un analyste commencent par « combien … **pour** … ? ». Trois fonctions y répondent, dans leur version à conditions multiples (le suffixe `.ENS` signifie « ensemble de critères ») :

| Question | Fonction | Syntaxe |
|---|---|---|
| Combien d'euros ? | `SOMME.SI.ENS` | `(plage_à_sommer ; plage_critère1 ; critère1 ; …)` |
| Combien de lignes ? | `NB.SI.ENS` | `(plage_critère1 ; critère1 ; …)` |
| Quelle moyenne ? | `MOYENNE.SI.ENS` | `(plage_à_moyenner ; plage_critère1 ; critère1 ; …)` |

⚠️ La **plage à sommer vient en premier** dans `SOMME.SI.ENS`, alors qu'elle vient **en dernier** dans l'ancienne `SOMME.SI(plage_critère ; critère ; plage_à_sommer)`. Cette inversion est une source d'erreurs classique.

Les critères sont des textes ou des nombres, éventuellement précédés d'un opérateur écrit **entre guillemets** : `"Site"`, `">0"`, `"<>"` (non vide). Pour comparer à une date ou à une cellule, on **concatène** : `">="&DATE(2025;3;1)`. Les jokers `*` (une suite de caractères) et `?` (un caractère) fonctionnent dans les critères de texte.

Voici les réponses à quelques questions de la gérante, calculées par LibreOffice :

```text
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Site")  →  617 715,45
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Boutique")  →  560 973,91
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!E2:E29828;"Réseaux")  →  146 074,36
=NB.SI.ENS(Lignes!L2:L29828;">0")  →  4 606
=MOYENNE.SI.ENS(Lignes!M2:M29828;Lignes!I2:I29828;"Jardin")  →  65,63
=SOMME.SI.ENS(Lignes!M2:M29828;Lignes!I2:I29828;"Jardin";Lignes!C2:C29828;">="&DATE(2025;3;1);Lignes!C2:C29828;"<"&DATE(2025;4;1))  →  14 788,58
=SOMME.SI(Lignes!H2:H29828;"Bougie*";Lignes!M2:M29828)  →  36 833,11
=NB.SI.ENS(Lignes!E2:E29828;"Site";Lignes!I2:I29828;"Décoration";Lignes!C2:C29828;">="&DATE(2025;11;1))  →  971
=NB.SI.ENS(Lignes!M2:M29828;">=100")  →  2 482
```

Lisons-les : le canal **Site** a rapporté 617 715,45 €, la **Boutique** 560 973,91 € et les **Réseaux** 146 074,36 € (ces trois montants s'additionnent bien en 1 324 763,72 € : c'est le premier **contrôle de cohérence** à toujours faire). Sur 29 827 lignes, 4 606 portent une remise ; une ligne de la catégorie Jardin pèse en moyenne 65,63 € ; les ventes de Jardin de mars 2025 valent 14 788,58 € ; les produits dont le nom commence par « Bougie » 36 833,11 € ; le Site a vendu 971 articles de décoration depuis le 1ᵉʳ novembre ; et 2 482 lignes valent 100 € ou plus.

Chacun de ces chiffres a été recoupé par pandas (`groupby`, `sum`, `mean`) : les écarts maximaux sont nuls au centime près. C'est l'habitude à prendre : **un chiffre obtenu par deux chemins indépendants est un chiffre auquel on peut se fier**.

#### Les pièges de l'agrégation conditionnelle

- **Les plages doivent avoir exactement la même taille.** Si l'on écrit `=SOMME.SI.ENS(M2:M29828 ; E2:E29818 ; "Site")` (dix lignes de moins pour le critère), Excel renvoie `#VALEUR!` : ici, LibreOffice l'a confirmé (`#VALEUR!`). C'est un bon signe : l'erreur est **visible**.
- **Une plage trop courte, au contraire, ne dit rien.** `=SOMME(M2:M29028)` oublie les 800 dernières lignes et renvoie 1 291 124,89 € au lieu de 1 324 763,72 € : **33 638,83 € disparus** sans le moindre message. C'est l'erreur la plus courante des classeurs réels, et la raison pour laquelle on préfère les tableaux structurés.
- **Les critères sont sensibles aux détails** : `"Site"` ne trouve pas `"site "` (avec une espace à la fin). Nous verrons comment nettoyer en 2.1.7.
- **Les dates doivent être de vraies dates** : une date stockée comme du texte (`"03/11/2025"`) n'est pas comparée comme une date (2.1.8).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.2, exercice 2.2.

### 2.1.5 Décider : SI, SI.CONDITIONS, ET, OU, SIERREUR

La fonction `SI(test ; valeur_si_vrai ; valeur_si_faux)` renvoie une valeur ou une autre selon un test. Pour ranger un panier dans une taille — « petit » en dessous de 40 €, « moyen » de 40 à 100 €, « gros » à partir de 100 € — on imbrique deux `SI` :

```text
=SI(A2>=100 ; "gros" ; SI(A2>=40 ; "moyen" ; "petit"))
```

La fonction `SI.CONDITIONS` (Excel 2019 et suivants, **à vérifier** selon votre version) évite l'imbrication : `=SI.CONDITIONS(A2>=100 ; "gros" ; A2>=40 ; "moyen" ; VRAI ; "petit")`. Le dernier couple `VRAI ; "petit"` joue le rôle de la valeur par défaut : sans lui, un montant qui ne remplit aucune condition produit `#N/A`.

```text
panier de 12 €     → petit
panier de 45 €     → moyen
panier de 99,90 €  → moyen
panier de 150 €    → gros
SI.CONDITIONS sur 99,90 € → moyen | ET(99,90 ≥ 40 ; 99,90 < 100) → VRAI | OU(12 ≥ 100 ; 150 ≥ 100) → VRAI
```

Les fonctions `ET(…)`, `OU(…)` et `NON(…)` combinent des tests : elles renvoient `VRAI` ou `FAUX`, et se placent à l'intérieur d'un `SI`. L'erreur classique est d'écrire `=SI(40<=A2<100 ; …)`, qui n'est **pas** un test d'intervalle en Excel : il faut `=SI(ET(A2>=40 ; A2<100) ; …)`.

`SIERREUR(formule ; valeur_de_remplacement)` remplace n'importe quelle erreur par une valeur : `=SIERREUR(A6/B6 ; 0)` renvoie 0 quand le dénominateur est nul. Utilisez-la **avec parcimonie** : elle **masque toutes les erreurs**, y compris celles qui révèlent un vrai problème (une référence cassée, un nom mal écrit). Si seule l'erreur « non trouvé » vous intéresse, préférez `SI.NON.DISP(…)`, qui ne traite que `#N/A`.

> ⚠️ **Piège.** Un `SIERREUR` qui renvoie 0 transforme une donnée **manquante** en donnée **égale à zéro**. Sur une moyenne ou une somme, cela fausse silencieusement le résultat. Préférez un message explicite (`"à vérifier"`) ou une cellule vide, et comptez ensuite les erreurs.

### 2.1.6 Chercher : RECHERCHEV, INDEX+EQUIV, RECHERCHEX

Presque toutes les analyses croisent deux tables : ici, les lignes de vente ne contiennent que l'identifiant du produit, et le prix d'achat est dans la feuille `Produits`. Retrouver une information d'une table à partir d'une clé s'appelle une **recherche** (en base de données, une **jointure**, chapitre 3).

**`RECHERCHEV(clé ; table ; n° de colonne ; FAUX)`** cherche la clé dans la **première colonne** de la table et renvoie la valeur de la colonne numéro n. Son quatrième argument est le piège principal : `FAUX` (ou 0) demande la correspondance **exacte** ; `VRAI` (ou omis !) demande la correspondance **approchée**, qui suppose la première colonne **triée** et renvoie la plus grande valeur inférieure ou égale à la clé.

```text
=RECHERCHEV(7;Produits!A2:F121;2;FAUX)  →  Moule mat
=RECHERCHEV(5;Ref!A2:B5;2;FAUX)  →  Cadre design
=RECHERCHEV(5;Ref!A2:B5;2;VRAI)  →  #N/A
=RECHERCHEV(Ref!G2;Ref!E2:F5;2;FAUX)  →  #N/A
=RECHERCHEV(SUPPRESPACE(Ref!G2);Ref!E2:F5;2;FAUX)  →  3
=RECHERCHEV(4;Bareme!A2:B4;2;VRAI)  →  0,05
```

Lisons ces résultats. La clé 7 est trouvée exactement (`Moule mat`). Avec une table **non triée** (identifiants 7, 3, 12, 5), chercher la clé 5 en correspondance exacte donne bien `Cadre design`, mais **la même recherche en mode approché échoue** (`#N/A`) ; dans Excel, selon l'ordre des données, le résultat peut même être **faux sans erreur** : c'est pourquoi il ne faut **jamais oublier le `FAUX`**. Une clé tapée avec une espace de trop (`"Bol design "`) ne se trouve pas (`#N/A`) tant qu'on ne la nettoie pas avec `SUPPRESPACE`. Enfin, la correspondance approchée a un **bon usage** : lire un **barème** trié, comme une remise par palier de quantité (1 → 0 %, 3 → 5 %, 10 → 10 %) ; ici, une quantité de 4 donne 5 %.

Trois autres limites de `RECHERCHEV` : elle **ne regarde qu'à droite** de la colonne clé ; le **numéro de colonne** est écrit en dur, donc **insérer une colonne casse la formule sans prévenir** ; et une clé numérique (`7`) ne correspond pas à la même clé écrite comme du texte (`"7"`) dans Excel (l'erreur est `#N/A` ; LibreOffice, plus indulgent, convertit silencieusement : **le comportement diffère**, nous ne pouvons donc pas le montrer ici et il est à tester dans votre Excel).

**`INDEX` et `EQUIV`** se combinent pour faire mieux : `EQUIV(clé ; colonne_clés ; 0)` renvoie la **position** de la clé, et `INDEX(colonne_résultat ; position)` renvoie la valeur à cette position. La colonne résultat peut être **n'importe où** (à gauche aussi), et rien ne casse si l'on insère une colonne.

**`RECHERCHEX(clé ; colonne_clés ; colonne_résultat ; si_non_trouvé)`** (Excel 2021 et Microsoft 365, **à vérifier** pour les versions antérieures) cumule les avantages : correspondance exacte par défaut, valeur de remplacement intégrée, recherche dans les deux sens.

```text
=INDEX(Produits!B2:B121;EQUIV(7;Produits!A2:A121;0))  →  Moule mat
=RECHERCHEX(7;Produits!A2:A121;Produits!B2:B121;"absent")  →  Moule mat
=RECHERCHEX(999;Produits!A2:A121;Produits!B2:B121;"absent")  →  absent
=RECHERCHEX("Bol design";Produits!B2:B121;Produits!A2:A121;"absent")  →  3
```

La dernière ligne illustre la recherche « à l'envers » : retrouver l'identifiant (3) d'un produit à partir de son nom, ce que `RECHERCHEV` ne sait pas faire.

⚠️ **Mais attention : un nom n'est pas une clé.** La recherche précédente renvoie l'identifiant **3**, la **première** correspondance, sans prévenir qu'il y en a d'autres. Vérifions l'unicité des noms dans le catalogue :

```text
catalogue : 120 produits, 60 noms distincts, 120 produits dont le nom est partagé
```

Le catalogue compte **120 produits mais seulement 60 noms distincts** : chaque nom est porté par deux produits (de prix différents). Une recherche par nom renvoie donc l'un des deux, silencieusement. Une **clé de recherche doit être unique** : ici l'identifiant du produit. Nous retrouverons cette anomalie, avec ses conséquences sur une jointure, en section 2.3.5.

#### Enrichir les lignes : le coût d'achat et la marge

Ajoutons à chaque ligne de vente le **coût d'achat unitaire** du produit, par `=RECHERCHEX(G2 ; Produits!A:A ; Produits!E:E)` (l'identifiant du produit est en colonne G) recopiée sur les 29 827 lignes dans une nouvelle colonne N. On obtient alors la **marge** de l'année : le chiffre d'affaires moins la somme des quantités multipliées par le coût unitaire.


![Une colonne ajoutée par recherche : le coût d'achat unitaire de chaque ligne, retrouvé dans la feuille `Produits` à partir de l'identifiant du produit. Extrait : seules quelques colonnes de la feuille sont affichées. Maquette dessinée avec matplotlib, valeurs issues du classeur.](figures/ch02-recherche.png)

```text
marge de l'année : 639 810,88 € (CA 1 324 763,72 €)
dont catégorie Jardin : 171 875,43 €
```

La **marge de 2025** s'élève à **639 810,88 €**, dont **171 875,43 €** pour la seule catégorie Jardin ; les deux chiffres sont recoupés par pandas (fusion des tables, puis somme). La marge est ici calculée sur le prix de vente tel quel : nous ignorons la TVA, simplification que nous reprendrons en section 2.2.4.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3, exercices 2.3 et 2.4.

### 2.1.7 Nettoyer du texte

Les données réelles sont sales : espaces en trop, majuscules incohérentes, nombres écrits comme du texte. Quelques fonctions de texte suffisent à corriger l'essentiel.

| Besoin | Fonction | Exemple (cellule `B2` = `" bOÎTE rustique  "`) |
|---|---|---|
| Enlever les espaces superflus | `SUPPRESPACE` | `SUPPRESPACE(B2)` |
| Normaliser la casse | `MAJUSCULE`, `MINUSCULE`, `NOMPROPRE` | `NOMPROPRE(SUPPRESPACE(B2))` |
| Extraire un morceau | `GAUCHE`, `DROITE`, `STXT` | `GAUCHE(A2 ; 1)` |
| Mesurer, repérer | `NBCAR`, `TROUVE`, `CHERCHE` | `TROUVE("-" ; F2)` |
| Remplacer | `SUBSTITUE` | `SUBSTITUE(E2 ; "," ; ".")` |
| Assembler | `CONCAT`, `JOINDRE.TEXTE`, opérateur `&` | `CONCAT(A2 ; "-" ; D2)` |
| Convertir en nombre | `CNUM` | `CNUM(E2)` |

```text
=NOMPROPRE(SUPPRESPACE(Texte!B2))  →  Boîte Rustique
=GAUCHE(Texte!A2;1)  →  T
=CNUM(DROITE(Texte!A2;NBCAR(Texte!A2)-1))  →  33 133
=NBCAR(Texte!B2)  →  17
=STXT(Texte!C2;1;3)  →  abc
=CONCAT(Texte!A2;"-";Texte!D2)  →  T33133-77
=JOINDRE.TEXTE(" | ";VRAI;SUPPRESPACE(Texte!B2);SUPPRESPACE(Texte!B3);SUPPRESPACE(Texte!B4))  →  bOÎTE rustique | moule MAT | Plaid NORDIQUE
=TROUVE("-";Texte!F2)  →  2
=CNUM(Texte!E2)  →  12,50
```

L'exemple le plus courant est le **numéro de ticket** de l'export de caisse : `T33133`, un code qui commence par une lettre. Pour obtenir le numéro seul, on enlève le premier caractère et on convertit : `=CNUM(DROITE(A2 ; NBCAR(A2)-1))` donne 33 133. De même, le nom d'article ` bOÎTE rustique  ` devient `Boîte Rustique` avec `NOMPROPRE(SUPPRESPACE(…))` : l'espace en tête et les doubles espaces disparaissent, et la casse est homogène. `TROUVE` est sensible à la casse et renvoie `#VALEUR!` si le texte n'existe pas ; `CHERCHE` ne l'est pas et accepte des jokers.

⚠️ **Piège.** `SUPPRESPACE` ne supprime pas l'**espace insécable** (code 160) que l'on obtient en copiant des données depuis une page web ou un PDF. Il faut alors `SUBSTITUE(A2 ; CAR(160) ; " ")` avant. Les décimales posent un autre piège : `"12,5"` est un nombre en Excel français, mais un texte qui **ne se convertit pas** en Excel anglais, où le séparateur décimal est le point. Quand vous échangez des fichiers entre langues, **testez**.

### 2.1.8 Manipuler des dates

Pour Excel, une date est un **numéro de série** : le nombre de jours écoulés depuis le 1ᵉʳ janvier 1900 (système par défaut de Windows, dans lequel le 1ᵉʳ janvier 1900 vaut 1). Le 1ᵉʳ janvier 2025 vaut **45 658** ; la cellule n'affiche une date que grâce à son **format**. Ce choix rend les calculs triviaux (la différence de deux dates est un nombre de jours) mais cache deux pièges : on peut afficher un nombre à la place d'une date (si le format est « Standard »), et inversement un nombre peut s'afficher comme une date.

> 🧪 **Un héritage historique.** Excel traite par erreur 1900 comme une année bissextile (pour rester compatible avec un ancien tableur) : les numéros de série d'avant le 1ᵉʳ mars 1900 sont décalés d'un jour. Sans conséquence pour des données récentes ; sachez-le si vous travaillez sur des dates anciennes. Les Mac utilisaient autrefois un système différent (point de départ en 1904) : une option du classeur le permet encore.

| Besoin | Fonction | Résultat |
|---|---|---|
| Extraire l'année, le mois, le jour | `ANNEE`, `MOIS`, `JOUR` | `ANNEE(3/11/2025)` = 2025 |
| Fabriquer une date | `DATE(année ; mois ; jour)` | `DATE(2025 ; 1 ; 1)` = 45 658 |
| Dernier jour du mois | `FIN.MOIS(date ; 0)` | `FIN.MOIS(10/02/2025 ; 0)` = 28/02/2025 |
| Décaler de n mois | `MOIS.DECALER(date ; n)` | `MOIS.DECALER(31/01/2025 ; 1)` = 28/02/2025 |
| Jour de la semaine | `JOURSEM(date ; 2)` | lundi = 1 |
| Écart | `DATEDIF(début ; fin ; "M")` | mois entiers écoulés |
| Jours ouvrés | `NB.JOURS.OUVRES(début ; fin)` | exclut samedis et dimanches |
| Afficher | `TEXTE(date ; "mmmm")` | « mars » |

```text
=DATE(2025;1;1)*1  →  45 658
=FIN.MOIS(DATE(2025;2;10);0)  →  45 716
=MOIS.DECALER(DATE(2025;1;31);1)  →  45 716
=JOURSEM(DATE(2025;11;3);2)  →  1
=TEXTE(DATE(2025;11;3);"dddd")  →  lundi
=DATEDIF(DATE(2025;1;15);DATE(2025;11;3);"M")  →  9
=DATEDIF(DATE(2025;1;15);DATE(2025;11;3);"D")  →  292
=NB.JOURS.OUVRES(DATE(2025;11;3);DATE(2025;11;9))  →  5
=TEXTE(DATE(2025;3;15);"mmmm")  →  mars
```

Les résultats sont des numéros de série, que l'on met en forme de date pour les lire (`FIN.MOIS` donne 45 716, c'est-à-dire le 28 février 2025) ; le 3 novembre 2025 est un **lundi** (`JOURSEM(…;2)` renvoie 1), il y a **9 mois entiers** et **292 jours** entre le 15 janvier et le 3 novembre, et la semaine du 3 au 9 novembre compte **5 jours ouvrés**. Les numéros de série sont recoupés par pandas (écart de dates).

`DATEDIF` est une fonction **non documentée dans l'aide** d'Excel mais qui fonctionne ; évitez son argument `"MD"`, dont les résultats sont réputés incohérents.

#### Dates en texte : le piège du format régional

Quand un export écrit les dates comme `03/11/2025`, Excel les reconnaît comme des dates **si** le format correspond à la langue du poste : en français, jour/mois/année ; en anglais américain, mois/jour/année. La chaîne `11/03/2025` est donc le **11 mars** dans un Excel français et le **3 novembre** dans un Excel américain. Si Excel ne la reconnaît pas, elle reste du **texte** : une `SOMME` de ces cellules vaut 0, mais `DATEVALUE` les convertit.

```text
somme de deux dates stockées en texte : 0
somme après DATEVALUE (03/11/2025 + 11/03/2025) : 91 691 = 45 964 + 45 727
11/03/2025 lu par un Excel français : 45 727 (le 11 mars 2025)
```

Notre classeur est en français : `11/03/2025` donne 45 727, le 11 mars. **Vérifiez toujours** quelques dates connues (un 25, un 31 : ceux-là ne peuvent pas être des mois) après un import : c'est le test le plus rapide pour détecter une inversion jour/mois.

⚠️ **Piège.** Les codes de format dans `TEXTE` dépendent de la **langue** : en français, l'année s'écrit `aaaa` et le jour `jjjj` ; en anglais `yyyy` et `dddd`. Un classeur partagé entre un poste français et un poste anglais peut donc afficher `#VALEUR!` ou un format inattendu. Dans ce livre, nous utilisons les codes valables dans les deux langues (`mmmm` pour le mois).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.4, exercice 2.5.

### 2.1.9 Les formules à résultats multiples : FILTRE, TRIER, UNIQUE, LET

Dans Excel 2021 et Microsoft 365, certaines fonctions renvoient **plusieurs valeurs** qui « débordent » (*spill*) dans les cellules voisines : `UNIQUE(plage)` liste les valeurs distinctes, `TRIER(plage)` les range, `FILTRE(plage ; condition)` extrait les lignes qui vérifient une condition, `SEQUENCE(n)` génère une suite de nombres. Avant ces fonctions, il fallait des astuces (formules matricielles, `Ctrl+Maj+Entrée`).

La fonction `LET` donne un **nom** à un résultat intermédiaire à l'intérieur d'une formule, ce qui la rend lisible et évite de recalculer deux fois la même chose : `=LET(somme ; SOMME(Montant) ; nb ; NBVAL(A:A)-1 ; somme/nb)` calcule le montant moyen par ligne.

```text
=NBVAL(UNIQUE(Lignes!I2:I29828))  →  6
=SOMME(FILTRE(Lignes!M2:M29828;Lignes!E2:E29828="Site"))  →  617 715,45
=LET(a;SOMME(Lignes!M2:M29828);b;NBVAL(Lignes!A2:A29828);ARRONDI(a/b;2))  →  44,41
```

Les résultats scalaires ont été vérifiés : il y a **6 catégories** distinctes, le total des lignes du **Site** est de 617 715,45 € (le même que `SOMME.SI.ENS`, trouvé par un autre chemin), et le **montant moyen d'une ligne** est de **44,41 €**. En revanche, **le débordement lui-même** (la liste affichée sur plusieurs cellules) n'est pas vérifiable avec notre outil : nous l'avons recoupé par pandas (`unique`, `sort_values`, filtre booléen), qui donne les mêmes lignes. Ces fonctions sont absentes des versions anciennes d'Excel : un classeur qui les utilise **ne se recalcule pas** chez un collègue qui en possède une (⚠️ à vérifier avant de partager).

### 2.1.10 Les erreurs, et la correspondance anglais–français

Excel signale une formule impossible par un code d'erreur commençant par `#`. Les reconnaître vous fait gagner un temps considérable.

```text
=1/0  →  #DIV/0!
=RECHERCHEV("zz";Produits!A2:B121;2;FAUX)  →  #N/A
="a"+1  →  #VALUE!
=INDEX(Produits!A:A;2000000)  →  #REF!
=NOMINCONNU(1)  →  #NAME?
=SIERREUR(1/0;"n/a")  →  n/a
```

| Code (Excel français) | Signification | Cause typique |
|---|---|---|
| `#DIV/0!` | division par zéro | dénominateur vide ou nul |
| `#N/A` | valeur non disponible | recherche sans résultat |
| `#VALEUR!` | mauvais type d'argument | texte à la place d'un nombre, plages de tailles différentes |
| `#REF!` | référence invalide | ligne ou colonne supprimée, `INDEX` hors plage |
| `#NOM?` | nom inconnu | faute de frappe dans une fonction ou un nom |
| `#NOMBRE!` | valeur numérique impossible | racine carrée d'un négatif |
| `#NUL!` | intersection vide | espace utilisé à la place de `;` ou `:` |
| `#DÉBORDEMENT!` | résultat qui déborde sur des cellules occupées | formule à résultats multiples bloquée |
| `#####` | colonne trop étroite | pas une erreur de calcul : élargir la colonne |

Le bloc précédent a produit cinq de ces erreurs avec LibreOffice (division par zéro, recherche sans résultat, texte plus un nombre, référence hors plage, nom inconnu) : `#DIV/0!`, `#N/A`, `#VALEUR!`, `#REF!` et `#NAME?` (le nom anglais de `#NOM?`). Une **différence** connue : la racine carrée d'un nombre négatif renvoie `#NOMBRE!` dans Excel et `#VALEUR!` dans LibreOffice ; la liste ci-dessus suit Excel et n'a pas pu être entièrement vérifiée.

Pour **chercher** les erreurs dans un classeur : `ESTERREUR(cellule)` renvoie `VRAI` ou `FAUX` ; le compte `=SOMMEPROD(--ESTERREUR(plage))` dénombre les erreurs d'une plage ; l'outil *Audit de formules* (onglet *Formules*) trace les antécédents d'une cellule. Un classeur propre n'affiche **aucune erreur** : un `#N/A` laissé en place est une alarme qu'on a éteinte.

#### Correspondance anglais–français

Un fichier `.xlsx` stocke les **noms anglais** des fonctions et le séparateur `,` ; Excel les affiche dans la langue de l'utilisateur. Quand vous lisez un tutoriel en anglais, voici les équivalents des fonctions de ce chapitre.

| Anglais | Français | Anglais | Français |
|---|---|---|---|
| `SUM`, `SUMIFS`, `SUMIF` | `SOMME`, `SOMME.SI.ENS`, `SOMME.SI` | `LEFT`, `RIGHT`, `MID` | `GAUCHE`, `DROITE`, `STXT` |
| `COUNTIFS`, `COUNTBLANK` | `NB.SI.ENS`, `NB.VIDE` | `TRIM`, `PROPER`, `LEN` | `SUPPRESPACE`, `NOMPROPRE`, `NBCAR` |
| `AVERAGEIFS` | `MOYENNE.SI.ENS` | `FIND`, `SUBSTITUTE`, `VALUE` | `TROUVE`, `SUBSTITUE`, `CNUM` |
| `IF`, `IFS`, `IFERROR` | `SI`, `SI.CONDITIONS`, `SIERREUR` | `CONCAT`, `TEXTJOIN`, `TEXT` | `CONCAT`, `JOINDRE.TEXTE`, `TEXTE` |
| `AND`, `OR`, `NOT` | `ET`, `OU`, `NON` | `YEAR`, `MONTH`, `EOMONTH` | `ANNEE`, `MOIS`, `FIN.MOIS` |
| `VLOOKUP`, `XLOOKUP` | `RECHERCHEV`, `RECHERCHEX` | `EDATE`, `WEEKDAY`, `NETWORKDAYS` | `MOIS.DECALER`, `JOURSEM`, `NB.JOURS.OUVRES` |
| `INDEX`, `MATCH` | `INDEX`, `EQUIV` | `FILTER`, `SORT`, `UNIQUE` | `FILTRE`, `TRIER`, `UNIQUE` |
| `SUMPRODUCT`, `LET` | `SOMMEPROD`, `LET` | `TRUE`, `FALSE` | `VRAI`, `FAUX` |

> ✅ **À retenir.**
> - Une formule est une **recette** : les références relatives se décalent, les références absolues (`$`) et les **noms** ne bougent pas ; un tableau structuré **grandit** tout seul.
> - `SOMME.SI.ENS` : la plage à sommer **vient d'abord** ; les plages doivent avoir **la même taille** ; une plage trop courte ne signale **rien**.
> - `RECHERCHEV` : toujours `FAUX` pour l'exacte ; elle regarde à droite et casse si l'on insère une colonne ; préférez `INDEX+EQUIV` ou `RECHERCHEX`.
> - `SIERREUR` masque **toutes** les erreurs : utilisez-la avec parcimonie.
> - Une date est un **numéro de série** ; vérifiez le format jour/mois après un import.
> - **Chaque chiffre important se recoupe par un second chemin** (ici pandas) : sur le classeur, 29 827 lignes, 1 324 763,72 €, un écart nul sur toutes les formules vérifiées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 à 2.4, exercices 2.1 à 2.5.


## 2.2 Tableaux croisés dynamiques et graphiques croisés dynamiques

Le **tableau croisé dynamique** (TCD, *PivotTable* en anglais) est l'outil le plus puissant d'Excel pour un analyste : il résume des milliers de lignes en un tableau de quelques lignes et colonnes, **sans écrire une seule formule**, et se remanie en deux clics de souris. C'est lui qui répond à la question de la gérante : « par catégorie et par mois, qu'avons-nous vendu ? ». Cette section explique comment il raisonne, comment le construire, et surtout comment **se méfier de ce qu'il affiche**.

> ⚠️ **Ce qui est vérifié, et ce qui ne l'est pas.** Le tableau croisé dynamique est un objet propre à Excel, que notre outil de vérification ne sait pas construire. Pour chaque TCD de cette section, nous donnons donc **trois choses** : la description des gestes à faire, le **résultat que le TCD doit afficher** (calculé en pandas avec `pivot_table`), et un **recoupement par des formules `SOMME.SI.ENS`** calculées par LibreOffice. Si votre TCD affiche autre chose, c'est le TCD (ou sa source) qui est en cause.


### 2.2.1 Le principe : lignes, colonnes, valeurs, filtres

Un tableau croisé dynamique prend une **table de données** (une ligne par observation, une colonne par variable) et la regroupe selon **quatre zones** que l'on remplit en faisant glisser des champs :

- **Lignes** : les champs dont chaque valeur distincte devient une ligne du tableau (par exemple `categorie`) ;
- **Colonnes** : les champs dont chaque valeur distincte devient une colonne (par exemple `canal`) ;
- **Valeurs** : le champ que l'on agrège (par exemple `montant`) et la **manière** de l'agréger : somme, nombre, moyenne, minimum, maximum… ;
- **Filtres** : des champs qui restreignent les lignes prises en compte (par exemple `annee`), sans apparaître dans le tableau.

Pour chaque combinaison (ligne, colonne), le TCD prend les lignes de la table qui ont ces valeurs et leur applique l'agrégation. C'est exactement l'opération que `SOMME.SI.ENS` fait cellule par cellule ; le TCD la fait **pour toutes les cellules à la fois**.


![Le volet des champs d'un tableau croisé dynamique : on fait glisser les champs de la table dans les quatre zones. Schéma dessiné avec matplotlib, pas une capture d'Excel (les libellés varient avec la version et la langue).](figures/ch02-champs-tcd.png)

#### Un TCD à la main sur huit lignes

Prenons huit lignes de vente (catégorie, canal, montant) :

| # | Catégorie | Canal | Montant |
|---|---|---|---|
| 1 | Cuisine | Boutique | 40 |
| 2 | Cuisine | Site | 25 |
| 3 | Jardin | Boutique | 80 |
| 4 | Jardin | Site | 60 |
| 5 | Cuisine | Boutique | 10 |
| 6 | Jardin | Site | 30 |
| 7 | Cuisine | Site | 15 |
| 8 | Jardin | Boutique | 20 |

Avec `categorie` en lignes, `canal` en colonnes et la **somme** du montant en valeurs, chaque case regroupe les lignes concernées : Cuisine × Boutique = 40 + 10 = 50 ; Cuisine × Site = 25 + 15 = 40 ; Jardin × Boutique = 80 + 20 = 100 ; Jardin × Site = 60 + 30 = 90. Les totaux de lignes et de colonnes s'obtiennent en additionnant (Cuisine = 90, Jardin = 190, Boutique = 150, Site = 130), et le total général est **280**, qui doit être égal à la somme des huit montants : 40 + 25 + 80 + 60 + 10 + 30 + 15 + 20 = 280. Ce **contrôle** (total du TCD = total de la source) est le plus important de toute la section.

### 2.2.2 Construire un tableau croisé pas à pas

Sur le classeur de la gérante, voici la marche à suivre (les noms de menus varient selon la version : **à vérifier** sur votre poste) :

1. Cliquez dans une cellule de la table de données ; si ce n'est pas déjà un tableau structuré, faites `Ctrl+T` pour en faire un (c'est ce qui permettra au TCD de suivre les nouvelles lignes).
2. Onglet *Insertion*, bouton *Tableau croisé dynamique* ; choisissez une **nouvelle feuille** comme destination.
3. Dans le volet des champs, glissez `categorie` dans *Lignes*, `canal` dans *Colonnes* et `montant` dans *Valeurs*.
4. Excel affiche par défaut **Somme de montant** (si la colonne ne contient que des nombres) ; un clic sur le champ permet de choisir une autre agrégation et le **format** des nombres (séparateur de milliers, deux décimales).

Le résultat attendu, calculé par pandas :

```python
pt = L.pivot_table(index="categorie", columns="canal", values="montant", aggfunc="sum", margins=True, margins_name="Total")
print(pt.round(2).to_string())
```
<!--sortie-->
```text
canal        Boutique    Réseaux       Site       Total
categorie                                              
Bien-être    48682.72   13670.69   55157.43   117510.84
Cuisine      98565.17   25137.50  109609.91   233312.58
Décoration  111898.40   28008.19  118835.74   258742.33
Jardin      149067.30   38686.18  166201.16   353954.64
Maison      129080.56   34744.95  140788.49   304614.00
Papeterie    23679.76    5826.85   27122.72    56629.33
Total       560973.91  146074.36  617715.45  1324763.72
```

La question qui compte : **peut-on se fier à ce tableau ?** Recoupons-le avec 18 formules `SOMME.SI.ENS` (une par case), calculées par LibreOffice :

```text
18 cases SOMME.SI.ENS contre le tableau croisé : écart maximal 0.0 €
somme des 18 cases : 1 324 763,72 | total de la source : 1 324 763,72
```

Les 18 cases sont identiques au centime près, et leur somme retombe sur le total de la source, **1 324 763,72 €**. La lecture est immédiate : le Jardin est la première catégorie (353 954,64 €), devant la Maison (304 614,00 €) et la Décoration (258 742,33 €) ; le Site pèse 617 715,45 €, devant la Boutique (560 973,91 €).


![Le tableau croisé dynamique attendu : catégories en lignes, canaux en colonnes, somme du montant, totaux généraux. Maquette dessinée avec matplotlib à partir de valeurs calculées (pas une capture d'Excel).](figures/ch02-tcd.png)

Observons enfin ce que le tableau ne montre pas : **les proportions**. La section 2.2.4 y revient.

### 2.2.3 Regrouper les dates : par mois, par trimestre, par année

La gérante voulait un tableau **par mois**. Mettre `date_commande` en lignes produit 365 lignes, une par jour. Excel (dans ses versions récentes) regroupe souvent les dates automatiquement en mois, trimestres et années ; sinon, un clic droit sur une date puis *Grouper* permet de choisir les niveaux (secondes, minutes, heures, jours, **mois**, **trimestres**, **années**). Les dates doivent être de **vraies dates** (2.1.8) : une colonne contenant du texte ne se regroupe pas.

```python
mp = L.assign(mois=L["date_commande"].dt.to_period("M")).pivot_table(index="mois", columns="categorie", values="montant", aggfunc="sum", margins=True, margins_name="Total")
print(mp.round(0).astype(int).iloc[[0, 1, 5, 6, 11, 12]].to_string())
```
<!--sortie-->
```text
categorie  Bien-être  Cuisine  Décoration  Jardin  Maison  Papeterie    Total
mois                                                                         
2025-01        10816    19475       19653    7455   27648       4132    89179
2025-02         7990    15519       16774    7649   20964       3746    72642
2025-06         6972    14775       13858   48204   19339       3782   106930
2025-07         6597    13837       13555   56711   17619       2902   111221
2025-12        17997    33689       60891   18763   44688       7817   183845
Total         117511   233313      258742  353955  304614      56629  1324764
```

On lit trois histoires dans ce tableau. La catégorie **Jardin** est saisonnière : 7 455 € en janvier, 56 711 € en juillet, puis 18 763 € en décembre. La **Décoration** a un pic en décembre (60 891 €, plus du double de novembre, 27 247 €). Et le **total** culmine en décembre à 183 845 €, soit plus du double de février (72 642 €).

```text
72 cases (6 catégories × 12 mois) SOMME.SI.ENS contre le tableau croisé : écart maximal 0.0 €
somme des 72 cases : 1 324 763,72
```

Les 72 formules (une par case, avec des bornes de dates `">="&DATE(…)` et `"<"&DATE(…)`) donnent les mêmes valeurs que le regroupement. Si l'on souhaite un résumé par trimestre : 251 609 € au premier trimestre, 310 783 € au deuxième, 314 572 € au troisième et 447 800 € au quatrième.

```text
par trimestre : {1: 251609, 2: 310783, 3: 314572, 4: 447800}
part de la Boutique selon la catégorie : de 41.4 à 43.2 % | du Site : de 45.9 à 47.9 %
```


![Un graphique croisé dynamique : le chiffre d'affaires de 2025 par mois et par catégorie (empilé). Le même tableau que ci-dessus, dessiné avec matplotlib.](figures/ch02-gcd.png)

Le **graphique croisé dynamique** est simplement le graphique d'un TCD : il en suit les lignes, les colonnes et les filtres, et se met à jour avec lui. C'est un bon outil d'exploration, moins bon pour la présentation finale (volume IV de la série (visualisation et communication)).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.5, exercice 2.6.

### 2.2.4 Afficher des proportions, calculer dans un TCD

Dans la zone *Valeurs*, le menu *Afficher les valeurs* remplace les montants par des **proportions** : % du total général, % du total de la colonne, % du total de la ligne, écart par rapport à une période précédente, cumul… Elles se calculent à partir des mêmes cases.

```text
% du total général (Jardin × Site) : 12.5 %  | Site (colonne) : 46.6 %
% du total de la ligne, Jardin : {'Boutique': 42.1, 'Réseaux': 10.9, 'Site': 47.0}
% du total de la ligne, toutes catégories : {'Boutique': 42.3, 'Réseaux': 11.0, 'Site': 46.6}
```

La lecture change tout. En **% du total général**, la case Jardin × Site vaut 12,5 % : c'est la plus grosse case, mais ce chiffre mélange la taille de la catégorie et celle du canal. En **% du total de la ligne**, on voit que **toutes les catégories ont à peu près le même partage entre canaux** (de 41 % à 43 % en Boutique, de 46 % à 48 % sur le Site) : les canaux ne se spécialisent pas par catégorie. Le Site pèse 46,6 % du total, la Boutique 42,3 %, les Réseaux 11,0 %. Quelle proportion choisir dépend de la question posée : **la bonne proportion est celle dont le dénominateur correspond à la question**.

#### Les champs calculés : attention au ratio de sommes

Un **champ calculé** ajoute au TCD une colonne définie par une formule sur les autres champs (par exemple `= marge / montant`). Mais le TCD **somme d'abord, puis calcule** : un champ calculé `marge / montant` donne le **rapport des sommes**, et non la **moyenne des rapports** ligne par ligne. Les deux ne coïncident pas :

```text
            moyenne des taux de ligne  rapport des sommes
categorie                                                
Bien-être                        46.3                45.9
Cuisine                          47.6                47.8
Décoration                       48.6                49.8
Jardin                           49.0                48.6
Maison                           48.8                48.2
Papeterie                        48.2                47.4
```

Pour la **Décoration**, la moyenne des taux de marge par ligne est de 48,6 % ; le rapport des sommes (ce que calcule un champ calculé) est de 49,8 %. La différence vient de ce que les lignes chères ont une marge relative plus forte et pèsent plus dans le rapport des sommes que dans la moyenne simple. **Aucun des deux n'est « faux »** : ils répondent à des questions différentes (« le taux de marge d'une ligne type » ou « la marge de la catégorie »). Il faut savoir lequel on affiche.

Autre limite : un champ calculé ne peut pas compter des **valeurs distinctes** (le nombre de clients différents, par exemple). Pour cela il faut le modèle de données de Power Pivot (section 2.5) ou un autre outil.

### 2.2.5 Segments, chronologies et pièges

Les **segments** (*slicers*) sont des boutons de filtre posés à côté du TCD (un bouton par canal, par exemple) ; la **chronologie** (*timeline*) est un curseur de dates. Ils rendent un TCD utilisable par quelqu'un qui ne le connaît pas : c'est le moyen le plus simple de fabriquer un petit tableau de bord interactif.

Les erreurs les plus fréquentes avec un TCD ne viennent pas du TCD, mais de sa **source** :

- **Le TCD ne s'actualise pas tout seul.** Si les données changent, il faut cliquer sur *Actualiser* (`Alt+F5`) ; un TCD daté de la semaine dernière sur des données de cette semaine est un grand classique. On peut demander l'actualisation à l'ouverture du fichier.
- **Une source en plage fixe** n'inclut pas les nouvelles lignes ; un **tableau structuré** (2.1.3) règle le problème.
- **Les doublons gonflent les totaux sans bruit.** Si 500 lignes sont copiées deux fois dans la source, le total passe de 1 324 763,72 € à 1 345 630,05 € (+ 20 866,33 €) et personne ne reçoit de message. Le contrôle du **nombre de lignes** (29 827 attendu) et de l'**unicité** de l'identifiant de ligne les détecte.
- **Les cellules vides** de la source comptent comme « (vide) » dans les lignes et colonnes, et faussent les moyennes si on les confond avec des zéros.
- **Les nombres stockés comme du texte** ne se somment pas : un TCD affichera alors **Nombre de** (un compte) au lieu de **Somme de**, ce qui doit vous alerter.

```text
doublons : total de la source 1 324 763,72 → avec 500 lignes en double 1 345 630,05 | lignes en double détectées : 500
nombres stockés comme du texte (12,5 ; 30 ; 7) : SOMME = 0 | NBVAL = 3 | SOMME après CNUM = 49,50
```

La dernière ligne reproduit ce piège : trois valeurs écrites comme du texte (`12,5`, `30`, `7`) donnent une somme de **0** et un compte de 3 ; après conversion par `CNUM`, la somme retombe sur **49,5**. Toute somme à zéro sur une colonne que l'on croyait remplie mérite un coup d'œil au **type** des cellules.

> ✅ **À retenir.**
> - Un TCD **regroupe** une table selon des champs en lignes, colonnes et filtres, et **agrège** un champ de valeurs ; chaque case est un `SOMME.SI.ENS`.
> - Vérifiez toujours : **total du TCD = total de la source**, et **nombre de lignes** attendu ; sur nos données, 18 cases et 72 cases recoupées, écart nul, total 1 324 763,72 €.
> - Une **proportion** n'a de sens qu'avec le bon dénominateur ; un **champ calculé** donne un rapport de sommes, pas une moyenne de rapports.
> - Les pièges viennent de la **source** : actualisation oubliée, plage fixe, doublons, vides, nombres en texte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.5, exercices 2.6 et 2.7.


## 2.3 Power Query pour l'import et la transformation

Chaque lundi, la gérante reçoit l'export de la caisse, l'ouvre, supprime à la main les lignes de titre, retire la ligne de total, corrige les majuscules, convertit les virgules en points… puis recommence la semaine suivante. **Power Query** est l'outil d'Excel qui remplace ces gestes par une **recette enregistrée** : on la construit une fois, on la rejoue en un clic sur chaque nouvel export. Cette section en explique le principe, montre la recette sur l'export de caisse, et vérifie chaque étape avec pandas.

> ⚠️ **Ce qui est vérifié, et ce qui ne l'est pas.** Power Query est un composant d'Excel (et de Power BI) que nous n'avons pas pu exécuter. Les **scripts en langage M** de cette section sont donc **non exécutés** et leur syntaxe est **à vérifier** dans votre version. En revanche, **chaque étape est reproduite en pandas** sur le vrai fichier `export_caisse_brut.csv`, avec le nombre de lignes à chaque étape et un contrôle final : ce sont les résultats que votre requête doit donner.

### 2.3.1 L'idée : une recette d'étapes enregistrées

Power Query (*Données → Obtenir des données*) ouvre un éditeur dans lequel chaque transformation (supprimer des lignes, changer un type, scinder une colonne, fusionner deux tables…) devient une **étape appliquée**, listée dans un volet à droite. L'ensemble des étapes est la **requête**. Trois propriétés la distinguent d'un nettoyage à la main :

- **elle est rejouable** : sur le prochain fichier, un clic sur *Actualiser* refait toutes les étapes dans le même ordre ;
- **elle est lisible** : les étapes portent un nom, on voit où une donnée a changé ; la requête est aussi un **document** du traitement (section 2.4) ;
- **elle ne touche pas à la source** : le fichier d'origine reste intact, le résultat est chargé dans une feuille ou dans le modèle de données.

Derrière l'interface, chaque étape est une ligne de code dans un langage fonctionnel appelé **M**. On peut l'ignorer au début (on clique), et le lire ensuite pour comprendre ou corriger une requête.


### 2.3.2 Importer : formats, encodage, paramètres régionaux

Power Query sait lire des classeurs Excel, des fichiers texte et CSV, des **dossiers entiers** (tous les fichiers d'un répertoire, empilés), des bases de données, des pages web. Pour un fichier texte, **trois réglages** décident de tout, et c'est là que naissent la plupart des erreurs d'import :

- le **délimiteur** (point-virgule, virgule, tabulation) : l'export français utilise le point-virgule parce que la virgule sert de séparateur décimal ;
- l'**encodage** : les anciens exports de Windows sont en `cp1252` (ANSI), les fichiers modernes en UTF-8 ;
- les **paramètres régionaux** (*culture*) : ils définissent la virgule décimale (`52,43`) et l'ordre des dates (`03/11/2025` = jour/mois/année).

Regardons le fichier tel que la caisse le fournit. Nous le lisons **sans rien interpréter** : tout en texte, sans en-tête, en conservant les lignes vides.

```python
brut = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", header=None, dtype=str, skip_blank_lines=False)
print(brut.shape)
print(brut.iloc[:6, :4].fillna("").to_string(header=False))
```
<!--sortie-->
```text
(289, 8)
0             Export caisse - Boutique                                   
1  Période du 03/11/2025 au 09/11/2025                                   
2                                                                        
3                            N° ticket        Date  Heure         Article
4                               T33133  03/11/2025  09:00  BOÎTE RUSTIQUE
5                               T33137  03/11/2025  10:35  Tapis nordique
```

Le fichier compte **289 lignes** et 8 colonnes. On y voit un **titre**, une ligne de **période**, une ligne **vide**, puis l'en-tête réel (`N° ticket`, `Date`, …) à la quatrième ligne. Un import automatique, qui supposerait un en-tête en première ligne, rangerait ce titre dans les noms de colonnes et ferait de toutes les colonnes du **texte**.

```text
caractères illisibles si l'on décode en UTF-8 au lieu de cp1252 : 169
dates 03/11/2025 lues « à l'américaine » : ['11/03/2025', '11/03/2025', '11/03/2025']
```

Deux erreurs d'import illustrent les réglages. Avec le **mauvais encodage**, 169 caractères accentués sont illisibles (`é` devient `�`) : un `Boîte` ne correspond plus à rien. Avec les **mauvais paramètres régionaux**, le 3 novembre (`03/11/2025`) est lu comme le **11 mars** : les trois premières dates se retrouvent au 11/03/2025. Comme toutes les dates de cette semaine ont un jour inférieur à 10 et le mois 11, **toutes** les lignes seraient décalées de plusieurs mois, sans le moindre message d'erreur.

### 2.3.3 Les étapes de nettoyage, une à une

Voici la recette pour l'export de caisse. Pour chaque étape, nous donnons l'opération de Power Query (son nom français dans l'interface, **à vérifier** selon la version) et l'équivalent pandas, avec le **nombre de lignes** après l'étape.

| # | Étape Power Query | Équivalent pandas | Lignes après |
|---|---|---|---|
| 1 | Supprimer les premières lignes (3) | `.iloc[3:]` | 286 |
| 2 | Utiliser la première ligne comme en-têtes | `.columns = …` | 285 |
| 3 | Supprimer les lignes d'en-tête répétées (filtrer `N° ticket` ≠ `N° ticket`) | `[t["N° ticket"] != "N° ticket"]` | 281 |
| 4 | Supprimer la ligne de total (filtrer les `Qté` vides) | `[t["Qté"].notna()]` | 280 |
| 5 | Changer les types (avec les paramètres régionaux `fr-FR`) | `to_datetime(format=…)`, `astype` | 280 |
| 6 | Nettoyer le texte (espaces, majuscules) | `.str.strip().str.capitalize()` | 280 |
| 7 | Ajouter une colonne : montant corrigé | `fillna(Qté × Prix)` | 280 |

```python
t = brut.iloc[3:].reset_index(drop=True)
t.columns = t.iloc[0]; t = t.iloc[1:].reset_index(drop=True)
n_apres_entete = len(t)
t = t[t["N° ticket"] != "N° ticket"]; n_sans_repetes = len(t)
t = t[t["Qté"].notna()].copy(); n_sans_total = len(t)
print(len(brut), "→", n_apres_entete, "→", n_sans_repetes, "→", n_sans_total, "lignes")
```
<!--sortie-->
```text
289 → 285 → 281 → 280 lignes
```

On passe de 289 lignes à **280 lignes de vente** : trois lignes de titre, l'en-tête réel, quatre en-têtes répétés (l'export les a reproduits à chaque « page ») et une ligne de total. La ligne de total est précieuse : nous la conservons de côté, elle servira de **total de contrôle**.

Viennent les types et le texte :

```python
for c in ["Prix unitaire", "Montant"]:
    t[c] = t[c].str.replace(",", ".").astype(float)          # virgule décimale -> point
t["Qté"] = t["Qté"].astype(int)
t["Date"] = pd.to_datetime(t["Date"], format="%d/%m/%Y")
t["Article"] = t["Article"].str.strip().str.capitalize()      # « BOÎTE RUSTIQUE » -> « Boîte rustique »
t["Catégorie"] = t["Catégorie"].str.strip().str.capitalize()  # « maison » -> « Maison »
print(t["Catégorie"].value_counts().to_dict())
print("montants manquants :", int(t["Montant"].isna().sum()))
```
<!--sortie-->
```text
{'Décoration': 68, 'Maison': 52, 'Cuisine': 50, 'Papeterie': 40, 'Bien-être': 38, 'Jardin': 32}
montants manquants : 8
```

Deux choix méritent l'attention. D'abord la **casse** : la fonction « Première lettre de chaque mot en majuscule » de Power Query (`Text.Proper`) donnerait `Bien-Être` et `Bol Design`, qui ne correspondent plus au catalogue (`Bien-être`, `Bol design`) ; la bonne transformation est **une majuscule initiale, le reste en minuscules** (`Text.Upper` du premier caractère, `Text.Lower` du reste). Ensuite les **8 montants manquants** : que mettre ?

#### Combler les montants manquants, et se contrôler

Une solution naturelle est de recalculer `Qté × Prix unitaire`. Mais la ligne de total du fichier permet de **vérifier** cette réparation : elle annonce 11 561,47 €.

```text
total annoncé par l'export : 11 561,47 | somme après réparation : 11 564,09 | écart : 2,62
```

La somme réparée vaut **11 564,09 €** contre **11 561,47 €** : un écart de **2,62 €**. La réparation est donc **un peu trop généreuse** : les huit lignes concernées appartiennent à des tickets qui avaient une **remise** (code promo), et `Qté × Prix` l'ignore. Le contrôle ne dit pas *quelle* ligne est fausse, mais il **prouve** qu'il y a un écart, ce qu'une réparation silencieuse n'aurait jamais révélé. Deux attitudes sont défendables : signaler l'écart et laisser un indicateur « montant estimé » dans une colonne, ou aller chercher la remise dans la source (ici la table des commandes). **Ne jamais réparer sans contrôler.**

Voici la requête complète en langage M (non exécutée) ; les étapes portent les noms de l'éditeur.

```text
let
    Source = Csv.Document(File.Contents("export_caisse_brut.csv"), [Delimiter=";", Columns=8, Encoding=1252]),
    SansTitre = Table.Skip(Source, 3),
    EnTetes = Table.PromoteHeaders(SansTitre, [PromoteAllScalars=true]),
    SansRepetes = Table.SelectRows(EnTetes, each [#"N° ticket"] <> "N° ticket"),
    SansTotal = Table.SelectRows(SansRepetes, each [Qté] <> null and [Qté] <> ""),
    Types = Table.TransformColumnTypes(SansTotal, {{"Date", type date}, {"Qté", Int64.Type},
             {"Prix unitaire", type number}, {"Montant", type number}}, "fr-FR"),
    Texte = Table.TransformColumns(Types, {{"Article", each Text.Upper(Text.Start(Text.Trim(_), 1)) & Text.Lower(Text.Middle(Text.Trim(_), 1))},
             {"Catégorie", each Text.Upper(Text.Start(Text.Trim(_), 1)) & Text.Lower(Text.Middle(Text.Trim(_), 1))}}),
    Corrige = Table.AddColumn(Texte, "Montant corrigé", each if [Montant] = null then [Qté] * [Prix unitaire] else [Montant], type number)
in
    Corrige
```

*Syntaxe à vérifier dans votre version de Power Query, en particulier les noms de colonnes entre `#"…"` et le traitement de la colonne `Qté` vide.*


![L'éditeur de Power Query : à gauche, les étapes appliquées (chacune rejouable) ; à droite, l'aperçu du résultat. Schéma dessiné avec matplotlib, avec les vraies valeurs de l'export, pas une capture d'écran.](figures/ch02-power-query.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercice 2.8.

### 2.3.4 Scinder, fusionner des colonnes, dépivoter

Trois transformations de forme reviennent sans cesse.

**Scinder une colonne.** Le numéro de ticket `T33133` mélange une lettre et un nombre. *Fractionner la colonne → par nombre de caractères* donne `T` et `33133`, ce que fait en pandas `t["N° ticket"].str[0]` et `.str[1:]`. On peut aussi scinder `Nom Prénom` par délimiteur (l'espace), une adresse par virgule.

**Fusionner des colonnes.** L'inverse : `Date` et `Heure` (deux colonnes de texte) deviennent un seul horodatage utilisable pour trier ou regrouper.

**Dépivoter.** Beaucoup de tableaux de reporting sont **larges** : une ligne par catégorie, une colonne par mois. Pour un TCD, un graphique ou une jointure, il faut le format **long** : une ligne par couple (catégorie, mois). L'opération *Dépivoter les colonnes* (*unpivot*) fait ce passage ; l'inverse est *Pivoter*. Prenons le tableau large du chiffre d'affaires par catégorie et par mois de 2025 : 6 lignes et 12 colonnes de mois.

```python
large = L.assign(mois=L["date_commande"].dt.to_period("M").astype(str)).pivot_table(index="categorie", columns="mois", values="montant", aggfunc="sum")
long = large.reset_index().melt(id_vars="categorie", var_name="mois", value_name="montant")
print(large.shape, "→", long.shape, "| total conservé :", round(long["montant"].sum(), 2))
```
<!--sortie-->
```text
(6, 12) → (72, 3) | total conservé : 1324763.72
```

Les 6 × 12 cases deviennent **72 lignes**, et le total (1 324 763,72 €) est **conservé** : c'est le contrôle de toute restructuration. Le format long est celui que les outils d'analyse attendent (chapitre 4 du volume) : une colonne par variable, une ligne par observation.

### 2.3.5 Fusionner et ajouter des requêtes

**Ajouter** des requêtes (*Append*) empile des tables de même structure : les exports de chaque semaine de l'année, par exemple. Avec l'option **Dossier**, Power Query lit tous les fichiers d'un répertoire et les empile : déposer le fichier de la semaine suivante dans le dossier suffit, un clic sur *Actualiser* met tout à jour. Notez que les fichiers doivent avoir **la même structure** (mêmes colonnes, même ordre) : un export dont une colonne a changé de nom fait échouer toute la requête, ce qui est **un bon signe** (l'erreur est visible).

**Fusionner** des requêtes (*Merge*) est une **jointure** : on rattache à chaque ligne d'une table des colonnes d'une autre, à partir d'une clé commune. Les types de jointure de Power Query ont leur équivalent pandas et SQL (chapitre 3) :

| Power Query | pandas | Ce que l'on garde |
|---|---|---|
| Externe gauche | `how="left"` | toutes les lignes de la table de gauche |
| Interne | `how="inner"` | seulement les lignes qui ont une correspondance |
| Anti gauche | `how="left"` puis filtre sur le manque | les lignes **sans** correspondance |

Rattachons à l'export de caisse le **coût d'achat** du catalogue, pour calculer la marge de la semaine. L'export ne contient pas l'identifiant du produit, seulement le **nom de l'article** : la clé de jointure sera le nom.

```python
cle = lambda s: s.str.lower()
prod = P.assign(cle=cle(P["nom_produit"]))
t["cle"] = cle(t["Article"])
m1 = t.merge(prod[["cle", "cout_achat"]], on="cle", how="left")
print(len(t), "lignes avant,", len(m1), "après la jointure sur le seul nom | total", O.fr(m1["Montant corrigé"].sum()))
```
<!--sortie-->
```text
280 lignes avant, 560 après la jointure sur le seul nom | total 23 128,18
```

**Le nombre de lignes a doublé** (280 → 560) et le total aussi (23 128,18 € au lieu de 11 564,09 €) : le nom d'article **n'est pas une clé**. Le catalogue compte 120 produits mais seulement **60 noms distincts** : chaque nom désigne deux produits, à des prix différents. La jointure rattache chaque ligne de vente à **chacun** des deux produits, et personne ne reçoit de message d'erreur. C'est l'erreur de fusion la plus coûteuse : **toujours vérifier le nombre de lignes avant et après une jointure**.

Pour lever l'ambiguïté, ajoutons le **prix** à la clé : le prix de caisse de novembre 2025 est le prix du catalogue majoré de 3 % (hausse du 1ᵉʳ janvier 2025, arrondie au centime).

```python
prod["prix_caisse"] = (prod["prix_vente"] * 1.03).round(2)
m2 = t.merge(prod[["cle", "prix_caisse", "cout_achat"]], left_on=["cle", "Prix unitaire"], right_on=["cle", "prix_caisse"], how="left")
print(len(t), "→", len(m2), "lignes | sans correspondance :", int(m2["prix_caisse"].isna().sum()))
doublons_cat = prod[prod.duplicated(["cle", "prix_caisse"], keep=False)][["id_produit", "nom_produit", "prix_vente", "cout_achat"]]
print(doublons_cat.to_string(index=False))
```
<!--sortie-->
```text
280 → 285 lignes | sans correspondance : 0
 id_produit nom_produit  prix_vente  cout_achat
         62  Carnet mat         2.9        1.53
         72  Carnet mat         2.9        1.53
```

Le résultat compte 285 lignes pour 280 attendues : **cinq lignes sont encore doublées**, parce que le catalogue lui-même contient **deux produits identiques** (`Carnet mat`, identifiants 62 et 72, même prix, même coût). C'est une anomalie du **catalogue** à signaler à son propriétaire ; en attendant, on **supprime les doublons du catalogue** avant de fusionner (l'étape *Supprimer les doublons* de Power Query).

```text
après dédoublonnage du catalogue : 280 lignes | sans correspondance : 0
marge de la semaine : 5 715,57 € sur 11 564,09 € de ventes
recoupement avec la base : lignes 280 | montant 11 561,47 | total de contrôle du fichier 11 561,47
```

Après dédoublonnage, la jointure rend bien **280 lignes**, toutes appariées. La marge de la semaine est de **5 715,57 €** sur 11 564,09 € de ventes (avec le montant réparé) ; et le recoupement avec la base des ventes confirme le **total de contrôle** : 280 lignes, 11 561,47 €, exactement la valeur de la ligne de total de l'export. Les 2,62 € de l'écart de réparation sont donc bien des remises que `Qté × Prix` ignorait.

Voici la fusion en langage M (non exécutée) :

```text
Fusion = Table.NestedJoin(Corrige, {"Article", "Prix unitaire"}, Catalogue, {"Nom", "PrixCaisse"}, "Cat", JoinKind.LeftOuter),
Colonnes = Table.ExpandTableColumn(Fusion, "Cat", {"cout_achat"})
```

### 2.3.6 Power Query, formules ou Python ?

| | Formules Excel | Power Query | Python / SQL |
|---|---|---|---|
| Point fort | immédiat, visible | rejouable sans code | très gros volumes, reproductible, versionnable |
| Point faible | difficile à rejouer proprement | outil propre à l'écosystème Microsoft | demande d'apprendre un langage |
| À choisir pour | calculs ponctuels, petits tableaux | **import et nettoyage récurrents de fichiers** | traitements lourds ou à partager en équipe |

> 🧭 **En pratique.** Si vous faites deux fois la même manipulation de fichier, **faites-en une requête**. Si le fichier dépasse le million de lignes, ou si le traitement doit tourner sans personne, passez à SQL ou à Python (chapitres 3 et 4).

> ✅ **À retenir.**
> - Une requête Power Query est une **liste d'étapes rejouables** ; elle ne modifie pas la source.
> - Trois réglages d'import décident de tout : **délimiteur, encodage, paramètres régionaux** (sur notre export : 169 caractères illisibles avec le mauvais encodage ; toutes les dates décalées avec les mauvais paramètres).
> - **Compter les lignes à chaque étape** (289 → 280 sur l'export) et **contrôler un total** (11 561,47 €) : l'écart de 2,62 € a révélé que la réparation ignorait des remises.
> - Une jointure sur une clé **non unique** multiplie les lignes (280 → 560) sans erreur : vérifiez l'unicité des clés et le nombre de lignes avant/après.
> - Dépivoter conserve le total (72 lignes, 1 324 763,72 €) : la restructuration se contrôle comme le reste.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercices 2.8 et 2.9.


## 2.4 Bonnes pratiques de tableur

Un classeur n'est pas seulement un calcul : c'est un **document que quelqu'un d'autre ouvrira**, souvent des mois plus tard, souvent la personne qui l'a écrit et qui ne se souvient plus de rien. Les erreurs de tableur ne viennent presque jamais d'une formule mal comprise ; elles viennent d'une **structure** qui les cache. Cette section rassemble les pratiques qui rendent un classeur **lisible, vérifiable et durable**.


### 2.4.1 Une structure en trois étages

La règle d'or est de **séparer ce qui entre, ce qui se calcule et ce qui se montre**. Un bon classeur comporte au moins quatre types de feuilles :

| Feuille | Contenu | Règle |
|---|---|---|
| `README` | à quoi sert le classeur, qui l'a fait, quand, d'où viennent les données, comment l'actualiser | écrite **en premier**, lue en premier |
| `Données` (ou plusieurs) | une table par feuille, brute ou nettoyée | **aucune mise en forme, aucune formule de synthèse** |
| `Calculs` | les formules et tableaux croisés qui lisent les données | rien de saisi à la main, sauf les **hypothèses** |
| `Présentation` | les chiffres et graphiques destinés aux lecteurs | ne contient que des **renvois** aux calculs |

Cette séparation a trois avantages. Quand les données changent (nouvelle semaine, nouvel export), on **remplace la feuille de données** et tout se recalcule. Quand on se demande d'où vient un chiffre, on remonte de la présentation aux calculs puis aux données. Et quand on donne le classeur à quelqu'un d'autre, il sait **où il peut toucher** et où il ne le doit pas.

Le contraire est le classeur « tout-en-un » : un tableau de bord où se mélangent des données collées, des calculs intermédiaires dans des cellules dispersées, et des chiffres retapés. Il fonctionne le jour où on le fabrique, puis plus jamais.

### 2.4.2 Des données propres : une ligne, une observation

Les outils d'analyse (tableaux croisés, Power Query, pandas, SQL) attendent des données **ordonnées** (*tidy*) :

1. **une ligne = une observation** (ici, un article vendu) ;
2. **une colonne = une variable**, avec **un seul type** (que des dates, que des montants) ;
3. **une seule ligne d'en-tête**, avec des noms courts et **sans cellules fusionnées** ;
4. **pas de ligne ni de colonne de totaux, de titres ou de blancs** au milieu des données ;
5. **une information par cellule** (pas de « Boutique / Ville A » dans la même cellule) ;
6. **des catégories écrites toujours de la même façon** (une liste de valeurs autorisées).

Comparons deux manières de présenter les mêmes ventes. À gauche, la présentation « pour être lue », qu'un humain aime ; à droite, la présentation « pour être analysée ».


![À éviter : un titre sur la première ligne, une ligne blanche, une colonne de total et, surtout, une ligne de sous-total au milieu des données. Agréable à lire, impossible à analyser. Maquette dessinée avec matplotlib.](figures/ch02-mal-range.png)

![À faire : une ligne d'en-tête, une ligne par article vendu, une colonne par variable, aucun total. Maquette dessinée avec matplotlib.](figures/ch02-bien-range.png)

Dans la première forme, un tableau croisé dynamique prendrait « Sous-total T1 » pour un mois, la ligne de titre pour un en-tête, et la colonne `Total` pour une catégorie. Dans la seconde, tout fonctionne : on regroupe par ce que l'on veut. Quand on **reçoit** des données sous la première forme (c'est fréquent), c'est précisément ce que Power Query (section 2.3) remet en forme.

⚠️ **Deux détails qui comptent.** D'abord les **identifiants** : un code comme `007` ou `00512` perd ses zéros si Excel le prend pour un nombre ; stockez-le comme **texte** (format texte *avant* la saisie). Ensuite les **cellules fusionnées** : elles cassent le tri, le filtre et les tableaux croisés ; pour centrer un titre au-dessus de plusieurs colonnes, utilisez l'alignement *Centré sur plusieurs colonnes*, qui ne fusionne rien.

### 2.4.3 Séparer les hypothèses des formules

Une formule qui contient un **nombre écrit en dur** est une bombe à retardement : `=B2*1,03` ne dit pas ce que représente 1,03, et personne ne pense à le changer quand le taux change. La règle est simple : **tout paramètre vit dans une cellule étiquetée**, et les formules y renvoient (par une référence absolue ou un nom, 2.1.2 et 2.1.3).

Illustrons-le avec une prévision simple pour 2026. Les hypothèses sont posées dans une feuille `Hyp` : volume +5 %, prix +3 %, inflation du coût d'achat +2 %. Le chiffre d'affaires 2026 est le chiffre de 2025 multiplié par `(1 + volume) × (1 + prix)` ; le coût d'achat est celui de 2025 multiplié par `(1 + volume) × (1 + inflation)` ; la marge est la différence.

```text
CA 2025 : 1 324 763,72 | coûts d'achat 2025 : 684 952,84 | marge 2025 : 639 810,88
marge 2026 (volume +5 %) : 699 147,47 | CA 2026 : 1 432 731,96 | recoupement en Python : 699 147,47
marge 2026 si le volume reste stable : 665 854,73
marge 2026 par rapport à 2025 : 9.3 % (volume +5 %) et 4.1 % (volume stable)
```

Avec ces hypothèses, la marge passe de **639 810,88 €** à **699 147,47 €** (+ 9,3 %) ; si le volume reste stable, elle s'élève à **665 854,73 €** (+ 4,1 %). Le **changement d'une seule cellule** (le volume) suffit à passer de l'un à l'autre : c'est ce qu'on appelle une **analyse de sensibilité**, et elle n'est possible que parce que l'hypothèse n'est écrite **qu'à un seul endroit**.

> 🧭 **En pratique.** Donnez une **couleur** aux cellules de saisie (par exemple un fond jaune pâle) et **une seule** couleur : tout le reste est calculé et ne se modifie pas. Ajoutez une colonne « source » ou « commentaire » à côté de chaque hypothèse : d'où vient ce 3 % ?

### 2.4.4 Se contrôler : validation, mise en forme conditionnelle, feuille de contrôles

On ne corrige bien que ce que l'on voit. Trois outils d'Excel aident à **rendre les erreurs visibles** :

- la **validation de données** (*Données → Validation*) restreint ce qu'une cellule accepte : une liste de valeurs (les trois canaux), un nombre entre deux bornes, une date dans la période. Une saisie `Sit` au lieu de `Site` est refusée à l'entrée plutôt que détectée dans un total faux ;
- la **mise en forme conditionnelle** colore les cellules qui remplissent une condition (valeurs négatives, doublons, écarts supérieurs à un seuil) ;
- une **feuille de contrôles** réunit des formules qui répondent à la question « ce classeur est-il intact ? ».

Voici notre feuille de contrôles, calculée par LibreOffice sur les données de la gérante, puis sur une copie où **500 lignes sont comptées deux fois** (un accident de copier-coller, l'erreur de la section 2.2.5). Les contrôles sont : nombre de lignes, nombre de doublons (lignes moins valeurs distinctes de l'identifiant), cellules vides dans une colonne clé, plage de dates, montants négatifs, total, et un verdict qui compare le nombre de lignes et le total à leurs **valeurs attendues**.

```text
contrôle                      données saines   avec 500 doublons
nombre de lignes                      29 827              30 327
doublons d'identifiant                     0                 500
canaux vides                               0                   0
date minimale                     01/01/2025          01/01/2025
date maximale                     31/12/2025          31/12/2025
montants ≤ 0                               0                   0
total des montants              1 324 763,72        1 345 630,05
verdict                                   OK               ÉCART
```

Le classeur sain passe tous les contrôles (29 827 lignes, aucun doublon, aucune valeur manquante, dates du 01/01/2025 au 31/12/2025, aucun montant négatif, verdict **OK**). La copie abîmée est détectée immédiatement : 30 327 lignes, **500 doublons**, un total de 1 345 630,05 € au lieu de 1 324 763,72 €, et un verdict **ÉCART**. **Les valeurs attendues** (29 827 lignes, 1 324 763,72 €) viennent d'une **autre source** que le classeur (par exemple la compta, ou la base de données) : c'est ce qui rend le contrôle utile, car un contrôle qui compare le classeur à lui-même ne prouve rien.

### 2.4.5 Les erreurs de tableur que tout le monde commet

Les erreurs spectaculaires de tableur ont des **mécanismes** simples et récurrents. Les reconnaître vaut mieux que mémoriser des anecdotes.

**1. La conversion automatique.** Excel interprète ce que l'on saisit ou importe : `1-2` devient une date, `007` devient 7, un nom qui ressemble à une date devient une date. Les chercheurs en génétique en ont fait l'amère expérience : des noms de gènes comme `SEPT2` ou `MARCH1` étaient convertis en dates dans des listes publiées, au point que les organismes de nomenclature ont fini par **renommer** des gènes (à vérifier, mais le cas est documenté). Pour éviter la conversion, importez en **texte** (Power Query, section 2.3) ou mettez la colonne au format texte **avant** de coller.

**2. L'arrondi et la précision.** Un tableur affiche un nombre arrondi mais calcule avec le nombre complet, et inversement. Deux illustrations sur nos données :

```text
somme des montants arrondis au dixième, 29 premières lignes : 1 281,90 | arrondi de la somme : 1 281,70
ARRONDI(2,675 ; 2) dans le tableur : 2,68 | round(2.675, 2) en Python : 2.67
(0,1 + 0,2) − 0,3 dans le tableur : 0 | en Python : 5.551115123125783e-17
12345678901234567 dans le tableur : 12 345 678 901 234 600
```

- **La somme des arrondis n'est pas l'arrondi de la somme** : 1 281,90 € contre 1 281,70 € sur seulement 29 lignes.
- **Outils différents, arrondis différents** : le tableur arrondit 2,675 à 2,68 (convention « 5 vers le haut » appliquée au nombre décimal), alors que Python donne 2,67, parce que 2,675 n'est **pas représentable exactement** en binaire (il est stocké un peu en dessous) ; de même, `(0,1 + 0,2) − 0,3` vaut 0 dans le tableur et 5,55 × 10⁻¹⁷ en Python : le tableur « nettoie » certains petits résidus, ce qui peut masquer un problème de précision.
- **La précision est limitée à 15 chiffres significatifs** : un identifiant de 17 chiffres (`12345678901234567`) perd ses derniers chiffres (LibreOffice affiche ici 12 345 678 901 234 600). **Les identifiants longs (numéros de carte, de compte) doivent être stockés comme du texte.**

Pour des montants, la règle est de **choisir où l'on arrondit** (à la ligne ? au total ?) et de s'y tenir : un écart de quelques centimes entre deux documents est presque toujours une affaire d'arrondi, pas d'erreur de calcul.

**3. La plage oubliée.** `=SOMME(M2:M29028)` oublie les 800 dernières lignes (33 638,83 € de moins, section 2.1.4). Un grand article d'économie très cité a, dit-on, subi une erreur de ce type (une plage qui omettait quelques pays) ; le détail est à vérifier, le mécanisme est certain. Contre cela : tableaux structurés, contrôle de total.

**4. Les limites du format.** Un fichier `.xlsx` est limité à **1 048 576 lignes** et 16 384 colonnes ; l'ancien format `.xls` s'arrêtait à **65 536 lignes**. Un service de santé publique a, en 2020, perdu plusieurs milliers de cas déclarés parce qu'un fichier de résultats était enregistré dans l'ancien format (à vérifier : l'incident est largement rapporté). Des données au-delà du million de lignes **n'ont rien à faire dans un tableur** : base de données, SQL, Python.

**5. Les liens et les valeurs figées.** Un classeur qui lit un autre classeur par un lien externe affiche l'ancienne valeur si le fichier source a bougé ; un « copier / collage spécial valeurs » fige un chiffre qui ne se mettra plus jamais à jour. Les deux sont légitimes, **à condition de les documenter**.

### 2.4.6 Documenter, protéger, versionner, partager

**Documenter.** La feuille `README` répond en dix lignes à : *à quoi sert ce classeur ? qui l'a produit, quand, pour qui ? quelles sont les sources des données et leurs dates ? comment l'actualiser ? quelles sont les hypothèses ? quelles sont les limites connues ?* Les commentaires de cellules servent aux exceptions (« valeur corrigée à la main le 12/03, voir le mail du fournisseur »).

**Nommer et versionner.** Un fichier s'appelle `ventes_2025_v03_2025-12-31.xlsx` plutôt que `ventes_final_vraiment_final.xlsx` : un numéro de version, une date ISO (année-mois-jour, qui se range correctement par ordre alphabétique). Si le classeur est partagé dans un espace en ligne, l'**historique des versions** permet de revenir en arrière ; si le travail est important, un **journal des modifications** (une feuille de plus) note qui a changé quoi.

**Protéger.** La protection d'une feuille ou de cellules verrouille les formules et laisse libres les cellules de saisie : c'est un **garde-fou contre les fausses manœuvres**, pas une mesure de sécurité (les mots de passe de protection d'un classeur sont faciles à contourner). Pour des données confidentielles, le contrôle d'accès se fait au niveau du **dossier ou du fichier**, pas de la feuille. Les classeurs qui contiennent des **données personnelles** (noms, adresses, téléphones de clients) sont soumis à des règles de confidentialité, et circulent mal par courrier électronique : le volume II y consacre un chapitre complémentaire.

**Partager.** Pour diffuser un chiffre, mieux vaut un **PDF** ou une feuille de présentation en lecture seule que le classeur de travail ; pour échanger des données, un **CSV** (simple, universel) plutôt qu'un classeur plein de formules et de liens.

> 🧭 **Liste de contrôle d'un classeur fiable.**
> 1. Une feuille `README` : objet, auteur, date, sources, hypothèses.
> 2. Données et calculs **séparés** ; données en **tableau structuré**, une ligne par observation.
> 3. **Aucun nombre en dur** dans une formule : des cellules d'hypothèses étiquetées.
> 4. Une **feuille de contrôles** comparant à une source indépendante.
> 5. **Aucune erreur** affichée (`#N/A`, `#REF!`…), aucune cellule fusionnée.
> 6. Un nom de fichier **versionné** et daté.

> ✅ **À retenir.**
> - Séparez ce qui **entre** (données, hypothèses), ce qui se **calcule** et ce qui se **montre**.
> - Des données **ordonnées** (une ligne, une observation) font fonctionner tous les outils ; un tableau « pour l'œil » les met en échec.
> - Un paramètre écrit en dur est une erreur future : une cellule, un nom, une analyse de sensibilité (ici : marge 2026 de 699 147,47 € ou 665 854,73 € selon le volume).
> - **Contrôlez** : lignes, doublons, vides, dates, total comparé à une **source indépendante** (500 doublons détectés, verdict ÉCART).
> - Les erreurs célèbres ont des mécanismes simples : conversion automatique, arrondis, plage oubliée, limites du format, liens et valeurs figées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercices 2.10 et 2.11.


## 2.5 ➕ Pour aller plus loin : Excel avancé

> 🧭 **Section complémentaire.** Elle présente ce qu'Excel sait faire au-delà de la feuille de calcul : un **modèle de données** relié (Power Pivot), un langage de **mesures** (DAX), l'**automatisation** (macros VBA, scripts Office), puis elle répond à la question qui conclut toute formation sur Excel : **quand faut-il le quitter ?** Aucun des composants de cette section n'a pu être exécuté sur la machine qui a produit le livre : les scripts DAX, VBA et Office Scripts sont **non exécutés** et leur syntaxe est **à vérifier** ; nous donnons à chaque fois le **résultat attendu**, calculé en pandas ou en SQL.


### 2.5.1 Power Pivot et le modèle de données

Un tableau croisé classique travaille sur **une seule table**. Or les données d'une entreprise sont réparties en plusieurs tables : les lignes de vente (les **faits**, des événements nombreux), le catalogue des produits et la liste des clients (les **dimensions**, des objets décrits une fois). Plutôt que d'ajouter des colonnes à la table des ventes par `RECHERCHEX` (2.1.6), Excel permet de **déclarer des relations** entre tables dans un **modèle de données** (le composant s'appelle *Power Pivot*), puis de construire un tableau croisé qui s'appuie sur plusieurs tables à la fois.

Une relation relie une colonne de la table des faits à la **clé** d'une dimension : `Lignes[id_produit]` vers `Produits[id_produit]`. Elle est de type **plusieurs à un** (plusieurs lignes de vente pour un produit). Pour qu'elle fonctionne, la clé du côté « un » doit être **unique** : c'est ce que la section 2.3.5 nous a appris à vérifier (le nom d'un produit ne l'est pas, son identifiant l'est).

```text
relation Lignes → Produits : identifiants du catalogue uniques : True | lignes sans produit connu : 0
relation Lignes → Clients  : identifiants clients uniques : True | lignes sans client connu : 0
lignes de ventes : 29 827 | produits : 120 | clients : 6 000
```

Les deux relations sont **saines** : les identifiants du côté « un » sont uniques, et aucune ligne de vente ne renvoie à un produit ou à un client inconnu (pas de ligne « orpheline »). C'est le **contrôle d'intégrité** que l'on fait avant de déclarer une relation : une clé en double ou une ligne orpheline faussent tous les résultats sans message.


![Un modèle de données en étoile : au centre la table des faits (`Lignes`), autour d'elle les dimensions (`Produits`, `Clients`, `Calendrier`). Chaque flèche est une relation « plusieurs à un » (∞ côté faits, 1 côté dimension). Schéma dessiné avec matplotlib.](figures/ch02-modele.png)

Ce dessin s'appelle un **schéma en étoile**. Il a quatre avantages décisifs sur la table unique avec colonnes collées : le **catalogue n'est stocké qu'une fois** (on change un prix à un seul endroit) ; le modèle gère **bien plus de lignes** que la grille d'Excel, car il les stocke en mémoire de façon compressée ; il permet de **compter des valeurs distinctes** (le nombre de clients différents), ce qu'un champ calculé de tableau croisé ne sait pas faire (2.2.4) ; et il prépare le terrain aux **mesures** de la sous-section suivante. La table `Calendrier` est une dimension particulière : une ligne par jour, avec le mois, le trimestre et l'année, indispensable pour comparer des périodes.

### 2.5.2 Les mesures DAX

**DAX** (*Data Analysis Expressions*) est le langage des formules du modèle de données. Il ressemble aux formules d'Excel, mais fonctionne différemment : au lieu de calculer une cellule, on définit une **mesure**, un calcul qui se **réévalue dans chaque case du tableau croisé**, selon les filtres de cette case. La même mesure donne le chiffre d'affaires de toute l'année dans le total général et celui d'une catégorie dans la ligne de cette catégorie.

C'est la différence avec la **colonne calculée**, évaluée **ligne par ligne** à la création (comme une colonne de formules) et stockée. Règle simple : une colonne calculée sert à **décrire** une ligne (le coût unitaire d'une vente) ; une mesure sert à **agréger** (une somme, un ratio, une comparaison).

Voici les mesures dont la gérante a besoin, en DAX (non exécuté, syntaxe à vérifier selon votre version) :

```text
CA := SUM ( Lignes[montant] )
CA Site := CALCULATE ( [CA], Lignes[canal] = "Site" )
Marge := SUMX ( Lignes, Lignes[montant] - Lignes[quantite] * RELATED ( Produits[cout_achat] ) )
Marge % := DIVIDE ( [Marge], [CA] )
Clients distincts := DISTINCTCOUNT ( Lignes[id_client] )
Panier moyen := DIVIDE ( [CA], DISTINCTCOUNT ( Lignes[id_commande] ) )
CA N-1 := CALCULATE ( [CA], SAMEPERIODLASTYEAR ( Calendrier[date] ) )
Croissance := DIVIDE ( [CA] - [CA N-1], [CA N-1] )
```

Quelques lignes méritent une explication. `CALCULATE` **modifie le contexte de filtre** avant d'évaluer sa première expression : `CALCULATE([CA]; canal = "Site")` calcule le chiffre d'affaires **comme si** le tableau était filtré sur le Site, quelle que soit la case où on le place. `SUMX` **itère** sur chaque ligne de la table, calcule une expression (`RELATED` va chercher le coût dans la table `Produits` grâce à la relation), puis additionne : c'est le même calcul que le `SOMMEPROD` de la section 2.1.6. `DIVIDE` renvoie un résultat vide, au lieu d'une erreur, quand le dénominateur est nul. `SAMEPERIODLASTYEAR` décale le contexte de dates d'un an : c'est l'une des fonctions d'**intelligence temporelle**, qui exigent une table `Calendrier` complète, sans trou.

Les résultats attendus, calculés en pandas sur le même classeur (et sur toutes les années pour la comparaison avec 2024) :

```text
CA                : 1 324 763,72
CA Site           : 617 715,45
Marge             : 639 810,88
Marge %           : 48,30 %
Clients distincts : 3 875
Panier moyen      : 102,33 € ( 12 946 commandes)
CA N-1 (2024)     : 1 189 461,17
Croissance        : 11,38 %
```

On lit : un chiffre d'affaires de 1 324 763,72 €, dont 617 715,45 € sur le Site ; une marge de 639 810,88 €, soit **48,30 %** du chiffre d'affaires ; **3 875** clients distincts ; un **panier moyen de 102,33 €** sur 12 946 commandes ; et une **croissance de 11,4 %** par rapport à 2024 (1 189 461,17 €). Remarquez que `Marge %` est un **ratio de sommes**, par construction (2.2.4) : c'est le comportement voulu d'une mesure, et c'est ce qui la distingue d'une moyenne de ratios. Chaque mesure s'adapte ensuite **au contexte du tableau** : placée dans un tableau croisé par catégorie, `Marge %` donne le taux de chaque catégorie, avec une seule définition.

> ⚠️ **Piège.** Le contexte de filtre est la notion la plus difficile de DAX, et la source des erreurs : une mesure qui donne un bon résultat dans le total peut en donner un faux dans une case, parce qu'un filtre d'une autre table s'y propage (ou ne s'y propage pas). **Testez chaque mesure sur un cas que vous savez calculer à la main**, comme nous l'avons fait ici avec pandas.

### 2.5.3 Macros VBA et scripts Office

Une **macro** enregistre une suite de gestes (mise en forme, copie, tri…) et la rejoue sur demande. Excel peut l'enregistrer pendant que vous travaillez, et la traduit en code **VBA** (*Visual Basic for Applications*). Un classeur qui contient des macros doit être enregistré au format `.xlsm`, que les messageries et les politiques de sécurité accueillent avec méfiance, à juste titre : les macros peuvent faire n'importe quoi sur votre poste.

Voici une macro minimale (non exécutée) qui actualise toutes les connexions de données puis exporte la feuille de présentation en PDF :

```text
Sub PublierRapport()
    ThisWorkbook.RefreshAll                         ' actualise requêtes et tableaux croisés
    Application.CalculateUntilAsyncQueriesDone      ' attend la fin des requêtes
    Sheets("Présentation").ExportAsFixedFormat Type:=xlTypePDF, _
        Filename:=ThisWorkbook.Path & "\rapport_" & Format(Date, "yyyy-mm-dd") & ".pdf"
End Sub
```

Les **Office Scripts** (Excel pour le web, scénarios automatisés par Power Automate) jouent le même rôle avec un langage différent, TypeScript :

```text
function main(workbook: ExcelScript.Workbook) {
    const feuille = workbook.getWorksheet("Données");
    const plage = feuille.getUsedRange();
    console.log("lignes :", plage.getRowCount());
}
```

Le premier script (VBA) tourne sur le poste, le second dans le nuage. Retenez trois principes. **Une macro ne remplace pas une formule** : tout ce qu'une formule fait, elle le fait de façon visible et recalculable, une macro non. **Toute macro doit être documentée**, car personne ne peut la relire dans l'interface d'Excel. Et **ne faites pas confiance aux macros reçues** : désactivez-les par défaut.

### 2.5.4 Quand quitter Excel : SQL ou Python ?

Excel est le bon outil dans beaucoup de situations, et le mauvais dans d'autres. Les signaux qui disent « il faut changer d'outil » sont assez nets :

| Signal | Pourquoi Excel peine | Alternative |
|---|---|---|
| Plus d'un million de lignes (ou plus de quelques centaines de milliers avec des formules) | limite de la grille, lenteur, fichier énorme | base de données et SQL (chapitre 3) |
| La même opération chaque semaine, avec plusieurs étapes | gestes à la main, erreurs | Power Query, ou un script Python |
| Plusieurs personnes modifient en même temps | conflits de versions | base partagée, dépôt de code |
| Il faut pouvoir **prouver** et **rejouer** l'analyse | formules dispersées, pas d'historique | script versionné, notebook (chapitre 4) |
| Calculs statistiques évolués (modèles, simulations) | fonctions limitées | Python ou R |

Une dernière illustration, pour **trianguler** : le chiffre d'affaires du Site en 2025, calculé trois fois, avec trois outils indépendants (la formule du tableur, une requête SQL sur la base, pandas).

```python
con = sqlite3.connect("donnees/boutique.db")
sql = """SELECT ROUND(SUM(l.montant), 2) FROM lignes_commande l JOIN commandes c ON c.id_commande = l.id_commande
         WHERE c.canal = 'Site' AND c.date_commande >= '2025-01-01'"""
print("SQL :", con.execute(sql).fetchone()[0])
print("pandas :", round(L.loc[L["canal"] == "Site", "montant"].sum(), 2))
```
<!--sortie-->
```text
SQL : 617715.45
pandas : 617715.45
```

Les deux donnent **617 715,45 €**, exactement le résultat de `SOMME.SI.ENS` de la section 2.1.4. Trois outils, un seul chiffre : c'est ce qui permet de s'y fier. Le chapitre suivant apprend à écrire cette requête SQL de zéro.

> ✅ **À retenir.**
> - Un **modèle de données** relie des tables par des clés **uniques** côté « un » ; contrôlez l'intégrité (clés uniques, pas de lignes orphelines) avant de déclarer une relation.
> - Une **mesure DAX** s'évalue dans chaque case selon son contexte de filtre ; une colonne calculée est évaluée ligne par ligne. `CALCULATE` modifie le contexte ; un ratio de mesures est un **ratio de sommes**.
> - Une **macro** automatise mais ne se lit pas comme une formule : documentez-la, méfiez-vous de celles qu'on vous envoie.
> - **Changez d'outil** quand les données dépassent la grille, quand le traitement doit être rejoué sans personne, ou quand il faut le prouver : SQL, Python, Power Query.
> - **Triangulez** : un même chiffre obtenu par trois outils (ici 617 715,45 €) est un chiffre fiable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.


## 2.6 ➕ Pour aller plus loin : Google Sheets et Looker Studio

> 🧭 **Section complémentaire.** Beaucoup d'équipes travaillent dans le nuage plutôt que dans un fichier : **Google Sheets** pour le tableur, **Looker Studio** pour les tableaux de bord. Cette section en présente l'esprit, les fonctions qui n'existent pas dans Excel, et les équivalences avec ce que vous avez appris. **Rien ici n'a pu être exécuté** (nous n'avons pas de compte ni d'accès à ces services) : tous les exemples de formules sont **non exécutés** et à vérifier dans votre environnement ; nous recalculons en SQL ou en pandas les résultats qu'ils doivent donner.


### 2.6.1 Google Sheets : ce qui ressemble, ce qui diffère

Google Sheets reprend l'essentiel du vocabulaire d'Excel : cellules, plages, références relatives et absolues, tableaux croisés dynamiques, la plupart des fonctions de la section 2.1 (`SUM`, `SUMIFS`, `IF`, `VLOOKUP`, `XLOOKUP`, `FILTER`, `SORT`, `UNIQUE`…). Un classeur Excel s'importe, un classeur Sheets s'exporte au format `.xlsx`, avec des différences possibles sur les fonctions propres à chacun et la mise en forme. Dans l'interface en français, les noms de fonctions sont traduits comme dans Excel (avec quelques écarts : à vérifier).

Les différences qui comptent pour un analyste :

- **La collaboration en temps réel** est native : plusieurs personnes éditent le même document, avec commentaires, suggestions, historique des versions. C'est le grand avantage, et le risque (modifications non contrôlées : section 2.4).
- **Les formules sur toute une colonne** s'écrivent avec `ARRAYFORMULA` : `=ARRAYFORMULA(J2:J * K2:K * (1 - L2:L / 100))` applique le calcul à chaque ligne sans recopier la formule.
- **`QUERY`** interroge une plage avec un langage proche de SQL (voir ci-dessous) : c'est la fonction la plus puissante de Sheets, et elle n'a pas d'équivalent direct dans Excel.
- **`IMPORTRANGE`** lit une plage d'**un autre document** Sheets : `=IMPORTRANGE("adresse_du_document" ; "Lignes!A1:M")`, après autorisation d'accès. Pratique, mais fragile (le document source peut être déplacé, supprimé, ou son accès retiré).
- Des fonctions utiles propres à Sheets : `SPLIT` (découper un texte), `IMAGE`, `GOOGLEFINANCE` (cours de bourse), `REGEXEXTRACT` (expressions régulières).
- **La puissance de calcul est limitée** : un document Sheets accepte un nombre maximal de cellules (de l'ordre de dix millions, **à vérifier**), et devient lent bien avant. Pour des volumes importants, la même conclusion qu'avec Excel s'impose (2.5.4).
- L'automatisation se fait avec **Google Apps Script**, un langage dérivé de JavaScript, comparable aux macros VBA (non exécuté ici).

#### QUERY : du SQL dans une cellule

La fonction `QUERY(données ; requête ; en-têtes)` prend une plage et une requête écrite dans un petit langage inspiré de SQL. Les colonnes sont désignées par leur **lettre** (`Col1`, `Col2`… si la plage est une formule). Pour lister le chiffre d'affaires du Site par catégorie, du plus grand au plus petit :

```text
=QUERY(Lignes!A1:M ; "select I, sum(M) where E = 'Site' group by I order by sum(M) desc label sum(M) 'CA'" ; 1)
```

(Non exécuté ; `I` est la colonne `categorie`, `M` la colonne `montant`, `E` la colonne `canal`.) Cette requête est exactement une requête SQL de regroupement : `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`. Nous pouvons donc **vérifier le résultat attendu** en SQL, avec SQLite, sur les mêmes données.

```python
con = sqlite3.connect(":memory:")
L.to_sql("lignes", con, index=False)
req = "SELECT categorie, ROUND(SUM(montant), 2) AS CA FROM lignes WHERE canal = 'Site' GROUP BY categorie ORDER BY CA DESC"
res_sql = pd.read_sql(req, con)
print(res_sql.head(4).to_string(index=False))
```
<!--sortie-->
```text
 categorie        CA
    Jardin 166201.16
    Maison 140788.49
Décoration 118835.74
   Cuisine 109609.91
```

```text
écart maximal entre la requête SQL et la colonne « Site » du tableau croisé de la section 2.2 : 0.0
total des six catégories : 617 715,45
```

La requête SQL, et donc la fonction `QUERY` qui en est le miroir, donne le **Jardin en tête (166 201,16 €)**, devant la Maison (140 788,49 €), la Décoration (118 835,74 €) et la Cuisine (109 609,91 €). Elle retombe exactement sur la colonne « Site » du tableau croisé de la section 2.2, et le total des six catégories (617 715,45 €) est le chiffre d'affaires du Site. Apprendre SQL (chapitre 3) est donc aussi la meilleure façon d'apprendre `QUERY`.

### 2.6.2 Looker Studio : des tableaux de bord reliés à des sources

**Looker Studio** est un outil de tableaux de bord en ligne (anciennement « Data Studio »). Il ne stocke pas les données : il se **connecte** à des sources (feuilles Google Sheets, fichiers CSV, bases de données, services d'analyse du web…) et affiche des graphiques, des tableaux et des indicateurs qui se mettent à jour quand la source change. Trois notions suffisent pour démarrer :

- une **dimension** est un champ qui décrit (catégorie, canal, mois) ; une **métrique** est un champ que l'on agrège (montant, quantité). C'est la distinction « lignes et colonnes » contre « valeurs » d'un tableau croisé ;
- un **champ calculé** se définit par une formule sur les champs de la source : `SUM(montant) / COUNT_DISTINCT(id_commande)` donne le **panier moyen**, un ratio de sommes (2.2.4), dont nous avons calculé la valeur attendue en 2.5.2 : 102,33 € ;
- les **filtres** et **contrôles** (liste déroulante, sélecteur de dates) laissent le lecteur explorer le tableau de bord seul.

Les points de vigilance sont ceux de tout tableau de bord relié à des données vivantes. **La fraîcheur** : le tableau de bord peut afficher des données mises en cache (une actualisation manuelle ou programmée peut être nécessaire). **L'accès** : celui qui voit le tableau de bord voit-il les données de la source ? Les identifiants de connexion et les droits sont à régler. **La responsabilité** : si la source change (une colonne renommée), le tableau de bord casse, et le lecteur ne le sait pas toujours. **La confidentialité** : relier des données personnelles de clients à un service en ligne demande de savoir où elles sont hébergées et qui y a accès (volume II, chapitre complémentaire sur la confidentialité). Le volume IV de la série (visualisation et communication) reviendra sur la conception de tableaux de bord.

### 2.6.3 Tableau d'équivalences

Ce tableau rassemble les opérations du chapitre dans les cinq outils que vous rencontrerez. Il sert de **pense-bête** quand vous passez de l'un à l'autre.

| Opération | Excel | Google Sheets | SQL | pandas |
|---|---|---|---|---|
| Somme conditionnelle | `SOMME.SI.ENS` | `SUMIFS` | `SELECT SUM(…) … WHERE …` | `df.loc[cond, "col"].sum()` |
| Compter sous condition | `NB.SI.ENS` | `COUNTIFS` | `SELECT COUNT(*) … WHERE …` | `(cond).sum()` |
| Recherche | `RECHERCHEX` | `XLOOKUP`, `VLOOKUP` | `JOIN` | `merge` |
| Valeurs distinctes | `UNIQUE` | `UNIQUE` | `SELECT DISTINCT` | `drop_duplicates`, `unique` |
| Filtrer | `FILTRE` | `FILTER` | `WHERE` | masque booléen |
| Trier | `TRIER` | `SORT` | `ORDER BY` | `sort_values` |
| Regrouper et agréger | tableau croisé dynamique | tableau croisé, `QUERY` | `GROUP BY` | `groupby`, `pivot_table` |
| Requête dans une cellule | — | `QUERY` | — | — |
| Découper un texte | `FRACTIONNER.TEXTE`, assistant | `SPLIT` | `SUBSTR`, `INSTR` | `str.split` |
| Dépivoter | Power Query | formules, `QUERY` | `UNION ALL` | `melt` |
| Calcul sur toute une colonne | formule recopiée, tableaux dynamiques | `ARRAYFORMULA` | expression dans `SELECT` | vectorisation |

> ✅ **À retenir.**
> - **Google Sheets** ressemble à Excel pour les fonctions et les tableaux croisés ; il se distingue par la **collaboration**, `QUERY`, `IMPORTRANGE` et `ARRAYFORMULA`. Ses limites de volume sont les mêmes qu'Excel, en plus strictes.
> - **`QUERY` est du SQL** : le résultat attendu se vérifie par une requête SQL (ici, 617 715,45 € répartis sur 6 catégories, Jardin en tête).
> - **Looker Studio** relie des tableaux de bord à des sources vivantes : pensez **fraîcheur, droits d'accès, confidentialité**.
> - Un **tableau d'équivalences** entre Excel, Sheets, SQL et pandas évite de réapprendre chaque fois.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.


## Bilan du chapitre 2

Vous savez maintenant :

- **écrire et lire des formules** : références relatives, absolues et mixtes, plages nommées, tableaux structurés qui grandissent tout seuls ;
- **agréger sous conditions** (`SOMME.SI.ENS`, `NB.SI.ENS`, `MOYENNE.SI.ENS`) et **décider** (`SI`, `SI.CONDITIONS`, `ET`, `OU`, `SIERREUR`, en sachant que ce dernier masque toutes les erreurs) ;
- **chercher** une valeur dans une autre table (`RECHERCHEV` et ses pièges, `INDEX+EQUIV`, `RECHERCHEX`), en vérifiant que la clé est **unique** ;
- **nettoyer du texte** et **manipuler des dates** (numéros de série, `FIN.MOIS`, `DATEDIF`, jours ouvrés), et repérer une **inversion jour/mois** ;
- **reconnaître les erreurs** d'Excel (`#N/A`, `#REF!`, `#DIV/0!`, `#VALEUR!`…) et traduire les fonctions entre l'anglais et le français ;
- **construire un tableau croisé dynamique**, regrouper des dates, afficher des proportions, comprendre qu'un champ calculé donne un **ratio de sommes**, et **recouper** le tableau par un autre chemin ;
- **importer et nettoyer un export désordonné** avec Power Query (étapes rejouables), en réglant le délimiteur, l'**encodage** et les **paramètres régionaux**, en comptant les lignes à chaque étape et en **contrôlant un total** ;
- **structurer un classeur** (README, données, calculs, présentation), tenir des **données ordonnées**, séparer les **hypothèses** des formules, tenir une **feuille de contrôles** et reconnaître les erreurs classiques de tableur ;
- (en option) décrire un **modèle de données** en étoile, écrire des **mesures DAX**, situer les **macros** et les **scripts Office**, décider **quand quitter Excel** ; situer **Google Sheets** (`QUERY`, `IMPORTRANGE`, `ARRAYFORMULA`) et **Looker Studio**.

Le chapitre a mis des chiffres sur des habitudes qui restent souvent des slogans. Tous ces chiffres ont été **recoupés par un second outil** (pandas ou SQL).

| Ce que nous avons mesuré | Résultat |
|---|---|
| Le classeur de la gérante | 29 827 lignes, 12 946 commandes, 3 875 clients, **1 324 763,72 €** |
| 25 formules vérifiées (LibreOffice) contre pandas | écart maximal nul au centime |
| Recalcul ligne par ligne contre colonne `montant` | **8 centimes** d'écart (arrondi à la ligne) |
| `SOMME` sur une plage trop courte de 800 lignes | **33 638,83 €** disparus, aucun message |
| Marge brute 2025 | 639 810,88 € (**48,30 %** du chiffre d'affaires) |
| Tableau croisé : 18 cases (catégorie × canal), 72 cases (catégorie × mois) | écart nul contre `SOMME.SI.ENS` |
| 500 lignes copiées deux fois | total gonflé de **20 866,33 €**, doublons détectés par les contrôles |
| Export de caisse : 289 lignes brutes → lignes de vente | **280** (3 de titre, 1 en-tête, 4 en-têtes répétés, 1 total) |
| Réparation des montants manquants contre le total de l'export | **2,62 €** d'écart : des remises ignorées |
| Jointure sur le nom d'article (non unique) | 280 lignes → **560**, total doublé |
| Marge 2026 selon l'hypothèse de volume | 699 147,47 € (+ 5 %) ou 665 854,73 € (stable) |
| Chiffre d'affaires du Site, trois outils (formule, SQL, pandas) | **617 715,45 €** partout |

Le fil conducteur du chapitre tient en une phrase : **un chiffre de tableur n'est fiable que s'il peut être recoupé**. Le recoupement prend plusieurs formes : un total comparé à une source indépendante, le nombre de lignes avant et après chaque transformation, la même requête dans deux outils, une feuille de contrôles. Quelles que soient les fonctions que vous maîtrisez, la discipline reste la même.

> ⚠️ **Ce que ce chapitre n'a pas pu vérifier.** Excel n'était pas installé : les formules ont été calculées avec LibreOffice, qui peut différer d'Excel (dans un cas, une racine carrée d'un nombre négatif donne `#VALEUR!` au lieu de `#NOMBRE!`, et une clé numérique est comparée à du texte avec plus d'indulgence). Les codes de format de `TEXTE` dépendent de la langue d'Excel. Les **tableaux croisés dynamiques réels**, **Power Query**, **Power Pivot et DAX**, **VBA**, **Office Scripts**, **Google Sheets** et **Looker Studio** n'ont pas été exécutés : les scripts correspondants sont signalés « non exécutés », avec le résultat attendu recalculé en pandas ou en SQL. Les menus et les libellés des « copies d'écran » (des maquettes dessinées) sont **à vérifier** dans votre version.

Le chapitre 3 apprend le **SQL**, le langage des bases de données. Vous y retrouverez la plupart des questions de ce chapitre (« combien, pour quelle catégorie, quel mois ? »), écrites cette fois dans un langage qui traite sans difficulté des millions de lignes, qui se **rejoue** exactement et qui ne dépend d'aucun menu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 (explorer et contrôler le classeur, agréger sous conditions, enrichir par recherche, nettoyer texte et dates, recouper un tableau croisé, rejouer une chaîne Power Query, auditer un classeur, trianguler Excel, SQL et pandas) et exercices 2.1 à 2.12.
