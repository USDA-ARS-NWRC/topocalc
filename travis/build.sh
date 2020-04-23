#!/bin/bash

set -e -x

python3 -m cibuildwheel --output-dir wheelhouse
ls wheelhouse

# Deploy to pypi only if there is a tag
if [ ! -z "$TRAVIS_TAG" ]
then
    python3 -m pip install twine
    python3 -m twine upload --skip-existing wheelhouse/*.whl
fi