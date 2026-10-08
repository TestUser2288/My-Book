## 2.4 ➕ Pour aller plus loin : dbt, Airflow, Power Automate et la planification avec Python

> 🧭 Section optionnelle. Elle décrit des outils que ce livre **n'exécute pas** (dbt, Airflow, Power Automate) : ce qui en est dit vient de leur documentation publique, sans essai ici, et les noms de paramètres comme la syntaxe changent d'une version à l'autre. Pour comprendre leur principe malgré tout, vous écrirez **deux jouets** qui, eux, s'exécutent.

Notre pipeline tient dans un script, un cron et une table des exécutions. C'est suffisant pour une boutique. Quand les chaînes se multiplient (vingt sources, trois équipes, des tableaux de bord qui dépendent les uns des autres), les mêmes besoins reviennent et on les confie à des outils dédiés.

### 2.4.1 Ce que cron ne sait pas faire

| Besoin | cron + script | Outil d'orchestration |
|---|---|---|
| **Dépendances** entre tâches (la tâche C attend A **et** B) | à écrire à la main | déclarées dans un graphe, respectées par le planificateur |
| **Reprise** au point d'échec | à écrire à la main | « relancer à partir de la tâche en échec » |
| **Historique** et interface | un journal, une table | interface qui montre chaque exécution, ses durées, ses journaux |
| **Rattrapage** de dates passées | à écrire à la main (section 2.2.5) | intégré (on demande « rejoue le 1er janvier au 31 mars ») |
| **Alertes**, relances automatiques | à écrire à la main | réglages par tâche |
| **Parallélisme**, plusieurs machines | difficile | prévu |
| **Secrets**, connexions | variables d'environnement | coffre intégré ou lié à un coffre |

La contrepartie est réelle : un orchestrateur est un **système de plus à installer, surveiller, mettre à jour et sécuriser**. Pour dix tâches simples, il coûte plus qu'il ne rapporte.

### 2.4.2 Airflow : planifier et superviser des graphes de tâches

**Apache Airflow** est un orchestrateur libre. On y décrit un **DAG** (le graphe orienté acyclique de la section 2.2.1) en Python : chaque nœud est une **tâche**, créée à partir d'un **opérateur** (exécuter une fonction Python, une commande, une requête SQL…), et les dépendances s'écrivent avec un opérateur `>>`. Le planificateur lance les exécutions selon un calendrier, un serveur web montre l'état de chaque tâche pour chaque date, et chaque exécution est associée à une **date logique** : on peut donc demander au système de rejouer les dates passées (*catchup*, *backfill*).

Voici l'allure d'un DAG pour notre chaîne. **Ce code n'est pas exécuté ici** et la syntaxe (en particulier le paramètre de calendrier) varie selon la version : il sert à montrer la forme, pas à être recopié.

```python noexec
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG("commandes_mensuelles", start_date=datetime(2025, 1, 1), schedule="0 6 3 * *", catchup=True, max_active_runs=1) as dag:
    extraire = PythonOperator(task_id="extraire", python_callable=extraire_fichier)
    transformer = PythonOperator(task_id="transformer", python_callable=transformer_lignes)
    charger = PythonOperator(task_id="charger", python_callable=charger_entrepot, retries=3)
    controler = PythonOperator(task_id="controler", python_callable=controler_chargement)
    extraire >> transformer >> charger >> controler
```

Retrouvez, dans ces lignes, des notions de la section 2.2 : l'expression cron (`schedule`), l'exécution unique à la fois (`max_active_runs`), le rattrapage (`catchup`), les reprises (`retries`) et le graphe de dépendances (`>>`). Ce que l'outil apporte, ce n'est pas une idée nouvelle : c'est la **tuyauterie** (interface, historique, reprise ciblée, alertes) qu'on aurait dû écrire. Ce qu'il ne fait **pas** : il n'écrit pas les tâches, et un DAG dont les tâches ne sont pas idempotentes se rejoue mal avec Airflow comme sans lui.

### 2.4.3 dbt : la transformation en SQL, testée et documentée

