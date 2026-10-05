"""Outils du chapitre 8 (apprentissage semi-supervisé et actif) : jeux de données préparés, stratégies d'acquisition,
boucle d'apprentissage actif. Utilisé par les blocs cachés du livre ; le cahier réécrit les parties essentielles à la main.

    import sys; sys.path.insert(0, "build"); import outils_ch08 as o
"""
import warnings

import numpy as np
import pandas as pd
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")


# ------------------------------------------------------------------ données
def charger_digits(graine=0):
    """Chiffres manuscrits (jeu RÉEL de scikit-learn) : pool d'entraînement (1 347 images) et jeu de test (450)."""
    d = load_digits()
    X, y = d.data / 16.0, d.target
    return train_test_split(X, y, test_size=0.25, random_state=graine, stratify=y)


def charger_churn(chemin="donnees/clients_ml.csv", graine=0):
    """Clients de la boutique : pool (9 000) et test (3 000), variables centrées-réduites, sans colonne de fuite."""
    c = pd.read_csv(chemin)
    X = c.drop(columns=["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"])
    X = pd.get_dummies(X, columns=["ville", "canal_acquisition", "appareil", "categorie_preferee"], dummy_na=True, dtype=float)
    X = X.fillna(X.median())
    Xp, Xt, yp, yt = train_test_split(X.to_numpy(), c["churn_90j"].to_numpy(), test_size=0.25, random_state=graine, stratify=c["churn_90j"])
    sc = StandardScaler().fit(Xp)
    return sc.transform(Xp), sc.transform(Xt), yp, yt


def tirer_etiquettes(y, n, rng, stratifie=False, min_positifs=2):
    """Indices des n exemples « étiquetés ». Si stratifie : proportions de classes respectées (au moins `min_positifs` positifs)."""
    if not stratifie:
        return rng.choice(len(y), n, replace=False)
    pos = np.where(y == 1)[0]
    k = max(min_positifs, int(round(n * y.mean())))
    return np.r_[rng.choice(pos, k, replace=False), rng.choice(np.where(y == 0)[0], n - k, replace=False)]


# ------------------------------------------------------------------ scores d'acquisition (plus grand = plus utile à étiqueter)
def proba_complete(modele, X, k):
    """predict_proba avec toutes les k classes (les classes jamais vues reçoivent la probabilité 0)."""
    P = np.zeros((len(X), k))
    P[:, modele.classes_] = modele.predict_proba(X)
    return P


def score_incertitude(P):
    return 1 - P.max(axis=1)


def score_marge(P):
    s = np.sort(P, axis=1)
    return 1 - (s[:, -1] - s[:, -2])


def score_entropie(P):
    return -(P * np.log(P + 1e-12)).sum(axis=1)


def score_comite(modeles, X, k):
    """Entropie du vote d'un comité de modèles (« query by committee »)."""
    votes = np.stack([m.predict(X) for m in modeles])             # (nb_modeles, n)
    freq = np.stack([(votes == c).mean(axis=0) for c in range(k)], axis=1)
    return -(freq * np.log(freq + 1e-12)).sum(axis=1)


def densite(X, nb_ref=400, graine=0):
    """Similarité cosinus moyenne de chaque point à un échantillon de référence : grande = point « typique » du pool."""
    rng = np.random.default_rng(graine)
    ref = X[rng.choice(len(X), min(nb_ref, len(X)), replace=False)]
    A = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    B = ref / (np.linalg.norm(ref, axis=1, keepdims=True) + 1e-12)
    return (A @ B.T).mean(axis=1)


def init_medoides(X, k, graine=0):
    """Démarrage à froid : on fait étiqueter les k « médoïdes » (le point le plus proche du centre de chaque groupe de k-means)."""
    from sklearn.cluster import KMeans
    centres = KMeans(k, n_init=5, random_state=graine).fit(X).cluster_centers_
    return np.array([int(np.argmin(((X - c) ** 2).sum(axis=1))) for c in centres])


# ------------------------------------------------------------------ la boucle d'apprentissage actif
def boucle_active(Xp, yp, Xt, yt, strategie, idx0, lot, budget, graine, k, metrique="acc", beta=1.0, nb_comite=5, renvoyer_etiq=False):
    """Boucle « pool-based » : on entraîne, on score les non étiquetés, on demande `lot` étiquettes, on recommence.
    Renvoie un tableau (n_etiquettes, score_test, part_positifs_etiquetes, proba_moyenne_test)."""
    rng = np.random.default_rng(graine)
    etiq = list(idx0)
    dens = densite(Xp, graine=graine) if strategie == "densite" else None
    lignes = []
    while True:
        m = LogisticRegression(max_iter=1000).fit(Xp[etiq], yp[etiq])
        if metrique == "acc":
            s = m.score(Xt, yt); ptest = np.nan
        else:
            Pt = m.predict_proba(Xt)[:, 1]; s = roc_auc_score(yt, Pt); ptest = Pt.mean()
        lignes.append((len(etiq), s, yp[etiq].mean(), ptest))
        if len(etiq) >= budget:
            break
        libres = np.setdiff1d(np.arange(len(Xp)), etiq)
        if strategie == "aleatoire":
            choix = rng.choice(libres, lot, replace=False)
        else:
            P = proba_complete(m, Xp[libres], k)
            if strategie == "incertitude":
                sc = score_incertitude(P)
            elif strategie == "marge":
                sc = score_marge(P)
            elif strategie == "entropie":
                sc = score_entropie(P)
            elif strategie == "densite":
                sc = score_entropie(P) * dens[libres] ** beta
            elif strategie == "comite":
                membres = []
                for _ in range(nb_comite):
                    b = rng.choice(etiq, len(etiq), replace=True)
                    membres.append(LogisticRegression(max_iter=1000).fit(Xp[b], yp[b]))
                sc = score_comite(membres, Xp[libres], k)
            else:
                raise ValueError(strategie)
            sc = sc + 1e-9 * rng.random(len(sc))                  # départage les ex æquo de façon reproductible
            choix = libres[np.argsort(-sc)[:lot]]
        etiq.extend(int(i) for i in choix)
    return (np.array(lignes), np.array(etiq)) if renvoyer_etiq else np.array(lignes)


# ------------------------------------------------------------------ comparaisons semi-supervisées
def courbe_semi(Xp, yp, Xt, yt, budgets, graines, seuil=0.9, k=7, alpha=0.2, base=100):
    """Précision sur le jeu de test selon le nombre d'étiquettes : modèle supervisé seul, auto-apprentissage, label spreading.
    Renvoie un dict nom -> tableau (nb_budgets, nb_graines). Les étiquettes sont tirées au hasard (graine base+s)."""
    from sklearn.semi_supervised import LabelSpreading, SelfTrainingClassifier
    out = {"supervise": [], "auto": [], "propagation": []}
    for nl in budgets:
        lignes = {"supervise": [], "auto": [], "propagation": []}
        for s in range(graines):
            rng = np.random.default_rng(base + s)
            idx = rng.choice(len(Xp), nl, replace=False)
            y_part = np.full(len(Xp), -1)
            y_part[idx] = yp[idx]
            lignes["supervise"].append(LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx]).score(Xt, yt))
            lignes["auto"].append(SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=seuil).fit(Xp, y_part).score(Xt, yt))
            lignes["propagation"].append(LabelSpreading(kernel="knn", n_neighbors=k, alpha=alpha, max_iter=200).fit(Xp, y_part).score(Xt, yt))
        for nom in out:
            out[nom].append(lignes[nom])
    return {nom: np.array(v) for nom, v in out.items()}
