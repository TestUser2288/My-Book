"""Outils du chapitre 4 (série 2, volume V) : analytique du risque et de l'assurance. Tout est SIMULÉ (voir `donnees_a5.py` pour la vérité programmée).

Le livre montre peu de code : les calculs (triangle, chain ladder, cohortes, matrice de transition, alertes, états) vivent ici, et chaque section appelle
quelques fonctions. Les figures sont produites par les fonctions `fig_*` (style commun de `style.py`).

Écrit aussi trois petits jeux de rapprochement (`ecrire_donnees`) : `ch04-compta-primes.csv` et `ch04-regularisations.csv` (le « grand livre » fictif de l'assureur).
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style as S  # noqa: E402

warnings.filterwarnings("ignore")
FRAIS = 0.28            # ratio de frais de l'assureur (fictif, constant : voir la docstring de donnees_a5.py)
BUCKETS = ["0", "1-29", "30-59", "60-89", "90+"]
TAUX_PROV = {"0": 0.005, "1-29": 0.02, "30-59": 0.10, "60-89": 0.30, "90+": 0.55}   # taux de provisionnement FICTIFS, par tranche de retard


def fr(x, nd=1, signe=False):
    """nombre à la française : espace fine insécable pour les milliers, virgule décimale"""
    s = f"{x:+,.{nd}f}" if signe else f"{x:,.{nd}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, nd=1, signe=False):
    return fr(100 * x, nd, signe) + " %"


# ----------------------------------------------------------------------------------------------- données
def charger(D):
    """Les huit jeux du chapitre, avec quelques colonnes dérivées."""
    lire = lambda f, **k: pd.read_csv(os.path.join(D, f), **k)
    pol, ex = lire("polices.csv"), lire("expositions.csv")
    sin = lire("sinistres.csv", parse_dates=["date_survenance", "date_declaration"])
    pay = lire("paiements.csv", parse_dates=["date_paiement"])
    ver = lire("verite_sinistres.csv")
    sin["an"] = sin["date_survenance"].dt.year
    sin["charge"] = sin["montant_paye"] + sin["reserve_dossier"]            # payé + réserve dossier-par-dossier
    sin = sin.merge(ver[["id_sinistre", "cout_ultime"]], on="id_sinistre").merge(pol[["id_police", "classe_age", "zone", "puissance", "usage", "bonus"]], on="id_police")
    ex = ex.merge(pol[["id_police", "classe_age", "zone"]], on="id_police")
    prets = lire("prets.csv", parse_dates=["date_octroi"])
    suivi = lire("suivi_mensuel.csv", parse_dates=["mois"])
    vp = lire("verite_prets.csv")
    return dict(pol=pol, ex=ex, sin=sin, pay=pay, ver=ver, prets=prets, suivi=suivi, vp=vp)


# ----------------------------------------------------------------------------------------------- assurance : sinistres
def bilan_annuel(d):
    """Une ligne par année de survenance : exposition, primes acquises, nombre, fréquence, coût moyen, charge déclarée (payé + réserves), S/P déclaré."""
    ex, s = d["ex"], d["sin"]
    g = ex.groupby("annee").agg(exposition=("exposition", "sum"), primes=("prime_acquise", "sum"))
    g["nb"] = s.groupby("an").size()
    g["frequence"] = g["nb"] / g["exposition"]
    g["charge"] = s.groupby("an")["charge"].sum()
    g["cout_moyen"] = g["charge"] / g["nb"]
    g["sp_declare"] = g["charge"] / g["primes"]
    return g


def triangle(d):
    """Triangle de développement ANNUEL des paiements : lignes = année de survenance, colonnes = délai (année de paiement - année de survenance).
    Retourne (incrémental, cumulé), avec NaN dans la partie future (au-delà du 31/12/2025)."""
    p = d["pay"].merge(d["sin"][["id_sinistre", "an"]], on="id_sinistre")
    p["delai"] = p["date_paiement"].dt.year - p["an"]
    inc = p.pivot_table(index="an", columns="delai", values="montant", aggfunc="sum", fill_value=0.0)
    for a in inc.index:
        for k in inc.columns:
            if a + k > 2025:
                inc.loc[a, k] = np.nan
    return inc, inc.cumsum(axis=1).where(inc.notna())


def chain_ladder(cum):
    """Chain ladder « à la main » : facteurs de développement (somme des cumuls du délai k+1 / somme des cumuls du délai k, sur les années où k+1 est connu),
    puis ultime = dernier cumul observé x produit des facteurs restants. Retourne (facteurs, tableau par année)."""
    n = cum.shape[1]
    f = []
    for k in range(n - 1):
        m = cum[k + 1].notna()
        f.append(cum.loc[m, k + 1].sum() / cum.loc[m, k].sum())
    f = np.array(f)
    rest = np.array([np.prod(f[k:]) for k in range(n)])                       # facteur jusqu'à l'ultime, depuis le délai k
    dernier = cum.apply(lambda r: r.dropna().iloc[-1], axis=1)
    k_obs = cum.apply(lambda r: r.notna().sum() - 1, axis=1)
    t = pd.DataFrame({"paye": dernier, "delai": k_obs, "facteur": rest[k_obs.to_numpy()]})
    t["ultime"] = t["paye"] * t["facteur"]
    t["a_payer"] = t["ultime"] - t["paye"]
    return f, t


def vrai_ultime(d):
    """Coût ultime VRAI par année de survenance (inconnu en pratique) : sinistres déclarés + les 114 non déclarés, survenus fin 2025 (affectés à 2025)."""
    s, v = d["sin"], d["ver"]
    u = s.groupby("an")["cout_ultime"].sum()
    u.loc[2025] += v.loc[~v["declare_au_31_12_2025"], "cout_ultime"].sum()
    return u


def comparer_provisions(d):
    """Pour chaque année : payé, charge dossier-par-dossier (payé + réserves), ultime chain ladder, ultime vrai."""
    inc, cum = triangle(d)
    f, t = chain_ladder(cum)
    b = bilan_annuel(d)
    r = pd.DataFrame({"paye": t["paye"], "charge_dossiers": b["charge"], "ultime_cl": t["ultime"], "ultime_vrai": vrai_ultime(d)})
    r["ecart_cl"] = r["ultime_cl"] / r["ultime_vrai"] - 1
    r["ecart_dossiers"] = r["charge_dossiers"] / r["ultime_vrai"] - 1
    return f, r


def sp_par_segment(d, col, ecreter=None, avant=2024):
    """S/P (coût ultime vrai / primes acquises) par segment, sur les années de survenance <= avant ; `ecreter` plafonne le coût de chaque sinistre."""
    s = d["sin"][d["sin"]["an"] <= avant].copy()
    c = s["cout_ultime"] if ecreter is None else s["cout_ultime"].clip(upper=ecreter)
    pr = d["ex"][d["ex"]["annee"] <= avant].groupby(col)["prime_acquise"].sum()
    return c.groupby(s[col]).sum() / pr


def ic_sp(d, col, ecreter=None, avant=2024, B=1000, graine=44):
    """Intervalle à 90 % du S/P de chaque segment par bootstrap : on retire au hasard (avec remise) les sinistres du segment, les primes restent fixes."""
    rng = np.random.default_rng(graine)
    s = d["sin"][d["sin"]["an"] <= avant]
    pr = d["ex"][d["ex"]["annee"] <= avant].groupby(col)["prime_acquise"].sum()
    out = {}
    for seg, g in s.groupby(col):
        c = (g["cout_ultime"] if ecreter is None else g["cout_ultime"].clip(upper=ecreter)).to_numpy()
        tir = rng.choice(c, size=(B, len(c)), replace=True).sum(axis=1) / pr[seg]
        out[seg] = (np.quantile(tir, 0.05), np.quantile(tir, 0.95))
    return pd.DataFrame(out, index=["bas", "haut"]).T


def table_sp(d, col, avant=2024):
    """Tableau par segment : exposition, primes, fréquence, coût moyen, S/P, ratio combiné (S/P + frais)."""
    s = d["sin"][d["sin"]["an"] <= avant]
    e = d["ex"][d["ex"]["annee"] <= avant]
    t = e.groupby(col).agg(exposition=("exposition", "sum"), primes=("prime_acquise", "sum"))
    t["nb"] = s.groupby(col).size()
    t["frequence"] = t["nb"] / t["exposition"]
    t["cout_moyen"] = s.groupby(col)["cout_ultime"].sum() / t["nb"]
    t["sp"] = s.groupby(col)["cout_ultime"].sum() / t["primes"]
    t["combine"] = t["sp"] + FRAIS
    return t


# ----------------------------------------------------------------------------------------------- assurance : GLM
def police_annees(d, jusqu_a=2024):
    """Table police-année avec le nombre de sinistres (pour le GLM de fréquence)."""
    s, e, pol = d["sin"], d["ex"], d["pol"]
    n = s.groupby(["id_police", "an"]).size().rename("nb").reset_index().rename(columns={"an": "annee"})
    t = e.merge(pol[["id_police", "age_conducteur", "puissance", "usage", "bonus"]], on="id_police").merge(n, on=["id_police", "annee"], how="left").fillna({"nb": 0})
    t["nb"] = t["nb"].astype(int)
    return t[t["annee"] <= jusqu_a].reset_index(drop=True)


def glm_frequence(d):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    t = police_annees(d)
    f = "nb ~ C(classe_age, Treatment('40-59 ans')) + C(zone, Treatment('A')) + C(puissance) + C(usage, Treatment('Privé')) + np.log(bonus)"
    return smf.glm(f, data=t, family=sm.families.Poisson(), offset=np.log(t["exposition"])).fit(), t


def glm_severite(d):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    s = d["sin"]
    s = s[(s["an"] <= 2024) & (s["nature"] == "Matériel")].copy()
    s["annee_rel"] = s["an"] - 2021
    return smf.glm("charge ~ C(zone, Treatment('A')) + C(classe_age, Treatment('40-59 ans')) + annee_rel", data=s, family=sm.families.Gamma(sm.families.links.Log())).fit()


def relativites(mod, prefixe, ref_label):
    """Rapports multiplicatifs (exp des coefficients) et intervalle à 95 % pour les modalités d'un facteur."""
    ci = np.exp(mod.conf_int())
    out = {}
    for k in mod.params.index:
        if prefixe in k:
            nom = k.split("T.")[1].rstrip("]")
            out[nom] = (np.exp(mod.params[k]), ci.loc[k, 0], ci.loc[k, 1])
    out[ref_label] = (1.0, 1.0, 1.0)
    return pd.DataFrame(out, index=["rapport", "bas", "haut"]).T


