#!/usr/bin/env bash
# Rend le chapitre 3 à partir des gabarits : copie tpl/ -> sections/ et cahier/, exécute les blocs (fill), substitue les {{clé}} de la prose
# par les valeurs « NUM clé valeur » imprimées par les blocs, puis vérifie (check). Usage : bash build/gabarits/ch11/build.sh [livre|cahier|tout]
set -euo pipefail
cd "$(dirname "$0")/../../.."
cible="${1:-tout}"
G=build/gabarits/ch11
RUN="env PATH=$PWD/.venv/bin:$PATH DONNEES=$PWD/donnees NO_COLOR=1 OMP_NUM_THREADS=1 PYTHONHASHSEED=0 TMPDIR=${TMPDIR:-$HOME/pip-tmp} .venv/bin/python"
if [ "$cible" = livre ] || [ "$cible" = tout ]; then
  cp $G/tpl/sections/11-*.md sections/
  $RUN build/fill.py sections/11-*.md
  $RUN $G/subst.py sections/11-*.md
  $RUN build/fill.py --check sections/11-*.md
fi
if [ "$cible" = cahier ] || [ "$cible" = tout ]; then
  cp $G/tpl/cahier/11-exercices.md cahier/
  $RUN build/fill.py cahier/11-exercices.md
  $RUN $G/subst.py cahier/11-exercices.md
  $RUN build/fill.py --check cahier/11-exercices.md
fi
