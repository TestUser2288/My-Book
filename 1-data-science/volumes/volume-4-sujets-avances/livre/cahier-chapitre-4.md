# Chapitre 4 : MLOps — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 4 du livre. Les **applications** reprennent, pas à pas et avec du code, ce que le livre n'a fait que résumer (batterie de tests, API de scoring, déploiement canari avec retour arrière, journal et étiquettes tardives, orchestration, suivi d'expériences, porte de qualité, mois de production simulé) et se terminent par une **chaîne complète** de bout en bout ; les **exercices** sont corrigés à la fin. Il se lit **de haut en bas** : les objets créés dans la section « Préparation » servent partout. Tout s'exécute **hors ligne et dans le processus Python** (API interrogée par un client de test, suivi d'expériences sur une base SQLite temporaire) ; les exemples de Docker, Kubernetes, Airflow ou GitHub Actions ne sont pas exécutés (voir le livre). Les données sont celles du livre : `clients_ml.csv`, des clients d'une boutique simulée, avec la résiliation à 90 jours `churn_90j` comme cible.

## Préparation

Une seule cellule charge les bibliothèques, les données, le découpage en trois jeux (60 % d'entraînement, 20 % de test, 20 % de « réservoir de production ») et les deux modèles du chapitre. Les fonctions utilitaires (`donnees`, `modele_v1`, `modele_v2`, `psi`, `semaine`, `creer_app`, `MiniOrchestrateur`…) sont dans `build/outils_ch04.py` ; leur code est celui dont le livre décrit le principe. Un dossier temporaire `WORK` reçoit tous les fichiers créés ; il est **supprimé à la fin**. Les colonnes `depense_6m`, `segment_vrai` et `commandes_apres_cible` ne sont **jamais** des variables d'entrée.

```python
import atexit, hashlib, json, math, os, shutil, sys, tempfile, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.metrics import roc_auc_score
from outils_ch04 import donnees, modele_v1, modele_v2, hash_fichier, psi, semaine, creer_app, ligne_json, MiniOrchestrateur

WORK = tempfile.mkdtemp(prefix="cah04_", dir=os.environ.get("TMPDIR"))
atexit.register(shutil.rmtree, WORK, ignore_errors=True)
d = donnees()
v1, v2 = modele_v1(d), modele_v2(d)
Xtr, Xte, Xpool, ytr, yte = d["Xtr"], d["Xte"], d["Xpool"], d["ytr"], d["yte"].to_numpy()
COLONNES = list(d["X"].columns)
s1_te, s2_te = v1.predict_proba(Xte)[:, 1], v2.predict_proba(Xte)[:, 1]
print(len(Xtr), "clients d'entraînement,", len(Xte), "de test,", len(Xpool), "en réservoir ; AUC de test :",
      round(roc_auc_score(yte, s1_te), 3), "(v1),", round(roc_auc_score(yte, s2_te), 3), "(v2)")
```
<!--sortie-->
```text
7200 clients d'entraînement, 2400 de test, 2400 en réservoir ; AUC de test : 0.867 (v1), 0.893 (v2)
```


## Applications

### Application 4.1 — Une batterie de tests pour un lot de données

*Sections du livre : 4.1.* **Objectif** : écrire les tests qui protègent le modèle, les essayer sur des **incidents** réalistes, et découvrir qu'aucun test de plages ne suffit.

**Étape 1 — l'empreinte d'un entraînement.** Avant de tester quoi que ce soit, on enregistre ce qui permettrait de refaire l'entraînement : le hash des données, la configuration, les versions.

```python
import platform, sklearn
empreinte = {"donnees": hash_fichier("donnees/clients_ml.csv"), "config": {"graine": 0, "part_test": 0.4},
             "python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__}
print(json.dumps(empreinte))
```
<!--sortie-->
```text
{"donnees": "fa48edff3715", "config": {"graine": 0, "part_test": 0.4}, "python": "3.13.3", "sklearn": "1.9.1", "pandas": "3.0.6"}
```

**Étape 2 — les tests.** Un test est une fonction qui rend vrai ou faux. On en écrit cinq : le schéma, les plages, l'absence de colonne interdite, l'indépendance à l'ordre des lignes, et la **stabilité de la distribution** (le PSI de chaque variable numérique, par rapport à l'entraînement, reste sous 0,25).

```python
INTERDITES = {"churn_90j", "commandes_apres_cible", "segment_vrai", "depense_6m", "id_client"}

def verifier(lot, modele):
    res = {"schéma": list(lot.columns) == COLONNES, "pas de colonne interdite": not (INTERDITES & set(lot.columns))}
    if not res["schéma"]:
        return {**res, "plages": None, "ordre des lignes": None, "distribution": None}      # inutile d'aller plus loin
    res["plages"] = bool(lot["age"].between(18, 100).all() and lot["part_achats_promo"].dropna().between(0, 1).all()
                         and lot["recence_jours"].between(0, 365).all())
    p = modele.predict_proba(lot)[:, 1]
    m = lot.sample(frac=1, random_state=0)                                                   # mêmes clients, autre ordre
    res["ordre des lignes"] = bool(np.allclose(pd.Series(modele.predict_proba(m)[:, 1], index=m.index).loc[lot.index], p))
    res["distribution"] = bool(max(psi(Xtr[c], lot[c]) for c in d["num"]) < 0.25)
    return res
```

**Étape 3 — quatre lots.** Un lot conforme, puis trois incidents : la part de promotions envoyée en pourcentage, la récence envoyée **en semaines**, une colonne qui disparaît de l'export.

```python
lots = {"conforme": Xte,
        "part promo en %": Xte.assign(part_achats_promo=Xte["part_achats_promo"] * 100),
        "récence en semaines": Xte.assign(recence_jours=Xte["recence_jours"] // 7),
        "colonne manquante": Xte.drop(columns=["ville"])}
tab = pd.DataFrame({nom: verifier(lot, v2) for nom, lot in lots.items()}).T
print(tab.map(lambda v: "—" if v is None else ("oui" if v else "NON")).to_string())
```
<!--sortie-->
```text
                    schéma pas de colonne interdite plages ordre des lignes distribution
conforme               oui                      oui    oui              oui          oui
part promo en %        oui                      oui    NON              oui          NON
récence en semaines    oui                      oui    oui              oui          NON
colonne manquante      NON                      oui      —                —            —
```

**Lecture.** Le lot conforme passe tous les tests. La **part de promotions en pourcentage** est arrêtée à la fois par le test de plages et par celui de distribution. La **récence en semaines** est le cas instructif : les valeurs (de 0 à 52) restent **dans les plages permises** (de 0 à 365) ; seul le test de distribution la voit. Quant à la colonne manquante, elle est arrêtée dès le schéma, avant tout calcul.


