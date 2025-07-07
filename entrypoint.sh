#!/bin/bash
set -e

# Setup uv environment if it doesn't exist or is broken
if [ ! -d ".docker_venv" ] || [ ! -f ".docker_venv/bin/python3" ] || ! .docker_venv/bin/python3 --version &>/dev/null; then
    echo "Setting up Python environment with uv (Python $PYTHON_VERSION)..."
    rm -rf .docker_venv  # Remove any broken environment
    uv venv --python $PYTHON_VERSION .docker_venv
fi

# Activate the environment
source .docker_venv/bin/activate

# Install dependencies if pyproject.toml or setup.py exists
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    echo "Installing Python dependencies..."
    uv pip install -e .
fi

# Execute the command passed to the container
exec "$@"