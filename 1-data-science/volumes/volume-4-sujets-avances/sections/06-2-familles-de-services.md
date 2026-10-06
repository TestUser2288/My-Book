## 6.2 Les grandes familles de services

Un catalogue de cloud public compte des centaines de services, mais ils se rangent en **six familles**. Les connaître suffit à lire n'importe quelle offre : les noms changent d'un fournisseur à l'autre, pas les fonctions. Pour chaque famille, nous regardons ce qu'elle fait, ce qu'elle coûte à son utilisateur en **réflexion** (et pas seulement en euros), et le lien avec ce qui a été étudié dans le volume.

### 6.2.1 Le calcul : machines virtuelles, conteneurs, fonctions

Trois façons de faire tourner du code, de la plus proche du matériel à la plus abstraite :

- **Machine virtuelle** : un ordinateur complet (système d'exploitation compris) que l'on loue à l'heure ou à la seconde. On le configure comme on veut ; on en est responsable (mises à jour, sécurité du système). Le démarrage d'une machine neuve prend de l'ordre de **minutes**.
- **Conteneur** : le code et ses dépendances, empaquetés dans une image standard (chapitre 4, section 4.6) qui s'exécute sur une machine partagée. Un service de conteneurs gérés place, redémarre et met à l'échelle les conteneurs. Le démarrage se compte en **secondes**.
- **Fonction à la demande** (*serverless*) : on fournit une fonction, le fournisseur l'exécute **quand une requête arrive** et la facture à l'exécution. Pas de serveur à gérer, et une facture nulle quand il n'y a pas de trafic. Revers : le **démarrage à froid** (la première requête après un temps d'inactivité attend le chargement de la fonction), des limites de durée et de mémoire, et une forte dépendance au fournisseur.

Ces ordres de grandeur sont **à vérifier** chez chaque fournisseur. Ce qui compte pour la conception est leur **conséquence** : *plus l'unité de calcul démarre vite, plus elle peut suivre la demande de près, donc moins on paie de capacité inutilisée*. Mesurons-le par une simulation.

**L'expérience.** Une file de requêtes d'un service de la boutique, minute par minute pendant une journée. La demande suit un cycle doux avec un pic à midi, puis une **pointe brutale** à 19 h (une vente flash annoncée sur les réseaux sociaux : en une dizaine de minutes, le trafic est multiplié par 8). Chaque instance traite 60 requêtes par minute. Quatre politiques de capacité :

1. **statique au pic** : on prévoit le nombre d'instances nécessaire à la pointe, toute la journée ;
2. **statique à la moyenne** (+ 30 % de marge) ;
3. **autoscaling de machines virtuelles** : l'orchestrateur ajoute des instances quand la charge dépasse 60 % de la capacité, deux minutes de suite, et elles mettent **5 minutes** à démarrer ;
4. **autoscaling de conteneurs** : même règle, mais **1 minute** de démarrage et décision immédiate.

On mesure le nombre d'instances-heures consommées (donc le coût) et l'**attente** : une requête qui arrive quand la file est longue attend, en minutes, la taille de la file divisée par la capacité.

