"""Figures du chapitre 3 (Analyse multivariée) du volume II.
Usage : python3 build/fig_ch03.py [nom_de_fonction ...]   (sans argument : toutes les figures)"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style  # noqa: E402
from style import AQUA, BLEU, ENCRE2, MUET, ORANGE, ROUGE, VIOLET  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

style.setup()
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def enquete():
    q = pd.read_csv(os.path.join(RACINE, "donnees", "enquete_satisfaction.csv"))
    return q, q[[f"q{j}" for j in range(1, 9)]]


def acp_cov(M):
    w, V = np.linalg.eigh(np.cov(M, rowvar=False))
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    V = V * np.sign(V[np.abs(V).argmax(axis=0), np.arange(V.shape[1])])
    return w, V


def correlations_enquete():
    q, Q = enquete()
    R = Q.corr().to_numpy()
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    im = ax.imshow(R, cmap=style.DIV, vmin=-1, vmax=1)
    ax.set_xticks(range(8)); ax.set_yticks(range(8))
    ax.set_xticklabels(Q.columns); ax.set_yticklabels(Q.columns)
    ax.grid(False)
    for i in range(8):
        for j in range(8):
            ax.text(j, i, f"{R[i, j]:.2f}".replace("0.", ".") if i != j else "1", ha="center", va="center",
                    fontsize=8, color="white" if abs(R[i, j]) > 0.6 else style.ENCRE)
    ax.axhline(3.5, color="white", lw=2); ax.axvline(3.5, color="white", lw=2)
    ax.set_title("Corrélations entre les huit questions", pad=24)
    ax.text(1.5, -0.75, "produits", ha="center", color=BLEU, fontsize=9)
    ax.text(5.5, -0.75, "service", ha="center", color=ORANGE, fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8, label="corrélation")
    style.save(fig, "ch03-correlations-enquete.png")


def acp_2d():
    X = np.array([[4, 4], [5, 3], [6, 6], [7, 5], [8, 7]], float)
    m = X.mean(0)
    Xc = X - m
    w, V = np.linalg.eigh(np.cov(Xc, rowvar=False))
    o = np.argsort(w)[::-1]; w, V = w[o], V[:, o]
    V = V * np.sign(V[0])                       # axe 1 vers la droite
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    t = np.linspace(-3.4, 3.4, 2)
    ax.plot(m[0] + t * V[0, 0], m[1] + t * V[1, 0], color=BLEU, lw=2, zorder=2)
    ax.plot(m[0] + t * V[0, 1], m[1] + t * V[1, 1], color=VIOLET, lw=1.4, ls="--", zorder=2)
    proj = (Xc @ V[:, [0]]) @ V[:, [0]].T + m
    for (x, y), (px, py) in zip(X, proj):
        ax.plot([x, px], [y, py], color=MUET, lw=1, zorder=1)
    ax.scatter(*proj.T, color=BLEU, s=22, zorder=3, facecolor="white", linewidth=1.5)
    ax.scatter(*X.T, color=ORANGE, s=48, zorder=4)
    for lab, (x, y) in zip("ABCDE", X):
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(-9, 5), color=ENCRE2, fontsize=10)
    ax.scatter(*m, marker="+", color=style.ENCRE, s=90, zorder=5)
    ax.annotate("axe 1 : 90 % de la variance", (m[0] - 2.2 * V[0, 0], m[1] - 2.2 * V[1, 0]), xytext=(14, -22),
                textcoords="offset points", color=BLEU, fontsize=9)
    ax.annotate("axe 2 : 10 %", (m[0] + 1.9 * V[0, 1], m[1] + 1.9 * V[1, 1]), xytext=(6, 4),
                textcoords="offset points", color=VIOLET, fontsize=9)
    ax.set_xlabel("nombre de commandes dans l'année")
    ax.set_ylabel("panier moyen (dizaines de €)")
    ax.set_xlim(2.8, 9.2); ax.set_ylim(1.8, 8.6); ax.set_aspect("equal")
    ax.set_title("Cinq clientes et leurs axes principaux")
    style.save(fig, "ch03-acp-2d.png")


def acp_eboulis_biplot():
    q, Q = enquete()
    Z = ((Q - Q.mean()) / Q.std()).to_numpy()
    w, V = acp_cov(Z)
    n, p = Z.shape
    rng = np.random.default_rng(3)
    sim = np.array([np.sort(np.linalg.eigvalsh(np.corrcoef(rng.normal(size=(n, p)), rowvar=False)))[::-1] for _ in range(500)])
    seuil = np.percentile(sim, 95, axis=0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1, 1.15]})
    k = np.arange(1, 9)
    a1.plot(k, w, "o-", color=BLEU)
    a1.plot(k, seuil, "o--", color=MUET, ms=4, lw=1.4)
    a1.axhline(1, color=ROUGE, lw=1, ls=":")
    a1.text(8.1, 1.04, "Kaiser (1)", color=ROUGE, fontsize=8, ha="right", va="bottom")
    a1.text(7.9, seuil[-1] - 0.06, "seuil de l'analyse parallèle", color=MUET, fontsize=8, ha="right", va="top")
    a1.text(2.15, w[1] + 0.08, f"{w[1]:.2f}", color=BLEU, fontsize=8)
    a1.text(1.15, w[0] + 0.02, f"{w[0]:.2f}", color=BLEU, fontsize=8)
    a1.set_xlabel("rang de la composante"); a1.set_ylabel("valeur propre")
    a1.set_title("Éboulis : deux composantes dominent")
    a1.set_ylim(0, 3.2)
    T = Z @ V[:, :2]
    ech = np.random.default_rng(5).choice(n, 300, replace=False)
    a2.scatter(T[ech, 0], T[ech, 1], s=9, color=MUET, alpha=0.5, edgecolor="none")
    ch = V[:, :2] * np.sqrt(w[:2])
    echelle = 3.2
    for j, nom in enumerate(Q.columns):
        coul = BLEU if j < 4 else ORANGE
        a2.annotate("", xy=(ch[j, 0] * echelle, ch[j, 1] * echelle), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=coul, lw=1.4))
    for groupe, coul, dy in [(slice(0, 4), BLEU, 0.55), (slice(4, 8), ORANGE, -0.55)]:
        bout = ch[groupe].mean(0) * echelle
        a2.text(bout[0] + 0.25, bout[1] + dy, "q1 à q4" if coul == BLEU else "q5 à q8", color=coul, fontsize=10,
                ha="left", va="center", fontweight="bold")
    a2.axhline(0, color=style.AXE, lw=0.8); a2.axvline(0, color=style.AXE, lw=0.8)
    a2.set_xlabel(f"CP1 ({w[0] / w.sum():.0%} de la variance)")
    a2.set_ylabel(f"CP2 ({w[1] / w.sum():.0%})")
    a2.set_title("Plan CP1-CP2 : produits (bleu) et service (orange)")
    a2.set_xlim(-4.6, 4.6); a2.set_ylim(-4.6, 4.6)
    plt.tight_layout()
    style.save(fig, "ch03-acp-eboulis-biplot.png")


def varimax(L, gamma=1.0, iterations=100, tol=1e-9):
    p, k = L.shape
    T = np.eye(k); crit = 0.0
    for _ in range(iterations):
        Lr = L @ T
        u, s, vt = np.linalg.svd(L.T @ (Lr**3 - (gamma / p) * Lr @ np.diag((Lr**2).sum(axis=0))))
        T = u @ vt
        if s.sum() < crit * (1 + tol):
            break
        crit = s.sum()
    return L @ T, T


def af_rotation():
    from sklearn.decomposition import FactorAnalysis
    q, Q = enquete()
    Z = ((Q - Q.mean()) / Q.std()).to_numpy()
    L = FactorAnalysis(2, rotation=None, random_state=0).fit(Z).components_.T
    L = L * np.sign(L.sum(axis=0))            # signe : somme des saturations de chaque colonne positive
    Lr, T = varimax(L)
    # signes : plus grande saturation de chaque colonne positive
    Lr = Lr * np.sign(Lr[np.abs(Lr).argmax(axis=0), [0, 1]])
    # colonne 1 = produits si possible (pour une figure stable)
    if np.abs(Lr[:4, 0]).mean() < np.abs(Lr[:4, 1]).mean():
        Lr = Lr[:, ::-1]
        T = T[:, ::-1]
    names = list(Q.columns)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.9))
    for ax, M, titre, off in [(axes[0], L, "Avant rotation", (-105, 6)), (axes[1], Lr, "Après rotation varimax", (10, 12))]:
        for j in range(8):
            coul = BLEU if j < 4 else ORANGE
            ax.scatter(M[j, 0], M[j, 1], color=coul, s=40, zorder=3)
        # étiquettes de groupe plutôt que huit étiquettes superposées
        for g, coul, nom in [(slice(0, 4), BLEU, "q1 à q4"), (slice(4, 8), ORANGE, "q5 à q8")]:
            cx, cy = M[g].mean(0)
            ax.annotate(nom, (cx, cy), xytext=off if coul == BLEU else (10, -16), textcoords="offset points",
                        color=coul, fontsize=10, fontweight="bold")
        ax.axhline(0, color=style.AXE, lw=0.8); ax.axvline(0, color=style.AXE, lw=0.8)
        ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_box_aspect(1)
        ax.set_title(titre)
    axes[0].set_xlabel("facteur 1 (brut)"); axes[0].set_ylabel("facteur 2 (brut)")
    axes[1].set_xlabel("facteur 1 (produits)"); axes[1].set_ylabel("facteur 2 (service)")
    # axes tournés tracés sur la figure de gauche
    for j, (dx, dy) in enumerate(T.T):
        axes[0].plot([-dx * 0.9, dx * 0.9], [-dy * 0.9, dy * 0.9], color=MUET, lw=1.2, ls="--")
    axes[0].text(0.0, -0.93, "tirets : les axes après rotation", color=MUET, fontsize=8, ha="center")
    plt.tight_layout()
    style.save(fig, "ch03-af-rotation.png")


# ---------- chapitre 3.3 : classification ----------
def kmeans(X, k, rng, n_init=10, max_iter=100, journal=False):
    meilleur = None
    for _ in range(n_init):
        centres = [X[rng.integers(len(X))]]
        for _ in range(k - 1):
            d2 = ((X[:, None, :] - np.array(centres)[None, :, :]) ** 2).sum(axis=2).min(axis=1)
            centres.append(X[rng.choice(len(X), p=d2 / d2.sum())])
        centres = np.array(centres)
        etapes = [centres.copy()]
        for iteration in range(max_iter):
            d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
            groupes = d.argmin(axis=1)
            nouveaux = np.array([X[groupes == j].mean(axis=0) if (groupes == j).any() else centres[j] for j in range(k)])
            if np.allclose(nouveaux, centres):
                break
            centres = nouveaux
            etapes.append(centres.copy())
        W = ((X - centres[groupes]) ** 2).sum()
        if meilleur is None or W < meilleur["W"]:
            meilleur = {"W": W, "groupes": groupes, "centres": centres, "iterations": iteration + 1, "etapes": etapes}
    return meilleur


def donnees_sim():
    rng = np.random.default_rng(11)
    profils = {"occasionnelles": (300, (1.5, 35), (0.7, 8)),
               "fidèles": (200, (6.0, 50), (1.4, 10)),
               "cadeaux": (100, (3.0, 110), (0.9, 15))}
    blocs, vrais = [], []
    for numero, (nom, (n_p, moyennes, ecarts)) in enumerate(profils.items()):
        blocs.append(rng.normal(moyennes, ecarts, size=(n_p, 2)))
        vrais += [numero] * n_p
    sim = np.vstack(blocs)
    sim[:, 0] = np.clip(sim[:, 0], 0, None)
    return sim, np.array(vrais), (sim - sim.mean(axis=0)) / sim.std(axis=0)


def donnees_clients():
    c = pd.read_csv(os.path.join(RACINE, "donnees", "clients.csv"))
    act = c[c["nb_commandes_an"] > 0].copy()
    var = ["nb_commandes_an", "panier_moyen", "duree_mois", "age"]
    return act, ((act[var] - act[var].mean()) / act[var].std()).to_numpy()


def kmeans_iterations():
    sim, vrais, Zs = donnees_sim()
    r = kmeans(Zs, 3, np.random.default_rng(0), n_init=1)
    etapes = r["etapes"] + [r["centres"]]
    choix = [0, 1, 2, len(etapes) - 1] if len(etapes) > 3 else list(range(len(etapes)))
    choix = sorted(set(choix))
    titres = {0: "initialisation (k-means++)"}
    fig, axes = plt.subplots(1, len(choix), figsize=(3.3 * len(choix), 3.6), sharex=True, sharey=True)
    for ax, e in zip(axes, choix):
        centres = etapes[e]
        lab = ((Zs[:, None, :] - centres[None]) ** 2).sum(axis=2).argmin(axis=1)
        for j, coul in enumerate([BLEU, ORANGE, AQUA]):
            ax.scatter(*Zs[lab == j].T, s=6, color=coul, alpha=0.55, edgecolor="none")
            ax.scatter(*centres[j], marker="D", s=70, color=coul, edgecolor=style.ENCRE, linewidth=1.2, zorder=5)
        ax.set_title(titres.get(e, "solution finale" if e == choix[-1] else f"étape {e}"), fontsize=10)
        ax.set_xlabel("commandes par an (standardisé)")
    axes[0].set_ylabel("panier moyen (standardisé)")
    plt.tight_layout()
    style.save(fig, "ch03-kmeans-iterations.png")


def choix_k():
    from sklearn.metrics import silhouette_score
    sim, vrais, Zs = donnees_sim()
    act, Zc = donnees_clients()
    res = {}
    for nom, Z, kmax in [("sim", Zs, 7), ("clients", Zc, 8)]:
        W, S = [], []
        for k in range(1, kmax + 1):
            r = kmeans(Z, k, np.random.default_rng(0), n_init=5)
            W.append(r["W"])
            S.append(silhouette_score(Z, r["groupes"]) if k > 1 else np.nan)
        res[nom] = (np.array(W), np.array(S))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
    for nom, coul, lab in [("sim", BLEU, "clientes simulées\n(3 vrais profils)"), ("clients", ORANGE, "clientes réelles")]:
        W, S = res[nom]
        k = np.arange(1, len(W) + 1)
        a1.plot(k, W / W[0], "o-", color=coul, ms=4)
        a2.plot(k[1:], S[1:], "o-", color=coul, ms=4)
        a1.text(k[-1] + 0.12, (W / W[0])[-1], lab, color=coul, fontsize=9, va="center")
        a2.text(k[-1] + 0.12, S[-1], lab, color=coul, fontsize=9, va="center")
    a1.set_xlim(0.7, 10.2); a2.set_xlim(1.7, 10.2)
    a1.set_xlabel("nombre de groupes k"); a1.set_ylabel("variance intra-groupe W(k) / W(1)")
    a1.set_title("Le coude : net seulement si les groupes existent")
    a2.set_xlabel("nombre de groupes k"); a2.set_ylabel("silhouette moyenne")
    a2.set_title("La silhouette : maximum franc au bon k")
    a2.set_ylim(0, 0.8)
    plt.tight_layout()
    style.save(fig, "ch03-choix-k.png")


def dendrogramme():
    from scipy.cluster.hierarchy import dendrogram, linkage, set_link_color_palette
    sim, vrais, Zs = donnees_sim()
    idx = np.random.default_rng(2).choice(len(Zs), 40, replace=False)
    L = linkage(Zs[idx], method="ward")
    seuil = (L[-3, 2] + L[-2, 2]) / 2
    set_link_color_palette([BLEU, ORANGE, AQUA])
    fig, ax = plt.subplots(figsize=(10, 4.2))
    dendrogram(L, color_threshold=seuil, above_threshold_color=MUET, no_labels=True, ax=ax)
    ax.axhline(seuil, color=ROUGE, ls="--", lw=1.2)
    ax.text(0.5, seuil + 0.4, "coupure : 3 groupes", color=ROUGE, fontsize=9)
    ax.set_ylabel("hauteur de fusion (critère de Ward)")
    ax.set_xlabel("40 clientes tirées au hasard")
    ax.grid(False)
    ax.set_title("Dendrogramme : deux grands sauts, donc trois groupes")
    style.save(fig, "ch03-dendrogramme.png")
    set_link_color_palette(None)


def lunes():
    from sklearn.cluster import AgglomerativeClustering, KMeans
    from sklearn.datasets import make_moons
    X, y = make_moons(n_samples=300, noise=0.07, random_state=0)
    km = KMeans(2, n_init=10, random_state=0).fit_predict(X)
    sg = AgglomerativeClustering(2, linkage="single").fit_predict(X)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, lab, titre in [(axes[0], km, "k-means : coupe chaque croissant"), (axes[1], sg, "hiérarchique, lien simple : suit la forme")]:
        for j, coul in enumerate([BLEU, ORANGE]):
            ax.scatter(*X[lab == j].T, s=12, color=coul, alpha=0.8, edgecolor="none")
        ax.set_title(titre, fontsize=10); ax.set_aspect("equal")
    plt.tight_layout()
    style.save(fig, "ch03-lunes.png")


def segments_clients():
    act, Zc = donnees_clients()
    r = kmeans(Zc, 4, np.random.default_rng(0), n_init=10)
    w, V = np.linalg.eigh(np.cov(Zc, rowvar=False))
    V = V[:, np.argsort(w)[::-1]]
    T = Zc @ V[:, :2]
    fig, ax = plt.subplots(figsize=(7, 5))
    for j, coul in enumerate([BLEU, ORANGE, AQUA, VIOLET]):
        ax.scatter(*T[r["groupes"] == j].T, s=7, color=coul, alpha=0.55, edgecolor="none")
        cx, cy = T[r["groupes"] == j].mean(axis=0)
        ax.text(cx, cy, str(j + 1), color="white", fontsize=11, fontweight="bold", ha="center", va="center",
                bbox=dict(boxstyle="circle,pad=0.3", fc=coul, ec="white"))
    ax.set_xlabel("composante principale 1"); ax.set_ylabel("composante principale 2")
    ax.set_title("Quatre segments tracés dans un nuage continu")
    style.save(fig, "ch03-segments-clients.png")


# ---------- chapitre 3.4 : correspondances ----------
def analyse_correspondances(N):
    N = np.asarray(N, dtype=float)
    P = N / N.sum()
    r, c = P.sum(axis=1), P.sum(axis=0)
    S = (P - np.outer(r, c)) / np.sqrt(np.outer(r, c))
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    return {"inertie": sv**2, "F": (U / np.sqrt(r)[:, None]) * sv, "G": (Vt.T / np.sqrt(c)[:, None]) * sv}


def clients_actifs():
    c = pd.read_csv(os.path.join(RACINE, "donnees", "clients.csv"))
    a = c[c["nb_commandes_an"] > 0].copy()
    a["tranche_panier"] = pd.qcut(a["panier_moyen"], 4, labels=["T1 très petit", "T2 petit", "T3 grand", "T4 très grand"])
    a["tranche_age"] = pd.cut(a["age"], [0, 29, 39, 200], labels=["moins de 30", "30-39", "40 et plus"])
    return a


def ca_carte():
    a = clients_actifs()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    for ax, (r, cn), titre, lim in [(axes[0], ("canal_acquisition", "tranche_panier"), "canal x panier : une association forte", 0.62),
                                    (axes[1], ("canal_acquisition", "ville"), "canal x ville : aucune association", 0.14)]:
        N = pd.crosstab(a[r], a[cn])
        ac = analyse_correspondances(N.values)
        boite = dict(boxstyle="round,pad=0.12", fc=style.SURFACE, ec="none", alpha=0.85)
        pts = [(nom, x, y, BLEU, "o") for nom, (x, y) in zip(N.index, ac["F"][:, :2])]
        pts += [(str(nom), x, y, ORANGE, "s") for nom, (x, y) in zip(N.columns, ac["G"][:, :2])]
        for nom, x, y, coul, marque in pts:
            ax.scatter(x, y, color=coul, s=60, marker=marque, zorder=3)
        # étiquettes : on alterne au-dessus / au-dessous en suivant l'ordre des abscisses
        for rang, (nom, x, y, coul, marque) in enumerate(sorted(pts, key=lambda t: t[1])):
            dy = 11 if rang % 2 == 0 else -17
            decal = {"Boutique": (0, 12), "Autre": (-6, 12), "Ville B": (-34, 0), "Ville C": (22, 9), "Site": (20, -15)} if cn == "ville" else {}
            ax.annotate(nom, (x, y), xytext=decal.get(nom, (0, dy)), textcoords="offset points", ha="center", color=coul,
                        fontsize=9, fontweight="bold" if marque == "o" else "normal", bbox=boite, zorder=4)
        ax.axhline(0, color=style.AXE, lw=0.8); ax.axvline(0, color=style.AXE, lw=0.8)
        part = 100 * ac["inertie"] / ac["inertie"].sum()
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_box_aspect(1)
        ax.set_xlabel(f"axe 1 ({part[0]:.0f} % de l'inertie)"); ax.set_ylabel(f"axe 2 ({part[1]:.0f} %)")
        ax.set_title(titre, fontsize=10)
        ax.text(0.02, 0.97, f"inertie totale = {ac['inertie'].sum():.3f}", transform=ax.transAxes, fontsize=8, color=MUET, va="top")
    plt.tight_layout()
    style.save(fig, "ch03-ca-carte.png")


def acm_coordonnees():
    a = clients_actifs()
    cols = ["canal_acquisition", "ville", "tranche_age", "tranche_panier", "offre_bienvenue", "rachat_12m"]
    D = pd.get_dummies(a[cols].astype(str), dtype=float)
    acm = analyse_correspondances(D.values)
    return cols, D, acm


def acm_carte():
    cols, D, acm = acm_coordonnees()
    G = acm["G"][:, :2]
    part = 100 * acm["inertie"] / acm["inertie"].sum()
    famille = [next(v for v in cols if m.startswith(v + "_")) for m in D.columns]
    couleurs = {"canal_acquisition": BLEU, "tranche_panier": VIOLET, "offre_bienvenue": ORANGE, "rachat_12m": AQUA,
                "tranche_age": ROUGE, "ville": MUET}
    fig, ax = plt.subplots(figsize=(8.6, 5.8))
    deplace = {"offre=0": (-48, 8), "offre=1": (-48, -14), "rachat=0": (6, 6), "rachat=1": (6, -14), "Site": (8, -16), "âge 30-39": (-78, 6)}
    for m, (x, y), fam in zip(D.columns, G, famille):
        coul = couleurs[fam]
        if fam == "ville":
            ax.scatter(x, y, color=coul, s=18, alpha=0.7, zorder=2)
            continue
        ax.scatter(x, y, color=coul, s=44, zorder=3)
        nom = (m.replace("canal_acquisition_", "").replace("tranche_panier_", "").replace("offre_bienvenue_", "offre=")
                .replace("rachat_12m_", "rachat=").replace("tranche_age_", "âge "))
        ax.annotate(nom, (x, y), xytext=deplace.get(nom, (6, 6)), textcoords="offset points", color=coul, fontsize=9, fontweight="bold")
    xv, yv = G[[i for i, f_ in enumerate(famille) if f_ == "ville"]].mean(axis=0)
    ax.annotate("points gris : les six villes\n(petits groupes, positions instables)", (G[famille.index("ville"), 0], G[famille.index("ville"), 1]),
                xytext=(26, 30), textcoords="offset points", color=MUET, fontsize=8)
    ax.axhline(0, color=style.AXE, lw=0.8); ax.axvline(0, color=style.AXE, lw=0.8)
    ax.set_xlabel(f"axe 1 ({part[0]:.0f} % de l'inertie)"); ax.set_ylabel(f"axe 2 ({part[1]:.0f} %)")
    ax.set_title("ACM : canal / panier sur l'axe 1, offre / rachat sur l'axe 2")
    style.save(fig, "ch03-acm-carte.png")


# ---------- chapitre 3.5 : discriminante ----------
def lda_frontieres():
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
    from matplotlib.colors import ListedColormap
    sim, vrais, Zs = donnees_sim()
    xx, yy = np.meshgrid(np.linspace(-1.9, 2.9, 400), np.linspace(-1.5, 3.9, 400))
    grille = np.c_[xx.ravel(), yy.ravel()]
    couleurs = [BLEU, ORANGE, AQUA]
    fond = ListedColormap(["#d3e3f8", "#fbd9cd", "#c8ecdf"])
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6), sharey=True)
    for ax, modele, nom in [(axes[0], LinearDiscriminantAnalysis(), "LDA : frontières droites"),
                            (axes[1], QuadraticDiscriminantAnalysis(), "QDA : frontières courbes")]:
        modele.fit(Zs, vrais)
        ax.contourf(xx, yy, modele.predict(grille).reshape(xx.shape), levels=[-0.5, 0.5, 1.5, 2.5], cmap=fond)
        for k, coul in enumerate(couleurs):
            ax.scatter(*Zs[vrais == k].T, s=6, color=coul, alpha=0.8, edgecolor="none")
        ax.set_title(f"{nom} (précision {100 * modele.score(Zs, vrais):.1f} %)".replace(".", ","), fontsize=10)
        ax.set_xlabel("commandes par an (standardisé)")
        ax.grid(False)
    axes[0].set_ylabel("panier moyen (standardisé)")
    for k, (x, y, nom) in enumerate([(-1.0, -1.44, "occasionnelles"), (1.7, -1.35, "fidèles"), (-0.2, 3.5, "cadeaux")]):
        axes[1].text(x, y, nom, color=couleurs[k], fontsize=9, fontweight="bold", ha="center")
    plt.tight_layout()
    style.save(fig, "ch03-lda-frontieres.png")


FIGS = {f.__name__: f for f in [correlations_enquete, acp_2d, acp_eboulis_biplot, af_rotation, kmeans_iterations, choix_k, dendrogramme, lunes, segments_clients, ca_carte, acm_carte, lda_frontieres]}

if __name__ == "__main__":
    for nom in (sys.argv[1:] or FIGS):
        FIGS[nom]()
