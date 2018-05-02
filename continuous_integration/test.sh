#!/bin/bash
# the Travis "script" step: see http://docs.travis-ci.com/ and ../.travis.yml
set -e

# make sure we're importing from the right place
mkdir empty_folder
cd empty_folder

$python -m pytest --pyargs cyflann

cd ..
