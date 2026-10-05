# Construction du volume I. Usage : make help
# Prérequis : bash setup-env.sh  (crée .venv et installe R, pandoc, xelatex...)
VENV   ?= .venv
PY     := $(VENV)/bin/python
# Les blocs bash des chapitres 4 et 6 appellent python/pytest/jupyter : le venv doit être en tête du PATH.
RUN    := PATH=$(abspath $(VENV))/bin:$$PATH $(PY) build/fill.py
S      := sections

# Variables exigées par le chapitre 6 (voir le commentaire en tête de sections/06-0-intro.md)
export DONNEES := $(abspath donnees)
export NO_COLOR := 1

# Groupes de fichiers exécutés ENSEMBLE (espace de noms partagé), dans cet ordre.
CH0 := $(S)/00-a-avant-propos.md $(S)/00-b-rappel-express.md
CH1 := $(sort $(wildcard $(S)/01-*.md))
CH2 := $(sort $(wildcard $(S)/02-*.md))
CH3 := $(sort $(wildcard $(S)/03-*.md))
CH4a := $(S)/04-1-python.md $(S)/04-2-r.md $(S)/04-3-algorithmes.md
CH4b := $(S)/04-4-numpy-pandas.md $(S)/04-5-visualisation.md
CH4c := $(S)/04-6-poo-tests.md $(S)/04-7-autres-langages.md $(S)/04-8-complexite.md
CH4d := $(S)/04-9-exercices.md
CH5 := $(sort $(wildcard $(S)/05-*.md))
CH6 := $(sort $(wildcard $(S)/06-*.md))
CH7 := $(sort $(wildcard $(S)/07-*.md))
GROUPS := CH0 CH1 CH2 CH3 CH4a CH4b CH4c CH4d CH5 CH6 CH7

.PHONY: help fill check livre pdf all
help:
	@echo "make check  : réexécute tout SANS écrire et signale les différences"
	@echo "make fill   : réexécute tout et réécrit les sorties dans sections/"
	@echo "make livre  : assemble livre/*.md à partir de sections/"
	@echo "make pdf    : livre + PDF (pandoc/xelatex)"

check:
	$(foreach g,$(GROUPS),$(RUN) --check $($(g)) &&) true
fill:
	$(foreach g,$(GROUPS),$(RUN) $($(g)) &&) true
livre:
	$(PY) build/assemble.py
pdf: livre
	$(PY) build/make_pdf.py
all: fill pdf
