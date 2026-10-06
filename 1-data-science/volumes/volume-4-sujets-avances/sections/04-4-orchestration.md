## ➕ 4.4 Orchestration

*Section complémentaire : elle prolonge 4.1 (le pipeline comme graphe) et ne conditionne pas la suite du chapitre.*

Jusqu'ici, chaque étape a été lancée à la main. En production, **les mêmes étapes tournent tous les jours** (extraire les clients du jour, valider, calculer les variables, scorer, publier) et il faut que quelqu'un s'occupe de ce qui peut mal tourner : une source indisponible, une étape qui échoue, un jour manqué à rattraper. Cette fonction s'appelle l'**orchestration** : un outil, l'**orchestrateur**, connaît le graphe des tâches, les déclenche à l'heure prévue dans le bon ordre, les relance en cas d'échec, garde une trace de ce qui s'est passé et alerte si besoin. Le plus connu est **Apache Airflow** ; il en existe d'autres (Prefect, Dagster, des services gérés par les fournisseurs de cloud, voir chapitre 6) et le principe est le même.

> 💡 **Intuition.** Un orchestrateur ne **calcule** rien : c'est un chef de chantier qui sait dans quel ordre les corps de métier doivent intervenir, qui rappelle l'électricien s'il n'est pas venu, et qui note ce qui est fait. Le travail lui-même (la validation, l'entraînement, le scoring) reste dans vos fonctions Python, SQL ou Spark.

### Les concepts : tâche, graphe, jour logique

- une **tâche** est une unité de travail qui réussit ou échoue (« valider les données du jour ») ;
- un **graphe de tâches** (DAG) dit quelle tâche dépend de quelle autre ; sans dépendance entre elles, deux tâches peuvent tourner **en parallèle** ;
- une **exécution** (*run*) est une instance du graphe pour **un jour logique** donné : « le traitement du 12 mars », lancé peut-être le 13 mars. La distinction est essentielle : le graphe reçoit **la date qu'il doit traiter**, pas la date du moment où il tourne ;
- chaque tâche d'une exécution a un **état** : planifiée, en cours, réussie, échouée, relancée, ou **ignorée** (parce qu'une tâche dont elle dépend a échoué).

L'ordre d'exécution se déduit du graphe : c'est un **tri topologique**, un ordre où chaque tâche vient après toutes celles dont elle dépend. La bibliothèque standard de Python en fournit un (`graphlib`). Reprenons le scoring quotidien de la boutique, avec une tâche d'alerte qualité qui dépend, comme le calcul des variables, de la validation :

```python
from graphlib import TopologicalSorter
deps = {"valider": {"extraire"}, "variables": {"valider"}, "alerte_qualite": {"valider"},
        "scorer": {"variables"}, "publier": {"scorer"}}
ts = TopologicalSorter(deps); ts.prepare()
while ts.is_active():
    prets = ts.get_ready(); print(sorted(prets)); ts.done(*prets)
```
<!--sortie-->
```text
['extraire']
['valider']
['alerte_qualite', 'variables']
['scorer']
['publier']
```

Chaque ligne est un **niveau** : les tâches d'un même niveau ne dépendent pas les unes des autres et peuvent tourner en même temps (ici, le calcul des variables et l'alerte qualité). C'est ce parallélisme que l'orchestrateur exploite, et c'est aussi ce qui rend la **dépendance explicite** précieuse : sans elle, on ne sait pas ce qui peut être relancé sans danger.

### Reprises, idempotence et rattrapage

Trois propriétés distinguent un pipeline « qui marche » d'un pipeline **qui tient en production**.

**Les reprises (*retries*).** Beaucoup d'échecs sont **transitoires** (une connexion qui saute, une base momentanément saturée) : relancer la tâche quelques secondes plus tard suffit. Si chaque tentative échoue indépendamment avec une probabilité $q$, la probabilité qu'au moins une des $r+1$ tentatives réussisse est
$$
1 - q^{\,r+1}.
$$
Pour $q = 0{,}1$ et deux reprises ($r = 2$), cela donne $1 - 0{,}1^{3} = 0{,}999$ : une panne transitoire fréquente devient presque invisible. On espace les tentatives de façon croissante (**attente exponentielle** : 30 s, 1 min, 2 min…) pour laisser le système se rétablir. Mais attention : une reprise ne guérit **que les pannes aléatoires**. Une erreur déterministe (une donnée invalide, un bug) échoue à chaque tentative et les reprises ne font que retarder l'alerte.

