#!/bin/bash
set -e

echo "Checking sudo access..."
sudo -v

# --------------------------------------------------
# System dependencies for pyenv + PyGObject
# --------------------------------------------------
echo "Installing pygobject dependencies..."
sudo apt update
sudo apt install -y \
  git curl wget build-essential \
  libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev \
  llvm libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev \
  liblzma-dev \
  gobject-introspection libgirepository-2.0-dev \
  libglib2.0-dev libcairo2-dev pkg-config cmake

# --------------------------------------------------
# Install pyenv (if not already installed)
# --------------------------------------------------
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
fi

# --------------------------------------------------
# Setup pyenv environment (non-interactive safe)
# --------------------------------------------------
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# --------------------------------------------------
# Install Python 3.12 via pyenv
# --------------------------------------------------
PYTHON_VERSION="3.12.2"

if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install "$PYTHON_VERSION"
fi

pyenv global "$PYTHON_VERSION"

# --------------------------------------------------
# Upgrade pip (SAFE – pyenv Python)
# --------------------------------------------------
python -m pip install --upgrade pip setuptools wheel

# --------------------------------------------------
# Install PyGObject (NO PEP 668 issue)
# --------------------------------------------------
echo "Installing PyGObject..."
python -m pip install PyGObject

# --------------------------------------------------
# Clone your project
# --------------------------------------------------
echo "Cloning Open Desktop"
git clone https://github.com/radin6262/Open-Desktop.git

# --------------------------------------------------
# Finish
# --------------------------------------------------
echo "Installation complete!"
echo "Python version:"
python --version
echo
echo "To run later:"
echo "  cd OpenDesktop"
echo "  python main.py"
echo
echo "This shell will exit in 8 seconds..."
sleep 8
exit 0
