"""Outils du chapitre 3 (mesures de risque, stress tests) : appelés depuis des blocs cachés du livre et du cahier.

Contenu : chargement des rendements, VaR/ES (normale, historique, Monte-Carlo, EWMA, GARCH filtré), tests de Kupiec et de Christoffersen,
feu tricolore binomial, évaluation d'obligations sur une courbe de taux, perte agrégée d'un modèle fréquence-sévérité.
Tout est déterministe (graines passées en argument).
"""
import os

import numpy as np
import pandas as pd
from scipy import stats

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.environ.get("DONNEES") or os.path.join(RACINE, "donnees")
ACTIFS = ["actions_A", "actions_B", "obligations", "immobilier", "matieres"]
POIDS = np.array([0.35, 0.15, 0.30, 0.10, 0.10])     # portefeuille d'exemple (somme 1)
VALEUR = 100.0                                         # millions d'euros


def num(cle, valeur, fmt=".2f"):
    """imprime « NUM clé valeur » : les gabarits de la prose ({{clé}}) lisent ces lignes (voir build/gabarits/ch03)."""
    texte = format(valeur, fmt)
    if "," in fmt:
        texte = texte.replace(",", " ")
    print(f"NUM {cle} {texte}")


def charger_marche():
    """(rendements, régimes) ; rendements indexés par date, régimes alignés."""
    r = pd.read_csv(os.path.join(DONNEES, "rendements_marche.csv"), parse_dates=["date"]).set_index("date")
    v = pd.read_csv(os.path.join(DONNEES, "marche_verite.csv"), parse_dates=["date"]).set_index("date")
    return r, v["regime"]


def pertes_portefeuille(r, poids=POIDS, valeur=VALEUR):
    """perte journalière (M€, positive = perte) d'un portefeuille à poids constants."""
    return -(r[ACTIFS].values @ poids) * valeur


# ----------------------------------------------------------------------------- VaR et ES sur un échantillon de pertes
def var_hist(pertes, alpha=0.99):
    """quantile empirique de niveau alpha de la perte (définition : plus petit x tel que F(x) >= alpha)."""
    p = np.sort(np.asarray(pertes))
    k = int(np.ceil(alpha * len(p))) - 1
    return float(p[k])


def es_hist(pertes, alpha=0.99):
    """moyenne des pertes au-delà de la VaR (au sens large : pertes >= VaR)."""
    p = np.asarray(pertes)
    v = var_hist(p, alpha)
    return float(p[p >= v].mean())


def var_normale(mu, sigma, alpha=0.99):
    """perte ~ N(mu, sigma^2) : VaR = mu + sigma z_alpha."""
    return float(mu + sigma * stats.norm.ppf(alpha))


def es_normale(mu, sigma, alpha=0.99):
    """ES d'une loi normale : mu + sigma phi(z_alpha)/(1-alpha)."""
    z = stats.norm.ppf(alpha)
    return float(mu + sigma * stats.norm.pdf(z) / (1 - alpha))


def var_student(mu, sigma, nu, alpha=0.99):
    """perte de loi de Student (échelle réduite à l'écart-type sigma) : VaR."""
    t = stats.t.ppf(alpha, nu) * np.sqrt((nu - 2) / nu)
    return float(mu + sigma * t)


def es_student(mu, sigma, nu, alpha=0.99):
    """ES d'une Student standardisée à variance 1 : formule fermée."""
    q = stats.t.ppf(alpha, nu)
    es = stats.t.pdf(q, nu) / (1 - alpha) * (nu + q * q) / (nu - 1)
    return float(mu + sigma * es * np.sqrt((nu - 2) / nu))


def var_ewma(pertes, alpha=0.99, lam=0.94):
    """VaR à un jour par EWMA de la variance (moyenne supposée nulle), loi normale ; renvoie la série sigma_t pour t+1."""
    p = np.asarray(pertes)
    s2 = np.empty(len(p) + 1)
    s2[0] = p[:50].var()
    for t in range(len(p)):
        s2[t + 1] = lam * s2[t] + (1 - lam) * p[t] ** 2
    return np.sqrt(s2[1:])


