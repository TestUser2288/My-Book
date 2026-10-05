"""Boîte à outils du chapitre 5 (analyse de survie) : les estimateurs écrits à la main.

Le livre (sections 5.1 à 5.5) explique chaque estimateur et en cite les résultats ; ce module contient leur
code complet, réutilisé par le cahier (applications et exercices du chapitre 5) :

    import sys; sys.path.insert(0, "build")
    from outils_ch05 import *

Conventions : y = durées (mois), d = 1 si l'événement (départ) est observé, 0 si la durée est censurée à droite.
"""
from math import gamma, log

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize, minimize_scalar
from statsmodels.tools.numdiff import approx_hess3

def log_vraisemblance_exp(lam, y, d):
    return d.sum() * np.log(lam) - lam * y.sum()

def tableau_km(y, d):
    """Version pédagogique : une ligne par instant de départ, calcul direct."""
    y, d = np.asarray(y, float), np.asarray(d, int)
    lignes, S, somme_gw = [], 1.0, 0.0
    for t in np.unique(y[d == 1]):
        n = int(np.sum(y >= t))                      # ensemble à risque : encore là juste avant t
        dj = int(np.sum((y == t) & (d == 1)))        # départs à l'instant t
        cj = int(np.sum((y == t) & (d == 0)))        # censures à l'instant t (comptées après les départs)
        S *= 1 - dj / n
        somme_gw += dj / (n * (n - dj)) if n > dj else np.inf
        lignes.append((t, n, dj, cj, round(dj / n, 4), round(S, 4), round(somme_gw, 4)))
    return pd.DataFrame(lignes, columns=["t_j", "n_j (à risque)", "d_j (départs)", "censurés en t_j",
                                         "d_j/n_j", "S(t_j)", "somme Greenwood"])

def kaplan_meier(y, d, entree=None):
    """Kaplan-Meier vectorisé. Retourne (t_j, n_j, d_j, S, somme_greenwood).
    entree : date d'entrée dans l'observation (troncature à gauche), 0 par défaut."""
    y, d = np.asarray(y, float), np.asarray(d, int)
    tj = np.unique(y[d == 1])
    y_tries = np.sort(y)
    departs = np.sort(y[d == 1])
    sorties_avant = np.searchsorted(y_tries, tj, side="left")                # clients sortis strictement avant t_j
    entres_avant = len(y) if entree is None else np.searchsorted(np.sort(np.asarray(entree, float)), tj, side="left")
    n = entres_avant - sorties_avant                                          # à risque : entrés avant t_j et pas encore sortis
    dj = np.searchsorted(departs, tj, side="right") - np.searchsorted(departs, tj, side="left")
    S = np.cumprod(1 - dj / n)
    with np.errstate(divide="ignore"):
        gw = np.cumsum(dj / (n * (n - dj)))
    return tj, n, dj, S, gw

def surv_at(t, tj, S, avant=1.0):
    """Valeur de la fonction en escalier S à l'instant t (avant = valeur avant le premier départ)."""
    i = np.searchsorted(tj, t, side="right") - 1
    return avant if i < 0 else S[i]

def intervalles(t, tj, S, gw, z=1.959964):
    s, g = surv_at(t, tj, S), surv_at(t, tj, gw, avant=0.0)
    se = s * np.sqrt(g)
    plan = (s - z * se, s + z * se)
    log_ = (s * np.exp(-z * np.sqrt(g)), s * np.exp(z * np.sqrt(g)))
    expo = np.exp(z * np.sqrt(g) / abs(np.log(s)))
    loglog = (s ** expo, s ** (1 / expo))
    return s, plan, log_, loglog

def rmst(tj, S, tau):
    """Aire sous la courbe en escalier de 0 à tau."""
    bornes = np.concatenate([[0.0], tj[tj < tau], [tau]])
    valeurs = np.concatenate([[1.0], S[tj < tau]])
    return float(np.sum(valeurs * np.diff(bornes)))

def logrank(y, d, groupe):
    """Test du log-rank à K groupes. Retourne (observés, attendus, chi2, ddl, p)."""
    y, d, groupe = np.asarray(y, float), np.asarray(d, int), np.asarray(groupe)
    niveaux = np.unique(groupe)
    K = len(niveaux)
    O, E, V = np.zeros(K), np.zeros(K), np.zeros((K, K))
    for t in np.unique(y[d == 1]):
        r = np.array([np.sum((y >= t) & (groupe == g)) for g in niveaux], float)
        o = np.array([np.sum((y == t) & (d == 1) & (groupe == g)) for g in niveaux], float)
        n_, dj_ = r.sum(), o.sum()
        O += o
        E += dj_ * r / n_
        if n_ > 1:
            V += dj_ * (n_ - dj_) / (n_ - 1) * (np.diag(r) / n_ - np.outer(r, r) / n_**2)
    x = (O - E)[:-1]
    chi2 = float(x @ np.linalg.solve(V[:-1, :-1], x))
    return O, E, chi2, K - 1, stats.chi2.sf(chi2, K - 1)

