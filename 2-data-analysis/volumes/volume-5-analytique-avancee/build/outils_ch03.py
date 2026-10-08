"""Outils du chapitre 3 « Introduction à l'analytique prédictive » (série 2, volume V).

Tout est calculé ici pour que le livre ne montre que l'essentiel :
  charger(D)                 -> dictionnaire de tables (commandes enrichies, clients, retours par client, jours, série mensuelle)
  calendrier(dates)          -> variables CONNUES À L'AVANCE (mois, jour de semaine, promotion du calendrier annuel)
  prevoir_*                  -> les prévisions du cas A (commandes mensuelles) : naïve, saisonnière, saisonnière avec croissance, Holt-Winters, régression de Poisson
  origines(d)                -> évaluation par origine glissante (2025) à 1 et 3 mois
  instantane(d, coupure)     -> une ligne par client actif à la date de coupure : variables calculées AVANT la coupure + cible « rachat dans les 90 jours »
  VARS / modele_log / ...    -> les variables et les modèles du cas B
  auc_main / gain / calibration -> métriques écrites à la main (vérifiées contre scikit-learn)
Le code du livre appelle ces fonctions ; les figures sont dessinées par les fonctions fig_* (style commun build/style.py).
"""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------ chargement
FETES = [((1, 8), (1, 28)), ((6, 24), (7, 14)), ((11, 22), (11, 30))]     # calendrier promotionnel annuel de la boutique (soldes d'hiver, soldes d'été, Vendredi noir)


def charger(D):
    cmd = pd.read_csv(f"{D}/commandes.csv", parse_dates=["date_commande"])
    lig = pd.read_csv(f"{D}/lignes_commande.csv")
    prod = pd.read_csv(f"{D}/produits.csv")
    ret = pd.read_csv(f"{D}/retours.csv", parse_dates=["date_retour"])
    cli = pd.read_csv(f"{D}/clients.csv", parse_dates=["date_inscription"])
    j = pd.read_csv(f"{D}/jours_exploitation.csv", parse_dates=["date"])
    x = lig.merge(prod[["id_produit", "categorie", "cout_achat"]], on="id_produit")
    x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]                  # marge brute hors taxe (TVA fictive de 20 %)
    par = x.groupby("id_commande").agg(montant=("montant", "sum"), marge=("marge", "sum"), cats=("categorie", lambda s: frozenset(s)))
    cmd = cmd.merge(par, on="id_commande")
    rl = ret.merge(lig[["id_ligne", "id_commande"]], on="id_ligne").merge(cmd[["id_commande", "id_client"]], on="id_commande")
    j["mois"], j["dow"] = j["date"].dt.month, j["date"].dt.dayofweek
    j["t"] = np.arange(len(j)) / 365.25
    j["per"] = j["date"].dt.to_period("M")
    M = j.groupby("per")["nb_commandes"].sum()
    return {"cmd": cmd, "cli": cli, "rl": rl, "j": j, "M": M, "premiere": cmd.groupby("id_client")["date_commande"].min()}


def calendrier(dates):
    d = pd.DatetimeIndex(dates)
    promo = np.zeros(len(d), int)
    md = np.asarray(d.month) * 100 + np.asarray(d.day)
    for (m1, j1), (m2, j2) in FETES:
        promo |= ((md >= m1 * 100 + j1) & (md <= m2 * 100 + j2)).astype(int)
    return pd.DataFrame({"date": d, "mois": d.month, "dow": d.dayofweek, "promo_active": promo})


# ------------------------------------------------------------------ cas A : prévision mensuelle
def _glm(j_train):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    return smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", j_train, family=sm.families.Poisson()).fit()


def prevoir_naif(M, o, h=1):
    return float(M.iloc[o - 1])


def prevoir_saison(M, o, h=1):
    return float(M.iloc[o + h - 1 - 12])


def prevoir_saison_croissance(M, o, h=1):
    g = M.iloc[o - 12:o].sum() / M.iloc[o - 24:o - 12].sum()
    return float(M.iloc[o + h - 1 - 12] * g)


def prevoir_hw(M, o, h=1):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    m = ExponentialSmoothing(M.iloc[:o].astype(float).values, trend="add", seasonal="mul", seasonal_periods=12, damped_trend=True).fit()
    return float(m.forecast(h)[-1])


def prevoir_poisson(M, o, h, j):
    m = _glm(j[j["per"] < M.index[o]])
    return float(m.predict(j[j["per"] == M.index[o + h - 1]]).sum())


