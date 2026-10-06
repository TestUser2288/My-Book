"""Outils du chapitre 2 (modélisation actuarielle) — partagés par le livre (blocs cachés) et le cahier.

Tout est écrit à la main (numpy / pandas / statsmodels) : chain ladder, Mack, Bornhuetter-Ferguson, bootstrap ODP,
crédibilité de Bühlmann-Straub, courbe de Lorenz ordonnée et indice de Gini de tarification.
"""
import numpy as np
import pandas as pd

ZONES = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F"]


# ----------------------------------------------------------------------------------------------- données
def charger_polices(dossier="donnees"):
    p = pd.read_csv(f"{dossier}/polices_auto.csv")
    s = pd.read_csv(f"{dossier}/sinistres_auto.csv")
    p["classe_age"] = pd.cut(p["age_conducteur"], [17, 24, 29, 39, 49, 59, 69, 120],
                             labels=["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70+"]).astype(str)
    p["bm_classe"] = pd.cut(p["bonus_malus"], [0, 60, 80, 100, 120, 200], labels=["<=60", "61-80", "81-100", "101-120", ">120"]).astype(str)
    return p, s


def cout_par_police(p, s, plafond=None):
    """Ajoute à `p` le coût total (éventuellement écrêté à `plafond` par sinistre) et le nombre de sinistres matériels."""
    m = s["montant"].clip(upper=plafond) if plafond else s["montant"]
    tot = m.groupby(s["id_police"]).sum()
    q = p.copy()
    q["cout"] = q["id_police"].map(tot).fillna(0.0)
    return q


# ----------------------------------------------------------------------------------------------- évaluation d'un tarif
def lorenz_gini(prime, cout, expo, graine=0):
    """Courbe de Lorenz ordonnée (Frees) : on trie les contrats du moins risqué au plus risqué selon la prime prédite par unité
    d'exposition (égalités départagées au hasard, graine fixe) ; renvoie (part cumulée d'exposition, part cumulée de coût,
    indice de Gini = 2·aire entre la diagonale et la courbe)."""
    r = np.asarray(prime, float) / np.asarray(expo, float)
    prime, cout, expo = np.asarray(prime, float), np.asarray(cout, float), np.asarray(expo, float)
    perm = np.random.default_rng(graine).permutation(len(r))
    prime, cout, expo, r = prime[perm], cout[perm], expo[perm], r[perm]
    o = np.argsort(r, kind="stable")
    e = np.cumsum(expo[o]) / expo.sum()
    c = np.cumsum(cout[o]) / cout.sum()
    x = np.concatenate([[0], e]); y = np.concatenate([[0], c])
    aire = np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2)
    return x, y, float(1 - 2 * aire)


def lift_deciles(prime, cout, expo, k=10):
    """Par classes d'exposition égale (selon la prime prédite par unité d'exposition) : prédit et observé par unité d'exposition."""
    r = prime / expo
    o = np.argsort(r, kind="stable")
    e = np.cumsum(expo[o]) / expo.sum()
    cl = np.minimum((e * k - 1e-12).astype(int), k - 1)
    d = pd.DataFrame({"cl": cl, "prime": prime[o], "cout": cout[o], "expo": expo[o]}).groupby("cl").sum()
    return pd.DataFrame({"predit": d["prime"] / d["expo"], "observe": d["cout"] / d["expo"], "expo": d["expo"]})


def deviance_poisson(y, mu, w=None):
    """Déviance de Poisson (somme) : 2 Σ [y ln(y/μ) − (y − μ)]."""
    y = np.asarray(y, float); mu = np.asarray(mu, float)
    t = np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0.0) - (y - mu)
    return float(2 * np.sum(t if w is None else w * t))


# ----------------------------------------------------------------------------------------------- triangles
def triangle_cumule(df, col="paiement_cumule"):
    """DataFrame long -> matrice (années × délais) avec NaN dans la partie inconnue."""
    return df.pivot(index="annee_survenance", columns="delai", values=col)


