# Chapitre 2 : ETL et automatisation des flux de travail — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 2 : on y **lit** des livraisons de fichiers sans les modifier, on **écrit** des règles et une quarantaine, on **prouve** qu'un chargement est idempotent, on **pilote** un pipeline en ligne de commande, on **lit un journal** pour trouver la panne, on **branche** des contrôles et des alertes, on **construit** de petits outils d'orchestration, et on **lit** une API puis on **envoie** un rapport. Le cahier est autonome : il recharge ses données et importe les briques du pipeline depuis `build/outils_ch02.py` (version complète de ce que le livre construit pas à pas). Tout est **simulé**, hors ligne : l'entrepôt est un fichier DuckDB temporaire, les serveurs (API, e-mail) sont locaux et arrêtés dans le même bloc.

```python
import os, sys, io, re, json, time, logging, warnings, subprocess
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
logging.getLogger("apscheduler").setLevel(logging.CRITICAL)
sys.path.insert(0, "build")
import outils_ch02 as P
from outils_ch02 import fr

D = os.environ["DONNEES"]
DEPOT = os.path.join(D, "ch02-depot")
man = P.manifeste(DEPOT)
clients = set(pd.read_csv(os.path.join(D, "clients.csv"))["id_client"])
VERITE = P.verite(DEPOT)
derniers = man.sort_values("date_livraison").groupby("mois").tail(1)          # la dernière version livrée de chaque mois

def chemin(fichier):
    return os.path.join(DEPOT, fichier)

print(len(man), "fichiers,", man["mois"].nunique(), "mois,", len(clients), "clients | total attendu :", fr(VERITE["total_original"], 2), "€")
```
<!--sortie-->
```text
15 fichiers, 12 mois, 6000 clients | total attendu : 1 324 763,72 €
```

## Applications

### Application 2.1 — Lire une livraison sans la modifier (section 2.1)

**Objectif.** Lire des fichiers de formats différents en gardant tout en texte, détecter un encodage, et voir à quoi ressemble un mauvais décodage.

**Étape 1 — lire en texte.** On lit le fichier de juin avec la fonction du pipeline et on compare avec le nombre de lignes annoncé.

```python
f = derniers[derniers["mois"] == "2025-06"].iloc[0]
df = P.extraire(chemin(f["fichier"]))
print(f["fichier"], "|", len(df), "lignes lues,", f["lignes_annoncees"], "annoncées | types :", df.dtypes.astype(str).unique().tolist())
print(df.head(3).to_string(index=False))
```
<!--sortie-->
```text
commandes_2025-06.csv | 2333 lignes lues, 2333 annoncées | types : ['str']
id_ligne id_commande date_commande id_client   canal id_produit quantite montant
   64650       28036    2025-06-01      3961 Réseaux         43        2   49.24
   64651       28036    2025-06-01      3961 Réseaux         69        1    8.14
   64652       28036    2025-06-01      3961 Réseaux         50        1   73.03
```

**Étape 2 — l'encodage.** Le fichier d'août n'est pas en UTF-8. Lisons ses octets, essayons de les décoder en UTF-8, puis en `cp1252`.

```python
octets = open(chemin("commandes_2025-08.csv"), "rb").read()
try:
    octets.decode("utf-8")
except UnicodeDecodeError as e:
    print("UTF-8 impossible :", str(e)[:60])
print("cp1252 : canaux lus →", sorted(set(pd.read_csv(io.StringIO(octets.decode("cp1252")))["canal"])))
```
<!--sortie-->
```text
UTF-8 impossible : 'utf-8' codec can't decode byte 0xe9 in position 1828: inval
cp1252 : canaux lus → ['Boutique', 'Réseaux', 'Site']
```

**Étape 3 — l'erreur silencieuse.** Décoder en `latin-1` ou en UTF-8 avec remplacement ne lève aucune erreur : on obtient seulement un texte faux. Comptons les caractères de remplacement.

```python
faux = octets.decode("utf-8", errors="replace")
print("caractères de remplacement :", faux.count("�"), "| « Réseaux » correctement lu :", faux.count("Réseaux"), "fois")
```
<!--sortie-->
```text
caractères de remplacement : 212 | « Réseaux » correctement lu : 0 fois
```

*Ce qu'il faut retenir.* Un décodage qui ne lève pas d'erreur n'est pas un décodage correct : on vérifie les **valeurs** (liste de canaux connus), pas seulement l'absence d'exception.

### Application 2.2 — Contrat de données et quarantaine (section 2.1)

**Objectif.** Appliquer la transformation du chapitre à tous les mois, compter les rejets par motif et par mois, puis **écrire une règle supplémentaire**.

**Étape 1 — les rejets de l'année.** Une ligne par mois, une colonne par motif.

```python
lignes = []
for _, f in derniers.iterrows():
    v, r = P.transformer(P.extraire(chemin(f["fichier"])), clients)
    lignes.append({"mois": f["mois"], **r["motif"].value_counts().to_dict(), "valides": len(v)})
rejets_mois = pd.DataFrame(lignes).fillna(0).set_index("mois").astype(int)
print(rejets_mois.to_string())
```
<!--sortie-->
```text
         client inconnu  montant négatif  valides  doublon exact
mois                                                            
2025-01               1                1     2225              0
2025-02               0                1     1711              0
2025-03               4                1     2023              0
2025-04               2                1     2225              0
2025-05               1                0     2387              0
2025-06               2                1     2330              0
2025-07               0                3     2240              0
2025-08               3                1     1803              0
2025-09               1                0     2521              0
2025-10               1                0     2644              0
2025-11               0                0     3459             25
2025-12               3                0     4259              0
```

**Étape 2 — une règle de plus : la date doit être dans le mois du fichier.** Aucun fichier du dépôt ne la viole ; on la teste donc sur un cas fabriqué, en décalant les dates de quarante jours.

```python
def hors_mois(valides, mois):
    return valides["date_commande"].dt.strftime("%Y-%m") != mois

v, _ = P.transformer(P.extraire(chemin("commandes_2025-04.csv")), clients)
decale = v.assign(date_commande=v["date_commande"] + pd.Timedelta(days=40))
print("fichier intact :", int(hors_mois(v, "2025-04").sum()), "ligne(s) hors mois | dates décalées :", int(hors_mois(decale, "2025-04").sum()), "lignes hors mois")
```
<!--sortie-->
```text
fichier intact : 0 ligne(s) hors mois | dates décalées : 2225 lignes hors mois
```

*Ce qu'il faut retenir.* Une règle de validité se **teste sur un cas où l'on connaît la réponse** : sur des données propres, elle ne dit rien et l'on ne sait pas si elle fonctionne.

### Application 2.3 — Rendre un chargement idempotent (section 2.1)

**Objectif.** Comparer trois stratégies de chargement (ajout, fusion, remplacement de partition) en les rejouant deux fois.

**Étape 1 — l'ajout simple double.** On charge février deux fois dans une table sans clé.

