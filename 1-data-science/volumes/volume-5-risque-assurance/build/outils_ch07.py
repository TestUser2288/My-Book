"""Outils du chapitre 7 (actif-passif et portefeuille) : partagés par le livre (blocs cachés) et le cahier.

Tout est écrit à la main (numpy / pandas / scipy) : table de mortalité, flux d'un passif de contrats vie, courbe des taux
interpolée, valeur actuelle, duration, convexité, revalorisation complète, frontière efficiente, contributions au risque.
Les données sont SIMULÉES (voir build/donnees5.py)."""
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

DONNEES = os.environ.get("DONNEES", "donnees")
H = 45                                   # horizon maximal des flux du passif (années)
MATS_COURBE = np.array([0.25, 1, 2, 3, 5, 7, 10, 20, 30])


def charger():
    """(courbe, rendements, régimes, portefeuille vie, mortalité population)"""
    c = pd.read_csv(os.path.join(DONNEES, "courbe_taux.csv"))
    r = pd.read_csv(os.path.join(DONNEES, "rendements_marche.csv"), parse_dates=["date"]).set_index("date")
    v = pd.read_csv(os.path.join(DONNEES, "marche_verite.csv"), parse_dates=["date"]).set_index("date")["regime"]
    pv = pd.read_csv(os.path.join(DONNEES, "portefeuille_vie.csv"))
    mo = pd.read_csv(os.path.join(DONNEES, "mortalite_population.csv"))
    return c, r, v, pv, mo


# ------------------------------------------------------------------------------------------------ taux et valeurs actuelles
def taux_annuels(ligne_courbe, h=H):
    """taux zéro-coupon aux maturités 1..h (interpolation linéaire, plat au-delà de 30 ans) ; `ligne_courbe` : 9 taux."""
    t = np.arange(1, h + 1)
    return np.interp(t, MATS_COURBE, np.asarray(ligne_courbe, float))


def facteurs(taux):
    """facteurs d'actualisation (1+y_t)^-t pour t = 1..len(taux)"""
    t = np.arange(1, len(taux) + 1)
    return (1.0 + taux) ** (-t)


def vp(flux, taux):
    return float((np.asarray(flux) * facteurs(taux)).sum())


def duration_macaulay(flux, taux):
    t = np.arange(1, len(flux) + 1)
    pv = np.asarray(flux) * facteurs(taux)
    return float((t * pv).sum() / pv.sum())


def duration_modifiee(flux, taux):
    """sensibilité à un déplacement parallèle des taux (composition annuelle) : -dP/dy / P, en tirant la formule à la main
    pour un taux unique y ; ici la courbe est déplacée d'un même dy, d'où la formule générale ci-dessous"""
    t = np.arange(1, len(flux) + 1)
    pv = np.asarray(flux) * facteurs(taux)
    return float((t * pv / (1.0 + taux)).sum() / pv.sum())


def convexite(flux, taux):
    t = np.arange(1, len(flux) + 1)
    pv = np.asarray(flux) * facteurs(taux)
    return float((t * (t + 1) * pv / (1.0 + taux) ** 2).sum() / pv.sum())


def choc_parallele(taux, dy):
    return np.asarray(taux) + dy


def choc_pente(taux, dy_court, dy_long, pivot=10.0):
    """déplacement linéaire en l'échéance : dy_court à 1 an, dy_long à `pivot` ans et au-delà"""
    t = np.arange(1, len(taux) + 1)
    w = np.clip((t - 1) / (pivot - 1), 0, 1)
    return np.asarray(taux) + dy_court + (dy_long - dy_court) * w


# ------------------------------------------------------------------------------------------------ table de mortalité et passif vie
def table_mortalite(mo, annees=range(2015, 2020)):
    """q_x par sexe, calculée sur les années données (décès cumulés / expositions cumulées) : m = décès / exposition (taux central),
    q = 1 - exp(-m). Colonnes F, M ; index = âge."""
    d = mo[mo["annee"].isin(list(annees))].groupby(["sexe", "age"])[["deces", "exposition"]].sum()
    out = {}
    for s in ("F", "M"):
        e = d.loc[s]
        m = (e["deces"] / e["exposition"]).clip(upper=0.9)
        out[s] = 1.0 - np.exp(-m)
    return pd.DataFrame(out)


def rapport_ae(pv, qtab):
    """rapport décès observés / décès attendus du portefeuille : mortalité de la table appliquée à l'âge atteint à mi-fenêtre
    (2017), pondérée par l'exposition 2015–2019 (approximation ; le chapitre 5 en donne une version plus fine)."""
    age_mid = np.clip(pv["age_emission"] + (2017 - pv["annee_emission"]).clip(lower=0), 0, 99)
    q = np.array([qtab.loc[a, s] for a, s in zip(age_mid, pv["sexe"])])
    return float(pv["deces"].sum() / (q * pv["exposition_2015_2019"]).sum())