def score_info(beta, y, d, x):
    """Score U(beta) et information I(beta) d'une covariable : boucle sur les départs."""
    U = I = 0.0
    for i in np.where(d == 1)[0]:
        R = y >= y[i]                                     # ensemble à risque
        w = np.exp(beta * x[R])
        m = (w * x[R]).sum() / w.sum()                    # moyenne pondérée de x dans R
        v = (w * x[R] ** 2).sum() / w.sum() - m**2        # variance pondérée
        U += x[i] - m
        I += v
    return U, I

def cox_ph(y, d, X):
    """Modèle de Cox par maximum de vraisemblance partielle (ex aequo : Breslow).
    y : durées, d : 1 = départ, X : matrice n x p.  Retourne un dictionnaire."""
    y, d, X = np.asarray(y, float), np.asarray(d, int), np.asarray(X, float)
    ordre = np.argsort(-y, kind="stable")
    ys, Xs = y[ordre], X[ordre]                                   # clients triés par durée DÉCROISSANTE
    tj = np.unique(y[d == 1])                                     # instants de départ distincts
    rang = np.searchsorted(-ys, -tj, side="right")                # nb de clients avec y >= t_j : leur ensemble à risque
    dj = np.array([np.sum((y == t) & (d == 1)) for t in tj])      # départs à chaque instant
    sx = np.array([X[(y == t) & (d == 1)].sum(axis=0) for t in tj])

    def sommes(beta):
        w = np.exp(Xs @ beta)
        s0 = np.cumsum(w)[rang - 1]                                                # somme des risques relatifs dans R_j
        s1 = np.cumsum(w[:, None] * Xs, axis=0)[rang - 1]                          # somme de w x
        s2 = np.cumsum(w[:, None, None] * Xs[:, :, None] * Xs[:, None, :], axis=0)[rang - 1]
        return s0, s1, s2

    def moins_ll(beta):
        s0, _, _ = sommes(beta)
        return -((sx @ beta).sum() - (dj * np.log(s0)).sum())

    def moins_score(beta):
        s0, s1, _ = sommes(beta)
        return -(sx.sum(axis=0) - (dj[:, None] * s1 / s0[:, None]).sum(axis=0))

    res = minimize(moins_ll, np.zeros(X.shape[1]), jac=moins_score, method="BFGS")
    beta = res.x
    s0, s1, s2 = sommes(beta)
    info = (dj[:, None, None] * (s2 / s0[:, None, None] - s1[:, :, None] * s1[:, None, :] / s0[:, None, None] ** 2)).sum(axis=0)
    return {"beta": beta, "cov": np.linalg.inv(info), "info": info, "ll": -res.fun,
            "ll0": -moins_ll(np.zeros(X.shape[1])), "tj": tj, "dj": dj, "s0": s0}

def test_ph(y, d, X, fit):
    """Test de score de proportionnalité des risques (Grambsch-Therneau), g(t) = rang de la durée."""
    y, d, X, beta, V = np.asarray(y, float), np.asarray(d, int), np.asarray(X, float), fit["beta"], fit["cov"]
    ev = np.where(d == 1)[0]
    g = stats.rankdata(y)[ev]
    g = g - g.mean()
    w = np.exp(X @ beta)
    ordre = np.argsort(-y, kind="stable")
    ys, Xs, ws = y[ordre], X[ordre], w[ordre]
    pos = np.searchsorted(-ys, -y[ev], side="right") - 1                  # fin de l'ensemble à risque de chaque départ
    s0 = np.cumsum(ws)[pos]
    m1 = np.cumsum(ws[:, None] * Xs, axis=0)[pos] / s0[:, None]
    cov = np.cumsum(ws[:, None, None] * Xs[:, :, None] * Xs[:, None, :], axis=0)[pos] / s0[:, None, None] - m1[:, :, None] * m1[:, None, :]
    R = X[ev] - m1                                                          # résidus de Schoenfeld (non normalisés)
    U = (g[:, None] * R).sum(axis=0)                                        # score des coefficients dépendant du temps
    Ibt = (g[:, None, None] * cov).sum(axis=0)
    Itt = (g[:, None, None] ** 2 * cov).sum(axis=0)
    Schur = Itt - Ibt.T @ V @ Ibt                                           # information « nette » (le beta est re-estimé)
    chi2_j = np.array([U[j] ** 2 / Schur[j, j] for j in range(X.shape[1])])
    chi2_glob = float(U @ np.linalg.solve(Schur, U))
    return chi2_j, chi2_glob