**Pour aller plus loin.** Ajoutez un test de **non-régression** (l'AUC sur le jeu de test ne doit pas passer sous 0,85) et un test de **comportement** : à profil égal, un client qui a plus de retours produit ne doit pas avoir un risque plus faible avec la régression logistique `v1`. Quel test échouerait si l'on remplaçait `v1` par un modèle entraîné sur les étiquettes mélangées ?

### Application 4.2 — Une API de scoring, de la requête à l'erreur

*Sections du livre : 4.2.* **Objectif** : servir `v2` par une API, vérifier la parité avec la prédiction hors ligne, provoquer les erreurs, mesurer l'ordre de grandeur de la latence.

**Étape 1 — le service.** On sauvegarde le modèle, on construit l'application, on l'interroge avec un client de test (aucun port réseau n'est ouvert).

```python
from fastapi.testclient import TestClient
chemin_v2 = os.path.join(WORK, "churn_v2.joblib"); joblib.dump(v2, chemin_v2)
api = TestClient(creer_app(chemin_v2, COLONNES, version="2.0.0"))
client = ligne_json(Xte.iloc[0])
print(api.get("/health").json())
r = api.post("/predict", json=client)
print(r.status_code, r.json(), "| hors ligne :", round(float(v2.predict_proba(Xte.iloc[[0]])[0, 1]), 4))
```
<!--sortie-->
```text
{'status': 'ok', 'version': '2.0.0'}
200 {'probabilite': 0.0049, 'version': '2.0.0'} | hors ligne : 0.0049
```

**Étape 2 — la parité sur un lot.** On envoie 100 clients à `/predict_batch` et on compare aux probabilités calculées directement.

```python
lot = [ligne_json(Xte.iloc[i]) for i in range(100)]
rep = np.array(api.post("/predict_batch", json=lot).json()["probabilites"])
ecart = np.abs(rep - v2.predict_proba(Xte.iloc[:100])[:, 1]).max()
print("écart maximal entre l'API et le modèle :", round(float(ecart), 5))
```
<!--sortie-->
```text
écart maximal entre l'API et le modèle : 5e-05
```

La différence n'est due qu'à l'**arrondi à 4 décimales** de la réponse JSON (l'écart ne peut pas dépasser $0{,}5\times10^{-4}$).

**Étape 3 — provoquer les erreurs.** Quatre requêtes invalides : âge hors plage, champ manquant, type erroné, fraction hors de $[0{,}1]$. Pour chacune, on affiche le code et le champ désigné.

```python
essais = {"âge de 17 ans": {**client, "age": 17}, "ville manquante": {k: v for k, v in client.items() if k != "ville"},
          "âge en lettres": {**client, "age": "vingt"}, "part promo à 90": {**client, "part_achats_promo": 90}}
for nom, corps in essais.items():
    e = api.post("/predict", json=corps)
    err = e.json()["detail"][0]
    print(f"{nom:16s}→ {e.status_code} · champ {err['loc'][-1]:18s} · {err['type']}")
```
<!--sortie-->
```text
âge de 17 ans   → 422 · champ age                · greater_than_equal
ville manquante → 422 · champ ville              · missing
âge en lettres  → 422 · champ age                · int_parsing
part promo à 90 → 422 · champ part_achats_promo  · less_than_equal
```

**Étape 4 — la latence.** On chronomètre 200 appels successifs. Les durées dépendent de la machine : on n'affiche pas leurs valeurs, seulement si l'**objectif de service** (95 % des réponses sous 500 ms, très large pour ce test) est tenu, et le centile de la latence est calculé par `np.percentile`.

```python
durees = []
for i in range(200):
    t0 = time.perf_counter(); api.post("/predict", json=ligne_json(Xte.iloc[i])); durees.append(time.perf_counter() - t0)
p50, p95 = np.percentile(durees, [50, 95])
print("p95 sous 500 ms :", bool(p95 < 0.5), "| p95 plus grand que la médiane :", bool(p95 >= p50))
```
<!--sortie-->
```text
p95 sous 500 ms : True | p95 plus grand que la médiane : True
```

**Questions.** (a) Pourquoi la réponse ne contient-elle que la probabilité et la version, pas la liste des variables ? (b) Que se passerait-il si le modèle était rechargé **à chaque requête** ? (c) Un client envoie `"appareil": null` : la requête est-elle acceptée ? Pourquoi ? *(Réponses : (a) minimiser ce qui sort (sécurité, 4.6) ; (b) le chargement coûte bien plus que la prédiction, d'où le chargement unique au démarrage ; (c) oui, `appareil` est facultatif dans le contrat, le modèle gère l'absence de valeur.)*

### Application 4.3 — Un déploiement canari avec retour arrière automatique

*Sections du livre : 4.2.* **Objectif** : simuler une semaine de canari où la nouvelle version a un **défaut** dans sa préparation des données, repérer le défaut par un indicateur, et revenir en arrière en changeant l'alias.

**Étape 1 — le routage.** Chaque client est dirigé vers la version « champion » ou « canari » par le hash de son identifiant ; on vérifie que la part réelle est proche de la part annoncée.

```python
def dans_canari(id_client, part_canari):
    return int(hashlib.sha256(str(id_client).encode()).hexdigest(), 16) % 100 < part_canari

def version_servie(id_client, part_canari, alias):
    return alias["canari"] if dans_canari(id_client, part_canari) else alias["champion"]

alias = {"champion": "1.0.0", "canari": "2.0.0"}
servies = np.array([version_servie(i, 10, alias) for i in range(len(Xpool))])
print("part effectivement servie par le canari :", round(100 * (servies == "2.0.0").mean(), 1), "% (annoncé : 10 %)")
```
<!--sortie-->
```text
part effectivement servie par le canari : 10.4 % (annoncé : 10 %)
```

**Étape 2 — une semaine de trafic.** Chaque jour, 2 000 clients sont tirés (avec remise) du réservoir. Le champion (`v1`) répond aux clients dirigés vers lui ; le canari (`v2`) aux autres. **À partir du jour 4**, un bug de l'équipe fait que le canari reçoit la récence **en semaines** (comme en 4.1). L'indicateur surveillé est l'écart entre le score moyen du canari et celui du champion ; la règle : si l'écart dépasse 0,03 **deux jours de suite**, on retourne en arrière.

```python
rng = np.random.default_rng(42)
lignes, alerte_veille = [], False
for jour in range(1, 8):
    idx = rng.integers(0, len(Xpool), 2000)
    lot = Xpool.iloc[idx]
    est_canari = np.array([dans_canari(i, 10) for i in idx])
    mod_canari = v2 if alias["canari"] == "2.0.0" else v1                                    # ce que l'alias désigne
    lot_c = lot[est_canari]
    if jour >= 4 and mod_canari is v2:
        lot_c = lot_c.assign(recence_jours=lot_c["recence_jours"] / 7)                         # le bug de la version 2
    m_champ = v1.predict_proba(lot[~est_canari])[:, 1].mean()
    m_can = mod_canari.predict_proba(lot_c)[:, 1].mean()
    ecart = abs(m_can - m_champ)
    alerte = bool(ecart > 0.03)
    if alerte and alerte_veille and mod_canari is v2:
        alias["canari"] = "1.0.0"                                                           # retour arrière : on déplace l'alias
    lignes.append((jour, round(100 * est_canari.mean(), 1), round(m_champ, 3), round(m_can, 3), round(ecart, 3), alerte, alias["canari"]))
    alerte_veille = alerte
print(pd.DataFrame(lignes, columns=["jour", "% canari", "score champion", "score canari", "écart", "alerte", "alias canari ensuite"]).to_string(index=False))
```
<!--sortie-->
```text
 jour  % canari  score champion  score canari  écart  alerte alias canari ensuite
    1       9.8           0.138         0.136  0.002   False                2.0.0
    2       9.4           0.141         0.136  0.005   False                2.0.0
    3      10.8           0.144         0.124  0.020   False                2.0.0
    4       9.9           0.137         0.053  0.083    True                2.0.0
    5      10.1           0.132         0.063  0.069    True                1.0.0
    6       9.6           0.129         0.148  0.019   False                1.0.0
    7      10.8           0.130         0.149  0.020   False                1.0.0
```


**Lecture.** Les trois premiers jours, l'écart est de l'ordre du bruit d'échantillonnage (le canari ne voit qu'environ 200 clients par jour) : pas d'alerte. Le jour 4, le bug fait chuter le score moyen du canari ; une alerte seule peut être du bruit, **deux jours de suite** est un signal, et l'alias est ramené sur la version 1 au jour 5. Les jours suivants, tous les clients reçoivent le champion : le service n'a jamais été interrompu et **aucun code n'a été modifié**.

**Pour aller plus loin.** (1) Remplacez la règle « 0,03 deux jours de suite » par « 0,02 un seul jour » : combien de fausses alertes obtenez-vous avant le jour 4 sur 200 historiques simulés ? (2) Changez la part du canari à 2 % : le bug est-il toujours détecté, et en combien de jours ? Reliez la réponse au calcul du nombre de clients nécessaires donné dans le livre.

### Application 4.4 — Le journal des prédictions et les étiquettes tardives

*Sections du livre : 4.3.* **Objectif** : journaliser soixante jours de prédictions, mesurer la performance **à mesure que les étiquettes arrivent**, et comparer à l'estimation sans étiquettes.

**Étape 1 — journaliser.** Chaque jour, 40 clients du réservoir demandent un score. Le service écrit une ligne JSON par prédiction : identifiant, jour, version, probabilité, quelques entrées de surveillance.

```python
def journaliser(fichier, id_pred, jour, client, proba, version):
    ligne = {"id": id_pred, "jour": jour, "version": version, "proba": round(proba, 4),
             "entrees": {k: client[k] for k in ("recence_jours", "satisfaction_moy", "part_achats_promo")}}
    with open(fichier, "a") as f:
        f.write(json.dumps(ligne) + "\n")

fichier_journal = os.path.join(WORK, "journal.jsonl")
sp = v2.predict_proba(Xpool)[:, 1]
for i in range(len(Xpool)):
    journaliser(fichier_journal, i, i // 40, ligne_json(Xpool.iloc[i]), float(sp[i]), "2.0.0")
journal = pd.read_json(fichier_journal, lines=True)
print(len(journal), "lignes sur", journal["jour"].nunique(), "jours ; colonnes :", list(journal.columns))
```
<!--sortie-->
```text
2400 lignes sur 60 jours ; colonnes : ['id', 'jour', 'version', 'proba', 'entrees']
```

**Étape 2 — les étiquettes arrivent 90 jours plus tard.** On définit une fonction qui rapproche le journal des étiquettes disponibles **à une date d'observation** (seules les prédictions de plus de 90 jours ont leur étiquette) et rend l'AUC avec un intervalle de confiance par rééchantillonnage.

