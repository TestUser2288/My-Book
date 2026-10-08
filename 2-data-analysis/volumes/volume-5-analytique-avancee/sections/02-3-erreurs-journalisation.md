## 2.3 Gestion des erreurs et journalisation

Un pipeline qui marche le jour de sa mise en service ne prouve rien. Ce qui compte, c'est ce qu'il fait **le jour où quelque chose ne va pas**, et la rapidité avec laquelle vous en êtes informé et pouvez comprendre. Cette section équipe notre chaîne de ce qui lui manque : un **journal** qui raconte, une **table des exécutions** qui compte, une **quarantaine** qui garde ce qui est douteux, des **contrôles** avant et après le chargement, des **reprises** pour les pannes passagères, et des **alertes** qui ne crient que quand il le faut.

### 2.3.1 Ce qui peut mal tourner

Avant d'ajouter des garde-fous, il faut savoir contre quoi. Les ennuis d'un pipeline se rangent en cinq familles, qui appellent des réponses différentes.

| Famille | Exemples dans notre dépôt | Réponse |
|---|---|---|
| **La source** | fichier absent, vide (septembre), tronqué (octobre), renvoyé (mars) | contrôle à la source (manifeste), alerte, attente d'un renvoi |
| **Le format** | colonne renommée (mai), dates en `JJ/MM/AAAA` (juillet), encodage (août) | contrat de données, tolérance **écrite**, échec clair sinon |
| **Les lignes** | doublons (novembre), clients inconnus, montants négatifs | quarantaine avec motif, seuil de tolérance |
| **Le traitement** | bogue, mémoire insuffisante, base verrouillée | exceptions, reprises si la panne est passagère, journal |
| **L'orchestration** | exécution en double, exécution oubliée, planificateur arrêté | verrou (section 2.2), rattrapage, alerte « rien ne s'est passé » |

Mettons la chaîne complète à l'épreuve : on **rejoue l'histoire** de l'année, livraison après livraison, dans l'ordre où les fichiers sont arrivés. L'exécution complète (`P.executer`) contient tout ce qu'on va détailler : lecture, contrat, contrôles, transformation, chargement en transaction, quarantaine, trace.

```python
ent3 = P.nouvel_entrepot()
cl3 = P.charger_dimensions(ent3)
h3 = P.Horloge()
journal_fichier = os.path.join(P.dossier_de(ent3), "pipeline.log")
log, tampon = P.journal(h3, fichier=journal_fichier)
P.rejouer(ent3, DEPOT, cl3, h3, log)
print(ent3.execute("SELECT statut, count(*) AS exécutions FROM executions GROUP BY ALL ORDER BY 1").df().to_string(index=False))
```
<!--sortie-->
```text
statut  exécutions
 ECHEC           2
SUCCES          13
```

Sur les quinze livraisons, **deux ont échoué** : le fichier vide de septembre et le fichier tronqué d'octobre. Dans les deux cas, **rien n'a été écrit** dans l'entrepôt, et les renvois du 9 octobre et du 6 novembre ont ensuite été chargés normalement. C'est ce que le collègue en congé de l'introduction aurait voulu : un échec **visible et sans conséquence** plutôt qu'un chiffre faux.

### 2.3.2 Le journal : raconter ce qu'on fait

Le **journal** (*log*) est le récit, ligne à ligne, de ce que le pipeline a fait. Le module standard `logging` de Python en offre l'essentiel : des **niveaux** de gravité, des **gestionnaires** qui décident où écrire (écran, fichier, serveur), et des **formateurs** qui décident de l'apparence.

| Niveau | Ce qu'on y met | Exemple |
|---|---|---|
| `DEBUG` | le détail technique, utile seulement pour comprendre un bogue | « requête SQL envoyée » |
| `INFO` | la marche normale : début, fin, nombres de lignes | « fin avril : 2 225 lignes chargées » |
| `WARNING` | quelque chose d'inhabituel mais sans gravité | « 25 lignes en quarantaine » |
| `ERROR` | une étape a échoué, le pipeline s'arrête ou saute | « fichier vide » |
| `CRITICAL` | le pipeline entier est hors service | « entrepôt injoignable » |

On règle le niveau du journal : à `INFO`, les messages `DEBUG` sont ignorés. Voici le principe, avec un journal qui écrit dans un tampon mémoire pour qu'on en voie le contenu.