```python
ent = P.nouvel_entrepot(); P.charger_dimensions(ent)
ent.execute("CREATE TABLE naif AS SELECT * FROM fait_ligne WHERE false")
vf, _ = P.transformer(P.extraire(chemin("commandes_2025-02.csv")), clients)
lot = vf.assign(fichier="commandes_2025-02.csv")[P.COLS + ["fichier"]]
ent.register("lot", lot)
for _ in range(2):
    ent.execute("INSERT INTO naif SELECT * FROM lot")
print("lignes valides :", len(vf), "| lignes dans la table après deux chargements :", ent.execute("SELECT count(*) FROM naif").fetchone()[0])
```
<!--sortie-->
```text
lignes valides : 1711 | lignes dans la table après deux chargements : 3422
```

**Étape 2 — la fusion et le remplacement de partition.** Deux entrepôts, deux stratégies, deux chargements chacun ; on compare les empreintes.

```python
def charger_partition(con, v, fichier, mois):
    con.execute("DELETE FROM fait_ligne WHERE strftime(date_commande, '%Y-%m') = ?", [mois])
    con.register("lot2", v.assign(fichier=fichier)[P.COLS + ["fichier"]])
    con.execute("INSERT INTO fait_ligne SELECT * FROM lot2")

A, B = P.nouvel_entrepot(), P.nouvel_entrepot()
for _ in range(2):
    P.charger(A, vf, "commandes_2025-02.csv")
    charger_partition(B, vf, "commandes_2025-02.csv", "2025-02")
print("fusion :", P.empreinte(A)[:2], "| partition :", P.empreinte(B)[:2], "| empreintes identiques :", P.empreinte(A) == P.empreinte(B))
```
<!--sortie-->
```text
fusion : (1711, 72642.44) | partition : (1711, 72642.44) | empreintes identiques : True
```

**Étape 3 — là où elles diffèrent.** Si le renvoi d'un mois **contient moins de lignes** que le premier fichier (une ligne a été retirée à la source), la fusion garde l'ancienne ligne, et le remplacement de partition la supprime. Vérifions.

```python
renvoi = vf.iloc[5:]                                   # le renvoi n'a plus les cinq premières lignes
P.charger(A, renvoi, "renvoi.csv"); charger_partition(B, renvoi, "renvoi.csv", "2025-02")
print("lignes après le renvoi — fusion :", P.empreinte(A)[0], "| partition :", P.empreinte(B)[0], "| lignes du renvoi :", len(renvoi))
```
<!--sortie-->
```text
lignes après le renvoi — fusion : 1711 | partition : 1706 | lignes du renvoi : 1706
```

*Ce qu'il faut retenir.* La fusion **ne supprime jamais** ; le remplacement de partition aligne l'entrepôt sur la dernière livraison, y compris pour les lignes **retirées**. Le choix dépend de ce que la source promet : un renvoi complet (partition) ou des corrections de lignes (fusion).

### Application 2.4 — Piloter le pipeline en ligne de commande, et planifier (section 2.2)

**Objectif.** Utiliser l'interface du pipeline comme le ferait un planificateur : simulation, mois ciblé, code de sortie ; puis calculer ses échéances.

**Étape 1 — l'interface.** On construit l'analyseur d'arguments du pipeline et on l'essaie.

```python
parseur = P.construire_parser()
args = parseur.parse_args(["--mois", "2025-10", "--seuil-rejets", "0.01"])
print({k: v for k, v in vars(args).items() if k != "depot"})
print(parseur.format_usage().strip())
```
<!--sortie-->
```text
{'mois': '2025-10', 'simuler': False, 'seuil_rejets': 0.01}
usage: pipeline [-h] [--depot DEPOT] [--mois MOIS] [--simuler]
                [--seuil-rejets SEUIL_REJETS]
```

**Étape 2 — trois lancements dans un processus à part.**

```python
def lancer(*args):
    r = subprocess.run([sys.executable, "build/outils_ch02.py", "pipeline", *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()

code, sortie = lancer("--simuler")
print("simulation :", code, "|", len(sortie), "lignes | première :", sortie[0])
code, sortie = lancer("--mois", "2025-10")
print("octobre :", code, "|", sortie[-1])
code, sortie = lancer("--mois", "2025-10", "--seuil-rejets", "0.0001")
print("octobre, seuil très strict :", code, "|", sortie[-1])
```
<!--sortie-->
```text
simulation : 0 | 12 lignes | première : [simulation] chargerait commandes_2025-01.csv (2227 lignes annoncées)
octobre : 0 | 2025-11-06 06:00:09 INFO    fin commandes_2025-10_v2.csv : 2644 insérées, 0 mises à jour, 1 rejetées
octobre, seuil très strict : 1 | 2025-11-06 06:00:09 ERROR   commandes_2025-10_v2.csv : ControleEchoue : 1 lignes rejetées sur 2645 (seuil 0,01 %)
```

**Étape 3 — les échéances.** Écrivons `0 6 3 * *` et calculons ses six prochaines dates à partir du 4 décembre 2025.

```python
from datetime import datetime
t, dates = datetime(2025, 12, 4), []
for _ in range(6):
    t = P.prochaine_echeance("0 6 3 * *", t)
    dates.append(t.strftime("%d/%m/%Y %Hh"))
print(dates)
```
<!--sortie-->
```text
['03/01/2026 06h', '03/02/2026 06h', '03/03/2026 06h', '03/04/2026 06h', '03/05/2026 06h', '03/06/2026 06h']
```

*Ce qu'il faut retenir.* Le code de sortie (0 ou 1) est la seule chose que lit le planificateur ; la **simulation** doit sortir avant toute écriture.

### Application 2.5 — Lire un journal et trouver la panne (section 2.3)

**Objectif.** Diagnostiquer une panne à partir du journal et de la table des exécutions, puis la réparer **par une relance**. Nous rejouons l'année en provoquant une panne que vous ne connaissez pas : au mois de juin, le **référentiel des clients** est passé vide.

**Étape 1 — l'année, avec une panne cachée.**

```python
ent = P.nouvel_entrepot(); cl = P.charger_dimensions(ent); h = P.Horloge(); log, tampon = P.journal(h)
for _, f in derniers.sort_values("date_livraison").iterrows():
    h.aller_a(f["date_livraison"])
    connus = set() if f["mois"] == "2025-06" else cl
    P.executer(ent, chemin(f["fichier"]), int(f["lignes_annoncees"]), connus, h, log)
print("\n".join(l for l in tampon.getvalue().splitlines() if "ERROR" in l or "WARNING" in l))
```
<!--sortie-->
```text
2025-07-03 06:00:09 ERROR   commandes_2025-06.csv : ControleEchoue : 2333 lignes rejetées sur 2333 (seuil 2,00 %)
```

**Étape 2 — poser le diagnostic.** À vous de répondre avant de lire le corrigé : **quel mois** a échoué, **quel contrôle** a arrêté le chargement, et **quelle est la cause la plus probable** ? Un indice : dans la table des exécutions, regardez le nombre de lignes rejetées.