**L'idempotence.** Une tâche est **idempotente** si l'exécuter deux fois (ou dix) a le même effet que l'exécuter une fois. C'est la condition pour que reprises et rattrapages soient sans danger : si une tâche échoue à moitié puis est relancée, elle ne doit pas avoir laissé deux fois les mêmes lignes. On l'obtient presque toujours par un des trois moyens suivants : **écraser** la sortie du jour plutôt que lui ajouter des lignes (une partition par jour), faire un **upsert** (insérer ou mettre à jour selon une clé), ou écrire dans un fichier temporaire puis le **renommer** d'un coup (opération atomique).

**Le rattrapage (*backfill*).** Quand on met en service un nouveau pipeline, ou qu'on corrige une erreur, il faut **rejouer des jours passés**. Un orchestrateur sait lancer le graphe pour chaque jour logique d'une plage ; c'est ici que l'idempotence et le « jour logique » du paragraphe précédent paient.

### Un mini-orchestrateur exécutable

Airflow ne se lance pas dans ce livre (voir plus bas), mais **ses principes tiennent en une trentaine de lignes de Python**, et c'est la meilleure façon de les voir. Le petit orchestrateur de `build/outils_ch04.py` (classe `MiniOrchestrateur`) fait exactement ce qui précède : il parcourt les tâches dans l'ordre topologique, relance celles qui échouent (au plus 2 fois), marque « ignorée » toute tâche dont une dépendance a échoué, et tient un **journal** de chaque tentative. Nous déclarons les quatre tâches du scoring de chaque jour : chacune reçoit le **jour logique** en argument.

```python hide
ORCH = os.path.join(WORK, "orch"); os.makedirs(os.path.join(ORCH, "table"), exist_ok=True)
sc_pool = v2.predict_proba(Xpool)[:, 1]
CASSE, TRANSITOIRE, tentatives = {3}, {1: 2}, {}            # jour 3 : source cassée ; jour 1 : 2 pannes transitoires

def lot_du_jour(jour):
    return Xpool.iloc[jour * 40:(jour + 1) * 40]

def appel_source_instable(jour):
    tentatives[jour] = tentatives.get(jour, 0) + 1
    if tentatives[jour] <= TRANSITOIRE.get(jour, 0):
        raise ConnectionError("source injoignable")

def ecrire_brut(jour):
    lot = lot_du_jour(jour).copy()
    if jour in CASSE:
        lot["part_achats_promo"] = lot["part_achats_promo"] * 100       # bug de l'export : pourcentage au lieu de fraction
    lot.to_csv(f"{ORCH}/brut_{jour}.csv")

def lire_brut(jour):
    return pd.read_csv(f"{ORCH}/brut_{jour}.csv", index_col=0)

def ecrire_scores(jour):
    lot = lire_brut(jour)
    pd.DataFrame({"id": lot.index, "proba": v2.predict_proba(lot)[:, 1]}).to_csv(f"{ORCH}/scores_{jour}.csv", index=False)

def publier_partition(jour):                                   # idempotent : on écrase la partition du jour
    shutil.copy(f"{ORCH}/scores_{jour}.csv", f"{ORCH}/table/jour={jour}.csv")

def publier_ajout(jour):                                       # NON idempotent : on ajoute à la fin d'un fichier unique
    f = f"{ORCH}/table_unique.csv"
    pd.read_csv(f"{ORCH}/scores_{jour}.csv").to_csv(f, mode="a", header=not os.path.exists(f), index=False)

def lignes_table():
    import glob
    return sum(len(pd.read_csv(f)) for f in glob.glob(f"{ORCH}/table/*.csv"))
NUM("p_succes", 1 - 0.1 ** 3)
```
<!--sortie-->
```text
NUM p_succes 0.999
```

```python
orch = MiniOrchestrateur(reprises=2)

@orch.tache("extraire")
def extraire(jour):
    appel_source_instable(jour)                    # échoue deux fois le jour 1 (panne transitoire simulée)
    ecrire_brut(jour)
@orch.tache("valider", depend_de=["extraire"])
def valider(jour):
    assert lire_brut(jour)["part_achats_promo"].between(0, 1).all(), "part de promotions hors de [0, 1]"
@orch.tache("scorer", depend_de=["valider"])
def scorer(jour):
    ecrire_scores(jour)
@orch.tache("publier", depend_de=["scorer"])
def publier(jour):
    publier_partition(jour)
```

Lançons le graphe pour les six premiers jours. Le jour 1 subit deux pannes transitoires ; le jour 3, la source envoie un export cassé (la part de promotions en pourcentage, comme en 4.1).