```python
flux = io.StringIO()
demo = logging.getLogger("demo")
demo.setLevel(logging.INFO)
gestionnaire = logging.StreamHandler(flux)
gestionnaire.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
demo.addHandler(gestionnaire)
demo.debug("requête envoyée")
demo.info("fin avril : %d lignes chargées", 2225)
demo.warning("%d lignes en quarantaine", 25)
demo.error("fichier vide")
print(flux.getvalue())
```
<!--sortie-->
```text
INFO    fin avril : 2225 lignes chargées
WARNING 25 lignes en quarantaine
ERROR   fichier vide
```

Le message `DEBUG` n'apparaît pas : il est sous le niveau réglé. En production on ajoute au format la date et l'heure (`%(asctime)s`), le nom du programme et, pour les journaux que lira une machine, une structure fixe.

Un journal en **texte libre** se lit bien à l'œil et mal à la machine. Un journal **structuré**, une ligne JSON par événement, permet de le **filtrer** (« tous les échecs d'octobre ») et de le **compter** sans expression régulière. Un formateur de quelques lignes suffit.

```python
class FormatJson(logging.Formatter):
    def format(self, record):
        return json.dumps({"niveau": record.levelname, "mois": getattr(record, "mois", ""), "message": record.getMessage()}, ensure_ascii=False)

gestionnaire.setFormatter(FormatJson())
demo.info("fin %s : %d lignes chargées", "commandes_2025-04.csv", 2225, extra={"mois": "2025-04"})
demo.error("%s est vide", "commandes_2025-09.csv", extra={"mois": "2025-09"})
print("\n".join(flux.getvalue().splitlines()[-2:]))
```
<!--sortie-->
```text
{"niveau": "INFO", "mois": "2025-04", "message": "fin commandes_2025-04.csv : 2225 lignes chargées"}
{"niveau": "ERROR", "mois": "2025-09", "message": "commandes_2025-09.csv est vide"}
```

Pour que les sorties de ce livre soient **identiques à chaque exécution**, les journaux de notre pipeline utilisent une **horloge factice** qui avance de trois secondes à chaque lecture (et saute à la date de livraison de chaque fichier). Dans la réalité, ce serait l'heure du système. Voici ce que le journal de l'année a écrit autour de l'échec d'octobre.

```python
extrait = [l for l in tampon.getvalue().splitlines() if "2025-10-03" <= l[:10] <= "2025-11-06"]
print("\n".join(extrait))
```
<!--sortie-->
```text
2025-10-03 06:00:06 INFO    début commandes_2025-09.csv
2025-10-03 06:00:12 ERROR   commandes_2025-09.csv : SourceVide : commandes_2025-09.csv est vide
2025-10-09 06:00:06 INFO    début commandes_2025-09_v2.csv
2025-10-09 06:00:12 INFO    fin commandes_2025-09_v2.csv : 2521 insérées, 0 mises à jour, 1 rejetées
2025-11-03 06:00:06 INFO    début commandes_2025-10.csv
2025-11-03 06:00:12 ERROR   commandes_2025-10.csv : ControleEchoue : 2249 lignes lues pour 2645 annoncées
2025-11-06 06:00:06 INFO    début commandes_2025-10_v2.csv
2025-11-06 06:00:12 INFO    fin commandes_2025-10_v2.csv : 2644 insérées, 0 mises à jour, 1 rejetées
```

```python hide
if os.environ.get("REGENERER_CAPTURES") == "1":
    from outils_capture import capturer
    capturer(P.page_journal(extrait, "pipeline.log (extrait)"), "figures/ch02-journal.png", largeur=980, hauteur=215, html=True)
```

