#!/bin/bash
set -e

echo "Checking sudo access..."
sudo -v


echo "Welcome to The Open-Desktop project installation prompt"
echo "Dev: Radin6262"
sleep 1
# --------------------------------------------------
# System dependencies for pyenv + PyGObject
# --------------------------------------------------
echo "Installing pygobject dependencies..."
set +e
if ! timeout 60s sudo apt update; then
    echo "apt update took too long, skipping..."
fi
set -e  # re-enable exit-on-error
sudo apt install -y \
  git curl wget build-essential \
  libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev \
  llvm libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev \
  liblzma-dev \
  gobject-introspection libgirepository-2.0-dev \
  libglib2.0-dev libcairo2-dev pkg-config cmake

sleep 1
echo "Checking for PyEnv"
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
sleep 1.2
# --------------------------------------------------
# Install Python 3.12 via pyenv
# --------------------------------------------------
echo "Python installation:"
PYTHON_VERSION="3.12.2"

if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install "$PYTHON_VERSION"
fi

pyenv global "$PYTHON_VERSION"
echo "Python installation finished"
sleep 1

# --------------------------------------------------
# Upgrade pip (SAFE – pyenv Python)
# --------------------------------------------------
echo "Upgrading Pip / If not latest version"
python3 -m pip install --upgrade pip setuptools wheel
sleep 1.2
# --------------------------------------------------
# Install PyGObject
# --------------------------------------------------
echo "Installing PyGObject..."
python3 -m pip install PyGObject
sleep 1.2
echo "Installating pyside6"
python3 -m pip install pyside6
# --------------------------------------------------
# Clone The Open Desktop project
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
echo "  python3 main.py"
echo
echo "This shell will exit in 8 seconds..."
sleep 8
exit 0