```python
etats = {jour: orch.lancer(jour) for jour in range(6)}
journal = pd.DataFrame(orch.journal, columns=["jour", "tâche", "essai", "état"])
print(journal[((journal["jour"] == 1) & (journal["tâche"] == "extraire")) | ((journal["jour"] == 3) & (journal["tâche"] != "extraire"))].to_string(index=False))
```
<!--sortie-->
```text
 jour    tâche  essai                    état
    1 extraire      1 échec (ConnectionError)
    1 extraire      2 échec (ConnectionError)
    1 extraire      3                      ok
    3  valider      1  échec (AssertionError)
    3  valider      2  échec (AssertionError)
    3  valider      3  échec (AssertionError)
    3   scorer      0                 ignorée
    3  publier      0                 ignorée
```

Le jour 1, l'extraction a échoué deux fois puis réussi à la troisième tentative : **la reprise a absorbé la panne**. Le jour 3, la validation a échoué trois fois de suite (les reprises ne servent à rien contre une erreur déterministe) ; l'orchestrateur a alors **ignoré** les deux tâches suivantes plutôt que de scorer des données fausses. C'est le comportement voulu : un test de données qui échoue **bloque** la suite (4.1). Vue d'ensemble de l'état final de chaque tâche, jour par jour :

```python hide
nb_essais = journal.groupby(["jour", "tâche"])["essai"].max()
tab_etats = pd.DataFrame({t: [etats[j][t] for j in range(6)] for t in ["extraire", "valider", "scorer", "publier"]}, index=[f"jour {j}" for j in range(6)])
NUM("n_ok", int((tab_etats == "ok").sum().sum())); NUM("n_ignorees", int((tab_etats == "ignorée").sum().sum())); NUM("n_echecs", int((tab_etats == "échec").sum().sum()))
assert etats[1]["extraire"] == "ok" and etats[3]["valider"] == "échec" and etats[3]["publier"] == "ignorée"
```
<!--sortie-->
```text
NUM n_ok 21
NUM n_ignorees 2
NUM n_echecs 1
```

```python hide-code
print(tab_etats.to_string())
```
<!--sortie-->
```text
       extraire valider   scorer  publier
jour 0       ok      ok       ok       ok
jour 1       ok      ok       ok       ok
jour 2       ok      ok       ok       ok
jour 3       ok   échec  ignorée  ignorée
jour 4       ok      ok       ok       ok
jour 5       ok      ok       ok       ok
```

Sur 24 tâches, 21 ont réussi, 1 a échoué et 2 ont été ignorées : l'incident est **circonscrit** à un jour et laisse les autres intacts, les jours étant indépendants.

### Corriger et rattraper : l'idempotence à l'épreuve

La source est réparée ; il reste à **rejouer le jour 3**, et pour plus de sûreté on rejoue même toute la période. Le mini-orchestrateur est inchangé : c'est la propriété des tâches (écrasement de la partition du jour) qui empêche les doublons. Pour s'en convaincre, comparons à une publication **par ajout**, non idempotente :

```python hide
CASSE.clear()                                                       # la source est corrigée
etats3 = orch.lancer(3)
lignes_apres_correction = lignes_table()
for j in range(6):
    orch.lancer(j)                                                  # on rejoue tout : rien ne doit changer
lignes_apres_rejeu = lignes_table()
for _ in range(2):
    publier_ajout(0)                                                # même jour publié deux fois par ajout
lignes_ajout = len(pd.read_csv(f"{ORCH}/table_unique.csv"))
NUM("lignes_attendues", 6 * 40); NUM("lignes_corrigees", lignes_apres_correction); NUM("lignes_rejeu", lignes_apres_rejeu); NUM("lignes_ajout", lignes_ajout)
assert etats3["publier"] == "ok" and lignes_apres_correction == 240 == lignes_apres_rejeu and lignes_ajout == 80
```
<!--sortie-->
```text
NUM lignes_attendues 240
NUM lignes_corrigees 240
NUM lignes_rejeu 240
NUM lignes_ajout 80
```

Après la correction, la table publiée contient 240 lignes (6 jours × 40 clients = 240, comme attendu) ; **rejouer les six jours** n'y change rien (240 lignes). À l'inverse, publier deux fois le seul jour 0 par ajout donne 80 lignes pour 40 clients : chaque reprise aurait **dupliqué** les données. C'est pourquoi on conçoit les tâches pour qu'elles soient idempotentes **avant** de les confier à un orchestrateur.