def garch_filtre(pertes_apprentissage, pertes_test):
    """Ajuste un GARCH(1,1) à innovations t sur l'apprentissage, puis FILTRE la volatilité sur le test (paramètres figés).

    Renvoie (sigma_prevue, nu, params) ; sigma_prevue[i] est la volatilité prévue pour le jour i du test, connue à la fin du jour i-1.
    """
    from arch import arch_model

    a = np.asarray(pertes_apprentissage) * 1.0
    am = arch_model(a, mean="Zero", vol="GARCH", p=1, q=1, dist="t", rescale=False)
    res = am.fit(disp="off")
    om, al, be = res.params["omega"], res.params["alpha[1]"], res.params["beta[1]"]
    nu = float(res.params["nu"])
    h = float(res.conditional_volatility[-1] ** 2)
    x_prev = a[-1]
    h = om + al * x_prev ** 2 + be * h
    t_ = np.asarray(pertes_test)
    out = np.empty(len(t_))
    for i in range(len(t_)):
        out[i] = np.sqrt(h)
        h = om + al * t_[i] ** 2 + be * h
    return out, nu, (om, al, be)


# ----------------------------------------------------------------------------- backtests
def kupiec(n_exc, n, p):
    """test du rapport de vraisemblance de Kupiec (proportion de dépassements) : (statistique, p-value)."""
    x = n_exc
    if x == 0:
        lr = -2 * n * np.log(1 - p)
    elif x == n:
        lr = -2 * n * np.log(p)
    else:
        pi = x / n
        lr = -2 * ((n - x) * np.log(1 - p) + x * np.log(p) - (n - x) * np.log(1 - pi) - x * np.log(pi))
    return float(lr), float(1 - stats.chi2.cdf(lr, 1))


def christoffersen_ind(exc):
    """test d'indépendance de Christoffersen sur une série 0/1 de dépassements : (statistique, p-value)."""
    e = np.asarray(exc).astype(int)
    a, b = e[:-1], e[1:]
    n00 = int(((a == 0) & (b == 0)).sum()); n01 = int(((a == 0) & (b == 1)).sum())
    n10 = int(((a == 1) & (b == 0)).sum()); n11 = int(((a == 1) & (b == 1)).sum())
    pi01 = n01 / max(n00 + n01, 1); pi11 = n11 / max(n10 + n11, 1); pi = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)

    def ll(pr, k1, k0):
        out = 0.0
        if k1 > 0:
            out += k1 * np.log(pr)
        if k0 > 0:
            out += k0 * np.log(1 - pr)
        return out
    l0 = ll(pi, n01 + n11, n00 + n10)
    l1 = ll(pi01, n01, n00) + ll(pi11, n11, n10)
    lr = -2 * (l0 - l1)
    return float(lr), float(1 - stats.chi2.cdf(lr, 1))


def zones_tricolores(n=250, p=0.01):
    """binomiale B(n, p) : probabilité cumulée et zone (convention de seuils : vert si cumul < 95 %, orange si < 99,99 %, rouge sinon)."""
    k = np.arange(0, 16)
    cum = stats.binom.cdf(k, n, p)
    zone = np.where(cum < 0.95, "verte", np.where(cum < 0.9999, "orange", "rouge"))
    return pd.DataFrame({"depassements": k, "proba_cumulee": cum, "zone": zone})


# ----------------------------------------------------------------------------- obligations et courbe de taux
MATS = np.array([0.25, 1, 2, 3, 5, 7, 10, 20, 30])


def courbe_a(mois, courbe=None):
    """taux zéro-coupon (continus approchés par annuels) interpolés linéairement sur les maturités du fichier, pour un mois donné."""
    if courbe is None:
        courbe = pd.read_csv(os.path.join(DONNEES, "courbe_taux.csv"))
    ligne = courbe[courbe["mois"] == mois].iloc[0, 1:].values.astype(float)
    return lambda t: np.interp(t, MATS, ligne)


def prix_obligation(coupon, maturite, taux_fn, nominal=100.0, choc=lambda t: 0.0):
    """prix d'une obligation à coupons annuels, actualisée sur la courbe zéro (annuelle) + choc(t)."""
    t = np.arange(1, maturite + 1, dtype=float)
    flux = np.full(len(t), coupon * nominal)
    flux[-1] += nominal
    d = (1 + np.array([taux_fn(x) + choc(x) for x in t])) ** (-t)
    return float((flux * d).sum())


