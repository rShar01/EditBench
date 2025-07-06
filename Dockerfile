FROM ubuntu:22.04

# Accept Python version as build argument
ARG PYTHON_VERSION=3.12
ENV PYTHON_VERSION=${PYTHON_VERSION}

# Update and install essential packages
RUN apt-get -y update && \
    apt-get -y install \
    htop vim openssh-client make cmake build-essential autoconf \
    libtool rsync ca-certificates git grep sed dpkg curl wget \
    bzip2 unzip pkg-config python3-dev libcairo2-dev \
    libpango1.0-dev gir1.2-pango-1.0 ffmpeg

# Install uv and create symlinks
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv && \
    ln -s /root/.local/bin/uvx /usr/local/bin/uvx

# Install NVM and Node.js 22
ENV NVM_DIR /root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install 22 && \
    nvm use 22 && \
    nvm alias default 22 && \
    ln -s $NVM_DIR/versions/node/$(nvm version)/bin/node /usr/local/bin/node && \
    ln -s $NVM_DIR/versions/node/$(nvm version)/bin/npm /usr/local/bin/npm

# Configure shell with NVM
RUN echo "export NVM_DIR=\"/root/.nvm\"" >> ~/.bashrc && \
    echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\"" >> ~/.bashrc

# Set working directory
WORKDIR /project

# Create entrypoint script
RUN cat > /entrypoint.sh << 'EOF'
#!/bin/bash
set -e

# Get Python version from environment or use default
PYTHON_VER=${PYTHON_VERSION:-3.12}

# Setup uv environment if it doesn't exist or is broken
if [ ! -d ".docker_venv" ] || [ ! -f ".docker_venv/bin/python3" ] || ! .docker_venv/bin/python3 --version &>/dev/null; then
    echo "Setting up Python environment with uv (Python $PYTHON_VER)..."
    rm -rf .docker_venv  # Remove any broken environment
    uv venv --python $PYTHON_VER .docker_venv
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
EOF

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]