```python
print(ent.execute("SELECT mois, statut, lignes_lues, lignes_rejetees, message FROM executions WHERE statut = 'ECHEC'").df().to_string(index=False))
print("chiffre d'affaires chargé :", fr(ent.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0], 0), "€ pour", fr(VERITE["total_original"], 0), "€ attendus")
```
<!--sortie-->
```text
   mois statut  lignes_lues  lignes_rejetees                                                       message
2025-06  ECHEC         2333             2333 ControleEchoue : 2333 lignes rejetées sur 2333 (seuil 2,00 %)
chiffre d'affaires chargé : 1 217 834 € pour 1 324 764 € attendus
```

**Étape 3 — réparer en relançant.** Le référentiel est rétabli ; on relance juin, puis on contrôle le total.

```python
f = derniers[derniers["mois"] == "2025-06"].iloc[0]
h.aller_a("2025-07-04")
print(P.executer(ent, chemin(f["fichier"]), int(f["lignes_annoncees"]), cl, h, log), "| total :", fr(ent.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0], 2), "€")
```
<!--sortie-->
```text
SUCCES | total : 1 324 763,72 €
```

*Ce qu'il faut retenir.* Un chargement **tout ou rien** laisse l'entrepôt intact ; l'idempotence permet de relancer sans se demander ce qui a été chargé ; le **seuil de rejets** a transformé une panne silencieuse (tout en quarantaine, chiffre faux) en échec visible.

### Application 2.6 — Contrôles avant et après, rapprochement (section 2.3)

**Objectif.** Écrire un contrôle à la source, mettre en évidence ce que ne voient pas les règles ligne à ligne, et rapprocher l'entrepôt d'une référence **par mois**.

**Étape 1 — le contrôle à la source, sur les quinze fichiers.**

```python
def controle_source(fichier, annonce):
    try:
        lues = len(P.extraire(chemin(fichier)))
    except P.SourceVide:
        lues = 0
    return lues, lues == annonce

res = [(f["fichier"], *controle_source(f["fichier"], int(f["lignes_annoncees"]))) for _, f in man.iterrows()]
mauvais = pd.DataFrame(res, columns=["fichier", "lignes lues", "conforme"]).query("not conforme")
print(mauvais.to_string(index=False))
```
<!--sortie-->
```text
              fichier  lignes lues  conforme
commandes_2025-09.csv            0     False
commandes_2025-10.csv         2249     False
```

**Étape 2 — une jointure qui perd des lignes.** Les règles ligne à ligne ne voient pas une jointure qui élimine des lignes ; le contrôle de **conservation** les voit. On joint les lignes de mars au catalogue **amputé de cinq produits**.

```python
brut = P.extraire(chemin("commandes_2025-03_v2.csv"))
v, r = P.transformer(brut, clients)
produits = pd.read_csv(os.path.join(D, "produits.csv"))
v_perdu = v.merge(produits.iloc[5:][["id_produit"]], on="id_produit")        # jointure interne : les produits 1 à 5 disparaissent
print("lignes valides :", len(v), "| après la jointure :", len(v_perdu), "| conservation (lignes) :", len(brut) == len(v_perdu) + len(r))
print("montant perdu :", fr(v["montant"].sum() - v_perdu["montant"].sum(), 2), "€")
```
<!--sortie-->
```text
lignes valides : 2023 | après la jointure : 1867 | conservation (lignes) : False
montant perdu : 7 656,87 €
```

**Étape 3 — rapprocher l'entrepôt par mois.** On charge l'année et on compare chaque mois à la référence (le chiffre d'affaires d'origine, connu par le générateur).

```python
ent = P.nouvel_entrepot(); cl = P.charger_dimensions(ent)
P.rejouer(ent, DEPOT, cl, P.Horloge())
mois_ca = ent.execute("SELECT strftime(date_commande, '%Y-%m') AS mois, round(sum(montant), 2) AS ca FROM fait_ligne GROUP BY 1 ORDER BY 1").df()
mois_ca["référence"] = mois_ca["mois"].map(lambda m: VERITE["par_mois"][m]["total_original"])
mois_ca["écart"] = (mois_ca["ca"] - mois_ca["référence"]).round(2)
print("mois avec un écart :", int((mois_ca["écart"].abs() > 0.005).sum()), "sur", len(mois_ca), "| écart maximal :", fr(mois_ca["écart"].abs().max(), 2), "€")
```
<!--sortie-->
```text
mois avec un écart : 0 sur 12 | écart maximal : 0,00 €
```

*Ce qu'il faut retenir.* Le contrôle « lignes et montants **conservés** » ne dépend d'aucune règle de gestion : il attrape les erreurs de jointure et de filtre. Rapprocher **par mois** et pas seulement au total évite que deux erreurs de signe opposé se compensent.

### Application 2.7 — Un exécuteur de graphe et des modèles SQL (section 2.4)

**Objectif.** Utiliser les deux jouets de la section 2.4 sur un cas voisin : un tableau de bord qui dépend de deux chargements.

**Étape 1 — un graphe, une panne.** Le chargement des livraisons tombe en panne ; que devient le reste ?

```python
graphe = {"charger_commandes": set(), "charger_livraisons": set(), "mart_ventes": {"charger_commandes"}, "mart_logistique": {"charger_livraisons"},
          "tableau_de_bord": {"mart_ventes", "mart_logistique"}, "envoyer": {"tableau_de_bord"}}
faits = []
def tache(nom, panne=False):
    def f():
        faits.append(nom)
        if panne:
            raise RuntimeError("API des colis injoignable")
    return f

actions = {t: tache(t, panne=(t == "charger_livraisons")) for t in graphe}
etat = P.lancer_graphe(graphe, actions)
print({t: s for t, s in etat.items()})
```
<!--sortie-->
```text
{'charger_commandes': 'ok', 'charger_livraisons': 'échec', 'mart_ventes': 'ok', 'mart_logistique': 'ignorée', 'tableau_de_bord': 'ignorée', 'envoyer': 'ignorée'}
```

**Étape 2 — des modèles SQL avec `ref()`.** On charge trois mois, puis on définit trois modèles : une vue de base, le chiffre d'affaires par canal et par mois, et la **part** de chaque canal dans le mois (une fonction de fenêtre).

```python
ent = P.nouvel_entrepot(); cl = P.charger_dimensions(ent); h = P.Horloge()
for _, f in derniers.head(3).iterrows():
    P.executer(ent, chemin(f["fichier"]), int(f["lignes_annoncees"]), cl, h)
MODELES = {"base": "SELECT strftime(date_commande, '%Y-%m') AS mois, canal, montant FROM fait_ligne",
           "ca_canal": "SELECT mois, canal, round(sum(montant), 2) AS ca FROM {{ ref('base') }} GROUP BY ALL",
           "part_canal": "SELECT mois, canal, ca, round(100 * ca / sum(ca) OVER (PARTITION BY mois), 1) AS part FROM {{ ref('ca_canal') }}"}
ordre, _ = P.construire_modeles(ent, MODELES)
print(ordre)
print(ent.execute("SELECT * FROM part_canal WHERE mois = '2025-03' ORDER BY canal").df().to_string(index=False))
print({t: P.tester_modele(ent, "part_canal", t) for t in ("unique:mois,canal", "non_nul:part")})
```
<!--sortie-->
```text
['base', 'ca_canal', 'part_canal']
   mois    canal       ca  part
2025-03 Boutique 39038.90  43.5
2025-03  Réseaux  8440.16   9.4
2025-03     Site 42308.24  47.1
{'unique:mois,canal': 0, 'non_nul:part': 0}
```

