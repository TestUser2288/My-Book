"""Outils du chapitre 1 (deep learning) : chargement de MNIST, boucle d'entraînement minimale, comptage de paramètres.
Importé par les blocs cachés du livre et par le cahier ; les algorithmes eux-mêmes sont écrits dans le texte."""
import os
import numpy as np
import torch
import torch.nn as nn

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def graine(s=0):
    """Fixe toutes les graines (numpy, torch) et limite les threads : résultats reproductibles."""
    np.random.seed(s)
    torch.manual_seed(s)
    torch.set_num_threads(2)


def charger_mnist(n_train=None, plat=False):
    """Retourne (x_train, y_train, x_test, y_test) en tenseurs float32 dans [0,1] ; images (N,1,28,28) ou (N,784) si plat."""
    d = np.load(os.path.join(RACINE, "donnees", "mnist_sous_ensemble.npz"))
    xtr, ytr, xte, yte = d["x_train"], d["y_train"], d["x_test"], d["y_test"]
    if n_train:
        xtr, ytr = xtr[:n_train], ytr[:n_train]
    f = lambda x: torch.tensor(x, dtype=torch.float32).div(255).reshape(len(x), -1) if plat else torch.tensor(x, dtype=torch.float32).div(255).unsqueeze(1)
    return f(xtr), torch.tensor(ytr, dtype=torch.long), f(xte), torch.tensor(yte, dtype=torch.long)


def nb_parametres(modele):
    return sum(p.numel() for p in modele.parameters() if p.requires_grad)


def exactitude(modele, x, y, lot=1000):
    modele.eval()
    ok = 0
    with torch.no_grad():
        for i in range(0, len(x), lot):
            ok += (modele(x[i:i + lot]).argmax(1) == y[i:i + lot]).sum().item()
    return ok / len(x)


def entrainer(modele, x, y, x_val, y_val, epoques=5, lot=128, optimiseur=None, lr=1e-3, wd=0.0, graine_lot=0, patience=None):
    """Boucle d'entraînement (entropie croisée). Retourne l'historique : perte d'entraînement, exactitudes d'entraînement et de validation par époque.
    Si `patience` est donné, on garde les poids de la meilleure époque de validation (arrêt précoce)."""
    opt = optimiseur(modele.parameters()) if optimiseur else torch.optim.Adam(modele.parameters(), lr=lr, weight_decay=wd)
    g = torch.Generator().manual_seed(graine_lot)
    hist = {"perte": [], "acc_train": [], "acc_val": []}
    meilleur, etat, sans_progres = -1, None, 0
    for e in range(epoques):
        modele.train()
        perm = torch.randperm(len(x), generator=g)
        total = 0.0
        for i in range(0, len(x), lot):
            idx = perm[i:i + lot]
            opt.zero_grad()
            perte = nn.functional.cross_entropy(modele(x[idx]), y[idx])
            perte.backward()
            opt.step()
            total += perte.item() * len(idx)
        hist["perte"].append(total / len(x))
        hist["acc_train"].append(exactitude(modele, x, y))
        hist["acc_val"].append(exactitude(modele, x_val, y_val))
        if patience is not None:
            if hist["acc_val"][-1] > meilleur:
                meilleur, sans_progres = hist["acc_val"][-1], 0
                etat = {k: v.clone() for k, v in modele.state_dict().items()}
            else:
                sans_progres += 1
                if sans_progres >= patience:
                    break
    if etat is not None:
        modele.load_state_dict(etat)
        hist["meilleure_epoque"] = int(np.argmax(hist["acc_val"])) + 1
    return hist
