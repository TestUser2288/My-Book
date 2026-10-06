# Chapitre 3 : Big data et calcul distribué — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 3 du livre. Les **applications** refont, pas à pas et avec le code, les études du livre (MapReduce, loi d'Amdahl, plans Spark, asymétrie, journal de messages, fenêtres et filigrane) ; les **exercices** se travaillent d'abord à la main, puis se vérifient par le calcul. Données : un historique de **un million de transactions** simulées de la boutique (fonction `gros_volume` de `build/donnees4.py`, écrite dans un dossier temporaire) et les 8 000 avis clients (`donnees/avis_clients.csv`). Prérequis : le chapitre 3 du livre ; Python avec pandas, PySpark et DuckDB (et un Java récent, nécessaire à Spark).

## Applications

### Préparation commune

À exécuter une fois. Elle importe les outils, génère le million de transactions dans un dossier temporaire (effacé à la fin du chapitre) et démarre Spark en mode local. Comptez une quinzaine de secondes pour le démarrage de Spark.

```python
import os, re, sys, shutil, tempfile, time, zlib, collections, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession, functions as F, Window

sys.path.insert(0, "build")
import donnees4

TMP = tempfile.mkdtemp(prefix="v4c3cahier_")
DOSSIER = donnees4.gros_volume(1_000_000, 4, dossier=os.path.join(TMP, "gros_volume"))
spark = (SparkSession.builder.master("local[2]").appName("cahier3")
         .config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "4")
         .config("spark.sql.adaptive.enabled", "false")
         .config("spark.sql.warehouse.dir", TMP + "/entrepot").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
ventes = spark.read.parquet(DOSSIER)
print("fichiers :", len(os.listdir(DOSSIER)), "; lignes :", ventes.count(), "; partitions :", ventes.rdd.getNumPartitions())

def plan(df):                                        # plan physique, sans identifiants internes ni chemins
    t = df._jdf.queryExecution().executedPlan().toString()
    t = re.sub(r"#\d+L?", "", t)
    t = re.sub(r", \[plan_id=\d+\]", "", t)
    t = re.sub(r"(Location|Batched|ReadSchema|PushedFilters|PartitionFilters|DataFilters|Format|InputPaths)[^\n]*", "", t)
    return "\n".join(l.rstrip() for l in t.splitlines() if l.strip())
```
<!--sortie-->
```text
fichiers : 4 ; lignes : 1000000 ; partitions : 2
```

### Application 3.1 — Un MapReduce complet sur les avis (section 3.1.4)

**Contexte.** La gérante veut la **note moyenne par catégorie de produit** sur les 8 000 avis. **Objectif.** Écrire les trois phases (map, mélange, reduce) à la main, avec un combineur, et mesurer ce que le combineur épargne au réseau.

**Étape 1 — Découper en partitions et appliquer la fonction map.** Quatre partitions, comme quatre machines ; chaque machine émet des paires (catégorie, (note, 1)).

```python
avis = pd.read_csv("donnees/avis_clients.csv")
lignes = list(zip(avis["categorie"], avis["note"]))
partitions = [lignes[i::4] for i in range(4)]

def map_partition(lignes):
    return [(cat, (note, 1)) for cat, note in lignes]

paires = [map_partition(p) for p in partitions]
print("partitions :", [len(p) for p in paires], "; paires émises au total :", sum(len(p) for p in paires))
```
<!--sortie-->
```text
partitions : [2000, 2000, 2000, 2000] ; paires émises au total : 8000
```

**Étape 2 — Le combineur.** Avant le mélange, chaque machine additionne localement ses paires de même catégorie.

```python
def combiner(paires):
    local = {}
    for cat, (s, n) in paires:
        a, b = local.get(cat, (0, 0))
        local[cat] = (a + s, b + n)
    return list(local.items())

combinees = [combiner(p) for p in paires]
print("paires à mélanger sans combineur :", sum(len(p) for p in paires))
print("paires à mélanger avec combineur :", sum(len(p) for p in combinees))
```
<!--sortie-->
```text
paires à mélanger sans combineur : 8000
paires à mélanger avec combineur : 16
```

**Étape 3 — Le mélange.** On envoie chaque paire à la machine `hachage(catégorie) mod 3` (trois machines *reduce*). On utilise `zlib.crc32`, un hachage **stable** (celui de Python, `hash`, change d'une exécution à l'autre pour les chaînes).

```python
reducteurs = [collections.defaultdict(list) for _ in range(3)]
for p in combinees:
    for cat, valeur in p:
        reducteurs[zlib.crc32(cat.encode()) % 3][cat].append(valeur)
for i, r in enumerate(reducteurs):
    print("machine reduce", i, ":", sorted(r))
```
<!--sortie-->
```text
machine reduce 0 : []
machine reduce 1 : ['B']
machine reduce 2 : ['A', 'C', 'D']
```

**Étape 4 — Reduce, puis vérification.**

```python
moyennes = {}
for r in reducteurs:
    for cat, valeurs in r.items():
        moyennes[cat] = sum(s for s, _ in valeurs) / sum(n for _, n in valeurs)
mr = pd.Series(moyennes).sort_index().round(3)
ref = avis.groupby("categorie")["note"].mean().sort_index().round(3)
print(mr.to_string())
print("identique à pandas :", bool(np.allclose(mr, ref)))
```
<!--sortie-->
```text
A    3.828
B    3.841
C    3.871
D    3.838
identique à pandas : True
```

