#!/bin/bash
# Build the source distribution tarball
# Only upload if a tagged commit

python3 -m pip install -r requirements.txt
python3 setup.py sdist --formats=gztar

if [ ! -z "$TRAVIS_TAG" ]
then
    python3 -m pip install twine
    python3 -m twine upload --skip-existing dist/*.tar.gz
fi