# ----------------------------------------------------------------------------- perte agrégée (fréquence-sévérité)
def perte_agregee_mc(lam, tirer_severite, n_sim=2000, seed=0):
    """simule n_sim années : N ~ Poisson(lam), somme de N sévérités tirées par `tirer_severite(rng, n)` (tirage groupé, rapide)."""
    rng = np.random.default_rng(seed)
    nn = rng.poisson(lam, n_sim)
    sev = tirer_severite(rng, int(nn.sum()))
    idx = np.repeat(np.arange(n_sim), nn)
    return np.bincount(idx, weights=sev, minlength=n_sim)


# ----------------------------------------------------------------------------- distribution des pertes opérationnelles (LDA)
def ajuster_lda(x, seuil=100000.0):
    """corps : lognormale tronquée au seuil (paramètres de ln x sur le corps) ; queue : Pareto généralisée sur les excès.
    Renvoie (mu, sigma, xi, echelle, proba_queue)."""
    x = np.asarray(x, float)
    corps = x[x <= seuil]
    exces = x[x > seuil] - seuil
    xi, _, sc = stats.genpareto.fit(exces, floc=0)
    return float(np.log(corps).mean()), float(np.log(corps).std()), float(xi), float(sc), len(exces) / len(x)


def tirer_lda(rng, k, par, seuil=100000.0, plafond=None):
    """tire k pertes du modèle ajusté ; `plafond` limite chaque perte (hypothèse de perte maximale plausible)."""
    mu, sg, xi, sc, pq = par
    queue = rng.random(k) < pq
    haut = stats.norm.cdf((np.log(seuil) - mu) / sg)
    corps = np.exp(mu + sg * stats.norm.ppf(rng.random(k) * haut))      # lognormale tronquée au seuil (inversion)
    g = seuil + sc / xi * ((1 - rng.random(k)) ** (-xi) - 1)
    out = np.where(queue, g, corps)
    return np.minimum(out, plafond) if plafond else out


def contributions_euler(r_actifs, poids=POIDS):
    """contributions de chaque actif à l'écart-type du portefeuille (en part du total, somme 1)."""
    S = np.cov(np.asarray(r_actifs).T)
    sp = np.sqrt(poids @ S @ poids)
    return poids * (S @ poids) / sp ** 2


# ----------------------------------------------------------------------------- backtest glissant de quatre méthodes
def var_glissantes(L, debut=1000, alpha=0.99, fenetre=500, pas_garch=250, fenetre_garch=1000):
    """VaR à un jour prévues pour les jours debut..fin-1 par quatre méthodes ; renvoie (dict nom -> (var, es))."""
    L = np.asarray(L)
    n = len(L) - debut
    z = stats.norm.ppf(alpha)
    out = {}
    h = np.array([var_hist(L[t - fenetre:t], alpha) for t in range(debut, len(L))])
    eh = np.array([es_hist(L[t - fenetre:t], alpha) for t in range(debut, len(L))])
    out["historique"] = (h, eh)
    mu_sd = [(L[t - fenetre:t].mean(), L[t - fenetre:t].std()) for t in range(debut, len(L))]
    out["normale"] = (np.array([var_normale(m, s, alpha) for m, s in mu_sd]), np.array([es_normale(m, s, alpha) for m, s in mu_sd]))
    ew = var_ewma(L)
    sig = np.array([ew[t - 1] for t in range(debut, len(L))])
    out["EWMA"] = (z * sig, sig * stats.norm.pdf(z) / (1 - alpha))
    gv, ge = np.empty(n), np.empty(n)
    for s in range(0, n, pas_garch):
        a = L[debut + s - fenetre_garch:debut + s]
        b = L[debut + s:debut + min(s + pas_garch, n)]
        sg, nu, _ = garch_filtre(a, b)
        gv[s:s + len(b)] = [var_student(0, x, nu, alpha) for x in sg]
        ge[s:s + len(b)] = [es_student(0, x, nu, alpha) for x in sg]
    out["GARCH-Student"] = (gv, ge)
    return out


def perte_quantile(L, v, alpha=0.99):
    """perte d'étalonnage (pinball) moyenne d'une prévision de quantile : plus c'est petit, mieux c'est."""
    u = np.asarray(L) - np.asarray(v)
    return float(np.mean(u * (alpha - (u < 0))))