**dbt** (*data build tool*) s'occupe d'une seule partie de la chaîne, la transformation **dans l'entrepôt** (la lettre T de l'ELT de la section 2.1.6). On écrit des **modèles** : chacun est un fichier SQL qui contient un seul `SELECT`. Un modèle désigne ceux dont il dépend par `{{ ref('nom') }}` ; dbt en déduit l'**ordre de construction** et le **graphe de lignage** (quelle table dépend de laquelle), puis crée les tables ou les vues. On peut y attacher des **tests** (unicité, absence de valeurs vides, valeurs permises, référence vers une autre table) et de la **documentation**.

**Non exécuté ici**, voici l'allure d'un modèle et du fichier de tests qui l'accompagne.

```sql noexec
-- models/ca_mois.sql
{{ config(materialized='table') }}
select strftime(date_commande, '%Y-%m') as mois, canal, sum(montant) as ca_ttc
from {{ ref('stg_lignes') }}
group by 1, 2
```

```yaml noexec
# models/ca_mois.yml
models:
  - name: ca_mois
    columns:
      - name: ca_ttc
        tests: [not_null]
```

Les modèles peuvent être matérialisés en **vue** (calculée à la lecture), en **table** (recalculée à chaque exécution), ou en table **incrémentale** (on n'ajoute que les nouvelles lignes). Ce dernier mode retrouve **exactement** le piège de la section 2.1.4 : s'il se fonde sur « les lignes plus récentes que la dernière date chargée », il rate les **corrections** de lignes anciennes, et les équipes ajoutent en pratique une fenêtre de recouvrement ou une clé de fusion. Un outil ne vous dispense pas de comprendre le problème qu'il résout.

### 2.4.4 Power Automate et les outils « bas code »

**Power Automate** (et ses équivalents) est un outil de **flux** à construire avec des blocs, sans écrire de code : un **déclencheur** (« un e-mail arrive avec une pièce jointe », « un fichier est déposé », « tous les lundis à 7 h »), puis une suite d'**actions** (enregistrer la pièce jointe dans un dossier, ajouter une ligne dans un tableau, envoyer un message) reliées par des **connecteurs** à d'autres services. Pour un besoin simple (« quand le fichier arrive, le copier dans le dossier partagé et prévenir l'équipe »), il va plus vite qu'un script, et il est maniable par des personnes qui ne programment pas.

Ses limites sont celles de tous les outils graphiques : les transformations lourdes y sont pénibles, les licences et quotas comptent, le suivi de versions et les tests y sont moins naturels qu'avec du code, et un flux construit par une personne qui part devient vite **opaque**. Une bonne règle : s'en servir pour **déclencher et acheminer** (déposer, notifier, relayer), et garder le **calcul** dans du code versionné et testé. *Cet outil n'est pas exécuté ici, et son interface n'est pas reproduite : vérifiez ses possibilités dans la documentation de votre version.*

### 2.4.5 Premier jouet : un exécuteur de graphe

Pour comprendre ce que fait un orchestrateur, écrivons-en un de quelques lignes. Il parcourt le graphe dans l'ordre (le module `graphlib` vu en 2.2.1), exécute chaque tâche, **saute** celles dont une précédente a échoué, et sait **reprendre** en ne relançant que ce qui n'est pas terminé.

```python
def lancer_graphe(graphe, actions, etat=None):
    etat = dict(etat or {})
    for tache in TopologicalSorter(graphe).static_order():
        if etat.get(tache) == "ok":
            continue
        if any(etat.get(p) != "ok" for p in graphe.get(tache, ())):
            etat[tache] = "ignorée"
            continue
        try:
            actions[tache]()
            etat[tache] = "ok"
        except Exception:
            etat[tache] = "échec"
    return etat
```

Utilisons-le sur les sept étapes de la section 2.2 : chaque action note son nom dans une liste, et l'entrepôt est **verrouillé** au moment de charger.

```python hide-code
appels = []
def action(nom, panne=False):
    def faire():
        appels.append(nom)
        if panne:
            raise RuntimeError("entrepôt verrouillé")
    return faire

actions = {t: action(t) for t in GRAPHE} | {"charger": action("charger", panne=True)}
etat1 = lancer_graphe(GRAPHE, actions)
print("exécutées :", appels, "\nétat :", etat1)
```
<!--sortie-->
```text
exécutées : ['repérer', 'extraire', 'transformer', 'quarantaine', 'charger'] 
état : {'repérer': 'ok', 'extraire': 'ok', 'transformer': 'ok', 'quarantaine': 'ok', 'charger': 'échec', 'contrôler': 'ignorée', 'publier': 'ignorée'}
```

Le chargement a échoué ; le contrôle et la publication, qui en dépendent, sont **ignorés** : on ne publie pas sur un chargement qui n'a pas eu lieu. La quarantaine, indépendante du chargement, est faite. Une fois la panne réparée, on relance **avec l'état précédent**.

```python
appels.clear()
actions["charger"] = action("charger")
etat2 = lancer_graphe(GRAPHE, actions, etat1)
print("relancées :", appels, "\nétat :", etat2)
```
<!--sortie-->
```text
relancées : ['charger', 'contrôler', 'publier'] 
état : {'repérer': 'ok', 'extraire': 'ok', 'transformer': 'ok', 'quarantaine': 'ok', 'charger': 'ok', 'contrôler': 'ok', 'publier': 'ok'}
```

```python hide
positions = {"repérer": (0, 0.5), "extraire": (2, 0.5), "transformer": (4, 0.5), "quarantaine": (6, -0.5), "charger": (6, 1.0), "contrôler": (8, 1.0), "publier": (10, 1.0)}
P.fig_graphe(GRAPHE, etat1, "ch02-graphe-panne.png", positions, "Après la panne du chargement : ✓ terminée, ✗ en échec, – ignorée (une tâche précédente a échoué)")
```
<!--sortie-->
```text
figure : ch02-graphe-panne.png
```

![L'état du graphe après la panne du chargement : les trois premières étapes et la quarantaine sont terminées (✓), le chargement est en échec (✗), le contrôle et la publication sont ignorés (–). La couleur et le symbole disent la même chose. Schéma dessiné à partir de l'état réel du petit exécuteur.](figures/ch02-graphe-panne.png)

Seules les tâches **non terminées** sont relancées : c'est le « relancer à partir de l'échec » que proposent les orchestrateurs. Notre jouet n'a pourtant **ni parallélisme** (il exécute une tâche à la fois), **ni mémoire** (l'état disparaît avec le programme), **ni interface**, **ni reprise automatique**. Il montre le principe, il ne remplace rien.

### 2.4.6 Second jouet : des modèles SQL avec `ref()`

L'idée de dbt tient, elle aussi, en quelques lignes : des modèles écrits en SQL, un repérage des `ref('...')` qui donne l'ordre de construction, des tests simples. Écrivons-la sur notre entrepôt. Quatre modèles : une vue de base, le chiffre d'affaires par jour, par mois, et par catégorie de produit et par mois.

```python
MODELES = {
    "stg_lignes": "SELECT id_ligne, date_commande, canal, id_produit, montant FROM fait_ligne",
    "ca_jour": "SELECT date_commande, canal, sum(montant) AS ca_ttc FROM {{ ref('stg_lignes') }} GROUP BY ALL",
    "ca_mois": "SELECT strftime(date_commande, '%Y-%m') AS mois, canal, sum(ca_ttc) AS ca_ttc FROM {{ ref('ca_jour') }} GROUP BY ALL",
    "ca_categorie_mois": """SELECT strftime(l.date_commande, '%Y-%m') AS mois, p.categorie, sum(l.montant) AS ca_ttc
                            FROM {{ ref('stg_lignes') }} l JOIN dim_produit p USING (id_produit) GROUP BY ALL""",
}
ordre, compile_sql = P.construire_modeles(ent3, MODELES)
print("ordre de construction :", ordre)
print(compile_sql["ca_jour"])
```
<!--sortie-->
```text
ordre de construction : ['stg_lignes', 'ca_jour', 'ca_categorie_mois', 'ca_mois']
SELECT date_commande, canal, sum(montant) AS ca_ttc FROM stg_lignes GROUP BY ALL
```

Les `{{ ref('...') }}` ont servi deux fois : à **ordonner** les modèles (aucun n'est construit avant ceux dont il dépend) et à être remplacés par le nom de la vue. Le **lignage** se lit directement dans ces références.

```python hide
graphe_modeles = {"stg_lignes": {"fait_ligne"}, "ca_jour": {"stg_lignes"}, "ca_mois": {"ca_jour"}, "ca_categorie_mois": {"stg_lignes", "dim_produit"}, "fait_ligne": set(), "dim_produit": set()}
pos_m = {"fait_ligne": (0, 0.6), "dim_produit": (0, -0.7), "stg_lignes": (2, 0.6), "ca_jour": (4, 1.0), "ca_mois": (6, 1.0), "ca_categorie_mois": (6, -0.4)}
P.fig_graphe(graphe_modeles, {"fait_ligne": "ok", "dim_produit": "ok"}, "ch02-lignage-modeles.png", pos_m, "Le lignage des quatre modèles (✓ : tables de l'entrepôt)", largeur=9.6, hauteur=3.4)
```
<!--sortie-->
```text
figure : ch02-lignage-modeles.png
```

![Le lignage des quatre modèles : les modèles bleus se calculent à partir des tables de l'entrepôt (vertes). Le graphe est déduit des références `ref()` écrites dans le SQL. Schéma dessiné.](figures/ch02-lignage-modeles.png)

Restent les **tests**. Deux suffisent à comprendre : « aucune clé en double » et « aucune valeur vide ». Appliquons-les aux modèles, puis à un modèle **fautif** qui, par une erreur d'union, reprend deux fois les lignes du canal `Site`.

```python hide-code
TESTS = {"ca_mois": ["unique:mois,canal", "non_nul:ca_ttc"], "ca_categorie_mois": ["unique:mois,categorie"]}
for modele, tests in TESTS.items():
    print(modele, {t: P.tester_modele(ent3, modele, t) for t in tests})
ent3.execute("CREATE OR REPLACE VIEW stg_faux AS SELECT * FROM fait_ligne UNION ALL SELECT * FROM fait_ligne WHERE canal = 'Site'")
print("stg_faux", {"unique:id_ligne": P.tester_modele(ent3, "stg_faux", "unique:id_ligne")})
```
<!--sortie-->
```text
ca_mois {'unique:mois,canal': 0, 'non_nul:ca_ttc': 0}
ca_categorie_mois {'unique:mois,categorie': 0}
stg_faux {'unique:id_ligne': 13928}
```

Les modèles corrects passent (zéro ligne en défaut), le modèle fautif échoue : il a **dupliqué** des lignes, et le test d'unicité l'a vu avant qu'un tableau de bord n'affiche un chiffre d'affaires gonflé. C'est l'essentiel de ce que dbt apporte : des transformations **versionnées**, **ordonnées automatiquement** et **testées à chaque exécution**.

> ⚠️ **Piège : l'outil ne remplace pas le jugement.** Un test « unique » passe sur un modèle qui contient une somme **fausse**. Les tests attrapent des catégories d'erreurs, pas toutes ; les rapprochements de la section 2.3.5 (lignes et montants conservés, retombée sur une autre source) restent indispensables.

### 2.4.7 Choisir

| Votre situation | Raisonnable |
|---|---|
| Un ou deux pipelines, un petit entrepôt, vous seul | un script, cron ou APScheduler, une table des exécutions (ce chapitre) |
| Beaucoup de transformations SQL dans un entrepôt, plusieurs analystes | un outil de transformation comme **dbt** : ordre, tests, documentation partagés |
| Des dizaines de tâches dépendantes, des équipes, de l'historique à rejouer | un **orchestrateur** comme Airflow (ou un service géré équivalent) |
| Un besoin simple de déclenchement entre applications, sans programmeur | un outil **bas code** comme Power Automate, pour acheminer plus que pour calculer |

Dans tous les cas, la qualité d'une chaîne tient moins à l'outil qu'à ses **propriétés** : tâches idempotentes, contrôles avant et après, journal et alertes, propriétaire désigné.

> ✅ **À retenir.**
> - Un orchestrateur apporte la **tuyauterie** (dépendances, reprise ciblée, historique, rattrapage, alertes) ; il n'apporte **ni** l'idempotence **ni** les contrôles.
> - **Airflow** décrit des graphes de tâches en Python ; **dbt** gère les transformations SQL (ordre déduit des `ref()`, tests, lignage) ; les outils **bas code** acheminent plus qu'ils ne calculent. *Aucun n'est exécuté dans ce livre.*
> - Deux jouets écrits en quelques lignes (un exécuteur de graphe, des modèles SQL avec `ref()`) suffisent à comprendre le principe, sans en avoir ni la solidité ni les fonctions.
> - Plus d'outils, c'est plus de systèmes à maintenir : on n'en ajoute que si le besoin est réel.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.11.