```python hide
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.0, 1.15]})
a.set_xlim(0, 6); a.set_ylim(0, 5); a.axis("off")
pos = {"extraire": (1.0, 2.5), "valider": (2.3, 2.5), "scorer": (3.6, 2.5), "publier": (4.9, 2.5)}
coul = {"ok": AQUA, "échec": ROUGE, "ignorée": MUET}
for t, (x, y) in pos.items():
    e = etats[3][t]
    boite(a, x, y, 1.05, 0.9, t, coul[e], taille=8.5, plein=(e != "ignorée"))
    a.text(x, y - 0.75, e, ha="center", fontsize=8, color=coul[e])
for (t1, p1), (t2, p2) in zip(list(pos.items())[:-1], list(pos.items())[1:]):
    fleche(a, (p1[0] + 0.53, p1[1]), (p2[0] - 0.53, p2[1]))
a.set_title("Le jour 3 : la validation échoue, la suite est ignorée", fontsize=10)
taches = ["extraire", "valider", "scorer", "publier"]
for j in range(6):
    for k, t in enumerate(taches):
        e = etats[j][t]
        b.add_patch(plt.Rectangle((j, 3 - k), 0.92, 0.88, color=coul[e], alpha=0.85 if e != "ignorée" else 0.35))
        n_ess = int(nb_essais.get((j, t), 0))
        if n_ess > 1:
            b.text(j + 0.46, 3 - k + 0.44, f"{n_ess} essais", ha="center", va="center", fontsize=8, color="white")
b.set_xlim(0, 6); b.set_ylim(0, 4); b.set_xticks(np.arange(6) + 0.46); b.set_xticklabels([f"jour {j}" for j in range(6)], fontsize=8.5)
b.set_yticks(3 - np.arange(4) + 0.44); b.set_yticklabels(taches, fontsize=9)
b.set_title("État final de chaque tâche (vert : réussie ; rouge : échec ; gris : ignorée)", fontsize=9.5)
for s in ("top", "right", "left", "bottom"):
    b.spines[s].set_visible(False)
b.tick_params(length=0); b.grid(False)
fig.tight_layout(); style.save(fig, "ch04-orchestration.png")
```
<!--sortie-->
```text
figure : ch04-orchestration.png
```

![À gauche : le graphe du jour 3, où la validation a échoué et les deux tâches suivantes sont ignorées. À droite : l'état final de chaque tâche pour les six premiers jours (le nombre d'essais est indiqué quand il dépasse un) avant la correction.](figures/ch04-orchestration.png)

### Les outils réels

Dans un projet réel, on n'écrit pas son orchestrateur ; on déclare le même graphe dans un outil. Voici le même scoring dans **Airflow** et **Prefect**, **non exécutés** (ces bibliothèques ne sont pas installées sur la machine qui a produit ce livre) : leurs interfaces évoluent d'une version majeure à l'autre, **à vérifier dans la documentation** de la version utilisée.

```python noexec
# Airflow — non exécuté (ne pas copier tel quel : l'API varie selon la version)
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=True,
     default_args={"retries": 2})
def scoring_quotidien():
    @task
    def extraire(ds=None): ...         # ds : le jour logique, fourni par Airflow
    @task
    def valider(ds=None): ...
    extraire() >> valider()            # ">>" : « valider dépend de extraire »

scoring_quotidien()
```

```python noexec
# Prefect — non exécuté
from prefect import flow, task

@task(retries=2, retry_delay_seconds=30)
def extraire(jour): ...

@flow
def scoring_quotidien(jour):
    extraire(jour)
```

Le paramètre `catchup=True` d'Airflow est le rattrapage : si le graphe est activé avec une date de début passée, il lance une exécution pour **chaque jour manqué**. Un autre outil, **dbt**, orchestre des transformations SQL : chaque modèle est une requête, et les dépendances sont déclarées par la fonction `ref` ; dbt en déduit le graphe, l'ordre et les tests de données (colonne non nulle, valeurs uniques).

```sql noexec
-- modèle dbt « scores_jour » — non exécuté
select c.id_client, s.proba, s.jour
from {{ ref('clients_valides') }} c
join {{ ref('scores_bruts') }} s using (id_client)
```

> 🧭 **En pratique.** On ne choisit pas un orchestrateur pour ses fonctions mais pour **ce qu'on sait exploiter**. Pour un seul pipeline quotidien, une simple tâche planifiée (`cron`) avec des journaux et une alerte sur code de retour suffit et sera plus fiable qu'un système lourd mal administré. L'orchestrateur devient utile quand les **dépendances** se multiplient, quand on doit **rattraper** des jours, ou quand plusieurs équipes partagent des données. Et l'orchestrateur lui-même doit être **supervisé** : un planificateur arrêté sans que personne ne le sache produit le pire des incidents, celui où rien ne tourne et rien n'alerte.

> 📒 **Pour pratiquer.** Le cahier propose de construire un pipeline de scoring avec reprises et rattrapage (application 4.5) et de rendre idempotente une tâche qui duplique ses sorties (exercice 4.6).
