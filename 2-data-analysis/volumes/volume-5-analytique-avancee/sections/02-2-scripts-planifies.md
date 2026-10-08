## 2.2 Scripts planifiés et pipelines

La section précédente a donné les pièces : lire, contrôler, charger. Pour que cela tourne **sans vous**, il reste trois choses : découper le travail en étapes qui s'enchaînent, le rendre pilotable de l'extérieur (une ligne de commande, des paramètres), et le déclencher à heure fixe, en sachant le relancer et le rattraper quand il a manqué un rendez-vous.

### 2.2.1 Un pipeline est une suite d'étapes qui dépendent les unes des autres

Un pipeline n'est pas un long script, c'est une suite d'**étapes**, chacune faisant une chose et une seule. Chaque étape reçoit ce que la précédente a produit et rend quelque chose à la suivante. Cette découpe a trois avantages : on teste une étape isolément, on la relance seule quand elle a échoué, et on sait toujours **où** le travail s'est arrêté.

Nos étapes sont celles du schéma de la section 2.1 : repérer le fichier du mois, l'extraire, le transformer, charger les lignes valides, mettre les autres en quarantaine, contrôler le résultat, publier. On les écrit comme un **graphe de dépendances** : pour chaque étape, la liste de celles qui doivent être terminées avant elle.

```python
from graphlib import TopologicalSorter
GRAPHE = {"repérer": set(), "extraire": {"repérer"}, "transformer": {"extraire"}, "quarantaine": {"transformer"},
          "charger": {"transformer"}, "contrôler": {"charger"}, "publier": {"contrôler"}}
print(list(TopologicalSorter(GRAPHE).static_order()))
```
<!--sortie-->
```text
['repérer', 'extraire', 'transformer', 'quarantaine', 'charger', 'contrôler', 'publier']
```

```python hide
positions = {"repérer": (0, 0.5), "extraire": (2, 0.5), "transformer": (4, 0.5), "quarantaine": (6, -0.5), "charger": (6, 1.0), "contrôler": (8, 1.0), "publier": (10, 1.0)}
P.fig_graphe(GRAPHE, None, "ch02-dag-pipeline.png", positions, "Les sept étapes du pipeline mensuel et leurs dépendances")
```
<!--sortie-->
```text
figure : ch02-dag-pipeline.png
```