def flux_passif(pv, qtab, ratio, valuation=2020, h=H):
    """flux attendus de décès (prestations versées en fin d'année) des contrats en vigueur au 1er janvier 2020
    (ceux sans décès en 2015–2019, non échus). Mortalité = ratio × table (qx, sans amélioration future : hypothèse prudente simple).
    Retourne (flux[1..h] en €, nombre de contrats retenus)."""
    vivants = pv[pv["deces"] == 0]
    duree = vivants["contrat"].map({"temporaire_10": 10, "temporaire_20": 20, "vie_entiere": 200})
    restant = duree - (valuation - vivants["annee_emission"])
    vivants = vivants[restant > 0]
    restant = restant[restant > 0]
    age0 = np.clip(vivants["age_emission"] + (valuation - vivants["annee_emission"]), 0, 99).to_numpy()
    sexe = vivants["sexe"].to_numpy()
    cap = vivants["capital"].to_numpy()
    rest = restant.to_numpy()
    flux = np.zeros(h)
    surv = np.ones(len(vivants))
    for t in range(1, h + 1):
        age = np.clip(age0 + t - 1, 0, 99).astype(int)
        q = np.where(sexe == "F", qtab["F"].to_numpy()[age], qtab["M"].to_numpy()[age])
        q = np.minimum(ratio * q, 1.0)
        actif = rest >= t
        flux[t - 1] = float((cap * surv * q * actif).sum())
        surv = surv * (1 - q)
    return flux, len(vivants)


# ------------------------------------------------------------------------------------------------ zéro-coupon, actifs
def vp_zc(m, y):
    return (1.0 + y) ** (-m)


def duration_zc(m, y):
    """duration modifiée d'un zéro-coupon de maturité m au taux y"""
    return m / (1.0 + y)


# ------------------------------------------------------------------------------------------------ portefeuille (Markowitz)
def stats_annuelles(R, jours=252):
    """rendement moyen et covariance annualisés (rendements simples journaliers)"""
    return R.mean().to_numpy() * jours, R.cov().to_numpy() * jours


def vol_ptf(w, S):
    return float(np.sqrt(w @ S @ w))


def min_variance(S, long_only=True):
    n = len(S)
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    res = minimize(lambda w: w @ S @ w, np.full(n, 1 / n), constraints=cons,
                   bounds=[(0, 1)] * n if long_only else None, method="SLSQP", options={"ftol": 1e-14, "maxiter": 500})
    return res.x


def frontiere(mu, S, cibles, long_only=True):
    """poids de variance minimale pour chaque rendement cible"""
    n = len(mu)
    W = []
    w0 = np.full(n, 1 / n)
    for c in cibles:
        cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}, {"type": "eq", "fun": lambda w, c=c: w @ mu - c}]
        res = minimize(lambda w: w @ S @ w, w0, constraints=cons, bounds=[(0, 1)] * n if long_only else None,
                       method="SLSQP", options={"ftol": 1e-14, "maxiter": 500})
        W.append(res.x)
        w0 = res.x
    return np.array(W)


def tangent(mu, S, rf, long_only=True):
    n = len(mu)
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    res = minimize(lambda w: -(w @ mu - rf) / np.sqrt(w @ S @ w), np.full(n, 1 / n), constraints=cons,
                   bounds=[(0, 1)] * n if long_only else None, method="SLSQP", options={"ftol": 1e-14, "maxiter": 500})
    return res.x


def contributions_risque(w, S):
    """contribution d'Euler de chaque actif à l'écart-type : w_i (Σw)_i / σ ; la somme vaut σ"""
    sig = np.sqrt(w @ S @ w)
    return w * (S @ w) / sig


