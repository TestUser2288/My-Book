"""Outils du chapitre 4 (MLOps) : données et modèles de la résiliation, PSI, scénarios de dérive, service FastAPI, mini-orchestrateur.

Ce module est utilisé par les blocs cachés du livre (sections/04-*.md). Le cahier montre le code équivalent pas à pas.
Tout est déterministe (graines fixes), hors ligne, et n'écrit que dans des dossiers temporaires fournis par l'appelant.
"""
import hashlib
import json
import math
import os
import time
from graphlib import TopologicalSorter
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

EXCLUES = ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]
CAT = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]


def donnees(chemin="donnees/clients_ml.csv"):
    """Chargement et découpage 60 % entraînement / 20 % test / 20 % « réservoir de production » (graine 0)."""
    c = pd.read_csv(chemin)
    X, y = c.drop(columns=EXCLUES), c["churn_90j"]
    num = [k for k in X.columns if k not in CAT]
    Xtr, Xrest, ytr, yrest = train_test_split(X, y, test_size=0.4, random_state=0, stratify=y)
    Xte, Xpool, yte, ypool = train_test_split(Xrest, yrest, test_size=0.5, random_state=0, stratify=yrest)
    return dict(X=X, y=y, num=num, cat=CAT, Xtr=Xtr, ytr=ytr, Xte=Xte, yte=yte, Xpool=Xpool.reset_index(drop=True),
                ypool=ypool.reset_index(drop=True).to_numpy())


def modele_v1(d):
    """Régression logistique : imputation médiane + indicateurs d'absence, mise à l'échelle, one-hot."""
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median", add_indicator=True)), ("sc", StandardScaler())]), d["num"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), d["cat"])])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000))]).fit(d["Xtr"], d["ytr"])


def modele_v2(d):
    """Boosting par histogrammes : valeurs manquantes et catégories gérées nativement."""
    pre = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan), d["cat"])],
                            remainder="passthrough", verbose_feature_names_out=False)
    clf = HistGradientBoostingClassifier(random_state=0, categorical_features=list(range(len(d["cat"]))))
    return Pipeline([("pre", pre), ("clf", clf)]).fit(d["Xtr"], d["ytr"])


def hash_fichier(chemin, n=12):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()[:n]


# ------------------------------------------------------------------ dérive
def psi(ref, new, k=10, eps=1e-4):
    """Population Stability Index : bornes = déciles de la référence ; valeurs manquantes ignorées."""
    ref, new = np.asarray(ref, float), np.asarray(new, float)
    ref, new = ref[~np.isnan(ref)], new[~np.isnan(new)]
    coupures = np.unique(np.quantile(ref, np.linspace(0, 1, k + 1)[1:-1]))
    bornes = np.concatenate([[-np.inf], coupures, [np.inf]])
    pr = np.clip(np.histogram(ref, bornes)[0] / len(ref), eps, None)
    pn = np.clip(np.histogram(new, bornes)[0] / len(new), eps, None)
    return float(((pn - pr) * np.log(pn / pr)).sum())


def semaine(d, modele, k, scenario, n=800, seuil=0.30):
    """Un lot de production de la semaine k (1 à 4) tiré du réservoir.

    scenario = "covariable" : la population change (plus de chasseurs de promotions, moins de satisfaits), P(y|x) inchangée ;
    scenario = "concept"    : la population est la même, mais une campagne de rétention retient une part croissante des clients
                              que le modèle signale (score >= seuil) : la relation entre x et y change.
    """
    pool = d["Xpool"]
    rng = np.random.default_rng(100 + k)
    if scenario == "covariable":
        def z(s):
            s = s.fillna(s.median())
            return ((s - s.mean()) / s.std()).to_numpy()
        w = np.exp([0, 0.25, 0.5, 0.75][k - 1] * (z(pool["part_achats_promo"]) - z(pool["satisfaction_moy"])))
        w = w / w.sum()
    else:
        w = np.full(len(pool), 1 / len(pool))
    idx = rng.choice(len(pool), n, p=w)
    Xw, yw = pool.iloc[idx].reset_index(drop=True), d["ypool"][idx].copy()
    if scenario == "concept":
        retenus = (modele.predict_proba(Xw)[:, 1] >= seuil) & (rng.random(n) < [0, 0.25, 0.5, 0.75][k - 1])
        yw[retenus] = 0
    return Xw, yw


