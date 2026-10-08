# Chapitre 2 : Tableaux de bord

> « Un tableau de bord ne sert pas à tout montrer : il sert à savoir quoi faire lundi matin. »


Un lundi matin, la gérante s'arrête devant votre bureau. « Chaque semaine, tu m'envoies un fichier. Je l'ouvre, je cherche ce qui m'intéresse, je ne trouve pas, je te rappelle. **Je veux voir chaque lundi où nous en sommes, sans te demander un fichier.** Et que ça me dise tout seul quand quelque chose ne va pas. »

La demande semble technique (« fais-moi un tableau de bord »), mais elle contient trois exigences très différentes. La première est **technique** : il faut des données qui se mettent à jour seules, organisées pour que les chiffres soient toujours calculés de la même façon. La deuxième est **visuelle** : il faut que la page se lise en quelques secondes, sans mode d'emploi. La troisième est **humaine** : il faut que la gérante s'en serve vraiment, que le jour où le tableau de bord signale un problème, elle sache ce qu'elle décidera. Un tableau de bord réussi est un **outil de décision** ; un tableau de bord raté est un joli tableau que l'on ouvre deux semaines, puis plus jamais.

Le chapitre précédent vous a donné les principes : choisir le bon graphique, soigner la mise en page, ne pas tromper. Ce chapitre les met en œuvre dans des **outils de tableaux de bord**, ceux que l'on rencontre le plus en entreprise, et il montre surtout ce qu'ils ont en commun, parce que les menus changent d'une version à l'autre alors que les idées durent.

> ⚠️ **Ce que ce chapitre ne fait pas, et pourquoi.** Power BI, Tableau, Looker, Metabase, Superset et Qlik sont des produits que **nous n'avons pas exécutés** pour écrire ce livre. Nous ne montrons donc **aucune capture de leurs écrans** et nous ne prétendons pas décrire leurs menus : ils changent d'une version à l'autre, et ce que nous en disons est à **vérifier dans la documentation de votre version**. Les figures de ce chapitre sont des **maquettes dessinées** avec matplotlib (rectangles génériques, aucune identité d'un produit), ou des graphiques calculés sur les données de la boutique. Ce qui peut être **vérifié** l'est : le modèle de données, les mesures, les filtres de sécurité et les chiffres de la page finale sont recalculés ici avec pandas et SQL, et chaque nombre du texte vient d'un calcul exécuté.

## Le chemin de ce chapitre

Le chapitre suit la demande de la gérante, de la donnée à l'écran, puis du premier outil au choix d'un outil.