```python
etiq = pd.Series(d["ypool"])
rng = np.random.default_rng(1)

def performance_a_la_date(obs, rep=300):
    mur = journal[journal["jour"] + 90 <= obs]
    y_m, p_m = etiq.loc[mur["id"]].to_numpy(), mur["proba"].to_numpy()
    bs = [roc_auc_score(y_m[k], p_m[k]) for k in (rng.integers(0, len(y_m), len(y_m)) for _ in range(rep))]
    return len(mur), roc_auc_score(y_m, p_m), *np.percentile(bs, [2.5, 97.5])

dates = [100, 110, 120, 130, 140, 150]
res = pd.DataFrame([(o, *performance_a_la_date(o)) for o in dates], columns=["jour d'observation", "étiquetées", "AUC", "bas", "haut"])
res["largeur"] = res["haut"] - res["bas"]
print(res.round(3).to_string(index=False))
```
<!--sortie-->
```text
 jour d'observation  étiquetées   AUC   bas  haut  largeur
                100         440 0.884 0.834 0.925    0.092
                110         840 0.871 0.837 0.904    0.067
                120        1240 0.874 0.849 0.897    0.048
                130        1640 0.874 0.849 0.898    0.049
                140        2040 0.881 0.858 0.899    0.041
                150        2400 0.888 0.871 0.907    0.036
```


**Lecture.** L'intervalle se resserre à mesure que des prédictions mûrissent : de 0,092 de large au jour 100 à 0,036 au jour 150 ; on dispose d'un intervalle plus étroit que 0,06 à partir du jour 120. **C'est le retard de la métrique réelle** : un modèle déployé le jour 0 n'est jugé de façon fiable qu'après plus de trois mois.

**Étape 3 — l'estimation sans étiquettes, semaine par semaine.** On compare la précision attendue des clients signalés (score au moins égal à 0,30, somme des probabilités) à la précision réellement observée **une fois toutes les étiquettes arrivées**.

```python
journal["resilie"] = etiq.loc[journal["id"]].to_numpy()
journal["semaine"] = journal["jour"] // 7
sig = journal[journal["proba"] >= 0.30]
par_semaine = sig.groupby("semaine").agg(signales=("proba", "size"), attendue=("proba", "mean"), reelle=("resilie", "mean")).round(3)
print(par_semaine.to_string())
```
<!--sortie-->
```text
         signales  attendue  reelle
semaine                            
0              34     0.606   0.618
1              40     0.601   0.500
2              35     0.631   0.657
3              42     0.609   0.786
4              34     0.623   0.500
5              41     0.581   0.561
6              44     0.637   0.477
7              42     0.626   0.643
8              29     0.601   0.621
```

