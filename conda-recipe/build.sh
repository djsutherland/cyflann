#!/bin/bash

# don't allow dirty worktrees, too easy to mess up
if git diff-index --quiet HEAD --; then
    echo "Dirty worktree; commit if you really want to build"
    git status
    exit 1
fi

$PYTHON setup.py egg_info
sed -n -e 's/^Version: \(.*\)$/\1/p' < cyflann.egg-info/PKG-INFO > __conda_version__.txt

$PYTHON setup.py install
