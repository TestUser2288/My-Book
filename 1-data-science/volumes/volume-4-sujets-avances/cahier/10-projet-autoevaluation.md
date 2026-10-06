# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume IV. Il contient **le projet du volume** : prendre le modèle de résiliation du volume III et en faire un **système** (un pipeline reproductible et testé, un suivi d'expériences, un service qui valide ses entrées, une supervision qui détecte la dérive), puis l'**auto-évaluation**. Aucune notion nouvelle : chaque étape renvoie à la section du livre qui l'explique. Tout s'exécute **hors ligne**, dans des dossiers temporaires.

## Projet du volume

### P.1 Le cahier des charges

La gérante a obtenu, au volume III, un modèle qui prédit les clients qui ne commanderont plus dans les 90 jours. Elle veut maintenant que l'équipe relation client reçoive **chaque matin** ces scores. Elle pose cinq exigences :

1. **Reproductible** : on doit pouvoir réentraîner le modèle et retrouver les mêmes résultats.
2. **Versionné et traçable** : à tout moment, savoir quel modèle sert, entraîné avec quelles données et quels réglages.
3. **Servi par une API** qui **refuse** les données invalides au lieu de produire un score absurde.
4. **Supervisé** : être prévenue si les clients d'aujourd'hui ne ressemblent plus à ceux de l'entraînement.
5. **Remplaçable sans risque** : un nouveau modèle ne doit passer en service que s'il est meilleur, et on doit pouvoir revenir en arrière.

La méthode suit huit étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Structurer | Où vivent le code, la configuration, les graines ? | 4.1 |
| P.3 Pipeline testé | Les données sont-elles saines ? Le modèle est-il reproductible ? | 4.1 |
| P.4 Suivre | Quel modèle, quels réglages, quelles métriques ? | 4.5 |
| P.5 Servir | Comment exposer le modèle sans accepter n'importe quoi ? | 4.2, 4.6 |
| P.6 Journaliser et superviser | Les clients changent-ils ? | 4.3, 4.7 |
| P.7 Décider du réentraînement | La dérive abîme-t-elle les performances ? | 4.7, 4.3 |
| P.8 Automatiser | Comment rejouer tout cela sans intervention ? | 4.4, 4.6 |
| P.9 Rapporter | Peut-on mettre en production ? | 4.1 à 4.3 |

> 📦 **Les données.** On reprend le fichier `donnees/clients_ml.csv` du volume III (12 000 clients, cible `churn_90j`), **simulé**. Rappel important : la colonne `commandes_apres_cible` est la **fuite d'information** du volume III (elle décrit l'avenir) et `segment_vrai` est une vérité cachée : ni l'une ni l'autre ne doit entrer dans le modèle. Une partie du travail de cette étude consiste à **empêcher mécaniquement** qu'elles y entrent.

### P.2 Étape 1 : structurer et configurer

On commence par séparer ce qui **change** (la configuration) de ce qui **ne change pas** (le code). Tout le reste du projet lit cette configuration.

```python
import json, os, tempfile, warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ESPACE = tempfile.mkdtemp(prefix="projet_mlops_")          # tout ce que le projet écrit vit ici, puis disparaît

CONFIG = {
    "graine": 7,
    "colonnes_exclues": ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"],
    "cible": "churn_90j",
    "part_test": 0.25,
    "seuil_alerte_psi": 0.2,
    "seuil_decision": 0.20,
}
donnees = pd.read_csv("donnees/clients_ml.csv")
print(donnees.shape, "| taux de résiliation :", round(donnees[CONFIG["cible"]].mean(), 3))
```
<!--sortie-->
```text
(12000, 24) | taux de résiliation : 0.14
```

### P.3 Étape 2 : un pipeline testé

**Vérifier les données avant de modéliser** (livre, section 4.1). Ces vérifications sont des fonctions : elles s'exécutent à chaque entraînement et **arrêtent** le pipeline si quelque chose cloche.

```python
def verifier_donnees(df, cfg):
    problemes = []
    if df["id_client"].duplicated().any():
        problemes.append("identifiants clients en double")
    if not df[cfg["cible"]].isin([0, 1]).all():
        problemes.append("cible non binaire")
    if not df["age"].between(15, 100).all():
        problemes.append("âge hors de [15, 100]")
    if (df["recence_jours"] < 0).any() or (df["montant_12m"] < 0).any():
        problemes.append("valeurs négatives impossibles")
    entrees = [c for c in df.columns if c not in cfg["colonnes_exclues"]]
    interdites = {"commandes_apres_cible", "segment_vrai"} & set(entrees)
    if interdites:
        problemes.append(f"colonnes interdites parmi les entrées : {sorted(interdites)}")
    return problemes, entrees

problemes, ENTREES = verifier_donnees(donnees, CONFIG)
print("problèmes détectés :", problemes or "aucun", "|", len(ENTREES), "variables d'entrée")
```
<!--sortie-->
```text
problèmes détectés : aucun | 19 variables d'entrée
```

On vérifie aussi que **le garde-fou fonctionne** : un test qui ne détecte jamais rien ne prouve rien (livre, section 4.1).

```python
fautif = donnees.copy()
fautif.loc[0, "age"] = 250
tricheur = donnees.assign(commandes_apres_cible=donnees["commandes_apres_cible"])
cfg_laxiste = {**CONFIG, "colonnes_exclues": ["id_client", "churn_90j", "depense_6m"]}      # on « oublie » d'exclure les deux colonnes
print("âge impossible       :", verifier_donnees(fautif, CONFIG)[0])
print("fuite non exclue     :", verifier_donnees(tricheur, cfg_laxiste)[0])
```
<!--sortie-->
```text
âge impossible       : ['âge hors de [15, 100]']
fuite non exclue     : ["colonnes interdites parmi les entrées : ['commandes_apres_cible', 'segment_vrai']"]
```

Le **pipeline de modèle** applique toutes les transformations **dans** la validation croisée et dans le service (livre, volume III, section 4.1) : imputation avec indicateurs d'absence, encodage des modalités, puis un boosting.