**À retenir.** Le résultat est **exactement** celui de pandas, et le combineur a réduit le nombre de paires qui voyagent. Il fonctionne parce que la somme et le comptage sont **associatifs**. Pour une **moyenne**, on ne peut pas combiner des moyennes (la moyenne des moyennes est fausse si les morceaux n'ont pas la même taille) : on combine des **couples (somme, effectif)**, puis on divise à la fin.

### Application 3.2 — La loi d'Amdahl sur votre machine (section 3.1.5)

**Contexte.** On veut savoir **quelle part de son calcul est parallélisable**, et prédire le gain de machines supplémentaires. **Objectif.** Mesurer des durées avec 1, 2 et 4 processus, en déduire $p$, puis extrapoler.

**Étape 1 — Mesurer sur votre ordinateur.** Ce bloc n'est pas exécuté ici : les durées dépendent de la machine. Lancez-le chez vous (dans un fichier Python, car `multiprocessing` demande que les fonctions soient définies dans un fichier).

```python
import time
from multiprocessing import Pool

def travail(n):                                   # un calcul qui occupe le processeur
    return sum(i * i % 7 for i in range(n))

if __name__ == "__main__":
    morceaux = [3_000_000] * 8
    for k in (1, 2, 4):
        t0 = time.perf_counter()
        with Pool(k) as pool:
            pool.map(travail, morceaux)
        print(k, "processus :", round(time.perf_counter() - t0, 2), "s")
```

**Étape 2 — Estimer $p$ à partir de durées.** Supposons que vous ayez mesuré 120 s avec 1 processus, 70 s avec 2 et 45 s avec 4. De $S(n)=T(1)/T(n)=1/[(1-p)+p/n]$ on tire $p=\dfrac{1-1/S(n)}{1-1/n}$.

```python
T = {1: 120.0, 2: 70.0, 4: 45.0}
for n in (2, 4):
    S = T[1] / T[n]
    p = (1 - 1 / S) / (1 - 1 / n)
    print(f"n = {n} : accélération {S:.2f} ; fraction parallélisable p = {p:.3f}")
```
<!--sortie-->
```text
n = 2 : accélération 1.71 ; fraction parallélisable p = 0.833
n = 4 : accélération 2.67 ; fraction parallélisable p = 0.833
```

**Étape 3 — Prédire.** Avec le $p$ estimé (il est le même pour $n=2$ et $n=4$, ce qui conforte le modèle), que donneraient 8, 16 et 64 machines ? Et quel est le plafond ?

```python
p = 5 / 6
for n in (8, 16, 64):
    print(f"n = {n:2d} : accélération prédite {1 / ((1 - p) + p / n):.2f}")
print("plafond :", round(1 / (1 - p), 2))
```
<!--sortie-->
```text
n =  8 : accélération prédite 3.69
n = 16 : accélération prédite 4.57
n = 64 : accélération prédite 5.57
plafond : 6.0
```

**À retenir.** Un $p$ **cohérent** pour plusieurs valeurs de $n$ valide le modèle ; s'il diminue quand $n$ augmente, c'est que la **communication** pèse (la loi d'Amdahl est alors optimiste). Ici, passer de 16 à 64 machines ne gagne presque rien : le plafond est de 6.

### Application 3.3 — Lire des plans d'exécution et choisir sa jointure (sections 3.2.4 et 3.2.7)

**Contexte.** Un calcul est lent ; avant de toucher au code, on lit son plan. **Objectif.** Compter les mélanges (`Exchange`) de quatre requêtes et en tirer une règle.

**Étape 1 — Un compteur de mélanges.**

```python
def melanges(df):
    t = plan(df)
    return t.count("Exchange hashpartitioning") + t.count("Exchange rangepartitioning") + t.count("Exchange SinglePartition")

q1 = ventes.filter(F.col("montant") > 10).select("canal", "montant")
q2 = ventes.groupBy("canal").agg(F.sum("montant"))
q3 = ventes.groupBy("canal").agg(F.sum("montant").alias("ca")).orderBy("ca")
q4 = ventes.groupBy("magasin", "canal").agg(F.sum("montant").alias("s")).groupBy("canal").agg(F.sum("s"))
for nom, q in [("filtre + projection", q1), ("groupBy", q2), ("groupBy + orderBy", q3), ("deux groupBy", q4)]:
    print(f"{nom:22s} : {melanges(q)} mélange(s)")
```
<!--sortie-->
```text
filtre + projection    : 0 mélange(s)
groupBy                : 1 mélange(s)
groupBy + orderBy      : 2 mélange(s)
deux groupBy           : 2 mélange(s)
```

**Étape 2 — Les jointures.** On joint les transactions à un catalogue de 500 produits, avec et sans diffusion.

```python
catalogue = spark.createDataFrame(pd.DataFrame({"id_produit": np.arange(1, 501, dtype=np.int32),
                                                "categorie": np.array(["Cuisine", "Maison", "Jardin", "Loisirs"])[np.arange(500) % 4]}))
avec = ventes.join(F.broadcast(catalogue), "id_produit").groupBy("categorie").agg(F.sum("montant"))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
sans = ventes.join(catalogue, "id_produit").groupBy("categorie").agg(F.sum("montant"))
print("avec diffusion :", melanges(avec), "mélange(s) ;", "BroadcastHashJoin" in plan(avec))
print("sans diffusion :", melanges(sans), "mélange(s) ;", "SortMergeJoin" in plan(sans))
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")
```
<!--sortie-->
```text
avec diffusion : 1 mélange(s) ; True
sans diffusion : 3 mélange(s) ; True
```

**Étape 3 — Même résultat ?** Les deux stratégies doivent donner les mêmes totaux.

```python
a = avec.orderBy("categorie").toPandas()
b = sans.orderBy("categorie").toPandas()
print("mêmes totaux par catégorie :", bool(np.allclose(a.iloc[:, 1], b.iloc[:, 1])))
```
<!--sortie-->
```text
mêmes totaux par catégorie : True
```

**À retenir.** Un filtre ou une projection **ne mélange pas** ; un `groupBy` ou un `orderBy` mélange une fois chacun ; une jointure sans diffusion en ajoute deux. La diffusion change le **coût** d'une jointure, jamais son **résultat**.

### Application 3.4 — Asymétrie des clés et salage (section 3.2.9)

**Contexte.** Un revendeur (client numéro 1) concentre 30 % des transactions. **Objectif.** Mesurer le déséquilibre, le corriger par le salage, et vérifier que l'agrégation finale est inchangée.

**Étape 1 — Créer l'asymétrie et la mesurer.**

```python
asym = ventes.withColumn("cle", F.when(F.rand(7) < 0.3, F.lit(1)).otherwise(F.col("id_client")))

def par_partition(df):
    t = df.withColumn("p", F.spark_partition_id()).groupBy("p").count().orderBy("p").toPandas()
    return t["count"].to_numpy()

avant = par_partition(asym.repartition(4, "cle"))
print("lignes par partition :", avant.tolist(), "; plus grosse / moyenne :", round(avant.max() / avant.mean(), 2))
```
<!--sortie-->
```text
lignes par partition : [174612, 475813, 174050, 175525] ; plus grosse / moyenne : 1.9
```

**Étape 2 — Saler.** On ajoute un grain de sel entre 0 et 31 et on répartit par la paire (clé, sel).

```python
sel = F.floor(F.rand(8) * 32).cast("int")
sale = asym.withColumn("sel", sel)
apres = par_partition(sale.repartition(4, "cle", "sel"))
print("lignes par partition :", apres.tolist(), "; plus grosse / moyenne :", round(apres.max() / apres.mean(), 2))
```
<!--sortie-->
```text
lignes par partition : [287706, 259473, 221620, 231201] ; plus grosse / moyenne : 1.15
```

**Étape 3 — Agréger en deux temps.** On somme d'abord par (clé, sel), puis on réagrège par clé. Le résultat doit être identique à l'agrégation directe.

```python
direct = asym.groupBy("cle").agg(F.round(F.sum("montant"), 2).alias("ca"))
en_deux_temps = (sale.groupBy("cle", "sel").agg(F.sum("montant").alias("s"))
                 .groupBy("cle").agg(F.round(F.sum("s"), 2).alias("ca")))
d = direct.orderBy("cle").toPandas()
e = en_deux_temps.orderBy("cle").toPandas()
print("clés :", len(d), "; mêmes totaux :", bool(np.allclose(d["ca"], e["ca"])))
print("part de la clé 1 dans le chiffre d'affaires :", round(float(d.loc[d["cle"] == 1, "ca"].iloc[0] / d["ca"].sum()), 3))
```
<!--sortie-->
```text
clés : 194037 ; mêmes totaux : True
part de la clé 1 dans le chiffre d'affaires : 0.301
```

**À retenir.** Le salage répartit la charge ; l'agrégation en deux temps rend le **même résultat** parce que la somme est associative. Il n'a de sens que pour des opérations qu'on sait **recombiner** ; il est inutile, voire nuisible, si aucune clé n'est dominante.

### Application 3.5 — Un journal de messages et un consommateur idempotent (section 3.3.3)

**Contexte.** Les ventes arrivent dans un journal de type Kafka. **Objectif.** Se répartir les partitions entre deux consommateurs, subir un plantage, et obtenir tout de même des totaux justes.

**Étape 1 — Le journal et les messages.** Chaque vente porte un identifiant unique, et la clé est le magasin.

```python
class Journal:
    def __init__(self, partitions):
        self.partitions = [[] for _ in range(partitions)]
    def publier(self, cle, valeur):
        p = zlib.crc32(str(cle).encode()) % len(self.partitions)
        self.partitions[p].append((cle, valeur))
        return p, len(self.partitions[p]) - 1
    def lire(self, p, decalage, maximum=10_000):
        return self.partitions[p][decalage:decalage + maximum]

journal = Journal(4)
echantillon = ventes.select("id_transaction", "magasin", "montant").orderBy("id_transaction").limit(2000).toPandas()
for ident, magasin, montant in echantillon.itertuples(index=False):
    journal.publier(magasin, (int(ident), float(montant)))
print("messages par partition :", [len(p) for p in journal.partitions])
```
<!--sortie-->
```text
messages par partition : [404, 796, 421, 379]
```

**Étape 2 — Deux consommateurs, un groupe.** Chacun lit les partitions dont le numéro a la parité de son rang. Le consommateur 0 **plante** après avoir traité 30 messages de sa première partition, **avant** de noter son décalage ; au redémarrage, il relit depuis le dernier décalage noté (0).

```python
def consommer(partitions, plante_apres=None):
    """Retourne les messages traités (avec doublons éventuels)."""
    traites = []
    for p in partitions:
        lus = [(cle, ident, montant) for cle, (ident, montant) in journal.lire(p, 0)]
        if plante_apres and p == partitions[0]:
            traites += lus[:plante_apres]            # traités, mais le décalage n'a pas été noté avant le plantage...
        traites += lus                               # ... donc au redémarrage tout est relu depuis le décalage noté (0)
    return traites

c0 = consommer([0, 2], plante_apres=30)
c1 = consommer([1, 3])
tous = c0 + c1
print("messages traités :", len(tous), "; messages publiés :", len(echantillon))
```
<!--sortie-->
```text
messages traités : 2030 ; messages publiés : 2000
```

**Étape 3 — Naïf, puis idempotent.**

```python
attendu = echantillon.groupby("magasin")["montant"].sum().round(2)
naif = pd.DataFrame(tous, columns=["magasin", "id", "montant"]).groupby("magasin")["montant"].sum().round(2)
idem = pd.DataFrame(tous, columns=["magasin", "id", "montant"]).drop_duplicates("id").groupby("magasin")["montant"].sum().round(2)
print("naïf juste :", bool(np.allclose(naif, attendu)), "; idempotent juste :", bool(np.allclose(idem, attendu)))
```
<!--sortie-->
```text
naïf juste : False ; idempotent juste : True
```

**À retenir.** Un plantage entre le traitement et la note du décalage produit des **doublons** (garantie « au moins une fois »). La parade est un identifiant unique et un traitement **idempotent**. Ici, `drop_duplicates("id")` joue ce rôle ; en production, on retient les identifiants déjà vus (dans une base, avec une durée de rétention) ou on écrit avec une clé qui écrase au lieu d'additionner.

### Application 3.6 — Fenêtres et filigrane (sections 3.3.4 et 3.3.5)

**Contexte.** Des évènements arrivent dans le désordre. **Objectif.** Compter par fenêtres fixes, glissantes et de session, puis mesurer **ce que coûte un filigrane trop serré**.

**Étape 1 — Les évènements.** Quatre cents évènements simulés avec une graine fixe : heure de l'évènement en secondes, montant, et **retard d'arrivée** (la plupart arrivent à l'heure, quelques-uns avec un retard allant jusqu'à deux minutes).

```python
rng = np.random.default_rng(3)
n = 400
heure = np.sort(rng.uniform(0, 1800, n))                       # 30 minutes d'activité
retard = np.where(rng.random(n) < 0.1, rng.uniform(30, 120, n), rng.uniform(0, 5, n))
montant = rng.gamma(2.0, 20.0, n).round(2)
ev = pd.DataFrame({"heure": heure, "montant": montant, "arrivee": heure + retard}).sort_values("arrivee").reset_index(drop=True)
print("évènements :", len(ev), "; arrivés après un évènement plus récent :", int((ev["heure"].cummax() > ev["heure"]).sum()))
```
<!--sortie-->
```text
évènements : 400 ; arrivés après un évènement plus récent : 92
```

**Étape 2 — Fenêtres fixes et glissantes (calcul par lots, exact).**

```python
fixes = ev.groupby((ev["heure"] // 300 * 300).astype(int))["montant"].agg(["count", "sum"]).round(1)
print(fixes.to_string())
glissantes = {d: ev[(ev["heure"] >= d) & (ev["heure"] < d + 300)]["montant"].sum() for d in range(0, 1800 - 299, 150)}
print("glissantes (300 s toutes les 150 s) :", {d: round(v) for d, v in glissantes.items()})
```
<!--sortie-->
```text
       count     sum
heure               
0         58  2410.4
300       68  2803.3
600       65  2580.9
900       75  2875.7
1200      73  3316.6
1500      61  2259.0
glissantes (300 s toutes les 150 s) : {0: 2410, 150: 3257, 300: 2803, 450: 2645, 600: 2581, 750: 2399, 900: 2876, 1050: 3571, 1200: 3317, 1350: 2322, 1500: 2259}
```

**Étape 3 — Le filigrane.** On traite les évènements dans l'ordre d'**arrivée** ; une fenêtre fixe de 300 s est fermée quand le filigrane (plus grand temps d'évènement vu, moins $D$) dépasse sa fin.

```python
def avec_filigrane(ev, D, largeur=300):
    plus_recent, ecartes, total = 0.0, 0.0, 0.0
    for h, m in zip(ev["heure"], ev["montant"]):
        if (h // largeur) * largeur + largeur <= plus_recent - D:
            ecartes += m                                       # fenêtre déjà fermée : évènement perdu
        else:
            total += m
        plus_recent = max(plus_recent, h)
    return total, ecartes

for D in (0, 10, 30, 60, 120):
    garde, perdu = avec_filigrane(ev, D)
    print(f"D = {D:3d} s : montant conservé {garde:8.1f} ; perdu {perdu:6.1f} ({perdu / ev['montant'].sum():.1%})")
```
<!--sortie-->
```text
D =   0 s : montant conservé  15827.5 ; perdu  418.4 (2.6%)
D =  10 s : montant conservé  16097.6 ; perdu  148.4 (0.9%)
D =  30 s : montant conservé  16153.4 ; perdu   92.6 (0.6%)
D =  60 s : montant conservé  16190.4 ; perdu   55.5 (0.3%)
D = 120 s : montant conservé  16246.0 ; perdu    0.0 (0.0%)
```

**Étape 4 — Le coût du filigrane en latence.** Une fenêtre de 300 s ne peut être publiée que lorsque le filigrane dépasse sa fin, c'est-à-dire **$D$ secondes après** sa fin au plus tôt.

```python
for D in (0, 30, 120):
    print(f"D = {D:3d} s : le résultat de la fenêtre [0, 300) n'est définitif qu'à l'instant {300 + D} s (temps d'évènement)")
```
<!--sortie-->
```text
D =   0 s : le résultat de la fenêtre [0, 300) n'est définitif qu'à l'instant 300 s (temps d'évènement)
D =  30 s : le résultat de la fenêtre [0, 300) n'est définitif qu'à l'instant 330 s (temps d'évènement)
D = 120 s : le résultat de la fenêtre [0, 300) n'est définitif qu'à l'instant 420 s (temps d'évènement)
```

**À retenir.** Plus le filigrane est large, moins on perd, mais plus on attend : la perte tombe à zéro quand $D$ dépasse le retard maximal (ici 120 s). Le bon $D$ se choisit en regardant la **distribution des retards** observés, pas à l'instinct.

## Exercices

### Exercice 3.1 ⭐ — Quelle mémoire pour quelle table ? (section 3.1.1)

Une ligne de transaction occupe 65 octets en mémoire. (a) Quelle mémoire occuperaient 400 millions de lignes ? Tiennent-elles dans un ordinateur de 16 Go ? (b) On n'a besoin que de la colonne `montant` (8 octets par valeur) : qu'en est-il ?

### Exercice 3.2 ⭐ — Partitionner par hachage (section 3.1.3)

Sept clients ont pour numéros 12, 25, 33, 40, 58, 61, 77. On les répartit sur quatre machines (numérotées 0 à 3) par la règle « numéro modulo 4 ». (a) Quelle machine reçoit chaque client ? (b) Quelle est la machine la plus chargée, et de combien dépasse-t-elle la moyenne ?

### Exercice 3.3 ⭐⭐ — Un combineur à la main (section 3.1.4)

Trois machines lisent les phrases « a b a », « b c » et « a a c » et comptent les mots. (a) Écrivez les paires émises par la phase map. (b) Combien de paires traversent le réseau sans combineur ? avec combineur ? (c) Donnez le résultat final.

### Exercice 3.4 ⭐ — Appliquer la loi d'Amdahl (section 3.1.5)

Un traitement a 80 % de travail parallélisable. Calculez l'accélération avec 4 et 16 machines, puis le plafond.

### Exercice 3.5 ⭐⭐ — Retrouver la fraction parallélisable (section 3.1.5)

Avec 8 machines, un traitement est 4 fois plus rapide. (a) Quelle fraction $p$ est parallélisable ? (b) Quel est le plafond ? (c) Combien de machines faut-il pour une accélération de 5 ?

### Exercice 3.6 ⭐⭐ — Combien de copies ? (section 3.1.7)

Chaque machine tombe en panne, indépendamment, avec la probabilité $q=0{,}02$ sur une période. (a) Probabilité de perdre un bloc copié sur 3 machines ? (b) Combien de copies pour descendre sous $10^{-9}$ ? (c) Sur 1 000 machines, combien tombent en panne en moyenne ?

### Exercice 3.7 ⭐ — Compter les étapes d'un plan (section 3.2.4)

Voici un plan simplifié (de bas en haut, comme dans le livre) :

```text
Sort ca DESC
+- Exchange rangepartitioning(ca)
   +- HashAggregate (final) : somme par magasin
      +- Exchange hashpartitioning(magasin)
         +- HashAggregate (partial)
            +- Filter (montant > 0)
               +- Scan parquet [magasin, montant]
```

(a) Combien de mélanges ? (b) En combien d'étapes (*stages*) Spark découpe-t-il ce calcul ? (c) Quelles opérations sont étroites ?

### Exercice 3.8 ⭐⭐ — Étroit ou large ? (section 3.2.4)

Classez en transformations étroites ou larges : `select`, `filter`, `withColumn`, `groupBy().agg()`, jointure par diffusion (côté gros tableau), jointure par tri et mélange, `distinct`, `orderBy`, `union`, `coalesce`, `repartition`, fonction fenêtre avec `partitionBy`.

### Exercice 3.9 ⭐⭐ — Combien de données voyagent ? (section 3.2.7)

Un tableau de 2 millions de lignes de 65 octets est joint à un catalogue de 500 lignes de 20 octets, sur une grappe de 10 exécuteurs. Estimez la quantité de données transmises (a) par la jointure par diffusion, (b) par la jointure par tri et mélange (on suppose que les deux tableaux sont intégralement mélangés). Quel est le rapport ?

### Exercice 3.10 ⭐⭐ — Dimensionner les partitions (section 3.2.6)

On traite 50 Go sur 5 exécuteurs de 4 cœurs. (a) Combien de partitions de 128 Mo ? (b) Combien par cœur ? (c) Combien de « vagues » de tâches faut-il pour tout traiter ?

### Exercice 3.11 ⭐⭐ — L'asymétrie en chiffres (section 3.2.9)

Un million de lignes sont réparties en 4 partitions par hachage de la clé ; une clé unique représente 30 % des lignes, les autres sont uniformes. (a) Combien de lignes dans la plus grosse partition ? Quel rapport à la moyenne ? (b) Même question avec 100 partitions. (c) Que conclure sur l'effet d'ajouter des machines ?

### Exercice 3.12 ⭐⭐⭐ — Une médiane ne se combine pas (sections 3.1.4 et 3.2)

(a) Deux partitions contiennent $\{1, 2, 3, 100\}$ et $\{4, 5, 6\}$. Comparez la médiane exacte à la **moyenne des médianes** des partitions. (b) Sur les montants du million de transactions, comparez la médiane exacte à la médiane approchée de Spark (`percentile_approx`).

### Exercice 3.13 ⭐⭐ — Petits fichiers (section 3.2.10)

Un DataFrame de 40 partitions est écrit avec `partitionBy("canal")` (3 valeurs). (a) Combien de fichiers au plus ? (b) Même question après `coalesce(4)`. (c) Si l'ouverture d'un fichier coûte 50 ms de frais fixes, quel est le coût fixe total dans chaque cas ?

### Exercice 3.14 ⭐ — Partitions et décalages d'un journal (section 3.3.3)

Six messages de clés 7, 8, 9, 10, 13, 16 sont publiés dans cet ordre dans un sujet à trois partitions, avec la règle « clé modulo 3 ». (a) Pour chaque message, donnez (partition, décalage). (b) Un consommateur lit la partition 1 à partir du décalage 2 : que voit-il ? (c) Quel est le défaut de ce partitionnement ?

### Exercice 3.15 ⭐⭐ — Garanties de livraison (section 3.3.3)

Un consommateur doit traiter dix messages. Il plante **une fois**, pendant le traitement du sixième, puis redémarre. Combien de messages sont traités au total (comptés avec leurs répétitions), et combien manquent, selon que le décalage est noté (a) **avant** le traitement ou (b) **après** ? Quelle garantie chaque ordre réalise-t-il ?

### Exercice 3.16 ⭐⭐ — Fenêtres fixes et glissantes (section 3.3.4)

Des évènements surviennent aux secondes 5, 12, 25, 31, 44 et 58. (a) Comptez-les par fenêtres fixes de 20 s. (b) Comptez-les par fenêtres glissantes de 20 s avancées de 10 s (à partir de la fenêtre $[-10, 10)$). (c) Vérifiez que le nombre total d'appartenances est le nombre d'évènements multiplié par 2.

### Exercice 3.17 ⭐⭐ — Le filigrane à la main (section 3.3.5)

Des évènements arrivent dans l'ordre suivant, repérés par leur temps d'évènement (en secondes) : 10, 50, 90, 30, 130, 70, 20. Les fenêtres fixes durent 60 s ; le retard toléré est $D=40$ s. (a) Quels évènements sont écartés ? (b) Quelle valeur minimale de $D$ aurait conservé tous les évènements ?

### Exercice 3.18 ⭐⭐⭐ — Fenêtres de session (section 3.3.4)

Les évènements d'un internaute surviennent aux secondes 4, 10, 15, 40, 44 et 90. Une session se ferme après un silence d'au moins 20 s. (a) Combien de sessions, et lesquelles ? (b) Quelle est la durée de chacune (du premier au dernier évènement) ? (c) Écrivez une fonction qui le calcule pour une liste d'heures quelconque.

## Corrigés

### Corrigé 3.1

(a) $400\times10^6\times65=26\times10^9$ octets, soit **26 Go** : **non**, cela ne tient pas dans 16 Go. (b) Avec la seule colonne `montant` : $400\times10^6\times8=3{,}2$ Go, qui tiennent sans difficulté. **Leçon** : lire seulement les colonnes utiles (stockage en colonnes, section 3.1.9) peut suffire à éviter de distribuer.

```python
print("toutes les colonnes :", 400e6 * 65 / 1e9, "Go ; colonne montant seule :", 400e6 * 8 / 1e9, "Go")
```
<!--sortie-->
```text
toutes les colonnes : 26.0 Go ; colonne montant seule : 3.2 Go
```

### Corrigé 3.2

(a) $12\bmod4=0$, $25\bmod4=1$, $33\bmod4=1$, $40\bmod4=0$, $58\bmod4=2$, $61\bmod4=1$, $77\bmod4=1$. (b) La machine 1 reçoit les clients 25, 33, 61 et 77, soit **4 sur 7**. La moyenne est $7/4=1{,}75$ ; le rapport est $4/1{,}75\approx2{,}29$ : la machine 1 a **2,3 fois la charge moyenne**. Avec si peu de clés, le hasard suffit à déséquilibrer.

```python
clients = [12, 25, 33, 40, 58, 61, 77]
charge = collections.Counter(c % 4 for c in clients)
print(dict(sorted(charge.items())), "; plus grosse / moyenne :", round(max(charge.values()) / (len(clients) / 4), 2))
```
<!--sortie-->
```text
{0: 2, 1: 4, 2: 1} ; plus grosse / moyenne : 2.29
```

### Corrigé 3.3

(a) Map : machine 1 : (a,1) (b,1) (a,1) ; machine 2 : (b,1) (c,1) ; machine 3 : (a,1) (a,1) (c,1). (b) **Sans combineur**, les 8 paires traversent le réseau. **Avec combineur** : machine 1 envoie (a,2) (b,1) ; machine 2 : (b,1) (c,1) ; machine 3 : (a,2) (c,1) : **6 paires**, soit 25 % de moins. (c) Reduce : $a=2+2=4$, $b=1+1=2$, $c=1+1=2$ ; total 8 mots, comme les 8 mots d'entrée.

```python
entree = ["a b a", "b c", "a a c"]
partiel = [collections.Counter(p.split()) for p in entree]
print("paires sans combineur :", sum(len(p.split()) for p in entree), "; avec combineur :", sum(len(c) for c in partiel))
print("résultat :", dict(sum(partiel, collections.Counter())))
```
<!--sortie-->
```text
paires sans combineur : 8 ; avec combineur : 6
résultat : {'a': 4, 'b': 2, 'c': 2}
```

### Corrigé 3.4

$S(4)=\dfrac{1}{0{,}2+0{,}8/4}=\dfrac{1}{0{,}4}=2{,}5$ ; $S(16)=\dfrac{1}{0{,}2+0{,}05}=4$ ; plafond $=\dfrac1{0{,}2}=5$. Quadrupler les machines (de 4 à 16) ne fait gagner que 60 %.

```python
amdahl = lambda p, n: 1 / ((1 - p) + p / n)
print(round(amdahl(0.8, 4), 2), round(amdahl(0.8, 16), 2), round(1 / (1 - 0.8), 2))
```
<!--sortie-->
```text
2.5 4.0 5.0
```

### Corrigé 3.5

(a) $\dfrac14=(1-p)+\dfrac p8=1-\dfrac{7p}{8}$, donc $p=\dfrac{8}{7}\times\dfrac34=\dfrac67\approx0{,}857$. (b) Plafond $=\dfrac1{1-p}=7$. (c) Pour $S=5$ : $\dfrac15=\dfrac17+\dfrac{6/7}{n}$, donc $\dfrac{6/7}{n}=\dfrac15-\dfrac17=\dfrac2{35}$ et $n=\dfrac67\times\dfrac{35}{2}=15$. **Quinze machines** pour passer de 4 à 5 : le rendement est faible.

```python
p = 6 / 7
print(round(p, 3), round(1 / (1 - p), 2), round(amdahl(p, 8), 2), round(amdahl(p, 15), 2))
```
<!--sortie-->
```text
0.857 7.0 4.0 5.0
```

### Corrigé 3.6

(a) $q^3=0{,}02^3=8\times10^{-6}$. (b) On veut $0{,}02^k\le10^{-9}$, soit $k\ge\dfrac{9}{-\log_{10}0{,}02}=\dfrac{9}{1{,}699}\approx5{,}3$ : **6 copies**. (c) $1000\times0{,}02=20$ machines en panne en moyenne : à cette échelle, **les pannes sont la norme**. Le calcul suppose des pannes **indépendantes** : une coupure d'alimentation d'une baie de serveurs touche plusieurs copies à la fois, ce pourquoi on place les copies dans des endroits différents.

```python
print(f"{0.02 ** 3:.1e}", int(np.ceil(9 / -np.log10(0.02))), 1000 * 0.02)
```
<!--sortie-->
```text
8.0e-06 6 20.0
```

### Corrigé 3.7

(a) **Deux** mélanges : `Exchange hashpartitioning(magasin)` pour l'agrégation, `Exchange rangepartitioning(ca)` pour le tri. (b) **Trois étapes** : on coupe à chaque `Exchange` (lecture–filtre–agrégation partielle ; agrégation finale ; tri). (c) Sont étroits : le `Scan`, le `Filter`, l'agrégation **partielle** (qui travaille sur place) ; l'agrégation finale et le tri ne démarrent qu'une fois le mélange terminé.

### Corrigé 3.8

**Étroites** : `select`, `filter`, `withColumn`, jointure par diffusion (côté gros tableau : il ne bouge pas), `union`, `coalesce` (fusionne des partitions voisines sans mélange). **Larges** : `groupBy().agg()`, jointure par tri et mélange, `distinct`, `orderBy`, `repartition`, fonction fenêtre avec `partitionBy`.

### Corrigé 3.9

(a) **Diffusion** : le catalogue pèse $500\times20=10$ ko ; il est envoyé à chacun des 10 exécuteurs : $10\times10=100$ ko. (b) **Tri et mélange** : tout le gros tableau est mélangé, $2\times10^6\times65=130$ Mo, plus 10 ko. (c) Le rapport est $130\,\text{Mo}/100\,\text{ko}=1\,300$ : la diffusion transmet **mille trois cents fois moins** de données.

```python
print("diffusion :", 500 * 20 * 10, "octets ; mélange :", 2_000_000 * 65 + 500 * 20, "octets ; rapport :", round((2_000_000 * 65 + 500 * 20) / (500 * 20 * 10)))
```
<!--sortie-->
```text
diffusion : 100000 octets ; mélange : 130010000 octets ; rapport : 1300
```

### Corrigé 3.10

(a) $50\,\text{Go}=50\,000\,\text{Mo}$ ; $50\,000/128\approx390{,}6$, donc **391 partitions**. (b) La grappe a $5\times4=20$ cœurs : $391/20\approx19{,}6$ partitions par cœur. (c) Chaque cœur traite une tâche à la fois : il faut $\lceil391/20\rceil=\mathbf{20}$ vagues. Plus de quatre partitions par cœur n'est pas un défaut : c'est la **taille** des morceaux (assez petits pour tenir en mémoire, assez gros pour que l'organisation reste négligeable) qui décide.

```python
n = int(np.ceil(50_000 / 128)); print(n, round(n / 20, 1), int(np.ceil(n / 20)))
```
<!--sortie-->
```text
391 19.6 20
```

### Corrigé 3.11

(a) La clé dominante pèse $300\,000$ lignes ; les $700\,000$ autres se répartissent uniformément : $700\,000/4=175\,000$ par partition. La plus grosse a $300\,000+175\,000=475\,000$ lignes ; la moyenne est $250\,000$ ; le rapport est **1,9**. (b) Avec 100 partitions : $300\,000+7\,000=307\,000$ pour une moyenne de $10\,000$ : le rapport est **30,7**. (c) **Ajouter des machines aggrave le déséquilibre** : la partition de la clé dominante ne rétrécit pas (elle contient au moins 300 000 lignes), alors que la moyenne diminue. La durée du calcul reste celle de cette partition : c'est le plafond d'Amdahl dans sa version « une tâche surchargée », et la raison d'être du salage.

```python
for k in (4, 100):
    biggest = 300_000 + 700_000 / k
    print(k, "partitions :", int(biggest), "lignes ; rapport", round(biggest / (1_000_000 / k), 1))
```
<!--sortie-->
```text
4 partitions : 475000 lignes ; rapport 1.9
100 partitions : 307000 lignes ; rapport 30.7
```

### Corrigé 3.12

(a) La médiane exacte de $\{1,2,3,4,5,6,100\}$ est **4**. Les médianes des partitions valent $2{,}5$ (de $\{1,2,3,100\}$) et $5$ ; leur moyenne est $3{,}75$ : **fausse**, parce que la médiane n'est **pas associative** : on ne peut pas la reconstituer à partir de médianes partielles. (b) Il faut un autre algorithme : on résume chaque partition par un **croquis** (histogramme, quantiles approchés), puis on combine les résumés. C'est ce que fait `percentile_approx`, avec une erreur contrôlée.

```python
a, b = [1, 2, 3, 100], [4, 5, 6]
print("exacte :", np.median(a + b), "; moyenne des médianes :", (np.median(a) + np.median(b)) / 2)
exacte = float(ventes.toPandas()["montant"].median())
approx = ventes.agg(F.percentile_approx("montant", 0.5, 10000)).first()[0]
print("médiane exacte :", round(exacte, 2), "; approchée :", round(approx, 2), "; écart relatif < 1 % :", abs(approx - exacte) / exacte < 0.01)
```
<!--sortie-->
```text
exacte : 4.0 ; moyenne des médianes : 3.75
médiane exacte : 29.98 ; approchée : 29.99 ; écart relatif < 1 % : True
```

### Corrigé 3.13

(a) Chacune des 40 partitions peut contenir des lignes des trois canaux : **jusqu'à $40\times3=120$ fichiers**. (b) Après `coalesce(4)` : **jusqu'à $4\times3=12$ fichiers**. (c) $120\times50\,\text{ms}=6\,\text{s}$ contre $12\times50\,\text{ms}=0{,}6\,\text{s}$ : **dix fois moins** de frais fixes, pour exactement les mêmes données. À 100 000 fichiers, ces frais deviennent des heures.

### Corrigé 3.14

(a) $7\bmod3=1$, $8\bmod3=2$, $9\bmod3=0$, $10\bmod3=1$, $13\bmod3=1$, $16\bmod3=1$. Dans l'ordre d'arrivée : clé 7 → (1, 0) ; clé 8 → (2, 0) ; clé 9 → (0, 0) ; clé 10 → (1, 1) ; clé 13 → (1, 2) ; clé 16 → (1, 3). (b) À partir du décalage 2 de la partition 1, il lit les clés **13 et 16**. (c) La partition 1 reçoit **4 messages sur 6** : déséquilibrée, comme dans l'exercice 3.2. Un hachage sur **peu de valeurs** de clé équilibre mal ; un bon sujet a **beaucoup plus de clés que de partitions**.

```python
cles = [7, 8, 9, 10, 13, 16]
compte = collections.Counter()
for c in cles:
    p = c % 3; print(c, "→", (p, compte[p])); compte[p] += 1
```
<!--sortie-->
```text
7 → (1, 0)
8 → (2, 0)
9 → (0, 0)
10 → (1, 1)
13 → (1, 2)
16 → (1, 3)
```

### Corrigé 3.15

(a) **Décalage noté avant** : au redémarrage, le sixième message est considéré comme lu, mais n'a pas été terminé. Il est **perdu** : 9 messages traités, 1 manquant. C'est la garantie **au plus une fois**. (b) **Décalage noté après** : le sixième message, traité mais non acquitté, est **relu** : il a été traité deux fois, soit 11 traitements pour 10 messages, 0 manquant, 1 doublon. C'est la garantie **au moins une fois**. Dans les deux cas, éviter le problème exige un traitement **idempotent** (identifiants) ou une transaction qui regroupe le traitement et la note du décalage (**exactement une fois**).

### Corrigé 3.16

(a) $[0,20)$ : 5, 12 → **2** ; $[20,40)$ : 25, 31 → **2** ; $[40,60)$ : 44, 58 → **2**. (b) $[-10,10)$ : 5 → **1** ; $[0,20)$ : 5, 12 → **2** ; $[10,30)$ : 12, 25 → **2** ; $[20,40)$ : 25, 31 → **2** ; $[30,50)$ : 31, 44 → **2** ; $[40,60)$ : 44, 58 → **2** ; $[50,70)$ : 58 → **1**. (c) $1+2+2+2+2+2+1=12=6\times2$ : chaque évènement appartient à **deux** fenêtres glissantes (durée 20 s, pas de 10 s : durée divisée par pas).

```python
ev = [5, 12, 25, 31, 44, 58]
fenetres = {d: [t for t in ev if d <= t < d + 20] for d in range(-10, 60, 10)}
print({d: len(v) for d, v in fenetres.items()}, "; appartenances :", sum(len(v) for v in fenetres.values()))
```
<!--sortie-->
```text
{-10: 1, 0: 2, 10: 2, 20: 2, 30: 2, 40: 2, 50: 1} ; appartenances : 12
```

### Corrigé 3.17

À chaque arrivée, on compare la **fin de la fenêtre** de l'évènement au filigrane, calculé avec le plus grand temps vu **avant** cet évènement ($D=40$).

| Arrivée | Plus grand temps vu avant | Filigrane | Fenêtre (fin) | Sort |
|---|---|---|---|---|
| 10 | 0 | −40 | $[0,60)$ (60) | conservé |
| 50 | 10 | −30 | $[0,60)$ (60) | conservé |
| 90 | 50 | 10 | $[60,120)$ (120) | conservé |
| 30 | 90 | 50 | $[0,60)$ (60) | conservé : $60>50$ |
| 130 | 90 | 50 | $[120,180)$ (180) | conservé |
| 70 | 130 | 90 | $[60,120)$ (120) | conservé : $120>90$ |
| 20 | 130 | 90 | $[0,60)$ (60) | **écarté** : $60\le90$ |

(a) **Seul l'évènement 20** est écarté. (b) Il aurait fallu que, à l'arrivée de 20, le filigrane soit inférieur à 60 : $130-D<60$, soit **$D>70$** (par exemple $D=71$ s).

```python
def ecartes(ordre, D, largeur=60):
    plus, out = 0, []
    for h in ordre:
        if h // largeur * largeur + largeur <= plus - D:
            out.append(h)
        plus = max(plus, h)
    return out

ordre = [10, 50, 90, 30, 130, 70, 20]
print("D = 40 :", ecartes(ordre, 40), "; D = 70 :", ecartes(ordre, 70), "; D = 71 :", ecartes(ordre, 71))
```
<!--sortie-->
```text
D = 40 : [20] ; D = 70 : [20] ; D = 71 : []
```

### Corrigé 3.18

(a) Les silences : $10-4=6$, $15-10=5$, $40-15=25$ ($\ge20$ : **nouvelle session**), $44-40=4$, $90-44=46$ (**nouvelle session**). Trois sessions : $\{4,10,15\}$, $\{40,44\}$ et $\{90\}$. (b) Durées (premier au dernier évènement) : $15-4=11$ s, $44-40=4$ s, et $0$ s pour la session d'un seul évènement. (c) Le code ci-dessous trie les heures puis coupe à chaque silence d'au moins `silence` secondes.

```python
def sessions(heures, silence=20):
    out = []
    for h in sorted(heures):
        if out and h - out[-1][-1] < silence:
            out[-1].append(h)
        else:
            out.append([h])
    return out

s = sessions([4, 10, 15, 40, 44, 90])
print(s, "; durées :", [x[-1] - x[0] for x in s])
```
<!--sortie-->
```text
[[4, 10, 15], [40, 44], [90]] ; durées : [11, 4, 0]
```

### Nettoyage

```python
spark.stop()
shutil.rmtree(TMP, ignore_errors=True)
print("dossier temporaire supprimé :", not os.path.exists(TMP))
```
<!--sortie-->
```text
dossier temporaire supprimé : True
```
