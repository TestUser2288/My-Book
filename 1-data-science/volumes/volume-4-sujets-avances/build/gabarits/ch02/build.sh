#!/usr/bin/env bash
# usage: build.sh livre|cahier|tout [--nofill]
set -e
T=$CLAUDE_JOB_DIR/tmp/v4c2/tpl
R=/var/www/book/1-data-science/volumes/volume-4-sujets-avances
cd $R
export HF_HOME=$R/modeles/hf TORCH_HOME=$R/modeles/torch HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 TMPDIR=/home/ubuntu/pip-tmp PYTHONHASHSEED=0 TOKENIZERS_PARALLELISM=false NO_COLOR=1 DONNEES=$R/donnees
PYBIN="env PATH=$R/.venv/bin:$PATH $R/.venv/bin/python"
what=${1:-tout}
if [ "$what" = livre ] || [ "$what" = tout ]; then
  cp $T/sections/*.md sections/
  [ "$2" = "--nofill" ] || $PYBIN build/fill.py sections/02-*.md 2>&1 | tail -n 12
  $PYBIN $CLAUDE_JOB_DIR/tmp/v4c2/patch.py sections/02-*.md
fi
if [ "$what" = cahier ] || [ "$what" = tout ]; then
  cp $T/cahier/*.md cahier/
  [ "$2" = "--nofill" ] || $PYBIN build/fill.py cahier/02-exercices.md 2>&1 | tail -n 6
  $PYBIN $CLAUDE_JOB_DIR/tmp/v4c2/patch.py cahier/02-exercices.md sections/02-*.md
fi
