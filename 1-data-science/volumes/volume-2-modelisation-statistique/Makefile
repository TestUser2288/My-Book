# Construction du volume II. Usage : make help
# Prérequis : bash setup-env.sh  (crée .venv et installe R, pandoc, xelatex...)
VENV   ?= .venv
PY     := $(VENV)/bin/python
# Les blocs bash des chapitres 4 et 6 appellent python/pytest/jupyter : le venv doit être en tête du PATH.
RUN    := PATH=$(abspath $(VENV))/bin:$$PATH $(PY) build/fill.py
S      := sections

# Variables exigées par le chapitre 6 (voir le commentaire en tête de sections/06-0-intro.md)
export DONNEES := $(abspath donnees)
export NO_COLOR := 1

# Groupes de fichiers exécutés ENSEMBLE (espace de noms partagé), dans l'ordre : un groupe = un chapitre.
# Dans un chapitre, une section peut réutiliser les objets définis dans les sections précédentes.
CH0  := $(sort $(wildcard $(S)/00-*.md))
CH1  := $(sort $(wildcard $(S)/01-*.md))
CH2  := $(sort $(wildcard $(S)/02-*.md))
CH3  := $(sort $(wildcard $(S)/03-*.md))
CH4  := $(sort $(wildcard $(S)/04-*.md))
CH5  := $(sort $(wildcard $(S)/05-*.md))
CH6  := $(sort $(wildcard $(S)/06-*.md))
CH7  := $(sort $(wildcard $(S)/07-*.md))
CH8  := $(sort $(wildcard $(S)/08-*.md))
CH9  := $(sort $(wildcard $(S)/09-*.md))
CH10 := $(sort $(wildcard $(S)/10-*.md))
GROUPS := CH0 CH1 CH2 CH3 CH4 CH5 CH6 CH7 CH8 CH9 CH10

.PHONY: help fill check livre pdf all
help:
	@echo "make check  : réexécute tout SANS écrire et signale les différences"
	@echo "make fill   : réexécute tout et réécrit les sorties dans sections/"
	@echo "make livre  : assemble livre/*.md à partir de sections/"
	@echo "make pdf    : livre + PDF (pandoc/xelatex)"

check:
	$(foreach g,$(GROUPS),$(if $($(g)),$(RUN) --check $($(g)) &&)) true
fill:
	$(foreach g,$(GROUPS),$(if $($(g)),$(RUN) $($(g)) &&)) true
livre:
	$(PY) build/assemble.py
pdf: livre
	$(PY) build/make_pdf.py
all: fill pdf
