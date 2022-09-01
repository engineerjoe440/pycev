#!/usr/bin/bash

venvDir="pycev-pytest"
requirementsFile="tests/test-requires.txt"

# Activate Environment
python3 -m venv $venvDir
source $WORKSPACE/$venvDir/bin/activate

# Install Requirements
python3 -m pip install -r $requirementsFile

python3 -m pip install .

# Run Tests
python3 -m pytest --xdoctest

# Deactivate Environment
deactivate