```python hide
rng = np.random.default_rng(6002)
T = 1440; minutes = np.arange(T); mu = 60                      # minutes d'une journée ; requêtes traitées par instance et par minute
lam = 120 + 380 * np.exp(-0.5 * ((minutes - 12 * 60) / 90) ** 2) + 1500 * np.exp(-0.5 * ((minutes - 19 * 60) / 5) ** 2)
arr = rng.poisson(lam)                                         # arrivées par minute

def simule(mini, demarrage, delai, cible=0.6, maxi=25):
    inst, pend, backlog, cons, ih = mini, [], 0, 0, 0.0
    insts, atts = [], []
    for k in range(T):
        pend = [(d - 1, n) for d, n in pend]
        inst += sum(n for d, n in pend if d <= 0)
        pend = [(d, n) for d, n in pend if d > 0]
        cap = inst * mu
        backlog = max(0, backlog + arr[k] - cap)
        atts.append(backlog / max(cap, 1)); insts.append(inst); ih += inst / 60
        u = arr[k] / max(cap, 1)
        cons = cons + 1 if (u > cible or backlog > 0) else 0
        if cons >= delai:
            besoin = min(maxi, int(np.ceil((arr[k] + backlog / 2) / (mu * cible))))
            ajout = max(0, besoin - inst - sum(n for d, n in pend))
            if ajout > 0:
                pend.append((demarrage, ajout)); cons = 0
        elif u < cible * 0.5 and inst > mini and backlog == 0:
            inst -= 1
    return np.array(insts), np.array(atts), ih

pic_inst = int(np.ceil(arr.max() / mu)) + 1
politiques = {
    "statique au pic": dict(mini=pic_inst, demarrage=99, delai=99999, maxi=pic_inst),
    "statique à la moyenne + 30 %": dict(mini=int(np.ceil(arr.mean() / mu * 1.3)), demarrage=99, delai=99999, maxi=25),
    "autoscaling de VM (démarrage 5 min)": dict(mini=3, demarrage=5, delai=2, maxi=25),
    "autoscaling de conteneurs (1 min)": dict(mini=3, demarrage=1, delai=1, maxi=25),
}
sim = {nom: simule(**args) for nom, args in politiques.items()}
lignes = []
for nom, (insts, atts, ih) in sim.items():
    lignes.append({"politique": nom, "instances-heures": ih, "coût du jour (€)": ih * P["vm_od"], "minutes avec attente > 1 min (%)": 100 * (atts > 1).mean(), "attente max (min)": atts.max()})
res_scal = pd.DataFrame(lignes)
print(f"arrivées par minute : moyenne {arr.mean():.0f}, maximum {arr.max()} ; instances nécessaires au pic : {pic_inst}")
```
<!--sortie-->
```text
arrivées par minute : moyenne 192, maximum 1663 ; instances nécessaires au pic : 29
```

```python hide-code
print(res_scal.round(1).to_string(index=False))
```
<!--sortie-->
```text
                          politique  instances-heures  coût du jour (€)  minutes avec attente > 1 min (%)  attente max (min)
                    statique au pic             696.0             278.4                               0.0                0.0
       statique à la moyenne + 30 %             120.0              48.0                              35.3               91.5
autoscaling de VM (démarrage 5 min)             161.9              64.8                               1.0                3.5
  autoscaling de conteneurs (1 min)             168.4              67.3                               0.0                0.3
```

La lecture est nette :

- **Statique au pic** : aucune attente, mais le coût le plus élevé, car on paie toute la journée une capacité qui ne sert que quelques minutes.
- **Statique à la moyenne** : le coût le plus bas… et l'attente la plus catastrophique : plus du tiers de la journée avec des files de plus d'une minute, et une attente maximale de plus d'une heure. C'est la panne ordinaire de qui sous-dimensionne.
- **Autoscaling de VM** : le coût est environ le quart de celui du statique au pic, mais la pointe est mal absorbée pendant les 5 minutes de démarrage : environ 1 % des minutes de la journée voient une attente de plus d'une minute, avec un maximum d'un peu plus de trois minutes. Pour un service qui facture à la seconde, c'est un moment critique.
- **Autoscaling de conteneurs** : à coût comparable, la pointe est absorbée sans attente notable. C'est l'effet direct de la rapidité de démarrage.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.5, 1]})
fen = slice(18 * 60 + 30, 19 * 60 + 45); x = minutes[fen] - 19 * 60
ax[0].fill_between(x, 0, arr[fen] / mu, color="#cde2fb", label="instances nécessaires pour la demande")
ax[0].step(x, sim["autoscaling de VM (démarrage 5 min)"][0][fen], color=ORANGE, lw=1.8, where="post", label="autoscaling de VM (démarrage 5 min)")
ax[0].step(x, sim["autoscaling de conteneurs (1 min)"][0][fen], color=AQUA, lw=1.8, where="post", label="autoscaling de conteneurs (démarrage 1 min)")
ax[0].set_xlabel("minutes depuis 19 h"); ax[0].set_ylabel("instances"); ax[0].set_title("La pointe de 19 h : qui suit la demande ?"); ax[0].legend(frameon=False, fontsize=8, loc="upper right"); ax[0].set_ylim(0, 38)
noms = ["statique\nau pic", "statique\nmoyenne", "autoscaling\nVM", "autoscaling\nconteneurs"]
vals = [res_scal["coût du jour (€)"].iloc[i] for i in range(4)]
b = ax[1].bar(noms, vals, color=[ORANGE, ROUGE, VIOLET, AQUA], width=0.6)
for r, v in zip(b, vals):
    ax[1].text(r.get_x() + r.get_width() / 2, v + 5, f"{v:.0f} €", ha="center", fontsize=8.5)