# ------------------------------------------------------------------ service FastAPI
def creer_app(chemin_modele, colonnes, version="2.0.0"):
    """Service de scoring : /health, /predict (un client), /predict_batch (liste), validation stricte des entrées."""
    import joblib
    from fastapi import FastAPI
    from pydantic import BaseModel, Field

    class Client(BaseModel):
        age: int = Field(ge=18, le=100)
        ville: str
        canal_acquisition: str
        appareil: Optional[str] = None
        anciennete_mois: int = Field(ge=0)
        nb_commandes_12m: int = Field(ge=0)
        panier_moyen: Optional[float] = Field(default=None, ge=0)
        montant_12m: float = Field(ge=0)
        recence_jours: int = Field(ge=0, le=365)
        nb_retours_12m: int = Field(ge=0)
        satisfaction_moy: Optional[float] = Field(default=None, ge=1, le=5)
        nb_tickets_support_12m: int = Field(ge=0)
        programme_fidelite: int = Field(ge=0, le=1)
        nb_promos_recues_12m: int = Field(ge=0)
        part_achats_promo: float = Field(ge=0, le=1)
        taux_ouverture_email: float = Field(ge=0, le=1)
        delai_livraison_moy: Optional[float] = Field(default=None, ge=0)
        categorie_preferee: str
        revenu_zone: float

    modele = joblib.load(chemin_modele)
    app = FastAPI(title="Risque de résiliation", version=version)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": version}

    @app.post("/predict")
    def predict(c: Client):
        df = pd.DataFrame([c.model_dump()])[colonnes]
        return {"probabilite": round(float(modele.predict_proba(df)[0, 1]), 4), "version": version}

    @app.post("/predict_batch")
    def predict_batch(lot: list[Client]):
        if not lot:
            return {"probabilites": [], "version": version}
        df = pd.DataFrame([c.model_dump() for c in lot])[colonnes]
        return {"probabilites": [round(float(p), 4) for p in modele.predict_proba(df)[:, 1]], "version": version}

    app.Client = Client
    return app


def ligne_json(ligne):
    """Convertit une ligne pandas en dictionnaire JSON (NaN -> None, entiers numpy -> int)."""
    out = {}
    for k, v in ligne.to_dict().items():
        if isinstance(v, (float, np.floating)) and math.isnan(v):
            out[k] = None
        elif isinstance(v, np.integer):
            out[k] = int(v)
        elif isinstance(v, np.floating):
            out[k] = float(v)
        else:
            out[k] = v
    return out


# ------------------------------------------------------------------ mini-orchestrateur
class MiniOrchestrateur:
    """Exécute un graphe de tâches dans l'ordre topologique, avec reprises (retries) et journal d'état. Équivalent minimal d'un DAG Airflow."""

    def __init__(self, reprises=2):
        self.taches, self.deps, self.reprises, self.journal = {}, {}, reprises, []

    def tache(self, nom, depend_de=()):
        def deco(f):
            self.taches[nom], self.deps[nom] = f, tuple(depend_de)
            return f
        return deco

    def lancer(self, jour):
        etat = {}
        for nom in TopologicalSorter(self.deps).static_order():
            if any(etat[p] != "ok" for p in self.deps[nom]):
                etat[nom] = "ignorée"
                self.journal.append((jour, nom, 0, "ignorée"))
                continue
            for essai in range(1, self.reprises + 2):
                try:
                    self.taches[nom](jour)
                    etat[nom] = "ok"
                    self.journal.append((jour, nom, essai, "ok"))
                    break
                except Exception as e:                                   # noqa: BLE001
                    etat[nom] = "échec"
                    self.journal.append((jour, nom, essai, f"échec ({type(e).__name__})"))
        return etat