**Étape 3 — l'analyse d'impact.** Si on change `base`, quels modèles faut-il reconstruire ? On remonte le graphe des `ref()`.

```python
import re
refs = {n: set(re.findall(r"ref\('(\w+)'\)", s)) for n, s in MODELES.items()}
def en_aval(source, refs):
    touches = {n for n, dep in refs.items() if source in dep}
    for n in list(touches):
        touches |= en_aval(n, refs)
    return touches
print("modèles à reconstruire si « base » change :", sorted(en_aval("base", refs)))
```
<!--sortie-->
```text
modèles à reconstruire si « base » change : ['ca_canal', 'part_canal']
```

*Ce qu'il faut retenir.* Le graphe donne **l'ordre** de construction et **l'impact** d'un changement ; les tests attrapent les erreurs de structure (doublons, vides) mais pas les erreurs de sens.

### Application 2.8 — Lire une API paginée (section 2.6)

**Objectif.** Lire toutes les pages d'une API qui tombe en panne, **rapprocher** ce qu'on a lu, et voir qu'une clé fausse **ne se réessaie pas**.

**Étape 1 — la lecture complète et le rapprochement.**

```python
CLE = "cle-de-demonstration-0000"
trace = []
with P.serveur_api(20121, CLE) as url:
    colis, total = P.lire_api(url, CLE, trace=trace)
livraisons = pd.read_csv(os.path.join(D, "livraisons.csv"))
print("pages :", len({c for c, _ in trace}), "| requêtes :", len(trace), "| lues :", len(colis), "| annoncé :", total, "| fichier du volume III :", int((livraisons["date_commande"] >= "2025-01-01").sum()))
```
<!--sortie-->
```text
pages : 16 | requêtes : 18 | lues : 7504 | annoncé : 7504 | fichier du volume III : 7504
```

**Étape 2 — un indicateur par deux voies.** Le taux de livraisons en retard par transporteur, calculé sur les données de l'API puis sur le fichier : les deux doivent être identiques.

```python
api_taux = colis.groupby("transporteur")["retard"].mean().round(4)
fichier_taux = livraisons[livraisons["date_commande"] >= "2025-01-01"].groupby("transporteur")["retard"].mean().round(4)
print(pd.DataFrame({"API": api_taux * 100, "fichier": fichier_taux * 100}).round(1).to_string())
print("identiques :", bool((api_taux == fichier_taux).all()))
```
<!--sortie-->
```text
                 API  fichier
transporteur                 
Transporteur A  15.3     15.3
Transporteur B  26.4     26.4
Transporteur C  52.2     52.2
identiques : True
```

**Étape 3 — une clé fausse.** Combien de requêtes fait-on avec une mauvaise clé ?

```python
trace2 = []
with P.serveur_api(20121, CLE) as url:
    try:
        P.lire_api(url, "mauvaise-cle", trace=trace2)
    except Exception as e:
        print(type(e).__name__, "après", len(trace2), "requête(s) | code :", trace2[-1][1])
```
<!--sortie-->
```text
HTTPError après 1 requête(s) | code : 401
```

*Ce qu'il faut retenir.* On réessaie les pannes **passagères** (429, 500), jamais les erreurs d'identité (401) ; et on rapproche toujours le nombre de lignes lues du total annoncé.

### Application 2.9 — Envoyer un rapport, après les contrôles (section 2.6)

**Objectif.** Assembler un e-mail à partir de l'entrepôt, l'envoyer au serveur de test, le **relire**, et le **bloquer** si un contrôle échoue.

**Étape 1 — le message, pour un mois donné.**

```python
import smtplib
from email.message import EmailMessage
ent = P.nouvel_entrepot(); cl = P.charger_dimensions(ent); P.rejouer(ent, DEPOT, cl, P.Horloge())

def message_mensuel(con, mois):
    ca = con.execute("SELECT canal, round(sum(montant)) AS ca FROM fait_ligne WHERE strftime(date_commande, '%Y-%m') = ? GROUP BY canal ORDER BY canal", [mois]).df()
    tab = pd.DataFrame({"Canal": ca["canal"], "CA TTC (€)": ca["ca"].map(lambda x: fr(x, 0))})
    m = EmailMessage()
    m["From"], m["To"], m["Subject"] = "rapports@boutique.example", "gerante@boutique.example", f"Chiffre d'affaires {mois} : {fr(ca['ca'].sum() / 1000, 0)} k€ TTC"
    m.set_content(tab.to_string(index=False))
    m.add_alternative(P.rapport_html(tab, f"Chiffre d'affaires {mois}", "Lignes contrôlées uniquement."), subtype="html")
    m.add_attachment(ca.to_csv(index=False), subtype="csv", filename=f"ca_{mois}.csv")
    return m

msg = message_mensuel(ent, "2025-06")
print(msg["Subject"], "|", [p.get_content_type() for p in msg.walk() if not p.is_multipart()])
```
<!--sortie-->
```text
Chiffre d'affaires 2025-06 : 107 k€ TTC | ['text/plain', 'text/html', 'text/csv']
```

**Étape 2 — le garde-fou : on n'envoie que si les contrôles passent.**

```python
def publier(message, controles, port):
    echecs = [nom for nom, ok in controles.items() if not ok]
    if echecs:
        raise RuntimeError("rapport NON envoyé : " + " ; ".join(echecs))
    with smtplib.SMTP("127.0.0.1", port, timeout=10) as s:
        s.send_message(message)
    return "envoyé"

ca_base = ent.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0]
controles = {"total = référence": abs(ca_base - VERITE["total_original"]) < 0.005, "aucun échec non résolu": not P.evaluer_alertes(ent, "2026-01-05", seuil_rejets=1)}
with P.serveur_smtp(20131) as recus:
    print(publier(msg, controles, 20131))
    try:
        publier(msg, {**controles, "mois contrôlé": False}, 20131)
    except RuntimeError as e:
        print(e)
import email, email.policy
recu = email.message_from_bytes(recus[0]["octets"], policy=email.policy.default)
print("messages reçus par le serveur de test :", len(recus), "| pièce jointe :", next(recu.iter_attachments()).get_filename())
```
<!--sortie-->
```text
envoyé
rapport NON envoyé : mois contrôlé
messages reçus par le serveur de test : 1 | pièce jointe : ca_2025-06.csv
```

*Ce qu'il faut retenir.* Le garde-fou se trouve **entre** le calcul et l'envoi : un rapport qui n'a pas passé ses contrôles ne part pas, et le message d'erreur dit lequel a échoué.

## Exercices

Les énoncés sont regroupés ici ; les corrigés suivent, dans la partie *Corrigés*. Essayez avant de regarder. Les étoiles indiquent la difficulté : ⭐ application directe, ⭐⭐ un raisonnement ou une combinaison, ⭐⭐⭐ une petite expérience ou un choix de conception.

### Exercice 2.1 ⭐ — ETL ou ELT ? (section 2.1.1 et 2.1.6)