ax[1].set_ylabel("coût de la journée (€, prix inventés)"); ax[1].set_ylim(0, max(vals) * 1.15); ax[1].set_title("Coût de la journée"); ax[1].grid(axis="x", visible=False)
plt.tight_layout(); style.save(fig, "ch06-autoscaling.png")
```
<!--sortie-->
```text
figure : ch06-autoscaling.png
```

![À gauche : pendant la pointe de 19 h, le nombre d'instances nécessaires (zone bleue) et celui des deux autoscalings (machines virtuelles à démarrage lent en orange, conteneurs à démarrage rapide en vert). À droite : coût de la journée pour les quatre politiques, avec des prix inventés.](figures/ch06-autoscaling.png)

> 💡 **Le serverless pousse la logique à l'extrême** : un démarrage d'une fraction de seconde (hors démarrage à froid) et une facturation à la requête permettent de **ne rien payer quand rien ne se passe**. La section 6.3.1 calcule à partir de quel volume de requêtes une machine louée devient moins chère qu'une fonction.

> ⚠️ **Limites de ce modèle.** Une vraie file de requêtes a des exigences de latence par requête (et pas seulement une attente moyenne), l'autoscaling réagit à des mesures bruitées et retardées, et la démultiplication des instances suppose que le service est **sans état** (il ne garde rien en mémoire d'une requête à l'autre : voir 4.2). Le modèle montre un **sens**, pas des valeurs.

### 6.2.2 Le stockage : objet, bloc, fichier, et ses paliers

Trois formes de stockage, pour trois usages :

| Forme | Principe | Usage typique | Remarque |
|---|---|---|---|
| **Objet** | des fichiers (« objets ») rangés dans des conteneurs plats (« seaux »), accessibles par une adresse web | données brutes, fichiers Parquet, sauvegardes, images, modèles | très bon marché, extensible presque sans limite, accès par réseau |
| **Bloc** | un disque virtuel attaché à une machine | système d'exploitation, bases de données | rapide, mais lié à une machine |
| **Fichier** | un dossier partagé entre plusieurs machines | partage de fichiers, ancien code | pratique, plus cher à volume égal |

Le stockage **objet** est la pièce maîtresse des architectures de données : c'est là que l'on dépose les données brutes, que Spark lit ses Parquet (chapitre 3) et que l'on range les modèles entraînés (chapitre 4). Il offre en général plusieurs **paliers** : *chaud* (accès fréquent, coût de stockage plus élevé), *froid* (accès rare), *archive* (accès très rare, très peu cher à conserver, mais cher et lent à récupérer). Le piège est de croire que le palier le moins cher au gigaoctet est le moins cher tout court : il faut ajouter le **coût de récupération**.

Un modèle avec des prix inventés : 10 To de données, avec ces tarifs (par Go et par mois) : chaud 0,023 € ; froid 0,012 € plus 0,010 € par Go récupéré ; archive 0,002 € plus 0,030 € par Go récupéré. Selon la **part des données relues chaque mois** :

```python hide-code
Go = 10_000
tarifs = {"chaud": (0.023, 0.0), "froid": (0.012, 0.010), "archive": (0.002, 0.030)}   # (stockage €/Go-mois, récupération €/Go)
parts = [1.0, 0.5, 0.1, 0.01, 0.0]
lignes = [{"part relue par mois": p, **{k: Go * s + Go * p * r for k, (s, r) in tarifs.items()}} for p in parts]
tab_stock = pd.DataFrame(lignes)
for k in tarifs: tab_stock[k] = tab_stock[k].round(0)
print(tab_stock.to_string(index=False))
sc, rc = tarifs["chaud"]; sa, ra = tarifs["archive"]; sf, rf = tarifs["froid"]
print(f"archive moins chère que chaud tant que la part relue est inférieure à {(sc - sa) / ra:.2f} ; archive moins chère que froid sous {(sf - sa) / (ra - rf):.2f}")
print(f"froid moins cher que chaud tant que la part relue est inférieure à {(sc - sf) / rf:.2f} (donc même si tout est relu chaque mois)")
```
<!--sortie-->
```text
 part relue par mois  chaud  froid  archive
                1.00  230.0  220.0    320.0
                0.50  230.0  170.0    170.0
                0.10  230.0  130.0     50.0
                0.01  230.0  121.0     23.0
                0.00  230.0  120.0     20.0