def facteurs_chain_ladder(C, exclure_diagonale=None):
    """Facteurs de développement f_j = Σ_i C_{i,j+1} / Σ_i C_{i,j} (pondérés par les volumes), sur les années où C_{i,j+1} est connu.
    `exclure_diagonale` : indice calendaire (i + j + 1) à écarter du calcul (cellules d'une diagonale douteuse)."""
    C = np.asarray(C, float)
    n, m = C.shape
    f = np.ones(m - 1)
    for j in range(m - 1):
        idx = [i for i in range(n) if not np.isnan(C[i, j + 1])]
        if exclure_diagonale is not None:
            idx = [i for i in idx if i + j + 1 != exclure_diagonale]
        f[j] = C[idx, j + 1].sum() / C[idx, j].sum()
    return f


def projeter(C, f, f_queue=1.0):
    """Complète le triangle par chain ladder ; renvoie (carré projeté, ultime par année). La queue multiplie le dernier cumul."""
    C = np.asarray(C, float).copy()
    n, m = C.shape
    for i in range(n):
        dern = int(np.max(np.where(~np.isnan(C[i]))[0]))
        for j in range(dern, m - 1):
            C[i, j + 1] = C[i, j] * f[j]
    ult = C[:, -1] * f_queue
    return C, ult


def facteur_queue(f, depuis=4, horizon=60):
    """Facteur de queue par extrapolation : on ajuste log(f_j − 1) = a + b·j sur les délais j ≥ `depuis`, puis on prolonge la décroissance
    géométrique au-delà du dernier délai observé. Renvoie (facteur de queue, taux de décroissance e^b)."""
    f = np.asarray(f, float)
    j = np.arange(len(f))
    sel = j >= depuis
    b, a = np.polyfit(j[sel], np.log(f[sel] - 1), 1)
    fut = np.arange(len(f), len(f) + horizon)
    return float(np.prod(1 + np.exp(a + b * fut))), float(np.exp(b))


def dernier_cumul(C):
    C = np.asarray(C, float)
    return np.array([C[i, np.max(np.where(~np.isnan(C[i]))[0])] for i in range(C.shape[0])])


def mack(C, f=None):
    """Erreur quadratique de prédiction de Mack (1993) pour les réserves par année et au total (queue = 1).
    Renvoie un DataFrame (reserve, erreur_type) et l'erreur type totale."""
    C = np.asarray(C, float)
    n, m = C.shape
    if f is None:
        f = facteurs_chain_ladder(C)
    sig2 = np.zeros(m - 1)
    for j in range(m - 1):
        idx = [i for i in range(n) if not np.isnan(C[i, j + 1])]
        r = C[idx, j + 1] / C[idx, j] - f[j]
        if len(idx) > 1:
            sig2[j] = np.sum(C[idx, j] * r ** 2) / (len(idx) - 1)
    # dernier facteur : extrapolation de Mack
    if m >= 3 and sig2[m - 2] == 0:
        sig2[m - 2] = min(sig2[m - 3] ** 2 / sig2[m - 4], sig2[m - 4], sig2[m - 3]) if sig2[m - 4] > 0 else sig2[m - 3]
    Cp, ult = projeter(C, f)
    dc = dernier_cumul(C)
    res = ult - dc
    mse = np.zeros(n)
    for i in range(n):
        dern = int(np.max(np.where(~np.isnan(C[i]))[0]))
        s = 0.0
        for k in range(dern, m - 1):
            s += sig2[k] / f[k] ** 2 * (1 / Cp[i, k] + 1 / np.nansum(C[: n - k - 1, k]))
        mse[i] = ult[i] ** 2 * s
    # covariance entre années (formule de Mack)
    tot = mse.sum()
    for i in range(n):
        di = int(np.max(np.where(~np.isnan(C[i]))[0]))
        for l in range(i + 1, n):
            dl = int(np.max(np.where(~np.isnan(C[l]))[0]))
            s = 0.0
            for k in range(di, m - 1):
                s += sig2[k] / f[k] ** 2 / np.nansum(C[: n - k - 1, k])
            tot += 2 * ult[i] * ult[l] * s
    out = pd.DataFrame({"reserve": res, "erreur_type": np.sqrt(mse)})
    return out, float(np.sqrt(tot)), sig2