Pour chacune de ces situations, dites si la transformation se fait plutôt **avant** le chargement (ETL) ou **après** (ELT), et pourquoi : (a) un fichier en `cp1252` avec des dates `JJ/MM/AAAA` ; (b) le chiffre d'affaires par mois et par canal ; (c) une colonne d'adresses électroniques à pseudonymiser avant que les données entrent dans l'entrepôt ; (d) un indicateur recalculé chaque nuit sur huit cents millions de lignes dans un entrepôt infonuagique ; (e) la part de chaque canal dans le chiffre d'affaires du mois, pour un tableau de bord.

### Exercice 2.2 ⭐ — Pourquoi tout lire en texte ? (section 2.1.2)

Un fichier de trois lignes contient des références de produits écrites `007`, `012` et `130`. Lisez-le avec la lecture par défaut de pandas, puis avec `dtype=str`. Qu'est-ce qui est perdu dans le premier cas, et pourquoi cela compte-t-il pour une clé ?

### Exercice 2.3 ⭐⭐ — Un filigrane par date de livraison (section 2.1.4)

Au lieu de retenir la dernière **date de commande** chargée, on retient la dernière **date de livraison** de fichier chargée. Écrivez `a_charger(man, derniere)` qui renvoie, dans l'ordre, les fichiers du manifeste livrés **après** cette date. Appliquez-la quand la dernière livraison chargée est celle du 3 avril 2025 (le premier fichier de mars) : le renvoi de mars est-il retenu ? Quelle faiblesse reste-t-il, et quelle information garder en plus pour s'en protéger ?

### Exercice 2.4 ⭐⭐ — La clé qui se recycle (section 2.1.5)

Imaginez que la source **recycle** ses identifiants : dans le fichier d'avril, les dix premières lignes portent les `id_ligne` des dix premières lignes de mars. Chargez mars puis avril par fusion : combien de lignes de mars disparaissent ? Écrivez ensuite `collisions(a, b)`, qui détecte les identifiants communs à deux lots dont le **contenu diffère**, et montrez qu'elle détecte le problème.

### Exercice 2.5 ⭐ — Écrire des expressions cron (section 2.2.3)

Écrivez les expressions cron de : (a) chaque lundi à 7 h 30 ; (b) le 1er et le 15 de chaque mois à 6 h ; (c) toutes les 10 minutes de 8 h à 18 h, du lundi au vendredi ; (d) tous les jours à 0 h 30. Vérifiez chacune avec `P.prochaine_echeance`, à partir du mercredi 5 novembre 2025 à 10 h 17. Quelle précaution prendre si vous utilisez ensuite ces expressions avec APScheduler ?

### Exercice 2.6 ⭐⭐ — Que faut-il rattraper ? (section 2.2.5)

On vous donne un petit manifeste et la liste des fichiers déjà chargés avec succès.

```python
man_t = pd.DataFrame({"mois": ["2025-01", "2025-02", "2025-02", "2025-03"], "fichier": ["a.csv", "b.csv", "b_v2.csv", "c.csv"],
                      "date_livraison": ["2025-02-03", "2025-03-03", "2025-03-10", "2025-04-03"]})
ok_t = pd.DataFrame({"fichier": ["a.csv", "b.csv"]})
```

Écrivez `a_faire(man, ok)` qui renvoie les mois à (re)charger avec le fichier à utiliser. Que doit-elle répondre ici, et pourquoi ?

### Exercice 2.7 ⭐⭐⭐ — Le verrou qui survit au processus (section 2.2.6)

Montrez, par une expérience, la différence entre un verrou de fichier `flock` et un verrou « fichier de PID » créé avec `os.O_EXCL` quand le processus qui le détient **est tué**. Que constatez-vous, et que faudrait-il faire pour que le second soit sûr ?

### Exercice 2.8 ⭐ — Quel niveau de journal ? (section 2.3.2)

Classez ces huit événements par niveau (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) : (a) « début du chargement de `commandes_2025-04.csv` » ; (b) « requête SQL exécutée en 0,4 s » ; (c) « 25 lignes en quarantaine » ; (d) « fichier vide » ; (e) « entrepôt injoignable après quatre essais » ; (f) « reprise 2 sur 4 après une erreur réseau » ; (g) « fin du chargement : 2 225 lignes » ; (h) « colonne renommée détectée : `total_ligne` devient `montant` ».

### Exercice 2.9 ⭐⭐ — Où mettre le seuil de rejets ? (section 2.3.5)

Calculez, pour la dernière version de chaque mois, la part de lignes rejetées. Quel mois est le plus touché, et à partir de quel seuil serait-il refusé ? Que devient ce mois si l'on **exclut les doublons exacts** du taux ? Quel seuil et quelle règle retenez-vous, et pourquoi ?

### Exercice 2.10 ⭐⭐ — Une règle de volume, et ses fausses alertes (section 2.3.7)

Une collègue propose : « alerter si le nombre de lignes d'un mois est inférieur à 80 % de la moyenne des trois mois précédents ». Appliquez cette règle au **premier fichier livré** de chaque mois (en prenant comme référence les nombres de lignes **finals** des trois mois précédents), puis comparez avec la règle fondée sur le **manifeste** (lignes lues contre lignes annoncées). Quels mois chaque règle signale-t-elle ? Laquelle recommandez-vous ?

### Exercice 2.11 ⭐⭐ — Quel outil pour quel besoin ? (section 2.4.7)

Pour chaque situation, choisissez entre un script avec cron, dbt, un orchestrateur de type Airflow, ou un outil bas code, et justifiez en deux phrases : (a) une analyste seule, un fichier mensuel, un entrepôt local ; (b) une équipe de six personnes qui maintient quatre-vingts tables SQL dépendantes les unes des autres ; (c) quarante tâches de natures différentes (extractions, scripts Python, requêtes), des dépendances croisées, un besoin de rejouer trois mois d'historique ; (d) « quand un fournisseur dépose un fichier dans un dossier partagé, le copier ailleurs et prévenir le service achats ».

### Exercice 2.12 ⭐⭐ — Le seuil de rentabilité d'un robot (section 2.5.4)

Avec les hypothèses de la section (tâche manuelle de 20 minutes par semaine ; robot à 24 heures de construction ; trois heures par incident), calculez le temps cumulé sur **trois ans** de la tâche manuelle et du robot pour un nombre d'incidents par an allant de 0 à 8. Jusqu'à combien d'incidents par an le robot est-il gagnant ? Que concluez-vous sur la fiabilité de l'estimation ?

### Exercice 2.13 ⭐⭐ — Débusquer les secrets (section 2.6.3)

Voici un extrait de script.

```python
EXEMPLE = '''API_KEY = "sk-demo-1234567890"
url = "https://utilisateur:motdepasse@service.example/api"
log.info("en-têtes : %s", {"Authorization": "Bearer abc123def456"})
mot_de_passe = os.environ["SMTP_MOT_DE_PASSE"]
requests.get(url, params={"token": "abcdef"})'''
```

Écrivez `chercher_secrets(texte)`, qui renvoie les numéros et le texte des lignes suspectes (avec des expressions régulières), appliquez-la, et dites quelle(s) ligne(s) **ne devrait pas** être signalée(s) et pourquoi.

