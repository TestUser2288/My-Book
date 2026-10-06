"""Outils du chapitre 5 (assurance vie) : tables de mortalité, Gompertz–Makeham, valeurs actuarielles, Lee–Carter.
Partagé par le livre (blocs cachés ou courts appels) et le cahier. Écrit en numpy/scipy : aucune bibliothèque actuarielle n'est installée."""
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

DONNEES = os.environ.get("DONNEES", "donnees")
AGES = np.arange(100)
ANNEES = np.arange(1980, 2020)


def charger():
    """population (m, expositions, décès par âge × année et sexe), vérité, portefeuille"""
    d = pd.read_csv(os.path.join(DONNEES, "mortalite_population.csv"))
    d["m"] = d["deces"] / d["exposition"]
    return d


def surface(d, sexe, col="m"):
    """matrice âges (lignes) × années (colonnes)"""
    return d[d["sexe"] == sexe].pivot(index="age", columns="annee", values=col)


def verite():
    v = pd.read_csv(os.path.join(DONNEES, "mortalite_verite.csv"))
    kt = pd.read_csv(os.path.join(DONNEES, "mortalite_kt_vrai.csv")).set_index("annee")
    ax = {s: v[v["sexe"] == s].set_index("age")["ax"].to_numpy() for s in "FM"}
    bx = v[v["sexe"] == "F"].set_index("age")["bx"].to_numpy()
    return ax, bx, kt


def m_vrai(sexe, annee):
    """taux centraux vrais de l'année (vérité programmée)"""
    ax, bx, kt = verite()
    return np.exp(ax[sexe] + bx * kt.loc[annee, "kt_" + sexe])


def q_depuis_m(m):
    """probabilité de décès dans l'année, force de mortalité constante dans l'année : q = 1 − exp(−m)"""
    return 1.0 - np.exp(-np.asarray(m, float))


def table_vie(q, radix=100000.0):
    """table à partir des q_x (âges 0..ω−1, q_ω−1 = 1 recommandé) : l_x, d_x, L_x (années vécues dans [x, x+1[) et e_x"""
    q = np.asarray(q, float)
    l = np.concatenate([[radix], radix * np.cumprod(1 - q)])
    dx = l[:-1] - l[1:]
    L = (l[:-1] + l[1:]) / 2
    e = np.cumsum(L[::-1])[::-1] / l[:-1]
    return pd.DataFrame({"age": np.arange(len(q)), "q": q, "l": l[:-1], "d": dx, "L": L, "e": e})


# ---------------------------------------------------------------- Gompertz–Makeham : μ(x) = A + B exp(c·x)
def gm_mu(x, p):
    A, B, c = np.exp(p[0]), np.exp(p[1]), np.exp(p[2])      # paramètres positifs : on optimise leurs logarithmes
    return A + B * np.exp(c * np.asarray(x, float))


def gm_ajuste(ages, deces, expo, p0=(-8.0, -10.0, -2.3)):
    """maximum de vraisemblance poissonien : D_x ~ Poisson(E_x · m_x), m_x = intégrale de μ sur [x, x+1[ ≈ μ(x+½)"""
    ages = np.asarray(ages, float)

    def nll(p):
        m = gm_mu(ages + 0.5, p)
        return float(np.sum(expo * m - deces * np.log(m)))
    r = minimize(nll, np.asarray(p0), method="Nelder-Mead", options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 4000})
    return r.x


def prolonge(q, p_gm, omega=120, depuis=95):
    """prolonge une table de q_x au-delà de 99 ans avec Gompertz–Makeham (ajusté sur les vieux âges) ; q_{ω−1} = 1"""
    q = list(np.asarray(q, float)[:depuis + 5])
    for x in range(len(q), omega):
        q.append(float(q_depuis_m(gm_mu(x + 0.5, p_gm))))
    q = np.minimum(np.array(q), 1.0)
    q[-1] = 1.0
    return q


