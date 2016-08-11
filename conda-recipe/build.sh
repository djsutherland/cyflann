#!/bin/bash

$PYTHON setup.py egg_info
sed -n -e 's/^Version: \(.*\)$/\1/p' < mmd.egg-info/PKG-INFO > __conda_version__.txt

FLANN_DIR=$PREFIX $PYTHON setup.py install
