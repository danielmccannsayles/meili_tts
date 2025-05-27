#!/bin/bash
echo "Launching MeiLiTTS..."

# We need to rebuild the pyenv since we're shipping it
# Get the absolute path to this script's directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$DIR/python/bin"
VENV_DIR="$DIR/.venv"
PYVENV_CFG="$VENV_DIR/pyvenv.cfg"

# Extract Python version dynamically
PYTHON_VERSION="$("$PYTHON_DIR/python3" --version | awk '{print $2}')"

# Rebuild pyvenv.cfg
cat > "$PYVENV_CFG" <<EOF
home = $PYTHON_DIR
include-system-site-packages = false
version = $PYTHON_VERSION
executable = $PYTHON_DIR/python$PYTHON_VERSION
command = $PYTHON_DIR/python3 -m venv $VENV_DIR
EOF

# Activate venv and launch
source "$VENV_DIR/bin/activate"
python "$DIR/main.py"