- **2.1 Power BI : modèle, visuels, publication.** Avant de dessiner quoi que ce soit, on organise les données en **étoile** (une table de faits, des dimensions), on définit des **mesures** qui se recalculent selon les filtres, on choisit des **visuels**, puis on **publie** et on planifie l'actualisation. Power BI sert d'exemple de l'approche « modèle d'abord ».
- **2.2 Tableau : feuilles, tableaux de bord, partage.** Tableau illustre l'approche inverse, plus **exploratoire** : on compose des *feuilles* en glissant des champs sur des **marques** (position, couleur, taille), on ajoute des **calculs de table** et des **niveaux de détail**, puis on assemble les feuilles en tableau de bord. Les deux approches se rejoignent.
- **2.3 Conception d'un tableau de bord selon les besoins des utilisateurs.** La section la plus importante : **partir de la décision**, choisir peu d'indicateurs, les ranger en trois niveaux (vue d'ensemble, analyse, détail), tester en cinq secondes, **valider les chiffres** et prévoir l'**adoption**. Nous construisons la page complète de la gérante.
- **2.4 ➕ Power BI avancé.** Le langage des mesures (DAX), la préparation des données (Power Query), la **sécurité au niveau des lignes** et le déploiement, avec des équivalents pandas qui permettent de **vérifier** chaque résultat.
- **2.5 ➕ Looker, Metabase, Superset, Qlik.** Quatre autres familles d'outils, ce qui les distingue, et une méthode pour **choisir** sans se laisser guider par la marque.

Le chapitre se termine par un bilan, et le **cahier** propose huit applications (modèle en étoile, mesures, calculs de table, critique de tableaux de bord, sécurité, choix d'outil…) et douze exercices.

> 💡 **Intuition.** Un outil de tableaux de bord est une **chaîne de montage** : les données brutes entrent à gauche, un chiffre juste et lisible sort à droite, et à chaque étape on peut se tromper. La qualité d'un tableau de bord se joue **en amont** (le modèle, les définitions) autant qu'en aval (les couleurs et la disposition).

## Les données du chapitre

Nous reprenons la boutique des volumes précédents : les commandes de 2023 à 2025, les clients, les produits, les livraisons, les sessions du site, les stocks. Toutes les données sont **simulées**. Nous utilisons un fichier supplémentaire, `villes.csv`, qui associe chaque ville fictive à une **région fictive** (quatre régions, dans un plan inventé) : elle sert à illustrer la sécurité par région, sans aucune géographie réelle.

> 📦 **Les données.** `commandes.csv`, `lignes_commande.csv` (83 905 lignes, 2023 à 2025), `produits.csv`, `clients.csv`, `villes.csv`, `livraisons.csv`, `sessions_web.csv`, `stock_quotidien.csv`, `jours_exploitation.csv`. Le script `build/outils_ch02.py` contient le chargement, le modèle en étoile et le dessin des maquettes ; les définitions des indicateurs sont celles du volume III, chapitre 6 (KPI).

Deux rappels des volumes précédents serviront souvent. D'abord, **les 120 produits portent seulement 60 noms** : on relie toujours les tables par l'**identifiant** du produit, jamais par son nom (volume II, section 2.2.5). Ensuite, les chiffres d'affaires de la boutique sont en **euros TTC** pour les ventes et la marge se calcule **hors taxes** avec une TVA fixée à 20 % **pour l'illustration** (volume III, chapitre 6).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 et exercices 2.1 à 2.12 ; chacun renvoie à la section du livre qui l'éclaire.


## 2.1 Power BI : modèle, visuels, publication

Avant d'ouvrir un outil de tableaux de bord, il faut comprendre **ce qu'il fait entre vos données et l'écran**. Cette section décrit la chaîne complète, avec Power BI comme exemple d'une approche « **modèle d'abord** » : on organise les données, on définit les calculs une fois, puis on dessine. Nous reproduisons chaque étape en pandas, pour que vous puissiez **vérifier** ce que l'outil affiche.

> 🧭 **Une précaution.** Power BI est un produit commercial que nous n'avons **pas exécuté**. Les notions (modèle, mesures, visuels, publication) sont stables ; les noms de menus, les limites de la version gratuite, les licences de partage et les fonctions précises **changent** : vérifiez-les dans la documentation de votre version. Les figures sont des maquettes dessinées, pas des captures.

### 2.1.1 Ce que fait un outil de tableaux de bord

Un outil de tableaux de bord reçoit des tables en entrée et produit une page interactive en sortie. Entre les deux, le même flux se retrouve partout, quel que soit le produit.

1. **Se connecter aux sources** : fichiers, bases de données, services en ligne.
2. **Préparer** les données : filtrer, corriger les types, fusionner, regrouper (c'est le rôle de Power Query dans Power BI).
3. **Modéliser** : relier les tables entre elles, dire laquelle contient les événements (les faits) et lesquelles les décrivent (les dimensions).
4. **Définir des mesures** : les calculs (chiffre d'affaires, taux de marge, panier moyen) écrits **une fois** et réutilisés partout.
5. **Dessiner** : poser des visuels sur une page, régler les filtres et les interactions.
6. **Publier et partager** : envoyer le résultat sur un serveur, choisir qui a le droit de le voir.
7. **Actualiser** : mettre à jour les données automatiquement, à heure fixe.

![Le flux d'un outil de tableaux de bord, étape par étape : ce que fait l'outil (milieu) et son équivalent à la main (bas). Maquette dessinée, pas une capture.](figures/ch02-flux-bi.png)


La figure met en regard chaque étape et son équivalent **à la main** en Python. Ce n'est pas un détour pédagogique : **c'est la méthode de contrôle de l'analyste**. Un tableau de bord affiche un chiffre ; si l'on est incapable de le recalculer autrement, on ne peut pas répondre à la gérante le jour où elle demande « pourquoi ce chiffre n'est pas le même que celui de la comptabilité ? ».

> 💡 **Intuition.** Un outil de tableaux de bord **n'invente aucun calcul** : il automatise des jointures, des filtres, des regroupements et des sommes. Tout ce qu'il affiche peut se reproduire avec un tableur, du SQL ou pandas. C'est ce qui permet de **vérifier croisé** (voir 2.3.5).

Deux modes de connexion existent presque partout. En mode **import**, l'outil copie les données dans sa mémoire : les visuels réagissent instantanément, mais les données ne sont à jour qu'à la dernière actualisation. En mode **requête directe**, il interroge la base à chaque clic : les données sont fraîches, mais chaque visuel dépend de la vitesse de la base. Pour un tableau de bord hebdomadaire de la boutique, l'import suffit largement ; la requête directe se justifie pour un suivi presque en temps réel, avec une base conçue pour cela.

### 2.1.2 Le modèle en étoile

Les lignes de commande de la boutique (qui a acheté quoi, quand, par quel canal) sont des **événements**. Les produits, les clients, les jours et les canaux sont des **descriptions**. Séparer les deux donne le **modèle en étoile** (*star schema*) : au centre, une **table de faits** (une ligne par événement, avec des chiffres : quantité, montant, marge) ; autour, des **tables de dimensions** (une ligne par produit, par client, par jour, par canal, avec des attributs : catégorie, région, mois, type de canal).

Chaque relation est **de un à plusieurs** : un produit apparaît dans beaucoup de lignes de faits, mais chaque ligne de faits concerne un seul produit. La clé d'une dimension doit donc être **unique**, et chaque ligne de faits doit avoir une correspondance. C'est exactement le contrôle d'effectifs du volume II (section 2.2.2), appliqué au modèle entier.

```python
faits = star["fait_ventes"]
controle = O.controle_etoile(star)
print(controle.to_string(index=False))
print("lignes de faits :", len(faits), "| CA 2023-2025 :", round(faits["montant"].sum()))
```
<!--sortie-->
```text
  dimension  lignes  cle_unique  faits_orphelins
   dim_date    1096        True                0
dim_produit     120        True                0
 dim_client    6000        True                0
  dim_canal       3        True                0
lignes de faits : 83905 | CA 2023-2025 : 3653157
```

Les quatre dimensions ont des clés uniques (1 096 jours, 120 produits, 6 000 clients, 3 canaux) et **aucune ligne de faits n'est orpheline** : chacune des 83 905 lignes trouve son jour, son produit, son client et son canal. Le modèle est sain, et le chiffre d'affaires total de la période, 3 653 157 €, est celui qu'on obtient en sommant les lignes sans aucune jointure.

![Le modèle en étoile de la boutique, calculé par pandas : une table de faits au centre, quatre dimensions autour. Chaque relation relie une clé unique (1) à plusieurs lignes de faits (n). Maquette dessinée avec les effectifs réels.](figures/ch02-schema-etoile.png)


La dimension des **dates** mérite une remarque : on la construit **explicitement**, avec un jour par ligne sur toute la période (même les jours sans vente), et des colonnes utiles (année, trimestre, mois, début de semaine, jour de la semaine, jour de promotion). Les calculs de comparaison dans le temps (« même période de l'an dernier », « cumul depuis le début de l'année », voir 2.4.1) ont **besoin** d'un calendrier complet et continu : les dates que l'on déduirait des seules ventes auraient des trous.

#### Le piège de la clé qui multiplie

Relier les tables par une clé qui n'est pas unique est l'erreur la plus fréquente, et la plus discrète : l'outil ne signale rien, les chiffres sont simplement faux. Un exemple minuscule suffit. Dans cette boutique-jouet, deux produits différents, P1 et P3, portent le même nom « Vase » :

| id_ligne | nom_produit | montant |
|---|---|---|
| 1 | Vase | 20 |
| 2 | Bougie | 30 |
| 3 | Vase | 20 |
| 4 | Bougie | 30 |
| 5 | Vase | 10 |
| 6 | Plaid | 50 |

Les six lignes totalisent 160 €. Si l'on relie à la dimension des produits **par le nom**, chaque ligne « Vase » trouve **deux** correspondances (P1 et P3) : elle est comptée deux fois. On obtient neuf lignes et 210 € au lieu de 160 €, soit les 50 € des trois vases comptés en double. Dans la boutique, **chaque nom de produit est porté par deux produits** : c'est le piège du volume II. Essayons.


```python
dim_prod = star["dim_produit"][["id_produit", "nom_produit"]]
par_nom = faits.merge(dim_prod, on="id_produit").drop(columns="id_produit").merge(dim_prod.drop(columns="id_produit"), on="nom_produit")
print(len(faits), "->", len(par_nom), "lignes | CA :", round(faits["montant"].sum()), "->", round(par_nom["montant"].sum()))
```
<!--sortie-->
```text
83905 -> 167810 lignes | CA : 3653157 -> 7306315
```

Le chiffre d'affaires est **doublé** (7,31 M€ au lieu de 3,65 M€) sans qu'aucune erreur n'apparaisse. Dans un outil de tableaux de bord, ce sont les **relations** du modèle qui jouent ce rôle de jointure : si l'on en déclare une sur une colonne non unique, l'outil refuse parfois (il demande une relation « plusieurs à plusieurs »), parfois accepte et calcule faux. Règle : **relier par des identifiants uniques, jamais par des libellés**, et vérifier les effectifs après chaque relation.

> ⚠️ **Piège.** Une relation « plusieurs à plusieurs » est presque toujours le **symptôme** d'une dimension mal construite, pas une fonctionnalité à utiliser. Avant de l'accepter, cherchez la colonne qui rend la clé unique (ici, `id_produit`).

### 2.1.3 Mesures et colonnes calculées

Un outil de tableaux de bord propose deux manières de calculer.

Une **colonne calculée** ajoute une colonne à une table : pour **chaque ligne**, on calcule une valeur (la marge de la ligne, par exemple). Elle est calculée **à l'actualisation** et **stockée** : elle occupe de la mémoire, et sa valeur ne dépend d'aucun filtre.

Une **mesure** n'est pas stockée. C'est une **recette** : « somme des montants », « somme des marges divisée par somme du chiffre d'affaires hors taxes ». Elle se calcule **au moment de l'affichage**, **pour le contexte de filtres courant** : si l'on filtre sur la catégorie Jardin, la mesure se recalcule pour les seules lignes de cette catégorie. C'est pourquoi **la même mesure** donne des valeurs différentes dans chaque case d'un tableau croisé.


La mesure « chiffre d'affaires » vaut 1 324 764 € sur l'ensemble de 2025, 353 955 € dans le contexte « catégorie Jardin », et 166 201 € dans le contexte « catégorie Jardin **et** canal Site » : une seule recette, trois contextes.

Cette distinction a une conséquence pratique, qu'illustrent trois règles.

**Règle 1 : un ratio est une mesure, jamais une colonne que l'on moyenne.** Le taux de marge d'un ensemble de lignes est la **somme des marges divisée par la somme du chiffre d'affaires**, pas la moyenne des taux. Si l'on calcule un taux par catégorie puis qu'on en fait la moyenne, on donne autant de poids à la petite catégorie Papeterie qu'à Jardin :

```python
par_cat = v25.groupby("categorie").agg(ca=("montant", "sum"), marge=("marge_ht", "sum"))
par_cat["taux"] = par_cat["marge"] / (par_cat["ca"] / 1.2)
global_ = v25["marge_ht"].sum() / (v25["montant"].sum() / 1.2)
print(f"taux global {global_:.1%} | moyenne des taux par catégorie {par_cat['taux'].mean():.1%}")
```
<!--sortie-->
```text
taux global 38.0% | moyenne des taux par catégorie 37.5%
```

L'écart est ici modeste (38,0 % contre 37,5 %), parce que les taux de marge des catégories sont proches ; il serait considérable si les tailles et les taux différaient davantage. Le principe, lui, ne se discute pas : **le bon taux est celui de la recette « somme sur somme »**, définie une fois dans une mesure.

**Règle 2 : certaines mesures ne s'additionnent pas.** Le nombre de **commandes** est un comptage de valeurs **distinctes** : une commande qui contient un vase et une bougie compte pour une commande, mais elle apparaît dans deux catégories.

```python
n_total = v25["id_commande"].nunique()
n_cat = v25.groupby("categorie")["id_commande"].nunique()
print("commandes 2025 :", n_total, "| somme des catégories :", n_cat.sum())
print(n_cat.to_string())
```
<!--sortie-->
```text
commandes 2025 : 12946 | somme des catégories : 25163
categorie
Bien-être     3224
Cuisine       4381
Décoration    4912
Jardin        4315
Maison        4487
Papeterie     3844
```

Les six lignes d'un tableau croisé par catégorie totalisent **25 163 commandes**, alors que la boutique n'en a reçu que **12 946** : le total d'un tableau de bord ne doit **jamais** être la somme des lignes d'une mesure non additive. Les outils sérieux calculent le total **en refaisant la mesure sur l'ensemble** (c'est ce qui se passe dans une mesure bien écrite) ; mais une colonne calculée ou un tableau déjà agrégé fige l'erreur.

**Règle 3 : la mesure se définit dans le modèle, pas dans chaque visuel.** Si deux visuels recalculent chacun le « panier moyen » à leur façon, on aura un jour deux chiffres différents sur la même page. Les définitions du volume III (chapitre 6, section 6.1.2) se traduisent donc en **mesures nommées**, écrites une fois, documentées, et utilisées par tout le monde.

> 📐 **Pour qui veut la formule.** Pour une table de faits $T$ et un contexte de filtres $C$ (l'ensemble des lignes retenues), une mesure est une fonction $m(T_C)$ de l'ensemble filtré. La somme et le comptage de lignes sont additifs ($m(A\cup B)=m(A)+m(B)$ si $A$ et $B$ sont disjoints) ; le comptage de valeurs distinctes, le ratio et la médiane ne le sont pas. Une **colonne calculée** est une fonction de **la ligne seule** : elle ne peut donc ni recalculer un ratio sur un groupe, ni compter des valeurs distinctes.

### 2.1.4 Les visuels

Le choix d'un visuel obéit aux principes du chapitre 1 (section 1.1) : la **question** décide du graphique. Les outils de tableaux de bord proposent quelques familles, et il est utile de les connaître par **ce qu'elles permettent de lire**.

![Les familles de visuels d'un outil de tableaux de bord, redessinées avec les données de la boutique : chaque visuel répond à une question différente. Maquette dessinée, pas une capture.](figures/ch02-visuels.png)


- **La carte** (un chiffre) : à lire d'un coup, avec un repère de comparaison (l'an dernier, l'objectif).
- **Les barres** : comparer des catégories ; le tri décroissant est le réglage le plus utile.
- **La courbe** : suivre une évolution ; on y superpose la période de référence.
- **Le tableau** : retrouver une valeur exacte, ou un **tableau croisé** (matrice) pour croiser deux dimensions avec une mise en forme conditionnelle.
- **Le nuage** : voir une relation entre deux mesures, à utiliser avec parcimonie dans un tableau de bord de direction.
- **Les barres à 100 %** : comparer des parts, avec peu de catégories.
- **Les segments** (*slicers*, filtres) : laisser le lecteur choisir une période, un canal, une catégorie.

Deux fonctionnalités changent la nature d'un visuel. Les **interactions croisées** : cliquer sur une barre filtre (ou met en évidence) tous les autres visuels de la page. C'est puissant, et c'est aussi la source d'erreurs de lecture : un lecteur qui a cliqué sans s'en souvenir lit des chiffres filtrés comme s'ils étaient globaux. Il faut donc **indiquer clairement** quels filtres sont actifs, prévoir un bouton de remise à zéro, et décider **visuel par visuel** s'il réagit ou non (les cartes de chiffre global, par exemple, ne devraient pas réagir). Les **infobulles** (*tooltips*) ajoutent du détail au survol sans encombrer la page ; elles ne fonctionnent pas sur téléphone ou sur papier : **n'y cachez jamais une information indispensable**.

> ⚠️ **Piège.** Un visuel qui n'existe que par défaut : un graphique en secteurs avec dix catégories, un double axe, un 3D. Les outils les proposent, la page les accepte, mais les principes du chapitre 1 (sections 1.1, 1.2 et 1.4) s'appliquent **comme ailleurs**.

### 2.1.5 Publier, partager, actualiser

Un rapport sur l'ordinateur de l'analyste n'est pas un tableau de bord : c'est un brouillon. La **publication** envoie le rapport (et son modèle de données) dans un **espace de travail** en ligne, d'où d'autres personnes peuvent le consulter dans un navigateur. Quatre décisions accompagnent toujours la publication.

**Qui voit quoi ?** On donne les droits à des **groupes** (« direction », « responsables de région »), pas à des personnes, et on choisit entre partager le **rapport** (lecture seule) et le **jeu de données** (qui permet à d'autres de construire leurs propres rapports sur le même modèle). Selon les offres, la consultation par d'autres personnes peut exiger des **licences** payantes : renseignez-vous **avant** de promettre un partage à toute l'équipe.

> ⚠️ **Piège de sécurité.** Certains outils offrent une option de **publication sur le web**, qui rend le rapport lisible **par n'importe qui sur Internet, sans authentification**. Elle ne convient qu'à des données **déjà publiques**. Ne l'utilisez jamais pour les chiffres de la boutique, et vérifiez dans la documentation ce que fait chaque option de partage **avant** de cliquer.

**Quand les données sont-elles à jour ?** On planifie une **actualisation** (par exemple chaque nuit). Si les données viennent d'un fichier ou d'une base **sur un poste ou un réseau local**, il faut en général une **passerelle** (un petit programme qui relie le serveur en ligne à vos données). Une actualisation peut **échouer** sans bruit : on active les notifications d'échec, et on **affiche sur la page la date des données** (« données actualisées le 31/12/2025 »), comme la page de la gérante le fait en 2.3.

**Quelle taille ?** Le temps de réponse d'un tableau de bord dépend du volume de données chargées. Une technique classique est l'**agrégation** : on garde la table fine pour le détail et une **table agrégée** pour les vues d'ensemble. Nous la simulons :

```python
sem = ventes["date_commande"].dt.to_period("W-SUN").dt.start_time
agrege = ventes.assign(semaine=sem).groupby(["semaine", "canal", "categorie"], as_index=False).agg(ca=("montant", "sum"), commandes=("id_commande", "nunique"))
print(len(ventes), "->", len(agrege), "lignes | CA identique :", np.isclose(ventes["montant"].sum(), agrege["ca"].sum()))
print("commandes distinctes :", ventes["id_commande"].nunique(), "| somme de la table agrégée :", agrege["commandes"].sum())
```
<!--sortie-->
```text
83905 -> 2830 lignes | CA identique : True
commandes distinctes : 36395 | somme de la table agrégée : 70758
```

La table agrégée est **trente fois plus petite** (2 830 lignes au lieu de 83 905), et le chiffre d'affaires est identique. Mais la **somme des commandes** y est de 70 758 au lieu de 36 395 : on a retrouvé le piège de la règle 2. **On n'agrège que des mesures additives**, et les mesures non additives restent calculées sur la table fine. Un bon outil sait choisir la table agrégée quand la question le permet et la table fine sinon ; vous devez vérifier qu'il ne fait pas d'erreur.

**Qui est responsable ?** Un tableau de bord publié a un **propriétaire** (le nom de la personne à contacter), une **version** et une **documentation** (le dictionnaire des indicateurs, 2.3.5). Sans cela, personne ne le corrige, et il continue d'afficher un chiffre faux pendant des mois.

> ✅ **À retenir.**
> - Un outil de tableaux de bord enchaîne **connexion, préparation, modèle, mesures, visuels, publication, actualisation** ; chaque étape se reproduit à la main et se **vérifie**.
> - Le **modèle en étoile** (une table de faits, des dimensions à clé unique) est la base ; on contrôle les effectifs et les lignes orphelines ; on relie par des **identifiants**, jamais par des libellés.
> - Une **mesure** est une recette recalculée dans chaque contexte de filtres ; un **ratio** est une somme sur une somme ; une mesure comme le nombre de commandes **ne s'additionne pas**.
> - On définit les mesures **une fois**, dans le modèle ; on **planifie** l'actualisation, on **affiche la date des données**, on partage par **groupes** et on ne publie jamais sur le web des données internes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 et 2.2, exercices 2.1 à 2.3.


## 2.2 Tableau : feuilles, tableaux de bord, partage

Tableau est un outil de visualisation né de l'**exploration** : on glisse des champs sur une feuille, le graphique se dessine, on le modifie, on en essaie un autre. L'approche est symétrique de celle de la section 2.1 : au lieu de **construire le modèle puis dessiner**, on **dessine pour comprendre**, et le modèle suit. Cette section présente les idées de Tableau (les **marques** et leurs canaux, les **calculs de table**, les **niveaux de détail**, les tableaux de bord et leur partage), avec le même réflexe qu'avant : reproduire chaque résultat en pandas pour le vérifier.

> 🧭 **Même précaution.** Tableau est un produit commercial **non exécuté** ici : nous décrivons ses **notions**, pas ses menus, qui changent d'une version à l'autre et sont à vérifier dans la documentation de la vôtre. Les figures sont des maquettes calculées ou dessinées avec matplotlib, jamais des captures.

### 2.2.1 Feuilles, marques et canaux visuels

Une **feuille** est un graphique. Elle se construit en déposant des **champs** sur des **étagères**. Deux familles de champs existent :

- les **dimensions**, qui **découpent** (catégorie, canal, mois, région) ;
- les **mesures**, qui **comptent** (chiffre d'affaires, quantité, marge).

Les champs déposés sur les étagères *Colonnes* et *Lignes* fixent la **structure** de la feuille ; ceux déposés sur la carte des **marques** fixent l'**apparence** de chaque mark (un point, une barre, une ligne, un carré). Les canaux de la carte des marques sont ceux que vous connaissez : la **position**, la **couleur**, la **taille**, une **étiquette**, le **détail** (qui multiplie les marques sans les colorier) et l'**infobulle**. C'est exactement la grammaire des graphiques du chapitre 1 (section 1.1) : on **encode** une variable de la table par un canal visuel, et l'on choisit le canal selon la précision avec laquelle l'œil le lit (la position est lue le plus précisément, la taille et la couleur beaucoup moins).

| Champ déposé… | …sur | Effet dans la feuille |
|---|---|---|
| `categorie` (dimension) | Lignes | une ligne de marques par catégorie |
| `canal` (dimension) | Colonnes | une colonne de marques par canal |
| `montant` (mesure, somme) | Couleur | l'intensité de chaque case dépend du chiffre d'affaires |
| `montant` (mesure, somme) | Taille | l'aire de chaque cercle dépend du chiffre d'affaires |
| `id_commande` (dimension) | Détail | une marque par commande, sans couleur supplémentaire |

La « feuille » de la première ligne de ce tableau est, en pandas, un **tableau croisé** : une dimension en lignes, une en colonnes, une mesure agrégée dans les cases.

```python
feuille = v25.pivot_table(index="categorie", columns="canal", values="montant", aggfunc="sum")
print((feuille / 1000).round(0).to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux   Site
categorie                           
Bien-être       49.0     14.0   55.0
Cuisine         99.0     25.0  110.0
Décoration     112.0     28.0  119.0
Jardin         149.0     39.0  166.0
Maison         129.0     35.0  141.0
Papeterie       24.0      6.0   27.0
```

La même feuille, projetée sur trois canaux visuels différents, donne trois lectures.

![Une même feuille (chiffre d'affaires 2025 par catégorie et par canal) encodée de trois façons : la position, la couleur et la taille. Maquette dessinée avec matplotlib, pas une capture de Tableau.](figures/ch02-marques.png)


La position (barres) permet de **comparer précisément** ; la couleur (carte de chaleur) montre le **motif d'ensemble** mais ne se lit pas au chiffre près, d'où les valeurs écrites dans les cases ; la taille (cercles proportionnels) est la plus approximative. L'exercice de l'analyste est de choisir **le canal qui correspond à la question**, pas celui que l'outil propose par défaut. Ici, la question de la gérante (« qu'est-ce qui vend le plus ? ») est une question de comparaison : on prend la position, on trie, et l'on garde la couleur pour une seule chose (par exemple, mettre en valeur la catégorie qui pose problème).

> 💡 **Intuition.** Dans un outil comme Tableau, **construire une feuille revient à répondre à trois questions** : qu'est-ce que je découpe (dimensions), qu'est-ce que je compte (mesures), et par quel canal visuel je montre chaque variable. Le glisser-déposer ne dispense pas de les poser.

Les champs d'une feuille ont aussi un **type de granularité** : une dimension « discrète » donne des catégories séparées (un en-tête par valeur) ; une dimension « continue » (une date, un nombre) donne un axe continu. Une date peut s'utiliser de **deux façons** : discrète (« chaque mois, tous les ans confondus ») ou continue (une ligne du temps). Choisir la mauvaise donne soit une courbe sans sens, soit un axe sans repères ; vérifiez toujours quelle est la granularité attendue.

### 2.2.2 Calculs de table et niveaux de détail

Les champs de base ne suffisent pas : on veut des parts, des cumuls, des moyennes mobiles, des rangs. Tableau offre deux mécanismes, que l'on confond souvent parce qu'ils donnent des résultats d'apparence voisine, alors que **leur logique est différente**.

#### Les calculs de table : sur le résultat affiché

Un **calcul de table** s'applique **à ce qui est déjà affiché**, au tableau agrégé que la feuille vient de calculer : « part du total », « cumul », « moyenne mobile », « rang », « différence avec la ligne précédente ». Il dépend donc de la **structure** de la feuille : si l'on change les dimensions, il se recalcule autrement. Voici les quatre calculs sur les catégories de la boutique.

```python
t = v25.groupby("categorie")["montant"].sum().sort_values(ascending=False).to_frame("ca")
t["pct_total"] = t["ca"] / t["ca"].sum() * 100
t["cumul_pct"] = t["pct_total"].cumsum()
t["rang"] = t["ca"].rank(ascending=False).astype(int)
print(t.round(1).to_string())
```
<!--sortie-->
```text
                  ca  pct_total  cumul_pct  rang
categorie                                       
Jardin      353954.6       26.7       26.7     1
Maison      304614.0       23.0       49.7     2
Décoration  258742.3       19.5       69.2     3
Cuisine     233312.6       17.6       86.9     4
Bien-être   117510.8        8.9       95.7     5
Papeterie    56629.3        4.3      100.0     6
```

On lit tout de suite que **Jardin pèse 26,7 %** du chiffre d'affaires 2025, que **les trois premières catégories en font 69,2 %**, et que Papeterie, avec 4,3 %, ferme la marche. Chaque colonne est un calcul de table différent ; remarquez que le **cumul** n'a de sens que si l'ordre est celui du tri (sinon, il additionne dans un ordre arbitraire), et que le **rang** dépend du sens du tri choisi. Ce sont ces dépendances qu'il faut vérifier quand on pose un calcul de table : *sur quelle dimension se calcule-t-il, dans quel ordre ?*

La **moyenne mobile** est le calcul de table le plus utile pour une courbe hebdomadaire bruitée : la moyenne des quatre dernières semaines.

```python
mm4 = hebdo["ca"].rolling(4).mean()
print(f"dernière semaine : {hebdo['ca'].iloc[-1]:,.0f} €  | moyenne mobile sur 4 semaines : {mm4.iloc[-1]:,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
dernière semaine : 44 168 €  | moyenne mobile sur 4 semaines : 43 018 €
```

La semaine du 22 décembre a rapporté 44 168 €, mais la moyenne des quatre dernières semaines est de 43 018 € : la moyenne mobile **lisse** le bruit, au prix d'un **retard** (elle met quelques semaines à réagir à un changement). Montrer les **deux** courbes est souvent la bonne réponse.

#### Les niveaux de détail : à une granularité choisie

Une expression de **niveau de détail** (en anglais *level of detail*, LOD) calcule une valeur **à une granularité que vous choisissez**, **indépendamment de la structure de la feuille**. Trois variantes existent : **FIXED** (on fixe la granularité : « le total par client »), **INCLUDE** (on ajoute une dimension à la feuille pour le calcul) et **EXCLUDE** (on en retire une). Le cas d'usage type est le **calcul en deux temps** : agréger à un niveau fin, puis agréger de nouveau à un niveau plus grossier.

Un exemple. « Quel est le chiffre d'affaires moyen par client ? » est une question à deux temps : on calcule d'abord le **total de chaque client**, puis on **moyenne ces totaux**. Moyenner directement les lignes de commande répondrait à une autre question (le montant moyen d'une ligne).

```python
ca_client = v25.groupby("id_client")["montant"].sum()
print(len(ca_client), "clients actifs en 2025 | moyenne", round(ca_client.mean(), 2), "€ | médiane", round(ca_client.median(), 2), "€")
print("montant moyen d'une ligne :", round(v25["montant"].mean(), 2), "€")
```
<!--sortie-->
```text
3875 clients actifs en 2025 | moyenne 341.87 € | médiane 233.21 €
montant moyen d'une ligne : 44.41 €
```

Les **3 875 clients actifs** ont dépensé en moyenne **342 €** en 2025, la médiane est de **233 €** (quelques gros clients tirent la moyenne vers le haut, comme au volume III, section 1.1) ; une ligne de commande, elle, vaut en moyenne 44 €. Le **panier moyen** de 102 € est encore autre chose : le total d'une **commande**. **Trois « moyennes » légitimes, trois granularités**, et la boutique en a besoin des trois. C'est exactement ce que les niveaux de détail permettent de nommer proprement dans l'outil.

> 💡 **Intuition.** Un calcul de table répond à « **que dit le tableau que j'ai sous les yeux ?** » (part, cumul, rang) ; un niveau de détail répond à « **que dit la table au niveau X, quoi que j'affiche ?** ». Quand un chiffre change parce que l'on a retiré une colonne de la feuille, c'est un calcul de table ; quand il ne bouge pas, c'est un niveau de détail.

Un point de méthode, enfin : les filtres n'agissent pas tous **au même moment**. Tableau applique ses opérations dans un **ordre fixe** (la documentation le résume sous le nom d'*ordre des opérations*) : par exemple, les filtres de dimension d'une feuille s'appliquent **après** un niveau de détail FIXED, ce qui peut surprendre (un filtre sur la catégorie ne change pas le « total par client » calculé en FIXED, à moins d'être défini comme filtre de contexte). L'équivalent pandas est de se demander si l'on **filtre avant ou après** le `groupby` :

```python
tous = v25.groupby("id_client")["montant"].sum()
jardin = v25[v25["categorie"] == "Jardin"].groupby("id_client")["montant"].sum()
print(len(jardin), "clients du Jardin")
print("dépense dans le Jardin :", round(jardin.mean(), 2), "€ | dépense totale :", round(tous[jardin.index].mean(), 2), "€")
```
<!--sortie-->
```text
2402 clients du Jardin
dépense dans le Jardin : 147.36 € | dépense totale : 457.93 €
```

Selon que l'on filtre la catégorie **avant** ou **après** le premier regroupement, on ne répond pas à la même question : « combien dépense un client du Jardin **en tout** ? » ou « combien dépense-t-il **dans** la catégorie Jardin ? ». Les 2 402 clients qui ont acheté dans le Jardin ont dépensé **457,93 €** en moyenne sur l'ensemble de la boutique en 2025, mais **147,36 €** dans la seule catégorie Jardin : un facteur trois. Le premier chiffre est celui d'une expression FIXED (le total du client, quoi que la feuille filtre) ; le second, celui d'un calcul sur la feuille filtrée. **Les deux sont justes, mais l'un d'eux seulement est celui que l'on attendait** ; vérifiez dans l'outil lequel s'affiche.

> ⚠️ **Piège.** Un calcul de table ou un niveau de détail qui **donne un résultat plausible** n'est pas forcément le résultat voulu. Après chaque calcul, posez-vous trois questions : sur quelle granularité ? avec quels filtres ? dans quel ordre ? Et reproduisez le chiffre d'une case en pandas.

### 2.2.3 Du classeur au tableau de bord

Les feuilles sont des briques ; le **tableau de bord** les assemble sur une page. Les outils de la famille de Tableau l'organisent avec des **conteneurs** (horizontaux ou verticaux) qui répartissent l'espace, et offrent le choix entre une **taille fixe** (la page a les dimensions voulues, elle est identique sur tous les écrans, avec des barres de défilement si l'écran est trop petit) et une taille **adaptée** (elle s'étire, mais la disposition peut s'abîmer). Pour un tableau de bord lu **sur un écran de bureau**, la taille fixe et un ordre de lecture soigné (section 2.3.4) donnent les résultats les plus prévisibles ; pour un affichage **sur téléphone**, on prépare une **mise en page dédiée**, plus étroite et plus simple, plutôt que de réduire la version de bureau.

Ce qui distingue un tableau de bord d'un ensemble de graphiques, ce sont les **actions** : cliquer sur une barre pour **filtrer** les autres feuilles, **surligner** les points apparentés, ouvrir une page de détail ou un document externe, changer un **paramètre** (par exemple, le seuil de l'alerte). Chaque action est un petit contrat avec le lecteur : « si vous cliquez ici, il se passe ceci ». Il faut le **dire** (une phrase d'instruction, un curseur visible, un bouton « effacer les filtres ») ; une interaction cachée n'existe pas pour la plupart des lecteurs.

La **connexion** aux données reprend le choix de la section 2.1.1 : une connexion **directe** interroge la source à chaque action ; un **extrait** (*extract*) est une copie compressée, plus rapide, actualisée à des heures fixes. Pour un tableau de bord hebdomadaire, l'extrait est le choix raisonnable.

Le **partage** se fait selon trois grandes formules. Un **serveur** ou un **service en ligne** de l'éditeur, avec des comptes, des groupes et des droits : c'est la voie normale en entreprise. Une **publication publique** (il existe une offre gratuite qui publie sur un site ouvert à tous) : **tout y est public**, données comprises, et l'on n'y met jamais de données de la boutique. Enfin, le **fichier** exporté (image, PDF, classeur) : pratique pour une réunion, mais figé, sans actualisation, et facile à transmettre hors de tout contrôle. On vérifie dans la documentation de sa version ce que chaque formule permet exactement, et à quelles conditions de licence.

Les **histoires** (*stories*) enchaînent plusieurs feuilles ou tableaux de bord en une séquence commentée : c'est un outil de présentation, étudié au chapitre 4 (section 4.3).

### 2.2.4 Deux philosophies, un même chemin

Les approches de Power BI et de Tableau diffèrent par leur **point de départ**, et se rejoignent très vite. L'analyste qui connaît l'une apprend l'autre en quelques semaines **à condition d'avoir compris les notions de fond**.

| Notion | Approche « modèle d'abord » (Power BI, 2.1) | Approche « exploration d'abord » (Tableau, 2.2) |
|---|---|---|
| Point de départ | le modèle de données, relié en étoile | une feuille, puis les liens entre les sources |
| Calcul réutilisable | **mesure** écrite dans le modèle | **champ calculé**, calcul de table ou niveau de détail |
| Granularité | contexte de filtres de chaque visuel | dimensions de la feuille, niveaux de détail |
| Force | cohérence de définitions entre rapports | rapidité d'exploration, souplesse visuelle |
| Risque | modèle lourd à faire évoluer | calculs dispersés dans chaque classeur |

Cette comparaison est volontairement **schématique** : les deux produits ont tellement évolué que chacun a emprunté à l'autre. Retenez-en l'essentiel : **dans les deux cas, le travail difficile est le même** : un modèle de données juste, des définitions claires, des chiffres vérifiés. Le reste (choix de couleur, disposition, interaction) relève de la conception, que nous abordons en 2.3.

> ✅ **À retenir.**
> - Une **feuille** encode des champs par des **canaux** (position, couleur, taille, détail) ; on choisit le canal selon la **question** et selon la précision de lecture.
> - Un **calcul de table** opère sur le **tableau affiché** (part, cumul, moyenne mobile, rang) et dépend de la structure de la feuille ; un **niveau de détail** opère à une **granularité choisie**, indépendamment d'elle.
> - Un chiffre plausible n'est pas forcément **le chiffre voulu** : on se demande sur quelle granularité, avec quels filtres, dans quel ordre, et on **recalcule en pandas** une case de la feuille.
> - Un tableau de bord assemble des feuilles avec des **actions** qu'il faut **annoncer** ; on partage par groupes, et une publication **publique** ne convient jamais aux données internes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3, exercices 2.4 et 2.5.


## 2.3 Conception d'un tableau de bord selon les besoins des utilisateurs

Les sections précédentes ont montré **comment** un outil fabrique un tableau de bord. Celle-ci répond à la question qui décide de sa réussite : **pour qui et pour quoi** ? Un tableau de bord conçu à partir des données disponibles (« montrons tout ce que nous avons ») est presque toujours abandonné ; un tableau de bord conçu à partir des **décisions** de la personne qui le lit devient un rituel du lundi matin. Nous suivons la méthode de bout en bout et construisons la page de la gérante, dont tous les chiffres sont recalculés ici.

### 2.3.1 Partir de la décision, pas des données

La première erreur est de commencer par la donnée : « nous avons des ventes, des stocks, des livraisons, faisons un graphique de chaque ». La méthode inverse tient en une chaîne de questions, que l'on pose **à la gérante avant d'ouvrir l'outil** :

1. Quelles **décisions** prenez-vous régulièrement ? (commander, relancer un transporteur, lancer ou arrêter une promotion…)
2. Quelle **question** chacune de ces décisions pose-t-elle ? (« Allons-nous manquer de produits ? »)
3. Quel **indicateur** y répond, avec quelle définition, et par rapport à quelle référence ?
4. À partir de quelle valeur **agit-on** ?
5. À quelle **fréquence** regarde-t-on, et sur quel écran ?

Pour la boutique, l'entretien d'une demi-heure avec la gérante donne le tableau suivant.

| Décision | Question | Indicateur | On agit si… |
|---|---|---|---|
| Relancer le transporteur | Les clients reçoivent-ils à temps ? | Livraisons à l'heure (%) | sous la **limite basse** de l'habituel |
| Commander du stock | Allons-nous manquer de produits ? | Rupture sur les 20 produits suivis (%) | au-dessus de la **limite haute** de l'habituel |
| Ajuster l'effort commercial | Les ventes suivent-elles ? | Chiffre d'affaires, commandes | durablement sous l'an dernier |
| Corriger l'offre ou les prix | Gagnons-nous toujours de l'argent ? | Taux de marge brute, panier moyen | en recul marqué |
| Travailler le site | Le site convertit-il ? | Taux de conversion | hors de la fourchette habituelle |

Remarquez ce que le tableau ne contient pas : aucun indicateur « parce qu'on peut le calculer ». Chaque ligne est **reliée à une décision**, ce qui est la règle du volume III (section 6.1.1) ; chaque indicateur a une définition écrite (6.1.2) et, pour les deux alertes, un seuil fondé sur la variabilité observée (6.3.5). Ce que l'on ajoute ici, c'est un **écran** : les alertes ne sont utiles que si la gérante les voit au moment où elle décide.

![Le processus de conception d'un tableau de bord : interroger, croquer, prototyper, tester en cinq secondes, publier, mesurer l'usage ; on revient en arrière tant que l'utilisateur ne comprend pas. Maquette dessinée.](figures/ch02-processus.png)


Le processus est **itératif** : on interroge, on **croque** la page sur papier (cinq minutes, aucun outil), on construit un **prototype** avec des données réelles, on le fait **tester** (on montre la page cinq secondes à quelqu'un qui ne la connaît pas, puis on lui demande ce qu'il en a retenu), on publie, puis on **mesure l'usage** et l'on corrige. Le test de cinq secondes est volontairement cruel : si la personne ne dit pas « les livraisons ne vont pas bien », la page n'a pas rempli son rôle, quel que soit son aspect.

> 💡 **Intuition.** Pour savoir ce qu'un tableau de bord doit contenir, demandez à son lecteur **ce qu'il fera lundi matin** selon ce qu'il verra. Un chiffre qui ne change aucune décision est du décor.

### 2.3.2 Trois niveaux : vue d'ensemble, analyse, détail

Un utilisateur n'a pas toujours le même besoin : tantôt **savoir si tout va bien**, tantôt **comprendre pourquoi** quelque chose ne va pas, tantôt **retrouver une ligne précise**. Un tableau de bord qui tente de tout faire sur une page est illisible ; la structure classique répartit ces trois besoins sur **trois niveaux**, reliés par des liens de navigation.

![Les trois niveaux d'un tableau de bord : une vue d'ensemble (quelques chiffres et alertes), des pages d'analyse (comparer, ventiler, filtrer), un niveau de détail (tableau de lignes). Chaque niveau répond à une question plus fine que le précédent. Maquette dessinée.](figures/ch02-niveaux.png)


- **Niveau 1, la vue d'ensemble** : cinq à huit chiffres, une courbe, une zone d'alertes. Elle se lit en **cinq secondes** et ne demande aucun clic. C'est la page de la gérante.
- **Niveau 2, l'analyse** : des pages par thème (ventes, livraisons, stock), avec des filtres (période, canal, catégorie) et des comparaisons. Elle répond à « **où** et **pourquoi** ? ». Les arbres d'indicateurs du volume III (section 6.2) en sont le plan : si le chiffre d'affaires baisse, on descend vers le trafic, la conversion ou le panier.
- **Niveau 3, le détail** : le **tableau de lignes** (les commandes en retard, les produits en rupture), exportable. Il répond à « **lesquelles** ? » et sert à agir (appeler le transporteur au sujet de ces douze colis).

La règle de navigation est de **descendre en cliquant** (de la carte vers l'analyse, de l'analyse vers le détail) et de pouvoir **remonter** en un clic. Chaque page porte un titre qui dit **ce qu'elle montre** et la date des données ; les filtres actifs sont écrits en toutes lettres, pour qu'un lecteur ne prenne pas un chiffre filtré pour un chiffre global (voir 2.1.4).

### 2.3.3 La page de la gérante

Construisons maintenant la page du niveau 1. Elle présente six chiffres, un graphique de tendance, une répartition par canal, une courbe de contrôle et une zone d'alertes. D'abord les chiffres : la semaine du 22 au 28 décembre 2025, comparée à la **même semaine un an plus tôt** (364 jours avant, pour comparer un lundi à un lundi).

```python
k, _ = O.kpi_semaine(d, "2025-12-22")
cs, ad = k["cette_semaine"], k["an_dernier"]
print(f"CA {cs['ca'] / 1000:.1f} k€ ({cs['ca'] / ad['ca'] - 1:+.1%}) | commandes {cs['commandes']:.0f} ({cs['commandes'] / ad['commandes'] - 1:+.1%})")
print(f"panier {cs['panier']:.1f} € ({cs['panier'] / ad['panier'] - 1:+.1%}) | marge {cs['taux_marge']:.1%} ({(cs['taux_marge'] - ad['taux_marge']) * 100:+.1f} pts)")
```
<!--sortie-->
```text
CA 44.2 k€ (+34.9%) | commandes 441 (+19.2%)
panier 100.2 € (+13.2%) | marge 39.4% (+2.2 pts)
```

Sur ces quatre chiffres, la semaine est **excellente** : 44,2 k€ de chiffre d'affaires (+34,9 % sur l'an dernier), 441 commandes (+19,2 %), un panier moyen de 100,2 € (+13,2 %) et un taux de marge brute de 39,4 % (+2,2 points). C'est la **deuxième meilleure semaine de 2025**. Mais la gérante a demandé qu'on lui dise **quand quelque chose ne va pas**, et deux indicateurs ne vont pas bien du tout. Les alertes utilisent la règle de 6.3.5 : on compare la semaine à la **moyenne des 26 semaines précédentes**, avec une **limite à trois écarts-types**.

```python
t0 = pd.Timestamp("2025-12-22")
moy, bas, _ = O.limites(hebdo["a_l_heure"], t0)
moy_r, _, haut_r = O.limites(hebdo["rupture"], t0)
print(f"livraisons à l'heure : {cs['a_l_heure']:.1%} | habituel {moy:.1%} | limite basse {bas:.1%}")
print(f"rupture : {cs['rupture']:.1%} | habituel {moy_r:.1%} | limite haute {haut_r:.1%}")
```
<!--sortie-->
```text
livraisons à l'heure : 44.5% | habituel 76.3% | limite basse 48.5%
rupture : 35.0% | habituel 8.4% | limite haute 28.3%
```

Les **livraisons à l'heure** sont à **44,5 %** alors que l'habituel est de **76,3 %** (la limite basse est à 48,5 %) : la semaine est **sous la limite**. La **rupture** touche **35,0 %** des produits suivis, contre 8,4 % d'habitude (limite haute : 28,3 %) : elle est **au-dessus de la limite**. Les deux alertes se confirment l'une l'autre, ce qui est cohérent avec l'histoire du volume III : en décembre, la demande monte, les stocks se vident, et le transporteur le plus lent s'engorge.

Un détail vaut d'être souligné. Le taux de livraisons à l'heure de **la même semaine, il y a un an**, était de 40,2 % : l'indicateur est donc **en hausse de 4,3 points** sur l'an dernier, alors qu'il est **à 32 points de son niveau habituel**. Si la page ne montrait que la comparaison à l'an dernier, elle afficherait un petit +4,3 en vert : **la bonne référence n'est pas toujours l'an dernier**. Pour des livraisons, c'est le niveau **habituel** ; pour des ventes saisonnières, c'est la même période de l'an dernier. La page affiche donc, pour chaque carte, **la référence qui convient à sa décision**, et l'écrit.


![La page d'une semaine pour la gérante : six chiffres avec leur référence, la tendance du chiffre d'affaires contre l'an dernier, la répartition par canal, la courbe de contrôle des livraisons et la zone d'alertes. Données simulées ; maquette calculée avec matplotlib, pas une capture d'un outil de tableaux de bord.](figures/ch02-tableau-de-bord.png)

La page respecte les quatre règles du chapitre 1 : **un message par graphique** (le titre dit ce que l'on regarde), **une seule couleur d'alerte** (le rouge ne sert qu'aux deux alertes), **la même couleur pour la même chose** (le gris est toujours « l'an dernier », le bleu toujours « cette année ») et **les références visibles** (« habituel : 76 % », « vs an dernier »). Les chiffres des cartes viennent des fonctions de ce chapitre, et ceux du graphique de tendance sont les mêmes que ceux de la section 2.1 : c'est le **même modèle** qui les alimente.

### 2.3.4 Disposition et lecture : le test de cinq secondes

Un lecteur ne **lit** pas une page : il la **balaie**. Pour une page en langue française, le regard part du coin supérieur gauche, parcourt la première ligne, redescend en diagonale vers la gauche, puis balaie la ligne suivante : c'est le **parcours en Z**. On y place donc, dans l'ordre, ce qui compte le plus : le titre et le contexte, les **chiffres clés**, la **tendance**, puis le **détail** ou les alertes.

![Le parcours de lecture en « Z » : titre et contexte en haut à gauche, chiffres clés sur la première ligne, tendance et répartition au milieu, alertes et notes en bas. Maquette dessinée.](figures/ch02-disposition.png)


La **densité** compte autant que l'ordre. Les maquettes suivantes présentent le **même contenu** : à gauche, quatorze éléments et neuf couleurs ; à droite, six chiffres, trois graphiques et une seule couleur d'alerte.

![Le même contenu, noyé puis ordonné : à gauche un tableau de bord qui montre tout, à droite le même rangé selon l'importance. Maquettes dessinées pour comparer la lecture.](figures/ch02-noye-ordonne.png)


Une règle pratique : **entre cinq et huit chiffres** sur la page principale, et pas plus de trois graphiques. Au-delà, on a un document, pas un tableau de bord. Si la gérante a besoin de plus, c'est qu'il faut une deuxième page (niveau 2), pas une page plus chargée.

#### La liste de contrôle, appliquée à notre propre page

Une liste de contrôle est un outil de relecture, pas une récitation. Passons notre page au crible, avec cinq questions.

1. **Le test de cinq secondes.** Que lit-on en cinq secondes ? Les chiffres en gros, puis la zone rouge « À regarder cette semaine ». C'est le but.
2. **Chaque chiffre a-t-il sa référence ?** Oui, sauf la conversion du site : aucune comparaison à l'an dernier, car les sessions n'existent que pour 2025 (volume III, section 6.1.4). La page le **dit** (« pas d'historique avant 2025 ») au lieu de laisser un blanc.
3. **Les couleurs portent-elles seules le message ?** Non : le sens de chaque variation est écrit (« +34,9 % », « habituel : 76 % »), le rouge n'est jamais la seule information. Un lecteur daltonien comprend la même chose.
4. **Les textes sont-ils lisibles ?** C'est le point le plus faible. Le contraste d'un texte se mesure : le rapport entre la luminance du texte et celle du fond doit atteindre **4,5 : 1** pour du petit texte (3 : 1 pour du grand texte ou des éléments graphiques), selon les recommandations d'accessibilité usuelles. Calculons-le pour les couleurs de la page sur fond blanc.

```python
def contraste(a, b="#ffffff"):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)
for nom, c in {"bleu": "#2a78d6", "rouge": "#e34948", "gris moyen": "#898781", "gris texte": "#52514e"}.items():
    print(f"{nom:<11} {contraste(c):.2f} : 1")
```
<!--sortie-->
```text
bleu        4.42 : 1
rouge       3.95 : 1
gris moyen  3.59 : 1
gris texte  7.94 : 1
```

Le **bleu** (4,42 : 1) sert à des lignes et des barres : c'est suffisant pour des éléments graphiques (3 : 1). Le **gris texte** (7,94 : 1) convient à tous les textes. Mais le **rouge** des petits textes d'alerte (3,95 : 1) et le **gris moyen** des axes (3,59 : 1) sont **sous le seuil de 4,5 : 1** pour du petit texte. Dans notre maquette, on les corrigerait en production en **fonçant** le rouge des textes (en gardant le rouge actuel pour les aplats et les traits) et en écrivant les axes en gris texte. Un contrôle de cette sorte prend une minute et évite que la page soit illisible sur un écran de salle de réunion.

5. **Le tableau de bord résiste-t-il à la semaine suivante ?** C'est-à-dire : la page se **recalcule-t-elle seule**, avec une date paramétrée, et reste-t-elle lisible quand les chiffres changent (une valeur à sept chiffres, une cible à zéro, une semaine sans donnée) ? C'est la question de l'automatisation, que traite le chapitre 4 (section 4.4).

> ⚠️ **Pièges de lecture à repérer.** Les cartes vertes ou rouges **sans** texte ; un axe qui ne part pas de zéro pour des barres ; des couleurs qui changent de sens d'un graphique à l'autre ; une période de comparaison non précisée ; un filtre actif qu'on ne voit pas. Chaque défaut figure dans la liste du chapitre 1 (section 1.4) : on les cherche **sur sa propre page**.

### 2.3.5 Valider, documenter, faire adopter

Une page jolie et fausse est plus dangereuse qu'une page laide et juste. Trois gestes protègent la gérante.

**La recette : le même chiffre par deux chemins.** Avant la mise en service, on recalcule les chiffres clés **indépendamment de l'outil** et on compare. Pour la boutique, deux contrôles suffisent : le total d'une année calculé en SQL et en pandas, et la semaine de la page recalculée directement sur la table de faits.

```python
import sqlite3
con = sqlite3.connect(":memory:")
faits.to_sql("fait_ventes", con, index=False)
sql = "SELECT ROUND(SUM(montant), 2) FROM fait_ventes WHERE date >= '2025-01-01'"
print("CA 2025 : SQL", con.execute(sql).fetchone()[0], "| pandas", round(v25["montant"].sum(), 2))
sem = faits[(faits["date"] >= "2025-12-22") & (faits["date"] <= "2025-12-28")]
print("semaine du 22/12 : table de faits", round(sem["montant"].sum(), 2), "| page", round(hebdo.loc["2025-12-22", "ca"], 2))
```
<!--sortie-->
```text
CA 2025 : SQL 1324763.72 | pandas 1324763.72
semaine du 22/12 : table de faits 44167.99 | page 44167.99
```

Les deux calculs du chiffre d'affaires 2025 donnent **1 324 763,72 €** (SQL et pandas) et la semaine du 22 décembre **44 167,99 €** de deux manières : la page affiche bien ce que la table contient. On ajoute le **rapprochement avec une source indépendante** quand il en existe une (la comptabilité, les relevés de caisse), et l'on **explique** l'écart jusqu'au centime, comme au volume II (section 3.3).

> 🧭 **En pratique.** Gardez un petit **classeur de recette** : une page par indicateur, avec la valeur affichée par le tableau de bord, la valeur recalculée à part, l'écart, la date et la personne qui a vérifié. Il sert à **chaque** modification du modèle ou d'une mesure.

**Le dictionnaire des indicateurs.** Chaque chiffre de la page a une fiche : nom, définition en une phrase, formule, source, fréquence d'actualisation, propriétaire (désigné par sa **fonction**). Voici celle de la page de la gérante.

| Indicateur | Définition | Source | Actualisation |
|---|---|---|---|
| Chiffre d'affaires | somme des montants TTC des lignes de commande de la semaine (lundi à dimanche) | table de faits | chaque nuit |
| Commandes | nombre de commandes **distinctes** de la semaine | table de faits | chaque nuit |
| Panier moyen | chiffre d'affaires ÷ commandes | mesure | chaque nuit |
| Taux de marge brute (HT) | marge hors taxes ÷ chiffre d'affaires hors taxes (TVA 20 % pour l'illustration) | mesure | chaque nuit |
| Livraisons à l'heure | part des colis **livrés** dans la semaine qui n'ont pas de retard | livraisons | chaque nuit |
| Rupture | part des jours-produits en rupture, sur 20 produits suivis | stock quotidien | chaque nuit |
| Conversion du site | part des sessions du site qui donnent une commande | sessions web | chaque nuit |

Les définitions importantes se discutent **avant** : « livraisons à l'heure » est calculé sur les colis **livrés** cette semaine (on ne connaît le retard d'un colis qu'à sa livraison) ; une autre définition (colis **commandés** cette semaine) donnerait un autre chiffre, et le dictionnaire dit laquelle est la bonne.

**L'adoption.** Un tableau de bord s'impose par l'usage, pas par la décision de le déployer. Quatre habitudes y aident : un **rendez-vous** (cinq minutes le lundi, avec la page à l'écran), un **propriétaire** nommé qui répond aux questions, une **mesure de l'usage** (les outils disent qui ouvre quoi : un visuel que personne ne regarde se retire) et un **journal des changements** (« la définition des livraisons à l'heure a changé le… »). Cinq raisons font mourir un tableau de bord : trop de chiffres, des chiffres qui contredisent ceux d'un autre document, des données qui ne sont plus à jour, aucune action qui en découle, et une page lente.

> ✅ **À retenir.**
> - On part des **décisions** de l'utilisateur : décision, question, indicateur, seuil d'action, fréquence. Un chiffre qui ne change aucune décision est du décor.
> - **Trois niveaux** : vue d'ensemble (cinq à huit chiffres, lisible en cinq secondes), analyse (où, pourquoi), détail (lesquels). On **descend en cliquant** et on peut remonter.
> - Chaque chiffre porte la **référence qui convient à sa décision** (l'habituel pour les livraisons, l'an dernier pour les ventes) ; les alertes viennent de **limites fondées sur la variabilité**.
> - Le test de cinq secondes, le parcours en Z et la liste de contrôle (références, couleurs, contraste, lisibilité) s'appliquent **à sa propre page** ; le contraste se **calcule**.
> - On **valide** par deux chemins indépendants, on **documente** dans un dictionnaire, on **suit l'usage** et l'on tient un journal des changements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5, exercices 2.6 à 2.9.


## 2.4 ➕ Pour aller plus loin : Power BI avancé, DAX, Power Query, sécurité par lignes, déploiement

> 🧭 **Section optionnelle.** Elle s'adresse à celles et ceux qui construiront des modèles de données pour d'autres personnes. Elle suppose les notions de 2.1 (étoile, mesures, contexte de filtres). Comme avant, **Power BI n'est pas exécuté** : le code DAX et M qui apparaît dans cette section est donné **à titre indicatif**, dans des blocs marqués « non exécuté » ; **ce qui est vérifié, c'est l'équivalent pandas**, dont les chiffres sont recalculés ici. La syntaxe exacte et les fonctions disponibles sont à vérifier dans la documentation de votre version.

Quatre savoirs distinguent un tableau de bord de démonstration d'un modèle de production : le langage des mesures (**DAX**), la préparation des données (**Power Query**), la **sécurité par lignes** et le **déploiement**. Chacun a un équivalent que vous connaissez déjà, ce qui donne une méthode : on écrit l'équivalent pandas, on **le fait parler**, puis on compare au chiffre de l'outil.

### 2.4.1 DAX : le langage des mesures

DAX est le langage des mesures de Power BI. Il ressemble à une formule de tableur, mais il se comporte comme un **langage de requête sur un modèle** : toute expression s'évalue **dans un contexte de filtres**. Deux notions font l'essentiel.

Le **contexte de ligne** : « pour cette ligne de la table », utilisé dans une colonne calculée ou dans une fonction d'itération (`SUMX`). Le **contexte de filtres** : « sur ces lignes-là », construit par la page, les segments et les cellules du visuel. La fonction centrale, `CALCULATE`, **modifie** le contexte de filtres avant d'évaluer une expression : elle ajoute un filtre, en remplace un, ou en retire un (`ALL`).

Quelques mesures de la boutique, écrites en DAX :

```text
-- DAX : indicatif, non exécuté
CA              = SUM ( fait_ventes[montant] )
Marge HT        = SUMX ( fait_ventes,
                    fait_ventes[montant] / 1,2
                    - fait_ventes[quantite] * RELATED ( dim_produit[cout_achat] ) )
CA an dernier   = CALCULATE ( [CA], SAMEPERIODLASTYEAR ( dim_date[date] ) )
Évolution       = DIVIDE ( [CA] - [CA an dernier], [CA an dernier] )
CA cumul annuel = TOTALYTD ( [CA], dim_date[date] )
Part du canal   = DIVIDE ( [CA], CALCULATE ( [CA], ALL ( dim_canal ) ) )
```

Lisons-les. `Marge HT` itère sur chaque ligne de faits (contexte de ligne) et va chercher le coût d'achat du produit grâce à la relation (`RELATED`). `CA an dernier` demande à `CALCULATE` de **décaler le contexte de date d'un an** : c'est la fonction de comparaison dans le temps, qui **exige une dimension de dates continue** (section 2.1.2). `DIVIDE` est une division qui renvoie un résultat vide, au lieu d'une erreur, quand le dénominateur est nul. `Part du canal` enlève le filtre de canal au dénominateur (`ALL`) pour obtenir le total de référence.

Chacune a un équivalent en pandas, que nous exécutons pour vérifier les chiffres que l'outil devrait afficher. D'abord les comparaisons dans le temps.

```python
mois = O.ca_par_mois(d)
dec25, dec24 = mois.loc[12, 2025], mois.loc[12, 2024]
print(f"décembre : {dec25:,.0f} € contre {dec24:,.0f} € ({dec25 / dec24 - 1:+.1%})".replace(",", " "))
cumul = mois.cumsum()
c25, c24 = cumul.loc[9, 2025], cumul.loc[9, 2024]
print(f"cumul à fin septembre : {c25:,.0f} € contre {c24:,.0f} € ({c25 / c24 - 1:+.1%})".replace(",", " "))
print(f"... comparé à toute l'année 2024 : {c25 / cumul.loc[12, 2024] - 1:+.1%}")
```
<!--sortie-->
```text
décembre : 183 845 € contre 157 304 € (+16.9%)
cumul à fin septembre : 876 963 € contre 798 738 € (+9.8%)
... comparé à toute l'année 2024 : -26.3%
```

Décembre 2025 a rapporté 183 845 € contre 157 304 € en décembre 2024 (+16,9 %), et le cumul depuis janvier est de 876 963 € à fin septembre contre 798 738 € un an plus tôt (+9,8 %). La dernière ligne rappelle le **piège classique** : comparer neuf mois de 2025 aux **douze** mois de 2024 donne −26,3 %, un résultat absurde parce qu'on compare des périodes de longueurs différentes. La fonction « même période de l'an dernier » existe pour l'éviter : **on compare à période égale**.

![Les deux comparaisons dans le temps : le chiffre d'affaires mensuel de 2025 contre celui de 2024 (même période de l'an dernier), et le cumul depuis le début de l'année.](figures/ch02-dax-an-dernier.png)


Ensuite, le changement de contexte et le ratio protégé.

```python
ca_site = v25.loc[v25["canal"] == "Site", "montant"].sum()
jardin_25 = v25[v25["categorie"] == "Jardin"]
part_jardin = jardin_25.loc[jardin_25["canal"] == "Site", "montant"].sum() / jardin_25["montant"].sum()
print(f"part du Site : {ca_site / v25['montant'].sum():.1%} (toutes catégories) | {part_jardin:.1%} (dans Jardin)")
```
<!--sortie-->
```text
part du Site : 46.6% (toutes catégories) | 47.0% (dans Jardin)
```

La même mesure « part du canal » donne **46,6 %** pour toute la boutique et **47,0 %** dans le contexte « catégorie Jardin » : la recette ne change pas, le **contexte** si. C'est ce que `CALCULATE` et `ALL` contrôlent : `ALL(dim_canal)` retire le filtre de canal au dénominateur, mais **conserve** le filtre de catégorie, ce qui fait de la mesure une part **dans la catégorie**. Si l'on voulait la part dans **tout** le chiffre d'affaires, il faudrait retirer aussi le filtre de catégorie : **chaque `ALL` est une décision de définition**. Enfin, `DIVIDE` protège la division : en pandas, une division par zéro donne l'infini, que l'on remplace par une valeur manquante. L'important est de **décider** ce que la page affiche (un blanc, un zéro, un tiret) quand le dénominateur est nul.


> ⚠️ **Piège.** Les fonctions de comparaison dans le temps supposent une **table de dates marquée comme telle** et couvrant des **années entières** ; un trou (une année incomplète à la fin) ou une date en double suffit à produire un résultat faux sans message d'erreur. Contrôlez la dimension (effectif, unicité) comme en 2.1.2, et comparez toujours un résultat à son équivalent pandas.

### 2.4.2 Power Query : la préparation, étape par étape

La préparation des données, dans Power BI, se fait dans un éditeur dédié, **Power Query**, dont chaque transformation est une **étape nommée** : lire la source, promouvoir les en-têtes, changer les types, filtrer, fusionner deux tables, regrouper. La liste des étapes (appelées « étapes appliquées ») est **rejouée à chaque actualisation** ; elle est écrite en coulisses dans un langage de script, **M**. C'est exactement la **chaîne de nettoyage reproductible** du volume II : un script depuis le brut, rejouable.

```text
-- M : indicatif, non exécuté
let
    Source = Csv.Document ( File.Contents ( "lignes_commande.csv" ), [Delimiter = ","] ),
    Entetes = Table.PromoteHeaders ( Source ),
    Types = Table.TransformColumnTypes ( Entetes, {{"montant", type number}} ),
    Fusion = Table.NestedJoin ( Types, {"id_produit"}, produits, {"id_produit"}, "produit", JoinKind.LeftOuter ),
    Resultat = Table.ExpandTableColumn ( Fusion, "produit", {"categorie"} )
in
    Resultat
```

Le chemin équivalent en pandas, avec le **compte de lignes à chaque étape** (la règle d'or du volume II) :

```python
t = d["lig"].merge(d["cmd"][["id_commande", "date_commande"]], on="id_commande")
etapes = [("lecture + dates", len(t))]
t = t[t["date_commande"] >= "2025-01-01"]
etapes.append(("filtre 2025", len(t)))
t = t.merge(d["prod"][["id_produit", "categorie"]], on="id_produit", how="left", validate="m:1")
etapes.append(("fusion produits", len(t)))
etapes.append(("regroupement par catégorie", t["categorie"].nunique()))
print(pd.DataFrame(etapes, columns=["étape", "lignes"]).to_string(index=False))
```
<!--sortie-->
```text
                     étape  lignes
           lecture + dates   83905
               filtre 2025   29827
           fusion produits   29827
regroupement par catégorie       6
```

L'effectif passe de 83 905 lignes à 29 827 au filtre de 2025, **reste à 29 827** après la fusion (aucune ligne multipliée, aucune perdue) et le regroupement donne les six catégories. Le paramètre `validate="m:1"` demande à pandas de **vérifier que la clé du côté droit est unique** : si ce n'était pas le cas, la fusion échouerait au lieu de multiplier silencieusement les lignes (section 2.1.2). Dans Power Query, le même réflexe consiste à **regarder l'effectif après chaque fusion** et à vérifier la cardinalité de la relation.

Un mot sur la performance : quand la source est une base de données, Power Query essaie de **déléguer** les étapes à la base (on parle de *query folding*) : le filtre devient une clause `WHERE` du SQL envoyé, et seules les lignes utiles remontent. Un filtre placé **tôt** dans la liste d'étapes, avant une transformation que la base ne sait pas faire, est donc beaucoup plus efficace que le même filtre placé tard. La règle de bonne pratique rejoint celle du SQL : **filtrer et agréger au plus près de la source**.

### 2.4.3 La sécurité au niveau des lignes

Un même tableau de bord est souvent lu par des personnes qui **n'ont pas le droit de voir les mêmes données** : la direction voit toutes les régions, un responsable de région voit la sienne. Plutôt que de publier un rapport par personne, on applique une **sécurité au niveau des lignes** (*row-level security*, RLS) : un **filtre**, rattaché à un rôle, retire à l'utilisateur les lignes qu'il n'a pas le droit de voir, **avant** qu'une mesure ne soit calculée. Le filtre est posé sur une dimension (ici, la région du client) et se **propage** à la table de faits par la relation de l'étoile.

L'équivalent pandas est un simple filtre, appliqué à partir d'une **table de droits** : qui a le droit de voir quelle région ? Notre fonction `vue` renvoie les lignes de faits autorisées ; un utilisateur absent de la table n'en voit **aucune** (refus par défaut).

```python
droits = pd.DataFrame({"utilisateur": ["direction"] * 4 + ["resp_1", "resp_3", "resp_12", "resp_12"],
                       "region": ["Région 1", "Région 2", "Région 3", "Région 4", "Région 1", "Région 3", "Région 1", "Région 2"]})
f25 = faits[faits["date"] >= "2025-01-01"].merge(star["dim_client"][["id_client", "region"]], on="id_client")
vue = lambda u: f25[f25["region"].isin(droits.loc[droits["utilisateur"] == u, "region"])]
for u in ["direction", "resp_1", "resp_3", "resp_12", "stagiaire"]:
    print(f"{u:<10} {vue(u)['montant'].sum():>11,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
direction    1 324 764 €
resp_1         511 532 €
resp_3         537 175 €
resp_12        641 872 €
stagiaire            0 €
```

Le responsable de la Région 1 voit 511 532 € (sur 1 324 764 € pour toute la boutique), celui de la Région 3 voit 537 175 €, la personne qui a droit aux Régions 1 et 2 voit 641 872 €, et un stagiaire absent de la table des droits voit **zéro**. Les quatre régions fictives, additionnées, redonnent exactement le total de la direction : **aucune ligne n'est perdue ni comptée deux fois**. C'est le **contrôle de la sécurité** : la somme des vues autorisées doit être égale à la vue complète, et le nombre de lignes que **personne** ne voit doit être nul.

![La même mesure (chiffre d'affaires 2025 par région fictive) vue par la direction et par le responsable de la Région 1 : le filtre de ligne retire les autres régions avant le calcul.](figures/ch02-securite-lignes.png)


Deux modes de mise en œuvre existent dans la plupart des outils. Les rôles **statiques** : un rôle par région, avec un filtre fixe (`région = Région 1`), et l'on place les personnes dans les rôles. Simples, mais lourds à gérer quand les règles changent. Les rôles **dynamiques** : un seul rôle, dont le filtre consulte une **table de droits** avec l'**identité de l'utilisateur connecté** ; on gère alors les droits par une table (c'est le cas de notre `droits`), pas dans l'outil.

> ⚠️ **Ce que la sécurité par lignes ne fait pas.**
> - Elle **ne protège pas** contre ceux qui ont le droit de **modifier** le modèle ou de lire la source : les administrateurs et les auteurs voient tout, et l'on ne confond pas rôle de lecture et rôle de modification (à vérifier dans la documentation de votre outil).
> - Elle ne règle ni les **exports** ni les **extractions** : un utilisateur qui peut télécharger les données autorisées les partage ensuite comme il veut.
> - Elle ne rend pas une donnée **anonyme** (voir le volume II, chapitre 5) : un petit effectif dans une région reste identifiable.
> - Elle se **teste** : on se connecte « en tant que » chaque rôle et l'on compare aux chiffres attendus, comme ci-dessus, **avant** chaque publication.

### 2.4.4 Le déploiement

Un tableau de bord qui compte dans l'entreprise ne se modifie pas directement en production. Les équipes qui en gèrent plusieurs adoptent les pratiques du logiciel, adaptées à la BI.

- **Plusieurs environnements** : développement, test, production, avec des données et des droits distincts. On modifie dans l'un, on teste dans l'autre, on publie dans le dernier. Certaines offres proposent des **pipelines de déploiement** qui promeuvent un contenu d'un environnement à l'autre en conservant les paramètres propres à chacun (à vérifier dans votre version).
- **Le suivi des versions** : un fichier de rapport est souvent un **fichier binaire**, mal adapté aux outils de versions comme Git ; certaines offres proposent un **format de projet en fichiers texte** qui s'y prête mieux (à vérifier). À défaut, on **nomme** les versions et on tient un journal des changements.
- **Les jeux de données certifiés** : un seul modèle de référence, porté par une équipe, que tous les rapports réutilisent, plutôt qu'un modèle différent dans chaque rapport. C'est la façon la plus sûre d'avoir **un seul chiffre d'affaires** dans toute l'entreprise.
- **L'actualisation incrémentale** : au lieu de recharger trois ans de commandes chaque nuit, on ne recharge que **les derniers jours** et l'on garde le reste. On gagne en temps et en charge ; en contrepartie, une correction faite sur une donnée ancienne **n'apparaît pas** tant qu'on ne force pas un rechargement complet.
- **La surveillance** : alertes sur les échecs d'actualisation, suivi des temps de chargement, revue des droits à intervalles réguliers (les personnes changent de poste).

Cette liste se résume en un **contrôle de mise en production** que l'on coche avant chaque publication : effectifs des tables et clés vérifiés (2.1.2) ; chiffres clés recalculés par un autre chemin (2.3.5) ; définitions à jour dans le dictionnaire ; sécurité par lignes testée avec chaque rôle ; actualisation planifiée, notifications d'échec activées ; date des données affichée ; propriétaire et journal des changements renseignés.

> ✅ **À retenir.**
> - Une mesure DAX s'évalue dans un **contexte de filtres** ; `CALCULATE` le modifie, `ALL` en retire une partie : **chaque `ALL` est une décision de définition**. Les comparaisons dans le temps exigent une dimension de dates continue et se font **à période égale**.
> - Power Query enchaîne des **étapes nommées** rejouées à chaque actualisation : on **compte les lignes** après chaque fusion et l'on vérifie la cardinalité.
> - La **sécurité par lignes** filtre avant le calcul ; on la **teste** (la somme des vues autorisées égale la vue complète, un inconnu ne voit rien) et l'on connaît ses limites (administrateurs, exports, petits effectifs).
> - Le déploiement suit les pratiques du logiciel : environnements, versions, **jeu de données certifié**, actualisation incrémentale, surveillance, et un contrôle de mise en production.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.6 et 2.7, exercices 2.10 et 2.11.


## 2.5 ➕ Pour aller plus loin : Looker, Metabase, Superset, Qlik

> 🧭 **Section optionnelle.** Elle replace Power BI et Tableau dans un paysage plus large et propose une méthode pour **choisir un outil**. Aucun des produits cités ici n'a été exécuté pour ce livre : les descriptions viennent de la **documentation publique** telle que nous la connaissons, elles évoluent vite (fonctions, licences, offres), et **tout est à vérifier** dans la documentation à jour avant de décider quoi que ce soit. Les figures sont des maquettes dessinées, sans l'identité d'aucun produit.

Les outils de tableaux de bord se ressemblent plus qu'ils ne le prétendent : tous assemblent les **mêmes quatre briques**, en mettant l'accent sur l'une ou sur l'autre. Comprendre ces briques permet de **lire** n'importe quelle plaquette commerciale et de poser les bonnes questions.

![Les quatre briques que l'on retrouve, dans des proportions différentes, dans tous les outils de tableaux de bord : un modèle sémantique, des requêtes sur la source, des visuels, une gouvernance.](figures/ch02-briques-bi.png)


- Le **modèle sémantique** : les définitions (mesures, relations, dimensions) écrites **une fois** pour toute l'entreprise. C'est la brique que nous avons construite en 2.1.
- Les **requêtes** : la manière de **récupérer** les données de la source (SQL envoyé à une base, copie en mémoire).
- Les **visuels et tableaux de bord** : la partie visible, la plus démonstrative en vente, et la moins déterminante à long terme.
- La **gouvernance** : droits, versions, audit, certification, actualisation, surveillance. C'est elle qui sépare un outil d'équipe d'un outil d'entreprise.

### 2.5.1 Quatre familles d'outils

**Looker** (selon la documentation publique) est centré sur le **modèle sémantique écrit en code** : les mesures et les relations sont décrites dans un langage de modélisation, versionné comme du code, et **chaque visuel génère une requête SQL** envoyée à l'entrepôt de données. Il n'y a pas de copie en mémoire : la donnée reste chez soi. Force : des définitions **uniques et revues** comme du code, et une gouvernance forte. Vigilance : il faut des compétences de modélisation et de SQL, et l'entrepôt doit répondre vite.

**Metabase** est un outil **libre** (il existe aussi une offre hébergée) pensé pour que **des personnes sans SQL** posent des questions à une base : on construit une « question » par menus (filtrer, regrouper, résumer), ou on écrit du SQL, puis on place les questions dans un tableau de bord. Force : une mise en route très rapide et une prise en main simple. Vigilance : une modélisation sémantique plus légère ; sur de grandes organisations, il faut organiser les définitions pour éviter que chacun crée sa propre version de « chiffre d'affaires ».

**Superset** est un projet **libre** de la fondation Apache : un éditeur SQL (SQL Lab), une grande variété de graphiques, des « jeux de données » qui portent colonnes et métriques, des tableaux de bord et un système de rôles. Force : souplesse, absence de licence, intégration à de nombreuses bases. Vigilance : il faut **l'installer, le configurer et l'administrer** (ou payer une offre hébergée), ce qui demande un savoir-faire technique.

**Qlik** s'appuie sur un moteur **associatif** en mémoire : quand on sélectionne une valeur (une catégorie), l'outil montre non seulement les données qui lui sont liées, mais aussi celles qui **ne le sont pas** (leur couleur dit la différence). Les données se chargent par un **script** de chargement. Force : exploration très libre, sans parcours imposé. Vigilance : un moteur et un langage de script propres à apprendre, et une gouvernance à organiser.

Ces quatre descriptions sont des **raccourcis**, utiles pour s'orienter, et non des mesures : les produits changent, empruntent les uns aux autres, et la même fonction peut exister sous un autre nom. La figure suivante place les outils les uns par rapport aux autres **à titre indicatif**.

![Positionnement indicatif de six outils selon deux axes : mode de travail (par code et modélisation, ou par clics et glisser-déposer) et cadre d'usage (usage libre d'analystes ou cadre d'entreprise). Il s'agit d'une tendance d'après la documentation publique, à vérifier, pas d'une mesure.](figures/ch02-positionnement-bi.png)


> ⚠️ **Piège.** Une carte de positionnement, même honnête, **cache les compromis** : un outil « libre » n'est pas gratuit (on paie l'administration), un outil « cadré » n'est pas lourd si l'organisation est prête, et un outil « simple » devient complexe dès qu'il faut gouverner cent tableaux de bord. Elle aide à poser des questions ; elle ne répond pas à votre situation.

### 2.5.2 Choisir sans se laisser guider par la marque

On choisit un outil comme on choisit un fournisseur : à partir de **critères liés à la situation**, pas d'une impression de démonstration. Sept questions suffisent presque toujours.

1. **Où sont les données ?** Dans une base d'entreprise accessible par SQL, dans des fichiers, dans des services en ligne ? Un outil qui se branche mal à la source coûte plus cher que la licence.
2. **Qui construit, qui consulte ?** Des analystes qui écrivent du SQL, des métiers qui veulent cliquer, quelques lecteurs (la gérante) ou des centaines ?
3. **Quel besoin de gouvernance ?** Un chiffre d'affaires unique pour toute l'entreprise exige un modèle partagé et revu ; un suivi d'équipe se contente de moins.
4. **Quel coût réel ?** Licences par personne, hébergement, **temps d'administration**, formation, et coût de sortie si l'on change d'outil.
5. **Quelles compétences existent déjà ?** Un outil bien adapté mais que personne ne sait utiliser ne sert à rien.
6. **Quelles intégrations ?** Envoi par courriel, intégration dans une application, sécurité par lignes, **sécurité des données** (où elles sont stockées, qui y accède).
7. **Peut-on partir ?** Les définitions (mesures, relations) sont-elles **exportables**, ou prisonnières de l'outil ?

Pour décider, on **pondère** les critères et l'on **note** chaque option. Cette méthode, simple, a une propriété importante : elle rend les **préférences visibles** et discutables. Prenons trois options fictives, A, B et C, notées de 1 à 5 sur quatre critères, avec un premier jeu de poids, puis un second où la gouvernance pèse davantage.

```python
notes = pd.DataFrame({"coût": [5, 2, 4], "facilité": [4, 3, 2], "gouvernance": [2, 5, 3], "flexibilité": [2, 4, 5]}, index=["A", "B", "C"])
poids_1 = pd.Series({"coût": 3, "facilité": 3, "gouvernance": 2, "flexibilité": 2})
poids_2 = poids_1.mask(poids_1.index == "gouvernance", 4)
print(pd.DataFrame({"poids 1": notes @ poids_1, "poids 2": notes @ poids_2}))
```
<!--sortie-->
```text
   poids 1  poids 2
A       35       39
B       33       43
C       34       40
```

Avec le premier jeu de poids, **A** arrive en tête (35 points, devant C à 34 et B à 33) ; quand la gouvernance double de poids (de 2 à 4), c'est **B** qui gagne (43 points, devant C à 40 et A à 39). Aucun classement n'est « le vrai » : **il dépend de ce qui compte pour vous**, et la discussion sur les poids est précisément la discussion utile. Ces notes sont fictives ; les vôtres viendraient d'un essai.

L'**essai** est la meilleure preuve : prenez **la même page** (trois questions de la gérante, une semaine de données) et construisez-la dans deux outils, en notant le **temps** passé, l'**exactitude** des chiffres (recette, 2.3.5), le résultat du **test de cinq secondes** et l'**effort de maintenance** attendu. Deux jours d'essai valent mieux que deux semaines de plaquettes.

> 💡 **Intuition.** L'outil est le **dernier** choix à faire : avant, il y a les décisions, les indicateurs, les définitions et le modèle. Un modèle propre et un dictionnaire clair se **transportent** d'un outil à l'autre ; un tableau de bord dessiné sans eux s'abîme dès qu'on change d'outil.

### 2.5.3 Ce que les outils ne font pas à votre place

Aucun outil ne **choisit les indicateurs**, ne **définit** « client actif », ne **vérifie** qu'une jointure ne multiplie pas les lignes, ne **décide** de la bonne période de comparaison, ne **sait** si un chiffre est du bruit ou un signal. Il fait de beaux graphiques de tout ce qu'on lui donne, y compris des chiffres faux. Ce qui reste à l'analyste, c'est le **travail de fond** de ce chapitre : un modèle juste (2.1), des calculs compris (2.2 et 2.4), une conception partie de la décision (2.3), et une recette qui compare deux chemins. Quand l'outil change, ce travail reste.

> ✅ **À retenir.**
> - Tous les outils assemblent **quatre briques** : un modèle sémantique, des requêtes, des visuels, une gouvernance ; ils diffèrent par l'accent mis sur chacune.
> - **Looker** (modèle en code, SQL sur l'entrepôt), **Metabase** (libre, questions par menus), **Superset** (libre, SQL et administration) et **Qlik** (moteur associatif en mémoire) : des raccourcis à **vérifier** dans la documentation.
> - On choisit selon **sept questions** (données, personnes, gouvernance, coût réel, compétences, intégrations, sortie), avec des **critères pondérés** dont les poids sont discutés, puis un **essai** sur la même page dans deux outils.
> - L'outil est le dernier choix : un modèle propre, des définitions écrites et une recette **se transportent** d'un outil à l'autre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.


## Bilan du chapitre 2

La gérante voulait voir chaque lundi où en est la boutique, sans demander un fichier. Elle a désormais une **page**, six chiffres avec leur référence, une courbe de contrôle et deux alertes (livraisons à l'heure à 44,5 % pour un habituel de 76,3 %, ruptures à 35,0 % pour un habituel de 8,4 %) ; et vous avez un **modèle** (une table de faits de 83 905 lignes, quatre dimensions aux clés uniques, aucune ligne orpheline) dont chaque chiffre se recalcule par un autre chemin.

| Section | Ce que vous devez emporter |
|---|---|
| **2.1 Power BI** | Un outil de tableaux de bord enchaîne **connexion, préparation, modèle, mesures, visuels, publication, actualisation**, et chaque étape se reproduit à la main. Le **modèle en étoile** relie par des **identifiants uniques** (relier par le nom double le chiffre d'affaires). Une **mesure** se recalcule dans chaque contexte de filtres ; un **ratio** est une somme sur une somme ; le nombre de commandes **ne s'additionne pas** (25 163 contre 12 946). On planifie l'actualisation, on affiche la date des données, on ne publie jamais sur le web des données internes. |
| **2.2 Tableau** | Une **feuille** encode des champs par des canaux (position, couleur, taille) ; on choisit le canal selon la question. Un **calcul de table** opère sur le tableau affiché ; un **niveau de détail** opère à une granularité choisie. Un chiffre plausible n'est pas forcément le chiffre voulu : on recalcule une case en pandas. |
| **2.3 Conception** | On part des **décisions**, pas des données ; **trois niveaux** (vue d'ensemble, analyse, détail) ; chaque chiffre a **la référence qui convient** (l'habituel pour les livraisons, l'an dernier pour les ventes) ; test de **cinq secondes**, parcours en **Z**, contraste **calculé** (4,5 : 1 pour du petit texte). On **valide** par deux chemins, on **documente** dans un dictionnaire, on mesure l'**usage**. |
| **➕ 2.4 Power BI avancé** | **DAX** : contexte de filtres, `CALCULATE`, comparaisons **à période égale** (neuf mois contre douze : −26,3 %, absurde). **Power Query** : étapes nommées, effectifs après chaque fusion. **Sécurité par lignes** : la somme des vues autorisées égale la vue complète, un inconnu ne voit rien ; limites (administrateurs, exports, petits effectifs). **Déploiement** : environnements, jeu de données certifié, actualisation incrémentale. |
| **➕ 2.5 Autres outils** | Quatre briques communes (modèle, requêtes, visuels, gouvernance) ; Looker, Metabase, Superset, Qlik comme **familles** à vérifier dans la documentation ; sept questions de choix, critères **pondérés** (le classement change avec les poids), puis un **essai** sur la même page. L'outil est le dernier choix. |

> 💡 **Trois idées à retenir de tout le chapitre.**
> 1. **Un tableau de bord est un outil de décision.** On part de ce que la personne décidera, pas de ce que l'on sait calculer.
> 2. **Le travail se fait avant l'écran.** Un modèle juste, des définitions écrites et une recette qui compare deux chemins comptent plus que le choix des couleurs ou de l'outil.
> 3. **Un chiffre sans référence, sans date et sans définition est un décor.** Chaque carte dit à quoi on la compare, quand elle a été mise à jour et comment elle est calculée.

Vous savez maintenant **concevoir, modéliser et valider** un tableau de bord. Le chapitre 3 montre comment **construire des visualisations avec du code** (matplotlib, seaborn, plotly), ce qui donne un contrôle total sur chaque détail et permet d'**automatiser** ; le chapitre 4 explique comment **raconter** ce que le tableau de bord montre, et comment faire tourner un rapport **chaque semaine sans y toucher**.

> ✅ **À retenir, tout simplement.** Quand la gérante regarde la page le lundi, elle doit savoir en cinq secondes **si tout va bien**, et si ce n'est pas le cas, **ce qu'elle va faire**. Le reste est de la technique au service de cette phrase.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 et exercices 2.1 à 2.12, avec leurs corrigés.
