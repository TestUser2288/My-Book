"""Télécharge MNIST (OpenML « mnist_784 », chiffres manuscrits réels ; base publique, libre pour la recherche et l'enseignement) et en conserve un SOUS-ENSEMBLE
(10 000 images d'entraînement, 2 000 de test, tirage stratifié à graine fixe) dans donnees/mnist_sous_ensemble.npz (≈ 3 Mo).
À lancer UNE fois ; le fichier est versionné. Source : LeCun, Cortes et Burges, « The MNIST database of handwritten digits »."""
import os
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

d = fetch_openml("mnist_784", version=1, as_frame=False, parser="auto")
X, y = d.data.astype(np.uint8), d.target.astype(np.uint8)
Xtr, Xte, ytr, yte = train_test_split(X, y, train_size=10000, test_size=2000, stratify=y, random_state=0)
sortie = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees", "mnist_sous_ensemble.npz")
np.savez_compressed(sortie, x_train=Xtr.reshape(-1, 28, 28), y_train=ytr, x_test=Xte.reshape(-1, 28, 28), y_test=yte)
print(Xtr.shape, Xte.shape, "->", sortie, os.path.getsize(sortie) // 1000, "Ko")