```python
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import roc_auc_score, average_precision_score

X, y = donnees[ENTREES], donnees[CONFIG["cible"]]
CATEGORIELLES = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
NUMERIQUES = [c for c in ENTREES if c not in CATEGORIELLES]

def fabriquer_pipeline(modele):
    prep = ColumnTransformer([
        ("num", SimpleImputer(strategy="median", add_indicator=True), NUMERIQUES),
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=20), CATEGORIELLES)])
    return Pipeline([("prep", prep), ("modele", modele)])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=CONFIG["part_test"], random_state=CONFIG["graine"], stratify=y)
pipe = fabriquer_pipeline(HistGradientBoostingClassifier(random_state=CONFIG["graine"])).fit(X_tr, y_tr)
p_te = pipe.predict_proba(X_te)[:, 1]
print(f"AUC test = {roc_auc_score(y_te, p_te):.4f} | précision moyenne = {average_precision_score(y_te, p_te):.4f}")
```
<!--sortie-->
```text
AUC test = 0.8800 | précision moyenne = 0.6105
```

Deux **tests de modèle** complètent la vérification des données : le pipeline doit être **déterministe** (même graine, mêmes scores) et ne doit pas régresser sous un score plancher.

```python
pipe2 = fabriquer_pipeline(HistGradientBoostingClassifier(random_state=CONFIG["graine"])).fit(X_tr, y_tr)
tests = {
    "déterminisme (même graine, mêmes scores)": bool(np.allclose(pipe2.predict_proba(X_te)[:, 1], p_te)),
    "AUC au-dessus du plancher de 0,85": roc_auc_score(y_te, p_te) > 0.85,
    "scores dans [0, 1]": bool(((p_te >= 0) & (p_te <= 1)).all()),
    "tolère une valeur manquante": bool(np.isfinite(pipe.predict_proba(X_te.head(1).assign(satisfaction_moy=np.nan))[:, 1]).all()),
}
for nom, ok in tests.items():
    print("OK " if ok else "ÉCHEC", nom)
assert all(tests.values())
```
<!--sortie-->
```text
OK  déterminisme (même graine, mêmes scores)
OK  AUC au-dessus du plancher de 0,85
OK  scores dans [0, 1]
OK  tolère une valeur manquante
```

### P.4 Étape 3 : suivre les expériences

On ne retient pas un modèle « parce que le notebook l'a dit » : on compare des candidats et on **consigne** ce qu'on a fait (livre, section 4.5). **MLflow** enregistre les paramètres, les métriques et le modèle ; ici avec une base SQLite temporaire.

```python
import logging, mlflow, mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LogisticRegression

logging.getLogger("mlflow").setLevel(logging.ERROR)
mlflow.set_tracking_uri(f"sqlite:///{ESPACE}/mlflow.db")
mlflow.set_experiment("resiliation")

candidats = {
    "logistique": fabriquer_pipeline(LogisticRegression(max_iter=2000)),
    "boosting": fabriquer_pipeline(HistGradientBoostingClassifier(random_state=CONFIG["graine"])),
}
for nom, modele in candidats.items():
    with mlflow.start_run(run_name=nom):
        modele.fit(X_tr, y_tr)
        p = modele.predict_proba(X_te)[:, 1]
        mlflow.log_param("famille", nom)
        mlflow.log_param("graine", CONFIG["graine"])
        mlflow.log_metric("auc_test", roc_auc_score(y_te, p))
        mlflow.log_metric("precision_moyenne_test", average_precision_score(y_te, p))
        mlflow.sklearn.log_model(modele, name="modele", serialization_format="cloudpickle")
runs = mlflow.search_runs(experiment_names=["resiliation"], order_by=["metrics.auc_test DESC"])
print(runs[["tags.mlflow.runName", "params.famille", "metrics.auc_test", "metrics.precision_moyenne_test"]].round(4).to_string(index=False))
```
<!--sortie-->
```text
tags.mlflow.runName params.famille  metrics.auc_test  metrics.precision_moyenne_test
           boosting       boosting            0.8800                          0.6105
         logistique     logistique            0.8527                          0.5519
```

> ⚠️ **Sérialiser n'est pas anodin.** Le format `cloudpickle` choisi ici enregistre l'objet Python tel quel ; **charger un fichier de ce type exécute du code** qu'il contient. On ne charge donc **que des modèles produits par soi-même** ou par une source de confiance. MLflow propose par défaut un format plus sûr (`skops`), qui refuse ici le modèle parce qu'il contient un type qu'il ne connaît pas : ce refus est le comportement voulu d'un outil prudent, et la raison pour laquelle nous précisons le format (livre, section 4.2).

On **enregistre le meilleur** dans le registre de modèles sous un alias « production ». Le service ira chercher le modèle par cet alias : changer de modèle, c'est déplacer l'alias, et revenir en arrière aussi.

```python
client = MlflowClient()
meilleur = runs.iloc[0]["run_id"]
version = mlflow.register_model(f"runs:/{meilleur}/modele", "modele_resiliation")
client.set_registered_model_alias("modele_resiliation", "production", version.version)
mv = client.get_model_version_by_alias("modele_resiliation", "production")
print("version en production :", mv.version, "| issue du run « boosting » :", mv.run_id == meilleur)
```
<!--sortie-->
```text
version en production : 1 | issue du run « boosting » : True
```

### P.5 Étape 4 : servir par une API qui valide ses entrées

Le service (livre, sections 4.2 et 4.6) charge le modèle **par alias**, définit un **schéma** d'entrée (types, bornes) et renvoie, avec le score, la **version du modèle**. Une entrée invalide est refusée avec une erreur 422 : c'est la validation qui protège la gérante d'un score absurde.

```python
from typing import Literal, Optional
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

class Client(BaseModel):
    age: int = Field(ge=15, le=100)
    ville: str
    canal_acquisition: Literal["Boutique", "Site", "Réseaux"]
    appareil: Optional[Literal["mobile", "ordinateur", "tablette"]] = None
    anciennete_mois: int = Field(ge=0)
    nb_commandes_12m: int = Field(ge=0)
    panier_moyen: Optional[float] = Field(default=None, ge=0)
    montant_12m: float = Field(ge=0)
    recence_jours: int = Field(ge=0, le=365)
    nb_retours_12m: int = Field(ge=0)
    satisfaction_moy: Optional[float] = Field(default=None, ge=1, le=5)
    nb_tickets_support_12m: int = Field(ge=0)
    programme_fidelite: Literal[0, 1]
    nb_promos_recues_12m: int = Field(ge=0)
    part_achats_promo: float = Field(ge=0, le=1)
    taux_ouverture_email: float = Field(ge=0, le=1)
    delai_livraison_moy: Optional[float] = Field(default=None, ge=0)
    categorie_preferee: Literal["A", "B", "C", "D"]
    revenu_zone: float

modele_prod = mlflow.sklearn.load_model("models:/modele_resiliation@production")
app = FastAPI(title="Score de résiliation")

@app.get("/health")
def sante():
    return {"statut": "ok", "version_modele": int(mv.version)}

@app.post("/predict")
def predire(c: Client):
    ligne = pd.DataFrame([c.model_dump()])[ENTREES]
    return {"score": round(float(modele_prod.predict_proba(ligne)[0, 1]), 6), "version_modele": int(mv.version)}

api = TestClient(app)
print(api.get("/health").json())
```
<!--sortie-->
```text
{'statut': 'ok', 'version_modele': 1}
```

