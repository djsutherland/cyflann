#!/bin/bash
# the Travis "script" step: see http://docs.travis-ci.com/ and ../.travis.yml
set -e

cd $HOME # get out of source directory to avoid confusing nose

$python -mnose --exe cyflann