# ---------------------------------------------------------------- portefeuille : une ligne par contrat-année
def lignes_police_annee(pv):
    """Reconstruit, pour chaque contrat, les années de la fenêtre 2015–2019 où il est en vigueur.
    exposition_2015_2019 = nombre d'années complètes avant le décès + 0,5 l'année du décès : le rang de l'année du décès s'en déduit."""
    lignes = []
    for r in pv.itertuples(index=False):
        debut = max(r.annee_emission, 2015)
        n = max(0, min(5, 2019 - debut + 1))
        if r.deces == 1:
            n = int(round(r.exposition_2015_2019 - 0.5)) + 1
        for j in range(n):
            an = debut + j
            dernier = (r.deces == 1 and j == n - 1)
            lignes.append((r.id_contrat, r.sexe, r.contrat, r.capital, an, r.age_emission + (an - r.annee_emission),
                           0.5 if dernier else 1.0, 1 if dernier else 0))
    return pd.DataFrame(lignes, columns=["id_contrat", "sexe", "contrat", "capital", "annee", "age", "expo", "deces"])


def ae_ic(deces, attendu, niveau=0.95):
    """rapport réel/attendu et intervalle exact de Poisson (Garwood) pour le nombre de décès, `attendu` supposé connu"""
    from scipy.stats import chi2
    a = (1 - niveau) / 2
    bas = chi2.ppf(a, 2 * deces) / 2 if deces > 0 else 0.0
    haut = chi2.ppf(1 - a, 2 * (deces + 1)) / 2
    return deces / attendu, bas / attendu, haut / attendu


# ---------------------------------------------------------------- mathématiques actuarielles
def valeurs(q, i, debut=0):
    """récurrences à rebours : A_x (capital 1 payé à la fin de l'année du décès), ä_x (rente 1 payée d'avance tant que l'assuré vit).
    q : vecteur q_x de l'âge 0 à ω−1 (dernier q = 1). Renvoie (A, a)."""
    q = np.asarray(q, float)
    v = 1.0 / (1.0 + i)
    n = len(q)
    A = np.zeros(n + 1)
    a = np.zeros(n + 1)
    for x in range(n - 1, -1, -1):
        A[x] = v * q[x] + v * (1 - q[x]) * A[x + 1]
        a[x] = 1.0 + v * (1 - q[x]) * a[x + 1]
    return A[:-1], a[:-1]


def temporaire(q, i, x, n):
    """A^1_{x:n} (capital 1 si décès avant x+n) et ä_{x:n} (rente temporaire d'avance), par récurrence sur n années"""
    v = 1.0 / (1.0 + i)
    A, a = 0.0, 0.0
    for k in range(n - 1, -1, -1):
        A = v * q[x + k] + v * (1 - q[x + k]) * A
        a = 1.0 + v * (1 - q[x + k]) * a
    return A, a


def reserve_prospective(q, i, x, n, capital, prime, t):
    """provision mathématique d'une temporaire n ans, à l'instant t (début d'année t, prime t déjà payée) :  tV = capital·A^1_{x+t:n−t} − prime·ä_{x+t:n−t}"""
    A, a = temporaire(q, i, x + t, n - t)
    return capital * A - prime * a


# ---------------------------------------------------------------- Lee–Carter
def lc_ajuste(M):
    """M : matrice des taux centraux (âges × années). ln m = a_x + b_x k_t ; contraintes Σ b_x = 1, Σ k_t = 0. Ajustement par SVD."""
    L = np.log(M.to_numpy())
    ax = L.mean(axis=1)
    U, S, Vt = np.linalg.svd(L - ax[:, None], full_matrices=False)
    b, k = U[:, 0], S[0] * Vt[0]
    s = b.sum()
    b, k = b / s, k * s
    return ax, b, k, S


def lc_recale(ax, bx, kt, deces, expo):
    """étape 2 de Lee–Carter : on ré-estime k_t pour que les décès prédits égalent les décès observés (année par année)"""
    from scipy.optimize import brentq
    kt2 = kt.copy()
    for t in range(len(kt)):
        f = lambda k: np.sum(expo[:, t] * np.exp(ax + bx * k)) - deces[:, t].sum()
        kt2[t] = brentq(f, kt[t] - 20, kt[t] + 20)
    return kt2


def derive_sigma(kt):
    """marche aléatoire avec dérive : k_{t+1} = k_t + δ + σ ε ; δ = (k_T − k_1)/(T−1), σ = écart-type des accroissements"""
    dk = np.diff(kt)
    return (kt[-1] - kt[0]) / (len(kt) - 1), dk.std(ddof=1)


def lc_projette(ax, bx, kt, horizon, n_sim, delta, sigma, rng):
    """simule n_sim trajectoires de k_t sur `horizon` années ; renvoie les k futurs (n_sim × horizon)"""
    eps = rng.normal(0, sigma, (n_sim, horizon))
    return kt[-1] + np.cumsum(delta + eps, axis=1)
