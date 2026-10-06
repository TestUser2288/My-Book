"""Outils du chapitre 2 (NLP et modèles de langage) : partagés par les blocs cachés du livre et par le cahier.

Contenu : tokeniseur simple, étiquetage des « tranches » difficiles du corpus d'avis, word2vec (skip-gram à échantillonnage négatif)
écrit en PyTorch, mini-transformer (classifieur et modèle de langage causal) écrit à la main, fonctions de décodage
(température, top-k, top-p), fusions BPE, et recherche d'information (TF-IDF contre plongements).
Tout est déterministe à graine fixe, petit (quelques milliers de paramètres) et tourne sur CPU en quelques secondes à quelques minutes.
"""
import math
import os
import re
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import donnees4  # noqa: E402

torch.set_num_threads(2)

# ------------------------------------------------------------------ corpus et tranches
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger_avis():
    return pd.read_csv(os.path.join(RACINE, "donnees", "avis_clients.csv")).assign(texte=lambda d: d["texte"].fillna(""))


def _phrases(source):
    out = {"pos": [], "neu": [], "neg": []}
    for sj in source.values():
        for pol in ("pos", "neu", "neg"):
            out[pol] += list(sj.get(pol, []))
    return out


_PH, _NIE = _phrases(donnees4.PHRASES), _phrases(donnees4.NIE)
_ANG = sum((v for v in donnees4.ANGLAIS.values()), [])
# phrases niées « réservées » : jamais vues à l'entraînement dans l'expérience de généralisation (une sur trois)
PHRASES_RESERVEES = [p for i, p in enumerate(_NIE["pos"] + _NIE["neg"]) if i % 3 == 0]


def etiqueter_tranches(df):
    """Ajoute des colonnes booléennes : niee (phrase niée/ironique), anglais, mixte (phrase polarisée ET phrase neutre),
    court (≤ 2 mots), inedite (contient une phrase niée réservée). Repose sur les gabarits du générateur : une faute de frappe
    peut faire échapper un texte à l'étiquetage."""
    pos = _PH["pos"] + _NIE["pos"]
    neg = _PH["neg"] + _NIE["neg"]
    neu = _PH["neu"]
    nies = _NIE["pos"] + _NIE["neg"]
    t = df["texte"]
    out = df.copy()
    out["niee"] = t.apply(lambda s: any(p in s for p in nies))
    out["anglais"] = t.apply(lambda s: any(p in s for p in _ANG))
    out["mixte"] = t.apply(lambda s: (any(p in s for p in pos) or any(p in s for p in neg)) and any(p in s for p in neu))
    out["court"] = t.str.split().str.len() <= 2
    out["inedite"] = t.apply(lambda s: any(p in s for p in PHRASES_RESERVEES))
    return out


def polarite(df, seuil_pos=4, seuil_neg=2):
    """Garde les avis nets : positif (note ≥ 4) = 1, négatif (note ≤ 2) = 0 ; écarte les notes de 3."""
    d = df[(df["note"] >= seuil_pos) | (df["note"] <= seuil_neg)].copy()
    d["y"] = (d["note"] >= seuil_pos).astype(int)
    return d


# ------------------------------------------------------------------ tokenisation
_MOTS = re.compile(r"[a-zàâäçéèêëîïôöûùüÿœæ]+(?:'[a-zàâäçéèêëîïôöûùüÿœæ]+)?|[!?]")


def tokeniser(texte):
    """Minuscules, mots (l'apostrophe reste attachée : « l'emballage » = 1 jeton), « ! » et « ? » conservés."""
    return _MOTS.findall(texte.lower().replace("’", "'"))


def tokeniser_fin(texte):
    """Variante qui sépare l'apostrophe : « l'emballage » -> « l' », « emballage »."""
    return re.findall(r"[a-zàâäçéèêëîïôöûùüÿœæ]+'?|[!?]", texte.lower().replace("’", "'"))


class Vocabulaire:
    def __init__(self, textes, min_freq=2, max_taille=None, tokeniseur=tokeniser):
        from collections import Counter
        self.tok = tokeniseur
        c = Counter(w for t in textes for w in self.tok(t))
        mots = [w for w, n in c.most_common(max_taille) if n >= min_freq]
        self.itos = ["<pad>", "<unk>", "<bos>", "<eos>"] + mots
        self.stoi = {w: i for i, w in enumerate(self.itos)}
        self.freq = c

    def __len__(self):
        return len(self.itos)

    def encoder(self, texte, longueur=None, bos=False, eos=False):
        ids = ([2] if bos else []) + [self.stoi.get(w, 1) for w in self.tok(texte)] + ([3] if eos else [])
        if longueur is not None:
            ids = ids[:longueur] + [0] * max(0, longueur - len(ids))
        return ids


