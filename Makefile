.PHONY: dcu clean gui env

PYTHON := python3.11
PIP := pip
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHONPATH := $(shell pwd)

dcu:
	@bash ./_scripts/dcu.sh

clean:
	rm -rf $(VENV)
	rm -f _scripts/venv.sh

gui:
	@echo "Starting the GUI..."
	@$(VENV_BIN)/python _scripts/gui.py

env:
	@bash ./_scripts/env.sh