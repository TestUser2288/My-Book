"""Outils du chapitre 5 (séries temporelles) : chargement, indices saisonniers, prévisions de référence, mesures d'erreur.
Partagé par le livre (blocs cachés) et le cahier. Aucun résultat n'est calculé à l'import."""
import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
DONNEES = os.environ.get("DONNEES", "donnees")


def lire(nom, **kw):
    return pd.read_csv(os.path.join(DONNEES, nom), **kw)


def jours(incidents=False):
    """série quotidienne (date en index) ; `incidents=True` charge la version avec incidents injectés (journée du 20/10/2025 en double)"""
    j = lire("jours_incidents.csv" if incidents else "jours_exploitation.csv", parse_dates=["date"])
    return j.set_index("date")


def mensuel(serie_j, how="sum"):
    return serie_j.resample("MS").agg(how)


def indices_saisonniers(m, periode=12, multiplicatif=True):
    """indices saisonniers par la méthode classique : rapport (ou écart) à la moyenne mobile centrée 2 x periode, moyenné par position, normalisé (moyenne 1 ou somme 0)"""
    k = periode
    mm = m.rolling(k, center=True).mean().rolling(2, center=True).mean().shift(-1) if k % 2 == 0 else m.rolling(k, center=True).mean()
    r = (m / mm) if multiplicatif else (m - mm)
    pos = m.index.month if k == 12 else np.arange(len(m)) % k
    idx = r.groupby(pos).mean()
    return idx / idx.mean() if multiplicatif else idx - idx.mean()


def mae(y, f):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(f))))


def rmse(y, f):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(f)) ** 2)))


def mape(y, f):
    y, f = np.asarray(y, float), np.asarray(f, float)
    return float(np.mean(np.abs(y - f) / np.abs(y)) * 100)


def mase(y, f, train, m=1):
    """erreur absolue moyenne rapportée à celle de la prévision naïve (saisonnière de période m) sur l'entraînement"""
    train = np.asarray(train, float)
    ech = np.mean(np.abs(train[m:] - train[:-m]))
    return mae(y, f) / ech


def prevision_naive(train, h):
    return np.repeat(train.iloc[-1], h)


def prevision_naive_saisonniere(train, h, m=12):
    v = train.iloc[-m:].values
    return np.array([v[i % m] for i in range(h)])


# ------------------------------------------------------------------ données du chapitre
def charger():
    """(j, m) : série quotidienne propre et série mensuelle du chiffre d'affaires TTC"""
    j = jours().asfreq("D")
    return j, mensuel(j["chiffre_affaires"])


def residus_robustes(ji):
    """incidents : modèle robuste (jour de semaine, mois, promotion, tendance) sur le log du CA ; retourne le score z robuste (MAD) de chaque jour"""
    import statsmodels.formula.api as smf
    base = jours().asfreq("D")
    y = np.log(ji[~ji.index.duplicated()]["chiffre_affaires"].asfreq("D"))
    d = pd.DataFrame({"y": y})
    d["jds"], d["mois"], d["t"] = d.index.dayofweek, d.index.month, np.arange(len(d)) / 365.25
    d["promo"] = base["promo_active"].values
    r = smf.rlm("y ~ C(jds) + C(mois) + promo + t", d).fit()
    res = d["y"] - r.fittedvalues
    mad = np.median(np.abs(res - np.median(res))) * 1.4826
    z = (res - np.median(res)) / mad
    z.attrs["mad"] = float(mad)
    return z


def previsions_mensuelles(m, fin_train="2024-12-01", horizon=12):
    """six prévisions du CA mensuel sur `horizon` mois après `fin_train` ; retourne (dict, train, test)"""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    tr, te = m[:fin_train], m[pd.Timestamp(fin_train) + pd.offsets.MonthBegin(1):][:horizon]
    F = {}
    F["naïve (dernier mois)"] = prevision_naive(tr, horizon)
    F["naïve saisonnière"] = prevision_naive_saisonniere(tr, horizon)
    g = tr.iloc[-12:].sum() / tr.iloc[-24:-12].sum()
    F["naïve saisonnière × croissance"] = F["naïve saisonnière"] * g
    F["moyenne des 12 derniers mois"] = np.repeat(tr.iloc[-12:].mean(), horizon)
    idx = indices_saisonniers(tr)
    des = tr / idx.reindex(tr.index.month).values
    b = np.polyfit(np.arange(len(tr)), des.values, 1)
    F["tendance linéaire × indices"] = np.polyval(b, np.arange(len(tr), len(tr) + horizon)) * idx.reindex(te.index.month).values
    hw = ExponentialSmoothing(tr, trend="add", seasonal="mul", seasonal_periods=12, initialization_method="estimated").fit()
    F["Holt-Winters"] = hw.forecast(horizon).values
    return F, tr, te


def tableau_erreurs(F, tr, te):
    lignes = [(k, mae(te, v), rmse(te, v), mape(te, v), mase(te, v, tr, 12), (np.sum(v) / te.sum() - 1) * 100) for k, v in F.items()]
    return pd.DataFrame(lignes, columns=["méthode", "MAE", "RMSE", "MAPE %", "MASE", "biais %"]).set_index("méthode")