On **teste le contrat** de l'API : un client valide, un client invalide, une valeur facultative absente, et surtout la **parité** avec le calcul hors ligne (le service ne doit pas calculer autre chose que le notebook).

```python
exemple = X_te.iloc[0].to_dict()
exemple = {k: (None if isinstance(v, float) and np.isnan(v) else (v.item() if hasattr(v, "item") else v)) for k, v in exemple.items()}
rep = api.post("/predict", json=exemple)
print("client valide      :", rep.status_code, rep.json())
print("parité hors ligne  :", abs(rep.json()["score"] - float(pipe.predict_proba(X_te.iloc[[0]])[0, 1])) < 1e-4)

invalide = {**exemple, "age": 250, "canal_acquisition": "Autre"}
r = api.post("/predict", json=invalide)
print("client invalide    :", r.status_code, "| champs refusés :", sorted(e["loc"][-1] for e in r.json()["detail"]))

sans_satisfaction = {**exemple, "satisfaction_moy": None}
print("valeur absente     :", api.post("/predict", json=sans_satisfaction).status_code)
```
<!--sortie-->
```text
client valide      : 200 {'score': 0.017973, 'version_modele': 1}
parité hors ligne  : True
client invalide    : 422 | champs refusés : ['age', 'canal_acquisition']
valeur absente     : 200
```

### P.6 Étape 5 : journaliser et superviser

