"""Outils du chapitre 7 (recommandation) : protocole d'évaluation et modèles de référence, en numpy/scipy uniquement.

Le livre et le cahier importent ce module pour le PROTOCOLE (découpage, métriques) ; les algorithmes eux-mêmes (cosinus, voisins,
moindres carrés alternés) sont écrits en clair dans le livre (formules) et dans le cahier (applications).

    from outils_ch07 import *            (après sys.path.insert(0, "build"))
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp

K_EVAL = 10


def charger():
    """Retourne (interactions, produits, R) ; R = matrice binaire clients x produits (csr), lignes = id_client - 1."""
    inter = pd.read_csv("donnees/interactions.csv")
    prod = pd.read_csv("donnees/produits_ml.csv")
    R = sp.csr_matrix((np.ones(len(inter)), (inter.id_client.values - 1, inter.id_produit.values - 1)), shape=(3000, 150))
    return inter, prod, R


def decouper(R, seed=7, min_items=5, part_test=0.25, part_val=0.20):
    """Retire au hasard, pour chaque client ayant au moins `min_items` achats, ~25 % de ses achats (test), puis ~20 % du reste (validation).
    Retourne un dict : R_train (sans test ni validation), R_trainval (sans test), test et val (matrices binaires des achats retirés),
    users (indices des clients évalués)."""
    rng = np.random.default_rng(seed)
    R = R.tocsr()
    lignes_t, cols_t, lignes_v, cols_v = [], [], [], []
    users = []
    for u in range(R.shape[0]):
        items = R.indices[R.indptr[u]:R.indptr[u + 1]]
        if len(items) < min_items:
            continue
        users.append(u)
        items = rng.permutation(items)
        n_t = max(1, int(round(part_test * len(items))))
        t, reste = items[:n_t], items[n_t:]
        n_v = max(1, int(round(part_val * len(reste))))
        v = reste[:n_v]
        lignes_t += [u] * len(t); cols_t += list(t); lignes_v += [u] * len(v); cols_v += list(v)
    forme = R.shape
    T = sp.csr_matrix((np.ones(len(cols_t)), (lignes_t, cols_t)), shape=forme)
    V = sp.csr_matrix((np.ones(len(cols_v)), (lignes_v, cols_v)), shape=forme)
    return {"R_train": (R - T - V).tocsr(), "R_trainval": (R - T).tocsr(), "test": T, "val": V, "users": np.array(users)}


# ------------------------------------------------------------------ modèles : chacun retourne une matrice de scores (clients x produits)
def cosinus_colonnes(M):
    """Similarité cosinus entre les colonnes (produits) d'une matrice creuse ; diagonale mise à zéro."""
    M = M.tocsc()
    norme = np.sqrt(np.asarray(M.multiply(M).sum(axis=0)).ravel())
    norme[norme == 0] = 1
    G = (M.T @ M).toarray() / np.outer(norme, norme)
    np.fill_diagonal(G, 0)
    return G


def scores_popularite(R):
    return np.tile(np.asarray(R.sum(axis=0)).ravel(), (R.shape[0], 1)).astype(float)


def scores_aleatoire(R, seed=0):
    return np.random.default_rng(seed).random(R.shape)


def scores_voisins_articles(R, k=20, shrink=0.0):
    """Item-item : similarité cosinus (avec rétrécissement n/(n+shrink) sur les co-achats), k plus proches voisins par produit."""
    S = cosinus_colonnes(R)
    if shrink > 0:
        co = (R.T @ R).toarray()
        S = S * co / (co + shrink)
    if k < S.shape[0]:
        seuil = -np.sort(-S, axis=1)[:, k - 1][:, None]
        S = np.where(S >= seuil, S, 0.0)
    return np.asarray(R @ S)


def scores_voisins_clients(R, k=50):
    """User-user : cosinus entre clients, k plus proches voisins ; score = somme des similarités des voisins ayant acheté."""
    R = R.tocsr()
    norme = np.sqrt(np.asarray(R.multiply(R).sum(axis=1)).ravel()); norme[norme == 0] = 1
    G = (R @ R.T).toarray() / np.outer(norme, norme)
    np.fill_diagonal(G, 0)
    seuil = -np.sort(-G, axis=1)[:, k - 1][:, None]
    G = np.where(G >= seuil, G, 0.0)
    return np.asarray(G @ R.toarray())


