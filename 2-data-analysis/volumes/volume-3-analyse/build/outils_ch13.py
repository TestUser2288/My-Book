"""Outils du chapitre 13 : un petit modèle du résultat annuel de la boutique, sa calibration sur 2025, la sensibilité, Monte-Carlo, scénarios.

Le modèle est volontairement petit (une quinzaine de paramètres) ; chaque paramètre est une variation **relative** (+0,05 = +5 %) autour de la situation de 2025,
sauf `retours_pts` (points de pourcentage du chiffre d'affaires TTC) et `elasticite` (nombre positif : une hausse de prix de 1 % retire `elasticite` % de commandes).
"""
import os
import numpy as np
import pandas as pd

D = os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")
TVA = 0.20
PART_REMISE_EN_STOCK = 0.85      # hypothèse : part des articles retournés qui peuvent être revendus (le coût d'achat est alors récupéré)


def charger():
    r = lambda f, **k: pd.read_csv(os.path.join(D, f), **k)
    return dict(cr=r("compte_resultat_mensuel.csv"), cmd=r("commandes.csv"), lig=r("lignes_commande.csv"), ret=r("retours.csv"), prod=r("produits.csv"),
                ses=r("sessions_web.csv"), camp=r("campagnes.csv"), liv=r("livraisons.csv"), jours=r("jours_exploitation.csv"))


def calibrer(T):
    """Retourne le dictionnaire des paramètres de base (2025), estimés sur les données."""
    cr, cmd, lig, ret, ses, camp = (T[k] for k in ["cr", "cmd", "lig", "ret", "ses", "camp"])
    x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande")
    x = x[x["date_commande"] >= "2025-01-01"]
    cmd25 = cmd[cmd["date_commande"] >= "2025-01-01"]
    b = {}
    ca = x["montant"].sum()
    b["ca_ttc"] = ca
    for c, k in (("Site", "site"), ("Boutique", "bou"), ("Réseaux", "res")):
        xs = x[x["canal"] == c]
        b[f"n_{k}"] = xs["id_commande"].nunique()
        b[f"panier_{k}"] = xs["montant"].sum() / b[f"n_{k}"]
    b["unites"] = x["quantite"].sum()
    b["articles_par_commande"] = b["unites"] / (b["n_site"] + b["n_bou"] + b["n_res"])
    cr25 = cr[cr["mois"].str.startswith("2025")]
    b["ca_ht_comptes"] = cr25["ca_ht"].sum()
    b["achats"] = cr25["achats"].sum()
    b["cout_unitaire"] = b["achats"] / b["unites"]
    # sessions par groupe : payantes (payant + réseaux sociaux) et autres
    pay = ses["source"].isin(["payant", "reseaux"])
    b["sessions_pay"], b["sessions_aut"] = int(pay.sum()), int((~pay).sum())
    b["conv_pay"] = ses.loc[pay, "commande"].sum() / b["sessions_pay"]
    b["conv_aut"] = ses.loc[~pay, "commande"].sum() / b["sessions_aut"]
    dep = camp.groupby("source")["depense"].sum()
    b["depense_pay"] = dep["payant"] + dep["reseaux"]
    b["depense_email"] = dep["email"]
    b["cout_session_pay"] = b["depense_pay"] / b["sessions_pay"]
    # charges : estimation des taux par régression sur les 36 mois (personnel) ou par ratio
    m = cr.copy()
    nb = cmd.assign(mois=cmd["date_commande"].str[:7])
    liv_cmd = nb[nb["canal"] != "Boutique"].groupby("mois").size()
    m["cmd_livrees"] = m["mois"].map(liv_cmd)
    A = np.column_stack([np.ones(len(m)), m["ca_ht"], (m["mois"].str[:4] == "2025").astype(float)])
    coef, *_ = np.linalg.lstsq(A, m["frais_personnel"], rcond=None)
    b["pers_fixe_mois"], b["pers_var"], b["pers_saut_2025"] = coef
    b["pers_fixe"] = 12 * (coef[0] + coef[2])
    b["cout_par_colis"] = (m["livraison"] * m["cmd_livrees"]).sum() / (m["cmd_livrees"] ** 2).sum()
    b["taux_bancaire"] = (cr25["frais_bancaires"].sum()) / ca
    b["loyers"], b["amort"], b["autres"] = cr25["loyers_charges"].sum(), cr25["amortissements"].sum(), cr25["autres_charges"].sum()
    b["resultat_comptes"] = cr25["resultat_exploitation"].sum()
    r25 = ret.merge(x[["id_ligne"]], on="id_ligne")
    b["taux_retour_ca"] = r25["montant_rembourse"].sum() / ca
    b["lignes_retournees"], b["lignes"] = len(r25), len(x)
    return b