### Exercice 2.14 ⭐⭐⭐ — La fiche de diffusion (section 2.6.5)

Rédigez la **fiche de diffusion** du rapport mensuel de la boutique (à qui, quand, quoi, quelles données, quelle version, qui répond, que faire en cas d'échec, comment savoir s'il est lu). Écrivez ensuite `verifier_pj(df)`, qui **refuse** d'attacher à un e-mail un tableau contenant des colonnes à caractère personnel, et testez-la sur le tableau du chiffre d'affaires par canal puis sur un extrait de `clients.csv`.

## Corrigés

### Corrigé 2.1

| Situation | Avant ou après ? | Pourquoi |
|---|---|---|
| (a) fichier `cp1252`, dates `JJ/MM/AAAA` | **avant** (ETL) | l'encodage et le format du fichier sont des défauts **du fichier** ; l'entrepôt ne doit jamais les voir |
| (b) chiffre d'affaires par mois et canal | **après** (ELT) | c'est un agrégat lié à l'**analyse** ; une vue SQL sur l'entrepôt suffit |
| (c) adresses à pseudonymiser | **avant** | la donnée personnelle ne doit pas entrer dans l'entrepôt si elle n'y est pas nécessaire |
| (d) indicateur nocturne sur 800 millions de lignes | **après**, dans l'entrepôt | on calcule là où sont les données : les sortir pour les calculer ailleurs coûte plus cher |
| (e) part de chaque canal | **après** | une fonction de fenêtre SQL, définie une fois et partagée (voir l'application 2.7) |

### Corrigé 2.2

```python
texte = "id_produit,reference\n007,A1\n012,B2\n130,C3\n"
print(pd.read_csv(io.StringIO(texte)).to_string(index=False))
print(pd.read_csv(io.StringIO(texte), dtype=str).to_string(index=False))
```
<!--sortie-->
```text
 id_produit reference
          7        A1
         12        B2
        130        C3
id_produit reference
       007        A1
       012        B2
       130        C3
```

La lecture par défaut devine que `id_produit` est un nombre : « 007 » devient `7` et « 012 » devient `12`, et les **zéros initiaux sont perdus**. Pour une clé, c'est grave : `7` et `007` désignent peut-être deux produits différents, et la jointure avec un référentiel qui écrit « 007 » ne retrouvera rien. En lisant **tout en texte**, on garde la valeur exacte et l'on convertit ensuite **explicitement**, colonne par colonne, quand on sait que la conversion est sans danger.

### Corrigé 2.3

```python
def a_charger(man, derniere):
    return man[man["date_livraison"] > derniere].sort_values("date_livraison")["fichier"].tolist()

print(a_charger(man, "2025-04-03")[:3])
import hashlib
empreinte_fichier = lambda f: hashlib.md5(open(chemin(f), "rb").read()).hexdigest()[:8]
print("mars v1 :", empreinte_fichier("commandes_2025-03.csv"), "| mars v2 :", empreinte_fichier("commandes_2025-03_v2.csv"))
```
<!--sortie-->
```text
['commandes_2025-03_v2.csv', 'commandes_2025-04.csv', 'commandes_2025-05.csv']
mars v1 : 8f359eb1 | mars v2 : 76a5c5a6
```

Le renvoi de mars (livré le 14 avril) est **retenu**, puisque sa date de livraison est postérieure à celle du premier fichier : un filigrane de **livraison** attrape les renvois, contrairement au filigrane de date de commande. Sa faiblesse : il suppose que chaque nouveau fichier porte une date de livraison **strictement plus récente**. Deux fichiers livrés le même jour, ou un fichier **remplacé sur place** (même nom, même date, contenu différent) échappent à la règle. La parade est de garder, pour chaque fichier chargé, son **nom et son empreinte** (somme de contrôle) : un fichier dont l'empreinte change est un nouveau fichier, quelle que soit sa date. Ici, les deux fichiers de mars ont des empreintes différentes.

### Corrigé 2.4

```python
va, _ = P.transformer(P.extraire(chemin("commandes_2025-03_v2.csv")), clients)
vb, _ = P.transformer(P.extraire(chemin("commandes_2025-04.csv")), clients)
vb2 = vb.copy()
vb2.loc[vb2.index[:10], "id_ligne"] = va["id_ligne"].iloc[:10].to_numpy()
ent = P.nouvel_entrepot(); P.charger_dimensions(ent)
P.charger(ent, va, "mars"); P.charger(ent, vb2, "avril")
print("lignes attendues :", len(va) + len(vb2), "| lignes dans l'entrepôt :", P.empreinte(ent)[0])

def collisions(a, b):
    m = a.merge(b, on="id_ligne", suffixes=("_a", "_b"))
    return m[(m["id_commande_a"] != m["id_commande_b"]) | (m["montant_a"] != m["montant_b"])]
print("collisions détectées :", len(collisions(va, vb2)))
```
<!--sortie-->
```text
lignes attendues : 4248 | lignes dans l'entrepôt : 4238
collisions détectées : 10
```

Dix lignes de mars ont été **écrasées par des lignes d'avril** sans aucune erreur : la fusion fait confiance à la clé. Le contrôle `collisions` les détecte **avant** le chargement : un identifiant déjà présent avec une **commande ou un montant différent** n'est pas une correction, c'est un conflit. Un identifiant déjà présent avec le **même** contenu est un simple renvoi, légitime. La règle à retenir : la clé naturelle est un contrat qu'on **vérifie** (unicité, stabilité), pas une hypothèse.

### Corrigé 2.5

```python
t0 = datetime(2025, 11, 5, 10, 17)
for nom, expr in (("(a)", "30 7 * * 1"), ("(b)", "0 6 1,15 * *"), ("(c)", "*/10 8-18 * * 1-5"), ("(d)", "30 0 * * *")):
    print(nom, f"{expr:20s}", P.prochaine_echeance(expr, t0))
```
<!--sortie-->
```text
(a) 30 7 * * 1           2025-11-10 07:30:00
(b) 0 6 1,15 * *         2025-11-15 06:00:00
(c) */10 8-18 * * 1-5    2025-11-05 10:20:00
(d) 30 0 * * *           2025-11-06 00:30:00
```

Les quatre expressions s'écrivent ainsi : (a) `30 7 * * 1`, (b) `0 6 1,15 * *`, (c) `*/10 8-18 * * 1-5`, (d) `30 0 * * *`. Remarquez que `8-18` pour les heures donne un dernier déclenchement à **18 h 50** (la plage couvre toute l'heure 18). Avec APScheduler, **n'utilisez pas les numéros de jours** de la semaine (`1` y désigne le mardi dans la version vue au chapitre) : écrivez `mon-fri`, ou passez par les paramètres nommés du déclencheur, puis **calculez les prochaines échéances** pour les lire.

### Corrigé 2.6

```python
def a_faire(man, ok):
    derniers_t = man.sort_values("date_livraison").groupby("mois").tail(1)
    return derniers_t[~derniers_t["fichier"].isin(ok["fichier"])][["mois", "fichier"]]

print(a_faire(man_t, ok_t).to_string(index=False))
```
<!--sortie-->
```text
   mois  fichier
2025-02 b_v2.csv
2025-03    c.csv
```