def bornhuetter_ferguson(C, f, prime, lr_prior, f_queue=1.0):
    """Ultime BF = payé + ultime a priori × (1 − part payée attendue), part payée = 1/(produit des facteurs restants)."""
    C = np.asarray(C, float)
    n, m = C.shape
    dc = dernier_cumul(C)
    ult = np.zeros(n)
    for i in range(n):
        dern = int(np.max(np.where(~np.isnan(C[i]))[0]))
        reste = np.prod(f[dern:]) * f_queue
        part_payee = 1.0 / reste
        ult[i] = dc[i] + prime[i] * lr_prior * (1 - part_payee)
    return ult


def bootstrap_odp(inc, n_boot=1000, graine=0, phi_corr=True):
    """Bootstrap de l'England–Verrall : GLM de Poisson (lignes + colonnes) sur les paiements incrémentaux, résidus de Pearson rééchantillonnés.
    `inc` : matrice (années × délais) de paiements incrémentaux avec NaN dans la partie inconnue. Renvoie le vecteur des réserves totales simulées
    (processus + paramètres) et la réserve centrale."""
    import statsmodels.api as sm
    rng = np.random.default_rng(graine)
    inc = np.asarray(inc, float)
    n, m = inc.shape
    ii, jj = np.indices((n, m))
    obs = ~np.isnan(inc)
    ligne, col = ii[obs], jj[obs]
    X = np.zeros((obs.sum(), n + m - 1))
    X[np.arange(obs.sum()), ligne] = 1
    mask_col = col > 0
    X[np.arange(obs.sum())[mask_col], n + col[mask_col] - 1] = 1

    def ajuste(y):
        mod = sm.GLM(y, X, family=sm.families.Poisson()).fit()
        return mod

    y = inc[obs]
    mod = ajuste(y)
    mu = mod.fittedvalues
    r = (y - mu) / np.sqrt(mu)
    p = len(mod.params)
    ndata = len(y)
    adj = np.sqrt(ndata / max(ndata - p, 1)) if phi_corr else 1.0
    r = r * adj
    phi = float(np.sum(((y - mu) / np.sqrt(mu)) ** 2) / max(ndata - p, 1))
    # matrice complète des moyennes futures
    Xfull = np.zeros((n * m, n + m - 1))
    idx = np.arange(n * m)
    li, co = ii.ravel(), jj.ravel()
    Xfull[idx, li] = 1
    mc = co > 0
    Xfull[idx[mc], n + co[mc] - 1] = 1
    futur = (ii + jj > n - 1).ravel()
    reserve_centrale = float(np.exp(Xfull[futur] @ mod.params).sum())
    sims = np.empty(n_boot)
    for b in range(n_boot):
        rs = rng.choice(r, size=len(y), replace=True)
        ystar = np.maximum(mu + rs * np.sqrt(mu), 0)
        try:
            mb = ajuste(ystar)
        except Exception:
            sims[b] = np.nan
            continue
        mf = np.exp(Xfull[futur] @ mb.params)
        sims[b] = np.sum(phi * rng.poisson(np.maximum(mf, 1e-9) / phi))
    return sims[~np.isnan(sims)], reserve_centrale, phi


# ----------------------------------------------------------------------------------------------- crédibilité
def buhlmann_straub(freq, poids):
    """Crédibilité de Bühlmann-Straub. `freq` : (groupes × périodes) des fréquences observées (NaN autorisé), `poids` : expositions.
    Renvoie dict (mu, s2 = E[variance de processus], a = variance des moyennes de groupes, k = s2/a, Z par groupe)."""
    F = np.asarray(freq, float); W = np.asarray(poids, float)
    W = np.where(np.isnan(F), 0, W); F = np.where(np.isnan(F), 0, F)
    wi = W.sum(axis=1); w = wi.sum()
    xi = (W * F).sum(axis=1) / np.maximum(wi, 1e-12)
    mu = (wi * xi).sum() / w
    r, T = F.shape
    n_obs = (W > 0).sum(axis=1)
    s2 = np.sum(W * (F - xi[:, None]) ** 2) / np.sum(np.maximum(n_obs - 1, 0))
    c = w - np.sum(wi ** 2) / w
    a = max((np.sum(wi * (xi - mu) ** 2) - (r - 1) * s2) / c, 1e-12)
    k = s2 / a
    Z = wi / (wi + k)
    return {"mu": float(mu), "s2": float(s2), "a": float(a), "k": float(k), "Z": Z, "xi": xi, "wi": wi}
