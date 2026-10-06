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

```python hide
fig_ch03.fenetres()
```
<!--sortie-->
```text
figure : ch03-fenetres.png
```

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

```python hide
flux = TMP + "/flux"
os.makedirs(flux)
debut = pd.Timestamp("2025-06-01 10:00:00")
for i, lot in enumerate(lots):
    pd.DataFrame({"t": [(debut + pd.Timedelta(seconds=s)).strftime("%Y-%m-%d %H:%M:%S") for s, _ in lot],
                  "montant": [float(m) for _, m in lot]}).to_json(f"{flux}/lot{i}.json", orient="records", lines=True)
print("paquets déposés :", sorted(os.listdir(flux)))
```
<!--sortie-->
```text
paquets déposés : ['lot0.json', 'lot1.json', 'lot2.json', 'lot3.json']
```

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

```python hide
requete.stop()
```

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
