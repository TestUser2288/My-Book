#!/usr/bin/env bash
# Prépare l'environnement de construction du volume (Debian/Ubuntu).
#   bash setup-env.sh            -> crée .venv et installe les paquets système (sudo)
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
sudo apt-get update
sudo apt-get install -y r-base-core r-recommended r-cran-ggplot2 r-cran-dplyr r-cran-tidyr \
  r-cran-readr r-cran-purrr pandoc sqlite3 texlive-xetex texlive-lang-french \
  texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern
echo "OK. Utilisez ensuite : make fill / make livre / make pdf"
