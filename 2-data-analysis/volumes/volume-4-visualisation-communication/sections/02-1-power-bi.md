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

```python hide
O.fig_flux()
```
<!--sortie-->
```text
figure : ch02-flux-bi.png
```

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

```python hide
O.fig_etoile(star)
```
<!--sortie-->
```text
figure : ch02-schema-etoile.png
```

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

```python hide
jouet_faits = pd.DataFrame({"id_ligne": range(1, 7), "nom_produit": ["Vase", "Bougie", "Vase", "Bougie", "Vase", "Plaid"], "montant": [20, 30, 20, 30, 10, 50]})
jouet_dim = pd.DataFrame({"id_produit": ["P1", "P2", "P3", "P4"], "nom_produit": ["Vase", "Bougie", "Vase", "Plaid"]})
jouet_jointure = jouet_faits.merge(jouet_dim, on="nom_produit")
assert jouet_faits["montant"].sum() == 160 and len(jouet_jointure) == 9 and jouet_jointure["montant"].sum() == 210
```

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

```python hide
v25 = ventes[ventes["annee"] == 2025]
ca_2025 = v25["montant"].sum()
ca_jardin = v25.loc[v25["categorie"] == "Jardin", "montant"].sum()
ca_jardin_site = v25.loc[(v25["categorie"] == "Jardin") & (v25["canal"] == "Site"), "montant"].sum()
print(round(ca_2025), round(ca_jardin), round(ca_jardin_site))
assert (round(ca_2025), round(ca_jardin), round(ca_jardin_site)) == (1324764, 353955, 166201)
```
<!--sortie-->
```text
1324764 353955 166201
```

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

```python hide
O.fig_visuels(d)
```
<!--sortie-->
```text
figure : ch02-visuels.png
```

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