# ------------------------------------------------------------------------------------------------ bilan jouet et simulations
class Bilan:
    """Bilan jouet d'un assureur vie au 1er janvier 2020 : passif = flux attendus des contrats en vigueur (valeur actuelle L0 sur la courbe
    du dernier mois), actif = (1 + surplus) × L0. Contient aussi les variations mensuelles de la courbe et les rendements du marché."""

    def __init__(self, surplus=0.10):
        c, r, regimes, pv, mo = charger()
        self.qtab = table_mortalite(mo)
        self.ae = rapport_ae(pv, self.qtab)
        self.flux, self.nb_contrats = flux_passif(pv, self.qtab, self.ae)
        self.courbe = c.iloc[:, 1:].to_numpy()                       # 120 × 9
        self.c0 = self.courbe[-1].copy()                              # courbe du dernier mois
        self.y0 = taux_annuels(self.c0)
        self.dC = np.diff(self.courbe, axis=0)                        # 119 variations mensuelles
        self.L0 = vp(self.flux, self.y0)
        self.A0 = (1 + surplus) * self.L0
        self.DL = duration_modifiee(self.flux, self.y0)
        self.R = r.to_numpy()
        self.cum = np.vstack([np.zeros(5), np.cumsum(np.log1p(self.R), axis=0)])
        self.T = len(self.R)

    def duree_appariee(self):
        """duration modifiée que doit avoir l'actif pour que les sensibilités en € soient égales : D_A = D_L · L / A"""
        return self.DL * self.L0 / self.A0

    def poids_zc(self, mats=(10, 20), duree_cible=None):
        """poids de deux zéros-coupons (maturités `mats`) qui donnent la duration modifiée cible"""
        d = self.duree_appariee() if duree_cible is None else duree_cible
        d1, d2 = duration_zc(mats[0], self.y0[mats[0] - 1]), duration_zc(mats[1], self.y0[mats[1] - 1])
        w2 = (d - d1) / (d2 - d1)
        return {mats[0]: 1 - w2, mats[1]: w2}


def rendement_zc(m, y_avant, y_apres):
    """rendement sur un an d'un zéro-coupon à maturité constante : acheté à la maturité m, revalorisé un an plus tard à la maturité m-1
    (la courbe 'inchangée' signifie que chaque taux au comptant est inchangé : le roulement le long de la courbe est inclus)"""
    return (1 + y_apres[m - 2]) ** (-(m - 1)) / (1 + y_avant[m - 1]) ** (-m) - 1


def rendement_actifs(w, y_avant, y_apres, r_actions, r_immo):
    """w : dict {maturité: poids, 'act': poids, 'imm': poids}"""
    out = 0.0
    for k, wk in w.items():
        if k == "act":
            out += wk * r_actions
        elif k == "imm":
            out += wk * r_immo
        else:
            out += wk * rendement_zc(k, y_avant, y_apres)
    return out