# ----------------------------------------------------------------------------------------------- crédit
def suivi_enrichi(d):
    s = d["suivi"].merge(d["prets"][["id_pret", "segment", "secteur", "region", "date_octroi", "duree_mois", "montant", "score_origine"]], on="id_pret")
    s["tranche"] = pd.cut(s["jours_retard"], [-1, 0, 29, 59, 89, 10 ** 6], labels=BUCKETS)
    s["secteur"] = s["secteur"].fillna("Particuliers")
    s["millesime"] = s["date_octroi"].dt.year.astype(str) + " S" + ((s["date_octroi"].dt.month - 1) // 6 + 1).astype(str)
    return s.sort_values(["id_pret", "mois"]).reset_index(drop=True)


def defauts_par_millesime_brut(d):
    """Part des prêts passés en défaut, par semestre d'octroi, SANS tenir compte de l'âge (trompeur : les récents ont eu moins de temps)."""
    s = suivi_enrichi(d)
    dd = s.groupby("id_pret")["jours_retard"].max().ge(90)
    p = d["prets"].set_index("id_pret")
    p["millesime"] = p["date_octroi"].dt.year.astype(str) + " S" + ((p["date_octroi"].dt.month - 1) // 6 + 1).astype(str)
    return dd.groupby(p["millesime"]).mean()


def courbes_cohortes(d, age_max=24, seuil_risque=300, par="millesime"):
    """Taux de défaut CUMULÉ par âge pour chaque semestre d'octroi : à chaque âge, risque = défauts / prêts observés à cet âge ; cumul = 1 - produit(1 - risque).
    On arrête la courbe quand moins de `seuil_risque` prêts sont encore observés (troncature à droite)."""
    s = suivi_enrichi(d)
    s["defaut"] = (s["jours_retard"] >= 90).astype(int)
    g = s.groupby([par, "age_mois"]).agg(obs=("defaut", "size"), dfl=("defaut", "sum")).reset_index()
    g["h"] = g["dfl"] / g["obs"]
    g = g[(g["age_mois"] <= age_max) & (g["obs"] >= seuil_risque)]
    g["cumul"] = g.groupby(par)["h"].transform(lambda h: 1 - (1 - h).cumprod())
    return g.pivot(index="age_mois", columns=par, values="cumul")


def matrice_transition(d, col=None, val=None):
    """Matrice de transition mensuelle entre tranches de retard (effectifs et pourcentages en ligne), avec une colonne « Sortie » (remboursé ou échu).
    La dernière observation de chaque prêt est exclue quand elle est censurée (décembre 2025)."""
    s = suivi_enrichi(d)
    s["suiv"] = s.groupby("id_pret")["tranche"].shift(-1).astype("object")
    dern = s.groupby("id_pret").tail(1).index
    sortie = s.loc[dern, "jours_retard"].lt(90) & s.loc[dern, "mois"].lt(pd.Timestamp("2025-12-01"))
    s.loc[sortie[sortie].index, "suiv"] = "Sortie"
    t = s.dropna(subset=["suiv"])
    if col is not None:
        t = t[t[col] == val]
    n = pd.crosstab(t["tranche"], t["suiv"])
    n = n[[c for c in BUCKETS + ["Sortie"] if c in n.columns]]
    return n, n.div(n.sum(axis=1), axis=0)


def stock_mensuel(d, mois_defaut=12):
    """Encours sain par mois (prêts encore suivis) et créances douteuses (encours des prêts entrés en défaut dans les `mois_defaut` derniers mois : HYPOTHÈSE de
    simplification, car le jeu s'arrête au défaut). Retourne aussi provisions fictives et taux de couverture."""
    s = suivi_enrichi(d)
    s["prov"] = s["encours"] * s["tranche"].map(TAUX_PROV).astype(float)
    sain = s[s["jours_retard"] < 90].groupby("mois").agg(encours=("encours", "sum"), prov=("prov", "sum"), nb=("encours", "size"))
    dfl = s[s["jours_retard"] >= 90].groupby("mois")["encours"].sum().reindex(sain.index, fill_value=0)
    t = sain.copy()
    t["douteux"] = dfl.rolling(mois_defaut, min_periods=1).sum()
    t["prov_douteux"] = t["douteux"] * TAUX_PROV["90+"]
    t["taux_douteux"] = t["douteux"] / (t["encours"] + t["douteux"])
    t["couverture"] = (t["prov"] + t["prov_douteux"]) / t["douteux"]
    return t


def hhi(parts):
    """Indice de Herfindahl-Hirschman : somme des carrés des parts (entre 1/n et 1)."""
    p = np.asarray(parts, dtype=float)
    p = p / p.sum()
    return float((p ** 2).sum())


def concentration(d, mois="2025-12-01", col="secteur"):
    s = suivi_enrichi(d)
    x = s[(s["mois"] == pd.Timestamp(mois)) & (s["jours_retard"] < 90)]
    e = x.groupby(col)["encours"].sum().sort_values(ascending=False)
    return e / e.sum()


def risque_secteur(d, debut="2024-01-01", coupe="2025-01-01"):
    """Taux de défaut mensuel annualisé par secteur, avant et après `coupe` (nombre de défauts / nombre de prêts-mois x 12) et intervalle de Poisson approché."""
    s = suivi_enrichi(d)
    s = s[(s["mois"] >= pd.Timestamp(debut)) & (s["age_mois"] >= 1)]
    s["periode"] = np.where(s["mois"] < pd.Timestamp(coupe), "avant", "apres")
    g = s.groupby(["secteur", "periode"]).agg(pm=("encours", "size"), dfl=("jours_retard", lambda x: int((x >= 90).sum()))).reset_index()
    g["taux"] = 12 * g["dfl"] / g["pm"]
    g["se"] = 12 * np.sqrt(g["dfl"].clip(lower=1)) / g["pm"]
    return g


# ----------------------------------------------------------------------------------------------- alertes précoces
CARACT = ["jours_retard", "incidents_3m", "dec_moy3", "dec_delta", "score_origine"]


def instantanes(d, horizon=6):
    """Une ligne par prêt et par mois (prêt non encore en défaut) avec des signaux CALCULABLES AU MOMENT t (retards, incidents, découvert) et la cible
    « défaut dans les `horizon` mois qui suivent » ; seuls les mois dont l'horizon est entièrement observé (<= 2025-06) sont conservés."""
    s = d["suivi"].merge(d["vp"], on="id_pret").merge(d["prets"][["id_pret", "score_origine"]], on="id_pret").sort_values(["id_pret", "mois"]).reset_index(drop=True)
    g = s.groupby("id_pret")
    s["retard_max3"] = g["jours_retard"].transform(lambda x: x.rolling(3, min_periods=1).max())
    s["dec_moy3"] = g["utilisation_decouvert"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    s["dec_delta"] = s["utilisation_decouvert"] - g["utilisation_decouvert"].shift(3).fillna(s["utilisation_decouvert"])
    avant = s["age_defaut"] - s["age_mois"]
    s["y"] = ((avant >= 1) & (avant <= horizon)).astype(int)
    s["avant"] = avant
    base = s[(s["jours_retard"] < 90) & (s["mois"] <= pd.Timestamp("2025-06-01"))]
    return base.reset_index(drop=True)


def modele_alerte(d, horizon=6):
    """Apprentissage sur 2023, test sur 2024-01 → 2025-06 (séparation TEMPORELLE) ; score = régression logistique sur des variables centrées-réduites."""
    from sklearn.linear_model import LogisticRegression
    b = instantanes(d, horizon)
    tr = b[b["mois"].between("2023-01-01", "2023-12-01")]
    te = b[b["mois"].between("2024-01-01", "2025-06-01")].copy()
    mu, sd = tr[CARACT].mean(), tr[CARACT].std()
    m = LogisticRegression(max_iter=1000).fit((tr[CARACT] - mu) / sd, tr["y"])
    te["score"] = m.predict_proba((te[CARACT] - mu) / sd)[:, 1]
    return m, tr, te, pd.Series(m.coef_[0], index=CARACT)


def evaluer_topk(te, ks=(25, 50, 100, 200, 400), score="score"):
    """Chaque mois, le comité examine les k prêts les mieux notés : précision (part de vrais défauts à venir) et rappel (part des défauts à venir attrapés)."""
    out = []
    for k in ks:
        pr, rc = [], []
        for _, m in te.groupby("mois"):
            top = m.nlargest(k, score)
            pr.append(top["y"].mean())
            rc.append(top["y"].sum() / max(m["y"].sum(), 1))
        out.append((k, np.mean(pr), np.mean(rc)))
    return pd.DataFrame(out, columns=["k", "precision", "rappel"]).set_index("k")


def delai_anticipation(te, k=100):
    """Pour les prêts qui font défaut dans la période de test et sont précédés d'un signal : nombre de mois entre la PREMIÈRE alerte (prêt dans le top-k du mois) et le défaut."""
    te = te.copy()
    te["alerte"] = te.groupby("mois")["score"].rank(ascending=False, method="first") <= k
    a = te[te["alerte"] & (te["y"] == 1)].groupby("id_pret")["avant"].max()
    return a


# ----------------------------------------------------------------------------------------------- reporting
def kpi_assureur(d, annee=2024):
    """Indicateurs de gestion de l'assureur pour une année de survenance (S/P sur le coût ultime estimé par chain ladder)."""
    f, r = comparer_provisions(d)
    b = bilan_annuel(d).loc[annee]
    ult = r.loc[annee, "ultime_cl"]
    return {"exposition": b["exposition"], "primes": b["primes"], "nb": int(b["nb"]), "frequence": b["frequence"], "cout_moyen": ult / b["nb"], "sp": ult / b["primes"],
            "frais": FRAIS, "combine": ult / b["primes"] + FRAIS}


def kpi_banque(d, mois="2025-06-01"):
    st = stock_mensuel(d).loc[pd.Timestamp(mois)]
    return {"encours": st["encours"], "nb": int(st["nb"]), "douteux": st["douteux"], "taux_douteux": st["taux_douteux"], "provisions": st["prov"] + st["prov_douteux"], "couverture": st["couverture"]}


def ecrire_donnees(D):
    """Grand livre FICTIF de l'assureur : primes comptabilisées par année (= primes acquises du système de gestion, sauf 2024 où un décalage de comptabilisation
    de 0,9 % est expliqué par six régularisations datées de janvier 2025), pour apprendre le rapprochement."""
    ex = pd.read_csv(os.path.join(D, "expositions.csv"))
    p = ex.groupby("annee")["prime_acquise"].sum().round(0)
    rng = np.random.default_rng(4401)
    ecart = round(float(p.loc[2024]) * 0.009, 0)
    cuts = rng.dirichlet(np.ones(6)) * ecart
    cuts = np.round(cuts, 0)
    cuts[-1] = ecart - cuts[:-1].sum()
    reg = pd.DataFrame({"reference": [f"REG-{i + 1:03d}" for i in range(6)], "annee_gestion": 2024, "date_comptable": "2025-01-" + pd.Series(rng.integers(2, 29, 6)).map("{:02d}".format),
                        "motif": ["régularisation de prime", "avenant tardif", "régularisation de prime", "avenant tardif", "régularisation de prime", "annulation tardive"], "montant": cuts})
    c = p.copy()
    c.loc[2024] = p.loc[2024] - ecart
    pd.DataFrame({"annee": c.index, "prime_comptabilisee": c.to_numpy()}).to_csv(os.path.join(D, "ch04-compta-primes.csv"), index=False)
    reg.to_csv(os.path.join(D, "ch04-regularisations.csv"), index=False)


def rapprochement(d, compta, tolerance=0.001):
    """Compare les primes acquises du système de gestion aux primes comptabilisées, par année ; écart relatif et verdict au regard de la tolérance."""
    g = d["ex"].groupby("annee")["prime_acquise"].sum().round(0)
    t = pd.DataFrame({"gestion": g, "compta": compta.set_index("annee")["prime_comptabilisee"]})
    t["ecart"] = t["gestion"] - t["compta"]
    t["ecart_rel"] = t["ecart"] / t["compta"]
    t["verdict"] = np.where(t["ecart_rel"].abs() <= tolerance, "conforme", "à expliquer")
    return t


# ----------------------------------------------------------------------------------------------- compléments (transitions, signaux, états, contrôles)
def proba_defaut_horizon(n, horizons=(1, 3, 6, 12)):
    """Probabilité d'être en défaut (90+) dans `h` mois, depuis chaque tranche : on élève la matrice de transition à la puissance h, en rendant « 90+ » et « Sortie »
    absorbants (un prêt entré en défaut ou sorti ne bouge plus)."""
    p = n.div(n.sum(axis=1), axis=0).reindex(columns=BUCKETS + ["Sortie"]).fillna(0.0)
    # lignes : 0, 1-29, 30-59, 60-89, 90+ (absorbant), Sortie (absorbant)
    P = np.vstack([p.loc[["0", "1-29", "30-59", "60-89"]].to_numpy(), np.eye(6)[4], np.eye(6)[5]])
    out = {h: np.linalg.matrix_power(P, h)[:4, 4] for h in horizons}
    return pd.DataFrame(out, index=["0", "1-29", "30-59", "60-89"])


def signaux_avant_defaut(d, jusqu_a=8):
    """Valeur moyenne des trois signaux, selon le nombre de mois qui restent avant le défaut (0 = le mois du défaut), comparée aux prêts qui ne font jamais défaut."""
    s = d["suivi"].merge(d["vp"], on="id_pret")
    s["avant"] = s["age_defaut"] - s["age_mois"]
    cols = ["jours_retard", "incidents_3m", "utilisation_decouvert"]
    t = s[s["avant"].between(0, jusqu_a)].groupby("avant")[cols].mean()
    t.loc["jamais"] = s.loc[s["age_defaut"].isna(), cols].mean()
    return t


def precision_par_trimestre(te, k=100):
    """Précision au top-k (moyenne des mois), par trimestre de test : le modèle appris en 2023 vieillit-il ?"""
    out = {}
    for mois, m in te.groupby("mois"):
        out[mois] = m.nlargest(k, "score")["y"].mean()
    s = pd.Series(out)
    return s.groupby(s.index.to_period("Q")).mean()


def etat_assureur(d, annee=2024):
    """État de gestion de l'assureur (maquette générique, cases A01-A06)."""
    k = kpi_assureur(d, annee)
    prim, cout = k["primes"], k["sp"] * k["primes"]
    frais = FRAIS * prim
    return pd.DataFrame({"case": ["A01", "A02", "A03", "A04", "A05", "A06"],
                         "libelle": ["Primes acquises", "Coût ultime estimé des sinistres", "Frais", "Résultat technique", "Ratio S/P", "Ratio combiné"],
                         "valeur": [prim, cout, frais, prim - cout - frais, cout / prim, (cout + frais) / prim]}).set_index("case")


def etat_banque(d, mois="2025-06-01"):
    """État de gestion de la banque (maquette générique, cases B01-B07)."""
    st = stock_mensuel(d).loc[pd.Timestamp(mois)]
    conc = hhi(concentration(d, mois))
    return pd.DataFrame({"case": ["B01", "B02", "B03", "B04", "B05", "B06", "B07"],
                         "libelle": ["Encours sain", "Créances douteuses", "Taux de créances douteuses", "Provisions (taux fictifs)", "Taux de couverture", "Indice de concentration (HHI)", "Nombre de prêts sains"],
                         "valeur": [st["encours"], st["douteux"], st["douteux"] / (st["encours"] + st["douteux"]), st["prov"] + st["prov_douteux"],
                                    (st["prov"] + st["prov_douteux"]) / st["douteux"], conc, st["nb"]]}).set_index("case")


def controles_etats(ea, eb, tol=1e-6):
    """Contrôles arithmétiques internes aux états : chaque ligne donne le nom du contrôle et un booléen."""
    c = {
        "A04 = A01 - A02 - A03": abs(ea.loc["A04", "valeur"] - (ea.loc["A01", "valeur"] - ea.loc["A02", "valeur"] - ea.loc["A03", "valeur"])) < 1,
        "A05 = A02 / A01": abs(ea.loc["A05", "valeur"] - ea.loc["A02", "valeur"] / ea.loc["A01", "valeur"]) < tol,
        "A06 = A05 + frais / A01": abs(ea.loc["A06", "valeur"] - (ea.loc["A05", "valeur"] + ea.loc["A03", "valeur"] / ea.loc["A01", "valeur"])) < tol,
        "B03 = B02 / (B01 + B02)": abs(eb.loc["B03", "valeur"] - eb.loc["B02", "valeur"] / (eb.loc["B01", "valeur"] + eb.loc["B02", "valeur"])) < tol,
        "B05 = B04 / B02": abs(eb.loc["B05", "valeur"] - eb.loc["B04", "valeur"] / eb.loc["B02", "valeur"]) < tol,
        "0 < HHI <= 1": 0 < eb.loc["B06", "valeur"] <= 1,
    }
    return pd.Series(c, name="conforme")


def afficher_etat(e):
    """Met en forme un état (montants en k€, ratios en %, indice à 3 décimales, effectif entier)."""
    pc, k3, ent = {"A05", "A06", "B03", "B05"}, {"B06"}, {"B07"}
    def f(c, v):
        if c in pc:
            return pct(v, 1)
        if c in k3:
            return fr(v, 3)
        if c in ent:
            return fr(v, 0)
        return fr(v / 1e3, 0) + "\u202fk\u20ac"
    return pd.DataFrame({"libelle": e["libelle"], "valeur": [f(c, v) for c, v in zip(e.index, e["valeur"])]})


# ----------------------------------------------------------------------------------------------- figures
def _pl():
    import matplotlib.pyplot as plt
    S.setup()
    plt.rcParams["axes.axisbelow"] = True
    return plt


def fig_triangle(d, nom="ch04-triangle.png"):
    plt = _pl()
    _, cum = triangle(d)
    f, t = chain_ladder(cum)
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    v = cum.to_numpy() / 1e6
    im = ax.imshow(np.ma.masked_invalid(v), cmap=S.SEQ, aspect="auto")
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            if np.isnan(v[i, j]):
                ax.text(j, i, "futur", ha="center", va="center", color=S.MUET, fontsize=8)
            else:
                ax.text(j, i, fr(v[i, j], 2), ha="center", va="center", color="white" if v[i, j] > 2.2 else S.ENCRE, fontsize=9)
    ax.set_xticks(range(cum.shape[1]), [f"délai {k}" for k in cum.columns])
    ax.set_yticks(range(cum.shape[0]), [str(a) for a in cum.index])
    ax.set_xlabel("années écoulées depuis l'année de survenance")
    ax.set_ylabel("année de survenance")
    ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_title("Paiements cumulés (M€) : la partie basse droite est l'avenir", loc="left")
    S.save(fig, nom)


def fig_sp_annee_classe(d, nom="ch04-sp-annee-classe.png"):
    plt = _pl()
    f, r = comparer_provisions(d)
    pr = d["ex"].groupby("annee")["prime_acquise"].sum()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.9), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    x = np.arange(len(r))
    ax.plot(x, 100 * r["charge_dossiers"] / pr, "o-", color=S.MUET, label="dossiers (payé + réserves)")
    ax.plot(x, 100 * r["ultime_cl"] / pr, "o-", color=S.BLEU, label="chain ladder")
    ax.plot(x, 100 * r["ultime_vrai"] / pr, "s--", color=S.ORANGE, label="vérité (inconnue en pratique)")
    ax.set_xticks(x, [str(a) for a in r.index])
    ax.set_ylabel("sinistres / primes acquises (%)")
    ax.set_title("Le S/P monte chaque année", loc="left")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_ylim(50, 95)
    ax = axes[1]
    t = table_sp(d, "classe_age").loc[["< 25 ans", "25-39 ans", "40-59 ans", "60 ans et +"]]
    cols = [S.ROUGE if v > 1 else S.BLEU for v in t["sp"]]
    ax.bar(range(4), 100 * t["sp"], color=cols, width=0.6)
    ax.axhline(100 - 100 * FRAIS, color=S.ENCRE2, lw=0.9, ls="--")
    ax.text(3.45, 100 - 100 * FRAIS + 2, "équilibre technique (S/P = 72 %)", ha="right", fontsize=8, color=S.ENCRE2)
    for i, v in enumerate(t["sp"]):
        ax.text(i, 100 * v + 2, pct(v, 0), ha="center", fontsize=9, color=S.ENCRE)
    ax.set_xticks(range(4), ["< 25", "25-39", "40-59", "60 et +"])
    ax.set_xlabel("âge du conducteur")
    ax.set_title("Les moins de 25 ans perdent de l'argent", loc="left")
    ax.set_ylim(0, 120)
    S.save(fig, nom)


def fig_zone_gros(d, nom="ch04-zone-gros-sinistre.png"):
    plt = _pl()
    a, b = sp_par_segment(d, "zone"), sp_par_segment(d, "zone", ecreter=50000)
    ia, ib = ic_sp(d, "zone"), ic_sp(d, "zone", ecreter=50000)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    x = np.arange(4)
    for off, v, ic, col, lab in [(-0.19, a, ia, S.ORANGE, "coût brut"), (0.19, b, ib, S.BLEU, "chaque sinistre plafonné à 50 000 €")]:
        ax.bar(x + off, 100 * v, 0.36, color=col, label=lab)
        ax.errorbar(x + off, 100 * v, yerr=[100 * (v - ic["bas"]), 100 * (ic["haut"] - v)], fmt="none", ecolor=S.ENCRE2, lw=1, capsize=3)
        for i in range(4):
            ax.text(i + off + 0.05, 100 * ic["haut"].iloc[i] + 1.5, f"{100 * v.iloc[i]:.0f}", ha="left", fontsize=8.5)
    ax.set_xticks(x, [f"zone {z}" for z in a.index])
    ax.set_ylabel("S/P 2021-2024 (%), intervalle à 90 %")
    ax.set_ylim(0, 120)
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("Quelques gros sinistres suffisent à faire d'une zone « la pire »", loc="left")
    S.save(fig, nom)


def fig_glm(d, nom="ch04-glm-age.png"):
    plt = _pl()
    mod, _ = glm_frequence(d)
    r = relativites(mod, "classe_age", "40-59 ans").loc[["40-59 ans", "60 ans et +", "25-39 ans", "< 25 ans"]]
    tarif = pd.Series({"40-59 ans": 1.0, "60 ans et +": 0.95 / 0.8, "25-39 ans": 1.0 / 0.8, "< 25 ans": 1.6 / 0.8})
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    y = np.arange(len(r))
    ax.errorbar(r["rapport"], y + 0.12, xerr=[r["rapport"] - r["bas"], r["haut"] - r["rapport"]], fmt="o", color=S.BLEU, capsize=3, label="fréquence estimée (GLM, IC 95 %)")
    ax.plot(tarif.loc[r.index], y - 0.12, "D", color=S.ORANGE, label="écart de prix du tarif")
    ax.set_yticks(y, r.index)
    ax.axvline(1, color=S.AXE, lw=0.8)
    ax.set_xlabel("rapport à la tranche 40-59 ans (toutes choses égales par ailleurs)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("Le risque des moins de 25 ans est près de 3 fois celui des 40-59 ans, le tarif le fait payer 2 fois", loc="left", fontsize=9.5)
    S.save(fig, nom)


def fig_cohortes(d, nom="ch04-cohortes.png"):
    plt = _pl()
    brut = defauts_par_millesime_brut(d)
    c = courbes_cohortes(d)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw={"width_ratios": [0.8, 1.2]})
    ax = axes[0]
    ax.bar(range(len(brut)), 100 * brut, color=S.MUET)
    ax.set_xticks(range(len(brut)), [m.replace(" ", "\n") for m in brut.index], fontsize=8)
    ax.set_ylabel("prêts passés en défaut (%)")
    ax.set_title("Taux brut : le récent a l'air sain", loc="left")
    ax = axes[1]
    pal = {"2022 S1": "#cde2fb", "2022 S2": "#86b6ef", "2023 S1": "#3987e5", "2023 S2": "#256abf", "2024 S1": S.ROUGE, "2024 S2": S.ORANGE, "2025 S1": S.AQUA}
    for m in c.columns:
        s_ = c[m].dropna()
        ax.plot(s_.index, 100 * s_, color=pal.get(m, S.MUET), lw=2.6 if m == "2024 S1" else 1.6, label=m)
    ax.set_xlabel("âge du prêt (mois)")
    ax.set_ylabel("défaut cumulé (%)")
    ax.set_title("À âge égal : le millésime 2024 S1 se détache", loc="left")
    ax.legend(ncol=2, fontsize=8, loc="upper left")
    S.save(fig, nom)


def fig_transitions(d, nom="ch04-transitions.png"):
    plt = _pl()
    n, p = matrice_transition(d)
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    ax.imshow(p.to_numpy(), cmap=S.SEQ, vmin=0, vmax=1, aspect="auto")
    for i in range(p.shape[0]):
        for j in range(p.shape[1]):
            v = p.iloc[i, j]
            ax.text(j, i, "" if v == 0 else (f"{100 * v:.1f}".replace(".", ",") + " %"), ha="center", va="center", color="white" if v > 0.5 else S.ENCRE, fontsize=8.5)
    ax.set_xticks(range(p.shape[1]), p.columns)
    ax.set_yticks(range(p.shape[0]), [f"{b}\n(n = {fr(n.loc[b].sum(), 0)})" for b in p.index], fontsize=8)
    ax.set_xlabel("tranche de retard le mois suivant")
    ax.set_ylabel("tranche de retard ce mois-ci")
    ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_title("Un retard de 30 à 59 jours bascule 2 fois sur 5 vers 60-89 jours", loc="left", fontsize=9.5)
    S.save(fig, nom)


def fig_secteurs(d, nom="ch04-secteurs.png"):
    plt = _pl()
    g = risque_secteur(d)
    sect = ["Commerce", "Restauration", "Bâtiment", "Services", "Industrie", "Particuliers"]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    y = np.arange(len(sect))
    for off, per, col, lab in [(0.18, "avant", S.MUET, "2024"), (-0.18, "apres", S.ROUGE, "2025")]:
        x = g[g["periode"] == per].set_index("secteur").loc[sect]
        ax.barh(y + off, 100 * x["taux"], 0.34, xerr=196 * x["se"], color=col, label=lab, error_kw=dict(lw=1, capsize=2, ecolor=S.ENCRE2))
    ax.set_yticks(y, sect)
    ax.invert_yaxis()
    ax.set_xlabel("défauts par an pour 100 prêts (IC 95 %)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("Commerce et Restauration se dégradent en 2025", loc="left")
    ax = axes[1]
    c = concentration(d, "2025-06-01")
    ax.barh(range(len(c)), 100 * c, color=S.BLEU)
    for i, v in enumerate(c):
        ax.text(100 * v + 1, i, pct(v, 0), va="center", fontsize=8.5)
    ax.set_yticks(range(len(c)), c.index)
    ax.invert_yaxis()
    ax.set_xlabel("part de l'encours sain au 30 juin 2025 (%)")
    ax.set_xlim(0, 70)
    ax.set_title(f"Concentration (HHI = {hhi(c):.2f}".replace(".", ",") + ")", loc="left")
    S.save(fig, nom)


def fig_alertes(d, nom="ch04-alertes.png"):
    plt = _pl()
    m, tr, te, coef = modele_alerte(d)
    ks = (10, 25, 50, 100, 150, 200, 300, 400)
    ev = evaluer_topk(te, ks)
    r = te[te["jours_retard"] >= 30]
    prec_r, rap_r = r["y"].mean(), r["y"].sum() / te["y"].sum()
    mois_n = te["mois"].nunique()
    rap_r_mois = r["y"].sum() / mois_n / (te["y"].sum() / mois_n)
    a = delai_anticipation(te, 100)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))
    ax = axes[0]
    ax.plot(ev.index, 100 * ev["precision"], "o-", color=S.BLEU, label="précision (parmi les k examinés)")
    ax.plot(ev.index, 100 * ev["rappel"], "s-", color=S.ORANGE, label="rappel (parmi les défauts à venir)")
    ax.plot([len(r) / mois_n], [100 * prec_r], "D", color=S.ROUGE, label=f"règle 30 j : précision {100 * prec_r:.0f} %")
    ax.plot([len(r) / mois_n], [100 * rap_r_mois], "D", color=S.ROUGE, mfc="white", label=f"règle 30 j : rappel {100 * rap_r_mois:.0f} %")
    ax.axhline(100 * (1 - 0.288), color=S.MUET, lw=0.8, ls=":")
    ax.text(398, 100 * (1 - 0.288) + 1.5, "plafond du rappel :\n29 % de défauts brutaux", ha="right", fontsize=7.5, color=S.MUET)
    ax.set_xlabel("nombre de prêts examinés chaque mois (k)")
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.legend(loc="lower right", fontsize=7.5)
    ax.set_title("Précision et rappel selon la charge du comité", loc="left")
    ax = axes[1]
    ax.hist(a, bins=np.arange(0.5, 7.5, 1), color=S.BLEU, rwidth=0.85)
    ax.set_xlabel("mois d'avance de la première alerte sur le défaut")
    ax.set_ylabel("prêts")
    ax.set_title(f"Délai d'anticipation (médiane {int(a.median())} mois)", loc="left")
    S.save(fig, nom)


def _boite(ax, x, y, w, h, texte, fc="#eef4fc", ec=S.BLEU, fs=9):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=fs, color=S.ENCRE)