def scores_contenu(R, prod):
    """Contenu : profil du client = moyenne des caractéristiques (catégorie en indicatrices, log-prix centré réduit) de ses achats ; cosinus."""
    F = pd.get_dummies(prod["categorie"], dtype=float).to_numpy()
    lp = np.log(prod["prix"].to_numpy()); F = np.hstack([F, ((lp - lp.mean()) / lp.std())[:, None]])
    n = np.asarray(R.sum(axis=1)).ravel(); n[n == 0] = 1
    P = (R @ F) / n[:, None]
    nP = np.linalg.norm(P, axis=1, keepdims=True); nP[nP == 0] = 1
    nF = np.linalg.norm(F, axis=1, keepdims=True)
    return (P / nP) @ (F / nF).T


def als_implicite(R, k=10, lam=5.0, alpha=10.0, n_iter=12, seed=0):
    """Moindres carrés alternés pour retours implicites (confiance c = 1 + alpha * r). Retourne les facteurs (U, V)."""
    rng = np.random.default_rng(seed)
    R = R.tocsr(); Rt = R.T.tocsr()
    n, m = R.shape
    U = 0.1 * rng.standard_normal((n, k)); V = 0.1 * rng.standard_normal((m, k))

    def pas(A, F_fixe):
        FtF = F_fixe.T @ F_fixe + lam * np.eye(k)
        sortie = np.zeros((A.shape[0], k))
        for i in range(A.shape[0]):
            idx = A.indices[A.indptr[i]:A.indptr[i + 1]]
            if len(idx) == 0:
                continue
            Fi = F_fixe[idx]
            M = FtF + alpha * Fi.T @ Fi            # V'V + V'(C_u - I)V + lam I   avec c - 1 = alpha sur les achats
            b = (1 + alpha) * Fi.sum(axis=0)        # V' C_u p_u : confiance 1 + alpha sur les achats
            sortie[i] = np.linalg.solve(M, b)
        return sortie

    for _ in range(n_iter):
        U = pas(R, V)
        V = pas(Rt, U)
    return U, V


def scores_als(R, **kw):
    U, V = als_implicite(R, **kw)
    return U @ V.T


def scores_svd(R, k=10, seed=0):
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=k, random_state=seed)
    Z = svd.fit_transform(R)
    return Z @ svd.components_


# ------------------------------------------------------------------ métriques
def evaluer(S, R_connu, cible, users, k=K_EVAL):
    """Évalue un classement. S : scores (clients x produits) ; R_connu : achats déjà connus (exclus du classement) ;
    cible : matrice binaire des achats retirés. Retourne un DataFrame par client : precision, rappel, ap, ndcg, succes (>= 1 hit)."""
    S = np.array(S, dtype=float)[users]
    connu = R_connu.toarray()[users] > 0
    S[connu] = -np.inf
    rel = cible.toarray()[users] > 0
    # rang des produits par score décroissant (départage par l'indice : déterministe)
    ordre = np.argsort(-S, axis=1, kind="stable")[:, :k]
    hits = np.take_along_axis(rel, ordre, axis=1)
    n_rel = rel.sum(axis=1)
    precision = hits.sum(axis=1) / k
    rappel = hits.sum(axis=1) / n_rel
    cumul = np.cumsum(hits, axis=1)
    rangs = np.arange(1, k + 1)
    ap = (hits * cumul / rangs).sum(axis=1) / np.minimum(n_rel, k)
    gain = 1 / np.log2(rangs + 1)
    dcg = (hits * gain).sum(axis=1)
    idcg = np.array([gain[:min(int(n), k)].sum() for n in n_rel])
    return pd.DataFrame({"precision": precision, "rappel": rappel, "ap": ap, "ndcg": dcg / idcg, "succes": (hits.sum(axis=1) > 0).astype(float),
                         "recommandes": list(ordre)}, index=users)


def resume(df):
    return df[["precision", "rappel", "ap", "ndcg", "succes"]].mean()


def ic_bootstrap(valeurs, B=2000, seed=0):
    """Intervalle de confiance à 95 % de la moyenne par bootstrap sur les clients."""
    rng = np.random.default_rng(seed)
    v = np.asarray(valeurs, float)
    m = rng.choice(v, (B, len(v))).mean(axis=1)
    return np.percentile(m, [2.5, 97.5])


