"""Outils du chapitre 4 (volume III) : segmentation, cohortes, RFM, rétention, entonnoir. Partagés par le livre (blocs cachés) et le cahier.

Convention : la date d'observation est le 31/12/2025 ; la boutique n'a de commandes que de 2023 à 2025 (les 4 000 clients inscrits avant 2023 sont
« déjà là » : on ne connaît pas leur première commande). Les figures reprennent le style de `build/style.py`.
"""
import os
import numpy as np
import pandas as pd

FIN = pd.Timestamp("2025-12-31")
DONNEES = os.environ.get("DONNEES", "donnees")


def charger(d=None):
    """retourne un dictionnaire de tables : cli, cmd (avec `ca` et `promo`), lig (avec `retourne`), prod, sess"""
    d = d or DONNEES
    cli = pd.read_csv(os.path.join(d, "clients.csv"), parse_dates=["date_inscription"])
    cmd = pd.read_csv(os.path.join(d, "commandes.csv"), parse_dates=["date_commande"])
    lig = pd.read_csv(os.path.join(d, "lignes_commande.csv"))
    prod = pd.read_csv(os.path.join(d, "produits.csv"))
    ret = pd.read_csv(os.path.join(d, "retours.csv"))
    sess = pd.read_csv(os.path.join(d, "sessions_web.csv"))
    cmd["ca"] = cmd["id_commande"].map(lig.groupby("id_commande")["montant"].sum())
    cmd["promo"] = cmd["code_promo"].notna()
    lig["retourne"] = lig["id_ligne"].isin(ret["id_ligne"])
    return dict(cli=cli, cmd=cmd, lig=lig, prod=prod, sess=sess)


def table_clients(cmd, lig, fin=FIN):
    """une ligne par client ayant au moins une commande avant `fin` : fréquence, montant, panier, récence, part du Site, part de commandes avec code promo, taux de retour"""
    c = cmd[cmd["date_commande"] <= fin]
    g = c.groupby("id_client").agg(n=("id_commande", "size"), ca=("ca", "sum"), der=("date_commande", "max"), prem=("date_commande", "min"),
                                   site=("canal", lambda s: (s == "Site").mean()), promo=("promo", "mean"))
    g["panier"] = g["ca"] / g["n"]
    g["rec"] = (fin - g["der"]).dt.days
    l = lig.merge(c[["id_commande", "id_client"]], on="id_commande")
    g["taux_ret"] = l.groupby("id_client")["retourne"].mean()
    return g


def variables_kmeans(g):
    """les cinq variables de la segmentation, après transformation logarithmique des variables très asymétriques"""
    return pd.DataFrame({"ln_commandes": np.log(g["n"]), "ln_panier": np.log(g["panier"]), "ln_recence": np.log1p(g["rec"]),
                         "part_site": g["site"], "part_promo": g["promo"]}, index=g.index)


def matrice_cohortes(cli, cmd, pas="Q", debut="2023-01-01"):
    """cohortes d'acquisition (période d'inscription) des clients inscrits depuis `debut` ; retourne (effectifs, taux d'activité, CA par client) :
    lignes = cohortes, colonnes = âge en périodes depuis l'inscription (0 = période d'inscription) ; NaN = pas encore observé (troncature à droite)"""
    new = cli[cli["date_inscription"] >= debut].set_index("id_client")
    coh = new["date_inscription"].dt.to_period(pas)
    c = cmd[cmd["id_client"].isin(new.index)].copy()
    c["coh"] = c["id_client"].map(coh)
    c["per"] = c["date_commande"].dt.to_period(pas)
    c["age"] = (c["per"] - c["coh"]).apply(lambda x: x.n)
    eff = coh.value_counts().sort_index()
    actifs = c.groupby(["coh", "age"])["id_client"].nunique().unstack()
    rev = c.groupby(["coh", "age"])["ca"].sum().unstack()
    derniere = pd.Period(FIN, pas)
    for k in eff.index:
        maxage = (derniere - k).n
        for a in actifs.columns:
            if a > maxage:
                actifs.loc[k, a] = np.nan
                rev.loc[k, a] = np.nan
    taux = actifs.div(eff, axis=0)
    ca_client = rev.div(eff, axis=0)
    return eff, taux, ca_client