Un modèle en production se **regarde** : on journalise chaque prédiction, puis on compare ce que le modèle voit aujourd'hui à ce qu'il a vu à l'entraînement (livre, sections 4.3 et 4.7). Simulons **huit semaines** d'exploitation. Les clients de chaque semaine sont tirés dans le jeu de test ; à partir de la semaine 5, une **campagne de promotions** change la clientèle : on sur-échantillonne les clients très sensibles aux promotions et peu satisfaits (c'est une **dérive de covariables** : les clients changent, pas la règle qui relie leurs caractéristiques à la résiliation).

```python
rng = np.random.default_rng(CONFIG["graine"])
base = X_te.copy()
base["vrai"] = y_te.to_numpy()

def semaine(i, n=500):
    poids = np.ones(len(base))
    if i >= 5:                                             # campagne de promotions à partir de la semaine 5
        intensite = 1 + 2.5 * (i - 4) / 4
        poids = np.exp(intensite * (2.0 * (base["part_achats_promo"].to_numpy() - 0.3) - 0.6 * (np.nan_to_num(base["satisfaction_moy"].to_numpy(), nan=3.5) - 3.5)))
    idx = rng.choice(len(base), n, replace=False if i < 5 else True, p=poids / poids.sum())
    return base.iloc[idx].copy().assign(semaine=i)

journal = pd.concat([semaine(i) for i in range(1, 9)], ignore_index=True)
journal["score"] = pipe.predict_proba(journal[ENTREES])[:, 1]
print(journal.groupby("semaine")[["part_achats_promo", "score"]].mean().round(3).T.to_string())
```
<!--sortie-->
```text
semaine                1      2      3      4      5      6      7      8
part_achats_promo  0.274  0.289  0.300  0.274  0.572  0.684  0.748  0.799
score              0.127  0.130  0.134  0.132  0.188  0.233  0.249  0.311
```

Pour **mesurer** la dérive d'une variable, on utilise l'**indice de stabilité de population** (PSI), écrit à la main : on découpe la variable en classes d'après l'**entraînement**, puis on compare les proportions observées aujourd'hui à celles d'hier.

$$\text{PSI}=\sum_{k}(a_k-e_k)\ln\frac{a_k}{e_k}$$

où $e_k$ est la part attendue (entraînement) dans la classe $k$ et $a_k$ la part actuelle. Règle usuelle : moins de 0,1 stable, de 0,1 à 0,25 à surveiller, plus de 0,25 dérive marquée.

```python
def psi(attendu, actuel, classes=10):
    attendu, actuel = np.asarray(attendu, float), np.asarray(actuel, float)
    bornes = np.unique(np.quantile(attendu[~np.isnan(attendu)], np.linspace(0, 1, classes + 1)))
    bornes[0], bornes[-1] = -np.inf, np.inf
    e = np.histogram(attendu[~np.isnan(attendu)], bornes)[0] / np.sum(~np.isnan(attendu))
    a = np.histogram(actuel[~np.isnan(actuel)], bornes)[0] / np.sum(~np.isnan(actuel))
    e, a = np.clip(e, 1e-4, None), np.clip(a, 1e-4, None)
    return float(np.sum((a - e) * np.log(a / e)))

surveillees = ["part_achats_promo", "satisfaction_moy", "recence_jours", "nb_commandes_12m", "age", "montant_12m"]
table = pd.DataFrame({f"s{i}": {v: psi(X_tr[v], journal.loc[journal.semaine == i, v]) for v in surveillees} for i in range(1, 9)})
scores_tr = pipe.predict_proba(X_tr)[:, 1]
table.loc["score du modèle"] = [psi(scores_tr, journal.loc[journal.semaine == i, "score"]) for i in range(1, 9)]
print(table.round(3).to_string())
```
<!--sortie-->
```text
                      s1     s2     s3     s4     s5     s6     s7     s8
part_achats_promo  0.017  0.031  0.026  0.009  0.963  1.864  2.812  4.083
satisfaction_moy   0.011  0.009  0.020  0.009  0.539  1.191  1.724  3.016
recence_jours      0.014  0.007  0.003  0.022  0.064  0.118  0.201  0.462
nb_commandes_12m   0.010  0.011  0.008  0.013  0.091  0.077  0.146  0.229
age                0.025  0.021  0.025  0.009  0.169  0.449  0.515  0.992
montant_12m        0.013  0.031  0.020  0.030  0.170  0.296  0.421  0.601
score du modèle    0.009  0.026  0.030  0.048  0.229  0.357  0.604  0.910
```

Une **règle d'alerte** transforme ces nombres en action : ici, alerte si le PSI d'au moins **deux** variables, ou celui du **score**, dépasse le seuil de la configuration.

```python
def alerte(colonne, seuil=CONFIG["seuil_alerte_psi"]):
    v = table.drop(index="score du modèle")[colonne]
    return bool((v > seuil).sum() >= 2 or table.loc["score du modèle", colonne] > seuil)

etat = pd.DataFrame({"semaine": range(1, 9), "alerte": [alerte(f"s{i}") for i in range(1, 9)]})
print(etat.T.to_string(header=False))
print("première alerte à la semaine :", int(etat.loc[etat["alerte"], "semaine"].min()) if etat["alerte"].any() else "aucune")
```
<!--sortie-->
```text
semaine      1      2      3      4     5     6     7     8
alerte   False  False  False  False  True  True  True  True
première alerte à la semaine : 5
```

### P.7 Étape 6 : la dérive abîme-t-elle les performances ?

Une alerte de dérive n'est **pas** une alerte de performance (livre, section 4.7). Les étiquettes (a-t-il résilié ?) n'arrivent qu'**au bout de 90 jours** : pendant ce temps, on est aveugle. Une fois les étiquettes connues, on peut mesurer.

```python
perf = journal.groupby("semaine").apply(lambda g: pd.Series({"AUC": roc_auc_score(g["vrai"], g["score"]), "taux de résiliation": g["vrai"].mean(), "score moyen": g["score"].mean()}))
print(perf.round(3).T.to_string())
```
<!--sortie-->
```text
semaine                  1      2      3      4      5      6      7      8
AUC                  0.875  0.908  0.863  0.853  0.779  0.811  0.830  0.823
taux de résiliation  0.138  0.140  0.158  0.154  0.212  0.274  0.254  0.304
score moyen          0.127  0.130  0.134  0.132  0.188  0.233  0.249  0.311
```

Dans notre simulation, la dérive est une **dérive de covariables** pure : les clients changent, mais la relation entre leurs caractéristiques et la résiliation reste la même. Deux constats, tous deux instructifs :

- **L'AUC baisse** (environ 0,875 en moyenne sur les semaines 1 à 4, environ 0,81 sur les semaines 5 à 8) **alors que la règle n'a pas changé**. La clientèle devenue plus homogène (beaucoup de clients sensibles aux promotions) est simplement **plus difficile à classer** : l'AUC dépend de la population sur laquelle on la mesure, et ne se compare pas d'une population à l'autre.
- **La calibration tient** : le taux de résiliation observé suit le score moyen (par exemple 0,304 observé pour 0,311 prédit en semaine 8). Le modèle ne se « trompe » pas de niveau ; il y a seulement plus de clients à risque.

Une baisse d'AUC n'est donc **pas** à elle seule la preuve que le modèle est cassé. Voyons maintenant la situation où **la règle elle-même change** (dérive conceptuelle) : à partir de la semaine 5, les clients sensibles aux promotions résilient **plus que ne le prévoit le modèle** (simulation : leur probabilité réelle de résiliation est multipliée par deux).

```python
rng2 = np.random.default_rng(11)
j2 = journal.copy()
sensibles = (j2["part_achats_promo"] > 0.5) & (j2["programme_fidelite"] == 0)
doubler = (j2["semaine"] >= 5) & sensibles
p_vraie = np.clip(j2["score"].to_numpy() * np.where(doubler, 2.0, 1.0), 0, 0.98)
j2["vrai_concept"] = np.where(j2["semaine"] >= 5, rng2.binomial(1, p_vraie), j2["vrai"])
perf2 = j2.groupby("semaine").apply(lambda g: pd.Series({"AUC": roc_auc_score(g["vrai_concept"], g["score"]), "écart (observé - prédit)": g["vrai_concept"].mean() - g["score"].mean()}))
print(perf2.round(3).T.to_string())
```
<!--sortie-->
```text
semaine                       1      2      3      4      5      6      7      8
AUC                       0.875  0.908  0.863  0.853  0.917  0.932  0.934  0.952
écart (observé - prédit)  0.011  0.010  0.024  0.022  0.098  0.129  0.123  0.127
```

Dans ce scénario, l'AUC **ne signale rien** : elle monte même (de 0,85-0,91 en semaines 1 à 4 à 0,92-0,95 ensuite), parce que le sous-groupe concerné devient plus facile à repérer. Seul l'**écart entre le taux observé et le score moyen** (le défaut de calibration, volume III, section 5.2) révèle le problème : il passe d'environ 0,01-0,02 à environ 0,10-0,13. D'où la règle pratique : surveiller **à la fois** la dérive des entrées (immédiate, sans étiquettes) et la **calibration** dès que les étiquettes arrivent ; l'AUC seule peut rassurer à tort comme alarmer à tort.

**Réentraîner.** Quand la décision est prise, on réentraîne sur une **fenêtre récente**, on compare le candidat à l'ancien modèle sur des données **récentes**, et on ne promeut le candidat que s'il est meilleur (**portail de promotion**).

```python
recent = j2[j2["semaine"].between(5, 6)]
a_reentrainer = recent.drop(columns=["vrai", "score", "semaine", "vrai_concept"])
nouveau = fabriquer_pipeline(HistGradientBoostingClassifier(random_state=CONFIG["graine"], max_iter=60)).fit(pd.concat([X_tr, a_reentrainer]), pd.concat([y_tr, recent["vrai_concept"]]))
eval_ = j2[j2["semaine"].between(7, 8)]
ancien_auc = roc_auc_score(eval_["vrai_concept"], pipe.predict_proba(eval_[ENTREES])[:, 1])
nouveau_auc = roc_auc_score(eval_["vrai_concept"], nouveau.predict_proba(eval_[ENTREES])[:, 1])
print(f"semaines 7-8 : AUC de l'ancien modèle {ancien_auc:.4f} | du candidat {nouveau_auc:.4f}")
print("promotion du candidat :", "OUI" if nouveau_auc > ancien_auc + 0.005 else "NON (gain insuffisant)")
```
<!--sortie-->
```text
semaines 7-8 : AUC de l'ancien modèle 0.9439 | du candidat 0.9381
promotion du candidat : NON (gain insuffisant)
```

Le portail refuse la promotion : le candidat, entraîné sur peu de données récentes, **ne fait pas mieux** que l'ancien modèle (son AUC est même un peu plus basse). Mais le vrai problème de ce scénario est un **défaut de calibration**, et il existe un remède bien moins coûteux que le réentraînement : **recalibrer** les scores de l'ancien modèle sur les données récentes (méthode de Platt, volume III, section 5.2).

```python
from sklearn.linear_model import LogisticRegression as LR

def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p)).reshape(-1, 1)

platt = LR(C=1e6).fit(logit(recent["score"].to_numpy()), recent["vrai_concept"])
s78 = eval_["score"].to_numpy()
recal = platt.predict_proba(logit(s78))[:, 1]
print(f"semaines 7-8 : taux observé {eval_['vrai_concept'].mean():.3f} | score moyen avant {s78.mean():.3f} | après recalibrage {recal.mean():.3f}")
print(f"AUC avant {roc_auc_score(eval_['vrai_concept'], s78):.4f} | après {roc_auc_score(eval_['vrai_concept'], recal):.4f}  (le classement ne change pas : la transformation est croissante)")
```
<!--sortie-->
```text
semaines 7-8 : taux observé 0.405 | score moyen avant 0.280 | après recalibrage 0.404
AUC avant 0.9439 | après 0.9439  (le classement ne change pas : la transformation est croissante)
```

Le recalibrage ramène le score moyen au niveau du taux observé **sans toucher au classement** : c'est la première réponse à tenter quand seule la calibration dérive. Il reste soumis au même portail de promotion et se versionne comme un modèle.

### P.8 Étape 7 : automatiser

Tout ce qui précède doit pouvoir être **rejoué sans intervention**. On l'écrit sous forme de commandes et de fichiers de configuration. Ils ne sont **pas exécutés ici** (ni Docker ni service d'intégration continue ne sont disponibles dans notre environnement) ; chaque ligne est expliquée dans le livre, sections 4.4 et 4.6.