archive moins chère que chaud tant que la part relue est inférieure à 0.70 ; archive moins chère que froid sous 0.50
froid moins cher que chaud tant que la part relue est inférieure à 1.10 (donc même si tout est relu chaque mois)
```

Lecture : pour des données relues **rarement** (1 % par mois), l'archive coûte vingt-trois euros par mois contre deux cent trente en palier chaud, soit dix fois moins. Mais pour des données relues **souvent** (la totalité chaque mois), c'est l'archive qui devient la plus chère. Le palier optimal se décide donc sur le **profil d'accès**, que l'on connaît mal au début : la bonne pratique est de **mesurer** les accès, puis de définir des règles de transition automatiques (« après 90 jours sans lecture, passer en froid »). Les fournisseurs facturent aussi souvent des **durées minimales de conservation** par palier et des frais de suppression anticipée, à ajouter au calcul et **à vérifier**.

### 6.2.3 Les bases de données : relationnelle, NoSQL, entrepôt

Trois grandes familles de bases de données gérées, que le volume I a introduites (volume I, section 5.1 pour le modèle relationnel, 5.5 pour NoSQL) :

- **Base relationnelle gérée** (type PostgreSQL, MySQL ou équivalents propriétaires) : le fournisseur installe, sauvegarde, met à jour et réplique. Idéale pour les applications transactionnelles (OLTP : beaucoup de petites lectures et écritures, transactions, intégrité ; volume I, 5.4.4 et 5.4.6).
- **Base NoSQL** (clé-valeur, documents, colonnes larges) : modèle plus souple, extensibilité horizontale, cohérence parfois assouplie. À choisir quand le schéma varie ou que le débit est énorme.
- **Entrepôt de données** (*data warehouse*) : stockage en colonnes, très bon pour les requêtes analytiques sur des milliards de lignes (OLAP : agrégats, jointures, fenêtres ; volume I, chapitre 5, section 5.3). Il se facture souvent à la **quantité de données lues** par requête, ce qui rend la forme du schéma et le partitionnement directement visibles sur la facture.

Le conseil classique est de **ne pas utiliser l'un pour faire le travail de l'autre** : une base transactionnelle interrogée par des analyses lourdes ralentit l'application ; un entrepôt utilisé comme base d'application répond trop lentement aux petites écritures.

### 6.2.4 Données et analytique : lots et flux

Pour traiter de grands volumes, les fournisseurs offrent des services de **traitement par lots** (une tâche lit beaucoup de données, calcule, écrit ; typiquement Spark, chapitre 3, section 3.2) et de **traitement en flux** (des événements arrivent en continu et sont traités au fil de l'eau ; chapitre 3, section 3.3). On y trouve des versions **gérées** des outils libres (Spark, Kafka, Airflow) et des services propriétaires équivalents. Le compromis est le même qu'ailleurs : moins d'administration, plus de dépendance.

### 6.2.5 Les plateformes d'apprentissage automatique et les notebooks

Les grandes plateformes proposent des environnements de **notebooks** hébergés, des services d'**entraînement** (qui démarrent des machines puissantes, éventuellement avec des cartes graphiques, pour la durée d'un entraînement), de **suivi d'expériences**, de **registre de modèles** et de **mise à disposition** de modèles (chapitre 4, sections 4.2 et 4.5). Elles rassemblent en un seul produit ce que l'on assemble soi-même avec les outils du chapitre 4. Leur intérêt : le travail d'intégration est fait, les ressources (surtout les GPU, rares et chers) s'allouent à la demande. Leur risque : le **verrouillage** (les formats et les interfaces propres à la plateforme) et le **coût caché** d'un notebook ou d'un point d'accès laissé allumé (6.3.2).

### 6.2.6 L'identité et le réseau

Deux familles sont transversales et conditionnent la sécurité de tout le reste :

- **Identité et accès** (*IAM*) : qui (une personne, un programme) a le droit de faire quoi sur quelle ressource. Toute action dans le cloud passe par cette couche, et la majorité des incidents viennent d'une politique d'accès trop large (6.3.4).
- **Réseau** : réseaux virtuels privés, sous-réseaux, règles de pare-feu, équilibreurs de charge, passerelles. Il décide ce qui est joignable depuis internet et ce qui reste interne.

### 6.2.7 Des équivalences entre trois grands fournisseurs

Les trois principaux fournisseurs (Amazon Web Services, Microsoft Azure, Google Cloud) proposent des services équivalents sous des noms différents. La table ci-dessous donne des **exemples de noms**, sans classement ni jugement : le contenu d'un service, son prix, ses limites et même son nom peuvent évoluer et diffèrent dans le détail. **Tous les noms sont à vérifier** dans la documentation en vigueur.

| Famille | AWS | Azure | Google Cloud |
|---|---|---|---|
| Machine virtuelle | EC2 | Virtual Machines | Compute Engine |
| Conteneurs gérés (Kubernetes) | EKS | AKS | GKE |
| Conteneurs sans serveur | Fargate | Container Apps | Cloud Run |
| Fonctions | Lambda | Functions | Cloud Run functions |
| Stockage objet | S3 | Blob Storage | Cloud Storage |
| Disque (bloc) | EBS | Managed Disks | Persistent Disk |
| Base relationnelle gérée | RDS, Aurora | SQL Database, bases gérées PostgreSQL/MySQL | Cloud SQL, AlloyDB |
| Base NoSQL | DynamoDB | Cosmos DB | Firestore, Bigtable |
| Entrepôt de données | Redshift | Synapse / Fabric | BigQuery |
| Spark géré | EMR | Databricks, Synapse | Dataproc |
| Flux d'événements | Kinesis, MSK | Event Hubs | Pub/Sub |
| Plateforme d'apprentissage automatique | SageMaker | Azure Machine Learning | Vertex AI |
| Identité et accès | IAM | Entra ID, RBAC | Cloud IAM |
| Gestion de secrets | Secrets Manager | Key Vault | Secret Manager |
| Journal d'audit | CloudTrail | Activity Log | Cloud Audit Logs |

### 6.2.8 Les outils de ce volume, version gérée

Chaque outil étudié dans ce volume a un pendant « géré » chez les grands fournisseurs. La correspondance aide à répondre à la question : *« est-ce que je l'installe moi-même, ou est-ce que je loue le service ? »*

| Outil du volume | Installé soi-même | Service géré (exemples, **à vérifier**) | À arbitrer |
|---|---|---|---|
| **Spark** (3.2) | cluster que l'on administre | EMR, Dataproc, Databricks, Synapse | coût d'administration contre prix par heure de cluster |
| **Kafka** (3.3) | brokers que l'on administre | MSK, Event Hubs (interface Kafka), services Kafka gérés | opérations difficiles à externaliser, dépendance forte |
| **Airflow / Prefect** (4.4) | serveur et workers | MWAA, Cloud Composer, services d'orchestration gérés | pas de serveur à maintenir contre versions imposées |
| **MLflow** (4.5) | serveur de suivi + base | intégré aux plateformes ML (SageMaker, Azure ML, Databricks, Vertex AI) | formats ouverts, mais interface propre à la plateforme |
| **FastAPI en conteneur** (4.2, 4.6) | machine virtuelle + Docker | Fargate, Container Apps, Cloud Run, services d'applications gérées | simplicité contre contrôle fin |
| **Une base SQL** (volume I, ch. 5) | PostgreSQL sur une machine | RDS, SQL Database, Cloud SQL | sauvegardes et reprise après panne incluses |
| **Stockage de fichiers Parquet** (3.2) | disque ou serveur de fichiers | S3, Blob Storage, Cloud Storage | coûts de sortie, durabilité |

La règle de pouce, qui revient dans ce chapitre : **louez ce qui est difficile à opérer et ne vous différencie pas** (bases de données, sauvegardes, réseau) ; **gardez ce qui est standard et portable** (conteneurs, SQL, Parquet) pour limiter la dépendance.

> ✅ **À retenir.**
> - Six familles couvrent le catalogue : **calcul**, **stockage**, **bases de données**, **analytique** (lots et flux), **plateformes d'apprentissage automatique**, **identité et réseau**.
> - Plus une unité de calcul **démarre vite**, plus elle suit la demande de près : c'est ce qu'illustre la comparaison entre autoscaling de machines virtuelles et de conteneurs.
> - Le **palier de stockage** optimal dépend du **profil d'accès**, à mesurer ; le palier le moins cher au gigaoctet n'est pas toujours le moins cher.
> - Les trois fournisseurs offrent des services **équivalents** sous des noms différents : les noms sont à vérifier.
> - Louez ce qui est dur à opérer ; gardez portable ce qui est standard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5 (simulateur d'autoscaling, paliers de stockage), exercices 6.6 à 6.8.