def tirages_annuels(b, N, seed):
    """N scénarios annuels : variation de la courbe (somme de 12 variations mensuelles tirées au hasard avec remise) et rendements
    annuels des actifs (fenêtre de 252 jours consécutifs tirée au hasard dans l'historique)."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(b.dC), (N, 12))
    dY = b.dC[idx].sum(axis=1)
    st = rng.integers(0, b.T - 252, N)
    ann = np.exp(b.cum[st + 252] - b.cum[st]) - 1
    return dY, ann


def variation_surplus_1an(b, w, dY, ann):
    """variation du surplus (A − L) sur un an, revalorisation COMPLÈTE : actif revalorisé, prestation de l'année payée, passif restant
    actualisé sur la courbe déplacée"""
    n = len(dY)
    out = np.zeros(n)
    S0 = b.A0 - b.L0
    for i in range(n):
        y1 = taux_annuels(np.maximum(b.c0 + dY[i], 0.0))
        rb = rendement_actifs(w, b.y0, y1, ann[i, :2].mean(), ann[i, 3])
        A1 = b.A0 * (1 + rb) - b.flux[0]
        L1 = vp(b.flux[1:], y1[: len(b.flux) - 1])
        out[i] = (A1 - L1) - S0
    return out


def simuler_alm(b, w, N=1000, annees=10, seed=11):
    """taux de couverture A_k / L_k à la fin de chaque année k = 0..annees, pour N trajectoires (courbe : marche aléatoire par bootstrap
    des variations mensuelles ; actifs : fenêtres annuelles de l'historique ; prestations déterministes)"""
    rng = np.random.default_rng(seed)
    FR = np.zeros((N, annees + 1))
    FR[:, 0] = b.A0 / b.L0
    for i in range(N):
        Ck = b.c0.copy()
        yk = b.y0.copy()
        A = b.A0
        for k in range(1, annees + 1):
            Cn = np.maximum(Ck + b.dC[rng.integers(0, len(b.dC), 12)].sum(axis=0), 0.0)
            yn = taux_annuels(Cn)
            s = rng.integers(0, b.T - 252)
            a = np.exp(b.cum[s + 252] - b.cum[s]) - 1
            rb = rendement_actifs(w, yk, yn, a[:2].mean(), a[3])
            A = A * (1 + rb) - b.flux[k - 1]
            Lk = vp(b.flux[k:], yn[: len(b.flux) - k])
            FR[i, k] = A / Lk
            Ck, yk = Cn, yn
    return FR


# ------------------------------------------------------------------------------------------------ univers simulé pour le rétrécissement
def univers_facteurs(n, seed=0, k=3):
    """covariance VRAIE d'un univers de n actifs à k facteurs (annualisée) : Σ = B Bᵀ + D"""
    rng = np.random.default_rng(seed)
    B = rng.normal(0.0, 0.10, (n, k)) + 0.10 * (np.arange(k) == 0)
    D = np.diag(rng.uniform(0.01, 0.04, n) ** 2 * 4)
    return B @ B.T + D


def experience_retrecissement(n=60, T=120, reps=100, seed=1):
    """volatilité VRAIE (calculée avec la vraie covariance) des portefeuilles de variance minimale sans contrainte construits avec la covariance
    empirique, la covariance rétrécie (Ledoit–Wolf) et les poids égaux ; moyenne sur `reps` échantillons de T observations."""
    from sklearn.covariance import LedoitWolf
    Sig = univers_facteurs(n, seed=seed)
    rng = np.random.default_rng(seed + 100)
    L = np.linalg.cholesky(Sig / 252)
    un = np.ones(n)
    def mv(S):
        x = np.linalg.solve(S, un)
        return x / x.sum()
    res = []
    for _ in range(reps):
        X = rng.normal(size=(T, n)) @ L.T
        w_emp = mv(np.cov(X.T))
        w_lw = mv(LedoitWolf().fit(X).covariance_)
        res.append([np.sqrt(w @ Sig @ w) for w in (w_emp, w_lw, un / n, mv(Sig))])
    return np.array(res).mean(axis=0)            # empirique, Ledoit–Wolf, égaux, optimum vrai


# ------------------------------------------------------------------------------------------------ surplus : instruments et optimisation
INSTR = [5, 10, 20, 30, "act", "imm"]
NOMS_INSTR = ["ZC 5 ans", "ZC 10 ans", "ZC 20 ans", "ZC 30 ans", "actions", "immobilier"]


def pnl_instruments(b, dY, ann):
    """gains en € sur un an de chaque instrument pour une unité de poids (soit A0 × rendement), matrice N × 6, et variation nette du passif
    (L1 − L0 + prestation de l'année), vecteur N. La variation du surplus d'une allocation w est X @ w − dliab."""
    n = len(dY)
    X = np.zeros((n, len(INSTR)))
    dl = np.zeros(n)
    for i in range(n):
        y1 = taux_annuels(np.maximum(b.c0 + dY[i], 0.0))
        for j, k in enumerate(INSTR):
            if k == "act":
                X[i, j] = b.A0 * ann[i, :2].mean()
            elif k == "imm":
                X[i, j] = b.A0 * ann[i, 3]
            else:
                X[i, j] = b.A0 * rendement_zc(k, b.y0, y1)
        dl[i] = vp(b.flux[1:], y1[: len(b.flux) - 1]) - b.L0 + b.flux[0]
    return X, dl


def poids_vecteur(w):
    """dict {5: .., 'act': ..} -> vecteur dans l'ordre INSTR"""
    return np.array([w.get(k, 0.0) for k in INSTR], float)


def surplus_min_variance(X, dl, long_only=True):
    """allocation de variance minimale du SURPLUS (somme des poids = 1)"""
    Z = (X - X.mean(axis=0)) / 1e6                     # calculs en M€ (conditionnement de l'optimiseur)
    Zl = (dl - dl.mean()) / 1e6
    n = X.shape[1]
    def f(w):
        r = Z @ w - Zl
        return float(r @ r) / len(r)
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    res = minimize(f, np.full(n, 1 / n), constraints=cons, bounds=[(0, 1)] * n if long_only else None, method="SLSQP",
                   options={"ftol": 1e-16, "maxiter": 500})
    return res.x


def surplus_frontiere(X, dl, budgets):
    """pour chaque budget d'écart-type du surplus (€), allocation de gain moyen maximal (somme des poids = 1, pas de vente à découvert)"""
    Z = (X - X.mean(axis=0)) / 1e6
    Zl = (dl - dl.mean()) / 1e6
    mX = X.mean(axis=0) / 1e6
    n = X.shape[1]
    out = []
    w0 = surplus_min_variance(X, dl)
    for sb in budgets:
        cons = [{"type": "eq", "fun": lambda w: w.sum() - 1},
                {"type": "ineq", "fun": lambda w, sb=sb: (sb / 1e6) ** 2 - float(((Z @ w - Zl) ** 2).mean())}]
        res = minimize(lambda w: -(mX @ w), w0, constraints=cons, bounds=[(0, 1)] * n, method="SLSQP",
                       options={"ftol": 1e-12, "maxiter": 500})
        out.append(res.x)
        w0 = res.x
    return np.array(out)


def var_es(dS, niveau_var=0.995, niveau_es=0.99):
    """VaR et ES (positives = pertes) de la variation du surplus"""
    var = -np.quantile(dS, 1 - niveau_var)
    seuil = np.quantile(dS, 1 - niveau_es)
    es = -dS[dS <= seuil].mean()
    return float(var), float(es)