```dockerfile noexec
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service/ service/
ENV MODEL_ALIAS=production
EXPOSE 8000
CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml noexec
# .github/workflows/ci.yml : à chaque modification, tester avant de pouvoir livrer
name: ci
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install -r requirements.txt
      - run: pytest -q                       # tests de données, de modèle et de contrat d'API
```

### P.9 Étape 8 : le rapport de mise en production

On termine par une **liste de décision** (go / no-go), générée à partir des résultats : une mise en production se justifie par des critères écrits, pas par un sentiment.

```python
criteres = {
    "données validées (aucun problème détecté)": not problemes,
    "tests de modèle réussis": all(tests.values()),
    "AUC de test au-dessus de 0,85": roc_auc_score(y_te, p_te) > 0.85,
    "API : entrée invalide refusée (422)": r.status_code == 422,
    "API : parité avec le calcul hors ligne": abs(rep.json()["score"] - float(pipe.predict_proba(X_te.iloc[[0]])[0, 1])) < 1e-4,
    "modèle enregistré avec alias « production »": mv.aliases == ["production"] or "production" in mv.aliases,
    "supervision : la règle d'alerte détecte la dérive simulée (semaine 5)": bool(etat["alerte"].any()) and int(etat.loc[etat["alerte"], "semaine"].min()) == 5,
}
for nom, ok in criteres.items():
    print("OK " if ok else "À REVOIR", nom)
print("\nDécision :", "GO pour la mise en production" if all(criteres.values()) else "NO-GO")
```
<!--sortie-->
```text
OK  données validées (aucun problème détecté)
OK  tests de modèle réussis
OK  AUC de test au-dessus de 0,85
OK  API : entrée invalide refusée (422)
OK  API : parité avec le calcul hors ligne
OK  modèle enregistré avec alias « production »
OK  supervision : la règle d'alerte détecte la dérive simulée (semaine 5)

Décision : GO pour la mise en production
```

> ✅ **À retenir.** Un modèle en production, c'est **un pipeline testé, un modèle versionné, une API qui valide, une supervision qui regarde et un moyen de revenir en arrière**. Le modèle n'est qu'une des briques ; la plupart des pannes viennent d'ailleurs : données qui changent, entrées invalides, nouvelle version non testée, étiquettes qui arrivent trop tard.

### P.10 Les limites de l'étude