![Le graphe des étapes du pipeline mensuel : chaque flèche dit « l'étape de droite ne peut commencer que quand celle de gauche est terminée ». La quarantaine et le chargement sont indépendants l'un de l'autre. Schéma dessiné.](figures/ch02-dag-pipeline.png)

Le module standard `graphlib` fournit l'ordre d'exécution : une étape n'apparaît jamais avant celles dont elle dépend. On l'appelle un **graphe orienté acyclique** (*DAG*, en anglais) : orienté parce que les flèches ont un sens, acyclique parce qu'on ne peut pas revenir en arrière, sans quoi une étape attendrait sa propre fin. Ce vocabulaire reviendra en section 2.4, car il est celui de tous les orchestrateurs.

Les étapes ne se contentent pas de s'enchaîner, elles se **paramètrent**. Notre pipeline travaille pour un mois donné, sur un dossier de dépôt donné, avec un seuil de rejets donné : ce sont des paramètres, pas des constantes enfouies dans le code. Voici la version la plus simple de la chaîne, qui prend le mois et la cible en arguments.

```python
CONFIG = {"depot": DEPOT, "seuil_rejets": 0.02}

def derniere_version(depot, mois):
    m = P.manifeste(depot)
    return m[m["mois"] == mois].sort_values("date_livraison").iloc[-1]

def pipeline(mois, cible, config=CONFIG):
    f = derniere_version(config["depot"], mois)
    valides, rejets = transformer(extraire(os.path.join(config["depot"], f["fichier"])), clients)
    inserees, majs = P.charger(cible, valides, f["fichier"])
    return {"fichier": f["fichier"], "insérées": inserees, "mises à jour": majs, "rejetées": len(rejets)}
```

La règle « on prend la **dernière version livrée** du mois » est une décision de métier, écrite à un seul endroit : quand le renvoi de mars arrive, la chaîne le préfère automatiquement au premier fichier. Essayons deux fois de suite sur mars, sur un entrepôt neuf.

```python
ent2 = P.nouvel_entrepot()
cl2 = P.charger_dimensions(ent2)
print(pipeline("2025-03", ent2))
print(pipeline("2025-03", ent2))
```
<!--sortie-->
```text
{'fichier': 'commandes_2025-03_v2.csv', 'insérées': 2023, 'mises à jour': 0, 'rejetées': 5}
{'fichier': 'commandes_2025-03_v2.csv', 'insérées': 0, 'mises à jour': 2023, 'rejetées': 5}
```

Le deuxième appel ne charge plus rien de nouveau et remplace les 2 023 lignes déjà présentes : c'est l'idempotence de la section 2.1, que l'on retrouve ici sans y penser. Un pipeline **paramétré par le mois** et **idempotent** peut être rejoué pour n'importe quel mois, dans n'importe quel ordre, autant de fois qu'on veut : c'est la propriété qui rend possible tout le reste de la section.

> 💡 **Intuition.** Les paramètres sont les boutons du pipeline, l'idempotence est son filet de sécurité. Sans paramètres, on ne peut pas rejouer un mois ancien ; sans idempotence, on n'ose pas le faire.

### 2.2.2 Piloter de l'extérieur : la ligne de commande

Un planificateur ne sait pas appeler une fonction Python : il sait **lancer une commande** et lire son **code de sortie** (0 si tout va bien, autre chose sinon). Il faut donc donner à notre pipeline une porte d'entrée en ligne de commande. Le module standard `argparse` s'en charge, avec une aide en prime.

```python
import argparse
parseur = argparse.ArgumentParser(prog="pipeline", description="Charge les commandes livrées par mois dans l'entrepôt.")
parseur.add_argument("--depot", default="donnees/ch02-depot", help="dossier des fichiers livrés")
parseur.add_argument("--mois", help="un seul mois (AAAA-MM) ; sinon tous les mois")
parseur.add_argument("--simuler", action="store_true", help="n'écrit rien : liste ce qui serait fait")
parseur.add_argument("--seuil-rejets", type=float, default=0.02, help="part maximale de lignes rejetées")
print(parseur.parse_args(["--mois", "2025-03", "--simuler"]))
```
<!--sortie-->
```text
Namespace(depot='donnees/ch02-depot', mois='2025-03', simuler=True, seuil_rejets=0.02)
```

Le script complet est `build/outils_ch02.py` (sous-commande `pipeline`) ; il enveloppe la chaîne que nous construisons. Lançons-le comme le ferait un planificateur : dans un processus à part, en lisant sa sortie et son code de sortie. D'abord en **simulation**, qui n'écrit rien.

```python
import subprocess
def lancer(*arguments):
    r = subprocess.run([sys.executable, "build/outils_ch02.py", "pipeline", *arguments], capture_output=True, text=True)
    print(r.stdout.rstrip())
    print("code de sortie :", r.returncode)
lancer("--mois", "2025-03", "--simuler")
```
<!--sortie-->
```text
[simulation] chargerait commandes_2025-03_v2.csv (2028 lignes annoncées)
code de sortie : 0
```

L'option `--simuler` (on dit aussi *dry run*) est l'une des plus utiles que l'on puisse offrir : avant de lancer une opération sur douze mois, on voit ce qu'elle ferait. Elle n'a de valeur que si elle ne fait **réellement rien d'autre** ; ici, elle sort avant toute écriture. Maintenant pour de vrai, puis avec un seuil de rejets très strict, qui doit faire échouer novembre (25 lignes en double sur plus de 3 400).

```python
lancer("--mois", "2025-03")
lancer("--mois", "2025-11", "--seuil-rejets", "0.005")
```
<!--sortie-->
```text
2025-04-14 06:00:06 INFO    début commandes_2025-03_v2.csv
2025-04-14 06:00:09 INFO    fin commandes_2025-03_v2.csv : 2023 insérées, 0 mises à jour, 5 rejetées
code de sortie : 0
2025-12-03 06:00:06 INFO    début commandes_2025-11.csv
2025-12-03 06:00:09 ERROR   commandes_2025-11.csv : ControleEchoue : 25 lignes rejetées sur 3484 (seuil 0,50 %)
code de sortie : 1
```

Le code de sortie **1** du second appel est l'information essentielle pour le planificateur : c'est lui qui déclenche une alerte, une nouvelle tentative ou un arrêt. Un script qui échoue mais rend 0 est le pire des scripts, car personne n'est prévenu.

> ⚠️ **Piège : le script qui avale ses erreurs.** Une exception attrapée par un `try/except` qui se contente d'afficher un message laisse le script se terminer « normalement ». Dans un pipeline, une erreur doit soit être **traitée** (on sait quoi faire), soit **remonter** jusqu'au code de sortie.

### 2.2.3 Planifier : le cron

Sous Linux et macOS, le planificateur historique s'appelle **cron**. On lui donne, pour chaque tâche, une **expression** de cinq champs qui dit *quand* la lancer, suivie de la commande. Windows a le Planificateur de tâches, qui fait la même chose avec des fenêtres.

```python hide
P.fig_cron("ch02-cron.png")
```
<!--sortie-->
```text
figure : ch02-cron.png
```

![Les cinq champs d'une expression cron, ici « 0 6 3 * * » : minute 0, heure 6, jour du mois 3, tous les mois, tous les jours de la semaine. Schéma dessiné.](figures/ch02-cron.png)

Chaque champ accepte les mêmes écritures.

| Écriture | Sens | Exemple | Lecture |
|---|---|---|---|
| `*` | toutes les valeurs | `0 6 * * *` | tous les jours à 6 h |
| `a,b` | liste | `0 6,18 * * *` | à 6 h et à 18 h |
| `a-b` | plage | `0 6 * * 1-5` | à 6 h, du lundi au vendredi |
| `*/n` | pas | `*/15 8-18 * * *` | toutes les 15 minutes, de 8 h à 18 h |

Pour comprendre, rien ne vaut l'écriture d'un petit évaluateur : une fonction qui, pour une expression et une date, donne la **prochaine échéance**. Elle tient en une vingtaine de lignes (le code est dans `build/outils_ch02.py`). Pour chaque champ, elle calcule l'ensemble des valeurs permises (`*`, listes, plages, pas) ; puis elle parcourt les jours à partir de la date donnée et renvoie la première minute qui satisfait les cinq champs. Une règle mérite d'être connue : quand le jour du mois **et** le jour de la semaine sont tous deux précisés, le cron classique déclenche si **l'un ou l'autre** convient.

```python hide
from datetime import datetime, timedelta, timezone
from outils_ch02 import champ_cron, prochaine_echeance
```

Le test : à partir du mercredi 5 novembre 2025 à 10 h 17, quand se déclenchent nos quatre exemples ?

```python
depuis = datetime(2025, 11, 5, 10, 17)
for expr in ["0 6 3 * *", "0 6 * * 1", "*/15 8-18 * * 1-5", "30 7 1 * *"]:
    print(f"{expr:20s}", prochaine_echeance(expr, depuis), "|", prochaine_echeance(expr, prochaine_echeance(expr, depuis)))
```
<!--sortie-->
```text
0 6 3 * *            2025-12-03 06:00:00 | 2026-01-03 06:00:00
0 6 * * 1            2025-11-10 06:00:00 | 2025-11-17 06:00:00
*/15 8-18 * * 1-5    2025-11-05 10:30:00 | 2025-11-05 10:45:00
30 7 1 * *           2025-12-01 07:30:00 | 2026-01-01 07:30:00
```

Notre évaluateur raisonne comme le cron classique. La bibliothèque APScheduler, que nous utilisons juste après, propose aussi `CronTrigger.from_crontab`. On pourrait croire qu'elle donne les mêmes réponses. Comparons.

```python
from apscheduler.triggers.cron import CronTrigger
depuis_utc = depuis.replace(tzinfo=timezone.utc)
for expr in ["0 6 3 * *", "0 6 * * 1", "0 0 13 * 5"]:
    aps = CronTrigger.from_crontab(expr, timezone="UTC").get_next_fire_time(None, depuis_utc)
    print(f"{expr:12s} cron classique : {prochaine_echeance(expr, depuis)} | APScheduler : {aps.replace(tzinfo=None)}")
```
<!--sortie-->
```text
0 6 3 * *    cron classique : 2025-12-03 06:00:00 | APScheduler : 2025-12-03 06:00:00
0 6 * * 1    cron classique : 2025-11-10 06:00:00 | APScheduler : 2025-11-11 06:00:00
0 0 13 * 5   cron classique : 2025-11-07 00:00:00 | APScheduler : 2025-12-13 00:00:00
```

Les deux derniers résultats **diffèrent**, et ce n'est pas un bogue de notre évaluateur. Dans la version d'APScheduler utilisée ici (3.11), les numéros de jours de la semaine de `from_crontab` **commencent au lundi** (0 = lundi, donc `1` désigne le mardi), alors que le cron classique commence au dimanche ; et quand le jour du mois **et** le jour de la semaine sont tous deux précisés, APScheduler exige **les deux** (un 13 qui tombe le jour numéro 5 de sa propre numérotation, soit un samedi, d'où le 13 décembre), alors que le cron classique accepte **l'un ou l'autre** (le 13 **ou** un vendredi, d'où le vendredi 7 novembre).

> ⚠️ **Piège : deux « cron » qui ne se ressemblent pas.** Une expression recopiée d'un outil à un autre peut se déclencher un autre jour sans erreur. Deux précautions : écrire les jours **en toutes lettres** (`mon`, `tue`…) quand l'outil le permet, et **calculer les prochaines échéances** pour les lire avant de mettre en production. Vérifiez la convention dans la documentation de votre version.

Quelques conseils d'usage, qui épargnent des soirées de dépannage.

- **L'heure.** Choisissez un fuseau explicite (le plus sûr : UTC) et évitez les créneaux de la nuit du changement d'heure : à 2 h 30, certains jours n'existent pas et d'autres existent deux fois.
- **La marge.** Le fichier est « livré le 3 » : planifier le chargement le 3 à 6 h, c'est parier que la livraison est faite avant. On préfère un chargement plus tardif, ou, mieux, un pipeline qui **vérifie la présence du fichier** et réessaie plus tard (section 2.3).
- **Le propriétaire.** Chaque tâche planifiée a un nom, une personne responsable et une adresse où se plaindre. Une tâche sans propriétaire est une tâche qu'on découvrira le jour où elle casse.

### 2.2.4 Planifier depuis Python : APScheduler

Quand le planificateur du système n'est pas disponible, ou quand on veut que le calendrier fasse partie du programme, on peut planifier **depuis Python**. La bibliothèque **APScheduler** lance des tâches dans un fil d'exécution à part, selon un déclencheur (intervalle, cron, date unique). Pour l'illustrer sans attendre un mois, utilisons une échéance d'**une seconde** et laissons trois exécutions se produire avant d'arrêter proprement.

```python
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
tops, fini = [], threading.Event()

def tache():
    tops.append(time.monotonic())
    if len(tops) == 3:
        fini.set()

planif = BackgroundScheduler()
planif.add_job(tache, IntervalTrigger(seconds=1))
planif.start(); fini.wait(timeout=10); planif.shutdown(wait=True)
print(len(tops), "exécutions, écarts arrondis (s) :", [round(b - a) for a, b in zip(tops, tops[1:])])
```
<!--sortie-->
```text
3 exécutions, écarts arrondis (s) : [1, 1]
```

Trois détails de ce code comptent plus que la planification elle-même. D'abord, on **attend un signal** (`fini.wait`) plutôt qu'un délai fixe, pour que l'exemple soit fiable. Ensuite, on arrête avec `shutdown(wait=True)`, qui laisse finir la tâche en cours : un arrêt brutal pourrait couper un chargement en plein milieu. Enfin, le planificateur vit **dans le processus** : s'il s'arrête, plus rien ne se déclenche. C'est son principal défaut par rapport à cron, géré par le système.

Trois réglages d'APScheduler méritent d'être connus, car ils décident de ce qui arrive quand le calendrier **se heurte à la réalité**.

| Réglage | Question à laquelle il répond | Valeur prudente pour un chargement |
|---|---|---|
| `max_instances` | Que faire si la tâche précédente n'est pas finie quand l'échéance revient ? | `1` : on ne lance pas deux chargements en parallèle |
| `coalesce` | Plusieurs échéances manquées (machine éteinte) : en rejouer une seule, ou toutes ? | `True` : une seule suffit, car le chargement est idempotent |
| `misfire_grace_time` | De combien de temps une échéance en retard est-elle encore valable ? | quelques heures : un chargement tardif vaut mieux que pas de chargement |

Vérifions le premier. Une tâche lente (une seconde) est planifiée toutes les 0,4 seconde, avec `max_instances=1`. Elle ne doit jamais tourner en double, et les échéances qui tombent pendant qu'elle travaille doivent être **refusées** (et signalées, jamais perdues en silence).

```python hide-code
from apscheduler.events import EVENT_JOB_MAX_INSTANCES
etat = {"en_cours": 0, "max": 0, "refus": 0}

def lente():
    etat["en_cours"] += 1; etat["max"] = max(etat["max"], etat["en_cours"])
    time.sleep(1.0)
    etat["en_cours"] -= 1

planif = BackgroundScheduler()
planif.add_listener(lambda e: etat.update(refus=etat["refus"] + 1), EVENT_JOB_MAX_INSTANCES)
planif.add_job(lente, IntervalTrigger(seconds=0.4), max_instances=1)
planif.start(); time.sleep(2.6); planif.shutdown(wait=True)
print("jamais deux en même temps :", etat["max"] == 1, "| échéances refusées signalées :", etat["refus"] > 0)
```
<!--sortie-->
```text
jamais deux en même temps : True | échéances refusées signalées : True
```

### 2.2.5 Relancer et rattraper

Le calendrier a des trous : la machine était éteinte, le fichier n'est arrivé que le 9, le planificateur a planté. Un bon pipeline sait **combler les trous** sans qu'on lui dise lesquels. C'est le **rattrapage** (*backfill*).

Le principe est de **comparer ce qui devrait être chargé à ce qui l'a été**. Ce qui devrait l'être : la dernière version livrée de chaque mois du manifeste. Ce qui l'a été : les exécutions réussies, que notre chaîne enregistre dans une table `executions` (section 2.3). La différence est la liste de ce qu'il reste à faire.

Imaginons que le planificateur n'ait fonctionné que de janvier à mai, avant une panne de machine.

```python
h2 = P.Horloge("2025-06-04 06:00:00")
dernier = man.sort_values("date_livraison").groupby("mois").tail(1)
for _, f in dernier.head(5).iterrows():
    P.executer(ent2, os.path.join(DEPOT, f["fichier"]), int(f["lignes_annoncees"]), cl2, h2)
print(P.a_rattraper(ent2, DEPOT)[["mois", "fichier"]].to_string(index=False))
```
<!--sortie-->
```text
   mois                  fichier
2025-06    commandes_2025-06.csv
2025-07    commandes_2025-07.csv
2025-08    commandes_2025-08.csv
2025-09 commandes_2025-09_v2.csv
2025-10 commandes_2025-10_v2.csv
2025-11    commandes_2025-11.csv
2025-12    commandes_2025-12.csv
```

La liste est celle des sept mois de juin à décembre. Il suffit de les rejouer : comme le chargement est idempotent, on n'a pas à se demander si l'un d'eux avait été **partiellement** chargé.

```python hide-code
for _, f in P.a_rattraper(ent2, DEPOT).iterrows():
    P.executer(ent2, os.path.join(DEPOT, f["fichier"]), int(f["lignes_annoncees"]), cl2, h2)
total = ent2.execute("SELECT round(sum(montant), 2), count(*) FROM fait_ligne").fetchone()
print("à rattraper :", len(P.a_rattraper(ent2, DEPOT)), "| lignes chargées :", total[1], "| chiffre d'affaires TTC :", fr(total[0], 2), "€")
```
<!--sortie-->
```text
à rattraper : 0 | lignes chargées : 29827 | chiffre d'affaires TTC : 1 324 763,72 €
```

Après rattrapage, plus rien n'est à faire, et l'entrepôt contient **exactement** les 29 827 lignes d'origine et le chiffre d'affaires du volume III (1 324 763,72 €) : les lignes orphelines, les avoirs et les doublons ont été mis en quarantaine, et le total de ce qui reste est juste, au centime. La section 2.3 revient sur ce calcul de rapprochement.

> 💡 **Intuition : planifier, c'est facile ; rattraper, c'est ce qui fait la robustesse.** Un pipeline qui ne sait que « faire le travail du jour » dépend de sa propre ponctualité. Un pipeline qui sait « faire tout ce qui manque » se moque d'avoir raté trois rendez-vous.

### 2.2.6 Éviter les exécutions simultanées

Dernier danger : deux exécutions en même temps. Cela arrive plus souvent qu'on ne croit : un chargement qui dure plus longtemps que prévu et la tâche suivante qui démarre, un collègue qui relance à la main pendant que le planificateur tourne. Deux processus qui écrivent dans la même table donnent, au mieux, une erreur, au pire un état incohérent.

La parade est un **verrou**. Sous Linux, un verrou de fichier (`flock`) a l'avantage d'être **libéré automatiquement** si le processus meurt : pas de verrou orphelin qui bloquerait tout jusqu'à intervention humaine.

```python
import fcntl, contextlib

@contextlib.contextmanager
def verrou(chemin):
    with open(chemin, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("une exécution est déjà en cours")
        yield
```

Faisons-le jouer : une première exécution prend le verrou et travaille, une seconde essaie de démarrer pendant ce temps.

```python hide-code
chemin_verrou = os.path.join(os.path.dirname(ent2.execute("PRAGMA database_list").fetchone()[2]), "pipeline.verrou")
resultat, premier_demarre = {}, threading.Event()

def exec_a():
    with verrou(chemin_verrou):
        premier_demarre.set(); time.sleep(0.5); resultat["A"] = "terminée"

fil = threading.Thread(target=exec_a); fil.start(); premier_demarre.wait()
try:
    with verrou(chemin_verrou):
        resultat["B"] = "terminée"
except RuntimeError as e:
    resultat["B"] = "refusée : " + str(e)
fil.join()
print(resultat)
```
<!--sortie-->
```text
{'B': 'refusée : une exécution est déjà en cours', 'A': 'terminée'}
```

La seconde exécution est **refusée avec un message clair** plutôt que de s'exécuter en parallèle. Dans un vrai déploiement, le verrou est un fichier à un emplacement fixe (par exemple dans le dossier temporaire du système, au nom du pipeline) ; ici, il se trouve dans le dossier temporaire de l'entrepôt de démonstration, supprimé à la fin.

> 🧭 **En pratique : le tableau de ce qu'il faut régler avant la mise en production.**
> - **Qui** lance (un compte de service, pas un compte personnel) et **où** (une machine toujours allumée, sauvegardée).
> - **Quand**, dans quel fuseau, avec quelle marge après la livraison des fichiers.
> - **Comment on relance** : à la main, avec un mois en paramètre, sans rien casser.
> - **Que se passe-t-il si deux exécutions se chevauchent**, ou si l'une est interrompue.
> - **Qui est prévenu** quand ça échoue (section 2.3).

> ✅ **À retenir.**
> - Un pipeline est une suite d'**étapes** qui dépendent les unes des autres : un **graphe** orienté sans cycle.
> - Il se **paramètre** (mois, dossier, seuils) et se lance en **ligne de commande**, avec un code de sortie fiable et une option de **simulation**.
> - **cron** (ou le planificateur du système) lance ; APScheduler planifie depuis Python. Les conventions d'écriture diffèrent d'un outil à l'autre : **calculez les prochaines échéances** avant de faire confiance à une expression.
> - Le **rattrapage** compare « ce qui devrait être chargé » à « ce qui l'a été » ; il n'est sûr que si le chargement est **idempotent**.
> - Un **verrou** empêche deux exécutions simultanées ; préférez un verrou que le système libère si le processus meurt.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.4, exercices 2.5 à 2.7.