def indice_concordance(y, d, eta):
    """C de Harrell : pourcentage de couples comparables bien ordonnés (les ex aequo de score comptent pour 1/2)."""
    y, d, eta = np.asarray(y), np.asarray(d), np.asarray(eta)
    concordants = egalites = total = 0
    for i in np.where(d == 1)[0]:
        plus_longs = y > y[i]                                  # clients observés plus longtemps que i
        total += plus_longs.sum()
        concordants += (eta[plus_longs] < eta[i]).sum()         # i a un score de risque plus élevé : bien ordonné
        egalites += (eta[plus_longs] == eta[i]).sum()
    return (concordants + 0.5 * egalites) / total

def log_vrais_aft(theta, y, d, X, loi):
    """theta = (gamma_0..gamma_p, ln sigma). Retourne la log-vraisemblance (avec censure à droite)."""
    gam, sigma = theta[:-1], np.exp(theta[-1])
    z = (np.log(y) - X @ gam) / sigma
    if loi == "weibull":
        lf, ls = z - np.exp(z), -np.exp(z)
    elif loi == "lognormale":
        lf, ls = stats.norm.logpdf(z), stats.norm.logsf(z)
    elif loi == "loglogistique":
        lf, ls = z - 2 * np.log1p(np.exp(z)), -np.log1p(np.exp(z))
    return np.sum(d * (lf - np.log(sigma) - np.log(y)) + (1 - d) * ls)

def ajuster(loi, y, d, X, sigma_fixe=None):
    """Maximum de vraisemblance. sigma_fixe=1 donne l'exponentielle (Weibull avec sigma = 1)."""
    p = X.shape[1]
    if sigma_fixe is None:
        f = lambda t: -log_vrais_aft(t, y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1), [0.0]])
    else:
        f = lambda t: -log_vrais_aft(np.concatenate([t, [np.log(sigma_fixe)]]), y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1)])
    r = minimize(f, t0, method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-11, "maxiter": 20000, "maxfev": 20000})
    r = minimize(f, r.x, method="BFGS")                                   # affinage
    H = approx_hess3(r.x, f)
    return {"theta": r.x, "cov": np.linalg.inv(H), "ll": -r.fun, "k": len(r.x)}

def survie_aft(t, mu, sigma, loi):
    z = (np.log(t) - mu) / sigma
    return {"weibull": lambda: np.exp(-np.exp(z)), "lognormale": lambda: stats.norm.sf(z), "loglogistique": lambda: 1 / (1 + np.exp(z))}[loi]()

def survie_marginale(t_grille, theta, loi, Xmat):
    mu, sg = Xmat @ theta[:-1], np.exp(theta[-1])
    return np.array([survie_aft(t, mu, sg, loi).mean() for t in t_grille])

def km_simple(t, dd):
    tj = np.unique(t[dd == 1])
    ys, ev = np.sort(t), np.sort(t[dd == 1])
    n_ = len(t) - np.searchsorted(ys, tj, side="left")
    dj_ = np.searchsorted(ev, tj, side="right") - np.searchsorted(ev, tj, side="left")
    return tj, np.cumprod(1 - dj_ / n_)

def incidence_cumulee(t, cause):
    """Aalen-Johansen. t : durées, cause : 0 = censuré, 1, 2, ... Retourne (instants, survie totale, [CIF des causes])."""
    t, cause = np.asarray(t, float), np.asarray(cause, int)
    tj = np.unique(t[cause > 0])
    ys = np.sort(t)
    n_ = len(t) - np.searchsorted(ys, tj, side="left")                          # ensemble à risque
    causes = sorted(set(cause[cause > 0]))
    dk = [np.array([np.sum((t == u) & (cause == k)) for u in tj]) for k in causes]
    S = np.cumprod(1 - sum(dk) / n_)                                            # survie totale (Kaplan-Meier toutes causes)
    S_avant = np.concatenate([[1.0], S[:-1]])                                   # S(t_j^-)
    return tj, S, [np.cumsum(S_avant * d_ / n_) for d_ in dk]