MODELES = {"naïf (mois précédent)": prevoir_naif, "saisonnier (même mois, an dernier)": prevoir_saison, "saisonnier × croissance": prevoir_saison_croissance,
           "Holt-Winters": prevoir_hw}


def origines(d, horizons=(1, 3), debut=24):
    """Origine glissante : à la fin du mois `o` (24 .. 35 mois d'historique), prévoit le mois o+h. Retourne un tableau long."""
    M, j = d["M"], d["j"]
    lignes = []
    for h in horizons:
        for o in range(debut, len(M) + 1 - h + 0):
            if o + h - 1 >= len(M):
                continue
            r = {"h": h, "origine": str(M.index[o - 1]), "cible": str(M.index[o + h - 1]), "reel": float(M.iloc[o + h - 1])}
            for nom, f in MODELES.items():
                r[nom] = f(M, o, h)
            r["régression de Poisson"] = prevoir_poisson(M, o, h, j)
            lignes.append(r)
    return pd.DataFrame(lignes)


def metriques(R, noms=None):
    noms = noms or [c for c in R.columns if c not in ("h", "origine", "cible", "reel")]
    out = {}
    for nom in noms:
        e = R[nom] - R["reel"]
        out[nom] = {"MAE": e.abs().mean(), "MAPE (%)": (e.abs() / R["reel"]).mean() * 100, "biais": e.mean(), "n": len(e)}
    return pd.DataFrame(out).T


def prevision_mois(d, mois="2026-01", scenario_promo=True):
    """Prévision de Poisson pour un mois futur (le calendrier est connu ; t continue la tendance)."""
    j = d["j"]
    m = _glm(j)
    jours = pd.date_range(f"{mois}-01", pd.Period(mois).end_time.normalize(), freq="D")
    f = calendrier(jours)
    f["t"] = (f["date"] - j["date"].iloc[0]).dt.days / 365.25
    if not scenario_promo:
        f["promo_active"] = 0
    return float(m.predict(f).sum()), m


# ------------------------------------------------------------------ cas B : rachat à 90 jours
VARS = ["l_recence", "l_nb_12m", "l_nb_3m", "l_montant_12m", "panier", "part_site", "nb_cats", "taux_retour", "fidelite", "rythme"]      # 10 variables « stables dans le temps »
VARS_CUMUL = ["l_nb_total", "anciennete"]                         # variables qui vieillissent : elles ne font que croître avec la date de coupure
VARS_BRUTES = ["recence", "nb_12m", "nb_3m", "montant_12m", "panier", "part_site", "nb_cats", "taux_retour", "fidelite", "rythme"]    # mêmes variables, sans logarithme


def instantane(d, coupure, horizon=90, fuite=None):
    """Une ligne par client ayant commandé au moins une fois jusqu'à `coupure` (incluse). Variables : passé seulement. Cible `y` : commande dans les `horizon` jours suivants.
    fuite='extraction' ajoute volontairement le nombre TOTAL de commandes de la base (futur compris)."""
    cmd, cli, rl, premiere = d["cmd"], d["cli"], d["rl"], d["premiere"]
    cut = pd.Timestamp(coupure)
    av = cmd[cmd["date_commande"] <= cut]
    g = av.groupby("id_client")
    f = pd.DataFrame({"recence": (cut - g["date_commande"].max()).dt.days, "nb_total": g.size(), "montant_total": g["montant"].sum()})
    a12 = av[av["date_commande"] > cut - pd.Timedelta(days=365)].groupby("id_client")
    f["nb_12m"], f["montant_12m"] = a12.size(), a12["montant"].sum()
    f["nb_3m"] = av[av["date_commande"] > cut - pd.Timedelta(days=90)].groupby("id_client").size()
    f[["nb_12m", "montant_12m", "nb_3m"]] = f[["nb_12m", "montant_12m", "nb_3m"]].fillna(0)
    f["panier"] = f["montant_total"] / f["nb_total"]
    f["part_site"] = av.assign(s=(av["canal"] == "Site").astype(float)).groupby("id_client")["s"].mean()
    f["nb_cats"] = g["cats"].agg(lambda s: len(frozenset().union(*s)))
    r = rl[rl["date_retour"] <= cut].groupby("id_client").size()
    f["retours"] = r
    f["retours"] = f["retours"].fillna(0)
    f["taux_retour"] = f["retours"] / f["nb_total"]
    c = cli.set_index("id_client")
    f["fidelite"], f["consentement"] = c["fidelite"], c["consentement_marketing"]
    f["anciennete"] = (cut - c["date_inscription"]).dt.days / 30.4
    f["age"] = cut.year - c["annee_naissance"] if "annee_naissance" in c else np.nan
    mois = ((cut - premiere.reindex(f.index)).dt.days / 30.4).clip(lower=1)
    f["rythme"] = f["nb_total"] / mois
    for k in ("nb_total", "nb_12m", "nb_3m", "montant_12m", "recence"):
        f["l_" + k] = np.log1p(f[k])
    ap = cmd[(cmd["date_commande"] > cut) & (cmd["date_commande"] <= cut + pd.Timedelta(days=horizon))]["id_client"].unique()
    f["y"] = f.index.isin(ap).astype(int)
    if fuite == "extraction":
        f["nb_commandes_base"] = cmd.groupby("id_client").size().reindex(f.index)
    f["trim"] = (cut.month - 1) // 3 + 1
    return f.reset_index().rename(columns={"index": "id_client"}) if f.index.name is None else f.reset_index()