La fonction répond **deux** mois : février, avec **`b_v2.csv`** (la dernière version livrée n'est pas celle qui a été chargée : `b.csv` l'a été, mais un renvoi est arrivé depuis), et mars avec `c.csv` (jamais chargé). Janvier n'est pas rendu : son dernier fichier est chargé. Le piège de l'exercice est de ne chercher que les **mois absents** et d'oublier les **renvois**.

### Corrigé 2.7

```python
import tempfile, shutil, fcntl
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
verrou_flock, verrou_pid = os.path.join(dossier, "a.verrou"), os.path.join(dossier, "b.pid")
enfant = f"""import fcntl, os, time
f = open({verrou_flock!r}, "w"); fcntl.flock(f, fcntl.LOCK_EX)
os.close(os.open({verrou_pid!r}, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
print("pret", flush=True); time.sleep(60)"""
p = subprocess.Popen([sys.executable, "-c", enfant], stdout=subprocess.PIPE, text=True)
p.stdout.readline(); p.kill(); p.wait()
f = open(verrou_flock, "w")
try:
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); print("flock : verrou obtenu après la mort du processus")
except BlockingIOError:
    print("flock : encore bloqué")
try:
    os.close(os.open(verrou_pid, os.O_CREAT | os.O_EXCL | os.O_WRONLY)); print("fichier PID : verrou obtenu")
except FileExistsError:
    print("fichier PID : le verrou orphelin bloque toujours")
f.close(); shutil.rmtree(dossier)          # dossier créé par mkdtemp dans TMPDIR : chemin explicite, jamais vide
```
<!--sortie-->
```text
flock : verrou obtenu après la mort du processus
fichier PID : le verrou orphelin bloque toujours
```

Le verrou `flock` est lié au **processus** : le système le libère quand le processus disparaît, même tué brutalement. Le « fichier de PID » est lié au **système de fichiers** : il reste après la mort du processus et bloque les exécutions suivantes jusqu'à ce qu'un humain le supprime. Pour le rendre sûr, il faudrait, à chaque démarrage, **lire le PID** qu'il contient, vérifier que ce processus **existe encore** (et que c'est bien notre programme), et sinon **reprendre le verrou**, avec la course que cela suppose entre deux démarrages simultanés : c'est précisément ce que `flock` fait gratuitement, sous Linux et macOS.

### Corrigé 2.8

| Événement | Niveau | Pourquoi |
|---|---|---|
| (a) début du chargement | `INFO` | marche normale, utile pour reconstituer l'histoire |
| (b) requête SQL en 0,4 s | `DEBUG` | détail technique, utile seulement pour comprendre une lenteur |
| (c) 25 lignes en quarantaine | `WARNING` | inhabituel, sans gravité, à surveiller |
| (d) fichier vide | `ERROR` | cette exécution ne peut pas continuer, mais le pipeline reste sain |
| (e) entrepôt injoignable après quatre essais | `CRITICAL` | plus aucun chargement n'est possible : intervention humaine |
| (f) reprise 2 sur 4 | `WARNING` | une panne passagère qui a un coût ; si la reprise réussit, il n'y a pas d'alerte |
| (g) fin du chargement | `INFO` | marche normale, avec les nombres |
| (h) colonne renommée détectée | `WARNING` | toléré par le contrat, mais **à signaler** : la source a changé sans prévenir |

Les cas (c), (f) et (h) sont les plus discutés : ce sont des **avertissements**, ni l'ordinaire (`INFO`) ni l'échec (`ERROR`). Ils méritent une ligne de journal, mais **pas une alerte** envoyée à quelqu'un, sauf s'ils se répètent.

### Corrigé 2.9

```python
ent = P.nouvel_entrepot(); cl = P.charger_dimensions(ent)
taux = []
for _, f in derniers.iterrows():
    brut = P.extraire(chemin(f["fichier"]))
    _, r = P.transformer(brut, cl)
    taux.append((f["mois"], len(brut), len(r), int((r["motif"] == "doublon exact").sum())))
t = pd.DataFrame(taux, columns=["mois", "lues", "rejetées", "doublons"])
t["taux (%)"] = (t["rejetées"] / t["lues"] * 100).round(2)
t["hors doublons (%)"] = ((t["rejetées"] - t["doublons"]) / t["lues"] * 100).round(2)
print(t.sort_values("taux (%)", ascending=False).head(4).to_string(index=False))
```
<!--sortie-->
```text
   mois  lues  rejetées  doublons  taux (%)  hors doublons (%)
2025-11  3484        25        25      0.72               0.00
2025-03  2028         5         0      0.25               0.25
2025-08  1807         4         0      0.22               0.22
2025-04  2228         3         0      0.13               0.13
```