**Question.** Les colonnes `attendue` et `reelle` varient d'une semaine à l'autre ; l'écart est-il plus grand que ce que le hasard explique avec une quarantaine de clients signalés ? Calculez l'erreur-type $\sqrt{p(1-p)/n}$ pour une semaine et comparez. *(Avec $p\approx0{,}6$ et $n\approx40$, l'erreur-type vaut environ 0,08 : des écarts de 5 à 15 points entre semaines ne prouvent rien.)*

### Application 4.5 — Orchestrer un pipeline d'entraînement

*Sections du livre : 4.4, 4.1.* **Objectif** : déclarer le graphe « charger → valider → entraîner → évaluer → publier » dans le mini-orchestrateur, observer reprises, tâches ignorées et rattrapage, et vérifier l'idempotence de la publication.

**Étape 1 — les tâches.** Chaque exécution (« jour logique ») entraîne une régression logistique sur un instantané des données d'entraînement. Deux incidents sont programmés : le jour 1, le chargement échoue deux fois (panne transitoire) ; le jour 2, l'instantané est **tronqué** (150 clients au lieu de 3 000) et le modèle appris est mauvais. La publication écrit dans un registre JSON par **mise à jour selon la clé** (idempotente).

```python
ORCH = os.path.join(WORK, "orch"); os.makedirs(ORCH, exist_ok=True)
registre_json = os.path.join(ORCH, "registre.json")
TRONQUE, PANNES, tentatives, appris = {2}, {1: 2}, {}, {}

def instantane(jour):
    n = 150 if jour in TRONQUE else 3000
    return Xtr.sample(n, random_state=jour)

orch = MiniOrchestrateur(reprises=2)

@orch.tache("charger")
def charger(jour):
    tentatives[jour] = tentatives.get(jour, 0) + 1
    if tentatives[jour] <= PANNES.get(jour, 0):
        raise ConnectionError("entrepôt injoignable")
    instantane(jour).to_csv(os.path.join(ORCH, f"snap_{jour}.csv"))

@orch.tache("valider", depend_de=["charger"])
def valider(jour):
    assert len(pd.read_csv(os.path.join(ORCH, f"snap_{jour}.csv"))) >= 1000, "instantané trop petit"

@orch.tache("entrainer", depend_de=["valider"])
def entrainer(jour):
    snap = pd.read_csv(os.path.join(ORCH, f"snap_{jour}.csv"), index_col=0)
    appris[jour] = modele_v1(dict(d, Xtr=snap, ytr=ytr.loc[snap.index]))

@orch.tache("evaluer", depend_de=["entrainer"])
def evaluer(jour):
    auc = roc_auc_score(yte, appris[jour].predict_proba(Xte)[:, 1])
    assert auc >= 0.85, f"AUC {auc:.3f} sous le seuil"

@orch.tache("publier", depend_de=["evaluer"])
def publier(jour):
    reg = json.load(open(registre_json)) if os.path.exists(registre_json) else {}
    reg[str(jour)] = {"auc": round(roc_auc_score(yte, appris[jour].predict_proba(Xte)[:, 1]), 4)}       # clé = jour : écrase, n'ajoute pas
    json.dump(reg, open(registre_json, "w"))
```

**Étape 2 — quatre jours d'exécution.**

```python
etats = {j: orch.lancer(j) for j in range(4)}
print(pd.DataFrame(etats).T.to_string())
journal_orch = pd.DataFrame(orch.journal, columns=["jour", "tâche", "essai", "état"])
print(journal_orch[(journal_orch["jour"] == 1) & (journal_orch["tâche"] == "charger")].to_string(index=False))
```
<!--sortie-->
```text
  charger valider entrainer  evaluer  publier
0      ok      ok        ok       ok       ok
1      ok      ok        ok       ok       ok
2      ok   échec   ignorée  ignorée  ignorée
3      ok      ok        ok       ok       ok
 jour   tâche  essai                    état
    1 charger      1 échec (ConnectionError)
    1 charger      2 échec (ConnectionError)
    1 charger      3                      ok
```

**Lecture.** Le jour 1 a réussi malgré la panne (trois essais pour `charger`) ; le jour 2 est arrêté par la validation (**aucune reprise ne peut corriger** un instantané trop petit) et les trois tâches suivantes sont ignorées : un modèle entraîné sur 150 clients n'a pas été publié.

**Étape 3 — corriger et rattraper.** La source est réparée. On relance **seulement** le jour 2, puis, pour vérifier l'idempotence, on rejoue **tous** les jours et on regarde le registre.

```python
TRONQUE.clear()
print("jour 2 après correction :", orch.lancer(2))
avant = json.load(open(registre_json))
for j in range(4):
    orch.lancer(j)
apres = json.load(open(registre_json))
print("clés du registre :", sorted(apres), "| identique après rejeu complet :", avant == apres)
```
<!--sortie-->
```text
jour 2 après correction : {'charger': 'ok', 'valider': 'ok', 'entrainer': 'ok', 'evaluer': 'ok', 'publier': 'ok'}
clés du registre : ['0', '1', '2', '3'] | identique après rejeu complet : True
```


**Pour aller plus loin.** Remplacez la publication par une version qui **ajoute** une ligne à un fichier à chaque appel : rejouez les quatre jours et comptez les lignes. Quelle règle de conception du livre (4.4) cela illustre-t-il ?

### Application 4.6 — Suivre une recherche d'hyperparamètres avec MLflow

*Sections du livre : 4.5.* **Objectif** : enregistrer six essais, choisir sur la **validation croisée**, enregistrer deux versions dans le registre, déplacer un alias et remonter jusqu'au hash des données.

**Étape 1 — le magasin de suivi** (SQLite temporaire) et la fonction qui enregistre un essai. Le modèle est enregistré au format `skops`, qui exige de **déclarer** les types que l'on accepte de recharger.

```python
import logging, mlflow, mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.base import clone
from sklearn.model_selection import cross_val_score
logging.getLogger("mlflow").setLevel(logging.ERROR)
APPROUVES = ["numpy.dtype", "functools.partial", "sklearn.utils.validation.check_array",
             "sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"]
mlflow.set_tracking_uri(f"sqlite:///{WORK}/mlflow.db")
mlflow.create_experiment("recherche", artifact_location=f"file://{WORK}/artefacts"); mlflow.set_experiment("recherche")

def enregistrer(nom, modele, params):
    with mlflow.start_run(run_name=nom):
        mlflow.log_params({**params, "graine": 0, "hash_donnees": hash_fichier("donnees/clients_ml.csv")})
        mlflow.log_metric("auc_cv", cross_val_score(modele, Xtr, ytr, cv=3, scoring="roc_auc").mean())
        mlflow.log_metric("auc_test", roc_auc_score(yte, modele.fit(Xtr, ytr).predict_proba(Xte)[:, 1]))
        mlflow.sklearn.log_model(modele, name="modele", skops_trusted_types=APPROUVES)
```

**Étape 2 — six essais tirés au hasard** dans une grille (pas d'apprentissage × nombre maximal de feuilles).

```python
grille = [(lr, nf) for lr in (0.03, 0.05, 0.1, 0.2) for nf in (7, 15, 31)]
choix = np.random.default_rng(0).choice(len(grille), 6, replace=False)
for k in choix:
    lr, nf = grille[k]
    enregistrer(f"hgb lr={lr} feuilles={nf}", clone(v2).set_params(clf__learning_rate=lr, clf__max_leaf_nodes=nf),
                {"clf__learning_rate": lr, "clf__max_leaf_nodes": nf})
essais = mlflow.search_runs(experiment_names=["recherche"], order_by=["metrics.auc_cv DESC"])
print(essais[["tags.mlflow.runName", "metrics.auc_cv", "metrics.auc_test"]].round(4).rename(columns=lambda c: c.split(".")[-1]).to_string(index=False))
```
<!--sortie-->
```text
                runName  auc_cv  auc_test
 hgb lr=0.05 feuilles=7  0.8953    0.9044
 hgb lr=0.03 feuilles=7  0.8932    0.9005
hgb lr=0.05 feuilles=15  0.8930    0.9023
hgb lr=0.05 feuilles=31  0.8907    0.8977
hgb lr=0.03 feuilles=31  0.8901    0.8952
 hgb lr=0.1 feuilles=15  0.8879    0.9000
```

**Étape 3 — le registre.** On enregistre le meilleur et le deuxième essai comme versions 1 et 2 du modèle `resiliation_hgb`, on donne l'alias `champion` à la version 1 et `challenger` à la version 2, on promeut le challenger puis on revient en arrière.

```python
reg = MlflowClient()
v_a = mlflow.register_model(f"runs:/{essais.loc[0, 'run_id']}/modele", "resiliation_hgb").version
v_b = mlflow.register_model(f"runs:/{essais.loc[1, 'run_id']}/modele", "resiliation_hgb").version
reg.set_registered_model_alias("resiliation_hgb", "champion", v_a); reg.set_registered_model_alias("resiliation_hgb", "challenger", v_b)
aliases = lambda: {a: reg.get_model_version_by_alias("resiliation_hgb", a).version for a in ("champion", "challenger")}
print("départ     :", aliases())
reg.set_registered_model_alias("resiliation_hgb", "champion", v_b); print("promotion  :", aliases())
reg.set_registered_model_alias("resiliation_hgb", "champion", v_a); print("retour     :", aliases())
```
<!--sortie-->
```text
départ     : {'champion': 1, 'challenger': 2}
promotion  : {'champion': 2, 'challenger': 2}
retour     : {'champion': 1, 'challenger': 2}
```

**Étape 4 — remonter la chaîne.** À partir de l'alias `champion`, on retrouve l'essai, ses paramètres et le hash des données ; on le compare au hash du fichier actuel, et l'on vérifie que le modèle rechargé par l'alias donne les mêmes probabilités que celui de l'essai.

```python
vc = reg.get_model_version_by_alias("resiliation_hgb", "champion")
run = reg.get_run(vc.run_id)
print("paramètres :", {k: v for k, v in run.data.params.items() if k.startswith("clf")}, "| données identiques :",
      run.data.params["hash_donnees"] == hash_fichier("donnees/clients_ml.csv"))
charge = mlflow.sklearn.load_model("models:/resiliation_hgb@champion")
print("écart maximal avec le modèle de l'essai :", float(np.abs(charge.predict_proba(Xte)[:, 1] - mlflow.sklearn.load_model(f"runs:/{vc.run_id}/modele").predict_proba(Xte)[:, 1]).max()))
```
<!--sortie-->
```text
paramètres : {'clf__learning_rate': '0.05', 'clf__max_leaf_nodes': '7'} | données identiques : True
écart maximal avec le modèle de l'essai : 0.0
```


**Questions.** (a) Le meilleur essai en validation croisée est-il aussi le meilleur sur le jeu de test ? Si ce n'est pas le cas, lequel devrait-on croire, et pourquoi ? (b) Quel élément manque encore à cette chaîne pour que l'essai soit **entièrement** reproductible (4.1) ? *(Réponses : (a) la validation croisée, car le test sert à juger **une fois** ; (b) la version du code (numéro de commit) et celle de l'environnement, qu'il faudrait ajouter comme étiquettes de l'essai.)*

### Application 4.7 — Une porte de qualité, une « intégration continue » et un service protégé

*Sections du livre : 4.6.* **Objectif** : écrire la porte qui décide si un candidat est publié, la faire tourner comme le ferait un outil de CI (un programme dont le **code de sortie** dit si tout va bien), charger la configuration depuis l'environnement et protéger une API par une clé et une limite de débit.

**Étape 1 — la porte.** Un candidat est publié s'il atteint un plancher **et** ne régresse pas par rapport au champion.

```python
def porte_qualite(candidat, champion, lot, y, plancher=0.85, tolerance=0.005):
    auc_c, auc_p = (roc_auc_score(y, m.predict_proba(lot)[:, 1]) for m in (candidat, champion))
    verdicts = {f"AUC ≥ {plancher}": auc_c >= plancher, f"régression ≤ {tolerance}": auc_c >= auc_p - tolerance}
    return all(verdicts.values()), round(auc_c, 3), verdicts

faible = modele_v1(dict(d, Xtr=Xtr.iloc[:300], ytr=ytr.iloc[:300]))                       # entraîné sur 300 clients seulement
for nom, cand in [("boosting (v2)", v2), ("logistique sur 300 clients", faible)]:
    ok, auc, verdicts = porte_qualite(cand, v1, Xte, yte)
    print(f"{nom:28s} AUC {auc} → {'publié' if ok else 'REFUSÉ'}  {verdicts}")
```
<!--sortie-->
```text
boosting (v2)                AUC 0.893 → publié  {'AUC ≥ 0.85': True, 'régression ≤ 0.005': True}
logistique sur 300 clients   AUC 0.818 → REFUSÉ  {'AUC ≥ 0.85': False, 'régression ≤ 0.005': False}
```

**Étape 2 — comme un outil de CI.** Un outil d'intégration continue ne lit pas un affichage : il lance un programme et regarde son **code de sortie** (0 : tout va bien ; autre chose : échec, la chaîne s'arrête). On écrit le contrôle dans un petit script, que l'on exécute dans un **processus séparé** pour chacun des deux candidats.

```python
import subprocess
script = os.path.join(WORK, "controle.py")
open(script, "w").write('''import sys, joblib
sys.path.insert(0, "build")
from outils_ch04 import donnees
from sklearn.metrics import roc_auc_score
d = donnees()
auc = roc_auc_score(d["yte"], joblib.load(sys.argv[1]).predict_proba(d["Xte"])[:, 1])
print(f"AUC {auc:.3f}")
sys.exit(0 if auc >= 0.85 else 1)
''')
for nom, cand in [("boosting", v2), ("faible", faible)]:
    chemin = os.path.join(WORK, f"cand_{nom}.joblib"); joblib.dump(cand, chemin)
    r = subprocess.run([sys.executable, script, chemin], capture_output=True, text=True)
    print(f"{nom:9s} → code de sortie {r.returncode} ({r.stdout.strip()})")
```
<!--sortie-->
```text
boosting  → code de sortie 0 (AUC 0.893)
faible    → code de sortie 1 (AUC 0.818)
```

**Étape 3 — la configuration par l'environnement.** Les valeurs qui changent entre test et production sont lues dans l'environnement ; l'absence d'une valeur obligatoire est une **erreur immédiate**.

```python
def charger_config(env):
    return {"alias": env.get("MODELE_ALIAS", "champion"), "seuil": float(env.get("SEUIL_ALERTE", "0.30")),
            "registre": env["URL_REGISTRE"]}

for env in ({"URL_REGISTRE": "sqlite:///exemple", "SEUIL_ALERTE": "0.25"}, {"MODELE_ALIAS": "challenger"}):
    try:
        print(charger_config(env))
    except KeyError as e:
        print("configuration incomplète, variable absente :", e)
```
<!--sortie-->
```text
{'alias': 'champion', 'seuil': 0.25, 'registre': 'sqlite:///exemple'}
configuration incomplète, variable absente : 'URL_REGISTRE'
```

**Étape 4 — une API protégée.** Chaque appel doit présenter une clé ; chaque clé est limitée à trois appels.

```python
from fastapi import FastAPI, Header, HTTPException
protege, appels = FastAPI(), {}
CLES = {"cle-de-test"}                                                    # exemple seulement : jamais de secret dans le code

@protege.get("/score")
def score(x_api_key: str = Header(default="")):
    if x_api_key not in CLES:
        raise HTTPException(401, "clé absente ou invalide")
    appels[x_api_key] = appels.get(x_api_key, 0) + 1
    if appels[x_api_key] > 3:
        raise HTTPException(429, "trop de requêtes")
    return {"ok": True}

cp = TestClient(protege)
codes = [cp.get("/score").status_code, cp.get("/score", headers={"x-api-key": "mauvaise"}).status_code]
codes += [cp.get("/score", headers={"x-api-key": "cle-de-test"}).status_code for _ in range(4)]
print(codes)
```
<!--sortie-->
```text
[401, 401, 200, 200, 200, 429]
```


**Lecture.** Le candidat entraîné sur 300 clients est refusé à la fois par le plancher et par la non-régression ; le script de CI sort avec le code 1 et la chaîne s'arrête. Le 401 est rendu **avant** tout calcul, le 429 **à partir du quatrième** appel valide.

### Application 4.8 — Un mois de production : quelles variables ont dérivé, et est-ce grave ?

*Sections du livre : 4.7.* **Objectif** : repérer quelles variables dérivent (PSI), **pondérer** par leur importance, confronter l'alerte sur les entrées à l'alerte sur la performance, et mesurer la sensibilité du PSI au découpage.

**Étape 1 — le PSI de chaque variable, semaine 4, dérive des variables.**

```python
Xw, yw = semaine(d, v2, 4, "covariable")
psis = pd.Series({c: psi(Xtr[c], Xw[c]) for c in d["num"]}).sort_values(ascending=False)
print(psis.round(3).head(6).to_string())
```
<!--sortie-->
```text
part_achats_promo         0.795
satisfaction_moy          0.713
nb_promos_recues_12m      0.460
panier_moyen              0.258
nb_tickets_support_12m    0.169
taux_ouverture_email      0.161
```

**Étape 2 — pondérer par l'importance.** Une variable qui dérive mais pèse peu dans le modèle compte moins. On mesure l'importance par **permutation** sur le jeu de test (la baisse d'AUC quand on mélange la variable, volume III).

```python
from sklearn.inspection import permutation_importance
imp = pd.Series(permutation_importance(v2, Xte, yte, scoring="roc_auc", n_repeats=3, random_state=0).importances_mean, index=COLONNES)
tab = pd.DataFrame({"PSI": psis, "importance": imp[psis.index]}).head(8)
print(tab.round(3).to_string())
```
<!--sortie-->
```text
                          PSI  importance
part_achats_promo       0.795       0.017
satisfaction_moy        0.713       0.039
nb_promos_recues_12m    0.460       0.002
panier_moyen            0.258       0.001
nb_tickets_support_12m  0.169       0.000
taux_ouverture_email    0.161      -0.000
montant_12m             0.101       0.055
age                     0.097       0.060
```


**Lecture.** Les variables qui dérivent le plus (la part d'achats en promotion, la satisfaction) ne sont **pas** les plus importantes pour le modèle (ce sont ici l'âge et le montant dépensé, dont le PSI reste proche de 0,1). Un PSI très élevé sur une variable peu importante est un signal à surveiller, pas à paniquer : pondérer par l'importance évite des alertes inutiles.

**Étape 3 — alerte sur les entrées contre alerte sur la performance.** Pour chaque scénario et chaque semaine, on déclenche une alerte « entrées » si le PSI de la part d'achats en promotion dépasse 0,25, et une alerte « performance » si l'AUC (étiquettes arrivées) a perdu plus de 0,05 par rapport à la semaine 1.

```python
lignes = []
for scenario in ("covariable", "concept"):
    auc1 = None
    for k in range(1, 5):
        Xw, yw = semaine(d, v2, k, scenario)
        auc = roc_auc_score(yw, v2.predict_proba(Xw)[:, 1]); auc1 = auc1 or auc
        lignes.append((scenario, k, round(psi(Xtr["part_achats_promo"], Xw["part_achats_promo"]), 3), round(auc, 3),
                       psi(Xtr["part_achats_promo"], Xw["part_achats_promo"]) > 0.25, auc < auc1 - 0.05))
res = pd.DataFrame(lignes, columns=["scénario", "semaine", "PSI promo", "AUC", "alerte entrées", "alerte performance"])
print(res.to_string(index=False))
```
<!--sortie-->
```text
  scénario  semaine  PSI promo   AUC  alerte entrées  alerte performance
covariable        1      0.015 0.876           False               False
covariable        2      0.106 0.859           False               False
covariable        3      0.345 0.869            True               False
covariable        4      0.795 0.857            True               False
   concept        1      0.015 0.876           False               False
   concept        2      0.023 0.847           False               False
   concept        3      0.008 0.808           False                True
   concept        4      0.002 0.776           False                True
```


**Lecture.** Dans la dérive des variables, l'alerte sur les entrées se déclenche et l'alerte sur la performance **non** : le modèle reste bon. Dans la dérive du concept, c'est l'inverse : **aucune alerte sur les entrées**, mais la performance s'effondre. Aucune des deux alertes ne suffit seule ; il faut surveiller les deux.

**Étape 4 — le PSI dépend du découpage.** Même variable, même semaine, trois nombres d'intervalles.

```python
Xw, _ = semaine(d, v2, 4, "covariable")
print({k: round(psi(Xtr["part_achats_promo"], Xw["part_achats_promo"], k=k), 3) for k in (5, 10, 20)})
```
<!--sortie-->
```text
{5: 0.753, 10: 0.795, 20: 0.815}
```

**Question.** Les seuils de 0,1 et 0,25 sont-ils des lois ? Que changer si l'on passe de 10 à 20 intervalles ? *(Non : des repères conventionnels, calibrés pour environ 10 intervalles et des échantillons d'au moins quelques centaines ; un découpage plus fin augmente le PSI à effectifs égaux, et il faut recalibrer les seuils sur des périodes calmes.)*

### Application 4.9 — Une chaîne complète, de l'entraînement à la supervision

*Sections du livre : 4.1 à 4.7.* **Objectif** : assembler en un seul parcours les briques du chapitre : un candidat est entraîné, testé, soumis à la porte de qualité, enregistré, servi par une API, journalisé en production, puis jugé quand les étiquettes arrivent. Chaque étape **s'arrête** si son contrôle échoue.

```python
rapport = {}
# 1. candidat et tests de données
candidat = clone(v2).set_params(clf__learning_rate=0.05)
res_tests = verifier(Xte, v2)
rapport["tests de données"] = all(v for v in res_tests.values() if v is not None)
# 2. porte de qualité (face au champion v1)
candidat.fit(Xtr, ytr)
ok_porte, auc_cand, _ = porte_qualite(candidat, v1, Xte, yte)
rapport["porte de qualité"] = ok_porte
assert all(rapport.values()), rapport                                           # sinon la chaîne s'arrête ici
```

```python
# 3. enregistrement dans le registre (suivi + version + alias)
mlflow.create_experiment("chaine", artifact_location=f"file://{WORK}/artefacts_chaine"); mlflow.set_experiment("chaine")
enregistrer("candidat lr=0.05", clone(v2).set_params(clf__learning_rate=0.05), {"clf__learning_rate": 0.05})
run_id = mlflow.search_runs(experiment_names=["chaine"]).loc[0, "run_id"]
version = mlflow.register_model(f"runs:/{run_id}/modele", "resiliation_chaine").version
reg.set_registered_model_alias("resiliation_chaine", "champion", version)
rapport["registre : alias champion"] = reg.get_model_version_by_alias("resiliation_chaine", "champion").version == version
# 4. service : le modèle est chargé depuis l'alias, puis servi par l'API
en_service = mlflow.sklearn.load_model("models:/resiliation_chaine@champion")
chemin_service = os.path.join(WORK, "service.joblib"); joblib.dump(en_service, chemin_service)
api2 = TestClient(creer_app(chemin_service, COLONNES, version=f"registre-v{version}"))
rapport["service : /health"] = api2.get("/health").status_code == 200
```

```python
# 5. production : 300 requêtes journalisées (jours 0 à 5, 50 clients par jour)
journal2 = os.path.join(WORK, "journal2.jsonl")
for i in range(300):
    rep = api2.post("/predict", json=ligne_json(Xpool.iloc[i])).json()
    journaliser(journal2, i, i // 50, ligne_json(Xpool.iloc[i]), rep["probabilite"], rep["version"])
j2 = pd.read_json(journal2, lines=True)
# 6. les étiquettes arrivent : performance réelle et dérive des entrées
y_prod = d["ypool"][j2["id"].to_numpy()]
auc_prod = roc_auc_score(y_prod, j2["proba"])
psi_max = max(psi(Xtr[c], Xpool.iloc[:300][c]) for c in d["num"])
rapport["performance réelle ≥ 0,80"] = bool(auc_prod >= 0.80)
rapport["dérive des entrées (PSI max < 0,25)"] = bool(psi_max < 0.25)
print(pd.Series(rapport).to_string())
print(f"AUC test du candidat : {auc_cand} | AUC sur 300 prédictions étiquetées : {auc_prod:.3f} | PSI maximal : {psi_max:.3f}")
```
<!--sortie-->
```text
tests de données                       True
porte de qualité                       True
registre : alias champion              True
service : /health                      True
performance réelle ≥ 0,80              True
dérive des entrées (PSI max < 0,25)    True
AUC test du candidat : 0.898 | AUC sur 300 prédictions étiquetées : 0.901 | PSI maximal : 0.079
```


**Lecture.** Le parcours passe tous les contrôles. Remarquez deux choses. D'abord, l'AUC sur **300 prédictions seulement** est entourée d'une grande incertitude (application 4.4) : elle sert à vérifier qu'il n'y a pas d'effondrement, pas à classer deux versions. Ensuite, chaque ligne du rapport correspond à une section du chapitre : tests et porte (4.1, 4.6), registre (4.5), service (4.2), journal et étiquettes (4.3), dérive (4.7).

**Pour aller plus loin.** Cassez volontairement une étape (envoyez la récence en semaines à l'étape 5 ; entraînez le candidat sur 300 clients ; changez `0.80` en `0.95`) et notez **quelle ligne du rapport échoue en premier**, et si c'est bien celle que vous attendiez.

## Exercices

### Exercice 4.1 ⭐ — Que manque-t-il pour reproduire ? (section 4.1)

Pour chacune des trois situations, dites lequel des cinq éléments de la liste de reproductibilité (graines, versions, empreinte des données, configuration, code) fait défaut. (a) En ré-entraînant le modèle de la semaine dernière sur les mêmes données avec le même code, une forêt aléatoire rend des probabilités légèrement différentes. (b) Après une mise à jour de l'environnement, l'AUC baisse de 0,01 alors que rien n'a changé dans le code ni les données. (c) Un fichier de données a été corrigé à la main sur un poste ; personne ne sait si tel modèle a été appris avant ou après la correction.

### Exercice 4.2 ⭐⭐ — Une échelle de satisfaction qui change (section 4.1)

La satisfaction moyenne est notée de 1 à 5 à l'entraînement. Un nouveau canal d'export l'envoie **en pourcentage** (note × 20). Mesurez, pour la régression logistique `v1` et pour le boosting `v2`, l'AUC et la probabilité moyenne prédite sur le jeu de test. Lequel des deux modèles est le plus sensible à cette erreur, et pourquoi ?

### Exercice 4.3 ⭐⭐ — Exporter la régression logistique en ONNX (section 4.2)

Construisez à la main le graphe ONNX de la partie linéaire de `v1` (produit matriciel avec biais, puis sigmoïde), exécutez-le avec `onnxruntime` sur les variables **préparées**, et mesurez l'écart avec `predict_proba`. Que se passe-t-il si l'on envoie au graphe les variables **non préparées** (sans imputation ni mise à l'échelle) ?

### Exercice 4.4 ⭐⭐ — Latence, débit, disponibilité (sections 4.2 et 4.3)

(a) Le site envoie 300 requêtes par seconde, chacune dure 80 ms, et un pod en traite 5 à la fois. Combien de pods faut-il, avec une marge de 25 % ? (b) Un objectif de disponibilité de 99,9 % sur 30 jours : combien de minutes d'indisponibilité le budget d'erreur autorise-t-il ? (c) Une page fait trois appels successifs au service ; chaque appel a 95 % de chances d'être sous le centile p95 (par définition). Quelle est la probabilité que les trois le soient, en supposant les appels indépendants ? Qu'en conclut-on sur l'engagement de service ?

### Exercice 4.5 ⭐⭐⭐ — Choisir la règle d'alerte au moindre coût (section 4.3)

On surveille le score moyen quotidien d'un service (200 clients par jour). Les 30 premiers jours servent de référence ; une dérive modérée commence au jour 61 (celle du livre). Comparez cinq règles : $|z|>2$, $|z|>2{,}5$, $|z|>3$, et les deux premières exigées **deux jours de suite**. Chaque fausse alerte (sur les 30 jours calmes qui suivent la référence) coûte 1 unité, chaque jour de retard de détection coûte 3 unités. Quelle règle minimise le coût moyen sur 150 historiques simulés ?

### Exercice 4.6 ⭐⭐ — Rendre une publication idempotente (section 4.4)

Une tâche « publier » ajoute à la fin d'un fichier unique les scores du jour. Après une reprise, les scores du jour sont en double. Écrivez deux versions de la tâche : l'ancienne et une version **idempotente** (une partition par jour que l'on écrase), puis prouvez la différence en exécutant chaque version deux fois pour le même jour.

### Exercice 4.7 ⭐⭐ — Un seul octet change tout… ou presque (section 4.5)

Créez une copie du fichier de données où l'âge de cinq clients est augmenté de 1. Comparez les hash des deux fichiers, puis entraînez `v1` sur chacune des deux versions : de combien l'AUC de test et les probabilités prédites changent-elles ? Que conclure sur l'utilité du hash, plutôt que de la comparaison des performances, pour la traçabilité ?

### Exercice 4.8 ⭐⭐ — Tester les cas limites d'une API (section 4.6)

Écrivez des tests de contrat pour `/predict_batch` : (a) une liste vide, (b) un seul client, (c) une liste de 10 clients dont le **quatrième** est invalide (âge de 17 ans), (d) un client avec un champ supplémentaire inconnu. Quels codes de statut attendez-vous ? Pour (c), où le message d'erreur désigne-t-il l'élément fautif ?

### Exercice 4.9 ⭐⭐ — Limiter le débit par fenêtre de temps (section 4.6)

Écrivez un limiteur de débit à **fenêtre fixe** : au plus 3 appels par clé et par fenêtre de 60 secondes. Pour pouvoir le tester sans attendre, la fonction reçoit l'instant courant en argument. Vérifiez : trois appels acceptés, le quatrième refusé, puis de nouveau accepté dans la fenêtre suivante.

### Exercice 4.10 ⭐⭐ — Un PSI à la main (section 4.7)

La référence a pour parts $p=(0{,}4;\,0{,}3;\,0{,}2;\,0{,}1)$ dans quatre intervalles, la période récente $q=(0{,}25;\,0{,}25;\,0{,}25;\,0{,}25)$. Calculez le PSI, la contribution de chaque intervalle, et vérifiez que le PSI est la somme de $\mathrm{KL}(q\|p)$ et de $\mathrm{KL}(p\|q)$. Quel intervalle contribue le plus ?

### Exercice 4.11 ⭐⭐⭐ — Boucle de rétroaction et groupe témoin (section 4.7)

Sur le jeu de test, simulez une campagne de rétention : les clients dont `v2` donne un score d'au moins 0,30 sont retenus (donc étiquetés « n'a pas résilié ») avec une probabilité de 75 %, **sauf** un groupe témoin de 10 % tiré au hasard qui ne reçoit pas la campagne. Comparez l'AUC de `v2` mesurée (a) sur les étiquettes d'origine (sans campagne), (b) sur les étiquettes de tous les clients après la campagne, (c) sur le seul groupe témoin. Quelle mesure est la moins biaisée, et pourquoi ?

### Exercice 4.12 ⭐⭐⭐ — Écrire une politique de ré-entraînement (section 4.7)

Proposez une règle de ré-entraînement fondée sur la performance mesurée (AUC perdue par rapport à la semaine 1) et appliquez-la aux deux scénarios du livre (dérive des variables, dérive du concept) : en quelle semaine se déclenche-t-elle ? Complétez par les quatre éléments qu'une politique **écrite** doit contenir.

## Corrigés

### Corrigé 4.1

(a) **Les graines** : sans graine fixée, l'aléa de la forêt (échantillons bootstrap, variables tirées) change à chaque entraînement. (b) **Les versions** des bibliothèques : une mise à jour a changé un calcul (algorithme d'optimisation, valeur par défaut) sans que le code bouge. (c) **L'empreinte des données** : sans hash enregistré avec le modèle, on ne peut pas dire quelle version du fichier l'a produit.

### Corrigé 4.2

```python
Xs = Xte.assign(satisfaction_moy=Xte["satisfaction_moy"] * 20)
lignes = []
for nom, m in (("v1 (logistique)", v1), ("v2 (boosting)", v2)):
    p0, p1 = m.predict_proba(Xte)[:, 1], m.predict_proba(Xs)[:, 1]
    lignes.append((nom, roc_auc_score(yte, p0), roc_auc_score(yte, p1), p0.mean(), p1.mean()))
print(pd.DataFrame(lignes, columns=["modèle", "AUC correct", "AUC avec ×20", "proba moyenne correcte", "proba moyenne avec ×20"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
         modèle  AUC correct  AUC avec ×20  proba moyenne correcte  proba moyenne avec ×20
v1 (logistique)        0.867         0.699                   0.131                   0.013
  v2 (boosting)        0.893         0.858                   0.119                   0.097
```


La régression logistique est **linéaire** dans la variable mise à l'échelle : une satisfaction multipliée par 20 devient une valeur standardisée de l'ordre de 20 fois plus grande, qui **extrapole** linéairement et écrase le reste du modèle (AUC 0,699 au lieu de 0,867, probabilité moyenne de 1,3 %). Les arbres du boosting, eux, **saturent** : toute valeur au-dessus du maximum vu à l'entraînement tombe dans la dernière coupure, la prédiction cesse de changer (AUC 0,858 au lieu de 0,893). Un modèle à arbres est donc plus **robuste** à ce type d'erreur, mais pas immunisé : il traite désormais tous les clients comme parfaitement satisfaits.

### Corrigé 4.3

```python
import onnx, onnxruntime as ort
from onnx import helper, TensorProto, numpy_helper
Z = v1.named_steps["pre"].transform(Xte); Z = Z.toarray() if hasattr(Z, "toarray") else Z
clf = v1.named_steps["clf"]; W, b = clf.coef_.T.astype(np.float32), clf.intercept_.astype(np.float32)
graphe = helper.make_graph([helper.make_node("Gemm", ["Z", "W", "b"], ["lin"]), helper.make_node("Sigmoid", ["lin"], ["p"])], "resiliation",
                           [helper.make_tensor_value_info("Z", TensorProto.FLOAT, [None, W.shape[0]])],
                           [helper.make_tensor_value_info("p", TensorProto.FLOAT, [None, 1])],
                           [numpy_helper.from_array(W, "W"), numpy_helper.from_array(b, "b")])
modele_onnx = helper.make_model(graphe, opset_imports=[helper.make_opsetid("", 13)]); modele_onnx.ir_version = 8
onnx.checker.check_model(modele_onnx)
session = ort.InferenceSession(modele_onnx.SerializeToString(), providers=["CPUExecutionProvider"])
p_onnx = session.run(None, {"Z": Z.astype(np.float32)})[0][:, 0]
ecart = float(np.abs(p_onnx - v1.predict_proba(Xte)[:, 1]).max())
brut = Xte[d["num"]].fillna(0).to_numpy(np.float32)                                      # numériques bruts, sans imputation ni échelle
brut = np.column_stack([brut, np.zeros((len(brut), Z.shape[1] - brut.shape[1]), np.float32)])
p_brut = session.run(None, {"Z": brut})[0][:, 0]
print("écart maximal avec predict_proba :", f"{ecart:.1e}", "| AUC du graphe sur entrées brutes :", round(roc_auc_score(yte, p_brut), 3))
```
<!--sortie-->
```text
écart maximal avec predict_proba : 1.9e-07 | AUC du graphe sur entrées brutes : 0.713
```


Sur les variables **préparées**, le graphe rend les mêmes probabilités que scikit-learn à 1.9e-07 près (simple précision). Sur les variables **non préparées**, la sortie n'a plus de sens (AUC 0,713, probabilité moyenne 47,9 %) : le graphe ne contient que la partie linéaire, **la préparation fait partie du modèle** et doit être exportée ou refaite à l'identique en service (4.1).

### Corrigé 4.4

```python
L = 300 * 0.080
pods = math.ceil(1.25 * L / 5)
budget = (1 - 0.999) * 30 * 24 * 60
p_trois = 0.95 ** 3
print(f"(a) requêtes simultanées L = {L:.0f} ; pods = ceil(1,25 × {L:.0f} / 5) = {pods}")
print(f"(b) budget d'erreur = {budget:.1f} minutes")
print(f"(c) probabilité que les trois appels soient sous le p95 = {p_trois:.3f}")
```
<!--sortie-->
```text
(a) requêtes simultanées L = 24 ; pods = ceil(1,25 × 24 / 5) = 6
(b) budget d'erreur = 43.2 minutes
(c) probabilité que les trois appels soient sous le p95 = 0.857
```

(a) La loi de Little donne $L=\lambda W=300\times0{,}08=24$ requêtes simultanées ; à 5 par pod avec 25 % de marge, $\lceil 1{,}25\times24/5\rceil=6$ pods. (b) $0{,}001\times30\times24\times60=43{,}2$ minutes par mois : passer de 99,5 % à 99,9 % divise le budget par cinq. (c) $0{,}95^3\approx0{,}857$ : même si chaque appel respecte son objectif 95 fois sur 100, **la page entière ne le respecte que 86 fois sur 100**. Un engagement de service doit donc être fixé sur le **parcours complet** que vit l'utilisateur, pas seulement sur chaque appel.

### Corrigé 4.5

```python
s2all = v2.predict_proba(Xpool)[:, 1]
def zs(s):
    s = s.fillna(s.median()); return ((s - s.mean()) / s.std()).to_numpy()
w_derive = np.exp(0.15 * (zs(Xpool["part_achats_promo"]) - zs(Xpool["satisfaction_moy"]))); w_derive /= w_derive.sum()

def historique(graine):
    rng = np.random.default_rng(graine)
    m = np.array([s2all[rng.choice(len(Xpool), 200, p=None if t < 60 else w_derive)].mean() for t in range(90)])
    return (m - m[:30].mean()) / m[:30].std(ddof=1)

REGLES = {"2σ": (2, 1), "2,5σ": (2.5, 1), "3σ": (3, 1), "2σ deux jours": (2, 2), "2,5σ deux jours": (2.5, 2)}
def declenche(z, seuil, consec):
    a = np.abs(z) > seuil
    return a if consec == 1 else a & np.r_[False, a[:-1]]

resultats = {r: [] for r in REGLES}
for h in range(150):
    z = historique(9000 + h)
    for r, (seuil, consec) in REGLES.items():
        a = declenche(z, seuil, consec)
        pos = np.flatnonzero(a[60:])
        resultats[r].append((a[30:60].sum(), pos[0] + 1 if len(pos) else 30))     # (fausses alertes, retard ; 30 si non détectée)
moy = pd.DataFrame({r: np.mean(v, axis=0) for r, v in resultats.items()}, index=["fausses alertes", "retard (jours)"]).T
for nom, (c_fausse, c_retard) in {"coût A (1 par fausse alerte, 3 par jour de retard)": (1, 3), "coût B (30 par fausse alerte, 3 par jour de retard)": (30, 3)}.items():
    moy[nom.split(' (')[0]] = c_fausse * moy["fausses alertes"] + c_retard * moy["retard (jours)"]
print(moy.round(1).to_string())
```
<!--sortie-->
```text
                 fausses alertes  retard (jours)  coût A  coût B
2σ                           1.7             5.9    19.4    68.9
2,5σ                         0.5            11.1    33.8    48.9
3σ                           0.2            17.7    53.4    58.6
2σ deux jours                0.1            19.9    59.8    62.3
2,5σ deux jours              0.0            26.5    79.5    79.9
```


Avec les coûts de l'énoncé (coût A), la règle qui minimise le coût moyen est « 2σ » (coût moyen 19,4). **Le résultat dépend des coûts** : si une fausse alerte coûte 30 unités (une nuit d'astreinte) au lieu de 1 (coût B), la règle optimale n'est plus la même : « 2,5σ » (coût moyen 48,9). Il n'existe pas de « bon seuil » en soi, seulement un seuil adapté au coût relatif des deux erreurs : modifiez les coûts dans le code pour le vérifier.

### Corrigé 4.6

```python
dossier = os.path.join(WORK, "ex46"); os.makedirs(os.path.join(dossier, "partitions"), exist_ok=True)
fichier_unique = os.path.join(dossier, "scores.csv")
scores_jour = pd.DataFrame({"id": range(40), "proba": v2.predict_proba(Xpool.iloc[:40])[:, 1]})

def publier_ajout(jour, df):                                                  # non idempotente : ajoute à la fin
    df.assign(jour=jour).to_csv(fichier_unique, mode="a", header=not os.path.exists(fichier_unique), index=False)

def publier_partition(jour, df):                                              # idempotente : écrase la partition du jour
    df.assign(jour=jour).to_csv(os.path.join(dossier, "partitions", f"jour={jour}.csv"), index=False)

for _ in range(2):
    publier_ajout(0, scores_jour); publier_partition(0, scores_jour)
n_ajout = len(pd.read_csv(fichier_unique))
n_part = sum(len(pd.read_csv(os.path.join(dossier, "partitions", f))) for f in os.listdir(os.path.join(dossier, "partitions")))
print("lignes après deux exécutions du jour 0 : par ajout", n_ajout, "| par partition", n_part)
```
<!--sortie-->
```text
lignes après deux exécutions du jour 0 : par ajout 80 | par partition 40
```

La version par ajout contient **80 lignes** pour 40 clients : chaque reprise duplique les données. La version par partition en contient **40**, quel que soit le nombre d'exécutions. Les trois façons d'obtenir l'idempotence (livre, 4.4) sont : écraser la sortie du jour, faire un *upsert* selon une clé, ou écrire dans un fichier temporaire puis le renommer d'un coup.

### Corrigé 4.7

```python
copie = os.path.join(WORK, "clients_modifie.csv")
tab = pd.read_csv("donnees/clients_ml.csv"); tab.loc[:4, "age"] += 1; tab.to_csv(copie, index=False)
h0, h1 = hash_fichier("donnees/clients_ml.csv", 16), hash_fichier(copie, 16)
d1 = donnees(copie); v1b = modele_v1(d1)
p0 = v1.predict_proba(Xte)[:, 1]
p1 = v1b.predict_proba(d1["Xte"])[:, 1]
print("hash original :", h0, "| hash modifié :", h1)
print("écart d'AUC de test :", round(roc_auc_score(yte, p0) - roc_auc_score(d1["yte"], p1), 5), "| écart maximal de probabilité :", round(float(np.abs(p0 - p1).max()), 5))
```
<!--sortie-->
```text
hash original : fa48edff3715fdc7 | hash modifié : 041b3c3d9ffbd37a
écart d'AUC de test : -4e-05 | écart maximal de probabilité : 0.00642
```

Les deux hash n'ont **rien en commun**, alors que l'AUC de test et les probabilités sont quasiment identiques : la comparaison des performances ne permet **pas** de savoir quelle version des données a servi, tandis que le hash le dit sans ambiguïté. C'est pour cela que l'on enregistre le hash des données avec chaque modèle (4.5) : la traçabilité est une propriété d'**identité**, pas de performance.

### Corrigé 4.8

```python
api8 = TestClient(creer_app(chemin_v2, COLONNES, version="2.0.0"))
clients10 = [ligne_json(Xte.iloc[i]) for i in range(10)]
cas = {"(a) liste vide": [], "(b) un client": clients10[:1],
       "(c) quatrième invalide": [{**c, "age": 17} if i == 3 else c for i, c in enumerate(clients10)],
       "(d) champ inconnu": [{**clients10[0], "champ_inconnu": 1}]}
for nom, corps in cas.items():
    r = api8.post("/predict_batch", json=corps)
    detail = r.json().get("detail")
    print(f"{nom:24s}→ {r.status_code}", "| loc :", detail[0]["loc"] if detail else "", "|", len(r.json().get("probabilites", [])), "probabilités")
```
<!--sortie-->
```text
(a) liste vide          → 200 | loc :  | 0 probabilités
(b) un client           → 200 | loc :  | 1 probabilités
(c) quatrième invalide  → 422 | loc : ['body', 3, 'age'] | 0 probabilités
(d) champ inconnu       → 200 | loc :  | 1 probabilités
```

Attendus : (a) 200 avec une liste vide (un lot vide est légitime) ; (b) 200 avec une probabilité ; (c) **422**, et le chemin d'erreur `['body', 3, 'age']` désigne l'élément de **position 3** (le quatrième) : le message dit exactement où est la faute ; (d) 200, car pydantic **ignore** par défaut les champs supplémentaires. Ce dernier comportement est un choix de contrat : si l'on préfère un refus, il faut le demander explicitement (`extra="forbid"`). Un cas limite non testé (ici, la liste vide) est souvent celui qui fait tomber le service en production.

### Corrigé 4.9

```python
class LimiteurFenetre:
    def __init__(self, max_appels=3, fenetre=60):
        self.max, self.fenetre, self.etat = max_appels, fenetre, {}

    def autoriser(self, cle, maintenant):
        debut, n = self.etat.get(cle, (maintenant, 0))
        if maintenant - debut >= self.fenetre:                              # nouvelle fenêtre
            debut, n = maintenant, 0
        if n >= self.max:
            self.etat[cle] = (debut, n); return False
        self.etat[cle] = (debut, n + 1); return True

lim = LimiteurFenetre()
suite = [lim.autoriser("k", t) for t in (0, 10, 20, 30, 59)] + [lim.autoriser("k", t) for t in (61, 62)]
print(suite)
assert suite == [True, True, True, False, False, True, True]
```
<!--sortie-->
```text
[True, True, True, False, False, True, True]
```

Trois appels passent, le quatrième et le cinquième (dans la même fenêtre de 60 s) sont refusés (le code HTTP serait 429), puis les appels repassent dès la fenêtre suivante. Cette version a un défaut connu : une rafale à cheval sur deux fenêtres peut faire passer **deux fois** le quota en peu de temps. La **fenêtre glissante** ou le **seau à jetons** corrigent cela, au prix d'un peu plus d'état à conserver.

### Corrigé 4.10

```python
p = np.array([0.4, 0.3, 0.2, 0.1]); q = np.array([0.25, 0.25, 0.25, 0.25])
termes = (q - p) * np.log(q / p)
kl_qp, kl_pq = (q * np.log(q / p)).sum(), (p * np.log(p / q)).sum()
print("contributions :", termes.round(4), "| PSI =", round(termes.sum(), 4))
print("KL(q||p) + KL(p||q) =", round(kl_qp + kl_pq, 4), "| intervalle le plus contributif :", int(termes.argmax()) + 1)
assert abs(kl_qp + kl_pq - termes.sum()) < 1e-12
```
<!--sortie-->
```text
contributions : [0.0705 0.0091 0.0112 0.1374] | PSI = 0.2282
KL(q||p) + KL(p||q) = 0.2282 | intervalle le plus contributif : 4
```

Les contributions sont toutes positives (les deux facteurs $(q_i-p_i)$ et $\ln(q_i/p_i)$ ont le même signe), le PSI est leur somme, et il coïncide avec $\mathrm{KL}(q\|p)+\mathrm{KL}(p\|q)$. L'intervalle 4 contribue le plus : sa part passe de 10 % à 25 %, soit un rapport de 2,5, et le logarithme du rapport est grand même si l'écart absolu (15 points) est le même que pour l'intervalle 1 (qui passe de 40 % à 25 %).

### Corrigé 4.11

```python
rng = np.random.default_rng(11)
s = v2.predict_proba(Xte)[:, 1]
signale = s >= 0.30
temoin = rng.random(len(yte)) < 0.10
retenu = signale & ~temoin & (rng.random(len(yte)) < 0.75)
y_apres = yte.copy(); y_apres[retenu] = 0
auc_origine = roc_auc_score(yte, s); auc_tous = roc_auc_score(y_apres, s); auc_temoin = roc_auc_score(y_apres[temoin], s[temoin])
print(pd.Series({"(a) étiquettes d'origine (sans campagne)": auc_origine, "(b) tous, après campagne": auc_tous, "(c) groupe témoin seul": auc_temoin}).round(3).to_string())
```
<!--sortie-->
```text
(a) étiquettes d'origine (sans campagne)    0.893
(b) tous, après campagne                    0.797
(c) groupe témoin seul                      0.853
```


La mesure (b) tombe à 0,797 alors que le modèle n'a pas changé : la campagne a **modifié les étiquettes** des clients que le modèle signale, et ces « succès » de la rétention sont comptés comme des erreurs du modèle. La mesure (c), faite sur le seul groupe témoin (240 clients qui n'ont pas reçu la campagne), retrouve une valeur proche de (a) (0,853 contre 0,893), au bruit d'échantillonnage près (le groupe ne compte que 240 clients, donc une trentaine de résiliations, et l'AUC y est peu précise) : c'est la **seule** qui estime la performance du modèle comme prédicteur du risque en l'absence d'intervention. D'où la règle : réserver un petit groupe témoin aléatoire (4.7), dont les étiquettes servent à la mesure et au ré-entraînement.