def previsions_28j(y, o, H=28):
    """prévisions de H jours après la date `o` (dernier jour connu) par cinq méthodes simples sur la série quotidienne y"""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    tr = y[:o]
    fut_idx = pd.date_range(o + pd.Timedelta(days=1), periods=H, freq="D")
    f = {}
    f["naïve saisonnière 7 j"] = np.tile(tr.iloc[-7:].values, H // 7)
    dows = fut_idx.dayofweek
    f["moyenne des 4 mêmes jours"] = np.array([tr.iloc[-28:][tr.iloc[-28:].index.dayofweek == d].mean() for d in dows])
    ly = y.reindex(fut_idx - pd.Timedelta(days=364)).values
    f["même jour l'an dernier"] = ly
    ratio = tr.iloc[-28:].sum() / y.reindex(tr.index[-28:] - pd.Timedelta(days=364)).sum()
    f["an dernier × niveau récent"] = ly * ratio
    hw = ExponentialSmoothing(tr.iloc[-120:], seasonal="mul", seasonal_periods=7, initialization_method="estimated").fit()
    f["Holt-Winters (7 j)"] = hw.forecast(H).values
    return f, fut_idx


def origines(y, debut="2025-01-07", fin="2025-12-02", pas=7, H=28):
    """évalue les cinq méthodes à plusieurs origines ; retourne (MAE quotidienne, erreur relative sur le total des H jours) par méthode et par origine"""
    mae_o, tot_o = {}, {}
    for o in pd.date_range(debut, fin, freq=f"{pas}D"):
        fut = y[o + pd.Timedelta(days=1): o + pd.Timedelta(days=H)]
        if len(fut) < H:
            continue
        f, _ = previsions_28j(y, o, H)
        for k, v in f.items():
            mae_o.setdefault(k, {})[o] = mae(fut, v)
            tot_o.setdefault(k, {})[o] = (v.sum() / fut.sum() - 1) * 100
    return pd.DataFrame(mae_o), pd.DataFrame(tot_o)


# ------------------------------------------------------------------ section 5.3
def prevision_tendance_indices(s, fin_train, horizon=12):
    """CA mensuel : tendance linéaire de la série désaisonnalisée × indices saisonniers (appris sur l'entraînement seulement)"""
    tr = s[:fin_train]
    idx = indices_saisonniers(tr)
    des = tr / idx.reindex(tr.index.month).values
    b = np.polyfit(np.arange(len(tr)), des.values, 1)
    fut = pd.date_range(pd.Timestamp(fin_train) + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return pd.Series(np.polyval(b, np.arange(len(tr), len(tr) + horizon)) * idx.reindex(fut.month).values, index=fut)


def ca_par_canal():
    """CA mensuel par canal (colonnes Boutique, Réseaux, Site)"""
    x = lire("lignes_commande.csv").merge(lire("commandes.csv")[["id_commande", "date_commande", "canal"]], on="id_commande")
    x["mois"] = pd.to_datetime(x["date_commande"]).dt.to_period("M").dt.to_timestamp()
    return x.pivot_table(index="mois", columns="canal", values="montant", aggfunc="sum")


def erreur_par_horizon(y, horizons=(7, 14, 28, 56, 84), debut="2025-01-07", fin="2025-10-07", pas=7):
    """erreur relative absolue moyenne (%) sur le TOTAL des h jours suivants, pour deux méthodes : niveau récent plat, et an dernier × niveau récent"""
    res = {("niveau récent (plat)", h): [] for h in horizons}
    res.update({("an dernier × niveau récent", h): [] for h in horizons})
    for o in pd.date_range(debut, fin, freq=f"{pas}D"):
        fut = y[o + pd.Timedelta(days=1): o + pd.Timedelta(days=max(horizons))]
        if len(fut) < max(horizons):
            continue
        tr = y[:o]
        niv = tr.iloc[-28:].mean()
        ly = y.reindex(fut.index - pd.Timedelta(days=364)).values
        ratio = tr.iloc[-56:].sum() / y.reindex(tr.index[-56:] - pd.Timedelta(days=364)).sum()
        for h in horizons:
            r = fut.iloc[:h].sum()
            res[("niveau récent (plat)", h)].append(abs(niv * h - r) / r * 100)
            res[("an dernier × niveau récent", h)].append(abs(ly[:h].sum() * ratio - r) / r * 100)
    t = pd.Series({k: np.mean(v) for k, v in res.items()})
    return t.unstack(0)[["niveau récent (plat)", "an dernier × niveau récent"]]


def comparer_sarima_hw(y, debut="2025-01-07", fin="2025-12-02", pas=14, H=28, fenetre=180):
    """SARIMA (1,1,1)(0,1,1,7) sur le log du CA quotidien contre Holt-Winters (7 j) : MAE quotidienne et erreur sur le total des H jours, à plusieurs origines"""
    import statsmodels.api as sm
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    out = {"SARIMA": [], "Holt-Winters": [], "SARIMA total": [], "Holt-Winters total": []}
    for o in pd.date_range(debut, fin, freq=f"{pas}D"):
        fut = y[o + pd.Timedelta(days=1): o + pd.Timedelta(days=H)]
        if len(fut) < H:
            continue
        tr = y[:o].iloc[-fenetre:]
        p = np.exp(sm.tsa.SARIMAX(np.log(tr), order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=50).forecast(H).values)
        q = ExponentialSmoothing(tr, seasonal="mul", seasonal_periods=7, initialization_method="estimated").fit().forecast(H).values
        out["SARIMA"].append(mae(fut, p)); out["Holt-Winters"].append(mae(fut, q))
        out["SARIMA total"].append(abs(p.sum() - fut.sum()) / fut.sum() * 100); out["Holt-Winters total"].append(abs(q.sum() - fut.sum()) / fut.sum() * 100)
    return pd.DataFrame(out)
