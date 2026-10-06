#!/usr/bin/env bash
# Prépare l'environnement de construction du volume V (Debian/Ubuntu).  Tout est simulé : aucun téléchargement de données ni de modèles.
#   bash setup-env.sh   -> crée .venv, installe les paquets Python, puis les paquets système (sudo), puis régénère donnees/
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
sudo apt-get update
sudo apt-get install -y r-base-core r-recommended pandoc sqlite3 texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern
.venv/bin/python build/donnees5.py        # régénère donnees/*.csv (≈ 10 s) ; credit_defaut.csv (UCI, CC0) est versionné
echo "OK. Utilisez ensuite : make check / make pdf   (un chapitre : make fill-ch CH=03)"