def rfm(g, fin=FIN):
    """scores R, F, M de 1 (faible) à 5 (fort) par quintiles ; la fréquence est classée par rang (beaucoup d'ex æquo)"""
    s = pd.DataFrame(index=g.index)
    s["R"] = pd.qcut(g["rec"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    s["F"] = pd.qcut(g["n"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    s["M"] = pd.qcut(g["ca"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return s


def nom_segment_rfm(r, f):
    """segments nommés à partir des scores de récence et de fréquence (grille classique)"""
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Fidèles"
    if r >= 4 and f <= 2:
        return "Nouveaux ou récents"
    if r <= 2 and f >= 4:
        return "À risque (gros clients)"
    if r <= 2 and f <= 2:
        return "Perdus"
    return "À surveiller"


def reachat(cmd, t0, horizon_jours=184):
    """à la date t0 : pour chaque client déjà client, récence (jours depuis la dernière commande) et indicateur d'une commande dans les `horizon_jours` suivants"""
    t0 = pd.Timestamp(t0)
    av = cmd[cmd["date_commande"] <= t0].groupby("id_client")["date_commande"].max()
    ap = cmd[(cmd["date_commande"] > t0) & (cmd["date_commande"] <= t0 + pd.Timedelta(days=horizon_jours))].groupby("id_client").size()
    df = pd.DataFrame({"rec": (t0 - av).dt.days})
    df["reachete"] = df.index.map(lambda i: i in ap.index).astype(int)
    return df


def entonnoir(sess, par=None):
    """effectifs et taux de passage de chaque étape de l'entonnoir (sessions, ajout au panier, début de paiement, commande), éventuellement par groupe"""
    cols = ["ajout_panier", "debut_paiement", "commande"]
    if par is None:
        t = sess[cols].sum().to_frame().T
        t.insert(0, "sessions", len(sess))
    else:
        t = sess.groupby(par)[cols].sum()
        t.insert(0, "sessions", sess.groupby(par).size())
    t["taux_panier"] = t["ajout_panier"] / t["sessions"]
    t["taux_paiement"] = t["debut_paiement"] / t["ajout_panier"]
    t["taux_commande"] = t["commande"] / t["debut_paiement"]
    t["conversion"] = t["commande"] / t["sessions"]
    return t


def ic_proportion(k, n, z=1.96):
    """intervalle de Wilson d'une proportion"""
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def nommer_segments(g, lab):
    """donne un nom à chaque segment de k-moyennes d'après son profil moyen (4 segments attendus) ; retourne une Series alignée sur g"""
    prof = g.assign(s=lab).groupby("s")[["n", "promo", "site"]].mean()
    noms = {prof["n"].idxmax(): "Réguliers actifs"}
    r = prof.drop(index=prof["n"].idxmax())
    noms[r["promo"].idxmax()] = "Chasseurs de promotions"
    r = r.drop(index=r["promo"].idxmax())
    noms[r["site"].idxmax()] = "Dormants du Site"
    noms[r["site"].idxmin()] = "Dormants de la Boutique"
    return pd.Series(lab, index=g.index).map(noms)


# ------------------------------------------------------------------------------------------------------------------ figures
def _style():
    import style
    style.setup()
    return style


def fig_coude(inerties, silhouettes, ks, nom="ch04-coude-silhouette.png"):
    import matplotlib.pyplot as plt
    st = _style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.2, 3.2))
    a.plot(ks, inerties, "o-", color=st.BLEU)
    a.set_xlabel("nombre de segments k"); a.set_ylabel("inertie (somme des carrés intra)"); a.set_title("Le coude : pas de cassure nette")
    b.plot(ks, silhouettes, "o-", color=st.ORANGE)
    k_best = ks[int(np.argmax(silhouettes))]
    b.axvline(k_best, color=st.MUET, ls=":")
    b.annotate(f"maximum : k = {k_best}", (k_best, max(silhouettes)), xytext=(k_best + 0.4, max(silhouettes) - 0.012), color=st.ENCRE2)
    b.set_xlabel("nombre de segments k"); b.set_ylabel("silhouette moyenne"); b.set_title("La silhouette : une structure faible")
    fig.tight_layout()
    st.save(fig, nom)


def fig_profils(profil_z, tailles, nom="ch04-profils-segments.png"):
    """carte de chaleur des moyennes standardisées par segment (lignes = segments, colonnes = variables)"""
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    v = np.abs(profil_z.values).max()
    im = ax.imshow(profil_z.values, cmap=st.DIV, vmin=-v, vmax=v, aspect="auto")
    ax.set_xticks(range(profil_z.shape[1])); ax.set_xticklabels(profil_z.columns, rotation=0)
    ax.set_yticks(range(profil_z.shape[0])); ax.set_yticklabels([f"{i} ({tailles[i]} clients)" for i in profil_z.index])
    for i in range(profil_z.shape[0]):
        for j in range(profil_z.shape[1]):
            ax.text(j, i, (f"{profil_z.values[i, j]:+.1f}" if round(profil_z.values[i, j], 1) != 0 else "0.0").replace(".", ","), ha="center", va="center", color="white" if abs(profil_z.values[i, j]) > 0.9 * v else st.ENCRE, fontsize=9)
    ax.grid(False)
    ax.set_title("Écart à la moyenne générale, en écarts-types")
    fig.colorbar(im, ax=ax, fraction=0.03)
    st.save(fig, nom)


def fig_cohortes(taux, eff, nom="ch04-cohortes-retention.png", titre="Part des clients de la cohorte ayant commandé, par trimestre depuis l'inscription"):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    M = taux.values * 100
    im = ax.imshow(M, cmap=st.SEQ, vmin=10, vmax=50, aspect="auto")
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(taux.columns)
    ax.set_yticks(range(M.shape[0])); ax.set_yticklabels([f"{c} (n = {eff[c]})" for c in taux.index], fontsize=8.5)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", color="white" if M[i, j] > 36 else st.ENCRE, fontsize=8)
    ax.grid(False)
    ax.set_xlabel("trimestres depuis l'inscription (0 = trimestre d'inscription)"); ax.set_title(titre, fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.03, label="%")
    st.save(fig, nom)


def fig_reachat(tb, nom="ch04-reachat.png"):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    ax.bar(range(len(tb)), tb["p"], color=[st.BLEU, st.BLEU, st.BLEU, st.ORANGE, st.ROUGE])
    ax.set_xticks(range(len(tb))); ax.set_xticklabels([f"{i}\n(n = {n})" for i, n in zip(tb.index, tb["n"])], fontsize=8.5)
    for i, p in enumerate(tb["p"]):
        ax.text(i, p + 1.5, f"{p:.0f} %", ha="center", color=st.ENCRE2)
    ax.set_ylim(0, 95); ax.set_ylabel("clients qui recommandent dans les 6 mois (%)"); ax.set_xlabel("jours écoulés depuis la dernière commande, au 30 juin 2025")
    ax.set_title("Un client silencieux n'est pas un client perdu")
    st.save(fig, nom)


def fig_entonnoir(tab, nom="ch04-entonnoir.png"):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    tab = tab.sort_values("conversion")
    y = np.arange(len(tab))
    w = 0.26
    ax.barh(y + w, tab["taux_panier"] * 100, w, color=st.MUET, label="session → panier")
    ax.barh(y, tab["taux_paiement"] * 100, w, color=st.AQUA, label="panier → paiement")
    ax.barh(y - w, tab["taux_commande"] * 100, w, color=st.BLEU, label="paiement → commande")
    ax.set_yticks(y); ax.set_yticklabels([f"{i}  (conversion {c * 100:.1f} %)".replace(".", ",") for i, c in zip(tab.index, tab["conversion"])])
    ax.set_xlabel("taux de passage à l'étape suivante (%)"); ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("Où l'on perd les visiteurs, selon la source")
    st.save(fig, nom)


def fig_validation(val, nom="ch04-validation-segments.png"):
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    cols = [st.BLEU, st.ORANGE, st.AQUA, st.VIOLET]
    ax.bar(range(len(val)), val["achat"], color=cols[:len(val)])
    ax.axhline(val.attrs["global"], color=st.MUET, ls="--")
    ax.text(len(val) - 0.5, val.attrs["global"] + 1.5, f"ensemble : {val.attrs['global']:.0f} %", ha="right", color=st.ENCRE2)
    ax.set_xticks(range(len(val))); ax.set_xticklabels([f"{i}\n(n = {n})" for i, n in zip(val.index, val["eff"])], fontsize=8.5)
    for i, p in enumerate(val["achat"]):
        ax.text(i, p + 1.5, f"{p:.0f} %", ha="center", color=st.ENCRE2)
    ax.set_ylim(0, 100); ax.set_ylabel("ont commandé au second semestre 2025 (%)")
    ax.set_title("Des segments construits au 30 juin prédisent le semestre suivant")
    st.save(fig, nom)


def fig_rfm(table, nom="ch04-rfm.png"):
    """grille récence × fréquence : effectifs par case"""
    import matplotlib.pyplot as plt
    st = _style()
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    ax.imshow(table.values, cmap=st.SEQ, aspect="equal")
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            ax.text(j, i, str(table.values[i, j]), ha="center", va="center", color="white" if table.values[i, j] > 0.6 * table.values.max() else st.ENCRE, fontsize=9)
    ax.set_xticks(range(table.shape[1])); ax.set_xticklabels(table.columns); ax.set_yticks(range(table.shape[0])); ax.set_yticklabels(table.index)
    ax.invert_yaxis(); ax.grid(False)
    ax.set_xlabel("score de fréquence F (5 = très fréquent)"); ax.set_ylabel("score de récence R (5 = très récent)")
    ax.set_title("Nombre de clients par couple (R, F)")
    st.save(fig, nom)


def fig_periodes(par_age, par_periode, nom="ch04-age-periode.png"):
    """taux d'activité moyen par âge (colonnes de la matrice) et par trimestre calendaire (diagonales)"""
    import matplotlib.pyplot as plt
    st = _style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.4, 3.2), sharey=True)
    a.plot(par_age.index, par_age.values, "o-", color=st.BLEU)
    a.set_title("Selon l'âge : plat après le premier trimestre"); a.set_xlabel("trimestres depuis l'inscription"); a.set_ylabel("clients actifs (%)")
    b.plot(range(len(par_periode)), par_periode.values, "o-", color=st.ORANGE)
    b.set_xticks(range(len(par_periode))); b.set_xticklabels([str(p) for p in par_periode.index], rotation=60, fontsize=8)
    b.set_title("Selon le trimestre civil : un pic chaque T4"); b.set_xlabel("trimestre civil")
    a.set_ylim(20, 50)
    fig.tight_layout()
    st.save(fig, nom)


def activite_par_periode(cli, cmd, debut="2023-01-01"):
    """taux d'activité des clients inscrits depuis `debut`, par trimestre civil (clients déjà inscrits avant le trimestre) : l'effet de PÉRIODE, lu sur les diagonales de la matrice"""
    new = cli[cli["date_inscription"] >= debut].set_index("id_client")
    coh = new["date_inscription"].dt.to_period("Q")
    c = cmd[cmd["id_client"].isin(new.index)].copy()
    c["per"] = c["date_commande"].dt.to_period("Q")
    c["age"] = (c["per"] - c["id_client"].map(coh)).apply(lambda x: x.n)
    actifs = c[c["age"] >= 1].groupby("per")["id_client"].nunique()
    exposes = pd.Series({p: int((coh < p).sum()) for p in actifs.index})
    return actifs / exposes


def fig_cohortes_presentable(taux, eff, nom="ch04-cohortes-presentable.png"):
    """version à montrer : seulement le rectangle observé pour toutes les cohortes retenues (8 cohortes, 8 trimestres), avec une ligne de moyenne et l'effectif"""
    import matplotlib.pyplot as plt
    st = _style()
    sub = taux.iloc[:8, :8] * 100
    moy = sub.mean()
    M = np.vstack([sub.values, moy.values])
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    im = ax.imshow(M, cmap=st.SEQ, vmin=10, vmax=50, aspect="auto")
    ax.set_xticks(range(8)); ax.set_xticklabels(["T" + str(i) for i in range(8)])
    ax.set_yticks(range(9)); ax.set_yticklabels([f"{c}  ({eff[c]})" for c in sub.index] + ["Moyenne"])
    for i in range(9):
        for j in range(8):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", color="white" if M[i, j] > 36 else st.ENCRE, fontsize=8.5, fontweight="bold" if i == 8 else "normal")
    ax.axhline(7.5, color="white", lw=3)
    ax.grid(False)
    ax.set_xlabel("trimestres depuis l'inscription (T0 : trimestre partiel)")
    ax.set_title("Clients ayant commandé, en % de la cohorte (taille entre parenthèses)", fontsize=10)
    st.save(fig, nom)
