# Construction d'un volume : LIVRE (sections/) et CAHIER d'exercices et d'applications (cahier/). Usage : make help
# Prérequis : bash setup-env.sh  (crée .venv et installe R, pandoc, xelatex...)
VENV   ?= .venv
PY     := $(VENV)/bin/python
# Les blocs bash appellent python/pytest/jupyter : le venv doit être en tête du PATH.
RUN    := PATH=$(abspath $(VENV))/bin:$$PATH $(PY) build/fill.py
S      := sections
C      := cahier

# Variables exigées par certains chapitres (voir le commentaire en tête du chapitre « outils »)
export DONNEES := $(abspath donnees)
export NO_COLOR := 1
export OMP_NUM_THREADS := 1
# Série 2, volume II : tout est simulé (donnees_a2.py) ; graines fixes
export PYTHONHASHSEED := 0
export TMPDIR := $(HOME)/pip-tmp

# Un groupe = un chapitre : ses fichiers sont exécutés ENSEMBLE, dans l'ordre (espace de noms Python partagé).
# Le cahier est exécuté séparément du livre : chaque chapitre du cahier doit être autonome (il recharge ses données).
N := 00 01 02 03 04 05 06 07 08 09 10
$(foreach n,$(N),$(eval CH$(n)  := $$(sort $$(wildcard $(S)/$(n)-*.md))))
$(foreach n,$(N),$(eval CAH$(n) := $$(sort $$(wildcard $(C)/$(n)-*.md))))
GROUPS := $(foreach n,$(N),CH$(n)) $(foreach n,$(N),CAH$(n))

.PHONY: help fill check livre cahier pdf pdf-livre pdf-cahier all fill-ch check-ch
help:
	@echo "make check      : réexécute tout (livre ET cahier) SANS écrire et signale les différences"
	@echo "make fill       : réexécute tout et réécrit les sorties dans sections/ et cahier/"
	@echo "make livre      : assemble livre/*.md (code 'hide' retiré)"
	@echo "make pdf        : assemble et construit les deux PDF (livre + cahier)"
	@echo "make pdf-livre  / make pdf-cahier : un seul PDF"

# un seul chapitre, livre PUIS cahier :  make fill-ch CH=03   /   make check-ch CH=03
fill-ch:
	$(if $(CH$(CH)),$(RUN) $(CH$(CH)) &&) $(if $(CAH$(CH)),$(RUN) $(CAH$(CH)) &&) true
check-ch:
	$(if $(CH$(CH)),$(RUN) --check $(CH$(CH)) &&) $(if $(CAH$(CH)),$(RUN) --check $(CAH$(CH)) &&) true
check:
	$(foreach g,$(GROUPS),$(if $($(g)),$(RUN) --check $($(g)) &&)) true
fill:
	$(foreach g,$(GROUPS),$(if $($(g)),$(RUN) $($(g)) &&)) true
livre:
	$(PY) build/assemble.py tout
pdf-livre: livre
	$(PY) build/make_pdf.py livre
pdf-cahier: livre
	@if [ -d $(C) ]; then $(PY) build/make_pdf.py cahier; fi
pdf: pdf-livre pdf-cahier
all: fill pdf