def fig_flux(nom="ch04-flux-reporting.png"):
    plt = _pl()
    fig, ax = plt.subplots(figsize=(10.2, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    ax.grid(False)
    bl = [(0.1, "Systèmes\nsources\n(gestion, compta)"), (2.0, "Extraction\net contrôles\nd'entrée"), (3.9, "Calculs\nversionnés\n(définitions)"), (5.8, "Rapprochement\navec la compta\n+ revue à 4 yeux"), (7.7, "Publication\n(état, tableau\nde bord)")]
    for x, t in bl:
        _boite(ax, x, 1.5, 1.7, 1.3, t)
    for i in range(4):
        ax.annotate("", (bl[i + 1][0], 2.15), (bl[i][0] + 1.7, 2.15), arrowprops=dict(arrowstyle="->", color=S.ENCRE2, lw=1.3))
    _boite(ax, 2.0, 0.1, 5.6, 0.8, "Journal des exécutions : version du code, date des données,\nrésultats des contrôles, qui a validé", fc="#fdf0ea", ec=S.ORANGE, fs=8.5)
    for x in (2.85, 4.75, 6.65):
        ax.annotate("", (x, 0.92), (x, 1.5), arrowprops=dict(arrowstyle="->", color=S.ORANGE, lw=1))
    ax.text(0.1, 3.15, "Reporting de gestion ou réglementaire : la chaîne est la même, seules changent les définitions et les échéances", fontsize=9.5, color=S.ENCRE)
    S.save(fig, nom)


def fig_etat(d, nom="ch04-maquette-etat.png"):
    plt = _pl()
    k = kpi_assureur(d, 2024)
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    ax.axis("off")
    ax.grid(False)
    lignes = [["A01", "Primes acquises", fr(k["primes"] / 1e3, 0) + " k€"], ["A02", "Coût ultime estimé des sinistres", fr(k["sp"] * k["primes"] / 1e3, 0) + " k€"],
              ["A03", "Frais (28 % des primes)", fr(FRAIS * k["primes"] / 1e3, 0) + " k€"], ["A04", "Résultat technique (A01 − A02 − A03)", fr((1 - k["sp"] - FRAIS) * k["primes"] / 1e3, 0) + " k€"],
              ["A05", "Ratio S/P (A02 / A01)", pct(k["sp"], 1)], ["A06", "Ratio combiné ((A02 + A03) / A01)", pct(k["combine"], 1)]]
    t = ax.table(cellText=lignes, colLabels=["Case", "Libellé (maquette fictive)", "Montant"], colWidths=[0.12, 0.6, 0.22], loc="center", cellLoc="left")
    t.auto_set_font_size(False)
    t.set_fontsize(9.5)
    t.scale(1, 1.75)
    for (i, j), c in t.get_celld().items():
        c.set_edgecolor(S.AXE)
        if i == 0:
            c.set_facecolor("#e8eef8")
            c.set_text_props(weight="bold")
        elif j == 2:
            c._loc = "right"
    ax.set_title("État de gestion (maquette générique, année 2024) : chaque case a un numéro, une définition et un contrôle", loc="left", fontsize=9.5)
    S.save(fig, nom)


if __name__ == "__main__":
    D = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
    ecrire_donnees(D)
    print("écrit : ch04-compta-primes.csv, ch04-regularisations.csv")