def modele_log(C=1.0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=1000))


def modele_arbre(profondeur=3, feuille=100):
    from sklearn.tree import DecisionTreeClassifier
    return DecisionTreeClassifier(max_depth=profondeur, min_samples_leaf=feuille, random_state=0)


def modele_boost(**kw):
    import lightgbm as lgb
    p = dict(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=40, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=0, verbose=-1, n_jobs=1)
    p.update(kw)
    return lgb.LGBMClassifier(**p)


# ------------------------------------------------------------------ métriques écrites à la main
def auc_main(y, s):
    """AUC = probabilité qu'un acheteur tiré au hasard ait un score plus élevé qu'un non-acheteur (égalités comptées pour moitié)."""
    y, s = np.asarray(y), np.asarray(s)
    pos, neg = s[y == 1], s[y == 0]
    comp = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return comp / (len(pos) * len(neg))


def gain(y, s, parts=(0.1, 0.2, 0.3, 0.5)):
    """Part des acheteurs capturée en contactant les `p` % meilleurs scores ; et le lift (part / p)."""
    y, s = np.asarray(y), np.asarray(s)
    o = np.argsort(-s, kind="stable")
    cum = np.cumsum(y[o]) / y.sum()
    out = []
    for p in parts:
        k = int(round(p * len(y)))
        out.append((p, cum[k - 1], cum[k - 1] / p))
    return pd.DataFrame(out, columns=["contactés", "acheteurs captés", "lift"])


def calibration(y, p, k=10):
    y, p = np.asarray(y), np.asarray(p)
    q = pd.qcut(p, k, duplicates="drop")
    return pd.DataFrame({"prévu": pd.Series(p).groupby(q, observed=True).mean().values, "observé": pd.Series(y).groupby(q, observed=True).mean().values,
                         "n": pd.Series(y).groupby(q, observed=True).size().values})


def fr(x, n=1, signe=False):
    s = f"{x:+,.{n}f}" if signe else f"{x:,.{n}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")


# ------------------------------------------------------------------ plusieurs coupures (panel), saison, mini-AutoML
COUPURES = ["2023-12-31", "2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30"]


def panel(d, coupures=COUPURES):
    return {c: instantane(d, c).assign(coupure=c) for c in coupures}


def avec_saison(s, variables=None):
    """Variables du modèle + indicatrices du trimestre de la coupure (connu à l'avance)."""
    variables = variables or VARS
    t = pd.get_dummies(s["trim"], prefix="T").reindex(columns=["T_1", "T_2", "T_3", "T_4"], fill_value=0).astype(float)
    return pd.concat([s[variables].reset_index(drop=True), t.reset_index(drop=True)], axis=1)


def configurations(n=60, graine=7):
    rng = np.random.default_rng(graine)
    cfgs, vus = [], set()
    while len(cfgs) < n:
        k = len(cfgs)
        fam = rng.choice(["logistique", "arbre", "boosting", "forêt"], p=[0.25, 0.25, 0.3, 0.2])
        if fam == "logistique":
            p = {"C": float(10 ** rng.uniform(-3, 2))}
        elif fam == "arbre":
            p = {"profondeur": int(rng.integers(2, 9)), "feuille": int(rng.choice([20, 50, 100, 200]))}
        elif fam == "boosting":
            p = {"learning_rate": float(10 ** rng.uniform(-2.3, -0.7)), "max_depth": int(rng.integers(2, 6)), "max_iter": int(rng.choice([50, 100, 200, 400])),
                 "l2_regularization": float(rng.choice([0, 1, 10]))}
        else:
            p = {"n_estimators": int(rng.choice([50, 100, 200])), "max_depth": int(rng.integers(3, 10)), "min_samples_leaf": int(rng.choice([5, 20, 50]))}
        cle = (str(fam), tuple(sorted(p.items())))
        if cle in vus:                       # pas deux fois la même configuration
            continue
        vus.add(cle)
        cfgs.append({"id": k + 1, "famille": str(fam), **p})
    return cfgs


