#!/bin/bash
# the Travis "script" step: see http://docs.travis-ci.com/ and ../.travis.yml
set -e

cd $HOME # get out of source directory to avoid confusing nose

PKG_CONFIG_PATH=$HOME/miniconda/lib/pkgconfig nosetests --exe cyflann