![Le journal du pipeline autour de l'échec du fichier d'octobre : le premier fichier est refusé car il contient 2 249 lignes pour 2 645 annoncées, puis le renvoi du 6 novembre est chargé normalement. Capture réelle d'un journal généré localement, rendu en HTML (le niveau est écrit en toutes lettres et en couleur).](figures/ch02-journal.png)

Un bon message de journal répond à quatre questions : **quoi** (quelle étape, quel fichier), **combien** (nombres de lignes lues, chargées, rejetées), **avec quel résultat** et, en cas d'erreur, **pourquoi**. Il ne contient **jamais** de secret (mot de passe, clé d'accès) ni de donnée personnelle (adresse e-mail, nom d'un client) : un journal circule bien plus que la base.

> ⚠️ **Piège : le journal qui dit tout ou rien.** Un journal bavard cache l'essentiel dans le bruit ; un journal silencieux ne dit rien le jour où l'on en a besoin. Règle pratique : **une ligne au début, une ligne à la fin, une ligne par décision ou anomalie**, avec les nombres.

### 2.3.3 La table des exécutions : le journal pour les machines

Le journal est fait pour un humain qui cherche. Pour répondre à des questions comme « quel mois n'a pas été chargé ? » ou « combien de lignes ont été rejetées cette année ? », on tient en plus une **table** : une ligne par exécution, avec son mois, son fichier, ses heures de début et de fin, son statut, ses compteurs et son message. C'est la table que lisent le rattrapage (section 2.2.5), les alertes (2.3.7) et, plus tard, le tableau de bord de santé du pipeline.

```python
print(ent3.execute("""SELECT mois, fichier, statut, lignes_lues AS lues, lignes_chargees AS chargées, lignes_rejetees AS rejetées
                      FROM executions WHERE mois IN ('2025-09', '2025-10') ORDER BY id_execution""").df().to_string(index=False))
```
<!--sortie-->
```text
   mois                  fichier statut  lues  chargées  rejetées
2025-09    commandes_2025-09.csv  ECHEC     0         0         0
2025-09 commandes_2025-09_v2.csv SUCCES  2522      2521         1
2025-10    commandes_2025-10.csv  ECHEC  2249         0         0
2025-10 commandes_2025-10_v2.csv SUCCES  2645      2644         1
```

Les quatre lignes racontent les deux histoires d'un coup d'œil : pour septembre et octobre, un **échec** (0 ligne chargée) suivi d'un **succès** quand le renvoi est arrivé. Le même contenu, mis en calendrier, donne la vue d'ensemble de l'année.

```python hide
ex3 = ent3.execute("SELECT * FROM executions ORDER BY id_execution").df()
P.fig_calendrier(ex3, "ch02-calendrier-executions.png")
```
<!--sortie-->
```text
figure : ch02-calendrier-executions.png
```

![Le calendrier des quinze exécutions de l'année : un cercle pour un succès, une croix pour un échec, placés à la date d'exécution sur la ligne du mois traité. Mars, septembre et octobre ont demandé une seconde livraison ; les croix de septembre et d'octobre sont les deux échecs.](figures/ch02-calendrier-executions.png)

> 💡 **Intuition.** Le journal répond à « que s'est-il passé ? », la table des exécutions répond à « où en est-on ? ». On a besoin des deux, et la table est celle que l'on branche sur des alertes et des tableaux de bord.

### 2.3.4 La quarantaine : mettre de côté, pas jeter

Les lignes que la transformation rejette ne disparaissent pas : elles sont écrites dans la table `rejets`, avec le fichier, le numéro de ligne dans le fichier, le motif et le contenu. Regardons ce que la quarantaine contient à la fin de l'année, pour la **dernière version** livrée de chaque mois (les premières versions de mars, de septembre et d'octobre sont remplacées).

```python
derniers = man.sort_values("date_livraison").groupby("mois").tail(1)["fichier"].tolist()
q = ent3.execute("SELECT motif, count(*) AS lignes FROM rejets WHERE fichier IN (SELECT unnest(?)) GROUP BY ALL ORDER BY 2 DESC", [derniers]).df()
print(q.to_string(index=False))
```
<!--sortie-->
```text
          motif  lignes
  doublon exact      25
 client inconnu      18
montant négatif       9
```

La quarantaine contient exactement les défauts qui ont été **injectés** dans les fichiers : 25 doublons (tous en novembre), 18 lignes dont le client n'est pas dans le référentiel et 9 montants négatifs. Une chaîne qui ne retrouverait pas ces nombres aurait un défaut, soit de contrôle, soit de comptage.

```python hide
rej = ent3.execute("""SELECT substr(fichier, 11, 7) AS mois, motif, count(*) AS n FROM rejets
                      WHERE fichier IN (SELECT unnest(?)) GROUP BY ALL""", [derniers]).df()
P.fig_rejets(rej, "ch02-rejets.png")
```
<!--sortie-->
```text
figure : ch02-rejets.png
```

![Les lignes en quarantaine à la fin de l'année, par mois et par motif : novembre concentre les 25 doublons, les autres mois n'ont que quelques lignes orphelines ou quelques avoirs.](figures/ch02-rejets.png)

La quarantaine est un **outil de travail**, pas une poubelle. Il faut décider **qui** la lit, **à quelle fréquence** et **ce qu'on en fait** : renvoyer à l'équipe source pour correction, ou rectifier le référentiel. Voici le cas d'un client qui manque au référentiel : le client 90001 est un nouveau client que le système de commandes connaissait déjà mais pas encore le référentiel. Une fois qu'il y est ajouté, on **relance le mois** : la ligne en quarantaine entre dans l'entrepôt, et rien d'autre ne change.

```python hide-code
fichier_q = ent3.execute("SELECT fichier FROM rejets WHERE contenu LIKE '%,90001,%'").fetchone()[0]
annonce_q = int(man.loc[man["fichier"] == fichier_q, "lignes_annoncees"].iloc[0])
ent4 = P.nouvel_entrepot(); cl4 = P.charger_dimensions(ent4)
for clients_connus in (cl4, cl4 | {90001}):
    P.executer(ent4, os.path.join(DEPOT, fichier_q), annonce_q, clients_connus, P.Horloge())
print(ent4.execute("SELECT id_execution AS exécution, lignes_chargees AS chargées, lignes_rejetees AS rejetées, message FROM executions").df().to_string(index=False))
```
<!--sortie-->
```text
 exécution  chargées  rejetées                       message
         1      2225         3 2225 insérées, 0 mises à jour
         2      2226         2 1 insérées, 2225 mises à jour
```

La seconde exécution met à jour les lignes déjà présentes et ajoute celle qui était en quarantaine ; le nombre de lignes rejetées baisse d'une unité. On a corrigé à la **source** (le référentiel) puis **relancé**, au lieu de modifier à la main une ligne dans l'entrepôt : c'est la seule façon de rester reproductible.

### 2.3.5 Les contrôles de qualité : avant et après

Une chaîne sûre contrôle à **deux moments**. Avant le chargement, on vérifie que ce qu'on a reçu est exploitable ; après, on vérifie que ce qu'on a écrit correspond à ce qu'on voulait écrire. Les contrôles d'entrée protègent l'entrepôt ; les contrôles de sortie protègent le lecteur du rapport. Les techniques de contrôle (complétude, validité, cohérence) ont été vues au volume II (section 3.2) : ici, on les **branche** dans la chaîne.

| Moment | Contrôle | Notre dépôt |
|---|---|---|
| **Avant** | le fichier n'est pas vide | septembre |
| **Avant** | les colonnes du contrat sont là | mai (nom différent, toléré) |
| **Avant** | **lignes lues = lignes annoncées** par le manifeste | octobre |
| **Avant** | la part de lignes rejetées reste sous le seuil | seuil de 2 % |
| **Après** | **lignes lues = lignes chargées + lignes rejetées** (rien ne s'est perdu) | tous les mois |
| **Après** | **somme des montants de la source = somme chargée + somme rejetée** (au centime) | tous les mois |
| **Après** | toutes les dates sont dans le mois du fichier | tous les mois |
| **Après** | le total de l'entrepôt retombe sur celui d'**une autre source** | voir plus bas |

Les deux contrôles de conservation s'écrivent en quelques lignes. Mettons-les à l'épreuve sur le fichier de mars, d'abord tel quel, puis après avoir **perdu dix lignes** en route (comme le ferait une jointure qui élimine des lignes sans qu'on s'en aperçoive).

```python
def rapprocher(brut, valides, rejets):
    source = pd.to_numeric(brut["montant"], errors="coerce").sum()
    cible = valides["montant"].sum() + pd.to_numeric(rejets["montant"], errors="coerce").sum()
    return {"lignes conservées": len(brut) == len(valides) + len(rejets), "montants conservés": bool(abs(source - cible) < 0.005)}

brut = extraire(os.path.join(DEPOT, "commandes_2025-03_v2.csv"))
valides, rejets = transformer(brut, clients)
print("intact :", rapprocher(brut, valides, rejets))
print("dix lignes perdues :", rapprocher(brut, valides.iloc[10:], rejets))
```
<!--sortie-->
```text
intact : {'lignes conservées': True, 'montants conservés': True}
dix lignes perdues : {'lignes conservées': False, 'montants conservés': False}
```

Le second contrôle est le plus précieux : il **ne dépend d'aucune règle de gestion**. Il dit seulement « tout ce qui est entré est ressorti, quelque part », et il attrape une catégorie entière d'erreurs (jointures qui perdent ou multiplient des lignes, filtres trop gourmands) que les règles ligne à ligne ne voient pas.

Reste le dernier contrôle du tableau, qui ne regarde plus le fichier mais **une autre source** : le total de l'entrepôt doit retrouver celui de la base des commandes du volume III, qui est un système indépendant du dépôt (volume II, section 3.3 sur la réconciliation).

```python
c25 = pd.read_csv(os.path.join(os.environ["DONNEES"], "commandes.csv")).query("date_commande >= '2025-01-01'")
base_ca = pd.read_csv(os.path.join(os.environ["DONNEES"], "lignes_commande.csv")).merge(c25[["id_commande"]])["montant"].sum()
entrepot_ca = ent3.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0]
print("base :", fr(base_ca, 2), "€ | entrepôt :", fr(entrepot_ca, 2), "€ | écart :", fr(entrepot_ca - base_ca, 2), "€ | état identique à celui du rattrapage :", P.empreinte(ent3) == P.empreinte(ent2))
```
<!--sortie-->
```text
base : 1 324 763,72 € | entrepôt : 1 324 763,72 € | écart : 0,00 € | état identique à celui du rattrapage : True
```

L'écart est nul : l'entrepôt retrouve le chiffre d'affaires de la base, **au centime**, malgré un fichier tronqué, un fichier vide, des doublons et des erreurs de saisie. Et l'état obtenu en rejouant l'histoire dans l'ordre d'arrivée est **identique**, empreinte comprise, à celui du rattrapage de la section 2.2.5, qui n'avait chargé que la dernière version de chaque mois : c'est l'idempotence qui l'assure.

Pour les contrôles de **forme** (types, valeurs permises, unicité), on peut aussi s'appuyer sur une bibliothèque de validation comme **pandera** (volume II, section 3.5), qui exprime le contrat comme un schéma et rapporte **tous** les défauts d'un coup plutôt que le premier. Voici le schéma des colonnes qui comptent pour le rapport, appliqué aux lignes valides, puis à une version où un montant a été rendu négatif.

```python
import pandera.pandas as pa
schema = pa.DataFrameSchema({"id_ligne": pa.Column(int, unique=True), "montant": pa.Column(float, pa.Check.ge(0)), "canal": pa.Column(str, pa.Check.isin(CANAUX))})
schema.validate(valides)
abime = valides.assign(montant=valides["montant"].where(valides.index != 3, -5.0))
try:
    schema.validate(abime, lazy=True)
except pa.errors.SchemaErrors as e:
    print(e.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
```
<!--sortie-->
```text
 column                       check  failure_case
montant greater_than_or_equal_to(0)          -5.0
```

> 🧭 **En pratique : où mettre quel contrôle ?** Les contrôles **bloquants** (fichier vide, colonnes absentes, conservation violée) arrêtent le chargement. Les contrôles **d'avertissement** (part de lignes rejetées au-dessus d'un seuil bas) laissent charger mais signalent. Le seuil est un choix métier : à 2 % de rejets le fichier de novembre passe (25 lignes sur 3 484, soit 0,7 %), à 0,5 % il aurait été refusé. L'important est qu'il soit **écrit**, **réglable** et **connu** de la gérante.

### 2.3.6 Les reprises : réessayer ce qui peut l'être

Toutes les pannes ne se valent pas. Un réseau qui coupe une seconde, un service qui répond « trop de demandes », une base momentanément verrouillée : réessayer un peu plus tard a toutes les chances de réussir. Un fichier vide, une colonne manquante, un contrôle de conservation violé : réessayer cent fois ne changera rien.

| Panne | Passagère ? | Que faire |
|---|---|---|
| connexion coupée, délai dépassé, service surchargé (429, 503) | **oui** | réessayer avec attente |
| fichier absent **pour l'instant** (livraison en retard) | **oui** | réessayer plus tard, avec une limite de durée |
| fichier vide, colonne absente, contrat violé | non | s'arrêter, prévenir |
| bogue (division par zéro, type inattendu) | non | s'arrêter, prévenir, corriger |

Pour les pannes passagères, la méthode classique est l'**attente exponentielle** : on réessaie après 1 seconde, puis 2, puis 4, en ajoutant un peu d'aléa (*jitter*) pour que mille processus qui ont échoué en même temps ne reviennent pas tous au même instant. Dans le code, on **passe en argument** la fonction qui dort, pour pouvoir tester sans attendre.

```python
def avec_reprises(fonction, essais=4, base=1.0, dormir=time.sleep, transitoires=(ConnectionError, TimeoutError)):
    rng = np.random.default_rng(0)
    for k in range(essais):
        try:
            return fonction()
        except transitoires:
            if k == essais - 1:
                raise
            dormir(base * 2 ** k * (1 + 0.25 * rng.random()))
```

Une fonction qui échoue deux fois puis réussit, et une autre qui échoue pour une raison **définitive** :

```python hide-code
appels, attentes = {"n": 0}, []

def service_capricieux():
    appels["n"] += 1
    if appels["n"] < 3:
        raise ConnectionError("réseau indisponible")
    return "données reçues"

print(avec_reprises(service_capricieux, dormir=attentes.append), "| essais :", appels["n"], "| attentes (s) :", [round(a, 1) for a in attentes])
try:
    avec_reprises(lambda: extraire(os.path.join(DEPOT, "commandes_2025-09.csv")), dormir=attentes.append)
except ValueError as e:
    print("erreur définitive, aucune nouvelle tentative :", e)
```
<!--sortie-->
```text
données reçues | essais : 3 | attentes (s) : [1.2, 2.1]
erreur définitive, aucune nouvelle tentative : fichier vide
```

La première panne est surmontée en trois essais (les attentes réelles auraient été d'environ une seconde, puis deux). La seconde, un fichier vide, **remonte tout de suite** : on ne réessaie pas ce qui ne peut pas s'arranger seul. Toute reprise a une **limite** (ici quatre essais) : à l'infini, un pipeline réessaie en silence ce qu'il aurait fallu signaler.

> ⚠️ **Piège : les reprises sans idempotence.** Réessayer un chargement qui a réussi à moitié double des lignes s'il n'est pas idempotent. C'est une raison de plus pour écrire les chargements en transaction (tout ou rien) et par fusion, comme à la section 2.1.

### 2.3.7 Les alertes : crier au bon moment

Le journal et la table des exécutions ne servent à rien si personne ne les lit. L'**alerte** est ce qui vient chercher quelqu'un. Le piège est symétrique : trop peu d'alertes et l'on découvre la panne par la gérante ; trop d'alertes et l'on **n'ouvre plus** les messages, y compris le jour où l'un d'eux compte vraiment. C'est la **fatigue d'alerte**.

La règle qui y répond : **n'alerter que sur ce qui appelle une action**, par une personne identifiée, qui sait quoi faire. Voici le jeu de règles de notre pipeline, rangé par gravité.

| Gravité | Règle | Action attendue |
|---|---|---|
| **Critique** | un mois a échoué et n'a pas été résolu depuis | contacter la source, relancer à la main |
| **Critique** | **aucun chargement réussi depuis plus de 35 jours** | le planificateur est peut-être arrêté |
| **Attention** | plus de 0,5 % de lignes en quarantaine sur un mois | lire la quarantaine, prévenir l'équipe source |
| *Pas d'alerte* | une ligne rejetée, un avertissement isolé, une reprise qui a réussi | à lire dans le journal, si on le souhaite |

Appliquons ces règles **au fil de l'année**, aux dates où l'on aurait pu les lire. On compte aussi, pour comparaison, les alertes qu'aurait émises une règle naïve « prévenir dès qu'une ligne est rejetée ou qu'une exécution échoue ».

```python hide-code
dates = sorted(man["date_livraison"].unique())
vues, naive = set(), 0
for d in dates:
    vues |= {m for _, m in P.evaluer_alertes(ent3, d)}
    jour = ent3.execute("SELECT count(*) FROM executions WHERE strftime(debut, '%Y-%m-%d') = ? AND (statut = 'ECHEC' OR lignes_rejetees > 0)", [d]).fetchone()[0]
    naive += jour
print("alertes utiles sur l'année :", len(vues), "| alertes d'une règle naïve :", naive)
print(*sorted(vues), sep="\n")
```
<!--sortie-->
```text
alertes utiles sur l'année : 3 | alertes d'une règle naïve : 15
2025-09 : échec non résolu (SourceVide : commandes_2025-09.csv est vide)
2025-10 : échec non résolu (ControleEchoue : 2249 lignes lues pour 2645 annoncées)
2025-11 : 25 lignes en quarantaine sur 3484
```

Sur quinze exécutions, la règle naïve aurait sonné **à chaque fois** (une ligne rejetée suffit : quinze alertes sur quinze), contre **trois** alertes utiles : deux échecs et le mois de novembre. Quand toutes les exécutions déclenchent une alerte, plus aucune n'en est une.

Reste la panne la plus sournoise, celle que **rien ne signale** : si le planificateur est arrêté, il n'échoue pas, il **ne fait rien**, et aucune règle fondée sur les échecs ne s'enclenche. On l'attrape par un **battement de cœur** (*heartbeat* ou *dead man's switch*) : une règle qui alerte quand il ne s'est **pas** passé quelque chose pendant plus longtemps que prévu. Vérifions-la : si nous regardons le 20 février 2026 sans que rien n'ait été chargé depuis le 3 janvier, la règle des 35 jours se déclenche.

```python
print([m for _, m in P.evaluer_alertes(ent3, "2026-02-20") if m.startswith("aucun")])
```
<!--sortie-->
```text
['aucun chargement réussi depuis plus de 35 jours']
```

> 🧭 **En pratique : quelques règles pour des alertes qui servent.**
> - **Un propriétaire** par alerte (une personne ou un groupe), et un message qui dit **ce qui s'est passé, depuis quand, et quoi faire** en premier.
> - **Pas de répétition** : une alerte déjà envoyée n'est pas renvoyée chaque jour ; on la renvoie si elle change de gravité.
> - **Un canal différent selon la gravité** : un message pour « attention », un appel ou une notification pour « critique ».
> - **Testez le chemin d'alerte** lui-même : une fois par trimestre, provoquez une fausse panne et vérifiez que quelqu'un la reçoit. Une alerte qui n'arrive nulle part est pire qu'une absence d'alerte, car elle donne le sentiment d'être protégé.

### 2.3.8 Échouer bruyamment

Tout ce qui précède tient en un principe : **un pipeline doit échouer bruyamment**. Entre un programme qui plante avec un message clair et un programme qui livre un chiffre faux sans rien dire, le premier coûte une matinée de dépannage, le second coûte une décision prise sur une erreur. Concrètement :

- un contrôle qui échoue **arrête** la chaîne et empêche la **publication** (on n'envoie pas le rapport d'un mois qui n'est pas contrôlé) ;
- le programme rend un **code de sortie** différent de zéro, que le planificateur sait lire ;
- le **message** nomme le fichier, le contrôle et les nombres en cause (« 2 249 lignes lues pour 2 645 annoncées ») ;
- l'état de l'entrepôt reste **celui d'avant** (transaction), donc aucun lecteur ne tombe sur un état à moitié chargé ;
- et un **humain** est prévenu, par un canal qu'il lit.

> ✅ **À retenir.**
> - Cinq familles d'ennuis : la **source**, le **format**, les **lignes**, le **traitement**, l'**orchestration**. Chacune a sa réponse.
> - Le **journal** raconte (quoi, combien, résultat, pourquoi ; jamais de secret ni de donnée personnelle) ; la **table des exécutions** compte et alimente alertes et tableaux de bord.
> - La **quarantaine** garde ce qui est douteux, avec son motif ; on corrige à la source, puis on relance.
> - On contrôle **avant** (fichier non vide, colonnes, nombre de lignes annoncé) et **après** (rien ne s'est perdu en lignes ni en montants ; retombée sur une autre source).
> - On **réessaie** les pannes passagères avec attente exponentielle et limite, jamais les pannes définitives.
> - Les alertes sont **rares, actionnables, avec un propriétaire** ; un **battement de cœur** attrape la panne qui ne fait pas de bruit.
> - **Échouer bruyamment** vaut mieux que se tromper en silence.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.5 et 2.6, exercices 2.8 à 2.10.