def construire(c):
    if c["famille"] == "logistique":
        return modele_log(c["C"])
    if c["famille"] == "arbre":
        return modele_arbre(c["profondeur"], c["feuille"])
    if c["famille"] == "boosting":
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(learning_rate=c["learning_rate"], max_depth=c["max_depth"], max_iter=c["max_iter"], l2_regularization=c["l2_regularization"], random_state=0)
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=c["n_estimators"], max_depth=c["max_depth"], min_samples_leaf=c["min_samples_leaf"], random_state=0, n_jobs=1)


def recherche(S, cfgs, entrainement=COUPURES[:6], test="2025-06-30", plis=(3, 4, 5)):
    """Mini-AutoML : pour chaque configuration, AUC en validation TEMPORELLE (on entraîne sur les coupures jusqu'à k, on valide sur la suivante), puis AUC sur la coupure de test (jamais vue)."""
    from sklearn.metrics import roc_auc_score
    lignes = []
    for c in cfgs:
        aucs = []
        for k in plis:
            tr = pd.concat([S[x] for x in entrainement[:k]])
            va = S[entrainement[k]]
            m = construire(c).fit(avec_saison(tr), tr["y"].values)
            aucs.append(roc_auc_score(va["y"], m.predict_proba(avec_saison(va))[:, 1]))
        tr = pd.concat([S[x] for x in entrainement])
        m = construire(c).fit(avec_saison(tr), tr["y"].values)
        lignes.append({**c, "cv": float(np.mean(aucs)), "cv_sd": float(np.std(aucs, ddof=1)), "test": roc_auc_score(S[test]["y"], m.predict_proba(avec_saison(S[test]))[:, 1])})
    return pd.DataFrame(lignes)


def auc_rapide(y, P):
    """AUC de plusieurs jeux de scores à la fois (lignes de P) par la statistique des rangs."""
    from scipy.stats import rankdata
    y = np.asarray(y)
    P = np.atleast_2d(P)
    r = rankdata(P, axis=1)
    n1 = y.sum()
    n0 = len(y) - n1
    return (r[:, y == 1].sum(1) - n1 * (n1 + 1) / 2) / (n1 * n0)


def variantes_logistiques(S, n=200, graine=11, entrainement=COUPURES[:6], test="2025-06-30"):
    """n régressions logistiques qui diffèrent par le sous-ensemble de variables et la régularisation ; retourne leurs scores sur la coupure de test."""
    rng = np.random.default_rng(graine)
    tr = pd.concat([S[c] for c in entrainement])
    Xtr, Xte = avec_saison(tr), avec_saison(S[test])
    P = []
    for _ in range(n):
        cols = list(rng.choice(VARS, int(rng.integers(3, 9)), replace=False)) + ["T_1", "T_2", "T_3", "T_4"]
        m = modele_log(float(10 ** rng.uniform(-3, 1))).fit(Xtr[cols], tr["y"].values)
        P.append(m.predict_proba(Xte[cols])[:, 1])
    return np.array(P), S[test]["y"].values


def optimisme(P, y, tailles=(500, 4000), ns=(1, 5, 20, 60, 200), B=200, graine=5):
    """Écart moyen entre l'AUC du gagnant sur un jeu de validation de `m` clients et son AUC sur tous les autres, selon le nombre n de candidats
    (mêmes tirages pour tous les n ; B tirages aléatoires du jeu de validation)."""
    rng = np.random.default_rng(graine)
    cumul = {(m, n): [] for m in tailles for n in ns}
    for m in tailles:
        for _ in range(B):
            idx = rng.permutation(len(y))
            v, p = idx[:m], idx[m:]
            av = auc_rapide(y[v], P[:, v])
            for n in ns:
                i = int(np.argmax(av[:n]))
                cumul[(m, n)].append(av[i] - auc_rapide(y[p], P[[i]][:, p])[0])
    return pd.DataFrame([{"validation": m, "candidats": n, "écart": float(np.mean(v))} for (m, n), v in cumul.items()])
