#!/bin/bash
# the Travis "install" step: see http://docs.travis-ci.com/ and ../.travis.yml
set -e

os=$(uname)
if [[ "$os" == "Linux" ]]; then
    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
        -O miniconda.sh
elif [[ "$os" == "Darwin" ]]; then
    wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh \
        -O miniconda.sh
else
    echo "unknown os '$os'"
    exit 1
fi
chmod +x miniconda.sh
./miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"

conda update --yes --quiet conda

conda install --yes -c dougal \
    python=$PYTHON_VERSION pip nose setuptools cython \
    numpy=$NUMPY_VERSION flann=$FLANN_VERSION pyflann

PKG_CONFIG_PATH=$HOME/miniconda/lib/pkgconfig python setup.py install
