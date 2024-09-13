#!/bin/bash

PYTHON="python3.11"
VENV="venv"
VENV_BIN="$VENV/bin"

install_python() {
    if ! command -v $PYTHON &> /dev/null; then
        echo "$PYTHON not found. Installing..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo add-apt-repository ppa:deadsnakes/ppa -y
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python@3.11
        else
            echo "Unsupported OS for automatic Python 3.11 installation."
            exit 1
        fi
    fi
}

create_venv() {
    if [ ! -d "$VENV" ]; then
        $PYTHON -m venv $VENV
        echo "Virtual environment created using $PYTHON."
    fi
}

create_activation_script() {
    echo "Creating venv.sh for easy activation"
    echo "source $VENV_BIN/activate" > _scripts/venv.sh
    chmod +x _scripts/venv.sh
}

copy_to_clipboard() {
    activation_command="source _scripts/venv.sh"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -qi microsoft /proc/version; then
            echo "$activation_command" | clip.exe
            echo "Activation command copied to clipboard for WSL."
        else
            echo "$activation_command" | xclip -selection clipboard
            echo "Activation command copied to clipboard."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$activation_command" | pbcopy
        echo "Activation command copied to clipboard."
    fi
}

main() {
    install_python
    create_venv
    create_activation_script
    copy_to_clipboard
    echo "To activate the virtual environment in the current shell, run:"
    echo "source _scripts/venv.sh"
}

main