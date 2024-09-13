.PHONY: dcu clean venv

PYTHON := python3
PIP := pip
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHONPATH := $(shell pwd)

dcu:
	@bash ./dcu.sh

clean:
	rm -rf $(VENV)
	rm -f venv.sh

env:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtual environment created."; \
	fi
	@echo "Creating venv.sh for easy activation"
	@echo "source $(VENV_BIN)/activate" > venv.sh
	@chmod +x venv.sh
	@echo "To activate the virtual environment in the current shell, run:"
	@echo "source venv.sh"
	# Copy the activation command to the clipboard
	@if [ "$(shell uname)" = "Linux" ]; then \
		if grep -qi microsoft /proc/version; then \
			echo "source venv.sh" | clip.exe; \
			echo "Activation command copied to clipboard for WSL."; \
		else \
			echo "source venv.sh" | xclip -selection clipboard; \
			echo "Activation command copied to clipboard."; \
		fi \
	elif [ "$(shell uname)" = "Darwin" ]; then \
		echo "source venv.sh" | pbcopy; \
		echo "Activation command copied to clipboard."; \
	fi