def resultat(b, prix=0.0, elasticite=1.2, trafic=0.0, budget_pub=0.0, cout_pub=0.0, conv=0.0, panier=0.0, frequentation=0.0, volume=0.0, cout_achat=0.0,
             retours_pts=0.0, livraison=0.0, fixes=0.0, detail=False):
    """Résultat d'exploitation annuel APRÈS coût des retours, en € (hors taxe)."""
    V = (1 + prix) ** (-elasticite) * (1 + volume)
    s_pay = b["sessions_pay"] * (1 + budget_pub) / (1 + cout_pub) * (1 + trafic)
    s_aut = b["sessions_aut"] * (1 + trafic)
    n_site = (s_pay * b["conv_pay"] + s_aut * b["conv_aut"]) * (1 + conv) * V
    n_bou = b["n_bou"] * (1 + frequentation) * V
    n_res = b["n_res"] * V
    f = (1 + panier) * (1 + prix)
    ca_ttc = (n_site * b["panier_site"] + n_bou * b["panier_bou"] + n_res * b["panier_res"]) * f
    ca_ht = ca_ttc / (1 + TVA)
    unites = (n_site + n_bou + n_res) * b["articles_par_commande"] * (1 + panier)
    achats = unites * b["cout_unitaire"] * (1 + cout_achat)
    personnel = b["pers_fixe"] * (1 + fixes) + b["pers_var"] * ca_ht
    livr = b["cout_par_colis"] * (n_site + n_res) * (1 + livraison)
    banque = b["taux_bancaire"] * ca_ttc
    marketing = b["depense_pay"] * (1 + budget_pub) + b["depense_email"]
    fixes_autres = (b["loyers"] + b["amort"] + b["autres"]) * (1 + fixes)
    avant = ca_ht - achats - personnel - livr - banque - marketing - fixes_autres
    remb_ht = (b["taux_retour_ca"] + retours_pts / 100) * ca_ttc / (1 + TVA)
    ratio_cout = achats / ca_ht
    cout_retours = remb_ht * (1 - PART_REMISE_EN_STOCK * ratio_cout)
    res = avant - cout_retours
    if detail:
        return dict(commandes_site=n_site, commandes=n_site + n_bou + n_res, ca_ttc=ca_ttc, ca_ht=ca_ht, achats=achats, personnel=personnel, livraison=livr, frais_bancaires=banque,
                    marketing=marketing, charges_fixes=fixes_autres, resultat_avant_retours=avant, cout_retours=cout_retours, resultat=res)
    return res


# ---- Monte-Carlo ---------------------------------------------------------------------------------------------------------------------------------
PARAMS_MC = {  # (moyenne, écart-type) de la variation relative (ou des points pour retours_pts) ; justification dans le livre
    "trafic": (0.0, 0.06), "conv": (0.0, 0.044), "panier": (0.0, 0.021), "frequentation": (0.0, 0.04), "cout_achat": (0.02, 0.03),
    "cout_pub": (0.05, 0.10), "retours_pts": (0.0, 0.4), "livraison": (0.0, 0.05), "fixes": (0.03, 0.01)}


def tirages(n, seed, rho=0.0, params=None, elasticite=(0.6, 1.8)):
    """n tirages des paramètres incertains ; `rho` = corrélation entre trafic et conversion (copule gaussienne)."""
    rng = np.random.default_rng(seed)
    p = dict(PARAMS_MC if params is None else params)
    z = rng.standard_normal((n, len(p)))
    noms = list(p)
    i, j = noms.index("trafic"), noms.index("conv")
    z[:, j] = rho * z[:, i] + np.sqrt(1 - rho ** 2) * z[:, j]
    out = {k: p[k][0] + p[k][1] * z[:, c] for c, k in enumerate(noms)}
    out["elasticite"] = rng.uniform(*elasticite, n)
    return out


def resultat_vec(b, tir, **fixes):
    """Évalue `resultat` sur tous les tirages ; `fixes` impose des valeurs (ex. prix=-0.05)."""
    n = len(next(iter(tir.values())))
    res = np.empty(n)
    for k in range(n):
        args = {c: float(v[k]) for c, v in tir.items()}
        args.update(fixes)
        res[k] = resultat(b, **args)
    return res


def resultat_rapide(b, tir, **fixes):
    """Même calcul, vectorisé (numpy) : les formules de `resultat` s'appliquent telles quelles à des tableaux."""
    args = dict(tir)
    args.update(fixes)
    return resultat(b, **args)


def quantiles(r, qs=(0.1, 0.5, 0.9)):
    return {f"p{int(q * 100)}": float(np.quantile(r, q)) for q in qs}


