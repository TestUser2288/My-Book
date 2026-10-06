## 3.2 Spark et PySpark

**Apache Spark** est un moteur de calcul distribué qui est devenu, depuis les années 2010, l'outil de référence pour traiter de gros tableaux de données. Il reprend l'idée de MapReduce (découper, calculer localement, mélanger, combiner) mais en **gardant les données en mémoire** entre deux étapes et en offrant une interface très proche de pandas et de SQL. **PySpark** est son interface Python.

### 3.2.1 L'architecture : un pilote et des exécuteurs

Un programme Spark se compose de :

- un **pilote** (*driver*) : le processus qui exécute votre script Python. Il **construit le plan** du calcul, le découpe en tâches et suit leur avancement ;
- des **exécuteurs** (*executors*) : des processus répartis sur les machines de la grappe, qui exécutent les **tâches** et conservent les partitions en mémoire ;
- un **gestionnaire de ressources**, qui attribue les machines (YARN, Kubernetes, ou le gestionnaire intégré de Spark).

![Architecture de Spark : le pilote demande des exécuteurs au gestionnaire de ressources, puis leur envoie des tâches et récupère les résultats.](figures/ch03-spark-architecture.png)

```python hide
fig_ch03.spark_architecture()
fig_ch03.mapreduce()
fig_ch03.ligne_colonne()
```
<!--sortie-->
```text
figure : ch03-spark-architecture.png
figure : ch03-mapreduce.png
figure : ch03-ligne-colonne.png
```

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

```python hide
def plan(df):
    """Plan physique de Spark, sans les identifiants internes ni les chemins de fichiers (reproductible)."""
    texte = df._jdf.queryExecution().executedPlan().toString()
    texte = re.sub(r"#\d+L?", "", texte)
    texte = re.sub(r", \[plan_id=\d+\]", "", texte)
    texte = re.sub(r"(Location|Batched|ReadSchema|PushedFilters|PartitionFilters|DataFilters|Format|InputPaths)[^\n]*", "", texte)
    return "\n".join(l.rstrip() for l in texte.splitlines() if l.strip())
```

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

```python hide
asym = ventes.withColumn("cle", F.when(F.rand(7) < 0.3, F.lit(1)).otherwise(F.col("id_client")))
def lignes_par_partition(df):
    t = df.withColumn("p", F.spark_partition_id()).groupBy("p").count().orderBy("p").toPandas()
    return t["count"].to_numpy()
avant = lignes_par_partition(asym.repartition(4, "cle"))
print("lignes par partition, clé brute :", avant.tolist())
print("rapport plus grosse / moyenne :", round(avant.max() / avant.mean(), 2))
```
<!--sortie-->
```text
lignes par partition, clé brute : [351057, 950627, 348689, 349627]
rapport plus grosse / moyenne : 1.9
```

Une partition reçoit **47,5 % des lignes** (30 % pour le revendeur, plus sa part des autres clients) au lieu de 25 % : elle contient environ **1,9 fois la moyenne**, et c'est elle qui fixe la durée du calcul, pendant que les trois autres terminent et attendent. Ajouter des machines n'y changerait rien : **la clé 1 reste sur une seule**.

La parade s'appelle le **salage** (*salting*). On **ajoute un grain de sel aléatoire** à la clé, qui la **découpe** en plusieurs sous-clés (« 1-0 », « 1-1 », …, « 1-31 »), réparties sur des partitions différentes. On agrège d'abord sur la clé salée (chaque morceau a une taille normale), puis on **réagrège** les résultats partiels sur la vraie clé, ce qui est peu coûteux : il n'y a plus que 32 lignes pour la clé 1.

```python
sel = F.floor(F.rand(8) * 32).cast("int")                         # un grain de sel entre 0 et 31
sale = asym.withColumn("sel", sel).repartition(4, "cle", "sel")   # la clé 1 est maintenant répartie
```

```python hide
apres = lignes_par_partition(sale)
print("lignes par partition, clé salée :", apres.tolist())
print("rapport plus grosse / moyenne :", round(apres.max() / apres.mean(), 2))
fig_ch03.asymetrie(avant, apres, avant.max() / avant.mean(), apres.max() / apres.mean())
```
<!--sortie-->
```text
lignes par partition, clé salée : [575589, 518147, 443853, 462411]
rapport plus grosse / moyenne : 1.15
figure : ch03-asymetrie.png
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

```python hide
def nb_fichiers(dossier):
    return sum(1 for _, _, fs in os.walk(dossier) for f in fs if f.endswith(".parquet"))
ventes.repartition(40).write.mode("overwrite").parquet(TMP + "/petits")
ventes.repartition(40).coalesce(2).write.mode("overwrite").parquet(TMP + "/gros")
print("40 partitions écrites : fichiers =", nb_fichiers(TMP + "/petits"))
print("après coalesce(2) : fichiers =", nb_fichiers(TMP + "/gros"))
```
<!--sortie-->
```text
40 partitions écrites : fichiers = 40
après coalesce(2) : fichiers = 2
```

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

```python hide
def duree(f, fois=3):
    meilleur = 1e9
    for _ in range(fois):
        t0 = time.perf_counter(); f(); meilleur = min(meilleur, time.perf_counter() - t0)
    return meilleur
t_spark = duree(lambda: ventes.groupBy("magasin").agg(F.sum("montant")).collect())
t_duck = duree(lambda: duckdb.sql(f"SELECT magasin, SUM(montant) FROM read_parquet('{DOSSIER}/*.parquet') GROUP BY magasin").df())
t_pandas = duree(lambda: pd.concat([pd.read_parquet(os.path.join(DOSSIER, f)) for f in sorted(os.listdir(DOSSIER))]).groupby("magasin")["montant"].sum())
print("Spark plus lent que DuckDB :", t_spark > t_duck, "; Spark et pandas à moins d'un facteur 10 :", max(t_spark, t_pandas) / min(t_spark, t_pandas) < 10)
```
<!--sortie-->
```text
Spark plus lent que DuckDB : True ; Spark et pandas à moins d'un facteur 10 : True
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