# ------------------------------------------------------------------ word2vec (skip-gram, échantillonnage négatif)
def entrainer_word2vec(textes, dim=32, fenetre=2, negatifs=5, epoques=5, min_freq=3, graine=0, lr=0.01, lot=4096):
    torch.manual_seed(graine)
    rng = np.random.default_rng(graine)
    voc = Vocabulaire(textes, min_freq=min_freq)
    phrases = [[voc.stoi.get(w, 1) for w in voc.tok(t)] for t in textes]
    centres, contextes = [], []
    for ph in phrases:
        for i, c in enumerate(ph):
            for j in range(max(0, i - fenetre), min(len(ph), i + fenetre + 1)):
                if j != i and c > 3 and ph[j] > 3:
                    centres.append(c)
                    contextes.append(ph[j])
    centres, contextes = torch.tensor(centres), torch.tensor(contextes)
    freq = np.array([voc.freq.get(w, 0) for w in voc.itos], float) ** 0.75
    freq[:4] = 0
    p_neg = torch.tensor(freq / freq.sum(), dtype=torch.float)
    entree, sortie = nn.Embedding(len(voc), dim), nn.Embedding(len(voc), dim)
    nn.init.normal_(entree.weight, 0, 0.1)
    nn.init.zeros_(sortie.weight)
    opt = torch.optim.Adam(list(entree.parameters()) + list(sortie.parameters()), lr=lr)
    n = len(centres)
    pertes = []
    for ep in range(epoques):
        perm = torch.randperm(n)
        total = 0.0
        for k in range(0, n, lot):
            idx = perm[k:k + lot]
            c, o = centres[idx], contextes[idx]
            neg = torch.multinomial(p_neg, len(idx) * negatifs, replacement=True).view(len(idx), negatifs)
            vc = entree(c)
            pos = F.logsigmoid((vc * sortie(o)).sum(-1))
            nega = F.logsigmoid(-(sortie(neg) * vc.unsqueeze(1)).sum(-1)).sum(-1)
            perte = -(pos + nega).mean()
            opt.zero_grad()
            perte.backward()
            opt.step()
            total += perte.item() * len(idx)
        pertes.append(total / n)
    return voc, entree.weight.detach().numpy(), pertes


def voisins(voc, E, mot, k=5):
    En = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
    i = voc.stoi[mot]
    s = En @ En[i]
    s[:4] = -1
    ordre = np.argsort(-s)
    return [(voc.itos[j], float(s[j])) for j in ordre if j != i][:k]


def cosinus(voc, E, a, b):
    va, vb = E[voc.stoi[a]], E[voc.stoi[b]]
    return float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb)))


# ------------------------------------------------------------------ mini-transformer
def encodage_sinusoidal(longueur, d):
    pos = np.arange(longueur)[:, None]
    i = np.arange(d // 2)[None, :]
    ang = pos / (10000 ** (2 * i / d))
    pe = np.zeros((longueur, d))
    pe[:, 0::2], pe[:, 1::2] = np.sin(ang), np.cos(ang)
    return pe


class Attention(nn.Module):
    def __init__(self, d, tetes, causal=False):
        super().__init__()
        assert d % tetes == 0
        self.h, self.dh, self.causal = tetes, d // tetes, causal
        self.qkv = nn.Linear(d, 3 * d)
        self.sortie = nn.Linear(d, d)
        self.poids = None

    def forward(self, x, masque_pad=None):
        B, T, d = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dh).permute(2, 0, 3, 1, 4)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.dh)          # (B, h, T, T)
        if self.causal:
            m = torch.triu(torch.ones(T, T, dtype=torch.bool), 1)
            scores = scores.masked_fill(m, float("-inf"))
        if masque_pad is not None:
            scores = scores.masked_fill(masque_pad[:, None, None, :], float("-inf"))
        a = scores.softmax(-1)
        self.poids = a.detach()
        return self.sortie((a @ v).transpose(1, 2).reshape(B, T, d))


class Bloc(nn.Module):
    def __init__(self, d, tetes, causal=False, drop=0.1):
        super().__init__()
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.att = Attention(d, tetes, causal)
        self.ffn = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        self.drop = nn.Dropout(drop)

    def forward(self, x, masque_pad=None):
        x = x + self.drop(self.att(self.n1(x), masque_pad))
        return x + self.drop(self.ffn(self.n2(x)))


