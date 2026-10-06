# Chapitre 3 : Big data et calcul distribué

> « Quand une machine ne suffit plus, on ne cherche pas une machine plus grosse : on apprend à faire travailler plusieurs machines ensemble. Et c'est là que les vrais problèmes commencent. »

> 🧭 **Où se situe ce chapitre.** Les chapitres 1 et 2 ont changé de **modèle** (réseaux de neurones, transformers). Celui-ci change d'**échelle** : que devient une analyse quand les données ne tiennent plus en mémoire, ou quand le calcul prend des heures ? Il suppose le SQL du volume I (chapitre 5, surtout les fonctions fenêtres de la section 5.3) et pandas (volume I, section 4.4).

La boutique a bien grandi. À ses débuts, quatre cents commandes tenaient dans un petit tableau ; aujourd'hui, le site, les réseaux sociaux et le magasin produisent **des millions de transactions** par an. La gérante veut des réponses de toujours (« combien a-t-on vendu par canal et par mois ? », « quels produits se vendent ensemble ? », « quels clients achètent le plus ? »), mais l'ordinateur portable commence à ramer, puis à planter.

Que faire ? Deux réflexes opposés sont à éviter.

- **Le réflexe « big data »** : « cent millions de lignes, il faut un *cluster* ! » C'est souvent faux. Les machines actuelles traitent très bien des dizaines de gigaoctets, et un cluster coûte cher en argent, en complexité et en pannes.
- **Le réflexe « ça ira bien »** : continuer avec les outils habituels en espérant que ça passe. Tant que les données tiennent en mémoire, c'est raisonnable ; au-delà, le programme s'arrête sur une erreur de mémoire sans prévenir.

Ce chapitre apprend à **choisir en connaissance de cause**. Il explique pourquoi et comment on répartit un calcul sur plusieurs machines, ce qu'on y gagne, ce qu'on y perd, puis il présente l'outil le plus répandu, **Apache Spark**.

## Le chemin de ce chapitre

- **3.1 Concepts du calcul distribué** : les quatre limites d'une machine, la **partition** des données, le modèle **MapReduce** (calculé à la main, puis programmé), la **loi d'Amdahl** qui plafonne les gains, les **pannes** et le théorème CAP, les formats **en colonnes** comme Parquet, et surtout **quand ne pas distribuer**.
- **3.2 Spark et PySpark** : l'architecture (pilote, exécuteurs, tâches), l'**évaluation paresseuse** et le **plan d'exécution**, les transformations qui déplacent des données (*shuffle*), les jointures, les fonctions fenêtres, les pièges (asymétrie des clés, petits fichiers) et une comparaison honnête avec DuckDB et pandas.
- ➕ **3.3 Hadoop, Kafka et traitement en flux** : l'écosystème qui a précédé Spark, les journaux de messages (Kafka) et le calcul sur des données qui n'arrêtent jamais d'arriver (fenêtres de temps, retards, garanties de livraison).

## Les données du chapitre

> 📦 **Un historique de transactions simulé.** Nous utilisons **deux millions de transactions** de la boutique, simulées avec une graine fixe par la fonction `gros_volume` du dossier `build/`. Chaque ligne a sept colonnes :
>
> | Colonne | Contenu |
> |---|---|
> | `id_transaction` | numéro unique (entier) |
> | `date` | jour de la transaction, en 2025 |
> | `id_client` | un des 200 000 clients |
> | `id_produit` | un des 500 produits |
> | `magasin` | une des dix villes (« Ville A » à « Ville J ») |
> | `canal` | `Boutique`, `Site` ou `Réseaux` |
> | `montant` | montant en euros |
>
> Ces fichiers **ne sont pas versionnés** : ils pèsent plusieurs dizaines de mégaoctets et se régénèrent en quelques secondes. Chaque exemple de ce chapitre les crée dans un dossier temporaire, qu'il efface ensuite.

> 💡 **Pourquoi deux millions et pas deux milliards ?** Parce que le livre doit s'exécuter sur un ordinateur ordinaire. Les mécanismes (partitions, mélange, plan d'exécution) sont **les mêmes** à toute échelle, et nous en mesurons les conséquences sur des tailles où elles se voient déjà. Une conséquence honnête : à deux millions de lignes, **un seul ordinateur suffit largement**, et le chapitre le montrera.


## 3.1 Concepts du calcul distribué

Distribuer un calcul, c'est le découper en morceaux que **plusieurs machines traitent en même temps**, puis recoller les résultats. L'idée tient en une phrase ; ses conséquences remplissent une section entière. Avant de voir comment on le fait, voyons **pourquoi** on y est parfois obligé, et **ce que cela coûte**.

### 3.1.1 Quatre raisons de dépasser une machine

Une machine bute sur quatre limites, qui n'arrivent pas en même temps.

1. **La mémoire.** Pour calculer un total par canal, il faut lire les données. Si elles ne tiennent pas dans la mémoire vive, un outil comme pandas, qui charge tout, s'arrête sur une erreur.
2. **Le disque.** Un seul disque a une capacité et un débit limités : lire un téraoctet d'un coup prend des heures, même si le calcul est trivial.
3. **Le temps.** Une analyse qui dure une nuit est acceptable une fois ; si on veut la relancer dix fois par jour, il faut la rendre dix fois plus rapide.
4. **La panne.** Une machine tombe en panne de temps en temps. Plus un calcul dure longtemps, plus la probabilité qu'une panne l'interrompe est grande.

Chiffrons la première limite sur nos données. Une fois chargées dans pandas, les deux millions de transactions occupent :


Environ **65 octets par ligne**, soit **130 Mo** pour deux millions de lignes : cela tient sans effort. Mais le même historique sur **un milliard de lignes** (une grande enseigne sur plusieurs années) demanderait **environ 65 Go** : bien plus que la mémoire d'un ordinateur de bureau (16 ou 32 Go). Ce n'est pas le calcul qui est difficile, c'est que **les données ne tiennent plus au même endroit**.

> 💡 **Règle de pouce pour décider.** Avant d'envisager une grappe de machines, comparez la taille de vos données à ce qu'une seule machine peut faire. Une machine moderne avec 64 Go de mémoire et un disque rapide traite confortablement **plusieurs dizaines de gigaoctets**, parfois bien plus avec des outils économes en mémoire (section 3.1.9). Distribuer a un coût de complexité réel : on ne le paie que quand on y est contraint.

### 3.1.2 Monter en puissance, ou en nombre ?

Deux façons de faire face à plus de données.

- **L'échelle verticale** (*scale up*) : acheter une machine plus puissante, avec plus de mémoire, plus de cœurs, un disque plus rapide. C'est **simple** (le programme ne change pas) mais **limité** (il existe une machine maximale) et **cher** (le prix croît plus vite que la puissance).
- **L'échelle horizontale** (*scale out*) : ajouter des machines ordinaires et répartir le travail. Il n'y a, en principe, pas de plafond, et le prix croît à peu près comme la puissance. Mais le programme doit être **conçu pour être réparti**, et les machines doivent communiquer, ce qui est lent et peut tomber en panne.

