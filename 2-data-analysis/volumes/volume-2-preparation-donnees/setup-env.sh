#!/usr/bin/env bash
# Prépare l'environnement de construction du volume (Debian/Ubuntu).  Tout est simulé : aucun téléchargement de données.
#   bash setup-env.sh   -> crée .venv, installe paquets Python (et Chromium pour les captures d'écran), paquets système (sudo) dont LibreOffice Calc, puis régénère donnees/
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/playwright install chromium            # facultatif : captures d'écran d'outils exécutés localement
sudo apt-get update
sudo apt-get install -y r-base-core r-recommended r-cran-tidyverse r-cran-readxl r-cran-openxlsx pandoc sqlite3 poppler-utils \
  texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern
sudo apt-get install -y --no-install-recommends libreoffice-calc
.venv/bin/python build/donnees_a2.py        # régénère donnees/ (≈ 10 s)
echo "OK. Utilisez ensuite : make check / make pdf   (un chapitre : make fill-ch CH=03)"