class MiniTransformer(nn.Module):
    """tache = 'classe' (classifieur de phrases, moyenne des vecteurs de sortie) ou 'langage' (prédiction du mot suivant)."""

    def __init__(self, taille_voc, d=48, tetes=4, couches=2, longueur=40, tache="classe", sorties=2, drop=0.1):
        super().__init__()
        self.tache, self.longueur = tache, longueur
        self.emb = nn.Embedding(taille_voc, d, padding_idx=0)
        self.register_buffer("pe", torch.tensor(encodage_sinusoidal(longueur, d), dtype=torch.float))
        self.blocs = nn.ModuleList([Bloc(d, tetes, causal=(tache == "langage"), drop=drop) for _ in range(couches)])
        self.norme = nn.LayerNorm(d)
        self.tete = nn.Linear(d, taille_voc if tache == "langage" else sorties)

    def forward(self, ids):
        pad = ids == 0
        x = self.emb(ids) * math.sqrt(self.emb.embedding_dim) + self.pe[: ids.shape[1]]
        for b in self.blocs:
            x = b(x, None if self.tache == "langage" else pad)
        x = self.norme(x)
        if self.tache == "langage":
            return self.tete(x)
        m = (~pad).unsqueeze(-1).float()
        return self.tete((x * m).sum(1) / m.sum(1).clamp(min=1))


def entrainer_classifieur(textes_tr, y_tr, voc, longueur=40, epoques=8, graine=0, lot=64, lr=2e-3, **kw):
    torch.manual_seed(graine)
    X = torch.tensor([voc.encoder(t, longueur) for t in textes_tr])
    y = torch.tensor(np.asarray(y_tr))
    m = MiniTransformer(len(voc), longueur=longueur, tache="classe", **kw)
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.01)
    for ep in range(epoques):
        m.train()
        perm = torch.randperm(len(X))
        for k in range(0, len(X), lot):
            idx = perm[k:k + lot]
            perte = F.cross_entropy(m(X[idx]), y[idx])
            opt.zero_grad()
            perte.backward()
            opt.step()
    return m.eval()


def predire_classe(m, voc, textes, longueur=40):
    X = torch.tensor([voc.encoder(t, longueur) for t in textes])
    with torch.no_grad():
        return m(X).softmax(-1)[:, 1].numpy()


def entrainer_langage(textes, voc, longueur=24, epoques=6, graine=0, lot=64, lr=3e-3, **kw):
    torch.manual_seed(graine)
    seqs = [voc.encoder(t, bos=True, eos=True)[:longueur] for t in textes]
    X = torch.tensor([s + [0] * (longueur - len(s)) for s in seqs])
    m = MiniTransformer(len(voc), longueur=longueur, tache="langage", **kw)
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.01)
    pertes = []
    for ep in range(epoques):
        m.train()
        perm = torch.randperm(len(X))
        tot = 0.0
        for k in range(0, len(X), lot):
            xb = X[perm[k:k + lot]]
            sortie = m(xb[:, :-1])
            perte = F.cross_entropy(sortie.reshape(-1, sortie.shape[-1]), xb[:, 1:].reshape(-1), ignore_index=0)
            opt.zero_grad()
            perte.backward()
            opt.step()
            tot += perte.item() * len(xb)
        pertes.append(tot / len(X))
    return m.eval(), pertes


def generer(m, voc, amorce="", n=20, temperature=1.0, top_k=None, graine=0):
    g = torch.Generator().manual_seed(graine)
    ids = voc.encoder(amorce, bos=True)
    for _ in range(n):
        with torch.no_grad():
            logits = m(torch.tensor([ids[-m.longueur:]]))[0, -1]
        p = decoder_probas(logits.numpy(), temperature=temperature, top_k=top_k)
        ids.append(int(torch.multinomial(torch.tensor(p, dtype=torch.float), 1, generator=g)))
        if ids[-1] == 3:
            break
    return " ".join(voc.itos[i] for i in ids[1:] if i > 3)


# ------------------------------------------------------------------ décodage
def softmax(z):
    z = np.asarray(z, float)
    e = np.exp(z - z.max())
    return e / e.sum()


def decoder_probas(logits, temperature=1.0, top_k=None, top_p=None):
    """Probabilités de tirage après température, puis top-k, puis top-p (noyau)."""
    p = softmax(np.asarray(logits, float) / max(temperature, 1e-8))
    if top_k is not None:
        garde = np.argsort(-p, kind="stable")[:top_k]          # les k premiers, même en cas d'égalité
        q = np.zeros_like(p)
        q[garde] = p[garde]
        p = q / q.sum()
    if top_p is not None:
        ordre = np.argsort(-p)
        cum = np.cumsum(p[ordre])
        garde = ordre[: int(np.searchsorted(cum, top_p) + 1)]
        q = np.zeros_like(p)
        q[garde] = p[garde]
        p = q / q.sum()
    return p


