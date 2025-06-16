FROM ubuntu:22.04

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




# # Install Miniconda and create test_env
# RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#     bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh

# ENV PATH /opt/conda/bin:$PATH
# RUN conda create -n test_env python=3.11
# RUN echo "source activate test_env" >> ~/.bashrc
# ENV PATH /opt/conda/envs/test_env/bin:$PATH
# ENV CONDA_DEFAULT_ENV test_env

# # Install pip packages
# RUN pip install numpy scipy matplotlib numba pandas scikit-learn tqdm openai anthropic python-dotenv magic-wormhole pyyaml
