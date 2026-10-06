#!/usr/bin/env bash
# Prépare l'environnement de construction du volume IV (Debian/Ubuntu).
#   bash setup-env.sh   -> crée .venv, installe paquets Python (PyTorch version CPU), paquets système (sudo), puis télécharge modèles et données.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
# PyTorch CPU : la roue par défaut de PyPI tire plusieurs Go de bibliothèques GPU. Les versions numpy/pandas/scipy/scikit-learn sont figées.
.venv/bin/pip install -q -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
sudo apt-get update
sudo apt-get install -y r-base-core r-recommended r-cran-ggplot2 r-cran-dplyr r-cran-shiny pandoc sqlite3 \
  texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern \
  default-jre-headless tesseract-ocr tesseract-ocr-fra
.venv/bin/python build/telecharger_modeles.py     # ≈ 780 Mo, une fois ; ensuite tout s'exécute hors ligne
.venv/bin/python build/telecharger_mnist.py       # facultatif : donnees/mnist_sous_ensemble.npz est déjà versionné
echo "OK. Utilisez ensuite : make check / make pdf   (un chapitre : make fill-ch CH=03)"