def entropie(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


# ------------------------------------------------------------------ BPE
def fusions_bpe(mots_freq, n_fusions):
    """mots_freq : dict {mot: fréquence}. Retourne la liste des fusions [(paire, fréquence)] et le corpus final (mots découpés)."""
    corpus = {tuple(m) + ("</w>",): f for m, f in mots_freq.items()}
    fusions = []
    for _ in range(n_fusions):
        paires = {}
        for mot, f in corpus.items():
            for a, b in zip(mot, mot[1:]):
                paires[(a, b)] = paires.get((a, b), 0) + f
        if not paires:
            break
        best = max(paires, key=paires.get)          # à égalité : la première paire rencontrée
        fusions.append((best, paires[best]))
        nouveau = {}
        for mot, f in corpus.items():
            out, i = [], 0
            while i < len(mot):
                if i < len(mot) - 1 and (mot[i], mot[i + 1]) == best:
                    out.append(mot[i] + mot[i + 1])
                    i += 2
                else:
                    out.append(mot[i])
                    i += 1
            nouveau[tuple(out)] = f
        corpus = nouveau
    return fusions, corpus


# ------------------------------------------------------------------ recherche d'information
def precision_au_rang(classement, pertinents, k=5):
    """classement : indices triés ; pertinents : ensemble d'indices pertinents. Fraction de pertinents parmi les k premiers."""
    return float(np.mean([i in pertinents for i in classement[:k]]))


# ------------------------------------------------------------------ sondes : 48 phrases écrites à la main, HORS des gabarits du corpus
SONDES_POS = [
    "Expédié en un clin d'œil, je suis comblé.", "Rien à reprocher à cet article, il est parfait.", "Un vase magnifique, bien mieux que je l'espérais.",
    "Je n'ai pas été déçu, loin de là.", "Le colis est arrivé en avance et en parfait état.", "Personnel adorable, ils ont tout réglé en une heure.",
    "Pas cher du tout pour une telle finition.", "Je le recommande les yeux fermés.", "Un cadeau qui a fait sensation.", "Aucun regret, je recommanderai.",
    "Emballage irréprochable, rien n'a bougé.", "Qualité au rendez-vous, merci à toute l'équipe.", "Superbe, exactement ce que je cherchais.",
    "Service impeccable, réponse immédiate.", "Ça valait vraiment le coup d'attendre.", "Excellent produit, livraison éclair.",
    "Je suis ravie, mes invités adorent.", "Franchement bravo, c'est du beau travail.", "Rapport qualité-prix imbattable.",
    "No complaints at all, lovely item.", "Tout est arrivé intact, merci beaucoup.", "Il tient ses promesses.",
    "On sent le soin apporté à la fabrication.", "Un vrai coup de cœur."]
SONDES_NEG = [
    "Interminable : trois semaines pour recevoir un simple colis.", "Rien n'a fonctionné, c'est une arnaque.", "Le produit est arrivé en morceaux.",
    "Je ne suis pas du tout satisfait de cet achat.", "Ce n'est pas du tout ce que j'espérais.", "Je regrette amèrement d'avoir commandé.",
    "Le service client m'a laissé tomber.", "Aucune réponse, aucune solution, rien.", "Franchement bof, ça ne vaut pas le prix.",
    "Fuyez, c'est une perte d'argent.", "Une honte, l'article est cassé et personne ne répond.", "Pas à la hauteur, loin de là.",
    "Il a cassé dès le premier jour.", "Colis égaré, jamais retrouvé.", "Qualité médiocre pour un tarif exorbitant.",
    "Trop cher et de piètre qualité.", "Je ne commanderai plus jamais ici.", "Terrible expérience, je déconseille.",
    "Le carton était écrasé et le contenu abîmé.", "Terrible: late, broken, and nobody replied.", "Un vrai cauchemar du début à la fin.",
    "Déçue, les photos sont trompeuses.", "Retard de deux semaines sans la moindre excuse.", "Rien de bon à en dire."]
SONDES = SONDES_POS + SONDES_NEG
Y_SONDES = np.array([1] * len(SONDES_POS) + [0] * len(SONDES_NEG))


REQUETES = {  # 3 formulations par sujet, écrites à la main ; pertinents = avis négatifs (note ≤ 2) dont le sujet principal est celui-ci
    "livraison": ["Le colis est arrivé en retard", "Livraison beaucoup trop longue", "Mon colis a mis des semaines à arriver"],
    "qualite": ["Le produit est abîmé et de mauvaise qualité", "Article cassé dès la réception", "La finition est décevante"],
    "prix": ["C'est beaucoup trop cher", "Le tarif n'est pas justifié", "Les frais de port sont exagérés"],
    "service": ["Le service client ne répond jamais", "Personne n'a répondu à mes messages", "Remboursement refusé sans explication"],
    "emballage": ["L'emballage était déchiré", "Aucune protection dans le carton", "Le colis n'était pas bien emballé"],
}