Novembre est le mois le plus touché, avec 0,72 % de lignes rejetées, **toutes** des doublons exacts : un seuil à 0,5 % l'aurait refusé, un seuil à 1 % l'aurait laissé passer. Si l'on exclut les doublons du taux, novembre tombe à zéro : un doublon exact est **sans danger** pour le chiffre (la ligne d'origine est chargée), alors qu'une ligne orpheline ou un montant négatif peut cacher une vraie erreur. Une règle raisonnable : un seuil **bas** (de l'ordre de 0,5 %) sur les rejets **hors doublons**, qui arrête le chargement, et un simple **avertissement** (journal, pas d'alerte) sur les doublons. Le chiffre exact compte moins que le fait qu'il soit **écrit, réglable et connu** de celle qui lit les rapports.

### Corrigé 2.10

```python
premiers = man.sort_values("date_livraison").groupby("mois").head(1).set_index("mois")
def lues(f):
    return len(P.extraire(chemin(f))) if os.path.getsize(chemin(f)) else 0
finales = pd.Series({m: lues(f) for m, f in derniers.set_index("mois")["fichier"].items()}).sort_index()
reference = finales.rolling(3).mean().shift(1)
premiers_lues = pd.Series({m: lues(f) for m, f in premiers["fichier"].items()}).sort_index()
regle_volume = premiers_lues[premiers_lues < 0.8 * reference].index.tolist()
regle_manifeste = [m for m, f in premiers.iterrows() if lues(f["fichier"]) != f["lignes_annoncees"]]
print("règle de volume :", regle_volume, "\nrègle du manifeste :", regle_manifeste)
```
<!--sortie-->
```text
règle de volume : ['2025-08', '2025-09'] 
règle du manifeste : ['2025-09', '2025-10']
```

La règle de volume signale **août** (une fausse alerte : le mois est naturellement creux, avec 1 807 lignes contre une moyenne de 2 321 sur les trois mois précédents) et **septembre** (fichier vide, vraie panne), mais **manque octobre** : le fichier tronqué (2 249 lignes) reste au-dessus de 80 % de la moyenne des trois mois précédents, parce que l'activité d'octobre est supérieure à celle de l'été. La règle du manifeste signale **exactement** les deux pannes (septembre et octobre) et aucune fausse alerte, parce qu'elle compare le fichier à **ce que la source dit avoir écrit** et non à une moyenne qui ignore la saison. On la recommande ; on garde la règle de volume, avec un seuil plus large et la comparaison à **l'an dernier** quand on l'a, comme contrôle de **plausibilité** complémentaire.

### Corrigé 2.11

- **(a)** Un **script avec cron** (ou APScheduler). Un fichier par mois et un entrepôt local ne justifient aucun système de plus à maintenir ; la qualité vient de l'idempotence et des contrôles, pas de l'outil.
- **(b)** **dbt** (ou un outil équivalent de transformation SQL). Quatre-vingts tables dépendantes appellent un ordre de construction déduit automatiquement, des tests à chaque exécution et une documentation partagée entre six personnes.
- **(c)** Un **orchestrateur** de type Airflow. Des tâches de natures variées, des dépendances croisées et le besoin de rejouer l'historique sont exactement ce qu'il apporte (graphe, reprise ciblée, historique des exécutions).
- **(d)** Un outil **bas code**. C'est de l'acheminement entre deux applications (copier un fichier, envoyer un message) sans calcul : il va plus vite qu'un script et peut être maintenu par le service concerné.

Dans tous les cas, **aucun outil n'apporte l'idempotence ni les contrôles** : ce sont des propriétés des tâches, pas de l'orchestrateur.

### Corrigé 2.12

```python
manuel_3_ans = 20 * 52 / 60 * 3
tab = pd.DataFrame({"incidents par an": range(9)})
tab["robot, 3 ans (h)"] = 24 + 3 * 3 * tab["incidents par an"]
tab["manuel, 3 ans (h)"] = round(manuel_3_ans, 1)
tab["robot gagnant"] = tab["robot, 3 ans (h)"] < manuel_3_ans
print(tab.to_string(index=False))
```
<!--sortie-->
```text
 incidents par an  robot, 3 ans (h)  manuel, 3 ans (h)  robot gagnant
                0                24               52.0           True
                1                33               52.0           True
                2                42               52.0           True
                3                51               52.0           True
                4                60               52.0          False
                5                69               52.0          False
                6                78               52.0          False
                7                87               52.0          False
                8                96               52.0          False
```

Sur trois ans, la tâche manuelle coûte 52 heures. Le robot coûte 24 heures plus trois heures par incident et par an, trois ans : il est gagnant jusqu'à **trois incidents par an** (51 heures), et perdant à partir de quatre (60 heures). Or le nombre d'incidents est justement ce qu'on connaît le moins avant de construire : à trois, le gain est d'**une heure** sur trois ans, soit rien ; à quatre, la perte est de huit heures. L'estimation est donc **très sensible** à l'hypothèse la moins sûre, et un robot dont le gain tient à un incident par an près ne justifie pas la dépense, sans même compter le risque de décision fondée sur un résultat faux quand le robot « réussit à côté ».

### Corrigé 2.13

```python
def chercher_secrets(texte):
    motifs = [r"(?i)[\"']?(api[_-]?key|secret|token|mot_de_passe|password)[\"']?\s*[:=]\s*[\"'][^\"']+[\"']", r"://[^/\s:]+:[^@\s]+@", r"Bearer\s+[A-Za-z0-9._-]+"]
    return [(i + 1, l.strip()) for i, l in enumerate(texte.splitlines()) if any(re.search(m, l) for m in motifs)]

for numero, ligne in chercher_secrets(EXEMPLE):
    print(numero, ligne)
```
<!--sortie-->
```text
1 API_KEY = "sk-demo-1234567890"
2 url = "https://utilisateur:motdepasse@service.example/api"
3 log.info("en-têtes : %s", {"Authorization": "Bearer abc123def456"})
5 requests.get(url, params={"token": "abcdef"})
```

Les lignes **1** (clé écrite en dur), **2** (mot de passe dans l'adresse), **3** (clé dans une ligne de journal) et **5** (jeton écrit en dur dans les paramètres) sont signalées. La ligne **4** **ne doit pas l'être** : elle lit le mot de passe dans une **variable d'environnement**, ce qui est la bonne pratique ; un détecteur qui la signalerait ferait fuir les alertes pour de bon. Réécriture : `API_KEY = secret("API_KEY")` (la fonction `secret` du chapitre échoue clairement si la variable manque), l'adresse **sans** identifiants avec l'authentification passée en en-tête, un filtre de journal qui masque `Bearer …`, et un jeton lu dans l'environnement. Un détecteur de ce genre se branche **avant le commit** (un contrôle automatique) ; s'il est trop tard, on **révoque** la clé divulguée au lieu de se contenter de supprimer la ligne, car l'historique la garde.

### Corrigé 2.14

**La fiche de diffusion du rapport mensuel.**

| Question | Réponse |
|---|---|
| **À qui ?** | la liste « direction-boutique », gérée par la gérante ; une personne la tient à jour |
| **Quand ?** | le 3 de chaque mois, **après** le chargement du mois et **uniquement si** tous les contrôles ont réussi ; en retard plutôt qu'erroné |
| **Quoi ?** | chiffre d'affaires par canal, comparé au mois précédent, en tableau dans le corps ; le détail en pièce jointe ; un lien vers le tableau de bord |
| **Quelles données ?** | agrégats par canal et par mois ; **aucune** donnée de client |
| **Quelle version ?** | le mois et la date de calcul dans l'objet ; la note sur les lignes écartées dans le corps |
| **Qui répond ?** | l'adresse de réponse de l'analyste ; une personne remplaçante nommée |
| **Si ça échoue ?** | reprises (réseau), puis alerte à l'analyste ; la gérante est prévenue qu'un rapport est en retard |
| **Est-il lu ?** | point de contrôle chaque trimestre : on demande aux destinataires s'ils l'utilisent ; sinon on le supprime ou on le change |

```python
INTERDITES = {"email", "adresse", "nom", "prenom", "telephone", "annee_naissance", "id_client"}

def verifier_pj(df):
    trouvees = sorted(INTERDITES & {c.lower() for c in df.columns})
    if trouvees:
        raise ValueError("pièce jointe refusée, colonnes à caractère personnel : " + ", ".join(trouvees))
    return "pièce jointe acceptée"

par_canal = pd.DataFrame({"canal": ["Boutique", "Site", "Réseaux"], "ca": [60587, 64851, 18454]})
print(verifier_pj(par_canal))
try:
    verifier_pj(pd.read_csv(os.path.join(D, "clients.csv"), nrows=3)[["id_client", "annee_naissance", "ville"]])
except ValueError as e:
    print(e)
```
<!--sortie-->
```text
pièce jointe acceptée
pièce jointe refusée, colonnes à caractère personnel : annee_naissance, id_client
```

Le garde-fou est **simple et bête**, et c'est sa force : il refuse sur le **nom** des colonnes, sans chercher à comprendre. Il se complète par une règle de conception (n'attacher que des agrégats) et par la lecture régulière de ce qui part réellement : un contrôle par liste noire laisse passer une colonne dont le nom a été changé (`id` pour `id_client`), d'où l'intérêt d'une **liste blanche** (« ne peuvent partir que ces colonnes ») dès que le rapport est stabilisé.