### Corrigé 4.12

```python
lignes = []
for scenario in ("covariable", "concept"):
    aucs = []
    for k in range(1, 5):
        Xw, yw = semaine(d, v2, k, scenario)
        aucs.append(roc_auc_score(yw, v2.predict_proba(Xw)[:, 1]))
    declenchees = [k + 1 for k, a in enumerate(aucs) if a < aucs[0] - 0.05]
    lignes.append((scenario, [round(a, 3) for a in aucs], declenchees[0] if declenchees else "jamais"))
print(pd.DataFrame(lignes, columns=["scénario", "AUC par semaine", "1re semaine de déclenchement"]).to_string(index=False))
```
<!--sortie-->
```text
  scénario              AUC par semaine 1re semaine de déclenchement
covariable [0.876, 0.859, 0.869, 0.857]                       jamais
   concept [0.876, 0.847, 0.808, 0.776]                            3
```


La règle « ré-entraîner dès que l'AUC mesurée a perdu plus de 0,05 par rapport à la semaine 1 » ne se déclenche **jamais** pour la dérive des variables (le modèle reste bon : inutile de payer un ré-entraînement) et se déclenche à la semaine 3 pour la dérive du concept. Attention : cette semaine est celle où **les étiquettes sont arrivées** ; dans la réalité, avec un délai de 90 jours, la décision n'est prise que bien après le début de la dérive, d'où l'intérêt de compléter par des alertes sur les entrées et le score. Une politique **écrite** doit contenir au moins : (1) **les déclencheurs** et leurs seuils (performance, PSI sur variables importantes) ; (2) **le diagnostic préalable** (bug en amont ou changement réel ?) et qui le fait ; (3) **les données** utilisées (fenêtre récente, groupe témoin pour éviter la boucle de rétroaction) ; (4) **les portes** que le nouveau modèle doit franchir (porte de qualité, déploiement progressif, retour arrière), et qui décide.