# ---- « et si » tirés des données -------------------------------------------------------------------------------------------------------------------
def promo_longue(T, debut="2025-02-17", jours_extra=7):
    """Prolonger une promotion de `jours_extra` jours à partir de `debut` (période creuse, sans promotion en 2025)."""
    import statsmodels.formula.api as smf
    j = T["jours"].copy()
    j["mois"] = j["date"].str[5:7]
    mod = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + C(annee)", data=j.assign(annee=j["date"].str[:4])).fit()
    uplift = float(np.exp(mod.params["promo_active"]) - 1)
    ic = np.exp(mod.conf_int().loc["promo_active"].values) - 1
    cmd, lig, prod = T["cmd"], T["lig"], T["prod"]
    x = lig.merge(cmd[["id_commande", "date_commande", "code_promo"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
    x["marge"] = x["montant"] / (1 + TVA) - x["quantite"] * x["cout_achat"]
    o = x.groupby("id_commande").agg(marge=("marge", "sum"), code=("code_promo", "first"), date=("date_commande", "first")).reset_index()
    o["code"] = o["code"].fillna("")
    promo_jours = set(j.loc[j["promo_active"] == 1, "date"])
    sur_promo = o[o["date"].isin(promo_jours)]
    s = (sur_promo["code"] == "SOLDES").mean()
    m_sold = o.loc[o["code"] == "SOLDES", "marge"].mean()
    m_norm = o.loc[o["code"] == "", "marge"].mean()
    fin = (pd.Timestamp(debut) + pd.Timedelta(days=jours_extra - 1)).strftime("%Y-%m-%d")
    base = j[(j["date"] >= debut) & (j["date"] <= fin)]["nb_commandes"].sum()
    marge_promo_par_cmd = s * m_sold + (1 - s) * m_norm
    delta = base * (1 + uplift) * marge_promo_par_cmd - base * m_norm
    u_star = (m_norm - marge_promo_par_cmd) / marge_promo_par_cmd
    return dict(uplift=uplift, uplift_bas=float(ic[0]), uplift_haut=float(ic[1]), commandes_base=int(base), part_soldes=float(s), marge_normale=float(m_norm), marge_soldes=float(m_sold),
                marge_promo=float(marge_promo_par_cmd), delta=float(delta), seuil_uplift=float(u_star))


def transporteurs(T):
    l = T["liv"]
    l = l[l["date_commande"] >= "2025-01-01"]
    g = l.groupby("transporteur").agg(colis=("id_commande", "size"), abimes=("colis_abime", "mean"), retards=("retard", "mean"))
    return g


# ---- sensibilité ---------------------------------------------------------------------------------------------------------------------------------
LIBELLES = {"trafic": "Trafic du site (sessions)", "conv": "Taux de conversion du site", "panier": "Articles par commande", "prix": "Prix de vente", "frequentation": "Fréquentation de la boutique",
            "cout_achat": "Coût d'achat des produits", "cout_pub": "Coût d'une session payante", "retours_pts": "Taux de retour (points)", "livraison": "Coût de livraison par colis",
            "fixes": "Charges fixes (loyer, personnel fixe…)"}
PLAGES_UNIFORMES = {"trafic": 0.10, "conv": 0.10, "panier": 0.05, "prix": 0.05, "frequentation": 0.10, "cout_achat": 0.05, "cout_pub": 0.20, "retours_pts": 2.0, "livraison": 0.20, "fixes": 0.05}
PLAGES_DONNEES = {"trafic": 0.06, "conv": 0.044, "panier": 0.021, "prix": 0.05, "frequentation": 0.04, "cout_achat": 0.03, "cout_pub": 0.10, "retours_pts": 0.4, "livraison": 0.05, "fixes": 0.01}


def tornade(b, plages, **autour):
    """Pour chaque paramètre : effet sur le résultat (en € par rapport à la situation de référence) quand il passe à −plage puis à +plage."""
    ref = resultat(b, **autour)
    lignes = []
    for k, w in plages.items():
        bas = resultat(b, **{**autour, k: autour.get(k, 0.0) - w}) - ref
        haut = resultat(b, **{**autour, k: autour.get(k, 0.0) + w}) - ref
        lignes.append((k, LIBELLES[k], w, bas, haut, max(abs(bas), abs(haut))))
    d = pd.DataFrame(lignes, columns=["parametre", "libelle", "plage", "effet_bas", "effet_haut", "amplitude"])
    return d.sort_values("amplitude", ascending=False).reset_index(drop=True), ref


def seuil(f, a, c):
    from scipy.optimize import brentq
    return brentq(f, a, c)


# ---- scénarios -------------------------------------------------------------------------------------------------------------------------------------
SCENARIOS = {
    "central": dict(prix=0.03, trafic=0.04, panier=0.01, frequentation=0.02, cout_achat=0.02, cout_pub=0.05, fixes=0.03),
    "pessimiste": dict(prix=0.03, trafic=-0.08, conv=-0.06, panier=-0.02, frequentation=-0.08, cout_achat=0.05, cout_pub=0.20, retours_pts=1.5, fixes=0.04),
    "optimiste": dict(prix=0.03, trafic=0.12, conv=0.04, panier=0.03, frequentation=0.05, cout_achat=0.0, cout_pub=0.0, retours_pts=-0.5, fixes=0.02),
}
OPTIONS = {"Prix inchangé": dict(prix=0.0), "Indexation de 3 %": dict(prix=0.03), "Hausse de 5 %": dict(prix=0.05), "Baisse de 5 %": dict(prix=-0.05), "Indexation de 3 % et publicité +20 %": dict(prix=0.03, budget_pub=0.2)}
PARAMS_ANNEE_PROCHAINE = {**PARAMS_MC, "trafic": (0.04, 0.06), "panier": (0.01, 0.021), "frequentation": (0.02, 0.04)}