Répartir un calcul peut prendre deux formes. Le **parallélisme de données** applique **la même opération** à des morceaux différents des données (c'est ce que fait presque tout ce chapitre). Le **parallélisme de tâches** exécute **des opérations différentes** en même temps (par exemple, un calcul de prix et un calcul de stock). Le premier passe très bien à l'échelle, car on peut presque toujours couper les données en davantage de morceaux.

### 3.1.3 Découper les données : partitions

Pour répartir des données, on les découpe en **partitions**, chacune confiée à une machine. Comment décider qu'une ligne va dans telle partition ? Trois règles courantes.

| Règle | Principe | Avantage | Inconvénient |
|---|---|---|---|
| **Au hasard / en tourniquet** | on distribue les lignes à tour de rôle | morceaux de taille égale | une même clé se retrouve partout |
| **Par hachage de la clé** | on calcule `hachage(clé) mod n` : la partition ne dépend que de la clé | toutes les lignes d'une même clé sont **au même endroit** | une clé très fréquente fait une partition trop grosse |
| **Par intervalles** | partition 1 pour les dates de janvier, partition 2 pour février… | requêtes par plage très efficaces | déséquilibre possible (décembre est plus chargé) |

Voyons le hachage sur un exemple tout petit. Cinq clients, trois machines, et la règle « numéro de client modulo 3 » (une fonction de hachage simplifiée) :

| Client | 17 | 42 | 105 | 256 | 301 |
|---|---|---|---|---|---|
| Reste de la division par 3 | 2 | 0 | 0 | 1 | 1 |
| Machine | 3 | 1 | 1 | 2 | 2 |

Les clients 42 et 105 sont sur la même machine, ainsi que 256 et 301. Retenez la propriété essentielle : **quand on regroupe par client, tout ce qui concerne un client est déjà sur une seule machine**, et chaque machine peut calculer les totaux de ses clients **sans parler aux autres**.

> ⚠️ **Le revers : l'asymétrie des clés.** Si 30 % des transactions concernent un seul client (un revendeur, par exemple), la machine qui reçoit ce client reçoit au moins 30 % du travail, alors que les autres s'ennuient. Le calcul est aussi lent que la machine la plus chargée. Nous mesurerons ce phénomène, appelé **asymétrie** (*skew*), à la section 3.2.9.

### 3.1.4 MapReduce : compter des mots sur plusieurs machines

En 2004, des ingénieurs de Google ont publié un modèle de calcul si simple qu'il a changé le métier : **MapReduce**. Son idée : **beaucoup de calculs se découpent en trois phases**, dont une seule demande de faire circuler des données.

1. **Map** : chaque machine applique **une fonction à ses propres données** et produit des paires (clé, valeur). Aucune communication.
2. **Mélange** (*shuffle*) : on **regroupe toutes les paires de même clé** sur la même machine. C'est la phase coûteuse, car les données traversent le réseau.
3. **Reduce** : chaque machine **combine** les valeurs de chaque clé qu'elle a reçue.

L'exemple classique est de **compter les mots** de trois avis, chacun sur une machine différente. Les trois machines lisent « le colis est arrivé », « le colis est cassé » et « le prix est bon ».

![Comptage de mots avec MapReduce : chaque machine produit des paires (mot, 1) ; le mélange regroupe les paires de même mot sur une même machine ; chaque machine additionne.](figures/ch03-mapreduce.png)

À la main :

| Phase | Machine 1 | Machine 2 | Machine 3 |
|---|---|---|---|
| **map** | (le,1) (colis,1) (est,1) (arrivé,1) | (le,1) (colis,1) (est,1) (cassé,1) | (le,1) (prix,1) (est,1) (bon,1) |
| **mélange** | le → 1,1,1 ; est → 1,1,1 | colis → 1,1 ; prix → 1 | arrivé → 1 ; cassé → 1 ; bon → 1 |
| **reduce** | le : 3 ; est : 3 | colis : 2 ; prix : 1 | arrivé : 1 ; cassé : 1 ; bon : 1 |

Seul le **mélange** déplace des données d'une machine à l'autre. La fonction map ne connaît que ses propres lignes ; la fonction reduce ne connaît que les valeurs d'une clé. C'est cette **ignorance volontaire** qui permet de répartir le travail sans coordination compliquée : si une machine tombe en panne, on relance simplement son morceau ailleurs.

Programmons cela sur les 8 000 avis clients de la boutique, avec un **processus par partition** sur notre machine (la logique est identique à celle d'un cluster, la communication en moins). Voici les deux phases :


```python
import collections, re

def map_partition(textes):                       # phase map : compte les mots d'un morceau
    c = collections.Counter()
    for t in textes:
        c.update(re.findall(r"\w+", t.lower()))
    return c

def reduce_compteurs(compteurs):                 # phase reduce : additionne les comptes partiels
    total = collections.Counter()
    for c in compteurs:
        total.update(c)
    return total
```

On découpe les avis en quatre morceaux, on lance un processus par morceau, puis on fusionne, et on **vérifie** que le résultat est identique à celui d'un calcul séquentiel :

```python
from multiprocessing import Pool

avis = pd.read_csv("donnees/avis_clients.csv")["texte"].fillna("").tolist()
morceaux = [avis[i::4] for i in range(4)]
with Pool(4) as pool:
    reparti = reduce_compteurs(pool.map(map_partition, morceaux))
print("identique au calcul séquentiel :", reparti == map_partition(avis))
print(len(reparti), "mots distincts ; les plus fréquents :", reparti.most_common(3))
```
<!--sortie-->
```text
identique au calcul séquentiel : True
642 mots distincts ; les plus fréquents : [('est', 3170), ('pas', 3168), ('le', 3069)]
```

Le résultat réparti est **exactement** le résultat séquentiel. Ce n'est pas une coïncidence : on a pu découper parce que **l'addition est associative et commutative** (on peut additionner les comptes dans n'importe quel ordre). Quand une opération de combinaison n'a pas cette propriété (une médiane, par exemple), on ne peut pas se contenter de combiner des résultats partiels : il faut réfléchir à une autre stratégie.

> 🧪 **Et le gain de temps ?** Il dépend de la machine et de la charge : nous ne le citons pas ici, puisqu'un chiffre de durée ne se reproduit pas d'une exécution à l'autre. La loi d'Amdahl, ci-dessous, en donne une borne qui, elle, ne dépend pas de la machine. Le cahier propose de mesurer le gain sur votre propre ordinateur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1 (un MapReduce complet sur les avis), exercices 3.1 à 3.3.

### 3.1.5 La loi d'Amdahl : pourquoi dix fois plus de machines n'est pas dix fois plus vite

Si on utilise $n$ machines, va-t-on $n$ fois plus vite ? Presque jamais, parce qu'une partie du travail **ne se répartit pas** : lire le fichier de départ, assembler les résultats, écrire la sortie. Notons $p$ la **fraction du temps qui est parallélisable** (la partie répartissable), et $1-p$ la fraction séquentielle. Avec $n$ machines :

- la partie séquentielle prend toujours le même temps, $(1-p)\,T$ ;
- la partie parallélisable est divisée par $n$ : elle prend $\dfrac{p\,T}{n}$.

Le temps total est donc $T\left[(1-p)+\dfrac{p}{n}\right]$ et l'**accélération** (le rapport entre le temps initial et le nouveau) vaut

$$S(n)=\frac{T}{T\left[(1-p)+p/n\right]}=\frac{1}{(1-p)+\dfrac{p}{n}}.$$

C'est la **loi d'Amdahl** (1967). Quand $n$ devient immense, $p/n$ tend vers 0 et l'accélération tend vers

$$S(\infty)=\frac{1}{1-p}.$$

**Exemple chiffré.** Un traitement dure 100 minutes, dont 10 minutes de partie séquentielle ($p=0{,}9$). Avec $n=10$ machines : $S(10)=\dfrac{1}{0{,}1+0{,}9/10}=\dfrac{1}{0{,}19}\approx5{,}26$. Dix fois plus de machines, **cinq fois et un quart** plus vite seulement. Avec 100 machines : $S(100)=\dfrac{1}{0{,}1+0{,}009}\approx9{,}17$. Et même avec une infinité de machines, on ne dépasse jamais $\dfrac1{0{,}1}=10$ : les 10 minutes séquentielles restent.


![Accélération d'Amdahl en fonction du nombre de machines, pour trois fractions parallélisables : plus la partie séquentielle est grande, plus vite on atteint un plafond.](figures/ch03-amdahl.png)


Lisez la figure : avec 99 % de travail parallélisable, 64 machines donnent une accélération d'environ **39**, loin de 64 ; avec 90 %, environ **8,8** ; avec 50 %, à peine **2**. L'enseignement pratique est plus important que la formule : **avant d'ajouter des machines, cherchez la partie séquentielle** (lecture, assemblage, mélange) et réduisez-la.

> ⚠️ **La loi d'Amdahl est optimiste.** Elle ignore le coût de la communication entre machines, qui **augmente** avec leur nombre. Au-delà d'un certain point, ajouter des machines peut même **ralentir** le calcul. À l'inverse, si l'on **grossit le problème** en même temps que la grappe (deux fois plus de données, deux fois plus de machines), la partie séquentielle pèse moins : c'est la loi de **Gustafson**, qui explique pourquoi les grandes plateformes restent efficaces sur de très gros volumes.

### 3.1.6 Le mélange : là où se joue la performance

Dans MapReduce, la phase map est « gratuite » (chaque machine travaille chez elle) mais le **mélange** coûte cher : les données traversent le réseau, sont écrites sur disque puis relues, et **tout le monde attend le plus lent**. Retenez la règle de pouce qui guide toute optimisation distribuée :

> **Le coût d'un calcul distribué se mesure surtout en quantité de données qui voyagent.** Un bon programme répartit tôt, **filtre et agrège avant le mélange**, et mélange le moins possible.

C'est ce que fait un **combineur** (*combiner*) : avant le mélange, chaque machine **additionne localement** ses propres paires. Dans notre exemple, au lieu d'envoyer trois fois (le,1) depuis trois machines, chaque machine enverrait un seul (le,3) si elle avait vu « le » trois fois. Sur de vrais volumes, la différence se compte en gigaoctets.

### 3.1.7 Les pannes : répliquer et recalculer

Sur une grappe de mille machines, il y a **toujours** une machine en panne. Deux stratégies s'attaquent à ce problème.

**Répliquer les données.** On garde plusieurs copies de chaque morceau sur des machines différentes (trois, typiquement). Si chaque machine tombe en panne indépendamment avec la probabilité $q=0{,}01$ sur une période, la probabilité que les **trois** copies disparaissent est $q^3=10^{-6}$, un sur un million. Le prix : un espace disque **triplé**.

**Recalculer au lieu de sauvegarder.** Plutôt que de sauvegarder chaque résultat intermédiaire, on **retient comment on l'a obtenu** (la « recette » : lire tel fichier, filtrer, regrouper). Si une partition est perdue, on **rejoue la recette** sur le morceau d'origine. C'est le principe du **lignage** de Spark, que nous retrouverons.

### 3.1.8 Le théorème CAP et la cohérence

Quand les données sont **copiées sur plusieurs machines**, une question se pose : que se passe-t-il si le réseau se coupe entre deux d'entre elles ? Le **théorème CAP** (Brewer, 2000 ; démontré par Gilbert et Lynch, 2002) l'énonce ainsi : un système distribué ne peut pas garantir en même temps

- la **cohérence** (*Consistency*) : tout lecteur voit la dernière écriture ;
- la **disponibilité** (*Availability*) : toute requête reçoit une réponse ;
- la **tolérance au partitionnement du réseau** (*Partition tolerance*) : le système continue de fonctionner malgré une coupure.

Comme les coupures de réseau **arrivent** dans la vraie vie, il faut les tolérer ; le choix réel se fait **entre cohérence et disponibilité pendant la coupure**. Un système **cohérent** refuse de répondre tant que les copies ne sont pas d'accord (un virement bancaire). Un système **disponible** répond avec ce qu'il sait, quitte à donner une valeur un peu ancienne (un compteur de « j'aime »). On parle alors de **cohérence à terme** (*eventual consistency*) : si plus personne n'écrit, toutes les copies finissent par converger.

> 💡 **Le bon réflexe.** Ne demandez pas « quel système est le meilleur ? » mais « **que coûte une réponse un peu périmée, comparé à une absence de réponse ?** ». La réponse change d'une application à l'autre, et c'est elle qui guide le choix.

### 3.1.9 Les formats : lire des lignes ou des colonnes

Comment stocker un tableau dans un fichier ? Deux philosophies.

- **Par lignes** (CSV, JSON, bases de données transactionnelles) : on écrit une ligne entière après l'autre. C'est idéal pour **ajouter une commande** ou lire **tout un enregistrement**.
- **Par colonnes** (Parquet, ORC, entrepôts analytiques) : on écrit toute la colonne `montant`, puis toute la colonne `canal`, etc. C'est idéal pour les **analyses**, qui ne lisent presque toujours que **quelques colonnes sur beaucoup de lignes**.

![Un tableau de quatre lignes stocké par lignes (à gauche) ou par colonnes (à droite) : pour additionner les montants, le stockage en colonnes ne lit que la colonne utile.](figures/ch03-ligne-colonne.png)

Le format en colonnes a trois autres avantages. Les valeurs d'une colonne se **ressemblent**, donc elles se **compressent** bien (la colonne `canal` ne contient que trois valeurs distinctes : on stocke un petit dictionnaire et des numéros). Le fichier contient des **statistiques** (minimum, maximum) par bloc, qui permettent de **sauter** les blocs inutiles. Enfin il conserve les **types** des colonnes (un entier reste un entier), alors qu'un CSV est du texte. Mesurons l'écart sur nos deux millions de lignes, écrites une fois en CSV et une fois en Parquet :


Le fichier Parquet est environ **3,6 fois plus petit** que le CSV (28 Mo contre 99,5 Mo) et lire **une seule colonne** y est **beaucoup plus rapide** : on ne lit pas les six autres, et on ne convertit pas du texte en nombres. Ces écarts, de l'ordre de plusieurs fois, se retrouvent à toute échelle ; c'est pourquoi **Parquet est le format par défaut des analyses sur de gros volumes**.

Reste le **stockage** lui-même. Sur de très gros volumes, on utilise souvent un **stockage objet** (un service qui range des fichiers dans des « seaux » et les retrouve par leur nom) plutôt qu'un disque classique : il est peu coûteux, quasiment illimité, et accessible depuis toutes les machines. Le prix est une latence plus élevée par accès, d'où l'intérêt de lire de **gros fichiers en colonnes** plutôt que beaucoup de petits.

### 3.1.10 Quand ne PAS distribuer

Avant de monter une grappe, regardons ce qu'une machine unique sait faire. **DuckDB** est un moteur de bases de données analytiques qui s'exécute **dans le processus Python**, lit directement les fichiers Parquet, exploite tous les cœurs et traite les données **par colonnes**. Sur nos deux millions de transactions :

```python
import duckdb

con = duckdb.connect()
resultat = con.sql(f"""
    SELECT canal, COUNT(*) AS transactions, ROUND(SUM(montant)) AS chiffre_affaires
    FROM read_parquet('{DOSSIER}/*.parquet') GROUP BY canal ORDER BY canal""").df()
print(resultat.to_string(index=False))
```
<!--sortie-->
```text
   canal  transactions  chiffre_affaires
Boutique        500725        19162622.0
 Réseaux        599994        22972662.0
    Site        899281        34445539.0
```

La réponse arrive **sans serveur et sans configuration, en quelques lignes**. Pour quelques millions de lignes, et même quelques centaines de millions sur une machine bien dotée, c'est l'outil raisonnable. Voici une grille pour décider :

| Votre situation | Outil raisonnable |
|---|---|
| données qui tiennent en mémoire (jusqu'à quelques Go) | pandas |
| données de quelques Go à quelques dizaines de Go, sur une machine | **DuckDB**, ou pandas avec lecture par morceaux |
| plus de données que ce qu'une machine peut stocker ou lire dans un délai acceptable ; traitements répétés | **Spark** (section 3.2) sur une grappe |
| données qui arrivent en continu et exigent une réponse en secondes | **traitement en flux** (section 3.3) |

> ⚠️ **Le piège du CV.** Écrire « Spark » sur une candidature est tentant, mais **installer et exploiter une grappe** est un métier (supervision, mises à jour, coûts). Une équipe qui utilise Spark sur des données qui tiennent dans une machine **perd du temps et de l'argent**. La bonne question n'est jamais « quel outil est à la mode ? » mais « **quelle est la plus petite infrastructure qui fait le travail ?** »

> ✅ **À retenir.**
> - On distribue pour trois raisons : **mémoire, temps et panne**. Si une machine suffit, **elle suffit**.
> - On découpe les données en **partitions** (par hachage, par intervalles…) ; un hachage met toutes les lignes d'une clé au même endroit, au risque de l'**asymétrie**.
> - **MapReduce** : *map* (local), **mélange** (réseau, coûteux), *reduce* (local). Il fonctionne parce que l'opération de combinaison est **associative**.
> - **Amdahl** : $S(n)=1/[(1-p)+p/n]$ ; la partie séquentielle impose un **plafond** $1/(1-p)$. Le coût de communication aggrave le tableau.
> - Pannes : on **réplique** les données et on **recalcule** à partir du lignage. **CAP** : pendant une coupure, il faut choisir entre cohérence et disponibilité.
> - **Parquet** (en colonnes, compressé, typé) bat le CSV de plusieurs fois en taille et en lecture. Pour quelques millions de lignes, **DuckDB** sur une machine suffit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.2 et exercices 3.1 à 3.6.


## 3.2 Spark et PySpark

**Apache Spark** est un moteur de calcul distribué qui est devenu, depuis les années 2010, l'outil de référence pour traiter de gros tableaux de données. Il reprend l'idée de MapReduce (découper, calculer localement, mélanger, combiner) mais en **gardant les données en mémoire** entre deux étapes et en offrant une interface très proche de pandas et de SQL. **PySpark** est son interface Python.

### 3.2.1 L'architecture : un pilote et des exécuteurs

Un programme Spark se compose de :

- un **pilote** (*driver*) : le processus qui exécute votre script Python. Il **construit le plan** du calcul, le découpe en tâches et suit leur avancement ;
- des **exécuteurs** (*executors*) : des processus répartis sur les machines de la grappe, qui exécutent les **tâches** et conservent les partitions en mémoire ;
- un **gestionnaire de ressources**, qui attribue les machines (YARN, Kubernetes, ou le gestionnaire intégré de Spark).

![Architecture de Spark : le pilote demande des exécuteurs au gestionnaire de ressources, puis leur envoie des tâches et récupère les résultats.](figures/ch03-spark-architecture.png)


Trois notions de vocabulaire suffisent pour lire la suite.

| Terme | Définition |
|---|---|
| **Partition** | un morceau des données ; **une tâche traite une partition** |
| **Tâche** (*task*) | l'unité de travail : une opération appliquée à une partition |
| **Étape** (*stage*) | un groupe de tâches qui s'exécutent **sans échange de données** ; une étape s'arrête là où un mélange est nécessaire |

Pour que ce chapitre s'exécute sur un seul ordinateur, nous lançons Spark en **mode local** : le pilote et les exécuteurs sont alors des fils d'exécution d'un même processus (ici deux, `local[2]`). Le **code est identique** à celui d'une grappe ; seule la ligne de configuration change.

```python
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder.master("local[2]").appName("chapitre3")
         .config("spark.ui.enabled", "false")
         .config("spark.sql.shuffle.partitions", "4")       # partitions après un mélange
         .config("spark.sql.adaptive.enabled", "false")     # plan fixe, pour que le livre soit reproductible
         .config("spark.sql.warehouse.dir", TMP + "/entrepot")
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
```

> 🧪 **Pourquoi désactiver l'optimisation adaptative ?** Spark sait, depuis la version 3, **réajuster son plan en cours de route** (c'est l'*Adaptive Query Execution*). C'est utile en production, mais cela rend le plan dépendant des données observées ; pour que vous retrouviez exactement les mêmes plans que ceux du livre, nous la coupons. Sur une vraie grappe, **laissez-la activée**.

### 3.2.2 Lire des données

Spark lit directement un dossier de fichiers Parquet, et le traite comme **un seul tableau** :

```python
ventes = spark.read.parquet(DOSSIER)
ventes.printSchema()
print("lignes :", ventes.count(), "; partitions :", ventes.rdd.getNumPartitions())
```
<!--sortie-->
```text
root
 |-- id_transaction: long (nullable = true)
 |-- date: timestamp_ntz (nullable = true)
 |-- id_client: long (nullable = true)
 |-- id_produit: integer (nullable = true)
 |-- magasin: string (nullable = true)
 |-- canal: string (nullable = true)
 |-- montant: double (nullable = true)

lignes : 2000000 ; partitions : 2
```

Un tableau Spark est un **DataFrame** (même mot que dans pandas, mais ce n'est pas le même objet : celui-ci est réparti et **ne vit pas dans la mémoire de votre programme**). La lecture a créé une partition par fichier ou par morceau de fichier : c'est le **degré de parallélisme** du calcul. Notons au passage que Spark a lu les **types** dans le fichier, sans rien deviner.

### 3.2.3 L'évaluation paresseuse : transformations et actions

C'est la notion la plus importante de Spark, et celle qui déroute le plus. **Spark ne calcule rien quand on lui décrit un calcul.** Il se contente de **mémoriser la recette**. Il ne travaille que quand on lui demande un **résultat**.

| | Exemples | Effet |
|---|---|---|
| **Transformation** | `filter`, `select`, `groupBy`, `join`, `withColumn` | construit un nouveau DataFrame, **sans calcul** |
| **Action** | `count`, `show`, `collect`, `toPandas`, `write` | **déclenche** le calcul et rend un résultat |

Pourquoi cette paresse ? Parce qu'en voyant **toute la recette** avant de commencer, Spark peut l'**optimiser** : ne lire que les colonnes utiles, appliquer un filtre au plus tôt, fusionner des étapes. Un exemple : le chiffre d'affaires par canal.

```python
par_canal = (ventes.groupBy("canal")
             .agg(F.count("*").alias("transactions"), F.round(F.sum("montant")).alias("chiffre_affaires")))
print(type(par_canal).__name__)          # aucun calcul n'a eu lieu : c'est une recette
par_canal.orderBy("canal").show()        # l'action : le calcul se déclenche maintenant
```
<!--sortie-->
```text
DataFrame
+--------+------------+----------------+
|   canal|transactions|chiffre_affaires|
+--------+------------+----------------+
|Boutique|      500725|     1.9162622E7|
| Réseaux|      599994|     2.2972662E7|
|    Site|      899281|     3.4445539E7|
+--------+------------+----------------+
```

La première instruction n'a fait **aucun calcul** : `par_canal` est une recette. Le calcul ne commence qu'à l'action `show`.

> ⚠️ **Une action à chaque ligne, c'est le piège classique.** Si vous appelez `count()` pour « voir où on en est » après chaque transformation, **chaque appel relance tout le calcul depuis la lecture des fichiers**. Calculez ce dont vous avez besoin, **une seule fois**, ou mettez le résultat en cache (section 3.2.6).

Pour le voir, demandons à Spark de nous montrer la recette qu'il a retenue, sans l'exécuter.

### 3.2.4 Lire un plan d'exécution

Le **plan physique** (que la méthode `explain` affiche ; nous le récupérons sous forme de texte) : la liste des opérations que Spark va réellement exécuter, de la **dernière** (en haut) à la **première** (en bas).


```python
print(plan(par_canal))
```
<!--sortie-->
```text
*(2) HashAggregate(keys=[canal], functions=[count(1), sum(montant)], output=[canal, transactions, chiffre_affaires])
+- Exchange hashpartitioning(canal, 4), ENSURE_REQUIREMENTS
   +- *(1) HashAggregate(keys=[canal], functions=[partial_count(1), partial_sum(montant)], output=[canal, count, sum])
      +- *(1) ColumnarToRow
         +- FileScan parquet [canal,montant]
```

Lisons-le **de bas en haut**.

1. `FileScan parquet [canal,montant]` : on lit les fichiers, et **seulement les colonnes `canal` et `montant`** (Spark a vu que les autres colonnes ne servent à rien). La ligne `ColumnarToRow` convertit les colonnes lues en lignes pour l'étape suivante.
2. `HashAggregate` avec `partial_count` et `partial_sum` : chaque tâche calcule **ses propres sous-totaux** par canal, localement. C'est l'équivalent exact du *combineur* de la section 3.1.6.
3. `Exchange hashpartitioning(canal, 4)` : le **mélange**. Les sous-totaux de chaque canal sont envoyés à une même partition (sur quatre, d'après notre réglage). C'est l'unique endroit où des données circulent.
4. `HashAggregate` final : on additionne les sous-totaux reçus.

On retrouve **map, mélange, reduce**, sans que nous l'ayons écrit : Spark a traduit une description de haut niveau en MapReduce optimisé. Retenez la distinction qu'il en tire :

- une transformation **étroite** (*narrow*) utilise **une seule** partition d'entrée pour produire une partition de sortie (`filter`, `select`, `withColumn`) : elle se fait **sur place**, sans réseau ;
- une transformation **large** (*wide*) a besoin de **plusieurs** partitions d'entrée (`groupBy`, `join`, `distinct`, `orderBy`) : elle impose un mélange, qui apparaît dans le plan sous le nom **`Exchange`**.

> 💡 **Le réflexe du plan.** Quand un calcul Spark est lent, la première chose à faire est de lire son plan et de **compter les `Exchange`**. Chacun est un point de communication ; un bon programme en a le moins possible, et les place **après** les filtres et les agrégations partielles.

Spark découpe le plan en **étapes** à chaque `Exchange`. Une étape s'exécute sans communication ; l'étape suivante ne peut pas commencer avant que **toutes** les tâches de la précédente aient fini (voilà le « tout le monde attend le plus lent »).

### 3.2.5 Le même calcul en SQL

Spark comprend aussi le SQL, et les deux écritures aboutissent **au même plan**. Pour les analystes, c'est une aubaine : on peut réutiliser tout le SQL du volume I.

```python
ventes.createOrReplaceTempView("ventes")
en_sql = spark.sql("""
    SELECT canal, COUNT(*) AS transactions, ROUND(SUM(montant)) AS chiffre_affaires
    FROM ventes GROUP BY canal""")
print("même résultat :", en_sql.orderBy("canal").toPandas().equals(par_canal.orderBy("canal").toPandas()))
print("même plan :", plan(en_sql) == plan(par_canal))
```
<!--sortie-->
```text
même résultat : True
même plan : True
```

Choisissez l'écriture que votre équipe lit le mieux : l'une ne va pas plus vite que l'autre.

Un exemple un peu plus riche, qui enchaîne filtre, calculs de date, agrégation et tri : le chiffre d'affaires mensuel de la boutique en ligne.

```python
mensuel = (ventes.filter(F.col("canal") == "Site")
           .withColumn("mois", F.month("date"))
           .groupBy("mois").agg(F.round(F.sum("montant")).alias("chiffre_affaires"))
           .orderBy("mois"))
print(mensuel.toPandas().head(4).to_string(index=False))
```
<!--sortie-->
```text
 mois  chiffre_affaires
    1         2929826.0
    2         2648709.0
    3         2920430.0
    4         2812932.0
```

Pour des analyses de taille raisonnable, on ramène **le résultat** (pas les données !) dans pandas avec `toPandas()`, et on reprend ses outils habituels (graphiques, statistiques).

> ⚠️ **`collect()` et `toPandas()` rapatrient tout chez le pilote.** Sur un résultat de dix lignes, c'est parfait. Sur un DataFrame de cent millions de lignes, c'est une panne de mémoire assurée. **Agrégez d'abord, rapatriez ensuite.**

### 3.2.6 Partitions et mémoire : `repartition`, `coalesce`, `cache`

Le nombre de partitions détermine le parallélisme. Trop peu, et des cœurs restent inactifs ; trop, et le coût d'organisation des tâches dépasse le travail utile. Deux opérations permettent de l'ajuster.

- `repartition(n)` redistribue les données en $n$ partitions égales : c'est un **mélange complet** (un `Exchange`), donc coûteux ; on peut aussi **repartitionner par colonne**.
- `coalesce(n)` **fusionne** des partitions voisines sans mélange : plus économique, mais seulement pour **diminuer** le nombre.

```python
print("lecture :", ventes.rdd.getNumPartitions())
print("après repartition(8) :", ventes.repartition(8).rdd.getNumPartitions())
print("après coalesce(2) :", ventes.coalesce(2).rdd.getNumPartitions())
```
<!--sortie-->
```text
lecture : 2
après repartition(8) : 8
après coalesce(2) : 2
```

Une règle de pouce : prévoir **au moins deux à quatre partitions par cœur disponible**, et, sur de grands volumes, les découper en morceaux de **100 à 200 Mo** environ (le plus grand des deux nombres l'emporte).

Autre outil : le **cache**. Quand on réutilise plusieurs fois un même DataFrame, Spark **recalcule toute la recette** à chaque action. `cache()` demande de **garder le résultat en mémoire** après le premier calcul.

```python
propre = ventes.filter(F.col("montant") > 0).cache()
n1 = propre.count()                          # premier calcul : lecture et filtre, résultat mis en mémoire
n2 = propre.count()                          # second appel : lu depuis la mémoire
print("même nombre de lignes :", n1 == n2, "; données en cache :", propre.is_cached)
propre.unpersist()
```
<!--sortie-->
```text
même nombre de lignes : True ; données en cache : True
```

Le cache n'est pas gratuit : il consomme de la mémoire (qui manquera ailleurs). **N'y mettez qu'un DataFrame réutilisé plusieurs fois**, et libérez-le avec `unpersist()` quand vous n'en avez plus besoin.

### 3.2.7 Les jointures

Joindre deux tableaux répartis est l'opération la plus coûteuse de Spark. Pour réunir deux lignes qui ont la même clé, **il faut que ces lignes soient sur la même machine**. Spark choisit entre deux stratégies.

- **La jointure par tri et mélange** (*sort-merge join*) : les **deux** tableaux sont mélangés par la clé (deux `Exchange`), triés, puis fusionnés. C'est le cas général ; il fonctionne pour deux gros tableaux, mais il est **lent**.
- **La jointure par diffusion** (*broadcast join*) : si l'un des tableaux est **petit**, on en envoie une **copie à chaque exécuteur**. Le gros tableau **ne bouge pas**, car chacun de ses morceaux trouve la copie du petit tableau sur place. Il n'y a **aucun mélange du gros tableau**.

Joignons les transactions au catalogue des 500 produits, pour calculer le chiffre d'affaires par catégorie :

```python
catalogue = spark.createDataFrame(pd.DataFrame({
    "id_produit": np.arange(1, 501, dtype=np.int32),
    "categorie": np.array(["Cuisine", "Maison", "Jardin", "Loisirs"])[np.arange(500) % 4]}))
par_categorie = (ventes.join(F.broadcast(catalogue), "id_produit")
                 .groupBy("categorie").agg(F.round(F.sum("montant")).alias("chiffre_affaires")))
print(plan(par_categorie))
```
<!--sortie-->
```text
*(2) HashAggregate(keys=[categorie], functions=[sum(montant)], output=[categorie, chiffre_affaires])
+- Exchange hashpartitioning(categorie, 4), ENSURE_REQUIREMENTS
   +- *(1) HashAggregate(keys=[categorie], functions=[partial_sum(montant)], output=[categorie, sum])
      +- *(1) Project [montant, categorie]
         +- *(1) BroadcastHashJoin [id_produit], [id_produit], Inner, BuildRight, false, false
            :- *(1) Filter isnotnull(id_produit)
            :  +- *(1) ColumnarToRow
            :     +- FileScan parquet [id_produit,montant]
            +- BroadcastExchange HashedRelationBroadcastMode(List(cast(input[0, int, true] as bigint)),false)
               +- LocalTableScan [id_produit, categorie]
```

Le plan contient `BroadcastHashJoin` : **la diffusion a été utilisée**. Le catalogue passe par un `BroadcastExchange` (la copie envoyée aux exécuteurs) ; le seul autre `Exchange` est celui de l'agrégation finale, et **les deux millions de lignes ne sont pas mélangés pour la jointure**. Sans l'indication `F.broadcast`, Spark choisit lui-même la diffusion si l'un des tableaux est plus petit qu'un seuil (10 Mo par défaut). Voyons ce qui se passe quand on interdit la diffusion :

```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")      # diffusion automatique interdite
sans = ventes.join(catalogue, "id_produit").groupBy("categorie").agg(F.sum("montant"))
texte = plan(sans)
print("jointure par tri et mélange :", "SortMergeJoin" in texte, "; mélanges (Exchange) :", texte.count("Exchange hashpartitioning"))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")  # on remet la valeur par défaut
```
<!--sortie-->
```text
jointure par tri et mélange : True ; mélanges (Exchange) : 3
```

Sans diffusion, Spark **mélange les deux tableaux par la clé** (deux `Exchange`) avant de les fusionner, puis fait l'agrégation (un troisième) : les deux millions de lignes traversent le réseau pour une jointure avec cinq cents lignes.

```python
print(par_categorie.orderBy("categorie").toPandas().to_string(index=False))
```
<!--sortie-->
```text
categorie  chiffre_affaires
  Cuisine        19186073.0
   Jardin        19136956.0
  Loisirs        19117146.0
   Maison        19140648.0
```

> 💡 **Règle d'or des jointures.** Quand un tableau est petit (catalogue, liste de magasins, table de correspondance), **diffusez-le**. C'est de loin la meilleure optimisation à la portée d'un analyste.

### 3.2.8 Fonctions fenêtres et fonctions personnalisées

Les **fonctions fenêtres** du SQL (volume I, section 5.3) existent aussi en Spark, et se **répartissent** : le tableau est mélangé par la clé de partition de la fenêtre, puis chaque groupe est traité indépendamment. Cherchons, pour chaque magasin, le jour de plus gros chiffre d'affaires :

```python
from pyspark.sql import Window

par_jour = ventes.groupBy("magasin", "date").agg(F.sum("montant").alias("ca"))
fenetre = Window.partitionBy("magasin").orderBy(F.desc("ca"))
meilleurs = (par_jour.withColumn("rang", F.row_number().over(fenetre)).filter("rang = 1")
             .select("magasin", "date", F.round("ca").alias("ca")).orderBy("magasin"))
print(meilleurs.toPandas().head(3).to_string(index=False))
```
<!--sortie-->
```text
magasin       date      ca
Ville A 2025-05-03 25465.0
Ville B 2025-05-16 24716.0
Ville C 2025-11-19 24805.0
```

Le calcul se fait en deux étapes : une agrégation, puis un classement par magasin. Notez que **`partitionBy` détermine le mélange** : une fenêtre sans `partitionBy` ramènerait **toutes** les lignes sur une seule partition, et ferait perdre tout parallélisme (Spark émet alors un avertissement).

Enfin, il est tentant d'écrire **une fonction Python** pour un calcul que Spark ne connaît pas (une **UDF**, *user-defined function*). C'est possible, mais **cher** : chaque ligne doit être **envoyée du moteur de Spark à un processus Python, puis renvoyée**. Les fonctions intégrées de Spark (`F.round`, `F.when`, `F.month`…) s'exécutent dans le moteur lui-même et sont **optimisables** ; une UDF est une boîte noire que Spark ne peut ni optimiser ni vectoriser.

> ✅ **Bon réflexe.** Avant d'écrire une UDF, cherchez la fonction intégrée correspondante (il y en a plus de 400). Si l'UDF est inévitable, préférez une **UDF vectorielle** (*pandas UDF*), qui traite des lots de lignes au lieu d'une à la fois.

### 3.2.9 L'asymétrie des clés et le salage

Reprenons le problème annoncé à la section 3.1.3. Les données de la boutique sont bien réparties, mais imaginons qu'**un revendeur** (le client numéro 1) concentre **30 % des transactions**. Regroupons par client, c'est-à-dire par hachage de la clé.


Une partition reçoit **47,5 % des lignes** (30 % pour le revendeur, plus sa part des autres clients) au lieu de 25 % : elle contient environ **1,9 fois la moyenne**, et c'est elle qui fixe la durée du calcul, pendant que les trois autres terminent et attendent. Ajouter des machines n'y changerait rien : **la clé 1 reste sur une seule**.

La parade s'appelle le **salage** (*salting*). On **ajoute un grain de sel aléatoire** à la clé, qui la **découpe** en plusieurs sous-clés (« 1-0 », « 1-1 », …, « 1-31 »), réparties sur des partitions différentes. On agrège d'abord sur la clé salée (chaque morceau a une taille normale), puis on **réagrège** les résultats partiels sur la vraie clé, ce qui est peu coûteux : il n'y a plus que 32 lignes pour la clé 1.

```python
sel = F.floor(F.rand(8) * 32).cast("int")                         # un grain de sel entre 0 et 31
sale = asym.withColumn("sel", sel).repartition(4, "cle", "sel")   # la clé 1 est maintenant répartie
```


![Nombre de lignes par partition avant et après salage : la clé très fréquente fait gonfler une partition ; le sel répartit la charge.](figures/ch03-asymetrie.png)

Après salage, la plus grosse partition ne dépasse plus que d'environ **1,15 fois** la moyenne : la charge est quasi uniforme. Le prix du salage est une **étape d'agrégation supplémentaire** et un code plus compliqué : on ne le met en place que lorsque le plan, ou le suivi des tâches, montre **une tâche bien plus longue que les autres**. Sur les versions récentes de Spark, l'optimisation adaptative que nous avons désactivée **détecte et corrige** automatiquement certaines asymétries de jointure : une raison de plus de la laisser activée en production.

### 3.2.10 Écrire : partitionnement et petits fichiers

Le résultat d'un calcul s'écrit généralement en Parquet. Deux décisions comptent.

**Partitionner par colonne.** `partitionBy("canal")` crée **un sous-dossier par valeur** (`canal=Site/`, `canal=Boutique/`…). Une requête qui filtre sur `canal` ne **lit que le dossier concerné** : c'est l'**élagage de partitions** (*partition pruning*), et il peut diviser le temps de lecture par le nombre de valeurs.

```python
sortie = TMP + "/par_canal"
ventes.write.mode("overwrite").partitionBy("canal").parquet(sortie)
print(sorted(d for d in os.listdir(sortie) if not d.startswith(("_", "."))))
```
<!--sortie-->
```text
['canal=Boutique', 'canal=Réseaux', 'canal=Site']
```

Choisissez une colonne **peu variée** (canal, pays, mois) ; une colonne comme `id_client` créerait 200 000 dossiers et un désastre.

**Éviter les petits fichiers.** Chaque tâche d'écriture produit **un fichier par partition**. Si le DataFrame a 40 partitions et que vous partitionnez en plus par une colonne à 3 valeurs, vous pouvez obtenir jusqu'à 120 minuscules fichiers. C'est le **problème des petits fichiers** : chaque fichier a un coût fixe d'ouverture, de lecture des métadonnées et de planification d'une tâche, qui dépasse vite le coût de lire ses données. On le prévient en **ramenant le nombre de partitions** (`coalesce`) avant d'écrire.


Écrire un DataFrame de 40 partitions donne **40 fichiers** ; après `coalesce(2)`, **2 seulement** : même données, **vingt fois moins de fichiers à ouvrir**. Visez des fichiers de 100 Mo à 1 Go, pas de quelques kilo-octets.

### 3.2.11 Spark, DuckDB ou pandas ? Une comparaison honnête

Les trois outils répondent à la même question. Vérifions-le, puis comparons-les sur nos deux millions de lignes : le chiffre d'affaires par magasin.

```python
import duckdb

via_spark = ventes.groupBy("magasin").agg(F.round(F.sum("montant"), 2).alias("ca")).orderBy("magasin").toPandas()
via_duckdb = duckdb.sql(f"SELECT magasin, ROUND(SUM(montant), 2) AS ca FROM read_parquet('{DOSSIER}/*.parquet') GROUP BY magasin ORDER BY magasin").df()
via_pandas = pdf.groupby("magasin")["montant"].sum().round(2).reset_index(name="ca")
print("Spark = DuckDB :", np.allclose(via_spark["ca"], via_duckdb["ca"]))
print("Spark = pandas :", np.allclose(via_spark["ca"], via_pandas["ca"]))
```
<!--sortie-->
```text
Spark = DuckDB : True
Spark = pandas : True
```


Les **trois outils donnent le même résultat**. Ce qui les distingue, c'est **où et comment** ils travaillent.

| | **pandas** | **DuckDB** | **Spark** |
|---|---|---|---|
| Où ça tourne | dans votre programme | dans votre programme | une grappe (ou un mode local) |
| Limite de volume | la mémoire de la machine | le disque de la machine (il traite par morceaux) | **la taille de la grappe** |
| Démarrage | immédiat | immédiat | plusieurs secondes (lancement de la machine virtuelle Java) |
| Parallélisme | un seul cœur (le plus souvent) | tous les cœurs | **toutes les machines** |
| Interface | Python | SQL | Python, SQL, Scala |
| Quand le choisir | exploration, petits volumes | analyses de quelques Go à quelques centaines de Go | **au-delà d'une machine**, ou **infrastructure déjà en place** |

Sur nos deux millions de lignes, **Spark ne gagne rien** : DuckDB, qui n'a rien à démarrer, répond plus vite, et pandas reste du même ordre de grandeur (nous avons mesuré les trois, sans citer de durée qui ne se reproduirait pas). Le coût fixe de Spark (machine virtuelle Java, organisation des tâches, mélanges) ne se rentabilise qu'avec des volumes, ou des machines, qui le justifient. Ce n'est pas un défaut, c'est le **prix de sa généralité** : il est conçu pour le cas où les autres ne peuvent plus rien. Tant que ce cas n'est pas le vôtre, **ne l'utilisez pas**.

> ✅ **À retenir.**
> - Spark = un **pilote** qui planifie, des **exécuteurs** qui calculent des **tâches** sur des **partitions**. Le mode local permet d'apprendre sur un ordinateur avec **le même code**.
> - **Évaluation paresseuse** : les transformations construisent une recette, les **actions** déclenchent le calcul. Évitez une action à chaque ligne.
> - Un **plan** (`explain`) se lit de bas en haut ; chaque **`Exchange`** est un mélange, donc un coût. Transformations **étroites** (sur place) contre **larges** (mélange).
> - **Jointure par diffusion** pour tout petit tableau : le gros n'est jamais mélangé. **Évitez les UDF** quand une fonction intégrée existe.
> - **Asymétrie des clés** : une tâche surchargée fixe la durée de tout ; on la corrige par le **salage**.
> - Écrire en **Parquet partitionné** par une colonne peu variée ; éviter les **petits fichiers**.
> - Spark donne les **mêmes résultats** que pandas ou DuckDB ; il ne se justifie que **quand une machine ne suffit plus**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.3 à 3.4 et exercices 3.7 à 3.13.


## ➕ 3.3 Hadoop, Kafka et traitement en flux

> 🧭 **Section complémentaire.** Elle replace Spark dans son écosystème (d'où il vient, ce qui l'entoure) et aborde le calcul sur des données **qui n'arrêtent jamais d'arriver**. Vous pouvez la sauter sans perdre le fil du volume ; elle est utile si vous croisez ces outils en entreprise.

### 3.3.1 D'où vient Spark : l'écosystème Hadoop

Avant Spark, il y avait **Hadoop**, né vers 2006 à partir des publications de Google sur MapReduce et sur son système de fichiers distribué. Hadoop fournit trois briques.

| Brique | Rôle |
|---|---|
| **HDFS** (*Hadoop Distributed File System*) | stocker de gros fichiers, **découpés en blocs** (128 Mo en général) **répliqués** sur plusieurs machines (trois copies par défaut) |
| **YARN** | répartir les machines entre les applications (le « gestionnaire de ressources » de la section 3.2.1) |
| **MapReduce** | le modèle de calcul de la section 3.1.4, **avec écriture sur disque entre chaque étape** |

La réplication de HDFS applique ce que nous avons vu à la section 3.1.7 : un bloc perdu est **recopié automatiquement** depuis une des deux autres copies. Au-dessus de cette base se sont greffés des outils : **Hive** (écrire du SQL qui se traduit en MapReduce), **HBase** (une base de données répartie)…

Spark a supplanté MapReduce pour une raison simple : **MapReduce écrit sur disque après chaque étape**, alors que Spark **garde les données en mémoire** d'une étape à l'autre. Pour un algorithme itératif (un apprentissage automatique, par exemple), la différence est de plusieurs ordres de grandeur. Aujourd'hui, Spark tourne volontiers **sans Hadoop** : au lieu de HDFS, on utilise un **stockage objet** dans le nuage (section 3.1.9), et au lieu de YARN, souvent **Kubernetes**. Hadoop reste très présent dans les grandes entreprises qui l'ont installé dans les années 2010 ; savoir le reconnaître suffit à l'analyste.

> 💡 **Lakehouse.** Les formats de table récents (**Delta Lake**, **Apache Iceberg**, **Apache Hudi**) ajoutent à des fichiers Parquet posés sur un stockage objet ce qui manquait aux fichiers bruts : des **transactions** (une écriture réussit entièrement ou pas du tout), l'**historique des versions** et la modification de lignes. Le résultat, entre l'entrepôt de données et le lac de fichiers, est parfois appelé *lakehouse*. Nous y reviendrons au chapitre 5 (ingénierie des données).

### 3.3.2 Lot ou flux ?

Jusqu'ici, nous avons traité des données **au repos** : un historique complet, un calcul qui commence et qui finit. C'est le **traitement par lots** (*batch*). Beaucoup d'usages exigent pourtant une réponse **pendant que les données arrivent** : détecter une fraude à la carte bancaire, mettre à jour un tableau de bord de ventes toutes les minutes, alerter quand un capteur dépasse un seuil. C'est le **traitement en flux** (*streaming*).

| | **Lot** | **Flux** |
|---|---|---|
| Données | un ensemble fini, connu à l'avance | une suite **sans fin** |
| Réponse | à la fin du calcul | **en continu**, résultat provisoire mis à jour |
| Latence typique | minutes à heures | secondes, ou moins |
| Difficulté | volume | **temps** : ordre d'arrivée, retards, reprises |

Le flux pose une difficulté neuve : on ne peut pas attendre « la fin » pour calculer. Il faut donc (1) un endroit où **ranger les messages** en attendant qu'on les lise (Kafka), et (2) une manière de **découper le temps** pour agréger (les fenêtres).

### 3.3.3 Kafka : un journal de messages

**Apache Kafka** est le système de transport de messages le plus répandu. Son idée centrale est d'une grande simplicité : un **journal** (*log*) où l'on ne fait qu'**ajouter** des messages à la fin, sans jamais les modifier, et que **chaque lecteur parcourt à son rythme**.

Voici le vocabulaire.

| Terme | Sens |
|---|---|
| **Sujet** (*topic*) | un journal nommé : `transactions`, `clics`… |
| **Partition** | un sujet est découpé en partitions, chacune **un journal ordonné** ; c'est l'unité de parallélisme |
| **Décalage** (*offset*) | le numéro d'un message **dans sa partition** (0, 1, 2…) |
| **Producteur** | un programme qui **publie** des messages |
| **Consommateur** | un programme qui **lit** ; il retient jusqu'où il a lu (son décalage) |
| **Groupe de consommateurs** | des consommateurs qui **se partagent les partitions** d'un sujet : chaque partition est lue par **un seul** membre du groupe |

Comme Kafka n'est pas installé dans l'environnement du livre (c'est un service, pas une bibliothèque), voici un **journal minimal en Python** qui en reproduit le fonctionnement. Il tient en quelques lignes, ce qui montre à quel point l'idée est simple :

```python
import zlib

class Journal:
    """Un sujet Kafka minimal : des partitions, où l'on n'ajoute que des messages."""
    def __init__(self, partitions):
        self.partitions = [[] for _ in range(partitions)]

    def publier(self, cle, valeur):
        p = zlib.crc32(str(cle).encode()) % len(self.partitions)    # même clé, même partition
        self.partitions[p].append((cle, valeur))
        return p, len(self.partitions[p]) - 1                       # (partition, décalage)

    def lire(self, p, decalage, maximum=10):
        return self.partitions[p][decalage:decalage + maximum]
```

Publions six achats de trois clients (deux d'entre eux achètent plusieurs fois), dans un sujet à trois partitions :

```python
ventes_flux = Journal(partitions=3)
for client, montant in [("c17", 20), ("c42", 35), ("c17", 12), ("c105", 8), ("c42", 50), ("c17", 9)]:
    print(client, montant, "→ (partition, décalage) =", ventes_flux.publier(client, montant))
```
<!--sortie-->
```text
c17 20 → (partition, décalage) = (2, 0)
c42 35 → (partition, décalage) = (0, 0)
c17 12 → (partition, décalage) = (2, 1)
c105 8 → (partition, décalage) = (0, 1)
c42 50 → (partition, décalage) = (0, 2)
c17 9 → (partition, décalage) = (2, 2)
```

Deux propriétés se voient dans le résultat. **Tous les messages d'un même client vont dans la même partition** (l'ordre y est donc respecté pour ce client, alors qu'il n'est pas garanti **entre** partitions). Et chaque message a un **décalage** : un lecteur n'a besoin de retenir que ce nombre pour savoir où il en est. Comme le journal n'est jamais modifié, **deux lecteurs indépendants** peuvent lire les mêmes messages, et on peut **rejouer le passé** : il suffit de repartir d'un décalage plus ancien. C'est ce qui distingue Kafka d'une file d'attente classique, où un message lu disparaît.

```python
dernier_lu = {p: 0 for p in range(3)}                   # le « décalage » de chaque partition pour un lecteur
for p in range(3):
    for cle, montant in ventes_flux.lire(p, dernier_lu[p]):
        dernier_lu[p] += 1
print("décalages retenus par partition :", dernier_lu)
dernier_lu = {p: 0 for p in range(3)}                   # rejouer le passé : on repart de zéro
print("messages relus depuis le début :", sum(len(ventes_flux.lire(p, 0)) for p in range(3)))
```
<!--sortie-->
```text
décalages retenus par partition : {0: 3, 1: 0, 2: 3}
messages relus depuis le début : 6
```

#### Garanties de livraison

Que se passe-t-il quand un consommateur **plante** en plein travail ? Tout dépend du moment où il **note son avancement** (le *commit* de son décalage).

| Garantie | Ordre des opérations | Conséquence |
|---|---|---|
| **Au plus une fois** (*at most once*) | on note le décalage, **puis** on traite | un plantage perd des messages, jamais de doublon |
| **Au moins une fois** (*at least once*) | on traite, **puis** on note le décalage | un plantage entraîne des **doublons**, jamais de perte |
| **Exactement une fois** (*exactly once*) | traitement **idempotent** ou transaction | ni perte ni doublon (au prix d'une conception soignée) |

La garantie « au moins une fois » est la plus courante. Elle oblige à écrire des traitements **idempotents** : refaire la même opération ne doit pas changer le résultat. Simulons un plantage entre le traitement et la note du décalage, sur trois transactions identifiées :

```python
transactions = [("t1", 20), ("t2", 35), ("t3", 12)]
total, vus = 0, set()
for tour in range(2):                                    # le consommateur plante après t2 au tour 0, puis reprend
    for ident, montant in transactions[: 2 if tour == 0 else 3]:
        total += montant                                 # traitement naïf : on additionne
print("total naïf :", total, "; total correct :", sum(m for _, m in transactions))
total = 0
for tour in range(2):
    for ident, montant in transactions[: 2 if tour == 0 else 3]:
        if ident not in vus:                             # idempotence : on ignore un identifiant déjà traité
            vus.add(ident); total += montant
print("total idempotent :", total)
```
<!--sortie-->
```text
total naïf : 122 ; total correct : 67
total idempotent : 67
```

Le traitement naïf **compte deux fois** les deux premières transactions, rejouées après le redémarrage ; le traitement idempotent, qui retient les **identifiants déjà vus**, retombe sur le bon total. Un identifiant unique par message est donc **un cadeau à se faire dès la conception**.

### 3.3.4 Découper le temps : les fenêtres

On ne peut pas additionner un flux infini ; on additionne **sur une fenêtre de temps**. Trois types sont courants.

![Les trois types de fenêtres sur huit évènements : fixes (chaque évènement dans une seule fenêtre), glissantes (dans plusieurs) et de session (délimitées par des silences).](figures/ch03-fenetres.png)


- **Fenêtres fixes** (*tumbling*) : des tranches consécutives, de même durée, sans chevauchement (« les ventes de chaque minute »).
- **Fenêtres glissantes** (*sliding*) : de même durée mais qui **avancent par pas plus petits** que leur durée, donc se chevauchent (« les ventes des 20 dernières secondes, mises à jour toutes les 10 secondes »). Chaque évènement appartient à plusieurs fenêtres.
- **Fenêtres de session** : une fenêtre dure **tant que l'activité continue** et se ferme après un silence (« la visite d'un internaute, qui se termine quand il reste inactif plus de 30 minutes »).

Prenons onze achats de la boutique en ligne, avec leur **heure** et leur **montant**. Ils arrivent en quatre paquets, dans l'ordre ci-dessous (heure en secondes depuis 10 h, montant en euros) :

```python
lots = [[(0, 10), (30, 20), (70, 5)], [(80, 15), (95, 5), (130, 10)], [(140, 8), (20, 99), (190, 12)], [(200, 6), (250, 9)]]
evenements = pd.DataFrame([(s, m) for lot in lots for s, m in lot], columns=["seconde", "montant"])
evenements["fenetre"] = evenements["seconde"] // 60 * 60          # début de la fenêtre fixe d'une minute
print(evenements.groupby("fenetre")["montant"].agg(["count", "sum"]).to_string())
```
<!--sortie-->
```text
         count  sum
fenetre            
0            3  129
60           3   25
120          2   18
180          2   18
240          1    9
```

Le calcul par lots donne le **résultat exact** : cinq fenêtres, avec 129 € dans la première (dont 99 € d'un achat qui n'est arrivé qu'**en troisième paquet**, mais s'est produit à la 20ᵉ seconde). Ce détail est au cœur du flux.

### 3.3.5 Temps de l'évènement, retards et filigrane

Deux horloges coexistent :

- le **temps de l'évènement** : quand l'achat **s'est produit** ;
- le **temps de traitement** : quand le système **l'a reçu**.

Ils diffèrent, parfois de beaucoup : un téléphone sans réseau envoie ses évènements un quart d'heure plus tard ; un message se perd, puis est renvoyé. Nos onze messages en sont un exemple : l'achat de 99 € s'est produit à la 20ᵉ seconde, mais **il est arrivé après des évènements de la 140ᵉ**. On l'appelle un **évènement en retard**.

Pour calculer les ventes de la première minute, **quand peut-on dire que la fenêtre est complète** ? On ne le sait jamais avec certitude : un retard peut toujours arriver. On pose donc une règle : **le filigrane** (*watermark*). Il s'exprime comme un retard maximal toléré : « aucun évènement n'arrive avec plus de $D$ secondes de retard ». À chaque instant, le **filigrane = (temps d'évènement le plus récent observé) − $D$**. Une fenêtre se **ferme** quand le filigrane dépasse sa fin ; les évènements qui arrivent ensuite pour cette fenêtre sont **écartés**.

Le compromis est inévitable : un $D$ **petit** donne des résultats rapides, mais on perd les retardataires ; un $D$ **grand** les récupère, mais **retarde** le résultat final de chaque fenêtre. Simulons-le en Python pur, en traitant les messages **dans leur ordre d'arrivée** :

```python
def avec_filigrane(lots, retard_max, largeur=60):
    plus_recent, ecartes, fenetres = 0, [], collections.defaultdict(int)
    for lot in lots:
        for seconde, montant in lot:
            debut = seconde // largeur * largeur
            if debut + largeur <= plus_recent - retard_max:      # la fenêtre est déjà fermée
                ecartes.append((seconde, montant))
            else:
                fenetres[debut] += montant
            plus_recent = max(plus_recent, seconde)
    return dict(sorted(fenetres.items())), ecartes
```

```python
for D in (60, 120):
    fen, ecartes = avec_filigrane(lots, retard_max=D)
    print(f"retard toléré {D:3d} s : première fenêtre = {fen[0]} € ; évènements écartés = {ecartes}")
```
<!--sortie-->
```text
retard toléré  60 s : première fenêtre = 30 € ; évènements écartés = [(20, 99)]
retard toléré 120 s : première fenêtre = 129 € ; évènements écartés = []
```

Avec 60 secondes de tolérance, la fenêtre de 0 à 60 s se ferme dès que l'évènement de la 130ᵉ seconde est vu ; le 99 € arrivé ensuite est **écarté** et la première fenêtre sous-évalue le total. Avec 120 secondes, il est **conservé**. Le choix du filigrane est donc **une décision métier** : combien de retard supporte-t-on, contre combien de latence ?

> ⚠️ **Écarter un évènement est silencieux.** Aucun message d'erreur ne vous prévient qu'une valeur a été ignorée. En production, on **compte les évènements écartés** et on surveille ce compteur : une hausse signale un problème en amont (réseau, horloge d'un capteur).

### 3.3.6 Le flux dans Spark : Structured Streaming

Spark traite un flux avec **la même interface que le lot**. Le flux est vu comme un **tableau qui ne cesse de s'allonger** ; on écrit la requête comme pour un tableau fini, et Spark la **réévalue** sur chaque nouveau paquet. Faisons-le avec les onze achats, déposés comme quatre fichiers JSON dans un dossier (chaque fichier simule un paquet de messages ; en production, ce serait un sujet Kafka).


```python
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

schema = StructType([StructField("t", StringType()), StructField("montant", DoubleType())])
flux_ventes = (spark.readStream.schema(schema).option("maxFilesPerTrigger", 1).json(flux)    # un paquet par cycle
               .withColumn("t", F.to_timestamp("t")))
requete = (flux_ventes.groupBy(F.window("t", "60 seconds")).agg(F.sum("montant").alias("ca"))
           .writeStream.format("memory").queryName("ventes_minute").outputMode("complete")
           .trigger(availableNow=True).start())
requete.awaitTermination(120)
```

L'agrégation est la même que pour un lot (`groupBy` sur une `window` de 60 secondes) ; ce qui change, c'est `writeStream`, qui dit **où et comment** écrire les résultats successifs. Le mode **`complete`** réécrit le tableau entier à chaque paquet ; `update` n'écrit que les lignes modifiées ; `append` n'écrit une ligne qu'une fois sa fenêtre **fermée** (donc avec un filigrane). Comparons le résultat de ce flux au calcul par lots de la section précédente :

```python
resultat = spark.sql("SELECT window.start AS debut, ca FROM ventes_minute ORDER BY 1").toPandas()
attendu = evenements.groupby("fenetre")["montant"].sum().to_numpy()
print("fenêtres :", len(resultat), "; identique au calcul par lots :", np.allclose(resultat["ca"], attendu))
```
<!--sortie-->
```text
fenêtres : 5 ; identique au calcul par lots : True
```

Le flux, traité paquet par paquet, aboutit **exactement au même résultat que le lot**, y compris pour le 99 € arrivé en retard : **sans filigrane, Spark conserve tout l'état** et accepte les retardataires, à vie. C'est exact, mais l'état **grossit sans limite** : sur un flux qui dure des mois, la mémoire finit par manquer. C'est précisément à cela que sert `withWatermark("t", "60 seconds")` : il autorise Spark à **oublier** les fenêtres anciennes. Son comportement exact (quels évènements sont écartés, à quel moment les résultats sont émis) dépend du mode de sortie et de la version ; consultez la documentation de votre version avant de vous y fier, et **testez** avec vos propres données plutôt que d'en déduire le comportement. Notre simulation de la section précédente en montre le principe, pas le détail d'implémentation de Spark.


### 3.3.7 Un tableau de bord de ventes, de bout en bout

Assemblons les briques pour un tableau de bord qui affiche les ventes de la minute écoulée.

1. Les **caisses et le site** publient chaque vente dans un sujet Kafka, **avec un identifiant unique** et la clé du magasin (les ventes d'un magasin arrivent dans l'ordre).
2. Une **application Spark Structured Streaming** lit le sujet, agrège par **fenêtre d'une minute** avec un **filigrane de quelques minutes** (le retard maximal des caisses), et **ignore les doublons** par identifiant.
3. Elle **écrit les résultats** dans une base ou un fichier Parquet, que le tableau de bord lit.
4. Un **compteur d'évènements écartés** et un compteur de **retard de lecture** (combien de messages le consommateur a de retard sur le journal) sont **surveillés** : si l'un grimpe, on est alerté.

> ✅ **À retenir.**
> - **Hadoop** = HDFS (stockage répliqué) + YARN (ressources) + MapReduce (écriture disque entre étapes). Spark l'a supplanté en gardant les données **en mémoire**.
> - **Lot** : un ensemble fini ; **flux** : une suite sans fin, avec une réponse continue. La difficulté du flux, c'est le **temps**.
> - **Kafka** = un **journal** où l'on ajoute des messages, découpé en **partitions** ; chaque lecteur retient son **décalage**, donc on peut **rejouer le passé**.
> - **Au moins une fois** est la garantie courante : écrivez des traitements **idempotents** (identifiant unique par message).
> - **Fenêtres** : fixes, glissantes, de session. **Filigrane** : le retard maximal toléré ; un évènement plus tardif est **écarté, sans bruit**.
> - Spark traite un flux avec **la même interface** que le lot (`readStream`, `writeStream`).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 à 3.6 et exercices 3.14 à 3.18.


## Bilan du chapitre 3

Vous savez maintenant :

- **décider s'il faut distribuer** : les quatre limites d'une machine (mémoire, disque, temps, panne), ce qu'une machine moderne sait faire seule, et pourquoi **DuckDB** ou pandas suffisent bien plus souvent qu'on ne le croit ;
- **découper un calcul** : partitions par hachage ou par intervalles, le modèle **MapReduce** (*map*, mélange, *reduce*), et la raison pour laquelle il marche (une combinaison **associative**) ;
- **borner un gain** : la **loi d'Amdahl** $S(n)=1/[(1-p)+p/n]$ et son plafond $1/(1-p)$, avec le coût du mélange qui aggrave le tableau ;
- **raisonner sur les pannes** (réplication, lignage) et sur le **théorème CAP** (cohérence ou disponibilité pendant une coupure) ;
- **choisir un format** : Parquet (en colonnes, compressé, typé) contre CSV (en lignes) ;
- **écrire du Spark** : l'architecture pilote–exécuteurs, l'**évaluation paresseuse**, la lecture d'un **plan** et de ses `Exchange`, `repartition`, `coalesce`, `cache`, la **jointure par diffusion**, les fonctions fenêtres, le coût des UDF ;
- **repérer et corriger** l'**asymétrie des clés** (par le salage) et le **problème des petits fichiers** ;
- (en option) **situer Hadoop et Kafka**, distinguer **lot et flux**, choisir une **fenêtre** et un **filigrane**, et écrire des traitements **idempotents** sous la garantie « au moins une fois ».

Le fil conducteur du chapitre tient en une phrase : **distribuer est un moyen, pas un but, et son coût se mesure en données qui voyagent**. Une machine qui suffit est préférable à dix qui coordonnent ; quand elle ne suffit plus, la performance se joue dans le **mélange** : on le lit dans le plan, on le réduit par le filtrage et l'agrégation précoces, on évite qu'une clé l'écrase.

Le chapitre 4 change de sujet : ce qui compte maintenant n'est plus de calculer un résultat, mais de **le rendre fiable dans la durée**. Un modèle est mis en production, il vieillit, ses données changent : c'est l'objet du **MLOps** (suivi des expériences, déploiement, surveillance).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.6 (MapReduce sur les avis, loi d'Amdahl sur votre machine, plan d'exécution et jointure, asymétrie et salage, journal de messages idempotent, fenêtres et filigrane) et exercices 3.1 à 3.18.

