#!/usr/bin/env bash
# Gabarits (avec {{cle}} / {{cle:format}}) -> fichiers du chapitre 5.
#   build.sh livre | cahier | tout
# 1) copie les gabarits dans sections/ ou cahier/ ; 2) fill (exécute, écrit les sorties « NUM cle valeur ») ;
# 3) subst (remplace {{cle}} dans la prose) ; 4) fill (sorties finales ; les NUM restent dans les sorties).
# Les fichiers sections/05-*.md et cahier/05-exercices.md du dépôt sont DÉJÀ rendus : ne repasser par ici que pour changer un nombre.
set -euo pipefail
R="$(cd "$(dirname "$0")/../../.." && pwd)"; G="$R/build/gabarits/ch05"; cd "$R"
export PATH="$R/.venv/bin:$PATH" DONNEES="$R/donnees" NO_COLOR=1 OMP_NUM_THREADS=1 PYTHONHASHSEED=0 TMPDIR="${TMPDIR:-$HOME/pip-tmp}"
rendre() {  # $1 = sections|cahier
  local d="$1"; mkdir -p "$d"
  for f in "$G/tpl/$d"/*.md; do cp "$f" "$d/$(basename "$f")"; done
  FILES=$(ls $d/05-*.md | sort)
  python build/fill.py $FILES
  python "$G/subst.py" $FILES
  python build/fill.py $FILES
  python build/fill.py --check $FILES
}
case "${1:-tout}" in
  livre) rendre sections;;
  cahier) rendre cahier;;
  tout) rendre sections; rendre cahier;;
esac
