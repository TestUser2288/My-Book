## 3.1 Concepts du calcul distribué

Distribuer un calcul, c'est le découper en morceaux que **plusieurs machines traitent en même temps**, puis recoller les résultats. L'idée tient en une phrase ; ses conséquences remplissent une section entière. Avant de voir comment on le fait, voyons **pourquoi** on y est parfois obligé, et **ce que cela coûte**.

### 3.1.1 Quatre raisons de dépasser une machine

Une machine bute sur quatre limites, qui n'arrivent pas en même temps.

1. **La mémoire.** Pour calculer un total par canal, il faut lire les données. Si elles ne tiennent pas dans la mémoire vive, un outil comme pandas, qui charge tout, s'arrête sur une erreur.
2. **Le disque.** Un seul disque a une capacité et un débit limités : lire un téraoctet d'un coup prend des heures, même si le calcul est trivial.
3. **Le temps.** Une analyse qui dure une nuit est acceptable une fois ; si on veut la relancer dix fois par jour, il faut la rendre dix fois plus rapide.
4. **La panne.** Une machine tombe en panne de temps en temps. Plus un calcul dure longtemps, plus la probabilité qu'une panne l'interrompe est grande.

Chiffrons la première limite sur nos données. Une fois chargées dans pandas, les deux millions de transactions occupent :

```python hide
pdf = pd.concat([pd.read_parquet(os.path.join(DOSSIER, f)) for f in sorted(os.listdir(DOSSIER))], ignore_index=True)
mem = pdf.memory_usage(deep=True).sum()
print("lignes :", len(pdf))
print("mémoire en Mo :", round(mem / 1e6))
print("octets par ligne :", round(mem / len(pdf)))
print("pour un milliard de lignes, en Go :", round(mem / len(pdf) * 1e9 / 1e9))
```
<!--sortie-->
```text
lignes : 2000000
mémoire en Mo : 130
octets par ligne : 65
pour un milliard de lignes, en Go : 65
```

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

```python hide
import types
class _Espace(types.ModuleType):                 # permet à `multiprocessing` de retrouver les fonctions définies dans les exemples du livre
    def __getattr__(self, nom):
        try:
            return globals()[nom]
        except KeyError:
            raise AttributeError(nom)
sys.modules["__book__"] = _Espace("__book__")
```

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

```python hide
def amdahl(p, n):
    return 1 / ((1 - p) + p / n)
for n in (2, 4, 10, 100):
    print(f"p = 0,9 ; n = {n:3d} : accélération {amdahl(0.9, n):.2f}")
print("plafond pour p = 0,9 :", round(1 / (1 - 0.9), 1))
for p in (0.5, 0.9, 0.99):
    print(f"p = {p} : plafond {1 / (1 - p):g} ; avec 64 machines : {amdahl(p, 64):.1f}")
```
<!--sortie-->
```text
p = 0,9 ; n =   2 : accélération 1.82
p = 0,9 ; n =   4 : accélération 3.08
p = 0,9 ; n =  10 : accélération 5.26
p = 0,9 ; n = 100 : accélération 9.17
plafond pour p = 0,9 : 10.0
p = 0.5 : plafond 2 ; avec 64 machines : 2.0
p = 0.9 : plafond 10 ; avec 64 machines : 8.8
p = 0.99 : plafond 100 ; avec 64 machines : 39.3
```

![Accélération d'Amdahl en fonction du nombre de machines, pour trois fractions parallélisables : plus la partie séquentielle est grande, plus vite on atteint un plafond.](figures/ch03-amdahl.png)

```python hide
fig_ch03.amdahl()
```
<!--sortie-->
```text
figure : ch03-amdahl.png
```

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

```python hide
pdf.to_csv(os.path.join(TMP, "t.csv"), index=False)
pdf.to_parquet(os.path.join(TMP, "t.parquet"), index=False)
taille_csv, taille_pq = os.path.getsize(os.path.join(TMP, "t.csv")), os.path.getsize(os.path.join(TMP, "t.parquet"))
print("taille du CSV en Mo :", round(taille_csv / 1e6, 1))
print("taille du Parquet en Mo :", round(taille_pq / 1e6, 1))
print("rapport :", round(taille_csv / taille_pq, 1))
t0 = time.perf_counter(); a = pd.read_csv(os.path.join(TMP, "t.csv"), usecols=["montant"])["montant"].sum(); t_csv = time.perf_counter() - t0
t0 = time.perf_counter(); b = pd.read_parquet(os.path.join(TMP, "t.parquet"), columns=["montant"])["montant"].sum(); t_pq = time.perf_counter() - t0
print("même somme :", bool(np.isclose(a, b)))
print("lecture d'une seule colonne au moins 3 fois plus rapide en Parquet :", t_csv / t_pq >= 3)
```
<!--sortie-->
```text
taille du CSV en Mo : 99.5
taille du Parquet en Mo : 28.0
rapport : 3.6
même somme : True
lecture d'une seule colonne au moins 3 fois plus rapide en Parquet : True
```

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
