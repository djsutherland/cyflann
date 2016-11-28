#!/bin/bash

$PYTHON setup.py egg_info
sed -n -e 's/^Version: \(.*\)$/\1/p' < cyflann.egg-info/PKG-INFO > __conda_version__.txt

# don't allow dirty worktrees, too easy to mess up
if grep '\.dirty' __conda__version.txt; then
    echo "No dirty worktrees; make a temp commit if you really want to build"
    git status
    exit 1
fi

$PYTHON setup.py install