# ------------------------------------------------------------------ démarrage à froid d'un client : « fold-in »
def vecteur_client(V, items, lam=50.0, alpha=8.0):
    """Facteur d'un client à partir de la liste de ses achats, les facteurs produits V étant fixés (une étape de l'ALS)."""
    k = V.shape[1]
    if len(items) == 0:
        return np.zeros(k)
    Vi = V[items]
    return np.linalg.solve(V.T @ V + lam * np.eye(k) + alpha * Vi.T @ Vi, (1 + alpha) * Vi.sum(axis=0))


# ------------------------------------------------------------------ simulation : un monde qui change (découpage aléatoire vs temporel)
def monde_en_derive(n_users=2000, n_items=100, k=4, seed=11, n_bouge=30):
    """Deux périodes ; entre les deux, la popularité de `n_bouge` produits change (certains montent, d'autres chutent). Retourne (R1, R2)."""
    rng = np.random.default_rng(seed)
    U = rng.standard_normal((n_users, k)); V = rng.standard_normal((n_items, k))
    pop1 = rng.normal(0, 0.8, n_items)
    pop2 = pop1.copy()
    bouge = rng.choice(n_items, n_bouge, replace=False)
    pop2[bouge] += rng.choice([-1.8, 1.8], n_bouge)
    aff = 0.55 * U @ V.T
    p1 = 1 / (1 + np.exp(-(-3.4 + pop1[None, :] + aff)))
    p2 = 1 / (1 + np.exp(-(-3.4 + pop2[None, :] + aff)))
    R1 = sp.csr_matrix((rng.random((n_users, n_items)) < p1).astype(float))
    R2 = sp.csr_matrix((rng.random((n_users, n_items)) < p2).astype(float))
    return R1, R2


# ------------------------------------------------------------------ simulation : boucle de rétroaction (exposition -> achats -> modèle -> exposition)
def boucle_retroaction(epsilon, taux=False, n_tours=40, n_users=1500, n_items=60, k=4, vitrine=5, seed=5):
    """À chaque tour, chaque client voit `vitrine` produits (les plus populaires selon les achats observés, sauf une part epsilon tirée au hasard)
    et achète un produit exposé avec une probabilité qui dépend de son goût réel ; il achète aussi, rarement, hors vitrine.
    Retourne un DataFrame par tour : part des achats concentrée sur 5 produits, nombre de produits achetés, corrélation entre achats observés et attrait réel, nombre des 5 meilleurs produits réels présents en vitrine."""
    rng = np.random.default_rng(seed)
    U = rng.standard_normal((n_users, k)); V = rng.standard_normal((n_items, k))
    attrait = rng.normal(0, 0.7, n_items)
    p = 1 / (1 + np.exp(-(-1.5 + attrait[None, :] + 0.6 * U @ V.T)))           # goût réel : probabilité d'acheter si exposé
    obs = np.ones(n_items)                                                       # achats observés (départ uniforme)
    expo = np.zeros(n_items)                                                     # nombre d'expositions en vitrine
    lignes = []
    for t in range(n_tours):
        cle = (obs + 1) / (expo + 10) if taux else obs                          # taux d'achat lissé, ou simple nombre d'achats
        classement = np.argsort(-cle, kind="stable")
        vus = np.tile(classement[:vitrine], (n_users, 1))
        alea = rng.random((n_users, vitrine)) < epsilon                          # une part de la vitrine est exploratoire
        vus = np.where(alea, rng.integers(0, n_items, (n_users, vitrine)), vus)
        achat_vitrine = rng.random((n_users, vitrine)) < np.take_along_axis(p, vus, axis=1)
        expo = expo + np.bincount(vus.ravel(), minlength=n_items)
        nouveaux = np.bincount(vus[achat_vitrine], minlength=n_items).astype(float)
        hors = rng.random((n_users, n_items)) < 0.004 * p                         # achats spontanés, hors vitrine
        nouveaux += hors.sum(axis=0)
        obs = obs + nouveaux
        part = np.sort(obs)[::-1][:5].sum() / obs.sum()
        rho = pd.Series(obs).corr(pd.Series(p.mean(axis=0)), method="spearman")
        meilleurs = set(np.argsort(-p.mean(axis=0))[:5])
        lignes.append({"tour": t + 1, "part_top5": part, "produits_achetes": int((nouveaux > 0).sum()), "correlation_vrai": rho,
                       "bons_en_vitrine": len(meilleurs & set(np.argsort(-((obs + 1) / (expo + 10) if taux else obs), kind="stable")[:5]))})
    return pd.DataFrame(lignes)
