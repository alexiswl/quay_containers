#!/bin/bash

# Usage
# install_jupyter.sh <env_name> <git_tag>

JUPYTERLAB_TAG=$2
JUPYTERLAB_GITHUB_COMMIT_ID=fc600c
JUPYTERLAB_TOC_COMMIT_ID=b23c417

# Install nodejs first
conda install -c conda-forge nodejs --yes

# Install git tag
pip install git+git://github.com/jupyterlab/jupyterlab@${JUPYTERLAB_TAG}

# Install extensions
# Fasta
jupyter labextension install @jupyterlab/fasta-extension --no-build
# Toc
## Dev dependencies
npm install --save-dev style-loader
npm install --save-dev css-loader
npm install --save-dev webpack

# Installation of the lab manger
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build

## Clone repo
git clone https://github.com/jupyterlab/jupyterlab-toc
cd jupyterlab-toc
git checkout ${JUPYTERLAB_TOC_COMMIT_ID}
jlpm install
jlpm run build
jupyter labextension install --no-build . 
cd -

# GitHub
git clone https://github.com/jupyterlab/jupyterlab-github
cd jupyterlab-github
git checkout ${JUPYTERLAB_GITHUB_COMMIT_ID}
jlpm install
jlpm run build
jupyter labextension install --no-build .
cd -

# Install jupytertext
pip install jupytext --upgrade

# Build
jupyter lab build

# Enable extensions
jupyter labextension enable fasta-extension
jupyter labextension enable jupyterlab-manager
jupyter labextension enable jupyterlab-toc
jupyter labextension enable jupyterlab-github
jupyter labextension enable jupytext
