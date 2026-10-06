"""Outils du chapitre 1 (risque de crédit et scoring), partagés par le livre (blocs cachés) et le cahier.

Contenu : chargement et découpage de `credits_conso.csv`, classes (bornes choisies à la main), tables WOE/IV, grille de score en points,
indicateurs de performance (AUC, Gini, KS), PSI, matrices de transition par cohortes. Aucune dépendance vers d'autres chapitres.
"""
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

DONNEES = os.environ.get("DONNEES", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees"))

# ------------------------------------------------------------------------------------------- données
def charger_credits():
    """Retourne (apprentissage, test) : découpage 70/30 stratifié, graine fixe."""
    df = pd.read_csv(os.path.join(DONNEES, "credits_conso.csv"))
    return train_test_split(df, test_size=0.3, random_state=7, stratify=df["defaut_12m"])


# ------------------------------------------------------------------------------------------- classes
INF = np.inf
BORNES = {   # bornes inférieures incluses : [b0, b1[, [b1, b2[, ...
    "age": [-INF, 25, 30, 40, 55, 65, INF],
    "taux_endettement": [-INF, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, INF],
    "anciennete_emploi": [-INF, 1, 3, 6, 10, INF],
    "revenu_annuel": [-INF, 20000, 26000, 32000, 40000, 50000, INF],
    "montant": [-INF, 4000, 7000, 12000, 20000, INF],
    "duree_mois": [-INF, 24, 36, 48, 60, INF],
    "nb_incidents_12m": [-INF, 1, 2, INF],
    "anciennete_relation": [-INF, 1, 3, 6, 12, INF],
}
ETIQUETTES = {"nb_incidents_12m": ["1: 0", "2: 1", "3: 2+"]}      # classes d'une variable entière : libellés explicites
CATEGORIELLES = ["logement", "objet"]
VARIABLES = list(BORNES) + CATEGORIELLES


def classer(x, nom):
    """Étiquette de classe de chaque valeur ; « manquant » à part. Les étiquettes se trient dans l'ordre des bornes."""
    if nom in CATEGORIELLES:
        return x.astype(str)
    b = BORNES[nom]
    lab = []
    for i in range(len(b) - 1):
        if nom in ETIQUETTES:
            lab.append(ETIQUETTES[nom][i]); continue
        lo, hi = b[i], b[i + 1]
        lab.append(f"{i + 1}: <{hi:g}" if lo == -INF else (f"{i + 1}: {lo:g}+" if hi == INF else f"{i + 1}: {lo:g}-{hi:g}"))
    c = pd.cut(x, b, right=False, labels=lab).astype(object)
    return pd.Series(np.where(x.isna(), "manquant", c), index=x.index)


def table_woe(x, y, nom, lissage=0.5):
    """Table WOE/IV d'une variable : WOE = ln(%bons / %mauvais) (élevé = sûr), lissé de `lissage` observation par classe."""
    d = pd.DataFrame({"classe": classer(x, nom), "mauvais": y.values})
    t = d.groupby("classe").mauvais.agg(effectif="count", mauvais="sum")
    t["bons"] = t["effectif"] - t["mauvais"]
    pb = (t["bons"] + lissage) / (t["bons"].sum() + lissage * len(t))
    pm = (t["mauvais"] + lissage) / (t["mauvais"].sum() + lissage * len(t))
    t["taux_defaut"] = t["mauvais"] / t["effectif"]
    t["woe"] = np.log(pb / pm)
    t["iv"] = (pb - pm) * t["woe"]
    return t


def iv_partition(n, m, lissage=0.5):
    """IV d'une partition donnée par les effectifs n (total) et m (mauvais) de chaque classe."""
    n = np.asarray(n, float); m = np.asarray(m, float); b = n - m
    pb = (b + lissage) / (b.sum() + lissage * len(n)); pm = (m + lissage) / (m.sum() + lissage * len(n))
    return float(((pb - pm) * np.log(pb / pm)).sum())


def fusion_monotone(x, y, k=10, sens=-1):
    """Part de k classes d'effectifs égaux (quantiles de x, manquants exclus) et fusionne les classes voisines jusqu'à ce que le taux de défaut
    soit monotone (sens = -1 : décroissant quand x augmente ; +1 : croissant). À chaque pas, on fusionne la paire fautive qui fait perdre le moins d'IV.
    Retourne (bornes inférieures des classes, effectifs, mauvais)."""
    ok = x.notna().values
    xv = x.values[ok]; yv = np.asarray(y)[ok]
    q = np.unique(np.quantile(xv, np.linspace(0, 1, k + 1)[1:-1]))
    bornes = np.r_[-np.inf, q]
    idx = np.searchsorted(q, xv, side="right")
    n = np.bincount(idx, minlength=len(bornes)).astype(float)
    m = np.bincount(idx, weights=yv, minlength=len(bornes)).astype(float)
    while True:
        taux = m / n
        fautives = [i for i in range(len(n) - 1) if sens * (taux[i + 1] - taux[i]) < 0]
        if not fautives:
            break
        iv0 = iv_partition(n, m)
        pertes = []
        for i in fautives:
            n2 = np.r_[n[:i], n[i] + n[i + 1], n[i + 2:]]; m2 = np.r_[m[:i], m[i] + m[i + 1], m[i + 2:]]
            pertes.append(iv0 - iv_partition(n2, m2))
        i = fautives[int(np.argmin(pertes))]
        n = np.r_[n[:i], n[i] + n[i + 1], n[i + 2:]]; m = np.r_[m[:i], m[i] + m[i + 1], m[i + 2:]]
        bornes = np.r_[bornes[:i + 1], bornes[i + 2:]]
    return bornes, n, m


def tables_woe(tr, variables=None):
    return {v: table_woe(tr[v], tr["defaut_12m"], v) for v in (variables or VARIABLES)}


def vers_woe(df, tables, variables=None):
    """Remplace chaque variable par le WOE de sa classe (classe inconnue → 0)."""
    out = {}
    for v in (variables or list(tables)):
        out[v] = classer(df[v], v).map(tables[v]["woe"]).fillna(0.0)
    return pd.DataFrame(out, index=df.index)


class Grille:
    """Grille de score : régression logistique de « bon » sur les WOE, puis mise à l'échelle en points.

    points d'une classe j de la variable k : -(beta_k·WOE_jk + alpha/p)·facteur + decalage/p  (convention : score élevé = sûr)
    """

    def __init__(self, tr, variables=None, base=600, cotes_base=50, pdo=20, C=1.0):
        self.variables = variables or VARIABLES
        self.tables = tables_woe(tr, self.variables)
        W = vers_woe(tr, self.tables, self.variables)
        y_bon = 1 - tr["defaut_12m"].values
        self.lr = LogisticRegression(C=C, max_iter=2000).fit(W, y_bon)     # ln(bons/mauvais) = alpha + sum beta_k WOE_k
        self.facteur = pdo / np.log(2)
        self.decalage = base - self.facteur * np.log(cotes_base)
        self.alpha = float(self.lr.intercept_[0])
        self.beta = dict(zip(self.variables, self.lr.coef_[0]))
        self.p = len(self.variables)

    def points_classes(self):
        lignes = []
        for v in self.variables:
            for cl, r in self.tables[v].iterrows():
                pts = (self.beta[v] * r["woe"] + self.alpha / self.p) * self.facteur + self.decalage / self.p
                lignes.append((v, cl, int(r["effectif"]), round(float(r["taux_defaut"]), 4), round(float(r["woe"]), 3), round(float(pts), 1)))
        return pd.DataFrame(lignes, columns=["variable", "classe", "effectif", "taux_defaut", "woe", "points"])

    def log_cote(self, df):
        return self.alpha + vers_woe(df, self.tables, self.variables).values @ np.array([self.beta[v] for v in self.variables])

    def score(self, df):
        return self.decalage + self.facteur * self.log_cote(df)

    def pd_predite(self, df):
        return 1 / (1 + np.exp(self.log_cote(df)))


# ------------------------------------------------------------------------------------------- mesures
def auc(y, s):
    """AUC pour un score où une valeur ÉLEVÉE signale un RISQUE élevé (y = 1 : défaut)."""
    return roc_auc_score(y, s)


def gini(y, s):
    return 2 * roc_auc_score(y, s) - 1


def ks(y, s):
    """Écart maximal entre les fonctions de répartition des scores de risque des mauvais et des bons."""
    y = np.asarray(y); s = np.asarray(s)
    o = np.argsort(s)
    y = y[o]
    cm = np.cumsum(y) / y.sum()
    cb = np.cumsum(1 - y) / (1 - y).sum()
    return float(np.max(np.abs(cm - cb)))


def bootstrap_auc(y, s, n=500, seed=0):
    """Intervalle de l'AUC à 95 % par rééchantillonnage des lignes."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y); s = np.asarray(s)
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        vals.append(roc_auc_score(y[i], s[i]))
    return np.percentile(vals, [2.5, 97.5])


def bootstrap_diff_auc(y, s1, s2, n=500, seed=0):
    """Différence d'AUC (s1 − s2) sur des rééchantillons APPARIÉS (mêmes lignes) : moyenne et intervalle à 95 %."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y); s1 = np.asarray(s1); s2 = np.asarray(s2)
    d = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        d.append(roc_auc_score(y[i], s1[i]) - roc_auc_score(y[i], s2[i]))
    return float(np.mean(d)), np.percentile(d, [2.5, 97.5])


def psi(attendu, observe, classes):
    """Indice de stabilité de population entre deux séries, sur des classes données (quantiles de `attendu`)."""
    b = np.unique(np.quantile(attendu, np.linspace(0, 1, classes + 1)))
    b[0], b[-1] = -np.inf, np.inf
    pa = np.histogram(attendu, b)[0] / len(attendu)
    po = np.histogram(observe, b)[0] / len(observe)
    pa, po = np.clip(pa, 1e-4, None), np.clip(po, 1e-4, None)
    return float(((po - pa) * np.log(po / pa)).sum())


# ------------------------------------------------------------------------------------------- migration
def compter_transitions(panel, annees=None):
    """Matrice 7×8 des effectifs de transitions (colonne 0 = sortie du portefeuille, retirée ensuite) à partir de `notations_panel.csv`."""
    p = panel if annees is None else panel[panel["annee"].isin(annees)]
    N = np.zeros((7, 9), dtype=int)
    for i, f in zip(p["note_debut"].values, p["note_fin"].values):
        N[i - 1, f] += 1
    return N          # colonnes : 0 = sorti, 1..8 = notes finales (8 = défaut)


def matrice_cohortes(N):
    """Estimation par cohortes : les sorties sont retirées du dénominateur (hypothèse : sortie non informative)."""
    M = N[:, 1:].astype(float)
    return M / M.sum(axis=1, keepdims=True)


# ------------------------------------------------------------------------------------------- IFRS 9 (règles d'exemple, ILLUSTRATIVES)
def etape_ifrs9(df, seuil_ratio=2.5, retard_2=30, retard_3=90):
    """Étape 3 : retard ≥ 90 jours (défaut) ; étape 2 : hausse sensible du risque (retard ≥ 30 jours, PD actuelle > 2,5 × PD d'origine, ou restructuration) ; sinon étape 1."""
    ratio = df["pd_actuelle"] / df["pd_origine"]
    st2 = (df["jours_retard"] >= retard_2) | (ratio > seuil_ratio) | (df["restructure"] == 1)
    return np.where(df["jours_retard"] >= retard_3, 3, np.where(st2, 2, 1))


def ecl_ifrs9(df, etapes, mult=1.0, annees_max=8):
    """Perte de crédit attendue par prêt. Étape 1 : PD à 12 mois × LGD × EAD, actualisée à mi-année au taux effectif.
    Étape 2 : somme sur la durée de vie (risque constant par an, EAD amortie linéairement, actualisation à mi-année). Étape 3 : LGD × EAD."""
    h = np.clip(df["pd_actuelle"].values * mult, 0, 0.999); lgd = df["lgd_estimee"].values; ead = df["ead"].values
    r = df["taux_effectif"].values; T = df["maturite_residuelle"].values
    un_an = h * lgd * ead / (1 + r) ** 0.5
    vie = np.zeros(len(df))
    for t in range(1, annees_max + 1):
        frac = np.clip(T - (t - 1), 0, 1)
        marg = (1 - h) ** (t - 1) * h * frac
        e_t = ead * np.clip(1 - (t - 0.5) / np.maximum(T, 0.5), 0, 1)
        vie += marg * lgd * e_t / (1 + r) ** (t - 0.5)
    return np.where(etapes == 1, un_an, np.where(etapes == 2, vie, lgd * ead))