- **Simulation de production.** Les « huit semaines » sont tirées (avec remise à partir de la semaine 5) dans les 3 000 clients du jeu de test ; la dérive est fabriquée. En vraie production, la dérive est moins nette et ses causes sont à chercher (changement de la collecte, saison, campagne, panne d'un capteur).
- **Pas de service réel.** L'API est testée **en mémoire** (`TestClient`) : nous n'avons pas mesuré le comportement sous charge, ni la sécurité (authentification, limitation du débit), ni le déploiement conteneurisé.
- **Pas d'orchestration.** Le réentraînement est déclenché à la main dans ce projet ; un orchestrateur (livre, section 4.4) le déclencherait sur critère.
- **Seuil de décision supposé.** Le seuil de 0,20 de la configuration n'a pas été optimisé : il dépend des coûts réels de la relation client (volume III, section 4.3.5).
- **Équité et vie privée non traitées ici** : un score de résiliation utilisé pour cibler des clients pose ces questions (volume III, section 5.4 ; chapitre 5 de ce volume, section 5.4).

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des chapitres facultatifs (➕ 3.3, 4.4 à 4.7, 6 et 7) comptent si vous les avez lues.

### Deep learning (chapitre 1)

1. Combien de paramètres compte un réseau dense 784 → 128 → 10 (avec les biais) ?
2. Pourquoi un neurone à sortie sigmoïde, entraîné avec la perte logistique, est-il « une régression logistique » ?
3. Une couche convolutive prend une image 28 × 28 à un canal et applique 8 filtres 3 × 3 sans rembourrage. Combien de paramètres, et quelle taille de carte de sortie ?
4. Pourquoi les gradients disparaissent-ils dans un réseau profond à activations sigmoïdes ? Donnez un ordre de grandeur pour 10 couches, et deux remèdes.
5. Pour un neurone sigmoïde et la perte logistique, quel est le gradient de la perte par rapport à la pré-activation $z$ quand la probabilité prédite est 0,8 et que l'étiquette vaut 1 ?
6. Votre réseau a une perte d'entraînement qui baisse et une perte de validation qui remonte. Que diagnostiquez-vous, et quels leviers avez-vous ?
7. Que fait la porte d'oubli d'un LSTM, et quel problème du réseau récurrent simple le LSTM atténue-t-il ?
8. Sur le tableau des clients (résiliation), le réseau obtient une AUC de 0,869 et le boosting 0,896. Que concluez-vous, et que faut-il vérifier avant de généraliser ?

### NLP et modèles de langage (chapitre 2)

9. Calculez le poids TF-IDF ($\text{tf}\cdot\ln\frac N{\text{df}}$) d'un mot présent deux fois dans un avis et dans un seul des trois avis du corpus.
10. Quel est le cosinus entre les vecteurs de comptage $(1,0,1)$ et $(1,1,0)$ ?
11. Un classifieur de sentiments obtient 94 % sur un test tiré du même moule que l'entraînement. Pourquoi ce chiffre peut-il tromper, et comment le vérifier ?
12. Pourquoi divise-t-on les scores d'attention par $\sqrt{d_k}$ ? Quel est l'écart-type des scores bruts si $d_k=64$ et si les composantes sont indépendantes de variance 1 ?
13. Environ combien de paramètres un bloc transformer de dimension $d=256$ compte-t-il (ordre de grandeur $12\,d^2$) ?
14. Pourquoi l'attention coûte-t-elle « le carré de la longueur », et que devient le coût quand on double la longueur de la séquence ?
15. Que fait la température du décodage ? Donnez les probabilités de $\text{softmax}(2,1,0)$ à $T=1$ et à $T=0{,}5$.
16. Un système RAG répond faussement avec assurance. Quels maillons examinez-vous, dans quel ordre ?

### Big data et calcul distribué (chapitre 3)

17. Quel est l'accélération maximale d'un programme dont 90 % du temps se parallélise, sur 10 machines puis sur un nombre infini ?
18. Citez trois situations où l'on ne devrait **pas** distribuer le calcul.
19. Pourquoi une moyenne ne se combine-t-elle pas simplement par « moyenne des moyennes » dans un MapReduce, et comment la réécrire ?
20. Qu'est-ce que l'asymétrie des clés dans une jointure ou un regroupement, et comment le salage la corrige-t-il ?
21. Qu'appelle-t-on évaluation paresseuse dans Spark, et que signale un `Exchange` dans un plan ?
22. Un consommateur de messages offre la garantie « au moins une fois ». Que doit faire le traitement pour que le résultat reste correct ?

### MLOps (chapitre 4)

23. Un service reçoit 50 requêtes par seconde et chaque requête dure 0,2 s en moyenne. Combien de requêtes sont en cours en moyenne (loi de Little) ?
24. Pourquoi ne faut-il charger un modèle sérialisé par `pickle` que depuis une source de confiance ?
25. Qu'est-ce que le décalage entre entraînement et service ? Donnez un exemple qui ne fait planter aucun programme.
26. Quelle différence entre un déploiement fantôme et un déploiement canari ?
27. Calculez le PSI pour une variable dont la répartition attendue est (0,5 ; 0,5) et la répartition observée (0,3 ; 0,7).
28. Distinguez dérive des variables et dérive du concept : quel indicateur détecte chacune ?
29. Pourquoi une estimation de la performance sans étiquettes peut-elle être aveugle ? Citez le cas vu au chapitre.
30. Comment revient-on à la version précédente d'un modèle en moins d'une minute ?

### Ingénierie des données (chapitre 5)

31. Un fichier compte 19 700 lignes, dont 1 700 doublons et 782 rejets. Combien de lignes propres attendez-vous, et pourquoi cette « équation » est-elle un test ?
32. Pourquoi le rejeu d'un lot gonfle-t-il la table avec un simple ajout, et pas avec une fusion (*upsert*) ?
33. Combien de paires faudrait-il comparer pour 5 000 clients sans blocage ? À quoi sert le blocage ?
34. Pourquoi une empreinte de l'adresse électronique (SHA-256 sans clé) ne protège-t-elle pas les personnes ? Que faire à la place ?
35. Citez quatre dimensions de la qualité des données et, pour deux d'entre elles, une règle écrite comme une petite fonction.

### Plateformes cloud (chapitre 6)

36. Deux composants de disponibilité 99,9 % en série, puis le même composant en double (en parallèle) : quelle disponibilité chaque architecture donne-t-elle ?
37. Une machine réservée coûte 60 % du tarif à la demande, que l'on utilise la machine ou non. À partir de quel taux d'usage la réservation devient-elle rentable ?
38. Pourquoi les frais de sortie peuvent-ils changer le choix d'un fournisseur ?

### Applications de démonstration (chapitre 7)

39. Une application Streamlit réentraîne un modèle à chaque clic. Quelle est la cause, et comment la corriger ?
40. Quand faut-il remplacer l'application par une API ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np

print("Q1  paramètres :", 784 * 128 + 128 + 128 * 10 + 10)
print("Q3  filtres : ", 8 * (3 * 3 * 1) + 8, "paramètres ; carte", 28 - 3 + 1, "x", 28 - 3 + 1)
print("Q4  0,25^10 =", f"{0.25**10:.2e}")
print("Q5  p - y =", round(0.8 - 1, 1))
print("Q9  TF-IDF =", round(2 * np.log(3 / 1), 3))
a, b = np.array([1, 0, 1]), np.array([1, 1, 0])
print("Q10 cosinus =", round(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), 2))
print("Q12 écart-type des scores =", np.sqrt(64))
print("Q13 12 d^2 =", 12 * 256**2)
softmax = lambda z, T: np.round(np.exp(np.array(z) / T) / np.exp(np.array(z) / T).sum(), 3)
print("Q15 T=1 :", softmax([2, 1, 0], 1), " T=0,5 :", softmax([2, 1, 0], 0.5))
print("Q17 Amdahl :", round(1 / (0.1 + 0.9 / 10), 2), "sur 10 ; plafond", 1 / 0.1)
print("Q23 Little : L =", 50 * 0.2)
ps, qs = np.array([0.5, 0.5]), np.array([0.3, 0.7])
print("Q27 PSI =", round(float(((qs - ps) * np.log(qs / ps)).sum()), 4))
print("Q31 lignes propres =", 19700 - 1700 - 782)
print("Q33 paires =", 5000 * 4999 // 2)
print("Q36 série =", round(0.999 * 0.999 * 100, 4), "% ; parallèle =", round((1 - 0.001**2) * 100, 4), "%")
```
<!--sortie-->
```text
Q1  paramètres : 101770
Q3  filtres :  80 paramètres ; carte 26 x 26
Q4  0,25^10 = 9.54e-07
Q5  p - y = -0.2
Q9  TF-IDF = 2.197
Q10 cosinus = 0.5
Q12 écart-type des scores = 8.0
Q13 12 d^2 = 786432
Q15 T=1 : [0.665 0.245 0.09 ]  T=0,5 : [0.867 0.117 0.016]
Q17 Amdahl : 5.26 sur 10 ; plafond 10.0
Q23 Little : L = 10.0
Q27 PSI = 0.1695
Q31 lignes propres = 17218
Q33 paires = 12497500
Q36 série = 99.8001 % ; parallèle = 99.9999 %
```

**1.** $784\times128+128+128\times10+10=101\,770$ (code ci-dessus) : une matrice de poids et un biais par couche (1.1.3).

**2.** Un neurone calcule $\sigma(w\cdot x+b)$, exactement la forme de la régression logistique, et la perte logistique est la même : seul l'**algorithme** change (descente de gradient plutôt qu'une résolution dédiée) (1.1.1, 1.1.4).

**3.** $8\times(3\times3\times1)+8=80$ paramètres, quelle que soit la taille de l'image ; la carte de sortie est de $28-3+1=26$ sur 26 (par filtre). Le **partage** des filtres explique ce faible compte (1.2.4).

**4.** La dérivée de la sigmoïde vaut au plus 0,25 ; multipliée à travers 10 couches, elle donne au mieux $0{,}25^{10}\approx10^{-6}$ : les premières couches n'apprennent presque plus. Remèdes : **ReLU** (dérivée 1 pour les valeurs positives), **initialisation de He**, normalisation, connexions résiduelles (1.1.6).

**5.** Pour la sigmoïde et la perte logistique, $\partial L/\partial z=p-y=0{,}8-1=-0{,}2$ : le gradient est l'écart entre la probabilité et l'étiquette, sans facteur parasite (1.1.5).

**6.** **Surapprentissage.** Leviers : **arrêt précoce**, **décroissance des poids**, **dropout**, réseau plus petit, **augmentation** des données, davantage de données ; on juge sur **plusieurs graines**, pas sur une seule exécution (1.1.8).

**7.** La porte d'oubli décide, à chaque pas, quelle fraction de la mémoire de la cellule on **garde**. En laissant passer le signal presque intact, le LSTM atténue la **disparition du gradient dans le temps** du réseau récurrent simple (1.3.2, 1.3.3).

**8.** Sur ce tableau, le **boosting fait mieux** (0,896 contre 0,869) : le réseau n'est pas le bon outil par défaut sur des données tabulaires de cette taille. Avant de généraliser, il faut **répéter sur plusieurs graines et découpages**, comparer avec un **test apparié** et vérifier que le réseau a été réglé aussi sérieusement que le boosting (1.6.3).

**9.** $\text{tf}\cdot\ln(N/\text{df})=2\ln3\approx2{,}197$ (code ci-dessus) : un mot rare dans le corpus pèse plus qu'un mot partout présent, dont $\ln(N/N)=0$ (2.1.3).

**10.** Produit scalaire 1 ; normes $\sqrt2$ chacune ; cosinus $=1/2=0{,}5$ (2.1.3).

**11.** Un test **tiré du même moule** (mêmes gabarits, mêmes tournures) mesure surtout la mémorisation du gabarit. Il faut un test **écrit à la main, hors gabarit** : dans le chapitre, la même méthode tombe de 94,2 % à 62,5 % (2.1.4, 2.1.5).

**12.** Le produit scalaire de deux vecteurs aléatoires de dimension $d_k$ a une variance égale à $d_k$ ; sans division, le softmax **sature** (une probabilité proche de 1) et les gradients s'effondrent. Écart-type pour $d_k=64$ : $\sqrt{64}=8$ (2.2.3).

**13.** $12\times256^2=786\,432$ paramètres environ : $4d^2$ pour l'attention (requêtes, clés, valeurs, sortie) et $8d^2$ pour le réseau de la couche suivante, avec un facteur 4 (2.2.5).

**14.** Chaque jeton se compare à **tous** les autres : $n^2$ scores. Doubler la longueur multiplie donc le coût par **quatre** (2.2.6).

**15.** La température **divise les logits** avant le softmax : basse, elle concentre la masse sur le jeton le plus probable ; haute, elle l'étale. Résultats ci-dessus : à $T=1$, $(0{,}665 ;\ 0{,}245 ;\ 0{,}090)$ ; à $T=0{,}5$, la tête de distribution monte à $0{,}867$ (2.3.4).

**16.** Du début à la fin : **la recherche** (les bons passages sont-ils retrouvés ?), puis **le contexte fourni** (est-il complet, non contradictoire ?), puis **la génération** (la réponse reste-t-elle fidèle aux passages ?), avec des citations pour vérifier. Un maillon faux donne une réponse fausse et assurée (2.5.3).

**17.** $S(10)=1/(0{,}1+0{,}09)\approx5{,}26$ ; plafond $1/(1-p)=10$ quel que soit le nombre de machines, et le coût du mélange abaisse encore ces valeurs (3.1.5).

**18.** Quand les données **tiennent en mémoire** d'une machine, quand le **temps de coordination** dépasse le gain, quand une **requête SQL sur un fichier Parquet** avec DuckDB répond en secondes, quand l'équipe n'a pas les moyens d'**exploiter** une grappe (3.1.10, 3.2.11).

**19.** La moyenne n'est pas **associative** : la moyenne de moyennes de groupes de tailles différentes est fausse. On combine des **sommes et des effectifs** : chaque partition renvoie $(\text{somme},\text{effectif})$, puis on divise à la fin (3.1.4).

**20.** Quelques clés regroupent une grande part des lignes : une partition travaille bien plus que les autres et ralentit tout. Le **salage** ajoute un suffixe aléatoire à la clé, répartit la clé chaude sur plusieurs partitions, puis recombine (3.2.9).

**21.** Les **transformations** ne calculent rien ; elles construisent un plan, que seule une **action** déclenche. Un `Exchange` marque un **mélange** : des données voyagent entre machines, c'est là que se paie la performance (3.2.3, 3.2.4).

**22.** Être **idempotent** : traiter deux fois le même message ne doit pas changer le résultat (clé de message, fusion plutôt qu'ajout) (3.3.3, 3.3.5).

**23.** $L=\lambda W=50\times0{,}2=10$ requêtes en cours en moyenne : de quoi dimensionner le nombre de processus (4.2).

**24.** Charger un fichier `pickle` **exécute du code** choisi par son auteur : un fichier piégé prend la main sur la machine. On ne charge que des fichiers de source maîtrisée, ou l'on préfère un format qui n'exécute rien (ONNX, formats déclarés) (4.2, 4.5).

**25.** Les données vues par le service ne sont pas préparées comme à l'entraînement. Exemple du chapitre : une **erreur d'unité** dans une entrée ne plante rien mais fait chuter l'AUC de 0,867 à 0,538 sans aucune erreur visible (4.1).

**26.** En **fantôme**, la nouvelle version reçoit les mêmes requêtes mais **ses réponses ne sont pas utilisées** : on compare sans risque. En **canari**, une petite fraction du trafic réel est servie par la nouvelle version : on **mesure** avant d'élargir (4.2).

**27.** $\sum(q-p)\ln(q/p)=0{,}1695$ (code ci-dessus), soit entre 0,1 et 0,25 : un changement **modéré** selon l'usage courant (4.7).

**28.** **Dérive des variables** : la distribution des entrées change ; le **PSI** ou le test de Kolmogorov-Smirnov la repère. **Dérive du concept** : le lien entre entrées et résultat change, les entrées restent identiques (PSI sous 0,02) ; seuls la **performance** ou l'**écart de calibration** la repèrent (4.7, projet P.7).

**29.** L'estimation repose sur l'hypothèse que **le lien entre variables et cible n'a pas changé** : si le concept dérive, elle reste confiante à tort. Dans le chapitre : 63 % annoncés, 10 % réels (4.3).

**30.** Le service charge le modèle par un **alias** (« production ») du registre : revenir en arrière, c'est **déplacer l'alias** vers la version précédente, sans redéployer le code (4.2, 4.5).

**31.** $19\,700-1\,700-782=17\,218$ commandes propres (code ci-dessus). Chaque ligne lue doit se retrouver **quelque part** (propre, doublon, rebut) : si l'équation ne tombe pas juste, le pipeline perd ou invente des lignes en silence (5.1.4).

**32.** Un ajout simple **recopie** les lignes du lot rejoué (17 218 → 23 111 dans le chapitre). Une **fusion** identifie la ligne par sa clé : la ligne existante est remplacée, rien n'est dupliqué (5.1.7).

**33.** $5\,000\times4\,999/2=12\,497\,500$ paires, soit environ 12,5 millions. Le **blocage** ne compare que les enregistrements partageant une clé grossière (code postal, initiale) : 828 paires dans le chapitre, pour un rappel qu'il faut **mesurer** (5.3.5).

**34.** Une empreinte sans clé se **retrouve par dictionnaire** : on hache les adresses possibles et on compare (4 200 adresses retrouvées sur 4 200 dans le chapitre). Il faut une **clé secrète** (HMAC), conservée à part, et se souvenir que les **quasi-identifiants** réidentifient (5.4.5).

**35.** Par exemple : **complétude**, **validité**, **unicité**, **cohérence**, **exactitude**, **fraîcheur**. Une règle de validité : `def age_valide(x): return 18 <= x <= 110` ; une règle d'unicité : `df["id"].is_unique` (5.2.2, 5.2.3).

**36.** En série : $0{,}999^2=99{,}8001\ \%$, **moins** que chaque maillon ; en parallèle (redondance qui bascule correctement) : $1-0{,}001^2=99{,}9999\ \%$. Un maillon unique plafonne l'ensemble (6.1.4).

**37.** On paie $0{,}6$ par heure de l'année, utilisée ou non ; la machine à la demande coûte $u$ par heure d'usage : la réservation est rentable dès $u>60\ \%$ d'usage. Avec les prix inventés du chapitre, le seuil est de 62,5 % (6.3.1).

**38.** On paie la **sortie** des données (et non l'entrée) : quand les volumes sortants sont grands, ces frais peuvent valoir **dix fois** le calcul, et rendre la migration coûteuse (**gravité des données**) (6.1.6, 6.3.3).

**39.** Streamlit **rejoue le script** à chaque interaction : sans cache, l'entraînement se refait à chaque clic. On le place dans une fonction décorée par `cache_resource` (ou `cache_data` pour des données) pour ne le payer qu'une fois (7.2.1, 7.2.4).

**40.** Quand **un autre programme** doit appeler le modèle, quand **plusieurs équipes** le partagent, quand le modèle est **versionné** ou qu'une **exigence de disponibilité** existe : une application est faite pour un humain, une API pour des programmes (7.4.9, 4.6).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Calculer une rétropropagation, compter des paramètres | 1.1 |
| Régler optimiseur et régularisation, juger sur plusieurs graines | 1.1.7, 1.1.8 |
| Expliquer convolution, pooling, récurrence, LSTM | 1.2, 1.3 |
| Comparer un réseau à une référence sur un tableau | 1.6 |
| Représenter un texte et bâtir une référence solide | 2.1 |
| Calculer l'attention, décrire un transformer | 2.2 |
| Régler un décodage, connaître les limites des modèles de langage | 2.3 |
| Construire et évaluer un RAG, un agent | 2.5 |
| Décider s'il faut distribuer, borner un gain | 3.1 |
| Lire un plan Spark, traiter asymétrie et petits fichiers | 3.2 |
| Distinguer lot et flux, écrire des traitements idempotents | 3.3 |
| Rendre un modèle reproductible, le tester, le servir | 4.1, 4.2 |
| Superviser, régler des alertes, mesurer la dérive | 4.3, 4.7 |
| Orchestrer, suivre les essais, automatiser la livraison | 4.4, 4.5, 4.6 |
| Concevoir un ETL rejouable et en mesurer la qualité | 5.1, 5.2 |
| Réconcilier des enregistrements, protéger les personnes | 5.3, 5.4 |
| Raisonner sur coûts et sécurité dans le cloud | 6 |
| Concevoir, tester et publier une application de démonstration | 7 |
| Déployer et surveiller un modèle de bout en bout | Projet du volume |
